## 一、 **OWASP介绍**

 **OWASP被视为Web应用安全领域的权威参考**
，在2009年发布的美国国家和国际立法、标准、准则、委员会和行业实务守则参考引用了OWASP。美国联邦贸易委员会(FTC)强烈建议所有企业需遵循OWASP十大WEB弱点防护守则。国际信用卡数据安全技术PCI标准更将其列为必要组件。OWASP组织为英国GovCERTUK提供SQL注入参考和为欧洲网络与信息安全局（ENISA),
云计算风险评估参考。OWASP TOP 10为IBM APPSCAN、HP WEBINSPECT等扫描器漏洞参考的主要标准。

作为一个501c3非盈利的全球性安全组织，致力于应用软件的安全研究。使命是使应用软件更加安全，使企业和组织能够对应用安全风险做出更清晰的决策。
**目前OWASP全球拥有130个分会近万名会员，共同推动了安全标准、安全测试工具、安全指导手册等应用安全技术的发展。**

##  **二、OWASP TOP10**

### 1、版本

版本

|

OWASP TOP 10 2013

|

OWASP TOP 10 2017

|

OWASP TOP 10 2021  
  
---|---|---|---  
  
A1

|

Injection 注入攻击

|

Injection 注入攻击

|

Broken Access Control

失效的访问控制  
  
A2

|

Broken Authentication and Session Management

失效的验证与连接管理

|

Broken Authentication

失效的身份认证

|

Sensitive Data Exposure

敏感数据泄露  
  
A3

|

Cross-Site Scripting，XSS

跨站脚本攻击

|

Sensitive Data Exposure

敏感数据泄露

|

Injection 注入攻击  
  
A4

|

Insecure Direct Object References

不安全的直接对象引用

|

XML External Entities，XXE

XML外部处理器漏洞

|

Insecure Design

不安全设计  
  
A5

|

Security Misconfiguration

安全配置错误

|

Broken Access Control

失效的访问控制

|

Security Misconfiguration

安全配置错误  
  
A6

|

Sensitive Data Exposure

敏感数据泄露

|

Security Misconfiguration

安全配置错误

|

Vulnerable and Outdated Component 脆弱过时组件  
  
A7

|

Missiojn Function Level Access Control

缺少功能级别的访问控制

|

Cross-Site Scripting，XSS

跨站脚本攻击

|

Identification and Authentication Failure 识别与认证失败  
  
A8

|

Cross-Site Request Forgery (CSRF)

跨站请求伪造

|

Insecure Deserialization

不安全的反序列化漏洞

|

Software and Data Integrity Failure 软件和数据完整性故障  
  
A9

|

Using Components with Known Vulnerabilities 使用含有已知漏洞的组件

|

Using Components with Known Vulnerabilities 使用含有已知漏洞的组件

|

Security Logging and Monitoring Failure

安全日志与监测失败  
  
A10

|

Unvalidated Redirects and Forwards

未验证的重定向与转发

|

Insufficient Logging & Monitoring

不足的记录和监控漏洞

|

Server-Side Request Forgery

服务器端请求伪造  
  
### 2、漏洞描述

 **A1：2017-注入**

将不受信任的数据作为命令或查询的一部分发送到解析器时，会产生诸如SQL注入、NoSQL注入、OS注入和LDAP注入的注入缺陷。攻击者的恶意数据可以诱使解析器在没有适当授权的情况下执行非预期命令或访问数据。

 **A2：2017-失效的身份认证**

通常，通过错误使用应用程序的身份认证和会话管理功能，攻击者能够破译密码、密钥或会话令牌，或者利用其它开发缺陷来暂时性或永久性冒充其他用户的身份。

 **A3：2017-敏感数据泄露**

许多Web应用程序没有正确保护敏感数据，如信用卡，税务ID和身份验证凭据。攻击者可能会窃取或篡改这些弱保护的数据以进行信用卡诈骗、身份窃取，或其他犯罪。

 **A4：2017-XML外部处理器漏洞**

