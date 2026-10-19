![](https://image.3001.net/images/20210317/1615960761_60519ab93f6ba5a855b5f.png!small)

## 关于Chameleon

Chameleon是一个支持自定义开发的蜜罐系统，可以帮助广大研究人员监控网络流量、Bots活动和用户密码凭证，支持的协议和组件有DNS、HTP
Proxy、HTTP、HTTPS、SSH、POP3、IMAP、STMP、RDP、VNC、SMB、SOCKS5、Redis、TELNET、Postgres和MySQL。

## 功能介绍

> 模块化方法（蜜罐作为脚本运行或作为对象导入）。
>
> 大多数蜜罐都用作服务器（只有少数蜜罐模拟应用层协议）。
>
> 使用用户名、密码和Banner设置服务器（默认用户名和密码为test）。
>
> 对ICMP、DNS-TCP和UDPPayload载进行解析，并根据常见模式进行检查。
>
> 提供了用于监视结果的可视化Grafana接口（按IP过滤-默认为全部）。
>
> 支持解析非结构化和结构化日志，并插入至Postgres中。
>
> 所有蜜罐都包含用于测试服务器的客户端。
>
> 默认情况下会打开并监视所有端口。
>
> 易于自动化，可部署在AWSEC2上.
>
> 更多功能可供探索...

## 工具运行要求（仅服务器）

    
    
    apt-get update -y && apt-get install -y iptables-persistent tcpdump nmap iputils-ping python python-pip python-psycopg2 lsof psmisc dnsutils
    
    pip install scapy==2.4.4 netifaces==0.10.9 pyftpdlib==1.5.6 sqlalchemy==1.3.23 pyyaml==5.4.1 paramiko==2.7.1 impacket==0.9.22 twisted==20.3.0 psutil==5.8.0 requests==2.25.1 redis==3.5.3 mysql-connector-python==8.0.23 pygments==2.5.2
    
    pip install -U requests[socks]
    
    pip install -Iv rsa==4.0
    
    pip install rdpy==1.3.2

## 工具安装和运行

### Ubuntu 18或19系统（自动配置）

    
    
    git clone https://github.com/qeeqbox/chameleon.git
    
    cd chameleon
    
    chmod +x ./run.sh
    
    ./run.sh auto_configure

Grafana接口（http://localhost:3000）将会在工具安装完成之后自动打开，用户名为“changeme457f6460cb287”，密码为“changemed23b8cc6a20e0”。如果你没有看到Chameleon仪表盘的话，请点击左侧边栏的搜索图标，然后手动添加即可。

等待几分钟之后，蜜罐将显示IP地址：

    
    
    ...
    
    honeypot_1  | Your IP: 172.19.0.3
    
    honeypot_1  | Your MAC: 09:45:aa:23:10:03
    
    ...

接下来，你就可以在本地系统中与蜜罐系统交互了：

    
    
    ping 172.19.0.3
    
    or run any network tool against it
    
    nmap 172.19.0.3

### Ubuntu 18或19系统（自动配置-测试）

    
    
    git clone https://github.com/qeeqbox/chameleon.git
    
    cd chameleon
    
    chmod +x ./run.sh
    
    ./run.sh auto_configure_test

Grafana接口（http://localhost:3000）将会在工具安装完成之后自动打开，用户名为“admin”，密码为“admin”。如果你没有看到Chameleon仪表盘的话，请点击左侧边栏的搜索图标，然后手动添加即可。

将所需的非阻塞服务器作为对象导入（SSH服务器）

    
    
    copy ssh_server.py to your folder
    
    
    # ip= String E.g. 0.0.0.0
    
    # port= Int E.g. 9999
    
    # username= String E.g. Test
    
    # password= String E.g. Test
    
    # mocking= Boolean or String E.g OpenSSH 7.0
    
    # logs= String E.g db, terminal or all
    
    # --------------------------------------------------------------------    
    # always remember to add process=true to run_server() for non-blocking
    
    
    from ssh_server import QSSHServer
    
    qsshserver = QSSHServer(port=9999)
    
    qsshserver.run_server(process=True)
    
    qsshserver.test_server(port=9999)
    
    qsshserver.kill_server()
    
    
    ssh test@127.0.0.1
    
    
    INFO:chameleonlogger:['servers', {'status': 'success', 'username': 'test', 'ip': '127.0.0.1', 'server': 'ssh_server', 'action': 'login', 'password': 'test', 'port': 38696}]

## Docker单独使用

    
    
    git clone https://github.com/qeeqbox/chameleon.git
    
    cd chameleon
    
    # choose which honeypot http, https, ssh etc and use -p in docker for the ports
    
    docker build -t honeypot ./honeypot/. && docker run -p 9999:9999 -p 9998:9998 -it honeypot --mode normal --servers "ssh:9999 http:9998"

 **如果你没有看到Chameleon仪表盘的话，请点击左侧边栏的搜索图标，然后手动添加即可。**

![](https://image.3001.net/images/20210317/1615960837_60519b05ee6c78039eae0.png!small)

## 当前服务器/模拟器

    
    
    DNS（服务器使用Twisted）
    
    HTTPProxy（服务器使用Twisted）
    
    HTTP（服务器使用Twisted）
    
    HTTPS（服务器使用Twisted）
    
    SSH（服务器使用socket）
    
    POP3（服务器使用Twisted）
    
    IMAP（服务器使用Twisted）
    
    STMP（服务器使用smtpd）
    
    RDP（服务器使用Twisted）
    
    SMB（服务器使用impacket）
    
    SOCK5（服务器使用socketserver）
    
    TELNET（服务器使用Twisted）
    
    VNC（模拟器使用Twisted）
    
    Postgres（模拟器使用Twisted）
    
    Redis（模拟器使用Twisted）
    
    Mysql（模拟器使用Twisted）
    
    Elasticsearch（即将上线..）
    
    Oracle（即将上线..）
    
    ldap（即将上线..）

## 工具使用

 **Grafana接口：**

**![](https://image.3001.net/images/20210317/1615960859_60519b1b4d4ba79ac2a57.png!small)**

 **Nmap扫描：**

**![](https://image.3001.net/images/20210317/1615960867_60519b23e928f97857381.png!small)**

 **用户凭证监控：**

![](https://image.3001.net/images/20210317/1615960875_60519b2be08c9216ec9a0.png!small)

## 项目地址

Chameleon：【[ _GitHub传送门_](https://github.com/qeeqbox/chameleon)】

## 参考资料

[
_https://github.com/qeeqbox/chameleon/pull/1﻿_](https://github.com/qeeqbox/chameleon/pull/1)

