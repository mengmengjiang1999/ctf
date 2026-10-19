***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **** **![facebook-bots-messenger1-1920.jpg](https://image.3001.net/images/20190222/1550849626_5c70165acaae7.jpg!small)**
**今天分享的这篇writeup，作者在Facebook视频聊天设备Portal的官网中，通过测试其中的客户支持聊天机器人（Support
Bot），利用其附件上传功能，发现了一个存在于Facebook
聊天架构中，影响Messenger、Portal和Workplace等Facebook全平台聊天应用，会导致用户在聊天应用中发送的附件泄露，非常严重。**

 **以下是作者的漏洞发现思路：**

## 发现漏洞

2019年1月22日凌晨4点，我苦闷地抽着烟测试漏洞，突然，Facebook视频聊天设备Portal官网 - portal.facebook.com
中新加入的聊天机器人功能映入我的眼帘。

> Facebook
> Portal：Portal是Facebook推出的智能视频聊天和社交功能联系工具，为Facebook的第一款消费类硬件产品，用户开始使用 Portal
> 聊天时，如果有多个人，Portal 则能够识别到所有人。Facebook 表示，Portal
> 希望可以创造一种聊天双方在同一个房间面对面的感觉。具体说明可以参考Portal官网 <https://portal.facebook.com/>

早前，我曾测试过
portal.facebook.com，并没在其中发现任何安全隐患，但是现在当我重新打开这个网站，在账户设置区域，我看到了一个此前没有发现的功能 -客户支持聊天机器人（Support Bot），如下：

![1_49o9YjgRRwwcApCLTaIX4w.jpeg](https://image.3001.net/images/20190222/1550849425_5c701591982a6.jpeg!small)接着，我注意到，在这个Support
Bot聊天频道中，可以向其中上传附件，图片、视频和文档等类型文件都能上传有效。所以，我就上传了一张正常图片，同时用Burpsuite对上传操作进行抓包，想看看POST请求中的具体参数，之后，我看到了以下请求包内容：

> POST /messaging/send/ HTTP/1.1
>
> Host: [www.facebook.com](http://www.facebook.com)
>
> client=mercury&action_type=ma-type:user-generated-> message&body=&ephemeral_ttl_mode=0&has_attachment=trueℑ_ids[0]=123&message_id=111&offline_threading_id=123

在这个请求包中，包含了一个名为 image_ids[0] 的有意思的参数，它应该表示我上传到Portal聊天机器人（Support
Bot）中的那张图片。我就想如果我把这个图片ID换成其他用户的图片ID，是否就能间接访问获取到其他用户的图片了呢！？同理，那其他用户的其它附件（如文档、视频和声频）也应该一样可用此方法间接访问获取到！最终，我经过设置的attacker
和 victim账户进行相互测试，发现了以下几个方面的安全问题：

> 可用此方法获取到其他用户通过Portal聊天机器人发送的任何附件，这些附件包含图片、文档、视频和音频；
>
> 该漏洞影响了所有Facebook的聊天架构应用，涉及Facebook主聊天系统、Messenger、Portal聊天应用和Workplace聊天应用；
>
> 我可以在所有Facebook的聊天架构应用中来复现这个漏洞问题；
>
> 在Burpsuite的Proxy代理标签中可以通过请求成功复现，但如果发送到Repeater模块中进行重放攻击则会返回一个未知错误。

## 漏洞利用场景

恶意攻击者利用该漏洞，可以编写脚本工具去暴力枚举其他用户的上传附件ID，如Images IDs, video IDs, files IDs and
audio messages
IDs。Facebook聊天应用的日均用户可是数百万啊，如果哪个VIP人士类似的图片和音视频附件被攻击者用该漏洞获取，那后果不堪设想，对用户个人隐私来说，也是一个极大的威胁。

PoC视频如下：

之后，我及时把该漏洞上报给了 Facebook 安全团队，他们非常重视，最后奖励了我15,000美金！这也是我上报Facebook漏洞以来收获的最高奖金。

## 漏洞上报进程

> 2019.1.22 漏洞初报
>
> 2019.2.4 漏洞分类
>
> 2019.2.13 漏洞修复
>
> 2019.2.13 修复确认
>
> 2019.2.13 $15,000赏金发放

## 经验

> 尝试时不时地去测试那些你曾经测试过的目标，可从一些新改进、更新的功能中发现问题；
>
> 不要相信响应内容，出错也并不意味着没有可能。

 ***参考来源：[medium](https://medium.com/bugbountywriteup/disclose-private-attachments-in-facebook-messenger-infrastructure-15-000-ae13602aa486)，clouds编译，转载请注明来自FreeBuf.COM **

