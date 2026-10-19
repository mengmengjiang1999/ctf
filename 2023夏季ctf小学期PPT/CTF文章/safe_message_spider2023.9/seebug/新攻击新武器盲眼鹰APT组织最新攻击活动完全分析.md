**作者：启明星辰 ADLab  
公众号：<https://mp.weixin.qq.com/s/T15pdznZZ4ZsVVpcKrWlnQ>**

## **一、概述**

启明星辰ADLab实验室在近几个月内，通过威胁情报检测系统接连捕获到多起针对哥伦比亚国家的政府部门，金融、银行、保险等行业及卫生和制药机构发起的钓鱼邮件定向攻击。攻击者以“冠状病毒检测紧急告知单”或“刑事诉讼通知单”等命名的诱饵文档作为邮件附件，并配合鱼叉邮件向攻击目标电脑植入远控木马。从邮件分析结果来看，攻击者会将邮件的来源伪装成哥伦比亚国家卫生部、国家税务和海关总署、民事身份登记处、检察院以及移民局等政府部门，以加强其邮件的真实性。我们通过对攻击者伪装的来源信息、域名使用偏好、IP地址关联及地理位置等特性进行对比分析，发现该系列攻击来源于盲眼鹰组织，但采用的攻击武器较以往完全不同。盲眼鹰首次被披露于2019年初，是一个疑似来自南美洲的APT组织，其最早活跃时间可追溯到2018年，主要针对哥伦比亚政府和大型公司进行攻击。

在对攻击活动深入分析后，我们发现该组织在我们发现的这批攻击中采用了更为先进攻击技术和反追踪技术。在以往的攻击中，该组织多使用MHTML格式的恶意文档作为攻击附件，而在本次攻击过程中，该黑客组织使用一个无恶意的文档作为媒介，诱使目标下载文档中提供恶意短链接（该短链接指向一个加密过MHTML的恶意文档），这大大提高攻击的有效性，其不仅能够绕过邮件安全防护系统和入侵检测系统，而且大大的降低了被杀毒软件查杀的概率（我们捕获的许多样本在VT上的查杀率均0，部分样本也长期保持着低于5%的极低查杀率）；我们发现的这批攻击中，该黑客组织放弃了以往常用的Imminent
Monitor RAT，采用了一款隐蔽能力和免杀能力更强的RAT--AsyncRAT，同时结合复杂多层加密与代码嵌套手段来提供反分析能力和反检测能力。

AsyncRAT是来源于国外的一款远控木马，其除了能够对目标进行最基本的远程间谍活动外，还可使用USB设备突破物理隔离、使用bot
killer清除目标上的竞争对手等。该木马最具特点的是采用不落地的无害模块作为目标的僵尸进程， 并采用 **“propelling in
use，destroy after use”**
的工作模式，即分解攻击任务为子任务，每个子任务以一个单独的DLL模块来实现，黑客执行任务时由多个子任务DLL模块按照一定的执行序列来实现，同时对完成任务的模块进行及时销毁。这种工作模式将一个完整恶意任务分解成多个无害的子任务，能够有效地躲避一些复杂安全防护策略，同时也能有效地防止取证分析人员获取其核心攻击模块。

此外，该黑客组织还采用了 **“Double Flux+Fast VPN”**
技术来达到反追踪和反侦测的目的。我们通过对攻击者使用的C&C基础设施进行分析发现，这批攻击的C&C域名是通过DNSExit.com来动态分派IP地址(IP地址是动态变化的，几乎都归属于哥伦比亚的ISP)。实际上，DNSExit不仅是一个“1(dns)对n(IP)”的服务，更是一个“m(dns)对n(IP)”，因此其应该采用了“double
flux”技术来规避溯源与追踪。不仅如此，黑客组织使用这种服务的背后还加了一层VPN，也就是说通过“Double
Flux”得到的IP地址并不是黑客真正的IP地址， 其只是一系列的VPN节点(节点的IP地址由Unus.Ins服务商提供)，因此借用”fast
flux”命名法我们将这种反追踪技术称为Fast VPN。攻击者利用“Double Flux+Fast
VPN”技术来作为攻击载荷和木马回连的通道，使得黑客的攻击变得非常难以追踪和溯源。

## **二、 攻击活动分析**

本章总结了黑客组织近期的攻击活动事件以及本次活动中使用的攻击手法。

### **2.1 近期攻击活动**

启明星辰ADLab实验室基于原始线索对黑客组织本次的攻击活动进行了全面追踪、关联和分析，发现此次活动最早可追溯到2019年9月，且近期活动主要以COVID-19相关内容作为钓鱼诱饵。我们综合所有的威胁情报数据，梳理了本次该组织发起的所有攻击事件，并绘制出以下攻击事件时间线。

![img](https://images.seebug.org/content/images/2020/08/19/1597822056000-wpsiluNJ5.jpg-w331s)

图2-1 APT组织近期攻击事件时间线

### **2.2 攻击手法**

在本次攻击活动中，我们发现盲眼鹰APT组织主要采用鱼叉邮件作为初期攻击方式。攻击者伪装成来自哥伦比亚卫生部、哥伦比亚国家总检察院、哥伦比亚移民局、哥伦比亚国家税务和海关总署以及哥伦比亚民事身份登记处等部门，向使用西班牙语言的南美地区（特别是哥伦比亚国家）的政府部门，金融、银行、保险等公司，以及卫生和制药机构的相关人员投递恶意攻击邮件。邮件主题均与攻击者所仿冒的政府部门文件题材相关，并在邮件正文添加针对附件文件的诱导性描述和附件查看密码等信息，更有利于加强邮件的真实性，诱使受害者启用恶意宏代码，进而向攻击目标机器上植入木马程序，以实施对入侵设备的远程控制、窃取机密数据、系统破坏等恶意行为。

启明星辰ADLab实验室通过对该组织近期攻击的监测和关联分析，发现了多个与其相关的邮件，下面我们列举出部分邮件内容以及针对性的诱饵文档。

#### **2.2.1 钓鱼邮件详情**

**伪装成哥伦比亚卫生部：**

1） 图2-2是攻击者伪装成哥伦比亚卫生部的攻击邮件之一。邮件主题为“Usted ha sido citado para una prueba
obligatoria de (COVID-19)”（翻译后为：“您被要求参加强制性检测（COVID-19）”）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822065000-wpsyWk5o2.jpg-w331s)

