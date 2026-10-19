  

本文介绍有关FRP代理配置以及使用FRP建立一级代理、二级代理、三级代理

frp是一个专注于内网穿透的高性能的反向代理应用，支持TCP、UDP、HTTP、HTTPS等多种协议。可以将内网服务以安全、便捷的方式通过具有公网IP节点的中转暴露到公网。

frp的好处是利用内网或防火墙后的机器，对外网环境提供http或https服务。对于http和https服务支持基于域名的虚拟主机，支持自定义域名绑定，使多个域名可以共用一个80端口。利用处于内网或防火墙后的机器，对外网环境提供tcp和udp服务，例如在家里通过ssh或者web访问公司内网环境内的主机或者业务进行办公。

frp采用Golang编写，支持跨平台，除了二进制文件，没有额外依赖。

## 安装

下载地址： https://github.com/fatedier/frp linux_amd64/windows_amd64

解压缩下载的压缩包，将其中的frpc拷贝到内网服务所在的机器上，将frps拷贝到具有公网ip的机器上。启动命令：Windows：frpc.exe -c
frpc.ini Linux：./frpc -c ./frpc.ini . 如果需要在后台长期运行，建议结合systemd和supervisor。

frp主要由客户端（frpc）和服务端（frps）组成[ frpc.exe frpc.ini frps.exe frps.ini
]，服务端通常部署在具有公网IP的机器上，客户端通常部署在需要穿透的内网服务所在机器上。内网服务由于没有公网IP，不能被非局域网内的其他用户访问。用户通过访问服务端的frps，由frp负责根据请求的端口或其他信息将请求路由到对应的内网机器，从而实现通信。

### 代理类型

frp支持多种代理类型来适配不同的使用场景

> tcp：单纯的TCP端口映射，服务端会根据不同的端口路由到不同的内网服务。  
> udp：单纯的UDP端口映射，服务端会根据不用的端口路由到不用的内网服务。  
> http：针对HTTP应用定制了一些额外的功能，例如修改Host Header，增加鉴权。  
> https：针对HTTPS应用定制了一些额外的功能。  
> stcp：安全的TCP内网代理，需要在访问者和被访问者的机器上都部署frpc，不需要在服务端暴露端口。  
> sudp：安全的UDP内网代理，需要在被访问者和访问者的机器上都部署frpc，不需要在服务端暴露端口。  
> xtcp：点对点内网穿透代理，功能同stcp，但是流量不需要经过服务器中转。  
> tcpmux：支持服务端TCP端口的多路复用，通过同一个端口访问不同的内网服务。

## 工具使用

这里linux是公网代理，作为服务端  
windows是内网服务器，作为客户端  
在linux中解压命令：  
tar zxvf frp_0.37.0_linux_amd64.tar.gz 解压  
服务端执行：

rm -rf frpc*  
代理作为服务端删除客户端pc

1.frp服务端配置

sudo apt-get -f install 修复损坏的软件包，尝试卸载出错的包，重新安装正确版本的包  
sudo apt install vim 安装vim（如果没有vim，请安装）  
下载解压好后开始更改配置：  
bind_port 客户端连接的端口  
token 密码（最新版没找到，旧版有）  
[common]  
bind_addr = 0.0.0.0  
bind_port = 7000  
服务端配置好端口和密钥  
./frps -c frps.ini 启用服务端frp

