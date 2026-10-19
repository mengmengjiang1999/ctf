结构化威胁信息表达 (STIX, Structured Threat Information Expression) 是一种用于交换 网络威胁情报
(CTI，Cyber Threat Intelligence) 的语言和序列化格式。STIX 可以使组织能 够以一致且机器可读的方式与另一方共享
CTI，从而使安全社区能够更好地了解他们最有 可能受到的计算机的攻击，并更快、更有效地预测和/或响应这些攻击。STIX旨在提升诸
多不同的能力，比如协同威胁分析、自动化威胁信息交换、自动检测和响应等。

近期对 STIX v2.1 进行了翻译和整理分享出来，欢迎大家提出宝贵意见。

下载地址: http://uuqaq.com/stix-v2.1-zh-ch.pdf

反馈邮箱: [tianzeep@outlook.com ](mailto:tianzeep@outlook.com)  

  

  

原版发布:

|

2021年6月10日

| |

译者信息:

|

WXZ, 2023 于云境实验室  
  
---|---|---|---|---  
  
版本日期:

|

2023年5月17日

| |

反馈邮箱:

|

tianzeep@outlook.com  
  
下载地址

|

 _http://uuqaq.com/stix-v2.1-zh-ch.pdf_  
  
STIX Version 2.1

OASIS 标准

本阶段:

<https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.docx>(权威发布)

<https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html>  

<https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.pdf>  

上一阶段:

<https://docs.oasis-open.org/cti/stix/v2.1/cs02/stix-v2.1-cs02.docx>(权威发布)

<https://docs.oasis-open.org/cti/stix/v2.1/cs02/stix-v2.1-cs02.html>  

<https://docs.oasis-open.org/cti/stix/v2.1/cs02/stix-v2.1-cs02.pdf>  

最新阶段:

<https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.docx>(权威发布)

<https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.html>  

<https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.pdf>  

技术委员会:

