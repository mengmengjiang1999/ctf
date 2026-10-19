# linux终端流量走代理的方法

边界打点完进内网渗透，由于网络原因我们不得不搭建隧道与进行内网通信，而我们的攻击机需要与内网通信此时就需要代理让流量走隧道进入内网，从而进一步的渗透。

## Socks5和HTTP代理的区别

Socks5代理：SOCKS代理只是简单地传递数据包，没有应用协议限制，也可以是HTTP请求，因此SOCKS代理服务器比其他类型的代理服务器更快。

 **Tips：**

 **Socks5代理** 只是Socks代理的其中一种，Socks代理包括 **Socks4、Socks5**
。Socks4代理仅支持TCP协议而Socks5代理支持TCP协议、UDP协议同时还支持各种身份验证机制、服务器端域名解析。

 **HTTP代理** ：可以支持代理的主机进行HTTP访问，主要用于浏览器代理访问网页，主要端口为80、8080。

### Socks5代理

Scoks5默认的通信端口是`1080`

    
    
    socks5://127.0.0.1:1080
    

### HTTP代理

HTTP代理则和Socks5不同

    
    
    http://127.0.0.1:1081
    

这里的端口按照实际代理客户端端口填。如果内网渗透走隧道的话按照实际配置的隧道通信的端口填写。

## 配置代理

### 临时代理

打开终端输入命令

#### http

    
    
    export http_proxy=http://localhost:port
    

#### https

    
    
    export https_proxy=http://localhost:port
    

#### Socks5

    
    
    export http_proxy=socks5://localhost:port
    export https_proxy=socks5://localhost:port
    

当然也可以直接设置全部

    
    
    export ALL_PROXY=socks5://localhost:port
    

### 永久代理

需要在shell配置文件中写入代理地址`~/.bashrc`或者`~/.zshrc`。

#### HTTP,HTTPS

    
    
    export http_proxy="http://localhost:port"
    export https_proxy="http://localhost:port"
    

#### Socks5

    
    
    export http_proxy="socks5://localhost:port"
    export https_proxy="socks5://localhost:port"
    

**or**

    
    
    export ALL_PROXY="socks5://localhost:port"
    

