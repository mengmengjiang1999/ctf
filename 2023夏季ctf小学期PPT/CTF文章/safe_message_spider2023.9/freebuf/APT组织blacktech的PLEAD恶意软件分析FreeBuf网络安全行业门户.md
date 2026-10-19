原创： piku Yoake  合天智汇

  
  

> 翻译文章
>
> 原文链接为
>
> https://blog.jpcert.or.jp/2018/06/plead-downloader-used-by-blacktech.html

  

在过去的一篇文章中，我们介绍了APT组织BlackTech使用的TSCookie恶意软件。据悉，该组织还使用了其他类型的恶意软件“PLEAD”。PLEAD有两类——RAT（远程访问工具）和Downloader(下载程序)。RAT的命令运行基于C＆C服务器提供。（请参阅https://www.lac.co.jp/lacwatch/people/20180425_001625.html了解更多信息）另一方面，PLEAD
Downloader的下载模块与TSCookie在内存上运行的方式如出一辙。

本文详细介绍了PLEAD下载器的工作流程。

  
![aaf3b37e13f28c75dfd87a42f5dace44.jpg](https://image.3001.net/images/20180822/1534902834_5b7cc23273889.jpg!small)  

首先PLEAD Downloader从某些站点下载经过RC4加密的模块。图1显示了从服务器下载的加密文件的示例。

  
![2173062a252ad31836ac639c187bb163.jpg](https://image.3001.net/images/20180822/1534902927_5b7cc28ff1782.jpg!small)  

下载文件的前20h是用于解码文件的RC4密钥。解码后，您可以找到模块（以下称为“PLEAD模块”），C＆C服务器，加密密钥等。图2是解密文件的示例。

  

PLEAD下载程序加载PLEAD模块（包含在解密数据中）并执行它。该模块不会保存为文件，只会存在于内存中。以下部分将介绍PLEAD模块的详细信息。

  

PLEAD模块基于C＆C服务器提供的命令运行。与C＆C服务器之间的通信采用RC4加密，然后使用LZO进行压缩。RC4加密密钥是由其自身生成的密钥和从C＆C服务器发送的密钥的组合。图3描述了PLEAD模块执行的通信流程。

  
![5311c7a497f124e8b9456a88ec63990c.jpg](https://image.3001.net/images/20180822/1534903105_5b7cc34163c59.jpg!small)  

PLEAD模块首先与C＆C服务器共享RC4密钥。下面是在通信开始时发送的HTTP
GET请求的示例。Cookie标头包含加密的RC4密钥。在Cookie标头中发送的数据中，“D”和“E”互换。有关数据格式，请参阅附录A中的表A-1和A-2。

  1. `GET /index.php?id=1577061168 HTTP/1.1`

  2. `Cache-Control: no-cache`

  3. `Accept: */*`

  4. `Pragma: no-cache`

  5. `Cookie: 800809D6411C6E2629001900A92309EB26192117C5A59F306E207A8993A2F20121FC3B42B6DF693838`

  6. `User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022)`

  7. `Host: [host name]`

  8. `Connection: Keep-Alive`

用于数据加密的RC4密钥长度为32字节，分为5个块（4字节* 4 + 16字节*
1）。密钥中的第一个块（图3中的Key1）包含在PLEAD模块的配置中。在HTTP
GET请求中将第二个和第三个块（Key2和3）设置为0。第四个块（Key4）是随机生成的，并在URL中的“id”之后插入。第五个块（Key5）基于Key4值生成。

首先发送的数据包含Key2值。使用该值，接收方服务器会加密Key3值并将其发送到C＆C服务器。数据格式在附录A的表A-3和A-4中描述。这样，生成RC4密钥并用于随后的通信。

下面是解码数据的Python脚本的一部分。

  1. `def decode(key1, key2, key3, key4, data, lzo_header):`

  2. ` rc4_key = key1 + pack("III", key2, key3, key4)`

  3. ` for i in xrange(4):`

  4. ` key4 = ROR(key4 + 1, 5)`

  5. ` rc4_key += pack("I", key4)`

  6. ` dec = rc4(data, rc4_key)`

  7. ` try:`

  8. ` return lzo.decompress(lzo_header + dec)`

  9. ` except:`

  10. ` sys.exit("[!] Lzo decompress error.")`

共享RC4密钥后，PLEAD模块使用HTTP POST请求发送有关受感染主机的信息。数据格式与附录A中的表A-1所示相同。

  1. `POST /index.php?id=2852129559 HTTP/1.1`

  2. `Content-Type: application/x-www-form-urlencoded`

  3. `Accept: */*`

  4. `User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022)`

  5. `Host: [host name]`

  6. `Content-Length: [data size]`

  7. `Connection: Keep-Alive`

  8. `Cache-Control: no-cache`

  9. `[data]`

数据本身包含受感染主机的主机名，操作系统版本，IP地址，用户帐户名。图4是解码数据的示例。

  
![4b7ae2d16a72eeeaa48e0988bdf5d7de.jpg](https://image.3001.net/images/20180822/1534903202_5b7cc3a217de5.jpg!small)  

之后，将从C＆C服务器发送命令。PLEAD模块可以执行以下功能。

  * 泄露文件列表

  * 任意shell命令执行

  * 上传/下载文件

  * 文件操作 （有关命令的详细信息，请参阅附录B中的B-1）

##  

  

正如我们之前所描述的，该组织一直在使用各种恶意软件对日本境内进行攻击。由于这次攻击活动可能还会继续，JPCERT将密切关注相关消息。

附录C中我们列出了本文中描述的样本的哈希值。最近确认的一些C＆C服务器也列在附录D中。请确保您的设备都没有访问这些主机。

附录A PLEAD模块通信数据

  
![2d55eb2f5f1799e5b6db3e349ef0b6ab.jpg](https://image.3001.net/images/20180822/1534903229_5b7cc3bda22b8.jpg!small)  

附录B PLEAD模块命令

  
![7a082ce0bfd14e665fc472ed1b026e0f.jpg](https://image.3001.net/images/20180822/1534903236_5b7cc3c4d0070.jpg!small)  

##  

附录C样本的SHA-256哈希值

PLEAD

  * bc2c8cc9896cdd5816509f43cb5dca7433198251d754a997a70db7e8ed5cca40

  * a26df4f62ada084a596bf0f603691bc9c02024be98abec4a9872f0ff0085f940

  * 2ddb2030ab3373b9438102b541aa4623b7dfee972850dcef05742ecbe8982e22

  * eec3f761f7eabe9ed569f39e896be24c9bbb8861b15dbde1b3d539505cd9dd8d

PLEAD模块

  * 23f554cc5bea9d4ccd62b0bbccaa4599f225ebce4ad956a576cc1a9b2a73dc15

##  

附录D C＆C服务器列表

em.totalpople.infooffice.panasocin.comgstrap.jkub.comwoc.yasonbin.info210.71.209.206

  

