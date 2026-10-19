##  背景

**PowerShell在过去的几年里在Offensive安全社区被广泛使用。但随着防御性安全行业的推进，正致使攻击性工具包从PowerShell迁移到反射C#以逃避现代安全产品的检测。其中一些改进包括脚本块记录，反恶意软件脚本接口（AMSI）以及第三方安全供应商针对恶意PowerShell活动签名的开发。目前已发布了多个C#工具包，如[Seatbelt](https://github.com/GhostPack/Seatbelt)，[SharpUp](https://github.com/GhostPack/SharpUp)和[SharpView](https://github.com/tevora-threat/SharpView)，用以攻击生命周期各个阶段的任务。而在攻击生命周期中缺少C#工具包的一个阶段就是持久性。为此，FireEye
Mandiant的红队创建了名为[SharPersist](https://github.com/fireeye/SharPersist)的新Windows持久性工具包。**

##  Windows 持久性

在红队参与中，需要花费大量的时间和精力来获得对组织的初始访问权限，因此以可靠的方式维护访问权限至关重要。持久性也是攻击生命周期中的关键组成部分，如下图所示。

![](https://image.3001.net/images/20190911/1568164082_5d7848f2796f0.png!small)

一旦攻击者在系统上建立了持久性，攻击者将可以在断电，重启或网络干扰后维持对系统的访问权。这允许攻击者在网络上长时间处于休眠状态，可能是几周、几个月甚至几年。建立持久性有两个关键组件：持久性植入和持久性触发，如下图所示。持久性植入是指恶意payload，例如可执行文件（EXE），HTML应用程序（HTA），动态链接库（DLL）
，或其他形式的代码执行。持久性触发是指恶意代码的执行，例如计划任务或Windows服务。有几种已知的持久性触发的方法可以在Windows上使用，例如Windows服务，计划任务，注册表和启动文件夹等。有关更完整的列表，请参阅[MITRE
ATT&CK persistence](https://attack.mitre.org/tactics/TA0003/)页面。

![](https://image.3001.net/images/20190911/1568164098_5d784902c7c19.png!small)

##  SharPersist 概述

SharPersist的创建是为了帮助使用多种不同的技术在Windows操作系统上建立持久性。它是一个用C#编写的命令行工具，可以反射性的加载Cobalt
Strike的“execute-assembly”命令或任何其他支持反射性加载.NET程序集的框架。SharPersist采用模块化设计，以便将来添加新的持久性技术。还有一些与tradecraft相关的项已经内置到该工具及其支持的持久性技术中，例如file
time stomping策略和最小化或隐藏运行应用程序。

SharPersist和所有相关的使用文档可以在[SharPersist FireEye
GitHub页面](https://github.com/fireeye/SharPersist)找到。

##  SharPersist 持久性技术

截至本文发表时，SharPersist支持的持久性技术及其所需的权限，如下表所示。

**技术** |  **描述** |  **技术开关名称（-t）** |  **是否需要管理权限？** |  **Touches 注册表？** |
**在磁盘上添加/修改文件？**  
---|---|---|---|---|---  
KeePass  |  Backdoor KeePass 配置文件  |  keepass  |  No  |  No  |  Yes  
New Scheduled Task  |  创建新的计划任务  |  schtask  |  No  |  No  |  Yes  
New Windows Service  |  创建新的 Windows 服务  |  service  |  Yes  |  Yes  |  No  
Registry  |  注册表键/值创建/修改  |  reg  |  No  |  Yes  |  No  
Scheduled Task Backdoor  |  后门现有的计划任务以及其他操作  |  schtaskbackdoor  |  Yes  |  No
|  Yes  
Startup Folder  |  在用户启动文件夹中创建 LNK 文件  |  startupfolder  |  No  |  No  |  Yes  
Tortoise SVN  |  创建 Tortoise SVN hook 脚本  |  tortoisesvn  |  No  |  Yes  |  No  
  
##  SharPersist 示例

在[SharPersist
GitHub](https://github.com/fireeye/SharPersist)上，有关于每种持久性技术的用法和示例的完整文档。下面将重点介绍一些技术。

**注册表持久性**

SharPersist中支持的注册表项的完整列表如下表所示。

**注册表项代码 （-k）** |  **注册表项** |  **注册表值** |  **是否需要管理权限？** |  **支持 Env 可选附加组件（-o
env）？**  
---|---|---|---|---  
hklmrun  |  HKLM\Software\Microsoft\Windows\CurrentVersion\Run  |  User
supplied  |  Yes  |  Yes  
hklmrunonce  |  HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce  |
User supplied  |  Yes  |  Yes  
hklmrunonceex  |  HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnceEx  |
User supplied  |  Yes  |  Yes  
userinit  |  HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon  |
Userinit  |  Yes  |  No  
hkcurun  |  HKCU\Software\Microsoft\Windows\CurrentVersion\Run  |  User
supplied  |  No  |  Yes  
hkcurunonce  |  HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce  |
User supplied  |  No  |  Yes  
logonscript  |  HKCU\Environment  |  UserInitMprLogonScript  |  No  |  No  
stickynotes  |  HKCU\Software\Microsoft\Windows\CurrentVersion\Run  |
RESTART_STICKY_NOTES  |  No  |  No  
  
在下面的示例中，我们将执行参数验证，然后添加注册表持久性。在添加持久性之前执行验证是最佳实践，因为它将确保你在实际添加相应的持久性技术之前具有正确的参数和其他安全性检查。下图中显示的示例在“HKCU\Software\Microsoft\Windows\CurrentVersion\Run”注册表项中创建名为“Test”的注册表值，其值为“cmd.exe/c
calc.exe”。

![](https://image.3001.net/images/20190911/1568164125_5d78491df0afd.png!small)

需要删除持久性，可以使用“-m
remove”参数，如下图所示。我们正在删除先前创建的“Test”注册表值，然后我们列出了“HKCU\Software\Microsoft\Windows\CurrentVersion\Run”的所有注册表值，以验证其是否已被成功删除。

![](https://image.3001.net/images/20190911/1568164146_5d7849325caaa.png!small)

**启动文件夹持久性**

在此示例中，我们将创建一个名为“Test.lnk”的LNK文件，该文件将放在当前用户的启动文件夹中，并将执行“cmd.exe/c
calc.exe”，如下图所示。

![](https://image.3001.net/images/20190911/1568164160_5d7849408801e.png!small)

同样，你可以使用“-m remove”参数删除启动文件夹持久性，如下图所示。这将从当前用户的启动文件夹中删除LNK文件。

![](https://image.3001.net/images/20190911/1568164174_5d78494e2498a.png!small)

**计划任务后门持久性**

可以将计划任务配置为一次执行多个操作，此技术将通过添加其他操作来后门后门现有的计划任务。我们需要做的第一件事就是查找一个用于后门的计划任务。在这本例中，我们将后门添加到了一个登录时运行的计划任务中，如下图所示。

![](https://image.3001.net/images/20190911/1568164188_5d78495c6608c.png!small)

一旦我们有了一个我们想要后门的计划任务，我们就可以执行dryrun以确保命令成功运行，然后实际执行该命令，如下图所示。

![](https://image.3001.net/images/20190911/1568164202_5d78496adcd48.png!small)

如下图所示，计划任务现在已被我们后门化。

![](https://image.3001.net/images/20190911/1568164215_5d7849772c9af.png!small)

同样，你可以使用“-m remove”参数持久性后门任务，如下图所示。

![](https://image.3001.net/images/20190911/1568164228_5d7849846ec96.png!small)

##  总结

在Offensive安全社区中，使用反射C#协助攻击生命周期的各个阶段是非常必要的，持久性也不例外。Windows提供了多种持久性技术，安全专家及其对手将继续发现和利用这些技术。

此工具旨在协助安全专家在攻击生命周期的持久性阶段。通过发布SharPersist，我们希望让人们能够了解Windows中可用的各种持久性技术，以及使用C#而不是PowerShell的方式使用这些持久性技术的能力。

 ***参考来源：[fireeye](https://www.fireeye.com/blog/threat-research/2019/09/sharpersist-windows-persistence-toolkit.html)，FB小编secist编译，转载请注明来自FreeBuf.COM**

