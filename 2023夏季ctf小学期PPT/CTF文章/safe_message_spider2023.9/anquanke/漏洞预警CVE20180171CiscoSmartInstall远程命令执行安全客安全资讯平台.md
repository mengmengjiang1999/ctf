# 漏洞预警|CVE-2018-0171:Cisco Smart Install远程命令执行

阅读量 **242008**

发布时间 : 2018-03-30 09:21:15

 **x**

##### 译文声明

本文是翻译文章，文章原作者 360Cert，文章来源：https://cert.360.cn

原文地址：<https://cert.360.cn/warning/detail?id=f7d09fffded750e131cda824ef356514>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01c332a1f4ec475bc4.jpg)

报告编号： B6-2018-032902  
报告来源： 360-CERT  
报告作者： 360-CERT，360-NetOPS  
更新日期： 2018-03-30

## 漏洞描述

思科 IOS 和 IOS-XE 系统 Smart Install Client
代码中存在一处缓冲区栈溢出漏洞（CVE-2018-0171）。攻击者可以远程向 TCP 4786
端口发送一个恶意数据包，利用该漏洞，触发目标设备的栈溢出漏洞造成设备拒绝服务（DoS）或在造成远程命令执行，攻击者可以远程控制受到漏洞影响的网络设备。  
据悉，思科交换器 TCP 4786 端口是默认开放的，目前相关PoC已经被发布（完整性有待证实），360-CERT建议相关用户尽快进行评估升级。

## 漏洞影响面

**影响危害级别：严重**  
 **影响设备主要涉及：**  
Catalyst 4500 Supervisor Engines  
Cisco Catalyst 3850 Series Switches  
Cisco Catalyst 2960 Series Switches  
 **部分包含Smart Install Client的设备也可能受到影响：**  
Catalyst 4500 Supervisor Engines  
Catalyst 3850 Series  
Catalyst 3750 Series  
Catalyst 3650 Series  
Catalyst 3560 Series  
Catalyst 2960 Series  
Catalyst 2975 Series  
IE 2000  
IE 3000  
IE 3010  
IE 4000  
IE 4010  
IE 5000  
SM-ES2 SKUs  
SM-ES3 SKUs  
NME-16ES-1G-P  
SM-X-ES3 SKUs

## 修复检测建议

**检测是否存在漏洞**  
确认目标设备是否开启4786/TCP端口，如果存在可能收到影响，比如用nmap扫描目标设备端口：  
nmap -p T:4786 192.168.1.0/24  
此外，可以通过以下命令确认是否开启 Smart Install Client 功能：  
switch>show vstack config  
Role: Client (SmartInstall enabled)  
Vstack Director IP address: 0.0.0.0  
switch>show tcp brief all  
TCB Local Address Foreign Address (state)  
0344B794 *.4786 *.* LISTEN  
0350A018 *.443 *.* LISTEN  
03293634 *.443 *.* LISTEN  
03292D9C *.80 *.* LISTEN  
03292504 *.80 *.* LISTEN  
如果您不确定您的漏洞是否受到影响，可以使用Cisco的Cisco IOS Software Checker进行检测：  
https://tools.cisco.com/security/center/softwarechecker.x

## 时间线

**2018-03-29 Cisco和EMBEDI发布漏洞信息**  
 **2018-03-30 360-CERT和360-NetOPS发布漏洞预警**

## 参考链接

> [Cisco Smart Install Remote Code Execution](https://embedi.com/blog/cisco-> smart-install-remote-code-execution/)

  
https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20180328-smi2

本文翻译自https://cert.360.cn
[原文链接](https://cert.360.cn/warning/detail?id=f7d09fffded750e131cda824ef356514)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/103122](/post/id/103122)

安全客 - 有思想的安全新媒体

本文转载自:
[https://cert.360.cn](https://cert.360.cn/warning/detail?id=f7d09fffded750e131cda824ef356514)

如若转载,请注明出处：
<https://cert.360.cn/warning/detail?id=f7d09fffded750e131cda824ef356514>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CVE-2018-0171](/tag/CVE-2018-0171)
  * [拒绝服务攻击](/tag/拒绝服务攻击)
  * [远程命令执行](/tag/远程命令执行)
  * [栈溢出漏洞](/tag/栈溢出漏洞)
  * [思科漏洞](/tag/思科漏洞)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

