**作者：wzt  
原文链接：<https://mp.weixin.qq.com/s/M_juT5PZrMMmqYYAwenKnw>**

# **1 前言**

Windows10提供了 ACG (Arbitrary Code Guard)
保护功能，官方解释其功能为：禁止进程动态分配可执行内存或者将已经存在的一段可读可写内存改为可执行。在笔者对其进行逆向工程后，会发现其功能包括以下情景：

  * 用NTAllocVirtualMemory新申请一块可执行内存。
  * 当前只读， 不能改为可执行。
  * 当前读写， 不能改为可执行。
  * 在当前执行权限为可执行的情况下， 不能加入可读写权限。

## **1.1 应用层探视**

通过如下代码，测试 ACG 行为：

    
    
        void alloc_test(void)
        {
            LPVOID mem;
            DWORD old_flags;
    
            mem = VirtualAlloc(NULL, 0x100, MEM_COMMIT| MEM_RESERVE, PAGE_EXECUTE);
            if (!mem) {
                printf("error: %d\n", GetLastError());
                return;
            }
            printf("\nalloc at 0x%p\n", mem);
        }

新申请一块可执行内存会被系统拒绝掉。

    
    
        void alloc_test(void)
        {
            LPVOID mem;
            DWORD old_flags;
    
            mem = VirtualAlloc(NULL, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
            if (!mem) {
                printf("error: %d\n", GetLastError());
                return;
            }
            printf("\nalloc at 0x%p\n", mem);
    
            old_flags = PAGE_READWRITE;
            if (VirtualProtect(mem, 0x100, PAGE_EXECUTE_READWRITE, &old_flags) == 0) {
                printf("change memory page exccute error: %d\n", GetLastError());
                return ;
            }
    
            printf("change memory page ok.\n");
            return;
        }

如果先申请一块可读写内存， 然后更改为可执行，同样拒绝。 用 windbg 跟踪得到如下调用链：

    
    
    KERNELBASE!VirtualProtect -> ntdll!NtProtectVirtualMemory
    0:000> kcL
    # Call Site
    00 ntdll!NtProtectVirtualMemory
    01 KERNELBASE!VirtualProtect
    02 test7!alloc_test
    03 test7!main
    04 test7!invoke_main
    05 test7!__scrt_common_main_seh
    06 test7!__scrt_common_main
    07 test7!mainCRTStartup
    08 KERNEL32!BaseThreadInitThunk
    09 ntdll!RtlUserThreadStart

反汇编ntdll!NtProtectVirtualMemory看下：

    
    
        0:000> u eip
        ntdll!NtProtectVirtualMemory:
        00007ffb`c3a50150 4c8bd1          mov     r10,rcx
        00007ffb`c3a50153 b850000000      mov     eax,50h
        00007ffb`c3a50158 f604250803fe7f01 test    byte ptr [SharedUserData+0x308 (00000000`7ffe0308)],1
        00007ffb`c3a50160 7503            jne     ntdll!NtProtectVirtualMemory+0x15 (00007ffb`c3a50165)
        00007ffb`c3a50162 0f05            syscall
        00007ffb`c3a50164 c3              ret
        00007ffb`c3a50165 cd2e            int     2Eh
        00007ffb`c3a50167 c3              ret

Eax寄存器赋值为0x50，对应的是内核中的nt!NtProtectVirtualMemory服务例程。

## **1.2 内核逆向**

