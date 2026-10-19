## 一.frp工具介绍

### 1.为什么要用内网穿透

![](https://image.3001.net/images/20201117/1605612042_5fb3b20a1525e0894e02c.jpg!small)

当两个不同网络环境的机器想要互相访问的时候，这个时候外网的机器无法单方面的访问内网的机器。所以我们要借助内网穿透工具进行访问。正常使用的时候我们想要控制内网中的linux的22端口或者windows的3389端口，使用了frp会非常方便且容易。

但是frp和端口转发并不是一样的，这样的frp是使用了内网的全端口全流量的。而端口转发仅仅是做了端口的流量的转发。可以使用SocksCap或者Proxifier进行使用。

### 2.frp介绍

frp采用了go语言进行开发的。支持tcp，udp协议。可以使用http和https应用协议。是一个具有反向代理的内网穿透工具。frp可以使用socks，类似于隧道通讯。

### 3.术语解释

  1. tcp/ip：tcp/ip是一个协议簇，包含了tcp，udp，pop3，dns，icmp，frp等等协议。因为tcp和ip协议比较具有代表性，所以叫tcp/ip协议。

  2. socks4/5：socks5使用了端口和ip地址，应该是工作在网络层和传输层的产品。单纯的socks协议工作在传输层。Socks 不要求应用程序遵循特定的操作系统平台，Socks 代理与[应用层](https://baike.baidu.com/item/%E5%BA%94%E7%94%A8%E5%B1%82/4329788)代理、 HTTP 层代理不同，Socks 代理只是简单地传递数据包，而不必关心是何种应用协议（比如[FTP](https://baike.baidu.com/item/FTP/13839)、HTTP和NNTP请求）。所以，[Socks代理](https://baike.baidu.com/item/Socks%E4%BB%A3%E7%90%86/10627160)比其他应用层代理要快得多。

  3. socks4/5区别：速度不同、支持协议不同、验证du机制不zhi同。SOCKS4/5代理只是简单地传递数据包，所以SOCKS代理服务器比HTTP代理服务器速度要快得多.SOCKS5既支持TCP协议又支持UDP协议，socks4只有tcp。HTTP代理支持HTTP协议、FTP协议、TCP协议、UDP协议等多种应用协议。SOCKS4代理不支持身份验证机制、服务器端域名解析。SOCKS5代理支持各种身份验证机制、服务器端域名解析。

  4. tcp：工作在传输层。传输控制协议（TCP，Transmission Control Protocol）是为了在不可靠的互联网络上提供可靠的端到端字节流而专门设计的一个传输协议。

  5. udp：工作在传输层。UDP 是User Datagram Protocol的简称， 中文名是用户数据报协议，是[OSI](https://baike.baidu.com/item/OSI)（Open System Interconnection，[开放式系统互联](https://baike.baidu.com/item/%E5%BC%80%E6%94%BE%E5%BC%8F%E7%B3%BB%E7%BB%9F%E4%BA%92%E8%81%94/562749)） 参考模型中一种无连接的[传输层](https://baike.baidu.com/item/%E4%BC%A0%E8%BE%93%E5%B1%82)协议，提供面向事务的简单不可靠信息传送服务。

  6. http：工作在应用层，超文本传输协议。http是一个简单的请求-响应协议，它通常运行在TCP之上。它指定了客户端可能发送给服务器什么样的消息以及得到什么样的响应。请求和响应消息的头以ASCII码形式给出；而消息内容则具有一个类似MIME的格式。这个简单模型是早期Web成功的有功之臣，因为它使开发和部署非常地直截了当。

  7. 端口转发：有时被叫做隧道，是安全壳(SSH) 为网络安全通信使用的一种方法。当黑客攻击一台机器可以扫描内网其他机器，这个是时候可以把其他的机器某个端口转发到具有公网ip的机器上，然后访问公网ip即可。

  8. 端口映射：是指将一台主机的内网（LAN）IP地址映射成一个公网（WAN）IP地址，当用户访问提供映射端口主机的某个端口时，服务器将请求转移到本地局域网内部提供这种特定服务的主机；利用端口映射功能还可以将一台外网IP地址机器的多个端口映射到内网不同机器上的不同端口。

  9. 流量转发：将来往某台机器的流量转发到另外的机器上去。端口转发和隧道通信是流量转发的一种方式。

  

## 二.frp工作原理

### 1.工作原理

frp工作分为五个步骤：

![](https://image.3001.net/images/20201117/1605612056_5fb3b2180a7efe197c485.jpg!small)

### 2.配置文件

  * ssh:

    
    
    ＃ frps.ini   
    [common]   
    bind_port = 7000  
    ​  
    ＃ frpc.ini   
    [common]   
    server_addr = xxxx  
    server_port = 7000  
    ​  
    [ssh]  
    type= tcp  
    local_ip = 127.0.0.1  
    local_port = 22  
    remote_port = 6000  
    plugin = socks5

  

  * web:

    
    
    [common]  
    bind_addr = 0.0.0.0  
    bind_port = 7000  
    privilege_token = 12345678  
    ​  
    #frpc.ini  
    [common]  
    server_addr = 192.168.112.140  
    server_port = 7000  
    privilege_token = 12345678  
    ​  
    [httpname]  
    type = tcp  
    local_port = 80  
    local_ip = 127.0.0.1  
    remote_port = 8080

  

  * dns转发:

    
    
    ＃ frps.ini   
    [common]   
    bind_port = 7000  
    ​  
    # frpc.ini  
    [common]  
    server_addr = x.x.x.x  
    server_port = 7000  
    ​  
    [dns]  
    type = udp  
    local_ip = 8.8.8.8  
    local_port = 53  
    remote_port = 6000  
    plugin = socks5

  

  * 仪表盘：

    
    
    [common]  
    dashboard_port = 7500  
    dashboard_user = admin  
    dashboard_pwd = admin  
    plugin = socks5

  

## 三.使用案例

kali(192.168.112.140):

![](https://image.3001.net/images/20201117/1605612069_5fb3b225bf5837b3f4ef5.jpg!small)

ubuntu(192.168.112.141):

![](https://image.3001.net/images/20201117/1605612079_5fb3b22f4c18deff29994.jpg!small)

成功访问：

![](https://image.3001.net/images/20201117/1605612091_5fb3b23ba27b2173a7485.jpg!small)

后台界面：

![](https://image.3001.net/images/20201117/1605612100_5fb3b24400465b08207f7.jpg!small)

ubuntu上提供了web服务，将ubuntu的80端口上的web服务器转到kali的8080端口，然后访问即可。

