# 行走的漏洞利用机器人：僵尸网络病毒携71个EXP占领高地

阅读量 **1544285**

|评论 **1**

发布时间 : 2019-12-19 10:45:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01097085cf33536b02.jpg)

## 前言

僵尸网络 Botnet 是指采用一种或多种传播手段，将大量主机感染bot程序（僵尸程序）病毒，从而在控制者和被感染主机之间所形成的一个可一对多控制的网络。

攻击者通过各种途径传播僵尸程序感染互联网上的大量主机，而被感染的主机将通过一个控制信道接收攻击者的指令，组成一个僵尸网络。之所以用僵尸网络这个名字，是为了更形象地让人们认识到这类危害的特点：众多的计算机在不知不觉中如同中国古老传说中的僵尸群一样被人驱赶和指挥着，成为被人利用的一种工具。

而本文提到的一种最新的僵尸网络Mirai变种ECHOBOT，足足使用了71个漏洞利用(EXP)，将对每一个资产进行漏洞批量扫描，要知道，半年前还有13个漏洞并没有加入他们的利用库中，这比很多漏洞扫描工具的更新速度还要快。

此外还将对近期披露的关于网军与僵尸网络合作共赢一事阐述。

## ECHOBOT僵尸网络

最新的僵尸网络参考平底锅的文章[1]中提及的ECHOBOT最新变种，从恶意软件的代码以及种类可见，其模块众多，跨多平台，内置71个漏洞利用代码，其中每个漏洞利用语句的变量名都代表了每个漏洞的所攻击的中间件。

