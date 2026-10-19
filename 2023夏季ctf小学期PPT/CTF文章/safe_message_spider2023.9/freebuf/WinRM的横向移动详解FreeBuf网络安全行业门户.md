横向的手法从简单的远程桌面协议（rdp）到漏洞利用，手法不断在改变，要对抗的设备产品也不断地变化，有个技术主管问我，红蓝的快乐在于什么？为什么我钟情在红蓝。我想中快乐就是来自于对抗吧。

## WinRM的简要概述

> Windows Remote Management (WinRM) is the Microsoft implementation of WS-> Management Protocol, a standard Simple Object Access Protocol (SOAP)-based,
> firewall-friendly protocol that allows hardware and operating systems, from
> different vendors, to interoperate.

简单来说，winRm（微软远程管理）是WS-Management协议的实现组件。WinRM是windows操作系统的一部分。是一项允许管理员在系统上远程执行管理任务的服务。通信通过HTTP（5985）或HTTPS
SOAP（5986）执行，默认情况下支持Kerberos和NTLM身份验证以及基本身份验证。使用此服务需要管理员级别的凭据。

而WS-Management协议是基于标准的简单对象访问协议（SOAP）的，防火墙友好的协议，允许来自不同供应商的硬件和操作系统进行互操作。WS-Management协议规范为系统提供了一种跨IT基础结构访问和交换管理信息的通用方法。WinRM和智能平台管理接口（IPMI）以及事件收集器是Windows硬件管理功能的组件。

WS-Management Protocol

> The WS-Management protocol was developed by a group of hardware and  
> software manufacturers as a public standard for remotely exchanging  
> management data with any computer device that implements the protocol.

## WinRM的调用手法

> You can use WinRM scripting objects, the WinRM command-line tool, or  
> the Windows Remote Shell command line tool WinRS to obtain management  
> data from local and remote computers that may have baseboard  
> management controllers (BMCs). If the computer runs a Windows-based  
> operating system version that includes WinRM, the management data is  
> supplied by Windows Management Instrumentation (WMI).

微软文档中我们可以知道调用  
winRm脚本对象  
winRm的命令行工具  
windows Remote shell (winRs)命令行工具  
来获取本地或远程主机的基板管理控制器（bmc）这个我们可以不用理会，我们可以看到如果计算机运行的是基于Windows操作系统的话，我们还能通过WS-Management协议获得远程计算机的硬件和系统数据等等功能，

## WinRM的通信过程

windows Rm（微软远程管理）采用的是WS-Management协议来进行通信。

### 1.初始认证

身份验证向服务器（也可以是主机）确认客户端的身份  
当客户端使用其计算机名连接到域服务器时，默认身份验证协议是Kerberos。

    
    
    Kerberos保证用户身份和服务器身份，而无需发送任何类型的二次凭据。
    

如果没有办法进行Kerberos认证的话，

    
    
    例如：当客户端使用其IP地址连接到域服务器或连接到工作组服务器时，则无法进行Kerberos身份验证。
    

这时候会采用NTLM身份验证协议，但是默认情况下，基于NTLM的身份验证是禁用的。

    
    
    NTLM身份验证协议可确保用户身份，而无需发送任何可委托的凭据。为了证明用户身份，NTLM协议要求客户端和服务器均从用户密码计算会话密钥，而无需交换密码本身。服务器通常不知道用户的密码，因此它与域控制器通信，后者确实知道用户的密码并计算服务器的会话密钥。
    

这里插一句为什么默认禁用TLM的身份验证？

    
    
    NTLM协议不能保证服务器的身份。与使用NTLM进行身份验证的所有协议一样，有权访问加入域的计算机的计算机帐户的攻击者可以调用域控制器来计算NTLM会话密钥，从而模拟服务器。例如著名的烂土豆，所以当我们看到winrm使用NtLM认证的话，可以试一下攻击。
    

其它认证在这里不多说

    
    
    基于证书
    协商身份验证
    CredSSP
    可信主机
    等等
    

### 2.通信过程

