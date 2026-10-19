![](https://image.3001.net/images/20200114/1578984151_5e1d62d7a6a4e.jpg!small)

**近期，安全研究者Alex
Birsanl对PayPal登录界面的身份验证机制进行分析，发现了其中一个隐藏的高危漏洞，可以通过请求其验证码质询服务端（reCAPTCHA
challenge），在质询响应消息中获取PayPal受害者的注册邮箱和明文密码，危害严重，漏洞最终获得了PayPal官方$15,300的奖励。**

## 漏洞前言

当我们在做漏洞测试时，相对于那些显而易见的功能应用来说，我们还会去关注那些未知资产或模糊端点的服务，有时候这种犄角旮旯服务产生的漏洞同样至关重要，影响关键。

在面对测试目标时，如果你是第一个关注它并对它开展测试评估的人，那么细致全面的检查无疑会发现一些安全问题，尤其是一些代码已经成型且处于持续运转的应用，若能在这种应用功能中发现安全漏洞，将会是非常重要非常危急，且收获颇丰的。本文中，作者就在PayPal用户经常用到的功能点
- 登录框架中发现了一个高危漏洞，我们一起来看看。

## 最初研究

我在研究PayPal的验证机制时，发现其auth验证页面的一个javascript脚本文件（recaptchav3.js）中，包含了一个CSRF
token和一个会话ID（Session ID），如下：

![](https://image.3001.net/images/20200114/1578983552_5e1d6080cf7e1.png!small)

这马上引起了我的注意，因为在有效javascript文件中存在的任何类型的会话数据，都有可能被攻击者以各种方式检索获取到。如用跨站脚本包含（cross-site script
inclusion，XSSI)，攻击者可以用一个嵌入了HTML<script>的Web页面包含进恶意跨域脚本，然后通过该恶意跨域脚本绕过边界窃取用户存储在网站中的敏感信息。

由此，我进行了一个简单测试，测试发现我猜测的跨站脚本包含漏洞（XSSI）是确定存在的。尽管每个Request请求中都会有一个javascript混淆方法去随机化变量名，但其中敏感的用户token还是一样会响应出现在了之前我们预计的位置，如果额外加点料，完全能实现对其中敏感信息的检索提取。

![](https://image.3001.net/images/20200114/1578983631_5e1d60cfc3613.png!small)

然而，一个安全问题的好坏在于你能用它来实现怎样的安全威胁。因此，有了以上 _csrf 和
_sessionID的发现，我立即着手对它们进行分析，想搞清楚它们的具体用途和可利用之处。

## 深入分析

经过无数次对上述PayPal身份验证请求中的CSRF token值（_csrf ）的替换，之后，我认为用这个CSRF
token不可能实现经典的跨站请求伪造攻击（CSRF），同样，替换_sessionID值也不能实现对受害者的冒充。

接下来，我回到了之前的recaptchav3.js中继续分析 _csrf 和
_sessionID的具体用途，之后，我顺藤摸瓜来到了PayPal主要安全机制之一的安全质询发起功能点的防暴力枚举处，虽然该功能用于大多数PayPal服务中，但我还是把关注点聚集到了PayPal的主登录框架中。

![](https://image.3001.net/images/20200114/1578983676_5e1d60fc27c25.png!small)

因为：如果经过数次的登录失败尝试，之后，在继续登录之前，PayPal会向用户发起一个验证码质询（reCAPTCHA
challenge），以验证当前尝试登录的主体是否是人还是暴力枚举的Robot。然而，就是这样一个功能实现，却让我发现了其中隐藏的信息，让我有点吃惊。

如果PayPal一旦检测到可能的暴力登录尝试，那么，在下次登录尝试之前，PayPal登录界面会弹出一个Google验证码（Google
Captcha）输入提示，如果最终该验证码由用户输入完成，那么就会向PayPal服务端/auth/validatecaptcha发起一下如下的HTTP
POST请求：

![](https://image.3001.net/images/20200114/1578983691_5e1d610b46cbd.png!small)

可见，其请求体中包含了我们熟悉的_csrf 和 _sessionID， 除此之外，还有jse和captcha两个数值比较大的参数。

发起上述验证码质询（reCAPTCHA
challenge）请求后，其后续的响应旨在将用户重新引入身份验证流程，为此，响应消息中包含了一个自动提交表单，其中存有用户最新登录请求中输入的所有数据，包括相关的电子邮件和纯文本密码（Plain
Text Password）！！经解析后的HTML如下：

![](https://image.3001.net/images/20200114/1578983710_5e1d611ec6076.png!small)

OMG，有了这些，攻击者可以通过社工或钓鱼方式，在正确时机范围内对受害者形成一些交互，就能获取上述的_csrf 和
_sessionID等token信息，有了这些token信息，再向/auth/validatecaptcha发起验证码安全质询，如果受害者登录成功，最终质询响应回来的信息中就会包含受害者的注册邮箱和明文密码信息。在真实攻击场景中，攻击者只需制作一个恶意页面（类似钓鱼页面），迷惑受害者点击访问，以模拟PayPal身份验证的反复尝试，去调用PayPal的验证码质询（Google
Captcha），然后在其质询响应消息中即可实现对受害者PayPal登录密码的获取。

最后，我又回到对/auth/validatecaptcha的HTTP POST请求中，想看看jse和captcha两个参数的实际作用，分析发现：

jse根本没起到验证作用；

recaptcha是Google提供过来的验证码质询（reCAPTCHA
challenge）token，它与特定的用户会话无关，无论人机验证，只要与其匹配的任何有效输入token，它都会接受。

## 漏洞利用

综上所述，除去Google的验证码质询解决方案以外，为了对以上漏洞进行成功利用，我把所有东西组合起来，制作了一个PoC验证。整个PoC验证包含两个步骤：

1、用跨站包含漏洞（XSSI）获取受害者会话中的_csrf 和
_sessionID等token信息，之后，利用这些token信息在受害者浏览器端发起针对PayPal身份验证服务端/auth/validatecaptcha的POST请求，形成暴力猜解登录尝试的模拟，以触发PayPal的验证码安全质询机制；

2、一旦受害者成功登录到PayPal之后，之前对/auth/validatecaptcha的请求响应消息中，将会包含受害者的注册邮箱和登录PayPal的明文密码。在我设计的PoC中，这些敏感信息会显示在页面中。整个PoC的最后步骤是去请求Google获取一个最新的reCAPTCHA
token。

![](https://image.3001.net/images/20200114/1578983963_5e1d621b93f18.png!small)

利用此方法，我又发现，在PayPal的一些未经用户授权的支付页面中，同样存在该漏洞，可以用上述方法获取到用户的明文***数据信息。

## 漏洞上报及处理进程

> 2019.11.18 我将PoC验证资料连同其它敏感信息一并提交给了PayPal在HackerOne上的众测项目；
>
> 2019.12 PayPal确认了漏洞的有效性；
>
> 2019.12.10 PayPal官方奖励了我$15,300，同时漏洞被PayPal评定为CVSS 8.0 (高危) ；
>
> 2019.12.11 PayPal及时修复了漏洞

## 漏洞修复及建议

现在，PayPal的验证码质询功能点/auth/validatecaptch加入了CSRF
token，已经不能实现之前的跨站脚本包含攻击。虽然漏洞是可以修复的，但如果遵循信息安全最古老的建议：永远不要以纯文本方式存储密码，那么这一切原本都是可以避免的。

 ***参考来源：[medium](https://medium.com/@alex.birsan/the-bug-that-exposed-your-paypal-password-539fc2896da9)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

