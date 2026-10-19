# 用SettingContent-ms绕过ASR和Office2016的OLE阻止功能执行命令

阅读量 **193787**

|评论 **2**

发布时间 : 2018-06-18 13:06:46

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Matt N，文章来源：posts.specterops.io

原文地址：<https://posts.specterops.io/the-tale-of-settingcontent-ms-files-f1ea253e4d39>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0136104eca027f8591.jpg)

## 前言

作为攻击者，对强化目标的初始访问被证明可能是相当大的挑战。当为初始访问选择payload时，攻击者必须选择允许执行任意代码或使用最少用户交互执行shell命令的文件格式。这些文件格式可能很少，这就是攻击者依赖文件类型(如.HTA、Office宏、.VBS、.JS等)的原因。Windows上的内置文件扩展名显然是有限的，而且随着防御能力的提高，payload的数量继续减少。

此外，攻击者必须以一种会导致执行的方式将该文件发送给最终用户。同样，这方面的选择可能会受到限制，因为直接链接到payload或将它们附加到电子邮件往往会受到防病毒或浏览器保护的阻碍。这就是攻击者选择对象链接和嵌入(Object
Linking and Embedding/OLE)、ZIP文件等的原因。为了打击通过文件传递的攻击，Office
2016引入了[阻止所有“危险”文件](https://support.office.com/en-us/article/Packager-Activation-in-Office-2016-52808039-4A7C-4550-BE3A-869DD338D834)格式在默认情况下通过OLE嵌入的方法。这降低了最依赖payload交付方法之一的有效性。当试图激活被阻止的文件扩展名时，Office将抛出错误并阻止执行：[](https://p3.ssl.qhimg.com/t012c624dfff34d3ad1.jpg
"Office 2016阻止许多“危险”文件扩展名之一")

除了OLE阻塞之外，Microsoft还在Windows 10中引入了 Attack Surface
Reduction(ASR)规则(这需要Windows防御者AV作为依赖项)。这些规则的目的是减少攻击者可以滥用或利用以获取系统上的代码执行的功能。最受推崇和最有效的ASR规则之一是“阻止Office应用程序创建子进程”。此规则将阻止作为Office应用程序的子进程生成进程的任何尝试[](https://p1.ssl.qhimg.com/t01a0fa82520766ab3f.png
"ASR阻止Office子进程")当你将OLE阻塞和ASR结合在一起时，通过网络在目标上执行代码的选项变得更加有限。大多数有用的文件类型不能通过Office
2016中新的OLE传递阻塞，ASR的子进程创建规则防止在Office应用程序下生成子进程的任何实例。

## 绕过方法

我们怎样才能绕过这些控制呢？我首先决定解决文件格式的问题。我花了很多时间在注册表中寻找可能允许执行的新文件格式。这些格式中的大部分都可以在HKCR:
registry hive的根目录中找到。这个过程涉及到将所有已注册的文件格式提取出来，然后查看它们，看看格式本身是否允许有什么有趣的东西。

在阅读了文件规范之后，我偶然发现了“.SettingContent-ms”文件类型。这种格式是在Windows 10中引入的，允许用户创建各种Windows
10设置页的“快捷方式”。这些文件只是XML，并包含各种Windows 10设置二进制文件的路径。一个示例.SettingContent-ms文件如下所示：[](https://p2.ssl.qhimg.com/t016e1980a5447e27dc.png
"Windows控制面板的.SettingContent-ms文件")这个文件所做的就是为用户打开控制面板。这个文件有趣的方面是<DeepLink>元素。此元素接受任何带有参数的二进制文件并执行它。如果我们简单地将“control.exe”替换为“cmd.exe/c
calc.exe”，会发生什么情况？[](https://p2.ssl.qhimg.com/t01a19b72b839530435.png
"用攻击者控制的值替换<DeepLink>元素")

如果我们双击该文件：[](https://p0.ssl.qhimg.com/t01e170bec34604521d.png
"执行修改后的SettingContent-ms文件")有趣的是，当双击文件时，没有“打开”提示符。Windows直接执行命令。

太棒了！因此，我们有一种文件格式，允许通过打开文件执行shell命令。这解决了初始访问的“使用什么文件格式”的问题。现在，我们怎样才能传播呢？我的下一个想法是看看如果这个文件直接通过一个链接从互联网上来会发生什么。

通过超链接直接从Internet执行SettingContent-ms文件，视频：<https://youtu.be/E4ywhiS8vF8>

