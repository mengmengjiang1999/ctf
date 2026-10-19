# Adobe ColdFusion 任意命令执行漏洞(CVE–2017–11283, CVE–2017–11284)预警

阅读量 **267064**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-10-19 19:12:09

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**0x00 事件描述**

Adobe ColdFusion 在 2017 年 9 月 12 日发布的安全更新中提及到之前版本中存在严重的反序列化漏洞（
**CVE-2017-11283, CVE-2017-11284** ），可导致远程代码执行。当使用 Flex 集成服务开启 Remote Adobe
LiveCycle Data Management access 的情况下可能受到该漏洞的影响，使用该功能会开启 RMI 服务， **监听的端口为
1099** 。ColdFusion 自带的 Java 版本过低，不会在反序列化之前对 RMI 请求中的对象类型进行检验。

360CERT 经过分析验证，确认该漏洞确实存在，请相关用户尽快进行更新处理。

**0x01 影响版本**

1.ColdFusion (2016 release) Update 4 以及之前的版本

2.ColdFusion 11 Update 12 以及之前版本

**0x02 漏洞利用验证**

往 RMI 服务发送构造好的 payload 做一个简单的远程代码执行验证。

**0x03 修复方案**

1.在管理页面关闭 Remote Adobe LiveCycle Data Management access

2.升级最新补丁 ColdFusion (2016 release) Update 5，ColdFusion 11 Update 13

**0x04 时间线**

2017-9-12 Adobe ColdFusion 发布安全更新

2017-10-19 360CERT 发布漏洞预警

**0x05 参考链接**

<https://helpx.adobe.com/security/products/coldfusion/apsb17-30.html>

<https://nickbloor.co.uk/2017/10/13/adobe-coldfusion-deserialization-rce-cve-2017-11283-cve-2017-11238/>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87047](/post/id/87047)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

