# 使用 Ptrace 拦截和模拟 Linux 系统调用

阅读量 **203979**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-28 17:00:21

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Chris Wellons，文章来源：nullprogram.com

原文地址：<http://nullprogram.com/blog/2018/06/23/>

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

ptrace(2)系统调用通常与调试有关。它是本地调试器监视类Unix系统上的调试器的主要机制。这也是实现strace系统调用跟踪的常用方法。使用ptrace，跟踪程序可以暂停跟踪程序、检查和设置寄存器和内存、监听系统调用，甚至拦截系统调用。

我说的拦截，指的是跟踪器可以更改系统调用参数，更改系统调用返回值，甚至阻止某些系统调用，跟踪器可以完全服务于系统调用本身。这很有意思，因为它还意味着跟踪器可以模拟操作系统。这是在没有来自任何内核的特殊帮助的情况下完成的。

问题是，一个进程一次只能有一个附加的跟踪器，因此不可能在使用GDB调试该进程的同时模拟一个操作系统。另一个问题是模拟的系统调用会有更高的开销。

在本文中，我将重点介绍x86-64上[Linux的Ptrace](http://man7.org/linux/man-pages/man2/ptrace.2.html)，并将利用几个特定于Linux的扩展。我还将省略错误检查，但是完整的源代码清单中将包含这些检查。

你可以在这里找到示例的代码：  
<https://github.com/skeeto/ptrace-examples>

## strace

在讨论真正有趣的内容之前，让我们先回顾一下strace的基本实现。它[不是DTrack](http://nullprogram.com/blog/2018/01/17/)，但是strace仍然是非常有用的。

Ptrace从来没有被标准化过。它的接口在不同的操作系统之间是相似的，特别是在其核心功能上，但是它在不同的系统中有微妙的不同。虽然特定的类型可能不同，但ptrace(2)原型通常类似于：

    
    
    long ptrace(int request, pid_t pid, void *addr, void *data);
    

pid是跟踪程序的进程ID。虽然跟踪器一次只能有一个跟踪器，但跟踪器可以连接到多个跟踪器。

request字段选择一个特定的Ptrace函数，就像ioctl(2)接口一样。对于strace，只需要两个：

  * PTRACE_TRACEMEE：这个进程将由其父进程跟踪。
  * PTRACE_SYSCALL：继续，但在下一个系统调用入口或出口处停止。
  * PTRACE_GETREGS：获取tracee的寄存器的副本。

另外两个字段addr和data作为所选Ptrace函数的泛型参数,它们经常被省略。在这种情况下，我传入0。

strace接口本质上是另一个命令的前缀。

    
    
    $ strace [strace options] program [arguments]
    

最简单的strace命令没有任何选项，因此第一件要做的事情，假设至少有一个参数fork(2)，然后exec(2)
argv尾部的tracee进程。但是在加载目标程序之前，新进程将通知内核它将被其父进程跟踪。跟踪程序将此Ptrace系统调用暂停。

    
    
    pid_t pid = fork();
    switch (pid) {
        case -1: /* error */
            FATAL("%s", strerror(errno));
        case 0:  /* child */
            ptrace(PTRACE_TRACEME, 0, 0, 0);
            execvp(argv[1], argv + 1);
            FATAL("%s", strerror(errno));
    }
    

父进程使用wait(2)等待子进程的PTRACE_TRACEME。当wait(2)返回时，子进程将被暂停。

    
    
    waitpid(pid, 0, 0);
    

在允许子进程继续之前，我们告诉系统tracee应该和父进程一起终止。真正的strace实现可能会设置其他选项，例如PTRACE_O_TRACEFORK。

    
    
    ptrace(PTRACE_SETOPTIONS, pid, 0, PTRACE_O_EXITKILL);
    

剩下的就是一个简单的的循环，它一次只能捕获一个系统调用。循环的主体有四个步骤：

  1. 等待进程进入下一个系统调用。
  2. 打印系统调用。
  3. 允许系统调用执行并等待返回。
  4. 打印系统调用返回值。

PTRACE_SYSCALL请求既用于等待下一个系统调用开始，也用于等待该系统调用退出。前面说过，需要wait(2)等待跟踪程序进入所需状态。

    
    
    ptrace(PTRACE_SYSCALL, pid, 0, 0);
    waitpid(pid, 0, 0);
    

当wait(2)返回时，进行系统调用的线程的寄存器中有系统调用号及其参数。但是，操作系统还没有为这个系统调用提供服务。这个细节很重要。

下一步是收集系统调用信息。在x86-64上，[系统调用号在rax中传递](http://nullprogram.com/blog/2015/05/15/)，参数(最多6)在rdi,
rsi, rdx, r10, r8, r9中传递。尽管不需要wait(2)，读取寄存器是另一个Ptrace调用。

    
    
    struct user_regs_struct regs;
    ptrace(PTRACE_GETREGS, pid, 0, &regs);
    long syscall = regs.orig_rax;
    
    fprintf(stderr, "%ld(%ld, %ld, %ld, %ld, %ld, %ld)",
            syscall,
            (long)regs.rdi, (long)regs.rsi, (long)regs.rdx,
            (long)regs.r10, (long)regs.r8,  (long)regs.r9);
    

出于[内部内核的目的](https://stackoverflow.com/a/6469069)，系统调用号存储在orig_rax而不是rax中。其他的系统调用参数都是直接的。

接下来是另一个PTRACE_SYSCALL和wait(2)，然后是另一个PTRACE_GETREGS来获取结果。结果存到rax中。

    
    
    ptrace(PTRACE_GETREGS, pid, 0, &regs);
    fprintf(stderr, " = %ldn", (long)regs.rax);
    

这个程序的输出非常粗糙。系统调用没有符号名称，每个参数都以数字形式打印出来，即使它是指向缓冲区的指针。一个更完整的字符串需要知道哪些参数是指针，并使用process_vm_readv(2)从tracee读取这些缓冲区，然后正确地打印它们。

但这为监听系统调用奠定了基础。

## 拦截系统调用

假设我们希望使用Ptrace来实现类似OpenBSD的[pledge(2)](https://man.openbsd.org/pledge.2)
，其中一个进程保证只使用一组受限的系统调用。这种思想是，许多程序通常有一个初始化阶段，它们需要大量的系统访问(打开文件、绑定socket等)。初始化之后，它们进入一个主循环，在这个循环中，它们处理输入，只需要一小部分系统调用。

在进入这个主循环之前，进程可以将自己限制在它所需要的几个操作中。如果程序存在缺陷，使得能够被[错误的输入](http://nullprogram.com/blog/2017/07/19/)所利用，则pledge将极大地限制该利用程序所能完成的操作。

使用相同的strace模型，而不是打印出所有系统调用，我们可以阻止某些系统调用，或者在tracee异常时终止它。要终止很容易：只需在跟踪器中调用exit(2)。因为它被配置为同时终止tracee，终止系统调用并允许子进程继续是有点棘手的。

难点在于一旦系统调用启动，就无法中止它。当跟踪器从系统调用入口的wait(2) 返回时，终止系统调用发生的唯一方法是终止tracee。

但是，我们不仅可以处理系统调用参数，还可以更改系统调用号本身，将其转换为不存在的系统调用。我们可以通过正常的随路信令返回一个EPERM错误。

    
    
    for (;;) {
        /* Enter next system call */
        ptrace(PTRACE_SYSCALL, pid, 0, 0);
        waitpid(pid, 0, 0);
    
        struct user_regs_struct regs;
        ptrace(PTRACE_GETREGS, pid, 0, &regs);
    
        /* Is this system call permitted? */
        int blocked = 0;
        if (is_syscall_blocked(regs.orig_rax)) {
            blocked = 1;
            regs.orig_rax = -1; // set to invalid syscall
            ptrace(PTRACE_SETREGS, pid, 0, &regs);
        }
    
        /* Run system call and stop on exit */
        ptrace(PTRACE_SYSCALL, pid, 0, 0);
        waitpid(pid, 0, 0);
    
        if (blocked) {
            /* errno = EPERM */
            regs.rax = -EPERM; // Operation not permitted
            ptrace(PTRACE_SETREGS, pid, 0, &regs);
        }
    }
    

这个简单的示例只检查系统调用的白名单或黑名单，也没有任何细微差别，比如允许打开文件(open(2))，只读但不能写，允许匿名内存映射，但不允许非匿名映射，等等。此外，tracee也无法动态删除权限。

trace3如何与tracer沟通？创建一个系统调用！

## 创建一个系统调用

对于我的新的类似pledge的系统调用，我将其命名为xpledge()，系统调用号10000，这是一个很大的数字，不太可能用于真正的系统调用。

    
    
    #define SYS_xpledge 10000
    

为了演示，我构建了一个简单的界面，这在实践中并不是很好。它与OpenBSD的pledge(2)没有什么共同之处，后者使用一个[字符串接口](https://www.tedunangst.com/flak/post/string-interfaces)。下面是整个接口和实现：

    
    
    #define _GNU_SOURCE
    #include <unistd.h>
    
    #define XPLEDGE_RDWR  (1 << 0)
    #define XPLEDGE_OPEN  (1 << 1)
    
    #define xpledge(arg) syscall(SYS_xpledge, arg)
    

如果参数传入得是0，则只允许几个基本的系统调用，包括用于分配内存的调用(例如brk(2)。PLEDGE_RDWR允许各种读写系统调用(read(2),
readv(2), pread(2), preadv(2)等)。PLEDGE_OPEN允许open(2)。

为了防止权限回滚，pledge()会阻塞自身，尽管这样也可以防止以后删除更多的权限。

在xpledge中，我只需要检查这个系统调用：

    
    
    /* Handle entrance */
    switch (regs.orig_rax) {
        case SYS_pledge:
            register_pledge(regs.rdi);
            break;
    }
    

操作系统将返回ENOSYS(未实现的函数)，因为这不是一个真正的系统调用。所以在退出的时候，我将它重写为success(0)。

    
    
    /* Handle exit */
    switch (regs.orig_rax) {
        case SYS_pledge:
            ptrace(PTRACE_POKEUSER, pid, RAX * 8, 0);
            break;
    }
    

我编写了一个测试程序，打开/dev/urandom进行读取，尝试pledge，然后再次尝试打开/dev/urandom，确认它可以读取原始的/dev/urandom文件描述符。在没有pledge跟踪器的情况下运行时，输出如下：

    
    
    $ ./example
    fread("/dev/urandom")[1] = 0xcd2508c7
    XPledging...
    XPledge failed: Function not implemented
    fread("/dev/urandom")[2] = 0x0be4a986
    fread("/dev/urandom")[1] = 0x03147604
    

进行无效的系统调用不会使程序崩溃。在跟踪器下运行时：

    
    
    $ ./xpledge ./example
    fread("/dev/urandom")[1] = 0xb2ac39c4
    XPledging...
    fopen("/dev/urandom")[2]: Operation not permitted
    fread("/dev/urandom")[1] = 0x2e1bd1c4
    

pledge成功了，但第二个fopen(3)没有，因为跟踪器的EPERM阻止了它。

这个概念可以更进一步，比如更改文件路径或返回假结果。跟踪程序可以有效更改它的跟踪对象，并在通过系统调用的任何路径的根目录中添加一些跟踪路径。它甚至可以欺骗进程，声称它是作为根用户运行的。事实上，这正是[Fakeroot
NG](https://fakeroot-ng.lingnu.com/index.php/Home_Page)程序的工作方式。

## 模拟系统

假设你不仅要拦截某些系统调用，而且要拦截所有系统调用。你有[一个在另一个操作系统上运行的二进制文件](http://nullprogram.com/blog/2017/11/30/)，因此它所做的系统调用都不能正常工作。

你可以只使用我到目前为止说过的方法来处理。跟踪程序总是将系统调用号替换为一个假的调用号，服务于系统调用本身。但这实在是太低效了。对于每个系统调用，这基本上需要三个上下文切换：一个在入口终止，一个运行系统调用，一个在退出时终止。

自2005年以来，Linux版本的PTrace对这种技术进行了改进：PTRACE_SYSEMU。每次系统调用只停止一次，在允许tracee继续之前，跟踪器要为该系统调用提供服务。

    
    
    for (;;) {
        ptrace(PTRACE_SYSEMU, pid, 0, 0);
        waitpid(pid, 0, 0);
    
        struct user_regs_struct regs;
        ptrace(PTRACE_GETREGS, pid, 0, &regs);
    
        switch (regs.orig_rax) {
            case OS_read:
                /* ... */
    
            case OS_write:
                /* ... */
    
            case OS_open:
                /* ... */
    
            case OS_exit:
                /* ... */
    
            /* ... and so on ... */
        }
    }
    

要从任何具有稳定(足够)系统调用ABI的系统运行相同体系结构的二进制文件，只需要这个PTRACE_SYSEMU跟踪器、一个加载器和二进制所需的任何系统库(或者只运行静态二进制文件)。

审核人：yiwang 编辑：少爷

本文翻译自nullprogram.com
[原文链接](http://nullprogram.com/blog/2018/06/23/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **秋真平** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/149409](/post/id/149409)

安全客 - 有思想的安全新媒体

本文转载自: [nullprogram.com](http://nullprogram.com/blog/2018/06/23/)

如若转载,请注明出处： <http://nullprogram.com/blog/2018/06/23/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [ptrace](/tag/ptrace)
  * [技术分析](/tag/技术分析)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) 秋真平

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