许多较早的或配置错误的XML处理器评估了XML文件中的外部实体引用。攻击者可以利用外部实体窃取使用URI文件处理器的内部文件和共享文件、监听内部扫描端口、执行远程代码和实施拒绝服务攻击。

 **A5：2017-失效的访问控制**

未对通过身份验证的用户实施恰当的访问控制。攻击者可以利用这些缺陷访问未经授权的功能或数据，例如：访问其他用户的帐户、查看敏感文件、修改其他用户的数据、更改访问权限等。

 **A6：2017-安全配置错误**

安全配置错误是最常见的问题。这通常是由不安全的默认配置，不完整或ad hoc配置，开放云存储，错误配置的HTTP标头，以及包含敏感信息的详细错误信息造成的。

 **A7：2017-跨站脚本攻击**

当应用程序的新网页中包含不受信任的、未经恰当验证或转义的数据时，或者使用可以创建HTML或JavaScript 的浏览器API
更新现有的网页时，就会出现XSS 缺陷。XSS 让攻击者能够在受害者的浏览器中执行脚本，并劫持用户会话、破坏网站或将用户重定向到恶意站点。

 **A8：2017-不安全的反序列化漏洞**

此漏洞通常会导致远程代码执行问题。即使反序列化错误不会导致远程代码执行，也可以被用来执行攻击，包括重放攻击、注入攻击以及权限提升攻击等。

 **A9：2017-使用含有已知漏洞的组件**

组件（如库、框架和其他软件模块）是以与应用程序相同的权限运行的。如果存在漏洞的组件被利用，这种攻击可能会导致严重的数据丢失或服务器接管危机。使用已知漏洞组件的应用程序和API可能会破坏应用程序的防御系统，从而启动各种形式的攻击，造成更为严重的影响。

 **A10：2017-不足的日志记录和监控漏洞**

不足的记录和监控漏洞，再加上事件响应能力欠缺以及缺少有效的整合，使得攻击者可以进一步攻击系统，维持其持久性，转而攻击更多的系统，并篡改、提取或销毁数据。

##  **三、OWASP CRS规则**

### 1、OWASP CRS规则文件结构

  * 90X文件：排除误报

  * 91X文件：检测恶意客户端规则

  * 92X文件：检测违反协议的规则

  * 93X和94X文件：检测运行程序攻击（SQL）或者命令执行攻击规则

  * 95X文件：检测出站数据泄露规则

  * .data文件：规则使用的数据文件

### 2、CRS规则检测攻击行为处理阶段

 **(1) Phase Request Headers 请求头阶段**

Apache完成读取请求头（post-read-request阶段）后立即处理此阶段中的规则。在这个时候还没有读取请求体，所以这个时候对所有请求参数并不是都可用。如果需要提前运行规则（在Apache对请求执行某些操作之前），在请求体读取之前执行某些操作，您需确定是否应该缓存请求体，或者决定如何将规则置于此阶段（例如，是否将其解析为XML）。

 **(2) Phase Request Body 请求体阶段**

请求体阶段是通用的输入分析阶段，大多数面向应用程序的规则都放在这里。在这个阶段是可以收到所有的请求参数，当然这个前提是请求主体是已经读取的。在此阶段ModSecurity支持请求正文阶段的三种编码类型：

application/x-www-form-urlencoded 用于传输表单数据

multipart/form-data 用于文件上传

text/xml 用于传递XML数据

大多数Web应用程序不使用其他编码。

 **(3) Phase Response Headers 响应头阶段**

此阶段发生在响应头被发送回客户端之前。如果要在此之前检查响应，以及是否要使用响应头来决定是否要缓存响应体，可以讲将规则配置为此阶段。需要注意的是，某些响应状态码（例如404）由于在Apache请求周期的早期处理，因此此类访问是无法触发ModSecurity的规则。此外，还有一些响应头由Apache在稍后的挂钩（例如日期，服务器和连接）中添加，ModSecurity也无法触发或检查。这应该在代理设置中或阶段5（日志记录）中进行配置。

 **(4) Phase Response Body 响应体阶段**

