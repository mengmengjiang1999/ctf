**通常Microsoft Exchange使用Autodiscover协议配置客户端（如Microsoft
Outlook），但它有一个设计缺陷，可导致web请求泄露至域外。**

研究人员在服务器上配置了多个Autodiscover域名，在2021年4月16日至2021年8月25日期间检测到372072个外泄的Windows域凭据，96671个从各种应用程序泄漏的凭据。

这是一个严重的安全问题，如果攻击者能够控制此类域名，或者能够“嗅探”同一网络中的通信流量，则可以捕获域凭据。

## 漏洞简介

泄漏的凭据是向Microsoft
Exchange服务器进行身份验证的Windows域凭据。此问题由微软的Autodiscover协议引发。Microsoft的Autodiscover协议旨在简化Exchange客户端（如Microsoft
Outlook）配置，使用户能够仅通过用户名和密码来配置客户端，而用户配置的登录到Exchange的凭证基本上都是域凭证，导致此类漏洞影响巨大。

2017年，Shape Security的研究人员发表了一篇关于手机电子邮件客户端此类漏洞的文章（CVE-2016-9940，CVE-2017-2414）。

## Autodiscover

Exchange的Autodiscover为客户提供一种简便配置Exchange客户端的方法。用户必须配置用户名和密码、服务器主机名/IP地址。在某些情况下，还需要其他设置（LDAP设置、WebDAV日历等）。

用户向Outlook添加新的Microsoft Exchange帐户，用户需要输入用户名和密码：

![autodiscover great
leak](https://image.3001.net/images/20210925/1632584488_614f432812707658c68d0.png!small)

用户填写详细信息后，Outlook将尝试使用Autodiscover来配置客户端。

![autodiscover great
leak](https://image.3001.net/images/20210925/1632584489_614f4329ac34caf4fccbf.png!small)

客户端解析用户提供的电子邮件地址amit@example.com，尝试根据电子邮件构建Autodiscover URL：

> https://Autodiscover.example.com/Autodiscover/Autodiscover.xml
>
> http://Autodiscover.example.com/Autodiscover/Autodiscover.xml
>
> https://example.com/Autodiscover/Autodiscover.xml
>
> http://example.com/Autodiscover/Autodiscover.xml

如果这些URL都没有响应，Autodiscover将启动其“back-off”。“back-off”机制正是这次造成漏洞的罪魁祸首，失败后下一次构建的URL将是：http://Autodiscover.com/Autodiscover/Autodiscover.xml，因此拥有Autodiscover.com的人将收到所有请求。

![autodiscover back off microsoft outlook great
leak](https://image.3001.net/images/20210925/1632584491_614f432ba5eb0f442308c.png!small)

## 漏洞复现

研究人员购买了以下域名：

> Autodiscover.com.br–巴西
>
> Autodiscover.com.cn–中国
>
> Autodiscover.com.co–哥伦比亚
>
> Autodiscover.es–西班牙
>
> Autodiscover.fr–法国
>
> Autodiscover.in–印度
>
> Autodiscover.it–意大利
>
> Autodiscover.sg–新加坡
>
> Autodiscover.uk–英国
>
> Autodiscover.xyz
>
> Autodiscover.online

将域名指向web服务器，等待web请求。研究人员收到大量来自不同域、IP地址和客户端的请求。嗅探到的数据中请求了/Autodiscover/Autodiscover.xml的相对路径，头部填充了凭据。

![autodiscovery outlook great
leak](https://image.3001.net/images/20210925/1632584492_614f432cbb5ebff95fd1c.png!small)

通常，web请求不应盲目地进行预身份验证，而应遵循HTTP身份验证过程：

1、客户端请求访问受保护的资源。

2、web服务器请求用户名和密码。

3、客户端向服务器提交用户名和密码。

4、服务器验证用户并返回请求的资源。

![autodiscover microsoft outlook ol switcheroo great
leak](https://image.3001.net/images/20210925/1632584494_614f432e188b629319276.png!small)

从日志中可以看出，hostname是客户端试图通过身份验证的域名，还包括用户名和密码：

> 2021–05–18 03:30:45 W3SVC1 instance-2 10.142.0.4 GET
> /Autodiscover/Autodiscover.xml – 80 – <IP address scrubbed> HTTP/1.1
> Microsoft+Office/16.0+(Windows+NT+10.0;+Microsoft+Outlook+16.0.13901;+Pro) –
> -<Victim domain scrubbed> 404 0 2 1383 301 265 <Victim domain scrubbed>
> Basic+<base64 encoded credentials scrubbed>= – –  
> 2021–05–18 03:30:52 W3SVC1 instance-2 10.142.0.4 GET
> /Autodiscover/Autodiscover.xml – 80 – <IP address scrubbed> HTTP/1.1
> Microsoft+Office/16.0+(Windows+NT+10.0;+Microsoft+Outlook+16.0.13901;+Pro) –
> – <Victim domain scrubbed> 404 0 2 1383 301 296 <Victim domain scrubbed>
> Basic+<base64 encoded credentials scrubbed> – –  
> 2021–05–18 03:30:55 W3SVC1 instance-2 10.142.0.4 GET
> /Autodiscover/Autodiscover.xml – 80 – <IP address scrubbed> HTTP/1.1
> Microsoft+Office/16.0+(Windows+NT+10.0;+Microsoft+Outlook+16.0.13901;+Pro) –
> – <Victim domain scrubbed> 404 0 2 1383 296 328 <Victim domain scrubbed>
> Basic+<base64 encoded credentials scrubbed> – –  
> 2021–05–18 03:31:19 W3SVC1 instance-2 10.142.0.4 GET
> /Autodiscover/Autodiscover.xml – 80 – <IP address scrubbed> HTTP/1.1
> Microsoft+Office/16.0+(Windows+NT+10.0;+Microsoft+Outlook+16.0.13901;+Pro) –
> – <Victim domain scrubbed> 404 0 2 1383 306 234 <Victim domain scrubbed>
> Basic+<base64 encoded credentials scrubbed> – –

在发送身份验证请求之前，客户端并没有检查资源是否可用，服务器上是否存在资源。客户端在收到服务器的HTTP 401响应后成功降级并发送认证信息：

![ol switcheroo
microsoft](https://image.3001.net/images/20210925/1632584495_614f432fd0c9e35b119d3.png!small)

当受害者被重定向到研究人员的服务器时，会弹出一个安全警报：

![microsoft outlook switcheroo great
leak](https://image.3001.net/images/20210925/1632584497_614f4331610729c86586b.png!small)

虽然证书有效，但它是自签名的，但是部署实际的SSL证书，可以轻松避免这种情况。

在2021年4月16日至2021年8月25日期间，研究人员通过这种方式捕获了大量凭据：

![ol switcheroo microsoft
outlook](https://image.3001.net/images/20210925/1632584498_614f433224741a0d2ad96.png!small)

行业分布如下：

![ol switcheroo microsoft outlook great
leak](https://image.3001.net/images/20210925/1632584499_614f4333b19f94da90738.png!small)

## 原文链接

> [guardicore](https://www.guardicore.com/labs/autodiscovering-the-great-> leak/)

