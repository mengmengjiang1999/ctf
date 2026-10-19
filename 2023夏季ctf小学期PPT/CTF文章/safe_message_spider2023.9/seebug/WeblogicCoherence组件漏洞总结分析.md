**作者：kejaly@白帽汇安全研究院  
校对：r4v3zn@白帽汇安全研究院**

## 前言

Coherence 组件是 WebLogic 中的一个核心组件，内置在 WebLogic 中。关于 Coherence
组件的官方介绍：<https://www.oracle.com/cn/java/coherence/>

![](https://images.seebug.org/content/images/2021/08/589a7b70-5cee-455e-90e7-5b35a1c38bb2.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653081000-image-20210802113229602.png-w331s>

近些年，weblogic Coherence 组件反序列化漏洞被频繁爆出，苦于网上没有公开对 weblogic Coherence
组件历史反序列化漏洞的总结，导致很多想入门或者了解 weblogic Coherence 组件反序列化漏洞的朋友不知道该怎么下手，于是本文便对
weblogic Coherence 组件历史反序列化漏洞做出了一个总结和分析。

关于 Coherence 组件反序列化漏洞利用链的架构，我把他分为两个，一个是基于 `ValueExtractor.extract`
的利用链架构，另一个则是基于 `ExternalizableHelper` 的利用链架构。

# 前置知识

想理清 WebLogic 的 Coherence 组件历史反序列化漏洞需要首先了解一些 Coherence
组件反序列化漏洞中经常会涉及的一些接口和类。他们在 Coherence 组件反序列化漏洞利用中经常出现。

## ValueExtractor

`com.tangosol.util.ValueExtrator` 是一个接口：
![](https://images.seebug.org/content/images/2021/08/7d745dd1-567a-497a-8f54-a64c34a4da52.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653081000-image-20210725145241910.png-w331s>

在 Coherence 中 很多名字以 `Extrator` 结尾的类都实现了这个接口：
![](https://images.seebug.org/content/images/2021/08/e5fe47f7-6c03-4a26-9f7c-72044879e7db.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653081000-image-20210725145311604.png-w331s>

这个接口中声明了一个 `extract` 方法，而 `ValueExtractor.extract` 正是 Coherence 组件历史漏洞（
`ValueExtractor.extract` 链部分 ）的关键。

## ExternalizableLite

Coherence 组件中存在一个 `com.tangosol.io.ExternalizableLite`，它继承了
`java.io.Serializable`，另外声明了 `readExternal` 和 `writeExternal` 这两个方法。
![](https://images.seebug.org/content/images/2021/08/ebc0be24-fdd5-4725-a2ce-1b9430ac3711.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210728101447302.png-w331s>

`com.tangosol.io.ExternalizableLite` 接口 和 jdk 原生的 `java.io.Externalizable`
很像，注意不要搞混了。

## ExternalizableHelper

上面提到的 `com.tangosol.io.ExternalizableLite` 接口的实现类的序列化和反序列化操作，都是通过
`ExternalizableHelper` 这个类来完成的。

我们可以具体看 `ExternalizableHelper` 这个类是怎么对实现 `com.tangosol.io.ExternalizableLite`
接口的类进行序列化和反序列化的，这里以 `readObject` 方法为例，`writeObject` 读者可自行去查看：

![](https://images.seebug.org/content/images/2021/08/3626dd4b-d9d6-4911-90cb-f595cf661157.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210728102323560.png-w331s>

如果传入的`DataInput` 不是 `PofInputStream` 的话（Coherence 组件历史漏洞 涉及到的
`ExternalizableHelper.readObject` 传入的 `DataInput` 都不是
`PofInputStream`），`ExternalizableHelper#readObject` 中会调用
`ExternalizableHelper#readObjectInternal` 方法：

`readObjectInternal` 中会根据传入的中 `nType` 进行判断，进入不同的分支：
![](https://images.seebug.org/content/images/2021/08/b2c3efac-e40c-4253-99bb-7e314cbf9cff.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210728103543135.png-w331s>

对于实现 `com.tangosol.io.ExternalizableLite` 接口的对象，会进入到 `readExternalizableLite`
方法：

![](https://images.seebug.org/content/images/2021/08/31453603-e01f-4edf-9cae-fa2ef7d946c8.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210728104059476.png-w331s>

可以看到在 `readExternalizableLite` 中 1125 行会根据类名加载类，然后并且实例化出这个类的对象，然后调用它的
`readExternal()` 方法。

# 漏洞链

## ValueExtractor.extract

我们在分析反序列化利用链的时候，可以把链分为四部分，一个是链头，一个是危险的中间的节点（漏洞点），另一个是调用危险中间节点的地方（触发点），最后一个则是利用这个节点去造成危害的链尾。

在 Coherence 组件 `ValueExtractor.extract` 利用链架构中，这个危险的中间节点就是
`ValueExtractor.extract` 方法。

### 漏洞点

#### ReflectionExtractor

`ReflectionExtractor` 中的 `extract` 方法含有对任意对象方法的反射调用：
![](https://images.seebug.org/content/images/2021/08/4386c4de-6784-4236-a26a-fa78b04504c4.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210725151740093.png-w331s>

配合 `ChainedExtractor` 和 `ConstantExtractor` 可以实现类似 cc1 中的 `transform` 链的调用。

##### 涉及 CVE

CVE-2020-2555，CVE-2020-2883

#### MvelExtractor

`MvelExtrator` 中的 `extract` 方法，会执行任意一个 MVEL 表达式（RCE）：
![](https://images.seebug.org/content/images/2021/08/094aff6e-96e4-401e-9830-73c6832b7b74.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210725151958385.png-w331s>

而在序列化和反序列化的时候 `m_sExpr` 会参与序列化和反序列化：
![](https://images.seebug.org/content/images/2021/08/a038caa0-36ad-4125-852c-15cb2fae69e0.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210725152123268-16274409140731.png-w331s>

所以 `m_xExpr` 可控，所以就导致可以利用 `MvelExtrator.extrator` 来达到执行任意命令的作用。

##### 涉及 CVE

CVE-2020-2883

#### UniversalExtractor

`UniversalExtractor`（Weblogic 12.2.1.4.0 独有） 中的 `extract` 方法，可以调用任意类中的的 `get`
和 `is` 开头的无参方法，可以配合 `jdbsRowset`，利用 JDNI 来远程加载恶意类实现 RCE。

具体细节可以参考：<https://nosec.org/home/detail/4524.html>

##### 涉及 CVE

CVE-2020-14645，CVE-2020-14825 ， CVE-2020-14841

#### LockVersionExtractor

`oracle.eclipselink.coherence.integrated.internal.cache.LockVersionExtractor`
中的 `extract()` 方法，可以调用任意 `AttributeAccessor` 的 `getAttributeValueFromObject`
方法，赋值 `Accessor` 为 `MethodAttributeAccessor` 进而可以实现调用任意类的无参方法。
![](https://images.seebug.org/content/images/2021/08/161870dd-159f-4161-9e7a-324277d24e57.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210730155536540.png-w331s>

![](https://images.seebug.org/content/images/2021/08/4b25fcbe-7b43-4fc8-8a18-621b2ff75892.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210730160730854.png-w331s>

具体细节可参考：<https://cloud.tencent.com/developer/article/1740557>

**`MethodAttributeAccessor.getAttributeValueFromObject`**
，本质是利用`MethodAttributeAccessor.getAttributeValueFromObject`中存在任意无参方法调用，在
CVE-2021-2394 中也利用到了。
![](https://images.seebug.org/content/images/2021/08/da5b8192-cd85-4da3-b9f7-ae387479945b.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210730155032451.png-w331s>

##### 涉及 CVE

CVE-2020-14825 ， CVE-2020-14841

#### FilterExtractor.extract

`filterExtractor.extract` 中存在任意
`AttributeAccessor.getAttributeValueFromObject(obj)` 的调用，赋值
this.attributeAccessor 为上面说的`MethodAttributeAccessor` 就可以导致任意无参方法的调用。
![](https://images.seebug.org/content/images/2021/08/ded3a98e-6078-47fa-b8cc-0104d32c9eb8.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210730155415313.png-w331s>

![](https://images.seebug.org/content/images/2021/08/63ac62b6-2cb4-42c8-936b-d8e4170bd584.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210730155505477.png-w331s>

关于 `readAttributeAccessor` 的细节可以看
CVE-2021-2394：<https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/ >和
<https://www.cnblogs.com/potatsoSec/p/15062094.html> 。

##### 涉及 CVE

CVE-2021-2394

### 触发点

上面例举出了很多危险的 `ValueExtractor.extract` 方法，接下来再看看哪里存在调用 `ValueExtractor.extract`
方法的地方。

#### Limitfiler

Limitfiler 中 `Limitfiler.toString` 中存在任意 `ValueExtractor.extract` 方法调用：
![](https://images.seebug.org/content/images/2021/08/3427a9b0-8e2b-4df0-bf60-b39cb9a34879.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210728114626359.png-w331s>

由于 `this.m_comparator` 参与序列化和反序列化，所以可控：
![](https://images.seebug.org/content/images/2021/08/fa70eaf9-1b05-48b6-acf8-322b7a547c0d.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210728114758555.png-w331s>

我们只需要赋值 `this.m_comparator` 为 恶意的 `ValueExtractor` 就可以实现任意 `ValueExtractor
.extract` 方法的调用。`toString` 方法，则可以利用 CC5 中用到的 `BadAttributeValueExpException`
来触发。

##### 涉及 CVE

CVE-2020-2555

#### ExtractorComparator

`ExtractorComparator.compare` ，其实是针对 CVE-2020-2555 补丁的绕过，CVE-2020-2555
的修复方法中修改了 `Limitfiler.toString` 方法，也就是说修改了一个调用 `ValueExtractor.extract` 方法的地方。
而 CVE-2020-2883 则找到另一个调用 `ValueExtractor.extract` 的地方，也就是
`ExtractorComparator.compare` 。

在`ExtratorComparator.compare` 中存在任意（因为 `this.m_extractor` 参与序列化和反序列化）
`ValueExtractor` 的 `extract` 方法调用。
![](https://images.seebug.org/content/images/2021/08/a8eb3fed-e329-46e0-adba-7956dbaa257a.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210728115727611.png-w331s>

![](https://images.seebug.org/content/images/2021/08/48a6a272-f1a8-4799-882e-50f067ec7f10.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210728115739991.png-w331s>

`Comparator.compare 方法，则可以通过 CC2 中用到的`PriorityQueue.readObject` 来触发。

另外在 weblogic 中， `BadAttributeValueExpException.readObject` 中也可以实现调用任意
`compartor.compare`方法：
![](https://images.seebug.org/content/images/2021/08/83f8841f-6a50-463c-9e49-d29a451fb8bd.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210728120040372.png-w331s>

##### 涉及 CVE

CVE-2020-2883，修复方法是将 `ReflectionExtractor` 和 `MvelExtractor` 加入了黑名单 。

CVE-2020-14645 使用 `com.tangosol.util.extractor.UniversalExtractor` 绕过，修复方法将
`UniversalExtractor` 加入黑名单。

CVE-2020-14825，CVE-2020-14841 使用
`oracle.eclipselink.coherence.integrated.internal.cache.LockVersionExtractor.LockVersionExtractor`
进行绕过。

## ExternalizableHelper

在分析`ExternalizableHelper`
利用链架构的时候，我们依然可以把链分为四部分，一个是链头，一个是危险的中间的节点（漏洞点），另一个是调用危险中间节点的地方（触发点），最后一个则是利用这个节点去造成危害的链尾。

在 `ExternalizableHelper` 利用链架构中，这个危险的中间节点就是 `ExternalizableLite.readExternal`
方法。

weblogic 对于反序列化类的过滤都是在加载类时进行的，因此在
`ExternalizableHelper.readExternalizableLite` 中加载的 class 是不受黑名单限制的。
![](https://images.seebug.org/content/images/2021/08/279fdf62-f50c-4ede-b7c7-2c049743d8f4.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210730135848902.png-w331s>

具体原因是：weblogic 黑名单是基于 jep 290 ，jep 290 是在 `readObject`
的时候，在得到类名后去检查要反序列化的类是否是黑名单中的类。而这里直接使用的 `loadClass` 去加载类，所以这里不受 weblogic
黑名单限制。（也可以这么理解： jep 290 是针对在反序列化的时候，通过对要加载类进行黑名单检查。而这里直接通过 `loadClass`
加载，并没有通过反序列化，和反序列化是两码事，当然在后续 `readExternal` 的时候还是受 weblogic
黑名单限制，因为走的是反序列化那一套）

weblogic
黑名单机制可以参考：<https://cert.360.cn/report/detail?id=c8eed4b36fe8b19c585a1817b5f10b9e>，<https://cert.360.cn/report/detail?id=0de94a3cd4c71debe397e2c1a036436f>，<https://www.freebuf.com/vuls/270372.html>

### 漏洞点

#### PartialResult

![](https://images.seebug.org/content/images/2021/08/5f0cbb02-f5ef-4c47-8b29-7dfcda66a033.jpg-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210806191659163.png-w331s>

`com.tangosol.util.aggregator.TopNAggregator.PartialResult` 的 `readExternal`
会触发任意 `compartor.compare` 方法。

大致原理：

    
    
    在 149 行会把comparator 作为参数传入 TreeMap 的构造函数中。
    
    然后 153 行，会调用 this.add ,this.add 会调用 this.m_map.put 方法，也就是说调用了 TreeMap 的 put 方法，这就导致了 comparator.compare()的调用。

具体分析见：<https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ>

然后调用 `comparator.compare` 就可以接到 `ExtractorComparator.compare` 那里去了，从而实现 rce 。

##### 涉及 CVE

###### CVE-2020-14756 （1月）

`ExternalizableHelper` 的利用第一次出现是在 CVE-2020-14756 中。利用的正是
`ExternalizableHelper` 的反序列化通过 `loadClass` 加载类，所以不受 weblogic
之前设置的黑名单的限制。具体利用可以参考：<https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ>

CVE-2020-14756 的修复方法则是对 `readExternalizable` 方法传入的 `Datainput` 检查，如果是
`ObjectInputStream` 就调用 checkObjectInputFilter() 进行检查，`checkObjectInputFilter`
具体是通过 jep290 来检查的。
![](https://images.seebug.org/content/images/2021/08/0ce88947-fdc4-4498-a1a3-a17768d0af05.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210730135848902.png-w331s>

###### CVE-2021-2135 （4月）

上面补丁的修复方案 只是检查了 `DataInput` 为 `ObjectInputStream` 的情况, 却没有过滤其他 `DataInput` 类型
。

那我们只需要找其他调用 `readExternalizableit` 函数的地方,并且传入的参数不是 `ObjectInputStream`
就可以了。【`ObjectInputStream` 一般是最常见的,通常来说是 `readObject` =>`readObjectInternal`
=>`readExternalizableite` 这种链,也就是上游是常见的 `readObject`,
所以补丁就可能只注意到ObjectInputStream 的情况。】

所以CVE-2021-2135 绕过的方法就是设置传入 `readExternalizableite` 函数的参数类型为 `BufferInput`
来进行绕过。

`ExternalizableHelper` 中调用 `readObjectInternal` 的地方有两处,一处是
`readObjectInternal` , 另一处则是 `deserializeInternal` 。而 deserializeInternal 会先把
`DataInput` 转化为 `BufferInut` ：
![](https://images.seebug.org/content/images/2021/08/141362c2-34a7-436a-a180-c7d449132260.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210725192343651.png-w331s>

所以只要找调用 `ExternalizableHelper .deserializeInternal` 的地方。

而 `ExternalizableHelper.fromBinary` （和 `ExternalizableHelper.readObject` 平级的关系
）里就调用了 `deserializeInternal` , 所以只需要找到一个地方用 来
`ExternalizableHelper.fromBinary` 来反序列化就可以接上后面的（CVE-2020-14756）利用链了。

然后就是找 调用了 `ExternalizableHelper.fromBinary` 的方法的地方。`SimpleBinaryEntry` 中的
`getKey` 和 `getValue`方法中存在 `ExternalizableHelper.fromBinary` 的调用，所以就只要找到调用
`getKey` 和 `getValue` 的地方就可以了。
![](https://images.seebug.org/content/images/2021/08/5b9f4955-a278-4d50-ac0e-48a632439138.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210806191959478.png-w331s>

然后在 `com.sun.org.apache.xpath.internal.objects.XString`重写的`equals`方法里调用了
`tostring` ，在 `tostring` 中调用了 `getKey` 方法。

`ExternalizableHelper#readMap` 中会调用 `map.put` ，`map.put` 会调用 `equals` 方法。

`com.tangosol.util.processor.ConditionalPutAll` 的 `readExteranl` 中调用了
`ExternalizableHelper#readMap` 方法。

然后再套上 `AttributeHolder` 链头就可以了。

具体可以参考：<https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg>

![](https://images.seebug.org/content/images/2021/08/63f3a6cd-5912-4f34-9594-7895bb1a5664.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210725194322960.png-w331s>

4月漏洞修复则是：

添加`simpleBianry` 到黑名单。

#### filterExtractor

`filterExtractor.reaExternal` 方法中的 `readAttributeAccessor()` 方法会直接 `new` 一个
`MethodAttributeAccessor` 对象。
![](https://images.seebug.org/content/images/2021/08/b0ed6c2a-0863-4685-8834-aa843996bde9.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210730154428860.png-w331s>

![](https://images.seebug.org/content/images/2021/08/0f41cd58-0dbc-4844-8c79-89b3635f5e42.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210730154447677.png-w331s>

随后在 `filterExtractor.extract` 函数中会因为调用
`this.attributeAccessor.getAttributeValueFromObject` 进而导致任意无参方法的调用。
![](https://images.seebug.org/content/images/2021/08/79af90e4-d47c-4711-b65d-bf75afb89c01.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653082000-image-20210730155415313.png-w331s>

##### 涉及 CVE

###### CVE-2021-2394 （4月）

![](https://images.seebug.org/content/images/2021/08/eee7828e-c0ef-4a1b-bcb5-8e939e8cd5aa.png-w331s)
<https://images.seebug.org/content/images/2021/08/11/1628653083000-image-20210730135848902.png-w331s>

在4月的补丁中，对 ois 的 `DataInput` 流进行了过滤，所以直接通过 `newInstance`
实例化恶意类的方式已经被阻止（CVE-2021-2135 通过 `bufferinputStream` 进行了绕过），所以需要重新寻找其他不在黑名单中的
`readExternal` 方法。

CVE-2021-2394 中就是利用 `filterExtractor.readExternal` 来进行突破。

具体可以参考：<https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/> 和
<https://www.cnblogs.com/potatsoSec/p/15062094.html>

### 触发点

`ExternalizableHelper.readExternal` 的触发点有 `ExternalizableHelper.readObject` 和
`ExternalizableHelper.fromBinary` 这两个。其中 CVE-2021-2135 则就是因为在 CVE-2020-14756
的修复方法中，只注意到了 `ExternalizableHelper.readObject`
，只在`ExternalizableHelper.readObject` 里面做了限制，但是没有考虑到
`ExternalizableHelper.fromBinary` 从而导致了绕过。

`ExternalizableHelper.readObject`可以利用
`com.tangosol.coherence.servlet.AttributeHolder`来触发，`com.tangosol.coherence.servlet.AttributeHolder`
实现了 `java.io.Externalizabe` 接口，并且他的`readExternal` 方法 调用了
`ExternalizableHelper.readObject(in)` 。
![](https://images.seebug.org/content/images/2021/08/364f5af6-b307-4fe9-8c48-8d26c80abd47.png-w331s)<https://images.seebug.org/content/images/2021/08/11/1628653084000-image-20210728172300444.png-w331s>

`ExternalizableHelper.fromBinary`
的触发则较为复杂一些，具体可以参考：<https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg>

# 后记

weblogic Coherence 反序列化漏洞很多都是相关联的，对于某个漏洞，很可能就是用到了之前一些漏洞的链子。其实不仅仅 weblogic
，java
其他反序列化链也是如此，很多情况都是一个链会用到其他链的一部分。所以在学习中，把一个组件或者一个库的漏洞总结起来一起分析还是比较重要的，最后希望这篇文章能帮助到其他一起学反序列化的朋友们。

# 参考

<https://nosec.org/home/detail/4524.html>

<https://cloud.tencent.com/developer/article/1740557>

<https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/>

<https://www.cnblogs.com/potatsoSec/p/15062094.html>

<https://cert.360.cn/report/detail?id=c8eed4b36fe8b19c585a1817b5f10b9e>

<https://cert.360.cn/report/detail?id=0de94a3cd4c71debe397e2c1a036436f>

<https://www.freebuf.com/vuls/270372.html>

<https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ>

<https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1670/>

