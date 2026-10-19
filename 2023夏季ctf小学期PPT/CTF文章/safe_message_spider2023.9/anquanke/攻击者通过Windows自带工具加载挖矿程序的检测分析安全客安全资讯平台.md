# 攻击者通过 Windows 自带工具加载挖矿程序的检测分析

阅读量 **236280**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-07-18 12:00:37

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Tony Lambert，文章来源：redcanary.com

原文地址：<https://redcanary.com/blog/cryptomining-enabled-by-native-windows-tools/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0147bb6a8177cb4d9d.jpg)

## 前言

我在职业生涯早期学到的一个教训是，技术专业人员通常会继承老问题。对于负责网络服务和安全的管理员来说尤其如此，因为他们继承了最大的问题：企业网络。随着网络的老化，网络往往变得更加难以安全和维护，而管理员常常实施新的安全措施，却发现他们的环境中已经存在一些邪恶的东西。

Red Canary的探测工程师对这个概念并不陌生。由于我们与事件响应伙伴的关系日益密切，Red
Canary通常部署在事件已经在进行中的环境中。尽管没有观察到最初的攻击，我们的网络事件响应小组([Cyber Incident Response
Team/CIRT](https://redcanary.com/blog/slaying-evil-cyber-incident-response-team/))可以提供一个全面的关于攻击者策略的观点，以加快补救。

在本文中，我将介绍一个场景，在这个场景中，我们与IR的一个合作伙伴一起进行搜索，以阻止正在进行的攻击。我还将分享检测策略，以发现在此事件中使用的攻击策略，以及越过陈旧的补丁管理建议的预防策略。

## 邪恶的最初迹象

当通过IR合作伙伴部署Red Canary时，事件处理程序通常会向检测工程团队简要介绍即将发生的事件的背景信息。在这种情况下，Red
Canary令人敬畏的Eric
Groce让我们知道，我们很快就会为一个由于恶意活动而无法使用网络的组织提供调查支持。这些问题严重影响了该组织的业务，我们将看到大量的事件。不久之后，我们看到了第一批事件的发生，从攻击者已经放置在设备上的持久性机制开始。

我们的第一个邪恶的迹象是应用白名单绕过技术，这种技术是在几年前因为我们的应用研究主任Casey
Smith而流行的。在这种情况下，运行Windows计划任务（Windows Scheduled
Task），执行Regsvr32.exe的实例以下载和执行代码。(这通常称为squiblydoo攻击。Casey在这篇[Atomic Red
Team](https://redcanary.com/blog/atomic-red-team-testing/)的文章中介绍了这次攻击。)

[](https://p2.ssl.qhimg.com/t01b97ba5c796d39e98.png)

下载的payload声称是PHP脚本文件，但其实是恶意脚本，进一步导致Windows命令处理程序(cmd.exe)产生PowerShell，然后Powershell执行Base64编码的命令来下载并执行第二个payload:antivirus.ps1。

[](https://p3.ssl.qhimg.com/t01f286e5751ffd82cb.png)

从这里开始，执行额外的PowerShell来检索以前存储为[Windows Management Instrumentation
(WMI)事件订阅](https://attack.mitre.org/wiki/Technique/T1084)的属性的代码。这与我们通常在“无文件(fileless)”恶意软件执行中看到的情况略有不同，后者通常使用Windows注册表项来存储PowerShell
payload，WMI类属性的使用更少，维护者更难检查和补救。

[](https://p2.ssl.qhimg.com/t01a4d07940f24880c4.png)

此时，我们已经可以看到，攻击者已经在组织的各个端点建立了相当大的持久性。我们收到了来自100多个主机的事件，显示了计划的任务执行和通过PowerShell检索WMI类属性。

## 挖矿开始

我们的下一个邪恶迹象来自WMI用于生成PowerShell的主机。我们可以基于PowerShell的父进程得出这样的结论：通过WMI生成的进程具有wmiprvse.exe的父进程。PowerShell命令再次使用base64进行编码，在解码之后我们可以看到一个复杂的脚本。

[](https://p0.ssl.qhimg.com/t0190185ad1a9a80c36.png)

攻击者创建了一个脚本，该脚本将检查工具的新版本，并在查询的版本号更改时尝试下载新的payload。在随后的脚本中，我们还观察到了查询端点的活动网络连接的攻击者，我们很快就发现了原因。对于每个具有已建立网络连接的进程，恶意PowerShell脚本都会执行findstr.exe的实例。这个内置的Windows实用程序用于搜索文件中由用户指定的文本字符串。在这种情况下，攻击者使用它来搜索与加密相关的字符串：“cryptonight”。

[](https://p4.ssl.qhimg.com/t017aee4d9b2ed5ebdd.png)

这种奇怪的行为是有意义的，一旦我们将其与我们在恶意挖矿程序实例中看到的行为进行比较。将挖矿程序作为payload部署的攻击者通常遵循以下模式：

  1. 将挖掘工具下载到端点。
  2. 检查端点，看看程序是否已经在运行。
  3. 终止任何现有的挖矿程序。
  4. 启动程序并继续。

在本例中，findstr.exe是在网络连接进程运行的每个二进制文件中执行的。如果这些进程中的任何一个包含字符串“cryptonight”，则恶意脚本将终止该进程并开始执行挖矿活动。

[](https://p2.ssl.qhimg.com/t01ecf15ce7f3f38d9a.png)

在Carbon Black (Cb)
Response中观察到的数据没有显示与PowerShell以外的这些活动相关的特定二进制文件，因此我们假设挖掘程序的加载方式对于CB响应来说是不可见的。后来，我们通过获取恶意PowerShell脚本并发现它使用一个版本的Invoke-ReflectivePEInjection(来自PowerSploit)将XMRig
Miner二进制文件加载到PowerShell中，从而确认了这一点。这个二进制文件使用Base64进行编码，并存储在脚本中，该脚本随后在运行时动态地提取它。通过使用反射注入，脚本加载挖掘程序二进制文件的方式避免了像LoadLibrary调用那样的Windows
API调用。这种技术通过对依赖Windows API调用的工具隐藏数据来了解加载了哪些二进制文件和代码库。

本质上，这个脚本包含了在运行时部署挖矿程序所需的所有内容，并通过这种对于大多数不结合某种形式的内存分析来检查PowerShell的内存空间的工具来说是不可见的方式部署，而不是信任API。

## 横向运动时间

在挖矿过程中，PowerShell脚本还开始扫描本地网络，查找445端口为服务器消息块(SMB)服务打开的主机。有读者可能会注意到我们以前见过这种模式。事实上，世界在2017年WannaCry
ransomware运动期间以及随后的几个月中都看到了这种模式，当时攻击者创造性地合并了WannaCry方法，并利用挖矿paload来分发WannaMare恶意软件。

[](https://p0.ssl.qhimg.com/t01acbac86da8199e31.png)

在挖矿活动的同时，我们开始注意到证书失窃的迹象。Powershell加载了两个动态链接库(DLL)，这两个库通常在凭证窃取攻击期间被观察到：samlib.dll和vaultcli.dll。此外，我们还发现PowerShell正在读取Windows本地安全授权进程(lsass.exe)的内存空间。

[](https://p1.ssl.qhimg.com/t016f02f6d00654a87c.png)

这些行为与我们观察到的攻击者使用MimiKatz窃取或滥用密码哈希的情况非常相似。当在这个上下文中拼凑在一起时，我们假设像MimiKatz这样的工具已经被加载到PowerShell中来收集合法的凭证，然后这些凭证被用来验证到其他端点，并传播一个加密的payload。这个策略显然有效，因为我们在环境中的200个主机上发现了类似的活动。

## 可能的第一感染者（Patient Zero）

在200多个检测中，只有一个端点在对抗性行为模式上表现出明显的偏离。在这个主机上，我们观察到从Java进程产生的奇怪命令。Windows命令行窗口(cmd.exe)的一个实例用于将编码的PowerShell命令写入VBScript中执行，命名脚本javaupdato.vbs。

[](https://p2.ssl.qhimg.com/t012a84ea247d2f0a7a.png)

回顾这个过程的Java父进程，该命令似乎是从运行有名为“WebHelpDesk”的应用程序的基于Java的Web服务器产生的。从提供的有关服务器的环境判断，我们能够识别它作为Solarwinds
Web Help
Desk服务器，这个服务器可从Internet上公开访问。在原始的遥测数据中，我们潜入Java父进程，发现了与Web服务器恶意联系的证据。攻击者上传了一个恶意Java类文件，并以类似于Web
shell活动的方式导致了cmd.exe的执行。反过来，cmd.exe编写并执行恶意脚本。

## Powershell：攻击者的选择工具

希望你已经注意到了一个特点：这个攻击者喜欢使用PowerShell。在这种情况下，恶意VBScript导致PowerShell下载的payload与在其他主机上所看到的略有不同。我们后来发现，payload包含一个漏洞，可以提升Web服务器上的权限。不需要利用这些漏洞，因为攻击者无意中获得了Web
Help Desk服务器的本地SYSTEM帐户运行进程的访问权限。当配置Web服务器时，它已被设置为在系统上最高管理员的安全上下文中运行！

在某种程度上，攻击者意识到了这一点，并使用另一种策略来触发在其他主机上看到的挖掘/横向移动payload的下载和执行。这一次，他们使用wmic.exe的实例，向进程提供恶意样式表，以触发PowerShell中的后续下载。

[](https://p3.ssl.qhimg.com/t017abf40c961b02403.png)

[](https://p2.ssl.qhimg.com/t0148dd320dc5873d5d.png)

## 检测策略：如何发现这些技术

如果没有适当的遥测技术，该组织的维护者就没有数据来检测这些技术，直到他们的网络陷入停顿。适当的检测需要以过程执行监控的形式进行遥测。防御者可以通过部署Endpoint
Detection and Response (EDR) 传感器(如Carbon Black Response或CrowdStrike
Falcon)来实现这一点。另一种可能是使用Sysinals的Sysmon来创建用于进程执行的Windows事件日志。通过使用来自入侵检测系统、Netflow或其他网络控件的遥测，可以观察到此事件的SMB网络扫描组件。

一旦遥测传感器就位，按照下面的检测策略找到并停止各种技术。

###  Regsvr32.exe

从这个事件中最容易发现的策略是涉及Regsvr32.exe的策略。所示的策略称为Squiblydoo攻击，通过在命令行中识别具有Web地址和字符串“scrobj.dll”的Regsvr32.exe实例，可以很容易地检测到该策略。

###  WMI或计划任务

可以通过查找wmiprvse.exe(WMI)或taskeng.exe(计划任务)的子进程来实现对通过WMI或计划任务产生的进程的监视。根据组织的大小和配置，这种检测策略可能非常麻烦，因此需要进行一些调整，以减少误报并突出恶意警报。

###  PowerShell

最佳检测策略是将进程执行监视与Windows事件日志控件相结合。如果将网络上的所有Windows客户端升级为使用PowerShell
v5而不是旧版本，则可以从其他安全和日志配置中受益。一个很好的起点是从Black Hill Information
Security获得有关[PowerShell日志(<https://www.blackhillsinfosec.com/powershell-logging-blue-team/>)]的资源。一旦生成包含PowerShell命令的日志，就可以对恶意脚本中涉及的单个行为创建检测功能。

###  恶意Web服务器开发

通过识别从Web服务器生成的可疑进程，可以观察到恶意Web服务器攻击。与WMI和计划任务监视一样，根据系统的配置，这种策略可能很麻烦。对于高精准度警报，你可以将检测功能调优到监视cmd.exe或该web服务器进程帐户中从web服务器生成的其他shell。大多数Web服务器都可以作为一个受到高度监视和审计的帐户来执行，所以要充分利用它！

## 测试您的检测覆盖率

想测试一下这些策略，看看你的控件是否遵守它们？这就是为什么我们创建了AtomRedTeam，这是一组小型的、高度可移植的测试的开源集合，对应[MITRE
ATT&CK](https://attack.mitre.org/wiki/Main_Page)框架中的相应技术。

查看以下 Atomic Red Team测试，看看你现有的控件是否可以检测到它们：

  * [Regsvr32.exe](https://github.com/redcanaryco/atomic-red-team/tree/master/atomics/T1117/T1117.md)
  * [Scheduled Task](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1053/T1053.md)
  * [PowerShell](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1086/T1086.md)
  * [WMI Event Subscription](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1084/T1084.md) Persistence
  * [Credential Dumping](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1003/T1003.md) (Think Mimikatz)

## 预防策略

如果你一直认为可以通过修补程序管理来防止此事件的部分发生，那么你是对的。我们已经写了很多文章来阐述[补丁管理和其他IT基础知识的重要性](https://redcanary.com/blog/5-it-fundamentals/)，大多数安全专业人员对这个建议并不陌生。补丁管理是一个很好的开始，但是对于这篇文章，我想深入探讨其他的预防策略：网络分割(network
segmentation)和Web服务器安全。

###  网络分割

防止像WannaCry和WannaMINE这样的快速传播的恶意攻击的一个关键防御方法是以一种将通信限制在段间已批准的信道的方式来分割你的网络。如果SMB扫描不应该被允许从你的营销办公室连接到网络的其余部分，禁止它并且用网络控制来监视它！

使用适当的访问控制列表进行网络分段可以防止主机将恶意传播到企业网络的其余部分。当正确分割时，快速传播的恶意程序将被限制在网络的单个部分，而不是像在无障碍的平面网络中那样在整个组织中传播。这对防御者很有帮助，因为它将事件与其他工作系统隔离开来。

尽管如此，SolarwinsWeb Help
Dest服务器的这种情况代表了一种特殊的情况。SolarWinds软件和其他IT管理工具通常位于网络的中心区域，在那里它们可以跨所有网段访问系统。这个位置是一个挑战，因为它允许一个主机成为一个潜在的矢量，来危害网络的所有部分。维权者应确保这些系统不能通过互联网公开访问。如果存在需要在组织网络之外使用IT管理工具的情况，请考虑使用虚拟专用网络(VPN)解决方案来提供安全的、经过身份验证的访问，这样攻击者就不会那么容易地扫描和危害这些系统。

###  Web服务器安全性

Web服务器的安全配置值得讨论，因为Web应用程序包含大量的现代企业软件。此外，许多这些Web应用程序都是为公众访问而设计的，这增加了所涉及的风险。为了让攻击者利用Web应用程序执行远程代码，可以使用利用漏洞或Web
shell功能来利用授予Web服务器进程的用户权限。防止利用Web
shell功能通常涉及测试和修补Web服务器和应用程序，但用户特权部分可以由了解其服务器需求的管理员管理。Linux
Web服务器上的Apache和Nginx可以很容易地配置为使用Web应用程序的非特权帐户，从而限制了利用漏洞造成的损害。

在Windows端，这有点困难，因为Web服务器用户的配置可能需要比Linux上更专业的站点或服务配置。一般的经验法则应该是使用在Web服务器主机或网络上任何其他系统上没有管理员权限的帐户。一旦你选择了一个非特权帐户，配置控件来监视该帐户执行的操作，从而监视您的Web服务器。

我们在这里已经给了特权帐户一个彻底的措施，所以我想提及为什么以Windows本地系统帐户运行一个Web服务器是特别糟糕的。这个帐户在Windows中拥有最高级别的特权，高于IT人员用于管理系统的本地管理员帐户。虽然这个帐户在每台计算机上都是唯一的，并且通常在其他主机上没有权限，但具有系统访问权限的攻击者可以在帐户下的单个主机上执行任何他们想要的操作。这包括可能窃取缓存在可用于在网络上横向移动的系统上的凭据。理论上，利用作为系统运行的服务可能导致攻击者获得域管理员(可以横向移动)的缓存凭据，并可能将合法用户锁在系统之外以防止补救。

要意识到你已经提供给互联网的Web服务器，并且用最少的特权加强它们的配置。此外，如果Web服务器提供对IT管理工具的访问，则不惜一切代价使其远离公共访问。通过要求使用带有身份验证的VPN来确保对这些管理资源的外部访问。

## 关键

我们希望深入调查这一事件可以帮助防御者理解为什么采取积极主动的措施来提高检测能力和预防是很重要的。如果你需要帮助[提高检测覆盖率](https://redcanary.com/solutions/detection-coverage/)，Red Canary在这里！

审核人：yiwang 编辑：边边

本文翻译自redcanary.com [原文链接](https://redcanary.com/blog/cryptomining-enabled-by-native-windows-tools/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **yimeng** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/151780](/post/id/151780)

安全客 - 有思想的安全新媒体

本文转载自: [redcanary.com](https://redcanary.com/blog/cryptomining-enabled-by-native-windows-tools/)

如若转载,请注明出处： <https://redcanary.com/blog/cryptomining-enabled-by-native-windows-tools/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [挖矿程序](/tag/挖矿程序)
  * [检测策略](/tag/检测策略)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t016fefd8e565877ad5.png) yimeng

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

