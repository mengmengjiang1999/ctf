![](https://image.3001.net/images/20220225/1645776527_62188e8f5f59978e87577.jpg!small)勒索软件Cuba正利用微软Exchange的漏洞进入企业网络并对设备进行加密。知名网络安全公司Mandiant追踪到，使用该勒索软件的团伙名为UNC2596，而勒索软件本身的名字为COLDDRAW。其实，这个勒索软件有一个更为人熟知的名字——Cuba，本文也将以这个名字引述它。

Cuba是一项于2019年年底启动的勒索软件行动，起初发展非常缓慢，但在2020年、2021年开始加速发展。随着该软件活动的日益活跃，联邦调查局在2021年12月发布了一份关于Cuba勒索软件的警告，警告称该团伙已侵入美国49个关键基础设施组织。此外，在的一份新报告中指出，Cuba行动主要针对的是美国，其次是加拿大。

##  **混合性强却是量身定制的恶意软件**

自2021年8月以来，Cuba勒索软件团伙利用Microsoft Exchange漏洞部署网络外壳、rat病毒和后门，试图在目标网络上建立据点。

![](https://image.3001.net/images/20220225/1645776604_62188edccfc67b94c3d65.jpg!small)

这一点可以在Mandiant一份最新报告中得到验证，“早在2021年8月，UNC2596就利用了包括ProxyShell和ProxyLogon在内的微软Exchange漏洞。”

被植入的后门包括Cobalt Strike和NetSupport
Manager远程访问工具，但该组织也使用他们自己的“Bughatch”、“wedgcut”、“eck.exe”和“Burntcigar”工具。

### 以下是三种工具的简单介绍：

Wedgcut是一个通过PowerShell枚举活动目录的侦察工具，通常以名为“check.exe”的可执行文件的形式出现。

Bughatch是从C&C服务器获取PowerShell脚本和文件的下载器。为了逃避检测，它从远程URL加载到内存中。

Burntcigar是一个可以利用Avast驱动程序中的漏洞在内核级别终止进程的工具，该工具附带了Avast驱动程序，用于“自带脆弱驱动程序”攻击。

此外，还有一个内存模式的病毒释放器，它获取并加载上述有效载荷，被称为Termite。其实，它倒也不是Cuba攻击者专用，之前已经被观察到运营在多次其他攻击活动中。

研究显示，cuba攻击流程大体是这样的。首先，攻击者使用偷来的账户凭证，通过现有的Mimikatz和Wicker工具升级特权。

然后，他们使用wedgcut进行网络侦察，再之后，他们使用RDP、SMB、PsExec和Cobalt Strike进行横向移动。

随后部署的是便是由Termite加载的Bughatch和 Burntcigar，它们通过禁用安全工具为数据外泄和文件加密奠定了基础。

Cuba不使用任何云服务来进行数据渗漏，而是将所有信息发送到他们自己的私人基础设施上。

###
![](https://image.3001.net/images/20220225/1645776644_62188f049be471317e151.jpg!small)

##  **恶意软件进化史**

早在2021年5月，Cuba勒索软件就与Hancitor恶意软件的垃圾邮件运营商合作，通过DocuSign钓鱼邮件进入公司网络。

从那之后，Cuba逐步发展了针对面向公众服务漏洞的攻击，如Microsoft Exchange ProxyShell和ProxyLogon漏洞。

这一转变使Cuba攻击更加强大，但却也更容易被防御，因为早在几个月前修补那些漏洞的安全更新就已经发布。

如果大多数有价值的目标都已经更新Microsoft Exchange漏洞补丁，Cuba攻击就可能会将注意力转向其他漏洞。

这就给了我们一个启示，一旦软件供应商发布可用的安全更新，就立即应用这些更新，这对我们而言至关重要，即使我们面对最复杂的攻击者，我们也能够保持强大的安全态势。

> 参考来源：https://www.bleepingcomputer.com/news/security/microsoft-exchange-> servers-hacked-to-deploy-cuba-ransomware/

