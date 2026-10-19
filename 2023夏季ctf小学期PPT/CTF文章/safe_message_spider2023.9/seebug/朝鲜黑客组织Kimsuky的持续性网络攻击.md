**作者：知道创宇404实验室翻译组**  
**原文链接：<https://us-cert.cisa.gov/ncas/alerts/aa20-301a>**

## 一、摘要

网络安全报告书由网络安全基础设施安全局（CISA）、联邦调查局（FBI）和美国网络司令部国家宣教部队（CNMF）联合撰写，主要描述了针对朝鲜高级黑客组织[Kimsuky](https://attack.mitre.org/groups/G0094/)网络攻击所使用的战术、技术和程序（TTP）。美国政府将该网络攻击称为HIDDEN
COBRA，有关HIDDEN COBRA的更多信息，请访问[https://www.us-cert.cisa.gov/northkorea](https://us-cert.cisa.gov/northkorea)。  
本文描述了截止2020年7月已知的Kimsuky黑客网络攻击事件，旨在保护相关组织免受该黑客影响。 [单击此处](https://us-cert.cisa.gov/sites/default/files/publications/TLP-WHITE_AA20-301A_North_Korean_APT_Focus_Kimsuky.pdf)以获取PDF版本。

## 二、主要发现

  * Kimsuky黑客组织可能自2012年开始运营。
  * Kimsuky很可能是朝鲜政府支持的全球情报搜集任务。
  * Kimsuky运用常见的策略窃取数据。[ [1](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia)]，[ [2](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829) ]
  * Kimsuky最可能使用网络钓鱼获取初始访问权限。[ [3](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829) ]
  * Kimsuky的情报收集针对韩国、日本和美国。
  * Kimsuky重点关注朝鲜半岛、核政策、外交政策及国家安全问题的相关信息。
  * Kimsuky特别关注对象： 各领域专家、智囊团、韩国政府机关；[[4](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia) ]，[ [5](https://attack.mitre.org/groups/G0094/) ]，[[6](https://www.securityweek.com/north-korea-suspected-cyber-espionage-attacks-against-south-korean-entities) ]，[[7](https://attack.mitre.org/groups/G0094/) ]，[ [8](https://go.crowdstrike.com/rs/281-OBQ-266/images/Report2020CrowdStrikeGlobalThreatReport.pdf) ]
  * CISA、FBI和CNMF建议目标群体应加强防御意识。

## 三、相关技术

#### 1、初始访问

Kimsuky通过网络钓鱼获取 _初始访问_ [ [TA0001](https://attack.mitre.org/tactics/TA0001/)
]权限。[[9](https://blog.malwarebytes.com/threat-analysis/2020/04/apts-and-covid-19-how-advanced-persistent-threats-use-the-coronavirus-as-a-lure/)],[[10](https://www.pwc.co.uk/issues/cyber-security-services/research/tracking-kimsuky-north-korea-based-cyber-espionage-group-part-2.html)],[[11](https://go.crowdstrike.com/rs/281-OBQ-266/images/Report2020CrowdStrikeGlobalThreatReport.pdf)]
网络钓鱼（电子邮件被嵌入恶意附件）方法是Kimsuky最常用的策略（网络钓鱼附件[
[T1566.001](https://attack.mitre.org/versions/v7/techniques/T1566/001/)
]）[[12](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia) ]、[ [13](https://attack.mitre.org/groups/G0094/) ]。

  * 该黑客组织已使用从目标群体之外的受害者网络窃取的托管凭据托管恶意脚本。在受害域上创建子域来冒充像Google、Yahoo的合法站点。[14]
  * Kimsuky还向受害者发送了旨在建立事后信任的良性电子邮件。
  * 冒充韩国记者，发送了几封面试主题的电子邮件。电子邮件主题为“首尔[Rededed TV Show]的Skype采访请求”，邀请收件人上节目充当嘉宾。黑客组织实际上是在邀请受害者接受有关朝鲜半岛和无核化问题的采访。
  * 收件人同意接受采访后，Kimsuky随后发送带有BabyShark（有关BabyShark的信息，请参见“执行”部分）恶意文档的电子邮件。面试日期临近时，发送了临时取消面试的电子邮件。
  * Kimsuky善于利用例如COVID-19、朝鲜核计划或媒体采访的时事。[[15](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829) ]，[[16](https://blog.malwarebytes.com/threat-analysis/2020/04/apts-and-covid-19-how-advanced-persistent-threats-use-the-coronavirus-as-a-lure/) ]，[[17](https://www.cyberscoop.com/north-korea-accelerate-commercial-espionage-meet-kims-economic-deadline/) ]

Kimsukyh还通过发送以安全警报为主题的网络钓鱼电子邮件获得初始访问权限，利用torrent共享站点分发恶意软件，并指示受害者安装恶意浏览器扩展程序（
_网络钓鱼链接
[[T1566.002](https://attack.mitre.org/versions/v7/techniques/T1566/002/)
]，_Drive-by Compromise
[[T1189](https://attack.mitre.org/versions/v7/techniques/T1189/)], _Man-in-the-Browser_
[[T1185](https://attack.mitre.org/versions/v7/techniques/T1185/)]).[
[18](https://attack.mitre.org/groups/G0094/) ]

#### 2、执行

获得初始访问权限后，Kimsuky使用[BabyShark](https://attack.mitre.org/software/S0414/)恶意软件和PowerShell或Windows
Command Shell _执行_ 指令[
[TA0002](https://attack.mitre.org/versions/v7/tactics/TA0002/) ]。

  * BabyShark是基于Visual Basic脚本（VBS）的恶意软件。
  * 受感染主机系统使用本机Microsoft Windows实用程序`mshta.exe`从远程系统下载并执行HTML应用程序（HTA）文件（ _签名的二进制代理执行：Mshta_ [ [T1218.005](https://attack.mitre.org/versions/v7/techniques/T1218/005/) ]）。
  * HTA文件成功下载后，解码并执行BabyShark VBS文件。
  * 该脚本通过创建在启动时运行的注册表项（ _引导或登录自动启动执行：注册表运行键/启动文件夹_ [ [T1547.001](https://attack.mitre.org/versions/v7/techniques/T1547/001/) ]）维护其 _持久性_ [ [TA0003](https://attack.mitre.org/versions/v7/tactics/TA0003/) ] 。
  * 收集系统信息（ _系统信息_ [ [T1082](https://attack.mitre.org/versions/v7/techniques/T1082) ]），将其发送到操作员的命令控制（C2）服务器，等待其他命令。[ [19](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829) ]，[ [20](https://attack.mitre.org/groups/G0094/) ]，[ [21](https://unit42.paloaltonetworks.com/new-babyshark-malware-targets-u-s-national-security-think-tanks/) ]，[ [22](https://unit42.paloaltonetworks.com/babyshark-malware-part-two-attacks-continue-using-kimjongrat-and-pcrat/) ]
  * 报告显示BabyShark是通过包含链接或附件的电子邮件传递的（更多信息请参见“初始访问”部分）（ _网络钓鱼链接_ [ [T1566.002](https://attack.mitre.org/versions/v7/techniques/T1566/002/) ]， _网络钓鱼附件_ [ [T1566.001](https://attack.mitre.org/versions/v7/techniques/T1566/001) ]）。黑客主要针对美国智囊团和全球加密货币行业。[ [23](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829) ]
  * Kimsuky黑客使用PowerShell运行网络上的可执行文件，而无需通过使用目标内存来接触计算机物理硬盘（ _命令和脚本解释器：PowerShell_ [ [T1059.001](https://attack.mitre.org/versions/v7/techniques/T1059/001/) ]）。无需调用`powershell.exe`HTA文件或`mshta.exe`[ [24](https://attack.mitre.org/groups/G0094/) ]，[ [25](https://unit42.paloaltonetworks.com/babyshark-malware-part-two-attacks-continue-using-kimjongrat-and-pcrat/) ]，[ [26](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/what-is-mshta-how-can-it-be-used-and-how-to-protect-against-it/) ]，[ [27](https://unit42.paloaltonetworks.com/new-babyshark-malware-targets-u-s-national-security-think-tanks/) ]即可执行PowerShell命令/脚本。

#### 3、持续性攻击

Kimsuky黑客通过使用恶意浏览器扩展、修改进程、操纵执行；使用远程桌面协议（RDP）以及更改应用程序的默认文件关联以建立 _Persistence_ [
[TA0003](https://attack.mitre.org/versions/v7/tactics/TA0003/)
]`autostart`，进而获取登录名和密码。

  * 2018年，Kimsuky黑客使用了扩展程序以窃取受害者浏览器中的密码和cookie（ _Man-in-the-Browser_ [ [T1185](https://attack.mitre.org/versions/v7/techniques/T1185/) ]）。[ [28](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia) ]
  * Kimsuky黑客可能会安装使用实用程序与服务交互或直接修改注册表项（ _启动或登录自动启动执行_ [ [T1547](https://attack.mitre.org/versions/v7/techniques/T1547) ]）来在 _启动时执行_ 的新的服务。服务器名称可以通过相关操作系统功能的名称来伪装，也可以伪装成良性软件，还可以利用管理员特权创建并执行，因此黑客可以使用特权升级至系统，通过服务执行直接启动服务。[ [29](https://attack.mitre.org/groups/G0094/) ]，[ [30](https://unit42.paloaltonetworks.com/new-babyshark-malware-targets-u-s-national-security-think-tanks/) ]
  * 2018年5月STOLEN PENCIL操作期间，Kimsuky黑客使用了GREASE恶意软件。GREASE是可以添加Windows管理员帐户并启用RDP，同时避免使用防火墙规则（ _远程服务：远程桌面协议_ [ [T1021.001](https://attack.mitre.org/versions/v7/techniques/T1021/001) ]）的工具。[ [31](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia) ]
  * Kimsuky黑客使用文档窃取程序模块，更改与`.hwp`注册表中的文字处理器（HWP）文档（文件）相关联的默认程序（ _事件触发执行：更改默认文件关联_ [ [T1546.001](https://attack.mitre.org/versions/v7/techniques/T1546/001) ]）。操纵默认注册表设置来打开恶意程序，而非合法的HWP程序（HWP是朝鲜语文字处理器）。在合法的HWP程序最终打开文档之前，该恶意软件将读取并通过电子邮件发送HWP文档中的内容。[ [32](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/) ] Kimsuky还通过将文件格式设置为`.docx`文件，`.hwp`会相应地调整其宏。[33]
  * Kimsuky黑客通过上传基于actor的版本和超文本处理器（PHP）的Web Shell来维护对受侵害域的访问；APT黑客可以在Web Shell上上载、下载和删除受感染域上的文件和目录（ _服务器软件组件：Web Shell_ [ [T1505.003](https://attack.mitre.org/versions/v7/techniques/T505/003) ]）。

#### 4、权限升级

Kimsuky黑客使用的权限升级方法[
[TA0004](https://attack.mitre.org/versions/v7/tactics/TA0004/)
]众所周知。这些方法包括：将脚本放入Startup文件夹、创建和运行新服务、更改默认文件关联以及注入恶意代码`explorer.exe`。

  * Kimsuky黑客使用Win7Elevate（来自Metasploit框架的漏洞）避免用户帐户控制，注入恶意代码explorer.exe`（*Process Injection* [ [T1055](https://attack.mitre.org/versions/v7/techniques/T1055/) ]）。这种恶意代码会从资源中解密数据库（包括击键记录和远程控制访问工具以及远程控制下载和执行工具的集合），无关受害者的操作系统。将解密文件保存到`临时文件夹中的编码名称（例如dfe8b437dd7c417a6d.tmp`）的磁盘上，并将该文件作为库加载，以确保重启后工具的再次使用。[ [35](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/) ]
  * 在注入恶意代码前，恶意软件会设置必要权限（请参见图1），将路径写入其恶意动态链接库中（DLL），并通过创建远程线程`explorer.exe`（ _Process Injection_ [ [T1055](https://attack.mitre.org/versions/v7/techniques/T1055/) ]）确保远程进程的加载。[ [36](https://yoroi.company/research/the-north-korean-kimsuky-apt-keeps-threatening-south-korea-evolving-its-ttps/) ]

![](https://images.seebug.org/content/images/2020/10/87bbafad-b2d5-447e-8d29-f3d88e9acfd9.png-w331s)

_图1：注入恶意代码前设置的权限_ [[37](https://yoroi.company/research/the-north-korean-kimsuky-apt-keeps-threatening-south-korea-evolving-its-ttps/)]

#### 5、防御手段

Kimsuky黑客使用禁用安全工具、删除文件和Metasploit.[[38](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)],[[39](https://attack.mitre.org/groups/G0094/)]在内的防御逃避手段[TA0005](https://attack.mitre.org/versions/v7/tactics/TA0005/)
。

  * Kimsuky黑客的恶意DLL在启动时运行至Windows防火墙注册表项为关闭状态（见图2），即禁用Windows系统防火墙并关闭其安全服务，从而阻止该服务器向用户发出有关禁用防火墙的警报（见图2）（ _Impair防御：禁用或修改系统防火墙_ [ [T1562.004](https://attack.mitre.org/versions/v7/techniques/T1562/004/) ]).[ [40](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/) ].

![](https://images.seebug.org/content/images/2020/10/792686fd-0727-452f-8747-9d068ed37abd.png-w331s)

_图2：注册表中禁用的防火墙值_ [[41](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)]

  * Kimsuky黑客使用了键盘记录程序，将磁盘上已泄漏的数据传输到其C2服务器，随后将其 _删除（主机指示：文件删除_ [ [T1070.004](https://attack.mitre.org/versions/v7/techniques/T1070/004/) ]）。[ [42](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/) ]
  * Kimsuky黑客已使用执行Microsoft HTA的实用程序：`mshta.exe`。`.hta`通过受信任的Windows实用程序（ _二进制代理执行：Mshta_ [ [T1218.005](https://attack.mitre.org/versions/v7/techniques/T1218/005) ]）用于恶意文件和JavaScript或VBS的 _代理执行_ 。它也可以用来绕过应用程序的准许。（ _滥用控制机制：绕过用户访问控制_ [ [T1548.002](https://attack.mitre.org/versions/v7/techniques/T1548/002) ]），[ [43](https://attack.mitre.org/groups/G0094/) ]，[ [44](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/what-is-mshta-how-can-it-be-used-and-how-to-protect-against-it/) ]
  * 上面已指出，Win7Elevate也用于规避传统措施。Win7Elevatve是Metasploit框架开源代码的一部分，用于将恶意代码注入explorer.exe（ _进程注入_ [ [T1055](https://attack.mitre.org/versions/v7/techniques/T1055) ]）。恶意代码从解密程序库，将解密后的文件以随机名称保存在磁盘上受害者的临时文件夹中，并将该文件作为库加载。[ [45](https://www.securityweek.com/north-korea-suspected-cyber-espionage-attacks-against-south-korean-entities) ]，[ [46](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/) ]，[ [47](https://attack.mitre.org/groups/G0094/) ]

#### 6、访问凭证

Kimsuky黑客使用合法工具和网络探测器从Web浏览器、文件和键盘记录器（[
[TA0006](https://attack.mitre.org/versions/v7/tactics/TA0006/) ]）中收集凭证。

  * Kimsuky黑客使用内存转储程序而非知名恶意软件，使用Windows命令行管理工具：`ProcDump`，允许用户根据某些标准（例如，中央处理器（CPU）的利用率高（ _OS凭据转储_ [ [T1003](https://attack.mitre.org/versions/v7/techniques/T1003/) ] ）创建进程的崩溃/核心转储）。`ProcDump`监视CPU峰值并在达到某个值时生成故障转储，将信息传递到保存在计算机上的Word文档中。它可以用作一般流程转储实用程序，黑客可以将其嵌入其他脚本中，如Kimsuky将其包含`ProcDump`在BabyShark恶意软件中。[ [48](https://www.microsoft.com/security/blog/2019/05/09/detecting-credential-theft-through-memory-access-modelling-with-microsoft-defender-atp/) ]
  * 根据安全研究人员的说法，Kimsuky滥用Chrome扩展程序，从浏览器中窃取密码和cookie（ _Man-in-the-Browser_ [ [T1185](https://attack.mitre.org/versions/v7/techniques/T1185/) ].)[ [49](https://attack.mitre.org/groups/G0094/) ]，[ [50](https://www.zdnet.com/article/cyber-espionage-group-uses-chrome-extension-to-infect-victims/) ]。使用冒名电子邮件将受害者引导到钓鱼网站，并向受害者显示良性PDF文档，但无法查看它。然后将受害者定向到正式的Chrome Web Store页面以安装Chrome扩展程序，该扩展程序窃取cookie和站点密码，并通过`jQuery.js`从单独站点加载名为JavaScript的文件（见图3）。[ [51](https://www.zdnet.com/article/cyber-espionage-group-uses-chrome-extension-to-infect-victims/) ]

![](https://images.seebug.org/content/images/2020/10/9cfb06e0-5473-437a-8a28-6d00220bebfa.png-w331s)

_图3：名为`jQuery.js`_[ [52](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia) ]的 _JavaScript文件_

  * Kimsuky黑客还使用名为PowerShell的基于PowerShell的键盘记录程序和名为Nirsoft SniffPass的网络探测工具（ _输入捕获：键盘记录_ [ [T1056.001](https://attack.mitre.org/versions/v7/techniques/T1056/001/) ]，*网络探测[ [T1040](https://attack.mitre.org/versions/v7/techniques/T1040/) ]）。通过挖掘加密货币的工具“ cryptojacker”将其记录到`%userprofile%\appdata\roaming\apach.{txt,log}`。因此Nirsoft SniffPass能获取通过非安全协议发送的密码。[ [53](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia) ]
  * Kimsuky黑客使用修改过的PHProxy（一种用PHP编写的开源Web代理）版本来检查受害者访问的网站之间的流量，并收集其输入的个人信息。[54]

#### 7、其他发现

Kimsuky黑客似乎依赖于使用受害者的操作系统命令提示符来枚举文件结构和系统信息（ _文件和目录_ [
[T1083](https://attack.mitre.org/versions/v7/techniques/T1083/)
]）。该信息被定向到`C:\WINDOWS\msdatl3.inc`恶意软件，并可能通过电子邮件发送到恶意软件的命令服务器。[
[55](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/) ]

#### 8、收集

Kimsuky黑客通过其HWP文档恶意软件和其键盘记录程序（ _集合_ [
[TA0009](https://attack.mitre.org/versions/v7/tactics/TA0009/)
]）从受害系统中收集数据。HWP文档恶意软件将更改 注册表中的默认程序关联以打开HWP文档（ _事件触发执行：更改默认文件关联_ [
[T1546.001](https://attack.mitre.org/versions/v7/techniques/T1546/001/)
]）。当用户打开HWP文件时，注册表项更改会触发恶意软件的执行，该恶意软件会打开HWP文档，将HWP文档的副本发送到对手控制下的帐户。允许用户正常打开文件，而无需任何提示用户发生任何事情。击键记录器拦截击键并将其写入`C:\Program
Files\Common Files\System\Ole DB\msolui80.inc`并记录用户按下键的活动窗口名称（ _输入捕获：键盘记录_ [
[T1056.001](https://attack.mitre.org/versions/v7/techniques/T1056/001/)
]）。还有另一个击键记录程序变体，可将记录储存到`C:\WINDOWS\setup.log`。[
[56](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)
]中。

Kimsuky黑客还使用了Mac OS Python植入程序，该程序从Mac OS系统收集数据并将其发送到C2服务器（ _命令和脚本解释器：Python_
[
[T1059.006]](https://attack.mitre.org/versions/v7/techniques/T1059/006/)）。Python程序根据后面指定的C2选项下载各种植入物`filedown.php`（请参见图4）。

![](https://images.seebug.org/content/images/2020/10/42a30781-f5c4-4e7f-be1d-562d912d3d72.png-w331s)
![](https://images.seebug.org/content/images/2020/10/8cfb5e70-94cf-4fd9-adfa-b7d5cb7b5c83.png-w331s)

_图4：针对MacOS的Python脚本_ [57]

#### 9、命令与控制

Kimsuky黑客使用修改后的TeamViewer客户端5.0.9104版进行 _命令和控制_ [
[TA0011](https://attack.mitre.org/versions/v7/tactics/TA0011/) ]（ _远程访问软件_ [
[T1219](https://attack.mitre.org/versions/v7/techniques/T1219/)
]）。在初始感染期间，将创建服务“远程访问服务”并将其调整为`C:\Windows\System32\vcmon.exe`在系统启动时执行（
_引导或登录自动启动执行：注册表运行键/启动文件夹_ [
[T1547.001](https://attack.mitre.org/versions/v7/techniques/T1547/001/)
]）。`vcmon.exe`执行时，它都会通过将注册表值清零来禁用防火墙（ _Impair Defenses：禁用或修改系统防火墙_ [
[T1562.004](https://attack.mitre.org/versions/v7/techniques/T1562/004/)
]）。通过更改以下内容来修改TeamViewer注册表设置：`TeamViewer`TeamViewer组件中的字符串；启动程序配置包括`SecurityPasswordAES`的注册表值，控制远程访问工具的工作方式。SecurityPasswordAES`注册表值表示由远程用户使用的密码的散列来连接的TeamViewer客户端（使用备用认证资料：通过hash[
[T1550.002](https://attack.mitre.org/techniques/T1550/002/)
]）。这样，攻击者可以设置预共享的身份验证值以访问TeamViewer Client。黑客将执行TeamViewer客户端`netsvcs.exe`。[
[58](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/) ]

Kimsuky黑客使用统一格式。在最近使用的网址中，“ `express[.]php?op=1`—”似乎是从1到3的选项范围。[59]

#### 10、渗出

网络安全公司报告中描述了两种已知的Kimsuky黑客用于exfiltrate窃取数据的方法：通过电子邮件或随机生成的117字节（如MD5
hash生成的RC4密钥 _渗出_ [
[TA0010](https://attack.mitre.org/versions/v7/tactics/TA0010/) ]）。

暂无迹象表明该黑客在渗出过程中破坏了计算机，这表明Kimsuky黑客的意图是窃取信息，而非破坏计算机网络。Kimsuky黑客首选的方法是通过电子邮件发送或接收被泄露的信息，恶意软件会在将数据发送到C2服务器之前对其进行加密（
_存档收集的数据_ [ [T1560](https://attack.mitre.org/versions/v7/techniques/T1560)
]）。Kimsuky黑客还在受害者的电子邮件帐户中设置了自动转发功能（ _电子邮件转发规则_ [
[T1114.003](https://attack.mitre.org/versions/v7/techniques/T1114/003/) ]）。

Kimsuky黑客使用MD5 hash生成的RC4密钥或随机生成的117字节窃取数据，并以RSA加密方式发送（加密
_通道[T1573.001](https://attack.mitre.org/versions/v7/techniques/T1573/001)
]）。Kimsuky黑客的恶意软件构造了一个1120位的公共密钥。最终的数据文件保存在`C:\Program Files\Common
Files\System\Ole DB\`（_数据分段：本地数据分段*[
[T1074.001](https://attack.mitre.org/versions/v7/techniques/T1074/001) ]）中。[
[60](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/) ]

## 四、Indicators of Compromise

有关IOC的可下载副本，请参阅[AA20-301A.stix](https://us-cert.cisa.gov/sites/default/files/publications/AA20-301A.stix.xml)。

_表1：Kimsuky黑客使用的域_

`login.bignaver[.]com` | `nytimes.onekma[.]com` | `webuserinfo[.]com`  
---|---|---  
`member.navier.pe[.]hu` | `nid.naver.onektx[.]com` | `pro-navor[.]com`  
`cloudnaver[.]com` | `read.tongilmoney[.]com` | `naver[.]pw`  
`resetprofile[.]com` | `nid.naver.unicrefia[.]com` | `daurn[.]org`  
`servicenidnaver[.]com` | `mail.unifsc[[.]com` | `naver.com[.]de`  
`account.daurn.pe[.]hu` | `member.daum.unikortv[.]com` | `ns.onekorea[.]me`  
`login.daum.unikortv[.]com` | `securetymail[.]com` | `riaver[.]site`  
`account.daum.unikortv[.]com` | `help-navers[.]com` | `mailsnaver[.]com`  
`daum.unikortv[.]com` | `beyondparallel.sslport[.]work` | `cloudmail[.]cloud`  
`member.daum.uniex[.]kr` | `comment.poulsen[.]work` | `helpnaver[.]com`  
`jonga[.]ml` | `impression.poulsen[.]work` | `view-naver[.]com`  
`myaccounts.gmail.kr-infos[.]com` | `statement.poulsen[.]work` | `view-hanmail[.]net`  
`naver.hol[.]es` | `demand.poulsen[.]work` | `login.daum.net-accounts[.]info`  
`dept-dr.lab.hol[.]es` | `sankei.sslport[.]work` | `read-hanmail[.]net`  
`Daurn.pe[.]hu` | `sts.desk-top[.]work` | `net.tm[.]ro`  
`Bigfile.pe[.]hu` | `hogy.desk-top[.]work` | `daum.net[.]pl`  
`Cdaum.pe[.]hu` | `kooo[.]gq` | `usernaver[.]com`  
`eastsea.or[.]kr` | `tiosuaking[.]com` | `naver.com[.]ec`  
`myaccount.nkaac[.]net` | `help.unikoreas[.]kr` | `naver.com[.]mx`  
`naver.koreagov[.]com` | `resultview[.]com` | `naver.com[.]se`  
`naver.onegov[.]com` | `account.daum.unikftc[.]kr` | `naver.com[.]cm`  
`member-authorize[.]com` | `ww-naver[.]com` | `nid.naver.com[.]se`  
`naver.unibok[.]kr` | `vilene.desk-top[.]work` | `csnaver[.]com`  
`nid.naver.unibok[.]kr` | `amberalexander.ghtdev[.]com` | `nidnaver[.]email`  
`read-naver[.]com` | `nidnaver[.]net` | `cooper[.]center`  
`dubai-1[.]com` | `coinone.co[.]in` | `nidlogin.naver.corper[.]be`  
`amberalexander.ghtdev[.]com` | `naver.com[.]pl` | `nid.naver.corper[.]be`  
`gloole[.]net` | `naver[.]cx` | `naverdns[.]co`  
`smtper[.]org` | `smtper[.]cz` | `naver.co[.]in`  
`login.daum.kcrct[.]ml` | `myetherwallet.com[.]mx` | `downloadman06[.]com`  
`login.outlook.kcrct[.]ml` | `myetherwallet.co[.]in` | `loadmanager07[.]com`  
`top.naver.onekda[.]com` | `com-download[.]work` | `com-option[.]work`  
`com-sslnet[.]work` | `com-vps[.]work` | `com-ssl[.]work`  
`desk-top[.]work` | `intemet[.]work` | `jp-ssl[.]work`  
`org-vip[.]work` | `sslport[.]work` | `sslserver[.]work`  
`ssltop[.]work` | `taplist[.]work` | `vpstop[.]work`  
`webmain[.]work` | `preview.manage.org-view[.]work` | `intranet.ohchr.account-protect[.]work`  
  
_表2：Kimsuky黑客使用的域名_

`[REDACTED]/home/dwn[.]php?van=101` | `[REDACTED]/home/dwn[.]php?v%20an=101` |
`[REDACTED]/home/dwn[.]php?van=102`  
---|---|---  
`[REDACTED]/home/up[.]php?id=NQDPDE` |
`[REDACTED]/test/Update[.]php?wShell=201` | ``  
  
## 五、联系方式

举报相关网络犯罪活动，请通过以下网址与当地的联邦调查局办事处联系：[www.fbi.gov/contact-us/field](https://www.fbi.gov/contact-us/field-offices)，或致电联邦调查局的24/7网络观察（CyWatch）热线：（855）
292-3937，还可通过电子邮件发送至[CyWatch@fbi.gov](mailto:CyWatch@fbi.gov)。请提供有关事件的日期、时间、地点、类型、受影响的人数、设备类型、个人或组织的名称、联系方式。请求相关响应资源或技术支持，请通过[Central@cisa.dhs.gov](mailto:Central@cisa.dhs.gov)与CISA联系。

## 六、参考文献

[[1] Netscout: Stolen Pencil Campaign Targets Academia
](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia)

[[2] CYWARE Social: Babyshark malware continues to target nuclear and
cryptocurr…](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829)

[[3] CYWARE Social: Babyshark malware continues to target nuclear and
cryptocurr…](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829)

[[4] Netscout: Stolen Pencil Campaign Targets Academia
](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia)

[[5] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[6] Securityweek.com: North Korean Suspected Cyber-espionage Attacks Against
So…](https://www.securityweek.com/north-korea-suspected-cyber-espionage-attacks-against-south-korean-entities)

[[7] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[8] CrowdStrike: 2020 Global Threat
Report](https://go.crowdstrike.com/rs/281-OBQ-266/images/Report2020CrowdStrikeGlobalThreatReport.pdf)

[[9] Malwarebytes: APTs and COVID-19: How advanced persistent threats use the
co…](https://blog.malwarebytes.com/threat-analysis/2020/04/apts-and-covid-19-how-advanced-persistent-threats-use-the-coronavirus-as-a-lure/)

[[10] PwC: Tracking ‘Kimsuky’, the North Korea-based cyber espionage group:
Part…](https://www.pwc.co.uk/issues/cyber-security-services/research/tracking-kimsuky-north-korea-based-cyber-espionage-group-part-2.html)

[[11] CrowdStrike: 2020 Global Threat
Report](https://go.crowdstrike.com/rs/281-OBQ-266/images/Report2020CrowdStrikeGlobalThreatReport.pdf)

[[12] Netscout: Stolen Pencil Campaign Targets Academia
](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia)

[[13] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[14] Private Sector Partner

[[15] CYWARE Social: Babyshark malware continues to target nuclear and
cryptocur…](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829)

[[16] Malwarebytes: APTs and COVID-19: How advanced persistent threats use the
c…](https://blog.malwarebytes.com/threat-analysis/2020/04/apts-and-covid-19-how-advanced-persistent-threats-use-the-coronavirus-as-a-lure/)

[[17] cyberscoop: North Korea could accelerate commercial espionage to meet
Kim’…](https://www.cyberscoop.com/north-korea-accelerate-commercial-espionage-meet-kims-economic-deadline/)

[[18] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[19] CYWARE Social: Babyshark malware continues to target nuclear and
cryptocur…](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829)

[[20] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[21] Palo Alto Networks Unit 42: New BabyShark Malware Targets U.S. National
Se…](https://unit42.paloaltonetworks.com/new-babyshark-malware-targets-u-s-national-security-think-tanks/)

[[22] Palo Alto Networks Unit 42: New BabyShark Malware Targets U.S. National
Se…](https://unit42.paloaltonetworks.com/new-babyshark-malware-targets-u-s-national-security-think-tanks/)

[[23] CYWARE Social: Babyshark malware continues to target nuclear and
cryptocur…](https://cyware.com/news/babyshark-malware-continues-to-target-nuclear-and-cryptocurrency-industries-40e04829)

[[24] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[25] Palo Alto Networks Unit 42: BabyShark Malware Part Two – Attacks
Continue …](https://unit42.paloaltonetworks.com/babyshark-malware-part-two-attacks-continue-using-kimjongrat-and-pcrat/)

[[26] McAfee: What is mshta, how can it be used and how to protect against
it](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/what-is-mshta-how-can-it-be-used-and-how-to-protect-against-it/)

[[27] Palo Alto Networks Unit 42: New BabyShark Malware Targets U.S. National
Se…](https://unit42.paloaltonetworks.com/new-babyshark-malware-targets-u-s-national-security-think-tanks/)

[[28] Netscout: Stolen Pencil Campaign Targets
Academia](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia)

[[29] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[30] Palo Alto Networks Unit 42: New BabyShark Malware Targets U.S. National
Se…](https://unit42.paloaltonetworks.com/new-babyshark-malware-targets-u-s-national-security-think-tanks/)

[[31] Netscout: Stolen Pencil Campaign Targets Academia
](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia)

[[32] Securelist: The “Kimsuky” Operation: A North Korean
APT?](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[33] Private Sector Partner

[34] Private Sector Partner

[[35] Securelist: The “Kimsuky” Operation: A North Korean
APT?](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[[36] Yoroi: The North Korean Kimsuky APT Keeps Threatening South Korea
Evolving…](https://yoroi.company/research/the-north-korean-kimsuky-apt-keeps-threatening-south-korea-evolving-its-ttps/)

[[37] Yoroi: The North Korean Kimsuky APT Keeps Threatening South Korea
Evolving…](https://yoroi.company/research/the-north-korean-kimsuky-apt-keeps-threatening-south-korea-evolving-its-ttps/)

[[38] Securelist: The “Kimsuky” Operation: A North Korean
APT?](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[[39] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[40] Securelist: The “Kimsuky” Operation: A North Korean
APT?](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[[41] Securelist: The “Kimsuky” Operation: A North Korean
APT?](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[[42] Securelist: The “Kimsuky” Operation: A North Korean
APT?](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[[43] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[44] McAfee: What is mshta, how can it be used and how to protect against
it](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/what-is-mshta-how-can-it-be-used-and-how-to-protect-against-it/)

[[45] Securityweek.com: North Korean Suspected Cyber-espionage Attacks Against
S…](https://www.securityweek.com/north-korea-suspected-cyber-espionage-attacks-against-south-korean-entities)

[[46] Securelist: The “Kimsuky” Operation: A North Korean
APT?](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[[47] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[48] Detecting credential theft through memory access modelling with
Microsoft …](https://www.microsoft.com/security/blog/2019/05/09/detecting-credential-theft-through-memory-access-modelling-with-microsoft-defender-atp/)

[[49] MITRE ATT&CK: Groups – Kimsuky](https://attack.mitre.org/groups/G0094/)

[[50] ZDNet: Cyber-espionage-group-uses-chrome-extension-to-infect-victims](https://www.zdnet.com/article/cyber-espionage-group-uses-chrome-extension-to-infect-victims/)

[[51] ZDNet: Cyber-espionage-group-uses-chrome-extension-to-infect-victims](https://www.zdnet.com/article/cyber-espionage-group-uses-chrome-extension-to-infect-victims/)

[[52] Netscout: Stolen Pencil Campaign Targets Academia
](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia)

[[53] Netscout: Stolen Pencil Campaign Targets Academia
](https://www.netscout.com/blog/asert/stolen-pencil-campaign-targets-academia)

[54] Private Sector Partner

[[55] Securelist: The “Kimsuky” Operation: A North Korean APT?
](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[[56] Securelist: The “Kimsuky” Operation: A North Korean APT?
](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[57] Private Sector Partner

[[58] Securelist: The “Kimsuky” Operation: A North Korean APT?
](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

[59] Private Sector Partner

[[60] Securelist: The “Kimsuky” Operation: A North Korean APT?
](https://securelist.com/the-kimsuky-operation-a-north-korean-apt/57915/)

## Revisions

2020年10月27日：初始版本

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1384/>

