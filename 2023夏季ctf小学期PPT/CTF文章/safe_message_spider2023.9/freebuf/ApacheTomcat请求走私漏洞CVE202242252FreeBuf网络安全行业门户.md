## **0x01 概述**

 **Apache Tomcat** 是一个开源的Java Servlet容器和JavaServer
Pages（JSP）容器。它是由Apache软件基金会开发和维护的，是一个轻量级、快速、可扩展的Web服务器，用于执行Java
Servlet和JavaServer Pages技术。

Tomcat是一个独立的服务器，它可以用作Java应用程序的Web服务器，也可以作为Servlet容器集成到其他Web服务器（例如Apache
HTTP服务器）中。它可以处理HTTP请求，并将它们传递给相应的Servlet或JSP进行处理，然后将结果返回给客户端。

Tomcat提供了许多功能，包括 **连接池、会话管理、安全性、Web应用程序部署、负载均衡等**
。它是Java企业级Web应用程序的常用部署环境，广泛用于开发和部署Java Web应用程序和服务。

笔者通过对数百个真实项目引入组件的分析选出了Tomcat组件的常见漏洞进行分析。本次分析的是 **CVE-2022-42252**
。该漏洞是Tomcat的rejectIllegalHeader配置为False时，Tomcat 不会拒绝包含无效 Content-Length
标头的请求，如果 Tomcat 位于反向代理后面，而该反向代理也无法拒绝具有无效标头的请求，则可能会发生请求走私攻击。

##  **0x02 组件使用场景**

tomcat-embed-core 是 Apache Tomcat 项目的一部分，它是用于在 Java 应用程序中嵌入 Tomcat
内核的库。tomcat-embed-core 允许你将 Tomcat 作为嵌入式容器嵌入到你的 Java 应用程序中，以便在应用程序内部运行 Web 应用。

##  **0x03 漏洞信息**

 **3.1 漏洞简介**

 **漏洞名称：** 请求走私漏洞

 **漏洞编号：** CVE-2022-42252

 **漏洞类型：** CWE-444 HTTP 请求/响应走私

 **CVSS评分：** CVSS v3.1：7.5

 **漏洞危害等级：** 高危

 **3.2 漏洞概述**

该漏洞是Tomcat的rejectIllegalHeader配置为False时，Tomcat 不会拒绝包含无效 Content-Length
标头的请求，如果 Tomcat 位于反向代理后面，而该反向代理也无法拒绝具有无效标头的请求，则可能会 **发生请求走私攻击** 。

 **3.3 漏洞利用条件**

DefaultServlet的readOnly属性为false（默认为true）。并且当存在自定义的静态文件形式的错误页面时，可以覆盖错误页面。

 **3.4 漏洞影响版本**

Apache Tomcat 10.1.0-M1 ~ 10.1.0

Apache Tomcat 10.0.0-M1 ~ 10.0.26

Apache Tomcat 9.0.0-M1 ~ 9.0.67

Apache Tomcat 8.5.0 ~ 8.5.52

 **3.5 漏洞分析**

 **1.HTTP请求走私**

HTTP 请求走私是一种干扰网站处理从一个或多个用户接收的 HTTP
请求序列的方式的技术。请求走私漏洞本质上通常很严重，它允许攻击者绕过安全控制，获得对敏感数据的未经授权的访问，并直接危害其他应用程序用户。

当前端服务器将 HTTP 请求转发到后端服务器时，它通常会通过同一后端网络连接发送多个请求，因为这样的效率和性能要高得多。该协议非常简单：HTTP
请求被一个接一个地发送，接收服务器解析 HTTP 请求标头以确定一个请求从哪里结束以及下一个请求从哪里开始：

