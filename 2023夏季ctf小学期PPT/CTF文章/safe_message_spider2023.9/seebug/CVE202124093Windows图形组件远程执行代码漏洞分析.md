**作者：天融信阿尔法实验室  
原文链接：<https://mp.weixin.qq.com/s/8GOXFfQZOvGB7W-sD6osLA>**

## 0x00前言

Windows图形组件DWrite库是用于高质量文本呈现的用户模式动态库，DWrite库存在远程代码执行漏洞。目前已有POC，POC可以实现任意地址写任意内容。

基于此我们做了分析，分析后得知字体库文件中的”maxp”表内容存在错误数据时，DWrite库使用此数据计算字体所需内存，导致分配内存过小，程序读取字体库中的数据写入数组并越界写入
到另外一个数据结构中，后续将结构中数据作为指针操作其中内容，写入数据和指针都可控。通过分析补丁，补丁修补方案为：取出”maxp”表的另一字段再加4，比较之前畸形数据得到较大值，以此计算需要分配内存大小。

文章包含如下内容：

定位chrome引擎的渲染进程

使用条件记录断点动态调试分析

使用IDA补丁比较静态分析

## 0x01漏洞信息

### 漏洞简述

漏洞名称：（Windows图形组件远程执行代码漏洞）

漏洞编号：（CVE-2021-24093）

漏洞类型：（数组越界写）

漏洞影响：（远程代码执行）

CVSS评分：（8.8）

利用难度：不太容易利用

基础权限：需要用户访问网页

### 组件概述

Microsoft DirectWrite是用于高质量文本呈现的现代Windows
API。它的大部分代码位于DWrite.dll用户模式库中。它用作各种广泛使用的桌面程序（例如Windows上的chrome，Firefox和Edge）的字体光栅化程序。

### 漏洞利用

使用chrome浏览器访问Web页面，渲染引擎进程异常，导致chorme页面崩溃。

### 漏洞影响

漏洞主要影响Win10的某些版本及Windows Server 2016、2019、2004、20H2等系统。

## 0x02漏洞复现

CVE-2021-21087

### 环境搭建

靶机环境: Windows 1909专业版 x64、chrome 86.0.4240.193 （64位）

poc.html放在本机，漏洞环境也在本机。

### 复现过程

1.将POC文件与poc.ttf放在同一目录下，使用chrome打开poc.html文件。

