# VPNFilter-新型IoT Botnet深度解析

阅读量 **221964**

发布时间 : 2018-05-31 11:04:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01cc7fca2c9cf06f8d.png)

报告编号： 2018-05-30

报告来源： 360CERT

报告作者： hjy, redrain

更新日期： 2018-05-30

## 0x00 事件概述

2018年5月23日，Cisco Talos团队披露了一起名为”VPNFilter”的IoT
Botnet事件，360CERT团队进行了详细的事件跟踪，并形成本文分析。

VPNFilter是一个通过IoT设备漏洞组建Botnet，多阶段，多平台，模块化，多功能的恶意网络攻击行动，从目前掌握的情况，总共有三个阶段。

**第一阶段** ，作为dropper获得感染设备的持续化访问权限，为第二阶段打开入口，该阶段采取了很强的C2隐藏行为和安全对抗行为。  
 **第二阶段** ，作为信息收集角色和模块功能平台，能对设备文件系统，设备常规信息收集，并提供命令执行能力和设备管理能力，并且在某些平台中实现了自我销毁。  
 **第三阶段**
，作为第二阶段的恶意功能模块下发，为第二阶段提供了更有目的性的攻击行为能力，截至目前，我们所掌握到的两个插件，一个提供tor通信，另一个用于数据包嗅探。

**关于VPNFilter特点描述**

  * 具有强对抗性和周密计划性
  * 多阶段执行
  * Dropper通过图床进行上下行
  * 采用和BlackEnergy相似的变种RC4算法对信息加密（来自Talos的观点）
  * 利用图片EXIF获取C2
  * C2通过Tor流量进行交互
  * 通过利用Linksys、Mikrotik、Netgear、TP-Link、QNAP的相关漏洞进行传播感染

**基础关联情况**