响应体阶段是通用输出分析阶段。此时的响应体是应该要已经被缓存的，然后运行规则检查响应体。在此阶段，可以检查出站HTML来判断是否有信息泄露，是否包含错误消息或是失败的身份验证文本。

 **(5) Phase Logging 日志阶段**

该阶段在日志记录发生之前运行。进入此阶段的规则只会影响日志记录的执行方式。此阶段可用于检查Apache记录的错误消息。但是不能在此阶段拒绝/阻断连接，因为已经太晚了。此阶段还允许检查在阶段3或者阶段4期间不可用的其他响应头。需要注意的是，在这个阶段不要将拒绝/阻断操作继承到规则中，因为这样本身是一个配置的错误。

### 3、了解TOP10中几类攻击以及如何检测防御

 **（1）注入**

 **SQL注入攻击** ：产生的条件一个是参数用户可控，前端传入的参数内容由用户控制；另外一个是参数带入数据库的查询，传入的参数拼接到 SQL
语句，并且带入数据库的查询。

 **OS注入攻击**
：当应用需要调用一些外部程序时会用到一些系统命令的函数。应用在调用这些函数执行系统命令的时候，如果将用户的输入作为系统命令的参数拼接到命令行中，在没有过滤用户的输入情况下，会造成命令执行漏洞。

 **那么针对SQL注入和命令注入，怎样的去检测和防御。**

 **1）关于SQL注入攻击**
，可以关闭SQL错误的回显、前端输入字符白名单验证（长度和类型等）、对输入的特殊字符使用转义处理、设置用户的权限对机密数据加密存储等进行防御攻击。

 **2）命令注入攻击** 。可以对白名单校验命令参数、单引号进制命令解析功能、最后命令执行者不使用ROOT权限的用户。

当然在生产环境中，大多是使用成熟的WAF产品，对这些攻击进行防御。这里我们使用OWASP中的核心规则集中关于注入检测规则，了解一下它是如何进行检测防御SQL注入攻击和命令注入攻击行为。

 **a.** **REQUEST-932-APPLICATION-ATTACK-RCE.conf（命令执行攻击检测）**

该规则文件中的932100、932105、932106为Unix命令注入检测；932110、932115为Windows命令注入检测；932120为存在Windows
PowerShell命令检测；932130为找到 Unix Shell表达式检测；932140找到 Windows FOR/IF 命令检测；932150找到
Unix 命令执行检测；932160找到 Unix Shell代码检测；932170、932171为Shellshock
(CVE-2014-6271)；932180对受限文件上传进行检测；932190为通配符绕过方法尝试检测。