图2-2 伪装成哥伦比亚卫生部邮件之一

2） 图2-3是攻击者伪装成哥伦比亚卫生部的攻击邮件之二。邮件主题为“Le hemos llamado en repetidas ocaciones y
no ha sido posible contactarle por favor leer comunicado
urgente”（翻译后为：“我们已经多次致电给您，无法联系到您，请阅读紧急通知”）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822066000-wpswF2lrx.jpg-w331s)

图2-3 伪装成哥伦比亚卫生部邮件之二

3） 图2-4是攻击者伪装成哥伦比亚卫生部的攻击邮件之三。邮件主题为“Detectamos en su sector la presencia de
COVID-19 ( Corona virus ) intentamos comunicarnos via telefonica con
usted”（翻译后为：“我们在您的部门发现了COVID-19( Corona virus )，并尝试通过电话与您联系”）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822066000-wpsvX1ap6.jpg-w331s)

图2-4伪装成哥伦比亚卫生部邮件之三内容

**伪装成哥伦比亚国家税务和海关总署：**

图2-5是攻击者伪装成哥伦比亚国家税务和海关总署的攻击邮件。邮件主题为

“Procederemos con una orden de embargo a las cuentas bancarias encontradas a
su nombre”（翻译后为：“我们将对以您名义发现的银行账户发出冻结令”）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822067000-wpsnMhSFE.jpg-w331s)

图2-5 伪装成哥伦比亚国家税务和海关总署的邮件

**伪装成哥伦比亚民事身份登记处：**

图2-6是攻击者伪装成哥伦比亚民事身份登记处的攻击邮件。邮件主题为“Su cedula de ciudadania ha sido reportada
como robada en nuestro sistema”（翻译后为：“您的公民证已在我们的系统报失”）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822067000-wpsAzeZ12.jpg-w331s)

图2-6 伪装成哥伦比亚民事身份登记处的邮件

**伪装成哥伦比亚检察院：**

图2-7是攻击者伪装成哥伦比亚检察院的攻击邮件。邮件主题为“El presente es el requerimiento enviado a
declarar por el proceso iniciado en su contra (ultimo
aviso)”（翻译后为：“这是针对您发起的处理流程声明（最后通知）”）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822067000-wpsUf3v8n.jpg-w331s)

图2-7 伪装成哥伦比亚检察院的邮件

**伪装成哥伦比亚移民局：**

图2-8是攻击者伪装成哥伦比亚移民局的攻击邮件。邮件主题为“Comunicado 710297647: Proceso Penal
Pendiente”（翻译后为：“声明710297647：待定刑事诉讼法”）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822067000-wpsWYKMxL.jpg-w331s)

图2-8 伪装成哥伦比亚移民局的邮件内容

#### **2.2.2 诱饵文档**

根据现有的情报分析表明，该组织以往最常用的邮件附件是带有恶意宏的MHTML格式的DOC文档。我们对近期捕获到的相关攻击样本进行分析后，发现在大多数情况下，攻击者开始使用带有短链接的RTF或PDF文档来作为恶意附件，以绕过邮箱网关的检测。表2-1列出了黑客组织在此次攻击活动中使用的恶意文档信息。

**文件名** | **时间戳**  
---|---  
citacion prueba covid.pdf | 2020-07-09 11:06:40  
citacion prueba covid.pdf | 2020-06-19 14:11:05  
Comunicado.pdf | 2020-04-25 13:11:38  
minsaludcomunicado.pdf | 2020-03-04 22:17:40  
estado de cuenta.pdf | 2020-02-25 21:58:29  
reactivar mi cedula.pdf | 2020-02-03 23:18:38  
DIAN estado de cuenta.rtf | 2019-11-04 15:01:00  
pdfproceso.rtf | 2019-10-25 14:09:00  
Proceso.rtf | 2019-08-26 21:00:00  
  
表2-1 相关恶意文档信息

**1）案例1**

    
    
    附件RTF文档中内嵌一个名为“VER PROCESO”的跳转链接，其指向的恶意链接使用的是IP Logger短链接服务。

