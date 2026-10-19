![](https://image.3001.net/images/20200310/1583854296_5e67b2d857650.png!small)

##  写在前面的话

 **在对Java
Web应用程序进行研究时，不安全的反序列化漏洞现在已经成为了攻击者或研究人员的常见目标了。这些漏洞将导致他人在目标设备上可靠地实现远程代码执行，而且这类漏洞通常很难修复。在这篇文章中，我们将对漏洞CVE-2020-2555（[ZDI-20-128](https://www.zerodayinitiative.com/advisories/ZDI-20-128/)）进行分析。这是一个严重漏洞，CVSS评分为9.8，该漏洞将影响Oracle
Coherence库，而这个库在Oracle WebLogic
Server等流行产品中都有广泛使用。目前，该漏洞已在[1月份](https://www.oracle.com/security-alerts/cpujan2020.html)的更新补丁中被修复。**

##  通过分析补丁来寻找漏洞源

这个漏洞存在于一个Java方法中，攻击者将能够通过受控参数来调用该方法。在Java中，为了重新创建对象图，代码将会自动调用一个类中的readObject()或readExternal()方法，而这两个方法以及其他的方法都可以被看作是一种有效的小工具反序列化漏洞源。

CVE-2020-2555的漏洞补丁引入了一个非常有意思的修改，补丁代码修改了LimitFilter类中的toString()方法：

![](https://image.3001.net/images/20200310/1583854308_5e67b2e44357d.png!small)

所有针对extract()方法的调用都被从toString()方法中移除了。extract()方法的重要性我们暂时先不做讨论，而这种修改的有趣之处就在于，各种标准的JRE类都可以通过readObject()方法来调用和访问toString()方法，比如说BadAttributeValueExpException：

![](https://image.3001.net/images/20200310/1583854327_5e67b2f7d5d32.png!small)

我们可以从上面的代码中看到，BadAttributeValueExpException类的序列化实例就可以用来调用任意类中的toString()方法，而这种技术就可以用来调用LimitFilter类中的toString()方法。没错，就是存在漏洞的LimitFilter类。

有关使用toString()方法作为入口点的小工具示例，请参阅[ysoserial项目](https://github.com/frohoff/ysoserial)的CommonsCollections5
小工具。

##  深入分析

众所周知，Java中的Sink方法调用是存在安全风险的。比如说以下几个场景：

> 1、通过调用FileOutputStream.write()方法创建任意文件；
>
> 2、通过调用Runtime.exec()方法执行任意命令；
>
> 3、通过调用method.invoke()方法来调用其他任意方法；

针对该漏洞，我们的重点应该放在一个针对Method.invoke()的调用身上，而这里的副作用就是可以通过反射来调用任意Java方法。根据这些给定的信息，我们可以查找由extract()方法调用导致Method.invoke()的调用，而我们在分析漏洞补丁的时候会将其标识为入口点。比如说，在Oracle
Coherence库中就有一个可序列化的类，而这个类实现了可序列化和可外部化的接口：

![](https://image.3001.net/images/20200310/1583854400_5e67b340adaa2.png!small)

通过分析ReflectionExtractor类，证实了我们的猜想：

![](https://image.3001.net/images/20200310/1583854406_5e67b34641e55.png!small)

ReflectionExtractor提供了一种存在安全风险的操作原语，它将允许攻击者调用其他类中的任意方法，并且攻击者甚至还可以直接控制具体的方法以及相关参数。

##  实现远程代码执行

一般来说吗，攻击者将需要调用多个方法才能够在目标设备上实现远程代码执行。比如说，针对常见的Apache Commons
Collections小工具，攻击者需要使用ChainedTransformer类来将任意方法串联起来以实现远程代码执行。相似的，Oracle
Coherence库中也提供了这样一个类，即ChainedExtractor，而这个类允许我们串联针对extract()方法的调用：

![](https://image.3001.net/images/20200310/1583854430_5e67b35ee335e.png!small)

将我们了解到的东西全部整理之后，我们就可以使用下列调用链来实现远程代码执行了：

![](https://image.3001.net/images/20200310/1583854435_5e67b36348050.png!small)

因此，如果目标使用了Oracle Coherence库，那么攻击者就可以通过发送恶意序列化对象来在目标环境中实现远程代码执行了。

##  总结

自从Chris Frohoff和Gabriel
Lawrence在AppSecCali上提出Java反序列化的相关概念之后，社区的安全研究人员就一直在尝试从中寻找出反序列化漏洞，而这类漏洞将允许他人实现可靠的远程代码执行。

 ***
参考来源：[zerodayinitiative](https://www.zerodayinitiative.com/blog/2020/3/5/cve-2020-2555-rce-through-a-deserialization-bug-in-oracles-weblogic-server)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

