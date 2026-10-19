# Sodinokibi勒索病毒全解

阅读量 **250787**

发布时间 : 2019-07-11 15:30:06

 **x**

##### 译文声明

本文是翻译文章，文章原作者 安全分析与研究，文章来源：安全分析与研究

原文地址：<https://mp.weixin.qq.com/s/iK8tQQ2sTa6YiVeoQlphMQ>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01edfec5ec7a101006.jpg)

此前我写过一篇《威胁情报：揭密全球最大勒索病毒GandCrab的接班人》，揭露了一些关于Sodinokibi勒索病毒的传播渠道与细节，有兴趣的可以关注我的公众号，然后翻看之前的内容，最近国外一家安全公司也发布了一个报告，揭露Sodinokibi勒索病毒的相关信息，详细报告下载链接：

<https://www.tgsoft.it/immagini/news/20190705Sodinokibi/Sodinokibi_eng.pdf>

我仔细研究了它的报告，发现它跟我之前分析基本一致，这款勒索病毒首次出现是在2019年4月，利用Oracle WebLogic
Server漏洞传播，C.R.A.M. TG Soft(反恶意软件研究中心) 在最近几个月分析了这款勒索病毒的演变

这款勒索病毒在国内首次发现是4月份，于2019年5月24日首次在意大利被发现，使用RDP攻击的方式进行传播感染

Sodinokibi勒索病毒的作者，如果这是他们开发的第一个勒索病毒版本，我可以猜测他们要么就是有很长时间的安全研究经验，要么就是拿到了GandCrab的部分源代码进行改装，我在四月份就曾分析过这款勒索病毒与GandCrab中使用的CC通过的代码非常相似，可以确定就是这款勒索病毒肯定与GandCrab有关系，至少是利用了GandCrab的部分渠道进行传播，GandCrab勒索于六月份开始关闭了，似乎Sodinokibi勒索病毒成为了GandCrab接班人

国外这份分析报告详细介绍了Sodinokibi勒索病毒的相关信息，包含：

![](https://p3.ssl.qhimg.com/t01784906a1ed402f0f.png)

Sodinokibi感染传播方式，就目前发现的主要利用以下几种方式：

Oracle Weblogic Server漏洞

RDP攻击

垃圾邮件

APT水坑攻击方式

漏洞利用工具包和恶意广告下载

Sodinokibi会在内存中解密出一个json格式的配置信息，如下所示：

![](https://p0.ssl.qhimg.com/t014f5ce01de122a122.png)

配置文件的格式，如下所示：

![](https://p3.ssl.qhimg.com/t0121f6fd9c3e430cb6.png)

各个字段对应的描述信息，如下所示：

![](https://p4.ssl.qhimg.com/t013d2a9ef10005480a.png)

其中C2域名，有几百个之多

这个分析报告写的非常详细了，很值得一看，Sodinokibi勒索病毒会不会是下一个GandCrab，需要安全研究人员继续追踪，不过就目前发现的Sodinokibi勒索病毒分析结果来看，这款勒索病毒未非出现新的变种或大的变种，必竟这款勒索病毒出来才两个多月，在未来一定会出现它的新的变种和版本，因为背后的运营团队不会就此罢手，一定会不断更新它的版本和渠道……

Sodinokibi勒索病毒已经成为了GandCrab勒索病毒的接班人，可是遗憾的是：这款勒索病毒目前还没解密工具，全球各大企业和机构一定要做好相应的防范措施，以防中招!

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/iK8tQQ2sTa6YiVeoQlphMQ)

本文翻译自安全分析与研究
[原文链接](https://mp.weixin.qq.com/s/iK8tQQ2sTa6YiVeoQlphMQ)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181812](/post/id/181812)

安全客 - 有思想的安全新媒体

本文转载自: [安全分析与研究](https://mp.weixin.qq.com/s/iK8tQQ2sTa6YiVeoQlphMQ)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/iK8tQQ2sTa6YiVeoQlphMQ>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

