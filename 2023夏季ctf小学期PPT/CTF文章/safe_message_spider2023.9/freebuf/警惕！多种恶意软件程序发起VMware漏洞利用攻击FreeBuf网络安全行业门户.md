今年4 月，VMware 公布并修补了编号为 CVE-2022-22954
的远程代码执行漏洞。因为缺乏对参数“deviceUdid”和“devicetype”进行有效的清理，该漏洞引入了服务器侧模版的注入攻击的可能性。它允许攻击者注入载荷，并能够在VMware
Workspace ONE Access 和 Identity Manager 组件上进行远程代码执行。FortiGuard
Labs（Fortinet全球威胁情报响应与研究团队）发布了有关CVE-2022-22954漏洞的威胁报告，并在 4 月份针对该漏洞发布了IPS 签名。

4月以来，Fortinet陆续观察到针对此平台的在野攻击事件，但大多数载荷均限于窥探受害者的密码、hosts文件等敏感数据。
**然而近期，一些更加危险的活动引起了Fortinet研究人员的警觉。**
一些特定有效载荷企图攻击运行Linux系统的潜在目标网络设备，试图植入Mirai、RAR1ransom勒索软件，利用合法的WinRaR加密用户数据，并使用xmrig挖矿软件变体GuardMiner挖矿木马对门罗币钱包进行挖矿行为。

本文将为您全面盘点恶意软件如何利用 VMware 漏洞以及漏洞利用后续行为，避免您的资产受到损害。

受影响平台

|

VMware Workspace ONE Access 和 Identity Manager  
  
---|---  
  
受影响群体

|

VMware 用户  
  
影响范围

|

攻击者利用此漏洞发送含有恶意命令的信息，发起命令注入攻击  
  
严重等级

|

高危  
  
