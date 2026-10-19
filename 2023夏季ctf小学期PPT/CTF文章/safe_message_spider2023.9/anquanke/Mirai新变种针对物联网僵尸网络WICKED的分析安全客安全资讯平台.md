# Mirai新变种：针对物联网僵尸网络WICKED的分析

阅读量 **139557**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-05-21 14:05:57

 **x**

##### 译文声明

本文是翻译文章，文章来源：https://www.fortinet.com/

原文地址：<https://www.fortinet.com/blog/threat-research/a-wicked-family-of-bots.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t012de2b5d5580b0752.jpg)

## 概述

随着对最新的物联网僵尸网络的不断追踪，FortiGuard实验室团队发现了越来越多的Mirai变种，这些变种的诞生很大程度上是由于两年前Mirai公开了其源代码。自此之后，许多攻击者持续将自己的需求添加到原来的代码之中，从而使Mirai不断发展演变。  
一些代码能力较强的攻击者对Mirai的源代码做出了重大修改，例如增加了将受感染设备变为恶意软件代理服务器（
[https://www.fortinet.com/blog/threat-research/omg–mirai-based-bot-turns-iot-devices-into-proxy-servers.html](https://www.fortinet.com/blog/threat-research/omg--mirai-based-bot-turns-iot-devices-into-proxy-servers.html)
）、将受感染设备作为各种加密货币挖矿机（ <https://www.fortinet.com/blog/threat-research/satori-adds-known-exploit-chain-to-slave-wireless-ip-cameras.html>
）的功能。此外，还有一些人将Mirai的代码与多种已知或未知的漏洞（ <https://www.fortinet.com/blog/threat-research/rise-of-one-more-mirai-worm-variant.html>
）相结合。而我们近期发现的恶意软件家族就是后者，我们将其命名为WICKED。  
这一新的变种在原始代码的基础之上，增加了至少3个漏洞利用方式，并将目标瞄准尚未修复漏洞的物联网设备。在本文中，我们将详细分析该系列恶意软件的工作原理，被感染主机的行为模式，并分析它与其它已知僵尸网络的联系。

## 对Bot的深入分析

为了揭示出Mirai和这个新变种之间的差异，我们需要详细查看新变种的配置表，具体是将该内容与密钥0x37做异或（XOR）操作，从而实现解密。  
我们注意到，其中存在一些有趣的字符串，例如“/bin/busybox WICKED”和“WICKED: applet not
found”，这也是我们将该变种命名为WICKED的原因。此外，字符串SoraLOADER成为了一个线索，由此推断出这个BOT可以作为另一个Mirai变种Sora僵尸网络的下载工具和传播工具。然而，在我们后续进行分析时，得到的结论与上述推断相互矛盾，从而我们得到了一个更有趣的假设。  
解密后的配置表：  
  
基于Mirai的僵尸程序通常都包含三个主要模块：攻击模块（Attack）、结束运行模块（Killer）和扫描模块（Scanner）。在此次分析中，我们将重点放在了能揭示出僵尸网络传播机制的扫描模块。原始版本的Mirai使用了传统的暴力破解尝试，以试图访问物联网设备。而在WICKED
Bot中，使用了一些可利用的已知漏洞，其中一些是比较老的漏洞。  
WICKED Bot会通过启动原始套接字SYN连接，扫描端口8080、8443、80和81。  
  
一旦成功建立连接，它将尝试对该设备进行漏洞利用，并下载其Payload。僵尸程序通过使用write()系统调用，将漏洞利用字符串写入套接字之中。对于write()系统调用的使用方式与send()系统调用相同，flags参数都设置为0，也就意味着没有额外的行为。  
通过写入套接字，发送一个请求：  

## 目标设备

该恶意软件要尝试利用的漏洞取决于能够连接的端口号。我们列举出了其利用的漏洞及相应的目标端口。  
8080端口：Netgear DGN1000和DGN2200 v1路由器漏洞（也被Reaper僵尸网络使用）  
  
81端口：CCTV-DVR远程代码执行漏洞（ <http://www.kerneronsec.com/2016/02/remote-code-execution-in-cctv-dvrs-of.html> ）  
  
8443端口：Netgear R7000和R6400命令注入漏洞（CVE-2016-6277， <https://www.exploit-db.com/exploits/41598/> ）  
  
80端口：针对受影响Web服务的Invoker Shell漏洞  
该漏洞并不是直接在设备上进行利用的，而是利用已安装的恶意Web Shell，对受漏洞影响的Web服务器进行漏洞利用。  
  
在成功进行漏洞利用后，僵尸程序会从恶意网站下载Payload。针对我们分析的僵尸程序样本，下载地址是hxxp://185.246.152.173/exploit/owari.{extension}。显而易见，该僵尸程序的目的是下载另一个Mirai变种Owari
Bot，而不是我们此前所推断出的Sora Bot。但经过分析，我们没有在网站目录中找到Owari
Bot的样本。在继续分析后，我们发现Owari已经被另一个僵尸程序样本取代，最后发现取代它的样本是Omni Bot。  
  
我们仔细检查了该恶意网站的历史镜像，确认它之前发布过Owari僵尸网络。  
此外，我们在网站的/bin目录下发现了其他Omni样本，这些样本曾被分析出（
<https://blog.newskysecurity.com/cve-2018-10561-dasan-gpon-exploit-weaponized-in-omni-and-muhstik-botnets-ad7b1f89cff3> ）是使用了GPON漏洞（CVE-2018-10561，
<https://www.exploit-db.com/exploits/44576/> ）。根据其时间戳的不同表明，Payload会定期进行更新。  

## 不同变种之间的联系

我们发现了WICKED、Sora、Owari和Omni僵尸网络的关联，并由此回想到我们去年四月对一位安全研究员的采访（
<https://blog.newskysecurity.com/understanding-the-iot-hacker-a-conversation-with-owari-sora-iot-botnet-author-117feff56863>
），我们认为他即是这些僵尸网络变种的作者。他使用Wicked作为自己网络上的昵称，并且已经被证实是Sora和Owari的作者。当被问及对Sora和Owari的未来计划时，Wicked的回答是：“Sora现在是一个被停滞的项目，我会继续对Owari进行研究。我目前的计划是继续对已有项目进行更新，因此不会很快出现第三个新的项目。”  
显然，正如我们在/bin目录下所看到的，Sora和Owari僵尸网络样本现在已经不再更新，二者已经被Omni取代。

## 结论

Wicked在采访中提及过，不同僵尸网络都是在同一个主机上托管的。由此我们基本可以确认，僵尸网络Wicked、Sora、Owari和Omni的作者都是同一个人，也就是Wicked本人。由此，我们认为，尽管Wicked僵尸程序最初设计的目的是为了承载Sora僵尸网络，但后来被不断修改，从而实现作者的其他攻击目标。  
Forti实验室将继续关注物联网威胁领域的最新发展动态，特别是在僵尸网络背后，攻击者为了感染更多物联网设备而新增加的漏洞利用方法。  
最后，感谢我们的同事David Maciejak、Joie Salvio、Jasper Manuel和Tony Loi对本文做出的贡献。  
本文由FortiGuard Lion团队发表。

## IoC

SHA256：  
ELF/Mirai.AT!tr  
57477e24a7e30d2863aca017afde50a2e2421ebb794dfe5335d93cfe2b5f7252 (Wicked)  
下载站点：  
[ hxxp://185.246.152.173/bins/](hxxp://185.246.152.173/bins/)  
[ hxxp://185.246.152.173/exploit/](hxxp://185.246.152.173/exploit/)

本文翻译自https://www.fortinet.com/ [原文链接](https://www.fortinet.com/blog/threat-research/a-wicked-family-of-bots.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/145452](/post/id/145452)

安全客 - 有思想的安全新媒体

本文转载自: [https://www.fortinet.com/](https://www.fortinet.com/blog/threat-research/a-wicked-family-of-bots.html)

如若转载,请注明出处： <https://www.fortinet.com/blog/threat-research/a-wicked-family-of-bots.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [僵尸网络](/tag/僵尸网络)
  * [技术分析](/tag/技术分析)
  * [IOT攻击](/tag/IOT攻击)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

