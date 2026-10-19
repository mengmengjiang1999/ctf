## **一、前言**

Unix和类Unix操作系统提供的ptrace系统调用支持一个进程控制另一个进程，常被用于程序调试、分析和监测工具，例如gdb、strace等。通过ptrace可以查看和修改被控制进程的内部状态，因此渗透攻击在注入shellcode时也会使用ptrace。本文介绍一种Linux下使用ptrace隐藏注入shellcode的技术和防御方法。

##  **二、背景**

不同版本操作系统有各自实现ptrace系统调用的方式，本文只关注Linux环境，因此先简单说明Linux下ptrace系统调用的用法。首先定义控制进程（tracer）和被控制进程（tracee），tracer可以观察和控制tracee的执行流程，检查和修改tracee的内存和寄存器内容，一个tracee只能关联（attach）一个tracer，一个tracer可以关联多个tracee。需要注意的是Linux下一个tracee实际是一个线程，一个包含多个线程的进程中每个线程可以单独关联各自的tracer。所有ptrace功能通过一个接口函数调用，格式如下：

    
    
    long ptrace(enum __ptrace_request request, pid_t pid, void *addr, void *data);

第一个参数request包含调用的具体功能，后续三个参数的含义和第一个参数相关，不同功能需要设置相应的参数，详细定义可以查看操作系统文档（man
ptrace）。图1演示了tracer控制一个tracee的过程。

![图1
ptrace控制流程](https://image.3001.net/images/20221123/1669164092_637d6c3c42b6d91669dda.jpg!small)

图1 ptrace控制流程

1)
tracer调用PTRACE_ATTACH功能关联指定的tracee，向tracee发送SIGSTOP信号，并调用waitpid等待tracee状态改变；

2) 当tracee状态变成STOP，waitpid返回；

3) tracer调用PTRACE_SYSCALL功能让tracee进入单步执行状态，并调用waitpid等待tracee状态改变；

4) 重复步骤2)和步骤3)；

5) tracer调用PTRACE_DETACH功能让tracee恢复运行，并解除关联。

步骤3)中tracer可以检查和修改tracee的内存和寄存器内容，给渗透攻击注入shellcode提供了可能，接下来描述利用ptrace隐藏注入shellcode的技术细节。

##  **三、技术**

达成隐藏注入shellcode的目标需要解决三个问题：

1) shellcode存放在哪里？

2) 如何执行shellcode？

3) 如何不被轻易发现正在运行的shellcode？

解决第一个问题，需要了解Linux进程的内存结构，如图2所示。

