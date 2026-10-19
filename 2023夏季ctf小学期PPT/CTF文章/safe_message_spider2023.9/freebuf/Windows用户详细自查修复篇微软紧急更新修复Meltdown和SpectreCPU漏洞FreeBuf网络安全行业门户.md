***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**1月3日深夜，微软发布了针对Meltdown和Specter的系统安全更新，而两个安全漏洞影响了几乎所有自1995年以来发布的CPU（不止Intel）。根据微软的安全建议来看，这些
Windows 安全更新能够解决了各种Windows 发行版中的Meltdown和Spectre漏洞。**  

操作系统|  **更新 KB**  
---|---  
Windows Server, version 1709 (Server Core Installation)|
[4056892](https://support.microsoft.com/en-us/help/4056892)  
Windows Server 2016| [4056890](https://support.microsoft.com/en-us/help/4056890)  
Windows Server 2012 R2 | [4056898](https://support.microsoft.com/en-us/help/4056898)  
Windows Server 2012| 暂不可用  
Windows Server 2008 R2 | [4056897](https://support.microsoft.com/en-us/help/4056897)  
Windows Server 2008 | 暂不可用  
  
 **其他系统版本见[ADV180002](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV180002)**

但这次的微软更新并非是全面修复。部分 Windows PC 可能还需要额外的 CPU固件更新来防范 **Spectre 攻击** ，不过
Microsoft的安全更新似乎完全解决了 **Meltdown 漏洞** 。  

目前用户在进行更新时似乎还遇到了其他问题，Meltdown 和 Spectre **安全更新** 似乎与 **反病毒软件们** 相处得并不融洽。

![intel-processor.jpg](https://image.3001.net/images/20180105/15151231313937.jpg!small)  

微软在安全补丁的兼容性说明中表示，

> 在我们的测试过程中，我们发现一些第三方应用程序已经对 Windows
> 内核内存进行了不受支持的调用，导致了蓝屏错误的发生。而这些调用导致的蓝屏错误会让设备无法boot。
>
>
> 为了防止出现这个问题，目前我们只对运行合作伙伴厂商的反病毒软件用户提供安全更新。是用其他AV产品的用户可以耐心等待，并与反病毒软件厂商跟进沟通，是否支持微软补丁。

 **目前安全研究员对于反病毒软件的兼容性制作了调查表【[Google
Sheet](https://docs.google.com/spreadsheets/d/184wcDt9I9TUNFFbsAVLpzAtckQxYiuirADzf3cL42FQ/edit#gid=0)】，用户也可以查询此表了解自己使用的反病毒软件的兼容情况。**

## Windows 用户更新指南如下

以下内容是Windows用户可以用来自查和进行安全更新的具体操作内容。

如果需要查看微软官方的告示【帮助页面】，主要是这四个页面：

> 1）[Windows桌面用户指南](https://support.microsoft.com/en-us/help/4073119/protect-> against-speculative-execution-side-channel-vulnerabilities-in)
>
> 2）[Windows Server用户指南](https://support.microsoft.com/en-> us/help/4072698/windows-server-guidance-to-protect-against-the-speculative-> execution)
>
> 3）微软安全建议 [ADV180002](https://portal.msrc.microsoft.com/en-US/security-> guidance/advisory/ADV180002)（包含更新软件包的KB编号）
>
> 4）更新第三方防病毒软件用户的[兼容性警告内容](https://support.microsoft.com/en-> us/help/4072699/important-information-regarding-the-windows-security-> updates-released)

## 反病毒软件兼容性判断

如果用户在自己系统的Windows更新功能中看到“检查更新”有新内容，则可以进行安装。不同的系统会有不同的补丁KB编号，主要是系统和硬件平台差别导致的。如果没有新内容出现，则意味着Windows检查到改用户的电脑上存在不兼容的
**反病毒软件** ！

微软表示他们已经在和各种厂商进行了沟通，部分不兼容的产品需要创建一个注册表项目，确保不会在本次安全更新后系统崩溃。

>
> **但在本次补丁安装时，系统会自动检测注册表项是否存在；如果键值存在，Windows更新进程才会相信反病毒软件已经得到更新，可以兼容补丁，系统才能正确更新。——这里就是问题点！**

部分厂商表示他们 **不打算** 创建这个注册表值，
**[部分厂商](https://docs.google.com/spreadsheets/d/184wcDt9I9TUNFFbsAVLpzAtckQxYiuirADzf3cL42FQ/edit#gid=0)**
表示自己无法在 **“技术上”** 实现，其他厂商则在之后的几天内会将自己的AV产品更新，满足要求。

所以，如果用户使用的反病毒软件不巧处在 **“无法添加注册表项** ”的一类中，可以通过如下步骤实现更新：

 **请在再三确认自己的厂商是否兼容，不兼容的话，我们才建议使用这个 .reg 文件！**

    
    
    Key="HKEY_LOCAL_MACHINE" Subkey="SOFTWARE\Microsoft\Windows\CurrentVersion\QualityCompat" Value="cadca5fe-87d3-4b96-b7fb-a231484277cc" Type="REG_DWORD”  
    

运行文件或者手动添加注册表项后，就可以正常安装微软补丁了。

## 如何检查补丁状态

微软还发布了一个Powershell来检查是否安装了正确的更新程序，或是否需要额外的固件更新。  

用户在启动PowerShell时，请确保是以管理员权限启动的，以便安装所需的模块。

下面的Powershell命令，将下载并安装Powershell模块，用于测试Meltdown和Specter的缺陷。

    
    
    Install-Module SpeculationControl

如果用户运行该命令返回的是错误，则可以运行以下命令：

    
    
    Set-ExecutionPolicy Bypass

然后，用户可以运行第二条命令：

    
    
    Get-SpeculationControlSettings

谷歌在发布漏洞研究报告的时候认为，接近所有的CPU都容易受到这两个漏洞的攻击。如果用户在运行这些命令后看到很多红色的文字，那么可以确认该用户的CPU处在威胁之中。

![Meltdown+Spectre-Powershell.png](https://image.3001.net/images/20180105/15151248863134.png!small)  

下一步，选择“检查更新”，安装补丁。 在兼容性上存在问题的用户则需要继续耐心等待几天。

![Meltdown+Spectre-Updates.png](https://image.3001.net/images/20180105/15151249648382.png!small)  

更新之后，用户需要再次运行Get-SpeculationControlSettings操作。然后 有两种可能的情况。

最常见的情况是以下结果：

![Meltdown+Spectre-Powershell-post-update-2.png](https://image.3001.net/images/20180105/15151250295809.png!small)  

这个意思是说 Meltdown补丁已经成功，但是 **Spectre漏洞** 修复不完整。 **红色的文字内容** 是指改名用户还是需要
**额外的芯片组固件更新** 。如果用户的笔记本电脑/台式机/服务器供应商提供了额外的芯片组固件更新，他们可以从官方站点获取，安装并完成修补程序。

如果一切正常，所有检查将以绿色文本显示，如下所示：

![Meltdown+Spectre-Powershell-OK.png.jpeg](https://image.3001.net/images/20180105/15151252843709.jpeg!small)  

当输出全部为绿色，每个设置都是True时，那么，

>  **恭喜，你已经成功在Windows系统级别修复了Meltdown和Spectre漏洞了！**

##  **补充：关于芯片组固件更新**

Intel 方面在1月4号发布了新通告表示，他们保证 90%的 CPU（近5年的）固件更新会在下周结束前全部放出。目前他们已经在和其他合作伙伴进行这些
CPU 更新。初始设备制造商和其他硬件供应商需要将这些固件更新包含在自己的产品更新中。

除此之外，该公司重申，固件更新不会造成显著的性能下降。Intel 承诺会随着时间的推移对这些补丁进行测试和优化，以进一步减轻对性能的影响。

![Intel-CPUs.png](https://image.3001.net/images/20180105/15151299605218.png!small)  

按照目前的资料来看，Intel 处理器已经确定会受到 Meltdown 漏洞的影响，但除了英特尔之外，Spectre 漏洞还会影响AMD和ARM CPU。

###  **参考来源：**

 **[BP](https://www.bleepingcomputer.com/news/microsoft/how-to-check-and-update-windows-systems-for-the-meltdown-and-spectre-cpu-flaws/)／[BP2
](https://www.bleepingcomputer.com/news/microsoft/microsoft-releases-emergency-updates-to-fix-meltdown-and-spectre-cpu-flaws/)/
[Microsoft](https://support.microsoft.com/en-us/help/4073119/protect-against-speculative-execution-side-channel-vulnerabilities-in)／[Microsoft
2](https://support.microsoft.com/en-us/help/4072698/windows-server-guidance-to-protect-against-the-speculative-execution)/
[Advice](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV180002) / [Microsoft 3](https://support.microsoft.com/en-us/help/4072699/important-information-regarding-the-windows-security-updates-released)/ [Intel](https://www.bleepingcomputer.com/news/hardware/intel-promises-firmware-updates-for-most-modern-cpus-by-the-end-of-next-week/)  
**

 ***本文编译整理Elaine，转载请注明FreeBuf.COM**

