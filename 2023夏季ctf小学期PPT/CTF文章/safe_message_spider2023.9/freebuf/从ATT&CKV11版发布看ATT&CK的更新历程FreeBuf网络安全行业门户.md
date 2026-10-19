## **背景**  

2022年4月26日ATT&CK V11如约而至，这次的版本的更新主要集中在三个方面。通过分析ATT&CK 版本的更新历程，我们可以梳理出ATT&
CK的三条发展路线。

  

##  **01** ATT&CK V 11版更新内容

2022 年 4 月26日，ATT&CK (v11)版本正式更新。现在访问 https://attack.mitre.org/
主页，看到的将是最新的V11版本。ATT&CK 版本（V11）这次一如既往的更新了企业、移动和 ICS 的技术、组和软件。此版本的 ATT&CK for
Enterprise 包含 14 种战术、191 种技术、386 种子技术、134 个组织和 680 种软件。ATT&CK for
Mobile测试版，包括12战术，78技术，41子技术。

除此之外，还有三个方面的更新亮点。

 **更新亮点1：检测的重组，有助于企业进行结构化检测攻击技术**

本次更新，在Enterprise ATT&CK
中采用了并行检测方法，采用了以前（V9版前）在技术中提供的文字描述的检测方法，并将它们提炼合并到连接到数据源的描述中。MITRE通过将技术上的检测文本描述与其数据源匹配，使得对应变得更加明确。这样也更有助于企业方便查看每次检测所需要收集的数据源，以及如何分析该数据进而进行检测定位攻击。

通过查看窃取或伪造Kerberos票据（T1558）技术的数据源和检测的变迁，我们可以更好地理解数据源和检测的变化。

例子：

