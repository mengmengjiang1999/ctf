2021年1月，星云攻防实验室监测到Microsoft发布了Microsoft Defender
缓冲区溢出漏洞的风险通告，该漏洞编号为CVE-2021-1647，漏洞等级：高危。

攻击者通过构造特殊的PE文件,可造成Microsoft Defender
远程代码执行。![v2-c6253eb9d57cab1b532f2bc07a13f6b5_720w.png](https://image.3001.net/images/20210120/1611110728_60079948f35495e954495.png!small)

## 漏洞描述

Windows Defender
在利用内置模拟执行组件扫描可执行文件时，存在一处堆溢出漏洞。攻击者可通过向目标受害者发送邮件或恶意链接等方式诱导受害者下载攻击者构造的恶意文件，从而使
Windows Defender 在自动扫描恶意文件时触发利用该漏洞，最终控制受害者计算机。

该漏洞目前有在野利用，谨防微信接收陌生文件，微信会自动下载放到download目录，Windows Defender扫描后会自动触发恶意文件从而弹出cmd。

## 受影响版本

> -Microsoft:Microsoft Defender:Windows 8.1 for 32-bit systems
>
> -Microsoft:Microsoft Defender:Windows 7 for x64-based Systems Service Pack 1
>
> -Microsoft:Microsoft Defender:Windows 7 for 32-bit Systems Service Pack 1
>
> -Microsoft:Microsoft Defender:Windows Server 2016 (Server Core installation)
>
> -Microsoft:Microsoft Defender:Windows Server 2016
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1607 for x64-based Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1607 for 32-bit Systems
>
> -Microsoft:Microsoft Defender:Windows 10 for x64-based Systems
>
> -Microsoft:Microsoft Defender:Windows 10 for 32-bit Systems
>
> -Microsoft:Microsoft Defender:Windows Server, version 20H2 (Server Core
> Installation)
>
> -Microsoft:Microsoft Defender:Windows 10 Version 20H2 for ARM64-based
> Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 20H2 for 32-bit Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 20H2 for x64-based Systems
>
> -Microsoft:Microsoft Defender:Windows Server, version 2004 (Server Core
> installation)
>
> -Microsoft:Microsoft Defender:Windows 10 Version 2004 for x64-based Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 2004 for ARM64-based
> Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 2004 for 32-bit Systems
>
> -Microsoft:Microsoft Defender:Windows Server, version 1909 (Server Core
> installation)
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1909 for ARM64-based
> Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1909 for x64-based Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1909 for 32-bit Systems
>
> -Microsoft:Microsoft Defender:Windows Server 2019 (Server Core installation)
>
> -Microsoft:Microsoft Defender:Windows Server 2019
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1809 for ARM64-based
> Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1809 for x64-based Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1809 for 32-bit Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1803 for ARM64-based
> Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1803 for x64-based Systems
>
> -Microsoft:Microsoft Defender:Windows 10 Version 1803 for 32-bit Systems
>
> -Microsoft:Microsoft System Center 2012 Endpoint Protection
>
> -Microsoft:Microsoft Security Essentials
>
> -Microsoft:Microsoft System Center 2012 R2 Endpoint Protection
>
> -Microsoft:Microsoft System Center Endpoint Protection
>
> -Microsoft:Microsoft Defender:Windows Server 2008 for 32-bit Systems Service
> Pack 2 (Server Core installation)
>
> -Microsoft:Microsoft Defender:Windows Server 2008 for 32-bit Systems Service
> Pack 2
>
> -Microsoft:Microsoft Defender:Windows RT 8.1
>
> -Microsoft:Microsoft Defender:Windows 8.1 for x64-based systems
>
> -Microsoft:Microsoft Defender:Windows Server 2012 R2 (Server Core
> installation)
>
> -Microsoft:Microsoft Defender:Windows Server 2012 R2
>
> -Microsoft:Microsoft Defender:Windows Server 2012 (Server Core installation)

## 漏洞级别

高危

## 修复建议

1、进行一键更新。应及时进行Microsoft Windows版本更新并且保持Windows自动更新开启。

Windows server / Windows 检测并开启Windows自动更新流程如下：

  * 点击开始菜单，在弹出的菜单中选择“控制面板”进行下一步。

  * 点击控制面板页面中的“系统和安全”，进入设置。

  * 在弹出的新的界面中选择“windows update”中的“启用或禁用自动更新”。

  * 然后进入设置窗口，展开下拉菜单项，选择其中的自动安装更新（推荐） 。

2、临时修补建议

通过如下链接自行寻找符合操作系统版本的漏洞补丁，并进行补丁下载安装。

2021 年 1 月安全更新 - 发行说明 - 安全更新程序指南 - Microsoft  
https://msrc.microsoft.com/update-guide/releaseNote/2021-Jan

![](https://image.3001.net/images/20210120/1611112493_6007a02d0d71dc7a0fadf.png!small)

