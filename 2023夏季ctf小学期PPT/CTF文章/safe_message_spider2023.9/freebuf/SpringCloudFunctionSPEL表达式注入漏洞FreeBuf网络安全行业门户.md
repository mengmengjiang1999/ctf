## **漏洞描述**

Spring框架为现代基于java的企业应用程序(在任何类型的部署平台上)提供了一个全面的编程和配置模型。

Spring Cloud 中的 serveless框架 Spring Cloud Function 中的 RoutingFunction 类的 apply
方法将请求头中的“spring.cloud.function.routing-expression”参数作为 Spel
表达式进行处理，造成Spel表达式注入，攻击者可通过该漏洞执行任意代码。

##  **利用条件**

3.0.0.RELEASE <= Spring Cloud Function <= 3.2.2

##  **环境搭建**

在官方网页新建一个 Spring boot 项目(https://start.spring.io/)、使用idea启动。

![](https://image.3001.net/images/20220330/1648615398_6243dfe66c83e6225eb70.jpeg!small)

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

![](https://image.3001.net/images/20220330/1648615453_6243e01dccf80b684e9c6.jpeg!small)
****

##  **漏洞复现**  

###  **漏洞原理**

apply方法会将http头部中的Spel表达式进行解析，从而造成Spel表达式注入。

查看官方diff(https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f)

![](https://image.3001.net/images/20220330/1648615507_6243e0531f47422a8e2b7.jpeg!small)![](https://image.3001.net/images/20220330/1648615514_6243e05a1fd9524187e69.jpeg!small)  

进入springframework/cloud/function/context/config/RoutingFunction文件。进入调试模式、将断点添加到apply()方法。

![](https://image.3001.net/images/20220330/1648615558_6243e086e1cf7567fdf8c.jpeg!small)进入到apply()方法后、会调用route()
在该方法中会去判读input是否为 message的实例，function 是否为空、然后进入else if 去获取头信息、获取key值
spring.cloud.function.routing-expression 、在中间会对有无空格做判断。然后继续向下走。  

![](https://image.3001.net/images/20220330/1648615576_6243e098ddbf6ab653438.jpeg!small)

会进入到springframework/cloud/function/context/config/RoutingFunction/functionFromExpression()方法。

![](https://image.3001.net/images/20220330/1648615602_6243e0b23dd5c86eafca0.jpeg!small)routingExpression
会做为参数传入到
springframework/expression/common/TemplateAwareExpressionParser/parseExpression()方法中。  

![](https://image.3001.net/images/20220330/1648615624_6243e0c8f3010de886c83.jpeg!small)

判读其context是否为none值 在进入

springframework/expression/spel/standard/SpelExpressionParser/doPareExpression()
会new 一个 InternalSpelExpressionParser 类调用 doPareExpression() 继续跟进。

![](https://image.3001.net/images/20220330/1648615646_6243e0deae0e7801eea5d.jpeg!small)在springframeworl/expression/spel/stand/InternalSpelExpressionParser/doParseExpression()方法中、会在tokenizer.process()中
对token进行 源码与字节码的判断操作、继续向下。  

![](https://image.3001.net/images/20220330/1648615666_6243e0f277151e368a154.jpeg!small)

会new 一个SpelExpression() 跟进到

springframwork/expression/spel/standard/SpelExpression/SpelExpression()。

![](https://image.3001.net/images/20220330/1648615686_6243e10677f7523711289.jpeg!small)在SpelExpression()方法中会将将表达式赋值到
this.expression 继续跟进 return到
springframework/expression/spel/standard/SpelpressionParser/doParseExpression()、继续return到springframework/expression/common/TemplateAwareExpressionPareser/pareExpression()、return
springframework/cloud/function/context/config/RoutingFunction/functionFromExpression()  

![](https://image.3001.net/images/20220330/1648615708_6243e11c82d26c4011225.jpeg!small)

在functionFromExpression()方法中会进入MessageUtils.toCaseInsensitiveHeadersStructure()。

![](https://image.3001.net/images/20220330/1648615724_6243e12c134282e223467.jpeg!small)

调用MessageStructureWithCaseInsensitiveHeaderKeys()，进入到putAll()方法 获取message中头信息。

![](https://image.3001.net/images/20220330/1648615746_6243e142c7f4ef728376f.jpeg!small)  

最后会进入漏洞触发点。

![](https://image.3001.net/images/20220330/1648615761_6243e151cf7b2dfad840e.jpeg!small)

 **漏洞测试**

Payload 的构造可以参考官方测试用例。

![](https://image.3001.net/images/20220330/1648615801_6243e179e06bbafabed9f.jpeg!small)本次利用创建文件测试。使用payload
touch /tmp/xxxxxx.test.test。  

![](https://image.3001.net/images/20220330/1648615813_6243e185239a9c3c3a3d2.jpeg!small)![](https://image.3001.net/images/20220330/1648615827_6243e1933d087c93462f8.jpeg!small)  

##  **修复建议**

官方已经发布漏洞补丁。(https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f)

目前还暂未更新版本。

