## 一、简介

RMI（Remote Method
Invocation）是由JDK自带提供的一套远程方法调用框架，用于实现跨JVM间的方法调用。其整体架构与常见的RPC框架类似。

![1647003136_622b46005120b850cc065.png!small?1647003136494](https://image.3001.net/images/20220311/1647003136_622b46005120b850cc065.png!small?1647003136494)

如图共有三个角色参与其中:

> Registry: 注册中心，负责维护当前集群提供的Service列表及对应的Server地址。
>
> Server: 服务提供者，其具体实现了各项Service，注册到Registry，同时对外接受Client的请求。
>
> Client: 服务调用者，通过Registry查询需要的Service, 后对Server发起请求。

样例代码:

Registry  
![1647003224_622b46587e9587abc6433.png!small](https://image.3001.net/images/20220311/1647003224_622b46587e9587abc6433.png!small)

Server  
![1647003251_622b467346b8ca017c7c9.png!small?1647003251423](https://image.3001.net/images/20220311/1647003251_622b467346b8ca017c7c9.png!small?1647003251423)

![1647003258_622b467a2ed443e274110.png!small?1647003258389](https://image.3001.net/images/20220311/1647003258_622b467a2ed443e274110.png!small?1647003258389)

Client  
![1647003286_622b46962bb7a40d3d671.png!small?1647003286345](https://image.3001.net/images/20220311/1647003286_622b46962bb7a40d3d671.png!small?1647003286345)

## 二、原理

### 基础

RPC类框架的核心技术均大同小异，在客户端调用Service时，代理技术将调用涉及的数据(目标方法、参数..)序列化并通过网络传输到服务端，服务端反序列化数据执行本地调用，后将返回值序列化传输回客户端。

走读RMI源码可得，在运行时期，Registry通过 **TCP 1099**
对外提供Service查询与注册能力，暴露的方法包括:list、lookup、bind、rebind、unbind， **Server启动时,
将监听一随机TCP端口作为服务端口**
，并通过bind将Service及服务地址注册到Registry，Client通过Registry的list、lookup查询Service，根据
**查询结果的服务地址直连Server，进行方法调用** 。

> Registry对外接口: sun.rmi.registry.RegistryImpl_Stub#operations
>
> 客户端方法调用代理逻辑: sun.rmi.server.UnicastRef#invoke(java.rmi.Remote,
> java.lang.reflect.Method, java.lang.Object[], long)

### JRMP

这里我们关注下RMI的通信协议部分, 参考官方文档如下:

>
> <https://docs.oracle.com/javase/8/docs/technotes/guides/serialization/index.html>
>
> <https://docs.oracle.com/javase/8/docs/platform/rmi/spec/rmi-protocol3.html>
>
> <https://docs.oracle.com/javase/8/docs/platform/rmi/spec/rmi-protocol4.html>

RMI使用的通信协议为: **JRMP, 其在JDK实现中通过TCP传输** ，其中主要包括头部、数据部分，其中
**序列化方案使用的是Java原生序列化技术：**

>
> <https://docs.oracle.com/javase/8/docs/technotes/guides/serialization/index.html>

从JDK实现核心逻辑(Client方法调用)看协议实现

sun.rmi.server.UnicastRef#invoke(java.rmi.Remote, java.lang.reflect.Method,
java.lang.Object[],
long)![1647003629_622b47ed98017b51701d5.png!small?1647003629625](https://image.3001.net/images/20220311/1647003629_622b47ed98017b51701d5.png!small?1647003629625)写JRMP
Header

> sun.rmi.transport.tcp.TCPChannel#createConnection
>
> sun.rmi.transport.tcp.TCPChannel#writeTransportHeader

确定调用类型及目标对象&方法

>
> sun.rmi.transport.StreamRemoteCall#StreamRemoteCall(sun.rmi.transport.Connection,
> java.rmi.server.ObjID, int, long)

备注:

> 这里可以看到RMI对远程目标对象及方法的定位实现:
>
> 目标对象通过java.rmi.server.ObjID来描述
>
> 目标方法通过一个hash值来描述，sun.rmi.server.Util#computeMethodHash
>
> 写目标方法传参 (基于Java序列化协议)
>
> sun.rmi.server.UnicastRef#marshalValue

### JRMPCall

![1647003849_622b48c9af37c14d8d8e0.png!small?1647003850580](https://image.3001.net/images/20220311/1647003849_622b48c9af37c14d8d8e0.png!small?1647003850580)

## 三、攻击面

RMI 对于参数传递和返回使用了Java原生序列化技术，故 **存在反序列化攻击风险** 。

### 攻击RMI Registry

Registry的查询注册能力本质是对外暴露一个 **ObjID RMI** 对象，其 **objnum固定为0**
，该对象包括如下5个方法，其中4个方法都有Object类型的传参，我们可通过 **构造恶意反序列化对象**
，通过RMI投递到Registry并实现反序列化攻击。

> void bind(java.lang.String, java.rmi.Remote)
>
> java.lang.String list()[]
>
> java.rmi.Remote lookup(java.lang.String)
>
> void rebind(java.lang.String, java.rmi.Remote)
>
> void
> unbind(java.lang.String)![1647003906_622b49024f579815b3cb1.png!small?1647003906387](https://image.3001.net/images/20220311/1647003906_622b49024f579815b3cb1.png!small?1647003906387)

### 攻击RMI Server

 **1.RMI Server没有 Registry ObjID(objnum=0)咋办？**

RMI提供一个分布式GC方案(<https://docs.oracle.com/javase/8/docs/platform/rmi/spec/rmi-dgc2a.html>), 其使得每个Server会提供一个 **DGC ObjID(objnum=2)**
，具体实现位于sun.rmi.transport.DGCImpl，公开方法为:

> void clean(java.rmi.server.ObjID[], long, java.rmi.dgc.VMID, boolean)
>
> java.rmi.dgc.Lease dirty(java.rmi.server.ObjID[], long, java.rmi.dgc.Lease)

 **2.不知道Server服务端口咋办？**

如果通过Registry#list、Registry#lookup，去查询Service的话，返回的代理对象内部是记录了Server的服务端口的，但该方式要求你的classpath下存在Service对应的接口类，否则在将抛出ClassNotFoundException。

方案: 直接解析Java反序列化字节数组，获取服务端口。

![1647003958_622b49364c95ae9c0fb5c.png!small](https://image.3001.net/images/20220311/1647003958_622b49364c95ae9c0fb5c.png!small)

![1647003967_622b493f1d36ac9aaea12.png!small?1647003967055](https://image.3001.net/images/20220311/1647003967_622b493f1d36ac9aaea12.png!small?1647003967055)

备注:

这里依赖一个Java反序列化字节解析工具me.trini7.run.serializes.bytes.SerializationProtocols，它根据序列化协议实现，可以在不依赖classpath的情况下解析出对象数据，并以JSON格式展示，后续有机会介绍反序列化协议时会在展开介绍。

lookup接口返回的是一个代理对象，其中服务端口的存储较为特殊，非代理对象及其字段对象的直接属性，其隐蔽的写入在java.rmi.server.RemoteObject#writeObject中，根据逻辑逆向出上述解码代码。

 **3.Attack**

![1647004005_622b4965baa0153792654.png!small?1647004005767](https://image.3001.net/images/20220311/1647004005_622b4965baa0153792654.png!small?1647004005767)

### 攻击RMI Client

略

## 四、JEP290

以上的攻击演示Registry、Server环境JDK版本为8u77，而当目标环境版本为8u121+时，攻击将不再有效。

![1647004073_622b49a94456445b5742c.png!small?1647004073330](https://image.3001.net/images/20220311/1647004073_622b49a94456445b5742c.png!small?1647004073330)

上述原因及为JDK为反序列化攻击提供的缓解方案: JEP290(<http://openjdk.java.net/jeps/290>),
其最早在JDK9中引入，后续向下移植到老版本的JDK中（JDK 8u121、JDK 7u131、JDK
6u141），JEP290支持创建自定义过滤器，在反序列化时检查对象类型。

 **Registry ObjID Filter:** sun.rmi.registry.RegistryImpl#registryFilter

> 只允许反序列化: String, Number, Remote, Proxy, UnicastRef, RMIClientSocketFactory,
> RMIServerSocketFactory, ActivationID, UID及子类

 **DGC ObjID Filter:** sun.rmi.transport.DGCImpl#checkInput

> 只允许反序列化: ObjID、UID、VMID、Lease

## 五、JEP290后的攻击

### 攻击RMI Registry

Yso的方案: **ysoserial.exploit.JRMPListener & ****ysoserial.payloads.JRMPClient**

 **使用** **yso.** **JRMPListener建立一个恶意的** Registry, 其针对来连接的RMI Server Or RMI
Client会返回恶意Payload序列化字节流。

使用 **yso.JRMPClient攻击正常的** Registry，使用对恶意Registry发起请求。当对返回的字节流做序列化时候被攻击。

![1647004132_622b49e413b0e1ea3ef53.png!small?1647004132150](https://image.3001.net/images/20220311/1647004132_622b49e413b0e1ea3ef53.png!small?1647004132150)

备注: 这里的突破8u121的核心逻辑是， **正常的** Registry(Client角色)，
去连接恶意Registry后，会对恶意Registry进行一次DGC#dirty的调用，并在未配置FIlter的情况下反序列化返回值。在后续的8u241中修复了该问题。

### 攻击RMI Server

####

之前的介绍中，通过DGC
ObjID去攻击Server，由于增加了Filter而无法生效，但如果Server提供的Service也接受了Object类型的参数，利用JRMPCall攻击仍然有效(通过lookup获取objID，计算methodhash即可)。

如何获取Server提供的Service methods呢？ **RMI提供的动态类下载是个机会:**

> <https://docs.oracle.com/javase/8/docs/technotes/guides/rmi/codebase.html>

RMI
Codebase支持客户端从服务端下载本地不存在的类，我们可以以此来获取获取Service并分析弱点方法(存在Object类型参数)，自动根据lookup返回的objID及计算出methodhash，及自动Fuzz参数填充(Object类型参数填充payload)，完成自动化攻击。

 **0x00 解析codebase**

![1647004230_622b4a466bab19f82f2d0.png!small?1647004230735](https://image.3001.net/images/20220311/1647004230_622b4a466bab19f82f2d0.png!small?1647004230735)

 **0x01 通过codebase远程下载类 & 自动分析弱点方法 (注意别被反杀了:)**

![1647004235_622b4a4b7cac31bea1e9d.png!small?1647004236775](https://image.3001.net/images/20220311/1647004235_622b4a4b7cac31bea1e9d.png!small?1647004236775)

 **0x02 攻击弱点方法(含参数自填充)**

![1647004239_622b4a4f7098dacc1a8c4.png!small?1647004239729](https://image.3001.net/images/20220311/1647004239_622b4a4f7098dacc1a8c4.png!small?1647004239729)

 **0x03 Attack**

![1647004242_622b4a52d153c59c00837.png!small?1647004243017](https://image.3001.net/images/20220311/1647004242_622b4a52d153c59c00837.png!small?1647004243017)

  

