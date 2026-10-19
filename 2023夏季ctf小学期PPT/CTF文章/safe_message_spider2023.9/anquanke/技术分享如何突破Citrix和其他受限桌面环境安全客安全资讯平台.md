# 【技术分享】如何突破Citrix和其他受限桌面环境

阅读量 **462639**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-06-07 14:00:40

 **x**

##### 译文声明

本文是翻译文章，文章来源：pentestpartners.com

原文地址：<https://www.pentestpartners.com/security-blog/breaking-out-of-citrix-and-other-restricted-desktop-environments/>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

翻译：[ **興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

**一、前言**

许多组织及机构正逐步转向虚拟化架构，包括应用及桌面的虚拟化。这一过程通常会涉及如Citrix之类的虚拟化平台来提供服务。

对虚拟化平台而言，如果你配置不当或者锁定失败，那么用户可能会打破你原以为牢不可破的虚拟化环境。可能随后不久，你就会发现你的整个域都被攻陷了。

在这之前，网上可能有很多教程指导用户如何突破受限桌面环境，但据我们所知，这方面还没有一个全面的教程囊括受限桌面环境突破的各种办法。

这正是本文的目的所在，我们希望这是一篇实用的文章。当然，本文也会是一篇不断更新的文章，虽然我们做了大量的努力和研究，但可以肯定的是，我们没有覆盖每一种攻击方法。如果你认为我们在某些方面有所欠缺，请及时告知我们加以补充。

  

**二、对话框**

获取一个对话框通常是突破虚拟化环境的首个突破口，如果系统经过某种加固，这种方法常常能起到奇效。

即使你只能看到一个非常简单的Notepad应用，你手头上还是有许多可选项的。

即使看起来最为无害、最为简单的应用也可能导致客户域被攻陷，这一点上已经有很多现实案例了。这种现象通常被称为“滚雪球”效应，其中某个小问题引发另一个问题，最终导致整个环境存在极大的安全风险。

许多标准的Windows应用程序通常都会提供某种接口来打开一个对话框：

当然有很多种方法可以打开一个对话框，然而，最简单的方法是：

1、“另存为（Save as）”/“打开为（Open as）”菜单项。

2、“打印（Print）”菜单项：选择“打印到文件（print to file）”选项（比如XPS/PDF等）。

  

**三、滥用对话框**

打开对话框之后，我们可以此为立足点，开始探索整个系统，或者用来提升权限。能达到什么效果通常与你的创造力有关，但我们通常可以有以下几种方案：

**1、创建新文件**

（1）批处理文件：右键，依次选择“新建（New）”、“文本文件（Text
File）”，重命名为.BAT（或者.CMD）文件，之后选择“编辑（Edit）”，“打开（Open）”。

（2）快捷方式：右键，依次选择“新建（New）”、“快捷方式（Shortcut）”、选择“%WINDIR%system32”。

**2、打开新的Windows资源管理器实例**

在任意文件夹上右键，选择“在新窗口中打开（Open in new window）”。

**3、探索上下文菜单**

（1）在任意文件或目录上右键，观察上下文菜单。

（2）点击“属性（Properties）”，重点观察对象是快捷方式，选择“打开文件路径（Open File Location）”按钮。

**4、输入框**

许多输入框都会接受文件路径，你可以尝试输入UNC路径，如“//attacker–pc/”或者“//127.0.0.1/c$”或者“C:”。

**5、绕过文件限制**

在“文件名（File name）”框中，输入“*.*”或者“*.exe”。

  

**四、帮助菜单**

帮助菜单有多种存在形式，但我们重点关注的是应用程序的帮助菜单以及通用的“Windows帮助及支持”菜单（可以通过Windows+F1快捷方式启动）。

帮助菜单中通常具有链接及快捷方式，以提供各种功能。如下图所示，用户可以点击其中的链接打开命令提示符：

其他方式：

1、在任意空白处点击右键，选择“查看源码（view source）”，通常会打开一个notepad实例。

2、顶部的打印图标可以引出一个打印对话框。

3、你可以通过语言栏访问帮助菜单。许多需要提供多语言服务的环境中（比如机场）经常会遇到这种场景。

4、许多应用程序经常会在开始菜单中带有指向厂商网页的超链接（比如www.vendor.com）。点击这种链接通常可以引出一个IE浏览器窗口，这也是一个突破口。

  

**五、环境变量/绕过路径限制**

某些系统做了些加固处理，我们无法直接访问某个敏感路径，如“C:WindowsSystem32”目录。但我们还是有可能使用各种符号链接绕过这个限制。

    
    
    %ALLUSERSPROFILE%
    %APPDATA%
    %CommonProgramFiles%
    %COMMONPROGRAMFILES(x86)%
    %COMPUTERNAME%
    %COMSPEC%
    %HOMEDRIVE%
    %HOMEPATH%
    %LOCALAPPDATA%
    %LOGONSERVER%
    %PATH%
    %PATHEXT%
    %ProgramData%
    %ProgramFiles%
    %ProgramFiles(x86)%
    %PROMPT%
    %PSModulePath%
    %Public%
    %SYSTEMDRIVE%
    %SYSTEMROOT%
    %TEMP%
    %TMP%
    %USERDOMAIN%
    %USERNAME%
    %USERPROFILE%
    %WINDIR%
    shell:Administrative Tools
    shell:DocumentsLibrary
    shell:Libraries
    shell:UserProfiles
    shell:Personal
    shell:SearchHomeFolder
    shell:System
    shell:NetworkPlacesFolder
    shell:SendTo
    shell:UserProfiles
    shell:Common Administrative Tools
    shell:MyComputerFolder
    shell:InternetFolder

我们也可以使用文件协议前缀，打开使用其他方式无法打开的应用程序：

    
    
    about:
    data:
    ftp:
    mailto:
    news:
    res:
    telnet:
    view-source:

即使在某些经过大量加固处理的系统上，我们也是有可能使用UNC路径：

    
    
    \127.0.0.1c$WindowsSystem32

**六、夺取命令提示符**

如果我们能够访问命令提示符，那么我们在突破受控系统上已经取得了第一阶段的胜利，我们可以借此获取操作系统的许多控制权，比如枚举许多有用的信息，为权限提升做准备。许多系统的加固强度不够大，在开始菜单中都能看到cmd.exe的标准快捷方式，我们自然可以将这个接口当成第一个突破口：

通常情况下，我们可以使用多个可执行程序获取系统的shell接口：

1、Cmd.exe

2、COMMAND.COM

3、Powershell.exe

4、第三方的管理/shell工具

**6.1 通过“运行（Run）”对话框**

这可能是最简单的一种办法。可以通过开始菜单或者“Windows+R”快捷键打开运行对话框：

**6.2 通过资源管理器**

这也是种简单有效的方法。浏览包含可执行程序的目录（例如“C:windowssystem32”），我们可以选择可执行程序，在弹出的右键菜单中选择：

**6.3 文件拖放**

我们可以将任何文件拖放到cmd.exe文件上（即便不正确的扩展名，如*.txt也可以），这样会弹出一个命令提示符窗口：

**6.4 超链接/快捷方式**

我们可以利用文件处理器，使用与可执行程序绑定的链接。这个链接可以在许多地方使用，比如对话框、在微软Office内部按住CTRL再点击链接等等。这个链接为“file:///c:/Windows/System32/cmd.exe”。

**6.5 任务管理器**

Windows的任务管理器能帮我们不少忙，此外，它也可以用来创建新的进程。我们可以通过各种方式启动任务管理器（taskmgr），比如开始菜单、较新版的Windows中的CTRL+ALT+DELETE组合键，以及直接使用CTRL+SHIFT+ESCAPE组合键。

**6.6 计划任务（Task Scheduler）**

这是个非常有趣的薄弱点。某些系统可能会限制cmd.exe的访问，但还是可以通过计划任务启动cmd.exe。我们可以用过命令行形式的计划任务工具（at.exe）或者GUI形式的计划任务工具（taskschd.msc）完成这一任务。在计划任务中，我们可以指定在特定时间（如1分钟内）或者特定事件（如用户登录）发生时运行cmd.exe。

**6.7 COMMAND.COM**

这是Windows出于兼容性而保留的一个16位程序。即使cmd.exe被禁用，这个程序通常也是可以访问的。不幸的是，64位的Windows中再也不提供COMMAND.COM了。

**6.8 Powershell.exe**

与cmd.exe类似，但PowerShell具备某些更加高级的功能，例如它可以使用并调用.NET的某些功能。

**6.9 MSPAINT.exe**

这是一种不常用但行之有效的方法，我们可以在微软的画图工具中绘制特定的颜色，创建指向cmd.exe的快捷方式，最终获取shell接口。其原理与创建BMP文件所使用的编码算法有关，我们可以小心选择特定的RGB颜色，将ASCII数据写入到某个文件中。

1、打开MSPaint.exe，设置画布大小为：宽度=6，高度=1像素。

2、放大画布，以便操作。

3、使用颜色选择器，按从左到右的顺序，依次使用以下数值设置像素值：

（1）R: 10, G: 0, B: 0

（2）R: 13, G: 10, B: 13

（3）R: 100, G: 109, B: 99

（4）R: 120, G: 101, B: 46

（5）R: 0, G: 0, B: 101

（6）R: 0, G: 0, B: 0

4、将该图保存为24位位图（*.bmp；*.dlib）

5、将其扩展名从bmp改为bat，然后运行。

**6.10 绕过交互式控制台限制**

当交互式命令提示符被禁用时，我们通常可以使用“/K”或者“/C”参数运行cmd.exe。我们可以使用“cmd.exe /K
pause”命令，就能绕过限制，载入一个交互式shell：

此外，我们也可以将“/C”参数传递给cmd.exe，创建一个非交互式的命令提示符会话。比如，我们可以使用如下命令“cmd.exe /C tasklist >
c:tasks.txt”。

**6.11 FTP方式**

虽然FTP客户端不能提供完全形式的命令行访问接口，但它通常是可用的，在其他通道都被堵死的情况下，我们可以在FTP客户端中使用“!dir”命令，罗列系统文件。此外，FTP客户端也可以用来传输数据，下载第三方工具。

其他一些有用的FTP命令：

    
    
    !whoami
    !date
    !ping 127.0.0.1

**七、绕过写入限制**

绕过目标环境的写入限制是非常重要的一点，我们可以借助这类技术，找到上传第三方工具以及写入数据的系统区域。

在一个理想的环境中，最好的管理原则就是用户只能具备最低的写入权限，同时不会对其正常工作造成影响。在现实中，这意味着用户在本地文件系统中只能具备非常低的写权限。

临时目录是一个很好的突破口，用户几乎总是具备该目录的写权限。我们可以通过“%TEMP%”环境变量，枚举默认的临时目录位置，类似的命令为“echo
%TEMP%”。临时文件目录通常为：

1、C:UsersUSERAppDataLocalTemp

2、C:temp

3、C:tmp

当然“%USERPROFILE%”目录也是另一个选择，不过该目录有可能会链接到某个网络共享文件夹。

Accesschk.exe

该工具属于Sysinternals工具集中的一员，与“cacls”/“icacls”功能类似。

我们可以使用这个工具，查找文件系统中我们具备哪些目录的写权限：

accesschk.exe -uwdqs Users c:

accesschk.exe -uwdqs “Authenticated Users” c:

  

**八、绕过执行限制**

某些系统会使用白名单机制，只允许某些具备特定文件名或文件扩展名的应用程序运行。有些时候，我们可以将malware.exe重命名为白名单中的合法名称（如mspaint.exe），绕过白名单限制。

在某些配置不当的环境中，只要目录符合白名单标准，任何应用程序都可以运行。如果你正在测试的系统允许运行微软的Word程序，你可以尝试将待运行的程序拷贝到WINWORD.EXE所在的目录加以运行。

  

**九、Internet Explorer浏览器**

许多Web应用程序使用类似Citrix/远程服务/Kiosk平台之类的技术进行分发部署。因此，大多数情况下，这意味着用户需要Web浏览器才能访问这些应用程序。以老版本的Internet
Explorer（IE）浏览器为例，我们可以借助IE浏览器，使用多种方式完成我们的任务：

**9.1 对话框及菜单栏**

1、地址栏：我们可以使用地址栏，填入前文提到过的各种路径及环境变量。例如可以使用 “file://c:windowssystem32cmd.exe” 路径。

2、菜单栏：帮助菜单、打印菜单以及搜索菜单都包含某些链接及选项，可能指向并打开浏览器之外的外部资源（如Windows资源管理器）。

3、右键点击：右键菜单中包含某些非常有用的选项，比如“查看源码”（notepad）以及“保存图片为”菜单。

4、收藏菜单：打开收藏选项卡（ALT+C），将文件夹拖到浏览器窗口中，任意项目（如“MSN站点”）都可以。

**9.2 主页**

我们可以将浏览器主页设置为任意值（如“cmd.exe”）来访问任意文件，当然这是一种快速但略不文雅的方法。

**9.3 F12开发者工具**

在IE浏览器中，我们可以使用F12快捷键打开开发者工具。选择“文件（File）”菜单中的“自定义Internet
Explorer视图源”选项，我们有可能可以自主选择自定义程序。

根据我们的目的，我们可以选择“C:windowssystem32cmd.exe”作为视图源，这样cmd.exe就成为IE中默认的HTML源代码查看器。最后，我们可以在某个网页上点击右键，选择“查看源码（View
Source）”，开始探索旅途。

**9.4 证书导入**

载入IE设置，转到“内容（Content）”选项卡，然后选择“证书（Certificates）”按钮。点击“导入（Import）”选项，会弹出如下向导：

向导的下一步会要求我们填入证书路径，这将打开一个Windows资源管理器（或者文件浏览类型）对话框。我们可以使用“三、滥用对话框”这一部分中的技巧来打破受限环境及提升权限。

**9.5 浏览器附加组件/小程序/动态内容**

默认情况下，IE的设计初衷是提供界面友好且内容丰富的用户体验。我们可以利用这一点，通过浏览器自身功能实现与操作系统的交互。在IE浏览器不被限制的情况下，我们可以使用ActiveX附加组件、Flash应用、Java小程序以及类似技术完成这一任务。

**9.6 基于浏览器的漏洞利用**

如果系统没有及时打补丁，不同版本的IE浏览器可能存在许多漏洞，攻击者可以访问精心构造的某个链接来利用这些漏洞。典型的利用平台就是Metasploit平台。

当然我们也可以诱骗系统上的另一个用户点击我们精心构造的那个链接，这意味着恶意代码会以这些用户的身份运行，如果这些用户是高权限账户那再好不过。

  

**十、微软Office**

与IE浏览器类似，大多数环境中都提供Office套装以满足用户办公需求。同样，这也为我们提供了众多可利用的点。

**10.1 VBA（Visual Basic for Applications）脚本及宏**

我们可以使用msfencode/msfpayload轻松生成VBA代码，创建目标主机上的反弹型shell或Meterpreter
shell。这种方法很少会被反病毒软件阻止。虽然Meterpreter
shell非常有用，但以这种方式创建的shell会运行在当前文档用户的上下文环境中。当然我们可以根据目标系统的具体安全性设置，使用Meterpreter来提升权限。

**10.2 开发者工具**

所有的Office应用中都提供开发者工具，但这项功能默认情况下并没有被启用。不同版本启用开发者工具的方法有所不同，以Office
2010为例，该选项位于应用程序选项的“自定义功能区”选项卡中。开发者工具一旦启用，各种加载项就可以为我们提供丰富的功能。

开发者工具中包含大量与操作系统交互的ActiveX控件。如果IE浏览器被禁用，但Excel并没有被禁用，我们为什么不创建自己的Web浏览器呢？

**10.3 通过VBA运行命令**

通过宏或者VBA代码，我们只需要简单的三行代码就能启动外部应用程序：

    
    
    Sub OpenCMD()
    Shell “CMD /K C:windowssystem32cmd.exe”, vbNormalFocus
    End Sub

**10.4 MS SQL服务器（本地及远程）**

虽然这是条较为漫长的道路，但如果我们能够访问微软出品的SQL服务器（特别是老版本的服务器），这种方法还是值得一试的。我们可以检查SQL服务器是否启用了XP_CMDSHELL组件。如果服务器缺乏访问限制或者用户控制机制，我们有可能可以在该服务器上执行命令并最终远程控制它。

**10.5 对话框及快捷键**

这又是对话框的一种利用方式。我们可以在标准文档（如Word文档）中嵌入简单的指向文件系统的快捷方式（如file://）。

  

**十一、修改ICA文件**

Citrix的某些配置依赖.ICA（Independent Computing
Architecture，独立计算结构）文件来存放某个连接的配置信息。这些配置信息中包含许多明显的特征参数，比如服务器地址以及端口信息，当然还有许多更加有趣的参数可以为我们所用。

简单的ICA文件形式如下：

    
    
    [Encoding]
    InputEncoding=ISO8859_1[WFClient]
    Version=2
    username=username
    clearpassword=password
    [ApplicationServers]
    ApplicationName=
    [ApplicationName]
    Address=IPAddress
    InitialProgram=notepad.exe
    TWIMode=On
    TransportDriver=TCP/IP
    WinStationDriver=ICA 3.0
    BrowserProtocol=HTTPonTCP

如上所示，“InitialProgram”参数表明，连接建立后，系统应该创建一个Notepad实例。如果系统没有经过加固，我们只需要将该参数简单修改为“cmd.exe”就可以为“Explorer.exe”弹出命令提示符窗口：

    
    
    InitialProgram=cmd.exe

某些应用程序可能需要进一步的身份验证，当前的身份无法奏效。我们可以模糊测试（fuzz）“InitialProgram”这个参数，枚举潜在有效的可执行程序。

Nmap（使用citrix-enum-apps这个NSE插件）以及Metasploit（使用auxiliary/gather/citrix_published_applications）可以用来枚举已发布的应用程序，互联网中还有许多类似的公开脚本可以完成同样工作。

  

**十二、默认/弱凭证**

在任何环境中，挖掘探索默认的用户名/密码组合或者使用弱口令（如“password”）的账户显然是攻击行动中非常关键的一环。

如果可能的话，你在发起攻击前应尝试枚举获取可用的用户名列表。我们可以通过错误信息判断某个账户是否存在，比如“该用户名不存在”以及“密码错误”这类错误消息都能提供有用的信息。“忘记密码”功能通常也能告诉我们某个用户是否存在。

如果你已经通过验证，也能获取一个shell，你可以尝试使用“net users”以及“net users /domain”命令。

包括如下用户名在内的许多用户名总是值得尝试的。很多情况下，账户的密码有可能就是用户名：

    
    
    test
    citrixtest
    administrator
    admin
    guest
    backup
    default

**十三、目标中的文件传输**

我们会简单介绍一下目标环境中可以使用的某些方法：

1、FTP

2、HTTP服务器（WAMP/LAMP以及其他一些公开工具）

3、SMB客户端工具 \hackertools

4、SMB服务端工具 \serverc$

5、DNS隧道

6、电子邮件（私人或企业邮件）

7、剪贴板

8、基于用户输入的流数据

9、设备穿透技术（RS323/串口、火线接口）

以上某些方法需要在攻击环境中架设服务器，不过这并不麻烦，Kali Linux中已经集成了许多服务，我们可以直接使用。

**13.1 DNS隧道**

即使在高度受限的环境中，DNS查询请求还是有可能可以抵达外部互联网，这是非常有趣的一个事实。我们在另一篇文章中单独介绍了这个技术点。

**13.2 电子邮件**

如果Web浏览器可用，通常情况下电子邮件也是可用的，我们可以使用个人电子邮件账户（如Gmail）传输目标主机上的数据。根据目标环境具体的防火墙策略以及网络过滤规则，我们可以探索哪种邮件协议可用，如POP3、IMAP以及SMTP协议。

全功能桌面环境可能具备公司邮件系统的访问权限，我们也可以使用类似的方式利用这一点。需要注意的是，许多企业（特别是大型公司）的邮箱系统通常会采取基于附件的内容过滤机制，我们可以使用加密数据（如ZIP）附件绕过这一限制。

**13.3 剪贴板**

剪贴板也是传输数据的一种方法。二进制文件可以先经过BASE64编码，在远程系统上解码重构以便执行。此外，我们也可以使用剪贴板传输汇编语言代码，然后在远程主机上使用debug.exe执行这些代码。

**13.4 基于用户输入的流数据**

利用用户输入的标准接口（比如键盘及鼠标），我们可以创建一个模拟用户输入的自动脚本来发送数据，数据可以使用慢速流进行传输，在另一端重构即可。

例如Rubber Ducky之类的可重新编程的人机接口设备（Human Interface
Devices，HIDs）正是这类攻击的优良载体。我的一名同事，David Lodge，写了篇文章详细介绍了这类攻击。

**13.5 设备穿透**

根据目标所在的具体环境，我们有可能穿透本地硬件设备（如USB存储设备）到达远程主机。某些客户端，例如微软的远程桌面协议以及Citrix
Receiver实际上使用了自动化的设备穿透机制，当然这个功能可以根据需要手动进行修改。

对于微软的远程桌面应用而言，启动远程服务客户端（mstsc.exe），选择“本地资源”标签页，点击窗口底部的“更多”按钮，我们可以选择本地哪种设备及驱动会被传递到远程主机。

对Citrix Receiver来说操作类似，在连接建立之前，我们可以转到桌面查看器首选项，选择“设备（Devices）”标签页：

连接建立后，我们也可以使用状态栏重复类似操作：

**13.6 设备穿透（RS232/串口）**

如果类似串口之类的设备也能够通过设备穿透技术进行连接，那么主机及服务器之间传输数据就会更加便捷。可用的串口列表可以在本地主机枚举获得，流数据可以经过串口传输到服务器。在服务端，我们可以使用终端应用程序（如Windows
HyperTerminal或者使用debug.exe编译的自定义程序）来接受数据。

**13.7 设备穿透（火线接口）**

安全社区对火线接口的印象不佳，原因在于它们容易受到物理内存攻击的影响。这类攻击利用了火线中的某个“功能”，使连接火线的外部设备能够具备DMA（Direct
Memory Access，直接内存访问）能力。从理论上讲，支持DMA功能的某些模拟火线设备（例如Apple
iPod）也可能使用设备穿透功能，然后该设备就可能具备远程内存的完全读写权限。这将带来严重的问题，因为内存中很有可能包含敏感数据，比如用户凭证、加密密钥等。

  

**十四、实用的系统/管理工具**

当Windows系统经过加固后，某些内置的用于系统管理的默认工具可能会被管理员忘记加固，因此可以为攻击者所用。其中大部分工具可以使用前文介绍的方法来运行;

1、MMC.exe：微软管理控制台，允许我们使用“管理单元“控制许多系统功能。

2、Mstsc.exe：微软远程服务，用来连接到另一台主机。

3、Regedit.exe：注册表控制工具。

4、Taskmgr.exe：任务管理器。

5、Control.exe：控制面板快捷方式。

6、Rundll32.exe：利用该工具可以调用原生API访问隐藏的系统功能。

7、Dxdiag.exe：DirecX诊断工具，可以用来收集系统信息。

8、Msconfig.exe：系统配置工具，可以显示许多系统信息，包含指向系统工具的链接。

9、Eventvwr.exe：本地事件查看器。

10、Systeminfo.exe：系统信息收集器的命令行工具。

11、Msinfo32.exe：系统信息收集。

12、Osk.exe：虚拟键盘程序，在没有键盘的环境中十分有用。

13、At.exe：计划任务调度程序命令行版。

14、Taskschd.msc：计划任务调度程序界面版。

15、Explorer.exe：创建一个新的Windows资源管理器实例。

16、WMIC.exe

17、Qwinsta.exe：显示RDP会话相关信息。

18、Tasklist.exe /qprocess.exe：列出进程信息。

当然有时候枚举当前可用的本地或第三方可执行文件也是非常有用的：

    
    
    dir /s %WINDIR% *.exe

**14.1 Rundll32**

通过Rundll32，我们可以运行许多命令，常见的命令如下所示：

已保存的用户名及密码：

    
    
    RunDll32.exe keymgr.dll,KRShowKeyMgr

控制面板：

    
    
    RunDll32.exe shell32.dll,Control_RunDLL

日期及时间属性：

    
    
    RunDll32.exe shell32.dll,Control_RunDLL timedate.cpl

设备管理器：

    
    
    RunDll32.exe devmgr.dll DeviceManager_Execute

文件管理器属性：

    
    
    RunDll32.exe shell32.dll,Options_RunDLL 0

忘记密码向导：

    
    
    RunDll32.exe keymgr.dll,PRShowSaveWizardExW

键盘属性：

    
    
    RunDll32.exe shell32.dll,Control_RunDLL main.cpl @1

锁定屏幕：

    
    
    RunDll32.exe user32.dll,LockWorkStation

网络链接：

    
    
    RunDll32.exe shell32.dll,Control_RunDLL ncpa.cpl

弹出打开方式对话框：

    
    
    Rundll32 Shell32.dll,OpenAs_RunDLL FILE.ext

打印机用户界面：

    
    
    Rundll32 Printui.dll,PrintUIEntry /?

系统属性对话框：

    
    
    Rundll32 Shell32.dll,Control_RunDLL Sysdm.cpl,,3

Windows防火墙：

    
    
    RunDll32.exe shell32.dll,Control_RunDLL firewall.cpl

Windows关于对话框：

    
    
    RunDll32.exe SHELL32.DLL,ShellAboutW

**14.2 WMIC.exe**

WMIC（Windows Management Instrumentation Command-Line）是一个非常强大的命令行工具，可以用来收集信息：

WMIC覆盖的范围非常广泛，我们只选取某些使用案例：

本地共享：

    
    
    wmic share list /format:table

本地用户：

    
    
    wmic useraccount list full

本地用户 – 输出到HTML文件：

    
    
    wmic /output:c:users.html useraccount list full /format:hform

进程：

    
    
    wmic process list full

服务：

    
    
    wmic service list full

软件：

    
    
    wmic os lsit full

已安装的补丁/服务包/修补程序：

    
    
    wmic qfe

**十五、快捷方式**

与大多数操作系统一样，Windows中经常使用的功能都会有快捷方式。特别是系统加固方式只是浮于表面时（例如只是简单删除了开始菜单链接），某些快捷方式在这种场景中就显得尤为有用。

**15.1 标准的操作系统快捷方式**

我们可以在Windows系统的许多地方创建标准的系统快捷方式，比如我们可以尝试在桌面或者资源管理器中点击右键，在弹出的右键菜单中创建指向其他资源的链接，如“%WINDIR%system32cmd.exe“。

**15.2 辅助功能快捷键**

许多快捷方式指向的是辅助功能，比如“粘滞键“以及”鼠标按键“等。按下正确的组合键会弹出相应的对话框，这些对话框可以用来访问轻松访问中心（Ease of
Access Centre，EAC）。我们可以使用EAC作为突破口。

1、粘滞键：按下SHIFT键5次。

2、鼠标按键：SHIFT+ALT+NUMLOCK

3、高对比度：SHIFT+ALT+PRINTSCN

4、切换键：按住NUMLOCK键5秒钟

5、过滤键：按住右SHIFT键12秒钟

其他标准快捷方式也有用处，有些快捷键与特定程序有关：

1、WINDOWS+F1 – Windows搜索

2、WINDOWS+D – 显示桌面

3、WINDOWS+E – 启动Windows资源管理器

4、WINDOWS+R – 运行对话框

5、WINDOWS+U – 轻松访问中心

6、WINDOWS+F – 搜索

7、SHIFT+F10 – 右键上下文菜单

8、CTRL+SHIFT+ESC – 任务管理器

9、CTRL+ALT+DEL – 显示锁定屏幕

10、F1 – 帮助

11、F3 – 搜索

12、F6 – 地址栏

13、F11 – IE浏览器会进入全屏模式

14、CTRL+H – IE浏览器历史记录

15、CTRL+T – IE浏览器新标签页

16、CTRL+N – IE浏览器新页面

17、CTRL+O – 打开文件

18、CTRL+S – 保存

19、CTRL+N – 新建

  

**十六、RDP/Citrix快捷方式**

Citrix以及微软远程桌面协议（RDP）有一套自己的快捷方式或者“热键“，对应操作系统功能或者其他功能。

**16.1 远程桌面热键**

1、CTRL+ALT+END – 打开Windows安全对话框

2、CTRL+ALT+BREAK – 在窗口和全屏之间切换

3、ALT+INSERT – 循环切换窗口

4、ALT+HOME – 显示开始菜单

5、ALT+DELETE – 显示控制/上下文菜单

6、CTRL+ALT+NUMBER 结合-号 – 截取活动窗口屏幕并保存到RDP剪贴板中

7、CTRL+ALT+NUMBER 结合+号 – 截取整个RDP会话屏幕并保存到RDP剪贴板中

**16.2 Citrix ICA热键**

1、SHIFT+F1 – 显示Windows任务列表

2、SHIFT+F2 – 切换标题栏

3、SHIFT+F3 – 关闭远程应用/Citrix连接

4、CTRL+F1 – 显示Windows NT安全桌面

5、CTRL+F2 – 显示远程任务列表或者开始菜单

6、CTRL+F3 – 显示任务管理器

7、ALT+F2 – 循环切换最大化及最小化窗口

8、ALT+PLUS – 循环切换已打开的窗口

9、ALT+MINUS – 反向循环切换已打开的窗口

  

**十七、批处理文件及脚本**

当交互式shell被禁用时，我们可以使用诸如.BAT和.CMD之类的批处理文件来执行系统命令。虽然.BAT文件可能会被禁用，但较为陌生的.CMD文件有时候还是能发挥作用的。

**17.1 Windows脚本宿主（Windows Script Host，WSH）**

假如“cscript.exe“或者”wscript.exe“未被禁用，我们可以使用WSH来运行许多脚本语言，默认情况下可以运行VBScript、VBA以及JScript语言。

例如，我们可以执行如下VBScript片段，将代码片段保存为.VBS文件即可。使用这段代码，我们有可能可以启动一个CMD命令行：

    
    
    set objApp = CreateObject(“WScript.Shell”)
    objApp.Run “CMD C:”

我们可以通过双击方式来运行这个VBS文件，也可以将文件名作为参数传递给cscript.exe或者wscript.exe来运行。

系统支持的其他语言也有可能被攻击者滥用，如Python、Perl、PHP等，我们可以尝试使用这些语言。许多主机上默认会安装Java运行环境，我们可以采用类似方式使用javac.exe以及java.exe完成命令运行目的。

  

**十八、敏感文件及数据**

许多敏感数据对（快速）权限提升来说非常有用。总会有某些人会以明文形式将密码保存在某个文件中。

**18.1 使用十八般武艺来搜索文件**

1、Windows资源管理器

2、Windows搜索功能

3、命令行配合“dir c: /s juicy.txt“以及“dir c: /s *password* == *cred* == *vnc* ==
*.config*”命令。

**18.2 枚举可能保存敏感数据的应用程序**

1、VNC：ultravnc.ini等

2、Apache：httpd.conf，.htaccess等

3、KeePass以及类似应用程序

**18.3 敏感注册表项**

1、reg query “HKCUSoftwareORLWinVNC3Password”

2、reg query “HKLMSOFTWAREMicrosoftWindows NTCurrentversionWinlogon”

3、reg query “HKLMSYSTEMCurrentControlSetServicesSNMP”

4、reg query “HKCUSoftwareSimonTathamPuTTYSessions”

**18.4 敏感文件**

1、sysprep.inf

2、sysprep.xml

3、%WINDIR%PantherUnattendUnattended.xml

4、%WINDIR%PantherUnattended.xml

5、%WINDIR%debugNetSetup.log

6、%WINDIR%repairsam

7、%WINDIR%repairsystem

8、%WINDIR%repairsoftware

9、%WINDIR%repairsecurity

10、%WINDIR%system32configAppEvent.Evt

11、%WINDIR%system32configSecEvent.Evt

12、%WINDIR%system32configdefault.sav

13、%WINDIR%system32configsecurity.sav

14、%WINDIR%system32configsoftware.sav

15、%WINDIR%system32configsystem.sav

16、%USERPROFILE%ntuser.dat

**18.5 Citrix ICAClient缓存连接**

我们有可能会在本地应用数据仓库中找到已缓存的连接信息。检查“ICAClient”目录，这个目录通常位于%APPDATA%目录。使用“dir /s
ICAClient”命令也可以。

我们可以将其他用户的ICAClient内容复制到自己的目录中，这样有可能可以劫持他们已缓存的连接。

**18.6 组策略首选项中保存的密码**

如果你正在测试的主机属于某个域，并且你可以访问域控上的SYSVOL网络共享目录，那么我们可以寻找存储在各种XML文件中的“cPassword”字段。我们可以手动浏览SYSVOL文件夹，查看以下相关文件：

1、Groups.xml

2、Services.xml

3、ScheduledTasks.xml

4、Printers.xml

5、Drives.xml

6、DataSources.xml

“Password”属性经过AES加密，然而密钥为静态密钥，并且微软官方通过许多MSDN文章介绍了这个静态密钥。

  

**十九、二进制驻留**

二进制程序的驻留涉及到将恶意代码放在某个目录，而这个目录经常会被存在漏洞的应用或服务所使用。通常我们需要结合多种脆弱配置才能完成这一任务。

**19.1 脆弱的Windwos服务权限**

常见的一个攻击点就是存在漏洞的Windows服务以及文件/目录权限。正如前文所述，Sysinternals的accesschk.exe工具可以用来枚举此类信息。

首先，要确认我们位于那个用户组。对于低权限用户来说，他们通常位于标准的“已认证用户”组中。

现在我们需要枚举哪些服务可以被我们修改：

    
    
    accesschk.exe -uwcqv “Authenticated Users” *

如果结果中包含任意服务，我们就可以选择它作为攻击目标。

许多服务会运行在SYSTEM权限下，因此如果我们具备这类服务的写权限，我们就能以最高权限运行任何应用程序。

    
    
    sc config SERVICENAME binpath= “C:malicious.exe” -e
    C:WINDOWSSystem32cmd.exe”
    sc config SERVICENAME obj= “.LocalSystem” password =””
    net stop SERVICENAME
    net start SERVICENAME

**19.2 DLL劫持**

应用程序通常不能自己启动运行，而是以来他们挂载的资源池来完成运行目的。这种情况对诸如DLL之类的代码库来说非常普遍。通常情况下，Windows应用程序会按照预设路径来查找DLL文件，会依次检查如下目录：

1、应用程序加载的目录

2、32位系统目录（C:WindowsSystem32）

3、16位系统目录（C:WindowsSystem）

4、Windows目录（C:Windows）

5、当前工作目录（CWD）

6、PATH环境变量指定的目录（先是系统变量然后是用户变量）

如果我们可以将我们的恶意DLL放在上游路径，那么应用程序就会优先加载我们的恶意代码。

  

**二十、总结**

通过本文分析，我们知道这类环境通常难以进行安全防护，甚至难以正确地进行安全防护。

当用户可以使用全功能的桌面环境时，这种安全防护可能是一项更具挑战的任务。操作系统的设计初衷是提供丰富的功能，尽可能地对用户友好。不幸的是，这两点都与系统安全存在某种冲突。

我们建议任何远程环境都按照务实方式进行配置，尽可能少地向用户提供可用功能，满足用户日常需求即可，这样能尽可能少地减少整体攻击面。

所有的默认配置都应该被调整和加强，以尽可能地减少攻击者可以使用的攻击路径。

当然这些环境应该提供尽可能丰富的日志功能，同时将日志报告给中央监控/报告系统。这样管理员就能实时监控可能发生的任何攻击行为。

  

**二十一、参考资料及延伸阅读**

1、Citrix安全规范：<http://www.citrix.com/support/security-compliance.html>

2、SANS白皮书：Citrix以及远程服务环境中的服务器安全：<http://www.citrix.com/content/dam/citrix/en_us/documents/support/citrix-xenapp-6-5-and-xendesktop-5-6-security-standards-and-deployment-scenarios.pdf>

3、Tariq Azad撰写的《如何对企业中的Citrix
XenApp服务器进行安全加固》：<http://www.goodreads.com/author/show/3072999.Tariq_Azad>

4、windows-privesc-check：<http://pentestmonkey.net/tools/windows-privesc-check>

5、使用mspaint创建cmd.exe：<http://nsimattstiles.wordpress.com/2013/03/19/gain-command-prompt-access-via-mspaint/>

本文翻译自pentestpartners.com [原文链接](https://www.pentestpartners.com/security-blog/breaking-out-of-citrix-and-other-restricted-desktop-environments/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86225](/post/id/86225)

安全客 - 有思想的安全新媒体

本文转载自: [pentestpartners.com](https://www.pentestpartners.com/security-blog/breaking-out-of-citrix-and-other-restricted-desktop-environments/)

如若转载,请注明出处： <https://www.pentestpartners.com/security-blog/breaking-out-of-citrix-and-other-restricted-desktop-environments/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

