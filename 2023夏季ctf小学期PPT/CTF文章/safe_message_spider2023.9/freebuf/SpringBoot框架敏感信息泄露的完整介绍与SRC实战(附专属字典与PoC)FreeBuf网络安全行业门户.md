## #前言

##Spring Boot框架介绍  
`Spring`框架功能很强大，但是就算是一个很简单的项目，我们也要配置很多东西。因此就有了`Spring
Boot`框架，它的作用很简单，就是帮我们自动配置，其设计目的是用来简化新`Spring`应用的初始搭建以及开发过程。`Spring
Boot`框架的核心就是自动配置，只要存在相应的jar包，`Spring`就帮我们自动配置。该框架使用了特定的方式来进行配置，从而使开发人员不再需要定义样板化的配置。如果默认配置不能满足需求，我们还可以替换掉自动配置类，使用我们自己的配置。另外，`Spring
Boot`还集成了嵌入式的Web服务器，系统监控等很多有用的功能，让我们快速构建企业及应用程序。

##Actuator中间件工具介绍  
`Actuator`是`Spring Boot`提供的服务监控和管理工具。当`Spring
Boot`应用程序运行时，它会自动将多个端点注册到路由进程中。而由于对这些端点的错误配置，就有可能导致一些敏感信息泄露。

## #如何发现Spring Boot框架

