# CVE-2016-4203分析：Adobe Acrobat和Reader 的CoolType处理导致的堆溢出漏洞

阅读量 **111821**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-07-21 16:59:39

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<https://blog.fortinet.com/2016/07/20/analysis-of-cve-2016-4203-adobe-acrobat-and-reader-cooltype-handling-heap-overflow-vulnerability>

译文仅供参考，具体内容表达以及含义原文为准。

**综述**

**最近,Adobe公司修复了Adobe Acrobat和Reader中的一些安全漏洞。其中一个是我们近期发现的堆缓冲区溢出漏洞(CVE – 2016 –
4203)。本博客中,我们想分享一些我们对这个漏洞的分析。**

**概念验证**

可以通过用Adobe Reader
DC打开PoC文件“poc_minimized.pdf”的方式来重现这个漏洞。当打开该文件时,AcroRd32.exe就会崩溃,崩溃信息如下所示:

    
    
    (8de0.6bc4): Access violation - code c0000005 (first chance)
    First chance exceptions are reported before any exception handling.
    This exception may be expected and handled.
    eax=097eeeed ebx=00000015 ecx=097ef6e0 edx=0000cc6c esi=2952d000 edi=00000024
    eip=0959a23c esp=2911e5f8 ebp=2911e608 iopl=0         nv up ei pl nz na po nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010202
    CoolType!CTInit+0x45ef1:
    0959a23c 0fb606          movzx   eax,byte ptr [esi]         ds:002b:2952d000=??
     
    0:022> kb
     # ChildEBP RetAddr  Args to Child             
    WARNING: Stack unwind information not available. Following frames may be wrong.
    00 2911e608 09598db1 097eee15 097ef564 097ef44c CoolType!CTInit+0x45ef1
    01 2911e674 095939a0 17e9cc38 17e9cd98 17e9cd58 CoolType!CTInit+0x44a66
    02 2911e6d0 095935c3 17e9cc38 17e9cd98 17e9cd58 CoolType!CTInit+0x3f655
    03 2911e720 0958d9a3 17e9cc38 17e9cd98 17e9cd58 CoolType!CTInit+0x3f278
    04 2911e784 0958d79c 00000001 2911e7d8 00000001 CoolType!CTInit+0x39658
    05 2911e79c 095a6cb0 2911e8a8 2911e7d8 1a99cf68 CoolType!CTInit+0x39451
    06 2911e8fc 095a6996 1a99cf68 097f61a8 2911ea88 CoolType!CTInit+0x52965
    07 2911eac4 095a614e 2911ecb8 00000000 097f6480 CoolType!CTInit+0x5264b
    08 2911eb90 095a506f 773dfa00 00000000 00000001 CoolType!CTInit+0x51e03
    09 2911ef58 095a468a 00000025 20f02fec 00001088 CoolType!CTInit+0x50d24
    0a 2911ef98 095a3691 20f02fe0 00000002 2911f028 CoolType!CTInit+0x5033f
    0b 2911f100 095a32c7 2911f518 2911f8ac 0000044a CoolType!CTInit+0x4f346
    0c 2911f150 0908a44c 145aae2c 2911f518 2911f8ac CoolType!CTInit+0x4ef7c
    0d 2911f258 0906bab0 2911f34c 00000000 21d6629c AGM!AGMInitialize+0x51bf0
    0e 2911f268 0906b98f 00000000 f7510c27 20d6cf70 AGM!AGMInitialize+0x33254
    0f 2911f280 0906ba9c 00000081 21cb6d00 21cb6d00 AGM!AGMInitialize+0x33133
    10 2911f9ac 0906182e 090004ca 00001fa0 2911fa01 AGM!AGMInitialize+0x33240
    11 2911f9bc 09080a4d 21d76fe8 00000053 00000000 AGM!AGMInitialize+0x28fd2
    12 2911fa01 00000000 c8000000 5021ca6f 0027c3d2 AGM!AGMInitialize+0x481f1
     
    0:022> !heap -p -a esi
        address 2952d000 found in
        _DPH_HEAP_ROOT @ 3d01000
        in busy allocation (  DPH_HEAP_BLOCK:         UserAddr         UserSize -         VirtAddr         VirtSize)
                                                           293c3924:         2952cf40               c0 -         2952c000             2000
        6a749abc verifier!AVrfDebugPageHeapAllocate+0x0000023c
        7749d836 ntdll!RtlDebugAllocateHeap+0x0000003c
        773ffb40 ntdll!RtlpAllocateHeap+0x000000f0
        773fdecb ntdll!RtlpAllocateHeapInternal+0x0000027b
        773fdc2e ntdll!RtlAllocateHeap+0x0000002e
        6854ed63 MSVCR120!malloc+0x00000049 [f:ddvctoolscrtcrtw32heapmalloc.c @ 92]
        095550fc CoolType!CTInit+0x00000db1
        095589db CoolType!CTInit+0x00004690

