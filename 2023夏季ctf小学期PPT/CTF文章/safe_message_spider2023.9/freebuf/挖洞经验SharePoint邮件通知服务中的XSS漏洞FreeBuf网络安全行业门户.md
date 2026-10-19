***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![Microsoft-Sharepoint.jpg](https://image.3001.net/images/20190318/1552899516_5c8f5dbcd374b.jpg!small)**

**跨站脚本漏洞（XSS）近年来一直是 OWASP的Top 10
经典攻击方式，能在野外发现XSS漏洞也是相当不错的了，尤其是在一些知名的网络产品中。近期，美国Target安全团队就在一次渗透测试过程中，发现了微软在线服务产品SharePoint的一个XSS独特漏洞，无需任何用户交互行为，就可实现攻击利用，以下是Target团队的分享。**

##  **SharePoint 介绍  
**

SharePoint属于微软 Office
365的旗下产品服务，可以作为企业和团队协作工作平台，它能提供包含Outlook、Excel、Word和其它微软系列产品的在线web接口门户服务（Portal），够无缝连接到用户、团队和企业知识库。利用SharePoint集成的web门户服务，可使得端到端的合作更为容易，实现了个人、团队和信息的整合、组织和搜索。SharePoint的web门户服务可以通过浏览器方式通知用户接收新邮件、Lync通信和Skype消息以及要开会议。

然而，就是SharePoint的这种通知服务，使得恶意攻击者可以利用Target安全团队发现的漏洞，通过发送邮件形式就能向受害者浏览器中注入恶意代码，无需用户交互，自动实现XSS攻击。

##  漏洞发现

在一次对基于SharePoint集成的应用程序渗透测试中，我们偶然发现了该漏洞。在测试某个功能点时，我们用目标测试应用向测试账号发送了一封包含有跨站脚本Payload的通知邮件，不一会儿，测试账号登录的SharePoint会话环境中就会跳出了以下XSS窗口：

![01.jpg](https://image.3001.net/images/20190318/1552899155_5c8f5c5331574.jpg!small)

经过分析，我们发现，这种集成的SharePoint服务架构中，客户端浏览器每隔一分钟就会向以下URL链接发起一次GET请求，去探测新邮件等消息，以便为用户进行实时信息更新。

>
> [https://outlook.office365.com/owa/ev.owa2?ns=PendingRequest&ev=PendingNotificationRequest&UA=0&cid=](https://outlook.office365.com/owa/ev.owa2?ns=PendingRequest&ev=PendingNotificationRequest&UA=0&cid=)[cid]&X-SuiteServiceProxyOrigin=https://[company].sharepoint.com  
>

另外，如果客户端用户有新邮件进来，SharePoint服务器会以JSON数据格式对用户作出通知响应，这种通知响应是集成在用户的SharePoint页面中的。以下为通知响应消息格式：

    
    
    HTTP/1.1 200 OK[TRUNCATED]<script>[{"__type":"NewMailNotificationPayload:#Exchange","id":"NewMailNotification","Sender":"SenderInformation","Subject":"Email Subject","PreviewText":"Preview Text","ItemId":"[itemID]","ConversationId":"[conversationID]","IsClutter":false,"SenderSmtpEmailAddress":"johndoe@example.com","InferenceClassification":"Focused","EventType":"0"}]</script>

其中，PreviewText参数中包含了邮件内容，但却无法有效过滤掉一些如< > / 的危险符号。虽然SharePoint对单引号 ’ 和双引号 ”
都进行了恰当的编码转义，但却未对反引号 ` 进行转义，所以基于此，包含有XSS Payload **<
/script><script>alert(`hello`)</script>**的以下邮件通知消息就可能成功执行：

    
    
    <script>[{"__type":"NewMailNotificationPayload:#Exchange","id":"NewMailNotification","Sender":"SenderInformation","Subject":"Email Subject","PreviewText":"</script><script>alert(`hello`)</script>","ItemId":"[itemID]","ConversationId":"[conversationID]","IsClutter":false,"SenderSmtpEmailAddress":"johndoe@example.com","InferenceClassification":"Focused","EventType":"0"}]</script>

注意，上述XSS Payload闭合了script标签，能成功执行XSS语句：

![02.jpg](https://image.3001.net/images/20190318/1552899342_5c8f5d0e0e902.jpg!small)

##  漏洞利用

该漏洞可在多种场景下被利用，以下是我们创建的一个PoC攻击场景：

1、攻击者通过缩小代码和变换字体颜色的方式，构造了一封看似无害的恶意邮件发送给受害者，注意其中嵌入的恶意代码：

![03.png](https://image.3001.net/images/20190318/1552899375_5c8f5d2f91615.png!small)

2、如果受害者在收到上述邮件时处于SharePoint
服务登录状态，那么，当收到这封邮件后，受害者后台的SharePoint邮件通知服务就会加载Payload，跳出我们伪造的“会话过期需要重新登录（Session
expired，Please log in again）”的提示，如下：

![04.jpg](https://image.3001.net/images/20190318/1552899389_5c8f5d3d84252.jpg!small)

3、最终，受害者点击OK后，XSS Payload会跳转到攻击者托管控制的网站上去，迷惑受害者输入用户名密码进行重新登录，从而窃取用户密钥凭据信息。

![05.jpg](https://image.3001.net/images/20190318/1552899404_5c8f5d4c4e1c2.jpg!small)

对漏洞的成功利用，只需要受害者处于SharePoint登录服务状态，能正常接收邮件，而且，值得注意的是，受害者无需真正去执行打开邮件的操作，仅完全由SharePoint的邮件通知服务来触发Payload即可实现攻击。

##  总结

Target安全团队在漏洞发现后及时向微软进行了上报，并附上了上述PoC验证攻击细节和攻击具体环境要求。不久之后，微软回复称漏洞已经修复，他们在其中调整了某个序列化程序使其能正确合理地编码转义敏感字符，能有效阻止XSS攻击在SharePoint应用通知服务中的再次发生。

***参考来源：[target](https://tech.target.com/2019/03/15/SharePoint-Cross-Site-Scripting.html)，clouds编译，转载请注明来自FreeBuf.COM**

