可能师傅们也遇到过这种情况：因为问题A跟进某个类方法，调试期间遇到一个更纠结的问题B，在费尽周折终于搞清楚后，蓦然回首却忘了自己在干什么（问题A）......  

JavaRMI与相关攻击面错综复杂，因此本文仅以时间线梳理各种绕过方法与缓解措施的主要逻辑，而不会详述具体调用栈（但会指出关键类方法）。大家可以自行跟进加深印象，也可以参考其它师傅的文章云调试。

RMI全称是Remote Method
Invocation（远程方法调用），可以理解为远程过程调用（RPC）的Java实现版本。它使得应用程序员可以像调用本地方法一样（stub.func(arg)），调用远程主机上提供的方法，方法实际最终在远程主机上执行（serv.func(arg)），原因是本地类封装了与远程类基于
**序列化** 的网络通信（socket）。

我们将上述提供业务方法的远程主机称为服务端，将发起方法调用的本地主机称为客户端。服务端会监听在一个随机端口上，将自己的通信地址等信息封装后（stub）由某种途径交给客户端。这种途径就是默认监听在1099端口上的注册端。

RMI全称是Remote Method
Invocation（远程方法调用），可以理解为远程过程调用（RPC）的Java实现版本。它使得应用程序员可以像调用本地方法一样（stub.func(arg)），调用远程主机上提供的方法，方法实际最终在远程主机上执行（serv.func(arg)），原因是本地类封装了与远程类基于
**序列化** 的网络通信（socket）。

我们将上述提供业务方法的远程主机称为服务端，将发起方法调用的本地主机称为客户端。服务端会监听在一个随机端口上，将自己的通信地址等信息封装后（stub）由某种途径交给客户端。这种途径就是默认监听在1099端口上的注册端。