**分析**

这个漏洞是堆缓冲区溢出漏洞的一个实例。让我们先看看这个特别制作的PDF文件。我们将这个最小化的PoC文件和正常的PDF文件进行了对比，如下所示。

图1：PoC文件与原始PDF文件

图2.用010编辑器对PoC文件的解析

从图1和图2我们可以看到，PoC文件和原始PDF文件的唯一区别是位于obj 17上的偏移值为0x30e3上的一个字节。该对象的结构如下所示：

    
    
    17 0 obj
    <
    /Length 14790
    /Filter [/FlateDecode]
    /DecodeParms [null]
    >> 
    stream
    …
    endstream
    endobj

问题是该对象到底存储了什么类型的数据？我们在PDF文件中发现了引用obj 17的对象，如下所示:

    
    
    8 0 obj
    <
    /FontFile2 17 0 R
    /FontName /AAAAAA+ComicSansMS
    /Flags 32
    /ItalicAngle 0
    /Ascent 1102
    /Descent -312
    /CapHeight 0
    /StemV 0
    /Type /FontDescriptor
    /CIDSet 19 0 R
    >> 
    endobj

从字段“/ FontFile2 17 0 R”中我们可以知道obj 17存储了一个字体文件。该字体文件的数据编码使用了obj
17中的FlateDecode。想要了解数据压缩的更多信息,请参阅https://tools.ietf.org/html/rfc1951。

Zlib是一个C语言库,实现了数据压缩算法。我们可以用它来解压obj 17中的数据。PoC文件中的obj
17解压数据存储在output.dat文件中，长度为0x4650。原始PDF文件中的obj
17解压数据存储在output_original.dat文件中，长度也是0x4650。下面是output.dat文件和output_original.dat文件之间的对比：

图3.PoC的字体文件(output.dat)与原始字体文件(output_original.dat)的对比

