微软挺奇怪的,什么事都要管一腿。

总所周知 win 1809后hypervisor的一些功能比如msr hook(通过替换msr_lstar寄存器)的方案已经无了.怎么无的呢?除了kva
shadow的问题,还有如下几个问题:  
翻开微软的内核,有如下函数  
KiErrata361Present  
KiErrataSkx55Present  
KiErrata704Present  
…  
这些函数有如下特点:

> 1.名字莫名其妙
>
> 2.调用者也莫名其妙,比如KiErrata361Present在一个IDA分析都要半个小时的函数里面调用.
>
> 3.大部分都是微软检测虚拟机的函数

KiErrata704Present:

他长这样:

    
    
    asm_pg_KiErrata704Present proc
        mov     ecx, 0C0000084h
        rdmsr
        push    rdx
        push    rax
        and     eax, 0FFFFFEFFh
        wrmsr
        pushfq
        or      qword ptr[rsp], 100h
        popfq
        syscall                 ; Low latency system call
        mov     r10, rcx
        mov     ecx, 0C0000084h
        pop     rax
        pop     rdx
        wrmsr
        mov     rax, r10
        ret
    asm_pg_KiErrata704Present endp

让我们简单的说一下,这个函数首先保存FMASK的值，然后设置MSR值，以便SYSCALL操作不会修改TF.然后修改TF位.让下一步指令单步执行(#DB异常),DB异常后果就是如果你hook了lstar,断点就打在了你的kisystemcall64上了.你的位置会被直接暴露.然后就是蓝屏(蓝屏代码在系统的DB异常处理函数里)  
解决方案也很简单,设置DB异常退出,发现RIP ==
我的kisystemcall64直接TF设置为0然后转到系统的kisystemcall64就行,代码如下:

    
    
    if (interruption_type == ia32_hardware_exception && guest_status->rip == (uintptr_t)fake_kisystemcall64) {
                /*
                    KiErrataSkx55Present
                */
                DebugPrint("KiErrataSkx55Present Detected \n");
                guest_status->rip = _huoji_readmsr(ia32_lstar);
                guest_status->eflags.Fields.TF = 0;
                _huoji_vmx_vmwrite(guest_rip, guest_status->rip);
                return;
                //return adjust_rip(guest_status);
            }

但是这没完,继续看 KiErrata361Present:  
他长这样:

    
    
    asm_pg_KiErrata361Present proc
        mov ax,ss
        pushfq
        or qword ptr[rsp],100h
        popfq
        mov ss,ax
        db 0f1h ;icebp
        pushfq
        and qword ptr[rsp],0FFFFFEFFh
        popfq
        ret
    asm_pg_KiErrata361Present endp

简单说明一下,icebp这个指令是intel的一个奇葩,他在intel是会走DB异常的,而且会要求CPU优先处理他的异常(因为他的type是ia32_prisw_exception,比普通的DB异常高一级).但是如果他跟mov
ss结合在一起呢?

mov ss会产生一个异常，但是这个异常会在下一个指令执行的时候再抛出.因此 他首先mov ss了,这样下一个指令才会执行异常, 到icebp的时候,
mov ss造成的异常就应该被抛出了。但是同时icebp也会造成一个异常，而且异常优先级哎比mov
ss的高,你说巧不巧.这样CPU就会处理icebp的异常而不处理mov ss的异常，但是mov
ss的异常是必须要求dr6的single_instruction
bit位(也就叫做DR6.BS位)为1的,要不然就炸。很遗憾的是icebp的异常他不会设置这个bs位,导致直接炸虚拟机.很多时候虚拟机在2004跑起来了结果一阵子就虚拟机guest机异常了就是这个毛病。请注意,icebp指令在amd是不起作用的，因为amd有单独的退出事件。也就是说amd完全不用管icebp指令带来的问题。amd
yes  
解决方案就是看到有TF设置的直接给dr6.bs设置为1就行,代码如下:

    
    
    if (interruption_type == ia32_prisw_exception) {
                /*
                    KiErrata361Present
                */
                _debug_dr6 dr6_register = { static_cast<ULONG32>(guest_status->guest_context->Dr6) };
                DebugPrint("KiErrata361Present Detected Rip: %p tf %d dr6 %d \n", guest_status->rip, guest_status->eflags.Fields.TF, dr6_register.single_instruction);
                if (guest_status->eflags.Fields.TF) {
                    DebugPrint("KiErrata361Present guest_status->eflags.Fields.TF \n");
                    //guest_status->guest_context->Dr6 = (1UL << 6); ////BS位置1 
                    dr6_register.single_instruction = 1;
                    guest_status->guest_context->Dr6 = dr6_register.flags;
                    //guest_status->eflags.Fields.TF = 0;
                    inject_event(guest_status, ia32_debug_exception, interruption_type, false, NULL, NULL);
                    return;
                }
            }

KiErrataSkx55Present:

代码如下:

    
    
    asm_pg_KiErrataSkx55Present proc
        mov     ss, word ptr [rcx]
        syscall
        mov     rax, rcx
        ret
    asm_pg_KiErrataSkx55Present endp

这个跟CVE-2018-8897大同小异,如前面所说,mov
ss造成的异常会在syscall的地方执行,syscall会跑到你的kisystemcall64的地址,解决方法也一样,发现有异常在你的kisystemcall64上TF位置0改RIP到原版本的lstar上即可.不再做阐述

