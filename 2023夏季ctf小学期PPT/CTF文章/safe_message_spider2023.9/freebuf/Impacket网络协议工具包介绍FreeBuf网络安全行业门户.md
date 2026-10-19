**[Impacket](https://www.coresecurity.com/corelabs-research/open-source-tools/impacket)是一个Python类库，用于对SMB1-3或IPv4 / IPv6
上的TCP、UDP、ICMP、IGMP，ARP，IPv4，IPv6，SMB，MSRPC，NTLM，Kerberos，WMI，LDAP等协议进行低级编程访问。
**

在本文的实验场景中，我们需要准备以下两个系统：

> 1.配置域控的Windows服务器；
>
> 2\. Kali Linux

系统相关设置如下：

### Windows Server

> 域: SERVER
>
> 用户: Administrator
>
> 密码: T00r
>
> IP地址: 192.168.1.140

 **Kali Linux:** 192.168.1.135

在正式开始使用Impacket工具之前，让我们先对目标Windows服务器执行Nmap版本扫描，以获取当前Windows Server上运行的有关服务信息。

    
    
    nmap -sV 192.168.1.140

![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294540177015.png!small)

正如你在上面的截图中看到的，目标系统当前运行的服务有域服务，Kerberos服务，Netbios服务，LDAP服务和Windows RPC服务。

现在让我们从GitHub安装Impacket工具。你可以在[这里](https://github.com/CoreSecurity/impacket.git)获取到。

首先，我们通过git clone命令克隆存储库，然后按以下截图所示安装Impacket。

    
    
    git clone https://github.com/CoreSecurity/impacket.git
    cd impacket/
    python setup.py install

![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294540326420.png!small)

这将在你的Kali Linux上安装Impacket。安装完成后，我们来查看下Impacket中都有哪些工具。

    
    
    cd impacket/examples

![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294540477091.png!small)

可以看到其中包含了许多的python脚本工具，让我们来尝试使用其中的一些工具：

###  **Ping.py**

一个简单的ICMP ping脚本，使用ICMP echo和echo-reply数据包检查主机状态。

    
    
    ./ping.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294540639307.png!small)**

 **语法: .** /ping.py [Source IP] [Destination IP]

    
    
    ./ping.py 192.168.1.135 192.168.1.140

以下是我从192.168.1.140（Windows Server）获得的ICMP响应

###
**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294540796583.png!small)**

###  **Lookupsid.py**

通过[MS-LSAT] MSRPC接口的Windows SID bruteforcer示例，旨在查找远程用户/组。

    
    
    ./lookupsid.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294540947547.png!small)**

 **语法:** ./lookupsid.py [[domain/] username [: password] @] [Target IP
Address]

    
    
    ./lookupsid.py SERVER/Administrator: T00r@192.168.1.140

如下所示，lookupsid.py已成功为我提取到了目标服务器的用户和组信息

###
**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294541141319.png!small)**

###  **Psexec.py**

Psexec.py允许你在远程Windows系统上执行进程，复制文件，并返回处理输出结果。此外，它还允许你直接使用完整的交互式控制台执行远程shell命令（不需要安装任何客户端软件）。

    
    
    ./psexec.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294541408156.png!small)**

 **语法:** ./psexec.py [[domain/] username [: password] @] [Target IP Address]

    
    
    ./psexec.py SERVER/Administrator: T00r@192.168.1.140

如下所示，我获取到了目标服务器的远程shell

###
**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294541647248.png!small)**

###  **Rpcdump.py**

该脚本将转储在目标上注册的RPC端点和字符串bindings列表。它也会尝试将它们与一些知名的端点进行匹配。

    
    
    ./rpcdump.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294542065547.png!small)**

 **语法:** ./rpcdump.py [[domain/] username [: password] @] [Target IP Address]

    
    
    ./rpcdump.py SERVER/Administrator: T00r@192.168.1.140

如下所示，我成功获取到了目标RPC列表

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294542296636.png!small)**

 **Samrdump.py**

与MSRPC套件中的安全帐户管理器远程接口通信的应用程序。它将为我们列出目标系统上的用户帐户，可用资源共享以及通过此服务导出的其他敏感信息

    
    
    ./samrdump.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294542575462.png!small)**

 **语法:** ./samrdump.py [[domain/] username [: password] @] [Target IP Address]

    
    
    ./samrdump.py SERVER/Administrator: T00r@192.168.1.140

如下所示，我从目标服务器提取了SAM信息

###
**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294542817882.png!small)**

###  **Sniff.py**

一个简单的数据包嗅探脚本。使用pcapy库来侦听通过指定接口传输的数据包

    
    
    . /sniff.py

选择正确的网卡，并开始嗅探

![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294543021216.png!small)

###  **Sniffer.py**

一个简单的数据包嗅探脚本，使用原始套接字来侦听与指定协议相对应的传输数据包。

    
    
    . /sniffer.py

sniffer开始监听icmp, tcp和udp数据包

![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294543306709.png!small)

###  **Wmiexec.py**

它会生成一个使用Windows Management
Instrumentation的半交互式shell，并以管理员身份运行。你不需要在目标服务器上安装任何的服务/代理，因此它非常的隐蔽。

    
    
    ./wmiexec.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294543514542.png!small)**

 **语法:** ./wmiexec.py [[domain/] username [: password] @] [Target IP Address]

    
    
    ./wmiexec.py SERVER/Administrator: T00r@192.168.1.140

如下所示，我获取到了目标服务器的shell

###
**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294543739329.png!small)**

###  **Wmiquery.py**

它允许发出WQL查询并获取目标系统WMI对象的描述信息。

    
    
    ./wmiquery.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294543989185.png!small)**

 **语法:** ./wmiquery.py [[domain/] username [: password] @] [Target IP Address]

    
    
    ./wmiquery.py SERVER/Administrator: T00r@192.168.1.140

这将打开一个shell，你可以在其中执行WQL查询

    
    
    SELECT * FROM Win32_LogicalDisk WHERE FreeSpace < 209152

###
**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294544245761.png!small)**

###  **Atexec.py**

通过Task Scheduler服务在目标系统上执行命令，并返回输出结果。

    
    
    ./atexec.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294544682770.png!small)**

 **语法:** /atexec.py [[domain/] username [: password] @] [Target IP Address]
[Command]

    
    
    ./atexec.py SERVER/Administrator: T00r@192.168.1.140 systeminfo

如下所示，我与目标服务器建立了远程连接，并执行了systeminfo命令，输出结果显示在了我的Kali终端上。

###
**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294544952995.png!small)**

###  **getArch.py**

该脚本将连接目标（或目标列表上的）计算机，并使用已记录的MSRPC特征收集由（ab）安装的操作系统架构类型。

    
    
    ./getArch.py

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294545584247.png!small)**

 **语法:** ./getArch.py -target [IP Address]

 **命令:** ./getArch.py -target 192.168.1.140

所下所示，目标系统架构为64-bit

###
**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294546144928.png!small)**

###  **Ifmap**

该脚本将绑定到目标的MGMT接口，以获取接口ID列表。它将在另一个接口UUID列表的顶部使用该列表，并报告该接口是否被列出和/或处于侦听状态。

**![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294546357129.png!small)**

 **语法:** ./ifmap.py [Host IP Address] [Port]

    
    
    ./ifmap.py 192.168.1.140 135
    ./ifmap.py 192.168.1.140 49154

![impacket网络协议工具包介绍](https://image.3001.net/images/20180620/15294546557217.png!small)

 ** *参考来源：[hackingarticles](http://www.hackingarticles.in/beginner-guide-to-impacket-tool-kit/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

