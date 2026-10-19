## 前言

 **本文是结合笔者多年网络安全工作经验，并参照这本Kali Linux官方教程《Kali Linux
Revealed》，献给信息安全爱好者及想参加Kali Linux Certified Professional (KLCP) Kali
Linux认证专家考试的同学。  
**

## 一、什么是Kali Linux认证专家（KLCP）

### 1.1认证概述

Kali-Linux认证专家（KLCP）是一个信息安全专业认证。KLCP证书的持有者可以证明其对Kali-Linux渗透测试平台的透彻理解。持有此证书的个人已经具备了将Kali-Linux用作超级用户的技能和能力，能够创建高度定制和安全的部署。此外，KLCP为任何信息安全专业人员提供了基础知识，允许他们将其作为信息安全事业的坚实基础，或是更高级培训和认证的第一步。

### 1.2考试概况

KLCP认证考试是基于计算机上机考试的，包含80题、均为多项选择题考试。你将有90分钟的时间完成考试，完成后将收到你的分数。这些问题来源于上述书籍和知识体系所涵盖的材料。

### 1.3证书获取

如果你通过了认证考试，你将收到一份显示你成绩的打印证书。Kali
Linux团队将联系您，告诉您如何获取证书。一旦您的送货信息已经提供，您可以在30-40天内收到您的证书。

## 二、Kali Linux认证专家考前复习指南

### 2.1关于KALI LINUX

KaliLinux 是基于 Debian 测试版的滚动更新版

### 2.2开始使用KALILINUX

> 1 如果你有一台Intel 64位 cpu的笔记本型计算机，你可以安装Kali 64-bit或Kali 32-bit
>
> 2 查看/proc/cpuinfo文件，你就能确认你计算机上面的CPU是32位还是64位
>
> 3 你可以使用wget -q -O –<https://www.kali.org/archive-key.asc>| gpg
> –import命令通过https下载Kali Linux镜像并导入Kali Linux的公钥
>
> 4 如果想使用Kali Linux 的虚拟机映像，你应该使用Kali 官方的Kali VM image

### 2.3 LINUX使用基础

1 用户的家目录是用～字符代表

2 使用以下命令得到文件的信息

> （1）type
>
> （2）Which

3 drwxr-xr-x 2 root root 60 Mar 21 08:30 vfio文件既不是块设备文件，也不是字符设备文件

4 文件的权限是 -r—w—- 表示为420

5 一个文件是-r-x--x--- 1 user root 0 Mar 24 01:19 test权限，那么user拥有的权限是读和执行

6 如果有2个在后台工作的任务，你应使用kill %1 命令停止第一个任务

7 chperm命令不能控制权限或者关联用户到一个文件的属性

8 id命令能够显示用户运行会话标识的身份，并也能列出用户所属组。

9 lspci 命令能够在/proc and /sys虚拟文件系统中总结PCI硬件

10 根据FHS文件系统，/var 目录包含日志文件，队列，缓冲区和cache数据

### 2.4安装KALI LINUX

1 对于基于Intel CPU的Kali SSH 无桌面服务器，这是推荐的配置512 MB RAM / 2 GB hard drive free space
/ amd64 CPU

2 512 MB RAM / 2 GB hard drive free space 不符合Kali Linux 桌面最小的配置要求

3 即使你不选择网络镜像服务器，Kali Linux 安装也能成功

4 对于使用Kali Linux 的mini.iso启动, 如果没有网卡和internet网络，Kali Linux 的安装会失败

5 手工分区极有可能因为用户的错误造成分区错误。

6 如下分区方式最适合服务器和多用户系统

> 分离/home, /var, and /tmp 分区

7如果在安装完Kali 之后，再安装最新版的windows，导致boot loader被擦掉，阻止Kali 启动

8 preseed.cfg配置文件的作用是对于安装时的问题，给以预定的回答。

9 在ARM 设备上安装Kali最简单和最有效的过程是用一个官方的、有效的Kali ARM 映像，登录使用root，密码是toor

10 在安装失败后，保存日志到Kali bug tracker 并不是好办法

### 2.5配置KALI LINUX

1 你可以使用GNOME 控制中心的NetworkManager去图形化设置网络选项

2 网卡配置文件在/etc/network，它是命令行网络配置的重要一部分

3 在Kali 通过ifupdown 命令配置网络

4 iface eth0 inet static 是配置静态IP地址网络的命令

5 如下方法都可以配置Kali Linux 的网络设备：

