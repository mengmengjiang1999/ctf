11月8日-9日，韩国2018 POC（Power of
Community）安全大会在首尔揭开帷幕，汇聚各国顶级黑客高手，共同探讨安全界的热门议题。POC是韩国最大的安全技术峰会，今年已经是第十二届，2006年一群韩国黑客与安全研究专家决定以“交流技术、分享知识”为目的举办会议，并将其命名为POC(Power
of Community，社区力量)，它是目前互联网安全界举办历史最悠久的大会之一。时至今日，POC已经成为了国际知名的安全技术交流峰会。

**【议题PPT下载】：<http://powerofcommunity.net/2018.htm>**

  

### WebGoat.SDWAN.Net in Depth

**演讲者：Denis Kolegov, Oleg Broslavsky**

今天，«SD-WAN»是一个非常热门和吸引人的话题。软件定义的WAN（SD-WAN）是一种基于软件定义网络（SDN）方法的技术，应用于企业网络中的广域网（WAN）。根据Gartner的预测研究，到2020年，超过50％的路由器将被SD-WAN解决方案所取代。

在本演讲中，我们披露了广泛且最流行的SD-WAN产品中的一组漏洞，包括Citrix NetScaler和Silver Peak
EdgeConnect。我们介绍了我们研究的新结果，考虑了不安全设计的一些技术细节并发现了漏洞，并描述了可能允许攻击者危及SD-WAN控制和数据平面的不同攻击场景。

  

### Windows Kernel Fuzzing

**Gmliu @ Tencent Zhanlu Lab**

近年来，Windows内核安全性受到高度重视，Microsoft已经增强了Windows内核的安全性。由于这个原因，内核问题越来越少，安全研究人员更难找到内核错误。所以我开发了一个工具来帮助安全研究人员fuzz
Windows内核。

在本次演讲中，我将首先介绍一种新的方法来fuzz
Windows内核。然后，我将展示一个fuzz的框架，它是如何工作的，并讨论一些Windows内核fuzz测试的方法。fuzz测试侧重于Windows内核对象以及与不同对象的关系。本演讲将介绍GDI对象和其他一些Windows内核对象。我将展示一些我在fuzz测试框架中发现的崩溃案例。最后，我将分享一些Windows崩溃详细信息并显示漏洞利用演示。

  

### Document parsers "research" as passive income

**演讲者：Jaanus Kääp**

从2015年底开始，我在MS
Office产品和Adobe应用程序中使用了相同的基本方法和工具进行漏洞研究。这个演讲描述了一些有用的方法和小技巧，我也将公开我的完整工具集。

  

### How to Exploit Blockchain Public Chain and Smart Contract Vulnerability

**演讲者：Jiafeng Li, Zuotong Feng @ Qihoo 360**

区块链并不完美，存在许多挑战，安全威胁是区块链面临的最重要问题之一。随着其经济价值持续上升，它促使攻击者使用各种攻击手段获取利益。

本演讲将介绍我们的团队在区块链研究和公共场所发现的攻击方法，如以太坊Geth节点Dos，EOS节点攻击，智能合约呼叫注入攻击，整数溢出和其他攻击，我将详细说明如何我找到了，我将介绍使用的方法，跟踪的功能，使用的工具等。每个漏洞都非常有趣，我期待与大家分享。据我们所知，这将是第一个发布2018年区块链安全白皮书的演示文稿。

  

### Pwning Microsoft Edge Browser: From Memory Safety Vulnerability to Remote
Code Execution

**演讲者：Jin Liu & Chong Xu**

在过去几年中，漏洞利用的攻击和防御已经迅速发展，特别是对于那些高风险的应用程序，例如Microsoft
Edge浏览器。Edge浏览器和Windows操作系统引入了许多新的缓解功能，如CFG，ACG和Win32K Type
Isolation。虽然这些缓解确实有助于提高漏洞利用作者的标准，但这种猫捉老鼠的游戏远未结束。

