![](https://image.3001.net/images/20210805/1628163644_610bce3c3ec1a3e670734.jpg!small)

往期文章：

> [《内网渗透测试：初探远程桌面的安全问题》](https://www.freebuf.com/articles/network/276242.html)
>
> [《内网渗透测试：登录远程桌面的别样姿势》](https://www.freebuf.com/articles/network/280817.html)
>
> [《内网渗透测试：基于文件传输的 RDP
> 反向攻击》](https://www.freebuf.com/articles/network/280818.html)
>
> [《内网渗透测试：获取远程桌面连接记录与 RDP
> 凭据》](https://www.freebuf.com/articles/network/280819.html)

## 前言

如今，在很多组织机构内部，针对 DMZ 或隔离网络区域内的计算机设备，为了限制其它接入端口风险，通常只允许这些设备开启 3389
端口，使用远程桌面来进行管理维护。那么我们能不能利用这个 3389 端口的 RDP 服务建立起一条通向内网的代理隧道呢？当然可以，下面就引出我们今天的主角
—— SocksOverRDP。

> 文中若有不当之处，还请各位大佬师傅们多多点评。
>
> 我的博客：<https://whoamianony.top/>

## SocksOverRDP

![20210805192108.png](https://image.3001.net/images/20210805/1628163203_610bcc8301502ab61ad21.png!small)

项目地址：<https://github.com/nccgroup/SocksOverRDP>

SocksOverRDP 可以将 SOCKS 代理的功能添加到远程桌面服务，它使用动态虚拟通道，使我们能够通过开放的 RDP
连接进行通信，而无需在防火墙上打开新的套接字、连接或端口。此工具在 RDP 协议的基础上实现了 SOCKS 代理功能，就像 SSH
的`-D`参数一样，在建立远程连接后，即可利用 RDP 协议实现代理功能。

该工具可以分为两个部分：

![image-20210805164336410](https://image.3001.net/images/20210805/1628163203_610bcc835b0d9e4672b02.png!small)

> 第一部分是一个`.dll`文件，需要在 RDP 连接的客户端上进行注册，并在每次运行时将其加载到远程桌面客户端 mstsc 的上下文运行环境中。
>
> 第二部分是一个`.exe`可执行文件，它是服务端组件，需要上传到 RDP 连接的服务器并执行。

以下是该工具的运作原理：

> If the DLL is properly registered, it will be loaded by the mstsc.exe
> (Remote Desktop Client) or Citrix Receiver every time it is started. When
> the server executable runs on the server side, it connects back to the DLL
> on a dynamic virtual channel, which is a feature of the Remote Desktop
> Protocol. After the channel is set up, a SOCKS Proxy will spin up on the
> client computer, by default on 127.0.0.1:1080. This service can be used as a
> SOCKS5 Proxy from any browser or tool.

大致原理是，当 SocksOverRDP-Plugin.dll 在 RDP 客户端上被正确注册后，每次启动远程桌面时都会由 mstsc 加载。接着，当
SocksOverRDP-Server.exe 被上传到 RDP 服务端上传并执行后 ，SocksOverRDP-Server.exe
会在动态虚拟通道上回连 SocksOverRDP-Plugin.dll，这是远程桌面协议的一个功能。虚拟通道设置完成后，SOCKS 代理将在 RDP
客户端计算机上启动，默认为 127.0.0.1:1080。此服务可用作任何浏览器或工具的 SOCKS5
代理。并且服务器上的程序不需要服务器端的任何特殊特权，还允许低特权用户打开虚拟通道并通过连接进行代理。

## 通过 SocksOverRDP 搭建 SOCKS5 代理

测试环境如下：

![image-20210805190918631](https://image.3001.net/images/20210805/1628163203_610bcc838edd692ea5b35.png!small)

右侧为一个内网环境，其中 Windows Server 2012 是一个 Web
服务器，有两个网卡，分别连通内外网。假设此时攻击者已经通过渗透手段拿下了这台 Web
服务器，需要设置代理进入内网继续对内网进行横向渗透。但是由于防火墙的规则等原因，只允许 TCP/UDP 3389 端口可以进行通信，所以我们只能尝试利用用
RDP 协议来建立通讯隧道。

### 攻击端

在攻击机上需要安装注册 SocksOverRDP-Plugin.dll。首先我们将 SocksOverRDP-Plugin.dll
放置到攻击机的任何目录中，但是为了方便我们可以将其放置到`％SYSROOT％\system32\`或`％SYSROOT％\SysWoW64\`目录下。

然后使用以下命令对 SocksOverRDP-Plugin.dll 进行安装注册：

![1628163364_610bcd24b36b345c65fac.png!small?1628163364575](https://image.3001.net/images/20210805/1628163364_610bcd24b36b345c65fac.png!small?1628163364575)

![image-20210805171250365](https://image.3001.net/images/20210805/1628163203_610bcc83ef0da7668b27d.png!small)

如上图所示，注册成功。但是由于 SocksOverRDP 建立的 SOCKS5 代理是默认监听在 127.0.0.1:1080
上的，所以只能从攻击机本地使用，为了让攻击者的 Kali 也能使用搭建在攻击机 Windows 10 上的 SOCKS5 代理，我们需要修改其注册表，将
IP 从 127.0.0.1 改为 0.0.0.0。注册表的位置为：

    
    
    HKEY_CURRENT_USER\SOFTWARE\Microsoft\Terminal Server Client\Default\AddIns\SocksOverRDP-Plugin

![image-20210805183835850](https://image.3001.net/images/20210805/1628163204_610bcc844a5feb9e4fec5.png!small)

然后启动远程桌面客户端 mstsc.exe 连接目标 Web 服务器 Windows Server 2012：

![image-20210805184009799](https://image.3001.net/images/20210805/1628163204_610bcc84a6ea3eb32d979.png!small)

如上图所示，弹出了一个提示说 SocksOverRDP 成功启动，当服务端的可执行文件运行后即可在攻击机的 1080 端口上启动 SOCKS5 代理服务。

### 服务端

远程桌面连接成功后，将服务端组件 SocksOverRDP-Server.exe 上传到 Windows Server 2012 上：

![image-20210805172727184](https://image.3001.net/images/20210805/1628163205_610bcc854e5382e972708.png!small)

直接运行 SocksOverRDP-Server.exe 即可：

![image-20210805172901544](https://image.3001.net/images/20210805/1628163205_610bcc85d9f585ab8e4ae.png!small)

此时便成功搭建了一个 SOCKS5 代理隧道，查看攻击机 Windows 10 的端口连接状态发现已经建立连接：

![image-20210805173743464](https://image.3001.net/images/20210805/1628163206_610bcc868dd80c48d2b0e.png!small)

然后在攻击机 Kali 上配置好 proxychains：

![image-20210805184447817](https://image.3001.net/images/20210805/1628163206_610bcc86cf84508bc301e.png!small)

此时便可以通过代理访问到内网的主机 DC 了。如下所示，成功打开了 DC 的远程桌面：

    
    
    proxychains4 rdesktop 192.168.93.30

![image-20210805184342519](https://image.3001.net/images/20210805/1628163207_610bcc8770141e651d6fc.png!small)

探测内网主机 DC 的端口开放情况：

    
    
    proxychains4 nmap -sT -Pn 192.168.93.30 -p 445

![image-20210805185347989](https://image.3001.net/images/20210805/1628163211_610bcc8b023afbc4ec1c9.png!small)

先该主机开启了 445 端口，我们可以直接用 smbexec.py 连接：

    
    
    proxychains4 python3 smbexec.py whoamianony/administrator:Whoami2021@192.168.93.30

![image-20210805190126459](https://image.3001.net/images/20210805/1628163212_610bcc8c0a0560007b37f.png!small)

如上图所示，成功拿下内网主机 DC。

## Ending......

![174486](https://image.3001.net/images/20210805/1628163213_610bcc8d2b615cda4b266.jpeg!small)

文中若有不当之处，还请各位大佬师傅们多多点评。

我的博客：<https://whoamianony.top/>

## 参考

>
> [https://github.com/nccgroup/SocksOverRDP﻿](https://github.com/nccgroup/SocksOverRDP)

