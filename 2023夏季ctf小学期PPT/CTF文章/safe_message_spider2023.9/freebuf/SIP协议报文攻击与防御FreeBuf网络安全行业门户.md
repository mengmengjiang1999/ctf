## 攻击原理

SIP(Session Initiation
Protocol)是一个应用层的信令控制协议。IP服务提供商基于此可以对外提供包含语音、视频、聊天服务。该协议可以创建、修改和释放一个或多个参与者的会话(多媒体会议、IP电话、多媒体分发)。

攻击者通过发送大量的intite消息到SIP服务器，导致被攻击SIP服务器分配大量的资源用以记录和跟踪会话，直到资源耗尽而无法响应合法用户的呼叫请求。

针对VoIP设备在SIP协议实现上的漏洞构造并发送相应的畸形SIP报文，导致SIP服务器拒绝服务。

## 防御原理

当客户有SIP服务器需要防护时，可以开启SIP功能进行防护。

###  **sip防护模式**

如果客户主要受到SIP inviteDDoS时，可以开启SIP学习模式或者防护模式进行防护，这里学习模式的性能比防护模式要好；

如果客户受到SIP register DDoS时，需要开启SIP防护模式进行防护；

如果客户同时受到SIP register DDoS和SIP inviteDDoS是，需要开启SIP防护模式进行防护。

###  **学习模式**

判断一个sip包是否是register报文，如果是直接加入白名单。

如果是invite报文，目标在防护状态下直接丢弃，目标不在防护状态下转发。此算法主要用于防护invite flood。如果是register
flood，将会透包。

SIP学习模式会主动学习发送register报文的源ip。无论目的ip在不在防护状态，开启sip学习模式并且目的端口为5060的报文都会进入sip学习模式的流程

![1607775127_5fd4b397b68c9c60b098c.png!small?1607775120446](https://image.3001.net/images/20201212/1607775127_5fd4b397b68c9c60b098c.png!small?1607775120446)

> 1.首先对sip报文进行解码，只解码register报文和invite报文，其他报文会解码失败；
>
> 2.判断报文是否是register报文，如果是register报文，则将源ip加入到高级信任，返回SC_FW_ACCEPT,放行该报文；否则转3；
>
> 3.测试目的ip是否在攻击状态，如果在攻击状态，则将invite报文丢弃；否则则让该报文过后续的处理流程。

## 测试工具

###  **搭建SIP** **业务的软件**

Linux: asterisk服务器

Windows:sip server 2008

###  **软件电话终端**

eyebeam客户端或者X-Lite软电话客户端

###  **Sip flood** **工具**

Scapy - 强大且高度互动的封包操控程序，可扫描、追踪路径、探测、个别测试、攻击和发掘网络装置  
Seagull - 支持多种协议之流量制造工具，特别是针对 IMS(IP Multimedia Subsystem)  
SIPBomber - Linux 用之 sip 协议测试工具  
SIPNess - SIP 应用程序测试工具  
SIPp - Open Source 测试工具，并能够制造 SIP 流量  
SIPsak - 号称 SIP 瑞士刀

IAXFlooder - 建立大量 IAX 封包之 Flooding 工具  
INVITE Flooder - 可用以对电话或 proxy 提交大量 SIP INVITE 讯息  
kphone-ddos - 可提交大量 SIP 封包以进行 flooding 攻击  
RTP Flooder - 建立大量"合法"的 RTP 封包以进行 flooding 攻击