![图2
Linux进程内存结构（x86，x86-64类似）](https://image.3001.net/images/20221123/1669164324_637d6d245b5d10dc20252.png!small)

图2 Linux进程内存结构（x86，x86-64类似）

执行cat /proc/<pid>/maps可以查看进程<pid>的内存结构，图3是top进程的内存结构。

![图3
top进程内存结构](https://image.3001.net/images/20221123/1669164387_637d6d631fd2b713788df.png!small)

图3 top进程内存结构

每行第二个字段表示该段内存的属性，包含'x'的具有执行权限。最容易写入shellcode的位置是Memory Mapping
Segment，可以申请匿名内存段，属性为rwxp，写入shellcode，伪代码如下：

    
    
    // 关联tracee
    ptrace(PTRACE_ATTACH, tracee_pid, NULL, NULL)
    waitpid(tracee_pid, 0, 0)
    // 修改系统调用为SYS_mmap并单步执行，执行完成以后恢复执行原有代码
    mem_addr = remote_mmap(tracee_pid, NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANON, -1, 0)
    // 写入shellcode到申请的内存段
    poke_text(tracee_pid, (size_t) mem_addr, shellcode, SHELL_LEN)

解决了第一个问题：shellcode存放在哪里，接着解决第二个问题：如何执行shellcode，这个问题比较简单，修改寄存器rip为mem_addr，再运行tracee即可执行shellcode，伪代码如下：

    
    
    // 读取tracee寄存器并备份
    ptrace(PTRACE_GETREGS, tracee_pid, NULL, &ampregs)
    memcpy(&old_regs, &ampregs, sizeof(struct user_regs_struct));
    // 修改rip为mem_addr（shellcode的地址）
    regs.rip = (u_int64_t) mem_addr;
    regs.rip += 2
    // 设置tracee寄存器
    ptrace(PTRACE_SETREGS, tracee_pid, NULL, &ampregs)
    // 执行shellcode，假设shellcode结尾执行了getpid系统调用
    for (;;) {
      ptrace(PTRACE_SYSCALL, tracee_pid, NULL, NULL)
      waitpid(tracee_pid, 0, 0)
      ptrace(PTRACE_GETREGS, tracee_pid, 0, &ampregs)
      if (regs.orig_rax == 39) {
        // 已执行getpid系统调用，恢复tracee状态
        ptrace(PTRACE_SETREGS, tracee_pid, NULL, &old_regs)
        break
      }
    }
    // 恢复tracee运行
    ptrace(PTRACE_DETACH, tracee_pid, NULL, NULL)

但是上述代码只是在tracee进程（线程）中执行了一次shellcode，还达不到隐藏注入的目的。一个简单的解决方法是在tracee所在进程中新建一个线程，在新建的线程中执行shellcode，并在shellcode中加入可以持续运行的循环。这时，通过监测进程状态难以发现注入的shellcode；如果tracee所在进程原来就包含多个线程，通过监测线程状态也难以准确判断是否被注入了shellcode；虽然检查tracee进程的内存段可以找到具有执行权限的匿名内存段，但是有些进程本来就存在具有执行权限的匿名内存段，仍然不能准确判断是否存在shellcode。综上所述，这种新建线程中执行shellcode的方式能够解决第三个问题：如何不被轻易发现正在运行的shellcode。伪代码如下：

    
    
    // 设置新建线程的栈
    stack_addr = remote_mmap(tracee_pid, NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0)
    stack_top = stack_addr + 4096
    poke_text(tracee_pid, (size_t)stack_addr, (char *)&mem_addr, sizeof(void *))
    // 修改系统调用为SYS_clone并单步执行，新建线程以后恢复执行原有代码
    thread_pid = remote_clone(pid, CLONE_PTRACE | CLONE_SIGHAND | CLONE_THREAD | CLONE_VM | CLONE_FS | CLONE_FILES, stack_top)
    // 在新建的线程中执行shellcode
    ptrace(PTRACE_GETREGS, thread_pid, NULL, &ampregs)
    regs.rip = (u_int64_t) mem_addr;
    ptrace(PTRACE_SETREGS, thread_pid, NULL, &ampregs)
    ptrace(PTRACE_DETACH, thread_pid, NULL, NULL)

##  **四、防御**

Linux内核使用图4描述的算法检查调用者（caller）相对目标（target）的ptrace访问权限。首先检查调用者和目标是否在同一个线程组，是则允许（allowed）使用ptrace功能；接着根据调用者和目标的用户编号（uid）和组编号（gid）是否一致、目标是否有可转存（dumpable）属性、调用方是否具有CAP_SYS_PTRACE权限，判定是否拒绝（denied）使用ptrace功能；然后调用Linux安全模块（LSM），例如：SELinux、Yama、Smack等，不同的安全模块有各自的检查判定规则；最后如果之前的检查没有拒绝使用ptrace功能，则允许使用。

![图4
Linux内核ptrace访问模式检查算法](https://image.3001.net/images/20221123/1669164583_637d6e271b054da03fbc8.jpg!small)

图4 Linux内核ptrace访问模式检查算法

除了在同一个线程组的情况，获得使用ptrace功能的许可必然经过Linux安全模块（LSM）的检查，因此可以配置LSM限制ptrace功能，以Yama为例：设置参数/proc/sys/kernel/yama/ptrace_scope（直接赋值或修改/etc/sysctl.conf中kernel.yama.ptrace_scope参数）可以控制ptrace的功能，参数值定义如下：

0：一个进程可以对它拥有权限的其它进程使用PTRACE_ATTACH功能。

1：一个进程只能对下属的子进程或线程使用PTRACE_ATTACH功能。

2：只有拥有CAP_SYS_PTRACE权限的进程能够对其它进程使用PTRACE_ATTACH功能。

3：任何进程均不能使用PTRACE_ATTACH或PTRACE_TRACEME功能，并且参数ptrace_scope取值不能改变。

可以根据应用需求，设置合适的/proc/sys/kernel/yama/ptrace_scope值，例如：生产环境设置成3禁用ptrace功能，开发环境设置成1用来调试程序。

此外，根据一个tracee只能关联一个tracer的规则，可以在程序开始使用PTRACE_TRACEME功能将当前线程变成tracee，之后其它进程不能再对其使用PTRACE_ATTACH功能。但是因为PTRACE_ATTACH作用于一个线程，所有相关线程都需要使用PTRACE_TRACEME才能避免所在进程被使用PTRACE_ATTACH功能。

还可以使用prctl系统调用关闭进程的转存功能，具体用法如下：

    
    
    prctl(PR_SET_DUMPABLE, SUID_DUMP_DISABLE, 0, 0, 0);

使用上述系统调用后，所在进程不能被其它进程（拥有CAP_SYS_PTRACE权限的进程除外）使用PTRACE_ATTACH功能。此方法虽然只适用调用者没有CAP_SYS_PTRACE权限的情况，但能够作用于正在运行的进程，具体做法如下：

1) 将调用prctl操作做成一个shellcode；

2) 使用ptrace将1)中生成的shellcode注入正在运行的目标进程并执行；

3) 恢复目标进程状态继续运行。

##  **五、总结**

ptrace系统调用为程序开发调试带来了便利，但是因其过于强大的功能成为一柄双刃剑，本文介绍的隐藏注入shellcode技术配合其它渗透攻击手段会对系统安全产生严重威胁，因此安全防护工作中需要注意防范。

 **注：本文中出现的代码在** **kali-rolling (x86_64)** **下测试成功。**

##  **参考资料：**

https://sploitfun.wordpress.com/2015/02/11/syscalls-used-by-malloc/ (内存结构图出处)

https://github.com/Srakai/Adun (新建线程思路来自于此)

https://www.kernel.org/doc/html/latest/admin-guide/LSM/Yama.html

