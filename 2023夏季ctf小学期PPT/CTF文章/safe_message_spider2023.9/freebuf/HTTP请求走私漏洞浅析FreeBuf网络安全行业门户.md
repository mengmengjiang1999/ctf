## **0x00 前言**

HTTP请求走私漏洞(HTTP Request Smuggling)是发生 **协议层**
的一种攻击，最早于2005年就被发现并提出。漏洞发生的主要原因是不同的服务器，对于RFC标准的具体实现不一而导致的。

##  **0x01 漏洞原理**

HTTP 1.1协议相对于1.0主要引入了两个新的特性: **Keep-Alive** 和 **pipline**

1、Keep-Alive特性具体是指在HTTP请求头中，添加一个参数

    
    
    Connection: Keep-Alive
    

告诉服务器在收到这个请求后不要关闭连接，后面再次发起请求时，继续使用这个TCP连接。

2、pipline特性是指在一次TCP连接中，可以连续不断地发送多个HTTP请求，而不必等待服务器响应。服务器会根据顺序进行处理。

有了这两个特性之后，HTTP 1.1相对于 HTTP 1.0来说，传输效率更高，如今HTTP 1.1也应用最为广泛。

在RFC 2616中规定，一个完整的数据包中需要在请求头部分包含”Content-Length”或者”Transfer-Encoding”来对数据包的长度进行说明。

1、Content-Length: 指明数据包的内容长度，一个字符长度为1，回车(\r\n)长度为2。如：

![1618801806_607cf48e13c727442311f.png!small?1618801808017](https://image.3001.net/images/20210419/1618801806_607cf48e13c727442311f.png!small?1618801808017)

这个数据包的请求长度为10:

![1618801804_607cf48c051b990f2f456.png!small?1618801808017](https://image.3001.net/images/20210419/1618801804_607cf48c051b990f2f456.png!small?1618801808017)

2、Transfer-Encoding: 当值为chunked时，服务器在读取到

    
    
    0\r\n\r\n
    

后就会认为该请求已经结束。

而之后的内容会存在于服务器的缓存中，和下一个请求一起发送给服务器。

HTTP请求走私漏洞的核心就在于前端和后端对于请求的长度判断不一而引起的。

如当前端使用Content-Length来判断，而后端使用Transfer-Encoding:chunked来判断时，我们构造一个请求如:

![1618801804_607cf48cee17bb8d55b15.png!small?1618801808018](https://image.3001.net/images/20210419/1618801804_607cf48cee17bb8d55b15.png!small?1618801808018)

前端认为请求长度为6，会将所有内容转发给后端，而后端读到”0\r\n\r\n”后就认为请求已经结束，因此最后一个”G”就会留到缓存服务器中，被拼接到下一个请求的开始，如

![1618801805_607cf48da213a12988962.png!small?1618801808018](https://image.3001.net/images/20210419/1618801805_607cf48da213a12988962.png!small?1618801808018)

这样当下一个正常用户发起请求时，就会返回错误，因为服务器并不认得”GPOST”是什么请求方式。

这就是一个简单的HTTP请求走私攻击的例子。

上面这个例子中，前端使用Content-Length判断，后端使用Transfer-Encoding:chunked判断，因此属 **于CL-TE**
类型，与之对应的还有 **TE-CL** 、 **TE-TE** 。

## 0x02 漏洞复现

利用工具:Burpsuite

需要在Repeater中关闭更新Content-Length

![1618801805_607cf48d3b5dade304320.png!small?1618801808018](https://image.3001.net/images/20210419/1618801805_607cf48d3b5dade304320.png!small?1618801808018)

以CL-TE为例 :对于靶场

正常访问:

![1618801804_607cf48cebe541b836673.png!small?1618801808018](https://image.3001.net/images/20210419/1618801804_607cf48cebe541b836673.png!small?1618801808018)

开启抓包，将请求修改为POST方式

构造请求

然后Send to Repeater

![1618802064_607cf5901fef9f14b59b3.png!small?1618802065743](https://image.3001.net/images/20210419/1618802064_607cf5901fef9f14b59b3.png!small?1618802065743)

当第二次放包的时候会返回

 **"Unrecognized method GPOST"**

![1618802063_607cf58fc4a4f91df90e7.png!small?1618802065745](https://image.3001.net/images/20210419/1618802063_607cf58fc4a4f91df90e7.png!small?1618802065745)

## 0x03 扩展

根据以上原理，我们可以更改下一个正常访问用户的请求内容，包括Cookie信息等。因此可以扩展出危害更大的攻击，如获取服务器敏感信息、获取用户登录信息、能交互的反射型XSS等。

## 0x04 缓解措施

对于前端，对所有请求进行规范化，避免模糊请求。

对于后端，拒绝掉一切模糊请求。

  

  

  

