**一旦我们渗透进了内网，我们往往需要尽可能多的了解以及收集内网的信息，这将决定我们下一步的提权和渗透行为。而在内部侦察中，传统的方式是使用Windows内置命令（如net
view，net
user等）来获取主机和域的信息。但这些命令并不隐蔽，它们极有可能被管理人员和监控系统所发现。因此，为了避免这种情况，我们可以使用其它的方法。例如我们可以使用PowerShell和WMI，来进行态势感知躲避检测。**

## PowerView

PowerView是由[Will
Schroeder](https://twitter.com/harmj0y)开发的PowerShell脚本，属于[PowerSploit](https://github.com/PowerShellMafia/PowerSploit)框架和Empire的一部分。该脚本完全依赖于PowerShell和WMI（Windows
Management
Instrumentation）查询。从现有的meterpreter会话中，可以使用以下命令加载和执行PowerView，以检索有关该域的信息：

    
    
    load powershell
    powershell_import /root/Desktop/PowerView.ps1
    powershell_execute Get-NetDomain

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276352967384.png!small)

PowerView有各种可以发现本地管理员的cmdlet。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276353137774.png!small)

Invoke-UserHunter可以帮助扩展网络访问，因为它可以识别用户登录的系统，并验证当前用户是否具有对这些主机的本地管理员访问权限。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276353311888.png!small)

由于PowerView包含多个cmdlet，因此还可以检索域信息。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276353493551.png!small)

PowerView也在Empire内部实现。下图显示了网络的域策略。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276353692133.png!small)

还有一些模块可以执行基于主机的枚举。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276353874276.png!small)

另外还有一个PowerView的Python实现，如果提供了证书，它可以从不属于域的一部分的主机执行。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276354048194.png!small)

## HostRecon

还有一个PowerShell脚本，它可以自动实现主机中的态势感知任务。[Beau
Bullock](https://twitter.com/dafthack)开发了[HostRecon](https://github.com/dafthack/HostRecon)，并可以使用PowerShell和WMI查询从主机检索各种信息以逃避检测。

    
    
    powershell_import /root/Desktop/HostRecon.ps1
    powershell_execute Invoke-HostRecon

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276354223983.png!small)

HostRecon可以枚举本地用户和主机的本地管理员。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/1527635441754.png!small)

该脚本将执行一系列检查来确定防火墙状态，安装了反病毒解决方案，如果使用LAPS和应用程序白名单产品。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276354612068.png!small)

该脚本还会尝试识别域名密码策略，域控制器和域管理员等域名信息。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276354819048.png!small)

## HostEnum

Andrew
Chiles开发了一个类似的脚本HostRecon，该脚本在主机中执行时会提供详细信息。HostEnum既可以在本地执行，也可以从内存中执行，并且可以以HTML格式生成输出。

    
    
    load powershell
    powershell_import /root/Desktop/HostEnum.ps1
    powershell_shell
    Invoke-HostEnum -Local -Domain
    HostEnum

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276354997073.png!small)

参数 **-Domain** 将执行某些域检查，如检索域用户列表和其他域信息。

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276355202170.png!small)

域信息：

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276355373645.png!small)

## RemoteRecon

在获得本地管理员凭证并将这些凭证共享到多个主机的情况下，可以利用WMI来执行远程主机上的态势感知。[RemoteRecon](https://github.com/xorrior/RemoteRecon)由[Chris
Ross](https://twitter.com/xorrior)开发，其目的是让红队无需部署原始植入物的情况下即可进行侦察。该脚本可以捕获击键和屏幕截图，执行命令和shellcode，还可以加载PowerShell脚本以执行其他任务。

在进行任何操作之前，需要使用本地管理员凭据将脚本首先远程安装到主机中，或者如果当前用户已经是目标主机上的本地管理员，则只需提供计算机名称。

    
    
    Import-Module .\RemoteRecon.ps1
    Install-RemoteRecon -ComputerName 'WIN-2NE38K15TGH'

![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/1527635565452.png!small)

通过脚本执行的命令输出可以使用Results参数进行检索。

    
    
    Invoke-PowerShellCmd -ComputerName 'WIN-2NE38K15TGH' -Cmd "ps -name exp" -Verbose
    Invoke-PowerShellCmd -ComputerName 'WIN-2NE38K15TGH' -Results
    

##
![PowerView：一个可以帮助你躲避检测的内网信息收集脚本](https://image.3001.net/images/20180530/15276355877942.png!small)

## 参考

> <https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon>
>
> <https://www.blackhillsinfosec.com/hostrecon-situational-awareness-tool/>
>
> <http://threatexpress.com/2017/05/invoke-hostenum/>
>
> <https://github.com/dafthack/HostRecon>
>
> <https://github.com/xorrior/RemoteRecon>

 ***参考来源：[pentestlab](https://pentestlab.blog/2018/05/28/situational-awareness/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  

