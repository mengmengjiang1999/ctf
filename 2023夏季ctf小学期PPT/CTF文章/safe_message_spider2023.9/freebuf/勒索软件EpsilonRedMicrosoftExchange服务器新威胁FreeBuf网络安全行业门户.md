虽然Microsoft Exchange针对存在的代码漏洞一直更新补丁，但这并未能阻止网络黑客停手。最新发现，一种自称为 Epsilon
Red的新型勒索软件，利用Microsoft Exchange服务器的系统漏洞对网络上的机器进行加密。在进入加密阶段之前，Epsilon
Red勒索软件依赖于十几个脚本，同时还使用一个商业远程桌面实用程序。

### 易受攻击的Microsoft Exchange服务器

网络安全公司在调查一家遭到网络攻击的美国公司时，发现勒索软件Epsilon Red通过利用本地Microsoft
Exchange服务器中未修补的漏洞实施入侵。经分析，攻击者可能利用ProxyLogon的一系列漏洞发起攻击。ProxyLogon系统漏洞已被网络黑客频繁利用，虽然92%易受攻击的Microsoft
Exchange服务器针对代码漏洞都进行了更新，但这并没能阻止网络黑客继续实施破坏。

### 独特的工具套装

Epsilon Red是用Golang
(Go)代码语言编写，前面有一组独特的PowerShell脚本，这些脚本为文件加密程序做准备，每个脚本都有特定的用途：

终止进程和服务安全工具、数据库备份程序，Office 应用程序，电子邮件客户端

删除卷影副本

窃取包含密码哈希值的安全帐户管理器 (SAM) 文件

删除 Windows 事件日志

禁用 Windows Defender

暂停进程

卸载安全工具(Sophos、Trend Micro、Cylance、MalwareBytes、Sentinel One、Vipre、Webroot)

扩展系统权限

大多数脚本编号为 1 到 12，但也有少数以单个字母命名。其中之一，c.ps1，似乎是渗透测试工具Copy-VSS的克隆。

![](https://image.3001.net/images/20210602/1622603727_60b6f7cf21450b27f58d0.png!small)

图：Epsilon Red 勒索软件使用的 PowerShell 脚本

在攻破网络后，黑客通过RDP访问计算机，并使用Windows Management Instrumentation (WMI) 安装软件并运行
PowerShell 脚本，最终部署 Epsilon Red 可执行文件。他们还安装了一个远程实用程序(Remote Utilities)的副本和Tor
Browser，此举是为了确保他们在无法通过初始入口进入时仍有备用入口。

![](https://image.3001.net/images/20210602/1622603740_60b6f7dc094a7a6b06fc9.png!small)

图：EpsilonRed 勒索软件安装 Remote Utilities 软件

### REvil 赎金票据模型

尽管这个版本的Epsilon Red看起来不够专业，但它对文件类型和文件夹进行加密没有限制。此外，它还包含来自开源工具 godirwalk
的代码，godirwalk 是一个用于遍历文件系统上的目录树的库。此功能使Epsilon
Red能够扫描硬盘驱动器，并将目录路径添加到子进程的目标列表中，这些子进程分别对子文件夹进行加密，最后，受感染的机器会运行大量勒索程序副本。它会加密目标文件夹中附加后缀“.epsilonred”的所有内容，而不保留可能破坏基本程序，甚至操作系统的可执行文件或DLL。

同典型勒索方式，Epsilon Red会在每个处理过的文件夹中放上赎金说明，告知如何联系攻击者以协商数据解密价格。这份赎金说明是REvil
勒索软件赎金说明的改进版本，Epsilon Red努力纠正原始语法和拼写错误。

![](https://image.3001.net/images/20210602/1622603772_60b6f7fcaa946562edef3.png!small)

图：Epsilon Red 使用修改后的REvil赎金票据

尽管 Epsilon
Red是勒索软件行业的新手，但他们已攻击多家公司并赚取一定赎金，该勒索软件威胁的一名受害者在5月15日向攻击者支付了4.28比特币(约21万美元)。

![](https://image.3001.net/images/20210602/1622603789_60b6f80d928994846fe04.png!small)

虽然网络技术趋于成熟，但这并不代表系统中存在的漏洞及背后代码编写同样完美。黑客们抓住任何一个漏洞出现的机会破坏系统发出勒索。网络技术需要安全稳健发展，在不断更新技术手段的同时，也要加强网络安全建设。软件安全是网络安全最基础的防线，加强软件安全，在软件开发阶段引入代码静态检测等手段，结合交付阶段的安全测试，可以有效降低系统漏洞，在完善软件功能的同时保障软件安全。