我们可以看到有大约一百个字节是不相同的。那么,下一个问题是找出到底是什么数据触发了这个漏洞。这需要一些调试技巧，让我们先回到Windbg。

    
    
    0:022> r
    eax=097eeeed ebx=00000015 ecx=097ef6e0 edx=0000cc6c esi=2952d000 edi=00000024
    eip=0959a23c esp=2911e5f8 ebp=2911e608 iopl=0         nv up ei pl nz na po nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010202
    CoolType!CTInit+0x45ef1:
    0959a23c 0fb606          movzx   eax,byte ptr [esi]         ds:002b:2952d000=??
     
    0:022> !heap -p -a esi
        address 2952d000 found in
        _DPH_HEAP_ROOT @ 3d01000
        in busy allocation (  DPH_HEAP_BLOCK:         UserAddr         UserSize -         VirtAddr         VirtSize)
                                                           293c3924:         2952cf40               c0 -         2952c000             2000
        6a749abc verifier!AVrfDebugPageHeapAllocate+0x0000023c
        7749d836 ntdll!RtlDebugAllocateHeap+0x0000003c
        773ffb40 ntdll!RtlpAllocateHeap+0x000000f0
        773fdecb ntdll!RtlpAllocateHeapInternal+0x0000027b
        773fdc2e ntdll!RtlAllocateHeap+0x0000002e
        6854ed63 MSVCR120!malloc+0x00000049 [f:ddvctoolscrtcrtw32heapmalloc.c @ 92]
        095550fc CoolType!CTInit+0x00000db1
        095589db CoolType!CTInit+0x00004690
        …
     
    0:022> db 2952cf40 Lc0
    2952cf40  00 02 00 b3 ff fb 01 bf-05 da 00 0b 00 23 00 55  .............#.U
    2952cf50  40 36 06 38 00 1e 12 1e-06 20 25 30 25 50 25 c0  @6.8..... %0%P%.
    2952cf60  25 04 80 25 90 25 a0 25-03 09 38 03 18 15 1b 18  %..%.%.%..8.....
    2952cf70  38 0f 21 1f 25 2f 25 3f-25 7f 25 04 1f 0c bf 0c  8.!.%/%?%.%.....
    2952cf80  02 50 0c 7f 0c 02 0c 25-10 d6 5d 71 5d 7d c4 c4  .P.....%..]q]}..
    2952cf90  18 fd 7d c4 c4 18 10 7d-d4 18 ed 5d 71 00 3f 2f  ..}....}...]q.?/
    2952cfa0  10 d6 ed 31 30 01 22 26-35 34 36 33 32 1f 00 ed  ...10."&54632...
    2952cfb0  02 03 14 16 00 ed 06 23-22 26 35 34 26 35 34 12  .......#"&54&54.
    2952cfc0  35 34 36 33 32 1f 00 ed-02 01 4a 30 46 46 30 30  54632.....J0FF00
    2952cfd0  45 45 03 07 36 2c 2b 37-07 14 37 2b 2b 37 14 04  EE..6,+7..7++7..
    2952cfe0  f2 44 30 30 44 44 30 30-44 fc d4 3c ef 3c 2c 38  .D00DD00D..<.<,8
    2952cff0  38 2c 3c ef 3c 5e 01 19-5e 2d 38 38 2d 5e fe e7  8,<.<^..^-88-^..

从上面的输出中可以看到,当对一个起始位置为0x2952cf40，大小为0xc0的堆缓冲区进行操作时，触发了一个界外内存访问。接下来,我们从这个堆缓冲区中搜索一些数据,比如output.dat文件中的|
00 02 00 b3|。

图4.output.dat中的数据搜索结果

我们在偏移值为0x2d0b的地方发现了它,而且它只出现了一次。然后,我们使用010编辑器中的TTFTemplate.bt解析了这个字体文件,并在“glyp”表中找到了|
00 02 00 B3
|。接下来,我们相应的分别从output.dat和output_original.dat的“glyp”表中提取大小为0xc0的数据。下面是它们之间的比较：

图5.glyph_poc.dat和glyph_original.dat之间的比较

如您所见,
它们之间有三个不同的地方。“glyf”表包含的数据定义了字体的字形符号的外观。这包括描述组成一个字形符号轮廓的点的规范和描述字形符号的网格的指令。“glyf”表支持简单的符号和复合符号的定义,也就是说,支持字形符号由其他符号组合而成。字体的字形符号数量仅由“head”表的值限制。字体中符号的放置顺序是任意的。

每个字形的开始带有以下头信息:

显然,glyph_poc.dat存储了一个简单的字形符号,因为前两个字节的值0x0002大于零。

一个简单的字形符号的结构如下所示:

基于上面的“字形”表的规范,我们尝试着对它进行了解析，并用不同的颜色进行标记，如下所示：

图6.解析简单字形

然后我们跟踪Adobe Reader是如何处理这个简单字形的，我们在Windbg中设置了以下断点：

