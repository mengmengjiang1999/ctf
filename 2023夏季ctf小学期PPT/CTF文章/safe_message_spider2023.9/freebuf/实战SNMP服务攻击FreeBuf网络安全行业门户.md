## 前言

之前写过一篇[《从交换机安全配置看常见的局域网攻击》](../articles/network/319009.html)的文章，讲解了我们在局域网中会遇到的一些网络攻击。本文继续围绕交换机，来聊聊我们熟知的SNMP服务。

## SNMP基础

### 简介

SNMP全称简单网络管理协议，是专门设计用于在IP网络管理网络节点（服务器、工作站、路由器、交换机及HUBS等）的一种标准协议，是一种应用层协议。通过SNMP可以访问设备信息、改写和配置设备参数等，SNMP运行在UDP161端口上，采用UDP协议在管理端和agent之间传输信息。

### 架构

SNMP架构主要分如下三个部分组成：

  *  **网络管理系统（NMS，Network-management systems）**

  *  **被管理的设备（managed device）**

  *  **代理者（agent）**

上面这三部分从名字上看很复杂，其实很简单。我们只需要知道，"NMS"就是客户端，"被管理的设备"就是交换机、路由器之类的设备，而"代理者"可以理解为装在交换机上的一个程序而已。

## SNMP版本

SNMP目前共有 **v1、v2c、v3** 这三个版本：

  * SNMP v1是SNMP协议的最初版本，不过依然是众多厂家实现SNMP的基本方式；

  * SNMP v2c通常被指是基于Community的SNMP v2c， **而Community本质上就是密码；**

  * SNMP v3是最新版本的SNMP，它对网络管理最大的贡献在于其安全性，增加了对认证和密文传输的支持。

## Community String

Community String在交换机与路由器配置里意为"社区字符串"也有人叫"团体名"，其实说的都是一个东西。Community其实就是充当
**密码** 作用的一串字符串而已。大多数的设备供应商，默认都有两个Community String：

  *  **public 通常用来查询(只读)**

  *  **private 通常用来查询和配置(读写)**

P.S：很多安全问题就是由这两个"默认密码"而引发的。

## MIB和OID

MIB全称管理信息库，是一种 **树状数据库；** MIB管理的对象，就是树的节点。每个节点都有唯一名字和唯一OID(Object
Identifier)，OID由树上的一系列整数组成，整数之间用点( . )分隔开，树的叶子节点才是真正能够被管理的对象。

我们通过SNMP获取信息就会用到OID，比如网络设备名的OID 是.1.3.6.1.2.1.1.5.0，其值为设备名称的字符串。简单点来理解就是：
**把MIB当成一个k.v数据库，我们输入key(OID)就能获取到对应的value** 。

为了方便查阅，我们收集了一些OID列表和MIB库。

  * <https://www.10-strike.com/network-monitor/pro/useful-snmp-oids.shtml>
  * <https://gist.github.com/JosefJezek/6824959>
  * <http://www.ttlsa.com/monitor/snmp-oid/>

 **OID查询**

  * <http://www.oid-info.com/cgi-bin/display?tree=#focus>
  * <https://bestmonitoringtools.com/mibdb/mibdb_search.php>

