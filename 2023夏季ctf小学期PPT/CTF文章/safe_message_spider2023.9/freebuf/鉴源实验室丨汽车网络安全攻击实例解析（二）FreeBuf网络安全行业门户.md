**作者 |** 田铮 上海控安可信软件创新研究院项目经理

 **来源 |** 鉴源实验室

>  **引言：**
> 汽车信息安全事件频发使得汽车行业安全态势愈发紧张。这些汽车网络安全攻击事件，轻则给企业产品发布及产品口碑造成影响，重则导致大范围的汽车召回或股价受损，造成的经济损失和安全代价不可估量。本文则选取典型的智能网联汽车网络安全攻击实例展开详细介绍。

##  **01** **汽车信息安全威胁**

随着汽车不断向智能化、网联化、电动化、自动化的发展，软件定义汽车的趋势日益显著。目前智能网联汽车关键代码规模提升了10-100倍，代码漏洞呈指数级增长，同时汽车电子控制单元（ECU）的数量和车内连通性不断增长，导致汽车受到信息安全攻击的风险大大增加。

近年来频发的汽车信息安全事件加剧了社会各界对于智能汽车发展前景的担忧。比如2015年美国黑帽大会，研究人员通过车载娱乐系统发动伪装攻击，成功入侵Jeep
Cherokee远程获取汽车的关键功能操作权限
[1]。这次事件直接导致克莱斯勒公司在全球召回140万辆汽车，也促使汽车工业界更加严肃看待智能汽车面临的信息安全风险。

在此之后，汽车行业积极应对信息安全挑战，但搭载了先进信息通信技术的新款智能网联汽车同样无法完全回避网络攻击的威胁。例如，腾讯科恩实验室分别在2016年[2]、2017年[3]两次攻击特斯拉实现对车辆的无物理接触远程攻击，利用内核、浏览器、MCU固件、UDS协议及OTA更新过程中的多个高危安全漏洞，攻入到特斯拉汽车的CID、IC、网关以及自动驾驶模块，随后将其发现的安全漏洞交与特斯拉。2019年[4-5]，腾讯科恩实验室在多款宝马自动驾驶汽车上展示了利用车载信息娱乐系统和车载信息通信终端的漏洞远程无线入侵汽车，并进一步利用中央网关的安全缺陷实现向内部核心CAN总线注入恶意消息，获取了底层安全关键车内网络的控制权。2020年[6]，360
Sky-Go团队针对梅赛德斯奔驰的车载娱乐主机、车载通讯模块、车联网通信协议及后端服务等联网模块，发现19个安全漏洞并利用漏洞形成攻击链路，预计影响200余万辆梅赛德斯奔驰汽车。类似这样的“白帽黑客”式策略一直在汽车安全业内上演，以寻找、提交汽车的安全漏洞甚至修复漏洞。

##  **02** **攻击案例分析**

###  **2.1 攻击安利介绍**

2016
年[2]，科恩实验室成功利用多个高危安全漏洞对特斯拉实施了无物理接触远程攻击，实现了对特斯拉驻车状态下汽车天窗、转向灯、座椅、显示器、门锁系统的远程控制，以及行驶状态下对雨刷、后备箱、刹车系统的远程控制。科恩实验室是通过无线（Wi-Fi/蜂窝）进入，破坏许多车载系统，如 CID（Center Information Display，中控显示系统）、IC（Instrument
Cluster，仪表组） 、Parrot（无线及蓝牙模块）和网关等，然后将恶意 CAN 消息注入 CAN
总线。这是全球范围内第一次通过安全漏洞成功无物理接触远程攻入特斯拉并实现任意车身和行车控制。

###  **2.2 案例分析**

 **2.2.1 研究对象**

科恩实验室成功在特斯拉Model S P85 和 P75 上完成了测试，对应的车型及版本信息如下图1和表1所示。

