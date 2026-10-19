**虽然说都已经 9012 年了，安全从业者的日常依旧离不开各种工具的辅助。在[ 2018
年安全工具盘点的基础上](https://www.freebuf.com/sectool/159428.html)，我们今年再增加一些免费或开源工具，供读者参考。其中有很多都经过专业人士的试用与推荐。**

![A.png](https://image.3001.net/images/20190115/15475378952095.png!small)

###  **网络安全监控**

[Argus](https://www.qosient.com/argus/)

Argus其实是 Audit Record Generation and Utilization
System（审计记录生成与使用系统）的缩写，能对网络流量与数据进行高效、深入的分析。Argus可以筛选大量流量并快速全面的生成报告。不论是单一使用还是与其他工具共同使用，这个工具都可以提供坚实的协助。

![ArgusOptimizationCycle.gif](https://image.3001.net/images/20190115/15475392377651.gif!small)

[P0f](http://lcamtuf.coredump.cx/p0f3/#)

P0f的更新频率很低，十几年来变化不大，但仍然比较欢迎。这款工具使用时简单、高效，不会产生额外的流量。主要用于标识与其交互的任何主机的操作系统。很多网络安全监控工具都可以创建探测、名称查找以及各种查询功能。P0f则以其轻量级、高速以及简洁运行的的特征而著称，对于高级用户来说必不可少。但对于一些新手而言，可能学习起来没那么简单。

![P0f.png](https://image.3001.net/images/20190115/15475394175483.png!small)

[Nagios](https://www.nagios.org/)

Nagios可以监控主机、系统和网络，实时发送警报。用户可以准确指定他们想要通知的内容。
这个程序可以监控HTTP、NNTP、ICMP、POP3和SMTP等网络服务。很多人将Nagios用于流量监控，其实它也可以用作全面、基础的网络管理方案，适用于网络安全专业人士和小型企业。

![微信截图_20190115165839.png](https://image.3001.net/images/20190115/15475427512690.png!small)

[Splunk](https://www.splunk.com/)

Splunk是一款高速、通用的网络监控工具，专为实时分析和历史数据搜索而设计。具有统一界面，对用户比较友好。其强大的搜索功能为应用程序监控提供了协助。Splunk可以处理非结构化数据，并轻松扩展。可以配合SIEM，达到更好的效果。

Splunk其实是付费应用，提供免费版本，但免费版本的功能有限。如果预算足够的话，付费购买也是性价比比较高的选择。

![Splunk_adaptive-response-gp_300.png](https://image.3001.net/images/20190115/15475430054844.png!small)

### 网络侦察与取证

[TheHarvester](https://tools.kali.org/information-gathering/theharvester)

TheHarvester基于Kali，有助于收集域名、电子邮件地址、员工姓名、以及来自SHODAN的信息等。

![scrape-target-email-addresses-with-theharvester.w1456.jpg](https://image.3001.net/images/20190115/15475435349939.jpg!small)

[Maltego](https://www.paterva.com)

Maltego是Paterva开发的用于开源智能和取证的专有软件，可以提供一个变换库，用于从开源中发现数据，并以图形格式显示该信息，适用于链接分析和数据挖掘。Maltego有助于发现关于侦察目标的大量数据，包括IP地址、域名、DNS条目以及员工电子邮件地址等。

![Logo-ThreatConnect-Partner-Maltego.png](https://image.3001.net/images/20190115/15475437472547.png!small)

### 加密类

2018 的盘点中，主推的是Gnupg PGP和Keepass以及OpenVPN这三款加密工具。今年新增Tor和Openswan。

[Tor](https://www.torproject.org/)

现在提到Tor大家似乎都会想起暗网。但事实上，Tor
本身只是个加密性能比较好的工具，可以保护互联网隐私。一般来说，系统将请求发送到代理web服务器以保护隐私、让用户难以被追踪。尽管会有一些恶意出口节点嗅探流量，但在使用过程中仔细留意，就不会有大的影响。在实际应用中，Tor对于网络安全的作用比在暗网中发挥的作用更大。

![Orbot-logo.svg.png](https://image.3001.net/images/20190115/15475439411647.png!small)

[Openswan](https://www.openswan.org/)

Openswan可以说是Linux下IPsec的最佳实现方式，可以设置支持IKWv2、X.509证书、NAT遍历等的安全VPN。Openswan支持net-to-net和RoadWarrior两种模式，前者可实现远程子网 通讯后类似局域网的访问，后者可以实现客户端用IPSec 连接到内网后的安全通讯。

![openswan.com.png](https://image.3001.net/images/20190115/15475440663587.png!small)

### 密码管理与恢复

[Cain and Abel](http://www.oxid.it/cain.html)

仅适用于Windows的密码恢复工具。可以记录VoIP对话，解码加密密码并分析路由协议。
可以获取到缓存密码、显示密码框、暴力破解密码并进行密码分析等。可作为数据包嗅探的入门程序。

![2-2.png](https://image.3001.net/images/20190115/15475441868803.png!small)

[Thycotic Secret Server](https://thycotic.com)

Secret
Server是一种高级密码管理器工具，适合IT团队使用。其设置秘密服务器，有助于IT团队管理者了解团队成员访问密码的情况并在必要时更改密码。当然，Secret
Server与其他密码管理器一样也可以生成强密码且不需要用户强行记忆。

![16750.png](https://image.3001.net/images/20190115/1547549656348.png!small)

此外，[1
password](https://www.iplaysoft.com/1password.html)、[LastPass](https://www.lastpass.com/)等也都是大家常用且好用的密码管理工具。

### 漏洞扫描与入侵检测

Burp
Suite、Nikto等工具可查看[2018年盘点文章](https://www.freebuf.com/sectool/159428.html)。新增工具请看下文。

[Snort](https://www.snort.org/)

Snort是一个企业级的开源IDS，可以与任何操作系统和硬件兼容。系统执行协议分析、内容搜索/匹配以及各种网络攻击的检测（如缓冲区溢出、隐形端口扫描程序、CGI攻击、OS指纹识别等）。其优点是易于配置，规则灵活，可以分析原始数据包。

![Snort-Free-Network-Intrusion-Detection-Prevention-System-640x321.png](https://image.3001.net/images/20190115/15475446816830.png!small)

[OWASP Zed Attack Proxy Project (ZAP)](https://www.zaproxy.org/)

开发人员需要测试Web应用程序的安全性时，常常使用ZAP。ZAP是完全开源的跨平台工具，可以实现Web应用程序的主动和被动扫描、发现抓取程序内容的爬虫，并生成相关报告。此外，ZAP还能添加组件。

![zap.jpg](https://image.3001.net/images/20190115/15475448428879.jpg!small)

[ModSecurity](https://modsecurity.org/)

ModSecurity堪称We应用程序防火墙的“瑞士军刀”，相当于Web应用程序开发者的必备工具。ModSecurity的主要功能包括实时监控和访问控制、HTTP流量日志记录、持续被动安全防御和Web应用程序加固等。

![modsecurity1.png](https://image.3001.net/images/20190115/1547544912325.png!small)

### 漏洞管理

[Nessus](https://www.tenable.com/downloads/nessus)

Nessus
堪称漏洞评估领域的行业标准，能帮助安全人员快速识别和修复问题（包括软件漏洞、缺失补丁、恶意软件和错误配置等问题）。借助预先构建的策略和模板、群组暂停功能和实时更新等功能，可以轻松、直观地进行漏洞评估。这款工具很活跃，最近刚发布了最新版本。

![NessusManagerAgents.png](https://image.3001.net/images/20190115/15475460301107.png!small)

[Balbix](https://www.balbix.com/)

Balbix能够分析网络中每种易受攻击的资产情况，包括相关数据、交互的用户、是否面向公众等，并确定资产对组织的重要性。Balbix
还可以将每个漏洞与活动的威胁源进行比较，并预测、评估未来发生漏洞的可能性以及漏洞可能对企业造成的损失。

![xpc.png.pagespeed.ic.695zqNsmAw.png](https://image.3001.net/images/20190115/15475462596608.png!small)

### 无线安全

[NetStumbler](http://www.netstumbler.com/downloads/)

主要适用于Windows用户，可以在无线网络中找到开放的接入点。NetStumbler既可以寻找WAP，又检测其他安全扫描工遗漏的漏洞。但需要注意的是这个工具仅仅适用于Windows，且不提供源代码。

[Kismet](https://www.kismetwireless.net/)

Kismet是基于控制台（ncurses）的802.11第2层无线网络检测器、嗅探器和入侵检测系统。
Kismet主要通过被动嗅探识别网络，还可以发现正在使用中的隐藏（非信标）网络。它可以通过嗅探TCP、UDP、ARP和DHCP数据包自动检测网络IP块，以Wireshark
/ tcpdump兼容格式记录流量，甚至可以在下载的地图上绘制检测到的网络和预估范围。

![2018-05-11T14_53_14.905Z-IMG_20180511_102100.jpg](https://image.3001.net/images/20190115/15475480499663.jpg!small)

[KisMAC](https://kismac-ng.org/)

KisMAC适用Mac，简单易用，经验不足的用户也容易上手。KisMAC相当于Kismet的Mac OS
X版本，但二者代码库不同。利用KisMAC工具，可以通过结束鉴权（deauthentication）攻击，实现映射和渗透测试。

![KisMac.png](https://image.3001.net/images/20190115/1547548907885.png!small)

### 嗅探与抓包

[Tcpdump](http://www.tcpdump.org/)

支持Mac、Windows和Linux，比Wireshark出现得更早。设置了数据包嗅探领域的标准，相当于这个领域的早期风向标。Tcpdump持续开发改进，力求简洁，所使用的系统资源较少，并且几乎没有安全风险。

![4154908.png](https://image.3001.net/images/20190115/15475489797435.png!small)

[Wireshark](https://www.wireshark.org/)

Wireshark是继Tcpdump之后的免费开源的网络数据包分析软件,截取网络数据包，并尽可能显示出最为详细的网络数据包数据。同时，可提供实时网络分析，让用户看到重建的TCP会话流。Wireshark的使用频率较高，很多安全从业者对此都不陌生。

![maxresdefault--1-.jpg](https://image.3001.net/images/20190115/15475490341894.jpg!small)

### 邮件安全

垃圾邮件、钓鱼邮件泛滥，让很多人不堪其扰。很多安全研究员也专门针对这一现象研发了一些工具。

[](https://www.mailwasher.net/)

> [MailWasher](https://www.mailwasher.net/)（扫描邮件、确定安全之后再下载）、
>
> [SPAMfighter](https://www.spamfighter.com)（可识别并过滤垃圾邮件，对家庭用户100%免费）
>
>
> [Spamihilator](https://www.spamihilator.com/en/)（通过过滤器、学习算法和概率计算来确定垃圾邮件，并设置用户培训区域，以便用户能培训系统更好地学习应当屏蔽的电子邮件）

以上为网络安全领域常用的一些工具摘录与盘点作为上一篇工具盘点文章的后续与补充，在专业网络安全工具网站[Sectools](https://sectools.org/)中，有更多工具和点评可以参考，感兴趣的读者可以去官网查看。

 ***参考来源：[CyberX](https://cyberx.tech/free-cybersecurity-tools/#vulnscan)、[Phoenix NAP](https://phoenixnap.com/blog/best-network-security-tools)等，转载请注明来自 FreeBuf.COM**

