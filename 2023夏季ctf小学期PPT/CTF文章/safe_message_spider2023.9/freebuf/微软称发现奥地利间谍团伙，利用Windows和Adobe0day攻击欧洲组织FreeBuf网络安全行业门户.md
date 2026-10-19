7月28日消息，微软安全和威胁情报团队称发现 **一家奥地利公司销售间谍软件DSIRF**
，该软件是基于未知的Windows漏洞开发。当前的受害者包括奥地利、英国和巴拿马等国的律师事务所、银行和战略咨询公司。

**![](https://image.3001.net/images/20220729/1659067649_62e35d019d8dd3bc2d853.png!small)DSIRF声称帮助跨国公司进行风险分析和收集商业情报**
。微软威胁情报中心（MSTIC）分析发现，间谍软件DSIRF利用Windows的零日特权升级漏洞和Adobe Reader远程代码漏洞执行攻击。微软表示，
**DSIRF利用的漏洞目前在更新补丁中已经修补**
。在内部，微软以代号KNOTWEED对DSIRF进行追踪，并表示该公司还与SubZero恶意软件的开发和销售有关。

MSTIC发现DSIRF与恶意软件之间有多种联系，包括恶意软件使用的命令和控制基础设施直接链接到DSIRF、一个与DSIRF相关的GitHub账户被用于一次攻击、发给DSIRF的代码签名证书被用于签署一个漏洞。

 **攻击中出现的CVE-2022-22047漏洞能从沙盒中逃脱** 。微软解释，该漏洞链开始时，从沙盒中的Adobe
Reader渲染器进程写入一个恶意DLL到磁盘。然后，CVE-2022-22047漏洞被用来瞄准一个系统进程，通过提供一个应用程序清单，其中有一个未记录的属性，指定恶意DLL的路径。当系统进程下一次生成时，恶意激活上下文中的属性被使用，恶意DLL从给定的路径加载，从而执行系统级代码。

调查人员已经确定了DSIRF控制下的一系列IP地址，该基础设施主要由Digital
Ocean和Choopa托管，至少从2020年2月开始就积极为恶意软件提供服务，并持续到现在。

微软建议保持最新的补丁和恶意软件检测，并注意破坏后的行动，如凭证转储和启用明文凭证。

 **参考链接：**

> [Microsoft reports Knotweed gang making SubZero attacks • The
> Register](https://www.theregister.com/2022/07/27/knotweed/)
>
> [Microsoft says it caught an Austrian spyware group using Windows 0-day
> exploits - The](https://www.theverge.com/2022/7/27/23281215/microsoft-> austrian-commercial-spyware-dsirf-knotweed-intelligence-> committee)[Verge](https://www.theverge.com/2022/7/27/23281215/microsoft-> austrian-commercial-spyware-dsirf-knotweed-intelligence-committee)

