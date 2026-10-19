前一篇文章中谈到了内网中的端口转发和反弹shell的几种常见方法。获得shell之后，我们就要查看一下自己的权限，权限足高，我们就开始内网攻击。权限不够，就要想办法提权。今天这篇文章，我们就开始介绍内网攻击的常用手法。

首先，我们来介绍一下中间人攻击。中间人攻击（Man-in-the-Middle Attack,
MITM）是一种“间接”入侵手法。所谓“中间人攻击”会通过拦截正常网络通信收据，并对拦截的数据进行篡改和嗅探。常用的中间人攻击手法有欺骗，监听嗅探，会话劫持等。

## DNS欺骗

Ettercap是一款强大的中间人攻击工具。可用于DNS欺骗，ARP欺骗，监听嗅探，会话劫持等常见的中间人攻击。KALI中就整合了该工具。背景知识不再多言，今天我们先简单介绍一下，如何在ettercap辅助下进行DNS欺骗和ARP欺骗。

### 准备工作  

进行DNS欺骗之前，要检查试验机，有没有开启IP转发。Net.ipv4.ip_forward=0，则IP转发没有开启，需要手动将其设为1。

  
![DNA_1.png](https://image.3001.net/images/20180802/1533195383_5b62b47798404.png!small)开启apache服务

###  
![DNS_2.png](https://image.3001.net/images/20180802/1533195421_5b62b49d1a11b.png!small)实验流程  

1) 修改便捷ettercap中的DNS文件

在对应的位置，添加【域名 标识 欺骗后的IP地址】，如下，当受害者访问百度是，会跳转到xxx.xxx.xxx.136设置的页面。

![DNS-3.png](https://image.3001.net/images/20180802/1533195438_5b62b4ae0e0f1.png!small)  

2) 设计index.html文件

该文件是网站的主页文件。可以修改原来的index.html，也可以自己写一个新的页面，替换掉之前的index.html。

![DNS4.png](https://image.3001.net/images/20180802/1533195451_5b62b4bb009f1.png!small)  

3) 启动ettercap图形界面

-G命令是开起GUI模式。大家不喜欢使用图形界面的话，ettercap也有命令行模式，后面我也会附上ettercap进行DNS欺骗的命令。

![DNS5.png](https://image.3001.net/images/20180802/1533195461_5b62b4c500f3e.png!small)  

4) 配置网卡

局域网内搭建的环境，选择eth0。

![DNS_6.png](https://image.3001.net/images/20180802/1533195718_5b62b5c652358.png!small)  

5) 扫描主机

Host->Scan for hosts->hosts list扫描网段内的主机数量，并列出。

![DNS_7.png](https://image.3001.net/images/20180802/1533195733_5b62b5d573887.png!small)  

6) 列出扫到的主机

![dns-8.png](https://image.3001.net/images/20180802/1533195858_5b62b65225711.png!small)  

7) 添加网关和被监听的主机

网关IP添加为target 1,受害者IP添加为target 2。也可以不添加target 2,这样会监听网段内所有的主机。  

![DNS-9.png](https://image.3001.net/images/20180802/1533195904_5b62b6808c66f.png!small)  

8) 配置arp poisoning

开启ARP毒化，选择远程嗅探连接

![dns-10.png](https://image.3001.net/images/20180802/1533195925_5b62b6954806c.png!small)  

9) 远程窃听

![DNS-11.png](https://image.3001.net/images/20180802/1533197652_5b62bd543879d.png!small)  

10) 配置插件

双击dns_spoof，可以看到前面标记好一个星号

![dns12.png](https://image.3001.net/images/20180802/1533197666_5b62bd62461a6.png!small)  

11) start>start sniffing开始窃听

![DNS13.png](https://image.3001.net/images/20180802/1533197701_5b62bd85e031d.png!small)  

受害机器访问网页时，会看到我们提前设计好的页面，当受害主机PING想要浏览的页面时，会显示攻击者IP。

![dns14.png](https://image.3001.net/images/20180802/1533197964_5b62be8c49bf9.png!small)  

### 命令

开启IP转发，设计欺骗网页等步骤和图形界面是一样的。但是借助命令行，只需要一条命令，就可以执行上述复杂的操作过程。

![DNS15.png](https://image.3001.net/images/20180802/1533197999_5b62beaf2f636.png!small)  

## ARP欺骗

ARP欺骗又称ARP毒化，是一种内网中间人攻击手段。攻击者通过发送伪造的ARP报文，恶意修改网关或网络内其他主机的ARP表，造成用户或网络的报文转发异常。我们先来看一下ARP欺骗前后，受害者的ARP缓存表的变化。

实施ARP欺骗之前，被攻击者的ARP缓存表

![arp缓存1.png](https://image.3001.net/images/20180802/1533198018_5b62bec2a60b8.png!small)  

实施ARP欺骗之后，被攻击者的ARP缓存表

![ARP缓存2.png](https://image.3001.net/images/20180802/1533198242_5b62bfa2b16a1.png!small)  

1) ARP欺骗截获流量

![ARP1.png](https://image.3001.net/images/20180802/1533198166_5b62bf562eb91.png!small)  

2) 此时，被攻击者的机器发往网关的流量被攻击者截获，被攻击这此时无法进行正常的网页浏览。

![ARP2.png](https://image.3001.net/images/20180802/1533198183_5b62bf67bab77.png!small)  

3) 流量转发  

仅仅是截获流量，被攻击主机很容易发现异常，如何神不知鬼不觉的监视被攻击的主机呢？这就需要我们启动流量转发功能。

![arp4.png](https://image.3001.net/images/20180802/1533198339_5b62c0037176a.png!small)  

开始端口转发之后，在进行ARP欺骗，受害者发送和接收的流量包，都会经过攻击者的主机。攻击者通过截获这些流量，就可以监视受害者。arpspoof和ettercap都可用于arp欺骗，arpspoof进行arp欺骗的命令，请参照
1）。在此，我在介绍一下ettercat进行ARP欺骗的命令。

![arp6.png](https://image.3001.net/images/20180802/1533198646_5b62c13612a9d.png!small)我个人比较喜欢ettercap，非常便利，还有GUI模式。还有很多进行ARP欺骗的工具，大家可以根据自己的喜好进行选择。  

4) 监控流量

Driftnet可用于过滤嗅探图片，利用driftnet进行流量监控，显示被害者浏览的图片。当然也可以利用wirshark监控流量，通过分析流量，也可以获得cookie之类的信息。

![arp7.png](https://image.3001.net/images/20180802/1533198805_5b62c1d59c8c8.png!small)

## 监听嗅探

嗅探，可用于监听网络上的数据流量包。嗅探经常与ARP欺骗结合，通过ARP欺骗，拦截本该发送给受害者的数据包。嗅探，也是常见的中间人攻击中的一种。  

Netfuke是一款出名的ARP欺骗工具，也可以用于嗅探监听。下面是利用NetFuke进行ARP欺骗和监听嗅探的方法。

1) 设置->嗅探设置

![NETFUKE1.png](https://image.3001.net/images/20180802/1533198875_5b62c21b7e35b.png!small)  

2) 设置->ARP欺骗设置

来源IP即攻击者，或者说当前所在机器的IP。中间人IP即代理或者网关的IP。目标IP是攻击目标所在的IP。

![NETFUKE2.png](https://image.3001.net/images/20180802/1533198897_5b62c2315625e.png!small)  

3) 搭载插件

插件->插件管理->修改器

参数设置中的可修改参数设置

![NETFUKE3.png](https://image.3001.net/images/20180802/1533198917_5b62c245dcc2d.png!small)

4) 点击开始，开始嗅探欺骗

此时受害者网页浏览时，就会看到我们设置的网页。  

![NETFUKE4.png](https://image.3001.net/images/20180802/1533198942_5b62c25ee882b.png!small)  

左侧视图框可以查看配置信息，右侧可以监控欺骗流量和CPU使用率。

![NETFUKE5.png](https://image.3001.net/images/20180802/1533198977_5b62c28139f0f.png!small)  

5) 此时，可利用wireshark抓包，分析流量

##
![抓包.png](https://image.3001.net/images/20180802/1533199230_5b62c37e49f41.png!small)

## 总结  

今天这篇文章，介绍了3种内网渗透中，可能用到的攻击手法：DNS欺骗，ARP欺骗和监听嗅探。这些都是大家平时耳熟能详的攻击方式。渗透测试中的攻击手法多种多样，后面的文章中，我会尽可能多的分享更多的渗透手法。大家有想要学习的内容，可以在文章下留言。

 ***本文作者：EVA。本文属北京丁牛科技原创出品，转载请注明来自FreeBuf.COM。**