![图片](https://image.3001.net/images/20221028/1666920158_635b2ede15b0c1fb43a7b.png!small)

图 1 CVE-2022-22954漏洞活动趋势图

 **Mirai变体**

Mirai 变体的完整载荷如图 2
所示，该字符串将打开临时目录并从http[:]//107[.]189[.]8[.]21/pedalcheta/cutie[.]x86_64链接下载
Mirai
变体，之后使用参数“VMware”执行恶意命令。![图片](https://image.3001.net/images/20221028/1666920200_635b2f0863e2a9bb22fa9.png!small)

图 2 攻击流量捕获

![图片](https://image.3001.net/images/20221028/1666920216_635b2f181cc4f4b7d50dd.png!small)

图 3 已解码的命令

如同多数Mirai僵尸网络一样，该变种的主要手段包括发起DoS拒绝服务和暴力破解攻击。Fortinet利用0x54参数对数据进行XOR解密后，解码了部分配置并发现C2服务器域名为“cnc[.]goodpackets[.]cc”。以下为解码后的字符串：

![图片](https://image.3001.net/images/20221028/1666920232_635b2f280803ac5517017.png!small)

图 4 已解码的配置字符串

Fortinet还使用经编码的帐户和密码字符串识别出暴力破解函数：

![图片](https://image.3001.net/images/20221028/1666920243_635b2f33d38a3a0bbb83f.png!small)

图 5 已识别的暴力破解函数

经Fortinet研究人员解码后还获得了部分密码，其中除了常见密码外，不乏一些知名物联网设备的默认账号。

该Mirai变种执行命令后，将显示硬编码字符串“InfectedNight did its
job”，同时发送参数为“VMware”的心跳信息至C2服务器，随后等待来自C2服务器的下一步命令。下图显示Fortinet捕获的心跳信息和暴力攻击流量会话。

![图片](https://image.3001.net/images/20221028/1666920263_635b2f47349a2e70b259b.png!small)

图 6 心跳信息流量捕获

![图片](https://image.3001.net/images/20221028/1666920283_635b2f5b554d7a655c1fa.png!small)

图 7 已捕获的暴力攻击会话

 **RAR1Ransom 和 GuardMiner初始化脚本**

![图片](https://image.3001.net/images/20221028/1666920300_635b2f6ca00c675906741.png!small)

图 8 针对Windows系统攻击的流量捕获

另一个值得关注的载荷来自字符串67[.]205[.]145[.]142。该载荷包含两个会话，每个会话所涉及的指令随受害者使用的操作系统而异。其中一个针对Windows系统的指令利用
PowerShell 下载脚本文件“init.ps1”，另一个针对Linux系统的指令则利用python
函数库中的curl、wget和urlopen指令下载脚本文件“init.sh”。

![图片](https://image.3001.net/images/20221028/1666920311_635b2f7741cd858384ff4.png!small)

图 9 针对Linux 系统攻击的流量捕获

在PowerShell 脚本文件“init.ps1”中，包含了一些指向 cloudflare-ipfs[.]com的链接，以用于下一步攻击，每个文件都有连接至crustwebsites[.]net. 的特定备份连接。

![图片](https://image.3001.net/images/20221028/1666920322_635b2f82bfded4e2091a9.png!small)

图 10 init.ps1 中的下载链接

用于初始化的7 个文件：

  * phpupdate.exe：Xmrig门罗币挖矿软件

  * config.json：矿池配置文件

  * networkmanager.exe：用于扫描和传播感染的可执行文件

  * phpguard.exe：用于保护Xmrig挖矿软件持续运行的可执行文件

  * init.ps1：通过创建计划任务实现持续性攻击的脚本文件

  * clean.bat：用于删除受感染主机中其他加密挖矿软件的脚本文件

  * encrypt.exe：RAR1 勒索软件

![图片](https://image.3001.net/images/20221028/1666920336_635b2f90338104488caa5.png!small)

图 11 init.ps1 中的“start encrypt”指令部分

如图 11 所示，在“start encrypt”指令中，攻击者在启动 RAR1ransom
前，会预先检查“flag_encrypt.flag”，如果检测到 flag
文件存在并且之前已下载“encrypt.exe”，则删除“encrypt.exe”，而后进入下一攻击阶段。否则，该指令将检查文件大小以确定是否更新文件路径。检查结束后即执行勒索软件攻击。

随后，脚本开始启动GuardMiner攻击。GuardMiner是一款跨平台挖矿木马程序，自2020年以来一直处于活跃状态。FortiGuard
Labs已发布有关该挖矿木马的详细报告。GuardMiner针对Linux系统发起的攻击，会自动下载脚本文件“init.sh”。

![图片](https://image.3001.net/images/20221028/1666920350_635b2f9e73f000d5b70f1.png!small)

图 12 针对 Linux 系统的脚本文件“init.sh”

Fortinet还注意到，GuardMiner
利用近期曝出的漏洞更新了“networkmanager.exe”。通过观察每个漏洞利用模块名称，Fortinet发现出于安全测试目的，GuardMiner可能会从Chaitin
Tech Github收集漏洞利用列表。

![图片](https://image.3001.net/images/20221028/1666920365_635b2fad0d807daf9c634.png!small)

图 13 rdata 部分包含的networkmanager.exe漏洞列表

以下为Fortinet获取的完整漏洞列表：

![图片](https://image.3001.net/images/20221028/1666920374_635b2fb66170f51121b95.png!small)

 **RAR1Ransom**

RAR1ransom通过利用C:/Windows/Temp folder中的合法WinRaR软件“rar.exe”，使用密码压缩受害者文件，并同时使用
WinRaR 中的多个默认选项完成加密操作以提高效率，如图 14所示，从进程资源管理器中能够找到这些进程。

![图片](https://image.3001.net/images/20221028/1666920386_635b2fc21a63a91f2f2f5.png!small)

图 14 RAR1Ransom勒索软件加密文件进程

整个命令如下所示，选项“df”和“m0”表示将文件添加至存档后不进行压缩并直接删除，“mt10”表示将使用十个线程加载，“ep”表示从文件名称中删除路径，“hp”表示使用密码加密文件数据和文件名。![图片](https://image.3001.net/images/20221028/1666920395_635b2fcb430c43f9681c2.png!small)

如图 15 所示，以下为受RAR1Ransom 攻击且具有特定扩展名的受感染文件。

![图片](https://image.3001.net/images/20221028/1666920405_635b2fd59178ce87f2fce.png!small)

图 15 目标文件扩展名

RAR1Ransom 为所有加密文件均分配了唯一的文件名和“.rar1”扩展名，并将附有图 17
所示勒索信息的文本文件“READ_TO_DECRYPT.txt”与加密文件置于同一文件夹中发送给受害者。

![图片](https://image.3001.net/images/20221028/1666920415_635b2fdf60a0fa2a27569.png!small)

图 16
加密文件![图片](https://image.3001.net/images/20221028/1666920426_635b2fea6840c9fb1bde0.png!small)

图17 勒索信内容

从图 17 勒索信中的钱包字符串可以看出，该字符串与图 18 中 GuardMiner
挖矿木马配置信息中的“user”字符串相同。由此可见，攻击者计划充分地利用受害者资源，不仅安装了RAR1Ransom勒索软件进行敲诈勒索，还植入了GuardMiner木马挖掘和收集加密货币。![图片](https://image.3001.net/images/20221028/1666920435_635b2ff36d7fb5f99586b.png!small)

图18 GuardMiner 配置信息”config.json”

 **结论**

尽管早在4月份，VMware官方已发布针对高危漏洞CVE-2022-22954的修复补丁，但截至目前仍有多个恶意软件程序企图利用该漏洞发起攻击。Fortinet
呼吁用户尽快安装最新版VMware软件，积极修复系统漏洞，并时刻警惕本地网络环境中的任何可疑进程。虽然这些Mirai变种、RAR1Ransom勒索软件以及GuardMiner木马程序并非非常复杂的威胁样本，但其采用的战术和方法始终不断变化和演进，广大用户依然不可掉以轻心。FortiGuard
Labs将持续检测此类漏洞攻击活动并为您提供前沿资讯。

