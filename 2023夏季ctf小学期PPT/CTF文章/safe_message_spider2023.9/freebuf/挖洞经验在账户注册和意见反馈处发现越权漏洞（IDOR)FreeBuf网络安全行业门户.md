**![01.png](https://image.3001.net/images/20191226/1577356065_5e048b214a5db.png!small)**

**今天分享几点关于越权漏洞（IDOR）的发现经验，这类型漏洞通常发生在Web应用提供给用户基于输入的对象中，漏洞造成的影响将会致使攻击者可以绕过授权限制，访问到目标系统内其它不应该被访问到的资源或数据。**

## IDOR概述

简单来说，假设目标网站有两个用户U1和U2，两者账户中都存储有个人文件，但只有自己才有权限查看访问到这些文件。打个比方，也即U1只能访问到自己的账户文件，不可访问U2的账户文件。

某天，U1访问他自己账户中的文件blahBlah.pdf，具体链接如下：

> <https://whocare.com/file/23>

上述链接中假设最后的数字23是与自己账户对应的一个参数，但好奇的U1用户却随手修改了这个数字参数，把它改成了50，然后发起了访问，链接如下：

> <https://whocare.com/file/50>

但正好这一改动，U1在自己账户权限内竟然看到了U2账户的文件。

所以问题出在哪里呢？原因在于Web应用在基于用户输入的直接对象访问机制中，缺少了对访问对象的身份验证措施。如何来发现IDOR漏洞？其实，IDOR就像XSS一样存在广泛，只要你清楚目标Web应用的设计架构或工作流，非常容易发现。这里我分享几点IDOR漏洞的发现经验，仅供参考。

## 在用户注册处发现IDOR漏洞

在网站注册机制中发起数据包拦截，目标网站whocare.com调用了一个账户注册API，Burp捕获的账户注册请求数据包如下：

    
    
    POST /analytics/index.php/plus/registerportal?user_id=43657&key=344246b382b1d70c25ea14ed6f2760c6 HTTP/1.1
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 239
    
    Host: api.whocare.com
    
    Connection: close
    
    Accept-Encoding: gzip, deflate
    
    User-Agent: okhttp/3.4.1
    
    email=test@whocare.com&password=as&username=&firstname=tvbb&lastname=gvcz&mobile=&country=test&city=hfhdggd&birthday_full=&gender=fknefjn

可以看到，在上述数据包的POST操作中包含了user_id参数，这里出于测试目的，我们把它修改为其它字符串随机值，然后服务端响应回来的消息中有了这样的提示：用户已经存在！更为重要的是，服务端响应回来的信息中包含了与该注册用户相关的姓名、邮箱、联系地址等等。响应数据包如下：

    
    
    HTTP/1.1 200 OK
    
    Date: Tue, 05 Mar 2019 12:53:30 GMT
    
    Content-Type: text/html
    
    Connection: close
    
    Set-Cookie: __cfduid=dc4d54bb59b5c4a2c8501e3ed1cd5952b1551790409; expires=Wed, 04-Mar-20 12:53:29 GMT; path=/; domain=.whocare.com; HttpOnly
    
    Vary: Accept-Encoding
    
    Server: cloudflare
    
    CF-RAY: 4b2c3badddb3ce21-LHR
    
    Content-Length: 311
    
    {"error":"exist","user":[{"id":"34666","username":"admin","firstname":"Pappu","lastname":"Rahul","email":"admin@whocare.com","mobile":null,"gender":"male","birthday":null,"country":"","city":null,"address":null,"address1":[Reducted],"postcode":[Reducted],"ip_address":[Reducted],"app_id":[Reducted]}]}

而且通过这样，我甚至可以通过暴力枚举用户参数user_id，大量获取目标网站用户信息，当然其中也会包含管理员信息。

## 在邮件订阅（Subscribe）列表中发现IDOR漏洞

同样，我们以whocare.com为目标网站，它为新用户提供了一个订阅选项，可以通过用户邮件方式获取一些网站的最新资讯。而在用户设置面板中，存在一个订阅取消按钮，当点击该按钮之后，它会向注册用户发送一个取消订阅的通知链接，URL如下：

> <http://whocare.com/deleteNewsletter/dGVzdGVybWFpbEBnbWFpbC5jb20=>

仔细看可知道，它结尾包含了一个base64编码的字符串，解密后dGVzdGVybWFpbEBnbWFpbC5jb20= :
testermail@gmail.com，这里看似这种动作未对请求做身份校验，所以，在此我们需要其他注册用户的绑定邮箱来进行测试，看看是否能对其他注册用户执行订阅取消操作。

这里的一种攻击可能性为：我们要以收集大量目标网站注册用户的邮箱，然后分别把它们进行base64编码，形成字典，放到Burp的Intruder模块中，进行自动化攻击测试，这样一来，就形成了对批量用户的订阅取消动作。这里可以综合利用上述的注册处IDOR漏洞来形成更大的威胁。  

## 在意见反馈的邮件转发处发现IDOR漏洞

比如还是在whocare.com中，如果用户向目标网站提交意见反馈（Feedback）的数据包如下：

    
    
    POST /Services/PostContactUsEmail HTTP/1.1
    
    Host: www.whocare.com
    
    Connection: close
    
    Content-Length: 327
    
    Accept: */*
    
    Origin: https://www.whocare.com
    
    X-Requested-With: XMLHttpRequest
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    Referer: https://www.whocare.com/feedback
    
    Accept-Encoding: gzip, deflate
    
    Accept-Language: en-US,en;q=0.9
    
    Cookie: [REDUCTED]
    
    ContactUs_Name_Txt=hiname&ContactUs_Email_Txt=attacker@gmail.com&ContactUs_MessageType_Txt=%D8%A7%D8%B3%D8%AA%D9%81%D8%B3%D8%A7%D8%B1&ContactUs_Department_Txt=feedback@whocare.com%23%D8%A7%D9%84%D8%AF%D8%B9%D9%85+%D8%A7%D9%84%D9%81%D9%86%D9%8A&ContactUs_MessageBody_Txtthis+is+the+comment&ContactUs_Captcha_Txt=QBAQLU

仔细看其中提交的参数，它包含了以下几个重要信息：

> ContactUs_Department_Txt= 将会收到反馈意见的邮箱地址
>
> ContactUs_Email_Txt= 当前用户用来发送反馈意见的邮箱地址
>
> ContactUs_MessageBody_Txt= 用户发送的反馈意见信息

上面有两个地方的邮箱地址我们可以进行修改，那就是：

> ContactUs_Department_Txt=admin@whocare.com
>
> ContactUs_Email_Txt=任何你想发送邮件的用户邮箱地址，或者恶意一点，把它设为网站所有用户邮箱地址。

这样一来，所有网站用户都会收到一封来自管理员邮箱的邮件，这可以用来作为钓鱼攻击的一个切入点。

## IDOR的修复建议

1、请求或其它操作动作中实施合理的访问权限控制措施；

2、对涉及用户相关的参数使用强加密或随机数生成，不要使用如id=3这种简单直白的数字形式；

3、更多防护措施请[点此参考OWASP官方说明](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)。

 ***参考来源：[medium](https://medium.com/bugbountywriteup/stories-of-idor-4966369e6d82)，clouds 编译整理，转载请注明来自 FreeBuf.COM**  