[OASIS Cyber Threat Intelligence (CTI) TC](https://www.oasis-open.org/committees/cti/)  

主席:

Richard Struse ([rjs@mitre.org](mailto:rjs@mitre.org)), [MITRE
Corporation](http://www.mitre.org/)  

Trey Darley ([trey.darley@cert.be](mailto:trey.darley@cert.be)),
[CCB/CERT.be](https://cert.be/)  

编辑:

Bret Jordan ([bret.jordan@broadcom.com](mailto:bret.jordan@broadcom.com)),
[Broadcom](http://www.broadcom.com/)  

Rich Piazza ([rpiazza@mitre.org](mailto:rpiazza@mitre.org)), [MITRE
Corporation](http://www.mitre.org/)  

Trey Darley ([trey.darley@cert.be](mailto:trey.darley@cert.be)),
[CCB/CERT.be](https://cert.be/)  

相关作品:

本规范替代或取代:

  * STIX 2.0版本. Part 1: STIX Core Concepts. Edited by Rich Piazza, John Wunder, and Bret Jordan. Latest stage:[](http://docs.oasis-open.org/cti/stix/v1.2.1/stix-v1.2.1-part1-overview.html)<http://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part1-stix-core.html>.
  * STIX 2.0版本. Part 2: STIX Objects. Edited by Rich Piazza, John Wunder, and Bret Jordan. Latest stage: <http://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part2-stix-objects.html>.
  * STIX 2.0版本. Part 3: Cyber Observable Core Concepts. Edited by IvanKirillov and Trey Darley. Latest stage:<http://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part3-cyber-observable-core.html>.
  * STIX 2.0版本. Part 4: Cyber Observable Objects. Edited by Ivan Kirillov and Trey Darley. Latest stage: <http://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part4-cyber-observable-objects.html>.
  * STIX 2.0版本. Part 5: STIX Patterning. Edited by Ivan Kirillov and Trey Darley. Latest stage: <http://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part5-stix-patterning.html>.

本规范所关联文件:

  * TAXII 2.1版本. Edited by Bret Jordan and Drew Varner. Latest stage: <https://docs.oasis-open.org/cti/taxii/v2.1/taxii-v2.1.html>.
  * STIX/TAXII 2.0 Interoperability Test Document: Part 1 Version 1.1. Edited by Allan Thomson and Jason Keirstead. Latest stage: <https://docs.oasis-open.org/cti/stix-taxii-2-interop-p1/v1.1/stix-taxii-2-interop-p1-v1.1.html>.
  * STIX/TAXII 2.0 Interoperability Test Document: Part 2 Version 1.0. Edited by Allan Thomson and Jason Keirstead. Latest stage: <https://docs.oasis-open.org/cti/stix-taxii-2-interop-p2/v1.0/stix-taxii-2-interop-p2-v1.0.html>.

摘要:

结构化威胁信息表达(STIX)是一种用于表达“网络威胁”和“可观测信息”的语言。该文件定义了适用于整个STIX的概念，并定义了STIX语言的整体结构。

状态:

OASIS会员在上述日期对本文件进行了最后一次修订或审批，其上还列出了批准的级别。查看上述“Latest
stage”部分，了解本文档在后续可能发生的变化。由技术委员会(TC)所制作且已赋予编号的版本和其他技术作品均在此列表中，详见<https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=cti#technical>。

技术委员会成员可以将对本文件的意见发送至技术委员会的电子邮件列表。其他人可以在技术委员会网站<https://www.oasis-open.org/committees/cti/>按照 "<https://www.oasis-open.org/committees/comments/index.php?wg_abbrev=cti>"
按钮的指引订阅后，将对本文件的意见发送至技术委员会所公开的公众意见列表。

该规范在[OASIS IPR 政策](https://www.oasis-open.org/policies-guidelines/ipr/)下以[Non-Assertion](https://www.oasis-open.org/policies-guidelines/ipr/#Non-Assertion-Mode)模式提供，该模式在技术委员会成立时选定。对实施本规范必要的任何专利信息，以及任何专利许可条款的信息是否已公开，请参阅TC网页(<https://www.oasis-open.org/committees/cti/ipr.php>)的“Intellectual Property Rights section”部分。

请注意，本规范中声明的任何标准化的机器可读内容（计算机语言定义），均在单独的纯文本文件中提供。如果文中展示内容与单独的纯文本文件不符，则以单独的纯文本文件中的内容为准。

关键字:

关键字 " **MUST** ", " **MUST NOT** ", " **REQUIRED** ", " **SHALL** ", " **SHALL
NOT** ", " **SHOULD** ", " **SHOULD NOT** ", " **RECOMMENDED** ", " **NOT
RECOMMENDED** ", " **MAY** ", 和" **OPTIONAL** " 在此文件中应按照BCP 14 [RFC2119]
[RFC8174] 进行描述；只有当它们以全部大写形式出现时，则如此处所示。

引用格式:

当引用本规范时，应使用以下引用格式:

 **[STIX-v2.1]**

STIX Version 2.1. Edited by Bret Jordan, Rich Piazza, and Trey Darley. 10 June
2021. OASIS Standard. <https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html>. Latest stage:
<https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.html>.

 **注意事项** **:**

Copyright © OASIS Open 2022. All Rights Reserved.

All capitalized terms in the following text have the meanings assigned to them
in the OASIS Intellectual Property Rights Policy (the "OASIS IPR Policy"). The
full [Policy](https://www.oasis-open.org/policies-guidelines/ipr)may be found
at the OASIS website.

This document and translations of it may be copied and furnished to others,
and derivative works that comment on or otherwise explain it or assist in its
implementation may be prepared, copied, published, and distributed, in whole
or in part, without restriction of any kind, provided that the above copyright
notice and this section are included on all such copies and derivative works.
However, this document itself may not be modified in any way, including by
removing the copyright notice or references to OASIS, except as needed for the
purpose of developing any document or deliverable produced by an OASIS
Technical Committee (in which case the rules applicable to copyrights, as set
forth in the OASIS IPR Policy, must be followed) or as required to translate
it into languages other than English.

The limited permissions granted above are perpetual and will not be revoked by
OASIS or its successors or assigns.

This document and the information contained herein is provided on an "AS IS"
basis and OASIS DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT
INFRINGE ANY OWNERSHIP RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR
FITNESS FOR A PARTICULAR PURPOSE.

OASIS requests that any OASIS Party or any other party that believes it has
patent claims that would necessarily be infringed by implementations of this
OASIS Committee Specification or OASIS Standard, to notify OASIS TC
Administrator and provide an indication of its willingness to grant patent
licenses to such patent claims in a manner consistent with the IPR Mode of the
OASIS Technical Committee that produced this specification.

OASIS invites any party to contact the OASIS TC Administrator if it is aware
of a claim of ownership of any patent claims that would necessarily be
infringed by implementations of this specification by a patent holder that is
not willing to provide a license to such patent claims in a manner consistent
with the IPR Mode of the OASIS Technical Committee that produced this
specification. OASIS may include such claims on its website, but disclaims any
obligation to do so.

OASIS takes no position regarding the validity or scope of any intellectual
property or other rights that might be claimed to pertain to the
implementation or use of the technology described in this document or the
extent to which any license under such rights might or might not be available;
neither does it represent that it has made any effort to identify any such
rights. Information on OASIS' procedures with respect to rights in any
document or deliverable produced by an OASIS Technical Committee can be found
on the OASIS website. Copies of claims of rights made available for
publication and any assurances of licenses to be made available, or the result
of an attempt made to obtain a general license or permission for the use of
such proprietary rights by implementers or users of this OASIS Committee
Specification or OASIS Standard, can be obtained from the OASIS TC
Administrator. OASIS makes no representation that any information or list of
intellectual property rights will at any time be complete, or that any claims
in such list are, in fact, Essential Claims.

The name "OASIS" is a trademark of [OASIS](https://www.oasis-open.org/), the
owner and developer of this specification, and should be used only to refer to
the organization and its official outputs. OASIS welcomes reference to, and
implementation and use of, specifications, while reserving the right to
enforce its marks against misleading uses. Please see <https://www.oasis-open.org/policies-guidelines/trademark/>for above guidance.

Portions copyright © United States Government 2012-2022. All Rights Reserved.

STIX, CYBOX, AND TAXII (STANDARD OR STANDARDS) AND THEIR COMPONENT PARTS ARE
PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND, EITHER EXPRESSED, IMPLIED,
OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTY THAT THESE STANDARDS
OR ANY OF THEIR COMPONENT PARTS WILL CONFORM TO SPECIFICATIONS, ANY IMPLIED
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR FREEDOM
FROM INFRINGEMENT, ANY WARRANTY THAT THE STANDARDS OR THEIR COMPONENT PARTS
WILL BE ERROR FREE, OR ANY WARRANTY THAT THE DOCUMENTATION, IF PROVIDED, WILL
CONFORM TO THE STANDARDS OR THEIR COMPONENT PARTS. IN NO EVENT SHALL THE
UNITED STATES GOVERNMENT OR ITS CONTRACTORS OR SUBCONTRACTORS BE LIABLE FOR
ANY DAMAGES, INCLUDING, BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR
CONSEQUENTIAL DAMAGES, ARISING OUT OF, RESULTING FROM, OR IN ANY WAY CONNECTED
WITH THESE STANDARDS OR THEIR COMPONENT PARTS OR ANY PROVIDED DOCUMENTATION,
WHETHER OR NOT BASED UPON WARRANTY, CONTRACT, TORT, OR OTHERWISE, WHETHER OR
NOT INJURY WAS SUSTAINED BY PERSONS OR PROPERTY OR OTHERWISE, AND WHETHER OR
NOT LOSS WAS SUSTAINED FROM, OR AROSE OUT OF THE RESULTS OF, OR USE OF, THE
STANDARDS, THEIR COMPONENT PARTS, AND ANY PROVIDED DOCUMENTATION. THE UNITED
STATES GOVERNMENT DISCLAIMS ALL WARRANTIES AND LIABILITIES REGARDING THE
STANDARDS OR THEIR COMPONENT PARTS ATTRIBUTABLE TO ANY THIRD PARTY, IF PRESENT
IN THE STANDARDS OR THEIR COMPONENT PARTS AND DISTRIBUTES IT OR THEM "AS IS."

  1. 介绍 ——Introduction. 1  

1.1. 文件约定 ——Document Conventions. 1  

1.2. 概述 ——Overview. 2  

1.3. 对早期版本的变更 ——Changes From Earlier Versions. 7  

1.4. 术语 ——Glossary. 7  

  2. 通用数据类型 ——Common Data Types. 9  

2.1. 二进制 ——Binary. 10  

2.2. 布尔 ——Boolean. 10  

2.3. 字典 ——Dictionary. 10  

2.4. 枚举 ——Enum.. 11  

2.5. 外部引用 ——External Reference. 11  

2.6. 浮点数 ——Float 13  

2.7. 哈希值 ——Hashes. 14  

2.8. 十六进制 ——Hexadecimal 14  

2.9. 标识符 ——Identifier 14  

2.10. 整数 ——Integer 17  

2.11. 杀伤链阶段 ——Kill Chain Phase. 17  

2.12. 列表 ——List 18  

2.13. 可观测容器(已过时) ——Observable Container (deprecated) 19  

2.14. 开放词汇 ——Open Vocabulary. 20  

2.15. 字符串 ——String. 21  

2.16. 时间戳 ——Timestamp. 21  

  3. STIX 一般概念 ——STIX General Concepts. 22  

3.1. 属性名称和字符串字面量 ——Property Names and String Literals. 22  

3.2. 通用属性 ——Common Properties. 22  

3.3. 对象 ID 和引用 ——Object IDs and References. 27  

3.4. SCO确定性ID创建 ——SCO Deterministic ID Creation. 28  

3.5. 对象创建 ——Object Creator 28  

3.6. 版本控制 ——Versioning. 28  

3.7. 通用关系 ——Common Relationships. 34  

3.8. 保留名称 ——Reserved Names. 35  

3.9. 对象属性元数据 ——Object Property Metadata. 35  

3.10. 预定义对象扩展 ——Predefined Object Extensions. 36  

  4. STIX域对象 ——STIX Domain Objects. 37  

4.1. 攻击模式 ——Attack Pattern. 37  

4.2. 攻击事件 ——Campaign. 41  

4.3. 处置建议 ——Course of Action. 45  

4.4. 编组 ——Grouping. 47  

4.5. 身份 ——Identity. 50  

4.6. 安全事件 ——Incident 52  

4.7. 威胁指标 ——Indicator 54  

4.8. 基础设施 ——Infrastructure. 59  

4.9. 入侵集 ——Intrusion Set 64  

4.10. 地理位置 ——Location. 69  

4.11. 恶意代码 ——Malware. 74  

4.12. 恶意代码分析结果 ——Malware Analysis. 81  

4.13. 批注信息 ——Note. 86  

4.14. 可观测数据 ——Observed Data. 88  

4.15. 专家见解 ——Opinion. 92  

4.16. 报告 ——Report 94  

4.17. 威胁源 ——Threat Actor 98  

4.18. 工具软件 ——Tool 104  

4.19. 脆弱性 ——Vulnerability. 107  

  5. STIX关系对象 ——STIX Relationship Objects. 110  

5.1. Relationship. 110  

5.2. Sighting. 112  

  6. STIX网络可观测对象 ——STIX Cyber-observable Objects. 118  

6.1. Artifact Object 118  

6.2. Autonomous System (AS) Object 120  

6.3. Directory Object 121  

6.4. Domain Name Object 122  

6.5. Email Address Object 124  

6.6. Email Message Object 125  

6.7. File Object 131  

6.8. IPv4 Address Object 145  

6.9. IPv6 Address Object 147  

6.10. MAC Address Object 148  

6.11. Mutex Object 149  

6.12. Network Traffic Object 150  

6.13. Process Object 162  

6.14. Software Object 168  

6.15. URL Object 169  

6.16. User Account Object 170  

6.17. Windows™ Registry Key Object 173  

6.18. X.509 Certificate Object 176  

  7. STIX元对象 ——STIX Meta Objects. 181  

7.1. Language Content 181  

7.2. Data Markings. 184  

7.3. Extension Definition. 192  

  8. STIX包对象 ——STIX Bundle Object 200  

8.1. Properties. 200  

8.2. Relationships. 200  

  9. STIX 匹配模式 ——STIX Patterning. 202  

9.1. Definitions. 202  

9.2. Constants. 204  

9.3. STIX Patterns. 206  

9.4. Pattern Expressions. 207  

9.5. Observation Expressions. 207  

9.6. Comparison Expressions. 211  

9.7. Object Path Syntax. 215  

9.8. Examples. 217  

  10. STIX 词汇表 ——STIX Vocabularies. 220  

10.1. Account Type Vocabulary. 220  

10.2. Attack Motivation Vocabulary. 221  

10.3. Attack Resource Level Vocabulary. 223  

10.4. Encryption Algorithm Enumeration. 224  

10.5. Extension Types Enumeration. 224  

10.6. Grouping Context Vocabulary. 225  

10.7. Hashing Algorithm Vocabulary. 225  

10.8. Identity Class Vocabulary. 227  

10.9. Implementation Language Vocabulary. 227  

10.10. Indicator Type Vocabulary. 228  

10.11. Industry Sector Vocabulary. 229  

10.12. Infrastructure Type Vocabulary. 231  

10.13. Malware Result Vocabulary. 232  

10.14. Malware Capabilities Vocabulary. 232  

10.15. Malware Type Vocabulary. 236  

10.16. Network Socket Address Family Enumeration. 238  

10.17. Network Socket Type Enumeration. 238  

10.18. Opinion Enumeration. 239  

10.19. Pattern Type Vocabulary. 240  

10.20. Processor Architecture Vocabulary. 240  

10.21. Region Vocabulary. 241  

10.22. Report Type Vocabulary. 243  

10.23. Threat Actor Type Vocabulary. 244  

10.24. Threat Actor Role Vocabulary. 246  

10.25. Threat Actor Sophistication Vocabulary. 247  

10.26. Tool Type Vocabulary. 249  

10.27. Windows™ Integrity Level Enumeration. 250  

10.28. Windows™ PE Binary Vocabulary. 251  

10.29. Windows™ Registry Datatype Enumeration. 251  

10.30. Windows™ Service Start Type Enumeration. 252  

10.31. Windows™ Service Type Enumeration. 253  

10.32. Windows™ Service Status Enumeration. 254  

  11. 定制化STIX (已过时) ——Customizing STIX (Deprecated) 255  

11.1. Custom Properties (Deprecated) 255  

11.2. Custom Objects (Deprecated) 256  

11.3. Custom Object Extensions (Deprecated) 257  

  12. 规范 ——Conformance. 259  

12.1. STIX Object Producers and Consumers. 259  

12.2. STIX Object Mandatory Features. 259  

12.3. STIX Object Optional Features. 259  

12.4. STIX Patterning Conformance. 259  

12.5. STIX Pattern Producer 260  

12.6. STIX Pattern Consumer 260  

12.7. STIX Patterning Conformance Levels. 260  

附录A 置信等级 ——Confidence Scales. 262  

附录B 关系汇总表 ——Relationship Summary Table. 265  

附录C 附加的例子 ——Additional Examples. 268  

C.1. 基础结构附加示例 ——Infrastructure Additional Examples. 268  

C.2. 扩展定义附加示例 ——Extension Definition Additional Examples. 274  

附录D IANA的考虑 ——IANA Considerations. 279  

附录E 参考文献 ——References. 282  

E.1. 规范性引用文件 ——Normative References. 282  

E.2. 信息性参考文献 ——Informative References. 285  

附录F 致谢 ——Acknowledgments. 288  

附录G 修订史 ——Revision History. 294  

# 1\. 介绍 ——Introduction

## 1.1. 概述 ——Overview

STIX是一个定义了网络威胁情报分类法的数据库，它由以下对象表示：

 **STIX Objects**

|

STIX Bundle Object

STIX包对象  
  
---|---  
  
 **STIX Core Objects**

 **STIX** **核心对象**

|

 **STIX Meta Objects (SMO)**

 **STIX** **元对象**  
  
STIX Domain Objects  
(SDO)

|

STIX Cyber-observable Objects  
(SCO)

|

STIX Relationship Objects  
(SRO)

|

Extension Definition Objects

|

Language Content Objects

|

Marking Definition Objects  
  
STIX域对象

|

STIX网络可观测对象

|

STIX关系对象

|

扩展定义对象

|

语言内容对象

|

标记定义对象  
  
 **STIX** **核心对象** **——STIX Core Objects**

包含所有SDO（STIX域对象）、 SCO（STIX网络可观测对象）和 SRO（STIX关系对象）。

 **STIX** **域对象** ******——** **STIX Domain Objects** **（** **SDO** **）**

高层次情报对象，威胁分析人员在了解威胁态势时通常会创建或使用SDO来标识行为和构造。

 **STIX** **网络可观测对象** **——STIX Cyber-observable Objects** **（SCO** **）**

SCO对象用于表示一个网络或主机中所观测到的事实，这些事实可能会被使用并与高层次情报相关联，以形成对威胁态势更完整的理解。

 **STIX** **关系对象 ——STIX Relationship Objects** **（SRO** **）**

包含“SDO对象间关联关系”对象、“SCO对象间关联关系”对象和“SDO与SCO之间关联关系” 对象，以形成对威胁态势更完整的理解。

 **STIX** **元对象 ——STIX Meta Objects (SMO)**

SMO也是一个STIX对象，提供了“必要的粘合”和“关联的元数据”来丰富或扩展STIX核心对象，以支持用户和系统工作流。

 **STIX** **包对象** **——STIX Bundle Object**

STIX包对象提供一种包装方法，可以将任意STIX内容打包在一起进行发布。

### 1.1.1. 基于图的模型 ——Graph-Based Model

STIX是一个由“节点”和“边”相连接的“图”，STIX域对象（SDO）和STIX网络可观测对象（SCO）定义了“图”中的“节点”，STIX关系对象（SRO）（包括外部的关系和嵌入式的关系）定义了“图”中的“边”，基于图形语言的描述方式是一种常见分析方法，并且兼顾了CTI的灵活性、模块化、结构化和表达一致性。

### 1.1.2. STIX域对象 ——STIX Domain Objects

STIX 定义了一组 STIX 域对象
（SDOs）：攻击模式、攻击事件、处置建议、编组、身份、威胁指标、基础设施、入侵集、地理位置、恶意代码、恶意代码分析结果、批注信息、可观测数据、专家见解、报告、威胁源、工具软件、脆弱性，每类对象均对应于
CTI 中的常用概念。

STIX 域对象 （SDOs）在第 4 节中定义。

### 1.1.3. STIX网络可观测对象 ——STIX Cyber-observable Objects

STIX 定义了一组 STIX 网络可观测对象 （SCOs），用于刻画基于主机和基于网络的信息。各种 STIX 域对象 （SDOs） 使用
SCOs来提供上下文支持。例如，SDO观测到的数据表示在特定时间所观测到的原始数据。

STIX网络可观测对象（SCOs）记录了有关网络或主机上发生的事实，但是并不会捕获是“何人”、“何时”或“何事”。通过将 SCOs与 STIX 域对象
（SDOs）
相关联，也许可以传达对威胁态势的更高层次理解并可能提供关于特定情报中“何人”及“何事”的见解，可能关联到一个组织。例如，关于一个样本文件的信息、一个观测到正在运行的进程，又或是两个IP间所产生的网络流量，都可以被捕获为SCOs。

STIX网络可观测对象(SCOs) 在第 6 节中定义。

以前在STIX 2.0中，网络可观测对象只能以“objects”形式存在于“Observed Data
object”中，目前仍然可能以这种方式来表示网络可观测对象，但此方法已被弃用，请参阅第 2.13 节。

### 1.1.4. STIX关系对象 ——STIX Relationships

关系是 STIX 域对象 （SDOs）、STIX 网络可观测对象 （SCOs） 之间或 SDO 和 SCO
之间的链接，用于描述对象间的关联关系。关系可以使用外部 STIX 关系对象 （SRO）
表示，或者在某些情况下，可以通过对象的某些属性存储一个嵌入关系的“标识符”来引用嵌入式关系。（例如 **created_by_ref** 属性）

通用 STIX 关系对象（generic STIX Relationship Object ，SRO）是SROs两种类型之一，适用于 STIX
中的大多数关系类型。此类通用SRO包含一个名为 **relationship_type** 的属性，用于具体地规范关系所表示的内容。此规范定义了一组用于
**relationship_type** 属性的已知术语，作为SDOs 之间关联明确的类型。例如，威胁指标SDO 通过indicates的
**relationship_type** 定义了自身与恶意软件的关系，描述了如何使用指标来检测是否存在相应恶意软件。除了规范中定义的术语外，STIX
还允许将用户自定义的术语用作关系类型。

目前，除了generic STIX Relationship Object外还有另外一类SRO——Sighting
SRO。Sighting对象用于捕获实体中“观测”到SDO出现的案例，例如观测一个指标。Sighting是一个单独的
SRO，因为它包含仅适用于Sighting关系的附加属性，例如count。如果需要generic
Relationship对象上不存在的其他属性，则可以在STIX未来版本中定义其他SROs。

除了使用 SROs (Relationship and Sighting)创建的关系外，STIX 还使用 ID
引用来表示嵌入的关系。嵌入关系对象包含一个属性存储着另一个对象的ID，用来引用另一个STIX对象。嵌入关系适合在“当属性内嵌在在对象中”时使用，而不是“第三方可能添加的内容”或“可能需要包含置信度分数的内容”时使用。由于它们表示一个内嵌链接并且没有其他属性，因此不需要
SRO 来表示它们。嵌入关系只能由包含它的对象的创建者（对象创建者）断言。

例如， STIX 对象创建的实体是内嵌的关于此对象的部分事实，因此这些信息是在 **created_by_ref**
属性所包含的嵌入式关系中捕获的，而不是通过使用SRO捕获。

嵌入式关系(ID引用)在 3.3 节中描述，STIX关系对象(SROs)在第 _5_ 节中定义。

### 1.1.5. STIX 网络可观测容器观测数据关系（弃用）——STIX Cyber Observable Observed Data
Relationships (弃用)

在为 STIX 2.1 规范进行精炼时，CTI TC达成共识，认为STIX 2.0 “Cyber Observable Container(见 2.13
节)”和图模型中“Observed Data object's graph”不足以支持关键的CTI用例。因此，在STIX 2.1中，“Cyber
Observable Container”被弃用，并推荐使用STIX 关系对象 (SROs) 替代。在“Cyber Observable
Container's graph（弃用）”图模型的上下文中，对象关系是连接两个(或更多)相关联SCOs的引用，在同一个“Cyber Observable
Container”中这些关系仅限于所包含的SCOs。

“Cyber Observable Container”关系不应与第 5 节中定义的 STIX 关系对象 （SROs） 混淆。

### 1.1.6. STIX模式 ——STIX Patterning

STIX Patterning语言可以检测网络和端点上的活动。这种语言允许根据时间戳与威胁情报平台或其他类似系统所收集的网络可观测数据进行匹配。STIX
Patterning目前仅由 STIX Indicator对象使用，但它可用于其他用例。

在进行筹备STIX Patterning工作之前，对现有的模式语言（如 Snort 或 Yara
）进行了彻底的评估，最终得出结论“没有现有的模式语言可以解决或支持STIX用例”。在OASIS组织的背景条件下，从“技术”和“知识产权（licensing/IPR）”两个方面来看，扩展现有语言存在诸多问题，因此排除此选项。

STIX Patterning主要设计用于支持 STIX
威胁指标。因此，它是一种用于传达如何查找在“给定网络或端点”中处于活动状态的“恶意代码”或“威胁源”的机制。

当前版本着重于支持常见的用例集，因此允许 STIX 的“生产者”和“消费者”可以利用初始patterns集进行表达。由于需要表达更复杂的模式，STIX
Patterning语言将在将来的版本中进行扩展，以提高其自动检测/修正方法的效能。

STIX Patterning在第 9 节中定义。

### 1.1.7. STIX模式ANTLR语法 ——STIX Patterning ANTLR Grammar

STIX Patterning 规范新版 ANTLR 语法可以在 Github 的 Pattern 语法存储库[Pattern
Grammar]中找到。注意，此语法是非规范性的，仅用于辅助实现。

### 1.1.8. STIX 通用属性 ——STIX Common Properties

STIX 域对象 （SDOs） 和关系对象 （SROs）
都共享了一组通用属性，这些属性提供核心功能，例如版本控制和数据标记（表示如何共享和使用数据）。同样，所有 STIX 网络可观测对象 （SCOs）
也共享了一组适用于所有 SCOs 的通用属性。类似的，STIX 元对象 （SMOs） 也使用了部分的通用属性。

### 1.1.9. STIX开放词汇表和枚举 ——STIX Open Vocabularies and Enumerations

一些STIX属性使用开放词汇表或枚举来定义。STIX中定义了枚举和开放词汇表，为了增强互联的可能性，不同实体使用相同的“确切字符串”来表达同一观点。如果使用一致表达，开放词汇可以减少同一个实体的相似表达，比如“能源部门”、“能源”，从而使“比较”和“关联”更加容易。

虽然强烈建议使用STIX词汇表中的预定义值，但在某些情况下这可能是不可行的。为了解决这个问题，生产者被允许使用开放词汇之外的值。在枚举的情况下，生产者被要求只使用STIX规范中定义的值。

第 10 节定义了STIX开放词汇表和枚举。本节“开放词汇表”中定义了“属性标识”里推荐使用的词汇。例如，第 4.17 节定义了“威胁源”的
**sophistication** 属性， 使用了第 10.25 节所定义的“威胁源”Sophistication词汇表。

### 1.1.10. 保留名称 ——Reserved Names

保留属性名称用一个称为“RESERVED”的类型并标记 “RESERVED FOR FUTURE USE” 描述文本。更多有关信息，请参阅第 3.8 节。

### 1.1.11. 序列化 ——Serialization

STIX的定义独立于任何“特定的存储”或“序列化方式”。然而，STIX 2.1的MTI（mandatory-to-implement）序列化使用UTF-8
编码的JSON，遵循 [RFC7493] 和[RFC8259] 规范。在表示所有STIX对象时，使用 JSON Object
类型进行描述。换句话说，所有STIX适用的工具都必须实现对JSON的支持，另外也可以实现对其他序列化的支持。

### 1.1.12. 传输STIX ——Transporting STIX

STIX 2.1定义本身与传输无关，即“结构”和“序列化”不依赖于任何特定的传输机制。作为 CTI 配套的规范，TAXII 专门设计用于STIX
对象的传输。STIX 提供了一个包（参见第 8 节）作为 STIX 对象的容器，以支持传输大量 STIX 数据，尤其是在通过非 TAXII 通信机制下。

### 1.1.13. JSON存储库 ——JSON Schemas

JSON存储库是由网络威胁情报技术委员会的成员开发的，可以在cti-stix2-json-schemas OASIS开放存储库[JSON
Schema]中找到。JSON存储库信息丰富，并尽力尝试验证内容是否符合STIX 2.1规范中的结构要求。该规范是STIX 2.1版本的标准描述。

## 1.2. 对早期版本的变更 ——Changes From Earlier Versions

本部分列出了与上个版本（STIX 2.0）相比的所有主要变更。

### 1.2.1. STIX 2.1主要变化和补充内容 ——STIX 2.1 Major Changes and Additions

STIX 2.1 differs from STIX 2.0 in the following ways:

  1. New objects: Grouping, Infrastructure, Language-Content (internationalization), Location, Malware-Analysis, Note, Opinion
  2. Objects that have undergone significant change: Malware, all SCOs
  3. New concepts: Confidence
  4. STIX Cyber-observable Objects can now be directly related using STIX Relationship Objects
  5. Renamed conflicting properties on Directory Object, File Object, Process Object, and Windows Registry Key Object.
  6. Added relationship from Indicator to Observed Data called "based-on".
  7. Added a description to Sighting and added a name to Location.
  8. Made some SCO relationships external on Domain-Name, IPv4-Addr, and IPv6-Addr.
  9. Added STIX Extension mechanisms and deprecated custom properties, objects, and extensions.

## 1.3. 术语 ——Glossary

 **AV** \- Anti-Virus / Anti-Malware solution

 **CAPEC** \- Common Attack Pattern Enumeration and Classification

 **Consumer** \- Any entity that receives STIX content

 **CTI** \- Cyber Threat Intelligence 网络威胁情报

 **Deprecated** \- STIX features or properties that are in the process of
being replaced by newer ones.

 **Embedded Relationship** \- A link (an "edge" in a graph) between one STIX
Object and another represented as a property on one object containing the ID
of another object

 **Entity** \- Anything that has a separately identifiable existence (e.g.,
organization, person, group, etc.)

 **IEP** \- FIRST (Forum of Incident Response and Security Teams) Information
Exchange Policy

 **Instance** \- A single occurrence of a STIX Object version

 **MTI** \- Mandatory To Implement

 **Object Creator** \- The entity that created or updated a STIX Object (see
section 3.5)

 **Object Representation** \- An instance of an object version that is
serialized as STIX

 **Producer** \- Any entity that distributes STIX content, including object
creators as well as those passing along existing content

 **SCO** \- STIX Cyber-observable Object

 **SDO -** STIX Domain Object (a "node" in a graph)

 **SMO** \- STIX Meta Object

 **SRO** \- STIX Relationship Object (one mechanism to represent an "edge" in
a graph)

 **STIX** \- Structured Threat Information Expression

 **STIX Content** \- STIX documents, including STIX Objects, STIX Objects
grouped as bundles, etc.

 **STIX Object** \- A STIX Domain Object (SDO), STIX Cyber Observable Object
(SCO), STIX Relationship Object (SRO), or STIX Meta Object (SMO).

 **STIX Relationship** \- A link (an "edge" in a graph) between two STIX
Objects represented by either an SRO or an embedded relationship

 **STIX Extension** \- A set of mechanisms supporting adding new objects and
updating existing objects in a standard way.

 **TAXII** \- An application layer protocol for the communication of cyber
threat information

 **TLP** \- Traffic Light Protocol

 **TTP** \- Tactic, technique, or procedure; behaviors and resources that
attackers use to carry out their attacks

# 2\. 通用数据类型 ——Common Data Types

本节定义了在整个 STIX 中用于所有 STIX 对象的通用类型，这些“类型”将被其他章节中的“Type”列所引用。本节定义 STIX
信息模型中所使用的通用类型的“名称”和“允许值”；但是，它并不定义任何使用这些类型的属性所表达的含义。这些类型可能会在文档的其他位置进一步限定。

下表是本节中定义的“数据类型”的摘要。

 **Type**

|

 **Description**  
  
---|---  
  
binary

|

A sequence of bytes.  
  
boolean

|

A value of true or false.  
  
dictionary

|

A set of key/value pairs.  
  
enum

|

A value from a STIX Enumeration.  
  
external-reference

|

A non-STIX identifier or reference to other related external content.  
  
float

|

An IEEE 754 [IEEE 754-2008] double-precision number.  
  
hashes

|

One or more cryptographic hashes.  
  
hex

|

An array of octets as hexadecimal.  
  
identifier

|

An identifier (ID) is for STIX Objects.  
  
integer

|

A whole number.  
  
kill-chain-phase

|

A name and a phase of a kill chain.  
  
list

|

A sequence of values ordered based on how they appear in the list. The
phrasing "list of type <type>" is used to indicate that all values within the
list **MUST** conform to the specified type.  
  
observable-container

|

One or more STIX Cyber-observable Objects in the deprecated Cyber Observable
Container.  
  
open-vocab

|

A value from a STIX open (open-vocab) or suggested vocabulary.  
  
string

|

A series of Unicode characters.  
  
timestamp

|

A time value (date and time).  
  
​

## 2.1. 二进制 ——Binary

 **Type Name:** binary

“binary”数据类型用来表示“字节序列”。为了允许在自定义对象上进行模式匹配，对于使用二进制类型的所有属性，属性名称 **必须** 以“_bin”结尾。

JSON MTI 序列化时遵循[RFC4648]规范，使用base64 编码字符串进行表达。其他序列化 **应当** 使用本机二进制类型（如果可用）。

## 2.2. 布尔 ——Boolean

 **Type Name:** boolean

“boolean”类型的值可以是真或假。此类型属性的值 **必须** 是“true”或“false”。

JSON MTI 序列化时遵循[RFC8259]规范，使用布尔值（true 和false），这些值是字面量（不带引号）的“true”或“false”。

 **Examples**

{

...

"summary": true,

...

}

## 2.3. 字典 ——Dictionary

 **Type Name:** dictionary

“dictionary”可以包含一组任意“键值对”的集合。字典的“键”在每个字典中 **必须** 是唯一的， **必须** 采用
ASCII编码，并且仅限于字符 a-z（小写 ASCII）、A-Z（大写 ASCII）、数字 0-9、连字符 （-） 和下划线 （_）。字典中“键”的长度
**必须在** ****250 个 ASCII 字符以内，并且应为小写。

STIX 中禁止使用空字典，如果可选的属性， **不得** 用替代品将其省略。如果该属性是必需的，则字典 **必须** 存在，并且必须至少有一个键值对。

“dictionary”的“值” **必须** 是有效属性的基本类型。

## 2.4. 枚举 ——Enum

 **Type Name:** enum

“enum”类型是使用“string”来表示的“硬编码”术语列表 。对于使用此类型的属性，有一个定义了“值”的列表，该“值”取自于列表中的标识。STIX
枚举在第 10 节中定义。规范中在“enum”中定义的术语 **不得** 在实现中扩展。

JSON MTI 序列化时遵循[RFC8259]规范，使用 JSON 字符串类型表示枚举。

## 2.5. 外部引用 ——External Reference

 **Type Name:** external-reference

外部引用用于描述“指向外部表示STIX信息的指针”。例如，“恶意软件对象”可以使用“外部引用”来表示“外部数据库中该恶意软件的ID”，或者“报告”可以使用引用来表示“源物料”。

JSON MTI序列化时遵循[RFC8259]规范，使用JSON对象类型表示external-reference。

### 2.5.1. Properties

 **Property Name**

|

 **Type**

|

 **Description**  
  
---|---|---  
  
 **source_name** (required)

|

string

|

The name of the source that the external-reference is defined within (system,
registry, organization, etc.).  
  
 **description** (optional)

|

string

|

A human readable description.  
  
 **url** (optional)

|

string

|

A URL reference to an external resource [RFC3986].  
  
 **hashes** (optional)

|

hashes

|

Specifies a dictionary of hashes for the contents of the **url**. This
**SHOULD** be provided when the **url** property is present.

Dictionary keys **MUST** come from one of the entries listed in the hash-algorithm-ov open vocabulary.

As stated in Section 2.7, to ensure interoperability, a SHA-256 hash
**SHOULD** be included whenever possible.  
  
 **external_id** (optional)

|

string

|

An identifier for the external reference content.  
  
### 2.5.2. Requirements

  * In addition to the **source_name** property, at least one of the **description** , **url** , or **external_id** properties **MUST** be present.

 **Examples**

An external-reference to a VERIS Community Database (VCDB) [VERIS] entry

{

...

"external_references": [

{

"source_name": "veris",

"external_id": "0001AA7F-C601-424A-B2B8-BE6C9F5164E7",

"url": "https://github.com/vz-risk/VCDB/blob/125307638178efddd3ecfe2c267ea434667a4eea/  
data/json/validated/0001AA7F-C601-424A-B2B8-BE6C9F5164E7.json",

"hashes": {

"SHA-256": "6db12788c37247f2316052e142f42f4b259d6561751e5f401a1ae2a6df9c674b"

}

}

],

...

}

An external-reference from the CAPEC™ [CAPEC] repository

{

...

"external_references": [

{

"source_name": "capec",

"external_id": "CAPEC-550"

}

],

...

}

An external-reference from the CAPEC repository with URL

{

...

"external_references": [

{

"source_name": "capec",

"external_id": "CAPEC-550",

"url": "<http://capec.mitre.org/data/definitions/550.html>"

}

],

...

}

An external-reference to ACME Threat Intel's report document

{

...

"external_references": [

{

"source_name": "ACME Threat Intel",

"description": "Threat report",

"url": "[http://](http://intelreport.mandiant.com/Mandiant_APT1_Report.pdf)
_www.example.com/threat-report.pdf_ "

}

],

...

}

An external-reference to a Bugzilla item

{

...

"external_references": [

{

"source_name": "ACME Bugzilla",

"external_id": "1370",

"url": "[https://](https://issues.oasis-open.org/browse/TAB-1370)
_www.example.com/bugs/1370_ "

}

],

...

}

An external-reference to an offline threat report (i.e., e-mailed, offline,
etc.)

{

...

"external_references": [

{

"source_name": "ACME Threat Intel",

"description": "Threat report"

}

],

...

}

## 2.6. 浮点数 ——Float

 **Type Name:** float

float数据类型表示IEEE 754 [IEEE
754-2008]双精度数(例如，带有小数部分的数)。然而，由于“±Infinity”和“NaN”在JSON中是无法表示的，所以它们在STIX中是无效值。

JSON MTI序列化时遵循[RFC7493]规范，使用JSON Number 类型表示。

​

 **Examples**

{

...

"distance": 8.321,

...

}

## 2.7. 哈希值 ——Hashes

 **Type Name:** hashes

哈希类型表示一个或多个加密哈希，作为一组特殊的键/值对。因此，每个哈希算法的名称 **必须** 声明为字典中的一个键，并且 **必须**
标识用于生成此哈希值的名称。这个名称 **应当** 取自hash-algorithm-ov开放词汇表中定义的值之一。

字典键在每个hashes属性中 **必须是**
唯一的，必须是ASCII格式，并且限于字符a-z(小写ASCII)、A-Z(大写ASCII)、数字0-9、连字符(-)和下划线(_)。字典键的最小长度
**必须** 为3个ASCII字符，并且 **不得** 超过250个ASCII字符。字典值 **必须**
是由字典键中声明的“哈希类型”定义所格式化的string。

为了获得良好的兼容性， **应当** 尽可能使用SHA-256 hash。

​

 **Examples**

SHA-256 and User-Defined Hash

{

"SHA-256": "6db12788c37247f2316052e142f42f4b259d6561751e5f401a1ae2a6df9c674b",

"x_foo_hash": "aaaabbbbccccddddeeeeffff0123457890"

}

## 2.8. 十六进制 ——Hexadecimal

 **Type Name:** hex

hex数据类型将八位字节(8-bit bytes)的数组编码为十六进制。该字符串 **必须**
由偶数个十六进制字符组成，由数字“0”到“9”以及小写字母“a”到“f”构成。

为了允许对自定义对象进行 pattern matching ，对于所有使用hex型的属性，属性名 **必须** 以“_hex”结尾。

 **Examples**

...

"src_flags_hex": "00000002"

...​

## 2.9. 标识符 ——Identifier

 **Type Name:** identifier

identifier唯一地标识STIX对象，这是非常明确的。identifier的确定性意味着由多个生产者为完全相同的“STIX对象”生成的identifier，使用相同的“命名空间”、“ID
Contributing 属性”，并且UUID方法将也将具有完全相同的identifier值

除了在已弃用的 Cyber Observable 容器中所使用的identifiers之外，所有identifiers都 **必须** 遵循object-type--UUID的形式，其中object-type是被标识或引用对象的type属性的确切值(根据定义，所有类型名称都是小写字符串)，而UUID
**必须** 是符合RFC 4122规范的UUID [RFC4122]。

identifiers的UUID部分在给定“生产者”所生成的所有对象中 **必须** 是唯一的，不管 object-type
前缀标识的是什么类型。也就是说，“生产者” **不能** 在不同类型的对象间复用identifiers的UUID部分。

STIX Domain 对象、STIX Relationship 对象、STIX Meta 对象和STIX Bundle 对象的identifiers部分
**应该**
使用UUIDv4的UUID。生产者使用非UUIDv4生成时需要注意潜在的冲突，并且应该使用保证唯一性的命名空间。但是，如果使用UUIDv5生成时，它们
**不能** 使用命名空间00abedb4-aa42-466c-9c01-fed23315a9b7。

STIX Cyber-observable 对象的 **应当** 采用基于UUIDv5的UUID作为identifier，并且 **应当**
根据以下规则生成:

  * The namespace **SHOULD** be 00abedb4-aa42-466c-9c01-fed23315a9b7. This defined namespace is necessary to support the goal of deduplication and semantic equivalence of some STIX objects in the community of producers.
  * The value of the name portion **SHOULD** be the list of "ID Contributing Properties" (property-name and property value pairs) as defined on each SCO object and **SHOULD** be represented as a JSON object that is then serialized / stringified according to [RFC8785] to ensure a canonical representation of the JSON data.
  * If the contributing properties are all optional, and none are present on the SCO, then a UUIDv4 **MUST** be used.
  * Producers not following these rules **MUST NOT** use a namespace of 00abedb4-aa42-466c-9c01-fed23315a9b7 and **SHOULD** use UUIDv4 in cases where the id would not be unique.

被弃用的Cyber-observable容器中使用的STIX Cyber-observable对象可能使用任何string值作为identifier。对于被弃用的Cyber
Observable容器，生产者通常使用简单的数字字符串作为identifier (例如，“0”、“1”、“2”等)。更多信息见第 2.13 节。

  * These identifiers, when used inside the deprecated Cyber-observable Objects Container specify a local reference to a Cyber-observable Object. These references **MUST** be valid within the local scope of the Cyber Observable Container (observable-container) that holds both the source Cyber-observable Object and the Cyber-observable Object that it references.
  * These identifiers **SHOULD** be a non-negative monotonically increasing integer, incrementing by 1 from a starting value of 0, and represented as a string within the JSON MTI serialization. However, implementers **MAY** elect to use an alternate key format if necessary.

使用Identifiers:

STIX网络威胁情报的消费者在处理Observed-Data对象的 **objects** 属性时， 可以假设该identifier是旧的弃用的Cyber
Observable容器identifier。消费者还可以检查identifier以查看它是否包含object-type，如果不包含，可以假设它是一个弃用的Cyber Observable容器identifier。如果它包含object-type，并且它可以匹配一个SCO，那么它很可能是一个UUIDv5确定性identifier，可以通过检查identifier的UUID部分来验证。[RFC
4122]定义了如何区分UUIDv4和UUIDv5值。

注意:有关使用UUIDv5的信息，请参阅 附录D 中的security considerations部分。

JSON MTI序列化时遵循[RFC8259]规范，使用JSON String类型表示identifier

 **Examples**

{

...

"type": "indicator",

"id": "indicator--e2e1a340-4415-4ba8-9671-f7343fbf0836",

...

}

{

"type": "ipv4-addr",

"id": "ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd",

"value": "198.51.100.3"

}

Deprecated Cyber Observable Container Identifiers

{

"0": {

"type": "ipv4-addr",

"value": "198.51.100.2"

},

"1": {

"type": "network-traffic",

"dst_ref": "0"

}

}

## 2.10. 整数 ——Integer

 **Type Name:** integer

integer data类型表示一个整数。除非另有规定，所有整数 **必须**
能够表示为[RFC7493]中定义的有符号54-bit值([-(2**53)+1，(2**53)-1])。在使用时，可以对该类型施加附加的限制。integer大小限制为54-bit位值，而不是RFC中规定的64-bit位值。

 **Examples**

{

...

"count": 8,

...

}

## 2.11. 杀伤链阶段 ——Kill Chain Phase

 **Type Name:** kill-chain-phase

kill-chain-phase表示“杀伤链”中的一个阶段，它描述了攻击者为了达到目标而可能历经的各个阶段。

JSON MTI序列化时遵循[RFC8259]规范，使用JSON Object类型表示kill-chain-phase。

 **Property Name**

|

 **Type**

|

 **Description**  
  
---|---|---  
  
 **kill_chain_name** (required)

|

string

|

The name of the kill chain. The value of this property **SHOULD** be all
lowercase and **SHOULD** use hyphens instead of spaces or underscores as word
separators.  
  
 **phase_name** (required)

|

string

|

The name of the phase in the kill chain. The value of this property **SHOULD**
be all lowercase and **SHOULD** use hyphens instead of spaces or underscores
as word separators.  
  
当引用Lockheed Martin Cyber Kill Chain™时， **kill_chain_name** 属性 **必须**
是lockheed-martin-cyber-kill-chain。

 **Examples**

Example specifying the "reconnaissance" phase from the Lockheed Martin Cyber
Kill Chain

{

...

"kill_chain_phases": [

{

"kill_chain_name": "lockheed-martin-cyber-kill-chain",

"phase_name": "reconnaissance"

}

],

...

}

Example specifying the "pre-attack" phase from the "foo" kill-chain

{

...

"kill_chain_phases": [

{

"kill_chain_name": "foo",

"phase_name": "pre-attack"

}

],

...

}

## 2.12. 列表 ——List

 **Type Name:** list

list类型定义了一个值的序列，根据值的显示方式进行排序。短语"list of type <type>"用于表示列表中的所有值 **必须**
符合指定的类型。例如，integer类型的list意味着列表中的所有值都必须是integer类型。此规范没有声明列表中允许存放的数量上线；但是，list的每个实例
**必须** 至少有一个值。特定的 STIX 对象属性可以为“列表的长度”定义更严格的上限和/或下限。

STIX 中禁止使用空列表，如果属性是可选的，则 **不得** 将其用作省略属性的替代品。如果该属性是必需的，则列表 **必须** 存在，并且 **必须**
至少有一个值。

JSON MTI 序列化时遵循[RFC8259]规范，使用JSON Array 类型表示，它是零个或多个值的有序列表。

 **Examples**

{

...

"observed_data_refs": [

"observed-data--b67d30ff-02ac-498a-92f9-32f845f448cf",

"observed-data--c96f4120-2b4b-47c3-b61f-eceaa54bd9c6",

"observed-data--787710c9-1988-4a1b-9761-a2de5e19c62f"

],

...

}

## 2.13. 可观测容器(已过时) ——Observable Container (deprecated)

 **Type Name:** observable-container

在Observable Container中表示Cyber-observable对象已被弃用，在创建新内容时 **不应**
再使用。现有的Observable Data对象使用 Observable Containers 时，可能包含本规范中定义的 SCOs，但也可能包含
STIX 2.0 版中所述的Cyber-observable对象(STIX Version 2.0. Part 3: STIX Objects)。

Observable Container类型可以包含一个或多个 STIX Cyber-observable对象作为一组特殊的键/值对。字典中的键是用于引用位于可观测容器中的对象作为某个键的值的引用。“键”的值是指向“其他对象 embedded
relationship 属性”的引用，它们 **必须** 位于同一容器中（例如Network Traffic 对象上的 src_ref 属性）。

解析引用的过程是通过“键”的“引用值”识别observable
container中的所有对象。当属性的值（例如，src_ref），与位于同一容器中的另一个对象的“键”完全匹配时，引用将解析为对象（指定引用）。所有这些引用都是容器内的本地引用，并且在同一容器中
**必须** 提供所引用的对象。此规范不涉及引用解析的实现。observable container字典中的每个键都是一个identifier。

 **STIX 2.0 Examples**

Network Traffic with Source/Destination IPv4 Addresses and AS

{

"0": {

"type": "ipv4-addr",

"value": "1.2.3.4",

"belongs_to_refs": ["3"]

},

"1": {

"type": "ipv4-addr",

"value": "2.3.4.5"

},

"2": {

"type": "network-traffic",

"src_ref": "0",

"dst_ref": "1",

}

"3": {

"type": "as"

"number": 42

}

}

 ****

{

"0": {

"type": "email-addr",

"value": "jdoe@example.com",

"display_name": "John Doe"

},

"1": {

"type": "email-addr",

"value": "mary@example.com",

"display_name": "Mary Smith"

},

"2": {

"type": "email-message",

"from_ref": "0",

"to_refs": ["1"],

"date": "1997-11-21T15:55:06Z",

"subject": "Saying Hello"

}

}

## 2.14. 开放词汇 ——Open Vocabulary

 **Type Name:** open-vocab

open-vocab类型使用string表示。对于使用此类型的属性，会有一个“建议值”列表，称为“建议词汇表”，该属性值在定义中标识。这些“建议词汇”在第10节中定义。属性的值
**应当** 从建议的词汇中选择，但也可以是任何其他string值。来自建议词汇表之外的值 **应当** 全部小写，并且 **应当**
使用连字符替代空格或下划线作为单词分隔符。

消费者在接收 STIX 内容时，当内容中存在有一个或多个未在“建议词汇表”中定义的open-vocab术语，可能会忽略这些值。

JSON MTI 序列化时遵循[RFC8259]规范，使用JSON String类型表示open-vocab。

 **Examples**

Example using value from the suggested vocabulary. In this example the Threat
Actor **sophistication** property is an open vocabulary and we are using one
of the suggested vocabulary values.

{

...,

"sophistication": "intermediate",

...

}

Example using a user-defined value. In this example, for the same Threat Actor
**sophistication** property, we are not using a value in the suggested
vocabulary.

{

...,

"sophistication": "pbx-advanced-activity",

...

}

## 2.15. 字符串 ——String

 **Type Name:** string

string数据类型表示“Unicode 编码字符集”中有效字符的组成的“有限长度”字符串[ISO10646]。Unicode 包含 ASCII
和许多其他国际字符集的字符。

JSON MTI 序列化时遵循[RFC8259]规范,使用JSON String类型表示，它要求使用 UTF-8 编码来支持 Unicode。

 **Examples**

{

...

"name": "The Black Vine Cyberespionage Group",

...

}

## 2.16. 时间戳 ——Timestamp

 **Type Name:** timestamp

timestamp类型定义了 STIX 中日期和时间的表示方式。

JSON MTI 序列化时遵循[RFC8259]规范，使用JSON String类型表示timestamp。

### 2.16.1. Requirements

  * The timestamp property **MUST** be a valid RFC 3339-formatted timestamp [RFC3339] using the format YYYY-MM-DDTHH:mm:ss[.s+]Z where the "s+" represents 1 or more sub-second values. The brackets denote that sub-second precision is optional, and that if no digits are provided, the decimal place **MUST NOT** be present.
  * The timestamp **MUST** be represented in the UTC timezone and **MUST** use the "Z" designation to indicate this.

请注意，当使用大于纳秒的精度时，可能会对互操作性产生影响，因为当存储为 UNIX 时间戳或浮点数时，由于这些格式的基本精度，它们可能会被截断。

 **Examples**

{

...

"created": "2016-01-20T12:31:12.123Z",

...}

# 3\. STIX 一般概念 ——STIX General Concepts

## 3.1. 属性名称和字符串字面量 ——Property Names and String Literals

所有类型名称、属性名称和字面量 **必须** 为小写，除非当引用其他标准中定义的规范名称（例如，来自 IANA
registry的字面量）。小写字母由“局部约定”定义。类型名称和属性名称 **必须** 以字母字符开头（例如，在 ASCII 中，这将是 a 到
z）。“属性名称”中的单词 **必须** 用下划线 （_） 分隔，而“类型名称”和“字符串枚举”中的单词 **必须** 用连字符 （-）
分隔。字典“键”和哈希算法名称可能使用下划线 （_） 或连字符 （-）。所有类型名称、属性名称、对象名称和词汇术语的长度 **必须** 介于 3 到 250
个字符之间。

属性的某些名称 **必须** 有特定的后缀。

  * 如果属性的值包含embedded relationships的ID引用，它 **必须** 以 **_ref** 结尾；
  * 如果属性的值包含一个embedded relationships列表，它 **必须** 以_ **refs** 结尾；
  * 如果属性的值包含binary值，它 **必须** 以 **_bin** 结尾；
  * 如果属性的值包含一个hexadecimal值，它 **必须** 以 **_hex** 结尾；
  * 属性可能包含其他编码的字符串。 某些对象类型将定义一个额外的可选属性来指定此编码。 附加属性的名称 **必须** 以 **_enc** 结尾。 例如， **name** 属性可能包含其他编码中的文本，而 **name_enc** 属性将用于指定当前使用的编码。 当原始属性不存在时，编码属性 **不得** 出现。

在JSON序列化中，所有属性名和字符串字面量 **必须** 与本规范中属性表中列出的名称完全相同，包括大小写。例如，SDO公共属性
**created_by_ref** 生成JSON时必须包含键名“created_by_ref”。属性表中标记为required的属性 **必须**
出现在JSON序列化中。

某些属性可能被指定为“已弃用”。这些属性正在被删除或替换，实现者应考虑使用较新的设计。

## 3.2. 通用属性 ——Common Properties

本节定义 STIX 对象上 **可能** 存在的通用属性。虽然某些 STIX 对象会全部使用这些通用属性，但并非所有对象类型都会全部使用。 每种类型的
STIX 对象各自定义哪些公共属性是必需的、哪些是可选的、以及哪些是不适用的。本节之下提供了比较简略的汇总表。此信息也可以在每个对象的属性表的开头找到。

 **Property Name**

|

 **Type**

|

 **Description**  
  
---|---|---  
  
 **type**

|

string

|

The **type** property identifies the type of STIX Object. The value of the
**type** property **MUST** be the name of one of the types of STIX Objects
defined in sections 4, 5, 6, and 7(e.g., indicator) or the name of a Custom
Object as defined by section 11.2.  
  
 **spec_version**

|

string

|

The version of the STIX specification used to represent this object.

The value of this property **MUST** be 2.1 for STIX Objects defined according
to this specification.

If objects are found where this property is not present, the implicit value
for all STIX Objects other than SCOs is 2.0. Since SCOs are now top-level
objects in STIX 2.1, the default value for SCOs is 2.1.  
  
 **id**

|

identifier

|

The **id** property uniquely identifies this object.

For objects that support versioning, all objects with the same **id** are
considered different versions of the same object and the version of the object
is identified by its **modified** property.  
  
 **created_by_ref**

|

identifier

|

The **created_by_ref** property specifies the **id** property of the identity
object that describes the entity that created this object.

If this attribute is omitted, the source of this information is undefined.
This may be used by object creators who wish to remain anonymous.  
  
 **created**

|

timestamp

|

The **created** property represents the time at which the object was
originally created.

The object creator can use the time it deems most appropriate as the time the
object was created. The minimum precision **MUST** be milliseconds (three
digits after the decimal place in seconds), but **MAY** be more precise.

The **created** property **MUST NOT** be changed when creating a new version
of the object.

See section 3.6for further definition of versioning.  
  
 **modified**

|

timestamp

|

The **modified** property is only used by STIX Objects that support versioning
and represents the time that this particular version of the object was last
modified.

The object creator can use the time it deems most appropriate as the time this
version of the object was modified. The minimum precision **MUST** be
milliseconds (three digits after the decimal place in seconds), but **MAY** be
more precise.

If the **created** property is defined, then the value of the **modified**
property for a given object version **MUST** be later than or equal to the
value of the **created** property.

Object creators **MUST** set the **modified** property when creating a new
version of an object if the **created** property was set.

See section 3.6for further definition of versioning.  
  
 **revoked**

|

boolean

|

The **revoked** property is only used by STIX Objects that support versioning
and indicates whether the object has been revoked.

Revoked objects are no longer considered valid by the object creator. Revoking
an object is permanent; future versions of the object with this **id** **MUST
NOT** be created.

The default value of this property is false.

See section 3.6for further definition of versioning.  
  
 **labels**

|

list of type string

|

The **labels** property specifies a set of terms used to describe this object.
The terms are user-defined or trust-group defined and their meaning is outside
the scope of this specification and **MAY** be ignored.

Where an object has a specific property defined in the specification for
characterizing subtypes of that object, the labels property **MUST NOT** be
used for that purpose.

For example, the Malware SDO has a property **malware_types** that contains a
list of Malware subtypes (dropper, RAT, etc.). In this example, the labels
property cannot be used to describe these Malware subtypes.  
  
 **confidence**

|

integer

|

The **confidence** property identifies the confidence that the creator has in
the correctness of their data. The confidence value **MUST** be a number in
the range of 0-100.

Appendix Acontains a table of normative mappings to other confidence scales
that **MUST** be used when presenting the confidence value in one of those
scales.

If the confidence property is not present, then the confidence of the content
is unspecified.  
  
 **lang**

|

string

|

The **lang** property identifies the language of the text content in this
object. When present, it **MUST** be a language code conformant to [RFC5646].
If the property is not present, then the language of the content is en
(English).

This property **SHOULD** be present if the object type contains translatable
text properties (e.g. name, description).

The language of individual fields in this object **MAY** be overridden by the
**lang** property in granular markings (see section 7.2.3).  
  
 **external_references**

|

list of type external-reference

|

The **external_references** property specifies a list of external references
which refers to non-STIX information. This property is used to provide one or
more URLs, descriptions, or IDs to records in other systems.  
  
 **object_marking_refs**

|

list of type identifier

|

The **object_marking_refs** property specifies a list of **id** properties of
marking-definition objects that apply to this object.

In some cases, though uncommon, marking definitions themselves may be marked
with sharing or handling guidance. In this case, this property **MUST NOT**
contain any references to the same Marking Definition object (i.e., it cannot
contain any circular references).

See section 7.2for further definition of data markings.  
  
 **granular_markings**

|

list of type granular-marking

|

The **granular_markings** property specifies a list of granular markings
applied to this object.

In some cases, though uncommon, marking definitions themselves may be marked
with sharing or handling guidance. In this case, this property **MUST NOT**
contain any references to the same Marking Definition object (i.e., it cannot
contain any circular references).

See section 7.2for further definition of data markings.  
  
 **defanged**

|

boolean

|

This property defines whether or not the data contained within the object has
been defanged.

The default value for this property is false.

This property **MUST NOT** be used on any STIX Objects other than SCOs.  
  
 **extensions**

|

dictionary

|

Specifies any extensions of the object, as a dictionary.

Dictionary keys **SHOULD** be the id of a STIX Extension object or the name of
a predefined object extension found in this specification, depending on the
type of extension being used.

The corresponding dictionary values **MUST** contain the contents of the
extension instance.

Each extension dictionary **MAY** contain the property **extension_type**. The
value of this property **MUST** come from the extension-type-enum enumeration.
If the **extension_type** property is not present, then this is a predefined
extension which does not use the extension facility described in section 7.3.
When this extension facility is used the **extension_type** property **MUST**
be present.  
  
下表列出了所有常见属性，以及如何将它们用于各个类型的 STIX 对象。下表信息作为参考，最终以规范正文为准。

 ****

|

 **STIX Core Objects**

|

 **STIX Meta Objects**

|

 ****  
  
---|---|---|---  
  
 **Property Name**

|

 **SDOs**

|

 **SROs**

|

 **SCOs**

|

 **Extension**

|

 **Language**

|

 **Markings**

|

 **Bundle**  
  
 **type**

|

Required

|

Required

|

Required

|

Required

|

Required

|

Required

|

Required  
  
 **spec_version**

|

Required

|

Required

|

Optional

|

Required

|

Required

|

Required

|

N/A  
  
 **id**

|

Required

|

Required

|

Required

|

Required

|

Required

|

Required

|

Required  
  
 **created_by_ref**

|

Optional

|

Optional

|

N/A

|

Required

|

Optional

|

Optional

|

N/A  
  
 **created**

|

Required

|

Required

|

N/A

|

Required

|

Required

|

Required

|

N/A  
  
 **modified**

|

Required

|

Required

|

N/A

|

Required

|

Required

|

N/A

|

N/A  
  
 **revoked**

|

Optional

|

Optional

|

N/A

|

Optional

|

Optional

|

N/A

|

N/A  
  
 **labels**

|

Optional

|

Optional

|

N/A

|

Optional

|

Optional

|

N/A

|

N/A  
  
 **confidence**

|

Optional

|

Optional

|

N/A

|

N/A

|

Optional

|

N/A

|

N/A  
  
 **lang**

|

Optional

|

Optional

|

N/A

|

N/A

|

N/A

|

N/A

|

N/A  
  
 **external_references**

|

Optional

|

Optional

|

N/A

|

Optional

|

Optional

|

Optional

|

N/A  
  
 **object_marking_refs**

|

Optional

|

Optional

|

Optional

|

Optional

|

Optional

|

Optional

|

N/A  
  
 **granular_markings**

|

Optional

|

Optional

|

Optional

|

Optional

|

Optional

|

Optional

|

N/A  
  
 **defanged**

|

N/A

|

N/A

|

Optional

|

N/A

|

N/A

|

N/A

|

N/A  
  
 **extensions**

|

Optional

|

Optional

|

Optional

|

N/A

|

Optional

|

Optional

|

N/A  
  
## 3.3. 对象 ID 和引用 ——Object IDs and References

所有 STIX 对象和 STIX 包对象都有一个 **id** 属性，该属性标识在每个实例对象中都是唯一的。此 **id** **必须**
满足identifier类型的要求（请参阅第 2.9 节）。

identifier类型还用作 ID 引用，以定义指向其他 STIX 对象的关联关系。“解析 ID
引用”是通过识别和获取“ID引用属性”所引用实际对象的过程。当 ID 引用属性（例如， **created_by_ref** ）的值与另一个对象的
**id** 属性完全匹配时，ID 引用将解析为对象。如果消费者可以访问对象的多个版本，则消费者 **应当** 将“对象的任何引用”解释为第 3.6
节中定义的最新版本。“ID 引用”可以引用消费者/生产者当前可能没有生成的对象。此规范不涉及 ID 引用解析的实现。

某些ID引用（嵌入关系）可能限于对象类型的子集，如关系定义的属性描述中所指定的。例如， **object_marking_refs**
公共属性指定“关系的唯一有效目标”是“一个或多个marking-definition对象”。

## 3.4. SCO确定性ID创建 ——SCO Deterministic ID Creation

为了确保 STIX 网络可观测对象 （SCOs） 的确定性 IDs，每个 SCO 定义了一组或多个名为“ID Contributing
Properties”的属性。这些属性 **可以** 用于创建 SCO 时 **id** 的默认计算。在某些情况下，每个 SCO 上列出的“ID
Contributing Properties”部分中可能会描述有助于 ID选择的其他扩展属性。基于这些命名属性创建 SCO ID 的默认算法是第 2.9
节中定义的 UUIDv5，但是， **可以** 使用其他用于创建 SCO ID 的算法。

本规范中包含的示例 SCOs 中的确定性 IDs （UUIDv5） 是使用第 2.9 节中定义的算法计算的。们已尽一切努力使这些 IDs
准确无误。示例的“引用属性”中使用的某些 IDs 不包括实际对象，因此无法准确计算适当的 UUIDv5值。在这些情况下，生成了 UUIDv4值。

## 3.5. 对象创建 ——Object Creator

对象创建者是为给定对象生成 **id** 属性的实体（例如，系统、组织、工具实例）。对象创建者表示为 Identity 对象。某些 STIX
对象允许此指定（请参阅第3.2节）。 **应在** **created_by_ref** 属性中捕获与表示“对象创建者”的 Identity
对象的“嵌入关系”（或者可以省略该属性，这意味着对象创建者是匿名的）。

从“另一个实体”重新发布对象而不对对象进行任何更改，从而保持原始 **id** 的实体不必考虑对象创建者， **不得** 变更
**created_by_ref** 属性。实体对象接受修改、增补或省略变更后重新发布时，必须为对象创建一个新
ID。出于版本控制的目的，它们被视为新对象的object creator。

## 3.6. 版本控制 ——Versioning

版本控制是对象创建者用来更新和撤销他们创建的STIX对象的机制。本节描述了版本化过程以及执行版本化和撤销的标准规则。版本化的STIX对象 **必须**
使用属性名称 **created_by_ref** 、 **created** 、 **modified** 和 **revoked**
。SCOs没有版本控制，因此没有这四个版本控制属性，有关这些属性的完整定义和规范用法，请参见第3.2节中的属性表。

对STIX对象进行版本控制 **可以** 更新、添加或移除信息。STIX对象的版本由其 **id** 和 **modified**
属性的组合来唯一标识。对象的第一个版本 **created** 和 **modified** 属性时间戳 **必须** 相同。 **modified**
属性的较新值表示该对象的较新版本。实现中 **必须** 将具有最新 **modified**
值的STIX对象的版本视为对象的最近状态。对于对象的每个新版本， **必须** 更新 **modified**
属性以表示新版本的创建时间。如果消费者收到两个不同的对象，但具有相同的 **id** 和 **modified**
时间戳，没有定义消费者如何处理这些对象。该规范没有说明在实现中应该如何处理非最新版本的对象。

STIX对象只有一个对象创建者，即生成对象 **id** 并创建第一个版本的实体。对象创建者可以(但不绝对)在对象的 **created_by_re**
f属性中标识。只有对象创建者才能创建STIX对象的新版本。除对象创建者之外的生产者 **不得**
创建该对象的新版本。如果对象创建者之外的生产者希望创建新版本，则 **必须** 用新 **id** 创建新对象。此外还 **应该**
创建一个derived-from Relationship对象，将新对象与其派生自的原始对象相关联。

对象版本的每个表示(每次对象版本被序列化和共享时) (由对象的 **id** 和 **modified** 属性标识) **必须**
始终具有相同的属性集且每个属性的值相同。如果一个属性具有与默认值相同的值，它 **可以**
从表示中省略，这并不表示对对象的更改。为了改变任何属性的值，或者添加或移除属性，修改后的属性必须随着改变的时间而更新，以标识为新的版本。

对象也可以被撤销，这意味着它们不再被对象创建者认为是有效的。与发布新版本一样，只有对象创建者可以撤销STIX对象。 **revoked**
属性中的true值表示对象(包括当前版本和所有以前的版本)已被吊销。撤销是永久性的:一旦对象被标记为撤销，就 **不能** 再创建该对象的后续版本。更改
**revoked** 属性以指示对象已被吊销是对该对象的更新，因此 **必须** 同时更新其 **modified**
属性。该规范没有说明实现中应该如何处理被撤销的数据。

应该注意的是，如果生产者对 SCO 进行版本控制（为这四个属性分配值），则不允许其他生产者使用相同的 **id** 创建或修改相同的 SCO，因为这将与
STIX2 中定义的严格版本控制规则相冲突。因此，为了协同和共享，版本控制下SCOs的生产者 **不得**
使用默认名称空间进行确定性ID创建。否则，多个不同的生产商如果生产相同的SCO情报，就会相互冲突。

 ****

### 3.6.1. 版本时间戳 ——Versioning Timestamps

有两个时间戳属性用于指示创建和修改 STIX 对象的时间： **created** 和 **modified** 。 **created**
属性指示创建对象的第一个版本的时间。 **modified** 的属性指示创建对象特定版本的时间。 **modified** 时间 **不得** 早于
**created** 时间。

此规范没有解决实现中应如何确定创建和修改时间的值以用于 **created** 和 **modified**
属性的细节（例如，一个系统可能使用对象首次添加到本地数据库的时间作为创建时间，而另一个系统可能使用对象首次作为 STIX 分发的时间）。

### 3.6.2. 新版本还是新对象？ ——New Version or New Object?

最终，实现中将遇到这样一种情况：必须决定是否更改现有对象的新版本，还是有足够的差异以至于创建新的对象。这通常被认为是数据质量问题，因此本规范不提供任何规范性约束。

但是，为了辅助实现并促进实现之间的一致性，提供了一些经验法则。当变化表明对象的意义发生了实质性变化时，都应使用具有不同 **id**
的新对象。实质性变更是指对象创建者认为会实质性改变对象含义的任何变更。例如，对象创建者可能会认为将威胁源从一个国家更改为另一个国家是实质性更改。这些决策始终由对象创建者做出。当决定是否为实质性变更时，对象创建者也应该考虑与对象的关系。如果变更会使与对象的关系的效用失效，则变更被视为重大变更，应使用新的对象
**id** 。

 **Examples**

Example of a new version

One object creator has decided that the previous name they used for an SDO is
incorrect. They consider that change as an update to the object.

Note: the IDs in the example below use a simplified format to help illustrate
the changing IDs more clearly.

 **Step #**

|

 **STIX Object**

|

 **Object Creator Action**  
  
---|---|---  
  
1

|

{

"type": "example",

"id": "example--1",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-01T06:13:14.000Z",

"name": "attention",

"description": "this is the description"

}

|

Original version of an object is created.  
  
2

|

N/A, STIX is not involved in this step

|

Object creator changes the name in their internal database.  
  
3

|

{

"type": "example",

"id": "example--1",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-08T03:43:44.000Z",

"name": "Attention!",

"description": "this is the description"

}

|

Object creator updates the **modified** property.  
  
Example of derived object

One object creator has decided that the previous name they used for an SDO is
incorrect. They consider that change fundamental to the meaning of the object
and therefore revoke the object and issue a new one.

 ****

 **Step #**

|

 **STIX Object**

|

 **Object Creator Action**  
  
---|---|---  
  
1

|

{

"type": "example",

"id": "example--2",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-01T06:13:14.000Z",

"name": "attention",

"description": "this is the description"

}

|

Original object created (via new id and setting **created** and **modified**
to the same value).  
  
2

|

N/A, STIX is not involved in this step

|

Object creator changes the name in their internal database.  
  
3

|

{

"type": "example",

"id": "example--2",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-08T03:43:44.000Z",

"name": "attention",

"description": "this is the description",

"revoked": true

}

|

Object creator revokes the existing object by setting **revoked** to true. The
**modified** property is updated.  
  
4

|

{

"type": "example",

"id": "example--3",

"created": "2016-05-08T03:43:44.000Z",

"modified": "2016-05-08T03:43:44.000Z",

"name": "Something completely different",

"description": "this is the description"

}

|

Object creator creates a new object (with a new **id** and setting **created**
and **modified** to the same value).  
  
5

|

{

"type": "relationship",

"id": "relationship--4",

"created": "2016-05-08T03:43:44.000Z",

"modified": "2016-05-08T03:43:44.000Z",

"relationship_type": "derived-from",

"source_ref": "example--2",

"target_ref": "example--3"

}

|

(Optional) Object creator creates a new Relationship indicating that the new
object is derived from the old object.  
  
 ****

Example of consumer workflow

This section describes an example workflow where a consumer receives multiple
updates to a particular object. (In this example, the STIX Objects have been
truncated for brevity.)

 **Step #**

|

 **Received STIX Object**

|

 **Recipient Action**  
  
---|---|---  
  
1

|

{

"type": "example",

"id": "example--5",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-01T06:13:14.000Z"

}

|

Consumer stores example object because this is the first time they have seen
the object.  
  
2

|

{

"type": "example",

"id": "example--5",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-08T03:43:44.000Z"

}

|

Consumer updates example object because the received **modified** property is
later than the object that is currently stored.

 ****  
  
3

|

{

"type": "example",

"id": "example--5",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-06T06:23:45.000Z"

}

|

Consumer ignores this object because they already have a newer version of the
object.

Note: consumer might choose to store meta-information about received objects,
including versions that were received out-of-order. The consumer also may
choose to store a copy for reference.  
  
4

|

{

"type": "example",

"id": "example--5",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-11T06:41:21.000Z",

"revoked": true

}

|

Consumer receives revoked version and decides to delete example object but
keeps some metadata regarding the object.  
  
5

|

{

"type": "example",

"id": "example--5",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-10T17:28:54.000Z"

}

|

Consumer ignores this object because they already have a newer version of the
object (the revoked version).  
  
​

Example of object creator workflow

This section describes an example workflow where an object creator publishes
multiple updates to a particular object. This scenario assumes a human using a
STIX implementation. (In this example, the STIX Objects have been truncated
for brevity.)

 **Step #**

|

 **STIX Object**

|

 **User Action**  
  
---|---|---  
  
1

|

N/A – STIX is not involved in this scenario.

(Tools could choose to create and track STIX versions for internal changes,
but it is not required by the specification.)

|

User clicks a create button in the user interface, creates an SDO, then clicks
save. This action causes information to be stored in the product’s database.  
  
2

|

{

"type": "example",

"id": "example--6",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-01T06:13:14.000Z"

}

|

The user clicks the "share" button, delivering the intelligence to sharing
partners.  
  
3

|

N/A – STIX is not involved in this scenario.

(Tools could choose to create and track STIX versions for internal changes,
but it is not required by the specification.)

|

The user performs additional analysis within the STIX implementation,
performing multiple modifications and saving their work multiple times.  
  
4

|

{

"type": "example",

"id": "example--6",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-03T16:33:51.000Z"

}

|

The user, happy with the status of their work, decides to provide an update to
some properties of the previously published object (not shown).  
  
5

|

{

"type": "example",

"id": "example--6",

"created": "2016-05-01T06:13:14.000Z",

"modified": "2016-05-08T13:35:12.000Z",

"revoked": true

}

|

The user receives lots of negative feedback regarding the quality of their
work and decides to retract the object by pressing the "revoke" button.  
  
## 3.7. 通用关系 ——Common Relationships

每个SDO和SCO都有自己的一组关系类型，这些关系类型是在该SDO或SCO的定义中规定的。以下是为所有SDOs和SCOs定义的常见关系类型。关于关系类型的更多信息见1.2.4节。

 **Relationship Type**

|

 **Source**

|

 **Target**

|

 **Description**  
  
---|---|---|---  
  
derived-from

|

<SDO or SCO of same type as target>

|

<SDO or SCO of same type as source>

|

The information in the target object is based on information from the source
object.

derived-from is an explicit relationship between two separate objects and
**MUST NOT** be used as a substitute for the versioning process defined in
section 3.6.  
  
duplicate-of

|

<SDO or SCO of same type as target>

|

<SDO or SCO of same type as source>

|

The referenced source and target objects are semantically duplicates of each
other.

This specification does not address whether the source or the target object is
the duplicate object or what action, if any, a consumer should take when
receiving an instance of this relationship.

As an example, a Campaign object from one organization could be marked as a
duplicate-of a Campaign object from another organization if they both
described the same campaign.  
  
related-to

|

<SDO or SCO of any type>

|

<SDO or SCO of any type>

|

Asserts a non-specific relationship between two SDOs. This relationship can be
used when none of the other predefined relationships are appropriate, and a
user-defined one is not needed.

As an example, a Malware object describing a piece of malware could be marked
as a related-to a Tool if they are commonly used together. That relationship
is not common enough to standardize but may be useful to some analysts.  
  
## 3.8. 保留名称 ——Reserved Names

本节定义了为将来修订本文档所保留的属性名称。本节中定义的属性名称和任何标记为RESERVED的属性名称， **不得** 用于任何自定义属性的名称，也
**不得** 出现在符合本规范版本的任何STIX内容中。

当前在所有STIX对象中保留的属性有:

  * severity
  * username
  * phone_number
  * action

## 3.9. 对象属性元数据 ——Object Property Metadata

### 3.9.1. SCO字符串编码 ——SCO String Encoding

捕获观测中的特定STIX网络可观测对象(SCO)字符串编码有助于归因、创建指标和相关用例。STIX
网络可观测对象中的某些“字符串属性”可能包含具有相同基本名称和后缀 **_enc** 的附加同级属性，用于所捕获属性值的原始observed
encoding名称。所有 **_enc** 属性都 **必须** 使用 IANA 字符集注册表[Character
Sets]中的相应名称指定其编码。如果定义了字符集的首选 MIME 名称，则 **必须** 使用此值；如果未定义，则 **必须** 改用注册表中的 Name
值。

 **Examples**

File with Unicode representation of the filename and a corresponding encoding
specification

{

"type": "file",

"id": "file-1389b98d-a3d3-5190-a996-716fd444059a",

"hashes": {

"SHA-256": "effb46bba03f6c8aea5c653f9cf984f170dcdd3bbbe2ff6843c3e5da0e698766"

},

"name": "quêry.dll",

"name_enc": "windows-1252"

}

## 3.10. 预定义对象扩展 ——Predefined Object Extensions

预定义对象扩展在 STIX 网络可观测对象 （SCOs） 中具有特定用途：定义基本之外的相关属性集，例如，网络流量对象的 HTTP 请求信息。因此，每个
SCO 可以包括一个或多个预定义对象扩展。

每个预定义对象扩展最多可以在给定的 SCO 上定义一次。在可观测对象实例中，每个扩展都在 **extensions**
属性下指定，该属性的类型为dictionary。请注意，这意味着每个扩展都是通过 extensions
属性中的相应键指定的。例如，在文件对象实例中指定时，将使用 ntfs-ext 的键值指定 NTFS 扩展名。

 **Examples**

Basic File with NTFS Extension

{

"type": "file",

"spec_version": "2.1",

"id": "file--1b40e321-ae73-5637-bd97-33c35a86b80d",

"hashes": {

"MD5": "3773a88f65a5e780c8dff9cdc3a056f3"

},

"size": 25537,

"extensions": {

"ntfs-ext": {

"sid": "1234567"

}

}

}

  

