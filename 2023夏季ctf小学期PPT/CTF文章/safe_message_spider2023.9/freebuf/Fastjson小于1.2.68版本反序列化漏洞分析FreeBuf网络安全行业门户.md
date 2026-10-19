## 前言

迟到的Fastjson反序列化漏洞分析，按照国际惯例这次依旧没有放poc。道理还是那个道理，但利用方式多种多样。除了之前放出来用于文件读写的利用方式以外其实还可以用于SSRF。

## 一、漏洞概述

在之前其他大佬文章中，我们可以看到的利用方式为通过清空指定文件向指定文件写入指定内容(用到第三方库)。当gadget是继承的第一个类的子类的时候，满足攻击fastjson的条件。此时寻找到的需要gadget满足能利用期望类绕过checkAutoType。

本文分析了一种利用反序列化指向fastjson自带类进行攻击利用，可实现文件读取、SSRF攻击等。

## 二、调试分析

### 1\. 漏洞调试

从更新的补丁中可以看到expectClass类新增了三个方法分别为：

java.lang.Runnable、java.lang.Readable、java.lang.AutoCloseable

首先，parseObject方法对传入的数据进行处理。通过词法解析得到类型名称，如果不是数字则开始checkAutoType检查。

![1602680651_5f86f74bd335e32a8cdcd.png!small?1602680652139](https://image.3001.net/images/20201014/1602680651_5f86f74bd335e32a8cdcd.png!small?1602680652139)

当传入的数据不是数字的时候，默认设置期望类为空，进入checkAutoType进行检查传入的类。

![1602680677_5f86f7653c39f6b206544.png!small?1602680677515](https://image.3001.net/images/20201014/1602680677_5f86f7653c39f6b206544.png!small?1602680677515)

判断期望类，此时期望类为null。往下走的代码中，autoCloseable
满足不在白名单内,不在黑名单内，autoTypeSupport没有开启，expectClassFlag为false。

  

其中：

A.计算哈希值进行内部白名单校验

B.计算哈希值进行黑名单校验

C.非内部白名单且开启autoTypeSupport或者是期望类的，进行hash校验白名单acceptHashCodes、黑名单denyHashCodes。如果在acceptHashCodes内则进行加载(
defaultClassLoader),在黑名单内则抛出 autoType is not support。

![1602680739_5f86f7a3532fa51e00caf.png!small?1602680739627](https://image.3001.net/images/20201014/1602680739_5f86f7a3532fa51e00caf.png!small?1602680739627)满足条件C后来到clazz的赋值，解析来的代码中对clazz进行了各种判断。

从明文缓存中取出autoCloseable赋值给 clazz。

![1602680869_5f86f8251ac638d1dafe7.png!small?1602680869420](https://image.3001.net/images/20201014/1602680869_5f86f8251ac638d1dafe7.png!small?1602680869420)![1602680962_5f86f882ac346e525a552.png!small?1602680963127](https://image.3001.net/images/20201014/1602680962_5f86f882ac346e525a552.png!small?1602680963127)当clazz不为空时，expectClassFlag为空不满足条件，返回clazz,至此，第一次的checkAutoType检查完毕。

![1602680996_5f86f8a438eb73510f1bb.png!small?1602680996461](https://image.3001.net/images/20201014/1602680996_5f86f8a438eb73510f1bb.png!small?1602680996461)

将检查完毕的autoCloseable进行反序列化，该类使用的是JavaBeanDeserializer反序列化器，从MapDeserializer中继承。

![1602681042_5f86f8d23ba6bf7e2789a.png!small?1602681043166](https://image.3001.net/images/20201014/1602681042_5f86f8d23ba6bf7e2789a.png!small?1602681043166)

![1602681063_5f86f8e72b6c8eeac9116.png!small?1602681063538](https://image.3001.net/images/20201014/1602681063_5f86f8e72b6c8eeac9116.png!small?1602681063538)

JSON.DEFAULT_TYPE_KEY 为@type ,并给它赋值传入的key @type ,将第二个类也就是这次 的gadget传入。

![1602681109_5f86f915ac5210dcc3d21.png!small?1602681109920](https://image.3001.net/images/20201014/1602681109_5f86f915ac5210dcc3d21.png!small?1602681109920)

期望类在这里发生了变化，expectClass的值变为java.lang.AutoCloseable，typeName为gadget，

![1602681137_5f86f931916be5d2ea579.png!small?1602681137840](https://image.3001.net/images/20201014/1602681137_5f86f931916be5d2ea579.png!small?1602681137840)

来到JSONType注解，取typename gadget转换变为路径，resource通过将 “.” 替换为”/“得到路径
。其实已经开始读取gadget了，它本意应该是加载AutoCloseable。

![1602681161_5f86f949af546e5d0bc1e.png!small?1602681161969](https://image.3001.net/images/20201014/1602681161_5f86f949af546e5d0bc1e.png!small?1602681161969)

可以看到这里有读取文件的功能。

![1602681189_5f86f96599507312c1100.png!small?1602681189811](https://image.3001.net/images/20201014/1602681189_5f86f96599507312c1100.png!small?1602681189811)

![1602681215_5f86f97f52e2380adccc3.png!small?1602681215574](https://image.3001.net/images/20201014/1602681215_5f86f97f52e2380adccc3.png!small?1602681215574)

isAssignableFrom()这个方法用于判断里面的类是否为继承类，当利用了java.lang.AutoCloseable这个方法去攻击fastjson，那么后续反序列化的链路一定是要继承于该类的子类。

TypeUtils.addMapping(typeName, clazz)这一步成功把gadget加入缓存中并返回被赋值gadget的clazz.

![1602681252_5f86f9a47c6a98c09e8ab.png!small?1602681252840](https://image.3001.net/images/20201014/1602681252_5f86f9a47c6a98c09e8ab.png!small?1602681252840)checkAutoType正式检查完毕，此时用deserializer
= parser.getConfig().getDeserializer(userType); userType既gadget进行反序列化。

![1602681274_5f86f9ba04e51a10b7044.png!small?1602681274248](https://image.3001.net/images/20201014/1602681274_5f86f9ba04e51a10b7044.png!small?1602681274248)

进入coreConnect()

![1602681299_5f86f9d308c9e9d02fe74.png!small?1602681299298](https://image.3001.net/images/20201014/1602681299_5f86f9d308c9e9d02fe74.png!small?1602681299298)

![1602681311_5f86f9df0d692516b2d8d.png!small?1602681311253](https://image.3001.net/images/20201014/1602681311_5f86f9df0d692516b2d8d.png!small?1602681311253)

在这里进行连接。至此漏洞利用完结。

### 2\. 总结：

在本次反序列化漏洞中，笔者认为关键点在于找到合适并且可利用的常用jar包中的gadget。gadget在被反序列化后即可执行类里的恶意的功能(不仅限于RCE还包括任意文件读取/创建,SSRF等)。也可以使本漏洞得到最大化的利用。

## 三、参考考链接

> <https://b1ue.cn/archives/348.html>
>
>
> <https://daybr4ak.github.io/2020/07/20/fastjson%201.6.68%20autotype%20bypass/>

作者：ale_wong

