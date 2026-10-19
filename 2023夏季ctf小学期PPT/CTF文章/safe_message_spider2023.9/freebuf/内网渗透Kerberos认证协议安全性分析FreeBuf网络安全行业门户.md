## 前言

要想进行内网渗透，可以说必须了解kerberos协议，可以说这是一个基础，本文总结了kerberos的认证流程以及可能出现的攻击方式。

## Kerberos认证

### kerberos认证是什么？

Kerberos 是一种由 MIT（麻省理工大学）提出的一种网络身份验证协议。它旨在通过使用密钥加密技术为客户端/服务器应用程序提供强身份验证。

Kerberos一词来源于希腊神话——一条凶猛的三头保卫神犬，用这个名字可能意味保护认证过程中的安全。

同时，Kerberos 是一种基于 **加密 Ticket 的身份认证协议** 。

###
![1688443377_64a399f1dfa7312f07944.png!small?1688443378620](https://image.3001.net/images/20230704/1688443377_64a399f1dfa7312f07944.png!small?1688443378620)

### kerberos的组成部分

Kerberos 主要由三个部分组成：Key Distribution Center (即KDC)、Client 和 Service。如下图所示：

![1688443404_64a39a0c759f83d339915.png!small?1688443404984](https://image.3001.net/images/20230704/1688443404_64a39a0c759f83d339915.png!small?1688443404984)

下面来看看每个部分具体的作用是什么

KDC：密钥分发中心，负责存储用户信息，管理发放票据，是Kerberos的核心部分。KDC默认是安装在域控中的。

 **由上图中可以看到 KDC 又分为两个部分：**

 **Authentication Server** ：AS 的作用就是验证 Client 端的身份（确定你是身份证上的本人），验证通过就会给一张
TGT（Ticket Granting Ticket）票给 Client。

 **Ticket Granting Server** ：TGS 的作用是通过 AS 发送给 Client 的票（TGT）换取访问 Server
端的票（上车的票 ST）。ST（ServiceTicket）也有资料称为 TGS Ticket，为了和 TGS 区分，在这里就用 ST 来说明。

 **KDC 服务框架中包含一个 KRBTGT
账户，它是在创建域时系统自动创建的一个账号，你可以暂时理解为他就是一个无法登陆的账号，在发放票据时会使用到它的密码 HASH 值。**

 **client：** 想访问某个server的客户端，通常是域内主机。

 **server：** 提供某种业务的服务，如http，mysql等

域控内还存在AD，也就是活动目录，用于存储用户，用户组，域相关的信息。

  

## kerberos的认证流程

![1688443591_64a39ac722b84b9bab358.png!small?1688443592087](https://image.3001.net/images/20230704/1688443591_64a39ac722b84b9bab358.png!small?1688443592087)

从上图可以看出整个认证过程总共分成了6步，分为下面三个阶段。

  * AS_REQ & AS_REP
  * TGS_REQ & TGS_REP
  * AP-REQ & AP-REP

下面来详细看看各个阶段所完成的工作：

![1688444035_64a39c83129d79e2a280b.png!small?1688444035542](https://image.3001.net/images/20230704/1688444035_64a39c83129d79e2a280b.png!small?1688444035542)

###  **AS_REQ**

当域内的某个client想要访问某个服务时，输入用户名和密码，此时客户端本机的 Kerberos 服务会向 KDC 的 AS
认证服务发送一个AS_REQ认证请求

请求内容是： **Client 的哈希值 NTLM-Hash 加密** 的时间戳以及 Client-info、Server-info
等数据，以及一些其他信息。

 **注意这里传递是用clinet的哈希值加密的内容，而不是传递了client的明文密码**

### AS_REP

AS收到请求后，AS 会先向活动目录 AD 请求，询问是否有此 Client 用户，如果有的话，就会取出它的 NTLM-Hash，并对AS_REQ请求中加密的时间戳进行解密，如果解密成功，则证明客户端提供的密