初始身份验证完成后，WinRM将对正在进行的通信进行加密。这里加密有：  
通过HTTPS连接时，TLS协议用于协商用于传输数据的加密。  
通过HTTP连接时，消息级别的加密取决于所使用的初始身份验证协议。

    
    
    基本身份验证不提供加密。
    NTLM身份验证使用带有128位密钥的RC（4）密码。
    Kerberos身份验证加密由etypeTGS票证中的确定。这是现代系统上的AES-256。
    CredSSP加密使用的是握手中协商的TLS密码套件。

在域中的话一般是Kerberos身份验证，所以我们可以简单理解为winRm通信的过程是采用AES-256加密的，那么在利用这个手法进行横向的时，我们的流量是加密的，会隐蔽安全一些。

### 3.无法访问的情况

WinRM服务将在Windows Server 2008和更高版本上自动启动（在Windows Vista中，需要手动启动该服务）。  
默认情况下，未配置WinRM侦听器。即使WinRM服务正在运行，也无法接收或发送请求数据的WS-Management协议消息。  
Internet连接防火墙（ICF）阻止访问端口。

## 实战利用手法

### 检测

我们都知道winrm通过HTTP（5985）或HTTPS
SOAP（5986）端口来进行通信，那么我们可以检索内网中打开端口5985和5986的主机。这里为了方便我们使用nmap来进行演示

这里的环境是：

> 攻击机器：192.168.50.146  
> web边界服务器：10.10.10.8/192.168.50.101  
> 内网目标主机：10.10.10.10

我们来探测一下winrm的http 5985端口是否开放吧，这里使用nmap要注意速率问题，还有就是nmap的特征更改一下，扫描模式使用隐蔽扫描吧