除了上面提到的，其实还有一种方法可以获取MIB库。那就是直接从设备供应商的官网进行下载，如下是我在[h3c文档](http://www.h3c.com/cn/d_200906/636062_30003_0.htm#_Toc231200798)上看到的。![](https://image.3001.net/images/20220110/1641805247_61dbf5bf35eaff7c66e33.png!small)

## 工具

测试SNMP可用的工具主要有如下几个：

###  **[1.net-snmp](http://www.net-snmp.org/)**

kali系统里面已经内置net-snmp工具包，我们直接终端输入命令即可使用；net-snmp是我们本次测试SNMP主要工具，后续的操作都采用这款工具进行演示和操作。

Net-snmp工具包提供如下工具，支持对交换机进行各种操作。

![](https://image.3001.net/images/20220110/1641805341_61dbf61d0762d2e683677.png!small)

而我们平常主要使用snmpwalk、snmpget、snmpset这三款工具进行测试。snmpwalk和snmpget都可以用来获取值，其主要区别是snmpwalk是对OID值的遍历，而snmpget是取具体的OID的值。

###  **2.msf模块**

msf也有一些针对SNMP的利用模块。由于本文篇幅有限，感兴趣的自行研究。

![](https://image.3001.net/images/20220110/1641805395_61dbf653a4400226aa510.png!small)

###  **3.snmputil**

用于windows系统的snmp工具。

## 环境搭建

了解完上面的基础知识后，我们在交换机上配置一个SNMP服务开始测试。

输入如下命令可在h3c交换机上开启SNMP服务(为了方便后面的测试，我把读和写都打开)。

    
    
    system-view  
    # 设置Agent使用的SNMP版本为v2c  
    snmp-agent sys-info version v2c  
    # 设置只读团体名为public  
    snmp-agent community read public  
    # 设置读写团体名为private  
    snmp-agent community write private

![](https://image.3001.net/images/20220110/1641805498_61dbf6baecb5a48f7164d.png!small)

P.S： **不同的设备配置方式有所不同，具体请参照官方文档** 。

## SNMP服务发现

第一步，通过nmap进行目标主机服务发现。

这里我们需要注意的是nmap默认是不扫描udp端口的，我们需要用`-sU`参数对udp端口进行单独扫描。![](https://image.3001.net/images/20220110/1641805591_61dbf7177aab0692fc165.png!small)

## 获取Community String

第二步，获取Community String。前面的基础知识已经介绍了Community
String就是密码，所以我们要想使用SNMP肯定需要先知道它对应的"密码"。

###  **1.默认密码尝试**

对于一些有经验的师傅来说，在对某些系统和服务进行渗透的时候，一开始肯定就是试试弱口令。更何况SNMP的默认密码在内网是普遍存在的。前面已经提到了，大多数的设备供应商和一些网管都喜欢用public和private。

如下图，如果密码错误会直接返回`Timeout: No Response from
192.168.6.1`，密码正确则返回设备相关信息(最前面的一列是OID，查询的时候前缀iso可以不输入，也可以用1代替)。

![](https://image.3001.net/images/20220110/1641805659_61dbf75bcd4255358a299.png!small)

###  **2.密码爆破**

如果通过手动尝试默认密码失败之后，我们还可以进行爆破。一般SNMP密码都不会太复杂，很容易就跑出来了。

进行SNMP密码爆破，我们需要用到一款新的工具onesixtyone，由于使用比较简单不过多介绍。事实上光看帮助信息的examples就知道怎么用了。

![](https://image.3001.net/images/20220110/1641805778_61dbf7d2e7ce74f7cdbf2.png!small)

尝试密码爆破，可以看到之前我们配置的密码都被扫出来了。

    
    
    onesixtyone -c /usr/share/doc/onesixtyone/dict.txt 192.168.6.1 -w 64

![](https://image.3001.net/images/20220110/1641805817_61dbf7f9a85f5dd4a2d69.png!small)

## 敏感信息获取

第三步，敏感信息获取。在拿到"密码"之后我们就可以开始下一步利用了，我们需要收集什么信息可以通过之前提供的OID表进行查询，需要注意的是不同设备OID是不同的。

下面简单演示一下。

  * 获取设备名

    
    
    snmpget -c private -v2c 192.168.6.1 .1.3.6.1.2.1.1.5.0

![](https://image.3001.net/images/20220110/1641805894_61dbf846f127775bd0cf4.png!small)

  * 获取设备运行了多久

    
    
    snmpget -c private -v2c 192.168.6.1 1.3.6.1.2.1.1.3.0

![](https://image.3001.net/images/20220110/1641805938_61dbf872e61277d133d94.png!small)

  * 获取设备划分的vlan

    
    
    snmpwalk -c private -v2c 192.168.6.1 1.3.6.1.4.1.25506.8.35.2.1.5.1.2

![](https://image.3001.net/images/20220110/1641805972_61dbf8945cb1e5a640a45.png!small)

  * 获取设备开放的端口

    
    
    snmpwalk -c private -v2c 192.168.6.1 1.3.6.1.2.1.6.13.1.2

![](https://image.3001.net/images/20220110/1641805987_61dbf8a307d0fcec572cd.png!small)

  * 获取存活的内网ip

    
    
    snmpwalk -c private -v2c 192.168.6.1 1.3.6.1.2.1.4.22.1.1.634

![](https://image.3001.net/images/20220110/1641805999_61dbf8afd9ec1c48455c6.png!small)

如果嫌找OID太麻烦，还可以直接用snmpwalk遍历整个MIB库。然后把数据保存下来慢慢翻，这也是种不错的选择。

    
    
    snmpwalk -c private -v2c 192.168.6.1 >>h3c_oid.txt

![](https://image.3001.net/images/20220110/1641806378_61dbfa2a9d557d318c4ad.png!small)

P.S：如果查询的内容返回值是单条信息，如"设备名称"可以用snmpget工具进行查询。如果是返回多条信息如"vlan信息"就需要用snmpwalk工具进行查询。snmpwalk单条信息和多条信息都使用，因为它是对OID进行遍历操作。

## 设备配置修改

除了可以读取信息，我们还可以对设备的配置进行修改。但这样做侵入性非常高，不建议这样做，一旦操作失误，极有可能暴露自己，从而导致权限的丢失。下面简单的演示一下配置修改：

我们先获取设备的名称。从返回值我们可以知道该设备名是"H3C"

    
    
    snmpget -c private -v2c 192.168.6.1 .1.3.6.1.2.1.1.5.0

![](https://image.3001.net/images/20220110/1641806281_61dbf9c9c97837ed6a1a8.png!small)

我们尝试对其进行修改，把名称改为"hacker"。

    
    
    snmpset -c private -v2c 192.168.6.1 .1.3.6.1.2.1.1.5.0 s "hacker"

![](https://image.3001.net/images/20220110/1641806255_61dbf9af395a3b33b012f.png!small)

再次获取设备名，发现已经修改成功了。

![](https://image.3001.net/images/20220110/1641806225_61dbf9913416bd30af2d6.png!small)

如果拿到的"社区字符串"是只读权限的，我们尝试修改会报如下错误：

![](https://image.3001.net/images/20220110/1641806105_61dbf919c59d8d8c30207.png!small)

在实战中，我们可以根据目标具体的场景来做不同的修改：如改一下设备的 **ACL。**

## SNMP rce

最后再来谈谈rce。SNMP并不是所有设备都可以被rce，目前看来好几个可以rce的都已经加到msf模块里面了。除此之外，如果目标是linux系统还可以借助
**NET-SNMP-EXTEND-MIB** 来进行rce。由于篇幅原因这里不再深入研究，具体操作可见下面两篇文章：

  * <https://mogwailabs.de/en/blog/2019/10/abusing-linux-snmp-for-rce/>

  * <https://rioasmara.com/2021/02/05/snmp-arbitary-command-execution-and-shell/>

# 参考

  * <https://www.cnblogs.com/xdp-gacl/p/3978825.html>

  * <https://www.anquanke.com/post/id/85976>

  * <https://rioasmara.com/2021/02/05/snmp-arbitary-command-execution-and-shell/>

  * <https://www.anquanke.com/post/id/85976>

  * <https://www.anquanke.com/post/id/260832#h3-8>

