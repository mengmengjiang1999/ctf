## 前言

近年来人们发现浏览器才是互联网最大的入口，绝大数用户使用互联网工具是浏览器，因此浏览器如果具备安全功能，将很好的保护用户上网。

## 一、同源策略

### 1、什么是同源策略

同源策略（Same Origin
Policy)是一种约定，他是浏览器最核心也是最基本的安全功能，如果缺少了同源策略，则浏览器的正常功能受到影响，可以说web的构建实在同源策略的基础之上的，浏览器只是针对同源策略的一种实现表示。

 **浏览器的同源策略，限制了来自不同源的文件或脚本，对当前的文件读取或者设置某些属性。**

如果没有同源策略，假设a.com有一段javascript脚本，在b.com未曾加载此脚本时，a.com可以随意修改b.com的页面（在浏览器的显示中）。为了不让浏览器的页面行为发生混乱，浏览器提出“Origin”（源）这的概念，来自不同源的对象无法互相干扰。

对于js来说，认为同源不同源的实列：

url| 结果| 原因  
---|---|---  
<http://stroe.shen.com/dir2/index.html>| 同源|  
  
<http://stroe.shen.com/dir/inner/admin.html>| 同源|  
  
<https://stroe.shen.com/test2.html>| 不同源| 不同的协议  
<http://stroe.shen.com:81/dir/inner/admin.html>| 不同源| 不同的端口  
<http://new.shen.com/dir/inner/admin.html>| 不同源| 不同的主机  
  
影响源的因素有：域名、IP地址、子域名、端口、协议

 **注意：**

对于当前页面来说，页面中存放js文件的域并不重要，重要的时加载js页面的域时什么。

简单来说，1.com通过以下代码：

    
    
    <script src=http://2.com/2.js></script>

加载了2.com上的2.js，但是2.js是运行在1.com页面中的，因此对于当前打开的页面（1.com）来说。2.js的源就是应该是1.com。

### 2、XMLHttpRequest同源策略

XMLHttpRequest 对象提供了对 HTTP 协议的完全的访问，包括做出 POST 和 HEAD 请求以及普通的 GET
请求的能力。XMLHttpRequest 可以同步或异步地返回 Web 服务器的响应，并且能够以文本或者一个 DOM 文档的形式返回内容。

 **原理**

在浏览器中<script>、<img>等标签都是可以跨域加载资源的，而不受同源策略的限制。这些带“src"属性的标签每次加载时，实际上就是有浏览器发起一次get请求。通过src数据加载资源，浏览器限制了js的权限，使其不能读写返回的内容。

而对于XMLHttpRequest来说，它可以访问来自同源对象的内容。但不能跨域访问资源。

后来w3c委员会制定XMLHttpRequest跨域访问标准。需要通过目标域返回的HTTP头来授权是否允许跨域访问，因为http头对于js来说一般时无法控制的。这个跨域方案的安全基础就是信任”js无法控制http头“。

