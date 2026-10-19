# 【漏洞预警】The WireX Botnet预警公告

阅读量 **119207**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-29 20:13:13

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**0x00 事件公告**

2017年8月17日，名为WireX
BotNet的僵尸网络通过伪装普通安卓应用的方式大量感染安卓设备并发动了较大规模的DDoS攻击，此举引起了部分CDN提供商的注意，此后来自Akamai,
Cloudflare, Flashpoint, Google, Oracle Dyn, RiskIQ, Team Cymru等组织 **联合**
对该事件进行分析，并于8月28日发布了该事件的安全报告。

该安全报告分析表明，攻击者可能从7月中旬(可能更早)开始组建WireX BotNet，并通过小规模的攻击受害网络来牟利。8月7日左右，WireX
BotNet开始进行流量更大持续时间更长的DDoS攻击。从8月15日开始，WireX引发的DDoS事件源自至少 **7万个**
独立IP地址。8月17日攻击数据的分析显示，来自 **100多个国家** 的设备感染了WireX BotNet。

**WireX BotNet的源IP趋势**

WireX
BotNet主要伪装成带有极大的诱惑性和隐蔽性的视频播放器、铃声、文件管理器等无害应用，此前已发现大约有300种不同的移动应用程序分散在Google
Play商店中。目前Google删除了受影响的应用程序，并开始从所有设备中删除该恶意应用程序，但还不清楚具体有多少安卓设备被WireX感染。

目前，360手机卫士、360安全卫士和360手机助手在内的产品已经能准确地进行WireX
BotNet查杀，技术层面（分析报告见参考3）确定了国内有100多个WireX
BotNet相关的恶意安卓应用。请使用安卓设备的用户和相关的安卓应用市场尽快进行相关的查杀。

**0x01 影响面分析**

事件等级： 较大

感染了Google Play商店和部分安卓应用市场，可能有数万台安卓设备受影响。

**0x02 处理建议**

1、建议安卓用户安装360手机卫士等有效的终端防护应用进行防护；

2、建议各安卓应用市场对于存量和提交的应用进行安全扫描后再上架；

**0x03 时间线**

2017-8-28 事件披露

2017-8-29 360烽火实验室和360NetLab对WireX进行技术分析

2017-8-29 360CERT发布预警公告

**0x04 参考**

1、The WireX Botnet: How Industry Collaboration Disrupted a DDoS Attack

[https://blog.cloudflare.com/the-wirex-botnet/?utm_content=buffer9e1c5&utm_medium=social&utm_source=twitter.com&utm_campaign=buffer](https://blog.cloudflare.com/the-wirex-botnet/?utm_content=buffer9e1c5&utm_medium=social&utm_source=twitter.com&utm_campaign=buffer)

2、安卓DDOS僵尸网络：The WireX Botnet

<http://bobao.360.cn/learning/detail/4323.html>

3、关于“WireX Botnet”事件Android样本分析报告

<http://blogs.360.cn/blog/analysis_of_wirex_botnet>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86718](/post/id/86718)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

