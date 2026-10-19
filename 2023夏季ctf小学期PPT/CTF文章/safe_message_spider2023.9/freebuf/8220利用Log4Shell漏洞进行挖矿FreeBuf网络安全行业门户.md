研究人员近日发现 8220 组织正在利用 Log4Shell 漏洞攻击 VMware Horizon
服务器，以便后续进行挖矿获利。受攻击的目标系统中包含韩国能源企业，由于系统存在漏洞且未打补丁，就被攻击者集火攻击。

Log4Shell（CVE-2021-44228）是 Java 日志程序 Log4j 的远程代码执行漏洞，攻击者可以通过使日志中包含远程 Java
对象来执行。

## 8220 团伙

8220 团伙是一个针对 Windows 与 Linux 系统进行攻击的组织，自从 2017 年以来一直保持活跃。如果成功入侵系统，8220
主要通过挖矿来进行获利。该团伙不局限于特定地域，而是针对全球发起攻击。此前，8220 也利用 Atlassian Confluence 服务器的漏洞
CVE-2022-26134 等进行攻击。

如果漏洞成功，攻击者会执行 PowerShell 命令来下载并执行后续的 PowerShell 脚本，最终安装门罗币矿机。

![image.png-230.9kB](https://image.3001.net/images/20230426/1682484300_6448ac4c842be1d35310e.png!small)利用
Atlassian Confluence 漏洞执行的 PowerShell 命令

Fortinet 的研究人员近日发现 8220 开始利用 Oracle Weblogic 服务器的漏洞安装 ScrubCrypt。ScrubCrypt
是使用 .NET 开发的恶意软件，也提供安装其他恶意软件的能力。通常来说，ScrubCrypt 最终会安装门罗币矿机，这也是 8220 团伙的最终目标。

![image.png-117.2kB](https://image.3001.net/images/20230426/1682484301_6448ac4d56f1c03d1e818.png!small)利用
Oracle Weblogic 漏洞攻击执行的 PowerShell 命令

研究人员确认，8220 团伙近期一直在利用 Oracle Weblogic 漏洞以及 Log4Shell 漏洞下载 ScrubCrypt，随后通过
ScrubCrypt 安装门罗币矿机。

## Log4Shell 攻击

自从 2021 年 12 月被披露以来，Log4Shell 漏洞已经被广泛利用。2022 年，Lazarus 组织也利用该漏洞发起攻击并传播
NukeSped 恶意软件。攻击者针对未打补丁的 VMware Horizon 中存在的 log4j
漏洞，该产品是用于远程工作与云基础架构的虚拟桌面解决方案。

分析日志发现，ws_tomcatservice.exe 进程安装了 8220 团伙使用的门罗币矿机。

![image.png-104.5kB](https://image.3001.net/images/20230426/1682484302_6448ac4e30b2cddab4a48.png!small)通过
ws_tomcatservice.exe 进程执行的 PowerShell 命令

没有完整的网络数据包，但从 VMware Horizon 的 ws_tomcatservice.exe 进程执行 PowerShell 命令与 8220
团伙常用的攻击方式来看，很可能是通过 Log4Shell 漏洞实现的攻击。

![image.png-126.1kB](https://image.3001.net/images/20230426/1682484303_6448ac4f077aa66163c0f.png!small)PowerShell
命令执行日志

## ScrubCrypt 与 XMRig CoinMiner 分析

![image.png-318.7kB](https://image.3001.net/images/20230426/1682484303_6448ac4fc43140f6b19df.png!small)恶意软件进程树

利用 Log4Shell 漏洞攻击下载并执行的 PowerShell 脚本，脚本文件名为
bypass.ps1。尽管恶意软件的代码有所不同，但文件名称与功能基本类似。

![image.png-851.2kB](https://image.3001.net/images/20230426/1682484305_6448ac510f3d764debe09.png!small)bypass.ps1
PowerShell 脚本

bypass.ps1 是带混淆的 PowerShell 脚本，简单去混淆后如下所示：

![image.png-305.7kB](https://image.3001.net/images/20230426/1682484306_6448ac52d59dfe0f830c4.png!small)PowerShell
脚本

脚本首先绕过 AMSI，随后在 %TEMP%PhotoShop-Setup-2545.exe 路径中创建并执行内嵌的恶意软件。PhotoShop-Setup-2545.exe 是由 .NET 开发的 Downloader 类恶意软件，会下载恶意代码并将其注入 RegAsm.exe。

![image.png-326kB](https://image.3001.net/images/20230426/1682484307_6448ac53af85743dba597.png!small).Net
恶意软件

在 RegAsm.exe 进程中注入并执行的恶意软件经过混淆处理，但与 Fortinet 研究ScrubCrypt 的相似性来看，很可能是
ScrubCrypt 类型的恶意软件。用于攻击的 ScrubCrypt 中包含 3 个 C&C 的 URL 与 4
个端口（58001、58002、58003 和 58004）。

![image.png-687.5kB](https://image.3001.net/images/20230426/1682484308_6448ac549bce295fca222.png!small)ScrubCrypt（RegAsm.exe）的
C&C URL

ScrubCrypt 连接到 C&C 服务器并下载其他恶意代码，实际中也发现了安装门罗币矿机的命令。

![image.png-172.9kB](https://image.3001.net/images/20230426/1682484310_6448ac562c29f0916e1d3.png!small)安装
XMRig CoinMiner 的 PowerShell 命令

deliver1.exe 是用于下载并执行注入的恶意软件，将 ScrubCrypt 保存在 MSBuild.exe 的内部资源中。该 ScrubCrypt
中包含 2 个 C&C URL 与 4 个端口号（9090、9091、9092 和 8444）。

![image.png-668.1kB](https://image.3001.net/images/20230426/1682484311_6448ac5710bd7efb5cbd6.png!small)ScrubCrypt（MSBuild.exe）的
C&C URL

![image.png-165kB](https://image.3001.net/images/20230426/1682484312_6448ac5834d670e00fb80.png!small)恶意软件下载

ScrubCrypt 会在注册表中增加：执行矿机时使用的配置数据（注入目标进程、矿池地址、钱包地址与矿机下载地址）、数据文件
plugin_3.dll、plugin_4.dll。

![image.png-648.5kB](https://image.3001.net/images/20230426/1682484313_6448ac593a737299e4dce.png!small)注册表数据

plugin_4.dll 是一种经过编码的 .NET 恶意软件，其主要功能是解码 plugin_3.dll 文件。释放矿机，并将 plugin_3.dll
注入指定的良性进程 AddInProcess.exe。

![image.png-740kB](https://image.3001.net/images/20230426/1682484314_6448ac5a5a0f703d2f174.png!small)矿机注入的配置数据

攻击者的门罗币钱包地址与之前发现针对 Atlassian Confluence 漏洞攻击、针对 Oracle Weblogic
漏洞攻击中所使用的门罗币地址相同，8220 团伙一直使用相同的钱包地址。

## 结论

8220 团伙针对未打补丁的系统发起攻击，安装门罗币矿机进行挖矿获利。该组织不仅针对存在漏洞的 Atlassian Confluence
发起攻击，也针对存在 Log4Shell 漏洞的 VMware Horizon 发起攻击。

## IOC

> d63be89106d40f7b22e5c66de6ea5d65  
> 2748c76e21f7daa0d41419725af8a134  
> 851d4ab539030d2ccaea220f8ca35e10  
> bd0312d048419353d57068f5514240dc  
> hxxp://163.123.142[.]210/bypass.ps1  
> hxxp://77.91.84[.]42/bypass.ps1  
> hxxp://77.91.84[.]42/Whkpws.png  
> hxxp://77.91.84[.]42/deliver1.exe  
> hxxp://77.91.84[.]42/plugin_3.dll  
> hxxp://77.91.84[.]42/plugin_4.dll  
> 179.43.155[.]202  
> su-95.letmaker[.]top  
> su95.bpdeliver[.]ru  
> 174.138.19[.]0:8080

## 参考来源

> [Ahnlab](https://asec.ahnlab.com/en/51568/)

