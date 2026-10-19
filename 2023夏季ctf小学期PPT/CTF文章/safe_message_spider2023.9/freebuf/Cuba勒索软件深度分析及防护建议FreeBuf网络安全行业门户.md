> **从2022年5月上旬开始，Unit
> 42观察到攻击者使用新工具和技术部署Cuba勒索软件。使用Unit42的命名模式，他们将Cuba勒索软件命名为Tropical Scorpius。**

##  **0** **1.** **Cuba勒索软件的部署方式**

Cuba勒索软件家族于2019年12月首次浮出水面。此后，该勒索软件家族背后的攻击者改变了策略和工具，成为2022年成为更普遍的威胁。该勒索软件历来通过Hancitor分发，通常通过恶意附件传递。

Hancitor也被称为Chanitor或Tordal，是一个基于宏的恶意软件，通过分布在垃圾电子邮件活动中的Microsoft
Office文档传播。安全研究员还观察到Tropical Scorpius利用Microsoft Exchange
Server中的漏洞，包括ProxyShell和 ProxyLogon。

该勒索软件组织使用双重勒索和一个泄露站点，该网站暴露了据称已被入侵的组织（图1a
和1b）。也就是说，该组织在2019年首次观察时没有泄漏站点，安全研究员怀疑这个灵感来自于其他勒索软件组，例如Maze和REvil。Cuba
Ransomware泄漏站点还包括一个付费部分，攻击者分享出售给感兴趣方的泄漏。

