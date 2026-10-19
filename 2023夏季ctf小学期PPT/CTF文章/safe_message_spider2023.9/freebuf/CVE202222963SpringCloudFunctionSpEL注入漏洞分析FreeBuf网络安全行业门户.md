## **前言**

在研究分析了CVE-2022-22980 Spring Data MongoDB
SpEL表达式注入漏洞之后，想起之前在spring4shell爆出之前，存在于SpringCloud
Function中的一个SpEL表达式注入漏洞，编号为CVE-2022-22963。在这里对其进行一波分析和学习。

##  **漏洞描述**

Spring Cloud Function 是基于 Spring Boot
的函数计算框架。该项目致力于促进函数为主的开发单元，它抽象出所有传输细节和基础架构，并提供一个通用的模型，用于在各种平台上部署基于函数的软件。在Spring
Cloud Function 相关版本，存在SpEL表达式注入。恶意攻击者无需认证可通过构造特定的 HTTP 请求头注入 SpEL
表达式，最终执行任意命令，获取服务器权限。

##  **利用范围**

3.0.0 <= Spring Cloud Function <= 3.2.2

##  **漏洞分析**

###  **环境搭建**

使用idea新建Spring Cloud Function项目。

![](https://image.3001.net/images/20220916/1663297682_6323e8925e1fab2bb2856.png!small)pom.xml中引入spring-boot-starter-web、spring-cloud-function-web

![](https://image.3001.net/images/20220916/1663297697_6323e8a15a5e9baa6f2ca.png!small)在application.properties中添加spring.cloud.function.definition=functionRouter

![](https://image.3001.net/images/20220916/1663297717_6323e8b5065236a923e4b.png!small)这里设置端口为8090，默认为8080

![](https://image.3001.net/images/20220916/1663297745_6323e8d1001662154a0ee.png!small)

运行之后，环境搭建完成。

###  **前置知识**

 **SpringCloud Function 相关介绍**

简单的介绍，Spring Cloud 是一系列框架的集合，
内部包含了许多框架，这些框架互相协作，共同来构建分布式系统。利用这些组件，可以非常方便地构建一个分布式系统。SpringCloudFunction就是一个SpringBoot开发的Servless中间件（FAAS）。

![](https://image.3001.net/images/20220916/1663297800_6323e90869f9a6cd1d784.png!small)

在环境搭建时，我们在application.properties中添加spring.cloud.function.definition=functionRouter

这里的属性spring.cloud.function.definition 表示声明式函数组合，简单理解就是一个默认路由。具体可参考如下说明。

![](https://image.3001.net/images/20220916/1663297821_6323e91d6d15738a3b17a.png!small)

 **functionRouter**

![](https://image.3001.net/images/20220916/1663297850_6323e93a00cc07bc8a7f6.png!small)
我们设置spring.cloud.function.definition=functionRouter就是使默认路由绑定具体函数交由用户进行控制。

![](https://image.3001.net/images/20220916/1663297875_6323e95337c7eaf000168.png!small)

在spring-cloud-function-web中可以通过设置Message
Headers来传达路由指令，也可以路通过spring.cloud.function.definition
或spring.cloud.function.routing-expression作为应用程序属性进行通信，允许使用 Spring 表达式语言
(SpEL)。

这就是产生SpEL注入的关键所在。

###  **动态分析**

在理解了前置知识中相关原理，其实也就能大概知晓漏洞原理。

查看DIFF（https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f）记录。

![](https://image.3001.net/images/20220916/1663297910_6323e97638c3efb337c1b.png!small)

看到从请求头中获取的 spring.cloud.function.routing-expression
之前是由StandardEvaluationContext 解析，修复新增了 isViaHeader 变量做了一个判断，如果是从请求头中获取的
spring.cloud.function.routing-expression 值，使用 SimpleEvaluationContext 解析。

在spring.cloud.function.context.catalog.simpleFunctionRegistry#doApply中。

![](https://image.3001.net/images/20220916/1663297932_6323e98c0e420e2a70551.png!small)

在执行function apply方法之后，会跳转到doApply中，对funtion进行判断，判断是不是functionRouter方法。

后续跟进，进入spring.cloud.function.context.config.Routingfunction#route

![](https://image.3001.net/images/20220916/1663297950_6323e99edf2ece1fa3c75.png!small)进入else
if 分支， http头spring.cloud.function.routing-expression
不为空，则传入其值到functionFromExpression方法。

![](https://image.3001.net/images/20220916/1663297971_6323e9b30c40f4b1811fe.png!small)随后对传入的header进行解析处理。

![](https://image.3001.net/images/20220916/1663297986_6323e9c2c27bdbdeb09e6.png!small)后续跟进发现对Spel表达式进行解析的方法就是StandardEvaluationContext

![](https://image.3001.net/images/20220916/1663298003_6323e9d32bfa72bee1e27.png!small)后续跟进，在解析传入的Spel之后，成功触发恶意代码。

![](https://image.3001.net/images/20220916/1663298018_6323e9e29c35f85f08e1c.png!small)

##  **漏洞复现**

![](https://image.3001.net/images/20220916/1663298046_6323e9fec5161738ec673.png!small)

##  **修复建议**

受影响的组件更新至3.1.7、3.2.3安全版本。

##  **参考材料**

1.https://docs.spring.io/spring-cloud-function/docs/3.2.2/reference/html/spring-cloud-function.html#_declarative_function_composition

2.https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f

3.https://spring.io.zh.xy2401.com/projects/spring-cloud-function/#overview

