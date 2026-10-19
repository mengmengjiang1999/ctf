## **一.** **OPC概述**

###  **背景概述**

OPC Object Linking and Embedding（OLE） for Process
Control（用于过程控制的OLE）。它是基于Windows的应用程序与现场过程控制应用之间的桥梁。在过去，为了存取现场设备的数据信息，每一个应用软件开发商都需要编写专用的接口函数。由于现场设备的种类繁多，且产品的不断升级，往往给用户和软件开发商带来了巨大的工作负担。然而，这样也不能满足实际的工作需要，系统集成商和开发商急切需要一种具有高效性、可靠性、开放性、可互操作性的即插即用的设备驱动程序。在这种情况下，OPC标准应运而生。

OPC标准以微软公司的OLE技术为基础，它的制定是通过提供一套标准的OLE/COM接口完成的，在OPC技术中使用的是OLE
2技术，OLE标准允许多台微机之间交换文档、图形等对象。

###  **发展历程**

OPC UA 将逐步代替传统的OPC。在这个过渡期中，基于DCOM的OPC产品会与UA 产品将共存。OPC基金会的迁移战略能让传统的OPC 和OPC
UA产品很好的结合。目前，已经安装使用的几百万套、上千种传统的OPC产品可以与新的OPC
UA产品共同使用。这为用户提供了更多的选择范围，他们能从不同的制造商-传统的OPC 和 OPC UA 厂家，选用任何需要的产品。

![1620876168_609c9b8859d3dae7f07f6.png!small](https://image.3001.net/images/20210513/1620876168_609c9b8859d3dae7f07f6.png!small)

###  **OPC &OPCUA协议结构区别**

![1620876209_609c9bb1a32f36064a6d9.png!small](https://image.3001.net/images/20210513/1620876209_609c9bb1a32f36064a6d9.png!small)

##  **二. OPC UA 安全研究**

相较于第一代的OPC，OPC UA加入了强健的信息安全特性。

###  **OPC UA安全机制：**

> 认证：支持X.509证书认证或用户名密码或Kerberos
>
> 授权：基于用户的细粒度的权限管理（读、写点值）
>
> 完整性：消息签名，阻止通讯消息被篡改、中间人攻击
>
> 机密性：通过消息加密，防止通讯内容被第三方看到
>
> 应用实例认证：OPC Server认证，确保OPC Server的真实性

在发展过程中OPC
Foundation产品中总共发现了17个漏洞，且使用这些产品的商业应用中也存在缺陷。大多数缺陷是通过模糊测试发现的，理论上这些漏洞被利用后会对工业环境带来物理损害。

卡巴斯基实验室的研究人员对 OPC UA 进行详细的分析后表示，某些漏洞可被利用发起远程代码执行和 DoS 攻击。OPC
基金会已发布公告，将这些漏洞归在两个漏洞编号下：CVE-2017-17433和CVE-2017-12069，后者还影响了西门子自动化和配电产品。

![1620876255_609c9bdf743e8da4450c0.png!small](https://image.3001.net/images/20210513/1620876255_609c9bdf743e8da4450c0.png!small)

  

![1620876277_609c9bf5befef2067e605.png!small](https://image.3001.net/images/20210513/1620876277_609c9bf5befef2067e605.png!small)

##  **三. 攻击模拟**

###  **研究环境**

3台PC分别模拟攻击机、客户机、服务端：

> 服务端：192.168.2.34
>
> 客户机：192.168.2.29
>
> 攻击机：192.168.2.39

系统分别是：ParrotOS，Windows 10 专业版，Ubuntu 18.04

工具软件：openPen，python-opcua，Wireshark

###  **漏洞简介**

在工业系统中，拒绝服务漏洞构成的威胁比任何恶意软件都严重。遥测和遥控系统中的拒绝服务可能导致企业蒙受财务损失，在某些情况下甚至导致工业流程的中断和关闭。从理论上讲，这可能会对昂贵的工业设备造成伤害，并造成其他物理损坏。

攻击者通过Port 4840/TCP端口向OPC服务器发送特制数据包，利用该漏洞访问各种资源或仅不停地发送建链数据包，即可造成DOS攻击。

攻击图，如下所示：

![1620876462_609c9cae5a4ca97327420.png!small](https://image.3001.net/images/20210513/1620876462_609c9cae5a4ca97327420.png!small)

###  **攻击步骤**

OPC正常会话的建立流程，如下图：![1620876362_609c9c4ab76a4c15a92e0.png!small](https://image.3001.net/images/20210513/1620876362_609c9c4ab76a4c15a92e0.png!small)

1：搭建模拟环境，在以上3台机器上准备相应的工具。

![1620876371_609c9c5306796593d02fe.png!small](https://image.3001.net/images/20210513/1620876371_609c9c5306796593d02fe.png!small)

  

![1620876377_609c9c59698c4e67b609f.png!small](https://image.3001.net/images/20210513/1620876377_609c9c59698c4e67b609f.png!small)

客户机连接正常：

![1620876377_609c9c59698c4e67b609f.png!small](https://image.3001.net/images/20210513/1620876377_609c9c59698c4e67b609f.png!small)

![1620876388_609c9c64c768344d0a91e.png!small](https://image.3001.net/images/20210513/1620876388_609c9c64c768344d0a91e.png!small)

2：攻击机利用nmap扫描主机的4840端口，查看是否对外开放。

![1620876397_609c9c6dd49d468b4b504.png!small](https://image.3001.net/images/20210513/1620876397_609c9c6dd49d468b4b504.png!small)

3：通过4840/tcp端口向OPC Discovery Server发送建链数据包，占用通信信道，造成DOS攻击，导致服务器无法访问。

![1620876407_609c9c77170112a052046.png!small](https://image.3001.net/images/20210513/1620876407_609c9c77170112a052046.png!small)

##  **四.** **防御建议**

Ø 安装厂商安全补丁，及时更新软件。

Ø 建议用户使用工业防火墙，网络分区和VPN等适当的机制来保护网络访问。

参考链接：

https://www.securityfocus.com/bid/100559/info

https://www.securityweek.com/many-vulnerabilities-found-opc-ua-industrial-protocol

https://ics-cert.kaspersky.com/reports/2018/05/10/opc-ua-security-analysis/

