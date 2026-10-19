**译者：知道创宇404实验室翻译组**  
**原文链接：<https://blog.nviso.eu/2020/09/01/epic-manchego-atypical-maldoc-delivery-brings-flurry-of-infostealers/>**

## 前言

2020年7月，NVISO检测到一组恶意Excel文档，也称为“
maldocs”，它们通过VBA激活的电子表格传递恶意软件。尽管我们曾见过恶意的VBA代码和掉落的有效载荷，但创建Excel文档本身的特定方式引起了我们的注意。

恶意Excel文档的创建者使用了一种技术，使他们无需实际使用Microsoft
Office即可创建装载宏的Excel工作簿。但是在这种特定工作方式下，这些文档的检测率通常低于标准maldocs。

这篇文章概述了这些恶意文档的产生方式。此外，它简要描述了观察到的有效负载，最后以建议和危害指标结尾，以帮助保护组织免受此类攻击。

## 主要发现

恶意的Microsoft Office文档是使用EPPlus软件而不是Microsoft Office
Excel创建的，这些文档可能与典型的Excel文档不同，所以可能会受到关注。

NVISO基于上载到VirusTotal等服务的有限数量的文件，以及整个活动中有效载荷传递的相似性，以中等可信度评估该活动，这是由单个攻击者执行的。

直到这篇文章发布之日为止，观察到的有效负载在大多数情况下都是所谓的信息窃取者，他们的目的是从浏览器，电子邮件客户端等中获取密码。

这些文件中产生的有效载荷仅在混淆和伪装方面有所发展。

## 分析

下面的分析部分分为两个部分，涉及感染链中的特定链接。

#### 恶意文件分析

在较早的文章中，我们写了有关“ VBA清除” [[1]](https://blog.nviso.eu/2020/02/25/evidence-of-vba-purging-found-in-malicious-documents/
"\[1\]")的技术，该技术可从VBA项目中删除已编译的VBA代码。我们很想知道是否有在野外发现的恶意文件正在采用这种技术（它降低了防病毒产品的初始检测率）。

最初，我们认为它们是使用Excel创建的，然后被VBA清除。但是仔细研究，我们发现，这些文档是使用.NET库创建的，该库创建了Office Open
XML（OOXML）电子表格。如我们的VBA清除博客文章所述，使用完全独立于Microsoft
Office的工具创建Office文档时，它们也可能缺少已编译的VBA代码。EPPlus是这样的工具。我们对这个.NET库很熟悉，因为几年来一直在使用它来为我们的红色团队和渗透测试人员创建恶意文档（“
maldocs”）。

当我们注意到maldocs没有经过编译的代码，并且也缺少Office元数据时，我们很快想到了EPPlus。该库还将创建OOXML文件，而无需编译VBA代码和Office元数据。

OOXML文件格式是一种开放包装约定（OPC）格式：一种ZIP容器，主要包含XML文件，可能还包含二进制文件（如图片）。它是由Microsoft在Office
2007发行版中首次引入的。OOXML电子表格使用扩展名.xlsx和.xlsm（用于带有宏的电子表格）。

使用EPPlus创建VBA项目时，它不包含已编译的VBA代码。EPPlus没有创建编译代码的方法：创建编译VBA代码的算法是Microsoft专有的。

我们检测到的第一个恶意文档是在2020年6月22日创建的，从那时起，我们在2个月的时间里发现了200多个恶意文档。在过去的几周里，攻击者增加了他们的活动，现在我们有时会看到10多个新的恶意文档。

