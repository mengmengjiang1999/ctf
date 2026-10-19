![](https://image.3001.net/images/20190820/1566230569_5d5ac829eca58.png!small)

**今天给大家介绍的是一款名叫Commando
VM的渗透测试虚拟机，这是一款基于Windows的高度可定制的渗透测试虚拟机环境，目前该产品已发布了正式的发行版，可用于渗透测试和红队研究中。**

![](https://image.3001.net/images/20190820/1566230577_5d5ac831a4ec7.png!small)

##  工具安装

###  工具基础要求

> 1、Windows 7 Service Pack 1或Windows 10；
>
> 2、60 GB磁盘空间；
>
> 3、2 GB内存；

###  建议配置

> 1、Windows 10；
>
> 2、80GB以上磁盘空间；
>
> 3、4GB以上内存；
>
> 4、两个网络适配器；
>
> 5、启用主机虚拟化支持（需要Kali或Docker）

##  工具指令

###  标准安装

创建并配置一台新的Windows虚拟机

1、确保虚拟机已经更新至最新版本，此时可能需要检查更新，重启设备，并检查确认。

2、保存虚拟机镜像。

3、在新配置的虚拟机中下载并拷贝install.ps1。

4、以管理员权限打开PowerShell。

5、通过运行下列命令启用脚本执行：

    
    
    Set-ExecutionPolicy Unrestricted

6、 最后，按照下列顺序执行安装脚本：

    
    
    .\install.ps1

你还可以将密码作为参数来执行命令：

    
    
    .\install.ps1 -password <password>

该脚本将会设置Boxstarter环境，并处理Commando
VM环境的下载、安装何配置。在此过程中，用户需要输入管理员密码来确保安装过程中主机的自动化配置和重启。如果用户没有设置密码的话，我们只需要直接按下回车键即可。

###  自定义安装

1、从下列地址下载zip压缩文件：

    
    
    https://github.com/fireeye/commando-vm

2、解压缩文件，并编辑文件“${Env:UserProfile}\Downloads\commando-vm-master\commando-vm-master\profile.json”，并将需要使用的工具添加到“packages”列表中。

![](https://image.3001.net/images/20190820/1566230647_5d5ac877246d4.png!small)

3、以管理员权限打开PowerShell窗口，并启用脚本执行：

    
    
    Set-ExecutionPolicy Unrestricted –f

4、切换到解压后的项目目录：

    
    
    cd${Env:UserProfile}\Downloads\commando-vm-master\commando-vm-master\

5、 使用-profile_file参数执行安装脚本：

    
    
    .\install.ps1 -profile_file .\profile.json

###  安装新的工具包

Commando
VM使用了ChocolateyWindows包管理工具，可以帮助用户轻松安装新的工具包。比如说，以管理员权限运行下列命令，就可以在系统中部署GitHub桌面端工具了：

    
    
    cinst github

###  工具更新

运行下列命令即可将所有的工具包更新至最新版本：

    
    
    cup all

##  预装工具

###  活动目录工具

> Remote Server Administration Tools (RSAT)
>
> SQL Server Command Line Utilities
>
> Sysinternals

###  命令&控制

> Covenant
>
> PoshC2
>
> WMImplant
>
> WMIOps

###  开发者工具

> Dep
>
> Git
>
> Go
>
> Java
>
> Python2
>
> Python3 (default)
>
> Ruby
>
> RubyDevkit
>
> Visual Studio 2017 Build Tools (Windows 10)
>
> Visual Studio Code

###  Docker

> Amass
>
> Spider Foot

###  安全绕过

> CheckPlease
>
> Demiguise
>
> DefenderCheck
>
> DotNetToJScript
>
> Invoke-CradleCrafter
>
> Invoke-DOSfuscation
>
> Invoke-Obfuscation
>
> Invoke-Phant0m
>
> NotPowerShell (nps)
>
> PS>Attack
>
> PSAmsi
>
> Pafishmacro
>
> PowerLessShell
>
> PowerShdll
>
> StarFighters

###  漏洞利用

> ADAPE-Script
>
> APIMonitor
>
> CrackMapExec
>
> CrackMapExecWin
>
> DAMP
>
> EvilClippy
>
> Exchange-AD-Privesc
>
> FuzzySec'sPowerShell-Suite
>
> FuzzySec'sSharp-Suite
>
> Generate-Macro
>
> GhostPack
>
> Rubeus
>
> SafetyKatz
>
> Seatbelt
>
> SharpDPAPI
>
> SharpDump
>
> SharpRoast
>
> SharpUp
>
> SharpWMI
>
> GoFetch
>
> Impacket
>
> Invoke-ACLPwn
>
> Invoke-DCOM
>
> Invoke-PSImage
>
> Invoke-PowerThIEf
>
> JuicyPotato
>
> KaliBinaries for Windows
>
> LuckyStrike
>
> MetaTwin
>
> Metasploit
>
> Mr.Unikod3r's RedTeamPowershellScripts
>
> NetshHelperBeacon
>
> Nishang
>
> Orca
>
> PSReflect
>
> PowerLurk
>
> PowerPriv
>
> PowerSploit
>
> PowerUpSQL
>
> PrivExchange
>
> RottenPotatoNG
>
> Ruler
>
> SharpClipHistory
>
> SharpExchangePriv
>
> SharpExec
>
> SpoolSample
>
> SharpSploit
>
> UACME
>
> impacket-examples-windows
>
> vssown
>
> Vulcan

###  信息收集

> ADACLScanner
>
> ADExplorer
>
> ADOffline
>
> ADRecon
>
> BloodHound
>
> dnsrecon
>
> FOCA
>
> Get-ReconInfo
>
> GoBuster
>
> GoWitness
>
> NetRipper
>
> Nmap
>
> PowerView
>
> Devbranch included
>
> SharpHound
>
> SharpView
>
> SpoolerScanner
>
> Watson

###  Kali Linux

> kali-linux-default
>
> kali-linux-xfce
>
> VcXsrv

###  网络工具

> CitrixReceiver
>
> OpenVPN
>
> Proxycap
>
> PuTTY
>
> Telnet
>
> VMWareHorizon Client
>
> VMWarevSphere Client
>
> VNC-Viewer
>
> WinSCP
>
> Windump
>
> Wireshark

###  密码攻击

> ASREPRoast
>
> CredNinja
>
> DomainPasswordSpray
>
> DSInternals
>
> Get-LAPSPasswords
>
> Hashcat
>
> Internal-Monologue
>
> Inveigh
>
> Invoke-TheHash
>
> KeeFarce
>
> KeeThief
>
> LAPSToolkit
>
> MailSniper
>
> Mimikatz
>
> Mimikittenz
>
> RiskySPN
>
> SessionGopher

###  逆向工程

> DNSpy
>
> Flare-Floss
>
> ILSpy
>
> PEview
>
> Windbg
>
> x64dbg

###  其他实用工具

> 7zip
>
> AdobeReader
>
> AutoIT
>
> Cmder
>
> CyberChef
>
> ExplorerSuite
>
> Gimp
>
> Greenshot
>
> Hashcheck
>
> Hexchat
>
> HxD
>
> Keepass
>
> MobaXterm
>
> MozillaThunderbird
>
> Neo4jCommunity Edition
>
> Notepad++
>
> Pidgin
>
> ProcessHacker 2
>
> SQLiteDB Browser
>
> Screentogif
>
> ShellcodeLauncher
>
> SublimeText 3
>
> TortoiseSVN
>
> VLCMedia Player
>
> Winrar
>
> yEdGraph Tool

###  漏洞分析

> ADControl Paths
>
> Egress-Assess
>
> Grouper2
>
> NtdsAudit
>
> PwndPasswordsNTLM
>
> zBang

###  Web应用程序

> BurpSuite
>
> Fiddler
>
> Firefox
>
> OWASPZap
>
> Subdomain-Bruteforce
>
> Wfuzz

###  字典

> FuzzDB
>
> PayloadsAllTheThings
>
> SecLists
>
> Probable-Wordlists
>
> RobotsDisallowed

##  工具运行截图

##
![](https://image.3001.net/images/20190820/1566230898_5d5ac9723be5e.png!small)![](https://image.3001.net/images/20190820/1566230897_5d5ac971e9dff.png!small)![](https://image.3001.net/images/20190820/1566230898_5d5ac97201797.png!small)![](https://image.3001.net/images/20190820/1566230898_5d5ac9728cc14.png!small)

##  项目地址

CommandoVM：【[GitHub传送门](https://github.com/fireeye/commando-vm)】

 *** 参考来源：[fireeye](https://github.com/fireeye/commando-vm)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

