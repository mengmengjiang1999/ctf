***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![1.jpg](https://image.3001.net/images/20190401/1554108563_5ca1d093e0ad7.jpg!small)

## 基本信息

产品版本：Avira Phantom VPN

下载地址：【[点我下载](https://package.avira.com/package/oeavira/win/int/avira_en_vpn__ws.exe)】

操作系统：Windows 10 v1709（x64）

漏洞信息：Avira VPN提权漏洞

## 漏洞概述

 **AviraPhantom
VPN服务平台在检查更新时会进行大量的检测，在更新过程中，VPN服务会将更新文件下载到“C:\Windows\Temp\”目录，存储的文件名为AviraVPNInstaller.exe。**

接下来，程序会验证该文件的签名，如果版本号不符合更新条件（版本号低于当前版本），则会停止更新。如果条件符合，服务会以SYSTEM权限运行更新代码。

但我们可以使用一个已签名的有效Avira可执行文件来替换这个“AviraVPNInstaller.exe”，然后在“C:\Windows\Temp”中存放一个恶意DLL文件并最终实现提权（NT
AUTHORITY\SYSTEM）。

## 漏洞分析

当Avira VPN服务(Avira.VPNService.exe, 版本号为2.15.2.28160)开始运行后，它会检测是否有可用更新：

![2.png](https://image.3001.net/images/20190401/1554108591_5ca1d0afef161.png!small)

应用程序服务会从“C:\Windows\Temp”目录中获取下载下来的更新文件：

![3.png](https://image.3001.net/images/20190401/1554108599_5ca1d0b79abd8.png!small)

可能大家已经发现了，任何一名通过身份验证的用户都可以向“C:\Windows\Temp”目录写入文件（但无法读取文件）。当该目录中已经存在有更新文件(C:\Windows\Temp\AviraVPNInstaller.exe)时，VPN服务会检查更新文件的“FileVersion”属性，以此来判断这个更新文件是否已经在这台设备上安装过了：

![4.png](https://image.3001.net/images/20190401/1554108607_5ca1d0bf68ef9.png!small)

如果文件版本表明该更新没有安装过，服务将会对文件的有效性以及文件签名进行验证：

![5.png](https://image.3001.net/images/20190401/1554108618_5ca1d0cae9f9f.png!small)

如果文件确实有效，并且由Avira签名，那么VPN服务将会开启更新功能。因为这一切都是低权限用户可以做到的，所以攻击者就有可能劫持软件更新包，并进行数据篡改。

为了劫持“AviraVPNInstaller.exe”，攻击场景必须满足下列条件：

> 1.“AviraVPNInstaller.exe”必须由Avira签名；
>
> 2.“AviraVPNInstaller.exe”的签名必须有效，对文件进行的任何修改都将导致签名失效；
>
> 3.“AviraVPNInstaller.exe”的版本号验证结果必须是“该更新未在主机上安装过”。

这也就意味着，我们需要想办法利用Avira的已签名文件，并且版本号要高于当前产品。

研究半天之后，我们发现了“ToastNotifier.exe”，它正好符合我们的要求：

![6.png](https://image.3001.net/images/20190401/1554108629_5ca1d0d560894.png!small)

注：ToastNotifier.exe来自于Avira反病毒产品套件中。

接下来，我们要做的就是把“ToastNotifier.exe”拷贝到“C:\Windows\Temp\AviraVPNInstaller.exe”。因为一切条件都满足，当服务启动后VPN服务会以SYSTEM权限运行这个可执行文件，这一步可以通过重启或以管理员权限运行下列命令来完成（PowerShell）：

    
    
    Get-ServiceAviraPhantomVPN | Stop-Service
    
    Get-ServiceAviraPhantomVPN | Start-Service

执行之后，“ToastNotifier.exe”将会尝试加载“C:\Windows\temp”目录中的恶意DLL文件：

![7.png](https://image.3001.net/images/20190401/1554108648_5ca1d0e89872c.png!small)

为了实现SYSTEM提权，我们要做的就是提供上面这些DLL文件。这里，我们使用“cryptnet.dll”（包含了我们的恶意代码），它可以帮助我们让VPN服务以SYSTEM权限启动“AviraVPNInstaller.exe”代码，然后以SYSTEM权限加载“cryptnet.dll”，最终实现低权限用户提权为SYSTEM权限。

![8.png](https://image.3001.net/images/20190401/1554108657_5ca1d0f1e2ebf.png!small)
***参考来源：[enigma0x3](https://enigma0x3.net/2019/03/20/avira-vpn-2-15-2-28160-elevation-of-privilege-through-insecure-update-location/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

