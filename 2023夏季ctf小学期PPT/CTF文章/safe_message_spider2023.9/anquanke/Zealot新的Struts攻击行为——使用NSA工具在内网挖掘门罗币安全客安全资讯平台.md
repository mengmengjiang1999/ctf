# Zealot：新的Struts攻击行为——使用NSA工具在内网挖掘门罗币

阅读量 **196348**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-12-19 12:05:25

 **x**

##### 译文声明

本文是翻译文章，文章原作者 MAXIM ZAVODCHIK, LIRON SEGAL，文章来源：f5.com

原文地址：<https://f5.com/labs/articles/threat-intelligence/cyber-security/zealot-new-apache-struts-campaign-uses-eternalblue-and-eternalsynergy-to-mine-monero-on-internal-networks>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_673_/t01a06c772fbf4290c6.jpg)

> F5威胁研究人员发现了一个新的Apache Struts攻击,
> 此行动是一个复杂的多阶段攻击，利用NSA的EternalBlue和EternalSynergy攻击内部网络。依据包含NSA漏洞的python脚本的压缩文件名，我们将此次攻击命名为“Zealot”。在继续研究此次攻击行动时，我们会持续更新。这是迄今为止我们所了解到的：  
>  1、新的Apache Struts行动，Zealot针对Windows和Linux系统。  
>  2、Zelot是一个复杂的，高度混淆和多阶段的攻击  
>  3、Zelotot攻击服务器所利用的漏洞：  
>  CVE-2017-5638：Apache Struts Jakarta Multipart Parser漏洞  
>  CVE-2017-9822：DotNetNuke（DNN） CMS漏洞  
>  4、此攻击利用EternalBlue和EternalSynergy工具进行内网横向移动  
>  5、它具有高度混淆的Windows PowerShell 客户端和Linux / OS
> X的Python客户端，似乎基于EmpireProject开发框架  
>  6、Zelot目前正在挖掘Monero，一个越来越受网络犯罪者喜爱的加密货币

## 引言

当F5的威胁研究人员首次发现名为Zealot的新Apache
Struts攻击时，它似乎是使用CVE-2017-5638（2017年3月首次发现）攻击服务器的众多攻击行动之一。2017年7月发现它也利用了DotNetNuke（DNN）漏洞（CVE-2017-9822）。Zealot使用DNN和Struts漏洞攻击Windows和Linux系统。如果这些请求是分开发送的，那么它们将是两个独立的使用相同payload的行动。当仔细观察高度混淆payload时，我们发现了一个更复杂的多阶段攻击，此攻击具有利用NSA泄露的EternalBlue和EternalSynergy工具进行横向移动的能力。  
Zealot目前致力于挖掘Monero币，然而攻击者可以使用被控制的系统来做任何事。

## Apache Struts Jakarta Multipart Parser (CVE-2017-5638)漏洞利用

攻击始于攻击者扫描网页并发送两个HTTP请求，其中一个请求就是利用了臭名昭着的Apache
Struts漏洞。同大多数针对Windows或Linux平台的Apache Struts攻击类似，Zealot配备了两种payload。

图1: 针对STRUTS的HTTP请求

如果服务器存在漏洞，它将执行JAVA代码来确定操作系统。

## Linux上的利用

对于Linux，它将在后台利用“nohup”执行命令（即使在shell关闭后，该命令也允许进程运行）。该命令下载并执行一个bash脚本。

###  下载和执行

Zealot会尝试使用几种方法获取脚本。它尝试通过TCP
socket连接到远程服务器，并将接收到的数据直接重定向到shell。如果失败，就使用“curl”和“wget”工具下载文件“larva”，然后在一秒钟后执行并删除。

图2: 获取和执行“larva”bash脚本的shell命令

这些下载和执行技术稍后将应用于所有的恶意软件，并被其作者称为“tcp”和“http”下载功能。

###  “larva”

下载的bash脚本通过测试是否存在预定义的互斥体（“21914”）来检查机器是否已经感染。如果存在，它将执行结束。

