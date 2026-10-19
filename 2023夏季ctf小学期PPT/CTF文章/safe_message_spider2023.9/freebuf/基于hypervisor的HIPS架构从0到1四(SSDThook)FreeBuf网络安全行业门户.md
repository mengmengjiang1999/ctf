## 前言

还记我们系列的标题吗? HIPS,作为系统监控,我们需要监控所有的syscall调用。这个部分会由hypervisor完成.  
ssdt hook是一个古老古老的东西了,还记得我以前入门就是很多人把ssdt hook看做是核心机密,现在已经烂大街了.我们的ssdt
hook不同于传统的"内联hook",我们准确的说叫做msr hook.回忆一下amd64里面syscall的方式,看看AMD手册的介绍:  
在AMD64体系下，为了解决之前int调用方式的不足，从而推出了syscall指令作为进入内核入口的指令，syscall在AMD64体系下调用的方式  
![image](https://image.3001.net/images/20210525/1621952318_60ad073e02483544a9e30.jpg!small)可以看到，最终RIP的值会等与MSR_LSTAR相等，而在微软体系里，MSR_LSTAR存放着kisystemcall64的函数地址  
因此,我们需要hook这个msr_star

## 目标

我们的目标很明确:

1 修改lstar地址,指向我们的fake_kisystemcall64

2 自己模拟微软的kisystemcall64过程

3 跳转到自己的ssdt function

让我们一步一步的来

## 修改lstar地址,指向我们的fake_kisystemcall64

svm里面,直接在初始化vmcb区域中修改lstar地址即可,截图如下:  
![image](https://image.3001.net/images/20210525/1621952339_60ad075381a7cd8aca5e5.jpg!small)而VT有两种方法,一种是修改vmentry和vmexit结构里面的lstar,好处是在进入VT和退出VT的时候会自动设置lstar值,第二种是进入虚拟化后再修改.我们走第二种方式:  
在进入虚拟化后,我们vmcall一个我们自己约定的vmcall number  
![image](https://image.3001.net/images/20210525/1621952369_60ad0771b19e131fb879d.jpg!small)然后在我们的vmcall
handler中,检测到如果有vmcall进来,就修改lstar的值:  
![image](https://image.3001.net/images/20210525/1621952384_60ad078094755b582f692.jpg!small)

## 模拟微软的kisystemcall64过程

这部分我已经在之前的  
[[2020]模拟整个kisystemCall64所需要的东西(win7-win10
1909)](https://key08.com/index.php/2020/05/24/718.html
"\[2020\]模拟整个kisystemCall64所需要的东西\(win7-win10 1909\)")  
已经提到了,这里放一个我已经改好的代码,支持win7-win2004 x64的系统,自己已经测试过了:

    
    
    extern g_orig_system_call:dq
    extern g_hook_enable:DB
    extern g_arg_tble:DB
    extern g_hook_table:DQ
    extern g_KiServiceCopyEndPtr:DQ
    extern g_CountNumCheckPtr:DQ
    extern g_KeServiceDescriptorTable:DQ
    extern g_KiSystemServiceRepeatPtr:DQ
    extern g_KiSaveDebugRegisterState:DQ
    extern g_KiUmsCallEntry:DQ
    extern g_is_win7:DQ
    MAX_SYSCALL_INDEX = 1000h
    USERMD_STACK_GS = 10h
    KERNEL_STACK_GS = 1A8h
    .code
    
    fake_kisystemcall64 proc
        swapgs
        ;int         3
        mov         gs:[USERMD_STACK_GS], rsp
        cmp         rax, MAX_SYSCALL_INDEX
        jge         KiSystemCall64
        lea         rsp, offset g_hook_enable
        cmp         byte ptr [rsp + rax], 0
        jne         KiSystemCall64_Emulate
    fake_kisystemcall64 endp
    
    KiSystemCall64 PROC
    	mov         rsp, gs:[USERMD_STACK_GS]
    	swapgs
    	jmp         [g_orig_system_call]			
    KiSystemCall64 ENDP
    
    KiSystemCall64_Emulate PROC
    
        mov         rsp, gs:[KERNEL_STACK_GS]   ; set kernel stack pointer
        push        2Bh                         ; push dummy SS selector
        push        qword ptr gs:[10h]          ; push user stack pointer
        push        r11                         ; push previous EFLAGS
        push        33h                         ; push dummy 64-bit CS selector
        push        rcx                         ; push return address
        mov         rcx, r10                    ; set first argument value
    
        sub         rsp, 8h                     ; allocate dummy error code
        push        rbp                         ; save standard register
        sub         rsp, 158h                   ; allocate fixed frame
        lea         rbp, [rsp+80h]              ; set frame pointer
        mov         [rbp+0C0h], rbx             ; save nonvolatile registers
        mov         [rbp+0C8h], rdi             ;
        mov         [rbp+0D0h], rsi             ;
        mov         byte ptr [rbp-55h], 2h      ; set service active
        mov         rbx, gs:[188h]              ; get current thread address
        prefetchw   byte ptr [rbx+90h]          ; prefetch with write intent
        stmxcsr     dword ptr [rbp-54h]         ; save current MXCSR
        ldmxcsr     dword ptr gs:[180h]         ; set default MXCSR
        cmp         byte ptr [rbx+3], 0         ; test if debug enabled
        mov         word ptr [rbp+80h], 0       ; assume debug not enabled
        jz          KiSS05                      ; if z, debug not enabled
        mov         [rbp-50h], rax              ; save service argument registers
        mov         [rbp-48h], rcx              ;
        mov         [rbp-40h], rdx              ;
        mov         [rbp-38h], r8               ;
        mov         [rbp-30h], r9               ;
        je          a2
       	call        [g_KiSaveDebugRegisterState]
        align       10h
        a2:
        test        byte ptr [rbx+3],80h 
    	je          a3			
    	mov         ecx,0C0000102h
    	rdmsr
    	shl         rdx,20h
    	or          rax,rdx
    a3:
    	cmp         qword ptr [rbx+0B8h],rax
    	je          B0
    	cmp         qword ptr [rbx+1B0h],rax
    	je          B0
    	mov         rdx,qword ptr [rbx+1B8h]
    	bts         dword ptr [rbx+4Ch],0Bh
    	dec         word ptr [rbx+1C"freebug你出bug了这个不是某Cfour敏感词"4h]
    	mov         qword ptr [rdx+80h],rax
    	sti
    	call        [g_KiUmsCallEntry]
    	jmp         FA0
    B0:
    	test        byte ptr [rbx+3],40h
    	je          FA0
    	lock        bts dword ptr [rbx+100h],8
    FA0:
    	mov         rax,qword ptr [rbp-50h]
    	mov         rcx,qword ptr [rbp-48h]
    	mov         rdx,qword ptr [rbp-40h]
    	mov         r8,qword ptr [rbp-38h]
    	mov         r9,qword ptr [rbp-30h]
    	xchg        ax,ax
    KiSS05:
    	sti
        cmp         byte ptr [g_is_win7], 0
        jne         NO_WIN7;
        mov         [rbx+88h], rcx
        mov         [rbx+80h], eax
        jmp         KiSystemServiceStart_Emulate
        NO_WIN7:
    	mov         qword ptr [rbx+1E0h],rcx
    	mov         dword ptr [rbx+1F8h],eax
    
    KiSystemCall64_Emulate ENDP
    
    KiSystemServiceStart_Emulate PROC
        mov         [rbx+90h], rsp
        mov         edi, eax
        shr         edi, 7
        and         edi, 20h
        and         eax, 0FFFh
    KiSystemServiceStart_Emulate ENDP
    
    KiSystemServiceRepeat_Emulate PROC
        ; RAX = [IN ] syscall index
        ; RAX = [OUT] number of parameters
        ; R10 = [OUT] function address
        ; R11 = [I/O] trashed
     
        lea         r11, offset g_hook_table
        mov         r10, qword ptr [r11 + rax * 8h]
        lea         r11, offset g_arg_tble
        movzx       rax, byte ptr [r11 + rax]   ; RAX = paramter count
        jmp         [g_KiServiceCopyEndPtr] ;bug  not check paramter count and jmp
    KiSystemServiceRepeat_Emulate ENDP
    
    end
    

## 跳转到自己的ssdt function

你可以看到,我已经定义了一个g_hook_table的东西,这个东西放着我们要hook的ssdt function id 和
我们的hook地址,这里不再做描:

    
    
    CHAR g_hook_enable[MAX_SYSCALL_INDEX];
    CHAR g_arg_tble[MAX_SYSCALL_INDEX];
    PVOID g_hook_table[MAX_SYSCALL_INDEX];
    .....
    NTSTATUS set_hook_function(IN ULONG index, IN PVOID hookPtr)
    {
    	NTSTATUS status = STATUS_SUCCESS;
    	if (index > MAX_SYSCALL_INDEX || hookPtr == NULL)
    	{
    		DebugPrint("\n[DebugMessage] STATUS_INVALID_PARAMETER!\n");
    		return STATUS_INVALID_PARAMETER;
    	}
    	KIRQL irql = KeGetCurrentIrql();
    	if (irql < DISPATCH_LEVEL)
    		irql = KeRaiseIrqlToDpcLevel();
    	LONG argumentsCount = (g_SSDT->pServiceTable[index] & 0xF) << 3;
    	InterlockedExchange8(&g_arg_tble[index], (CHAR)argumentsCount);
    	InterlockedExchange64((PLONG64)&g_hook_table[index], (LONG64)hookPtr);
    	InterlockedExchange8(&g_hook_enable[index], TRUE);
    
    	if (KeGetCurrentIrql() > irql)
    		KeLowerIrql(irql);
    
    	return status;
    }
    

至此,我们就可以随意hook函数了.

    
    
    NTSTATUS init_ssdt_hook()
    {
    	//__debugbreak();
    	DebugPrint("\n[DebugMessage] initHooks!\n");
    	NTSTATUS status = STATUS_SUCCESS;
    	if (!NT_SUCCESS(set_hook_function(g_iNtCreateFile, HookZwCreateFile))) {
    		status = STATUS_UNSUCCESSFUL;
    		goto exit;
    	}
    	if (!NT_SUCCESS(set_hook_function(g_iNtProtectVirtualMemory, HookZwProtectVirtualMemory)))
    	{
    		status = STATUS_UNSUCCESSFUL;
    		goto exit;
    	}
    	DebugPrint("\n[DebugMessage] HOOK SSDT FUNCTION SUCCESS :) !\n");
    exit:
    	return status;
    }
    

hook示例:

    
    
    NTSTATUS HookZwProtectVirtualMemory(HANDLE ProcessHandle, PVOID* BaseAddress, PSIZE_T RegionSize, ULONG NewProtect, PULONG OldProtect) {
    	if (KeGetCurrentIrql() != PASSIVE_LEVEL)
    		return STATUS_UNSUCCESSFUL;
    	
    	NTSTATUS return_status = pfn_NtProtectVirtualMemory(ProcessHandle, BaseAddress, RegionSize, NewProtect, OldProtect);
    	....
    	做一些莫名其妙的代码
    	.....
    	return return_status;
    	
    }
    

## 解决PG检测问题

记得在msr exit里面欺骗PG,原理很简单,做一层shadow就行.不再叙述,show the code

    
    
    void vt_shadow_msr(ULARGE_INTEGER* fake_msr_value, bool is_read, uintptr_t origin_msr, _guest_status* guest_context) {
    	if (is_read) {
    		if (fake_msr_value->QuadPart == NULL) {
    			fake_msr_value->QuadPart = origin_msr;
    		}
    		guest_context->guest_context->Rax = fake_msr_value->LowPart;
    		guest_context->guest_context->Rdx = fake_msr_value->HighPart;
    	}
    	else {
    		fake_msr_value->LowPart = guest_context->guest_context->Rax & MAXUINT32;
    		fake_msr_value->HighPart = guest_context->guest_context->Rdx & MAXUINT32;
    	}
    }
    ....
    msr exit handler:
    if (msr_id == ia32_lstar) {
    		vt_shadow_msr(&guest_status->fake_lstar_msr_value, access_type, g_orig_system_call, guest_status);
    	}
    

此外 windows 1809以上要注意PG的几处检测,我也已经总结好了:  
[微软如何检测到hypervisor以及如何预防](https://www.freebuf.com/articles/endpoint/273489.html
"微软如何检测到hypervisor以及如何预防")

## 关闭kva shadow

kva
shaodw创造了两个不同的页表,导致如果不做处理的情况下会炸系统.在1809之前可以用MmCreateShadowMapping映射自己的kisystemcall64到shadow
page,但在这之后微软他不给了,国外的@Daax 作者提供了一个efer hook的方法:  
https://revers.engineering/syscall-hooking-via-extended-feature-enable-register-efer/  
**(注意本人也尝试过,但是AMD的syscall的gate有问题,没有成功,这里感谢几个360的大佬,虽然最终没有解决方案但是还是跟我一起浪费时间研究了很久)**于是最简单的方法是关掉kva
shadow,所幸微软提供了一套关闭和检测kva shadow是否打开的方法:  
kva shadow是否打开:

    
    
    #define SystemKernelVaShadowInformation 196ull
    bool Tools::check_kva_shadow_enable() {
    	SYSTEM_KERNEL_VA_SHADOW_INFORMATION kva_info = { 0 };
    	NTSTATUS nt_result = ZwQuerySystemInformation((SYSTEM_INFORMATION_CLASS)SystemKernelVaShadowInformation, &kva_info, sizeof(kva_info), 0ull);
    	bool result = false;
    	if (NT_SUCCESS(nt_result)) {
    		result = kva_info.KvaShadowFlags.KvaShadowEnabled;
    	}
    	DebugPrint("check_kva_shadow_enable: %d \n", result);
    	return result;
    }
    

关闭kva shadow:

    
    
    wchar_t regedit_key[] = L"\\Registry\\Machine\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management";
    void Tools::disable_kva_shadow() {
    	uintptr_t value = 3;
    	CreateValueKey(regedit_key, L"FeatureSettingsOverride", REG_DWORD, &value, sizeof(DWORD));
    	CreateValueKey(regedit_key, L"FeatureSettingsOverrideMask", REG_DWORD, &value, sizeof(DWORD));
    }
    

调用即可:

    
    
    int cpu_type = get_cpu_type();
    	if (Tools::check_kva_shadow_enable()) {
    		disable_kva_shadow();
    		DebugPrint("[DebugMessage] KVA shadow enable! need restart computle \n");
    		return STATUS_HV_OPERATION_DENIED;
    	}
    

## 结语

本hypervisor入门系列也就完结的差不多了,你可以看到在这篇文章没有多少的文字,而是很多代码,因为相信如果你是从1看到这的,已经养成了看代码而不是在看文字的习惯了.写hypervisor目的并不是做出什么出色的产品,而是在于能学习很多系统底层的知识.作者在学hypervisor的时候遇到了很多困难但是没有什么办法解决,全靠网上仅有的开源的几个代码学习,因此才萌生写一个入门的文章.希望能帮助到后人学习.  
至于接下来的嵌套虚拟化，去虚拟化之类的，就是从1到100的技术了.作者不会继续再这系列文章更新此类教程.

