**作者：CybleBlogs  
译者：知道创宇404实验室翻译组  
原文链接：<https://blog.cyble.com/2022/12/01/ducklogs-new-malware-strain-spotted-in-the-wild/>**

## **恶意软件即服务为黑客提供复杂的功能**

Cyble研究和情报实验室（CRIL）一直在持续监控在野外新出现的活跃恶意软件家族。最近，CRIL观察到一种名为DuckLogs的新恶意软件，它执行多种恶意活动，如Stealer、Keylogger、Clipper、远程访问等。CRIL还在野外观察到DuckLogs
C&C服务器的多个活动实例，这表明恶意软件正在出现。

DuckLogs是MaaS（恶意软件即服务）。它窃取用户的敏感信息，如密码、cookie、登录数据、历史记录、加密钱包详细信息等，并将被盗数据从受害者的机器转移到其C&C服务器。下图显示了网络犯罪论坛中关于DuckLog的黑客
（TA） 广告。

![](https://images.seebug.org/content/images/2022/12/795fedab-781a-4457-b910-689ca59d51ec.jpg-w331s)
图1–网络犯罪论坛中的DuckLogs窃取者广告

TA还在帖子中声称该恶意软件具有多种功能，如下图所示。

![](https://images.seebug.org/content/images/2022/12/83a06f6a-fe97-47d2-ba1b-afe27cee2e6a.jpg-w331s)
图2–DuckLogs功能

TA通过三种不同的计划出售DuckLogs恶意软件，如下所示。

![](https://images.seebug.org/content/images/2022/12/e87a9ca3-9f9a-4fd6-997c-6aaf12787a11.jpg-w331s)
图3–DuckLogs恶意软件的价格详情

## Web面板：

DuckLogs提供了一个复杂的 Web 面板，允许TA执行多项操作，例如构建恶意软件二进制文件、监控和下载受害者的被盗日志等。DuckLogs
Web面板的登录页面如下所示。

![](https://images.seebug.org/content/images/2022/12/b9b40849-de7f-455b-a6a5-130373c70ed1.jpg-w331s)
图4–DuckLogs Web面板登录页面

下图显示了DuckLogs Web面板的仪表板页面，该页面显示了受DuckLogs恶意软件感染的受害者的总体全局统计数据。

![](https://images.seebug.org/content/images/2022/12/027b7144-905a-49c5-845d-4b2fd2e24c84.jpg-w331s)
图5–DuckLogs Web面板仪表板

TA还可以通过自定义Web面板的S设置页面上提供的选项来构建恶意软件二进制文件，如下所示。

![](https://images.seebug.org/content/images/2022/12/48750e52-a7c4-41e3-9db9-665d40a81caf.jpg-w331s)
图6–DuckLogs Web面板设置页面

下图显示了stealer和dropper的生成器页面，允许TA在设置页面上启用必要的功能后构建所需的有效负载。dropper生成器是Web面板中的附加功能，它构建另一个二进制文件，作为dropper将自定义DuckLogs恶意软件发送到用户的计算机。

![](https://images.seebug.org/content/images/2022/12/c7ce241f-efdf-4883-8ba2-4f06acca3508.jpg-w331s)
图7–Web面板生成器页面

## 技术分析

我们取了样本哈希（SHA256）， **
_e9bec9d4e28171c1a71acad17b20c32d503afa4f0ccfe5737171854b59344396进行分析_**
。它是一个名为 _“BkfFB.exe”_ 的32位.NET可执行文件。

执行BkfFB.exe时， _Main（）_ 函数解码名为“Bunifu.UI.dll”的硬编码base64编码模块，该模块存在于二进制文件中，并使用
_Invoke_ 方法将其加载到内存中，如图8所示。

![](https://images.seebug.org/content/images/2022/12/f7379ec5-a3ee-4f2c-9c2e-f82a0e688ae4.jpg-w331s)
图8–父文件加载Bunifu.UI.dll（阶段1有效负载）

## 第 1 阶段

新模块“Bunifu.UI.dll”是一个经过混淆的.NET文件，它进一步执行 _Bunifu_TextBox（）_
函数来检索父恶意软件文件BkfFB.exe的资源中存在的嵌入式位图图像“Gmtpo”。

该恶意软件使用隐写技术在压缩的位图图像中隐藏恶意内容。位图图像的成功解压将检索内存中的另一个.NET文件，即“ _MajorRevision.exe_
”，如图9所示。“Bunifu.UI.dll”模块现在使用 _Assembly.Load_ 方法加载“ _MajorRevision.exe”_
，将解压的位图内容作为参数传递，然后调用它。

![](https://images.seebug.org/content/images/2022/12/78da11b4-63a3-4ed3-8d4d-b7043ddf5feb.jpg-w331s)
图9–Bunifu.UI.dll加载MajorRevision（第2阶段有效负载）

## 第 2 阶段

在 **执行“MajorRevision.exe” _模块时，_ 它最初**将模块中存在的较大字节数组转换为十六进制值，其中包含多个反分析和反
**检测检查，以防止恶意软件在受控环境中执行，** 如下所示。

![](https://images.seebug.org/content/images/2022/12/e5b64713-c488-404c-8e22-2053c95023ed.jpg-w331s)
图10–MajorRevision内存中的反分析字符串.exe

在下一阶段，恶意软件通过转换另一个更大的字节数组来检索内存中的最终有效载荷（“DuckLogs.exe”），该数组也存在于“MajorRevision.exe”中。

最后，它通过使用如下所示的进程空心技术创建具有父文件名 （“BkfFB.exe”） 的新进程来注入有效负载。

![](https://images.seebug.org/content/images/2022/12/f02a8c54-eebd-4d4e-b61c-bceeaebec314.jpg-w331s)
图11–注入最终有效负载的过程

下图显示了最终恶意软件有效负载“DuckLogs.exe”的文件信息。静态分析表明，恶意软件有效负载是一个受Obfuscator（1.0）保护的32位.NET编译可执行文件。

![](https://images.seebug.org/content/images/2022/12/4b4b435d-813c-4245-a424-4a9f8d327dac.jpg-w331s)
图12–最终有效负载静态详细信息

## 最终有效负载分析

DuckLogs最终有效负载具有执行恶意活动的代码，例如stealer、keylogger和clipper功能。此外，该恶意软件还具有持久性、UAC
绕过、Windows defender绕过、禁用器、远程访问、文件抓取器等功能。

## 持久性和 UAC 绕过

执行后，恶意软件会在“启动”文件夹中创建自己的副本以建立持久性。将文件复制到 _启动_ 文件夹可使TA在用户登录受感染系统时自动执行恶意文件。

该恶意软件还绕过UAC（用户访问控制）并使用管理员权限自动执行。获得提升的权限后，攻击者可以在受害者的系统上窃取敏感数据、更改安全设置、安装其他恶意软件等。下图显示了DuckLogs用于执行持久性和UAC绕过的函数。

![](https://images.seebug.org/content/images/2022/12/d545730d-90d0-4807-80c7-09cac942c5fa.jpg-w331s)
图13–用于持久性和UAC绕过的函数

## Windows Defender Bypass

该恶意软件执行以下PowerShell命令以禁用受害者系统中的Windows Defender功能。

  * _“C：\Windows\System32\WindowsPowerShell\v1.0\powershell.exe” Uninstall-WindowsFeature -name Windows-Defender_

## Stealer

“Stealer”模块从已安装的浏览器中窃取书签、历史记录、cookie、下载和密码等信息，并从电子邮件客户端、信使、VPN等应用程序中窃取敏感信息。

窃取者还针对安装在受害者机器中的加密钱包，并将所有被盗信息发送给TA。下图显示了窃取程序模块使用的功能。

![](https://images.seebug.org/content/images/2022/12/e5b4531f-29d8-44f0-9ad6-90f7faef8977.jpg-w331s)
图14–窃取程序的功能

## Clipper

“Clipper”模块通过将受害者的钱包地址与TA的钱包地址交换来劫持加密货币交易。恶意软件使用Clipboard.GetText（）方法获取受害者的剪贴板数据，通过匹配正则表达式模式来识别受害者的加密货币钱包地址，然后Clipper使用
_Clipboard.SetText（）_ 方法将其替换为TAs钱包地址。

它支持加密钱包，如BCH（比特币现金），BTC（比特币），DOGE（狗狗币），ETH（以太坊），LTC（莱特币），XLR（Solaris），XMR（门罗币）和XRP（瑞波币）。下图显示了用于执行Clipper活动的代码段。

![](https://images.seebug.org/content/images/2022/12/3434c5ff-227e-4ffc-b592-e46136a4c4ca.jpg-w331s)
图15–Clipper的代码

## Keylogger

“Logger”模块监视并存储受害者机器中的击键。捕获的击键保存在%temp%文件夹中以便导出。下图显示了恶意软件用于Keylogger的代码片段。

![](https://images.seebug.org/content/images/2022/12/9ae03c18-8338-4937-bb80-af615bbddfe5.jpg-w331s)
图16–Keylogger的代码

## 禁用器

“禁用器”模块可以使用下图所示的功能，禁用受害者机器上的任务管理器、运行、CMD和RegEdit等功能。

![](https://images.seebug.org/content/images/2022/12/76214cc7-003d-4289-90d9-faab9371a871.jpg-w331s)
图17–禁用器功能

## 文件抓取器

“抓取器”模块从受害者的系统中获取与浏览器相关的文件，例如书签、历史记录、登录数据、LocalState和Cookie，并将其发送给攻击者。下图显示了文件抓取器模块所针对的浏览器名称。

![](https://images.seebug.org/content/images/2022/12/60ad4d9e-5410-4f9f-92f4-dded62150a8f.jpg-w331s)
图18–文件抓取器功能

## 远程控制

TA可以使用“控制”模块控制受害者的机器，并执行以下活动：

  * 在受害者机器中传输和执行其他文件。
  * 在浏览器中打开任何网址。
  * 关闭、重新启动、注销和锁定计算机。
  * 从系统中卸载恶意软件。
  * 发送消息。
  * 执行DoS（拒绝服务）攻击。
  * 显示蓝屏死机。
  * 禁用鼠标和键盘输入等。

下图显示了恶意软件用于执行远程控制活动的功能。

![](https://images.seebug.org/content/images/2022/12/629e15a4-62f1-4cba-a429-4e9e5f2ae884.jpg-w331s)
图19–远程访问控制代码

## 命令与控制

最后，恶意软件将所有敏感数据从受害者的机器泄露到其命令和控制（C&C）服务器 _ducklogs[.]com_ 。CRIL还观察到以下DuckLogs
C&C域名在野外活跃：

  * hxxps[:]//lovableduck[.]ru
  * hxxp[:]//ilovetheducks[.]ru
  * hxxp[:]//quackquack[.]ru
  * hxxps[:]//smallduck[.]ru

## 总结

DuckLogs是一种独特的组合，将Stealer、Keylogger和Clipper恶意软件捆绑到一个恶意软件包中，可以在网络犯罪论坛中以相对较低的价格获得，使这种威胁对更广泛的潜在受害者构成危险。

Cyble研究和情报实验室将继续监控野外的新恶意软件，并更新博客，提供可操作的情报，以保护用户免受此类攻击。

## 建议

  * 最初的感染可能通过垃圾邮件发生，因此企业应使用基于电子邮件的安全性来检测网络钓鱼电子邮件。还应避免在未验证其真实性的情况下打开不受信任的链接和电子邮件附件。
  * 编译的DuckLogs二进制文件由多层打包和保护。因此，建议在连接的设备（包括PC和笔记本电脑）上使用著名的防病毒软件。安全软件应具有最新的安全更新，以检测新的恶意软件系列，如DuckLogs。
  * DuckLogs能够执行Clipper活动。用户在进行任何加密货币交易之前应仔细检查他们的钱包地址，以确保在复制和粘贴实际钱包地址时没有变化。
  * 教育员工保护自己免受网络钓鱼/不受信任的URL等威胁。
  * 阻止可能传播恶意软件的URL，例如Torrent/Warez。

## MITRE ATT&CK®技术

**策略** | **技术ID** | **技术名称**  
---|---|---  
执行 | [T1204](https://attack.mitre.org/techniques/T1204/)
[T1059](https://attack.mitre.org/techniques/T1059/001/)
[T1047](https://attack.mitre.org/techniques/T1047/) | 用户执行PowerShell
Windows管理工具  
持久性 | [T1547系列](https://attack.mitre.org/techniques/T1547/001/) | 注册表运行键/启动文件夹  
权限提升 | [T1055系列](https://attack.mitre.org/techniques/T1055/) | 进程注入  
防御规避 | [T1562](https://attack.mitre.org/techniques/T1562/)
[T1497](https://attack.mitre.org/techniques/T1497/) | 禁用或修改工具虚拟化/沙盒规避  
发现 | T1057 [T1082](https://attack.mitre.org/techniques/T1082/)
[T1518](https://attack.mitre.org/techniques/T1518/) | 进程发现 系统信息发现 安全软件发现  
命令与控制 | T1071 T1105 [T1573](https://attack.mitre.org/techniques/T1573/)
[T1102](https://attack.mitre.org/techniques/T1102/) | 应用层协议 入口工具传输 加密通道 Web服务  
  
## IOC

IOC | IOC类型 | 描述 |  |  
---|---|---|---|---  
5bbbef641b0d73309939c16a8bb1621b c790ad50365158aecd4599ebab8db004bf9a9091
e9bec9d4e28171c1a71acad17b20c32d503afa4f0ccfe5737171854b59344396 | MD5 SHA1
SHA256 | BkfFB.exe （主文件） |  |  
58a0f68310f775b4bd4ea251064ed667 83c727335125f06b712cf4390bb9d265f77088a0
e15bf47074cc31f3445b3efb8ad75fac95ab085b5598cc82075902292ab8276b | MD5 SHA1
SHA256 | DuckLogs.exe （最终有效载荷） |  |  
Ducklogs[.]com | 域 | C&C |  |  
lovableduck[.]ru ilovetheducks[.]ru quackquack[.]ru smallduck[.]ru | 域 |
类似的C&C |  |  
179[.]43[.]187[.]84 | IP | C&C |  |  
hxxp://lovableduck[.]ru/host/drops/eYjqq6Ezx/ee48v958r[.]exe
hxxp://ilovetheducks[.]ru/host/drops/Gh879pKQj/btvM8o8sv[.]exe
hxxp://quackquack[.]ru/host/drops/g6tujhiry/hjt50kzbo[.]exe
hxxp://quackquack[.]ru/host/drops/Gh879pKQj/btvM8o8sv[.]exe
hxxp://quackquack[.]ru/host/drops/jgh1zyoel/fsgrvawrq[.]exe
hxxp://smallduck[.]ru/host/drops/ezQEvGqPI/nZAQiWiHm[.]exe
hxxp://smallduck[.]ru/host/drops/SrM7WQD2E/7s4udn5F1[.]exe
hxxp://smallduck[.]ru/host/drops/20NVT6CUe/9GseGAVEy[.]exe
hxxp://lovableduck[.]ru/host/drops/KI2kRAS0x/rrxgKvAJd[.]exe
hxxp://lovableduck[.]ru/host/drops/k1rf7fmny/lr2xfd9m9[.]exe
hxxp://ilovetheducks[.]ru/host/drops/e563bgj4y/hrldcrajl[.]exe
hxxp://ilovetheducks[.]ru/host/drops/JTQ4iHTm3/wT9lPlvPK[.].exe | URL | 有效载荷 |
|  
|  |  |  |  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2034/>