图3: 测试目标感染与否

然后它将使用相同的下载和执行方式来获取名为“mule”的加密矿工文件。

图4: “larva” 脚本下载“mule”

它将利用管道向python进程传送一段使用base64编码的python代码。

图5: 嵌入base64 编码的Python代码

###  Little Snitch和未知的功能

一旦解码，可以看到python代码检查是否正在运行一个“Little Snitch”进程（macOS的防火墙解决方案），如果是的话，执行将终止。

图6: Little Snitch 防火墙检查

如果没有防火墙程序运行，它将向C＆C服务器发送一个请求，以获取下一段python代码。  
**注意：在我们进行这项研究的时候，由于服务器宕机，我们无法收集到后续的Python代码。目前攻击者并没有针对MAC。攻击者使用EmpireProject框架（请参阅下面的部分），该框架为Linux和OS
X平台生成一个python客户端程序，Little
Snitch的检查则是这个python客户端程序的一部分。目前，该攻击在Windows使用加密矿工MZ，Linux使用ELF，在OS
X平台则没有可用的二进制文件。**  
这个脚本与服务器通信的方式超越常见僵尸网络的复杂程度，所以它引起了我们的注意。 向C＆C发送请求时，将添加特定的User-Agent和Cookie，这意味着任何试图从自己的浏览器或工具访问C＆C的人（如我们的研究人员）都不会得到与恶意软件相同的响应。

图7: 发送至C&C 的具有特殊HTTP头部值的请求

接收到的响应也很奇怪，因为内容是加密的，所以正常的网络检测设备看不到。只有脚本有key。响应是使用RC4算法加密的另一段Python代码，一旦解密，就会执行。

图8: 应用RC4解密HTTP响应

## Windows上的利用

如果检测到的操作系统是Windows，则STRUTS payload将以隐藏模式启动PowerShell执行base64编码的代码。
需解码两次，其结果是另一个混淆的脚本。一旦解除混淆，它则是一段URL，用来从另一个地址下载文件。

图9: 经过2层base64解码后的混淆脚本

###  Crypto-Miner的反射DLL注入

下载的文件是一个更多混淆的PowerShell脚本“scv.ps1”。  
它将下载矿工恶意软件并运行。然后，它将利用反射式DLL注入技术将恶意软件注入到PowerShell进程中，以实现隐身的目的。

###  在内部网络中传播

如果Windows主机没有安装python
2.7，它将下载python安装程序并进行安装，然后下载启动传播到内网的python模块（“probe.py”）。该脚本使用“pyminifier”（Python代码最小化、混淆和压缩的公共包）进行混淆。原始脚本使用base64编码，压缩了20次。

图10: 使用“pyminifier”混淆Python脚本

“probe.py”脚本首先确定平台是32位还是64位，以及底层操作系统。

图11: 变量名和值源自“星际争霸” 游戏

如果变量名和它们的值听起来很熟悉，那么你可能就是传说中的星际争霸游戏的粉丝。Zealot, Raven, Observer,
Overlord都是游戏中的角色。  
由于在Windows机器上运行，它将下载“zealot.zip”和“raven64.exe”文件。“zealot.zip”包含攻击者使用“pyminifier”进行混淆所需的多个python脚本和库。

图12: “zealot.zip”

zealot.py – 执行EternalBlue和EternalSynergy工具的主脚本  
a0.py – Windows 7 EternalSynergy漏洞 shellcode  
a1.py – Windows 7 EternalBlue漏洞利用，接收一个shellcode作为参数。  
a2.py – Windows 8 EternalBlue漏洞利用，接收一个shellcode作为参数。  
m.py – SMB协议包装  
data – 包含2个shellcode文件：  
shellcode_win7 — a1.py所需  
shellcode_win8 — a2.py所需  
所有其他文件均为已知的Python包。  
“raven64.exe”扫描内网的445端口，并调用zealot.py在Windows 7和Windows
8注入三个不同的shellcode利用EternalSynergy和EternalBlue工具。

