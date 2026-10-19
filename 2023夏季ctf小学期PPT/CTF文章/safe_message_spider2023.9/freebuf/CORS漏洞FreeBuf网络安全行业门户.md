### 基础理论：

 **拓展：**

Host

客户端请求的服务器的域名和端口号(其中端口号是可选的，如果没有就根据协议来默认端口号，如http是80，https是443)

Referer

请求来源页面的地址，包括协议、域名、端口号、url参数(不包括hash参数)  
服务器判断请求来源一般用这个字段

Origin

请求来源于哪个站点。只有跨域请求，或者同域的post请求，才会请求头才会携带Origin  
Origin只有协议、域名、端口号，没有url参数

 **同源策略：**

同源策略是一种限制性跨源规范，它限制网站与源域之外的资源交互的能力。
同源策略是多年前定义的，旨在应对潜在的恶意跨域交互，例如一个网站从另一个网站窃取私人数据。 它通常允许一个域向其他域发出请求，但不允许访问响应。

 **生么是Cors？**

跨源资源共享 (CORS) 是一种浏览器机制，可以对位于给定域之外的资源进行受控访问。 它扩展并增加了同源策略 ( [SOP
](https://portswigger.net/web-security/cors/same-origin-policy)) 的灵活性。
然而，如果网站的 CORS 策略配置和实施不当，它也可能带来跨域攻击。 CORS 不能防止跨源攻击，例如 [跨站点请求伪造
](https://portswigger.net/web-security/csrf)( [CSRF
](https://portswigger.net/web-security/csrf))。

 **验证cors漏洞：**

这里我觉得主要是看响应部分

情况一：

Origin中的url和Access-Control-Allow-Origin是一样的，并且Access-Control-Allow-Credentials: true

请求部分

> GET /sensitive-victim-data HTTP/1.1  
> Host: vulnerable-website.com  
> Origin: https://cn-dragon.cn/  
> Cookie: sessionid=...

响应部分

> HTTP/1.1 200 OK  
> Access-Control-Allow-Origin: https://cn-dragon.cn/  
> Access-Control-Allow-Credentials: true  
> ...

情况二：

Origin的值为null，浏览器响应Access-Control-Allow-Origin: null

请求部分

> GET /sensitive-victim-data  
> Host: cn-dragon.cn  
> Origin: null

响应部分

> HTTP/1.1 200 OK  
> Access-Control-Allow-Origin: null  
> Access-Control-Allow-Credentials: true

以上只是简单的判断，如果想了解更详细请参考burpsuite官网提供的内容：[跨域资源共享（CORS）](https://portswigger.net/web-security/cors#what-is-cors-cross-origin-resource-sharing)

### 实操：

 **CORS漏洞**

我们借助的是burpsuite的在线靶场进行操作的，我们找到初级难度

![1690100946_64bce4d2174efeb09b984.png!small?1690100949059](https://image.3001.net/images/20230723/1690100946_64bce4d2174efeb09b984.png!small?1690100949059)

找到对应的漏洞位置，位置是Myaccount这个位置

![1690101290_64bce62a33eb1f15841fa.png!small?1690101293818](https://image.3001.net/images/20230723/1690101290_64bce62a33eb1f15841fa.png!small?1690101293818)

我们抓包分析，添加Origin(这里冒号前不用空格，冒号后的url部分需要空格)，这里发现响应包部分是一样的，证明漏洞存在

![1690102018_64bce90287d1e12f8a9df.png!small?1690102021482](https://image.3001.net/images/20230723/1690102018_64bce90287d1e12f8a9df.png!small?1690102021482)

  

 **具有可信空源的CORS漏洞**

漏洞位置还是同样点，我们将Origin值改为空，我们放包。

![1690106329_64bcf9d9ea3a4949ada55.png!small?1690106333010](https://image.3001.net/images/20230723/1690106329_64bcf9d9ea3a4949ada55.png!small?1690106333010)

  

讲的很浅显，希望各位师父不要介意，如果有大佬有补充的可以在下面补充，一起进步提升谢谢。

  

