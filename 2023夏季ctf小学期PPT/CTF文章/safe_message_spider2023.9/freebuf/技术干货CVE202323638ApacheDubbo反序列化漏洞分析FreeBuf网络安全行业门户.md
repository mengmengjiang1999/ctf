## 框架介绍

Apache Dubbo是一款高性能、轻量级的开源Java RPC
框架，它提供了三大核心能力：面向接口的远程方法调用，智能容错和负载均衡，以及服务自动注册和发现。Dubbo一开始把自己定位为一个RPC框架，专注于服务之间的调用。随着微服务的概念越来越火爆，Dubbo开始重新思考自己的定位，除了服务调用，开始逐渐向服务治理、服务监控、服务网关等方向扩展，随着Dubbo生态圈的逐渐完善，Dubbo慢慢的演变为一个成熟的微服务框架。

## 漏洞描述

在此前的CVE-2021-30179漏洞就是利用了Dubbo泛化调用功能，用户可以向Dubbo服务端传入任意类，这就导致攻击者可以通过反序列化的方式，来触发特定Gadget，达到远程命令执行的目的。在CVE-2021-30179后续的补丁中，增加了黑名单来过滤恶意传入的类，而CVE-2023-23638就是对此防御方式的绕过。

![v2-dd6f3bb74fc292b119cc2a33542f089a_720w.png](https://image.3001.net/images/20230718/1689649649_64b601f1c711451a9afeb.png!small)

### 利用范围

  * Apache Dubbo 2.7.x <= 2.7.21

  * Apache Dubbo 3.0.x <= 3.0.13

  * Apache Dubbo 3.1.x <= 3.1.5

### 相关介绍

简单介绍一下Dubbo的泛化调用，泛化调用（客户端泛化调用）是指在调用方没有服务方提供的
API（SDK）的情况下，对服务方进行调用，并且可以正常拿到调用结果，使用场景是在调用方没有接口及模型类元，知道服务的接口的全限定类名和方法名的情况下，可以通过泛化调用调用对应接口，
比如：实现一个通用的服务测试框架。泛化调用是通过Dubbo的filter机制实现的。

具体的使用方式可以参考：https://cn.dubbo.apache.org/zh-cn/overview/tasks/develop/generic/

## 漏洞分析

环境POC：POC采用的是https://github.com/X1r0z/CVE-2023-23638

JDK版本：8u121

## 代码分析

漏洞产生的本质还是利用了Dubbo泛化调用功能，而Dubbo处理泛化调用的方式是通过filter机制实现的，核心类是org.apache.dubbo.rpc.filter.GenericFilter

![v2-86cbe3e599bc5f6d1f01c8112ca2ad55_720w.png](https://image.3001.net/images/20230718/1689649650_64b601f26201cf7d64130.png!small)

invoke方法首先会对Invocation对象进行校验

![v2-8d23f467f09591e743e1fcd574f744d9_720w.png](https://image.3001.net/images/20230718/1689649651_64b601f34be5235cdb103.png!small)

检查方法名是否为$invoke或者$invokeAsync、检查参数是否不为null、检查参数长度是否为3、检查invoke对象接口是否不是通过GenericService继承的，校验通过后就会通过getArguments()
获取参数，三个参数name、types、args分别为 String 类型、String 数组类型和Object 数组类型。

![v2-891734c358f53540202175c390157dee_720w.png](https://image.3001.net/images/20230718/1689649652_64b601f446cad857018fa.png!small)

随后通过 findMethodByMethodSignature
反射查找服务端提供的方法，如果没有找到就会抛出异常，所以在POC中传入的方法必须是Dubbo服务端提供的方法。

![v2-2d011c015274d9fdd64b86d5ae3e4f95_720w.png](https://image.3001.net/images/20230718/1689649652_64b601f4e809a627d29ea.png!small)

随后通过获取请求中传递的generic的值来选择将参数反序列化为pojo对象的方式，一共有五种：

true、raw.return、nativejava、bean、protobuf-json。

## CVE-2021-30179的利用方式

### 1\. 将generic设置为raw.return

![v2-719aab2e0471a77aa35cc9bd14134307_720w.png](https://image.3001.net/images/20230718/1689649653_64b601f5c3b523675a675.png!small)

将最终调用PojoUtils#realize0

![v2-0b33dcd2e2a32056daabada5e29e27fb_720w.png](https://image.3001.net/images/20230718/1689649654_64b601f6c37f64b3d9def.png!small)

若pojo为map实例，则获取key为"class"的值，并通过反射得到class所对应的类type，后续处理中经过判断：如果type不是Map的子类、不为Object.class且不是接口，则进入else，对type通过反射进行了实例化，得到对象dest。

![v2-f81c4205137e21f119f7970fe4d15379_720w.png](https://image.3001.net/images/20230718/1689649655_64b601f79ae8129131400.png!small)

后续会对pojo进行遍历，以键名为name，值为value，调用getSetterMethod(dest.getClass(), name,
value.getClass())，获取set方法

![v2-abdeb3a0ce1dfadecfe2367e63bd524d_720w.png](https://image.3001.net/images/20230718/1689649656_64b601f835817bdebe5c4.png!small)

最后利用反射执行invoke调用危险方法进行利用

![v2-084238629a7648fb415ec54f03384b93_720w.png](https://image.3001.net/images/20230718/1689649656_64b601f8c16a7babe875e.png!small)

### 2\. 将generic设置为nativejava

遍历args，检查args[i]是否为byte[]类型，如果是，则将字节数组转化为输入流，然后，代码使用ExtensionLoader.getExtensionLoader方法获取了一个Serialization类的扩展实现对象，并调用其deserialize方法来将输入流中的字节流反序列化为一个Java对象，代码调用readObject方法来读取反序列化后的Java对象，并将其赋值给原始的args[i]参数，从而将字节数组转换为Java对象，后续利用CC4触发gadget。

![v2-913f31163a02f2f60d2a70694865d7a0_720w.png](https://image.3001.net/images/20230718/1689649657_64b601f93a5cd1ee08620.png!small)

### 3\. 将generic设置为bean

将遍历args，如果args[i]为JavaBeanDescriptor的实例，则调用JavaBeanSerializeUtil#deserialize方法

![v2-45e49dba70751e6a175be2c867cc2f00_720w.png](https://image.3001.net/images/20230718/1689649658_64b601fa3950ac33ef5bc.png!small)

最终调用JavaBeanSerializeUtil#deserializeInternal进行反序列化，最后利用invoke调用org.apache.xbean.propertyeditor.JndiConverter的setAsText发起JNDI注入。

![v2-0535792e32c80fe30f1e7b9117bf497f_720w.png](https://image.3001.net/images/20230718/1689649658_64b601fadb20e5e7e3df8.png!small)

注意：上述均为CVE-2021-30179的利用方式，由于环境使用的是Dubbo 3.1.5版本，存在对上述利用的限制，主要为：

针对raw.return和bean利用的黑名单过滤

![v2-85da0ee5088ea85f25ce358543b2248e_720w.png](https://image.3001.net/images/20230718/1689649659_64b601fb8af6399ac85df.png!small)

针对nativejava利用—通过判断配置文件是否允许nativejava的反序列化

![v2-541a68ca53a39cd1288110b5e6acfe97_720w.png](https://image.3001.net/images/20230718/1689649661_64b601fd022f2032e104e.png!small)

### 黑名单绕过

根据上面分析我们知道对黑名单的过滤主要在PojoUtils#realize0方法中，使用validateClass方法进行过滤

![v2-ede99f59e1abaa5718dbd575b4bc1b63_720w.png](https://image.3001.net/images/20230718/1689649662_64b601fe12cb36bac19cf.png!small)

validateClass方法首先会对OPEN_CHECK_CLASS属性进行判断，如果这个属性为false，那么就不会对传入类进行检查，直接返回。那么其中一种绕过的方式就是，设置OPEN_CHECK_CLASS属性为false，从而绕过黑名单检查。

![v2-2d34cd3089a99302a8a01bf8696fb64b_720w.png](https://image.3001.net/images/20230718/1689649663_64b601ff20e28911ad480.png!small)

在SerializeClassChecker.getInstance方法中，使用Singleton模式（单例模式）

![v2-34966c6f3f24268f69450b5f1b1adf1d_720w.png](https://image.3001.net/images/20230718/1689649664_64b6020051a9557d77e6f.png!small)

通过自定义赋值替换INSTANCE对象，将它的OPEN_CHECK_CLASS属性置为false，来绕过黑名单类的检查。

POC如下：

![v2-c1112c698add1a57dd7c190e9bb61271_720w.png](https://image.3001.net/images/20230718/1689649665_64b6020187bb819662fe5.png!small)

更加详细的分析和注意事项可以参考X1r0z师傅的文章：https://exp10it.cn/2023/03/apache-dubbo-cve-2023-23638-%E5%88%86%E6%9E%90/，当然CVE-2023-23638利用方式也不止这一种，可以参考其他师傅们优秀的分析文章。

## 漏洞复现

![v2-7bd8a90b0d33ca3168a04c00992eaba9_720w.png](https://image.3001.net/images/20230718/1689649666_64b602027039df005ac55.png!small)

关于JNDI注入的时候需要注意使用的JDK版本（LDAP的利用方式，JDK版本需低于于6u211、7u201、8u191、11.0.1）

## 漏洞建议

根据漏洞利用的版本信息，排查并升级到安全版本，或直接访问参考链接获取官方更新指南。

参考材料

  * https://github.com/X1r0z/CVE-2023-23638

  * https://exp10it.cn/2023/03/apache-dubbo-cve-2023-23638-%E5%88%86%E6%9E%90/

  * https://cn.dubbo.apache.org/zh-cn/overview/tasks/develop/generic/

  * https://github.com/lz2y/DubboPOC

