# CVE-2022-22963 SpringCloud Function SpEL注入漏洞分析

阅读量 **96394**

发布时间 : 2022-09-19 14:30:58

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t013eb55efcf89d4e92.jpg)

## 前言

在研究分析了CVE-2022-22980 Spring Data MongoDB
SpEL表达式注入漏洞之后，想起之前在spring4shell爆出之前，存在于SpringCloud
Function中的一个SpEL表达式注入漏洞，编号为CVE-2022-22963。在这里对其进行一波分析和学习。

## 漏洞描述

Spring Cloud Function 是基于 Spring Boot
的函数计算框架。该项目致力于促进函数为主的开发单元，它抽象出所有传输细节和基础架构，并提供一个通用的模型，用于在各种平台上部署基于函数的软件。在Spring
Cloud Function 相关版本，存在SpEL表达式注入。恶意攻击者无需认证可通过构造特定的 HTTP 请求头注入 SpEL
表达式，最终执行任意命令，获取服务器权限。

## 利用范围

3.0.0 <= Spring Cloud Function <= 3.2.2

## 漏洞分析

### **环境搭建**

使用idea新建Spring Cloud Function项目。

pom.xml中引入spring-boot-starter-web、spring-cloud-function-web

在application.properties中添加spring.cloud.function.definition=functionRouter

这里设置端口为8090，默认为8080

运行之后，环境搭建完成。

### **前置知识**

**SpringCloud Function 相关介绍**

简单的介绍，Spring Cloud 是一系列框架的集合，
内部包含了许多框架，这些框架互相协作，共同来构建分布式系统。利用这些组件，可以非常方便地构建一个分布式系统。SpringCloudFunction就是一个SpringBoot开发的Servless中间件（FAAS）。

在环境搭建时，我们在application.properties中添加spring.cloud.function.definition=functionRouter

这里的属性spring.cloud.function.definition 表示声明式函数组合，简单理解就是一个默认路由。具体可参考如下说明。

![](https://p3.ssl.qhimg.com/t019d28d7a8642e4089.png)

**functionRouter**

我们设置spring.cloud.function.definition=functionRouter就是使默认路由绑定具体函数交由用户进行控制。

![](https://p4.ssl.qhimg.com/t017bf44563cee523a8.png)

在spring-cloud-function-web中可以通过设置Message
Headers来传达路由指令，也可以路通过spring.cloud.function.definition
或spring.cloud.function.routing-expression作为应用程序属性进行通信，允许使用 Spring 表达式语言
(SpEL)。

这就是产生SpEL注入的关键所在。

### **动态分析**

在理解了前置知识中相关原理，其实也就能大概知晓漏洞原理。

查看DIFF（https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f）记录。

![](https://p4.ssl.qhimg.com/t018b2c32e5e57dde70.png)

看到从请求头中获取的 spring.cloud.function.routing-expression
之前是由StandardEvaluationContext 解析，修复新增了 isViaHeader 变量做了一个判断，如果是从请求头中获取的
spring.cloud.function.routing-expression 值，使用 SimpleEvaluationContext 解析。

在spring.cloud.function.context.catalog.simpleFunctionRegistry#doApply中。

![](https://p3.ssl.qhimg.com/t0134370d6b514d32d6.png)

在执行function apply方法之后，会跳转到doApply中，对funtion进行判断，判断是不是functionRouter方法。

后续跟进，进入spring.cloud.function.context.config.Routingfunction#route

![](https://p3.ssl.qhimg.com/t0180385dc045d9819e.png)

进入else if 分支， http头spring.cloud.function.routing-expression
不为空，则传入其值到functionFromExpression方法。

随后对传入的header进行解析处理。

后续跟进发现对Spel表达式进行解析的方法就是StandardEvaluationContext

后续跟进，在解析传入的Spel之后，成功触发恶意代码。

## 漏洞复现

![](https://p1.ssl.qhimg.com/t01a14535e8b77291e9.png)

## 修复建议

受影响的组件更新至3.1.7、3.2.3安全版本。

## 参考材料

1.https://docs.spring.io/spring-cloud-function/docs/3.2.2/reference/html/spring-cloud-function.html#_declarative_function_composition

2.https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f

3.https://spring.io.zh.xy2401.com/projects/spring-cloud-function/#overview

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星阑科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/280278](/post/id/280278)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [网络安全](/tag/网络安全)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ae1a72a720da3a7b.png) 星阑科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

