**作者：Lucifaer  
原文链接：[https://lucifaer.com/2020/02/25/WebLogic%20WLS%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6RCE%E5%88%86%E6%9E%90%EF%BC%88CVE-2020-2551%EF%BC%89/?from=timeline&isappinstalled=0](https://lucifaer.com/2020/02/25/WebLogic%20WLS%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6RCE%E5%88%86%E6%9E%90%EF%BC%88CVE-2020-2551%EF%BC%89/?from=timeline&isappinstalled=0)**

## 0x01 漏洞概述

![](https://images.seebug.org/content/images/2020/02/2fd66c39-9260-4dd0-9953-4a05c0fdafee.jpg-w331s)

Weblogic官方在1月补丁中修复了CVE-2020-2551漏洞，该漏洞位于`WLS`核心组件中，允许远程攻击者通过`iiop`进行网络请求，从而攻击Weblogic服务器，最终远程攻击者可以利用该漏洞完全接管Weblogic服务器。

从通告中我们能看到漏洞发生在`WLS`的核心组件，所以给了我们一个思路去分析该漏洞，只需要从接受并解析`iiop`请求点入手进行分析即可。

## 0x02 漏洞分析

分析该漏洞应该从两方面来进行：

  1. 客户端：通过分析Context的生成过程以及`Context.bind()`的流程来理解服务端解析的数据结构

  2. 服务端：通过分析解析流程最终找到漏洞触发点

本文也将从这两个方面进行分析。分析到最后其实会发现`iiop`只是触发方式，关键的触发点还是由于Weblogic应用本身的处理逻辑，也就是说本质上是个应用漏洞而非协议漏洞。

### 2.1 Context的生成以及bind的流程

无论利用`rmi-iiop`的方式去写客户端，还是写服务端，都需要在编写具体逻辑前获取`Conetext`对象，也就是如下的代码：

    
    
    new InitialContext();

如果研究过CORBA通信过程的话，就能理解这一部分是获取`Naming
Service`的过程，对于客户端来说是获取其中存在的IOR引用以供后面的rpc流程使用；对于服务端来说，用于完成对象注册。这里来跟进一下Context的生成过程，方便后续理解Weblogic的解析逻辑。

![](https://images.seebug.org/content/images/2020/02/191dea40-ae26-46df-be24-ec6a2965bfbd.jpg-w331s)

这里有个很重要的参数`environment`，在该参数中可以设置`Context`的静态变量来指定`Context`的初始化参数，包括`JNDI_FACTORY`、`PROVIDER_URL`。这些初始化参数在后续的流程中有极其重要的作用。

![](https://images.seebug.org/content/images/2020/02/cd53f807-abb2-4791-9c28-58455813b11c.jpg-w331s)

当在`environment`中设置了`Context.INITIAL_CONTEXT_FACTORY`后会尝试获取该`Context factory`：

![](https://images.seebug.org/content/images/2020/02/c6876827-20aa-4244-90a6-de5d1d02088f.jpg-w331s)

![](https://images.seebug.org/content/images/2020/02/08b09e4a-0034-48f6-8f50-b1b694ac7f68.jpg-w331s)

这里会根据设定的`Context.INITIAL_CONTEXT_FACTORY`，反射获取工厂类，之后调用`getInitialContext()`方法。首先看一下在JDK中原生以及在Weblogic中所拓展出的工厂类到底有哪些：

![](https://images.seebug.org/content/images/2020/02/5a03ca2c-80da-4ae3-97a3-38a444f10e26.jpg-w331s)

这里我们简单的看一下`WLInitialContextFactory`这个Weblogic拓展的工厂类：

![](https://images.seebug.org/content/images/2020/02/06e06ed9-fd2c-41eb-96bc-a5bd95664f83.jpg-w331s)

![](https://images.seebug.org/content/images/2020/02/50d4e34e-5bed-48f8-b83e-49e93a645451.jpg-w331s)

![](https://images.seebug.org/content/images/2020/02/2ed1d325-826d-4ba7-9e06-1465529af6dd.jpg-w331s)

这里跟进看一下`getORBReference()`方法：

![](https://images.seebug.org/content/images/2020/02/ad6b319b-c73a-4884-baf8-67fef2515ebf.jpg-w331s)

这里和CORBA的写法是一样的：

![](https://images.seebug.org/content/images/2020/02/243c6535-0f78-47c7-aea6-2ed41e78504a.jpg-w331s)

都是初始化`orb`获取`Naming
Service`的过程，如果想要了解详细的过程，可以研究一下上一篇讲[CORBA](http://https://paper.seebug.org/1124/
"CORBA") 的文章。

在获取了`Context`后，接着来看一下其绑定流程，此流程在`bind()`函数中有所体现：

![](https://images.seebug.org/content/images/2020/02/dcaf1e42-32c3-4da3-bc94-34ae7a6aeec9.jpg-w331s)

熟悉CORBA的同学肯定一眼就能看出这里完成的是生成IOR，同时设定corba协议中的数据类型与java类型交互的约定为`tk_value`，并设定请求的`op`或者叫做`operation`为`bind_any`。这里不仅仅设定了服务端对注册请求的处理方式（`bind_any`的处理流程），同时设定了后面反序列化的方式（`tk_value`）。

### 2.2 Weblogic解析流程

在了解了Context的生成及`bind()`流程后，接着来看一下Weblogic的解析流程。Weblogic默认在7001端口接收`iiop`请求，所有的请求都是交由`weblogic.rmi.cluster.ClusterableServerRef#invoke`来处理的：

![](https://images.seebug.org/content/images/2020/02/3ae6be0d-d86c-4035-abbe-bf46268a2a26.jpg-w331s)

在`handleRequest`中的流程较为长，我只截关键处理点：

![](https://images.seebug.org/content/images/2020/02/f7b4cc15-c44a-42b8-a03c-4c4ba5fed5ec.jpg-w331s)

直接跟进`var2.invoke()`，具体的实现方法在`weblogic.rmi.cluster.ClusterableServerRef#invoke`：

![](https://images.seebug.org/content/images/2020/02/af83b5be-b336-4be9-8a51-87b70d250da0.jpg-w331s)

![](https://images.seebug.org/content/images/2020/02/e3f9a5f9-46e9-4be9-9b7e-40e3206dcb5c.jpg-w331s)

这里首先会判断请求是否为`objectMethods`中已经存在的类型，当不存在时将会调用`delegate.invoke()`来处理，由于我们在发送注册请求时的请求类型为`bind_any()`并不在`objectMethods`中，所以会触发`delegate.invoke()`，具体的实现类为`weblogic.corba.cos.naming._NamingContextAnyImplBase#_invoke`：

![](https://images.seebug.org/content/images/2020/02/3ed15e55-8e0e-447e-8407-e7163ed2f4cf.jpg-w331s)

因为我们当前的请求类型为`bind_any()`，其所对应的`var5`为0，所以会进入两个关键的流程：

  1. `WNameHelper.read()`

  2. `var2.read_any()`

![](https://images.seebug.org/content/images/2020/02/1e8b47c2-3ea7-42de-ac88-035799273270.jpg-w331s)

![](https://images.seebug.org/content/images/2020/02/ecbf5bbc-5ad3-4706-9a96-eea5fdf57d25.jpg-w331s)

在`WNameHelper.read()`主要负责提取IOR中的信息（id、kind）用于之后注册到`orb`的流程中。

而反序列化的触发点在`var2.read_any()`中：

![](https://images.seebug.org/content/images/2020/02/659697ec-7c87-42d1-b268-6301eb767948.jpg-w331s)

在上一节中，已经说过在`bind()`流程中发起注册请求时，会构造一个`Any`类，并将交互类型设置为`tk_value`也就是`this.read_TypeCode()`。继续跟进：

![](https://images.seebug.org/content/images/2020/02/cd67704b-3020-43ed-a598-1d295fff719a.jpg-w331s)

![](https://images.seebug.org/content/images/2020/02/30773cbf-5d17-4f21-8522-65b418def33d.jpg-w331s)

这里会根据`TCKind`来分派具体的处理流程，`tk_value`对应29：

![](https://images.seebug.org/content/images/2020/02/34417aa1-164e-4016-b26c-00c83047a381.jpg-w331s)

接下来就是之前CORBA文章中所提到过的反序列化流程：

![](https://images.seebug.org/content/images/2020/02/120c845e-919b-4f25-bfc5-d7d250a68b8f.jpg-w331s)

由`CDRInputStream`跳转到JDK原生反序列化：

![](https://images.seebug.org/content/images/2020/02/1089e57a-5dba-41a3-8e38-0059e518f4da.jpg-w331s)

至此分析结束。

## 0x03 利用研究

根据0x02中的分析，可以梳理出攻击需要的两个元素：

  1. 构造一个`bind_any()`请求

  2. 寻找一条gadget填充到`Any`类中

攻击效果如下：

![](https://images.seebug.org/content/images/2020/02/0738fe16-e0d9-4ecf-afd1-7c1b433c1847.jpg-w331s)

**Reference**

  1. <https://cert.360.cn/report/detail?id=d3f6666d6558f02a6204dd51cb749558>

  2. <https://cert.360.cn/warning/detail?id=8746760715a399499f8a46fb85edcda1>

  3. <https://www.oracle.com/security-alerts/cpujan2020.html>

  4. <https://lucifaer.com/2020/02/20/Java%20CORBA%E7%A0%94%E7%A9%B6/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1130/>

