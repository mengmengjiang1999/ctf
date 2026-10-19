## 前言

前面已经出了三篇关于内网渗透方面的文章，今天就接着来看看在内网中经常会使用的一个工具Responder。在这边文章中你可以学到Responder的原理，作用以及其综合利用。这也是内网渗透的第四篇文章，前三篇如下，大家有兴趣可以前去看看。

[内网渗透：Kerberos认证协议安全性分析](https://www.freebuf.com/articles/network/371028.html)

[内网横移：抓取域管理员密码](https://www.freebuf.com/articles/web/370338.html)

[内网渗透：详解kerberoast攻击](https://www.freebuf.com/articles/network/371446.html)

另外，我在freebug的知识大陆建立了一个帮会，免费加入，会不断更新相关的文章，欢迎大家加入帮会，共同探讨。

帮会名称：安全防线

## Responder简介

Responder在内网渗透中会经常看到它的身影，是常用的一个工具。 **Responder通过协议欺骗和模拟服务这两个功能来获取到目标的Net-NTLM
hash，进而可能得到系统的控制权限。**

## Responder原理

客户端/目标 **无法通过DNS域名解析** ，则会回退到LLMNR（在Windows Vista中引入）和NBT-NS进行解析。如果我们的Responder在运行着，那么我们将 **对所有我们能看到的LLMNR和NBT-NS请求响应“yeah,
就是我”，然后所有的传输都将被引导到我们这。**

如下图所以，在DNS解析失败以后，会使用其它的协议进行解析主机名或域名：

![1689085719_64ad6717142d4d761b5f6.png!small?1689085718809](https://image.3001.net/images/20230711/1689085719_64ad6717142d4d761b5f6.png!small?1689085718809)

上面就是Responder进行协议欺骗的原理。 **Responder主要就是两个作用，就是协议欺骗和模拟服务。**

协议欺骗：通过回到协议的广播包，进行欺骗，进而冒充别的主机，将流量转到欺骗主机。利用的协议有下面的三种LLMNR、NBNS、MDNS。

模拟服务：Responder会模拟出一些常见的服务，与其交互，获取到秘钥等信息

  

**首先要明白Responder工具使用的也是欺骗的一种，跟传统的arp欺骗在原理上也是相同的，就是收到广播包时进行回复，这样就会将请求转移到我们设置的主机上。**

同时，这种方式与arp欺骗也有所不同，是由于它使用的协议是LLMNR、NBNS、MDNS。这三种协议与DNS协议类似，都是根据主机名或者域名来解析为IP地址，但是
**这三种协议是在DNS无法解析以后才会生效** 。那么，这就产生了一个问题，那就是如何让DNS不生效，进而使用这种协议，达到欺骗的效果。

可以使用下面的方式

 **1）访问不存在的服务，如SMB，http等**

net use \\\winsssss\

 **2）ping一个不存在的域名或者主机名**

上面只是说了最简单的两种，当然还有其它的方式。

### 知识点

    
    
    win域内进行解析主机名或者域名的顺序  
    1.查看本地hosts文件
    2.查找DNS缓存，windows可使用命令 ipconfig/displaydns 查看
    3.DNS服务器
    4.尝试LLMNR、NBNS和MDNS协议进行解析

### 三种协议的介绍

 **LLMNR**

链路本地多播名称解析（LLMNR）是一个基于域名系统（DNS）数据包格式的协议，IPv4和IPv6的主机可以通过此协议对同一本地链路上的主机执行名称解析。
**Windows 操作系统从 Windows Vista开始就内嵌支持，Linux系统也通过systemd实现了此协议。它通过UDP
5355端口进行通信，且LLMNR支持IPV6。**

 **NBNS**

网络基本输入/输出系统(NetBIOS) 名称服务器(NBNS) 协议是 TCP/IP 上的 NetBIOS (NetBT) 协议族的一部分，它在基于
NetBIOS 名称访问的网络上提供主机名和地址映射方法。通过UDP 137端口进行通信，但NBNS不支持IPV6。

 **mdns（局域网中的DNS）**

mdns 即多播dns（Multicast
DNS），mDNS主要实现了在没有传统DNS服务器的情况下使局域网内的主机实现相互发现和通信，遵从dns协议，使用现有的DNS信息结构、名语法和资源记录类型。并且没有指定新的操作代码或响应代码。

在计算机网络中 ， 多播DNS （ mDNS ）协议将主机名解析为不包含本地名称服务器的小型网络中的IP地址。 它是一种零配置服务，使用与单播域名系统
（DNS）基本相同的编程接口，数据包格式和操作语义。 虽然Stuart
Cheshire将mDNS设计为独立协议，但它可以与标准DNS服务器协同工作。它通过UDP 5353端口进行通信，且MDNS也支持IPV6。

## Responder的作用

了解了Responder的工作原理，那么该工具最终可以帮助我们拿到什么？

我们的目标当然是获取机器的登录凭证。我们知道在内网中认证时不会发送用户名和明文密码的，是通过发送Net-NTLM hash来进行认证的。
**那么Responder的目的就是获取到用户的Net-NTLM hash(Net-NTLM Hash用于网络身份认证（例如NTLM认证）)。**

Net-NTLM hash目前存在两个版本，分别是 **Net-NTLMv1和Net-NTLM v2。**

NTLM v2相对于NTLMV1更加的安全，无法通过NTLM v2还原出用户的ntlm
hash，而NTLMv1由于其脆弱性，在控制Challenge后可以在短时间内通过彩虹表还原出用户的ntlm hash。由于这种原因，NTLM
v2不能直接应用于Pass The Hash攻击，只能通过暴力破解来获取明文密码。而攻击者获取NTLMv1 hash后，可以直接还原出NTLM
HASH，这样的话就可以将NTLM HASH直接用于Pass The Hash攻击，相较于NTLM v2还需要破解才能利用更加不安全。

 **NTLMV1可以通过下面的工具或者网站进行破解**

NTLMv1还原工具： <https://github.com/eladshamir/Internal-Monologue>

访问网站[https://crack.sh/get-cracking/，使用免费的彩虹表进行破解](https://crack.sh/get-cracking/%EF%BC%8C%E4%BD%BF%E7%94%A8%E5%85%8D%E8%B4%B9%E7%9A%84%E5%BD%A9%E8%99%B9%E8%A1%A8%E8%BF%9B%E8%A1%8C%E7%A0%B4%E8%A7%A3)

