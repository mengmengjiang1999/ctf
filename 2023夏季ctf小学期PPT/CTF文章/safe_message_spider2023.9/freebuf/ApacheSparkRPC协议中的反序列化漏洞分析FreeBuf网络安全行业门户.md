***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **在前一阵，Spark官方发布了标题为《CVE-2018-17190: Unsecured Apache Spark standalone
executes user code》的安全公告。**

公告中指明漏洞影响版本为全版本，且没有标明已修复的版本，只有相关缓解措施。

官方缓解措施如下：在任何未受到不必要访问保护的Spark单机群集上启用身份验证，例如通过网络层面限制。使用spark.authenticate和相关的安全属性。

查询了相关文档，spark.authenticate是RPC协议中的一个配置属性，此参数控制Spark RPC是否使用共享密钥进行认证。

## Spark RPCS

park RPC 是一个自定义的协议。底层是基于netty4开发的，相关的实现封装在spark-network-common.jar和spark-core.jar中，其中前者使用的JAVA开发的后者使用的是scala语言。

协议内部结构由两部分构成header和body，header中的内容包括:整个frame的长度（8个字节），message的类型（1个字节），以及requestID（8个字节）还有body的长度（4个字节）

body根据协议定义的数据类型不同略有差异.

![1.jpg](https://image.3001.net/images/20190118/15477805629057.jpg!small)

RpcRequest消息类型的body大致由两部分构造，前半部分包含通信双方的地址和端口以及名字信息，接下来就是java序列化后的内容ac ed 00
05开头。

![2.jpg](https://image.3001.net/images/20190118/15477806059605.jpg!small)

消息类型为RpcResponse的body就直接是java反序列后的内容。

![3.jpg](https://image.3001.net/images/20190118/15477806487759.jpg!small)

## 搭建Spark单独集群服务器

从官网下载，然后通过-h指定IP地址，让端口监听在所有的网卡上./start-master.sh -h 0.0.0.0 -p 70774.

## 证明服务端存在反序列化过程

spark_exploit.py 通过第一个参数和第二个参数指明远程spark集群的连接信息，第三个参数为JAVA反序列化漏洞payload。

通过调用 build_msg 函数将 payload 构建到消息中再发送给服务端，过程比较简单。

![5.jpg](https://image.3001.net/images/20190118/15477807129171.jpg!small)![6.jpg](https://image.3001.net/images/20190118/15477807434893.jpg!small)

## 反向操作客户端

evil_spark_server.py
脚本通过继承BaseRequestHandler类完成了一个简单的TCP服务，对发送过来的数据提取出request_id,
然后再调用build_msg，将request_id和payload构成合法的RPC响应数据包发送给客户端。

![7.jpg](https://image.3001.net/images/20190118/15477807838236.jpg!small)

启动服务

![8.png](https://image.3001.net/images/20190118/15477808361959.png!small)

使用spark客户端进行连接

![9.png](https://image.3001.net/images/20190118/15477808709894.png!small)

![10.jpg](https://image.3001.net/images/20190118/15477809091392.jpg!small)

## 总结

通过抓包看请求数据以及阅读相关代码,逐步确定RPC协议中的请求数据。客户端和服务端都使用了JAVA序列化来传输数据，两边都可以进行利用。

当反过头来想利用反序列化来执行系统命令时，查找ysoserial发现除利用低版本jdk构造利用链外，并无其他合适的gadget。

随着时间的推移，各个库中的漏洞都将被修复和升级，已有的gadget将不再起作用。java 反序列化漏洞终将成为历史。

## 参考

1、<https://spark.apache.org/security.html>

2、<https://zhuanlan.zhihu.com/p/28893155>

 ***本文作者：斗象能力中心TCC-星光，转载请注明来自FreeBuf.COM**

