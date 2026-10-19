**自Windows
XP开始，Windows中就内置网络端口转发的功能。任何传入到本地端口的TCP连接（IPv4或IPv6）都可以被重定向到另一个本地端口，或远程计算机上的端口，并且系统不需要有一个专门用于侦听该端口的服务。**

在Linux中，使用iptables可以非常轻松地配置端口重定向。在Windows Server系统上，路由和远程访问服务（RRAS）通过使用虚拟专用网络
(VPN)
或拨号连接支持远程用户或站点到站点连接，但这种方式相对较为麻烦。其实，除此之外还有一种更为简单的方法可以帮助我们在Windows中实现端口转发，即我们可以使用命令Netsh的Portproxy模式配置Windows中的端口转发。该命令的语法如下：

    
    
    netsh interface portproxy add v4tov4 listenaddress=localaddress listenport=localport connectaddress=destaddress connectport=destport
    

> listenaddress - 等待连接的本地IP地址。
>
> listenport - 本地侦听TCP端口。
>
> connectaddress - 将传入连接重定向到本地或远程IP地址（或DNS名称）。

connectport -一个TCP端口，来自listenport的连接会被转发到该端口。假设当前我们的RDP服务端口在一个非标准端口上进行响应，如3340（端口可以在服务设置中更改）。为此，我们需要将传入流量从TCP端口3340重定向到另一个本地端口
- 3389（即标准rdp端口）。

我们以管理员身份启动命令提示符并执行以下命令：

    
    
    netsh interface portproxy add v4tov4 listenport=3340 listenaddress=10.1.1.110 connectport=3389 connectaddress=10.1.1.110
    

![](https://image.3001.net/images/20180708/1531006509801.jpg!small)

10.10.1.110 - 计算机的当前IP地址。

使用netstat确保3340端口当前处于被侦听状态：

    
    
    netstat -ano | findstr :3340
    

**![](https://image.3001.net/images/20180708/15310065226636.jpg!small)**

**注意** ：如果该命令未返回任何内容并且通过netsh interface portproxy进行端口转发不成功，则请确保iphlpsvc（IP
Helper）服务当前已在你的系统上运行。

![](https://image.3001.net/images/20180708/15310065374366.jpg!small)

必须在为其创建端口转发规则的网络接口上启用IPv6支持。

![](https://image.3001.net/images/20180708/15310065516612.jpg!small)

以上条件必须满足，如果没有IP Helper服务且未启用IPv6支持，则端口重定向将不起作用。

你可以使用其PID找出正在侦听此端口的进程（在我们的示例中PID为636）：

    
    
    tasklist | findstr 636
    

让我们使用任意的RDP客户端尝试从远程系统连接到此计算机。指定RDP端口3340，在RDP服务器地址后以冒号分隔，例如10.10.1.110:3340

![](https://image.3001.net/images/20180708/15310065694212.png!small)

如果不出问题的话，连接应该会被成功建立。

 **重要：** 请确保防火墙（Windows防火墙或通常包含在杀毒软件中的第三方防火墙）允许到新端口的传入连接。
如有必要，可以使用以下命令添加新的Windows防火墙规则：

    
    
    netsh advfirewall firewall add rule name=”forwarded_RDPport_3340” protocol=TCP dir=in localip=10.1.1.110  localport=3340 action=allow
    

你可以创建任意数量的Windows端口转发规则。所有netsh interface
portproxy规则都是持久性的，并会在Windows系统重启后被保存。

显示系统中的转发规则列表：

    
    
    netsh interface portproxy show all
    

在我们的例子中，只有一个转发规则即从3340到3389端口的转发：

    
    
    Listen on ipv4:             Connect to ipv4:
    Address         Port        Address         Port
    --------------- ----------  --------------- ----------    10.1.1.110     3340        10.1.1.110     3389
    

**![](https://image.3001.net/images/20180708/15310065925309.jpg!small)**

**Tip：** 此外，portproxy设置可以通过以下命令查看：

    
    
    netsh interface portproxy dump
    #========================
    # Port Proxy configuration
    #========================
    pushd interface portproxy
    reset
    add v4tov4 listenport=3340 connectaddress=10.1.1.110 connectport=3389
    popd
    # End of Port Proxy configuration
    

![](https://image.3001.net/images/20180708/15310066104113.jpg!small)

删除指定的端口转发规则：

    
    
    netsh interface portproxy delete v4tov4 listenport=3340 listenaddress=10.1.1.110
    

清除所有当前的端口转发规则：

    
    
    netsh interface portproxy reset
    

**重要：** 以上端口转发仅适用于TCP端口，对于UDP端口将不起作用，并且不能使用127.0.0.1作为连接地址。

如果要将传入的TCP连接转发至另一台计算机，则命令如下：

    
    
    netsh interface portproxy add v4tov4 listenport=3389 listenaddress=0.0.0.0 connectport=3389 connectaddress=192.168.100.101
    

此规则将所有传入的RDP请求（到3389端口）从此计算机重定向到IP地址为192.168.1.101的远程计算机上。

portproxy的另一个特性就是可以让它看起来像任意的远程网络服务在本地运行。

例如，将连接从本地端口5555转发至远程地址157.166.226.25（CNN网站）：

    
    
    netsh interface portproxy add v4tov4 listenport=5555 connectport=80 connectaddress= 157.166.226.25 protocol=tcp
    

现在，如果你在浏览器中访问<http://localhost:5555/>，则将打开CNN网站的主页。因此，尽管浏览器对本地计算机进行了寻址，但它仍会打开一个远程页面。

![](https://image.3001.net/images/20180708/15310066358174.jpg!small)

端口转发还可用于将端口从网卡的外部地址，转发到在同一计算机上运行的虚拟机端口。

此外，在Windows Server 2012 R2中情况可能会有所不同。在Windows Server 2012
R2中，端口转发规则仅在系统重启之前有效，并且在重启后它们会被重置。出现这种病情况，你需要检查网络接口上是否存在定期断开连接，以及操作系统引导时IP地址是否发生更改（最好使用静态IP地址）。作为一种解决方案，我会添加一个使用netsh
interface portproxy规则的脚本到Windows scheduler，以在系统启动时运行。

在Windows Server
2003/XP中，必须在注册表项HKLM\SYSTEM\ControlSet001\Services\Tcpip\Parameters中另外将IPEnableRouter参数设置为1。

 ***参考来源：[woshub](http://woshub.com/port-forwarding-in-windows/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

