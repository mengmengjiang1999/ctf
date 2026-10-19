## **漏洞描述**

6月20号，VMware发布安全公告，修复了spring Data MongoDB
组件中的一个SpEL表达式注入漏洞，该漏洞的CVSSv3评分为8.2，漏洞编号：CVE-2022-22980，漏洞威胁等级：高危。

Spring Data
MongoDB应用程序在对包含查询参数占位符的SpEL表达式使用@Query或@Aggregation注解的查询方法进行值绑定时，若输入未被过滤，则易遭受SpEL注入攻击。该漏洞允许未经身份验证的攻击者构造恶意数据执行远程代码，最终获取服务器权限。

##  **相关介绍**

Spring Data for MongoDB是 Spring Data
项目的一部分，该项目旨在为新的数据存储提供熟悉和一致的基于Spring的编程模型，同时保留存储的特定特征和功能。Spring
表达式语言(简称SpEL)：是一个支持运行时查询和操作对象图的强大的表达式语言，也是一种简洁的装配Bean的方式，它通过运行期执行的表达式将值装配到Bean的属性或构造器参数中。

通过 SpEL 可以实现：通过 bean 的 id 对 bean 进行引用；调用方式以及引用对象中的属性；计算表达式的值；正则表达式的匹配。

##  **利用范围**

Spring Data MongoDB == 3.4.0

3.3.0 <= Spring Data MongoDB <= 3.3.4

更早或不再受支持的Spring Data MongoDB版本也受到此漏洞影响。

##  **漏洞分析**

###  **环境搭建**

此次采用threedr3am师傅的漏洞demo（https://github.com/threedr3am/learnjavabug/tree/master/spring/spring-data-mongodb-spel-CVE-2022-22980）进行复现分析。

###  **动态调式**

在调试之前查看一下demo中的DemoController，其构造的请求路径为/demo，请求参数为keyword。

![](https://image.3001.net/images/20220712/1657611585_62cd254128dd9fdbb7dd5.png!small)根据diff(https://github.com/spring-projects/spring-data-mongodb/commit/7c5ac764b343d45e5d0abbaba4e82395b471b4c4?diff=split)记录发现，此次漏洞修复的主要位置在ParameterBindingJsonReader
类的 bindableValueFor 函数。

![](https://image.3001.net/images/20220712/1657611601_62cd255170f4d2d441552.png!small)话不多说，先在org.springframework.data.mongodb.util.json.ParameterBindingJsonReader#bindableValueFor函数处打下断点。

![](https://image.3001.net/images/20220712/1657612030_62cd26fea7b05214e02aa.png!small)将环境运行起来后开启debug模式。使用burp抓包并传入payload后，立即触发断点。

![](https://image.3001.net/images/20220712/1657612045_62cd270db8b4cb8ee5a03.png!small)持续跟进，当第一次到达漏洞触发点时，发现并未成功触发payload。

![](https://image.3001.net/images/20220712/1657612069_62cd27250dd9675d25690.png!small)继续跟进，发现在org.springframework.data.mongodb.util.json.ParameterBindingJsonReader#readBsonType函数中判断token的Type属性后，进入到UNQUOTED_STRING，在这里进行setCurrentName操作，value为id。

![](https://image.3001.net/images/20220712/1657612082_62cd2732f338377bee45c.png!small)随后回到bindableValueFor函数，后续经过对value的处理，value由id变为了:#{?0}。

![](https://image.3001.net/images/20220712/1657612098_62cd27423b7a3e94ff2e6.png!small)

在value为:#{?0}后，会再次进入org.springframework.data.mongodb.util.json.ParameterBindingJsonReader#bindableValueFor函数。

在bindableValueFor函数中首先对tokenValue进行了赋值，随后对tokenValue进行PARAMETER_BINDING_PATTERN和EXPRESSION_BINDING_PATTERN规则匹配。

![](https://image.3001.net/images/20220712/1657612115_62cd2753e78e8f0abf789.png!small)EXPRESSION_BINDING_PATTERN只能匹配
?#{} 或者：#{}形式的字符串。

![](https://image.3001.net/images/20220712/1657612131_62cd2763111596f94d238.png!small)随后，将赋值交给binding，再通过substring取出占位符?0

![](https://image.3001.net/images/20220712/1657612144_62cd2770eafc5c3cd98ae.png!small)接下来通过for循环将占位符和传入的payload进行替换。

![](https://image.3001.net/images/20220712/1657612164_62cd27849f1776517ba37.png!small)同时通过PARAMETER_BINDING_PATTERN规则匹配成功后即认为是spel表达式格式，此时expression为传入payload。

![](https://image.3001.net/images/20220712/1657612228_62cd27c4434ab7a7de73a.png!small)执行this.evaluateExpression。

![](https://image.3001.net/images/20220712/1657612241_62cd27d1ad25d55b93394.png!small)最终进入org.springframework.data.mongodb.repository.query.DefaultSpELExpressionEvaluator#evaluate函数，此时使用的是
StandardEvaluationContext 类型，包含了 SpEL 所有的功能。

![](https://image.3001.net/images/20220712/1657612255_62cd27df96a083eed8228.png!small)

此时的 SpEL表达式为之前构造的恶意攻击载荷，可成功命令执行。

###  **漏洞复现**

![](https://image.3001.net/images/20220712/1657612276_62cd27f406772c4d317d8.png!small)

##  **修复建议**

目前此漏洞已经修复，受影响的用户建议尽快升级至官方修护版本：

Spring Data MongoDB 3.4.1或更高版本；

Spring Data MongoDB 3.3.5或更高版本。

下载链接：

https://github.com/spring-projects/spring-data-mongodb/tags

##  **参考材料**

1.https://tanzu.vmware.com/security/cve-2022-22980

2.https://xz.aliyun.com/t/11478

3.https://spring.io/blog/2022/06/20/spring-data-mongodb-spel-expression-injection-vulnerability-cve-2022-22980