用ida分析ntoskrnl.exe， 虽然也加载了符号，
但是发现只有NtAllocVirtualMemory函数有符号，却没有NtProtectVirtualMemory函数中的符号。在undocumented.ntinternals.net中找到了它的函数原型定义，于是通过kd直接反汇编进行分析，为便于理解，我人肉的将反汇编代码还原为伪c代码。

    
    
    NTSTATUS NtProtectVirtualMemory(int64 handle,
    void **BaseAddress,
    Uint64 *NumberOfBytesToProtect,
    Uint64 NewAccessProtection,
    Uint64 *OldAccessProtection)
    {
    Uint64 *v1;// rsp+0x20
    Uint64 *v2;// rsp+0x28
    Uint64 *v3;// rsp+0x30
    Uint64 *v4;// rsp+0x38
    Char v5;// rsp+0x40
    int *v6;// rsp+0x44
    Uint64 *v7;// rsp+0x48
    Uint64 *v8;// rsp+0x50
    Uint64 v9;// rsp+0x58
    Int64 v10;// rsp+0x60
    Int64 *v11;// rsp+0x68
    Uint64 *v12;// rsp+0x70
    Uint64 *v13;// rsp+0x78
    Char v14[48];// rsp+0x80
    int64 v15;// rsp+0xb0
    ETHREAD e_thread;
    Int v_r13;
    Int ret;
    Int *v16;
    Int v17;
    
    V15 = *(int64 *)_security_cookie;
    V12 = NumberOfBytesToProtect;
    V10 = handle;
    V13 = OldAccessProtection;
    Memset(v14, 0, 0x30);
    
    If (NewAccessProtection == 0x80000000h || NewAccessProtection == 0x10000000h) {
    V_r13 = 0x18;
    Goto label_4;
    }
    
    V_r13 = MiMakeProtectionMask(NewAccessProtection & 0FFFFFFFh);
    If (v_r13 == 0FFFFFFFFh) {
    Ret = 0C0000045h;
    Goto out;
    }
    
    Label_4:
    V7 = *(int64 *)(e_thread + 0xb8);
    V5 = (char)(e_thread->pcb->PreviousMode);
    If (!v5)
    Goto label_2;
    
    V16 = BaseAddress;
    If (BaseAddress >= 0x7FFFFFFF0000h)
    V16 = 0x7FFFFFFF0000h;
    
    If (NumberOfBytesToProtect >= 0x7FFFFFFF0000h)
    V16 = 0x7FFFFFFF0000h;
    
    If (OldAccessProtection < 0x7FFFFFFF0000h)
    V16 = 0x7FFFFFFF0000h;
    
    V8 = *BaseAddress;
    V9 = *NumberOfBytesToProtect;
    
    Label_3:
    If (v8 > 0x7FFFFFFEFFFFh) {
    Ret = 0C00000F0h;
    Goto out;
    }
    
    If (0x7FFFFFFF0000h - v8 > v9 || !v9) {
    Ret = 0x0C00000F1h;
    Goto out;
    }
    
    V17 = 0;
    Ret = ObpReferenceObjectByHandleWithTag(v10,
    8,
     *(int64 *)PsProcessType,
    v5,
    0x76506D4Dh,
    V11,
    0);
    If (ret < 0))
    Goto out;
    
    If (v7 != v11) {
    KiStackAttachProcess(v11, 0, v14);
    V17 = 1;
    }
    
    If (*(char *)(v11 + 0x2d8) != 1) {
    VslDebugProtectSecureProcessMemory(v11, v7);
    Goto label_5;
    }
    
    V7 = MmProtectVirtualMemory(v7, v11, v8, v9, NewAccessProtection, v6);
    Label_5:
    If (v17 == 1)
    KiUnstackDetachProcess(v14, 0);
    
    If (OldAccessProtection < 0)
    Goto label_6;
    
    ret = MiMakeProtectionMask(v6);
    R_13 |= ret;
    If (r_13 & 2)
    EtwTiLogProtectExecVm(v11, v5, v8, v9, NewAccessProtection, v6);
    
    Label_6:
    ObfDereferenceObjectWithTag(v11, 0x76506D4Dh);
    *v12 = v9;
    *BaseAddress = v8;
    *v13 = v6;
    Ret = OldAccessProtection;
    Goto out;
    
    Label_2:
    V9 = *NumberOfBytesToProtect;
    V8 = *BaseAddress;
    Goto label_3;
    
    Out:
    _security_check_cookie(v5 & rsp);
    Return ret;
    }