![](https://p403.ssl.qhimgs4.com/t01b31bf5a061055e27.png)

数据来源于360-netlab

**VPNFilter感染时间轴**

![](https://p403.ssl.qhimgs4.com/t01960a74736c74f551.png)

## 0x01 stage1分析

cisco报告中stage1的样本有2个，1个为MIPS架构，1个为x86架构。我们重点分析了x86架构的样本(SHA256:0e0094d9bd396a6594da8e21911a3982cd737b445f591581560d766755097d92)。

样本最初于2017年6月12日被提交到VirusTotal，文件名为C:\Users\chli\Documents\qsync.php。

![](https://p403.ssl.qhimgs4.com/t01c081853aab8e29a1.png)

设置守护进程。

![](https://p403.ssl.qhimgs4.com/t0187beaaeafe926d05.png)

通过写crontab实现持久化，这在IOT病毒中还是第一次出现。crontab格式为{minute}{hour}{day-of-month}{month}{day-of-week}， _/5_ *表示每5分钟执行一次。

![](https://p403.ssl.qhimgs4.com/t01e0549904d50d5a60.png)

样本中的关键字符串都经过了变形的RC4算法加密，这也是将其与BlackEnergy关联起来的重要原因之一。

![](https://p403.ssl.qhimgs4.com/t0183811552e57f6923.png)

标准的RC4算法中对S盒的初始化如下：

![](https://p403.ssl.qhimgs4.com/t018342e28dedd6641b.png)

样本的RC4算法中对S盒的初始化如下：

![](https://p403.ssl.qhimgs4.com/t0135fe8b0d3562a3b1.png)

样本中的算法实际上把swap换成了异或，key是硬编码的%^:d。对12个被加密的字符串解密后的结果如下。

    
    
    /var/run/client.crt
    /var/run/client.key
    /var/run/client_ca.crt
    0.3.9qa
    /var/run/msvf.pid
    <http://toknowall.com/manage/content/update.php>
    /var/vpnfilter
    /update/test
    <http://photobucket.com/user/nikkireed11/library>
    <http://photobucket.com/user/kmila302/library>
    <http://photobucket.com/user/lisabraun87/library>
    <http://photobucket.com/user/katyperry45/library>
    

样本首先尝试从photobucket.com下载图片，从EXIF的经纬度中提取C2地址。如果失败尝试从toknowall.com/manage/content/update.php下载图片，重复同样的操作。对toknowall.com的历史解析如下。

![](https://p403.ssl.qhimgs4.com/t01c5e92afd14780192.png)

忽略Cloudflare，看到历史解析记录188.165.218.31，直接访问上面解密后出来的188.165.218.31/manage/content/update.php。现在C2地址失效了，看备份web.archive.org/web/20180509165520/toknowall.com/manage/content/update.php。

![](https://p403.ssl.qhimgs4.com/t01d83456cd3c07eb13.png)

可以看出来是个图片。

![](https://p403.ssl.qhimgs4.com/t01c9347a6f28ece960.png)

查看EXIF。

    
    
    GPSLatitude     1193143    deg 55' 21.00"
    GPSLongitude    4296160226 deg 47' 54.00"
    

在样本中通过0x08049160处的函数实现还原出C2地址操作：

![](https://p403.ssl.qhimgs4.com/t01a614787851d63c39.png)

    
    
    const char lat[] = "97 30 1193143"; // from Exif data
    const char lon[] = "4294967178 140 4294967274"; // from Exif data
    int o1p1, o1p2, o2p1, o3p1, o3p2, o4p1;
    uint8_t octets[4];
    
    sscanf(lat, "%d %d %d", &o1p2, &o1p1, &o2p1);
    sscanf(lon, "%d %d %d", &o3p2, &o3p1, &o4p1);
    octets[0] = o1p1 + ( o1p2 + 0x5A );
    octets[1] = o2p1 + ( o1p2 + 0x5A );
    octets[2] = o3p1 + ( o3p2 + 0xB4 );
    octets[3] = o4p1 + ( o3p2 + 0xB4 );
    
    printf("%u.%u.%u.%u\n", octets[0], octets[1], octets[2], octets[3]);
    

还原出来C2地址217.12.202.40，相关历史如下。

    
    
    时间          域名
    2017-05-15    [www.redstargel.ru](www.redstargel.ru)
    2017-05-07    redstargel.ru  
    2016-10-24    redstargel.ru  
    2016-10-22    jojoran.ru  
    2016-08-03    jojoran.ru  
    2016-05-22    bellasweets.ru  
    2016-05-21    bellasweets.ru  
    2016-05-19    bellasweets.ru  
    2016-05-15    bellasweets.ru  
    2016-05-08    bellasweets.ru  
    2016-05-07    bellasweets.ru  
    2016-04-23    bellasweets.ru  
    2016-03-14    bellasweets.ru  
    2016-03-04    bellasweets.ru  
    2016-03-03    bellasweets.ru  
    2016-03-02    bellasweets.ru  
    2015-12-26    bellasweets.ru  
    2015-12-25    bellasweets.ru  
    2015-12-24    bellasweets.ru  
    2015-12-03    bellasweets.ru  
    2015-11-20    bellasweets.ru  
    2015-11-19    bludmaster.ru  
    2015-11-01    bellasweets.ru  
    2015-10-31    bellasweets.ru  
    

如果两次图片下载都失败了，则监听本地socket，判断IP、magic number等，从数据包中提取C2地址。

![](https://p403.ssl.qhimgs4.com/t01e244b42d030ad57c.png)

确认从C2地址下载的文件大于1000字节。

![](https://p403.ssl.qhimgs4.com/t0136b8dc9d360fe7a3.png)

chmod511使下载的文件具有可执行权限， 然后通过sys_execve系统调用执行。

![](https://p403.ssl.qhimgs4.com/t013c861705d1038795.png)

## 0x02 stage2分析

cisco报告中stage2的样本有8个，2个为MIPS架构，2个为ARM架构，3个为x86架构。在3个x86架构的样本中，有一个(SHA256:9683b04123d7e9fe4c8c26c69b09c2233f7e1440f828837422ce330040782d17)和其它两个差别较大。因为该样本是一个调试样本，包含了一些调试信息。

![](https://p403.ssl.qhimgs4.com/t01b07da537242eec75.jpeg)

![](https://p403.ssl.qhimgs4.com/t0199c7c775053359b6.jpeg)

![](https://p403.ssl.qhimgs4.com/t014ea6c8849f7ec9f4.jpeg)

根据调试信息，可以非常清晰看到stage2的执行流程。

该调试样本首先初始化之后使用和stage1同样的算法和密钥解密出字符串，然后等待stage3的tor模块进行通信。将ip地址、mac地址等信息整理成json格式的数据，发给C2地址217.12.202.40，94.242.222.68和91.121.109.209。

继续分析不包含调试信息的样本(SHA256:8a20dc9538d639623878a3d3d18d88da8b635ea52e5e2d0c2cce4a8c5a703db1)，可以看到创建了一个模块目录/var/run/vpnfilterm和一个工作目录/var/run/vpnfilterw(目录名不是固定的，和文件名有关，比如这里vpnfilter是文件名)。

![](https://p403.ssl.qhimgs4.com/t0186b22bf3642efdee.png)

接收指令并执行的部分如下。

![](https://p403.ssl.qhimgs4.com/t019979fe309020b2aa.png)

download命令能下载文件到/var/tmp/vpn.tmp目录。

![](https://p403.ssl.qhimgs4.com/t017c5499d30ee68607.png)

restart命令能通过sys_exit系统调用结束当前进程。

![](https://p403.ssl.qhimgs4.com/t0187bc0ea0c15557db.png)

reboot命令能通过sys_reboot系统调用重启系统。

![](https://p403.ssl.qhimgs4.com/t019e1fbbb6302e09c1.png)

copy命令能读取系统上的文件。

![](https://p403.ssl.qhimgs4.com/t010eb706f97d24c6a3.png)

exec命令能调用下面这些解释器执行命令。

    
    
    /bin/sh
    /bin/ash
    /bin/bash
    /bin/shell
    

![](https://p403.ssl.qhimgs4.com/t01029c8b03a8f3ea21.png)

该样本和调试样本相比，除了不打印调试信息之外还有下面这些区别。

1.解密字符串虽然还是使用的和stage1相同的算法，但是key是g&*kdj$dg0_@@7’x。

![](https://p403.ssl.qhimgs4.com/t014b1eb0527a2776f5.png)

2.会将输入输出重定向到/dev/null，也就是不显示输入输出，并且通过sys_unlink系统调用删除自己。

![](https://p403.ssl.qhimgs4.com/t01a1d478a7653bbc24.png)

![](https://p403.ssl.qhimgs4.com/t01411d9d55cf963eb7.png)

3.不同于调试样本中使用固定的user agent，该样本每次从下列9个user agent中随机选择。

![](https://p403.ssl.qhimgs4.com/t014c57f4a5d7928faa.png)

    
    
    Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:52.0) Gecko/20100101 Firefox/52.0
    Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0
    curl/7.47.0
    Wget/1.17.1 (linux-gnu)
    git/2.7.4
    Google Chrome/64.0.3282.140 Windows
    Google Chrome/64.0.3282.140 Linux
    Lynx/2.8.8pre.4 libwww-FM/2.14
    python-requests/2.18.4
    

## 0x03 stage3分析

cisco报告中stage3的样本有2个，1个为MIPS架构，主要用于数据包嗅探；1个为x86架构，主要用于tor通信。我们重点分析了MIPS架构的样本(SHA256:f8286e29faa67ec765ae0244862f6b7914fcdde10423f96595cb84ad5cc6b344)。

样本中查找了数据包中下面这些字段：

1.tmUnblock.cgi

![](https://p403.ssl.qhimgs4.com/t0104bb17952f65b464.png)

tmUnblock.cgi是cisco/linksys路由器中的一个模块，随手一搜可以发现该模块包含大量漏洞，并且之前也被各种病毒利用。

![](https://p403.ssl.qhimgs4.com/t014204025aebe4341a.png)

![](https://p403.ssl.qhimgs4.com/t013ebf81355bf8e4c6.png)

2.*modbus*\n%s:%uh->%s:%hu

![](https://p403.ssl.qhimgs4.com/t016200a0b7c02d4c5b.png)

Modbus是施耐德电气发明的一个总线协议。

3.User=/Name=/Login=/Pass=等等

![](https://p403.ssl.qhimgs4.com/t01d768174881b0eb28.png)

这些都是与HTTP BASIC认证相关的字段，查找这些字段能够获取登录凭证。

## 0x04 后续

在22日Talos披露报告之前，FBI当局即表示接管控制了一个大型IoT Botnet，并认为和APT-28组织的相关行动有关：

得出这一结论的主要来源是Talos认为在stage1部分采用了和此前BlackEnergy相似的RC4变种算法，即替换swap为异或，因为这样的变种算法极为少见且出现在BlackEnergy中习惯使用，所以能形成重合观点。
但由于BlackEnergy行动的披露，极有可能类似实现被其他组织重用，所以我们认为并不能完全作为确凿证据相关，于是我们展开了调查。

我们通过对BlackEnergy的历史行动研究发现，早在2014年和BlackEnergy的相关行动就能看出其已经着手IoT
Botnet组建，且也是通过分段化的形式逐步构建僵尸网络，这样的大规模行动在APT行为里并不常见。  
根据VPNFilter三个阶段的行为，我们并不认为这是一个简单粗暴的IoT
Botnet，攻击者意图构建一个广泛的，有自我隐藏能力，可以灵活提供攻击能力的大型恶意软件族群，由stage3的动作可以看出攻击者有极强的目的性。

我们在此基础上虽然无法判断是否是APT-28的实锤，但是一定能得出的结论是，VPNFilter是一个高度工程化，有周密计划和目的性的大型精巧的攻击行动。

## 0x05 相关IoC

**STAGE1 dropper url:**

    
    
    photobucket[.]com/user/nikkireed11/library
    photobucket[.]com/user/kmila302/library
    photobucket[.]com/user/lisabraun87/library
    photobucket[.]com/user/eva_green1/library
    photobucket[.]com/user/monicabelci4/library
    photobucket[.]com/user/katyperry45/library
    photobucket[.]com/user/saragray1/library
    photobucket[.]com/user/millerfred/library
    photobucket[.]com/user/jeniferaniston1/library
    photobucket[.]com/user/amandaseyfried1/library
    photobucket[.]com/user/suwe8/library
    photobucket[.]com/user/bob7301/library
    toknowall[.]com
    

**STAGE2 C2:**

    
    
    91.121.109[.]209
    217.12.202[.]40
    94.242.222[.]68
    82.118.242[.]124
    46.151.209[.]33
    217.79.179[.]14
    91.214.203[.]144
    95.211.198[.]231
    195.154.180[.]60
    5.149.250[.]54
    91.200.13[.]76
    94.185.80[.]82
    62.210.180[.]229
    api.ipify[.]org?format=json
    zuh3vcyskd4gipkm[.]onion/bin32/update.php
    tljmmy4vmkqbdof4[.]onion/bin32/update.php
    6b57dcnonk2edf5a[.]onion/bin32/update.php
    6b57dcnonk2edf5a[.]onion/bin32/update.php
    

**Malware**

STAGE1

50ac4fcd3fbc8abcaa766449841b3a0a684b3e217fc40935f1ac22c34c58a9ec
0e0094d9bd396a6594da8e21911a3982cd737b445f591581560d766755097d92

STAGE2

9683b04123d7e9fe4c8c26c69b09c2233f7e1440f828837422ce330040782d17
d6097e942dd0fdc1fb28ec1814780e6ecc169ec6d24f9954e71954eedbc4c70e
4b03288e9e44d214426a02327223b5e516b1ea29ce72fa25a2fcef9aa65c4b0b
9eb6c779dbad1b717caa462d8e040852759436ed79cc2172692339bc62432387
37e29b0ea7a9b97597385a12f525e13c3a7d02ba4161a6946f2a7d978cc045b4
776cb9a7a9f5afbaffdd4dbd052c6420030b2c7c3058c1455e0a79df0e6f7a1d
8a20dc9538d639623878a3d3d18d88da8b635ea52e5e2d0c2cce4a8c5a703db1
0649fda8888d701eb2f91e6e0a05a2e2be714f564497c44a3813082ef8ff250b

STAGE3

f8286e29faa67ec765ae0244862f6b7914fcdde10423f96595cb84ad5cc6b344
afd281639e26a717aead65b1886f98d6d6c258736016023b4e59de30b7348719

## 0x06 时间线

**2018-05-23** Cisco Talos披露VPNFilter事件

**2018-05-30** 360CERT发布对病毒的详细分析

## 0x07 参考链接

  1. <https://blog.talosintelligence.com/2018/05/VPNFilter.html>
  2. <http://www.documentcloud.org/documents/4482917-FBI-Seizure-Affidavit.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/146625](/post/id/146625)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [网络攻击](/tag/网络攻击)
  * [VPNFilter](/tag/VPNFilter)
  * [IoT Botnet事件](/tag/IoT Botnet事件)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

