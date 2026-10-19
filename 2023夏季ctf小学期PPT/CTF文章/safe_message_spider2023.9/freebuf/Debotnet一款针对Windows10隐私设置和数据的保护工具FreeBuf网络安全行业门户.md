![](https://image.3001.net/images/20200801/1596281285.png!small)

## Debotnet

Debotnet是一款针对Windows10隐私设置和数据的保护工具，Debotnet本质上是一个免费的可移植工具，它可以帮助我们控制和管理Windows
10中跟隐私相关的配置，并保证用户的个人数据安全性。

实际上，如果你想要保护你的隐私数据时，你就会发现Windows10的默认隐私设置还是有很多可以改进的地方。每当我们在为家庭或工作环境设置新的电脑或更新当前设置时，我们总是需要花时间去仔细检查安装配置过程中的每一个隐私设置，并尽可能地确保我们的隐私信息得到最好的安全保护。

在保护用户隐私信息上，Windows
10还是存在很多不足之处的，因为系统内嵌入了很多遥测功能和在线功能，这些功能会将用户的数据（无论敏感或是不敏感的数据）发送给微软，而且这些功能还无法被禁用，这也就意味着微软能够做到以下几件事情：

> 在未经用户同意的情况下，在用户计算机中运行软件；
>
> 在未经用户同意的情况下，获取用户计算机中的数据；
>
> 在未经用户同意的情况下，删除用户计算机中的软件或数据文件；

基于上述这些行为，我们把Windows 10暂且定义为恶意软件肯定不为过，更确切地说，可以算是一种僵尸网络了。

## 功能介绍

> 禁用那些会将用户数据发送给微软的Windows遥测和在线功能；
>
> 选择需要禁用的功能；
>
> Dobotnet能够显示所有配置信息，允许用户实现完整控制；
>
> 简单的脚本引擎，允许用户添加自定义隐私规则；
>
> 支持调试模式和测试模式；
>
> GitHub库定期更新脚本；
>
> 支持[Ninite](https://ninite.com/)服务，允许我们下载和安装超过70款热门Windows应用程序；
>
> 支持[Chocolatey](https://chocolatey.org/)软件，包含超过4000款应用包；
>
> 支持通过命令行和Microsoft Media Creation Tool来下载Windows 10 ISO文件；
>
> 整合了自定义PowerShell脚本，例如[W4RH4WK / Debloat-> Windows-10](https://github.com/W4RH4WK/Debloat-Windows-10)、[Sycnex /
> Windows10Debloater](https://github.com/Sycnex/Windows10Debloater)；
>
> 下载已被弃用的Windows App；
>
>
> 提供了高级且用户友好的GUI界面，支持[主题配置](https://github.com/mirinsoft/debotnet/blob/master/themes/theme.md)；
>
> 无需安装，便携可移植；

## 工具使用

正如上文介绍的那样，Debotnet的主要工具都不是硬编码的。Debotnet基于简单的.DS1文件，它精确地定义了哪些注册表项、文件和/或/服务应该被程序禁用、阻止、删除等。这些脚本文件允许您执行命令行工具和参数以及简单的PowerShell代码。

## 使用样例

    
    
    [Info]
    
    ID=No more forced updates
    
    Ver=1.0
    
    Desc=This will notify when updates are available, and you decide when to install them.\n\nThe values added to registry with this script will prevent forced updates.
    
    Dev=Federico Dossena
    
    DevURL=https://github.com/adolfintel/Windows10-Privacy
    
    WinVer=Compatible with Windows 10
    
    Evaluation=Recommended
    
    EvaluationColor=009e5e
    
    [Code]
    
    Task1=Try,query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v NoAutoUpdate,STDOUT
    
    Task2=Try,query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v AUOptions,STDOUT
    
    Task3=Try,query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v ScheduledInstallDay,STDOUT
    
    Task4=Try,query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v ScheduledInstallTime,STDOUT
    
    File5=Reg,add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v NoAutoUpdate /t REG_DWORD /d 0 /f,STDOUT
    
    File6=Reg,add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v AUOptions /t REG_DWORD /d 2 /f,STDOUT
    
    File7=Reg,add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v ScheduledInstallDay /t REG_DWORD /d 0 /f,STDOUT
    
    File8=Reg,add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v ScheduledInstallTime /t REG_DWORD /d 3 /f,STDOUT

## 工具下载

Dev站点最新稳定版：【[点我下载](https://www.mirinsoft.com/debotnet)】

GitHub库最新稳定版：【[点我下载](https://github.com/mirinsoft/debotnet/releases)】

Chocoletey Release：【[点我下载](https://chocolatey.org/packages/debotnet)】

Nightly：【[点我下载](https://www.mirinsoft.com/debotnet-nightly)】

## 项目地址

Debotnet：【[GitHub传送门](https://github.com/builtbybel/debotnet)】

