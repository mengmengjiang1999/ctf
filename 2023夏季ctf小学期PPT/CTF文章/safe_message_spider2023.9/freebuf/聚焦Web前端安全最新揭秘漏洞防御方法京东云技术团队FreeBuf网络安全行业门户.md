在 Web
安全中，服务端一直扮演着十分重要的角色。然而前端的问题也不容小觑，它也会导致信息泄露等诸如此类的问题。在这篇文章中，我们将向读者介绍如何防范Web前端中的各种漏洞。【万字长文，请先收藏再阅读】

首先，我们需要了解安全防御产品已经为我们做了哪些工作。其次，我们将探讨前端存在哪些漏洞，并提供相应的防范思路。

# 一、安全防御产品

安全防御产品一般有：

![](https://image.3001.net/images/20230809/1691548892_64d2fcdcadb60dd750637.png!small)

传统互联网公司的安全防御体系，类似于一个空气净化模型，每个层都有不同的产品，包括网络层防护、应用层防护、主机层防护、运行时防护、安全开发防护和安全运营防护。外部攻击流量经过过滤后，到达应用系统的流量相对较为安全。

对于我们前端而言，最有用的是安全开发防护层中的白盒和黑盒。白盒扫描是对我们的源代码进行扫描，在上线时会自动检测问题。黑盒扫描则不考虑程序的结构和代码细节，对应用程序进行漏洞扫描，每天都有定时任务扫描公网。

在安全方面，我们与集团安全部门进行双向合作。在集团安全防御体系已经做了一些工作的基础上，我们如何针对前端可能存在的漏洞进行防范，是我们研发部门需要思考的问题。

# 二、漏洞防范

### 1、安全传输

首先，务必使用HTTPS协议，这可以有效防止局域网内的明文抓包。

### 2、域分离

其次，进行域分离。将一些业务关联性较小的内容转移到不相关的域中。如果分离域下出现了XSS漏洞，不会影响业务主域，而且分离域下的XSS漏洞也无法获得奖励。如果所有内容都在主域下，一旦主域出现漏洞，主域下的所有子域都会受到破坏。

 **前端领域** 常见的漏洞有 **3种** ： **XSS** 漏洞、 **CSRF** 漏洞、 **界面操作劫持** 漏洞

### 3、XSS防御方案

对于概念，包括名词定义、攻击方式、解决方案等估计大家都看过不少，但留下印象总是很模糊，要动手操作一番才能加深印象并能真正理解。

 **1）XSS 模拟攻击**

先动手实现一个 XSS 的攻击场景，然后再讲解 XSS 的防范手段。看这个代码：

![](https://image.3001.net/images/20230809/1691548893_64d2fcdd57d05ef07acf3.png!small)

  

点击“write”按钮后，会在页面插入一个a链接，a链接的跳转地址是文本框的内容。在这里，通过innerHTML把一段用户输入的数据当做HTML写入到页面中，这就造成了XSS漏洞。尝试如下输入：

![](https://image.3001.net/images/20230809/1691548893_64d2fcddd717fe633709e.png!small)

  

首先用一个单引号闭合掉href的第一个单引号，然后闭合掉<a>标签，然后插入一个img标签。页面代码变成了：

![](https://image.3001.net/images/20230809/1691548894_64d2fcde4cfa1654a3ba7.png!small)

  

脚本被执行：

![](https://image.3001.net/images/20230809/1691548894_64d2fcdec55b4be77b9b8.png!small)

  

所以你明白了吧，XSS跨站脚本攻击就是注入一段脚本，并且该脚本能够被执行。其中最常见的XSS
Payload就是读取浏览器的Cookie对象。通过盗取Cookie，攻击者可以直接调用接口，发起“Cookie劫持”攻击。

![](https://image.3001.net/images/20230809/1691548895_64d2fcdf40bf36fc18f9f.png!small)

  

为了防止“Cookie劫持”，集团的统一登录使用了Cookie的“HttpOnly”和“Secure”标识。

HttpOnly标识表示该Cookie仅在HTTP层面传输。一旦设置了HttpOnly标志，客户端脚本就无法读写该Cookie，从而有效地防御XSS攻击获取Cookie的风险。

Secure标识确保Cookie只在加密的HTTPS连接中传输，从而降低了“Cookie劫持”的风险。

因此，建议避免使用localStorage存储敏感信息，哪怕这些信息进行过加密。因为localStorage存储，没有针对XSS攻击，做任何防御机制。一旦出现XSS漏洞，那么存储在localStorage里的数据就极易被获取到。

 **2）XSS的危害**

让我们简单谈谈XSS的危害。注入的脚本可能会进行JavaScript函数劫持，覆盖我们代码中原有的函数，修改js原型链上的函数，或在原函数基础上添加额外行为。例如，将网络请求的响应发送到攻击者的服务器。

JavaScript函数劫持是什么？它是在目标函数触发之前重写某个函数的过程。例如：

    
    
    let_write =document.write.bind(document);document.write=function(x){if(typeof(x)=="undefined"){return;}_write(x);}

注入的脚本还可能对用户进行内存攻击。如果知道用户使用的浏览器、操作系统，攻击者就有可以实施一次精准的浏览器内存攻击。通过XSS，可以读取浏览器的UserAgent对象。

    
    
    alert(navigator.userAgent);

![](https://image.3001.net/images/20230809/1691548897_64d2fce182ac3a2453965.png!small)

  

该对象提供了客户端的信息，如操作系统版本：Mac OS X 10_15_7，浏览器版本：Chrome/114.0.0.0

注入的脚本可能强制弹出广告页面、刷流量，也可能进行大量的DDoS攻击，导致网络拥塞。此外，它还可能控制受害者的机器向其他网站发起攻击。

如果信贷产品的网页存在XSS漏洞，黑客可以注入一段脚本，调用查询借还记录的接口，并将响应结果发送到自己的服务器。然后，利用用户的借还记录等信息，对用户进行电信诈骗。

第三方统计脚本有机会窃取用户的敏感信息，如浏览历史、真实IP、地理位置、设备信息，并将其传送给攻击者。此外，我们使用的第三方依赖和npm包也有可能窃取用户信息。在这方面，集团对代码进行了白盒扫描，已一定程度上规避问题。但最好我们在选择第三方包时，选择可信赖的包。

 **3）XSS 防范方法**

XSS 防范方法通常有以下几种：

①慎防第三方内容：对于流行的统计脚本和第三方依赖，要谨慎使用。

②输入校验和输出编码：进行输入校验，包括长度限制、值类型是否正确以及是否包含特殊字符（如<>）。同时，在输出时进行相应的编码，根据输出的位置选择适当的编码方式，如HTML编码和URL编码。

③使用HttpOnly属性：防范XSS攻击后的"cookie劫持"。

使用Secure属性，确保Cookie只在加密的HTTPS连接中传输，降低"cookie劫持"的风险。

④避免使用localStorage存储敏感信息。

⑤使用Content-Security-Policy（内容安全策略）：可以通过指定只允许加载来自特定域名的脚本，防范XSS攻击，例如，可以使用以下配置只允许加载来自mjt.jd.com域名的脚本

    
    
    #只允许加载来自特定域名的脚本
    add_header Content-Security-Policy "script-src mjt.jd.com";

### 4、CSRF防御方案

![](https://image.3001.net/images/20230809/1691548897_64d2fce1f05ab1904baa9.png!small)

  

CSRF漏洞是借用用户的权限做一些事情，注意，是“借用”，而不是“盗取”。XSS漏洞是“盗取”用户权限，CSRF漏洞是“借用”用户权限。

 **1）CSRF 模拟攻击**

我们先动手实现一个 CSRF 攻击场景，然后再介绍 CSRF
的防范手段。我们要模拟以下场景：用户先登录了银行网站，然后黑客网站诱导用户访问和点击，从而利用用户的登录权限，让用户给黑客自己转账。我们使用 express
启动一个服务，模拟 CSRF 攻击。银行网站的服务启动在 3001 端口，并提供以下3个接口：

    
    
    app.use('/',indexRouter);app.use('/auth',authRouter);app.use('/transfer',transferRouter);

authRouter:

    
    
    router.get('/',function(req, res, next){res.cookie('userId','ce032b305a9bc1ce0b0dd2a',{expires:newDate(Date.now()+900000)})res.end('ok')});

/auth 接口在 cookie 中设置了一个名为 userId 的 cookie，即给用户授予登录权限。

transferRouter：

    
    
    router.get('/',function(req, res, next){const{query }=req;const{userId }=req.cookies;if(userId){res.send({status:'transfer success',transfer:query.number
        })}else{res.send({status:'error',transfer:''})}});

/transfer 接口判断了 cookie，如果存在 cookie，则转账成功，否则转账失败。

使用 ejs 提供银行转账页面：

    
    
    <!DOCTYPEhtml><html lang="en"><head><meta charset="UTF-8"><meta name="viewport"content="width=device-width, initial-scale=1.0"><title><%=title %></title></head><body><h2>转账
      </h2><script>consth2 =document.querySelector('h2');h2.addEventListener('click',()=>{fetch('/transfer?number=15000&to=Bob').then(res=>{console.log(res.json());})})</script></body></html>

黑客网站的服务启动在 3002 端口，并提供一个与银行网站外观相同的页面：

    
    
    <!DOCTYPEhtml><html lang="en"><head><meta charset="UTF-8"><meta name="viewport"content="width=device-width, initial-scale=1.0"><title><%=title %></title></head><body><div class="wrapper"id="container"><h2>转账
      </h2><form action="http://bank.com/transfer"method=GET><input type="hidden"name="number"value="150000"/><input type="hidden"name="to"value="Jack"/></form><script>consth2 =document.querySelector('h2');h2.addEventListener('click',()=>{submitForm();})functionsubmitForm(){document.forms[0].submit();}</script></div></body></html>

由于两个网站都是在 localhost 域名下，cookie 是根据域名而不是端口进行区分的。因此，我们使用 Whistle 进行域名映射：

    
    
    # bank.com 映射到 127.0.0.1:3001bank.com 127.0.0.1:3001# hack.com 映射到 127.0.0.1:3002hack.com 127.0.0.1:3002

现在我们开始操作。首先打开浏览器，访问银行网站 的 /auth获得授权：

![](https://image.3001.net/images/20230809/1691548898_64d2fce28b25ed999db57.png!small)

  

然后通过点击”转账”按钮发送请求，http://bank.com/transfer?number=15000&to=Bob，进行转账操作：

![](https://image.3001.net/images/20230809/1691548899_64d2fce34d12e63a6b22d.png!small)

  

用户受到邮件或者广告诱惑进入了 黑客网站，黑客网站首页有一个“转账”按钮，调银行的transfer接口
http://bank.com/transfer?number=150000&to=Jack 这个请求放在 <form /> 的 action 中

![](https://image.3001.net/images/20230809/1691548899_64d2fce3e764ee6443c55.png!small)

  

可以看到请求携带了 cookie，并成功转账，这样一次 CSRF 攻击就完成了。

从上面可以看出，CSRF 攻击的主要特点是：

①发生在第三方域名(hack.com)

②攻击者利用 cookie 而不获取具体的 cookie 值

因此，防范 CSRF 攻击的关键是防止其他人冒充你去执行只有你能执行的敏感操作。

 **2）CSRF 危害**

简单说，CSRF会导致：个人隐私泄露、机密资料泄露、甚至危及用户和企业的财产安全。一句话概括CSRF的危害：盗用受害者身份，受害者能做什么，攻击者就能以受害者的身份做什么。

### 3）CSRF 防范方法

①阻止不同域的访问：同源检测

在HTTP请求中检查Referer或origin字段，确保请求来源是站内地址和站内域名。如果发现Referer或origin地址异常，就可以怀疑遭到了CSRF攻击。

②使用验证码

尽管会降低用户体验，但验证码是防止CSRF攻击的最有效手段。

③提交时要求附加本域才能获取的信息

例如使用一次性token（生成token的因子包括时间戳和用户ID）来验证请求的合法性。

④不要允许所有域访问，使用allow-access-from domain时避免以下方式，即根据前端请求的域来允许访问：

    
    
    Stringorigin =request.getHeader("origin");if(StringUtils.isNotEmpty(origin)){response.setHeader("Access-Control-Allow-Origin",origin);response.setHeader("Access-Control-Allow-Credentials","true");}else{response.setHeader("Access-Control-Allow-Origin","*");}

这种方式是不可取的，应该限制访问的域。

### 5、界面操作劫持防御方案

它是一种基于视觉欺骗的攻击方式，其核心在于利用标签的透明属性。攻击者会在网页的可见输入控件上覆盖一个不可见的框，从而让用户误以为自己在操作可见控件，实际上却是在操作不可见框。

![](https://image.3001.net/images/20230809/1691548900_64d2fce4c8b49dd43fe2c.png!small)

  

界面操作劫持还包括：点击劫持、拖放劫持、触屏劫持

 **1）常见的攻击场景**

点击劫持的常见攻击场景是伪造登录框。当用户在伪造的登录框中输入用户名和密码后，他们以为自己点击的是登录页面上的登录按钮，但实际上他们点击的是黑客页面上的“登录”按钮，导致密码被发送到黑客的服务器上。

拖放劫持利用了拖放操作不受“同源策略”限制的特点，用户可以把一个域的内容拖放到另一个不同的域。攻击者结合CSRF漏洞，将iframe中目标网页的token拖放到攻击者的页面中，从而实施攻击。

触屏劫持是在手机上进行的一种视觉欺骗攻击。由于手机屏幕空间有限，手机浏览器会隐藏地址栏以节省空间。攻击者常常利用这一点，当触发一个权限获取的提示框时，他们会将提示框的主体背景设为透明，并覆盖上伪造的消息提示图像，只留下权限提示框的确认按钮。这样，用户会误以为自己在点击某个消息的确认，实际上却是在点击权限确认。

 **2）界面操作劫持的防范方法**

①Content-Security-Policy （内容安全策略）

    
    
    #防御界面操作劫持
    #add_header Content-Security-Policy "frame-ancestors 'self';";#只允许网页在相同被嵌套到框架
    #add_header Content-Security-Policy "frame-ancestors 'none';";#禁止网页在任何域名下被嵌套到框架
    #add_header Content-Security-Policy "frame-ancestors mkt.shop.jd.com";#只允许网页在某些域名被嵌套到框架

②脚本防御：破坏frame，防止利用透明层进行操作劫持攻击

    
    
    if(top ===self){document.documentElement.style.display ='block';}else{top.location =self.location;}

③使用iframe嵌入目标网站进行测试，若成功嵌入，则说明可能存在漏洞。

# 三、培养安全意识

为了确保代码的安全性，我们需要培养以下几点安全意识：

![](https://image.3001.net/images/20230809/1691548901_64d2fce5684d8df2fa61d.png!small)

  

通过培养这些安全意识，我们可以更好地保护我们的代码和系统，减少安全风险和潜在的攻击。

  

> 作者：京东科技 张朝阳
>
> 来源：京东云开发者社区

