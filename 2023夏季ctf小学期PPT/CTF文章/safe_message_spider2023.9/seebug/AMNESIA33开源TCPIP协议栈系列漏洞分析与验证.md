**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/UWeFBK3E1Zs4cTcMl4UU3A>**

## 一、前言

近期，国外安全研究人员在多个被广泛使用的开源TCP/IP协议栈发现了多个漏洞，这一系列漏洞统称为AMNESIA33。这些漏洞广泛存在于嵌入式和物联网设备中，影响了多个行业领域（包括医疗、运输、能源、电信、工业控制、零售和商业等），目前已知范围内涉及了超150家供应商以及数以百万计的设备。与URGEN11和Ripple20不同的是，AMNESIA33影响的是多个开源TCP/IP协议栈，因此这些漏洞可以悄无声息的地影响到无数个代码库、开发团队与各个公司的产品。目前已知的漏洞涉及到了智能家居、工厂PLC、SCADA设备与工控交换机，电力监控等设备。

这些漏洞存在于uIP、FNET、picoTCP和Nut/Net等开源协议栈上，影响TCP/IP协议栈的多个组件，包括DNS、IPv6、IPv4、TCP、ICMP、LLMNR和mDNS等。其中包括多个严重漏洞，它们的CVE编号分别为CVE-2020-17437、CVE-2020-17443、CVE-2020-24338、CVE-2020-24336、CVE-2020-25111。

CVE-2020-17437（CVSS评分8.2）、CVE-2020-17443（CVSS评分8.2）可导致设备拒绝服务。CVE-2020-24338、CVE-2020-24336、CVE-2020-25111（这三个CVSS评分均为9.8）都可导致远程代码执行(RCE)。其它28个漏洞的严重程度各异，CVSS评分分别从4到8.2。

由于IoT、OT、IT设备供应链的特性，漏洞影响的设备众多，影响范围广且持续时间长，漏洞修复的实施较困难。同时，由于uIP、picoTCP开源协议栈已经不再维护，所以部分漏洞没有补丁，很多产品只能寻找替代技术方案或者是增加防范措施。

因此，启明星辰ADLab对相关漏洞进行了分析，并成功复现了多个漏洞，开发了AMNESIA33相关漏洞检测技术，并提取了流量监控特征，这些技术正在应用到我们的安全产品中。为了缓解漏洞的影响，我们提出了下列防范建议。

## 二、防范建议

**对于这些漏洞的防范缓解措施，我们建议采取如下几个措施：**

（1）配置内网设备的DNS服务器为内网DNS服务器。

（2）如不必要，请关闭IPv6设置。

（3）利用漏扫产品识别出采用问题协议栈的设备资产，对组织内可能存在问题的IoT,OT和IT设备进行风险评估。

（4）防火墙及IPS产品加入AMNESIA33漏洞攻击识别特征，监控恶意流量。

（5）如不必要，设备不要暴露在公网。

（6）尽可能更新相关受影响协议栈到最新版本。

下表是部分已经修复的协议栈及版本

TCP/IP协议栈 | 修复版本  
---|---  
FNET | 4.70及以上  
uIP-Contiki-NG | 4.6.0及以上  
Nut/Net | 5.1及以上  
  
CISA联盟分享了13个涉及到AMNESIA33漏洞的公司的产品修复建议，包括了Microchip、Siemens等公司的产品，详见参考链接[5]。

## 三、相关概念介绍

1、DNS协议解析

DNS的请求和响应的基本单位是DNS报文（Message）。请求和响应的DNS报文结构是完全相同的，每个报文都由以下五段（Section）构成：

