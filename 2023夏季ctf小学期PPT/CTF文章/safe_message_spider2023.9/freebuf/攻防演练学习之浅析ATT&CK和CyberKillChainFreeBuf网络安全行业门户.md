# HVV-Learning-003-浅析ATT&CK和Cyber Kill Chain

  * [目录]()
  * [1、前言]()
  * [2、Cyber Kill Chain网络杀伤链]()
    * [2.1、Instrusion-Kill-Chain 入侵杀伤链]()
    * [2.2、Cyber-Kill-Chain的阶段定义]()
    * [2.3、Cyber-Kill-Chain模型的不足]()
  * [3、ATT&CK框架]()
    * [3.1、什么是ATT&CK]()
    * [3.2、ATT&CK的发展历史]()
    * [3.3、以开源的力量快速发展]()
    * [3.4、ATT&CK核心要素-战术、技术、流程(TTP)]()
    * [3.5、ATT&CK的其他概念-Software、Group]()
    * [3.6、Triton-一个工业恶意软件的TTP]()
    * [3.7、ATT&CK的战术阶段]()
    * [3.8、ATT&CK的v7/v8版本差异]()
    * [3.9、ATT&CK 三大矩阵]()
  * [4、ATT&CK And Cyber-Kill-Chain]()
    * [4.1、两者的战术对应关系]()
    * [4.2、ATT&CK给安全界带来的价值]()

## 0、前前言

以前也时不时会在freebuf上看文章，但是一直没发过。忽然发现freebuf可以自由投稿。先把以前在 **同名公众号（非典型产品经理笔记）**
上写的原创内容，挑一部分发一下。

后续新内容会考虑同步在freebuf上发送。

 **本系列当前共14篇** 。

## 1、前言

 **理解事物从描述开始** 。要理解一件事情，首先要能描述它，不可描述的事情，显然很难被解析、被应对，难以发展和演进。 网络攻防因其抽象性，更是如此。

## 2、Cyber Kill Chain网络杀伤链

### 2.1、Instrusion-Kill-Chain 入侵杀伤链

`Cyber-Kill-Chain`刚面世的时候，是被称为`入侵杀伤链`，后续才更名为`网络杀伤链`。

在2011年，为了描述网络攻防， **洛克希德·马丁公司** 的计算机科学家，提出一种"入侵杀伤链(Instrusion Kill
Chain)"用于保持计算机网络，入侵杀伤链中提出， **攻击可能会分阶段发生，并且可以通过在每个阶段建立的控制来破坏** 。

![](https://image.3001.net/images/20221223/1671805268_63a5b95470b5b7c7abf5b.png!small)

后续，各数据安全组织开始使用该杀伤链来定义网络攻击的各个阶段，也基于它定义如何进行防御。

### 2.2、Cyber-Kill-Chain的阶段定义

下图为 **洛克希德·马丁公司** 官网(<https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html>)对于Cyber-Kill-Chain的阶段定义:

![](https://image.3001.net/images/20221223/1671805270_63a5b9565d67250baac09.png!small))

CKC将攻击共划分为如下7个阶段：

1)、 **侦察 Reconnaissance** ：指通过各种信息来源（如github、空间扫描、社工等)方式，收集可访问的攻击入口。

2)、 **武器化 Weaponization**
：指攻击者利用漏洞信息，提前制作攻击武器，以便在攻击过程中能快速完成突破。所谓工欲善其事，必先利其器说的就是这个道理。

3)、 **投递 Delivery** ：指通过钓鱼邮件、web访问、USB外设等途径，向目标企业网络投递攻击武器。

4)、 **漏洞利用 Exploitation** ：当武器(恶意软件）触及到目标系统或终端时，会通过漏洞等方式，控制受害者的终端或业务系统服务器。

5)、 **安装 Installation** :恶意软件安装一个新的后门或新的木马程序，以提升入侵者的访问权限，能接触到更多系统。

6)、 **命令与控制 Command and Control** ：通过前述各类攻击武器，攻击者可以进行命令控制操作，比如说发起进一步的嗅探、攻击等。

