# 前言

构建零信任网络，自然离不开网络准入(NAC)，这就涉及到交换机的一些安全测试，于是有了此文《从交换机安全配置看常见局域网攻击》。

# 交换机安全配置

如本文标题所说从交换机安全配置看常见的局域网攻击，那么下面提到的各种攻击方式，自然是建立在交换机安全配置之上来说的。我们通过h3c官方提供的《H3C
交换机安全加固手册》和《安全配置指导》，从这两份手册可以看出交换机支持的安全配置非常多，基本已经覆盖了各种我们熟知局域网攻击。下面就挑几个典型的攻击方式进行演示。

![](https://image.3001.net/images/20220107/1641546851_61d80463a087da5be9f9a.png!small)

# arp欺骗

### 原理

在每台主机都有一个ARP缓存表，缓存表中记录了IP地址与MAC地址的对应关系，而局域网数据传输依靠的是MAC地址。ARP缓存表机制存在一个缺陷，就是当请求主机收到ARP应答包后，不会去验证自己是否向对方主机发送过ARP请求包，就直接把这个返回包中的IP地址与MAC地址的对应关系保存进ARP缓存表中，如果原有相同IP对应关系，原有的则会被替换。

那么攻击者就可以发送恶意广播消息，告诉目标我是某某主机，毒化目标主机arp缓存表，这就是arp欺骗。

### 工具

> arpspoof
>
> Ettercap
>
> bettercap

arp攻击主要有如下两种场景：

> arp断网攻击，主要原理是：毒化目标主机arp缓存表，欺骗网关地址；
>
> 中间人嗅探，主要原理是：目标主机和网关双向欺骗，需配合路由转发功能。

### 攻击演示

这里，我们采用bettercap进行arp攻击演示。

攻击者：192.168.6.3

目标：192.168.6.5

1.启动bettercap，如果机器有多网卡需指定对应网卡，http-ui根据个人喜好决定是否开启。具体命令如下所示：

    
    
    sudo ./bettercap -caplet http-ui -iface en0

如下显示即为成功

![](https://image.3001.net/images/20220107/1641547041_61d8052172e206488c68a.png!small)

账号密码在http-ui.cap里面可以找到![](https://image.3001.net/images/20220107/1641547070_61d8053e5f82b7be34f2b.png!small)

2.主机探测：

进入LAN选项卡，开始进行主机探测。

![](https://image.3001.net/images/20220107/1641547124_61d80574096ea1c3420dc.png!small)

也可以直接在终端输入命令开启，如下![](https://image.3001.net/images/20220107/1641547150_61d8058ec3c25ad976661.png!small)

3.配置开启arp欺骗

进入Advanced选项卡开始进行arp欺骗，如下所示。

![](https://image.3001.net/images/20220107/1641547179_61d805ab8645924e3def6.png!small)

默认会欺骗整个局域网主机，我们按需进行配置，配置目标ip，把fullduplex一起打开可以欺骗还可以网关(双向)。

![](https://image.3001.net/images/20220107/1641547200_61d805c09401a18767c79.png!small)

然后回来LAN选项卡，可以看着这个小图标即为配置成功。

![](https://image.3001.net/images/20220107/1641547219_61d805d3e49f53b6405c0.png!small)

最后再来看下效果

![](https://image.3001.net/images/20220107/1641547239_61d805e756c71359a00e7.png!small)

如上可以看到攻击成功的效果，目标机器arp表里面网关mac被改成了攻击者的mac。

再看看交换机的路由表也一样如此。

![](https://image.3001.net/images/20220107/1641547350_61d806569bd985221f2cd.png!small)

wireshark抓包结果如下，一目了然。

如不了解arp包的详细分析请看<https://blog.csdn.net/yangshihuz/article/details/103866507>

![](https://image.3001.net/images/20220107/1641547367_61d8066712629e43c6f4d.png!small)

## arp欺骗防御

接下来我们再来看看交换机如何防护这种攻击。

通过翻官方手册，找到如下这条：

![](https://image.3001.net/images/20220107/1641547429_61d806a59d0a3037cc034.png!small)

进行简单配置后，达到了预期效果。

    
    
    system-view  
    arp check enable  
    arp user-ip-conflict record enable

![](https://image.3001.net/images/20220107/1641547450_61d806baa6dd6fa99fa06.png!small)

为了更全面的防御各种ARP攻击，最后整理出如下配置：

    
    
    system-view  
    arp check enable  
    # arp spoof  
    arp user-ip-conflict record enable  
    # arp flood  
    arp source-suppression enable  
    arp source-suppression limit 100  
    arp resolving-route enable  
    arp resolving-route probe-count 5  
    arp resolving-route probe-interval 3  
    arp valid-check enable  
    arp active-ack enable

# dns欺骗

### 原理

需要和ARP欺骗配合使用，当ARP欺骗成功后，嗅探到对方发出的DNS请求数据包，分析数据包取得ID和端口号后，向目标发送自己构造好的一个DNS返回包，对方收到DNS应答包后，发现ID和端口号全部正确，即把返回数据包中的域名和对应的IP地址保存进DNS缓存表中，而后来的当真实的DNS应答包返回时则被丢弃。

### 工具

> Ettercap
>
> bettercap

dns欺骗主要用途就是用来钓鱼。

### 攻击演示

我们还是用bettercap进行演示：

> 配置并启用arp欺骗。
>
> 配置dns欺骗

此处为了方便演示，我们起了一台kali当web服务器，待会儿dns欺骗会用到。

![](https://image.3001.net/images/20220107/1641547500_61d806ec7e38f4a7ae030.png!small)

再配置dns欺骗，此处用博客进行演示，让域名解析到192.168.6.3上，也是就之前配置好的kali。![](https://image.3001.net/images/20220107/1641547531_61d8070babc6b9e7cb50d.png!small)

然后我们在被欺骗的主机上主动发起dns查询，可以看到符合我们的预期。![](https://image.3001.net/images/20220107/1641547552_61d807207849c5c3b659b.png!small)

我们再用wireshark筛选一下结果如下，可以看到成功伪造了dns应答包。![](https://image.3001.net/images/20220107/1641547574_61d807366810b01471779.png!small)

Bettercap更多模块使用，请直接查看官方文档。

<https://www.bettercap.org/modules/>

关于arp攻击最常见的就是上面演示的两种，除此之外还有一些攻击如arp泛洪之类的，由于操作比较简单，这里不做演示。可用下面工具进行测试：

<https://github.com/davidgfnet/net-tools>

<https://github.com/EmreOvunc/ARP-Poisoning-Tool>

# DHCP Flood

### 原理

攻击源发送大量DHCP请求报文给DHCP服务器，占用DHCP服务器大量的CPU资源并耗尽DHCP服务器上的地址空间，使合法的DHCP客户端无法获取到IP地址。

### 工具

这里主要采用yersinia进行演示：

> <https://github.com/kamorin/DHCPig>
>
> <https://github.com/tomac/yersinia>

### yersinia介绍

yersinia是一款针对交换机二层网络的攻击工具，功能包括：

支持针对以下网络协议的攻击：

> 生成树协议 (STP)
>
> 思科发现协议 (CDP)
>
> 动态中继协议 (DTP)
>
> 动态主机配置协议 (DHCP)
>
> 热备路由器协议 (HSRP)
>
> 802.1q
>
> 802.1x
>
> 交换机间链路协议 (ISL)
>
> VLAN 中继协议 (VTP)

### 攻击演示

1.以图形化界面方式启动

    
    
    yersinia -G

![](https://image.3001.net/images/20220107/1641547729_61d807d1d9ea2cf563e1a.png!small)

2.配置并启动dhcp攻击

开始前，先看看dhcp的ip使用情况，可以看到一切正常。![](https://image.3001.net/images/20220107/1641547753_61d807e99f6263783be2a.png!small)

回到kali开始配置，切换到DHCP选项卡，可以看到支持四种模式，我们只需要选择支持dos的就可以发起DHCP Flood攻击。

![](https://image.3001.net/images/20220107/1641547794_61d808128a1d26607acfb.png!small)

kali发起攻击后，到交换机再看ip池的使用，如下图可以看到已经使用了很多ip。这种攻击主要是把dhcp的ip池占满，那么别的客户端就不能正常获取ip了。![](https://image.3001.net/images/20220107/1641547814_61d80826986a4ad200a58.png!small)

### DHCP攻击防御

    
    
    # 配置DHCP Flood攻击检测最大报文数为2，检测时间为9000毫秒  
    dhcp flood-protection threshold 2 9000  
    # 配置DHCP Flood攻击表项老化时间为90秒  
    dhcp flood-protection aging-time 90  
    # 配置DHCP Snooping

# 最后

这些xp时代的技术放到今天已经不好用了，在实战中也基本不会用上这些攻击方式，只能说时代变了。

# References

> <https://support.huawei.com/enterprise/zh/doc/EDOC1100038449?section=k005>
>
> <https://www.bettercap.org/modules/>
>
>
> <https://www.h3c.com/cn/Service/Document_Software/Document_Center/Home/Switches/00-Public/Maintenance/Security_Hardening/H3C_SH(Comware_V7)-6W100/#_Toc12365358>
>
>
> <https://www.h3c.com/cn/Service/Document_Software/Document_Center/Home/Switches/00-Public/Configure/Operation_Manual/H3C_CG-R63xx/>
>
> <https://www.cisco.com/c/en/us/support/docs/ip/access-lists/13608-21.html>
>
>
> [http://www.h3c.com/cn/d_201812/1142011_30005_0.htm#_Toc533427456﻿](http://www.h3c.com/cn/d_201812/1142011_30005_0.htm#_Toc533427456)
>
>
> [https://www.cnblogs.com/swyft/articles/5557365.html﻿](https://www.cnblogs.com/swyft/articles/5557365.html)

