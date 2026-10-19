**译者：知道创宇404实验室翻译组**  
**原文链接：<https://www.ptsecurity.com/ww-en/analytics/pt-esc-threat-intelligence/incident-response-polar-ransomware-apt27/>**

### 前言

本次攻击是一个著名的亚洲APT组织所为，该组织涉嫌对政府目标进行网络间谍活动。在本文中，我们将分享这次攻击的调查结果。

### 事件顺序

对客户基础设施文件的大规模加密和赎金要求构成了调查的起点。大量损坏的文件本身就是一个非常明显的攻击指标，可以用来检测入侵。分析显示，客户的基础设施不是在三四天前（甚至在几小时前，就像在大规模袭击中经常发生的那样）遭到破坏，而是在2018年初受到的攻击。此外，攻击者最初感染的是受害者的外国办事处。随后，总部也遭到了攻击。

我们认为，外国办事处网络的最初入口点是网络中的一个易受攻击的服务器。2018年2月，在[ChinaChopper](https://en.wikipedia.org/wiki/China_Chopper
"ChinaChopper")和[TwoFace](https://unit42.paloaltonetworks.com/unit42-twoface-webshell-persistent-access-point-lateral-movement/ "TwoFace") web
shell的帮助下，攻击者获得了最初的访问权，并获得了持久性。

![](https://images.seebug.org/content/images/2020/11/4f488e7b-f598-45f2-bd7f-be3d71f6ae92.jpg-w331s)

攻击者使用[NBTScan](http://unixwiz.net/tools/nbtscan.html
"NBTScan")进行网络侦察，使用[PsExec](https://docs.microsoft.com/en-us/sysinternals/downloads/psexec
"PsExec")进行横向移动。他们获得了与[Mimikatz](https://github.com/gentilkiwi/mimikatz/releases
"Mimikatz")合作的资格。在某些情况下，我们能够检测已存档和上传的lsass进程的内存转储。因为使用Mimikatz很可能被终端安全软件阻止，攻击者被迫运行bruteforcing
offline。另一种方法是用[SMBTouch](https://github.com/3gstudent/Smbtouch-Scanner
"SMBTouch")扫描主机，寻找所谓的Eternal*
SMB漏洞，然后在可能的情况下运利用EternalBlue漏洞并感染计算机。攻击者在最感兴趣的主机上安装[SysUpdate](https://www.nccgroup.com/uk/about-us/newsroom-and-events/blogs/2018/may/emissary-panda-a-potential-new-malicious-tool/
"SysUpdate")和[HyperBro](https://unit42.paloaltonetworks.com/emissary-panda-attacks-middle-east-government-sharepoint-servers/ "HyperBro")后门是为了持久性访问。

外国办事处和总部都在进行加密货币挖掘。这种活动在一年半的时间里没有引起注意。在此期间，攻击者仅通过定期获取新账户或建立隧道链来维持他们的访问能力。我们认为，到2020年初，攻击者已经失去了访问权限（原因我们不知道）。2020年2月9日，我们在国外办事处的服务器上看到Web
Shell的使用。通过使用前面描述的工具，攻击者获得了总部域管理机构的证书。这次，他们删除了操作系统日志并停止了Shadow
Copy服务，从而使后续的事件分析更加复杂。

最终，在2020年4月29日，被攻击的域名管理员的账户被用来将Polar勒索软件推送到电脑上并运行它，进行加密用户文件并索要赎金。当我们的专家在2020年5月为客户提供帮助时，攻击者再次尝试通过在总部和办公室网络上的Web
Shell来重新控制基础设施，但是这次没有成功。

这里我们提供了一个时间线，以便更好地显示事件的顺序。

![](https://images.seebug.org/content/images/2020/11/e6541482-cc9d-4060-b12f-276b7ce53f0f.jpg-w331s)

CSIRT的目标包括恢复客户数据，其中包括属于不同部门的关键信息。我们对加密恶意软件进行了分析，从而可以恢复丢失的文件。

### Polar勒索软件

三个文件被发送到受害者的计算机：

  * GDFInstall.exe(MD5：13435101240f78367123ef01a938c560)是由Ubisoft签署的合法计算机游戏组件。

![](https://images.seebug.org/content/images/2020/11/3da66be4-5ae6-4dde-9874-13b0d8399f5d.jpg-w331s)

  * GameuxInstallHelper.dll(MD5：1fd8402275d42e7389f0d28b9537db0f)是运行GDFInstall.exe时导入的.NET DLL库（于2020年4月29日编译）。

![](https://images.seebug.org/content/images/2020/11/b2734dcf-adee-4e56-9dd3-5a9355239973.jpg-w331s)

这个组件实际上不是合法的。在导出GameExplorerInstallW符号后，将执行攻击者代码。这种在合法应用程序上下文中加载恶意代码的常用技术称为[DLL劫持](https://attack.mitre.org/techniques/T1574/001/
"DLL劫持")。

![](https://images.seebug.org/content/images/2020/11/63f1e18d-fec6-49bd-9f9d-deaebdc4dbc8.jpg-w331s)

读取文件`c:\programdata\Sysurl.Hex`（如果不存在，则从`c:\windows\system32\Sysurl.Hex`复制），然后使用密钥ABCSCDFRWFFSDJJHGYUOIj进行简单的XOR解密。最后用Base64解码，生成一个PE文件，该文件通过.NET加载并在内存中运行。有效负载和中间库在完成之前被删除。删除以标准（不安全）方式发生，如果及时停止磁盘访问并且信息未被覆盖，则可以恢复数据。

  * Sysurl.Hex是Polar勒索软件的加密副本。

这种有效负载调用程序（合法应用程序在其中加载恶意库，然后解密恶意组件并传递控制权）通常用于运行[PlugX](https://attack.mitre.org/software/S0013/
"PlugX")后门，在亚洲APT组织（如APT10，APT41，TA459和Bronze Union）中很常见。

我们更详细地分析勒索软件的解密和解码版本（MD5：841980b4ae02a4e6520ab834deee241b）。

根据GameuxInstallHelper.dll的启动方式，我们可以很快地猜出该文件也是使用.NET编译的可执行文件。编译日期为2020年4月9日。代码入口点是Polar命名空间中Encode类的Actions方法。

该恶意软件通过执行以下命令来删除系统事件日志和Shadow Copy副本：

    
    
    dism /online /enable-feature /featurename:NetFx3
    vssadmin.exe Delete Shadows /All /Quiet
    bcdedit /set {default} recoveryenabled no
    wmic shadowcopy delete
    wbadmin delete backup
    wbadmin delete systemstatebackup -keepversions:0
    bcdedit /set {default} bootstatuspolicy ignoreallfailures
    bcdedit /set {default} recoveryenabled no
    wevtutil.exe clear-log Application
    wevtutil.exe clear-log Security
    wevtutil.exe clear-log System
    wbadmin delete catalog -quiet
    wbadmin delete catalog -quiet
    wbadmin delete systemstatebackup

然后，它查找并停止以下进程：

![](https://images.seebug.org/content/images/2020/11/2678f8e3-1aee-4a1a-a349-8580b59f5887.png-w331s)

然后，该恶意软件会获取已连接磁盘的列表，并开始递归遍历目录，并跳过其中的一些：

  * C:\Windows 
  * C:\Program Files 
  * C:\Program Files (x86) 
  * C:\ProgramData 
  * C:\Python 
  * $SysReset 
  * $Recycle.Bin 
  * $RECYCLE.BIN 

它只关心具有以下扩展名的文件：

![](https://images.seebug.org/content/images/2020/11/82406df1-7150-4d20-b0b2-771b8015baa8.png-w331s)

在开始加密之前，该恶意软件会创建一个基本加密密钥，该密钥由以下字母表中随机选择的八个字符组成：`abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890*!=&?&/`。

根据文件大小，使用两种加密方法。每种方法都涉及不同的加密密钥。但是，这两种方法都使用基本加密密钥。

首先，我们将研究小于64052000字节（约61MB）的文件的加密方法。中间密码是基本加密密钥的SHA-256哈希和。它对所有文件都是相同的，并与硬编码的salt和1000次迭代一起使用，以生成加密密钥和初始化向量。每个密钥都用AES-CBC加密。.locked扩展名被添加到加密文件中。

![](https://images.seebug.org/content/images/2020/11/d9f275db-2783-4d2f-a461-654355ff7480.jpg-w331s)

较大的文件以不同的方式加密。在这种情况下，16字节的加密密钥是通过从基本加密密钥中获取前8个字节和从附加的硬编码数组中获取剩余8个字节形成的。随后是AES-ECB的[自定义](http://read.pudn.com/downloads415/sourcecode/crypt/1761761/AES.cs__.htm
"自定义")实现。16字节的块被加密，接下来的12800字节被跳过。结果是只加密了文件的一小部分，而不是整个文件。选择这种方法很可能是为了加快加密过程。加密文件的扩展名为.cryptd。

![](https://images.seebug.org/content/images/2020/11/317e8730-6bc8-4112-ba23-f6b6630f0ff9.jpg-w331s)

请注意，结果是创建一个新文件（在其中写入加密流）。原始文件被不安全地删除。因此，如果原始文件还没有被新信息覆盖，就不能从磁盘上恢复。

![](https://images.seebug.org/content/images/2020/11/d4aa6236-f741-43b9-82e3-d351829fe55c.jpg-w331s)

在每个包含加密文件的目录中，将创建一个名为readme_contact_alex.dali@iran.ir.htm的文件，其内容如下：

    
    
    Your companies cyber defense systems have been weighed, measured and have been found wanting!!!
    The breach is a result of grave neglect of security protocols
    All of your computers have been corrupted with Polar malware that has encrypted your files.
    We ensure that the only way to retrieve your data swiftly and securely is with our software.
    Restoration of your data requires a private key which only we possess
    Don't waste your time and money purchasing third party software, without the private key they are useless.
    It is critical that you don't restart or shutdown your computer.
    This may lead to irreversible damage to your data and you may not be able to turn your computer back on.
    To confirm that our software works email to us 2 files from random computers you will get them decrypted.
    readme_contact_alex.dali@iran.ir.htm contain encrypted session keys we need in order to be able to decrypt your files.
    The softwares price will include a guarantee that your company will never be inconvenienced by us.
    You will also receive a consultation on how to improve your companies cyber security
    If you want to purchase our software to restore your data contact us at:
    Pt34Jarmys@protonmail.com
    alex.dali@iran.ir
    
    We can only show you the door. You're the one who has to walk through it.
    
    Your personal installation key:*REDACTED*

勒索要求的文本与[MegaCortex](https://id-ransomware.blogspot.com/2019/05/megacortex-ransomware.html "MegaCortex")勒索软件使用的文本相似。

勒索要求包含基本加密密钥的修改版本。这个版本是通过使用RSA加密基本加密密钥（使用硬编码的1024字节公钥）并在Base64中对其进行编码而得到的。

文件加密完成后，恶意软件将映像（包含在可执行文件资源中）写入磁盘路径`c:\programdata\Rs.bmp`，并将其设置为桌面背景。

![](https://images.seebug.org/content/images/2020/11/c0f932c3-5184-4b92-9b1a-8fd1fca72278.jpg-w331s)

随后，该恶意软件重复删除系统事件日志和Shadow Copy副本的相同过程，该过程在开始时执行。然后它发送一个带有受害者计算机名称的HTTP
POST请求到位于hxxp://www.therockbrazil.com.br/assinaturas/logs.php的服务器。

![](https://images.seebug.org/content/images/2020/11/308c54e1-d234-45de-9efa-467c1f68fbdd.jpg-w331s)

### 如何解密文件

跟踪加密步骤的读者可能已经注意到，整个加密系统的安全性取决于我们所称的基本加密密钥。它的值用RSA-1024加密并放入赎金请求中。目前，没有既便宜又快速的方法来分解这样大的密钥。所以我们尝试了另一种策略。

请记住，基本密钥是从前面引用的字母表中随机抽取8个字符生成的。以下是实现的方式：

![](https://images.seebug.org/content/images/2020/11/a96ce901-e1e3-4fdb-8d38-63bc52f39468.jpg-w331s)

随机函数调用一次，不带任何参数。该调用返回一个随机数，该随机数的种子是从Environment.TickCount变量的值获取的。此变量为4个字节，存储自操作系统启动以来的毫秒数。

![](https://images.seebug.org/content/images/2020/11/d84c91e7-9993-4b43-9a95-0fc8731c2711.jpg-w331s)

所以要解码这些文件，我们只需要知道勒索软件运行时的正常运行时间（计算机开机的时间）。

大多数受影响的计算机不仅与公司网络断开了连接，而且关闭了以分析硬盘内容。因此，无法知道计算机的正常运行时间。操作系统日志包含关机和开机的时间。但在这种情况下，勒索软件会两次销毁这些日志。因此，我们无法找到任何线索表明受影响计算机本身的正常运行时间的可能值。

然而，幸运的是，[SCCM](https://en.wikipedia.org/wiki/Microsoft_System_Center_Configuration_Manager
"SCCM")被用于客户端基础设施，客户端代理运行在所有加密的计算机上。我们需要的信息被集中存储，并且没有被篡改：我们所需要的只是反复试验以选择正确的值。

![](https://images.seebug.org/content/images/2020/11/f8be8420-b984-4243-be2c-3600dea18404.jpg-w331s)

现在我们有了相对精确的正常运行时间值，我们需要确定勒索软件的运行时间。在最后，恶意软件会删除中间DLL库和加密勒索软件，但不会删除其进程用于执行恶意操作的合法可执行文件。换句话说，这个文件出现在系统上的时间应该是勒索软件运行的大概时间，大约在几秒钟之内。我们在一个普通的工作站上大约一分钟内成功地破解了基本加密密钥的精确值（大约几万次迭代）。然后我们可以解密剩下的文件。在一些情况下，我们在一开始就很难用暴力破解密钥。原因是时区设置不正确。

### 归因

我们提到了攻击者工具包中的SysUpdate和HyperBro后门。这些是APT27组织（也称为Bronze
Union、LuckyMouse、emissurary Panda或Iron
Tiger）使用的一些神秘的远程访问木马程序。该组织至少在2010年就开始活动。他们将注意力集中在国防和能源工业以及航空航天和制造业的政府目标上。最常见的是，原始攻击是通过利用漏洞，暴力破解凭据或利用Web服务器错误配置来破坏受害者的Web服务器的。尽管在战术、技术和程序(TTPs)以及泄密工具的使用上都有相似之处，但该团队的一些研究人员对将这些攻击归因于APT27持怀疑态度。

### 1.目标选择

媒体公司从未对APT27感兴趣。这与我们调查的结果是一致的：攻击者没有试图访问目标基础设施上的私人信息，而是运行软件以获取直接的经济利益。

### 2.加密货币挖掘和勒索软件

这是非典型的，不合适的软件，它可以迅速吸引人们的注意，破坏任何长期网络间谍计划。勒索软件在完成工作后“phones
home”的URL地址与APT27网络基础设施没有任何共同之处。当然，有些组织（如Lazarus和Winnti）将网络间谍与直接的财务动机相结合。因此，也许APT27正在扩大兴趣范围。或者，作为替代方案，该组织已经与其他攻击者达成协议，使用他们的软件来换取部分收益。为了便于将Polar归因于APT27，我们可以注意到有效负载、执行和命名的顺序：以类似的方式，加密的SysUpdate后门通常称为sys.bin.url，Polar勒索软件则称为Sysurl.Hex。然而，这也可能是一个错误的标志。

### 3.2018年和2020年的自动化

以下是2018年用于在计算机列表上自动安装加密货币矿工的脚本：

    
    
    @echo off
    for /f %%i in (c:\programdata\list.txt) do (
    net use \\%%i\c$  "*" /u:*\administrator
    copy c:\programdata\vmnat.exe \\%%i\c$\windows\system32\vmnat.exe
    SCHTASKS /Create /S %%i /u *\administrator /p "*" /tn * /tr "cmd.exe /c start c:\windows\system32\vmnat.exe" /sc onstart /RU SYSTEM
    schtasks /run /S %%i /u *\administrator /p "*" /tn *
    net use \\%%i\c$ /del
    net use * /del /Y
    )
    
    del vmnat.exe
    del list.txt
    del work.bat

这是用于在2020年从计算机列表中自动删除勒索软件的脚本：

    
    
    @echo off
    for /f %%i in (c:\programdata\list.txt) do (
       net use  \\%%i\c$ "*" /u:*\*
       if not errorlevel 1 (
         del \\%%i\c$\programdata\GameuxInstallHelper.dll
         del \\%%i\c$\programdata\GDFInstall.exe
         del \\%%i\c$\programdata\Sysurl.Hex
         net use \\%%i\c$ /del
      )ELSE (
        echo not access %%i >> c:\programdata\no_access.txt
      )
    )

（我们将敏感信息替换为“*”）

这些脚本在结构上显示出某些相似之处，并且在同一路径上具有相同的文件行循环。另一方面，缩进、脚本任务和文件命名是不同的。有些命令过于笼统，无法分辨，因为它们可以在在线搜索结果中找到并重新使用。

### 4.SysUpdate和hyperro后门的主体

在某些情况下，我们无法根据木马本身来确认特定后门的存在。我们根据独特的文件名和其他已确认的工具，确定了已在2018年使用的Superpro后门。我们通过查看进程转储内存中的C2地址和后门，确认了2020年使用的SysUpdate后门，这些地址和后门是在调查期间从一个与我们的客户无关的组织上传到[VirusTotal](https://www.virustotal.com/gui/file/b645ff7ca1bce2a9449bcf7378895022170ec8adba62ccf528e453667da2210a/details
"VirusTotal")的。

综上所述，这些相似之处可以指定APT27是罪魁祸首，但并不完全绝对。

### 结论

在本文中，我们描述了针对一家媒体公司的APT27攻击。这些网络犯罪分子通过在外国的一个办公室进入了该公司的总部。他们对基础设施的控制维持了两年。他们使用了曾经见过的公开可用和定制开发的工具。黑客们虽然没有改变他们的TTP，却选择了相当不寻常的软件来获利。用户数据被加密后，赎金要求被提出。勒索软件加密算法中的一个错误使我们得以恢复加密的文件。据我们所知，攻击者没有获得任何有价值的信息。

### MITRE TTPs

Tactic | ID | Name  
---|---|---  
Initial Access | T1190 | Exploit Public-Facing Application  
| T1199 | Trusted Relationship  
Execution | T1059 | Command and Scripting Interpreter: Windows Command Shell  
| T1053 | Scheduled Task/Job: Scheduled Task  
| T1047 | Windows Management Instrumentation  
Persistence | T1547 | Boot or Logon Autostart Execution: Registry Run Keys /
Startup Folder  
| T1574 | Hijack Execution Flow: DLL Search Order Hijacking  
| T1053 | Scheduled Task/Job: Scheduled Task  
| T1078 | Valid Accounts: Domain Accounts  
| T1078 | Valid Accounts: Default Accounts  
Privilege Escalation | T1068 | Exploitation for Privilege Escalation  
Defense Evasion | T1140 | Deobfuscate/Decode Files or Information  
| T1070 | Indicator Removal on Host: Clear Windows Event Logs  
| T1070 | Indicator Removal on Host: File Deletion  
| T1070 | Indicator Removal on Host: Timestomp  
Credential Access | T1003 | OS Credential Dumping: LSASS Memory  
Discovery | T1087 | Account Discovery: Domain Account  
| T1082 | System Information Discovery  
| T1049 | System Network Connections Discovery  
Lateral Movement | T1210 | Exploitation of Remote Services  
| T1570 | Lateral Tool Transfer  
| T1021 | Remote Services: SMB/Windows Admin Shares  
Collection | T1560 | Archive Collected Data: Archive via Utility  
| T1005 | Data from Local System  
| T1119 | Automated Collection  
| T1039 | Data from Network Shared Drive  
Command and Control | T1071 | Application Layer Protocol: Web Protocols  
| T1132 | Data Encoding: Standard Encoding  
| T1573 | Encrypted Channel: Symmetric Cryptography  
Exfiltration | T1020 | Automated Exfiltration  
| T1041 | Exfiltration Over C2 Channel  
Impact | T1486 | Data Encrypted for Impact  
  
### IOCs

**ChinaChopper:**

2ce60073c09887f9e3a482097294e17d  
5bc0d6918e03a92f04b3dfc21b619c7f  
73717a2f9bfe19ccdad541bec1fa2b69  
82a8470534d74c9c5c0d84071eb0a703  
b89e96e2ea8dd6fdb438f7d5b8ecf60c

**TwoFace:**

581c331d41ef5f5df99ae0d16b2cebf0  
ff2693903a1049984745e79381e9ed7e

**SysUpdate:**

3c1981991cce3b329902288bb2354728  
43a2c2fb8d52dc1835ac18516b13aff1  
4b5484e3de5c5a2e60fcee50d04183d6

**SysUpdate C &C:**

103.59.144[.]183（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=103.59.144.183
"ZoomEye搜索结果")）  
95.179.189[.]33（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=95.179.189.33
"ZoomEye搜索结果")）

**NBTScan:**

f01a9a2d1e31332ed36c1a4d2839f412

**SMBTouch:**

b50fff074764b3a29a00b245e4d0c863

**PsExec:**

aeee996fd3484f28e5cd85fe26b6bdcd

**Termite:**

dc92496358b8e67568a35b861ba1804e39e3d36b

**Dsquery:**

3583d7c971de148a1ffb3302d1510ef1

**EternalBlue:**

8c80dd97c37525927c1e549cb59bcbf3

**frsocks:**

da0c13d834cafc010bec1afa2d76196ced71e661

**Mimikatz:**

449da3d7405c2c79fa55bd7973096e28  
0078ff05c20689f40ea9cb8c47fcfb2e52cdc3a9

**BitMiner:**

5430039162e58c44f9a5941295b55fba

**Polar:**

841980b4ae02a4e6520ab834deee241b

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1414/>

