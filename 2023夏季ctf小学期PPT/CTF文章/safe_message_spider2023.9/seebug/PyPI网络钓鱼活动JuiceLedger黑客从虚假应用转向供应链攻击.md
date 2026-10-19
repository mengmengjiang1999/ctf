**作者：AMITAI BEN SHUSHAN EHRLICH  
译者：知道创宇404实验室翻译组  
原文链接：<https://www.sentinelone.com/labs/pypi-phishing-campaign-juiceledger-threat-actor-pivots-from-fake-apps-to-supply-chain-attacks/>**

## 执行摘要

1.JuiceLedger是一个相对新的黑客，专注于通过名为“JuiceStealer”的.NET程序集窃取信息。  
2.JuiceLedger在短短6个月多的时间里迅速将其攻击链从欺诈应用程序演变为供应链攻击。  
3.8月，JuiceLedger对PyPI贡献者进行了网络钓鱼活动，并成功入侵了多个合法软件包。  
4.已识别出数百个提供JuiceStealer恶意软件的仿冒包。  
5.至少有两个下载总量接近70万的软件包遭到入侵。  
6.PyPI表示，已知的恶意软件包和仿冒域名现已被删除。

## 概述

SentinelLabs与[Checkmarx](https://checkmarx.com/blog/first-known-phishing-attack-against-pypi-users/)合作，一直在跟踪被称为“JuiceLedger”的黑客的活动和演变。2022年初，JuiceLedger开始开展相对低调的活动，使用“JuiceStealer”传播欺诈性Python安装程序应用程序，该`.NET`应用程序旨在从受害者的浏览器中窃取敏感数据。2022年8月，黑客投毒开源软件包，以通过供应链攻击将更广泛的受众锁定为信息窃取者，大大提高了该组织构成的威胁级别。

JuiceLedger运营商在网络钓鱼活动中积极针对PyPi包贡献者，成功地用恶意软件毒化了至少两个合法包。已知还有数百个恶意程序包被误码。

在这篇文章中，我们详细介绍了JuiceLedger的演变，描述了该组织的攻击向量和活动，并提供了对JuiceStealer有效负载的分析。

## 双管齐下的攻击—虚假应用和供应链攻击

![img](https://images.seebug.org/content/images/2022/09/07/1662525445000-1avedv.png-w331s)

对[PyPi包贡献者](https://twitter.com/pypi/status/1562442188285308929)的供应链攻击似乎是今年早些时候开始的活动的升级，该活动最初通过虚假的加密货币交易应用程序针对潜在受害者，其中一个机器人被称为“AI加密货币交易机器人”，名为“特斯拉交易机器人”。

今年8月，对PyPI的攻击涉及一个更为复杂的攻击链，包括向PyPI开发人员发送的网络钓鱼电子邮件、域名仿冒以及旨在用JuiceStealer恶意软件感染下游用户的恶意程序包。该向量似乎与早期的JuiceLedger感染方法并行使用，因为类似的有效载荷大约在同一时间通过假加密货币分类帐网站交付。

## 针对PyPI贡献者

2022年8月24日，PyPi发布了针对PyPi用户的持续网络钓鱼活动的[详细信息](https://twitter.com/pypi/status/1562442188285308929)。根据他们的报告，这是已知的第一个针对PyPI的网络钓鱼攻击。网络钓鱼电子邮件指出，强制“验证”过程要求贡献者验证他们的包，否则有可能将其从PyPI中删除。

![PyPI supply chain attack phishing
email](https://images.seebug.org/content/images/2022/09/07/1662525489000-2xufes.png-w331s)

发送给PyPI贡献者的网络钓鱼电子邮件示例。资料来源：PyPI通过Twitter

网络钓鱼电子邮件将受害者指向模仿PyPI登录页面的Google网站登录页面。那里提供的凭据被发送到一个已知的JuiceLedger域：`linkedopports[.]com`.

![img](https://images.seebug.org/content/images/2022/09/07/1662525525000-3blvbv.png-w331s)
PyPi钓鱼网站。[资料来源](https://twitter.com/pypi/status/1562442199811309568?s=20&t=cG3jJe6qSl2DOOfCWVq6Qg):PyPI通过Twitter

其中一些网络钓鱼攻击似乎已经成功，导致其贡献者凭据被泄露的合法代码包遭到破坏。

PyPI还报告说，他们发现了许多符合类似模式的域名仿冒包。JuiceLedger使用域名仿冒来传递其恶意应用程序。

抢注流行的代码包并不是什么新鲜事。在过去几年中出现了类似攻击的报告，包括针对Rust开发人员的[CrateDepression](https://www.sentinelone.com/labs/cratedepression-rust-supply-chain-attack-infects-cloud-ci-pipelines-with-go-malware/)活动，最近由SentinelLabs报道。

JuiceLedger在8月份的活动中上传的受损包包含一个简短的代码片段，负责下载和执行JuiceStealer的签名变体。添加的恶意代码如下所示。

![img](https://images.seebug.org/content/images/2022/09/07/1662525546000-4tmrsw.png-w331s)
恶意代码片段。[资料来源](https://checkmarx.com/blog/first-known-phishing-attack-against-pypi-users/):Checkmarx

添加到这些包中的代码片段与在域名抢注包中添加的代码片段非常相似。根据PyPI，恶意代码片段存在于以下软件包中：

    
    
     exotel==0.1.6
     spam==2.0.2 and ==4.0.2

查看受感染包的代码片段表明，参与者在注册URL中添加了受感染包的指示。

![img](https://images.seebug.org/content/images/2022/09/07/1662525582000-5whpvx.png-w331s)
来自 _exotel_
中毒代码的片段。[资料来源](https://twitter.com/pypi/status/1562442207079976966?s=20&t=cG3jJe6qSl2DOOfCWVq6Qg)：PyPi通过Twitter

JuiceLedger的8月活动还包含一个以Ledger为主题的欺诈应用程序。Ledger是一种用于加密资产的硬件“冷存储”钱包技术，其用户已成为嵌入假Ledger安装包中的数字签名版本的JuiceStealer的目标。

![Certificate used to sign JuiceStealer
malware](https://images.seebug.org/content/images/2022/09/07/1662525591000-6gsdzv.png-w331s)
用于签署JuiceStealer恶意软件的证书

该证书 `13CFDF20DFA846C94358DBAC6A3802DC0671EAB2`用于签署总共四个样本，其中一个样本看似无关，但都是恶意的。

## JuiceStealer恶意软件分析

JuiceLedger的信息窃取器，称为JuiceStealer，是一个相对简单的`.NET`应用程序，内部命名为“meta”。盗窃者的第一个迹象是在今年2月开始出现的。经过多次迭代，信息窃取器被嵌入到许多欺诈性应用程序和安装程序中。

### Python安装程序

2月13日上传到VirusTotal的第一版
JuiceStealer(`d249f19db3fe6ea4439f095bfe7aafd5a0a5d4d2`)似乎不完整，可能是开发人员提交的测试。它是一组模仿Python安装程序变体中的第一个。

此示例遍历包含单词“chrome”的进程，将其关闭，然后搜索Google
Chrome扩展日志文件。信息窃取程序会遍历包含单词“vault”的日志，可能会搜索加密货币库，并通过HTTP向嵌入式C2服务器报告。

    
    
    private static void Main(string[] args)
    {
      Console.WriteLine("Please wait while Python installs...");
      string[] directories = Directory.GetDirectories("C:\\Users\\" + Environment.UserName + "\\AppData\\Local\\Google\\Chrome\\User Data");
      foreach (Process process in Process.GetProcessesByName("chrome"))
      process.Kill();
      Thread.Sleep(2500);
      Console.WriteLine("Python is almost ready...");

几天后，欺诈安装程序的完整版本作为名为“python-v23.zip”的zip文件(`1a7464489568003173cd048a3bad41ca32dbf94f`)的一部分提交，其中包含infostealer的更新版本、合法的python安装程序和指令文件“INSTRUCTIONS.exe”。

![img](https://images.seebug.org/content/images/2022/09/07/1662525601000-7exhdy.png-w331s)
伪造的Python安装程序说明文件

此版本的信息窃取程序引入了一个名为“Juice”（因此得名）的新类，并且还可以搜索Google Chrome密码、查询Chrome
SQLite文件。它还会启动包含在名为“config.exe”的zip中的Python安装程序。将合法软件命名为“config.exe”似乎在各种JuiceStealer变体中很常见。

像我们分析的许多JuiceStealer样本一样，它被编译为一个独立的`.NET`应用程序。这使文件明显变大。

`pdb`许多早期版本的JuiceStealer共有的路径包含用户名“reece”和内部项目名称“meta” 。

    
    
    C:\Users\reece\source\repos\meta\meta\obj\Release\netcoreapp3.1\win-x86\meta.pdb

## JuiceStealer的进化

以观察到的`pdb`路径为中心，我们能够将其他活动链接到JuiceLedger。再加上我们对JuiceStealer开发阶段的额外发现，表明该组织于2021年底开始运营。

### Pre-JuiceStealer虚假安装程序

1月30 日，一组三个编译为独立应用程序的虚假安装程序从位于GB的提交者 _f40316fe_
上传到VirusTotal。同一提交者还上传了JuiceStealer的第一个变体，这似乎也是一个测试。所有伪造的安装程序都有一个相似的`pdb`路径，包含用户名“reece”，并且似乎是黑客对JuiceStelaer的第一次迭代。

    
    
    C:\Users\reece\source\repos\install-python\install-python\obj\Release\netcoreapp3.1\win-x86\install-python.pdb

### Nowblox诈骗网站

在整个研究过程中，我们发现了与Nowblox的可能联系，Nowblox是一个于
2021年运营的诈骗网站，提供免费的Robux。几个名为“Nowblox.exe”的应用程序从GB的提交者系统地上传到VirusTotal，所有应用程序都具有以下`pdb`路径：

    
    
    C:\\Users\\reece\\source\\repos\\Nowblox\\Nowblox\\obj\\Debug\\Nowblox.pdb

虽然路径本身并不是一个很强的指示，但我们在研究中发现了另一个指向Nowblox的链接，其形式为名为“NowbloxCodes.iso”(`5eb92c45e0700d80dc24d3ad07a7e2d5b030c933`)的文件。使用ISO文件可能表明它是通过网络钓鱼电子邮件发送的，因为ISO文件已成为绕过电子邮件安全产品的[流行攻击媒介](https://www.sentinelone.com/labs/who-needs-macros-threat-actors-pivot-to-abusing-explorer-and-other-lolbins-via-windows-shortcuts/)。但是，我们没有数据可以验证这一点。

该文件包含一个LNK文件(`e5286353dec9a7fc0c6db378b407e0293b711e9b`)，触发执行混淆的PowerShell命令，该命令反过来运行`mstha`从当前离线的`hxxps://rblxdem[.]com/brace.hta`加载一个`.HTA`文件。

该域`rblxdem[.]com`托管在`45.153.35[.]53`，用于托管多个Ledger网络钓鱼域以及JuiceStealer
C2域`thefutzibag[.]com`，提供了另一个可能的JuiceLedger链接。

## 欺诈性应用程序——特斯拉交易机器人

随着时间的推移，JuiceLedger运营商开始使用直接以加密货币为主题的欺诈应用程序，其中，他们命名为“Tesla Trading
bot”的应用程序。以与Python安装程序类似的方案交付，它嵌入在带有其他合法软件的zip文件中JuiceStealer在此期间发生了重大变化，增加了对其他浏览器和Discord的支持。

嵌入的指令消息与伪Python安装程序中的消息非常相似，提示用户禁用他们的安全解决方案。

![img](https://images.seebug.org/content/images/2022/09/07/1662525615000-8iftqr.png-w331s)
JuiceLedger安装程序敦促用户绕过自己的安全性

虽然交付机制仍不清楚，但JuiceLedger运营商似乎为虚假交易机器人维护了一个网站，促使用户下载欺诈性应用程序。

![img](https://images.seebug.org/content/images/2022/09/07/1662525625000-9iwkfx.png-w331s)
恶意特斯拉交易机器人的下载站点

## PyPI响应

PyPI[表示](https://twitter.com/pypi/status/1562442209177522177?s=20&t=cG3jJe6qSl2DOOfCWVq6Qg)他们正在积极审查恶意软件包的报告，并已删除了数百个仿冒域名。敦促包维护者在可用的情况下对其帐户使用2FA授权，并在输入凭据时确认地址栏中的URL`http://pypi.org`。用户还可以检查站点的TLS证书是否颁发给`pypi.org`.

建议认为自己可能是JuiceLedger攻击受害者的维护者立即重置密码，并将任何可疑活动报告给security@pypi.org。

## 结论

JuiceLedger似乎已经从几个月前的机会主义、小规模感染迅速演变为对主要软件分销商进行供应链攻击。对PyPI贡献者的攻击的复杂性升级，包括有针对性的网络钓鱼活动、数百个域名仿冒包和受信任开发人员的帐户接管，这表明黑客有时间和资源可供使用。

鉴于PyPI和其他开源软件包在企业环境中的广泛使用，诸如此类的攻击令人担忧，敦促安全团队审查提供的指标并采取适当的缓解措施。

## IOC

**伪Python安装程序**  
90b7da4c4a51c631bd0cbe8709635b73de7f7290
dd569ccfe61921ab60323a550cc7c8edf8fb51d8
97c541c6915ccbbc8c2b0bc243127db9b43d4b34
f29a339e904c6a83dbacd8393f57126b67bdd3dd
71c849fc30c1abdb49c35786c86499acbb875eb5
2fb194bdae05c259102274300060479adf3b222e

**Nowblox ISO 文件**  
5eb92c45e0700d80dc24d3ad07a7e2d5b030c933
e5286353dec9a7fc0c6db378b407e0293b711e9b

**CryptoJuice 样品**

**SHA1** | **提交日期** | **领域**  
---|---|---  
cbc47435ccc62006310a130abd420c5fb4b278d2 | 2022-08-24 11:00:45 |
linkedopports[.]com  
8bbf55a78b6333ddb4c619d615099cc35dfeb4fb | 2022-08-24 10:59:40 |
linkedopports[.]com  
bac2d08c542f82d8c8720a67c4717d2e70ad4cd9 | 2022-08-23 21:34:01 |
linkedopports[.]com  
567e1d5aa3a409a910631e109263d718ebd60506 | 2022-08-23 21:33:58 |
linkedopports[.]com  
1e697bc7d6a9762bfec958ee278510583039579c | 2022-08-23 21:32:31 |
linkedopports[.]com  
ea14f11e0bd36c2d036244e0242704f3cf721456 | 2022-08-20 13:29:20 |
ledgrestartings[.]com  
5703ed6565888f0b06fffcc40030ba679936d29f | 2022-08-20 13:25:59 |
ledgrestartings[.]com  
cd0b8746487d7ede0ec07645fd4ec655789c675b | 2022-08-18 08:43:43 | python-release[.]com  
d3ed1c7c0496311bb7d1695331dc8d3934fbc8ec | 2022-08-18 08:33:28 | python-release[.]com  
0a6731eba992c490d85d7a464fded2379996d77c | 2022-08-18 08:32:00 | python-release[.]com  
a30df748d43fbb0b656b6898dd6957c686e50a66 | 2022-08-08 00:10:52 | python-release[.]com  
52b7e42e44297fdcef7a4956079e89810f64e113 | 2022-08-08 00:07:36 | python-release[.]com  
aa8c4dffeeacc1f7317b2b3537d2962e8165faa2 | 2022-08-05 10:19:20 |
thefutzibag[.]com  
a6348aea65ad01ee4c7dd70b0492f308915774a3 | 2022-08-05 10:06:04 |
thefutzibag[.]com  
b305c16cb2bc6d88b5f6fe0ee889aaf8674d686e | 2022-05-04 03:15:56 | ledge-pc[.]com  
666e5554ccdafcb37a41f0623bb9acc53851d84f | 2022-04-06 10:45:39 |
trezsetup[.]com  
463897fa2dd2727a930b8f3397d10a796b6aa0d6 | 2022-04-06 10:38:24 |
trezsetup[.]com  
e2e239f40fdb2e5bf9d37b9607b152f173db285c | 2022-03-30 04:58:00 |
axiesinfintity[.]com  
c0e3c2436e225f7d99991a880bf37d32ff09c5bd | 2022-03-27 18:14:18 |
axiesinfintity[.]com  
6f3c5a06d1a53fac45182e76897e7eab90d4a186 | 2022-03-22 09:08:18 | campus-art[.]com  
bd7eb97b3dc47e72392738d64007df5fc29de565 | 2022-03-21 15:10:01 | campus-art[.]com  
de4596669f540b8bd34aa7cbf50e977f04f3bba3 | 2022-03-20 22:07:30 |
teslatradingbot[.]com  
55ba11f522532d105f68220db44392887952e57b | 2022-03-14 05:02:04 |
barkbackbakery[.]com  
9e9c6af67962b041d2a87f2abec7a068327fa53a | 2022-03-13 05:01:47 |
barkbackbakery[.]com  
ed9a4ce2d68d8cc9182bb36a46d35a9a8d0510cb | 2022-03-06 23:21:48 |
capritagworld[.]com  
f10006f7b13e4746c2293a609badd2d4e5794922 | 2022-03-06 23:14:04 |
capritagworld[.]com  
f07954ba3932afd8ad7520c99a7f9263aa513197 | 2022-03-06 17:29:24 |
teslatradingbot[.]com  
56e3421689d65e78ff75703dd6675956b86e09e8 | 2022-03-05 22:53:42 |
ideasdays[.]com  
004c66532c49cb9345fc31520e1132ffc7003258 | 2022-03-05 21:01:36 |
ideasdays[.]com  
6fe5f25205679e148b7b93f1ae80a659d99c7715 | 2022-03-04 18:35:32 |
teslatradingbot[.]com  
964e29e877c65ff97070b7c06980112462cd7461 | 2022-03-02 02:08:58 |
teslatradingbot[.]com  
225638350f089ee56eae7126d048b297fce27b7d | 2022-02-28 19:30:23 | hitwars[.]com  
9fb18a3426efa0034f87dadffe06d490b105bda3 | 2022-02-28 19:23:51 | hitwars[.]com  
a78dd3cd9569bd418d5db6f6ebf5c0c5e362919b | 2022-02-18 22:53:42 |
barkbackbakery[.]com  
d249f19db3fe6ea4439f095bfe7aafd5a0a5d4d2 | 2022-02-13 07:10:09 |
barkbackbakery[.]com  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1960/>

