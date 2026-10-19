# 实例再读 SITX（Structured Threat Information eXpression）

阅读量 **137805**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-08-11 11:17:40

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**一、背景**

针对众多复杂的高级可持续性威胁的新威胁场景（除国家安全层面，诸如网络犯罪、经济威胁、工业间谍、黑客行为和恐怖主义），我们可以从“杀伤链”中攻击生命周期中参考有效信息，促进形成防御策略。

面对
APT，依据传统思路在安全事件已经发生后进行应急响应的成本将是巨大的。而更好的解决思路则在于如何利用威胁情报驱动安全防御策略，最好是在攻击者开始进行漏洞利用之前就可以对其进行发现及遏制（即“Left
of Hack”阶段）来解决滞后性的威胁检测及威胁响应。

因此，一切有关”敌人能力“、”敌人行为“、”敌人目标“的传统情报在网络领域同等重要。

类似的特征包括：

l ”发生或可能发生什么样的攻击行为“

l ”如何检测并发现这样的行为“

l ”在现在及未来的一段时间内，敌人会利用什么策略、技术以及实施过程（TTP）“

l ”敌人的攻击目标可能存在的脆弱性、不规范配置及弱点“

l
”敌人曾经实施过哪些攻击行为“等等通过信息共享，每个参与伙伴都可以获得有关威胁环境的完整理解，这里不仅仅包括概要，还包含了细颗粒度的解决方案（例如我可以通过哪些特征找到攻击者）。例如，A
企业今天遭遇到的威胁很可能就是 B 企业明天可能会遭遇的，这样如果 A 企业分享了其自身总结的有关该种类型威胁的细节指示作为网络威胁指示，那么 B
企业就能够将其作为参考，从而在“Left of hack”阶段发现并定位威胁，来前置威胁响应，即在 Weaponization 之前的阶段进行威胁分析，在
Delivery 阶段进行威胁检测，在攻击者未完成 Exploitation 的阶段进行针对性响应。

与此同时，《 Intelligence-Driven Computer Network Defense Informed by Analysis of
Adversary Campaigns and Intrusion Kill Chains》一文结合攻击样本对杀伤链中的七个环节进行了实例分析，见下图。

并对 Kill Chain 各阶段做了详细解释：

∣Reconnaissance 侦查踩点：勘探、搜索并确认目标，诸如爬虫搜索收集的一些会议文章、邮件列表、社会交际关系等特殊情报信息。

∣Weaponization 制作攻击工具：将 backdoor、Trojan、payload 等不同形式的攻击载荷捆绑在诸如 PDF、Office
等客户端程序上。

∣Delivery 传输攻击工具：通过如今最流行的三种方式，如邮件附件、门户网站、USB 可移动设备，来传输攻击工具。

∣Exploitation 目标弱点利用：当工具被传送至受害者主机环境后，则利用目标应用或主机的脆弱性，完成弱点利用过程。

∣Installation 寄生宿主：无论木马或后门形式的远控程序被安装在宿主主机，攻击者就可以在目标的内网环境中进行漫游，从而进一步渗透。

∣Command and Control (C2) 完成控制：受害主机反弹外连攻击机，从而建立一个 C2 通道，使得攻击者自由进出目标内网网络环境。

∣Action of Objectives
远程操控：在完成上述六个阶段后，攻击者才会深入到内网环境开始进行深入渗透。包括信息收集、加密、提取从而获取数据；破坏数据的完整性、可用性。达到完全控制宿主网络环境，更甚通过该网络做跳板从而深入渗透其它环境。

情报的传播速度与广泛程度对于复杂性威胁环境来说至关重要，故而建立一个自动化、帮助人为分析或执行的快速防御机制就是首要步骤。同时，自动化机制则需要来自于各个不同体系的产品、系统、结构等优质信息以及大量防御特征辅助训练和建设。

**二、范例**

STIX 目标为提供一系列包含网络威胁管理的核心用例，如下图所示。

“中央研究院資訊服務處”上在《淺談以 STIX 實現網路威脅情報標準化框架》一文中对该用例的解释通俗易懂，如下。

而 STIX 标准中例举的以某次钓鱼事件结合起来更有助理解，原文所述大概如下。

用例 1：分析网络威胁

一个潜在的网络钓鱼事件，网络分析师可以分析可疑的钓鱼邮件、所有相关的附件以及是否存在恶意链接、邮件是否被截获转发，同时评估钓鱼攻击的主要受害群体并进行分析记录。

用例 2：网络威胁特征分类

在确定钓鱼攻击后，网络分析师将从钓鱼邮件中获取一系列可视化的相关特征（诸如伪造地址、真实地址、项目信息、钓鱼
URL、附件类型、特殊形式附件等等），识别此次钓鱼攻击中涉及到的相关
TTPs（Tactics、Techniques、Procedures，策略、技术、实施过程），演示杀伤链中的相关攻击过程，分配调节规则库的信任度阈值，确定并编制适宜的应对指南，为规则库中添加相对应的威胁特征，指导分配应对处理，同时记录过程以作日后参考。

用例 3：管理网络威胁应急响应工程

