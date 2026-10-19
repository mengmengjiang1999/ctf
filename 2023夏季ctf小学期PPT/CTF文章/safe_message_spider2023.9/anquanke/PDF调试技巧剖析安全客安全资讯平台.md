# PDF调试技巧剖析

阅读量 **689620**

|评论 **1**

发布时间 : 2019-10-09 14:45:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01ad09f55cfd97ca3d.png)

Acrobat因为缺少符号，导致分析漏洞成因以及利用编写难度增加。该文章主要介绍Plugin机制和Javascript引擎，并且会直接给出相关的一些结论，这些结论主要通过官方文档和源码，再通过类比找到关键点，反复调试验证得到。

## 1\. Acrobat的Plugin机制

Acrobat的SDK文档中详细介绍了Plugin机制，并且Acrobat软件本身的很多功能都是通过Plugin机制实现的（在Acrobat安装目录下的plug_ins目录下的api后缀文件，本质上是dll文件，比如支持Javascript的EScript插件，支持搜索的Search插件等）。

在Acrobat的Plugin机制里，最重要的概念就是HFT（Hot Function Table），一个HFT包含了一组特定的回调函数。

Acrobat主程序维护了一系列的HFT,并且在加载每一个Plugin时,会将core HFT传给Plugin，Plugin通过调用core
HFT里的回调函数可以获取其他HFT（既可以是Acrobat主程序的HFT，也可以是其他Plugin注册的HFT）,并注册自己的HFT以供主程序或者其他Plugin调用，示意图如下所示。

通过Acrobat的Plugin机制，结合Acrobat的SDK中的头文件，我们可以定位很多HFT的回调函数并且根据需要在IDA里重命名，变相识别符号。

接下来详细介绍定位各个HFT的步骤。

### 1.1 获取coreHFT-修改对应的回调函数名称

1) Windbg调试Acrobat的主程序AcroRd32.exe(勾选Debug Child Process
Also)，在调试器中断时通过sxe命令下断点（这里Plugin的名称可以自由选择，下图选择的是EScript.api）。

2) 直接运行直到对应的Plugin加载，将IDA中通过edit->Segments->Rebase
Program将IDA中的基地址和windbg中的基地址保持一致（AcroRd32.dll和其他需要的Plugin也进行同样的操作）。

3) 在IDA中阅读PluginMain函数，找到PISetupSDK回调函数，如下图所示。

4) 在PISetupSDK处下断点，第2个参数是指向PISDKData_V0200的指针，PISDKData_V0200的定义如下。

运行到断点处时，根据结构体定义获取coreHFT。

上图中，中间那段就是coreHFT的一系列回调函数，但是这是动态查看到的结果，不适合用于IDA重命名函数名，所以顺着coreHFT的第一个4字节得到了最后一行的0x299和0x64f3b580，得到0x64f3b580后，直接在AcroRd32.dll模块中跳转到对应地址（前提是AcroRd32.dll在IDA中的基地址已经和windbg中的一致），如下图所示。

注意，0x64f3b580是获取coreHFT的回调函数，所有HFT都有一个对应的回调函数，但是只要求这些函数最终返回HFT，而中间的过程不做任何要求，所以获取不同的HFT的回调函数实现可能不一样，但是都会有明显的标志可以帮助确认。

比如上图中的generateCoreHFT（自己命名的），实现如下图所示。

这里我已经根据Acrobat的SDK中的头文件CorProcs.h修改了对应函数的名称。删除了注释后的CorProcs.h内容如下图所示，可以对比上图，顺序是一一对应的。

到这里已经找到了获取coreHFT的回调函数，再根据CorProcs.h头文件得到了最核心的一些函数，其中最有用的2个函数是ASAtomGetString和ASExtensionMgrGetHFT。

通过ASAtomGetString函数，我们可以得到所有的Atom字符串及对应的Atom（本质上就是索引）。

通过ASExtensionMgrGetHFT函数，我们可以得到所有已经注册的HFT表，再结合Acrobat SDK中的头文件达到重命名函数的目的。

### 1.2 遍历所有的Atom字符串

在IDA中阅读ASAtomGetString函数，得到关键的全局变量地址，如下图所示，关键的全局变量地址为0x66723e78。

将该地址替换下面的windbg脚本中的寄存器@$t0。

    
    
    r @$t0 = 0x66723e78 ;
    
    r @$t0 = poi(@$t0) ;
    
    r @$t1 = poi(@$t0 + 0x1c) ; 
    
    r @$t0 = poi(@$t0 + 0x18) + 0x4 ;
    
    .for(r @$t2 = 0;@$t0 + @$t2 * 8 < @$t1; r @$t2 = @$t2 + 1) {r @$t2;r @$t3 = @$t0 + @$t2 * 8;da poi(@$t3);}

然后将所有windbg脚本拷贝到命令行窗口运行，效果如下。

如果将关键地址替换如下脚本命令中的@$t0寄存器，同时将@$t4寄存器设置为对应的Atom（索引），则可以直接查看对应的字符串。

    
    
    r @$t4 = 0x299 ;
    
    r @$t0 = 0x66723e78 ;
    
    r @$t0 = poi(@$t0) ;
    
    r @$t0 = poi(@$t0 + 0x18) + 0x4 ;
    
    r @$t0 = @$t0 + @$t4 * 8 ;
    
    da poi(@$t0) ;

这里0x299是1.1节中打印coreHFT相关信息的时候得到的，运行这段脚本的结果如下图所示。

可以验证1.1节中得到的HFT的确是coreHFT。

### 1.3 获取所有的HFT

在IDA中阅读函数ASExtensionMgrGetHFT,得到关键的全局变量地址。如下图所示，关键的全局变量地址为0x667241E4。

将该地址替换为下面windbg脚本中的@$t0寄存器，同时把@$t5寄存器设置为1.2节中得到的全局变量地址。

    
    
    r @$t5 = 0x66723e78 ;
    
    r @$t0 = 0x667241E4;
    
    r @$t0 = poi(@$t0);
    
    r @$t1 = poi(@$t0) - 0x4;
    
    r @$t0 = poi(@$t0 + 0xc);
    
    r @$t5 = poi(@$t5) ;
    
    r @$t5 = poi(@$t5 + 0x18) + 0x4 ;
    
    .for(r @$t2 = 0; @$t2 <= @$t1; r @$t2 = @$t2 + 1) {r @$t3 = poi(@$t0 + @$t2 * 4);dd @$t3 L0x2;r @$t4 = low(poi(@$t3));r @$t6 = @$t5 + @$t4 * 8 ;da poi(@$t6) ;.echo ------------------------------------}

将所有脚本命令拷贝到windbg的命令行窗口，运行后的结果如下所示(为了直观和理解，这里将所有结果都展示了出来，不过选择的Plugin不同这里展示的结果可能不同，因为有些HFT可能还没有注册)。