![1](https://image.3001.net/images/20210711/1625933023_60e9c4df18dd0d56a384b.png!small)

可以配置自启动：

![2](https://image.3001.net/images/20210711/1625933024_60e9c4e03b2464f65a9b7.png!small)

vi /lib/systemd/system/frps.service #修改配置（这里没有该文件就添加个）

    
    
    [Unit]
    Description=fraps service
    After=network.target syslog.target
    Wants=network.target
    [Service]
    Type=simple
    #启动服务的命令（此处写你的 frps 的实际安装目录）
    ExecStart=/opt/frp/frps -c /opt/frp/frps.ini
    [Install]
    WantedBy=multi-user.target
    
    #启动 frpc
    systemctl daemon-reload
    systemctl start frps
    #设置为开机启动
    systemctl enable frps

![3](https://image.3001.net/images/20210711/1625933025_60e9c4e1cb7e267ab5963.png!small)

2.frp客户端配置

    
    
    # frpc.ini
    [common]
    server_addr = 192.168.253.11
    server_port = 7000
    [http_proxy]
    type = tcp
    remote_port = 7777
    plugin = socks5
    
    server_addr = 102.224.185.237 #代理服务器的IP
    server_port = 7000 #服务端服务器设置frps.ini中的端口
    token = asd #服务端服务器设置frps.ini中的密码
    [web] #服务器名（可以填写ssh、ftp等）
    type = tcp #连接协议类型
    local_ip = 127.0.0.1 #访问的ip可以是内网任何一个ip！
    local_port = 80 #本地端口（根据协议修改）
    remote_port = 6001 #远程服务器的ip端口
    
    一台Windows和一台Linux建立隧道连接
    
    server_addr = 102.224.185.237 #代理服务器的IP
    server_port = 7000 #服务端服务器设置frps.ini中的端口
    token = dayuxiyou! #服务端服务器设置frps.ini中的密码
    
    [web] #服务器名（可以填写ssh、ftp等）
    type = tcp #连接协议类型
    local_ip = 127.0.0.1 #访问的ip可以是内网任何一个ip！
    local_port = 80 #本地端口（根据协议修改）
    remote_port = 6001 #远程服务器的ip端口
    启动命令：（在目录下打开命令行）
    frpc.exe -c frpc.ini

![4](https://image.3001.net/images/20210711/1625933027_60e9c4e343a061249cf95.png!small)

![5](https://image.3001.net/images/20210711/1625933028_60e9c4e465f0353820e17.png!small)

将ip地址和端口配好，然后使用命令进行连接即可

连接成功

验证一下，win10采用了双网卡

![6](https://image.3001.net/images/20210711/1625933029_60e9c4e55927fde6d20ee.png!small)

切记设置可以远程连接

首先在子域普通用户上远程控制域控

![7](https://image.3001.net/images/20210711/1625933030_60e9c4e69e20ad0b6b704.png!small)

## 使用FRP建立一级代理

外网代理：192.168.27.157

内网web服务器：192.168.27.170 10.10.3.100

代理机器：frps.ini 文件内

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7099
    

然后在目录下执行： frps.exe -c frps.ini

![8](https://image.3001.net/images/20210711/1625933031_60e9c4e78fa841b760503.png!small)

然后到内网主机下，frpc.ini:

    
    
    \# frpc.ini
    [common]
    server_addr = 192.168.27.157
    server_port = 7099
    [http_proxy]
    type = tcp
    remote_port = 8877
    plugin = socks5
    

然后再目录下执行： frpc.exe -c frpc.ini

![9](https://image.3001.net/images/20210711/1625933032_60e9c4e8398607c5fe857.png!small)

![10](https://image.3001.net/images/20210711/1625933033_60e9c4e942b85a8d0a2af.png!small)

一级代理成功

## 使用FRP建立二级代理

外网代理：192.168.27.157

内网web服务器：192.168.27.170 10.10.3.100

域控：10.10.3.6 10.10.21.5

财务独立内网：10.10.21.2

域控不能直接连接外网代理，可以连接内网web服务器，内网web服务器可以直接连接代理，所以通过内网web服务器作为跳板，进行二级代理。首先在外网代理上启动frps服务，在内网的web服务器与域控之间建立一条frps隧道，内网web服务器启动frps，域控启动frpc服务，相互连接，建立起一条一级代理隧道，此时web服务器就作为跳板了，此时再在web服务器上打开frpc服务，与外网代理进行隧道建立，此时二级代理完成，可直接访问到域控

1\. 外网代理上 frps.ini:

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7000
    

然后执行： frps.exe -c
frps.ini![11](https://image.3001.net/images/20210711/1625933034_60e9c4ea548f1700ed573.png!small)

2\. 内网web服务器上：

（1）frps.ini:

    
    
    [common]
    bind_addr = 10.10.3.100
    bind_port = 7000
    

然后执行： frps.exe -c
frps.ini![12](https://image.3001.net/images/20210711/1625933035_60e9c4eb1bc0bf8886071.png!small)

（2）frpc.ini:

    
    
    # frpc.ini
    [common]
    server_addr = 192.168.27.157
    server_port = 7000
    [http_proxy]
    type = tcp
    local_ip = 10.10.3.100
    local_port = 1080
    remote_port = 1080
    

然后执行： frpc.exe -c
frpc.ini![13](https://image.3001.net/images/20210711/1625933035_60e9c4ebdf131de8ac16f.png!small)

3\. 在域控上 frpc.ini:

    
    
    # frpc.ini
    [common]
    server_addr = 10.10.3.100
    server_port = 7000
    [http_proxy]
    type = tcp
    remote_port = 1080
    plugin = socks5
    

然后执行： frpc.exe -c frpc.ini

![14](https://image.3001.net/images/20210711/1625933036_60e9c4ecc47ec4cc4deea.png!small)

然后对隧道连接是否成功进行检测，在其他机器上进行代理，代理测试是否成功要根据情况而定：

![15](https://image.3001.net/images/20210711/1625933037_60e9c4edccb5c51ac04cc.png!small)

当前情况通过frp隧道然后代理连接到了内网的域控机器，但是域控机器无法访问外网，所以说无法通过代理服务器访问百度，通过远程桌面连接进行验证。

![16](https://image.3001.net/images/20210711/1625933039_60e9c4ef2320743f5533e.png!small)

![17](https://image.3001.net/images/20210711/1625933040_60e9c4f07b3efc5d28ec8.png!small)

验证成功

二级代理成功

## 使用FRP建立三级代理

外网代理：192.168.27.157

内网web服务器：192.168.27.170 10.10.3.100

域控：10.10.3.6 10.10.21.5

财务独立内网机器：10.10.21.2 172.16.5.2

财务核心机器：172.16.5.5

财务核心机器不能直接连接代理，可以连接财务独立内网机器，财务独立内网机器不能直接连接代理，可以连接内网域控，内网域控不能直接连接代理，可以连接内网web服务器，内网web服务器可以直接连接外网代理，所以通过内网web服务器作为跳板，将socks代理建设在内网域控中后，将打通隧道进行横向攻击核心区机器！

首先验证财务核心机器能被远程连接

![18](https://image.3001.net/images/20210711/1625933041_60e9c4f1d05f9221ab167.png!small)

1.首先在外网代理上 frps.ini:

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7000
    

然后执行： frps.exe -c frps.ini

![19](https://image.3001.net/images/20210711/1625933042_60e9c4f2b294ca99f70dc.png!small)

2.然后在内网web服务器上：

（1）frpc.ini:

    
    
    # frpc.ini
    [common]
    server_addr = 192.168.27.157
    server_port = 7000
    [http_proxy]
    type = tcp
    local_ip = 10.10.3.100
    local_port = 9999
    remote_port = 9999
    

然后执行： frpc.exe -c
frpc.ini![20](https://image.3001.net/images/20210711/1625933043_60e9c4f38bca0c929bb90.png!small)

（2）frps.ini:

    
    
    [common]
    bind_addr = 10.10.3.100
    bind_port = 7000
    

然后执行： frps.exe -c frps.ini

![21](https://image.3001.net/images/20210711/1625933044_60e9c4f47f7d4b9e6cb55.png!small)

3.在子域控制器执行：

（1）frpc.ini:

    
    
    # frpc.ini
    [common]
    server_addr = 10.10.3.100
    server_port = 7000
    [http_proxy]
    type = tcp
    local_ip = 10.10.21.5
    local_port = 9999
    remote_port = 9999
    

然后执行： frpc.exe -c frpc.ini

![22](https://image.3001.net/images/20210711/1625933045_60e9c4f553550c637e26d.png!small)

（2）frps.ini:

    
    
    [common]
    bind_addr = 10.10.21.5
    bind_port = 7000
    

然后执行： frps.exe -c frps.ini

![23](https://image.3001.net/images/20210711/1625933046_60e9c4f62e4c8e5736f84.png!small)

4.最后在财务部独立域 frpc.ini:

    
    
    frpc.ini:
    # frpc.ini
    [common]
    server_addr = 10.10.21.5
    server_port = 7000
    [http_proxy]
    type = tcp
    remote_port = 9999
    plugin = socks5
    

然后执行： frpc.exe -c frpc.ini

![24](https://image.3001.net/images/20210711/1625933047_60e9c4f7055eaef6449e4.png!small)

然后开始验证三级代理是否建立成功，首先尝试代理并测试：

![25](https://image.3001.net/images/20210711/1625933048_60e9c4f821d90a7c9da18.png!small)

可能是因为代理服务器并不出网，处在内网环境的原因，所以直接尝试远程桌面连接：

![26](https://image.3001.net/images/20210711/1625933049_60e9c4f99046a16d9fc4f.png!small)

![27](https://image.3001.net/images/20210711/1625933050_60e9c4facd5db9496c008.png!small)

测试通过，代理成功

## 总结

使用frp有很多优势：

> 1.利用处于内网或防火墙后的机器，对外网环境提供HTTP或HTTPS服务。
>
> 2.对于HTTP、HTTPS服务支持基于域名的虚拟主机，支持自定义域名绑定，使多个域名可以共用一个80端口。
>
> 3.利用处于内网或防火墙后的机器，对外网环境提供TCP和UDP服务，例如在家里通过SSH访问处于公司内网环境的主机

对于其它穿透隧道工具的不足：

> 1.Earthworm不能过杀软，秒杀
>
> 2.Tunnel非常不稳定，web都动不动就崩溃，更别说支持3389
>
> 3.ptunnel环境在内网多限制情况不可利用，局限性大
>
> 4.DNS隧道穿透，适合僵尸网络

