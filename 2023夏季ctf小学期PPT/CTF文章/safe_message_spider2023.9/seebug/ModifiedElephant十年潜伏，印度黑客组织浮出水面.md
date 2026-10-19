**译者：知道创宇404实验室翻译组  
原文链接：<https://assets.sentinelone.com/sentinellabs-apt/modified-elephant-apt>**

## 摘要

  * 我们的研究将这十年的活动迹象归因于一种我们称之为ModifiedElephant的黑客组织。 

  * ModifiedElephant对印度各地的人权活动家、人权捍卫者、学者和律师进行有针对性的攻击，目的是栽赃可以定罪的电子证据。 

  * ModifiedElephant至少从 2012 年开始运作，并多次针对特定的人群。 

  * ModifiedElephant通过使用商业上可用的远程访问木马(rat)进行操作，并且与商业监视行业有潜在的联系 

  * 威胁者利用恶意文件的鱼叉式网络钓鱼来传送恶意软件，如 NetWire、 DarkComet，以及基础设施重叠的简易键盘记录程序，这让我们能够联想到很久以前未知的恶意活动。

## 背景

2021 年 9 月，SentinelLabs 发表了对土耳其 nexus
黑客的行动的研究，我们称之为”[EGoManiac](http://https://www.sentinelone.com/labs/egomaniac-an-unscrupulous-turkish-nexus-threat-actor/
"EGoManiac")”，我们注意到他们在记者系统中植入有罪证据，给土耳其国家警察逮捕他们提供正当理由。黑客主动陷害和监禁易受攻击的对手的威胁行为者，是网络威胁现象中一个被严重低估的方面，这引发了作为证据的设备的完整性的问题，令人不安。在一个不相关的[案件](http://https://www.washingtonpost.com/world/asia_pacific/india-bhima-koregaon-activists-jailed/2021/02/10/8087f172-61e0-11eb-a177-7765f29a9524_story.html
"案件")中，新出现的细节引起了我们的注意，作为一个潜在的类似情景，它值得更多的审查。

