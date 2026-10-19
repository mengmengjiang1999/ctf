## Linux sudo权限提升漏洞复现（CVE-2021-3156)

### 漏洞背景：

Sudo是一个功能强大的工具，其允许普通用户执行root权限命令，大多数基于Unix和Linux的操作系统都包含sudo。

2021年01月26日，sudo被披露存在一个基于堆的缓冲区溢出漏洞（CVE-2021-3156，该漏洞被命名为“Baron
Samedit”），可导致本地权限提升。

当在类Unix的操作系统上执行命令时，非root用户可以使用sudo命令来以root用户身份执行命令。由于sudo错误地在参数中转义了反斜杠导致堆缓冲区溢出，从而允许任何本地用户（无论是否在sudoers文件中）获得root权限，无需进行身份验证，且攻击者不需要知道用户密码。

安全研究人员于1月26日公开披露了此漏洞，并表示该漏洞已经隐藏了近十年。

### 漏洞影响版本：

sudo 1.8.2-1.8.31p2

sudo 1.9.0-1.95p1

不受影响版本：sudo==>1.9.5p2

### 漏洞检测：

root<span class="label label-primary">@kali</span>:~# ls /etc/sudoers  
/etc/sudoers  
root@kali:~# sudo —version  
Sudo version 1.8.27

发现我们使用的sudo为1.8.27属于漏洞影响范围

### 复现过程

1.先创建一个kali普通权限的用户  
![](https://image.3001.net/images/20210305/1614906980_60418664762e3b4c16614.png!small)

2.下载CVE-2021-3156脚本

<https://haxx.in/CVE-2021-3156_nss_poc_ubuntu.tar.gz>

3.复制于kali中  
![](https://image.3001.net/images/20210305/1614906981_604186651cf18028a19a5.png!small)

4.解压

tar -xvzf CVE-2021-3156_nss_poc_ubuntu.tar.gz

![](https://image.3001.net/images/20210305/1614906981_60418665aa2096afd04c6.png!small)

5.进入CVE-2021-3156目录

cd CVE-2021-3156  
随后输入命令make &&./sudo-hax-me-a-sandwich 0  
![](https://image.3001.net/images/20210305/1614906982_60418666369ae56b2a35d.png!small)

会发现我们直接从普通用户到管理员用户

