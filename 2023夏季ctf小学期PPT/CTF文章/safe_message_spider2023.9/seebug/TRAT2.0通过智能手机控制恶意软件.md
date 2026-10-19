**译者：知道创宇404实验室翻译组**  
**原文链接：<https://www.gdatasoftware.com/blog/trat-control-via-smartphone>**

### 前言

恶意软件攻击者希望通过便利功能吸引客户。现在，攻击者只需使用智能手机和Telegram应用程序，就可以远程控制恶意软件。

### 俄罗斯论坛上的广告

研究人员@3xp0rtblog发现了T-rat2.0，并在Twitter上发布了它，其中包括示例哈希值和销售线程。一个奢侈的广告如下所示。

下图显示了lolz.guru（由3xp0rtblog发现并报告）上张贴广告的部分内容。它赞扬了使用T-RAT时的舒适性和便利性，因为它可以通过带有Telegram应用程序的智能手机进行控制。

![](https://images.seebug.org/content/images/2020/10/61b3aedd-01de-462f-97a1-389a003bd0f4.png-w331s)
翻译：更新的，成熟的RAT。放在口袋里就可以访问和使用所有功能。只需Internet和T-RAT就可以从任何设备进行控制，使其正常工作。

![](https://images.seebug.org/content/images/2020/10/b87afbd5-386d-411b-a5ac-98476a829497.png-w331s)
翻译：优点：舒适，方便，控制简单，功能丰富，匿名性和可靠性……

### 感染链和持久性

第一个已知阶段是下载器[4]，它从hxxps://hgfhhdsf.000webhostapp.com/1DJjnw(dot)jpg获取加密的文件[6]，并将其保存到%TEMP%/gfdggfd.jpg。

为了解密有效负载，下载程序将密钥0x01应用于XOR。生成的文件是一个ZIP存档，它将保存到%TEMP%/hrtghgesd.zip中。下载程序将删除%TEMP%/gfdggfd.jpg并提取ZIP存档。注意：这两个硬编码名称均由QWERTY键盘上的按键彼此相邻的字符组成，因此攻击者可能只是在键盘上滚动来创建它们。

提取的恶意软件的位置确定如下：

（1）下载器检查当前用户是否具有管理员权限。如果有，则路径的第一部分是以下内容之一（随机选择）。

  * %APPDATA%\Microsoft\Windows\
  * %USERPROFILE%\Windows\System32\
  * %LOCALAPPDATA%\Microsoft\Windows\​

如果他们没有管理员权限，则路径的第一部分为以下内容之一：

  * %SYSTEM%\Microsoft\Protect\
  * %COMMONAPPDATA%\Microsoft\Windows\​​​​​​​​​
  * %USERPROFILE%\AppData\LocalLow\Microsoft\Windows\​​​​​​​​​​​​
  * C:\Windows\assembly\GAC\​

（2）对于恶意软件路径的第二部分，下载程序生成一个介于347和568203之间的随机数，将其转换为字符串，然后使用MD5，SHA1或SHA256生成哈希。它使用哈希的十六进制表示形式作为恶意软件路径的第二部分。

该档案包含实际的T-RAT可执行文件sihost.exe，以及几个DLL文件。一些值得注意的库是Telegram.Bot.dll和socks5.dll。

名为service的子文件夹包含另外六个文件（哈希在IoC列表中）：
![](https://images.seebug.org/content/images/2020/10/f507eae9-105f-44ee-a5c8-c4e5404cbaf1.png-w331s)

该下载程序通过安排日常任务来保留sihost.exe。任务的名称是系统的处理器ID。如果当前用户具有管理员权限，则会将运行级别设置为HIGHEST。之后，下载程序将在批处理文件的帮助下删除自己。​​

![](https://images.seebug.org/content/images/2020/10/7f64fe0a-05de-43e4-81c3-e4a4314c38c6.png-w331s)
ZIP存档的内容[3]

![](https://images.seebug.org/content/images/2020/10/a789f65c-c167-43fc-bb14-84c672865e58.png-w331s) ZIP归档文件中服务文件夹的内容[3]

### 封隔器和混淆器

原始的T-RAT示例[1]和下载程序[4]是.NET程序集，他们以相同的方式打包。打包的部分作为base64字符串嵌入在文件的叠加层中。字符串的开头和结尾由序列“ghjghjbnv”标记。打包程序存根会搜索序列以找到打包的图像，解码base64字符串并动态加载生成的.NET程序集。

![](https://images.seebug.org/content/images/2020/10/0b7b2ed6-051d-49f7-9a41-af1423e985e1.png-w331s)
十六进制编辑器中带有标记序列的base64字符串

![](https://images.seebug.org/content/images/2020/10/dcf5be95-bc36-40e7-96e2-12d948d3dd16.png-w331s)
PortexAnalyzer可视化效果使base64字符串在字节图中显示为蓝色区域

解压缩的.NET程序集被ConfuserEx的变体所模糊。某些俄语字符串是可见的，但大多数引用的字符串都是base64编码的。

用NoFuserEx对程序集进行模糊处理后，将保留base64编码的字符串。我编写了一个小的Python脚本来完成其余的工作（请参阅附录A）。它用NOP替换了对FromBase64String的调用的IL代码，并将base64字符串替换为其已解码的对应字符串。由于解码的字符串较短，因此其余部分将填充为U
+ 200B，这是零宽度空间Unicode字符。（注意：这是一个相当懒惰的解决方案，它不会创建完美运行的可执行文件，但足以进行持续的静态分析。）

此程序集的混淆处理中最耗时的部分无法自动化。方法和类的符号名称已由混淆器消除。因此，在分析T-RAT的代码时，我在此过程中添加了自己的名称。该代码库具有98个不同的命令来控制T-RAT客户端。

![](https://images.seebug.org/content/images/2020/10/123c183c-f451-451f-9a42-5987e4de03bf.png-w331s)
手动混淆前后的T-RAT样本

### 功能概述

攻击者使用基于文本的命令和RAT提供的命令按钮，通过电报控制T-RAT。命令使用英语，帮助消息大多为俄语。广告横幅的一部分展示了这些控件以及它们在手机上的外观（请参见下图）。

![](https://images.seebug.org/content/images/2020/10/eb67d520-d69c-432a-b134-f9579ec3c248.png-w331s)
第一段翻译：您将获得什么？成熟RAT。我们的产品具有有趣且最重要的必需功能：RAT、窃取程序、键盘记录程序VNC、HRDP、Clipper、隐藏代理服务器等等。我们邀请您更详细地了解我们的功能。

U-RAT有98条命令。我没有在主要文章中描述每个命令，而是将它们分为几组，下面将对其进行说明。完整的命令清单在附录B中。

  1. Menu navigation  
这些用于进入或退出某些模块（如文件管理器）。它们有助于通过智能手机进行更方便的控制。

  2. File manager  
T-RAT可以在文件系统上导航，显示有关驱动器和可用空间，文件夹内容以及修改文件和文件夹的信息。它还可以将文件发送给攻击者。有趣的是，它混入了Unix命令名称。例如，文件列表是通过ls完成的。

  3. Stealer  
该模块允许从浏览器获取密码，Cookie，自动填充数据，Telegram、Discord、Steam、Nord、Viber、Skype和Filezilla的会话或配置数据。在发送到Telegram之前，大多数数据文件除了将T-RAT可执行文件保存在文本文件中外，还保存在%TEMP%/winsys/中的ZIP存档中。

  4. Clipper  
Clipper检查剪贴板上的硬币地址并替换它们，因此，任何数字货币都会被发送到攻击者的钱包中。它支持Qiwi、WMR、WMZ、WME、WMX、Yandex
money、Payer、CC、BTC、BTCG、Ripple、Doge和Tron。攻击者使用clipper命令保存指定加密货币的地址，并启动或停止clipper的执行。

  5. Monitoring and spying  
攻击者可以运行键盘记录器，创建屏幕截图，通过麦克风录制音频，通过网络摄像头拍照，发送剪贴板内容。

  6. Evasion  
T-RAT有多种绕过UAC的方法，包括Fodhelper，Cmstp，Cleanup和Computerdefaults。它可以禁用Windows
Defender和智能屏幕通知。它可以禁用各种安全设置，例如，可以更改关联策略以将“.exe”设置为低风险文件扩展名，并可以关闭ZoneIdentifiers。它可以检查沙箱和虚拟机。

  7. Disruption  
这些命令杀死进程、通过主机文件阻止网站、通过图像文件执行选项设置调试器来阻止和重定向程序（因为阻止调试器是不存在的）、禁用任务栏和任务管理器。

  8. Remote control  
T-RAT通过电报提供Powershell或CMD终端。也可以通过HRDP或VNC进行远程控制。

T-RAT运行名为service \
in.exe的HRDP客户端，该客户端位于可执行文件的位置。然后，它将创建一个具有随机密码和名称的新用户帐户，并将凭据发送给攻击者。它将新创建的用户添加到“远程桌面用户”组，并通过将fDenyTSConnections设置为“0”来启用远程访问。

VNC服务器在32位系统上为service\winserv1.exe，在64位系统上为service\winserv2.exe。

### IoC

**Hashes**

![](https://images.seebug.org/content/images/2020/10/f95e4339-6617-4885-8c17-12329dd82faa.png-w331s)

**IoCs for downloader[4]**

![](https://images.seebug.org/content/images/2020/10/935fe898-f84b-45f4-8d99-431c1e50a212.png-w331s)

**IoCs for T-RAT[1]**

![](https://images.seebug.org/content/images/2020/10/407a8d7e-d3ef-4a25-a432-209a3c5b1df5.png-w331s)

**附录A：去模糊脚本**

    
    
    #!/usr/bin/env python2.7
    import re
    import base64
    import sys
    import os
    import argparse
    from shutil import copyfile
    
    def isBase64(s):
        try:
            return base64.b64encode(base64.b64decode(s)) == s
        except Exception:
            return False
    
    
    def searchAndReplace(search, replace, binfile):
        content = ""
    
        with open(binfile,"rb") as bif:
            content = bif.read()
            new_content = content.replace(search, replace)
            if new_content == content:
                print "Search string not found."
                return
    
        with open(binfile,"wb+") as wif:
            wif.write(new_content)
    
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='Decode and replace base64 strings in binary. Karsten Hahn @ G DATA CyberDefense')
        parser.add_argument('str_listing', help='Text file with strings listing of sample. E.g. use Sysinternals strings.exe')
        parser.add_argument('sample', help='Sample file where base64 strings should be replaced')
    
        args = parser.parse_args()
        inputfile = args.sample
        outputfile = args.sample + ".decoded"
    
        copyfile(inputfile, outputfile)
    
        base64Regex = re.compile(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$')
    
        str_listing = args.str_listing
    
        with open(str_listing) as ref_file:
            print 'Extracting base64 strings...'
            base_strings = []
            for line in ref_file:
                base_strings += base64Regex.findall(line)
            print "Replacing base64 strings..."
            for base_str in sorted(base_strings, key=len, reverse=True):
                if len(base_str) > 3 and isBase64(base_str):
                    decoded_string = base64.b64decode(base_str)
                    decoded_bytes = bytearray(str(decoded_string).decode('utf-8').encode("utf-16le"))
                    base_bytes = bytearray(str(base_str).decode('utf-8').encode("utf-16le"))
                    while len(decoded_bytes) < len(base_bytes):
                        decoded_bytes.extend(b'\x0B\x20')
                    #print decoded_bytes
                    searchAndReplace(base_bytes, decoded_bytes, outputfile)
            print "Replacing calls to decode Base64..."
    
            # Optional: remove calls to Base64 conversion, this is specific to the sample
            # for T-RAT
            # searchAndReplace(b'\x28\x27\x00\x00\x0A', b'\x00\x00\x00\x00\x00', outputfile)
            # for T-RAT downloader
            # searchAndReplace(b'\x28\x17\x00\x00\x0A', b'\x00\x00\x00\x00\x00', outputfile)
    
        print 'All done'
        print 'Deobfuscated file written to', outputfile

**附录B：T-RAT命令**

这些是T-RAT 2.0命令以及其中一些命令的说明。

Command | Description  
---|---  
/help | Print available commands (shows different commands depending on the
state of the menu)  
/getscreen | Takes a screenshot and sends as photo to Telegram  
/webcam | Takes a picture using the webcam and sends as photo to Telegram  
/record | Records audio using the microphone. Saves it to record.wav in the
executable's folder.  
/sysinfo | Shows: username, IP, MAC, computername, processor model, number of
cores, processor size, graphics card model, RAM, operating system,
architecture, system directory, antivirus, firewall, drive info and available
space  
/isadmin | Checks if executable has admin rights  
/activewindow |  
/openwindows |  
/programs | Shows list of installed programs by obtaining all DisplayName
values for all subkeys of SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall  
/processlist |  
/killprocess [process] |  
/run [path] | Creates a hidden folder in %TEMP% named winsys. Puts a VBScript
file named .vbs in this folder. The VBScript uses ShellExecute to run the file
given in [path] parameter.  
It uses a template called "Run2" in the resources for the VBScript and
replaces "lmao" with [path] |  
/clipboard | Posts clipboard content to Telegram  
/location |  
/path |  
/blocksite [example google.com] | Blocks a site via hosts file redirection to
localhost  
/redirectprogram [first] [second] | Sets the second parameter as debugger for
the first via Image File Execution Options (IFEO)  
/blockprogram [name] [block | unblock]  
unblock: Removes the IFEO debugger from registry |  
/CmstpUACBypass | UAC bypass via cmstp.exe  
/CleanupUACBypass | UAC bypass via SilentCleanup  
/FodHelperUACBypass | UAC bypass via fodhelper.exe  
/ComputerDefUACBypass | UAC bypass via computerdefaults.exe  
/OffCertChecking | In Attachment Policies sets: HideZoneInfoOnProperties to
"1" and SaveZoneInformation to "2" (= Off)  
In Associations Policies sets: DefaultFileTypeRisk to "6152" (= Low) and
LowRiskFileTypes to ".exe" (yes, only ".exe") |  
/DisableWindowsDefender | Disables TamperProtection; enables
DisableAntiSpyware, DisableBehaviorMonitoring, DisableOnAccessProtection and
DisableScanOnRealtimeEnable  
/OffAvNotification | Disables SmartScreen and sets registry values to "0" for:
EnableLUA, ConsentPromptBehaviorAdmin, PromptOnSecureDesktop  
/cmd | Provides a remote cmd terminal  
/powershell | Provides a remote powershell console  
/settings |  
/disconnect |  
/opencd | Calls mciSendStringA with "set cdaudio door open"  
/closecd | Calls mciSendStringA with "set cdaudio door closed"  
/exploreroff | Sets DisableTaskMgr to "1"  
/exploreron | Deletes subkey tree for
Software\Microsoft\Windows\CurrentVersion\Policies\System  
/hidetaskbar | Calls user32.dll ShowWindow with SW_HIDE parameter  
/showtaskbar | Calls user32.dll ShowWindow for Shell_TrayWnd  
/wallpaper | Asks the user to send a picture to set as wallpaper  
/collapsewindows |  
/reboot |  
/kill |  
/suicide |  
cd [directory] | Sets working directory  
back | Goes one step back in the command listing  
ls |  
drives |  
action [name] | Provides file operations: info, run, delete, read, send, cd  
mkdir [NameFileInFolder] | Creates a directory  
remove [NameFileInFolder],[AnotherDirectory] |  
rename [NameFileInFolder],[NewName] |  
/hrdp | 1) Runs service\in.exe from executable folder. 2) Sets
fDenyTSConnections to "0" 3) Creates new user account named usr with password
4) Adds new user to Remote Desktop Users group 5) Prints credentials for new
user to Telegram  
/StartProxyServer | Starts a Socks5 proxy using port 5901  
/StopProxyServer | Stops above proxy  
/StartVNC | Runs service\winserv1.exe for 32 bit architecture, or
service\winserv2.exe for 64 bit architecture. Both reside in the executable
folder.  
/StopVNC | Kills any process with a name containing the substring winserv1 (32
bit)or winserv2 (64 bit)  
/CheckVNC | Returns if a process name containing winserv1 or winserv2 exists  
/commands | Menu navigation  
/control | Menu navigation  
/stealer | Menu navigation  
/filemanager | Menu navigation  
/StealPasswords |  
/StealWebData | Searches for Web Data folder in the %LOCALAPPDATA% directory
and extracts autofill information. This folder is part of Chrome.  
/StealCookies | Saves cookies to Cookies.txt in the executable folder and
uploads it to Telegram  
/GetTelegramSession | Steal Telegram data  
/GetSteamFiles | Steal Steam data  
/GetNordData | Steal Nord data  
/GetFilezillaConfig | Steal Filezilla configuration  
/GetSkypeSession | Saves skype appdata folder contents to
%TEMP%/winsys/Skype.zip and uploads this file to Telegram  
/GetDiscordSession | Saves Discord\Local Storage\leveldb folder contents to
%TEMP%/winsys/Discord.zip and uploads this to Telegram  
/GetViberSession | Steal Viber data  
/SetQiwi [wallet] | Set Qiwi wallet for clipper  
/SetWMR [wallet] | Set WMR wallet for clipper  
/SetWMZ [wallet] | Set WMZ wallet for clipper  
/SetWME [wallet] | Set WME wallet for clipper  
/SetWMX [wallet] | Set WMX wallet for clipper  
/SetYandexMoney [wallet] | Set Yandex Money wallet for clipper  
/SetCC [wallet] | Set CC wallet for clipper  
/SetPayeer [wallet] | Set Payeer wallet for clipper  
/SetRipple [wallet] | Set Ripple wallet for clipper  
/SetDogechain [wallet] | Set Doge wallet for clipper  
/SetTron [wallet] | Set Tron wallet for clipper  
/SetBTCG [wallet] | Set BTCG wallet for clipper  
/SetBTC [wallet] | Set BTC waller for clipper  
/wallets |  
/SaveConfig |  
/SendConfig |  
/StartScreenLogger |  
/StartKeyLogger |  
/SendLog |  
/StopKeyLogger |  
/SendScreenshots |  
/StopScreenLogger |  
/ClipperStart |  
/ClipperStop |  
/ClipboardLoggerStart |  
/ClipboardLoggerSend |  
/ClipboardLoggerStop |  
/clipboard |  
/functions |  
/exit | Menu navigation  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1379/>