2018 年 1 月 1 日，印度长期存在的种族和政治紧张局势激化，政府的批评者与亲政府的支持者在 [Bhima
Koregaon](http://https://www.theguardian.com/world/2021/aug/12/bhima-koregaon-case-india-conspiracy-modi "Bhima Koregaon")
附近发生冲突。这一事件引发了随后的抗议活动，导致了更多的暴力事件和至少一人死亡。

在接下来的几个月里，Maharashtra 警方将暴力事件的起因与印度被禁的纳萨尔派-毛主义共产党联系起来。2018 年 4 月 17
日，警方进行了突击搜查，并以恐怖主义相关罪名逮捕了一些人。逮捕机构在被告的电脑系统中发现了涉嫌犯罪的文件，包括涉嫌企图谋杀总理莫迪的计划。

由于Arsenal咨询公司公布了数字检测调查结果以及之后会提到的结果，我们可以收集到一些被告者系统的完整性的罕见见解，并掌握犯罪文件的来源。事实证明，被告设备系统的入侵导致了栽赃文件，这些文件后来被用作恐怖主义的证据和被告者被监禁的理由。这些入侵并不是孤立的事件。

我们对这些入侵的研究揭示了十年来针对特定群体和个人的持续恶意行为，我们现在归咎于一个以前未知的 黑客组织，它名为
ModifiedElephant。这个组织已经运作多年，由于他们的运作范围并不大，他们的工具也不起眼，以及他们只针对区域特定的目标，因而逃过了研究者的关注和检测。在本文撰写之时，ModifiedElephant
仍处于活跃状态。

## 目标和目的

ModifiedElephant 的目标是进行长期监视，在方便协调的逮捕行动之前交付”证据”——指控目标犯有特定罪行的档案。

在仔细回顾过去十年的攻击活动后，我们已经确定了 ModifiedElephant
网络钓鱼活动针对的数百个组织和个人。在印度，活动家、人权捍卫者、记者、学者和法律专业人士是最容易成为攻击目标。值得注意的目标包括与 Bhima
koregan 案件有关的人士。

## 感染行为

在过去的十年里，ModifiedElephant 操作员试图通过恶意文件附件的鱼叉式电子邮件来感染他们的目标，他们的技术随着时间的推移而发展。
他们的主要传输机制是恶意的 Microsoft Office
文档文件，当时这些文件被武器化，用来传输恶意软件。特定的有效载荷随着时间的推移和不同目标的变化而变化。然而，仍然存在一些值得注意的趋势。

  * 在 2013 年中期，黑客使用了包含可执行文件附件的仿冒双扩展的钓鱼邮件(filename.pdf.exe)。
  * 2015 年之后，参与者尝试使用不太明显的包含公开可用漏洞的文件，例如 .doc, .pps, .docx, .rar和密码保护的 Rar 文件。这些尝试涉及合法的引诱文件，使用.pdf, .docx, 和 .mht 格式，以吸引目标的注意力，同时执行恶意软件。
  * 在 2019 年的网络钓鱼活动中，ModifiedElephant 操作者也采取了提供链接到外部托管文件的方法，供受害者手动下载和执行。
  * Amnesty首次[公开指出](http://https://www.amnesty.org/en/latest/research/2020/06/india-human-rights-defenders-targeted-by-a-coordinated-spyware-operation/ "公开指出")的这种活动的一个子集，攻击者使用了大量.Rar 存档(高达 300mb)，可能是为了绕过检测。

我们观察到，诱饵文件反复使用
[CVE-2012-0158](http://https://nvd.nist.gov/vuln/detail/cve-2012-0158
"CVE-2012-0158")、
[CVE-2014-1761](http://https://nvd.nist.gov/vuln/detail/CVE-2014-1761
"CVE-2014-1761")、 [CVE-2013-3906](http://https://msrc-blog.microsoft.com/2013/11/05/cve-2013-3906-a-graphics-vulnerability-exploited-through-word-documents/ "CVE-2013-3906")、
[CVE-2015-1641](http://https://nvd.nist.gov/vuln/detail/CVE-2015-1641
"CVE-2015-1641")，利 用它们植入并执行自己选择的恶意软件。
钓鱼邮件和诱饵附件的标题和主题通常是与被害者相关的话题，如激进主义新闻和团体，全球和地方事件的气候变化，政治和公共服务。2021
年初，Arsenal咨询公司公开了了对 2014
年两封钓鱼邮件的[公开解析](http://https://web.archive.org/web/20210421135320/https://twitter.com/ArsenalArmed/status/1384867766675595264
"公开解析")。

![](https://images.seebug.org/content/images/2022/02/87fa2d5b-8a20-45af-bb52-ad2efa4819b2.png-w331s) 图1:包含来自 ModifiedElephant 的恶意附件的鱼叉式钓鱼电子邮件

ModifiedElephant 不断地使用免费的电子邮件服务提供商，如 Gmail 和
Yahoo，来进行他们的活动。钓鱼邮件采取了许多方法来伪装合法性的外表，包括具有转发历史的虚假主体内容，其中包含长长的收件人列表，原始的电子邮件收件人列表中有许多看似虚假的账户，或者只是使用新的电子邮件或诱饵文件多次重新发送恶意软件。值得注意的是，在特定的攻击中，参与者会特别固执，并试图在一天内多次攻击同一个对象。
通过回顾攻击者活动的时间线，我们可以观察到攻击者多年来轮换基础设施的明显趋势。

![](https://images.seebug.org/content/images/2022/02/507d91f9-5d32-4300-a6b6-8e9810eb6b8f.png-w331s)
图 2: ModifiedElephant 和 SideWinder C2 基础设施的时间轴示例

例如，从 2013 年初到 2016 年中，可以描绘一个相当明确的时间表，几乎没有
时间上的重叠，表明攻击活动可能进化或扩大范围。日期是基于观察到的发送与给定域交流的样本中第一个和最后一个钓鱼邮件的日期。值得注意的是，在这张图中，一个独立的印度nexus黑客组织
SideWinder与 ModifiedElephant 一起出现，我们发现，他们在针对同一个目标。

## 工具的选择

ModifiedElephant
最常使用的恶意软件并不复杂，而且非常普通，但事实证明它足以满足其目标——获得远程访问和对受害者机器的无限制控制。部署的主要恶意软件家族是 NetWire 和
DarkComet 远程访问木马(RATs)。这两种“ RATs”都是公开的，并且由于技术和能力方面出众，黑客长期使用。

一项特别攻击是围绕 **_Ltr_1804_to_cc.pdf_** 文件展开的，该文件包含针对莫迪总理的暗杀阴谋的细节。Arsenal
咨询公司的一份检测报告显示，这份文件是警方获得的证明有罪的[证据](http://https://web.archive.org/web/20210917152050/https://scroll.in/article/991095/why-isnt-the-government-looking-for-the-source-of-modi-assassination-malware-on-rona-wilsons-pc "证据")之一，它是通过 [NetWire RAT
远程会议](http://https://arsenalexperts.com/persistent/resources/pages/BK-Case-Rona-Wilson-Report-I.zip "NetWire RAT 远程会议")提供的，我们认为其与 ModifiedElephant
有关。进一步的[分析](http://https://arsenalexperts.com/persistent/resources/pages/BK-Case-Surendra-Gadling-Report-III.zip "分析")显示，ModifiedElephant 在大约 15
分钟的时间内，在多个不相关的受害者系统中捏造和编排几乎相同的证据。

## INCUBATOR KEYLOGGER

早在2012年就有受害者成为了键盘记录器有效载荷的目标([0a3d635eb11e78e6397a32c99dc0fd5a](http://https://www.virustotal.com/gui/file/d780446e89cb71d5346ac7a389266c15b0c0d5c42e46c7a88003f93aab2ba8b5
"0a3d635eb11e78e6397a32c99dc0fd5a"))。这些键盘记录程序是用 Visual Basic
编写的，并且在技术上并不令人印象深刻。此外，它们非常脆弱，已经不再能够正常运作了。

键盘记录器的整体结构与 2012
年[意大利黑客论坛](http://https://italianhack.forumfree.it/?t=63131534
"意大利黑客论坛")上公开分享的代码非常相似。ModifiedElephant 变体创建了一个名为“cssrs incubator”的隐藏窗口，与
**SetWindowsHookEx** 一起监控键盘敲击。它注册互斥锁“4oR_$$$tonelsu-mviiLempel-Ziv”, 使用
VBScript to WMI 连接器查询受害者系统的 MAC 地址和操作系统。这个恶意软件最终通过电子邮件从““Logs from ”标题下取出日志。

![](https://images.seebug.org/content/images/2022/02/7fabc226-be78-407e-9856-32b002db8d5e.png-w331s)
图 3: Log 上传格式字符串

在某些方面，Incubator 键盘记录器比上面提到的代码更加脆弱，因为它依赖于特定的 web
内容来运行(在编写本文时，这些代码已不可以在互联网上使用)。例如，键盘记录器将使用一个 GET
请求到一个过时的‘whatismyip.com’端点来获取受害者系统的 IP。

![](https://images.seebug.org/content/images/2022/02/8372a6d4-6422-4491-97c8-c551f12fe133.png-w331s)
图 4: 用于检查受害者 IP 的过时 WhatIsMyIp 端点

类似地，为了提取日志，键盘记录器拉出 Microsoft 模式模板来设置 SMTP
服务器，并使用硬编码(但是模糊化了)的电子邮件地址推送内容。在编写本文时，键盘记录器请求的模式站点都不可用，因而键盘记录器(2012 年版本)无法正常工作。

![](https://images.seebug.org/content/images/2022/02/60bf717b-713a-4f92-a76a-26da6963051b.png-w331s)
图 5: 使用 Microsoft 模式模板创建 SMTP 服务器的 Incubator 键盘记录器

键盘记录器利用硬编码的 SMTP 凭据和电子邮件地址，将记录的键盘敲击信息传递给攻击者控制的帐户，包 括:

**Email** | **Associated Sample**  
---|---  
[chiragdin3@gmail.com](mailto:chiragdin3@gmail.com) |
0a3d635eb11e78e6397a32c99dc0fd5a  
[loggerdata123@gmail.com](mailto:loggerdata123@gmail.com) |
c095d257983acca64eb52979cfc847ef  
[maalhamara@gmail.com](mailto:maalhamara@gmail.com) |
0a3d635eb11e78e6397a32c99dc0fd5a 56d573d4c811e69a992ab3088e44c268
1396f720bc7615385bc5df49bbd50d29 d883399966cb29c7c6c358b7c9fdb951
eff9b8e1ee17cd00702279db5de39a3c  
[maalhamara2@gmail.com](mailto:maalhamara2@gmail.com) |
0db49f572bb1634a4217b5215b1c2c6f ea324dd1dbc79fad591ca46ead4676a1
fd4902b8a4a4718f5219b301475e81aa  
[nayaamaal1@yahoo.com](mailto:nayaamaal1@yahoo.com) |
0db49f572bb1634a4217b5215b1c2c6f  
[nayaamaal122@yahoo.com](mailto:nayaamaal122@yahoo.com) |
d883399966cb29c7c6c358b7c9fdb951  
[nayaamaal2@yahoo.in](mailto:nayaamaal2@yahoo.in) |
ea324dd1dbc79fad591ca46ead4676a1  
[nayaamaal4@yahoo.com](mailto:nayaamaal4@yahoo.com) |
1396f720bc7615385bc5df49bbd50d29  
[newmaal@yahoo.com](mailto:newmaal@yahoo.com) |
fd4902b8a4a4718f5219b301475e81aa  
[shab03@indiatimes.com](mailto:shab03@indiatimes.com) |
c095d257983acca64eb52979cfc847ef  
[tamizhviduthalai@gmail.com](mailto:tamizhviduthalai@gmail.com) |
1720ae54d8ca630b914f622dcf0c1878  
[tryluck222@gmail.com](mailto:tryluck222@gmail.com) |
56d573d4c811e69a992ab3088e44c268  
[volvoxyz123@gmail.com](mailto:volvoxyz123@gmail.com) |
ef42dc2b27db73131e1c01ca9c9c41b6  
  
键盘记录器样本还包含 VBP 和 PDB 路径，为它们的原始开发环境提供了一些潜在的条件。

![](https://images.seebug.org/content/images/2022/02/8912f561-f09b-4979-ab9f-12ca029173b6.png-w331s)

在某些情况下，攻击者在一个或多个目标上使用相同的有效载荷进行多次网络钓鱼尝试。然而，ModifiedElephant
通常使用新的恶意软件样本进行每次感染尝试。

## ANDROID 木马

ModifiedElephant 还同时发送了包含 NetWire 和 Android 恶意软件有效载荷的多个钓鱼邮件。安卓恶意软件是一种不明商品性木马，以
APK
文件的形式发送([0330921c85d582deb2b77a4dc53c78b3](http://https://www.virustotal.com/gui/file/4dbb14ff2836733b34594956c4234d2a54c04257710dd31a0884b1926d35d7bc
"0330921c85d582deb2b77a4dc53c78b3"))。虽然 Android 木马可能是为更广泛的网络犯罪而设计的，但它与
ModifiedElephant Netwire 样本同时输送表明，同一个攻 击者试图在端点和移动设备上都对目标发起攻势。

![](https://images.seebug.org/content/images/2022/02/1932a012-f6bd-4e73-98a5-79ca59259312.png-w331s)
图 6: 带有 Netwire 和 Android GM Bot 变体恶意附件的ModifiedElephant 钓鱼电子邮件

![](https://images.seebug.org/content/images/2022/02/d3a4ddb7-1347-48d2-8d4d-4adc7f93a1aa.png-w331s)
图 7: 修改带有 Netwire 和 Android GM Bot 变体恶意附件的ModifiedElephant钓鱼邮件

该木马使攻击者能够拦截和管理短信和呼叫数据，清除或解锁设备，执行网络请求和远程管理。木马以一种非常基本的形式为攻击者提供了一个理想的低成本移动监控工具包。

## 与其他黑客组织的关系

我们对这个黑客组织的研究揭示了多种有趣的线索，突出了其有针对性的监视和任务的复杂性，即多个攻击者利用不同的机制来追踪同一群人。这些攻击者包括私营部门的攻击性黑客(PSOAs)，也有披着商业外观的团体来配合他们的非法活动。

基于我们对 ModifiedElephant
的分析，该组织针对众多目标进行运作，并可能与其他地区的黑客有关系。从我们的角度来看，我们无法进一步消除这种关系的可能性——无论是作为一个积极的伞状组织的
一部分，在各黑客组织之间合作和分享技术资源和目标，还是仅仅是巧合的有联系。以下是一些有趣的相关部分。

  * 多年来被 ModifiedElephant 锁定的许多个人也被移动监视间谍软件锁定或确认感染。Amnesty International组织查明，2019 年 NSO Group 的 Pegasus 被用于针对与 Bhima koregan 案件有关的人权维护者的袭击。此外，Bhima Koregaon 案的被告 Rona Wilson 的 iPhone 自 2017 年以来就成为 Pegasus 的攻击目标，这是基于Arsenal咨询公司分析的取证磁盘图像中发现的iTunes备份的数字取证分析。
  * 2013 年 2 月至 2014 年 1 月期间，目标之一罗娜 · 威尔逊(Rona Wilson)收到了一些钓鱼邮件，这些邮件可以归咎于“响尾蛇”(SideWinder)组织。ModifiedElephant 和响尾蛇之间的关系尚不清楚，他们的钓鱼邮件的时间和目标在我们的数据库中有重复部分。这可能表明攻击者被东家提供了类似的任务，或者他们以某种方式协同工作。响尾蛇是一个主要针对整个亚洲的政府、军队和商业实体的黑客组织。
  * ModifiedElephant钓鱼电子邮件有效载荷([b822d8162dd540f29c0d8af28847246e](http://https://www.virustotal.com/gui/file/828de55ffbfb1c1b6ffcbb56b838486dbaecc9b41a0d111fcca290978ed05e95 "b822d8162dd540f29c0d8af28847246e"))与 [Operation Hangover](http://https://web.archive.org/web/20210226131047/https://paper.seebug.org/papers/APT/APT_CyberCriminal_Campagin/2013/NS-Unveiling-an-Indian-Cyberattack-Infrastructure_FINAL_Web.pdf "Operation Hangover")共享基础设施重叠((new-agency[.]us)。“Operation Hangover”的业务除了针对世界各地组织的经济间谍活动外，还包括针对印度国内外国家安全重点目标的监视行动。
  * 另一个有趣的发现是在 2012 年，与 ModifiedElephant 活动密切相关的一个键盘记录器样本中包含了字符串“ Logs from Moosa’s”([c14e101c055c9cb549c75e90d0a99c0a](http://https://www.virustotal.com/gui/file/b665efe9b3dd575e17631146706d6a950d642aa7b7401ac794480c2bb557594c "c14e101c055c9cb549c75e90d0a99c0a"))。这个字符串可能指的是在同一时间被FinFisher间谍软件锁定的巴林活动人士Moosa Abd-Ali Ali。在没有更多信息的情况下，我们认为需要更多研究去验证猜想。

## 归因

调查一个像 ModifiedElephant
这样的攻击组织是一个有趣的挑战。此时此刻，我们拥有了攻击者在过去十年中行为的重要证据，他们攻击目标的独特观察，以及对他们技术目标的深刻理解。 我们观察到
ModifiedElephant 的活动与印度的国家利益紧密相关，而且 ModifiedElephant
的攻击与有争议的、充满政治色彩的个人逮捕案件存在着明显的相关性。

## 总结

Bhima Koregaon 一案为我们提供了一个观察的视角: 一个黑客组织愿意投入大量时间和资源，图求瓦解持相反观点的人。我们对
ModifiedElephant
的描述只关注了一小部分潜在受害者，简述了攻击者的技术，以及对他们的目标的不全面了解。关于这一黑客组织及其行动的许多问题尚未解决; 但有一点是明确的:
世界各地专制政府的反对者必须仔细了解那些试图剥夺他们发声权利的技术手段。

## IOC

**Type** | **Label**  
---|---  
File | ca91cea6038ebc431c88d7a3280566f5  
File | 1720ae54d8ca630b914f622dcf0c1878  
File | 0a3d635eb11e78e6397a32c99dc0fd5a  
File | ebbddbdadfa5a7e3e5f00faf27543909  
File | 93f53bf0f3db53aebcad54a4aa8cc833  
File | 5c5279eab1cbffec7d174a79e4233217  
File | 7ad281f61b89a85ae69242f9bd1a28be  
File | cc634fe1d5087d629b141d242ff49732  
File | 7fa8bb8c90a1d1864a5eda90bb8fa2a3  
File | eef779774586e59a0e387f7ce06b092e  
File | b8a464741d16dcf046b1e27d63f62bcd  
File | e631b2f8496c40e54951a2daebfc73ae  
File | ad1b6380efb0aad16f01bd1a23f2e649  
File | 3e38ed7d2168d8170c50db86e5ebd99c  
File | ae95cf0cd0e1a5cd6561ae3a17968dec  
File | a650de5d94dd938d9fd0cf55fae83dd6  
File | c9da1fa9e874b68df14788c80ca5cfee  
File | 319444e7bd7a20caef38dfcf22948f3c  
File | b822d8162dd540f29c0d8af28847246e  
File | d8fe02b0e134e8c9c338a784d2afacae  
File | 54be0a494baaf99ea3f88bdf6557c282  
File | 77cb1d0ddf20461b35ccd60bc9e9693f  
File | 1efe4a0981876ea7ec1780e21b0738a2  
File | bec87849d25eef2e41c0c2e42c90b044  
File | e1af82438339a1dd406479b884aba6f8  
File | ac65e7d08e48c6d20e3f90f7d9f73d8b  
File | cb347961b2f25f91639c16431e224002  
File | b6071ff11d4b41e52143ec5ba416131a  
File | 2463a3ed222be9d564e380b19522c481  
File | bf2d01c8cf111170589e52447b904163  
File | d883399966cb29c7c6c358b7c9fdb951  
File | a1af186d95ed7de686bd2e59e826f265  
File | 1396f720bc7615385bc5df49bbd50d29  
File | a07a315d5e05d4970a57d3c499f5c9dc  
File | ac04dfc7ccd9cc317b73f5860da94e7a  
File | a73e489b730cf730bd51ac790995d635  
File | afe38f5b0feeb4da163ca2d2ce85379b  
File | aa7faa3465f31f2f3343fe3646af2fba  
File | a77833d689be13eae622d48f8a5a8b12  
File | abd0b2779bdf3b0dd8b2a97815501850  
File | d6a491618a97e0044cc5f319d58c2dac  
File | 778547b3e0371ba048c32010b0dc42de  
File | d49f22104d979efb5e2da383fea403fe  
File | f1b6f87fd82f20f68f8624d63abda57d  
File | cadbc701381ed49c37ee3452171e0934  
File | a6b71ac86b1267385950815b7d18861b  
File | fd4902b8a4a4718f5219b301475e81aa  
File | eff9b8e1ee17cd00702279db5de39a3c  
File | 63b25fb5c4a41103d8f30659b3ed2c27  
File | b662b3fc9174e608718072ea55b37472  
File | 43cc3810b86a27e4a15349bbcad3e8e4  
File | ef42dc2b27db73131e1c01ca9c9c41b6  
File | ead29687b7c4e76c59269e76a85341b7  
File | bf6c7302cb2bbad454ad4302152285fe  
File | 74c0c5b81124b13b05b9c8792d50597e  
File | 1f0265c7fe4560d66f722e4264e717db  
File | 3b5a6b3a04ac5c2902ede522614c868c  
File | 6ebae56d4cc2a9a9454603b6116fa1a4  
File | 05472d6ee747a0e8aff33cf4e5d1141c  
File | 602df3a5732f8d8be2d9d6d8b8c48105  
File | aca0516142f102aba41e046a340f24e9  
File | cdc613712ac2ab85d6a0d314bb95a082  
File | 3e597147b7f94ea1cce064c11edffc42  
File | c0a2202236b0db4702e2ed521aef048c  
File | bee81874f719d61093f7ce12b2641ee4  
File | d49f22104d979efb5e2da383fea403fe  
File | 6a802a1dbdb11b8ac086c7a335a212b4  
File | a956cbab8fd7eaaf0c7dc8c7fd314a12  
File | c30b3a305bb180d7dc28e4cdfcda8bdf  
File | ea324dd1dbc79fad591ca46ead4676a1  
File | 04a186f53fdc9e871cb408df9c4a93ad  
File | 56d573d4c811e69a992ab3088e44c268  
File | 114c1a7d605f57752450a4985d143337  
File | b18bd12e615dca9094aac74740f0d154  
File | 1f3dac514c6f7542d84763dfd1c622b9  
File | 944d16d2e96dbb4092941857a66f3e07  
File | deb655a7a79832e2313e40d8d901f958  
File | 3a2f2086ac104d71f450b30ab47e36d5  
File | 04061f6e1a0463131ed129bcb03003d5  
File | 0db49f572bb1634a4217b5215b1c2c6f  
File | a21dfecebfb3bc499f805c71a6584f2b  
File | b7c1de8c84583465a78202f46bae4065  
File | 13bacd239931b7a1bea2f91a3c5f4d79  
File | a8cb8aed839878d4ca028c8f43bbfab3  
File | 61c22386df656f32f45bc1928a1e5a94  
File | d2a2e167f68e02b3713052ee3d63e013  
File | afe6d7985388013e32ae388a29600ae2  
File | 619016de4589ecb7039844a7c9a3f326  
File | 1fa4d31f8ce38b0660cfbee3da26ca63  
File | a8cea2eb313a908037bcc273b99a434d  
File | 0330921c85d582deb2b77a4dc53c78b3  
File | c0636b98f0c20fa82870d10ffd21dfe1  
File | e8efc4a7d41d754968199aebbfba77db  
File | 03e40d5f54940d3da97aa8ff981551a2  
File | bf164f4ffe8f571666e6ffdabba9d08f  
File | c35b13ca7dc705361237e341af7a7e08  
File | a7ce8ea97df340e6f7a77dcbe065a617  
File | 0ad6bf767f5c45a6faf32a40c5807057  
File | ac7ebe2cb77dd9ac74bc55931e91bc23  
File | d698739648717c21e7eb2ba1806e673a  
File | a7e96388fef3ac919f9f6703d7c0ebd4  
File | bf868371dd78162283a193940a1ae9fd  
File | c14e101c055c9cb549c75e90d0a99c0a  
File | d25250dca84aad3747418432c52be231  
File | 4dd1c71eee084eafdd0e9a29bd4d2e59  
File | 557bcc59ab20c44eb5b84c5073199983  
File | fedeb97850c1d917fbe3aeac388efd35  
File | 9ca885835c2c08af33ccf9e094358ea6  
File | b1c18520937d259d253d07e085d9e2b0  
File | 5b7780fc5e535eb507d86a54db70dee2  
File | 489c42a45b233acc377d10e1ec424b4b  
File | b7818efa622a88d0c59e9c744cc91d43  
File | 28094131dfc2c92d57a665c7fbc4fc0e  
File | af79639a14200ea25410b902fe0d5ee7  
File | 6be54d26001bd55770e3259562046ab2  
File | dccff8250ab9f275b367688e0eba7ec6  
File | 550dce15c334bc6b46c41c705d197e19  
File | c095d257983acca64eb52979cfc847ef  
File | a2e70ef708c06fdc57b0079dda4f89fe  
File | 93bed674dacbf3959c103711164747bf  
File | 60bff49b10afc593f67888c4f767ea36  
File | e6714e3bd83b4a349ab48cc203b91813  
File | bfd3e1a3926fd5ef4eec1ac533f2ee34  
File | e60b8ddee18e295d9e33e490eafdbfb3  
File | 96212539955ef86074398485c46e0483  
File | 169a58a0743301ebc5a536d890f10c06  
File | aaad5fe071f985c57164a2766d4d8a89  
File | c7a48f4f6ade403e09c3bac7185e92ee  
File | 60a083a1b7cd5e9a30212dc9541e161d  
File | c57f16bd980eec7340d1e541877f0098  
Domain | pahiclisting.ddns[.]net  
Domain | bzone.no-ip[.]biz  
Domain | johnmarcus.zapto[.]org  
Domain | ramesh212121.zapto[.]org  
Domain | atlaswebportal.zapto[.]org  
Domain | testingnew.no-ip[.]org  
Domain | nepal3.msntv[.]org  
Domain | socialstatistics.zapto[.]org  
Domain | socialstudies.zapto[.]org  
Domain | gayakwaad[.]com  
Domain | knudandersen.zapto[.]org  
Domain | jasonhistoryarticles.read-books[.]org  
Domain | duniaenewsportal.ddns[.]net  
Domain | vinaychutiya.no-ip[.]biz  
Domain | researchplanet.zapto[.]org  
Domain | greenpeacesite[.]com  
Domain | new-agency[.]us  
Domain | chivalkarstone[.]com  
Domain | newmms[.]ru  
  
## REFERENCES

  * [https://www.amnesty.org/en/latest/research/2020/06/india-human-rights-defenders-targeted-by-a-coordinated-spyware-operation/](http://https://www.amnesty.org/en/latest/research/2020/06/india-human-rights-defenders-targeted-by-a-coordinated-spyware-operation/ "https://www.amnesty.org/en/latest/research/2020/06/india-human-rights-defenders-targeted-by-a-coordinated-spyware-operation/")

  * [https://arsenalexperts.com/persistent/resources/pages/BK-Case-Rona-Wilson-Report-I.zip](http://https://arsenalexperts.com/persistent/resources/pages/BK-Case-Rona-Wilson-Report-I.zip "https://arsenalexperts.com/persistent/resources/pages/BK-Case-Rona-Wilson-Report-I.zip")

  * [https://arsenalexperts.com/persistent/resources/pages/BK-Case-Surendra-Gadling-Report-III.zip](http://https://arsenalexperts.com/persistent/resources/pages/BK-Case-Rona-Wilson-Report-II.zip "https://arsenalexperts.com/persistent/resources/pages/BK-Case-Surendra-Gadling-Report-III.zip")

  * [https://arsenalexperts.com/persistent/resources/pages/BK-Case-Surendra-Gadling-Report-III.zip](http://https://arsenalexperts.com/persistent/resources/pages/BK-Case-Surendra-Gadling-Report-III.zip "https://arsenalexperts.com/persistent/resources/pages/BK-Case-Surendra-Gadling-Report-III.zip")

  * [https://arsenalexperts.com/persistent/resources/pages/BK-Case-Rona-Wilson-Report-IV.zip](http://https://arsenalexperts.com/persistent/resources/pages/BK-Case-Rona-Wilson-Report-IV.zip "https://arsenalexperts.com/persistent/resources/pages/BK-Case-Rona-Wilson-Report-IV.zip")

  * [https://web.archive.org/web/20210226131047/https://paper.seebug.org/papers/APT/APT_CyberCriminal_Campagin/2013/NS-Unveiling-an-Indian-Cyberattack-Infrastructure_FINAL_Web.pdf](http://https://web.archive.org/web/20210226131047/https://paper.seebug.org/papers/APT/APT_CyberCriminal_Campagin/2013/NS-Unveiling-an-Indian-Cyberattack-Infrastructure_FINAL_Web.pdf "https://web.archive.org/web/20210226131047/https://paper.seebug.org/papers/APT/APT_CyberCriminal_Campagin/2013/NS-Unveiling-an-Indian-Cyberattack-Infrastructure_FINAL_Web.pdf")

  * [https://archive.org/download/unveiling-an-indian-cyberattack-infrastructure-appendixes/Unveiling%20an%20Indian%20Cyberattack%20Infrastructure%20-%20appendixes.pdf](http://https://archive.org/download/unveiling-an-indian-cyberattack-infrastructure-appendixes/Unveiling%20an%20Indian%20Cyberattack%20Infrastructure%20-%20appendixes.pdf "https://archive.org/download/unveiling-an-indian-cyberattack-infrastructure-appendixes/Unveiling%20an%20Indian%20Cyberattack%20Infrastructure%20-%20appendixes.pdf")

  * [https://github.com/malwarekiwi/Public-Content/raw/master/Global%20Perspective%20of%20the%20SideWinder%20APT.pdf](http://https://github.com/malwarekiwi/Public-Content/raw/master/Global%20Perspective%20of%20the%20SideWinder%20APT.pdf "https://github.com/malwarekiwi/Public-Content/raw/master/Global%20Perspective%20of%20the%20SideWinder%20APT.pdf")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1830/>

