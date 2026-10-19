![](https://image.3001.net/images/20210321/1616312829_6056f9fd119fc2a2fe4ba.png!small)

## 漏洞信息

 **受影响产品：** ILEX International Sign&go 7.1.2 build 201804160953

ILEX International Sign&go是一个ILEX
International的模块化全球SSO解决方案，它可以通过公共体系结构和管理给广大用户提供强大的身份验证、Web访问管理、移动访问管理、身份联合功能。

 **漏洞类型：** 本地权限提升

 **漏洞编号：** CVE-2020-23968

 **漏洞概述：** 由于对日志目录的访问权限过高，ILEX International
Sign&Go软件可能被滥用以执行特权文件操作，例如创建任意文件。攻击者将能够利用该漏洞通过特权Sign&Go进程上的DLL劫持来获取本地计算机上的SYSTEM权限。此漏洞已在最新版本中修补，用户应更新到最新版本。

## 漏洞发现

在Windows笔记本电脑上执行安全审计时，我通常都会去检查一下常见的提权漏洞，即使用Procmon工具（Sysinternals开发）来分析已安装的非系统应用程序的行为。

在最近的一次安全审计活动中，我查看了Procmon输出，并且发现Sign&go进程正在写入C:\ProgramData目录中的日志文件：

![](https://image.3001.net/images/20210321/1616312856_6056fa18e3cedafb55a0f.png!small)

除此之外，我还发现这里存在大量DLL劫持的机会，攻击者可以利用其来实现持久化操作：

![](https://image.3001.net/images/20210321/1616312866_6056fa2280c07239d1218.png!small)

上述进程实际上是一个服务，服务会跟随系统自动启动，并且具备SYSTEM权限：

![](https://image.3001.net/images/20210321/1616312884_6056fa3406c6b70ee5006.png!small)

![](https://image.3001.net/images/20210321/1616312892_6056fa3c07563f0af58ab.png!small)

![](https://image.3001.net/images/20210321/1616312900_6056fa441039bb0cd1c95.png!small)

![](https://image.3001.net/images/20210321/1616312908_6056fa4cb66e287ea3ad7.png!small)

服务的源码位于路径“C:\Program Files\Sign and go 7.1 Workstation Security
Suite\sngWSService.exe”：

![](https://image.3001.net/images/20210321/1616312917_6056fa558018502e3f08e.png!small)

而且代码已经经过了数字签名：

![](https://image.3001.net/images/20210321/1616312925_6056fa5da5e0f6d2df1d3.png!small)

![](https://image.3001.net/images/20210321/1616312934_6056fa66db078977b5fb8.png!small)

![](https://image.3001.net/images/20210321/1616312943_6056fa6f4e585228512b4.png!small)

## 目录访问权限分析

检查了“C:\ProgramData\Ilex\S&G\Logs”目录的权限之后，我们发现它的权限是从“C:\ProgramData”那里继承的：

![](https://image.3001.net/images/20210321/1616312954_6056fa7a6eabc866dfd48.png!small)

![](https://image.3001.net/images/20210321/1616312962_6056fa8296cc7502781a6.png!small)

所以说，对于一名普通用户，或企业环境下的用户，只要经过身份认证即可拥有“C:\ProgramData\Ilex\S&G\Logs”目录的读写权限。

## 漏洞分析

我们已经拥有了一个以SYSTEM权限运行的Windows服务了，接下来我们就可以对用户控制的文件和目录去执行各种操作了。

这里我们使用了多种技术来利用Windows文件系统的功能，研究人员James Forshaw已经开发并发布了一款名为【[
_符号链接测试工具集_](https://github.com/googleprojectzero/symboliclink-testing-tools)】的研究工具，仅供研究人员进行漏洞利用概念验证。

在本例中，我将使用对象管理器符号链接来利用该漏洞，因为没有权限的用户可以在Windows对象管理器中创建符号链接，以便将权限升级到系统。作为非特权用户，我们可以将解析到\RPC
Control\目录的装载点与该目录中的对象管理器符号链接连接起来：

![](https://image.3001.net/images/20210321/1616312973_6056fa8d79d0fd74cc744.png!small)

## 漏洞利用链

为了利用该漏洞，我们需要做到下列几件事情：

> 删除“C:\ProgramData\Ilex\S&G\Logs”中的所有文件。
>
>
> 创建一个名为“C:\ProgramData\Ilex\S&G\Logs\000-sngWSService1.log”的指向“C:\Windows\System32\pwned.dll”的伪符号连接。由于服务可以写入“000-sngWSService[1-2].log”，所以在利用该漏洞时，首先要检测该服务所使用的文件。
>
> 普通用户不允许重启服务来实现文件写入操作，但是，如果计算机断网的话，服务将会开始向日志文件中写入错误消息。因此，我们的第三步操作可以是断开网络连接。

上述步骤将会使用符号链接技术来将日志文件上的文件写入操作转移到攻击者选择的任意文件：

![](https://image.3001.net/images/20210321/1616312985_6056fa997bf10b74553f0.png!small)

## 漏洞利用

我们已经编写了PowerShell和C++版本的漏洞利用PoC代码了，大家可以点击【[这里](https://github.com/ricardojba/CVE-2020-23968-ILEX-SignGo-EoP)】获取。

 **PowerShell漏洞利用执行结果：**

![](https://image.3001.net/images/20210321/1616313004_6056faac5a4d1b9c56604.png!small)

参考资料

> [ _https://github.com/googleprojectzero/symboliclink-testing-> tools_](https://github.com/googleprojectzero/symboliclink-testing-tools)
>
> [ _https://github.com/Hood3dRob1n/Y.A.S.P./blob/master/payloads/reverse-> dll/reverse_dll.c_](https://github.com/Hood3dRob1n/Y.A.S.P./blob/master/payloads/reverse-> dll/reverse_dll.c)
>
> [ _https://github.com/ricardojba/CVE-2020-23968-ILEX-SignGo-> EoP_](https://github.com/ricardojba/CVE-2020-23968-ILEX-SignGo-EoP)
>
> [
> _https://troopers.de/downloads/troopers19/TROOPERS19_AD_Abusing_privileged_file_operations.pdf_](https://troopers.de/downloads/troopers19/TROOPERS19_AD_Abusing_privileged_file_operations.pdf)

