  * [目录]()
  * [1、前言]()
  * [2、几个依赖项]()
    * [2.1、TCP 三次握手]()
    * [2.2、SSL/TLS 握手]()
  * [3、UDP-SPA 技术原理]()
    * [3.2、UDP-SPA 的典型模块组合和典型技术流程]()
    * [3.3、UDP-SPA 实现中各模块关键点]()
    * [3.4、SPACapture 的技术方案选择]()
    * [3.5、SPADynFW 技术方案]()
  * [4、UDP-SPA 方案的变种思考(TCP-OPTION)]()
    * [4.1、UDP-SPA 方案的设计劣势（带外控制）]()
    * [4.2、TCP-Option 方案（从带外转带内）]()
  * [5、TCP-SPA 技术原理]()
    * [5.1、新的选择 — TLS/SSL 层控制]()
    * [5.2、技术原理]()
    * [5.3、TCP-SPA 的优劣势]()
    * [5.4、TCP-SPA 实现机制差异说明]()
  * [6、TCP+UDP 双重 SPA ]()
    * [6.1、安全效果的组合]()
    * [6.2、模块机制的组合]()

## 0、前前言

以前也时不时会在freebuf上看文章，但是一直没发过。忽然发现freebuf可以自由投稿。先把以前在 **同名公众号上写的原创内容** ，挑一部分发一下。

后续新内容会考虑同步在freebuf上发送。

## 1、前言

近些年火热的零信任领域中，一直有零信任三大技术路线SIM的说法， SIM=SDP（Software Defined
Perimeter,软件定义边界）+IAM（Identity and Access Management ,统一身份管理）+MSG（Micro
Segmentation,微分段）。

其中， SDP **主要解决**
用户到业务的南北向访问安全，在近些年疫情、安全、零信任理念驱动等因素影响下，算是零信任领域中更为主要的赛道，大量厂商各显神通，都推出了SDP相关的产品方案。

 **而SDP的关键特征，就是SPA ，可见其重要程度** 。本系列则计划针对SPA进行一些解读，便于大家理解。

注： 零信任理念并不在本系列中展开，后续考虑另设专题讨论。感兴趣的读者可以自行在网络上查找现有材料