![8421.png](https://image.3001.net/images/20230809/1691547088_64d2f5d0a62a58e325b06.png!small)

图1 研究对象—Tesla Model S

![8422.png](https://image.3001.net/images/20230809/1691547089_64d2f5d19e0f5589da437.png!small)

表1 测试车辆版本信息

 **2.2.2 攻击步骤解析**

1）攻击浏览器

在攻击开始前，首先需要确定攻击面。每辆特斯拉汽车中都有车辆提供的Wi-Fi热点，很多用户会将SSID的信息保存在车上以便用于自动连接。如果伪造这个Wi-Fi热点，并将QtCarBrowser的流量重定向到攻击者的域名，即可实现远程攻击特斯拉汽车。此外，当在蜂窝模式下，通过建立精心设计的域名，网络钓鱼和用户输入错误也会导致远程触发浏览器漏洞，实现在没有物理访问的情况下远程交付漏洞利用。

通过特斯拉浏览器的用户代理可推断出QtWebkit的版本在2.2.x，该版本的QtWebkit存在许多漏洞。研究者获取特斯拉CID的QtCarBrowser二进制文件后，通过利用浏览器的这两个漏洞来获得特斯拉CID的shell，从而实现任意代码执行。

第一个漏洞存在于函数JSArray::sort()中。这个函数将在JavaScript代码中调用数组的sort()方法函数时被调用。存在漏洞的函数代码片段如图2所示，如果compareFunction为JSArray::shiftCount()，则m_vector的长度将被改变，并且整个m_vector结构将被转移到另一个地方。然而，局部变量指针存储仍然指向旧位置，导致内存损坏。当非移位数组调用
sort() 触发此问题时，本地指针存储引用的变量映射始终与新存储结构的变量 m_length
重叠，导致崩溃。通过利用JSArray::sort()中的漏洞，可获取JSCell地址。

![8423.png](https://image.3001.net/images/20230809/1691547090_64d2f5d25c272e1db317e.png!small)

图2 易受攻击的函数代码片段

第二个漏洞则是由科恩实验室发现的CVE-2011-3928，可用于内存泄漏。如图3所示，若分配多个 Element
结构，在static_cast后，HTMLInputElement的成员m_data将与Element的指针m_next重叠。此外，将第二个和第三个Element结构作为子元素插入到同一标签中，m_next和m_data都指向第三个Element结构。由于m_data指向StringImpl结构，且该StringImpl结构与
Element结构重叠。StringImpl结构体的成员m_data始终是固定值1，StringImpl结构体的m_length始终是一个足够大的指针，足以读取整个内存。

![8424.png](https://image.3001.net/images/20230809/1691547091_64d2f5d3450debcbf03e7.png!small)

图3 CVE-2011-3928中的漏洞

2）本地权限升级

在基于浏览器攻击获得远程shell后，仍无法获得任意权限，这就需要另一个漏洞来从AppArmor中逃脱，并获得比浏览器进程上下文更高的权限。研究者发现，特斯拉上仍存在著名的ARM
Linux漏洞CVE-2013-6282（即：内核API中缺少访问检查）。研究者利用该漏洞，首先修补了setresuid()系统调用以获得root权限，然后调用reset_security_ops()来禁用AppArmor，实现了在内核上下文中获得任意读/写权限。

3）未经授权访问嵌入式系统

在特斯拉Model S上除了CID还有三个更重要的独立嵌入式系统，即IC,
Parrot和Gateway，如图4所示。由于网络设计上的缺陷和缺乏强大的密码保护，研究者可通过远程攻击获得这三个系统的root访问权限。

![8425.png](https://image.3001.net/images/20230809/1691547092_64d2f5d43c8d4f45e3230.png!small)

图4 车载网络的重要设备

 **·** IC

在 CID 中获得 root 权限后，研究者可在没有任何密码的情况下通过“ssh root@ic”的命令获取 IC 上的 root
访问权限，并通过SSH登录IC。

此外可实现 CID 和 IC 间的相互访问。CID包含一个密钥轮换方案，每24小时从母舰接收用户的随机新令牌。CID 会以明文形式在 IC
的文件系统中设置密钥，这意味着即使只能访问 IC，也可以SSH到CID 并获得root权限。

 **·** Parrot

Parrot模块是一个第三方模块，型号是FC6050W，它集成了无线及蓝牙功能，可通过USB协议与CID相连。通过扫描Parrot上的开放端口，研究者发现端口23为Telnet打开。一个重要漏洞在于Telnet是匿名的，研究者可通过“nc
parrot 23”的简单命令来访问和控制Parrot模块。

 **·** Gateway

Gateway看起来比IC和Parot安全得多。研究者首先利用二进制文件gw-diag在端口23上唤醒Gateway的后门，找到Gateway的shell
入口。然后，研究者通过逆向固件来获得其中的token，获得Gateway的访问权限。

4）ECU编程

通过拆卸CID单元，研究者发现了与网关ECU
相连的SD卡中存在一些调试和升级相关的日志文件。这些文件中描述了整个升级的详细过程，包括将十六进制文件发送到ECU，配置继电器开关和其他重要步骤，可通过拆解文件查看到重要的内部信息。

对于更新软件来说，整个更新由在内存地址0x40006AE4位置的函数控制。它将首先对文件进行安全检查并设置其工作模式，以确保整个汽车在更新过程中保持物理安全。然后绕过完整性检查，并将固件刷写到网关，成功将定制的代码编程到ECU中，具体操作步骤如下：

 **①** 解压缩release.tgz文件，确保校验和值满足要求。

 **②** 检查压缩文件中是否存在manifest文件，并从中获得该固件包中的版本信息。

 **③**
处理程序中每个“.Hex”文件。将十六进制文件转换为二进制流，并使用UDS协议发送固件。目标芯片上的引导加载程序需要将十六进制文件写入flash，并在每次启动时检查应用程序是否有效。最后检查固件是否已发送并编程到目标ECU。

 **④** 处理完所有这些文件后，创建一个日志，并重新启动。

5）网关逆向工程和攻击

在网关上运行的许多重要任务存在漏洞，这些任务几乎可与CAN总线上的ECU进行任何类型的通信。研究者可随时注入任何 CAN 消息，并使用补丁来阻止一些必要的
CAN 信号，实现车辆的车身控制，具体攻击过程包括：

 **①** 网关将20100和20101端口的UDP广播传输到CAN总线上，研究者可通过伪造UDP信号来实现门锁系统的控制。

 **②** 研究者可通过将诊断功能0x01替换为诊断功能0x04，并注入CAN消息，将其发送到ID为0x45的PT-CAN总线，实现在汽车运行或停止时打开灯的操作。

 **③** 研究者定位到固件中存储的结构体后，通过更改固件中的目标ID来阻止一些重要消息（例如BDY
CAN上0x218的ID），实现在汽车行驶状态时打开后备箱或禁用自动锁定功能。

6）攻击UDS/CAN总线

统一诊断服务 (UDS) 已编入 ISO-14229 中，并允许诊断控制车载电子控制单元 (ECU)
上的功能。研究者通过将电子稳定程序（ESP）设置为低速诊断编程会话，利用Bash shell 脚本通过网关注入 UDS 数据帧并低速禁用 ESP
ECU，最终导致CAN-CH 总线上没有任何车速相关的CAN消息，并且汽车高速行驶时IC的实时速度值无法更新。此外，车辆会显示有关防抱死制动系统 (ABS)
的警报信息，引发转向和制动失灵的安全问题。

![8426.png](https://image.3001.net/images/20230809/1691547093_64d2f5d51b86df75d6f6a.png!small)

图5 科恩实验室制作的CAN控制器

  

##  **03** **总结**

本文介绍了科恩实验室在实现特斯拉Model
S远程控制的研究中所涉及的漏洞和相关技术细节。此次安全攻击事件，是首例利用CAN总线进行远程攻击，从而对特斯拉汽车停车和驾驶模式下进行远程控制的典型案例。最终，科恩实验室将研究报告及漏洞交予特斯拉，特斯拉在10天内做出回应，并利用其OTA
机制进行了浏览器、内核和ECU固件等方面的漏洞修复和安全更新，将代码签名保护引入了特斯拉汽车以保护车载系统。

## 参考文献

[1] Charlie Miller,Chris Valasek.Remote exploitation of an unaltered passenger
vehicle[C]. Black Hat USA,2015.

[2] Keen Security Lab of Tencent. Free-fall:hacking Tesla from wireless to CAN
bus [C]. Black Hat USA,2016.

[3] Keen Security Lab of Tencent. Over-the-air: how we remotely compromised
the gateway,BCM,and autopilot ECUs of Tesla cars[C]. Black Hat USA,2017.

[4]Cai Zhiqiang , Wang Aohui , Zhang Wenkai , Gruffke M ,Schweppe H . 0-days &
Mitigations: Roadways to Exploit and Secure Connected BMW Cars[C]. Black Hat
USA,2019.

[5] Keen Security Lab of Tencent. Experimental Security Assessment of BMW
Cars: A Summary Report[EB/OL].
https://keenlab.tencent.com/en/whitepapers/Experimental_Security_Assessment_of_BMW_Cars_by_KeenLab.pdf,2018.

[6] 360 Sky-Go group. Security Research Report on Mercedes-Benz Cars [EB/OL].
https://skygo.360.net/archive/Security-Research-Report-on-Mercedes-Benz-Cars-en.pdf,2020.

