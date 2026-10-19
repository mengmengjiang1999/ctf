**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/1a5Isz6KPtWuO9SQkiuGXw>**

### 背景

近日，纽约大学阿布扎比分校的安全研究员Mathy Vanhoef发现了一系列影响巨大的Wi-Fi漏洞，这一系列漏洞被统称为FragAttacks，FragAttacks影响了1997年Wi-Fi技术诞生以来的所有Wi-Fi设备（包括计算机、智能手机、园区网络、家庭路由器、智能家居设备、智能汽车、物联网等等）。

其中三个漏洞影响大多数WiFi设备，属于Wi-Fi 802.11标准帧聚合和帧分片功能中的设计缺陷，而其他漏洞是Wi-Fi产品中的编程错误。

黑客只要在目标设备的Wi-Fi范围内，就能利用FragAttacks漏洞窃取敏感用户数据并执行恶意代码，甚至可以接管整个设备。

启明星辰ADLab第一时间对漏洞进行了分析，并提出了相应的缓解建议。由于WiFi产品的协议栈，包括了Soft Mac及Full
Mac多种实现方案。FragAttacks系列漏洞不仅存在影响操作系统内核、WiFi驱动，还影响WiFi的SOC芯片，所以漏洞的影响长期存在。请及时关注并更新设备供应商的安全更新。

### 修复及缓解建议：

·及时更新设备供应商发布的FragAttacks漏洞安全更新。

·确保您访问的所有网站和在线服务都启用了安全超文本传输协议HTTPS(比如安装HTTPS Everywhere插件)。

·例如在Wi-Fi 6（802.11ax）设备中禁用分片，禁用成对重新生成密钥以及禁用动态分片。

### 漏洞列表及具体影响：

Wi-Fi设计缺陷相关的漏洞包括：

