# Sense

 **靶机简介**

![](https://image.3001.net/images/20220111/1641912403_61dd9853cdef5a0288ba3.jpg!small)

靶机地址：https://app.hackthebox.com/machines/111  
靶机难度：easy  
靶机发布时间：22 Oct 2017  
靶机简介：Sense是一个已经retired的机器，枚举是这个盒子中的一个重要因素，虽然简单但是需要大量的耐心，所以请确保您不会忽视任何东西！

### 请注意：

本文仅用于技术讨论与研究，文中的实现方法切勿应用在任何违法场景。如因涉嫌违法造成的一切不良影响，本公众号及作者概不负责。

>  **0x01 信息收集**

1、靶机ip

    
    
    10.10.10.60
    

2、端口与服务

    
    
    nmap -sC -sV -Pn -O -oA initial 10.10.10.60
    

  * -sC: 运行默认nmap脚本

  * -sV: 检测服务版本

  * -O: 检测操作系统

-oA: 输出保存在namp文件夹中  
![](https://image.3001.net/images/20220111/1641912405_61dd98551998cfb019d78.jpg!small)可以看到以下扫描结果：

  * 80端口：http服务

  * 443端口：https服务

80端口会跳转到443端口。

>  **0x02 漏洞探测与利用**  
>  80/443端口：

显示网页是pfSense的登录界面。pfSense是一个开源防火墙，因此在枚举过程中要更加小心。如果我们做任何非常可疑的事情（例如暴力攻击），可能会受到防火墙的阻止，之后的尝试将毫无用处。  
![](https://image.3001.net/images/20220111/1641912407_61dd9857480b70fe20ab6.jpg!small)1、枚举目录：

    
    
    gobuster -u https://10.10.10.60/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -e
    

![](https://image.3001.net/images/20220111/1641912408_61dd9858c9f9616ca0efb.jpg!small)

检查了所有目录，它们要么是404，要么重定向回登录页面。考虑使用-x选项来查找特定的文件扩展名。例如.php, .txt, .sh, .bak等扩展。

    
    
    gobuster -u https://10.10.10.60/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -e -x txt
    

![](https://image.3001.net/images/20220111/1641912409_61dd9859c81c709983360.jpg!small)找到两个txt文件，分别是-changelog.txt和system-users.txt，打开看一下：  
![](https://image.3001.net/images/20220111/1641912410_61dd985ac89dcdc4ecf34.png!small)意思是2/3的漏洞已经修复。  
![](https://image.3001.net/images/20220111/1641912411_61dd985bbabff1b7e2d15.jpg!small)pfsense的默认用户名和密码是：admin/pfsense  
![](https://image.3001.net/images/20220111/1641912412_61dd985cb0cd0624bee6d.jpg!small)所以这里找到一个用户名及密码：  
rohit/pfsense

2、登录后台  
![](https://image.3001.net/images/20220111/1641912413_61dd985da3dc17c59ed42.jpg!small)![](https://image.3001.net/images/20220111/1641912414_61dd985ec849a77cd56ba.jpg!small)可以看到版本号：

    
    
    Version 	2.1.3-RELEASE (amd64)  
    built on Thu May 01 15:52:13 EDT 2014  
    FreeBSD 8.3-RELEASE-p16
    Unable to check for updates.
    

在google上搜索该版本号的漏洞利用：  
![](https://image.3001.net/images/20220111/1641912416_61dd9860db3513ce7ba11.jpg!small)

发现pfsense<2.1.4版本有一个命令注入漏洞，将代码保存为exploit.py

用法：

    
    
    usage: exploit.py [-h] [--rhost RHOST] [--lhost LHOST] [--lport LPORT]
                      [--username USERNAME] [--password PASSWORD]
    

![](https://image.3001.net/images/20220111/1641912419_61dd9863545a0467e4a0a.jpg!small)可以获取root权限。  
user flag：  
![](https://image.3001.net/images/20220111/1641912421_61dd98654791dd7a79b66.jpg!small)root
flag：  
![](https://image.3001.net/images/20220111/1641912422_61dd98661107796352148.jpg!small)