> （1）通过命令行设置systemd-networkd
>
> （2）通过/etc/network/interfaces 文件
>
> （3）通过ifupdown 命令

6 使用图形化工具的 NetworkManager 和命令行设置/etc/systemd/network 是一样的

7 用户密码加密后放在/etc/shadow 里面

8 向Kali Linux 中增加用户使用adduser 命令

9 用这个命令停用用户的账号passwd -l olduser

10 对于Kali默认安装的SSH服务，你需要知道的是如下：

> （1）默认配置阻止基于密码的登录
>
> （2）SSH 服务默认停用
>
> （3）SSH 服务默认被安装
>
> （4）从LIVE IMAGE 安装的，密钥是预生成的

11 systemctl命令可用于控制ssh和postgresql服务

12 使用createdb创建一个新的postgresql 数据库

13 pg_createuser并不是一个postgresql 命令

14 想创建一个postgres 数据库叫db_new，参考如下命令：

    
    
    createdb -T template0 -E UTF-8 -O dbuser db_new

15 启动Apache2不能使用如下命令systemctl start apache

16 apachectl和Apache2并不相关

17 在Kali中,systemd 负责启动顺序, 也作为服务管理器和监控器。

18 使用systemctl status postgresql命令检查postgresql 服务的状态

### 2.6帮助完善 KALI LINUX

1 使用

> （1）dpkg -l | grep nmap
>
> 或（2）dpkg -s nmap | grep ^Version
>
> 或（3）dpkg-query -l | grep nmap

命令检查是否kali中的nmap 被修改过。

2 使用reportbug命令报告bug给Debian 的开发者

3 使用如下两种方式向Debian 开发者提交bug

