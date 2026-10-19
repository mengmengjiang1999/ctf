# 1月9日安全热点–苹果为Spectre漏洞发布iOS和macOS更新

阅读量 **142680**

发布时间 : 2018-01-09 10:44:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)

## 资讯类

Win10用户安装Meltdown/Spectre漏洞的安全更新KB4056892后无法启动系统

许多用户在微软社区（answers.microsoft.com）下抱怨说，在安装了Windows对
Meltdown/Spectre漏洞的安全更新KB4056892之后，搭载AMD速龙的PC就无法启动了，无法进入安全模式，只能看到Windows启动logo。多次启动失败之后，就开始回滚，然后显示错误0x800f0845
。不幸的是，在没有修改gpedit（组策略）的情况下，很难禁用掉自动更新，于是就开始不停地安装更新然后回滚。一些用户称即便重装Windows10也不能解决。  
详情见：

<https://answers.microsoft.com/en-us/windows/forum/windows_10-update/after-installation-of-kb4056892-boot-failure-after/6c015632-2a45-4725-a882-f231f8c88f36?auth=1>

<https://www.reddit.com/r/sysadmin/comments/7ode4s/problems_with_windows_7_quality_rollup_kb4056894/>

<https://answers.microsoft.com/en-us/windows/forum/windows_7-update/stop-0x000000c4-after-installing-kb4056894-2018-01/f09a8be3-5313-40bb-9cef-727fcdd4cd56?auth=1>

苹果为Spectre漏洞发布iOS和macOS更新

（苹果发布了macOS High Sierra 10.13.2补充更新，iOS 11.2.2和Safari
11.0.2，包含对Spectre漏洞的缓解措施。此前在2017年12月发布了iOS 11.2，macOS 10.13.2和tvOS
11.2，以修复Meltdown漏洞（CVE-2017-5753））

<https://www.bleepingcomputer.com/news/apple/apple-releases-security-updates-for-spectre-cpu-flaw/>

<https://support.apple.com/en-us/HT208397>

<https://support.apple.com/en-us/HT208401>

WPA3 WiFi认证协议的第一份正式草案将在今年晚些时候发布

![](https://p4.ssl.qhimg.com/dm/1024_373_/t01d8578e20bf1697eb.png)

<https://www.bleepingcomputer.com/news/hardware/wpa3-wifi-standard-announced-after-researchers-kracked-wpa2-three-months-ago/>

腾讯安全玄武实验室发布的对Spectre漏洞的在线监测工具

<http://xlab.tencent.com/special/spectre/spectre_check.html>

2017 Black Hat Europe大会回顾

<https://researchcenter.paloaltonetworks.com/2018/01/2017-black-hat-europe-noc-tales-coverage-compromise/>

## 技术类

Spectre CVE-2017-5753 PoC for Android/ARM64

<https://github.com/V-E-O/PoC/blob/master/CVE-2017-5753/source.c>

mcafee发布2018年威胁预测

<https://securingtomorrow.mcafee.com/consumer/mcafee-shares-threat-predictions-2018-saying-goes-forewarned-forearmed/>

VirusTotal Graph增加新特性，查看各文件的相关性更容易

<https://www.bleepingcomputer.com/news/security/new-virustotal-graph-makes-it-easy-to-visualize-malware/>

![](https://p3.ssl.qhimg.com/dm/1024_670_/t010f1713572c97382b.jpg)

mcafee对瞄准平昌奥运会的恶意文件的分析

<https://securingtomorrow.mcafee.com/mcafee-labs/malicious-document-targets-pyeongchang-olympics/>

使用硬件性能计数器检测Spectre & Meltdown漏洞

<https://www.endgame.com/blog/technical-blog/detecting-spectre-and-meltdown-using-hardware-performance-counters>

Spectre & Meltdown漏洞检测工具

<https://github.com/speed47/spectre-meltdown-checker>

看我如何利用D-Link 815N

<https://cr0n1c.wordpress.com/2018/01/08/exploiting-cheap-labor/>

<https://github.com/Cr0n1c/dlink_815_shell_poc/blob/master/dlink_auth_rce>

Oracle WebLogic <10.3.6 wls-wsat组件反序列化远程命令执行

<https://cxsecurity.com/issue/WLB-2018010082>

Cisco Talos团队对Meltdown and Spectre漏洞的解读

<http://blog.talosintelligence.com/2018/01/meltdown-and-spectre.html>

FiberHome LM53Q1多个漏洞（CVE-2017-16885, CVE-2017-16886, CVE-2017-16887）的exploit

<https://www.exploit-db.com/exploits/43460/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **77caikiki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/94023](/post/id/94023)

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