[篇1：SPA-Learning-001-零信任之初步了解SPA和SDP-SPA](https://www.freebuf.com/articles/351869.html)

[篇2：SPA-Learning-002-零信任SDP之SPA的核心逻辑与代际之争](https://www.freebuf.com/articles/353462.html)

[篇3-SPA-Learning-003-零信任SDP之SPA
典型方案和技术原理](https://www.freebuf.com/articles/353463.html)

[篇4-SPA-Learning-004-零信任SDP之SPA真的能防止DDOS吗？﻿](https://www.freebuf.com/articles/353464.html)

## 1、前言

在 [SPA-Learning-002-零信任 SDP 之 SPA
的核心逻辑与代际之争](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247484356&idx=1&sn=705f3c5b0c0072d362b42a22a6ce421e&chksm=cfdbfd88f8ac749eae49e52095076547f01e0a5fc6db7d74001263e028032a341eb4e9d32d44&token=1612787612&lang=zh_CN#rd)的
**3、 SPA 的代际之争** 章节中，我们提到了 SPA 从 Port Knocking 开始，有 UDP SPA、TCP SPA、UDP+TCP
SPA 三种关键形态。

那么这三种技术形态的技术原理又有何差异呢？

## 2、几个依赖项

### 2.1、TCP 三次握手

可通才https://en.wikipedia.org/wiki/Handshaking[1]，最终如下图，可以看到，TCP 三次握手环节如下：

1)、client 向服务端发送 SYN 包(SYNbit=1)，同时标记 SEQ=x。由 connect()调用触发，并进入 SYN_SENT 状态

2)、server 向客户端回复 SYN 包(SYNbit=1)，SEQ=y。同包携带 ACK 信息(ACKbit=1)，并设置
ACKnum=x，确认收到了 client 的 SEQ。服务端进入 SYN_RCVD 状态。

3)、客户端答复 ACK 包(ACKbit=1），并且设置 ACKnum=y+1，以示对 server 的 SEQ 确认。客户端进入 ESTAB
建连状态，connect（）函数返回成功

4)、服务端收到数据包确认后，进入 ESTB 状态。同时 accept()函数从 ESTAB 连接队列中返回相应 socket 句柄，供应用层读写

经过上述 3 步流程，可进入 read()/write()读写收发 TCP 数据的状态。

![](https://image.3001.net/images/20221223/1671802224_63a5ad700c49b8dd64b54.png!small)

### 2.2、SSL/TLS 握手

可参考 https://en.wikipedia.org/wiki/Transport_Layer_Security#TLS_handshake[2]，从
TCP 握手开始包含 TLS 握手的流程如下图：

![](https://image.3001.net/images/20221223/1671802225_63a5ad714a8c245ff21f2.png!small)

可以看到，TLS 握手发送的 client Hello，是 TCP 连接中的首个真实数据包。

## 3、UDP-SPA 技术原理

UDP-SPA **指的是** 通过 UDP 发送一个独立、额外的 SPA packet 进行敲门 ，从而实现针对未授权终端，拦截 TCP-SYN
首包，从而使 **TCP 无法建立连接** 的 SPA 方案。其效果及不足可参考 [SPA-Learning-002-零信任 SDP 之 SPA
的核心逻辑与代际之争](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247484356&idx=1&sn=705f3c5b0c0072d362b42a22a6ce421e&chksm=cfdbfd88f8ac749eae49e52095076547f01e0a5fc6db7d74001263e028032a341eb4e9d32d44&token=1612787612&lang=zh_CN#rd)中的
**3.2、第 1 代(标准 SPA) — UDP SPA** 章节。

#### 3.1、零信任 SDP 中的 UDP-SPA 的业务访问流程

下述为 SDP 控制面和数据面分离场景下， **并行部署模式** （控制面和数据面都映射到互联网）的业务流程。

![](https://image.3001.net/images/20221223/1671802227_63a5ad7314473a52c2862.png!small)

#### 3.1.1、线性/串行部署模式业务流程

 **线性/串行部署的关键特征** 是，仅暴露 SDP 数据面至公网。SDP 控制面没有公网 IP，而是由数据面完成 SPA
校验后，代理转发认证请求至控制面。

其业务流程如下图，不文字详述。

值得注意 的是，SDP 数据面和 SDP 控制之间，通常通过\ 设备间互信通道 \ 转发请求。

![](https://image.3001.net/images/20221223/1671802228_63a5ad7447ba4c8663f37.png!small)

### 3.2、UDP-SPA 的典型模块组合和典型技术流程

#### 3.2.1、SPAClient 模块组和 SPADaemon 模块组

> SPAClient 模块组，至少应由如下两个模块组成：

一、SPAMonitor(敲门监控模块):

1)、探测、监听是否 SPA 敲门失败，重新发送敲门包

2)、启动定时器，定时发送敲门包，以实现续期。

二、SPAPacket(敲门发包模块)：

1)、根据 SPA Seed，生成有效敲门包，将设备标识、用户标识等信息存入敲门包内 2)、SPA 包安全机制保障，按约定进行防重放、防伪造机制

> SPADaemon 服务端模块组，至少应由如下模块组成：

一、SPACapture(流量监控模块)：

1)、 从 UDP 监听敲门端口中，读取数据包

二、SPAValidate（敲门校验模块):

1)、校验 SPA 包的格式有效性，无效丢弃

2)、完整性检测，发现篡改丢弃

3)、防重放检测

4)、检查计算机名、设备标识、用户标识，机码/人码匹配

三、SPADynFW（防火墙模块)

1)、支持按指定源 IP 放行 ACL 策略

2)、支持 ACL 策略定时失效

四、SPAAnalyze（异常分析模块)

1)、根据敲门校验结果，分析异常(如种子泄漏、借用、SPA-Flood 攻击等），进行阻断或仅日志记录

五、SPASeedSync(种子同步模块)

1)、由于 SDP 涉及多机组建集群、分布式容灾等，SPA 种子发生吊销、新增、变更等，需要多机同步，保障终端连接任意一个数据面或控制面节点
，都能够得到及时、一致的反馈（如对新增种子能通过校验、过期种子能阻断访问等）。

