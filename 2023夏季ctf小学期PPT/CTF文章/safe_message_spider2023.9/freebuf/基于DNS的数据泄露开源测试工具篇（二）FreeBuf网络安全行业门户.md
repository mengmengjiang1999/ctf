**免责声明：本文作者竭力保证文章内容可靠，但对于任何错误、疏漏或不准确的内容，作者不负任何责任。文章部分内容来源于网络是出于传递更多信息的目的，对此不负任何法律责任。本文仅用于技术分享与讨论，严禁用于其他用途。**

##  一、前言

**在[基于DNS的数据窃取开源测试工具篇(一)](https://www.freebuf.com/sectool/222561.html?preview=true)中，简要分析了DET基于DNS进行数据窃取部分的源码。本文将继续探讨图1中所示的PyExfil中利用DNS完成数据窃取的部分。**

![](https://image.3001.net/images/20191218/1576642895_5df9a94fc3c71.png!small)

图1 DET、PyExfil、DNSExfiltrator的首页展示

##  二、PyExfil工具简介

PyExfil项目[1]本身是一个测试库，作为python库的形式提供给用户使用，该工具实现了多种数据泄露技术，包括攻击者在真正的攻击活动中已经或正在使用的部分技术。开源该工具的初衷是帮助用户在自己的系统中快速部署，从而帮助用户快速部署，用于检测其系统抵抗数据泄露的能力。

PyExfil工具实现了大量的相关技术，分别在网络、通信、物理、隐写等模块中实现，模块分类及对应技术详情见表1：

模块分类  |  技术详情  
---|---  
网络模块  |  **DNS** **查询** 、HTTP Cookie、ICMP Echo8、NTP Request、BGP Open、HTTPS
Replace Certificate、QUIC、Slack、POP3身份验证、FTP MKDIR、Source IP Based
Exfiltration、HTTP Response  
通信模块  |  NTP Request、DropBox LSP、DNS Over TLS、ARP
Broadcast、JetDirect、GQUIC、MDNS Query、AllJoyn  
物理模块  |  Audio、QR Code、WIFI Frame Payload  
隐写模块  |  图像二进制偏移、Video Dictionary、Braille Text Document  
  
表1 PyExfil的模块分类及其包含的技术统计

PyExfil整体项目结构梳理如图2。本文关注的DNS窃密部分位于网络模块中，dns_exfil.py文件是该工具利用DNS完成窃密的具体实现。

![](https://image.3001.net/images/20191218/1576642947_5df9a9831dfcb.png!small)

图2 PyExfil项目结构概况

##  三、基于DNS的数据窃取的源码简要分析

###  （一）服务端源码简要分析

![](https://image.3001.net/images/20191218/1576642966_5df9a99604fe5.png!small)图3
PyExfil的服务端源码概况

服务端源码梳理及工作流程如图3，通过源码分析，整理其窃密数据接收、恢复的主要过程如下：

(1) socket绑定设定端口并监听所有数据，分别提出数据(DNS请求包的所有数据部分)、地址。

(2) 在数据中查找包类型标识符，并根据包类型采取对应的处理方法。其中包类型及其判别依据见表2。

包类型  |  判别依据  
---|---  
初始化包  |  " **INIT_445** "+文件名+"::"+CRC32  
窃密数据包  |  "\x00\x00\x01\x00\x01"+ **数据** +"\xcc\xcc\xcc\xcc\xff\xff\xff\xff"  
结束包  |
"\xcc\xcc\xcc\xcc\xff\xff\xff\xff"+"::"+"\xcc\xcc\xcc\xcc\xff\xff\xff\xff"  
  
表2 PyExfil的包类型及其判别依据对应关系

(3) 服务端将根据不同的包类型采取不同的处理方法：

> 1) 初始化包：从包中提取即将传送文件的重要信息：文件名、CRC32校验值。
>
> 2) 窃密数据包：从包中提取窃取的文件数据，增量保存到变量actual_file中。
>
> 3) 结束包：标志着文件传输结束，则通过CRC32校验后恢复文件到本地，并回复客户端“OK”。

###  （二）客户端源码简要分析

![](https://image.3001.net/images/20191218/1576642976_5df9a9a00edcc.png!small)图4
PyExfil客户端源码概况

客户端源码及主要工作流程梳理如图4，通过源码分析，整理其构造、编码、发送窃密数据的主要过程如下：

(1) 参照DNS协议各字段，以服务端域名为基础构造一个普通的DNS请求，存储到dns_request。

(2) 按制定的窃密文件路径，将文件数据读入内存，并计算其CRC32值。

(3) 通过socket发送初始化包。其中，初始化包的组成结构大致如图5(dns_request由步骤(1)生成)。

![](https://image.3001.net/images/20191218/1576642987_5df9a9ab84582.png!small)图5
PyExfil初始化包的组成结构

(4) 通过socket逐个发送文件数据块。其中，窃密数据包组成结构如图6。

![](https://image.3001.net/images/20191218/1576642994_5df9a9b29ac7d.png!small)图6
PyExfil窃密数据包的组成结构

(5) 当所有文件数据块发送完毕后，通过socket发送结束包。其中，客户端构造的结束包组成结构如图7。

![](https://image.3001.net/images/20191218/1576643005_5df9a9bd3c6e2.png!small)图7
PyExfil结束包的组成结构

##  **总结与思考：**

PyExfil部署实验环境后，模拟执行数据窃取后的不同类型流量包情况分别如图8、图9、图10。

![](https://image.3001.net/images/20191218/1576643013_5df9a9c555ad6.png!small)图8
初始化包流量包情况

![](https://image.3001.net/images/20191218/1576643020_5df9a9ccaa376.png!small)图9
窃密数据包流量情况

![](https://image.3001.net/images/20191218/1576643027_5df9a9d3633c9.png!small)图10
结束包流量情况

通过以上分析，PyExfil具有明显的特征：PyExfil利用DNS的方式特点明显——在DNS请求的同一个UDP包中，先构造DNS普通DNS请求包，窃密数据附加到DNS协议内容以外的区域，即窃密数据位置在DNS协议规定的内容之外。

但综合来看，PyExfil在实验调试中也发现了一些问题：

> (1) 文件数据明文传输，打开Pcap包可以直接看到二进制数据对应窃密字符串。
>
> (2) 窃密数据包没有编号，且没有任何重传机制，在网络状况较差时，文件恢复失败率较高。
>
> (3) 源码中DNS请求部分为手动编码输入，结果是传输同一个窃密文件时，有很多内容相同的DNS请求——这本身就是一种异常。
>
> (4) 源码中只在成功恢复文件后响应客户端请求“Got it，OK”；为了减小异常，可以考虑对每个请求构造响应，且为自己定义的A记录值。

##  **参考链接：**

> [1] [PyExfil项目地址](https://github.com/ytisf/PyExfil)

***本文作者：GZHU/asUwIll，转载请注明来自FreeBuf.COM**

  

