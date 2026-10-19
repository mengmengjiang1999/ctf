**近期，来自网络安全公司Citadelo的安全研究专家在VMware Cloud
Director平台中发现了一个新型的高危漏洞，该漏洞的CVE编号为[CVE-2020-3956](https://www.vmware.com/security/advisories/VMSA-2020-0010.html)。攻击者一旦成功利用该漏洞，那么将允许他们接管并滥用目标组织的网络服务器以及基础设施。**

##
![](https://image.3001.net/images/20200604/1591238198_5ed85e3645d92.jpg!small)关于VMware
Cloud Director

VMware Cloud Director
是一款领先的云计算服务交付平台，一些全球受欢迎的云服务提供商利用它成功地运维和管理云计算服务业务。云服务提供商使用 VMware Cloud
Director 向全球数以千计的企业和 IT 团队安全、高效地交付弹性云计算资源。

根据研究人员透露的信息，这个漏洞将有可能允许经过身份验证的攻击者访问目标企业的公司网络，获取敏感数据，并进一步控制目标组织整个基础架构中的私有云。

根据VMware发布的安全公告，由于VMware Cloud
Director没有正确地处理用户的输入数据，导致程序中出现了一个代码注入漏洞，该代码注入漏洞得相关信息目前已上报给VMware的安全团队，广大用户可以使用漏洞修复程序或安全解决方案来修复或解决受影响VMware产品中的这个漏洞。

CVE-2020-3956漏洞是一个代码注入漏洞，由于VMware Cloud Director没有正确地处理用户的输入数据，因此攻击者能够通过向Cloud
Director发送恶意数据来触发并利用该漏洞实施攻击。该漏洞在CVSS v.3漏洞严重性等级中的评分为8.8分（满分为10分）。

研究人员表示，攻击者可以通过基于HTML5或Flex的UI接口、API Explorer接口和API来访问和利用该漏洞。

![](https://image.3001.net/images/20200604/1591238221_5ed85e4de4845.jpg!small)经研究发现，当攻击者经过了身份验证之后，将能够向Cloud
Director发送恶意数据，并实现任意远程代码执行。此漏洞将影响10.0.0.2之前的10.0.x版本、9.7.0.5之前的9.7.0.x版本、9.5.0.6之前的9.5.0.x版本和9.1.0.4之前的9.1.0.x版本。

研究人员在一篇博客文章中解释，攻击者能够通过操作一个简单的表单提交来获得对目标VMware Cloud
Director中任意一台虚拟机（VM）的控制和访问权限。跟其他漏洞一样，所有的一切都是从一个简单的异常错误开始的，当我们在vCloud
Director中输入${7*7}作为SMTP服务器的主机名时，我们将收到以下错误消息：String value has an invalid
format, value: [49]。而这条错误信息也暗示了某种形式的表达式语言注入，因为我们将能够在服务器端执行简单的计算函数。

通过安全研究人员的进一步分析，他们发现攻击者甚至还可以利用这个漏洞来访问任意的Java类。

比如java.io.BufferedReader等等，并通过向这些类传递恶意Payload来对它们进行实例化。

###  Citadelo的安全研究专家在成功触发该漏洞之后，将能够执行以下操作：

> 1、 查看内部系统数据库的内容，包括分配给此基础结构的任何客户的密码哈希。
>
> 2、 修改系统数据库以窃取分配给Cloud Director中不同组织的外部虚拟机（VM）。
>
> 3、 将权限从“组织管理员”（通常是客户帐户）升级到“系统管理员”（具有访问所有云帐户（组织）的权限），因为攻击者可以更改此帐户的哈希值。
>
> 4、 将登录页面修改为Cloud Director，这允许攻击者以明文形式捕获另一个客户的密码，包括系统管理员帐户。
>
> 5、 阅读与客户相关的其他敏感数据，如全名、电子邮件地址或IP地址。

Citadelo的安全研究人员目前已经将漏洞信息私下报告给了VMware，VMware也已经发布9.1.0.4、9.5.0.6、9.7.0.5和10.0.0.2版本并修复了该漏洞。

##  其他资源

>
> 漏洞PoC代码：【[点我获取](https://github.com/aaronsvk/CVE-2020-3956/blob/master/exploit.py)】
>
> VMware官方解决方案：【[点我访问](https://kb.vmware.com/s/article/79091)】

 ***
参考来源：[securityaffairs](https://securityaffairs.co/wordpress/104157/hacking/vmware-cloud-director-flaw.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

