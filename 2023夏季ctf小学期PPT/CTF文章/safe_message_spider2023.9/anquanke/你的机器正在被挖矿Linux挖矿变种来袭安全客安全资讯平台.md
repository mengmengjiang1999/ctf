# 你的机器正在被挖矿 Linux挖矿变种来袭

阅读量 **331215**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-04 10:58:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t011a2e88ebcef011e5.jpg)

## 样本简介

近日捕获到一款新型的Linux挖矿病毒变种样本，相关的URL下载信息如下所示：

http://w.3ei.xyz:43768/initdz(服务器已关)

http://w.lazer-n.com:43768/initdz

通过微步在线对服务器URL进行查询，w.3ei.xyz如下所示：

![](https://p3.ssl.qhimg.com/t01f9582a85df7764ec.png)

w.lazer-n.com，如下所示：

![](https://p2.ssl.qhimg.com/t01f60632cce245c965.png)

此挖矿病毒到目前为止已经挖了111个门罗币了，而且还在继续挖矿……

## 详细分析

1.修改主机host文件，如下所示：

![](https://p0.ssl.qhimg.com/t01c185505e0d66fece.png)

在主机host文件中，写入如下内容：

    
    
    echo \"127.0.0.1 mine.moneropool.com\" >> /etc/hosts
    
    echo \"127.0.0.1 xmr.crypto-pool.fr\" >> /etc/hosts
    
    echo \"127.0.0.1 monerohash.com\" >> /etc/hosts
    
    echo \"127.0.0.1 xmrpool.eu\" >> /etc/hosts
    
    echo \"127.0.0.1 pool.noobxmr.com\" >> /etc/hosts
    
    echo \"127.0.0.1 pool.minexmr.cn\" >> /etc/hosts
    
    echo \"127.0.0.1 xmr.poolto.be\" >> /etc/hosts
    
    echo \"127.0.0.1 monerohash.com\" >> /etc/hosts
    
    echo \"127.0.0.1 stratum.viaxmr.com\" >> /etc/hosts
    
    echo \"127.0.0.1 pool.monero.hashvault.pro\" >> /etc/hosts
    
    echo \"127.0.0.1 xmr-us.suprnova.cc\" >> /etc/hosts
    
    echo \"127.0.0.1 de.moriaxmr.com\" >> /etc/hosts
    
    echo \"127.0.0.1 de2.moriaxmr.com\" >> /etc/hosts
    
    echo \"127.0.0.1 fr.minexmr.com\" >> /etc/hosts
    
    echo \"127.0.0.1 de.minexmr.com\" >> /etc/hosts
    
    echo \"127.0.0.1 ca.minexmr.com\" >> /etc/hosts
    
    echo \"127.0.0.1 sg.minexmr.com\" >> /etc/hosts
    
    echo \"127.0.0.1 xmr.bohemianpool.com\" >> /etc/hosts
    
    echo \"127.0.0.1 xmr-usa.dwarfpool.com\" >> /etc/hosts
    
    echo \"127.0.0.1 monero.miners.pro\" >> /etc/hosts
    
    echo \"127.0.0.1 xmr.prohash.net\" >> /etc/hosts
    
    echo \"127.0.0.1 thyrsi.com\" >> /etc/hosts
    
    echo \"127.0.0.1 minerxmr.ru\" >> /etc/hosts
    
    echo \"127.0.0.1 zer0day.ru\" >> /etc/hosts
    
    echo \"127.0.0.1 minergate.com\" >> /etc/hosts
    
    echo \"127.0.0.1 pixeldra.in\" >> /etc/hosts
    
    echo \"220.194.237.43 w.3ei.xyz\" >> /etc/hosts
    
    echo \"220.194.237.43 w.21-3n.xyz\" >> /etc/hosts

2.测试主机是否能联网，如下所示：

![](https://p4.ssl.qhimg.com/t01d64b4fcfff6b6f19.png)

3.检测/etc/zigw、/tmp/zigw、/etc/zjgw等文件是否存在，如果存在，则结束相关进程，删除对应的文件，如下所示：

![](https://p1.ssl.qhimg.com/t01e19cdf68c722ba20.png)

4.判断主机是否拥有root权限，如下所示：

![](https://p5.ssl.qhimg.com/t01eb07151c86ebf5f4.png)

5.如果主机拥有root权限，同时判断/etc目录下是否存在pvds程序，如果不存在则从http://w.lazer-n.com:43768/pvds网站下载挖矿程序到/etc目录下pvds，如下所示：

![](https://p1.ssl.qhimg.com/t01a1efda354bde5d70.png)

挖矿程序，如下所示：

![](https://p2.ssl.qhimg.com/t019b0c241219aed6be.png)

6.判断/etc目录下是否存在httpdz和migrations程序，如果不存在，则从服务器下载相应的挖矿程序，如下所示：

![](https://p2.ssl.qhimg.com/t017cb2983a05b61a9b.png)

7.判断/usr/bin/rmn和/etc/yums两个程序是否存在，如果存在，则从服务器下载挖矿程序，如下所示：

![](https://p3.ssl.qhimg.com/t01f47506afde75fd7e.png)

8.如果不是root权限，则下载相应的挖矿程序到/tmp/pvds、/tmp/httpdz、/tmp/migrations等，如下所示：

![](https://p2.ssl.qhimg.com/t01ebd4aa936feb4c9c.png)

9.能过判断是否为root权限，下载挖矿程序到/etc/initdz或/tmp/initdz，进行挖矿操作，如下所示：

![](https://p3.ssl.qhimg.com/t0163ea98e9bd5be148.png)

10.检测/etc/rzx或/tmp/rzx是否为挖矿程序，如下所示：

![](https://p1.ssl.qhimg.com/t01961b0a02f4013d13.png)

11.启动挖矿程序，如下所示：

![](https://p1.ssl.qhimg.com/t01c4687951a8f1e9a1.png)

捕获到的挖矿流量，如下所示：

![](https://p2.ssl.qhimg.com/t010cf66c1fa64adaba.png)

矿池地址：xmr.f2pool.com:13531

钱包地址：

46j2hc8eJbZZST8L4cpmLdjKKvWnggQVt9HRLYHsCKHUZbuok15X93ag9djxnt2mdpdJPRCsvuHzm92iahdpBxZa3FbBovX

通过网站查询，黑客一共挖了111门罗币了，如下所示：

![](https://p0.ssl.qhimg.com/t01497829f59232a8ad.png)

12.从网站http://w.lazer-n.com:43768/crontab.sh下载crontab.sh，并设置crontab自启动项，如下所示：

![](https://p1.ssl.qhimg.com/t01b70cf86e5c7c582e.png)

设置的cron文件，如下所示：

/var/spool/cron/root、/var/spool/cron、/etc/cron.d

cron的文件内容，如下所示：

![](https://p4.ssl.qhimg.com/t015e581e3c055018da.png)

13.修改SSH文件内容，设置SSH连接密钥，如下所示：

![](https://p1.ssl.qhimg.com/t0156dabb79f9285d83.png)

14.清理其它挖矿等恶意程序和相关日志信息等，如下所示：

![](https://p3.ssl.qhimg.com/t011a64d73aecb46c63.png)

清理libudev.so，如下所示：

![](https://p0.ssl.qhimg.com/t01f34f805edaeb6d17.png)

清理xig挖矿程序，如下所示：

![](https://p4.ssl.qhimg.com/t01991a79cb5e4c69a7.png)

清理qW3xT.2，如下所示：

![](https://p4.ssl.qhimg.com/t0120361e8341422609.png)

清理systemctI，如下所示：

![](https://p3.ssl.qhimg.com/t01d3cb491b3a86fb5d.png)

清理update.sh，如下所示：

![](https://p0.ssl.qhimg.com/t018a1448411d99c0b9.png)

清理kworker，如下所示：

![](https://p4.ssl.qhimg.com/t0143c0525721b3e993.png)

清理rsync，如下所示：

![](https://p4.ssl.qhimg.com/t0139aa77315b44d3e7.png)

清理shm，如下所示：

![](https://p4.ssl.qhimg.com/t01db974e5940f5c0ec.png)

清理kpsmouseds，如下所示：

![](https://p2.ssl.qhimg.com/t015e8f795b86b16440.png)

清理X11unix，如下所示：

![](https://p4.ssl.qhimg.com/t0144e1b1f48abb74a0.png)

15.添加ats系统服务配置，如下所示：

![](https://p1.ssl.qhimg.com/t01b530e2df430296c6.png)

16.清理历史记录，系统日志等，如下所示：

![](https://p3.ssl.qhimg.com/t01c67aa29412179cc4.png)

## 相关IOC

### URL

<http://w.3ei.xyz:43768/initdz>

<http://w.lazer-n.com:43768/initdz>

<http://w.3ei.xyz:43768/pvds>

<http://w.3ei.xyz:43768/pvds2>

<http://w.lazer-n.com:43768/pvds>

<http://w.lazer-n.com:43768/pvds2>

### MD5

06d98dc54c8b01aad4bdc179c569eb88

8438f4abf3bc5844af493d60ea8eb8f6

cea224c7219877a0d602315aa6529ff1

3a72506b186070977fcceeae5fefc444

272d1d7a9f13e15f6b22d9a031695a0d

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181524](/post/id/181524)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [linux](/tag/linux)
  * [挖矿软件](/tag/挖矿软件)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