![
](https://images.seebug.org/content/images/2021/05/86aa1949-4188-476d-81ad-5888f4193cba.png-w331s)

Wi-Fi实现相关的漏洞包括：

![
](https://images.seebug.org/content/images/2021/05/f0a6b289-d1c5-4961-b45b-f8fbb8f1532c.png-w331s)

通过这一系列漏洞，攻击者完全可以获得用户的敏感信息或直接控制智能设备，如控制智能电源插座，甚至直接接管网络中存在漏洞的计算机，参见下文参考资料[2]。

### 漏洞分析：

我们选取了在所有设备普遍存在的CVE-2020-24586、CVE-2020-24587、CVE-2020-24588三个设计漏洞进行分析。由于CVE-2020-24588的漏洞影响较大，我们着重进行介绍CVE-2020-24588。

#### 技术背景

由于802.11MAC层协议耗费了相当多开销用作链路的维护，为了提高MAC层的效率，802.11n引入帧聚合技术，报文帧聚合技术包括：A-MSDU(MAC服务数据单元聚合)
及 A-MPDU(MAC协议数据单元聚合)。

A-MSDU允许对目的地及应用都相同的多个A-MSDU子帧进行聚合，聚合后的多个子帧只有一个共同的MAC帧头，当多个子帧聚合到一起后，从而减少了发送每一个802.11报文所需的PLCP
Preamble、PLCP
Header和802.11MAC头的开销，同时减少了应答帧的数量，从而提高无线传输效率。A-MSDU报文帧聚合技术是802.11n协议的强制要求，所有支持802.11n协议的设备都必须支持。

下图示意了在802.11协议栈中，发送端和接收端是如何处理A-MSDU数据的。

![
](https://images.seebug.org/content/images/2021/05/6f45ed61-7d1b-46cb-9f36-4440e9a29d5d.png-w331s)
图1. 802.11协议数据处理流程

在802.11协议栈中，发送端将来自3-7层的网络数据经过数据链路层的LLC子层添加LLC/SNAP头后封装成MSDU(MAC服务数据单元），MSDU经过添加DA、SA、长度及pading后，封装成A-MSDU子帧，在MAC子层的顶层将多个A-MSDU子帧封装成A-MSDU，经MAC子层后，帧数据被添加上MAC头及帧尾封装成802.11数据帧（MPDU），MPDU/PSDU经过物理层添加PLCP
Preamble（PLCP前导码）及PLCP Header（PHY头）。无线侧最后通过射频口将二进制流发送到接收端。

接收端通过相反路径对802.11数据帧进行拆解，最后获得发送端的3-7层的网络数据。

A-MSDU的协议数据组成如图2所示，我们从上到下进行分别说明：

  1. 一个MSDU由LCC/SNAP头、IP头、TCP/UDP头及协议数据Data组成。
  2. MSDU添加DA(目的地址)，SA(源地址)，后续数据长度及Padding(四字节对齐)组成一个MSDU子帧。
  3. 多个MSDU子帧组成一个802.11帧的A-MSDU域。
  4. 802.11数据帧通过QOS Control的A-MSDU Present位来表示这是一个包括A-MSDU域的数据帧。

![ ](https://images.seebug.org/content/images/2021/05/f8ae3cfb-5c3a-4abf-bda0-fb43cd30dfe5.png-w331s) 图2. A-MSDU数据组成示意

在802.11协议中，一个普通的802.11数据帧与A-MSDU数据帧的结构是相同的，只是QOS Control域的A-MSDU Preset位 为1
，则标示了该数据帧是一个A-MSDU数据帧。 A-MSDU Preset位为0，则标示这是普通802.11数据帧。

在802.11协议中WEP及CCMP只保护802.11
MAC的有效载荷，至于802.11帧头以及下层协议的标头则原封不动，也就是说802.11协议中数据帧中QOS
Control并没有加密，这为攻击者提供了攻击入口。

![
](https://images.seebug.org/content/images/2021/05/1aaf2323-fc61-4d1d-88af-d42ab3fc75a3.png-w331s)
图3. CCMP加密的802.11数据帧格式

为防止中间人攻击，IEEE在2011年设计了SPP A-MSDU机制来保护A-MSDU Preset位及A-MSDU的Payload。SPP
A-MSDU通过在RSN capabilities 域中添加SPP A-MSDU Capable及SPP A-MSDU Required来标示是否支持SPP
A-MSDU机制及是否采用SPP A-MSDU机制。

![
](https://images.seebug.org/content/images/2021/05/ecc47fd2-48a1-4943-8a8a-dbe2d881a873.png-w331s)
图4. RSN Capabilities 域数据格式

#### 针对A-MSDU聚合的帧注入攻击(CVE-2020-24588)

虽然有SPP A-MSDU机制来保护A-MSDU Preset位不被篡改，但是在实际的测试中，几乎所有的设备都不遵循SPP
A-MSDU机制，这使得中间人攻击成为可能。

我们假设发送端发送了一个正常的802.11数据帧，这是一个里面封装的是一个普通TCP包，其dst=“192.168.1.2", src="1.2.3.4",
id=34

![ ](https://images.seebug.org/content/images/2021/05/e3d426ea-1cf2-4ae6-89be-af20cab5f0b5.png-w331s) 图5. 原始的802.11数据帧

由于偏移0x18的QOS Control(0200）不受保护，攻击者可以将 QOS Control域中的A-MSDU Preset翻转为1，使得QOS
Control的值为8200，同时在帧末尾注入恶意的A-MSDU子帧2（如下图的红色线标示），最后发送给接收端。

![
](https://images.seebug.org/content/images/2021/05/5e3a794e-224d-412d-a296-45fe46c3c19a.png-w331s)
图6. 篡改后的802.11A-MSDU数据帧

由于QOS Control域中的A-MSDU Preset翻转为1，当接收端接收到数据帧后，会按A-MSDU格式来拆解里面的数据。数据被识别成两个A-MSDU子帧。A-MSDU子帧1中的数据是原始的MSDU数据，所以会被协议栈丢弃，但第二个子帧会被正确解析并处理。这上面的例子中第二个子帧会被识别成ICMP
ping包，接收端会回复一个ICMP echo Reply给发送端。

<https://mp.weixin.qq.com/s/1a5Isz6KPtWuO9SQkiuGXw>

视频1.发送端收到ICMP echo Reply

下图示意了中间人帧注入流程：

![
](https://images.seebug.org/content/images/2021/05/0b5c1efe-153a-48a3-b47a-bc817e79ec69.png-w331s)
图7. 中间人帧注入流程

  1. STA（终端）和AP（热点/无线路由器）信道A（如信道6）, 建立关联
  2. MITM利用多信道中间人技术使得STA认为AP已经切换到信道B（如信道11）。
  3. STA在信道11给 MITM发送加密的Wifi正常数据帧。
  4. MITM将 接收到的Wifi帧QOS域的A-MSDU Preset标示设为1，同时插入篡改的A-MSDU数据。把一个正常的Wifi帧改成一个A-MSDU帧，并注入一个ICMP请求包，并在通道6发给AP。
  5. AP接收到A-MSDU数据帧，AP拆解A-MSDU, 分成多个A-MSDU子帧，其中第一个A-MSDU子帧为非法包，会被丢弃，但后续的MSDU子帧会被系统正常处理。AP会回复收到一个ICMP Echo 应答给MITM.
  6. MITM收到AP的回复后，将接收到的WIFI帧转发给STA，这样STA收到AP回复的ICMP应答。

#### CVE-2020-24588的修复

今年3月Windows发布了相应的补丁，修复了FragAttacks系列漏洞，5月11日Linux也发布了FragAttacks系列漏洞补丁[6]，Linux针对CVE-2020-24588的修复如下：

    
    
    ---     net/wireless/util.c | 3 +++
     1 file changed, 3 insertions(+)
    
    diff --git a/net/wireless/util.c b/net/wireless/util.c
    index 39966a873e40..7ec021a610ae 100644
    --- a/net/wireless/util.c
    +++ b/net/wireless/util.c
    @@ -771,6 +771,9 @@ void ieee80211_amsdu_to_8023s(struct sk_buff *skb, struct sk_buff_head *list,
            remaining = skb->len - offset;
            if (subframe_len > remaining)
                goto purge;
    +       /* mitigate A-MSDU aggregation injection attacks */
    +       if (ether_addr_equal(eth.h_dest, rfc1042_header))
    +           goto purge;
    
            offset += sizeof(struct ethhdr);
            last = remaining <= subframe_len + padding;
    -- 

因为在A-MSDU聚合注入攻击中，需要将普通加密Wi-Fi帧转换为A-MSDU帧。这意味着第一个A-MSDU子帧的前6字节对应于RFC1042的帧头，通过增加判断DA(目标地址)是否和rfc1042_header(\xaa\xaa\x03\x00\x00\x00)一致，如果相等则认为是恶意攻击，可以把这个A-MSDU帧抛弃。

#### 混合密钥攻击(CVE-2020-24587)

![
](https://images.seebug.org/content/images/2021/05/552a2eaf-a3f0-4088-9768-67457190bc15.jpg-w331s)
图8.混合密钥攻击流程

在步骤1当中，攻击者诱导受害者访问受攻击者控制的服务器，通过一些手段，比如指定一个超长的URL，从而使受害者发送的数据包不得不分成两段进行传输，分片的数据包用秘钥k加密，这两个数据包为
和 。而攻击者通过多信道的中间人进行拦截，一旦监测到攻击者指定IP数据包，便将此数据包转发给AP，即 ，AP一旦收到此数据包后，就将其解密后存在内存当中。

在步骤2进行之前，受害者需要与AP重新进行四次握手并协商新的密钥。之后攻击者等待受害者发送包含敏感信息的数据包，即 和
。攻击者将数据包号码为n+1的数据包拦截，并将其序列号修改为s，然后转发给AP，即数据包
。而AP直接把他当作序列号s数据包的第二个分片信息，将他解密后重组成新的数据包，而新的数据包中包含受害者的敏感信息与攻击者指定的IP。于是敏感信息就被发送到受害者控制的服务器上，造成信息泄露。

#### 分片缓存投毒攻击(CVE-2020-24586)：

![
](https://images.seebug.org/content/images/2021/05/5037c047-c928-455d-bf52-023756ee3383.png-w331s)
图9.分片缓存投毒攻击流程

在步骤1中，攻击者嗅探到受害者的MAC地址后，伪造受害者MAC地址去连接AP。这样就可以合法的用受害者的身份在AP的内存中插入分片。

在步骤2中，受害者进行正常的认证工作，此时攻击者发送数据包
，这个数据包中包含攻击者指定的IP数据包。然后AP解密此数据包，并保存在内存中，以受害者的MAC地址作为标识。然后攻击者通过发送解除认证的数据包并断开连接，随后在受害者和AP之间建立一个多信道的中间人。注意此时AP内存中的分片并没有被清除。

之后受害者与AP之间进行正常的连接。此时攻击者只需要等待受害者发送第二个分片，数据包号码为n+1，攻击者将此数据包拦截后，并将此数据包的序列号修改为s，然后其转发给AP，即数据包
，一旦AP收到此数据包，和混合密钥漏洞类似，AP会将此数据包解密，并和之前保存在缓存中的数据包重组成新的数据包，因为这两个数据包包含相同的MAC地址和序列号。最后，AP将重组后的数据包发送给攻击者控制的服务器，从而造成敏感信息泄露。

参考资料：

1.<https://papers.mathyvanhoef.com/usenix2021.pdf>  
2.<https://www.youtube.com/embed/88YZ4061tYw>  
3.<https://www.fragattacks.com/#notpatched>  
4.<https://github.com/vanhoefm/fragattacks>  
5.<https://lore.kernel.org/linux-wireless/20210511180259.159598-1-johannes@sipsolutions.net/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1587/>

