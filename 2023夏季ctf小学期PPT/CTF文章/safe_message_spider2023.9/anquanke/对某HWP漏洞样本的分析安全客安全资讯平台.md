# 对某HWP漏洞样本的分析

阅读量 **315259**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-11-01 11:30:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01257ceaa93c256ac1.jpg)

## 前言

最近拿到一些 HWP(韩文字处理程序) 的漏洞样本，花了几天时间调试了一下，本文记述了我对其中一个样本的调试过程。

HWP 是韩国 Hancom 公司开发的韩文字处理软件，类似于中国的 WPS。HWP 在韩国政企中占有率很高，所以经常被用来攻击韩国用户。FireEye
曾在2015年9月抓到一个[HWP 0day](https://www.fireeye.com/blog/threat-research/2015/09/zero-day_hwp_exploit.html)。目前针对HWP的攻击中使用最多的是
CVE-2017-8291，这是一个 GhostScript 组件的类型混淆漏洞。

本次调试的样本是另一处漏洞，具体的CVE编号暂不清楚，这个漏洞在原理上可以和 FireEye 抓到的 CVE-2015-6585
归为一类，但并不完全相同。这批样本首先[被安博士所披露](http://asec.ahnlab.com/1015)。2015年5月20日安博士又写过另一篇类似的[分析文章](http://asec.ahnlab.com/1035)。

## 基本信息

###  样本信息

> MD5：33874577bf54d3c209925c9def880eb9

###  调试环境

> VMware + windbg + windows_7_sp1_x86 + HWP 2010 English Edtion (HwpApp.dll
> 8.0.0.466)

###  环境搭建

  1. 安装 HWP2010 韩文版，[磁力链接](magnet:?xt=urn:bith:B6F6E352C4CC579E3F027EB746C5BD880B743902)
  2. 安装 HWP2010 最新补丁，[下载链接](https://cdn.hancom.com/pds/hnc/Product/Patch/Office/Hwp2007Update_20160825.exe)
  3. 在控制面板中卸载 HWP2010
  4. 重新安装 HWP2010 韩文版

上述四个步骤之后可以出现带有英文界面的 HWP2010 (HwpApp.dll 8.0.0.466)

###  漏洞复现

HWP 文档的解析主程序为 Hwp.exe ，利用 gflags.exe 工具对其开启页堆，在调试状态下打开文档发生崩溃，崩溃现场如下：

    
    
    First chance exceptions are reported before any exception handling.
    This exception may be expected and handled.
    eax=c0c0c0c0 ebx=0dabe600 ecx=0e0c0e0c edx=00000029 esi=0012e9ac edi=00000000
    eip=06b1028a esp=0012e954 ebp=0f22cf80 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00010206
    *** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:Program FilesHncHwp80HwpApp.dll -    HwpApp+0x4028a:
    06b1028a 8b4254          mov     eax,dword ptr [edx+54h] ds:0023:0000007d=????????
    
    Disassembly：
    06b10277 0fb75008        movzx   edx,word ptr [eax+8]
    06b1027b 0fb74006        movzx   eax,word ptr [eax+6]
    06b1027f c1e210          shl     edx,10h
    06b10282 0bd0            or      edx,eax
    06b10284 8b4228          mov     eax,dword ptr [edx+28h]
    06b10287 8b11            mov     edx,dword ptr [ecx]
    06b10289 50              push    eax
    06b1028a 8b4254          mov     eax,dword ptr [edx+54h] ds:0023:0000007d=????????
    06b1028d 896c241c        mov     dword ptr [esp+1Ch],ebp
    06b10291 ffd0            call    eax ; 崩溃点下面不远处有一个call eax
    06b10293 8bd8            mov     ebx,eax
    
    0:000> ? 06b10291-hwpapp
    Evaluate expression: 262801 = 00040291
    

关闭页堆，对 call eax 语句下断点，再次在调试器中打开文档，发现此时 eax=0x0e0c0e0c，从堆分配的栈回溯信息中可以看到
0x0e0c0e0c 位于一块由 VirtualAlloc 函数申请，大小为 18MB 的堆内存上。

    
    
    bp hwpapp+40291
    
    ...
    Breakpoint 0 hit
    eax=0e0c0e0c ebx=02c6c600 ecx=0e0c0e0c edx=0e0c0e0c esi=0012e6dc edi=00000000
    eip=04730291 esp=0012e684 ebp=0271e4e0 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp+0x40291:
    04730291 ffd0            call    eax {0e0c0e0c} // 控制流转移
    
    // 由于 Hwp2010 并未开启 DEP，所以不需要 xchg 指令去导向 ROP，直接可以在堆内存上执行shellcode。
    0:000> u 0e0c0e0c
    0e0c0e0c 0c0e            or      al,0Eh
    0e0c0e0e 0c0e            or      al,0Eh
    0e0c0e10 0c0e            or      al,0Eh
    0e0c0e12 0c0e            or      al,0Eh
    0e0c0e14 0c0e            or      al,0Eh
    0e0c0e16 0c0e            or      al,0Eh
    0e0c0e18 0c0e            or      al,0Eh
    0e0c0e1a 0c0e            or      al,0Eh
    
    // 0xe0c0e0c 处疑似用堆喷射进行了填充
    0:000> dc e0c0e0c
    0e0c0e0c  0e0c0e0c 0e0c0e0c 0e0c0e0c 0e0c0e0c  ................
    0e0c0e1c  0e0c0e0c 0e0c0e0c 0e0c0e0c 0e0c0e0c  ................
    0e0c0e2c  0e0c0e0c 0e0c0e0c 0e0c0e0c 0e0c0e0c  ................
    0e0c0e3c  0e0c0e0c 0e0c0e0c 0e0c0e0c 0e0c0e0c  ................
    0e0c0e4c  0e0c0e0c 0e0c0e0c 0e0c0e0c 0e0c0e0c  ................
    0e0c0e5c  0e0c0e0c 0e0c0e0c 0e0c0e0c 0e0c0e0c  ................
    0e0c0e6c  0e0c0e0c 0e0c0e0c 0e0c0e0c 0e0c0e0c  ................
    0e0c0e7c  0e0c0e0c 0e0c0e0c 0e0c0e0c 0e0c0e0c  ................
    
    0:000> !heap -p -a 0e0c0e0c
        address 0e0c0e0c found in
        _HEAP @ 2760000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
    invalid allocation size, possible heap corruption
            0dfb0018 24006d 0000  [00]   0dfb0030    120035c - (busy VirtualAlloc)
            Trace: 25a05a4
            777bdd6c ntdll!RtlAllocateHeap+0x00000274
            74e53db8 MSVCR90!malloc+0x00000079
    
    0:000> ? 0x120035c/0n1024/0n1024
    Evaluate expression: 18 = 00000012
    

## 漏洞成因

###  静态分析

####  触发分析

用 [HwpScan2工具](https://www.nurilab.net/hwpscan2) 打开漏洞文件，我们可以看到 BodyText 部分有6个
section 流，每个 section 流都表示文本相关的一些信息(具体可参考HWP格式规范)。

![](https://p5.ssl.qhimg.com/t014cf48fa95a0bf79d.png)

HWP文件格式用 Tag 来描述文档的各种信息，每个 section 中有不同的 Tag 来描述不同的信息，每个 Tag 由 DWORD
头部和数据部分构成，具体结构如下：

![](https://p2.ssl.qhimg.com/t01ef6b3ce0ff974c23.png)

可以看到头部的 DWORD 中包含：

> Tag ID、Level 和 Size

其中

> Tag ID = HWPTAG_BEGIN + Value，HWPTAG_BEGIN = 0x10

不同的 Tag ID 对应的 Value 和其代表的含义如下图所示：

![](https://p4.ssl.qhimg.com/t010e762ea5023ceff8.png)

其中 HWPTAG_PARA_TEXT Tag 里存储的数据是一个段落的文本信息。在段落的文本信息中可以指定一些控制字，控制字范围为
0-31，这些控制字可以指定一些额外的特性。这些都在HWP的说明文档中有介绍，如下图所示：

![](https://p2.ssl.qhimg.com/t017c81276465779bb7.png)

其中 03 控制字代表的意思如下。大致意思是该控制字会指定一些额外的超链接、书签或其他信息。文档上指明该控制字数据类型为 extended，大小为8字节。

![](https://p1.ssl.qhimg.com/t01cf27dc6eaebd9b09.png)

我们来看一下 section0 对应的该字段信息，section0 流里面只有一个 HWPTAG_PARA_TEXT Tag
(同一个流里面可以有多个同一类型的 Tag)

![](https://p5.ssl.qhimg.com/t012a5d23d393534506.png)

从下图可以看到 section0 的 HWPTAG_PARA_TEXT 数据中有一个 03 控制字段(03 00 ->
0x0003)，这个字段的最后4个字节是 0c 0e 0c 0e，按小端地址翻转一下就是 0x0e0c0e0c，这正是混淆发生后相关寄存器的值。

![](https://p3.ssl.qhimg.com/t01d21aaffed03c50ad.png)

我们来看一下混淆发生处的函数，可以看到 call 指令 (即v9())
位于一个while循环内，在调用具体的函数前首先会对一个4字节地址进行小端地址翻转，得到一个对象地址，然后取出对象首地址的虚表指针，调用虚表偏移+0x54处的虚函数。对象地址等价于：

> (0c 0e 0c 0e) -> 0x0e0c0e0c；

v9() 等价于

> call [*(0x0e0c0e0c) + 0x54]

![](https://p1.ssl.qhimg.com/t0187dd998d033d53e7.png)

####  堆喷分析

在审计 section2-section6 时发现每一个都有一段长度为 0x120035A字节(18MB) 的 HWPTAG_PARA_TEXT
区域，其与上面疑似堆喷射的内存大小几乎一致。

![](https://p5.ssl.qhimg.com/t01e35365d351789b3d.png)

每段 18MB 数据的前面大部分都是疑似雪橇指令，雪橇指令结束处可以看到疑似 shellcode：

![](https://p0.ssl.qhimg.com/t01969f940451df3418.png)

###  动态分析

####  堆喷射

我们在内存中搜索上图红框圈出的特征码：

    
    
    // 重点关注后面10条记录
    0:000> s -d 0x3 l?0x7fffffff 0x53525657
    02dd0efb  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    07b99443  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    0b94fc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    0cb5fc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    0dd6fc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    0ef7fc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    1130fc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    133afc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    145bfc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    157cfc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    169dfc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    17befc6b  53525657 c9335155 0c0e0cba 028a420e  WVRSUQ3......B..
    
    // 查看一下堆块基本情况
    0:000> !heap
    NtGlobalFlag enables following debugging aids for new heaps:    stack back traces
    Index   Address  Name      Debugging options enabled
      1:   019f0000                
      2:   00010000                
      3:   002e0000                
      4:   01950000                
      5:   01850000                
      6:   02850000                
      7:   029c0000                
      8:   03160000                
      9:   032c0000                
     10:   03560000                
     11:   04e80000                
     12:   06610000                
     13:   07370000                
     14:   07540000                
    
    // 可以看到4号堆几乎全被用完，其含有10块大小为18MB的内存
    0:000> !heap -stat -h 01850000
     heap @ 01850000
    group-by: TOTSIZE max-display: 20
        size     #blocks     total     ( %) (percent of total busy bytes)
        12003b0 5 - 5a01270  (49.27)
        120035c 5 - 5a010cc  (49.27)
        e4 910 - 81240  (0.28)
        f0 381 - 348f0  (0.11)
        24000 1 - 24000  (0.08)
        18 15bc - 209a0  (0.07)
        20000 1 - 20000  (0.07)
        100 18e - 18e00  (0.05)
        194 e5 - 16964  (0.05)
        aa00 2 - 15400  (0.05)
        28 6f0 - 11580  (0.04)
        10bc0 1 - 10bc0  (0.04)
        10000 1 - 10000  (0.03)
        fda0 1 - fda0  (0.03)
        fb50 1 - fb50  (0.03)
        a8 159 - e268  (0.03)
        4400 3 - cc00  (0.03)
        2200 6 - cc00  (0.03)
        800 17 - b800  (0.02)
        82 13b - 9ff6  (0.02)
    
    0:000> !heap -flt s 12003b0
        _HEAP @ 19f0000
        _HEAP @ 10000
        _HEAP @ 2e0000
        _HEAP @ 1950000
        _HEAP @ 1850000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0a750018 240078 0000  [00]   0a750030    12003b0 - (busy VirtualAlloc)
            0cb70018 240078 0078  [00]   0cb70030    12003b0 - (busy VirtualAlloc)
            10110018 240078 0078  [00]   10110030    12003b0 - (busy VirtualAlloc)
            133c0018 240078 0078  [00]   133c0030    12003b0 - (busy VirtualAlloc)
            157e0018 240078 0078  [00]   157e0030    12003b0 - (busy VirtualAlloc)
        _HEAP @ 2850000
        _HEAP @ 29c0000
        _HEAP @ 3160000
        _HEAP @ 32c0000
        _HEAP @ 3560000
        _HEAP @ 4e80000
        _HEAP @ 6610000
        _HEAP @ 7370000
        _HEAP @ 7540000
    
    0:000> !heap -flt s 120035c
        _HEAP @ 19f0000
        _HEAP @ 10000
        _HEAP @ 2e0000
        _HEAP @ 1950000
        _HEAP @ 1850000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0b960018 24006d 0000  [00]   0b960030    120035c - (busy VirtualAlloc)
            0dd80018 24006d 006d  [00]   0dd80030    120035c - (busy VirtualAlloc)
            121b0018 24006d 006d  [00]   121b0030    120035c - (busy VirtualAlloc)
            145d0018 24006d 006d  [00]   145d0030    120035c - (busy VirtualAlloc)
            169f0018 24006d 006d  [00]   169f0030    120035c - (busy VirtualAlloc)
        _HEAP @ 2850000
        _HEAP @ 29c0000
        _HEAP @ 3160000
        _HEAP @ 32c0000
        _HEAP @ 3560000
        _HEAP @ 4e80000
        _HEAP @ 6610000
        _HEAP @ 7370000
        _HEAP @ 7540000
    

####  类型混淆

既然这是一个类型混淆漏洞，我们来试着搞清楚到底是什么和什么产生了混淆。即：正常情况下这个地方调用的是什么函数？

既然上面说了 03 控制字支持的是超链接、书签之类的特性，那么我们不妨来构造一个含有超链接的普通HWP文档。然后对 v9()
对应处下断点，看看命中之后调用的是什么函数。

我们构造的带超链接的文本如下：

![](https://p2.ssl.qhimg.com/t0131c99c8d754b8801.png)

在 HwpScan2 里面看一下构造的样本的 HWPTAG_PARA_TEXT 数据：

![](https://p0.ssl.qhimg.com/t011dd3927de7948d35.png)

可以看到构造的正常样本在 03 00 控制字后面的四个字节是一个字符串：”klh%”，猜测其是 hyperlink(%hlk) 的简写，随后的四个字节被置为
00 00 00 00，随后跟着我们在文本中嵌入的 url 的 unicode编码。

我们在调试器内看一下这个样本：

    
    
    0:004> bp HwpApp+0x40263 
    *** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:Program FilesHncHwp80HwpApp.dll - 
    
    0:004> g
    ModLoad: 08d80000 08e23000   C:Program FilesHncHwp80DocFiltersEtcDocGroup.DFT
    ModLoad: 73500000 73509000   C:Program FilesHncHwp80DocFiltersRes.ENU
    ModLoad: 08d80000 08e0a000   C:Program FilesHncHwp80DocFiltersMajorDocGroup.DFT
    ModLoad: 73040000 73049000   C:Program FilesHncHwp80DocFiltersRes.ENU
    ModLoad: 0a1d0000 0a466000   C:Program FilesHncHwp80DocFiltersMsDocGroup.DFT
    ModLoad: 73500000 73509000   C:Program FilesHncHwp80DocFiltersRes.ENU
    ModLoad: 0a1d0000 0a302000   C:Program FilesHncHwp80DocFiltersODTDocGroup.DFT
    ModLoad: 73040000 73049000   C:Program FilesHncHwp80DocFiltersRes.ENU
    ModLoad: 06890000 068d8000   C:Program FilesHncHwp80DocFiltersXMLDocGroup.DFT
    ModLoad: 73500000 73509000   C:Program FilesHncHwp80DocFiltersRes.ENU
    ModLoad: 745b0000 7474e000   C:WindowsWinSxSx86_microsoft.windows.common-controls_6595b64144ccf1df_6.0.7601.17514_none_41e6975e2bd6f2b2comctl32.dll
    ModLoad: 744b0000 745a5000   C:Windowssystem32propsys.dll
    ModLoad: 74460000 74481000   C:Windowssystem32ntmarta.dll
    ModLoad: 77150000 77195000   C:Windowssystem32WLDAP32.dll
    Breakpoint 0 hit
    eax=00000004 ebx=02ddc600 ecx=02dbf798 edx=027d71a0 esi=0012e9ac edi=00000000
    eip=04770263 esp=0012e958 ebp=0285e578 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    HwpApp+0x40263:
    04770263 8d0442          lea     eax,[edx+eax*2]
    *** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:Program FilesHncHwp80Hwp.exe - 
    
    0:000> !heap -p -a edx
        address 027d71a0 found in
        _HEAP @ 26e0000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            027d7188 0025 0000  [00]   027d71a0    0010c - (busy)
            Trace: 3805a4
            777bdd6c ntdll!RtlAllocateHeap+0x00000274
            74e53db8 MSVCR90!malloc+0x00000079
    
    // HWPTAG_PARA_TEXT + HWPTAG_PARA_CHAR_SHAPE + HWPTAG_PARA_LINE_SEG + other data
    0:000> db edx l10c
    027d71a0  20 00 20 00 20 00 20 00-03 00 6b 6c 68 25 28 9f   . . . ...klh%(.
    027d71b0  d7 02 00 00 00 00 03 00-68 00 74 00 74 00 70 00  ........h.t.t.p.
    027d71c0  3a 00 2f 00 2f 00 77 00-77 00 77 00 2e 00 6e 00  :././.w.w.w...n.
    027d71d0  65 00 77 00 73 00 69 00-73 00 2e 00 63 00 6f 00  e.w.s.i.s...c.o.
    027d71e0  6d 00 2f 00 76 00 69 00-65 00 77 00 2f 00 3f 00  m./.v.i.e.w./.?.
    027d71f0  69 00 64 00 3d 00 4e 00-49 00 53 00 58 00 32 00  i.d.=.N.I.S.X.2.
    027d7200  30 00 31 00 38 00 30 00-39 00 31 00 32 00 5f 00  0.1.8.0.9.1.2._.
    027d7210  30 00 30 00 30 00 30 00-34 00 31 00 36 00 35 00  0.0.0.0.4.1.6.5.
    027d7220  39 00 33 00 04 00 6b 6c-68 00 00 00 00 00 00 00  9.3...klh.......
    027d7230  00 00 04 00 0d 00 00 00-00 00 00 00 30 10 00 00  ............0...
    027d7240  84 03 00 00 84 03 00 00-fd 02 00 00 1c 02 00 00  ................
    027d7250  00 00 00 00 18 a6 00 00-00 00 06 00 00 00 00 00  ................
    027d7260  4b 00 00 00 31 ee 9e 04-00 00 00 00 01 00 00 00  K...1...........
    027d7270  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    027d7280  00 00 00 00 01 00 00 00-84 03 00 00 00 00 00 00  ................
    027d7290  00 00 00 00 00 00 00 00-06 00 00 00 0c 00 00 00  ................
    027d72a0  07 00 00 00 42 00 00 00-06 00 00 00              ....B.......
    
    0:000> ? edx+eax*2
    Evaluate expression: 41775528 = 027d71a8
    
    // 03 控制字字段，可以看到原先 00 00 00 00 处被填写为了28 9f-d7 02，翻转后即为 0x02d79f28，这是一个对象指针，我们稍后解释
    0:000> db 027d71a8 l10
    027d71a8  03 00 6b 6c 68 25 28 9f-d7 02 00 00 00 00 03 00  ..klh%(.........
    
    ...
    0:000> p
    eax=00000000 ebx=02ddc600 ecx=02d79f28 edx=02d79f28 esi=0012e9ac edi=00000000
    eip=04770287 esp=0012e958 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp+0x40287:
    04770287 8b11            mov     edx,dword ptr [ecx]  ds:0023:02d79f28=04a39b60
    0:000> p
    eax=00000000 ebx=02ddc600 ecx=02d79f28 edx=04a39b60 esi=0012e9ac edi=00000000
    eip=04770289 esp=0012e958 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp+0x40289:
    04770289 50              push    eax
    0:000> p
    eax=00000000 ebx=02ddc600 ecx=02d79f28 edx=04a39b60 esi=0012e9ac edi=00000000
    eip=0477028a esp=0012e954 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp+0x4028a:
    0477028a 8b4254          mov     eax,dword ptr [edx+54h] ds:0023:04a39bb4=047eded0
    0:000> p
    eax=047eded0 ebx=02ddc600 ecx=02d79f28 edx=04a39b60 esi=0012e9ac edi=00000000
    eip=0477028d esp=0012e954 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp+0x4028d:
    0477028d 896c241c        mov     dword ptr [esp+1Ch],ebp ss:0023:0012e970=6e01134b
    0:000> p
    eax=047eded0 ebx=02ddc600 ecx=02d79f28 edx=04a39b60 esi=0012e9ac edi=00000000
    eip=04770291 esp=0012e954 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp+0x40291:
    04770291 ffd0            call    eax {HwpApp!HwpCreateParameterArray+0x38010 (047eded0)}
    
    // 对象大小为 0x34
    0:000> !heap -p -a 02d79f28 
        address 02d79f28 found in
        _HEAP @ 26e0000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            02d79f10 000a 0000  [00]   02d79f28    00034 - (busy)
              ? HwpApp!HwpCreateParameterArray+283ca0
            Trace: 325a10
            777bdd6c ntdll!RtlAllocateHeap+0x00000274
            74e53db8 MSVCR90!malloc+0x00000079
            74e53eb8 MSVCR90!operator new+0x0000001f
    
    // 查看对象内容
    0:000> dc 02d79f28 l34/4
    02d79f28  04a39b60 00000000 00000000 02db7be8  `............{..
    02d79f38  02dbf798 0285e578 04a3944c 0000a800  ....x...L.......
    02d79f48  07caef34 72edbbc6 00000000 00000000  4......r........
    02d79f58  12154747                             GG..
    
    // 对象基址 +0x00 处是一个虚表指针，虚表偏移+0x54处为 sub_bded0 函数
    0:000> dps 04a39b60 l54/4+1
    04a39b60  04966300 HwpApp!HwpCreateParameterArray+0x1b0440
    ...
    04a39bb0  04880990 HwpApp!HwpCreateParameterArray+0xcaad0 // +0x50
    04a39bb4  047eded0 HwpApp!HwpCreateParameterArray+0x38010 // +0x54
    
    // 对象基址 +0x20 处是Unicode编码的文本内容
    0:000> du 07caef34 
    07caef34  "http://www.newsis.com/view/?id"
    07caef74  "=NISX20180912_0000416593;1;0;0;"
    
    // 对象基址 +0x0C 处是前一个对象
    0:000> dc 02db7be8 l34/4
    02db7be8  04a39b60 00000000 02d79f28 02db7c38  `.......(...8|..
    02db7bf8  02dbf798 0285dc90 04a3944c 0000a800  ........L.......
    02db7c08  02dcadc4 72edbbc5 00000000 00000000  .......r........
    02db7c18  00000000                             ....
    
    // 前一个对象存储的内容(和文档内容一致)
    0:000> du 02dcadc4 
    02dcadc4  "http://www.kyeongin.com/main/vi"
    02dcae04  "ew.php?key=20180911010003744;1;"
    02dcae44  "0;0;"
    
    // 对象基址 +0x10 处是后一个对象
    0:000> dc 02dbf798 l34/4
    02dbf798  04a34ef0 0285e4e0 00000000 00000000  .N..............
    02dbf7a8  00000000 00000000 00000000 00000000  ................
    02dbf7b8  00000000 00000000 00000000 00000001  ................
    02dbf7c8  02dbf538                             8...
    
    // 后一个对象为空，所以没有对应的文档内容，相关地址为空
    
    // 对象基址 +0x14 处是另外一个大小为0x80的对象
    0:000> !heap -p -a 0285e578 
        address 0285e578 found in
        _HEAP @ 26e0000
          HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
            0285e560 0013 0000  [00]   0285e578    00080 - (busy)
              ? HwpApp!HwpCreateParameterArray+282250
            Trace: 79763e4
            777bdd6c ntdll!RtlAllocateHeap+0x00000274
            74e53db8 MSVCR90!malloc+0x00000079
            74e53eb8 MSVCR90!operator new+0x0000001f
            4843f27 HwpApp!HwpCreateParameterArray+0x0008e067
    
    0:000> dc 0285e578 l80/4
    0285e578  04a38110 027d71a0 00000026 0000003d  .....q}.&...=...
    0285e588  00000043 00000043 0000004b 00030001  C...C...K.......
    0285e598  00000000 02859eb8 00000000 00000001  ................
    0285e5a8  00000026 0000002a 00010000 00000003  &...*...........
    0285e5b8  00000018 80000000 0285e4e0 0285e448  ............H...
    0285e5c8  ffffffff 00000010 0000000d 00000000  ................
    0285e5d8  00000000 00000000 00000000 00000000  ................
    0285e5e8  00000000 00000000 00000000 00000000  ................
    
    // 该对象基址 +0x04 处存储着 027d71a0 
    // 即 HWPTAG_PARA_TEXT + HWPTAG_PARA_CHAR_SHAPE + HWPTAG_PARA_LINE_SEG + other data
    0:000> db 027d71a0 l10c
    027d71a0  20 00 20 00 20 00 20 00-03 00 6b 6c 68 25 28 9f   . . . ...klh%(.
    027d71b0  d7 02 00 00 00 00 03 00-68 00 74 00 74 00 70 00  ........h.t.t.p.
    027d71c0  3a 00 2f 00 2f 00 77 00-77 00 77 00 2e 00 6e 00  :././.w.w.w...n.
    027d71d0  65 00 77 00 73 00 69 00-73 00 2e 00 63 00 6f 00  e.w.s.i.s...c.o.
    027d71e0  6d 00 2f 00 76 00 69 00-65 00 77 00 2f 00 3f 00  m./.v.i.e.w./.?.
    027d71f0  69 00 64 00 3d 00 4e 00-49 00 53 00 58 00 32 00  i.d.=.N.I.S.X.2.
    027d7200  30 00 31 00 38 00 30 00-39 00 31 00 32 00 5f 00  0.1.8.0.9.1.2._.
    027d7210  30 00 30 00 30 00 30 00-34 00 31 00 36 00 35 00  0.0.0.0.4.1.6.5.
    027d7220  39 00 33 00 04 00 6b 6c-68 00 00 00 00 00 00 00  9.3...klh.......
    027d7230  00 00 04 00 0d 00 00 00-00 00 00 00 30 10 00 00  ............0...
    027d7240  84 03 00 00 84 03 00 00-fd 02 00 00 1c 02 00 00  ................
    027d7250  00 00 00 00 18 a6 00 00-00 00 06 00 00 00 00 00  ................
    027d7260  4b 00 00 00 31 ee 9e 04-00 00 00 00 01 00 00 00  K...1...........
    027d7270  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    027d7280  00 00 00 00 01 00 00 00-84 03 00 00 00 00 00 00  ................
    027d7290  00 00 00 00 00 00 00 00-06 00 00 00 0c 00 00 00  ................
    027d72a0  07 00 00 00 42 00 00 00-06 00 00 00              ....B.......
    

###  逆向分析

我们来看一下正常调用时 call 的 sub_bded0 函数究竟是个什么函数？

可以看到这个函数的作用很简单，简单来讲就是获取虚表内的上一个虚函数地址(+0x50处的虚函数指针)，然后调用之，返回 *[+0x50虚函数的返回值 +
0x04] 处的值

    
    
    .text:000BDED0                   sub_BDED0 proc near
    .text:000BDED0 8B 01             mov     eax, [ecx]
    .text:000BDED2 8B 50 50          mov     edx, [eax+50h]
    .text:000BDED5 FF D2             call    edx
    .text:000BDED7 8B 40 04          mov     eax, [eax+4]
    .text:000BDEDA C3                retn
    .text:000BDEDA                   sub_BDED
    

我们以 “%hlk” 为例看一下上一个虚函数 (+0x50) 的作用是什么：

    
    
    0:000> p
    eax=047eded0 ebx=02ddc600 ecx=02d79f28 edx=04a39b60 esi=0012f59c edi=00000000
    eip=04770291 esp=0012f544 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp+0x40291:
    04770291 ffd0            call    eax {HwpApp!HwpCreateParameterArray+0x38010 (047eded0)}
    0:000> t
    eax=047eded0 ebx=02ddc600 ecx=02d79f28 edx=04a39b60 esi=0012f59c edi=00000000
    eip=047eded0 esp=0012f540 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp!HwpCreateParameterArray+0x38010:
    047eded0 8b01            mov     eax,dword ptr [ecx]  ds:0023:02d79f28=04a39b60
    0:000> p
    eax=04a39b60 ebx=02ddc600 ecx=02d79f28 edx=04a39b60 esi=0012f59c edi=00000000
    eip=047eded2 esp=0012f540 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp!HwpCreateParameterArray+0x38012:
    047eded2 8b5050          mov     edx,dword ptr [eax+50h] ds:0023:04a39bb0=04880990
    0:000> p
    eax=04a39b60 ebx=02ddc600 ecx=02d79f28 edx=04880990 esi=0012f59c edi=00000000
    eip=047eded5 esp=0012f540 ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp!HwpCreateParameterArray+0x38015:
    047eded5 ffd2            call    edx {HwpApp!HwpCreateParameterArray+0xcaad0 (04880990)} // 调用 +0x50 处的虚函数
    0:000> t
    eax=04a39b60 ebx=02ddc600 ecx=02d79f28 edx=04880990 esi=0012f59c edi=00000000
    eip=04880990 esp=0012f53c ebp=0285e578 iopl=0         nv up ei pl nz na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    HwpApp!HwpCreateParameterArray+0xcaad0:
    04880990 b8100ca804      mov     eax,offset HwpApp!HwpCreateParameterArray+0x2cad50 (04a80c10) // 获取某个值
    
    // 定位该值在 hwpapp.dll 中的偏移
    0:000> ? 04a80c10-hwpapp
    Evaluate expression: 3476496 = 00350c10
    
    // 在IDA中可以看到，上一个虚表函数的作用是获取对应的 "%hlk" 标志
    .data:00350C10 dword_350C10    dd 10A90003h            ; DATA XREF: sub_150990o
    .data:00350C10                                         ; sub_2EE4D0+Ao
    .data:00350C14                 dd '%hlk'
    .data:00350C18                 dd 0
    .data:00350C1C                 dd offset sub_150920
    

在IDA中还可以找到相关标志的全称与简写对应关系(截图仅列出部分)，合理推测这些就是 03 控制字支持的那些特性。

![](https://p2.ssl.qhimg.com/t0176ce883b5c326213.png)

通过交叉引用，我们可以发现一处一模一样的调用点，从而更加确定被混淆函数的作用是获得当前特性对应的标志(从而可以用来在后面进行比较等)。

![](https://p2.ssl.qhimg.com/t011c57c20e0bed95af.png)

对其他特性的标志做相应检查后发现逻辑全部相似，漏洞发生处调用的函数正常情况下均为：

> sub_bded0

###  成因总结

  1. 正常逻辑下 HWPTAG_PARA_TEXT TAG 里面会指定段落的文本信息，其中(HWPTAG_PARA_TEXT 及其他一些 Tag)可以用 03 控制字指定一些控制属性，如超链接、书签等。在正常情况下，每一个标签(用4字节表示)后是对应的对象地址(4字节)，该地址在正常情况下会被初始化为 NULL，执行过程中会将对象地址动态赋值给相应的内存。在解析 HWPTAG_PARA_TEXT 数据内 03 控制字的过程中，会调用对应 对象关联的第(0x54/4 + 1)个处理例程，其作用是获取该属性对应的标志，如 “%hlk” 等。
  2. 攻击者通过精心构造 HWPTAG_PARA_TEXT TAG 的数据，绕过了执行过程中对相关对象指针的校验和赋值，借助事先用堆喷射布控的内存，成功实现类型混淆。由于hwp 2010未开启 DEP ，攻击者直接将 eip 劫持到位于堆上的 shellcode 并执行之。

整个过程中 HWP 解析程序不会崩溃，用户在打开文档时几乎是无感知的。

## shellcode 分析

漏洞成功触发转移 eip 到 0x0e0c0e0c，雪橇指令会一路滑行到 0x0f1afc71，进入 shellcode 的先导阶段。

    
    
    0:000> u 0f1afc6b
    0f1afc6b 57              push    edi
    0f1afc6c 56              push    esi
    0f1afc6d 52              push    edx
    0f1afc6e 53              push    ebx
    0f1afc6f 55              push    ebp
    0f1afc70 51              push    ecx
    0f1afc71 33c9            xor     ecx,ecx
    0f1afc73 ba0c0e0c0e      mov     edx,0E0C0E0Ch
    
    0:000> bp 0f1afc73
    0:000> g
    Breakpoint 1 hit
    eax=0e0c0e0f ebx=02c6c600 ecx=00000000 edx=0e0c0e0c esi=0012e6dc edi=00000000
    eip=0f1afc73 esp=0012e668 ebp=0271e4e0 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    0f1afc73 ba0c0e0c0e      mov     edx,0E0C0E0Ch
    

###  反虚拟机

有意思的是，shellcode 首先会调用 cpuid
指令检测虚拟机环境，相关基础知识在[这篇文章](https://consen.github.io/2016/09/11/Anti-VM-via-CPUID/)中有介绍。

    
    
    0:000> p
    eax=0e0c0e03 ebx=0eeffc66 ecx=00000000 edx=0eeffca5 esi=0012ec8c edi=00000000
    eip=0eeffca8 esp=0012ec18 ebp=027d1c98 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    0eeffca8 33c0            xor     eax,eax
    0:000> p
    eax=00000000 ebx=0eeffc66 ecx=00000000 edx=0eeffca5 esi=0012ec8c edi=00000000
    eip=0eeffcaa esp=0012ec18 ebp=027d1c98 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    0eeffcaa 40              inc     eax
    0:000> p
    eax=00000001 ebx=0eeffc66 ecx=00000000 edx=0eeffca5 esi=0012ec8c edi=00000000
    eip=0eeffcab esp=0012ec18 ebp=027d1c98 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    0eeffcab 53              push    ebx
    
    // 调用cpuid指令
    0:000> p
    eax=00000001 ebx=0eeffc66 ecx=00000000 edx=0eeffca5 esi=0012ec8c edi=00000000
    eip=0eeffcac esp=0012ec14 ebp=027d1c98 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    0eeffcac 0fa2            cpuid
    0:000> p
    eax=000306a9 ebx=00010800 ecx=ffba2203 edx=0f8bfbff esi=0012ec8c edi=00000000
    eip=0eeffcae esp=0012ec14 ebp=027d1c98 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    0eeffcae 5b              pop     ebx
    0:000> p
    eax=000306a9 ebx=0eeffc66 ecx=ffba2203 edx=0f8bfbff esi=0012ec8c edi=00000000
    eip=0eeffcaf esp=0012ec18 ebp=027d1c98 iopl=0         nv up ei pl nz na po nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    0eeffcaf c1f91f          sar     ecx,1Fh
    
    // 判断最高位是否为1
    0:000> p
    eax=000306a9 ebx=0eeffc66 ecx=ffffffff edx=0f8bfbff esi=0012ec8c edi=00000000
    eip=0eeffcb2 esp=0012ec18 ebp=027d1c98 iopl=0         nv up ei ng nz na pe cy
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000287
    0eeffcb2 f6c101          test    cl,1
    
    // 我们在调试器内手动清零 ecx，使后续行为能够正常触发
    0:000> r ecx=0
    
    // 依据 cpuid 的结果判断是否位于虚拟机，若位于虚拟机则直接返回
    0:000> p
    eax=000306a9 ebx=0eeffc66 ecx=00000000 edx=0f8bfbff esi=0012ec8c edi=00000000
    eip=0eeffcb5 esp=0012ec18 ebp=027d1c98 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    0eeffcb5 0f8538030000    jne     0eeffff3                                [br=0]
    

###  启动并注入 notepad

执行流正常往下后，shellcode 会在某特定位置(jmp eax)处循环调用所需用到的函数，我们对该调用点下断输出。可以看到 shellcode
按顺序调用了下述 API (VirtualQuery+5 调用由于太多，所以没有列出)：

    
    
    > KERNELBASE!LoadLibraryExA+0x5
    > KERNELBASE!GlobalAlloc
    > KERNELBASE!GlobalAlloc
    > KERNELBASE!CreateFileW+0x5
    > KERNELBASE!GetFileSize
    > KERNELBASE!SetFilePointer
    > KERNELBASE!ReadFile
    > kernel32!CreateProcessA+0x5
    > KERNELBASE!VirtualAllocEx
    > KERNELBASE!WriteProcessMemory+0x5
    > KERNELBASE!CreateRemoteThread
    
    // 调试器内观察
    0:000> bp 0eeffd31 ".if(eax != KERNELBASE!VirtualQuery+0x5){u eax; g;}.else{g;}"
    
    0:000> g
    KERNELBASE!LoadLibraryExA+0x5:
    75968d6b 51              push    ecx
    75968d6c 51              push    ecx
    75968d6d ff7508          push    dword ptr [ebp+8]
    75968d70 8d45f8          lea     eax,[ebp-8]
    75968d73 50              push    eax
    75968d74 e83cfaffff      call    KERNELBASE!Basep8BitStringToDynamicUnicodeString (759687b5)
    75968d79 85c0            test    eax,eax
    75968d7b 741e            je      KERNELBASE!LoadLibraryExA+0x35 (75968d9b)
    
    KERNELBASE!GlobalAlloc:
    7596d6de 6a18            push    18h
    7596d6e0 6858d79675      push    offset KERNELBASE!BemFreeContract+0x3e0 (7596d758)
    7596d6e5 e8b63fffff      call    KERNELBASE!_SEH_prolog4 (759616a0)
    7596d6ea 33ff            xor     edi,edi
    7596d6ec 897de4          mov     dword ptr [ebp-1Ch],edi
    7596d6ef 897ddc          mov     dword ptr [ebp-24h],edi
    7596d6f2 8b4508          mov     eax,dword ptr [ebp+8]
    7596d6f5 a98d80ffff      test    eax,0FFFF808Dh
    
    KERNELBASE!GlobalAlloc:
    7596d6de 6a18            push    18h
    7596d6e0 6858d79675      push    offset KERNELBASE!BemFreeContract+0x3e0 (7596d758)
    7596d6e5 e8b63fffff      call    KERNELBASE!_SEH_prolog4 (759616a0)
    7596d6ea 33ff            xor     edi,edi
    7596d6ec 897de4          mov     dword ptr [ebp-1Ch],edi
    7596d6ef 897ddc          mov     dword ptr [ebp-24h],edi
    7596d6f2 8b4508          mov     eax,dword ptr [ebp+8]
    7596d6f5 a98d80ffff      test    eax,0FFFF808Dh
    
    KERNELBASE!CreateFileW+0x5:
    7596a855 8b4518          mov     eax,dword ptr [ebp+18h]
    7596a858 83ec64          sub     esp,64h
    7596a85b 48              dec     eax
    7596a85c 0f8499e5ffff    je      KERNELBASE!CreateFileW+0x57 (75968dfb)
    7596a862 48              dec     eax
    7596a863 0f8468360000    je      KERNELBASE!CreateFileW+0x4e (7596ded1)
    7596a869 48              dec     eax
    7596a86a 0f8579360000    jne     KERNELBASE!CreateFileW+0x14 (7596dee9)
    
    KERNELBASE!GetFileSize:
    7596de8b 8bff            mov     edi,edi
    7596de8d 55              push    ebp
    7596de8e 8bec            mov     ebp,esp
    7596de90 51              push    ecx
    7596de91 51              push    ecx
    7596de92 8d45f8          lea     eax,[ebp-8]
    7596de95 50              push    eax
    7596de96 ff7508          push    dword ptr [ebp+8]
    
    KERNELBASE!SetFilePointer:
    7596df0d 8bff            mov     edi,edi
    7596df0f 55              push    ebp
    7596df10 8bec            mov     ebp,esp
    7596df12 8b4508          mov     eax,dword ptr [ebp+8]
    *** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:Program FilesHncCommon80HncLibeay8.dll - 
    7596df15 2503000010      and     eax,offset HncLibeay8!Ordinal1003+0x3 (10000003)
    7596df1a 83ec28          sub     esp,28h
    7596df1d 83f803          cmp     eax,3
    7596df20 0f84405f0100    je      KERNELBASE!SetFilePointer+0x15 (75983e66)
    
    KERNELBASE!ReadFile:
    7596e013 6a18            push    18h
    7596e015 6898e09675      push    offset KERNELBASE!BemFreeContract+0x1b0 (7596e098)
    7596e01a e88136ffff      call    KERNELBASE!_SEH_prolog4 (759616a0)
    7596e01f 33c9            xor     ecx,ecx
    7596e021 894de0          mov     dword ptr [ebp-20h],ecx
    7596e024 33c0            xor     eax,eax
    7596e026 8d7de4          lea     edi,[ebp-1Ch]
    7596e029 ab              stos    dword ptr es:[edi]
    
    kernel32!CreateProcessA+0x5:
    75b92087 6a00            push    0
    75b92089 ff752c          push    dword ptr [ebp+2Ch]
    75b9208c ff7528          push    dword ptr [ebp+28h]
    75b9208f ff7524          push    dword ptr [ebp+24h]
    75b92092 ff7520          push    dword ptr [ebp+20h]
    75b92095 ff751c          push    dword ptr [ebp+1Ch]
    75b92098 ff7518          push    dword ptr [ebp+18h]
    75b9209b ff7514          push    dword ptr [ebp+14h]
    
    KERNELBASE!VirtualAllocEx:
    759679b8 8bff            mov     edi,edi
    759679ba 55              push    ebp
    759679bb 8bec            mov     ebp,esp
    759679bd 51              push    ecx
    759679be 8b4510          mov     eax,dword ptr [ebp+10h]
    759679c1 8945fc          mov     dword ptr [ebp-4],eax
    759679c4 8b450c          mov     eax,dword ptr [ebp+0Ch]
    759679c7 894510          mov     dword ptr [ebp+10h],eax
    
    KERNELBASE!WriteProcessMemory+0x5:
    759842f8 51              push    ecx
    759842f9 51              push    ecx
    759842fa 8b450c          mov     eax,dword ptr [ebp+0Ch]
    759842fd 53              push    ebx
    759842fe 8b5d14          mov     ebx,dword ptr [ebp+14h]
    75984301 56              push    esi
    75984302 8b35d0119675    mov     esi,dword ptr [KERNELBASE!_imp__NtProtectVirtualMemory (759611d0)]
    75984308 57              push    edi
    
    KERNELBASE!CreateRemoteThread:
    759938c0 8bff            mov     edi,edi
    759938c2 55              push    ebp
    759938c3 8bec            mov     ebp,esp
    759938c5 ff7520          push    dword ptr [ebp+20h]
    759938c8 6a00            push    0
    759938ca ff751c          push    dword ptr [ebp+1Ch]
    759938cd ff7518          push    dword ptr [ebp+18h]
    759938d0 ff7514          push    dword ptr [ebp+14h]
    
    ...
    0:000> |
    .  0    id: 960    create    name: Hwp.exe
       1    id: 970    child    name: notepad.exe // 创建notepad.exe进程并执行远程线程注入
    
    0:000> g
    (970.e7c): Break instruction exception - code 80000003 (first chance)
    eax=00000000 ebx=00000000 ecx=001bf920 edx=777870b4 esi=fffffffe edi=00000000
    eip=777e04f6 esp=001bf93c ebp=001bf968 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    ntdll!LdrpDoDebuggerBreak+0x2c:
    777e04f6 cc              int     3
    
    // 切换到notepad.exe进程进行调试
    1:004> |.
    .  1    id: 970    child    name: notepad.exe
    

###  写入 wsss.dll

    
    
    // 观察发现 notepad.exe 进程会写入一个 wsss.dll 动态库到temp目录
    1:004> bp ntdll!ZwWriteFile+5
    
    1:004> g
    Breakpoint 3 hit
    eax=0000018c ebx=000000a4 ecx=00000000 edx=759618d4 esi=00000000 edi=001bfd7c
    eip=77786a6d esp=001bfce4 ebp=001bfd44 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    ntdll!ZwWriteFile+0x5:
    77786a6d ba0003fe7f      mov     edx,offset SharedUserData!SystemCallStub (7ffe0300)
    
    1:004> dd esp l8
    001bfce4  75967584 000000a4 00000000 00000000
    001bfcf4  00000000 001bfd24 000601e6 00022600
    
    // 写入的Buffer为PE文件
    1:004> dc 000601e6
    000601e6  00905a4d 00000003 00000004 0000ffff  MZ..............
    000601f6  000000b8 00000000 00000040 00000000  ........@.......
    00060206  00000000 00000000 00000000 00000000  ................
    00060216  00000000 00000000 00000000 000000e8  ................
    00060226  0eba1f0e cd09b400 4c01b821 685421cd  ........!..L.!Th
    00060236  70207369 72676f72 63206d61 6f6e6e61  is program canno
    00060246  65622074 6e757220 206e6920 20534f44  t be run in DOS 
    00060256  65646f6d 0a0d0d2e 00000024 00000000  mode....$.......
    
    1:004> !handle a4 0xf
    Handle a4
      Type             File
      Attributes       0
      GrantedAccess    0x120196:
             ReadControl,Synch
             Write/Add,Append/SubDir/CreatePipe,WriteEA,ReadAttr,WriteAttr
      HandleCount      2
      PointerCount     3
      No Object Specific Information available
    

查看一下0xa4句柄对应的文件名称，可以看到为temp目录下的wsss.dll

![](https://p1.ssl.qhimg.com/t013286e9b11764e0d4.png)

###  其他行为

    
    
    explorer.exe
        load： C:Usersuser_nameAppDataLocalTempwsss.dll
        create process：C:WindowsSystem32sysprepsysprep.exe
    
    sysprep.exe
        write：C:Windowssystem32iconsvc.dll
        load：C:Windowssystem32iconsvc.dll
    

## 哈希

    
    
    wsss.dll && iconsvc.dll：
    3ba8a6815f828dfc518a0bdbd27bba5b
    
    漏洞样本：
    54783422cfd7029a26a3f3f5e9087d8a
    b5b6e93ab27cec75f07af2a3a6a40926
    800866bbab514657969996210bcf727b
    ead682b889218979b1f2f1527227af9b
    f09ea2a841114121f32211faac553e1b
    9daf088fe4c9a9580216e98dbb7d1fca
    3ec69ee7135272e5bed3ea5378ade6ee
    33874577bf54d3c209925c9def880eb9
    af792a34548a2038f034ea9a6ff0639a
    

## 链接

<http://asec.ahnlab.com/1015>

<http://asec.ahnlab.com/1035>

<http://d.hatena.ne.jp/Kango/20141223/1419269574>

<http://ex3llo.tistory.com/31>

<http://www.nurilab.co.kr/?p=114>

<https://consen.github.io/2016/09/11/Anti-VM-via-CPUID/>

<https://www.fireeye.com/content/dam/fireeye-www/global/en/blog/threat-research/FireEye_HWP_ZeroDay.pdf>

<https://cdn.hancom.com/link/docs/%ED%95%9C%EA%B8%80%EB%AC%B8%EC%84%9C%ED%8C%8C%EC%9D%BC%ED%98%95%EC%8B%9D_5.0_revision1.2.pdf>

## 工具

<https://www.nurilab.net/hwpscan2>

<https://github.com/yujgewt/fewawef/blob/master/tag_parser.py>

<https://www.hancom.com/cs_center/csDownload.do>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **银雁冰** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/163085](/post/id/163085)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [HWP](/tag/HWP)
  * [类型混淆](/tag/类型混淆)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t01f54e4e260feda379.jpg) 银雁冰

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

