![](https://image.3001.net/images/20230516/1684247197_6463929ded93bbfb1c75f.png!small)

## 关于CMLoot

CMLoot是一款真的SMB共享的文件爬取工具，在该工具的帮助下，广大研究人员能够轻松寻找存储在系统中心配置管理器（SCCM/CM）
SMB共享中的敏感文件。

这类共享主要用于将软件分发到Windows企业环境中的Windows客户端，同时可以包含带有密码和证书（pfx）等敏感信息的脚本/配置文件。大多数SCCM部署都配置为允许所有用户读取共享上的文件，但有时仅限于计算机帐户使用。

SCCM/CM的内容库有一个“复杂”的文件结构：

![](https://image.3001.net/images/20230516/1684247210_646392aae6603ab7d7547.jpeg!small)

其中，DataLib文件夹中包含了很多.INI文件，这些.INI文件以原始文件名+.INI命名，而这些.INI文件包含文件的哈希，文件本身以“＜文件夹名称：哈希的4个首字符＞\
完整哈希”的格式存储在FileLib中。

## CM访问账号

我们可以对CM中的包应用访问控制机制，但这只会保护包含DataLib文件描述符记录的文件夹，而非文件本身。CMLoot将在清点过程中记录它无法访问（访问被拒绝）的任何包或文件，接下来，Invoke-CMLootHunt以使用此文件枚举访问控制试图保护的实际文件。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/1njected/CMLoot.git

## 工具使用

下列命令可以通过在活动目录中搜索CM服务器或通过在安装了SC（系统中心）的工作站中搜索注册表键来寻找CM服务器：

    
    
    (Get-ItemProperty -Path HKLM:\SOFTWARE\Microsoft\SMS\DP -Name ManagementPoints).ManagementPoints

目标设备或网络中可能部署了多个CM服务器，它们可以包含不同的文件，所以一定要找到所有这些文件。

为此，我们需要创建一个清单文件，它只是一个包含对文件描述符（.INI）引用的文本文件。以下命令将解析SCCM服务器上的所有.INI文件，以创建可用文件列表：

    
    
    PS> Invoke-CMLootInventory -SCCMHost sccm01.domain.local -Outfile sccmfiles.txt

然后使用清单文件来创建目标并下载有价值的敏感文件：

    
    
    PS> Invoke-CMLootDownload -InventoryFile .\sccmfiles.txt -GridSelect

下载单个文件：

    
    
    PS> Invoke-CMLootDownload -SingleFile \\sccm\SCCMContentLib$\DataLib\SC100001.1\x86\MigApp.xml

下载包含特定文件扩展的所有文件：

    
    
    PS> Invoke-CMLootDownload -InventoryFile .\sccmfiles.txt -Extension ps1

尝试搜索无法访问的共享：

    
    
    Invoke-CMLootHunt -SCCMHost sccm -NoAccessFile sccmfiles_noaccess.txt

提取MSI文件：

    
    
    Invoke-CMLootExtract -Path .\CMLootOut\msi

## 工具运行演示

运行清单文件，扫描可用文件：

![](https://image.3001.net/images/20230516/1684247281_646392f1316f7e4c5cba2.gif!small)

使用GridSelect选择文件：

![](https://image.3001.net/images/20230516/1684247306_6463930aab1df33963384.gif)

下载所有扩展：

![](https://image.3001.net/images/20230516/1684247331_64639323a5da7eb418469.gif)

搜索不可访问的文件并提取MSI：

![](https://image.3001.net/images/20230516/1684247345_646393317fe5779fa2444.gif)

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-3-Clause_](https://github.com/1njected/CMLoot/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **CMLoot** ：【[ _GitHub传送门_](https://github.com/1njected/CMLoot)】

## 参考资料

> [ _https://techcommunity.microsoft.com/t5/configuration-manager-> archive/understanding-the-configuration-manager-content-> library/ba-p/273349﻿_](https://techcommunity.microsoft.com/t5/configuration-> manager-archive/understanding-the-configuration-manager-content-> library/ba-p/273349)

