## 一、概述

 **本文章结合作者在资产探测、入侵检测、网络攻防、蜜罐研究相关工作中大量实践,在此对工控蜜罐识别与反识别的技术进行研究与应用实践与大家进行分享与探讨。**

工控蜜罐通常指非真实工控设备，通常指应用服务、仿真程序等，比如服务蜜罐包括conpot、openplc、CryPLH2、仿真程序包括modbus
tester、Mod Rssim、snap7、opendnp3、qtester104、DNP3_testhaness、EtherNetIP
Virtual等。

## 二、蜜罐介绍

蜜罐是一种软件应用系统，用来称当入侵诱饵，诱导黑客前来攻击。攻击者入侵系统后，通过监测与预计分析，就可以知道他是如何入侵的，随时了解针对系统发动的最新的攻击和漏洞。还可以通过窃听黑客之间的联系，收集黑客所用的种种工具，并且掌握他们的社交网络。

蜜罐系统以伪装技术为基础，在用户内部网络中部署与真实资产相似的“陷阱”（蜜罐节点）,当攻击者通过外部安全防御系统的缺陷渗透进入到内部网络时，通常需要搜索网络内部的资产，以此找到对攻击者而言有价值的目标。
蜜罐节点自身的伪装性能够欺骗攻击者，当攻击者将蜜罐节点作为攻击目标时，
蜜罐节点能够第一时间感知并汇报安全事件，具体包括：蜜罐节点会记录攻击者的所有行为，系统也会产生告警，通知安全运营管理人员。蜜罐节点会诱骗攻击者将其他蜜罐节点作为后续的攻击目标，
所有蜜罐节点将组成“陷阱”网络，延缓了攻击时间，使得蜜罐系统能够记录更多的攻击信息，分析潜在威胁。

### （1）蜜罐种类

蜜罐可以分为数据库蜜罐、web蜜罐、服务蜜罐、工控蜜罐及端点蜜罐，各种蜜罐对应的相关产品如下图所示：

