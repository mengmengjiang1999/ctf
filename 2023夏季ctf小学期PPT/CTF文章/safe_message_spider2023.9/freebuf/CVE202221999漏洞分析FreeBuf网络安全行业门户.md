## 一、 漏洞信息

CVE-2022-21999（CVE-2022–22718）是微软2月周二补丁所爆出来的打印机本地提权漏洞。其本质上是CVE-2020-1030的绕过。

## 二、 测试环境及漏洞复现

### 测试环境

POC：<https://github.com/ly4k/SpoolFool>

靶机： win10 x64 专业版，1909

###
漏洞复现![wKg0C2I4YomAH8N0AAEC456pCtU803.png](https://image.3001.net/images/20220808/1659943019_62f0b86bd7233fc96cbde.png!small)

## 三、 漏洞成因分析

### Print Spool

 **主要组件**

Print
Spooler是打印后台处理服务，即管理所有本地和网络打印队列及控制所有打印工作。如果此服务被停用，本地计算机上的打印将不可用。主要组件如下图所示：

![wKg0C2I4YqCAeowJAABLUzFBSnU927.png](https://image.3001.net/images/20220808/1659943020_62f0b86c899cb7f185edb.png!small)

具体组件信息微软官方文件有详细阐述，感兴趣的同学可通过参考链接1进行查阅。

 **Spool directory**

当用户打印文档时，打印作业被spool送到一个预定的位置，称为spool directory。另外spool
directory在每台打印机设备上都是可以配置（修改）的，而且它会赋予所有用户拥有FILE_ADD_FILE权限。

通过在打印机的注册表项设置spool  
directory的值来支持单个spool directory。

![wKg0C2I4YseAPOh2AAB6e2vYDyc290.png](https://image.3001.net/images/20220808/1659943021_62f0b86d0978e9530bb1d.png!small)

 **Point and Print**

Point and Print 是为驱动程序分发而设计的多种打印机共享技术之一。在Point and Print中，驱动程序（v4
之前的型号）和配置文件会自动从打印服务器下载。安装可通过自定义的 Point and Print DLL 进行扩展。该DLL是通过在打印机配置中定义
CopyFiles 注册表项来实现的。

 **相关函数**

Print spool提供以下四个函数用于管理配置数据

![wKg0C2I4YtAJJzPAAB3koqgL2o744.png](https://image.3001.net/images/20220808/1659943021_62f0b86d8c8042978890a.png!small)

以上函数去执行与print`s Key(pValueName控制)相关的注册表操作。

当我们通过上述函数修改print的配置时，有一个大前提就是打印机需要以PRINTER_ACCESS_ADMINISTER权限被打开。

### 成因分析

 **SetPrinterDataEx分析**

带有 CopyFiles 注册表项的 SetPrinterDataEx 会导致spooler自动加载在 Module 值中分配的 Point and
Print DLL。其调用链如下：

![wKg0C2I4YvKAL21IAABXilgaE60337.png](https://image.3001.net/images/20220808/1659943022_62f0b86e05343e6543d70.png!small)

用户层调用SetPrinterDataEx函数，Winspool会向本地Print
Spooler（LocalSpl）发送一个RPC请求，后者会将请求route 到SplSetPrinterDataEx 中的本地打印提供程序实现。

![wKg0C2I4YvAIOdjAAC0gZlXyM267.png](https://image.3001.net/images/20220808/1659943022_62f0b86e71b2e46306c2e.png!small)

在localspl.dll!SplSetPrinterDataEx中会对pKeyName的值进行匹配

![wKg0C2I4YweAOkVqAAA1kP9IKrA747.png](https://image.3001.net/images/20220808/1659943022_62f0b86ee63fec952d04a.png!small)

当 pszKeyName 以”CopyFiles\”字符串开头时触发Load事件，会调用SplCopyFileEvent去处理。

![wKg0C2I4YxGAHTbLAAAlDeYsdPQ775.png](https://image.3001.net/images/20220808/1659943023_62f0b86f9acf4a332d5e9.png!small)

SplCopyFileEvent首先通过调用SplGetPrinterDataEx获取模块路径长度，为其申请相应的内存，接着再次通过SplGetPrinterDataEx获取模块完整路径。最后将要加载的模块路径传入SplLoadLibraryTheCopyFileModule。

![wKg0C2I4Yx6AEIhOAABlAjX70tE413.png](https://image.3001.net/images/20220808/1659943024_62f0b8701111feb7b238f.png!small)

调试信息如下：

![wKg0C2I4YyaAR2mEAADvExGSU3w328.png](https://image.3001.net/images/20220808/1659943024_62f0b8707a525e5bd0695.png!small)

SplLoadLibraryTheCopyFileModule会对模块路径进行验证，只有通过验证后才可以加载DLL。

![wKg0C2I4YzaAXP3AADqzsrbgc894.png](https://image.3001.net/images/20220808/1659943025_62f0b87102323b2c6f87e.png!small)

MakeCanonicalPath将模块路径转换为规范路径。

![wKg0C2I4Yz6AE5foAACpz2K4qco134.png](https://image.3001.net/images/20220808/1659943025_62f0b8717ed4d1699c9f0.png!small)

IsModuleFilePathAllowed函数将验证模块规范路径是否在system路径或者打印机驱动目录下。

![wKg0C2I4Y0eAKI1eAABcPOKGLIY456.png](https://image.3001.net/images/20220808/1659943026_62f0b8720e87ab4e9c5bd.png!small)

  * System路径：DLL只能直接在C:\Windows\System32\路径下才可以（不包括下层目录）。
  * 打印机驱动目录路径：DLL可以在打印机驱动目录下的任意路径。

![wKg0C2I4Y1aAH2ihAABJx3rvODw882.png](https://image.3001.net/images/20220808/1659943026_62f0b8728083aeb5ee8ee.png!small)

Tips：匹配算法是通过是将模块规范路径去掉其前四个字节后，进行匹配的。即?\C:\Windows\System32\spool\drivers\x64  
printers\变为C:\Windows\System32\spool\drivers\x64  
printers\。此种方法存在一定的缺陷，漏洞利用也是针对这种检查方式的绕过。

 **漏洞点分析**

Spooler在加载Point and Print DLL时会依次搜索一下两个路径：

  * %SYSTEMROOT%\System32 % SYSTEMROOT% System32
  * %SYSTEMROOT%\System32\spool\drivers<ENVIRONMENT><DRIVERVERSION> %

![wKg0C2I4Y3uAEyY9AAAxnSUpzPU824.png](https://image.3001.net/images/20220808/1659943027_62f0b8733c3a2da3a37c3.png!small)

我们可以从第二个路径做文章，也就是打印机驱动程序目录，我们可以利用一个不存在的版本（4）驱动程序目录来进行利用。如果我们能够创建具有读写权限的目录，那么missing
path可能存在代码执行机会。然后可以将任意 DLL 放置到文件路径中，并通过  
SetPrinterDataEx 调用它。

## 四、 漏洞利用分析

### 利用流程

 **创建打印机**

为获取PRINTER_ACCESS_ADMINISTER权限，要在本地创建一台新的打印机。

![wKg0C2I4Y6SARTWPAACPU2bEaD0411.png](https://image.3001.net/images/20220808/1659943027_62f0b873b25e92333b442.png!small)

 **设置Spool directory**

通过SetPrinterDataEx设置Spool directory，获取一个拥有FILE_ADD_FILE的权限的文件目录。

![wKg0C2I4Y7WAMWWlAAA6m94LpT0889.png](https://image.3001.net/images/20220808/1659943028_62f0b8742c578bbdfbe92.png!small)

这里需要特殊说明一下，在使用CVE-2020-1030漏洞补丁更新后，SetPrinterDataEx在设置Spool
directory时会对其传入的路径进行一次检查。

![wKg0C2I4Y72AaGKfAAAloyc8KnY114.png](https://image.3001.net/images/20220808/1659943028_62f0b874966fc3f5d646b.png!small)

IsValidSpoolDirectory将要设置的Spool directory路径转换为规范路径后，测试其是否具有GENERIC_WRITE权限。

![wKg0C2I4Y8WAKfoAAABxwT5GlaE907.png](https://image.3001.net/images/20220808/1659943029_62f0b87507be33af526e1.png!small)

验证成功后，在打印机注册表项对Spool directory进行更改。

 **符号链接**

设置自定义Spool
directory目的是我们想通过它去执行任意DLL，但在通过我们对SetPrinterDataEx可知，其在加载DLL前会对其路径进行一次检查（必须是system路径或打印机驱动目录），此时我就可以通过符号链接（重解析）来绕过。

![wKg0C2I4Y9qAR5ZHAAAf0hjSJGo407.png](https://image.3001.net/images/20220808/1659943029_62f0b8757293b2ecef43c.png!small)

即让自定义的路径[\localhost\C$/spooldir)指向C:\Windows\System32\spool\drivers\x64\，至于这里为什么要用UNC路径，后面会进行解释。

![wKg0C2I4YOAMfRLAAA0ve1wfQk122.png](https://image.3001.net/images/20220808/1659943029_62f0b875d17d8dadb7fde.png!small)

 **重新启动Spooler服务**

在第2步中的设置Spool directory，并没有实际进行创建，仅是在注册表中进行设置。而实际创建目录仅在
Spooler初始化时才会被创建。但此时我们的打印机已经被创建，Spooler的初始化也已经完成。看起来很难完成，但车到山前必有路，可以通过将
AppVTerminator.dll 加载到 Spooler中，强制 Spooler重新启动以创建目录。

![wKg0C2I4ZBmAbq3pAABA4CtEgY8908.png](https://image.3001.net/images/20220808/1659943030_62f0b8764211241a98936.png!small)

AppVTerminator的Dllmain可直接结束当前进程（spoolsv.exe）。

![wKg0C2I4ZCOAAIHdAABqKtc9LI8747.png](https://image.3001.net/images/20220808/1659943030_62f0b876ae6dad6094804.png!small)

Spooler被强制结束后，会触发其恢复机制，从而达到重启服务的目的。

Spooler重启之后会通过localspl!SplCreateSpooler  
调用 localspl!BuildPrinterInfo 时会创建spool directory。在 localspl!BuildPrinterInfo  
赋予FILE_ADD_FILE 权限之前，进行最后检查以确保目录路径不在打印机驱动程序目录中。

Tips：此项路径检查同样是在CVE-2020-1030的补丁中添加。

![wKg0C2I4ZCyACeX6AABaAfgp2Gs939.png](https://image.3001.net/images/20220808/1659943031_62f0b8776f272492080ac.png!small)

综上所述，想要成功加载一个DLL我们必须保证以下两点：

BuildPrinterInfo检查时，保证Spool directory路径不以

  * C:\ Windows\System32\spool\drivers\x64\开头
  * SplLoadLibraryTheCopyFileModule 检查时，保证Spool directory路径以C:\ Windows\System32\spool\drivers\x64\开头

这样看起来好像很矛盾，但它的检查算法(IsModuleFilePathAllowed)是存在缺陷的（去掉前4个字节匹配），因此我们可以将Spool
directory设置为UNC路径，例如[\localhost\CKaTeX parse error: Undefined control
sequence: \spooldir at position 1:
\̲s̲p̲o̲o̲l̲d̲i̲r̲\printers\\](fil…/spooldir/printers/),经过设置软连接后，它的规范路径是\?\UNC\localhost\C$\Windows\System32\spool\drivers\x64\printers\，因此去掉前四个字节后与C:\Windows\System32\spool\drivers\x64\也不匹配。成功过掉检查后，BuildPrinterInfo就会给Spool
directory（C:\Windows\System32\spool\drivers\x64\）赋予FILE_ADD_FILE权限。

 **写入DLL并加载**

Spooler服务成功重启后，我们可以将想要执行的DLL文件写入到C:\Windows\system32\spool\DRIVERS\x64\4，然后通过SplLoadLibraryTheCopyFileModule去加载（以SYSTEM权限加载）。

![wKg0C2I4ZFqASLHAACHEWbYS48203.png](https://image.3001.net/images/20220808/1659943031_62f0b877e2fb525f14dc1.png!small)

### 符号链接

CVE-2022-21999实际上是CVE-2020-1030的绕过，其核心是UNC路径和符号链接。这里简单介绍一下符号链接。

符号链接是将自己链接到一个目标文件或目录的路径上。当系统识别到符号链接时，它会跳转到符号链接所指向的目标中去，而不改变此时的文件路径。实际上，我认为这就是高级快捷方式。

如下图所示，为打印机驱动程序目录创建符号链接\localhost\C$\Users\jiabin3\AppData\Local\Temp\c0e601f7-92b2-4167-b18f-3a23c65eaa94。然后可以看到，打开此路径之后  
，其内部的目录（文件）结构与打印机驱动程序目录是一致的。唯一的区别是他们的路径不一样，我认为这是一种高级映射方式。

![wKg0C2I4ZGyAMu9NAAB2mgnwzXI014.png](https://image.3001.net/images/20220808/1659943032_62f0b8786ac8f52d1b487.png!small)

## 参考链接

> Print Spool组件介绍
>
> <https://docs.microsoft.com/en-us/windows-> hardware/drivers/print/introduction-to-spooler-components>
>
> Windows Print Spooler Privilege  
> Escalation
>
> <https://research.ifcr.dk/spoolfool-windows-print-spooler-privilege-> escalation-cve-2022-22718-bf7752b68d81>
>
> Windows 符号链接
>
> [https://sspai.com/post/66834﻿](https://sspai.com/post/66834)

