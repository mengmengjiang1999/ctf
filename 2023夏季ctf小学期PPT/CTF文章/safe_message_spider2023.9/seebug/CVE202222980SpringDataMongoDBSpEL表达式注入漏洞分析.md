**作者：xxhzz@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/8zzXZgSwHAmte5t7KSDhdA>**

## **漏洞描述**

6月20号，VMware发布安全公告，修复了spring Data MongoDB
组件中的一个SpEL表达式注入漏洞，该漏洞的CVSSv3评分为8.2，漏洞编号：CVE-2022-22980，漏洞威胁等级：高危。

Spring Data
MongoDB应用程序在对包含查询参数占位符的SpEL表达式使用@Query或@Aggregation注解的查询方法进行值绑定时，若输入未被过滤，则易遭受SpEL注入攻击。该漏洞允许未经身份验证的攻击者构造恶意数据执行远程代码，最终获取服务器权限。

## **相关介绍**

Spring Data for MongoDB是 Spring Data
项目的一部分，该项目旨在为新的数据存储提供熟悉和一致的基于Spring的编程模型，同时保留存储的特定特征和功能。Spring
表达式语言(简称SpEL)：是一个支持运行时查询和操作对象图的强大的表达式语言，也是一种简洁的装配Bean的方式，它通过运行期执行的表达式将值装配到Bean的属性或构造器参数中。

通过 SpEL 可以实现：通过 bean 的 id 对 bean 进行引用；调用方式以及引用对象中的属性；计算表达式的值；正则表达式的匹配。

## **利用范围**

Spring Data MongoDB == 3.4.0

3.3.0 <= Spring Data MongoDB <= 3.3.4

更早或不再受支持的Spring Data MongoDB版本也受到此漏洞影响。

## **漏洞分析**

### **环境搭建**

此次采用threedr3am师傅的漏洞demo（<https://github.com/threedr3am/learnjavabug/tree/master/spring/spring-data-mongodb-spel-CVE-2022-22980>）进行复现分析。

### **动态调式**

在调试之前查看一下demo中的DemoController，其构造的请求路径为/demo，请求参数为keyword。

![](https://images.seebug.org/content/images/2022/11/7ab0fb55-9fdd-4138-b264-d1f6cd08ce2f.png-w331s)

根据diff(<https://github.com/spring-projects/spring-data-mongodb/commit/7c5ac764b343d45e5d0abbaba4e82395b471b4c4?diff=split>)记录发现，此次漏洞修复的主要位置在ParameterBindingJsonReader
类的 bindableValueFor 函数。

![](https://images.seebug.org/content/images/2022/11/27959e72-424d-44fb-bb76-39a5acc08333.png-w331s)

话不多说，先在org.springframework.data.mongodb.util.json.ParameterBindingJsonReader#bindableValueFor函数处打下断点。

![](https://images.seebug.org/content/images/2022/11/508b74a7-eb9f-4e96-853e-f288fb762751.png-w331s)

将环境运行起来后开启debug模式。使用burp抓包并传入payload后，立即触发断点。

![](https://images.seebug.org/content/images/2022/11/c8fd2444-aba9-4f90-a5ec-d2435359a17a.png-w331s)

持续跟进，当第一次到达漏洞触发点时，发现并未成功触发payload。

![](https://images.seebug.org/content/images/2022/11/3146bc8b-3199-4b2e-b4dc-15a68154ae44.png-w331s)

继续跟进，发现在org.springframework.data.mongodb.util.json.ParameterBindingJsonReader#readBsonType函数中判断token的Type属性后，进入到UNQUOTED_STRING，在这里进行setCurrentName操作，value为id。
![](https://images.seebug.org/content/images/2022/11/eabdc92c-d70a-4d43-8eef-c6f9b32cbbc4.png-w331s)

随后回到bindableValueFor函数，后续经过对value的处理，value由id变为了:#{?0}。

![](https://images.seebug.org/content/images/2022/11/700e49e3-8f75-4428-bbc7-c71cc9df9a53.png-w331s)

在value为:#{?0}后，会再次进入org.springframework.data.mongodb.util.json.ParameterBindingJsonReader#bindableValueFor函数。

在bindableValueFor函数中首先对tokenValue进行了赋值，随后对tokenValue进行PARAMETER_BINDING_PATTERN和EXPRESSION_BINDING_PATTERN规则匹配。

![](https://images.seebug.org/content/images/2022/11/b0d96427-b2fb-4c3b-8200-4a7f8cd214b1.png-w331s)

EXPRESSION_BINDING_PATTERN只能匹配 ?#{} 或者：#{}形式的字符串。

![](https://images.seebug.org/content/images/2022/11/c99c37ba-ca95-465b-85e1-563a6365ae12.png-w331s)

随后，将赋值交给binding，再通过substring取出占位符?0

![](https://images.seebug.org/content/images/2022/11/54184fc6-ae5b-43c9-a022-129e6d4ff717.png-w331s)

接下来通过for循环将占位符和传入的payload进行替换。

![](https://images.seebug.org/content/images/2022/11/616d82c5-18c9-4ed4-ab3b-b634e6def381.png-w331s)

同时通过PARAMETER_BINDING_PATTERN规则匹配成功后即认为是spel表达式格式，此时expression为传入payload。

![](https://images.seebug.org/content/images/2022/11/bc751901-4d2b-49d4-8bbb-3228992096a2.png-w331s)

执行this.evaluateExpression。

![](https://images.seebug.org/content/images/2022/11/63b4a8e4-d44b-4773-92a7-aa2887f281ed.png-w331s)

最终进入org.springframework.data.mongodb.repository.query.DefaultSpELExpressionEvaluator#evaluate函数，此时使用的是
StandardEvaluationContext 类型，包含了 SpEL 所有的功能。

![](https://images.seebug.org/content/images/2022/11/8f4badb6-e17a-4466-97ef-705706349a5d.png-w331s)

此时的 SpEL表达式为之前构造的恶意攻击载荷，可成功命令执行。

### **漏洞复现**

![](https://images.seebug.org/content/images/2022/11/350a681b-55a3-4967-bfd2-cb2b09b7aa27.png-w331s)

## **修复建议**

目前此漏洞已经修复，受影响的用户建议尽快升级至官方修护版本：

Spring Data MongoDB 3.4.1或更高版本；

Spring Data MongoDB 3.3.5或更高版本。

下载链接：

<https://github.com/spring-projects/spring-data-mongodb/tags>

## **参考材料**

1.<https://tanzu.vmware.com/security/cve-2022-22980>

2.<https://xz.aliyun.com/t/11478>

3.<https://spring.io/blog/2022/06/20/spring-data-mongodb-spel-expression-injection-vulnerability-cve-2022-22980>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2004/>

