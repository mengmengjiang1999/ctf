# 一封钓鱼邮件带来著名的Dridex银行木马最新变种

阅读量 **249152**

发布时间 : 2019-07-01 14:30:06

 **x**

##### 译文声明

本文是翻译文章，文章原作者 CyberThreatAnalyst，文章来源：CyberThreatAnalyst

原文地址：<https://mp.weixin.qq.com/s/Fl9KTxTSUDyZVJOu-fDqxQ>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01ca34aaf7e5009589.jpg)

Dridex是一款著名的银行木马，主要窃取受害者网上银行凭证，此银行木马主要通过钓鱼邮件定向发送钓鱼邮件给受害者，欺骗受害者打开邮件中的附件文档，感染银行木马，盗取相关信息，在2015年，Dridex造成的损失就超过4000万美元，此银行木马非常活跃，背后的运营团队也在不断更新的技术，改进Payload加载方载逃避各种安全软件的检测，使其变的越来越复杂，去年1月份，FacePoint团队的安全研究人员发现Dridex还扩大了感染链，通过FTP网站进行传播……

最近国外安全研究人员，发现此银行木马更新了，最新变种通过钓鱼邮件进行传播，邮件内容，如下所示：

![](https://p2.ssl.qhimg.com/t01ff41e88bc10c3770.png)

附件中有一个加密的doc文档，文档密码为：pass170619，打开文档，里面包含恶意的宏代码，如下所示：

![](https://p0.ssl.qhimg.com/t01912a0275564a127f.png)

执行恶意宏代码，在TEMP目录释放XLS文件，然后通过WMIC启动恶意XLS文件，如下所示：

![](https://p5.ssl.qhimg.com/t018a3b7e40ef038d2b.png)

XSL恶意程序从服务器下载Dirdex银行木马安装程序到TEMP目录，如下所示:

![](https://p3.ssl.qhimg.com/t0131508fc54dacf8db.png)

恶意服务器URL，如下所示：

![](https://p5.ssl.qhimg.com/t01e8d39a2df4340112.png)

hxxps://tor2net.com/udfgh87898df87gdfug89df/servicewn.exe

银行木马安装程序核心功能剖析

1.解密执行到ShellCode代码处，如下所示：

![](https://p2.ssl.qhimg.com/t01e485e1a5e91c4225.png)

2.获取VirtualAlloc函数地址，分配相应的内存空间，如下所示：

![](https://p5.ssl.qhimg.com/t01fc977c9d50cfd85f.png)

3.然后调用解密函数，解密出银行木马安装程序核心Payload，如下所示：

![](https://p4.ssl.qhimg.com/t018dbb9e3664f9cb2f.png)

解密出来的Payload，如下所示：

![](https://p5.ssl.qhimg.com/t01b7435d42e0f6db67.png)

4.最后跳转到Payload代码，执行Payload，安装银行木马，如下所示：

![](https://p0.ssl.qhimg.com/t01e21701d0649aaed0.png)

5.安装过程代码，如下所示：

![](https://p5.ssl.qhimg.com/t015648cd5350dc1b1b.png)

此Dirdex银行木马变种，主要利用白加黑的方式加载Payload，以逃避安全软件的检测，并将白程序设置为计划任务自启动项，如下所示：

![](https://p2.ssl.qhimg.com/t01ab6e207f5e423574.png)

设置为主机自启动项目，如下所示：

![](https://p3.ssl.qhimg.com/t0120d4dcbf5ff472ab.png)

生成的相应白加黑文件目录，如下所示：

![](https://p5.ssl.qhimg.com/t01f33a0a7f51d98792.png)

通过正常程序加载同目录下的恶意DLL文件，执行银行木马主体功能，如下所示：

![](https://p5.ssl.qhimg.com/t01e9276ca2aa08323a.png)

最近几年银行木马非常流行，一款流行的银行木马都会造成客户数亿美元的损失，前段时间银行大盗Carbanak木马源代码被泄露，这款银行木马曾盗取10亿+美元，随着勒索病毒的暴利，有些银行木马还成了其它恶意软件的渠道分销商，通过银行木马下载传播勒索病毒，此前TrickBot、Emotet两款银行木马渠道都曾传播过勒索病毒，笔者曾经详细分析过多款银行木马样本,包含：TrickBot、Emotet、Ursnif、Redaman、IcedID等，发现最近Ursnif(Gozi)银行木马也非常活跃，现已捕获到了最新一个样本，下篇再分享给大家

样本下载地址：

<https://www.malware-traffic-analysis.net/2019/06/18/index.html>

本文转自：[CyberThreatAnalyst](https://mp.weixin.qq.com/s/Fl9KTxTSUDyZVJOu-fDqxQ)

本文翻译自CyberThreatAnalyst [原文链接](https://mp.weixin.qq.com/s/Fl9KTxTSUDyZVJOu-fDqxQ)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181238](/post/id/181238)

安全客 - 有思想的安全新媒体

本文转载自: [CyberThreatAnalyst](https://mp.weixin.qq.com/s/Fl9KTxTSUDyZVJOu-fDqxQ)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/Fl9KTxTSUDyZVJOu-fDqxQ>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [钓鱼邮件](/tag/钓鱼邮件)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