令人吃惊的是当这个文件直接来自互联网时，一旦用户点击“打开”，它就会立即执行。查看该文件的流，您会注意到它确实捕获了Web标记：[](https://p2.ssl.qhimg.com/t019b72fcd2ead9a7af.png
"将MOTW广告应用于下载的文件")在联机查找[ZoneIds](https://blogs.msdn.microsoft.com/oldnewthing/20131104-00/?p=2753)时，“3”等于“URLZONE_INTERNET”。由于这样或那样的原因，该文件仍然在没有通知或警告用户的情况下执行。

因此，我们现在有了允许执行任意shell命令并没有向用户提示警告或对话的文件类型。在尝试获得初始访问权限时，使用不寻常的文件类型穿过目标的周界可能会有风险。理想情况下，这个文件应该放在一个更常见的文件类型的容器中，比如Office文档。

如前所述，Office 2016在嵌入对象链接和嵌入时会阻止预先设置的“已经知道是恶意”的文件类型列表。但是，SettingContent-ms文件格式不包括在该列表中：[](https://p4.ssl.qhimg.com/t0100717b01a60e8ba0.png "Office
2016 OLE阻止列表不阻塞SettingContent-ms文件")此时，我们可以通过OLE嵌入恶意的.SettingContent-ms文件来规避Office 2016
OLE文件扩展名阻塞：[](https://p2.ssl.qhimg.com/t018be77bb0ef68d029.png "Office 2016
OLE阻止列表不阻塞SettingContent-ms文件")当一个文档来自Internet并嵌入了一个.SettingContent-ms文件时，用户只能看到“Open Package Contents”提示符。单击“打开”将导致执行。如果环境没有启用任何Attack Surface
Reduction（ASR）规则，则攻击者只需在目标上执行代码即可。我很好奇，所以我深入研究了ASR的子进程创建规则是如何保持的。还值得注意的是，在本文发布时，如果Office是从Windows
Store安装的，则ASR规则似乎不适用于Office。

[启用这些规则](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-exploit-guard/enable-attack-surface-reduction)非常简单，可以通过一个PowerShell命令来完成：“Set-MpPreference
-AttackSurfaceReductionRules_Ids <rule ID>
-AttackSurfaceReductionRules_Actions Enabled”

<rule ID>参数是要启用的规则的GUID。您可以在[这里](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-exploit-guard/attack-surface-reduction-exploit-guard)找到记录的每个ASR规则的GUID。对于这个测试，我想启用子进程创建规则，它是GUID
D4F940AB-401b-4EFC-AADC-AD5F3C50688A。

启用该规则后，攻击将不再有效：[](https://p5.ssl.qhimg.com/t01a23de045a5c881e2.png "Attack
Surface Reduction规则SettingContent-ms执行")

由于该规则旨在阻止从Office应用程序派生子进程，因此我们执行了payload，但该规则阻止了该命令。这让我开始思考ASR是如何在不破坏某些功能的情况下实现这一点的。我首先开始测试随机路径中的随机二进制文件，看看ASR是否基于图像路径阻塞。这是相当耗时的，所以我没有深入。

最后，我退了一步，思考Office的哪些部分是工作所必须的。在运行ProcMon并在Word中单击时查看Process
Explorer一小段时间后，我注意到仍然有由Word生成的子进程。[](https://p3.ssl.qhimg.com/t0118e0370a491a1f72.png
"Word的有效子进程创建")

这是有意义的，因为Office需要使用依赖于其他程序的功能。我认为ASR规则可能基于图像路径阻塞子进程，但是当激活特性时，Office路径中的图像就可以生成。

为了测试这个理论，我将我的.SettingContent-ms文件更改为“Excel.exe”的路径：[](https://p3.ssl.qhimg.com/t016168f76c8e809f97.png
"将<DeepLink>元素改为Excel.exe")

下一步是将这个新文件嵌入到Word文档中，并查看ASR是否阻止了“Excel.exe”的生成。[](https://p0.ssl.qhimg.com/t010cbf839a5e20f0ae.png
"通过修改SettingContent-ms文件在winword下生成Excel")

有趣的是，ASR允许Excel启动。因此，子进程创建ASR规则似乎是基于白名单路径进行决策的。

这让我走上了一条漫长的道路，试图找到一个我可以使用的二进制文件，它存在于路径“C：ProgramFilesMicrosoftOffice”中。在浏览了其中的几个命令并将“C：windowsSystem
32cmd.exe”作为命令行中的一个参数传递给它们之后，其中一个执行了：[](https://p3.ssl.qhimg.com/t01f5bcdcf0f3149d2a.png
"通过ASR白名单“AppVLP.exe”执行命令")

完美！我们能够滥用“AppVLP”来执行shell命令。通常，这个二进制文件用于应用程序虚拟化，但是我们可以使用它作为一个滥用二进制文件来绕过ASR文件路径规则。为了测试这个完整的链，我更新了我的.SettingContent-ms 文件，如下所示：[](https://p2.ssl.qhimg.com/t01cf37498b5c3da476.png
"最终OLE/ASR逃逸的payload")现在，该文件只需要嵌入到Office文档中并执行：[](https://p3.ssl.qhimg.com/t010e6c2bd2b2c79634.png
"使用AppVLP.exe通过.SettingContent-ms和ASR实现OLE阻塞逃逸")

可以看到，启用Office 2016的OLE 阻塞规则和ASR的子进程创建规则后，.SettingContent-ms文件结合Office文件夹中的“AppVLP.exe”允许我们绕过这些控件并执行任意命令。

虽然Office文档通常用MOTW标记并在受保护[视图沙箱](https://support.office.com/en-us/article/what-is-protected-view-d6f09ac7-e6b9-4495-8e43-2bbcdbcb6653)中打开，但有些文件格式允许OLE，而不是由受保护视图沙箱触发。你可以在[这里](https://posts.specterops.io/phishing-against-protected-view-enigma0x3-on-wordpress-com-eed399fca512)找到更多的信息。

## 结论

在研究了ASR和Windows
10中的新文件格式之后，我意识到尝试和审计Windows每个版本中添加的新二进制文件和文件类型是很重要的。在这种情况下，.SettingContent-ms扩展允许攻击者在最新版本的Windows上运行任意命令，同时避开ASR和Office 2016
OLE阻塞。此外，尽管应用了MOTW，但文件类型似乎在打开后立即执行(甚至是从Internet上)。

## 防御

太好了，那你能做些什么呢？一个.SettingContent-ms文件不应该在“C：windowsImmersiveControlPanel”路径之外的任何地方执行。此外，由于文件格式只允许执行shell命令，因此通过该文件运行的任何内容都会受到命令行日志记录的影响。

始终监视来自Office应用程序的子进程创建也是一个好主意。应该在Office应用程序下生成一些应用程序，因此监视异常值可能很有用。实现这一目标的一个工具是Sysmon。

另一种选择是通过关闭文件处理程序来消除文件格式。我没有对此进行广泛的测试，也不能保证Windows中的某些东西不会因为这样做而中断。对于那些能处理程序关闭.SettingContent-ms文件格式的可能影响的人，可以将“HKLM：SettingContentShellOpenCommand”中的“DelegateExecute”键设置为空。同样，这可能会破坏操作系统的功能，所以请谨慎行事。

您可以在这里找到PoC SettingContent-MS文件：<https://gist.github.com/enigma0x3/b948b81717fd6b72e0a4baca033e07f8>

## 时间表

正如SPECTROPS致力于透明化(https：//posts.specterops.io/a-push-toward-transparency-c385a0dd1e34)一样，我们承认攻击者一旦公开使用新的攻击技术的速度。这就是为什么在公布一种新的攻击性技术之前，我们定期将问题通知各自的供应商，提供充足的时间来缓解问题，并通知选定的、受信任的供应商，以确保能够尽快向其客户发送检测结果。

  * 2018年2月16日：MSRC发送的报告
  * 2018年2月16日：MSRC确认了该报告，确定了案件编号
  * 2018年3月2日：MSRC确认他们可以在2018年4月24日前解决问题：
  * 2018年4月25日：请求更新情况：MSRC通知我案件处理程序发生变化。要求工程小组提供最新情况，并将尽快向我转告
  * 2018年6月1日：来自MSRC的另一请求
  * 2018年6月4日：提供另一最新情况：MSRC答复说，该问题的严重性低于服务标准，案件将结案。
  * 2018年6月11日：发表报告

本文翻译自posts.specterops.io [原文链接](https://posts.specterops.io/the-tale-of-settingcontent-ms-files-f1ea253e4d39)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **秋真平** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/147745](/post/id/147745)

安全客 - 有思想的安全新媒体

本文转载自: [posts.specterops.io](https://posts.specterops.io/the-tale-of-settingcontent-ms-files-f1ea253e4d39)

如若转载,请注明出处： <https://posts.specterops.io/the-tale-of-settingcontent-ms-files-f1ea253e4d39>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [渗透](/tag/渗透)
  * [Office](/tag/Office)
  * [技术分析](/tag/技术分析)
  * [windows安全](/tag/windows安全)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) 秋真平

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

