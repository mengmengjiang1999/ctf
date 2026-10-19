## 前提条件

> 1）后期利用期间可以通过目标NTLM身份验证
>
> 2）重启WinRM服务
>
> 3）使用此NTLM支持PowerShell Docker镜像到Linux的PS-> Remote，您可以从Linux到Windows进行PS远程到Windows。

## 背景资料

**偶然发现在我的测试中使用PowerShell远程处理作为维护系统远程代码执行的主要方法很有用。它是一个内置的Windows功能。不幸的是，由于PowerShell
Core的Linux分支支持的身份验证机制，从我的Kali Linux远程连接到我的目标并不是一件容易的事。**

PowerShell远程处理需要对Kerberos身份验证，这意味着客户端计算机和目标计算机必须都连接到同一域。如果我们没有可以连接的机器来执行远程处理，那么这对测试人员来说可能会造成问题。幸运的是，我们可以选择将自己添加为目标配置中的`“TrustedHost”`，这将允许我们执行NTLM身份验证而不是Kerberos，因此无需从域上的系统进行连接。

现在唯一的问题是，用于Linux的PowerShell核心（撰写本文时为PowerShell
6.1.0）并未支持NTLM身份验证。幸运的是，[Redditors](https://www.reddit.com/r/PowerShell/comments/6itek2/powershell_remoting_linux_windows_with_spnego/)找到了在Centos上使用PowerShell进行NTLM身份验证的方法，因此我将他们的发现整合到一个简单的PowerShell
Docker镜像[quickbreach / powershell-ntlm中](https://hub.docker.com/r/quickbreach/powershell-ntlm/)。

### 如何使用从Linux到Windows的PowerShell远程处理

本节将逐步介绍如何从Linux客户端到Windows目标建立远程PowerShell会话。假设您对目标PC具有管理访问权限（RDP，payload等）。

1.在目标上启用PowerShell远程处理

`Enable-PSRemoting –Force`

2.获取目标系统上当前 **TrustedHost** 的列表以供参考

`Get-Item WSMan:\localhost\Client\TrustedHosts`

3.将自己添加为目标上的 **TrustedHost** 。这是在Enter-PSSession设置阶段使用NTLM身份验证所必需的，这是唯一可用于通过PowerShell远程连接从Linux连接到Windows的身份验证机制。要完成此操作，请运行以下命令之一：使用通配符允许所有计算机在对此主机进行身份验证时使用NTLM

`Set-Item WSMan:\localhost\Client\TrustedHosts -Force -Value`

或者只将您的IP添加到NTLM身份验证允许列表中

`Set-Item WSMan:\localhost\Client\TrustedHosts -Force -Concatenate -Value
192.168.10.100`

![gotTrust.png](https://image.3001.net/images/20190126/1548490499_5c4c1703cc873.png!small)

4.设置并重新启动WinRM服务

`Set-Service WinRM -StartMode Automatic`

`Restart-Service -Force WinRM`

5.放入PowerShell-NTLM Docker镜像的实例。下面的示例命令还在docker镜像内的`/mnt`路径上安装包含PowerShell脚本

`docker run -it -v /pathTo/PowerShellModules:/mnt quickbreach/powershell-ntlm`

6.现在我们一直在等待：使用以下命令进入远程PowerShell会话 - 请注意，您必须指定-Authentication类型：

    
    
    # Grab the creds we will be logging in with  
    $creds = Get-Credential  
    ​  
    # Launch the session   
    # Important: you MUST state the  authentication type as Negotiate  
    Enter-PSSession -ComputerName (Target-IP) -Authentication Negotiate -Credential $creds  
    ​  
    # i.e.  
    ​  
    Enter-PSSession -ComputerName 10.20.30.190 -Authentication Negotiate -Credential $creds

您也可以以类似的方式使用Invoke-Command功能

`Invoke-Command -ComputerName 10.20.30.190 -Authentication Negotiate
-Credential $creds -ScriptBlock {Get-HotFix}`

![demo.png](https://image.3001.net/images/20190126/1548490526_5c4c171e7a0fd.png!small)

## 清除痕迹  

如果您的命令之前存在TrustedHosts以自行添加，请更换您的IP并运行以下命令：

    
    
    $newvalue = ((Get-ChildItem WSMan:\localhost\Client\TrustedHosts).Value).Replace(",192.168.10.100","")
    Set-Item WSMan:\localhost\Client\TrustedHosts -Force -Value $newvalue

或者，如果您是唯一的TrustedHosts，则可以删除所有TrustedHosts

`Clear-Item WSMan:\localhost\Client\TrustedHosts`

重新启动WinRM服务以完成更改（请注意，这将使您与Enter-PSSession断开连接）

`Restart-Service WinRM`

 ***参考来源[quickbreach](https://blog.quickbreach.io/ps-remote-from-linux-to-windows/)，由周大涛编译，转载请注明来自FreeBuf.COM**

