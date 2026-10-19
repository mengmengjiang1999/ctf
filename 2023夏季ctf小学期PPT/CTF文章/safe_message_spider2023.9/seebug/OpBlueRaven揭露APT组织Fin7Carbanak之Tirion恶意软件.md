**译者：知道创宇404实验室翻译组**  
**原文链接：<https://threatintel.blog/OPBlueRaven-Part1/>**

本文旨在为读者提供有关PRODAFT＆INVICTUS威胁情报（PTI）团队针对不同威胁者的最新详细信息，以及发现与臭名昭著的Fin7
APT组织合作的人是谁。

所有这些都源自威胁者方面的一次OPSEC故障，我们将尝试逐步扩展主题，类似于我们在不断发现的基础上扩大范围。

## 关于Fin7和Carbanak的前所未有的事实：第1部分

在5月至2020年7月之间；PRODAFT威胁情报团队的四名成员进行了BlueRaven行动。案例研究源于发现一组看似不重要的轻微OpSec故障。当然，后来发现这些威胁因素与臭名昭著的Fin7
/ Carbanak威胁因素有联系。

PTI的OP源于攻击者一方的OPSEC故障。与以前发现和发布的数据不同，使此OP如此与众不同的是，我们设法发现了大量有关攻击者工具集的未发布信息，这些信息揭示了攻击者的TTP。

Carbanak Group /
Fin7于2014年首次被发现，是世界上最有效的APT组织之一，并且是最早知道的APT组织之一。该组织被认为在全球范围内造成超过9亿美元的损失。我们的OP结果发现了有关这些威胁者的以下关键发现：

  * 获得了Fin7中某些攻击者的真实身份。
  * 有关Fin7的工具和攻击方法的详细证据已经出现。
  * Fin7和REvil勒索软件组（将在后面的阶段中详细介绍）之间的关系已经出现。

撰写此报告旨在提高认识并协助网络安全专家进行分析。当然，PRODAFT的一些发现已被删除。因此，授权机构可以与PRODAFT或INVICTUS联系以进行进一步的披露。

每篇文章都将讨论操作的特定方面，包括但不限于攻击方法，组织和攻击者的身份。我们的团队设法窃听了攻击者之间的各种刺耳对话。这些对话中的大多数也将在整个系列中发布。

## Carbanak后门

Carbanak Backdoor是我们小组获得的第一批发现之一。
当前版本的CARBANAK后门程序（团队中最知名的工具，即Carbanak组的名字）是引起我们团队关注的第一个工具。根据PE文件标题在2019年11月编译的“
3.7.5”版本是后门命令和控制服务器的最新检测到版本。下面的屏幕快照提供了“ 3.7.5”版Carbanak后门管理面板的屏幕截图。

