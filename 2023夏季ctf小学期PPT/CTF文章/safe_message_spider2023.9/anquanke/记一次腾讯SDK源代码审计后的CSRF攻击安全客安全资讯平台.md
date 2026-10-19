# 记一次腾讯SDK源代码审计后的CSRF攻击

阅读量 **174785**

|评论 **1**

发布时间 : 2018-03-23 15:01:43

 **x**

##### 译文声明

本文是翻译文章，文章原作者 呆哥@ChaMd5，文章来源： ChaMd5安全团队

原文地址：<http://mp.weixin.qq.com/s/fiTejXSF5Mlm-a0KqvWCQw>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01c035113ddae3f908.jpg)

## 0x00 前言

初进ChaMd5安全团队，应M姐姐之邀写下这篇技术文章，这篇文章主要讲述本人近期代码审计腾讯的第三方登录SDK包时发现的一个漏洞，阅读这篇文章需要读者对OAuth2.0协议的原理和应用特别熟悉，如果读者对此不了解，请参考以下链接：

OAuth2.0协议RFC 文档：

<https://tools.ietf.org/html/rfc6749>

QQ开放平台的接入说明：

<http://wiki.connect.qq.com/oauth2-0%e7%ae%80%e4%bb%8b>

这是我之前写的一篇分析OAuth2.0协议安全性的文章：

<https://www.anquanke.com/post/id/98392>

## 0x01 攻击模型分析

我在这篇文章里讲的这种攻击方法是针对OAuth协议的一种CSRF攻击，大家都知道，很多网站都有绑定第三方账号的功能，这种攻击手段就是利用了网站的这种功能，为了深入分析漏洞，我先把绑定第三方账号的流程分析一下：

Step 1：某妹子使用账户密码登录XX网站

Step 2：妹子选择绑定QQ账户，在输入凭证信息后，QQ返回如下形式的链接：

<http://xx.com/Index.php?Code=XXX>

Step 3: 妹子访问上述链接，服务器接收到code参数，进行验证后与当前用户绑定。

为了说明这种攻击方法，我从2012年全国网络与信息安全峰会上知道创宇的一位大佬的PPT里借用一张图：

![](https://p1.ssl.qhimg.com/t016e307b50ba758b81.png)

这种攻击方式看似复杂其实说起来也很简单，主要的问题出现在了上图的第四步中，即攻击者构造链接http://xx.com/Index.php?Code=XXX，其中Code参数绑定的是攻击者的QQ账户，然后发给Victim诱骗点击（CSRF），Victim点击之后，他的账户就与攻击者的QQ账户绑定了，这样攻击者就能通过其QQ登录Victim的账户，实现用户劫持！

当然了，为了防止这种攻击，腾讯在返回的授权登录链接中增加了一个state参数用于防止类似的CSRF攻击。用户在请求使用QQ登录的时候会生成一个与session绑定的不可预测字符串state，并把这个参数发送给授权服务器，授权服务器验证完用户身份后会返回如下形式的链接：

http://xx.com/Index.php?Code=XXX&state=XXX

在接收到此链接时，xx.com会先检测当前session中的state参数和收到的链接中的state参数是否匹配，如果匹配才会进行下一步的操作。这样的话，即使攻击者把自己的授权链接发给Victim，也会因为state验证失败而无法绑定攻击者的账户（攻击者无法预测Victim的session中的state参数，因此就无法构造恶意链接来进行CSRF攻击）。

## 0x02 漏洞分析

在详细了解了攻击原理之后，我们来剖析一下QQ登录的官方SDK文件。

这里我们废话不多说，直接定位到核心类文件Oauth.class.php

![](https://p3.ssl.qhimg.com/t01628fa38b69671517.png)

在这个类文件中qq_login方法用于第一步生成state参数并跳转到QQ授权登录接口，可以看到state参数在第36行生成并紧接着调用recorder类的write方法写入到session中，跟进recorder类继续分析：

![](https://p3.ssl.qhimg.com/t0110185ec7ab84fe39.png)

定位到32行，write方法是把传入的值写到self::$data中，在看到26行，构造函数中self::$data被初始化为一个空数组。

![](https://p3.ssl.qhimg.com/t010181d5e87b5fd189.png)

在最后的析构函数中self::$data被存入到session中，这里看上去没有什么大问题，继续向下分析，我们找到Oauth.class.php中的qq_callback方法：

![](https://p2.ssl.qhimg.com/t0190b8def85d915a70.png)

qq_callback方法用于验证state参数并利用传入的code参数获得access_token，我们主要关注state参数的验证阶段，在第57行我们看到有一个if条件判断当前session中的state参数（$state）和链接中传入的state参数（$_GET[‘state’]）是否匹配，如果不匹配则直接调用showError方法die掉：

![](https://p2.ssl.qhimg.com/t01fb9fe6203b7396e2.png)

但是，问题就出现在这里！之前我们已经分析到，state参数在qq_login方法中生成，但是如果Victim没有调用这个方法，self::$data就会被构造函数初始化为一个空数组，再来看一下recorder类中的read方法：

![](https://p2.ssl.qhimg.com/t0184342ad74c3f4b72.png)

如果self::$data为空则返回null，因此这里存在一个很明显的逻辑缺陷，只要攻击者把恶意链接的state参数留为空，这时$_GET[‘state’]为空值，$state也为空值，if($_GET[‘state’]
!= $state)为false，这样就可以完美的躲过CSRF检测，嘿嘿！

## 0x03 后记

这个漏洞从确认到修复只用了三个小时的时间，腾讯SRC的响应速度也是非常惊人。

![](https://p5.ssl.qhimg.com/t0106498b7ddd60db12.png)

在最新版的SDK文件中，在验证state时会先判断当前的session中是否保存有state参数，即判断当前用户是否调用过qq_login方法，这样就可以成功的阻止类似的CSRF攻击了：

![](https://p5.ssl.qhimg.com/t01e9d1ed4630bbc16c.png)

本文翻译自 ChaMd5安全团队
[原文链接](http://mp.weixin.qq.com/s/fiTejXSF5Mlm-a0KqvWCQw)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **呆哥** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/102029](/post/id/102029)

安全客 - 有思想的安全新媒体

本文转载自: [ ChaMd5安全团队](http://mp.weixin.qq.com/s/fiTejXSF5Mlm-a0KqvWCQw)

如若转载,请注明出处： <http://mp.weixin.qq.com/s/fiTejXSF5Mlm-a0KqvWCQw>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [SDK](/tag/SDK)
  * [OAuth2.0协议](/tag/OAuth2.0协议)
  * [CSRF攻击](/tag/CSRF攻击)

 **+1** __6赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101430193/C05A78457374038CA9B7C6740E22D232/40)
呆哥

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

