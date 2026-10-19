  
  

原创： 慌得一批  = 合天智汇

  

**0x01.CORS简介**

CORS是一个W3C标准，全称是"跨域资源共享"（Cross-originresource sharing）。

出于安全原因，浏览器限制从脚本中发起的跨域HTTP请求。默认的安全限制为同源策略，即JavaScript或Cookie只能访问同域下的内容。

而CORS允许浏览器向跨源服务器，发出XMLHttpRequest请求，从而克服了AJAX只能同源使用的限制。

 **0x02.分类**

CORS请求分成两类：简单请求（simplerequest）和非简单请求（not-so-simplerequest）

只要同时满足以下两大条件，就属于简单请求。

（1）请求方法是HEAD，GET，POST之一

（2）HTTP的头信息不超出以下几种字段。

Accept

Accept-Language

Content-Language

Last-Event-ID

Content-Type：（只限于三个值application/x-www-form-urlencoded、multipart/form-data、text/plain）

凡是不同时满足上面两个条件，就属于非简单请求。

对于简单请求，浏览器直接发出CORS请求。具体来说，就是在头信息之中，增加一个Origin字段。

如果Origin指定的源，不在许可范围内，服务器会返回一个正常的HTTP回应。如果回应的头信息没有包含Access-Control-Allow-Origin字段，浏览器就会抛出一个错误，被XMLHttpRequest的onerror回调函数捕获。注意，这种错误无法通过状态码识别，因为HTTP回应的状态码有可能是200。

如果Origin指定的域名在许可范围内，服务器返回的响应，会多出几个以Access-Control-开头的字段。

其中最重要的两个是Access-Control-Allow-Origin和Access-Control-Allow-Credentials

Access-Control-Allow-Origin是必须的，它表示可接受跨域的域名

Access-Control-Allow-Credentials是可选的。它的表示是否允许发送Cookie或其他凭据

 **这里要敲重点了，通常是由于** **Access-Control-Allow-Origin** **配置不当从而引发导致跨域问题。**

对于非简单CORS请求，会在正式通信之前，增加一次HTTP查询请求，称为预检请求（preflight）

一旦服务器通过了预检请求，以后每次浏览器正常的CORS请求，就都跟简单请求一样

 **0x03.CORS漏洞测试**

通常，当服务器收到头部带有Origin字段的请求的时候才会配置CORS

所以我们需要发送头部带有Origin的数据包来进行测试

curlhttps://api.artsy.net -H "Origin: http://bbb.com" -I

HTTP/1.1200 OK

Access-Control-Allow-Credentials:true

Access-Control-Allow-Origin:http://bbb.com

....

可以看到Access-Control-Allow-Origin返回的是我们的Origin值

这便意味着可以接受来自http://bbb.com的跨域请求

那很明显这个站点就存在CORS漏洞了

如果http://bbb.com是我们控制的一个网站或者该网站有XSS等漏洞我们便可以利用该漏洞对https://api.artsy.net进行CORS攻击

首先讲恶意js植入http://bbb.com当用户访问时js便在不知不觉中发起跨域请求窃取用户在https://api.artsy.net上的敏感信息或进行敏感操作

利用：

**< script type="text/javascript">**  
---  
**var xhr = new XMLHttpRequest();**  
**xhr.onreadystatechange = function() {**  
**if(xhr.readyState === 4) {**  
**console.log(xhr.responseText);**  
**}**  
**}**  
**xhr.open("GET", " https://api.artsy.net ");**  
**xhr.send();**  
**< /script>**  
  
首先将以上代码保存为1.html

然后用游览器打开1.html并打开控制台

  
![图片.png](https://image.3001.net/images/20181205/1543995210_5c077f4a0e762.png!small)  

这里可以我们可以看到游览器成功的进行了一次跨域请求

控制台输出了https://api.artsy.net的源代码

所以如果https://api.artsy.net包含了用户的敏感信息或进行敏感操作那就可以被攻击者读取到，之后可以再用XMLHttpRequest发送到攻击者的服务器上

可能有的同学就要抬杠了，直接这样请求不是挺正常么

那我们现在把https://api.artsy.net换成https://www.baidu.com看看

很明显，游览器不会让我们这么干

![图片.png](https://image.3001.net/images/20181205/1543995217_5c077f519188a.png!small)  

因为服务器没有返回CORS头，游览器就不会进行跨域请求

 **0x04防御**

（1）如果没有必要就不要开启CORS

### （2）严格限制域白名单，而不是使用*

### （3）尽量避免使用Access-Control-Allow-Credentials

  
  

