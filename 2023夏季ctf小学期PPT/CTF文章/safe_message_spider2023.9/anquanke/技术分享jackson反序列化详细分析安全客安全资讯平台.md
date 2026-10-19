# 【技术分享】jackson反序列化详细分析

阅读量 **397337**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-07-18 15:00:11

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

****

作者：[PandaIsCoding](http://bobao.360.cn/member/contribute?uid=2929519300)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**前言**

这是今年四月份被公开的jackson反序列化漏洞，不过目前看来利用比较鸡肋，本篇只以技术学习的角度来分析这个漏洞，如有问题，还望大牛批评指出。

  

**漏洞情况**

Jackson是一套开源的java序列化与反序列化工具框架，可将java对象序列化为xml和json格式的字符串及提供对应的反序列化过程。该漏洞的触发条件是ObjectMapper反序列化前调用了enableDefaultTyping方法。该方法允许json字符串中指定反序列化java对象的类名，而在使用Object、Map、List等对象时，可诱发反序列化漏洞，导致可执行任意命令。

  

**影响版本**

Jackson 2.7(<2.7.10)

Jackson 2.8(<2.8.9)

  

**环境**

Jackson-2.8.8.jar

Jdk1.7.0_45(这里分析使用jdk1.7， 不能使用jdk1.8之上的版本，后面会解释说明)。

我们先看下漏洞的poc。

User.java:

Exp.java:

Main.java:

首先jackson会解析要转化json数据中的类，提取出类的变量和相应方法。我们在

BeamnPropertyMap.class->init(Collection<SettableBeanProperty> props)最后

_hashArea = hash处下上断点可以看出User.class的信息。

然后BeanDeserializer.class->vanillaDeserialize()函数，该函数会遍历json数据的key-value，

并将类中key变量设置为value值。

根据构造的json数据，jackson会首先设置User类object的值。

由于object的值是com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl。

Jackson会首先设置TemplatesImpl相关变量。

程序再次进入BeamnPropertyMap.class->init(Collection<SettableBeanProperty>
props)，在_hashArea中我们可以看到TemplatesImpl类的相关信息。

其中有三个是我们通过json传入得参数，其对应的函数分别为

    
    
    transletBytecodes :  private synchronized void com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.setTransletBytecodes(byte[][]),
    outputProperties:  public synchronized java.util.Properties com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.getOutputProperties(),
    transletName:  protected synchronized void com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.setTransletName(java.lang.String),

然后程序进入vanillaDeserialize函数，按照我们构造json数据 的key的顺序开始设置value值。

然后进入deserializeAndSet()函数,先调用setTransletBytecodes()函数设置

transletBytecodes的值。此时value值就是我们的exp数据。

然后调用setTransletName()函数设置transletName的值，此时的value就是我们传入得”p”.

最后一次循环处理key为outputProperties的情况。程序执行了getOutputProperties()方法。弹出计算器。

为什么执行getOutputProperties()函数后就算执行我们的exp呢（这里弹出计算器）,这里其实就是反序列化payload的构造问题了。这里是通过TemplatesImpl类来实现的反序列化利用的。其实就是TemplatesImpl中有个_bytecodes变量，用来存放类的字节的，当我们调用getOutputProperties()函数，就会加载bytecodes中的类，执行了我们的代码。相关内容具体可参考：http://drops.xmd5.com/static/drops/papers-14317.html这篇文章。

新版本的2.8.9就对反序列化所用的一些类进行了过滤:

添加了一个函数判断，来检测是否加载的类为反序列化漏洞常用类，如果是则报错。

现在回到一开始说的jdk的问题，最初测试时我是在jdk1.8.0_45环境下测试的，发现无法弹出计算器。然后又用了jdk1.7才弹出计算器的。

想想应该是jdk1.7到jdk1.8，com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl类有了变化，才导致反序列化利用失败的。

为了找到原因，我看了下jdk1.7
和jdk1.8中com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl类
调用getOutputProperties()执行流程有什么变化。

发现在getOutputProperties()调用后，执行defineTransletClasses()时两个版本有所区别。

Jdk1.7:

Jdk1.8:

可以看到jdk1.8多了个_tfactory.getExternalExtensionsMap()的处理。我们在jdk1.8的环境下跟踪下程序，发现到这里_tfactory的值为null,所以执行_tfactory.getExternalExtensionsMap()函数时会出错，导致程序异常，不能加载_bytecodes的中的类。

因为我们在构造json数据时，对com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl只设置了三个变量。没有设置_tfactory的值，所以这里_tfactory为null。

后来想想只要在构造json数据时，设置_tfactory的值，也许就能在jdk1.8下执行，测试时并没有成功，还是too young, too
simple, sometimes naive。

由上图可知，在jackson初始化com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl并没有获取设置_tfactory的相关函数，所以也无法设置_tfactory的值。目前还未想出来如何绕过。

  

**参考**

<http://bbs.pediy.com/thread-218416.htm>

<http://drops.xmd5.com/static/drops/papers-14317.html>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **PandaIsCoding** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86446](/post/id/86446)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t011f2416f5f80ad992.jpg)
PandaIsCoding

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

