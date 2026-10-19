编者注：本文仅供学习研究，严禁从事非法活动，任何后果由使用者本人负责。

##  **前言**

总结了一下现在还能用的关闭Defender的方法，部分是原创，一部分借鉴的大佬。觉得字多的同学可以直接跳过思路查看步骤进行实操。

###

##  **修改注册表关闭Defender**

 **1.测试环境**

windows10 20H2

windows10 21H2

windows11![](https://image.3001.net/images/20220315/1647324188_62302c1cc2f875ab5e2f5.png!small)

 **2.思路**

微软为了提供用户更妥善的安全保护，在2020年8月更新中更新了支持文档。若用户安装了其他杀毒软件，Defender将自动关闭；若用户卸载杀毒软件解决方案，Defender将强制自动开启。那我们可不可以模拟杀毒软件的行为，让Defender误以为我们安装了杀软，从而达到关闭Defender的目的呢？答案是可以的。

将系统注册表备份，安装杀毒软件后再次提取注册表信息并进行对比。最后将疑似影响Defender运行的键值进行改动对比，最终得出几个键值的排列组合可以达到沉默Defender的作用。

HKLM\SOFTWARE\Policies\Microsoft\Windows
Defender下，DisableAntiSpyware的值改为1，DisableAntiVirus的值改为1。

默认情况下并无这两个键值。

![](https://image.3001.net/images/20220315/1647325357_623030ad54d147613bd59.png!small)更改后：

![](https://image.3001.net/images/20220315/1647327765_62303a15b4a6ab6950fbc.png!small)HKLM\SOFTWARE\Microsoft\Security
Center\Provider\Av\\{D68DDC3A-831F-4fae-9E44-DA132C1ACF46}下，STATE改为
0x00060100。

![](https://image.3001.net/images/20220315/1647328320_62303c402876d415a5fd6.png!small)

 **3.步骤**

管理员模式打开命令行，执行：

    
    
    reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiSpyware /t reg_dword /d 1 /f
    reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiVirus /t reg_dword /d 1 /f
    
    reg add "HKLM\SOFTWARE\Microsoft\Security Center\Provider\Av\{D68DDC3A-831F-4fae-9E44-DA132C1ACF46}" /v STATE /t reg_dword /d "0x00060100" /f

 **4.成果**

修改完后重启，Defender仍然运行，但杀毒引擎已失效。

这里随意丢上一个msf的木马，成功绕过检测。

![](https://image.3001.net/images/20220315/1647329013_62303ef598982cc64c43c.png!small)

 **5.总结**

1）需要管理员权限操作。

2）重启后才能生效。

3）执行完reg add命令后需要检查注册表是否生效，有时执行后注册表未更新，需多执行几次。

4）某些版本只需要更改DisableAntiVirus和STATE这两个键值即可生效。

##  **PowerShell**

 **1.测试环境**

windows10 1809

windows11

![](https://image.3001.net/images/20220315/1647329211_62303fbbc5ae2bdb90281.png!small)![](https://image.3001.net/images/20220315/1647329261_62303fedb6a7269165ba4.png!small)

 **2.步骤**

管理员权限打开powershell，输入如下命令：

    
    
    $preferences = Get-MpPreference
    Set-MpPreference -DisableRealtimeMonitoring (!$preferences.DisableRealtimeMonitoring)

 **3.成果**

实时保护已关闭，且木马正常运行。

![](https://image.3001.net/images/20220315/1647329881_623042594c53d9ad158d3.png!small)

 **4.总结**

1）实时监控虽然关闭，但扫描引擎还正常运行，此时主动扫描木马还是会被检测到。

2）某些系统版本不生效，如windows10 20H2。

![](https://image.3001.net/images/20220315/1647330310_623044062292dc23d24db.png!small)

##  **TrustedInstaller权限关闭Defender**

 **1.原理**

TrustedInstaller权限是windows vista或7里面为了系统安全起见而设立的，为系统最高权限，比我们所熟知的System权限更高。

在Windows
XP及以前，System账户与管理员组对系统文件都有着完全访问的权限。这意味着以管理员身份运行的程序可以任意更改系统，降低了系统安全性。TrustedInstaller则改变了这一情况，使得只有拥有TrustedInstaller令牌的系统进程才能更改系统重要内容，而其他大部分系统服务就没有权限。
这是因为，以SYSTEM权限运行的程序不一定同时拥有TrustedInstaller的权限，只有通过了Service Control
Manager（服务启动控制器）的验证后才能获取。

所以SYSTEM权限做不到的事情，我们可以尝试通过TrustedInstaller权限实现。

 **2.思路**

我们可以利用工具获取TrustedInstaller权限，从 Nirsoft
官方页面（https://www.nirsoft.net/utils/advanced_run.html）下载 **AdvancedRun** 。

将可执行文件AdvancedRun.exe解压出来后即可执行如下命令将程序作为TrustedInstaller启动。

    
    
    AdvancedRun.exe /EXEFilename "c:\windows\system32\cmd.exe" /RunAs 8 /Run

此时弹出一个cmd，虽然查看当前用户显示System，但我们使用 whoami /priv查看特权还是能对比出与System的差别的。

TrustedInstaller:

![](https://image.3001.net/images/20220315/1647331016_623046c84b5df2e2eb488.png!small)

System:

![](https://image.3001.net/images/20220315/1647331331_62304803a37a115aa4a34.png!small)

接下来我们尝试利用TrustedInstaller权限来关闭Defender。

创建一个vbs脚本来自动化关闭Defender，内容如下。

    
    
    cription: Script to disable the Microsoft Defender Antivirus serviceSet ServiceSet = GetObject("winmgmts:").ExecQuery _("select * from Win32_Service where Name='WinDefend'")For Each Service In ServiceSetRetVal = Service.StopService() If RetVal <> 0 Then MsgBox "Error " & RetValEnd IfService.ChangeStartMode("Manual")Next

利用wscript.exe执行脚本。

    
    
    AdvancedRun.exe /EXEFilename "%windir%\system32\wscript.exe" /CommandLine '"C:\Users\Pepper\Downloads\advancedrun\1.vbs"' /RunAs 8 /Run

返回错误。

![](https://image.3001.net/images/20220315/1647331568_623048f028b19eb261150.png!small)

Error 2 表示用户没有所需的访问权限。

既然没有对服务的访问权限，那我们可以试一下能不能直接关闭Defender的进程，将上面的脚本改动一下，关闭MsMpEng.exe进程：

    
    
    Set ServiceSet2 = GetObject("winmgmts:\\.\root\cimv2")
    Set ServiceSet = ServiceSet2.Execquery("select * from Win32_Process where Name='MsMpEng.exe'")
    For Each Service In ServiceSet
      RetVal = Service.Terminate() 
      If RetVal <> 0 Then 
        MsgBox "Error " & RetVal
      End If
    Next

又返回了Error2，思路似乎到这里就断了。但是之前研究Defender注册表的时候发现了一个表项中存储着Defender的运行信息，当时将权限提升到System也没有修改成功。

![](https://image.3001.net/images/20220315/1647331704_62304978164b3cae1a358.png!small)试着以TrustedInstaller权限修改一下。

![](https://image.3001.net/images/20220315/1647332073_62304ae96a597619cccf6.png!small)![](https://image.3001.net/images/20220315/1647332133_62304b2533c324960f5b8.png!small)

轻松干掉Defender。

 **3.步骤**

1）TrustedInstaller权限启动cmd。

    
    
    AdvancedRun.exe /EXEFilename "c:\windows\system32\cmd.exe" /RunAs 8 /Run

2）执行reg add命令，修改注册表

    
    
    reg add "HKLM\SOFTWARE\Microsoft\Windows Defender" /v DisableAntiSpyware /t reg_dword /d 1 /f

 **4.总结**

与方案一相比，不需要重启，但是需要上传工具获取TrustedInstaller权限。

##  **修改进程Token，关闭杀毒引擎**

 **1.原理**

利用Windows 提供的OpenProcessTokenAPI
与进程令牌进行交互，MSDN声明必须PROCESS_QUERY_INFORMATION有权使用OpenProcessToken，但实际未受保护的进程可以通过PROCESS_QUERY_INFORMATION操作受保护进程的令牌。使用这种技术，攻击者可以强行删除MsMpEng.exe令牌中的所有权限，并将其从系统降低到不受信任的完整性。对不受信任的完整性的削弱会阻止受害进程访问系统上的大多数安全资源，从而在不终止进程的情况下悄悄地使进程失去能力。

 **2.思路**

已经有师傅[写好代码并开源](https://github.com/pwn1sher/KillDefender)了，这里大概讲解一下思路。

![](https://image.3001.net/images/20220315/1647332208_62304b704f8641472c433.png!small)首先执行EnableDebugPrivilege函数提升当前进程权限，然后利用getpid函数获取到我们想修改Token的进程的PID，实现逻辑是遍历当前进程名，匹配后返回该进程PID。

![](https://image.3001.net/images/20220315/1647332251_62304b9b30bf0684520fa.png!small)利用OpenProcess打开指定进程，并调用OpenProcessToken获取该进程Token。

![](https://image.3001.net/images/20220315/1647332280_62304bb801b9273e0298d.png!small)接下来需要使用
SetPrivilege()函数将进程的权限全部都去除掉。

![](https://image.3001.net/images/20220315/1647332781_62304dad46ef9a2764cc2.png!small)SetPrivilege的实现和之前提到过的EnableDebugPrivilege函数实现方式类似，主要用到三个函数：OpenProcessToken获取进程的令牌句柄，LookupPrivilegeValue查询进程权限，AdjustTokenPrivileges修改进程权限。注意EnableDebugPrivilege是修改当前进程的DEBUG权限，SetPrivilege是修改指定进程的指定权限。

![](https://image.3001.net/images/20220315/1647332882_62304e120b21e625ead46.png!small)

最后使用SetTokenInformation设置信息替换访问令牌的现有信息，破坏其完整性。

 **3.局限**

必须获取system权限才能使用该方法。

![](https://image.3001.net/images/20220315/1647333105_62304ef10e3b067068e19.png!small)

 **4.成果**

扫描引擎已失效，点击扫描无法正常运行。

![](https://image.3001.net/images/20220315/1647333339_62304fdbb56c0e5e3d36a.png!small)生成一个原始木马，未被识别并上线。

![](https://image.3001.net/images/20220315/1647333700_62305144cc890302f4513.png!small)![](https://image.3001.net/images/20220315/1647333742_6230516e662c791a3420b.png!small)![](https://image.3001.net/images/20220315/1647333782_623051968347ea1263ab1.png!small)

继续测试火绒的进程HipsDaemon.exe，同样生效。

![](https://image.3001.net/images/20220315/1647333805_623051adbffe007c586e6.png!small)测试360时，发现有行为检测被拦截。

![](https://image.3001.net/images/20220315/1647333827_623051c324d2733bb70d6.png!small)测试卡巴斯基，可以关闭扫描引擎，但会由于未知原因断网，难以利用。

![](https://image.3001.net/images/20220315/1647334550_62305496b6d16f85f768d.png!small)

##  **利用驱动关闭杀毒引擎**

 **1.原理**

加载自带微软官方签名的 ProcExp 驱动，利用其导出函数做到 Kill EDR 的效果。

 **2.思路**

大佬已经写得很好了，参考[资料](http://ryze-t.com/posts/2021/06/29/EdrKiller.html)。

 **其它**

K杀软的方式还有很多，比如还可以修改组策略，利用未文档化函数等，参考[资料](https://xz.aliyun.com/t/10663)。

##  **参考内容**

https://www.winhelponline.com/blog/enable-or-disable-defender-shortcut-command-line/

https://www.winhelponline.com/blog/run-program-as-trustedinstaller-locked-registry-keys-files/

http://ryze-t.com/posts/2021/06/29/EdrKiller.html

https://elastic.github.io/security-research/whitepapers/2022/02/02.sandboxing-antimalware-products-for-fun-and-profit/article/

  

  

