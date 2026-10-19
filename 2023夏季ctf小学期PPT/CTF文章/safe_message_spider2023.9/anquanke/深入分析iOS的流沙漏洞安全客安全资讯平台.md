# 深入分析iOS的流沙漏洞

阅读量 **86360**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-09-09 11:13:29

 **x**

##### 译文声明

本文是翻译文章，文章来源：默白@360安全播报

原文地址：<http://blog.trendmicro.com/trendlabs-security-intelligence/sinking-into-the-ios-quicksand-vulnerability/>

译文仅供参考，具体内容表达以及含义原文为准。

我们对iOS的流沙漏洞(标有CVE-2015-5749)进行调查,得出的结论是:这个安全漏洞,尽管它对机密数据具有严重的危险性,但由于其需要特定的条件而难以被利用。

例如,MDM产品必须支持并使用“推送配置”的功能;这个功能通常允许设备管理员将配置信息和应用程序一起推送到用户设备。这是苹果公司所鼓励的做法。

**  
**

**深入分析流沙漏洞**

根据报道,流沙漏洞绕过iOS沙箱的保护,影响移动设备的管理(MDM)客户端。去年八月之前到2015年八月发布的8.4.1iOS版本的安全问题都受此影响。

iOS的沙箱主要用来分开或分离的每一个来自其他应用程序以及操作系统(OS)的应用程序。它的功能是作为一项安全措施,一种防止任何恶意应用程序访问设备上的其他应用程序的内容的“安全网”。不过,该漏洞允许攻击者使用带有恶意代码的应用程序去查找,从而找到了存储在设备内部其他应用的配置等信息。

图一:收录在 client中的目录“/Library/Managed Preferences/mobile/.”

图2.攻击者可以利用这个漏洞来读取该配置的敏感信息

另外,攻击者也可能诱使员工,并且让用户通过App
Store或企业凭证安装一个应用程序(这事实上是恶意软件)在MDM的客户端。在企业的资源调配上,组织和公司可以建立自己的内部应用程序,从而不必经过苹果商店进行检查和验证。

想象一下,一个企业的设置,其中的内部企业应用程序是由MDM客户端所部署。这些MDM客户端能够被IT管理员所使用去控制,并且监督全体员工使它们在监察下访问企业网络和敏感信息。攻击者可能会利用“可信源”这一概念,可能诱使员工进入安装恶意应用的程序,并从他们的MDM认证它是合法的。

**  
**

**保持事物(在安全性方面)的角度**

尽管对企业数据有严重风险,但是如果该漏洞在外界被成功利用的影响是很小的,首先,不是所有的iOS设备都由MDM客户端开启。我们建议用户更新他们的iOS设备到其最新版本。如果部署的应用程序是有效的,合法的,对于内部的应用程序,先验证他们的IT管理员是至关重要,。这可以防止任何恶意的应用程序进入企业网络,从而窃取敏感数据。

本文翻译自默白@360安全播报 [原文链接](http://blog.trendmicro.com/trendlabs-security-intelligence/sinking-into-the-ios-quicksand-vulnerability/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82355](/post/id/82355)

安全客 - 有思想的安全新媒体

本文转载自: [默白@360安全播报](http://blog.trendmicro.com/trendlabs-security-intelligence/sinking-into-the-ios-quicksand-vulnerability/)

如若转载,请注明出处： <http://blog.trendmicro.com/trendlabs-security-intelligence/sinking-into-the-ios-quicksand-vulnerability/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

