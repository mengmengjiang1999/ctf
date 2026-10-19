# 【技术分享】关于HTTP Security Headers，你需要了解的一切

阅读量 **275568**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-02-07 10:21:14

 **x**

##### 译文声明

本文是翻译文章，文章来源：appcanary.com

原文地址：<https://blog.appcanary.com/2017/http-security-headers.html>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**  
**

**0x00 前言**

28年前，一些物理学家需要一种简单的分享实验数据的方法，因此网络诞生了。这被普遍认为是一个好的进步。不幸的是，物理学家接触的一切——从三角学到强大的核能，最终都被武器化了。超文本传输协议协议也是如此。

本文解释了什么是安全头和怎么在Rails、Django、Express.js、Go、Nginx和Apache中实现这些头。

请注意一些头最好是在你的HTTP服务器中配置，另外一些应该在应用层中设置。在这里由你自己权衡。你能使用Mozilla's
[Observatory](https://observatory.mozilla.org/analyze.html?host=appcanary.com)来测试你的实现。

**  
**

**0x01 HTTP Security Headers内容**

X-XSS-Protection

Content Security Policy

HTTP Strict Transport Security(HSTS)

HTTP Public Key Pinning(HPKP)

X-Frame-Options

X-Content-Type-Options

Referer-Policy

Cookie Options

  

**0x02 X-XSS-Protection**

    
    
    X-XSS-Protection: 0;
    X-XSS-Protection: 1;
    X-XSS-Protection: 1; mode=block

**为什么？**

跨站脚本通常的简写是XSS，是一种攻击手段，攻击者使一个页面加载一些恶意的javascript。X-XSS-Protection是Chrome和IE中的一个特性，被设计用来防御反射型XSS攻击——攻击者将恶意的payload作为请求的一部分发送。

X-XSS-Protection：0 关闭。

X-XSS-Protection：1 过滤来自请求的脚本，但是还是会交给页面。

X-XSS-Protection：1；mode=block 触发时，将阻止整个页面的呈现。

**是否该使用它？**

是的。需要设置X-XSS-Protection：1；mode=block
。但是有时过滤有问题的脚本是有问题的，查看[这里](http://blog.innerht.ml/the-misunderstood-x-xss-protection/)了解为什么。

**怎么做？**

**了解更多**

[X-XSS-Protection – MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection)

  

**0x03 Content Security Policy**

    
    
    Content-Security-Policy: <policy>

**为什么？**

内容安全策略可以认为是X-XSS-Protection的高级版本。尽管X-XSS-Protection能阻止来自请求的脚本，但是它不能阻止一些XSS攻击，如在你服务器上面存储恶意脚本或者使用恶意脚本加载额外的资源。

CSP提供了一种语言，来定义浏览器能加载来自哪的资源。你能以非常详细的方式来列出原始的脚本、图片、字体和样式等的白名单列表。你还能使用哈希和特征来比较任何加载的资源。

**是否该使用它？**

是的。虽然它不能阻止所有的XSS攻击，但是它是缓解XSS攻击的一个重要的措施，并且是深度防御的重要的一个环节。它可能很难实现。如果你是一个勇敢的读者并继续阅读，校验[appcanary.com](https://appcanary.com/)返回的头，你将会看到我们并没有实现CSP。有一些rails开发插件可以使用，避免了自己实现CSP，但也能有实际的安全作用。

**怎么做？**

写一个CSP策略可能是个挑战。参考[此处](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)，是你能使用的所有指令的列表。从[这里](https://csp.withgoogle.com/docs/adopting-csp.html)开始比较好。

**了解更多**  

[Content-Security-Policy – MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)

[CSP Quick Reference Guide](https://content-security-policy.com/)

[Google’s CSP Guide](https://csp.withgoogle.com/docs/index.html)

**  
**

**0x04 HTTP Strict Transport Security(HSTS)**

    
    
    Strict-Transport-Security: max-age=<expire-time>
    Strict-Transport-Security: max-age=<expire-time>; includeSubDomains
    Strict-Transport-Security: max-age=<expire-time>; preload

**为什么？**

当我们想与一些人安全通信时，我们面对了两个问题。第一个问题是隐私：我们想确保我们发送的消息只能接收者看到。另一个问题是认证：我们如何知道接收者是他们自己说的那个人？

HTTPS使用加密解决了第一个问题，但是还有个认证问题（稍后详述，参见Public Key
Pinning）。HSTS头解决了元问题：你如何知道与你通信的人是否支持加密？

HSTS缓解了一种成为[sslstrip](https://moxie.org/software/sslstrip/)的攻击。假设你使用的是恶意攻击者控制的WIFI路由器提供的网络。攻击者可以禁用你和你访问的网站之间的加密机制。即使你访问的网站只能通过HTTPS访问，攻击者还是可以使用中间人攻击HTTP流量，来使得网站看起来工作在未加密的HTTP上。不需要SSL证书，只要禁用加密就可以。

通过让你的浏览器知道它必须总是使用加密访问网站，Strict-Transport-Security头解决了这个问题，除非你的浏览器看到了HSTS头并且没有过期，否则将无法访问未加密的网站，并且如果不经过HTTPS则会出错。

**是否应该使用它？**

是的。你的应用只能通过HTTPS访问，对吗？尝试通过老的HTTP访问将重定向到安全站点，对吗？（提示：如果你想避免商业证书颁发机构的证书可以使用[letsencrypt](https://letsencrypt.org/)。）

HSTS头的一个缺点是，它允许使用一种[聪明的技术](http://www.radicalresearch.co.uk/lab/hstssupercookies)来创建supercookies来作为用户的指纹。作为一个网站的运营者，你可能已经有些方式跟踪了你的用户，但是尝试只使用HSTS是更好的方式并且不使用supercookies。

**怎么做？**

有两个选项：

includeSubDomains——HSTS适用于子域名

preload——谷歌维护了一个服务，在浏览器中硬编码你的网站为HTTPS访问。通过这种方式，一个用户甚至不得不访问你的网站：他们的浏览器已经知道了它应该拒绝未加密的连接。顺便说一句，选择列表是很困难的，因此最好仅在你知道你的所有的子域名都永久支持HTTPS的情况下才开启它。

  

  

**了解更多**

[RFC 6797](https://tools.ietf.org/html/rfc6797)

[Strict-Transport-Security – MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)

**0x05 HTTP Public Key Pinning(HPKP)**

    
    
    Public-Key-Pins: pin-sha256=<base64==>; max-age=<expireTime>;
    Public-Key-Pins: pin-sha256=<base64==>; max-age=<expireTime>; includeSubDomains
    Public-Key-Pins: pin-sha256=<base64==>; max-age=<expireTime>; report-uri=<reportURI>

**为什么？**

上面描述的HSTS头是被设计来确保所有的网站连接都是加密的。然而，它没有指出使用的关键点。

网站的信任是基于CA模型的。你的浏览器和操作系统绑定一些受信任的证书颁发机构的公钥，这些机构通常是专门的公司或者国家地区。当一个CA向你的域名颁发证书后，意味着信任这个CA的任何人都将自动信任使用这个证书加密的SSL流量。这些CA负责验证你拥有的域（可以是发送邮件、请求你托管文件或调查你的公司）。

两个CA给两个不同的人颁发同一个域名的证书，浏览器将信任这两个CA。这就导致了一个问题，尤其是因为CAs[可能被攻击](https://technet.microsoft.com/library/security/2524375)。这允许攻击者使用MiTM攻击他们想攻击的域名，即使那个域名使用了SSL和HSTS，也是一样。

HPKP头试着缓解这个问题。这个头让你绑定一个证书。当一个浏览器第一次看见这个头，它将保存这个证书。当每个请求达到max-age，除非从服务器发送的证书链中至少有一个指纹记录，否则浏览器将失败。

和上述的HSTS很像，HPKP头也有隐私影响。这些在它的[RFC](https://tools.ietf.org/html/rfc7469#section-5)中有描述。

**是否该使用它？**

可能不需要。

HPKP是一个非常非常锋利的尖刀。考虑到这个：如果你绑定了错误的证书，或者你丢失了密钥，或者某些事出错了，你将阻止你的用户访问你的网站。你能做的只是等待绑定过期。

[该文](https://blog.qualys.com/ssllabs/2016/09/06/is-http-public-key-pinning-dead)举了个关于它的例子，并且包含了一种有趣的攻击方式，使用HPKP勒索他们的受害者。

一个可选项是使用Public-Key-Pins-Report-Only头，这将在出错时报告出来，但是不会锁住用户。这至少让你知道用户被假证书攻击了。

**怎么做？**

两个选项是：

includeSubDomains——HPKP适用于子域名

report-uri——不可靠的行为将被报告

你不得不为你绑定的密钥生成一个base64加密的指纹，并且你不得不使用一个备份的密钥。怎么做，请参考这个[帮助文档](https://developer.mozilla.org/en-US/docs/Web/HTTP/Public_Key_Pinning#Extracting_the_Base64_encoded_public_key_information)。

  

**了解更多**

[RFC 7469](https://tools.ietf.org/html/rfc7469)

[HTTP Public Key Pinning(HPKP) – MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Public_Key_Pinning)

  

**0x06 X-Frame-Options**

    
    
    X-Frame-Options: DENY
    X-Frame-Options: SAMEORIGIN
    X-Frame-Options: ALLOW-FROM https://example.com/

**为什么？**

在我们开始给漏洞命名前，我们先给黑客技术命名。“Clickjacking”是这些名字中的一个。

想法如下：你创建一个看不见的iframe，将它放在焦点中并引导用户输入。作为一个攻击者，你能欺骗人们玩一个基于浏览器的游戏，然而他们点击的是隐藏的显示twitter的iframe，迫使他们非自愿转推。

它听起来很蠢，但是它是一个有效的攻击。

**是否应该使用它？**

是的。如果你的应用是一个漂亮的雪花。你想别人破环它吗？

**怎么做？**

X-Frame-Options有3种模式：

DENY——没有人能够在iframe中放入页面

SAMEORIGIN——该页面只能由同一来源的某个iframe显示。

ALLOW-FROM——指定一个特定的可放入iframe的URL

要记住的一件事是你能按你想要的来增加iframes的深度，并且在这种情况下，SAMEORIGIN和ALLOW-FROM不被指定。也就是说如果你有一个3层的iframe，并且最里层的iframe有SAMEORIGIN，我们关心的是包裹它的iframe的来源还是最顶层的iframe？

  

**了解更多**

[RFC 7034](https://tools.ietf.org/html/rfc7034)

[X-Frame-Options – MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options)

  

**0x07 X-Content-Type-Options**

    
    
    X-Content-Type-Options: nosniff;

**为什么？**

这个头解决了被称为“MIME嗅探”的问题，它是一个浏览器的“特性”。

理论上，每次你的服务器响应一个请求，它应该是设置了一个Content-Type头以便告诉浏览器它是在获取HTML、gif或者flash等。不幸的是，网络总是会被打破，从来没有真正遵循的东西；许多人不会设置正确的Content-Type头。

结果会导致浏览器判断他们是否真的有用并且试图通过检查内容本身且忽略指定的类型来推断内容类型。如果它看起来像是gif，则展示一个gif，即使内容类型是text/html。同样，我们看似得到了一些HTML，即使服务器说他是个gif，我们依然应该展示它。

当你运行一个图片分享站点，并且用户能上传包含javascript的看起来像HTML的图片，你将遭受到存储型XSS攻击。

X-Content-Type-Options头的存在是告诉浏览器设置被告诉的类型。

**是否该使用它？**

是的，只是确保正确设置内容类型。

**怎么做？**

**了解更多**  

[X-Content-Type-Options – MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options)

##  

**0x08 Referrer-Policy**

    
    
     Referrer-Policy: "no-referrer"
        Referrer-Policy: "no-referrer-when-downgrade" 
        Referrer-Policy: "origin" 
        Referrer-Policy: "origin-when-cross-origin"
        Referrer-Policy: "same-origin" 
        Referrer-Policy: "strict-origin" 
        Referrer-Policy: "strict-origin-when-cross-origin" 
        Referrer-Policy: "unsafe-url"

**为什么？**

Referer头对于分析非常有用，但是对于隐私是件坏事。有时网站会苏醒并且认为一直发送它不是个好主意。

Referrer-Policy头在浏览器设置Referer头时可以指定。

**是否应该使用它？**

由你自己决定，但是它可能是个好东西。如果你不关心你用户的隐私，可以考虑它作为分析的一种好的方法。

设置Referrer-Policy：“no-referrer”

**怎么做？**

**了解更多**

[Referrer Policy – MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy)

  

**0x09 Cookie Options**

    
    
    Set-Cookie: <key>=<value>; Expires=<expiryDate>; Secure; HttpOnly; SameSite=strict

**为什么？**

这不是个安全的头，但是有3个不同的选项你应该注意：

Cookies标记为Secure将只能通过HTTPS提供服务。这阻止了一些人在MiTM攻击中读取cookies，它可以强制浏览器访问一个指定的网页。

HttpOnly是一个误称，并且和HTTPS无关。Cookies标记为HttpOnly将阻止在javascript中访问。因此如果有XSS缺陷，攻击者不能立即偷到cookies。

SameSite帮助防御CSRF攻击。这种攻击是用户可能在访问不同的网站，无意中欺骗他们对你的网站发出请求，例如，用于GET请求的图片，或者使用javascript提交POST请求，通常使用CSRF令牌来防御这种攻击。Cookie被标记为SamSite将不会发送到不同的站点。

它有两种模式，lax和strict。Lax模式允许cookie作为GET请求的顶层内容被发送（例如你点击一个链接）。Strict不发送任何第三方的cookies。

**是否应该使用它？**

绝对应该设置Secure和HttpOnly。不幸的是，SameSite cookies只在Chrome和Opera中提供，因此现在可以忽略他们。

**怎么做？**

**了解更多**

[Cookies – MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#Secure_and_HttpOnly_cookies)

本文翻译自appcanary.com [原文链接](https://blog.appcanary.com/2017/http-security-headers.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **root** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85422](/post/id/85422)

安全客 - 有思想的安全新媒体

本文转载自: [appcanary.com](https://blog.appcanary.com/2017/http-security-headers.html)

如若转载,请注明出处： <https://blog.appcanary.com/2017/http-security-headers.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) root

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

