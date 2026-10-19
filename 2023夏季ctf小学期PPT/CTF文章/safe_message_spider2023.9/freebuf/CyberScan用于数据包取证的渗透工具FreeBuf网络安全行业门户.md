**CyberScan是一个开源的数据包取证渗透工具，可用于数据包的分析，解码，扫描端口，pinging以及获取IP的地理定位包括（纬度，经度，地区，国家等）。**

##  **截图**

![demo.png](https://image.3001.net/images/20190512/1557629282_5cd7896202dce.png!small)

##  **支持的操作系统**

> Windows XP/7/8/8.1/10
>
> GNU/Linux
>
> MacOSX

##  **安装**

你可以通过克隆Git存储库下载CyberScan：

    
    
    git clone https://github.com/medbenali/CyberScan.git
    cd CyberScan/
    python CyberScan.py -v

CyberScan支持Python版本2.6.x和2.7.x开箱即用。

## CyberScan 模块使用

CyberScan能够发送和捕获多个协议的数据包，伪造并对它们进行解码以用于大多数网络任务，如扫描，ping，探测和攻击。

请确保你的机器已安装了CyberScan：

    
    
    $ git clone https://github.com/medbenali/CyberScan.git

查看帮助选项：

    
    
    $ CyberScan -h

## Pinging 网络

CyberScan支持使用多种协议执行ping操作，在本地以太网上发现主机的最快方法是使用ARP：

 **ARP Ping**

    
    
    $ CyberScan -s 192.168.1.0/24 -p arp
    [*] Starting Ping ARP for 192.168.1.0/24
    Begin emission:
    Finished to send 256 packets.
    
    Received 0 packets, got 0 answers, remaining 256 packets

 **ICMP Ping**

在其他情况下，我们可以使用ICMP ping：

    
    
    $ CyberScan -s 192.168.1.1-254 -p icmp
    [*] Starting Ping ARP for 192.168.1.0/24
    Begin emission:
    Finished to send 256 packets.
    
    Received 0 packets, got 0 answers, remaining 256 packets

 **TCP Ping**

在ICMP回应请求被阻止的情况下，我们仍然可以使用TCP：

    
    
    $ CyberScan -s 192.168.1.1-254 -p tcp -d 80

 **UDP Ping**

甚至UDP（从实时主机产生ICMP端口不可达错误）。我们可以选择任何最有可能关闭的端口，例如端口0：

    
    
    $ CyberScan -s 192.168.*.1-10 -p udp

## 网络扫描

 **端口扫描器**

在CyberSan Tool中，我们可以指定/不指定开始和结束端口进行扫描

    
    
    $ CyberScan -s 192.168.1.1 -p scan -d 1 -t 100
    WARNING: No route found for IPv6 destination :: (no default route?)
    [*] CyberScan Port Scanner
    [*] Scanning 192.168.1.1 From Port 1 To 100: 
    [*] Starting CyberScan 1.01 at 2017-07-14 14:00 CEST
    [*] Scan In Progress ...
    [*] Connecting To Port :  100 
    [*] Scanning Completed at 2017-07-14 14:00 CEST
    [*] CyberScan done: 1IP address (1host up) scanned in 0.32 seconds
    [*] Open Ports: 
      23 TELNET: Open
      53 DNS: Open
      80 HTTP: Open
    
    
    $ CyberScan -s 8.8.8.8 -p scan
    WARNING: No route found for IPv6 destination :: (no default route?)
    [*] CyberScan Port Scanner
    [*] Scanning For Most Common Ports On 8.8.8.8
    [*] Starting CyberScan 1.01 at 2017-07-14 14:03 CEST
    [*] Scan In Progress ...
    [*] Connecting To Port :  10000 109 110 123 137 138 139 143 156 2082 2083 2086 2087 21 22 23 25 3306 389 546 547 69 80 8443 993 995 
    [*] Scanning Completed at 2017-07-14 14:03 CEST
    [*] CyberScan done: 1IP address (1host up) scanned in 13.11 seconds
    [*] Open Ports: 
      53 DNS: Open
      443 HTTPS: Open

##  **地理定位 IP**

    
    
    $ CyberScan -s 72.229.28.185 -p geoip
    WARNING: No route found for IPv6 destination :: (no default route?)
    [*] IP Address:  72.229.28.185
    [*] City:  New York
    [*] Region Code:  NY
    [*] Area Code:  212
    [*] Time Zone:  America/New_York
    [*] Dma Code:  501
    [*] Metro Code:  New York, NY
    [*] Latitude:  40.7605
    [*] Longitude:  -73.9933
    [*] Zip Code:  10036
    [*] Country Name:  United States
    [*] Country Code:  US
    [*] Country Code3:  USA
    [*] Continent:  NA

## 分析和解码数据包

Cyberscan可以分析PCAP文件提取和解码以太网、IP、TCP、ICMP、UDP包头。

 **以太网包头**

    
    
    $ CyberScan -f test.pcap -p eth
    WARNING: No route found for IPv6 destination :: (no default route?)
    ----------------------------------------    [*] Packet : 1
    [+] ### [ Ethernet ] ###
    [*] Mac Destination : 00:1f:f3:3c:e1:13
    [*] Mac Source : f8:1e:df:e5:84:3a
    [*] Ethernet Type : 2048

 **IP 包头**

    
    
    $ CyberScan -f test.pcap -p ip
    WARNING: No route found for IPv6 destination :: (no default route?)
    ----------------------------------------    [*] Packet : 1
    [+] ###[ IP ] ###
    [*] IP Source : 172.16.11.12
    [*] IP Destination : 74.125.19.17
    [*] IP Version :  4
    [*] IP Ihl :  5
    [*] IP Tos :  0
    [*] IP Len :  79
    [*] IP Id :  56915
    [*] IP Flags :  2
    [*] IP Frag :  0
    [*] IP Ttl :  64
    [*] IP Protocol :  6
    [*] IP Chksum :  18347
    [*] IP Options :  []
    [*] IP Dump : 
    0000   45 00 00 4F DE 53 40 00  40 06 47 AB AC 10 0B 0C   E..O.S@.@.G.....
    0010   4A 7D 13 11 FC 35 01 BB  C6 D9 14 D0 C5 1E 2D BF   J}...5........-.
    0020   80 18 FF FF CB 8C 00 00  01 01 08 0A 1A 7D 84 2C   .............}.,
    0030   37 C5 58 B0 15 03 01 00  16 43 1A 88 1E FA 7A BC   7.X......C....z.
    0040   22 6E E6 32 7A 53 47 00  A7 5D CC 64 EA 8E 92      "n.2zSG..].d...

 **TCP 包头**

    
    
    $ CyberScan -f test.pcap -p tcp
    WARNING: No route found for IPv6 destination :: (no default route?)
    ----------------------------------------    [*] Packet : 1
    [+] ###[ TCP ] ###
    [*] TCP Source Port :  64565
    [*] TCP Destination Port :  443
    [*] TCP Seq :  3336115408
    [*] TCP Ack :  3307089343
    [*] TCP Dataofs :  8
    [*] TCP Reserved :  0
    [*] TCP Flags :  24
    [*] TCP Window :  65535
    [*] TCP Chksum :  52108
    [*] TCP Urgptr :  0
    [*] TCP Options :  [('NOP', None), ('NOP', None), ('Timestamp', (444433452, 935680176))]
    [*] TCP Dump : 
    0000   FC 35 01 BB C6 D9 14 D0  C5 1E 2D BF 80 18 FF FF   .5........-.....
    0010   CB 8C 00 00 01 01 08 0A  1A 7D 84 2C 37 C5 58 B0   .........}.,7.X.

 **UDP 包头**

    
    
    $ CyberScan -f test.pcap -p udp
    WARNING: No route found for IPv6 destination :: (no default route?)
    ----------------------------------------    [*] Packet : 1
    [+] ###[ UDP ] ###
    [*] UDP Source Port :  54639
    [*] UDP Destination Port :  53
    [*] UDP Len :  47
    [*] UDP Chksum :  30084
    [*] UDP Dump : 
    0000   D5 6F 00 35 00 2F 75 84  13 A2 01 00 00 01 00 00   .o.5./u.........
    0010   00 00 00 00 04 65 38 37  32 01 67 0A 61 6B 61 6D   .....e872.g.akam
    0020   61 69 65 64 67 65 03 6E  65 74 00 00 01 00 01      aiedge.net.....

 **ICMP 包头**

    
    
    $ CyberScan -f test.pcap -p icmp
    WARNING: No route found for IPv6 destination :: (no default route?)
    ----------------------------------------    [*] Packet : 1
    [+] ###[ ICMP ] ###
    [*] ICMP Type :  3
    [*] ICMP Code :  3
    [*] ICMP Chksum :  5296
    [*] ICMP Id :  None
    [*] ICMP Seq :  None
    [*] ICMP Dump : 
    0000   03 03 14 B0 00 00 00 00  45 00 00 43 C1 80 00 00   ........E..C....
    0010   40 11 4A FC AC 10 0B 01  AC 10 0B 0C 00 35 E7 E8   @.J..........5..
    0020   00 2F 00 00                                        ./..

***参考来源：[GitHub](https://github.com/medbenali/cyberscan)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