在通过定义好的规则指标发现并确认了钓鱼攻击后，网络决策人员和操作人员都会清晰的了解到钓鱼攻击在整个情景中是怎样发生的，包括恶意软件的安装过程和执行过程，并落实好相应的预警和检测策略，进而有助于评估或定位事件的影响和损失。

l （用例 3.1）网络威胁预警

在通过定义好的规则指标发现并确认了钓鱼攻击后，决策者会根据钓鱼攻击的规则或指标库的参考，综合评估提出的应对措施，相应的成本及风险，来辅助决策是否对此次提议进行采纳。如若采纳，操作人员再进行落实实施。

l （用例 3.2）网络威胁检测

在通过定义好的规则指标发现并确认了钓鱼攻击后，操作人员可能又从攻击实例中获取一些新型匹配模式，从而再次运用到实际操作环境中去检测新的钓鱼攻击。

l  
（用例 3.3）事件响应  

在确定钓鱼攻击事件后，操作人员会调查取证此次钓鱼攻击是否已成功进行并在目标环境中已造成什么样的损失（诸如恶意软件是刚刚安装还是已经跑起来一段时间了），以及损失的详细情况（哪些信息系统遭受感染，哪些数据遭受泄露）。一旦获悉事件现状，操作人员就可以实施适宜的缓解和补救措施（恢复系统还是进行隔离）。

用例 4：威胁情报共享

在通过定义好的规则指标发现并确认了钓鱼攻击后，可以根据决策者提前定义好的策略方针，手动或自动选择该项情报可以分享给哪些可信的伙伴或社区组织，使得他们能够很好的利用情报信息。

**三、结构**

STIX 架构图包含了诸多核心网络威胁概念，它们具有相互独立且可复用的结构体系及特征， 并相互作用。

STIX 架构

l Observables 状态表象

Observables 元素的作用：用来描述有哪些监测的目标与其所处的即时状态。

它是 STIX 中的基础元素，对信息系统或网络环境进行实时监控，用来描述目标所处状

态。它包含文件信息（文件名、Hash、文件大小等等）、注册表键值、正在运行的服务项、

HTTP 请求等等。STIX 用 CybOX 作代表语言。

如下图所示，在“fireeye-pivy-observables.XML”一例中。

fireeye-pivy-observables.XML

“Observables”对 pivy 样本中如下属性进行描述

① 主题 Title

样本：XXX

② 对象 Object

文件对象：哈希 Hash

哈希类型：MD5

哈希值：XXX

③ 关联对象 Related-Objects

关联关系：Connected_To | Created | Characterized by | etc.

关联事件：idref 指向

l

Indicator 情报指标  

Indicator 元素的作用：描述 Observable 状态表象下的关联威胁指标，形如一个情报索

引，映射并定位到多个关联的情报属性。

Indicator

它会结合实际情景或上下文关系，来传递一些的特殊 Observables 状态信息，用来表示

网络安全环境中的一些工具或敏感行为。内部包含的一个或多个 Observables 状态信息可能

都映射到相关的 TTP 及另外一些元数据中，比如操作的限制、Windows 的有效时间窗、可能

产生的影响、指标来源、指标内容、响应建议等等。STIX 用 IndEX 做代表语言。

如下图所示，在“fireeye-pivy-Indicator.XML”一例中。 “Indicator”对 pivy 样本中如下

属性进行描述

① 主题 Title

样本：XXX

② 类型 Type

Malware Artifacts | Domain Watchlist | IP Watchlist | etc.

③ Observable 指标 Indicator:Observable

Observable idref 指向

④ TTP 指标 Indicator:TTP

TTP idref 指向

⑤ COA 指标 Indicator:Suggested_COAs

Course Of Action idref 指向

fireeye-pivy-Indicator.XML

与此同时，Indicator 指标是情报模型中的最基本元素，《Intelligence-Driven Computer

Network Defense Informed by Analysis of Adversary Campaigns and Intrusion Kill
Chains》一文中

提到，Indicators 指标可以客观地描述出一次入侵过程，它被细分为三种类型：

原子级指标：入侵过程中颗粒度最细的指标，如 IP 地址、Email 地址、脆弱性识别等。

计算级指标：来源于某些数据和事件分析过程中的指标，如恶意 Hash 值、正则表达式

等。

行为级指标：来源于对原子级指标和计算级指标的整合，如“用[正则]匹配出入侵者在

[某些时段]针对[某些 IP]所使用的具体后门程序，然后哈希得出 MD5 值”作为行为级指标。

而上述三者在情报的完整生命周期的不同阶段中转变形态，如下图所示。

l Incident 事件描述

Incident 元素的作用：展示已发生过的该类威胁的事件全貌，以作参考。

Incident 是在事件应急响应的过程中，发现或确认的，对组织产生影响织的 Indicators(威胁指

标)离散型实例。Incident 由诸如事故发生时间、影响范围、关联指标、TTP 利用、意图、影

响评估、响应要求、响应措施、事故信息源、行动日志等等。如下图的 Data Model 所示，以

Poison lvy 的样本为例展示了 Incident 和 TTP 之间的关系。

Relationship between the Incident Component and TTP Component

