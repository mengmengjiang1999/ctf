***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  一 前言

 **近日，Microsoft 公告中披露了一则关于 Exchange Server
的任意用户伪造漏洞，天融信阿尔法实验室对此漏洞进行了复现及分析。漏洞复现是在 exchange server 2010 SP2
中进行的，复现过程中，发现原作者给出获取用户 SID 的方法，在 2010 版本中并没有相关操作选项，所以作者给出的 POC
也就无法使用。不过后来在[Github](https://github.com/WyAtu/CVE-2018-8581/)中找到一个 POC。在该 POC
中，使用了一种反向委托的方法来获取用户 SID，并利用这个 POC 成功复现了漏洞。**

##  二 背景介绍

Microsoft ExchangeServer 是个消息与协作系统。Exchange Server
可以被用来构架应用于企业、学校的邮件系统或免费邮件系统。它还是一个协作平台。你可以在此基础上开发工作流，知识管理系统，Web
系统或者是其他消息系统，是一个全面的 Internet 协作应用服务器，适合有各种协作需求的用户使用。

###  2.1 漏洞描述

在 MicrosoftExchange Server 中存在一个特权提升漏洞，该漏洞允许任何经过身份验证的用户冒充 ExchangeServer
上的其他任意用户。漏洞产生的原因是由于在 Exchange Server 中使用 NTLM 身份验证时存在特定缺陷，服务器产生的 NTLM
响应可以反射回攻击者服务器，导致攻击者可以验证任意的 EWS（Exchange Web 服务）请求。

###  2.2 受影响的系统版本

> Exchange Server 2010
>
> Exchange Server 2013
>
> Exchange Server 2016

###  2.3 漏洞编号

CVE-2018-8581

##  三、测试环境

> Windows 2008 R2
>
> Exchange Server 2010 SP2

##  四、漏洞复现

首先进行脚本参数配置。

![1547199490_5c38640267d3a.png!small](https://image.3001.net/images/20190111/1547199490_5c38640267d3a.png!small)

在填好相关参数时，运行脚本。

![image.png](https://image.3001.net/images/20190114/1547437493_5c3c05b52e6b6.png!small)

然后再打开 web 界面执行相关操作。

![1547199589_5c386465be5c1.png!small](https://image.3001.net/images/20190111/1547199589_5c386465be5c1.png!small)

输入目标（Administrator）邮箱后确定。

![1547199615_5c38647f265d1.png!small](https://image.3001.net/images/20190111/1547199615_5c38647f265d1.png!small)

最终就成功代理了目标（Administrator）邮箱。

在代理成功后，可以接收目标邮箱的邮件收取，也可以对其邮件进行查看、删除等操作。

现在用 mailtest2 用户向目标（Administrator）邮箱发送一封邮件。

![1547199652_5c3864a4637f1.png!small](https://image.3001.net/images/20190111/1547199652_5c3864a4637f1.png!small)

![1547199652_5c3864a4a0aa0.png!small](https://image.3001.net/images/20190111/1547199652_5c3864a4a0aa0.png!small)

可以看到，代理用户成功接收到了由 mailtest2 用户向目标（Administrator）邮箱新发来的邮件。

如果想移除委托关系，可以将脚本中的 FLAG 改为 0 后运行。

![1547199660_5c3864ace7a55.png!small](https://image.3001.net/images/20190111/1547199660_5c3864ace7a55.png!small)

![1547199665_5c3864b1e2caf.png!small](https://image.3001.net/images/20190111/1547199665_5c3864b1e2caf.png!small)

Remove 后再查看委托用户的邮箱。

![1547199670_5c3864b6d2485.png!small](https://image.3001.net/images/20190111/1547199670_5c3864b6d2485.png!small)

##  五 漏洞利用流程及原理分析

为了能够让大家在分析漏洞时能够更加流畅，这里先介绍几个概念。

###  1、什么是 SID？

SID 全称为：Security Identifiers，是微软从 Server2000 时代引入的一个概念：安全标识符。在 MicrosoftOS
系统中（Server2000 以上级别）工作组环境下：计算机、组、用户都会有自己的 SID 号，这些信息是存储在用户计算机本地注册表中的。这些 SID
号是根据其对象类型的不同随机生成的，具有一定的命名规则。简单来说，SID 其实就是对象身份的象征。

###  2、什么是 EWS？

EWS 是微软实现的一种客户端和服务器之间的交换信息的协议。Exchange Server
提供了包括从电子邮件、会议安排、团体日程管理、任务管理、文档管理、实时会议和工作流等丰富的协作应用。

###  3、NTLM 认证概念、NTLM 认证流程以及 NTLM 认证消息结构。

3.1 什么是 NTLM 认证？

NTLM 认证简单来说就是一种在不直接提供密码的情况下，客户端间接向服务器证明知道用户的密码，从而达到认证目的的一种方法。

3.2 NTLM 认证流程

![1547199683_5c3864c3b933b.png!small](https://image.3001.net/images/20190111/1547199683_5c3864c3b933b.png!small)

3.2.1 客户端如果试图访问服务器资源，首先会向服务器发送协商消息。在发送的请求中会包含一个以明文表示的用户名。

3.2.2 服务器接收到请求后会生成一个 16byte 的随机数，并返回给客户端。这个随机数被称为 Challenge 或者 Nonce。

3.2.3 客户端在接收到服务器返回的 Challenge 后，会使用当前登录用户的密码哈希值对其加密，生成 Authenticate 认证消息，然后将
Authenticate 发送给服务器。

3.2.4 服务器接收到客户端发送回来的 Authenticate 后，会向
DC（Domain）发送针对客户端的验证请求。该请求主要包含以下三方面的内容：客户端用户名，客户端 Authenticate 和原始的 Challenge。

3.2.5 DC 根据用户名获取该帐号的密码哈希值，对原始的 Challenge 进行加密。如果加密后的 Challenge
和服务器发送的一致，则意味着用户拥有正确的密码，验证通过，否则验证失败。DC 将验证结果发给服务器，并最终反馈给客户端。

3.3 NTLM 认证消息的结构

Negotiate 协商消息、Challenge 挑战消息和 Authenticate 认证消息,
他们的结构很相似：NTLMSSPXXXXXXXXXX。其中 NTLMSSP 表示是 NTLM 验证的请求。但是在实际中，NTLMSSPXXXXXXXXXX
是经过 base64 编码的。

举个例子：

![1547199695_5c3864cfa46e9.png!small](https://image.3001.net/images/20190111/1547199695_5c3864cfa46e9.png!small)

概念介绍完，接下来开始分析漏洞利用流程及原理，通过 POC 来看，漏洞利用执行过程可分为四大步骤。

![1547199702_5c3864d6bf9a3.png!small](https://image.3001.net/images/20190111/1547199702_5c3864d6bf9a3.png!small)

图一：总流程图

##  **第一步：获取用户 SID**

获取用户 SID 的目的是为了后续构造 SOAP 头来冒充用户。

![1547199712_5c3864e080ce6.png!small](https://image.3001.net/images/20190111/1547199712_5c3864e080ce6.png!small)

<t:EmailAddress>是攻击者邮箱地址，这里可以理解成委托方。

<t:PrimarySmtpAddress>是受害者邮箱地址，可以理解成被委托方。

该脚本是通过反向委托的方式来获取目标邮箱用户 SID。通过向服务器发送一个将 CONTROLLED_EMAIL 委托给 TARGET_MAIL
的请求包，服务器就会返回 TARGET_MAIL 用户 SID。

![1547199747_5c3865034539e.png!small](https://image.3001.net/images/20190111/1547199747_5c3865034539e.png!small)

![图片
1.png](https://image.3001.net/images/20190112/15472736719666.png!small)![t2.png](https://image.3001.net/images/20190112/15472736764320.png!small)

上图是代码执行流程，看代码可以发现，这部分有多次 add 和 remove 委托的行为。之所以这样重复请求，是为了防止发生意外错误。

上面说到 Exchange Server 添加委托操作的时候，服务器会返回被委托方（Target）的 SID，但是当添加委托时，返回的数据包中如果包含
ErrorDelegateAlreadyExists 字符时，说明已经存在委托行为。

![图片
3.png](https://image.3001.net/images/20190112/15472737226978.png!small)这时就需要先remove掉委托关系，然后再add，这样才能获取到用户SID。  

**第二步：请求推送订阅**

 **![图片
4.png](https://image.3001.net/images/20190112/1547273818133.png!small)![图片
5.png](https://image.3001.net/images/20190112/15472738182242.png!small)![图片
6.png](https://image.3001.net/images/20190112/15472738181584.png!small)![图片
7.png](https://image.3001.net/images/20190112/15472738189499.png!small)**

推送订阅目的是将 NTLM 响应返回给攻击者服务器。

这部分是漏洞点所在，包括两个漏洞--SSRF 和 NTLM 身份验证缺陷。

SSRF 漏洞：攻击者可以使用一个已认证的邮箱账号发 EWS 发送推送订阅请求。（图中/EWS/Exchange.asmx 是 EWS
请求的地址）。推送订阅时，Exchange 允许用户自己指定 URL，所以攻击者可以将这一 URL 改为自己的服务器地址。上图的
EVIL_HTTPSERVER_URL 就是攻击者自己的服务器。当这个推送订阅请求包发送到服务器时，服务器就会向攻击者指定的 URL 发送请求。

![1547201400_5c386b7838f30.png!small](https://image.3001.net/images/20190111/1547201400_5c386b7838f30.png!small)

其中<t：URL>是 SSRF 的核心，跟踪一下服务器处理流程。

根据请求的 Exchange.asmx 文件以及请求内容，找一下 Exchange Server 的处理函数。

![1547199798_5c3865361add3.png!small](https://image.3001.net/images/20190111/1547199798_5c3865361add3.png!small)

![1547199976_5c3865e829379.png!small](https://image.3001.net/images/20190111/1547199976_5c3865e829379.png!small)

可以看到该类其中有一个关键的数据成员 Url, 下面跟踪一下该成员函数，看看哪里使用了该成员函数。

![1547199982_5c3865ee8d14f.png!small](https://image.3001.net/images/20190111/1547199982_5c3865ee8d14f.png!small)

![1547199999_5c3865ffaf27b.png!small](https://image.3001.net/images/20190111/1547199999_5c3865ffaf27b.png!small)

可以看到该 Url 被保存到 PushSubScription 的 clientUrl 中了。

跟踪发现该变量仅有三处使用。

![1547199996_5c3865fcc837c.png!small](https://image.3001.net/images/20190111/1547199996_5c3865fcc837c.png!small)

主要的一处便是通过 Http 协议进行 Notification 消息发送的过程。

![1547200012_5c38660c4f47a.png!small](https://image.3001.net/images/20190111/1547200012_5c38660c4f47a.png!small)

在这里准备好各种参数之后，通过http协议和指定的URL进行通信。  

![1547200035_5c38662382e15.png!small](https://image.3001.net/images/20190111/1547200035_5c38662382e15.png!small)

NTLM 身份验证缺陷：在发送请求时，Exchange Server 使用的是 CredentialCache.DefaultCredentials
进行连接：

![1547200030_5c38661e2bc5b.png!small](https://image.3001.net/images/20190111/1547200030_5c38661e2bc5b.png!small)

并且 CredentialCache.DefaultCredentials 是以 NT AUTHORITY\SYSTEM 权限运行，这就会导致
Exchange Server 将服务器生成的 NTLM 响应发送到攻击者的服务器。Exchange Server 默认情况下还设置了以下注册表项：

    
    
        HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\DisableLoopbackCheck= 1

![1547200041_5c3866298644e.png!small](https://image.3001.net/images/20190111/1547200041_5c3866298644e.png!small)

这就导致攻击者可以使用返回 NTLM 响应进行 HTTP 身份验证，从而可以验证任意 EWS 请求。

**第三步：构造攻击数据包**

![1547200049_5c3866317726b.png!small](https://image.3001.net/images/20190111/1547200049_5c3866317726b.png!small)

由于 CredentialCache.DefaultCredentials 是以 NT AUTHORITY\SYSTEM 权限运行，所以攻击者可以与
TokenSerializationRight 进行「特权」会话，然后利用 SOAP 头部模拟任何想要伪装的用户。

使用一开始获取到的用户 SID 来构造 SOAP 头冒充受害者用户。

SOAP Body 处构造的是委托请求的包，作用是目标邮箱的 inbox 收件箱将会委托于攻击者，这样就可以查看并修改目标邮箱的邮件。

**第四步：NTLM 认证及攻击**

![1547200053_5c38663598814.png!small](https://image.3001.net/images/20190111/1547200053_5c38663598814.png!small)

![1547200061_5c38663d982e3.png!small](https://image.3001.net/images/20190111/1547200061_5c38663d982e3.png!small)

这里攻击者利用 Python HTTPServer 搭建一个简单的 web 服务器来作为自己的服务器，这个服务器其实是起到一个代理（中转）的作用。因为在
NTLM 认证证程中，它监听并响应着 Exchange Server 订阅功能发来的请求（请求中包含 NTLM 值），同时利用得到的 NTLM 响应值请求
EWS，在这个过程中，它其实充当着就是一种像中间代理人一样的身份。我们可以把这个攻击者服务器称作代理服务器。

下面以 Wireshark 通信流量包来详细分析下 NTLM 的整个认证及攻击流程，大家可对照总流程（图一）的第四步骤来分析。

首先，攻击者在推送订阅后，Exchange Server 的订阅功能会向代理服务器发送 POST 请求。

![1547200068_5c3866443d6a1.png!small](https://image.3001.net/images/20190111/1547200068_5c3866443d6a1.png!small)

然后代理服务器会返回一个包含 WWW-Authenticate：NTLM 的 header 头并返回 401 状态（未认证）。

![1547200077_5c38664d8f7e2.png!small](https://image.3001.net/images/20190111/1547200077_5c38664d8f7e2.png!small)

![1547200083_5c3866533aa57.png!small](https://image.3001.net/images/20190111/1547200083_5c3866533aa57.png!small)

Exchange Server 收到后，就会发送一个 Negotiate 协商消息开始 NTLM 验证。

![1547200093_5c38665d5b797.png!small](https://image.3001.net/images/20190111/1547200093_5c38665d5b797.png!small)

然后代理服务器会用这个 Negotiate 协商消息并带上 relay_body（攻击包）去请求 EWS。

![1547200106_5c38666a82c66.png!small](https://image.3001.net/images/20190111/1547200106_5c38666a82c66.png!small)

![1547200113_5c38667130865.png!small](https://image.3001.net/images/20190111/1547200113_5c38667130865.png!small)

接着，EWS 就会返回 Challenge 挑战消息，然后代理服务器会将这个 Challenge 挑战消息响应回 Exchange Server
的订阅功能。

![1547200119_5c38667738d21.png!small](https://image.3001.net/images/20190111/1547200119_5c38667738d21.png!small)

Exchange Server 的订阅功能接收到后，就会对其加密，返回 Authenticate 认证消息给代理服务器。

![1547200130_5c38668285a0f.png!small](https://image.3001.net/images/20190111/1547200130_5c38668285a0f.png!small)

![1547200147_5c386693d0a0b.png!small](https://image.3001.net/images/20190111/1547200147_5c386693d0a0b.png!small)

然后，代理服务器返回了 401 状态。其实这个返回什么并不重要，因为我们目的是获取 Authenticate 认证消息。

最后代理服务器就会用这个获取到的 Authenticate 认证消息并带上 relay_body（攻击包）去请求 EWS，从而成功验证并完成攻击。

![1547200149_5c386695913fd.png!small](https://image.3001.net/images/20190111/1547200149_5c386695913fd.png!small)

![1547200145_5c38669130232.png!small](https://image.3001.net/images/20190111/1547200145_5c38669130232.png!small)

##  六 修复建议

手工修复：

删除
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\DisableLoopbackCheck
键值

在管理员权限的命令行窗口中，输入如下命令：

reg delete HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa/v
DisableLoopbackCHECK /f

在删除键值后，无需重新启动操作系统，也无需重新启动 Exchange Server。

官方补丁：

Microsoft 在 2018 年 11 月发布了补丁，但该补丁仅对该漏洞进行了缓解，并没有进行严格意义上的修复。不过 Microsoft
发布的公告指出，在此后 Exchange 累计更新中，将不会再默认启动这一注册表项。

##  七 参考链接

<https://www.zerodayinitiative.com/blog/2018/12/19/an-insincere-form-of-flattery-impersonating-users-on-microsoft-exchange>

<https://github.com/WyAtu/CVE-2018-8581/>

[http://blog.51cto.com/popeyeywy/333556](https://github.com/WyAtu/CVE-2018-8581/)

<https://www.cnblogs.com/shuidao/p/3634637.html>

<https://www.cnblogs.com/artech/archive/2011/01/25/NTLM.html>

***本文作者：alphalab，转载请注明来自FreeBuf.COM**

