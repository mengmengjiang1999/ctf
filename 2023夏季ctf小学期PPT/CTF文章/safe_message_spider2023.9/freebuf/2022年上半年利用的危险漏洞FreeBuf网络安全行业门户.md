在过去几年中，漏洞的数量和复杂性都有所增加。它们采取各种形式，并被转换为远程代码执行缺陷或权限升级场景。接下来介绍几种2022年上半年网络攻击者利用的一些危险的漏洞。

## ProxyLogon (cve - 2021 - 26855)

ProxyLogon 是一个影响 Microsoft Exchange 2013、2016 和 2019
的漏洞。它允许攻击者绕过身份验证，从而冒充管理员。由于内部基础设施缺乏更新，这仍然是 2022 年被利用最多的漏洞之一。

该漏洞于 2021 年 8 月发布，已被添加到各种自动工具包中，并被广泛的网络攻击者在存在该漏洞时使用恶意代码。这个漏洞可以很容易地在端口 433
上被利用，为横向移动、持久访问和远程操作打开大门。

![](https://image.3001.net/images/20220819/1660875693_62fef3ad8aa1ea6264128.png!small)

## ZeroLogon (CVE-2020-1472)

出于同样的原因，CVE-2020-1472(也称为
ZeroLogon)继续被网络攻击者在野外利用。这个漏洞自2020年8月以来一直被人所知，它存在于登录过程中的一个密码漏洞中。详细地说，初始化向量(IV)始终被设置为所有0，而IV应该始终是一个随机数。

利用此漏洞，攻击者可以连接活动目录netlogon远程协议(MS-NRPC)并使用NTLM登录。

![](https://image.3001.net/images/20220819/1660875702_62fef3b6f3481bc380966.png!small)

## Log4Shell (CVE-2021-44228)

Log4Shell 是另一个在 2022 年成为头条新闻的漏洞。该漏洞影响流行的 Apache Java 日志库 Log4j，并于 2021 年 12
月发布。该日志库用于全球许多 Web 应用程序，因此，网络攻击者大量扫描它。

成功的发现 Log4Shell 会导致远程代码执行，在这种情况下，威胁者可以在服务器端下载并执行恶意负载。

![](https://image.3001.net/images/20220819/1660875710_62fef3beaa9a1edd4c376.png!small)

## VMware vSphere 客户端 (CVE-2021-21972)

远程执行代码漏洞的严重等级为 9.8，并于 2021 年 2 月在 VMware vSphere 客户端 (HTML5) 中发现。vSphere
是一种流行的虚拟化器，用于企业基础架构和内部网络。

内部威胁可以通过此漏洞在 443 端口上提升权限并执行远程命令。之后，该机器可以作为访问整个基础设施的跳板。

![](https://image.3001.net/images/20220819/1660875721_62fef3c9c593e7e6dfcff.png!small)

## PetitPotam (cve - 2021 - 36942)

PetitPotam 漏洞存在于 Windows 服务器中，其中 Active Directory 证书服务 (AD CS) 未配置针对 NTLM
中继攻击的保护。网络攻击者可以通过强制域控制器向他控制的 NTML 中继服务器进行身份验证来控制域控制器，然后它拦截流量并模拟客户端。

PetitPotam 可以通过安装KB5005413或确保允许 NTLM 身份验证的服务利用保护，例如身份验证扩展保护 (EPA或 SMB 签名等签名功能)
来修复。

![](https://image.3001.net/images/20220819/1660875730_62fef3d2a0bbe1d624a53.png!small)

“大型漏洞”听起来可能距离每个人很远，但它们正在成为现代网络危机的一个非常熟悉的特征。然而，企业仍然依靠传统技术来使做预防准备，是一个危险的信号。针对软件安全问题，企业通过将安全性构建到软件开发生命周期或
SDLC 中，在编码期间通过静态检测查找安全隐患，而不应该成为事后考虑的事项。

  

> 文章来源：
>
>
> [https://resources.infosecinstitute.com/](https://resources.infosecinstitute.com/topic/most-> dangerous-vulnerabilities-exploited/)

