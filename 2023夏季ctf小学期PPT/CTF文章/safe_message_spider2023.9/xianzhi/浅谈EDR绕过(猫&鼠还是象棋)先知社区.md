这篇文章介绍了作者去年提出的一种新方法，用于阻止EDR
DLLs加载到新生成的进程中。经过几个月的努力，作者成功地实现了这个想法，并在今年的x33fcon和Troopers会议上展示了这个主题，并发布了PoC。本文将介绍该技术的背景和描述。

Endpoint Detection and Response
(EDR)系统如何检测恶意活动或软件。EDR系统可以从用户空间（用户进程运行的位置）或内核空间（操作系统层级）进行检测。用户空间的典型分析/检测包括静态和动态分析、用户空间钩子和堆栈跟踪分析。静态分析可以用于文件签名（例如任何杀毒软件使用的方式）或检查元数据（如证书及其有效性）。动态分析可以包括对可执行文件的主动调试，或将其放入类似沙箱的环境中以查看其在运行时的行为。堆栈跟踪分析可以显示进程是否从未备份的内存区域执行特定的Windows
API（私有提交内存部分中的动态代码，非常可疑）。来自内核空间的检测通常利用Kerne Callback和ETW Threat
Intelligence（ETWti）。

EDR（终端威胁检测和响应）使用签名驱动程序在内核空间中操作，并拦截特定的Kernel
Callback来拦截进程和线程的执行，以执行自己的代码来检查是否存在恶意代码。使用  
PsSetCreateProcessNotifyRoutine()来拦截新进程的创建并检查其要执行的内容，同时也  
可以使用PsSetCreateThreadNotifyRoutine()来拦截新线程的创建并检查其入口点是否存在  
恶意代码。该技术需要在内核中运行，因此任何错误都可能导致系统崩溃。

![](./img/2701216981237644770.png)

ETWti是由Microsoft提供的一个接口，驱动程序可以订阅以接收特殊的ETW事件。这些事件专门用于检测恶意活动，包括进程创建、内存分配、线程创建等。

![](./img/1524163979687333021.png)

对于这篇博文来说，我们主要讨论用户空间钩子检测技术。至少根据我以前的经验，几乎所有的EDR都用到了相关的检测技术。

用户空间hook了什么呢？  
在进行用户空间进程的实时分析时，EDR供应商和大多数AV供应商会加载自己的动态链接库（DLL）到操作系统上运行的进程中。加载DLL后，它会对选择的Windows
API的内存区域进行修补，以放置一个钩子，这基本上是一个JMP指令，转到它们自己的DLL内存区域。这些钩子检测技术是EDR中最常用的检测技术之一。

![](./img/1328375332387927726.png)

在这种攻击中，恶意软件可以拦截进程的运行时Windows
API调用，并检查其输入参数以了解它在运行时要做什么。这样，恶意软件可以执行shellcode以执行任意代码。

![](./img/510213217530751196.png)

下面来讲解一种恶意软件的攻击技术。首先，恶意软件使用OpenProcess获取远程进程的句柄，然后使用VirtualAllocEx在远程进程中分配内存。接着，使用WriteProcessMemory将Shellcode写入到新分配的内存区域中。最后，使用CreateRemoteThread在远程进程中创建一个新线程来执行Shellcode。为了避免基于签名的检测，可能会在运行时对Shellcode进行加密和解密，然后再使用WriteProcessMemory写入到远程进程中。CreateRemoteThread会调用ntdll.dll中的NtCreateThreadEx函数，这是从用户空间调用的最后一个函数。由于ntdll.dll函数是从用户空间调用的最后一个函数，因此许多供应商倾向于钩住这个特定DLL中的函数。

某个NtCreateThreadEx的定义看起来如下：

![](./img/2037025652630104425.png)

当恶意软件想要在新线程中启动Shellcode时，EDR可以检查NtCreateThreadEx的输入参数，特别是startAddress输入指针。当恶意软件想要在新线程中启动Shellcode时，startAddress通常指向已解密的纯文本Shellcode，例如C2植入程序。现在，EDR可以在startAddress内存区域上应用Yara规则（内存扫描）以查找任何已知的恶意C2植入程序，如CobaltStrike、Sliver、Covenant等。如果规则匹配，则可以确认存在恶意软件并杀死进程。

现有的用户空间钩子逃避技术  
包括Unhooking、使用直接Syscalls、使用硬件断点和修补DLL入口点。这些技术可以绕过用户空间钩子检测，因此需要使用其他技术来检测和防止恶意软件的运行。

Unhooking  
在这种方法中，从任何位置(Disk, KnownDlls) 获取ntdll.dll的新副本，并用跳转到EDR
DLL的EDR修补的内存区域替换。这将有效地绕过钩子，因为不再发生跳转，也不再进行输入参数分析。

