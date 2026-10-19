  

### 【正文】

网址（URL）：[https://college.360.cn/](https://college.360.cn/)

在浏览器地址栏中输入以上网址（360网络安全学院官网），即向官网发起一个GET请求：

1  |  GET / HTTP/1.1  
---|---  
2  |  Host: college.360.cn  
3  |  Connection: keep-alive  
4  |  Cache-Control: max-age=0  
5  |  Upgrade-Insecure-Requests: 1  
6  |  User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36  
7  |  Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8  
8  |  Accept-Encoding: gzip, deflate, br  
9  |  Accept-Language: zh-CN,zh;q=0.9  
10  |
Cookie:Qs_lvt_266522=1534056729;__guid=268759395.2694206631754367500.1534056730203.3916;MEIQIA_VISIT_ID=18gUSffgCjuCTd9bP94pAFeTIlv;
MEIQIA_EXTRA_TRACK_ID=14jVCPbbVDiHtXt4gIvpZx3MGsm;__huid=11AvprrzOOJOJ5JWx/cL2XKAzfGM+TH2t5SV8TIpxWyDM=;Qs_pv_266522=3561761371268066000%2C3748820700298938000;test_cookie_enable=null  
  
响应包：

1  |  HTTP/1.1 200 OK  
---|---  
2  |  Server: nginx/1.9.15  
3  |  Date: Sun, 12 Aug 2018 06:58:58 GMT  
4  |  Content-Type: text/html  
5  |  Last-Modified: Mon, 06 Aug 2018 11:27:20 GMT  
6  |  Connection: close  
7  |  ETag: W/"5b683098-47ee"  
8  |  Content-Length: 18414  
|  
9  |  <html lang="zh-cn">  
10  |  ……  
11  |  </html>  
  
### 【请求包中关键点】

1、请求方法。

常见的请求方法有GET、POST，此次采用GET方法请求；紧跟着的“/”表示请求的官网所在的根目录内容；最后的HTTP/1.1表示1.1版本，详细内容可见《RFC
2616 - Hypertext Transfer Protocol -- HTTP_1.1》标准。

2、请求主机名。

本行表示请求的主机为“college.360.cn”。

3、浏览器种类。

本行表明此次请求的浏览器种类，用于表明身份。从这里可看出操作系统、浏览器及版本，如下图所示。

4、cookie信息。

HTTP协议是无状态的，每次连接都需要进行身份验证（比如访问登录后的页面），为了减少用户重复输入验证信息，提高用户访问体验，采用cookie方式进行验证。用户登录成功后，服务器会给客户端设定特有的cookie信息，随后的访问中，将自动携带此cookie，以便服务器识别、分辨用户身份。

如果cookie在有效期内，被劫持，然后冒充使用，那么攻击者无需知道用户的登录信息，也可像合法用户一样访问相关授权页面和功能。

### 【响应包中关键点】

状态码。

HTTP访问的状态码，表明了此次访问的状态，常见的状态码如下：

服务器信息。

本行描述了服务的名称及版本信息。

响应资源的类型与字符集。

不同的类型，浏览器会采用不同的解析方式。

页面更新时间。

本行表示此页面最后更新日期和时间，采用GMT（格林尼治平时）格式。

响应体的长度。

此次响应体的长度。

### 【小结】

通过了解web请求及响应的基础内容，对后续web测试（如模糊测试）奠定基础，除了本文涉及的内容外，web请求及响应中，还包括：referer、X-Power-By、set-cookie等内容，更详细的内容除了查询《RFC 2616 - Hypertext Transfer Protocol --HTTP_1.1》标准外，也可在360网络安全学院的“web安全”课程中找到更精、更全的内容。

  

###

 **  
  
  
**

