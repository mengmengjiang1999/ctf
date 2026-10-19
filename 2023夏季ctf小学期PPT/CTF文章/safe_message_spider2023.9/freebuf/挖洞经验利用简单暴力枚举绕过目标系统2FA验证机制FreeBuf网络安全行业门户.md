**![](https://image.3001.net/images/20191112/1573551452_5dca7d5c995f5.jpg!small)**

**今天分享的这篇Writeup是作者在参与漏洞众测中，针对目标系统的动态口令OTP (One Time
Password)，通过利用简单的暴力枚举方法，实现了对目标系统双因素验证机制2FA (Two-Factor
Authentication)的绕过或破解。目标系统是印度最大的旅行服务公司网站，其采用了动态口令OTP作为双因素验证2FA的实现手段。**

通常来说，OTP是从0000到9999的4位数组合，假如OTP有一万种可能性的组合，在如今强大的计算机时代，处理10000种组合也只需几分钟的时间。所以，如果OTP的验证机制不当，任何人都可以通过简单的暴力枚举来绕过它。

##  为什么我可以绕过2FA？

> 目标系统对不成功的请求尝试不作速率限制
>
> 目标系统对不成功的请求尝试没有新的动态口令措施

前提准备：

> Web浏览器、BurpSuite。
>
> 绕过2FA的复现过程

##  绕过2FA的复现过程

1、开启BurpSuite，使用手机号码登录目标系统网站，这里，故意输错系统发送到你手机中的动态OTP（这里我们随便输入1234），然后用BurpSuite捕获流量；

![](https://image.3001.net/images/20191112/1573551211_5dca7c6b2d48d.png!small)

从BurpSuite中我们可以看到OTP API的相关信息 - verifyOTP?otp=：

![](https://image.3001.net/images/20191112/1573551221_5dca7c75a3a8b.png!small)

2、把这次OTP的发送过程右键 Send to intruder：

![](https://image.3001.net/images/20191112/1573551233_5dca7c8177e98.png!small)![](https://image.3001.net/images/20191112/1573551247_5dca7c8fe98e1.png!small)

3、选择otp=1234占位符，并把它设置为简单暴力枚举变量方式：

![](https://image.3001.net/images/20191112/1573551260_5dca7c9c6ce10.png!small)

4、选择Payload标签项，把其修改为任意形式的组合，然后点击attack：

![](https://image.3001.net/images/20191112/1573551273_5dca7ca9f0d1b.png!small)

5、攻击开始。从枚举响应结果中，我们可以看到一个长度为2250的异常响应，不出意外，就是它了：

![](https://image.3001.net/images/20191112/1573551318_5dca7cd6d2f71.png!small)

6、 用该OTP配合登录，可以成功有效！

![](https://image.3001.net/images/20191112/1573551335_5dca7ce70eb6e.png!small)

***参考来源：[medium](https://medium.com/clouddevops/bugbounty-how-i-cracked-2fa-two-factor-authentication-with-simple-factor-brute-force-a1c0f3a2f1b4)，clouds
编译整理，转载请注明来自 FreeBuf.COM**

  

