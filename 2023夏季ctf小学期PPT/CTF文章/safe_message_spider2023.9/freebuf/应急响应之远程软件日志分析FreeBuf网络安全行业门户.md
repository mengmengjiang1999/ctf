# 概述

日常运营分析过程中，很少对远控软件日志进行分析，如向日葵、Todesk，关于这两款软件在日常运营分析过程中，最常和这两款软件有关的，可能是违规软件使用告警，多数情况下内网禁止使用此类软件。恰好最近做过一次简单的向日葵日志分析，本文将对两款常见软件日志进行分析。平台上已有一篇[《todesk日志分析》](https://www.freebuf.com/articles/endpoint/363274.html)，可供大家参考，本文也借鉴了该文章提供的特征进行分析。

# Todesk

ToDesk 是一款多平台远程控制软件，支持主流操作系统Windows、Linux、Mac、Android、iOS跨平台协同操作。

默认情况下todesk日志文件保存在安装目录同级目录Logs下，在4.7以前的版本中，目录下有以service为首的文件以及以client为首的文件。其中service文件表示是被别人远控的日志。client文件表示是远控别人的日志。在4.7后的版本含4.7中，目录下不再存在以client为首的文件。

v4.6.2.3 日志目录结构 VS v4.7.0.2 日志目录结构  
![图片.png](https://image.3001.net/images/20230702/1688272261_64a0fd851f4801732a6ce.png!small)

## v4.6日志分析

v4.7之前版本的日志分析可以参考该文章[《todesk日志分析》](https://www.freebuf.com/articles/endpoint/363274.html)进行分析。

### 本机远控其他主机

通过client日志查找本机远程控制其他主机的日志行为。匹配关键词“Room createMuxRoom server”。

![图片.png](https://image.3001.net/images/20230702/1688272983_64a10057706779aa0debf.png!small)

其中user代表此设备代码，room代表远程控制设备代码。

匹配关键词“Upnp stop”，查找关闭链接记录。

![图片.png](https://image.3001.net/images/20230702/1688273313_64a101a19f46c8f1255af.png!small)

### 本机被其他主机远控记录

在server日志中匹配关键词“tcp begin connect
”，可看到远程连接记录和对端的ip地址。其中Port为443的IP是官方服务器地址，可忽略。

![图片.png](https://image.3001.net/images/20230702/1688287936_64a13ac0b132bb1c053be.png!small)

通过上述日志可以看到端口为20000的连接记录。通过对address地址进行反查归属地址，可以确认是我们远程连接的主机地址。

![图片.png](https://image.3001.net/images/20230702/1688287995_64a13afb0676411bcf4c1.png!small)

## v4.7日志分析

v4.7版本中的日志目录下并没有以client为首的日志文件，因此我们直接对server日志进行分析。

### 本机远控其他主机

由于没有client日志，因此v4.6中提及到的方法在v4.7中并不适用，可以在日志中匹配关键词"client recv connect
request,"。

![图片.png](https://image.3001.net/images/20230702/1688275491_64a10a23dcab0dcfabcbe.png!small)

myid代表此设备代码，destid代表远程控制设备代码。

### 本机被其他主机远控记录

在server日志中查找本机被其他主机远控记录与v4.6中的分析方法一致。同样在日志中匹配关键词“tcp begin connect
”，可看到远程连接记录和对端的ip地址。其中Port为443的IP是官方服务器地址，可忽略。

![图片.png](https://image.3001.net/images/20230702/1688288030_64a13b1e4bbf9d775db3b.png!small)

通过上述日志可以看到端口为20000的连接记录。通过对address地址进行反查归属地址，可以确认是我们远程连接的主机地址。

![图片.png](https://image.3001.net/images/20230702/1688288102_64a13b660bd120f175bec.png!small)

# 向日葵

向日葵远程控制软件是一款拥有多年远控技术经验的远程控制软件,可远程控制手机,远程桌面连接,远程开机,远程管理等,并深入各行各业提供企业远程办公、企业IT运维、技术支持等企业远程解决方案。

## V 13.3 日志分析

### 本机远控其他主机

针对向日葵的日志分析，可结合[【向日葵远控】本地提取连接日志分析+手机号提取](https://zhuanlan.zhihu.com/p/558745599?utm_id=0)进行参考学习。由于日常中使用向日葵的机会较少，所以直接对向日葵最新版本的日志进行分析。

#### 控制端日志分析

![图片.png](https://image.3001.net/images/20230702/1688288456_64a13cc8d2e590b6b19ec.png!small)

上图分别是本机控制端日志和被控端日志文件目录结构。首先对本机控制端日志（以sunlogin_service.+时间命名）文件进行分析：

首先是当前主机的IP信息、MAC地址、操作系统信息等。

![图片.png](https://image.3001.net/images/20230702/1688288568_64a13d38e68d87228d841.png!small)

其次登录成功：

![图片.png](https://image.3001.net/images/20230702/1688288686_64a13daea28a7db4b5686.png!small)

本机控制端日志中也存在一些网络连接行为，如443端口，多为向日葵的一些网站域名解析地址。在本机控制端日志中我并没有发现什么有价值的信息，如果你有更多的发现，也可私信我。

#### 被控端日志分析

与控制端日志相比，被控端日志比较丰富，首先是目录结构，如下：

![图片.png](https://image.3001.net/images/20230702/1688290910_64a1465ea8438fe915346.png!small)

可以重点关注以sunlogin_service.+时间命名的文件、history文件。首先看history文件，记录了被远程连接的时间以及连接方式（识别码），在日常分析过程中，定位时间节点较为关键。

![图片.png](https://image.3001.net/images/20230702/1688291119_64a1472f493b31577f5da.png!small)

接下来是以sunlogin_service.+时间命名的文件，同样也是获取本地的IP、MAC、主机名等信息：

![图片.png](https://image.3001.net/images/20230702/1688294749_64a1555d3283e2ff02549.png!small)

直接在原始日志中日志匹配“remote ip”，可以看到控制端的主机出口IP地址。

![图片.png](https://image.3001.net/images/20230702/1688294873_64a155d91809214f60460.png!small)

端口为4118的IP地址则为向日葵相关域名的解析地址，可忽略。如果不放心，可以使用情报平台的IP解析域名功能进行确认。

![图片.png](https://image.3001.net/images/20230702/1688295127_64a156d738f9da818181e.png!small)

![图片.png](https://image.3001.net/images/20230702/1688295172_64a15704bbd38206ed0c5.png!small)

# 总结

在日常分析过程中，可结合上述特征进行分析定位异常。同时要注意各个版本之间的日志变化情况。日志格式并不是一成不变的。也可以通过模拟各种常见场景，提取行为特征。毕竟
**实践才是检验真理的唯一标准** 。如果你有更好的方法或者思路，请私信我。

# 参考

https://www.freebuf.com/articles/endpoint/363274.html

https://zhuanlan.zhihu.com/p/558745599?utm_id=0