![img](https://images.seebug.org/content/images/2020/08/19/1597822068000-wpsJ3R8Yb.jpg-w331s)

图2-9 RTF文档内容

![img](https://images.seebug.org/content/images/2020/08/19/1597822068000-wpsKTvvcH.jpg-w331s)

图2-10 IP Logger短链接平台

**2）案例2**

附件PDF文档中内嵌一个名为“Ver
comunicado”的跳转链接和一行文本信息（仅用于提升文档的可信度）。其指向的恶意链接使用的是Acortarurl短链接服务。

![img](https://images.seebug.org/content/images/2020/08/19/1597822068000-wpsaM0nMd.jpg-w331s)

图2-11 PDF文档内容

## **三、溯源与关联分析**

在对本次攻击样本的IOC进行深入追踪溯源后，我们挖掘出黑客组织更多的C2服务器信息。后文，我们将结合目前掌握的情报数据和公开的研究报告资料信息，来对此次攻击事件进行详细的组织关联分析。

#### **3.1 C &C基础设施分析**

通过提取和关联所有样本中的C&C服务器相关信息，我们发现黑客组织所使用的基础设施都位于哥伦比亚、哥斯达黎加和巴拿马，所有IP都归属于哥伦比亚的ISP。查看这些IP的具体信息（如图3-1）可以看到，此IP段的网络服务提供商是Unus.Ins公司，该公司操控着26209个IP地址，且几乎所有这些IP地址都是提供给匿名VPN服务使用，例如Powerhouse
Management.Inc（phmgmt.com）。由于该ISP在网络中的流量大多数具有欺诈性，因此美国反欺诈安全公司Scamalytics将其标注为高欺诈风险ISP（如图3-2）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822068000-wpsyBHSg0.jpg-w331s)

图3-1 相关IP具体信息

![img](https://images.seebug.org/content/images/2020/08/19/1597822068000-wpscymbeL.jpg-w331s)

图3-2 Scamalytics公司标注信息

图3-3为该组织在此次攻击活动中使用的部分域名、IP、PE文件和Office文件的对应关系：

![img](https://images.seebug.org/content/images/2020/08/19/1597822069000-wpsmMUEVO.jpg-w331s)

图3-3 对应关系图

该组织使用的域名是在国外DNSExit.com平台上免费注册的三级子域（该平台提供的免费域实际上是二级域，如图3-4），且这些子域所指向的IP地址被频繁的更换（如图3-5）。如果一个C2服务器被关闭，攻击者则可以快速地更新DNS记录指向新服务器，恢复连接。攻击者利用域名注册商提供的DNS服务（double
flux），再配合使用VPN服务（fast VPN）作为攻击载荷和木马回连的通道，以达到反追踪和反侦测的目的。

![img](https://images.seebug.org/content/images/2020/08/19/1597822069000-wpsZ80qw5.jpg-w331s)

图3-4 DNSExit.com平台

![img](https://images.seebug.org/content/images/2020/08/19/1597822069000-wps9biF3H.jpg-w331s)

图3-5 域名指向的IP

#### **3.2关联和技术演进分析**

我们从本次事件中黑客组织所使用的样本、C&C服务器等层面进行了关联分析，并结合该组织早期攻击活动中的相关特性，得出以下几处重要的关联点。

##### **3.2.1 伪装成来源信息**

在早期的攻击活动中，盲眼鹰组织惯于将自身伪装成哥伦比亚国家民事登记处、哥伦比亚国家税务和海关总署等部门来对哥伦比亚的政府和金融机构进行攻击。而在本次攻击事件中，攻击者所使用邮件的伪装来源信息除了同该组织具有一定的重叠以外，还新增了一些哥伦比亚其他政府部门信息。具体详见表3-1。

**诱饵伪装来源（2018年4月-2019年2月）** | **诱饵伪装来源（2019年9月-2020年7月）**  
---|---  
哥伦比亚民事登记处 | 哥伦比亚民事登记处  
哥伦比亚国家税务和海关总署 | 哥伦比亚国家税务和海关总署  
哥伦比亚国家司法部门 | 哥伦比亚国家总检察院  
哥伦比亚国家统计局 | 哥伦比亚移民局  
哥伦比亚国家网络警察局 | 哥伦比亚卫生部  
  
表3-1 来源信息

##### **3.2.2** **恶意附件文档**

该组织擅于使用携带恶意宏的MHTML格式的word文档作为攻击载荷。在此次攻击活动中，我们观察到攻击者更改了初期的攻击策略，其先将带有短链接内容的PDF或RTF格式的恶意附件作为第一阶段的诱饵文档，再通过诱导受害者点击链接后，跳转到指定的服务器上下载恶意文档，该恶意文档是包含宏代码的word文档。从这些PDF/RTF格式的恶意附件在VT上的扫描结果（如图3-6）可以看到，它们的查杀率普遍偏低甚至为0。攻击者将这类低查杀率的恶意文档作为邮件附件，能在一定程度上达到绕过邮件网关的目的。![img](https://images.seebug.org/content/images/2020/08/19/1597822069000-wpse3Pm7A.jpg-w331s)

图3-6 VT查杀结果

##### **3.2.3** **域名使用偏好**

我们将该组织在早期行动中使用的动态域名，与本次行动所使用的域名做对比分析，可以很清晰的看出，这些域名都是通过同一个动态域名商DNSEXIT注册的。此外，在本次事件中的域名“medicosta.linkpc.net”与2018年事件中的域名“medicosco.publicvm.com”相似度极高，由此猜测它们极有可能是由同一组织注册。

##### **3.2.4 IP地址关联**

根据我们在3.1小节中所分析的结果显示，攻击者所有关联域名的曾绑定和现绑定的IP地址，均由互联网运营商Unus.Ins公司提供，且大多数用作VPN服务。这与该组织在2018年的攻击事件中发送邮件时使用的VPN相关IP地址128.90.xxx.xxx网段完全相同，由此可以看出这极有可能是出自同一组织。

##### **3.2.5** **地理位置特性**

从攻击者所使用的C&C基础设施来看，其所使用的所有IP地址（包括128.90.xxx.xxx、191.95.xxx.xxx、190.253.xxx.xxx及179.33.xxx.xxx等网段）均归属于哥伦比亚的ISP（如图3-7）。而这些IP地理位置也与该组织早期活动涉及的地理位置相同。

![img](https://images.seebug.org/content/images/2020/08/19/1597822069000-wpswIH6ZP.jpg-w331s)

图3-7 IP地址的地理位置

基于该组织从伪装来源信息、诱饵文档、域名使用偏好、IP地址关联以及地理位置特性等方面的对比分析，我们初步推断本次的攻击行动来自“APT-C-36盲眼鹰”组织。

## **四、攻击载荷分析**

图4-1显示了黑客组织在此次攻击活动中的整个流程。

![img](https://images.seebug.org/content/images/2020/08/19/1597822070000-wpsnpcVPH.jpg-w331s)

图4-1 黑客攻击流程图

在初期阶段，该组织首先利用与其伪装来源有关的主题邮件，附加恶意文档一并发送给攻击目标。当受害者点击文档中的短链接时，其实际上是被重定向到下一阶段DOC文档的托管平台，从而执行下载流程。该DOC文档运行后会启动恶意宏代码，访问并解析执行指定的页面（html文件），随后从C&C服务器上下载payload文件，成功下载后立即执行。此payload会在内存中加载执行其解密后的DLL模块来实现第一阶段的功能，接着第二阶段的DLL模块再执行其解密后的EXE模块，为了隐藏恶意下发功能，第三阶段的EXE模块会将解密后的可执行PE文件（AsyncRAT远控木马）映射到傀儡进程中执行。最后，AsyncRAT木马程序与C&C服务器建立SSL通信，接收控制指令以实现其间谍活动。

攻击者为了隐藏其真实企图，采用多层模块嵌套和以不落地形式在内存中加载执行木马程序的手法，再结合该木马针对自身运行环境检测（如虚拟机、沙箱、反调试等）的功能，以避免其在自动化系统分析中暴露恶意行为。下文，我们从黑客组织近期攻击事件的案例中，选取一例进行详细的剖析。

### **4.1** **钓鱼邮件**

图4-2展示了攻击者仿冒来自哥伦比亚国家卫生部的钓鱼邮件，邮件标题为“Usted ha sido citado para una prueba
obligatoria de
(COVID-19)”（翻译后为：“您被要求参加强制性检测（COVID-19）”），正文内容是关于检测的相关问题（如图4-3），并声称邮件附件是检测时间和地点，以诱导受害者打开附件文档。

![img](https://images.seebug.org/content/images/2020/08/19/1597822070000-wpsj2zYdK.jpg-w331s)

图4-2 仿冒来自哥伦比亚国家卫生部的钓鱼邮件内容

![img](https://images.seebug.org/content/images/2020/08/19/1597822070000-wpsCZmMps.jpg-w331s)

图4-3 邮件翻译后的内容

### **4.2** **恶意文档**

黑客组织所使用的恶意文档包括PDF、RTF以及MHTML格式的DOC文档。其并未使用漏洞，而是通过嵌入的恶意宏代码来触发后续恶意行为。与该组织以往攻击手法不同的是，本次并未直接通过邮件传播MHTML格式的恶意文档，而是将包含一个跳转链接（该链接指向MHTML格式的恶意文档）的正常文档作为邮件附件来进行投递，以绕过邮箱网关的安全检测。

图4-4是4.1小节中的邮件附件，该pdf文件包含哥伦比亚国家卫生部的标志、一行文本信息（标注文档密码，实则无用）和一个名为“Ver
comunicado”的跳转链接（如图）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822070000-wpsCMCY4H.jpg-w331s)

图4-4 PDF文档跳转链接内容

当用户点击文档链接时，实际上攻击者是利用Acortarurl短链接服务平台将受害者重定向到其指定的服务器上，下载MHTML格式的word文档。下图为访问Acortarurl的流量内容。

![img](https://images.seebug.org/content/images/2020/08/19/1597822070000-wpsiUDIAD.jpg-w331s)

图4-5 Acortarurl的流量内容

虽然此案例中的恶意文档链接已失效，不过通过关联分析后，我们发现了其他相关的恶意文档。该文档同样是伪装成来自哥伦比亚国家卫生部，攻击者在文档正文利用西班牙语诱导用户点击“启用内容”按钮来查看检测时间和地点。具体内容如图4-6所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822071000-wpsTUgOex.jpg-w331s)

图4-6 内嵌VBA的DOC恶意文档内容

当我们查看该文档的VBA工程时，提示需要输入密码。解密后从宏代码的内容可以看到，当受害者启用宏功能后，恶意代码将自动执行Document_Open函数。具体内容如图4-7所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822071000-wpsANgqox.jpg-w331s)
图4-7 恶意宏代码内容

该函数会利用Microsoft工具mshta.exe来解析“http://pastebin.com/raw/Xrp7W0V3”（放置在pastebin网址上的html恶意脚本文件）。具体内容如图4-8所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822071000-wpsgM69xs.jpg-w331s)

图4-8 加密的HTML脚本文件内容

解密后的恶意脚本文件主要功能是利用Windows内置程序certutil.exe远程下载指定的EXE文件，然后将其保存至“%appdata%msts.exe”并执行该程序。

![img](https://images.seebug.org/content/images/2020/08/19/1597822071000-wpsOzZCSf.jpg-w331s)

图4-9 解密后的HTML脚本文件内容

### 4.3 Payload

如上文所示，通过html恶意脚本下载并执行的
“msts.exe”（C#编写并加入了大量的混淆）实际上是一个Dropper文件。“msts.exe”会从资源中解密出“DriverUpdate.dll”（C#编写）并在内存中反射加载该DLL模块来实现第一阶段的功能；接着第二阶段的“DriverUpdate.dll”再解密出其原始文件“msts.exe”中的另一个资源数据，然后执行解密后的“Cyrus.exe”模块；第三阶段的“Cyrus.exe”从自身资源中解密出Async
RAT远控木马，并将其整个文件覆盖映射到当前进程中执行。最后，Async
RAT木马程序与C&C服务器进行通信连接，连接成功则发送上线包请求上线，并等待接收控制指令。

#### 4.3.1 第一阶段模块

“msts.exe”主要用于解密并在内存中加载下一阶段的功能模块。其将自身伪装成Intel无线驱动应用程序，并附有详细的文件说明和版本号（如图4-10），以此迷惑攻击目标。

![img](https://images.seebug.org/content/images/2020/08/19/1597822071000-wpsrmXNEt.jpg-w331s)

图4-10 “msts.exe”文件属性详细信息

该Dropper模块的入口点在WindowsFormsApplication1处（如图4-11），其首先通过调用SelectedCard类中的D_D_D_D函数对名为“xor4”的资源数据进行解密。

![img](https://images.seebug.org/content/images/2020/08/19/1597822072000-wpsSnlt1d.jpg-w331s)

图4-11 Dropper模块的入口函数

解密算法是循环异或运算，其固定密钥为“RR5IRBNF5F4GN7997QFBYY”，解密代码如图4-12所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822072000-wpsfu7Zei.jpg-w331s)

图4-12 解密代码具体内容

在解密出PE文件后，Dropper模块则附加三个启动参数（“AcBRmi、S8epuew和IntelWireless”）来加载执行第二阶段的功能模块。

![img](https://images.seebug.org/content/images/2020/08/19/1597822072000-wpsAAMgVj.jpg-w331s)

图4-13 加载执行功能代码

#### 4.3.2 第二阶段模块

该阶段模块的文件名为“DriverUpdater.dll”，当此模块运行后，会提取和解密第一阶段Dropper模块中另一个资源文件“AcBRmi”，之后在内存中加载执行解密出的第三阶段的PE文件。

![img](https://images.seebug.org/content/images/2020/08/19/1597822072000-wpsepsCPq.jpg-w331s)

图4-14 解密和执行PE文件的功能代码

解密算法依然是循环异或运算，其密钥为“CZysHnTTIiop”，解密代码如图4-15所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822073000-wpsG3GVVR.jpg-w331s)

图4-15 异或解密算法代码

#### 4.3.3 第三阶段模块

此功能模块的文件名称是“Cyrus.exe”，其主要任务为解密和执行最终的远控木马。

**初始化阶段**

1）
在执行入口函数之前，该模块会在初始化Class3的私有成员变量byte_Data时，先调用Class1类的方法解密自身资源文件Kdgv。具体如图4-16所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822073000-wpsjTrR0F.jpg-w331s)

图4-16 解密资源文件

资源数据的首次解密采用简单的异或加密算法，固定密钥为"dXhhaxrqDcQ"，通过对资源数据的每个字节做简单的XOR运算完成第一次解密。解密函数的代码如图4-17所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822073000-wps5P1tDa.jpg-w331s)

图4-17 解密函数代码内容

第一次解密前和解密后的资源数据如图4-18所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822073000-wpsFa8K3l.jpg-w331s)

图4-18 首次解密前后的数据内容

之后再对第一次解密后的数据进行二次解密，前16位为解密密钥“0x19 0xEF 0xB6 0xB6 0xE7 0x7E 0x92 0x92 0x0D
0xA0 0xE0 0x95 0xAD 0x8F 0x6B 0x14”，后面紧跟着的是待解密密文。 解密前后的数据内容如图4-19所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822073000-wpszV5Rln.jpg-w331s)

图4-19 二次解密前后的数据内容

函数以16字节为循环，将密钥同密文依次进行按位异或，最终解密得到“Stub.exe”文件。解密函数代码如图4-20所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822073000-wpsgjfCOH.jpg-w331s)

图4-20 解密函数代码内容

除此之外，该模块还会将提取出的配置信息数据，分别赋值给它们所对应的私有成员变量，在我们分析的此案例中，其配置数据大部分的值都为0。具体内容如图4-21所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822074000-wps1Ouw8h.jpg-w331s)

图4-21 配置信息数据内容

**执行主功能代码**

该模块首先使用Assembly.GetEntryAssembly().Location获取当前进程的全路径。接着通过判断上文提到的部分私有成员变量值来决定要执行的流程分支，其中包括互斥体的创建、虚拟机和沙箱的检测、文件下载、拷贝自身等。在本案例样本中，根据其配置信息来看，此模块仅执行最后一项流程，调用smethod_11函数。代码如图4-22所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822074000-wpsX923zj.jpg-w331s)

图4-22 代码执行流程

进入到smethod_11函数后，该模块先调用Class3.
SelectPuppetProcess来选择后续执行的RAT载体。由于参数int_13的值为0，所以返回值为string_10（当前模块的全路径）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822074000-wpsiDL2Wj.jpg-w331s)

图4-23 代码内容

在选择完RAT的傀儡进程后，该模块再调用smethod_9函数，其中参数1为自身进程的全路径，参数2为之前解密出的PE文件数据。首先，该模块重新创建一个自身新进程，然后卸载此进程映像，并把之前解密出的新PE头部，以及节数据依次写入到新进程模块中，最后修改OEP并启动运行（“Stub.exe”）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822074000-wpsF7c7RV.jpg-w331s)

图4-24 写入和执行新PE文件

#### 4.3.4 RAT模块

如上文所述，被执行的名为“Stub.exe”的PE文件则是最终的RAT模块。通过分析和溯源后发现，该PE文件是用C#语言编写的AsyncRAT远控木马。除了远程桌面监控、键盘记录、进程管理、远程WebCam、远程Shell等功能以外，其还包括加密、反沙盒、反虚拟机、反分析和反调试等对抗模块。下面我们会对RAT中的核心部分做深入的分析。

![img](https://images.seebug.org/content/images/2020/08/19/1597822075000-wpsgqJq1a.jpg-w331s)

图4-25 远程程序AsyncRAT控制端

##### 1）初始化配置信息

木马程序通过调用Settings.InitializeSettings函数来初始化配置信息。从图4-26中的函数实现代码可以看到，其会提取出固定的密钥并使用AES256算法解密出所有的配置数据信息。包含端口号、Host信息、版本号、Pastebin信息、解密秘钥、SSL通信证书及证书签名等信息，之后调用Settings.VerifyHash函数对证书进行验证。

![img](https://images.seebug.org/content/images/2020/08/19/1597822075000-wpsbZT2sl.jpg-w331s)

图4-26 初始化配置信息

解密之后的配置信息如图4-27所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822075000-wps4VO7qv.jpg-w331s)

图4-27 配置信息详细内容

##### 2）检测运行环境

为了逃避沙箱/安全人员的检测，木马程序使用了各种识别沙箱/虚拟机的技术，用于判断自身程序所在的运行环境，如果发现是在虚拟环境，或是被调试状态，程序则直接退出。从而达到隐藏自身，规避检测的目的。下面是该木马使用到的技术。

① VMWARE和VirtualBox虚拟机的检测。

![img](https://images.seebug.org/content/images/2020/08/19/1597822075000-wpsODGexg.jpg-w331s)

图4-28 虚拟机的检测

② SandBox的检测。

![img](https://images.seebug.org/content/images/2020/08/19/1597822075000-wpsAgsIrS.jpg-w331s)

图4-29 沙盒的检测

③ 判断程序自身是否被调试。

![img](https://images.seebug.org/content/images/2020/08/19/1597822075000-wpscBFJ9M.jpg-w331s)

图4-30调试环境的检测

④ 通过判断获取的硬盘容量是否大于6100000000L（56.81G），来检测是否为真实机器或虚拟环境。

![img](https://images.seebug.org/content/images/2020/08/19/1597822076000-wpsVrV0wr.jpg-w331s)

图4-31 判断硬盘容量

##### 3）安装机制

木马程序的安装机制包括进程唯一性判断、在宿主机的持久化设置和守护进程设置。该木马以解密配置信息中的MTX字串"AsyncMutex_s8H9OlmYu”为名来创建互斥体，以保证运行进程的唯一性。

![img](https://images.seebug.org/content/images/2020/08/19/1597822076000-wpsQiK0Y6.jpg-w331s)

图4-32 创建互斥体

其还会判断当前执行文件路径与安装目录是否一致，如果相同，则代表该模块已安装过，安装功能便不再执行。如不相同，该木马则会通过对比系统中运行的进程名来确保运行进程的唯一性。具体代码如图4-33所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822076000-wpsgkdXoq.jpg-w331s)

图4-33 判断安装路径

之后，木马程序根据当前是否为管理员执行权限，来选择是通过安装计划任务还是写入开机自启动命令实现持久化。具体代码如图4-34所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822076000-wpssTeZJi.jpg-w331s)

图4-34 安装计划任务或添加自启动

在完成持久化操作后，木马程序将自身重新写入到安装目录下并命名为指定文件名（chromgoogle.exe）。然后再在临时目录下生成和执行.bat批处理脚本文件。该bat文件用于运行“chromgoogle.exe”可执行文件及自身删除。具体内容如图4-35所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822076000-wps9b9vVI.jpg-w331s)

图4-35 脚本文件内容

最后，木马程序通过提升当前进程权限及设置线程始终处于执行状态方式，来实现守护进程。

![img](https://images.seebug.org/content/images/2020/08/19/1597822076000-wpsduCpXr.jpg-w331s)

图4-36 进程守护实现代码

##### 4）上线机制

在安装机制设置完成后，木马程序则通过配置信息中的IP和端口与控制端服务器建立SSL协议连接。此时该木马会收集受感染主机的系统信息，并把这些信息压缩后作为上线包发送到C&C服务器。上线包的内容包含主机设备的用户名、系统版本号、管理员账号和木马程序当前执行路径、版本号、安装时间等相关信息。通过对木马程序的分析，我们发现上线包的长度是不固定的。启明星辰ADLab研究员在对上线包格式做解析、提取后，整理归纳出木马程序上线数据包格式和上线数据包内容格式。具体如图4-37和表4-1（其中“绿色横格”作为一组数据的分割线）所示。

**数据大小** | **数据说明** | **数据内容**  
---|---|---  
0x01 | 子包数量 （以组为单位） | 0x8D（HEX值固定）  
0x01 | 名称长度 | 0xA6（HEX值固定）  
0x06 | 名称 | “Packet”（字符串值固定）  
0x01 | 包名长度 | 0xAA（HEX值固定）  
0x0A | 上线包名 | “ClientInfo”（字符串值固定）  
|  |  
0x01 | 名称长度 | 0xA4（HEX值固定）  
0x04 | 名称 | “HWID”（字符串值固定）  
不固定 | 标识码长度 | 不固定（如0xB4）  
不固定 | 唯一机器标识码 | 不固定（如“F40DD340EC6FDDB01847140”）  
|  |  
0x01 | 名称长度 | 0xA4（HEX值固定）  
0x04 | 名称 | “User”（字符串值固定）  
不固定 | 用户名长度 | 不固定（如0xAA）  
不固定 | 用户名 | 不固定（如“xxx”）  
|  |  
0x01 | 名称长度 | 0xA4（HEX值固定）  
0x04 | 名称 | “Path”（字符串值固定）  
不固定 | 路径长度 | 不固定  
不固定 | 恶意代码当前执行路径 | 不固定  
|  |  
0x01 | 名称长度 | 0xA7（HEX值固定）  
0x07 | 名称 | “Version”（字符串值固定）  
不固定 | 版本号长度 | 不固定（如0xA7）  
不固定 | 恶意代码版本号 | 不固定  
|  |  
0x01 | 名称长度 | 0xA5（HEX值固定）  
0x05 | 名称 | “Admin”（字符串值固定）  
不固定 | 管理员账号名长度 | 不固定（如0xA5）  
不固定 | 管理员账号名 | 不固定（如“Admin”）  
|  |  
0x01 | 名称长度 | 0xAB（HEX值固定）  
0x0B | 名称 | “Performance”（字符串值固定）  
不固定 | 窗口信息长度 | 不固定  
不固定 | 用户前台窗口信息 | 不固定  
|  |  
0x01 | 名称长度 | 0xA8（HEX值固定）  
0x08 | 名称 | “Pastebin”（字符串值固定）  
不固定 | Pastebin值长度 | 不固定（0xA4）  
不固定 | 配置中Pastebin的值 | 不固定（如“null”）  
|  |  
0x01 | 名称长度 | 0xA9（HEX值固定）  
0x09 | 名称 | “Antivirus”（字符串值固定）  
不固定 | 信息长度 | 不固定  
不固定 | 杀毒软件信息 | 不固定（如“N/A”）  
|  |  
0x01 | 名称长度 | 0xA9（HEX值固定）  
0x09 | 名称 | “Install”（字符串值固定）  
不固定 | 信息长度 | 不固定（如0xB1）  
不固定 | 恶意代码安装时间信息 | 不固定  
|  |  
0x01 | 名称长度 | 0xA4（HEX值固定）  
0x04 | 名称 | “Pong”（字符串值固定）  
|  |  
0x01 | 名称长度 | 0xA5（HEX值固定）  
0x05 | 名称 | “Group”（字符串值固定）  
不固定 | Group值长度 | 不固定（如0xA7）  
不固定 | 配置中Group的值 | 不固定（如“Default”）  
  
表4-1 上线数据包格式

![img](https://images.seebug.org/content/images/2020/08/19/1597822076000-wpsQSKIU7.jpg-w331s)

图4-37 上线数据包内容格式

**下面是木马程序发送上线请求的具体操作步骤：**

**步骤1**

其首先会对配置信息中“Pastebin”的值做判断，如果不为NULL，则使用webClient.DownloadString方法获取服务端的上线域名/IP和端口号（从“Pastebin”上提取）。部分代码如图4-38所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822077000-wpsNpuKAx.jpg-w331s)

图4-38 从“Pastebin”上提取上线域名和端口号

如果为NULL，则直接从配置信息中提取出对应的上线域名/IP和端口号（以逗号作为分隔符），这表明该木马程序是具有配置多个C2的功能，攻击者能够灵活地添加多个备用C2，即使其中一部分被阻断，也能够重获控制权。具体代码如图4-39所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822077000-wpsPp80S3.jpg-w331s)

图4-39 从配置信息中提取上线域名和端口号

**步骤2：**

木马程序在与控制端连接成功后，便开始调用自定义类方法IdSender.SendInfo方法，收集受感染主机和木马自身版本等相关信息，这些信息会被逐个的储存在MsgPack类中。获取设备信息代码如图4-40所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822077000-wpslFmgA0.jpg-w331s)

图4-40 获取设备信息

**步骤3：**

在此之后，木马程序调用msgPack.Encode2Bytes函数对上线包数据进行封包。该函数首先会执行this.Encode2Stream方法，通过调试分析得知，由于该木马是使用map类型来存储上线数据，那么此处便会调用this.WriteMap方法来操作上线包。

![img](https://images.seebug.org/content/images/2020/08/19/1597822077000-wpsUpiqQe.jpg-w331s)

图4-41 调用this.WriteMap方法

木马程序封包功能主要是在Encode2Stream方法中实现，为了能更直观地将上线数据包处理流程展现给读者，我们以本案例作为参考，绘制出整个封包的流程图（如图4-42）。

![img](https://images.seebug.org/content/images/2020/08/19/1597822078000-wpsaa0MOp.jpg-w331s)

图4-42 数据包封包流程图

我们通过对封包函数的交叉引用进行详细分析后，得出该木马程序的上线包（以及后续的心跳包和控制指令包）均采用此方式进行处理。需要特别注意的是，代表其子包的数量值（value）、名称和数据的长度值（value），实际上都是先对这些数据的真实值（num和len）做判断，再将真实值与对应的固定值相加，最后得出value值。发送包格式如表4-2所示（可结合图4-37理解）。

**子包数量** **（/组）** | **长度** **（子包1name）** | **数据** **（子包1name）** | **长度**
**（子包1data）** | **数据** **（子包1data）** | **子包2** **…**  
---|---|---|---|---|---  
num | name_value | string_name | data_value | string_data | ……  
  
表4-2 数据包格式

**步骤4：**

在封包完毕后，木马程序使用GZipStream类的方法对上线包进行压缩处理。代码如图4-43所示。

![img](https://images.seebug.org/content/images/2020/08/19/1597822078000-wpsVja19K.jpg-w331s)

图4-43 数据包压缩处理

**步骤5：**

最后，该木马会将数据包包长和数据包（获取的信息）分两个包依次发送给控制端申请上线。

![img](https://images.seebug.org/content/images/2020/08/19/1597822078000-wpsq0WRoz.jpg-w331s)
图4-44 发送数据包

##### 5）心跳机制

木马程序通过使用Timer类实现了自身的心跳机制。其主要功能是每10到15秒向控制端发送心跳包，心跳包内容包含包名和被感染主机系统用户前台窗口信息。

![img](https://images.seebug.org/content/images/2020/08/19/1597822078000-wpslOWsXe.jpg-w331s)

图4-45 发送心跳包

由图4-45中的代码实现可见，该远程木马心跳包的数据是同样使用MsgPack.Encode2Byte方法进行封包处理的。

##### 6）远程控制

在针对木马程序处理控制命令部分进行详细分析时，我们发现在被控端木马的恶意代码中，并未包含任何远程指令的具体实现功能代码。于是我们针对控制端和被控端做进一步的调试和观察后，发现所有跟远程操作相关的功能代码，都是根据其功能进行归类且被封装在不同的DLL模块中。当控制端在执行远程操作时，则首先与被控端发送特定的数据包进行交互，接着再将压缩后的功能模块附加到数据包中发送给被控端，由被控端以不落地形式在内存中加载执行，来完成控制端指定的控制命令。通过采用“propelling
in use，destory after
use”的工作模式，攻击者既可以灵活地调整木马程序的配置信息，又能较有效地防止取证分析人员获取其核心攻击模块，且在一定程度上达到免杀和绕过安全机制的效果。图4-46是木马程序在执行控制命令时（以“远程控制桌面”指令为例），两端之间的具体操作流程图。

![img](https://images.seebug.org/content/images/2020/08/19/1597822078000-wpszvUy5Q.jpg-w331s)

图4-46 远程操作交互流程图

该远控木马程序总共有十几个可执行核心功能模块，其中包含远程桌面监控、Webcam监控、键盘记录、文件查找、远程shell、Bots
Killer以及DDos攻击等功能。表4-3列出了所有模块的名称以及其所对应的功能。

**模块名称** | **模块功能**  
---|---  
Chat.dll | Chat  
Extra.dll | Visit Website /Send MessageBox /Get Admin Privileges / Disable
Windows Defender /Set Wallpaper  
FileManager.dll | File Manager  
FileSearcher.dll | File Searcher  
LimeLogger.dll | Keylogger  
Miscellaneous.dll | BotsKill /USB Spread /Seed Torrent /Remote Shell /DOS
Attack /Execute.NET Code  
Options.dll | Report Window  
ProcessManager.dll | Process Manager  
Recovery.dll | Password Recovery  
RemoteCamera.dll | Webcam  
RemoteDesktop.dll | Remote Desktop  
SendFile.dll | Send File To Disk  
SendMemory.dll | Send File To Memory  
  
表4-3 核心模块功能解析

表4-4为部分攻击指令数据包的内容。其中黄色标注部分为：当控制端要执行远程控制操作时，其与被控端交互的通用数据包格式（除“string_SHA256”和“压缩后的二进制数据”以外，其他内容都相同），其余都是其他相关操作的信息指令。

**数据内容** | **数据说明**  
---|---  
“Packet”“plugin”“DLL”“string_SHR256”（由C&C服务器发起）
**\------------------------------------------------------**
“Packet”“SendPlugin”“DLL”“string_SHR256”（由RAT发起）
**\------------------------------------------------------**
“Packet”“plugin”“DLL”“压缩后的二进制数据”“Hash”“string_SHR256” （由C&C服务器发起） |
动态回传各类控制指令功能模块数据包。  
“Packet”“dos”“Option”“postStart”“Host”“string_host”“Port”“string_port”“Timeout”“string_timeout”
| DDos攻击相关配置信息  
“Packet”“fileManager”“Command”“getPath”“Path”“string_path”
**\------------------------------------------------------**
“Packet”“fileManager”“Command”“getDriver” | 远程文件管理相关操作信息  
“Packet”“keylogger”“isON”“false” | 键盘记录相关操作信息  
“Packet”“processManager”“Option”“Kill”“ID”“string_id”
**\------------------------------------------------------**
“Packet”“processManager”“Option”“List” | 进程管理相关操作信息  
“Packet”“ShellWriteInput”“WriteInput”“string_txt”
**\------------------------------------------------------**
“Packet”“ShellWriteInput”“WriteInput”“exit” | 远程Shell执行相关操作信息  
  
表4-4 攻击指令数据包解析

## **五、总结**

通过分析可以看出，“APT-C-36盲眼鹰”组织主要采用的手法是网络钓鱼攻击，即以使用带有社工伪装的邮件（仿冒国家政府部门）作为攻击入口，利用低查杀率的邮件附件（用于绕过邮箱网关）向目标主机投放后门程序。在侵入主机设备后，再通过多层嵌套加载、虚拟机沙箱检测及功能模块动态推送等技术手段，达到在目标主机上长期潜伏而不被发现的效果。同时，结合对该组织历史攻击武器的深入研究我们发现，为了应对不断进步的安全防御和检测，该黑客组织改进了其攻击策略，所使用的后门木马工具更复杂、对抗性更强，这表明该组织在持续地更新迭代恶意代码的功能和形态，并呈现出功能模块化的趋势。

鉴于该黑客组织长期通过钓鱼邮件以及Office
VBA宏进行攻击的惯用手段，我们建议相关用户不要随意打开和下载未知来源的邮件附件及链接，做好邮件系统的防护，如有需要可通过打开Office文档中的：文件-选项-信任中心-信任中心设置-宏设置，来禁用一切宏代码执行。一旦系统或服务器出现异常行为，及时报告并请专业人员进行排查，以消除安全隐患。

## **IOC**

**SHAR·1**  
612b7cd95eb317c2931d89acfb1c99506d799d26  
ee42b8a4b53c8363828b9bc732045aa248e1d64a  
e9e0871d37d1765756175e8931eedadb3f210b9b  
e9e0871d37d1765756175e8931eedadb3f210b9b  
c277bb8d01cb3e9d18d5378c6f518f4faca508fb  
b586969a25aca22612ff59978d3a6062663baa86  
79bf3730a7089b5c108bad883c1cc9a3779cb366

**IP**  
128.90.112.142  
128.90.112.231  
128.90.105.72

**URL**  
https://acortaurl.com/diangovocestadodecuentadeudaquotamp _ **P
https://acortaurl.com/activarcedulaonlineregistraduriagovcoquotamp**
https://yip.su/2oTZk  
https://acortaurl.com/pdfproceso00910020190976543  
https://acortaurl.com/diangovcodocumentos2019deudaalafecha0393948amp_

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1297/>

