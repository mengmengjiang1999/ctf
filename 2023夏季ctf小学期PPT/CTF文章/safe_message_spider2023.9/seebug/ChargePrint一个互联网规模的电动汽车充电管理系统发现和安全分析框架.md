**作者：Tony Nasr, Sadegh Torabi, Elias Bou-Harb, Claude Fachkha and Chadi Assi**

**译者：知道创宇404实验室翻译组**

**原文链接：<https://www.ndss-symposium.org/ndss-paper/chargeprint-a-framework-for-internet-scale-discovery-and-security-analysis-of-ev-charging-management-systems/ >**

## 摘要

电动汽⻋充电管理系统 (EVCMS) 是一组专⽤软件，允许⽤⼾远程操作电动汽⻋充电站 (EVCS)。随着为⽀持不断增⻓的全球电动汽⻋⻋队⽽部署的 EVCS
数量不断增加，EVCMS 的数量也在不断增加，从⽽引⼊了新的攻击⾯。在本⽂中，我们提出了一种新颖的多阶段框架 ChargePrint，⽤于发现互联⽹连接的
EVCMS 并调查其安全状况。ChargePrint 利⽤从 EVCMS
⼩种⼦中提取的标识符，通过迭代指纹识别以及分类和聚类⽅法的组合来扩展设备搜索引擎的功能。使⽤部署于 9 个不同 EVCMS 的 1,800
个已发现主机的初始种⼦，我们确定了由 44 个独特 EVCMS 检测的 27,439 个在线EVCS。我们深⼊的安全分析通过研究 120
个零日漏洞，凸显了所部署的 EVCMS 的不安全性，这揭⽰了针对
EVCS、其⽤⼾以及连接的电⽹进⾏⽹络攻击的可⾏性。最后，我们建议用户采取对策来减少潜在的威胁，同时我们也通过与系统开发⼈员/供应商进⾏协调漏洞披露
(CVD) 为 EVCS ⽣态系统的安全做出了贡献。这些系统开发⼈员/供应商承认并为发现的漏洞分配了 20 多个 CVE-ID。

## I．简介

电动汽⻋充电管理系统 (EVCMS) 是一组专⻔软件，⽤于检测底层电动汽⻋充电站
(EVCS)。它们为⽤⼾/运营商提供先进的功能、界⾯和⼯具来远程监视、控制和管理其 EVCS
的操作，包括安排充电会话、计费/⽀付、记录保存和⽤⼾管理/⾝份验证[1]。

鉴于政府为刺激电动汽⻋的购买⽽提供的激励措施[2]，全球电动汽⻋市场正在快速增⻓，⽬前包括1100 万辆[3]。同样，通过在公共/私⼈空间部署⼤量 EVCS
来满⾜不断增⻓的客⼾需求，电动汽⻋充电基础设施也在不断扩展。[4]。这意味着部署的 EVCMS 数量会增加，以检测已安装的
EVCS。因此，电动汽⻋充电⽣态系统会随着扩散的攻击⾯⽽⾯临⼤量安全挑战。

具体来说，不同且大多数EVCMS 是主要针对特定供应商的临时开发。它们普遍缺乏法规，导致整个电动汽⻋充电⽣态系统⾯临各种威胁。事实上，EVCMS
构成了对⼿的主要⽬标，因为它们提供了一个远程攻击向量，可以破坏底层
EVCS、其充电操作和连接的关键基础设施。特别是，此类攻击的影响会随着其直接集成到电⽹⽽被放⼤[5]。

尽管如此，之前的⼯作重点仍是调查电动汽⻋充电⽣态系统的安全性[6]，[7]，⼈们对⼴泛部署的 EVCMS 的安全状况缺乏了解。⼤量部署的 EVCS 及其
EVCMS 作为新的可⾏攻击⾯，它们扩展的远程功能也受到了推动。我们的⽬标是通过评估已实施的 EVCMS
在野外的安全性来⾸次探索这种威胁态势，这需要在整个互联⽹上发现和映射 EVCMS 实例及其主机。由于缺乏有关已部署 EVCS
的经验数据，这是一项具有挑战性的任务。此外，与典型的物联⽹（IoT）设备不同，利⽤现有的指纹识别⽅法[8]，[9]来识别 EVCMS
从而准确发现连接互联⽹的 EVCS是不切实际的。主要因为 EVCMS 是基于云的，并且往往具有闭源实现特性。此外，虽然部署的 EVCMS
具有有限且重要的横幅，但由于其多样性和开发⼈员之间标准化的缺失，它们往往具有有限的(或没有)⽤于识别它们的搜索引擎标签和横幅规则。

为了应对这些挑战，我们提出了一个多层框架ChargePrint，⽤于指纹识别和发现互联⽹连接的 EVCS，并评估其 EVCMS
的安全性以防⽌远程利⽤。该框架依赖于分析候选 EVCMS
的种⼦，从其横幅中提取标识符，然后利⽤著名的在线设备搜索引擎以及分类和聚类⽅法的组合来执⾏迭代发现/指纹识别。因此，该框架通过一系列混合技术（检查相应的可访问
EVCS 固件进⾏⽩盒分析，以及通过在线检查EVCMS 实例端点进⾏⿊盒分析），对已识别的 EVCMS
及其主机实例进⾏深⼊的安全分析。此外，根据使⽤ChargePrint 的分析结果，我们说明了⽹络攻击的可⾏性，并讨论了它们对
EVCS、其⽤⼾和运营商以及互联电⽹的影响。

此外，在我们建议采取缓解对策的同时，我们还将我们的调查结果传达给受影响的供应商，以引起⼈们对现有漏洞的关注。事实上，一些系统开发商（例如施耐德电⽓、Cornerstone
Technologies）已经承认了我们的发现，并且这些漏洞被分配了超过 20 个常⻅漏洞和披露 (CVE) ID [10]。最后，通过演⽰易受攻击的
EVCMS 实施对电动汽⻋充电⽣态系统进⾏⼤规模攻击的可⾏性，我们希望激励系统开发⼈员重新评估和提⾼其 EVCMS 的安全性，并减少未来实施中的威胁。

**本文主要贡献总结如下：**

1) 我们提出了一种新的多层框架（ChargePrint）来解决EVCS 发现/指纹识别问题，并通过获取和利⽤有关EVCMS 独特标志和特征的信息来解决
EVCMS 经验数据的缺乏问题。此外，为了证明我们的⽅法的有效性，我们用它实现了 ChargePrint 并⼤规模利，还发现了27,439 个连接互联⽹的
EVCS 主机实例。这些实例由 44种不同的 EVCMS 产品进⾏检测。据我们所知，我们是第一批在野外调查 EVCMS 实例的公司之一。

2) 我们⾸次尝试对 EVCMS 进⾏全⾯的安全分析，定义了电动汽⻋充电⽣态系统中的新攻击⾯。我们通过在ChargePrint
中实施混合安全分析的⽅法来检查各种特定供应商的 EVCMS 产品的固件和在线实例，从⽽突出显⽰EVCMS
中的主要安全缺陷。此外，我们还定制了⾃动扫描模块，进⾏⼤规模EVCMS漏洞分析。分析发现25,300台EVCMS主机受到了120个可远程利⽤的零日漏洞的影响。此外，我们将我们的发现传达给了相应的系统开发⼈员，他们承认了这些发现并分配了
20 多个 CVE-ID。

3) 通过讨论针对电动汽⻋充电利益相关者（即 EVCS、⽤⼾/运营商和电⽹）的攻击影响，我们揭⽰了现有 EVCMS
的不安全性。更重要的是，我们建议采取缓解对策，以加强已部署的系统抵御⽹络攻击的能⼒。我们通过报告的调查结果激励开发⼈员提⾼现有和未来 EVCMS
产品的安全性，从⽽为⼴泛⽣态系统的安全做出贡献。最后，我们通过跟踪制造商发布的补丁并调查其实际部署情况，重新评估 2022 年 EVCMS 的安全状态。

本⽂的其余部分安排如下。我们将在下一节中介绍相关背景信息，并在第III节中详细描述拟议框架。第一部分介绍了所实施框架的实证评估以及实验结果、对电动汽⻋⽣态系统的威胁影响以及可能的缓解策略IV。漏洞披露信息和补丁后续⼯作以及经验教训和未来的⼯作研究⽅向
分别在V和 VI各节中注明。最后，在VIII总结本⽂的主要内容之前，我们在VII中检查相关⼯作。

## II. 背景

**EVCS vs 物联网：** EVCS及其 EVCMS 具有一些常⻅特征，例如⽤于远程管理的互联⽹连接。但与物联⽹设备及其嵌⼊式软件相⽐，EVCS及其
EVCMS 具有许多独特的特征。

**_第一_**
，EVCS配备了⽐物联⽹设备更⼤的处理单元和存储容量，以满⾜EVCMS存储和处理充电记录和活动⽇志的需求，并确保其繁重的性能要求和持续服务得到满足。因此EVCS可以做到将电能输送到电动汽⻋支持全天使⽤，实现⻓时间的充电周期。

**_第⼆_** ，EVCS 的电⼒电⼦电路旨在维持⽐物联⽹设备⼤得多的电源，因为它们需要从电⽹向电动汽⻋电池供电[11]。EVCS 根据其最⼤供电量区分了
3 个主要类别： 1 级通过120V AC输出功率为 1.5-2
千⽡的插座来提供电⼒；2级通过208-240V连接峰值功率为19千⽡（平均7.2千⽡）的功率提供电⼒输出，3级通过480-800V
AC输⼊峰值功率⾼达240千⽡平均 110千⽡提供充电。

**_第三_** ，物联⽹设备依赖于各种协议（例如 BLE、ZigBee等）来操作和提供某些功能 [12]，EVCS
依赖于运营商设计的专有协议，以允许各个⽣态系统实体以及 EVCMS 之间进⾏通信，这对于管理和控制 EVCS
的各种操作和功能而言⾄关重要。具体来说，为了标准化这种通信，开放充电联盟 (OCA) 于2012 年设计并推出了开放充电点协议 (OCPP) [13]
考虑了EVCS 消息交换事实上的标准应⽤协议。

**_第四_** ，EVCS
的设计⽬的是与⽤⼾/操作员进⾏定期的、直接的交互，这与部署在公共场所（例如闭路电视）的物联⽹设备不同。物联网设备不会近距离使用，也不会像EVCS设置的那样频繁地每天发生交互。

**_第五_** ，EVCMS 提供了⽐⼤多数物联⽹设备固件更⼤、更复杂的软件界⾯。EVCMS 包含⼤量功能，因此具有更⼴泛的代码库和结构，来适应 EVCS
提供和要求的各种操作。特别是，EVCMS 旨在实时组织和跟踪电动汽⻋调度，以及管理充电记录。除了远程管理之外，EVCMS还为 EVCS 本⾝的⼈机界⾯
(HMI) 等物理接⼝提供⽀持。EVCMS还需要处理充电 ID 令牌，例如近场通信 (NFC) 卡。EVCMS
还实现了复杂的访问控制机制、⽤⼾⾝份验证和管理、⽤⼾⻆⾊隔离和权限矩阵，这些在通常在以单个或有限⽤⼾/权限运⾏的物联⽹软件中不可⽤。虽然⼤多数 IoT
设备固件使⽤标准打包压缩格式进⾏交付和设备部署（例如 LZMA 和 Zip），但许多 EVCMS 仍使⽤⾃定义和专有压缩格式（例如
EPK）。我们还注意到，物联⽹设备固件使⽤更常⻅的⽂件系统类型（例如squashfs），然而EVCMS使⽤不太常⻅的⽂件系统类型（例如JFFS2）。

