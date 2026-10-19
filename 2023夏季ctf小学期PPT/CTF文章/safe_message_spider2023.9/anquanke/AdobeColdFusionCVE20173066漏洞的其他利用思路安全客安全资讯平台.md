# Adobe ColdFusion：CVE-2017-3066漏洞的其他利用思路

阅读量 **139345**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-03-16 15:02:26

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Matthias Kaiser ，文章来源：https://codewhitesec.blogspot.hk/

原文地址：<https://codewhitesec.blogspot.hk/2018/03/exploiting-adobe-coldfusion.html>

译文仅供参考，具体内容表达以及含义原文为准。

## 一、前言

在最近一次渗透测试任务中，我的小伙伴Thomas遇到了几台服务器，这几台服务器上运行着Adobe ColdFusion
11以及12平台，其中某些服务器存在CVE-2017-3066漏洞，但无法通过TCP协议外连，因此无法利用这个漏洞。Thomas向我求助，问我是否有办法帮他获取SYSTEM权限的shell，因此我把我所做的工作汇成这篇文章与大家一起分享。

## 二、Adobe ColdFusion & AMF简介

在讨论技术细节之前，我先简单介绍一下Adobe ColdFusion（CF）。Adobe
ColdFusion是类似ASP.net之类的应用程序开发平台（Application Development
Platform），然而诞生时间要更为久远。开发者可以使用Adobe ColdFusion来搭建网站、SOAP以及REST Web服务，使用Action
Message Format（AMF）与Adobe Flash进行交互。

AMF协议是一种自定义的二进制序列化协议。该协议有两种格式：AMF0以及AMF3。一个Action
Message由头部（header）以及主体（body）所组成。AMF0以及AMF3中支持多种数据类型。比如，AMF3格式支持的协议元素以及类型标识符如下所示：

    
    
    Undefined      - 0x00
    Null           - 0x01
    Boolean        - 0x02
    Boolean        - 0x03
    Integer        - 0x04
    Double         - 0x05
    String         - 0x06
    XML            - 0x07
    Date           - 0x08
    Array          - 0x09
    Object         - 0x0A
    XML End        - 0x0B
    ByteArray      - 0x0C
    

