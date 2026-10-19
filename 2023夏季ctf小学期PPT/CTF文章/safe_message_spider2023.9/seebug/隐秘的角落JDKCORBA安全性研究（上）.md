**作者：蚂蚁安全非攻实验室  
公众号：[蚂蚁安全实验室](https://mp.weixin.qq.com/s/FxAKuX9IY6dLuhMuWjJMqQ)**

## 特别推荐

**诸葛建伟 清华大学网络科学与网络空间研究院副研究员**

“对非可信数据的反序列化”一直是应用安全领域中常见且高危的安全漏洞类型，在各种不同Web开发语言、分布式架构及中间件框架中大面积流行，也经常被攻击者发掘并利用形成对业务应用的远程代码执行突破口。网络安全研究领域对反序列化漏洞已有较多研究和技术文章的发表，甚至学术界也曾对此问题进行过关注与研究。

而正如文章标题所指，蚂蚁安全实验室的这篇分享揭密了反序列化安全风险的一个“隐秘角落”：Java开发分布式应用中流行使用的COBRA架构，这个角落直到2019年才被研究者公开涉足。本文以由浅入深，案例驱动的方式详细介绍了COBRA基本架构及其应用细节，并全方位地从不同角度分析了COBRA架构所面临的反序列化漏洞风险，技术内容的详尽程度与行文风格对Web安全的研究人员和技术爱好者都非常友好，对理解Java
COBRA架构的最新安全风险有很大的帮助。

## 一、背景

在移动互联网时代，互联网平台为了服务海量用户和支持高并发业务场景，服务端分布式架构已经成为了主流的应用部署架构。CORBA、JAVA
RMI、DCOM等分布式技术先后诞生且得到了广泛应用，其安全性也成为影响互联网生态安全的重要因素。以CORBA为例，目前其协议仍然被很多JAVA中间件、基础设施支持，例如weblogic、websphere、glassfish等，研究其协议实现的安全性，对于互联网基础设施安全防护有着重要价值。

在JAVA分布式架构中存在着大量的序列化与反序列化操作令人担心其安全风险，但并非所有的反序列化框架都存在安全风险，为此于今年我们提出了开放动态反序列化（ODD，Open
Dynamic
Deserialization）的概念以揭示反序列化中真正的安全风险。ODD简单来说就是应用架构支持在反序列化过程中动态生成任意类型的对象。ODD的核心是“开放”和“动态”，是为了提升应用开发的灵活性和效率而设计。但是从安全角度来说，“开放”和“动态”本质上是不安全的，它容易失去对程序行为的控制，导致非安全输入对程序行为的任意劫持，从而形成一个集中的RCE(远程代码执行)突破点。

ODD这种漏洞本质虽然是我们在今年的fastjson应急中总结并明确的，但这种漏洞类型在历史上已经引起了大量的安全问题，各类分布式技术以及系统均受到了非常大的挑战。2015年Gabriel
Lawrence和Chris Frohoff在AppSecCali上发表的著名安全报告"Marshalling
Pickles"，提出了POP(Property-Oriented
Programing)攻击链，能够利用JAVA体系中ODD设计导致的安全缺陷实现RCE，ODD类型反序列化漏洞在JAVA领域影响面被急剧扩大。在报告中，作者也明确警告
Avoid magic -- Avoid open-ended (de)serialization when
possible，即不要做开放式反序列化。但显然业界并没有把这个警告当回事，ODD安全漏洞愈演愈烈，首当其冲的就是 JAVA RMI
及其相关应用系统。@pwntester在2016年black hat黑客大会中提出了针对 **JAVA RMI技术的一系列攻击方式**
，除在当时的安全研究圈引起巨大轰动以外，其攻击思路至今仍然被各red team引用并作为其主要武器之一。

过去几年，行业中针对CORBA安全性的公开分享并不多。直到2019年，@An Trinh在当年的blackhat黑客大会上提出了 **针对 IIOP
协议的反序列化攻击方式** ，而 IIOP正是用来在CORBA对象请求代理之间交流的协议。此后RMI-IIOP相关的漏洞井喷式爆发， 2020年相关
CVE数量多达20+且基本都能造成 RCE，例如经典的 **CVE-2020-4450** 和 **CVE-2020-2551** 。