![img](https://images.seebug.org/content/images/2020/09/15/1600159346000-cmdmanager.png-w331s)

我们将获得的最新版本与2017年Virustotal中的“命令管理器”版本进行了比较，并对此工具进行了评估。在下图中，可以看到由于上述两个版本的反编译而获得的源代码之间的差异。下图仅列出了两个版本之间的源代码，左列属于2017年上载到Virustotal的文件，右列属于我们团队获得的“
3.7.5”版本。蓝线表示不同的文件，而绿线表示新文件。通过对命令和控制服务器软件的检查，可以发现，通过GUI界面对插件进行了基本更改，以创建更详细的错误日志，并添加了新的语言编码。

![img](https://images.seebug.org/content/images/2020/09/15/1600159346000-cmdmanagercompare.jpg-w331s)

确定了2019年编译的6个版本的恶意软件“命令管理器”工具。下图给出了检测到的版本的时间。

版 | 编译时间  
---|---  
3.7.5 | 2019年11月7日星期四16:50:51  
3.7.3 | 2019年9月16日星期一18:06:32  
3.7.2 | 2019年7月24日星期三20:52:26  
3.7.1 | 2019年7月5日星期五21:16:24  
3.6.3 | 2019年5月16日星期四11:13:05  
3.6 | 2019年4月19日星期五10:17:22  
  
在旧版本的Bot.dll中，它是在受害设备上运行的恶意软件的组件，在反汇编中检测到981个功能，而在同一软件的新版本中检测到706个功能。使用Diaphora二进制比较工具，有607个函数获得最佳匹配分数，而有43个函数获得部分匹配。另外，与Virustotal中的旧版本相比，新的bot文件的文件大小小于50kb。当检查新的bot文件时，可以看到，旧版本中除基本功能以外的功能都是作为插件实现的。这些新插件可以执行诸如按键记录，过程监视之类的操作，并且可以通过反射加载方法无文件执行。结果，恶意软件的文件大小减小了，从而为基于签名的安全软件解决方案留下了更少的痕迹。

  * 高清插头
  * hd64.plug
  * hvnc.plug
  * hvnc64.plug
  * keylog.dll
  * keylog64.dll
  * procmon.dll
  * procmon64.dll
  * rdpwrap.dll
  * switcher.dll
  * switcher64.dll
  * vnc.plug
  * vnc64.plug

在本节中，将检查先前发现的文件中“not”的一些插件。由于这些是臭名昭著的工具包中前所未有的功能，因此，我们认为以下各节对于进一步分析该小组的TTP至关重要。

### 键盘记录插件

“keylog.dll”插件使用RegisterRawInputDevices
API捕获用户击键。为了确定在哪个上下文中使用了击键，前台进程的“可执行文件路径”，“ Windows文本”和时间戳信息将与击键一起记录下来。

![img](https://images.seebug.org/content/images/2020/09/15/1600159346000-keylog.jpg-w331s)

键盘记录插件使用Windows GDI + API将收集的数据转换为Bitmap，并将其写入用户％TEMP％目录中名为“
SA45E91.tmp”的文件夹中。下图显示了恶意软件用来存储数据的功能。

![img](https://images.seebug.org/content/images/2020/09/15/1600159346000-keylog-log.jpg-w331s)

下图给出了所获得日志示例的屏幕截图。

![img](https://images.seebug.org/content/images/2020/09/15/1600159346000-samplekeylog.jpg-w331s)

### 过程监控器插件

该插件可以跟踪在目标系统中运行的进程，并用于获取有关所需进程的开始和终止时间的信息。在下图中，给出了收集有关正在运行的进程的信息的功能的屏幕快照。

![img](https://images.seebug.org/content/images/2020/09/15/1600159347000-procmon.jpg-w331s)

## Tirion装载机（ Carbanak后门的未来）

Fin7小组的新加载程序工具是名为Tirion的恶意软件，该软件被认为是替代Carbanak后门程序而开发的。它包含许多功能，用于信息收集，代码执行，侦察和横向移动。与上一节中检查过的最新版本的Carbanak后门程序一样，该恶意软件执行的许多功能已作为独立的插件开发。使用反射性加载方法将它们加载到目标系统中并以无文件方式执行。公开数据显示，Carbanak后门的开发目前已停止，并且同一团队正在Tirion
Loader上进行开发和测试。攻击者之间的通信日志表明，此新工具旨在替代Carbanak后门。

![img](https://images.seebug.org/content/images/2020/09/15/1600159347000-tirion.png-w331s)

Tirion恶意软件的功能如下：

  * 信息收集
  * 截屏
  * 列出运行进程
  * 命令/代码执行
  * 流程迁移
  * Mimikatz执行
  * 密码抢夺
  * Active Directory和网络侦听

检测到的最新Tirion
Loader版本属于“2020年6月28日23:24:03”编译的版本“1.6.4”。下图显示了攻击者可以在机器人设备上执行的操作。“
1.0”版本是最早检测到的版本，被认为是使用的第一个版本，已于“2020年3月5日20:29:53”进行了编译。

![我是一个](https://images.seebug.org/content/images/2020/09/15/1600159347000-tirion1.png-w331s)

攻击者编写的“readme.txt”文件中的以下文本清楚地说明了恶意软件的基本组件。

> Описание системы удаленного доступа Tirion Система состоит из 3-х
> компонентов:
>
>   1. Сервер
>   2. Клиент
>   3. Лоадер Эти компоненты связаны следующим образом: Лоадер переодически
> коннектится к серверу, клиент подключается к серверу с постоянным коннектом.
> Лоадер выполняет команды от сервера и передает ему ответы. Через клиента
> пользователь отдает команды лоадеру через сервер. Полученны ответы от
> лоадера, сервер передает клиенту.
>

相关文本的英文翻译如下。

    
    
    The system consists of 3 components:
    
    Server
    
    Client
    
    Loader
    
    These components are related as follows:
    The loader periodically connects to the server, the client connects to the server with a permanent connection. The loader executes commands from server and sends it responses. Through the client, the user issues commands to the loader through the server. Received responses from the loader,the server transmits to the cl

恶意软件的文件组织如下：

### 档案结构

    
    
    |-- client
    |   |-- client.exe
    |   |-- client.ini.xml
    |   |-- jumper
    |   |   |-- 32
    |   |   `-- 64
    |   |       `-- l64_r11.ps1
    |   |-- keys
    |   |   `-- client.key
    |   |-- libwebp_x64.dll
    |   |-- libwebp_x86.dll
    |   `-- plugins
    |       `-- extra
    |           |-- ADRecon.ps1
    |           |-- GetHash32.dll
    |           |-- GetHash64.dll
    |           |-- GetPass32.dll
    |           |-- GetPass64.dll
    |           |-- PswInfoGrabber32.dll
    |           |-- PswInfoGrabber64.dll
    |           |-- PswRdInfo64.dll
    |           |-- powerkatz_full32.dll
    |           |-- powerkatz_full64.dll
    |           |-- powerkatz_short32.dll
    |           `-- powerkatz_short64.dll
    |-- loader
    |   |-- builder.exe
    |   |-- loader32.dll
    |   |-- loader32.exe
    |   |-- loader32_NotReflect.dll
    |   |-- loader64.dll
    |   |-- loader64.exe
    |   `-- loader64_NotReflect.dll
    |-- readme.txt
    `-- server
        |-- AV.lst
        |-- System.Data.SQLite.dll
        |-- ThirdScripts
        |-- client
        |   `-- client.key
        |-- data.db
        |-- loader
        |   `-- keys
        |       |-- btest.key
        |       `-- test.key
        |-- logs
        |   |-- error
        |   `-- info
        |-- plugins
        |   |-- CommandLine32.dll
        |   |-- CommandLine64.dll
        |   |-- Executer32.dll
        |   |-- Executer64.dll
        |   |-- Grabber32.dll
        |   |-- Grabber64.dll
        |   |-- Info32.dll
        |   |-- Info64.dll
        |   |-- Jumper32.dll
        |   |-- Jumper64.dll
        |   |-- ListProcess32.dll
        |   |-- ListProcess64.dll
        |   |-- NetSession32.dll
        |   |-- NetSession64.dll
        |   |-- Screenshot32.dll
        |   |-- Screenshot64.dll
        |   |-- extra
        |   |-- mimikatz32.dll
        |   `-- mimikatz64.dll
        |-- server.exe
        |-- server.ini.xml
        |-- x64
        |   `-- SQLite.Interop.dll
        |-- x86
            `-- SQLite.Interop.dll

### Readme.txt

“readme.txt”文件中内容如下：

    
    
    client 1.6.3
    [+] The result of ADRecon work is saved in the database in the loader from which it was launched, when the tab is called again, the data loaded automatically
    [+] Added a form for launching the script ps2x.py (PsExec).
    server 1.5
    [+] Added support for executing scripts from the ThirdScripts folder
    
    client 1.5
    [+] Added plugin NetSession. The plugin collects information about the computers connected to the computer where the loader is running.
    
    client 1.4
    [+] added plugin info. In the context menu, select Info and after a while in the Info field there will be the user name, domain and version of Windows
    
    client 1.3.3
    [+] The “Get passwords” button has been added to the mimikatz plugin
    
    client 1.3.2
    [+] Added support for RDP grabber.
    client 1.3
    [+] added plugin mimikatz.
    [+] added grabber plugin.
    
    server 1.2:
    [*] updated data transfer protocol
    [+] added AV definition, for this there must be an AV.lst file in the server folder
    
    loader:
    [*] updated data transfer protocol
    [+] sending local
    
    server 1.1:
    [+] - added support for the jumper plugin
    
    client 1.1
    [+] - added support for the jumper plugin

### 装载机组件

将在受害系统上运行的恶意软件的此组件大小约为9kb，并从服务器运行命令。当攻击者想要在受害者的设备上运行某个功能时，包含该功能的相关插件文件会以反射方式加载到受害者的设备上，并以无文件方式执行。

服务器和加载器之间的网络流量使用在构建阶段确定的密钥进行加密。下图包含相关的加密算法。

![img](https://images.seebug.org/content/images/2020/09/15/1600159347000-enc.jpg-w331s)

### PswInfoGrabber

它是一个DLL文件，负责从目标系统中窃取和报告敏感信息，尤其是浏览器和邮件密码。确定攻击者也独立于Tirion
Loader使用了此工具。在下图中，包含了由恶意软件收集的日志的屏幕截图。

![img](https://images.seebug.org/content/images/2020/09/15/1600159347000-chrome.jpg-w331s)

## opBlueRaven | 第一部分的结尾

在这些系列的第一版中，我们希望通过将PTI发现的最新Carbanak工具包与可公开访问的较旧版本进行比较，以介绍我们的运营情况。

在下一篇文章中，我们还将通过提供攻击者之间实际对话的参考来更深入地研究攻击者的TTP。 此外，我们还将提供直接从威胁行为者的计算机获取的屏幕截图。

![img](https://images.seebug.org/content/images/2020/09/15/1600159347000-redacted.png-w331s)

## 附录：YARA签名

    
    
    import "pe"
    rule apt_Fin7_Tirion_plugins
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Tirion Loader's plugins. It is used by Fin7 group. Need manual verification"
            version = "1.0"
            date = "2020-07-22"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "fdc0ec0cc895f5b0440d942c0ab60eedeb6e6dca64a93cecb6f1685c0a7b99ae"
    
        strings:
            $a1 = "ReflectiveLoader" ascii
            $a2 = "plg.dll" fullword ascii
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 15000 and (pe.exports("?ReflectiveLoader@@YA_KPEAX@Z") or
                pe.exports("?ReflectiveLoader@@YGKPAX@Z"))
    }
    
    rule apt_Fin7_Tirion_PswInfoGrabber
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Tirion Loader's PswInfoGrabber plugin. It is used by Fin7 group."
            version = "1.0"
            date = "2020-07-22"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "e7d89d1f23c2c31e2cd188042436ce6d83dac571a5f30e76cbbcdfaf51e30ad9"
    
        strings:
            $a1 = "IE/Edge Grabber Begin" fullword ascii
            $a2 = "Mail Grabber Begin" fullword ascii
            $a3 = "PswInfoGrabber" ascii
            $a4 = "Chrome Login Profile: '"
            $a5 = "[LOGIN]:[HOST]:"
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 150KB
    }
    
    rule apt_Fin7_Tirion_loader
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Tirion Loader's loader component. It is used by Fin7 group."
            version = "1.0"
            date = "2020-07-22"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "e7d89d1f23c2c31e2cd188042436ce6d83dac571a5f30e76cbbcdfaf51e30ad9"
    
        strings:
            $a1 = "HOST_PORTS" fullword ascii
            $a2 = "KEY_PASSWORD" fullword ascii
            $a3 = "HOSTS_CONNECT" ascii
            $a4 = "SystemFunction036"
            $a5 = "ReflectiveLoader"
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 15KB
    }
    
    rule apt_Fin7_Carbanak_keylogplugin  
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Carbanak backdoor's keylogger plugin. It is used by Fin7 group"
            version = "1.0"
            date = "2020-07-21"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "db486e0cb94cf2bbe38173b7ce0eb02731ad9a435a04899a03d57b06cecddc4d"
    
        strings:
            $a1 = "SA45E91.tmp" fullword ascii
            $a2 = "%02d.%02d.%04d %02d:%02d" fullword ascii
            $a3 = "Event time:" fullword ascii
            $a4 = "MY_CLASS" fullword ascii
            $a5 = "RegisterRawInputDevices" fullword ascii 
    
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 15000
    }
    
    rule apt_Fin7_Carbanak_procmonplugin  
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Carbanak backdoor's process monitoring plugin. It is used by Fin7 group"
            version = "1.0"
            date = "2020-07-21"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "3bf8610241a808e85e6ebaac2bb92ba4ae92c3ec1a6e56e21937efec71ea5425"
    
        strings:
            $a1 = "[%02d.%02d.%04d %02d:%02d:%02d]" fullword ascii
            $a2 = "%s open %s" fullword ascii
            $a3 = "added monitoring %s" fullword ascii
            $a4 = "pm.dll" fullword ascii
            $a5 = "CreateToolhelp32Snapshot" fullword ascii  
    
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 10000
    }
    
    rule apt_Fin7_Carbanak_hdplugin  
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Carbanak backdoor's hidden desktop plugin. It is used by Fin7 group"
            version = "1.0"
            date = "2020-07-21"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "39b545c7cd26258a9e45923053a5a64c9461470c3d7bfce3be1c776b287e8a95"
    
        strings:
            $a1 = "hd%s%s" fullword ascii
            $a2 = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" fullword ascii
            $a3 = "StartHDServer" fullword ascii
            $a4 = "SetThreadDesktop" fullword ascii
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 15000
    }
    rule apt_Fin7_Carbanak_hvncplugin  
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Carbanak backdoor's hvnc plugin. It is used by Fin7 group"
            version = "1.0"
            date = "2020-07-21"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "40ce820df679b59476f5d277350dca43e3b3f8cac7ec47ad638371aaa646c315"
    
        strings:
            $a1 = "VncStartServer" fullword ascii
            $a2 = "VncStopServer" fullword ascii
            $a3 = "RFB 003.008" fullword ascii
            $a4 = "-nomerge -noframemerging" fullword ascii
            $a5 = "--no-sandbox --allow-no-sandbox-job --disable-3d-apis --disable-gpu --disable-d3d11" fullword wide
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 300000
    }
    
    rule apt_Fin7_Carbanak_vncplugin  
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Carbanak backdoor's vnc plugin. It is used by Fin7 group"
            version = "1.0"
            date = "2020-07-21"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "ecf3679f659c5a1393b4a8b7d7cca615c33c21ab525952f8417c2a828697116a"
    
        strings:
            $a1 = "VncStartServer" fullword ascii
            $a2 = "VncStopServer" fullword ascii
            $a3 = "ReflectiveLoader" fullword ascii
            $a4 = "IDR_VNC_DLL" fullword ascii
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 400000
    }
    
    rule apt_Fin7_Carbanak_rdpplugin  
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Carbanak backdoor's rdp plugin. It is used by Fin7 group"
            version = "1.0"
            date = "2020-07-21"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "0d3f1696aae8472145400d6858b1c44ba7532362be5850dae2edbd4a40f36aa5"
    
        strings:
            $a1 = "sdbinst.exe" fullword ascii
            $a2 = "-q -n \"UAC\"" fullword ascii
            $a3 = "-q -u \"%s\"" fullword ascii
            $a4 = "test.txt" fullword ascii
            $a5 = "install" fullword ascii
            $a6 = "uninstall" fullword ascii
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 400000
    }
    
    rule apt_Fin7_Carbanak_switcherplugin  
    {
    
        meta:
            author = "Yusuf A. POLAT"
            description = "Carbanak backdoor's switcher plugin. It is used by Fin7 group"
            version = "1.0"
            date = "2020-07-21"    
            reference = "https://threatintelligence.blog/"
            copyright = "PRODAFT"
            SHA256 = "d470da028679ca8038b062f9f629d89a994c79d1afc4862104611bb36326d0c8"
    
        strings:
            $a1 = "iiGI1E05.tmp" fullword ascii
            $a2 = "oCh4246.tmp" fullword ascii
            $a3 = "inf_start" fullword ascii
            $a4 = "Shell_TrayWnd" fullword ascii
            $a5 = "ReadDirectoryChangesW" fullword ascii
            $a6 = "CreateToolhelp32Snapshot" fullword ascii
        condition:
            uint16(0) == 0x5A4D  and (all of ($a*)) and filesize < 15000
    }

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1335/>