![图片1.png](https://image.3001.net/images/20221206/1670295085_638eae2d12df73df42d3d.png!small)

图1. Cuba Ransomware 使用的泄漏站点的屏幕截图，重点关注该组织免费提供的内容

![图片2.png](https://image.3001.net/images/20221206/1670295086_638eae2eb1b866ccd6b02.png!small)

图2. 古巴勒索软件集团泄露网站部分的屏幕截图，其中提供数据出售

##  **0** **2.** **Tropical Scorpius 受害者分析**

最新的 Unit 42 勒索软件威胁报告包括对 Cuba 勒索软件影响 33 个组织的观察。截至 2022 年 7 月，Tropical Scorpius
已使用 Cuba Ransomware 影响了多个领域的 27
个其他组织，例如专业和法律服务、州和地方政府、制造、运输和物流、批发和零售、房地产、金融服务、医疗保健、高科技、公用事业和能源、建筑和教育。自该组织于
2019 年首次浮出水面以来，该勒索软件团伙在其泄密网站上总共暴露了 60 个组织。

安全研究员怀疑受害者的数量比泄漏网站显示的还要更多，因为如果受害者支付赎金，勒索软件运营商通常不会公开发布数据。尽管如此，联邦调查局表示，古巴勒索软件团伙从赎金中赚取了至少
4390 万美元，并要求至少 7400
万美元。![图片3.png](https://image.3001.net/images/20221206/1670295088_638eae3036cdff0b84199.png!small)

图 3. 古巴勒索软件泄露网站上出现的组织，按行业分布

安全研究员观察到，这个勒索软件团伙的泄密站点并不像其他勒索软件团伙那样在全球范围内分布目标组织。虽然泄密站点并不能反映受此勒索软件组织影响的实际受害者数量，但它们仍让我们大致了解该组织的目标和目的。我们注意到，在古巴勒索软件泄漏网站上列出的
60 名受害者中，有 40 名位于美国——占涉嫌违规组织总数的 66%。相比之下，在 LockBit 泄漏网站上，据称被破坏的组织中只有约 30%
位于美国。

##  **0** **3.** **工业间谍和 Tropical Scorpius**

2022 年 5 月，BleepingComputer 报道称“工业间谍”市场正在进入勒索软件业务。在 2022 年 4
月出现后，“工业间谍”成为一个众所周知的网站，攻击者可以在该网站上注册，从被入侵的公司购买被窃取的数据。勒索软件的扩展虽然是一种相关类型的恶意活动，但似乎也与
Tropical Scorpius 有关。

![图片4.png](https://image.3001.net/images/20221206/1670295088_638eae30a3ab4587d28e5.png!small)

图 4. 工业间谍登录页面

BleepingComputer 报告称，工业间谍勒索软件使用的赎金票据与 Cuba
赎金票据非常相似，两份票据都包含完全相同的联系信息。值得一提的是，勒索软件团体通常会复制其他团体的勒索记录作为自己的样本，但安全研究员认为这种关系还有更多。

Unit 42 观察到一个 Cuba Ransomware 有效载荷用于加密受感染系统上的文件，将 .cuba
扩展名附加到文件中，但随后观察到泄露的数据已在“工业间谍”市场上发布出售。Unit 42 仍然不确定为什么 Tropical Scorpius
攻击者决定利用“工业间谍”市场而不是他们自己的泄密站点；然而，由于 BleepingComputer
发布的调查结果和这一奇怪的事件，他们认为两者之间的参与程度比最初想象的要多。

##  **0** **4.** **勒索软件功能**

虽然很明显 Tropical Scorpius 攻击者不断开发和更新他们的工具包，但 Cuba 勒索软件的核心有效载荷自 2019
年被发现以来基本保持不变。加密算法仍取自 WolfSSL 的开源存储库，特别是用于文件加密的 ChaCha 和 RSA 用来密钥加密。

![图片5.png](https://image.3001.net/images/20221206/1670295089_638eae313ec610429d6ee.png!small)

图 5. Cuba Ransomware 和WolfSSL 的 RSA 加密功能之间的代码重叠

与大多数勒索软件家族类似，Cuba Ransomware 根据文件大小对文件进行不同的加密。如果文件长度小于 0x200000
字节，则对整个文件进行加密。如果没有，Cuba Ransomware 会以 0x100000
字节的块对文件进行加密，加密块之间的中断根据整体大小而有所不同。例如，大小在 0x200000 字节和 0xA00000 字节之间的文件将被修改为
0x400000 字节的块，直到文件结束。

![图片6.png](https://image.3001.net/images/20221206/1670295089_638eae31c4924021cb725.png!small)

图 6. 在文件加密之前确定块间距

![Dingtalk_20221205095701.jpg](https://image.3001.net/images/20221206/1670295090_638eae3256eda1e186fc6.jpg!small)

表 1. Cuba Ransomware 中基于文件大小的块间距

每个加密文件还带有一个初始的 1024 字节标头，其中包含 magic 值 FIDEL.CA（可能是指 Fidel Castro，遵循 Cuba
主题），然后是包含文件特定 ChaCha 密钥的 RSA-4096 加密块和随机数。成功加密文件后，扩展名 .cuba 会附加到文件名中。

![图片7.png](https://image.3001.net/images/20221206/1670295091_638eae33131a4e76554c6.png!small)

图 7. FIDEL.CA 魔术值后跟加密的RSA blob

正如趋势科技所讨论的那样，Cuba Ransomware 的开发人员已经建立了将在运行时终止的目标进程和服务列表，并增加了目录和扩展名的数量以避免加密。

 **目标进程和服务：**

MySQL

MySQL82SQLSERVERAGENT

MSSQLSERVER

SQLWriter

SQLTELEMETRY

MSDTC

SQLBrowser

sqlagent.exe

sqlservr.exe

sqlwriter.exe

sqlceip.exe

msdtc.exe

sqlbrowser.exe

vmcompute

vmms

vmwp.exe

vmsp.exe

outlook.exe

MSExchangeUMCR

MSExchangeUM

MSExchangeTransportLogSearch

MSExchangeTransport

MSExchangeThrottling

MSExchangeSubmission

MSExchangeServiceHost

MSExchangeRPC

MSExchangeRepl

MSExchangePOP3BE

MSExchangePop3

MSExchangeNotificationsBroker

MSExchangeMailboxReplication

MSExchangeMailboxAssistants

MSExchangeIS

MSExchangeIMAP4BE

MSExchangeImap4

MSExchangeHMRecovery

MSExchangeHM

MSExchangeFrontEndTransport

MSExchangeFastSearch

MSExchangeEdgeSync

MSExchangeDiagnostics

MSExchangeDelivery

MSExchangeDagMgmt

MSExchangeCompliance

MSExchangeAntispamUpdate

Microsoft.Exchange.Store.Worker.exe

 **避免加密的目录：**

\windows

\program files\microsoft office

\program files (x86)\microsoft office

\program files\avs

\program files (x86)\avs

\$recycle.bin

\boot

\recovery

\系统卷信息

\msocache

\users\所有用户

\users\默认用户

\users\default

\temp

\inetcache

\google\

 **避免加密的扩展：**

.exe

.dll

.sys

.ini

.lnk

.vbm

.cuba

另一个重大更新可以在勒索软件释放的勒索信中找到，它们不仅依赖于它们的 Tor 站点，还通过 TOX
提供通信，由于其安全的消息传递功能，它在勒索软件组中慢慢变得越来越流行。

![图片8.png](https://image.3001.net/images/20221206/1670295092_638eae3405efb1b30bd75.png!small)

图 8. Cuba Ransomware 组织丢弃的赎金票据

 **防御规避**

Unit 42观察到攻击者在部署勒索软件Tropical Scorpius之前使用一些有趣的工具和技术来逃避检测并在受感染的环境中四处走动。Tropical
Scorpius 利用一个释放器将内核驱动程序写入名为 ApcHelper.sys 的文件系统，这针对并终止了安全产品。dropper
没有签名，但是，内核驱动程序是使用在 LAPSUS NVIDIA 泄漏中找到的证书进行签名的。

![图片9.png](https://image.3001.net/images/20221206/1670295092_638eae34f3ac86ffe1cf9.png!small)

图 9. 内核驱动程序数字签名

在执行内核驱动程序 dropper/loader 时，内核 dropper 使用多个 Windows API 来查找资源部分并加载名为 Driver
的资源类型名称。这是一个嵌入式 PE 文件，并且是最终将在后续 API 调用中写入文件系统的驱动程序。

![图片10.png](https://image.3001.net/images/20221206/1670295093_638eae357cdfe653c0955.png!small)

图 10. 内核释放器资源部分

内核驱动程序放入文件系统后，加载程序将首先通过 cmd.exe 为文件路径运行删除命令参数。

![图片11.png](https://image.3001.net/images/20221206/1670295094_638eae3624611d06f2e0e.png!small)

之后，它将使用 cmd.exe 创建一个新服务并运行以下参数为内核驱动程序设置一个服务。

![图片12.png](https://image.3001.net/images/20221206/1670295094_638eae3687d4307635cae.png!small)

然后加载程序将负责终止安全产品的内核驱动程序复制到文件系统上。

![图片13.png](https://image.3001.net/images/20221206/1670295094_638eae36eae8b99d6dd3f.png!small)

释放和加载的内核驱动程序的核心功能是解析额外的内核 API 以执行功能并针对要终止的安全产品列表。

附加API使用所需API名称的字符串常量解析，下面的每个Windows API都用于：

对MmGetSystemRoutineAddress的函数调用，以返回指向该函数的指针。

下面是在示例中找到的已解决的其他内核 API 的列表。

![图片14.png](https://image.3001.net/images/20221206/1670295095_638eae3759b13d1b42e7f.png!small)

图 11. 内核驱动程序运行时 API

目标安全产品列表与之前在名为 “BURNTCIGAR” 的工具中观察到的目标列表重叠。这个特定的内核驱动程序是 Mandiant 观察到的变体。

![图片15.png](https://image.3001.net/images/20221206/1670295095_638eae37c20e33251fce8.png!small)

图 12. 目标安全产品

解决附加API后，开始针对安全产品的流程（针对的产品在上面的图 12 中）。设置一个do-while循环（循环如下图 13
所示），目的是检查系统上运行的进程，以查看它们是否与目标安全产品中的项目匹配。

通过查找每个ThreadID并调用函数

PsLookupThreadByThreadId来执行此命名检查。

该函数将用于查找指向线程的ETHREA结构的指针。ETHREAD结构是一个内核对象，维护对重要进程/线程结构和对象的各种引用，这些引用是操作系统为CPU分配任务和执行所需的。返回的指向ETHREAD的指针在函数中使用PsIsThreadTerminating以确保线程没有终止。

然后如果存在线程对象，为了找到该线程所属的进程，使用函数PsGetThreadProcess，返回值为PEPROCESS。PEPROCESS是进程对象的内核对象表示，它维护指向存储进程相关信息的位置的指针。如果关联线程确实存在PEPROCESS，则ImageFileName偏移量将分配给反编译输出实例中的变量，这是图13中名为“v3”的变量。变量“v3”将具有循环中当前线程/进程的进程映像文件名，它可以是计算机系统上的任何活动进程。

接下来执行名称检查的是在strstr函数中使用两个参数的内部if-then语句。第一个参数是来自PEPROCESS结构的ImageFileName的进程映像文件名。第二个参数是安全产品名称的子字符串搜索，以便与第一个参数进行比较。（例如，名称Sophos是否存在于
ImageFileName进程名称字符串中？）

如果匹配，则下一个名为sub_140001BE0的函数将检查线程的状态代码是否设置为status pending挂起状态。如果评估结果为真，则将使用
ZwTerminateProcess 调用子例程以终止。线程对象将被取消引用，循环将继续到下一个线程以再次开始评估以终止。

![图片16.png](https://image.3001.net/images/20221206/1670295096_638eae3835a8bd3f4b2ac.png!small)

图 13. 反编译内核驱动程序示例

Tropical Scorpius 的策略改变是利用过期的合法 NVIDIA 证书，以及使用它们自己的驱动程序针对安全产品进行终止。与先前版本的易受攻击的
BURNTCIGAR 驱动程序中公开观察到的对未记录 IOCTL（输入/输出控制系统调用）的利用相比，这是一个值得注意的变化。

##  **0** **5.** **本地权限提升**

Tropical Scorpius 利用的本地权限提升工具最初是使用 PowerShell 的 Invoke-WebRequest 从网络托管平台
tmpfiles[.]org下载的。

Unit 42 观察到攻击者利用了一个滥用 CVE-2022-24521 的二进制文件，这是通用日志文件系统 (CLFS)
中的一个漏洞。该漏洞利用了CLFS.sys中的一个逻辑错误，特别是在 CClfsBaseFilePersisted::LoadContainerQ()
函数中。格式错误的 BLF 文件用于破坏具有用户模式地址的容器上下文对象的 pContainer
字段，以获取代码执行。代码执行用于窃取系统令牌并提升权限。PixiePoint Security 的 Sergey Kornienko 于 2022 年 4
月 25 日提供了有关此漏洞和利用策略的详细记录。

Tropical Scorpius 威胁攻击者可能使用这篇文章作为构建漏洞利用的指南，因为使用的利用策略与 Sergey
描述的相同，包括用于喷射堆的管道属性堆利用方法。

##  **0** **6.** **横向传播**

Tropical Scorpius 威胁参与者利用各种工具进行初始系统侦察。ADFind 和 Net Scan 是使用 PowerShell 的
Invoke-WebRequest 从网络托管平台tmpfiles[.]org下载的。这两种工具都被放到同一个系统上，并使用缩短的名称，以掩盖它们的用途。

使用基于 PowerShell 的脚本 GetUserSPNs.ps1
执行低权限系统上的凭证准备和收集。在三个不同的系统上观察到这个特定的脚本，它识别出被用作服务帐户的用户帐户。攻击者使用此过程来确定值得针对其关联的
Active Directory Kerberos 票证的帐户，以便通过称为 Kerberoasting 的技术离线收集和破解 Kerberos 票证。

在使用 GetUserSPNs.ps1 大约一周后，观察到与凭据盗窃相关的其他活动，用户工作站上的 Mimikatz
被作为压缩文件写入用户的文档文件夹。Mimikatz 是一个著名的凭据盗窃工具，它包含各种选项，用于针对可能找到凭据的操作系统部分。

大约在观察到 Mimikatz 的时候，在另一个工作站上观察到了一个自定义的黑客工具。该工具旨在从主机的 LSASS内存中提取缓存的 Kerberos
票证，以被放入用户的文档文件夹中。

Unit 42 根据其总体目标来命名Tropical Scorpius使用的Kerberos工具：

KerberCache。截取了工具输出的屏幕截图，显示了工具生成的解析数据。

![图片17.png](https://image.3001.net/images/20221206/1670295096_638eae38b507cbfedb130.png!small)

图 14. KerberCache 票证提取示例

KerberCache将调用API LsaConnectUntrusted

以获取用于后续调用的句柄。在返回的句柄之后，

对LsaLookupAuthenticationPackage的调用将被赋予名为Kerberos的包，以及来自

先前对LsaConnectUntrusted的API调用的句柄。

若成功，它将调用LsaCallAuthenticationPackage。

下图是函数流的片段，一旦被调用，就会发生反编译的格式化和解析。

![图片18.png](https://image.3001.net/images/20221206/1670295097_638eae391feb12fbf49bf.png!small)

图 15. 票证解析反编译示例

成功检索缓存的 Kerberos 票证后，票证将被传递给对数据进行 base64
编码的函数，并将写入执行该工具的当前工作目录。该工具的命名约定输出可以分为以下部分：

[user@servername]_[encryption_type].[ticket_number].kirbi。

写入文件系统时，实际票证命名约定显示为以下示例输出：

krbtgt@CORP.INTERNAL_18.0.kirbi。

![图片19.png](https://image.3001.net/images/20221206/1670295097_638eae39b5ebb4360da4a.png!small)

图 16. 票证编码反编译示例

##  **0** **7.** **域管理**

Tropical Scorpius 使用的域管理工具最初是使用 PowerShell 的Invoke-WebRequest 从网络托管平台
tmpfiles[.]org 下载的。该样本是使用 Themida 的 Anti-VM 功能打包的，Themida
是一种著名的商业打包工具。它还伪装成文件名 Filezilla。

执行时，如果在虚拟化环境中运行，打包程序将显示以下消息：

![图片20.png](https://image.3001.net/images/20221206/1670295098_638eae3a6ef79d326673b.png!small)

图 17. Themida Anti-VM 示例

与黑客工具相关的独特命令提供了高可信度的 Zero.exe 是 ZeroLogon 黑客工具。ZeroLogon 黑客工具用于滥用
CVE-2020-1472，通过从域控制器请求 NTLM 哈希来获得域管理员 (DA) 权限。

![图片21.png](https://image.3001.net/images/20221206/1670295099_638eae3b2fa87e70a0ea2.png!small)

图 18. ZeroLogon hacktool 打包示例

公开指出，ZeroLogon 黑客工具已在其他恶意软件家族中广受欢迎，作为其在犯罪软件领域的攻击链的一部分，与Qbot 和 Hancitor
相关的入侵重叠。

##  **0** **8.** **命令与控制**

除了上述工具外，Unit 42 还发现了一个自定义远程访问木马/后门，其中包含独特的命令和控制 (C2)
协议。基于二进制文件中的字符串以及功能，他们选择将其命名为 ROMCOM RAT。

ROMCOM RAT 可以通过使用它的两个导出之一来执行：ServiceMain、startWorker。

两个导出都导致执行相同的功能，但是，不同之处在于作为参数传递的字符串：ServiceMain传递字符串 _inet，而 startWorker 传递字符串
_file。仅基于这个字符串，样本中的执行流程就完全不同了，ServiceMain 导致样本向其 C2 服务器发送信标，而 startWorker
导致样本在系统上打开后门并等待连接。

ServiceMain 导出

执行 ServiceMain 导出后，ROMCOM 将执行以下命令行：

C:\Windows\System32\rundll32.exe

C:\Windows\System32\comDll.dll,startWorker

这将导致 startWorker 导出的执行，这意味着两个导出都将在机器上处于活动状态，假设 ROMCOM 最初是通过服务执行的。

![图片22.png](https://image.3001.net/images/20221206/1670295099_638eae3bd7c06bdaec909.png!small)

图 19. 通过带有startWorker参数的rundll32.exe执行ROMCOM示例

从那里，ROMCOM 将收集系统和用户信息，并尝试通过 WinHTTP API 将其发送到硬编码的 C2 服务器。如果成功，则相应地解析和处理响应。

![图片23.png](https://image.3001.net/images/20221206/1670295100_638eae3cb4312f7abd4b8.png!small)

图 20. ROMCOM 中提供的ICMP功能

![图片24.png](https://image.3001.net/images/20221206/1670295101_638eae3d55b64900b42c9.png!small)

图 21. 从C2接收的数据包的命令处理

如果连接失败，ROMCOM 会尝试使用 ICMP 请求连接到 C2 服务器并与之通信。使用 IcmpCreateFile() 和
IcmpSendEcho() 等 Windows API 函数，它将尝试将系统和用户信息重新发送到服务器，直到收到响应。一旦收到响应，就会以与解析 HTTP
响应相同的方式对其进行解析。

![图片25.png](https://image.3001.net/images/20221206/1670295101_638eae3de5ea10fccfed1.png!small)

图 22. ICMP请求功能

如果响应的第四个字节等于9，ROMCOM将休眠12000毫秒。如果第四个字节设置为5，则响应将包含后续数据的大小，因此在向C2发出第二个请求之前分配内存，根据使用的最后一个协议使用HTTP或ICMP。

然后将第二个请求中接收到的数据传递给一个函数，该函数首先通过5555和5600之间的端口连接到本地地址127.0.0[.]3，然后发送C2接收到的数据。然后该函数返回，然后
ROMCOM绑定到127.0.0[.]2:5555，它将等待连接并将从该连接接收到的任何数据转发到其C2服务器。

![图片26.png](https://image.3001.net/images/20221206/1670295102_638eae3e724ffac28e2f8.png!small)

图 23.连接到由ROMCOM startWorker 进程托管的本地套接字服务器

这很好地引出了关于 startWorker 导出的讨论。

 **startWorker导出**

startWorker导出将字符串
_file传递给ROMCOM的main函数，这导致ServiceMain导出执行的代码被跳过。相反，startWorker首先打开一个套接字对象并尝试绑定到
IP 127.0.0[.]3 和端口
5555。但是，如果端口已在使用中，ROMCOM将增加端口值并尝试绑定一次再次。这个循环一直持续到ROMCOM绑定到一个未使用的端口，或者直到端口值达到5600，此时它被设置为5554并且循环重新开始。

![图片27.png](https://image.3001.net/images/20221206/1670295103_638eae3f4ce7211798042.png!small)

图 24. 设置本地套接字服务器

一旦 ROMCOM 成功绑定到一个端口，它就会开始监听传入的连接——这将由执行 ServiceMain
导出的进程来完成。当接收到传入连接时，将产生一个线程来处理来自已连接客户端的任何请求。

![图片28.png](https://image.3001.net/images/20221206/1670295104_638eae4001bb8aaf3713d.png!small)

图 25. 命令处理程序

可以在下面看到表 2，其中包含接受的命令列表及其用途：

![Dingtalk_20221205103801.jpg](https://image.3001.net/images/20221206/1670295104_638eae40900f6ec8d8724.jpg!small)

表 2. 支持的后门命令及其功能

本质上，这种特定的执行结构导致 ROMCOM 样本作为服务运行，通过 HTTP/ICMP 请求接收命令，然后将这些命令传递给通过 rundll32.exe
执行的 ROMCOM 样本。执行命令，并将结果传递回服务执行的 ROMCOM 有效负载。最后，通过 HTTP 或 ICMP 请求将结果发布到 C2 服务器。

 **ROMCOM 2.0**

ROMCOM似乎正在积极开发中，因为能够在 2022 年 6 月 20 日发现上传到 VirusTotal (VT) 的类似样本，该样本正在与同一 C2
服务器通信。

原始样本的日期为 2022 年 4 月 10 日，而此样本的文件头时间戳为 2022 年 5 月 28 日，大约大 400 kb。它共享相同的
startWorker 和 ServiceMain 导出；但是，它还包含称为 startInet
的第三个导出。重要的是要注意在样本中发现的调试字符串的增加，这可能表明该样本在开发完成之前被防病毒软件捕获；VT 上传者 ID ( 22b3c7b0
)进一步支持了这一理论，该 ID过去上传了数百万个文件，这排除了任何人自己上传文件的可能性。

在此版本中，ServiceMain 将执行 ROMCOM 2.0 示例两次，首先执行 startInet 导出，然后继续执行 startWorker
导出。然而，开发人员并没有像最初的 ROMCOM 示例那样简单地调用 CreateProcessA ，而是更加关注使用 COM 对象来执行。

![图片29.png](https://image.3001.net/images/20221206/1670295105_638eae412adae4a37c803.png!small)

图 26. startInet 和startWorker 导出的执行

使用任务调度程序提供的各种 COM 接口，每个进程都作为系统上的任务生成。ROMCOM 2.0 将首先通过调用
ITaskService->GetFolder 获取任务根文件夹。然后它会删除与将使用ITaskFolder->DeleteTask
创建的任务同名的任何现有任务。

![Dingtalk_20221205104125.jpg](https://image.3001.net/images/20221206/1670295105_638eae4193f736db47751.jpg!small)

表 3. 通过任务计划程序COM接口注册的任务名称

使用ITaskService->NewTask创建一个空任务使用 IPrincipal->put_Id
修改安全主体以将标识符设置为NTAUTHORITY\SYSTEM使用 IPrincipal->LogonType
将登录类型设置为TASK_LOGON_INTERACTIVE_TOKEN并使用IPrincipal->put_RunLevel将运行级别设置为
TASK_RUNLEVEL_HIGHEST。

![图片30.png](https://image.3001.net/images/20221206/1670295106_638eae4210d30adebed21.png!small)

图 27. 使用SYSTEM 权限创建任务

使用 IRegistrationTrigger->PutDelay 为任务设置 0 秒的延迟，由字符串 PT0S 指示，从而导致任务在创建后立即执行。

![图片31.png](https://image.3001.net/images/20221206/1670295106_638eae42a955fecbc9602.png!small)

图 28. 创建任务触发器，延迟设置为0秒

最后，为任务设置一个动作，动作路径设置为rundll32.exe，参数设置为

C:\Windows\system32\mskms.dll,ARGUMENT

其中ARGUMENT是startWorker或startInet，具体取决于出口通过。

![图片32.png](https://image.3001.net/images/20221206/1670295107_638eae433ec5a1989b667.png!small)

图 29. 创建任务操作，导致rundll32.exe 执行 mskms.dll

注册后，将触发任务，从而执行ROMCOM 2.0主要功能。这遵循与原始示例相同的结构，startInet
进程到达硬编码的C2服务器并将任何响应传递给startWorker进程以进行相应处理。开发人员还扩展了已处理命令的列表，在现有10个命令的基础上再增加10
个。其中包括下载专门设计用于对系统进行单个或多个屏幕截图的有效负载，以及提取所有已安装程序的列表以发送回C2。

（参见图 30 中所示的SCREENSHOOTER字符串参考）。

![图片33.png](https://image.3001.net/images/20221206/1670295107_638eae43ba844735f8ae9.png!small)

图 30. 下载所描述的SCREENSHOOTER 有效负载

![Dingtalk_20221205104211.jpg](https://image.3001.net/images/20221206/1670295108_638eae443b26eb5bd94c0.jpg!small)

表 4. ROMCOM 2.0支持的命令

##  **0** **9.** **勒索软件受害企业经常存在的问题**

（1）厂商为了方便调试及远程维护，接入较多无线网卡；

（2）现场终端机使用U盘很频繁，对U盘使用没有管控措施；

（3）生产网络与办公网络之间没有隔离防护措施；

（4）服务器和终端机登录密码过于简单，容易被暴力破解；

（5）对告警消息未及时响应处置。