![image-20211026120747350](https://image.3001.net/images/20211103/1635943676_618284fc9a3fb074bc494.png!small)

Origin字段用来说明，本次请求来自哪个源（协议 + 域名 + 端口）。服务器根据这个值，决定是否同意这次请求。 Access-Control-Allow-Origin它的值要么是请求时`Origin`字段的值，要么是一个`*`，表示接受任意域名的请求。

### 3、Flash插件同源策略

对于浏览器来说，除了DOM、Cookie、XMLHttpRequest会受到同源策略的限制，浏览器的一些第三方插件也可以有不紫的同源策略，常见的一些插件如Flash、java
Applet等。

 **原理**

Flash它主要通过目标网站提供的crossdomain.xml文件判断是否允许当前源的Flash跨域访问目标资源。

假设[www.test.com](www.test.com)的策略文件为例,当浏览器在任意其他域的页面加载了Flash后，如果对[www.test.com](www.test.com)发起访问，Flash会检查[www.test.com](www.test.com)上策略文件是否存在。如果文件存在，则检查发起的请求的域是否在许可范围内。

    
    
    <?xml version="1.0"?>  
    <cross-domain-policy>  
    <allow-access-from domain="*.test.com" />  
    <allow-access-from domain="*.test.net" />  
    <allow-access-from domain="*.test2.com" />  
    <allow-access-from domain="*.test.cn" />  
    <allow-access-from domain="*.test1.com" />  
    </cross-domain-policy>

在上面的策略文件中,只有在allow-access-from标签内的域的情况是被允许的。

Flash9及其之后的版本，还通过MINE检查确定crossdomain.xml是否合法，比如查看服务器返回的http头的Content-Type是否是test/*、application/xml等。攻击者可以通过上传crossdomain.xml文件控制flash的行为，绕过同源策略，出了MIME检查外，Flash还会检查crossdomain.xml是否在根目录下，也使得一些上传文件的攻击失效。

### 4、IE8的CSS跨域漏洞测试

浏览器的同源策略也是可能存在问题了，我们可以通过绕过等方式，下面我们在测试一下IE8的CSS跨域漏洞

 **A服务器部署**

<http://192.168.163.131/a.html>

    
    
    <body>  
    {}body{font-family:  
    yyyyyyyyyyyyyyy  
    bbbbbbbbbbbbbbb  
    </body>

 **B服务器部署**

<http://192.168.163.132/b.html>

![image-20211026153653781](https://image.3001.net/images/20211103/1635943677_618284fda3515590f55c7.png!small)

    
    
    <style>  
    @import url("http://192.168.163.131/a.html");  
    </style>  
    <script>  
    setTimeout(function(){  
    var a = document.body.currentStyle.fontFamily;  
    alert(a);  
    },2000);  
    </script>

使用IE8及以下版本浏览器访问<http://192.168.163.132/b.html>，测试![image-20211026192254207](https://image.3001.net/images/20211103/1635943678_618284fe9323109195910.png!small)

我们看到弹出a.html中的内容，理论var x=document.body.currentStyle.fontFamily;可以把{}body{font-family:"之后的所有内容存到x中，再由alert弹出。

前面我们提到<scriot>等标签仅能加载资源，但是不能读写资源的内容，而这个漏洞能实现跨域读取页面内容。具体怎么利用就仁者见仁智者见智了。

## 二、恶意网站拦截

### 1、恶意网站拦截原理

在网页中插入一段恶意代码，利用浏览器漏洞执行任意代码的攻击方式，被称为“挂马”。

挂马攻击能够破坏浏览器的安全，在很多时候，挂马攻击实施时会在一个正常网页通过<script>、<iframe>等标签加载一个恶意的网址。恶意网站包括两大类：挂马网站或诈骗、钓鱼网站等。

挂马网站：通常包含恶意的脚本如js或Flash,利用浏览器漏洞执行shellcode。

诈骗钓鱼网站：模仿知名网站的相似页面来欺骗用户。

目前浏览器推出的拦截恶意网站的功能大多时基于黑名单的方式，浏览器周期性从服务器获得一份最新的恶意网站黑名单，如果用户上网访问的网站在黑名单里，浏览器就会弹出一个告警界面。![image-20211026222746908](https://image.3001.net/images/20211103/1635943679_618284ffd0f11d3d9fa89.png!small)

PhishTank是互联网免费提供恶意网站黑名单的组织之一。

    
    
    https://phishtank.org/index.php

![image-20211026223257215](https://image.3001.net/images/20211103/1635943681_61828501d157f3518ee92.png!small)

### 2、EVSSL证书简述

EV SSL，也称EV SSL证书，英文全名为：Extended Validation SSL
Certificate，就是全球领先的数字证书颁发机构和主流的浏览器开发商共同制定的一个新的SSL证书严格身份验证标准，

增强型 SSL 证书（EVSSL）是最高级别的 SSL
数字证书。EVSSL最大的特色便是激活网站浏览器的栏位使其变成绿色，利用鲜明的标示告诉网友：这个网站正受到最严密的信息安全防护

同时EVSSL证书遵循X509标准，并向前兼容普通证书，如果浏览器不支持EV模式，则把该证书当前普通证书，如果浏览器痔疮，则会在地址栏中特别标记。

**在IE浏览器中存在EV证书的效果：**![image-20211026224146034](https://image.3001.net/images/20211103/1635943684_6182850446f18237e95d6.png!small)

**在IE浏览器中不存在EV证书的效果：**![image-20211026224212313](https://image.3001.net/images/20211103/1635943685_6182850543b7c70361c67.png!small)

我们可以通过绿色表现以对抗钓鱼网站。

## 三、内容安全策略（CSP）

### 1、内容安全策略（CSP）原理

随着web风险逐步严重，缓解跨脚本攻击问题，浏览器引入了内容安全策略（CSP）的概念，

简单来说：开发者明确告诉客户端（指定比较严格的策略和规则），那些外部资源可以加载和执行的，即使攻击者发现漏洞，但是他是没办法注入脚本的。

开发人员可以使用这种工具以各种方式锁定其应用程序，降低内容注入漏洞（如跨站点脚本）的风险，并降低其应用程序执行的权限

### 2、如何启用CSP

通过 HTTP 头信息的Content-Security-Policy的字段

    
    
    Content-Security-Policy: policy

其中policy的描述机器灵活。

 **范例1：**

    
    
    Content-Security-Policy: allow 'self' *.qq.com

浏览器信任来自qq.com及其子域下的内容。

 **范例2：**

    
    
    Content-Security-Policy: allow 'self'; img-src *; media-src qq.com; script-src test.com

浏览器除了信任自身来源外，还可以加载任意域的图片、来自qq.com的媒体文件和来自test.com的脚本，其他的一律拒绝。

## 四、总结

浏览器是互联网的重要入口，在web安全事件层出不穷的现在，浏览器的安全更是重中之重，浏览器安全以同源策略为基础，加深理解同源策略才能把握住浏览器安全的本质，本章节我们详细介绍了同源策略的原理和内容安全策略（CSP）并对浏览器拦截恶意网站的原理进行分析。

