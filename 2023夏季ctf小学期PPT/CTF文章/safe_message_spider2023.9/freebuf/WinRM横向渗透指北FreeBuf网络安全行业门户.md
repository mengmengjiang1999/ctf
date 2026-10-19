# 前言

在针对Windows设备的横向渗透中，我们往往会碰到已知系统用户名和密码，却无从下手（远程桌面、SMB等服务不适合/关闭）的情况。这时，不妨转换下思路，以WinRM（Windows
Remote Management，Windows远程管理）服务为切入点控制Windows设备。

# 介绍

WinRM（Windows Remote Management，Windows远程管理）是Windows系统中的WS-Management实现。而WS-Management（Web Services-Management，Web服务管理，简称WSMan）是一种基于Web的用于管理分布式系统的协议，可以用来访问和操作远程资源，执行各种管理任务。因此，WinRM服务可以用来远程操作Windows设备，在该设备上执行任意命令，且不依赖于RDP，不会和远程桌面冲突，不易被防火墙拦截，不易被注意到，极有可能成为我们横向渗透的突破口。

WinRM客户端与服务端通过HTTP/HTTPS协议来互相通信，服务端URL的格式为：

    
    
    http(s)://<Host>:<Port>/<URLPrefix>
    

通信时，WinRM客户端会以POST方法请求服务端URL，根据响应的WWW-Authenticate标头来判断身份验证方法。接着再通过POST方法带上身份验证标头请求服务端URL，传递所要执行的命令等信息。且两者传输信息所用的端口号和URL前缀（默认为wsman）相同。