![](https://image.3001.net/images/20221223/1671802229_63a5ad75a218d81931a6d.png!small)

#### 3.2.2、SPA 典型技术流程

![](https://image.3001.net/images/20221223/1671802230_63a5ad76c205c591508d5.png!small)

### 3.3、UDP-SPA 实现中各模块关键点

从上述流程中，可以看出关键要解决和保障的项如下：

1)、SPACapture 流量抓取模块实现 ：此项会大幅影响稳定性和性能（并发），差的方案和好的方案，性能可能是 10 倍以上的差异。

2)、 SPAValidate 防重放、防篡改机制、防窃取机制 **如何实现。**

3)、SPADynFW 防火墙模块 ：此项主要影响大规则场景下的规则变更可靠性和性能，差的方案，可能会导致规则超过一定规模，则容易变更失败 或者 性能很差

4)、SPASeedSync 种子同步模块 ：这是一个很容易被忽视的模块，会影响 SPA
在不同的部署模式下的种子生效时间、以及可靠性。比如说大规模的用户种子的新增、吊销如何同步？多久同步？异常宕机的处理等等

### 3.4、SPACapture 的技术方案选择

核心实现要求：高性能、高可靠、 静默抓包(三体 ：不要回答、不要回答、不要回答）。

#### 3.4.1、libpcap 方案

libpcap（Packet Capture Library ），即数据包捕获函数库，是 Unix/Linux
平台下的网络数据包捕获函数库。它是一个独立于系统的用户层包捕获的 API 接口，为底层网络监测提供了一个可移植的框架。

这是一个 **系统通用性最优** 的方案，纯应用层即可调用。

说到 libpcap 可能有些人还比较陌生，如果说到 tcpdump，大家就不困了。。是的，tcpdump 也是用的 libpcap 进行抓包。

Libpcap 利用 BSD Packet Filter(BPF)对网卡接收到的链路层数据包进行过滤 ，如果规则命中成功，则会将数据提交给应用层进行处理。

本方案是性能偏低的方案。

#### 3.4.2、XDP 方案

XDP(eXpress Data Path)，为 Linux 内核提供了高性能、可编程的网络数据路径 。由于网络包在还未进入网络协议栈之前就处理，它给
Linux 网络带来了巨大的性能提升（性能比 DPDK 还要高）。

它的速度很快，不足之处是脱离了协议栈，需要自行维护连接跟踪信息、同时不能和 iptables 机制很好结合。

感兴趣的也可参考此处：https://tonydeng.github.io/sdn-handbook/linux/XDP/[3]，或查找一些其他资料，此处暂不展开

![](https://image.3001.net/images/20221223/1671802231_63a5ad77db4b558512b08.png!small)

#### 3.4.3、其他方案

1)、PF_RING：是一个内核和应用层处理网络数据的机制，相比 libpcap 主要是减少了内存拷贝次数，从而提升性能。

2)、DPDK(Intel Data Plane Development Kit)：是一种脱离网卡驱动和 TCP/UDP
协议栈，能直接应用层处理网络数据的机制（避免了应用层和内核的交互），性能很高，多用于大流量网络设备。

3)、NFQUEUE：是`iptables`的一种规则增强, 它用于将网络数据包从内核传给用户态进程,
由用户态进程处理后，再将处置结果发回内核（通过、放行）。

### 3.5、SPADynFW 技术方案

动态防火墙核心实现要求 ：高性能(百万规则）、高可靠

实现 DynFW 也有一些典型方案，分别有：

1)、iptables、ufw：标准的防火墙机制。

2)、ipset：ipset 是 iptables 的一个扩展补充，可以批量设置 IP 列表，再针对列表进行控制，有助于减少 iptables 规则条数。

3)、XDP：同 3.4.2 小节，可以通过 XDP 对数据包进行处理拦截。

## 4、UDP-SPA 方案的变种思考(TCP-OPTION)

### 4.1、UDP-SPA 方案的设计劣势（带外控制）

从效果上，我们可以看到 UDP-SPA 的方案，是通过 UDP 包发送单独的 SPA Packet，校验后才放开 TCP-SYN 包的方式进行的防护。

这个方案是带外控制方案(独立的 UDP 端口命令通道发送 SPA Packet)。 * *

带外控制 **是** 产生敲门放大漏洞的根因。

#### 4.1.1、带外控制需要依赖关联信息(IP）

可以看到如下图：

1)、SPAClient 先发送 SPA Packet 敲门包，针对这个数据包可以进行强校验，判断 OK。

