# Ring3触发BSOD代码实现及内核逆向分析

阅读量 **254330**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-10 10:00:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0171caae4b52906ea3.png)

## 0、引言

做过Windows内核开发或者驱动开发的朋友，必然常常会遇到BSoD，其全称为Blue Screen of
Death；of作为介词，其缩写o则需要小写了；然而Windows
NT内核当时推出时，想必微软也大势宣传其是进程安全的，不像DOS那样，一个进程挂了，整个系统就挂了；当然，如果对于系统启动过程非常熟悉的话，应该听说过一些系统的关键进程如csrss.exe挂了的话，则整个系统必然挂；这篇文章的目的就是揭露这后边的秘密，看看系统是如何选择性死亡了，这也牵扯到另一桩生意——一些恶意代码就喜欢鱼死网破。特别是一些服务万千用户的服务器，公司是承受不起这种损失的。

涉及到的知识点：

1、调用为公开的API实现Ring3的BSoD行为；  
2、蓝屏dmp的分析与相关技巧的应用；  
3、通过分析dmp来加快关键算法的定位，找关键逻辑；  
4、借助IDA来逆向分析OS对Critical Process，Thread触发BSoD的实现原理；  
5、安全厂商比较通用的解决方案；

## 1、背景

当关键进程诸如csrss.exe挂掉时，系统是根据什么来判断是否要触发BSoD的呢？一个最直观的想法就是根据进程名来识别，但很快这个想法就被否决了，因为进程名很容易伪造，随便写个程序命名为csrss.exe，然后手动杀掉，系统依旧如初；另一个想法便是OS做了签名检测，如果是微软的签名且EXE的名字还要满足，这个想法有点接近，但很快也被排除了，微软自带了那么多进程，随便找一个带有微软签名的，把进程名改一下，杀掉他，系统依旧运行的妥妥的。当然，这些想法有很多，最核心的方法不是去猜测这些，而是去逆向分析下TerminateProcess
()的内核实现，这个我们再下边会涉及到；接下来我们先用代码实现一下BSoD；

## 2、代码实现

2.1 关键的API介绍

    
    
    NTSTATUS NTAPI NtSetInformationThread(IN HANDLE ThreadHandle,IN THREADINFOCLASS ThreadInformationClass,IN PVOID ThreadInformation,IN ULONG ThreadInformationLength);
    NTSTATUS NTAPI NtSetInformationProcess(IN HANDLE ProcessHandle,IN PROCESSINFOCLASS ProcessInformationClass,IN PVOID ProcessInformation,IN ULONG ProcessInformationLength);
    
    NTSTATUS NTAPI RtlSetThreadIsCritical(IN BOOLEAN NewValue,OUT PBOOLEAN OldValue OPTIONAL,IN BOOLEAN NeedBreaks)
    NTSTATUS NTAPI RtlSetProcessIsCritical (IN BOOLEAN NewValue,OUT PBOOLEAN OldValue OPTIONAL,IN BOOLEAN NeedBreaks);
    

上边这几个API便是实现此目的的核心API，当然除了这些，还有其他的API，原理都是大同小异；简单介绍下，NtSetInformationThread和NtSetInformationProcess这两个API就是针对给定的进程或者线程做一些属性更新操作，大部分操作都是直接操作的进程或者线程对应的内核对象即EPROCESS、ETHREAD中相关的字段；与这两个API对应的则是NtQueryInformationThread()和NtQueryInformationProcess()这两个API，大家可自行查阅学习；

THREADINFOCLASS和PROCESSINFOCLASS这两个枚举常量，官方头文件公布出来的如下：

