作者：中兴沉烽实验室_xgr，LiYan

## 0x00 前言

随着5G的部署和商用，5G空口及其安全性越来越得到关注，本文介绍了5G空口控制面和用户面数据机密性和完整性保护至关重要的空口 SMC（Security
Mode
Command）过程，以及该过程与空口PDCP协议安全之间的关系，并进一步介绍了近年来出现的漏洞CVD-2019-0030的基本原理，其形成机制，和修复建议。

## 0x01 5G空口SMC过程

### 1.1 空口协议栈

5G NR（New
Radio）是新一代无线通信空口标准，其R15版本于2018年6月正式批准推出，成为支撑新一代超级互联移动通信系统的基础，以实现以下三种使用场景：

> • 增强移动宽带（eMBB）
>
> • 超高可靠性和低时延通信（URLLC）
>
> • 大规模机器类通信（mMTC）

5G NR由UE和gNB组成（以5G SA独立组网为例），其控制面和用户面通信协议栈如下图1所示：

![image-20210303105957024.png](https://image.3001.net/images/20210316/1615893562_6050943a4293efd99fea8.png!small)

图1 用户面和控制面协议栈

如图1所示，空口UU协议栈用户面采用SDAP、PDCP、RLC、MAC和PHY进行协议对接，控制面用RRC、PDCP、RLC、MAC、PHY进行协议对接，其中PDCP、RLC、MAC和PHY属于用户面和控制面共用，PDCP协议则负责整个控制面RRC信令和UP用户面的完整性保护和加密保护。这些完整新保护和加密保护的重要参数的协商和传递依赖于空口安全模式过程，也就是AS安全模式过程（AS
SMC）。

### 1.2 SMC过程

5G
NR中，gNB应通过网络管理配置允许使用的算法列表，包括一个完整性算法列表和一个机密性算法列表。这些列表应按照运营商决定的优先顺序排列。当要在gNB中建立AS安全上下文时，AMF应将UE
5G安全能力发送给gNB。基站侧gNB会根据核心网AMF下发的UE安全能力信息和基站本地配置策略，选择最高优先级的加密或完保算法。

所选算法应通过空口SMC过程（即AS
SMC）发送至UE。所选机密性算法用于加密（当被激活时）用户平面和RRC业务。所选完整性算法用于用户面和RRC流量的完整性保护（当被激活时）。AS
SMC激活控制面业务的机密性和完整性保护，而用户面业务的机密性和完整性保护基于来自SMF的UP安全策略，并通过RRC信令的重配置过程激活。

 **控制面**

在3GPP TS 38.413和3GPP TS 23.502中规定的UE注册或PDU会话建立期间，通过AS SMC过程以建立安全的RRC信令连接。AS
SMC具体流程包括gNB将AS SMC发送至UE，UE返回AS SMC Complete消息，如下图2所示。

![image-20210312172614765.png](https://image.3001.net/images/20210316/1615893600_60509460b37be0d27563c.png!small)

图2 AS SMC过程

> 步骤1a：gNB使用KgNB的RRC完整性密钥对AS SMC消息进行完整性保护；
>
> 步骤1b：gNB发送到UE的AS SMC消息，含所选的RRC和UP机密性和完整性算法；
>
> 步骤1c：gNB发送到UE的AS SMC消息后，开启RRC下行链路加密；
>
> 步骤2a：UE验证AS SMC完整性成功后，开启RRC完整性保护和RRC下行链接解密；
>
> 步骤2b：UE发送AS SMC Complete消息给gNB，使用AS
> SMC消息中指示的所选RRC算法和基于当前KgNB的RRC完整性密钥进行完整性保护；
>
> 步骤2c：UE发送AS SMC Complete消息给gNB成功后，开启RRC上行链路加密；
>
> 步骤1d：gNB在接收并成功验证AS SMC Complete消息之后，开启RRC上行链路解密。

若UE中对AS SMC的任何控制都不成功，则UE应返回不受保护的安全模式故障消息（见3GPP TS 38.331）。AS
SMC应仅在UE和gNB之间的初始上下文设置期间使用（即在从RRC-IDLE状态转换到RRC-CONNECTED状态时激活初始KgNB）。

 **用户面**

SMF应在PDU会话建立流程中向ng-eNB/gNB提供该PDU会话的用户面（UP）安全策略。UP安全策略应指示是否应对属于该PDU会话的所有DRB激活UP机密性和/或UP完整性保护。UP安全策略应当用于激活属于PDU会话的所有DRB的UP机密性和/或UP完整性。ng-eNB/gNB应根据接收到的UP安全策略，用RRC重配置信令为每个DRB激活UP机密性和/或UP完整性保护。

![image-20210312172443838.png](https://image.3001.net/images/20210316/1615893614_6050946e6a82f77bfa851.png!small)

图3 UP安全激活机制

用户面安全激活机制如图3所示，其具体步骤如下：

> 步骤1a：应只在AS SMC 过程中激活RRC安全之后，才执行用于添加DRB的RRC连接重配置过程。
>
> 步骤1b：gNB应向UE发送RRC连接重配置消息以用于激活UP安全，其中包含用于根据安全策略激活每个DRB的UP完整性保护和加密的指示。
>
>
> 步骤1c：按照RRC连接重配置消息的指示激活了DRB的UP完整性保护后，若gNB没有K~UPint~，则gNB应生成K~UPint~并对DRB进行UP完整性保护。类似地，按照RRC连接重配置消息的指示激活了DRB的UP加密后，若gNB没有K~UPenc~，则gNB应生成K~UPenc~并启动对上述DRB进行UP加密。
>
> 步骤2a：UE应验证RRC连接重配置消息。若验证成功：
>
>
> 步骤2a.1：按照RRC连接重配置消息的指示激活DRB的UP完整性保护后，若UE没有K~UPint~，则UE应生成K~UPint~并对DRB进行UP完整性保护。
>
>
> 步骤2a.2：类似地，按照RRC连接重配置消息的指示激活DRB的UP加密后，若UE没有K~UPenc~，则UE应生成K~UPenc~并对DRB进行UP加密。
>
> 步骤2b：若UE成功验证了RRC连接重配置消息的完整性，UE应向gNB发送RRC连接重配置完成消息。

若没有为DRB激活UP完整性保护，gNB和UE不应对这些DRB的流量进行完整性保护，且不应将MAC-I置于PDCP包中。若没有为DRB激活UP加密，gNB和UE不应加密这些DRB的流量。

## 0x02 PDCP协议安全

PDCP协议则负责整个控制面RRC信令和UP用户面的完整性保护和加密保护，当空口控制面和用户面的完整性和加密保护安全性激活后，PDCP就拥有用来进行完整性保护和加密保护的算法和参数。

下面以用户面的完整性保护和加密保护为例介绍其工作原理，具体原理可以参见3GPP TS33.501附录D。

 **完整性算法原理**

完整性算法的输入参数包括一个名为KEY的128位完整性密钥，一个32位COUNT，一个称为BEARER的5位承载标识，1位传输方向，即DIRECTION，以及消息本身，即MESSAGE。
上行链路的DIRECTION位应为0，下行链路的DIRECTION位应为1。MESSAGE的位长是LENGTH。图4描述了如何使用完整性算法NIA验证消息的完整性。

![image-20210301115205277.png](https://image.3001.net/images/20210316/1615893648_6050949024eae4013497e.png!small)

图4 MAC-I / NAS-MAC（或XMAC-I / XNAS-MAC）的推衍

基于这些输入参数，发送方使用完整性算法NIA计算一个32位消息认证码（MAC-I/NAS-MAC）。然后，在发送消息时将消息验证代码附加到消息中。对于完整性保护算法，接收方对接收到的消息计算预期消息认证码（XMAC-I/XNAS-MAC），其方式与发送方对发送的消息计算其消息认证码相同，并通过将其与接收到的消息认证码（即MAC-I/NAS-MAC）进行比较来验证消息的数据完整性。

 **加密算法原理**

加密算法的输入参数包括一个名为KEY的128位密码密钥，一个32位COUNT，一个5位承载标识BEARER，1位传输方向，即DIRECTION，以及所需密钥流的长度，即LENGTH。上行链路的DIRECTION位应为0，下行链路的DIRECTION位应为1。

图5说明了使用加密算法NEA生成密钥流对明文进行加解密的方法，该方法通过将明文和密钥流按位异或实现明文加解密。
可以通过生成相同的密钥流作为输入参数并与密文通过按位异或来恢复明文。

![image-20210301115113710.png](https://image.3001.net/images/20210316/1615893661_6050949d78f007575cba2.png!small)

图5 数据加解密处理

基于输入参数，算法生成输出密钥流块KEYSTREAM，用于加密输入明文块PLAINTEXT以产生输出密文块CIPHERTEXT。

## 0x03 CVD-2019-0030漏洞原理

ReVoLTE漏洞（CVD-2019-0030）是业界近年发现的一个关于PDCP加密的漏洞，来自波鸿鲁尔大学（Ruhr University
Bochum）和纽约大学阿布扎比分校（NYU Abu
Dhabi）的研究员发现，PDCP存在重复使用keystream导致用户通话数据被解密的可能性，该漏洞具体分析报告于2019年11月份通过GSMA的CVD
programme提交给GSMA。相同的攻击除了可实施与VoLTE,对其他空口类型的业务也适用，并且对5G call也适用。

VoLTE call是在LTE用户面PDCP层之上传输，PDCP层使用stream cipher进行加密，其中stream cipher是keystream
产生器，其使用32-bit加密密钥，PDCP COUNT值，bearer
ID，传输方向，keystream长度输入到加密算法，产生Keystream。再使用keystream对PDCP
packet进行加密。对于不同的packet，如果输入参数相同，相同的keysream就会被重用于不同的报文。

![image-20210301201234194.png](https://image.3001.net/images/20210316/1615893673_605094a9d3102ff216a17.png!small)

图6 用户面数据加解密

加密算法涉及到参数如下：

> KEY：128-bit cipher key；
>
> COUNT：32-bit PDCP count；
>
> BEARER：a 5-bit bearer identity ；
>
> DIRECTION：1-bit direction of the transmission； 0 for uplink and 1 for
> downlink
>
> LENGTH：the length of the keystream required；

因为相同的输入参数产生相同的Keystream，所以只要获取与Target Call（想要窃听的通话Call）一样的Keystream，就可将Target
Call密文解密出明文。ReVoLTE漏洞（CVD-2019-0030）正是是利用网络设备重复使用keystream这一漏洞， 攻击者先记录targeted
Call，然后再利用网络设备重复使用keystream的漏洞对target call的内容解密，从而达到窃听的目的，如图7所示。

![image-20210301163258888.png](https://image.3001.net/images/20210316/1615893713_605094d14cc9a198ee1a3.png!small)

![image-20210301164508798.png](https://image.3001.net/images/20210316/1615893722_605094dab4df82412b690.png!small)

图7 ReVoLTE窃听过程

一般情况下，用户开始建立会话，在生成Keystream过程中：

> COUNT：PDCP SQN + hyper frame count
>
> BEARER: The beaer Identity depends on the used bearer;

这两个参数的会有变化，使得用于PDCP packet加密的Keystream
是不同的，从而无法轻易获取到相同的Keystream。那么此漏洞中是什么情况下会导致两个不同的PDCP Packet的Keystream是相同的？例如：

> Case1. PDCP COUNTs wrap around;
>
> Case2. bearer ID reused.

通过对协议的分析，可以发现协议在这个问题上的要求存在模糊不明确地方，例如根据TS36.331章节5.3.1.2的要求：

> “The eNB is responsible for avoiding reuse of the COUNT with the same RB
> identity and with the same K~eNB~, e.g. due to the transfer of large volumes
> of data, release and establishment of new RBs. In order to avoid such re-> use, the eNB may e.g. use different RB identities for successive RB
> establishments, trigger an intra cell handover or an RRC_CONNECTED to
> RRC_IDLE to RRC_CONNECTED transition.”

可以看出协议对于相同RB和K~enb~下出现COUNT重用的可能性是有预判的，并且给出了要求，采取更换RB实体或者 intra
cell切换或者RRC重连来处理，但是同时可以发现在协议的其他地方如章节5.3.10.3存在描述不一致的情况：

> “When the UE receives a reconfiguration message for adding a data bearer, it
> adds a new PDCP entity and configures it with the current security
> configuration. A new PDCP entity causes a reset of the count variable. More
> precisely, the hyper frame number and the sequence numbers are set to 0.
> While the count starts over again, the security configuration including the
> k_up remains the same, which results in the keystream reuse.”【6】

该具体章节显示在重新建立用户面会话连接时，在进行RRC重配置流程处理过程中仍然采用当前的安全配置，包括原来的用户面KEY，将可能导致Keystream重用问题。

综上，协议不同部分的要求存在不一致的情况，可能导致开发人员理解和实现协议时出现偏差，从而导致漏洞的发生。研究人员也在实际的网络中测试并确认了该漏洞的存在。

可能的解决方案：

> 1.分析实现流程避免重用Bearer ID，查看Bearer ID被重用时是否会导致Keystream被重用；
>
> 2.如果出现前述漏洞，考虑在Bearer ID 在重用时执行key refresh的流程。例如5G协议TS38.331中通过intra-cell
> handover进行AS Key Refresh的要求：

AS Key Refresh:

This procedure is based on an intra-cell handover. The KgNB chaining that is
performed during a handover ensures that the KgNB is re-freshed with respect
to the RRC and UP COUNT after the procedure. The gNB/ng-eNB shall indicate to
the UE to change the current KgNB in intra-cell handover during this
procedure.

## 0x04 总结

综上所述，NR协议中对于用户会话重建流程时BEARER使用时存在重复使用，以及COUNT被同时清零的情况，导致了空口PDCP协议的用户面加密算法中用来生成Keystream的几个参数出现了重复，生成了重复的Keystream，从而对用户面数据进行加密时出现重用keystream的情况，导致CVD-2019-0030中用户通话被窃听的安全漏洞；

本文总结了5G空口安全的知识，对安全模式过程、PDCP加解密安全性等进行了一定的介绍，由于5G空口安全涉及到复杂的5GS控制面和用户面协议，还有很多方面未能深入探讨，例如5G安全中非常重要的鉴权，KEY的生成，用户签约信息安全等等。

## 0x05 参考文献

> 1.3GPP TS23.501. Technical Specification Group Services and System Aspects;
> System Architecture for the 5G System (5GS);  
> Stage 2 (Release 16). 09 2019
>
> 2.3GPP TS23.502. Technical Specification Group Services and System Aspects;
> Procedures for the 5G System (5GS); Stage 2 (Release 16), 09 2019
>
> 3.3GPP TS33.501. Technical Specification Group Services and System Aspects;
> Security architecture and procedures for 5G system (Release 15), 06 2019
>
> 4.3GPP TS38.323. Technical Specification Group Radio Access Network; NR;
> Packet Data Convergence Protocol (PDCP) specification (Release 16), 09 2020
>
> 5.3GPP TS36.331. Evolved Universal Terrestrial Radio Access (E-UTRA); Radio
> Resource Control (RRC); Protocol specification. 3rd Generation Partnership
> Project (3GPP), 06 2011
>
> 6.Call Me Maybe: Eavesdropping Encrypted LTE Calls With ReVoLTE, David
> Rupprecht, Katharina Kohls, Christina Pöpper, Thorsten Holz
>
> 7.3GPP TS38.331. 5G; NR; Radio Resource Control (RRC); 3rd Generation
> Partnership Project (3GPP), 2018
>
> 8.3GPP TS36.323. Evolved Universal Terrestrial Radio Access (E-UTRA); Packet
> Data Convergence Protocol (PDCP) specification. 3rd Generation Partnership
> Project (3GPP), 01 2010

