## DNS隧道

**DNS协议又称域名系统是互联网的基础设施，只要上网就会用到，因而DNS协议是提供网络服务的重要协议，在黑客进入内网后会使用DNS、ICMP、HTTP等协议隧道隐藏通信流量。本文通过DNS隧道实验并对流量进行分析，识别DNS隧道流量特征。**

##  实验环境

> CentOS Linux 两台

##  创建DNS服务器

###  1.安装bind

> yum install bind*

###  2.配置named文件

> 修改/etc/named.conf

将下图中选中的地方改为any

![](https://image.3001.net/images/20190922/1569146633_5d874709c6d25.png!small)

###  3\. 设置NS记录，A记录

增加区域解析文件在/etc/named.rfc1912.zones增加区域解析记录文件

![](https://image.3001.net/images/20190922/1569146676_5d8747341bd57.png!small)

增加正向解析记录

将/var/named/named.localhost改为上图中修改的名字

> cp /var/named/named.localhost/var/named/name.dnstunel

修改文件如下

添加NS记录，A记录

![](https://image.3001.net/images/20190922/1569146697_5d87474959091.png!small)

添加bind为自启动服务

> systemctl enablenamed.service
>
> systemctl restartnamed.service

查看启动状态

> systemctl statusnamed.service

![](https://image.3001.net/images/20190922/1569146764_5d87478c682a8.png!small)

将另一台主机DNS服务器设置为192.168.1.7，ping
ns.dnstuneltest.com是否正确解析，(如果不能解析，可能跟防火墙有关系，在DNS服务器上执行iptables -F)

##  Iodine

Ionine支持两种模式，中继以及直连模式，服务器与客户端可以直接通信而不需要第三种辅助软件，通信的DNS数据损坏容易容易被发现。

###  安装

下载地址：

> <https://github.com/yarrick/iodine/archive/master.zip>

unzip 解压

cd iodine-master

make

出现报错

![](https://image.3001.net/images/20190922/1569146786_5d8747a29613c.png!small)

yum -y install zlib-devel

make;make install

安装完成

进入 bin

iodined 服务器

iodine 客户端

###  实验测试

**服务器**

> ./iodined -f -c -P 123456 10.1.0.1ns.dnstuneltest.com
>
> -f 前台显示，运行后一直在命令行等待
>
> -c 中继模式|直连模式
>
> -P 认证密码

Ip 虚拟出网卡的IP，在隧道建立后，客户端同样会多出一块dns0网卡，与该IP在 同一网段，可以任意设置，虚拟IP。

设置的域名，这里要跟区域配置文件一致。

输入完成之后，ifconfig查看会多一块网卡

![](https://image.3001.net/images/20190922/1569146826_5d8747ca4baf2.png!small)

![](https://image.3001.net/images/20190922/1569146836_5d8747d4634f0.png!small)

**客户端**

> ./iodine -f -P 123456 192.168.1.7 ns.dnstuneltest.com
>
> -f 前台显示
>
> -P 认证密码
>
> IP 为配置DNS服务器IP或者为购买的云服务IP，输入此选项之后，直接与指定IP查询，而不经过其他DNS服务器层解析

客户端此时也会新增一个网卡，DNS0，IP为10.1.0.2与服务器DNS0网卡处于同一网段中，此时服务器端与客户端可以使用这两个IP互相通信。

![](https://image.3001.net/images/20190922/1569146926_5d87482ed5393.png!small)

###  流量包分析

> 抓包
>
> tcpdump -i enp2s0 port 53 -w /tmp/iodine.pcap

##  建立链接的包分析

在客户端启动后，会向服务器发送DNS请求包

![](https://image.3001.net/images/20190922/1569146944_5d8748407376c.png!small)

客户端情报求包，请求包的type类型为10 (未知，可以作为检测的一种特征)，数据作为域名前缀

yrbh1o.ns.dnstuneltest.com, yrbh1o就是请求的数据

![](https://image.3001.net/images/20190922/1569146956_5d87484c51cde.png!small)

服务器响应包，rdata字段携带数据，因为查询包没有指定查询类型，所以rdata字段没有长度限制(限制于UDP最大包长512字节)

![](https://image.3001.net/images/20190922/1569146995_5d87487333165.png!small)

采用中继模式，客户端会一直发送心跳包，保持链接（因为DNS服务器不会直接与客户端发起链接，所以客户端会一直想服务器发送数据包）但是DNS协议的字段格式已经损坏。

##  通信流量包分析

通信过程的中的DNS协议格式已经损坏，wireshark已经无法正确分析

![](https://image.3001.net/images/20190922/1569147012_5d874884b3e79.png!small)

正常DNS的数据包中的query字段的形式是所占字节-三级域名-所占字节-二级域名-所占字节-一级域名形式并且正常的query字段时只有再域名结束时才会出现00阶段。

05fanyi05baidu03com

![](https://image.3001.net/images/20190922/1569147039_5d87489f2f448.png!small)

隧道中的流量明显不符合上文的query字段规定。由60 08开头。

![](https://image.3001.net/images/20190922/1569147062_5d8748b6705ac.png!small)

##  suricata检测规则(并未测试，仅共参考)

    
    
    UDP payload协议偏移40个字节处是否为00 0a并且频率达到5秒3次以上。
    
        alert udp $HOME_NET any -> any 53 (msg:"dnstunnel-iodine-connect";content: "|00 0a|";offset:40;depth:4;threshold: type limit, track by_src, count 3, seconds 5;classtype:dns;sid:2010000; rev:1;)
    
        通信包，query字段60 08开头，并且后面跟的不是59个字母或者数字的组合，或者后面的字母不存在\x00同时频率在60s一百次以上。
    
         alert udp $HOME_NET any -> any 53 (msg:"dnstunnel-iodine-traffic";dsize > 100;content:"|6008|";offset:12;pcre:
    
        !"/[\x60\x08][a-zA-Z0-9]{59}/";threshold: type limit,track by_src, count 100, seconds 60;classtype:dns; sid:2010001; rev:1;)
    
        alert udp $HOME_NET any -> any 53 (msg:"dnstunnel-iodine-traffic";dsize > 100;content:"|6008|";offset:12;content:"|00|";depth:
    
        59;threshold: type limit, track by_src, count 100, seconds60;classtype:
    
        dns; sid:2010002; rev:1;)

##  Dns2tcp

###  安装

需要与其他回连工具配合，或者写入反弹shell

下载链接

> 链接：<https://pan.baidu.com/s/14SIxdiIWHKZDUz6lgn_Zag>

提取码：t1rw

安装编译

    
    
    ./configure
    
        make;make install

服务器端

    
    
    server/dns2tcpd

客户端

    
    
    Linux:
    
        client/dns2tcpc
    
         windows:

云盘直接下载windows版本，或者下载

    
    
    dns2tcpc.exe

###  实验测试

**服务器端**

1.创建配置文件

    
    
    Vim/etc/dns2.conf
    
        Listen  = 192.168.1.6（Linux服务器的IP,服务器的IP） 
    
        port   = 53         (监听本机的端口)
    
        user   =nobody     
    
        chroot  = /tmp       
    
        domain =.ns.dnstuneltest.com（上面配置NS记录的域名） 
    
        resources =ssh:127.0.0.1:22,socks:127.0.0.1:1082,http:127.0.0.1:3128(设置本地监听的服务资源，根据自身服务开启的资源设置)

2.启动

    
    
    ./dns2tcpd -f/etc/dns2.conf

启动之后会将DNS的隧道流量根据客户端选择的资源使用对应的服务建立连接

出现如下错误需要关闭服务器自带的dns解析服务

![](https://image.3001.net/images/20190922/1569147189_5d874935af0c1.png!small)

**客户端**

> dns2tcpc -r ssh-z ns.dnstuneltest.com 192.168.1.6 -l 8888 -d 2
>
> r:指定对应的资源，前面服务器需开启指定的资源
>
> -z:自定解析的dns域名，如果域名已经添加的公网的DNS解析则可以省略后面的IP
>
> -l:端口
>
> -d:是否为调试模式 2 等级可以省略

![](https://image.3001.net/images/20190922/1569147208_5d874948a6625.png!small)

客户端使用访问服务器

![](https://image.3001.net/images/20190922/1569147224_5d874958c053f.png!small)

###  流量包分析

建立链接并未产生通信包

![](https://image.3001.net/images/20190922/1569147245_5d87496daba47.png!small)

使用ssh访问时，才会产生数据包

![](https://image.3001.net/images/20190922/1569147256_5d8749783700a.png!small)

数据包分析

需要时客户端会向服务端发起TXT类型请求，服务器的返回包也会放在回复的TXT记录中

![](https://image.3001.net/images/20190922/1569147272_5d874988d0bef.png!small)

![](https://image.3001.net/images/20190922/1569147287_5d874997e61f1.png!small)

客户端通过TXT类型记录的域名前缀来发出数据，通过DNS
RR中的TXT记录来附加回应的内容。域名前缀和回应内容均采用base64编码，如果提取单条数据，进行base64解码，即可看到传输的内容。从发包行为上可以发现，如果在进行传输数据这种大量数据交互操作的情况，dns2tcp会将数据切分成若干个小单元，依次发出，时间间隔非常小，而当无数据交互，空闲时，两端仍然通过发包维持通信状态。

##  Suricata规则检测(并未测试，仅共参考)

因为Dns2tcp采用的是标准的dns协议格式，所以只能通过发包的频率检测

    
    
    alert udp $HOME_NET any -> any 53(msg:"dns tunnel-dns2tcp";content: "|0010|";offset:40;depth:4; threshold: type limit, track by_src, count 150,seconds 10;classtype:dns; sid:2010003; rev:1;)

结尾

小白水文，求大神放过

pcap包下载地址：

> 链接：<https://pan.baidu.com/s/1R9IhfxI285QMLGwjh_gQVw>

提取码：n5ha

***本文原创作者：johylodog，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

