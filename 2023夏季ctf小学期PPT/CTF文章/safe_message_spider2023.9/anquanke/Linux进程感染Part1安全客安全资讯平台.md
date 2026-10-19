# Linux 进程感染：Part 1

阅读量 **240121**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-27 14:30:12

 **x**

##### 译文声明

本文是翻译文章，文章原作者 tarlogic，文章来源：tarlogic.com

原文地址：<https://www.tarlogic.com/en/blog/linux-process-infection-part-i/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t016d89e608624a3054.png)

## 前言

在红队需要执行的各种任务中有一项因其使用的技术而引人注目：在系统中植入APT（高级持续性威胁），并确保它的持久性。不幸的是，这种持久性机制大多依赖于通过一种或多种激活技术(例如shell脚本、别名、链接、系统启动脚本等)在不同位置保存可执行文件的副本，因此蓝队只需找到这些副本就能进行分析。

虽然安全人员迟早会发现到底发生了什么，但可以通过一些技术使得在受感染的计算机中难以(或者至少延迟)检测APT。在本文中，我们将详细介绍一种基于进程树而不是常规的基于文件系统存储的持久性机制。

## 前提条件

这种技术应用于x86-64
GNU/Linux，尽管理论上可以很容易地扩展到任何具有较为完整的调试API的操作系统。最起码的要求是：任何现代GCC版本都能进行这项工作。

## 使用其他进程的地址空间作为仓库

这种技术的思想是将正在运行的非特权进程的地址空间作为存储区域，方法是在其中注入两个线程：第一个线程将试图感染其他进程，而另一个线程将包含攻击载荷(在本例中，用于确保文件系统持久性)。如果文件被删除，它将通过别名还原。

这种技术受到机器正常运行时间的严格限制，因此它应该用于不会频繁重启的系统。在其他系统中，它可以被当作一种补充的持久性机制。

## 注入

显然最关键一步之一就是代码注入本身。由于不可能事先知道代码在受害者地址空间中的地址，所以代码应该是PIC(position-independent
code，与位置无关的代码)。这显然表明需要借助动态库，因为它们在实际应用时会按照预期出现在内存中。但存在一些缺点：

  * 注入的大部分信息将是元数据
  * 解析和加载库所需的代码，虽然不是过于复杂，但与攻击载荷的大小相比，也是不可忽略的。
  * 共享库使用常见文件格式，导致生成的文件易于分析。

理想情况下，注入应该尽可能小：几个代码页，或者再多一个用于数据。而这其中还可能包含链接脚本。不论如何，为了证明这个概念，我们将实现一个共享库。

另一个需要记住的限制是，目标进程不需要作为动态可执行文件加载(因此，C库可能不需要动态加载)。另外，在加载的共享库上手工解析符号是很麻烦的，因为依赖于ABI，而且几乎无法维护。这意味着需要手工重新实现许多标准C函数。

另外，注入需要依赖ptrace系统调用。如果进程没有足够的权限(或者管理员禁用了这个功能)，就无法使用这种技术。

最后还会遇到动态内存使用限制的问题。动态内存的使用涉及处理堆，而堆的内部结构没有标准。通常不会在程序的地址空间中保持较大的内存占用，应该尽可能少地使用动态内存来减少内存占用。

## 概念证明

概念证明如下：

  * 这个库将包含两个入口点。入口点的位置可以事先知道(因为它们位于从可执行文件开始的固定距离)，并且对应于注入线程主函数的开始处。
  * 注入线程将列出系统中所有正在运行的进程，查找可能受攻击的进程。
  * 将尝试对每个进程进行ptrace(PTRACE_SEIZE)，并读取内存，以便检测是否已被感染。
  * 为了准备目标地址空间，必须注入系统调用。这些系统调用必须分配必要的内存页来存储注入的代码。
  * 生成两个线程并继续执行调试的进程。

每一个阶段都需要进行一些仔细的准备，下面将详细介绍。

## 准备环境

为了让代码尽可能简洁，使用一个编译为共享库的小型C程序作为入口点。此外，为了在使用程序前进行测试，将提供另一个在库中运行特定符号的小型C程序。为了简化开发，还将包括一个包含所有构建规则的Makefile。

对于可注入库的入口点，将使用以下模板：

    
    
    void
    persist(void)
    {
      /* Implement me */
    }
    void
    propagate(void)
    {
      /* Implement me */
    }
    

执行入口点初始执行的程序将命名为“spawn.c”，如下所示：

    
    
    #include 
    #include 
    #include 
    int
    main(int argc, char *argv[])
    {
      void *handle;
      void (*entry)(void);
      if (argc != 3) {
        fprintf(stderr, "Usagen%s file symboln", argv[0]);
        exit(EXIT_FAILURE);
      }
      if ((handle = dlopen(argv[1], RTLD_NOW)) == NULL) {
        fprintf(stderr, "%s: failed to load %s: %sn", argv[0], argv[1], dlerror());
        exit(EXIT_FAILURE);
      }
      if ((entry = dlsym(handle, argv[2])) == NULL) {
        fprintf(stderr, "%s: symbol `%s' not found in %sn", argv[0], argv[2], argv[1]);
        exit(EXIT_FAILURE);
      }
      printf("Symbol `%s' found in %p. Jumping to function...n", argv[2], entry);
      (entry) ();
      printf("Function returned!n");
      dlclose(handle);
      return 0;
    }
    

