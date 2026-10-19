# 揭秘Icebox虚拟机自检解决方案实现Windows内存自省的原理

阅读量 **219531**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-01 10:30:07

 **x**

##### 译文声明

本文是翻译文章

原文地址：<https://thalium.github.io/blog/posts/windows-full-memory-introspection-with-icebox/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01c1e2a10aa793b889.png)

## 一、概述

虚拟机自省（Virtual Machine
Introspection，VMI）是一种用于探索虚拟机的强大技术。这种技术可以直接作用于虚拟机管理程序，并且可以隐蔽且精确地控制虚拟机状态，也就是CPU上下文和内存。

基本上，VMI的一个常见用法是首先在地址上设置断点，然后等待中断，最后读取虚拟内存。例如，如果我们想要在Windows上监视用户的文件写入活动，只需要在内核区域的`NtWriteFile`函数上设置一个断点即可。在触发断点后，我们就可以检索相关的进程，并捕获对应的调用堆栈。所有这些操作最终都需要访问虚拟机的虚拟内存。

听起来，访问这个内存似乎很简单。但事实证明，在Windows上的实际情况要更复杂一些。大家可能都已经了解分页机制，简而言之，分页机制包括在磁盘上备份物理内存页面，以使其可用于进一步访问，从而以某种方式增加物理内存空间。在默认情况下，Windows也将这些备份的页面存储到页面文件中（默认情况下为`pagefile.sys`，也称为交换文件）。因此，当遇到断点时，可能无法直接访问进程虚拟内存的全部内容，因为某些页面可能已经被调出。

禁用页面文件是Windows中的一个功能，是一种可以将所有页面保存到物理内存中的简单方式。但是很遗憾，正如我们在本文中即将看到的，这种技术还不足够。实际上，Windows在处理物理内存的过程中还做了一些优化。

本文的第一部分主要介绍Windows虚拟地址转换机制，描述了物理内存页面描述中涉及的所有软件状态。

然后，在第二部分中，我们将重点介绍IceBox如何在其初始化阶段自动配置操作系统，以提供Windows虚拟机的完整物理内存访问。

## 二、Windows虚拟地址转换

###  2.1 硬件部分

软件内存管理依赖于基础硬件的支持。从硬件的角度来看，内存管理单元（MMU）负责虚拟地址转换以访问物理内存。关于更完整的说明，可以参考《英特尔64位和IA-32位架构软件开发人员手册》。在这里，我们仅介绍最为常见的情况——64位4级分页模式。  
这个转换过程从CR3寄存器开始，当然还有一个虚拟地址。

地址的较高16位没有使用，随后的48位分别为4个9位的值，分别对应于页表层次结构的4个级别：

Level 0是4级页映射偏移量（PML4）；

Level 1是页目录指针偏移量（PDP）；

Level 2是页目录偏移量（PDP）；

Level 3是页表偏移量（PT）。

而最后的12位，对应于页面中的偏移量。

下图说明了整个过程：

