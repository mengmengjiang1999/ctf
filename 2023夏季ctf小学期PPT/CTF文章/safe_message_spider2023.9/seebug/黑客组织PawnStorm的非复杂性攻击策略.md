**译者：知道创宇404实验室翻译组  
原文链接：<https://www.trendmicro.com/en_us/research/20/l/pawn-storm-lack-of-sophistication-as-a-strategy.html>**

## 前言

远程访问木马（RAT）的防御者不会立即辨别这是来自APT黑客的恶意软件。同样，网络服务（例如电子邮件、Microsoft
Autodiscover、SMB、LDAP和SQL）的恶意攻击也是如此。在2020年，APT黑客组织Pawn Storm使用非复杂的攻击方法。

2020年，Pawn
Storm黑客组织传播了Google云端硬盘和IMAP远程访问木马（RAT）进行网络攻击，目标群体包括外交部、大使馆、国防工业和军事部门以及世界各地的各行业。该组织还通过网络攻击窃取公司电子邮件帐户的凭据，还利用IMAP
RAT恶意软件对军方和政府相关的电子邮件地址进行了硬编码，与计算机进行通信。最近，挪威当局宣布Pawn
Storm黑客组织通过网络攻击[入侵了挪威议会](https://pst.no/alle-artikler/pressemeldinger/datainnbruddet-mot-stortinget-er-ferdig-etterforsket/) 。

恶意软件的后续版本揭露了黑客的发展趋势。仅使用样本很难将这些恶意软件归因于Pawn Storm。但基于对Pawn
Storm活动的长期监控，我们对这些样本进行了归属分类。

## Pawn Storm活动回顾：

**损害中东用户的帐户**

我们一直密切监控Pawn
Storm的活动，在2020年3月发布了[最新研究](https://www.trendmicro.com/vinfo/us/security/news/cyber-attacks/probing-pawn-storm-cyberespionage-campaign-through-scanning-credential-phishing-and-more#:~:text=Since May 2019%2C Pawn Storm,companies in
the Middle East.&text=The campaigns included spam waves,States%2C Russia%2C
and Iran.)上，我们分享了被Pawn
Storm严重攻击的帐户（主要在中东）。中东的攻击活动在2020年仍在继续。在2020年12月上旬，该组织使用VPN服务连接到受感染的云服务器，使用云服务器连接到商业电子邮件服务提供商，登录到阿曼一家养鸡场的受感染电子邮件帐户，向全球目标发送了网络钓鱼垃圾邮件。这表明Pawn
Storm黑客在多个级别上模糊了其攻击轨迹。

中东各种受感染电子邮件帐户的滥用始于2019年5月，并一直持续到今天。自2020年8月以来，他们不再发送网络钓鱼电子邮件，而是利用IMAP
RAT中受损系统进行通信。

**暴力网络攻击**

我们认为Pawn Storm通过对网络服务（例如电子邮件、LDAP、Microsoft
Autodiscover、SMB和SQL）的攻击来破坏电子邮件帐户。例如，在2020年5月，Pawn
Storm在TCP端口445和1433上扫描了包括来自欧洲国防工业IP地址，这可能是为了寻找易受攻击的SMB和SQL服务器的凭证。2020年8月，Pawn
Storm还从专用IP地址向全球LDAP服务器发送了UDP探测。

在2020年，Pawn
Storm试图通过在Tor和VPN服务器上攻击流量以掩藏踪迹。然而，这并不足以隐藏这些活动。在Microsoft[一篇](https://www.microsoft.com/security/blog/2020/09/10/strontium-detecting-new-patters-credential-harvesting/)有关通过Tor强行使用Office365凭据的[文章中](https://www.microsoft.com/security/blog/2020/09/10/strontium-detecting-new-patters-credential-harvesting/)，Microsoft将活动归因于Strontium，这是Pawn
Storm的另一个名称。我们在2020年初撰写了[有关攻击的文章](https://www.trendmicro.com/vinfo/us/security/news/cyber-attacks/probing-pawn-storm-cyberespionage-campaign-through-scanning-credential-phishing-and-more#:~:text=Since May 2019%2C Pawn Storm,companies in
the Middle East.&text=The campaigns included spam waves,States%2C Russia%2C
and Iran.)。这些攻击始于2019年，我们可以将全球Microsoft
Autodiscover服务器的广泛探测与高可信度指标进行关联，将其归咎于Pawn Storm黑客组织。

为说明Pawn Storm黑客组织的网络钓鱼攻击中恶意软件的简单性，我们通过以下示例进行描述：

Google Drive RAT的技术分析 ：

![图1.来自Pawn
Storm的鱼叉式网络钓鱼电子邮件–于2020年8月收集。](https://images.seebug.org/content/images/2020/12/21/1608521199000-1kxyym.png-w331s)图1.来自Pawn
Storm的网络钓鱼电子邮件–于2020年8月收集

从2020年8月开始，Pawn
Storm发送了几封带有恶意RAR附件的网络钓鱼电子邮件。在我们收到的最早的样本中，有两个几乎相同的RAR文件，其中包含一个名为info.exe的文件。这两个版本的info.exe文件都是自解压存档（SFX），它们提取并执行两个文件：decrypt.exe和gdrive.exe。

**c4a61b581890f575ba0586cf6d7d7d3e0c7603ca40915833d6746326685282b7**
installing

  * crypto.exe – 661d4a0d877bac9b813769a85c01bce274a77b29ccbd4b71e5b92df3c425b93b
  * gdrive.exe – cbd9cb7b69f864ce8bae983ececb7cf8627f9c17fdaba74bd39baa5cdf605f79

**3fd45b9b33ff5b6363ba0013178572723b0a912deb8235a951aa3f0aa3142509**
installing

  * crypto.exe – 661d4a0d877bac9b813769a85c01bce274a77b29ccbd4b71e5b92df3c425b93b
  * gdrive.exe – 2060f1e108f5feb5790320c38931e3dc6c7224edf925bf6f1840351578bbf9cc

## 诱饵文件

我们注意到文件crypto.exe是一个诱饵文件，执行info.exe后，它将运行。该应用程序仅显示一个消息框，用户可以在其中键入用于解密的密码。检查此文件的反汇编可以发现，只有在主应用程序上输入密码后，它才会显示另一个消息框。

![图2-典当风暴](https://images.seebug.org/content/images/2020/12/21/1608521201000-2kuhen.png-w331s)

![图2-3。
crypto.exe显示的消息框](https://images.seebug.org/content/images/2020/12/21/1608521203000-3dkbct.png-w331s)

图2-3.crypto.exe显示的消息框

关闭此应用程序后，SFX归档文件将执行文件gdrive.exe。gdrive.exe的不同版本几乎相同，只是在受害者的ID上对base64编码的文件2060f1e108f5feb5790320c38931e3dc6c7224edf925bf6f1840351578bbf9cc进行了少量添加。

![图4.显示comp_id的Drive.exe代码片段](https://images.seebug.org/content/images/2020/12/21/1608521204000-4lbvjy.png-w331s)

图4.显示comp_id的Drive.exe代码片段

![](https://images.seebug.org/content/images/2020/12/21/1608521204000-5guror.png-w331s)

图5.显示comp_id和base64编码的Drive.exe代码片段

### **初始运行**

该恶意软件要做的第一件事是将其复制到启动目录中以保持持久性，使用以下命令通过cmd.exe完成此操作：

move /Y "{malware_location}"
"C:\Users{username}\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup\gdrive.exe"

每次恶意软件使用cmd.exe运行命令时，执行命令的标准输出（STDOUT）都会通过管道传输并以以下文件名格式写入Google云端硬盘帐户：

  * {utcnow} _report_ {受害者的身份证}

![图6.代码片段显示了命令的执行](https://images.seebug.org/content/images/2020/12/21/1608521206000-6gbsmc.png-w331s)

图6.代码片段显示了命令的执行

用于读写攻击者的Google云端硬盘帐户的客户端密钥和令牌已硬编码在恶意软件本身上。

![图7-典当风暴不复杂](https://images.seebug.org/content/images/2020/12/21/1608521207000-7xqcex.png-w331s)

![图7-8。
显示客户端密钥和令牌的代码片段](https://images.seebug.org/content/images/2020/12/21/1608521208000-8ckilv.png-w331s)

图7-8.显示客户端密钥和令牌的代码片段

通过Google云端硬盘发送回信息，黑客可以检查执行该恶意软件的计算机是否是为目标受害者。

### 接收命令和数据泄露

该漫游器每20分钟检查一次Google云端硬盘中的文件。如果存在具有相应文件名格式的文件（cmd_
{受害者的ID}），它将下载该文件并将其内容作为批处理文件运行。

![图9.代码片段显示等待命令](https://images.seebug.org/content/images/2020/12/21/1608521208000-9rbbqi.png-w331s)

图9.代码片段显示等待命令

同样，命令的STDOUT将被写回到Google云端硬盘。以Google云端硬盘作为命令与控制（C＆C）服务器，这可以作为攻击者的反向外壳。从Google云端硬盘收到的命令文件一旦下载，也会被删除。

![图10.显示readFile的代码片段](https://images.seebug.org/content/images/2020/12/21/1608521209000-10kivcq.png-w331s)

图10.显示readFile的代码片段

使用上面提到的“反向外壳”方法，黑客可以使用以下命令来窃取数据/文档：

powershell -command
"[Convert]::ToBase64String([IO.File]::ReadAllBytes('{filename}')

![图11.代码片段显示了数据的渗漏](https://images.seebug.org/content/images/2020/12/21/1608521210000-11aocnd.png-w331s)

图11.代码片段显示了数据的渗漏

具有文件名Google
Drivemonitor.exe（0b94e123f6586967819fa247cdd58779b1120ef93fa1ea1de70dffc898054a09）的辅助负载是键盘记录程序,收集的击键存储在与执行恶意软件相同的目录中。

![图12.显示关键日志的代码片段](https://images.seebug.org/content/images/2020/12/21/1608521210000-12lizel.png-w331s)

图12.显示关键日志的代码片段

此辅助有效负载不具有将收集的击键上传回攻击者的任何功能。但由于主要的恶意软件充当“反向外壳”，因此黑客可以在后期取回收集的击键。最终，黑客对恶意软件进行了改进加密。

## IOCs

IP地址

**IP地址** | **描述** | **有效日期**  
---|---|---  
34.243.239.199([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=34.243.239.199))
| 连接到受感染帐户的电子邮件服务器。IP地址可能已被Pawn Storm破坏。 | 2020年10月29日– 2020年12月8日  
74.208.228.186([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=74.208.228.186))
| 连接到受感染帐户的电子邮件服务器。IP地址可能已被Pawn Storm破坏。 | 2020年10月15日– 2020年12月14日  
193.56.28.25([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=193.56.28.25))
| 扫描TCP端口445和1433 | 2020年5月21日至5月26日  
195.191.235.155([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=195.191.235.155))
| 扫描UDP端口389 | 2020年8月22日  
**SHA256** | **Filename** | **Description** | **Trend Micro Pattern
Detection** | **Trend Micro Machine Learning Detection**  
---|---|---|---|---  
c4a61b581890f575ba0586cf6d7d7d3e0c7603ca40915833d6746326685282b7 | info.exe |
Google Drive RAT | Trojan.MSIL.DRIVEOCEAN.A | Troj.Win32.TRX.XXPE50FSX005  
3fd45b9b33ff5b6363ba0013178572723b0a912deb8235a951aa3f0aa3142509 | info.exe |
Google Drive RAT | Trojan.MSIL.DRIVEOCEAN.A | Troj.Win32.TRX.XXPE50FSX005  
cbd9cb7b69f864ce8bae983ececb7cf8627f9c17fdaba74bd39baa5cdf605f79 | gdrive.exe
| Google Drive RAT | Trojan.MSIL.DRIVEOCEAN.A | Troj.Win32.TRX.XXPE50FFF039  
2060f1e108f5feb5790320c38931e3dc6c7224edf925bf6f1840351578bbf9cc | gdrive.exe
| Google Drive RAT | Trojan.MSIL.DRIVEOCEAN.A | Troj.Win32.TRX.XXPE50FFF039  
f364729450cb91b2a4c4e378c08e555137028c63480a221bb70e7e179a03f5cc | gdrive.exe
| Google Drive RAT | Trojan.MSIL.DRIVEOCEAN.A | N/A  
e3894693eff6a2ae4fa8a8134b846c2acaf5649cd61e71b1139088d97e54236d | info.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FSX005  
83fbd76d298253932aa3e3a9bc48c201fe0b7089f0a7803e68f41792c05c5279 |
decrypt_v2.4.exe | IMAP RAT | Trojan.MSIL.OCEANMAP.A |
Troj.Win32.TRX.XXPE50FSX005  
fe00bd6fba209a347acf296887b10d2574c426fa962b6d4d94c34b384d15f0f1 | email.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
b61e0f68772f3557024325f3a05e4edb940dbbe380af00f3bdaaaeabda308e72 | igmtSX.exe
| IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
c8b6291fc7b6339d545cbfa99256e26de26fff5f928fef5157999d121fe46135 | igmtSX.exe
| IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
50b000a7d61885591ba4ec9df1a0a223dbceb1ac2facafcef3d65c8cbbd64d46 | email.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
3384a9ef3438bf5ec89f268000cc7c83f15e3cdf746d6a93945add300423f756 | email.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
abf0c2538b2f9d38c98b422ea149983ca95819aa6ebdac97eae777ea8ba4ca8c | email.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
faf8db358e5d3dbe2eb9968d8b19f595f45991d938427124161f5ed45ac958d5 | email.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
4c1b8d070885e92d61b72dc9424d9b260046f83daf00d93d3121df9ed669a5f9 | email.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
770206424b8def9f6817991e9a5e88dc5bee0adb54fc7ec470b53c847154c22b | email.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
6fb2facdb906fc647ab96135ce2ca7434476fb4f87c097b83fd1dd4e045d4e47 | email.exe |
IMAP RAT | Trojan.MSIL.OCEANMAP.A | Troj.Win32.TRX.XXPE50FFF039  
31577308ac62fd29d3159118d1f552b28a56a9c039fef1d3337c9700a3773cbf | photos.exe
| IMAP RAT | Trojan.MSIL.OCEANMAP.A | N/A  
661d4a0d877bac9b813769a85c01bce274a77b29ccbd4b71e5b92df3c425b93b | decrypt.exe
| decoy file | N/A | N/A  
0b94e123f6586967819fa247cdd58779b1120ef93fa1ea1de70dffc898054a09 | Google
Drivemonitor.exe | keylogger | TrojanSpy.MSIL.KEYLOGGR.WLDG | N/A  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1434/>

