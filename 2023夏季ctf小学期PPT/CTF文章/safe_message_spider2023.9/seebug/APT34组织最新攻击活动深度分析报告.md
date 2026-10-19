**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/o_EVjBVN2sQ1q7cl4rUXoQ>**

# 一、概述

2021年以来，启明星辰`ADLab`追踪到多起以军队事务和移动运营商业务为话题的定向攻击活动。攻击者伪装成为军事部门以军队内部事务如海军战舰就绪清单、某军官解雇令为诱饵对目标发起定向攻击并植入木马，同时也常常伪装成为一些国家的重要企业以招聘人员为由攻击目标。我们通过对攻击目标、入侵技术特点、代码同源性等因素进行比对分析后，确认此批攻击来源于`APT34`组织。`APT34`组织`2019`年的武器库泄露事件中曾暴露出其控制的`Exchange`服务器的`webshell`列表，这些列表中包含了十多家被黑客成功渗透过的中国企业和机构。

APT34首次被披露于`2016`年，是一个来自于伊朗的`APT`组织，其最早活跃时间可追溯到`2014`年，攻击目标主要集中在中东及亚洲地区，涉及金融、政府、能源、化工、电信等行业。`APT34`善于采用通信隐匿技术来规避检测和追踪，比如：通过`Exchange`
`Web` `Services (EWS)` API实现高可信度、高隐匿性的“EWS隧道技术”。

APT34在此次活动中做了大量的技术改进和升级，其中大部分都是以提高攻击的匿名性、隐蔽性、可控性和安全性为目的，防止被检测和追踪。比如`APT34`在本次攻击中，首次利用预攻击诱饵文档关闭宏提示；首次使用“匿名DNS隧道技术”，借助公共服务商`RequestBin`提供的匿名`DNS`服务，隐匿的上报设备指纹信息和感染进度；升级`Karkoff`后门，优化了“EWS隧道技术”，提高了基于`EWS`通信的内容安全，如基于`EWS`隧道利用`RSA`和`AES`算法对控制指令进行加密、提高了邮件载体的迷惑性以及利用窃取的EWS账号作为控制命令服务器等等手段以掩人耳目；首次使用`JS`代码注释作为控制通道，将控制指令加密隐藏于`Javascript`的注释中，使得控制命令的下发难以检测等等。

此外，本次攻击活动中，黑客还将窃取的黎巴嫩军方和移动运营商账户作为本次攻击的控制命令服务器，而`APT34`为了进一步的隐蔽自身，长期对`Exchange`服务进行攻击扫描，控制大量国家重要机构和企业的`Exchange`服务器，同时从这些服务器上窃取了相关的登录凭证，进而利用`Exchange`服务作为控制端服务器从事间谍活动。

本文将对`APT34`的本次攻击活动进行深入的分析和探讨，首先简要介绍该组织的历史活动，然后对其攻击手法，所使用的新的基础设施，以及本次攻击所采用的新技术进行分析，最后对攻击过程中所使用的后门以及相关的技术细节进行深入分析。

# 二、组织分析

长期以来，`APT34`广泛地在全球进行网络攻击，收集重要的网络攻击资源，包括各种登录凭证，匿名资源，隐蔽通道，然后整合这些资源对某些特定的目标发起定向攻击，本节将重点分析该组织在本次攻击活动中所使用的技术和资源。

## 2.1 历史攻击活动

为了对APT34在此次攻击活动中使用的策略和技术进行全面了解，启明星辰`ADLab`结合该组织近期和历史主要活动进行梳理总结，绘制了`APT34`活动时间线（如图2-1）。从时间线可以看出，APT34的攻击目标主要集中在中东地区，其定制了大量的网络武器，且攻击武器持续升级，攻击手法也在不断推陈出新。从攻击入口来看，主要采用鱼叉式钓鱼邮件、社工钓鱼、NDAY漏洞等方式实施组合攻击。在隐匿通信技术使用上，APT34历次的攻击活动普遍具有一致性——通用手段是借助HTTP隧道和DNS隧道进行流量隐匿。近期则更多的采用了高可信度、高隐匿性的EWS隧道技术来绕过安全检测。