最后，编译这两个程序的Makefile，如下所示：

    
    
    CC=gcc
    INF_CFLAGS=--shared -fPIE -fPIC -nostdlib
    all : injectable.so spawn
    injectable.so : injectable.c
            $(CC) $(INF_CFLAGS) injectable.c -o injectable.so
    spawn : spawn.c
            $(CC) spawn.c -o spawn -ldl
    

运行make命令编译所有内容：

    
    
    % make
    (…)
    % ./spawn injectable.so propagate
    Symbol `propagate' found in 0x7ffff76352ea. Jumping to function...
    Function returned!
    

## 系统调用

对于上面的Makefile，需要注意的是，injectable.so是通过-nostdlib编译的(这是必需的)，因此我们将不能访问高级C系统调用接口。为了突破这一限制，需要混合使用C和内联汇编，以便与操作系统进行交互。

通常情况下，x86-64
Linux系统调用是通过syscall指令执行的(而在较早的x86系统中，则使用0x80中断)。在任何情况下，基本思想都是一样的：寄存器使用系统调用参数填充，然后通过一些特殊指令调用系统。%rax的内容由系统调用函数代码初始化，其参数按%rdi、%rsi、%rdx、%r10、%r8和%r9的顺序传递。返回值存储在%rax中，错误用负返回值表示。因此，在汇编中使用write()系统调用的简单“hello
world”如下所示：

    
    
        movq $1, %rax           // Syscall code for write(): 1
        movq $1, %rdi           // Arg 1: File descriptor (stdout)
        leaq %rip(saludo), %rsi // Arg 2: Buffer address
        movq $11, %rdx          // Arg 3: size (11 bytes)
        syscall                 // All set, call the kernel
    […]
    saludo: .ascii “Hola mundon”
    

得益于GCC的内联汇编语法，在C中使用汇编语言是相当容易的，而且由于它的简洁性，它可以被简化成一句代码。GCC的write wrapper可以简化为：

    
    
    #include 
    #include 
    ssize_t
    write(int fd, const void *buffer, size_t size)
    {
      size_t result;
      asm volatile(“syscall” : “=a” (result) : “a” (__NR_write), “S” (fd), “D” (buffer), ”d” (size);
      return result;
    }
    

在“syscall”之后传递的值指定在执行汇编代码之前如何初始化寄存器。在这种情况下，%rax(specifier:“a”)被初始化为`__NR_write`(扩展到系统调用代码以进行写入的宏，如syscall.h中定义的那样)、带有buffer地址的%rdi(specifier:“D”)、%rsi(specifier:“S”)和包含字符串大小的%rsi(specifier:“S”)。返回值被收集回%rax(specifier:“=a”，等号表示“结果”是一个只写的值，编译器不需要担心它的初始值)。

由于字符串解析在许多程序中很常见，而且通常都需要这一步，编写strlen的实现(按照string.h中的原型)来度量字符串长度是很方便的：

    
    
    size_t
    strlen(const char *buffer)
    {
      size_t len = 0;
      while (*buffer++)
        ++len;
      return len;
    }
    

它允许定义以下宏：

    
    
    #define puts(string) write(1, string, strlen(string))
    

它提供了一种在标准输出中显示调试消息的简单方法：

    
    
    void
    persist(void)
    {
      puts("This is persist()n");
    }
    void
    propagate(void)
    {
      puts("This is propagate()n");
    }
    

运行后应该产生以下输出：

    
    
    % ./spawn injectable.so persist
    Symbol `persist' found in 0x7f3eb58403be. Jumping to function...
    This is persist()
    Function returned!
    % ./spawn injectable.so propagate
    Symbol `propagate' found in 0x7fb8874403db. Jumping to function...
    This is propagate()
    Function returned!
    

第一个困难解决，从现在开始，对于任何缺少的系统调用功能，都应该实现相应的C
wrapper，所需的库函数(如strlen)应该按照我们需要的相应的标准头原型来实现。

## 枚举过程

为了在其他进程中注入恶意代码，第一步是了解系统中可用的进程。有两种方法可以做到这一点：

  * 访问/proc并列出所有文件夹，或者
  * 检测所有系统PID，从PID 2到给定的PID_MAX

虽然第一种方法看起来是最快的，但它也是最复杂的，因为：

  * /proc可能没有安装。
  * Linux缺少处理文件夹的opendir/readdir系统调用。它实际上依赖于getdents，它返回一个需要手动处理的可变大小结构的buffer。
  * 文件名必须手动转换为整数，以便提取它们所引用的PID。因为我们无法访问库函数，所以这种转换特性也应该手动实现。

虽然第二种方法看起来比较慢，但在现代操作系统中几乎都能正常工作。在这种方法中，在PID范围内通过信号0多次调用Kill，如果PID存在且调用进程可以向其发送信号(这反过来与调用进程的权限有关)，则返回0，否则将返回错误代码。

现在唯一未知的是`PID_MAX`，它在每个系统不一定都是相同的。幸运的是，在绝大多数情况下，`PID_MAX`被设置为默认值(32768)。由于在没有发送信号的情况下，kill是非常快的，所以调用kill
33000次似乎是可行的。

使用这种技术，需要一个用于kill的wrapper。遍历2到32768之间的所有可能的PID(因为PID
1是为init保留的)，并为找到的每个进程打印一条消息：

    
    
    int
    kill(pid_t pid, int sig)
    {
      int result;
      asm volatile("syscall" : "=a" (result) : "a" (__NR_kill), "D" (pid), "S" (sig));
      return result;
    }
    

编写一个函数，打印十进制数字：

    
    
    void
    puti(unsigned int num)
    {
      unsigned int max = 1000000000;
      char c;
      unsigned int msd_found = 0;
    
      while (max > 0) {
        c = '0' + num / max;
        msd_found |= c != '0' || max == 1;
        if (msd_found)
          write(1, &c, 1);
        num %= max;
        max /= 10;
      }
    }
    

现在剩下的工作是修改propagate()，用来进行枚举：

    
    
    void
    propagate(void)
    {
      pid_t pid;
    
      for (pid = 2; pid < PID_MAX; ++pid) if (kill(pid, 0) >= 0) {
          puts("Process found: ");
          puti(pid);
          puts("n");
        }
    }
    

编译后，预期得到这样的结果：

    
    
    % ./spawn injectable.so propagate
    Process found: 1159
    Process found: 1160
    Process found: 1166
    Process found: 1167
    Process found: 1176
    Process found: 1324
    Process found: 1328
    Process found: 1352
    

对于常规的桌面GNU/Linux发行版来说，通常会发现超过100个用户进程。这相当于说有一百多个可能的感染目标。

## 尝试PTRACE_SEIZE

这种技术的主要缺点：由于访问限制(例如setuid进程)，无法对上面列举的一些进程进行调试。对每个已发现进程的ptrace调用(PTRACE_SEIZE)都可以用于标识哪些进程是可调试的。

虽然对于调试运行中的程序，首先想到的是使用`PTRACE_ATTACH`，但是这种技术有副作用：如果成功，它将停止调试，直到使用`PTRACE_CONT`恢复调试为止。这可能会影响目标进程(特别是当它对时间敏感时)，从而被用户发现。但是`PTRACE_SEIZE`(在Linux3.4中引入)并不会停止目标进程。

根据libc，ptrace是一个可变的函数，因此通过始终接受4个参数、填充参数或不根据请求的命令填充参数，可以很方便地简化wrapper：

    
    
    long
    ptrace4(int request, pid_t pid, void *addr, void *data)
    {
      long result;
      register void* r10 asm("r10") = data;
      asm volatile("syscall" : "=a" (result) : "a" (__NR_ptrace), "S" (pid), "D" (request), "d" (addr));
      return result;
    }
    

现在propagate函数如下：

    
    
    void
    propagate(void)
    {
      pid_t pid;
      int err;
    
      for (pid = 2; pid < PID_MAX; ++pid) if (kill(pid, 0) >= 0) {
          puts("Process found: ");
          puti(pid);
          puts(": ");
          if ((err = ptrace4(PTRACE_SEIZE, pid, NULL, NULL)) >= 0) {
            puts("seizable!n");
            ptrace4(PTRACE_DETACH, pid, NULL, NULL);
          } else {
            puts("but cannot be debugged <img draggable="false" class="emoji" alt="🙁" src="https://s.w.org/images/core/emoji/11/svg/1f641.svg"> [errno=");
            puti(-err);
            puts("]n");
          }
        }
    }
    

它将列出系统上所有可调试的进程。

## 结论

前面的测试让我们快速地了解了这种技术的可行性。到这一步，已经接近普通的调试器了，最大区别是我们的代码是自动运行的。在下一篇文章中，我们将介绍如何捕获调试器的系统来远程注入系统调用。这些远程系统调用将用于创建生成注入线程的代码和数据页。

本文翻译自tarlogic.com [原文链接](https://www.tarlogic.com/en/blog/linux-process-infection-part-i/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **yimeng** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168543](/post/id/168543)

安全客 - 有思想的安全新媒体

本文转载自: [tarlogic.com](https://www.tarlogic.com/en/blog/linux-process-infection-part-i/)

如若转载,请注明出处： <https://www.tarlogic.com/en/blog/linux-process-infection-part-i/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [系统安全](/tag/系统安全)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhimg.com/t016fefd8e565877ad5.png) yimeng

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

