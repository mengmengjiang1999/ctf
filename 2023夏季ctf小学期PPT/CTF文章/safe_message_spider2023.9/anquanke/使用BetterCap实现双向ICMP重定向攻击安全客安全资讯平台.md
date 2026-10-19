# 使用BetterCap实现双向ICMP重定向攻击

阅读量 **144941**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-01-12 17:34:02

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<http://www.evilsocket.net/2016/01/10/bettercap-and-the-first-real-icmp-redirect-attack/>

译文仅供参考，具体内容表达以及含义原文为准。

**BetterCap的下一个版本将包含一个新的攻击机制，来替代原本默认使用的ARP模块。**

新模块会执行MITM攻击（MITM:中间人攻击，一种“间接”入侵攻击），它完全自动化，并有ICMP全双工重定向特性。我在Zimperium的同事发现了这种攻击方式，称之为DoubleDirect攻击。

BetterCap将会是第一个被用作为MITM攻击的框架，它可以100%地继承原来的特性，不需要任何其他的设备作为辅助，便可以开始工作。

如果你认为BetterCap早在几年前就发布了的话，那么我有必要提醒你关注一些有关BetterCap的说明：

很显然，你必须熟悉你的网络拓扑结构。比方说，当你在使用一台交换机时，面对着不同的端口，你就需要采用不同的攻击方式，例如：ARP中毒攻击。

是的，除非你已经能够管理网络流量，否则BetterCap的ICMP框架就是无效的（而在哪种情况下，你必须选择采用MITM攻击方式呢？）

从另一个角度说，MITM也不是太好的选择。如果你仔细看看它的代码，你就会发现只有ICMP攻击者才会这样做：

这基本上只能起到重设路由网关流量的作用，而没其他用处。

为了能够得到一个真正意义上的，能供ICMP重定向攻击方式使用的数据包，你就必须重设路由网关和路由上的其他目标地址。这就是我在Zimperium网站的博文中所写到的，为什么要使用DNS监听线程的原因。

**请继续关注吧，下一个版本很快就会更新了。**

本文翻译自360安全播报 [原文链接](http://www.evilsocket.net/2016/01/10/bettercap-and-the-first-real-icmp-redirect-attack/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ResoLuT1On** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83286](/post/id/83286)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](http://www.evilsocket.net/2016/01/10/bettercap-and-the-first-real-icmp-redirect-attack/)

如若转载,请注明出处： <http://www.evilsocket.net/2016/01/10/bettercap-and-the-first-real-icmp-redirect-attack/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t016458bfee0c6f1be9.jpg)
ResoLuT1On

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

