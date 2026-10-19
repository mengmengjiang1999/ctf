微软近期发现了一个总部设在黎巴嫩的攻击组织
POLONIUM。根据受害者与攻击工具的分析，微软认为其很有可能是由伊朗情报与安全部（MOIS）下属的攻击者运营的。并且，微软未发现该组织的攻击与过往黎巴嫩相关攻击组织有任何关联。自从
2020 年以来，有消息称伊朗正在从第三方代理人处开展网络攻击行动，以对抗归因指责。

在过去的三个月中，POLONIUM
组织已经攻击了二十余个以色列组织与一个在黎巴嫩开展业务的政府间合作组织。该攻击利用合法云服务（OneDrive）与受害者进行 C&C 通信。

## 攻击活动

自 2022 年 2 月以来，POLONIUM 主要针对以色列的制造业、信息技术行业和国防行业发起攻击。在一个案例中，发现 POLONIUM 将一个 IT
公司攻陷后利用其进行供应链攻击，攻击下游航空公司与律师事务所。该组织攻击的多个制造业公司也都是为以色列国防部门服务的。

这很符合伊朗攻击组织的攻击倾向，现在攻击者越来越倾向于瞄准服务提供商进行攻击，获取下游访问权限。

## 归因

微软以中等信心评估 POLONIUM 组织由伊朗情报和安全部（MOIS）负责运营：

> POLONIUM 攻击的目标很多都是 MERCURY 之前入侵的受害者，美国网络司令部认为 MERCURY 就是 MuddyWater
>
> 在部分受害者处，MOIS 为 POLONIUM 提供了过往攻击使用的访问权限，这可能是一种交接
>
> POLONIUM 与 Lyceum 都使用包括 OneDrive 在内的云服务进行数据泄露、命令控制
>
> POLONIUM 与 CopyKittens 都使用 AirVPN

## 滥用云服务

POLONIUM 利用云服务进行命令和控制以及数据泄露，微软在攻击中发现 POLONIUM 滥用 OneDrive 和
Dropbox。相关恶意软件被检测为：

> Trojan:PowerShell/CreepyDrive.A!dha
>
> Trojan:PowerShell/CreepyDrive.B!dha
>
> Trojan:PowerShell/CreepyDrive.C!dha
>
> Trojan:PowerShell/CreepyDrive.D!dha
>
> Trojan:PowerShell/CreepyDrive.E!dha
>
> Trojan:MSIL/CreepyBox.A!dha
>
> Trojan:MSIL/CreepyBox.B!dha
>
> Trojan:MSIL/CreepyBox.C!dha

尽管 OneDrive 会对所有上传的文件进行扫描，但 POLONIUM 并未使用 OneDrive
存储恶意软件，只是与合法用户相同的方式与云服务进行交互。

## CreepyDrive

CreepyDrive 利用 OneDrive 进行 C&C 通信，样本具备上传下载文件的基本功能。

CreepyDrive 的所有请求都使用 Invoke-WebRequest
cmdlet。该样本一旦运行，就会持续工作。但该样本不包含持久化机制，如果终止就需要攻击者手动重启。

CreepyDrive 其中缺少受害者标识符，研究人员猜测可能对不同的攻击目标使用了不同的样本，对应不同的 OneDrive 账户。

### 获取 OAuth 令牌

攻击者在样本中内置了 Refresh Token，这是 OAuth 2 规范的一部分，允许在过期后发布新的 OAuth Token。这种情况下，与
OneDrive 帐户相关的保护设置完全由威胁参与者控制。

通过 `https://login.microsoftonline.com/consumers/oauth2/v2.0/token`请求生成 OAuth
Token。

该请求是为恶意样本提供必要的 OAuth Token，以实现对 OneDrive 的交互。使用该 OAuth Token 就可以向 Microsoft
Graph API
请求（https://graph.microsoft.com/v1.0/me/drive/root:/Documents/data.txt:/content）访问
data.txt 文件。

data.txt 文件指示恶意程序要执行的任务，主要是三个分支。

#### Upload

响应中为 Upload
时，触发该分支。还需要包含两个信息：要上传的本地文件路径、攻击者自定义的远程文件名。请求结构为：`ttps://graph.microsoft.com/v1.0/me/drive/root:/Uploaded/???:/content`。

#### Download

响应中为 Download 时，触发该分支。通过 OneDrive
下载文件，请求结构为：`https://graph.microsoft.com/v1.0/me/drive/root:/Downloaded/???:/content`。

#### Execute

未响应任何指令时，将进入该分支。响应中可以包含要执行的命令数组或先前下载文件的文件路径。攻击者也可以使用单命令与文件路径的组合。

数组中的每个值都单独作为参数传递给以下自定义函数，该函数使用 Invoke-Expression cmdlet 运行命令：

![image.png-25.3kB](https://image.3001.net/images/20220609/1654744964_62a167841b63eb0cd3e01.png!small)自定义函数

每个命令的执行结果都会收集起来，发送到 OneDrive
上的以下位置：`https://graph.microsoft.com/v1.0/me/drive/root:/Documents/response.json:/content`。

执行期间，攻击者可以使用
`https://graph.microsoft.com/v1.0/me/drive/root:/Documents/data.txt:/content`请求重置原始文件
data.txt 中的内容。

最后，CreepyDrive 进入休眠，休眠结束后重新执行。

## CreepySnail

POLONIUM 组织使用了一个被检测为 `Backdoor:PowerShell/CreepySnail.B!dha`的自定义 PowerShell
程序。发现的 CreepySnail 的 C&C 服务器为：

> 135.125.147.170:80
>
> 185.244.129.79:63047
>
> 185.244.129.79:80
>
> 45.80.149.108:63047
>
> 45.80.149.108:80
>
> 45.80.149.57:63047
>
> 45.80.149.68:63047
>
> 45.80.149.71:80

下面的代码显示了 CreepySnail PowerShell 程序如何使用窃取的凭证进行身份验证并连接到 C&C 服务器。

![image.png-293.8kB](https://image.3001.net/images/20220609/1654744964_62a16784853b9941ddfac.png!small)CreepySnail
PowerShell 代码

## 公共工具的使用

POLONIUM 通过 OneDrive 下载了一个辅助程序 plink，这是一种常见的自动化交互式 SSH
工具。攻击者使用其在失陷主机与攻击基础设施间创建冗余隧道。观察到的用于 plink 隧道的 C&C 地址：

> 185.244.129.109
>
> 172.96.188.51
>
> 51.83 .246 .73

## 供应链攻击

POLONIUM 入侵了一家位于以色列的云服务提供商，使用服务商的访问权限来入侵下游客户，又入侵了以色列一家律师事务所和一家航空公司。利用 IT
产品和服务提供商入侵下游客户，仍然是伊朗攻击者的最爱。

## 参考来源

> [Microsoft](https://www.microsoft.com/security/blog/2022/06/02/exposing-> polonium-activity-and-infrastructure-targeting-israeli-organizations/)

