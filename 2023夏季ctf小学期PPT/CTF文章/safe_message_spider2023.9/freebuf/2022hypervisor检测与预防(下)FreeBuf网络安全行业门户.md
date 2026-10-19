copy paster们久等了  
书接上回,前情回顾.如果没有看过请专辑里面的上/中篇

### KiErrata671Present

这是微软新加的PG用于检测ept/npt的hook.具体实现原理请谷歌搜索或者百度搜索

任何大于1803的内核都有这个功能.而且目前测试是,虚拟机不会出现这个情况(可能不准确,因为只挂机过一天,这触发实在是没啥规律).物理机会出现一次随机PG蓝屏

唯一的解决方案是:接管CR寄存器读写.当有writecr0出现时,用zydis检查内存汇编.目标是否是KiErrata671Present:

    
    
    inc eax
    ret
    

如果是则立刻构将那个页面设置为不可执行.然后造一个shadow页并且重定向那个页面到shadow页.让其正常返回预期值.

### pending #DB

这个原理的核心是”mov
ss,XXX”导致的异常会推迟.按道理来说如果没有vmexit发生则会在vmexit指令那边执行延迟异常.但是如果有vmexit而且你的垃圾玩具机没有处理的话则会在vmexit指令的下面一个指令执行延迟异常.导致看起来有一个指令被跳过一样  
具体可见:  
https://howtohypervise.blogspot.com/2019/01/a-common-missight-in-most-hypervisors.html  
![image](https://image.3001.net/images/20220713/1657714535_62ceb76739ed25f327f21.gif!small)  
检测代码:

    
    
    .code
    asm_vf_pending_db proc
        mov r10,rcx
        mov qword ptr[r10],0
        pushfq
        mov ecx, ss
        or dword ptr [rsp], 0100h
        popfq
        mov ss, ecx
        cpuid
        mov qword ptr[r10],1
        nop
        ret
    asm_vf_pending_db endp
    end
    ....
    bool hv_check = true;
    __try {
        asm_vf_pending_db(hv_check);
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        ;
    }
    if (hv_check) {
        DebugPrint("[verification] detected hypervisor through pending #db \n");
    }
    else {
        DebugPrint("[verification] check pending #db success! \n");
    }
    

解决方案:  
在adjust rip的时候检查tf位 如果tf为1而且btf为0则注入#db异常

### 暴露的vmexit和stack、vmcb/vmcs

按道理来说.host机的所有相关设置guest都不能访问.  
但是你的stack、vmcb/vmcs和你的玩具机的vmexit都是暴露给guest的.guest完全可以直接修改你的设置的参数.从而hijack
host.  
因此在host和guest分离的基础上.我们需要修改pte让这些敏感内存重定向到一个空白页

    
    
    void svm::protect_hypervisor(_svm_vcpu_context *vcpu) {
        //被保护的页面不能低于4kb大小.否则会溢出.
        if (svm::svm_context->protect_blank_page == nullptr) {
            svm::svm_context->protect_blank_page =
                tools::allocate_contiguous_memory(page_size * 0x4);
        }
        NT_ASSERT(svm::svm_context->protect_blank_page);
        if (svm::svm_context->protect_blank_page == nullptr) {
            DebugPrint("[%s] low resources! \n", __FUNCTION__);
            return;
        }
        const auto blank_pa =
            tools::get_physical_address(svm::svm_context->protect_blank_page);
        npt::build_shadow_page(vcpu->npt.pml4_table,
                               tools::get_physical_address(vcpu->stack), blank_pa);
        npt::build_shadow_page(
            vcpu->npt.pml4_table,
            tools::get_physical_address(svm::svm_context->msr_bitmap), blank_pa);
        .....其他要保护的....
    }
    

上面代码不完整,并且有几个要思考修复的bug.这是作业.不要想着抄代码.

这是效果:  
![image](https://image.3001.net/images/20220713/1657714614_62ceb7b62ac16d88cd6d7.png!small)