2)、直接发送 TCP-SYN 包，SYN 包本身没有任何 SPA 信息。

![](https://image.3001.net/images/20221223/1671802233_63a5ad791c67848828843.png!small)

如何解决关联问题？可以看到，两者的相关内容，只有 IP 头、UDP 头、TCP 头三部分。

那么我们分别查看这 3 个的数据格式：

 **1)、UDP 头，有 UDP 的源端口、目标端口、长度、校验和。**

![](https://image.3001.net/images/20221223/1671802234_63a5ad7a52b4e6d5afdb3.png!small)

2)、 TCP 头，也有 TCP 的源端口、目标端口、序列号等字段。但是值得注意的是，UDP 的源、目标 端口，极大概论和 TCP 是不同的。

![](https://image.3001.net/images/20221223/1671802235_63a5ad7b6b28e87ae0cc3.png!small)

3)、所以 TCP 头和 UDP 头，无法完成关联 。那么剩余内容，就是 IP 头。IP 头中， **源 IP、目标 IP 是有共性的，可以通过源 IP
来判断两个包是否同一个发送者** 。

![](https://image.3001.net/images/20221223/1671802236_63a5ad7c9d90cc816d9be.png!small)

小结：正因为带外方案，导致需要一个机制能将 **UDP SPA Packet 和 TCP-SYN 建连请求** 进行关联，而这个关联点， **就是源
IP** 。

那么最好就是能想办法解决掉带外控制的问题，从带外转向带内。

### 4.2、TCP-Option 方案（从带外转带内）

那如果有一种方案，能在 TCP-SYN 包之前，携带 SPA 信息，是否就能通过一个数据包来实现 **SPA 控制和连接建连** 了呢？

这个方案，就是 TCP-OPTION。参考
wiki，见：https://en.wikipedia.org/wiki/Transmission_Control_Protocol[4]。

![](https://image.3001.net/images/20221223/1671802237_63a5ad7dc1b283aeed674.png!small)

参考 https://www.iana.org/assignments/tcp-parameters/tcp-parameters.xhtml#tcp-parameters-1[5]，TCP option 有一些预留字段，可以用于在 TCP Header 中存放一些补充数据。

![](https://image.3001.net/images/20221223/1671802239_63a5ad7f2142b6e73d490.png!small)

#### 4.2.1、参考：TOA（TCP Option Address）

TOA（TCP Option Address） ，是 FullNat 模式下能够让后端服务器获取 ClientIP 的一种 **实现** 方式。

部分 CDN、负载均支持 TOA 发送或接收。

1)、阿里云：https://help.aliyun.com/document_detail/52477.html[6]/https://help.aliyun.com/document_detail/119658.html?utm_content=g_1000230851\&spm=5176.20966629.toubu.3.f2991ddcpxxvD1#title-3r0-96m-u8v[7]

![](https://image.3001.net/images/20221223/1671802240_63a5ad80d42ece739193a.png!small)

2)、F5 的 irule 配置 TOA 读取：https://community.f5.com/t5/technical-articles/accessing-tcp-options-from-irules/ta-p/287183[8]

![](https://image.3001.net/images/20221223/1671802242_63a5ad821922e9a4fa3a2.png!small)

#### 4.2.2、TCP-Option 方案的不足

默认内核是不支持设置 253、254 这种保留值，包括 4.2 小节中所述的 76-252 的保留值。

如果你翻阅一下 linux 内核代码，很容易就能发现，linux 内核在`net/ipv4/tcp.c!do_tcp_setsockopt`函数中，
**可以看到并没有为保留值预留操作机制** 。

![](https://image.3001.net/images/20221223/1671802243_63a5ad83c07c56520acd4.png!small)

所以， tcp-option 的不足：

1)、需要内核驱动、系统兼容性和软件环境兼容性差：需要发送者和接收者 ，都需要 **内核驱动** 才能正常完成发送和接收处理。此项在 PC
端，方案偏重，影响软件环境兼容性（比如和同样有内核驱动的安全软件冲突）；在移动端，有实现困难，因为移动端(android/ios) 不允许安装自定义驱动
，难以有效实现。

2)、网络适应性偏差：在互联网上，如果有 TCP 代理节点，则会导致 tcp option 被摘除，导致 TO 方案异常。对于有 CDN、有 LB
负载均衡的场景，几乎不适应。

3)、TCP Option 字节空间有限 ：总共 40 字节，还有一些默认的 tcp option 要填充，留给 SPA Packet
能存放的字节非常有限。

参考 fwknop 的设计决策（见： https://www.cipherdyne.org/fwknop/docs/design-decisions.html[9]），里面还提到两点：

4)、不需要管理员权限：显然，如果使用了 tcp option，是一定需要管理员权限甚至是内核权限