![](./img/2981726495299321825.png)

直接syscall（系统调用）  
这种方法可以通过在当前进程内存中检索或重新构建ntdll.dll函数并直接执行它们来实现。这种方法可以绕过ntdll.dll内存位置中的钩子。文本提到了几个检索技术的Proof
of Concept，包括从内存中重建ntdll.dll函数 (HellsGate,
RecycledGate,*-Gate)、从磁盘获取新的ntdll.dll副本并将函数内容放入内存(GetSyscallStub, e.G. C
DInvoke)以及在恶意软件可执行文件中嵌入部分或全部Syscall Stubs(Syswhispers 1,2,3)。

此外，文本还提到了使用硬件断点来规避用户空间钩子的方法，其中TamperingSyscalls是第一个使用硬件断点的PoC。

![](./img/4709113376798029421.png)

通过在ntdll.dll函数中设置硬件断点来拦截执行，隐藏特定函数的输入参数并备份原始值，然后恢复输入参数并继续执行以避免EDR检测。

在这第一个原始poc执行过程中，利用者通过单步执行程序，找到了Syscall指令被调用的位置。在调用Syscall之前，利用者需要将原始输入参数恢复到堆栈中，以确保函数能够按预期工作。

通过在DLL入口点处进行修补  
2020年里的博文中提出该技术以及工具SharpBlock ：  
1.利用DEBUG_ONLY_THIS_PROCESS标志创建一个新进程，并将父进程作为调试器来拦截特定事件的执行，并在恢复执行之前执行代码。  
2.作为调试器，父进程等待LOAD_DLL_DEBUG_EVENT事件，这些事件在DLL被加载到进程中但在执行DLL中的内容之前出现。  
3.父进程检查正在加载的DLL。如果是EDR DLL，则会使用0x3c -return来修补其Entrypoint，以便该DLL在之后不会再放置钩子，而是直接返回并退出。

![](./img/4872692254874530491.png)

有效地实现，不会再有dll和钩子放置在新进程中了。  
某种新型实现的想法  
在阅读完如下博文后我有了新型实现的想法：  
<https://waawaa.github.io/es/amsi_bypass-hooking-NtCreateSection/>  
该技术可以通过在涉及将DLL加载到进程并将其映射到内存的过程中自己放置钩子到API函数来防止DLL被加载到进程中。它可以用于例如在调用assembly::load()之前防止amsi.dll加载到当前进程，从而导致AMSIs绕过。

钩取了函数NtCreateSection，当目标DLL的内存段要创建时，可以拦截这个过程并返回NTSTATUS失败。如果NtCreateSection失败，内存映射也无法完成，最终导致DLL根本无法加载。但是这种方法只能应用于当前进程中尚未加载的DLL。

EDR DLLs 的问题  
EDRs可以像国际象棋游戏中的白方一样行动。它们可以在接收到新进程的Kernel
Callback后，直接将自己的DLL加载到进程内存中。在良好的实现中（有些供应商不这样做），DLL将在ntdll.dll之后立即加载。它将被加载到基本上任何用户空间进程中（除非您可能会发现一些例外）。

由于这些DLL已经在我们自己的进程中加载了，因此我们不能挂钩NtCreateSection来防止它们的加载。

可以解答吗？  
但是如果我们创建一个新的挂起进程，只加载ntdll.dll：

    
    
    tProcPath = newWideCString(r"C:\windows\system32\windowspowershell\v1.0\powershell.exe")
    
    status = CreateProcess(
        NULL,
        cast[LPWSTR](tProcPath),
        ps,
        ts, 
        FALSE,
        CREATE_SUSPENDED or CREATE_NEW_CONSOLE or EXTENDED_STARTUPINFO_PRESENT,
        NULL,
        r"C:\Windows\system32\",
        addr si.StartupInfo,
        addr pi)

![](./img/5099953763652706947.png)  
我的想法是在已经加载了ntdll.dll的进程中，通过将自定义的Shellcode写入进程中，来设置一个钩子（hook）以阻止特定DLL的加载。步骤如下：

  1. 创建一个挂起的进程。
  2. 为自定义Shellcode分配内存并将其写入该区域。
  3. 远程在NtCreateSection上放置一个钩子，跳转到我们的Shellcode。
  4. 恢复进程。
  5. 我们控制DLL加载

![](./img/1530086505456868668.png)

听起来简单？当然，至少在实际实施时对我而言并不简单。

