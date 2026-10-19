***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![PC-HackerOne.jpg](https://image.3001.net/images/20181112/1541989559_5be8e4b7f2996.jpg!small)**
**大家好，今天我要和大家分享的是一个HackerOne相关的漏洞，利用该漏洞，我可以绕过HackerOne漏洞提交时的双因素认证机制（2FA）和赏金项目中（Bug
Bounty Program）的上报者黑名单限制。该漏洞严重性最终被定级为中级，漏洞原因为授权不当（ Improper
Authorization），赏金为$10,000美金。**

## 漏洞说明

该漏洞是一个功能性Bug，最初上报给HackerOne时，他们给我设置的赏金是 $2,500，漏洞评级CVSS
5.0，但经HackerOne安全团队对这个漏洞执行根本原因分析流程（Root Cause
Analysis，RCA)之后，他们又基于我上报的这个漏洞，发现了另一个高危严重漏洞（CVSS
7.1)，因此，HackerOne官方最终又额外奖励了我$7,500美金。

## 漏洞发现

众所周知，HackerOne是一个漏洞众测网站，而我也经常在上面参与各个厂商的漏洞测试。通常，我总会留意HackerOne的一些新推出功能，某天，偶然间我就发现了其一个名为[“嵌入式漏洞报告样式”（Embedded
Submission Form）的试用功能](https://docs.hackerone.com/programs/embedded-submissions-form.html)，利用该功能，白帽们可以：

> 1、利用其嵌入式提交脚本，提供个人邮箱后，不用创建HackerOne账号就可上报提交漏洞，之后HackerOne会向这个邮箱反馈具体的漏洞处理进程；
>
> 2、另外，如果不提供个人邮箱，就会被视为匿名漏洞提交，这种提交方式下，白帽们就不会获得任何上报积分和赏金。匿名上报是该功能的一个选项。

大家可以点[此处官方说明查看](https://docs.hackerone.com/programs/embedded-submissions-form.html)Embedded Submission Form功能的具体使用方法。

围绕该功能，我有了以下授权不当（Improper Authorization）的漏洞发现：

> 1、在上报提交某个厂商测试项目的漏洞时，可以利用“嵌入式漏洞报告样式”（Embedded Submission
> Form）功能，在不开启匿名上报时，绕过HackerOne对漏洞提交时的双因素认证（2FA）条件限制，当然了绕过这个2FA限制，这个提交漏洞还是计为你的上报漏洞。具体的2FA设置可点此查看；
>
>
> 2、可以绕过厂商漏洞测试项目的上报者黑名单限制。这里的上报者黑名单，也就是说，如果某名白帽总是上报一些无关漏洞，或存在超出测试范围或违反测试方法的行为，那么测试厂商可以把这名白帽拉到黑名单中，就不会再收到该名白帽的上报漏洞了。这个上报者黑名单功能可点此查看。

## 漏洞分析

### 绕过HackerOne对对漏洞提交时的双因素认证（2FA）

通常，漏洞测试厂商在白帽们提交漏洞之前，可以强制漏洞提交者实行一个双因素认证（2FA）校验，URL样式大概如此：

> <https://hackerone.com/><program>/submission_requirements

具体设置如下：

![01.jpg](https://image.3001.net/images/20181112/1541989153_5be8e321db1d2.jpg!small)像漏洞测试厂商[Parrot
Sec的测试项目](https://hackerone.com/parrot_sec)，在该功能下，就要求漏洞提交者在提交漏洞之前，执行一个双因素认证（2FA）校验步骤，即使我尝试者在我自己的账户中禁用漏洞提交的2FA校验操作，但是，最终也还是不行，这样的话我会被Parrot
Sec阻拦掉不能提交漏洞了，所以，必须得启用2FA校验操作。

![02.jpg](https://image.3001.net/images/20181112/1541989169_5be8e3312e5b7.jpg!small)现在，我们利用“嵌入式漏洞报告样式”（Embedded
Submission Form）功能，来尝试看看是否能绕过这个漏洞提交的2FA校验机制：

> 1、登录你自己的HackerOne账户，去掉你账户中的2FA校验功能设置；
>
> 2、来到漏洞测试厂商Parrot Sec的赏金项目下<https://hackerone.com/parrot_sec>，点击提交漏洞（Submit
> Report），此时，因为你自己没启用2FA校验功能，所以是不能提交漏洞的，只有启用2FA校验功能才能顺利提交漏洞；
>
> 3、从Parrot Sec厂商的漏洞测试策略中，找到Embedded Submission
> Form相关的漏洞提交链接，其漏洞提交链接形如：<https://hackerone.com/><redacted_UUID>/embedded_submissions/new，其中的redacted_UUID为一串类似0a1e1f11-257e-4b46-b949-c7151212ffbb的串号数字。
>
> 4、在你的HackerOne账户登录状态下，利用上述的Embedded Submission
> Form功能提交漏洞，然后就能不需要测试项目强制的2FA校验要求了。后经测试，这种方式的漏洞提交，还能绕过测试项目中设置的漏洞提交频率（Report
> Rate Limit）和内部功能滥用限制（ Internal Abuse Limit）。  
>

漏洞造成的影响：

白帽子们可以绕过漏洞测试项目中的2FA校验、漏洞提交频率和其它内部功能滥用限制，这种不当的授权操作，对厂商的漏洞处理形成干扰，也破坏了HackerOne平台的严谨安全性。HackerOne安全团队基于此发现的第二个漏洞比较严重，如果另一名白帽在此时正在编写漏洞提交报告，那么攻击者可以访问到其漏洞报告中的附件内容。

### 绕过漏洞测试项目的上报者黑名单限制

如果某名黑客的提交行为与测试项目中的策略不一致，或超出测试范围，或违反测试方法，测试厂商可以把该名白帽拉入黑名单，禁止接收到其提交漏洞，当然还能在公开（Public）或私密（Private）项目中限制该名白帽。更多说明[点此查看](https://docs.hackerone.com/programs/banning-hackers.html)。具体设置如下：

![03.png](https://image.3001.net/images/20181112/1541989305_5be8e3b98823d.png!small)于是，我想到了我的朋友
Ace Candelario ，他是Parrot Sec公司的公司代表，也是Parrot
Sec公司在HackerOne平台的漏洞确认分类人。因此，我请求他在Parrot
Sec测试项目后台把我的HackerOne账户拉入黑名单，禁止我提交漏洞。之后，我点击提交漏洞就会出现以下错误页面：

![04.png](https://image.3001.net/images/20181112/1541989320_5be8e3c8b87ff.png!small)好吧，我已经成为了Parrot
Sec漏洞测试项目的黑名单人员了。但是，当我用前述绕过2FA的方法步骤来尝试时，我还是可以继续向Parrot Sec提交漏洞！

漏洞影响：

一些恶意的白帽子们，在被拉入黑名单之后，还能以此继续向测试厂商提交漏洞，对厂商的漏洞处理形成干扰，也破坏了HackerOne平台的严谨安全性。

## 漏洞原因

经HackerOne安全团队评估，以上两个漏洞的触发原因相同，都是由于在利用Embedded Submission
Form功能编写漏洞报告时，其中的调试请求 uuid/embedded_submissions 中启用了不安全的检验方法
interact_without_authorization，这种情况下，后端的访问控制列表机制（ACL）就会被绕过。

##
![2018-11-12_100825.png](https://image.3001.net/images/20181112/1541989460_5be8e45443484.png!small)漏洞上报进程

> 2018.10.04 02:41:19 — 向HackerOne安全团队提交漏洞
>
> 2018.10.05 20:07:59 — HackerOne确认并分类漏洞
>
> 2018.10.05 20:53:21 —HackerOne向我发放 $10,000美金赏金
>
> 2018.10.06 00:38:15 — CVSS 7.1的高危漏洞被及时修复，CVSS5.0漏洞正在修复中
>
> 2018.10.25 23:11:03 —CVSS5.0漏洞被修复
>
> 2018.10.25 23:11:03 —漏洞处理完成

更多技术信息请参考[原漏洞报告](https://hackerone.com/reports/418767)。

 ***参考来源：[medium](https://medium.com/japzdivino/bypass-hackerone-2fa-requirement-and-reporter-blacklist-46d7959f1ee5)，clouds编译，转载请注明来自FreeBuf.COM**  

