**Microsoft Exchange 的自动发现功能实施中的缺陷已经泄露了全球大约100,000个 Windows域的登录名和密码。**

在 Guardicore的安全研究副总裁Amit Serper的一份新报告中，研究人员揭示了自动发现协议的错误实施(而不是Microsoft
Exchange中的错误)如何导致Windows证书被发送到第三方不受信任的网站。

在讨论问题之前，先来快速了解一下Microsoft Exchange的自动发现协议以及它是如何实现的。

## 什么是 Microsoft Exchange 自动发现

Microsoft Exchange使用自动发现功能自动配置用户的邮件客户端(如Microsoft Outlook)及其组织的预定义邮件设置。

当Exchange用户在电子邮件客户端(如Microsoft
Outlook)中输入他们的电子邮件地址和密码时，邮件客户端将尝试对各种Exchange自动发现url进行身份验证。

在此认证过程中，登录名和密码会自动发送到“自动发现URL”。

![](https://image.3001.net/images/20210924/1632466503_614d76476b4d73f7f8c8e.png!small)  

将连接到的自动发现url来自客户端中配置的电子邮件地址。

例如，当Serper使用电子邮件“amit@example.com”测试自动发现功能时，他发现邮件客户端试图验证以下自动发现url:

https://Autodiscover.example.com/Autodiscover/Autodiscover.xml

http://Autodiscover.example.com/Autodiscover/Autodiscover.xml

https://example.com/Autodiscover/Autodiscover.xml

http://example.com/Autodiscover/Autodiscover.xml

邮件客户端将尝试每个 URL，直到它成功通过 Microsoft Exchange 服务器的身份验证并将配置信息发送回客户端。

## 将凭据泄漏到外部域

如果客户端无法对上述 URL 进行身份验证，Serper 发现某些邮件客户端(包括 Microsoft
Outlook)将执行“后退”程序。此过程尝试创建其他URL以进行身份验证，例如 autodiscover.[tld] 域，其中 TLD
来自用户的电子邮件地址。

在本例中，生成的URL是http://Autodiscover.com/Autodiscover/Autodiscover.xml。

自动发现协议的这种错误实现导致邮件客户端向不受信任的域(例如 autodiscover.com)进行身份验证，这就是问题的开始。

由于电子邮件用户所在的组织不拥有此域，并且凭据会自动发送到URL，因此域所有者可以收集发送给他们的任何凭据。

为了对此进行测试，Guardicore 注册了以下域并在每个域上设置了 Web 服务器，以查看 Microsoft Exchange
自动发现功能会泄露多少凭据。

> Autodiscover.com.br - 巴西
>
> Autodiscover.com.cn - 中国
>
> Autodiscover.com.co - 哥伦比亚
>
> Autodiscover.es - 西班牙
>
> Autodiscover.fr - 法国
>
> Autodiscover.in - 印度
>
> Autodiscover.it - 意大利
>
> Autodiscover.sg - 新加坡
>
> Autodiscover.uk - 英国
>
> 自动发现.xyz
>
> Autodiscover.online

注册并使用这些域后，Serper发现电子邮件客户端(包括 Microsoft Outlook)使用基本身份验证发送了许多帐户凭据，从而使它们易于查看。

![](https://image.3001.net/images/20210924/1632466468_614d7624ccf871e30ddcb.png!small)  

对于使用NTLM和Oauth发送凭据的Microsoft Outlook客户端，Serper创建了一种称为“The ol'
switcheroo”的攻击，强制客户端将请求降级为基本身份验证请求。

这将再次允许研究人员访问用户的明文密码。

![](https://image.3001.net/images/20210924/1632466455_614d76176d6fa2571f8a9.png!small)  

在2021年4月20日至2021年8月25日期间进行这些测试时，Guardicore服务器收到:

> 648,976 个针对其自动发现域的 HTTP 请求。
>
> 372,072 个基本身份验证请求。
>
> 96,671 个唯一预认证请求。

Guardicore 表示，发送其凭据的域包括：

> 在中国市场上市的公司
>
> 食品制造商
>
> 投资银行
>
> 发电厂
>
> 电力输送
>
> 房地产
>
> 航运和物流
>
> 时装和珠宝

## 缓解Microsoft Exchange自动发现泄露

根据Serper建议，企业和开发人员可以使用这些建议来缓解这些Microsoft Exchange 自动发现泄露。

对于使用 Microsoft Exchange 的组织，应尽可能阻止所有自动发现。建议禁用基本身份验证，因为它实际上是以明文形式发送凭证。

对于软件开发人员，Serper 建议用户在构建自动发现URL时防止他们的邮件客户端向上出错，这样他们就不会连接到Autodiscover.[tld]域。

微软发言人表示，目前正在积极采取措施保护使用者，并致力于漏洞披露问题以降低客户不必要的风险。

Serper表示，许多开发人员只是使用都存在相同问题的第三方库，在使用是并未关注是否存在安全风险。当前软件开发离不开第三方库的使用，但其中的风险问题却一直存在。

当应用程序中的第三代码方库存在安全漏洞时，对企业来说后果可能很严重。首先，违规风险可能会更高，其次是增加了补丁的复杂性。漏洞时间越长修补就越复杂，打补丁所需的时间就越长，破坏应用程序的风险也就越大。

对于既是直接依赖又是传递依赖的库，修补可能需要长达 2.5
倍的时间。这同样适用于复杂的漏洞，例如任意代码执行缺陷，与典型问题相比，修复这些漏洞可能需要两倍的时间。远程代码执行和拒绝服务错误也需要更长的时间来解决。

为了提高网络抵御风险能力，在软件开发期间不断通过静态代码检测时时发现缺陷并修复，可以降低安全漏洞，大大提高软件安全性。在网络世界危机四伏的今天，
**[静态代码安全检测](https://www.woocoom.com/b031.html)**
已成为继防火墙、杀毒软件和入侵检测后，网络安全防护的又一有效手段。

  

> 参读链接：
>
> https://www.woocoom.com/b021.html?id=03ee6a92b2014900bc975252550378a1
>
> https://www.bleepingcomputer.com/news/microsoft/microsoft-exchange-> autodiscover-bugs-leak-100k-windows-credentials/