![微信截图_20201230151403.png](https://image.3001.net/images/20210101/1609511967_5fef341fc4b3b96c939fb.png!small)

可以看到是开放的。但是5985端口走的是没加密的http服务，如果在实战中的话因为流量没有加密可能会不够隐蔽，注意手法吧，万一让检测到就gg了

当然在cs中也可以探测端口是否开放;

![微信截图_20201230151853.png](https://image.3001.net/images/20210101/1609511956_5fef34148b4f9ce274efb.png!small)

这里要注意速率要低调一点，预防还没进行横向就在端口探测阶段就让蓝队捕捉到了我们的流量。

![微信截图_20201230152504.png](https://image.3001.net/images/20210101/1609511947_5fef340b7fbc233463217.png!small)

可以看到返回了扫描信息。

### 使用winrs.exe来执行远程命令利用

Winrs.exe 是一个内置的命令行工具,它允许远程命令的执行在WinRm的适当的有资格的用户。 命令支持各种开关以及使用备用凭据进行身份验证的能力。

    
    
    C:\Users\（123223Li）>winrs.exe /?
    
    用法
    =====
    (全部大写的字符 = 必须由用户提供的值。)
    
    winrs [-/SWITCH[:VALUE]] COMMAND
    
    COMMAND - 可以作为 cmd.exe 外壳程序中的命令来执行的任何字符串。
    
    开关
    ========
    (所有开关都接受短形式或长形式。例如 -r 和
    -remote 都有效。)
    
    -r[emote]:ENDPOINT      - 使用 NetBIOS 名称或标准连接 URL: [TRANSPORT://]TARGET[:PORT] 的目标终结点。如果未指定该点，
    则使用 -r:localhost。
    
    -un[encrypted]          - 指定不加密到远程外壳程序的消息。这在以下情况下有用: 疑难解答、已使用 IPSec 加密网络通讯，或者 强制使用物理安全性。默认情况下，使用 Kerberos 或 NTLM 密钥加密消息。选择 HTTPS 传输时忽略该开关。
    
    -u[sername]:USERNAME    - 在命令行上指定用户名。如果未指定该用户名，则工具将使用协商身份验证或提示指定名称。
    如果指定 -username，则还必须指定 -password。
    
    -p[assword]:PASSWORD    - 在命令行上指定密码。如果未指定 -password 而指定 -username，则工具将提示指定密码。如果指定 -password，则还必须指定 -user。
    
    -t[imeout]:SECONDS      - 不推荐使用该选项。
    
    -d[irectory]:PATH       - 指定远程外壳程序的启动目录。如果未指定，则远程外壳程序将在用户的主目录下启动，该主目录由环境变量 %USERPROFILE% 定义。
    
    -env[ironment]:STRING=VALUE   - 指定外壳程序启动时要设置的单个环境变量，这允许更改外壳程序的默认环境。必须多次使用该开关来指定多个环境变量。
    
    -noe[cho]               - 指定应禁用该回显。可能需要此操作来确保不在本地显示用户对远程提示的响应。默认情况下，回显为 "on"。
    
    -nop[rofile]            - 指定不应加载用户的配置文件。默认情况下，服务器将试图加载用户配置文件。如果远程用户不是目标系统上的本地管理员，则需要使用该选项 (默认设置将导致错误)。
    
    -a[llow]d[elegate]      - 指定可以将用户凭据用于访问远程共享，例如，不是目标终结点所在的计算机上创建的远程共享。
    
    -comp[ression]          - 启用压缩。远程计算机上的旧安装可能不支持压缩，因此默认情况下处于禁用状态。
    
    -[use]ssl               - 在使用远程终结点时使用 SSL 连接。指定该传输 "https:" 以外的设置时，将使用默认的 WinRM 默认端口。
    
    -?- 帮助
    
    若要终止远程命令，用户可以键入 Ctrl-C 或 Ctrl-Break，该键入将被发送到远程外壳程序。第二次 Ctrl-C 将强制终止 winrs.exe。
    
    若要管理活动的远程外壳程序或 WinRS 配置，请使用 WinRM 工具。管理活动的外壳程序的 URI 别名为 shell/cmd。WinRS 配置的 URI 别名为 winrm/config/winrs。键入 "WinRM -?" 可以在 WinRM 工具中找到示例用法。
    
    示例:
    winrs -r:https://myserver.com command
    winrs -r:myserver.com -usessl command
    winrs -r:myserver command
    winrs -r:http://127.0.0.1 command
    winrs -r:http://169.51.2.101:80 -unencrypted command
    winrs -r:https://[::FFFF:129.144.52.38] command
    winrs -r:http://[1080:0:0:0:8:800:200C:417A]:80 command
    winrs -r:https://myserver.com -t:600 -u:administrator -p:$%fgh7 ipconfig
    winrs -r:myserver -env:PATH=^%PATH^%;c:\tools -env:TEMP=d:\temp config.cmd
    winrs -r:myserver netdom join myserver /domain:testdomain /userd:johns /passwordd:$%fgh789
    winrs -r:myserver -ad -u:administrator -p:$%fgh7 dir \\anotherserver\share
    

那么我们可以直接利用

![微信截图_20201230205741.png](https://image.3001.net/images/20210101/1609511934_5fef33fe7b6a80ec411aa.png!small)

这个工具的优点是它是winrm的工具，我们不用往主机上扔工具。  
不好的地方就是：使用这个工具需要明文密码。

ok，我们来分析一下这个工具的流量情况等等。  
首先它的流量是加密的（AES）这个还是很安全的，然后我们看看windows主机中日志情况

这里是这个winrs的攻击利用链：

    
    
    svchost.exe (DcomLaunch)-> winrshost.exe -> cmd.exe [/c remote command] -> [remote command/binary]
    

![微信截图_20201230210434.png](https://image.3001.net/images/20210101/1609511924_5fef33f4bc8dde6000539.png!small)

Winrs事件以Microsoft-Windows-WinRM / Operational（事件ID 91）记录在远程主机上，横向成功记得屁屁，

### Winrm.vbs（通过Winrm.cmd调用）

Winrm.vbs是一个Visual Basic脚本，允许管理员“配置WinRM并获取数据或管理资源”  
是基于WinRM脚本API，而这个api使我们使能够从远程计算机执行WS-Management协议操作和获得数据。

    
    
    微软文档：https://docs.microsoft.com/en-us/windows/win32/winrm/about-windows-remote-management
    

> This command–line tool for system management is implemented in a  
> Visual Basic Scripting Edition file (Winrm.vbs) written using the  
> WinRM scripting API. This tool enables an administrator to configure  
> WinRM and to get data or manage resources. For more information, see  
> the online help provided by the command line

那么我们往下看可以看到一个有意思的东西

> WMI service
>
> The WMI service continues to run side-by-side with WinRM and provides  
> requested data or control through the WMI plug-in. You can continue to  
> obtain data from standard WMI classes, such as Win32_Process, as well  
> as IPMI-supplied data. For more information about configuration and  
> installation required for WinRM,

WinRM（.vbs）允许通过WinRM传输进行WMI对象的远程交互？？wmi之前我们分析过它横向利用手法。那么winrm（.vbs）可以调用wmi不就是：

通过已控机器与目标进行winrm通信，然后调用目标主机的wmi执行命令。而目标与已控机器之间的通信时加密的，蓝队在进行目标机器检测朔源的情况下，是先检测到wmi在执行恶意命令，但是没有发现wmi的横向情况，会不会想到是我们是通过winrm去远程调用wmi？哈哈哈

然后我们可以看看winrm.vbs的一个使用吧

    
    
    winrm -?

![微信截图_20201230225914.png](https://image.3001.net/images/20210101/1609511913_5fef33e9a7860d99313ae.png!small)

这里我们要注意一个是调用的方式一个是认证方面的东西，就是我指出来的那些。然后在域环境下的话，我们还是使用kerberos吧

![微信截图_20201230230702.png](https://image.3001.net/images/20210101/1609511904_5fef33e00e64d29392871.png!small)

我们可以利用一个非常著名的WMI类，Win32_Process，可通过利用来生成（远程）进程执行命令。

    
    
    winrm invoke Create wmicimv2/Win32_Process @{CommandLine="notepad"} -r:corp-dc
    

利用winrm.vbs远程控制主机调用wmicimv2/Win32_Process wmi类来打开一个notepad.exe（相当于执行命令）

![微信截图_20201230224653.png](https://image.3001.net/images/20210101/1609511894_5fef33d6766a89faec4d2.png!small)  
流程标识符 （PID）和 返回值 在事件XML元数据中返回，以确认成功执行远程操作

ok 我们来看看一个目标上面的一个情况

    
    
    svchost.exe (DcomLaunch) -> wmiprvse.exe -> [remote command/binary]
    

![微信截图_20201230225401.png](https://image.3001.net/images/20210101/1609511881_5fef33c96e4c2aae05894.png!small)

### 第3方工具

 **cobalt strike**

在cs中有2中winrm的横向方法，利用成功会自动返回一个会话，当然如果不出网的话我们就需要借助cs中的一个中转手法。

这里演示的手法是不出网络的情况

![微信截图_20201230232804.png](https://image.3001.net/images/20210101/1609511863_5fef33b797bb6a54bfcea.png!small)

这里看到是分别有winrm和winrm64

    
    
    winrm    x86    Run a PowerShell script via WinRM
    winrm64    x64    Run a PowerShell script via WinRM
    

cobalt strike 官方文档中我们知道在cobalt strike中使用wimRM的过程是：

使用powershell调用winRM所以我们可以看看下图

![微信截图_20210101192908.png](https://image.3001.net/images/20210101/1609511850_5fef33aa2db814267b5b5.png!small)

虽然打开PowerShell并不奇怪，但是使用powershell去调用winrm的话还是比较敏感。

ok 在cobalt strike利用winrm在域中横向移动需要获取到目标主机的账号密码或hash值，这里的流量也是aes加密的  
因为也是基于kerberos的一个认证。

![微信截图_20210101194113.png](https://image.3001.net/images/20210101/1609511828_5fef33942caf01e87e622.png!small)

注意，如果目标不出网的话，我们需要设置一个cs的中转监听器，让流量通过我们已控的主机回连到Cobalt Strike中

![微信截图_20210101194328.png](https://image.3001.net/images/20210101/1609511814_5fef3386541fc684a9fe2.png!small)

![微信截图_20210101194441.png](https://image.3001.net/images/20210101/1609511802_5fef337a909c0077cfc4f.png!small)

开始横向移动

![微信截图_20210101194537.png](https://image.3001.net/images/20210101/1609511776_5fef336080e8e3f8f44d9.png!small)

横向成功会返回一个会话

![微信截图_20210101194710.png](https://image.3001.net/images/20210101/1609511760_5fef3350900d507f617c0.png!small)

因为目标走已控主机回连cobalt strike中 那么在目标主机中的网络连接情况：

![微信截图_20210101195312.png](https://image.3001.net/images/20210101/1609511725_5fef332d4841d42836c18.png!small)

然后看到一个5985的端口，也就是winrm的通信端口，则意味着WinRM服务被配置为仅接受通过HTTP的连接，并且未启用加密。，貌似winrm和winrm64都是使用5985端口的。

 **Metasploit**  
Metasploit框架具有多个模块，可用于发现启用了WinRM服务的主机，发现用于服务认证的凭证以及执行任意命令和代码。

以下模块可以发现启用了WinRM服务的系统及其支持的身份验证协议。

    
    
    auxiliary/scanner/winrm/winrm_auth_methods
    

![微信截图_20210101214513.png](https://image.3001.net/images/20210101/1609511703_5fef33175d436c89f212e.png!small)

注意：我们需要添加好路由或使用代理把MSF带入内网中

如果已获取本地管理员凭据，则可以使用这些凭据通过WinRM服务与其他主机进行身份验证。

以下模块可以确定本地管理员凭据是否对其他系统有效。

    
    
    auxiliary/scanner/winrm/winrm_login 
    

![微信截图_20210101214736.png](https://image.3001.net/images/20210101/1609511686_5fef33068b85026c4e023.png!small)

Metasploit还有一个模块，可以通过WinRM服务执行任意命令。

该模块需要本地管理员凭据，域和目标主机。

    
    
    auxiliary/scanner/winrm/winrm_cmd
    

![微信截图_20210101214834.png](https://image.3001.net/images/20210101/1609511672_5fef32f8c217e6e480e9b.png!small)

命令返回：

![微信截图_20210101214916.png](https://image.3001.net/images/20210101/1609511654_5fef32e6d055efdfb3bf1.png!small)

也可以通过WinRM和以下模块执行任意代码。  
该模块需要本地管理员凭据以及将执行代码的主机列表。  
此模块可用于横向移动到共享相同本地管理员帐户的主机中。

    
    
    exploit/windows/winrm/winrm_script_exec
    

![微信截图_20210101215021.png](https://image.3001.net/images/20210101/1609511641_5fef32d99a3a94c1371e9.png!small)

利用后，模块将尝试修改PowerShell执行策略以允许执行未签名的脚本。然后，将PowerShell脚本写入磁盘并自动执行以返回Meterpreter会话。

该模块还将尝试迁移到系统级别的进程，以避免由于WinRS的时间限制而丢失外壳。

![微信截图_20210101215126.png](https://image.3001.net/images/20210101/1609511629_5fef32cd1785e369b4877.png!small)

### 防御

当然，存在检测和限制WinRM远程命令执行/横向移动的机会。考虑以下：

    
    
    监视源自wmiprvse.exe和winrshost.exe的远程进程执行链
    监视Microsoft-Windows-WinRM / Operational事件日志中的可疑条目。注意：在测试WMI类交互（WinRM.vbs / SharpWSManWinRM / etc）期间，似乎没有成功的连接会话记录在此处。但是，未成功的错误记录了WMI资源的名称。
    考虑将可信主机列入白名单，以仅允许某些计算机连接到WinRM服务器。可以在此Red Canary博客文章中找到更多信息。 注意：WinRM受信任的主机控制客户端可以连接到什么。这样，以集中方式控制此设置可能是有利的，但是更好的方法是利用跳转主机和（主机）防火墙规则来控制应允许哪些计算机连接到WinRM主机。
    管理员不是唯一可以利用WinRM进行远程管理的用户。该成员远程管理用户本地/域组可以在WinRM的连接到WMI资源。确保仅允许授权人员使用组成员身份。
    

## 参考：

> <https://bohops.com/2020/05/12/ws-management-com-another-approach-for-winrm-> lateral-movement/>  
> <https://pentestn00b.wordpress.com/2016/08/22/powershell-psremoting-pwnage/>  
> <https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/ps-> remoting-second-hop?view=powershell-7>  
> <https://docs.microsoft.com/en-us/windows/win32/winrm/portal>

学艺不精 有错误还望批评指正 最后还公司招红蓝对抗可以找我（dnsil@qq.com） 团队有几个同学找红蓝岗

