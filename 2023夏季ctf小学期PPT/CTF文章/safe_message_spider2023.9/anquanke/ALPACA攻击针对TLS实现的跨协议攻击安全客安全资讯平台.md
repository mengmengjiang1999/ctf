# ALPACA攻击：针对TLS实现的跨协议攻击

阅读量 **204821**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-29 15:30:18

 **x**

##### 译文声明

本文是翻译文章，文章原作者 alpaca-attack，文章来源：alpaca-attack.com

原文地址：<https://alpaca-attack.com/﻿>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t010f71eebadb010625.png)

ALPACA攻击可以针对TLS保护的安全网站进行跨协议攻击。

## TLS

TLS被广泛用于增强HTTP、IMAP、SMTP、POP3、FTP等应用层协议的机密性、完整性和真实性。但TLS并没有将TCP连接与应用层协议绑定。因此，中间人攻击者可以重定向TLS流量到不同的TLS服务终端到另一个IP地址或端口。比如，如果子域名之间共享通配符证书(Wildcard
Certificates)，攻击者就可以将流量从一个子域名重定向到另一个子域名，生成有效的TLS会话。

## ALPACA攻击概述

ALPACA是一种利用实现不同协议的TLS服务器的应用层协议内容混淆攻击。攻击者可以将一个子域名的流量重定向到另一个子域名，生成有效的TLS会话。这会打破TLS认证，并可能进一步发起跨协议攻击。

![](https://p5.ssl.qhimg.com/t01768ea54ccd8aeed4.jpg)

攻击者对web服务器发起跨协议攻击，利用有漏洞的FTP和邮件服务器可以分为三种方式。

  * 在上传攻击（Upload Attack）中，攻击者可以窃取认证cookie和其他隐私数据。
  * 在下载攻击（Download Attack）中，攻击者可以执行存储型XSS攻击。
  * 在反射攻击中，攻击者可以在受害者网站环境下执行反射XSS攻击。

研究人员对针对TLS的跨协议攻击进行了分析，并对web服务器进行案例研究，发现攻击者可以重定向受害者web服务器的HTTPS请求到SMTP、IMAP、POP3、FTP服务器。在真实攻击场景下，攻击者可以成功提取会话cookie和其他依你说数据，并可以在有漏洞的web服务器上执行任意JS代码，成功绕过TLS。

**ALPACA攻击是通用攻击方式？**

研究人员分析发现ALPACA攻击是通用的，TLS连接的真实早在应用层数据交换前就被黑了。

**受影响的协议或设备？**

ALPACA攻击事实上是TLS的服务器认证漏洞，所以是有TLS服务器都可能会受到该攻击的影响。

![](https://p4.ssl.qhimg.com/t01c055255bd0fabd00.jpg)

但在实际场景中，漏洞的利用场景还是相对有限的。因此，可以分为有漏洞的服务器和可利用的服务两类：

  * 在web服务器和FTP服务器共享证书的情况下，如果攻击者有权限在FTP服务器上写入，这种情况就比较危险。
  * 如果web服务器与SMTP\POP3\IMAP服务器共享证书，那么根据服务器的具体行为，会带来不同情况的危险。

![](https://p5.ssl.qhimg.com/t01a074381e6e619753.jpg)

![](https://p5.ssl.qhimg.com/t01a6c5907cc3627503.jpg)

**攻击的实际可能性**

大多数攻击都需要MIMT攻击者，也就是说攻击者要拦截和修改受害者浏览器发送给web服务器的数据。这种情况在互联网环境下是比较困难的，但是在本地网络上被利用的可能性更大一些。此外，有一些攻击的变种并不需要中间人，因此更加危险。

研究人员将在即将召开的Black Hat USA 2021和USENIX
Security2021大会上作关于ALPACA攻击的演讲和展示，更多研究论文参见：<https://alpaca-attack.com/ALPACA.pdf>

相关代码参见GitHub：<https://github.com/RUB-NDS/alpaca-code/>

本文翻译自alpaca-attack.com [原文链接](https://alpaca-attack.com/﻿)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ang010ela** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/244744](/post/id/244744)

安全客 - 有思想的安全新媒体

本文转载自: [alpaca-attack.com](https://alpaca-attack.com/﻿)

如若转载,请注明出处： <https://alpaca-attack.com/﻿>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [TLS](/tag/TLS)
  * [ALPACA](/tag/ALPACA)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) ang010ela

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