![图片](https://image.3001.net/images/20230901/1693536145_64f14f91581f02e8e26d6.png!small)

在这种情况下，前端和后端系统就请求之间的边界达成一致至关重要。否则，攻击者可能能够发送不明确的请求，前端和后端系统会以不同的方式解释该请求：

![图片](https://image.3001.net/images/20230901/1693536156_64f14f9ce2f576c09691b.png!small)

在这里，攻击者导致其前端请求的一部分被后端服务器解释为下一个请求的开始。它有效地添加到下一个请求之前，因此可能会干扰应用程序处理该请求的方式。这是请求走私攻击，可能会造成灾难性的后果。

HTTP 规范提供了两种不同的方式来指定请求的结束位置：Content-Length和Transfer-Encoding。

在两个HTTP header都存在的时候，根据HTTP规范应忽略Content-Length标头。但是若某些服务器不支持Transfer-Encoding标头或者标头被混淆，服务器未处理Transfer-Encoding标头就会产生请求走私漏洞。

进行HTTP请求走私攻击可以将Content-Length和Transfer-Encoding两个heade放在单个HTTP请求中，以便前端和后端服务器以不同的方式处理请求。

 **2.CVE-2022-42252**

nvd上该漏洞的信息可以看出漏洞是在rejectIllegalHeader为false的配置下，Tomcat不会拒绝 Content-Length标头造成的。

![图片](https://image.3001.net/images/20230901/1693536172_64f14fac2e396dd6a5b50.png!small)

查看补丁代码。

![图片](https://image.3001.net/images/20230901/1693536185_64f14fb947375592b90d0.png!small)![图片](https://image.3001.net/images/20230901/1693536253_64f14ffddc3f6d8302c6a.png!small)

发现在headers的Content-Length标头的值中含有控制字符的时候会将该行header去除，然后正常解析。

并且在补丁后的skipLine函数，如果需要去除的header为Content-Length，那么会将rejectThisHeader设为true，不去除该header，而是抛出一个异常。

可以猜想，如果前端的服务器没有拒绝这个非法的Content-Length标头，而修复前的Tomcat后端会去除该header进行一个正常的响应，这也就会造成请求走私的可能。

 **3.6 漏洞复现**

修改conf/server.xml的connect配置如下：

![图片](https://image.3001.net/images/20230901/1693536267_64f1500b44aeb33ae96d3.png!small)

发送Poc：

POST / HTTP/1.1  
Host::8080  
Cache-Control: max-age=0  
Upgrade-Insecure-Requests: 1  
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/110.0.5481.78 Safari/537.36  
Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7  
Accept-Encoding: gzip, deflate  
Accept-Language: zh-CN,zh;q=0.9  
Content-Length: 12\x00073 # \x0007需要hex模式下修改

查看对Content-Length的处理。

removeHeader执行前：

![图片](https://image.3001.net/images/20230901/1693536279_64f1501726905f38eefc4.png!small)

removeHeader执行后：

![图片](https://image.3001.net/images/20230901/1693536290_64f150225238673faeb38.png!small)

随后会进行正常的处理并返回响应码200。根据RFC7230的规定如果Content-Length
头部的值不符合规范，或者无法正常的解析头部，应该返回一个400的错误响应。

![图片](https://image.3001.net/images/20230901/1693536302_64f1502e45aa8932c0bea.png!small)

 **3.7 修复方法**

漏洞修复的办法有如下几种：

  *  **升级Tomcat至该漏洞不存在的版本**

更新 Apache Tomcat >= 10.1.1

更新 Apache Tomcat >= 10.0.27

更新 Apache Tomcat >= 9.0.68

更新 Apache Tomcat >= 8.5.83

Tomcat官方的修复方案是在skipLine方法中多了一次验证，如果是因为当前处理的header为Content-Length就将rejectThisHeader设为true，不去除本次header而是抛出一个异常并返回一个400错误页面。

![图片](https://image.3001.net/images/20230901/1693536313_64f1503998a3f0a57d32f.png!small)

  

![图片](https://image.3001.net/images/20230901/1693536323_64f150433e5eeb6b32894.png!small)

  *  **将rejectIllegalHeader设置为true**

8.5.x版本rejectIllegalHeader的默认配置为false，设置为true在处理非法header的时候便会报错。

  *  **使用WAF等拦截**

由于该漏洞是需要tomcat作为后端服务器，所以可以在前端处理该HTTP请求的时候便对请求进行拒绝处理或者拦截等操作。