![](https://images.seebug.org/content/images/2020/09/161398f3-c309-48df-b796-c1732c03f07e.png-w331s)
图1-每天观察到的独特的maldocs。

在两个月的时间内发现的maldocs具有许多与Microsoft
Office创建的文档的属性完全不同的属性。我们认为是这是因为它们是使用独立于Microsoft
Excel的工具创建的。尽管我们没有攻击者用来创建这些恶意文档的确切工具的副本，但此工具创建的恶意文档具有许多属性，这些属性使我们确信它们是使用上述EPPlus软件创建的。

EPPlus的某些属性包括但不限于：

  * 功能强大且用途广泛的库：它不仅可以创建包含VBA项目的电子表格，而且还可以对该项目进行密码保护和/或数字签名。它不依赖Microsoft Office。它也可以在Mono（跨平台，开源.NET）上运行。

  * 用EPPlus创建的OOXML文件具有一些属性，可将它们与用Excel创建的OOXML文件区分开。这里是一个概述：

ZIP日期：ZIP文件中包含的每个文件都有一个时间戳（ZIPFILE记录中的DOSDATE和DOSTIME字段）。对于使用Microsoft
Office创建（或编辑）的文档，此时间戳始终为1980-01-01
00:00:00（DOSDATE为0x0021，DOSTIME为0x0000）。使用EPPlus创建的OOXML文件具有与文档创建时间相对应的时间戳。通常，OOXML文件中的所有文件的时间戳都是相同的，但是由于执行延迟，时间戳之间可能相差2秒。2秒是DOSTIME格式的分辨率。

![](https://images.seebug.org/content/images/2020/09/a5c9849a-3d19-4173-a282-f4bd7ab09465.png-w331s)
图2 – DOSTIME差异（左：EPPlus创建的文件）

  * 额外的ZIP记录：一个典型的ZIP文件由ZIP文件记录（magic 50 4B 03 04）和（压缩）文件内容组成。然后是ZIP目录条目（magic 50 4B 01 02），后面是一个ZIP结束的目录记录（magic 50 4B 05 06）。Microsoft Office创建包含这3种ZIP记录类型的OOXML文件。EPPlus创建包含4个ZIP记录的OOXML文件：在每个ZIP文件记录之后还包括一个ZIP数据描述记录（magic504b0708）。

![](https://images.seebug.org/content/images/2020/09/c4a59a9b-5614-4ccd-b0f8-44245a90e132.png-w331s)
图3 –额外的ZIP记录（左：EPPlus创建的文件）

  * 缺少Office文档元数据：使用Microsoft Office创建的OOXML文档包含元数据（作者，标题等）。此元数据存储在docProps文件夹中的XML文件中。默认情况下，使用EPPlus创建的文档没有元数据：ZIP容器内没有docProps文件夹。

![](https://images.seebug.org/content/images/2020/09/c462e6a7-384e-427b-89bf-d48d82a6a467.png-w331s)
图4 –缺少元数据（左：EPPlus创建的文件）。

  * 已清除VBA：具有通过Microsoft Office创建的VBA项目的OOXML文件包含OLE文件（vbaProject.bin），该文件的流包含已编译的VBA代码和已压缩的VBA源代码。使用EPPlus创建的文档不包含已编译的VBA代码，而仅包含压缩的VBA源代码。这意味着： 模块流仅包含压缩的VBA代码。

没有SRP流（SRP流包含特定于实现和版本的编译代码，其名称以__SRP_开头）。

_VBA_PROJECT流不包含已编译的VBA代码。实际上，_VBA_PROJECT流的内容被硬编码在EPPlus源代码中：始终为CC 61 FF FF
00 00 00。

![](https://images.seebug.org/content/images/2020/09/4b0e8af9-c64e-4329-b16b-1213da08964e.png-w331s)
图5 –硬编码的流内容（左：EPPlus创建的文件）。

除上述内容外，我们还观察到了VBA源代码的某些属性，这些属性提示使用基于EPPlus之类的库的创建工具。

actor使用的VBA源代码有两个变体（一些变体使用PowerShell来下载有效负载，其他变体使用纯VBA代码）。但是所有这些变体都包含一个调用程序，该调用程序具有一个参数，即带有URL的字符串（BASE64或十六进制编码）。像这样（十六进制示例）：`Loader"68
74 74 70…"`

请注意，函数名称和参数之间没有空格字符：Loader与“ 68 74 74 70…”之间没有空格。

这表明VBA代码不是通过Office中的VBA EDI输入的：当输入这样的语句时，如果没有空格字符，VBA
EDI会自动为您添加一个空格字符（即使您复制/粘贴该代码也是如此）。

缺少此空格字符说明该代码不是通过VBA EDI输入的，而是可能通过EPPlus之类的库输入的。

为了说明这些属性上的差异，我们使用EPPlus库使用内部工具之一（ExcelVBA）显示示例。我们使用工具ExcelVBA在文本文件vba.txt中用vba代码创建vba.xlsm文件，并显示其某些属性：
![](https://images.seebug.org/content/images/2020/09/88bcf02c-2f08-48d3-9d07-ad6226b1cb78.png-w331s)
图6 – NVISO使用EPPlus库创建的XLSM文件。

![](https://images.seebug.org/content/images/2020/09/d075bc9f-c440-4869-bb39-f0b927361afb.png-w331s)
图7 –运行oledump.py显示该文档是使用EPPlus库创建的。

一些恶意文档包含使用EPPlus Wiki上的示例代码清楚地由EPPlus创建的对象。我们通过以下示例（此广告系列中的第一个文档）进行说明：

**文件名** ：扫描顺序列表.xlsm  
**MD5** ：8857fae198acd87f7581c7ef7227c34d  
**SHA256** :8a863b5f154e1ddba695453fdd0f5b83d9d555bae6cf377963c9009c9fa6c9be  
**文件大小** ：5.77 KB（5911字节）  
**最早内容修改** ： 2020-0646

本文档包含一个具有以下名称的drawing1.xml对象（圆角矩形）：`name =" VBASampleRect"。`

![](https://images.seebug.org/content/images/2020/09/f5e83dab-6518-4d1a-aa85-2cbf9cdf57f7.png-w331s)
图8 – maldoc的zipdump。

![](https://images.seebug.org/content/images/2020/09/34abfae6-cdc1-433b-acc8-e96330314b9b.png-w331s)
图9 –选择drawing1.xml对象显示名称。

这是使用EPPlus Wiki [[2]](https://github.com/EPPlusSoftware/EPPlus/wiki/VBA
"\[2\]")上的示例代码创建的：

![](https://images.seebug.org/content/images/2020/09/e4f724c4-2fbb-440b-9513-f75ed1e34ea3.png-w331s)
图10 – EPPlus示例代码，清楚地显示了相似之处。

值得注意的是，我们观察到的所有恶意文档的VBA项目均受密码保护。有趣的是，VBA代码本身未经编码/加密，而是以明文形式存储（尽管经过压缩）[[3]](https://blog.didierstevens.com/2020/07/20/cracking-vba-project-passwords/
"\[3\]")。当打开具有受密码保护的VBA项目的文档时，VBA宏将在没有密码的情况下执行：用户不需要提供密码。仅在VBA
IDE（集成开发环境）中查看VBA项目时才需要密码：

![](https://images.seebug.org/content/images/2020/09/8dc40016-b97c-4731-8ccf-fe697567322d.png-w331s) 图11 –查看VBA项目的密码提示。

我们无法恢复这些密码。我们将开膛手约翰（John the
Ripper）与rockyou.txt密码列表[[4]](https://www.kaggle.com/wjburns/common-password-list-rockyoutxt "\[4\]")结合使用，对Hashcat使用了小型ASCII蛮力攻击。

尽管每个恶意文档都有其自己的VBA代码，但每个恶意文档都是唯一的，迄今为止已分析了200多个样本，但我们可以将所有这些VBA代码概括和抽象为少数几个模板。VBA代码将使用PowerShell或ActiveX对象下载有效负载。不同的字符串使用十六进制，BASE64或XOR编码进行编码，或这些编码的组合。本博客文章的末尾提供了一个Yara规则来检测这些恶意文档，以进行识别和检测。

## 有效负载分析

如上一部分所述，通过恶意VBA代码，从各个网站下载了第二阶段的有效负载。由其各自的恶意文档创建的每个第二阶段可执行文件都充当最终有效负载的放置程序。为了阻止诸如防病毒解决方案之类的检测机制，利用了多种混淆技术，但是这些技术不够先进，无法掩盖恶意意图。攻击者所使用的基础设施似乎主要包括受感染的网站。

流行的防病毒解决方案，例如VirusTotal上列出的解决方案，如图12所示，通常将第二阶段的可执行文件标识为“
AgentTesla”。尽管利用VirusTotal进行恶意软件识别不是一种理想的方法，但它确实显示了简单的混淆会导致错误的分类。在整个分析过程中，我们将解释这些流行的检测中只有很少的结果是准确的。

![](https://images.seebug.org/content/images/2020/09/3f72cb97-11fd-46b0-9d0b-9e202f1d15b0.png-w331s)
图12：VirusTotal的“ AgentTesla”错误识别。

我们观察到的不同混淆技术概述了操作Epic
Manchego的所有第二阶段可执行文件所共有的模式。从图13中可以看到，第二阶段将动态加载解密DLL。然后，此DLL组件继续提取其他设置和第三阶段有效负载，然后再将执行转移到最终的有效负载（通常是信息窃取者）。

![](https://images.seebug.org/content/images/2020/09/83ed6a8c-e79f-434b-acc3-48cbcbbbf691.png-w331s)
图13：Epic Manchego操作的最后阶段交付机制。

尽管以上混淆模式对于所有样本都是通用的，但我们已经观察到其复杂性的演变以及可能采用更多机会主义技术的广泛变化。

![](https://images.seebug.org/content/images/2020/09/7a99d9b3-5fb7-411e-8624-5811654180da.png-w331s)

该行动第二阶段样本的一个共同因素是使用隐写术掩盖其恶意意图。图14标识了在最近的变体中使用的部分配置，其中包括最终有效负载在内的设置字典被编码为数百个图像，这是作为第二阶段嵌入式资源的一部分。

![](https://images.seebug.org/content/images/2020/09/edbc7b2e-2686-48dc-abb8-9315609443fe.png-w331s) 图14：BMP图像中编码的部分字典。

图像本身是以下第二阶段样本的一部分，该样本具有以下属性：

**文件名** ：crefgyu.exe  
**MD5** ：7D71F885128A27C00C4D72BF488CD7CC  
**SHA256** :C40FA887BE0159016F3AFD43A3BDEC6D11078E19974B60028B93DEF1C2F95726  
**文件大小** ：761 KB（779.776字节）  
**编译时间** ： 2020-03-09 16:39

值得注意的是，混淆过程不是由攻击者自己建立的。对第二阶段隐写术解码程序的仔细审查揭示了大多数样本是如何错误地将最终有效载荷包含两次。在加载程序配置的以下表示形式（图15）中，我们可以看到其有效负载确实是重复的。第二级和第三级有效载荷的复杂性还倾向于表明操作涉及不同的参与者，因为初始文档反映了经验不足的参与者。

在分析的多个基于字典的变体中，我们还注意到，无论最终的有效负载如何，相似的键都用作设置的一部分。所有字典都包含最终的有效载荷，即“EpkVBztLXeSpKwe”，而某些字典（如图15所示）也包含与“PXcli.0.XdHg”相同的值。这暗示了可能的有效载荷传递构建器，可以由多个参与者使用。

![](https://images.seebug.org/content/images/2020/09/3dc2ade3-4b2e-4437-88ae-eefbf6001fc1.png-w331s) 图15：第二阶段解码字典。

在30个不同的基于字典的第二阶段的手动分析数据集中，观察到19个唯一的最终有效载荷。从这些中，“Azorult”窃贼占该变种交付量的50％（图16）。其他有效负载包括“
AgentTesla”，“Formbook”，“Matiex”和“njRat”，这些都已经有据可查。“Azurult”和“njRAT”都有明显的重用率。

![](https://images.seebug.org/content/images/2020/09/6f06a2d7-a6d6-40b6-9827-2582ff8460c0.png-w331s)
图16：基于字典的有效载荷分类和带有修剪散列的样本的（重新）使用。

我们对滴管和相应有效负载的分析揭示了混淆例程中的常见模式。尽管机会主义混淆方法可能会发展，但交付的有效负载仍然是相当有限的一组恶意软件系列的一部分。

## 指定目标

我们从VirusTotal检索到的少量恶意文档与网络钓鱼电子邮件本身一起上传。对这些电子邮件的分析可以为该参与者的潜在目标提供一些启示。由于检索到的源电子邮件数量有限，因此无法根据受害者确定明确的模式。在我们能够检索到的6封电子邮件中，收件人分别是医疗设备部门，铝业，设施管理部门和定制压机供应商。

在调查发件人域时，似乎大多数电子邮件都是从合法公司发送的。使用“已被我拥有” [[5]](https://haveibeenpwned.com/
"\[5\]")服务确认是否已知有任何电子邮件地址遭到破坏，但没有结果。这使我们想知道攻击者在早期感染期间是否能够利用这些帐户，或者是否由另一方提供。无论谁破坏了帐户，攻击者似乎主要使用合法的公司电子邮件帐户来发起网络钓鱼活动。

从发送者和接收者这两个角度来看，似乎没有一种可以推断出潜在新目标的模式。似乎没有针对的特定部门，发送域也没有关联。

电子邮件的正文（内容）和主题均与更经典的网络钓鱼方案有关，例如，发起业务的请求，附件提供了“详细信息”。观察到的主题概述可以在下面看到，请注意，某些主题已被各自的邮件网关更改：

  * 回复：需要报价/
  * 报价量和重量为首选
  * **_*_ SPAM ***** FW：Offer_10044885_ [companyname] _2_09_2020.xlsx *
  * [怀疑的垃圾邮件]替代要求*
  * 采购订单明细
  * 报价请求

![](https://images.seebug.org/content/images/2020/09/e38c263e-59bb-4f7c-892f-51bd42a54b90.png-w331s)
图17 –网络钓鱼电子邮件示例。

这种诱使用户打开附件的方法并不是什么新鲜事物，并且没有提供很多其他信息来精确定位针对任何特定组织或行业的广告系列。

但是，通过VirusTotal利用maldocs的公开提交，我们聚集了200多个文档，这使我们能够按提交计数对27个国家/地区进行排名，而无需区分可能通过VPN执行的上传。如图18所示，美国，捷克共和国，法国，德国以及中国等地区占了大多数目标区域。

![](https://images.seebug.org/content/images/2020/09/8f0cea25-a705-494e-b40e-946e35420dd3.png-w331s)
图18 – VT提交的地理分布。

在分析目标区域的初始文档时，我们主要识别基于英语，西班牙语，中文和土耳其语的图像。

![](https://images.seebug.org/content/images/2020/09/443c319e-aa26-4862-b970-51b786144039.png-w331s)
图19 – Maldoc内容分别为中文，土耳其语，西班牙语和英语。

但是，某些图像包含一个有趣的细节：某些文档属性使用西里尔字母，而与图像的主要语言无关。

尽管在多幅图像中观察到了西里尔字母设置，但是在撰写此文章时发现了一个新的恶意文档，这引起了我们的兴趣，因为它似乎是第一个明确冒充医疗保健部门成员的人（“俄亥俄·哈丁纪念医院”），如图20所示。还要注意上述设置：СТРАНИЦА1ИЗ1
; 表示第1页，共1页。

![](https://images.seebug.org/content/images/2020/09/1541a892-ecec-4474-a8d5-fca31551434d.jpg-w331s)
图20 –带有西里尔字母设置的Maldoc内容模拟了“ Ohiohealth Hardin Memorial Hospital”。

此Microsoft Excel文档具有以下详细信息：

**文件名** ： 새 로 운 주 문 _2608.xlsm（韩文：新订单_2608.xlsm）  
**MD5** ：551b5dd7aff4ee07f98d11aac910e174  
**SHA256** :45cab564386a568a4569d66f6781c6d0b06a9561ae4ac362f0e76a8abfede7bb  
**文件大小** ：5.77 KB（5911个字节）  
**最早修改内容时间** ： 2020年6月22日14时01分46秒

尽管可以从网上简单地找到来自该医院的模板，然后由攻击者使用，但是这种令人惊讶的操作方式变化似乎与自跟踪开始以来观察到的行为者的不断发展相吻合。

## 评价

根据分析，NVISO评估以下内容：

  * 所观察到的威胁行动者已经找到了一种创建恶意Office文档的新方法，该方法可以至少略微减少检测机制。

  * 攻击者可能正在尝试和发展其方法，以创建恶意Office文档，从而可能使工作流程自动化。

  * 尽管目前的定位似乎很有限，但这些首次投放可能是为了测试而不是全面的广告系列。 提交给VirusTotal的最新检测结果表明，该攻击者可能正在加强其行动。

  * 尽管创建恶意文档的方法是唯一的，但有效负载传送和实际有效负载的方法并不是唯一的方法，应该由现代技术加以阻止或检测。

  * 有趣的是Xavier Mertens最近在SANS日记中通过VT追踪恶意软件活动[[6]](https://isc.sans.edu/forums/diary/Tracking+A+Malware+Campaign+Through+VT/26498/ "\[6\]")发表的文章。似乎另一位安全研究人员也一直在跟踪这些文档，但是，他们已经从maldocs中提取了VBA代码并上传了该部分。这些模板与PowerShell的下一阶段下载方式有关。

总之，NVISO评估了这种特定的恶意Excel文档创建技术，尽管有效载荷分析通常被认为更有趣，但它可能会被更多地在野外观察到，尽管它被电子邮件网关或分析人员遗漏了。但是，阻止和检测这些类型的新颖性（例如本博客中描述的恶意软件创建）使组织能够在出现激增或类似活动时更快地进行检测和响应。建议部分提供了裁定和指标作为检测手段。

## 推荐建议

  * 过滤电子邮件附件和从组织外部发送的电子邮件。
  * 实施强大的端点检测和响应防御。
  * 创建网络钓鱼意识培训并执行网络钓鱼练习。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1328/>

