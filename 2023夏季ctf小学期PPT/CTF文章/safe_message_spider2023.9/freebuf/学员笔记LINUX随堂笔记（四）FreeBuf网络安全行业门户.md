文章来源：知了堂冯老师  

![v2-c4c958a3e1dfbc0814708d05a49ef731_hd
\(1\).jpg](https://image.3001.net/images/20191113/1573636231_5dcbc8875a08e.jpg!small)  

我来啦我来啦~昨天的消化好了吗？今天我们继续向优秀的同学学习！

![好好学习.gif](https://image.3001.net/images/20191115/1573790007_5dce21377c15d.gif!small)

## 第5章 软件包安装、升级、卸载

## 一. RPM包方式安装

### 1.1 rpm概述

RPM是Red Hat Packege Manager,是Red Het软件管理器，Fedora、Red
Hat、CentOS、SUSE、Mandrake等主流Linux发行版默认采用了这种软件包管理方式。

RPM包的中类和组成

rpm 对应的文件含义：httpd-2.2.15-29.el6.centos.x86_64.rpm

httpd //表示软件的名称

2.2.15 //表示软件的版本号

29 //表示软件更新发行的次数

x86_64 //表示适合硬件的平台

.rpm //是rpm软件包的标识

### 1.2 rpm包管理

1.查看已安装的rpm包

rpm

语法：rpm [子选项][软件名]

子选项

-qa //查看系统中已经安装所有rpm软件包列表

-qi //查看系统中已经安装指定软件的详细信息

-ql //查看指定软件包所安装的目录和文件列表

-qc //仅显示安装包的配置文件

-pd //仅显示指定软件安装包的安装文档文件

实例

rpm –qa _httpd_ //查看httpd软件包安装情况

2.查看rpm包的信息

rpm

语法：rpm -qp [子选项][rpm包]

子选项

-qpi //通过.rpm包文件查看该软件的详细信息

-qpl //查看.rpm安装包内所包含目录，文件列表

-qpc //查看.rpm安装包内包含的配置文件列表

-qpd //查看.rpm包含的文档文件列表

实例：

rpm -qpi _httpd-2.2.15-29.el6.centos.x86_64.rpm_ //查看httpd主程序包的详细信息

3.安装升级更新、卸载、完整性校验

rpm

语法：rpm [子选项][rpm包文件][辅助选项]

子选项

-i //安装一个新的rpm软件包

-U //升级某个rpm包，若原未安装，则进行安装

-F //更新某个rpm包，若原未安装，则放弃安装

-e //卸载指定的rpm软件安装包

实例

rpm –i _httpd-2.2.15-29.el6.centos.x86_64.rpm_ //安装httpd主程序

rpm –U _httpd-2.2.15-30.el6.centos.x86_64.rpm_ //更新安装httpd主程序

rpm –F httpd-2.2.15-30.el6.centos.x86_64.rpm //更新httpd主程序

rpm –e httpd //卸载httpd主程序

注意：卸载的时候会遇到依托关系，需要与下边的辅助选项配合使用

4.rpm辅助选项

\--force //强制安装所指定的rpm包

\--nodeps //安装、升级或卸载软件时，忽略包的依赖关系

-h //以“#”号显示安装进度

-v //显示安装过程中的详细信息

实例

rpm - Ivh _httpd-2.2.15-30.el6.centos.x86_64.rpm_ //显示安装信息和安装进度

rpm –e httpd –nodeps //强制卸载httpd软件

rpm –ivh httpd-2.2.15-30.el6.centos.x86_64.rpm –force //强制安装httpd软件

5.维护rpm数据库

重建 rpm

rpm –rebuilddb //重置rpm数据库

rpm –initdb //重置rpm数据库

导入公钥

语法 rpm --import [公钥文件所在位置路径]

软件包完整校验

使用md5查询

语法： md5sum [软件安装包]

实例：

md5sum _httpd-2.2.15-29.el6.centos.x86_64.rpm_ //获取httpd主程序包的加密码

查看文件时否被篡改

语法：rpm –K [软件安装包]

实例：

rpm –K _httpd-2.2.15-29.el6.centod.x86_64.rpm_ //检测httpd主程序包是否被篡改

## 二. 源码编译安装软件

确认源代码编译环境

gcc --version

g++ --version

源代码包安装流程

步骤1：tar解包

用途：解压并释放源代码包到指定目录

步骤2：./configure 配置

语法 ./configure --prefix = [安装路径]

用途：设置安装目录，安装模块等选项

步骤3：make 编译

用途： 生存可执行的二进制文件

步骤4：make install 安装

用途：复制二进制文件系统配置应用环境

### 2.1 ./configure参数详解

\--cache-file=FILE

'configure' 会在你的系统上测试存在的特性 ( 或者 bug!). 为了加速随后进行的配置 , 测试的结果会存储在一个cachefile 里 .
当 configure 一个每个子树里都有 'configure' 脚本的复杂的源码树时 , 一个很好的 cache file 的存在会有很大帮助

\--help

输出帮助信息 . 即使是有经验的用户也偶尔需要使用使用 '--help' 选项 , 因为一个复杂的项目会包含附加的选项 . 例如 ,GCC 包里的
'configure' 脚本就包含了允许你控制是否生成和在 GCC 中使用 GNU 汇编器的选项 .

\--no-create

'configure' 中的一个主要函数会制作输出文件 . 此选项阻止 'configure' 生成这个文件 . 你可以认为这是一种演习(dry run),
尽管缓存 (cache) 仍然被改写了 .

\--quiet

\--silent

当 'configure' 进行他的测试时 , 会输出简要的信息来告诉用户正在作什么 . 这样作是因为 'configure' 可能会比较慢,
没有这种输出的话用户将会被扔在一旁疑惑正在发生什么 . 使用这两个选项中的任何一个都会把你扔到一旁 .( 译注 : 这两句话比较有意思 , 原文是这样的 :

If there wasno such output, the user would be left wondering what is
happening. Byusing this option, you too can be left wondering!)

\--version

打印用来产生 'configure' 脚本的 Autoconf 的版本号 .

\--prefix=PREFIX

'--prefix' 是最常用的选项 . 制作出的 'Makefile' 会查看随此选项传递的参数 , 当一个包在安装时可以彻底的重新安置他的结构独立部分
. 举一个例子 , 当安装一个包 , 例如说 Emacs, 下面的命令将会使 Emacs Lisp file 被安装到"/opt/gnu/share":

$ ./configure --prefix=/opt/gnu

\--exec-prefix=EPREFIX

与 '--prefix' 选项类似 , 但是他是用来设置结构倚赖的文件的安装位置 . 编译好的 'emacs' 二进制文件就是这样一个问件 .
如果没有设置这个选项的话 , 默认使用的选项值将被设为和 '--prefix' 选项值一样 .

\--bindir=DIR

指定二进制文件的安装位置 . 这里的二进制文件定义为可以被用户直接执行的程序 .

\--sbindir=DIR

指定超级二进制文件的安装位置 . 这是一些通常只能由超级用户执行的程序 .

\--libexecdir=DIR

指定可执行支持文件的安装位置 . 与二进制文件相反 , 这些文件从来不直接由用户执行 , 但是可以被上面提到的二进制文件所执行 .

\--datadir=DIR

指定通用数据文件的安装位置 .

\--sysconfdir=DIR

指定在单个机器上使用的只读数据的安装位置 .

\--sharedstatedir=DIR

指定可以在多个机器上共享的可写数据的安装位置 .

\--localstatedir=DIR

指定只能单机使用的可写数据的安装位置 .

\--libdir=DIR

指定库文件的安装位置 .

\--includedir=DIR

指定 C 头文件的安装位置 . 其他语言如 C++ 的头文件也可以使用此选项 .

\--oldincludedir=DIR

指定为除 GCC 外编译器安装的 C 头文件的安装位置 .

\--infodir=DIR

指定 Info 格式文档的安装位置 .Info 是被 GNU 工程所使用的文档格式 .

\--mandir=DIR

指定手册页的安装位置 .

\--srcdir=DIR

这个选项对安装没有作用 . 他会告诉 'configure' 源码的位置 . 一般来说不用指定此选项 , 因为 'configure'
脚本一般和源码文件在同一个目录下 .

\--program-prefix=PREFIX

指定将被加到所安装程序的名字上的前缀 . 例如 , 使用 '--program-prefix=g' 来 configure 一个名为 'tar'
的程序将会使安装的程序被命名为 'gtar'. 当和其他的安装选项一起使用时 , 这个选项只有当他被 `Makefile.in' 文件使用时才会工作 .

\--program-suffix=SUFFIX

指定将被加到所安装程序的名字上的后缀 .

\--program-transform-name=PROGRAM

这里的 PROGRAM 是一个 sed 脚本 . 当一个程序被安装时 , 他的名字将经过 `sed -e PROGRAM' 来产生安装的名字 .

\--build=BUILD

指定软件包安装的系统平台 . 如果没有指定 , 默认值将是 '--host' 选项的值。

\--host=HOST

指定软件运行的系统平台 . 如果没有指定 , 将会运行 `config.guess' 来检测 .

\--target=GARGET

指定软件面向 (target to) 的系统平台 . 这主要在程序语言工具如编译器和汇编器上下文中起作用 . 如果没有指定 ,默认将使用 '--host'
选项的值 .

\--disable-FEATURE

一些软件包可以选择这个选项来提供为大型选项的编译时配置 , 例如使用 Kerberos 认证系统或者一个实验性的编译器最优配置 . 如果默认是提供这些特性
, 可以使用 '--disable-FEATURE' 来禁用它 , 这里 'FEATURE' 是特性的名字 .例如 :

$ ./configure --disable-gui

\--enable-FEATURE[=ARG]

相反的 , 一些软件包可能提供了一些默认被禁止的特性 , 可以使用 '--enable-FEATURE' 来起用它 . 这里 'FEATURE'是特性的名字
. 一个特性可能会接受一个可选的参数 . 例如 :

$ ./configure --enable-buffers=128

`--enable-FEATURE=no' 与上面提到的 '--disable-FEATURE' 是同义的 .

\--with-PACKAGE[=ARG]

在自由软件社区里 , 有使用已有软件包和库的优秀传统 . 当用 'configure' 来配置一个源码树时 , 可以提供其他已经安装的软件包的信息 . 例如
, 倚赖于 Tcl 和 Tk 的 BLT 器件工具包 . 要配置 BLT, 可能需要给 'configure' 提供一些关于我们把 Tcl 和 Tk
装的何处的信息 :

$ ./configure --with-tcl=/usr/local --with-tk=/usr/local

'--with-PACKAGE=no' 与下面将提到的 '--without-PACKAGE' 是同义的 .

\--without-PACKAGE

有时候你可能不想让你的软件包与系统已有的软件包交互 . 例如 , 你可能不想让你的新编译器使用 GNU ld. 通过使用这个选项可以做到这一点 :

$ ./configure --without-gnu-ld

\--x-includes=DIR

这个选项是 '--with-PACKAGE' 选项的一个特例 . 在 Autoconf 最初被开发出来时 , 流行使用 'configure'
来作为Imake 的一个变通方法来制作运行于 X 的软件 .'--x-includes' 选项提供了向 'configure' 脚本指明包含 X11
头文件的目录的方法 .'--x-libraries=DIR' 类似的 ,'--x-libraries' 选项提供了向 'configure' 脚本指明包含
X11 库的目录的方法 .在源码树中运行 'configure' 是不必要的同时也是不好的 . 一个由 'configure' 产生的良好的
'Makefile' 可以构筑源码属于另一棵树的软件包 . 在一个独立于源码的树中构筑派生的文件的好处是很明显的 : 派生的文件 , 如目标文件 ,
会凌乱的散布于源码树 . 这也使在另一个不同的系统或用不同的配置选项构筑同样的目标文件非常困难 . 建议使用三棵树 :

1、 插入补丁

patch -p1 < [需要打补丁的安装文件]

## 三. YUM安装软件

### 3.1 yum概述

Yum（全称为 Yellow dog Updater,
Modified）是一个在Fedora和RedHat以及CentOS中的shell前端软件包管理器。基于RPM包管理，能够从指定的服务器自动下载RPM包并且安装，可以自动处理依赖性关系，并且一次安装所有依赖的软件包，无须繁琐地一次次下载、安装命名为YUM。

使用yum工具管理软件包

yum的配置文件

基本配置文件：/etc/yum.conf

仓库设置：/etc/yum.repos.d/*.repo

日志文件：/var/log/yum.log

yum缓存目录（存放下载的软件包、仓库信息等数据）

/var/cache/yum/$basearch/$releasever

#yum clean all //清理缓存数据

软件包查询

yum list 软件名 //查询软件包列表

[root@localhost 桌面]#yum list updates //查询更新列表

yum info 软件名 //查询软件包描述信息

yum search all 关键词 //关键词查询相关软件包

查询软件包组

yum grouplist 包组名

yum groupinfo 包组名

软件安装

yum install 软件名 -y 表示自动确认

yum groupinstall 包组名

升级软件

yum update 软件名

yum groupupdate 软件组名

卸载软件

yum remove 软件名

yum groupremove 包组名

[root@localhost 桌面]#yum -y groupremove "Desktop"

### 3.2构建yum数据库

准备安装源（服务器端）

软件仓库的提供方式

FTP服务：ftp://...

HTTP服务：[http://..](https://link.zhihu.com/?target=http%3A//..).

本地目录：file:///..

RPM软件包的来源

Red Hat发布的RPM包**

第三方组织发布的RPM包**

用户自定义的RPM包**

### 3.2.1创建本地yum源

[root@localhost 桌面]#mkdir /media/cdrom //创建cdrom目录

[root@localhost 桌面]#mount /dev/cdrom /media/cdrom //挂载光驱到/media/cdrom下

[root@localhost 桌面]#cd /etc/yum.repos.d/ //切换到yum源所在路径

[root@localhost yum.repos.d]#mkdir _1_ //创建一个1目录

[root@localhost yum.repos.d]#mv *.repo 1 //将原有的源移动到1目录中

[root@localhost yum.repos.d]#vim local.repo //编写本地源文件

[base] //yum本地库名称

name=Red Hat Enterprise Linux //名称描述

baseurl=file:///media/cdrom //指定本地源路径

enabled=1 //启用该本地源

gpgcheck=1 //gpg检测开启

gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release //指定gpg-key路径

注意：如果gpgcheck=0，就不用写gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release

### 3.2.2配置ftp共享yum源(服务器端)

[root@localhost 桌面]#vim /etc/sysconfig/network-scripts/ifcnfig-eth0 //配置IP

[root@localhost 桌面]#service network restart //重启网络服务

[root@localhost 桌面]#mkdir /media/ _cdrom_ //创建cdrom目录

[root@localhost 桌面]#mount /dev/cdrom /media/cdrom //挂载光驱到/media/cdrom下

[root@localhost 桌面]#cd /media/cdrom/Packages/ //切换到光盘挂载点的包目录

[root@localhost Packages]# rpm -ivh vsftpd-2.2.2-11.el6_4.1.x86_64.rpm
//安装vsftpd软件

[root@localhost Packages]#mkdir /var/ftp/ _cent_ //在ftp默认路径下，创建一个cent目录

[root@localhost Packages]#cp * /var/ftp/cent/ //将当前目录中的所有内容复制到ftp目录下cent目录中

[root@localhost 桌面]#service vsftpd start //开启vsftpd服务

[root@localhost 桌面]#cd /etc/yum.repos.d/ //切换到yum源所在路径

[root@localhost yum.repos.d]#mkdir 1 //创建一个1目录

[root@localhost yum.repos.d]#mv *.repo 1 //将原有的源移动到1目录中

[root@localhost yum.repos.d]#vim local.repo //编写本地源文件

[base] //yum本地库名称

name=Red Hat Enterprise Linux //名称描述

baseurl=ftp://[当前服务器IP]/cent //指定本地源路径

enabled=1 //启用该本地源

gpgcheck=1 //gpg检测开启

gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release //指定gpg-key路径

### 3.2.3配置ftp共享yum源(客户端)

注意：确保客户端与服务器端网络能够正常通信

[root@localhost 桌面]#cd /etc/yum.repos.d/ //切换到yum源所在路径

[root@localhost yum.repos.d]#mkdir 1 //创建一个1目录

[root@localhost yum.repos.d]#mv *.repo 1 //将原有的源移动到1目录中

[root@localhost yum.repos.d]#vim local.repo //编写本地源文件

[base] //yum本地库名称

name=Red Hat Enterprise Linux //名称描述

baseurl=ftp://[YUM服务器IP]/cent //指定yum服务器yum源路径

enabled=1 //启用该本地源

gpgcheck=1 //gpg检测开启

gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release //指定gpg-key路径

## 四. PXE网络安装操作系统

服务器的批量部署准备阶段

规模化：同时装配多台服务器

自动化：安装系统、配置各种服务

远程实现：不需要光盘、U盘等安装介质

关于PXE网络

PXE,Pre-boot eXcution Environment

预启动执行环境，在操作系统之前运行

可用于远程安装、构建无盘工作站

服务端

运行DHCP服务，用来分配地址、定位引导程序

运行TFTP服务器，提供引导程序下载

客户端

网卡支持PXE协议

主板支持网络启动

### 4.1搭建PXE远程安装服务器

准备安装YUM源仓库

[root@localhost 桌面]#vim /etc/sysconfig/network-scripts/ifcnfig-eth0 //配置IP

[root@localhost 桌面]#service network restart //重启网络服务

[root@localhost 桌面]#mkdir /media/cdrom //创建cdrom目录

[root@localhost 桌面]#mount /dev/cdrom /media/cdrom //挂载光驱到/media/cdrom下

[root@localhost 桌面]#cd /media/cdrom/Packages/ //切换到光盘挂载点的包目录

[root@localhost Packages]# rpm -ivh vsftpd-2.2.2-11.el6_4.1.x86_64.rpm
//安装vsftpd软件

[root@localhost Packages]#mkdir /var/ftp/cent //在ftp默认路径下，创建一个cent目录

[root@localhost Packages]#cp * /var/ftp/cent/ //将当前目录中的所有内容复制到ftp目录下cent目录中

[root@localhost 桌面]#service vsftpd start //开启vsftpd服务

[root@localhost 桌面]#cd /etc/yum.repos.d/ //切换到yum源所在路径

[root@localhost yum.repos.d]#mkdir 1 //创建一个1目录

[root@localhost yum.repos.d]#mv *.repo 1 //将原有的源移动到1目录中

[root@localhost yum.repos.d]#vim local.repo //编写本地源文件

[base] //yum本地库名称

name=Red Hat Enterprise Linux //名称描述

baseurl=ftp://[当前服务器IP]/cent //指定本地源路径

enabled=1 //启用该本地源

gpgcheck=1 //gpg检测开启

gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release //指定gpg-key路径安装并启用TFTP服务

[root@localhost yum.repos.d] #yum -y install tftp-server //使用yum安装tftp服务

[root@localhost yum.repos.d] #vi /etc/xinetd.d/tftp //修改tfpt主配置文件

disable =no //更改此项yes为no

[root@localhost yum.repos.d]#service xinetd start //启动tftp服务 准备Linux内核、初始化镜像文件

用于PXE网络安装的Linux内核、初始化镜像文件可以从RHEL6系统光盘获得，分别为vmlinuz和initrd.img

[root@localhost yum.repos.d]#cd /media/cdrom/images/pxeboot //进入光盘镜像pxe引导目录下

[root@localhost pxeboot]#cp vmlinuz initrd.img /var/lib/tftpboot
//将内核文件和初始化文件拷贝到tftp引导目录下

### 4.2准备PXE引导程序、启动菜单文件

用于PXE网络安装的引导程序pxelinux.0,由软件包syslinux提供

[root@localhost pxeboot]#yum -y install syslinux
//安装网络安装的引导程序syslinux程序[root@localhost pxeboot]#cp
/usr/share/syslinux/pxelinux.0 /var/lib/tftpboot //将pxe引导程序拷贝到tftp引导

目录下

默认的启动菜单文件为default,应放置子tftp根目录的pxelinux.cfg子目录下

[root@localhost pxeboot]#mkdir /var/lib/tftpboot/pxelinux.cfg //创建默认启动菜单的目录

[root@localhost pxeboot]#vi /var/lib/tftpboot/pxelinux.cfg/default //编写默认启动菜单

default auto //默认为自动

prompt 1 //启用提示等待

label auto //自动执行标签

kernel vmlinuz //内核文件为vmlinuz

append initrd=initrd.img devfs=nomount ramdisk_size=8192 //确定初始化格式和大小

label linux text

kernel vmlinuz

append text initrd=initrd.img devfs=nomount ramdisk_size=8192

label linux rescue

kernel vmlinuz

append rescue initrd=initrd.img devfs=nomount ramdisk_size=8192

安装并启用DHCP服务

[root@localhost pxeboot]#yum -y install dhcp //安装DHCP软件包

[root@localhost pxeboot]#vi /etc/dhcp/dhcpd.conf //配置dhcp主配置文件

subnet 192.168.4.0 netmask 255.255.255.0 { //指定DHCP分配网段

……

option routers 192.168.4.254; //指定路由IP

option domain-name-servers 192.168.4.254,202.106.0.20; //指定DNS服务ip地址

range 192.168.4.100 192.168.4.200; //划定分配ip地址范围

next-server 192.168.4.254; //指定TFTP服务器地址

filename "pxelinux.0"; //指定PXE引导程序文件名

}

#service dhcpd start //重启DHCP服务

### 4.3客户端测试PXE网络安装

确保电脑网卡正常

在blos中将开机主引导设置为pxe引导

kickstart无人值守技术

创建应答文件，预先定义好各种安装设置

免去交互设置过程，从而实现全自动化安装

通过添加%post脚本，完成安装后的各种配置操作

桌面菜单"应用程序"-系统工具-Kickstart-保存/root/ks.cfg

[root@localhost pxeboot]#yum -y install system-config-kickstart //安装桌面配置应用程序

配置安装完成后执行列程序完成客户机ftp共享yum源仓库的连接

安装后脚本

%post --interpreter=/bin/bash

rm -f /etc/yum.repos.d/* //删除客户机原有yum源仓库

echo '[base] //yum仓库名

name=Red Hat Enterprise Linux //名称描述

baseurl=ftp://192.168.4.254/cent //yum源包路径

enabled=1 //启用本地源

gpgcheck=1 //启用gpg校验

gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release' >
/etc/yum.repos.d/rhel6.repo //指定gpg校验码路径

%end //结束

PXE+kickstart实现批量自动装机

[root@localhost pxeboot]#cp /root/ks.cfg /var/ftp/rhel6/ks.cfg
//将系统配置好的模板文件拷贝到，ftp共享的yum源路径下

修改启动菜单文件，调用应答文件

[root@localhost pxeboot]#vi /var/lib/tftpboot/pxelinux.cfg/default //修改默认启动路径

default auto //默认为自动

prompt 0 //取消提示等待

label auto //标记为自动

kernel vmlinuz //指定内核文件

append ks=ftp://192.168.4.254/rhel6/ks.cfg initrd=initrd.img devfs=nomount
ramdisk_size=8192 //附加模板路径、初始化格式和大小

\-----------------------------------------end--------------------------------------------
今天是周五了，大家开不开心！休息两天我们继续~

![v2-be7b3a919d240f369cef3d85db776fa7_hd.j](https://pic4.zhimg.com/80/v2-be7b3a919d240f369cef3d85db776fa7_hd.jpg)

  