![](https://p5.ssl.qhimg.com/t017c1b5202990d72a3.png)

确实很小气，THREADINFOCLASS中几乎没给出有用的，PROCESSINFOCLASS中的ProcessBreakOnTermination倒是很显眼；根据网上公开的数据，整理如下：

    
    
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
        ProcessBreakOnTermination,         //29
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
        ThreadBreakOnTermination,           //18
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
    

最核心的就是ProcessBreakOnTermination和ThreadBreakOnTermination，前者的含义是，只要进程挂了，那么就触发BSoD；后者是指定的线程挂了，系统就BSoD；RtlSetThreadIsCritical()和RtlSetProcessIsCritical()仅仅是针对以上两个API调用的简单包装；

2.2 关键API逆向分析

![](https://p1.ssl.qhimg.com/t0120b00f143723716c.png)

![](https://p3.ssl.qhimg.com/t01dd425a63995cd388.png)

上图中的-2和-1分别代表当前线程和当前进程，即GetCurrentThread()和GetCurrentProcess()的返回值；既然ntdll已经帮我们包装好了，那就用呗，不然多不近人情；

2.3 demo代码如下：

    
    
    #include <stdio.h>
    #include <windows.h>
    
    bool EnableDebugPrivilege();
    bool TestCriticalApi();
    typedef NTSTATUS(__cdecl *RTLSETPROCESSISCRITICAL)(IN BOOLEAN NewValue,OUT PBOOLEAN OldValue OPTIONAL,IN BOOLEAN NeedBreaks);
    
    int main(void)
    {
        TestCriticalApi();
        return 0;
    }
    
    bool EnableDebugPrivilege()
    {
        HANDLE hToken = NULL;
        LUID debugPrivilegeValueLuid={0};
        TOKEN_PRIVILEGES tokenPrivilege = {0};
    
        if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken))
            return false;
    
        if (!LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &debugPrivilegeValueLuid))
        {
            CloseHandle(hToken);
            return false;
        }
    
        tokenPrivilege.PrivilegeCount = 1;
        tokenPrivilege.Privileges[0].Luid = debugPrivilegeValueLuid;
        tokenPrivilege.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
        if (!AdjustTokenPrivileges(hToken, FALSE, &tokenPrivilege, sizeof(tokenPrivilege), NULL, NULL))
        {
            CloseHandle(hToken);
            return false;
        }
    
        return true;
    }
    
    bool TestCriticalApi()
    {
        if(!EnableDebugPrivilege())
            return false;
    
        HMODULE  hNtdllMod = GetModuleHandle(TEXT("ntdll.dll"));
        if(!hNtdllMod)
            return false;
    
        RTLSETPROCESSISCRITICAL RtlSetProcessIsCritical;
        RtlSetProcessIsCritical = (RTLSETPROCESSISCRITICAL)GetProcAddress(hNtdllMod, "RtlSetProcessIsCritical");
        if (!RtlSetProcessIsCritical)
            return false;
    
        NTSTATUS status = RtlSetProcessIsCritical(TRUE, NULL, FALSE);
        printf("status:%x\n",status);
    
        getchar();
    
        status = RtlSetProcessIsCritical(FALSE, NULL, FALSE);
        printf("status:%x\n",status);
        getchar();
    
        return true;
    }
    