通常有两种方法：  
1.网站的icon文件是一个绿色的树叶：  
[![](https://image.3001.net/images/20210924/1632459245_614d59edb7f942569fc76.png!small)](https://image.3001.net/images/20210924/1632459245_614d59edb7f942569fc76.png!small)

2.页面存在特有的报错信息：[![](https://image.3001.net/images/20210924/1632459246_614d59ee4317b285ce5e3.png!small)](https://image.3001.net/images/20210924/1632459246_614d59ee4317b285ce5e3.png!small)

## #敏感信息泄露所影响的版本

`Spring Boot < 1.5`： 默认未授权访问所有端点。  
`Spring Boot >= 1.5`： 默认只允许访问`/health`和`/info`端点，但是此安全性通常被应用程序开发人员禁用。  
#每个端点的作用  
官方文档有对它们展开详细的描述：

    
    
    路径					描述					默认启用
    auditevents	显示当前应用程序的审计事件信息	Yes
    beans	显示一个应用中所有Spring Beans的完整列表	Yes
    conditions	显示配置类和自动配置类(configuration and auto-configuration	classes)的状态及它们被应用或未被应用的原因
    configprops	显示一个所有@ConfigurationProperties的集合列表	Yes
    env	显示来自Spring的 ConfigurableEnvironment的属性	Yes
    flyway	显示数据库迁移路径，如果有的话	Yes
    health	显示应用的健康信息（当使用一个未认证连接访问时显示一个简单	的’status’，使用认证连接访问则显示全部信息详情）
    info	显示任意的应用信息	Yes
    liquibase	展示任何Liquibase数据库迁移路径，如果有的话	Yes
    metrics	展示当前应用的metrics信息	Yes
    mappings	显示一个所有@RequestMapping路径的集合列表	Yes
    scheduledtasks	显示应用程序中的计划任务	Yes
    sessions	允许从Spring会话支持的会话存储中检索和删除(retrieval and deletion)	用户会话。使用Spring Session对反应性Web应用程序的支持时不可用。
    shutdown	允许应用以优雅的方式关闭（默认情况下不启用）	No
    threaddump	执行一个线程dump	Yes
    heapdump	返回一个GZip压缩的hprof堆dump文件	Yes
    jolokia	通过HTTP暴露JMX beans（当Jolokia在类路径上时，WebFlux不可用）	Yes
    logfile	返回日志文件内容（如果设置了logging.file或logging.path属性的话），支持使用HTTP Range头接收日志文件内容的部分信息	Yes
    prometheus	以可以被Prometheus服务器抓取的格式显示metrics信息	Yes
    

##访问/actuator  
如果网站设置了`management.endpoints.web.exposure.include`为`*`，那么我们可以在`/actuator`看到所有存在的断点：  
[![](https://image.3001.net/images/20210924/1632459247_614d59ef179f71c50a13f.png!small)](https://image.3001.net/images/20210924/1632459247_614d59ef179f71c50a13f.png!small)

##访问/actuator/version  
泄露版本信息[![](https://image.3001.net/images/20210924/1632459247_614d59efaf314b7a4bacc.png!small)](https://image.3001.net/images/20210924/1632459247_614d59efaf314b7a4bacc.png!small)

##访问/env或者/actuator/env  
获取环境属性  
其中redis账户和信息泄露：  
[![](https://image.3001.net/images/20210924/1632459248_614d59f0562e8c5c1b2d4.png!small)](https://image.3001.net/images/20210924/1632459248_614d59f0562e8c5c1b2d4.png!small)

其中数据库账户和信息泄露：  
[![](https://image.3001.net/images/20210924/1632459249_614d59f13c2b5dd6bda3f.png!small)](https://image.3001.net/images/20210924/1632459249_614d59f13c2b5dd6bda3f.png!small)

##访问/actuator/metrics  
获得每个度量的名称，其中主要监控了JVM内容使用、GC情况、类加载信息等：  
[![](https://image.3001.net/images/20210924/1632459250_614d59f23e009e8870c91.png!small)](https://image.3001.net/images/20210924/1632459250_614d59f23e009e8870c91.png!small)

如果想要得到每个度量的详细信息，你需要传递度量的名称到URL中，比如这样:  
`http://x.x.x.x/actuator/metrics/http.server.requests`

##访问/actuator/threaddump  
获取服务器的线程堆栈：  
[![](https://image.3001.net/images/20210924/1632459250_614d59f2d91eb514bc6dd.png!small)](https://image.3001.net/images/20210924/1632459250_614d59f2d91eb514bc6dd.png!small)

##访问/actuator/loggers  
获取服务器的日志级别：  
[![](https://image.3001.net/images/20210924/1632459251_614d59f396075401357a2.png!small)](https://image.3001.net/images/20210924/1632459251_614d59f396075401357a2.png!small)

##访问/actuator/configprops  
查看配置文件中设置的属性内容，以及一些配置属性的默认值：  
[![](https://image.3001.net/images/20210924/1632459252_614d59f42d3bbda656bf0.png!small)](https://image.3001.net/images/20210924/1632459252_614d59f42d3bbda656bf0.png!small)

##访问/actuator/info  
展示了关于应用的一般信息，这些信息从编译文件比如`META-INF/build-info.properties`或者git文件比如`git.properties`或者任何环境的`property`中获取:  
[![](https://image.3001.net/images/20210924/1632459252_614d59f4c40c3dc909b48.png!small)](https://image.3001.net/images/20210924/1632459252_614d59f4c40c3dc909b48.png!small)

##访问/actuator/prometheus  
获取一些监控指标：  
[![](https://image.3001.net/images/20210924/1632459253_614d59f56dcb04c1540d4.png!small)](https://image.3001.net/images/20210924/1632459253_614d59f56dcb04c1540d4.png!small)

##访问/actuator/mappings  
其中描述全部的URI路径，以及它们和控制器的映射关系：  
访问：`http://x.x.x.x/actuator/mappings`

    
    
    {
      "/**/favicon.ico": {
        "bean": "faviconHandlerMapping"
      },
      "{[/hello]}": {
        "bean": "requestMappingHandlerMapping",
        "method": "public java.lang.String com.neo.controller.HelloController.index()"
      },
      "{[/error]}": {
        "bean": "requestMappingHandlerMapping",
        "method": "public org.springframework.http.ResponseEntity<java.util.Map<java.lang.String, java.lang.Object>> org.springframework.boot.autoconfigure.web.BasicErrorController.error(javax.servlet.http.HttpServletRequest)"
      }
    }
    

##访问/actuator/health  
`health`endpoint只展示了简单的UP和DOWN状态，比如这样：  
[![](https://image.3001.net/images/20210924/1632459254_614d59f6358a7eddcc387.png!small)](https://image.3001.net/images/20210924/1632459254_614d59f6358a7eddcc387.png!small)  
为了获得健康检查中所有指标的详细信息，就需要通过在`application.yaml`中增加如下内容：

    
    
    management:
      endpoint:
        health:
          show-details: always
    

一旦你打开上述开关，那么在`/health`中可以看到详细内容，比如下面这样：

    
    
    {
      "status": "UP",
      "diskSpace": {
        "status": "UP",
        "total": 209715195904,
        "free": 183253909504,
        "threshold": 10485760
      }
      "db": {
            "status": "UP",
            "database": "MySQL",
            "hello": 1
        }
    }
    

##访问/heapdump或者/actuator/heapdump  
会返回一个GZip压缩的JVM堆dump，其中是`jvm heap`信息。下载的`heapdump`文件大小通常在 50M—500M
之间，有时候也可能会大于 2G。然后使用 MAT 可以获得`jvm heap`中的密码明文。

其中还有部分端点，这里就不一一展示了。  
#Spring Boot敏感端点路径专属字典  
这里送波福利吧：

其中字典放在了 **挽风安全** 公众号，输入 **SpringBoot信息泄露** 就可以获取字典下载地址了。

## #用工具跑字典

##Burp Suite  
用Burp Suite跑似乎有点问题：  
在Intruder爆破模块中，将payload设置成如此形式，跑不出来：  
[![](https://image.3001.net/images/20210924/1632459255_614d59f70bbf64d2829ec.png!small)](https://image.3001.net/images/20210924/1632459255_614d59f70bbf64d2829ec.png!small)

[![](https://image.3001.net/images/20210924/1632459255_614d59f7a28281b9488b4.jpg!small)](https://image.3001.net/images/20210924/1632459255_614d59f7a28281b9488b4.jpg!small)

然而手测完页面却能访问，而且是有敏感信息的，所以这里有点问题。然后上网搜完，说是payload要设置成如下形式：  
![image](https://image.3001.net/images/20210924/1632459108_614d59643e1559f754ecd.png!small)

其中有部分状态码返回200了，还有Content-length也返回的是正确的，可是还是大部分是错误的，和我手测不相符：  
[![](https://image.3001.net/images/20210924/1632459256_614d59f84201a1c6b44a8.png!small)](https://image.3001.net/images/20210924/1632459256_614d59f84201a1c6b44a8.png!small)

这里如果有师傅知道原因请告诉我。

##自己写python脚本  
既然上面出现了问题，那么我只能自己写一个来跑了：

其中脚本放在了 **挽风安全** 公众号，输入 **SpringBoot信息泄露** 就可以获取脚本下载地址了。

结果也是全部正确：  
[![](https://image.3001.net/images/20210924/1632459257_614d59f91274127fd5ed5.png!small)](https://image.3001.net/images/20210924/1632459257_614d59f91274127fd5ed5.png!small)进阶脚本，可以跑多个URL：

其中脚本放在了 **挽风安全** 公众号，输入 **SpringBoot信息泄露** 就可以获取脚本下载地址了。

测试出来的结果也是全部正确。

##SRC实战  
我用这个漏洞实战了某些src，均挖掘出了敏感信息并提交至平台。上面的所有截图均为实战时候的截图，现已全部修复。

## 专属字典与PoC下载地址

关注 **Johnson666安全** 公众号，输入 **SpringBoot信息泄露** 就可以获取下载地址了。

> 参考  
>
> <https://blog.csdn.net/weixin_50464560/article/details/119778686?spm=1001.2014.3001.5501>