![](https://images.seebug.org/content/images/2020/12/30819b24-a853-4775-83ff-e1ed2a7d3ec9.png-w331s)
DNS
Header是每个DNS报文都必须拥有的一部分，它的长度固定为12个字节。Question部分存放的是向服务器查询的域名数据，一般情况下它只有一条Entry。每个Entry的格式是相同的，如下所示：

![](https://images.seebug.org/content/images/2020/12/9cdb921c-5eee-4891-b187-dd24841d84e3.png-w331s)

QNAME是由labels序列构成的域名。QNAME的格式使用DNS标准名称表示法。这个字段是变长的，因此有可能出现奇数个字节，但不进行补齐。DNS使用一种标准格式对域名进行编码。它由一系列的label（和域名中用.分割的label不同）构成。每个label首字节的高两位用于表示label的类型。RFC1035中分配了四个里面的两个，分别是：00表示的普通label，11（0xC0）表示的压缩label。

Answer、Authority和Additional三个段的格式是完全相同的，都是由零至多条Resource
Record（资源记录）构成。这些资源记录因为不同的用途而被分开存放。Answer对应查询请求中的Question，Question中的请求查询结果会在Answer中给出，如果一个响应报文的Answer为空，说明这次查询没有直接获得结果。

RR(Resource Record)资源记录是DNS系统中非常重要的一部分，它拥有一个变长的结构，具体格式如下：

![](https://images.seebug.org/content/images/2020/12/9c33a01d-7e97-4cef-8b36-21c6eaf871cd.png-w331s)

NAME：它指定该条记录对应的是哪个域名，格式使用DNS标准名称表示法

TYPE：资源记录的类型。

CLASS：对应Question的QCLASS，指定请求的类型，常用值为IN，值为0x001。

TTL(Time To
Live)资源的有效期：表示你可以将该条RR缓存TLL秒，TTL为0表示该RR不能被缓存。TTL是一个4字节有符号数，但是只使用它大于等于0的部分。

RDLENGTH：一个两字节非负整数，用于指定RDATA部分的长度（字节数）。

RDATA：表示一个长度和结构都可变的字段，它的具体结构取决于TYPE字段指定的资源类型。

DNS响应包如下图所示：

![](https://images.seebug.org/content/images/2020/12/931788cf-c5c4-405c-94a8-8a88974f46cd.png-w331s)
从上图中可知，该Answers区段中存在9个资源记录，红框中表示的是主机地址（A类型）资源记录。

域标签label在DNS数据包里被编码，每个普通标签的第一个字节代表这个标签的长度，剩下的字母数字字符为标签本身(一些特殊字符也是可以的)，但是最终结尾的字符一定是以空字节结尾(即0x00)，用来表示域名的结束。举个例子，如下图所示，域标签第一个字符是0x03，这代表第一个标签长度为3(即0x77
0x77 0x77 == “www”)，同理，0x62 0x61 0x69 0x64 0x75 == “baidu”，最后可以看到以0x00结尾。

![](https://images.seebug.org/content/images/2020/12/91b633aa-b0b0-474e-bb3c-d06d55580ed5.png-w331s)

2、TCP紧急模式

为了发送重要协议数据,TCP提供了一种称为紧急模式(urgentmode)的机制，TCP协议在数据段中设置URG位,表示进入紧急模式。通过设置紧急模式，发送方可以在发送队列中优先发送这部分的数据，而且不用在发送队列中排队，而接收方可以对紧急模式采取特殊的处理。这种方式数据不容易接受被阻塞,服务器端程序会优先接受这些紧急的数据，而不用进行排队处理。在TCP报文中定义了两个字段来标示紧急模式，一个URG标志，该标志表示报文中有紧急数据，另一个标志是紧急指针，它标示紧急数据在传输数据中偏移位置。如下图所示：

![](https://images.seebug.org/content/images/2020/12/ab212b73-b931-4bc9-b8c0-2ea543e2c7e4.png-w331s)

## 四、漏洞分析

下面我们对几个CVSS评分较高的漏洞进行分析：

**1、CVE-2020-17437**

CVE-2020-17437存在于uIP协议栈的uip.c文件的uip_process函数中，该函数主要是处理ip/tcp报文，下图是uIP协议栈对TCP报文中带有TCP_URG紧急指针标识时的处理代码，如果编译时配置了UIP_URGDATA，则程序会走到下面的if分支，对紧急指针数据进行专门处理。

但是在默认情况下，UIP_URGDATA并没有配置。代码会进入到else分支，程序会跳过处理紧急指针数据，并修改uip_len的数值。程序在修改uip_len的时候并没有判断紧急指针的值，当uip_len的值特别小，而紧急指针的值urgp
特别大时，就会引起整数溢出，导致设备重启或者是越界读写。

![](https://images.seebug.org/content/images/2020/12/0f9e1dc7-edc1-4a9a-b887-c6a6d7bd2966.png-w331s)

**2、CVE-2020-24338**

该漏洞出现在picoTCP/IP协议栈中解析域名label的pico_dns_decompress_name()函数中，该函数具体实现如下代码所示：

![](https://images.seebug.org/content/images/2020/12/7b4e1a6c-98eb-4190-940e-0942ddbc459b.png-w331s)

第95、96行初始化iterator，name指向待解压缩的labels，dest_iterator指向存放解压出来的labels的缓冲区，大小为256字节。第97行开始为while循环，读取到字符串结尾空字节退出。第98行，通过iterator&0xC0判断label类型，如果为压缩label，则通过packet定位到普通label所在的位置，如果为普通label直接进入else代码块中，第107行，调用memcpy将普通label拷贝到dest_iterator中。我们知道dest_iterator缓冲区大小只有256字节，而while循环退出条件为读到字符串结尾空字节，因此当name长度超过256字节时，导致dest_iterator缓冲区溢出。

**3、CVE-2020-24336**

该漏洞出现在contiki协议栈中的ip64_dns64_4to6()中，该函数功能是将ipv4类型的DNS数据包转换成ipv6类型的DNS数据包，关键代码如下：

![](https://images.seebug.org/content/images/2020/12/5e8c45b7-d64c-475c-a175-128d9302f2f7.png-w331s)

遍历Answer区段并更新到ipv6类型的Answer区段中。从第209行开始转换资源记录，具体实现代码如下所示：

![](https://images.seebug.org/content/images/2020/12/86110122-554e-4869-b15b-fcef42f4e8ed.png-w331s)

首先判断TYPE是否是DNS_TYPE_A，DNS_TYPE_A表示该资源记录为ipv4主机地址，然后将对应区段拷贝到acopy中。第220行，从资源记录中直接取RDLENGTH，前文已介绍，该区段表征RDATA的长度。第227行，判断len长度是否等于4，这里正常情况，len应该为4，因为ipv4地址长度为4个字节。如果len不等于4，则进入else语句中，直接调用memcpy进行RDATA数据拷贝。这里是存在问题的，Ipv4主机地址长度不等于4，并没有验证主机地址的合理性而且len最大为0xFFFF，直接拷贝可能导致缓冲区溢出。

**4、CVE-2020-25111**

在使用Nut/Net协议栈的设备中，NutDnsGetResourceAll()是处理DNS请求的函数，其中处理DNS答复的函数是DecodeDnsQuestion()，处理域标签的函数是ScanName()，漏洞就出现在ScanName()函数中。如下图所示，cp为指向域名第一个字节的指针(即第一个域标签的长度字节)，
_npp为即将被解析的域名buffer，通过strlen()将整个域名长度赋值给rc,然后基于rc分配_ npp
buffer，之后通过一个while，循环处理每一个label。问题显而易见，cp是攻击者可控的，由此可以控制
_npp的大小。而对于标签的长度，即len变量，直接从数据包中得到，并没有做任何边界检查，然后通过while循环处理。因此可以对len设置任意的值，即攻击者对_
npp buffer可控的长度。由此可以在堆中造成越界写，这可导致远程代码执行(RCE)。

![](https://images.seebug.org/content/images/2020/12/1fe4ea16-7b86-4d11-bada-c4a1b89240d2.png-w331s)

**5、CVE-2020-17443**

CVE-2020-17443存在于PicoTCP协议栈pico_icmp6.c文件中。问题代码位于pico_icmp6_send_echoreply（）函数中，该函数的主要功能是回复ICMPv6应答数据包以响应对端的ICMPv6
Echo(ping)请求。

![](https://images.seebug.org/content/images/2020/12/9525e4c5-b777-4145-8514-bc1ae77889ce.png-w331s)

我们可以看到第68行，replay结构的缓冲大小基于echo的报文中transport_len变量。

在第84行，程序从echo->payload向reply->payload地址复制了长度为echo->transport_len - 8大小的数据。

注意，如果echo->transport_len 小于 8，echo->transport_len - 8会导致整数溢出，memcpy操作会导致缓冲区溢出。

在PicoTCP协议栈攻击者通过构造恶意的ICMPv6数据包，这个恶意的数据包ICMP报头小于8，会导致设备重启或拒绝服务。

## 五、漏洞验证

1、CVE-2020-17437漏洞验证视频

2、CVE-2020-17443漏洞验证视频

详见以下链接：

[https://mp.weixin.qq.com/s?__biz=MzAwNTI1NDI3MQ==&mid=2649615617&idx=1&sn=b6df9ee2c5265ded1913b318cc241d90&chksm=83063011b471b9073ac1b159d95ed8f40617d5897442ba9157c446962a560cccc3477205cd67&token=566237918&lang=zh_CN#rd](https://mp.weixin.qq.com/s?__biz=MzAwNTI1NDI3MQ==&mid=2649615617&idx=1&sn=b6df9ee2c5265ded1913b318cc241d90&chksm=83063011b471b9073ac1b159d95ed8f40617d5897442ba9157c446962a560cccc3477205cd67&token=566237918&lang=zh_CN#rd)

## 六、参考链接

1、<https://www.forescout.com/research-labs/amnesia33/>

2、<https://www.securityweek.com/amnesia33-vulnerabilities-tcpip-stacks-expose-millions-devices-attacks>

3、<https://www.zdnet.com/article/amnesia33-vulnerabilities-impact-millions-of-smart-and-industrial-devices/>

4、<https://tools.ietf.org/html/rfc1035>

5、<https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1428/>

