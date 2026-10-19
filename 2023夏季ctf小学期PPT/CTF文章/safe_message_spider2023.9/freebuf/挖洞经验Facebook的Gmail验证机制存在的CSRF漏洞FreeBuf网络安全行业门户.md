![maxresdefault.jpg](https://image.3001.net/images/20190808/1565268545_5d4c1a4185204.jpg!small)

**本文分享的是一个Facebook CSRF漏洞，用Gmail或G-Suite账户来验证新创建Facebook账户时存在的CSRF令牌验证机制漏洞，攻击者利用该漏洞，可在验证新创建Facebook账户时，以最小用户交互方式用受害者邮箱验证其注册的Facebook账户，实现间接CSRF攻击。漏洞最终获得Facebook官方$3000美金奖励。**

##  OAuth登录机制对CSRF token验证不足

当用户用Gmail或G-Suite账号来创建一个新的Facebook账户时，存在以下两种身份验证机制：

> 从Gmail中接收5位数的验证码，然后在Facebook网页中输入以确认
>
> 从Gmail或G-Suite账号的第三方进行OAuth授权跳转登录

![2019-08-08_204509.jpg](https://image.3001.net/images/20190808/1565268345_5d4c197990930.jpg!small)

要绕过第一种方法估计很难了，Facebook后端部署的Checkpoint安防设备和强大的速率限制条件，会毫不客气地阻断任何暴力破解和可疑行为。所以，我们来观察一下第二种方法，经过一番测试，我在其中发现了一个CSRF漏洞，原因在于，在OAuth授权跳转登录过程中缺少必要的CSRF令牌验证机制。OAuth
Login链接如下：

>
> `[https://accounts.google.com/o/oauth2/auth?client_id=15057814354-80cg059cn49j6kmhhkjam4b00on1gb2n.apps.googleusercontent.com&state=ARf8Zzq50032sck96TSFssFhWVvMUWO7KEJlq3n3_7Yp73WcWvlpyFn1dpdoUGv5QOLAn2ffrRZ_L_3ZfAncV_I0Ihog80LabpToEfHUIgfzBK720-pGRNbXGeYkETOwjeCfbsl70shdjuLnp3jC4dIsn-> xPTwoggineLFh34F61bbYGsg&response_type=code&redirect_uri=https%3A%2F%2Fwww.facebook.com%2Foauth2%2Fredirect%2F&scope=openid+email&login_hint=victim_email@gmail.com](https://accounts.google.com/o/oauth2/auth?client_id=15057814354-80cg059cn49j6kmhhkjam4b00on1gb2n.apps.googleusercontent.com&state=ARf8Zzq50032sck96TSFssFhWVvMUWO7KEJlq3n3_7Yp73WcWvlpyFn1dpdoUGv5QOLAn2ffrRZ_L_3ZfAncV_I0Ihog80LabpToEfHUIgfzBK720-pGRNbXGeYkETOwjeCfbsl70shdjuLnp3jC4dIsn-> xPTwoggineLFh34F61bbYGsg&response_type=code&redirect_uri=https%3A%2F%2Fwww.facebook.com%2Foauth2%2Fredirect%2F&scope=openid+email&login_hint=victim_email@gmail.com)`

请注意，其中的state参数为一个CSRF令牌，该令牌用于在一些跨站点的请求响应中，去验证那些经身份验证过的用户，以此来防止攻击者蓄意的CSRF攻击。

通常来说，如果在上述OAuth Login过程中，该state参数由客户端的 Firefox
浏览器生成，那么，该参数令牌也仅限于在该Firefox浏览器中验证有效。但是，这里的问题是，该OAuth
Login机制还缺乏必要的验证措施，也就是，这里的这个state参数（CSRF
token）可用在任何其他客户端浏览器中实现有效验证。所以，对攻击者来说，可以简单地把上述URL链接进行嵌入构造到一个网页中，只要受害者点击到该网页，攻击者就能以受害者身份（如注册邮箱victim_email@gmail.com）完成Facebook账户的身份验证，实现间接的CSRF攻击。

但是，这里还有一个问题，那就是受害者在点击攻击者构造的页面之前，攻击者Facebook账户需要在受害者浏览器中实现登录，而这里，刚好可用Facebook的一键式登录（Log
In With One
Click）来完成这个动作。把以下Facebook的一键式登录链接嵌入到恶意网页的IFrame中，当受害者点击网页后，攻击者Facebook账户就可在受害者浏览器中完成登录加载。

>
> [https://www.facebook.com/recover/password/?u=100008421723582&n=232323&ars=one_click_login&fl=one_click_login&spc=1&ocl=1&sih=0](https://www.facebook.com/recover/password/?u=100008421723582&n=232323&ars=one_click_login&fl=one_click_login&spc=1&ocl=1&sih=0)

之后，当OAuth Login按钮被受害者点击后，受害者邮箱被攻击者用来确认登录了Facebook，之后，再用以下链接来退出攻击者的Facebook账户：

> <https://m.facebook.com/logout.php?h=17AfealsadvYomDS>

结合以上方法构造出一个恶意页面，攻击者就能用受害者邮箱（如以下视频中的Gmail）完成新创建Facebook账户的验证了。

>
> （需要视频嵌入）[https://www.youtube.com/watch?time_continue=8&v=SmRVIip_ySE](https://www.youtube.com/watch?time_continue=8&v=SmRVIip_ySE)

##  总结

总体来说，该漏洞危害确实有限，原因在于Facebook的第三方OAuth Login过程中缺乏对CSRF
token的有效验证，导致攻击者可以利用不变的CSRF
token来做文章。但随着Web应用的不断发展，各种场景下的第三方OAuth机制越来越多，其存在的问题和漏洞将会非常值得注意。

![2019-08-08_204820.jpg](https://image.3001.net/images/20190808/1565268517_5d4c1a25d0b29.jpg!small)

##  漏洞上报进程

> 2019.5.10 : 漏洞初报
>
> 2019.5.17 : Facebook跟进调查
>
> 2019.5.31 : Facebook修复
>
> 2019.6.19 : Facebook奖励我$3,000

***参考来源：[medium](https://medium.com/@lokeshdlk77/csrf-email-confirmation-vulnerability-for-gmail-g-suite-in-facebook-5ab551a0a526)，clouds编译整理，转载请注明来自FreeBuf.COM**

  

