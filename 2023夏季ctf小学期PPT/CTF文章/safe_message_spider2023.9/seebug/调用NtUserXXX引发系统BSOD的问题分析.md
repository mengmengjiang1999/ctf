作者：Leeqwind  
作者博客：<https://xiaodaozhi.com/kernel/30.html>

这篇文章通过一次在 Windows XP 和 Windows 7 操作系统内核中分别调用同一个 NtUserXxx
系统调用产生不同现象的问题，对其做了简单分析。

最近在驱动中需要实现在一些 HOOK 处理函数中调用如 NtUserBuildHwndList 这样的 API
对目标样本进程的窗口状态（是否存在窗口等）进行判定。NtUserBuildHwndList 是用来根据线程 ID 生成与线程信息结构体
tagTHREADINFO 关联的 tagDESKTOP 桌面对象中存在的窗口对象句柄列表的 USER 系统调用，其函数声明如下：

    
    
    NTSTATUS
    NtUserBuildHwndList (
        IN  HDESK  hdesk,
        IN  HWND   hwndNext,
        IN  BOOL   fEnumChildren,
        IN  DWORD  idThread,
        IN  UINT   cHwndMax,
        OUT HWND  *phwndFirst,
        OUT PUINT  pcHwndNeeded
        );

实现代码在 Windows 7 下一切正常，但在 Windows XP 中的部分进程上下文中调用时会产生的偶发 BSOD
异常。为了解决该问题，通过内核调试进行分析。

#### 分析

挂上 WinDBG 内核调试模式启动 Windows XP 的虚拟机镜像，加载驱动并执行样本进程。幸运的是很快触发预期的异常。

    
    
    Access violation - code c0000005 (!!! second chance !!!)
    win32k!InternalBuildHwndList+0x1a:
    bf835e26 8b402c          mov     eax,dword ptr [eax+2Ch]
    kd> dc eax+2Ch l 1
    0000002c  ????????                             ????
    kd> r eax
    eax=00000000
    kd> kv
    ChildEBP RetAddr  Args to Child
    ee609c04 bf835d37 e12dc350 bc6bc8c8 0000000a win32k!InternalBuildHwndList+0x1a (FPO: [Non-Fpo])
    ee609c1c bf835fa7 bc6bc8c8 0000000a e2610870 win32k!BuildHwndList+0x4f (FPO: [Non-Fpo])
    ee609c60 ede0b2aa 00000000 00000000 00000000 win32k!NtUserBuildHwndList+0xd8 (FPO: [Non-Fpo])
    ee609ca8 ede0b3f3 85e45da0 862845a0 c0000001 MyDriver!MyCallOfNtUserBuildHwndList+0x10a (FPO: [Non-Fpo])

