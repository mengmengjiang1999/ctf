![](https://image.3001.net/images/20211227/1640588910_61c9666e8a310f1c3b92a.jpg!small)

## 关于UDP-Hunter

UDP-Hunter是一款功能强大的UDP服务安全评估工具，该工具可以覆盖IPv4和IPv6协议。

UDP扫描一直是一项缓慢而痛苦的工作，如果你打算在UDP的基础上添加IPv6支持，那么可选的工具就会非常有限。UDP-Hunter是一个基于Python的开源网络评估工具，主要用于UDP服务的安全扫描。简而言之，UDP-Hunter专注于为IPv6和IPv4主机提供常见的UDP协议安全审计服务。

到目前为止，UDP-Hunter支持19种不同种类的服务探测。该工具允许广大研究人员对大型网络进行批量扫描，以及对特定端口和更多端口进行目标主机扫描。一旦工具扫描到了一项开放服务之后，UDP-Hunter将会进行进一步操作，甚至还可以为广大研究人员提供关于如何利用发现服务的指导。值得一提的是，UDP-Hunter还能够以整洁的文本格式输出分析报告。

## 工具机制

当我们给UDP-Hunter提供一个IP地址范围之后，工具将创建一个IP列表，工具还支持使用域名，因为工具会将域名解析为IP地址并添加至列表中。UDP-Hunter在内部创建好这个列表之后，它将会给列表中所有的IP地址发送UDP探针。如果目标主机运行了UDP服务之后，工具便会立刻响应。UDP-Hunter可以直接嗅探目标网络，尤其是UDP流量，然后读取抵达目标主机的所有UDP数据包。UDP-Hunter运行之后，工具会报告所有接收到的UDP探针。

我们可以给工具添加--noise=false选项来忽略不相关的UDP数据包，并只观察我们感兴趣的数据包。

## 支持的UDP探针

当前版本的UDP-Hunter支持下列UDP服务探针（默认端口）：

    
    
    ike - 500 端口
    
    rpc / RPCCheck - 111 端口
    
    ntp / NTPRequest - 123 端口
    
    snmp-public / SNMPv3GetRequest - 161 端口
    
    ms-sql / ms-sql-slam - 1434 端口
    
    netop - 6502 端口
    
    tftp - 69 端口
    
    db2 - 523 端口
    
    citrix - 1604 端口
    
    echo - 7 端口
    
    chargen - 19 端口
    
    systat - 11 端口
    
    daytime / time - 13 端口
    
    DNSStatusRequest / DNSVersionBindReq - 53 端口
    
    NBTStat - 137 端口
    
    xdmcp - 177 端口
    
    net-sup端口 - 5405 端口
    
    mdns-zeroconf - 5353 端口
    
    gtpv1 - 2123 端口

## 工具要求

    
    
    -Python 3.x
    
    -Python模块（requirements.txt）：netaddr、colorama、argparse、ifaddr、datetime

## 工具安装

广大研究人员可以点击【[ _这里_](https://github.com/NotSoSecure/udp-hunter)】直接下载工具，或者使用下列命令将该项目源码克隆至本地使用：

    
    
    git clone https://github.com/NotSoSecure/udp-hunter

工具初始化-安装所需模块：

    
    
    pip3 install -r requirements.txt

需要的配置文件：

    
    
    -udp.txt - 该文件包含UDP探针
    
    -udphelp.txt - 该文件包含工具列表，以及针对每个UDP探针或UDP服务的操作建议

你也可以使用下列命令行参数修改配置文件：

    
    
    “--configfile ”和“--probehelp ”

下列命令可以验证配置选项：

    
    
    python udp-hunter.py

## 功能/选项

当前版本的UDP-Hunter提供了下列功能选项：

强制选项：

    
    
    --host：单个主机
    
    --file：IP地址文件

可选选项：

    
    
    --output：输出文件
    
    --probes：探针名称（默认为全部探针）
    
    --ports：端口列表（默认为全部端口）
    
    --retries：发送给每台目标主机的数据包数量（默认为2）
    
    --noise：过滤地址列表外的IP内容
    
    --verbose：开启Verbose模式
    
    --timeout：设置超时时长
    
    --lhost6：提供IPV6监听器接口
    
    --lhost4：提供IPv4监听器接口
    
    --configfile：配置文件地址（默认为udp.txt）
    
    --probehelp：帮助文件地址（默认为udphelp.txt）

## 工具使用

    
    
    python udp-hunter.py --file=inputfile.txt --output=outputfile.txt [optional arguments] Usage: python udp-hunter.py --file=inputfile.txt --output=outputfile.txt [--probes=NTPRequest,SNMPv3GetReques] [--ports=123,161,53] [--retries=3] [--noise=true] [--verbose=false] [--timeout=1.0] [--configfile]

## 项目地址

 **UDP-Hunter：** 【[ _GitHub传送门_](https://github.com/NotSoSecure/udp-hunter)】

## 参考资料

> 1、[ _https://www.gadhiyasavan.com/2020/02/udp-> hunter.html_](https://www.gadhiyasavan.com/2020/02/udp-hunter.html)
>
> 2、[ _https://asciinema.org/a/305052_](https://asciinema.org/a/305052)
>
> 3、[ _https://asciinema.org/a/305053_](https://asciinema.org/a/305053)
>
> 4、[ _https://github.com/vanhauser-thc/THC-> Archive/tree/master/Tools_](https://github.com/vanhauser-thc/THC-> Archive/tree/master/Tools)
>
> 5、[ _https://github.com/royhills/ike-scan_](https://github.com/royhills/ike-> scan)
>
> 6[、 _https://nmap.org/book/scan-methods-udp-> scan.html_](https://nmap.org/book/scan-methods-udp-scan.html)
>
> 7、[ _https://github.com/portcullislabs/udp-proto-> scanner_](https://github.com/portcullislabs/udp-proto-scanner)

