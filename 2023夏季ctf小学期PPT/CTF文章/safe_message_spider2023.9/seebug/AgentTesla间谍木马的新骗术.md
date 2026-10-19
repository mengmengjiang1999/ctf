**原文链接：[https://labs.sentinelone.com/](https://labs.sentinelone.com/agent-tesla-old-rat-uses-new-tricks-to-stay-on-top/ "https://labs.sentinelone.com/")  
译者：知道创宇404实验室翻译组**

Tesla
RAT（远程访问特洛伊木马）已成为2020年上半年威胁企业的最流行的恶意软件系列之一，被发现的攻击次数甚至超过TrickBot或Emotet，仅次于Dridex
。尽管Agent
RAT代理已经存在了至少6年，但它仍在不断适应和发展，挫败了许多组织的安全工作。在COVID-19大流行期间，引入了具有附加功能的新变种，并且该恶意软件已广泛用于以冠状病毒为主题的网络钓鱼活动中。

## AgentTesla | 背景与概述

AgentTesla的核心是键盘记录程序和信息窃取者。AgentTesla于2014年底首次发现，在过去的1-2年中，其使用量一直稳定增长。该恶意软件最初在各种地下论坛和市场上出售，还有它自己的AgentTesla.com网站（现已停产），与许多同时代代理商一样，AgentTesla也提供了该恶意软件本身以及数据收集管理面板，从被攻击设备获取的信息可以通过面板界面快速获得给攻击者。

![img](https://images.seebug.org/content/images/2020/08/13/1597308474000-Teslasite_1_edit.jpg-w331s)

最初推出时，可以购买各种“包”。每个软件包的基本区别在于许可期限和构建/更新的访问权限。当时，价格颇具竞争力，1个月的许可证售价为12.00美元，一直到6个月的许可证售价为35.00美元。还值得注意的是，与许多其他这种性质的工具一样，AgentTesla大力的破解版很快出现。

AgentTesla的早期版本还吹捧了全套功能，正如人们希望在现代RAT中发现的那样，其中包括：

  * 多国语言支持
  * PHP Web面板
  * 付款后自动激活（针对直接客户）
  * 24/7支持
  * 稳定快速地执行
  * 按键日志，屏幕截图和剪贴板提取的多种交付方式
  * 支持多种Windows版本（XP或更高版本）

![img](https://images.seebug.org/content/images/2020/08/13/1597308484000-Teslasite_4.jpg-w331s)

## 投放机制

像许多其他威胁一样，AgentTesla的主要传递机制是电子邮件（网络钓鱼邮件）。攻击者通常会及时处理其社交工程诱饵，并且当前的流行COVID病毒并未对攻击者构成限制。在过去的几个月中，观察到攻击者通过以COVID为主题的消息传播AgentTesla，这些攻击者常常伪装成来自WHO（World
Health Organization）的最新消息。

![img](https://images.seebug.org/content/images/2020/08/13/1597308484000-Email_Spam_Tesla_Covid.jpg-w331s)

AgentTesla活动背后的参与者也使用了恶意的Office文档来促进第一阶段的交付。即使在当今的活动中，也利用了利用Office漏洞（例如[CVE-2017-11882](https://nvd.nist.gov/vuln/detail/CVE-2017-11882)和[CVE-2017-8570）](https://nvd.nist.gov/vuln/detail/CVE-2017-8570)制作的特制文档。这些以及类似漏洞允许在最少用户交互的情况下快速交付和执行（除了打开恶意文档并允许活动内容进行之外）。

## 新AgentTesla变体的功能集

随着时间的推移，AgentTesla已添加了其他功能。这些改进包括更强大的扩展和注入方法，以及无线网络详细信息和凭据的发现和盗窃。

目前，AgentTesla继续用于各种攻击阶段。其持久地管理和操纵受害者设备的能力仍然吸引了低级犯罪分子。AgentTesla现在能够从许多常见的VPN客户端，FTP和电子邮件客户端以及Web浏览器中获取配置数据和凭据。该恶意软件具有从注册表、相关配置或文件中提取凭证的能力。我们对当前AgentTesla样本的分析揭示了以下目标软件列表：

![img](https://images.seebug.org/content/images/2020/08/13/1597308484000-tesla_target_app_code_2.jpg-w331s)
![img](https://images.seebug.org/content/images/2020/08/13/1597308484000-tesla_target_app_code_1.jpg-w331s)

  * 360浏览器
  * 苹果Safari
  * Becky！互联网邮件
  * 黑鹰
  * Brave
  * CentBrowser
  * CFTP
  * Chedot
  * Chromium
  * Citrio
  * 爪子邮件
  * 可可
  * 科摩多巨龙
  * 酷诺
  * 核心FTP
  * CyberFox
  * 元素
  * Epic Privacy
  * FileZilla
  * FlashFXP
  * Flock
  * 谷歌浏览器
  * 冰猫
  * 冰龙
  * IncrediMail
  * IncrediMail
  * KMeleon
  * IncrediMail
  * 猎宝
  * Microsoft IE和Edge
  * Microsoft Outlook
  * 火狐浏览器
  * Mozilla雷鸟
  * 开放VPN
  * 歌剧
  * 歌剧邮件
  * 轨道
  * 苍白的月亮
  * 邮箱
  * QIP冲浪
  * 高通Eudora
  * 海猴子
  * Sleipnir 6
  * SmartFTP
  * 人造卫星
  * 腾讯QQ浏览器
  * 球棒！电子邮件
  * 火炬
  * Trillian Messenger
  * UC浏览器
  * 乌兰
  * 维瓦尔第
  * 狐狸
  * WinSCP
  * Yandex

收集的数据通过SMTP或FTP传输到C2。传输方法取决于恶意软件的内部配置，其中还包括攻击者C2的凭据（FTP或SMTP）。

当前变体通常会删除或检索要注入的辅助可执行文件，或者它们将尝试注入目标主机上已经存在的已知（易受攻击）二进制文件。

例如，正如我们在示例中所看到的`4007480b1a8859415bc011e4981f49ce2ff7a7dd7e883fe70d9f304cbfefedea`，随后将RegAsm.exe的副本（放入％temp％中）注入了其中。然后，该RegAsm.exe的新实例将负责处理恶意活动（数据收集泄漏）。我们还可以看到经常使用“
[过程空心](https://attack.mitre.org/techniques/T1055/012/)
”作为注入方法。进程空洞允许创建或操作进程，通过该过程可将内存部分与该空间解除映射（空洞），然后使用所需的恶意代码进行重新分配。

一些示例在过程创建和后续注入方面的创意很少。例如，在sample中`b74bcc77983d587207c127129cfda146644f6a4078e9306f47ab665a86f4ad13`，我们可以观察到它在％temp％中创建隐藏的文件夹和进程，并将这些隐藏的进程实例用于主要感染例程，并用作持久进程（通过注册表设置）

    
    
    /c copy "C:/Users/admin1/Desktop/tes_10.exe" "%temp%\FolderN\name.exe" /Y

![img](https://images.seebug.org/content/images/2020/08/13/1597308484000-tesla_hidden2.jpg-w331s)
![img](https://images.seebug.org/content/images/2020/08/13/1597308484000-tesla_hidden1.jpg-w331s)

## 执行行为

启动后，恶意软件将开始收集本地系统信息，安装键盘记录器模块以及初始化来发现和收集数据的例程。此过程的一部分包括基本的WMI查询。示例包括：

    
    
    start iwbemservices::execquery - select * from win32_operatingsystem
    start iwbemservices::execquery - select * from win32_processor

能够发现无线网络设置和凭据的最新示例将在短暂的睡眠时间（启动后）之后生成netsh.exe实例。最初使用的语法是：

    
    
    Netsh.exe wlan show profile

持久性通常是通过注册表项输入或计划任务来实现的。

例如，在示例中`7ec2b40879d6be8a8c6b6ba239d5ae547604ad2605de0d2501a4cca25915afa1`，将可执行文件的副本放入?\
AppData \ Local \ Temp中，并使用以下语法作为目标，以生成持久性任务：

    
    
    Schtasks.exe /Create /TN "Updates\xjZWstBWrIuw" /XML C:\Users\xxxxxx\AppData\Local\Temp\tmp1718.tmp"

![img](https://images.seebug.org/content/images/2020/08/13/1597308484000-tesla_sched_task_1_post.jpg-w331s)

在样本中`b74bcc77983d587207c127129cfda146644f6a4078e9306f47ab665a86f4ad13`，我们看到了一个通过注册表建立持久性的示例。启动后，恶意软件实例将作为隐藏文件放入隐藏文件夹中的％temp％。

    
    
    /c copy "C:/Users/admin1/Desktop/tes_10.exe" "%temp%\FolderN\name.exe" /Y

然后，以下命令用于创建自动运行注册表项：

    
    
    /c reg add "HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows" /v Load /t REG_SZ /d "%temp%\FolderN\name.exe.lnk" /f

## 结论

AgentTesla已经存在了几年，但我们看到它仍然被当作一个商品在许多的复杂攻击中被利用。攻击者不断进步，并找到成功逃避检测的使用AgentTesla等工具的新方法。归根结底，如果目标是收集和窃取数据，则攻击者将继续努力。因此，我们仍然看到像AgentTesla这样的“商品”工具，以及Pony，Loki和其他低挂水果恶意软件。与当时的社会工程学诱饵相结合时，这些非复杂的攻击将继续成功。检测和预防是减少暴露于这些威胁的关键。所述[SentinelOne平台](https://www.youtube.com/watch?v=mhJGzfzymME&feature=youtu.be)完全能够检测和防止基于AgentTesla恶意活动。

## IOC

**MITER ATT＆CK**

修改注册表（[T1112](https://attack.mitre.org/techniques/T1112/)）  
颠覆信任控件：安装根证书（[T1553.004](https://attack.mitre.org/techniques/T1055/012/)）  
隐藏工件：NTFS文件属性（[T1564.004](https://attack.mitre.org/techniques/T1564/004/)）  
劫持执行流：DLL搜索顺序劫持（[T1574.001](https://attack.mitre.org/techniques/T1574/001/)）  
进程注入：进程空心（[T1055） .012](https://attack.mitre.org/techniques/T1055/012/)）  
信息存储库中的数据（[T1213](https://attack.mitre.org/techniques/T1213/)）  
引导或登录自动启动执行：注册表运行键/启动文件夹（[T1547.001](https://attack.mitre.org/techniques/T1547/001/)）  
进程注入（[T1055](https://attack.mitre.org/techniques/T1055/)）  
不安全的凭据：文件中的凭据（[T1552.001](https://attack.mitre.org/techniques/T1552/001/)）  
系统信息发现（[T1082](https://attack.mitre.org/techniques/T1082/)）  
查询注册表（[T1012](https://attack.mitre.org/techniques/T1012/)）  
OS凭证转储（[T1003](https://attack.mitre.org/techniques/T1003/)）  
计划任务（[T1053](https://attack.mitre.org/techniques/T1053/)）

**SHA256**

70aecc29ffb60caf068e4d8107f4d53fcdbd333bed7ac6fb3a852b00e86ded31  
7d1bcec8a3f71910e15cbb3adae945cd5096b7de259b51aef8f2e229bd4b40e2  
7ec2b40879d6be8a8c6b6ba239d5ae547604ad2605de0d2501a4cca25915afa1  
9b27388be292aea50d62cfebd130a9832f0d676feb28771d70d3e30bdb117f3a  
a040efaf5dfac863805103ea0aa90a15b3690ad060188a15ea7d68491b274123  
aa08d96a25908ce76e07475aefbbe192bd812665a5600dc30600688510dd033e  
be26ad023b732078c42b4f95067fb9107fe88aebd7ebbf852e7e968e50eee8a0  
1abf66ab839c550bc77d97d1644c1225935a86b9591e9a95bcd606ebec6bbc19  
b74bcc77983d587207c127129cfda146644f6a4078e9306f47ab665a86f4ad13  
f44c6c8c1c81f9990f11a0f70e6517c358fc1ee00a78b32461d4a2594b48e47d  
9fee57918672137160499dcd1a099670ef8f9a787f3a1ad6d8123df26cddbc3b  
4007480b1a8859415bc011e4981f49ce2ff7a7dd7e883fe70d9f304cbfefedea  
590c19542f6959d6424107eb4f2998b04d035575341b1f23a40dea6d82aecadd  
648261052662b044dc233349ccdfa9dfd6853ec9a21ced386f8f172b2568b0d1  
f24018dead69b0f899d33e73f72f5c3ef6f3c391850484b06b042f36dbc08cac  
7ce7bf11f6285621381b80027c488e9b5009205131a89738975ccc89574a1533  
e2473526523180f460af4d8e164df9060c9f328cc7c0bae5846d51b28c12febe  
7adc0e8236262080e62c4bfb97e745880247f9e244ae8718e60cc217a3ae773b  
0107fadc185fd6b53dc033d4a79e53ef1621ae623917de029b6c02eeae2021c1  
388386f3361138514c561dcf6169e8f9e8726c91e2dc66663efb07bf21ece052  
507b63c73ba3bee19c8c8afb40526c1196240376277f4b49e25bedc5d866b980

**SHA1**

a2ad3ec4cd2d70edf2bc9089c493f898b7da44a5  
8f841e8f7d2c3334145c8c9f89c8cd6929a06b2a  
3390272bb793ad15a45d647c3e5a716145fd262a  
8cd26c88b74f913f6e1c9d71a8d1e9aa53b7c6f6  
160c5583f9ba3d11e94a0dd8c9a64936981e8194  
859f498f0ba963e468a3912d936ad8e7ec01dbcd  
90fc8a737a7030db2e3583cbccb3156bb0a8ff12  
683efb5746e85867b5d613dc07a116a80becce58  
6c2d55f7fcecdcae779b148f0060b8ab4062e0a9  
7617dc78df626d5df43e38506fa7c577baef4bc5  
05d74461b2a63b75f319ef2c5c4aa074af4e97c3  
9e9c8ef7f20677795684b2749a59367cf5c3ec0a  
3e15c7c82b875c3553456dc08a8b79019cb48644  
7e674dd61f0802316bc092ffd44f5b8a36ab26d5  
7cf661644a638dcb554a81ba490ddcaee2ed6f12  
5b744ce5d3cccd556d66704d8fdde882ea928829  
94277994af62de5948d6de134edac0089a54b71e  
3ce8f4bfeb99fa2fb8898c7664ad3838ce4a4fcf  
4ffa900d7cf3ae6414bf90f6c9a4667cedfd57dd  
83be2722b7adc91bc3ee219b75e9176bc7ce8e6e  
72d3d907d7502c383ffc8239d255882838a5a6e4

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1293/>

