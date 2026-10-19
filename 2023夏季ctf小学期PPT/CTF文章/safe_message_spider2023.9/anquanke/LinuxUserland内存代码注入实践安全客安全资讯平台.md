# Linux Userland内存代码注入实践

阅读量 **308861**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-19 14:30:43

 **x**

##### 译文声明

本文是翻译文章，文章原作者 sektor7，文章来源：blog.sektor7.net

原文地址：<https://blog.sektor7.net/#!res/2018/pure-in-memory-linux.md>

译文仅供参考，具体内容表达以及含义原文为准。

## 一、前言

突破目标环境后，后续常见的攻击活动包括踩点、信息收集以及权限提升。当目标系统默认情况下没有提供所需工具，或者攻击者需要加快后续侦查行动时，攻击者可能就需要其他功能。

在大多数情况下，攻击者会将专用工具上传到目标系统中运行。这种方法最大的问题是磁盘上会留下攻击痕迹，如果被检测到，防御方可能会获取其他信息，从而危及整个攻击活动。

在最近几年，已经有许多研究人员分析过如何在不落盘的情况下，将代码注入Windows操作系统中（参考[[1]](https://github.com/fdiskyou/Zines/blob/master/29a/29a-6.zip),
[[2]](http://www.hick.org/code/skape/papers/remote-library-injection.pdf),
[[3]](https://www.dc414.org/wp-content/uploads/2011/01/242.pdf),
[[4]](https://www.joachim-bauch.de/tutorials/loading-a-dll-from-memory/),
[[5]](https://clymb3r.wordpress.com/2013/04/06/reflective-dll-injection-with-powershell/)及其他资料）。关于`*NIX`系统（特别是Linux）也有许多研究成果，过去有些人提出了非常好的思路，如skape & jt
[[2]](http://www.hick.org/code/skape/papers/remote-library-injection.pdf)、the
grugq [[6]](https://grugq.github.io/docs/ul_exec.txt)、Z0MBiE
[[7]](http://z0mbie.daemonlab.org/infelf.html), Pluf & Ripe
[[8]](http://phrack.org/issues/63/11.html)、Aseem Jakhar
[[9]](http://www.securitybyte.org/resources/2011/presentations/runtime-thread-injection-and-execution-in-linux-processes.pdf)、mak
[[10]](https://github.com/mak/pyself)以及Rory McNamara
[[11]](https://blog.gdssecurity.com/labs/2017/9/5/linux-based-inter-process-code-injection-without-ptrace2.html)。

## 二、攻击场景

想象一下，我们正坐在一个闪烁的光标前，在刚入侵的Linux服务器上使用shell，此时我们想在不留下任何痕迹的情况下继续探索。我们需要运行其他工具，但不希望在主机上上传任何数据。或者，由于系统在已挂载分区上设置了`noexec`选项，因此无法运行任何程序。此时我们还能怎么办？

本文介绍了如何绕过运行限制，利用目标系统上仅有的工具在目标主机上运行代码。在 _everything-is-a-file_
（“一切都是文件”）的系统上，想做到这一点有点难度，但如果我们跳出思维限制，尽可能使用系统提供的功能，还是能找到可行性。

Sektor7实验室做了一些实验，研究新的、经过改进的攻击方法，希望能在本文中与大家共享。

## 三、Payload（Shellcode）投递

对攻击者而言，找到可靠又隐蔽的方法将payload或者工具投递到目标主机总是非常有挑战的一个任务。

最常见的方法是连接到C2服务器或者第三方服务器，这些服务器上托管着攻击所需工具，可以下载到目标系统中。这些操作可能会在网络基础架构上留下一些痕迹（如网络数据流、代理日志等）。

在许多情况下，攻击者会忽视目标主机上已经开放的一个控制通道：shell会话。攻击者可以将这个会话作为数据链路，将payload上传至受害系统中，无需与外部系统建立新的TCP连接。这种方法存在一些缺点，如果出现网络故障，那么数据传输和控制信道可能会发生中断。

在本文中，我们介绍了两种投递方法：out-of-band（带外）以及in-band（带内），并且主要使用后一种方法来传输代码（特别是shellcode）。

![](https://p3.ssl.qhimg.com/t0197ac2d6c88b77d3e.png)

## 四、演示环境

我们的实验环境如下：

  * 受害主机：运行最新版的Kali Linux虚拟机
  * 攻击主机：运行Arch Linux系统，作为VM的宿主系统
  * SSH连接：攻击主机到受害主机的SSH连接，模拟shell访问
  * 简单的`Hello World` shellcode，x86_64架构（参考附录A）

## 五、内存运行方法

###  tmpfs

攻击者用来存放文件的第一个位置是`tmpfs`。`tmpfs`会将所有数据存入内核内部缓存中，并且动态扩张和缩小以适配其中包含的文件。另外，从`glibc
2.2`开始，`tmpfs`会挂载到`/dev/shm`目录，用于POSIX共享内存（`shm_open()`、`shm_unlink()`）。

比如，Kali系统中已挂载的`tmpfs`虚拟文件系统目录如下所示：

![](https://p1.ssl.qhimg.com/t01150af21868f86b11.png)

默认情况下，已挂载的`/dev/shm`并没有设置`noexec`标志。如果某个处女座管理员设置了该标志，那么就能有效防住这种方法：攻击者虽然能存放数据，但无法执行（`execve()`执行失败）。

![](https://p2.ssl.qhimg.com/t012b0c406ec5a31df8.png)

后面我们还会提到`/dev/shm`。

###  GDB

**GNU Debugger**
是Linux上的模拟调试工具，虽然生产服务器上通常没有安装该工具，但我们偶尔可以在开发环境或者某些嵌入式/专用系统上找到该工具。`gdb(1)`
manual的说明如下：

> GDB主要能够提供如下功能，帮助我们捕捉程序运行中的bug：
>
>   * 启动程序，指定可能影响程序行为的任何因素；
>   * 在特定条件下停止程序运行；
>   * 检查程序运行时发生了什么事情；
>   * 修改应用中数据，这样就能尝试修正某个bug的影响，继续研究后续bug。
>

借助GDB的最后一个功能，我们可以在不落盘的情况下，在内存中运行shellcode。

首先我们需要将shellcode转换成byte字符串：

![](https://p5.ssl.qhimg.com/t0188b05cd07604f9a5.png)

然后，在`gdb`上下文中运行`/bin/bash`，在`main()`处设置断点，注入shellcode然后继续运行，如下所示：

![](https://p5.ssl.qhimg.com/t016ff7a564aa600f74.png)

###  Python

**Python** 是一门非常流行的解释性语言，与GDB不同，我们经常可以在默认的Linux环境中使用Python。

我们可以使用许多模块（比如`ctypes`）来扩展Python的功能，`ctypes`库提供了C兼容的数据类型，允许我们调用DLL或者共享库中的函数。换句话说，`ctypes`可以构建类似C的脚本、利用外部库的强大功能并且直接访问内核的`syscall`。

为了使用Python在内存中运行shellcode，我们的脚本需要执行如下操作：

  * 将`libc`库载入Python进程中
  * `mmap()`用于shellcode的一片新的`W+X`内存区域
  * 将shellcode拷贝至新分配的缓冲区中
  * 使该缓冲区可以被调用（强制转换）
  * 调用缓冲区

完整的脚本如下所示（Python 2）：

![](https://p0.ssl.qhimg.com/t019d78b6e693ef712c.png)

整个脚本可以转换为经过Base64编码的字符串：

![](https://p5.ssl.qhimg.com/t0184a605ec9cc0728b.png)

使用一条命令投递到目标主机上：

![](https://p3.ssl.qhimg.com/t013b55fe0054938def.png)

###  自修改dd

在极少数情况下，当上述方法都不能使用时，我们还可以使用许多Linux系统上默认安装一个工具。这款工具为`dd`（包含在`coreutils`软件包中），通常用来转换和拷贝文件。如果我们将该工具与`procfs`文件系统和`/proc/self/mem`文件（该进程的内存）结合起来，就找到了可能用来在内存中运行shellcode的一个小媒介。为了完成这个任务，我们需要强制`dd`动态修改自身数据。

`dd`运行时的默认行为如下所示：

![](https://p1.ssl.qhimg.com/t017273c9751ce4706d.png)

而自修改的`dd`运行时如下所示：

![](https://p3.ssl.qhimg.com/t0170ec62e4718c3726.png)

我们首先需要的是找到`dd`进程中可以复制shellcode的地方。整个过程必须能在运行中稳定且可靠，因为我们操作的是会覆盖自己内存的、正在运行的一个进程。

在成功复制/覆盖操作后调用的代码是一个不错的对象，后面跟着的就是进程退出操作。我们可以在PLT（Procedure Linkage
Table，过程链接表）、`exit()`调用主代码片段中或者`exit()`之前完成shellcode注入。

覆盖PLT并不是一个稳定的操作，因为如果我们的shellcode过长，就会覆盖在调用`exit()`前会使用的某些关键部位。

进一步调查后，我们发现程序在调用`exit()`前会调用`fclose(3)`函数：

![](https://p1.ssl.qhimg.com/t01bc6ff1bcf031c8fd.png)

只有两个地方调用了`fclose()`：

![](https://p2.ssl.qhimg.com/t014525b70ecd05b554.png)

进一步测试后，我们发现`0x9c2b`处的代码（`jmp 1cb0`）是运行时所使用的代码，并且后面跟着一大段代码，这些代码被覆盖后可能不会导致进程崩溃。

为了应用这个技术，我们还需要解决两个障碍：

1、在复制操作后，`dd`会关闭`stdin`、`stdout`以及`stderr`文件描述符：

![](https://p5.ssl.qhimg.com/t01f1c7c0d72710f2fa.png)

2、地址空间布局随机化问题。

我们可以在bash中复制`stdin`以及`stdou`文件描述符来解决第一个问题（参考`bash(1)`）：

> 复制文件描述符
>
> 重定向运算符`[n]<&word`可以用来复制输入文件描述符。如果`word`扩展到1或者更多数字，那么文件描述符`n`就会变成该文件描述符的副本。

我们可以在shellcode前添加`dup()` syscall：

![](https://p4.ssl.qhimg.com/t019cde2ae7b80e2977.png)

第二个问题比较麻烦。现在在大多数Linux发行版中，二进制程序会被编译成PIE（Position Independent
Executable，位置无关可执行文件）对象：

![](https://p4.ssl.qhimg.com/t01257f09c1a922cde9.png)

并且默认情况下ASLR处于启用状态：

![](https://p5.ssl.qhimg.com/t01967ce239497ab870.png)

幸运的是，Linux支持每个进程使用不同的执行域（execution
domains，即personality，个性化机制）。执行域可以指导Linux如何将signal编号映射为signal动作。执行域系统可以让Linux为在类UNIX系统中编译的程序提供部分支持。从Linux
2.6.12开始，我们就可以使用`ADDR_NO_RANDOMIZE`标志，这个标志可以在正在运行的进程中禁用ASLR。

为了在userland（用户级）运行时关闭ASLR，我们可以使用`setarch`工具设置不同的personality标志：

![](https://p1.ssl.qhimg.com/t0143f21f0346ab5c8b.png)

现在一切准备就绪，可以运行自修改的`dd`了：

![](https://p3.ssl.qhimg.com/t01738bd023035267a2.png)

###  系统调用

除了`tmpfs`之外，以上方法都有一个巨大的缺点：虽然这些方法能够执行shellcode，但无法执行可执行对象（即ELF文件）。如果我们还需要更为复杂的功能，就会发现纯汇编shellcode用处有限并且不可扩展。

这里内核开发者又来救火了：Linux从3.17版开始引入了一个新的系统调用：`memfd_create()`。这个调用可以创建一个匿名文件，返回对应的文件描述符。这个文件行为上类似正常文件，但存在于RAM中，并且所有引用计数归零后就会自动释放该文件。

换句话说，Linux内核提供了一种方法，可以创建内存中的文件，并且该文件看上去与正常文件类似，可以执行`mmap()`或者`execve()`操作。

我们可以通过如下步骤在虚拟内存中创建基于`memfd`的文件，最终将我们的工具上传至受害主机中，无需落盘：

  * 创建shellcode，该shellcode会在内存中创建一个`memfd`文件
  * 将shellcode注入`dd`进程中（参考前文“自修改dd”内容）
  * 挂起`dd`进程（由shellcode完成）
  * 准备待上传的工具（这里我们以静态链接的`uname`为例）
  * 利用in-band数据链接（通过shell会话）将经过base64编码的工具传输到受害主机上，直接载入`memfd`文件中
  * 运行工具

首先要做的就是创建一个新的shellcode（参考附录B）。新的shellcode重新打开已关闭的`stdin`和`stdout`文件描述符，调用`memfd_create()`创建内存文件（这里为`AAAA`），然后调用`pause()`
syscall挂起目标进程（`dd`）。这里需要执行挂起操作，因为我们要避免`dd`进程退出，并且使其他进程能够访问其`memfd`文件（通过`procfs`）。shellcode中的`exit()`
syscall应该永远没有调用机会。

然后我们修改`dd`，挂起并检查`memfd`文件是否存在于内存中：

![](https://p1.ssl.qhimg.com/t012ff720d3392994e4.png)

接下来要准备待上传的工具。需要注意的是攻击者使用的工具必须静态链接或者使用与目标主机上相同的静态库。

![](https://p2.ssl.qhimg.com/t01e5cd0c8e558f4d7a.png)

接下来只需要将经过Base64编码的工具`echo`到`memfd`文件中，运行即可：

![](https://p3.ssl.qhimg.com/t0192b5171ba347ae95.png)

需要注意的是我们可以重复使用`memfd`文件。如果有必要的话，我们可以使用同一个文件描述符“存储”下一个工具：

![](https://p5.ssl.qhimg.com/t01231eaf1d95ea1c77.png)

**那么如果受害主机上运行的内核版本比3.17要早呢？**

有个名为`shm_open(3)`的C库函数，这个函数可以在内存中创建新的POSIX共享对象，而POSIX共享对象实际上是一个句柄，不相关进程可以使用该句柄来`mmap()`同一个共享内存区域。

来看一下`Glibc`源代码。`shm_open()`会在某些`shm_name`上调用`open()`（源文件：[glibc/sysdeps/posix/shm_open.c](https://code.woboq.org/userspace/glibc/sysdeps/posix/shm_open.c.html)）：

![](https://p3.ssl.qhimg.com/t01361e6d40981b32ce.png)

而`shm_name`使用`shm_dir`动态分配：

![](https://p1.ssl.qhimg.com/t01ac1dd5a0a73ec3fa.png)

`shm_dir`由`_PATH_DEV`与`shm/`拼接而成（源文件：[glibc/sysdeps/posix/shm_open.c](https://code.woboq.org/userspace/glibc/sysdeps/posix/shm_open.c.html)）：

![](https://p3.ssl.qhimg.com/t015fb3dd8700c77f7c.png)

而`_PATH_DEV`的定义为`/dev/`。

因此，`shm_open()`实际上是在`tmpfs`文件系统上创建/打开了一个文件，而前面我们已讨论过这方面内容。

## 六、OPSEC注意事项

在目标主机上执行任何攻击活动都需要考虑潜在的副作用。虽然我们已经尽量避免代码落盘，但我们的行为仍然可能留下一些“蛛丝马迹”，包括：

1、日志（如shell历史数据）。在这种情况下攻击者需要确保日志已被删除或者覆盖（某些情况下，由于权限不够我们无法做到这一点）。

2、进程列表。如果另一个用户在受害者机上查看正在运行的进程，可能会看到一些奇怪的进程名（如`/proc/< num
>/fd/3`）。我们可以修改目标进程的`argv[0]`字符串来规避这一点。

3、Swappiness。即使我们的载荷存在于虚拟内存中，大多数情况下它们可能会被交换到磁盘上（对交换空间的分析是另一个话题）。我们可以采用如下策略规避这一点：

  * `mlock()`、`mlockall()`及`mmap()`：需要`root`或者`CAP_IPC_LOCK`。
  * `sysctl vm.swappiness`或者`/proc/sys/vm/swappiness`：需要`root`权限。
  * `cgroup`（`memory.swappiness`）：需要`root`或者修改`cgroup`的相应权限。

最后一种方法并不能保证在负载较重的情况下内存管理器不会将进程交换到硬盘上（比如root cgroup允许交换且需要内存时）。

## 七、参考资料

In-Memory PE EXE Execution by Z0MBiE/29A  
<https://github.com/fdiskyou/Zines/blob/master/29a/29a-6.zip>

Remote Library Injection by skape & jt  
<http://www.hick.org/code/skape/papers/remote-library-injection.pdf>

Reflective DLL Injection by Stephen Fewer  
<https://www.dc414.org/wp-content/uploads/2011/01/242.pdf>

Loading a DLL from memory by Joachim Bauch  
<https://www.joachim-bauch.de/tutorials/loading-a-dll-from-memory/>

Reflective DLL Injection with PowerShell by clymb3r  
<https://clymb3r.wordpress.com/2013/04/06/reflective-dll-injection-with-powershell/>

The Design and Implementation of Userland Exec by the grugq  
<https://grugq.github.io/docs/ul_exec.txt>

Injected Evil by Z0MBiE/29A  
<http://z0mbie.daemonlab.org/infelf.html>

Advanced Antiforensics : SELF by Pluf & Ripe  
<http://phrack.org/issues/63/11.html>

Run-time Thread Injection The Jugaad way by Aseem Jakhar  
<http://www.securitybyte.org/resources/2011/presentations/runtime-thread-injection-and-execution-in-linux-processes.pdf>

Implementation of SELF in python by mak  
<https://github.com/mak/pyself>

Linux based inter-process code injection without ptrace(2) by Rory McNamara  
<https://blog.gdssecurity.com/labs/2017/9/5/linux-based-inter-process-code-injection-without-ptrace2.html>

## 八、附录

###  附录A

实验中使用的`Hello world` shellcode：

![](https://p2.ssl.qhimg.com/t015858ebf23ce9d72f.png)

###  附录B

![](https://p2.ssl.qhimg.com/t01d67f892e21dc2682.png)

本文翻译自blog.sektor7.net [原文链接](https://blog.sektor7.net/#!res/2018/pure-in-memory-linux.md)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168204](/post/id/168204)

安全客 - 有思想的安全新媒体

本文转载自: [blog.sektor7.net](https://blog.sektor7.net/#!res/2018/pure-in-memory-linux.md)

如若转载,请注明出处： <https://blog.sektor7.net/#!res/2018/pure-in-memory-linux.md>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [代码注入](/tag/代码注入)
  * [系统安全](/tag/系统安全)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

