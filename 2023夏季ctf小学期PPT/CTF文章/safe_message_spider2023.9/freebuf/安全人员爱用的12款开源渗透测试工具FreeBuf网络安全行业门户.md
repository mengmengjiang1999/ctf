回顾过去，黑客入侵异常困难，需要大量手动操作。然而，如今，一套自动化测试工具让渗透测试人员变身“半机械人”，能够比以往任何时候都更轻松地完成更多测试。以下12款开源渗透测试工具，可以帮助渗透测试人员更快、更好、更智能地完成工作。

![](https://image.3001.net/images/20230725/1690280476_64bfa21c4b7d5be7ea044.jpg!small)

## AutoFunkt

AutoFunkt是一个Python脚本，用于从Cobalt Strike可扩展的C2配置文件中自动创建无服务器云重定向器。

> 传送门：https://github.com/RedSiege/AutoFunkt

## C2concealer

C2concealer是一个命令行工具，可以生成随机的C2可扩展配置文件以在Cobalt Strike中使用。

> 传送门：https://github.com/RedSiege/C2concealer

## Dig Dug

Dig
Dug的工作原理是将字典中的单词附加到可执行文件中。该字典被重复附加，直到达到最终所需的可执行文件大小。一些AV和EDR引擎可能会测量熵来确定可执行文件是否值得执行。其他供应商工具会检查可执行文件是否有空字节填充的迹象。

> 传送门：https://github.com/RedSiege/DigDug

## dumpCake

dumpCake会将密码身份验证尝试转储到SSH守护进程。每个SSHD子进程都将附加到该进程，并且在该进程完成时，尝试的密码和连接日志将转储到脚本中。

> 传送门：https://github.com/brandonscholet/dumpCake

## EyeWitness

EyeWitness截取网站屏幕截图，收集服务器标头信息，并在可能的情况下识别默认凭据。在大型测试中，该工具可以为渗透测试人员的网站分类工作节省大量时间。渗透测试人员经常在筛选一长串网站时使用此工具。

> 传送门：https://github.com/RedSiege/EyeWitness

## EDD-Enumerate Domain Data

EDD（Enumerate Domain
Data）的设计类似于PowerView，但它在.NET环境中运行。PowerView本质上是终极域枚举工具。该工具在很大程度上是通过查看现有项目中不同功能的实现并将它们组合到EDD中来实现的。

> 传送门：https://github.com/RedSiege/EDD

## GPP Deception

GPP
Deception脚本生成一个groups.xml文件，能模仿真实的GPP，以便在加入域的计算机上创建新用户。蓝队测试人员可以将此文件用作蜜源文件。通过监控对蜜源文件的访问，蓝队可以检测渗透测试人员或恶意行为者横向移动时扫描的包含用户名和cpasswords的GPP文件。

> 传送门：https://github.com/RedSiege/GPPDeception

## Just-Metadata

Just-Metadata是一个收集和分析有关IP地址元数据的工具。它试图在一个大型数据集中找到系统之间的关系。它被用于被动地收集大量IP地址相关情报信息，并试图推断出其中的隐藏关系。

> 传送门：https://github.com/RedSiege/Just-Metadata

## ProxmarkWrapper

ProxmarkWrapper是一个围绕Proxmark3客户端的wrapper，如果捕获到RFID卡，它将发送文本警报和/或电子邮件。

> 传送门：https://github.com/RedSiege/ProxmarkWrapper

## Wappybird

Wappybird是一个多线程Wappalyzer
命令行工具，用于查找Web技术，具有可选的CSV输出。用户还可以设置一个目录，将所有抓取的数据保存在每个主机的子文件夹中。

> 传送门：https://github.com/brandonscholet/wappybird

## WMIplant

WMImplant是一个基于PowerShell的工具，它利用WMI对目标计算机执行操作，同时也作为发出命令和接收结果的C2通道。WMImplant需要目标计算机上的本地管理员权限。

> 传送门：https://github.com/RedSiege/WMImplant

## WMIOps

WMIOps是一个powershell脚本，它使用WMI在Windows环境中的本地或远程主机上执行各种操作。它主要用于渗透测试或红队交战。

> 传送门：https://github.com/RedSiege/WMIOps

原文链接：

<https://www.helpnetsecurity.com/2023/07/18/open-source-penetration-testing-tools/>

