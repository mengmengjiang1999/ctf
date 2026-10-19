# Spring Cloud Function SPEL表达式注入漏洞

阅读量 **175387**

发布时间 : 2022-03-30 09:30:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01bae6a6078fc58ef9.png)

## 漏洞描述

Spring框架为现代基于java的企业应用程序(在任何类型的部署平台上)提供了一个全面的编程和配置模型。

Spring Cloud 中的 serveless框架 Spring Cloud Function 中的 RoutingFunction 类的 apply
方法将请求头中的“spring.cloud.function.routing-expression”参数作为 Spel
表达式进行处理，造成Spel表达式注入，攻击者可通过该漏洞执行任意代码。

## 利用条件

3.0.0.RELEASE <= Spring Cloud Function <= 3.2.2

## 环境搭建

在官方网页新建一个 Spring boot 项目(https://start.spring.io/)、使用idea启动。

![](https://p5.ssl.qhimg.com/t01a6390da1a7dc96bc.jpg)

修改 pom.xml配置文件

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.6.5</version>
    <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <description>Demo project for Spring Boot</description>
    <properties>
    <java.version>17</java.version>
    <spring-cloud.version>2021.0.1</spring-cloud.version>
    </properties>
    <dependencies>
    <dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-function-context</artifactId>
    </dependency>
    <dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter</artifactId>
    </dependency>
    <dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-task</artifactId>
    </dependency>
    
    <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
    </dependency>
    
    <dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-function-webflux</artifactId>
    </dependency>
    
    <dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-function-dependencies</artifactId>
    <version>3.2.2</version>
    <type>pom</type>
    </dependency>
    
    <dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-function-web</artifactId>
    <version>3.2.2</version>
    </dependency>
    </dependencies>
    <dependencyManagement>
    <dependencies>
    <dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-dependencies</artifactId>
    <version>${spring-cloud.version}</version>
    <type>pom</type>
    <scope>import</scope>
    </dependency>
    </dependencies>
    </dependencyManagement>
    
    <build>
    <plugins>
    <plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    </plugin>
    </plugins>
    </build>
    
    </project>

最后访问 http://127.0.0.1:8080. 出现以下页面表示成功。

![](https://p1.ssl.qhimg.com/t0164527df56ee9a243.jpg)

## 漏洞复现

### **漏洞原理**

apply方法会将http头部中的Spel表达式进行解析，从而造成Spel表达式注入。

查看官方diff(https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f)

进入springframework/cloud/function/context/config/RoutingFunction文件。进入调试模式、将断点添加到apply()方法。

进入到apply()方法后、会调用route() 在该方法中会去判读input是否为 message的实例，function 是否为空、然后进入else
if 去获取头信息、获取key值 spring.cloud.function.routing-expression
、在中间会对有无空格做判断。然后继续向下走。

![](https://p2.ssl.qhimg.com/t014d2f96789d58f2fd.jpg)

会进入到springframework/cloud/function/context/config/RoutingFunction/functionFromExpression()方法。

routingExpression 会做为参数传入到
springframework/expression/common/TemplateAwareExpressionParser/parseExpression()方法中。

判读其context是否为none值 在进入

springframework/expression/spel/standard/SpelExpressionParser/doPareExpression()
会new 一个 InternalSpelExpressionParser 类调用 doPareExpression() 继续跟进。

![](https://p4.ssl.qhimg.com/t0102a1a099bc8c5e27.jpg)

在springframeworl/expression/spel/stand/InternalSpelExpressionParser/doParseExpression()方法中、会在tokenizer.process()中
对token进行 源码与字节码的判断操作、继续向下。

![](https://p4.ssl.qhimg.com/t0186bd3a27048b16bd.jpg)

会new 一个SpelExpression() 跟进到

springframwork/expression/spel/standard/SpelExpression/SpelExpression()。

![](https://p2.ssl.qhimg.com/t014d24dc80dca4e616.jpg)

在SpelExpression()方法中会将将表达式赋值到 this.expression 继续跟进 return到
springframework/expression/spel/standard/SpelpressionParser/doParseExpression()、继续return到springframework/expression/common/TemplateAwareExpressionPareser/pareExpression()、return
springframework/cloud/function/context/config/RoutingFunction/functionFromExpression()

![](https://p5.ssl.qhimg.com/t013c4af6eb1ef249bc.jpg)

在functionFromExpression()方法中会进入MessageUtils.toCaseInsensitiveHeadersStructure()。

![](https://p4.ssl.qhimg.com/t01998ffbb758a487c1.jpg)

调用MessageStructureWithCaseInsensitiveHeaderKeys()，进入到putAll()方法 获取message中头信息。

最后会进入漏洞触发点。

![](https://p4.ssl.qhimg.com/t011f93cfffb35c7ef0.jpg)

### **漏洞测试**

Payload 的构造可以参考官方测试用例。

本次利用创建文件测试。使用payload touch /tmp/xxxxxx.test.test。

![](https://p5.ssl.qhimg.com/t010e510985b5fc3b93.jpg)

![](https://p2.ssl.qhimg.com/t01e6aa507c11faa341.jpg)

## 修复建议

官方已经发布漏洞补丁。(https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f)

目前还暂未更新版本。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星阑科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/271221](/post/id/271221)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [安全漏洞](/tag/安全漏洞)
  * [Spring Cloud Function SPEL](/tag/Spring Cloud Function SPEL)

 **+1** __7赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ae1a72a720da3a7b.png) 星阑科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

