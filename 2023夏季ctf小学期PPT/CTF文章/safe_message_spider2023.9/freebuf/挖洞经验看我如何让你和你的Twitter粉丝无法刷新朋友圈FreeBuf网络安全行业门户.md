***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![247842-3kQUCf1465652976.jpg](https://image.3001.net/images/20190404/1554368144_5ca5c69023c89.jpg!small)**
**大家好，今天分享的这个writeup是关于Twitter的一个Dos漏洞，利用该漏洞，只需发送一条推特朋友圈，就可以触发Twitter后端服务器解析错误，导致你和你的粉丝账户无法刷新推特朋友圈。**

## 从XSS入手打开切口

DoS攻击一般是指针对某一类型资源（如网站、应用程序或服务器）的特定请求攻击，攻击可以造成该资源服务失效，甚至功能瘫痪。

刚开始，我原本打算去尝试发现Twitter移动官网（mobile.twitter.com）上的XSS漏洞，但却一无所获。但后来，我登录进Twitter移动官网，开启了一个对话框进行测试，在其中反复发送了各种Payload，想获得一些有效的XSS解析响应。以下是我的一个大致思路过程：

我注意到，用户在Twitter中发送任意URL链接时，Twitter会用自身短网址服务把用户的发送URL链接转变为“t.co”前缀域名样式，这是正常情况。短网址服务是Twitter为保护用户免受恶意链接威胁而引入的，有点类似Facebook的重定向跳转保护服务Linkshim。但是，当你用“twitter.com”子域名或是“mobile.twitter.com”网站来发送URL链接时，却不会生成“t.co”前缀域名样式，哦，这......。

这就有点意思了，因为大多现代Web技术网站针对用户的连续操作请求，为了增加用户体验和响应效率，都不会重新通过服务器加载整个页面，而是经由异步通信方式的AJAX或XMLHttpRequests在后台执行请求，实现轻量级请求交互。就比如说，当你从Twitter网站系统之外的地方，试图去访问<https://mobile.twitter.com/notifications>这个链接，此时，Twitter后端服务器确实是需要完整地加载这个页面；但如果你从Twitter网络系统内部来访问这个链接，Twitter后端服务器却只通过某些javascript脚本就能实现渲染加载，而不需要执行整个页面的加载。  

所以，从这个点来讲，我原先构造的XSS漏洞发现思路是，希望在Twitter网站系统内部，通过发送一条属于Twitter自身网站URL且包含XSS
Payload变量的消息。

## XSS漏洞到Dos漏洞的发现

我一开始构造的XSS Payload链接是这样的：

> <https://mobile.twitter.com/?>'"><img/src=x/onerror=alert(1)>

我猜想，如果在Twitter网站系统之外，可能不会生效，但如果在Twitter网站系统内部，因加载方式不同可能会触发一些不同的东西。所以，围绕这类XSS
Payload我就反复进行发送测试。

后来，我发现，其中包含有 **"%u003e"** 的一个XSS
payload竟然会导致一个Twitter服务错误！而且这个错误会让我看不到任何Twitter的会话消息！这就更有意思了！为什么呢？

这个十六进制的%u003e经Urldecode后明显是大于符号 ** >**，但是，Twitter却无法对它进行解析处理！之后，我又尝试了包含 “
**%xx** ”
等样式的URL链接进行发送，简单地就像<https://mobile.twitter.com/%xx>，这下又来了，还是产生了同样的错误！

我猜测，%xx不是一个有效的十六进制值，可能Twitter后端想尝试对它进行匹配解析，但是却在其内部服务中找不到%xx的对应解析值，所以，每当用户请求包含%xx且属于Twitter网站的URL链接时，Twitter后端就抛出这个错误。

基于此，我就想那我用这个包含%xx的链接 <https://mobile.twitter.com/%xx>
来发条推特朋友圈吧，可能大家无法想像，这简直让我吓掉了下巴！包含这条链接的朋友圈一发出去，我的朋友圈就刷不出来了，而且，连我Twitter账户中的粉丝也都无法刷新朋友圈了！注意，这里是Twitter移动官网（mobile.twitter.com）的情况，那么，Twitter主站会有这种情况吗？

拭目以待，但是，经测试，Twitter主站不存在上述情况，现在怎么办呢？有没有其它变通方法？哈哈，经过一番研究，我发现，可以以下通过链接 -<https://twitter.com/i/onboarding/verify> ，强制把电脑显示界面强制转换为手机显示界面！步骤为：

> 1、在电脑端登录Twitter账户；
>
> 2、在当前浏览器页面中粘贴进<https://twitter.com/i/onboarding/verify>，访问；
>
> 3、点击随后弹框出现的 “Got it” 按钮；
>
> 4、现在，你就处于手机显示界面了。

参照Twitter移动官网的测试方法，经测试，用链接<https://twitter.com/%xx>发了朋友圈之后，当前我自己账户的朋友圈和我账户中粉丝的朋友圈也都无法刷新了！PoC漏洞验证视频如下：

## 演示视频：

最终，我把漏洞上报后，经Twitter官方确认，这是一个影响*.twitter.com，且算严重的Dos漏洞，所以Twitter给了我$1,120美金奖励。漏洞详情，参见Hackerone报告
- <https://hackerone.com/reports/500686>

***参考来源：[seekurity](https://www.seekurity.com/blog/general/twitter-denial-of-service-bug-or-how-i-could-prevent-all-followers-from-reading-or-accessing-literally-any-tweets/)，clouds编译，转载请注明来自FreeBuf.COM**  

