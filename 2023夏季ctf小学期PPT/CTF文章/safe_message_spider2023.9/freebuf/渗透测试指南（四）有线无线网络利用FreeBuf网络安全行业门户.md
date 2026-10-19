渗透测试指南系列文章内容纲要  
[ 第一章 渗透测试简介](https://www.freebuf.com/column/238471.html)  
[ 第二章 前期交互](https://www.freebuf.com/column/238471.html)  
[ 第三章 信息收集](https://www.freebuf.com/column/238867.html)  
[ 第四章 漏洞识别](https://www.freebuf.com/column/238867.html)  
[ 第五章 社会工程学](https://www.freebuf.com/column/239520.html)  
 ** 第六章 有线/无线网络利用**  
第七章 基于应用的漏洞利用  
第八章 基于本地主机和物理的利用  
第九章 后-利用 技术  
第十章 渗透测试工具集介绍  
第十一章 渗透报告

本文简单介绍了常见的几个网络服务的攻击模式，攻击工具，以及针对无线通信如WiFi和蓝牙的常见攻击模式分析。

# 基于网络的漏洞利用

本章覆盖到的网络服务和攻击模式如下  
NetBIOS，LLMNR和SMB  
DNS缓存投毒  
SNMP  
SMTP  
FTP  
hash传递（pass-the-hash）  
中间人攻击（MITM）  
SSL stripping攻击  
DoS和DDoS  
网络访问控制绕过（NAC bypass）  
VLAN hopping攻击

本章针对网络服务在 攻击模式，攻击工具，安全提示 三个方面展开描述。

## NetBIOS，LLMNR和SMB

NetBIOS和LLMNR是微软用于主机识别的协议。打开windows系统 控制面板--系统
界面，可以在“计算机名称，域和工作组设置”中看到计算机名，比如Pentest，这个名字就和域名一样，用于替换难记的ip地址。举一个简单的例子，比如右键共享某个文件夹xxx，共享完成后，系统会提示通过访问
\\\Pentest\xxx 查看共享文件。通过共享也就开启了SMB服务。

和NetBIOS有关的端口包括TCP 135，139；UDP 137，138。和SMB有关的端口为TCP 445。

### 攻击模式

所谓攻击模式(Attack
Pattern)和设计模式类似是根据经验提炼出来的抽象的，适用范围较广的模式。比如设计模式里的工厂模式，观察者模式等，在某种情境下套用模式效率会更高，代码结构更便于维护。攻击模式也是类似，比如中间人攻击，缓存投毒攻击，在某种情况下，使用相应的攻击模式，能高效达成攻击利用的目的。

[Common Attack Pattern Enumeration and Classification
(CAPEC)](https://capec.mitre.org/data/definitions/1000.html)
收集了非常多的攻击模式，从抽象到细节都有涉及，这是一座攻击模式宝库，有兴趣的读者请查阅。

主机枚举，账户密码暴破，LLMNR投毒，利用已知漏洞如永恒之蓝（EternalBlue）

### 工具

NBNSpoof， Metasploit， Responder，Pupy， searchsploit

### 安全提示

如无必要，可关闭NetBIOS和LLMNR的服务，这样可以减小系统的攻击面。可以通过查看注册表来判断LLMNR是否关闭。

## DNS缓存投毒

在我之前的文章
[渗透测试指南（三）社会工程学](https://www.freebuf.com/column/239520.html)中有提到一个社工方式为域欺骗，域欺骗可以通过改变受害者计算机上的主机文件（hosts文件），DNS投毒或者利用DNS服务器软件的漏洞进行。本节看一下DNS投毒是怎么回事。

我们访问一个域名时，系统会自动解析域名ip，顺序分别是 本地DNS缓存--hosts文件--DNS域名解析

DNS在解析域名时，会将上级回复的解析结果缓存在本地，在一定时间内如果再次查询该域名，就用缓存里的数据回复。而DNS缓存投毒是指攻击者用某些方式（比如入侵DNS服务器，中间人攻击等）把部分或者所有的域名都解析为攻击者控制的服务器ip地址。

![dns_poison.png](https://image.3001.net/images/20200616/1592288040_5ee863280b557.png!small)

图片来源 <https://medium.com/iocscan/dns-cache-poisoning-bea939b5afaf>

在dns投毒之前，通过nslookup
example.com，返回的是正常的ip地址，在DNS投毒之后，返回的就是攻击者可控制的ip地址，这样能达到钓鱼，域欺骗，中间人的目的。

### 安全提示

配置DNS服务器，尽量少的依赖其他DNS服务器，避免其他DNS服务器遭受投毒后感染

使用BIND 9.5.0以上的版本

使能DNSSEC

## SNMP

简单网络管理协议(SNMP)用于对组织内的设备进行管理。被管理的设备部署snmp agent，而管理的设备部署snmp manager。snmp使用udp
161端口。snmp有多个版本，其中v2c和v3被广泛使用，其中v2c使用字符串作为口令，而v3使用账户密码作为登录凭证。

### 工具

使用nmap和snmp相关的NSE脚本， snmp-check

### 安全提示

修改snmp v2c的默认口令

限制udp 161端口的访问

使用snmp v3

## SMTP

SMTP是邮件发送协议,另外和邮件相关的协议还有POP3和IMAP,其中SMTP用于邮件发送,而IMAP和POP3用于邮件接收.

端口对应关系:  
SMTP: 25, 465, 587  
POP3: 110, 995  
IMAP: 143, 993

SMTP支持以下信令  
HELO, EHLO, STARTTLS, RCPT, DATA, RSET, MAIL, QUIT, HELP, AUTH, VRFY, EXPN

### 攻击模式

open-relay 邮件匿名转发, 可以通过nmap脚本smtp-open-relay来检测邮件服务器是否开启邮件转发。邮件转发可用于发送社工邮件。

使用smtp-user-enum工具，基于VRFY和EXPN信令进行用户名枚举

通过searchsploit smtp搜索smtp相关的漏洞

### 安全提示

关闭smtp服务器open-relay功能

屏蔽VRFY和EXPN信令

## FTP

FTP是文件传输协议，是使用频率非常高的网络协议。一般是监听tcp 21端口。

### 攻击模式

匿名访问ftp服务器，查看文件（msf有利于模块auxiliary/scanner/ftp/anonymous）

ftp账户，密码暴破

### 安全提示

用SFTP或者FTPS替代FTP

取消FTP匿名账户登录

配置FTP高强度账户密码

对ftp的目录和文件做好权限配置，对用户可访问的文件做访问控制

加密ftp服务器上的文件

## hash传递

Windows把用户密码通过hash保存在SAM文件中，SAM文件位置在C:\Windows\System32\config\

Windows有两套认证协议，一个是NTLM，一个是Kerberos，而NTLM又有两个版本NTLM v1和NTLM v2，NTLM就存在hash传递问题

所谓hash传递是指
认证服务器保存了用户的密码的hash值，用户在客户端输入密码后，客户端计算密码的hash值传给服务器，服务器比较密码hash值是否一致。而hash传递是指攻击者不知道密码原文，但是知道hash后的密码，攻击者只要把hash后的密码发给服务器，也可以完成认证。

### 工具

Mimikatz，该工具被用于获取内存中的密码的hash值。

metasploit也有Mimikatz模块，可以实现相同功能。

## 中间人攻击

中间人攻击（Man-in-the-middle：MITM）是指攻击者把自己放在通信双方的中间位置。

### 攻击模式

ARP 缓存投毒

DNS劫持，DNS污染，DNS缓存投毒

操作STP（Spanning Tree Protocol）成为根交换机

流氓路由器，让其他路由器认为该路由器有最佳路由策略

在被攻击者设备安全恶意软件，劫持流量到中间人设备

### 工具

arpspoof， ettercap， SSLStrip， SSLsplit

### 安全提示

配置路由器/交互机的ACL

实现802.1X

使能DAI（Dynamic Address Resolution Protocol Inspection）防止ARP投毒

配置好VLAN

## DoS/DDoS

DoS攻击可分为直接攻击，反射攻击，放大攻击

直接攻击是指攻击设备流量直接打到目标设备，反射攻击是指攻击者把流量打到中间设备，中间设备再反射给目标设备。放大攻击属于反射攻击，只不过是在反射过程中，流量被放大。

DDoS攻击的应用场景是目标设备是云平台，攻击者无法达到能把目标设备的流量打满，故需要多台设备一起攻击。

DoS攻击除了打流量外，还有其他攻击方式，比如死亡之ping，缓冲区溢出等

### 工具

hping3， mirai，hulk，LOIC， R-U-Dead-Yet， slowloris， torshammer

## 其他攻击模式

降级攻击，比如利用POODLE漏洞可以降低加密协议套件强度

BGP劫持

NAC绕过（MAC认证绕过，攻击者修改本机MAC地址为NAC MAC白名单中的地址，即可绕过）

VLAN 跳跃攻击

DHCP饥饿攻击和流氓DHCP服务器（先通过饥饿攻击耗尽DHCP服务器的IP地址，再搭建流氓DHCP服务器（工具：Yersenia））

# 基于无线和RF的漏洞利用

## 流氓接入点(Rogue Access Point)

攻击者架设一个无需认证的流氓接入点让用户连接到该AP后，进一步执行其他攻击

## 邪恶双生子(Evil Twin)

攻击者架设一个和目标AP一样的SSID和密码的AP，让被攻击者以为连接到正常的AP(Access Point)

## 解除认证攻击(Deauthentication)

无线设备连接到AP，无线设备有STATION ID，AP有BSSID, 可以通过工具aireplay-ng来解除无线设备和AP的认证关系，导致连接断开

首先要获取无线设备的STATION ID和AP的BSSID，要开启无线网卡的监听模式，可以通过airmon-ng开启/确认监听模式是否开启，接下来可以通过airodump-ng查看BSSID和STATION

## WiFi信号干扰(Jamming Wireless Signals)

WiFi信号有2.4g和5g频段，每个频段有分为多个通道，每个通道有自己的频率范围，如果通过无线发射设备在目标频率范围不断发射高强度信号，可以造成拒绝服务攻击。

## 战争驾驶(War Driving)

可以简单理解为开车在目标附近游荡，收集目标地点的无线信号情况并在地图上画出。

常用的工具比如WiGLE

## WEP攻击

WEP是通过RC 4算法加密，且初始向量IV是明文传输的。可以通过抓取大量的WEP来破解PSK(Pre-Share Key)密码

    
    
    # 开启无线网卡监听模式
    airmon-ng start wlan0 l1
    
    # 监听目标AP和通道，保存到文件
    airodump-ng -c l1 --bssid 11:22:33:44:55:66 -w tmp_capture wlan0
    
    # 破解WEP密码
    aircrack-ng -b 11:22:33:44:55:66 tmp_capture.cap
    

## WPA攻击

WPA有两个版本WPA和WPA2，不过现在已经有WPA3了，高版本WPA修复了低版本的一些安全漏洞，可以通过抓取WPA四次握手过程，去破解PSK密码

演示过程如下

    
    
    # 开启无线网卡监听模式
    airmon-ng start wlan0
    
    # 抓取目标AP和通道的数据包，保存为文件
    airodump-ng --channle 11 --write tmp_capture --bssid 11:22:33:44:55:66
    
    # 针对目标AP进行解除认证攻击，让无线设备重新连接目标AP，这个过程中，能抓取到WPA认证过程的四次握手，当airodump-ng终端看到四次握手信息后，退出
    aireplay-ng -0 0 -a 11:22:33:44:55:66 wlan0
    
    # 利用字典跑WPA的密码
    aircrack-ng -w password.list tmp_caputre.cap
    

## KRACK攻击

KRACK是key reinstallation
attack(密钥重装攻击)的缩写。有兴趣可查看参考材料<https://krackattacks.com>

## WPS攻击

WPS(WiFi Protected Setup)如果AP支持且开启WPS功能，那么就可以通过PIN码登录设备，而PIN码是8位数字，可以被暴破。

常用的工具有Reaver

## KARMA攻击

KARMA(Karma Attack Radio Machines
Automatically)是一种中间人攻击方法。无线客户端每次连接到一个AP，都会记录下SSID和PSK等信息，在无线客户端没有连接到无线网络时，会不断的尝试连接这些已经记录在本地的AP信息（PNL：Preferred
network list）。KARMA攻击是指监听无线客户端的所有Probe尝试，让后仿冒一个PNL中的AP达到中间人攻击的目的。

## 分片攻击(Fragmentation Attacks)

无线分片攻击可以用于攻击使能WEP的设备。通过PRGA（pseudo random generation
algorithm）算法生成1500字节来执行无线注入攻击。

常用的工具有packetforge-ng

更多相关内容可查看论文<https://www.offensive-security.com/wifu/Fragmentation-Attack-in-Practice.pdf>

## 蓝牙劫持(Bluejacking)

蓝牙劫持是指通过蓝牙向目标设备发生信息，如通讯录名片等

## 蓝牙窃用(Bluesnarfing)

通过蓝牙从目标设备获取信息，如获取IMEI，通话记录及短信等。

常用的蓝牙窃用工具有bluesnarfer

## RFID攻击

RFID分为主动和被动，被动RFID卡片不自带电源，需要读卡器电磁谐振获取能量，发送和接收数据。主动RFID卡片自带电源。

RFID分为低频卡和高频卡，其中低频卡120k-140kHz，高频卡13.56MHz，超高频卡860M-960MHz, 频率越高，允许传送的距离越长

常用的RFID攻击工具为Proxmark3， 可以通过该攻击clone卡片，模拟卡片等

# 总结

我看Pentest+认证指南把利用分为三个章节，分别是有线/无线，应用程序，本地和物理。我在想为什么要这么分类。针对一个目标系统的渗透测试，要先考虑攻击面。首先如果目标系统没有联网功能，那只能通过
**本地/物理** 的方式进行测试，本地比如GUI，串口shell，物理比如JTAG，UART从本地 **硬件和软件**
层面对系统进行测试。当然了，目标系统能联网也有这个攻击面，为了便于理解，我们先假设目标系统分为联网和不联网两类。而联网可以通过无线和有线，针对无线和有线的物理信道的攻击和网络服务本身无关，也是一个攻击面。在物理信道之上的网络服务，又可以分为自研的网络服务和第三方网络服务比如开源的软件/服务，所有最终可以分为这几类：本地的攻击，无线信道攻击，第三方应用服务攻击，自研应用服务攻击。

Pentest+针对脆弱点评估和漏洞利用知识体系，大体上是点到为止，没有特别深入，这也很正常。就SQL注入来说，要深入讲解可能一大本书都讲不完。所以在这样一本认证指南书籍中，也不会非常深入讲解，从top-down的视角教你一些其他知识。比如从章节布局了解渗透测试流程体系，以及攻击面分析思路。从各个章节内容了解该章节涉及到的基本思维方式，比如有线/无线章节，从版本探测，已知漏洞验证，metasploit的使用等等。渗透测试过程总会碰到一些之前没接触过的新服务，这时候，你就需要参考本书罗列的已知方法，融会贯通。我认为这才是认证指南知识体系的意义所在。

原计划接下来的文章安排  
第七章 基于应用的漏洞利用  
第八章 基于本地主机和物理的利用  
第九章 后-利用 技术  
第十章 渗透测试工具集介绍  
第十一章 渗透报告

我做了一些小调整，我计划后续再写四篇文章，顺序分别是 后利用及报告，渗透测试工具集，基于应用的漏洞利用，基于本地主机和物理的利用。

 **由于笔者水平有限，文章难免会有错误的，欢迎读者批评指正。笔者个人邮箱：kafrocyang@gmail.com**

# 参考文献

[1] CompTIA Pentest+ Cert Guide