具体参见微软官方文档：[Windows 远程管理 - Win32 apps | Microsoft
Learn](https://learn.microsoft.com/zh-cn/windows/win32/winrm/portal)

# 基本用法

Windows系统已经预装了WinRM服务端以及对应的客户端工具WinRS（Windows Remote
Shell），直接在Powershell中输入相应的命令即可。

![WinRM](https://image.3001.net/images/20230822/1692697257_64e482a933c4fc14d265f.png!small)

![WinRS](https://image.3001.net/images/20230822/1692697301_64e482d56f9c673a78b22.png!small)

## 服务端

WinRM服务默认处于“已停止”状态，可以在"服务"中手动启动，或者运行如下命令一键配置WinRM服务

    
    
    winrm qc
    

![一键配置WinRM服务](https://image.3001.net/images/20230822/1692697361_64e483116727377b2d3ed.png!small)

这条命令会执行以下操作：

  * 启动WinRM服务并将其配置为自动启动

  * 在5985和5986端口上配置侦听器

  * 打开5985和5986端口并在系统防火墙中放行

至此，该设备上的WinRM服务便已配置完毕并启动了，我们可以使用WinRM客户端工具远程连接到该设备并执行各种命令。

当然，我们还可以再对配置信息进行检索和修改。

### 检索所有配置信息

输入以下命令并按回车，程序会返回WinRM服务的所有配置信息

    
    
    winrm g winrm/config
    

![检索所有配置信息](https://image.3001.net/images/20230822/1692697424_64e483503965e6bb89383.png!small)

### 列出所有侦听器信息

我们可以输入以下命令并回车来检查侦听器是否正常工作，并查看连接相关信息

    
    
    winrm e winrm/config/listener
    

![列出所有侦听器信息](https://image.3001.net/images/20230822/1692697495_64e483973f973c978a89f.png!small)

### 修改侦听端口（服务端与客户端共用）

输入以下命令并回车可以修改HTTP协议或者HTTPS协议对应的端口号（其中HTTP协议默认为5985，HTTPS协议默认为5986）

    
    
    winrm s winrm/config/Listener?Address=*+Transport=<HTTP或HTTPS> '@{Port="<目标端口号>"}'
    

![修改侦听端口](https://image.3001.net/images/20230822/1692697567_64e483df50fa31be29b06.png!small)

### 修改URL前缀

URL前缀默认为wsman，使用客户端工具连接时如果使用默认前缀可无需附带进去。输入以下命令可以进行修改。

    
    
    winrm s winrm/config/Listener?Address=*+Transport=<HTTP或HTTPS> '@{URLPrefix="<目标URL前缀>"}'
    

![修改URL前缀](https://image.3001.net/images/20230822/1692697624_64e48418ea060748d5277.png!small)

## 客户端

使用WinRS时，需要确保WinRM服务已启动且配置好。

在使用时，可能会出现目标地址不受信任的情况。这时候，可以输入以下命令，使任意地址都受信任：

    
    
    winrm s winrm/config/client '@{TrustedHosts="*"}'
    

![添加信任](https://image.3001.net/images/20230822/1692697685_64e48455569665d1235be.png!small)

完成后，输入以下命令就可以在目标设备上执行任意命令了

    
    
    winrs -r:'<http/https>://<Domain/Host/IP>:<Port>' -u:'<域>\<用户名>' -p:'<密码>' '<命令>'
    

![执行命令](https://image.3001.net/images/20230822/1692697734_64e484864bcda81b96068.png!small)

这里的域一般为目标设备的计算机名。如果用户是微软帐户，则域为AzureAD。有些时候，可以省略掉这一部分。

我们可以直接连接到目标设备的PowerShell来执行命令，而无需重复连接。

    
    
    winrs -r:'<http/https>://<Domain/Host/IP>:<Port>' -u:'<域>\<用户名>' -p:'<密码>' 'powershell'
    

![连接到PowerShell](https://image.3001.net/images/20230822/1692697795_64e484c3ba439cbdea357.png!small)

# 相关工具

在实际的渗透过程中，使用原版客户端工具WinRS的效率不是很高。因此，我们可以使用第三方WinRM客户端工具或者引入WinRM相关库写脚本来辅助我们进行横向渗透。这里简单地介绍一下Python中的WinRM客户端库pywinrm以及渗透测试常用的WinRM工具Evil-WinRM。

## pywinrm

pywinrm是Python下的WinRM客户端库。

### 安装

输入以下命令即可安装该模块：

    
    
    pip install pywinrm
    

对于部分身份验证方法，需要安装额外的库：

  * Kerberos

    
    
    # for Debian/Ubuntu/etc:
    $ sudo apt-get install gcc python-dev libkrb5-dev
    $ pip install pywinrm[kerberos]
    
    # for RHEL/CentOS/etc:
    $ sudo yum install gcc python-devel krb5-devel krb5-workstation python-devel
    $ pip install pywinrm[kerberos]
    

  * CredSSP

    
    
    # for Debian/Ubuntu/etc:
    $ sudo apt-get install gcc python-dev libssl-dev
    $ pip install pywinrm[credssp]
    
    # for RHEL/CentOS/etc:
    $ sudo yum install gcc python-devel openssl-devel
    $ pip install pywinrm[credssp]
    

### 例子

执行命令

    
    
    import winrm
    
    s = winrm.Session('windows-host.example.com', auth=('john.smith', 'secret'))
    r = s.run_cmd('ipconfig', ['/all'])
    print(r.status_code,"\n") // 打印状态码
    print(r.std_out,"\n") // 打印输出信息
    print(r.std_err,"\n") // 打印错误信息
    

输出

    
    
    0
    Windows IP Configuration
    
       Host Name . . . . . . . . . . . . : WINDOWS-HOST
       Primary Dns Suffix  . . . . . . . :
       Node Type . . . . . . . . . . . . : Hybrid
       IP Routing Enabled. . . . . . . . : No
       WINS Proxy Enabled. . . . . . . . : No
    ...
    

执行PowerShell脚本

    
    
    import winrm
    
    ps_script = """$strComputer = $Host
    Clear
    $RAM = WmiObject Win32_ComputerSystem
    $MB = 1048576
    
    "Installed Memory: " + [int]($RAM.TotalPhysicalMemory /$MB) + " MB" """
    
    s = winrm.Session('windows-host.example.com', auth=('john.smith', 'secret'))
    r = s.run_ps(ps_script)
    print(r.status_code,"\n") // 打印状态码
    print(r.std_out,"\n") // 打印输出信息
    print(r.std_err,"\n") // 打印错误信息
    

输出

    
    
    0
    Installed Memory: 3840 MB
    

具体参见：[pywinrm · PyPI](https://pypi.org/project/pywinrm/)

## Evil-WinRM

Evil-WinRM是一款专门为渗透测试打造的WinRM第三方客户端工具。它十分强大、易于使用，且具有以下特性：

  * 支持Linux和Windows

  * 支持在内存中加载脚本、DLL、程序、.NET程序集等以绕过部分杀软

  * 支持哈希传递

  * 支持以Kerberos方式进行身份验证

  * 支持以HTTPS协议传输

  * 列出没有特权的远程计算机服务

  * 命令历史记录

  * 输入自动补全

  * 支持日志记录

  * 支持在Docker中部署

  * 能够避免因误触Ctrl+C而退出Shell

因此，在实际的WinRM横向渗透中，使用这款工具不仅能满足我们的大部分需求，还能大大提高效率。

项目地址：https://github.com/Hackplayers/evil-winrm

Evil-WinRM已经预装于Kali
Linux上，直接在命令行中输入相应命令即可使用。对于其他系统以及安装方式，可以参照该项目Github的README.MD来操作。

输入以下命令可以查看帮助信息

    
    
    evil-winrm -h
    

![查看帮助信息](https://image.3001.net/images/20230822/1692697875_64e48513ebe30fea94ce7.png!small)

    
    
    Usage: evil-winrm -i IP -u USER [-s SCRIPTS_PATH] [-e EXES_PATH] [-P PORT] [-p PASS] [-H HASH] [-U URL] [-S] [-c PUBLIC_KEY_PATH ] [-k PRIVATE_KEY_PATH ] [-r REALM] [--spn SPN_PREFIX] [-l]
        -S, --ssl                        Enable ssl
        -c, --pub-key PUBLIC_KEY_PATH    Local path to public key certificate
        -k, --priv-key PRIVATE_KEY_PATH  Local path to private key certificate
        -r, --realm DOMAIN               Kerberos auth, it has to be set also in /etc/krb5.conf file using this format -> CONTOSO.COM = { kdc = fooserver.contoso.com }
        -s, --scripts PS_SCRIPTS_PATH    Powershell scripts local path
            --spn SPN_PREFIX             SPN prefix for Kerberos auth (default HTTP)
        -e, --executables EXES_PATH      C# executables local path
        -i, --ip IP                      Remote host IP or hostname. FQDN for Kerberos auth (required)
        -U, --url URL                    Remote url endpoint (default /wsman)
        -u, --user USER                  Username (required if not using kerberos)
        -p, --password PASS              Password
        -H, --hash HASH                  NTHash
        -P, --port PORT                  Remote host port (default 5985)
        -V, --version                    Show version
        -n, --no-colors                  Disable colors
        -N, --no-rpath-completion        Disable remote path completion
        -l, --log                        Log the WinRM session
        -h, --help                       Display this help message
    

已知目标设备系统用户名和密码时，输入以下命令并回车，即可连接到目标设备的PowerShell

    
    
    evil-winrm -i <目标设备IP> -u <用户名> -p <密码>
    

![连接到PowerShell](https://image.3001.net/images/20230822/1692697930_64e4854ae5f02c3412334.png!small)

更多命令语法请参照帮助信息。

# 练手题

知名渗透靶场HackTheBox上的一道入门题，与WinRM相关，可以尝试一下:

[Responder - HackTheBox Starting Point](https://app.hackthebox.com/starting-point)

# 后记

本文主要介绍了WinRM的基本信息，包括协议、原理等，以及通过WinRM进行横向渗透所需要掌握的一些基本的技巧。各位读者如果在阅读时有所疑问，欢迎在评论区提出，我会逐一进行回复。

