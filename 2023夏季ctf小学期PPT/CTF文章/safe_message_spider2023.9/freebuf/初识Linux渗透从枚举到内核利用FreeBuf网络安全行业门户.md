****

### ![1.png](https://image.3001.net/images/20180718/15319062116799.png)

## 背景

**许多人都认为Linux是最安全的操作系统，因此在对Linux的安全问题上也放松了警惕。那么事实真的如此吗？其实安全从来都只是相对的，Linux也不例外。虽然它加载了强大的安全机制，但仍可能受到来自各方面带来的安全威胁。本文我们主要将讨论有关Linux架构的主要利用技术，以及相关的安全防御措施。**

 **PS：本文仅用于技术讨论与分享，严禁用于非法用途**

##  **Linux 概述**

 **![2.png](https://image.3001.net/images/20180718/15319062316079.png)**

操作系统的主要目的是用于管理计算机硬件及软件资源，并为计算机程序提供通用服务。Linux操作系统是由 Linus
Torvalds于1991年开发的一个UNIX操作系统的克隆版本。不要混淆了Linux和Unix。它具有GNU通用公共许可证（GPL）的许可。Linux下为我们提供了强大的Shell系统用户界面，用于接收用户输入的命令并把它送入内核执行。一些比较知名的shell包括：Bourne
again shell (Bash), C shell (csh), Korn shell (ksh)。你可以通过cat
/etc/shells查看你当前的shell环境类型。

![3.png](https://image.3001.net/images/20180718/15319062498027.png)

以下是一些非常常用的linux命令：

ls：列出文件和目录

find：查找文件

cd：切换路径

cp：复制

mv：移动

mkdir：创建一个目录

rmdir：删除目录

rm：删除文件

想要了解有关命令的更多细节信息，只需键入man命令即可。

![4.png](https://image.3001.net/images/20180718/15319062703632.png)

##  **Linux 流和重定向**

当你与Linux环境进行交互时，它将为你提供输入/输出重定向功能以简化你的体验。关于输入输出流的操作, 有以下三种流你可以使用：

标准输入流 (stdin)

标准输出流 (stdout)

标准错误输出 (stderr)

这三个主要流的图示如下：

![5.png](https://image.3001.net/images/20180718/1531906289278.png)

另一个功能是重定向。它主要用于对流的重定向。执行文本重定向，你可以使用以下符号：

“>”：覆盖文件。

“>>”：将输入添加到文件中。

以下是一些重定向符号及其用途列表：

![6.jpg](https://image.3001.net/images/20180718/15319063071661.jpg)

##  **Linux文件系统层次结构**

在Linux中，一切都可以看做文件，包括所有允许/禁止读写执行权限的目录和设备。Linux的[分层](https://www.peerlyst.com/tags/hierarchical)设计如下：

![7.png](https://image.3001.net/images/20180718/15319063333146.png)

/root：系统管理员的主目录

/home：包含所有用户的个人文件

/bin：包含所有二进制文件（可执行文件）

/sbin：超级管理命令，这里存放的是系统管理员使用的管理程序

/lib：包含所需的库文件

/usr：包含普通用户使用的二进制文件

/opt：包含可选的附加应用程序

/etc：包含程序所需的所有配置文件

/dev：包含设备文件

/media：包含临时可移动设备的文件

/mnt：包含文件系统的挂载点

/boot：包含引导加载程序文件

/tmp：包含临时文件

/var：包含变量文件，如日志文件

/proc：包含有关系统进程的信息

![8.png](https://image.3001.net/images/20180718/15319063677929.png)

##  **用户和组**

用户和组在Linux中至关重要，同时它提供多任务和多用户功能。管理用户和组，你可以使用以下linux命令：

Useradd：添加新用户

Passwd：更改用户密码

Userdel：删除用户，你可以添加“-r”选项删除用户的文件

查看用户组文件：cat /etc/group

![9.png](https://image.3001.net/images/20180718/15319063952163.png)

创建一个组：

 **newgrp** <Group-Name-Here>

##  **权限**

在Linux中用户和组的权限主要包括：

读，以字母r表示

写，以字母w表示

执行，以字母x表示

要查看文件的权限，除了-l选项外，还可以使用ls命令：

![11.png](https://image.3001.net/images/20180718/15319064391083.png)

##  **chmod , chown 和 chroot 命令：**

要更改文件权限，可以使用chmod命令，格式如下：

 **chmod** <Permission Letters> <File/Directory>

或者你也可以使用八进制表示来代替字母

![12.png](https://image.3001.net/images/20180718/15319064816739.png)  

chown用于更改文件的所有者。

chroot改变程序执行时所参考的根目录位置。

##  **Cronjobs 和 Crontabs：**

自动化和任务调度是系统管理中非常重要的方面，尤其是在使用Linux时。自动化任务使系统管理员的工作变得更加轻松。Linux为我们提供了很好的任务调度功能，以在特定的时间运行命令或脚本，我们称之为Cron。调度
任务创建格式如下：

<Day of the week> <Month> <Day of the Month> <Hour> <Minutes> <Command>

![13.png](https://image.3001.net/images/20180718/15319065027225.png)

要检查Crontab（包含有关cronjobs信息的文件），只需键入cat /etc/crontab即可

![14.png](https://image.3001.net/images/20180718/15319065249156.png)

##  **Linux 攻击向量**

以上我们对Linux系统环境和命令已经有了一个初步的了解。下面，我们把目光转向有关Linux所面临的安全威胁上。攻击者的攻击媒介多种多样，通常攻击向量可以分为以下三种主要类型：

网络威胁

主机威胁

应用威胁

我们将在后半部分详细讨论有关针对Linux的安全威胁。在开始攻击Linux之前，枚举是必不可少的工作阶段。

##  **使用Nmap检测系统**

 **![15.png](https://image.3001.net/images/20180718/15319065446253.png)**

我们可以使用Nmap来帮助我们检测，当前主机是否在Linux上运行。只需输入nmap – O <target>即可。

##  **Linux 枚举**

有许多开源工具可以帮助我们枚举Linux机器。推荐大家使用LinEnum，在我看来这是最好用的工具之一。

你可以在这里进行下载：<https://github.com/rebootuser/LinEnum>

使用：./LinEnum.sh -k keyword -r report -e /tmp/ -t

 **选项：**

-k 输入关键字

-e 输入导出位置

-t 包括彻底（冗长）测试

-r 输入报告名称

-h 显示帮助文本

不带参数运行 = 有限扫描/没有输出文件

-e 要求用户输入输出位置，例如/tmp/export。如果不存在该目录文件，则会自动为你创建。

-r 要求用户输入报告名称。报告（.txt文件）将保存到当前工作目录。

-t 执行彻底（慢速）测试。如果不加该参数，则会执行默认的“快速”扫描。

-k 可选，支持用户在大量文件中搜索单个关键字。

![16.png](https://image.3001.net/images/20180718/15319065779632.png)

LinEnum可帮助你查找有关Linux主机的信息，包括：

###  **系统信息：**

主机名

网络详情

当前IP

默认路由详情

DNS服务器信息

###  **用户信息：**

当前用户详细信息

最后登录用户

显示用户登录主机

列出所有用户，包括uid/gid信息

列出root帐户

提取密码策略和哈希存储方式信息

检查umask值

检查/etc/passwd中是否存储密码哈希值

提取“默认”uid的完整详细信息，例如0,1000,1001等

尝试读取受限制的文件，即/etc/shadow

列出当前用户的历史文件（如bash_history，.nano_history等）

基本的SSH检查

##  **Linux提权**

根据定义：“提权主要是利用编程错误或设计缺陷，来授予攻击者特殊权限以访问网络及其相关数据和应用程序等。”（摘自techtarget.com）。

提权可分为垂直和水平两种；平行提权，即权限类型不变，权限ID改变。垂直提权，即权限ID不变，权限类型改变。野外使用的提权技术种类繁多其中包括：

Linux Services Exploitations：通过查找linux服务或配置中的错误来提权。

通配符：通配符可用于注入任意命令。

具体可以参考，之前发布的一篇有关[利用通配符进行Linux本地提权](http://www.freebuf.com/articles/system/176255.html)的文章。

###  **SUID 滥用：**

在这种技术中，攻击者使用需要root权限的合法工具（如nmap）在系统上运行恶意命令

###  **Linux内核利用：**

这种利用的危害极大。一旦攻击者成功利用linux内核，他们将能够完全控制系统。

检查系统是否存在权限提升漏洞，可以使用 “Linux privilege
checker”。下载地址：[https：//github.com/sleventyeleven/linuxprivchecker/blob/master/linuxprivchecker.py](https://github.com/sleventyeleven/linuxprivchecker/blob/master/linuxprivchecker.py)

![17.png](https://image.3001.net/images/20180718/15319066145925.png)

##  **Linux Exploit Suggester**

Linux Exploit Suggester是一款由PenturaLabs开发的，可根据操作系统版本号自动查找相应提权脚本的工具。其主要功能包括：

“Remote" 模式 (--kernel 或 --uname 开关)

"Direct" 模式 (默认)

"CVE list" 模式 (--cvelist-file 开关)

"Check security" 模式 (--checksec 开关)

使用：./linux-exploit-suggester.sh

下载地址：<https://github.com/mzet-/linux-exploit-suggester>

甚至它还为我们提供了加固措施：

![18.png](https://image.3001.net/images/20180718/15319066453507.png)

![19.png](https://image.3001.net/images/20180718/15319066706038.png)

##  **Linux内核利用**

如今的操作系统大都基于“环保护模型”（ring protection mode）。该模型通常分为4层，编号从0到3，如下图所示：

![20.png](https://image.3001.net/images/20180718/15319066923460.png)

Linux操作系统也基于相同的机制，但只有2层：User Land 和 Kernel
Land。内存管理（Memorymanagement）是linux内核提供的最强大的功能之一。

###  **内核利用技术：**

 **1.空指针引用**

NULL指针错误会引发空指针NullPointerException异常。换句话说，就是编程对象引用了值为NULL的地址。

![21.jpg](https://image.3001.net/images/20180718/15319067136872.jpg)

 **2.任意内核读/写**

该攻击主要是通过将数据传递到Linux内核实现的。

 **3.内存损坏漏洞**

为方便内部的处理，内存被划分为了4096字节的内存块，并被命名为page。12个最低有效位是偏移量；其余的是页码。在最新的x86架构中，Linux内核将虚拟空间（通常为4GB）当中的3GB给了UserLand，另外1GB用于kernel
land。此操作称为分段。该操作称之为分段。

内核使用页码来表示物理和虚拟之间的对应关系地址。为了管理不同的内存区域，这里使用了虚拟内存区域（VMA）：

**![22.png](https://image.3001.net/images/20180718/15319067408208.png!small)**

 **A-内核栈漏洞：**

堆栈是一个特殊的内存空间。这个内存空间会自动增长。而攻击者也正是利用了这一点，一旦函数调用过多，就会致使调用堆栈无法容纳这些调用的返回地址，导致数据越界，覆盖老的堆栈数据产生栈溢出漏洞。

 **B-内核堆漏洞：**

堆用于动态内存分配。内核堆利用是非常危险的，因为在多数情况下，攻击者往往不需要准备任何的Linux模块调试环境，即可实现堆利用。

 **Race Condition(竞争条件)**

由于两个或者多个进程竞争使用不能被同时访问的资源，使得这些进程有可能因为时间上推进的先后原因而出现问题，这就叫做竞争条件（Race
Condition）。为了避免这个问题，linux实现了我们所谓的Mutex（互斥对象）。

 **缓冲区溢出防御技术**

这里有许多已实现技术，可以帮助你抵御缓冲区溢出攻击，例如：

 **地址空间布局随机化：** Address space layout randomization
(ASLR)，是参与保护缓冲区溢出问题的一个计算机安全技术。是为了防止攻击者在内存中能够可靠地对跳转到特定利用函数。ASLR包括随机排列程序的关键数据区域的位置，包括可执行的部分、堆、栈及共享库的位置。

##  **stack canary**

stack canary防护技术主要用于防止stack overflow（堆栈溢出）。如果能在运行时检测出stack
overflow破坏，就有可能对函数栈进行保护。目前的堆栈保护实现大多使用基于 “Canaries” 的探测技术来完成对这种破坏的检测。

![23.png](https://image.3001.net/images/20180718/15319067925417.png)

##  **Non-executable stack**

不可执行堆栈（NX）是一种虚拟内存保护机制，通过限制特定内存和实现NX位来阻止shell代码注入在堆栈上执行。

##  **Linux 返回导向编程（ROP）**

返回导向编程（ROP）是一种高级的内存攻击技术，简单的来说它的特点就是通过控制返回指针来使程序导向新的控制流，利用场景包括使用ROP来绕过DEP、ASLR这样的防御机制。

![24.png](https://image.3001.net/images/20180718/15319068178154.png)

##  **Linux安全加固**

以下是我对你的一些Linux安全加固建议：

定期更新Linux内核和应用程序。

避免使用像FTP和telnet这类的不安全服务，建议使用SFTP和OpenSSH。

仅使用必要的应用和服务，最大化的减小攻击面。

如果条件允许，建议使用SELinux。

使用强密码策略。

关注faillog记录。

强化/etc/sysctl.conf配置。

使用身份验证服务器。

## 总结

本文主要向大家概述了一些基础的有关Linux系统命令和术语，并深入探讨了Linux安全方面的问题以及利用与防御技术。希望通过本文的学习，能让你对Linux有一个更加深入的了解。

##  **相关参考文献**

1.高级基础设施渗透测试 - Packt Publishing：Chiheb chebbi

2.Linux用户和组：<https://www.linode.com/docs/tools-reference/linux-users-and-groups/>

3.使用Crontab在Linux上创建调度任务：<https://kvz.io/blog/2007/07/29/schedule-tasks-on-linux-using-crontab/>

4.LinEnum： _<https://github.com/rebootuser/LinEnum>_

***参考来源：peerlyst，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

