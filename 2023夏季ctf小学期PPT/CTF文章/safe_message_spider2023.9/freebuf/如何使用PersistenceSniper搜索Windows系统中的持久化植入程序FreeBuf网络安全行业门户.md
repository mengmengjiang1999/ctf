![](https://image.3001.net/images/20220921/1663765719_632b0cd70893a0e18426c.png!small)  

## 关于PersistenceSniper

PersistenceSniper是一款功能强大的PowerShell模块，该工具专为蓝队研究人员、安全应急事件响应人员和系统管理员设计，旨在帮助大家寻找Windows系统中的持久化植入程序。

该工具目前正在积极开发中，可能随时会更新，请确保在使用该工具前已升级到了最新版本。

## 支持检测的持久化技术

> [Run Key](https://attack.mitre.org/techniques/T1547/001/)
>
> [RunOnce Key](https://attack.mitre.org/techniques/T1547/001/)
>
> [Image File Execution
> Options](https://attack.mitre.org/techniques/T1546/012/)
>
> [Natural Language Development Platform 6 DLL Override
> Path](https://www.hexacorn.com/blog/2018/12/30/beyond-good-ol-run-key-> part-98/)
>
> [AEDebug Keys](https://www.hexacorn.com/blog/2013/09/19/beyond-good-ol-run-> key-part-4/)
>
> [Windows Error Reporting
> Debugger](https://www.hexacorn.com/blog/2019/09/20/beyond-good-ol-run-key-> part-116/)
>
> [Windows Error Reporting
> ReflectDebugger](https://www.hexacorn.com/blog/2018/08/31/beyond-good-ol-> run-key-part-85/)
>
> [Command Prompt AutoRun](https://persistence-> info.github.io/Data/cmdautorun.html)
>
> [Explorer Load](https://persistence-info.github.io/Data/windowsload.html)
>
> [Winlogon Userinit](https://attack.mitre.org/techniques/T1547/004/)
>
> [Winlogon Shell](https://attack.mitre.org/techniques/T1547/004/)
>
> [Windows Terminal
> startOnUserLogin](https://twitter.com/nas_bench/status/1550836225652686848)
>
> [AppCertDlls DLL Injection](https://attack.mitre.org/techniques/T1546/009/)
>
> [App Paths Hijacking](https://www.hexacorn.com/blog/2013/01/19/beyond-good-> ol-run-key-part-3/)
>
> [ServiceDll Hijacking](https://www.hexacorn.com/blog/2013/09/19/beyond-good-> ol-run-key-part-4/)
>
> [Group Policy Extensions DLLs](https://persistence-> info.github.io/Data/gpoextension.html)
>
> [Winlogon MPNotify](https://persistence-info.github.io/Data/mpnotify.html)
>
> [CHM Helper DLL](https://www.hexacorn.com/blog/2018/04/22/beyond-good-ol-> run-key-part-76/)
>
> [Hijacking of hhctrl.ocx](https://www.hexacorn.com/blog/2018/04/23/beyond-> good-ol-run-key-part-77/)
>
> [Startup Folder](https://attack.mitre.org/techniques/T1547/001/)
>
> [User Init Mpr Logon Script](https://attack.mitre.org/techniques/T1037/001/)
>
> [AutodialDLL Winsock
> Injection](https://www.hexacorn.com/blog/2015/01/13/beyond-good-ol-run-key-> part-24/)
>
> [LSA Extensions DLL](https://persistence-> info.github.io/Data/lsaaextension.html)
>
> [ServerLevelPluginDll DNS Server DLL Hijacking](https://persistence-> info.github.io/Data/serverlevelplugindll.html)
>
> [LSA Authentication Packages
> DLL](https://attack.mitre.org/techniques/T1547/002/)
>
> [LSA Security Packages DLL](https://attack.mitre.org/techniques/T1547/005/)
>
> [Winlogon Notify Packages
> DLL](https://attack.mitre.org/techniques/T1547/004/)
>
> [Explorer Tools Hijacking](https://www.hexacorn.com/blog/2017/01/18/beyond-> good-ol-run-key-part-55/)
>
> [.NET DbgManagedDebugger](https://www.hexacorn.com/blog/2013/09/19/beyond-> good-ol-run-key-part-4/)
>
> [cmd Hijacking](https://www.hexacorn.com/blog/2022/01/16/beyond-good-ol-run-> key-part-135/)
>
> [WMI Subscriptions](https://attack.mitre.org/techniques/T1546/003/)
>
> [Windows Services](https://attack.mitre.org/techniques/T1543/003/)
>
> [Terminal Services InitialProgram](https://persistence-> info.github.io/Data/tsinitialprogram.html)
>
> [Accessibility Tools
> Backdoor](https://attack.mitre.org/techniques/T1546/008/)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/last-byte/PersistenceSniper.git

## 工具使用

PersistenceSniper的使用非常简单，以管理员权限运行PowerShell，然后运行下列命令：

    
    
    PS C:\> git clone https://github.com/last-byte/PersistenceSniper
    
    PS C:\> Import-Module .\PersistenceSniper\PersistenceSniper\PersistenceSniper.psd1
    
    PS C:\> Find-AllPersistence

如果你想保持PersistenceSniper为PowerShell Galley中的最新版本，以管理员权限运行PowerShell，然后运行下列命令即可：

    
    
    PS C:\> Install-Module PersistenceSniper
    
    PS C:\> Import-Module PersistenceSniper
    
    PS C:\> Find-AllPersistence

如果你需要了解工具的所有参数和解释，可以在导入模块之后运行下列命令：

    
    
    Get-Help -Name Find-AllPersistence -Full

如果你想检测单个持久化技术，可以使用Find-AllPersistence的PersistenceMethod参数。比如说，你想通过Run和RunOnce注册表键来检测持久化植入程序，可以运行下列命令：

    
    
    PS C:\> Find-AllPersistence -PersistenceMethod RunAndRunOnce

![](https://image.3001.net/images/20220921/1663765881_632b0d7913e29a7064e85.gif)

PersistenceSniper的Find-AllPersistence会返回一个包含了PSCustomObject对象的数组，其中包含下列属性：

    
    
    $PersistenceObject = [PSCustomObject]@{
    
          'ComputerName' = $ComputerName
    
          'Technique' = $Technique
    
          'Classification' = $Classification
    
          'Path' = $Path
    
          'Value' = $Value
    
          'Access Gained' = $AccessGained
    
          'Note' = $Note
    
          'Reference' = $Reference
    
          'Signature' = Find-CertificateInfo (Get-ExecutableFromCommandLine $Value)
    
          'IsBuiltinBinary' = Get-IfBuiltinBinary (Get-ExecutableFromCommandLine $Value)
    
          'IsLolbin' = Get-IfLolBin (Get-ExecutableFromCommandLine $Value)
    
    }

此时我们就可以对输出进行格式化和过滤了。如果你想查看允许攻击者获取NT AUTHORITY\SYSTEM权限的持久化技术，可以运行下列命令：

    
    
    PS C:\> Find-AllPersistence | Where-Object "Access Gained" -EQ "System"

![](https://image.3001.net/images/20220921/1663765895_632b0d87c4321027c1b55.png!small)

当然了，由于PersistenceSniper是一款基于PowerShell的工具，我们还可以将其输出发送给Out-GridView来通过GUI界面进行交互：

![](https://image.3001.net/images/20220921/1663765905_632b0d913c6c5d035a0f2.png!small)

## 处理假阳性

PersistenceSniper在搜索持久化技术的时候，可能会出现误报的情况，因为很多合法软件也会使用其中的部分技术。为此，我们可以通过创建一个包含已知误报的CSV文件来解决这个问题。

这里我们可以使用Find-AllPersistence，配合其他参数，我们可以直接将查找到的输出保存到一个CSV文件中（或作为输入以对结果分类）：

    
    
    PS C:\> Find-AllPersistence -DiffCSV false_positives.csv

![](https://image.3001.net/images/20220921/1663765918_632b0d9e17334ce1959e7.png!small)

## 许可证协议

本项目的开发与发布遵循[ _CC0-1.0_](https://github.com/last-byte/PersistenceSniper/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **PersistenceSniper** ：【[ _GitHub传送门_](https://github.com/last-byte/PersistenceSniper)】

## 参考资料

> [
> _https://www.powershellgallery.com/packages/PersistenceSniper/1.0_](https://www.powershellgallery.com/packages/PersistenceSniper/1.0)
>
> [ _https://docs.microsoft.com/en-> us/sysinternals/downloads/autoruns_](https://docs.microsoft.com/en-> us/sysinternals/downloads/autoruns)
>
> [ _https://www.hexacorn.com/blog/2017/01/28/beyond-good-ol-run-key-all-> parts/_](https://www.hexacorn.com/blog/2017/01/28/beyond-good-ol-run-key-> all-parts/)
>
> [ _https://lolbas-project.github.io/_](https://lolbas-project.github.io/)
>
> [ _https://twitter.com/dottor_morte_](https://twitter.com/dottor_morte)