7)、 **目标行动Actions on Objective** :
当攻击者接触到既定攻击目标时，可以对其进行各种既定行动（如盗窃机密数据、破坏/加密数据进行勒索等）

### 2.3、Cyber-Kill-Chain模型的不足

 **Cyber-Kill-Chain** 解决了如何描述攻击战术的各个阶段的问题，能让大家更好地理解攻击过程。

但是CKC存在如下关键问题：

1、抽象程度较高，不同的攻方、守方针对 **同一个攻击事件** ，也会给出不同的描述，缺乏统一的描述机制和原语支撑。

2、随着网络世界的复杂化，攻防不对称程度持续深化。针对同一个阶段，攻击方有无数种技术、方法可以使用，而防守方
**却无法清晰描述和知晓自身的安全防护能力的全景实况** ，难以持续提升攻防对抗能力。

注： **网络世界的复杂化**
是指，比如说操作系统种类越来越多（windows,mac,linux,android,ios等），开发语言越来越多(c/c++、python/ruby、golang等），中间件越来越多(IIS,apache,nginx等）、服务框架、业务系统数量都越来越多，这些复杂化，会增加大量的漏洞、攻击技术、攻击方法。

在《 **ATT＆CK框架实践指南** 》一书中，从防守方视角描述了基于Cyber-Kill-Chain模型不足下，面临的困局。该书是这么描述的，防守方始终会被以下问题（如下图 所示）所困扰：

![](https://image.3001.net/images/20221223/1671805272_63a5b958d7351cfce12c4.png!small)

  * 我们的防御方案有效吗？

  * 我们能检测到 APT 攻击吗？

  * 新产品能发挥作用吗？

  * 安全工具覆盖范围是否有重叠呢？

  * 如何确定安全防御优先级？

## 3、ATT&CK框架

### 3.1、什么是ATT&CK

 **ATT &CK的全称是Adversarial Tactics(对抗战术）, Techniques（技术）, and Common
Knowledge**（公共知识库）。

 **ATT &CK**提供了一个复杂框架，截止到2022年04月更新的ATT&CK
V11，介绍了攻击者在攻击过程中使用的14个战术，191个技术，386个子技术，134个APT组织和680个攻击软件，还包含了
**知名APT组织对这些技术、子技术的使用样例。**

 **ATT &CK**提供了一种许多组织机构迫切需要的关键功能——
**用一种标准化的方法来开发、组织和使用威胁情报防御策略，实现企业合作伙伴、行业人员、安全厂商以相同的语言进行沟通和交流** 。

因此， **ATT &CK**从2015年公开发布模型以后，就迅速被世界各地的许多安全厂商和信息安全团队所采用。当前， **ATT
&CK**在全球范围内用被广泛用于入侵检测，威胁狩猎，安全工程，威胁情报，红蓝建设和风险管理等领域。

### 3.2、ATT&CK的发展历史

1、根据 ATT&CK 官网FAQ，最早在2013年，MITRE开始制定ATT&CK框架，但此时还只是MITRE内部完善和使用。

![](https://image.3001.net/images/20221223/1671805274_63a5b95a87570223343cb.png!small)

2、2015年，ATT&CK模型首次对外公开分享，包含9种战术，96种攻击技术。

3、2018年全年发布了3个对外版本。1月，ATT&CK正式发布了v1版本; 同年4月份，又发布了v2版本； 同年10月份，又发布了v3版本。在该年度，
**ATT &CK在业界获得了爆发式关注，众多安全厂商基于ATT&CK正式版本，在产品中增加了对该模型的支持**。

4、2019年3月的RSA大会中，有超过10个议题讨论将ATT&CK用于攻击行为建模、改进网络防御、威胁狩猎、红蓝对抗复盘、攻击检测方面的研究和分析。

5、截止当前，最新发布的是2022年4月v11版本，共包含14个战术，191个技术，386个子技术，134个APT组织和680个攻击软件。

### 3.3、以开源的力量快速发展

不得不提一笔的是，ATT&CK属于开源框架，原则上任何人都可以进行贡献，所以其版本发展非常快。

借助开源后整个安全界的力量，从2018年开始， **基本上以每年3个版本的方式进行更新** ，如下：

<https://attack.mitre.org/resources/versions/>

![](https://image.3001.net/images/20221223/1671805275_63a5b95bc09d93d203309.png!small)

### 3.4、ATT&CK核心要素-战术、技术、流程(TTP)

ATT&CK框架的核心是战术(Tactics)、技术(Techniques)、流程(Procedures)，简称作" **TTP** "。

战术(Tactics)：是指攻击者某一个攻击流程在战术层面上的目的，一共14个战术，使用编号ID和名称标识。比如说`TA0001 Initial
Access（突破口/入口点)`是为了进入目标公司的企业内网，获取第一个立足点，便于进一步攻击； 再比如说`TA0004 Privilege
Escalation(权限提升)`的战术目的，是为了从普通用户权限提升为管理员、系统权限，以便控制整个业务系统或终端、主机系统。

 **技术(Techniques)：是指攻击者为了完成某个战术，使用了什么攻击技术。比如说为了完成`TA0004 Privilege
Escalation(权限提升)`, 攻击者可以使用`T1547 Boot or Logon Autostart
Execution(开机或登录自动启动执行)`的攻击技术，比如说增加一个开机自动启动的系统服务项**，从而使木马在开机时自动被运行，从而获取操作系统的最高权限。

 **流程(Procedures):** 这里的流程更多是 **指攻击技术的使用流程**
。从官网可以看出，技术流程的示例可以来自知名APT组织，也可以来自于某些木马病毒、恶意软件。可见 ， 如下图：

![](https://image.3001.net/images/20221223/1671805277_63a5b95d6772c1da41924.png!small)![](https://image.3001.net/images/20221223/1671805278_63a5b95eb56519c55d9f2.png!small)

在攻击过程中，攻击者通过将 **技术、子技术** 以 **流程** 组织起来，最终达成 **战术目标** 。如下图：

![](https://image.3001.net/images/20221223/1671805280_63a5b9608d2a9184fa318.png!small)

### 3.5、ATT&CK的其他概念-Software、Group

1)、 **Software软件**
：在攻击过程中，攻击者使用到的不同类型的软件。通常分为两类，**工具(Tool)、恶意软件(Malware)**。两者的区别为，工具(Tool)更有可能被攻击者、防守者使用，如PsExec、Metasploit、Mimikatz。而恶意软件(Malware)则是为了恶意的目的，通常是攻击者使用。

2)、 **Group 组织** ：在ATT&CK中，GROUP通常是知名的APT组织，这些组织大多都会有持续性、针对性的威胁事件。

3)、 **Mitigation 缓解措施** ：在ATT&CK中，是指用于阻止攻击技术/子技术成功攻击的措施，比如说数据备份可以对抗勒索软件的数据加密。

根据 《 **ATTACK_Design_and_Philosophy**
》一文，见https://attack.mitre.org/docs/ATTACK_Design_and_Philosophy_March_2020.pdf，可以看到多个要素之间的关系。

![](https://image.3001.net/images/20221223/1671805281_63a5b961d79cd8d52b74f.png!small)

如下为实际案例APT28组织，利用`mimikatz`工具实现`OS Credential Dumping:LSASS Memory`技术性攻击，最终达成了
**Credential Access 凭证获取** 的战术目标。

![](https://image.3001.net/images/20221223/1671805283_63a5b96351689e45ec258.png!small)

### 3.6、Triton-一个工业恶意软件的TTP

上图仅仅是 **一个战术阶段** 的简单示意图， **真实的攻击工具/事件的TTP远比上图复杂**
，准确描述TTP通常以json形式描述，并可以通过相关工具如(`https://mitre-attack.github.io/attack-navigator/`导航工具）进行加载展示、编辑导出等操作。

2019年4月，FireEye公司发公告称，工业恶意软件Triton卷土重来，并发布了该工具的TTP。篇幅所限，下为部分TTP json文件的内容。

    
    
    techniques": [{  
    "techniqueID": "T1043",  
    "tactic": "command-and-control",  
    "color": "#3182bd",  
    "comment": "Look for outbound connections with portprotocol mismatches on common and uncommon ports such as 443, 4444, 8531, and 50501.",  
    "enabled": true,  
    "metadata": []  
    },  
    {  
    "techniqueID": "T1183",  
    "tactic": "privilege-escalation",  
    "color": "#3182bd",  
    "comment": "Look for modifications and new entries referencing .exe files under registry key HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options ",  
    "enabled": true,  
    "metadata": []  
    },  
    {  
    "techniqueID": "T1183",  
    "tactic": "persistence",  
    "color": "#3182bd",  
    "comment": "Look for modifications and new entries referencing .exe files under registry key HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options ",  
    "enabled": true,  
    "metadata": []  
    },  
    {  
    "techniqueID": "T1183",  
    "tactic": "defense-evasion",  
    "color": "#3182bd",  
    "comment": "Look for modifications and new entries referencing .exe files under registry key HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options ",  
    "enabled": true,  
    "metadata": []  
    },  
    省略若干技术利用过程 

下为依据`https://mitre-attack.github.io/attack-navigator/`导航器生成的
**TRITON的TTP图形化TTP** 。

### 3.7、ATT&CK的战术阶段

到这里我们需要理解一下ATT&CK的战术阶段，有点类似于Cyber-Kill-Chain，但是相比Cyber-Kill-Chain只有7个阶段， **ATT
&CK共计14个战术阶段更为详细**。

攻击者通过战术组合，达成最终的攻击目标（如拿下标靶系统、盗窃所需数据等）。

![](https://image.3001.net/images/20221223/1671805285_63a5b9651fc62bf139bd6.png!small)

14个战术分别如下：

1)、 **TA0043 Reconnaissance 侦察** ： 收集信息以计划未来的对手行动，即有关目标组织的信息，进行攻击准备

2)、 **TA0042 Resource Development资源准备/武器开发** ：提前准备攻击资源，包括开发攻击武器，建立远控中心、指挥中心等。

3)、 **TA0001 Initial Access 入口点/突破口**
：利用鱼叉钓鱼、水坑攻击、公开漏洞/0day等各种方式，获取入口点/突破口，以便进一步攻击。

4)、 **TA0002 Execution 命令执行** :尝试运行恶意代码，执行命令。

5)、 **TA0003 Persistence 持久化**
：通过修改配置、增加启动脚本等方式，以便保持突破口和攻击通路，能够更快速、便捷地发起后续攻击。简单理解，可以认为至此则该终端/主机被控制成为了 **肉鸡**
。

6)、 **TA0004 Priiege Escalation 权限提升** ：通过漏洞等方式来提升访问权限，如从普通用户权限提升至系统权限、管理员权限等。

7)、 **TA0005 Defense Evasion 防御绕过** :
通过多种方式，如白进程注入等方式来隐藏自身，避免被杀毒软件等各类安全软件发现、拦截。

8)、 **TA0006 Credential Access 凭证获取** ：通过键盘监听等方式，窃取用户的账号密码。