![](https://images.seebug.org/content/images/2021/03/e2304b9c-7bbf-4932-a8e1-5e574334609f.png-w331s)

2.页面打开，点击确定按钮加载ttf文件。

![](https://images.seebug.org/content/images/2021/03/1f9e5fc6-e387-4996-9da8-f97c8c2639db.png-w331s)
3.浏览器渲染引擎进程崩溃

![](https://images.seebug.org/content/images/2021/03/967661c3-2456-4b32-bc87-8b7526f6a57a.png-w331s)

4.定位进程崩溃地点

（1）打开Html页面时会启动多个chrome进程，首先需要定位到哪个是渲染引擎进程。

（2）先关闭chrome浏览器(否则会影响定位结果)，使用火绒剑来定位渲染引擎进程，清空火绒剑记录内容，开启监控，设置动作过滤包括进程启动和进程退出，点击确定，然后开启监控，如下：
![](https://images.seebug.org/content/images/2021/03/e755b1f5-711e-4f00-a76f-6ff090e86545.png-w331s)

（3）使用chrome打开poc.html，在弹出框上点击确定，之后渲染引擎崩溃，关闭监控，查看监控到的内容，过滤监控内容，只需要包含chrome.exe的记录，如下：

![](https://images.seebug.org/content/images/2021/03/15fa7590-0a3c-4ccc-b653-886323f7b05b.png-w331s)

（4）可以看到最后一个进程退出，进程ID为4228，渲染引擎崩溃，进程应该也会退出，假设最后一个进程是渲染引擎进程，它创建记录是在从上往下数第七个，再试一次，重复(2-3)的过程，这次打开poc.html之后不要点击确定按钮，查看火绒剑记录如下：

![](https://images.seebug.org/content/images/2021/03/17c1efc9-4f8a-4788-a5b6-4535f4c21306.png-w331s)
定位到第七个进程，进程ID为4948，使用Windbg
x64附加此进程，(如果chrome浏览器切换到后台，比如我点击回到桌面，chrome会自动点击确定按钮，导致渲染进程退出，可以先打开windbg，不用切回桌面再打开windbg，或者使用双屏幕也可以。)

附加成功之后，输入g继续运行，然后回到浏览器中，点击确定按钮，windbg断下，如下：

![](https://images.seebug.org/content/images/2021/03/f6b65d5e-bae8-4091-8a76-fa4e5ee177e7.png-w331s)

可以看到引用一个错误的内存地址，发生异常，可知已经定位到正确的渲染进程。

## **0x03漏洞分析**

### 基本信息

漏洞文件：DWrite.dll

漏洞函数：`fsg_ExecuteGlyph`

漏洞对象：TrueType字体中的”maxp”表

### 背景知识

TrueType字体通常包含在单个TrueType字体文件中，其后缀为.TTF。TrueType中的所有数据都使用big-endian编码，TTF文件中包含了字体的版本号和几个表，每个表都有一个TableEntry结构项，TableEntry结构包含了资源标记、校验和、偏移量和每个表的大小。下面是TrueType字体目录的C语言定义:

    
    
    typedef sturct
    
    {
    
    char  tag[4];
    
    ULONG  checkSum;
    
    ULONG  offset;
    
    ULONG  length;
    
    }TableEntry;
    
    typedef struct
    
    {
    
    Fixed  sfntversion;  //0x00010000  for  version  1.0
    
    USHORT  numTables;
    
    USHORT  searchRange;
    
    USHORT  entrySelector;
    
    USHORT  rangeShift;
    
    TableEntry  entries[1];//variable  number  of  TableEntry
    
    }TableDirectory;

文件开头为TableDirectory结构体，
TableDirectory结构的最后一个字段是可变长度的TableEntry结构的数组，每个结构对应一个表。TrueType字体中的每个表都保存了不同的逻辑信息，其中”maxp”表的作用是描述字体中所需内存分配情况的汇总数据，”maxp”表的内容具体结构为：

    
    
    typedef struct
    
    {
    
    Fixed version;// 0x00010000 for version 1.0
    
    USHORT numGlyphs;
    
    USHORT maxPoints;// 非复合字形中的最大点
    
    USHORT maxContours;
    
    USHORT maxCompositePoints;// 复合字形中的最大点
    
    USHORT maxCompositeContours;
    
    USHORT maxZones;
    
    USHORT maxTwilightPoints;
    
    USHORT maxStorage;
    
    USHORT maxFunctionDefs;
    
    USHORT maxInstructionDefs;
    
    USHORT maxStackElements;
    
    USHORT maxSizeOfInstructions;
    
    USHORT maxComponentElements;// 任何复合字形在“顶级”处引用的最大组件数
    
    USHORT maxComponentDepth;
    
    }

### 详细分析

#### 1\. 基础分析

poc.ttf中数据:

![](https://images.seebug.org/content/images/2021/03/7895b087-0dd6-4bcd-a2cd-3aee9997b0cc.png-w331s)

图中箭头1指向的数据为”maxp”表的TableEntry结构，Offset字段为00000158为箭头2所指向的地方，是”maxp”表内容的具体结构，maxPoints字段值为0(距离箭头2偏移0x6)，`maxCompositePoints`字段为3(距离箭头2偏移0xA)。

AE标志符号的表条目中的x和y增量在运行时会覆盖到另一个数据结构，TTF中内容如下：

![](https://images.seebug.org/content/images/2021/03/e0ab7563-b39a-43d7-b555-05d240231c7c.png-w331s)

异常触发时指令为`add word ptr [r8+56h]，ax`，ax为
`0x9E9F`(图中1标记)，r8为`0x00007A7B00007879`(图中2标记)的地址处，78 79 7A
7B都是TTF中的数据，补0是因为在异常指令之前对x数组和y数组调用了memset初始化内存空间。

poc.html中如下：

![](https://images.seebug.org/content/images/2021/03/d1133d12-61e6-4122-8707-1945aa6750c2.png-w331s)

正常情况下，ttf文件中maxPoints字段值为`0x168`，`maxCompositePoins`字段值为0x2352，在poc.ttf文件中将”maxp”结构中maxPoints字段的值改为0，将`maxCompositePoins`值改为3，当加载并光栅化损坏的”maxp”表的数据时，会导致堆分配缓冲区过小，调用栈如下：

![](https://images.seebug.org/content/images/2021/03/d8f783c2-2880-4212-b91f-3de4b0598361.png-w331s)
当复合字形Æ（AE，HTML实体＆＃198;，U + 00C6）被栅格化时，函数`DWrite! fsg_ExecuteGlyph`崩溃，调用栈如下：

![](https://images.seebug.org/content/images/2021/03/578862f6-bdad-4b87-8139-bec3ec930433.png-w331s)

`fsg_ExecuteGlyph`函数内部对堆块内部的两个整数数组(对应于x和y坐标)进行操作，使用0x148这个长度调用memset来初始化两个数组，但是数组的长度小于0x148，会将跟在数组后面的一个指针置0。

如果字体是一个变量且指定了轴值，它还将调用`TrueTypeRasterizer ::
Implementation::ApplyOutlineVariation-> GlyphOutlineVariationInterpolator ::
ApplyVariation`会从TTF中获取数据赋值给数组内的成员，但是数组较小，所以将数组后面的指针置为TTF中的数据。之后会向这个指针指向的地址中写入数据导致异常。

漏洞库版本如下：

![](https://images.seebug.org/content/images/2021/03/6bf3bce3-19f9-4a84-94fd-a82a0e940353.png-w331s)

#### 2.静态分析

崩溃函数`fsg_ExecuteGlyph`分析

![](https://images.seebug.org/content/images/2021/03/b9c48144-1335-405a-a5da-aedb7ce6dba8.png-w331s) 在大的堆块中，有两块内存分别用于x数组和y数组，调用memset初始化，之后调用call
cs:off_7FFF41C70D10
，函数内部会调用`DWrite!TrueTypeRasterizer::Implementation::ApplyOutlineVariation`给x数组和y数组赋值,addr1指向的内存没有0x148字节那么大，所以会写到其它的数据对象上，接下里会引用被覆盖的数据作为指针去写数据：
![](https://images.seebug.org/content/images/2021/03/ca5bd41c-e1ff-4348-bcf2-876da1915368.png-w331s)
`rsi+8`中的数据被数组赋值时修改了，使用TTF中的数据覆盖了`[rsi+8]`的数据，`0x00007FFF41B341F6`地址处调用的指令`dd
[r8+56],ax，`其中ax中的数据也是可以控制的。

##### 函数调用链

计算内存大小的函数调用链为

`TrueTypeRasterizer::Implementation::Initialize-> fs_NewSfnt
->fsg_WorkSpaceSetOffsets`函数`fsg_WorkSpaceSetOffsets`内部计算需要申请的内存空间大小并将结果传出到fs_NewSfnt中。

`fs_NewSfnt`获取需要申请的内存大小，之后调用calloc申请内存。

![](https://images.seebug.org/content/images/2021/03/5671c24d-aea1-476f-b8de-c02280d8c1a0.png-w331s)

可以看到图中调用完成`fs_NewSfnt`后，在下面的循环中获取v39内存块中的内容作为申请内存的大小。

`fs_NewSfnt`函数内容如下：

![](https://images.seebug.org/content/images/2021/03/0a426896-1478-40b0-9baa-10337eccac28.png-w331s)

![](https://images.seebug.org/content/images/2021/03/144df51d-5581-4cde-9c46-d101610932b4.png-w331s)
v2为传入的第二个参数a2，`*((_DWORD *)v2 + 3)`与`fs_NewSfnt`中取内存大小区域（ _(_DWORD_ )(v14 +
4i64 * j),j为3时）是一致的。

##### 补丁Diff

![](https://images.seebug.org/content/images/2021/03/a11c02ec-f747-4724-ab2b-c579dc804e56.png-w331s)
`fsg_WorkSpaceSetOffsets`函数补丁前后有修改。

查看补丁前`fsg_WorkSpaceSetOffsets`函数伪C代码如下：

其中参数v3指向”maxp”表具体内容

![](https://images.seebug.org/content/images/2021/03/ba0d3c35-ea59-4441-8757-ae75849378bc.png-w331s)
可以看到图中从`maxCompositePoints`和`maxPoints`字段中取较大值，并且与常量1比较取较大值，得到值为3，之后加8，得到0xb，作为第一个参数传入`fsg_GetOutlineSizeAndOffsets`中，这个函数看名称应该是获取轮廓的大小和偏移值。

补丁后`fsg_WorkSpaceSetOffsets`函数伪C代码有点问题，所以下面贴出汇编代码如下：

![](https://images.seebug.org/content/images/2021/03/83f9a152-b05f-4f8a-a1f1-661de4b3663b.png-w331s)

![](https://images.seebug.org/content/images/2021/03/45584749-a8fb-49bd-9c3a-80c4a2196600.png-w331s)

![](https://images.seebug.org/content/images/2021/03/84d41eeb-948d-4730-8778-47faa667bd50.png-w331s)
打过补丁后，程序是先从`maxCompositePoints`和`maxPoints`字段中取较大值，得到3，再与1比较得较大值仍然为3，3+8得到0xb，再取出maxp表中`maxComponentElements`字段，POC中此值为0x0062，相对”maxp”表具体内容偏移为0x1C

![](https://images.seebug.org/content/images/2021/03/aaa2bfd7-4e49-4f21-a49a-5eca8e727a3a.png-w331s)
`0x62+4=0x66`，比较0x66与0xb得到较大值作为第一个参数传入`fsg_GetOutlineSizeAndOffsets`函数中。

函数`fsg_GetOutlineSizeAndOffsets`没有变化，只是因为传入的第一个参数不同，所以最终计算出的结果也不同。

##### 漏洞函数分析

`fsg_ExecuteGlyph`函数对堆块内部的两个整数数组，对应于x坐标和y坐标进行操作，实际上数组的较小，`fsg_ExecuteGlyph`函数先调用了两次memset将数组清零，如果字体是一个变量且指定了轴值，还会调用`TrueTypeRasterizer::Implementation::ApplyOutlineVariation->GlyphOutlineVariationInterpolator::ApplyVariation`将字体中的数据赋值到坐标数组，这样就会破坏到后续的结构成员。

#### 3\. 动态分析

计算所需内存的过程可以通过条件断点的方式来调试，附加到调试器后，可以设置如下断点命令，

    
    
    bp DWrite!TrueTypeRasterizer::Implementation::Initialize "r $t0=$t0+1; .printf \"Initialize times:%d\n\",@$t0;.echo;gc"

![](https://images.seebug.org/content/images/2021/03/0fd1fc70-c0ef-40fa-95ca-758673315607.png-w331s)

可以看到第13次调用`TrueTypeRasterizer::Implementation::Initialize`函数之后就会进入崩溃。

重新启动，下断点：

    
    
    bp DWrite!TrueTypeRasterizer::Implementation::Initialize "r $t0=$t0+1; .printf \"Initialize times:%d\n\",@$t0;.echo;.if(@$t0 == 0x0D){}.else{gc}"

运行可以看到：

![](https://images.seebug.org/content/images/2021/03/c9cfe153-67ff-4a16-8233-c81c1c6fffb3.png-w331s)
在调用`fs_NewSfnt`之前下断点，查看传入参数内容：

![](https://images.seebug.org/content/images/2021/03/d99b34f5-87a7-45f4-a2d6-70d018ddc75a.png-w331s)
单步步过，再次查看内存，可以看到需要申请的内存大小为0x6fa4。

继续往下运行：

![](https://images.seebug.org/content/images/2021/03/5461ae1c-513a-4cf7-8553-ebe9dc38b915.png-w331s)
可以看到申请的内存地址为0x00000196bc484b60。

在崩溃函数中下断点，运行：

![](https://images.seebug.org/content/images/2021/03/dbe27088-8b09-4486-bc04-877e91b5e9f0.png-w331s)
堆块起始地址为上面的申请的0x00000196bc484b60，调用memset使用的大小为0x148，上面是内存块1，addr1为0x00000196bc4850fc

查看堆块大小以及addr1相对堆块起始地址的偏移大小如下：

![](https://images.seebug.org/content/images/2021/03/0aeb9217-6563-4471-bec6-8144a1536d9a.png-w331s)
最终调用`fsg_ExecuteGlyph+0x772`处的指令`add [r8+56h], ax`时，a8来源于`[rsi+8]`

![](https://images.seebug.org/content/images/2021/03/c153c14a-c272-4114-bd63-b597b9500917.png-w331s)
查看rsi+8相对于堆块的偏移

![](https://images.seebug.org/content/images/2021/03/097b1a5b-61f2-4fe1-894e-ca9ac6fee844.png-w331s)
rsi+8相对于堆块起始地址偏移0x6c8，而addr1相对于堆块起始地址偏移`0x59c，0x59c+0x148=0x6E4>0x6C8，`所以操作addr1中的数据时会覆盖`rsi+8`处的数据，从图上可以看到，调用`memset`后`rsi+8`中的数据初始化为0。

调用`ApplyOutlineVariation`函数之后，`rsi+8`处数据被修改为ttf文件中的数据。（重新启动，内存地址与上面不一样）

![](https://images.seebug.org/content/images/2021/03/cad560cd-12e9-498d-a2d4-6a610d732fef.png-w331s)
继续运行，如下：

![](https://images.seebug.org/content/images/2021/03/b01a2bba-53a7-4830-8fe6-6220fbb67b0c.png-w331s)
可以看到ax为`0x9e9f`，r8为`0x00007a7b00007879`，这两个数据都在poc.ttf文件中的数据，所以这个指针数据可控(where)，要写入的内容(what)也可控。

打过补丁之后查看DWrite!`fsg_ExecuteGlyph`函数没有变化，调试发现整个堆块的大小变得更大了，x数组和y数组的大小还是0x148字节，ESI对象距离堆块起始地址的距离变大，所以在x数组和y数组的赋值过程中没有覆盖到ESI对象,如下：
![](https://images.seebug.org/content/images/2021/03/1f7953b5-267a-4698-9312-520e8a6e5838.png-w331s)
可以看到堆块大小为0x7d24，之前为0x6fa4。

![](https://images.seebug.org/content/images/2021/03/a3de0d60-e6cf-49d2-8441-012bdae0b4a5.png-w331s)
addr1结束地址为`0x0000015fd070427c<0x0000015fd0704868`，所以数组使用0x148的大小不会覆盖到后面的数据。

## 0x04总结

TTF文件的”maxp”表描述字体中所需内存分配情况的汇总数据，DWrite库没有校验数据，在ttf中写入畸形数据时，程序申请内存过小，导致溢出到其它的数据结构，实现了任意地址写任意数据。补丁在计算所需内存时读取ttf中另一个值+4，与之前畸形数据比较得较大值，申请足够的内存。

## 0x05解决方案

微软已经更新了官方补丁，下载链接：

<https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-24093>

## 0x06参考文献

1.<https://bugs.chromium.org/p/project-zero/issues/detail?id=2123>

2.<https://docs.microsoft.com/en-us/typography/opentype/spec/maxp>

3.<https://blog.csdn.net/blueangle17/article/details/23750999>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1526/>

