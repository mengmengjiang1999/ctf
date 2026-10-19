# Dubbo反序列化漏洞详细分析

阅读量 **385259**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-26 16:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t012fdc1b72a8884c2a.png)

## 0x00 前言

关于Java反序列化的漏洞已经分析了几个，这次再利用Commons-Collections利用链来分析一下去年Dubbo的反序列化漏洞，同样也是未处理用户数据，最后造成了问题，这类问题屡见不鲜。

## 0x01 关于Dubbo和CVE-2019-17564

Apache
Dubbo是阿里巴巴公司基于Java的高性能开源RPC框架，可以和Spring框架无缝集成。它提供了三大核心功能：面向接口的远程方法调用，智能容错和负载均衡，以及服务自动注册和发现。  
附一张Dubbo架构：

![](https://p0.ssl.qhimg.com/t01b70bff3e24c9cd08.jpg)

除了官方推荐的默认Dubbo协议外，Dubbo还支持HTTP，RMI等协议。  
造成本次的反序列化漏洞（CVE-2019-17564）的主要原因是：在用户使用HTTP协议进行通信时，会将消费者远程的request中POST的数据进行反序列化，而且Dubbo对于消息体未做过滤等处理，所以造成了这次反序列化问题。

## 0x02 详细分析

###  一、影响范围

  * 2.7.0 <= Apache Dubbo <= 2.7.4
  * 2.6.0 <= Apache Dubbo <= 2.6.7
  * Apache Dubbo = 2.5.x

###  二、环境搭建

1.首先Dubbo需要zookeeper，因此我们需要首先下载zookeeper，并完成相关启动。启动成功后打开zookeeper的客户端程序会显示：“Welcome
to ZooKeeper!”。

2.下载官方的Dubbo样例，之后使用samples中的dubbo-samples-http即可。但是导入IDEA后要进行相关修改：  
首先需要在pom.xml文件中将版本改为漏洞版本，我选择了2.7.3；  
然后添加相关gadget，这里使用Commons-Collection4的gadget；  
最后一步的话是修改spring/http-provider.xml中的ip和port。

3.在zookeeper服务端启动后，依次启动HttpProvider、HttpConsumer后可以看到下图，说明Dubbo环境成功。

![](https://p0.ssl.qhimg.com/t01a026f35026cf866c.png)

4.用ysoserial生成payload。

    
    
    java -jar ysoserial.jar CommonsCollections4 calc > dubbo.ser
    

5.之后用burp发POST包到目标地址，可以成功触发计算器弹出。

![](https://p5.ssl.qhimg.com/t01c6d6bc64fe174116.jpg)

###  三、详细分析

首先在DispatcherServlet#service()中下断点，进入调式，并用burp发包，断在handler.handle(request,
response)这里

![](https://p2.ssl.qhimg.com/t011669dab66f7b4849.png)

我们单步步入handle函数后可以看到，首先获取uri，然后获取到这个路径去获取相关处理对象skeletonMap，如果失败则会报错。进入else后通过handleRequest函数进行处理

![](https://p1.ssl.qhimg.com/t0190583ab4310f8b86.png)

跟进handleRequest函数后，可以看到将请求传入了readRemoteInvocation(request)

![](https://p2.ssl.qhimg.com/t010c9b67cb5f090d90.png)

跟进readRemoteInvocation函数后，可以看到会调用重载的两个参数的readRemoteInvocation函数，参数为将request和我们post的序列化数据

![](https://p4.ssl.qhimg.com/t01d6d86230c6a6c9ce.png)

跟进readRemoteInvocation(HttpServletRequest request, InputStream
is)后可以看到，调用了createObjectInputStream函数，将序列化数据封装为ObjectInputStream，生成了包含序列化数据的ois对象。之后用this.doReadRemoteInvocation(ois)进行获取RemoteInvocation远程调用对象。

![](https://p3.ssl.qhimg.com/t0103a7e7ea80237552.png)

跟进doReadRemoteInvocation(ObjectInputStream
ois)后，可以看到并没有任何过滤操作，直接调用ois.readObject()反序列化了之前封装的ois对象，其中包含恶意的序列化内容，结合相关反序列化链，造成RCE

![](https://p3.ssl.qhimg.com/t01087c78b37c37f799.png)

###  四、修复

升级Apache Dubbo到最新版本。  
在之后的版本更新中，获取了skeleton对象后会调用JsonRpcBasicServer.hanlde函数进行处理，原来的利用链失效。

## 0x03 结语

本文我们详细分析了Dubbo的反序列化漏洞，从开始获取我们提交的数据，到readObject()，最主要的问题还是对于用户输入的盲目信任，需要做相关处理，漏洞的挖掘也可以从用户输入等方面着手，找相关危险的调用。最后祝大家新年快乐，牛年大吉。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **zzZ** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231416](/post/id/231416)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t0177bde109b464d6d4.png) zzZ

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