> （1）使用官方Debian bug
> tracker[https://bugs.debian.org](https://bugs.debian.org/)发送一个email
> 给submit@bugs.debian.org
>
> （2）提交bug 给官方Kali bug tracker
> 在[https://bugs.kali.org](https://bugs.kali.org/)并且标记Debian 补丁.

### 2.7 KALILINUX 的安全和监控

1 Kali Linux 默认安装时，没有内建的安全功能启用

2 如下命令和Kali Linux 防火墙关联：

> （1）iptables
>
> （2）netfilter
>
> （3）ip6tables
>
> （4）fwbuilder

3 INPUT是Kali Linux 防火墙的默认链

4 如下配置使得Kali Linux 防火墙不处理包：

> （1）ULOG
>
> （2）ACCEPT
>
> （3）LOG

5 Kali Linux 防火墙处理顺序是如下：

> （1）PREROUTING
>
> （2）INPUT
>
> （3）FORWARD
>
> （4）OUTPUT
>
> （5）POSTROUTING

6 MASQUERADE 方法用于伪造源NAT包在Kali Linux 防火墙中

7 iptables -A INPUT -s 8.8.8.8 -j DROP命令的作用是阻止来源于8.8.8.8的所有数据包：

8 使用iptables -F INPUT命令删除INPUT 链的所有规则。

9 使用 iptables -A INPUT -m state –state NEW -p tcp –dport 22 -j ACCEPT
命令明确地允许SSH连接到你的Kali Linux 机器

10 使用 /etc/network/interfaces 文件，保证在Kali Linux 启动时间应用自定义的防火墙规则。

11 使用gnome-system-monitor工具，进行图形化监控进程状态

12 使用 dpkg -V 命令去确认可疑的包。

13 使用 fail2ban 防御登录时的 brute-force

### 2.8 DEBIAN包管理技巧

1 使用 dpkg 命令直接安装包，而不需要考虑依赖包。

2 Advanced Package Tool 工具是一个完整的包管理系统，用于安装、删除、更新包，也能升级系统。

3 使用 /etc/apt/sources.list 文件定义包源。

4 正确的apt源是:deb<http://http.kali.org/kali>kali-rolling main non-free contrib

5 如下apt源不适用于Debian 免费软件列表：

deb<http://http.kali.org/kali>kali-rolling main non-free contrib

6 对于大多数用户来说，kali-rolling 是推荐的。

7 使用 dpkg -i man-db_2.7.0.2-5_amd64.deb 命令安装man-db包

8 在Kali Linux 上使用apt-get full-upgrade 命令，执行更新并删除废弃的包，安装新的依赖包。

9 使用 apt update 命令下载最新的可用包

10 使用 dpkg -L metasploit-framework 命令列出metaploit-framework 包安装的全部文件

11 使用 dpkg -S msfconsole 命令显示msfconsole包安装的文件路径和名字。

12 使用dpkg -l 命令列出操作系统中已经安装的全部包名字。

13 使用 dpkg –add-architecture 命令为不同的 CPU 安装CPU架构支持。

14 Kali 的包管理器的图像化前端有 synaptic 和 aptitude

15 使用 dpkg –print-architecture 命令显示安装在当前操作系统中cpu体系架构。

16 control.tar.gz包含 Debian包最重要的信息。

17 manifest不是标准Debian 包的一部分

18 data.tar.xz 文件包含全部在文件系统中安装的 Debian 包信息

19 Breaks 包头将引发dpkg拒绝安装一个包，并触发apt去解决更新一个不兼容的包到最新。

20 postconf 不是一个有效的 Debian 包配置脚本

### 2.9高级使用技巧

1 apt source 命令会下载Debian 包的源代码

2 git clone 命令将会取回GIT 仓库的源代码

3 假设你在一个有未解包源代码的目录中，使用命令 apt build-dep ./ ，安装在 debian/control文件中 Build-Depends
域对应的依赖包

4 debian/changelog文件将揭示你的Debian 包变更是否有卡住。

5 在应用变更时，使用 dch –local kali 命令更新以kali作为前缀的Debian包

6 如下是正确从一个正在运行的Kali Linux 实例复制到当前目录下一个下载的Kali源代码树中：

    
    
    $ cp /boot/config-4.9.0-kali1-amd64 ~/kernel/linux-source-4.9/.config

7 使用make menuconfig 命令执行图形化内核配置工具。

8 使用apt install curl git live-build命令安装Kali Linux 环境

9 kali-linux-full metapackage 安装默认Kali Linux 安装的全部软件

10 persistence.conf 文件包含维护目录的数据

11 使用 mkfs.ext3 -L persistence /dev/sdc3
命令创建第三个硬盘的第三个分区，名为“persistence”，并格式化为EXT3文件系统。

12 使用 # cryptsetup luksOpen /dev/sdb3 kali_persistence 命令准备一个 LUKS
容器在/dev/sdb3

13 使用 # cryptsetup luksAddNuke /dev/sdb4 命令给/dev/sdb4的LUKS分区添加一个空密码

### 2.10在企业中使用KALI LINUX

1 可使用如下方法在一个没有操作系统的机器中安装Kali

> （1）DHCP
>
> （2）PXE
>
> （3）BOOTP
>
> （4）TFTP

2 使用 salt ’*’ pkg.install dnmap 命令安装dnmap下属的全部包。

3 使用 dpkg-buildpackage -us -uc 命令通过未签名的 .buildinfo 和 .changes
文件，从一个未签名的源代码包生成一个二进制包

4 使用 reprepro 命令创建和管理Debian 仓库

5 repo 配置文件要求的域：

> （1）Codename
>
> （2）Components
>
> （3）Architectures

6 通过编辑 sources.list 文件，使得可以使用自定义的仓库

### 2.11介绍安全评估

1 CIA模型不包含：

> （1）分类
>
> （2）信息
>
> （3）可访问性
>
> （4）认证

2 假如一个企业的web服务器主要用于财务报告，那么最关心的是可用性

3 在一个加密算法中发现一个缺陷，减弱了加密系统的强度，依据CIA模型，它减弱的是机密性

4 对于安全弱点，你可以exploit

5 Overall Risk是指对发生、影响、响应、维护相关的全部安全风险。

6 Penetration Test 的作用是作为杠杆去发现最坏的场景。

7 Client-Side Attack 是一种技术，用于针对目标组织内员工工作站上安装的各种应用程序进行攻击。

## 三、后记

Kali Linux官方教程，本文附加免费下载链接

> <https://kali.training/downloads/Kali-Linux-Revealed-1st-edition.pdf>

通过学习原书并参考本文，你可以做到:

1、熟练使用Kali Linux操作系统。

2、自动化、定制和预装Kali Linux。

3、创建Kali设备，如Kali ISO。

4、构建、修改和托管Kali包和仓库。

5、创建、挂钩和修改简单的Kali包。

6、自定义并重建Linux内核。

7、通过网络部署Kali。

8、管理和协调Kali Linux的多个安装版本。

9、建立和定制Kali ARM架构映像。

10、创建自定义的渗透测试设备。

 ***本文作者：c9t9h5，转载请注明来自FreeBuf.com**

