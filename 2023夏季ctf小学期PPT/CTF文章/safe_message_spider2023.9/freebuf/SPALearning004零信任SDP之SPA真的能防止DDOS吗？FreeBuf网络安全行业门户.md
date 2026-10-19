  * [目录]()
  * [1、前言]()
  * [2、SDP标准的说法变更]()
    * [2.1、SDP 1.0标准中，宣称可防止DDOS]()
    * [2.2、SDP2.0标准的调整]()
  * [3、UDP-SPA缓解DDOS，而非阻止]()
    * [3.1、前情提要]()
    * [3.2、UDP-SPA的DDOS缓解效果]()

## 0、前前言

以前也时不时会在freebuf上看文章，但是一直没发过。忽然发现freebuf可以自由投稿。先把以前在 **同名公众号上写的原创内容** ，挑一部分发一下。

后续新内容会考虑同步在freebuf上发送。

[篇1：SPA-Learning-001-零信任之初步了解SPA和SDP-SPA](https://www.freebuf.com/articles/351869.html)

[篇2：SPA-Learning-002-零信任SDP之SPA的核心逻辑与代际之争](https://www.freebuf.com/articles/353462.html)

[篇3-SPA-Learning-003-零信任SDP之SPA
典型方案和技术原理](https://www.freebuf.com/articles/353463.html)

[篇4-SPA-Learning-004-零信任SDP之SPA真的能防止DDOS吗？﻿](https://www.freebuf.com/articles/353464.html)

## 1、前言

有读者问我，说SPA真的能防止DDOS吗？因为经常听到说法，说SDP可以阻止DDOS，如何理解？

## 2、SDP标准的说法变更

### 2.1、SDP 1.0标准中，宣称可防止DDOS

因为SDP标准中宣称， SDP可防止DDOS攻击。下为 **SDP
1.0（见：https://downloads.cloudsecurityalliance.org/initiatives/sdp/SDP\\_Specification\\_1.0.pdf
[1]）标准截图：**

"SDP可以阻止DDOS攻击，而VPN网关则不会"

![](https://image.3001.net/images/20221223/1671802639_63a5af0f58ffd8a6de053.png!small)

### 2.2、SDP2.0标准的调整

如下图，在\ 《SDP Specification 2.0》
（见：https://www.c-csa.cn/u\\_file/photo/20210624/fe0730576f.pdf[2]）的 “Single
Packet Authorization (SPA)”\ 章节中有如下描述：

验证一个入站的SPA包，是轻量级计算，从而提高了SDP系统针对DDoS攻击的弹性。

![](https://image.3001.net/images/20221223/1671802640_63a5af10db73e80bea1ce.png!small)

可以看到，SDP标准2.0在DDOS的说明上变得更为严谨了。

## 3、UDP-SPA缓解DDOS，而非阻止

### 3.1、前情提要

参考 SPA-Learning-002-零信任SDP之SPA的核心逻辑与代际之争[3]的1.4章节，从OSI模型来理解，UDP-SPA主要
**能够起到一定防护作用的是OSI4层及以上的DDOS攻击(即TCP-SYN Flood或TLS Flood、HTTP-Flood)。**

![](https://image.3001.net/images/20221223/1671802641_63a5af11e1a5def4fa1fa.png!small)

### 3.2、UDP-SPA的DDOS缓解效果

UDP-SPA的DDOS防护主要分为两大类：降低攻击意愿、开销转换。

#### 3.2.1、降低攻击意愿

\ 【信息隐藏】如果攻击者，不是刻意攻击，只是想扫描尝试一下：\ 因为端口隐身的，信息不对称，攻击者认为该IP没有服务， **会放弃攻击**
。这个就相当于是将自身隐藏在丛林之中，攻击者不知道你的存在，所以可能会放弃攻击，或者攻破方向。

\ 【提高难度】\ 由于SPA格式是二进制的而且难以分析，不是普适的web HTTP，攻击者即使知道受SPA保护，也可能会放弃攻击。

#### 3.2.2、开销转换

**攻击者知道SDP的IP地址和端口(受SPA保护)：但是由于SPA格式较为复杂，且不利于调试，如果攻击者水平不行，没办法伪造出有效的SPA包，那么就有可能在格式校验时，就被拦截丢包**
。此时，\ 防ddos性能通常高于TCP-SYN包的内核处理，\ 从而起到缓解DDOS的作用

#### 3.2.3、什么情况下DDOS会缓解失败？

 **攻击者如果水平OK，模拟出一个比较真的SPA包** ，此时SPA服务就要做比较多的事情(下为典型举例）：
**a)、校验长度、格式****b)、校验加密算法、checksum校验和**

 **c)、防重放检测 d)、校验SPA码是否存在、有效未过期等**

 **e)、检测SPA码是否该用户所能够使用 f)、打印日志（写文件、写syslog)**

若上述事情逐步执行，当 **SPA校验的性能和资源开销** 高于 **TCP-SYN建连** 时，TCP DDOS就缓解失败了。

#### 3.2.4、一种特殊情况：理论和落地的区别

当然，也有特殊情况， **一个好的程序员/开发团队影响也很大，差的编码和设计，和** 好的编码设计，可能性能 **会相差数倍甚至几十倍**
，可能导致仅做初步校验，开销就高于TCP-SYN建连开销，此时， **则该SPA实现在实际上毫无防DDOS的作用。**

### 参考资料

[1]

https://downloads.cloudsecurityalliance.org/initiatives/sdp/SDP_Specification_1.0.pdf:
https://downloads.cloudsecurityalliance.org/initiatives/sdp/SDP_Specification_1.0.pdf

[2]

https://www.c-csa.cn/u_file/photo/20210624/fe0730576f.pdf:
https://www.c-csa.cn/u_file/photo/20210624/fe0730576f.pdf

[3]

SPA-Learning-002-零信任SDP之SPA的核心逻辑与代际之争:
https://www.wolai.com/jznHLFgsUdaBaLSqRRvFYt.md

