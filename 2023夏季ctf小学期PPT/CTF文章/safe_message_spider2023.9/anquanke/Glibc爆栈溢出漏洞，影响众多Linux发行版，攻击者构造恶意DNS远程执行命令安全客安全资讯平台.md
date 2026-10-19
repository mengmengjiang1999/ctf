# Glibc爆栈溢出漏洞，影响众多Linux发行版，攻击者构造恶意DNS远程执行命令

阅读量 **107075**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-02-17 13:29:26

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**Glibc,GNU C库内核受到去年GHOST
vulnerability的影响,容易受到另一个重大漏洞几乎所有的Linux机器,以及web服务API和主要web框架中运行的代码都受影响。**

cve-2015-7547,是一个基于堆栈缓冲区溢出，glibc中getaddrinfo函数在处理特定dns
response数据包时存在栈溢出，攻击者可通过构建恶意dns服务或中间人的方法对受害者发起攻击，可造成远程代码执行。

**补丁地址：**

<https://sourceware.org/ml/libc-alpha/2016-02/msg00416.html>

**修复建议：**

主要发行版以发布安全补丁，按照各发行版本安全公告升级glibc

  

**相关文章：**

[https://sourceware.org/ml/libc-alpha/2016-02/msg00416.html](http://https://sourceware.org/ml/libc-alpha/2016-02/msg00416.html)

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83485](/post/id/83485)

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

