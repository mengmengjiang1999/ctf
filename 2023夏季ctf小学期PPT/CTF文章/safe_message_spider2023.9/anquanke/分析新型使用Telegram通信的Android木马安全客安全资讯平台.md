# 分析新型使用Telegram通信的Android木马

阅读量 **193492**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-21 14:08:10

 **x**

##### 译文声明

本文是翻译文章

原文地址：<https://www.welivesecurity.com/2018/06/18/new-telegram-abusing-android-rat/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01ad1c93fc7463c1ac.jpg)

## 写在前面的话

最近ESET研究人员发现了一个新的AndroidRAT家族，在之前调查的IRRAT病毒和TeleRAT病毒的活跃程度时，我们发现了这个全新的恶意软件家族，这个家族至少从2017年8月开始就在传播。在2018年3月，它的源代码可以通过Telegram渠道免费获取，因此，数百个恶意软件变种已经在野外传播。其中一种变体与其他变体不同，它是在专门的Telegram频道上出售的，以HeroRat的名字营销。根据功能，它有三种定价模式，并附带一个支持视频频道。目前还不清楚这个变体是否由泄露的源代码创建的。

## 它如何运作？

攻击者通过第三方应用程序商店，社交媒体和消息应用程序，通过各种马甲，引诱受害者下载RAT。我们发现恶意软件主要分布在伊朗，目前该恶意软件尚未在Google
Play上看到。

![](https://p5.ssl.qhimg.com/t01397673e572041a59.png)

恶意软件可在所有Android版本上运行：但是用户需要同意应用程序所需的权限（有时包括以管理员身份激活应用程序），这是社会工程学发挥作用的地方。

![](https://p2.ssl.qhimg.com/t01b47240d415ef0496.png)

在受害者的设备上安装并启动恶意软件后，会出现一个小的弹出窗口，声称该应用程序无法在设备上运行，因此将被卸载。在我们分析的变体中，虚假的卸载消息取决于目标设备的语言设置来显示。  
卸载看似完成后，应用程序的图标消失。然而，在攻击者方面，一个新的受害设备刚刚被注册。

![](https://p4.ssl.qhimg.com/t018deb1014d5ccfc4b.png)

![](https://p5.ssl.qhimg.com/t01c4df1b3afd1ef463.png)

获得对受害者设备的访问权限后，攻击者利用Telegram的bot功能来控制新感染的设备。每个受感染的设备都是通过bot控制的，并由攻击者使用Telegram应用程序设置和操作。该恶意软件具有很多功能，包括短信拦截和读取联系人信息，发送短信和拨打电话，录制音频和屏幕，获取设备位置以及控制设备的设置。

HeroRat的功能分为三个“bundles”版本——`bronze`, `silver` 和 `gold
panels`，分别销售25,50,100美元。恶意软件的功能可以通过Telegram
bot界面中的按钮的形式访问。攻击者只需点击正在运行的恶意软件版本中的按钮即可控制受害设备。

![](https://p0.ssl.qhimg.com/t01563202e5a64cf438.png)

![](https://p4.ssl.qhimg.com/t01651996c120116b85.png)

与以前分析的Android RAT不同，这是用标准的Android
Java编写的，这个新发现的恶意软件家族是使用Xamarin框架开发的——这是一种罕见的Android恶意软件组合。恶意软件通过Telegram协议进行通信的方式，而不是以前描述的rat利用的Telegram
Bot API，这个恶意软件家族还使用Telesharp，一个用c#创建Telegram Bot的库。  
通过Telegram协议，通信命令和泄漏数据都完全覆盖了通信协议，这是一种旨在避免基于流量的检测，从而实现已知上传服务器的措施。

## 如何保持安全

因为恶意软件的源代码开源了，新的变种随时可以出现。为避免成为Android恶意软件的受害者，请在下载应用程序时坚持使用官方Google
Play商店，确保在将任何内容下载到设备之前阅读用户评论，并注意安装前后授予应用程序的权限。

## IoCs

Package Name | Hash | Detection  
---|---|---  
System.OS | 896FFA6CB6D7789662ACEDC3F9C024A0 | Android/Agent.AQO  
Andro.OS | E16349E8BB8F76DCFF973CB71E9EA59E | Android/Spy.Agent.AMS  
FreeInterNet.OS | 0E6FDBDF1FB1E758D2352407D4DBF91E | Android/Agent.AQO  
  
审核人：yiwang 编辑：边边

本文翻译自 [原文链接](https://www.welivesecurity.com/2018/06/18/new-telegram-abusing-android-rat/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **无名小卒** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148556](/post/id/148556)

安全客 - 有思想的安全新媒体

本文转载自: [](https://www.welivesecurity.com/2018/06/18/new-telegram-abusing-android-rat/)

如若转载,请注明出处： <https://www.welivesecurity.com/2018/06/18/new-telegram-abusing-android-rat/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Android木马](/tag/Android木马)
  * [技术分析](/tag/技术分析)
  * [Telegram](/tag/Telegram)
  * [安全研究](/tag/安全研究)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t013aa021a06d47a307.png) 无名小卒

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

