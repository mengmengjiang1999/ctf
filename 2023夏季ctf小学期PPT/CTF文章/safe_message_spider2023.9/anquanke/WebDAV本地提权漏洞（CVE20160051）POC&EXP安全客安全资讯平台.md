# WebDAV本地提权漏洞（CVE-2016-0051）POC & EXP

阅读量 **97864**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-02-17 11:41:03

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**漏洞信息**

该漏洞存在于Microsoft Web 分布式创作和版本管理 (WebDAV)中，如果 Microsoft Web 分布式创作和版本管理 (WebDAV)
客户端验证输入不当，那么其中就会存在特权提升漏洞。成功利用此漏洞的攻击者可以使用提升的特权执行任意代码。

若要利用此漏洞，攻击者首先必须登录系统。然后，攻击者可以运行一个为利用此漏洞而经特殊设计的应用程序，从而控制受影响的系统。

工作站和服务器最易受此攻击威胁。此安全更新程序通过更正 WebDAV 验证输入的方式来修复这个漏洞。

**漏洞影响范围**

Windows Vista SP2 x86 & x64 （特权提升）

Windows Server 2008 SP2 x86 & x64 （特权提升）

Windows Server 2008 R2 SP1 x64（特权提升）

Windows 7 SP1 x86 & x64 （特权提升）

Windows 8.1 x86 & x64（拒绝服务）

Windows Server 2012（拒绝服务）

Windows Server 2012 R2（拒绝服务）

Windows RT 8.1（拒绝服务）

Windows 10（拒绝服务）

**POC & EXP**

漏洞作者发布了蓝屏的POC以及用于 **32位win7系统** 的提权EXP

地址：

[https://github.com/koczkatamas/CVE-2016-0051](https://github.com/koczkatamas/CVE-2016-0051)

**Windows 7 SP1 x86 本地提权演示：**

**Windows 10 x64蓝屏演示：**

**修复建议**

通过windows更新程序自动下载并安装更新程序。或前往[微软安全中心](https://technet.microsoft.com/library/security/ms16-016)获取独立的更新程序包。

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83483](/post/id/83483)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

