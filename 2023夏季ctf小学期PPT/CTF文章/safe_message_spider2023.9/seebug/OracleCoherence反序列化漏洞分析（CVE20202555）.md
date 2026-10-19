**作者：Lucifaer**  
**原文链接：[https://lucifaer.com/2020/03/10/Oracle%20Coherence%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%EF%BC%88CVE-2020-2555%EF%BC%89/?from=timeline&isappinstalled=0](https://lucifaer.com/2020/03/10/Oracle%20Coherence%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%EF%BC%88CVE-2020-2555%EF%BC%89/?from=timeline&isappinstalled=0)**

# 0x01 漏洞概述

![](https://images.seebug.org/content/images/2020/03/c62e2b63-5381-4af1-a12b-7c8543c5f363.jpg-w331s)

Oracle官方在1月补丁中修复了CVE-2020-2555漏洞，该漏洞位于`Oracle
Coherence`组件中。该组件是业内领先的用于解决集群应用程序数据的缓存的解决方案，其默认集成在Weblogic12c及以上版本中。

该漏洞提出了一条新的反序列化gadget，未经身份验证的攻击者通过精心构造的T3请求触发可以反序列化gadget，最终造成远程命令执行的效果。

# 0x02 漏洞分析

ZDI已经给出了一部分的[分析][1]，根据ZDI发出的diff图，不难看出补丁是将`extract`的利用全部移除了，具体的代码可以在`com.tangosol.util.filter.LimitFilter#toString`中找到：

![](https://images.seebug.org/content/images/2020/03/024bad75-ff24-4e63-9ab0-fbdcc1c831b5.jpg-w331s)

所以只要跟踪`extract()`的执行流，就能理解漏洞产生的原理。其实总体来说该漏洞应该分为两部分来分析：

  * 反射调用链
  * 反序列化触发点

## 2.1 反射调用链

首先先来具体看一下`com.tangosol.util.filter.LimitFilter#toString`的逻辑：

![](https://images.seebug.org/content/images/2020/03/4fa6d542-0a14-441e-9a61-9ffdf7bc04aa.jpg-w331s)

红线所标注的就是漏洞触发的关键点，这里的`m_comparator`、`m_oAnchorTop`、`m_oAnchorBottom`是我们能通过`LimitFilter`的构造函数进行构造的。当`m_comparator`是继承于`ValueExtractor`接口的类时，会尝试调用`m_comparator.extract()`方法，并将结果放入StringBuffer中。

我们接着来看一下`ValueExtractor`的实现类：

![](https://images.seebug.org/content/images/2020/03/30166521-930d-4528-b9c8-5cb2ebe44acc.jpg-w331s)

其中`ReflectionExtractor`和`ChainedExtractor`值得我们关注。通过名字不难想到这两个类一个是用于完成反射相关操作的，一个是用于执行链式操作的。

在`ReflectionExtractor#extract`中，可以很明显的看到存在反射调用的流程：

![](https://images.seebug.org/content/images/2020/03/d4ec55bf-d68c-41a2-885f-c9dbc5bbe15d.jpg-w331s)

简单来说就是获取`oTarget`的`Method`，并反射调用该对象的具体方法。具体方法由`this.getMethodName()`来控制：

![](https://images.seebug.org/content/images/2020/03/b24cab8b-2c62-4d7a-b09b-1267b256689d.jpg-w331s)

![](https://images.seebug.org/content/images/2020/03/887bac5a-9dcd-481d-9758-c90dca11eede.jpg-w331s)

同样，这个值也是可以通过`ReflectionExtractor`的构造函数来去指定的。现在我们可以指定任意一个方法通过反射调用该方法。但是想要执行代码的话并不是单次反射就能完成的，我们还需要找到一个方法将多条反射调用串起来（就如CommonCollections的利用链相同）。`ChainedExtractor`就完成了这个工作：

![](https://images.seebug.org/content/images/2020/03/073912af-9526-42ca-94c7-660c3ff50cfd.jpg-w331s)

这里的`ValueExtractor`数组是通过`this.getExtractors()`获得的，同样也可以通过`ChainedExtractor`构造函数进行指定：

![](https://images.seebug.org/content/images/2020/03/656bccef-f314-428e-8e04-7560f8587781.jpg-w331s)

![](https://images.seebug.org/content/images/2020/03/90eb557a-e3d1-4a63-b664-8e3dfc282ad3.jpg-w331s)

![](https://images.seebug.org/content/images/2020/03/9ac99e00-79da-449c-8fac-35e8fa659944.jpg-w331s)

也就是说现在我们只需要构造多条`ReflectionExtractor`，将其置于`ValueExtractor`数组中，就可以触发链式反射调用流程。这一点和CommonCollections的利用链也非常像，最终的执行流可以大致简化为：

![](https://images.seebug.org/content/images/2020/03/483559ce-c487-4b19-b5ac-89f06cf4deb9.jpg-w331s)

## 2.2 反序列化触发点

上面我们分析了具体的反射调用流程，这一切都是建立在`LimitFilter#toString`触发时所发生的，为了利用反射调用流程，我们还需要找到一个能够在反序列化时触发`toString`方法的触发点。ZDI这篇文章中说到了一个触发点——`BadAttributeValueExpException#readObject`：

![](https://images.seebug.org/content/images/2020/03/463bf9f0-e6e1-40bb-97c5-face11142b8b.jpg-w331s)

所以只需要设置`BadAttributeValueExpException`的成员变量`val`为`LimitFilter`就可以完成触发。

# 0x03 漏洞利用

通过上面的分析，我们来梳理一下整体的构造流程：

  1. 构造能串联起来完成命令执行的多条`ReflectionExtractor`反射调用
  2. 利用`ChainedExtractor`将多条`ReflectionExtractor`串联起来
  3. 将`ChainedExtractor`设置为`LimitFilter`的成员变量`m_comparator`的值
  4. 为了完成链式反射调用链，将`LimitFilter`的成员变量`m_oAnchorTop`设置为相应的值（如`Runtime.class`）
  5. 将构造完成的`LimitFilter`设置为`BadAttributeValueExpException`的成员变量`val`的值
  6. 序列化`BadAttributeValueExpException`
  7. 构造包含序列化数据的T3请求，发送请求完成攻击

攻击效果：

![](https://images.seebug.org/content/images/2020/03/7b46f718-7702-4469-bb97-c1adcc7ad6ac.jpg-w331s)

# 0x04 其他利用方式

抛砖引玉的说一个其他的利用方式。由于我并不是非常喜欢这样串联利用链的方式（因为不好理解），所以简单的看了下其他的Extractor，看看有没有更加简单的利用方式。这里找到另外一个非常好理解的利用方式。前面的流程都是一样的，唯一不同的是可以不利用`ReflectionExtractor`加`ChainedExtractor`这样的组合，同样能完成命令执行。

漏洞产生的原因也从链式反射调用改为表达式注入。相信一说到表达式注入各位就已经知道是用的什么链了，这里就不再过多赘述，就放一张利用效果图：

![](https://images.seebug.org/content/images/2020/03/a0606936-3fe8-4ac8-9a76-20646133cc6e.jpg-w331s)

**Reference**

  1. <https://www.thezdi.com/blog/2020/3/5/cve-2020-2555-rce-through-a-deserialization-bug-in-oracles-weblogic-server>

  2. <https://www.oracle.com/security-alerts/cpujan2020.html>

  3. <https://www.thezdi.com/blog/2020/3/5/cve-2020-2555-rce-through-a-deserialization-bug-in-oracles-weblogic-server>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1141/>