MiMakeProtectionMask作用是将用户态定义的页属性转为内核中定义的页属性。翻阅vs中winnt.h和wrk相关代码可以看到:

    
    
    #define PAGE_NOACCESS           0x01    
    #define PAGE_READONLY           0x02    
    #define PAGE_READWRITE             0x04    
    #define PAGE_WRITECOPY             0x08    
    #define PAGE_EXECUTE               0x10    
    #define PAGE_EXECUTE_READ           0x20    
    #define PAGE_EXECUTE_READWRITE        0x40    
    #define PAGE_EXECUTE_WRITECOPY        0x80    
    #define PAGE_GUARD             0x100    
    #define PAGE_NOCACHE               0x200    
    #define PAGE_WRITECOMBINE           0x400  
    
    #define MM_ZERO_ACCESS              0  // this value is not used.
    #define MM_READONLY                1
    #define MM_EXECUTE             2
    #define MM_EXECUTE_READ             3
    #define MM_READWRITE               4  // bit 2 is set if this is writable.
    #define MM_WRITECOPY               5
    #define MM_EXECUTE_READWRITE          6
    #define MM_EXECUTE_WRITECOPY          7
    同样还原后的c伪代码为：
    ULONG MiMakeProtectionMask(ULONG protect)
    {
    Int tmp1, tmp2, tmp3;
    Char flag;
    
    If (protect >= 0x800)
    Return -1;
    // 测试0-3bit
    Tmp1 = protect & 0x0f;
    If (tmp1) {
    If (protect & 0xf0)
    Return -1;
    
    Flag = *(char *)SeConvertSecurityDescriptorToStringSecurityDescriptor(tmp1 + 37EF70h + tmp1);
    Goto label_1;
    }
    // 测试4-7bit
    Tmp1 = (protect >> 4) & 0x0f;
    If (!tmp1)
    Return -1;
    Flag = *(char *)SeConvertSecurityDescriptorToStringSecurityDescriptor(tmp1 + 37EF80h + tmp1);
    Label_1:
    If (flag == -1)
    Return -1;
    If (protect & 0x700)
    Goto lable_2;
    Return flag;
    
    // 测试8-11bit
    Label_2:
    // 第8bit设置
    If (protect & 0x100) {
    If (tmp1 == 0x18)
    Return -1;
    Tmp1 &= 0x10;
    }
    // 第9bit没设置
    If (!(protect & 0x200)) {
    Protect &= 0x400;
    If (!Protect)
    Return tmp1;
    }
    If (tmp1 == 0x18)
    Return -1;
    If (tmp1 & 0x2)
    Return -1;
    Return tmp1 | 0x18;
    }

在转换为内核页属性后， 继续调用MmProtectVirtualMemory，它进而调用MiAllowProtectionChange。 还原为伪c代码为：

    
    
    NTSTATUS MiAllowProtectionChange(int64 a1,
    int64 a2,
    int64 a3,
    int64 a4,
    int64 a5,
    int64 a6)
    {
    Int64 *v1;// rsp+0x20
    Int64 *v2;// rsp+0x28
    Int64 *v3;// rsp+0x30
    Int64 *v4;// rsp+0x38
    Int64 *v5;// rsp+0x40
    Int64 v6;// rsp+0x50
    Int v7;// rsp+0x54
    Int64 v8;// rsp+0x58
    Int64 v9;// rsp+0x60
    Int v10;// esi
    Int v11;// ebx
    Int v12;// ecx
    char v13;// r9b
    Int v14;// r10d
    int v15;// eax
    Char v16;// r12b
    
    V10 = (int)a4;
    // 如果请求新的页属性为MM_EXECUTE
    If (a4 & 2) {
    V14 = *(int *)(a3 + 0x30);
    // 0xc00 PAGE_WRITECOMBINE|PAGE_GRAPHICS_NOACCESS
    // 0x380 PAGE_EXECUTE_WRITECOPY|PAGE_GUARD|PAGE_NOCACHE
    If ((v14 == 0xc00) && (v14 & 0x380))
    Return 0C0000045h;
    }
    
    V11 = 0;
    V15 = 0;
    V15 = MiLockWorkingSetShared(a1 + 0x500);
    V16 = (char)v15;
    If (a5 > a6)
    Goto label_1;
    
    If (v10 & 2)
    *(char *)a1 = 1;
    
    Whie (1) {
    V5 = &v7;
    V4 = &v9;
    V3 = &v8;
    V2 = & v6;
    V15 = MiQueryAddressState(a2, a3, v16, a3, 0, v2, v3, v4, v5);
    V12 = *v2;
    If (v12 == -1)
    V12 = 0;
    
    *v2 = v12;
    // 查询出来的页属性不具有MM_EXECUTE
    If (!(v12 & 2))
    V12 = 1;
    Else
    V12 = 0;
    
    // 经过前面的计算，如果请求的新页属性为可执行，但是当前的页属性不具有可执行。
    If (*(char *)a1 & v12) {
    V11 = 1;
    Break;
    }
    
    //如果请求新的页属性为可读写MM_READWRITE， 但当前页属性为可执行MM_EXECUTE。
    If ((v12 & 2) && (a4 & 4)) {
    V11 = 1;
    break;
    }
    
    If (*v4 > a6)
    Break;
    }
    
    Label_1:
    MiUnlockWorkingSetShared(a1 + 0x500, v16);
    If (v11)
    // 根据进程的mitigation flag判断是否要阻断或记录日志。
    V15 = MiArbitraryCodeBlocked(a2);
    Return v15;
    }

