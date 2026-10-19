据bleepingcomputer消息，SafeBreach Labs
安全研究人员最新发现，伊朗黑客正在窃取谷歌和Instagram的波斯语用户信息。攻击者使用的是一个基于PowerShell的信息窃取器，安全研究人员称之为PowerShortShell。

该信息窃取器还用来监视 Telegram，以及从受感染的设备中收集系统信息。这些窃取来的信息被发送至攻击者控制的服务器。

今年7月，SafeBreach Labs 在鱼叉式钓鱼邮件中发现了此次攻击，Shadow Chaser
Group于9月在Twitter上对此进行了公开报道。

攻击者利用微软MSHTML远程代码执行（RCE）漏洞（编号 CVE-2021-40444），向Windows用户发送恶意的Winword附件。

##  **从受害者分布推算攻击者是谁？**

PowerShortShell 窃取程序由下载到受感染系统上的 DLL 执行。这一程序启动后，PowerShell
脚本开始收集数据和屏幕快照，并将其发送至攻击者控制的服务器。

“研究表明，从受害者分布来看，接近一半的受害者位于美国。从微软Word文档中将'科罗纳大屠杀'归咎于伊朗领导人的相关内容，以及收集的数据分析来看，我们猜测受害者可能是对伊朗伊斯兰政权构成威胁、且生活在国外的伊朗人。”SafeBreach
Labs安全研究主任Tomer Bar说。“对手可能与伊朗的伊斯兰政权有联系，因为监视 Telegram是伊朗威胁者（如Infy、Ferocious
Kitten和Rampant Kitten）的惯用手段。”

![](https://image.3001.net/images/20211126/1637918198_61a0a5f667470c5191289.png!small)受害者分布图（SafeBreach
Labs）

##  **漏洞被广泛利用不足为奇**

微软MSTHML的CVE-2021-40444 RCE漏洞从8月18日开始就被广泛利用，两周之后微软才发布安全公告，三周后修复漏洞的补丁才发布出来。

最近，这一漏洞被Magniber勒索软件团伙利用，与恶意广告一起感染受害者，并加密他们的设备。

微软还表示，包括勒索软件团伙在内的多个威胁者，都瞄准了这个Windows MSHTML
RCE漏洞，通过制作带有恶意软件的Office文档来实现网络钓鱼攻击。这些攻击滥用了 CVE-2021-40444 漏洞，“作为分发自定义 Cobalt
Strike Beacon 加载器初始访问活动的一部分”。

部署的信标与与几个网络犯罪活动有关的恶意基础设施进行通信，包括但不限于人为操作的勒索软件。

![](https://image.3001.net/images/20211126/1637918263_61a0a637d96ee5f711189.png!small)CVE-2021-40444
攻击链（微软）

不足为奇的是，越来越多的攻击者正在使用 CVE-2021-40444 漏洞。因为攻击者早在补丁发布之前就在暗网传播漏洞利用和验证教程。

从其传播的漏洞利用教程来看，具体操作很容易实现，任何人都可以利用CVE-2021-40444漏洞发起攻击，只需一个可以将恶意文档和CAB文件分发到受攻击系统的Python服务器。

  

> 参考来源：https://www.bleepingcomputer.com/news/security/hackers-exploit-> microsoft-mshtml-bug-to-steal-google-instagram-creds/

