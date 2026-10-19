> 近日，Qualys 安全团队发布安全公告称，在 Polkit 的 Pkexec
> 程序中发现了一个本地权限提升漏洞CVE-2021-4034。Qualys安全团队在其博客文章中完整介绍了 Polkit
> 漏洞的细节。笔者在这里将以导读的形式，为大家解读一下这篇Qualys安全团队关于 Polkit 漏洞的精彩分析，揭开这个漏洞的神秘面纱。

 **简介**
Polkit是一个应用程序级别的工具集，通过定义和审核权限规则，实现不同优先级进程间的通讯：控制决策集中在统一的框架之中，决定低优先级进程是否有权访问高优先级进程。Polkit在系统层级进行权限控制，提供了一个低优先级进程和高优先级进程进行通讯的系统。和
sudo 等程序不同，Polkit 并没有赋予进程完全的 root 权限，而是通过一个集中的策略系统进行更精细的授权。Polkit定义出一系列操作，例如运行
GParted, 并将用户按照群组或用户名进行划分，例如 wheel
群组用户。然后定义每个操作是否可以由某些用户执行，执行操作前是否需要一些额外的确认，例如通过输入密码确认用户是不是属于某个群组。由于Polkit的
Pkexec工具中存在一处本地权限提升漏洞，致使攻击者可以通过控制环境变量，从而诱导Pkexec执行任意代码。利用成功后，可导致非特权用户获得管理员权限。
**** **漏洞分析** Pkexec是一个用来允许授权用户以其他用户身份执行program的工具，其参数如下图：

![](https://image.3001.net/images/20220128/1643336898_61f354c2f0b4f6223d95a.png!small)

在Pkexec工具的 main() 函数中，首先会使用如下图代码处理所接收的命令行参数：

![](https://image.3001.net/images/20220128/1643336908_61f354cc104c6a87e819f.png!small)

Pkexec工具将判断传入的参数是否为绝对路径，如果给出非绝对路径，Pkexec工具也将尝试在 path 中定位program，具体的做法是在PATH
环境变量的目录中搜索要执行的program。具体的代码见下图红框处：

![](https://image.3001.net/images/20220128/1643336938_61f354eae93bba0bd3840.png!small)

如果命令行参数argc的数量为 0，这意味着如果传递给execve()的参数列表 argv为空，即 {NULL}，那么 argv[0]将为
NULL，是参数列表的终止符，这将导致：Pkexec代码中第 534 行，整数 n 设置为 1；

![](https://image.3001.net/images/20220128/1643336947_61f354f396fc3b1efc844.png!small)

第 610 行，从 argv[1]
越界读取指针路径；![](https://image.3001.net/images/20220128/1643336963_61f3550326c3a9277f7e1.png!small)第
639 行，指针 s 被越界写入argv[1]
；![](https://image.3001.net/images/20220128/1643336991_61f3551f54970ca6c47a5.png!small)
**但是从这个越界的 argv[1] 中读取和写入的到底是什么呢？** 要回答这个问题，我们需要知道的是：当execve()
一个新program时，kernel将我们的参数、环境变量字符串以及指针（argv 和 envp）复制到新program堆栈的末尾，如下图：

![](https://image.3001.net/images/20220128/1643337007_61f3552f670597e811148.png!small)

由于argv和envp 指针在内存中是连续的，如果 argc 为 0，那么越界argv[1] 实际上是
envp[0]，即为指向我们的第一个环境变量“value”的指针。最终导致：Pkexec代码中第610行，将要执行的程序的路径从argv[1]（即envp[0]）中越界读取，并指向“value”；

![](https://image.3001.net/images/20220128/1643337127_61f355a77fca1d39ff0b4.png!small)

由于“value”不是以斜线开头，因此进入 629 行的if分支，并在第 632 行将这个 “value”传递给
g_find_program_in_path()

![](https://image.3001.net/images/20220128/1643337141_61f355b5dc739d433ffac.png!small)

随后，g_find_program_in_path() 在PATH
环境变量目录中搜索一个名为“value”的可执行文件。如果找到这样的可执行文件，则将其完整路径返回给 pkexec的 main()
函数。最后，这个完整路径被越界写入 argv[1]（即 envp[0]），从而覆盖了我们的第一个环境变量，见下图红框处：

![](https://image.3001.net/images/20220128/1643337154_61f355c2cd22cd708692c.png!small)

所以准确的说：如果我们的 PATH
环境变量是“PATH=name”，并且如果目录“name”存在（在当前工作目录中）并且包含一个名为“value”的可执行文件，则写入一个指向字符串“name/value”的指针越界到
envp[0]；或者说：如果我们的 PATH 是“PATH=name=.”，并且目录是“name=.”
存在并包含一个名为“value”的可执行文件，然后将指向字符串“name=./value”的指针越界写入
envp[0]。换言之：这种越界写入允许我们将一个“不安全”的环境变量（例如，LD_PRELOAD）重新引入 pkexec
的环境。这些“不安全”变量通常在调用 main() 函数之前已经被ld.so从 SUID 程序的环境中删除。 **总结**

此次漏洞虽然需要在本地触发，但Polkit作为系统预装工具，影响众多 Linux
发行版，并且漏洞利用简单且稳定，可以很好的应用于“权限提升”这个攻击阶段中，因此应该得到重视。

笔者对漏洞进行分析后，从笔者的角度对此次Pkexec漏洞提出如下三个观点：

1、此次存在漏洞的Pkexec工具自身比较特殊，有SUID权限。利用有SUID权限的工具进行提权历史上已有案例。此类工具应该强化检查，防止高权限错误传递。2、在Unix的衍生系统BSD以及Windows系统中不会存在同类问题，因为这些OS永远不会出现argc=0的情况。3、此次漏洞在更早之前曾被发现（大约是2013年被发现），但一直认为是无关紧要的bug，直到近期才被发现利用方式，所以软件的bug和vul的边界需要得到研究人员的重视。

本文以导读的形式，为大家带来了Qualys安全团队关于 polkit 漏洞的精彩分析，希望读者可以对此漏洞有着更深入的了解与认识。

参考链接：https://blog.qualys.com/vulnerabilities-threat-research/2022/01/25/pwnkit-local-privilege-escalation-vulnerability-discovered-in-polkits-pkexec-cve-2021-4034https://blog.csdn.net/qq_42896627/article/details/107383011https://wiki.archlinux.org/title/Polkit_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)