**EVCMS 资产：** EVCMS可以采⽤不同的部署模式，其中基于固件和基于云的模式最为突出。基于固件的模型是通过将应⽤程序⽤⼾界⾯ (UI)
⽂档集合（即 Web 界⾯⽂件）直接嵌⼊到EVCS 固件中来实现的，EVCS 固件是最⼩化的操作系统(OS)，旨在提供对 EVCS
的低级控制硬件。基于云的模型是在云中的 Web 服务器上实现的，该服务器与 EVCS 连接并进行通信。在这项⼯作中，我们研究了基于固件和基于云的
EVCMS软件产品，并对它们的各种实例进⾏了深⼊的漏洞分析。

**指纹识别和发现：**
一般来说，发现联⽹设备依赖于指纹识别和横幅分析。指纹识别是设备查询的映射：对设备类型等类标签的响应。横幅分析则执⾏互联⽹范围内的协议扫描（例如
HTTP、SSH）并收集应⽤层数据（即横幅）以提取⽂本信息并使⽤一组规则识别设备。在⽂献中，已经介绍了⼏种框架来发现和识别⾯向互联⽹的设备[9]，[14]。

然⽽，尽管在识别通⽤物联⽹和⼯业控制系统（ICS）远程管理设备⽅⾯取得了有希望的结果[8]，由于各种原因，这些⽅法对于注释EVCS是⽆效的；(1) 与在线
EVCMS 相关的横幅有限；(2) EVCMS 相关信息⼤多基于云或闭源，很难找到；(3)
与⼤量通⽤物联⽹设备模型相⽐，在缺乏使⽤传统指纹识别技术识别这些系统的横幅规则的情况下，EVCMS
规范更难获得；(4)ICS设备可以通过设备搜索引擎提供的内置标签来识别，但EVCMS却没有；(5)
EVCMS的多样性和缺乏标准化开发，导致横幅表⽰形式多种多样，难以分析和跟踪。由于各种产品及其功能之间的差异，使得提取和搜索有关它们的有⽤信息变得困难。这些因素使得利⽤现有⽅法来准确有效地定位
EVCS 并对其进⾏指纹识别是不可⾏的。因此，我们开发 ChargePrint 来克服这些挑战，并提出一种有效的EVCMS
发现和指纹识别⽅法，这是分析其安全态势的先决条件。

**设备搜索引擎：**
⼤多数在线设备搜索引擎通过主动扫描互联⽹（例如，IPv4地址空间）来收集有关互联⽹连接设备/主机的信息，同时执⾏后续的横幅分析以tag/label所识别的主机。鉴于主机横幅和已识别设备信息的存储库如此丰富，我们通过应⽤程序编程接⼝（API）利⽤现有解决⽅案，依靠被动扫描（基于元扫描）技术[15]来实现搜索。具体来说，我们使⽤四个最著名的设备搜索引擎进⾏实验：(1)
Shodan [16]：执⾏连续检测和监控，通过索引其服务横幅/元数据来收集有关互联⽹连接设备的实时信息；(2) ⼈⼝普查系统 [17
号]：通过定期探测公共IP地址和域名来监控可访问互联⽹的设备；(3) **ZoomEye**
[18]：收集有关在线设备和服务的信息，旨在提供互联⽹规模的威胁检测；和（4）Fofa[19]：提供有关互联⽹连接设备⽹络资产、范围分析和应⽤程序流⾏度统计的情报。

**漏洞分析：** 我们解决了⽂献中的关键差距[20]，[21] ⾸次尝试分析基于固件和基于云的 EVCMS 产品的安全性，特别是EVCMS
针对远程攻击的弹性。为了执⾏此分析，我们利⽤⽩盒技术来检查可⽤的 EVCMS 固件和脚本，并利⽤⿊盒技术来检查从在线 EVCMS
端点提取的资产。我们主要专注于检测和发现可远程利⽤的 EVCMS 漏洞，这些漏洞将允许访问和控制各个系统及其底层 EVCS。我们特别提到 OWASP
[22] 和MITRE 解决最重要的安全问题 [23]，并且对于每个都开发了系统的⽅法来推断它们在特定 EVCMS 中的存在。

## III. 拟议框架：ChargePrint

我们设计并实施了ChargePrint，这是一个多阶段框架，⽤于通过发现互联⽹连接的 EVCS 主机实例并检查其 EVCMS 的安全性来探索 EVCS
威胁态势。如图1所⽰ChargePrint 有两个主要核⼼部分，即发现活动和安全分析活动。我们展⽰了ChargePrint
的详细内部架构，它由多个互连的组件和层组成，⽀持发现和安全分析的迭代操作。

### _A.发现_

⾸先，我们进⾏发现操作，以查找野外连接互联⽹的EVCMS 主机实例并对其进⾏指纹识别，然后利⽤它们来扩展EVCMS
产品的知识，同时为识别攻击⾯以进⾏安全分析铺平道路。接下来，我们详细阐述该框架的发现活动的模块。

**_1）种子储存：_** 为了引导发现活动，我们通过从初步查找中收集和存储的 EVCMS 种⼦来构建初始数据库，其中我们利⽤查询
Shodan、Censys、 **ZoomEye** 和Fofa 中的索引主机扫描数据以及与 EVCS 相关的 23 个关键字（例如，EV
充电器、EVCS）的列表以及已知的 EVCMS 产品。为了验证这些系统，我们⼿动检查其 Web
⽤⼾界⾯横幅的特定指标，例如产品系列/型号和供应商名称/徽标，并将它们与可⽤的相应 EVCMS
开发⼈员的软件包⽂档中的信息相关联。此外，我们选择信息最多的主机作为初始 EVCMS 候选集，并将其横幅存储到数据库中进⾏分析。

**_2）标识符提取：_** 下⾯我们详细阐述分析种⼦ EVCMS 以提取可⽤于区分各种 EVCMS 产品的标识符。