我们的JAVA安全研究工作很早就已经覆盖CORBA，出于“抛砖引玉”的想法，我们把研究过程中积累的思路和经验形成两篇文章分享出来：

**· 隐秘的角落--JDK CORBA 安全性研究（上）：介绍CORBA基本架构以及浅析实现细节，为后续安全风险分析打基础。**

**· 隐秘的角落--JDK CORBA 安全性研究（下）：从客户端、服务端和通信协议三部分，全方位分析CORBA安全风险，并讨论如何防范。**

## 二、基础概念

**什么是 CORBA？**

CORBA 从概念上扩展了 RPC，它是一种面向对象的 RPC，RPC 应用都是面向过程的，而 CORBA 应用是面向对象的。

**那么什么是RPC？**

RPC（Remote Promote Call） 远程过程调用协议。RPC使得程序能够像访问本地系统资源一样，去访问远端系统资源。

简单的说，RPC就是从一台机器(客户端)上通过参数传递的方式调用另一台机器(服务器)上的一个函数或方法(可以统称为服务)并得到返回的结果。

![](https://images.seebug.org/content/images/2021/01/d0032d19-3563-41a3-99a7-0661f6b4a2f8.webp-w331s)

CORBA 流程设计如下：

![](https://images.seebug.org/content/images/2021/01/15f9a555-dce8-48df-a57e-46eb482c5be5.webp-w331s)

CORBA 体系如下：

![](https://images.seebug.org/content/images/2021/01/408476b5-10d6-4f08-8489-55b2340f3160.webp-w331s)

（静态存框->静态存根）

客户端调用静态存根(static stubs)向服务器发出请求，存根(stubs)是代理对象支持的客户端程序。

服务器端调用静态框架(static skeleton)处理客户端请求，框架(skeleton)是服务器端程序。

一些基础术语，如下（可跳过，在详细阅读后文过程中再查看）：

**IOR** ：可互操作对象引用，类似 JDBC 数据库连接信息或者 JNDI 连接信息对象等，用于传输对象之间的操作信息。

**ORB** （Object Request Broker）：对象请求代理。ORB 是一个中间件，他在对象间建立客户-服务器的关系。通过
ORB，一个客户可以很简单地使用服务器对象的方法。ORB
截获客户端的方法调用，然后负责找到服务端方法实现并且传递参数，最后将返回方法执行结果。客户不用知道对象在哪里，是什么语言实现的。

**ORBD** （ORB守护程序）：负责查找 IOR 指定的对象实现，以及建立客户机和服务器之间的连接。一旦建立了连接，GIOP
将定义一组由客户机用于请求或服务器用于响应的消息。

**GIOP** （General Inter-ORB Protocol）：GIOP
元件提供了一个标准传输语法（低层数据表示）和ORB之间通信的信息格式集。GIOP只能用在ORB与ORB之间，而且，只能在符合理想条件的面向连接传输协议中使用。

**IIOP** （Internet Inter-ORB Protocol）：IIOP 是 CORBA 的通信协议，用于CORBA对象RPC请求之间的交流。

**IDL** ：IDL全称接口定义语言，是用来描述软件组件接口的一种规范语言。用户可以定义模块、接口、属性、方法、输入输出参数。Java 中提供了
idlj 命令用来编译 IDL 描述文件，用以生成 Java 语言的 客户端 java 文件等。

**CORBA与ORB的关系**
：CORBA的分布式对象调用能力依赖于ORB，而ORB之间进行通信是通过GIOP协议完成的。GIOP定义了ORB之间互操作的传输语法和标准消息格式，比如请求头、请求体所包含的字段和长度。

**IIOP与GIOP的关系** ：IIOP与GIOP的关系就象特殊语言与OMG
IDL之间的关系；GIOP能被映射到不同层，它能指定协议。就象IDL不能见着完整的程序一样，GIOP
本身也不能提供完整的协作工作。IIOP和不同传输层上的其它相似映射，实现抽象的GIOP定义。GIOP是一个抽象的协议，而IIOP是其一个具体的实现，定义了如何通过TCP/IP协议交换GIOP消息。

## 三、环境准备

首先，尝试 **构建一个简单的 corba 应用** 。

这里已经准备好了一套 **JDK CORBA 环境** ，git clone 后直接使用 idea 打开即可，代码都是在 JDK 8u221 环境中运行过。

## 四、idl 简单编写以及idlj 使用

首先编写一个简单的 hello.idl，如下：

    
    
    module com {
    
      interface Hello{
    
         string sayHello();
    
    　  };
    
    };

如上，module 名在 java 源码中表示为 package，设置一个接口类 Hello，类中含有一个无参、返回类型为 String 的
sayHello 函数。

然后使用 JDK 自带的 idlj 工具生成 client 和 server 代码，命令如下：

idlj -fall hello.idl

注：idlj -fall hello.idl 可以生成 server 、client 端所需的所有 class，如果只需要 client 端或 server
端的话，使用 -fclient / -fserver 即可。

命令执行完成后，会直接在当前目录下生成 com 目录，目录中含有 6 个文件如下：

![](https://images.seebug.org/content/images/2021/01/98fc4cc7-4699-47f7-98f1-38378c2bbb64.webp-w331s)

## 五、本地尝试

为了方便观察，我将 server 运行在本地。

首先启动 ORBD 服务器，运行如下命令，会监听本地 1050 和 1049 端口：

orbd -port 1050 -ORBInitialPort 1049 -ORBInitialHost localhost

随后运行 HelloServer，效果如下：

![](https://images.seebug.org/content/images/2021/01/6cbd7057-2d86-4946-bae0-f1bdbc7d6ad7.webp-w331s)

最后运行 HelloClient，效果如下：

![](https://images.seebug.org/content/images/2021/01/04e24465-ca3b-4efa-a1c0-08b364dc5153.webp-w331s)

如上图，已经调用成功了，接下来简单分析一下整个通信流程。

## 六、通信过程

经过简单的抓包分析，得出整个通信过程如下图：

![](https://images.seebug.org/content/images/2021/01/c6e99319-a79a-4718-9ab2-ff32e487589a.webp-w331s)

如上图：

首先会启动 ORBD 作为 name service 的服务器，会创造 name service 服务。

第二步，corba server 端向 orbd 获取 name service，协商好通信格式。

第三步，orbd 返回自己保存的 name service。

第四步，corba server 端拿到 name service 后，会将自己的 corba 服务绑定到 name service 上面（流程和 rmi
类似）。

第五步，corba client 端这个时候想要查找 corba server 提供的某个服务，先向 orbd 发起请求，获取 name service。

第六步，orbd 来者不拒，将自己保存的 name service 返回给 client 端。

第七步，corba client 端利用 name service 查找到某个 corba server 端提供的服务（client 端获得的是
stub），然后发起一个 rpc 请求，要求 corba server 响应。

第八步，corba server 在监听到 corba client 端的请求后，一顿调用并且计算出结果，然后将其打包封装，最后返回给 corba
client。

以上，就是一个 corba 应用的一次远程调用的通信流程。

使用 wireshark 抓取通信流量，如下图：

![](https://images.seebug.org/content/images/2021/01/f78d9803-7fca-4b59-a9f1-9bc4ba7b1c1c.webp-w331s)

## 七、Client 解析

Client 端主要是通过 stub 远程调用 Server 端。

stub 类是 client 端调用 orb 的媒介，stub 、orb 关系，借用一张图表述如下：

![](https://images.seebug.org/content/images/2021/01/1362aae9-265d-4a00-8f6a-1b01e7833682.webp-w331s)

client 通过对 stub 的调用，间接调用了 server 端的函数实现。

stub 会对客户端的调用参数和调用请求进行封装交给 orb，而后 orb 通过调用分派机制与 server
端通信，server端获取到了cliant端的调用请求，将请求参数带入请求操作（调用函数）中，最终返回给 orb 一个 response，orb 传递给
client 的 stub ，stub 传递给 client 调用者，简单流程如下：

客户端含有 Hello 、_HelloStub.... 服务端含有 HelloImpl

#1 client 发起调用：sayHello()

->

#2 stub 封装 client 的调用请求，并发送给 orbd

->

#3 orb 接受请求，根据 server 端注册信息，分派给 server 端处理调用请求

->

#4 server 接受调用请求，执行 sayHello ，并将执行结果进行封装，传递给 orbd

->

#5 ordb 收到 server 端的返回后，将其传递给 stub

->

#6 stub 收到请求后，解析返回二进制流，提取 server 端的处理结果

->

#7 最终结果会返回给 client 调用者

## 八、stub的生成

stub 类是存在于 client 端的 server 端的 handle。生成方法有好几种，在此只列举三种，如下：

· 1. 使用代码先获取 NameServer ，然后 resolve_str

· 2. 使用 ORB.string_to_object

· 3. 使用 javax.naming.InitialContext.lookup

### 1\. 通过 NameServer 获取

示例代码如下：

    
    
    Properties props = new Properties();
    
    // 生成一个ORB，并初始化，这个和Server端一样
    
    props .put("org.omg.CORBA.ORBInitialPort", "1050");
    
    props.put("org.omg.CORBA.ORBInitialHost", "192.168.0.2");
    
    ORB orb = ORB.init(args, props);
    
    // 获得根命名上下文
    
    org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
    
    // 用NamingContextExt代替NamingContext.
    
    NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);
    
    // 通过名称获取服务器端的对象引用
    
    String name = "Hello";
    
    Hello hello = HelloHelper.narrow(ncRef.resolve_str(name));

### 2\. 通过 ORB.string_to_object

示例代码如下：

    
    
    ORB orb = ORB.init(args, null);
    org.omg.CORBA.Object obj 
    = orb.string_to_object("corbaname::192.168.0.2:1050#Hello");
    Hello hello = HelloHelper.narrow(obj);

如上代码，传入的参数是 corbaname: 开头的字符串，string_to_object 支持三种协议：

corbaname: 、 corbaloc: 、 IOR:

#### 2.1 IOR

IOR 是一个数据结构，它提供了关于类型、协议支持和可用 ORB 服务的信息。ORB 创建、使用并维护该 IOR。

简单可以理解为，存储着 corba server 相关 rpc 信息，以 IOR:XXX 形式表现的字符串，如：

    
    
    IOR:000000000000000100000000000000010000000000000027000100000000000b33302e35322e38382e370000041a00000000000b4e616d6553657276696365

#### 2.2 corbaloc

corbaloc 经过处理最终也是生成一个 IOR ，然后通过 IOR 创建出一个 stub

#### 2.3 corbaname

他的处理逻辑如下：

![](https://images.seebug.org/content/images/2021/01/95506b94-32b6-4fce-9615-8de6c396399c.webp-w331s)

如上图，这完全和第一种通过 NameServer 获取 stub 的方式一样，后续的调用链在 client 安全风险分析过程中会展示出来。

### 3.通过 jndi （javax.naming.InitialContext.lookup）

代码如下：

    
    
    ORB orb = ORB.init(args, null);
    
    Hashtable env = new Hashtable(5, 0.75f);
    
    env.put("java.naming.corba.orb", orb);
    
    Context ic = new InitialContext(env);
    
    // resolve the Object Reference using JNDI
    
    Hello helloRef 
    =HelloHelper.narrow((org.omg.CORBA.Object)ic.lookup("corbaname::192.168.0.2:1050#Hello"));

如上述代码，也是使用的 corbaname 作为协议开头，因为 jndi 同时支持3中写法：

iiopname:

iiop:

corbaname:

其中， iiopname 和 iiop 开头的协议串，最终会转换成 corbaloc 开头的协议串。corbaname 开头的协议，会触发
org.omg.CosNaming._NamingContextStub#resolve 调用。

resolve 函数 和 resolve_str 函数实现逻辑是一样的、执行结果也相同，只是参数类型不同而已。

## 九、client 端调用 rpc

使用方式目前只收集到 2 种：

· 1. 通过 client 端 stub 进行调用

· 2. 通过 Dynamic Invocation Interface（dii request）调用

### 1\. stub 调用

代码如下：

    
    
    Properties props = new Properties();
    
    // 生成一个ORB，并初始化，这个和Server端一样
    
    props .put("org.omg.CORBA.ORBInitialPort", "1050");
    
    props.put("org.omg.CORBA.ORBInitialHost", "192.168.0.2");
    
    ORB orb = ORB.init(args, props);
    
    // 获得根命名上下文
    
    org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
    
    // 用NamingContextExt代替NamingContext.
    
    NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);
    
    // 通过名称获取服务器端的对象引用
    
    String name = "Hello";
    
    Hello hello = HelloHelper.narrow(ncRef.resolve_str(name));
    
    //调用远程对象
    
    System.out.println(hello.sayHello());

### 2\. dii 调用

代码如下：

    
    
    Properties props = new Properties();
    
    // 生成一个ORB，并初始化，这个和Server端一样
    
    props .put("org.omg.CORBA.ORBInitialPort", "1050");
    
    props.put("org.omg.CORBA.ORBInitialHost", "192.168.0.2");
    
    ORB orb = ORB.init(args, props);
    
    // 获得根命名上下文
    
    org.omg.CORBA.Object objRef = orb.resolve_initial_references("NameService");
    
    // 用NamingContextExt代替NamingContext.
    
    NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);
    
    // 通过名称获取服务器端的对象引用
    
    String name = "Hello";
    
    Hello hello = HelloHelper.narrow(ncRef.resolve_str(name));
    
    Request request = hello._request("sayHello");
    
    request.invoke();
    
    System.out.println(request.result().value());

如上述代码，在 stub 获取的部分和 stub 调用方式完全一样，后续是通过获取
com.sun.corba.se.impl.corba.RequestImpl 以此来进行 dii 调用的（Dynamic Invocation
Interface）。

## 十、Server 解析

### 服务注册

回顾一下 HelloServer 中注册服务的代码，如下：

    
    
    // 获得命名上下文 NameService
    
    org.omg.CORBA.Object objref = orb.resolve_initial_references("NameService");
    
    // 使用NamingContextExt 它是 INS（Interoperable Naming Service，协同命名规范）的一部分
    
    NamingContextExt ncRef = NamingContextExtHelper.narrow(objref);
    
    // 绑定一个对象引用，以便客户端可以调用
    
    String name = "Hello";
    
    NameComponent[] nc = ncRef.to_name(name);
    
    ncRef.rebind(nc, href);

如上代码，在获取到 NameService 后随即开始注册服务，服务名叫做 Hello，client 端可以通过服务名在 NameService
中搜索服务。在此调用 NamingContextExt#rebind 是向 ORBD 发送一个重绑定请求。

### 派遣请求

在服务绑定完成后，服务端会开始监听一个高端口等待客户端的连接通信。

下图是客户端发起请求后，服务端派遣请求的工作流程：

![](https://images.seebug.org/content/images/2021/01/d19da710-aad8-4ecf-a739-081a28492b5a.webp-w331s)

至此，JDK CORBA 基本概念介绍结束。

## 十一、安全风险

经过分析和探索，发现了 client 端、server 端、orbd 端含有如下风险点：

· client 端 ，存在反序列化风险和远程类加载风险

· server 端，存在反序列化风险

· orbd，存在反序列化风险

在下篇中，将会分析 JDK CORBA 中存在的风险点。

## 参考文献

RPC基本原理：<https://www.cnblogs.com/sumuncle/p/11554904.html>

CORBA Website：<https://www.corba.org/>

wiki：<https://en.wikipedia.org/wiki/Common_Object_Request_Broker_Architecture>

基本概念：<https://www.cnblogs.com/zhuchunling/p/9540541.html>

构建简单的 corba 应用：<https://blog.csdn.net/chjttony/article/details/6561466>

corba 简介：<https://blog.csdn.net/chjttony/article/details/6543116>

corba 通信过程浅析：<http://weinan.io/2017/05/03/corba-iiop.html>

## 关于作者

**蚂蚁安全非攻实验室**
：隶属于蚂蚁安全九大实验室之一。蚂蚁安全非攻实验室致力于JAVA安全技术研究，覆盖蚂蚁自研框架和中间件、经济体开源产品以及行业中广泛使用的第三方开源产品，通过结合程序自动化分析技术和AI技术，深度挖掘相关应用的安全风险，构建可信的安全架构解决方案。

![](https://images.seebug.org/content/images/2021/01/1310595e-3c6e-4440-9f9f-83f73ee0f5bb.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1445/>

