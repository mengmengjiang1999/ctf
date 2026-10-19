# 微软与执法机构及其他合作伙伴共同捣毁Gamarue

阅读量 **100309**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-12-11 12:00:25

 **x**

##### 译文声明

本文是翻译文章，文章原作者 msft-mmpc，文章来源：microsoft.com

原文地址：<https://blogs.technet.microsoft.com/mmpc/2017/12/04/microsoft-teams-up-with-law-enforcement-and-other-partners-to-disrupt-gamarue-andromeda/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_576_/t01e50ccc8d2f20dabd.jpg)

## 一、前言

今天（2017年12月4日），在微软安全研究人员的帮助下，多个国际执法机构与微软数字犯罪部门（Digital Crimes
Unit，DCU）宣布已成功捣毁[Gamarue](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Gamarue)。Gamarue是一款分布广泛的恶意软件，在仙女座（Andromeda）僵尸网络的计算机节点中可以看到该恶意软件的身影。

捣毁过程最初可以追溯到2015年12月，当时微软的Windows Defender研究小组和DCU成立了CME（Coordinated Malware
Eradication，协调根除恶意软件）专项计划，以彻底清除Gamarue。在与互联网安全公司ESET的合作过程中，我们对Gamarue恶意软件及其基础设施进行了深入研究。

我们对超过44,000恶意软件样本进行了研究，从中发现了与Gamarue有关的庞大基础设施。我们向国际多个执法机构提供了这些基础设施的详细信息，其中包括：

1、僵尸网络命令控制服务器所使用的1,214个域名以及IP地址

2、464个不同的僵尸网络

3、超过80个相关恶意软件家族

国际协调合作机制成功捣毁了僵尸网络服务器，打乱了全世界最大的恶意软件家族之一的运转状态。从2011年起，Gamarue一直在散布其他安全威胁，其中包括：

1、[Petya](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Petya)以及[Cerber](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Cerber)勒索软件

2、[Kasidet](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Kasidet)恶意软件（也称之为Neutrino僵尸程序），该软件用于发动DDoS攻击

3、[Lethic](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Lethic)，这是一款垃圾邮件僵尸程序

4、信息窃取恶意软件，如[Ursnif](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?name=win32/ursnif)、[Carberp](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Carberp)以及[Fareit](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Fareit)等等

## 二、全球分布情况

直到被摧毁之前，在过去的六年中，Gamarue一直处于非常活跃的状态，并没有放缓的迹象。根据Windows
Defender的统计数据，在过去六个月时间内，Gamarue在全球范围内广泛流传。

