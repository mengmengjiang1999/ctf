**译者：知道创宇404实验室翻译组  
原文链接：<https://blogs.juniper.net/en-us/threat-research/new-pastebin-like-service-used-in-multiple-malware-campaigns>**

### 前言

Juniper Threat Labs发现了几个依赖于pastebin-like服务的恶意软件活动。有问题的domain是paste.nrecom.net。
这些攻击通常以网络钓鱼电子邮件开始，当用户被诱骗执行恶意软件时，它会在不写入磁盘的情况下，从paste.nrecom.net将其加载到内存中。为恶意软件基础设施使用合法的web服务并不是什么新鲜事，正如我们看到的APT
group
FIN6使用pastebin来托管感染链的一部分，rock使用它来进行命令和控制。虽然使用合法的web服务并不新奇，但这是我们第一次看到攻击者使用paste.nrecom.net。我们发现的恶意软件包括Agentsela、LimeRAT、Ransomware和Redline
Stealer。

### 什么是paste.nrecom.net？

![](https://images.seebug.org/content/images/2020/10/5cdda0d1-5531-41c1-867c-bfeed091ba9a.png-w331s)

paste.nrecom自2014年5月开始投入使用。pastebin是一种可以发布代码或文本数据并与他人共享的服务。paste.nrecom做同样的事情，它还提供了一个允许编写脚本的API。这对攻击者是有利的，因为他们可以轻松地以编程方式插入和更新数据。该服务由Stikked提供支持，Stikked是一个基于PHP的开源pastebin。

### 攻击者怎么进行恶意攻击？

因为它是一个纯文本的服务，人们会认为它不能在其中托管可执行文件（二进制数据）。但是，二进制数据可以通过简单的编码来表示为文本文件。常用的编码方法是使用base64。

![](https://images.seebug.org/content/images/2020/10/69bbebaf-ea8e-41f5-bdad-17b60fba0437.png-w331s) 以base64编码的恶意粘贴。

为了增加另一层混淆，它们使用XOR密钥对二进制数据进行加密。例如，以下文件使用XOR密钥0x02加密。
![](https://images.seebug.org/content/images/2020/10/0e968c4a-128b-4ab7-b0b0-eeac240895f7.png-w331s)

![](https://images.seebug.org/content/images/2020/10/8b52eebe-6e6e-489e-b1bd-fc7013dec02d.png-w331s) 经过base64解码后，仍使用XOR算法对文件进行加密。

![](https://images.seebug.org/content/images/2020/10/6b85e452-afe3-4fdc-b14b-ac8301bf94ae.png-w331s)
完成所有必要的解码和解密后，可以看到可执行文件，如上所示。

从2020年9月21日开始，我们已经看到几个恶意软件家族利用这项服务迅速发展。
![](https://images.seebug.org/content/images/2020/10/2970dfa9-694e-42e0-a7fe-d24d75435b05.png-w331s)

### 恶意软件活动

攻击通常以包含附件（例如文档，存档或可执行文件）的网络钓鱼电子邮件开始。当用户被诱骗安装恶意附件时（第一阶段），它将从paste.nrecom.net下载下一阶段。我们还看到恶意软件在同一服务中托管其配置数据。

#### Agent Tesla

Agent
Tesla是一种间谍软件，它能够从Web浏览器，邮件客户端和FTP服务器窃取个人数据。它还可以收集屏幕截图，视频并捕获剪贴板数据。该恶意软件的最新版本还能够从VPN客户端窃取个人数据。它在地下市场的售价低至15美元，根据附加功能可能会升至70美元。

Agent
Tesla是使用这种类似pastebin的服务中最活跃的恶意软件之一。广告系列通常从带有恶意附件的网络钓鱼电子邮件开始。根据我们发现的样本，这些活动针对与航运，供应链和银行相关的多个行业。在某些情况下，附件是归档文件，例如.iso，.rar或.uue，如下所示：
![](https://images.seebug.org/content/images/2020/10/b752c8ad-413f-406e-813a-8fe6d64bf1d1.png-w331s)

![](https://images.seebug.org/content/images/2020/10/54da670b-e456-4db1-a4a8-27aa5300f24b.png-w331s)

从链中可以看到，有两个paste.nrecom请求，因为它会将Agent
Tesla的有效负载分为两个。第一个请求是文件的前半部分，第二个请求是文件的后半部分。此技术使安全解决方案难以分析有效负载。

![](https://images.seebug.org/content/images/2020/10/6a9c90ec-77de-404b-b5c7-008ee51e8138.png-w331s)

以下是一些电子邮件附件和一些电子邮件附件中的文件，我们发现这些电子邮件附件是使用paste.nrecom安装Agent Tesla的。

![](https://images.seebug.org/content/images/2020/10/108babd7-61ba-4638-8c09-943b836e3e65.png-w331s)

在某些情况下，附件是下载Agent Tesla加载程序的Office文档。

![](https://images.seebug.org/content/images/2020/10/ed312024-6602-47be-821b-55d7ee19d852.png-w331s)
![](https://images.seebug.org/content/images/2020/10/0c0f3e56-270a-48fd-8b97-a0e0f99d458e.png-w331s)

#### W3Cryptolocker勒索软件

W3Cryptolocker是一个相对较新的勒索软件。该勒索软件于2020年7月出现。根据其代码中的字符串，我们将该恶意软件称为W3Cryptolocker。

![](https://images.seebug.org/content/images/2020/10/48aeace7-2340-43e0-b622-8e171b1b9160.png-w331s)

该加载程序托管在一个可能被黑客入侵的网站italake.com上。

![](https://images.seebug.org/content/images/2020/10/dd72f92d-1f58-469d-856b-4247334bd938.png-w331s)
![](https://images.seebug.org/content/images/2020/10/914cbf17-0a8e-4d61-86d6-79eac2f3e934.png-w331s)

它将加密所有驱动器中的所有文件，但扩展名为“ .xls”的文件和具有以下字符串的文件夹除外：

  * Windows
  * ProgramData
  * $Recycle.bin
  * System Volume Information

它为加密文件添加了扩展名.xls。对每个文件夹进行加密后，它将在每个文件夹上创建一个“ Read_Me.txt”文件，并显示以下消息。

![](https://images.seebug.org/content/images/2020/10/890b4062-38ea-466b-a769-d968ad6c2b54.png-w331s)

访问`https://yip[.]su/2QstD5`会将您带到一个Freshdesk支持站点bit7.freshdesk.com。

![](https://images.seebug.org/content/images/2020/10/841b5a39-ec75-4152-82d1-0812ef6f8aa1.png-w331s)

其他W3Cryptolocker样本

  * c97852b425e41d384227124d93baf6c2d3e30b52295a828b1eac41dc0df94d29
  * 9a0af98d0b8f7eacc3fdd582bbc0d4199825e01eeb20c2a6f98023c33ece74f6
  * 01eea2a4628c6b27a5249a08152655246871acafa657e391b73444c05097976e
  * 9a08e87e8063b13546e464f73e87b2ca5bde9410fec4e614313e2b8a497592fa
  * 8dfe87850bd17b4eb0169b85b75b5f104ae6b84deeb2c81fe6ae5e19685f6c66
  * 53124033d521158771eac79ad6f489c6fdd5b25ab96712035c2ca65b3a3c5eed
  * aac2024789ffd2bfce97d6a509136ecf7c43b18c2a83280b596e62d988cedb10
  * fafabdffa67883587ba1a3c29f6345a378254f720efe8c2f318a4d5acdbce373

#### Redline Stealer

Redline
Stealer是一种恶意软件，于2020年3月左右出现，据报道它针对美国的医疗保健和制造业。该恶意软件被发现在论坛上投放广告，并提供多种定价选项，起价为100美元/月。它具有以下功能：

  * Browser Data Stealer 
    * Login and Passwords
    * Cookies
    * Autocomplete Fields
    * Credit Cards
  * Remote Task Functions
    * Execute Commands
    * Download Files
    * Download Files and Execute
    * RunPE (Process Injection for fileless infection)
    * OpenLink
  * FTP and IM client stealer 
  * File-grabber 
  * Collects information about the victim’s system 

我们发现的样本是将比特币矿工存档到RAR文件中。该档案文件包含一个可执行文件MinerBitcoin.exe，该文件可从paste.nrecom.net下载Redline
Stealer有效负载。

![](https://images.seebug.org/content/images/2020/10/1cbbbad1-72b6-4b24-ab10-553a33d93dd2.png-w331s)
![](https://images.seebug.org/content/images/2020/10/0719f808-cbfe-4090-9693-854355258648.png-w331s)

#### LimeRAT

LimeRAT是用.NET编码的远程管理木马，并且是开源的。它是APT-C-36小组用来针对哥伦比亚政府机构的恶意软件。它可以用作：

  * Ransomware
  * Remote Desktop
  * Crypto Mining
  * CryptoStealer
  * DDOS
  * Keylogger
  * Password Stealer

![](https://images.seebug.org/content/images/2020/10/5beeada3-1f8e-4af2-9af0-ad40f14bebcf.png-w331s)

我们发现的另一个示例是aae2e0d0792e22164b3c81d0051c5f94a293bae69e7aac5cc4ad035860dbf802。在进行此分析时，该样本仍具有零VT检测。它从`https://paste[.]nrecom[.]net/view/raw/93a7cd20`下载LimeRAT。

![](https://images.seebug.org/content/images/2020/10/c445f15e-f141-4567-a6a9-f7b334912139.png-w331s)

### 结论

使用恶意软件基础结构的合法Web服务（例如pastebin或paste.nrecom）为网络犯罪分子提供了一个优势，因为这些服务由于其合法使用而无法轻易删除。我们建议安全操作部门将paste.nrecom添加到可能出于恶意目的而滥用的Web服务中。建议监视此类服务，以检查可疑内容，特别是以base64编码的二进制数据。

### IOC

#### Domain

Paste.nrecom.net  
192.12.66.108（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=192.12.66.108
"ZoomEye搜索结果")）  
lol.thezone.vip

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1354/>