![1653384219_628ca41be49faf8176e2f.png!small?1653384220451](https://image.3001.net/images/20220524/1653384219_628ca41be49faf8176e2f.png!small?1653384220451)

ATT&CK（V9）版 T1558技术的检测

![1653384229_628ca425923f15e2264b5.png!small?1653384230094](https://image.3001.net/images/20220524/1653384229_628ca425923f15e2264b5.png!small?1653384230094)

ATT&CK（V10）版 T1558技术的检测

![1653384236_628ca42c3bf76c8f1130c.png!small?1653384236824](https://image.3001.net/images/20220524/1653384236_628ca42c3bf76c8f1130c.png!small?1653384236824)

ATT&CK（V11） T1558技术的检测

  

研究攻击者采用的攻击技术的终极目的还是为了企业提供更好的进行检测和防御方法。那么随着对攻击技术研究的不断深入丰富和发展，对攻击技术的防御和检测也就顺理成章地成为ATT&
CK的发展方向。从ATT&CK路线图我们可以看到，自从ATT&CK
V5版本将缓解措施转换为组件对象，提高知识库的价值和可用性后，在实际环境，ATT&CK发挥了较好的作用。那么对检测的组件化成为ATT&CK的另外发力方向。ATT&CK利用V9和V10两个版本完善了数据源和数据源组件的描述后，V11版本进一步增强了检测的文字描述。检测的文字描述也包含在数据源的页面中，与数据组件列出的每个技术相关联。

![1653384393_628ca4c909c4bd499c630.png!small?1653384393642](https://image.3001.net/images/20220524/1653384393_628ca4c909c4bd499c630.png!small?1653384393642)

 **更新亮点2：ATT &CK for Mobile 子技术版本**

![1653384398_628ca4ced0309a4efcf96.png!small?1653384399597](https://image.3001.net/images/20220524/1653384398_628ca4ced0309a4efcf96.png!small?1653384399597)

ATT&CK for Mobile V11

ATT&CK for
Enterprise在V7版本进行了技术的重大变革，增加了子技术版本后，受到了大家的好评。子技术的出现，让ATT&CK框架更加精炼，主要表现为以下几个方面：一是使整个知识库的技术抽象层次属于同一个层级；二是将技术的数量控制在可管理的水平，避免爆发式增长；三是通过便捷式新增子技术更新，来减少对技术本身修改。

本次更新带来了ATT&CK for Mobile 子技术测试版，正式版预计在夏天正式发布。本次的ATT&CK for
Mobile测试版，包括12战术，78技术，41子技术。

 **更新亮点3：用于ICS的ATT & CK正式加入 attack.mitre.org**

![1653384433_628ca4f1636edd24b2f32.png!small?1653384434115](https://image.3001.net/images/20220524/1653384433_628ca4f1636edd24b2f32.png!small?1653384434115)

（1）ATT&CK for ICS自2020年ATT& CK V6版本发布后，一直作为一个单独站点，这次MITRE将 ATT&CK for ICS
合并到首页中，可以通过https://attack.mitre.org/matrices/ics/ 直接访问。

（2） 将ICS和Enterprise 涉及的组织和软件进行了合并，在这些组织和软件的描述中将分别看到ICS和Enterprise。

![1653384514_628ca5428cc1d8fb17ab7.png!small?1653384515231](https://image.3001.net/images/20220524/1653384514_628ca5428cc1d8fb17ab7.png!small?1653384515231)

例如ID：S06063 Stuxnet 的软件技术使用截图

https://attack.mitre.org/versions/v11/software/S0603/

（3）
将ICS和Enterprise的数据源和数据组件进行了合并。由于ICS和Enterprise的数据源之间存在相当多的重叠，因此增加了一个过滤器，允许在整个数据源列表和单个数据源页面上分别查看ICS、Enterprise或者所有的数据源和组件。

![1653384523_628ca54baf5a834d4482c.png!small?1653384524218](https://image.3001.net/images/20220524/1653384523_628ca54baf5a834d4482c.png!small?1653384524218)

##  **02** 回顾ATT &CK的更新历程

MITRE是美国政府资助的一家研究机构，该公司于1958年从MIT分离出来，并参与了许多商业和最高机密项目。MITRE在美国国家标准技术研究所（NIST）的资助下从事了大量的网络安全实践。MITRE在2013年推出了ATT&CK模型，它是根据真实的观察数据来描述和分类对抗行为。ATT&CK将已知攻击者行为转换为结构化列表，将这些已知的行为汇总成战术和技术，并通过几个矩阵以及结构化威胁信息表达式（STIX）、指标信息的可信自动化交换（TAXII）来表示。

2018年开始ATT&CK具备了现在框架的雏形，由于其对攻击技术的描述引发了行业的关注。V1和V2版现在官网已经不提供查看，具体内容可以在github进行下载；V3版本是在官网可以查看的最老的版本。从此时开始ATT&CK开始了一年两更的频率。V4版本增加了“Impact（影响）战术，对技术进行了丰富；V5版本侧重于对缓解措施的丰富，赋予了缓解措施条目编号和具体的描述。这可以看到，ATT&CK慢慢从分析攻击技术到如何由攻到防的发展。V6版本最大的变化是增加了以云为中心的技术，添加了三个基础架构即服务
(IaaS) 平台，即亚马逊网络服务 (AWS)、微软 Azure (Azure)和谷歌云平台 (GCP)。软件即服务
(SaaS)平台将涵盖针对一般基于云的软件平台的技术。除了 IaaS 和 SaaS，还添加了两个云软件平台，Azure Active Directory
(Azure AD)和Office 365，以涵盖针对这些特定平台的技术。在V6版本发布稍后2020年1月7日，发布了ATT&CK for ICS
，其中包含81种攻击技术。版本V7则包括一个测试版 (V7beat) 和正式版
(V7)，对攻击技术的分析结构进行了重大调整，通过将攻击“技术”进一步拆解为攻击“子技术”，使得整个知识库的技术抽象属于同一层次，未来可以通过便捷式的新增子技术更新，来减少对技术本身的修改，也形成面向攻击者作业手段的更加精准的刻画。版本V8
进行了战术调整，也就是将之前的“Pre-”和“Enterprise/企业”合并为统一的企业版，弃用了 PRE-ATT&CK 域，添加了两个新的
战术Reconnaissance and Resource Development 来替换PRE-ATT&CK；另外，增加了“Network/网络”模型。版本V9调整了云模型，增加了“Containers/容器”模型，但其最主要的工作是进行了数据源的优化，实施了数据源优化的第一阶段工作。版本V10则完成了数据源优化的第二阶段工作，增加了一组新的数据源和数据组件对象。版本V11着重对检测的重构，企业版中的检测现在和数据源和数据组件相关联；同时引入子技术的移动版的
beta 版；工控版加入到 MITRE ATT&CK 官网。

ATT&CK框架更新历程表

版本

|

时间

|

内容变化

|

变化说明  
  
---|---|---|---  
  
V1

|

2018.01.06-
2018.04.12

|

企业版战术10、技术188

|

正式发布V1  
  
V2

|

2018.04.13-
2018.10.22

|

分类：Enterprise（Windows、Linux 和 macOS），Pre-,

企业版战术11、技术219

|

增加战术:

Initial Access  
  
V3

|

2018.10.23-
2019.04.29

|

分类：Enterprise（Windows、Linux 和 macOS），Pre-,Mobile

企业版战术11、技术223

|

可以在官网查看的最旧版本。  
  
V4

|

2019.04.30-
2019.07.30

|

分类：Enterprise（Windows、Linux 和 macOS），Pre-,Mobile

企业版战术12、技术244

|

增加战术Impact  
  
V5

|

2019.07.31-
2019.10.23

|

分类：Enterprise（ALL,Linux,macOS,Windows），Pre-,Mobile

企业版战术12、技术244

|

引入了“缓解措施”  
  
V6

|

2019.10.24-
2020.03.30

|

分类：Enterprise（Windows,macOS,Linux,Cloud），Pre-,Mobile（Android，IOS），ICS

企业版战术12、技术266

|

增加了云、工控  
  
V7 beta

|

2020.03.31-
2020.07.07

|

分类：Enterprise（Windows, macOS ,Linux,Cloud<iaas(aws,azure,gcp), saas

office365,Azure AD >），Pre-,Mobile（Android，IOS），ICS

企业版战术12、技术156，子技术260

|

技术细化为子技术  
  
V7

|

2020.07.08-
2020.10.26

|

分类：Enterprise（Windows,macOS,Linux,Cloud），Pre-,Mobile（Android，IOS），ICS

企业版战术12、技术156，子技术272

|

更新了技术，第一个以子技术为代表的正式版  
  
V8

|

2020.10.27-
2021.04.28

|

分类：Enterprise（Pre,Windows,macOS,Linux,Cloud,Network,）,Mobile（Android，IOS），ICS

企业版战术14、技术177，子技术348

|

Pre并入企业版，战术增加为14，增加了Network平台  
  
V9

|

2021.04.29-
2021.10.20

|

分类:Enterprise（Pre,Windows,macOS,Linux,CloudNetwork,Containers）,Mobile（Android，IOS），ICS

企业版战术/技术：战术14、技术185个、子技术367

|

数据源描述-I，调整云，增加Google Workspace，增加容器。  
  
V10

|

2021.10.21-
2022.04.25

|

分类：Enterprise（Pre
,Windows，macOS,Linux,Cloud,Network,Containers），Mobile（Android，IOS），ICS

企业版战术/技术：战术 14、技术188个、子技术379

|

数据源描述-II，技术内容继续丰富。  
  
V11

|

2022.04.26

|

分类：Enterprise（Pre
,Windows，macOS,Linux,Cloud,Network,Containers），Mobile（Android，IOS），ICS

ATT&CK v11 的企业版：战术14、技术 191 个，子技术 386 个。移动版技术 78个，子技术 41 个。工控版技术 78 个，无子技术

|

更新了企业、移动和ICS的内容。检测重组  
  
##  **03** 三条发展方向相辅相成，ATT&CK不断地壮大

通过上述回顾ATT&CK的版本更迭历程，不难看到ATT&CK的三条发展反向，每次更新都是这三个方向的一次深化，助力ATT&CK不断壮大。

![1653384474_628ca51ae5002df60db4f.png!small?1653384475497](https://image.3001.net/images/20220524/1653384474_628ca51ae5002df60db4f.png!small?1653384475497)

1、持续保持对攻击技术的关注，不断收集最新的攻击组织和攻击软件的特点对攻击技术和子技术进行丰富填充，这是ATT&CK的立足之本；

按照ATT&CK的路线图，今年10月份将要发布的V12版本会带来本年度最大的变化就是行动内容（Campaigns）元素的增加，如果经常使用攻击工具的人不会对这个词陌生。这个内容的意义也比较重大，比如有些攻击行为是没有组织命名的，也就是没有APT编号，反之有APT编号的组织在不同的攻击目标下选取的攻击路径和攻击技术也不尽相同。对于行动内容的描述可以增加我们对网络攻击者的理解，对于每一次攻击行为链路的理解。

2、不断扩充框架在各种基础设施方面的覆盖，包括网络、移动端、云、容器，以及ICS的不断纳入ATT&CK家族框架，持续扩展ATT&CK适用的场景和平台；

3、攻击技术的防御和检测组件化将ATT&CK攻击技战术知识，落地为实际防御能力。ATT&CK通过这条路线完成了从对攻击技术的观察到更好地指导企业进行攻击缓解和企业级检测和防御。

参考

https://attack.mitre.org/

https://mp.weixin.qq.com/s/1pJo_b979rqqKP9ldC13Vg

