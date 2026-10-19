# Fastjson <=1.2.47 远程代码执行漏洞分析

阅读量 **914628**

|评论 **11**

发布时间 : 2019-07-12 12:24:16

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01a305ff8c3d77587c.png)

作者：icematcha@云影实验室

### 0x00前言

近日，Fastjson被传爆出新的“0day”，也引起了大家的高度关注。云影实验室第一时间进行了跟进和分析，通过分析我们发现，此次的漏洞并不算新的漏洞，其实官方早在去年五月就已经推出了相关补丁修复，但可能没有发布相关的安全通告，导致许多用户没有及时升级处理，而在此次护网中就谣传变成了现在的“0day”。

![](https://p0.ssl.qhimg.com/t01c7fff445e0b2b762.png)

此次漏洞利用的核心点是java.lang.class这个java的基础类，在fastjson
1.2.48以前的版本没有做该类做任何限制，加上代码的一些逻辑缺陷，造成黑名单以及autotype的绕过。下面跟着代码看看这个类的具体应用。

### 0x01分析过程

Fastjson在开始解析json前会优先加载配置，在加载配置时会调用TypeUtils的addBaseClassMappings和loadClass方法将一些经常会用到的基础类和三方库存放到一个ConcurrentMap对象mappings中，类似于缓存机制。

![](https://p4.ssl.qhimg.com/t017d0d4f12a73c7c18.png)

![](https://p4.ssl.qhimg.com/t010608c497edb35858.png)

配置加载完成后正式开始解析json数据，在ParserConfig.checkAutoType方法中对’@type’对应的value进行处理。fastjson在1.2.2+版本默认便不再开启autoType选项，且在调用解析函数时我们没有传入预期的反序列化对象的对应类名时，fastjson则通过从mappings中或者deserializers.findClass()方法来获取反序列化对象的对应类。

![](https://p4.ssl.qhimg.com/t018e8d0b55a653b01d.png)

找到对应类后便返回，不再经过黑名单和autotype的检查流程。而java.lang.class该类恰好存在于deserializers对象的buckets属性中：

![](https://p1.ssl.qhimg.com/t01a9ecbabc79b3c5e3.png)

接着获取到java.lang.class对应的反序列化处理类MiscCodec：

![](https://p2.ssl.qhimg.com/t018d9653e89a021c46.png)

在MiscCodec类中，java.lang.class拥有加载任意类到mappings中的功能。首先从输入的json串中解析获取val对应的键值：

![](https://p4.ssl.qhimg.com/t015fb2c7995a8aa5fb.png)

![](https://p3.ssl.qhimg.com/t0133184f5749d2de6c.png)

获取后调用前面提到的TypeUtils. loadClass()方法对该键值进行类加载操作：

![](https://p4.ssl.qhimg.com/t011ac70cc36404f384.png)

在TypeUtils. loadClass()中，我们就可以看到当cache参数为true时，将键值对应的类名放到了mappings中后返回：

![](https://p1.ssl.qhimg.com/t01f090822ee0f48dbc.png)

Mappings是ConcurrentMap类的，顾名思义就是在当前连接会话生效。所以我们需要在一次连接会话同时传入两个json键值对时，此次连接未断开时，继续解析第二个json键值对。此时我们利用’@type’传入早已在黑名单中的com.sun.rowset.JdbcRowSetImpl类尝试jdni注入利用：

![](https://p5.ssl.qhimg.com/t0125f23a648bf03f8d.png)

可以看到fastjson直接从mappings中获取到了该类，并在做有效判断后，直接返回了:

![](https://p4.ssl.qhimg.com/t012ba625e2ccfda7ac.png)

此时的mappings中确实存在com.sun.rowset.JdbcRowSetImpl类：

![](https://p0.ssl.qhimg.com/t015636c1fd1ba92b13.png)

而就像前面已经提到的，黑名单以及autotype开关的检查是在上面那处return之后的，所以也就变相的绕过了黑名单以及autotype开关的检查。

![](https://p2.ssl.qhimg.com/t01bf5ce4411c64a85b.png)

![](https://p0.ssl.qhimg.com/t019db00b3623dc1561.png)

绕过了黑名单和autotype,剩下的利用过程就跟以前的利用完全一致了，利用jdni注入来RCE：

![](https://p2.ssl.qhimg.com/t014a9c4dcb99bc0b5c.png)

所以最终的漏洞利用其实是分为两个步骤，第一步利用java.lang.class加载黑名单类到mappings中，第二步直接从mappings中取出黑名单类完成漏洞利用。

### 0x02总结

回头来看看，我觉得该漏洞更像是一个逻辑漏洞，而不是依赖一些硬性的漏洞利用点，是代码的运行逻辑缺陷造成的漏洞利用。

在1.2.48版本的补丁中，首先黑名单做了更新，加了两条，其中应该包含了java.lang.class这个类：

![](https://p2.ssl.qhimg.com/t019b7902c66548a120.png)

MiscCodec中也将传入的cache参数置为了false：

![](https://p4.ssl.qhimg.com/t01821d4bdc90f5bcd8.png)

ParserConfig.checkAutoType()也调整了检查策略和逻辑。

![](https://p3.ssl.qhimg.com/t0176aa1429b4946c7d.png)

### 0x03修复建议

Fastjson在1.2.47及以下的版本受影响，请及时升级到1.2.48及以上版本。

### 0x04参考链接

<https://github.com/alibaba/fastjson>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **云影实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181874](/post/id/181874)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [fastjson](/tag/fastjson)

 **+1** __16赞

 __收藏

![](https://p3.ssl.qhimg.com/t012b723966029ed2c4.png) 云影实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

