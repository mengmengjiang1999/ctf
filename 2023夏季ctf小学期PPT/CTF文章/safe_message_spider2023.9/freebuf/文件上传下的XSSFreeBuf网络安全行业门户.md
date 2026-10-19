## **背景** ：

在很多环境下都会遇到任意文件上传，但文件都被存储到oss服务器上。然而通常在此类文件上传中，文件名不可控，通常会随机命名，但是文件后缀可以随意构造。在此类oss利用上，通常采用挂黑页或引用了js文件，上传恶意js文件，去盗取用户信息等。

### 一、前言

在某次测试中，发现在线网页聊天存在上传文件功能，可以上传任意文件。但是服务端只对txt、html、js脚本语言进行解析。

![](https://image.3001.net/images/20210910/1631266821_613b28050405eec860100.png!small)![访问txt的页面](https://image.3001.net/images/20210910/1631266832_613b28104684a0c168cdb.png!small)

但在此处发现上传的文件名，会在页面上展示，而文件在存入服务端时会随机命名，但此处文件后缀可控，可以自定义任何文件后缀。

![](https://image.3001.net/images/20210910/1631266849_613b2821d6d45768fc5e2.png!small)

![](https://image.3001.net/images/20210910/1631266867_613b283322e3eb3c29420.png!small)

于是有了以下尝试：

常规XSS漏洞会产生在表单文本输入，此处我们可控的聊天文本框不存在XSS漏洞，但是此处文件名在页面上展示且在服务端随机编码后在前端”a“标签中，如果构造恶意的文件后缀，即可触发存储型XSS漏洞。

![](https://image.3001.net/images/20210910/1631266881_613b28415efe1ac139e09.png!small)

### 二、触发XSS漏洞

利用xss常规操作，闭合a标签，去触发script。

问题1：发现script语句闭合成功，但页面并未触发，原因在于alert函数并未被解析。此处猜想alert函数在传入时被当作文本处理。

![](https://image.3001.net/images/20210910/1631266897_613b28516f0e3030b35dd.png!small)

  

问题2：当我们正常传入分号”；“时，文件后缀会被截断，原因在于在我们上传文件时，文件名是以分号截断取值，所以传入的参数不能包含分号。

![](https://image.3001.net/images/20210910/1631266967_613b2897b84ba741e7f37.png!small)

所以在这里采最后用Img src的方式，base64编码绕过调用script，去执行。（base64编码绕过分号限制）。

    
    
    <img src=x onerror=eval(atob('dmFyIHMgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdzY3JpcHQnKTtzLnR5cGUgPSAndGV4dC9qYXZhc2NyaXB0JztzLnRleHQgPSAnYWxlcnQoMSk7Jztkb2N1bWVudC5ib2R5LmFwcGVuZENoaWxkKHMpOw=='))>

![](https://image.3001.net/images/20210910/1631266990_613b28ae1e865e50b7ddd.png!small)![](https://image.3001.net/images/20210910/1631267000_613b28b8819383d440764.png!small)

### 三、总结

关于文件上传导致的XSS漏洞还有很多，例如：图片内插入js代码解析，上传图片类html代码解析等等，此处不再一一赘述。任何用户可控的地方都可能存在漏洞，无论文件上传是否上传到OSS服务器都需要对用户可控参数进行严格的过滤。

  

  

