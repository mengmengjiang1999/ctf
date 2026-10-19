[Cisco Talos](https://blog.talosintelligence.com/2021/08/rat-campaign-targets-latin-america.html)先前观察到一组针对拉丁美洲国家的新型态的电子邮件攻击活动，攻击者利用开放文件格式（Open Document
Format，简称ODF）的恶意软体进行攻击，这些活动使用大量感染组件来传播两种广受欢迎的套装恶意软体和远端访问木马工具 (RAT)：njRAT 和
AsyncRAT。其攻击行为针对拉丁美洲的旅游及旅馆组织。也发现到基于 .NET
的感染链产生器/二进制文件加密器，用于生成近期活动中使用的恶意感染组件，包括针对拉丁美洲的攻击。此类产生器表明作者打算捆绑恶意软体进行攻击，以便运营商、客户和附属机构轻松部署和利用。

这些活动包括启用巨集的 Office 文件，这些文件充当感染的切入点。接下来是 PowerShell 和 VB
脚本的模组链，所有这些都致力于禁用AMSI等防病毒保护功能并最终交付 RAT 有效负载。

此外[HP Wolf Security](https://threatresearch.ext.hp.com/stealthy-opendocument-malware-targets-latin-american-hotels/)也在后续侦测到相关的行为，攻击者利用OpenDocument的格式伪装与旅馆联系的相关文件，诱使攻击目标的人员点选相关附件并进行附载的交付，进而利用PowerShell和VB
Script来进行相关攻击。

![1662996928_631f51c08400dffdd1c37.png!small](https://image.3001.net/images/20220912/1662996928_631f51c08400dffdd1c37.png!small)

图片来源：HP Wolf Security

如HP Wolf Security于文章中描述到的攻击传播链。

恶意文件利用电子邮件附件发送。如果用户打开文件，他们会看到一个提示，询问是否应该更新引用其他文件的字段。如果他们对此讯息单击 “是”，则会打开一个
Excel 文件。

![1662996962_631f51e2f36035dfc2331.png!small](https://image.3001.net/images/20220912/1662996962_631f51e2f36035dfc2331.png!small)

图片来源：HP Wolf Security

之后，向用户显示另一个提示，询问是否应该启用或禁用巨集。如果用户允许使用巨集，则会触发传播链，最终导致恶意软体有效负载[AsyncRAT](https://malpedia.caad.fkie.fraunhofer.de/details/win.asyncrat)的执行。

![1662996997_631f5205b1750ceb63b72.png!small](https://image.3001.net/images/20220912/1662996997_631f5205b1750ceb63b72.png!small)

图片来源：HP Wolf Security

文中提到：看到 OpenDocument
文件被用来分发恶意软体很有趣，因为我们很少在野外看到使用这种文件格式的恶意软体。引人注目的是，防病毒扫描程序检测不到该活动中使用的文件类型，[截至 7 月
7 日，VirusTotal 的检测率为
0%](https://www.virustotal.com/gui/file/74d8bc5023f8d56e5b9fb46a5da5f1ce7e3e04826ca543274d7f6205866490b9)。

![1662997039_631f522f325b9e7c28723.png!small](https://image.3001.net/images/20220912/1662997039_631f522f325b9e7c28723.png!small)

这是很特别的一个现象，我们可以从[HP Wolf
Security的文章](https://threatresearch.ext.hp.com/stealthy-opendocument-malware-targets-latin-american-hotels/)中了解更多细节，那么对于企业所面临的威胁可以怎么有效的进行防护呢？

首先，我们要了解现有安全产品的防护机制，对于侦测不到的威胁是否有足够的能力进行防护，于先前的文章中[防病毒对电子邮件安全有效吗？](https://www.opswat.com/blog/is-anti-virus-effective-for-email-security)提到的相关描述我们可以了解到几点：

  * 现阶段， [每小时出现 14,000 个新恶意软体](https://portal.av-atlas.org/malware)
  * 一些 AV 引擎以长达 2 到 16 小时或一整天的巨大间隔更新
  * 多型态产生器[可以隐藏](https://ivanlef0u.fr/repo/madchat/vxdevl/vdat/polyinvr.htm)来自 AV 扫描的实际病毒

鉴于上述数据， [91% 的网路攻击从电子邮件开始](https://blog.knowbe4.com/bid/252429/91-of-cyberattacks-begin-with-spear-phishing-email)并仍然是恶意行为者的最大攻击媒介也就不足为奇了，因为它便宜、易于使用，并且为组织提供了直接的通信管道。要了解为什么恶意软体仍然如此成功以及恶意行为者如何将其有害脚本/内容传递到用户邮箱，请参阅
[用于发布它们的主要附件类型列表：](https://press.hp.com/us/en/press-releases/2021/hp-wolf-security-threat-insights-report-q321.html)

  * 压缩文件（从26% 上升到 38%），
  * Word 文件（23% – RTF 文档 38%），
  * 电子表单 (17%),
  * 可执行文件 (16%)

看到这里，我们也可以很明显的看到对于长久以来的侦测，并没有此次攻击所使用的档案类型，这也是此攻击型态独特的地方，我们或许开始思考针对这样类型的档案进行控制及封锁，但不幸的是永远没有完整的档案类型清单我们可以进行控制。

2022年3月，日本总务省发布了[地方政府信息安全政策指引](https://www.soumu.go.jp/main_content/000805453.pdf)，该安全政策指引中提到LGWAN
(Local Government Wide Area Network) 需注意的关键事项，注意危险因子去除的重要性。

  * ファイルからテキストのみを抽出（仅从档案中提取文件本文）
  * サービス等を活用してサニタイズ处理（ファイルを一旦分解した上で危険因子を除去した后、ファイルを再构筑し、分解前と同様なファイル形式に复元する）采用档案净化技术 (移除威胁因子、重建档案、拆解档案并恢复档案原有格式)

![1662996893_631f519d16f986aeef5be.png!small](https://image.3001.net/images/20220912/1662996893_631f519d16f986aeef5be.png!small)

此项指引显著的表示需要更有效的控制相关邮件及档案传输安全，其中CDR的技术就特别的重要，当档案经过CDR的清洗后，使用者所接触到的档案，就不再具有威胁，CDR的关键技术可以将相关武器化的档案进行无毒化动作，包含：巨集、连结和内嵌(OLE)
物件或是存在于图片、影片中的物件等等。

![](https://image.3001.net/images/20220912/1662997168_631f52b09c1083c50d5fc.png!small)

另外，我们也可以利用沙箱技术针对未知的威胁进行动态分析，只不过沙箱的处理时间会依照不同的需求而有着不同的回应时间，对于邮件及档案传输的过程中往往会造成延迟的问题，这也是Gartner提到的，利用CDR的技术来避免恶意软体规避沙箱检测的技术及补充其不足的问题。

![](https://image.3001.net/images/20220912/1662997219_631f52e34ec5f0a79f32d.png!small)

但并非沙箱就是一个不好的解决方案，可以透过CDR整合现有的沙箱技术，透过CDR及MultiScanning的技术所侦测到的问题档案，可以再转送到沙箱或是EDR进行分析，如此一来对于事前、事中及事后的阶段就会有一个完整的蓝图出现。您可以参考[CDR的选择指南](https://info.opswat.com/zh-tw/content-disarm-and-reconstruction-cdr-selection-guide-ch)，了解到CDR技术的细节。

参考资料：

<https://blog.talosintelligence.com/2021/08/rat-campaign-targets-latin-america.html>

[https://threatresearch.ext.hp.com/stealthy-opendocument-malware-targets-latin-american-hotels/#](https://threatresearch.ext.hp.com/stealthy-opendocument-malware-targets-latin-american-hotels/)

<https://www.opswat.com/blog/how-do-you-treat-email-attachments>

<https://www.opswat.com/blog/is-anti-virus-effective-for-email-security>

