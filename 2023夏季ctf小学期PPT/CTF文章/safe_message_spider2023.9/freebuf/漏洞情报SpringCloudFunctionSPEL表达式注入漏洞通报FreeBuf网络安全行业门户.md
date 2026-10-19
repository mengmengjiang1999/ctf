近日，Spring Cloud Function官方测试版本通报了一个有关Spring Cloud Function
SPEL表达式注入漏洞。利用该漏洞，远程攻击者可通过SPEL表达式注入的方式在远程执行注入攻击。

![](https://image.3001.net/images/20220326/1648298481_623f09f13ac9d0d312eef.png!small)

## 漏洞描述：

Spring Cloud Function是基于 Spring Boot
的函数计算框架，它抽象出所有传输细节和基础架构，允许开发人员保留所有熟悉的工具和流程，并专注于业务逻辑。

此次发现的漏洞利用了SPEL表达式注入实现攻击，根据目前已知的信息，访问Spring Cloud
Function的HTTP请求头中具有spring.cloud.function.routing-expression。，它的SpEL表达式可进行注入，远程攻击者在注入后可通过 StandardEvaluationContext解析执行远程命令。

## 影响范围：

3.0.0.RELEASE <= Spring Cloud Function <= 3.2.2

## 解决方案：

目前Spring Cloud官方已经推出补丁修复漏洞，受影响用户可以通过官方补丁进行修复。

官方链接：

<https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f>

