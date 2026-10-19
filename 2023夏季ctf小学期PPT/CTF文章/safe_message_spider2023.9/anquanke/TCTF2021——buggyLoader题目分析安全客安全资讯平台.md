# TCTF 2021——buggyLoader 题目分析

阅读量 **189107**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-28 10:30:12

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0141224fd749e3d242.jpg)

## 0x01 题目简介

前段时间TCTF
2021总决赛上出了一道java反序列化题目，碰巧前不久刚分析过shiro反序列化漏洞，如果在了解过shiro反序列化漏洞的重难点之后再看此题就会感觉比较简单，因为他们考察的知识点都是classloader相关内容。本篇文章将使用对比学习的方式一步步解决buggyLoader这道题目中遇到的问题，最后汇总知识点以及回答一些目前网上存在的问题。

题目默认页面如下图所示，主要考察Java反序列化的一些知识点，通过basic路由进行触发

![](https://p0.ssl.qhimg.com/t015e0be12c96b91269.png)

## 0x02 环境搭建

###  0x1 docker搭建

为了更加方便的学习该题目，笔者首先进行调试环境搭建部署。好在该比赛提供了赛后复现docker

<https://github.com/waderwu/My-CTF-Challenges/tree/master/0ctf-2021-final/buggyLoader>

根据题目docker文件了解到，该java服务部署在nginx服务之后，官方提供的nginx
docker做了一层转发，而且java题目所在的虚拟机网络接口为internal_network，这样不方便调试分析。在实际做题过程中可以修改docker-compose.yml将服务端口和调试直接映射出来，像下面一样修改题目部署文件。

    
    
    version: '2.4'
    services:
      web:
        build: ./
        ports:
          - "8811:8080"
          - "5566:5566"
        restart: always
        networks:
          - out_network
    networks:
        out_network:
            driver_opts:
                com.docker.network.driver.mtu: 1400
            ipam:
                driver: default
    

###  0x2 调试环境

笔者采用此方法进行调试，直接将buggyloader.jar放在idea中，在项目配置中添加依赖即可

![](https://p5.ssl.qhimg.com/t011035f3603714655e.png)

关于jar包的启动信息都存放在MANIFEST.MF文件中

![](https://p1.ssl.qhimg.com/t017bab68549a733791.png)

通过该文件笔者得知该jar包启动类为org.springframework.boot.loader.JarLauncher

    
    
    Manifest-Version: 1.0
    Spring-Boot-Classpath-Index: BOOT-INF/classpath.idx
    Implementation-Title: javaDeserializeLabs
    Implementation-Version: 0.0.1-SNAPSHOT
    Spring-Boot-Layers-Index: BOOT-INF/layers.idx
    Start-Class: com.yxxx.javasec.deserialize.JavaDeserializeLabsApplication
    Spring-Boot-Classes: BOOT-INF/classes/
    Spring-Boot-Lib: BOOT-INF/lib/
    Build-Jdk-Spec: 1.8
    Spring-Boot-Version: 2.4.4
    Created-By: Maven Jar Plugin 3.2.0
    Main-Class: org.springframework.boot.loader.JarLauncher
    

在jar包中找到该类，在配置好JDK环境后点击调试该类。

![](https://p0.ssl.qhimg.com/t01be5176052ca7ef70.png)

对于Spring
Web服务就不多讲了，可读性比较高架构本身并不是很难，可以很轻松的在class文件中找到RequestMapping注解标识的路由。比如在indexController.class中的greeting函数是一个路由处理函数，如下图所示。

![](https://p0.ssl.qhimg.com/t01d69977c1994cfce7.png)

一开始将断点下在greeting函数上并不生效，最后用如下指令将jar包解开后，添加依赖进行调试

    
    
    jar -xvf buggyloader.jar
    

## 0x03 题目分析

在做题目的过程中存在了很多问题，不过最后都一一解决了，有以下几个问题

1.该题目反序列化过程中不能存在数组的反序列化  
2.之前分析shiro时的无数组型commons-collections5利用链在该题中报错了  
3.新编写的无数组型commons-collections6利用链同样报错了

首先编写方便反序列化的封装函数

    
    
    ByteArrayOutputStream btout = new ByteArrayOutputStream();
    ObjectOutputStream objOut = new ObjectOutputStream(btout);
    objOut.writeUTF("SJTU");
    objOut.writeInt(1896);
    objOut.writeObject(obj);
    objOut.close();
    byte[] exp = btout.toByteArray();
    String data = Utils.bytesTohexString(exp);
    System.out.println(data);
    

###  0x1 自定义ObjectInputStream

很快啊就找到了反序列化点，但是仔细看代码发现这个方法使用了MyObjectInputStream类进行反序列化

![](https://p1.ssl.qhimg.com/t01ec9ca1bc0dbf273c.png)

自定义的ObjectInputStream类如下，该类主要重写了resolveClass方法，将原先ObjectInputStream类采用的Class.forName方法替换成了classloader的加载方式，这就引来了很多问题

    
    
    public class MyObjectInputStream extends ObjectInputStream {
        private ClassLoader classLoader;
        public MyObjectInputStream(InputStream inputStream) throws Exception {
            super(inputStream);
            URL[] urls = ((URLClassLoader)Transformer.class.getClassLoader()).getURLs();
            this.classLoader = new URLClassLoader(urls);
        }
        protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
            Class clazz = this.classLoader.loadClass(desc.getName());
            return clazz;
        }
    }
    

对比TCTF、Shiro和原生ObjectInputStream的resolveClass如下图所示

![](https://p4.ssl.qhimg.com/t01d4f538f24c8cab33.png)

在ObjectInputStream和Shiro中都采用了Class.forName的类加载机制，但是TCTF这道题仅仅使用了classloader加载。和之前分析Shiro反序列化过程一样需要引入一些类加载知识点

1.Class.forName不支持原生类型，但其他类型都是支持的  
2.Class.loadClass不能加载原生类型和数组类型，其他类型都是支持的  
3.类加载和当前调用类的Classloader有关

这里的原生类型指的是byte、short、int、long、float、double、char、boolean。需要特别注意的是Class.loadClass
**不支持加载数组类型** 。

关于共同之处简单的讲这两个类加载都是基于ClassLoader进行的，关于ClassLoader将会单独写一篇文章进行学习，这里只需要记住ClassLoader制定了类搜索路径，这就意味着如果ClassLoader不对那么将永远不会加载出需要的类。

###  0x2 与Shiro类加载的区别

Shiro实际上实现了一套相对复杂完整的类加载机制ClassUtils(其实是tomcat的那套类加载机制)，细细的观察可以发现里面是存在Class.forName进行类加载的，根据双亲委托原则该方法不能加载WEB-INF/lib下的数组类型。但是无数组型commons-collections3利用链足够了，即使里面有java原生类数组比如
byte[]、Object[]等

![](https://p5.ssl.qhimg.com/t01401ac9dd924d932b.png)

双亲委派原则如下，说白话就是优先让顶级类搜索加载class文件。shiro采用了tomcat的类加载机制，其中Class.forName加载对应下图的4橘黄色图块，也就意味着可以加载tomcat/lib、Java原生类、tomcat指定位置类的数组类型。

![](https://p1.ssl.qhimg.com/t011d7805c68cb3ab0d.png)

此图引自<https://www.cnblogs.com/aspirant/p/8991830.html>

再来看看此题中的类加载方式

![](https://p1.ssl.qhimg.com/t01d753e292a19fe875.png)

该classloader处于这三者之后，他的父加载器是AppClassLoader

![](https://p0.ssl.qhimg.com/t01572a9d75883959aa.png)

###  0x3 无数组型cc5利用链遇到的问题

这个利用方式和 **P神在小密圈中Java安全漫谈-15一文提出的方法** 以及 **wh1t3p1g师傅研究Shiro是构造的利用链类似**
https://www.anquanke.com/post/id/192619，都是使用了templatesImpl进行代码执行，利用newTransformer函数进行触发，巧妙的是通过TiedMapEntry触发LazyMap的get方法完成上述操作，大概是如下流程，最后可以实现调用templates中的任意方法。

![](https://p1.ssl.qhimg.com/t01f3afa50f64c7e6dd.png)

一开始使用的是https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/shiro_CC5_2中的Poc，在反序列化的时候遇到了一些问题

![](https://p5.ssl.qhimg.com/t01b45b0a97f58e0e7e.png)

仔细分析发现BadAttributeValueExpException的父类Throwable在反序列化过程中存在对数组的操作

![](https://p3.ssl.qhimg.com/t01d208eb236d6a34c5.png)

因此判定不能使用BadAttributeValueExpException类作为入口函数。

###  0x4 无数组型cc6利用链遇到的问题

继续将poc调整为 **P神** 和 **wh1t3p1g**
师傅采用的cc6改造链，链接如下https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/TCTFbuggyLoaderCC6.java，不幸的是又报了其他的错误，这个错误应该是在反序列化byte[][]时出现的。

![](https://p0.ssl.qhimg.com/t01de397cf898d14f55.png)

可以分析出造成该问题的原因，TemplatesImpl类在反序列化_bytecodes字段时使用了classloader加载该类型，然而classloader又不能加载数组类型所以报错。

那么确定是TemplatesImpl的问题后思路就比较受限了，因为ysoserial提供的命令执行就这两种

  * transformers调用链
  * TemplatesImpl字节码执行

为了解决这个问题，有两个大方向可以思考

  * 寻找新的命令执行方式
  * 寻找二次反序列化漏洞点

相对来说第二种更方便寻找一些，可以参考这篇文章中的解决方法<https://aluvion.gitee.io/2020/05/12/%E5%88%A9%E7%94%A8%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E8%BF%9B%E8%A1%8CJNDI%E6%B3%A8%E5%85%A5/>

###  0x5 二次反序列化漏洞

上面那片文章中的重点内容如下

![](https://p3.ssl.qhimg.com/t010310b19d514bea7c.png)

沿着这个思路看一看具体是怎样的流程，首先找到二次反序列化点，如果我们能控制base64参数的内容就可以实现classloader绕过，从而使用ObjectInputStream的resolveClass来加载对应的类。

![](https://p2.ssl.qhimg.com/t01380ce9921302269b.png)

继续向上溯源，发现是findRMIServer函数进行的调用，这样只需要控制directoryURL并且控制其中的路径为/stub/就能走到二次反序列化的分支

![](https://p2.ssl.qhimg.com/t0187c5fd5e3efd2b1e.png)

关于该路径的构造可参考oracle官网提供的示例<https://docs.oracle.com/javase/7/docs/api/javax/management/remote/rmi/RMIConnector.html>

继续向上溯源，找到了调用方法为connect，但是这样是无法被反序列化成功的，因为有参函数的构造必然会涉及到数组的反序列化

    
    
    public synchronized void connect(Map<String,?> environment)
        throws IOException {
        final boolean tracing = logger.traceOn();
        String        idstr   = (tracing?"["+this.toString()+"]":null);
        .....
        findRMIServer(jmxServiceURL, usemap);
    

下图是有参函数调用要执行的函数，必须传入Class[]和Object[]

![](https://p1.ssl.qhimg.com/t012d8be61b0239e23a.png)

这么分析来看只能调用RMIConnector类的connect无参方法，只需根据类型创建好对应类即可

    
    
    final RMIConnector rmic = new RMIConnector(new JMXServiceURL("service:jmx:rmi://127.0.0.1:8888/stub/payload"),new HashMap<>());
    

因为InvokerTransformer的一个参数的构造方法为私有方法，这里采用反射的方式调用

    
    
    Constructor con = InvokerTransformer.class.getDeclaredConstructor(String.class);
    con.setAccessible(true);
    InvokerTransformer transformer = (InvokerTransformer) con.newInstance("connect");
    

然后剩下的就是cc6的内容了，完整的payload在<https://raw.githubusercontent.com/BabyTeam1024/ysoserial_analyse/main/TCTFbuggyLoader.java>

###  0x6 发送payload

采用题目中的get发送方式会报400的错误，采用post发送

    
    
    curl -d 'data=payload' http://127.0.0.1:8080/basic
    

可成功执行利用链如下图所示

![](https://p5.ssl.qhimg.com/t01bdcc0e460d06b854.png)

## 0x04 总结

这题配合着之前分析的shiro反序列化漏洞的一些思考一块学习效果极好，可以更好的掌握Java反序列化中ClassLoader发挥的作用。TCTF
buggyLoader主要还是考察反序列化如何绕过不能进行数组类型加载，最后采用的方式是使用二次反序列化漏洞，从而实现无限制的Java原生反序列化，这种方式在实际的漏洞挖掘中也很常见，比如之前笔者分析的Weblogic
CVE-2021-2394漏洞。Java反序列化漏洞还是比较有意思的，同时也有很多知识要总结梳理，《Java安全—ClassLoader类加载器》已经快马加鞭的在路上了。

## 参考文献

<http://pipinstall.cn/2021/10/01/TCTF2021%E6%80%BB%E5%86%B3%E8%B5%9B2%E8%A7%A3Java%E4%B8%8EBypass%20Shiro550%20ClassLoader.loadClass/>  
<https://github.com/c014/0CTF-2021-Final-RevengePHP-and-buggyLoader-exp/blob/main/buggyLoader/Poc.java>  
<https://blog.wanan.world/2021/10/05/TCTF2021-buggyloader-Study/index/>  
<https://www.cnblogs.com/aspirant/p/8991830.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256986](/post/id/256986)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [TCTF](/tag/TCTF)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