5)、潜在修改原始 TCP 数据包 ，引发部分安全设备的兼容性问题

![](https://image.3001.net/images/20221223/1671802246_63a5ad860af2bb6a4df54.png!small)

## 5、TCP-SPA 技术原理

### 5.1、新的选择 — TLS/SSL 层控制

正是由于 tcp option 自身存在较多的落地问题， **导致无法以带内控制的方式，将 TCP-SYN 包进行拦截** 。

基于 [SPA-Learning-002-零信任 SDP 之 SPA
的核心逻辑与代际之争](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247484356&idx=1&sn=705f3c5b0c0072d362b42a22a6ce421e&chksm=cfdbfd88f8ac749eae49e52095076547f01e0a5fc6db7d74001263e028032a341eb4e9d32d44&token=1612787612&lang=zh_CN#rd)第
1.5 章节，我们其实还可以再上移一层，即在表示层/会话层进行控制(TLS/SSL) 。

![](https://image.3001.net/images/20221223/1671802247_63a5ad8748cfd75b600c2.png!small)

### 5.2、技术原理

方案其实也非常简单，就是在 ClientHello（TCP 数据首包）时，检查是否携带了 SPA Packet， 校验通过则正常返回，失败则拒绝。

![](https://image.3001.net/images/20221223/1671802248_63a5ad88a34637be31644.png!small)

被拦截的效果如下：

![](https://image.3001.net/images/20221223/1671802250_63a5ad8a9fae15f5ae59b.png!small)

#### 5.2.1、通过 wireshark 验证

TCP-SPA 可以通过 wireshark 抓包，对 ClientHello 进行抓取解析，通常可以看到 Extension 扩展字段中，会有
Unknow Type（未知类型），即为新增的 SPA Packet。这里不同厂商实现方式不同，其长度、type 是有所不同的，但是万变不离其宗。

![](https://image.3001.net/images/20221223/1671802252_63a5ad8c02a1ae890c965.png!small)

### 5.3、TCP-SPA 的优劣势

 **优势：**

1)、基于带内控制机制， **规避了敲门放大** 。对网络适应性、软件环境兼容性都能做到极佳。

通过每连接携带的 SPA Packet，使得攻击者无法依据同路由器公网 IP 进行 SPA 绕过。

![](https://image.3001.net/images/20221223/1671802253_63a5ad8dbfa6a0cfff1d8.png!small)

2)、同样由于 **带内控制机制 ，实现了** 连接级 SPA （在连接首包发送 SPA Packet，通过后只放开当前连接）

![](https://image.3001.net/images/20221223/1671802254_63a5ad8ef268b85517015.png!small)

 **劣势：**

1)、 **TCP 握手能够成功，端口未完全隐身**

### 5.4、TCP-SPA 实现机制差异说明

#### 5.4.1、 TCP-SPA VS UDP-SPA 的差异对比及新入

![](https://image.3001.net/images/20221223/1671802255_63a5ad8fe87d40c019d4a.png!small)

相比于 UDP-SPA 定期敲门，TCP-SPA 是 **每一次 TCP 建连时都需要校验 ，如果** 每一条连接校验时 SPA Packet
都要经过复杂计算的话，会非常耗费性能。

#### 5.4.2、TCP-SPA 需引入缓存加速机制

因为上述 SPA Packet 校验频率变密集了， 为了防止 TCP SPA 引入性能瓶颈 ，在技术上需要优化。一种通行的方式，是缓存加速机制 。

所以 TCP-SPA 在逻辑模块上， 需要引入新的模块 ：

SPACache 缓存校验加速模块： 通过精良的设计，使得 TCP-SPA 虽然每连接都携带了 SPA Packet，利用 **缓存加速机制， 在**
校验上无需要每连接都进行完整的校验 ，大幅优化性能。

当然同时也去掉了 SPADynFW 动态防火墙模块 ，不需要再添加防火墙规则。

![](https://image.3001.net/images/20221223/1671802256_63a5ad90ef84d1413e484.png!small)

#### 5.4.3、TCP-SPA 和 UDP-SPA 的性能对比

如下图，可以看到： 1、 **UDP-SPA 相比 TCP-SPA 增加了定时添加 IP 规则** ，会产生删除、新增防火墙规则的性能、资源开销

2、TCP-SPA 相比 UDP-SPA 又增加了每连接、每次校验 SPA Packet 的开销。但是此项可以通过 SPACache
缓存加速模块进行优化，优化效果为：

 **1)、每连接、每次轻量极简校验**

 **2)、定时完整校验**

缓存优化后， **TCP-SPA 理论上性能和 UDP-SPA 相差仿佛，甚至可能略高一线。**

当然，上述只是理论，这也同时取决于开发者的工程能力、编码能力，一份烂的代码，能够将性能下降数倍甚至数十倍。

![](https://image.3001.net/images/20221223/1671802258_63a5ad92188dcb6c12755.png!small)

## 6、TCP+UDP 双重 SPA

TCP+UDP 双重 SP Ａ则是前述 UDP 和 TCP 的组合。

### 6.1、安全效果的组合

参考[SPA-Learning-002-零信任 SDP 之 SPA
的核心逻辑与代际之争](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247484356&idx=1&sn=705f3c5b0c0072d362b42a22a6ce421e&chksm=cfdbfd88f8ac749eae49e52095076547f01e0a5fc6db7d74001263e028032a341eb4e9d32d44&token=1612787612&lang=zh_CN#rd)第
3.4 章节，如下：

1)、相比 UDP-SPA 模式， **双重 SPA 解决了敲门放大漏洞问题** 。

2)、相比 TCP-SPA 模式， **双重 SPA 解决了 4 层漏洞防御，实现了 SDP 端口隐藏。**

![](https://image.3001.net/images/20221223/1671802259_63a5ad931d876994d5fd3.png!small)

### 6.2、模块机制的组合

如下图，可以看到:

1)、相比 UDP-SPA，双重 SPA 需要引入 SPACache 缓存校验机制 ，用于对每连接、每次的 SPA Packet 校验进行优化加速。可见本文
5.4.3 小节

2)、相比 TCP-SPA，双重 SPA 需要引入 SPADynFW 动态防火墙机制 ，以实现 OSI4 层防护（端口隐身）。可见本文第 3.5 小节

![](https://image.3001.net/images/20221223/1671802260_63a5ad94b160d70b34387.png!small)

### 参考资料

[1]

https://en.wikipedia.org/wiki/Handshaking:
https://en.wikipedia.org/wiki/Handshaking

[2]

https://en.wikipedia.org/wiki/Transport_Layer_Security#TLS_handshake:
https://en.wikipedia.org/wiki/Transport_Layer_Security#TLS_handshake

[3]

https://tonydeng.github.io/sdn-handbook/linux/XDP/:
https://tonydeng.github.io/sdn-handbook/linux/XDP/

[4]

https://en.wikipedia.org/wiki/Transmission_Control_Protocol:
https://en.wikipedia.org/wiki/Transmission_Control_Protocol

[5]

https://www.iana.org/assignments/tcp-parameters/tcp-parameters.xhtml#tcp-parameters-1: https://www.iana.org/assignments/tcp-parameters/tcp-parameters.xhtml#tcp-parameters-1

[6]

https://help.aliyun.com/document_detail/52477.html:
https://help.aliyun.com/document_detail/52477.html

[7]

https://help.aliyun.com/document_detail/119658.html?utm_content=g_1000230851&spm=5176.20966629.toubu.3.f2991ddcpxxvD1#title-3r0-96m-u8v:
https://help.aliyun.com/document_detail/119658.html?utm_content=g_1000230851&spm=5176.20966629.toubu.3.f2991ddcpxxvD1#title-3r0-96m-u8v

[8]

https://community.f5.com/t5/technical-articles/accessing-tcp-options-from-irules/ta-p/287183: https://community.f5.com/t5/technical-articles/accessing-tcp-options-from-irules/ta-p/287183

[9]

https://www.cipherdyne.org/fwknop/docs/design-decisions.html:
https://www.cipherdyne.org/fwknop/docs/design-decisions.html

