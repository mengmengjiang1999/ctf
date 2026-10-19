## 概述

**我们一直在跟踪Trickbot银行木马活动，最近在垃圾邮件中发现了一个Trickbot变种（TrojanSpy.Win32.TRICKBOT.TIGOCDC），其中包含带启用宏的Microsoft
Word文档。 单击文档后，它会执行一个混淆的JS文件，并下载Trickbot作为其有效负载。
此恶意软件还会检查受影响计算机中正在运行的进程数，如果它检测到位于虚拟环境中，则恶意软件将不会继续执行其进程。**  

除了信息窃取功能之外，它还会删除具有特定扩展名的文件，然后将文件替换为恶意软件的副本。 Trickbot活动对美国影响最大。
它还向中国，加拿大和印度发送了垃圾邮件。

  

![1.jpg](https://image.3001.net/images/20190808/1565229385_5d4b814965c2e.jpg!small)图1
恶意软件工作流程

## 技术细节

在示例电子邮件中，垃圾邮件声称是广告提供商的订阅通知，通知用户已经提交了三年订阅的申请并与发件人进行结算。
邮件随后解释，在交易中将向用户的卡收取更多费用，从而诱导用户查看所有结算和订阅信息的附加文档，文档中包含了恶意脚本。  

Word文档向用户显示以下通知（参见图2），该通知指出可以通过启用宏内容来查看内容。
该文档将JS脚本隐藏在文档本身而不是宏中，它通过使用与文档背景相同的字体颜色伪装脚本。

  

![2.jpg](https://image.3001.net/images/20190808/1565229523_5d4b81d3f0943.jpg!small)

图2 Word文档

恶意脚本经过混淆并有不同的功能。其解密函数如下图所示：

  
![3.png](https://image.3001.net/images/20190808/1565229566_5d4b81fe42b9f.png!small)

图3 解密函数

  

在对文件进行反混淆处理后，我们能够对其进行进一步分析并观察其行为。
执行时，它将显示一个假的Microsoft错误，以欺骗用户，并在启用宏后弹出一条错误消息。 但实际上，JS文件已经在后台运行。  

![4.png](https://image.3001.net/images/20190808/1565229622_5d4b823617859.png!small)

图4 伪造的Microsoft错误提示  

  

为了持久控制受害者计算机，恶意软件将自身的副本命名为Shell.jse保存在Startup文件夹。JS文件还检查正在运行的进程，它检查受害者计算机中所有正在运行的进程的总数，若没有足够的进程，恶意脚本不会进行其他的操作，该策略是为了达到反分析的目的。  

如果正在运行的进程少于1,400个字符（字符串的长度），则恶意软件会将其视为在虚拟或沙箱环境中运行。 它还将检查通用于分析的进程是否存在。
除此之外，恶意软件会检查其运行的环境是否与特定用户名相关。  

![5.png](https://image.3001.net/images/20190808/1565229706_5d4b828a4e302.png!small)图5
进程和用户名检测  

![6.jpg](https://image.3001.net/images/20190808/1565229743_5d4b82afa4eea.jpg!small)图6
异常退出界面  

  

以下是恶意软件在受影响系统中检查的进程和调试工具列表：  

> AgentSimulator.exe
>
> B.exe
>
> BehaviorDumper
>
> BennyDB.exe
>
> ctfmon.exe
>
> DFLocker64
>
> FrzState2k
>
> gemu – ga.exe
>
> iexplore.exe
>
> ImmunityDebugger
>
> LOGSystem.Agent.Service.exe
>
> lordPE.exe
>
> ProcessHacker
>
> procexp
>
> Procmon
>
> PROCMON
>
> Proxifier.exe
>
> tcpdump
>
> VBoxService
>
> VBoxTray.exe
>
> vmtoolsd
>
> vmware
>
> VzService.exe
>
> windanr.exe
>
> Wireshark
>
>  
>
>
> 经过进一步分析，恶意软件检查的用户名如下：  
>
>
> Emily
>
> HAPUBWS
>
> Hong Lee
>
> Johnson
>
> milozs
>
> Peter Wilson
>
> SystemIT | admin
>
> VmRemoteGuest
>
> WIN7 – TRAPS

对于恶意软件的payload，它将连接到URL：185.159.82.15/hollyhole/c644.php然后检查要下载的文件。
如果是可执行文件，会将文件保存为％Temp％{random} .exe并在之后执行。 如果该文件不是可执行文件，则会将其作为{random}
.cro保存在同一文件夹中。 然后使用certutil.exe解码.cro文件，命名为{random} .exe保存在同一目录中，然后执行。
经过进一步研究，我们发现下载的.exe文件是Trickbot恶意软件的变种。

![7.png](https://image.3001.net/images/20190808/1565229799_5d4b82e770c2d.png!small)

图7 下载、重命名、保存、执行流程代码

除了窃取OS，CPU和内存信息等系统信息外; 也会收集用户帐户; 安装的计划和服务; IP配置;
和网络信息（配置，用户和域设置），还会从应用程序和Internet浏览器收集以下凭据和信息。

 _ ___应用程序信息： _ ___  

> Filezilla
>
> Microsoft Outlook
>
> PuTTy
>
> Remote Desktop (RDP)
>
> VNC
>
> WinSCP

浏览器凭据和信息（Google Chrome，Internet Explorer，Microsoft Edge和Mozilla Firefox）：  

> 自动填充数据  
>
>
> 表单数据
>
> 浏览记录
>
> 信用卡数据
>
> HTTP POST响应
>
> cookie
>
> 用户名和密码

此恶意软件还使用名为psfin32的PoS（point-of-sale）提取模块，该模块识别位于感兴趣的域中的PoS相关术语。
该模块使用LDAP查询在具有以下子字符串的计算机上搜索PoS信息：

> *ALOHA*
>
> *BOH*
>
> *CASH*
>
> *LANE*
>
> *MICROS*
>
> *POS*
>
> *REG*
>
> *RETAIL*
>
> *STORE*
>
> *TERM*

该变体还会安装shadnewdll代理模块，用于拦截和修改受影响设备上的Web流量，通过流量修改进行虚假银行交易。
该模块与银行木马IcedID有相似之处，后者将受害者重定向到虚假的在线银行网站。

在恶意软件无法连接的情况下，它将在计算机中搜索具有以下扩展名的文件。  

> .doc
>
> .xls
>
> .pdf
>
> .rtf
>
> .txt
>
> .pub
>
> .odt
>
> .ods
>
> .odp
>
> .odm
>
> .odc
>
> .odb

具有上述扩展名的文件将保存在％Temp％文件夹中的ascii.txt。 然后将所有文件删除并替换为恶意软件和扩展名.jse的副本（但实际上是JS文件）。

![8.png](https://image.3001.net/images/20190808/1565229990_5d4b83a6d705a.png!small)

图8 扫描替换文件代码片段

## 解决方案

据报道，Trickbot已窃取超过2.5亿个帐户。新变体展示了网络犯罪分子如何不断调整现有的银行木马以增加新功能。但是，用户只需遵循垃圾邮件的最佳处理方法就可防止这些攻击。

除了意识到垃圾邮件的特殊标记，例如可疑的发件人地址和明显的语法错误，我们还建议用户不要打开未经验证的电子邮件附件。用户和企业也可以使用多层方法来抵御Trickbot等威胁所带来的风险。

## IoCs

![9.PNG](https://image.3001.net/images/20190808/1565230055_5d4b83e7e5d84.png!small)

 ***参考来源：[TrendMicro](https://blog.trendmicro.com/trendlabs-security-intelligence/latest-trickbot-campaign-delivered-via-highly-obfuscated-js-file/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Anti-MalwareBlog+%28Trendlabs+Security+Intelligence+Blog%29)，由Kriston编译，转载请注明来自FreeBuf.COM**

