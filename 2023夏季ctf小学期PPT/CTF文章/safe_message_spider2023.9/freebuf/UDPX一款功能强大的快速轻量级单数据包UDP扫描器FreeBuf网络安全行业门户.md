![](https://image.3001.net/images/20230517/1684258591_6463bf1f4f3d5f2401910.png!small)

## 关于UDPX

UDPX是一款功能强大的快速轻量级单数据包UDP扫描器，该工具基于Go语言开发，支持扫描和发现超过45种网络服务，并且支持添加自定义的扫描服务类型。该工具易于使用，是一款轻量级的工具，支持在Windows、Linux和macOS操作系统上运行。

## 工具特性

> 1、运行速度快，支持在20秒内扫描整个/16网络并识别单个服务；
>
> 2、不需要安装libpcap或其他任何依赖组件；
>
> 3、支持在Linux、macOS和Windows操作系统上运行；
>
> 4、支持自定义配置和开发，我们可以添加更多的探针或测试更多的协议；
>
> 5、支持以JSONL格式存储扫描结果；
>
> 6、支持扫描域名；

## 工具运行机制

扫描UDP端口与扫描TCP有很大的区别，由于UDP是一种无连接协议，因此我们不一定能够从探测UDP端口中得到任何结果。UDPX实现了一种基于单个数据包的方法，特定于协议的数据包被发送到定义的服务（端口）并等待响应。默认情况下，限制设置为500毫秒，可以通过-w参数进行更改。如果服务在这段时间内发送回一个数据包，那么可以肯定的是，它确实在侦听该端口，并且被报告为端口打开状态。

一种典型的技术是向目标机器上的每个端口发送0字节的UDP数据包。如果我们收到“ICMP端口无法访问”消息，则该端口将关闭。如果接收到对探测器的UDP响应（异常），则端口处于打开状态。如果我们根本没有得到响应，则状态为打开或已筛选，这意味着端口打开或数据包筛选器正在阻止通信。

## 支持的服务

UDPX支持扫描超过45种服务，下面给出的是服务列表：

> ipmi
>
> snmp
>
> ike
>
> tftp
>
> openvpn
>
> kerberos
>
> ldap
>
> ard
>
> bacnet
>
> bacnet_rpm
>
> chargen
>
> citrix
>
> coap
>
> db
>
> db
>
> digi1
>
> digi2
>
> digi3
>
> dns
>
> ipmi
>
> ldap
>
> mdns
>
> memcache
>
> mssql
>
> nat_port_mapping
>
> natpmp
>
> netbios
>
> netis
>
> ntp
>
> ntp_monlist
>
> openvpn
>
> pca_nq
>
> pca_st
>
> pcanywhere
>
> portmap
>
> qotd
>
> rdp
>
> ripv
>
> sentinel
>
> sip
>
> snmp1
>
> snmp2
>
> snmp3
>
> ssdp
>
> tftp
>
> ubiquiti
>
> ubiquiti_discovery_v1
>
> ubiquiti_discovery_v2
>
> upnp
>
> valve
>
> wdbrpc
>
> wsd
>
> wsd_malformed
>
> xdmcp
>
> kerberos
>
> ike

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地，并运行工具构建脚本：

    
    
    git clone https://github.com/nullt3r/udpx
    
    cd udpx
    
    go build ./cmd/udpx

除此之外，我们也可以使用go命令安装工具：

    
    
    go install -v github.com/nullt3r/udpx/cmd/udpx@latest

## 工具参数选项

    
    
    __  ______  ____ _  __
    
           / / / / __ \/ __ \ |/ /
    
          / / / / / / / /_/ /   /
    
         / /_/ / /_/ / ____/   |
    
         \____/_____/_/   /_/|_|
    
             v1.0.2-beta, by @nullt3r
    
     
    
    Usage of ./udpx-linux-amd64:
    
      -c int
    
         设置最大并发链接数量，默认为32
    
      -nr
    
         不随机化地址
    
      -o string
    
         要写入结果的输出文件路径
    
      -s string
    
         仅扫描指定服务，例如ard, bacnet, bacnet_rpm, chargen, citrix, coap, db, db, digi1, digi2, digi3, dns, ipmi, ldap, mdns, memcache, mssql, nat_port_mapping, natpmp, netbios, netis, ntp, ntp_monlist, openvpn, pca_nq, pca_st, pcanywhere, portmap, qotd, rdp, ripv, sentinel, sip, snmp1, snmp2, snmp3, ssdp, tftp, ubiquiti, ubiquiti_discovery_v1, ubiquiti_discovery_v2, upnp, valve, wdbrpc, wsd, wsd_malformed, xdmcp, kerberos, ike
    
      -sp
    
         显示接收到的数据包，仅显示前32个字节
    
      -t string
    
         要扫描的目标IP/CIDR
    
      -tf string
    
         包含目标IP/CIDR的文件列表路径
    
      -w int
    
         等待响应的最大超时时间，默认500ms

## 工具使用

扫描单个IP：

    
    
    udpx -t 1.1.1.1

扫描一个CIDR地址，最大并发128个连接，超时为1000ms：

    
    
    udpx -t 1.2.3.4/24 -c 128 -w 1000

扫描输入地址文件，最大并发128个连接，仅扫描指定服务：

    
    
    udpx -tf targets.txt -c 128 -s ipmi

输出文件JSONL格式数据如下：

    
    
    {"address":"45.33.32.156","hostname":"scanme.nmap.org","port":123,"service":"ntp","response_data":"JAME6QAAAEoAAA56LU9vp+d2ZPwOYIyDxU8jS3GxUvM="}

## 如何添加自己的探针

打开文件pkg/probes/probes.go，其中包含了所有可用的Payload，我们可以根据自己的需要添加协议名称、端口和包数据（十六机制编码）：

    
    
    {
    
            Name: "ike",
    
            Payloads: []string{"5b5e64c03e99b51100000000000000000110020000000000000001500000013400000001000000010000012801010008030000240101"},
    
            Port: []int{500, 4500},
    
    },

## 工具运行截图

![](https://image.3001.net/images/20230517/1684258776_6463bfd872cdde2b32b37.png!small)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/nullt3r/udpx/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **UDPX** ：【[ _GitHub传送门_](https://github.com/nullt3r/udpx)】

## 参考资料

> [ _https://nmap.org/_](https://nmap.org/)
>
> [ _https://github.com/NotSoSecure/udp-> hunter_](https://github.com/NotSoSecure/udp-hunter)
>
> [ _https://github.com/zmap/zgrab2_](https://github.com/zmap/zgrab2)
>
> [ _https://github.com/zmap/zmap_](https://github.com/zmap/zmap)