![](https://image.3001.net/images/20200313/1584092693_5e6b5615cc779.png!small)

### （2）常见蜜罐及地址

T-pot蜜罐是一种融合了多种开源蜜罐服务的汇总，其中包括工控蜜罐conpot，所有蜜罐采用docker容器化方式部署与管理，关于T-pot的安装和使用可以参考freebuf相关文章，下图是T-pot蜜罐使用的系统架构图。

![](https://image.3001.net/images/20200313/1584094765_5e6b5e2ddab0b.png!small)

### （3）现有工控蜜罐缺陷

目前互联网上部署了大量的工控蜜罐，大多都是基于conpot蜜罐和仿真服务程序。这些蜜罐基本属于中低交互形式，蜜罐指纹特征通用、部署在云服务器上或者企业直接通过端口映射方式接入到互联网。

## 三、蜜罐识别方法

首先在192.168.10.100(windows安装仿真器)及192.168.10.122(linux安装部署openplc、conpot、tpot蜜罐仿真服务)，安装方法可以参考freebuf相关文章。

### （1）IP地址识别

一般工控设备如plc、dcs、rtu等很少直接暴露到互联网，在业务需要情况下可能会将工控设备直接暴露在互联网，比如设备远程维护等。

通过查询IP地址对应的ISP，既服务提供运营商，来判断所述IP是否属于云服务器提供商的IP地址。当所述IP属于云服务器，并且开放了PLC的工控协议服务如modbus、s7、ethernetip等，则可判定IP为工控蜜罐。

针对IP地址对应的ISP和Organization的信息查询，能够通过如IPIP、纯真、Rtbasia、ipplus360、iplookup、GeoIp2、IP2Region的IP地址信息库，通过获取的信息来综合判定IP地址是否属于云服务器提供商。

![](https://image.3001.net/images/20200313/1584092941_5e6b570d93269.png!small)

![](https://image.3001.net/images/20200313/1584092951_5e6b57174f6e4.png!small)

### （2）操作系统及MAC厂商指纹识别

一般工控设备均为嵌入式设备，如plc、dcs、rtu大多使用实时操作系统如vxworks、QNX，HMI设备一般使用wincc操作系统等；通过TCP/IP操作系统指纹识别，获取目标IP的TCP/IP协议栈指纹，当目标IP的操作系统被识别为Linux的非嵌入式操作系统。并且该设备未经过路由转发与映射，通常可认为是蜜罐系统。

操作系统识别可以使用Nmap和Xprobe2的扫描工具，Nmap是一种开源的工业级扫描工具，Xprobe2是一种操作系统扫描工具。

设备MAC地址会根据不同的设备厂商分配不同的段， 工控设备厂商大多也可以从MAC地址来区分。

下图MAC为西门子厂商 S7300 PLC真实设备

![](https://image.3001.net/images/20200313/1584093168_5e6b57f098a4c.png!small)

下图MAC为施耐德厂商 M580 PLC真实设备

![](https://image.3001.net/images/20200313/1584093175_5e6b57f752785.png!small)

下图MAC为GE厂商 GESRTP协议 PLC 真实设备

一般工控蜜罐，如服务蜜罐大多部署在linux vmware及docker容器里面，而仿真服务部署在windows系统上面。

下图为modbus协议PLC使用vmware，可判断为蜜罐服务

下图为该设备为modbus协议plc设备，但是通过tplink路由器进行报文路由，所以该 设备 mac地址变成tplink路由器mac地址。

![](https://image.3001.net/images/20200313/1584093407_5e6b58df0d561.png!small)

### （3）指纹特征识别

 **Openplc modbus蜜罐服务指纹特征识别：**

Modbus plc真实工控设备一般会开放modbus 502端口， http 80/8080端口，snmp 161端口：

安装部署Openplc，并且阅读源码如下，分析蜜罐特征，可以看出openplc只实现了1-16功能码，而重要的设备信息功能码如报告从设备信息17功能码、获取设备信息43功能、施耐德获取cpu、工程等信息90私有功能码均未实现。

![](https://image.3001.net/images/20200313/1584093415_5e6b58e7c72e5.png!small)

Plc Modbus协议指纹识别，所以我们可以构造17、43、90功能码去请求openplc，获取设备信息，均会返回非法功能码指纹，如下图所示：

 **openplc http协议指纹识别：**

利用nmap 扫描工具对目标设备开放的端口和服务进行扫描识别，可以发现openplc默认开放了http
8080端口，浏览器访问[http://ip:8080](http://ip:8080/)查看plc管理页面与真实工控plc设备不一样，并提取http指纹特征。

![](https://image.3001.net/images/20200313/1584093508_5e6b594460941.png!small)

![](https://image.3001.net/images/20200313/1584093517_5e6b594d4e70d.png!small)

 **Conpot S7 协议 蜜罐服务指纹特征识别：**

在shodan寻找工控蜜罐如下图所示，可通过nmap -p 102 --script s7-enumerate.nse 116.85.10.173 进行s7
plc资产探测验证，并获取以下数据报文。

![](https://image.3001.net/images/20200313/1584093547_5e6b596bdb833.png!small)

通过阅读conpot s7comm源码，找到S7服务蜜罐通用特征如下所示

特征1：

![](https://image.3001.net/images/20200313/1584093559_5e6b5977ceadc.png!small)

如下图所示:

![](https://image.3001.net/images/20200313/1584093569_5e6b59815d2c2.png!small)

特征2:

通过阅读conpot s7蜜罐服务代码，发现S7返回的获取设备信息应用数据最后6个字节始终为 “\x00\x00\x00\x00\x00\x00”

![](https://image.3001.net/images/20200313/1584093578_5e6b598a0f0d3.png!small)

但是特征1可以通过conpot 模板进行蜜罐特征快速简单修改，而特征2如果要修改，则需参照s7协议规约对源代码进行修改，我们采用指纹特征识别conpot
s7蜜罐时候，则可以采用以上两种方式进行识别。

 **Conpot ENIP蜜罐服务指纹特征识别：**

通过阅读conpot enip蜜罐服务代码，发现向设备发送63功能码获取设备信息，返回的数据device_status== \x60\x31
和device_state == \xff

![](https://image.3001.net/images/20200313/1584094422_5e6b5cd6d8c30.png!small)

 **其它工控蜜罐：**

Conpot 中还包括其它工控服务程序，均可以结合工控协议规约及通过抓包分析，并与真实设备抓取的数据包进行比对分析，找出蜜罐特征。

其它蜜罐及仿真服务程序包括，conpot、openplc、CryPLH2、仿真程序包括modbus tester、Mod
Rssim、snap7、opendnp3、qtester104、DNP3_testhaness、EtherNetIP Virtual等。

## 四、蜜罐反识别方法

通过对蜜罐部署方式及特征分析，如果我们部署蜜罐服务时候，可以考虑采用以下方法进行规避。

> 1.如果蜜罐服务要部署在外网，尽量避免使用云服务厂商提供的服务。
>
>
> 2.如果蜜罐服务部署在企业内网，尽量在蜜罐服务或者仿真程序前面部署一个vxworks系统的设备，并在上面开启端口转发服务，或者利用Qmenu模拟运行vxworks操作系统，使攻击者误以为扫描到的工控设备使用的是vxworks实时操作系统。
>
>
> 3.定期修改蜜罐内部特征，如conpot蜜罐模板信息，conpot源码中返回报文的协议特征。同一个ip蜜罐节点，尽量只开放如真实plc设备的端口和服务，如502、80、161等端口，避免开放过多及无效的应用端口，被攻击者快速识别蜜罐。
>
> 4.修改宿主机mac地址，尽可能修改成西门子、GE等工控设备的MAC地址，增加攻击者识别蜜罐的难度。
>
> 5.服务蜜罐尽可能实现协议规约必须的功能码，如施耐德plc的17、42、90信息获取功能码任何一个。
>
> 6.尽可能实现高交付服务蜜罐，也可以采用虚实结合部署方式进行部署，增加蜜罐识别难度。

## 五、蜜罐架构及系统业务

工控蜜罐系统架构如下图所示：

![](https://image.3001.net/images/20200313/1584093786_5e6b5a5a72c7b.png!small)

工控蜜罐系统业务如下图所示：

![](https://image.3001.net/images/20200313/1584094527_5e6b5d3f64bc3.png!small)

## 六、总结

蜜罐服务及系统使用场景较多，主要包括部署在互联网、企业内网、网络攻防竞赛平台中等。当部署在互联网上，可以收集资产探测系统的资产识别指纹，以及攻击者的针对漏洞的攻击行为，便于安全研究与分析；当部署在企业内网，可以做为威胁感知系统，捕获攻击者行为，触发告警系统，延缓真实设备被攻击的时间和风险；当部署在网络攻防竞赛系统里面，可以混淆真实设备，诱导攻击者入侵，增加比武竞赛难度。

## 七、参考链接

> [openplc部署于分析](https://www.freebuf.com/articles/ics-> articles/213018.html)<https://www.freebuf.com/articles/ics-> articles/213018.html>
>
> [工控资产嗅探与分析](https://www.freebuf.com/ics-> articles/209786.html)<https://www.freebuf.com/ics-articles/209786.html>
>
>
> [tpot安装与使用](http://www.freebuf.com/news/193347.html)<http://www.freebuf.com/news/193347.html>
>
>
> [mac地址与对应厂商](https://gitlab.com/wireshark/wireshark/raw/master/manuf)<https://gitlab.com/wireshark/wireshark/raw/master/manuf>

 ***本文原创作者：yy0308，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