![](https://images.seebug.org/content/images/2023/08/6568b353-170a-4efb-b86d-a60d036c198f.jpg-w331s)

**收集资产:** 为了获取资产，我们收集并检查可通过固件包访问的 EVCMS 产品、在线部署的基于 Web
的实例的⻔⼾以及与拥有⾃⼰⽹站的供应商/开发⼈员相关的产品。我们注意到，并不总是能够获得给定 EVCMS
产品的所有这些资产，因为某些情况下供应商/开发商⽹站上没有可供下载的相应固件。

为了收集 EVCMS 固件，我们使⽤由产品和开发⼈员名称、⽹站链接以及包扩展等关键字组成的 dork
来查询⽹络搜索引擎，以搜索属于产品供应商/开发⼈员的索引⽹站。然后，我们通过使⽤ Scrapy
递归地抓取超链接来检查这些⽹站的站点地图，寻找可以保存固件（例如
/download）的潜在端点[24]从而抓取⽹⻚，直到到达潜在的固件获取端点。为了收集基于 Web 的 EVCMS，我们探测主机实例的主要⻔⼾端点并下载其
Web ⽂档（即 HTML 和 CSS ⽂件）以及其他可访问端点的⽂件及其语⾔变体。

**解析资产:** 为了解析下载的固件，我们提取它们的包并通过雕刻和探索文件系统以及利用binwalk 的 API
构建的自定义实用程序转储嵌入的文件、二进制文件和目录[25]。为了解析获取的⻔⼾，我们通过检查⻔⼾ Web ⽂档的⽂档对象模型 (DOM)
结构来检查它们。到解析收集到的供应商⽹站，我们抓取他们的⽹⻚并累积 HTML 标记内包含的⽂本字符串。

**提取标识符:** 接下来，我们提取一组标识符这使我们能够准确地代表各⾃的 EVCMS
候选者并将其与其他产品区分开来。提取来⾃固件的标识符，我们在⽂件系统树中找到唯一的⽂件/⽬录路径名（例如，/cgi-bin/cgiServer）这将作为EVCMS产品的直接指标。为了从⻔⼾⽹站中提取标识符，我们搜索 HTML⽂档的 DOM，使⽤正则表达式，⽤于充当
EVCMS 指⽰符的特殊元素，例如产品名称、版本、供应商/开发⼈员名称和徽标。在图2，我们展⽰了主要⻔⼾的屏幕截图查看通过 ChargePrint 发现的
EVCMS 的一些⽰例。与供应商/开发商⽹站一样，我们从先前积累的字符串中堆积出 EVCS 相关⽂本列表（例如EV 充电解决⽅案），以丰富我们的
EVCS扩展发现 EVCMS 的术语知识实例.以表I中为例，我们提出一组在 EVlink EVCMS产品上运⾏的候选者的标识符。
![](https://images.seebug.org/content/images/2023/08/e7796f4b-abd6-49d3-997d-c9d141793229.jpg-w331s)
(a)EVlink
![](https://images.seebug.org/content/images/2023/08/c5aa5685-45b9-422b-87ad-da7edf8fa3eb.jpg-w331s) (b) CSWI Etrel 图2:(a) EVlink和(b) CSWI Etrel
EVCMS主要门户网站的屏幕截图

**_3）查询和数据验证：_** 在这个阶段，我们利⽤提取给定 EVCMS 产品的标识符，以发现由我们已拥有其标识符的相应 EVCM
检测的主机实例，以及利用提取的 EVCS 字符串单词表的组合来发现新的 EVCMS 产品。
![](https://images.seebug.org/content/images/2023/08/97a8c48d-21db-43a9-9af3-efb2b089bc8a.jpg-w331s)
表I：EVlink标识符⽰例集

**查询引擎:** 我们通过以下两种⽅法利⽤提取标识符，⽬的是通过查询设备搜索引擎来扩⼤搜索范围并执⾏扩展的系统收集，以找到更多由当前已知的 EVCMS
产品和新的
EVCMS候选产品配备的主机实例。⾸先，我们使⽤提取的产品特定标识符执⾏有针对性的搜索，以过滤其横幅与查询信息匹配的主机。其次，我们使⽤从供应商/开发⼈员⽹站上找到的提取的
EVCMS 字符串/关键字编译的单词列表对 EVCS 相关的横幅主机数据进⾏一般搜索。

**相似性分析:** 由于我们的通⽤搜索结果可能包含属于不同 EVCMS 的各种主机，因此在将它们与先前检测到的现有或新 EVCMS
关联之前，我们需要进一步验证。因此，我们引入了一种新的相似性度量（DOMetric）来比较给定主机的 HTML 页面 （H），其中包含数据库中已知的
EVCMS 候选 （C），以识别正在运行分配给同一 EVCMS 产品系列的服务的主机实例基于其服务和接口的相似性;因为运行同一 EVCMS
产品变体的主机实例将具有相同或高度相似的 Web 文档。

为了使⽤ DOMetric 确定相似度得分，我们⾸先解析 EVCMS ⻔⼾的 HTML ⻚⾯以提取其结构、样式和⽂本内容。我们通过解析 EVCMS 门户的
HTML 页面来提取其结构、样式和文本内容。我们通过使用执行成对比较来确定结构相似性
D1（H，C）格式塔模式匹配方法[26]在序列上的标记，然后我们利⽤方程1查找已识别主机的标签之间的最⻓公共序列（LCS）（S1）和数据库中已知的
EVCMS 候选者（S2）。对于样式相似性 D2（H、C），我们从⽂档的 HTML
中收集嵌⼊的样式声明块和公共标签的选择器，并找到两个⽂档之间最⼤数量的公共声明，A（主机）和B（候选 EVCMS），使⽤ Jaccard
指数（公式2）。最后，我们通过⽮量化确定⽂本相似度（D3）主机标签内的封闭⽂本（T1）和候选⼈（T2）按照它们在 HTML
中出现的顺序排列，然后使⽤余弦相似度指数（公式3）对它们进⾏⽐较。
![](https://images.seebug.org/content/images/2023/08/be74e7d1-1375-4ab5-8b32-89f7cff38b27.jpg-w331s)
![](https://images.seebug.org/content/images/2023/08/b087eff2-2e9a-46ed-b647-6fbddf9cd07b.jpg-w331s)
**主机标签：** 通过这些相似性度量，我们使⽤方程4计算每对主机的总DOMetric 分数（H）和候选
EVCMS（C），w是一个⽐例因⼦（例如，w=13）。其余未标记的主机将保留使⽤随后的⼆元分类器进⾏进一步调查。
![](https://images.seebug.org/content/images/2023/08/b68cfa46-a1c0-42ab-960f-630cccec988c.jpg-w331s)
**_4）系统识别：_** 在此阶段，我们检测属于已知 EVCMS 产品的主机的实例（即，数据库中具有种⼦候选），并确定属于新 EVCMS
产品的实例，我们从中选择数据库候选，并删除不代表 EVCMS 主机的通⽤ (IoT) 设备实例。

**主机分类：** 由于扩展查询和数据验证中存在⼤量未标记主机，我们采⽤了利⽤ 14 个特征的⼆元分类器（表II) 以确定这些主机是否是 EVCMS。
![](https://images.seebug.org/content/images/2023/08/6b5b88e2-9fa5-4cff-9b0a-15af6689bd0d.jpg-w331s)
表 II：⼆元分类器的数据集特征

我们通过从手动检查和标记的 1，000 个主机实例（基本事实）的数据集中提取特征来评估四种常见的分类器（逻辑回归、k
最近邻、朴素贝叶斯和支持向量机），这些数据集具有 500 个 EVCM 和 500 个非 EVCMS 主机，分为训练 （70%） 和测试 （30%）
以进行验证。根据表3中提供的评估指标结果，我们选择逻辑回归（LR）算法作为首选分类器模型，因为它优于其他模型，具有显着更高的准确性（93.1%）和F1-Measure（94.2%）值。但是，对于未来的工作，可以通过评估更广泛的机器学习模型。

**主机集群:** 为了在通过⼆元分类识别的 EVCMS 实例中识别新产品，我们设计并实现了算法1对新识别的进⾏聚类
![](https://images.seebug.org/content/images/2023/08/9e352cf6-b03a-4cea-882f-2045f9f19a71.jpg-w331s)
表III：⼆元分类算法的评估
![](https://images.seebug.org/content/images/2023/08/47b16b79-62e4-4c4f-9537-d4e2ed7fa318.jpg-w331s)
EVCMS 根据使⽤ DOMetric 分数⻚⾯ HTML的相似性，将属于相同 EVCMS
产品的相关组托管到相关组中（回想一下方程4）。该算法将实例元组列表作为输⼊（ _β_ ) 并返回更新后的列表 _β′_
具有各⾃的集群分配。每个实例的元组包含一个索引 _i_ ，用于在其他实例中引用和标识它、门户 HTML 内容 _p_ 、集群标识符 _cId_
（默认情况下初始化为 0，表示主机尚未分配给集群）和一个布尔值标志 _cnd_ ，指示此实例是否为候选项。我们定义了一个函数 _DOMetric（）_
来计算两个网页的 DOMetric 分数，以及一个函数 _maxContent（）_ 来比较两个网页以确定具有较大内容和较新版本字符串的网页。

选择 DOMetric 阈值 为要使算法准确地将主机关联到同一集群中，必须选择有效的 DOMetric 相似性阈值 （ _α_
）。根据我们的观察，属于同一产品系列的已部署系统始终具有非常相似的结构和接口，除了由于差异而产生的差异到集成新组件的产品版本变型。EVCMS
产品版本变体是特定 EVCMS
产品系列的实例，由于版本差异，其构建有所不同，因此，虽然这些变体彼此不同，但它们仍然共享⾮常相似的结构和⽂件系统，并且属于相同的 EVCMS 产品系列。
![](https://images.seebug.org/content/images/2023/08/107d7635-9a34-4f7f-bfe8-3e0984f973a2.jpg-w331s)
图 3：通过算法 1 的实验找到 DOMetric 阈值

因此，我们必须选择一个适当的阈值，以考虑不同 EVCMS 产品系列以及属于同一产品系列的版本变体之间的差异。为了确定优化的 DOMetric
阈值，我们通过运行算法 1 进行多项实验，该算法的 DOMetric 阈值 （α） 范围从 0 到 1（包括 0 到 1），在三个自定义数据集（即集合
#1、集合 #2 和集合 #3）上进行，包含 500、2，000 和 3，500 个 EVCMS 产品主机实例，由 5 个， 分别为 10 个和 15 个
EVCMS 产品系列，以及 13、29 和 41 个 EVCMS 产品版本变体。

如图3，我们注意到三个趋势。⾸先，当以低的速度运⾏算法时α值（α≤0.8),我们观察到簇的数量保持在1，然后稳步增加。簇编号不正确，表明较低的阈值会导致所检查的系统之间存在较⼤的重叠；任何显著不同的⽐较系统（即属于不同的
EVCMS 产品系列）将由于低聚类条件（⼩α）导致聚类过程出错。其次，当运⾏算法时α值范围从 0.8 到 0.9，我们观察到 Set #1、Set #2 和
Set
#3的簇数⼏乎与在每个集合中找到的正确簇数相关。事实上，阈值应该是出于对分析/⽐较的系统主机实例之间⾼相似率的需要⽽设定的。这对应于一组具有显着相似性的系统。因此，我们选择最⾼的DOMetric相似度阈值（α=0.9）来最⼤限度地提⾼由算法1获得的正确簇数量的准确性。第三，当运⾏算法时α如果值⾼于
0.9 且最⼤为 1，则结果会为每个集合⽣成更多数量的簇，这些簇代表 EVCMS 产品版本变体的簇。

**候选人选择：** 一旦识别出集群，我们就会检查它们并为每个集群选择有代表性的候选者（新种⼦系统）。我们通过选择部署不同版本的相应
EVCMS产品且其内容/配置⼤于其余实例的主机实例来确定相应的候选者（在算法中1的召回函数maxContent()）。随后，我们存储EVCMS
候选者进入种子 EVCMS
数据库，然后我们利用它来执行框架发现活动的新版本。这种迭代方法允许ChargePrint通过识别各种主机实例来扩展指纹识别和发现过程，这些主机实例部署了EVCMS数据库中候选产品的相同产品，其中就迭代而言，包括新旧系统。对于每个框架迭代，我们使用在发现的第一阶段收集其资产的种子
EVCMS 候选项执行新搜索。

### _B.安全分析_

对于新获得的EVCMS候选产品（种⼦），我们使⽤一系列系统⽅法进⾏深⼊的安全分析，如图1所⽰。

**_1）资产分析：_** 通过检查EVCMS组件，我们分析产品资产。这些组件代表发现漏洞的攻击⾯。

**拆除资产：**
为了进⾏安全分析活动，我们拆除并剖析收集到的资产以进⾏进一步分析。为了剖析固件映像，我们转储并安装嵌⼊式⽂件系统以探索它们包含的⽬录/⽂件，具体来说，我们搜索以找到包含
EVCMS Web 服务⽂件的 EVCMS ⽂档集合。这些⽂件提供各种接⼝和控件，其中包含⽤⼾/操作员以及外部对⼿可以访问的 EVCMS
⼊⼝点。为了剖析没有固件映像的候选 EVCMS 实例的资产，我们确定了 EVCMS 的主要 Web ⽤⼾界⾯服务以及所有其他可⽤的 Web
路径，并发现我们从中收集表单和参数的资源/脚本。此外，我们通过下载Web文档集合（如Web目录和JavaScript文件）来创建各个EVCMS主机实例的脱机镜像。

**对组件进行分类：** 为了组织分析过程，我们将获得的组件分为三类：编译⽂件（例如⼆进制⽂件、可执⾏⽂件）、⾮编译⽂件（例如脚本）和 Web 端点。我们从
EVCMS 产品的固件映像中提取已编译的⽂件，同时从 EVCMS 主机实例的固件映像和 Web ⻔⼾中收集未编译的⽂件，从 EVCMS
固件映像的⽂档集合中提取 Web
端点以及候选主机实例。特别是，我们通过自定义脚本从可用固件中提取端点，这些脚本利用树列表和预编译的自定义单词词典，通过搜索文件系统并识别 Web
文档集合目录并递归定位表示端点的有效服务器后端和前端文件，然后解析它们以提取参数。

**分析组件：** 我们对收集的组件执⾏两种类型的分析：⽩盒分析和⿊盒分析。我们利⽤⽩盒程序来检查我们可以直接完整访问的 EVCMS
组件，例如⼆进制⽂件和脚本。具体来说，我们对已编译的服务器端⼆进制⽂件（例如，cgi服务器）执⾏静态分析，对未编译的客⼾端/服务器端⽂件和脚本（例如
JavaScript、PHP）进⾏源代码审查。反汇编和反编译过程通过专⻔的软件（例如，Cutter
[27]），同时⼿动审查相应的代码路径和执⾏流程，因为发现的漏洞对于每个 EVCMS
产品和设计流程都是唯一的。源代码审查过程是通过我们编写的⾃定义脚本实现⾃动化的，这些脚本⽤于搜索潜在的易受攻击的函数和⼊⼝点，然后在⾃动化缩⼩分析范围后进⾏⼿动检查和验证。我们利用黑盒分析来调查我们无法直接访问的
EVCMS 组件，例如在 EVCMS 主机实例门户上标识的端点，由于无法获取相关的固件映像，我们无法访问其后端二进制文件和脚本。

**_2）漏洞分析：_**
随着EVCMS的发现仅仅使⽤商业扫描仪是不可能发现漏洞的，我们开发了一系列⾃定义模块、脚本、⼯具和测试程序。我们还利⽤⼿动⼯作来正确地参与 EVCMS
架构，因为这需要深⼊的调查、⼴泛的安全领域专业知识和安全编程经验来识别安全错误并有效地指导调查过程。

**部件检查：**
当通过反汇编和反编译来分析已编译的⼆进制⽂件时，我们专注于跟踪其执⾏流程以识别错误和业务逻辑缺陷。与审查源代码⽂件时一样，我们专注于查找缺乏输⼊清理和验证的⼊⼝点，从⽽允许注⼊和执⾏任意代码和查询，这是对⼿控制系统的主要⽬标。例如，在检查
EVCMS ⽂档集合中的客⼾端 JavaScript ⽂件时，我们找到了⽆法正确清理数据变量的易受攻击的函数，从⽽允许在受影响的 EVCMS
上下⽂中执⾏任意 JavaScript，从⽽破坏其逻辑和功能，从⽽通过以下⽅式攻击⽤⼾/操作员：劫持他们的会话和系统。

例如，在清单中1,
脆弱函数goToTerminal没有实现清理通过变量传递的数据的机制术语号，直接在第3/6/8⾏使⽤，允许控制数据的攻击者传递并执⾏恶意代码，破坏合法序列并覆盖EVCMS逻辑流程。最后，在调查收集的端点时，我们使⽤Burpsuite
拦截 HTTP 请求/响应流量 [28] 查找插⼊点（例如，GET/POST 参数）。

**实体测试：** 固件映像及其底层实体可⽤于某些 EVCMS 产品，但不适⽤于其他产品。因此，在研究期间⽆法访问运⾏这些EVCMS
的⼤部分代码和⼆进制⽂件。相反，我们严重依赖⿊盒测试技术来进⾏安全分析，通过在这些后端逻辑相对未知的 EVCMS
主机实例的端点上使⽤精⼼设计的⽅法来检测漏洞。该过程包括将随机数据和精⼼设计的数据跟踪到已发现的⼊⼝点（例如输⼊、参数）以得出意外结果，同时查找漏洞迹象。为此，我们针对所分析的
EVCMS ⽣成定制的有效负载测试上下⽂，并使⽤⾃定义⼯具在相应的⼊⼝点上运⾏这些列表，以收集返回的输出以供检查。
![](https://images.seebug.org/content/images/2023/08/731b21c3-2867-4471-9ebe-401af012bdd8.jpg-w331s)
清单 1：JavaScript 函数中的弱点导致 EVCMS 代码执行

**漏洞检测：** 我们检查 EVCMS 产品以找出 OWASP 的主要软件弱点 [23]
利⽤我们定制的⾃定义测试程序来检测这些特定类别漏洞的发⽣。为了检测 SQL 注⼊ (SQLi)，我们使⽤sqlmap [29] 在 EVCMS
端点/参数上注⼊睡眠延迟查询。为了检测外部 XML 实体注⼊ (XXE) 和服务器端请求伪造(SSRF)，我们在 EVCMS HTTP
请求消息/参数/端点中附加精⼼设计的 XML 实体和地址，其中包含对我们控制的服务器的回调。为了检测硬编码凭据，我们检查 EVCMS
固件⽂件系统中的嵌⼊式凭据。为了检测逗号分隔值注⼊ (CSVi)，我们通过提供精⼼设计的 CSV 负载并检查响应来检查 EVCMS 功能和端点。

此外，为了检测跨站脚本（XSS），我们将字符串标记的 JavaScript 有效负载注⼊ HTTP
请求插⼊点（即参数、端点、标头），然后解析响应以验证注⼊。为了检测跨站点请求伪造 (CSRF)，我们检查 EVCMS获取/发布-基于配置/设置的请求缺少特定于请求的随机令牌。为了检测跨源资源共享(CORS) 和 Flash 跨域策略 (FCDP) 错误配置，我们检查EVCMS
端点的跨域策略⽂件中是否存在许可规则。为了检测信息泄露，我们解析 EVCMS 端点以获取与底层 EVCS 和EVCMS
设置/配置相关的敏感信息。为了检测强制浏览和缺少⾝份验证，我们通过验证其访问控制机制来检查 EVCMS
功能，并搜索逻辑缺陷以在⽆需登录的情况下请求⾝份验证后端点/资源。为了检测丢失的速率限制，我们向 EVCMS 端点发送一个 HTTP
请求周期，然后⽐较返回的响应以确定它们是否包含差异。

**_3）自动扫描：_** 为了使安全分析高效，我们构建了自动扫描模块（图1）。

**漏洞概念验证 (PoCs):** 一旦我们检测到各个 EVCMS 产品候选中的漏洞，我们就会为每个候选产品制作定制的特定于漏洞的
PoC，其中包括包含漏洞有效负载的请求和预期响应与证明漏洞的指标相关联，并且我们将扫描的主机实例产品模型和版本字符串与所检查系统的模型和版本字符串相关联。这样可以最⼤限度地减少发送请求的数量，并通过依赖
Shodan 等第三⽅设备搜索引擎已收集的数据和详细信息，以有限的主机交互探索索引的互联⽹扫描。因此，每当一组漏洞链接到特定的 EVCMS
产品型号和版本号时，我们就会配置 PoC 从 HTTP 横幅中提取扫描的主机实例版本字符串，然后将其与 ChargePrint
数据库中易受攻击的产品相关的详细信息关联起来。这允许证明给定 EVCMS 产品上是否存在漏洞，并自动确定受影响的 EVCMS 检测的主机实例数。

**主机扫描:** 通过迭代收集的代表 EVCMS 产品各种集群的候选主机实例数据库，我们利⽤⽣成的漏洞 PoC
⾃动确定易受攻击的实例。对于数据库中代表给定产品集群的每个候选 EVCMS，我们制作一组漏洞 PoC，以确定属于同一集群的其他主机实例是否存在漏洞。

为了报告遭受已发现漏洞的互联⽹连接 EVCMS 主机实例的确切数量，漏洞已得到确认后，我们通过发送精确数量的 PoC
请求并解析响应以对测试时的事件进⾏计数来对每台主机执⾏有针对性的扫描。我们构建此⾃动扫描的基础是，由给定 EVCMS
产品检测的主机实例必须运⾏相似或相同的构建和服务，因此将遭受相同的漏洞类别。因此，我们不是对部署给定 EVCMS
产品变体的每个主机实例重新进⾏彻底分析，⽽是对较少的实例进⾏深⼊的安全分析，同时将我们的发现推⼴到其他类似主机。

**道德考虑:** 与基于扫描的安全测量研究一样，我们遵守最佳实践[30]‒[35]。特别是，我们采取了多项措施来确保所检查的 EVCMS
的运⾏不会受到损害。

**_不可否认性：_**
在我们的扫描中，我们在传出的请求中设置了一个⾃定义⽤⼾代理字符串，以表⽰善意的意图并提供联系信息，以允许系统所有者与我们沟通，并可以选择从我们的研究中删除。我们还向我们的机器的公共
IP 地址提供了反向 DNS 记录，以允许⽬标获取有关该研究的其他信息。

**_相关扫描和非利用有效负载：_** 为了执⾏⼤规模扫描，我们依赖于之前由第三⽅设备搜索引擎（例如
Shodan、Censys）收集的互联⽹扫描数据，并且我们利⽤了不会产⽣现实⽣活中的利⽤和主动交互的⾮利⽤有效负载。我们使⽤侧通道技术通过精⼼设计的概念验证来推断漏洞，利⽤版本字符串和横幅相关性来验证漏洞的存在，⽽不会对所检查的EVCMS
造成任何损坏或持久影响，类似于设备搜索引擎的⽅式，例如作为 Shodan，确定主机是否受到特定 CVE
漏洞的影响。此外，我们还开发了⾃⼰的⽅法将⼤量主机聚集到版本化产品中，以便对代表性候选者或相应固件进⾏分析，并在特定版本中查找允许与所有相关主机关联的问题，⽽⽆需与它们交互。

**_客户端分析和测试环境：_** 我们注意到，在发现的 13 个漏洞中，有 8 个是客⼾端漏洞，它们不会影响或对分析的EVCMS
造成任何影响，因为它们是通过离线客⼾端脚本分析发现的。⾄于其余 5 个服务器端漏洞，是通过固件分析和在供应商（特别是 Cornerstone
Technologies、Bluesky Energy 和 Etrel）提供的环境中进⾏协调测试发现的。我们还通过与运行供应商特定 EVCM
综合列表的当地和国家电动汽车运营商沟通，并在执行此类资产的监控任务时在受控环境中测试 PoC，验证了 PoC 不会对分析的 EVCM
造成伤害，我们没有观察到任何破坏性结果。虽然我们没有在我们扫描的所有国际供应商上测试我们的PoC是否存在漏洞，但我们确实与少数供应商（例如，Cornerstone
Technologies，Bluesky Energy）合作，我们利用供应商提供的技术和工具来验证资产是否完好无损。我们注意到，PoC
包含不利用漏洞的被动有效负载，在最坏的情况下，可以通过重新启动 EVCMS 或 EVCS
来避免任何意外的副作用。作为额外的预防措施，在适⽤时，我们利⽤事实上的远程监控⼯具，对远程主机进⾏最少的轮询，以持续验证远程系统和正在运⾏的服务的性能、完整性和可⽤性，并且我们根据这些过程的结果采取⾏动，这没有透露任何问题。此外，我们与机构的网络管理员和
IT 领导以及上游 ISP 进行了协调，以确保我们的扫描不会对网络运营产生不利影响。

**_负责任的披露：_** 我们执⾏了系统性的协调漏洞披露 (CVD) [36] 努⼒并及时地与受影响的供应商进⾏沟通，在撰写本⽂之前⾄少 6
个⽉向他们报告漏洞，以便他们在准备安全修复时有⾜够的时间通知各⾃的⽤⼾/运营商。

**_数据隐私：_** 我们根据有关收集的数据和 IP 地址的数据保留/管理政策获得了机构审查委员会 (IRB) 的批准。具体来说，我们在分析期间保留了从
EVCMS 主机实例收集的数据，之后，为了保护数据的私密性和可靠性，我们从我们的机器中删除了在研究受影响的主机实例期间收集的所有数据。

## IV．实验结果

我们实施了 ChargePrint，并在此展⽰其发现和安全分析活动的结果。

### _A.在野外发现联网的EVCS_

**_1）初步搜索：_** 初始搜索查询使⽤选定的引擎识别出 1,800 个运⾏ 9 个不同 EVCMS 产品的主机，如图所⽰4，初始搜索使⽤
**ZoomEye** 和 Fofa 产⽣了⼤量经过验证的主机（约 1,700 个），如下所⽰：
![](https://images.seebug.org/content/images/2023/08/bcea2573-cd35-455d-b628-5a30c0d017c5.jpg-w331s)
图 4：使⽤ ChargePrint 进⾏初始和扩展搜索时发现的主机数量

与 Shodan 和 Censys（⼤约 200
个主机）相⽐。这些显着差异归因于两个主要因素。⾸先，每个引擎都采⽤不同的扫描⼯具和技术来进⾏设备发现和探测，这会在已识别的主机和横幅数据中产⽣差异，例如，Shodan
和 Censys 依赖于 ZMap 和 ZTag [37] ⽽ **ZoomEye** 和 Fofa
则依赖于他们⾃⼰的专有扫描仪。其次，每个引擎实现不同的定制查找查询，将搜索结构与存储的主机信息相关联，例如，为了优化查找并避免搜索整个数据，搜索引擎可以将给定主机与设备或系统特定的标签相关联（例如，从其横幅中提取的设备类型、操作系统）。我们注意到，所选的搜索引擎都没有定义与EVCS
相关的标签，因此，显着妨碍了初始搜索的结果。

**_2)使用ChargePrint进行扩展搜索：_** 动机是由于初始搜索中识别出的 EVCS 主机数量有限，我们利⽤ChargePrint 对
EVCMS 管理的 EVCS 主机执⾏扩展和迭代查找/查询。如图所⽰4与初始查找相⽐，我们使⽤ChargePrint
进⾏的扩展查询产⽣了明显更多的主机数量，具体来说，我们利⽤最初 9 个 EVCMS 产品的候选者来识别由各种 EVCMS 检测的总共 27,439
个唯一主机实例。通过利 ChargePrint，我们改进了使⽤所有搜索引擎的 EVCMS 查找结果，证明了其有效性，识别的主机实例数量显着增加，使⽤
**ZoomEye** ⼏乎达到了⼗倍（25,316），使⽤ Fofa（18,484）达到了⼗倍，并⽤ Shodan (5,945) 和 Censys
(5,442) 增加了⼗倍，如图4所⽰。

我们注意到，通过框架的发现和指纹识别活动的 5 次迭代，总共发现了 27,439 个 EVCMS 主机实例。此外，我们的分析表明，这些主机实例由 44
个独特的 EVCMS 产品进⾏检测，这些产品代表了在主机集群阶段获得的组数，并⼿动验证为有效的 EVCMS，如第 1
节中所述Ⅲ-A4。这凸显了ChargePrint 迭代指纹识别⽅法的重要性，该⽅法不仅扩展了对连接互联⽹的 EVCS
主机总数的了解，⽽且还发现了更⼴泛的已部署 EVCMS 产品。我们在表IV列出了 44 个已发现和分析的 EVCMS 的完整列表。
![](https://images.seebug.org/content/images/2023/08/0dd3e10c-0e5e-451a-8f8f-19914fe5e403.jpg-w331s)
表 IV：分析的易受攻击的 EVCMS 列表

**_3）地理分布：_** 确定的
EVCMS主机分布在21个国家，其中匈⽛利、芬兰、美国、法国和南⾮的主机数量明显多于其他国家（约占78%）（图5）。然⽽，这种分布并不完全符合全球部署的电动汽⻋充电器的数量[3]，美国和英国等国家应该分别拥有最多数量的
EVCS。这种偏差是由于 ChargePrint 依赖于许多初始 EVCMS
候选⽅案，这些候选⽅案可能通常部署在某些国家/地区。此外，虽然我们在每个国家/地区都确定了各种 EVCMS
产品（图5），在这些国家/地区找到的⼤多数主机仅对应于一种或两种独特的产品。例如，我们确定了超过 10,000 台部署 Ensto CSI 的主机，其中
90% 位于匈⽛利（4,900 台主机）和芬兰（4,100台主机）。

![](https://images.seebug.org/content/images/2023/08/582562b0-19a3-4c6a-9d80-8e3080853c38.jpg-w331s)
表 V：已识别的 EVCMS 漏洞概述

**_4)港口和服务：_** 我们利用已识别的 EVCMS 主机横幅，查找用于运行 EVCMS Web 界面服务的开放端口，以及查找与已知服务（如
SSH）关联的端口。如图 6 所示，大多数确定的 EVCMS 产品都在公共端口上运行 HTTP（S） 服务（例如，80，8080、和
443），但是，我们也发现了各种 EVCMS 产品（例如 81、82 和 8888）为 HTTP（S） 服务配置的替代端口。虽然开放端口提供有关已识别
EVCMS 主机上受支持服务的信息，但这些端口的某些组合可在将来的工作中用作特定于供应商的高级功能，用于某些 EVCMS 产品的目标发现和加速指纹识别。

### _B.量化EVCMS的安全状况_

对 EVCMS 产品/主机实例的深⼊安全分析发现了属于 13个常⻅弱点枚举 (CWE) 的 120 个漏洞 [38]
具有严重、⾼和中等严重程度的类别（表V），发现了 25,300 个主机实例（约占所有主机的 92%），并⽀持远程利⽤ EVCMS
并控制底层EVCS。另外，如图所⽰7，部署在 13,989 台主机上的 29 个产品与⾼和/或严重漏洞相关，⼏乎所有剩余的具有中等严重漏洞的 EVCMS
产品都部署在少量主机上（≤8)，部署在超过 10,000 台主机上的 Ensto CSI 除外。我们注意到，⼤约8% 的已验证 EVCMS
主机与任何漏洞⽆关，这是由于⽆法检查其相应的固件和⻔⼾端点来执⾏深⼊的安全和漏洞分析。接下来，我们提供了所分析的 EVCMS
产品和主机实例中已识别漏洞的详细信息和⽰例：

**_1)严重漏洞：_** 如表所列V,我们发现了 5 个严重程度的服务器端漏洞，影响了 7 个独特的 EVCMS 产品（图7），检测了 4,431 个
EVCMS 主机实例（约占 16%）。我们在 1,684 个 EVCMS 主机实例上发现了 4次
SQLi，这可以通过提取包含敏感信息（例如⽤⼾帐⼾详细信息和付款信息）表的存储数据库来充分利⽤主机。此外，我们还发现了 XXE 和 SSRF
漏洞，攻击者可以利⽤这些漏洞强制 EVCMS 向内部/外部⽹络发送任意请求，并从 EVCMS 中窃取数据。我们还发现，900 个和 1,203 个
EVCMS 主机实例分别受到硬编码凭据和 CSVi 的影响，这将允许攻击者通过直接访问资源/配置并上传持久有效负载来破坏 EVCMS。
![](https://images.seebug.org/content/images/2023/08/957d1eb4-f9d7-4a93-936d-0bc8a06d7f82.jpg-w331s)
图 5：已发现的 EVCMS 主机/实例的地理分布
![](https://images.seebug.org/content/images/2023/08/e99fbb23-1a1c-4084-90fa-3d4626bd3263.jpg-w331s)
图 6：EVCMS 端⼝在实例中的分布

**_2)高严重性漏洞：_** 我们发现 4 个⾼严重性客⼾端漏洞影响了 9,750 个主机实例（约占总数的 35%）上安装的 22 个 EVCMS
产品。XSS 漏洞将允许攻击者在易受攻击的 EVCMS 上下⽂中执⾏任意 JavaScript 代码，劫持⽤⼾帐⼾并使攻击者能够通过控制所有可⽤功能来操作
EVCS。此外，通过嵌⼊持久有效负载或通过注⼊的 Web shell 创建后⻔，可以利⽤ XSS 弱点在相应的 EVCMS
上进⾏权限升级，这些后⻔在系统⽤⼾的上下⽂中执⾏，从⽽允许攻击者通过暴露来获得对 EVCS 的管理员级别访问权限会话cookie。此外，我们还发现了
CSRF 漏洞，这将允许攻击者强迫⽬标⽤⼾执⾏意想不到的操作，例如更改 EVCS 设置和配置（例如，重新启动 EVCS）。此外，我们还发现了 CORS 和
PCDP错误配置漏洞，这些漏洞使攻击者能够通过窃取帐⼾数据和会话 cookie 来攻击 EVCMS。

**_3)中度严重漏洞：_** 我们发现了 4个中等严重性漏洞，这些漏洞影响安装在 17，831 个 EVCMS 主机实例上的 30 个 EVCMS
产品（占总数的 65%）这些漏洞可以为访问部分特权功能（例如通过强制浏览公开维护端点）打开大门，或者允许攻击者通过信息暴露漏洞查看与 EVCS
相关的机密状态和设置。此外，缺少身份验证和速率限制漏洞将允许在不确认权限的情况下访问 EVCMS 上的特定资源/功能。

### _C.攻击对电动汽车利益相关者的影响_

在 EVCS 之上的相互作⽤实体的复杂⽣态系统中，利⽤已发现的漏洞可能会导致对⼿破坏 EVCMS 及其相互通信，从⽽对利益相关者（即
EVCS、⽤⼾/运营商/电网和电⼒公司）进⾏攻击。

**电动汽车生态系统和运营:** 在协调 EVCS 环境的 EVCMS
产品环境中发现的漏洞构成了一个重⼤安全问题，因为这危及整个电动汽⻋充电⽣态系统，如图所⽰8。在正常情况下，⽤⼾/运营商能够通过EVCMS的中继操作来管理他们的EVCS，通过向其发送命令来控制底层EVCS。在简化图上（图9），我们介绍了连接主要实体的互通协议的详细信息：运营商、EVCMS
和 EVCS。如图9,互通协议可以分为4个阶段:

1) 在⾝份验证阶段，操作员通过 HTTP POST 请求向相应的登录端点提交凭据来请求访问 EVCMS，如果这些凭据有效，EVCMS
将授予操作员访问权限并将其重定向到登录墙。

2) 在管理阶段，操作员将通过发送 HTTP GET 请求来请求可⽤功能，EVCMS
将根据其权限级别向该请求提供适当的仪表板组件，之后操作员可以通过特定于端点的操作执⾏所需的各种操作HTTP GET/POST 请求。

3) 在控制阶段，EVCMS建⽴通信通道，发送并执⾏所请求的特定操作的命令（例如，开始/停⽌充电等），之后EVCS将返回状态以更新相应的EVCMS配置。

4) 在监控阶段，操作员将通过向 EVCMS 发出 HTTP GET 请求来请求 EVCS 状态概览，EVCMS 提供所需的信息，然后 EVCS
通过电⼒链路连接到电⽹（图8），可以从电⽹提取电⼒馈⼊插⼊式电动汽⻋进⾏充电，或将电⼒重新注⼊电⽹以对插⼊式电动汽⻋进⾏放电。EVCS
为电动汽⻋放电的能⼒依赖于⻋辆到电⽹ (V2G) 技术⽀持的 EVCS双向功率流功能 [39]。
![](https://images.seebug.org/content/images/2023/08/39325bb2-bd13-4b5d-81af-9b0f9c99e079.jpg-w331s)
图 7：EVCMS 产品/主机之间的漏洞分布

**针对 EVCS 的攻击:** 利⽤所讨论的漏洞的攻击者可以操纵EVCS 充电操作和时间表（即启动、延迟或停⽌充电）。许多分析的 EVCMS 都遭受了
XSS 的影响，XSS 可能允许攻击者将恶意 JavaScript 代码注入 EVCMS 的上下文并劫持运营商的帐户，从而允许通过受控 EVCS
覆盖命令来操纵和/或中断正在进行的充电操作，从而修改运营商的帐户和 EVCS
设置/配置。攻击者可能会破坏通过修改其充电水平并通过承受高电压/电流忽略关键的电池条件来连接电动汽车的电池 [40]。

此外，通过利⽤ SQLi 获得对受损 EVCMS 的⾼权限访问，攻击者可以降级 EVCS 固件并可能上传恶意制作的固件，从⽽允许对 EVCS
保持难以检测的隐蔽低级访问，从⽽在 EVCS 上创建持久性。攻击者还可以通过 SSRF 或 XXE 利⽤一组
EVCS，并将它们⽤作⽹络代理，以作为僵⼫⽹络的一部分执⾏协调的本地和/或互联⽹扫描活动。虽然这些僵⼫⽹络可⽤于通过分布式拒绝服务 (DDoS)
攻击淹没互联⽹上的其他设备，但它们也可⽤于发现其他易受攻击的⽹络设备，这些设备可能会受到损害，从⽽扩⼤攻击者的⽴⾜点并增加攻击⾯。此外，攻击者可以利用
CSRF 锁定 EVCS，禁用特定功能并拒绝合法用户的物理/虚拟访问，从而执行物理
DoS，并且此类攻击可以使用精心设计的勒索软件进行武器化，通过滥用对这些受损 EVC 的权力来获得经济利益，并锁定它们直到兑现赎金。

**针对用户/操作员的攻击:** 易受攻击的 EVCMS 实例可被⽤来获得对 EVCS 的控制并规定其与 EV
的关系，并且此类漏洞可能会暴露系统内存储的数据，从⽽危及其⽤⼾/操作员的安全和隐私。例如，通过 XSS 或 CORS/FCDP 错误配置劫持EVCMS
⽤⼾会话，攻击者可以获得运营商/⽤⼾的个⼈⾝份信息
(PII)，例如姓名、地址和电话号码，并且这些信息可能会被泄露或出售给⽹络犯罪分⼦，然后⽤于勒索、骚扰和⾝份盗窃。除了 PII
泄漏攻击之外，攻击者还可以获得EVCMS
上存储的其他资源，例如充电记录和电动汽⻋特定的⽇志数据，他们可以从中推断充电时间表并⽤于对相应的⽤⼾/运营商执⾏监视/间谍活动。另一⽅⾯，许多 EVCS
允许通过各⾃的 EVCMS 进⾏电⼦账单和⽀付，因此，这些数据也可能被攻击者从受感染的 EVCMS
主机实例中泄露，并被网络犯罪分子滥用以执行支付欺诈，通过以下方式利用诸如SQLi之类的漏洞来转储存储在EVCMS中的信息。
![](https://images.seebug.org/content/images/2023/08/442514fc-747f-4aad-92dc-c63632ecef87.jpg-w331s)
图 8：EVCMS 周围实体与⼲扰对手的相互作⽤

**针对电网的攻击:** 脆弱的电动汽⻋充电⽣态系统引⼊了针对关键基础设施的新的且快速增⻓的攻击⾯，这主要是由于EVCS
在电⽹内的直接连接和集成，并且考虑到它在为数百万客⼾提供电⼒⽅⾯发挥的重要作⽤，针对这种基础设施将产⽣重⼤影响。事实上，对电网进行大规模网络攻击会吸引各种对手，包括大型组织和国家支持的恶意行为者，他们可能会寻求经济和/或声誉损害他们的对手[41]。从本质上讲，要进行这些攻击，攻击者需要控制大量受损
EVCMS 主机实例的充电过程，以控制其底层 EVCS 并启动并发电动汽车充电会话，以及停止/延迟正在进行的充电操作，以对电网进行几次危险的频率不稳定攻击
[42]–[44]。文献提供的信息和仿真结果演示了对电网执行频率不稳定攻击的几种方法。例如，攻击者可以通过命令易受攻击的EVCS在短时间内对连接的EV进行充电和放电来制造开关攻击，短时间内造成电⽹频率扰动和连锁故障[45],[46]。此外，此类攻击可以通过对
8,300 辆电动汽⻋进⾏强制放电来执⾏，如[中的模拟分析结果所⽰]47]。考虑到使⽤我们的分析发现的易受攻击的 EVCMS 的数量（即 27,439
个），以及单个EVCMS 通常管理多个 EVCS
的事实，我们得出结论，对电⽹进⾏此类频率不稳定攻击是⾮常可⾏的。虽然在这些研究中，作者假设EVCS会受到损害，并且不讨论利用细节，但在我们的工作中，我们提出了创建受感染EVCS僵尸网络的技术细节.

### _D.建议的对策_

在这项工作中，我们强调了EVCMS中的主要安全漏洞，我们还建议采取一些缓解对策来解决当前被各自系统开发人员忽视的安全问题，并加强部署的EVCMS以抵御未来的攻击。首先，缓解所讨论的攻击需要修补EVCMS中所有已识别的漏洞类别，为此，我们参考CWE
MITRE [38]和Open Web Application Security Project [22]的文档，了解有关每个漏洞的CWE-ID的已知/推荐对策的详细信息。例如，为了防止SQLi（CWE-89），开发人员不得使用动态查询，也不能在查询执行中包含用户提供的输入，并且为了防止XSS（CWE-79），必须在响应中返回用户提供的入口点和参数数据之前正确编码和清理这些数据。其次，为了减轻针对电网的网络攻击，运营商可以监控EVCS充电计划，通过利用机器学习模型来学习正常模式并识别异常活动，以检测充电行为中的异常情况。
![](https://images.seebug.org/content/images/2023/08/37c77b48-f2f1-44aa-8c8c-6670c83a608c.jpg-w331s)
图 9：EVCMS 互通协议图

此外，为了防止 EVCS 配置和 EV 充电计划受到篡改，EVCMS和 EV 可以实现相互共识来验证两端的系统修改，因此，破坏EVCMS
的对⼿将⽆法强制执⾏⾃定义充电未经参与实体（例如，电动汽⻋运营商/⽤⼾）批准的情况下安排配置。第三，为了减少 EVCMS
攻击⾯，系统开发⼈员必须通过不断评估安全性来采⽤安全设计流程。在系统开发⽣命周期 (SDLC) 期间的可靠性，以及运营商正确、安全地设置其 EVCS
以防⽌某些攻击。例如，⽤⼾应始终使⽤强帐⼾凭据替换 EVCS 固件上附带的默认凭据，并设置弹性⾝份验证⽅法。

此外，私⼈ EVCS 运营商可以在其 EVCMS
⻔⼾上禁⽤公共设备发现，以隐藏远程互联⽹攻击者，并配置防⽕墙仅允许来⾃受信任⽅的连接。鉴于所发现的漏洞产⽣了⼴泛的影响/影响，应该依法制定和强制执⾏严格的EVCMS安全措施和设计标准，以激励系统开发商/供应商付出更多努⼒确保他们的系统经过法律的考验和必要程度的审查，以满⾜客⼾的安全期望并满⾜相应法律的要求。

## V. 零日漏洞披露和补丁后续行动

根据既定的 CVD 流程，我们通过适当的渠道、通过发送到专用产品安全事件响应团队 (PSIRT) 地址的加密电子邮件以及网站安全事件表格，将调查结果传达给
EVCMS 系统开发人员，然后再披露结果以允许他们采取必要的行动。而对于各种 EVCMS
产品，没有足够的有关相应供应商/开发商的信息，无法将调查结果传达给施耐德电气等多家制造商（例如，缺乏专用电子邮件地址、无法找到供应商网站、缺乏响应）、
Cornerstone Technologies、Bluesky Energy、Eaton 和 Etrel
已收到并承认发现的零日漏洞，并与美国国家标准与技术研究院 (NIST) [48] 协调分配了 20 多个 CVEID，例如：CVE-2021-22706（CVSS 分数：8.8/高）、CVE-2021-22722（CVSS 分数：8.9/高）、CVE-2021-22729（CVSS
分数：9.4/严重）、CVE-2021-22730（CVSS
分数：9.4/严重）此外，这些供应商还采取了措施，通过在新软件版本中部署相应的补丁来解决漏洞，特别是指定的 CVE。
![](https://images.seebug.org/content/images/2023/08/595cfefb-cdc8-4616-b5ec-0796e326999e.jpg-w331s) 表VI：EVCMS软件补丁版本发布

为了评估计划和部署的软件补丁的状态，我们对这些制造商从最初向他们报告漏洞之⽇起的 2021 年 3-6-9
个⽉内所取得的进展进⾏了跟踪。在表VI，我们展示了本次后续的结果，列出了 EVCMS 及其解决漏洞的相应软件补丁版本。 在分析的 44 个 EVCMS
中，有 18 个（40%）发布了软件更新版本来修补安全漏洞，我们列出了其中的最新版本以及相应的日期。 例如，EVlink 版本 R7（表
IV）中的漏洞经过多个阶段的修补，并于 2022 年 5 月新版本 R8 的最终发布完成，如表 VI 所示。 对于其中一些 EVCMS
产品，我们与施耐德电气和 Cornerstone Technologies 等制造商/开发商密切合作，执行连续测试并验证已部署的修复。
在大多数情况下，补丁准确地解决了问题，但是，在某些情况下，会发现先前漏洞的新变体。 例如，当特定参数上的 XSS
问题得到修补时，由于引入新的软件功能，新的/其他端点上会发现新的问题。

总而言之，基于对这些 EVCMS 软件更新进行的静态分析，已经实施了更好的防御机制，满足当前 IT 系统中部署的最新安全标准。
至于其余系统，由于各种原因尚未确认或观察到更新：（1）缺乏足够的联系信息，无法就发现的漏洞与相应的供应商/开发人员进行沟通，（2）补丁未发布 然而，(3)
由于后勤原因而缺乏软件更新，例如某些产品已停产，或 (4) 制造商将工作重点从修补当前系统漏洞转向投资新产品线。

此外，为了调查原始 EVCMS 主机实例集的更新状态，我们通过版本字符串提取探测系统并将其与当前修补的 EVCMS 版本列表进行比较，从而执行全局扫描。
我们确定，在 27,439 台主机中，6,980 台 (25.5%)仍然代表最初检测到的 EVCMS 实例，而其余 20,459 台 (74.5%)
要么是不再与 EVCMS 实例关联的动态 IP 地址，要么无法成功解析 。 我们注意到，在这 6,980 个 EVCMS 实例中，只有 1,112
个（15.9%）已相应更新到修补已发现漏洞的新软件版本。 此外，我们对一组新的 14,900 个 EVCMS
主机实例执行新一轮扫描，其中版本字符串表明仅更新了 1,760 个（11.8%）实例，因此得到了适当的保护。

在这两次扫描中，我们观察到更新的 EVCMS 实例部署了Ensto CSI 和 EVlink，并且我们强调，总体更新数量较低可归因于通⽤ EVCMS
设计架构的更新频率较低且缺乏⾃动更新功能，因此需要⼿动/技术修补，并强制要求在应⽤更新时重新启动 EVCS，这是⼤多数⽤⼾避免的操作负担。尽管如此，这些
EVCMS 实例最好不要暴露在公共互联⽹上，⽽仅连接到隔离或虚拟内部⽹络，以减少攻击⾯，并仍然保持预期的远程功能。

## VI. 经验教训和未来的工作

虽然我们识别并分析了 44 个 EVCMS，但我们注意到，由于某些 EVCMS 产品的专有性质，这些产品仅提供给充电点运营商 (CPO)
和预付费订阅的企业级客⼾，因此获取有关所有可⽤ EVCMS的信息是一项艰巨的任务。此外，某些
EVCMS的安全机制使得检查位于⾝份验证⻔⼾后⾯的内容变得不可⾏。在这些情况下，我们检查了部分 EVCMS
资产，因此剩余资产仍然可能隐藏漏洞。在未来的⼯作中，我们注意到我们利⽤了分类⽅法和提取的特征，可以更新或修改这些特征以增强整体指纹识别结果，通过实施和评估进一步的分类模型来找到每个阶段的最佳⽅法/参数。最后，我们还可以利⽤ChargePrint
和本研究的知识来构建和部署一个在线平台，⽤于对 EVCMS 产品进⾏实时发现和漏洞分析，并将这些产品提交给各个系统开发⼈员进⾏审核。

## VII. 相关工作

在这项研究中，我们通过设计一个新颖的框架，利⽤⾃定义技术来规避 EVCMS
分析特有的挑战，从⽽研究以前⽂献中从未解决过的利基攻击⾯的发现和安全⽅⾯。如表VII所⽰，我们将之前的研究⼯作系统化，将⽂献分为三类：设备指纹、EVCS安全和固件分析，同时在指纹和安全分析⽅⾯对它们进⾏⽐较。

**设备指纹识别:** 多项研究提出了发现 IoT 和 ICS 设备并对其进⾏指纹识别的⽅法。冯等⼈[8]
提出了一个引擎，通过提取应用层响应数据中的相关术语，然后将它们用作网络搜索引擎查询来查找产品描述，生成用于发现和注释物联网设备的关联规则。

![](https://images.seebug.org/content/images/2023/08/d6a1d241-2359-48aa-bd27-5480707f0923.jpg-w331s)

科斯汀等⼈[49]利⽤监督机器学习对嵌⼊式设备固件数据库进⾏分类，然后对在线 Web 界⾯进⾏指纹识别，将它们链接到数据库中的相应图像。佐佐⽊等⼈[14]
提出了一种专⻔⽤于发现 ICS 远程管理设备的指纹识别⽅法，⽅法是选择可能存在 ICS 的⽹络并从中收集 WebUI，然后从基于 WebUI
检测到的远程管理系统中识别并创建签名，其中包含受监控设施的名称和位置的⾃定义字段。作者进⾏了⽐较并指出，他们的结果超过了识别 ICS（例如
Shodan）的⾏业来源的结果，尽管如此，这些设备中的很⼤一部分已经被搜索引擎标记为 ICS。尽管如此，我们注意到，与 ICS 不同的是，ICS 已经拥有由
Shodan和 Censys 等设备搜索引擎提供的记录完善的内置标签，但⼈们对 EVCMS 缺乏了解，也缺乏⽤于识别它们的内置标签。

王等⼈从不同的⻆度来看
[9]提出了一种识别物联⽹设备的引擎，通过从响应数据中提取结构和⻛格特征，利⽤同一供应商或产品的物联⽹设备之间响应数据的最⾼相似性。于等⼈[50]提出了一种固件识别⽅法，通过分析⽹⻚内容来提取信息，同时使⽤分类和⻚⾯分割来识别设备型号和固件版本。与其他设备类型相⽐，EVCS
具有有限且重要的横幅，因为很难找到与其相关的信息和规范，特别是因为⼤多数EVCMS
产品都是基于云的且闭源的，此外还缺乏针对这些设备的横幅规则。识别他们。此外，EVCMS
的开发⼈员之间的多样性和缺乏标准化导致了⼴泛的横幅表⽰形式，这些表⽰形式更难分析和跟踪，使得使⽤现有⽅法来指纹 EVCS
变得不可⾏，因此，我们设计了我们的⽅法，从初步开始使⽤ EVCMS 种⼦进⾏引导搜索。

**EVCS 安全:** 先前的研究着眼于 EVCS 安全性的不同⽅⾯，然⽽，EVCS 固件和 EVCMS 安全性很少受到学术关注。阿尔卡拉斯等⼈[6]
对开放充电点协议 (OCPP) 进⾏了安全分析，提出了允许中间⼈攻击⼲扰 EV 资源预留的弱点，并提出了防范其提议的攻击的对策 [51]。鲍伊等⼈[52]
对⻋辆到电⽹协议进⾏了安全分析，提出了针对充电过程的攻击。⻉克等⼈[7] 实施了一种⽆线窃听⼯具来进⾏电磁旁道攻击，以从EVCS
电⼒线通信⽹络恢复消息。普拉特等⼈[53] 制定了安全原则，以防⽌针对 EVCS 和电⽹的⽹络攻击。安图恩等⼈[54] 和 Gottumukkala
等⼈[55] 提出了与电动汽⻋充电⽣态系统组件相关的⽹络威胁的理论概述。弗莱吉等⼈[56] 调查了电动⻋互联⽹ (IoEV)
的安全性，指出可⽤于破坏其运⾏的⽹络攻击。穆萨维安等⼈[57] 提出了一种模型，可优化 EV 基础设施内的安全⻛险，以处理通过 EVCS
通信⽹络的恶意软件传播攻击。

我们注意到，这些⼯作依赖于理论攻击场景，其中假设EVCS 被恶意软件感染，⽽不讨论利⽤过程。据我们所知，我们的工作首次对 EVCMS
产品进行了深入的安全分析，同时提出了一系列允许对 EVCS 进行实际远程利用和操纵的漏洞，从而揭示了大规模的漏洞。
规模化电动汽车生态系统的不安全性，同时警告供应商立即实施缓解措施。

**系统分析:** 之前的一些研究检查了物联⽹和⼯业控制系统设备固件的安全性。科斯汀等⼈[20]
利⽤安全⼯具和静态分析技术进⾏了⼤规模物联⽹固件分析。佐佐⽊等⼈[14] 通过检查不安全的配置、调查未修补的已知漏洞以及利⽤现有扫描仪（例如
Nmap、OpenVAS）执⾏渗透测试来查找零⽇漏洞，对 ICS 远程管理系统进⾏了安全分析。虽然 ICS
主题之前已被研究过，并且有更⼴泛的⽂献讨论其安全性，但很难利⽤现成的⼯具对具有深层代码路径（如
EVCMS）的产品执⾏安全分析。因此，我们依靠量⾝定制的特定安全分析程序，利⽤静态分析/动态指标来检测 EVCMS 中的漏洞。郑等⼈[21]
提出了一种物联⽹固件模糊器，通过⽤⼾和系统模式模拟来发现 1 天漏洞。斯⾥⽡斯塔⽡等⼈[58] 为基于Linux
的固件构建了一个仿真和动态分析框架，该框架采⽤模糊测试和静态分析技术来发现软件错误。赖特等⼈[59]
对固件重新托管领域的流⾏作品进⾏了分类，并提出了系统仿真和分析过程中⾯临的常⻅挑战。陈等⼈[60] 提出了一种⾃动化系统
(Firmadyne)，该系统通过完整的系统仿真对嵌⼊式设备固件进⾏动态分析。

我们在收集的 EVCMS 固件映像上测试了 Firmadyne，试图观察分析结果，但是，由于它⽆法分析 EPK 等专有⽂件压缩，因此它⽆法运⾏许多提供的
EVCMS 固件。尽管如此，我们在 ChargePrint 的设计中融⼊了 Firmadyne
引⼊的一些分析技术，例如与⽂件系统提取⽅法相关的技术。法萨诺等⼈[61] 提出重新托管作为固件仿真的替代⽅案，⽤于硬件系统的动态分析。虽然这些研究在分析
IoT 固件⽅⾯很有效，但⼤多数⽅法都依赖于已知的 CVE
漏洞和安全扫描程序，因此除了误报率较⾼之外，⽆法发现新的漏洞。⼤多数这些研究也仅对固件包进⾏分析，⽽我们对可⽤固件和在线端点进⾏分析，⽽⽆需访问底层固件。此外，⼤多数这些研究依赖动态分析技术来检查嵌⼊式设备图像，但由于硬件限制和与
QEMU 等仿真软件不兼容的专有固件，这在分析EVCMS 图像时实际上是不可⾏的[62]。

## VIII. 结论

我们通过评估 EVCMS 作为新攻击⾯的安全状况，⾸次尝试探索与 EVCS 相关的威胁。我们提出了一种新颖的发现和安全分析框架
(ChargePrint)，可以在分析其漏洞的同时对野外 EVCMS 实例进⾏指纹识别。此外，我们利用 ChargePrint 识别实现44 种不同
EVCMS 的 27,439 台主机，扩展现有搜索引擎的设备发现/指纹识别功能。此外，我们的深⼊分析发现了 120 个 0day
漏洞，这些漏洞可能导致⼤多数 (92%) EVCMS 主机被远程利⽤，从⽽引起了⼈们对⼤规模实施的EVCMS
不安全性的严重担忧。最后，虽然我们注意到对电动汽⻋充电⽣态系统中各个利益相关者的攻击影响，但我们将我们的发现传达给各⾃的系统开发⼈员，以激励他们提⾼EVCMS
和整个电动汽⻋充电⽣态系统的安全性。

## 致谢

我们感谢审稿⼈的时间和宝贵的反馈。这项⼯作得到了加拿⼤⾃然科学与⼯程研究委员会（NSERC）和康考迪亚⼤学的⽀持。这项⼯作还得到了美国国家科学基⾦会
(NSF)、⾼级⽹络基础设施办公室 (OAC) #1907821 和#2104273

## 参考⽂献

[1] Hydro-Quebec, “Electric Vehicle Charging Stations: Technical Installation
Guide,” https://www.hydroquebec.com/data/ electrification-transport/pdf/technical-guide.pdf, 2015.

[2] Gouvernement du Qu´ebec, “New Electric Vehicle Rebate,”
https://vehiculeselectriques.gouv.qc.ca/english/rabais/ve-neuf/ programme-rabais-vehicule-neuf.asp, 2020.

[3] International Energy Agency, “Global EV Outlook 2021,”
https://www.iea.org/reports/global-ev-outlook-2021, Jun. 2020.

[4] F. Lambert, “Electric car charge points soar to 7.3 million chargers, 60%
growth in public chargers,” https://electrek.co/2020/06/15/ electric-car-charge-points-data, Electrek, Jun 2020.

[5] D. Shelar et al., “Compromising Security of Economic Dispatch in Power
System Operations,” in Proc. of the 47th Annual IEEE/IFIP Int. Conf. on
Dependable Systems and Networks (DSN), 2017, pp. 531–542.

[6] C. Alcaraz, J. Lopez, and S. Wolthusen, “OCPP Protocol: Security Threats
and Challenges,” IEEE Transactions on Smart Grid, vol. 8, no. 5, pp.
2452–2459, 2017.

[7] R. Baker and I. Martinovic, “Losing the car keys: Wireless PHYLayer
insecurity in EV charging,” in 28th USENIX Security Symposium (USENIX Security
19). Santa Clara, CA: USENIX Association, Aug.2019, pp. 407–424.

[8] X. Feng et al., “Acquisitional rule-based engine for discovering
Internetof-Things devices,” in 27th USENIX Security Symposium (USENIX Security
18). Baltimore, MD: USENIX Association, Aug. 2018, pp. 327–341.

[9] X. Wang et al., “Iottracker: An enhanced engine for discovering internet-of-thing devices,” in 2019 IEEE 20th International Symposium on” A World of
Wireless, Mobile and Multimedia Networks”(WoWMoM). IEEE, 2019, pp. 1–9.

[10] National Vulnerability Database, “Common Vulnerabilities and Exposures
(CVE),” https://cve.mitre.org, 2021.

[11] Office of Energy Efficiency & Renewable Energy, “Vehicle Charging,”
https://www.energy.gov/eere/electricvehicles/vehicle-charging, 2020.

[12] J. Tournier et al., “A survey of iot protocols and their security issues
through the lens of a generic iot stack,” Internet of Things, vol. 16,
p.100264, 2021.

[13] OCPP, “OCPP 2.0 Part 2: Specification. Technical Report,” 2018.

[14] T. Sasaki et al., “Exposed infrastructures: Discovery, attacks and
remediation of insecure ics remote management devices,” in 2022 IEEE Symposium
on Security and Privacy (SP). IEEE, 2022, pp. 2379–2396.

[15] B. Zhao et al., “A large-scale empirical study on thevulnerability of
deployed iot devices,” IEEE Transactions on Dependable and Secure Computing,
2020.

[16] Shodan, “The search engine for Internet-connected devices.”
https://www.shodan.io, Shodan, 2021.

[17] Censys, “A search engine based on Internet-wide scanning for the devices
and networks.” https://censys.io, Censys, 2021.

[18] Zoomeye, “ZoomEye - Cyberspace Search Engine,” https://www.zoomeye.org,
Zoomeye, 2021.

[19] Fofa, “Fofa,” https://fofa.so, Fofa, 2021.

[20] A. Costin et al., “A Large-Scale analysis of the security of embedded
firmwares,” in 23rd USENIX Security Symposium (USENIX Security 14). San Diego,
CA: USENIX Association, Aug. 2014, pp. 95–110.

[21] Y. Zheng et al., “FIRM-AFL: High-Throughput greybox fuzzing of IoT
firmware via augmented process emulation,” in 28th USENIX Security Symposium
(USENIX Security 19). Santa Clara, CA: USENIX Association, Aug. 2019, pp.
1099–1114.

[22] OWASP, “OWASP Foundation — Open Source Foundation for Application
Security,” https://owasp.org, 2021.

[23] MITRE, “2021 CWE Top 25 Most Dangerous Software
Weaknesses,”https://cwe.mitre.org/top25/archive/2021/2021 cwe top25.html,
2021.

[24] Zyte, “Scrapy — A Fast and Powerful Scraping and Web Crawling Framework,”
https://scrapy.org, Scrapy, 2021.

[25] R. Labs, “Binwalk: Nb 1 Firmware extraction tool in the world.”
https://www.refirmlabs.com/binwalk, Refirm Labs, 2021.

[26] J. W. Ratcliff and D. E. Metzener, “Pattern-matching-the gestalt
approach,” Dr Dobbs Journal, vol. 13, no. 7, p. 46, 1988.

[27] rizin.re, “Cutter,” https://cutter.re, rizin.re, 2021.

[28] PortSwigger, “Burp Suite - Application Security Testing Software -PortSwigger),” https://portswigger.net/burp, 2021.

[29] B. Damele and M. Stampar, “sqlmap: automatic SQL injection and database
takeover tool,” http://sqlmap.org, 2021.

[30] O. Alrawi et al., “The betrayal at cloud city: An empirical analysis of
Cloud-Based mobile backends,” in 28th USENIX Security Symposium (USENIX
Security 19). Santa Clara, CA: USENIX Association, Aug. 2019, pp. 551–566.

[31] S. Schrittwieser, M. Mulazzani, and E. Weippl, “Ethics in security
research which lines should not be crossed?” in 2013 IEEE Security and Privacy
Workshops. IEEE, 2013, pp. 1–4.

[32] J. Dittmer, “Minimizing Legal Risk When Using Cybersecurity Scanning
Tools.” https://www.sans.org/white-papers/37522/, SANS, Jan.2017.

[33] Z. Durumeric, E. Wustrow, and J. A. Halderman, “ZMap: Fast internetwide
scanning and its security applications,” in 22nd USENIX Security Symposium
(USENIX Security 13). Washington, D.C.: USENIX Association, Aug. 2013, pp.
605–620.

[34] F. Li et al., “You’ve got vulnerability: Exploring effective
vulnerability notifications,” in 25th USENIX Security Symposium (USENIX
Security 16). Austin, TX: USENIX Association, Aug. 2016, pp. 1033–1050.

[35] T. Ristenpart et al., “Hey, you, get off of my cloud: exploring
information leakage in third-party compute clouds,” in Proceedings of the 16th
ACM conference on Computer and communications security, 2009, pp. 199–212.

[36] Organisation for Economic Co-operation and Development (OECD),
“ENCOURAGING VULNERABILITY TREATMENT,” Online at
https://one.oecd.org/document/DSTI/CDEP/SDE(2020)3/FINAL/en/ pdf, 2021.

[37] The ZMap Project, “The ZMap Project,” https://zmap.io, The ZMap Project,
2021.

[38] MITRE, “Common Weakness Enumeration (CWE),” https://cwe.mitre. org, 2021.

[39] Z. Zhou et al., “Secure and efficient vehicle-to-grid energy trading in
cyber physical systems: Integration of blockchain and edge computing,” IEEE
Transactions on Systems, Man, and Cybernetics: Systems, vol. 50, no. 1, pp.
43–57, 2020.

[40] F. Sagstetter et al., “Security challenges in automotive
hardware/software architecture design,” in 2013 Design, Automation Test in
Europe Conference Exhibition (DATE), 2013, pp. 458–463.

[41] G. Liang et al., “The 2015 ukraine blackout: Implications for false data
injection attacks,” IEEE Transactions on Power Systems, vol. 32, no. 4, pp.
3317–3318, 2016.

[42] S. Soltan, P. Mittal, and H. V. Poor, “BlackIoT: IoT botnet of high
wattage devices can disrupt the power grid,” in 27th USENIX Security Symposium
(USENIX Security 18). Baltimore, MD: USENIX Association, Aug. 2018, pp. 15–32.

[43] S. Acharya, Y. Dvorkin, and R. Karri, “Public Plug-in Electric Vehicles +
Grid Data: Is a New Cyberattack Vector Viable?” IEEE Transactions on Smart
Grid, pp. 1–1, 2020.

[44] O. Erdinc et al., “Smart household operation considering bi-directional
ev and ess utilization by real-time pricing-based dr,” IEEE Transactions on
Smart Grid, vol. 6, no. 3, pp. 1281–1291, 2014.

[45] A. K. Farraj and D. Kundur, “On Using Energy Storage Systems in Switching
Attacks that Destabilize Smart Grid Systems,” in Proc. of the IEEE Power &
Energy Society Innovative Smart Grid Technologies Conference (ISGT), 2015, pp.
1–5.

[46] L. Shan et al., “A Coordinated Multi-Switch Attack for Cascading Failures
in Smart Grid,” IEEE Transactions on Smart Grid, vol. 5, no. 3, pp. 1183–1195,
2014.

[47] M. A. Sayed et al., “Electric vehicle attack impact on power grid
operation,” International Journal of Electrical Power & Energy Systems, p.
107784, 2021.

[48] National Institute of Standards and Technology (NIST), “National
Institute of Standards and Technology — NIST,” https://www.nist.gov, 2021.

[49] A. Costin, A. Zarras, and A. Francillon, “Towards automated
classification of firmware images and identification of embedded devices,” in
IFIP International Conference on ICT Systems Security and Privacy Protection.
Springer, 2017, pp. 233–247.

[50] D. Yu et al., “Large-scale iot devices firmware identification based on
weak password,” IEEE Access, vol. 8, pp. 7981–7992, 2020.

[51] J. E. Rubio, C. Alcaraz, and J. Lopez, “Addressing Security in OCPP:
Protection Against Man-in-the-Middle Attacks,” in 2018 9th IFIP International
Conference on New Technologies, Mobility and Security (NTMS), Paris, France,
2018, pp. 1–5.

[52] K. Bao et al., “A Threat Analysis of the Vehicle-to-Grid Charging
Protocol ISO 15118,” Computer Science-Research and Development, vol. 33, no.
1-2, pp. 3–12, 2018.

[53] R. M. Pratt and T. E. Carroll, “Vehicle Charging Infrastructure
Security,” in 2019 IEEE International Conference on Consumer Electronics
(ICCE), Las Vegas, NV, USA, 2019, pp. 1–5.

[54] J. Antoun et al., “A Detailed Security Assessment of the EV Charging
Ecosystem,” IEEE Network, vol. 34, no. 3, pp. 200–207, 2020.

[55] R. Gottumukkala et al., “Cyber-physical System Security of Vehicle
Charging Stations,” in 2019 IEEE Green Technologies Conference (GreenTech),
Lafayette, LA, USA, 2019, pp. 1–5.

[56] Y. Fraiji et al., “Cyber Security Issues of Internet of Electric
Vehicles,” in 2018 IEEE Wireless Communications and Networking Conference
(WCNC), Barcelona, Spain, 2018, pp. 1–6.

[57] S. Mousavian et al., “A risk-based optimization model for electric
vehicle infrastructure response to cyber attacks,” IEEE Transactions on Smart
Grid, vol. 9, no. 6, pp. 6160–6169, 2018.

[58] P. Srivastava et al., “Firmfuzz: Automated iot firmware introspection and
analysis,” in Proceedings of the 2nd International ACM Workshop on Security
and Privacy for the Internet-of-Things, 2019, pp. 15–21.

[59] C. Wright et al., “Challenges in firmware re-hosting, emulation, and
analysis,” ACM Computing Surveys (CSUR), vol. 54, no. 1, pp. 1–36, 2021.

[60] D. D. Chen et al., “Towards automated dynamic analysis for linux-based
embedded firmware.” in NDSS, vol. 1, 2016, pp. 1–1.

[61] A. Fasano et al., “Sok: Enabling security analyses of embedded systems
via rehosting,” in Proceedings of the 2021 ACM Asia Conference on Computer and
Communications Security, 2021, pp. 687–701.

[62] Software Freedom Conservancy, “QEMU: A generic and open source machine
emulator and virtualizer.” https://www.qemu.org/, QEMU, 2021.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2096/>

