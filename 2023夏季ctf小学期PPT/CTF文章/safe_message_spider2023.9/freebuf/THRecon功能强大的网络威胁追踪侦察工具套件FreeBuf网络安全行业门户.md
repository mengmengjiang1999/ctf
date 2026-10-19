**今天给大家介绍的是一款名叫THRecon的工具，该工具可以收集终端信息，而这些信息可以用来进行事件响应分类、威胁追踪和现场取证。当你的系统发出安全警报时，该工具可以给你提供尽可能多的相关分析信息，并帮助你确定是否发生了入侵行为。**

## 信息收集

**[Host Info](https://github.com/TonyPhipps/THRecon/wiki/Computer)** |
**[Processes](https://github.com/TonyPhipps/THRecon/wiki/Processes)*** |
**[Services](https://github.com/TonyPhipps/THRecon/wiki/Services)** |
**[Autoruns](https://github.com/TonyPhipps/THRecon/wiki/Autoruns)** |
**[Drivers](https://github.com/TonyPhipps/THRecon/wiki/Drivers)**  
---|---|---|---|---  
ARP | [DLLs](https://github.com/TonyPhipps/THRecon/wiki/DLLs)*  | EnvVars |
Hosts File | ADS  
[DNS](https://github.com/TonyPhipps/THRecon/wiki/DNS) | Strings* | [Users &
Groups](https://github.com/TonyPhipps/THRecon/wiki/GroupMembers) |
[Ports](https://github.com/TonyPhipps/THRecon/wiki/Ports) | [Select
Registry](https://github.com/TonyPhipps/THRecon/wiki/Registry)  
Hotfixes | Handles* | Sofware | Hardware | [Event
Logs](https://github.com/TonyPhipps/THRecon/wiki/EventLogs)  
Net Adapters | Net Routes | Sessions | Shares |
[Certificates](https://github.com/TonyPhipps/THRecon/wiki/Certificates)  
[Scheduled Tasks](https://github.com/TonyPhipps/THRecon/wiki/ScheduledTasks) |
TPM | Bitlocker | Recycle Bin | User Files  
  
* 数据主要从主机当前运行的进程和可执行文件中提取。

## 工具要求

1.要求Powershell 5.0及以上版本（扫描设备）。

2.要求Powershell 3.0及以上版本（目标系统）。

3.在没有psexec封装器（Invoke-THR_PSExec）的情况下扫描一台远程设备，则要求远程设备上开启WinRM服务。

## 快速安装

在Powershell中使用git命令进行安装，然后开启新的Powershell会话，安装命令如下：

    
    
    git clone https://github.com/TonyPhipps/THReconC:\Users\$env:UserName\Documents\WindowsPowerShell\Modules\THRecon

如果没有安装git的话，你可以新建一个文件夹，然后将项目源码拷贝到目录中，然后开启新的Powershell会话：

    
    
    mkdir C:\Users\$env:UserName\Documents\WindowsPowerShell\Modules\THRecon\

## 测试样例

如果你需要进行快速扫描，你需要在主机中创建一个空文件夹，然后在cmd中切换到该目录，默认输出结果会保存在当前目录中：

    
    
    mkdir c:\temp\
    
    cd c:\temp\
    
    Invoke-THR-Quick

## 问题解决

【[安装Powershell模块](https://msdn.microsoft.com/en-us/library/dd878350\(v=vs.85\).aspx)】

如果你的系统无法自动加载相关模块，你需要手动导入模块：

    
    
    cd C:\Users\$env:UserName\Documents\WindowsPowerShell\Modules\THRecon\
    
    Import-ModuleTHRecon.psm1

## 工具运行截图

"Invoke-THR"命令的输出结果：

![a.png](https://image.3001.net/images/20180712/15313952357442.png!small)

输出文件：

![b.png](https://image.3001.net/images/20180712/1531395241909.png!small)
***参考来源：[THRecon](https://github.com/TonyPhipps/THRecon)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

