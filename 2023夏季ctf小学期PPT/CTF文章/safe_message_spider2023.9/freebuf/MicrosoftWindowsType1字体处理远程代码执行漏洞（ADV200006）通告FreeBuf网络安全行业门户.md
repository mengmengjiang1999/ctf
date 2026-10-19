## 文档信息

编号  |  QiAnXinTI-SV-2020-0009  
---|---  
关键字  |  字体 Adobe Type 1 PostScript ADV200006  
发布日期  |  2020年3月24日  
更新日期  |  2020年3月24日  
TLP  |  WHITE  
分析团队  |  奇安信威胁情报中心  
  
## 通告背景

2020年3月24日，微软官方发布了一个非例行的预警通告。通告描述有两个漏洞存在于Windows Adobe Type Manager库处理Adobe
Type 1 PostScript字体模块中，可能导致代码执行，有意思的是2015年Hacking
Team泄露的工具中其中一个漏洞也是出于该模块。从通告中可知该漏洞已经被用于有限的在野攻击中，攻击者可以通过多种方式利用此漏洞：例如诱导用户打开特制文档或通过在Windows预览窗格中查看来执行漏洞攻击。由于微软会在稍后四月的补丁日才对该漏洞进行修复，所以奇安信威胁情报中心发布该通告提醒用户通过适当的缓解措施做好提前防范。

奇安信息威胁情报中心红雨滴团队已经确认漏洞的存在并保持关注，有更多细节和进展会随时通报。

## 漏洞概要

**漏洞名称** **** |  Microsoft WindowsType 1字体远程代码执行漏洞  
---|---  
**威胁类型** **** |  代码执行  |  **威胁等级** **** |  严重  |  **漏洞** **ID** |  ADV200006  
**利用场景** **** |  攻击者可以通过构造包含恶意的字体文件，诱使用户打开特制文档或在Windows预览窗格中查看它，可能导致任意代码执行。  
**受影响系统及应用版本** ****  
Windows 10 for 32-bit Systems  
Windows 10 for x64-based Systems  
Windows 10 Version 1607 for 32-bit Systems  
Windows 10 Version 1607 for x64-based Systems  
Windows 10 Version 1709 for 32-bit Systems  
Windows 10 Version 1709 for ARM64-based Systems  
Windows 10 Version 1709 for x64-based Systems  
Windows 10 Version 1803 for 32-bit Systems  
Windows 10 Version 1803 for ARM64-based Systems  
Windows 10 Version 1803 for x64-based Systems  
Windows 10 Version 1809 for 32-bit Systems  
Windows 10 Version 1809 for ARM64-based Systems  
Windows 10 Version 1809 for x64-based Systems  
Windows 10 Version 1903 for 32-bit Systems  
Windows 10 Version 1903 for ARM64-based Systems  
Windows 10 Version 1903 for x64-based Systems  
Windows 10 Version 1909 for 32-bit Systems  
Windows 10 Version 1909 for ARM64-based Systems  
Windows 10 Version 1909 for x64-based Systems  
Windows 7 for 32-bit Systems Service Pack 1  
Windows 7 for x64-based Systems Service Pack 1  
Windows 8.1 for 32-bit systems  
Windows 8.1 for x64-based systems  
Windows RT 8.1  
Windows Server 2008 for 32-bit Systems Service Pack 2  
Windows Server 2008 for 32-bit Systems Service Pack 2 (Server Core
installation)  
Windows Server 2008 for Itanium-Based Systems Service Pack 2  
Windows Server 2008 for x64-based Systems Service Pack 2  
Windows Server 2008 for x64-based Systems Service Pack 2 (Server Core
installation)  
Windows Server 2008 R2 for Itanium-Based Systems Service Pack 1  
Windows Server 2008 R2 for x64-based Systems Service Pack 1  
Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core
installation)  
Windows Server 2012  
Windows Server 2012 (Server Core installation)  
Windows Server 2012 R2  
Windows Server 2012 R2 (Server Core installation)  
Windows Server 2016  
Windows Server 2016 (Server Core installation)  
Windows Server 2019  
Windows Server 2019 (Server Core installation)  
  
需要注意的是Win10相关的操作系统，尤其是1703之后的版本，由于相关的字体处理都移至用户层的fontdrvhost.exe中，因此漏洞利用将只导致AppContainer沙盒的代码执行和有限度的权限提升。

## 漏洞描述

两个漏洞存在于Adobe Type Manager库处理Adobe Type 1 PostScript字体模块中，可导致代码执行，目前技术细节未知。

## 影响面评估

此漏洞主要影响Windows的字体处理，目前疑似被有限的针对性利用，考虑到相关设备的数量级，潜在威胁较大。

## 处置建议

### 修复方法

目前暂时没有相关的补丁发布，微软当前提供了多个相关的缓解措施，但是相关操作都会有一些不良后果，是否使用需要结合自己业务进行判断。

1\.
在Windows资源管理器中禁用预览窗格和详细信息窗格，可用于防止相关恶意OTF字体被Windows预览窗口加载，但不能阻止经过身份验证的本地用户运行特制程序来利用此漏洞。

 **Windows Server 2008** **，Windows 7** **，Windows Server 2008 R2** **，Windows
Server 2012** **，Windows Server 2012 R2** **和Windows 8.1** **通过如下操作禁用**

 **Windows Server 2016** **，Windows 10** **和Windows Server 2019** **通过以下操作禁用**

通过以下操作撤销以上操作

 **Windows Server 2008** **，Windows 7** **，Windows Server 2008 R2** **，Windows
Server 2012** **，Windows Server 2012 R2** **和Windows 8.1**

 **Windows Server 2016** **，Windows 10** **和Windows Server 2019**

2\.
禁用WebClient服务，禁用WebClient服务可以阻止最可能的远程攻击媒介，应用此替代方法后，成功利用此漏洞的远程攻击者仍然有可能导致运行位于目标用户计算机或局域网（LAN）上的程序，但打开任意程序之前，系统将提示用户进行确认。

 **通过以下操作禁用WebClient** **服务**

 **撤销相关操作**

3\. 直接重命名对应的漏洞模块ATMFD.DLL，WIN10 1709之后的版本就没有该DLL了。

 **通过以下命令重名漏洞dll** **。**

32位系统，管理员权限运行以下命令

重启系统

64位系统，管理员权限运行以下命令

重启系统

 **通过以下命令撤销重命名操作。**

32位系统，管理员权限运行以下命令

重启系统

64位系统，管理员权限运行以下命令

重启系统

4\. Windows 8.1或更低版本操作系统的可选操作（禁用ATMFD）。

 **可通过设置注册表实现对应的操作。**

 **撤销以上操作**

## 参考资料

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/adv200006>

