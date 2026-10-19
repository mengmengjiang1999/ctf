![1619511876_6087ca44d9c403d42344a.png!small](https://image.3001.net/images/20210427/1619511876_6087ca44d9c403d42344a.png!small)

1.首先我们要知道什么是X-Forwarded-For

X-Forwarded-For 是一个 HTTP 扩展头部。HTTP/1.1（RFC 2616）协议并没有对它的定义，它最开始是由 Squid
这个缓存代理软件引入，用来表示 HTTP 请求端真实 IP。如今它已经成为事实上的标准，被各大 HTTP 代理、负载均衡等转发服务广泛使用，并被写入
[RFC 7239](http://tools.ietf.org/html/rfc7239)（Forwarded HTTP Extension）标准之中。

X-Forwarded-For 请求头格式非常简单，就这样：

    
    
    X-Forwarded-For: client, proxy1, proxy2

可以看到，XFF 的内容由「英文逗号 + 空格」隔开的多个部分组成，最开始的是离服务端最远的设备 IP，然后是每一级代理设备的 IP。

如果一个 HTTP 请求到达服务器之前，经过了三个代理 Proxy1、Proxy2、Proxy3，IP 分别为 IP1、IP2、IP3，用户真实 IP 为
IP0，那么按照 XFF 标准，服务端最终会收到以下信息：

    
    
    X-Forwarded-For: IP0, IP1, IP2

Proxy3 直连服务器，它会给 XFF 追加 IP2，表示它是在帮 Proxy2 转发请求。列表中并没有 IP3，IP3 可以在服务端通过 Remote
Address 字段获得。我们知道 HTTP 连接基于 TCP 连接，HTTP 协议中没有 IP 的概念，Remote Address 来自 TCP
连接，表示与服务端建立 TCP 连接的设备 IP，在这个例子里就是 IP3。

Remote Address 无法伪造，因为建立 TCP 连接需要三次握手，如果伪造了源 IP，无法建立 TCP 连接，更不会有后面的 HTTP
请求。不同语言获取 Remote Address 的方式不一样，例如 php 是 $_SERVER["REMOTE_ADDR"]，Node.js 是
req.connection.remoteAddress，但原理都一样。

2.当随意用一个账号登录时，显示的乱码，采用抓包进行看一下![1619511914_6087ca6aca66179cfd825.png!small](https://image.3001.net/images/20210427/1619511914_6087ca6aca66179cfd825.png!small)

3.X-Forwarded-For一般是不会被抓包得到的，在repeater中进行重发，发现响应包显示我们当前的IP被记录![1619511923_6087ca73a97223c35c97c.png!small](https://image.3001.net/images/20210427/1619511923_6087ca73a97223c35c97c.png!small)

4.添加X-Forwarded-For并把其值添加为随意的IP，响应包中的IP也随之改变，猜测服务器后端可能是获取 X-Forwarded-For数据![1619511936_6087ca80dea5390bc388f.png!small](https://image.3001.net/images/20210427/1619511936_6087ca80dea5390bc388f.png!small)

5.在注入将X-Forwarded-For的值改为*，并将抓取的包放入txt文档中，使用sqlmap进行探测![1619511949_6087ca8dc35747e6380f3.png!small](https://image.3001.net/images/20210427/1619511949_6087ca8dc35747e6380f3.png!small)![1619511954_6087ca92bd538603ca34c.png!small](https://image.3001.net/images/20210427/1619511954_6087ca92bd538603ca34c.png!small)![1619511958_6087ca96936419f1c1c0a.png!small](https://image.3001.net/images/20210427/1619511958_6087ca96936419f1c1c0a.png!small)

6.得到最后的用户名和密码登录即可得到KEY![1619511969_6087caa1543a383476688.png!small](https://image.3001.net/images/20210427/1619511969_6087caa1543a383476688.png!small)![1619754426_608b7dba715ac2e2b0f0f.png!small](https://image.3001.net/images/20210430/1619754426_608b7dba715ac2e2b0f0f.png!small)