鉴于当前标准的特殊局限性，STIX 利用社区情报或最佳实践定义或代表最新的 STIX-
Incident 事件结构。

l TTP ( Tactics、Techniques、Procedures ) 威胁情景再现（包括 策略、技术、过程）

TTPs 元素的作用：用来描述攻击者或敌人的威胁行为或威胁情景。

Tactics、Techniques、Procedures

TTPs 原本为军事范围用词，用来描述敌人以及敌人不同层面的细节信息。该元素在

网络威胁中扮演核心角色，并与 Indicators, Incidents, Campaigns, ThreatActors 密切关联，

同时描述如何利用 TTPs 元素来获取 ExploitTargets。

TTPs 将会对攻击者的细节行为进行描述，包括(攻击特征、恶意软件、漏洞等)的展

示、(工具、基础设施等)资源的利用、目标资产的信息、关联目标的信息、攻击目的及

意图、关联杀伤链、TTP 信息来源等。

鉴于当前标准的特殊局限性，STIX 利用社区情报或最佳实践定义或代表最新的 STIX-
TTPs 事件结构。如 CAPEC 可定义和描述 TTP 的攻击特征(attack pattern)、MAEC 可用来

定义 TTP 的恶意软件特征(Malware)、CybOX 可用来定义 TTP 的工具及基础设施特征。

如下图所示，在“Mandiant_APT1_Report.XML”一例中。Mandiant_APT1_Report 样本中

对 TTPs 如下属性进行描述

① 主题 ttp : Title

∣样本：XXX

② 行为描述 ttp : Behavior

恶意软件 ttp : Malware

∣类型 Type： Backdoor | Relay | etc.

∣名称 Name

∣描述 Description

攻击特征 ttp : Attack_Pattern

∣描述 Description

③ 资源描述 ttp : Resources

基础设施 ttp : Infrastructure

∣类型 Type：Hop Point Accessors | FQDNs | IP Blocks | etc.

∣特征描述 Observable_Characterization：Address_Object:Address_Value | etc.

④ 杀伤链 ttp : Kill_Chain_Phases

kill_chain_id 指向

Mandiant_APT1_Report.XML

同时，以 Malware C2 Channel 为例，数据模型如下图所示。

Data Model

l Campaign 攻击动机

Campaign 元素的作用：用来描述攻击者的犯案动机，即为什么进行攻击。

Campaign

Campaign 的结构中包含攻击者的动机、相关 TTP 的利用、相关事件描述、行为描述、

其它关联的 Campaign、与 Campaign 有关的所有动作描述、Campaign 信息来源等等。

l ThreatActor 威胁源

ThreatActor 元素的作用：用来描述攻击链中所攻击者或敌人。

ThreatActor

ThreatActor 的结构中包含了攻击发起者的身份、攻击意图、攻击历史、TTP 历史、其它

关联的 ThreatActors、操作限制、与 ThreatActor 有关的所有动作描述、ThreatActor 信息来源

等等。

如下图所示，在“Mandiant_APT1_Report.XML”一例中。Mandiant_APT1_Report 样本中

对 TTPs 如下属性进行描述

① 身份信息 ThreatActor : Identities

∣身份信息 Related_Identities：XXX

∣描述 Specification： OrganisationName; Address:Country; RelationShip; Lauguages;
etc.

∣角色 Role：Nation_State | Military | etc.

② TTP 映射 ThreatActor: Observed_TTPs

∣ TTP idref 指向

③ 关联威胁源 ThreatActor : Associated_Actors

关联威胁源 ThreatActor : Associated_Actors

∣确认情况 Confidence：Confirmed | Possible

∣关系描述 RelationShip：Asserted Alias | Member

∣威胁源 Threat_Actor：Threat_Actor idref 指向

Mandiant_APT1_Report.XML

l ExploitTarget 目标弱点利用

ExploitTarget 元素的作用：用来描述可以被 TTP 利用的目标软件、系统、配置等存在的脆弱性或漏洞。

ExploitTarget

ExploitTarget 的结构中包含脆弱性的特征描述、漏洞的特征描述、配置问题的特征描述、

潜在的、目标弱点的信息来源以及如何应对等等。

l Course of Action 应对措施

Course of Action 元素的作用：用来描述如何针对不同威胁所采取的详细响应措施及防范

办法。

Course of Action

Course of Action 的结构中包含威胁管理中的相关内容（如目标弱点的补救措施、事件的响应等）、COA 类型、COA 描述、COA 对象、COA
典型结构（IPS 规则、自动化匹配或推荐）、COA 影响范围、COA 预估效果等等。

《 Intelligence-Driven Computer Network Defense Informed by Analysis of
Adversary Campaigns and Intrusion Kill Chains》一文针对 Course of Action
矩阵分析，从检测、防范、终端、降低、欺骗、摧毁几个不同的反馈程度，对 Kill Chain 杀伤链生命周期各阶段的 Course of Action
做了实例解释，不同阶段投入产品不同，对 Kill Chain 产生的作用不同：

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **北京信息科技大学 祁鑫** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84376](/post/id/84376)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) 北京信息科技大学
祁鑫

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