![](https://p5.ssl.qhimg.com/t0164c9dbb535215c17.png)

1、CR3包含页面映射4级的基地址，也称为目录表基地址（DTB，第12-51位）；

2、PML4E提供了页目录指针表（PDPT）的基地址，可以在PDP偏移量处读取PDPE；

3、PDPE给出了页目录表（PDT）的基地址，可以从PD偏移量处读取PDE；

4、PDE给出了页表（PT）的基地址，可以从PT偏移量处读取PTE。

最后，页表项（PTE）描述了物理内存中页的状态。在Windows中，这个硬件状态由`_MMPTE_HARDWARE`结构定义。

    
    
    nt!_MMPTE_HARDWARE
       +0x000 Valid               : Pos 0, 1 Bit
       +0x000 Dirty1              : Pos 1, 1 Bit
       +0x000 Owner               : Pos 2, 1 Bit
       +0x000 WriteThrough        : Pos 3, 1 Bit
       +0x000 CacheDisable        : Pos 4, 1 Bit
       +0x000 Accessed            : Pos 5, 1 Bit
       +0x000 Dirty               : Pos 6, 1 Bit
       +0x000 LargePage           : Pos 7, 1 Bit
       +0x000 Global              : Pos 8, 1 Bit
       +0x000 CopyOnWrite         : Pos 9, 1 Bit
       +0x000 Unused              : Pos 10, 1 Bit
       +0x000 Write               : Pos 11, 1 Bit
       +0x000 PageFrameNumber     : Pos 12, 36 Bits
       +0x000 ReservedForHardware : Pos 48, 4 Bits
       +0x000 ReservedForSoftware : Pos 52, 4 Bits
       +0x000 WsleAge             : Pos 56, 4 Bits
       +0x000 WsleProtection      : Pos 60, 3 Bits
       +0x000 NoExecute           : Pos 63, 1 Bit
    

从上述原理中，提取出对我们本次研究有用的两点，分别是：

1、向硬件指示所有其他位均有效并且可以安全访问目标物理页面的有效标志；

2、`PageFrameNumber`表示物理内存中的页面索引。

当页面有效时，就可以很容易地计算出物理地址：

    
    
    PhysicalAddress = _MMPTE_HARDWARE.PageFrameNumber * 0x1000 + PageOffset
    

###  2.2 软件部分

在Windows中，工作集（Working
Set，WS）是有关内存管理的一个关键概念。它基本上对应于在不引起页面错误的情况下可以访问的页面集。实际上，存在三种类型的工作集：进程、系统和会话，每一种都有其自己的限制。

在本文中，我们使用以下简化后的工作集表示，来说明Windows虚拟地址转换的行为：

![](https://p4.ssl.qhimg.com/t013135b098e20a4a2d.png)

在这里，我们考虑单个进程的工作集。为简单起见，这个工作集在左侧表示为一组PTE。其中的每一个PTE都引用一个有效页面，如右侧所示。有效PTE设置了有效位，在这种情况下，MMU就发挥了作用，并执行到物理地址的转换。

如果没有设置有效位，则MMU会忽略所有其他PTE标志，访问这样的页面将会产生页面错误。这就为操作系统提供了将这些位用于任何地方的可能性，特别是可以优化其管理内存的方式。因此，Windows通过名为`_MMPTE`的特定联合体为页面定义了几种内部状态：

    
    
    nt!_MMPTE
       +0x000 u  : 
          +0x000 Long         : Uint8B
          +0x000 VolatileLong : Uint8B
          +0x000 Hard         : _MMPTE_HARDWARE
          +0x000 Proto        : _MMPTE_PROTOTYPE
          +0x000 Soft         : _MMPTE_SOFTWARE
          +0x000 TimeStamp    : _MMPTE_TIMESTAMP
          +0x000 Trans        : _MMPTE_TRANSITION
          +0x000 Subsect      : _MMPTE_SUBSECTION
          +0x000 List         : _MMPTE_LIST
    

除了已经介绍的`_MMPTE_HARDWARE`之外，所有其他结构均表示PTE的软件状态，操作系统使用该状态来实现一些优化。在以下各小节中，我们通过查看`_MMPTE_SOFTWARE`来判断出需要分析并考虑的结构：

    
    
    nt!_MMPTE_SOFTWARE
       +0x000 Valid                : Pos 0, 1 Bit     //_MMPTE_HARDWARE
       +0x000 PageFileReserved     : Pos 1, 1 Bit
       +0x000 PageFileAllocated    : Pos 2, 1 Bit
       +0x000 ColdPage             : Pos 3, 1 Bit
       +0x000 SwizzleBit           : Pos 4, 1 Bit
       +0x000 Protection           : Pos 5, 5 Bits
       +0x000 Prototype            : Pos 10, 1 Bit    //_MMPTE_PROTOTYPE/_MMPTE_SUBSECTION
       +0x000 Transition           : Pos 11, 1 Bit    //_MMPTE_TRANSITION
       +0x000 PageFileLow          : Pos 12, 4 Bits
       +0x000 UsedPageTableEntries : Pos 16, 10 Bits
       +0x000 ShadowStack          : Pos 26, 1 Bit
       +0x000 Unused               : Pos 27, 5 Bits
       +0x000 PageFileHigh         : Pos 32, 32 Bits  //_MMPTE_SOFTWARE
    

在Rekall取证项目中，已经充分记录了下面的内容。但是，需要注意的是，在Windows虚拟地址转换中还涉及到一些可能的软件PTE状态以及转换，以缓解最近发现的CPU推测执行漏洞（CVE-2018-3615
L1终端故障，又称为Foreshadow）。

###  2.3 Transition PTE（过渡PTE）

在Windows中，平衡集管理器（Balance Set
Manager，KeBalanceSetManager）负责管理工作集。当可用物理内存低于某个阈值时，这个组件可以决定从工作集删除一些很少使用的页面。有关平衡集管理器的更多信息，可以参考Windows
Internals第七版的第五章：内存管理。在此过程中，会将PTE的当前状态从有效（`_MMPTE.u.hard.Valid=1`）更改为过渡（`_MMPTE.u.Hard.Valid=0`且`_MMPTE.u.Soft.Transition=1`）。下图说明了这一步骤：

![](https://p4.ssl.qhimg.com/t01e1b00933b0e8504e.png)

其中，先前有效的页面已经从工作集中删除（以灰色表示），并且相应的PTE被标记为处于过渡状态。

尽管无法直接访问该页面，但其内容仍然存在，并且在物理内存中有效。在访问后，将会触发页面错误，这将导致PTE的状态由过渡状态再恢复为有效状态。这个过渡状态对应于`_MMPTE_TRANSITION`结构：

    
    
    nt!_MMPTE_TRANSITION
       +0x000 Valid            : Pos 0, 1 Bit     // 0
       +0x000 Write            : Pos 1, 1 Bit
       +0x000 Spare            : Pos 2, 1 Bit
       +0x000 IoTracker        : Pos 3, 1 Bit
       +0x000 SwizzleBit       : Pos 4, 1 Bit
       +0x000 Protection       : Pos 5, 5 Bits
       +0x000 Prototype        : Pos 10, 1 Bit
       +0x000 Transition       : Pos 11, 1 Bit    // 1
       +0x000 PageFrameNumber  : Pos 12, 36 Bits
       +0x000 Unused           : Pos 48, 16 Bits
    

在过渡状态下，PTE的目标物理地址的计算方法如下：

    
    
    PhysicalAddress = _MMPTE.u.Trans.PageFrameNumber * 0x1000 + PageOffset
    

###  2.4 分页文件PTE

随后，处在过渡状态的页面将被调出到磁盘上的页面文件中。这个步骤会将页面从物理内存中释放出来，并将其备份到磁盘，如下图所示：

![](https://p2.ssl.qhimg.com/t0120fe4d4e4539c57d.png)

对应的结构是之前已经查看过的`_MMPTE_SOFTWARE`，其中`Valid`、`Prototype`和`Transition`标志设置为0，但`PageFileHigh`并不是0。

    
    
    nt!_MMPTE_SOFTWARE
       +0x000 Valid                : Pos 0, 1 Bit     // 0
       +0x000 PageFileReserved     : Pos 1, 1 Bit
       +0x000 PageFileAllocated    : Pos 2, 1 Bit
       +0x000 ColdPage             : Pos 3, 1 Bit
       +0x000 SwizzleBit           : Pos 4, 1 Bit
       +0x000 Protection           : Pos 5, 5 Bits
       +0x000 Prototype            : Pos 10, 1 Bit    // 0
       +0x000 Transition           : Pos 11, 1 Bit    // 0
       +0x000 PageFileLow          : Pos 12, 4 Bits
       +0x000 UsedPageTableEntries : Pos 16, 10 Bits
       +0x000 ShadowStack          : Pos 26, 1 Bit
       +0x000 Unused               : Pos 27, 5 Bits
       +0x000 PageFileHigh         : Pos 32, 32 Bits  // !=0
    

在这种情况下，检索页面内容的唯一方法是从相应的页面文件中将其读取回来。默认情况下，操作系统按驱动器定义一个页面文件。每个分页文件由索引进行标识。在备份页面时，目标页面文件索引对应于`PageFileLow`字段，文件中的页面偏移量（`PageFileOffset`）解析如下：

    
    
    PageFileOffset = _MMPTE.u.Soft.PageFileHigh * 0x1000 + PageOffset
    

###  2.5 Demand-zero PTE

操作系统没有保存零填充的页面，而是仅仅将这个信息保留在相应的PTE结构中。当必须要还原此类页面时，平衡集管理器将从零页表中获取一个并更新相应的PTE。零页表将由零页面线程（`MiZeroPageThread`）维护，以满足需要使用零的页面错误。

全零页面中包含一个非空的PTE值（`_MMPTE.u.Long`），但在`_MMPTE_SOFTWARE`结构中，以下标志被设置为零，分别是：`Valid`、`Prototype`、`Transition`和`PageFileHigh`。

    
    
    nt!_MMPTE_SOFTWARE
       +0x000 Valid                : Pos 0, 1 Bit     // 0
       +0x000 PageFileReserved     : Pos 1, 1 Bit
       +0x000 PageFileAllocated    : Pos 2, 1 Bit
       +0x000 ColdPage             : Pos 3, 1 Bit
       +0x000 SwizzleBit           : Pos 4, 1 Bit
       +0x000 Protection           : Pos 5, 5 Bits
       +0x000 Prototype            : Pos 10, 1 Bit    // 0
       +0x000 Transition           : Pos 11, 1 Bit    // 0
       +0x000 PageFileLow          : Pos 12, 4 Bits
       +0x000 UsedPageTableEntries : Pos 16, 10 Bits
       +0x000 ShadowStack          : Pos 26, 1 Bit
       +0x000 Unused               : Pos 27, 5 Bits
       +0x000 PageFileHigh         : Pos 32, 32 Bits  // 0
    

###  2.6 Prototype PTE

原型PTE（Prototype PTE）用于描述由内存段（Section
Objects）表示的内存。可以通过`CreateFileMapping`函数来创建段对象，然后使用`OpenFileMapping`打开该段对象，并使用`MapViewOfFile`进行映射。基本上，段对象应该对应于共享内存，如下图所示：

![](https://p2.ssl.qhimg.com/t01dda91a10f9786620.png)

我们有两个进程，每个进程拥有一个相同的段对象（sectionX），它们指向相同的物理页面。在这里，所有PTE都是有效的。

在这里有一个与操作系统相关的难点，就是同步共享页面的裁剪。实际上，由于多个PTE可以引用同一个物理页面，因此如果操作系统决定从物理内存中删除共享页面，则它必须查找引用该页面的所有PTE，并更新其当前状态。由于这种方法看起来效率很低，因此Windows使用了原型PTE来解决这一问题。

有关原型PTE及其与段对象关系的完整说明，各位读者可以参考：<https://artemonsecurity.blogspot.com/2018/10/what-is-proto-pte-and-how-windows-vmm.html>

简而言之，当平衡集管理器裁剪共享页面时，会在相应的PTE中设置`_MMPTE.u.Soft.Prototype`标志。在这种情况下，涉及到的结构是`_MMPTE_PROTOTYPE`，其定义如下：

    
    
    nt!_MMPTE_PROTOTYPE
       +0x000 Valid                : Pos 0, 1 Bit   // 0
       +0x000 DemandFillProto      : Pos 1, 1 Bit
       +0x000 HiberVerifyConverted : Pos 2, 1 Bit
       +0x000 ReadOnly             : Pos 3, 1 Bit
       +0x000 SwizzleBit           : Pos 4, 1 Bit
       +0x000 Protection           : Pos 5, 5 Bits
       +0x000 Prototype            : Pos 10, 1 Bit  // 1
       +0x000 Combined             : Pos 11, 1 Bit
       +0x000 Unused1              : Pos 12, 4 Bits
       +0x000 ProtoAddress         : Pos 16, 48 Bits
    

在这个结构中，`ProtoAddress`指向另一个名为prototype PTE的PTE。而这个在内核`PagedPool`中分配的prototype
PTE实际上描述了当前页面的状态。从那时开始，在删除页面时，操作系统只需要更新相应的prototype PTE即可。

现在，原型PTE本身可以表示所有此前描述过的状态，包括`valid`、`transition`、`paged`、`demand
zero`。理论上，也可以是其他状态，但这里并不涉及虚拟地址转换。

例如，下图说明了处于过渡状态的原型PTE，这表明其`PageFrameNumber`仍然以具有有效内容的物理页面为目标：

![](https://p0.ssl.qhimg.com/t014ea64ef596751d15.png)

###  2.7 Subsection PTE

考虑到映像文件映射，系统依靠原型PTE实现了特殊的优化。在这些文件中，包括几个不可写的常量页面。这样一来，系统就无须备份页面文件中已驻留在原始文件中的此类页面。

为了处理这种情况，系统会在目标原型PTE中设置`PTE.u.Soft.Prototype`标志。然后，这个PTE的对应结构是`_MMPTE_SUBSECTION`，其定义如下：

    
    
    nt!_MMPTE_SUBSECTION
       +0x000 Valid             : Pos 0, 1 Bit    // 0
       +0x000 Unused0           : Pos 1, 3 Bits
       +0x000 SwizzleBit        : Pos 4, 1 Bit
       +0x000 Protection        : Pos 5, 5 Bits
       +0x000 Prototype         : Pos 10, 1 Bit   // 1
       +0x000 ColdPage          : Pos 11, 1 Bit
       +0x000 Unused1           : Pos 12, 3 Bits
       +0x000 ExecutePrivilege  : Pos 15, 1 Bit
       +0x000 SubsectionAddress : Pos 16, 48 Bits
    

下图说明了从两个工作集中删除`ntdll.dll`页面的情况：

![](https://p0.ssl.qhimg.com/t0182e3d2596b28ad84.png)

这里无需过于详细地说明，`_MMPTE.u.Subsect.SubsectionAddress`指向的是`_CONTROL_AREA`结构，该结构本身指向`_FILE_OBJECT`。

但遗憾的是，如果不读取文件系统上的原始映像文件，则无法访问Subsection PTE的内容。

###  2.8 基于VAD的PTE

最后的优化是由Windows实现的。当PTE值为空（`_MMPTE.u.Long=0`）时，必须检查虚拟地址描述符（VAD）进程，以找到相应的原型PTE（在Windows内部和rekall项目中的VAD
Hardware
PTE中，将该状态命名为unknown）。当设置`_MMPTE.u.Soft.Prototype`标志并且`PTE.u.Proto.ProtoAddress`等于`0xFFFFFFFF0000`时（在Windows中，该状态称为虚拟地址描述符；在rekall项目中，该状态称为VAD
Prototype PTE），情况相同。

    
    
    nt!_MMPTE_PROTOTYPE
       +0x000 Valid                : Pos 0, 1 Bit     // 0
       +0x000 DemandFillProto      : Pos 1, 1 Bit
       +0x000 HiberVerifyConverted : Pos 2, 1 Bit
       +0x000 ReadOnly             : Pos 3, 1 Bit
       +0x000 SwizzleBit           : Pos 4, 1 Bit
       +0x000 Protection           : Pos 5, 5 Bits
       +0x000 Prototype            : Pos 10, 1 Bit    // 1
       +0x000 Combined             : Pos 11, 1 Bit
       +0x000 Unused1              : Pos 12, 4 Bits
       +0x000 ProtoAddress         : Pos 16, 48 Bits  // 0xFFFFFFFF0000
    

下图说明了在这种情况下，如何访问所需的原型PTE。

![](https://p2.ssl.qhimg.com/t01ea6a563752deb297.png)

首先，这种基于VAD的情况仅在用户进程的上下文中发生。从相应的`_EPROCESS`结构（蓝色）开始，我们必须找到相应的存储区。这个区域被称为“虚拟地址描述符”（VAD），由`_MMVAD`内核结构定义。每个进程都拥有一组VAD，这些VAD从`VadRoot`字段开始组成一个自平衡的AVL树。简而言之，每个VAD都有一个起始地址（`StartingVpn`代表虚拟起始页编号）和一个终止地址（`EndingVpn`）字段。有以下三种可能的情况：

1、所需地址在`StartingVpn`以下，将考虑左子树（红色）；

2、所需地址在`EndingVpn`以上，将考虑右子树（蓝色）；

3、否则，所需的地址位于`StartingVpn`和`EndingVpn`定义的范围内，即找到所需的VAD（深灰色）。

现在，每个VAD都将一组原型PTE作为`FirstPrototype`字段公开。由于原型PTE都是4KB的页面，因此可以轻松计算出目标原型PTE（深绿色）。最后，就可以对获得的原型PTE进行处理。

###  2.9 缓解L1终端故障（Foreshadow）

自2018年8月开始，对上述虚拟地址转换方法进行了改进。目前，如果只在虚拟地址上使用`!pte kd`命令可能会输出以下结果：

    
    
    kd> !pte 7ff743655000
    ... PTE at FFFFE93FFBA1B2A8
    ... contains 000020000891F860
    ... not valid
    ...   Transition: 891F
    ...   Protect: 3 - ExecuteRead
    

如我们所见，相应的PTE是无效的（000020000891F860）。我们可以很容易地验证内容是否代表`PageFrameNumber`为`0x20000891F`的过渡PTE。但是在`kd`中，却显示了一个不同的过渡PFN值`0x891F`。导致这种差异的原因是什么呢？

微软安全响应中心（MSRC）给出了完整的答案：在这里，引入了一种新的缓解措施，用于缓解一个名为L1终端故障（L1TF）的推测执行侧信道漏洞。

简而言之，英特尔手册中所述的MMU行为与推测的行为不同。当未设置`_MMPTE_HARDWARE.Valid`标志时，CPU会推测性地尝试访问L1高速缓存中以`PageFrameNumber`为目标的页面。如果存在指令，则会预取指令，这可能会导致敏感信息（例如内核地址）泄露。

为了缓解这个CPU漏洞，Windows现在确保每个无效的PTE都有一个`PageFrameNumber`，超出可用物理内存的限制。这是通过`MiSwizzleInvalidPte`函数来实现的。

    
    
    _MMPTE __fastcall MiSwizzleInvalidPte(_MMPTE pte)
    {
      if ( gKiSwizzleBit )
      {
        if ( !(gKiSwizzleBit & pte.u.Long) )
          return (_MMPTE)(pte.u.Long | gKiSwizzleBit);
        pte.u.Long |= MMPTE_SWIZZLE_BIT;
      }
      return pte;
    }
    

`gKiSwizzleBit`全局值是在系统初始化期间，在`MiInitializeSystemDefaults`函数中定义的：

    
    
    KiSwizzleBit = 1i64 << (KiImplementedPhysicalBits - 1);
    

请注意，这里的`gKiSwizzleBit`并不是正式名称，而只是我们在这篇文章中的建议名称。

使用`cpuid`指令初始化`KiImplementedPhysicalBits`值以获取最大的物理内存，可以参考`KiDetectKvaLeakage`函数。

###  2.10 小结

下图总结了整个PTE解析算法：

![](https://p2.ssl.qhimg.com/t0178c0725381e756d2.png)

现在，我们就能够处理Windows虚拟地址转换中涉及的所有软件PTE状态：

1、绿色，表示我们可以访问目标页面的内容；

2、红色，表示以下两种情况，仍然需要访问文件系统：

（1）分页文件PTE；

（2）Subsection PTE。

## 三、IceBox和Windows内存访问

IceBox并没有寻找一种解析虚拟磁盘中的页面文件和可执行文件的方法，而是专注于一种更实用的方法。在理想情况下，我们希望启动虚拟机并访问其物理内存，而无需任何特殊配置或用户操作。

###  3.1 禁用页面文件

禁用页面文件是`sysdm.cpl`的一项众所周知的功能，如下图所示：

![](https://p3.ssl.qhimg.com/t01787d79b871a2998a.png)

修改注册表中位于`HKEY_LOCAL_MACHINESYSTEMCurrentControlSetControlSession ManagerMemory
Management`的键下，名为`PagingFiles`的多字符串值，如下图所示：

![](https://p5.ssl.qhimg.com/t011de3b9bc938b1e2f.png)

页面文件由名为`smss.exe`的第一个用户进程创建，该进程在内核初始化（`Phase1InitializationIoReady`）期间启动。一切工作都开始于`SmpLoadDataFromRegistry`函数，该函数从注册表中创建`SmpPagingFileList`。每个条目都包含页面文件的路径（在我们的测试示例中为`c:pagefile.sys`和`e:pagefile.sys`）。随后，`SmpCreatePagingFiles`函数遍历`SmpPagingFileList`，以最终在每个页面文件上调用`NtCreatePagingFile`系统调用。

如果要禁用IceBox中的页面文件，需要禁用`NtCreatePagingFile`。出于隐蔽性的考虑，这里不执行任何挂钩，而是在`NtCreatePagingFile`上设置一个临时的断点。当由`smss.exe`触发断点时，通过修改RIP寄存器将控制流重定向到RET指令。在初始化之后，`smss.exe`将启动第一个`csrss.exe`进程。该进程的启动让我们可以删除`NtCreatePagingFile`上的上一个断点。

###  3.2 禁用Subsection PTE

为了解决这个问题，我们还需要更深入地了解系统如何创建和映射`_SECTION`对象。它是以`NtCreateSection`和子函数开始：

    
    
    NtCreateSection
     NtCreateSectionCommon
      MiCreateSection
       MiCreateImageOrDataSection
        MiCreateNewSection
         MiCreateImageFileMap
    

在最后一个函数中，有一个值得关注的部分，其伪代码如下：

    
    
    status = MiBuildImageControlArea(...,&FileSize,&pNewControlArea);
    if (!NT_SUCCESS(Status)) goto CleanUp;
    //...
    if (IoIsDeviceEjectable(arg0_pFileObject->DeviceObject))
    {
        bIsEjectable = 1;
    }
    //...
    if (bIsEjectable)
    {
        pNewControlArea->u.ImageControlAreaOnRemovableMedia = 1;
    }
    

基本上，如果目标设备对象被认为是可弹出的，就会在新创建的控制区域中设置`ImageControlAreaOnRemovableMedia`标志。然后，在`MiCreateNewSection`中检查该标志。设置后，将调用`MiSetPagesModified`函数，该函数更新每个PTE的状态，这些状态描述了从原型到过渡的部分。由于禁用了页面文件，这些PTE将始终处于过渡状态，该状态由IceBox处理。

为了实现这一点，`IoIsDeviceEjectable`函数需要返回`true`：

    
    
    bool __fastcall IoIsDeviceEjectable(PDEVICE_OBJECT pDeviceObject)
    {
      return (((pDeviceObject->Characteristics & FILE_FLOPPY_DISKETTE) == 0) & !_bittest(&InitWinPEModeType, 31u)) == 0;
    }
    

因此，我们就有了两种选择：

1、强制在卷设备的属性中添加`FILE_FLOPPY_DISKETTE`标志；

2、修改`InitWinPEModeType`值。

第一个选择需要检测设备的创建时间，并更新其属性。第二个选择似乎更加容易。实际上，`InitWinPEModeType`是在`Phase1InitializationDiscard`函数中初始化的：

    
    
    if ( Options && strstr(Options, "MININT") )
      {
        InitIsWinPEMode = 1;
        if ( strstr(Options, "INRAM") )
          InitWinPEModeType |= 0x80000000;
        else
          InitWinPEModeType |= 1u;
      }
    

这个选项对应于Windows
PE功能，WinPE适用于部署、安装和修复Windows桌面和服务器安装的小型操作系统。由于该系统是从ISO文件启动的，因此Subsection
PTE限制不影响这个选项。还有非常好的一点，这个选项（至少）自Windows XP以来就一直存在。

IceBox当前通过在操作系统启动期间强制将这个`InitWinPEModeType`全局设置为`0x80000000`来启动WinPE模式。

###  3.3 内存压缩

内存压缩是Windows 10中引入的功能，并且已经向后移植到Win 8和Win
7。这个机制可以压缩客户端Windows版本上的私有页面，以增加可用内存大小。内存压缩涉及到内核和用户两个部分：

1、对于内核，核心功能是在名为“存储管理器”（SM，所有公共和私有内核函数均以`Sm`和`Smp`为前缀）的专用组件中实现的；

2、对于用户空间，`Superfetch`服务（托管在`svchost.exe`实例中的`sysmail.dll`）由`NtSetSystemInformation`调用存储管理器来管理存储。

有关内存压缩的更完整说明，请参考Windows Internals第七版的第五章：内存管理。由于压缩只是一种内存优化方式，因此我们想要禁用该功能。

内核使用`SmFirstTimeInit`函数中的`PsCreateMinimalProcess`创建`MemoryCompression`进程。在创建该进程之前，`MmStoreCheckPagefiles`函数确保至少存在一个页面文件，否则会返回状态`STATUS_NOT_SUPPORTED`。

通过禁用页面文件的方式，将隐蔽地禁用内存压缩功能。

## 四、局限性

上述对于页面文件和WinPE模式的修改会影响系统。首先，禁用页面文件存在以下几个限制：

1、页面文件是第二种内存存储方式，实际上可以增加物理内存的大小。因此，禁用页面文件也就直接限制了可用物理内存的总量。通过增加虚拟机的物理内存，可以规避此类影响。

2、如果系统发生崩溃，会使用页面文件来临时存储生成的崩溃转储。禁用页面文件将不会创建故障转储。

3、如前所述，内存压缩需要页面文件的支持。因此，禁用页面文件将影响内存压缩的功能。

其次，从隐蔽性的角度来看，WinPE模式很容易被检测到。目前，在我们的IceBox方案中，没有考虑到这一点。

## 五、总结

这篇文章从VMI的角度分析了虚拟机的内存访问原理。更准确地说，我们描述了一些Windows虚拟地址转换的内部原理和针对漏洞实施的缓解措施，这里涉及到的漏洞是推测执行侧信道漏洞（L1中断故障）。在对内存内部结构有了深入了解之后，我们就可以访问任意存在于内存中的物理页面。同样，我们还可以解决页面没有映射到物理内存中，而是仅存在于文件系统中的情况。

随后，我们描述了VMI如何在其初始化阶段自动允许Windows虚拟机配置，以强制将任何页面以持久性方式映射到内存中。所有这些都在IceBox中实现，可以实现以下自动功能：

1、禁用页面文件，以避免分页机制；

2、启用WinPE模式，避免Subsection PTE直接引用磁盘上的页面。

综合评估对系统的影响以及内存自省带来的优势，我们认为进行以上调整的好处要大于其缺点。

本文翻译自 [原文链接](https://thalium.github.io/blog/posts/windows-full-memory-introspection-with-icebox/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/209467](/post/id/209467)

安全客 - 有思想的安全新媒体

本文转载自: [](https://thalium.github.io/blog/posts/windows-full-memory-introspection-with-icebox/)

如若转载,请注明出处： <https://thalium.github.io/blog/posts/windows-full-memory-introspection-with-icebox/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [虚拟机](/tag/虚拟机)
  * [VMI](/tag/VMI)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