![](https://image.3001.net/images/20220223/1645583961_62159e59936c655406481.png!small)

##  **攻击业务危险方法**

如果远程方法实现中存在输入流可控的危险方法：

    
    
    clazz {
        func(arg) {
            exec(arg)
        }
    }

理论上就跟利用Web应用漏洞一样，RMI此时就是一个毫无存在感的中间层。实际情况是基本没有能直接调用到的危险方法，而且也不知道危险方法的调用接口（clazz.func(arg)）。

  * java.rmi.server.useCodebaseOnly在7u21|6u45时由默认false改为true，下文均需要被攻击端存在gadgets。另外为了行文流畅，8u241对String类型反序列化作的变动放在文末统一说明。

##  **攻击远程方法参数**

当服务端并不存在危险业务方法，但我们可以拿到远程方法接口类（比如开源应用）。发现它接收一个Object类型参数（func(Object arg,
...)），在此处传入恶意payload对象，服务端从网络接收数据并试图反序列化还原对象时，就会触发gadgets。

相比Object类型，远程方法入参更有可能是int、boolean等基本数据类型，或是String以及其它封装类。客户端会根据方法名及参数类型生成哈希，服务端收到这个哈希就能知道调用的是哪一个方法（sun.rmi.server.UnicastServerRef#hashToMethod_Map）。

那么把恶意对象强行塞给非Object参数能否触发反序列化执行呢？当远程方法参数为非基本数据类型时，sun.rmi.server.UnicastRef#unmarshalValue就会进入readObject所在分支。通过修改网络数据、修改字节码、修改内存对象、修改RMI客户端实现
任意一种方法，将方法哈希修改为服务端存在且符合类型要求的远程方法哈希，即可触发强行塞入的恶意对象。

![](https://image.3001.net/images/20220223/1645584287_62159f9f2021ddf587064.png!small)

##  **攻击RMI注册端**

抛开具体业务远程方法，Registry也提供了基本方法：

  * bind(String, Remote)
  * list()
  * lookup(String)
  * rebind(String, Remote)
  * unbind(String)

除了list方法不会向 **注册端**
传递参数，其余四个方法的任意参数都会被注册端接收并readObject（sun.rmi.registry.RegistryImpl_Skel#dispatch），要解决的问题是如何让恶意对象符合类型要求。

[BaRMIe](https://github.com/NickstaDB/BaRMIe/blob/master/src/nb/barmie/net/proxy/thread/BindPayloadInjectingProxyThread.java)采用代理注册端，通过handleData方法替换字节流数据，最终形成bind(payload,
null)。

[ysoserial.exploit.RMIRegistryExploit](https://github.com/frohoff/ysoserial/blob/master/src/main/java/ysoserial/exploit/RMIRegistryExploit.java#L75)采用动态代理，通过createMemoitizedProxy方法封装为Remote，最终形成bind("pwnedXXX",
payload)。

我们也可以自己创建一个类并实现Remote,
Serializable，将payload对象赋值放入任意类属性。虽然注册端递归反序列化后最终会找不到自定义类报错，但在此之前会先触发gadgets。

![](https://image.3001.net/images/20220223/1645584398_6215a00e64cefd17c7544.png!small)

在JEP290（8u121，7u131，6u141）加入的sun.rmi.registry.RegistryImpl#registryFilter会限制递归深度、数组长度，并基于白名单递归检查类型，会拦截payload的最终执行。

![](https://image.3001.net/images/20220223/1645584442_6215a03ad5bca9b230b2f.png!small)此外在8u141将dispatch中原来的先readObject再RegistryImpl.checkAccess（默认仅允许注册端与服务端同地址），修正为了先作检查。会使攻击者伪装成服务端向注册端发起bind/rebind/unbind的攻击失效，但不会影响攻击者作为客户端发起lookup。

##  **攻击DGC服务**

DGC全称是Distributed Garbage
Collection，顾名思义其实就是GC（垃圾回收）的分布式方案。与Registry类似，DGC服务也提供了基本方法dirty()和clean()。客户端需要用到
**注册端** 或 **服务端** 的远程对象时，会通过dirty申请。相应的，当客户端不再需要时则会通过clean注销。

而同样与Registry类似， **注册端** 或 **服务端**
上的sun.rmi.transport.DGCImpl_Skel#dispatch，会接收DGC客户端经由dirty或clean传过来的部分数据并readObject，要解决的问题是sun.rmi.transport.DGCImpl_Stub#dirty并没有一个参数接口用于传递对象。

对此，[ysoserial.exploit.JRMPClient](https://github.com/frohoff/ysoserial/blob/master/src/main/java/ysoserial/exploit/JRMPClient.java#L55)按照DGC通信的固定格式直接走socket通信在相应位置写入了payload，最终形成[0x4a524d49,
2, 0x4c, 0x50| 2, 0, 0, 0, 1, -669196253586618813L, payload]的数据流。

![](https://image.3001.net/images/20220223/1645587721_6215ad09e41c3a2b34c1f.png!small)

在JEP290加入的sun.rmi.transport.DGCImpl#checkInput逻辑也与之前相同，会拦截payload的最终执行。

##  **攻击JRMP客户端**

RMI和DGC服务都是基于JRMP协议通信，就像HTTP应用与TCP之间会有Web服务器处理HTTP协议一样，JRMP也有相应的处理模块。我们将主动发起JRMP请求的一方称为JRMP客户端，将监听JRMP请求的一方成为JRMP服务端。

JEP290主要通过白名单限制了RMI服务端与DGC服务（注册端或服务端）readObject时能使用的类，却没有限制JRMP客户端处理JRMP服务端返回的异常信息readObject（sun.rmi.transport.StreamRemoteCall#executeCall）。

同上文所述，JRMP服务端的sun.rmi.transport.Transport#serviceCall等位置都是直接writeObject(Exception)，所以需要实现恶意JRMP服务端在JRMP客户端发起连接时，将payload走异常接口给抛回去。

[ysoserial.exploit.JRMPListener](https://github.com/frohoff/ysoserial/blob/8eb5cbfbf6c47a23682f6186bea9baf6439e57b9/src/main/java/ysoserial/exploit/JRMPListener.java#L244)就是这种实现，构造为[81,
2, payload]的数据返回给JRMP客户端，使其进入异常处理触发payload。

###  **寻找Gadgets**

  * DGCClient implements the client side of the RMI distributed garbage collection system. The external interface to DGCClient is the registerRefs() method. When a LiveRef to a remote object enters the JVM, it must be registered with the DGCClient to participate in distributed garbage collection. When the first LiveRef to a particular remote object is registered, a dirty() call is made to the server-side DGC for the remote object.

可以知道当LiveRef加载进JVM后，会通过registerRefs注册并发起dirty请求。[ysoserial.payloads.JRMPClient](https://github.com/frohoff/ysoserial/blob/8eb5cbfbf6c47a23682f6186bea9baf6439e57b9/src/main/java/ysoserial/payloads/JRMPClient.java#L71)以sun.rmi.server.UnicastRef#readExternal充当反序列化入口，在其中装填了sun.rmi.transport.LiveRef，借由DGC机制便可主动发起JRMP请求。

如果有地方能够触发这个反序列化入口，就可以让它成为JRMP客户端向恶意JRMP服务端发起请求，进而走没被限制的异常readObject触发最终payload。刚好UnicastRef是RegistryImpl#registryFilter的白名单类，原汤化原食了。

###  **触发反序列化**

[ysoserial.exploit.RMIRegistryExploit](https://github.com/frohoff/ysoserial/blob/master/src/main/java/ysoserial/exploit/RMIRegistryExploit.java#L77)利用的registry.bind(name,
remote)在8u141后失效了，[ysomap.exploits.rmi.RMIRegistryExploit](https://github.com/wh1t3p1g/ysomap/blob/master/core/src/main/java/ysomap/exploits/rmi/RMIRegistryExploit.java#L76)使用的Naming.lookup(registry,
remote)则依然有效。

同样要解决让第一步的payload符合类型要求的问题。要么依托原RMI客户端发起lookup，找一个实现了Remote且能存放LiveRef的类（比如RemoteObjectInvocationHandler），或者利用递归反序列化特性自己构造类；要么重新实现RMI客户端强行发送数据。

  * 前者找类并测试会遇到一个与类型相关很有意思的问题

![](https://image.3001.net/images/20220223/1645588081_6215ae7142a0625c1bd67.png!small)[8u231](https://github.com/openjdk/jdk/commit/55fc1fb794937091c11b40f674cc52b3560c3300)捕获了在加载Ref（第一步的payload）后会触发的异常，在发起JRMP请求（releaseInputStream）之前清除了Ref。

![](https://image.3001.net/images/20220223/1645595154_6215ca12e7bc08b318998.png!small)

并且将dirty和clean中的setObjectInputFilter(DGCImpl_Stub::leaseFilter)过滤器提到了JRMP请求发起之后、恶意JRMP服务端最终gadgets触发之前（ref.invoke(call))的位置。

细看可以发现缓解措施针对的都是加载Ref（第一步的payload）之后的过程，当有一个gadgets能在加载自身就触发JRMP请求，就能绕过这些过滤，An
Trinhs找到了一条这样的链：

1\. UnicastRemoteObject#readObject

2.RMIServerSocketFactory#createServerSocket

3.RemoteObjectInvocationHandler#invoke

利用动态代理机制封装了类，同时gank了本来的方法调用，将其引入invoke。

![](https://image.3001.net/images/20220223/1645595194_6215ca3ae31db53ecf788.png!small)

从OracleJDK-8u241/[OpenJDK-8u242](https://github.com/openjdk/jdk8u/commit/9fb68f29a5fc2bf5407e72f96ca6cd81be1af6e8#diff-9071564785e3fe39d109f0bb6b72a651)开始将多处readObject再转型String的地方修改为了SharedSecrets.getJavaObjectInputStreamReadString().readString，修复了lookup时的反序列化入口，并且影响上文
**攻击远程方法参数** 和 **攻击RMI注册端** 中涉及String类型参数的地方。

##  **反制攻击方**

最后稍微聊一下喜闻乐见的反制问题，ysoserial在[477ecb8](https://github.com/frohoff/ysoserial/commit/477ecb8f05f42b0195a67d9712e97f2c6d31e1da)更新了一个无限制的registry.list()，哪怕在8u261中依然是写着赤果果的readObject：

![](https://image.3001.net/images/20220223/1645595226_6215ca5a83299fdadf6fc.png!small)

而在那个commit之前，也许作者是想借由原生的registry.bind(name,
remote)得到注册端回显，方便攻击时判断gadgets环境，为此其戴了ExecCheckingSecurityManage作为安全措施（/doge），但还是可以通过CC链读写文件等方式间接溯源或者RCE。

##  **参考内容**

[Attacking Java RMI services after JEP
290](https://mogwailabs.de/en/blog/2019/03/attacking-java-rmi-services-after-jep-290/)

[针对RMI服务的九重攻击 - 下](https://xz.aliyun.com/t/7932)

[JEP 290: Filter Incoming Serialization
Data](https://openjdk.java.net/jeps/290)

[Understanding distributed garbage
collection](https://www.ibm.com/docs/en/sdk-java-technology/8?topic=iiop-understanding-distributed-garbage-collection)

[30行代码透彻解析RPC](https://www.bilibili.com/video/BV17Z4y1s7cG)

