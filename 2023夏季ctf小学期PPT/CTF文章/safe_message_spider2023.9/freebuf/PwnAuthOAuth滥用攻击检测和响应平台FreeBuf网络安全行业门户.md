## 背景

**鱼叉式网络钓鱼攻击被视为企业最大的网络威胁之一。只需一名员工大意的输入了他的凭据，或运行了一些未知的恶意软件，就可能会使整个企业网络掌控于攻击者，甚至瘫痪。因此，公司往往会选择投入大量的资源，来防止凭证收集和有效载荷驱动的社会工程学攻击。但是对于非传统但同样危险社会工程学方法OAuth滥用，却没有给予足够的重视。在OAuth滥用攻击中，受害者授权第三方应用程序访问其帐户。一旦获得授权，应用程序就可以访问用户的数据，而不需要凭证并绕过可能存在的任何双因素身份验证。**

今天，我发布了[PwnAuth](https://github.com/fireeye/PwnAuth)，这是一个让组织和渗透测试人员能够拥有测试其检测和响应OAuth滥用社会工程活动能力的平台。在发布该工具时，我们希望提高人们对这种威胁的认识，提高安全社区的检测能力，并为防御者提供对策。

转到我们的GitHub开始使用[PwnAuth](https://github.com/fireeye/PwnAuth)。

### OAuth简介

OAuth
2.0被描述为“一种开放协议，允许从Web，移动和桌面应用程序以简单标准的方法进行安全授权......”它已成为亚马逊，谷歌，Facebook和微软等主要互联网公司事实上的协议，以促进授权第三方应用程序访问用户数据。访问Microsoft
OneDrive以便轻松进行文件共享的应用程序，就是一个很好的OAuth利用的示例。

我们以访问OneDrive的应用程序为例，在OAuth授权流程中定义一些角色

 **应用程序或“客户端（Client）”**

请求访问的第三方应用程序。在此情况下，希望访问您的OneDrive文件的应用程序为“客户端（Client）”。

 **API“资源（Resource）”**

“客户”希望访问的目标应用程序。在此种情况下，Microsoft OneDrive API端点为“资源（Resource）”。

 **“资源所有者（Resource Owner）”**

允许访问其部分帐户的人员。在此情况下，是你。

 **授权服务器**

授权服务器提供资源所有者用来同意或拒绝的接口。服务器可以与API资源或不同的组件相同。在此情况下，Microsoft登录门户是“授权服务器”。

 **范围**

范围定义为第三方应用程序请求的访问类型。大多数API资源将定义应用程序可以请求的一组范围。这与Android手机应用程序在安装时请求的权限类似。在此示例中，应用程序可能会请求访问你的OneDrive文件和用户配置文件。

OAuth
2.0提供了几种不同的授权“grant类型”，以更好的满足用户与之交互的不同应用程序。在此我们将对“授权代码”grant类型做进一步的说明，该授权类型由实现OAuth的Web应用程序使用。
以下是授权流程示例：

1.创建一个“同意”链接，通过标识应用程序和请求的作用域的参数，将资源所有者引导至授权服务器。

    
    
    https://login.microsoftonline.com/auth
    ?response_type=code
    &client_id=123456789
    &redirect_uri=https%3A%2F%2Fexample-app.com%2Fcallback
    &scope=mail.read+offline_access

2.资源所有者将收到授权提示，说明应用程序名称和请求的范围。 资源所有者可以选择批准或拒绝此授权请求。

3.一旦选择了同意，授权服务器将使用授权码重定向应用程序。

    
    
    HTTP/1.1 200 OK
    Content-Type: application/json
    Cache-Control: no-store
    Pragma: no-cache
    {
    "access_token":"aMQe28fhjad8fasdf",
    "token_type":"bearer",
    "expires_in":3600,
    "refresh_token":"OWWGE3YmIwOGYzYTlmM2YxNmMDFkNTVk",
    "scope":"mail.read+offline_access"
    }

4.然后应用程序可以使用授权代码并从授权服务器请求访问令牌。访问令牌可以在设定的时间段内使用，从API资源访问用户的数据，而无需资源所有者采取任何进一步的行动。

## OAuth滥用蔓延

OAuth应用程序提供了一个理想的载体，攻击者可以通过它攻击目标并获取电子邮件，联系人和文件等机密数据。攻击者可能会创建恶意应用程序，并使用获取的访问令牌通过API资源检索受害者的帐户数据。访问令牌不需要知道用户的密码，并能轻松的绕过任何双因素认证防护。此外，删除攻击者访问权的唯一方法是显式撤销对OAuth应用程序的访问。为了获得OAuth令牌，攻击者需要利用社会工程学的方法说服受害者点击“同意链接”并批准该应用程序。由于所有受害者交互都位于合法资源提供者（例如Microsoft）拥有的网站上，因此对于未经过专业安全培训的用户来说，往往很难区分OAuth应用程序是否合法。

虽然可能不是此类活动的首例，但在2016年总统选举期间OAuth滥用首先引起了媒体的关注。FireEye在我们的[2017年M-TRENDS报告](https://www.fireeye.com/current-threats/annual-threat-report/mtrends/rpt-m-trends-2017.html)中撰文介绍了APT28滥用OAuth，获取美国政客的电子邮件的情况。从那时起，[FireEye就发现了这种技术正传播到商品上，并试图在Gmail上传播](https://blog.trendmicro.com/trendlabs-security-intelligence/pawn-storm-abuses-open-authentication-advanced-social-engineering-attacks)。

## PwnAuth

PwnAuth是我写的一个Web应用程序框架，这是一个让组织和渗透测试人员能够拥有测试其检测和响应OAuth滥用社会工程活动能力的平台。Web应用程序为渗透测试人员提供了一个易于使用的UI，以管理恶意OAuth应用程序，存储收集的OAuth令牌以及与API资源进行交互。通过创建模块，应用程序用户界面和框架可以很容易地扩展到其他API资源。虽然任何允许OAuth应用程序的云环境都可能成为目标，但是PwnAuth目前使用一个模块来支持恶意Office
365应用程序，这些应用程序将捕获OAuth令牌并使用捕获的令牌与Microsoft Graph API进行交互。Office
365模块本身可以进一步的被扩展，但目前提供以下功能：

> 阅读邮件
>
> 搜索用户的邮箱
>
> 读取用户的联系人
>
> 下载消息和附件
>
> 搜索OneDrive并下载文件
>
> 代表用户发送消息

PwnAuth的界面设计的非常的直观和友好。使用PwnAuth的第一步是创建一个Microsoft应用程序。这些信息必须输入PwnAuth（图1）。

![Fig1.png](https://image.3001.net/images/20180528/15274636255908.png!small)

配置完成后，你可以使用生成的“授权URL”对潜在受害者进行钓鱼。目标用户一旦点击，PwnAuth将捕获其OAuth令牌。受害者列表示例（图2）。

![Fig2.png](https://image.3001.net/images/20180528/15274636401162.png!small)

一旦PwnAuth捕获了受害者的OAuth令牌，你就可以开始访问他们的数据。例如，使用PwnAuth向受害者的邮箱查询包含字符串“password”的所有消息（图3）。

![Fig3.png](https://image.3001.net/images/20180528/15274636557073.png!small)

有关使用的更多信息，请参阅[GitHub wiki](https://github.com/fireeye/PwnAuth/wiki)。

##  **缓解措施**

我们的FireEye技术栈包括基于网络的签名，以检测潜在的恶意OAuth许可URL。攻击者倾向于将某些范围包含在可检测到并标记的恶意应用程序中。有关社会工程学的培训机构，可以将OAuth滥用情况添加到其现有的培训计划中，以便用户更好的了解和保护自己。此外，作为企业可以采取进一步的措施来限制恶意OAuth应用程序的潜在影响，并提高其检测功能。依据API资源，企业可用的选项差异很大，但通常包括：

> 限制第三方应用程序可以请求的API范围。
>
> 在企业中禁用第三方应用具有Cloud App Security的组织可以利用“应用程序权限”功能查询和阻止第三方应用程序。。
>
> 为应用程序实施白名单或黑名单。
>
> 对所有同意的应用程序查询企业的用户。
>
> 记录所有用户同意事件并报告可疑活动。

Office 365特别为管理员提供了一些选项：

> 拥有Cloud App Security的企业可以利用[“应用程序权限”](https://docs.microsoft.com/en-> us/cloud-app-security/manage-app-permissions)功能查询和阻止第三方应用程序。
>
> 管理员可以[阻止对第三方应用程序](https://docs.microsoft.com/en-us/azure/active-> directory/application-access-unexpected-application#i-want-to-disable-all-> future-user-consent-operations-to-any-application)的访问。
>
> 管理员可以采取行动，如果他们认为[恶意应用程序被授予访问帐户的权限](https://docs.microsoft.com/en-> us/azure/active-directory/application-access-unexpected-application)。
>
> 统一审计日志记录用户何时同意第三方应用程序;但是，特定范围和应用程序信息未记录在日志中。

我创建了一组脚本来帮助管理员[在云环境中搜索恶意OAuth应用程序](https://github.com/dmb2168/OAuthHunting)。目前有一个脚本可用于Office
365，后续我计划将添加支持更多的云环境。

## 总结

OAuth滥用攻击是一种危险且非传统的网络钓鱼技术，攻击者可利用这种技术获取组织的机密数据。随着我们将更多服务迁移到云中，企业应小心锁定第三方应用程序访问权限，并确保其监控和检测策略涵盖应用程序许可授予。组织和安全专业人员可以使用PwnAuth来测试他们检测和响应这种新型攻击的能力。

 ***参考来源：[fireeye](https://www.fireeye.com/blog/threat-research/2018/05/shining-a-light-on-oauth-abuse-with-pwnauth.html)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

