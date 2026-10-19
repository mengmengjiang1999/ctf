![20210804220640.jpg](https://image.3001.net/images/20210805/1628096390_610ac7860256716bcf564.jpg!small)

## 前言

WinRM 作为 Windows 操作系统的一部分，是一项允许管理员在系统上远程执行管理任务的服务。这样的服务当然不会被攻击者错过，本篇文章我们就来讲讲
WinRM 在横向渗透中的使用。

> 文中若有不当之处，还请各位大佬师傅们多多点评。
>
> 我的博客：<https://whoamianony.top/>

## WinRM 服务简介

WinRM 是 Windows Remote Managementd（Windows 远程管理）的简称，是 Web 服务管理标准 WebService-Management 协议的 Microsoft
实现。该协议是基于简单对象访问协议（SOAP）的、防火墙友好的标准协议，允许来自不同供应商的硬件和操作系统能够互操作。

WinRM 作为 Windows 操作系统的一部分，是一项允许管理员在系统上远程执行管理任务的服务。并且，WinRM 默认情况下支持 Kerberos 和
NTLM 身份验证以及基本身份验证，初始身份验证后，WinRM 会话将使用 AES 加密保护。使用 WinRM 服务需要拥有管理员级别的权限。

在现代 Windows 系统中，WinRM HTTP 通过 TCP 端口 5985 进行通信，而 HTTPS（TLS）通过 TCP 端口 5986
进行通信。如果所有的机器都是在域环境下，则可以使用默认的 5985 端口，否则的话则通过 5986 端口使用 HTTPS 传输。

使用 WinRM 我们可以在远程主机设置了防火墙的情况下远程管理这台服务器，因为启动 WinRM 服务后，防火墙默认会自动放行 5985
端口。这样的管理服务当然不会被攻击者错过，在内网渗透中，我们可以使用 WinRM
服务进行横向移动，并且使用这种远程连接进行横向移动不容易被察觉到，也不会占用远程连接数。

## WinRM 服务的安装与配置

要利用 WinRM 服务，并让`winrm`命令行工具执行相应操作，通信的双方必须同时安装和配置好 Windows 远程管理。

### WinRM 服务的安装

Windows 远程管理服务（WinRM）适用于 Windows Server 2008 和 Windows 7
以后的操作系统并自动与其支持的操作系统一起安装，但是只有在 Windows Server 2008 以上的操作系统 WinRM
服务才会自动启动，其他都需要手动开启。

### WinRM 服务的配置

默认情况下，不配置 WinRM 侦听器。 即使 WinRM 服务正在运行，也不能接收或发送 WS-Management 协议消息。

使用以下命令可以查看 WinRM 侦听器配置情况：

    
    
    winrm e winrm/config/listener  
    # 或 winrm enumerate winrm/config/listener

![image-20210804153757275](https://image.3001.net/images/20210805/1628096390_610ac7865eec35e004a5b.png!small)

如上图，有几个参数：

> Address：表示监听器所监听的地址。
>
> Transport：用于指定用于发送和接收 WS-Management 协议请求和响应的传输类型，如 HTTP 或 HTTPS，其默认值为 HTTP。
>
> Port：表示监听器所监听 TCP 端口。
>
> Hostname：正在运行 WinRM 服务的计算机的主机名。该值必须是完全限定的域名、IPv4 或 IPv6 文本字符串或通配符。
>
> Enabled：表示是启用还是禁用侦听器，其默认值为 True，表示启用。
>
> URLPrefix：用于指定要在其上接受 HTTP 或 HTTPS 请求的 URL 前缀。 例如，如果计算机名称为 SampleMachine，则
> WinRM 客户端将在目标地址中指定`https://SampleMachine/<在目标地址中指定的 URLPrefix>`。 默认 URL 前缀为
> "wsman"。
>
> CertificateThumbprint：用于指定服务证书的指纹。
>
> ListeningOn：用于指定侦听器使用的 IPv4 和 IPv6 地址。

若要检查具体配置设置的状态，可以使用以下命令：

    
    
    winrm get winrm/config

![image-20210804155451344](https://image.3001.net/images/20210805/1628096390_610ac7868e6d016d3dd9f.png!small)

你可以使用以下命令启动 WinRM 服务，并对 WinRM 服务进行默认配置：

    
    
    winrm quickconfig

![image-20210804160813342](https://image.3001.net/images/20210805/1628096390_610ac786d260fd2ef5131.png!small)

该命令将执行以下这些操作：

> 启动 WinRM 服务，并将服务启动类型设置为 "自动启动"。启动后，防火墙会默认并放行 5985 端口。
>
> 为在任何 IP 地址上使用 HTTP 或 HTTPS 发送和接收 WS-Management 协议消息的端口配置侦听器。
>
> 定义 WinRM 服务的 ICF 异常，并打开 HTTP 和 HTTPS 端口。

还有一些其他配置命令：

    
    
    # 使用 PowerShell 查询 WinRM 状态  
    Get-WmiObject -Class win32_service | Where-Object {$_.name -like "WinRM"}  
    ​  
    # 开启 WinRM 远程管理  
    Enable-PSRemoting –force  
      
    # 设置 WinRM 自启动  
    Set-Service WinRM -StartMode Automatic  
    ​  
    # 对 WinRM 服务进行快速配置，包括开启 WinRM 和开启防火墙异常检测, HTTPS传输, 5986端口  
    winrm quickconfig -transport:https      
      
    # 为 WinRM 服务配置认证  
    winrm set winrm/config/service/auth @{Basic="true"}  
      
    # 修改 WinRM 默认端口  
    winrm set winrm/config/client/DefaultPorts @{HTTPS="8888"}  
      
    # 为 WinRM 服务配置加密方式为允许非加密：  
    winrm set winrm/config/service @{AllowUnencrypted="true"}  
      
    # 设置只允许指定 IP 远程连接 WinRM  
    winrm set winrm/config/Client @{TrustedHosts="192.168.10.*"}  
    ​  
    # 设置允许所有 IP 远程连接 WinRM  
    winrm set winrm/config/Client @{TrustedHosts="*"}

## WinRM 的默认组访问权限

在安装过程中，WinRM 将创建本地组WinRMRemoteWMIUsers__，然后，WinRM
将远程访问设置为本地管理组和WinRMRemoteWMIUsers__组中的用户。我们可以通过以下命令

    
    
    net localgroup WinRMRemoteWMIUsers__ <username> /add 

来向WinRMRemoteWMIUsers__组中添加本地用户、域用户或域组。

## 利用 WinRM 服务远程执行命令

### 使用 winrs 命令

WinRS 是 Windows 的远程 Shell，它相当于 WinRM 的客户端，使用它可以访问运行有 WinRM 的服务器，不过自己也得装上 WinRM
才能运行 WinRS。使用如下。

在 WinRM 客户端主机上执行以下命令：

    
    
    winrs -r:http://192.168.93.30:5985 -u:administrator -p:Whoami2021 whoami  
    winrs -r:http://192.168.93.30:5985 -u:administrator -p:Whoami2021 ipconfig  
    # winrs -r:[ip] -u:[username] -p:[password] <command>

执行后得到以下报错：

![image-20210804172346402](https://image.3001.net/images/20210805/1628096391_610ac7872c7fc3bd7a4e4.png!small)

> Winrs error:WinRM 客户端无法处理该请求。可以在下列条件下将默认身份验证与 IP 地址结合使用: 传输为 HTTPS 或目标位于
> TrustedHosts 列表中，并且提供了显式凭据。使用 winrm.cmd 配置 TrustedHosts。请注意，TrustedHosts
> 列表中的计算机可能未经过身份验证。 有关如何设置 TrustedHosts 的详细信息，请运行以下命令: winrm help config。

此时，需要在客户端上执行下面这条命令，设置为信任所有主机，再去连接即可：

    
    
    winrm set winrm/config/Client @{TrustedHosts="*"}

然后便可以正常使用了：

![image-20210804172824608](https://image.3001.net/images/20210805/1628096391_610ac7875e1a3e801b040.png!small)

如上图所示，成功在远程主机上执行命令。

### 使用

