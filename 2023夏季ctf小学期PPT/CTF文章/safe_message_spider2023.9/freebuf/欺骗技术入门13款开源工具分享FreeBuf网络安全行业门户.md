![Under-The-Hood-Of-Deception-Technology.001.jpg](https://image.3001.net/images/20190628/1561731461_5d16218559104.jpg!small)

> “无论什么战斗，光靠防守是赢不了的。想要赢，就必须攻击。” ——《死亡笔记》

**一旦被那些受利益驱使或有政府背景的黑客团伙盯上，在这场不太公平的攻防博弈中，你会明显感到力不从心。他们有充足的时间，有娴熟的技术和丰富的资源，而且只要在无数次的尝试中成功一次就可以大获全胜。但安全团队的防守却需要保证百分之百的成功率。这也就是我们常说的“攻防不对等”。防守方靠什么扳倒在战役开始前就已“占尽先机”的攻击方？**

眼下安全市场中，真正意义上主动出击的安全技术就是欺骗防御了。欺骗技术最大的特点就是将攻防活动中的认知成本、经济成本以及时间成本转移到攻击者身上。1989年，美国普渡大学的Gene
Spafford首次提出了网络欺骗的核心思想。尽管概念由来已久，但针对欺骗技术的研究和应用却在近几年才兴起。

欺骗技术对于检测内网渗透活动、发现权限提升、建立威胁情报库等工作的意义几乎是不可比拟的。本文将推荐几款免费的开源欺骗工具，作为欺骗技术的入门课。但开源工具都有共同的弱点——使用体验与实际效果无法保证。

## 一、网络服务

### 1\. Cowrie

下载地址：<https://github.com/micheloosterhof/cowrie>

简介：Cowrie是一种中等交互式SSH和Telnet蜜罐，用于记录暴力攻击和攻击者执行的shell交互。它能够模拟交互式SSH服务器，并具备可自定义的命令响应机制。另一个类似的工具是HonSHH（<https://github.com/tnich/honssh>），部署在真实SSH服务器和攻击者之间，实现“中间人（MiTM）”连接并记录所有SSH通信。

### 2\. Dionaea

下载地址：<https://github.com/DinoTools/dionaea>

简介：Dionaea是一个多协议蜜罐，涵盖FTP到SIP（VoIP攻击）的所有内容，而其中最强大的则是SMB协议诱饵。它甚至能够通过LibEmu模拟恶意软件payload来检测shellcode或分析攻击活动。

##  二、IoT诱饵

### 3\. Honeything

下载地址：<https://github.com/omererdem/honeything>

简介：Honeything模拟的是TR-069 WAN管理协议以及存在漏洞的RomPager Web服务器。其它物联网诱饵可以通过模拟嵌入式的telnet
/ FTP服务器来创建，例如使用BusyBox这个软件。

## 三、SCADA / ICS诱饵

### 4\. ConPot

下载地址：<http://conpot.org/>

简介：ConPot模拟了很多工业控制系统中的基础设施，包括MODBUS、DNP3和BACNET等协议。它还配备了一个模拟SCADA HMI的Web服务器。

### 5\. GasPot

下载地址：<https://github.com/sjhilt/GasPot>

简介：GasPot模拟的是Veeder Root Gaurdian AST（通常用于监控石油和天然气行业）。

## 四、数据库和NoSQL蜜罐

### 6\. MongoDB-HoneyProxy

下载地址：<https://github.com/Plazmaz/MongoDB-HoneyProxy>

简介：MongoDB-HoneyProxy模拟的是一个不安全的MongoDB数据库。黑客会经常扫描互联网，寻找上那些安全防护机制有漏洞的数据库并将其公开。因此MongoDB数据库是一个命中率较高的一类诱饵。

### 7\. ElasticHoney

下载地址：<https://github.com/jordan-wright/elastichoney>

简介：ElasticHoney是一个简单的ElasticSearch蜜罐，主要利用RCE远程代码执行漏洞发现攻击者。

## 五、凭证蜜罐和honeytoken

### 8\. DCEPT

下载地址：<https://github.com/secureworks/dcept>

简介：2011年被Dell收购的SecureWorks的DCEPT（Domain Controller Enticing Password
Tripwire）是一款基于honeytoken并设置在微软Active
Directory上的安全程序。Honeytoken是指用一些正常情况下永远不会使用的信息内容作为诱饵，一旦发现这些honeytoken被访问，则表明这些信息内容可能被收到攻击。在DCEPT中，honeytoken主要是虚假凭证，使用这些虚假凭证进行登录尝试就说明网络中存在恶意活动。

### 9\. Canarytokens

下载地址：<https://github.com/thinkst/canarytokens>

简介：Thinkst Applied
Research研究院开发的Canarytokens会在用户系统中放置不同类型的诱饵数据，等待攻击者触发后进行恶意活动和行为的追踪。目前Thinkst
Canarytokens已有商业版本。

## 六、伪装客户端与恶意软件分析

### 10\. Thug

下载地址：<https://buffer.github.io/thug/>

简介：Thug是一个模拟web浏览器行为分析客户端攻击情况的“伪装客户端（honeyclient）”，能够分析恶意链接，检测其中是否包含JavaScript、ActiveX或Flash组件。另外还能够下载payload样本并与VirusTotal集成后进行分析。

### 11\. Cuckoo Sandbox

下载地址：<https://cuckoosandbox.org/>

简介：Cuckoo Sandbox是一个能够分析恶意软件的沙箱工具，我们可以在里面执行疑似恶意的软件样本以及Cuckoo
VM中的二进制文件、Microsoft
Office文档和电子邮件，并且还能收到一份包含已执行哪些代码、更改了哪些文件/注册表、观察到了哪些网络callback等内容的完整报告。

## 七、All-in-One一体化工具

### 12\. Honeydrive

下载地址：<http://bruteforcelab.com/honeydrive>

简介：HoneyDrive是比较优秀的Linux蜜罐发行版，包含10多个预安装和预配置的蜜罐软件包，如Kippo
SSH蜜罐、Dionaea和Amun恶意软件蜜罐、Honeyd低交互蜜罐、Glastopf web蜜罐和Wordpot、Conpot SCADA /
ICS蜜罐、Thug和PhoneyC蜜客等等。此外，它还有很多实用的预配置脚本和程序，如Kippo-Graph、Honeyd-Viz、DionaeaFR、ELK stack等，对数据进行分析、处理及可视化呈现。

### 13\. MHN（Modern Honey Network）

 _[]()_下载地址：<https://github.com/threatstream/mhn> _[]()[]()_

简介：MHN是用于蜜罐管理和数据收集的集中式服务器，能够实现传感器的快速部署和数据快速收集，Web界面简洁明了。它的蜜罐部署脚本包括了几种常见的蜜罐技术：Snort、Cowrie、Dionaea和glastopf等。

对专业的安全人员来说，部署这些工具并不是难事。部署完毕后，我们就可以从攻击方的角度进行测试，优化源代码、降低指纹识别的难度。如果做到这一步，也不要忘了向作者提交补丁，发扬开源精神。

还是那句话，开源项目只能起到辅助作用，帮助你了解蜜罐或欺骗产品的作用，想要达到真正的防御和检测效果还是应该依赖于专业厂商开发的商业工具。

 *** 参考来源：[smokescreen](https://www.smokescreen.io/practical-honeypots-a-list-of-open-source-deception-tools-that-detect-threats-for-free/)，FB小编柚子编译，转载请注明来自FreeBuf.COM**

