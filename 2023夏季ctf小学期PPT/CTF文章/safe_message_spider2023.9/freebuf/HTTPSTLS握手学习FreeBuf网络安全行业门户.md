## HTTPS

超文本传输安全协议(HyperText Transfer Protocol Secure，HTTPS;)常称为HTTP over TLS 、HTTP
over SSL 、HTTP Secure是一种通过计算机网络进行安全通信的传输协议。HTTPS经由HTTP进行通信，利用 **SSL/TLS**
来加密数据包(SSL/TLS也可以用在其他协议上FTP --> FTPS,SMTP-->
SMTPS)。目的主要为了，提供对网站服务器的身份验证，保护交换资料的隐私与完整性。HTTPS使用443端口，而HTTP使用80端口。

TLS(Transport Layer Security)传输层安全性协议，

TLS的前身是SSL(Secure Sockets Layer)安全套接层

SSL 1.0 未公开、 2.0 3.0 分别在2011年 2015年弃用 从1999年出现的

TLS 1.0 到现在的2018年 TLS 1.3(详细内容可以参考RFC 8446)

对于HTTPS来说它并不是一个单独的协议，而是对工作在一加密连接(TLS、SSL)上的常规HTTP协议称呼。HTTP协议和安全协议同属于应用层,但其实安全协议具体位置在HTTP之下，传输层之上。

SSL/TLS协议也有一个开源实现 **OpenSSL** 。linux、Mac自带OpenSSL，Windows需要下载安装：[Win32/Win64
OpenSSL Installer for Windows - Shining Light Productions
(slproweb.com)](https://slproweb.com/products/Win32OpenSSL.html)使用openSSL生成私钥公钥命令：
生成私钥 ：openssl genrsa -out my.key 生成公钥： openssl rsa -in my.key -pubout -out
my.pem 生成之后会有个CA证书的自签名。
TLS是由若干不同职责的模块组成，比较常用的有握手协议、变更密码规范协议、警报协议、记录协议![image-20211020123454623](https://image.3001.net/images/20211020/1634708954_616faddadddec81a1ebae.png!small)

从体系结构图可以看出，SSL/TLS协议可分为两层：握手协议、记录协议

 **握手协议** (Handshake
Protocol)是用来协商会话参数(会话密钥)，建立在SSL记录协议之上。用于在实际传输数据前，双方进行身份验证、协商加密算法、交换会话密钥，用于后续的混合加密系统。

 **变更密码规范协议** (Change Cipher Spec
Protocol)，是一个非常简单的"通知"。告诉对方，接下来的数据将使用加密保护，再次之前的数据都是明文。

 **警报协议** (Alert Protocol)，向对方发出警报信息，类似HTTP的状态码。如protocol_version
就是不支持旧版本，bad_certificate证书有问题，收到警报后可以选择继续，或者终止连接。

 **记录协议** (Record
Protocol)，建立在可靠传输之上，为高层协议提供数据封装，压缩以及加密等基本功能的支持。保证连接的机密性和完整性。其他子协议都需要通过记录协议发出。但多个记录协议数据可以在一个TCP包里一次性发出，不需要TCP那样返回ACK。

### HTTPS成本

虽然HTTPS安全性高，但是成本也就上来了，申请证书需要费用，加解密计算降低了访问速度。现在更多的做法是，无关紧要的页面还是使用HTTP，只有包含敏感数据的请求才使用HTTPS。

# HTTPS的通信

HTTPS通信可以分为3大阶段: 1、TCP的3次握手 2、TLS的连接 3、HTTP请求和响应

TLS握手过程： 下图每个框都是一个记录，多条记录组成TCP包发送。所以最多要经过2RTT(4个消息)，才可以完成握手。然后才能发送HTTP报文。

![image-20211020124828050](https://image.3001.net/images/20211020/1634708956_616faddc3950571f0a09a.png!small)

    
    
    TLS握手总是以ClientHello 消息开始。

但是TLS握手可以分为两种方式：使用RSA做密钥交换和ECDHE做密钥交换。

### ECDHE握手

在TCP成功建立连接后。客户端先发送一个"Client
Hello"消息![image-20211020125224537](https://image.3001.net/images/20211020/1634708958_616fadde11bc3ff56a46d.png!small)

![image-20211020125245622](https://image.3001.net/images/20211020/1634708960_616fade000bcbbe5d1f7b.png!small)

Client Hello消息包包括：客户端的版本号、支持的密码套件，还有一个 **随机数(Client Random)** 由于后续生成会话密钥。

![image-20211020125735922](https://image.3001.net/images/20211020/1634708961_616fade1771c993db0fcf.png!small)

![image-20211020130357997](https://image.3001.net/images/20211020/1634708962_616fade27eb23fcbbec6c.png!small)

在1的时候 服务器收到客户端的Hello保留客户端的随机数(Client Random) ，也会返回一个的server
Hello里面也有一个随机数(Server Random)，然后从客户端列表中选择一个要使用Cipher
Suites(密码套件)![image-20211020131310227](https://image.3001.net/images/20211020/1634708963_616fade349b95f55ad9ca.png!small)

服务端为了证明自己的身份，把证书也发给客户端(Server Certificate消息)。

![image-20211020131653035](https://image.3001.net/images/20211020/1634708964_616fade40c2c9d4a1e202.png!small)

因为服务器选择了ECDHE算法，然后会发送Server Key Exchange 消息里面有服务器公钥(Server Params)。

![image-20211020131733270](https://image.3001.net/images/20211020/1634708964_616fade4ce03aa4f9136f.png!small)

之后是Server Hello Done 消息，打招呼完毕。

![image-20211020131819132](https://image.3001.net/images/20211020/1634708965_616fade5880dc85bdae92.png!small)

此时第一个RTT就结束了(一共两个TCP数据包，后面服务器发送的子协议都使用记录协议一起发送给了)。此时客户端和服务器通过明文共享了三个信息(Client
Random 、 Server Random 、Server Params)

然后客户端按照密码套件的要求，也生成一个客户端公钥(Client Params)，用Client Key Exchange 消息发送给服务器。

此时客户端和服务器都拿到了密钥交换算法的两个参数(Client Params 、Server Params)用ECDHE算法生成一个"Pre-Master"(预主密钥，也是个随机数)。 现在客户端和服务器有了三个随机数Client Random、Server Random、Pre-Master，通过这三个生成加密会话的主密钥Master-Secret(48字节)。但是这还不是最后的会话密钥，还要用主密钥派生出会话密钥。最后双方个发一个Change Cipher
Spec，然后再发一个Finished消息。把之前发送的数据做一个摘要，加密一下给对方验证。就完了。

###  **RSA握手：**

大体流程没有变只是"Pre-Master"(预主密钥)，不再需要算法生成，而是客户端直接生成随机数，然后用服务器的公钥，通过"Client Key
Exchange"消息发送给服务器。服务器在用私钥解密，这样子也实现了共享三个随机数，生成主密钥。

### 总结一下就是：

1、HTTPS协议，先进行TCP三次握手，然后执行TLS握手，才能建立安全连接

2、TLS握手过程中产生3个随机数，由此生成主密钥

3、Hello消息交换随机数、KEY Exchange 交换 pre-Master

4、Change Cipher Spec 改变密码规范之前传输都是明文，之后都是通过对称密钥加密的密文。

