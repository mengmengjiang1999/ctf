# FastJson<=1.2.68RCE原理详细分析

阅读量 **323401**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-18 10:30:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0175552f2250560322.jpg)

## 0x00 前言

上篇文章中学习了FastJson主流的第二版漏洞，在v1.2.48中
设置cache为false修复了这个漏洞，之后在1.2.68中出现了新的利用方式。本文就FastJson1.2.68版本的漏洞进行详尽的原理分析。

## 0x01 导火索之expectClass

这次的罪魁祸首的确是expectClass参数，但是！expectClass的由来还得从autoType说起。  
fastjson为了实现反序列化引入了autoType，之后防止进行恶意反序列化对象从而导致RCE，引入了checkAutoType()，这就引出了很多的问题，包括我们之前提到的都属于它的锅。而这次的expectClass参数也是checkAutoType()函数的一个参数，在之前的漏洞中都没有用到过，所以这次是一个全新的bypass
checkAutoType()的方式，也造成了今年疯传的那个漏洞。

我们先来看一下通过checkAutoType()校验的方式有哪些：

  1. 白名单里的类
  2. 开启了autotype
  3. 使用了JSONType注解
  4. 指定了期望类（expectClass）
  5. 缓存在mapping中的类
  6. 使用ParserConfig.AutoTypeCheckHandler接口通过校验的类

我们这次用的就是第四种方式。

checkAutoType()中的expectClass参数类型为java.lang.Class，当expectClass传入checkAutoType()时不为null，并且我们要实例化的类是expectClass的子类或其实现时会将传入的类视为一个合法的类（不能在黑名单中），然后通过loadClass返回该类的class，我们就可以利用这个绕过checkAutoType()。

此外，由于checkAutoType()中黑名单的检测位于loadClass之前，所以不能在黑名单中，另外恶意类需要是expectClass的接口或是expectClass的子类。

我们查找把expectClass参数传递给checkAutoType()函数的利用类有两个：

  1. 在JavaBeanDeserializer类的deserialze()函数中会调用checkAutoType()并传入可控的expectClass
  2. 在ThrowableDeserializer类的deserialze()函数中也会调用并传入

无论是上述哪一个利用类都会将[@type](https://github.com/type
"@type")的值作为typeName传给expectClass并调用checkAutoType(…expectClass…)，所以思路就是在poc里写两个[@type](https://github.com/type
"@type")，第一个正常通过checkAutoType()，然后调用上述类中的deserialze()函数，然后在其中使用expectClass绕过第二次的checkAutoType()函数。

其中对应的分别为：AutoCloseable类和Throwable类，接下来详细分析。

## 0x02 详细分析

###  AutoCloseable

**环境**

首先IDEA创建1.2.68的fastjson的maven项目，之后编写Exp.java和JavaBean.java。

    
    
    //Exp.java
    package com;
    import com.alibaba.fastjson.JSON;
    public class Exp {
        public static void main(String args[]){
            JSON.parseObject("{\"@type\":\"java.lang.AutoCloseable\", \"@type\":\"com.JavaBean\", \"cmd\":\"calc.exe\"}");
        }
    }
    
    
    
    //JavaBean.java
    package com;
    import java.io.IOException;
    public class JavaBean implements AutoCloseable{
        public JavaBean(String cmd){
            try{
                Runtime.getRuntime().exec(cmd);
            }catch (IOException e){
                e.printStackTrace();
            }
        }
    
        public void close() throws Exception {
    
        }
    }
    

启动后弹出计算器，触发payload。

