**作者：知道创宇404实验室翻译组**  
**原文链接：<https://www.cybereason.com/blog/back-to-the-future-inside-the-kimsuky-kgh-spyware-suite>**

### 前言

[Cybereason Nightnus团队](https://www.cybereason.com/company/nocturnus
"Cybereason
Nightnus团队")一直在追踪朝鲜的各种黑客组织，其中包括名为[Kimsuky](https://attack.mitre.org/groups/G0094/
"Kimsuky")（又名：Velvet Chollima、Black
Banshee和Thillium）的网络间谍组织。该组织至少从2012年开始活跃，在全球有许多攻击历史，包括针对韩国智库的攻击，在过去几年里，他们将攻击目标扩大到包括美国、俄罗斯和欧洲各国在内的国家。他们的观测目标包括：

  * Pharmaceutical/Research companies working on COVID-19 vaccines and therapies
  * UN Security Council
  * South Korean Ministry of Unification 
  * Various Human Rights Groups
  * South Korean Institute for Defense Analysis
  * Various Education and Academic Organizations
  * Various Think Tanks
  * Government Research Institutes
  * Journalists covering Korean Peninsula relations
  * South Korean Military

10月27日，[US-CERT发布了一份报告](https://us-cert.cisa.gov/ncas/alerts/aa20-301a "US-CERT发布了一份报告")，总结了Kimusky最近的活动，并描述了该组织的TTP和基础设施。

研究人员将报告中的信息与Cybereason
Nightnus积累的情报相结合，发现了一个未记录的模块化间谍软件套件，名为KGH_SPY，该套件为Kimsuky提供了执行间谍行动的隐身能力。

此外，Cybereason Nightnus还发现了另一种被称为CSPY
Downloader的新恶意软件，据观察，它是一种复杂的工具，具有广泛的反分析和规避能力，允许攻击者在下载额外的有效负载之前确定是否“the coast
is clear”。

最后，Cybereason Nightnus团队确定了Kimsuky使用的新服务器基础设施，该基础设施与之前确定的Kimsuky基础设施重叠。

![](https://images.seebug.org/content/images/2020/11/19a1d615-9115-4834-a89a-359a7a842fe5.png-w331s)
Cybereason Platform抓获KGH后门

### 主要发现

  * **发现一个新的模块化间谍软件套件：** “KGHüu SPY”是一个模块化工具套件，为攻击者提供侦察、键盘记录、信息窃取和后门功能。
  * **发现一种隐形的新恶意软件：** “CSPY Downloader”是一种旨在逃避分析和下载额外有效负载的工具。
  * **新的工具集基础设施：** 新发现的工具集基础设施注册于2019-2020年，与另一个名为[BabyShark](https://malpedia.caad.fkie.fraunhofer.de/details/win.babyshark "BabyShark")的Kimsuky恶意软件重叠，该恶意软件过去曾被用于针对[美国的智库](https://unit42.paloaltonetworks.com/new-babyshark-malware-targets-u-s-national-security-think-tanks/ "美国的智库")。
  * **反取证：** 报告中恶意软件的创建/编译时间似乎被篡改以阻止调查取证。
  * **与其他Kimsuky恶意软件的行为和代码相似性：** 新发现的恶意软件与已知的Kimsuky恶意软件具有各种行为和代码相似性，包括：使用EGIS吊销证书的代码签名；共享字符串；文件命名约定；字符串解密算法；引用作者/项目的PDB路径。
  * **未被防病毒检测到：** 在编写本报告时，任何防病毒供应商都未检测到一些有效负载。

### KIMSUKY基础设施重叠

Kimsuky以其复杂的基础设施而闻名，该基础设施使用免费注册的域、受损的域以及该组织注册的私有域。通过对基础设施的追踪，Nightneus团队能够检测到与[BabyShark](https://malpedia.caad.fkie.fraunhofer.de/details/win.babyshark
"BabyShark")恶意软件的重叠，以及与不同恶意软件（如[Applesed](https://www.virusbulletin.com/uploads/pdf/conference_slides/2019/VB2019-Kim.pdf
"Applesed")后门）的其他连接：

![](https://images.seebug.org/content/images/2020/11/a7f7f897-a207-493d-b8c1-4c10c1a5387e.png-w331s)
不同Kimsuky域的基础结构图及其之间的重叠

这些年来，Kimsuky一直在他们的操作中使用一系列恶意软件。Kimsuky使用的一些恶意软件的基础设施可以通过对他们的一些工具所使用的URI结构的模式分析来跟踪。下表将常见的URI模式映射到各自的恶意软件：

Malware name | Description | C2 URL Pattern  
---|---|---  
[AppleSeed](https://www.virusbulletin.com/uploads/pdf/conference_slides/2019/VB2019-Kim.pdf
"AppleSeed") | Backdoor |
http://hao.aini.pe[.]hu/init/image?i=ping&u=8dc1078f1639d34c&p=wait..  
AppleSeed | Backdoor | http://mernberinfo[.]tech/wp-data/?m=dunan&p=de3f6e263724&v=win6.1.0-sp1-x64  
AppleSeed | Backdoor |
http://eastsea.or[.]kr/?m=a&p1=00000009&p2=Win6.1.7601x64-Spy-v2370390  
[FlowerPower](https://vblocalhost.com/uploads/VB2020-46.pdf "FlowerPower") |
Powershell based profiling tool |
http://dongkuiri.atwebpages[.]com/venus02/venus03/venus03.ps1  
FlowerPower | Powershell based profiling tool |
http://attachchosun.atwebpages[.]com/leess1982/leess1982.ps1  
[Gold Dragon](https://malpedia.caad.fkie.fraunhofer.de/details/win.gold_dragon
"Gold Dragon") | Backdoor |
http://portable.epizy[.]com/img/png/download.php?filename=images01  
Gold Dragon | Backdoor |
http://foxonline123.atwebpages[.]com/home/jpg/download.php?filename=flower03  
[BabyShark](https://malpedia.caad.fkie.fraunhofer.de/details/win.babyshark
"BabyShark") | VBS-based backdoor and reconnaissance tool |
http://nhpurumy.mireene[.]com/theme/basic/skin/member/basic/
upload/download.php?param=res2.txt  
BabyShark | VBS-based backdoor and reconnaissance tool |
http://jmable.mireene[.]com/shop/kcp/js/com/expres.php?op=2  
  
### 新的工具集基础设施

通过跟踪以前的基础设施并将不同Kimsuky工具使用的URI模式相关的数据关联起来，我们发现新恶意软件工具集使用的新基础设施：

Malware name | Description | C2 URL Pattern  
---|---|---  
KGH malware suite | Different components in the KGH malware suite |
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=sbk&ver=x64  
KGH malware suite | Different components in the KGH malware suite |
http://csv.posadadesantiago[.]com/home/up.php?id=[Machine_name]  
CSPY Downloader | Downloader |
http://wave.posadadesantiago[.]com/home/dwn.php?van=10860  
CSPY Downloader | Downloader |
http://wave.posadadesantiago[.]com/home/dwn.php?van=101  
CSPY Downloader | Downloader |
http://wave.posadadesantiago[.]com/home/dwn.php?van=102  
KGH_Backdoor winload.x | Backdoor and Keylogger component, VBS downloader |
http://csv.posadadesantiago[.]com/home?act=news&id=[Machine_name]  
KGH_Backdoor winload.x | Backdoor and Keylogger component, VBS downloader |
http://csv.posadadesantiago[.]com/home?id=ֿ[Machine_name]&act=upf&ver=x64  
KGH_Backdoor winload.x | Backdoor and Keylogger component, VBS downloader |
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=tre&ver=x64  
KGH_Backdoor winload.x | Backdoor and Keylogger component, VBS downloader |
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=wbi&ver=x64  
KGH_Backdoor winload.x | Backdoor and Keylogger component, VBS downloader |
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=cmd&ver=x64  
KGH_Backdoor winload.x | Backdoor and Keylogger component, VBS downloader |
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=pws&ver=x64  
PM_Abe_draft_letter _on_UN_NK_20200130.doc | Phishing document |
http://myaccounts.posadadesantiago[.]com/test/Update. php?wShell=201  
  
新域名注册的IP地址与之前Kimsuky相关的涉及Baby Shark恶意软件的攻击报告的IP地址相同：

IP Address | Domain Name | Kimsuky Activity  
---|---|---  
173.205.125.124 | csv.posadadesantiago[.]com | KGH Backdoor  
173.205.125.124 | wave.posadadesantiago[.]com | CSPY Downloader  
173.205.125.124 | myaccounts.posadadesantiago[.]com | Malicious Phishing
Document  
173.205.125.124 | www.eventosatitlan[.]com | Baby Shark / Autumn Aperture
Campaign  
  
### 疑似反取证

回溯（[timestomping](https://attack.mitre.org/techniques/T1070/006/
"timestomping")）是许多攻击者使用的一种技术，它涉及到操纵文件的创建时间或编译日期，以阻止分析尝试（反取证）。据怀疑，本报告中提到的大多数文件的创建日期被攻击者篡改，并追溯到2016年：

Name | SHA-256 | Creation Date (likely fake) | VT Upload Date  
---|---|---|---  
m1.dll cur_install_x64.dll |
af13b16416760782ec81d587736cb4c9b2e7099afc10cb764eeb4c 922ee8802f | 2016-10-02
07:35:25 |  
2020-10-07 13:03:45 |  |  |  
msic.exe | E4d28fd7e0fc63429fc199c1b683340f725f0bf9834345174ff0b6a 3c0b1f60e |
2016-09-28 02:08:00 | 2020-10-07 13:03:530  
msfltr32.dll | 66fc8b03bc0ab95928673e0ae7f06f34f17537caf159e178a452c2
c56ba6dda7 | 2016-10-02 07:23:16 | 2020-10-07 13:03:56  
m.dll | f989d13f7d0801b32735fee018e816f3a2783a47cff0b13d70ce2f 1cbc754fb9 |
2016-09-28 08:41:36 | 2020-10-07 13:03:56  
0807.dotm | 97d4898c4e70335f0adbbace34593236cb84e849592e5971a797 554d3605d323
| 2016-08-07 11:31:00 | 2020-08-19 09:46:33  
0928.dotm | d88c5695ccd83dce6729b84c8c43e8a804938a7ab7cfeccaa0699 d6b1f81c95c
| 2016-09-28 02:08:00 | 2020-10-06 07:53:38  
winload.exe | 7158099406d99db82b7dc9f6418c1189ee472ce3c25a3612a5ec
5672ee282dc0 | 2016-07-30 01:20:23 | 2020-06-12 01:48:02  
  
这一假设得到了上述所有恶意软件样本中硬编码域的注册日期的支持。根据[RiskIQ
PassiveTotal](https://community.riskiq.com/ "RiskIQ
PassiveTotal")中的域名注册信息，这些域名首次注册时间为2019年1月至2020年8月，即看似被操纵的创建日期之后数年：

Domain | IP Resolution | First Observed | Earliest Observed Certificate Issue
Date  
---|---|---|---  
csv.posadadesantiago[.]com | 173.205.125.124 | 2020-08-09 | **SHA-1:**
87b35e1998bf00a8b7e32ed391c217deaec408ad **Date:** 2020-08-19  
wave.posadadesantiago[.]com | 173.205.125.124 | 2020-02-27 | **SHA-1:**
F846981567760d40b5a90c8923ca8c2e7c881c5f **Date:** 2020-03-24  
myaccounts.posadadesantiago[.]com | 173.205.125.124 | 2019-01-25 | **SHA-1:**
90d00ecb1e903959a3853e8ee1c8af89fb82a179 **Date:** 2019-01-25  
  
### KGH间谍软件套件

![](https://images.seebug.org/content/images/2020/11/66d61815-2742-4046-81a4-5543427dd093.png-w331s)
KGH恶意软件套件的不同组件之间的连接

在我们的分析过程中，CyberEasonNightus发现了一个名为“KGH”的新恶意软件套件，其中包含多个用作间谍软件的模块。名称“KGH”来源于在恶意软件示例中找到的PDB路径和内部名称：

![](https://images.seebug.org/content/images/2020/11/9955e80e-0929-42f3-a026-f2d1bb8bd996.png-w331s)
后门内部名称中的“KGH”

![](https://images.seebug.org/content/images/2020/11/87a8cf9a-bb98-4b8a-b53f-91c15ce44248.png-w331s)
“m.dll”pdb路径

2017年，[Ahnlab在一份研究报告](https://www.slideshare.net/JackyMinseokCha/targeted-attacks-on-major-industry-sectors-in-south-korea-20171201-cha-minseokavar-2017-beijingfull-version
"Ahnlab在一份研究报告")中提到了“KGH”，但尚不清楚这是否与同一名恶意软件作者有关。

### 感染媒介：恶意WORD文档

感染载体似乎来自包含恶意宏的Word文档：

Name | SHA-256 | Domain | Creation Date (likely fake) | VT Upload Date  
---|---|---|---|---  
0807.dotm | 97d4898c4e70335f0adbbace34593236cb84e849592e5971a797554d3605d323 |
csv.posadadesantiago.com | 2016-08-07 11:31:00 | 2020-08-19 09:46:33  
0928.dotm | d88c5695ccd83dce6729b84c8c43e8a804938a7ab7cfeccaa0699d6b1f81c95c |
csv.posadadesantiago.com | 2016-09-28 02:08:00 | 2020-10-06 07:53:38  
  
我们观察到了两个Word文档，它们与上面提到的域进行通信，其中包含彼此的代码相似之处，以及前面提到的“Interview with a north
korean defector.doc”。 恶意文档的宏执行以下操作：

**0807.dotm：**

1.将名为“winload.x”的脚本和重命名为“cs.exe”的wscript.exe二进制文件删除到“%appdata%\Micorosoft\Templates”。

2.设置注册表项“HKCU \ Environment \
UserInitMprLogonScript”以运行cmd命令，该命令将“winload.x”复制为“a.vbs”，执行该命令并删除“a.vbs”。提到的注册表项用于执行登录脚本，并将在启动时执行写入到注册表中的内容。该文档正在使用此密钥来实现文件“winload.x”的持久性：

![](https://images.seebug.org/content/images/2020/11/e0b1b415-d364-411f-a961-5b4fc0548735.png-w331s)
使用UserInitMprLogonScript注册表项的持久性

3.收集系统，网络和驱动器信息以及已安装的应用程序，将其保存到名为“info”的文件，然后使用iexplorer.exe将其发送到C2。

4.执行“winload.x”（“a.vbs”）时，它将尝试从“csv.posadadesantiago[.]com/home?act=news&id=[Machine_name]”下载并执行代码：

![](https://images.seebug.org/content/images/2020/11/6220fdb3-b95e-4034-a633-5efd333638a6.png-w331s)

**0928.dotm:**

1.收集有关受感染的系统、网络、驱动器和已安装的应用程序的信息。

2.将收集到的信息保存到“%appdata%\Micorosoft\Templates”中名为“info”的文件中，并将其发送到C2。

3.从“csv.posadadesantiago[.]com/home?id=[Machine_name]&act=sbk&ver=x64”下载m1.dll（KGH安装程序）。

4.从“csv.posadadesantiago[.]com/home?id=[Machine_name]&act=wbi&ver=x64”下载m.dll（KGH
Browser Stealer）。

5.执行KGH安装程序：

![](https://images.seebug.org/content/images/2020/11/e27b3ed4-1c9f-4724-a520-319d5e2d1847.png-w331s)
从0928.dotm宏代码创建URL

这两个文档使用相似的函数名和变量名：

![](https://images.seebug.org/content/images/2020/11/476ba9b0-4ec6-48a7-84c8-034b6a67233d.png-w331s)
0928.dotm VB代码（左）和0807.dotm VB代码（右）

一旦宏收集了所有信息，它就会通过HTTP POST请求将数据发送到C2服务器：

![](https://images.seebug.org/content/images/2020/11/9eaeb731-ccb8-4bc9-9c0f-4868ef81669e.png-w331s)
收集在“info”中的系统信息

### KGH间谍软件有效负载概述

观察到以下有效负载已被前述恶意文件下载和删除：

File Name(s) | Purpose | Creation Date (likely fake) | VT Upload Date  
---|---|---|---  
m1.dll | Drops KGH backdoor and creates persistence to msic.exe and drops:-C:\Users\user\AppData\Local\AreSoft\msic.exe -C:\Users\user\AppData\Local\AreSoft\msfltr32.dll | 2016-10-02 07:35:25 |
2020-10-07 13:03:45  
msic.exe | Loads and executes msfltr32.dll
C:\Users\user\AppData\Local\AreSoft\msfltr32.dll | 2016-09-28 02:08:00 |
2020-10-07 13:03:53  
msfltr32.dll | KGH backdoor capabilities: - Persistence - Keylogger -Downloads additional payloads - Executes arbitrary commands (cmd.exe /
powershell) | 2016-10-02 07:23:16 | 2020-10-07 13:03:56  
m.dll | KGH-Browser Stealer Steals stored data from Chrome, Edge, Firefox,
Thunderbird, Opera, Winscp. | 2016-09-28 08:41:36 | 2020-10-07 13:03:56  
  
Cybereason平台捕获的宏下载/删除了以下文件：

![](https://images.seebug.org/content/images/2020/11/90384231-3307-4fd0-82fd-4fc58c0a45ae.png-w331s)
文件的创建

### KGH安装程序（M1.DLL）的分析

KGH安装程序已于2020年10月上传到VirusTotal，在撰写本文时，任何防病毒引擎都未检测到此报告：

![](https://images.seebug.org/content/images/2020/11/8bca4b25-6e0b-437a-8e33-8e4cf8531289.png-w331s)
VT中的KGH安装程序检测

该文件是一个DLL，它执行“outinfo”导出中的安装/删除程序代码：

![](https://images.seebug.org/content/images/2020/11/9a73bdd9-d32f-4bb0-afd0-64cc6687965f.png-w331s)
KGH安装程序出口

DLL的资源部分包含两个加密的Blob。可以看到，在这些资源中有朝鲜语的痕迹：

![](https://images.seebug.org/content/images/2020/11/ca7c5897-5fe0-4b75-8400-d4140c07db37.png-w331s)

这些加密的Blob依次放置到C:\Users\user\AppData\Local\Temp\3f34a.tmp。删除它们之后，程序还将对其解密并写入新创建的文件夹并创建持久性：

  * C:\Users\user\AppData\Local\AreSoft\msic.exe
  * C:\Users\user\AppData\Local\AreSoft\msfltr32.dll

![](https://images.seebug.org/content/images/2020/11/8deb5944-decd-4576-93a0-c3b546ccf27e.png-w331s)
删除受感染机器上的文件位置

后门通过创建以下注册表自动运行项来实现持久性：

**Key:** HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows\Load  
**Value:** C:\Users\user\AppData\Local\AreSoft\msic.exe

### KGH后门装载程序（MSIC.EXE）的分析

KGH加载程序（msic.exe）负责在内存中加载和执行KGH后门DLL（msfltr32.dll）：

![](https://images.seebug.org/content/images/2020/11/8a689907-c8db-4169-b447-3fbf73421dea.png-w331s)
Msic.exe将msfltr32.dll加载到内存

该文件本身是未签名的，并且伪装成合法的Microsoft Windows工具：

![](https://images.seebug.org/content/images/2020/11/6d400daa-ef2b-4a97-8d45-a2cbc6800ca8.png-w331s) Msfltr32.dll签名信息

### KGH后门-主模块（MSFLTR32.DLL）

msfltr32.dll是KGH后门的核心模块。后门包含以下功能：

  * Persistence using autorun keys
  * Keylogger
  * Directory and file listing
  * Downloading secondary payloads from the C2 server
  * Exfiltrating collected information from the host to the C2 server
  * Executing arbitrary commands via cmd.exe or PowerShell

### KGH后门：键盘记录功能

KGH后门在其代码中内置了键盘记录程序功能，这是通过轮询[GetAsyncKeyState（）](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate
"GetAsyncKeyState（）")函数的常用[技术](https://eyeofrablog.wordpress.com/2017/06/11/windows-keylogger-part-1-attack-on-user-land/ "技术")来实现的：

![](https://images.seebug.org/content/images/2020/11/ff5750ca-5f1f-43f7-8514-e1345dbbda0f.png-w331s)
摘录自KGH的键盘记录器功能

记录的内容存储在%appdata%中的“lg”文件夹中，文件扩展名为“.x”。

### KGH后门二级负载

KGH后门通过“csv.posadadesantiago[.]com/home?act=news&id=[Machine_name]”与C2联系，并将响应保存到“C:\Users\user\AppData\Local\Temp\n.x”：

![](https://images.seebug.org/content/images/2020/11/a5635560-7fdc-49f5-8c88-39eabfe152c5.png-w331s)
KGH后门中的URL字符串

然后，KGH后门将解析“nx”的内容。“nx”文件可能包含“SHL”，“DLL”或“EXE”文件。

如果是“DLL”或“EXE”，则KGH后门将执行该文件。如果下载的文件包含“SHL”文件，则KGH后门将解析该文件以检索C2发送的命令：

![](https://images.seebug.org/content/images/2020/11/8c42ed2d-fa63-4596-8aa9-3acb93ca4cd6.png-w331s)
从KGH后门检查“nx”文件类型代码

### KGH后门命令

KGH后门具有从服务器接收的一组预定义命令：

![](https://images.seebug.org/content/images/2020/11/1ca6023e-eecf-4448-92d3-b2aaf0888d41.png-w331s)

Command | Purpose  
---|---  
upf | Uploads files to the C2  
tre | Create a list of all files in the system using the “tree” command, save
to a file named “c.txt” and upload the file to the C2  
wbi | Download “m.dll” browser stealer module and exfiltrates stolen data  
cmd | Execute a cmd shell command  
pws | Execute a powershell command  
  
KGH后门生成或下载的文件列表：

File | Purpose  
---|---  
C:\Users\user\AppData\Roaming\lg[year_month_day].x | Keylogger stolen data
storage  
C:\Users\user\AppData\Local\Temp\n.x | Payload downloaded from the server  
C:\Users\user\AppData\Local\Temp\C.txt | Output of tree command (directory and
files listing) C:\Windows\System32\cmd.exe /c tree /f C:\ >>
C:\Users\user\AppData\Local\Temp\C.txt  
C:\Users\user\Documents\w.x | Stolen browser data (from m.dll module)  
sig.x | Likely checks write permission to the disk  
C:\test1.txt | N/A  
  
### KGH INFOSTEALER模块（M.DLL）

KGH套件的另一个组件是m.dll模块，它用于信息窃取，可以从浏览器，Windows Credential
Manager，WINSCP和邮件客户端中收集数据。在编写此报告时，任何AV供应商都未检测到infostealer模块。

嵌入在m.dll模块中的PDB路径进一步显示了与KGH后门的清晰连接，因为它被命名为“KGH_Browser-Master”：

![](https://images.seebug.org/content/images/2020/11/08664c8c-7481-4061-b593-d866bc7c6831.png-w331s)

在“CSPY Downloader”的PDB中也观察到“SPY”用户，此报告中也提到了该用户：

![](https://images.seebug.org/content/images/2020/11/74cdcce0-a543-4975-8587-f107819f0b3d.png-w331s)
CSPY下载器的PDB路径

infostealer模块窃取了以下应用程序中存储的信息（cookie，凭据）：

  * **浏览器：** Chrome，IE / Edge，Firefox，Opera
  * **WinSCP客户端**
  * **Windows凭据管理器**
  * **Mozilla Thunderbird邮件客户端**

![](https://images.seebug.org/content/images/2020/11/502b9441-d304-4125-8803-57cdead19139.png-w331s)
主要信息窃取程序

被盗的信息被写入一个名为“wx”的文件中：

![](https://images.seebug.org/content/images/2020/11/562aa0af-2697-4603-9fbd-c9df7ce025c7.png-w331s)
创建存储被盗数据的“wx”文件

### CSPY下载器

当寻找[US-CERT报告](https://us-cert.cisa.gov/ncas/alerts/aa20-301a "US-CERT报告")中提到的某些URI模式（“ /home/dwn.php?van=101”）时，发现另一个恶意可执行文件与C2
wave.posadadesantiago[.]com通信。

该样本是由一个名为“Interview with a north Korean
defector”的[恶意文档](https://www.virustotal.com/gui/file/252d1b7a379f97fddd691880c1cf93eaeb2a5e5572e92a25240b75953c88736c/detection
"恶意文档")提供的。嵌入其中的宏将解压缩并执行winload.exe。

经过分析，Nocturnus确定winload.exe是一种新型的下载程序，被Cybereason称为“CSPY”
，其中包含强大的规避技术，旨在确保“coast is clear”，并且在继续下载辅助有效负载之前，恶意软件不会在虚拟机或分析工具的上下文中运行：

![](https://images.seebug.org/content/images/2020/11/d12bcbc7-e322-4dc4-b9f4-0ac9f1d2de0f.png-w331s)
VirusTotal上传的winload.exe与上述C2通信

[ESTSecurity](https://blog.alyac.co.kr/3052
"ESTSecurity")在报告中提到了这个文件。与调查结果一致的是，它配备了UPX，具有韩语资源、反虚拟机功能和时间戳，时间戳调整为2016年7月30日：

![](https://images.seebug.org/content/images/2020/11/e150ecf1-aded-4b7a-8f99-3929dc6bdcee.png-w331s)
CSPY下载器的PDB路径

![](https://images.seebug.org/content/images/2020/11/9895e71e-f810-4668-ace6-0d3d8ce52172.png-w331s)
PDB恶意软件的路径和资源

该文件还使用以下已吊销的证书进行签名。可见，签约日期也可能是假的。

![](https://images.seebug.org/content/images/2020/11/c36adf27-822e-471e-8170-99406e4bcd1e.png-w331s)
Kimsuky的典型吊销证书

当进一步检查文件时，可以找到一些有趣的功能。指示性字符串和API调用可以通过从每个字符中扣除1来解密，类似于KGH后门，后者的字符串可以通过从每个字符中扣除5来解密。解密字符串时，会显示恶意软件的完整日志。日志文件存储在%appdata%\microsoft\NTUSERS.log：

![](https://images.seebug.org/content/images/2020/11/3455d1ce-78c3-4cbd-bcb3-66018851fd5e.png-w331s) CSPY Downloader的解密日志字符串

有趣的是，上面提到的一些日志字符串有语法错误，这可能表明攻击者不是以英语为母语的人。

以上日志暗示此示例可能是恶意软件的调试版本。在许多情况下，攻击者使用调试版本来测试新的恶意软件或新功能。这也可能意味着该恶意软件是新开发的，尚未完全投入运行。另一个指向这一假设的线索是，恶意软件代码的某些部分似乎有缺陷或不完整。

## 反分析技术

在下载辅助有效负载之前，CSPY
Downloader会启动一系列广泛的检查，通过搜索与虚拟化相关的特定加载模块、进程PEB结构、各种文件路径、注册表项和内存，来确定它是否正在虚拟环境中调试或运行：

![](https://images.seebug.org/content/images/2020/11/de7125ed-64d7-402e-b58b-fca0e4380041.png-w331s)
恶意软件执行反分析检查的方法列表

值得一提的是，解压缩CSPY
Downlader的[文件](https://www.virustotal.com/gui/file/252d1b7a379f97fddd691880c1cf93eaeb2a5e5572e92a25240b75953c88736c/detection
"文件")在删除下载程序之前运行了一系列几乎相同的反虚拟机技术。反分析检查完成后，加载程序开始准备受感染的环境以下载其他有效负载。一共有3次下载尝试（因此3次GET请求后面有一个不同的数字ID），有效负载随后被下载到用户的%temp%文件夹中。

![](https://images.seebug.org/content/images/2020/11/f14564c4-235d-4c45-bd71-912588a39571.png-w331s)
有效负载下载方法

下载有效负载后，它们将被移动并重命名。整个过程可以总结如下：

Download URI | Filename | Copied To | Purpose  
---|---|---|---  
dwn.php?van=10860 | dwn.dat0 | %temp%\Appx.exe | Main executable  
dwn.php?van=101 | dwn.dat1 | C:\Users\Public\Documents\AppxUp\BSup.hf |
Possible module  
dwn.php?van=102 | dwn.dat2 | C:\Users\Public\Documents\AppxUp\BCup.hf |
Possible module  
  
为了执行下载的主要有效负载，加载程序尝试伪装成合法的Windows服务，并在其虚假描述中声称其用于支持打包的应用程序。

为了避免引起受害者的怀疑，CSPY下载器利用了一种已知的UAC旁路[技术](https://cqureacademy.com/cqure-labs/cqlabs-how-uac-bypass-methods-really-work-by-adrian-denkiewicz
"技术")，该技术使用SilentCleanup任务以提升的权限执行二进制文件。

![](https://images.seebug.org/content/images/2020/11/649db2c9-9673-4ab0-877c-64dc816fba14.png-w331s)
使用schtasks实用程序禁用UAC

作为利用过程的一部分，以上值将在%windir%变量下写入注册表，并在执行后删除。Appx.exe再次移动到了%programdata%\Microsoft\Windows，并且已注册为服务。

最后，CSpy将启动其自删除方法。

### 结论

在此报告中，我们发现了Kimsuky组织使用了新的工具集基础设施，该组织是一个臭名昭著的黑客组织，自2012年以来一直代表朝鲜政权开展活动。通过对新基础结构的仔细检查与模式分析相结合，Cybereason的Neuternus团队发现了“KGH
恶意软件套件”（一种可能参与近期间谍活动的模块化恶意软件）和“CSPY Downloader”（以前均未记录）。

我们发现，旧的Kimsuky恶意软件和服务器与新发现的恶意软件和基础设施之间存在某些有趣的重叠。此外，报告还强调了新的恶意软件样本与旧的Kimsuky恶意软件和ttp之间基于行为和代码的相似性。

在整个报告中，值得注意的是，攻击者采用了各种反取证和反分析技术来躲避检测，包括将恶意软件样本的创建/编译时间回溯到2016年、使用代码混淆、反虚拟机和反调试技术。在撰写本报告时，我们提到的一些样品仍未被任何供应商检测到。

虽然这次活动的受害者仍不清楚，但有线索表明，这些基础设施针对的是处理侵犯人权行为的组织。未来，Kimsuky可能会针对许多行业、组织和个人进行攻击。

### MITRE ATT&CK BREAKDOWN

Reconnaissance | Initial Access | Execution | Persistence | Defense Evasion |
Credential Access | Discovery | Collection | Exfiltration  
---|---|---|---|---|---|---|---|---  
[Gather Victim Host Information](https://attack.mitre.org/techniques/T1592/
"Gather Victim Host Information") |
[Phishing](https://attack.mitre.org/techniques/T1566/ "Phishing") | [Command
and Scripting Interpreter](https://attack.mitre.org/techniques/T1059/ "Command
and Scripting Interpreter") | [Registry Run
Keys](https://attack.mitre.org/techniques/T1547/001/ "Registry Run Keys") |
[Masquerading](https://attack.mitre.org/techniques/T1036/ "Masquerading") |
[Credentials from Web Browsers](https://attack.mitre.org/techniques/T1555/003/
"Credentials from Web Browsers") | [File and Directory
Discovery](https://attack.mitre.org/techniques/T1083/ "File and Directory
Discovery") | [Keylogging](https://attack.mitre.org/techniques/T1056/001/
"Keylogging") | [Exfiltration Over C2
Channel](https://attack.mitre.org/techniques/T1041/ "Exfiltration Over C2
Channel")  
[Gather Victim Network Information](https://attack.mitre.org/techniques/T1590/
"Gather Victim Network Information") |  | [User
Execution](https://attack.mitre.org/techniques/T1204/ "User Execution") |
[Logon Script (Windows) ](https://attack.mitre.org/techniques/T1037/001/
"Logon Script \(Windows\) ") | [Bypass User Account
Control](https://attack.mitre.org/techniques/T1548/002/ "Bypass User Account
Control") | [Keylogging](https://attack.mitre.org/techniques/T1056/001/
"Keylogging") | [System Information
Discovery](https://attack.mitre.org/techniques/T1082/ "System Information
Discovery") |  |  
|  |  | [Windows Service](https://attack.mitre.org/techniques/T1543/003/
"Windows  Service") |
[Timestomp](https://attack.mitre.org/techniques/T1070/006/ "Timestomp") |
[Steal Web Session Cookie](https://attack.mitre.org/techniques/T1539/ "Steal
Web Session Cookie") | [System Network Configuration
Discovery](https://attack.mitre.org/techniques/T1016/ "System Network
Configuration Discovery") |  |  
|  |  |  | [Software Packing](https://attack.mitre.org/techniques/T1027/002/
"Software Packing") |  | [Virtualization/Sandbox
Evasion](https://attack.mitre.org/techniques/T1497/ "Virtualization/Sandbox
Evasion") |  |  
  
### IOC

**URLs:**

http://csv.posadadesantiago[.]com/home?act=news&id=[Machine_name]  
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=upf&ver=x64  
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=tre&ver=x64  
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=wbi&ver=x64  
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=cmd&ver=x64  
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=pws&ver=x64  
http://csv.posadadesantiago[.]com/home?id=[Machine_name]&act=sbk&ver=x64  
http://csv.posadadesantiago[.]com/home/up.php?id=[Machine_name]  
http://myaccounts.posadadesantiago[.]com/test/Update.php?wShell=201  
http://wave.posadadesantiago[.]com/home/dwn.php?van=10860  
http://wave.posadadesantiago[.]com/home/dwn.php?van=101  
http://wave.posadadesantiago[.]com/home/dwn.php?van=102

**Domains**

csv.posadadesantiago[.]com  
wave.posadadesantiago[.]com  
myaccounts.posadadesantiago[.]com  
www.eventosatitlan[.]com

**IPs**

173.205.125.124（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=173.205.125.124
"ZoomEye搜索结果")）  
Malicious Documents  
97d4898c4e70335f0adbbace34593236cb84e849592e5971a797554d3605d323  
d88c5695ccd83dce6729b84c8c43e8a804938a7ab7cfeccaa0699d6b1f81c95c  
7af3930958f84e0b64f8297d1a556aab359bb65691208dc88ea4fc9698250c43  
252d1b7a379f97fddd691880c1cf93eaeb2a5e5572e92a25240b75953c88736c

**KGH SPYWARE SUITE**

Bcf4113ec8e888163f1197a1dd9430a0df46b07bc21aba9c9a1494d2d07a2ba9  
af13b16416760782ec81d587736cb4c9b2e7099afc10cb764eeb4c922ee8802f  
E4d28fd7e0fc63429fc199c1b683340f725f0bf9834345174ff0b6a3c0b1f60e  
66fc8b03bc0ab95928673e0ae7f06f34f17537caf159e178a452c2c56ba6dda7  
f989d13f7d0801b32735fee018e816f3a2783a47cff0b13d70ce2f1cbc754fb9  
Fa282932f1e65235dc6b7dba2b397a155a6abed9f7bd54afbc9b636d2f698b4b  
65fe4cd6deed85c3e39b9c1bb7c403d0e69565c85f7cd2b612ade6968db3a85c

**CSPY Downloader**

7158099406d99db82b7dc9f6418c1189ee472ce3c25a3612a5ec5672ee282dc0  
e9ea5d4e96211a28fe97ecb21b7372311a6fa87ce23db4dd118dc204820e011c

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1388/>

