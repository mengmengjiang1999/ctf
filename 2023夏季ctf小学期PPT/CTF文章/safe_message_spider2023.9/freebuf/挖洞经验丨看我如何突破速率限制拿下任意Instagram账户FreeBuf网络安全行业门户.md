***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![hack-instagram.jpg](https://image.3001.net/images/20190715/1563202303_5d2c92ff4e8a8.jpg!small)

 **该Writeup是关于Instagram平台的任意账户劫持漏洞，作者通过构造出突破速率限制（Rate
Limiting）的方法，可暴力猜解出任意Instagram账户的密码重置确认码，以此实现Instagram账户劫持。最终Facebook和Instagram的安全团队联合修复了该漏洞，并对作者给出了高达$30,000美金的奖励。以下是作者的分享。**

##  **从密码重置功能入口试运气**

在著名的数据泄露事件发生之后，Facebook在全平台不断改进它的安全控制措施。出于对包括账户劫持等严重漏洞的奖励，Facebook增加了相应的漏洞赏金数额。我想试试运气，看看能否发现一些东西，结果真的就在Instagram上中大奖了。（Instagram为Facebook旗下的子应用）

对Instagram的测试一开始，我就想到了账户劫持漏洞（Account
Takeover），当然与之相关的应该就是Instagram的忘记密码功能了。所以，我就在Web方式下，用我自己的Instagram账户进行反复的密码重置测试。密码重置请求发出后，Instagram会给账户相应的邮箱返回一条重置链接，这种重置链接貌似进行了全面的安全防范，滴水不漏，我找不到任何破绽。

## 转向移动端深入分析

所以，我就转向了Instagram移动应用端的密码重置机制下，不料我就在这里发现了一个可疑行为。密码重置要求下，当用户输入他的手机号码后，Instagram会向该手机号发送一个6位确认码，在手机端输入该6位确认码之后，密码重置才能成功生效。理论上来说，这种6位数确认码，有10*10*10*10*10*10*的一百万种可能，如果我在手机端都能尝试一遍所有这一百万种的各种可能，那么是不是就能对任意账户实现账户劫持了呢？可以肯定的是，应对这种暴力破解，Instagram后端肯定存在一定的速率限制（Rate
Limiting）。不过，我决定试试看。

至少我的测试验证了Instagram后端的速率限制机制长什么样。在我发送的1000多个请求中，大约有250个左右会被有效通过，其余的750个会被速率限制机制阻挡掉。然后，我又发送了另外一组1000多个请求，这一次，其中有绝大部分被速率限制机制阻挡掉。这样看来，Instagram的验证和速率限制机制还可以。

但有两件事我有点想不通，那就是发出的请求数量和Instagram未对请求执行黑名单化的行为。原因在于，即使我能在短时间内发送有限数量的请求，但我也能连续发送请求而不会被阻挡掉。这就.....是不是有点问题呢？

## 发现突破速率限制（Rate Limiting）的方法

经过几天的连续测试，我发现了可以成功绕过Instagram速率限制机制的方法，那就是：

> Race Hazard（竞态条件）
>
> IP Rotation（IP轮换）

竞争冒险（Race Hazard）：又名竞态条件、竞争条件（Race
Condition），它旨在描述一个系统或者进程的输出依赖于不受控制的事件出现顺序或者出现时机。此词源自于两个信号试着彼此竞争，来影响谁先输出。

举例来说，如果计算机中的两个进程同时试图修改一个共享内存的内容，在没有并发控制的情况下，最后的结果依赖于两个进程的执行顺序与时机。而且如果发生了并发访问冲突，则最后的结果是不正确的。竞争冒险常见于不良设计的电子系统，尤其是逻辑电路。但它们在软件中也比较常见，尤其是有采用多线程技术的软件。

IP轮换（IP
Rotation）：是指在一定时间内，用不同的IP地址去请求同一个服务端接口。通常用代理可实现这种IP地址轮换，这种方式应用于突破网站反爬虫机制对大量数据的抓取。

如果你对竞争冒险（Race Hazard）或竞态条件（Race
Condition）了解较少，请自行百度熟悉。在竞态条件之下，我使用多个IP地址向Instagram后端发送多个密码重置的确认码并发请求，这种情况下，可以绕过Instagram的速率限制机制，不被阻挡。可以发送的请求数量取决于请求的并发性和我们使用的IP地址数量。另外，我还发现，密码重置的确认码会在10分钟之后过期，这就使得此类攻击更加困难，也因此，我们可能需要多达1000个的不同IP地址来执行这种攻击。

后来，我把该漏洞上报给Facebook之后，由于在漏洞报告中没详细说明情况，他们的安全团队起初无法复现漏洞。之后，经过和他们的反复邮件沟通，我又制作了一段概念验证性视频发给他们，最终他们确认了该漏洞的有效性。

## 概念验证性攻击（PoC）

密码重置时向Instagram后端请求确认码：

    
    
    POST /api/v1/users/lookup/ HTTP/1.1
    
    User-Agent: Instagram 92.0.0.11.114 Android (27/8.1.0; 440dpi; 1080×2150; Xiaomi/xiaomi; Redmi Note 6 Pro; tulip; qcom; en_IN; 152830654)
    
    Accept-Language: en-IN, en-US
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    Accept-Encoding: gzip, deflate
    
    Host: i.instagram.com
    
    Connection: keep-alive
    
    q=mobile_number&device_id=android-device-id-here

该POST请求发出后，受害都将会收到一个6位数的密码重置确认码，该确认码的有效期为10分钟。

客户端输入以上确认码后，Instagram后端对该确认码的验证：

    
    
    POST /api/v1/accounts/account_recovery_code_verify/ HTTP/1.1
    
    User-Agent: Instagram 92.0.0.11.114 Android (27/8.1.0; 440dpi; 1080×2150; Xiaomi/xiaomi; Redmi Note 6 Pro; tulip; qcom; en_IN; 152830654)
    
    Accept-Language: en-IN, en-US
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    Accept-Encoding: gzip, deflate
    
    Host: i.instagram.com
    
    Connection: keep-alive
    
    recover_code=123456&device_id=android-device-id-here

基于以上两个POST请求和之前的攻击策略，我们需要使用多个IP地址对该密码重置服务端进行暴力猜解。经测试发现，大概来说，我可以用每个IP地址发送将近2000个的请求，而不被Instagram后端的速率限制阻挡。

在我的实际测试中，我用1000台机器对应的1000个IP地址，并轻松实现了请求并发，发送了将近20万个请求，占100万个总概率的20%。以下是实际测试的PoC视频：

## 总结

真实攻击场景下，攻击者用5000个IP地址就能成功暴力猜解出一个有效的密码重置确认码，以此就能“黑”掉（劫持掉）一个Instagram账户。这么多的IP地址听起来貌似很难实现，但如果用
Amazon 或
Google等云服务就能非常容易地让你拥有如此多的IP地址，执行完一百万个密码重置确认码的暴力猜解，全程的成本花费也仅仅就是150美元。这....。

最终，Facebook安全团队因我那个20万个有效请求发送的POC视频确认了漏洞，并及时修复了该漏洞。而我最后也获得了Facebook官方奖励的$30,000美金。  

![Bounty.jpg](https://image.3001.net/images/20190715/1563202811_5d2c94fb67ed7.jpg!small)***参考来源：[thezerohack](https://thezerohack.com/hack-any-instagram#articlescroll)，clouds编译，转载请注明来自FreeBuf.COM**  