**在实现中的挑战**  
**PIC代码**  
我们不得不编写自定义Shellcode。在编写Shellcode时，需要使用PIC-Code以确保代码可以在不同环境中正常工作。  
·所有东西都应该存在于编译后的可执行文件的 .text 段中。这是一个动态（位置无关）的部分，我们可以提取它来获得 PIC-Code。  
·我们不能再使用任何全局变量（它们不会被放置在 .text 段中）- 因此，我们必须找到交换不同函数之间信息的替代方法。  
· 所有被调用的 Windows API 都需要动态解析。  
·mainCRTStartup 程序需要被替换为我们的入口点以进行正确的执行。  
·特定了这个PoC（Proof of
Concept，概念验证）的局限性：只能使用ntdll.dll函数，因为当钩子被触发时，进程甚至还没有完全初始化。此时不能加载其他DLL，否则会导致进程崩溃。我也提到了另一种可能的解决方案是等待进程初始化完成后再应用逻辑，但我自己没有实现。

·编写PIC-Code时可能无法使用的一些常用函数，如charcmp，StrStrIA，strlen，memcpy等。作者提到他手动编写了这些函数的逻辑，或者使用了GitHub
Copilot来自动生成代码。

·在调试PIC代码时遇到的困难，因为只能使用ntdll.dll函数。作者最终编写了一个自定义的日志记录函数，以便在需要排除故障时提供一些信息。  
原始的NtcreateSection值  
通过hooking
NtCreateSection函数来创建进程中的Section。当新进程被恢复时，原始值不再存在于其进程内存中。但是为了能够创建其他DLL或对象句柄的Section，需要在某个时候恢复原始值。最后注意这是一个Syscall
Stub，可以使用现有的直接Syscall检索和执行技术，如TartarusGate或GetSyscallStub，但仅使用ntdll.dll函数。  
讨论了一个初始的 PoC（Proof of Concept）方案，使用了一个在主机进程中的 egghunter，其中在 Shellcode 中放置了一个
egg。在放置钩子之前，原始的主机进程可以检索原始的 NtCreateSection 值，并将 egg 替换为该原始值，以便 Shellcode
本身可以在运行时恢复原始值。其中使用的技术术语包括：PoC（概念证明）、egghunter（寻找
egg）、Shellcode（外壳代码）、NtCreateSection（创建新进程的函数）。

    
    
    void originalBytes() { // used to store the original bytes of the function we are hooking. This function can be used in PIC to exchange information between functions, as global variables cannot be used. Thanks @Mr-Un1k0d3r for the hint.
        asm(".byte 0xDE, 0xAD, 0xBE, 0xEF, 0x13, 0x37, 0xDE, 0xAD, 0xBE, 0xEF, 0x13, 0x37, 0xDE, 0xAD, 0xBE, 0xEF, 0x13, 0x37, 0xDE, 0xAD, 0xBE, 0xEF, 0x13, 0x37 ");
    }

![](./img/3902585996349395455.png)

堆栈对齐？  
在Github上已有的PIC-Code实现，比如Handlekatz和博客文章。这些实现中都包含一个小的嵌入式ASM-Stub，用于实现特定的功能。

    
    
    extern entryFunction
    global alignstack
    
    segment .text
    
    alignstack:
        push rdi                    ; 备份 rdi 因为我们将使用其作为主要的寄存器
        mov rdi, rsp                ; 保存栈指针到rdi
        and rsp, byte -0x10         ; 将栈指针调整到16字节的边界上
        sub rsp, byte +0x20         ; 为我们的c函数分配一些空间
        call entryFunction          ; 调用c函数
        mov rsp, rdi                ; 重置栈指针
        pop rdi                     ; 重置rdi寄存器
        ret                         ; 跳转到我们离开的地方

编写Shellcode时需要注意将栈指针调整到16字节的边界上，然而，在实现中不能使用这种技术，因为它会修改栈，导致NtCreateSection函数的输入参数被破坏。因此，在编写Shellcode时需要直接跳转到入口点函数，而不是修改栈。

![](./img/5954282489481688997.png)

在调用NtCreateSection函数时不需要对栈进行对齐的情况。在这种情况下，NtCreateSection函数已经自动完成了栈对齐，因此不需要再次进行对齐操作。

**选择正确的NTSTATUS返回值**  
不同的进程/软件不同地处理对NtCreateSection的调用，并且根据返回的NTSTATUS调用行为不同。一些进程/软件可能会忽略返回值，其他进程/软件将尝试无限重复调用等等。我尝试防止amsi.dll加载到新生成的Powershell进程中，当返回NTSTATUS
0时，Powershell会崩溃，这是因为Windows
OS和/或Microsoft认为Section已经成功创建，因此继续正常执行而不处理结果崩溃。但是，当传递像0xC0000054-STATUS_FILE_LOCK_CONFLICT这样的错误时，此错误将被正确处理，并且amsi.dll不会被加载，但是Powershell仍将启动。

