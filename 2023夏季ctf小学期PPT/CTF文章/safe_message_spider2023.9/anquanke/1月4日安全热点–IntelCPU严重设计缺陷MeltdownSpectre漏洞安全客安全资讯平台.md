# 1月4日安全热点 – Intel CPU严重设计缺陷/Meltdown/Spectre漏洞

阅读量 **135429**

发布时间 : 2018-01-04 10:58:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01500f0590be491fc0.png)

## 资讯类

Intel处理器被曝存在严重设计缺陷

（Intel处理器芯片基础架构中被爆存在一个严重的设计缺陷。受此影响，Linux以及Windows不得不大幅改动、重新设计内核。Linux内核的修复代码已经公布，而微软将在下周二补丁日发布Windows补丁。）

<https://www.anquanke.com/post/id/93455>

Google称几乎所有1995年以来的CPU都受”Meltdown” 和 “Spectre”漏洞影响

<https://www.bleepingcomputer.com/news/security/google-almost-all-cpus-since-1995-vulnerable-to-meltdown-and-spectre-flaws/>

<https://security.googleblog.com/2018/01/todays-cpu-vulnerability-what-you-need.html?m=1>

视频演示：  
  
您的浏览器不支持video标签  

Google Project Zero团队发布了该CPU漏洞的详细描述

<https://googleprojectzero.blogspot.co.uk/2018/01/reading-privileged-memory-with-side.html?m=1>

据说是该CPU “Meltdown” 和 “Spectre”漏洞的PoC

<https://github.com/turbo/KPTI-PoC-Collection>

“Meltdown” 和 “Spectre”漏洞的区别（ **Meltdown** 只针对Intel，而 **Spectre适用于** Intel,
ARM, 和AMD 处理器）

<https://danielmiessler.com/blog/simple-explanation-difference-meltdown-spectre/>

### 各厂商/平台发布针对此次CPU漏洞的安全公告

ARM：<https://developer.arm.com/support/security-update>

Android: <https://source.android.com/security/bulletin/2018-01-01>

![](https://p1.ssl.qhimg.com/t01cbc7724020a56cbf.png)

Chromium发布Meltdown/Spectre漏洞的缓解措施：<https://www.chromium.org/Home/chromium-security/ssca>

Firefox：<https://blog.mozilla.org/security/2018/01/03/mitigations-landing-new-class-timing-attack/>

微软：<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV180002>

<https://support.microsoft.com/en-us/help/4056892/windows-10-update-kb4056892>

英伟达/NVIDIA: <https://forums.geforce.com/default/topic/1033210/geforce-drivers/nvidias-response-to-speculative-side-channels-cve-2017-5753-cve-2017-5715-and-cve-2017-5754/>

Google移除掉Play Store的36个冒充是安全防护软件的app

（实际上，这些应用程序包含的代码主要是显示虚假的安全警报，显示广告，并秘密收集个人数据。）

<https://www.bleepingcomputer.com/news/security/google-removes-36-fake-android-security-apps-packed-with-adware/>

来自趋势科技的分析：

<http://blog.trendmicro.com/trendlabs-security-intelligence/apps-disguised-security-tools-bombard-users-ads-track-users-location/>

![](https://p4.ssl.qhimg.com/t01de88296d09a8aa0f.png)

## 技术类

NSA的 ExplodingCan exploit的Python实现

<https://github.com/danigargu/explodingcan>

![](https://p5.ssl.qhimg.com/t015cfc4412908d7811.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **77caikiki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/93466](/post/id/93466)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [每日热点](/tag/每日热点)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t0142708c469a213013.png) 77caikiki

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

