![v2-ede9906e2edbdfbf027f70ecf91c86f9_720w.jpg](https://image.3001.net/images/20211117/1637117565_61946e7d19f88ac12e53b.jpg!small)

由于保密要求，无法展示真实场景数据，故在本地搭建域环境进行测试。

在深入了解如何通过证书服务攻击获取域控权限之前，我们先进入草莓时刻，了解一下什么是AD CS。

 **Background**

近日国外安全研究员Will Schroeder and Lee Christensen在Black Hat 2021中发表了一项重要的议题，他们花费数月研究
Active Directory Certificate Services (AD CS）并于6月17号发布《Certified Pre-Owned》白皮书，详细分析了AD CS服务潜在的一些漏洞和手法。

![v2-22703b0e0f49277c6921ffdaaec8ff0f_720w.jpg](https://image.3001.net/images/20211117/1637117565_61946e7deb8f917eabc7b.jpg!small)

虽然默认情况下没有为 Active Directory 环境安装AD CS，但据据国外安全研究员的调查统计，目前大部分企业均部署了该服务，且许多AD
CS的环境均存在误配，在这种情况下，攻击者可以利用没有正确配置的AD
CS服务进行用户凭证窃取、权限维持、域控提权及域内权限维持等。因此错误配置的证书服务实例导致域安全变得脆弱，这就使得研究AD CS及其相关漏洞具有重要意义。

![v2-f1790a43ee3fe27db7d1c579caa63812_720w.jpg](https://image.3001.net/images/20211117/1637117566_61946e7e59ae037852bfe.jpg!small)

了解完AD CS的工作原理后，接下来我们将通过真实环境的再模拟，深度还原真实场景。

##  **0x01 环境搭建**

此段将重点阐述ADCS证书服务的搭建。

主要搭建步骤如下：

 **服务器管理器-- >添加角色和功能向导-->勾选服务器角色-->勾选证书注册服务和证书注册策略服务-->安装**

![v2-c2c89cc988883689f6436a0cc0cb1cec_720w.jpg](https://image.3001.net/images/20211117/1637117566_61946e7ed31dc1bff051e.jpg!small)![v2-04132b4a47686cd82e6e9b65f9b74cd5_720w.jpg](https://image.3001.net/images/20211117/1637117567_61946e7f571460ac870fc.jpg!small)

## 小贴士

 **AD CS服务器的搭建**

因为在实际攻击过程中，不能将认证请求Relay到自身，所以此处并不建议将AD
CS服务搭建在主域控制器上，在真实环境中，也很少有管理员会将证书服务装在域控上，故我方可以随意挑选一台机器作为我们的AD CS服务器。

 **证书注册Web服务（CES）**

证书注册 Web 服务是一种 Active Directory 证书服务 (AD CS) 角色服务，它使用户和计算机能够使用 HTTPS
协议来进行证书注册。主要有以下功能：请求、更新和安装颁发的证书、检索证书吊销列表 (CRL)、下载根证书、通过互联⽹或跨森林注册、为属于不受信任的 AD
DS 域或未加⼊域的计算机⾃动续订证书。

 **证书注册策略服务**

该组件使⽤户能够获取证书注册策略信息。结合CES，它可以在⽤户设备未加⼊域或⽆法连接到域控制器的场景中实现基于策略的证书注册。

当在企业服务器上部署完AD CS后，根据提示完成安装配置。

![v2-a5b36caa6e1d63a1e37ebf6d2c976a84_720w.jpg](https://image.3001.net/images/20211117/1637117567_61946e7fcf1a8ddd43e35.jpg!small)![v2-5da04fc5998217c94bdebe0cb11d638c_720w.jpg](https://image.3001.net/images/20211117/1637117569_61946e8109c5c997872c2.jpg!small)

请注意，该电脑在机器上的登陆账号一定要属于Enterprise Admins组，否则在安装企业CA时，出现无法选择的提示。

![v2-c09dcb1fdcb985f6edf857c1e9b5067a_720w.jpg](https://image.3001.net/images/20211117/1637117569_61946e815747c205fc1e3.jpg!small)

当选择完成后，后面步骤都选择“下一步”即可。

![v2-6891f666cc934e8f8bf188257036d433_720w.jpg](https://image.3001.net/images/20211117/1637117569_61946e81a5729c80fd5c8.jpg!small)![v2-1b11c51645509d60fad596e49d6a0cf6_720w.jpg](https://image.3001.net/images/20211117/1637117570_61946e820efea7f5e68ae.jpg!small)

安装完成后，在浏览器中输入并访问http://<AD CS server >/certsrv，当出现登陆页面时，即为安装成功。

![v2-71246a2fb0165ebe10b48b986f4b84f9_720w.jpg](https://image.3001.net/images/20211117/1637117570_61946e8263dda6e81c7bb.jpg!small)![v2-ea8e914444826d24847518f680ab7cd0_720w.jpg](https://image.3001.net/images/20211117/1637117570_61946e82e565076611e11.jpg!small)

##  **0x02 AD CS + NTLM Relay获取域控权限**

当我们配置好AD CS服务，在浏览器中访问http://<AD CS server >/certsrv
时，将出现认证界面（此认证界面为NTLM认证），由于该认证未配置NTLM中继保护，我们可以配合NTLM Relay获取高权限机器：

![v2-cefc27c59f930b1272bd2770696179f0_720w.jpg](https://image.3001.net/images/20211117/1637117571_61946e83de224129d2245.jpg!small)

AD CS通过管理员安装的其他AD CS服务器角色支持几种基于HTTP的注册方法，例如上述提到的证书注册Web服务（CES），证书注册策略服务等。

这些基于HTTP的证书注册接口都是易受NTLM
Relay攻击，使得攻击者可以仿冒任何通过NTLM认证的AD账号。在仿冒受害者帐户时，攻击者可以访问这些Web界面，并根据用户或计算机证书模板请求客户端身份验证证书。

 **01 实验环境**

![v2-9454e25292b4a5449f9968955dfe3ad2_720w.jpg](https://image.3001.net/images/20211117/1637117572_61946e84459a4b8d6d2b8.jpg!small)

 **02 工具安装**

最新的Impacket工具包已经支持AD CS的NTLM Relay攻击。

![v2-44ce30de831b73ce38de764d6304b17c_720w.jpg](https://image.3001.net/images/20211117/1637117572_61946e84d90c3948f2683.jpg!small)

当上述操作完成后，我们就可以在Kali攻击机设置NTLM中继，通过已发现的漏洞，让域控向攻击中转机发起验证，将传入的身份验证从Kali转发到AD
CS服务器进行身份验证。

![v2-37d0e2e498713e189a1536d1b294b249_720w.jpg](https://image.3001.net/images/20211117/1637117573_61946e851dfbeef35da8a.jpg!small)

此时，NTLM中继已准备就绪，正在等待Kali传入身份验证，当该部分数据导出之后就可以强制DC-01向NTLM中继进行身份验证。

特别提示：当使用了基于MS-EFSRPC的Petitpotam无法成功利用，也可以使用传统的Printerbug。

![v2-e46bffd677c2b1f0128a26408f734dd0_720w.jpg](https://image.3001.net/images/20211117/1637117573_61946e856ab2302e78acd.jpg!small)

当Kali收到票证，即可用于身份验证。

![v2-3efff8a081038e99308c748fc6a6867e_720w.jpg](https://image.3001.net/images/20211117/1637117573_61946e85bff3714cb1964.jpg!small)

拥有了这个票证，我们可以用来请求域间票证授予票证（TGT）。

![v2-cd33f1e36c4d5dab564f37dd661a2c3e_720w.jpg](https://image.3001.net/images/20211117/1637117574_61946e862710b3f8af2f6.jpg!small)![v2-e50d524a427c986228ab6d2888e8b716_720w.jpg](https://image.3001.net/images/20211117/1637117574_61946e8694ce63968284c.jpg!small)![v2-6545c035f1ed97ab212d8282ffb61f92_720w.jpg](https://image.3001.net/images/20211117/1637117575_61946e872ec4779e21cd3.jpg!small)

在成功获取票证后，使用DCSync导出了所有的Hash
即可控制域内所有的机器，根据信息搜集阶段搜集的信息定位到靶标机，并成功登陆，如图所示使用DCSync导出krbtgt账号Hash。

![v2-9070e66ecd5c7cfd25f1bfd0344c49e8_720w.jpg](https://image.3001.net/images/20211117/1637117575_61946e87a49250bc1fa69.jpg!small)

##  **0x03 Conclusion**

上述内容详细介绍了AD CS服务的搭建方法，以及配合NTLM Relay 服务获取域控权限。简单总结一下本次攻防对抗的渗透流程：

> 通过Web打点进入内网，通过资产探测发现存在域环境。
>
> 尝试SPN服务扫描，获取部分可进行Kerberoasting的高权限账号，但是爆破无果。
>
> 域内提权历史漏洞已修补。
>
> 通过定位证书服务器，发现其开放证书注册Web服务，通过上述步骤成功获取TGT票据。
>
> 通过域内信息聚合定位到靶标，使用域管Hash登录该服务器，结束渗透。