![](https://p1.ssl.qhimg.com/t01d7deb4e276234883.png)

**动态调试**

首先在JSON.parseObject()断点进入调试

![](https://p4.ssl.qhimg.com/t0156a217eb614d5006.png)

同之前文章分析的大体相同，在DefaultJSONParser.java中，parseObject()对传入数据进行解析，如果是[@type](https://github.com/type
"@type")则获取到类型名后进行checkAutoType()的检查

![](https://p3.ssl.qhimg.com/t01e8b12cda4110a9d8.png)

单步步入后详细分析下checkAutoType()的检查逻辑

其中一处可以看到如果expectClass不为null，且不在那几个里面就会把expectClassFlag设置为true，我们第二次进入checkAutoType()就会用到

![](https://p0.ssl.qhimg.com/t01be5e4e6102c6b467.png)

接下来会进行黑白名单查询。首先进行内部白名单，之后及进行内部黑名单，由于内部黑名单为null故跳过

![](https://p4.ssl.qhimg.com/t01b5deb818a645084f.png)

之后，如果非内部白名单并且开启autoTypeSupport或者是expectClass时会进行黑白名单查找。首先在白名单内二分查找，如果在则加载后返回指定class对象，如果不在或者为空，会继续在黑名单中进行二分查找；若不在黑名单且getClassFromMapping返回值为null，就再在白名单查询，若为空则异常，否则continue

![](https://p4.ssl.qhimg.com/t01a551267616ee39d8.png)

之后从缓存中得到赋值给clazz

![](https://p5.ssl.qhimg.com/t0127bd18821b1600ce.png)

之后从checkAutoType()返回clazz到DefaultJSONParser.java#parseObject()中，单步到deserializer.deserialze()

![](https://p4.ssl.qhimg.com/t012b6b38ffd8d90f23.png)

在deserialze()解析字段，当为[@type](https://github.com/type
"@type")（第二个）时，调用checkAutoType()并传入expectClass

![](https://p4.ssl.qhimg.com/t01c28b943955cf9b3d.png)

第二次步入checkAutoType()，在这里把expectClassFlag设为true

![](https://p5.ssl.qhimg.com/t017449beae2c8900d3.png)

这次进入成功之前分析的黑白名单环节

![](https://p2.ssl.qhimg.com/t019161144226fb007f.png)

之后由于autoTypeSupport为true进入if段，又进行了一次黑白名单校验

![](https://p2.ssl.qhimg.com/t01c11312daf3fcef96.png)

之后resource将“.”替换为”/“得到路径，并且这里貌似有读文件的功能

![](https://p5.ssl.qhimg.com/t01db3d44b0258944e3.png)

之后如果autoType打开或者使用了JSONType注解，又或者
expectClassFlag为true时，并且只有在autoType打开或者使用了JSONType注解时，才会将类加入到缓存mapping中。另外没使用JSONType注解不会返回

![](https://p3.ssl.qhimg.com/t01bc44c10bf6f9e607.png)

之后expectClass不为null，加载到mapping中，并返回JavaBeanDeserializer#deserialze()

![](https://p1.ssl.qhimg.com/t01bcab1e8286e76f1b.png)

之后deserializer.deserialze()，由于将恶意类加入mapping，在反序列化解析时会绕过autoType，成功利用

![](https://p2.ssl.qhimg.com/t01a595d0084598be5a.png)

###  Throwable

Throwable类反序列化处理为ThrowableDeserializer#deserialze()，当为[@type](https://github.com/type
"@type")时，同样调用checkAutoType()并传入expectClass，也就是Throwable.class类对象。之后的利用都差不多。

![](https://p1.ssl.qhimg.com/t018f8c87791c74c243.png)

## 0x03 修复

首先对过滤的expectClass进行修改，新增3个新的类，并且将原来的Class类型的判断修改为hash的判断，通过彩虹表碰撞可以得知分别为：java.lang.Runnable，java.lang.Readable和java.lang.AutoCloseable。

![](https://p0.ssl.qhimg.com/t018a82f640844a22e8.png)

![](https://p1.ssl.qhimg.com/t01e18001cea731ff81.png)

此外，Fastjson
1.2.68及之后的版本引入了safeMode功能，作为控制反序列化的开关，开启后禁止反序列化，会直接抛出异常，彻底解决反序列化造成的RCE问题，一劳永逸。

## 0x04 结语

到目前为止，相关的FastJson漏洞都讲了一些，就告一段落了，相信都非常详细，可以简单查看并进行学习。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **zzZ** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/225439](/post/id/225439)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t0177bde109b464d6d4.png) zzZ

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

