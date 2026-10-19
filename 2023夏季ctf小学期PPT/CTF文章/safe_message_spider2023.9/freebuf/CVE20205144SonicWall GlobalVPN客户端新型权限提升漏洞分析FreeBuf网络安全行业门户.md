![](https://image.3001.net/images/20210120/1611156757_60084d15b84006f2fe4f7.png!small)

## 概述

今年疫情依然形势严峻，这对我们的日常生活和工作都带来了很大的改变。对于工作来说，很多公司都将一些业务转移到了线上去完成，因此VPN的安全就变得至关重要了。在这篇文章中，我们将分析SonicWall
Global VPN（Windows客户端）中新发现的一个权限提升漏洞。

## 可执行文件搜索命令劫持

Windows系统使用一种通用的方法来查找需要加载的可执行文件或DLL。

当正在运行的进程在没有指定特定路径的情况下搜索可执行文件时，Windows将按已知顺序通过目录搜索可执行文件。如果操作系统找不到可执行文件，Windows将在PATH环境变量中搜索，这是万不得已的办法—首先搜索系统范围内的PATH环境变量，该变量只能由Administrators组的成员修改，然后搜索用户的PATH环境变量，该变量也可以由用户自己修改。

在本文中，我们将不关注特权进程依赖于用户拥有的PATH环境变量的情况。

但是，我们将讨论更常用的系统范围内的PATH环境变量，它由特权目录列表组成，其中包含系统范围内的常用可执行文件：

![](https://image.3001.net/images/20210120/1611156768_60084d20c052359c3bf02.png!small)

对于最佳实践方案，特权应用程序不应依赖于可执行搜索顺序机制，尤其是PATH环境变量，即使它们的可执行文件可以在加载顺序的任何步骤中的默认目录中找到。

如果攻击者成功地修改了搜索顺序并将可控制的目录放在其中的内置目录之前，那么攻击者将获取到依赖于PATH路径的可执行文件的执行权限。

要做到这一点，必须拥有这些系统环境变量的写入权限。默认情况下，非特权用户是没有这种权限的。因此，攻击者必须是Administrators组的成员。

为此目的而升级到管理权限并不是一件小事，因此这似乎是一条死胡同。但是，由于已安装的应用程序也会使用PATH，一些应用程序（比如说Python）通过将自己创建的目录放在PATH中来更改搜索顺序，而不必遵循Windows在默认目录中的权限方面强制执行的相同标准。值得注意的是，这些错误配置可能会被无权限用户用来提升权限（稍后将详细说明）。

## 漏洞分析

当SonicWall Global VPN客户端在安装或卸载的时候，它会使用一个Windows
Installer，而这个程序是以SYSTEM权限执行的。为了安装（或卸载）“SonicWall
IPSec驱动程序”，Installer将提取dneinst.exe，该组件是DNE（一个Citrix应用程序，它扩展了操作系统和网络协议设备）的一部分，这个组件也会以SYSTEM权限运行。

在执行过程中，dneinst.exe将创建PowerShell进程以执行PowerShell命令，而不会指定完整的powershell.exe路径，这种在最高安全权限上执行的行为将会导致安全漏洞的出现。

![](https://image.3001.net/images/20210120/1611156784_60084d30b363d6ec4f802.png!small)

通常，要进行安全的CreateProcess调用，最佳实践是使用完整路径来进行调用。在这种情况下，powershell.exe仅通过其文件名调用，此时会触发Windows按以下顺序搜索powershell.exe：

![](https://image.3001.net/images/20210120/1611156790_60084d363c89b6f8a740c.png!small)

Powershell.exe通常可以在下列路径中找到：

  * C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

  * C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe

因此，执行将在最后一步成功地将其加载到PATH中。但是，如果一个系统安装了Python，那么Python路径将添加到PATH环境变量中，并且要先于powershell.exe的目录位置。

![](https://image.3001.net/images/20210120/1611156796_60084d3cde5cdc2e68739.png!small)

当Python创建这些目录（例如C:\Python27）时，它们被授予许可权限，允许任何经过身份验证的用户（包括未经授权的用户）向这些位置进行写入：

![](https://image.3001.net/images/20210120/1611156802_60084d423ef5ef3baeb3c.png!small)

而开发人员的责任，就是要确保执行不能被这种行为所篡改！

## 漏洞利用

为了利用该漏洞，标准用户需要创建一个恶意文件，并将其命名为powershell.exe，然后将其拷贝到自己所能访问的每一个目录之中，而且顺序一定要在系统范围PATH环境变量中C:\Windows\SysWOW64\WindowsPowerShell\v1.0的前面。比如说，C:\Python27。接下来，我们只需要等待PowerShell脚本运行就可以了。

## 概念验证PoC

在我们的漏洞利用PoC中，我们创建了一个名为“malicious”的文件，它讲解吃powershell.exe，并弹出一个命令行Shell：

 **视频地址：**[ _https://油管/hgkyyPC0mzQ_](https://xn--uvwy13a/hgkyyPC0mzQ)

