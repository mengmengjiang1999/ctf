## rdtsc

大部分虚拟机包括沙箱用的都存在一个问题，cpuid等一些会造成vmexit的东西, 被硬件加速了 不开虚拟机的时候
只花很少的时间，大于200个CPU周期左右  
一旦进了虚拟机  
会到大约20000个周期不等  
木马 外挂 可以通过判断CPU周期确定自己是不是在虚拟机里 导致沙箱不存活之类的  
如  
<https://github.com/huoji120/DuckSandboxDetect/blob/main/ConsoleApplication1/ConsoleApplication1.cpp#L25>  
因此我们要在进入虚拟化后,算一下退出所消耗的周期,然后在tsc_offset减去对应的值即可

## 不可信参数

host不能接受不可信参数,比如xsetbv如果给0会造成PG.  
可以通过try catch预防 但是很多manual map的虚拟机是没办法用try catch的,因此要么做idt shadow
要么老老实实按照xen的来检查惨

## idt/gdt shadow

host机不能跟guest机用同一个idt/gdt  
需要自己自定义异常处理  
异常处理可以支持嵌套异常处理  
这是简单的异常处理代码:

    
    
    uintptr_t idt::search_seh_jmp_rip(uintptr_t rip) { 
     const auto exception_directory = &nt_headers->_optional_header._data_directory[IMAGE_DIRECTORY_ENTRY_EXCEPTION];
     ....
    }
    void idt::seh_handler(_idt_stack_register_error_code* stack_reg) 
    {
        if (global::cpu_type == _cpu_type::amd)
        {
            svm::svm_context->vcpu[function::get_current_cpu_num()]->last_error_code = stack_reg->error_code;
        }
        else {
            //intel..
        }
        uintptr_t search_rip = stack_reg->rip;
        uintptr_t search_rsp = stack_reg->rsp;
        uintptr_t search_rbp = stack_reg->rbp;
        size_t frame = 0;
        DebugPrint("[hyperduck] search exception rip %p \n", search_rip);
        for (;;frame++)
        {
            if (search_rip < reinterpret_cast<uintptr_t>(MmSystemRangeStart) || search_rsp < reinterpret_cast<uintptr_t>(MmSystemRangeStart))
                break;
    
            if (!search_rip || !MmIsAddressValid((PVOID)search_rip) || !MmIsAddressValid((PVOID)search_rip)) {
                break;
            }
            search_rip = search_seh_jmp_rip(search_rip);
            /*
                fix me :
                Because the add value of RSP is not calculated through assembly, generally speaking, one or two layers of simple functions can be used, and complex functions are not very good. If you want to be accurate, you need to traverse the assembly like Microsoft, and encounter the increase of add RSP
                Refer to rtlvirtualunwind for details
                In addition, the recovery of registers and stacks is not completely restored
            */
            if (search_rip == 0) {
                search_rip = (uintptr_t)(*(uintptr_t*)search_rsp);
                search_rsp += 8;
            }
            else {
                break;
            }
        }
        if (search_rip == 0) {
            DebugPrint("[hyperduck] unhandle exception! %p \n", search_rip);
            function::bug_check();
        }
        DebugPrint("[hyperduck] handle exception jmp to %p frame: %d \n", search_rip, frame);
        stack_reg->rip = search_rip;
        stack_reg->rsp = search_rsp;
        stack_reg->rbp = search_rbp;
    }

这样你就可以把之前所说的不可信参数加一个检查

    
    
    __try
        {
            asm_xsetbv(xcr, xcr_value.QuadPart);
            //_xsetbv(xcr, xcr_value.QuadPart);
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
            inject_exception_gp_by_code(guest_context, guest_context->vcpu->last_error_code);
            return;
        }

另外也能预防类似于NMI异常导致的vmexit暴露的问题

## msr

对于AMD来说(intel也一样)  
有些MSR是不能改的  
比如amd64_efer 如果在虚拟机运行的时候改了会造成DF异常  
因此需要shadow这些MSR

    
    
    void svm_exit::svm_shadow_msr(ULARGE_INTEGER* fake_msr_value, bool is_read, uintptr_t origin_msr, _svm_guest_status* guest_context) {
        if (is_read) {
            if (fake_msr_value->QuadPart == NULL) {
                fake_msr_value->QuadPart = origin_msr;
            }
            guest_context->guest_register->Rax = fake_msr_value->LowPart;
            guest_context->guest_register->Rdx = fake_msr_value->HighPart;
        }
        else {
            fake_msr_value->LowPart = guest_context->guest_register->Rax & MAXUINT32;
            fake_msr_value->HighPart = guest_context->guest_register->Rdx & MAXUINT32;
        }
    }

