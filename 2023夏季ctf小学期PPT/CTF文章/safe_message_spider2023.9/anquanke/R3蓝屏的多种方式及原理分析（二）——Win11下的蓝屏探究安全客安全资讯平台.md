# R3蓝屏的多种方式及原理分析（二）—— Win11下的蓝屏探究

阅读量 **210308**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-21 14:30:32

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t019c61f5d07141930e.jpg)

## 0x00 前言

在前一篇[《R3蓝屏的多种方式及原理分析（一）》](https://www.anquanke.com/post/id/254815)，主要讲解了如何利用`NtRaiseHardError`进行蓝屏，以及它蓝屏的整个“旅程”。剩下的篇幅来介绍第二类蓝屏到底是如何发生的，主要解决以下问题：

    
    
    如何将自己的“地位”提升为系统Critical Process/Thread 
    Critical Process是如何蓝屏的
    变成Critical Thread之后为什么无法蓝屏
    Windows内核Critical Process的设计到底精髓在哪里
    如何利用以及如何防护此类攻击
    

## 0x01 背景

离第一篇的投稿已经过去了好几天，这段时间正好处于Windows
11发布的档口，看了下相关的报道，内核没什么大的更新，主要是更新了UI的内容，我猜测关于这部分的内核内容是没什么变化的，由于之前已经逆过一遍Win10的，那么咱们便直接从Win
11入手开始分析吧，如果跟Win10有很大不同的地方我会指出。有些微软自己官方说的小细节是存在误导的可能性的，还得靠自己来逆，废话不多说，直接开始。

先来看一下Win11下的蓝屏吧，黑屏？？？我觉得还不如蓝屏

![](https://p2.ssl.qhimg.com/t01c2f622319d0d21ad.png)

## 0x02 相关API

根据上一篇就已经知道这4个ＡＰＩ，但仅仅知道了函数名，这一节要详细介绍一下，每个参数的含义，先把逆向出来的各参数含义写在下面。

**特别注意：Rtl系列的两个函数都是`cdecl`(外平栈)，否则会出现栈不平导致报错的情况。**

    
    
    NTSTATUS __cdecl RtlSetProcessIsCritical(    
    IN BOOLEAN     NewValue,                // 想要设置成的新值  0/1  1为启用 Critical Process 0为关闭
    OUT PBOOLEAN OldValue     OPTIONAL,    // 返回的旧值       0/1  返回的是EPROCESS.Flags.BreakOnTermination的值
    IN BOOLEAN     NeedBreaks                 // 是否要求system critical breaks启用 
    )    
    
    NTSTATUS __cdecl RtlSetThreadIsCritical(    
    IN BOOLEAN     NewValue,                // 想要设置成的新值  0/1  1为启用 Critical Thread 0为关闭
    OUT PBOOLEAN OldValue     OPTIONAL,    // 返回的旧值       0/1  ETHREAD.CrossThreadFlags.BreakOnTermination的值
    IN BOOLEAN     NeedBreaks                 // 是否要求system critical breaks启用   
    )        
    
    NTSTATUS NTAPI NtSetInformationProcess(    
    IN HANDLE     ProcessHandle,                            // 进程的句柄  -1为当前进程
    IN PROCESSINFOCLASS     ProcessInformationClass,    // 想要设置的类型
    IN PVOID     ProcessInformation,                        // 参数指针，由第二个参数ProcessInformationClass决定，
                                                        // 由于本文需要设置的是BreakOnTermination，只有是和否
                                                        // 因此只需要bool类型，下面的长度也默认为4
    IN ULONG     ProcessInformationLength                 // 参数长度
    )
    
    NTSTATUS NTAPI NtSetInformationThread(    
    IN HANDLE     ThreadHandle,                            // 线程的句柄  -2为当前线程
    IN THREADINFOCLASS     ThreadInformationClass,            // 想要设置的类型
    IN PVOID     ThreadInformation,                        // 参数指针
    IN ULONG     ThreadInformationLength                 // 参数长度
    )
    

## 0x03 Rtl系如何封装Nt系函数

分析的版本，以下均基于Win11 正式版的ntoskrnl.exe、以及dll文件和pdb文件

![](https://p1.ssl.qhimg.com/t0180a31d918773ae86.png)

###  1.RtlSetThreadIsCritical和RtlSetProcessIsCritical

打开IDA附加到ntdll上，直接开整。这俩函数基本算是一个模子刻出来的，把函数名字里的Process改成Thread，-2改成-1就完美替换。

![](https://p5.ssl.qhimg.com/t014c14ba84a9919397.png)

图上的`ZwQueryInformationxxx()`和`NtSetInformationxxx()`都是四个参数，IDA的F5问题很大，这个上一节已经讲过了，咱们主要是用来看流程，关键的地方还得看汇编。

上面的`NtGlobalFlags`先不谈，先来看看NtSetInformationThread/Process的参数

![](https://p2.ssl.qhimg.com/t012bdab1385b5bd8dc.png)

翻译成C则如下所示

    
    
    status = NtSetInformationThread(GetCurrentThread(), ThreadBreakOnTermination, &Enable, sizeof(Enable));
    status = NtSetInformationProcess(GetCurrentProcess(), ProcessBreakOnTermination, &Enable, sizeof(Enable));
    

###  2.GetCurrentProcess和GetCurrentThread

下面来逐个解析参数，首先第一个参数，为什么是-1和-2？

科普个小知识，`GetCurrentProcess`()和`GetCurrentThread()`返回的都是伪句柄，伪句柄是什么读者可以自行了解。反正结论就是

  * `-1`代表当前`进程`
  * `-2`代表当前`线程`

至于为什么，我也不知道为什么，它的源码就是这么写的，可能就是为了用着方便吧。打开vs，跟踪一下，查看调用堆栈，两个函数分别是`KernelBase!GetCurrentProcess`
`Kernel32!GetCurrentThread`，不知道为什么`kernel32!GetCurrentProcess`转发给kernelbase了，无语子，不就一行代码的事，至于吗？

![](https://p4.ssl.qhimg.com/t014c6b69b7d9b22692.png)

###  3.两个枚举类型PROCESSINFOCLASS和THREADINFOCLASS

两个Nt函数的第二个参数分别为`PROCESSINFOCLASS`和`THREADINFOCLASS`，结构如下

    
    
    typedef enum _THREADINFOCLASS
    {
        ThreadBasicInformation,             //0
        ThreadTimes,                        //1
        ThreadPriority,                     //2
        ThreadBasePriority,                 //3
        ThreadAffinityMask,                 //4
        ThreadImpersonationToken,           //5
        ThreadDescriptorTableEntry,         //6
        ThreadEnableAlignmentFaultFixup,    //7
        ThreadEventPair_Reusable,           //8
        ThreadQuerySetWin32StartAddress,    //9
        ThreadZeroTlsCell,                  //10
        ThreadPerformanceCount,             //11
        ThreadAmILastThread,                //12
        ThreadIdealProcessor,               //13
        ThreadPriorityBoost,                //14
        ThreadSetTlsArrayAddress,           //15
        ThreadIsIoPending,                  //16
        ThreadHideFromDebugger,             //17
        ThreadBreakOnTermination,           //18   0x12
        ThreadSwitchLegacyState,            //19
        ThreadIsTerminated,                 //20
        ThreadLastSystemCall,               //21
        ThreadIoPriority,                   //22
        ThreadCycleTime,                    //23
        ThreadPagePriority,                 //24
        ThreadActualBasePriority,           //25
        ThreadTebInformation,               //26
        ThreadCSwitchMon,                   //27
        MaxThreadInfoClass                  //28
    } THREADINFOCLASS;
    typedef enum _PROCESSINFOCLASS
    {
        ProcessBasicInformation,           //0
        ProcessQuotaLimits,                //1
        ProcessIoCounters,                 //2
        ProcessVmCounters,                 //3
        ProcessTimes,                      //4
        ProcessBasePriority,               //5
        ProcessRaisePriority,              //6
        ProcessDebugPort,                  //7 
        ProcessExceptionPort,              //8
        ProcessAccessToken,                //9
        ProcessLdtInformation,             //10
        ProcessLdtSize,                    //11
        ProcessDefaultHardErrorMode,       //12
        ProcessIoPortHandlers,             //13
        ProcessPooledUsageAndLimits,       //14
        ProcessWorkingSetWatch,            //15
        ProcessUserModeIOPL,               //16 
        ProcessEnableAlignmentFaultFixup,  //17
        ProcessPriorityClass,              //18
        ProcessWx86Information,            //19
        ProcessHandleCount,                //20
        ProcessAffinityMask,               //21
        ProcessPriorityBoost,              //22
        ProcessDeviceMap,                  //23
        ProcessSessionInformation,         //24
        ProcessForegroundInformation,      //25
        ProcessWow64Information,           //26
        ProcessImageFileName,              //27
        ProcessLUIDDeviceMapsEnabled,      //28
        ProcessBreakOnTermination,         //29  0x1D
        ProcessDebugObjectHandle,          //30
        ProcessDebugFlags,                 //31
        ProcessHandleTracing,              //32
        ProcessIoPriority,                 //33
        ProcessExecuteFlags,               //34
        ProcessTlsInformation,             //35
        ProcessCookie,                     //36
        ProcessImageInformation,           //37
        ProcessCycleTime,                  //38
        ProcessPagePriority,               //39
        ProcessInstrumentationCallback,    //40
        ProcessThreadStackAllocation,      //41
        ProcessWorkingSetWatchEx,          //42
        ProcessImageFileNameWin32,         //43
        ProcessImageFileMapping,           //44
        ProcessAffinityUpdateMode,         //45
        ProcessMemoryAllocationMode,       //46
        MaxProcessInfoClass                //47
    } PROCESSINFOCLASS;
    

本文只使用BreakOnTermination的两个，其实`NtSetInformationThread/Process`的功能是很强大的，用处非常多，想法有多大，舞台就有多大，在本文不再展开，后续文章中可能会继续介绍。

第三个参数和第四个参数上面有注释相信大家也都能看得懂。

###  4.NtGlobalFlags

这个东西还是很有用的，以下为它的具体含义。

Description | Symbolic Name | Hexadecimal Value | **Abbreviation** |
**Destination**  
---|---|---|---|---  
[Buffer DbgPrint Output](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/buffer-dbgprint-output) | FLG_DISABLE_DBGPRINT |
0x08000000 | ddp | R,K  
[Create kernel mode stack trace database](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/create-kernel-mode-stack-trace-database)
| FLG_KERNEL_STACK_TRACE_DB | 0x2000 | kst | R  
[Create user mode stack trace database](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/create-user-mode-stack-trace-database) |
FLG_USER_STACK_TRACE_DB | 0x1000 | ust | R,K,I  
[Debug initial command](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debug-initial-command) | FLG_DEBUG_INITIAL_COMMAND |
0x04 | dic | R  
[Debug WinLogon](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debug-winlogon) | FLG_DEBUG_INITIAL_COMMAND_EX |
0x04000000 | dwl | R  
[Disable heap coalesce on free](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/disable-heap-coalesce-on-free) |
FLG_HEAP_DISABLE_COALESCING | 0x00200000 | dhc | R,K,I  
[Disable paging of kernel stacks](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/disable-paging-of-kernel-stacks) |
FLG_DISABLE_PAGE_KERNEL_STACKS | 0x080000 | dps | R  
[Disable protected DLL verification](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/disable-protected-dll-verification) |
FLG_DISABLE_PROTDLLS | 0x80000000 | dpd | R,K,I  
[Disable stack extension](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/disable-stack-extension) |
FLG_DISABLE_STACK_EXTENSION | 0x010000 | dse | I  
[Early critical section event creation](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/early-critical-section-event-creation) |
FLG_CRITSEC_EVENT_CREATION | 0x10000000 | cse | R,K,I  
[Enable application verifier](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-application-verifier) |
FLG_APPLICATION_VERIFIER | 0x0100 | vrf | R,K,I  
[Enable bad handles detection](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-bad-handles-detection) |
FLG_ENABLE_HANDLE_EXCEPTIONS | 0x40000000 | bhd | R,K  
[Enable close exception](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-close-exception) |
FLG_ENABLE_CLOSE_EXCEPTIONS | 0x400000 | ece | R,K  
[Enable debugging of Win32 subsystem](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-debugging-of-win32-subsystem) |
FLG_ENABLE_CSRDEBUG | 0x020000 | d32 | R  
[Enable exception logging](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-exception-logging) |
FLG_ENABLE_EXCEPTION_LOGGING | 0x800000 | eel | R,K  
[Enable heap free checking](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-heap-free-checking) |
FLG_HEAP_ENABLE_FREE_CHECK | 0x20 | hfc | R,K,I  
[Enable heap parameter checking](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-heap-parameter-checking) |
FLG_HEAP_VALIDATE_PARAMETERS | 0x40 | hpc | R,K,I  
[Enable heap tagging](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-heap-tagging) | FLG_HEAP_ENABLE_TAGGING |
0x0800 | htg | R,K,I  
[Enable heap tagging by DLL](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-heap-tagging-by-dll) |
FLG_HEAP_ENABLE_TAG_BY_DLL | 0x8000 | htd | R,K,I  
[Enable heap tail checking](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-heap-tail-checking) |
FLG_HEAP_ENABLE_TAIL_CHECK | 0x10 | htc | R,K,I  
[Enable heap validation on call](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-heap-validation-on-call) |
FLG_HEAP_VALIDATE_ALL | 0x80 | hvc | R,K,I  
[Enable loading of kernel debugger symbols](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-loading-of-kernel-debugger-symbols) | FLG_ENABLE_KDEBUG_SYMBOL_LOAD | 0x040000 | ksl | R,K  
[Enable object handle type tagging](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-object-handle-type-tagging) |
FLG_ENABLE_HANDLE_TYPE_TAGGING | 0x01000000 | eot | R,K  
[Enable page heap](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-page-heap) | FLG_HEAP_PAGE_ALLOCS |
0x02000000 | hpa | R,K,I  
[Enable pool tagging](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-pool-tagging)<br>(Windows 2000 and Windows XP
only) | FLG_POOL_ENABLE_TAGGING | 0x0400 | ptg | R  
[Enable system critical breaks](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-system-critical-breaks) |
FLG_ENABLE_SYSTEM_CRIT_BREAKS | 0x100000 | scb | R, K, I  
[Load image using large pages if possible](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/load-image-using-large-pages-if-possible)
|  |  | lpg | I  
[Maintain a list of objects for each type](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/maintain-a-list-of-objects-for-each-type)
| FLG_MAINTAIN_OBJECT_TYPELIST | 0x4000 | otl | R  
[Enable silent process exit monitoring](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/enable-silent-process-exit-monitoring) |
FLG_MONITOR_SILENT_PROCESS_EXIT | 0x200 |  | R  
[Object Reference Tracing](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/object-reference-tracing)<br>(Windows Vista and
later) |  |  |  | R, K  
[Show loader snaps](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/show-loader-snaps) | FLG_SHOW_LDR_SNAPS | 0x02 | sls
| R,K,I  
[Special Pool](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/special-pool) |  |  | spp | R <br>R,K (Windows Vista
and later)  
[Stop on exception](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/stop-on-exception) | FLG_STOP_ON_EXCEPTION | 0x01 |
soe | R,K,I  
[Stop on hung GUI](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/stop-on-hung-gui) | FLG_STOP_ON_HUNG_GUI | 0x08 |
shg | K  
[Stop on unhandled user-mode exception](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/stop-on-unhandled-user-mode-exception) |
FLG_STOP_ON_UNHANDLED_EXCEPTION | 0x20000000 | sue | R,K,I  
  
上面逆向Rtl得到的值是`0x100000`，它对应是`Enable system critical breaks`，微软官方对它的解释为：The
**Enable system critical breaks** flag forces a system break into the
debugger，大致意思是如果开启它，则可以强制产生一个中断让系统进入内核调试器。

![](https://p2.ssl.qhimg.com/t01b6728c02f21d65d9.png)

这里a3咱们传的值为False直接跳过了，若为True，则会检查是否`Enable system critical
breaks`，如果没有开启则直接返回。这里返回值的含义是 **C0000001: 连到系统上的设备没有发挥作用** 。

`NtGlobalFlags`的很多值都有研究的价值可以用来反调试，这里不再展开，感兴趣的可以自行研究。

## 0x04 NtSetInformationProcess/Thread的逆向分析

从上面就可以看出`NtSetInformationProcess`和`NtSetInformationThread`是具有高度对称性的，代码应该也是差不多的。

> `NtSetInformationProcess(-1,0x1D,P3,4)`

![](https://p1.ssl.qhimg.com/t01d72493383d406dfa.png)

LABEL_46做了清理工作，减少了EPROCESS的引用计数。可以看见如何将进程设置为Critical
Process——将`EPROCESS.Flags.BreakOnTermination(Pos 13)`位 置1

> `NtSetInformationThread(-2,18,P3,4)`

![](https://p0.ssl.qhimg.com/t01ed790c98748a3f5f.png)

同样地，LABEL_48做了清理工作，减少引用计数。可以看见如何将线程设置为Critical
Thread——将`ETHREAD.CrossThreadFlags.BreakOnTermination(Pos 5)`位 置1

至此可以总结出它们的方式： **只用分别设置自己的`BreakOnTermination`位即可**

## 0x05 Critical Process蓝屏实现

上文主要讲了“地位”的提升，接下来就是选择哪个函数结束本进程的问题，我这里使用2个，其实最后都是调用`nt!NtTerminateProcess`。

![](https://p1.ssl.qhimg.com/t018ac1f569a46a6f6c.png)

###  1.代码实现

由于Rtl只是封装，Nt才是本质，所以在代码中我只写Nt的部分，对于Rtl的使用，可以翻到下面看完整项目。

    
    
    #include <stdio.h>
    #include <windows.h>
    
    const ULONG SE_DEBUG_PRIVILEGE = 20;
    
    typedef enum _PROCESSINFOCLASS
    {
        ProcessBasicInformation,           //0
        ProcessQuotaLimits,                //1
        ProcessIoCounters,                 //2
        ProcessVmCounters,                 //3
        ProcessTimes,                      //4
        ProcessBasePriority,               //5
        ProcessRaisePriority,              //6
        ProcessDebugPort,                  //7 
        ProcessExceptionPort,              //8
        ProcessAccessToken,                //9
        ProcessLdtInformation,             //10
        ProcessLdtSize,                    //11
        ProcessDefaultHardErrorMode,       //12
        ProcessIoPortHandlers,             //13
        ProcessPooledUsageAndLimits,       //14
        ProcessWorkingSetWatch,            //15
        ProcessUserModeIOPL,               //16 
        ProcessEnableAlignmentFaultFixup,  //17
        ProcessPriorityClass,              //18
        ProcessWx86Information,            //19
        ProcessHandleCount,                //20
        ProcessAffinityMask,               //21
        ProcessPriorityBoost,              //22
        ProcessDeviceMap,                  //23
        ProcessSessionInformation,         //24
        ProcessForegroundInformation,      //25
        ProcessWow64Information,           //26
        ProcessImageFileName,              //27
        ProcessLUIDDeviceMapsEnabled,      //28
        ProcessBreakOnTermination,         //29  0x1D
        ProcessDebugObjectHandle,          //30
        ProcessDebugFlags,                 //31
        ProcessHandleTracing,              //32
        ProcessIoPriority,                 //33
        ProcessExecuteFlags,               //34
        ProcessTlsInformation,             //35
        ProcessCookie,                     //36
        ProcessImageInformation,           //37
        ProcessCycleTime,                  //38
        ProcessPagePriority,               //39
        ProcessInstrumentationCallback,    //40
        ProcessThreadStackAllocation,      //41
        ProcessWorkingSetWatchEx,          //42
        ProcessImageFileNameWin32,         //43
        ProcessImageFileMapping,           //44
        ProcessAffinityUpdateMode,         //45
        ProcessMemoryAllocationMode,       //46
        MaxProcessInfoClass                //47
    } PROCESSINFOCLASS;
    
    // 函数指针
    typedef NTSYSCALLAPI NTSTATUS(WINAPI *NTSETINFORMATIONPROCESS)(
        IN HANDLE               ProcessHandle,
        IN PROCESSINFOCLASS ProcessInformationClass,
        IN PVOID                ProcessInformation,
        IN ULONG                ProcessInformationLength
        );
    typedef BOOL(__cdecl *RTLADJUSTPRIVILEGE)(ULONG, BOOL, BOOL, PBOOLEAN);
    
    
    NTSETINFORMATIONPROCESS NtSetInformationProcess;
    RTLADJUSTPRIVILEGE RtlAdjustPrivilege;
    
    int main()
    {
        // 任何进程都会自动加载ntdll
        HMODULE  NtBase = GetModuleHandle(TEXT("ntdll.dll"));
        if (!NtBase) return false;
    
        // 获取各函数地址
        NtSetInformationProcess = (NTSETINFORMATIONPROCESS)GetProcAddress(NtBase, "NtSetInformationProcess");
        RtlAdjustPrivilege = (RTLADJUSTPRIVILEGE)GetProcAddress(NtBase, "RtlAdjustPrivilege");
    
        BOOLEAN A;
        BOOL Enable = TRUE;
    
        // RtlAdjustPrivilege返回值为0才成功
        if (RtlAdjustPrivilege(SE_DEBUG_PRIVILEGE, TRUE, FALSE, &A))
        {
            printf("------Please run program as an Administrator------\n");
            system("pause");
            return FALSE;
        }
    
        // 设置本进程为Critical Process
        NtSetInformationProcess(GetCurrentProcess(), ProcessBreakOnTermination, &Enable, sizeof(Enable));
    
        // 退出
        ExitProcess(0);
        //TerminateProcess((HANDLE)-1, 0);
    
        return 0;
    }
    

###  2.流程分析

首先不附加内核调试器，直接蓝。

恢复快照，随后附加一下Windbg，再运行，出现一个Input，让你输入，输入B(b)则windbg会接收到一个断点，输入I(i)，则会忽略该错误继续运行，栈回溯看一下。

![](https://p4.ssl.qhimg.com/t0110a2de6f58d85da2.png)

看来就是这个函数导致蓝屏，若附加内核调试器，则会被调试器接收，否则会直接蓝屏，接下来看看这个函数的执行流程。

###  3.PspCatchCriticalBreak

这个函数在Win11中与Win10中稍有不同，对于内核调试而言，在Win10中仅有Break(B,b)，Ignore(I,i)两种选择，这两种选择都无法造成蓝屏，而在`Win11中新增了Continue(C,c)选项`，选择C则会导致蓝屏。

![](https://p1.ssl.qhimg.com/t0111e399e755837981.png)

ETHREAD & 0x7F取了当前对象的类型，咱们这里是`Critical
Process`，因此当然是EPROCESS。我这里为了方便直接将其重命名为EPROCESS，实际情况还是根据传进来的对象来判断是进程还是线程。

![](https://p5.ssl.qhimg.com/t01082249ea481b1369.png)

最后调用了`KeBugCheckEx()`实现蓝屏。通过栈回溯咱们知道前面还有2个函数，`nt!PspTerminateAllThreads`和`nt!NtTerminateProcess`，大家应该都能猜到肯定是检查了EPROCESS的`BreakOnTermination`位才进入`PspCatchCriticalBreak`，但是这俩函数还是和后面的线程一起分析比较好。

## 0x06 思考

首先提出猜想：既然进程能像上面那样操作，先设置，再退出。那么线程是否可以呢？直接写代码开始测试

    
    
    #include <stdio.h>
    #include <windows.h>
    
    const ULONG SE_DEBUG_PRIVILEGE = 20;
    typedef enum _THREADINFOCLASS
    {
        ThreadBasicInformation,             //0
        ThreadTimes,                        //1
        ThreadPriority,                     //2
        ThreadBasePriority,                 //3
        ThreadAffinityMask,                 //4
        ThreadImpersonationToken,           //5
        ThreadDescriptorTableEntry,         //6
        ThreadEnableAlignmentFaultFixup,    //7
        ThreadEventPair_Reusable,           //8
        ThreadQuerySetWin32StartAddress,    //9
        ThreadZeroTlsCell,                  //10
        ThreadPerformanceCount,             //11
        ThreadAmILastThread,                //12
        ThreadIdealProcessor,               //13
        ThreadPriorityBoost,                //14
        ThreadSetTlsArrayAddress,           //15
        ThreadIsIoPending,                  //16
        ThreadHideFromDebugger,             //17
        ThreadBreakOnTermination,           //18   0x12
        ThreadSwitchLegacyState,            //19
        ThreadIsTerminated,                 //20
        ThreadLastSystemCall,               //21
        ThreadIoPriority,                   //22
        ThreadCycleTime,                    //23
        ThreadPagePriority,                 //24
        ThreadActualBasePriority,           //25
        ThreadTebInformation,               //26
        ThreadCSwitchMon,                   //27
        MaxThreadInfoClass                  //28
    } THREADINFOCLASS;
    
    // 函数指针
    typedef NTSYSCALLAPI NTSTATUS(WINAPI *NTSETINFORMATIONTHREAD)(
        HANDLE ThreadHandle,
        THREADINFOCLASS ThreadInformationClass,
        PVOID ThreadInformation,
        ULONG ThreadInformationLength
        );
    typedef BOOL(__cdecl *RTLADJUSTPRIVILEGE)(ULONG, BOOL, BOOL, PBOOLEAN);
    
    
    NTSETINFORMATIONTHREAD NtSetInformationThread;
    RTLADJUSTPRIVILEGE RtlAdjustPrivilege;
    
    int main()
    {
        // 任何进程都会自动加载ntdll
        HMODULE  NtBase = GetModuleHandle(TEXT("ntdll.dll"));
        if (!NtBase) return false;
    
        // 获取各函数地址
        NtSetInformationThread = (NTSETINFORMATIONTHREAD)GetProcAddress(NtBase, "NtSetInformationThread");
        RtlAdjustPrivilege = (RTLADJUSTPRIVILEGE)GetProcAddress(NtBase, "RtlAdjustPrivilege");
    
        BOOLEAN A;
        BOOL Enable = TRUE;
    
        // RtlAdjustPrivilege返回值为0才成功
        if (RtlAdjustPrivilege(SE_DEBUG_PRIVILEGE, TRUE, FALSE, &A))
        {
            printf("------Please run program as an Administrator------\n");
            system("pause");
            return FALSE;
        }
    
        // 设置本进程为Critical Process
        NtSetInformationThread(GetCurrentThread(), ThreadBreakOnTermination, &Enable, sizeof(Enable));
    
        // 退出
        ExitProcess(0);
        //TerminateProcess((HANDLE)-1, 0);
    }
    

**很遗憾，执行了一下发现并没有蓝屏，这也是网上经常出现的代码，很多人在各论坛里抄来抄去，却不知道这段代码根本不好使**
。我觉得这段代码应该是XP时期的，因为它在XP下是可以蓝的。

这代码乍一看，确实觉得没问题，退出进程不就会退出所有的线程吗？那么退出线程里检测到BreakOnTermination为1就应该蓝屏啊。

继续猜测：第一个参数传的是-2，当前线程即主线程。莫非是主线程不能作为`Critical Therad`？那么我将所有线程全部设成`Critical
Therad`呢？

我这里用vs2015选择x64 Release版本，这样子设置程序就会有4个线程（如果没有的话，可以自己多创建几个线程），方便进行测试

    
    
    #include <stdio.h>
    #include <windows.h>
    #include <tlhelp32.h>
    const ULONG SE_DEBUG_PRIVILEGE = 20;
    
    typedef enum _THREADINFOCLASS
    {
        ThreadBasicInformation,             //0
        ThreadTimes,                        //1
        ThreadPriority,                     //2
        ThreadBasePriority,                 //3
        ThreadAffinityMask,                 //4
        ThreadImpersonationToken,           //5
        ThreadDescriptorTableEntry,         //6
        ThreadEnableAlignmentFaultFixup,    //7
        ThreadEventPair_Reusable,           //8
        ThreadQuerySetWin32StartAddress,    //9
        ThreadZeroTlsCell,                  //10
        ThreadPerformanceCount,             //11
        ThreadAmILastThread,                //12
        ThreadIdealProcessor,               //13
        ThreadPriorityBoost,                //14
        ThreadSetTlsArrayAddress,           //15
        ThreadIsIoPending,                  //16
        ThreadHideFromDebugger,             //17
        ThreadBreakOnTermination,           //18   0x12
        ThreadSwitchLegacyState,            //19
        ThreadIsTerminated,                 //20
        ThreadLastSystemCall,               //21
        ThreadIoPriority,                   //22
        ThreadCycleTime,                    //23
        ThreadPagePriority,                 //24
        ThreadActualBasePriority,           //25
        ThreadTebInformation,               //26
        ThreadCSwitchMon,                   //27
        MaxThreadInfoClass                  //28
    } THREADINFOCLASS;
    
    // 函数指针
    typedef NTSYSCALLAPI NTSTATUS(WINAPI *NTSETINFORMATIONTHREAD)(
        HANDLE ThreadHandle,
        THREADINFOCLASS ThreadInformationClass,
        PVOID ThreadInformation,
        ULONG ThreadInformationLength
        );
    typedef BOOL(__cdecl *RTLADJUSTPRIVILEGE)(ULONG, BOOL, BOOL, PBOOLEAN);
    
    
    NTSETINFORMATIONTHREAD NtSetInformationThread;
    RTLADJUSTPRIVILEGE RtlAdjustPrivilege;
    
    int main()
    {
        // 任何进程都会自动加载ntdll
        HMODULE  NtBase = GetModuleHandle(TEXT("ntdll.dll"));
        if (!NtBase) return false;
    
        // 获取各函数地址
        NtSetInformationThread = (NTSETINFORMATIONTHREAD)GetProcAddress(NtBase, "NtSetInformationThread");
        RtlAdjustPrivilege = (RTLADJUSTPRIVILEGE)GetProcAddress(NtBase, "RtlAdjustPrivilege");
    
        BOOLEAN A;
        BOOL Enable = TRUE;
    
        // RtlAdjustPrivilege返回值为0才成功
        if (RtlAdjustPrivilege(SE_DEBUG_PRIVILEGE, TRUE, FALSE, &A))
        {
            printf("------Please run program as an Administrator------\n");
            system("pause");
            return FALSE;
        }
    
        //    将所有线程设置为Critical Therad
        // 拍摄快照，该快照拥有拍摄时刻的所有进程和线程信息
        HANDLE Snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, NULL);
    
        THREADENTRY32 te32;
        // 在使用 Thread32First 前初始化 THREADENTRY32 的结构大小.
        te32.dwSize = sizeof(THREADENTRY32);
    
        // 获取第一个线程
        if (Thread32First(Snapshot, &te32))
        {
            ULONG PID = GetCurrentProcessId();
            HANDLE ThreadHandle = NULL;
            te32.dwSize = sizeof(te32);
            do
            {
                ThreadHandle = OpenThread(THREAD_ALL_ACCESS,FALSE,te32.th32ThreadID);
                // 如果线程属于本进程  则将其设置为Critical Thread
                if (PID == te32.th32OwnerProcessID)
                {
                    NTSTATUS status = NtSetInformationThread(ThreadHandle, ThreadBreakOnTermination, &Enable, sizeof(Enable));
                    printf("线程ID为%X\n",te32.th32ThreadID);
                }
                // 直至遍历完所有线程
            } while (Thread32Next(Snapshot, &te32));
        }
        // 退出
        ExitProcess(0);
        //TerminateProcess((HANDLE)-1, 0);
    }
    

仍然没有蓝屏，是不是没有设置成功呢？用Windbg看一下四个线程的位置

![](https://p1.ssl.qhimg.com/t01a818882e29947341.png)

![](https://p1.ssl.qhimg.com/t011f40c83115fdc4d0.png)

![](https://p3.ssl.qhimg.com/t010f8251c4f6a66fdc.png)

![](https://p0.ssl.qhimg.com/t01a9ab4963d0ee6b67.png)

**四个线程的BreakOnTermination确实已经置1，却还是没有蓝屏。**

看来上面那些都不是蓝屏的重点。尽管没有猜出它蓝屏的条件，但是这种猜测是完全有必要的，有时候能节省不少时间，不能像无头苍蝇一样冲进去就开逆，有时候这样会适得其反，逆向时最重要的就是带着自己的想法和目的去逆，把所有代码都看一遍是不可能的。在这里为大家抛出这些疑问，下一节将带着这些疑问进一步探索`Critical
Therad`的秘密。

## 0x07 总结

本篇主要讲解了Critical
Process/Thread是如何被设置的，Process又是如何导致蓝屏的，介绍了其中的一些重要结构和类型，最终解决了问题1和问题2，经过一些探索又对Critical
Thread产生了疑问，下篇文章将为大家解答这些疑问。

## 0x08 参考

[NtGlobalFlags](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/gflags-flag-table?redirectedfrom=MSDN)  
[Ring3触发BSOD代码实现及内核逆向分析](https://www.anquanke.com/post/id/213412)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Mikasys** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256107](/post/id/256107)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [逆向](/tag/逆向)
  * [windows内核](/tag/windows内核)
  * [操作系统](/tag/操作系统)

 **+1** __7赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) Mikasys

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