然而，在使用不同的可执行文件或EDR
DLL时，可能会出现GUI错误消息的情况。只要没有人按下“确定”按钮，程序就不会继续执行。作者个人的经验是，对于阻止EDR
DLL，最好仍然返回NTSTATUS成功值，但如果遇到问题，可以尝试调整该值。

**概念证明-Ruy Lopez**  
该恶意软件的技术方法可以欺骗EDR（终端检测和响应）系统，使其无法检测到恶意软件的存在。EDR通常被视为在象棋游戏中扮演白方的角色，但是使用这种方法，恶意软件可以像白方一样行动，并在EDR
DLL加载之前进入远程进程并防止其加载。我将此称为“Ruy Lopez”，这是一种起始技术，来自于国际象棋中白方的开局策略。

一个已经发布的概念证明（Proof of
Concept）执行后将在挂起模式下生成一个新的PowerShell，将Shellcode写入该挂起的进程中，并放置钩子，然后恢复它。但由于它只是一个概念证明，它只会有效地阻止/防止amsi.dll被加载，从而导致AMSI绕过。如果您想阻止EDR
DLL，您必须修改HookForward代码来实现，这对于学习目的来说，自己动手做总是很好的。

我在测试中发现，我的技术可以成功地检测和防止大多数EDR厂商的恶意软件，但在某些特殊情况下，可能需要根据不同的厂商进行修改或调整。在其中一个测试中，有一个厂商注入DLL而不是以常规方式加载它，这种情况下作者的技术无法阻止。在另一个测试中，作者发现其中一个厂商的五个不同的DLL中有一个会导致进程崩溃，但幸运的是，这个DLL并不是放置钩子的那个。最后，作者提供了一个可以找到这个技术的PoC链接：

  * <https://github.com/S3cur3Th1sSh1t/Ruy-Lopez>

**OPSec安全吗？**  
注入和钩取是一些恶意软件使用的技术，它们允许恶意软件在系统内部运行并执行其操作。然而，这些技术也会留下易于发现的痕迹，称为指标或IoCs。如果蓝队或猎人/分析师审查涉及的进程，就很容易发现这些指标并发现是否发生了恶意活动。作者提到，尽管存在这些指标，但目前还没有自动化的检测机制能够预警或防止这种技术。作者建议EDR供应商可以集成检查，如果一个挂起的进程被恢复，并且在那个时候某些ntdll.dll函数被钩取，则杀死该进程。

**OPSec改进**  
这第一个PoC使用了Win32 API来进行注入和放置hook（钩子），但在Troopers演讲后已经改为直接使用Syscalls（系统调用）。

在发布版本中需要具有RWX权限（可读、可写、可执行），因为Shellcode需要进行一些自我修改。但这并非必需，相对容易调整，我在代码中加了一些注释，以便有兴趣的人进行修改。通过修改程序，也可以使用RX权限（可读、可执行）。

讨论了两种方法来避免Shellcode被检测和拦截。第一种方法是使用哈希算法来代替明文DLL名称，以避免基于签名的检测。第二种方法是使用硬件断点来代替钩子，以避免基于IoC的检测。

**提到了几个潜在的使用方式：**

  1. 绕过Device Guard/信任检查：通过阻止wldp.dll文件的加载来实现。
  2. 阻止自定义的AMSI Provider DLLs的加载。
  3. 使用ThreadlessInject方式的注入/执行Shellcode，这里的Shellcode会在任何DLL加载时自动执行，也会在进程初始化时至少执行一次。这种方法不需要执行原语或者像ThreadlessInject那样放置钩子，而是可以直接解密嵌入的Shellcode并执行它。

**链接 &资源**

  * Hellsgate <https://github.com/am0nsec/HellsGate>
  * RecycledGate <https://github.com/thefLink/RecycledGate>
  * DInvoke <https://github.com/TheWover/DInvoke>
  * Syswhispers <https://github.com/jthuraisamy/SysWhispers>
  * Syswhispers2 <https://github.com/jthuraisamy/SysWhispers2>
  * Syswhispers3 <https://github.com/klezVirus/SysWhispers3>
  * TamperingSyscalls <https://github.com/rad9800/TamperingSyscalls>
  * SharpBlock Blog post <https://ethicalchaos.dev/2020/06/14/lets-create-an-edr-and-bypass-it-part-2/>
  * Chess White player idea <https://bruteratel.com/release/2022/08/18/Release-Scandinavian-Defense/>
  * HandleKatz <https://github.com/codewhitesec/HandleKatz>  
From:<https://s3cur3th1ssh1t.github.io/Cat_Mouse_or_Chess/>

