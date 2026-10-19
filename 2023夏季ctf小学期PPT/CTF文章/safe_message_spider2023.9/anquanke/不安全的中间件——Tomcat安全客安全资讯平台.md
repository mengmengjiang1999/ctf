# 不安全的中间件——Tomcat

阅读量 **351786**

发布时间 : 2020-11-19 16:00:36

 **x**

##### 译文声明

本文是翻译文章，文章原作者 酒仙桥6号部队，文章来源：酒仙桥6号部队

原文地址：<https://mp.weixin.qq.com/s/MmLhJ2EbvmuJx2YTSeeTyQ>

译文仅供参考，具体内容表达以及含义原文为准。

本文翻译自酒仙桥6号部队
[原文链接](https://mp.weixin.qq.com/s/MmLhJ2EbvmuJx2YTSeeTyQ)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **酒仙桥六号部队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/223002](/post/id/223002)

安全客 - 有思想的安全新媒体

本文转载自: [酒仙桥6号部队](https://mp.weixin.qq.com/s/MmLhJ2EbvmuJx2YTSeeTyQ)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/MmLhJ2EbvmuJx2YTSeeTyQ>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t0110bc5d794d277012.png) 酒仙桥六号部队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

