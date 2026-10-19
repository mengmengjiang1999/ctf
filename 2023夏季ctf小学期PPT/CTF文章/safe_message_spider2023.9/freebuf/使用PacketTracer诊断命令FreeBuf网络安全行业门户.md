## **目标**

> 第 1 部分：收集最终用户设备设置
>
> 第 2 部分：收集有关网络设备的信息
>
> 第 3 部分：诊断连接问题

##  **背景/场景**

在此Packet Tracer (PT) 活动中，我们将使用各种命令来收集设备信息，并解决设备配置和连接问题。设备信息包括 IP 地址、默认网关和 DNS
服务器设置。让设备进行网络上通信和连接到Internet ，这些设置至关重要。

## 第 1 部分：收集最终用户设备设置

### 第 1 步：记录HQ-Laptop-1的IP地址设置

![](https://image.3001.net/images/20230515/1684161791_646244ff7f5570d819469.png!small)首先在HQ集群中启动活动，如图所示，
**配线柜** 位于第一层的左下角，旁边是一个高大的黑色底盘。找到打印机 **FL-1P、HQ-Laptop-1、PC 1–1、1–2、1–3** 和
**1–4** ，以及第一层的所有其他设备。

    
    
    C:\>ipconfig
    
    Wireless0 Connection:(default port)
    
    Connection-specific DNS Suffix..:
    Link-local IPv6 Address.........: FE80::20A:F3FF:FEE4:EEAA
    IPv6 Address....................: ::
    IPv4 Address....................: 192.168.50.4
    Subnet Mask.....................: 255.255.255.0
    Default Gateway.................: ::
    192.168.50.1
    
    Bluetooth Connection:
    
    Connection-specific DNS Suffix..:
    Link-local IPv6 Address.........: ::
    IPv6 Address....................: ::
    IPv4 Address....................: 0.0.0.0
    Subnet Mask.....................: 0.0.0.0
    Default Gateway.................: ::
    0.0.0.0
    
    C:\>ipconfig /all
    
    Wireless0 Connection:(default port)
    
    Connection-specific DNS Suffix..:
    Physical Address................: 000A.F3E4.EEAA
    Link-local IPv6 Address.........: FE80::20A:F3FF:FEE4:EEAA
    IPv6 Address....................: ::
    IPv4 Address....................: 192.168.50.4
    Subnet Mask.....................: 255.255.255.0
    Default Gateway.................: ::
    192.168.50.1
    DHCP Servers....................: 192.168.50.1
    DHCPv6 IAID.....................:
    DHCPv6 Client DUID..............: 00-01-00-01-43-B9-1D-8A-00-0A-F3-E4-EE-AA
    DNS Servers.....................: ::
    10.2.0.125
    
    Bluetooth Connection:
    
    Connection-specific DNS Suffix..:
    Physical Address................: 00E0.A3A2.D8AA
    Link-local IPv6 Address.........: ::
    --More--
单击它以切换到 **桌面选项卡以查看有关** **HQ-Laptop-1** 的更多详细信息。然后，可以使用“` **ipconfig**`”然后“`
**ipconfig /all**`”命令打开命令提示符来获取网络的 IP 地址和其他详细信息。

### 第 2 步：记录 Net-Admin 的 IP 地址设置

转到 **配线柜** 并选择 **Net-Admin** 选项开始。从那里选择桌面选项卡，然后查找 **命令提示符** 选项。打开后使用“`
**ipconfig
/all**`”命令获取我们需要的信息。在这个命令呈现的网络连接的详细信息中、你的IP地址、子网掩码、默认网关都显示出来了。这种方法可以快速并简单地拍摄网络设置快照。

    
    
    C:\>ipconfig /all
    
    FastEthernet0 Connection:(default port)
    
       Connection-specific DNS Suffix..: 
       Physical Address................: 0001.C910.22D6
       Link-local IPv6 Address.........: FE80::201:C9FF:FE10:22D6
       IPv6 Address....................: ::
       IPv4 Address....................: 192.168.99.9
       Subnet Mask.....................: 255.255.255.0
       Default Gateway.................: ::
                                         192.168.99.1
       DHCP Servers....................: 0.0.0.0
       DHCPv6 IAID.....................: 
       DHCPv6 Client DUID..............: 00-01-00-01-67-A3-E9-BD-00-01-C9-10-22-D6
       DNS Servers.....................: ::
                                         10.2.0.125
    
    Bluetooth Connection:
    
       Connection-specific DNS Suffix..: 
       Physical Address................: 0001.649E.81BB
       Link-local IPv6 Address.........: ::
     --More--
## 第 2 部分：收集有关网络设备的信息

### 第 1 步：收集有关 HQ 和 ISP之间链路的网络连接信息

访问 **配线柜** 左侧机架并导航至 **HQ-Edge > CLI**选项卡。输入多个命令，包括“ `**enable**`”、“ `**show ip
route | begin Gateway**`”、“ `**show running-config | begin ip route**`”、“
`**show cdp neighbors detail**`”、` **ping 10.0.0.49**`“ ”和“ `**show
arp**`”。完成后，退出配线柜。

    
    
    HQ-Edge>enable
    HQ-Edge#show ip route | begin Gateway
    Gateway of last resort is 0.0.0.0 to network 0.0.0.0
    
         10.0.0.0/8 is variably subnetted, 6 subnets, 4 masks
    O       10.0.0.0/29 [110/2] via 10.0.0.49, 00:17:04, GigabitEthernet0/0/0
    O       10.0.0.32/29 [110/2] via 10.0.0.49, 00:17:04, GigabitEthernet0/0/0
    C       10.0.0.48/29 is directly connected, GigabitEthernet0/0/0
    L       10.0.0.50/32 is directly connected, GigabitEthernet0/0/0
    O       10.0.3.0/24 [110/3] via 10.0.0.49, 00:17:04, GigabitEthernet0/0/0
    O       10.2.0.0/16 [110/2] via 10.0.0.49, 00:17:04, GigabitEthernet0/0/0
         192.168.10.0/24 is variably subnetted, 2 subnets, 2 masks
    C       192.168.10.0/24 is directly connected, GigabitEthernet0/0/1.10
    L       192.168.10.1/32 is directly connected, GigabitEthernet0/0/1.10
         192.168.20.0/24 is variably subnetted, 2 subnets, 2 masks
    C       192.168.20.0/24 is directly connected, GigabitEthernet0/0/1.20
    L       192.168.20.1/32 is directly connected, GigabitEthernet0/0/1.20
         192.168.30.0/24 is variably subnetted, 2 subnets, 2 masks
    C       192.168.30.0/24 is directly connected, GigabitEthernet0/0/1.30
    L       192.168.30.1/32 is directly connected, GigabitEthernet0/0/1.30
         192.168.50.0/24 is variably subnetted, 2 subnets, 2 masks
    C       192.168.50.0/24 is directly connected, GigabitEthernet0/0/1.50
    L       192.168.50.1/32 is directly connected, GigabitEthernet0/0/1.50
         192.168.75.0/24 is variably subnetted, 2 subnets, 2 masks
    C       192.168.75.0/24 is directly connected, GigabitEthernet0/0/1.75
    L       192.168.75.1/32 is directly connected, GigabitEthernet0/0/1.75
         192.168.99.0/24 is variably subnetted, 2 subnets, 2 masks
    C       192.168.99.0/24 is directly connected, GigabitEthernet0/0/1.99
    L       192.168.99.1/32 is directly connected, GigabitEthernet0/0/1.99
    S*   0.0.0.0/0 is directly connected, GigabitEthernet0/0/0
    HQ-Edge#show cdp neighbors detail
    
    Device ID: ISP
    Entry address(es): 
      IP address : 10.0.0.49
    Platform: cisco PT1000, Capabilities: Router
    Interface: GigabitEthernet0/0/0, Port ID (outgoing port): GigabitEthernet1/0
    Holdtime: 165
    
    Version :
    Cisco Internetwork Operating System Software
    IOS (tm) PT1000 Software (PT1000-I-M), Version 12.2(28), RELEASE SOFTWARE (fc5)
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2005 by cisco Systems, Inc.
    Compiled Wed 27-Apr-04 19:01 by miwang
    
    advertisement version: 2
    Duplex: full
    
    HQ-Edge#ping 10.0.0.49 
    
    Type escape sequence to abort.
    Sending 5, 100-byte ICMP Echos to 10.0.0.49, timeout is 2 seconds:
    !!!!!
    Success rate is 100 percent (5/5), round-trip min/avg/max = 0/0/0 ms
    
    HQ-Edge#show arp
    Protocol  Address          Age (min)  Hardware Addr   Type   Interface
    Internet  10.0.0.49               17  0060.2FE1.903B  ARPA   GigabitEthernet0/0/0
    Internet  10.0.0.50               -   0000.0C99.CB04  ARPA   GigabitEthernet0/0/0

### 第 2 步：收集总部设备的网络连接信息

 **在1–1** 、 **1–2 、 1–3** 、 **1–4** 、 **FL-1P** 和 **HQ-Laptop-1** 上使用 ipconfig
命令查找它们的 **IPv4** 地址和 **默认网关** 。

    
    
    C:\>ipconfig
    
    FastEthernet0 Connection:(default port)
    
       Connection-specific DNS Suffix..: 
       Link-local IPv6 Address.........: FE80::201:C7FF:FE54:EB5
       IPv6 Address....................: ::
       IPv4 Address....................: 192.168.10.3
       Subnet Mask.....................: 255.255.255.0
       Default Gateway.................: ::
                                         192.168.10.1
    
    Bluetooth Connection:
    
       Connection-specific DNS Suffix..: 
       Link-local IPv6 Address.........: ::
       IPv6 Address....................: ::
       IPv4 Address....................: 0.0.0.0
       Subnet Mask.....................: 0.0.0.0
       Default Gateway.................: ::
                                         0.0.0.0
    
    C:\>arp -a
    No ARP Entries Found

然后，在 **1–1** **上** **，** 使用 **命令提示符** 输入“`**arp -a**`”命令并 ping **1-2、1-3、1-4**
、 **FL-1P** 和 **HQ-Laptop-1** 。最后，输入“` **tracert 10.2.0.125**`”命令来查找数据包到达 DNS
服务器所采用的路由。

    
    
    C:\>ping 192.168.10.7
    
    Pinging 192.168.10.7 with 32 bytes of data:
    
    Ping statistics for 192.168.10.7:
        Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
    
    C:\>ping 192.168.20.5
    
    Pinging 192.168.20.5 with 32 bytes of data:
    
    Reply from 192.168.20.5: bytes=32 time<1ms TTL=127
    Reply from 192.168.20.5: bytes=32 time<1ms TTL=127
    Reply from 192.168.20.5: bytes=32 time=1ms TTL=127
    
    Ping statistics for 192.168.20.5:
        Packets: Sent = 4, Received = 3, Lost = 1 (25% loss),
    Approximate round trip times in milli-seconds:
        Minimum = 0ms, Maximum = 1ms, Average = 0ms
    
    C:\>ping 192.168.20.6
    
    Pinging 192.168.20.6 with 32 bytes of data:
    
    Ping statistics for 192.168.20.6:
        Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
    
    C:\>ping 192.168.50.3
    
    Pinging 192.168.50.3 with 32 bytes of data:
    
    Reply from 192.168.50.3: bytes=32 time=1ms TTL=127
    Reply from 192.168.50.3: bytes=32 time=13ms TTL=127
    Reply from 192.168.50.3: bytes=32 time=13ms TTL=127
    
    Ping statistics for 192.168.50.3:
        Packets: Sent = 4, Received = 3, Lost = 1 (25% loss),
    Approximate round trip times in milli-seconds:
        Minimum = 1ms, Maximum = 13ms, Average = 9ms
    
    C:\>ping 192.168.50.4
    
    Pinging 192.168.50.4 with 32 bytes of data:
    
    Reply from 192.168.50.4: bytes=32 time=14ms TTL=127
    Reply from 192.168.50.4: bytes=32 time=18ms TTL=127
    Reply from 192.168.50.4: bytes=32 time=11ms TTL=127
    
    Ping statistics for 192.168.50.4:
        Packets: Sent = 4, Received = 3, Lost = 1 (25% loss),
    Approximate round trip times in milli-seconds:
        Minimum = 11ms, Maximum = 18ms, Average = 14ms
    
    C:\>arp -a
      Internet Address      Physical Address      Type
      192.168.10.1          000a.41ea.6b47        dynamic
    
    C:\>tracert 10.2.0.125
    
    Tracing route to 10.2.0.125 over a maximum of 30 hops: 
    
      1   0 ms      0 ms      0 ms      192.168.10.1
      2   0 ms      0 ms      0 ms      10.0.0.49
      3   *         0 ms      0 ms      10.2.0.125
    
    Trace complete.

## 第 3 部分：诊断连接问题

我们将使用包括 **nslookup** 、ping故障排除和 **netstat** 在内的诊断命令和技术来排除DNS、Web
访问故障，并可以发现目标设备上的侦听端口。

### 第 1 步：测试 URL 以调查连接问题

首先关闭 **PC 1–1** 上的 **命令提示符** 。打开 Web **浏览器**
并在地址栏中键入“`**test.ptsecurity.com**`”，然后键入 IP 地址“` **192.168.75.2**`”。

![](https://image.3001.net/images/20230515/1684162178_64624682e08d07fa37cbb.png!small)

### 第 2 步：使用nslookup命令验证DNS服务

 **在命令提示符** 中使用 ping 和“ `**nslookup**`”命令检查网站连接。“`
**nslookup**`”命令允许使用备用DNS服务器。要了解有关“`**nslookup**`”命令及其变体的更多信息，请在命令提示符窗口中运行“`
**nslookup /?**`”。在命令提示符下使用“` **nslookup test.ptsecurity.com
192.168.99.3**`”以使用特定的 DNS 服务器。请注意，加载 Packet Tracer可能需要几秒钟。

    
    
    C:\>ping test.ptsecurity.com
    Ping request could not find host test.ptsecurity.com. Please check the name and try again.
    C:\>nslookup test.ptsecurity.com
    
    Server: [10.2.0.125]
    Address:  10.2.0.125
    *** UnKnown can't find test.ptsecurity.com: Non-existent domain.
    
    C:\>nslookup
    
    Server: [10.2.0.125]
    Address:  10.2.0.125
    
    >nslookup /?
    Unrecognized command:   nslookup /?    :- enter a valid server ip address
    
    >exit
    
    C:\>nslookup test.ptsecurity.com 192.168.99.3
    
    Server: [192.168.99.3]
    Address:  192.168.99.3
    DNS request timed out.
     timeout was 15000 milli seconds.
    
    Server: [192.168.99.3]
    Address:  192.168.99.3
    
    Non-authoritative answer:
    Name:   test.ptsecurity.com
    Address:   192.168.75.2

### 第 3 步：使用 ping 命令的输出来诊断连接问题

首先是命令提示符中的“ `**ping mail.cybercloud.com**`”和“ `**www.ptsecurity.com**` **” 。**

    
    
    C:\>ping mail.cybercloud.com
    
    Pinging 172.19.0.4 with 32 bytes of data:
    
    Ping statistics for 172.19.0.4:
        Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
    
    C:\>ping www.ptsecurity.com
    
    Pinging 10.0.0.3 with 32 bytes of data:
    
    Reply from 10.0.0.3: Destination host unreachable.
    Reply from 10.0.0.3: Destination host unreachable.
    
    Ping statistics for 10.0.0.3:
        Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),

然后打开 **Web 浏览器** 并导航到“ `**www.ptsecurity.com**` **”。**

![](https://image.3001.net/images/20230515/1684162353_6462473113f5e6cecb368.png!small)

### 第 4 步：使用netstat命令查找活动端口和侦听端口

打开命令提示符并转到 HQ 的配线柜。在 PC 1-1 和 FTP 服务器上使用“` **netstat**`”命令。

    
    
    C:\>netstat
    
    Active Connections
    
      Proto  Local Address          Foreign Address        State
      TCP    0.0.0.0:25             0.0.0.0:0              CLOSED
      TCP    0.0.0.0:110            0.0.0.0:0              CLOSED
      TCP    0.0.0.0:8443           0.0.0.0:0              CLOSED
    C:\>netstat bob
    Invalid Command.
    
    C:\>ipconfig
    
    FastEthernet0 Connection:(default port)
    
       Connection-specific DNS Suffix..: 
       Link-local IPv6 Address.........: FE80::290:21FF:FE64:E9B9
       IPv6 Address....................: ::
       IPv4 Address....................: 192.168.75.2
       Subnet Mask.....................: 255.255.255.0
       Default Gateway.................: ::
                                         192.168.75.1
    C:\>netstat
    
    Active Connections
    
      Proto  Local Address          Foreign Address        State
      TCP    0.0.0.0:25             0.0.0.0:0              CLOSED
      TCP    0.0.0.0:110            0.0.0.0:0              CLOSED
      TCP    0.0.0.0:8443           0.0.0.0:0              CLOSED
      TCP    192.168.75.2:21        192.168.10.3:1027      ESTABLISHED
    
    C:\>netstat
    
    Active Connections
    
      Proto  Local Address          Foreign Address        State
      TCP    0.0.0.0:25             0.0.0.0:0              CLOSED
      TCP    0.0.0.0:110            0.0.0.0:0              CLOSED
      TCP    0.0.0.0:8443           0.0.0.0:0              CLOSED
      TCP    192.168.75.2:21        192.168.10.3:1027      CLOSED

关闭命令提示符并打开 Web 浏览器，导航到“ `**192.168.75.2**`”。检查FTP 服务器上的“` **netstat**`”命令。

![](https://image.3001.net/images/20230515/1684162437_646247855a6b20e67c1e4.png!small)以上就是使用Packet
Tracer诊断命令的全部内容。

## 来源

> https://systemweakness.com/using-packet-tracer-to-diagnostic-> commands-6183986945d2