这些MSR在svm中需要注意:  
amd64_vmcr、amd64_tsx、amd64_efer

## tsx

TSX指令会造成一个vmexit  
但是这个vmexit是没有具体的vmexit code的,导致虚拟机崩溃  
最好的办法是在CPUID部分给guest返回不支持RTM

    
    
    switch (guest_context->guest_register->Rax)
        {
        case cpuid_get_extended_feature:
            _bittestandreset((long*)&cpuid_reg.rcx, amd64_cpuid_tsx_support);
            break;

并且在TSX MSR上注入PG异常

## CR3

很多开源虚拟机,CR3是guest和host共享的

![](https://image.3001.net/images/20220619/1655624149_62aed1d5c52f96fc3404c.png!small)

导致可以通过写垃圾CR3后提交vmexit让host崩溃  
POC代码:

    
    
    dpc level:
    _writecr3(0x133337);
    cpuid; //<-此时你的垃圾玩具机就崩溃了

修复:  
host和guest要独立一份CR3

## TSS

TSS在windows上负责异常的时候拷贝栈.  
当异常发生并且执行被重定向到中断处理程序时,RSP中的地址不能被信任.因为有可能不正确.或者在权限转换的时候发生提权操作  
修复:  
拷贝TSS,修改host的gdt的tss为自己的.然后把几个比如NMI、de这些带stack的东西设置自己的堆栈就行

## xsetbv

xsetbv 光靠try
catch还是不太行.可能会发生”主机设置了后导致了异常,再try的时候来不及”的情况.所以要跟XEN/KVM一样在try前面再次检查字段有没有问题:

大概代码:

    
    
    bool valid_xcr0(uintptr_t xcr0)
    {
        /* FP must be unconditionally set. */
        if (!(xcr0 & X86_XCR0_FP))
            return false;
    
        /* YMM depends on SSE. */
        if ((xcr0 & X86_XCR0_YMM) && !(xcr0 & X86_XCR0_SSE))
            return false;
    
        if (xcr0 & (X86_XCR0_OPMASK | X86_XCR0_ZMM | X86_XCR0_HI_ZMM))
        {
            /* OPMASK, ZMM, and HI_ZMM require YMM. */
            if (!(xcr0 & X86_XCR0_YMM))
                return false;
    
            /* OPMASK, ZMM, and HI_ZMM must be the same. */
            if (~xcr0 & (X86_XCR0_OPMASK | X86_XCR0_ZMM | X86_XCR0_HI_ZMM))
                return false;
        }
    
        /* BNDREGS and BNDCSR must be the same. */
        if (!(xcr0 & X86_XCR0_BNDREGS) != !(xcr0 & X86_XCR0_BNDCSR))
            return false;
        return true;
    }
    ....
    
        UINT32 xcr = (UINT32)guest_status->guest_context->Rcx;
        ULARGE_INTEGER xcr_value;
        if (xcr != 0) {
            //不为0 注入GP异常
            inject_event(guest_status, ia32_invalid_opcode, ia32_hardware_exception, false, NULL);
            return;
        }
        xcr_value.u.LowPart = (UINT32)guest_status->guest_context->Rax;
        xcr_value.u.HighPart = (UINT32)guest_status->guest_context->Rdx;
    
        __cpuid_params_t cpuid_reg;
        _huoji_cpuidex((int*)&cpuid_reg, 7, 0);
    
        if ((xcr_value.LowPart & cpuid_reg.rax) != cpuid_reg.rax || (xcr_value.HighPart & cpuid_reg.rdx) != cpuid_reg.rdx) {
            //cpu不支持这个指令
            inject_event(guest_status, ia32_invalid_opcode, ia32_hardware_exception, false, NULL);
            return;
        }
    
        if (!valid_xcr0(xcr_value.QuadPart)) {
            //给了个无效值
            inject_event(guest_status, ia32_invalid_opcode, ia32_hardware_exception, false, NULL);
            return;
        }
    .....

