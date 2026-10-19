# Valak恶意软件分析

阅读量 **263096**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-04 09:45:18

 **x**

##### 译文声明

本文是翻译文章，文章原作者 cybereason，文章来源：cybereason.com

原文地址：<https://www.cybereason.com/blog/valak-more-than-meets-the-eye>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t010db17058f9bb5f26.png)

## 介绍

Valak 在2019年首次发现，它被归类为一种加载器，主要用于多场针对美国的战役。它经常与
[Ursnif](https://www.cybereason.com/blog/new-ursnif-variant-turns-to-cryptocurrency-as-banks-become-more-secure) (又名
[Gozi](https://malpedia.caad.fkie.fraunhofer.de/details/win.gozi) ) 和
[IcedID](https://malpedia.caad.fkie.fraunhofer.de/details/win.icedid) 配合，经过
Cybereason Nocturnus
在2020年4月份的调查，Valak被确认用于主要针对美国和德国的战役中。这些活动涉及到新版本，表明该恶意软件作者一直在快速开发更好的，改进的版本。目前已经发现了30多种不同版本的恶意软件，很短的时间内显示出了巨大的进步。Valak
的主要功能包括：

  * **无文件阶段** ：在无文件阶段中用注册表来存储不同的组件
  * **侦察** ：从被感染主机收集用户、计算机和网络信息
  * **地理位置感知** ：检查受害者机器的地理位置
  * **屏幕截图** ：获取受感染主机的屏幕截图
  * **下载次要payload** ：下载其它插件和恶意软件
  * **企业意识** ：针对管理员和企业网络
  * **渗透Exchange服务器** ：从 Microsoft Exchange 邮件系统收集和窃取敏感信息，包括凭据和域证书

在改进中，Valak 新版本最重要且最有趣的功能是名为“PluginHost”的组件。它提供和C2
服务器的通信，并以“ManagedPlugin”的名称下载其他插件。被观察到的插件有“Systeminfo”和“Exchgrabber”，它们似乎都是针对企业的。

## 威胁分析

###  初次感染

在这些活动中，最常见的感染媒介是嵌入了恶意宏代码的 Microsoft Word 文档。根据目标的不同，文档的内容为英文或者德文。

恶意宏代码用于下载名为”U.tmp”，扩展名为”.cab”的 DLL 文件并保存到 temp 文件夹中。

DLL 文件下载地址：“hxxp://v0rzpbu[.]com/we201o85/aio0i32p.php?l=hopo4.cab”

下载完 DLL 文件后，该代码用”regsvr32.exe”运行恶意 DLL

执行时，DLL 会调用 WinExec API 进行删除和启动。这一阶段中，Valak 使用随机命名的恶意 JavaScript
文件，该文件每次执行都会更改名称。下面的例子中该 JavaScript 文件名为 “sly4.0”。

## 多阶段攻击：Valak的逐步分析

###  第一阶段：获得初步立足点

下载的 JavaScript 代码”sly4.0”包含一个名为”PRIMARY_C2”的变量，其中包含多个伪造和合法的域名，有Google, Gmail,
Avast 和 Microsoft 等等，样本间的域名列表有所不同。

Valak 使用两个预定义的 URI 创建到列表中不同 C2 服务器的连接：

  * 一个用于下载名为“project.aspx”的编码文件，另存为 project[1].htm在版本30中，该文件改名为”rpx.aspx“

  * 一个用于下载名为“a.aspx”的编码文件，另存为 a[1].htm在版本30中，该文件改名为”go.aspx“

恶意软件使用 Base64 和 XOR 密码对这两个文件进行解码，密钥是预定义字符串和运行时从内存收集的信息的组合。

该恶意软件在
“HKCUSoftwareApplicationContainerAppsw64”注册表项中设置诸如C2服务器，ID，下载的payload和已解码的project.aspx之类的信息，这些将在第二阶段中使用。

下载好payload并设置好注册表的键和值后，Valak使用计划任务来设置它的持久化。

计划任务设置为启动
wscript，该JavaScript脚本执行”Classic2Application.bz”文件中名为“Default2.ini”的备用数据流（ADS）。

ADS中的脚本执行“HKCUSoftwareApplicationContainerAppsw64ServerUrl”的内容，该注册表项包含第二阶段JavaScript文件“project.aspx”的内容。

## 第二阶段：获取并执行次级PAYLOAD

第一阶段，Valak 为这次攻击夯实基础。第二阶段，它下载用于侦察活动和窃取敏感信息的其他模块。

第二阶段中将使用两个payload(“project.aspx”和”a.aspx”)和注册表键中的配置来执行恶意活动。

## 第二阶段的JS – PROJECT.ASPX

“project.aspx”（即我们所称的第二阶段的JS）是一个看起来与第一阶段的JavaScript文件（“sly4.0”）非常相似的文件。但是，仔细检查后，它包含其他功能。

该脚本被计划任务所执行以实现持久化，它的主要目标是：

  * 执行插件管理组件Pluginhost.exe
  * 从C2下载并解析其它payload
  * 将payload另存为备用数据流并设置计划任务以运行它们

在第二阶段，配置文件已更改为包含唯一“Client_ID”和尝试下载的另一个文件“bounce.aspx”。

第二阶段还包含三个独特的功能，即“CreateExecJob”，“CreateOleExecJob”和“LaunchPlugin”.

这些函数经”ParseTask”函数调用，并从C2接收已解析的任务。

如果该恶意软件下载了以“ODTASK”开头的payload，它会调用“CreateOleExecJob”，将payload作为文件“C:UsersPublicPowerManagerSpm.jar”的ADS写入，并创建计划任务“PerfWatson_%taskname%”来运行它。

如果恶意软件收到以单词“PLUGIN”开头的内容，它会调用”LaunchPlugin“，将WMI以内容作为参数来执行PluginHost.exe文件。

如果恶意软件收到以单词“TASK”开头的内容，它会调用”CreateExecJob“，将该内容作为文件”C:UsersPublicPowerManagerSpm.jar“的ADS写入，并创建计划任务”PowerUtility_%taskname%W“来运行它。

我们的分析表明，这次，Valak的payload是IcedID。但是，该payload可能会有所不同，因为攻击者可以将其他payload下载到受感染的系统。

在以前的感染中，Valak下载了不同的远程管理工具，如putty.exe和NetSupport Manager。

## PLUGINHOST – A.ASPX

解码后的”a.aspx“作为 %TEMP%\<ID>.bin
保存在临时文件夹中，该文件内部名为”PluginHost.exe“，是一个可执行文件，用于管理其他组件。

Valak 的模块化插件架构：

## PLUGINHOST – 插件管理组件

可执行文件”PluginHost.exe“的功能分为四个类：Bot，HTTPClient，Program 和
Utils，这使得它能执行下载并加载恶意软件的其他组件。

###  Bot：

bot类负责从第一阶段设置的几个注册表项中进行读取

  * GetID() 读取包含ID的注册表项”SetupServiceKey“
  * GetC2() 读取包含C2域名的注册表项”ShimV4“

两个函数都是用Utils类来读取注册表项

###  HTTPClient:

HTTPClient类包含两个函数，post 和 GetPluginBytes。

GetPluginBytes() 函数使用 GetC2() 获取C2域名并添加嵌入的URI。该URL用于下载插件的其他模块。

###  Program:

Program类包含文件的主函数 main()。该函数执行函数 GetPluginBytes()
来下载类型为”ManagedPlugin“的模块组件。这些组件将以反射方式加载到可执行文件的内存中，并扩展插件功能。

###  Utils:

Utils类包含其他类使用的几个维护函数。

## MANAGEDPLUGIN – 增强功能的插件套件

在提到其他插件时，值得注意的是，在 Valak 的早期版本中，插件是由第二阶段的JS通过PowerShell下载的。而近期的 Valak
版本抛弃了很流行但易于检测的 PowerShell 下载器，并将其转换为 PluginHost，作为管理和下载额外 payload 的一种方式。这种转变表明
Valak 的作者正在寻找更隐秘的方法来改进他们的躲避技术。

本次分析中，我们发现几种不同的模块被赋予相同的内部名称”ManagedPlugin.dll”。

这些模块被“PluginHost.exe”下载并加载。

  * **Systeminfo** ：负责广泛的侦察，针对本地和域管理员
  * **Exchgrabber** ：旨在窃取 Microsoft Exchange 数据并渗透到企业邮件系统中
  * **IPGeo** ：验证目标的地理位置
  * **Procinfo** ：收集被感染机器正在运行的进程信息
  * **Netrecon** ：执行网络侦察
  * **Screencap** ：从被感染机器获取屏幕截图

在这些组件中，一些组件专注于一个单一的、特定的活动来实现它们的目标，当涉及其它到能力和潜在影响时，它们的健壮性相对较差。这包括ipgeo,
procinfo, netrecon和screencap。

下面是“systeminfo”和“exchgrabber”的深入介绍，它们比前面提到的插件组件更高级、更复杂：

## MANAGEDPLUGIN： SYSTEMINFO，侦察模块

当涉及到类名时，“Systeminfo” 与 “PluginHost”
有许多相似之处。然而，与“PluginHost”不同的是，它包含了一些侦察功能，这些功能集中于收集用户、机器和现有的 AV 产品的信息。

该模块收集有关用户的信息，并尝试验证这是本地管理员还是域管理员。这表明，在感染机器之后，Valak
选择主要针对管理员和域管理员。这表明了一种倾向，目标是更高配置的帐户，如企业管理员。

该模块尝试使用 AntivirusSoftware() 函数查找被感染的机器是否安装了任何安全产品。使用 WMI 查询 “SELECT * FROM
AntiVirusProduct” 来收集已安装的杀毒软件的信息。

该模块还收集受感染机器的物理地址(MAC)和IP地址。

其他侦察活动还包括以下几个功能:

  * **NetUser** ：提供更多关于用户的信息
  * **SystemUpTime** ：记录机器运行的时间
  * **WindowsVersion** ：确定 Windos 版本

为了过滤数据，插件使用了HTTPClient类中的“post”函数。“Post”使插件能够上传内容并将数据提取到远程C2，远程C2的域名存储在注册表中。

与“PluginHost”类似，“SystemInfo”使用另一个名为GetQuery()的函数，该函数构建URL以将信息发送到远程C2。URL使用Base64和一些字符替换进行编码。

“ManagedPlugin”模块的核心功能在“ManagedPlugin”类中。该函数无休止地循环并继续执行侦察活动并将其发送给攻击者。

## MANAGEDPLUGIN：EXCHAGRABBER – 目标为企业的窃取者

Exchgrabber，类似于systeminfo，当涉及到像Bot、HTTPClient和Utils这样的一些函数名时，它与PluginHost有一些相似之处。然而，它有自己不同的能力。

乍一看，这个模块似乎只用于窃取凭证，这可以在几个类和数据参数中看到，它们的名称都很清楚，比如“Credential”和“CredentialType”。

模块在类“credential”中处理其凭据管理，其中包括几个函数，用于处理凭据管理活动和保存这些凭据的数据类型。

这个类中最有趣的函数之一是“Credential”，它接收四个参数: username、password、target 和
CredentialType。它将这些凭证插入到相应的模块变量中。

“target”变量在核心的ManagedPlugin函数中用于存储与Microsoft Office应用程序相关的字符串。

“credential”函数中另一个有趣的参数是“CredentialType”。凭证的类型由枚举变量“CredentialType”决定，该变量包含模块试图提取的每个凭证。

**凭证类型是可以从企业Microsoft Exchange服务器数据中提取的敏感信息，包括域密码和域证书。**

提取此敏感数据允许攻击者访问企业内部邮件服务的内部域用户以及访问企业的域证书。使用systeminfo，攻击者可以识别哪个用户是域管理员。这造成了敏感数据泄露和潜在的大规模网络间谍或信息窃取的非常危险的组合。它还表明，这个恶意软件的目标首先是企业。

在检查类MainPlugin背后的核心逻辑后，每个类如何与其他类协作来从Microsoft Exchange和Outlook中提取数据就很清楚了。

该模块试图检查提取的数据是否与Microsoft
Office或MS.Outlook有关。如果有关，它将尝试访问文件“Autodiscover.xml”，使用函数
GetFiles。“Autodiscover.xml “是一个动态生成的文件，包含Microsoft
Outlook访问在配置向导中输入的邮箱所需的数据。Exchange
Autodiscover服务的主要目的是建立与Exchange用户邮箱的初始连接。然后，它尝试收集专用交换林的AutoDiscover
SMTP地址，并最终将所有提取的数据放在一个名为“text”的变量中。

在收集敏感数据之后，模块使用Base64对其进行压缩。这是“Utils”类中这个特定模块的一个新特性。然后，它使用POST函数和一个嵌入的URI将敏感数据发送到攻击者的C2。

## VALAK随时间的演变

在撰写这份报告时，我们已经看到了 Valak 的巨大变化。它目前的版本号是24。

本节通过分析版本6、版本9、版本23和版本24，重点介绍了 Valak 以前的版本和新版本之间的主要差异。

###  Payload混淆的改进

在旧版本中，Valak 下载第二阶段 JS 只使用了一种混淆技术: Base64。新版本除了使用Base64外，还使用XOR。

###  插件管理组件

Valak 的最新版本在第一阶段下载了两个payload。第一个payload是 Valak 的插件管理组件(“pluginhost.exe”)，第二个是
Valak 第二阶段的 JavaScript payload。在早期版本中，Valak 没有包含“pluginhost” payload。

###  PowerShell活动

在老版本的 Valak 中，第二阶段 JS 像新版本一样下载额外的内容，包括”TASK“， ”ODTASK“， ”PLUGIN“。在较新的版本中，Valak
还在第一阶段下载“PluginHost”，并在第二阶段接收到“PLUGIN”后执行它，然后再下载
ManagedPlugin.dll。在较早的版本中，Valak使用第二阶段的任务“PLUGIN”来利用PowerShell并下载“ManagedPlugin”作为一个Base64编码的二进制文件。

正如前面提到的，Valak 的后续版本放弃了流行但易于检测的PowerShell下载器方法，转而使用“PluginHost”来管理和下载额外的
payload。这一转变可能表明，Valak 的作者正在寻求利用更隐秘的方法，并改进他们的规避技术。

## VALAK的基础设施

分析不同的示例可以发现一个重复的URI模式，该模式用于连接到一个嵌入代码的域名的“bucket”。

例如，用于下载“PluginHost”(a.s aspx)的URI总是被构建为：

“a.aspx?redir=1&clientUuid=91&r_ctplGuid=” +<the encoded_ID>\+ “&TS2=”
+<random string>

这个URI并不是样本之间唯一的相似性，Valak有多个URI来跨组件匹配此行为。

**Valak被观察到的URI模式：**

  * **DLL的下载** ：DLL URI 总是包含”aio0i32p“
  * **第二阶段** ： 第二阶段（project.aspx）总是包含”?cwdTelemetry=2&regclid=“
  * **任务获取** ：从C2获取任务时总包含”?dx11diag=“
  * **其它插件的下载** ：”PluginHost“下载插件时总包含”db.aspx?llid=“
  * **Exchgrabber插件数据** ：从插件中提取数据的URI包含”class4.aspx?internalService“

Valak恶意软件的另一个有趣的方面是，它有一个共享的基础设施，几乎所有的不同版本。如下图所示，大多数已知域名之间都有连接，无论是URI相似性、下载的文件还是连接的文件。

## VALAK和其他恶意软件的关系

Valak 病毒的感染最初被描述为单方面的，Valak 主要下载其他已知的恶意软件，如 Ursnif 或 IcedID。然而，在调查过程中，我们发现
Valak 与其他恶意软件的关系实际上是多方面的。

例如，以下由恶意软件流量分析提供的网络流量记录说明了由 Ursnif 发起的感染链，它从同一个C2服务器下载 IcedID 和 Valak。

虽然这些特定的恶意软件之间的合作关系的性质还不完全清楚，我们怀疑它是基于地下社区的个人联系和相互信任。鉴于 Ursnif 和 IcedID
都被认为是使用俄语的电子犯罪生态系统的一部分，Valak
的作者可能也是使用俄语的地下社区的一部分。众所周知，这个社区在信任和声誉的基础上保持着相当密切的联系。

另一个可能将 Valak
背后的作者与俄语社区联系起来的线索是钓鱼文件中遗留的俄语和阿拉伯语(沙特阿拉伯)语言设置的痕迹。这些语言痕迹出现在我们分析的所有样本中，如下图所示:

需要指出的是，上述语言痕迹很容易被威胁行动者有意地操纵和放置在那里，因此，凭此确定威胁行动者的来源是不够的。

## VALAK作为独立恶意软件的演变

虽然最初下载的恶意软件是作为其他恶意软件的 payload，但在最近出现的Valak中，恶意软件似乎是作为一个独立的单元出现在传统的钓鱼活动中。

最近的行动针对两个特定的地理位置，包括美国和德国，文件的内容和名称是用英语和德语编写的，并伪装成合法文件。

尽管Valak似乎已经随着时间的推移而发展，并拥有信息窃取的功能，但很明显，Valak背后的威胁行动者继续与其他恶意软件合作，如 IcedID 和
Ursnif，以最大化他们的收入。

## 结论

本项研究中，Cybereason
Nocturnus团队分析了新兴的恶意软件Valak。尽管Valak于2019年首次亮相并被几名安全分析师归类为恶意软件加载器，但我们的调查表明Valak不仅仅是简单的恶意软件加载器。它是一种复杂的模块化恶意软件，具有侦察和信息窃取的功能。

在大约6个月的时间里，Valak的开发人员取得了巨大的进步，发布了30多个不同的版本。每个版本都扩展了恶意软件的功能，并增加了规避技术以提高其隐身能力。Valak至少有6个插件组件，使攻击者能够从受害者那里获得敏感信息。

扩展的恶意软件功能表明，Valak可以单独使用，也可以不与其他恶意软件一起使用。话虽如此，但Valak背后的威胁实施者似乎正与电子犯罪生态系统中的其他威胁实施者合作，制造出一种更危险的恶意软件。

这些恶意软件的攻击似乎主要针对美国和德国。Cybereason
Nocturnus团队将继续监控Valak病毒的传播情况，以确定病毒是否会传播到其他地区，因为恶意软件还在继续发展，并在网络犯罪分子中越来越流行。

本文翻译自cybereason.com [原文链接](https://www.cybereason.com/blog/valak-more-than-meets-the-eye)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **慕长风** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/207197](/post/id/207197)

安全客 - 有思想的安全新媒体

本文转载自: [cybereason.com](https://www.cybereason.com/blog/valak-more-than-meets-the-eye)

如若转载,请注明出处： <https://www.cybereason.com/blog/valak-more-than-meets-the-eye>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [Valak](/tag/Valak)

 **+1** __2赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLWIwV1auq82Xoe66LNVMC1ZsMRStnPpYHqsQKwYmc5POuwVpJSic7zsjUHXib52OSkoA5VufNDEnvg/132)
慕长风

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

