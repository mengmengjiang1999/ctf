**Kerberos是一种支持票证身份验证的安全协议。如果客户端计算机身份验证请求包含有效的用户凭据和服务主体名称 (SPN)，则 Kerberos
身份验证服务器将授予一个票证以响应该请求。然后，客户端计算机使用该票证来访问网络资源。在内部网络中，SPN扫描通过
查询向域控制器执行服务发现。这对于红队而言，可以帮助他们识别正在运行重要服务的主机，如终端、交换机、微软SQL等，并隐藏他们。此外，SPN的识别也是kerberoasting攻击的第一步。**

[Tim
Medin](https://twitter.com/TimMedin)在他的[Kerberos攻击](https://www.youtube.com/watch?v=HHJWfG9b0-E)演讲中很好地解释了SPN。[Sean
Metcalf](https://twitter.com/PyroTek3)还提供了一些有关SPN的资源，其中包括有关[Active
Directory服务主体名称](http://adsecurity.org/?page_id=183)的系列资源，可在本文结尾处找到。

## SetSPN

SetSPN是一个本地windows二进制文件，可用于检索用户帐户和服务之间的映射。该实用程序可以添加，删除或查看SPN注册。

    
    
    setspn -T pentestlab -Q */*

![1setspn-service-discovery.png](https://image.3001.net/images/20180608/15284138822222.png!small)

由于用户已经选择了密码，因此绑定到域用户帐户而不是计算机帐户的服务更可能被配置为弱密码，而对用户有规范名称的服务应该会成为Kerberoasting攻击的针对目标。以下SPN列表中，
**PENTESTLAB_001** 服务与用户帐户相关联。

![2setspn-spn-records.png](https://image.3001.net/images/20180608/1528413899509.png!small)

## GetUserSPNs

[Tim
Medin](https://twitter.com/TimMedin)开发了一个PowerShell脚本，它是[kerberoast](https://github.com/nidem/kerberoast)工具包的一部分，可以帮助我们查询活动目录，以发现仅与用户帐户相关联的服务。

    
    
    powershell_import /root/Desktop/GetUserSPNs.ps1

![3getuserspns-powershell-script.png](https://image.3001.net/images/20180608/15284139228051.png!small)

还有一个VBS脚本也是该工具的一部分，可以为我们提供相同的信息。该脚本可以通过使用本机Windows二进制cscript从Windows命令提示符执行。

    
    
    cscript.exe GetUserSPNs.vbs

## ![4getuserspns-vbs-script-cmd.png](https://image.3001.net/images/20180608/15284139386881.png!small)

## PowerShell AD Recon

除了[Tim Medin](https://twitter.com/TimMedin)开发的工具外，Sean
Metcalf也开发了各种PowerShell脚本来执行Kerberos侦察。这些脚本是[PowerShell AD
Recon](https://github.com/PyroTek3/PowerShell-AD-Recon)存储库的一部分，可以在Active
Directory中查询服务，例如Exchange，Microsoft
SQL，Terminal等。Sean将每个脚本绑定到一个特定的服务，具体取决于你想要发现的SPN。以下脚本将标识网络上的所有Microsoft SQL实例。

    
    
    powershell_import /root/Discover-PSMSSQLServers.ps1
    powershell_execute Discover-PSMSSQLServers

![5powershell-ad-recon-mssql-servers-discovery-via-metasploit.png](https://image.3001.net/images/20180608/15284139567474.png!small)

还可以使用PSMSExchangeServers脚本来查找Microsoft Exchange服务器。

    
    
    powershell_import /root/Discover-PSMSExchangeServers.ps1
    powershell_execute Discover-PSMSExchangeServers

![6powershell-ad-recon-exchange-servers-discovery-via-metasploit.png](https://image.3001.net/images/20180608/15284139745872.png!small)

枚举服务帐户很重要，因为这些帐户可能配置了弱密码。PasswordLastSet和LastLogon属性，可以为我们提供那些较有可能会设置弱密码的服务指示。

    
    
    powershell_import /root/Find-PSServiceAccounts.ps1
    powershell_execute Find-PSServiceAccounts

## ![7powershell-ad-recon-service-accounts-via-metasploit.png](https://image.3001.net/images/20180608/15284139934939.png!small)

## Empire

PowerShell Empire还有一个可显示域帐户的服务主体名称（SPN）的模块。

    
    
    usemodule situational_awareness/network/get_spn

![8empire-spn-module.png](https://image.3001.net/images/20180608/15284140386701.png!small)

这些服务将以下列格式呈现。

![9empire-spn-discovery.png](https://image.3001.net/images/20180608/15284140523085.png!small)

## PowerShellery

[Scott Sutherland](https://twitter.com/_nullbind)在将Get-SPN模块实现到Empire之前，已经创建了多个Powershell脚本作为[PowerShellery](https://github.com/nullbind/Powershellery)的一部分，可以为各种服务收集SPN。其中一些需要PowerShell
v2.0的环境，还有一些则需要PowerShell v3.0环境。

    
    
    Get-SPN -type service -search "*"

![10powershellery-getspn.png](https://image.3001.net/images/20180608/15284140723943.png!small)

结果我们也可以将其转换为表格的形式，以便于我们的浏览。

    
    
    Get-SPN -type service -search "*" -List yes | Format-Table

![11powershellery-getspn-table.png](https://image.3001.net/images/20180608/15284140943365.png!small)

这里我再告诉大家一个脚本，可以为我们获取UserSID，服务和实际用户。

    
    
    Import-Module .\Get-DomainSpn.psm1
    Get-DomainSpn

## ![12powershellery-get-domainspn.png](https://image.3001.net/images/20180608/15284141187384.png!small)

## Impacket

服务主体名称（SPN）也可以从未加入域的系统中发现，impacket工具包下的python版GetUserSPNs可以为我们做到这点。但是，无法使用基于token的身份验证，因此与Active
Directory进行通信需要获取有效的域凭证。

    
    
    ./GetUserSPNs.py -dc-ip 10.0.0.1 pentestlab.local/test

 **![13impacket-get-user-spn.png](https://image.3001.net/images/20180608/15284141371136.png!small)**

 **相关资源**

<https://adsecurity.org/?p=230>

<https://adsecurity.org/?p=1508>

<http://adsecurity.org/?page_id=183>

<https://github.com/nullbind/Powershellery>

<https://github.com/PyroTek3/PowerShell-AD-Recon>

 ***参考来源：[pentestlab](https://pentestlab.blog/2018/06/04/spn-discovery/)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**

