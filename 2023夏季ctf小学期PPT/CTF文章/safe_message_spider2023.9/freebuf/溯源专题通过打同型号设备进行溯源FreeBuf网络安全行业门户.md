欢迎关注同名微信公众号！[狼蛛安全实验室](https://mp.weixin.qq.com/s/ccMQEhCoSwOaUV1RMFpFvg)！

##  **前言**

情景重现，通过前期的情报掌握，发现某一台设备被攻击者攻击，但还未做为跳板为攻击者传送数据，这时候就可以通过研究此型号设备的漏洞，尝试去获取此型号设备的Shell，最后尝试拿到被攻击者攻击的设备的shell，在上面布置后门以及流量监控程序。

##  **研究设备漏洞**

###  **一、什么设备？**

通常情况下，大部分攻击者攻击的设备都是路由器的设备，因为攻击者打下这个设备之后的主要目的就是拿它来做跳板机，作为数据的中转，通过它将最终获取到的数据转发到攻击者手中，那时时刻刻都有流量进出的路由器设备显然再合适不过了，同时大部分路由器的漏洞都不算太复杂，路由器厂商的安全意识也不算太高，打下来的难度相较于其他设备来说没有那么难。

###  **二、如何获取此型号设备的Shell？**

获取设备的Shell有三种方法，由于不清楚攻击者到底是通过何种方法打进去的，所以需要都尝试一下：

 **1、寻找已经曝光的CVE**

如果攻击者是用1day或者Nday的漏洞攻击进来的，那么就会使用带有CVE编号的漏洞进行攻击，这时候就可以通过谷歌或者直接上CVE官网搜索此型号的设备是否存在历史的漏洞，如果存在历史漏洞就好办了，直接上谷歌去搜索有关此CVE的信息，一般都是有对此漏洞进行描述的，可以作为复现此漏洞的一个辅助，不仅如此，还可以通过Github来搜索此CVE是否有人分析过并把EXP/POC放到Github上面去。

![1669967432_6389ae48e615f042fc091.png!small](https://image.3001.net/images/20221202/1669967432_6389ae48e615f042fc091.png!small)

\- [CVE编号搜索](https://cve.mitre.org/cve/search_cve_list.html)

\- [CVE有关信息检索](https://nvd.nist.gov/vuln)

\- [CVE漏洞EXP库](https://www.exploit-db.com/)

 **2、自己动手挖漏洞**

由于自己动手挖漏洞这个篇幅太过于繁多并且是提供一个思路，大家感兴趣的话可以在公众号留言，如果大家想看的话后续会发布此类文章，这里就简要说明一下：

  *  **寻找固件**

![1669967488_6389ae8078e3a969ff844.jpg!small](https://image.3001.net/images/20221202/1669967488_6389ae8078e3a969ff844.jpg!small)

上图就是一个固件，固件故名思意就是固化的软件，通俗点就是路由器上跑的代码，获取的思路也有几种：

a. 官网：官网中会放升级固件的固件包

b. 谷歌、论坛：有好心人会给链接

c. 提取固件：需要拿到设备通过特定的方式提取

  *  **解包**

解包的方式就一种就是binwalk解包，如果解不开就是被加密了或者binwalk的功能不完善：

![1669967495_6389ae87e211257d1cff0.png!small](https://image.3001.net/images/20221202/1669967495_6389ae87e211257d1cff0.png!small)

  *  **挖洞**

拿到文件系统之后就可以开始挖洞了，这里就简单介绍一些漏洞形式：

a. 命令注入

通过GET数据包中获取QUERY_STRING的值，未经过滤就直接拼接传给system执行导致命令注入。

![1669967554_6389aec20633f9c996629.png!small](https://image.3001.net/images/20221202/1669967554_6389aec20633f9c996629.png!small)

b. 栈溢出

图中的sscanf并未做长度限制，导致读入任意长度的字符串引发栈溢出。

![1669967563_6389aecb333aff8e856b3.jpg!small](https://image.3001.net/images/20221202/1669967563_6389aecb333aff8e856b3.jpg!small)

 **3、找攻击者留下的后门**

攻击者打下一个设备之后，总会留下一个后门以便他后续连接，而路由器设备的后门通常为telnetd监听某一个端口，所以可以通过扫描被攻击设备是否存在开放了一个莫名其妙的端口，比如的扫描结果：

    
    
    bash
    > nmap 192.168.0.1
    Nmap scan report for dlinkrouter (192.168.0.1)
    Host is up (0.0058s latency).
    Not shown: 993 closed tcp ports (reset)
    PORT      STATE SERVICE
    53/tcp    open  domain
    80/tcp    open  http
    443/tcp   open  https
    9999/tcp  open  abyss#奇奇怪怪的端口
    49152/tcp open  unknown

一般开在这种端口的shell都是不需要密码的，因为默认的telnet端口才是需要认证的，所以直接telnet (IP)
(PORT)就可以连接上了，连接成功之后就获得了一个Shell。

##  **后渗透**

获取到设备的Shell之后，下一步就是留下后门以便后续的操作，并且布置流量监控程序，监控是否有可疑的流量。

###  **一、留下后门  
**

一般拿到Shell之后都会先启动

telnetd -p (PORT) -l /bin/sh

先保持一个可以用的Shell，再将telnetd写到启动文件当中去，比如下图的这些启动文件，保证即使设备重启也可以启动telnetd。

![1669967711_6389af5f732a8a52ee8c9.png!small](https://image.3001.net/images/20221202/1669967711_6389af5f732a8a52ee8c9.png!small)

###  **二、布置流量设备**

布置流量设备也有两个方法：

 **1、自带流量抓包功能**

在某些比较高级的路由器上，都会有一个抓包的功能，所以只需要开启这个抓包的功能即可。

 **2、tcpdump**

布置流量设备即通过tftp/wget等文件传输功能，传输一个tcpdump到路由器上，下面是一写常见的抓起命令：

    
    
    bash
    ./tcpdump -i eth0 -s 0 -X -w /tmp/tcp.pcap#抓取eth0报文内容并保存到文件中
    ./tcpdump -i eth0 src (IP)#抓取指点源地址的数据包
    ./tcpdump -A -i eth0 #抓取eth0的数据并包显示

下面是一些其他的参考资料：

\- [TCPDump技术介绍及常见使用案例](http://www.bjbook.net/tcpdump.html)

\- [tcpdump命令详解](https://www.cnblogs.com/hunttown/p/13631592.html)

\-[路由器抓包工具TCPDUMP使用方式](https://blog.csdn.net/BeFander/article/details/126987558)

##  **总结**

本文梳理了通过打同型号设备来进行溯源的思路，从如何研究设备漏洞到后渗透留下后门和布置流量监控设备，最终完成部署，然后就可以静静等待攻击者利用跳板传送数据，这时候流量监控就可以记录到攻击者传输数据的行为达到溯源的目的。

