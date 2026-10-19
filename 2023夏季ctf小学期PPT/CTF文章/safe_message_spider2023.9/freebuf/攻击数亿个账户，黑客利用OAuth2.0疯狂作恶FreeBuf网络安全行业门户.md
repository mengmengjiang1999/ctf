## **一、OAuth协议介绍**

OAuth是一种标准授权协议，它允许用户在不需要向第三方网站或应用提供密码的情况下向第三方网站或应用授予对存储于其他网站或应用上的信息的 **委托访问**
权限。OAuth通过访问令牌来实现这一功能。

 **1.发展历史**

OAuth协议始于2006年Twitter公司OpenID项目，该公司的一位合作伙伴希望通过OpenID来实现委派认证，在经过研究后他们发现还没有一项关于API委派访问的开放标准，于是他们在2006年成立了OAuth讨论组，并且在当年的12月就发布了OAuth1.0协议。2010年4月，IETF将OAuth1.0纳入标准协议，编号为rfc5849，2012年OAuth2.0发布。

![v2-d3aea47bc3ec03fc4bf00da309faf55f_720w.webp](https://image.3001.net/images/20230423/1682229368_6444c87868ee42190c96f.png!small)

 **2.OAuth角色**

OAuth协议中定义了4个角色：

  *  **资源所有者**

拥有向受保护资源授权能力的实体，我们可以理解为用户。

  *  **资源服务器**

存储受保护资源的服务器，可以接收带access_token的请求并返回受保护的资源。

  *  **客户端**

代表资源所有者请求受保护资源的应用即第三方的应用。

  *  **授权服务器**

在资源所有者通过认证后向客户端签发access_token的服务器。

![v2-03a31d76b9162e267b807a1eb3a0297b_720w.webp](https://image.3001.net/images/20230423/1682229392_6444c8904b051c953df38.png!small)

 **3.抽象流程**

下面这张图描述了OAuth协议中四个角色的交互过程。

A.客户端向资源所有者请求授权。

B.客户端接收到授权凭证，这里的授权凭证是一个代表资源所有者授权的凭证。

C.客户端与授权服务器交互并提交授权凭证。

D.授权服务器对客户端进行认证并验证授权凭证，如果有效，则颁发访问令牌。E.客户端使用访问令牌向资源服务器请求受保护资源。

F.资源服务器验证访问令牌，如果有效，向客户端返回受保护的资源。![v2-69cdd72d7f27f37d9b4ef1e0ac814f4c_720w.webp](https://image.3001.net/images/20230423/1682229892_6444ca842ac2c1b9b8851.png!small)

 **4.相关概念**

 **授权模式**

授权模式指的是客户端向授权服务器获取访问令牌（Access Token）的方式，RFC6749中定义了四种授权模式及一种拓展机制。

 **授权码模式**

授权码是客户端获取访问令牌的一个临时凭据，授权码模式也是四种授权模式中最安全的一种。在授权码模式中，用户授权后，认证服务器向客户端生成授权码，客户端再利用授权码向认证服务器请求访问令牌。

 **隐式授权模式**

隐式授权是一种简化的授权码模式，在隐式授权模式中，认证服务器没有向客户端签发授权码这一步骤，直接向客户端颁发访问令牌。

 **密码授权模式**

密码模式主要应用于高度可信的客户端中，用户需要向客户端提供自己的用户名和密码，客户端再利用用户名和密码向认证服务器请求访问令牌。

 **客户端凭据**

客户端凭据的主要应用场景是其访问的资源为相对固定的受保护资源，客户端仅代表自身去向资源服务器请求资源。

 **访问令牌**

访问令牌是用于访问受保护资源的凭据，访问令牌一般都会包含用户身份、访问范围、有效时间等信息。

 **刷新令牌**

刷新令牌是用于获取访问令牌的凭据，主要是在访问令牌过期后用来向认证服务器请求新的访问令牌。

 **5.OAuth客户端**

客户端也是OAuth协议中非常重要的一个概念，客户端代表第三方应用身份，在OAuth协议中规定客户端需要向认证服务器进行注册，协议没有规定注册的具体方法，但是规定了客户端需要提供的一些参数。

  *  **客户端标识符(client_id)，** 每个客户端都应该有一个唯一标识符，用于识别该客户端并与其他客户端区分开来。
  *  **客户端密钥（client_secret），** 每个客户端还应该有一个密钥，用于与 OAuth 服务端进行身份验证和通信。
  *  **授权类型（grant_type），** 客户端应该指定它所使用的授权类型，例如授权码、隐式授权、密码授权或客户端凭证授权。
  *  **回调URL（redirect_uri），** 客户端应该指定一个回调 URL，OAuth 服务端将在用户授权后将授权码或令牌发送到该 URL。
  *  **可接受的响应类型（response_type），** 客户端应该指定它所接受的响应类型，例如 code、token或其他拓展响应类型。
  *  **可接受的范围（scope），** 客户端应该指定它所接受的范围，即客户端所请求的访问权限。
  *  **其他元数据，** 客户端还可以指定其他元数据，例如客户端名称、描述、图标等。

 **6.授权码模式**

授权码模式是应用最多的OAuth授权模式，下图描述了授权码模式中各个角色之间的交互流程。

A.客户端通过指示资源所有者的用户代理到授权端点。客户端包括它的客户端标识符、请求的范围、本地状态和授权服务器将向其发送的重定向
URI一旦授予（或拒绝）访问权限，用户代理就会返回。

B.授权服务器验证资源所有者（通过用户代理）并确定资源所有者是否授予或拒绝客户端的访问请求。

C.如果资源所有者授予访问权限，则授权服务器使用之前提供的重定向 URI。

D.客户端利用上一步接收到的授权码向认证服务器请求访问令牌，并且客户端需要向认证服务器进行身份验证。

E.认证服务器验证客户端，验证授权代码，并确保重定向 URI接收到的与用于重定向客户端的 URI 相匹配。如果验证通过，授权服务器响应访问令牌和刷新令牌。

  

![v2-ba230446e4fab37862b5b16b9e8be7a6_720w.webp](https://image.3001.net/images/20230423/1682229913_6444ca99a76096be66333.png!small)

##  **二、OAuth攻击面**

身份基础设施的底层均绕不开身份认证协议这一关键技术，但是在OAuth协议实际应用中也暴露了许多安全风险，主要包括以下几个攻击面。

1. **认证绕过**

第三方应用登录是OAuth的一个典型应用案例，但是如果使用了错误的实现方式就会造成认证绕过的后果。以下是某个应用的第三方登录实现逻辑。

首先APP通过OAuth拿到用户的OpenId，拿到OpenId之后APP再调用登录接口并以OpenID为参数，服务端在数据库中查询到OpenId对应的用户随即返回该用户的session。

整个过程中应用仅仅使用了OpenId作为鉴权的参数，但是由于OpenId是一个相对固定的参数，一旦泄露出去，这里就会产生认证绕过的风险。

![v2-027f30f5f799a59ccd2aa7f092c376b8_720w.webp](https://image.3001.net/images/20230423/1682229923_6444caa3c72d16263a232.png!small)

2. **开放重定向**

开放重定向是只攻击者可以通过控制请求参数使用户重定向到任意地址的攻击，在OAuth中导致开放重定向的罪魁祸首是对redirect_uri参数没有经过校验，由于认证服务器会通过重定向将用户授权凭据传递给客户端，攻击者通常会利用这种攻击手法来窃取用户授权凭据。

![v2-049f8a451dd37005190e0739410c7ea2_720w.webp](https://image.3001.net/images/20230423/1682229932_6444caacb8b9e9941e270.png!small)

 **3.SSRF**

导致SSRF的一个重要原因是OAuth客户端的注册过程，OAuth客户端注册通常会向认证服务器提供一些包含客户端信息的元数据，其中一些参数以url的形式提供给认证服务器，包括重定向地址、log地址、jwks等，如果服务器在服务端对这些地址发起web请求，这里就会出现SSRF漏洞。

![v2-f0a04bed0c945518c7fbede6a24b9066_720w.webp](https://image.3001.net/images/20230423/1682229944_6444cab8ba6161d984ff6.png!small)

 **4.参数注入**

参数注入主要包括SQL注入和XSS，OAuth协议交互和客户端注册中涉及到多种参数传递过程，如果在服务端没有进行恰当的过滤和验证，很有可能就会出现参数注入漏洞，比如在一些OAuth实现中直接将客户端注册填写的redirect_url渲染到html页面，或者是将code参数直接用字符串拼接的方式带入到SQL查询语句中，这些不安全的实现都会导致意外的事故。

 **5.会话投毒**

会话投毒攻击一般出现在授权访问的过程中，主流的OAuth服务实现一般有以下几个流程：

1.客户端校验，对传递过来的客户端参数包括client_id、redirect_uri、scpoe等参数进行合法性校验。

2.用户认证，认证服务器向资源所有者进行身份验证，主要是利用表单等方式对用户身份进行验证。

3.向用户询问是或否授权，在这个步骤中会向用户展示客户端信息及授权范围，并向用户展示授权按钮。

4.将用户授权凭据通过重定向传递给第三方客户端。

以上几个步骤中客户端校验、用户认证、授权逻辑通常都是在三个接口中独立实现，三个接口需要维持的一些状态参数会存储到session中。

比如在第一步客户端校验通过后将redirect_uri存储在session中，在通过验证后并授权之后再从session中取出redirect_uri并将用户重定向到这个地址。

在这个过程中，如果攻击者在自己的页面制作一个合法的客户端授权请求、但是在后台偷偷发送自己注册的恶意客户端授权请求，session里面的内容就会被刷新，用户再授权之后就会将授权凭据重定向到攻击者的客户端地址。

  

##  **三、OAuth攻击案例**

针对OAuth的攻击案例在现实中也是层出不穷，以下是一些漏洞和攻击的典型案例。

  

 **1.CVE-2021-26715**

CVE-2021-26715是OAuth的开源实现MITREid
Connect中存在的一个SSRF漏洞、该漏洞的主要原因是其在服务端通过http请求客户端logo地址展示给用户。

首先注册客户端，向客户端传递一个恶意的logo地址

![v2-941160bb60bfde1dc012ee30cdea550c_720w.webp](https://image.3001.net/images/20230423/1682229960_6444cac84d5b39deb3a55.png!small)

再通过接口获取客户端logo

![v2-52ce478f8710a23c9bed1ae5b744cfdd_720w.webp](https://image.3001.net/images/20230423/1682229972_6444cad4d663fd8da15a6.png!small)

接收到的是恶意地址的内容。根据api地址定位到相关代码内容

![v2-04058c7ea6f617d9f3daccb1f0f40462_720w.webp](https://image.3001.net/images/20230423/1682229982_6444cade23c92749800e6.png!small)

api对应的方法是

org.mitre.openid.connect.web.ClientAPI#getClientLogo

getClientLogo方法中通过

InMemoryClientLogoLoadingService#getLogo

方法，传入客户端实体类获取客户端logo图像

![v2-a26d5d7dec26b2ae7699ea48b4702dc7_720w.webp](https://image.3001.net/images/20230423/1682229989_6444cae592792c4ad534b.png!small)

最终在

org.mitre.openid.connect.service.impl.InMemoryClientLogoLoadingService类中可以看到构造http请求向logo地址发起的http请求。

  

 **2.redirect_uri**

这是一个通过redirect_uri地址绕过防护进行开放重定向攻击的案例，白帽黑客kuzu7shiki在hackerone上披露的一份报告显示，kuzu7shiki发现了pixiv提供的OAuth服务中的一个漏洞，正常的OAuth认证参数构造如下：

[https://oauth.secure.pixiv.net/v2/auth/authorize?client_id=a1Z7w6JssUQkw5Hid0uIDeuesue9&redirect_uri=https%3A%2F%2Fbooth.pm%2Fusers%2Fauth%2Fpixiv%2Fcallback&response_type=code&scope=read-works+read-favorite-users+read-friends+read-profile+read-email+write-profile&state=%3A1a38b53563599621ce25094661b1c4458ddb52d79d771149](https://link.zhihu.com/?target=https%3A//oauth.secure.pixiv.net/v2/auth/authorize%3Fclient_id%3Da1Z7w6JssUQkw5Hid0uIDeuesue9%26redirect_uri%3Dhttps%253A%252F%252Fbooth.pm%252Fusers%252Fauth%252Fpixiv%252Fcallback%26response_type%3Dcode%26scope%3Dread-works%2Bread-favorite-users%2Bread-friends%2Bread-profile%2Bread-email%2Bwrite-profile%26state%3D%253A1a38b53563599621ce25094661b1c4458ddb52d79d771149)

kuzu7shiki将redirect_uri改成以下这种形式：

redirect_uri=https%3A%2F%2Fbooth.pm%2Fusers%2Fauth%2Fpixiv%2Fcallback/../../../../ja/items/4503924

在用户授权后认证服务器将用户重定向到地址：

https%3A%2F%2Fbooth.pm/ja/items/4503924

booth.pm是一个购物平台、items/4503924为商品详情页面，这个页面的内容是商家可以控制的，这个漏洞的关键点在于pixiv没有对重定向地址进行严格校验，如果攻击者注册一个商家账户并在商品页面植入类似Google
Analytics的访问统计插件，用户在授权之后，授权凭据就会暴露在攻击者的统计数据中。

  

 **3.OAuth钓鱼**

这是国外安全公司fortra发布的一篇关于利用OAuth钓鱼对Office365应用进行钓鱼的攻击案例。

Office365可以理解为一个在线版的office应用，主要包含文档、表格、邮件等功能，并且其API支持OAuth委托认证。攻击者钓鱼的主要手法是向用户发送一个假冒的内部文档。

![v2-541ea3e06162b9cd0e5aad793a85e4eb_720w.webp](https://image.3001.net/images/20230423/1682230001_6444caf107c3bc3d30509.png!small)

实际上链接是

httpps://[http://login.microsoftonline.com/common/oauth2/v2.0/authorize?%20client_id=fc5d3843-d0e8-4c3f-b0ee-6d407f667751&response_type=id_token+code&redirect_uri=https%3A%2F%2Fofficemtr.com%3A8081%2Foffice&scope=offline_access%20contacts.read%20user.read%20mail.read%20notes.read.all%20mailboxsettings.readwrite%20Files.ReadWrite.All%20openid%20profile&state=12345Ajtwmd&response_mode=%20form_post&nonce=YWxsYWh1IGFrYmFy](https://link.zhihu.com/?target=http%3A//login.microsoftonline.com/common/oauth2/v2.0/authorize%3F%2520client_id%3Dfc5d3843-d0e8-4c3f-b0ee-6d407f667751%26response_type%3Did_token%2Bcode%26redirect_uri%3Dhttps%253A%252F%252Fofficemtr.com%253A8081%252Foffice%26scope%3Doffline_access%2520contacts.read%2520user.read%2520mail.read%2520notes.read.all%2520mailboxsettings.readwrite%2520Files.ReadWrite.All%2520openid%2520profile%26state%3D12345Ajtwmd%26response_mode%3D%2520form_post%26nonce%3DYWxsYWh1IGFrYmFy)

这里可以很明显看出来是一个OAuth认证链接，受害者在点击该链接后会跳出登录界面

![v2-c45bbe6b96b66f5f02da2549476a54dc_720w.webp](https://image.3001.net/images/20230423/1682230011_6444cafb16c5296b9840e.png!small)

受害者输入用户密码后进行授权

![v2-400e1dfe5882c71c0091ba419bde9300_720w.webp](https://image.3001.net/images/20230423/1682230047_6444cb1fa8e2f3568d975.png!small)

一旦用户点击授权，用户凭据将会被发送到攻击者的恶意客户端地址，并且攻击者拥有授权范围的所有能力，包括读取联系人、操作邮件、文档等等。

  

 **4.o365-attack-toolkit**

o365-attack-toolkit是github上一个针对office365进行攻击的开源工具，这个工具主要也是利用了Office365服务api支持OAuth认证的特性。

![v2-d732caea1f7becfb13ff50945e5e29bb_720w.webp](https://image.3001.net/images/20230423/1682230035_6444cb1305aaae9417276.png!small)

工具主要包含了钓鱼页面、后端服务、以及管理接口三个部分，钓鱼页面负责对受害者进行钓鱼攻击，后端服务利用Microsoft Graph
API请求用户存储在office365服务中的数据，管理界面为攻击者提供用户及资产的可视化管理的功能。以下是这款工具的一些主要功能界面：

 **①用户管理**

![v2-dcc52ac41153a13e076402e06a310fce_720w.webp](https://image.3001.net/images/20230423/1682230076_6444cb3c7fc574ff60742.png!small)

 **②邮件搜索**

![v2-ff1ed2773aee2cc55ee7e33b1a7035da_720w.webp](https://image.3001.net/images/20230423/1682230089_6444cb497d3121f3c5c5c.png!small)

 **③文件搜索**

![v2-1143d3165e4b9319da9bb2b407af010c_720w.webp](https://image.3001.net/images/20230423/1682230123_6444cb6b54d82607aca54.png!small)

