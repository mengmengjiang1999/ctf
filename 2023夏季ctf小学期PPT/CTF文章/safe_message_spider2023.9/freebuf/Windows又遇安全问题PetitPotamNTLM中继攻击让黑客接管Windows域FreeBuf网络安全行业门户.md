Windows操作系统中一个新发现的安全漏洞可被利用来强制远程Windows服务器(包括域控制器)与恶意目标进行身份验证，从而允许攻击者发起NTLM中继攻击并完全接管Windows域。

这个被称为“ PetitPotam ”的问题是由安全研究员Gilles
Lionel发现的，他上周分享了技术细节和概念验证(PoC)代码，指出该漏洞的工作原理是“Windows主机通过MS-EFSRPC
EfsRpcOpenFileRaw函数对其他机器进行身份验证”。

## 什么是MS-EFSRPC?

MS-EFSRPC是微软的加密文件系统远程协议，该协议用于对远程存储并通过网络访问的加密数据执行维护和管理操作。

具体来说，该攻击使域控制器能够使用MS-EFSRPC接口在恶意行为者的控制下对远程
NTLM进行身份验证并共享其身份验证信息。通过连接到LSARPC完成以上控制，从而导致目标服务器连接到任意服务器并执行NTLM身份验证。

网络安全人员称：攻击者可以通过使用MS-EFSRPC协议将DC NTLM 凭据中继到Active Directory证书服务AD CS
Web注册页面以注册DC证书，从而以域控制器为目标来发送其凭据。 这将有效地为攻击者提供一个身份验证证书，该证书可用于作为DC访问域服务并破坏整个域。

![](https://image.3001.net/images/20210727/1627350778_60ff66fab07a8346c93ae.jpg!small)

## 影响版本

NTLM身份验证哈希可用于执行中继攻击，或者最近可以破解以获取受害者的密码。PetitPotam攻击可能非常危险，因为它允许攻击者接管域控制器并危害整个企业组织。

该PetitPotam技术可以潜在地影响大多数支持的Windows版本中，它成功地依靠Windows 10和Windows Server
2016和Windows Server 2019对系统进行测试。

## 微软解决方案

虽然禁用对MS-EFSRPC的支持并不能阻止攻击运行，但微软此后发布了针对该问题的缓解措施，同时将“PetitPotam”描述为“经典的NTLM中继攻击”，它允许具有网络访问权限的攻击者拦截合法客户端和服务器之间的身份验证流量，并中继那些经过验证的身份验证请求以访问网络服务。

微软指出：为了防止在启用了NTLM的网络上发生NTLM中继攻击，域管理员必须确保允许NTLM身份验证的服务使用诸如扩展身份验证保护 (EPA)
或签名功能(如 SMB 签名)之类的保护措施。”

“PetitPotam利用服务器，其中Active Directory证书服务(AD CS)未配置NTLM中继攻击保护。

![](https://image.3001.net/images/20210727/1627350760_60ff66e873e22cb67fb6a.jpg!small)

为了防止这种攻击，Windows制造商建议客户在域控制器上禁用 NTLM身份验证。如果出于兼容性原因无法关闭 NTLM，该公司敦促用户采取以下两个步骤之一
：

使用组策略网络安全：限制 NTLM：传入 NTLM 流量在域中的任何 AD CS 服务器上禁用 NTLM。

在运行“证书颁发机构Web注册”或“证书注册Web服务”服务的域中的AD CS服务器上禁用Internet信息服务(IIS)的NTLM。

如果没有必要，Microsoft 建议强烈建议禁用NTLM，或者启用身份验证扩展保护机制以保护Windows计算机上的凭据。

PetitPotam标志着过去一个月内在PrintNightmare和SeriousSAM(又名
HiveNightmare)漏洞之后披露的第三个主要Windows安全问题。

软件应用在不断更新和使用的同时，也为网络攻击提供了一定条件。系统中任何一个微不足道的问题都很可能演变成带有巨大潜在危害的安全漏洞，因此不论是在软件使用时，还是开发过程当中，确保软件安全成为重要任务。尤其网络攻击逐年增加，任何一个不当配置或[
**代码缺陷**](https://www.woocoom.com/b031.html)都可能为网络攻击埋下伏笔。因此软件开发企业有必要在开发过程中确保软件安全，检测并改正
**代码缺陷** ，同时加强软件安全漏洞扫描，从多方面降低遭受网络攻击的风险。

> 参读链接：
>
> <https://www.woocoom.com/b021.html?id=465465468ff94962ad6457303238c7d7>
>
> <https://thehackernews.com/2021/07/new-petitpotam-ntlm-relay-attack-> lets.html>

