**作者：Tangerine  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

> 引言与架构：
>
>
> 自动驾驶即来，移动设备、视频流量、云服务的不断扩展，带宽需求也随之快速增长，网络环境也变得复杂，数据安全和隐私问题非常重要，其中对数据安全和隐私要求高的机构不能忽视局域网数据安全。
>
> 交换机作为构建局域网最基本的设备，企业交换机的部署需要更合适的安全协议，可以更有效的规避数据风险，保护企业的局域网安全，MACsec
> 是致力于下一代高速加密的企业、政府或服务提供商新的选择，如果有这样的需求，MACsec
> 安全协议数据链路层为企业提供更安全的选择，这篇文章来简单分析二者的联系。

![image-20230330200904222](https://images.seebug.org/content/images/2023/04/07/1680845541000-image-20230330200904222.png-w331s)

## 1.MACsec协议是什么？

MACsec，英文全称 **Media Access Control security** ，中文为 **媒体访问控制安全协议**
，是基于802.1AE和802.1X协议的局域网上的安全通信方法，它拥有身份认证、数据加密、完整性校验、重播保护等功能保证 **以太网数据帧**
的安全，从更底层防止设备处理有安全威胁的报文，MACsec加密比任何其他更高层加密方法（如IPsec和SSL）的优先级更高。

因为在很多情况下，绝大部分的数据不像广域网中使用多种加密算法，在局域网链路中传输形式是明文传输的，由此引发许多安全隐患，在诸如银行金融领域，军事单位中帐户的信息被窃取、篡改，遭受恶意网络攻击后会引发严重的网络安全事件。

> MACsec可以保护所有以太网链路中流量（注意不是所有互联网流量，而是强调协议之间的 **互操作性** 和 **互补性**
> ），包括拒绝服务、入侵、中间人、伪装、被动窃听和重放攻击，可以将 MACsec 与其他安全协议（如 IP 安全 （IPsec） 和安全套接字层
> （SSL） 结合使用，以提供端到端网络安全。

网络中部署MACsec后，可对传输的以太网数据帧进行保护，降低信息泄露和遭受恶意网络攻击的风险。数据和报文仅在PC和交换机之间的链路上加密（点对点加密）。
交换机收到的数据包将解密并通过未加密的上行链路发送，为了加密交换机之间的传输，建议使用交换机 — 交换机加密。

### 1.1 MACsec的数据控制和数据处理：

> **控制部分** 遵从的是IEEE802.1x（802.10,802.11...WIFI也属于这个协议），只有认证的双方能够建立链接， **数据部分**
> 遵从的是IEEE802.AE，对以太网报文基于AES-GCM进行加密。

  1. 当MACsec被使用时，只有认证双方可以连接网络
  2. 所有期望“欺骗”交换机/路由将网络数据重定向到攻击者机器的行为都不能成功
  3. MACsec是WiFi中WPA2的有线等效
  4. 应用不会感知MACsec的存在

### 1.2 MACsec应用场景一：交换机点对点

![image-20230330202721857](https://images.seebug.org/content/images/2023/04/07/1680845543000-image-20230330202721857.png-w331s)

交换机之间部署双向的MACsec对数据进行安全保护，实现通信安全。

### 1.3 MACsec应用场景二：含中间交换机

![image-20230330203307314](https://images.seebug.org/content/images/2023/04/07/1680845543000-image-20230330203307314.png-w331s)

当中间包含多个交换机时，可以使用数据链路层的二层协议透明传输功能，实现通信安全。

## 2.如何应用MACsec在互联网安全中？

在两台设备之间实现MACsec时，MACsec协议的工作过程可以分为四个主要阶段，包括 **身份认证、会话协商** 、 **安全通信** 和
**会话终止** 。

![image-20230331015055918](https://images.seebug.org/content/images/2023/04/07/1680845543000-image-20230331015055918.png-w331s)

  * **身份认证** 阶段

在客户端和接入设备之间建立安全会话前，客户端首先需要在接入设备的端口上进行802.1X认证。客户端通过认证后， **RADIUS**
服务器会把生成的CAK分发给客户端和接入设备。

![image-20230331015147037](https://images.seebug.org/content/images/2023/04/07/1680845543000-image-20230331015147037.png-w331s)

  * **会话协商** 阶段

使用配置的预共享密钥 (PSK) 作为 CAK（连接关联密钥），通过 EAPOL-MKA（LAN-MACsec协议上的可扩展身份验证协议）消息在设备之间协商会话。设备间优先级高的端口会被选举为Key
Server，负责生成和分发SAKs（安全关联密钥），设备之间相互通知自己的能力和建立会话所需的各种参数（如优先级，是否需要加密会话等）通过 MKA 协议。

CAK作用：生成用于MACsec的所有其他密钥的长期主密钥。

SAK作用：是路由器/终端设备用于加密给定会话流量的密钥。

![image-20230331015351981](https://images.seebug.org/content/images/2023/04/07/1680845543000-image-20230331015351981.png-w331s)

  * **安全通信** 阶段

会话协商完成后，客户端和接入设备有了可用的SAK，并使用SAK加密数据报文，开始加密通信。

![image-20230331015907814](https://images.seebug.org/content/images/2023/04/07/1680845543000-image-20230331015907814.png-w331s)

  * **会话终止** 阶段

当接入设备收到802.1X客户端的下线请求消息后，立即清除该用户对应的安全会话，避免一个未认证的客户端使用端口上前一个已认证客户端建立的安全会话接入网络。

此外，MKA协议里定义了一个会话保活定时器，如果在超时时间内（6秒），本端没有收到对端的MKA协议报文，则在定时器超时后，本端将清除建立的安全会话。

  * **名词解释：**

缩写 | 名称 | 指代对象  
---|---|---  
**MKA** | MACsec密钥协议 | 在IEEE 802.1X REV-2010中定义为用于发现MACsec对等体和协商密钥的关键协议协议  
**CAK** | 连接关联密钥 | 用于生成用于MACsec的所有其他密钥的长期主密钥。 LAN实施从MSK派生此信息（在EAP交换期间生成）  
**PMK** | 成对主密钥 | 用于派生用于加密流量的会话密钥的组件之一。手动配置或从802.1X派生  
**CKN** | CAK密钥名称 | 用于配置密钥值或CAK。仅允许偶数个十六进制字符（最多64个字符）。  
**SAK** | 安全关联密钥 | 由从CAK选出的密钥服务器派生，是路由器/终端设备用于加密给定会话流量的密钥。  
**ICV** | 完整性检查值键 | 从CAK派生，并在每个数据/控制帧中标记，以证明该帧来自授权对等体。8-16个字节，具体取决于密码套件  
**KEK** | 密钥加密密钥 | 派生自CAK（预共享密钥），用于保护MacSec密钥  
**SCI** | 安全通道标识符 | 每个虚拟端口接收一个唯一的安全通道标识符(SCI)，该标识符基于与16位端口ID连接的物理接口的MAC地址  
  
## 3.MACsec协议的格式

![image-20230331013222576](https://images.seebug.org/content/images/2023/04/07/1680845543000-image-20230331013222576.png-w331s)

**控制帧(EAPOL-MKA)** 协议格式：

  * EAPOL目标MAC = 01:80:C2:00:00:03将数据包组播到多个目标
  * EAPOL以太网类型= 0x888E

![image-20230331014520281](https://images.seebug.org/content/images/2023/04/07/1680845544000-image-20230331014520281.png-w331s)

**数据帧** 协议格式：

MACSec会在数据帧上插入两个额外标签，最大开销 **为32字** 节（最少16字节）。

  * **SecTag** = 8到16字节（8字节SCI是可选的）
  * **ICV** = 8到16个字节，基于密码套件(AES128/256)

> 数据包编号和重放保护：
> 在每个安全关联中，可以通过对照本堆存储的分组号检查SecTAG报头的分组号字段来执行重放保护。每个MCsC分组具有唯一的顺序分组号，并且每
> 个分组号在给定的安全关联中只能使用一次。

## 4.自动驾驶汽车的汽车网络和系统架构攻击

无论是数据交换和数据通信，又或者是家庭网络安全和企业园区网络安全，涉及两个远距离数据中心网络之间使用光纤互联，光纤穿越的地方属于公共区域，该区域
内的数据暴露风险较大。为了防止数据在中间传输过程中被窃取或修改，可在两个网络边缘设备出 端口上采用 MACsec 对数据传输进行安全保护。

![image-20230331165738464](https://images.seebug.org/content/images/2023/04/07/1680845544000-image-20230331165738464.png-w331s)

### 4.1 以太网链路窃听攻击实现：

在通常的以太网连接中，没有在数据链路层部署MACsec协议，也没有入侵者进行攻击，获取新数据，接下来查看两种情况，分别是遭受图像监控和数据破坏攻击在没有部署和部署MACsec协议的协议执行流程。

![image-20230331021346401](https://images.seebug.org/content/images/2023/04/07/1680845544000-image-20230331021346401.png-w331s)

黑客可以通过私密加装中间设备，以偷取数据，监控屏幕，终端无法得知系统是否处于危险状态，也无法得知是否有人窃听网络。

![image-20230331021739744](https://images.seebug.org/content/images/2023/04/07/1680845544000-image-20230331021739744.png-w331s)

启用MACsec协议，保密传输帧时，成功阻止入侵者获取信息，保证数据的正常显示。

> 处理数据和控制流量：
> 所有流量都在一个活动的MACsec端口上进行控制，在该端口上，数据被加密，或其完整性受到保护。如果MACsec会话无法得到保护，所有数据和控制流量都会被丢弃，当MACsecseC在某个端口上处于活动状态时，该端口会阻止数据流量的流动，在MACsecsec会话安全之前，端口不会转发数据流量。
>
> 如果正在进行的会话被打断，端口上的流量将再次被传输，直到建立新的安全会话。

![image-20230331021956288](https://images.seebug.org/content/images/2023/04/07/1680845544000-image-20230331021956288.png-w331s)

### 4.2 以太网链路DoS攻击实现：

入侵者可以在中间数据链路层中破坏数据流的传输，导致Camera无法起作用，但并不是Camera出现问题，难以准确定位问题所在。

![image-20230331152904968](https://images.seebug.org/content/images/2023/04/07/1680845544000-image-20230331152904968.png-w331s)

当部署MACsec协议后，检测入侵者的接收设备并没有得到认证（如RADIUS），所以为了保护正常显示，会在交换设备出阻止入侵连接，进入正常用户数据帧接收处，导致防护成功。

> 数据控制：
>
>
> 在MACsec会话得到保护之前，活动MACsec端口不会传输控制流量（如STP、LACP）。建立会话时，只有8O2.1X协议数据包从端口传输。建立安全会话后，控制流量会正常通过端口。

![image-20230331152959281](https://images.seebug.org/content/images/2023/04/07/1680845544000-image-20230331152959281.png-w331s)

汽车企业和制造商可可以使用MACsec在最大程度上保护汽车，以免暴露在外界特别容易受到以太网链路攻击，MACsec可以比作汽车安全工具箱中的性价比很高的安全工具，并且MACsec支持系统工程师将其与其他安全措施结合使用（IPSec和TLS）这样的工具。

## 5.路由器Cisco安全MACsec协议配置过程和相关验证

### 步骤1.验证链路两端的配置

显示当前设备的运行配置信息，并只显示与密钥链相关的配置信息，方便管理员查看和管理设备上的密钥链配置。

    
    
    C9500#sh run | sec key chain
    key chain KEY macsec
     key 01
     cryptographic-algorithm aes-256-cmac
     key-string 7
    101C0B1A0343475954532E2E767B3233214105150555030A0004500B514B175F5B05515153005E0E5E505C5256400702
    5859040C27181B5141521317595F052C28
     lifetime local 00:00:00 Aug 21 2019 infinite <-- use NTP to sync the time for key chains
    mka policy MKA
    key-server priority 200
    macsec-cipher-suite gcm-aes-256
    confidentiality-offset 0 

显示交换机接口te1/1/3的运行配置信息，包括地理位置、组态信息和特定的协议配置等，可以通过这个命令查看和修改交换机接口的配置信息。

    
    
    C9300#sh run interface te1/1/3
    interface te1/1/3
    macsec network-link
    mka policy MKA
    mka pre-shared-key key-chain KEY

### 步骤 2 验证MACsec已启用，且所有参数/计数器都正确

显示MACsec加密的摘要信息

  * Interface：交换机的接口名称。
  * Transmit SC：此接口上MACsec加密所用的下行（即传输数据）Secure Channel ID（SC）计数器的值。
  * Receive SC：此接口上MACsec加密所用的上行（即接收数据）Secure Channel ID（SC）计数器的值。

FortyGigabitEthernet1/0/1 接口使用的MACsec加密。"Transmit SC"和 "Receive SC" 列都有值1。

    
    
    C9500#sh macsec summary
    Interface Transmit SC Receive SC
    FortyGigabitEthernet1/0/1 1 1

查看指定接口的MACsec加密的具体配置信息，包括其状态、操作模式、加密策略。

    
    
    C9500#sh macsec interface fortyGigabitEthernet 1/0/1
    MACsec is enabled
    Replay protect : enabled
    Replay window : 0
    Include SCI : yes
    Use ES Enable : no
    Use SCB Enable : no
    Admin Pt2Pt MAC : forceTrue(1)
    Pt2Pt MAC Operational : no
    Cipher : GCM-AES-256
    Confidentiality Offset : 0

网络设备的功能列表或能力列表，包括硬件和软件上的功能。

    
    
        Capabilities
    ICV length : 16
    Data length change supported: yes
    Max. Rx SA : 16
    Max. Tx SA : 16
    Max. Rx SC : 8
    Max. Tx SC : 8
    Validate Frames : strict
    PN threshold notification support : Yes
    Ciphers supported : GCM-AES-128
    GCM-AES-256
    GCM-AES-XPN-128
    GCM-AES-XPN-256

"Transmit Secure Channels"是指在使用MACsec加密的网络连接中，发送（即传输数据）数据流的安全通道（Secure
Channel）的数量，每个接口可以有多个Transmit Secure Channels，以提供更多的安全通道、更好的容错能力和更高的性能。

    
    
    Transmit Secure Channels
    SCI : 0CD0F8DCDC010008
    SC state : notInUse(2)
    Elapsed time : 00:24:38
    Start time : 7w0d
    Current AN: 0
    Previous AN: -    Next PN: 2514
    SA State: notInUse(2)
    Confidentiality : yes
    SAK Unchanged : yes
    SA Create time : 1d01h
    SA Start time : 7w0d

SC Statistics用于加密网络连接中，记录和统计安全通道（Secure
Channel）的数据传输情况、错误情况以及其他相关统计数据的功能。在数据流向安全通道传输时，设备会记录各种数据，并提供与安全通道相关的统计信息。

    
    
    SC Statistics
    Auth-only Pkts : 0
    Auth-only Bytes : 0
    Encrypt Pkts : 3156 <-- should increment with Tx traffic
    Encrypt Bytes : 0

SA是两个设备之间的一个安全协议，它包含了用于保护数据通信的密钥及算法等信息。在SA传输数据时，设备会对SA的传输进行数据记录，包括传输的正确性、协议支持情况等。

    
    
    SA Statistics
    Auth-only Pkts : 0
    Encrypt Pkts : 402 <-- should increment with Tx traffic

Receive Secure Channels是指在使用MACsec加密的网络连接中，接收（即接收数据）数据流的安全通道（Secure
Channel）的数量。在接收数据时，接收器会使用一组Secure Channel
ID计数器的值来标识和保护数据流。MACsec使用这个值来保护数据流的完整性，以防止未经授权的访问和数据篡改。

    
    
    Receive Secure Channels
    SCI : A0F8490EA91F0026
    SC state : notInUse(2)
    Elapsed time : 00:24:38
    Start time : 7w0d
    Current AN: 0
    Previous AN: -    Next PN: 94
    RX SA Count: 0
    SA State: notInUse(2)
    SAK Unchanged : yes
    SA Create time : 1d01h
    SA Start time : 7w0d
    SC Statistics
    Notvalid pkts 0
    Invalid pkts 0
    Valid pkts 0
    Valid bytes 0
    Late pkts 0
    Uncheck pkts 0
    Delay pkts 0
    UnusedSA pkts 0
    NousingSA pkts 0
    Decrypt bytes 0
    SA Statistics
    Notvalid pkts 0
    Invalid pkts 0
    Valid pkts 93
    UnusedSA pkts 0
    NousingSA pkts 0
    !
    Port Statistics
    Ingress untag pkts 0
    Ingress notag pkts 748
    Ingress badtag pkts 0
    Ingress unknownSCI pkts 0
    Ingress noSCI pkts 0
    Ingress overrun pkts 0

显示指定接口fortyGigabitEthernet 1/0/1上的MKA（MACsec Key Agreement 密钥协商协议）会话信息。

    
    
    C9500#sh mka sessions interface fortyGigabitEthernet 1/0/1
    Summary of All Currently Active MKA Sessions on Interface FortyGigabitEthernet1/0/1...
    ================================================================================================
    ====
    Interface Local-TxSCI Policy-Name Inherited Key-Server
    Port-ID Peer-RxSCI MACsec-Peers Status CKN
    ================================================================================================
    ====
    Fo1/0/1 0cd0.f8dc.dc01/0008 MKA NO YES
    8 a0f8.490e.a91f/0026 1 Secured01 <--- CKN number must match on both
    0cd0.f8dc.dc01 <-- MAC of local interface
    a0f8.490e.a91f <-- MAC of remote neighbor
    8 <-- indicates IIF_ID of respective local port (here IF_ID is 8 for local port fo1/0/1)

查找特定端口（如/0/1端口）的接口号（interface number）为"Fo1/0/1

  * iif-id：接口标识符。
  * gid：分组标识符。
  * slot/unit：接口的槽号和单元号。
  * slun：接口的SLUN（Switch Logic Unit Number）值。
  * HWIDB-Ptr：指向关键硬件接口的指针。
  * status：接口的状态。
  * status2：接口的第二种状态。
  * state：接口的当前状态。
  * snmp-if-index：SNMP（Simple Network Management Protocol）接口索引号。

    
    
    C9500#sh platform pm interface-numbers | in iif|1/0/1
    interface iif-id gid slot unit slun HWIDB-Ptr status status2 state snmp-if-index
    Fo1/0/1 8 1 1 1 1 0x7EFF3F442778 0x10040 0x20001B 0x4 8

查看 FortyGigabitEthernet 1/0/1 接口的 MACsec Key Agreement (MKA) 会话的详细信息，MACsec
保护参数、密钥、会话 ID 等信息。

    
    
    C9500#sh mka sessions interface fortyGigabitEthernet 1/0/1 detail
    MKA Detailed Status for MKA Session
    ===================================
    Status: SECURED - Secured MKA Session with MACsec
    Local Tx-SCI............. 0cd0.f8dc.dc01/0008
    Interface MAC Address.... 0cd0.f8dc.dc01
    MKA Port Identifier...... 8
    Interface Name........... FortyGigabitEthernet1/0/1
    Audit Session ID.........
    CAK Name (CKN)........... 01
    Member Identifier (MI)... DFDC62E026E0712F0F096392
    Message Number (MN)...... 536 <-- should increment as message numbers increment
    EAP Role................. NA
    Key Server............... YES
    MKA Cipher Suite......... AES-256-CMAC
    Latest SAK Status........ Rx & Tx
    Latest SAK AN............ 0
    Latest SAK KI (KN)....... DFDC62E026E0712F0F09639200000001 (1)
    Old SAK Status........... FIRST-SAK
    Old SAK AN............... 0
    Old SAK KI (KN).......... FIRST-SAK (0)
    SAK Transmit Wait Time... 0s (Not waiting for any peers to respond)
    SAK Retire Time.......... 0s (No Old SAK to retire)
    SAK Rekey Time........... 0s (SAK Rekey interval not applicable)
    MKA Policy Name.......... MKA
    Key Server Priority...... 200
    Delay Protection......... NO
    Delay Protection Timer.......... 0s (Not enabled)
    Confidentiality Offset... 0
    Algorithm Agility........ 80C201
    SAK Rekey On Live Peer Loss........ NO
    Send Secure Announcement.. DISABLED
    SAK Cipher Suite......... 0080C20001000002 (GCM-AES-256)
    MACsec Capability........ 3 (MACsec Integrity, Confidentiality, & Offset)
    MACsec Desired........... YES

查看 MACsec Key Agreement (MKA) 策略配置的详细信息，包括 MKA 策略名称、密钥交换协议和密钥服务器配置。

    
    
    C9500#sh mka policy MKA
    MKA Policy defaults :
    Send-Secure-Announcements: DISABLED
    !
    MKA Policy Summary...
    !
    Codes : CO - Confidentiality Offset, ICVIND - Include ICV-Indicator,
    SAKR OLPL - SAK-Rekey On-Live-Peer-Loss,
    DP - Delay Protect, KS Prio - Key Server Priority
    Policy KS DP CO SAKR ICVIND Cipher Interfaces
    Name Prio OLPL Suite(s) Applied
    ===============================================================================
    MKA 200 FALSE 0 FALSE TRUE GCM-AES-256 Fo1/0/1 <-- Applied to Fo1/0/1

查看已发送和已接收的 MACsec PDU (协议数据单元) 数量的统计信息。

    
    
    C9500#sh mka statistics | sec PDU
    MKPDU Statistics
    MKPDUs Validated & Rx...... 2342 <-- should increment
    "Distributed SAK"..... 0
    "Distributed CAK"..... 0
    MKPDUs Transmitted......... 4552 <-- should increment

### 步骤3.检查链路启动时的软件调试

这一步非常重要，需要我们识别关键信息。

  * `debug cts sap events`: 显示 CTS (Cisco TrustSec) 和 SAP (Security Association Protocol) 事件的调试信息，包括已建立的安全关联和激活的安全服务等。
  * `debug cts sap packets`: 显示 CTS 和 SAP 数据包的调试信息，包括已发送和已接收的数据包、数据包的标头、负载和加密状态等。
  * `debug mka event`: 显示 MKA (MACsec Key Agreement) 事件的调试信息，包括MKA 会话状态的变化，启用和禁用 MKA 功能等。
  * `debug mka errors`: 显示 MKA 运行时可能出现的错误和故障的调试信息，包括 MACsec 错误、密钥交换故障、MKA 配置错误等。
  * `debug mka packets`: 显示 MKA 数据包的调试信息，八廓已发送和已接收的 MKA 控制报文 (MKA control packets)、保护参数提案 (SA proposal)、密钥交换报文 (KEK Packets)、生命信号报文 (Keep-Alive Packets) 等。
  * `debug mka ka errors`: 显示 MKA 存活 (Keep-Alive) 相关错误和故障的调试信息，包括保活超时、保活错误、无法发送或接收保活报文等。

    
    
    ### Verify CTS and SAP events ###
    debug cts sap events
    debug cts sap packets
    ### Troubleshoot MKA session bring up issues ###
    debug mka event
    debug mka errors
    debug mka packets
    ### Troubleshoot MKA keep-alive issues ###
    debug mka linksec-interface
    debug mka macsec
    debug macsec
    *May 8 00:48:04.843: %LINK-3-UPDOWN: Interface GigabitEthernet1/0/1, changed state to down
    *May 8 00:48:05.324: Macsec interface GigabitEthernet1/0/1 is UP
    *May 8 00:48:05.324: CTS SAP ev (Gi1/0/1): Session started (new).
    *May 8 00:48:05.324: cts_sap_session_start CTS SAP ev (Gi1/0/1) peer:0000.0000.0000
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    CTS SAP ev (Gi1/0/1): Old state: [waiting to restart],
    event: [restart timer expired], action: [send message #0] succeeded.
    New state: [waiting to receive message #1].
    *May 8 00:48:05.449: CTS SAP ev (Gi1/0/1): EAPOL-Key message from D0C7.8970.C381 <-- MAC of
    peer switch/router
    *May 8 00:48:05.449: CTS SAP ev (Gi1/0/1): EAPOL-Key message #0 parsed and validated.
    *May 8 00:48:05.449: CTS SAP ev (Gi1/0/1): Our MAC = 682C.7B9A.4D01 <-- MAC of
    local interface
    peer's MAC = D0C7.8970.C381.
    CTS SAP ev (Gi1/0/1): Old state: [waiting to receive message #1],
    event: [received message #0], action: [break tie] succeeded.
    New state: [determining role].
    *May 8 00:48:05.449: cts_sap_generate_pmkid_and_sci CTS SAP ev (Gi1/0/1) auth:682c.7b9a.4d01
    supp:d0c7.8970.c381, AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    CTS SAP ev (Gi1/0/1): Old state: [determining role],
    event: [change to authenticator], action: [send message #1] succeeded.
    New state: [waiting to receive message #2].
    *May 8 00:48:05.457: CTS SAP ev (Gi1/0/1): EAPOL-Key message from D0C7.8970.C381.
    CTS SAP ev (Gi1/0/1): New keys derived:
    KCK = 700BEF1D 7A8E10F7 1243A168 883C74FB,
    KEK = C207177C B6091790 F3C5B4B1 D51B75B8,
    TK = 1B0E17CD 420D12AE 7DE06941 B679ED22,

### 步骤4.在链路启动时查看平台级跟踪

显示第一个交换机的MACsec接口和其对应物理接口之间的映射关系。

    
    
    9300_stack#sh platform software fed switch 1 ifm mappings
    Interface IF_ID Inst Asic Core Port SubPort Mac Cntx LPN GPN Type Active
    GigabitEthernet1/0/1 0x8 1 0 1 0 0 26 6 1 1 NIF Y
    Note the IF_ID for respective intf
    - You will see this respective IF_ID in MACSEC FED traces below.

  * `set platform software trace fed switch 1 cts_aci verbose`: 开启第一个交换机上的CTS-ACI跟踪，并设置为详细模式。
  * `set platform software trace fed switch 1 macsec verbose`: 开启第一个交换机上的MACsec跟踪，并设置为详细模式。
  * `request platform software trace rotate all`: 将所有跟踪文件循环重写，以释放存储空间并确保跟踪一直处于运行状态。

    
    
    9300_stack#set platform software trace fed switch 1 cts_aci verbose
    9300_stack#set platform software trace fed switch 1 macsec verbose <-- switch number with
    MACsec port
    9300_stack#request platform software trace rotate all

显示第一个交换机软件平台跟踪的消息。

    
    
    9300_stack#show platform software trace message fed switch 1
    2019/05/08 01:08:50.688 {fed_F0-0}{1}: [macsec] [16837]: UUID: 0, ra: 0, TID: 0 (info): FED sent
    macsec_sa_sc_res_msg successfully
    2019/05/08 01:08:50.688 {fed_F0-0}{1}: [macsec] [16837]: UUID: 0, ra: 0, TID: 0 (info): FED
    sending macsec_sa_sc_res_msg
    2019/05/08 01:08:50.688 {fed_F0-0}{1}: [macsec] [16837]: UUID: 0, ra: 0, TID: 0 (debug): Running
    Install RxSA job for SCI: 15044144197663784960 AN:0 if_id: 0x8 lpn: 1

### 步骤5.验证硬件中MACsec接口的状态

显示包含所有可用于性能测量（performance measurement）的接口及其相应的编号。

    
    
    9300_stack#sh platform pm interface-numbers
    interface iif-id gid slot unit slun HWIDB-Ptr status status2 state snmp-if-index
    ------------------------------------------------------------------------------------------------    -------    Gi1/0/1 8 1 1 1 1 0x7F2C90D7C600 0x10040 0x20001B 0x4 8

  * `sh pl software fed switch 1 ifm if-id 8`: 显示第一个交换机上关于特定接口映射的信息，这里的接口ID为8。
  * `iif-id 8 maps to gig1/0/1`: FED上的接口ID 8 映射到 GigabitEthernet 1/0/1 物理接口。

    
    
    9300_stack#sh pl software fed switch 1 ifm if-id 8 <-- iif-id 8 maps to gig1/0/1
    Interface IF_ID : 0x0000000000000008
    Interface Name : GigabitEthernet1/0/1
    Interface Block Pointer : 0x7f4a6c66b1b8
    Interface Block State : READY
    Interface State : Enabled
    Interface Status : ADD, UPD
    Interface Ref-Cnt : 8
    Interface Type : ETHER
    Port Type : SWITCH PORT
    Port Location : LOCAL
    Slot : 1
    Unit : 0
    Slot Unit : 1
    SNMP IF Index : 8
    GPN : 1
    EC Channel : 0
    EC Index : 0
    Port Handle : 0x4e00004c

显示给定资源句柄（
`0x7f4a6c676bc8`）在第一个交换机的硬件前端（FED）中的映射情况，并根据需要指定相应的ASIC块，显示MACsec详细配置信息。

    
    
    9300_stack# sh pl hard fed switch 1 fwd-asic abstraction print-resource-handle 0x7f4a6c676bc8 1
    << port_LE handle
    Handle:0x7f4a6c676bc8 Res-Type:ASIC_RSC_PORT_LE Res-Switch-Num:0 Asic-Num:1 Feature-    ID:AL_FID_IFM Lkp-ftr-id:LKP_FEAT_INGRESS_PRECLASS1_IPV4 ref_count:1
    priv_ri/priv_si Handle: (nil)Hardware Indices/Handles: index1:0x0 mtu_index/l3u_ri_index1:0x2 sm
    handle [ASIC 1]: 0x7f4a6c682a08
    Detailed Resource Information (ASIC# 1)
    **snip**
    LEAD_PORT_ALLOW_CTS value 0 Pass
    LEAD_PORT_ALLOW_NON_CTS value 0 Pass
    LEAD_PORT_CTS_ENABLED value 1 Pass <-- Flag = 1 (CTS enabled)
    LEAD_PORT_MACSEC_ENCRYPTED value 1 Pass <-- Flag = 1 (MACsec encrypt enabled)
    LEAD_PORT_PHY_MAC_SEC_SUB_PORT_ENABLED value 0 Pass
    LEAD_PORT_SGT_ALLOWED value 0 Pass
    LEAD_PORT_EGRESS_MAC_SEC_ENABLE_WITH_SCI value 1 Pass <-- Flag = 1 (MACsec with SCI enabled)
    LEAD_PORT_EGRESS_MAC_SEC_ENABLE_WITHOUT_SCI value 0 Pass
    LEAD_PORT_EGRESS_MAC_SEC_SUB_PORT value 0 Pass
    LEAD_PORT_EGRESS_MACSEC_ENCRYPTED value 0 Pass
    **snip**

## 6.如何应用在车载通信安全中？

用密钥加密数据（对称加密），防止被未经授权的第三方窃听，而协议所在的通信等级是选择协议时的一个主要考虑因素，MACsec (IEEE 802.1AE)
在OSI第2层工作，因此始终仅直接用于两个相邻以太网节点之间。

![image-20230331165110309](https://images.seebug.org/content/images/2023/04/07/1680845544000-image-20230331165110309.png-w331s)

在车载通信安全中，存在极端情况是拒绝服务攻击，反复发送消息，其目标是导致信息过载。这会极大影响系统的正常通信，这些防御机制可以恢复被攻击者攻破的安全架构防护层。根据应用情况
，决定是否要继续无阻碍运行，或者由自动化汽车的驾驶员再次接管方向盘。

上图多级安全架构对于保护通过车载以太网进行的通信来说具有重要的作用，而网络安全领域和IT领域的交换机配置、VLAN虚拟局域网等多种方式应用广泛，可以对汽车安全形成一定的试验区，增强安全车载和智能驾驶。

## 7.MACsec的两种安全学习模式

### 7.1 静态 CAK 模式：

#### 步骤1：

先使用静态 CAK 模式启用 MACsec 时，两个安全密钥（连接关联密钥 （CAK）和随机生成安全关联密钥 （SAK）
将用于保护链路安全。在点对点以太网链路的每一端，两台设备之间都会定期交换这两个密钥，以确保链路安全。

  * 连接关联是一组 MACsec 属性，用于对接口创建两个安全通道，一个用于入站流量，一个用于出站流量。安全通道负责在 MACsec 安全链路上发送和接收数据。

#### 步骤2：

然后使用静态 CAK 安全模式启用 MACsec ，使用预共享密钥首次建立 MACsec 安全链路。预共享密钥包括连接关联名称 （CKN） 及其自己的
CAK。CKN 和 CAK 由连接关联中的用户配置，且必须在链路的两端匹配，才能首次启用 MACsec。

#### 步骤3：

最后成功交换匹配的预共享密钥后，将启用 MACsec 密钥协议 （MKA） 协议。MKA 协议负责维护链路上的
MACsec，并决定点对点链路上的哪个交换机成为关键服务器。然后，密钥服务器会创建一个仅与交换机在点对点链路另一端共享的 SAK，该 SAK
用于保护遍历该链路的所有数据流量。只要启用了 MACsec，密钥服务器将继续在点对点链路上定期创建并共享随机创建的 SAK。

### 7.2 动态 CAK 模式：

#### 步骤1：

先在MACsec 链路上的对等节点会作为 802.1X 身份验证过程的一部分动态生成安全密钥。对等节点在身份验证期间从 RADIUS 服务器接收
MACsec 密钥属性，并使用这些属性动态生成 CAK 和 CKN。然后，他们交换密钥以创建一个 MACsec 安全连接。

#### 步骤2：

然后因为动态 CAK 模式比静态 CAK 模式的管理更容易，所以不需要手动配置密钥。可以用 RADIUS 服务器集中管理密钥。

#### 步骤3：

最后在交换机到主机链路上，交换机是 802.1X 验证方，主机是请求方。在链路连接交换机或路由器上，这些设备必须同时充当验证方和请求方，以便相互验证。

> 动态 CAK 模式依赖于使用可扩展身份验证协议传输层安全 （EAP-TLS） 的基于证书的验证。RADIUS 服务器和交换设备必须使用 EAP-TLS
> 和公共密钥基础架构，才能在动态 CAK 模式下支持 MACsec，这也说明了协议的严谨性和安全性。

## 8.MACsec安全协议：

因此需要注意的是：并不是所有的交换机都支持MACsec安全协议，在终端一个无限制的数目可能需要验证到单个交换机端口，不支持MACsec安全协议，属于多验证模式，。也不是所有的汽车都存在MACsec保护。新兴的造车企业（如比亚迪、Telsa）及传统车企投入的一些未来车型的研发则有陆续采用更先进的整车电子电气架构，智能驾驶域控制器，内嵌MACsec安全协议，为智能化控制和车载安全提供基础，防范黑客攻击。

> 参考链接：
>
> 1.[汽车E/E电子架构的进化和改革简介 - 知乎
> (zhihu.com)](https://zhuanlan.zhihu.com/p/97912248)
>
> 2.[车载网络安全——MACsec/IPsec/SSL简介 - 知乎
> (zhihu.com)](https://zhuanlan.zhihu.com/p/597536539)
>
> 3.[用于自动驾驶的安全车载以太网——多级安全架构简介 - 知乎
> (zhihu.com)](https://zhuanlan.zhihu.com/p/386919986)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2060/>