展示结果分2行，第1行的结构和1.1节中coreHFT的一样(第1个4字节是HFT名称的索引，第2个4字节是获取对应HFT的回调函数)，第2行则是HFT的实际名称。

    
    
    0:000> r @$t5 = 0x66723e78 ;
    
    0:000> r @$t0 = 0x667241E4;
    
    0:000> r @$t0 = poi(@$t0);
    
    0:000> r @$t1 = poi(@$t0) - 0x4;
    
    0:000> r @$t0 = poi(@$t0 + 0xc);
    
    0:000> r @$t5 = poi(@$t5) ;
    
    0:000> r @$t5 = poi(@$t5 + 0x18) + 0x4 ;
    
    0:000> .for(r @$t2 = 0; @$t2 <= @$t1; r @$t2 = @$t2 + 1) {r @$t3 = poi(@$t0 + @$t2 * 4);dd @$t3 L0x2;r @$t4 = low(poi(@$t3));r @$t6 = @$t5 + @$t4 * 8 ;da poi(@$t6) ;.echo ------------------------------------}
    
    
    
    08836ec8  00000299 64f3b580
    
    050325f0  "Core"
    
    ------------------------------------    
    08836ce8  0000029a 64f3b8e0
    
    05033248  "AcroSupport"
    
    ------------------------------------    
    08836c20  00001048 65527f40
    
    08836ae0  "ASExternalWarningHandler"
    
    ------------------------------------    
    08836b58  00001049 00000000
    
    05025940  "ASTest"
    
    ------------------------------------    
    0885e128  0000104b 00000000
    
    05087310  "ASThread"
    
    ------------------------------------    
    0885e4e8  0000029b 64f3bb80
    
    05032670  "Cos"
    
    ------------------------------------    
    ------------------------------------未显示完

接下来针对部分HFT演示一下通过Acrobat SDK中的头文件修改函数名称，所有的HFT操作都是类似的，不过有些HFT在Acrobat
SDK中不存在，Adobe没有公开。

**1.3.1 Cos HFT**

根据上面的结果，可以知道获取Cos HFT的回调函数为0x64f3bb80,在IDA中查看该函数，如下所示。

    
    
    ------------------------------------    
    0885e4e8  0000029b 64f3bb80
    
    05032670  "Cos"
    
    ------------------------------------
这个写法和之前的获取Core HFT类似，继续跟进sub_64F3BC6E,如下图所示（太长了不适合图片）。

    
    
    int sub_64F3BC6E()
    
    {
    
      _DWORD *v0; // esi@1
    
      int v1; // ST40_4@2
    
      int v3; // [sp+8h] [bp-10h]@2
    
      int v4; // [sp+Ch] [bp-Ch]@2
    
      int v5; // [sp+10h] [bp-8h]@2
    
      int v6; // [sp+14h] [bp-4h]@2
    
    
    
      v0 = TlsGetValue(dword_665BAF2C);
    
      if ( !v0[23] )
    
      {
    
        v3 = 16;
    
        v1 = v0[24];
    
        v4 = 109;
    
        v5 = 589824;
    
        v6 = 0;
    
        v0[23] = sub_64EC7CC0(v1, &v3);
    
      }
    
      sub_64F3C33F(1, sub_64F82ED0, 0);
    
      sub_64F3C33F(2, sub_64F13BA0, 0);
    
      sub_64F3C33F(3, sub_64F97C60, 0);
    
      sub_64F3C33F(4, sub_64F81580, 0);
    
      -----------未 显 示 完
    
      return sub_64F3C33F(109, sub_6536C480, 0);
    
    }

可以知道Cos HFT中有109个回调函数（上述没有显示完），此时再到Acrobat
SDK中查看头文件CosProcs.h，去除掉注释后得到如下结果，正好109个函数声明，和上图一一对应（这里懒没有在IDA中一一重命名）。

如果个数对应不上，应该是有重复的函数声明，在头文件中以#if #else #endif的形式存在，删除重复的就好了。

    
    
    NPROC(ASBool, CosObjEqual, (CosObj obj1, CosObj obj2))
    
    NPROC(CosType, CosObjGetType, (CosObj obj))
    
    NPROC(ASBool, CosObjIsIndirect, (CosObj obj))
    
    NPROC(ASBool, CosObjEnum, (CosObj obj, CosObjEnumProc proc, void *clientData))
    
    NPROC(CosDoc, CosObjGetDoc, (CosObj obj))
    
    NPROC(CosObj, CosNewNull, (void))
    
    NPROC(CosObj, CosNewInteger, (CosDoc dP, ASBool indirect, ASInt32 value))
    
    NPROC(CosObj, CosNewFixed, (CosDoc dP, ASBool indirect, ASFixed value))
    
    NPROC(CosObj, CosNewBoolean, (CosDoc dP, ASBool indirect, ASBool value))
    
    NPROC(CosObj, CosNewName, (CosDoc dP, ASBool indirect, ASAtom name))
    
    NPROC(CosObj, CosNewString, (CosDoc dP, ASBool indirect, const char *str, ASTArraySize nBytes))
    
    NPROC(CosObj, CosNewArray, (CosDoc dP, ASBool indirect, ASTArraySize nElements))
    
    ---------未 完

**1.3.2 PDSRead HFT**

这里之所以列出PDSRead HFT是因为它代表了一种情况——实际的实现中回调函数个数比Acrobat SDK中头文件里的回调函数个数多。

仍然根据之前打印出的所有HFT结果（上图没有显示完）可以发现获取PDSRead HFT的回调函数是0x64f3cf70,在IDA中查看如下所示。

    
    
    ------------------------------------    
    08899e18  00001060 64f3cf70
    
    0888c7d8  "PDSRead"
    
    ------------------------------------
跟进sub_64F3D0C2，如下所示。

    
    
    int sub_64F3D0C2()
    
    {
    
      int v0; // ebp@0
    
      _DWORD *v1; // esi@1
    
      int v2; // ST40_4@2
    
      int v4; // [sp+8h] [bp-10h]@2
    
      int v5; // [sp+Ch] [bp-Ch]@2
    
      int v6; // [sp+10h] [bp-8h]@2
    
      int v7; // [sp+14h] [bp-4h]@2
    
    
    
      v1 = TlsGetValue(dword_665BAF2C);
    
      if ( !v1[532] )
    
      {
    
        v4 = 16;
    
        v2 = v1[533];
    
        v5 = 53;
    
        v6 = 851968;
    
        v7 = 0;
    
        v1[532] = sub_64EC7CC0(v0);
    
      }
    
      sub_64F3D3FD(1, sub_64FC8F90, 0);
    
      sub_64F3D3FD(2, sub_64FC9120, 0);
    
      sub_64F3D3FD(3, sub_64FC9480, 0);
    
      sub_64F3D3FD(4, sub_64FE89D0, 0);
    
      sub_64F3D3FD(5, sub_654BD830, 0);
    
      sub_64F3D3FD(6, sub_654BD890, 0);
    
      --------------------------------    
      sub_64F3D3FD(52, sub_654BE790, 0);
    
      return sub_64F3D3FD(53, sub_654BF1F0, 0);
    
    }