bu CoolType!CTInit+0x44a61 " .if((poi(poi(poi(esp+0xc))) & 0x0`ffffffff) =
0x0`b3000200) { .printf "hit:\n";} .else {gc}"

当运行到该断点时,我们得到了以下调试信息:

    
    
    0:021> g
    (8de0.6bc4): C++ EH exception - code e06d7363 (first chance)
    hit:
    eax=097ef6e0 ebx=097ef6d0 ecx=097eeda0 edx=2911e6fc esi=097ef758 edi=097ef756
    eip=09598dac esp=2911e610 ebp=2911e674 iopl=0         nv up ei pl zr na pe nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246
    CoolType!CTInit+0x44a61:
    09598dac e8f1110000      call    CoolType!CTInit+0x45c57 (09599fa2)
     
    0:022> dds esp
    2911e610  097eee00 CoolType!CTGetVersion+0x1dd1c8    -->param1
    2911e614  097ef510 CoolType!CTGetVersion+0x1dd8d8    -->param2
    2911e618  097ef3bc CoolType!CTGetVersion+0x1dd784    -->param3
    2911e61c  097ef6e0 CoolType!CTGetVersion+0x1ddaa8    -->param4
    2911e620  17e9cd98                                                                  -->param5
    2911e624  00000001                                                                -->param6
    2911e628  00000002                                                                  -->param7
    2911e62c  097eee58 CoolType!CTGetVersion+0x1dd220
    2911e630  097eee60 CoolType!CTGetVersion+0x1dd228
    2911e634  097ef756 CoolType!CTGetVersion+0x1ddb1e
    2911e638  097ef758 CoolType!CTGetVersion+0x1ddb20
    2911e63c  2911e6c4
    2911e640  2911e6c8
    2911e644  097ef6d0 CoolType!CTGetVersion+0x1dda98
    2911e648  17e9cdc4
    2911e64c  17e9cf84
    2911e650  00000015
    …
     
    0:022> dd 097ef6e0 L4
    097ef6e0  2952cf40 2952cf4a 2952d000 00000000
     
    0:022> db 2952cf40  lc0
    2952cf40  00 02 00 b3 ff fb 01 bf-05 da 00 0b 00 23 00 55  .............#.U
    2952cf50  40 36 06 38 00 1e 12 1e-06 20 25 30 25 50 25 c0  @6.8..... %0%P%.
    2952cf60  25 04 80 25 90 25 a0 25-03 09 38 03 18 15 1b 18  %..%.%.%..8.....
    2952cf70  38 0f 21 1f 25 2f 25 3f-25 7f 25 04 1f 0c bf 0c  8.!.%/%?%.%.....
    2952cf80  02 50 0c 7f 0c 02 0c 25-10 d6 5d 71 5d 7d c4 c4  .P.....%..]q]}..
    2952cf90  18 fd 7d c4 c4 18 10 7d-d4 18 ed 5d 71 00 3f 2f  ..}....}...]q.?/
    2952cfa0  10 d6 ed 31 30 01 22 26-35 34 36 33 32 1f 00 ed  ...10."&54632...
    2952cfb0  02 03 14 16 00 ed 06 23-22 26 35 34 26 35 34 12  .......#"&54&54.
    2952cfc0  35 34 36 33 32 1f 00 ed-02 01 4a 30 46 46 30 30  54632.....J0FF00
    2952cfd0  45 45 03 07 36 2c 2b 37-07 14 37 2b 2b 37 14 04  EE..6,+7..7++7..
    2952cfe0  f2 44 30 30 44 44 30 30-44 fc d4 3c ef 3c 2c 38  .D00DD00D..<.<,8
    2952cff0  38 2c 3c ef 3c 5e 01 19-5e 2d 38 38 2d 5e fe e7  8,<.<^..^-88-^..
     
    0:022> !heap -p -a 2952cf40 
        address 2952cf40 found in
        _DPH_HEAP_ROOT @ 3d01000
        in busy allocation (  DPH_HEAP_BLOCK:         UserAddr         UserSize -         VirtAddr         VirtSize)
                                                           293c3924:         2952cf40               c0 -         2952c000             2000
        6a749abc verifier!AVrfDebugPageHeapAllocate+0x0000023c
        7749d836 ntdll!RtlDebugAllocateHeap+0x0000003c
        773ffb40 ntdll!RtlpAllocateHeap+0x000000f0
        773fdecb ntdll!RtlpAllocateHeapInternal+0x0000027b
        773fdc2e ntdll!RtlAllocateHeap+0x0000002e
        6854ed63 MSVCR120!malloc+0x00000049 [f:ddvctoolscrtcrtw32heapmalloc.c @ 92]
        095550fc CoolType!CTInit+0x00000db1
        095589db CoolType!CTInit+0x00004690
        ...

从上面的输出中可以看到,堆缓冲区的地址0x2952cf40处存储了大小为0xc0的简单字形。这与glyph_poc.dat中的数据相匹配。地址0x2952cf4a指向endPtsOfContours[2]，而地址0x2952d000指向简单字形的结尾。

以下是简单字形的一些字段的值：

    
    
    endPtsOfContours [0]:   00 0b  
    endPtsOfContours [1]:  00 23
    instructionLength: 00 55 
    instructions[n]:   40 36 06 38 00 1e 12 1e-06 20 25 30 25 50 25 c0 
                                  25 04 80 25 90 25 a0 25-03 09 38 03 18 15 1b 18
                                  38 0f 21 1f 25 2f 25 3f-25 7f 25 04 1f 0c bf 0c
                                 02 50 0c 7f 0c 02 0c 25-10 d6 5d 71 5d 7d c4 c4 
                                18 fd 7d c4 c4 18 10 7d-d4 18 ed 5d 71 00 3f 2f 
                                10 d6 ed 31 30
    Flags[]: ……
    xCoordinates[ ]: …….
    yCoordinates[ ]: …….

我们继续跟踪简单字形中的“Flags”字段是如何处理的。在IDA
Pro中,下面是处理“Flags”字段的代码分支。它的长度是0x24(endPtsOfContours[1]+ 1 = 0x23 + 0x1 = 0
x24)。  

图7.处理“Flags”字段的分支

在Windbg中,我们得到以下调试信息:

    
    
    0:022> bu 0959a132
     
    0:022> g
    Breakpoint 1 hit
    eax=0000004d ebx=097eee00 ecx=00000000 edx=00000024 esi=2952cfa5 edi=00000000
    eip=0959a132 esp=2911e5f8 ebp=2911e608 iopl=0         nv up ei ng nz ac pe cy
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000297
    CoolType!CTInit+0x45de7:
    0959a132 8bca            mov     ecx,edx
     
    0:022> db esi
    2952cfa5  01 22 26 35 34 36 33 32-1f 00 ed 02 03 14 16 00  ."&54632........
    2952cfb5  ed 06 23 22 26 35 34 26-35 34 12 35 34 36 33 32  ..#"&54&54.54632
    2952cfc5  1f 00 ed 02 01 4a 30 46-46 30 30 45 45 03 07 36  .....J0FF00EE..6
    2952cfd5  2c 2b 37 07 14 37 2b 2b-37 14 04 f2 44 30 30 44  ,+7..7++7...D00D
    2952cfe5  44 30 30 44 fc d4 3c ef-3c 2c 38 38 2c 3c ef 3c  D00D..<.<,88,<.<
    2952cff5  5e 01 19 5e 2d 38 38 2d-5e fe e7 ?? ?? ?? ?? ??  ^..^-88-^..?????
    2952d005  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????
    2952d015  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????
     
    0:022> db ebx
    097eee00  01 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    097eee10  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    097eee20  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    097eee30  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    097eee40  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
    097eee50  00 00 00 00 00 00 00 00-00 00 0c 00 00 00 00 00  ................
    097eee60  0b 00 23 00 00 00 00 00-00 00 00 00 00 00 00 00  ..#.............
    097eee70  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................

缓冲区的地址0 x097eee00用于存储解析“Flags”字段的结果。

下面的C代码来自IDA Pro的sub_8049FA2函数，用来处理“Flags”字段:

    
    
    //parse the Flags field which length is 0x24, the result is stored in param a1.  v20 points to the offset of data in the glyph object.
    do 
          {
            if ( v14 )
            {
              v28 -= v14;
              v54 = v28;
              if ( v28 < 0 )
                return 5133;
              if ( v14 )
              {
                LOBYTE(v50) = *(v27 - 1);
                memset(v27, v50, v14);
                v27 += v14;
                do
                  --v14;
                while ( v14 );
                v28 = v54;

下面的C代码来自IDA Pro的sub_8049FA2函数，用来处理“Flags”字段:

    
    
    //parse the Flags field which length is 0x24, the result is stored in param a1.  v20 points to the offset of data in the glyph object.
    do 
          {
            if ( v14 )
            {
              v28 -= v14;
              v54 = v28;
              if ( v28 < 0 )
                return 5133;
              if ( v14 )
              {
                LOBYTE(v50) = *(v27 - 1);
                memset(v27, v50, v14);
                v27 += v14;
                do
                  --v14;
                while ( v14 );
                v28 = v54;
              }
            }
            else
            {
              v29 = *(_BYTE *)v20;
              *v27 = *(_BYTE *)v20;
              if ( v29 & 8 )
              {
                if ( ++v20 > *(_DWORD *)(a4 + 8) )
                  return 5133;
                v14 = *(_BYTE *)v20;
              }
              ++v20;
              ++v27;
              --v28;
              if ( v20 > *(_DWORD *)(a4 + 8) )
                return 5133;
            }
          }
          while ( v28 > 0 );
          if ( v14 )
            return 5121;
          v30 = v55;
          v31 = 0;
          v32 = (char *)a1;  // a1 stores the result of parsing Flags field. |01 22 26 35 34 36 33 32 1f ed ed ed 03 14 16 00 ed ed ed ed ed ed ed 23 22 26 35 34 26 35 34 12 35 34 36 33|
          v33 = 0;
          v51 = a1;
          v48 = 0;

在解析完“Flags”字段之后,我们看到了以下调试信息:

    
    
    0:022> t
    eax=097ef6e0 ebx=097eee24 ecx=00000000 edx=00000006 esi=2952cfc4 edi=00060000
    eip=0959a1ab esp=2911e5f8 ebp=2911e608 iopl=0         nv up ei pl zr na pe nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246
    CoolType!CTInit+0x45e60:
    0959a1ab 8b7d30          mov     edi,dword ptr [ebp+30h] ss:002b:2911e638=00000024                       
     
    0:022> db ebx-24 L30
    097eee00  01 22 26 35 34 36 33 32-1f ed ed ed 03 14 16 00  ."&54632........
    097eee10  ed ed ed ed ed ed ed 23-22 26 35 34 26 35 34 12  .......#"&54&54.
    097eee20  35 34 36 33 00 00 00 00-00 00 00 00 00 00 00 00  5463............               
     
    0:022> db esi
    2952cfc4  32 1f 00 ed 02 01 4a 30-46 46 30 30 45 45 03 07  2.....J0FF00EE..
    2952cfd4  36 2c 2b 37 07 14 37 2b-2b 37 14 04 f2 44 30 30  6,+7..7++7...D00
    2952cfe4  44 44 30 30 44 fc d4 3c-ef 3c 2c 38 38 2c 3c ef  DD00D..<.<,88,<.
    2952cff4  3c 5e 01 19 5e 2d 38 38-2d 5e fe e7 ?? ?? ?? ??  <^..^-88-^..????
    2952d004  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????
    2952d014  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????
    2952d024  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????
    2952d034  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????

从图5我们可以看到在“Flags”字段中存在三种不同字节，这将导致一个完全不同的结果。

结果存储在一个起始地址为0x097eee00，大小为0x24的缓冲区中。然后这个缓冲区用来解析xCoordinates[]和yCoordinates[]字段。下面的C代码来自IDA
Pro的sub_8049FA2函数，用来处理xCoordinates[]字段:

    
    
    v48 = 0;
          if ( v55 > 0 )  //handling xCoordinates, the result is stored in param a3. 
            {
            v34 = 0;
            do
            {
              v35 = *v32;
              if ( v35 & 2 )
              {
                v36 = (v35 & 0x10) == 0;
                v37 = *(_BYTE *)v20;
                if ( v36 )
                  v34 -= v37;
                else
                  v34 += v37;
                ++v20;
              }
              else if ( !(v35 & 0x10) )
              {
                v38 = *(_BYTE *)(v20 + 1);
                v34 += _byteswap_ushort(*(_WORD *)v20);
                v33 = v48;
                v20 += 2;
              }
              *(_DWORD *)a3 = v34;
              a3 += 4;
              v32 = (char *)v51 + 1;
              v51 = (char *)v51 + 1;
              v30 = v55;
              if ( v20 > *(_DWORD *)(a4 + 8) )
                return 5133;
              v48 = ++v33;
            }
            while ( v33 < v55 );
          }

处理完“xCoordinates”后,我们发现以下调试信息:

    
    
    0:022> t
    eax=097eee24 ebx=00000000 ecx=00000024 edx=0000efeb esi=2952cfeb edi=00000024
    eip=0959a224 esp=2911e5f8 ebp=2911e608 iopl=0         nv up ei pl zr na pe nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246
    CoolType!CTInit+0x45ed9:
    0959a224 895d28          mov     dword ptr [ebp+28h],ebx ss:002b:2911e630=097eee24
     
    0:022> db esi
    2952cfeb  3c ef 3c 2c 38 38 2c 3c-ef 3c 5e 01 19 5e 2d 38  <.<,88,<.<^..^-8
    2952cffb  38 2d 5e fe e7 ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  8-^..???????????
    2952d00b  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????
    2952d01b  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????
     
    0:022> dd 097ef3bc L40
    097ef3bc  0000321f 0000321f 00003132 00003132
    097ef3cc  00003132 00003134 00003135 0000317f
    097ef3dc  000031af 000077f5 ffffa825 ffffed6a
    097ef3ec  ffffed67 ffffed67 ffffed6e 0000239a
    097ef3fc  00004ed1 000055e5 ffff8d10 ffffb847
    097ef40c  ffffcc4b ffffbe8f ffffeebf ffffee7b
    097ef41c  ffffee37 ffffee07 ffffee07 ffffee07
    097ef42c  ffffedd7 ffffedd7 ffffedd7 ffffee1b
    097ef43c  ffffee1b ffffee1b ffffef17 ffffefeb
    097ef44c  00000000 00000000 00000000 00000000
    097ef45c  00000000 00000000 00000000 00000000
    097ef46c  00000000 00000000 00000000 00000000
    097ef47c  00000000 00000000 00000000 00000000
    097ef48c  00000000 00000000 00000000 00000000
    097ef49c  00000000 00000000 00000000 00000000
    097ef4ac  00000000 00000000 00000000 00000000

接下来,下面的C代码来自IDA Pro的sub_8049FA2函数，用来处理yCoordinates[]字段:

    
    
    if ( v30 > 0 )   // handle yCoordinates, the result is stored in param a2. 
          {    //v20 points to the following buffer.
                      2952cfeb  3c ef 3c 2c 38 38 2c 3c-ef 3c 5e 01 19 5e 2d 38  <.<,88,<.<^..^-8
                      2952cffb  38 2d 5e fe e7 ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  8-^..???????????
     
            v39 = (char *)a1; // a1 stores the result of parsing the Flags field. |01 22 26 35 34 36 33 32 1f ed ed ed 03 14 16 00 ed ed ed ed ed ed ed 23 22 26 35 34 26 35 34 12 35 34 36 33|
     
            v40 = 0;
            v41 = a4;
            do
            {
              v42 = *v39;
              if ( v42 & 4 )
              {
                v36 = (v42 & 0x20) == 0;
                v43 = *(_BYTE *)v20;   //crash here!
                if ( v36 )
                  v40 -= v43;
                else
                  v40 += v43;
                ++v20;
              }
              else if ( !(v42 & 0x20) )
              {
                v44 = *(_BYTE *)(v20 + 1);
                v40 += _byteswap_ushort(*(_WORD *)v20);
                v41 = a4;
                v20 += 2;
              }
              v45 = (_DWORD *)a2;
              a2 += 4;
              *v45 = v40;
              *(_BYTE *)a1 &= 1u;
              v39 = (char *)a1 + 1;
              a1 = (char *)a1 + 1;
              if ( v20 > *(_DWORD *)(v41 + 8) )
                return 5133;
            }
            while ( ++v31 < v55 );  //v55 is 0x24
          }

发生崩溃时,我们看到了下面的调试信息:

    
    
    0:022> t
    eax=097eeeed ebx=00000015 ecx=097ef6e0 edx=0000cc6c esi=2952d000 edi=00000024
    eip=0959a23c esp=2911e5f8 ebp=2911e608 iopl=0         nv up ei pl nz na po nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000202
    CoolType!CTInit+0x45ef1:
    0959a23c 0fb606          movzx   eax,byte ptr [esi]         ds:002b:2952d000=??
     
    0:022> t
    (8de0.6bc4): Access violation - code c0000005 (first chance)
    First chance exceptions are reported before any exception handling.
    This exception may be expected and handled.
    eax=097eeeed ebx=00000015 ecx=097ef6e0 edx=0000cc6c esi=2952d000 edi=00000024
    eip=0959a23c esp=2911e5f8 ebp=2911e608 iopl=0         nv up ei pl nz na po nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010202
    CoolType!CTInit+0x45ef1:
    0959a23c 0fb606          movzx   eax,byte ptr [esi]         ds:002b:2952d000=??
     
    0:022> dd 097ef510
    097ef510  00003cef 00003cef 00003d2b 00003d57
    097ef520  00003d8f 00003dc7 00003dc7 00003dc7
    097ef530  00003d9b 00003dd7 00003ec6 00003f02
    097ef540  ffff9d03 ffff9cea ffff9c8c ffffc9c4
    097ef550  ffffc9fc ffffca29 ffffca87 ffffcb85
    097ef560  ffffcc6c 00000000 00000000 00000000
    097ef570  00000000 00000000 00000000 00000000
    097ef580  00000000 00000000 00000000 00000000
     
    0:022> db esi L10
    2952d000  ?? ?? ?? ?? ?? ?? ?? ??-?? ?? ?? ?? ?? ?? ?? ??  ????????????????

因为ebx小于edi,循环条件仍然是正确的,程序会继续解析yCoordinates[]字段。虽然esi指向简单符号的结尾,但是它会导致一个界外内存访问。

  

总之,这个漏洞是一个典型的堆缓冲区溢出漏洞。特别的是,这个漏洞是由一个精心制作的PDF文件引发的。该PDF文件包括一个无效字体文件，由于操作数组指针时不当的边界检查，它会导致一个界外内存访问。攻击者可以通过越界访问来达到意想不到的读,写或释放,甚至导致恶意代码插入、控制流劫持或信息泄露攻击。

**缓解措施**

鼓励所有Adobe Acrobat和Reader的用户都升级到该软件的最新版本。此外,部署Fortinet
IPS解决方案的组织机构也已经免受这个签名为Adobe.Acrobat.Reader.CoolType.TTF.Memory.Corruption的漏洞威胁。

本文翻译自360安全播报 [原文链接](https://blog.fortinet.com/2016/07/20/analysis-of-cve-2016-4203-adobe-acrobat-and-reader-cooltype-handling-heap-overflow-vulnerability)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **mpk_no1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84264](/post/id/84264)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](https://blog.fortinet.com/2016/07/20/analysis-of-cve-2016-4203-adobe-acrobat-and-reader-cooltype-handling-heap-overflow-vulnerability)

如若转载,请注明出处： <https://blog.fortinet.com/2016/07/20/analysis-of-cve-2016-4203-adobe-acrobat-and-reader-cooltype-handling-heap-overflow-vulnerability>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t01db4a1d58aa0341cc.jpg) mpk_no1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