对其中的几个检测规则进行介绍，比如其中针对CVE-2014-6271漏洞的检测。首先我们应该了解的是目前的bash使用的环境变量是通过函数名称来调用的，导致漏洞出问题是以“(){”开头定义的环境变量在命令ENV中解析成函数后，Bash执行并未退出，而是继续解析并执行shell命令。那么，接下来，我们看一下
**932170** 和 **932171** 规则是如何检测的。

 **932170** ：SecRule REQUEST_HEADERS|REQUEST_LINE "@rx ^\\(\s*\\)\s+{"

 **932171** ：SecRule ARGS_NAMES|ARGS|FILES_NAMES "@rx ^\\(\s*\\)\s+{"

在这两条规则中，使用正则分别对请求头、请求行以及所有的请求参数和文件上载的表单字段列表，进行检测。其中“^\\(\s*\\)\s+{”，针对的就是对CVE-2014-6271漏洞的特征“(){”进行的检测。

再看一下其中的 **932120** 、 **932160** 规则，这两条规则分别针对Windows和Unix命令执行进行检测。

 **932120** ：SecRule REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|

REQUEST_COOKIES_NAMES|ARGS_NAMES|ARGS|XML:/*

"@pmFromFile windows-powershell-commands.data"

 **932160** ：SecRule REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|

REQUEST_COOKIES_NAMES|ARGS_NAMES|ARGS|XML:/*

"@pmFromFile unix-shell.data"

这两条规则中，均使用的运算符@pmFromFile，来对文件中的关键字进行匹配，并且是进行的不区分大小写的匹配。该运算符使用基于集合的匹配算法（Aho-Corasick），可以并行匹配任意数量的关键字。当需要匹配大量关键字时，此运算符比正则表达式执行得会更好。

windows-powershell-commands.data和unix-shell.data可下载查看完整文件内容，下图列举展示其中一部分。

![1636428650_6189eb6aeb7f5b005cf6c.png!small?1636428661763](https://image.3001.net/images/20211109/1636428650_6189eb6aeb7f5b005cf6c.png!small?1636428661763)

以上是介绍了命令执行攻击检测规则文件中的部分几个规则，该攻击检测规则文件还有使用正则表达式匹配命令执行攻击的检测，具体检测方式可以查看完整的规则文件。

 **b.** **REQUEST-942-APPLICATION-ATTACK-SQLI.conf（SQL注入攻击检测）**

该规则文件中针对SQL注入攻击检测更加的复杂，例如其中的942100检测到是通过Libinjection展开的SQL注入攻击。这里的Libinjection是一个轻量级的C语言编写的SQL注入攻击检测的库，其原理是通过对用户输入进行词法分析生成指纹，然后通过二分法查找算法，在特征库中进行匹配，匹配到则报SQL注入漏洞。其相比传统正则匹配识别SQL注入的好处在于速度快以及低误报，低漏报，速度快，有一个注意的点是它不支持对在注释内的SQL注入攻击进行检测。当然在942-SQL注入检测规则文件中的
**942200、942300、942440** 规则有针对注释攻击的检测以及942500对MySQL内联注释检测。这里在列举几个的规则：

 **942100** ：SecRule REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|

REQUEST_COOKIES_NAMES|REQUEST_HEADERS:User-Agent|REQUEST_HEADERS:Referer|ARGS_NAMES|ARGS|XML:/* "@detectSQLi"

该规则中对请求COOKIE、请求头中的User-Agent、Referer；请求参数和XMl进行SQL注入攻击检测。

 **942101** ：SecRule REQUEST_BASENAME "@detectSQLi"

该规则对REQUEST_FILENAME的文件名部分进行SQL注入攻击检测。可以看出942100和942101两条规则都是检测到通过
Libinjection 展开的 SQL 注入攻击行为。

 **942160** ：SecRule REQUEST_BASENAME|REQUEST_COOKIES|

!REQUEST_COOKIES:/__utm/|REQUEST_COOKIES_NAMES|ARGS_NAMES|ARGS|XML:/* "@rx
(?i:sleep\\(\s*?\d*?\s*?\\)|benchmark\\(.*?\,.*?\\))"

该规则通过正则对REQUEST_FILENAME的文件名部分、请求COOKIE、请求参数和XML检测使用 sleep() 或 benchmark()
的盲注攻击行为。

 **942500** ：SecRule REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|

REQUEST_COOKIES_NAMES|ARGS_NAMES|ARGS|XML:/*

"@rx (?i:/\\*[!+](?:[\w\s=_\\-()]+)?\\*/)"

该规则通过正则对请求COOKIE、请求参数和XML检测MySQL内联注释。规则中其他检测SQL注入行为，可查看完整规则文档进行了解。

 **（2）不安全的反序列漏洞**

首先了解一下， **什么是序列化和反序列化**
。序列化即将对象转化为字节流，便于保存在文件，内存，数据库中；反序列化即将字节流转化为对象。也就是把数据转化为一种可逆的数据结构，再把这种可逆的数据结构转化回数据，这就是序列化与反序列化。

 **这里对PHP反序列化漏洞攻击和Java反序列化漏洞攻击进行简单介绍一下。**
在PHP中主要序列化函数是serialize()，unserialize()，在执行unserialize后会触发析构函数或是wakeup函数，根本原因还是由于class的魔法函数。在Java中，序列化用到了ObjectOutputStream类中的writeObject()；反序列化用到了ObjectInputStream类中的readObject()。如果实际情况下，能够重写readObject方法，那么就有可能达到反序列化的时候命令执行。需要了解的是，在流量中java序列化数据的特征大多以标记（ac
ed 00 05）00 05是版本号 ，base64编码后是以rO0AB开头。

那么在CRS规则中，是如何对反序列化漏洞进行检测的。找到规则集中的两个规则文件分别是对PHP和Java相关的攻击检测。

 **a. REQUEST-933-APPLICATION-ATTACK-PHP**

该规则文件中，有针对PHP脚本文件上传、中高风险的PHP函数名称、PHP函数的调用、序列化对象注入等关于PHP的相关攻击检测。这里看一下关于PHP的序列化对象注入检测。它在其中的规则号为933170：

SecRule REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|

REQUEST_COOKIES_NAMES|REQUEST_HEADERS|ARGS_NAMES|ARGS|XML:/* "@rx
[oOcC]:\d+:\".+?\":\d+:{.*}"

该检测规则使用正则对请求COOKIE、请求头、请求参数等进行匹配。匹配条件就是后面的正则表达式式。其实简单了解一个PHP序列化对象注入的payload例子：

O:4:"Test":1:{s:4:"test";s:18:"<?php%20phpinfo();?>";}就可以很好理解这里的匹配规则。

 **b. REQUEST-944-APPLICATION-ATTACK-JAVA**

该规则文件中，有针对远程命令执行：Apache Struts、Oracle WebLogic的检测规则、利用Java反序列化Apache
Commons检测规则以及检测可疑的Java方法和Base64编码的字符串匹配可以关键字等检测规则。这里看一下关于序列化的一些检测规则。

 **944200** ：

SecRule ARGS|ARGS_NAMES|REQUEST_COOKIES|

!REQUEST_COOKIES:/__utm/|REQUEST_COOKIES_NAMES|REQUEST_BODY|REQUEST_HEADERS|XML:/*|

XML://@* "@rx \xac\xed\x00\x05"

 **944210** ：

SecRule ARGS|ARGS_NAMES|REQUEST_COOKIES|

!REQUEST_COOKIES:/__utm/|REQUEST_COOKIES_NAMES|REQUEST_BODY|REQUEST_HEADERS|XML:/*|

XML://@* "@rx (?:rO0ABQ|KztAAU|Cs7QAF)"

 **944240** ：

SecRule ARGS|ARGS_NAMES|REQUEST_COOKIES|

!REQUEST_COOKIES:/__utm/|REQUEST_COOKIES_NAMES|REQUEST_BODY|REQUEST_HEADERS|XML:/*|XML://@*

"@rx (?:clonetransformer|forclosure|instantiatefactory|

instantiatetransformer|invokertransformer|prototypeclonefactory|prototypeserializationfactory|whileclosure|getproperty|filewriter|xmldecoder)"

 **在上面三个检测规则中，可以看到使用正则对请求参数、请求COOKIE、请求体、请求头等对序列化标志（ac ed 00
05）和ConstantTransformer等类对象进行检测。**

##  **四、总结**

在上述的关于对OWASP CRS规则的介绍中，可以了解到CRS规则检测的覆盖范围是全面的。
**分为请求头阶段、请求体阶段、响应头阶段、响应体阶段以及日志记录阶段。**
本文中介绍了CRS规则在请求过程中对注入攻击和反序列化攻击的几个检测方法。其实深入了解到CRS的检测规则以后，可以看出，在当前WAF的检测攻击行为中，无论是其中传统的正则表达式检测方法，还是使用参数对知识库类的文件内容调用，还是其中SQL注入和XSS攻击的中使用Libinjection配合检测。其目的是为了减少在真实环境中的误报等情况。在减少误报的情况下，再使其横向拓展检测。其实在CRS规则中，对CVE-2014-6271、CVE-2017-10271等已知漏洞的检测是已经体现到的。

在本文介绍后关于OWASP CRS核心规则以后，不难了解到针对开源、可自主编写的OWASP
CRS规则，如果现有的WAF可以兼容使用其规则，其实是可以将WAF对相关的攻击检测策略更加的完善、更加的及时有效。