9)、 **TA0007 Discovery 发现**
：通过工具/命令等方式，发现主机/终端内所有帐号列表，以便攻击者确认哪些账号可以后续辅助攻击，以及扫描网络架构相关基础环境信息。

10)、 **TA0008 Lateral Movement 横向移动** ：通过凭证、漏洞等方式，向其他主机/应用/终端渗透，从而获取下一步立足点。

11)、 **TA0009 Colection 收集** ：收集更多信息和数据，包括并不限于浏览器记录、文件、注册表等信息。

12)、 **TA0011 Command &Control 命令控制**：攻击者在各受控机器上部署木马程序，和C2
Server通信，以便接收后续攻击命令，包括渗透、窃取资料等。

13)、 **TA0010 Exfiltration 数据窃取** ：攻击者通过压缩、加密、伪装、分片等方式，窃取敏感数据和资料。

14)、 **TA0040 Impact 施加影响** ：攻击者可以会加密客户数据（如勒索软件）或中断服务等方式，破坏系统的可用性或完整性。

### 3.8、ATT&CK的v7/v8版本差异

ATT&CK在2020年发布的v8版本，将`Pre ATT&CK`阶段合入到了`ATT&CK for Enterprise`主阶段中。

![](https://image.3001.net/images/20221223/1671805286_63a5b9660813e57b983ff.png!small)

2020年10月27日，MITRE在官方blog (<https://medium.com/mitre-attack/the-retirement-of-pre-attack-4b73ffecd3d3>中宣布二者合并。

![](https://image.3001.net/images/20221223/1671805286_63a5b966ec242beacdd55.png!small)

### 3.9、ATT&CK 三大矩阵

ATT&CK一共有三大矩阵，前面讲述的是最典型、覆盖面最广的`ATT&CK for Enterprise
Matrix`(针对PC、云环境包括SAAS/IAAS/网络/容器等）。还有另外两个矩阵，是`ATT&CK for Mobile
Matrix`（针对移动设备）、`ATT&CK for ICS Matrix`(针对工业网络）。

![](https://image.3001.net/images/20221223/1671805287_63a5b967e03d2ce3e1b21.png!small)

## 4、ATT&CK And Cyber-Kill-Chain

### 4.1、两者的战术对应关系

下图为ATT&CK和Cyber-Kill-Chain网络杀伤链的战术阶段对应关系。但是注意一点的是，两者战术阶段并不能完全对应的。

相比之下，ATT&CK战术阶段的技术性、操作性更强( **ATT &CK的战术阶段是可以根据需要乱序执行、根据需要进行任意组合的**)，而Cyber-Kill-Chain顺序性更强（ **更强调攻击起始到最终拿下目标的宏观过程** ）。

![](https://image.3001.net/images/20221223/1671805288_63a5b968c8807e2bc18e2.png!small)

### 4.2、ATT&CK给安全界带来的价值

总结而言，在`Cyber-Kill-Chain`描述过程的基础上，ATT&CK框架通过TTP机制，提供了攻防一致性的沟通语言，解决了
**现状认知、效果衡量、能力提升** 几大问题。

 **现状认知** ( **可描述** ):
基于ATT&CK攻击技术知识库，可以让企业/机构的防守方知晓当前网络安全防护体系的实际防御能力，是否能防护已知漏洞的攻击，能否基于ATT&CK中的技术防御点，检测发现潜在、未知的攻击。

效果衡量(可衡量)：企业可以依据ATT&CK攻击技术知识库来评估所采购的产品/服务的安全效果、防护能力，从而确认是否物有所值；安全厂商也可以依此展示自身的安全效果、防护能力。双方具有一致语言描述安全效果。

能力提升(可提升)：依据ATT&CK矩阵的TTP机制，可以将攻防技术、攻防流程、攻防思路、攻防策略具象化描述，可以在攻防演练中检视实践，可以在攻防对抗中提升红蓝双方的能力。

参考：

<https://en.wikipedia.org/wiki/Kill_chain>

<https://attack.mitre.org/resources/versions/>

<https://attack.mitre.org/tactics/ics/>

<https://www.aqniu.com/learn/61125.html>

<https://medium.com/mitre-attack/the-retirement-of-pre-attack-4b73ffecd3d3>

<https://cloud.tencent.com/developer/article/1780517>

<https://blog.csdn.net/ducc20180301/article/details/121745575>

<https://attack.mitre.org/docs/ATTACK_Design_and_Philosophy_March_2020.pdf>

 **相关：**

[#7 HVV-Learning-002-攻防演练的典型网络以及攻防现状(2021)](http://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247483858&idx=1&sn=79b2fbdf7fa54ea723f3bc224c0858e5&chksm=cfdbff9ef8ac7688ca938ba324492204830a1abc57a208da0330f20d636cdcc5d4f14b26d1ab&scene=21#wechat_redirect)

[HVV-Learning-001-初步了解网络安全攻防演练](http://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247483850&idx=1&sn=83f9e282a657148565b1841656497ad4&chksm=cfdbff86f8ac769050a09c5cb98c7e80b269cdd2637777aa510e0c7e6a3a09afe30104d1aeb5&scene=21#wechat_redirect)

