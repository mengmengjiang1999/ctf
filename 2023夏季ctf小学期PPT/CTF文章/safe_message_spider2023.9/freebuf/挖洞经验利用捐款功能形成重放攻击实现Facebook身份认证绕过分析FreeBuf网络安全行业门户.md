**![1_WZ7h4J66VN0exytlHKyYkA.jpeg](https://image.3001.net/images/20191210/1575969613_5def634d6a6e3.jpeg!small)**

**该篇Writeup是利用Facebook捐款功能形成身份验证重放攻击，实现Facebook账户双因素认证（2FA）绕过的漏洞，原因在于Facebook在URL会话中加入的身份认证措施不够完善。**

## 漏洞情况

起因源于我收到一个朋友的捐款活动消息，当我用手机版Facebook-App (IOS)
点击其页面中的“捐款（donate）”按钮后，它就自动跳转到了一个用***或Paypal支付的Web页面，该页面的后置路径为：{/donation/login/?nonce=xxxxx&uid=xxxxxx}。

![1_hYvRjp4XPBw9MZZu-lsIsg.jpeg](https://image.3001.net/images/20191210/1575969463_5def62b7c1c53.jpeg!small)

其产生的URL链接为：

>
> [https://m.facebook.com/donation/login/?nonce=xxxxxx&uid=](https://m.facebook.com/donation/login/?nonce=xxxxxx&uid=){USER_ID}

但是，访问了该链接之后，我发现，即使我是Facebook退出状态，根本没有登录Facebook，当用Web浏览器访问上述的URL链接后，再次访问facebook.com我就能无需任何密码或其它身份认证手段，顺利地进入我的Facebook账户了！

作为验证，我把上述由我Facebook账户产生的URL捐款链接[https://m.facebook.com/donation/login/?nonce=xxxxxx&uid=](https://m.facebook.com/donation/login/?nonce=xxxxxx&uid=){USER_ID}
，发送给了我的另外一个朋友，果不其然，在他电脑中，当他访问了该链接之后就能顺利地从facebook.com进入我的Facebook账户了！无需任何密码或2FA身份认证措施！而且，即使是更改了我Facebook账户的登录密码，他一样可以保持对我Facebook账户的登录状态。

## 漏洞复现

> 1、用Facebook
> App(IOS)从一些公益性组织页面中发现捐款页面，如：<https://www.facebook.com/donate/xxx/xxx/>
>
> 2、尝试发起一次捐款操作；
>
>
> 3、之后你会跳转到链接：“[https://m.facebook.com/donation/login/?nonce=xxxxxx&uid=xxxxxx](https://m.facebook.com/donation/login/?nonce=xxxxxx&uid=xxxxxx)
> ”；
>
> 4、拷贝该条URL链接，把它用于其它你未登录过Facebook账户的设备中，用Web浏览器点击访问；
>
> 5、之后访问Facebook.com主页，你就会发现你已经自动登录到你的Facebook账户中了；
>
>
> 6、即使你把Facebook账户密码或相关会话进行了清理，但拥有该条URL链接的攻击者一样可以保持对你Facebook账户的登录状态，实现无需密码或其它2FA措施的认证绕过。

一般来说，我们会在一些需要身份认证的链接中加入时间戳timestamp，综合UID和一次应用参数nounce（number used
once）来防止会话的重放攻击，但是Facebook在这里做的不够完善，因此导致了漏洞。该漏洞可以导致对身份认证机制的绕过，对Facebook账户形成持久登录状态。

## 漏洞上报及处理进程

> 2019.6.18 — 漏洞初报
>
> 2019.6.19 — 漏洞分类
>
> 2019.6.21 — Facebook修复漏洞
>
> 2019.6.21 — 修复确认
>
> 2019.6.21 — 赏金发放

 ***参考来源：[medium](https://medium.com/@0xBarakat/broken-session-permanent-access-to-facebook-users-cfed68684113)，clouds 编译整理，转载请注明来自 FreeBuf.COM**  

