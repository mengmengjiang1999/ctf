# 1月13日安全热点–Intel的AMT安全问题/DNS篡改恶软OSX/MaMi

阅读量 **149294**

发布时间 : 2018-01-13 11:07:54

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)

## 资讯类

2018年才过去两周，就迎来了macOS平台的DNS篡改恶意软件OSX/MaMi

<https://www.bleepingcomputer.com/news/apple/the-first-mac-malware-of-2018-is-a-dns-hijacker-called-mami/>

<https://www.tomsguide.com/us/mami-mac-malware,news-26451.html>

这个恶意软件的信息最早出现在malwarebytes的论坛上（一个网友不小心安装了什么然后他的DNS就被篡改了）

![](https://p0.ssl.qhimg.com/dm/1024_278_/t01e39a80b82021d02a.png)

<https://forums.malwarebytes.com/topic/218198-dns-hijacked/>

该恶意软件以未签名的Mach-O 64位二进制文件的形式分发，现在VirusTotal上可已经可以检测到（16/59）

<https://www.virustotal.com/#/file/5586be30d505216bdc912605481f9c8c7bfd52748f66c5e212160f6b31fd8571/detection>

![](https://p1.ssl.qhimg.com/dm/1024_525_/t01b8ac939db8ad3609.png)

样本下载：<https://objective-see.com/downloads/malware/MaMi.zip>

解压密码：infect3d

objective-see对macOS平台的DNS篡改恶意软件OSX/MaMi的分析

<https://objective-see.com/blog/blog_0x26.html>

F-Secure的Harry
Sintonen发现了Intel的AMT中一个安全问题，该问题可导致攻击者在几秒钟内完全控制用户的设备，影响全球数百万台企业笔记本电脑。Harry解释了这个问题，并建议了应该如何缓解。  
<https://thehackernews.com/2018/01/intel-amt-vulnerability.html>

<https://business.f-secure.com/intel-amt-security-issue>

演示视频：  
  
您的浏览器不支持video标签  

本周勒索软件盘点

<https://www.bleepingcomputer.com/news/security/the-week-in-ransomware-january-12th-2018-ethereum-and-small-variants/>

Google Play的游戏应用中发现了投放色情广告的恶意软件  
<https://blog.checkpoint.com/2018/01/12/childrens-apps-google-play-display-porn-ads/>

![](https://p3.ssl.qhimg.com/t01b83c394879b0a97b.jpg)

## 技术类

CVE-2018-0802的PoC

<https://github.com/zldww2011/CVE-2018-0802_POC>

How I exploited ACME TLS-SNI-01 issuing Let’s Encrypt SSL-certs for any domain
using shared hosting

<https://labs.detectify.com/2018/01/12/how-i-exploited-acme-tls-sni-01-issuing-lets-encrypt-ssl-certs-for-any-domain-using-shared-hosting/>

IDACyber：一款IDA Pro数据可视化插件

<https://github.com/patois/IDACyber>

CVE-2018-1000001：libc的realpath() buffer underflow

<https://www.halfdog.net/Security/2017/LibcRealpathBufferUnderflow/>

邮件列表：

<http://seclists.org/oss-sec/2018/q1/38>

<http://seclists.org/oss-sec/2018/q1/42>

看我如何结合两个漏洞拿到雅虎账号的通讯录

<http://www.sxcurity.pro/2018/01/11/chaining-yahoo-bugs/>

演示视频：

  
您的浏览器不支持video标签  

2017 SANS Holiday Hack Challenge Writeup

<https://0xd13a.github.io//2017-SANS-Holiday-Hack-Challenge-Writeup/>

Zone transfers in The Netherlands

<https://binaryfigments.com/2018/01/12/zone-transfers-in-the-netherlands/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **77caikiki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/94632](/post/id/94632)

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

