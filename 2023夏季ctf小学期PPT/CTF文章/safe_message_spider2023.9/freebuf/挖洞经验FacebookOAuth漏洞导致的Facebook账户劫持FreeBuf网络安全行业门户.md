![](https://image.3001.net/images/20200310/1583833907_5e676333b50fe.jpg!small)

**平时在用“Login with
Facebook”功能进行跳转登录时，因为其用到了多个URL重定向跳转，所以总会给我有一种不安全的感觉。但是，要想发现Facebook漏洞，并非易事，需要莫大的功夫和精力，更别说涉及登录的Facebook
OAuth了，这更是难上加难。然而，我就发现了Facebook OAuth这么一个漏洞，获得了Facebook官方$55,000的奖励。**

就是这么一个漏洞，存在了多年，而且，从google搜索和StackOverflow社区中都能找到相关漏洞线索，这些线索存在的时间几乎是9到10年之久。

##  漏洞概况

“Login with Facebook”功能以OAuth
2.0协议处理facebook.com和其它第三方网站之间的用户token，只有当正确身份的用户token被验证通过，用户才能从第三方网站跳转到facebook.com网站。攻击者利用该漏洞可以劫持受害者用户的OAuth身份验证机制，窃取受害者用户的access
token，最终实现对受害者Facebook账户的劫持。另外，攻击者可以通过控制架设恶意站点，针对大多数APP应用（如Instagram, Oculus,
Netflix, Tinder, Spotify等），窃取用户access_token，获取相关交互服务和第三方网站的访问控制权。

##  POC

Facebook的SDK中，存在一个名为"/connect/ping"的登录服务端，它负责为用户生成一个user_access令牌，并把链接跳转指向一个Facebook应用通用的白名单集“XD_Arbiter”下。该服务端在Facebook的SDK加载过程中，会首先创建一个方便跨域通信的代理框架（proxy
iframe），该代理框架会通过 postMessage()
API发回用户token、相关代码和一些未授权或未知的请求状态。整个"/connect/ping"的工作流程如下：

>
> [https://www.facebook.com/connect/ping?client_id=APP_ID&redirect_uri=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D42%23origin%3Dhttps%253A%252F%252Fwww.domain.com](https://www.facebook.com/connect/ping?client_id=APP_ID&redirect_uri=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D42%23origin%3Dhttps%253A%252F%252Fwww.domain.com)

该服务端部署了参数污染（parameter
pollution）防护、同源验证、重定向跳转限制等各种安全措施，我使用了好多绕过手段也没发现可利用的端倪。刚开始，完全是毫无头绪。

后来，我发现可以把其中的
“xd_arbiter.php?v=42”修改成为“xd_arbiter/?v=42”，而且，还可以通过添加目录或参数的形式实现目录遍历。总算有点线索了，但是离窃取用户token还有十万八千里。为此，我们需要想办法让代理框架为我们所用，可以让它在“location.hash”或跨域postMessage()
API通信接口中实现一些信息劫持。非常幸运，我在Facebook的“page_proxy”中发现了这么一个天然的代理框架 （目前已被删除）：

> <https://staticxx.facebook.com/platform/page_proxy/r/7SWBAvHenEn.js>

该“page_proxy”中包含了我们想要的代码实现：

    
    
    var frameName = window.location.href.split("#")[1];
    
        window.parent.postMessage(frameName,"*");

上述代码位于一个“EventListener”属性之下，如果请求条件判断失效，代码会以postMessage()方式抛出针对任意域的“frameName”
消息，表明配置或代码错误。

##  Exploiting Proxy

要想利用这个 “page_proxy”，也并非难事，只需要把page_proxy和xd_arbiter结合起来。三者关系如下：

> <https://staticxx.facebook.com/platform/page_proxy/r/7SWBAvHenEn.js>
>
> <https://staticxx.facebook.com/connect/xd_arbiter.php?version=42>
>
>
> <https://staticxx.facebook.com/connect/xd_arbiter/r/7SWBAvHenEn.js?version=42>

在该漏洞构造流程中，以下两点较为重要：

> HTTP请求中缺失“X-Frame-Options”头；
>
> “window.parent”方法会把用户交互处理抵消，所以不必担心window.open或其它的按钮跳框弹出事件。

为了针对上述Oauth的攻击，在包含进Facebook认证流的同时，需要改装重写我们自己的Custom_SDK.js，如下：

    
    
    var app_id = '124024574287414',
    
        app_domain = '[www.instagram.com](http://www.instagram.com/)';
    
        var exploit_url = '<https://www.facebook.com/connect/ping?client_id=>' + app_id + '&redirect_uri=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter%2Fr%2F7SWBAvHenEn.js%3Fversion%3D44%23origin%3Dhttps%253A%252F%252F' + app_domain;
    
        var i = document.createElement('iframe');
    
        i.setAttribute('id', 'i');
    
        i.setAttribute('style', 'display:none;');
    
        i.setAttribute('src', exploit_url);
    
        document.body.appendChild(i);
    
        window.addEventListener('OAuth', function(FB) {
    
          alert(FB.data.name);
    
        }, !1);

然后，我把该JS脚本部署在我自己的网站，通过测试，利用它能隐蔽窃取受害用户对任意域的access_token，最终可导致潜在的受害用户账户劫持。

![](https://image.3001.net/images/20200310/1583833693_5e67625d2424f.png!small)

##  Facebook账户劫持漏洞及修复

因为可以窃取第一方的graphql用户token，所以针对受害者Facebook账户来说，完全可以在账户恢复功能中构造添加绑定新手机号的请求。由于该过程中，Facebook后端对GraphQL请求是白名单化且无任何权限验证的，因此，攻击者也就具备了对受害者Facebook账户中消息、照片、视频或隐私权设置的完全读写更改权限。

我及时向Facebook上报了该漏洞，Facebook官方也及时地确认了该漏洞的有效性，并立即进行了以下修复措施：

> 废弃“/connect/ping”服务端，并取消其对所有Facebook应用的用户access_token生成；
>
> 在XD_Arbiter文件中添加了__d(“JSSDKConfig”)代码行，避免在page_proxy中的JS构造执行。

##  绕过修复措施

虽然我和Facebook都清楚OAuth的核心服务端“/dialog/oauth/"中，仍然存在携带用户token跳转到page_proxy的情况，而且在上述漏洞报告中我也提醒过他们需要进行修复。但是，Facebook在回复中声称xd_arbiter是白名单化的，上述修复措施足够缓解该漏洞问题，将不会导致用户token泄露。

之后，我在后续的两三天又再次检查了page_proxy中的代码，发现代码“__d(“JSSDKConfig”)”被移到了底部，而且代码的postMessage()调用仍然可以被执行，为此，我又想办法看看能否再次对其进行绕过。

但分析之后我发现，[www.facebook.com](http://www.facebook.com/)后端并没有遵循xd_arbiter的重定向状态，而是为客户端的请求域创建了closed_window
和 postMessage() 调用来防止攻击，此规则虽然对chrome浏览器的m版本（multi-install）、”mobile”和”touch”版本生效，但对firefox浏览器却无任何防护效果。

另外，在域名“mbasic.facbook.com”下也会发生HTTP 302跳转，且对所有浏览器有效，这就再次和之前的漏洞结合起来了：

>
> [https://mbasic.facebook.com/dialog/oauth?client_id=124024574287414&redirect_uri=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter%2Fr%2F7SWBAvHenEn.js%3Fversion%3D42%23origin%3Dhttps%253A%252F%252Fwww.instagram.com%252F](https://mbasic.facebook.com/dialog/oauth?client_id=124024574287414&redirect_uri=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter%2Fr%2F7SWBAvHenEn.js%3Fversion%3D42%23origin%3Dhttps%253A%252F%252Fwww.instagram.com%252F)

最终修复措施

> 不允许对xd_arbiter的任意修改，只接受单纯的文件路径"xd_arbiter.php"；
>
> 禁用所有xd_arbiter上的HTTP跳转；
>
> 删除page_proxy资源“7SWBAvHenEn.js”；
>
> 在另外一个JS脚本资源中增加正则过滤验证。

##  漏洞影响

攻击者利用该漏洞，部署控制恶意站点诱惑用户访问，当用户在使用Facebook的Oauth身份验证机制时，就能窃取用户的Facebook access
token，实现对用户的Facebook或其它第三方账户劫持。

##  漏洞上报和修复进程

> 2019.12.16 漏洞初报
>
> 2019.12.16 漏洞确认
>
> 2019.12.23 漏洞修复
>
> 2020.1.3 修复措施绕过
>
> 2020.1.10 后续漏洞再次被确认
>
> 2020.1.17 漏洞修复
>
> 2020.2.21 Facebook奖励$55,000（账户劫持的单个最高漏洞奖励）

***参考来源：[amolbaikar](https://www.amolbaikar.com/facebook-oauth-framework-vulnerability/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