根据信息显示，是在 win32k!InternalBuildHwndList 函数中触发了异常。根据栈回溯可知，在我们的驱动模块调用
win32k!NtUserBuildHwndList 例程之后，实际调用 win32k!BuildHwndList 函数，随后进入
win32k!InternalBuildHwndList 例程中。最终在 InternalBuildHwndList 中发生了异常。

    
    
    win32k!InternalBuildHwndList:
    bf835e10 8bff            mov     edi,edi
    bf835e12 55              push    ebp
    bf835e13 8bec            mov     ebp,esp
    bf835e15 56              push    esi
    bf835e16 57              push    edi
    bf835e17 8b7d0c          mov     edi,dword ptr [ebp+0Ch]
    bf835e1a 85ff            test    edi,edi
    bf835e1c 74e8            je      win32k!InternalBuildHwndList+0x94 (bf835e06)
    bf835e1e 8b7508          mov     esi,dword ptr [ebp+8]
    bf835e21 a118ae9abf      mov     eax,dword ptr [win32k!gptiCurrent (bf9aae18)]
    bf835e26 8b402c          mov     eax,dword ptr [eax+2Ch]   <- ACCESS VIOLATION, eax=0x00000000
    bf835e29 8b8894010000    mov     ecx,dword ptr [eax+194h]
    bf835e2f 8b460c          mov     eax,dword ptr [esi+0Ch]
    
    win32k!BuildHwndList:
    bf835d08 8bff            mov     edi,edi
    bf835d0a 55              push    ebp
    bf835d0b 8bec            mov     ebp,esp
    bf835d0d a174949abf      mov     eax,dword ptr [win32k!pbwlCache (bf9a9474)]
    bf835d12 85c0            test    eax,eax
    bf835d14 74cd            je      win32k!BuildHwndList+0x17 (bf835ce3)
    bf835d16 832574949abf00  and     dword ptr [win32k!pbwlCache (bf9a9474)],0
    bf835d1d 53              push    ebx
    bf835d1e 8b5d0c          mov     ebx,dword ptr [ebp+0Ch]
    bf835d21 53              push    ebx
    bf835d22 ff7508          push    dword ptr [ebp+8]
    bf835d25 8d4810          lea     ecx,[eax+10h]
    bf835d28 894804          mov     dword ptr [eax+4],ecx
    bf835d2b 8b4d10          mov     ecx,dword ptr [ebp+10h]
    bf835d2e 50              push    eax
    bf835d2f 89480c          mov     dword ptr [eax+0Ch],ecx
    bf835d32 e8d9000000      call    win32k!InternalBuildHwndList (bf835e10)   <- CALL InternalBuildHwndList
    bf835d37 8b4804          mov     ecx,dword ptr [eax+4]
    bf835d3a 3b4808          cmp     ecx,dword ptr [eax+8]
    
    win32k!NtUserBuildHwndList:
    bf835f21 6a14            push    14h
    bf835f23 68e8d798bf      push    offset win32k!`string'+0x550 (bf98d7e8)
    bf835f28 e8dbacfcff      call    win32k!_SEH_prolog (bf800c08)
    bf835f2d 6a02            push    2
    bf835f2f 5f              pop     edi
    bf835f30 e825acfcff      call    win32k!EnterCrit (bf800b5a)
    bf835f35 a158aa9abf      mov     eax,dword ptr [win32k!gpsi (bf9aaa58)]
    bf835f3a f6400208        test    byte ptr [eax+2],8
    bf835f3e 0f8547ffffff    jne     win32k!NtUserBuildHwndList+0x1f (bf835e8b)
    bf835f44 8b4d0c          mov     ecx,dword ptr [ebp+0Ch]
    bf835f47 33db            xor     ebx,ebx
    bf835f49 3bcb            cmp     ecx,ebx
    bf835f4b 0f8542ffffff    jne     win32k!NtUserBuildHwndList+0x2b (bf835e93)
    bf835f51 33c0            xor     eax,eax
    bf835f53 395d14          cmp     dword ptr [ebp+14h],ebx
    bf835f56 0f84e0000000    je      win32k!NtUserBuildHwndList+0x69 (bf83603c)
    bf835f5c ff7514          push    dword ptr [ebp+14h]
    bf835f5f e89439feff      call    win32k!PtiFromThreadId (bf8198f8)
    bf835f64 8bf0            mov     esi,eax
    bf835f66 3bf3            cmp     esi,ebx
    bf835f68 0f8423010000    je      win32k!NtUserBuildHwndList+0x65 (bf836091)
    bf835f6e 8b463c          mov     eax,dword ptr [esi+3Ch]
    bf835f71 3bc3            cmp     eax,ebx
    bf835f73 0f8418010000    je      win32k!NtUserBuildHwndList+0x65 (bf836091)
    bf835f79 8b4004          mov     eax,dword ptr [eax+4]
    bf835f7c 8b4008          mov     eax,dword ptr [eax+8]
    bf835f7f 8b4038          mov     eax,dword ptr [eax+38h]
    bf835f82 395d08          cmp     dword ptr [ebp+8],ebx
    bf835f85 0f85dd000000    jne     win32k!NtUserBuildHwndList+0x70 (bf836068)
    bf835f8b 895de4          mov     dword ptr [ebp-1Ch],ebx
    bf835f8e 3bc3            cmp     eax,ebx
    bf835f90 0f84ad000000    je      win32k!NtUserBuildHwndList+0xaa (bf836043)
    bf835f96 395d10          cmp     dword ptr [ebp+10h],ebx
    bf835f99 0f8572ffffff    jne     win32k!NtUserBuildHwndList+0xca (bf835f11)
    bf835f9f 56              push    esi
    bf835fa0 57              push    edi
    bf835fa1 50              push    eax
    bf835fa2 e861fdffff      call    win32k!BuildHwndList (bf835d08)   <- CALL BuildHwndList
    bf835fa7 8bf0            mov     esi,eax
    bf835fa9 8975e0          mov     dword ptr [ebp-20h],esi

发生异常时 eax 寄存器值为零。根据 InternalBuildHwndList 函数的指令序列得知 eax 寄存器存储的是
win32k!gptiCurrent 的值，win32k!gptiCurrent 是一个临界变量。在 NtUserBuildHwndList 函数中通过调用
win32k!EnterCrit 进入临界区，用来确保 USER 相关的各种全局资源能够独占访问。win32k!EnterCrit 通过调用
KeEnterCriticalRegion 进入临界区并通过 ExAcquireResourceExclusiveLite 函数对 gpresUser
资源实施共享锁定之后，调用 PsGetThreadWin32Thread 获取当前线程的线程信息结构体 tagTHREADINFO 指针并赋值给
win32k!gptiCurrent 变量。

    
    
    kd> u win32k!EnterCrit
    win32k!EnterCrit:
    bf800b5a ff1524cb98bf    call    dword ptr [win32k!_imp__KeEnterCriticalRegion (bf98cb24)]
    bf800b60 6a01            push    1
    bf800b62 ff3520ab9abf    push    dword ptr [win32k!gpresUser (bf9aab20)]
    bf800b68 ff159ccb98bf    call    dword ptr [win32k!_imp__ExAcquireResourceExclusiveLite (bf98cb9c)]
    bf800b6e ff1560cb98bf    call    dword ptr [win32k!_imp__PsGetCurrentThread (bf98cb60)]
    bf800b74 50              push    eax
    bf800b75 ff15f4d098bf    call    dword ptr [win32k!_imp__PsGetThreadWin32Thread (bf98d0f4)]
    bf800b7b a318ae9abf      mov     dword ptr [win32k!gptiCurrent (bf9aae18)],eax
    bf800b80 c3              ret

PsGetThreadWin32Thread 函数的指令非常简单：

    
    
    kd> u PsGetThreadWin32Thread
    nt!PsGetThreadWin32Thread:
    8052883a 8bff            mov     edi,edi
    8052883c 55              push    ebp
    8052883d 8bec            mov     ebp,esp
    8052883f 8b4508          mov     eax,dword ptr [ebp+8]
    80528842 8b8030010000    mov     eax,dword ptr [eax+130h]
    80528848 5d              pop     ebp
    80528849 c20400          ret     4

获取当前线程 KTHREAD + 0x130 位置的域的值并作为返回值返回。根据 Windows XP 的定义，该偏移位置存储的是 Win32Thread
指针。

    
    
    kd> dt _KTHREAD
    nt!_KTHREAD
       +0x000 Header           : _DISPATCHER_HEADER
       +0x010 MutantListHead   : _LIST_ENTRY
       +0x018 InitialStack     : Ptr32 Void
       +0x01c StackLimit       : Ptr32 Void
       ...
       +0x12c CallbackStack    : Ptr32 Void
       +0x130 Win32Thread      : Ptr32 Void

然而在 InternalBuildWndList 函数中对 win32k!gptiCurrent
指针变量进行操作之前，并未判断该指针是否为空，直接操作则必然引发异常。事实上，在 Windows XP 操作系统中，Win32k
中的很多例程其默认为在调用自己之前，gptiCurrent 已经是一个有效的值，所以并不进行必要的判断。

然而如果当前线程不是 GUI 线程，如控制台应用程序进程的线程，它们的 Win32Thread 域始终是空值，如果不进行判断就直接在内核中调用
NtUserBuildWndList 等函数，就将直接引发前面提到的 BSOD 异常。幸运的是，用户层进程在通过系统服务调用位于 Win32k.sys
中的系统例程时，其通常通过 User32.dll 或 Gdi32.dll 等动态库模块中的函数来进行，此时该线程应已在内核通过
PsConvertToGuiThread 等函数将其转换成 GUI 线程。

在 Windows 中，所有的线程作为非 GUI 线程启动。如果某线程访问任意 USER 或 GDI 系统调用（调用号 >= 0x1000），Windows
将提升该线程为 GUI 线程（nt!PsConvertToGuiThread）并调用进程和线程呼出接口。

这样一来，通过常规方式从用户层到内核层的标准系统调用来调用 User 或 GDI
的系统服务时，操作系统负责处理相关的初始化和转换操作。但像在我们的驱动程序中执行全局的调用时，就需要对调用的环境（进程和线程）进行必要的判断，而不能轻易地擅自直接进行调用。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/576/>