在本次演讲中，我们将介绍几个有趣的漏洞和开发技巧示例，并讨论如何在Windows 10 x64上进行可靠的Edge RCE漏洞利用。

  

### Practical evading attacks on commercial AI image recognition services

**演讲者：Kang Li**

在过去的一年中，我们通过利用软件漏洞和算法漏洞展示了对AI应用程序的各种攻击。本演讲为主要互联网公司提供的公共图像识别API提供了新的逃避攻击。

对基于人工智能的图像识别的攻击是人工智能领域的热门话题，尤其是对抗机器学习的形式。产生对抗性攻击是一个非常活跃的研究课题。然而，学术工具产生的对抗性样本尽管在研究环境中取得了成功，但在实践中不会对商业AI服务和API产生错误的分类效果。大多数基于AI的商业图像识别系统采用防御性方法来过滤其输入，这些过滤器使得学术对抗的例子无效。

这些防御性过滤器的设置和参数不为公众所知，因此我们设计了盲目绕过和击败此类过滤器的方法和工具。我们已成功演示针对大多数商用AI基于图像识别服务的针对性逃避攻击。在本次演讲中，我们将展示允许攻击者欺骗多个众所周知的基于AI的商业服务的方法和威胁示例。

  

### Era of iOS 12 with A12: End of iOS War?

**演讲者：Liang Chen @ KeenLab of Tencent**

  

### 802.11 Smart Fuzzing

**演讲者：Lidong LI & Naijie XU @ CyberPeace**

近年来，wifi不仅被用作家庭网络，而且更多的物联网设备和互联网汽车正在使用wifi接口。本主题主要用于802.11-wifi协议的fuzz测试。我们将展示一些关于802.11
fuzz测试和我们研究的技巧。

  

### Exploiting Chrome IPC

**演讲者：Ned Williamson**

自从Chrome渲染器进程中的win32k锁定以来，在Windows上转移Chrome沙箱变得更加困难。最近成功的竞争漏洞发生在2015年。

虽然每个人都专注于win32k，但Chrome浏览器沙箱的安全性却被忽略了。通过应用新的fuzz测试策略，可以揭示许多漏洞，其中一个我曾经在saelo和niklasb的帮助下在Hack2Win上展示了完整的链式漏洞利用。在本次演讲中，我希望通过使用简单且可靠的方式，使用有针对性的fuzz测试来展示我是如何发现这些错误的，并简要介绍我们如何利用免费bug来完全逃离沙箱。

  

### Automating Windows Kernel Pool Overflow/Corruption Exploits Development

**演讲者：Nikita Tarakanov**

在本次演讲中，我们将介绍一种新的开发框架，以自动利用Windows内核池溢出/损坏漏洞。从技术上讲，我们的框架利用了内核池操作技术和各种开发技术（其中一些是新的，从未发布过）。我们证明了这个新的开发框架从许多方面促进了漏洞利用。首先，它适用于从Windows
7到Windows 10 RedStone
4的所有Windows版本。其次，它绕过所有内核安全缓解，包括池元数据强化，对象头类型索引编码，SMEP，KMCI。

  

### IPC MitM: Exploiting a Fun Logic Bug for Kernel-Mode Code Execution on
MacOS

**演讲者：Samuel Groß**

本演讲首先将重新讨论macOS和iOS上的基本IPC原语以及它们的一般OS设计。然后，将解释一个有趣的逻辑漏洞，允许攻击者拦截和操纵用户域进程之间的IPC流量。最后，将介绍利用此漏洞的不同方法：首先通过以sudo为目标获取root权限，然后通过欺骗kextutil将无符号kext加载到内核中，从而绕过SIP并获得内核模式代码执行。此漏洞在Pwn2Own
2018中用作针对macOS上Safari的攻击链的最后一部分，将发布完整的漏洞利用程序以及实现利用所需的XPC协议部分的库。

  

### IOService Becomes a Grandpa

**演讲者：Tielei Wang, Hao Xu @ PanguTeam**

