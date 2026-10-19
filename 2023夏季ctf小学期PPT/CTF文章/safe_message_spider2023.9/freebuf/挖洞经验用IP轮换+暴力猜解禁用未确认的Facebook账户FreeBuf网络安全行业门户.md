![](https://image.3001.net/images/20191205/1575539551_5de8d35f18b37.jpeg!small)

本文分享的是通过IP轮换结合暴力破解方法禁用Facebook新创建的未确认用户，此前在2014年Facebook曾针对该漏洞做过修复，但是由于修复策略不够完善，导致可以用IP轮换方法再次绕过这种防护，形成对任意新创建未确认Facebook用户的间接禁用攻击。

## 早前的账户创建确认漏洞

在[2014年Facebook曾针对该漏洞做过修复](https://pagefault.me/2014/10/23/disabling-fb-accounts/)。当时的漏洞情况是这样的：如果你用个人邮箱注册一个Facebook账户，创建完成之后，Facebook会向你的邮箱发送一个5位数确认码邮件，但出于个人邮箱被恶意注册的安全原因考虑，Facebook还会在邮件末尾附加上一个“未曾注册过Facebook”的选项按钮，以便让那些个人邮箱被恶意注册的用户提交上报Facebook。如下：

![](https://image.3001.net/images/20191205/1575539368_5de8d2a8411e9.png!small)

提交之后，会产生以下链接：

> [https://www.facebook.com/confirmemail.php?e=victim@mail.com&c=5-DIGIT-> CODE&report=1](https://www.facebook.com/confirmemail.php?e=victim@mail.com&c=5-DIGIT-> CODE&report=1)

移动端对应的是：

> [https://m.facebook.com/confirmemail.php?e=victim@mail.com&c=5-DIGIT-> CODE&report=1&message=1](https://m.facebook.com/confirmemail.php?e=victim@mail.com&c=5-DIGIT-> CODE&report=1&message=1)

漏洞原因在于，其中的 c
参数，也就是Facebook发送过来的一个5位数确认码，可以被攻击者暴力破解猜测到，因此可导致攻击者用此种方式去禁用任何未及时确认的Facebook新注册账户。该漏洞已于2014年10月被Facebook修复。

## 现在存在的问题

通过测试分析，作者发现该路径下设置了访问频率限制（Rate limit），针对5位数确认码做暴力猜解时会被Facebook阻拦掉。如下：

![](https://image.3001.net/images/20191205/1575539424_5de8d2e045cc8.png!small)

我猜想Facebook之前的修复策略如果是基于IP的限制方法的话，我可以通过变换IP地址来进行暴力猜解啊。果然，当我变换新的IP地址再进行进行暴力猜解之后，Facebook完全不会实施阻拦。

![](https://image.3001.net/images/20191205/1575539582_5de8d37e4ce85.png!small)

为了更顺利的实施这种暴力猜解工作，需要对每次请求的IP地址都做出变化，也即IP轮换。为了综合利用IP轮换+暴力猜解，我谷歌了一些在线资料，并最终用Luminati+Burp搭建了一个测试环境（[参考此处](https://medium.com/@lokeshdlk77/how-to-rotate-ip-address-in-brute-force-attack-e66407259212)），完美绕过了Facebook后端限制，并有效地猜测出Facebook5位数确认码，实现对Facebook未确认账户的禁用。

## 漏洞影响

>
> 1、对于受害者用户来说，如果攻击者以此方式禁用了它的Facebook账户，那么由于其邮箱地址已经被Facebook列入黑名单，所以受害者在今后就无法用该邮箱注册Facebook账户了；
>
>
> 2、另外，如果攻击者知道受害者用户的确切注册邮箱，即使用户已经经过了Facebook确认，但一样能通过此种方式去举报受害者用户邮箱，形成账户滥用提交，后期可由Facebook对受害者的Facebook账户实现禁用，整个过程无需与用户进行任何交互。

## 漏洞上报及处理进程

> 2019.6.30 : 漏洞初报
>
> 2019.7.3 : Facebook深入确认
>
> 2019.8.23: Facebook完成修复
>
> 2019.8.23 : Facebook奖励了$1000

***参考来源：[medium](https://medium.com/@lokeshdlk77/disable-any-unconfirmed-account-in-facebook-123aeba19426)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