![](https://images.seebug.org/content/images/2021/06/081684f7-2935-471e-8948-7cfb22e62e8a.png-w331s)
图2-1 攻击活动时间线

APT34（OilRig）于`2016`年首次被`Palo Alto
Networks`发现，其最早的攻击活动可追溯到`2014`年。自该黑客组织活跃开始，其每年都会针对中东地区的金融、政府、能源、化工、电信等重要行业实施网络攻击。2016年5月，首次被发现通过鱼叉式钓鱼邮件针对沙特阿拉伯金融机构发动攻击,使用了基于`HTTP`和`DNS`通信的木马`Helminth`。2017年8月开始利用最新的`Office
Nday`漏洞`CVE-2017-0199`和`CVE-2017-11882`针对中东地区的政府机构实施钓鱼攻击，涉及木马`POWRUNER`
和`BONDUPDATE`。2018年则持续针对中东各国的政府机构进行攻击，后门为基于`Powershell`的变种木马`BONDUPDATE`。2019年6月开始，疑似由APT34与`Hive0081`组织协作开发的新型恶意数据擦除软件`ZeroCleare`被用于执行破坏性攻击，影响到中东地区多个能源和工业部门的组织，约1400台设备遭感染。2019年7月，伪装成剑桥大学“研究人员”，通过`LinkedIn`（领英）分发恶意文件并进行网络钓鱼，使用了三类新型恶意软件`TONEDEAF`、`VALUEVAULT`和`LONGWATCH`。2020年4月，在针对中东电信组织的攻击中新颖的使用了基于`EWS
API`的隧道通信技术（邮箱作为`C&C`），可将控制指令隐写在电子邮件的图像附件中传输，关联木马`RDAT、Karkoff`。2020年5月，在网络攻击中使用`DNS-over-HTTPS（DoH）`协议，也是首批部署`DoH`的`APT`组织之一。2021年1月至4月，继续针对中东地区实施攻击，通过公共服务商`RequestBin`提供的`DNS`隧道服务上传信息，同时采用`EWS
API`隧道和HTTP隧道的方式隐匿通信，本文也将重点分析最新攻击活动中涉及的木马变种`KarkoffDll`和`SideTwist`。

## 2.2 攻击手法

在此次攻击活动中，`APT34`主要采用`Word`诱饵文档作为攻击入口，结合窃取的`Exchange`账号完成组合入侵。基于文档内容、语言、`C&C`（黑客窃取的邮件账户）所属区域，可以判断是针对中东地区的定向攻击（主要目标为黎巴嫩，还可能包括沙特阿拉伯、科威特和阿联酋等）。攻击文档伪装成“黎巴嫩海军战舰就绪清单”、“`Ntiva`公司的招聘信息”（美国IT服务商）、“解雇令”等内容，并在文档正文中添加诱导性描述以诱使目标启用恶意宏代码，从而植入后门程序。值得注意的是，一些攻击样本内置了黎巴嫩政府、移动运营商的`Exchange`邮箱账户登陆凭证。相关账户在遭到攻击者的入侵后，被用于以`EWS
API`协议的方式传输恶意流量。可以推测攻击者在先期准备阶段已成功入侵了有关组织或与其具有信任关系的邮件账户，并借高可信`Exchange`服务器为信任节点中转通信，隐藏恶意行为。我们将此次攻击的手法总结如图2-2所示。

![](https://images.seebug.org/content/images/2021/06/be3df95e-7dae-4630-a6ea-eee277255921.png-w331s) 图2-2 攻击手法

攻击活动中使用的诱饵文档如下：

![](https://images.seebug.org/content/images/2021/06/232d5644-18cd-4e16-8ab9-258afd84bb58.png-w331s)
图2-3 伪装成黎巴嫩海军战舰就绪清单

![](https://images.seebug.org/content/images/2021/06/90e912e2-9581-43c0-9f26-6ef0e14713a9.png-w331s)

图2-4 伪装成Ntiva公司的招聘信息

![](https://images.seebug.org/content/images/2021/06/b25c66ad-a0de-4072-a424-961099279552.png-w331s)

图2-5 伪装成解雇令

![](https://images.seebug.org/content/images/2021/06/a243f095-ea2f-4467-bf85-b04d12dd84e7.png-w331s)

图2-6 无实际内容（诱导启用宏）

## 2.3 基础设施分析

在本攻击事件中，黑客使用了更多类型的基础设施。通过对该批攻击样本回连的数据进行收集和分析，我们将本次攻击的基础上设施分为三类，包含基于DNS协议的攻击活动上报设施、基于EWS的控制命令设施和基于HTTP/HTTPS协议的控制命令设施。

  * 1）DNS隐匿通信设施 

这一部分设施是基于公开的DNSBin服务部署的子域服务，主要用于通知黑客目标已经中招以便进行下一步的攻击。攻击者利用公共服务商Requsetbin提供的DNS隧道服务，接收从受害者设备上传的相关信息。表2-1为该组织在此次攻击活动中所使用的部分DNS信息。

表2-1 DNS上报域名

![](https://images.seebug.org/content/images/2021/06/5d1302b0-9f1d-4ccb-8ad8-19b6ee901b47.png-w331s)

上表中蓝色部分为黑客申请的DNSbin服务域名，攻击代码在目标设备上成功执行后会基于目标设备信息和简单随机化数据构造子域，最后将这两部分组合起来作为上线请求通知黑客。通过子域信息可以反推出受害设备的一些简单信息。相关受害者DNS请求数据如下表所示：

表2-2 受害者DNS请求数据

![](https://images.seebug.org/content/images/2021/06/69399992-cbf6-461f-84e1-f0bed49e1e35.png-w331s)

从上表可以看出，子域数据中包含了被截断的主机名、主机用户名、随机信息以及攻击阶段信息（技术细节请参见攻击案例分析部分）。

  * 2）EWS通信设施（KarkoffDll）

该设施主要用于控制命令服务器，当诱饵文档在受害者主机上成功地植入`KarkoffDll`后，将通过EWS与这部分设施通信。这期间交互数据主要以控制命令和任务执行反馈信息为主。`EWS
(Exchange Web Services)` 是微软实现的一种客户端和服务器之间的交换信息的协议，该协议是基于标准的`web
service`工作的，通过使用`HTTP`+`XML`+`SOAP`来传输消息。黑客基于该协议则可利用邮箱来对目标实施远程管理，依附于高信任度的合法邮件服务器作为跳板，既能有效的对抗监管审查和流量分析，又能有效的隐藏其真实地址。

因此这里我们将一个被黑客控制的邮箱账户直接称为控制命令服务器`C&C`。其中在攻击样本中内置了多个邮件账户信息`sig.dir.logistic`，`ahabib`和`masters.michelle`，其中前两个账户位于服务器`mail.army.gov.lb`和`mail.touch.com.lb`，分别属于黎巴嫩军方和黎巴嫩移动络运营商的邮件服务器，而后一个属于比较普通公共邮箱服务器`mail.protonmail.com`。默认情况下攻击样本回连到`sig.dir.logistic或ahabib`，当然黑客可以远程指定由`masters.michelle`邮箱账户接管控制。

表2-3 本次攻击涉及的Exchange邮箱账户
![](https://images.seebug.org/content/images/2021/06/ecb52734-7bbc-466d-8f00-1eb4422122f3.png-w331s)

通过相关情报分析，黎巴嫩军方和移动运营商的邮箱账户极有可能为该黑客组织前期通过钓鱼或`Exchange`爆破工具窃取。该组织在`2019`年曾发生过数据泄露事件，其通过漏洞、钓鱼攻击、`Exchange`爆破工具攻陷了大量`Exchange`账户。下表梳理了`APT34`使用的部分钓鱼链接：

表2-4 疑似AP34使用的钓鱼链接

![](https://images.seebug.org/content/images/2021/06/e2d0949f-1487-4620-899c-e25cecc627ab.png-w331s)

攻击者通过钓鱼页面可以直接窃取到目标的电子邮件信息并应用于下一阶段的攻击活动。

![](https://images.seebug.org/content/images/2021/06/e2691c86-0b10-4ffd-a2f9-41831d1b26f9.png-w331s)

图2-7 通过钓鱼页面盗取邮件账户

对于APT34爆破Exchange邮件账户的手段，我们复盘了该组织被曝光的各类攻击武器，其中Jason能够用于窃取邮件账户信息，并可以针对Exchange服务器（07到17版本）的邮件账户进行爆破。

![](https://images.seebug.org/content/images/2021/06/29a9d594-c9f1-4d7f-bec2-8074ef473b36.png-w331s)
图2-8 Jason工具（爆破邮件账户）

APT34在2019年曾泄露出大量已被攻陷的Exchange账户，其中涉及到不少黎巴嫩和中东的受害者，甚至还包括了我国的十多家企业和机构。而此次暴露的邮箱账户表明APT34仍然在持续开展针对Exchange服务器及邮件系统的攻击，其同样可能以类似的手段攻击我国的机构、企业并实现隐蔽驻留（EWS
API隐匿通信），需要引起足够的重视。

![](https://images.seebug.org/content/images/2021/06/a33d74b1-3fb1-4ca1-8a11-e7546c9474d6.png-w331s)
图2-9 已曝光的失陷Exchange示例

  * 3）HTTP/HTTPS通信设施（SideTwist） 除此之外，在对SideTwist进行逆向分析后，我们发现该后门将通信数据隐藏于html文本的javascript中，这些被隐藏的数据以注释的形式存在于javascript标签中。这是APT34采用的最新方法，这种方法非常隐蔽且极难被检测。我们基于分析得到信息指纹并结合一些情报数据，最终获得了一批与该组织有关的网络基础设施（表2-5）。

表2-5 C&C基础设施

域名| 创建时间| 注册邮箱| IP 地址| ISP  
---|---|---|---|---  
pluginmain.com| 2021/2/9| runminer@yandex.com| 96.9.255.246(N/A)| NEXEON  
severalfissures.com| 2020/12/22| vince.gould@yandex.com| 193.239.84.207| M247
Ltd  
endlesspromises.com| 2020/12/15| REDACTED FORPRIVACY | 23.19.58.17/18|
Leaseweb Uk Limited  
metroupload.com| 2020/12/15| karenangell@yandex.com| 23.19.58.17(N/A)|
Leaseweb Uk Limited  
forecasterman.com| 2020/12/15| cortholahan@yandex.com| 23.19.58.17/18|
Leaseweb Uk Limited  
crucialanswer.com| 2020/12/13| REDACTED FORPRIVACY| 23.19.58.17/18| Leaseweb
Uk Limited  
confusedtown.com| 2020/12/13| wendy.kely@yandex.com| 0.0.0.0| N/A  
donotfollowmeass.com| 2020/12/13| lukasvoll@yandex.com| 23.19.58.17| Leaseweb
Uk Limited  
cannibalwoman.com| 2020/12/12| REDACTED FORPRIVACY| 23.19.58.17| Leaseweb Uk
Limited  
unsecuredstorage.com| 2020/12/8| domenicrey@yandex.com| 23.19.58.17/18|
Leaseweb Uk Limited  
hopeisstamina.com| 2020/12/8| REDACTED FORPRIVACY| 23.19.58.17/18| Leaseweb Uk
Limited  
Importantgate.com | 2020/12/8| pinerfox@yandex.com| 0.0.0.0| N/A  
flexiblepaper.com | 2020/12/7| jon-reynol@yandex.com| 23.19.58.17| Leaseweb Uk
Limited  
acceptplan.com| 2020/12/6| yumiwellen@yandex.com| N/A| N/A  
klwebsrv.com| 2020/11/26| avupdater@yandex.com| 23.19.58.17| Leaseweb Uk
Limited  
  
## 2.4 技术演进

APT34的本次攻击活动与早期相比，有着一些改变，其中从诱饵文档到后门程序上都存在较多改进。比如增加了用于关闭宏提示的诱饵文档，基于DNS的感染上报，以及以`JavaScript`为载体的流量隐藏等等。

  * 1）关闭宏提示诱饵文档 本次攻击中，我们第一次发现`APT34`采用了一种预攻击诱饵的手法，黑客首先向目标发送一个没有任务恶意行为的诱饵文档，该诱饵文档会偷偷地在目标主机上关闭`excel`和`word`两种文件的宏提示功能。并在此后攻击中，黑客会再次利用其它诱饵文档来下发后门。

![](https://images.seebug.org/content/images/2021/06/0cae803f-1522-491b-befa-0bcd740e796c.png-w331s)
图2-10 关闭宏提示功能

  * 2）基于DNS隧道的感染上报 相比于APT34以往的攻击活动，本次添加一个利用DNS协议进行攻击活动的上报，上报的服务器是公共的网络设施。这种上报最主要的特点是阶段化以及匿名化，同时流量是难以发现和检测的。通过分析发现，上报信息中包括受害者的一些列的可识别信息（如感染时间、用户名、主机名，IP地址等）。攻击者采用这种新的技术手法，能够及时掌握入侵执行进度（侦察阶段），以便进一步调整技战术策略来提高攻击的成功率。

![](https://images.seebug.org/content/images/2021/06/d27c109b-d533-4c29-8525-c262b24261ac.png-w331s)
图2-11 DNS上报信息代码

  * 3）以JavaScript为载体的流量隐藏

根据目前掌握的信息可知，`SideTwist`是`APT34`在本次攻击活动使用的一款新后门。该后门在与C&C交互时，采用了较隐匿的通信机制。攻击者将加密后的控制指令数据隐藏在html页面的`<script>`标签中，并以注释的形式存储。当后门获取指令时，则使用HTTP请求从伪造的虚假页面中提取控制指令数据。这能非常有效地逃避流量监视和检测。

![](https://images.seebug.org/content/images/2021/06/40cd75fd-da7c-4c24-b89f-c5d1387ab2c1.png-w331s) 图2-12 伪造的虚假页面部分源代码

  * 4）KarkoffDll后门改进

在以往的攻击中，APT使用的Karkoff后门是以独立的EXE可执行文件存在，文件名类似out.exe之类的文件，通过计划任务启动执行；而本次攻击中黑客将该后门分离成两部分，分别为白文件Mircroft.Exchange.WebServices.dll和后门程序System
Exchange Service.dll（提高了免杀能力），我们将新变种命名为KarkoffDll。该变种通过VBS脚本启动，而VBS以计划任务启动。

![](https://images.seebug.org/content/images/2021/06/360c1914-e7b3-4cf9-8b89-a48b7edb54cf.png-w331s)
图2-13 模块分离

  * 5）EWS邮件模本改进

在本次攻击中，黑客着重针对EWS通信过程中的邮件模板进行了精心设计和伪装。从先前的攻击案例来看，用于传输数据的邮件任务模板设计简单，无论是邮件主题前缀（“Great!”），还是邮件内容（“This
is our
reusme”）都略显简易，容易引人生疑。而在此次行动中，攻击者通过精心仿造Dropbox平台（网络存储服务提供商）的服务更新邮件来混淆视听，邮箱用户即使关注到恶意邮件内容（存储于已删除邮件），也很可能会误认为是Dropbox平台正常的服务邮件而忽略。另外，在前期攻击活动中通信数据被加密隐写在图像附件（RDAT）或TXT文本附件（Karkoff）中，此次攻击则隐藏在邮件Emailbody正文尾部，一方面可以起到不错的视觉混淆效果，另一方面也能避开部分针对邮件附件的文件检测。

![](https://images.seebug.org/content/images/2021/06/a6d9dd60-1bff-4b0e-b9e5-c6b4adf3dd07.png-w331s)

图2-14 邮件任务对比

此外，在前期攻击活动中使用的EWS
API邮件通信只支持2种邮件任务：“CMD”邮件任务和“结果”邮件任务，分别用于接收和发送指令，但这两种任务无法及时提供受控机器的连接情况。APT34在此次攻击中进行了升级——新增了“心跳包”邮件任务，当“已删除邮件”中不存在“CMD”邮件时，则更新“心跳包”邮件，攻击者即可掌握受控机器的上线连接情况。

![](https://images.seebug.org/content/images/2021/06/daaa6955-52d5-47cd-91c1-fc2292d3a946.png-w331s)

图2-15 增加“心跳包”邮件

# 三、攻击案例剖析

APT34的这次攻击涉及到多种形式的诱饵文档和样本形态,在分析完这批攻击样本和攻击策略后，我们将此次攻击活动划分为三个阶段：`初期侦察`、`后门植入`和`隐匿驻留`。整套攻击流程经过了攻击者的精心策划和部署。

初期侦察阶段，`APT34`首先投递“`无害`”的恶意文档诱导受害者点击执行宏代码，并利用绕过技术“关闭”`Office`的宏安全警告。默认允许宏代码执行就如同打开了“潘多拉魔盒”，攻击者后续所有基于宏的恶意行为将会悄无声息的执行，这给攻击者后续的入侵活动提供了便利。同时，由于文档不存在明显的恶意行为，该阶段也很难被受害者察觉。在该诱饵文档的宏执行过程中，其借助了公共服务商`RequestBin`提供的`DNS`服务来传输受害设备的指纹信息和宏感染进度，由于`RequestBin`的`DNS`匿名使用特性，所以我们称这种技术为“`匿名DNS隧道技术`”，黑客巧妙地利用了这一点，并在此次攻击活动中广泛应用于诱饵文档中。

后门植入阶段，攻击者继续投递诱饵文档并通过宏代码植入后门`KarkoffDll`或`SideTwist`。植入过程包含解密释放后门和安装计划任务两部分工作，同时其也会借助公共服务商`RequestBin`提供的`DNS`服务来传输受害设备的指纹信息和宏感染进度。

隐匿驻留阶段，植入的两类后门通过不同的隧道通信技术实现敏感数据传输。后门`KarkoffDll`通过`EWS
API`与`Exchange`邮箱账户（可信服务器）通信，将数据加密隐匿在`EWS协议`中传输，我们称之为“`EWS隧道技术`”。后门`SideTwist`采用“`HTTP隧道`”来实现与控制命令服务器的通信，在通信过程中，该后门还采用了基于`HTTP协议`的“`JS控制通道`”来隐秘下发控制指令。我们将在3.3章节做相关的技术分析，攻击活动的整体流程参考图3-1。

![](https://images.seebug.org/content/images/2021/06/5ea18d70-3b55-4cda-9e11-eec63898b142.png-w331s)
图3-1 入侵流程

## 3.1 阶段一：初期侦察

在初期侦察阶段，攻击者通过投递“无害”的恶意文档诱导受害者点击执行宏代码。宏代码的主要功能是绕过Office宏安全警告，同时会将宏感染情况通过DNS上报给攻击者（DNS上报信息是此次攻击活动中诱饵文档的共性特点，将在阶段二中具体分析）。文档宏的核心代码如下：

![](https://images.seebug.org/content/images/2021/06/39b1b5db-1550-48e9-99a8-fbc8d262b81d.png-w331s)

图3-2 绕过Office默认宏安全警告

在检测Office版本时，首先查找注册表中excel.exe的程序路径，之后结合GetFileVersion函数获取Office的所属版本。

![](https://images.seebug.org/content/images/2021/06/6f73ec00-4be8-4386-8f09-1b2403d5a846.png-w331s)

图3-3检测Office版本

然后，分别针对Excel和Word程序添加Office安全可信路径的注册表项（可信路径为”C:\”），并设置为支持子目录可信。最终，攻击者通过增加Office可信目录可以达到自动执行C盘下Office恶意宏的目的，为后续的入侵活动提供支持。

![](https://images.seebug.org/content/images/2021/06/e53c2861-6e1b-45ff-a42d-1d7e18dcd296.png-w331s)

图3-4增加Office可信目录

## 3.2 阶段二：后门植入

在完成第一阶段的侦察并绕过宏安全警告后，攻击者继续投递恶意宏文档以植入后门。其中，攻击者巧妙的借助了公共服务商`RequestBin`提供的`DNS`隧道服务进行宏感染情况的上报。使用公共DNS隧道服务可以充分保证通信的隐匿性，攻击者根据上报的DNS信息能够及时掌握后门植入的进度，并及时调整技战术策略。
诱饵文档诱导受害者
“启用宏”来执行恶意VBA脚本（如受害者已执行阶段一的诱饵文档则会默认执行宏）。以释放后门`KarkoffDll`的恶意文档为例，VBA宏通过`Document_Open`和`Document_Close`两类事件来触发恶意行为。

![](https://images.seebug.org/content/images/2021/06/f2722909-1818-4a06-8012-1de939971165.png-w331s)

图3-5 VBA行为

Document_Open（文档打开时）： DNS上报感染进度（第一次）
Base64解码提取后续的恶意代码并释放至新创建的目录“\appdata\local\Google_Corporation\”
检查环境是否有鼠标可用（反沙箱） DNS上报感染进度（第二次）

Document_Close（文档关闭时）： 检查环境是否有鼠标可用（反沙箱） DNS上报感染进度（第三次）
注册windows任务计划（伪装名称：Google Update），每5分钟运行脚本(exchange.vbs执行后续恶意代码), 持续20天
DNS上报感染进度（第四次）

### 3.2.1 DNS上报信息

在DNS上报信息的过程中，需上报内容将以DNS子域的形式传递，包括受害者的可识别信息（用户名、主机名、宏代码执行阶段）。除此之外，黑客在RequestBin端还可以识别到受害者的IP地址及感染时间。

![](https://images.seebug.org/content/images/2021/06/1d5f9a9d-fe12-484c-b613-6f9dd80fc1b2.png-w331s)

图3-6 DNS隧道通信

当恶意文档在以下设备环境中执行时，DNS上报流量参考图3-7所示。 Hostname : WIN-36F2EAP UserName : jayer
DNS上报信息示例（子域“2eapjayv9u2”为传输信息）：
2eapjayv9u2.53a91f99cdc251934931.d.requestbin.net

![](https://images.seebug.org/content/images/2021/06/70474c63-877c-491c-aa8d-34264ec9d8cc.png-w331s)
图3-7 DNS上报流量

requestbin.net端接收到的完整感染上报情况参考图3-8所示。

![](https://images.seebug.org/content/images/2021/06/d8db2b63-222c-4d3c-a5a2-60da357e4a90.png-w331s)
图3-8 “requestbin.net”接收DNS上报信息

在此次攻击活动中，诱饵文档的共性技战术特点是均通过`RequestBin`提供的`DNS`隧道服务进行宏感染情况的上报。我们针对3种不同类型的诱饵文档进行了比对分析，发现文档基于功能的不同上报次数也有所差异。初期侦查阶段（绕过宏安全警告）的诱饵文档共2次上报感染阶段，而后门植入阶段涉及的两类诱饵文档分别进行了4次和6次上报，对比情况参考下图所示。

![](https://images.seebug.org/content/images/2021/06/4cc827d2-4da7-42d7-b97c-9c0145ecc093.png-w331s)
图3-9 感染阶段上报对比

### 3.2.2 注册任务计划

当受害者打开文档时（Document_Open），宏代码通过Base64解码并释放后续的恶意代码。此阶段包含两类不同的后门KarkoffDll和SideTwist，其释放路径和加载方式也有所不同，相关路径如下所示：
“……\ appdata\local\Google_Corporation\”（KarkoffDll）
"……\public\documents\SystemFailureReporter\"（SideTwist）

![](https://images.seebug.org/content/images/2021/06/ebafee81-c79f-40aa-ae30-11dde728658e.png-w331s) 图3-10 后门释放路径

当受害者关闭文档时（Document_Close），宏代码将注册Windows任务计划以循环加载执行后续的恶意代码。以释放后门KarkoffDll的文档为例，当文档关闭时，其会创建任务名为Google
Update的任务计划。

![](https://images.seebug.org/content/images/2021/06/75c44ec4-2708-466b-ac15-0f663349ffe9.png-w331s)
图3-11 注册任务计划

该任务计划每5分钟执行一次`exchange.vbs`脚本，从而加载后续恶意代码`MicrosoftExchangeModule.dll`和依赖库`Microsoft.Exchange.WebServices.dll`。后门的持久性高度依赖于此任务计划，其生命周期也与任务计划时间相同（任务计划持续20天）。

## 3.3 阶段三：隐匿驻留

攻击者最终可能植入两类后门木马，分别使用了不同的隐匿隧道通信技术来实现敏感信息的传输：EWS隧道技术（`KarkoffDll`）和HTTP隧道技术（`SideTwist`），下文分别对这两类样本及其使用的通信技术进行深入分析。

### 3.3.1 EWS隧道通信

后门KarkoffDll利用了EWS API协议实现受控机与C&C间的隐匿隧道通信。EWS（全称`Microsoft Exchange Web
service`）是`Exchange 2007`之后推出的基于SOAP (`Simple Object Access Protocol`) 协议的 web
service，提供了访问Exchange资源的接口。微软Exchange团队后续又推出了`Microsoft Exchange Web
Service(EWS) Managed API`，开发者可以根据此接口发送和接收信息，实现操作Exchange服务器邮箱的各类功能。
攻击者在成功窃取到受害目标或与目标具有信任关系的Exchange服务器邮箱账户后，将该账号作为`C&C`跳板，通过EWS API隐匿的传输数据。由于EWS
API本身基于SOAP协议和HTTPS加密，且恶意数据被组合加密(自定义`Base64+RSA+AES`)后隐藏嵌入在邮件内容中传输，在对抗流量检测方面可以起到很好的效果。我们搭建了`EWS`环境来模拟被入侵邮件账户的受控情况：

![](https://images.seebug.org/content/images/2021/06/adf1914f-da4a-41fc-bd33-9956107dd810.png-w331s) 图3-12 通过EWS API传输敏感数据

攻击者将恶意EWS模块封装在DLL(MicrosoftExchangeModule.dll)中，并结合Windows任务计划和exchange.vbs脚本定时加载。

![](https://images.seebug.org/content/images/2021/06/1e6c58ed-78ad-47e5-b374-d7465567f227.png-w331s)
图3-13 exchange.vbs加载DLL

MicrosoftExchangeModule.dll的执行流程如图3-14所示，我们将分别从初始化、EWS API通信、控制指令三个部分进行介绍。

![](https://images.seebug.org/content/images/2021/06/4fab5daa-bc05-461f-80eb-c3c488b09271.png-w331s) 图3-14 恶意DLL执行流程图

  * 1）初始化 首先，后门执行的初始阶段会随机休眠30秒至120秒以尝试绕过沙箱检测。

![](https://images.seebug.org/content/images/2021/06/a8f99050-6bbd-4418-b057-c951c664f8a9.png-w331s)
图3-15 初始休眠
之后，通过自定义码表的Base64算法对UserName进行编码从而生成程序ID标识(Program.id)，该标识将用于后续通信的识别。

![](https://images.seebug.org/content/images/2021/06/f905888f-ee25-4a85-b25e-9ae72acd1c74.png-w331s)
图3-16 生成程序ID
进一步后门会读取资源信息，包括登陆EWS服务器邮箱所需的Host域名、账号、密码、邮件地址，以及配置文件中的模式值（首次运行为null）。

![](https://images.seebug.org/content/images/2021/06/575a5527-53b8-44e0-8e72-557af00d77fa.png-w331s)
图3-17 登陆邮箱所需的连接信息

由于后门循环启动，黑客可以通过更改配置文件中”KMAV”对应的模式值来实现不同的功能分支。配置文件字段及相关信息如下：
![](https://images.seebug.org/content/images/2021/06/7be3974c-e501-4e49-b04c-40c5ea99155e.png-w331s)
图3-18 配置文件相关信息

  * 2）EWS API通信 初始化后，后门在CheckEWSConnection()函数内根据从配置文件中读取到的模式值(credential.mode)选择执行分支。当模式值为0-2时程序会在当前登陆连接的Exchange邮件账户中创建邮件任务；当值为3-7时则会将邮件任务发送至黑客指定的邮箱（如：masters.michelle@protonmail.com）。

![](https://images.seebug.org/content/images/2021/06/8f2db839-38cb-4ac5-8d33-ba49422eaf49.png-w331s)
图3-19 执行分支

各分支根据传入参数创建EWSCommunication对象、EWSManager对象以及进行EWS服务器连接建立的初始化工作。

![](https://images.seebug.org/content/images/2021/06/a0bccab7-cddd-4a04-9dfb-bc2d02551422.png-w331s) 图3-20 创建连接对象

进一步在Initialize()函数中将设置EWS请求的UserAgent、操作文件夹位置（默认为已删除邮件）。
![](https://images.seebug.org/content/images/2021/06/19941ca8-c939-4cec-b0c9-810c8616f7d7.png-w331s)
图3-21 初始化配置

如果是首次执行后门（模式值为0），还将添加以下邮件收件箱规则： （1）DefaultExchangeRule1：若邮件主题中包含“Important
Dropbox Updates”字符串，删除邮件并且将邮件标记为“已读” （2）DefaultExchangeRule：若邮件主题中包含“Important
Dropbox API Updates”字符串，删除邮件并且将邮件标记为“已读”

![](https://images.seebug.org/content/images/2021/06/a1eedd7c-d09a-4b0a-b196-209751d2e92c.png-w331s)
图3-22 收件箱规则

创建收件箱规则的目的是将包含指定字符串的邮件移至“已删除邮件”，降低被邮箱用户发现的机率。攻击者采用了3种邮件任务实现数据传输，分别为“心跳包”邮件（aliveSubject）、“CMD”邮件（cmdSubject）、“结果”邮件（resultSubject）：

表3-1 邮件任务信息

资源名称| 值(邮件主题名前缀)| 功能解释  
---|---|---  
aliveSubject| Dropbox and Paper, together| “心跳包”邮件任务（更新执行时间）  
cmdSubject| Important Dropbox API Updates| “CMD”邮件任务（接收C&C指令信息）  
resultSubject| Important Dropbox Updates| “结果”邮件任务（上报指令执行结果）  
  
首次执行后门时受控机器会创建默认的“心跳包”邮件和“结果”邮件，“CMD”邮件则会由攻击者在下发控制指令时创建。
“心跳包”邮件主题名结构：aliveSubject + Program.id（自定义Base64) 示例：" Dropbox and Paper,
together CoFD!o4^}-F?CuF0}dNN"

![](https://images.seebug.org/content/images/2021/06/cccd360a-ab07-4e3d-be7a-3d393d418b5a.png-w331s)
图3-23 邮件任务主题

加解密算法： EWS
API基于`SOAP`协议和`HTTPS`加密通信，其本身已具有较强的安全性。攻击者进一步还将传输数据组合加密后嵌入在`Emailbody`中对抗流量检测，并通过前后字符串定位加密数据内容：
startString: “These don’t require action, but they may” endString: “enrich
your application and increase the value” 默认“结果”邮件的数据结构如下（初次创建）： mid | cid |
data | UserDomainName | MachineName | UserName

![](https://images.seebug.org/content/images/2021/06/d65ddb48-51c9-479b-b29d-cd8c932c2c2a.png-w331s)
图3-24 邮件Emailbody

邮件标题和内容均通过伪造Dropbox平台（网络存储服务提供商）的服务更新内容来混淆视听。在通信安全方面，黑客采用了RSA（非对称加密算法）、AES（对称加密算法）、自定义码表Base64的组合加密策略。通信共使用了两对RSA密钥对A和B，其中受控端内置了A密钥对的公钥和B密钥对的公钥、私钥。受控端上传信息时先由AES加密内容，再通过RSA_PublicKey_A加密AES
密钥，由于本地不存在A的私钥，那么即使捕获到加密流量也不具备解密条件。而接收黑客指令时由于本地有密钥对B的私钥，则可以解密识别控制指令。两类加密的指令数据格式如图3-25所示：

![](https://images.seebug.org/content/images/2021/06/1884067f-6e4f-4510-b7e2-ff0dbbbb846a.png-w331s)
图3-25 加密指令数据格式

GetCommands()函数负责指令的获取和初次解码，后门通过GetList() API查找已删除邮件列表并过滤
“CMD”邮件，通过HTTPS解密捕获到的流量如下：
![](https://images.seebug.org/content/images/2021/06/cb2984f2-4062-4ec3-9882-2a74ce84e80d.png-w331s)
图3-26 GetList API流量（HTTPS中间人捕获）

如果从邮件列表中过滤到cmdSubject任务（`Important Dropbox API Updates +
Program.id`），则进一步读取邮件内容并通过自定义Base64算法解码提取加密指令。此外，黑客在痕迹清理方面也表现出较强的专业性，在提取指令后会立即清除该CMD邮件以隐藏痕迹。

![](https://images.seebug.org/content/images/2021/06/19372944-659c-49e5-8e05-1f0156025a99.png-w331s)
图3-27 寻找及清理CMD邮件

如果未能从“已删除邮件”中获取到指令，则记录当前时间并更新至心跳包邮件(aliveSubject任务)，之后关闭程序。
![](https://images.seebug.org/content/images/2021/06/a6ab9952-2a19-4510-b83f-b4af1b746d36.png-w331s)
图3-28 更新心跳包邮件

  * 3） 控制指令 加密指令经过GetCommands()函数解码后，进入ParseCommand()函数进一步解析密文，依照RSA私钥解密(得到AES密钥)、AES密钥+IV解密（得到明文）的顺序提取出指令内容。 ![](https://images.seebug.org/content/images/2021/06/dcc76d90-c565-4978-9f03-51b9b0ea80b6.png-w331s) 图3-29 解析密文

![](https://images.seebug.org/content/images/2021/06/ee4c32f9-4ac7-4609-82c3-3284f98995fb.png-w331s)
图3-30 控制指令执行分支

指令解析后对应5种类型，以指令值101（功能：执行CMD命令）为例: “101|1|3|13|mkdir malware”，其控制指令结构示意如下：

![](https://images.seebug.org/content/images/2021/06/e5c4cfd5-a82a-4a07-b1c9-c134fe79c05a.png-w331s)
图3-31 控制指令结构示例

当受控机器接收到“CMD”邮件任务（cmdSubject）时，程序解密并执行指令，然后创建”结果“邮件（resultSubject）上报指令执行结果。如果指令未匹配，则返回”Done:D”。执行CMD命令“mkdir
malware”后的返回数据如下：

![](https://images.seebug.org/content/images/2021/06/479cf3b9-fa43-4edf-b340-e9832eff11b9.png-w331s)
图3-32 resultSubject数据（未加密）

控制指令功能参考下表所示： 表3-2 控制指令功能

指令值(mid)| 指令名称| 指令功能  
---|---|---  
101| Execute| Cmd执行命令  
102| Download| 将控制端的传递数据保存至指令目录  
103| Upload| 将需上传文件路径保存至cmd.result并准备上传  
104| Shred| 清除指定文件(移动该文件至随机位置后再进行删除操作)  
105| Send_Log| 读取ExceptionHandling运动cmd.result并准备上传  
  
### 3.3.2 HTTP隧道通信

SideTwist后门是由第一阶段宏代码添加的计划任务启动执行。其首先通过sleep延迟执行恶意行为以尝试绕过沙箱检测，休眠时间为计算出的随机数的10倍。

![](https://images.seebug.org/content/images/2021/06/b6d84666-e8af-4b3c-a702-4c6baf3ba7e8.png-w331s)
图3-33 Sleep延迟执行恶意行为

接着获取主机用户名、计算机名以及域名等信息，并通过简单的异或计算出用以标识的唯一值。此外，后门还会检查“update.xml”文件是否存在于上级目录中，不存在则输出调试信息并结束进程。

![](https://images.seebug.org/content/images/2021/06/7d1424fc-9684-4d1b-b646-2e4dbfc839ec.png-w331s)
图3-34 计算唯一标识符和检查XML文件

如该文件存在，后门则发送HTTP GET请求到C&C服务器
（sarmsoftware.com/search/[identifier]），使用的端口号为443，并将80作为备用的端口号。

![](https://images.seebug.org/content/images/2021/06/a85da638-85f9-42c9-a03f-cbf371c82f12.png-w331s)
图3-35 使用HTTP协议与服务器通信

发送给服务器的GET请求流量内容如下图所示：
![](https://images.seebug.org/content/images/2021/06/474329ac-2d36-4aac-a784-2cb9cdb66d9c.png-w331s)
图3-36 GET请求流量数据包内容

在分析此样本时，该域名已无法访问，我们通过其它途径找到了与其关联的页面源代码。后门将加密后的控制指令字符串以特定格式隐藏在HTML特定javascript标记内，并在字串首尾以“/
_“”_
/”作为提取指令时的分隔符，我们称这种利用`javascript`作为控制命令下发的通道为为“JS控制通道”。具体如图3-37所示（该例的控制指令编号为-1）。

![](https://images.seebug.org/content/images/2021/06/cdc3d8d4-dd42-4db8-b90a-07a782081b0c.png-w331s)
图图3-37 提取控制指令数据

后门所有通信流量的加解密均采用Base64和梅森旋转算法（`Mersenne
twister`）。解密控制指令数据时，其先使用Base64对字串进行解码，之后再将加密数据的前4个字节作为种子，通过`Mersenne
twister`进行解密，解密后的数据使用‘|’作为分隔符。如果数据中包含参数，则参数部分还需再进行一次`Base64`解码。解密后的数据格式如图3-38所示。

![](https://images.seebug.org/content/images/2021/06/5a57384a-7b01-4b1f-a9e9-5cb6d362139e.png-w331s)
图3-38 解密流程和解密后的数据格式

解密流程部分代码如下图所示：
![](https://images.seebug.org/content/images/2021/06/01f83441-327b-49ff-9f17-a55efd30ce89.png-w331s)
图3-39 解密流程部分代码内容

成功解密后，后门首先会提取出控制指令编号，判断该值是否为-1。如果是，则获取受感染主机的用户名以及主机名等信息，并将信息拼接成
“用户名|主机名|WORKGROUP”（‘|’作为分隔符）格式。之后再使用Mersenne twister和Base64对数据进行加密。

![](https://images.seebug.org/content/images/2021/06/48350ca2-5f95-4d14-8b73-c1c9fa4adb5d.png-w331s)
图3-40 加密获取到的用户主机信息

最后，后门使用HTTP POST方法，将加密后的数据发送给C&C服务器。数据采用简单的JSON格式，具体如图3-41所示。

![](https://images.seebug.org/content/images/2021/06/bd06981a-5c1c-4b68-b4e1-e7df2d1b9715.png-w331s)
图3-41 向C&C服务器发送加密后的数据

最终发送给服务器的返回数据格式如下图所示：
![](https://images.seebug.org/content/images/2021/06/f5b779f6-f741-43e6-b4cb-58136a518dc2.png-w331s)
图3-42 发送到服务器的加密后数据格式

SideTwist后门的功能比较简单，在分析中并没有发现如屏幕监控或键盘记录之类的监视功能，猜测其主要用于前期的侦查阶段。具体的控制指令功能如下表所示。

表3-3 控制指令功能

控制指令标识符| 控制指令| 参数| 功能  
---|---|---|---  
-1| 101（未使用）| 无参数（参数1）| 上传主机相关信息  
非-1值| 101| shell 命令（参数1）| 运行shell命令  
非-1值| 102| 文件名（参数1）/ 下载路径（参数2）| 下载指定文件  
非-1值| 103| 文件（参数1）| 上传指定文件  
非-1值| 104| shell 命令（参数1）| 运行shell命令  
  
# 四、总结

通过以上的分析可以看出，`APT34`组织的攻击手法隐秘高明，且在不断地改进升级其攻击技术，扩充其匿名性的基础设施和增加其独具一格的`TTP`。同时其还擅长于巧妙地利用低成本公共服务来隐藏其攻击痕迹，提高其攻击的成功率。此外，该组织为了逃避检测机制，常常会更换攻击策略和战术。

APT34偏向于使用更容易做免杀的脚本或更具欺骗性的`word`文档作为初期阶段的载荷投递，接着通过定制加强的后门来执行攻击任务，同时利用各种隐匿通信隧道与黑客方交换数据，例如其长期使用的“EWS隧道技术”作为控制通道以及本次攻击中新使用的“匿名DNS隧道技术”作为预攻击活动上报，使用“JS控制通道”作为控制命令下发的管道。“EWS隧道技术”通过依附高可信组织的`Exchange`邮件账户作为`C&C`（失陷邮件账户）,极大的提高了安全检测的难度，可以说是一种较为高明且保险的攻击策略。而“匿名`DNS`隧道技术”不同于一般的`DNS`隧道技术，其采用了成本低且完全匿名的形式，极难检测和追踪。“JS控制通道”的使用也是该组织在HTTP通信过程中首次使用的，难以检测和发现。

当我们面临这种攻击时，常常很难在攻击未发现的情况下检测出此类攻击，无论是基于规则、算法，还是基于机器学习算法的检测，其在流量规避上一直在寻求新的手段和方法，不断地利用公共设施和窃取的账户做为控制命令服务器。攻击隐藏和攻击发现这是一个长期的对抗过程，只有提高我们的发现能力和威胁情报反应能力才能够将这种攻击的威胁降低到最小，这其中需要我们具备较强的分析能力，较快的反应能力外，还需要结合新的防御思路和先进的检测技术来平衡攻防不对等的状态。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1614/>