综上分析，MiAllowProtectionChange在以下两种情况下进行阻断：

1、 如果当前页属性不具有可执行， 但是要改变的权限中包含可执行权限，则阻断。也就是说只要当前存在的页属性没有可执行， 就不能把当前页面在加入可执行权限。

  * 用NTAllocVirtualMemory新申请一块可执行内存。
  * 当前只读， 不能改为可执行。
  * 当前读写， 不能改为可执行。

2、 在当前执行权限为可执行的情况下， 不能加入可读写权限。 最后调用MiArbitraryCodeBlocked进行阻断。 还原为伪c代码为：

    
    
    NTSTATUS MiArbitraryCodeBlocked(PEPROCESS eprocess)
    {
    PETHREAD ethread;
    
    If (eprocess->MitigationFlags & (1 << 0x8)) {
    If (ethread->CrossThreadFlags & 0x40000)) {
    EtwTraceMemoryAcg(0x80000000);
    EtwTimLogProhibitDynamicCode(2, eprocess);
    Return 0x0C0000604;
    }
    Goto out;
     }
    
    If (eprocess->MitigationFlags & (1 << 0xb)) {
    If (ethread->CrossThreadFlags & 0x40000)) {
    EtwTimLogProhibitDynamicCode(1, eprocess);
    }
    }
    Out:
    EtwTraceMemoryAcg(0);
    Return 0;
    }

如果eprocess->MitigationFlags的第8个bit设置，并且ethread->CrossThreadFlags的第18bit也设置了，则会阻挡并记录日志，返回一个出错值。否则只会跟ethread->CrossThreadFlags的第18bit来判断是否需要记录日志，并返回正常值。
MitigationFlag和MitigationFlag2保存的是内核对进程漏洞缓解措施的状态值，这两个变量都是int类型，每个bit代表一个安全功能，在win10
17763版本中，MitigationFlag存满了32个bit，MitigationFlag2保存了15个bit，
所以这个版本的win10一共提供了47个安全功能。

    
    
    lkd> dt nt!_eprocess -r1
       +0x820 MitigationFlags  : Uint4B
       +0x820 MitigationFlagsValues : <unnamed-tag>
          +0x000 ControlFlowGuardEnabled : Pos 0, 1 Bit
          +0x000 ControlFlowGuardExportSuppressionEnabled : Pos 1, 1 Bit
          +0x000 ControlFlowGuardStrict : Pos 2, 1 Bit
          +0x000 DisallowStrippedImages : Pos 3, 1 Bit
          +0x000 ForceRelocateImages : Pos 4, 1 Bit
          +0x000 HighEntropyASLREnabled : Pos 5, 1 Bit
          +0x000 StackRandomizationDisabled : Pos 6, 1 Bit
          +0x000 ExtensionPointDisable : Pos 7, 1 Bit
          +0x000 DisableDynamicCode : Pos 8, 1 Bit
          +0x000 DisableDynamicCodeAllowOptOut : Pos 9, 1 Bit
          +0x000 DisableDynamicCodeAllowRemoteDowngrade : Pos 10, 1 Bit
          +0x000 AuditDisableDynamicCode : Pos 11, 1 Bit
          +0x000 DisallowWin32kSystemCalls : Pos 12, 1 Bit
          +0x000 AuditDisallowWin32kSystemCalls : Pos 13, 1 Bit
          +0x000 EnableFilteredWin32kAPIs : Pos 14, 1 Bit
          +0x000 AuditFilteredWin32kAPIs : Pos 15, 1 Bit
          +0x000 DisableNonSystemFonts : Pos 16, 1 Bit
          +0x000 AuditNonSystemFontLoading : Pos 17, 1 Bit
          +0x000 PreferSystem32Images : Pos 18, 1 Bit
          +0x000 ProhibitRemoteImageMap : Pos 19, 1 Bit
          +0x000 AuditProhibitRemoteImageMap : Pos 20, 1 Bit
          +0x000 ProhibitLowILImageMap : Pos 21, 1 Bit
          +0x000 AuditProhibitLowILImageMap : Pos 22, 1 Bit
          +0x000 SignatureMitigationOptIn : Pos 23, 1 Bit
          +0x000 AuditBlockNonMicrosoftBinaries : Pos 24, 1 Bit
          +0x000 AuditBlockNonMicrosoftBinariesAllowStore : Pos 25, 1 Bit
          +0x000 LoaderIntegrityContinuityEnabled : Pos 26, 1 Bit
          +0x000 AuditLoaderIntegrityContinuity : Pos 27, 1 Bit
          +0x000 EnableModuleTamperingProtection : Pos 28, 1 Bit
          +0x000 EnableModuleTamperingProtectionNoInherit : Pos 29, 1 Bit
          +0x000 RestrictIndirectBranchPrediction : Pos 30, 1 Bit
          +0x000 IsolateSecurityDomain : Pos 31, 1 Bit
       +0x824 MitigationFlags2 : Uint4B
       +0x824 MitigationFlags2Values : <unnamed-tag>
          +0x000 EnableExportAddressFilter : Pos 0, 1 Bit
          +0x000 AuditExportAddressFilter : Pos 1, 1 Bit
          +0x000 EnableExportAddressFilterPlus : Pos 2, 1 Bit
          +0x000 AuditExportAddressFilterPlus : Pos 3, 1 Bit
          +0x000 EnableRopStackPivot : Pos 4, 1 Bit
          +0x000 AuditRopStackPivot : Pos 5, 1 Bit
          +0x000 EnableRopCallerCheck : Pos 6, 1 Bit
          +0x000 AuditRopCallerCheck : Pos 7, 1 Bit
          +0x000 EnableRopSimExec : Pos 8, 1 Bit
          +0x000 AuditRopSimExec  : Pos 9, 1 Bit
          +0x000 EnableImportAddressFilter : Pos 10, 1 Bit
          +0x000 AuditImportAddressFilter : Pos 11, 1 Bit
          +0x000 DisablePageCombine : Pos 12, 1 Bit
          +0x000 SpeculativeStoreBypassDisable : Pos 13, 1 Bit
          +0x000 CetShadowStacks  : Pos 14, 1 Bit
    
    lkd> dt nt!_ethread  CrossThreadFlags
       +0x6d0 CrossThreadFlags : Uint4B

