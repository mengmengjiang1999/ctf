**译者：知道创宇404实验室翻译组  
原文链接：<https://www.trendmicro.com/en_us/research/21/k/Squirrelwaffle-Exploits-ProxyShell-and-ProxyLogon-to-Hijack-Email-Chains.html>**

Squirrelwaffle的常规操作是发送恶意垃圾邮件回复现有电子邮件链，今天我们要调查它利用 Microsoft Exchange Server
漏洞（ProxyLogon 和 ProxyShell）的策略。

9月，Squirrelwaffle
作为一种新的加载器出现，并通过垃圾邮件攻击传播。它向已存在的电子邮件链回复恶意邮件，这种策略可以降低受害者对恶意行为的防范能力。为了实现这一点，我们认为它使用了
ProxyLogon 和 ProxyShell 的开发链。

Trend Micro 应急响应团队调查了发生在中东的几起与 Squirrelwaffle
有关的入侵事件。我们对这些攻击的最初访问做了更深入的调查，看看这些攻击是否涉及上述漏洞。

我们发现的所有入侵都来自于内部微软 Exchange 服务器，这些服务器似乎很容易受到 ProxyLogon 和 ProxyShell
的攻击。在这篇博客中，我们将对这些观察到的初始访问技术和 Squirrelwaffle 攻击的早期阶段进行更多的阐述。

## 微软 Exchange 感染

我们在其中三台 Exchange 服务器上的 IIS 日志中发现了利用 CVE-2021-26855、 cve-2021-34473和
cve-2021-34523漏洞，这些漏洞在不同的入侵行为中被攻破。在 ProxyLogon (CVE-2021-26855)和 ProxyShell
(cve-2021-34473和 CVE-2021-34523)入侵中使用了同样的CVEs。微软在三月份发布了一个 ProxyLogon 的补丁;
那些在五月或七月更新的用户就不会受 ProxyShell 漏洞的影响。

### CVE-2021-26855: 预认证代理漏洞

这个服务器端请求伪造(SSRF)漏洞可以通过向 exchangeserver 发送特制的 web 请求来允许黑客访问。Web 请求包含一个直接针对
exchangeweb 服务(EWS) API 端点的 XML 有效负载。

该请求使用特制的 cookie 绕过身份验证，并允许未经身份验证的黑客执行 XML 有效负载中编码的 EWS 请求，然后最终对受害者的邮箱执行操作。

从我们对 IIS 日志的分析中，我们发现攻击者在其攻击中使用了一个公开可用的漏洞。这个漏洞给了攻击者获取用户 SID
和电子邮件的机会。他们甚至可以搜索和下载受害者的邮件。图1到图3突出显示了 IIS 日志中的证据，并显示了漏洞代码。