![](https://p2.ssl.qhimg.com/t01bd4a70df6a27efb8.png)

当执行到第一个getchar()时，用Procexp强制杀掉test.exe进程，则触发BSoD；下边就根据此dmp来追踪BSoD的触发逻辑，这也不失为一种办法；

## 3、通过dmp来追寻OS对CriticalProcess进程的优待

![](https://p3.ssl.qhimg.com/t01ecd93f36018d63f2.png)

3.1 step1 看一下栈回溯

    
    
    0: kd> k
    # Child-SP          RetAddr           Call Site
    00 ffffd001`7039a848 fffff801`876c8d08 nt!KeBugCheckEx
    01 ffffd001`7039a850 fffff801`8760affd nt!PspCatchCriticalBreak+0xa4
    02 ffffd001`7039a890 fffff801`874ac5e9 nt! ?? ::NNGAKEGL::`string'+0x4d47d
    03 ffffd001`7039a8f0 fffff801`874ac2c9 nt!PspTerminateProcess+0xfd
    04 ffffd001`7039a930 fffff801`87162263 nt!NtTerminateProcess+0xb9
    05 ffffd001`7039aa00 00007ffa`c1e9380a nt!KiSystemServiceCopyEnd+0x13
    06 000000e4`b442eb08 00000000`00000000 0x00007ffa`c1e9380a
    

虽然栈回溯不是那么完美，也不要紧，关键的地方出来了，顺着调用栈这几个函数，先简单用Windbg来反汇编看下，后边用IDA来分析下；

3.2 step2 看一下传给KeBugCheckEx的参数

    
    
    void KeBugCheckEx( ULONG BugCheckCode, ULONG_PTR BugCheckParameter1, ULONG_PTR BugCheckParameter2, ULONG_PTR BugCheckParameter3, ULONG_PTR BugCheckParameter4 );
    https://docs.microsoft.com/zh-cn/windows-hardware/drivers/ddi/wdm/nf-wdm-kebugcheckex
    

函数原型如上，共计五个参数，后边的四个参数都是依赖于第一个参数BugCheckCode而不同的，下边就顺道带着大家一起来处理下这个问题——怎么用Windbg来处理；

x64下，函数的前四个参数是通过”cd89”这几个寄存器实现的，后边的参数通过栈传递，所以这里我们需要返回到调用KeBugCheckEx的上一级来查看传入的参数；当然也可以通过其他手段直接在本层查找，后边解64位程序的dmp时再来详解其趣事；

    
    
    0: kd> ub fffff801`876c8d08
    nt!PspCatchCriticalBreak+0x85:
    fffff801`876c8ce9 400fb6ce        movzx   ecx,sil
    fffff801`876c8ced 3c06            cmp     al,6
    fffff801`876c8cef 4889742420      mov     qword ptr [rsp+20h],rsi
    fffff801`876c8cf4 0f44cd          cmove   ecx,ebp
    fffff801`876c8cf7 4533c9          xor     r9d,r9d
    fffff801`876c8cfa 440fb6c1        movzx   r8d,cl
    fffff801`876c8cfe b9ef000000      mov     ecx,0EFh
    fffff801`876c8d03 e818efa8ff      call    nt!KeBugCheckEx (fffff801`87157c20)
    

ecx寄存器的值为0xEF，即BugCheckCode为0xEF，下一步就要确定其后的几个参数的意义了，这时Windbg的帮助文档就显神通了；且看我操作：

![](https://p0.ssl.qhimg.com/t01abf6ff1edfb5adb3.png)

根据文档提示，后边的几个参数全是Reserved，不用关心；

3.2 step2 nt! ?? ::NNGAKEGL::`string’+0x4d47d这个看中像字符串，分析下里边有没有可识别的字符

    
    
    0: kd> ub fffff801`8760affd
    nt! ?? ::NNGAKEGL::`string'+0x4d45a:
    fffff801`8760afda 488bd8          mov     rbx,rax
    fffff801`8760afdd e816e9aeff      call    nt!PsGetServerSiloState (fffff801`870f98f8)
    fffff801`8760afe2 83f802          cmp     eax,2
    fffff801`8760afe5 7416            je      nt! ?? ::NNGAKEGL::`string'+0x4d47d (fffff801`8760affd)
    fffff801`8760afe7 4c8d8748040000  lea     r8,[rdi+448h]
    fffff801`8760afee 488bd7          mov     rdx,rdi
    fffff801`8760aff1 488d0d3894faff  lea     rcx,[nt! ?? ::NNGAKEGL::`string' (fffff801`875b4430)]
    fffff801`8760aff8 e867dc0b00      call    nt!PspCatchCriticalBreak (fffff801`876c8c64)
    
    0: kd> db fffff801`875b4430
    fffff801`875b4430  54 65 72 6d 69 6e 61 74-69 6e 67 20 63 72 69 74  Terminating crit
    fffff801`875b4440  69 63 61 6c 20 70 72 6f-63 65 73 73 20 30 78 25  ical process 0x%
    fffff801`875b4450  70 20 28 25 73 29 0a 00-cc cc cc cc cc cc cc cc  p (%s)..........
    fffff801`875b4460  42 72 65 61 6b 2c 20 6f-72 20 49 67 6e 6f 72 65  Break, or Ignore
    fffff801`875b4470  20 28 62 69 29 3f 20 00-cc cc cc cc cc cc cc cc   (bi)? .........
    fffff801`875b4480  43 72 69 74 69 63 61 6c-20 74 68 72 65 61 64 20  Critical thread
    fffff801`875b4490  30 78 25 70 20 28 69 6e-20 25 73 29 20 65 78 69  0x%p (in %s) exi
    fffff801`875b44a0  74 65 64 0a 00 cc cc cc-cc cc cc cc cc cc cc cc  ted.............
    0: kd> da /c 100 fffff801`875b4430
    fffff801`875b4430  "Terminating critical process 0x%p (%s)."
    0: kd> da /c 100 fffff801`875b4460
    fffff801`875b4460  "Break, or Ignore (bi)? "
    0: kd> da /c 100 fffff801`875b4480
    fffff801`875b4480  "Critical thread 0x%p (in %s) exited."
    

确实是个字符串，准确说是个格式化字符串；其实要找到这些参数对应的数据也是很简单的事情，我这里给出结果，大家可自行实验找到数据；

    
    
    0: kd> dq ffffd001`7039a850
    ffffd001`7039a850  00000000`000000ef ffffe001`07819080
    ffffd001`7039a860  00000000`00000000 00000000`00000000
    ffffd001`7039a870  00000000`00000000 ffffe001`08b73380
    ffffd001`7039a880  ffffe001`07819080 fffff801`8760affd
    ffffd001`7039a890  00000000`00000000 ffffe001`08b736a0
    ffffd001`7039a8a0  00000000`00000000 00000000`00000000
    ffffd001`7039a8b0  00000000`00000000 00000000`00000001
    ffffd001`7039a8c0  00000000`00000001 ffffe001`08b73380
    
    rdi:ffffe001`07819080
    rdx:ffffe001`07819080
    r8:rdi+448=ffffe001`078194c8
    
    0: kd> db ffffe001`078194c8
    ffffe001`078194c8  74 65 73 74 2e 65 78 65-00 00 00 00 00 00 00 02  test.exe........
    

3.3 step3 分析下nt!PspTerminateProcess为何调用到KeBugCheckEx

    
    
    0: kd> ub fffff801`874ac5e9
    nt!PspTerminateProcess+0xd9:
    fffff801`874ac5c5 e8b65cbaff      call    nt!KeAbPostRelease (fffff801`87052280)
    fffff801`874ac5ca 4883bbf006000000 cmp     qword ptr [rbx+6F0h],0
    fffff801`874ac5d2 0f85c4771500    jne     nt! ?? ::NNGAKEGL::`string'+0x4621c (fffff801`87603d9c)
    fffff801`874ac5d8 448bce          mov     r9d,esi
    fffff801`874ac5db 458bc6          mov     r8d,r14d
    fffff801`874ac5de 498bd4          mov     rdx,r12
    fffff801`874ac5e1 488bcb          mov     rcx,rbx
    fffff801`874ac5e4 e8b3420100      call    nt!PspTerminateAllThreads (fffff801`874c089c)
    

