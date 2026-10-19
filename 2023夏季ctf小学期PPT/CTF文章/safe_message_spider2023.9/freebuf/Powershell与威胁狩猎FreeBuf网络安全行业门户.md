**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

## Powershell简介

PowerShell是一种功能强大的脚本语言和shell程序框架，主要用于Windows计算机方便管理员进行系统管理并有可能在未来取代Windows上的默认命令提示符。PowerShell脚本因其良好的功能特性常用于正常的系统管理和安全配置工作，然而，这些特性被攻击者理解并转化为攻击特性，也就成为了攻击者手中的攻城利器，给企业网络造成威胁。

    
    
    百度百科解释：
    Windows PowerShell 是一种命令行外壳程序和脚本环境，使命令行用户和脚本编写者可以利用 .NET Framework的强大功能。
    它引入了许多非常有用的新概念，从而进一步扩展了您在 Windows 命令提示符和 Windows Script Host 环境中获得的知识和创建的脚本。
    Windows PowerShell v3将伴随着Microsoft Hyper-V 3.0和Windows Server 2012发布。PowerShell v3是一个Windows任务自动化的框架，它由一个命令行shell和内置在这个.NET框架上的编程语言组成。
    PowerShell v3采用新的cmdlet让管理员能够更深入到系统进程中，这些进程可以制作成可执行的文件或脚本（script）。一条cmdlet是一条轻量命令，Windows PowerShell运行时间在自动化脚本的环境里调用它。
    Cmdlet包括显示当前目录的Get-Location，访问文件内容的Get-Content和结束运行进程的Stop-Process。
    PowerShell v3在Windows Server 8中装载了Windows Management Framework 3.0。PowerShell运行环境也能嵌入到其它应用。
    

## Powershell版本特性

### PowerShell V2

PowerShell V2提供事件记录能力，可以协助蓝队进行相关的攻击事件推断和关联性分析，但是其日志记录单一，相关Post-Exploitation可做到无痕迹；并且因为系统兼容性，在后续版本攻击者都会尝试降级至此版本去躲避日志记录。

### PowerShell V3/V4

PowerShell V3/V4 相比之前提供了更全面的日志记录功能。Windows PowerShell 3.0 改进了对命令和模块的日志记录和跟踪支持。
自PowerShell
v3版本以后支持启用PowerShell模块日志记录功能，并将此类日志归属到了4103事件。PowerShell模块日志可以配置为记录所有的PowerShell模块的活动情况，包括单一的PowerShell命令、导入的模块、远程管理等。可以通过GPO进行启用模块日志记录。

### PowerShell V5

PowerShell
V5加入了CLM和ScriptBlock日志记录功能，能去混淆PowerShell代码并记录到事件日志。随着PowerShell攻击技术的不断成熟，攻击者为了规避防护和日志记录进行了大量的代码混淆，在执行代码之前很难发现或确认这些代码实际上会做些什么事情，给攻击检测和取证造成了一定的困难，因此微软从PowerShell5.0开始加入了日志转储、ScriptBlock日志记录功能，并将其归入到事件4104当中，ScriptBlock
Logging提供了在事件日志中记录反混淆的 PowerShell 代码的能力。

### PowerShell V6

PowerShell V6
出于功能需求，提供了更全面的系统覆盖能力。由于PowerShell在Linux和MacOS等操作系统上的支持在MacOS上安装（pwsh），处于安全性考虑日志记录作为必不可少的一部分，PowerShell使用本机os_log
API登录Apple的统一日志记录系统。在Linux上，PowerShell使用Syslog，微软将此上升成为一种几乎全平台支持的日志记录解决方案。

### PowerShell V7

PowerShell V7（PS7）基于.NET Core 3.0，Microsoft旨在提供与Windows
PowerShell模块更高的兼容性，高达90％。作为PowerShell
7的一部分，Microsoft在之前的日志记录基础上，增加了一种安全使用本地或远程存储中的凭据的方法，以便不需要将密码嵌入到脚本中。还将改进日志记录，以提供将本地计算机日志发送到远程设备的机制，而不管原始操作系统如何。