![](https://p3.ssl.qhimg.com/t01d7db150dd5ef4010.png)

▲截图用Hash：b4135621d623676cc021c570aea07964

本着推动国内安全厂商对该僵尸网络防护能力提升的原则，我们搬运了平底锅整理的漏洞利用列表，仅供参考。

一、Yachtcontrol-船用电子设备和船用导航软件的web服务器

CVE-2019-17270 扫描端口8081

![](https://p5.ssl.qhimg.com/t0199299e96ecbd4819.png)

二、Technicolor TD5130v2和Technicolor TD5336路由器

CVE-2019-18396 / CVE-2017-14127 扫描端口161

三、AVCON6视频会议系统存在AVCON6远程执行代码漏洞

![](https://p5.ssl.qhimg.com/t01b49b10c27a51f5da.png)

四、Enigma网管系统 v65.0.0

CVE-2019-16072

![](https://p5.ssl.qhimg.com/t018c5090e40ef6fc60.png)

五、三菱电机smartRTU＆INEA ME-RTU

CVE-2019-14931

![](https://p5.ssl.qhimg.com/t0133e7637330c0871c.png)

六、适用于Linux服务器的Sar2HTML绘图工具v3.2.1

Sar2HTML远程执行代码

![](https://p0.ssl.qhimg.com/t0126e3d86da854bb8c.png)

七、NetGain企业管理系统

CVE-2017-16602

![](https://p4.ssl.qhimg.com/t01a23316f0ffbaca73.png)

八、Citrix NetScaler SD-WAN 9.1.2.26.561201设备

CVE-2017-6316

![](https://p4.ssl.qhimg.com/t012d9d27ed50313491.png)

九、Thomson Reuters Velocity Analytics Vhayu Analytic Servers 6.94 build 2995

CVE-2013-5912

![](https://p3.ssl.qhimg.com/t01a788b82ad2af3bab.png)

十、ACTi ASOC 2200 Web Configurators 2.6及更低版本远程执行代码漏洞

![](https://p3.ssl.qhimg.com/t0133a2de9c9c61947e.png)

十一、3Com OfficeConnect路由器远程执行代码

![](https://p3.ssl.qhimg.com/t01a25a4fd53d2179d6.png)

十二、Barracuda 防垃圾邮件防火墙versions 3.3.x

![](https://p3.ssl.qhimg.com/t0117a1bf81b6759bc8.png)

十三、CCBill 在线支付系统远程代码执行

![](https://p3.ssl.qhimg.com/t0123405d4c51d18a71.png)

剩下的58个漏洞编号列表以及其他漏洞执行语句可见以下链接，可复制

[1]<https://github.com/pan-unit42/iocs/blob/master/mirai/ECHOBOT_28thOct2019.md>

[2]<https://github.com/pan-unit42/iocs/blob/master/mirai/ECHOBOT_6thAug2019.md>

[3]<https://unit42.paloaltonetworks.com/new-mirai-variant-adds-8-new-exploits-targets-additional-iot-devices/>

此外，该变种还采用了新的凭据爆破账号，猜测某些IOT厂商又设置了默认的“后门账号”。

![](https://p4.ssl.qhimg.com/t0172264ab7af816707.png)

## 僵尸网络与网军合作

从上面这个案例可见，当僵尸网络部署了大批有效的漏洞武器后，鉴于全世界范围内很多设备并没有及时更新的情况下，大批主机将会受控，并且基于受控主机的基础上进行一步进行横向扩展和感染，尤其是一个僵尸网络病毒感染了一台内网主机之后。

那么僵尸网络运营商在获取了大量的僵尸主机（肉鸡）后，他们会做些什么？

主要有两个方向：

  1. 通过肉鸡本身盈利，例如大批量挖矿，或针对指定目标发起DDOS攻击敛财，服务器勒索。
  2. 出售肉鸡盈利

这里就要提一下第二个方向。

如今的一些有攻击策略的，擅长隐藏自身的APT组织(网军)，都在想方设法在网络侧下功夫，这也就意味着会发生下面这个场景：

当安全分析人员在获取到一个攻击者域名时，发现该域名被某威胁情报源打标签为Mirai，也就是上面提到的僵尸网络，大部分安全分析人员会如何处理？

报告给客户，这是一个僵尸网络病毒，不用分析了，按照网上的教程清除吧。

但是如果这是网军从僵尸网络运营商处购买肉鸡，从而发起攻击呢？

目前已知就有两个组织是这么干的。

  1. 俄罗斯：2015年被发现 GameOver Zeus恶意软件僵尸网络背后的策划者正在帮助俄罗斯情报部门从他感染的计算机上收集敏感文件。

2019年被美国发现 Dridex恶意软件僵尸网络的管理员与俄罗斯国家情报部门合作搜索敏感数据。

  2. 朝鲜[2]：

2019年，朝鲜网军Lazarus 被曝与Trickbot合作，获取僵尸主机作为回连资源，其中有一个域名与该组织资产重叠。

![](https://p1.ssl.qhimg.com/t01b3e028da24f8971c.png)

![](https://p1.ssl.qhimg.com/t0129b5bf42f72aa5f8.png)

也因此，奇安信威胁情报中心加大了对僵尸网络的监控与分析，为了防止网军掺杂其流量进行攻击，影响追踪效果。

## 总结

物联网
IoT引爆家电、家居、手机等多个行业，主要原因正是各项技术和各个企业的落地实践越来越成熟。正如科幻大片中的场景，当大部分的东西都能被感知，人与物的沟通、物与物的协作更加顺畅后，毫无疑问，智能家居将会成为家电产业的第三战场，带来的不只是商业机会和增长点，还有更多的空间和舞台，以及大量的僵尸主机。

显而易见，新战场将属于物联网IOT，在路由器，摄像头，智能家居漏洞频发的时代，你家里的电冰箱都可能作为攻击源的一部分，这恰恰会成为网军在斑驳杂乱的流量中宛如一只猎豹伺机而动，猎杀目标无形无踪。

这与本文前面提到的僵尸网络变种的进攻思路具备一致性，路由器，防火墙，IP摄像机，船舶管理系统，服务器管理实用程序，工业可编程逻辑控制器，在线支付系统等等这些涉及各行各业的工作必需系统出现在了大批量的攻击列表中，这也恰恰体现了一种攻击思路：广撒网，精聚焦。

未来僵军合作趋势恐愈演愈烈，奇安信威胁情报中心将聚焦各行各业的定向性攻击，挖掘未知威胁，更新防御对策，抵御相关攻击的发起。

## IOC

<https://github.com/pan-unit42/iocs/blob/master/mirai/ECHOBOT_28thOct2019.md>

## 参考链接：

[1]<https://unit42.paloaltonetworks.com/mirai-variant-echobot-resurfaces-with-13-previously-unexploited-vulnerabilities/>

[2]<https://labs.sentinelone.com/the-deadly-planeswalker-how-the-trickbot-group-united-high-tech-crimeware-apt/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/195302](/post/id/195302)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [僵尸网络](/tag/僵尸网络)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

