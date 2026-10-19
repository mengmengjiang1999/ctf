# Apache Synapse 远程代码执行漏洞（CVE–2017–15708）预警

阅读量 **182552**

发布时间 : 2017-12-12 11:33:40

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01ef7bf3563cad0a94.png)

## 0x00 背景

Apache Synapse 是一个简单、轻量级的高性能企业服务总线 (ESB)，它是在 Apache Software Foundation 的
Apache License Version 2.0 下发布的。使用 Apache Synapse，您可以通过 HTTP、HTTPS、Java™
Message Service (JMS)、简单邮件传输协议 (SMTP)、邮局协议版本 3
(POP3)、FTP、文件系统和许多其他传输介质筛选、转换、路由、操作和监视经过大型企业系统的 SOAP、二进制文件、XML 和纯文本消息。

在 2017 年 12 月 10 日，Apache 官方公开了关于 Apache Synapse
存在严重漏洞（CVE-2017-15708），可导致远程代码执行，360CERT 随后对该漏洞进行了分析验证。

## 0x01 漏洞概述

Apache Synapse 在启动后会开启 RMI 服务（端口 1099）,由于该服务未对请求的对象类型进行校验，存在反序列化漏洞。同时，Apache
Synapse 使用了版本较低的库 commons-collections-3.2.1 。通过使用该库中存在的 Gadget
在反序列化时是可以实现远程代码执行。

使用 ysoserial 来做一个利用验证

![](https://cert.360.cn/static/fileimg/CVE-2017-15708_1_1512991808.png)

由于是出现在 RMI 的反序列漏洞，如果用户使用的 Java 的版本高于 8u121，7u131，6u141
也不会受到该漏洞的影响，因为在后面的版本加入了反序列化过滤机制。

## 0x02 全网影响

影响版本

Apache Synapse 3.0.0, 2.1.0, 2.0.0, 1.2, 1.1.2, 1.1.1

根据 360CERT 全网资产检索平台实时显示数据

![](https://cert.360.cn/static/fileimg/CVE-2017-15708_2_1512991816.png)

## 0x03 修复建议

  1. 升级到最新版本 3.0.1
  2. 使用高版本的 Java

## 0x04 时间线

2017 年 12 月 10 日 Apache Synapse 远程代码执行漏洞公开

2017 年 12 月 11 日 360CERT发布预警

## 0x05 参考链接

<http://www.openwall.com/lists/oss-security/2017/12/10/4>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/90183](/post/id/90183)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CVE](/tag/CVE)
  * [漏洞预警](/tag/漏洞预警)
  * [Apache](/tag/Apache)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

