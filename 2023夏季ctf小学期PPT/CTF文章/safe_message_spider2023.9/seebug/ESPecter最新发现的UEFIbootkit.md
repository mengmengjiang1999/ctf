**译者：知道创宇404实验室翻译组  
原文链接：<https://www.welivesecurity.com/2021/10/05/uefi-threats-moving-esp-introducing-especter-bootkit/>**

ESET公司研究发现了一个以前未记录的 UEFI bootkit，其根源可以追溯到至少2012年

## 前言

ESET 的研究人员发现了一个以前从未记录的真实存在的 UEFI bootkit，它现在仍然存在于 EFI系统分区上，我们称之为 ESPecter
。它可以绕过驱动程序强制签名限制来加载自己的未签名驱动程序，这为其间谍活动提供了便利。除了卡巴斯基最近发现的关联不大的 FinSpy
bootkit，现在可以肯定地说，现实世界中的 UEFI
威胁不再局限于[Lojax](http://https://hackernews.cc/archives/24185 "Lojax")使用的 SPI
闪存植入。 传统 BIOS 基础上的 UEFI
(可扩展固件接口)已经一去不复返了。作为嵌入到现代计算机和设备芯片中的一种先进技术，它在保证操作系统前期环境安全和加载操作系统方面起着至关重要的作用。如此广泛使用的技术成为威胁行为者寻求一劳永逸的诱人目标，这一点毫不奇怪。

## 概述

在过去几年中，我们已经看过 UEFI bootkits (DreamBoot、 EfiGuard)、泄露文档(DerStarke、
QuarkMatter)甚至泄露源代码(Hacking Team Vector EDK)的实例，这表明真正的 UEFI 恶意软件是存在的，不论是以SPI
闪存植入还是 ESP 植入的形式。尽管如此，到目前为止，只发现了三个 UEFI
恶意软件([LoJax](https://www.welivesecurity.com/wp-content/uploads/2018/09/ESET-LoJax.pdf)、[MosaicRegressor](https://securelist.com/mosaicregressor/98849/)、FinSpy）。虽然前两个属于
SPI 闪存植入类别，最后一个属于 ESP 植入类别，令人惊讶的是，它不是唯一的ESP 植入类别。 现在，我们描述的最近发现的
ESPecter，是第二个使用ESP形式的UEFI bootkit，它以修补的Windows引导管理器的形式存在，进行分析。ESPecter
是在一台遭到感染的机器上发现的，而且它配有一个具有键盘记录和文档窃取功能的用户模式客户端组件，因此我们认为 ESPecter
主要用于间谍活动。有趣的是，我们追溯这种威胁的根源至少可以追溯到2012年，之前它是作为一个引导工具包为传统BIOS系统提供服务的。尽管 ESPecter
存在了很长时间，但是它的操作和升级到 UEFI的行为却直到现在才被记录下来。请注意，ESPecter 和卡巴斯基 FinSpy
之间唯一的相似之处在于，它们共享 UEFI 启动管理器妥协方法。

![](https://images.seebug.org/content/images/2021/10/2e97744d-d78f-4472-8f84-9a90a2a442bb.png-w331s)
图1. Windows系统上的传统引导流程(左)和 UEFI 引导流程(右)的比较 通过修补 Windows Boot
Manager，攻击者可以在操作系统完全加载之前执行系统引导过程的早期阶段(参见上图) 。因而ESPecter 可以绕过 Windows
驱动程序签名强制(DSE) ，以便在系统启动时执行自己的无签名驱动程序。然后，该驱动程序将其他用户模式组件注入到特定的系统进程中，以启动与 ESPecter
的 c & c 服务器的通信，并允许攻击者通过下载和运行其他恶意软件或执行 c & c 命令来控制受到攻击的机器。 尽管 Secure Boot
可以阻止执行ESP来源的不可信的 UEFI 二进制文件，但在过去几年中，我们已经见证了各种 UEFI 固件漏洞，成千上万个设备因为允许禁用或绕过
Secure Boot，而受到攻击(例如 VU # 758382，VU # 976132，VU # 631788，...)。这表明，确保 UEFI
固件安全这个工作颇具挑战性，而且各种供应商运用安全策略和使用 UEFI 服务的方式并不总是恰当的。 以前，我们报道过多个恶意 EFI
案例，它们是简单的、单用途的 UEFI 应用程序，没有广泛的功能。这些报道以及同时发现的 ESPecter 和 FinFisher bootkit
(两者都是全功能 UEFI bootkit)表明，威胁行为者在操作系统之前的持久性方面不仅仅依赖 UEFI 固件植入，而且还试图利用遭到禁用的 Secure
Boot 来执行他们自己的 ESP 植入。 我们尚未确定 ESPecter 背后的威胁行为者。

## ESPecter bootkit 的进化

当我们查看遥测数据时，我们可以将这个 bootkit 的起源追溯到至少2012年。一开始，它使用 MBR
(主引导记录)修改作为其长期使用方法，并且它的作者对新的 Windows OS
版本投入越来越多的关注。有趣的是，这些年来，这个恶意软件的组件几乎没有变化，2012年和2020年版本之间的差异并没那么明显。 多年之后，ESPecter
背后的人显然决定将他们的恶意软件从传统 BIOS 系统移植到现代的 UEFI 系统。为了实现这一点，他们修改了位于 ESP 上的合法的 Windows
Boot Manager 二进制文件(`bootmgfw.efi`)，同时覆盖从 Windows 7到 Windows 10的多个 Windows
版本。正如我们前面提到的，这个方法有一个缺点——它要求禁用Secure Boot，以便使用修改过的boot管理器。然而，值得一提的是，第一个支持安全启动的
Windows 版本是 Windows 8，这意味着所有以前的版本都容易受到这种方法的攻击。 对于支持安全启动的 Windows
操作系统版本，攻击者需要禁用它。现在，我们还不知道 ESPecter 运营者是如何做到这一点的，但有几种可能的情况: \-攻击者可以对设备进行物理访问(历史上称为“evil maid”攻击) ，并在 BIOS 设置菜单中手动禁用安全启动(固件配置菜单仍然被标记并称为“ BIOS
设置菜单”是很常见的，甚至在 UEFI 系统中也是如此) \-安全引导已经在被攻破的机器上禁用了(例如，用户可能会使用双引导窗口和其他不支持安全引导的操作系统) \- 利用允许禁用安全启动的未知 UEFI 固件漏洞
\- 在已过时的固件版本或不再支持的产品上利用已知的 UEFI 固件漏洞

## 技术分析

在我们的调查中，我们发现了一些与 ESPecter 相关的恶意组件: \- 安装程序，仅适用于bootkit的旧版 MBR 版本，其目的是通过重写引导设备的
MBR 在计算机上设置持久性 \-启动代码，以UEFI系统上修改的Windows引导管理器（`bootmgfw.efi`）形式，或以旧引导系统中恶意MBR形式 \-内核模式驱动程序，用于为用户模式有效负载准备环境，并在操作系统启动的早期阶段将它们注入特定的系统进程来加载 \- 用户模式有效负载，负责与 c & c
进行通信、更新 c & c 配置并执行 c & c 命令

有关 ESPecter bootkit 危害的完整方案，请参见下图。

![](https://images.seebug.org/content/images/2021/10/732acf09-9add-4d34-bf03-1adacd25cae4.png-w331s)

## 实现持久性-UEFI 启动

在使用 UEFI 启动模式的系统上，ESPecter 持久性是通过修改 Windows启动管理器`bootmgfw.efi`和 回退引导装载程序二进制
`bootx64.efi` 建立的，这两个文件通常分别位于 ESP 目录 EFI\Microsoft\Boot\和 EFI\Boot\
中。引导加载程序的修改包括添加一个名为.efi 到 PE，并更改可执行文件的入口点地址，这样程序流就跳转到添加部分的开头，如下图所示。

![](https://images.seebug.org/content/images/2021/10/215a2e48-8bcf-4cb2-b429-fbc43152a00b.png-w331s)
原版(顶部)和修改版(底部) Windows 启动管理器(bootmgfw.efi)的比较

### 简化的启动链

如下图左侧的方案所示，UEFI 系统上的引导过程(忽略固件部分)是从执行位于 ESP 中的引导加载程序开始。对于 Windows 操作系统，这部分由
Windows Boot Manager 二进制文件(bootmgfw.efi) 完成，其用途是查找已安装的操作系统并将执行转移到其 OS 核心引导程序-winload.efi。与引导管理器类似，OS 内核加载程序负责加载和执行引导链中的下一个组件—— Windows 内核(ntoskrnl.exe)。

![](https://images.seebug.org/content/images/2021/10/f4e331ed-e514-408d-8346-d0cec3db7292.jpg-w331s)
典型的 Windows UEFI 引导流程(左)与 ESPecter 修改的引导流程(右)相比较

### ESpecter 如何修改 UEFI 启动过程

为了成功地删除其恶意负载，ESPecter 需要在启动过程中绕过 Windows Boot Manager 和 Windows
内核执行的完整性检查。为了做到这一点，它寻找字节模式来识别内存中所需的函数，并相应地对它们进行补丁。 关于引导加载程序Windows Boot
Manager (bootmgfw.efi)，启动工具包从修补 BmFwVerifySelfIntegrity
函数开始。此函数负责验证引导管理器自己的数字签名，并用于防止执行修改后的引导管理器。在下图中，您可以看到 ESPecter
是如何使用各种字节模式搜索内存中的 BmFwVerifySelfIntegrity函数 (以支持众多 bootmgfw.efi 版本)
，并修改这个函数，使其始终返回零，暗示函数验证是成功的。

![](https://images.seebug.org/content/images/2021/10/4e88361d-8c3f-43bf-bc85-76ea4d8d94b6.png-w331s) hex-ray 反编译代码——搜索和修补 BmFwVerifySelfIntegrity 函数
如前所述，这个引导装载程序的主要目标是找到一个已安装的操作系统并将执行转移到其 OS 内核装载程序。对于 Windows Boot Manager，这发生在
Archpx64TransferTo64BitApplicationAsm 函数中; 因此，ESPecter
查找这个函数是为了捕捉操作系统加载程序已加载到内存中但尚未执行的时刻。如果捕捉到这个时刻，ESPecter
补丁此函数插入自己的迂回函数，由此可以方便地在恰当时间修改内存中加载的 OS 加载程序。
操作系统加载程序的修改不包括任何完整性检查或其他功能的补丁。在这个阶段，bootkit需要重新分配它的代码，因为作为一个 UEFI
应用程序，它在从其入口点函数返回后可能会被从内存中卸载。为此，它会使用 BlImgAllocateImageBuffer 或
BlMmAllocateVirtualPages
函数(取决于找到的模式)。在这次重新分配之后，bootkit将在负责传输执行到操作系统内核的函数——OslArchTransferToKernel
中插入一个迂回函数(位于先前分配的缓冲区)，这样它就可以在内存中修补 Windows 内核，时间只要在被加载后，但是被执行之前即可。Bootkit
的引导代码的最后一个阶段负责通过修补 SepInitializeCodeIntegrity 内核函数来禁用 DSE。

![](https://images.seebug.org/content/images/2021/10/2559aa22-0881-40df-aeb3-f48e43749583.png-w331s) hex 射线反编译 SepInitializeCodeIntegrity
函数在内存中修补前(左)和后(右)的比较

有趣的是，引导代码还对 MiComputeDriverProtection
内核函数进行了补丁。尽管这个功能不会直接影响恶意驱动程序的成功加载，但是如果没有在内核内存中找到并修补这个功能，bootkit
就不会继续放置驱动程序。我们无法确定第二个补丁的用途，但是我们假设这个修改后的函数可能被其他未知的ESPecter组件使用。 \-\SystemRoot\System32\null.sys(驱动器) \- \SystemRoot\Temp\syslog (加密配置)

该配置由内核驱动程序部署的 WinSys.dll 用户模式组件使用，由一个单字节的 XOR 密钥和加密的配置数据组成。为了解密配置，WinSys.dll:
\- Base64对配置数据进行解码 \- XORs 使用 XOR 键对数据进行处理 \- Base64对由“ |”分隔的每个值分别进行解码

下图展示了一个由于 EFI 版本的 ESPecter 放置的配置示例。IoCs 部分提供了一个完整的 IP 地址和域名列表，这些列表来自我们发现的
ESPecter bootkit 示例(包括 Legacy Boot 和 UEFI 版本)中嵌入的配置。

![](https://images.seebug.org/content/images/2021/10/14a88180-d089-49ac-bdc6-17b0bcb440db.jpg-w331s) ESPecter bootkit EFI 版本提供的配置的解密

## 实现持久性-Legacy Boot

如前所述，我们现在知道的有支持 UEFI 的 ESPecter 版本，以及支持传统启动模式的其他版本。对于
传统启动模式，持久性是通过修改位于磁盘驱动器的第一个物理扇区中的 MBR
代码这一技术实现的，这个技术较为常见，因此，我们在这里不详细解释它，只是对它进行总结。

### ESPecter 如何修改遗留引导过程？

恶意 MBR 首先通过安装程序解密先前复制到磁盘扇区2、3和4的代码，钩住实模式 INT13h (BIOS 扇区读写服务)
中断处理器，然后将执行程序传递给原始的 MBR 代码，并由安装程序备份到第二扇区(扇区1)。与其他已知的 MBR 引导工具包类似，当调用
**INT13h** 中断处理器 时，钩子代码(位于扇区0)检查服务0x02(从驱动器读取扇区)和0x42(从驱动器读取扩展扇区)
，以拦截`bootmgr`（Windows 启动管理器的传统版本）的加载。注意，ESPecter 的遗留版本不需要在 `bootmgr` 中为
`BmFwVerifySelfIntegrity` 函数打补丁，因为 `bootmgr` 二进制文件没有以任何方式修改。 从这一点来看，引导代码的功能几乎与
UEFI 版本的引导代码相同，导致恶意驱动程序(位于第0轨道上，从第6扇区开始)被投放到下列位置之一，具体取决于架构: \-`\SystemRoot\System32\drivers\beep.sys (x86)` \-`\SystemRoot\System32\drivers\null.sys (x64)`

在这种情况下，加密的配置不会放入到`syslog`文件中，而是一直隐藏在损坏的磁盘的扇区5中。

![](https://images.seebug.org/content/images/2021/10/7c86fdff-c513-4100-8210-1d02642173ff.jpg-w331s)
传统版本 ESPecter 使用的修改过的磁盘方案

## 内核模式驱动程序

驱动程序的主要目的是加载用户模式的有效负载，设置键盘记录程序，并最终删除自身。设置键盘记录程序分为两个步骤: \-首先，它创建了一个名为`\device\WebBK`的设备，该设备公开了一个处理来自用户模式组件的`IRP_MJ_device_control`请求的函数。
这个函数支持一个 IOCTL (输入/输出控制)代码(`0x22C004`) ，可用于触发负责一个异步过程调用例程的注册，它用于处理截获的击键记录。 \-通过为键盘驱动程序`object\Device\KeyboardClass0`的`IRP_MJ_读取`请求设置`CompletionRoute`，可以拦截击键。

该过程完成后，任何进程都可以通过定义自己的例程并使用自定义 IOCTL `0x22C004`来记录截获的击键，并将其传递给创建的设备对象。

默认情况下，驱动程序会加载两个基本有效负载——`WinSys.dll`和 `Client.dll`——它们具有下载和执行其他有效负载的能力。第一个，
`WinSys.DLL`，它是以加密的形式嵌入到驱动程序的二进制文件中的。第二个，`Client.dll`，由
`WinSys.dll`下载到文件`\SystemRoot
\Temp\memlog`，也是以加密的形式，使用相同的加密方法——一个简单的带减法的单字节异或——但不是相同的密钥。这两个库都被解密并由驱动程序放到系统目录
`\SystemRoot\System32\`中。

通过将`WinSys.dll`和`Client.dll`库分别注入`svchost.exe`和`winlogon.exe`，可以实现它们的执行。为此，驱动程序使用
`PsSetLoadImageNotifyRoutine`注册图像加载回调例程 `NotifyRoutine`，用于执行: \-在winlogon.exe进程的上下文中，从Client.dll导出主线程 \- 在svchost.exe进程的上下文中，从WinSys.dll导出主线程

`NotifyRoutine`在执行之前在内存中挂钩`winlogon.exe`和`svchost.exe`进程映像的入口点;
然后这个挂钩负责加载和执行适当的有效负载 DLL。如下图所示，该例程只处理正在加载的第一个`svchost.exe`或 `winlogon.exe`映像。

![](https://images.seebug.org/content/images/2021/10/184374c6-826d-4357-ab7f-386be1f80036.jpg-w331s)

## 用户模式组件–WinSys.dll

WinSys.dll充当基本更新代理，定期联系其C&C服务器以下载或执行其他有效负载或执行简单命令。C&C地址以及其他值（如活动ID、bootkit版本、C&C通信尝试之间的时间和活动小时数范围）位于配置中，可从以下位置加载：
\- `HKLM\SYSTEM\CurrentControlSet\Control`注册表中的`DefaultConfig`值 \-`\SystemRoot\Temp\syslog`文件 \- 或者直接从特定磁盘扇区（传统引导版本中）获取

如果同时存在注册表和磁盘存储配置，则使用注册表中的配置。

### C&C通信

`WinSys.dll`使用HTTPS与其C&C进行通信，通过使用以下URL格式发送HTTP GET请求来启动通信：
https:///Heart.aspx？ti=&tn=&tg=&tv=

其中，`drive_ID`是主系统卷序列号的MD5散列，其他参数是识别该恶意软件实例的具体信息。

因此，C&C可以使用显示为字符串的命令ID（随意后跟命令参数）进行响应。命令的完整列表见表1。

表1. WinSys 组件 c & c 命令

命令 ID | 描述 | 网址  
---|---|---  
1或4 | Exit. | -  
2 | 使用 HTTP POST 将各种系统信息(CPU 名称、 OS 版本、内存大小、以太网 MAC 地址、已安装软件列表等)上传到预定义的 URL |
https:///GetSysteminfo.aspx  
3 | 下载或下载并执行文件到预定义的位置从预定义的 URL 使用 HTTP GET | https:///UpLoad.aspx?ti=  
5 | 重启电脑 (只适用于 windowsvista) | 不适用  
6 | 使用HTTP GET从预定义的 URL 下载新配置，并将其保存到注册表中 | https:///ModifyIpaddr.aspx?ti=  
  
## 用户模式组件-Client.dll

恶意驱动程序部署的第二个有效负载是 Client.dll。它是一个后门，支持众多的命令集(表2)
，并包含各种自动数据外泄功能，包括文档窃取、键盘记录和通过定期截屏来监视受害者的屏幕。所有收集到的数据都存储在一个隐藏的目录中，每个数据源都有单独的子目录（所用目录路径的完整列表可以从我们的
[GitHub](https://github.com/eset/malware-ioc/tree/master/especter)存储库中获得）。还要注意的是，击键的拦截是由驱动程序处理的，客户机只需要将 IOCTL
`0x22C004`发送到驱动程序的设备，以便将截获的击键保存到文件中，从而注册其日志功能。

![](https://images.seebug.org/content/images/2021/10/8bcf28bf-7bec-408b-b904-e24fc85b81ac.jpg-w331s)
客户端负载通过将 IOCTL 发送到 bootkit 的设备驱动程序来设置键盘记录器功能

客户端组件的配置应该以加密形式存在文件覆盖中。它包含诸多信息，如 c & c 地址和端口，表明应该收集哪些数据的标志(按键、屏幕截图、具有特定扩展名的文件)
，屏幕截图线程的时间段，外泄数据的最大文件大小，以及文件扩展名列表。

### C&C 通信

客户端设置了自身与 C&C 的通信通道。为了与 C&C 进行通信，它使用单字节 XOR 加密的 TCP
协议，与密钥不同，该协议应用于的非空消息字节，在这里分析的活动中，密钥是`0x66`。通信是通过向配置中指定的 IP: PORT
对发送信标消息来启动的。此消息包含`drive_ID`值(主系统卷的序列号 MD5散列)以及一个指定消息类型的值，即命令请求或上传收集的数据。

在执行 C&C 命令后，结果将报告给 C&C，并指定执行操作的结果代码、命令
ID，有趣的是，每个这样的结果报告消息都带有一个水印/标记，表示位于偏移量`0x04`的宽字符串`WBKP`，这使得在网络级别识别这种恶意通信更加容易。
表2. 客户端 C&C 命令列表

命令 ID | 描述  
---|---  
0x0000 | 停止后门  
0x0064 | 执行从 C&C 接收的命令行并使用管道捕获输出  
0x00C8 | 根据 C&C 命令参数的值，执行电源命令下线、断电、重新启动或关机  
0x012C | 截取前景窗口的屏幕快照，完整的屏幕快照，或者根据参数值改变自动的屏幕快照参数  
0x0190 | 执行各种文件系统操作  
0x01F4 | 上传收集的数据和文件  
0x0258 | 执行各种与服务相关的命令  
0x02BC | 执行各种与进程相关的命令  
0x0320 | 修改配置值  
0x0384 | 停止/启动键盘记录器，具体取决于参数的值  
  
## 总结

ESPecter可以说明，在前OS持久性方面，威胁行为者不仅依赖 UEFI 固件植入，他们还投入时间创建了恶意软件，但由于有 UEFI Secure
Boot 等现有安全机制的存在，如果启用和配置正确，这些恶意软件很容易被这些机制阻止。

## IoCs

一个完整的 IoCs 和示例列表可以在我们的 [GitHub](https://github.com/eset/malware-ioc/tree/master/especter) 存储库中找到。

### ESET 检测

EFI/Rootkit.ESPecter Win32/Rootkit.ESPecter Win64/Rootkit.ESPecter

### C&C IP 地址和域的配置

    
    
    196.1.2[.]111
    103.212.69[.]175
    183.90.187[.]65
    61.178.79[.]69
    swj02.gicp[.]net
    server.microsoftassistant[.]com
    yspark.justdied[.]com
    crystalnba[.]com

### Legacy版本安装程序

    
    
    ABC03A234233C63330C744FDA784385273AF395B
    DCD42B04705B784AD62BB36E17305B6E6414F033
    656C263FA004BB3E6F3EE6EF6767D101869C7F7C
    A8B4FE8A421C86EAE060BB8BF525EF1E1FC133B2
    3AC6F9458A4A1A16390379621FDD230C656FC444
    9F6DF0A011748160B0C18FB2B44EBE9FA9D517E9
    2C22AE243FDC08B84B38D9580900A9A9E3823ACF
    08077D940F2B385FBD287D84EDB58493136C8391
    1D75BFB18FFC0B820CB36ACF8707343FA6679863
    37E49DBCEB1354D508319548A7EFBD149BFA0E8D
    7F501AEB51CE3232A979CCF0E11278346F746D1F

### 受损的windows启动管理器

    
    
    27AD0A8A88EAB01E2B48BA19D2AAABF360ECE5B8
    8AB33E432C8BEE54AE759DFB5346D21387F26902

## MITRE ATT&CK 技术

下表是使用 MITRE ATT&CK 框架的第9版构建的。

策略 | ID | 名称 | 技术  
---|---|---|---  
Execution | T1106 | ative API | ESPecter leverages several Windows APIs:
VirtualAlloc , WriteProcessMemory, and CreateRemoteThread for process
injection.  
Persistence | T1542.003 | Pre-OS Boot: Bootkit | ESPecter achieves persistence
by compromising Windows Boot Manager (bootmgfw.efi) located on the ESP, or by
modifying the MBR on Legacy Boot systems.  
| T1547 | Boot or Logon Autostart Execution | ESPecter replaces the legitimate
null.sys or beep.sys driver with its own malicious one in order to be executed
on system startup.  
Defense Evasion | T1055.001 | Process Injection: Dynamic-link Library
Injection | ESPecter’s driver injects its main user-mode components into
svchost.exe and winlogon.exe processes.  
| T1564.001 | Hide Artifacts: Hidden Files and Directories | ESPecter’s
Client.dll component creates hidden directories to store collected data.  
| T1564.005 | Hide Artifacts: Hidden File System | ESPecter bootkit installers
for Legacy Boot versions use unallocated disk space located right after the
MBR to store its code, configuration and malicious driver.  
| T1140 | Deobfuscate/Decode Files or Information | ESPecter uses single-byte
XOR with subtraction to decrypt user-mode payloads.  
| T1562 | Impair Defenses | ESPecter patches Windows kernel function directly
in memory to disable Driver Signature Enforcement (DSE).  
| T1036.003 | Masquerading: Rename System Utilities | ESPecter bootkit
installers for Legacy Boot versions copy cmd.exe to con1866.exe to evade
detection.  
| T1112 | Modify Registry | ESPecter can use DefaultConfig value under
HKLM\SYSTEM\CurrentControlSet\Control to store configuration.  
| T1601.001 | Modify System Image: Patch System Image | ESPecter patches
various functions in Windows Boot Manager, Windows OS loader and OS kernel
directly in memory during the boot process.  
| T1027.002 | Obfuscated Files or Information: Software Packing | ESPecter’s
WinSys.dll component is packed using the MPRESS packer.  
| T1542.003 | Pre-OS Boot: Bootkit | ESPecter achieves persistence by
modifying Windows Boot Manager (bootmgfw.efi) located on the ESP or by
modifying the MBR on Legacy Boot systems.  
| T1553.006 | Subvert Trust Controls: Code Signing Policy Modification |
ESPecter patches Windows kernel function SepInitializeCodeIntegrity directly
in memory to disable Driver Signature Enforcement (DSE).  
| T1497.003 | Virtualization/Sandbox Evasion: Time Based Evasion | ESPecter’s
WinSys.dll component can be configured to postpone C&C communication after
execution or to communicate with the C&C only in a specified time range.  
Credential Access | T1056.001 | Input Capture: Keylogging | ESPecter has a
keylogging capability.  
Discovery | T1010 | Application Window Discovery | ESPecter’s Client.dll
component reports foreground window names along with keylogger information to
provide application context.  
| T1083 | File and Directory Discovery | ESPecter’s Client.dll component can
list file information for specific directories.  
| T1120 | Peripheral Device Discovery | ESPecter’s Client.dll component
detects the insertion of new devices by listening for the WM_DEVICECHANGE
window message.  
| T1057 | Process Discovery | ESPecter’s Client.dll component can list running
processes and their loaded modules.  
| T1012 | Query Registry | ESPecter’s WinSys.dll component can check for
installed software under the Registry key
HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall.  
| T1082 | System Information Discovery | ESPecter user-mode payloads can
collect system information from the victim’s machine.  
| T1124 | System Time Discovery | ESPecter’s WinSys.dll component can use
GetLocalTime for time discovery.  
Collection | T1119 | Automated Collection | ESPecter’s Client.dll component
can automatically collect screenshots, intercepted keystrokes and various
files.  
| T1025 | Data from Removable Media | ESPecter’s Client.dll component can
collect files with specified extension from removable drives.  
| T1074.001 | Data Staged: Local Data Staging | ESPecter’s Client.dll
component stores automatically collected data into a hidden local directory.  
| T1056.001 | Input Capture: Keylogging | ESPecter has keylogging
functionality.  
| T1113 | Screen Capture | ESPecter’s Client.dll component has screen capture
functionality.  
Command and Control | T1071.001 | Application Layer Protocol: Web Protocols |
ESPecter’s WinSys.dll component communicates with its C&C server over HTTPS.  
| T1573.001 | Encrypted Channel: Symmetric Cryptography | ESPecter’s
Client.dll component encrypts C&C traffic using single-byte XOR.  
| T1105 | Ingress Tool Transfer | ESPecter’s user-mode components can download
additional payloads from C&C.  
| T1104 | Multi-Stage Channels | ESPecter’s user-mode components use separate
C&C channels.  
| T1095 | Non-Application Layer Protocol | ESPecter’s Client.dll component
uses TCP for C&C communication.  
Exfiltration | T1020 | Automated Exfiltration | ESPecter’s Client.dll
component creates a thread to automatically upload collected data to the C&C.  
| T1041 | Exfiltration Over C2 Channel | ESPecter exfiltrates data over the
same channel used for C&C.  
| T1029 | Scheduled Transfer | ESPecter’s Client.dll component is set to
upload collected data to the C&C every five seconds.  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1738/>

