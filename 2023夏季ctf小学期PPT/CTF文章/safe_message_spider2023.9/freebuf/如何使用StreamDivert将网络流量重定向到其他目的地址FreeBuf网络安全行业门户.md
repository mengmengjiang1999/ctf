![](https://image.3001.net/images/20211108/1636355303_6188cce7df62b66647670.jpg!small)  

## 关于StreamDivert

StreamDivert是一款中间人工具和网络流量转发工具，该工具可以针对目标系统中的进出网络流量执行分析和重定向操作，并且能够将TCP、UDP和ICMP流量转发至其他的目标地址。比如说，StreamDivert可以将所有传入的SMB连接转发到另一台服务器的445端口上，或者仅将指定传入的SMB连接从给定的源IP地址集转发至其他服务器。

## StreamDivert功能介绍

  * 将所有到特定端口的传入连接中继到另一个目标；
  * 将从特定源IP到端口的传入连接中继到另一个目标；
  * 将传入连接中继到SOCKS（4/5）服务器；
  * 将所有到特定端口的传出连接中继到另一个目标；
  * 将传出连接中继到特定IP和端口的另一个目标上；
  * 通过IPv4和IPv6处理TCP、UDP和ICMP流量；
  * 强制通过特定网络接口重定向数据包；

## 工具下载&安装

广大研究人员可以访问该项目的【[
_Releases页面_](https://github.com/jellever/StreamDivert/releases)】下载并获取StreamDivert的最新版本预编译源码。

或者，也可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/jellever/StreamDivert.git

## 工具使用

我们可以直接以管理员权限并运行下列命令来执行StreamDivert：

    
    
    streamdivert.exe config_file [-f] [-v]

StreamDivert所提供的配置文件中包含了我们需要处理和分流的条目信息，下面给出的是config配置文件的参考样例：

    
    
    //Divert all inbound TCP connections to port 445 (SMB) coming from 10.0.1.50 to 10.0.1.49 port 445
    
    tcp < 445 10.0.1.50 -> 10.0.1.49 445
    
     
    
    //Divert all inbound TCP connections to port 445 (SMB) coming from 10.0.1.51 to a local SOCKS server
    
    tcp < 445 10.0.1.51 -> socks
    
     
    
    //Divert all inbound TCP connections to port 445 (SMB) coming from fe80::f477:846a:775d:d37 to fe80::20c:29ff:fe6f:88ff port 445
    
    tcp < 445 fe80::f477:846a:775d:d37 -> fe80::20c:29ff:fe6f:88ff 445
    
     
    
    //Divert all inbound TCP connections to port 445 (SMB) to 10.0.1.48 port 445
    
    tcp < 445 0.0.0.0 -> 10.0.1.48 445
    
     
    
    //Divert all inbound UDP connections to to port 53 (DNS) to  10.0.1.49 port 53
    
    udp < 53 0.0.0.0 -> 10.0.1.49 53
    
     
    
    //Divert all inbound ICMP packets coming from 10.0.1.50 to 10.0.1.49
    
    icmp < 10.0.1.50 -> 10.0.1.49
    
     
    
    //Divert all outbound TCP connections to 10.0.1.50, port 80 to 10.0.1.49 port 8080
    
    tcp > 10.0.1.50 80 -> 10.0.1.49 8080
    
     
    
    //Send all packets going to 10.0.1.50 port 80 and prefer interface 9 to send them. If the interface does not exist or is not up, the packets are send from the default interface.
    
    tcp > 10.0.1.50 80 -> 10.0.1.50 80 interface 9
    
     
    
    //Force all packets going to 10.0.1.50 port 80 over interface 9, or drop the packets if the interface does not exist or is not up.
    
    tcp > 10.0.1.50 80 -> 10.0.1.50 80 force interface 9
    
     
    
    //Divert all outbound UDP connection to port 53 (DNS) to 10.0.1.49 port 53
    
    udp > 0.0.0.0 53 -> 10.0.1.49 53

其中的[f]参数将会修改Windows防火墙，并将某个应用程序设置为例外，以正确地将传入流量重定向到另一个端口。[-v]参数可以控制日志记录的详细程度。如果提供，StreamDivert将记录有关重定向数据包和数据流的详细信息。

## StreamDivert使用场景

  * 将出站C&C流量转移到本地Socket以进行动态恶意软件分析；
  * 将受感染主机的所有入站SMB连接转发至Responder/ ntlmrelayx（在渗透测试中很有用）；
  * 通过保留端口路由流量，当网络防火墙介于两者之间时有用。比如说，通过端口445路由Meterpreter Shell流量，或通过端口3389运行一台SOCKS服务器等等；

## 项目地址

 **StreamDivert：** 【[ _GitHub传送门_](https://github.com/jellever/StreamDivert)】

## 参考资料

  * [ _https://github.com/jellever/StreamDivert/releases_](https://github.com/jellever/StreamDivert/releases)