看来是这个nt!PspTerminateAllThreads里边搞的事情，用Windbg来分析的话，有点不太合适了，我们用IDA来分析下；

## 4、IDA分析nt!PspTerminateAllThreads内部针对Critical Process、Thread的特殊处理

代码中是取的EPROCESS偏移0x304位置处的数据，且判断的是该数据的bit13的这个位是否为1，为1的话则命中下边的逻辑，ok，下边就是分析下EPROCESS
0x304偏移处的数据的bit13位是什么了；如下：

![](https://p5.ssl.qhimg.com/t012ac361d4c0bb9e90.png)

    
    
    0: kd> dt _EPROCESS
    nt!_EPROCESS
        ...
       +0x304 Flags            : Uint4B
       +0x304 CreateReported   : Pos 0, 1 Bit
       +0x304 NoDebugInherit   : Pos 1, 1 Bit
       +0x304 ProcessExiting   : Pos 2, 1 Bit
       +0x304 ProcessDelete    : Pos 3, 1 Bit
       +0x304 ControlFlowGuardEnabled : Pos 4, 1 Bit
       +0x304 VmDeleted        : Pos 5, 1 Bit
       +0x304 OutswapEnabled   : Pos 6, 1 Bit
       +0x304 Outswapped       : Pos 7, 1 Bit
       +0x304 FailFastOnCommitFail : Pos 8, 1 Bit
       +0x304 Wow64VaSpace4Gb  : Pos 9, 1 Bit
       +0x304 AddressSpaceInitialized : Pos 10, 2 Bits
       +0x304 SetTimerResolution : Pos 12, 1 Bit
       +0x304 BreakOnTermination : Pos 13, 1 Bit
       +0x304 DeprioritizeViews : Pos 14, 1 Bit
       +0x304 WriteWatch       : Pos 15, 1 Bit
       +0x304 ProcessInSession : Pos 16, 1 Bit
       +0x304 OverrideAddressSpace : Pos 17, 1 Bit
       +0x304 HasAddressSpace  : Pos 18, 1 Bit
       +0x304 LaunchPrefetched : Pos 19, 1 Bit
       +0x304 Background       : Pos 20, 1 Bit
       +0x304 VmTopDown        : Pos 21, 1 Bit
       +0x304 ImageNotifyDone  : Pos 22, 1 Bit
       +0x304 PdeUpdateNeeded  : Pos 23, 1 Bit
       +0x304 VdmAllowed       : Pos 24, 1 Bit
       +0x304 ProcessRundown   : Pos 25, 1 Bit
       +0x304 ProcessInserted  : Pos 26, 1 Bit
       +0x304 DefaultIoPriority : Pos 27, 3 Bits
       +0x304 ProcessSelfDelete : Pos 30, 1 Bit
         ...
    

由此可知，nt!PspTerminateAllThreads会判断当前的进程的BreakOnTermination位是否置位，即当前进程是否为Critical
Process，若是的话，则触发BSoD的逻辑；逻辑基本全部屡清楚了；

## 5、留一个作业

大家可以尝试着分析下NtSetInformationProcess或者NtSetInformationThread设置进程或线程的Critical属性时，设置的是哪里。思路如下：

1）常规的办法是直接IDA逆向分析，找到关键点；

2）讨巧的方法是用Windbg下一个内存写断点；

## 6、需要解决的问题

作为安全厂商，我们该如何针对客户提供保护呢？一些常规的方法大概如下：  
1、HOOK相关的API，当执行类似的操作时，根据后台下发的策略做相应的校验拦截动作；  
2、定时遍历系统所有的进程，进行比较，将系统自身关键进程排除掉，其他Critical进程或者线程根据后台下发的策略进程恢复；  
3、直接根据后台策略修改命中策略进程EPROCESS，ETHREAD相关字段；

## 7、总结

1、学习了在Ring3如何通过普通的代码粗发BSoD；并代码实现了；  
2、学习了OS提供这种机制的背后的原理；  
3、学习了Windbg如何简单分析BSoD；  
4、逆向分析了部分关键代码，了解OS的操作方法；  
5、给出了通用的解决方法；

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **void *** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/213412](/post/id/213412)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [逆向工程](/tag/逆向工程)
  * [windbg](/tag/windbg)
  * [IDA](/tag/IDA)
  * [dmp](/tag/dmp)
  * [BSoD](/tag/BSoD)

 **+1** __5赞

 __收藏

![](https://p5.ssl.qhimg.com/t013c5d4d3bc7c086d8.jpg) void *

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