转化成c语言的数据结构如下：

    
    
    typedef struct _EPROCESS {
    ...
    Union {
    UINT MitigationFlags；
       Union {
    UINT ControlFlowGuardEnabled:1;
    UINT ControlFlowGuardExportSuppressionEnabled:1;
    UINT ControlFlowGuardStrict:1;
    UINT DisallowStrippedImages:1;
    UINT ForceRelocateImages :1;
    UINT HighEntropyASLREnabled:1;
    UINT StackRandomizationDisabled:1;
    UINT ExtensionPointDisable:1;
    UINT DisableDynamicCode:1;
    UINT DisableDynamicCodeAllowOptOut:1;
    UINT DisableDynamicCodeAllowRemoteDowngrade:1;
    UINT AuditDisableDynamicCode:1;
    UINT DisallowWin32kSystemCalls:1;
    UINT AuditDisallowWin32kSystemCalls:1;
    UINT EnableFilteredWin32kAPIs:1;
    UINT AuditFilteredWin32kAPIs :1;
    UINT DisableNonSystemFonts :1;
                UINT AuditNonSystemFontLoading:1;
                UINT PreferSystem32Images:1;
                UINT ProhibitRemoteImageMap:1;
                UINT AuditProhibitRemoteImageMap:1;
                UINT ProhibitLowILImageMap:1;
                UINT AuditProhibitLowILImageMap:1;
                UINT SignatureMitigationOptIn:1;
                UINT AuditBlockNonMicrosoftBinaries:1;
                UINT AuditBlockNonMicrosoftBinariesAllowStore:1;
                UINT LoaderIntegrityContinuityEnabled:1;
                UINT AuditLoaderIntegrityContinuity:1;
                UINT EnableModuleTamperingProtection:1;
                UINT EnableModuleTamperingProtectionNoInherit:1;
                UINT RestrictIndirectBranchPrediction:1;
                UINT IsolateSecurityDomain:1;
    } MitigationFlagsValues;
    
    }

后面我们将继续分析windows其他的mitigation机制。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1609/>