## Powershell日志

### Powershell审核策略

PowerShell安装完成之后，日志记录默认是不开启的，需要管理员用户手动开启日志记录功能。

> 1\. 按Win+R打开Windows运行窗口,在输入框里输入gepdit.msc,打开Windows本地组策略编辑器;
>
> 2\. 找到计算机配置/管理模板/Windows组件/Windows Powershell，根据需求打开右侧所需要的日志功能;

![image](https://image.3001.net/images/20210322/1616401749_60585555d0b90ff18dfea.jpeg!small)

### Powershell日志说明

事件ID| 关联| 审计| 笔记  
---|---|---|---  
400| 403| 始终记录，无论记录设置如何| 引擎状态从无更改为可用，记录任何本地或远程PowerShell活动的开始；  
403| 400| 始终记录，无论记录设置如何| 引擎状态从可用状态更改为停止，记录PowerShell活动结束。  
500| 501| 在profile.ps1中需要$ LogCommandLifeCycleEvent = $ true| 命令“Write-Host”已启动。  
501| 500| 在profile.ps1中需要$ LogCommandLifeCycleEvent = $ true| 命令“Write-Host”已停止。  
600| 500| 始终记录，无论记录设置如何| 记录类似“WSMan”等提供程序在系统上进行PowerShell处理活动的开始，比如”Provider
WSMan Is Started“；  
800| 500| ModuleLogging| 命令行的管道执行细节：写入主机测试。  
事件ID| 关联| 审计| 笔记  
---|---|---|---  
4100|  
|  
| PowerShell遇到错误时记录  
4103|  
| ModuleLogging| 执行管道  
4104|  
| ScriptBlockLogging| 执行远程命令 创建Scriptblock文本（1/1）： Write-Host
PowerShellV5ScriptBlockLogging  
40961|  
| 始终记录，无论记录设置如何| PowerShell控制台正在启动  
40962|  
| 始终记录，无论记录设置如何| PowerShell控制台已准备好进行用户输入  
  
## 简单的Powershell威胁狩猎

配置完Powershell审核策略后，我们可以进行一次简单的威胁狩猎来验证一下，通过Powershell模拟执行Get-process获取系统进程信息，然后观察Powershell日志能否记录此次测试行为。

![image](https://image.3001.net/images/20210322/1616401927_6058560795470e7dfc733.png!small)

    
    
    Powershell事件800
    命令行的管道执行详细信息: Get-process。
    
    上下文信息: 
     DetailSequence=1
     DetailTotal=1
    
     SequenceNumber=21
    
     UserId=DESKTOP-qianxin\liyang
     HostName=ConsoleHost
     HostVersion=5.1.18362.1171
     HostId=b48aff54-a9ca-4081-8cf8-427c6b414f3c
     HostApplication=C:\Windows\system32\WindowsPowerShell\v1.0\PowerShell.exe
     EngineVersion=5.1.18362.1171
     RunspaceId=1dfb0803-74a2-4eda-8235-555e5fcd474a
     PipelineId=6
     ScriptName=
     CommandLine=Get-process 
    
    详细信息: 
    CommandInvocation(Get-Process):“Get-Process”
    

通过上面的日志，我们可以看到Powershell可以清晰的记录模拟测试命令。那么我们大胆的推测一下，是否可以通过命令行行为监控在网内进行简单有效的威胁狩猎。

## 参考链接

> PowerShell在渗透测试的使用浅析  
> https://blog.csdn.net/weixin_45116657/article/details/103449931
>
> 围绕PowerShell事件日志记录的攻防博弈战(内含福利)  
> http://blog.nsfocus.net/attacks-defenses-powershell-event-logging/