如果想了解AMF0以及AMF3二进制消息格式的详细内容，大家可以查阅相关[维基百科](https://en.wikipedia.org/wiki/Action_Message_Format)页面。

不同语言中关于AMF的具体实现也有所不同。对于Java来说，我们可以使用Adobe BlazeDS（现在是Apache BlazeDS），Adobe
ColdFusion中也用到了这个技术。

BlazeDS AMF序列化器（serializer）可以序列化复杂的对象图（object graph）。序列化器会从根对象（root
object）开始处理，递归序列化根对象成员。

在序列化复杂对象方面，BlazeDS支持两种常用的序列化技术：

1、序列化Bean属性（AMF0以及AMF3）；

2、使用Java的`java.io.Externalizable`接口来序列化（AMF3）。

###  序列化Bean属性

这种技术需要待序列化的对象具有公开的无参数构造函数，每个成员都拥有公开的Getter以及Setter方法（符合JavaBeans规范）。

为了收集某个对象所有的成员值，AMF序列化器会在序列化过程中调用所有的Getter方法。成员名、成员值以及对象的类名存放在Action消息的body区中。

在反序列化过程中，程序会从Action消息中获取类名，构造新的对象，然后以成员值作为参数调用每个成员名对应的set方法。这一个过程由专门的方法来实现，比如`flex.messaging.io.amf.Amf3Input`类中的`readScriptObject()`方法或者`flex.messaging.io.amf.Amf0Input`类中的`readObjectValue()`方法。

### 使用`java.io.Externalizable`接口序列化

如果某些类实现（implement）了`java.io.Externalizable`接口（继承自`java.io.Serializable`），BlazeDS还支持这些类的复杂对象的序列化。

    
    
    public abstract interface Externalizable
      extends Serializable
    {
      public abstract void writeExternal(ObjectOutput paramObjectOutput)
        throws IOException;
    
      public abstract void readExternal(ObjectInput paramObjectInput)
        throws IOException, ClassNotFoundException;
    }
    

实现这一接口的每个类都需要自己提供反序列化逻辑，调用相关方法来处理`java.io.ObjectInput`对象，读取序列化后的类型及字符串（比如`method
read(byte[] paramArrayOfByte)`）。

在AMF3中对某个对象（类型标识符为0xa）进行反序列化时，会调用`flex.messaging.io.amf.Amf3Input`类的`readScriptObject()`方法。在如下代码的759行，`readExternalizable`方法会被调用，该方法会在待反序列化的对象上调用`readExternal()`方法。

    
    
    /*      */   protected Object readScriptObject()
    /*      */     throws ClassNotFoundException, IOException
    /*      */   {
    /*  736 */     int ref = readUInt29();
    /*      */     
    /*  738 */     if ((ref & 0x1) == 0) {
    /*  739 */       return getObjectReference(ref >> 1);
    /*      */     }
    /*  741 */     TraitsInfo ti = readTraits(ref);
    /*  742 */     String className = ti.getClassName();
    /*  743 */     boolean externalizable = ti.isExternalizable();
    /*      */     
    /*      */
    /*      */
    /*  747 */     Object[] params = { className, null };
    /*  748 */     Object object = createObjectInstance(params);
    /*      */     
    /*      */
    /*  751 */     className = (String)params[0];
    /*  752 */     PropertyProxy proxy = (PropertyProxy)params[1];
    /*      */     
    /*      */
    /*  755 */     int objectId = rememberObject(object);
    /*      */     
    /*  757 */     if (externalizable)
    /*      */     {
    /*  759 */       readExternalizable(className, object); //<- call to readExternal
    /*      */     }
    /*      */     //...
    /*      */   }
    

阅读上述文字后，大家应该对Adobe ColdFusion以及AMF有了基本的了解。

## 三、已有成果

Chris Gates（[@Carnal0wnage](https://github.com/Carnal0wnage
"@Carnal0wnage")）之前发表过一篇[文章](http://www.carnal0wnage.com/papers/LARES-ColdFusion.pdf)，详细介绍了如何渗透测试ColdFusion，是难得的一篇好文。

Wouter Coekaerts（[@WouterCoekaerts](https://github.com/WouterCoekaerts
"@WouterCoekaerts")）也在自己的[博客](http://wouter.coekaerts.be/2011/amf-arbitrary-code-execution)中提到，反序列化不可信的AMF数据是非常危险的一种行为。

如果在Flexera/Secunia数据库中查找历史上已有的Adobe
ColdFusion漏洞信息，你会发现这些漏洞大多数为XSS、XXE或者信息泄露漏洞。

最近的几个漏洞为：

    
    
    通过RMI实现不可信数据的反序列化（CVE-2017-11283/4 by @nickstadb）
    XXE（CVE-2017-11286 by Daniel Lawson of @depthsecurity）
    XXE（CVE-2016-4264 by @dawid_golunski）
    

## 四、CVE-2017-3066

2017年，AgNO3 GmbH的Moritz Bechler以及我的小伙伴Markus Wulftange各自独立发现了Apache
BlazeDS中的CVE-2017-3066漏洞。

这个漏洞的要点是Adobe Coldfusion中没有采用可信类的白名单机制。因此如果某个类位于Adobe
ColdFusion的类路径（classpath）中，只要这些类符合Java
Beans规范或者实现了`java.io.Externalizable`，那么就可以发送到服务器进行反序列化。Moritz和Markus两个人都发现，实现了`java.io.Externalizable`接口的JRE类（`sun.rmi.server.UnicastRef2`以及`sun.rmi.server.UnicastRef`）会在AMF3反序列化过程中触发一个TCP出站连接。当成功连接到攻击者的服务器后，程序会使用Java的原生反序列化方法（`ObjectInputStream.readObject()`）来反序列化服务器的响应数据。这两个人都找到了一个非常好的“桥梁”，可以将AMF反序列化与Java的原生反序列化过程结合起来，这样许多公开的利用代码就可以用在这种场景中。大家可以访问Markus的[博客](http://codewhitesec.blogspot.de/2017/04/amf.html)了解关于该漏洞的详细信息。Apache通过`flex.messaging.validators.ClassDeserializationValidator`类引入了一种验证机制，其中包含一个默认的白名单，但也可以使用配置文件来进行配置。详细信息可以查阅Apache
BlazeDS的发行[说明](http://www.apache.org/dist/flex/BlazeDS/4.7.3/RELEASE_NOTES)。

## 五、CVE-2017-3066的其他利用思路

本文开头提到过，我的小伙伴Thomas向我请求帮助，希望能够在没有出站连接的条件下同样能够利用这个漏洞。

先前我已经快速阅读过 Moritz Bechler发表的研究论文（[Java Unmarshaller
Security](https://github.com/mbechler/marshalsec/blob/master/marshalsec.pdf)），论文中他分析了几种“Unmarshaller”，其中就包括BlazeDS。Moritz
Bechler所提供的漏洞利用载荷不适用我们这种场景，因为classpath中缺少相关的库。

因此我还是决定按照自己常用的方法来挖掘。面对Java时，我首先会想到我最喜欢的“逆向工程工具”：Eclipse。Eclipse配上强大的反编译插件[JD-Eclipse](https://github.com/java-decompiler/jd-eclipse)就足以应付动态以及静态分析场景。之前我也是一名开发者，习惯于使用IDE，这样开发起来能够更加方便，使非常低效且容易出错的反编译工作能够顺利推进。我新建了一个Java工程，将Adobe
Coldfusion 12的所有jar文件以外部库方式添加到工程中。

首先我想到的是寻找对Java的`ObjectInputStream.readObject`方法的进一步调用情况。使用Eclipse可以轻松完成这个任务，只需要打开`ObjectInputStream`类，右键点击`readObject()`方法，然后点击“Open
Call Hierarchy”即可。感谢JD-Eclipse以及反编译器的强大功能，Eclipse可以根据收集到的类信息，在没有源代码的情况下重新构造整个函数调用图。调用图最开始看起来规模非常庞大，但只要具备一定经验，你很快就能发现整张图中哪些节点比较有趣。经过几个小时的分析后，我找到了两个比较有希望的调用图。

###  基于SETTER方法的利用技术

第一个切入点源自于`org.jgroups.blocks.ReplicatedTree`类的`setState(byte[] new_state)`方法。

![](https://p4.ssl.qhimg.com/t01e7dbb11c823e6a41.png)

阅读这个方法的实现代码，我们可以想象第605行会出现什么状况。

    
    
    /*      */   public void setState(byte[] new_state)
    /*      */   {
    /*  597 */     Node new_root = null;
    /*      */     
    /*      */
    /*  600 */     if (new_state == null) {
    /*  601 */       if (log.isInfoEnabled()) log.info("new cache is null");
    /*  602 */       return;
    /*      */     }
    /*      */     try {
    /*  605 */       Object obj = Util.objectFromByteBuffer(new_state);
    /*  606 */       new_root = (Node)((Node)obj).clone();
    /*  607 */       root = new_root;
    /*  608 */       notifyAllNodesCreated(root);
    /*      */     }
    /*      */     catch (Throwable ex) {
    /*  611 */       if (log.isErrorEnabled()) { log.error("could not set cache: " + ex);
    /*      */       }
    /*      */     }
    /*      */   }
    

快速查看函数调用图后，我们确认调用链的最后一个节点是调用`ObjectInputStream.readObject()`。

这里只需要注意一件事情：传递给`setState()`的`byte[]`参数在`0x0`偏移处有一个额外的字节`0x2`，我们可以在`org.jgroups.util.Util`类的364行代码中看到这个信息。

    
    
    /*      */   public static Object objectFromByteBuffer(byte[] buffer, int offset, int length) throws Exception
    /*      */   {
    /*  358 */     if (buffer == null) return null;
    /*  359 */     if (JGROUPS_COMPAT)
    /*  360 */       return oldObjectFromByteBuffer(buffer, offset, length);
    /*  361 */     Object retval = null;
    /*  362 */     InputStream in = null;
    /*  363 */     ByteArrayInputStream in_stream = new ByteArrayInputStream(buffer, offset, length);
    /*  364 */     byte b = (byte)in_stream.read();
    /*      */     try {
    /*      */       int len;
    /*  367 */       switch (b) {
    /*      */       case 0:
    /*  369 */         return null;
    /*      */       case 1:
    /*  371 */         in = new DataInputStream(in_stream);
    /*  372 */         retval = readGenericStreamable((DataInputStream)in);
    /*  373 */         break;
    /*      */       case 2:
    /*  375 */         in = new ObjectInputStream(in_stream);
    /*  376 */         retval = ((ObjectInputStream)in).readObject();
    /*      */       //...
    /*      */       }
    /*      */      }
    /*      */ }
    

漏洞利用情况如下图所示：

![](https://p0.ssl.qhimg.com/t01a2d368e25deb1702.png)

这个漏洞利用方法针对的是Adobe ColdFusion 12，并且只有启用JGroups时才能利用成功。

###  基于Externalizable的利用技术

第二个切入点源自于`org.apache.axis2.util.MetaDataEntry`类的`readExternal`方法。

![](https://p5.ssl.qhimg.com/t01a61ec483bcc8d0b9.png)

在代码中的297行，程序会调用`SafeObjectInputStream.install(inObject)`方法。

    
    
    /*     */   public static SafeObjectInputStream install(ObjectInput in)
    /*     */   {
    /*  62 */     if ((in instanceof SafeObjectInputStream)) {
    /*  63 */       return (SafeObjectInputStream)in;
    /*     */     }
    /*  65 */     return new SafeObjectInputStream(in) ;
    /*     */   }
    

在这个函数中，我们的`AMF3Input`实例属于`org.apache.axis2.context.externalize.SafeObjectInputStream`类的一个实例。

    
    
    /*     */   private Object readObjectOverride()
    /*     */     throws IOException, ClassNotFoundException
    /*     */   {
    /* 318 */     boolean isActive = in.readBoolean();
    /* 319 */     if (!isActive) {
    /* 320 */       if (isDebug) {
    /* 321 */         log.debug("Read object=null");
    /*     */       }
    /* 323 */       return null;
    /*     */     }
    /* 325 */     Object obj = null;
    /* 326 */     boolean isObjectForm = in.readBoolean();
    /* 327 */     if (isObjectForm)
    /*     */     {
    /* 329 */       if (isDebug) {
    /* 330 */         log.debug(" reading using object form");
    /*     */       }
    /* 332 */       obj = in.readObject();
    /*     */     } else {
    /* 334 */       if (isDebug) {
    /* 335 */         log.debug(" reading using byte form");
    /*     */       }
    /*     */       
    /* 338 */       ByteArrayInputStream bais = getByteStream(in);
    /*     */       
    /*     */
    /* 341 */       ObjectInputStream tempOIS = createObjectInputStream(bais);
    /* 342 */       obj = tempOIS.readObject();
    /* 343 */       tempOIS.close();
    /* 344 */       bais.close();
    /*     */     }
    /*     */   //...
    /*     */   }
    

上述代码的341行会创建`org.apache.axis2.context.externalize.ObjectInputStreamWithCL`类的一个新的实例，这个类扩展了（extend）标准的`java.io.ObjectInputStream`类。在第342行，我们最终实现了对`readObject()`方法的调用。

漏洞利用情况如下图所示：

![](https://p2.ssl.qhimg.com/t01af0a34d011584aa7.png)

这种漏洞利用方法适用于Adobe ColdFusion 11以及12。

###  COLDFUSIONPWN工具

为了让我们的工作更加轻松，我开发了一款简单的工具：
**[ColdFusionPwn](https://github.com/codewhitesec/ColdFusionPwn)**
。这是一款命令行工具，我们可以通过该工具生成序列化后的AMF消息。该工具可以与Chris Frohoff的ysoserial配合使用生成gadget。

## 六、总结

毋庸置疑，反序列化不可信的输入数据并不是一件好事。从攻击者的角度来看，利用反序列化漏洞是一项富有挑战性的任务，因为他们需要找到“正确”的对象（即gadget），才能触发漏洞、构造利用路径，然而这也是非常有趣的一个探索历程。

顺便提一句：如果你想深入了解服务端的Java利用技术，理解Java中的各种反序列化漏洞，正确开展静态以及动态分析，那么你应该会对我们即将推出的“Java高级利用技术”课程感兴趣。

本文翻译自https://codewhitesec.blogspot.hk/
[原文链接](https://codewhitesec.blogspot.hk/2018/03/exploiting-adobe-coldfusion.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/101176](/post/id/101176)

安全客 - 有思想的安全新媒体

本文转载自:
[https://codewhitesec.blogspot.hk/](https://codewhitesec.blogspot.hk/2018/03/exploiting-adobe-coldfusion.html)

如若转载,请注明出处： <https://codewhitesec.blogspot.hk/2018/03/exploiting-adobe-coldfusion.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Adobe ColdFusion](/tag/Adobe ColdFusion)
  * [反序列化](/tag/反序列化)
  * [CVE-2017-3066](/tag/CVE-2017-3066)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