![](https://p4.ssl.qhimg.com/t01e3f96008b91834a4.png)

图1. 从2017年5月到11月Gamarue在全球各地的分布情况

虽然这个安全威胁遍布全球，但受影响的前10个国家主要为亚洲国家。

![](https://p2.ssl.qhimg.com/t01a8f1723284e86e69.png)

图2. 2017年5月至11月受Gamarue影响最严重的前十个国家

在过去六个月里，平均每个月大约有1,095,457台主机上检测到或拦截过Gamarue。

![](https://p0.ssl.qhimg.com/t010ae6a6a3fae0a171.png)

图3. 2017年5月至11月期间感染Gamarue的主机数、IP地址数以及文件数，统计数据中不包含LNK检测数据

## 三、Gamarue僵尸程序

在地下网络犯罪市场上，Gamarue有另一个称号，即Andromeda（仙女座）僵尸程序。所谓僵尸程序（bot），指的是攻击者用来控制被感染主机的恶意程序。与其他僵尸程序一样，Gamarue也被明码标价，黑客们可以自由购买这个犯罪工具包。

Gamarue犯罪工具包由以下几个组件所构成：

1、 **应用生成器（Bot-builder）** ，该组件可以生成恶意软件程序，感染计算机。

2、 **命令控制（Command-and-control）应用**
，这是基于PHP的一个仪表盘（dashboard）应用，攻击者可以通过该应用来管理并控制僵尸程序。

3、 **相关文档（Documentation）** ，介绍如何创建Gamarue僵尸网络。

僵尸网络（botnet）是由被感染主机所组成的网络，可以与命令控制（C&C）服务器通信，而C&C服务器是黑客用来控制受感染主机的服务器。

Gamarue僵尸程序的演变过程一直以来都是安全研究人员的研究重点。在该网络被摧毁时，Gamarue已经出现5个活跃的版本：2.06、2.07、2.08、2.09以及2.10。最新以及最流行的版本为2.10版本。

Gamarue采用了模块化实现方法，也就是说，其功能可以通过插件来扩展，插件可以来自于犯罪工具套件中，也可以单独购买。Gamarue使用的插件包括：

1、 **Keylogger** （150美元）：用来记录用户键盘敲击动作以及鼠标移动轨迹，以窃取用户名及密码、财务信息等。

2、 **Rootkit** （包含在犯罪工具套件中）：可以将rootkit代码注入受害者主机上运行的所有进程，以达到持久驻留目的。

3、 **Socks4/5** （包含在犯罪工具套件中）：将受害者主机变成代理服务器，为恶意软件或恶意指令提供托管服务，感染互联网上的其他主机。

4、 **Formgrabber** （250美元）：捕捉通过网络浏览器（Chrome、Firefox以及Internet
Explorer）提交的任何数据。

5、 **Teamviewer** （250美元）：使攻击者能够远程控制受害者主机，监视用户桌面，具有文件传输等功能。

6、 **Spreader**
：增加可移动驱动器传播渠道，可以通过可移动驱动器（如便携式硬盘驱动器或者通过USB端口连接的闪存驱动器）来传播Gamarue恶意软件；该模块也使用了域名生成（Domain
Name Generation，DGA）算法来生成服务器域名，通过该域名来下载更新。

## 四、Gamarue攻击链

多年以来，攻击者使用各种方式来传播Gamarue，这些渠道包括：

1、可移动驱动器

2、带有恶意链接的社交媒体（如Facebook），这些链接指向托管Gamarue的网站

3、通过下载或漏洞利用工具集来传播

4、包含恶意链接的垃圾邮件

5、木马下载器

一旦Gamarue成功感染某台主机，就会与C&C服务器通信，使当前主机变成僵尸网络中的一个节点。通过C&C服务器，黑客可以控制被Gamarue感染的主机，窃取信息，或发送命令让程序下载其他恶意软件模块。

![](https://p3.ssl.qhimg.com/t01962e265a545a8a65.png)

图4. Gamarue攻击链

Gamarue的主要目标是传播其他流行的恶意软件家族。在CME计划中，我们至少观察到经Gamarue传播的80个不同的恶意软件家族。其中包括如下几类家族：

1、[Petya](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Petya) （勒索软件）

2、[Cerber](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Cerber) （勒索软件）

3、[Troldesh](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Troldesh) （勒索软件）

4、[Ursnif](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Ursnif) （信息窃取及银行木马）

5、[Carberp](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Carberp) （信息窃取及银行木马）

6、[Fareit](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Fareit)（信息窃取及DDoS恶意软件）

7、[Kasidet](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Kasidet)（蠕虫及DDoS恶意软件）

8、[Lethic](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Lethic) （垃圾邮件僵尸程序）

9、[Cutwail](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Cutwail) （垃圾邮件僵尸程序）

10、[Neurevt](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Neurevt)（点击欺诈型恶意软件）

11、[Ursnif](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?name=win32/ursnif)（点击欺诈型恶意软件）

12、[Fynloski](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Win32/Fynloski)（后门程序）

通过安装其他恶意软件，黑客可以在已感染的主机网络上做更多的事情。

###  4.1 命令控制通信流程

当已感染主机上的Gamarue恶意软件开始联系C&C服务器时，它会向服务器发送一些信息，比如硬盘序列号（用于标识该主机的僵尸网络ID）、Gamarue版本ID、已感染主机的操作系统、本地IP地址、代表登录用户是否具备管理员权限的一个标志符、已感染主机所使用的键盘语言设置信息。Gamarue会通过HTTP方式，以JSON格式来发送这些信息。

![](https://p4.ssl.qhimg.com/t01b3403a7d9fe7e881.png)

图5. Gamarue发往C&C服务器的信息

其中与键盘语言设置有关的信息非常有趣，如果键盘语言与如下几个国家或地区相匹配，那么当前主机后续不会被再次感染：

1、Belarus

2、Russia

3、Ukraine

4、Kazahkstan

数据被发往C&C服务器之前，会经过RC4算法加密处理，加密算法所使用的秘钥被硬编码在Gamarue恶意软件中。

![](https://p4.ssl.qhimg.com/t0172ba41fde46b37d4.png)

图6. 加密后的C&C通信数据

一旦C&C服务器收到该数据，就会发送黑客预先在控制面板中设置的一条指令。

![](https://p5.ssl.qhimg.com/t01b6710aef5fd567f4.png)

图7. 攻击者用来与Gamarue僵尸程序通信的控制面板样例

Gamarue支持如下几类命令：

1、下载EXE文件（如其他的可执行恶意软件文件）

2、下载DLL文件（如其他恶意软件，2.09及后续版本中删掉了该命令）

3、安装插件

4、更新僵尸程序（如更新僵尸恶意软件）

5、删除DLL文件（2.09及后续版本中删掉了该命令）

6、删除插件

7、终止僵尸程序运行

攻击者可以使用最后三条命令来删除主机上的Gamarue活动痕迹。

C&C服务器返回的数据同样经过RC4算法加密，使用的秘钥与感染主机发送消息时使用的秘钥相同。

![](https://p5.ssl.qhimg.com/t01734f9d3f4ab0635a.png)

图8. C&C服务器返回的加密数据

返回的数据经过解密后，包含如下信息：

1、以分钟为单位的时间间隔信息：再次请求C2服务器命令时所需等待的时间

2、任务ID：攻击者使用该ID来跟踪某项任务执行过程中是否出现错误

3、命令：具体命令（前面提到过）

4、下载URL地址：恶意软件可以从该地址处下载插件、更新版程序以及其他恶意软件，具体下载的文件类型由具体命令决定。

![](https://p4.ssl.qhimg.com/t012cafc91cf5d8c3ea.png)

图9. 解密后的C&C服务器数据

###  4.2 反沙盒技术

Gamarue采用了一些反病毒软件对抗技术，使分析及检测过程变得更加困难。在感染主机之前，Gamarue会先检查当前主机进程所对应的一个哈希列表。如果Gamarue发现某个进程可能与恶意软件分析工具有关（如虚拟机或沙盒工具），那么它就不会感染这台主机。在早期版本中，如果探测到虚拟机环境，Gamarue会抛出一个伪造版载荷。

![](https://p2.ssl.qhimg.com/t019d09c46ad0351c5d.png)

图10. Gamarue检查当前运行的进程是否与恶意软件分析工具有关

###  4.3 隐身机制

Gamarue使用了[跨进程注入技术](https://blogs.technet.microsoft.com/mmpc/tag/cross-process-injection/)，借此规避各种安防产品的检测机制。Gamarue会将自身代码注入如下几个合法进程中：

1、msiexec.exe（2.07至2.10版的Gamarue）

2、wuauclt.exe、wupgrade.exe以及svchost.exe（2.06版）

Gamarue也会使用一个rootkit插件来隐藏相关文件及自启动注册表项。

Gamarue也采用了一种隐身技术来存储、加载自身插件。这些插件采用无文件存放方式，会保存在注册表中，也可以保存在Gamarue文件的备用数据流中。

###  4.4 篡改系统

Gamarue会尝试篡改操作系统，所采取的措施包括禁用防火墙、Windows更新、用户账户控制（UAC）功能。这些功能无法被重新启用，直到被感染主机彻底清除Gamarue为止。这种系统篡改功能并不适用于Windows
10操作系统。

![](https://p1.ssl.qhimg.com/t017409b6e4274356e1.png)

图11. 禁用防火墙及系统更新

###  4.5 盈利方式

黑客通过Gamarue来盈利的方式多种多样。由于Gamarue的主要目的是传播其他恶意软件，因此黑客可以通过安装付费方案来实现盈利。Gamarue还可以通过插件来窃取用户信息，然后将这些信息通过网络犯罪地下市场售卖给其他黑客。各个犯罪组织之间也可以售卖、租赁、或者交换被Gamarue感染主机的访问权限。

## 五、防御措施

如果不想感染Gamarue以及其他恶意软件及有害软件，大家可以采用如下措施：

1、打开来自于未知用户的电子邮件或者社交媒体消息时要格外小心谨慎。

2、下载软件时，如果不是通过软件开发者官网下载的话，请格外小心谨慎。

更重要的是，请确保自己已安装了合适的安全解决方案，以保护自身主机免受Gamarue和其他安全威胁影响。Windows
Defender反病毒软件可以检测病删除Gamarue恶意软件。借助先进的机器学习模型以及通用型、启发式检测技术，Windows Defender
AV可以通过云保护服务实时检测新型、[未处理过的](https://blogs.technet.microsoft.com/mmpc/2017/07/18/windows-defender-antivirus-cloud-protection-service-advanced-real-time-defense-against-never-before-seen-malware?ocid=cx-blog-mmpc)恶意软件。此外，类似[Microsoft
Safety Scanner](https://www.microsoft.com/wdsi/products/scanner)以及[Malicious
Software Removal
Tool（恶意软件删除工具，MSRT）](https://www.microsoft.com/download/malicious-software-removal-tool-details.aspx)等独立工具也可以检测并删除Gamarue。

[Microsoft Edge](https://docs.microsoft.com/en-us/microsoft-edge/deploy/index?ocid=cx-blog-mmpc)可以阻止Gamarue通过Web方式感染用户，比如来自与社交媒体消息中的恶意链接、通过下载方式或利用工具的传播途径等。Microsoft
Edge是一个安全浏览器，会在低权限的应用程序容器中打开页面，使用基于信誉值的机制来阻止恶意下载行为。

在企业环境中可以搭建额外的保护层。[Windows Defender Advanced Threat
Protection](https://www.microsoft.com/en-us/windowsforbusiness/windows-atp?ocid=cx-blog-mmpc)可以帮助安全操作人员检测网络中的Gamarue活动轨迹（包括跨进程注入技术），使安全人员可以及时调查并应对攻击事件。Windows
Defender ATP具备强大的行为检测及机器学习检测库，可以标记恶意软件感染流程中的恶意行为，包括传播、安装、持久化机制、命令控制通信等行为。

[Microsoft Exchange Online Protection（EOP）](https://products.office.com/en-us/exchange/exchange-email-security-spam-protection?ocid=cx-blog-mmpc)通过内置的反垃圾邮件过滤器功能可以阻止来自电子邮件的Gamarue感染途径，从而保护Office 365用户。[Office 365
Advanced Threat Protection](https://products.office.com/en-us/exchange/online-email-threat-protection?ocid=cx-blog-mmpc)可以阻止带有不安全附件、恶意链接、链接至恶意文件的邮件，对抗这类邮件攻击活动，使用户邮箱更加安全。

[Windows Defender Exploit
Guard](https://blogs.technet.microsoft.com/mmpc/2017/10/23/windows-defender-exploit-guard-reduce-the-attack-surface-against-next-generation-malware/)可以阻止恶意文档（如传播Gamarue的恶意文档）及恶意脚本。Windows Defender Exploit
Guard中包含的[Attack Surface Reduction (ASR)](https://docs.microsoft.com/en-us/windows/threat-protection/windows-defender-exploit-guard/attack-surface-reduction-exploit-guard?ocid=cx-blog-mmpc)功能使用了一组内置的智能策略，能够阻止在恶意文档中探测到的恶意行为。此外，用户也可以启用ASR规则，[阻止](https://docs.microsoft.com/en-us/windows/threat-protection/windows-defender-exploit-guard/attack-surface-reduction-exploit-guard?ocid=cx-blog-mmpc)通过Microsoft
Outlook或网络邮件（如Gmail、Hotmail或Yahoo）运行或加载的恶意附件。

微软会继续维持协作机制，通过[病毒信息联盟（Virus Information Al）](https://www.microsoft.com/en-us/wdsi/alliances/virus-information-alliance)提供恶意样本的一次性封装包，清理被Gamarue感染的主机，保护各类组织的客户免受安全威胁影响。

本文翻译自microsoft.com
[原文链接](https://blogs.technet.microsoft.com/mmpc/2017/12/04/microsoft-teams-up-with-law-enforcement-and-other-partners-to-disrupt-gamarue-andromeda/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/89250](/post/id/89250)

安全客 - 有思想的安全新媒体

本文转载自:
[microsoft.com](https://blogs.technet.microsoft.com/mmpc/2017/12/04/microsoft-teams-up-with-law-enforcement-and-other-partners-to-disrupt-gamarue-andromeda/)

如若转载,请注明出处： <https://blogs.technet.microsoft.com/mmpc/2017/12/04/microsoft-teams-up-with-law-enforcement-and-other-partners-to-disrupt-gamarue-andromeda/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [僵尸网络](/tag/僵尸网络)
  * [Gamarue](/tag/Gamarue)
  * [仙女座](/tag/仙女座)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