![Figure 1. Exploiting CVE-2021-26855, as seen in the IIS
logs](https://images.seebug.org/content/images/2021/11/26/1637893121000-1yludc.png-w331s)
图1. 利用 CVE-2021-26855漏洞，如 IIS 日志所示

日志(图2到图3)还显示，攻击者使用 ProxyLogon 漏洞获取这个特定用户的 SID 和电子邮件，使用它们发送恶意垃圾邮件。

![Figure 2. The function responsible for getting the SID inside the
exploit](https://images.seebug.org/content/images/2021/11/26/1637893121000-2rsdxe.png-w331s)
图2.负责获取利用内部 SID 的函数

![Figure 3. The user agent used in the
attack](https://images.seebug.org/content/images/2021/11/26/1637893122000-3knlcp.png-w331s)
图3. 攻击中使用的用户代理

### CVE-2021-34473: 预授权路径混乱

这个 ProxyShell 漏洞滥用了显式登录 URL 的 URL 规范化，如果后缀是
`autodiscover/autodiscover.json`，则从 URL 中删除登录电子邮件。任意后端 URL都能获得 与Exchange
计算机帐户(NT AUTHORITY\SYSTEM)相同的访问权限。

![Figure 4. Exploiting
CVE-2021-34473](https://images.seebug.org/content/images/2021/11/26/1637893123000-4nawqk.png-w331s)
图4. 利用漏洞 CVE-2021-34473

### CVE-2021-34523: Exchange PowerShell 后端标高特权

Exchange 有一个 PowerShell 远程处理功能，可用于读取和发送电子邮件。由于没有邮箱，NT
权限系统不能使用它。但是，如果通过以前的漏洞直接访问后端或PowerShell，则可以为后端或PowerShell 提供 X-Rps-CAT
查询字符串参数。后端或PowerShell 将被反序列化，并用于恢复用户身份。因此，可以使用它模拟本地管理员来运行 PowerShell 命令。

![Exploiting CVE-2021-34523
](https://images.seebug.org/content/images/2021/11/26/1637893123000-5nzzxy.png-w331s)
图5. 利用漏洞CVE-2021-34523

![malicious spam received by targets
](https://images.seebug.org/content/images/2021/11/26/1637893124000-6gjadb.png-w331s)
图6. 目标接收到的恶意垃圾邮件

有了这个，攻击者将能够劫持合法的电子邮件链，并发送他们的恶意垃圾邮件作为对上述链的回复。

## 恶意垃圾邮件

在观察到的一次入侵中，受攻击网络中的所有内部用户都收到了类似于图6所示的电子邮件，其中垃圾邮件作为合法的回复发送给现有的电子邮件线程。所有发现的电子邮件都是用英文写的，因为这次垃圾邮件攻击发生在中东。虽然不同的地区使用不同的语言，但大多数是用英语书写的。更值得注意的是，受害者域名的真实帐户名被用作发送者和接收者，因而接收者更有可能点击链接并打开恶意的
Microsoft Excel 电子表格。

![Malicious spam via the MTA route
](https://images.seebug.org/content/images/2021/11/26/1637893124000-7jfysa.png-w331s)
图7. 通过 MTA 路由发送的恶意垃圾邮件

在同一次入侵中，我们分析了收到的恶意电子邮件的邮件头，邮件路径是内部的(在三个内部交换服务器的邮箱之间)
，这表明这些电子邮件并非来自外部发件人、公开邮件中继或任何邮件传输代理(MTA)。

![Malicious Microsoft Excel document
](https://images.seebug.org/content/images/2021/11/26/1637893125000-8wvhis.png-w331s)
图8. 恶意的 Microsoft Excel 文档

使用这种技术向所有内部域用户发送恶意垃圾邮件，它被发现或被阻止攻击的可能性会降低，因为邮件逃逸无法过滤或隔离任何这些内部电子邮件。攻击者在访问易受攻击的
Exchange 服务器之后，也没有丢弃或使用横向移动工具，因此不会检测到可疑的网络活动。此外，Exchange
服务器上没有执行恶意软件，这些恶意软件在恶意电子邮件在环境中传播之前不会触发任何警报。

## 恶意的 Microsoft Excel 文件

攻击者利用 Exchange 服务器发送内部邮件。这一切都是为了让用户失去防备，让他们更有可能点击链接并打开植入的 Microsoft Excel 或
Word 文件。

恶意邮件中使用的两个链接(`aayomsolutions[.]co[.]in/etiste/quasnam[]-4966787` 和
`aparnashealthfoundation[.]aayom.com/quasisuscipit/totamet[-]4966787`)在机器中放置一个
ZIP 文件。在本例中，ZIP 文件包含一个恶意的 microsoftexcel 表，该表下载并执行与 Qbot 相关的恶意 DLL。

![Excel 4.0 Macros
](https://images.seebug.org/content/images/2021/11/26/1637893126000-9hvwud.png-w331s)
图9. Excel 4.0宏

这些表包含负责下载和执行恶意 DLL 的恶意 Excel 4.0宏。

![Excel file infection
chain](https://images.seebug.org/content/images/2021/11/26/1637893127000-10aypaa.png-w331s)
图10. Excel 文件感染链

电子表格从硬编码的 url 中下载 DLL，这些 url 是 hxxps: [/] iperdesk.com/jwqj8r2nt/be.html
，hxxps: [//] arancal.com/hglcgcs3m/be.html 和 hxxps:
grandthum.co.in/9z6dh5h5g/be.html。

最后，文档使用以下命令执行 DLL:

  * C:\Windows\System32\regsvr32.exe" C:\Datop\good.good
  * C:\Windows\System32\regsvr32.exe" C:\Datop\good1.good
  * C:\Windows\System32\regsvr32.exe" C:\Datop\good2.good

![DLL infection
flow](https://images.seebug.org/content/images/2021/11/26/1637893127000-11mpioj.png-w331s)
图11. DLL 感染流程

## 安全建议

正如前面提到的，通过利用 ProxyLogon 和 ProxyShell，攻击者能够绕过通常的检查来避免被阻止。Squirrelwaffle
攻击应该让用户警惕新的策略，它们会想办法掩盖恶意邮件和文件。来自可信联系人的电子邮件也不能保证无论什么链接或文件包含在电子邮件是安全的。

必须确保已经应用了针对 Microsoft Exchange Server 漏洞的补丁程序，特别是 ProxyShell 和 ProxyLogon
(CVE-2021-34473、 cve-2021-34523和 CVE-2021-31207)。

以下是需要考虑的其他最佳安全做法:

  * 在所有 Exchange 服务器上启用虚拟补丁模块，以便为尚未针对这些漏洞修补的服务器提供关键级别的保护
  * 在关键的服务器上使用[端点检测和响应(EDR)解决方案](https://www.trendmicro.com/en_us/business/products/detection-response/edr-endpoint-sensor.html) ，因为它提供了机器内部的可见性，并检测任何在服务器上运行的可疑行为
  * 对服务器使用端点保护设计
  * 在电子邮件，网络和网络是非常进口检测类似的网址和样本应用沙盒技术

用户还可以选择通过管理检测和响应(MDR)来保护系统，该系统利用先进的人工智能来关联和优先化威胁，确定它们的来源。它可以在威胁被执行之前检测到它们，防止进一步的危害。

## IOCs

### SHA-256

Hash | Detection name | File name  
---|---|---  
4bcef200fb69f976240e7bc43ab3783dc195eac8b350e610ed2942a78c2ba568 |
Trojan.X97M.QAKBOT.YXBKIZ | keep-39492709.xls  
4cf403ac9297eeda584e8f3789bebbdc615a021de9f69c32113a7d0817ff3ddb |  |
good.good  
784047cef1ef8150e31a64f23fbb4db0b286117103e076382ff20832db039c0a |
TrojanSpy.Win32.QAKBOT.YMBJS | grand-153928705.xls  
8163c4746d970efe150d30919298de7be67365c935a35bc2107569fba7a33407 |
Trojan.XF.DLOADR.AL | miss-2003805568.xls  
89281a47a404bfae5b61348fb57757dfe6890239ea0a41de46f18422383db092 |
Trojan.Win32.SQUIRRELWAFFLE.B | Test2.test  
b80bf513afcf562570431d9fb5e33189a9b654ab5cef1a9bf71e0cc0f0580655 |
Trojan.Win32.SQUIRRELWAFFLE.B | Test1.test  
cd770e4c6ba54ec00cf038aa50b838758b8c4162ca53d1ee1198789e3cbc310a |
Trojan.Win32.SQUIRRELWAFFLE.B | test.test  
  
### Domain

aayomsolutions.co.in/etiste/quasnam[]-4966787  
aparnashealthfoundation.aayom.com/quasisuscipit/totamet-4966787

* * *

### URL

    
    
    hxxps://headlinepost.net/3AkrPbRj/x.html
    hxxps://dongarza.com/gJW5ma382Z/x.html
    hxxps://taketuitions.com/dTEOdMByori/j.html
    hxxps://constructorachg.cl/eFSLb6eV/j.html,;
    hxxps://oel.tg/MSOFjh0EXRR8/j.html
    hxxps://imprimija.com.br/BIt2Zlm3/y5.html
    hxxp://stunningmax.com/JR3xNs7W7Wm1/y1.html
    hxxps: //decinfo.com.br/s4hfZyv7NFEM/y9.html
    hxxps: //omoaye.com.br/Z0U7Ivtd04b/r.html
    hxxps://mcdreamconcept.ng/9jFVONntA9x/r.html
    hxxps://agoryum.com/lPLd50ViH4X9/r.html
    hxxps://arancal.com/HgLCgCS3m/be.html
    hxxps://iperdesk.com/JWqj8R2nt/be.html
    hxxps://grandthum.co.in/9Z6DH5h5g/be.html

* * *

### IP 地址

hxxp://24.229.150.54:995/t4  
108.179.193.34（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=108.179.193.34)）  
69.192.185.238（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=69.192.185.238)）  
108.179.192.18（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=108.179.192.18)）  
23.111.163.242（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=23.111.163.242)）

* * *

### Host Indicator

    
    
    C:\Datop\
    C:\Datop\test.test
    C:\Datop\test1.test
    C:\Datop\test2.test
    C:\Datop\good.good
    C:\Datop\good1.good
    C:\Datop\good2.good
    %windir%\system32\Tasks\aocrimn
    Scheduled task: aocrimn /tr regsvr32.exe -s "%WorkingDir%\test.test.dll" /SC ONCE /Z /ST 06:25 /ET

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1764/>