本演讲将首先介绍IOKit，这是XNU内核的面向对象设备驱动程序框架，并深入介绍了类继承等功能的实现。然后，我们将检查IOKit用户客户端创建过程并分析被忽略的攻击面。在此发现的指导下，我们将在最新的iOS
/ macOS内核上介绍和分析一些新的类似漏洞。

  

### Vulnerability analysis of Z-wave products used in Korea

**演讲者：WYP**

本演讲重点介绍使用Z-Wave无线通信协议产品的漏洞，该协议具有良好的可用性、可扩展性和低功耗协议的优点。演讲主要分为两部分：第一部分介绍ZWave的相关研究和发展趋势，并从安全角度介绍直接分析Z-Wave产品的结果。第二部分演示使用我们创建的Z-Wave欺骗工具通过任意创建的数据包控制商业产品的过程。

我们将展示对几种产品的攻击，包括一些配备了主要公司通信模块的智能门锁，还介绍并演示各种攻击媒介，包括DoS攻击和Replay攻击。尽管这个演示基于一些公司的特定产品，但漏洞和攻击通常可以应用于所有使用z-Wave协议的产品。

  

### Baby I can drive your car: remotely hacking Telematics CAN-connected
devices

**演讲者：Yannay Livneh**

近年来，为车辆管理提供额外服务的行业Telematics正在崛起，为车辆提供许多服务，如车队管理、基于使用的保险、实时位置跟踪、车内连接等。

为了改善Telematics设备提供的服务（例如实时故障报告），其中许多设备连接到车辆的计算机网络以及外部世界 -例如互联网。因此，它们是想要远程连接到车辆电子系统的攻击者的有利目标。如果成功执行这样的情况，则可能产生严重的结果并影响车辆的安全性。

在我们的研究中，我们分析了常见Telematics设备的安全性。我们发现攻击者可以通过多种方式破坏设备（本地和远程）。使用受攻击的设备，攻击者可以通过蜂窝调制解调器连接向车载CAN网络发送消息，从而允许攻击者控制关键的车辆功能。上述假设的情景在现在是有可能发生的。

攻击者可以接管这些设备，导致车辆行为不端，甚至出现更多难以想象的情况。

我们在演讲中讨论研究和结果，解释攻击者可以使设备执行命令的多个漏洞和攻击媒介。然后我们描述了一个可行的攻击计划，攻击者可以通过该计划完全控制设备。最后，我们以完整的POC结束，显示了攻击情形的样子，即攻击者不用靠近汽车附近，就能通过互联网激活汽车功能。

  

### SSRF To RCE In Java

**演讲者：Yongtao Wang, Sai Cheng, Jie Fu @ Qihoo 360**

SSRF不是一项新技术，在过去的几十年中，许多安全研究人员提出了各种攻击。我们的研究发现JDK中存在高风险的安全漏洞，并且利用此安全漏洞可以获得WINDOWS凭证。在应用程序具有SSRF漏洞的情况下，可以实现RCE的效果，这个漏洞已经被Oracle官方网站承认为重要的补丁更新。在本演讲中，我们将详细介绍漏洞原理、发现过程、攻击场景和攻击过程。之后，我们将针对此漏洞发布漏洞利用工具。

  

### Diving into Windows Defender Application Guard

**演讲者：Yunhai Zhang @ NSFOCUS security team**

随着Windows 10 RS3的发布，引入了一种独特的基于硬件的隔离技术，称为Windows Defender Application
Guard（WDAG）。通过使用本机Windows
Hypervisor，WDAG旨在将不受信任的网站和PDF文档隔离在与操作系统分离的轻量级容器中，从而保护桌面PC。

在本演示中，我们将深入研究WDAG的内部结构。第一部分将重点介绍WDAG的内部工作原理，其中讨论了如何创建容器，如何在容器中启动应用程序，容器的安全机制等主题。第二部分将展示如何修改容器以在容器内构建调试环境。最后一部分将讨论WDAG的攻击面。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/748/>

