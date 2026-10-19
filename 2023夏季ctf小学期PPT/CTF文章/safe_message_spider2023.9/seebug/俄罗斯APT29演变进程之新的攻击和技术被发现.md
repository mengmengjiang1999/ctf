**原文链接：[Evolution of RUSSIAN APT29 – New attacks and techniques
uncovered](https://www.avertium.com/resources/threat-reports/evolution-of-russian-apt29-new-attacks-and-techniques-uncovered "Evolution of RUSSIAN APT29
– New attacks and techniques uncovered")  
译者：知道创宇404实验室翻译组**

## 摘要

2020年12月，总部位于德克萨斯州的IT监控管理平台 SolarWinds 遭到威胁行为组织 APT29(也被称为Nobelium、Cozy
Bear和Midnight
Blizzard)的攻击。该组织通过将恶意代码植入Orion（一款监控公司网络内各种组件的软件程序）软件程序成功入侵了该公司，随后发起了针对美国的大规模网络攻击。

当涉及到异常复杂的恶意软件攻击时，APT29 总是会被提及，而SolarWinds
的漏洞标志着威胁组织将持续进行恶意软件攻击。自从SolarWinds遭到攻击以来，APT也一直在对政府、国防、制造业和IT服务商们进行着攻击。在近期的攻击事件中，该组织通过利用着少有人知道的Windows功能，将目标瞄准了驻乌克兰的外交官们。具体内容，且看下文介绍。

### 事件概述

  * 多年以来，俄罗斯黑客组织APT29参与了多项恶意软件攻击事件，而SolarWinds漏洞只是他们持续存在的开始。
  * 2021年8月，APT29试图利用一个名为ProxyShell的Exchange漏洞集群(CVE-2021-31207, CVE-2021-34523, CVE-2021-34473)。
  * 2021年10月，微软发布了关于APT29再次攻击全球IT服务商。该事件于2021年5月开始，目前确认已导致14起确认的泄密事件，波及范围包含 140家公司。
  * 观察到APT29依赖于各种技术，包括密码喷射、API滥用、网络钓鱼和令牌盗窃，以获得凭证和对受害者系统的特权访问。
  * 2022年，APT29与另一个“高度针对性”的恶意软件有关，该恶意软件能够持续访问受损环境。微软威胁情报团队将这一开命名为MagicWeb，并重申了APT29致力于开发和维护专用功能的承诺。
  * 2022年，黑客组织APT29被发现利用了一个鲜为人知的Windows功能——凭据漫游(Credential Roaming)。这个漏洞是在对一个未指明的欧洲外交实体进行成功的网络钓鱼攻击后曝光的。
  * APT29在2023年4月的间谍活动中使用之前未记录的恶意软件攻击北约和欧盟成员国的外交部门。波兰军事反情报机构和波兰CERT (CERT. pl)发现了这一活动，其中包括APT29向外交人员发送鱼叉式网络钓鱼电子邮件。

## APT29相关事件回顾

### 2021年

多年来，俄罗斯黑客组织APT29 参与了多项恶意软件攻击事件，而SolarWinds漏洞只是他们持续存在的开始。

2021年8月，APT29试图利用一个名为ProxyShell的Exchange漏洞集群(CVE-2021-31207, CVE-2021-34523,
CVE-2021-34473)。此漏洞允许威胁参与者在未打补丁的Exchange服务器上部署web
shell以供以后访问。尽管有安全补丁可用，但由于未能更新服务器，组织仍然容易受到攻击。

同年，APT29将攻击重点转移到软件和云服务经销商。这些攻击影响了150多个组织的3000个个人账户。针对每个目标，他们采用专有的模式和配置借此来逃避被检测。

APT29利用SUNBURST后门、TEARDROP恶意软件和GoldMax恶意软件对SolarWinds进行供应链攻击。同时还通过恶意软件，对美国的9个政府机构(国土安全部、CISA、美国财政部等)及100家私营公司发起了攻击。主要是通过获得访问权限后，对受害者的网络内容进行研究，同时也将入侵目标瞄准于Microsoft
365和Azure。

此外，APT29还秘密地将软件后门集成到SolarWinds发布的网络管理程序中，从而进行间谍活动。攻击者还引入了新的Azure身份，并提升了现有身份的权限，以此操纵微软程序来进行电子邮件盗窃。由于该次事件的成功实施，APT29已经渗透到网络安和基础设施安全局。

2021年10月，微软发布了关于APT29再次攻击全球IT供应商的警告。该事件于2021年5月开始，目前确认已导致14起确认的泄密事件，波及范围包含
140家公司。

在此期间，观察到APT29通过各种技术（包括密码喷洒、网络钓鱼和令牌盗取）获得凭证来对受害者进行相关访问。

微软认为，APT29使用了一种名为FoggyWeb的远程访问恶意软件，在受感染的Active Directory联合服务服务器(AD
FS)上建立持久性。而这种持久化后门是在2021年4月被首次发现的。

### 2022

2022年，APT29被发现与另一个“高度针对性”的后门软件有关，该恶意软件能够持续访问受损环境。微软威胁情报团队将这一开发称为MagicWeb，重申了APT29致力于开发和维护专用功能的承诺。

MagicWeb与另一个名为FoggyWeb的工具有相似之处，据报道了解，在修复工作期间，MagicWeb在获得对环境的高度特权访问并横向移动到AD
FS服务器之后可以被部署到维护访问上避免被驱逐。

虽然FoggyWeb具有提供额外有效负载和从Active Directory Federation Services (AD
FS)服务器窃取敏感信息的专门功能，但MagicWeb是一个恶意的DLL(“Microsoft.IdentityServer.Diagnostics.dll”的后门版本)，可以通过绕过身份验证来隐蔽访问AD
FS系统。

在此之前，APT29 主导的一项针对北约附属组织的活动被披露，其目的是获取外交政策信息。 具体来说，这涉及禁用名为 Purview
Audit（以前称为高级审核）的企业日志记录功能，通过它来从Microsoft 365帐户中收集电子邮件。
攻击者在此期间使用的另一种新策略是使用密码分析攻击来获取与休眠帐户关联的凭据，并将其注册为多重身份验证 (MFA)，从而授予其访问组织 VPN
基础设施的权限。

#### Windows漫游凭证事件

此外，在2022年，APT29被发现利用了一个鲜为人知的Windows功能——凭据漫游。
在对一个未指明的欧洲外交政体进行成功的网络钓鱼攻击后，这一漏洞被曝光。
Mandiant在2022年初发现攻击者在受害者网络中使用了凭据漫游。当时，APT29对Active
Directory系统执行了“大量具有不寻常属性的LDAP查询”。

凭据漫游是Windows Server 2003 Service Pack 1
(SP1)中引入的一项功能，它使用户能够跨Windows域内的各种工作站安全地访问其凭据，例如私钥和证书。微软解释称：凭据漫游将用户凭据存储在ms-PKI-dpapimasterkeys和ms-PKI
AccountCredentials两个属性之中。后者是一个多值LDAP属性，包含二进制大对象(blob)中的加密凭证对象。

Mandiant发现了一个任意文件写入漏洞，可以允许攻击者在登录受害者的账号中实现远程代码执行。该追踪漏洞被命名为CVE-2022-30170
(CVSS评分7.3)，微软在2022年9月13日补丁星期二更新中解决了这个问题。同时该公司表示，如果要执行漏洞，需要用户进行Windows
登录。而这一漏洞如果被成功利用，APT29将获得受害者计算机的远程交互式登录权限。

## 近期攻击

### 波兰政府事件

2023年4月，APT29针对北约和欧盟成员国的外交部门进行了间谍活动。该操作利用了以前未记录的恶意软件有效载荷。波兰军事反情报机构和波兰CERT
(CERT.
pl)发现了这一活动，其中包括APT29向外交人员发送鱼叉式[网络钓鱼电子邮件](https://explore.avertium.com/resource/ebook-7-common-indicators-of-a-phishing-attempt "网络钓鱼电子邮件")。

这些电子邮件通过伪装成来自欧洲大使馆的信息，来诱骗相关用户打开邮件。邮件包含PDF附件，伪装的会议日程及链接。在点击链接后，会通过使用JavaScript代码解码有效载荷的网页，相关邮件内容也可以进行下载。

![](https://images.seebug.org/content/images/2023/08/d55cfd65-cef9-4e25-abcf-2cfe4bdb6071.jpg-w331s)
图一：攻击邮件（图片来源：Source: CERT.pl）

APT29过去主要使用.iso文件进行恶意软件分发，但目前已经引入了新的.IMG文件技术。当这些文件在Windows中打开时，会被自动挂载为虚拟磁盘，并允许用户访问其中的文件。在这种情况下，这些文件会触发Windows快捷方式(LNK)，然后加载恶意DLL。

这种技术被称为DLL侧加载，攻击者从已知的应用程序中提供可执行文件，以从同一目录加载具有特定名称的DLL库，而攻击者仅仅提供一个具有相同名称的恶意DLL来负载该文件。通过利用合法文件将恶意代码加载到内存中，以此来逃避安全工具的检测。

该攻击的初始有效载荷被波兰研究人员称为SNOWYAMBER——一个轻量级的定制恶意软件发射器，其可收集基本的计算机信息，并与Notion上的命令和控制服务器进行通信链接。该软件的主要目标是下载并执行其他恶意软件，包括Cobalt
Strike和BruteRatel信标（一种商业开发后框架，最初是为渗透测试人员设计的，但也被攻击者采用）。

尽管在2022年10月已经有报道指出SNOWYAMBER这种变体，但在2023年2月，波兰研究人员发现了一种具有增强反检测程序的新变体。APT29还利用了另一种名为HALFRIG的有效载荷，SNOWYAMBER不同的是，它从shellcode中解密了Cobalt
Strike，而不是依赖于命令和控制服务器进行下载。

三月份，黑客们使用了另一种名为QUARTERRIG的工具，与HALFRIG共享了它的部分代码库。此时，APT29的目标列表包括外交实体(大使馆、外交人员、外交部等)、政府实体、国际组织和非政府组织。虽然攻击主要集中在欧盟和北约实体，但一些目标位于非洲。

### 驻乌克兰外交官事件

2023年6月，APT29发起了一场有针对性的行动，旨在入侵驻乌克兰大使馆的众多外交官的电脑。alo Alto Networks 的Unit
42研究部门透露，这种大规模的间谍活动主要集中在乌克兰首都基辅的80个外国使团、22个使团的外交官中。

2023年4月中旬，波兰外交部的一名外交官向各国大使馆发出了一份合法宣传单，用来宣传在基辅出售的一辆二手宝马5系轿车。APT29拦截并复制了该传单，在将其嵌入恶意软件后，发布给了在基辅工作的数十名外交官。

这位波兰外交官表示，他已经购买意向进行了邮件回复，因为价格看起来“很诱人”（价格其实是跌破了市场正常值），也有人给他回了电话。结果，为了让更多人下载恶意软件并访问设备，黑客以假广告中以较低的价格(7500欧元)将宝马卖给了这位外交官。

这个攻击软件主要是伪装成一个旧宝马的相册。用户打开照片时会被入侵。大使馆中的约有21名外交官收到威胁，具体的名单还有待核实。

2021年，美国和英国情报机构将APT29与俄罗斯对外情报局联系起来。Unit
42的研究人员将假汽车广告活动追溯到SVR，以此判定；威胁参与者使用了以前与间谍机构相关的特定工具和技术。

## 一场新的攻击活动

2023年5月，Lab52的研究人员发表了他们对未知威胁行为者使用与APT29类似技术的新活动的发现，使他们相信新的活动来自APT29。他们将此次活动命名为“Information”，并表示有一个类似于
QUARTERRIG 的新样本，该恶意软件之前由 CERT.PL 分析并连接到 APT29，现已上传到 VirusTotal。QUARTERRIG
活动的分析将其称为“Note”。 然而，Lab52 已将该活动命名为“Information”，以便他们可以展示该活动的新功能。

VirusTotal上公开的样本哈希值为422ba73f389ae5ef9411cf4484c840c7c82f2731c6324db0b24b6f87ce8477d，在Lab52发现该样本时，只有3个反病毒引擎将该样本识别为恶意样本。Lab52报告上指出，新活动的结构与我们之前提到的
CERT.PL 报告中概述的“Note”活动高度相似，而CERT.PL报告中研究的样本可以追溯到2023年3月。Lab52还观察到自 2023 年 4
月以来恶意软件的操作发生了变化，主要体现在最新的分析样本中注入方法发生的变化。

此次可以在名为“dbg.info”的文件中找到shellcode，这与以前的活动中观察到的情况不同。“Information.iso”包括以下部分:

  * AppvlsSubsystems64.dll——一个用于加载正版系统DLL并将shellcode注入其中的DLL。
  * dbg.info -包含shellcode。
  * info .exe -一个由微软签名的合法二进制文件，旨在通过DLL Side-Load加载AppvlsSubsystems64.dll。

Lab52还表示：在这个新活动中，AppvIsvSubsystems64.dll的编译日期相较于之前已经做了更新，这表明其可能已经对样本进行了修改。该公司还表示，与以往的活动相比，最显著的变化是注入技术。

目标保持不变 **:使用可执行文件(Information.exe)执行两个dll。第一个DLL
AppvlsvSubsystems64.dll将在进程执行期间加载，第二个DLL将由AppvlsvSubsystem64.dll加载，但在本例中，它将使用不同的技术进行修改，以尽量减少检测方法。**

因此，合法的二进制文件Information.exe将作为恶意软件执行的容器。要实现这一点，它将加载AppvIsvSubsystems64.dll，并需要在加载到Information.exe之前识别要用shellcode修改的合适的系统DLL，其主要的变化在
AppvIsvSubsystems64.dll 中。此外，命令和控制 (C2) 也有所不同。与 QUARTERRIG 从 HALFRIG
的演变过程类似，AAPT29在这次新的攻击中增强了其dll加载程序“Applvsubsystem64.dll”的复杂性。

![](https://images.seebug.org/content/images/2023/08/ff6f611a-7076-4839-8dd2-a9712ce14f69.jpg-w331s)

图2:当前“Information”运动的感染链(图片来源：Lab52)

### CCleaner

截至2023年7月，Lab52报告发现了APT29使用的更高级策略，其中包括使用SVG Dropper,
DLL进行感染和C2行为。被观察到的活动的主要植入方式是通过发送一条发件人为挪威大使馆的主题为“邀请-圣卢西亚庆祝活动”的网络钓鱼电子邮件。

![](https://images.seebug.org/content/images/2023/08/cb8b8b5e-a161-454a-bc1e-9ba09da009ec.jpg-w331s)
图3:网络钓鱼邮件(图片来源：Lab52)

打开该文件后，执行的脚本将启动安装和下载扩展名为 .iso
的文件的过程，该文件还保存了下一阶段的感染。此过程中，会将.svg文件转换为HTML走私技术，有效地感染受害者。接下来将下载一个名为“invitation.is”的ISO文件。文件包含的内容与Lab52之前在其他APT29活动中观察到的内容相似。

`%windir%/system32/cmd.exe /q /c "robocopy . C:\Windows\Tasks /NODCOPY /NFL
/NDL /NJH /NJS /NC /NS /NP > nul & start
C:\Windows\Tasks\CCleanerReactivator.exe > nul"`

使用Robocopy，在执行CCleanerReactivator.exe之前，所有文件都将复制到`C:\Windows\Tasks`文件夹中。CCleanerReactivator.exe是一个数字签名的二进制文件，但在VirusTotal中仍未检测到。此软件为释放计算机空间的合法目的服务，可以合法下载。

关于C2通信，Lab52报告称与之前活动相比已经发生了重大变化。过去C2的注册主要包含UserName和ComputerName的加密JSON的POST请求，但是最新的版本中，C2的受害者id已被简化为只有4位数字，此外，下一个阶段的(shellcode)也是直接从C2下载，而不是在本地加载。

对于网络安全专业人员来说，密切关注已建立的APT和新出现的APT一样重要。 2023 年 4 月 APT29
针对北约和欧盟成员国外交和外交部的间谍活动的例子表明，即使是成熟的威胁行为者也可以改进其策略并开发以前未记录的恶意软件有效负载。

通过密切监视和分析已知 APT 组织的活动，安全专业人员可以深入了解其方法，从而针对未来的攻击做好更好的准备并采取主动防御措施。忽视或低估已建立的 APT
可能会使组织容易受到高度复杂和不断变化的威胁的影响，从而可能导致重大数据泄露，并危及国家安全或敏感信息。全面的网络安全方法应包括对知名和新兴威胁行为者进行警惕监控，以防范不断演变的网络威胁。

## MITRE MAP

首次访问 | 执行 | 防御 | 发现  
---|---|---|---  
T1566: Phishing | T1102: Web Service | T1070: Indicator Removal of Host |
T1057: Process Discovery  
| T1055: Process Injection | T1176: Browser Extensions |  
|  |  | T1574: Hijack Execution Flow  
|  |  | T1134: Access Token Manipulation  
  
## AVERTIUM 建议

  * 员工培训和意识:定期为员工举办网络安全培训课程，教育他们了解网络钓鱼活动的危险。教他们如何识别可疑的电子邮件、链接和附件，鼓励向IT或安全团队报告潜在的网络钓鱼威胁行为；
  * 电子邮件过滤:实现更高级的电子邮件过滤解决方案，对发送至员工邮箱的钓鱼钓鱼邮件进行检测。通过这些过滤器分析电子邮件内容、附件和发件人等级、以识别和隔离潜在的恶意邮件。
  * 多因素身份验证(MFA):在访问敏感帐户和系统时强制使用多因素身份验证。MFA通过要求用户提供第二种形式的验证(如：发送验证码至移动端）来提高额外的安全可能。
  * 定期的安全补丁和更新:确保所有软件、操作系统和安全应用程序都是最新的补丁和更新。网络罪犯经常利用过时软件的已知漏洞发动网络钓鱼攻击。定期更新有助于降低这些风险，增强整体网络安全态势。

## IoCs

  * 波兰政府发布了多份与 SnowyAmber 相关的间谍活动的 IoC。这些 IoC 可以帮助构建对已知恶意软件样本的检测。 I
  * **“Information”** 哈希文件数据
  * Information[.]iso
    * B422BA73F389AE5EF9411CF4484C840C7C82F2731C6324DB0B24B6F87CE8477D
  * Information[.]exe
    * 6C55195F025FB895F9D0EC3EDBF58BC0AA46C43EEB246CFB88EEF1AE051171B3
  * AppvIsvSubsystems64[.]dll
    * E7C49758BAE63C83D251CACBFADA7C09AF0C3038E8FF755C4C04F916385805D8
  * Dbg[.]info

    * 5F6219ADE8E0577545B9F13AFD28F6D6E991326F3C427D671D1C1765164B0D57
  * CCleaner

  * MD5 File Hash 
    * f29083f25d876bbc245a1f977169f8c2
  * SHA 1 File Hash 
    * a61b35a9a9650396223bb82aad02c0ec1f1bb44b
  * SHA26 File Hash 
    * 4875a9c4af3044db281c5dc02e5386c77f331e3b92e5ae79ff9961d8cd1f7c4f
    * 59e5b2a7a3903e4fb9a23174b655adb75eb490625ddb126ef29446e47de4099f
    * 7fc9e830756e23aa4b050f4ceaeb2a83cd71cfc0145392a0bc03037af373066b
    * 966e070a52de1c51976f6ea1fc48ec77f6b89f4bf5e5007650755e9cd0d73281
    * a8ae10b43cbf4e3344e0184b33a699b19a29866bc1e41201ace1a995e8ca3149
    * af1922c665e9be6b29a5e3d0d3ac5916ae1fc74ac2fe9931e5273f3c4043f395
    * d7bda5e39327fe12b0c1f42c8e27787f177a352f8eebafbe35d3e790724eceff
  * URL
    * hxxps://kefas[.]id/search/s[.]php
  * Domain
    * Kefas[.]id

## 参考文献

  1. [Russian cyberspies hit NATO and EU organizations with new malware toolset | CSO Online](https://www.csoonline.com/article/575023/russian-cyberspies-hit-nato-and-eu-organizations-with-new-malware-toolset.html "Russian cyberspies hit NATO and EU organizations with new malware toolset | CSO Online")
  2. [The Resurgence of Russian Threat Actor, NOBELIUM (avertium.com)](https://explore.avertium.com/resource/resurgence-of-nobelium "The Resurgence of Russian Threat Actor, NOBELIUM \(avertium.com\)")
  3. [New tricks of APT29 – update on the CERT.PL report (lab52.io)](https://lab52.io/blog/2162-2/ "New tricks of APT29 – update on the CERT.PL report \(lab52.io\)")
  4. [New invitation from APT29 to use CCleaner - AlienVault - Open Threat Exchange](https://otx.alienvault.com/pulse/64b4e6cf804bf63108eb373b "New invitation from APT29 to use CCleaner - AlienVault - Open Threat Exchange")
  5. [MagicWeb: NOBELIUM’s post-compromise trick to authenticate as anyone | Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2022/08/24/magicweb-nobeliums-post-compromise-trick-to-authenticate-as-anyone/ "MagicWeb: NOBELIUM’s post-compromise trick to authenticate as anyone | Microsoft Security Blog")
  6. [Microsoft Uncovers New Post-Compromise Malware Used by Nobelium Hackers (thehackernews.com)](https://thehackernews.com/2022/08/microsoft-uncovers-new-post-compromise.html "Microsoft Uncovers New Post-Compromise Malware Used by Nobelium Hackers \(thehackernews.com\)")
  7. [APT29 Exploited a Windows Feature to Compromise European Diplomatic Entity Network (thehackernews.com)](https://thehackernews.com/2022/11/apt29-exploited-windows-feature-to.html "APT29 Exploited a Windows Feature to Compromise European Diplomatic Entity Network \(thehackernews.com\)")
  8. [New invitation from APT29 to use CCleaner (lab52.io)](https://lab52.io/blog/2344-2/ "New invitation from APT29 to use CCleaner \(lab52.io\)")
  9. [Russian hackers lured diplomats in Ukraine with cheap BMW ad | Reuters](https://www.reuters.com/world/europe/russian-hackers-lured-embassy-workers-ukraine-with-an-ad-cheap-bmw-2023-07-12/ "Russian hackers lured diplomats in Ukraine with cheap BMW ad | Reuters")
  10. [They See Me Roaming: Following APT29 by Taking a Deeper Look at Windows Credential Roaming | Mandiant](https://www.mandiant.com/resources/blog/apt29-windows-credential-roaming "They See Me Roaming: Following APT29 by Taking a Deeper Look at Windows Credential Roaming | Mandiant")
  11. [BlueBravo Uses Ambassador Lure to Deploy GraphicalNeutrino Malware (recordedfuture.com)](https://go.recordedfuture.com/hubfs/reports/cta-2023-0127.pdf "BlueBravo Uses Ambassador Lure to Deploy GraphicalNeutrino Malware \(recordedfuture.com\)")
  12. [Espionage campaign linked to Russian intelligence services - Baza wiedzy - Portal Gov.pl ](https://www.gov.pl/web/baza-wiedzy/espionage-campaign-linked-to-russian-intelligence-services "Espionage campaign linked to Russian intelligence services - Baza wiedzy - Portal Gov.pl \(www.gov.pl\)")
  13. [Russia-Linked APT29 Uses New Malware in Embassy Attacks - SecurityWeek](https://www.securityweek.com/russia-linked-apt29-uses-new-malware-in-embassy-attacks/ "Russia-Linked APT29 Uses New Malware in Embassy Attacks - SecurityWeek")
  14. [APT29 intensifies credential-stealing attacks | SC Media](https://www.scmagazine.com/brief/apt29-intensifies-credential-stealing-attacks "APT29 intensifies credential-stealing attacks | SC Media")
  15. [Diplomats Beware: Cloaked Ursa Phishing With a Twist (paloaltonetworks.com)](https://unit42.paloaltonetworks.com/cloaked-ursa-phishing/ "Diplomats Beware: Cloaked Ursa Phishing With a Twist \(paloaltonetworks.com\)")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2097/>

