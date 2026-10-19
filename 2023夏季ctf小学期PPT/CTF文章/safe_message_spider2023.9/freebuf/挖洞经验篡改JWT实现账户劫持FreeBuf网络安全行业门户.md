![](https://image.3001.net/images/20200430/1588237489_5eaa94b178f93.png!small)

**今天分享的这篇Writeup是关于JSON Web Tokens
(JWT)的，其利用点是可以绕过用户邮件验证码确认，实现密码重置从而达到账户劫持目的。**

## JSON Web Token，JWT

JSON Web Token (JWT) 是基于RFC
7519标准定义的，以JSON形式在网络应用间安全传递信息的一种紧凑而独立的方法，尤其适用于分布式站点的单点登录（SSO）场景。JWT携带的属性信息通过HMAC算法的电子签名方式被用来在客户端和服务端之间进行身份验证，其默认的签名算法为HMAC
SHA256。

JWT的结构

> JWT主要由三个部分组成，各部分之间为.分开，它们分别是：
>
> Header（头部）
>
> Payload（负载）
>
> Signature（签名）

样式为：

xxxxx.yyyyy.zzzzz

### 无需token进行邮件地址验证

我发现的漏洞是这样的。通过利用目标系统的邀请功能并修改其中携带的JWT
token信息，无需点击确认链接，即可实现对用户邮件地址和身份的验证。假设我有一个邮箱地址是attacker@attacker.com，然后我在目标网站的邀请功能中发起对该邮箱地址的一个邀请操作，接下来，我登录该邮箱attacker@attacker.com后，会在收件箱中收到一个URL形式携带JWT的确认链接。该过程在Burp中的响应如下：

![](https://image.3001.net/images/20200430/1588237244_5eaa93bc45c99.png!small)

我在收件箱中收到的URL形式携带JWT的确认链接如下：

![](https://image.3001.net/images/20200430/1588237263_5eaa93cf2eb05.png!small)

链接后即是一串JWT token，通过网站<https://jwt.io/>，解码该JWT token后的结果如下：

![](https://image.3001.net/images/20200430/1588237277_5eaa93dd87ac8.png!small)

到此，我第一时间想到的就是尝试用上述邀请功能邀请目标网站管理员的对应邮箱admin@company.com，操作之后，Burp中的响应消息如下：

![](https://image.3001.net/images/20200430/1588237291_5eaa93eba7f7e.png!small)

然后，在收件箱中同样也收到了一个携带JWT的URL链接，通过JWT编码解码操作，我尝试把其中我自己邀请人的attacker@attacker.com更改为admin@company.com，把其中的id也更改为admin的ID，并把其时间戳（timestamp）即“created
date”:”xxxxxxxx”也做了相应修改，然后再次通过编码生成新的JWT。利用该JWT我就可以来确认用户身份，并重置与邮箱admin@company.com对应的公司管理员用户密码。

![](https://image.3001.net/images/20200430/1588237318_5eaa9406bcc43.png!small)

因此，后续可以利用该JWT的延伸凭据信息，去登录目标网站公司如业务支持等不同业务端的SSO接口。

## 重置其他用户密码

该方法由于需要知道对方受害者用户的ID号信息，因此并不适用于任意用户，利用方式还是存在一定难度，但至少我可以通过注册两个用户的方式来验证漏洞。就比如用其它邮箱注册了一个测试用户（假设为Victim），从账户信息中可以看到其用户id为：jyAzV7KhT，然后我用之前我的attacker@attacker.com发起密码重置请求，然后从我的邮箱attacker@attacker.com中收到一个携带JWT的重置链接，如下：

![](https://image.3001.net/images/20200430/1588237351_5eaa9427c87f9.png!small)

把该JWT放到<https://jwt.io/>的JWT解码工具中解密，在右边Decode区域得出具体的JWT三部份内容，接着，把其中的id更改为Victim账户的id：jyAzV7KhT。这样就生成了Victim账户的密码重置JWT了，把它放入上述URL确认链接之后，就能更改Victim账户密码了！

![](https://image.3001.net/images/20200430/1588237373_5eaa943dc62c1.png!small)

## 漏洞原因

目标网站在客户端进行JWT的生成，这样一来，就可导致JWT可被客户端篡改的风险，安全的方式是把JWT放到服务端生成。

## 技术参考

> <https://jwt.io/introduction/>
>
> <https://hackerone.com/reports/638635>

***参考来源：[securitybreached](https://blog.securitybreached.org/2020/04/04/playing-with-json-web-tokens-for-fun-and-profit/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

