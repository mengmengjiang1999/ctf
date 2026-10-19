## 引言

**微信扫描二维码登录网站，相信很多网站登录中都有这个功能。但是这个功能使用不当，将会出现劫持漏洞。话不多说，直接分享三个实战挖掘的案例，三个的实现方式都不一样（已脱敏）.**

## A网站登录处存在二维码劫持漏洞

正常走其流程，发现登录扫一个二维码即可：

![](https://image.3001.net/images/20200417/1587057294_5e98928ef0a3b.png!small)

微信扫描后发现，只要关注了 A网站 的公众号，无需点击确认，扫描后即可登录：

![](https://image.3001.net/images/20200417/1587057313_5e9892a19c2ae.png!small)

![](https://image.3001.net/images/20200417/1587057325_5e9892ad56b9d.png!small)

‘打开浏览器f12，发现生成二维码的链接如下：

![](https://image.3001.net/images/20200417/1587057338_5e9892ba50e89.png!small)

但是直接访问，发现报错：

![](https://image.3001.net/images/20200417/1587057349_5e9892c569455.png!small)

估计是判断了Refere头，我们用python 的requests去请求试试：

![](https://image.3001.net/images/20200417/1587057362_5e9892d27e18f.png!small)

发现轮询判断二维码是否扫描，是否登录的接口如下：

![](https://image.3001.net/images/20200417/1587057382_5e9892e6e64cf.png!small)

其中：

> 未登录 code为 1
>
> 登录 code 为 0
>
> 二维码过期 code 为 2

当登录成功，code返回0，将会set-cookie，返回一个绑定登录账号的cookie：

![](https://image.3001.net/images/20200417/1587057440_5e9893201297e.png!small)

可成功获取到msg。

制定攻击流程：

> （1）请求<https://a.com/account/login_weixin.html>获取到 msg参数
>
> （2）轮询请求 [_https://_ a.com _/account/checkLogin.html?1586329068966
> &ticket=_msg参数](https://www.php.cn/account/checkLogin.html?1586329068966&ticket=gQEp8DwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAySVFteDRTWW1mXzIxQVZVZDF1MUoAAgThdY1eAwRYAgAA)其中
> ticket参数为 第一步获取到的msg参数
>
> （3）将二维码投放出去，钓鱼等待受害者扫描
>
> （4）受害者扫描二维码，轮询返回登录成功
>
> （5）获取此时的cookie。用这个cookie去登录受害者账号

Exp：

qrcode.py

![](https://image.3001.net/images/20200417/1587057519_5e98936fa671e.png!small)

此python文件用来获取二维码以及轮询

Index.php：

![](https://image.3001.net/images/20200417/1587057543_5e98938719ca0.png!small)

此页面用于投放二维码，供受害者扫描。

攻击流程：

（1）开启qrcode.py：

![](https://image.3001.net/images/20200417/1587057608_5e9893c87d3f2.png!small)

（2）投放恶意页面：

![](https://image.3001.net/images/20200417/1587057622_5e9893d61fd1a.png!small)

（3）受害者扫描二维码

（4）获取到session：

![](https://image.3001.net/images/20200417/1587057636_5e9893e4c0bbb.png!small)

（5）登录受害者账号：

![](https://image.3001.net/images/20200417/1587057651_5e9893f39104c.png!small)

自行脑补下登录成功的样子吧。。为了脱敏。。。这篇文章仅仅讨论技术。

## B网站登录处存在二维码劫持漏洞

登录处：

![](https://image.3001.net/images/20200417/1587057700_5e9894241aa7a.png!small)

二维码登录流程：

> （1）获取二维码和 key
>
> （2）轮询（很长一段时间不会过期）
>
> （3）用户扫描二维码或点击登陆链接确认登录，轮询将返回openid
>
> （4）登录

其中，获取链接和key的阶段。是没有做请求来源校验和csrf token的。意味着任何人任何地点都可以请求获取二维码和key：

![](https://image.3001.net/images/20200417/1587057722_5e98943adc37f.png!small)

请求链接：

> [ _http://b.com_ _/_ _xxxx_ _/getWxQrcode?_
> _xxx=xxxx（GET参数不重要）_](http://b.com/xxxx/getWxQrcode?xxx=xxxx%EF%BC%88GET%E5%8F%82%E6%95%B0%E4%B8%8D%E9%87%8D%E8%A6%81%EF%BC%89)

接着轮询：

![](https://image.3001.net/images/20200417/1587057741_5e98944ddef9a.png!small)

请求链接：

> [ _https://_ _b.com_ _/_ _xxxx_ _/checkWxQRState?_ _QRkey_
> _=QRkey_](https://b.com/xxxx/checkWxQRState?QRkey=QRkey)

这里的请求参数中的QRkey就是在上一步获取二维码和key时，获取的响应参数 QRkey。

此时需要用微信扫描二维码。本人分析了一下，发现二维码链接如下：

> [
> _http://b.com/login/scan/gQH18DwAAAAAAAAAAS5odHRwOi8vd2VpexxxxxxxxxxxxFNTF1MUEAAgTY5YVeAwRYAgAA_](http://user.lenovo.com.cn/login/scan/xxx/gQH18DwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAyZC13c2g4SU1hamUxSU1FNTF1MUEAAgTY5YVeAwRYAgAA)

其中 /scan/后的字符串就是我们的QRkey。只不过这个链接必须在微信中打开。

微信打开后，轮询返回了一个openid，这个openid应该是绑定这微信的，同一个微信号返回的openid都是一样的:

（偶然发现，如果微信没有自己去改微信号，就是openid的值哦）

![](https://image.3001.net/images/20200417/1587057761_5e989461635bc.png!small)

获取到openid后，openid和QRkey构造一下链接。如果微信绑定了账号的，即可登录。

登录链接：

> [ _https://_ _b_ _.com/_ _xxxx_ _/qrWxLogin?_ _openid_ _=oo6-IuOhw_
> _xxxxxxxx_ __hOI &_ _QRkey_ _=gQH18DwAAAAAAAAAAS5odHRwOi8vd2Vp_
> _xxxxxxxxxxxxxxxxx_ _4SU1_ _xxxxxxx_
> _SU1EAAgTY5YVeAwRYAgAA_](https://b.com/xxxx/qrWxLogin?openid=oo6-IuOhwxxxxxxxx_hOI&QRkey=gQH18DwAAAAAAAAAAS5odHRwOi8vd2Vpxxxxxxxxxxxxxxxxx4SU1xxxxxxxSU1EAAgTY5YVeAwRYAgAA)

根据此流程，可构造钓鱼页面。

攻击流程：

> （1）开启php相关环境，使受害者能够访问test.php；运行python脚本（attack.py），开始轮询。
>
> （2）受害者访问恶意页面（test.php），用微信扫描二维码，然后点击b网站那里的登录确认 或者将链接直接微信发给受害者，受害者微信处点开
>
> （3）此时attack.py中获取到openid，组合成登录链接。攻击者可使用登录链接登录受害者账号

使用php和python来写：

钓鱼页面：

![](https://image.3001.net/images/20200417/1587057784_5e989478e7d87.png!small)

![](https://image.3001.net/images/20200417/1587057792_5e9894800cded.png!small)

python轮询：

![](https://image.3001.net/images/20200417/1587057806_5e98948e82387.png!small)

当有用户扫描二维码或点击链接。点击确认后，获得openid，组成登录链接：

![](https://image.3001.net/images/20200417/1587057820_5e98949ce8d2b.png!small)

我们直接访问这个链接，即可成功登录。

## C网站登录处存在二维码劫持漏洞

正常请求：（前提：微信绑定了C网站账号，且在微信处登录了C网站账号）

1、网页端访问登录页面：

![](https://image.3001.net/images/20200417/1587057859_5e9894c366099.png!small)

2、网页端持续轮询，检查二维码状态。这里返回1，表示二维码还没有被扫描

![](https://image.3001.net/images/20200417/1587057873_5e9894d1a84f9.png!small)

![](https://image.3001.net/images/20200417/1587057879_5e9894d74d266.png!small)

3、手机微信端扫描二维码，发送了一个请求：

![](https://image.3001.net/images/20200417/1587057896_5e9894e85bee8.png!small)

响应：

![](https://image.3001.net/images/20200417/1587057910_5e9894f6c13d7.png!small)

4、网页端轮询，返回值 2，表示二维码已被客户端扫描，但未确认：

![](https://image.3001.net/images/20200417/1587057930_5e98950a08e04.png!small)

![](https://image.3001.net/images/20200417/1587057937_5e98951101e21.png!small)

网页端显示：

![](https://image.3001.net/images/20200417/1587057949_5e98951ded68c.png!small)

5、手机微信端点击 “确认登录电脑端”

![](https://image.3001.net/images/20200417/1587057969_5e989531c34ac.png!small)

![](https://image.3001.net/images/20200417/1587057977_5e9895398dd0e.png!small)

6、轮询接口，返回了登录成功的cookie值：

![](https://image.3001.net/images/20200417/1587057996_5e98954ce3b9a.png!small)

![](https://image.3001.net/images/20200417/1587058003_5e9895537db08.png!small)

即可成功登录网页端

攻击链：

1、访问：[
_https://c.om/xxxx/qrcodelogin/show_](https://reg.lenovo.com.cn/auth/qrcodelogin/show),获取
set-cookie：qrtoken

2、用获取到的qrtoken，轮询 状态接口

> [ _https://c.om/xxxx/xxxxxx/qrcodeLoginCheck/_ qrtoken值
> _?callback=jQuery1587040960902_](https://reg.lenovo.com.cn/auth/qrcodelogin/qrcodeLoginCheck/l1984-8c6fdf31-526f-4e7f-9a5f-20975b5b12b6?callback=jQuery1587040960902)

其中：

> 返回值为1，用户还没有扫描二维码
>
> 返回值为2，用户还没有点击确定
>
> 返回值带有参数 xxxxx-passport，登录成功，xxxxx-passport为登录凭证

3、已经在微信客户端登录过的受害者在微信客户端打开恶意网页链接，或者微信客户端扫描恶意网页的二维码。

4、恶意网页先后通过两个img标签，依次请求登录确认网页、登录成功接口

5、轮询状态接口，获取 xxxxx-passport，劫持用户账号

Demo：

构建轮询脚本：qrcode.py：（测试发现一个二维码90秒过期，该脚本可自动重新请求）

![](https://image.3001.net/images/20200417/1587058047_5e98957f53451.png!small)

构建恶意页面：qrcode.php

![](https://image.3001.net/images/20200417/1587058059_5e98958b8f419.png!small)

开启轮询脚本：

![](https://image.3001.net/images/20200417/1587058071_5e98959700ba9.png!small)

手机微信端访问恶意页面。

轮询处获得cookie：

![](https://image.3001.net/images/20200417/1587058085_5e9895a5947ee.png!small)

以上就是本人在实战中挖到的劫持漏洞，至于修复方式的话，本人暂时没想到太多。猜想：微信客户端点击确认的时候，加入一个csrf_token可能会好很多。如果大家有什么好的建议，欢迎在评论处分享！

 ***本文作者：xiaopan233，转载请注明来自FreeBuf.COM**