图 13: “zealot.py” 执行 NSA Eternal 漏洞

一旦注入的shellcode成功执行，它将启动PowerShell从另一个不同的服务器来下载相同的“scv.ps1”。

图 14: Win8平台Shellcode（内含编码后PowerShell 代码 ）

与EternalBlue工具不同，EternalSynergy工具有内置的shellcode，它使用外部文件作为它们的shellcode（“data”文件夹中）。这两个shellcode均包含PowerShell命令。与EternalBlue
shellcode不同的是，EternalSynergy试图从另一台服务器上下载并执行名为“minerd_n.ps2”的PowerShell脚本。

## 挖矿程序

“mule”恶意软件是Monero币的挖矿软件。由于高匿名性，Monero币已成为网络犯罪的首选。目前此地址门罗币价值大约是8,500美元，
攻击者一共收货多少利润目前还不清楚。

图15: Mule 恶意软件挖矿参数

## 利用现成的工具

在对已部署的脚本进行了更多的研究之后，Zealot攻击者似乎利用了EmpireProject，这是一个PowerShell和Python利用框架。

图16: github上EmpireProject的logo及简介

## DotNetNuke 漏洞利用 (CVE-2017-9822)

Zealot攻击者发送的另一个请求是利用基于ASP.NET的内容管理系统DotNetNuke，通过易受攻击的DNNPersonalization
cookie（CVE-2017-9822）发送序列化对象。

图 17: 针对DNN的HTTP请求

为了获得任意的代码执行，攻击者使用ASP.NET“ObjectDataProvider”和“ObjectStateFormatter”来嵌入另一个对象并调用一个shell。
“ObjectStateFormatter”使用了二次混淆，因为嵌入对象是base64编码格式。被调用的shell将执行一个base64编码的PowerShell脚本，这个脚本是通过Apache
Struts漏洞投递的。

图18: ASP.NET序列化对象，包括编码的PowerShell payload

## 总结

Zealot似乎是第一个使用NSA工具在内网中传播的Struts攻击行动。其他类似NotPetya和WannaCry的勒索软件，以及Adylkuzz
cryptominer，都是通过直接扫描公网SMB端口并利用ShadowBrokers的NSA工具来攻击中小企业。
然而，Zealot行动正在开启新的攻击途径，通过Web应用程序在内网传播恶意软件。我们目前在Zealot中所观察到的复杂程度正在使我们相信，此次行动是由高于普通僵尸网络分发者几个级别的攻击者执行的。

## 参考链接

1 <https://nvd.nist.gov/vuln/detail/CVE-2017-5638>  
2 <https://nvd.nist.gov/vuln/detail/CVE-2017-9822>  
3 <https://github.com/EmpireProject>  
4 <https://www.proofpoint.com/us/threat-insight/post/adylkuzz-cryptocurrency-mining-malware-spreading-for-weeks-via-eternalblue-doublepulsar>

本文翻译自f5.com [原文链接](https://f5.com/labs/articles/threat-intelligence/cyber-security/zealot-new-apache-struts-campaign-uses-eternalblue-and-eternalsynergy-to-mine-monero-on-internal-networks)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **TRex** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/91143](/post/id/91143)

安全客 - 有思想的安全新媒体

本文转载自: [f5.com](https://f5.com/labs/articles/threat-intelligence/cyber-security/zealot-new-apache-struts-campaign-uses-eternalblue-and-eternalsynergy-to-mine-monero-on-internal-networks)

如若转载,请注明出处： <https://f5.com/labs/articles/threat-intelligence/cyber-security/zealot-new-apache-struts-campaign-uses-eternalblue-and-eternalsynergy-to-mine-monero-on-internal-networks>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞](/tag/漏洞)
  * [NSA](/tag/NSA)
  * [ZEALOT](/tag/ZEALOT)
  * [Struts](/tag/Struts)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) TRex

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

