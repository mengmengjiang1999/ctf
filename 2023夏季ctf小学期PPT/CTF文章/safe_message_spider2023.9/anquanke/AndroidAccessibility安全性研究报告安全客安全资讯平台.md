# Android Accessibility安全性研究报告

阅读量 **109072**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-09-08 10:33:05

 **x**

##### 译文声明

本文是翻译文章，文章来源：360烽火实验室

译文仅供参考，具体内容表达以及含义原文为准。

**摘要**

Android Accessibility被称为无障碍或残疾人模式，设计初衷是为了帮助特殊用户更好地使用Android设备。

从使用Android
Accessibility技术的样本占样本总数百分比看，截止2012年仅有0.015%，截止2015年不足0.5%，2016年上半年占比超过2.6%。

从使用Android Accessibility技术的样本数量看，2016年上半年是2015年全年的3倍。

从使用Android Accessibility技术场景看，可以分为合理利用、提升体验、灰色地带和肆意滥用。

利用Android Accessibility技术的恶意样本呈现出明显的逐年增长趋势，2016年上半年恶意样本数量接近于2015年同期的2.5倍。

360烽火实验室最新发现伪装成手机安全软件，利用Android
Accessibility技术劫持浏览器地址栏的木马，该木马同时具备隐藏图标、自我保护等多种对抗手段。

Android Accessibility滥用案例已被发现的主要归类为三类情况：恶意安装、广告干扰和窃取信息。

使用人群与权限控制的矛盾和用户对Accessibility的认识不足成为Android Accessibility被滥用的主要因素。

**云盘链接** ：<https://yunpan.cn/cMCjSR4sk982H>（提取码：7bcd）

本文翻译自360烽火实验室 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360安全卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84525](/post/id/84525)

安全客 - 有思想的安全新媒体

本文转载自: [360烽火实验室]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t01cc856584b7ed76c0.jpg) 360安全卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

