近年来，在地下市场中蓬勃发展的一个领域是“初始访问权限”的售卖。攻击者一旦获取受害者的初始访问权限，就将其转售给其他攻击者进行获利。

2017 年 11 月，IBM X-Force 首次披露了恶意软件 IcedID。该恶意软件与 Pony
共享了部分代码，最初主要窃取银行凭据，后来也转型在失陷主机上部署、传播其他恶意软件。

IcedID 最常见的投递方式是通过带有恶意附件的鱼叉邮件，附件多为加密的压缩文件。压缩文件内是一个带有恶意宏代码的文档文件，拉取 IcedID 恶意样本。

IcedID 近期使用失陷的 Microsoft Exchange 服务器利用失陷账户发送鱼叉邮件。Payload 也从文档文件转而使用带有 Windows
LNK 文件和 DLL 文件的 ISO 文件。使用 ISO 文件可以绕过 Mark-of-the-Web
控件，从而在不触发警告的情况下执行恶意软件。研究人员已经发现了针对能源、医疗、保健、法律和制药行业的攻击。

## 感染链

![image.png-47.9kB](https://image.3001.net/images/20220406/1649224381_624d2abd44cb3b0b9a01b.png!small)感染链

攻击从鱼叉邮件开始，邮件提示用户有关重要文档的信息，带有加密的压缩文件，解压密码在邮件正文中提供。为了看起来更可信，攻击者使用了对话劫持伪造此前电子邮件的回复，且邮件也由失陷邮件账户发送。

![image.png-105kB](https://image.3001.net/images/20220406/1649224381_624d2abda5d52e74e6b69.png!small)邮件信息

压缩文件中包含一个同名的 ISO 文件，文件是在电子邮件发送前不久创建的：

![image.png-17.3kB](https://image.3001.net/images/20220406/1649224382_624d2abe3710b73ec70b1.png!small)压缩文件信息

ISO 文件中包含一个名为 `document`的 LNK 文件和一个名为 `main`的 DLL 文件。从时间戳可知，DLL
文件是提前一天准备好的，LNK 文件是提前一周准备好的。

![image.png-24.9kB](https://image.3001.net/images/20220406/1649224382_624d2abe7fe3b3ba4c910.png!small)ISO
文件信息

LNK 文件显示的图标使其看起来像是文档文件，用户点击时会触发 `regsvr-32`执行 DLL 文件。

![image.png-43.5kB](https://image.3001.net/images/20220406/1649224382_624d2abed3d393c5b7de0.png!small)LNK
文件信息

DLL 文件为 IcedID 的 Loader，其中大部分都是垃圾代码且有很多导出函数：

![image.png-208.7kB](https://image.3001.net/images/20220406/1649224383_624d2abf412e7d4a2c337.png!small)DLL
文件信息

Loader 加载存储在资源段中的加密载荷，并且使用了 API Hash 技术：

![image.png-77.8kB](https://image.3001.net/images/20220406/1649224383_624d2abfc795ca017c3c6.png!small)部分代码

生成的哈希与硬编码的哈希比较，定位 `FindResourceA`进行调用获取 Payload：

![image.png-551.5kB](https://image.3001.net/images/20220406/1649224384_624d2ac060846bbef8759.png!small)资源信息

使用 `VirtualAlloc`分配内存并保存解密的 Payload：

![image.png-102.8kB](https://image.3001.net/images/20220406/1649224386_624d2ac257d06ddb9eb29.png!small)部分代码

执行的是 IcedID 常用的 `Gziploader`，该恶意软件会首先对机器进行指纹识别并向 C&C 服务器发送失陷主机相关信息。信息通过 HTTP
GET 请求，藏在 Cookie 中发送：

![image.png-101.4kB](https://image.3001.net/images/20220406/1649224386_624d2ac2cb69097512d1e.png!small)Cookie
信息

C&C 服务器为 `yourgroceries.top`，分析时并未响应相关指令：

![image.png-291.6kB](https://image.3001.net/images/20220406/1649224387_624d2ac354b32f28cf40e.png!small)处理响应

## 会话劫持

攻击者将对话劫持用于攻击中已有一段时间，这样使钓鱼邮件看起来更加真实。过去的半年中，攻击者也更加精进，不再是以哦那个虚假的电子邮件地址发送邮件，而是直接使用失陷的账户地址。

2021 年 11 月，Qakbot 被发现利用会话劫持进行分发。研究人员 Kevin Beaumont 认为分发邮件的 Microsoft
Exchange 服务器有被 ProxyShell 利用的痕迹。

## 2022 年 3 月新攻击行动

3 月中旬，研究人员发现了与之前相同的会话被重复利用。在野发现的大多数原始 Exchange 服务器似乎仍未打补丁，这使得 ProxyShell
成为了非常好的攻击向量。

当然，除了公网部署的 Exchange 服务器被利用，也发现了内部的 Exchange 服务器也在发送钓鱼邮件。如下所示，Exchange 服务器的 IP
地址为本地 IP 地址、顶级域名为 local 且 Exchange 的标头都指向其为内部电子邮件。

    
    
    Received: from ExchSrv01.[REDACTED].local (172.29.0.12) byExchSrv01.[REDACTED].local (172.29.0.12) with Microsoft SMTP Server(version=TLS1_2, cipher=TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384) id 15.2.464.5via Mailbox Transport; Thu, 10 Mar 2022 14:34:29 +0100Received: from ExchSrv01.[REDACTED].local (172.29.0.12) byExchSrv01.[REDACTED].local (172.29.0.12) with Microsoft SMTP Server(version=TLS1_2, cipher=TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384) id 15.2.464.5;Thu, 10 Mar 2022 14:34:29 +0100Received: from ExchSrv01.[REDACTED].local ([fe80::b148:8e7:61f8:61b4]) byExchSrv01.[REDACTED].local ([fe80::b148:8e7:61f8:61b4%6]) with mapi id15.02.0464.005; Thu, 10 Mar 2022 14:34:29 +0100…X-MS-Exchange-Organization-AuthAs: InternalX-MS-Exchange-Organization-AuthMechanism: 04X-MS-Exchange-Organization-AuthSource: ExchSrv01.[REDACTED].localX-MS-Has-Attach: yesX-MS-Exchange-Organization-SCL: -1X-MS-Exchange-Organization-RecordReviewCfmType: 0x-ms-exchange-organization-originalclientipaddress: 172.29.5.131x-ms-exchange-organization-originalserveripaddress: fe80::b148:8e7:61f8:61b4%6﻿

研究人员未能找到该 Exchange 服务器对应的公网 IP 地址，也不知道攻击者是如何攻陷它的。

![image.png-18.8kB](https://image.3001.net/images/20220406/1649224388_624d2ac443328003b4c2f.png!small)登录页面

上面描述的客户端通过 MAPI 连接到服务器，MAPI 协议用于访问 Exchange 服务器上的邮箱，这表明攻击者是使用 Exchange
客户端而不是使用 SMTP 来发送电子邮件。

在多封电子邮件中都能发现 `X-Mailer：Microsoft Outlook 16.0`与 `X-Originating-IP`，这是使用 Web
界面时由 Exchange 服务器添加的标头。

## 归因

2021 年 6 月，Proofpoint 发布了关于多个为勒索软件提供初始访问权限售卖的分析报告。其中，TA577 和 TA551 都使用
IcedID。特别的，TA551 使用的技术就包括会话劫持和加密压缩文件，并且该组织还使用 regsvr-32.exe 来执行恶意 DLL 文件。

## 总结

会话劫持是一种强大的社会工程学技术，可以显著提高钓鱼的成功率。攻击者也将 Payload 从文档文件转移到 ISO 文件中，并且极力隐藏攻击行动。

## IOC

> 3542d5179100a7644e0a747139d775dbc8d914245292209bc9038ad2413b3213  
> 698a0348c4bb8fffc806a1f915592b20193229568647807e88a39d2ab81cb4c2  
> a17e32b43f96c8db69c979865a8732f3784c7c42714197091866473bcfac8250  
> yourgroceries.top

## 参考来源

> [Intezer](https://www.intezer.com/blog/research/conversation-hijacking-> campaign-delivering-icedid/)