可以发现PDSRead的HFT中应该有53个回调函数，但是查看Acrobat
SDK中的头文件PDSReadProcs.h，发现只有50个回调函数，如下所示。

    
    
    NPROC (ASBool,  PDDocGetStructTreeRoot,     (IN  PDDoc pdDoc,
    
    NPROC (ASInt32, PDSTreeRootGetNumKids,      (IN  PDSTreeRoot treeRoot))
    
    NPROC (void,    PDSTreeRootGetKid,          (IN  PDSTreeRoot treeRoot,
    
    NPROC (ASBool,  PDSTreeRootGetRoleMap,      (IN  PDSTreeRoot treeRoot,
    
    NPROC (ASBool,  PDSTreeRootGetClassMap,     (IN  PDSTreeRoot treeRoot,
    
    -------------------------------------
这种情况下按照顺序前面的50个回调函数是一一对应的。

**1.3.3 Forms HFT**

这里之所以列出Forms HFT是因为它也是另一种情况——它的HFT的回调函数不是一个个插入的，而是直接静态拷贝的。

根据之前打印的结果可以知道获取Forms HFT的回调函数是0x64f46f90，IDA中查看如下图所示。

    
    
    ------------------------------------    
    0889f408  006310aa 64f46f90
    
    088d0cb0  "Forms"
    
    ------------------------------------
可以发现这次的实现和之前获取core HFT、Cos HFT的实现不一样了，这种就是直接静态拷贝得到一个HFT的。

跟进off_665D8E78,发现是一个函数地址表。

    
    
    .data:665D8E78 off_665D8E78    dd offset sub_65785D30  ; DATA XREF: sub_64F46F90+8o
    
    .data:665D8E7C                 dd offset sub_6577D150
    
    .data:665D8E80                 dd offset sub_6577CF80
    
    .data:665D8E84                 dd offset sub_6577D090
    
    .data:665D8F44                 dd offset sub_6577D4A0
    
    -----------------------------------------------------    
    .data:665D8F48                 dd offset sub_6577C9D0
    
    .data:665D8F4C                 align 10h
    
    .data:665D8F50 off_665D8F50    dd offset sub_6577CB10  ; DATA XREF: sub_64F46FF0+8o

再计算一下0xd4/4，结果是53，也就是说这个表里总共有53个回调函数，占用的字节数是0xd4。

再在Acrobat
SDK的头文件FormsHFTProcs.h，去除注释后内容如下，刚好53个函数声明，正好和上面的函数地址表一一对应（懒，没有在IDA中实际重命名函数）。

    
    
    PIPROC(ASBool, IsPDDocAcroForm, (PDDoc doc), doc)
    
    PIPROC(void, AFPDDocLoadPDFields, (PDDoc doc), doc)
    
    PIPROC(void, AFPDDocEnumPDFields, (PDDoc doc, ASBool terminals, ASBool parameterIgnored, AFPDFieldEnumProc proc, void *clientData),doc, terminals, parameterIgnored, proc, clientData)
    
    -------------------------------------------------
**1.3.4 EScript HFT**

EScript HFT并没有包含在Acrobat SDK中，也就是无法重命名回调函数。

这里之所以介绍它是因为他代表了一类特殊的情况——某些HFT表可能既在AcroRd32.dll中存在，又在Plugin中存在，会发生冲突。

这里我在加载完EScript.api后再次打印所有的HFT表，部分结果如下所示。

    
    
    ------------------------------------    
    0889f890  000010b5 64edc6b0
    
    088d0f00  "ESHFT"
    
    ------------------------------------    
    0889f7a0  000010b6 64edcdc0
    
    088d0ed0  "WebLink"
    
    ------------------------------------    
    0889f9a8  000010b7 64f47240
    
    088ead10  "WebLinkPriv"
    
    ------------------------------------    
    0889fbd8  000010be 6515b270
    
    088cf710  "EFSInfo"
    
    0889fde0  000010c1 64f82950
    
    088cf920  "Updater"
    
    ------------------------------------    
    0889fd68  000010c2 64f51680
    
    088eaff8  "PrivPubSecHFT"
    
    ------------------------------------    
    08d7ae98  04f911e7 64b921a0
    
    0888beb8  "$ESHFT"

可以看到，在上面的结果中，第一个是ESHFT表，最后一个是$ESHFT表，这种情况的出现是因为ESHFT表是在Arcobat主程序（也就是AcroRd32.dll中的），而$ESHFT表则是在Plugin
EScript.api中的。

跟进获取ESHFT表的回调函数0x64edc6b0（属于AcroRd32.dll）和$ESHFT表的回调函数0x64b921a0（属于EScript.api），对比效果如下图所示。

**1.3.5 Search HFT**

这里之所以介绍Search HFT，是因为它代表了另一种情况——一个Plugin可能不会被加载。

如果一个Plugin没有被加载，它的HFT表怎么获取呢？

1) 首先在Plugin的导出函数PluginMain中得到PISetupSDK函数。

2) 然后再PISetupSDK函数中得到handShake函数。

3) 在handShake中，找到导出HFT的代码。

4）导出HFT的代码不同插件实现可能不同，关键就是在汇编层面找”push
函数地址”这样的形式，针对这样形式的push指令，每一个函数地址都跟进去看一下，经验足够的话是很容易判断出最终的HFT表的。

接下来用Search Plugin和EScript Plugin来实际演示一下过程。

先看EScript Plugin对应的HFT的静态查找过程。

再来看看Search Plugin对应的HFT表的静态查找过程（图在下一页）。

### 1.4 结束语

在Acrobat SDK的文档中，提到了Acrobat core API的概念。

Acrobat core API的架构如下。

可以看出，所谓的Acrobat core API就是上一节提到的HFT概念。上图架构中的各个组件在Acrobat SDK中对应的头文件如下表所示。

Acrobat Viewer —————— Acrobat SDK中以AV为前缀的文件，HFT在AVProcs.h中声明

Acrobat Support —————— Acrobat SDK中以AS为前缀的文件，HFT在ASProcs.h中声明

COS —————— Acrobat SDK中以Cos为前缀的文件，HFT在CosProcs.h中声明

PDSEdit —————— Acrobat SDK中以PDS为前缀的文件，HFT在PDSReadProcs.h和PDSWriteProcs.h中声明

Portable Document —————— Acrobat SDK中以PD为前缀的文件，HFT在PDProcs.h中声明

到这里，动态查找各个HFT和静态查找各个Plugin的HFT都已经介绍完毕，通过找到的HFT以及Acrobat
SDK中的头文件，是可以将大量关键的函数进行重命名的，从而帮助快速漏洞分析、漏洞可行性的判断以及漏洞利用方案的编写等等。

## 2\. Acrobat的Javascript机制

Acrobat SDK的文档中明确说明了最新的Acrobat Reader使用的Javascript引擎是基于SpiderMonkey 24.2。

![](https://p2.ssl.qhimg.com/t0149526e056781b985.png)

SpiderMonkey
24.2是一个稳定发行版本，源码可以在http://ftp.mozilla.org/pub/spidermonkey/releases/下载。

首先介绍一下怎么找到Javascript层的api对应的Native层的实现，这点不是必需的，但是能有效地辅助调试。

### 2.1 查找Javascript层的api对应的Native实现

对于大部分Javascript层的api,直接在EScript.api模块中搜索对应的属性名称或者方法名称，再利用IDA的交叉引用即可找到对应的Native实现，比如下图的app.alert。

![](https://p0.ssl.qhimg.com/t015cc70aee94962756.png)

再比如，this.addScript如下图所示（在Acrobat
Reader中，全局作用域中this指代的是当前打开的pdf文档——一个Doc对象，所以this.addScript本质上是Doc::addScript）。

![](https://p0.ssl.qhimg.com/t01b84603de89a96831.png)

但是，某些Javascript层的api不在EScript.api模块中实现，而是在其他模块中实现，这种时候对应的属性名称或者方法名称既在EScript.api模块中会出现，也会在其他模块中出现。

比如app.media对象的所有属性和方法对应的Native实现都不在EScript.api模块中（虽然app对象是），而是在Multimedia.api模块中。

现在在EScript.api中搜索一下app.media的方法alertFileNotFound，结果如下所示。

![](https://p5.ssl.qhimg.com/t010266bbe1e2a9d55d.png)

可以看到，无法在EScript.api中找到app.media对象的属性和方法对应的Native实现，但是EScript.api明显以特定的结构保存了app.media对象的相关信息。

再在Multimedia.api模块中搜索一下alertFileNotFound，如下图所示。

![](https://p2.ssl.qhimg.com/t01e011a227c95e02db.png)

注意，通过这种方法找Javascript
api对应的Native实现不是取巧，是由实现机制得到的（这里的实现机制包括SpiderMonkey本身实现的Javascript调用Native函数机制和Adobe在这个机制的基础上进一步实现了自己的机制，这里不适合展开，后续内容会涉及这部分内容）。

掌握了该方法后，就可以根据Acrobat SDK中的Javascript
API重命名各个对象属性和方法的Native实现，进一步达到识别符号的目的，也方便调试时下断点。

### 2.2 SpiderMonkey关键结构

虽然用SpiderMonkey本身来解释这些结构会更好(有pdb信息和源码)，但是因为Acrobat的EScript.api在最关键的JSObject对象做了一些修改，防止混淆以下所有内容都是展示EScript的结果。

这部分结内容可以先大致看一下，掌握了后续内容后再回过头阅读。

因为在自己调试实验的时候需要有一个出发点，而这个出发点在后续小节里才涉及。

**2.2.1 Value结构体**

Javascript是无类型语言，但是这只是语言层面而言，在底层一定是要有和类型相关的信息的，Value结构体的功能就是如此（可以参考vbs的variant类型）。

一个Value结构体占8个字节，除了double和超过32位大小的整数，其他类型都是高4字节用于保存类型，低4字节保存值或者实际对象的指针，类型的值对应的类型如下所示。

    
    
    JS_ENUM_HEADER(JSValueType, uint8_t)
    
    {
    
        JSVAL_TYPE_DOUBLE              = 0x00,
    
        JSVAL_TYPE_INT32               = 0x01,
    
        JSVAL_TYPE_UNDEFINED           = 0x02,
    
        JSVAL_TYPE_BOOLEAN             = 0x03,
    
        JSVAL_TYPE_MAGIC               = 0x04,
    
        JSVAL_TYPE_STRING              = 0x05,
    
        JSVAL_TYPE_NULL                = 0x06,
    
        JSVAL_TYPE_OBJECT              = 0x07,
    
    
    
        /* These never appear in a jsval; they are only provided as an out-of-band value. */
    
        JSVAL_TYPE_UNKNOWN             = 0x20,
    
        JSVAL_TYPE_MISSING             = 0x21
    
    } JS_ENUM_FOOTER(JSValueType);

比如对于下面的Javascript代码

    
    
    this["0"] = 0x5
    
    this["1"] = 0x100000000
    
    this["2"] = 3.14
    
    this["3"] = undefined
    
    this["4"] = false
    
    this["5"] = true
    
    this["6"] = null
    
    this["7"] = "str1"
    
    this["8"] = {}
    
    this["9"] = function() {app.alert("in function");}
    
    
    
    app.alert("end");

底层表示如下所示。

![](https://p2.ssl.qhimg.com/t0117cdb4f7e2206404.png)

**2.2.2 String对象**

String对象的第1个4字节由字符串字符长度（不是字节长度）和flag组成（低4位用于保存flag，其余位用于保存字符串字符长度）。

为了提高字符串的处理效率，String对象又细分成不同类型，由flag决定，flag的值和字符串的类型如下所示。

    
    
         *   Rope         0000       0000
    
         *   Linear       -         !0000
    
         *   HasBase      -          xxx1
    
         *   Dependent    0001       0001
    
         *   Flat         -          isLinear && !isDependent
    
         *   Undepended   0011       0011
    
         *   Extensible   0010       0010
    
         *   Inline       0100       isFlat && !isExtensible && (u1.chars == inlineStorage) || isInt32)
    
         *   Stable       0100       isFlat && !isExtensible && (u1.chars != inlineStorage)
    
         *   Short        0100       header in FINALIZE_SHORT_STRING arena
    
         *   External     0100       header in FINALIZE_EXTERNAL_STRING arena
    
         *   Int32        0110       x110 (NYI, Bug 654190)
    
         *   Atom         1000       1xxx
    
         *   InlineAtom   1000       1000 && is Inline
    
         *   ShortAtom    1000       1000 && is Short
    
    Int32Atom    1110       1110 (NYI, Bug 654190)

不过这里只介绍最常见的一种——Atom字符串，也就是flag为0x8。

对于2.2.1节中的代码

    
    
    this["7"] = "str1"

实际的存储如下所示。

![](https://p4.ssl.qhimg.com/t01a621b750bdb9b390.png)

这里需要注意一点，一个String对象至少占32个字节，除了头8个字节，剩余的内存是用来直接保存长度比较小的字符串，这样可以提高内存的使用效率。

如果字符串的长度过长，剩余的内存则不使用，第2个4字节指向实际的字符串，如下图所示。

![](https://p5.ssl.qhimg.com/t01398cdff1a26e775b.png)

**2.2.3 JSObject**

JSObject对应的是Javascript层的Object概念。

这个结构涉及的概念有点多，也是需要重点消化的对象，因为接下来的function、Array、Map、Set等都建立在JSObject的基础上。

首先我们从一个空的Object开始来研究JSObject。

**2.2.3.1 空Object对应的JSObject**

对于以下代码（this.dummy1和this.dummy2是为了直观地确认emptyObject的存在，可以忽略）

    
    
    this.dummy1 = 255
    
    this.emptyObject = {}
    
    this.dummy2 = 255

首先this.emptyObject的值是一个空的Object，Native层的表示如下。

![](https://p1.ssl.qhimg.com/t01e91e5487bf015d7d.png)

**2.2.3.2 Shape对象**

从上面的一些图中应该可以看到SpiderMonkey引擎在添加新的属性时，属性的值是按照顺序在内存中存放的（以一个Value结构体为单位）,那么一定是需要一个中间的媒介，来保存属性的名称以及属性的值的对应关系，从而通过属性（字符串）找到对应的Value。

Shape对象就是这个中间的媒介，Shape的逻辑如下图所示。

![](https://p5.ssl.qhimg.com/t0116e10655a13e1f99.png)

① 每一个Shape对象保存了id和slot索引，通过对比id来进行所谓的查找属性，id一致后就可以根据对应的slot索引得到属性的值。

② 一个JSObject的第一个成员指向Shape单链表的最后一个元素。

③ 单链表的最后一个Shape对象可能会指向一个哈希表。

④ 查找属性的时候，先通过id尝试在哈希表里直接获取对应的Shape（如果有哈希表的话）。

⑤ 如果没有找到或者哈希表不存在，则通过遍历单链表，然后对比id来查找Shape。

⑥ 如果找到了Shape，则根据Shape中的slot索引获取属性的值。

实际演示，对于如下代码

    
    
    this.dummy1 = 255
    
    this.emptyObject = {}
    
    this.dummy2 = 255
    
    this.emptyObject.mem1 = "mem1"
    
    this.emptyObject.mem2 = "mem2"
    
    this.emptyObject.mem3 = "mem3"
    
    this.emptyObject.mem4 = "mem4"
    
    this.emptyObject.mem5 = "mem5"

在内存中的实际关系如下图所示。

![](https://p3.ssl.qhimg.com/t010845d8096da7c6ee.png)

上图中出现了一个新的概念——fixed slots，fixed
slots是紧跟在JSObject（或者JSObject的子类）后面的固定大小的slot数组，主要用于优化，给一个对象添加属性时，会先填充fixed
slots，fixed slots用完后才会使用单独的slots（JSObject偏移量+0x8指向的slot数组）。

理解上图可能需要配合前面的Shape对象的逻辑图。

调试时，为了方便，可以使用如下windbg 脚本命令，@$t0寄存器代表的是JSObject的起始地址。

    
    
    r @$t0 = 0x08067b68 ;
    
    r @$t1 = poi(@$t0) ;
    
    r @$t2 = poi(@$t0 + 0x8 );
    
    r @$t8 = poi(@$t1 + 0x10);
    
    .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}

在该例子中，运行后的效果如下所示。

    
    
    0:000> r @$t0 = 0x08067b68 ;
    
    0:000> r @$t1 = poi(@$t0) ;
    
    0:000> r @$t2 = poi(@$t0 + 0x8 );
    
    0:000> r @$t8 = poi(@$t1 + 0x10);
    
    0:000> .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}
    
    
    
    07e3c1c8  "mem5"                                          
    
    $t4=00000004 $t5=00000004
    
    0efda218  07e3c1c0 ffffff85
    
    --------------------    
    07e3c1a8  "mem4"
    
    $t4=00000004 $t5=00000003
    
    08067b98  07e3c1a0 ffffff85
    
    --------------------    
    07e3c188  "mem3"
    
    $t4=00000004 $t5=00000002
    
    08067b90  07e3c180 ffffff85
    
    --------------------    
    07e3c168  "mem2"
    
    $t4=00000004 $t5=00000001
    
    08067b88  07e3c160 ffffff85
    
    --------------------    
    07e3c148  "mem1"
    
    $t4=00000004 $t5=00000000
    
    08067b80  07e3c140 ffffff85
    
    --------------------
打印的结果中，第1行是属性的名称，第2行是fixed slots的个数和Shape对应的slot索引，第3行是属性的值。

**2.2.3.3 TypeObject对象**

TypeObject有2个关键成员，第1个是clasp——可以用来判断一个Object所属类型；第2个是proto——Javascript中的prototype概念的实现。

proto在查找对象属性的时候会用到，如果当前JSObject的Shape单链表中没有找到属性，则会在proto的Shape单链表继续查找，依次类推。

对于如下代码

    
    
    this.dummy1 = 255
    
    this.proto = {}
    
    this.emptyObject = {}
    
    this.dummy2 = 255
    
    this.proto.mem1 = "proto"
    
    this.emptyObject.__proto__ = this.proto

TypeObject演示如下。

![](https://p2.ssl.qhimg.com/t0132d8a466dbf0a94d.png)

**2.2.4 JSFunction和JSScript**

JSFunction对应的是Javascript层function的概念。

一个JSFcuntion要么封装了一个Native函数，要么封装了一个JSScript，JSScript包含了一个function对应的各种信息（比如最关键的字节码）。

对于代码

    
    
    this.dummy1 = 255
    
    function test() {app.alert("in function test");}
    
    this.dummy2 = 255

JSFunction的逻辑如下所示。

![](https://p2.ssl.qhimg.com/t0164b9793c7c129067.png)

可以看到JSFunction最关键的就是偏移0x1c处的4字节和0x24处的4字节。

0x24处的4字节指向一个Atom字符串，该字符串表示function的名称，注意这里的”test”和打印this的属性时的字符串”test”含义是不一样的，打印this的属性时的字符串”test”表示的是this对象的属性名称，这个属性不一定是”test”，但是function的名称确定后就不会变了。

0x1c处的4字节要么是一个Native函数的地址（如果JSFunction封装的是Native函数的话），要么指向一个JSScript对象(调用函数的话相应的字节码会被解释执行)。

接下来看看JSScript对象的逻辑。

![](https://p2.ssl.qhimg.com/t0104c051a790efe015.png)

可以看到JSScript的关键点在偏移0xC处的4字节和偏移0x24字节处的4字节。

偏移0xC处的4字节指向对应的function的字节码起始处。

偏移0x24处的4字节指向一个ScriptSourceObject对象(继承自JSObject),而ScriptSourceObject的fixed
slots中的第1个是ScriptSource对象，ScriptSourceObject也就是简单地封装了一下ScriptSource对象。

ScriptSource对象包含了对应function的Javascript源码和源码所在的文件名。

JSScript可以用来在调试过程中辅助判断某个对象。

**2.2.5 Array对象**

Array对象是基于JSObject的，对于如下代码

    
    
    this.dummy1 = 255
    
    this.arr = Array(255, "elem2", 255)
    
    this.arr.push({})
    
    this.dummy2 = 255

this.arr的实际存储形式如下。

![](https://p1.ssl.qhimg.com/t016beda24937047915.png)

从上图可以看出，Array对象的所有元素都存储在elements中，不存在slots。

### 2.2.6 Map对象

Map对象也是基于JSObject，不过涉及到Hash，所以稍微复杂一些。

对于如下代码

    
    
    this.dummy1 = 255
    
    this.map = new Map()
    
    this.map.set("key1", "value1")
    
    this.map.set("key2", "value2")
    
    this.map.set("key3", "value3")
    
    this.dummy2 = 255

this.map的实际存储形式如下。

![](https://p2.ssl.qhimg.com/t011bea199653782ab9.png)

从上图中可以看到，一个Map对象在fixed slots后有一个指向Ordered HashTable的指针。

在Ordered HashTable中，有length和capacity的值，同时还有一个指向entries的指针。

在entries中，key和value相邻并以Value结构体的形式存在。

**2.2.7 Set对象**

Set对象和Map对象很类似，而且都是基于Ordered HashTable。

对于代码

    
    
    this.dummy1 = 255
    
    this.set = new Set()
    
    this.set.add("value1")
    
    this.set.add("value2")
    
    this.set.add("value3")
    
    this.dummy2 = 255

this.set的实际存储形式如下。

![](https://p3.ssl.qhimg.com/t0163052b31fbb1234f.png)

可以看到Set对象的存储形式和Map对象差不多，只是在最后存储Value结构体时逻辑不一样。

**2.2.8 FrameRegs和StackFrame**

FrameRegs和StackFrame是SpiderMonkey的解释器解释执行字节码时需要的2个最关键的结构，它们都是Interpret函数中频繁使用到的变量。

FrameRegs结构包含3个成员，依次是sp_、pc_和fp_。

sp_成员模拟esp(rsp)寄存器，pc_成员模拟eip(rip)寄存器，fp_成员模拟ebp(rbp)寄存器。

sp_永远指向栈顶，pc_一开始指向字节码的起始地址，在解释执行的过程中会指向下一个字节码，fp_指向的是一个StackFrame结构体。

StackFrame保存了当前的作用域、局部变量、当前的脚本、this、arguments和callee等关键信息。

整体逻辑如下所示。

![](https://p5.ssl.qhimg.com/t0160fd09e5bc985f64.png)

其中最关键的就是sp_和fp_，这2个能够大大提高调试Javascript的速度。

通过sp_可以在特定代码执行后快速获取某些Javascript变量的值。

通过fp_则可以得到this对象，再结合之前的打印JSObject对象所有属性的windbg脚本命令，可以查看所有相关的属性的值，如果this对象是全局变量，还可以将该this值保存起来，无论什么时候都可以顺藤摸瓜查看所有变量的值。

而且fp_指向的StackFrame末尾（StackFrame大小0x48字节）开始依次保存局部变量的值（局部变量在编译阶段已经被分配了特定的索引，所以在运行时不存在变量的名称等信息）。

### 2.3 实战

在大致了解了2.2节中的各个关键结构后，接下来就是在调试中不断熟悉，形成自己的调试经验。

**2.3.1 准备pdf**

实战的前提是能够随意构造嵌有js代码的pdf文件，Acrobat Pro版可以做到，PDF-XChange-Editor也可以，当然通过一些开源的工具也行。

Acrobat Pro要收费，PDF-XChange-Editor可以免费使用，不过生成的pdf有水印。

接下来使用的pdf均是通过PDF-XChange-Editor生成的（在菜单栏的Form菜单可以添加Javascript）。

![](https://p3.ssl.qhimg.com/t0102b53a59f770d947.png)

### 2.3.2 windbg加载Acrobat Reader

windbg加载Acrobat Reader（勾选Debug Child Process Also选项），中断到调试器就输入g命令运行，一直到Acrobat
Reader可以交互。

crtl+break或者alt+delete强行中断到windbg，输入lmm escript查看EScript.api模块的基地址。

如果EScript.api模块还没有加载，说明Acrobat启动的代码还没执行完，输入g命令继续运行，等一会儿再重复相同操作。

    
    
    0:034> lmm escript
    
    Browse full module list
    
    start    end        module name
    
    64b90000 64e5f000   EScript    (deferred)   

IDA加载EScript.api，并重定向基地址为实际的地址。

**2.3.3 查找Interpret——解释执行pcode(字节码)的函数**

不只是对于Acrobat
Reader中的SpiderMonkey引擎，研究所有解释执行类的语言找这个函数都是最关键的，因为这里是代码产生实际效果的过程，跟踪这些过程可以摸清楚各种关键结构和关键机制。

针对SpiderMonkey 24.2，查找该函数有2种快捷方法。

1) 直接在IDA中搜索文本“switch 230 cases”，得到的结果就在Interpret函数中。

![](https://p2.ssl.qhimg.com/t01704a8b928864a856.png)

2)
在字符串窗口找到字符串”js::RunScript”，然后通过交叉引用进入到引用该字符串的函数，再通过交叉引用退回到上一层函数，该函数就是js::RunScript。

![](https://p2.ssl.qhimg.com/t01185cbfb29a4b981a.png)

然后在js::RunScript函数中定位到Interpret函数。

![](https://p3.ssl.qhimg.com/t010f3716610b5b86a8.png)

找到Interpret后，在Interpret函数找到核心switch（循环解释执行字节码的地方），然后根据IDA中的地址在windbg相应地址处下断点，然后输入g命令直接运行。

![](https://p1.ssl.qhimg.com/t018f82a45253f9421c.png)

到这里，通过Acrobat Reader的打开文件功能打开带有Javascript代码的pdf文件就会触发断点。

接下来会分别介绍细粒度调试和快速调试2种方式，可以根据兴趣阅读。

细粒度调试就是以字节码甚至以汇编语言为单位一步步跟踪Javascript代码产生的效果。

快速调试就是以Javascript语句为单位跟踪Javascript代码产生的效果。

**2.3.4 细粒度调试Javascript代码**

1) 在PDF-XChange-Editor中生成带有如下javascript代码的pdf文档。

![](https://p1.ssl.qhimg.com/t0177a8faaa82050fd8.png)

2) 然后使用Acrobat Reader打开生成的pdf文档，触发断点，如下图所示。

![](https://p3.ssl.qhimg.com/t01abb187b708332693.png)

到这里，首先在IDA中查看FrameRegs(2.2.8节介绍的)，如下图所示。

![](https://p4.ssl.qhimg.com/t0148c5b97958825c67.png)

从上图的推测结果可以看到，ebp-0x30处的12字节是FrameRegs，[ebp-0x30]指向临时堆栈，[ebp-0x2C]指向当前字节码，[ebp-0x28]指向StackFrame。

3) 通过StackFrame（[ebp-0x28]）获取this指针（在这次实验中this代表的是Doc对象），如下图所示。

![](https://p4.ssl.qhimg.com/t014df5423964dc63b2.png)

4) 将值0xbd29740替换2.2.3.2节中的Windbg脚本命令中的@$t0寄存器，运行后就可以查看this（Doc对象）当前的所有属性。

可以把this值临时保存到记事本或者其他其他文本中，然后在调试的任何时候都可以配合2.2.3.2中的windbg脚本命令查看Doc对象的属性，然后顺藤摸瓜查看Javascript代码中的所有变量的值。

Windbg脚本命令运行结果如下所示（为了篇幅把中间大部分内容省了）。

    
    
    0:000> r @$t0 = 0xbd29740 ;
    
    0:000> r @$t1 = poi(@$t0) ;
    
    0:000> r @$t2 = poi(@$t0 + 0x8 );
    
    0:000> r @$t8 = poi(@$t1 + 0x10);
    
    0:000> .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}
    
    
    
    0c6e1c50  "rightsManagement"
    
    $t4=00000001 $t5=000000b9
    
    0bcc8e28  00000000 ffffff82
    
    --------------------    
    0b994ae8  "encryptUsingPolicy"
    
    $t4=00000001 $t5=000000b8
    
    0bcc8e20  0bd1e5d8 ffffff87
    
    --------------------    
    0a8377c8  "layout"
    
    $t4=00000001 $t5=00000002
    
    0bcc8870  00000000 ffffff82
    
    --------------------    
    0a815528  "info"
    
    $t4=00000001 $t5=00000001
    
    0bcc8868  00000000 ffffff82
    
    --------------------    
    0a81c4a8  "hidden"
    
    $t4=00000001 $t5=00000000
    
    0bd29758  00000000 ffffff82
    
    --------------------
5) 获取并保存了this后，接下来跟踪字节码的执行。

查看pc_([ebp-0x2C])指向的字节码，跟踪字节码的执行的步骤如下所示。

![](https://p5.ssl.qhimg.com/t0181bbbfa38843ce37.png)

解释:
如果要一步步跟踪字节码的执行过程，首先通过[ebp-0x2C]得到当前的字节码，将16进制字节码换算成10进制，再在SpiderMonkey源码中的jsopcode.tbl查看对应的字节码的名称，根据字节码名称在SpiderMonkey源码中的Interpreter.cpp中查看对应字节码的处理流程。

以当前实验中的第一条语句this[“0”] = 0x5为示例。

①
通过[ebp-0x2C]发现当前字节码是0x41(65)，查询后发现是JSOP_THIS,windbg中直接输入g命令解释执行该字节码，准备执行下一个字节码的时候调试器又触发断点，此时通过[ebp-0x30]查看sp_指向的临时堆栈的栈顶。

![](https://p0.ssl.qhimg.com/t01a19528cee4aaa743.png)

可以看到，JSOP_THIS字节码执行完后，FrameRegs中的sp_指向的临时栈栈顶已经保存了this的值。

②
通过[ebp-0x2C]发现当前字节码是0x3e(62)，查询后发现是JSOP_ZERO,windbg中直接输入g命令解释执行该字节码，准备执行下一个字节码的时候调试器又触发断点，此时通过[ebp-0x30]查看临时栈栈顶。

    
    
    0:000> dd poi(@ebp-0x30)-0x8
    
    0b9e5e28  00000000 ffffff81

可以看到，JSOP_ZERO字节码执行完后，FrameRegs中的sp_指向的临时栈栈顶已经保存了整数0。

③
通过[ebp-0x2C]发现当前字节码是0xd7(215)，查询后发现是JSOP_INT8,windbg直接输入g命令解释执行该字节码，准备执行下一个字节码的时候调试器又触发断点，此时通过[ebp-0x30]查看临时栈栈顶。

    
    
    0:000> dd poi(@ebp-0x30)-0x8
    
    0b9e5e30  00000005 ffffff81

可以看到，JSOP_INT8字节码执行完后，FrameRegs中的sp_指向的临时栈栈顶已经保存了整数0x5。

④
通过[ebp-0x2C]发现当前字节码是0x38(56)，查询后发现是JSOP_SETELEM，windbg直接输入g命令执行解释该字节码，准备执行下一个字节码的时候调试器又触发断点，此时运行之前保存的打印this的所有属性的windbg脚本命令，结果如下（省略了大部分结果）。

    
    
    0:000> r @$t0 = 0xbd29740  ;
    
    0:000> r @$t1 = poi(@$t0) ;
    
    0:000> r @$t2 = poi(@$t0 + 0x8 );
    
    0:000> r @$t8 = poi(@$t1 + 0x10);
    
    0:000> .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}
    
    
    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t4=00000001 $t5=000000ba
    
    0bcc8e30  00000005 ffffff81
    
    --------------------    
    0c6e1c50  "rightsManagement"
    
    $t4=00000001 $t5=000000b9
    
    0bcc8e28  00000000 ffffff82
    
    --------------------    
    0b994ae8  "encryptUsingPolicy"
    
    $t4=00000001 $t5=000000b8
    
    0bcc8e20  0bd1e5d8 ffffff87
    
    --------------------
可以看到this(Doc对象)新增了一个属性，打印的第一个属性id是0x1，属性的值是整数0x5。

注意这里属性的id不在是字符串的地址，而是0x1，右移1位后的结果0x0代表的就是索引（最低位的0x1表示这个不是字符串地址，因为地址最低位肯定为0x0）。

到这里，Javascript代码this[“0”] = 0x5对应的字节码执行完毕，跟踪其他的语句对应的字节码的步骤类似。

**2.3.5 快速调试Javascript代码**

快速调试代码主要利用了提前保存的Doc对象（因为它在整个pdf的Javascritp代码执行过程中一直存在并且地址保持不变）和app.alert弹窗（根据个人喜好可以选择其他的）。

1) 首先使用PDF-XChange-Editor生成一个带有如下Javascript代码的pdf文档，注意在感兴趣的地方插入app.alert来快速跳过某些字节码的解释执行。

![](https://p4.ssl.qhimg.com/t01ea634215a799e4a1.png)

2) Acrobat Reader打开生成的pdf，触发断点，如下所示。

![](https://p4.ssl.qhimg.com/t01f45e6ff496a60b19.png)

到这里，首先在IDA中查看FrameRegs(2.2.8节介绍的)，如下图所示。

![](https://p3.ssl.qhimg.com/t019b7afa484d411b3d.png)

从上图的推测结果可以看到，ebp-0x30处的12字节是FrameRegs，[ebp-0x30]指向临时堆栈，[ebp-0x2C]指向当前字节码，[ebp-0x28]指向StackFrame。

3) 通过StackFrame（[ebp-0x28]）获取this指针（在这次实验中this代表的是Doc对象），如下图所示。

![](https://p0.ssl.qhimg.com/t0100cc0ac93ce17111.png)

4) 将值0xbd29a38替换2.2.3.2节中的Windbg脚本命令中的@$t0寄存器，运行后就可以查看this（Doc对象）当前的所有属性。

可以把this值临时保存到记事本或者其他其他文本中，然后在调试的任何时候都可以配合2.2.3.2中的windbg脚本命令查看Doc对象的属性，然后顺藤摸瓜查看Javascript代码中的所有变量的值。

Windbg脚本命令运行结果如下所示（为了篇幅把中间大部分内容省了）。

    
    
    0:000> r @$t0 = 0xbd29a38  ;
    
    0:000> r @$t1 = poi(@$t0) ;
    
    0:000> r @$t2 = poi(@$t0 + 0x8 );
    
    0:000> r @$t8 = poi(@$t1 + 0x10);
    
    0:000> .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}
    
    
    
    0a83c788  "removeLinks"
    
    $t4=00000001 $t5=000000b8
    
    0b8ec920  0bd24ab0 ffffff87
    
    --------------------    
    0a83c768  "getLinks"
    
    $t4=00000001 $t5=000000b7
    
    0b8ec918  0bd24a88 ffffff87
    
    --------------------    
    0a81c4a8  "hidden"
    
    $t4=00000001 $t5=00000000
    
    0bd29a50  00000000 ffffff82
    
    --------------------
5) 获取this并保存后，接下来直接禁用断点，然后输入命令g运行，Acrobat Reader弹出对话框。

    
    
    0:000> bl
    
         0 e Disable Clear  64bc21bc     0001 (0001)  0:**** EScript!mozilla::HashBytes+0x2177c
    
    0:000> bd 0
    
    0:000> bl
    
         0 d Enable Clear  64bc21bc     0001 (0001)  0:**** EScript!mozilla::HashBytes+0x2177c
    
    0:000> g
    
    (4b38.3950): C++ EH exception - code e06d7363 (first chance)
    
    (4b38.3950): C++ EH exception - code e06d7363 (first chance)

![](https://p5.ssl.qhimg.com/t01376d7ca536f3191b.png)

6) 点击OK，弹出下一个对话框。

![](https://p5.ssl.qhimg.com/t0185309f4c0524c5f7.png)

7)
此时可以知道app.alert(“1”)之前的Javascript代码对应的字节码肯定已经解释执行完毕，通过ctrl+break或者alt+delete强行中断到调试器。

![](https://p0.ssl.qhimg.com/t0167cc2b4cdbe166b8.png)

8) 再次运行刚才运行过的Windbg脚本命令，结果如下。

    
    
    0:003> r @$t0 = 0xbd29a38  ;
    
    0:003> r @$t1 = poi(@$t0) ;
    
    0:003> r @$t2 = poi(@$t0 + 0x8 );
    
    0:003> r @$t8 = poi(@$t1 + 0x10);
    
    0:003> .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}
    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000009
    
    $t4=00000001 $t5=000000bd
    
    0b8ec948  00000000 ffffff83
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000007
    
    $t4=00000001 $t5=000000bc
    
    0b8ec940  00000000 ffffff82
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000005
    
    $t4=00000001 $t5=000000bb
    
    0b8ec938  51eb851f 40091eb8
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000003
    
    $t4=00000001 $t5=000000ba
    
    0b8ec930  00000000 41f00000
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000001
    
    $t4=00000001 $t5=000000b9
    
    0b8ec928  00000005 ffffff81
    
    --------------------    
    0a83c788  "removeLinks"
    
    $t4=00000001 $t5=000000b8
    
    0b8ec920  0bd24ab0 ffffff87
    
    --------------------
可以看到新增了几个属性，属性的id分别是9、7、5、3、1（属性的id右移1位的结果就是索引，比如这里分别对应索引4、3、2、1、0），值分别是false、undefined、3.14、0x100000000、0x5，和Javascript代码是一一对应的。

9) 输入命令g运行，再次点击对话框的OK，弹出下一个对话框。

![](https://p4.ssl.qhimg.com/t0187e336d61590f837.png)

10) 再次强行中断并运行Windbg脚本命令，结果如下。

    
    
    0:001> r @$t0 = 0xbd29a38  ;
    
    0:001> r @$t1 = poi(@$t0) ;
    
    0:001> r @$t2 = poi(@$t0 + 0x8 );
    
    0:001> r @$t8 = poi(@$t1 + 0x10);
    
    0:001> .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}
    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=0000000f
    
    $t4=00000001 $t5=000000c0
    
    0b8ec960  0a818ba0 ffffff85
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=0000000d
    
    $t4=00000001 $t5=000000bf
    
    0b8ec958  00000000 ffffff86
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=0000000b
    
    $t4=00000001 $t5=000000be
    
    0b8ec950  00000001 ffffff83
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000009
    
    $t4=00000001 $t5=000000bd
    
    0b8ec948  00000000 ffffff83
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000007
    
    $t4=00000001 $t5=000000bc
    
    0b8ec940  00000000 ffffff82
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000005
    
    $t4=00000001 $t5=000000bb
    
    0b8ec938  51eb851f 40091eb8
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000003
    
    $t4=00000001 $t5=000000ba
    
    0b8ec930  00000000 41f00000
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000001
    
    $t4=00000001 $t5=000000b9
    
    0b8ec928  00000005 ffffff81
    
    --------------------    
    0a83c788  "removeLinks"
    
    $t4=00000001 $t5=000000b8
    
    0b8ec920  0bd24ab0 ffffff87
    
    --------------------
可以看到又新增了3个属性，id分别是0xf、0xd、0xb（索引分别是7、6、5），值分别是一个字符串、null、true。

11) 再次输入g运行，点击对话框的OK，弹出下一个对话框。

![](https://p5.ssl.qhimg.com/t01ab64b2768f0530a6.png)

12) 再次强行中断并运行Windbg脚本命令，结果如下。

    
    
    0:003> r @$t0 = 0xbd29a38  ;
    
    0:003> r @$t1 = poi(@$t0) ;
    
    0:003> r @$t2 = poi(@$t0 + 0x8 );
    
    0:003> r @$t8 = poi(@$t1 + 0x10);
    
    0:003> .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}
    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000013
    
    $t4=00000001 $t5=000000c2
    
    0b8ec970  0bd24b50 ffffff87
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=00000011
    
    $t4=00000001 $t5=000000c1
    
    0b8ec968  0bda9078 ffffff87
    
    --------------------    
    Memory access error at '); r @$t9 = 0xaa'
    
    $t3=0000000f
    
    $t4=00000001 $t5=000000c0
    
    0b8ec960  0a818ba0 ffffff85
    
    --------------------
可以看到又多了2个属性，id分别是0x13、0x11（索引分别是9、8）,值是2个JSObject（JSFunction也是JSObject），和Javascript代码也是对应的。

快速调试就只有这么多，通过快速调试可以查看任何一句Javascript代码产生的影响。

一般调试时大部分都应该使用快速调试，在关键部分结合细粒度的调试。

**2.3.6 调用Native function的逻辑**

2.2.4已经介绍了JSFunction的概念，这里主要通过实际调试直观地感受一下之前的概念。

1) 生成一个包含如下代码的pdf。

![](https://p5.ssl.qhimg.com/t01ac7057a0ecbeba6b.png)

2) 根据之前的技巧调试该pdf，触发断点，找到this的值为0x0bd29a38。

3) 使用windbg脚本命令打印this的所有属性，找到app属性及对应的值。

    
    
    --------------------    
    0a819ce8  "app"
    
    $t4=00000001 $t5=00000058
    
    0b8ebe18  0bd29b78 ffffff87
    
    --------------------
4) 可以看到app对象的地址是0x0bd29b78，再次使用windbg脚本命令打印app对象的所有属性。

    
    
    0:000> r @$t0 = 0x0bd29b78  ;
    
    0:000> r @$t1 = poi(@$t0) ;
    
    0:000> r @$t2 = poi(@$t0 + 0x8 );
    
    0:000> r @$t8 = poi(@$t1 + 0x10);
    
    0:000> .for(; @$t8 != 0; r @$t1 = @$t8;r @$t8 = poi(@$t1 + 0x10)) {r @$t3 = poi(@$t1 + 0x4);r @$t9 = 0;.catch {du poi(@$t3 + 0x4); r @$t9 = 0xaa};.if (@$t9 != 0xaa) {r @$t3};r @$t3 = poi(@$t1 + 0x8);r @$t4 = @$t3 >> 0n27;r @$t5 = @$t3 & 0x00ffffff;r @$t4, @$t5;.if(@$t5 < @$t4) {dd @$t0+0x18+@$t5*8 L0x2;}.else {r @$t5 = @$t5-@$t4;dd @$t2+@$t5*8 L0x2;};.echo --------------------;}
    
    0a81e7c8  "doc"
    
    $t4=00000001 $t5=00000000
    
    0bd29b90  0bd29a38 ffffff87
    
    --------------------
嗯?怎么只有一个doc属性，app不是还有很多方法和属性吗?这是因为app的其他属性和方法都在app对象的prototype中。

5) 根据2.2.3.3得到app对象的prototype。

    
    
    0:000> dd 0x0bd29b78 L0x4
    
    0bd29b78  0bdb5df0 0bd25980 00000000 64e124d0
    
    
    
    0:000> dd 0bd25980 L0x4
    
    0bd25980  0b9f7110 0bd29268 00000000 80ff0008

上面的0xbd29268就是app对象的prototype，再次使用windbg脚本命令打印app的prototype的所有属性，并找到alert属性及它的值。

    
    
    --------------------    
    0a818cc8  "alert"
    
    $t4=00000001 $t5=0000000d
    
    0b99b040  0bd3c3d0 ffffff87
    
    --------------------
6) alert对象的地址是0xbd3c3d0，是一个JSFunction。

打印alert对象的值，如下所示。

    
    
    0:000> dd 0xbd3c3d0 L0xa
    
    0bd3c3d0  0bd3b8c8 0bd250c0 00000000 64e124d0
    
    0bd3c3e0  0c763b00 00000000 00000000 64be4600
    
    0bd3c3f0  00000000 0a818cc0
    
    
    
    0:000> dc 0a818cc0 L0x8
    
    0a818cc0  00000058 0a818cc8 006c0061 00720065  X.......a.l.e.r.
    
    0a818cd0  00000074 00000000 00000000 00000000  t...............

可以确定没有找错，那么根据2.2.4可以知道偏移0x1C处的地址（这里是0x64be4600）就是app.alert的Native实现了。

是这样吗？通过2.1节得到的app.alert的Native实现应该是地址0x64C63CB0，如下所示。

![](https://p3.ssl.qhimg.com/t012ca61954c4f148ca.png)

为什么alert的JSFucntion封装的Native函数地址不对呢？

这里就需要介绍一直没介绍的JSObject剩余的8个字节（参考2.2.3）。

Acrobat为了使得EScript可以调用其他模块(动态链接库)实现的Native函数，在SpiderMoneky的Native调用机制上实现了自己的机制。

这个机制由一个特定的函数实现（我称为CallExternalReference），就是上面得到的alert的JSFunction封装的Native函数，在IDA中定位0x64be4600如下。

![](https://p2.ssl.qhimg.com/t015c508bb355815492.png)

也就是调用Natvie函数时其实调用的是CallExternalReference，并传入实际要调用的函数名称（比如这里的”alert”），然后CallExternalReference会在传入的对象（这里是app对象的prototype）中根据传入的函数名称查找实际的Native实现。

app的prototype保存的函数名称对应的Native实现如下。

![](https://p1.ssl.qhimg.com/t01e583a466546eab4f.png)

可以看到这次alert对应的Native实现0x64c63cb0是正确的了。

## 3 结束语

到这里，pdf最重要的2个机制——plugin机制和Javascript机制都介绍完毕。Plugin机制能够帮助手动识别很多关键函数，Javascript机制则是漏洞利用的关键所在，不管是分析漏洞还是编写漏洞利用都是十分重要的，该文档并没有把Javascript相关的所有机制都介绍一下，但是掌握了该文档中介绍的技术，应该可以应付绝大部分情况，希望对研究PDF的人员有所帮助。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360成都安全响应中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/188138](/post/id/188138)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [PDF](/tag/PDF)

 **+1** __11赞

 __收藏

![](https://p3.ssl.qhimg.com/t01e4d00bec4013a066.png) 360成都安全响应中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

