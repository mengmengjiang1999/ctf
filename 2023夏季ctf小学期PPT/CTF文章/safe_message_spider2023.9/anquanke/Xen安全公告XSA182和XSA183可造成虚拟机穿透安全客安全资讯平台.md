# Xen安全公告XSA-182和XSA-183-可造成虚拟机穿透

阅读量 **109156**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-07-26 21:32:07

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**author:cyg07@360云安全团队**

**今天Xen更新了2个重要的补丁公告XSA-182和XSA-183,其中XSA-182可以造成直接的虚拟机穿透,建议使用Xen
PV模式的云平台尽快更新补丁。**

XSA-182问题描述:

Xen
PV模式存在快速路径来更新已存在的页表目录,该功能主要是为了在安全状态(认为是安全的状态下)下减少重复验证的开销,比如只清除页表上的Access/Dirty。但是考虑得还是太宽泛,不够严谨、安全。

从补丁上看,官方启用了标志位白名单策略来修复这个问题。

影响:

PV模式的虚拟机管理员可以利用该漏洞穿透到宿主机系统。

影响系统:

所有的Xen版本都受影响。

使用PV模式的x86硬件平台可以被攻击者利用。

只运行HVM模式或ARM虚拟机的Xen平台无法被攻击者利用。

缓解措施:

只启用HVM模式运行Xen虚拟机。

更多信息请查看:

[http://xenbits.xen.org/xsa/advisory-182.html](http://xenbits.xen.org/xsa/advisory-182.html)

[http://xenbits.xen.org/xsa/advisory-183.html](http://xenbits.xen.org/xsa/advisory-183.html)

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360GearTeam** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84285](/post/id/84285)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t01c466407f2a92aaf5.jpg)
360GearTeam

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

