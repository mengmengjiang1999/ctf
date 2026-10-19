# 1月8日安全热点–AMD CPU栈溢出漏洞

阅读量 **149128**

发布时间 : 2018-01-08 10:26:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)

## 资讯类

Google安全专家在AMD CPU中发现了一个新的栈溢出漏洞，攻击者可通过构造特殊的EK证书触发。  
(在管理TLV数据结构的时候缺少边界检查是导致此栈溢出的根本原因。)  
<http://securityaffairs.co/wordpress/67448/hacking/67448.html>

<https://www.theregister.co.uk/2018/01/06/amd_cpu_psp_flaw/>

四个团队是如何独立发现Spectre/Meltdown漏洞的  
<https://www.wired.com/story/meltdown-spectre-bug-collision-intel-chip-flaw-discovery/>

至少在2018年1月9日之前，Windows用户依然受Meltdown/Spectre漏洞影响

<https://neosmart.net/blog/2018/windows-vulnerable-to-meltdown-spectre-until-january-9/>

Intel面临着关于Meltdown和Spectre的集体诉讼

<https://news.hitb.org/content/intel-faces-class-action-lawsuits-regarding-meltdown-and-spectre>

Meltdown和Spectre漏洞的补丁已经出来了，但是并不解决任何问题

<https://news.hitb.org/content/meltdown-and-spectre-fixes-arrive-dont-solve-everything>

微软已经停止支持比特币作为微软产品的支付方式

<https://www.bleepingcomputer.com/news/cryptocurrency/microsoft-halts-bitcoin-transactions-because-its-an-unstable-currency/>

上周勒索软件回顾

<https://www.bleepingcomputer.com/news/security/the-week-in-ransomware-january-5th-2018-slow-for-the-holidays/>

## 技术类

一个硬件安全工程师眼中的Meltdown

<https://media.weibo.cn/article?id=2309404193352517074988>

Meltdown variant 3a的PoC（在用户态dump出ARM系统寄存器）  
<https://github.com/lgeek/spec_poc_arm>

In-Spectre-Meltdown：检测Meltdown & Spectre漏洞的工具  
<https://github.com/Viralmaniar/In-Spectre-Meltdown>

shimit：实现Golden SAML攻击的工具  
<https://github.com/cyberark/shimit>

IPFS—http的终极杀手

<https://weibo.com/ttarticle/p/show?id=2309404179043187580696>

文件上传漏洞扫描及利用工具  
<https://github.com/almandin/fuxploider>

Setting up a DNS Firewall on steroids

<https://navytitanium.github.io/DNSMasterChef/>

Very vulnerable ARM application (CTF风格的利用教程)

<https://github.com/bkerler/exploit_me>

Realmode Assembly – Writing bootable stuff – Part 6

<https://0x00sec.org/t/realmode-assembly-writing-bootable-stuff-part-6/4915>

Emotet Grinch又回归了

<https://blog.minerva-labs.com/the-emotet-grinch-is-back>

恶意软件反编译和脱壳

<https://0x00sec.org/t/malware-decompiling-and-unpacking-loda-keylogger/4896>

视频：<https://www.youtube.com/watch?v=DwC6VKN0CvM>

样本下载：<https://www.hybrid-analysis.com/sample/9300e6bbdb4bd12e1a1f58a5a50759811d39437e3cbe2769164d5d04e199656c>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **77caikiki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/93881](/post/id/93881)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [每日热点](/tag/每日热点)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t0142708c469a213013.png) 77caikiki

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

