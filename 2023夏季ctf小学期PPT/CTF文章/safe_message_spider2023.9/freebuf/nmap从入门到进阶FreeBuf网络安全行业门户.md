## 0x01 介绍

![image.png](https://image.3001.net/images/20210722/1626943371_60f92f8bdca02d54c0c17.png!small)

渗透测试的基本理念是尽可能多的收集信息，而主动扫描则是信息收集的一个重要手段，因此掌握nmap是渗透测试必备的基础能力。

nmap 是一个免费、开源网络扫描工具，用于探测指定网络的主机、端口、服务版本信息。

和所有工具一样，扫描也细分为很多方向，不同需求催生不同的工具，例如专为大型网络扫描而生的masscan，为了速度实现了特定的tcp协议栈（很多选项直接"借用"nmap的习惯），号称X分钟扫描全网。所以nmap并不是所有方面的number
1，但确实是最经典的一个。

## 0x02 过程

“收集的信息越多，渗透的可能性越大”

从nmap的扫描日志中，可以清楚的看到nmap的扫描过程

四个阶段：

> 主机：Initiating Ping Scan 探测主机存活
>
> 端口：Initiating SYN Stealth Scan 探测端口开闭
>
> 服务：Initiating Service scan 获取服务信息
>
> 脚本：Initiating NSE 特定信息获取、漏洞检测等
    
    
    Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-21 06:32 EDT
    NSE: Loaded 153 scripts for scanning.
    NSE: Script Pre-scanning.
    NSE: Starting runlevel 1 (of 3) scan.
    Initiating NSE at 06:32
    Completed NSE at 06:32, 0.00s elapsed
    NSE: Starting runlevel 2 (of 3) scan.
    Initiating NSE at 06:32
    Completed NSE at 06:32, 0.00s elapsed
    NSE: Starting runlevel 3 (of 3) scan.
    Initiating NSE at 06:32
    Completed NSE at 06:32, 0.00s elapsed
    Initiating Ping Scan at 06:32
    Scanning 10.10.85.35 [4 ports]
    Completed Ping Scan at 06:32, 0.41s elapsed (1 total hosts)
    Initiating SYN Stealth Scan at 06:32
    Completed SYN Stealth Scan at 06:32, 0.79s elapsed (12 total ports)
    Initiating Service scan at 06:32
    Scanning 12 services on 10.10.85.35
    Service scan Timing: About 58.33% done; ETC: 06:33 (0:00:44 remaining)
    Completed Service scan at 06:33, 64.89s elapsed (12 services on 1 host)
    NSE: Script scanning 10.10.85.35.
    NSE: Starting runlevel 1 (of 3) scan.
    Initiating NSE at 06:33
    Completed NSE at 06:33, 15.48s elapsed
    NSE: Starting runlevel 2 (of 3) scan.
    Initiating NSE at 06:33
    Completed NSE at 06:33, 1.41s elapsed
    NSE: Starting runlevel 3 (of 3) scan.
    Initiating NSE at 06:33
    Completed NSE at 06:33, 0.00s elapsed
    Nmap scan report for 10.10.85.35
    Host is up, received echo-reply ttl 127 (0.38s latency).
    Scanned at 2021-07-21 06:32:07 EDT for 83s
    

## 0x03 常见扫描选项

 **nmap选项**|  含义  
---|---  
-sV| 获取服务版本信息  
-p or -p-| 扫描指定端口或扫描全部端口  
-Pn| 禁用主机发送，只扫描开放端口  
-A| 高级模式，启用系统探测、服务版本探测、脚本探测等  
-sC| 使用默认nmap脚本扫描  
-v| 详细模式  
-sU| UDP端口扫描  
-sS| TCP SYN端口扫描  
  
### 全端口扫描

-p port 指定端口扫描，nmap默认只扫描top 1000端口

如需对全端口扫描，可以使用-p-，效果和-p1-65535一样

### TCP/SYN/UDP扫描

-sT TCP扫描，进行完整的连接扫描，完成三次握手（SYN-SYN/ACK-ACK），完整的连接一般会在应用日志中留痕，不需要root权限，普通用户默认扫描方式

![image.png](https://image.3001.net/images/20210722/1626943410_60f92fb24d2258b3d50db.png!small)

-sS SYN扫描也叫半连接扫描，不进行完整的三次握手，一般不会在应用日志中留痕，速度快，需要root权限

![image.png](https://image.3001.net/images/20210722/1626943428_60f92fc41d2cb57126a03.png!small)

-sU UDP扫描，速度慢、准确率低，一般只针对少量特定UDP端口进行扫描

示例：

-p U:53,111,137,T:21-25,80,139,8080,S:9

### NULL/FIN/XMAS扫描

旨在bypass防火墙的扫描方式，通过设置或取消标志位，尝试绕过扫描监测工具，原理和效果类似于SYN，一般用不到，随着现代防火墙的发展，已经属于比较鸡肋的功能，有兴趣可以深入了解

## 0x04 重要扫描选项

### 服务探测 -sV

默认不探测服务

![image.png](https://image.3001.net/images/20210722/1626943444_60f92fd463d9083d430f0.png!small)  
使用-sV，可获取服务信息

![image.png](https://image.3001.net/images/20210722/1626943455_60f92fdfe9e6655b949a8.png!small)

原理：

通常包括banner抓取、文件检测等手段

最典型的ssh版本探测，通过抓取返回信息

    
    
    nc 127.0.0.1 22
    SSH-2.0-OpenSSH_8.4p1 Debian-5
    

对比nmap扫描结果

    
    
    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 8.4p1 Debian 5 (protocol 2.0
    

### NSE脚本扫描 -sC

默认不执行脚本探测，对于某些特定服务，想要获取完整版本信息则需要添加脚本扫描，否则只能获得粗略版本信息，不便于漏洞分析

对于samba，执行-sV，只能获取粗略版本信息 3.X-4.X

![image.png](https://image.3001.net/images/20210722/1626943468_60f92fec2ea1a3f691707.png!small)

使用-sC选项，能获取到详细版本信息4.3.8以及附加的额外信息

![image.png](https://image.3001.net/images/20210722/1626943476_60f92ff40112adccb53ca.png!small)

### 漏洞探测 --script vuln

默认的-sC选项，是一类标识为default的扫描工具

常见分类

> `safe`:-不会影响目标
>
> `intrusive`:- 侵入式扫描，可能会影响目标
>
> `vuln`:- 漏洞检测
>
> `exploit`:- 漏洞利用
>
> `auth`:- 尝试对服务进行认证绕过，例如FTP匿名登录
>
> `brute`:- 尝试对服务进行暴力破解
>
> `discovery`:- 尝试查询服务信息，例如samba版本信息

/usr/share/nmap/scripts/script.db中

![image.png](https://image.3001.net/images/20210722/1626943488_60f930000ff4fb51e4081.png!small)

使用默认脚本扫描，可以获得系统版本信息

![image.png](https://image.3001.net/images/20210722/1626943496_60f930088d8bd5b835150.png!small)

使用--script vuln扫描，可以获取漏洞信息，ms17-010(永恒之蓝)

![image.png](https://image.3001.net/images/20210722/1626943502_60f9300ec42cb22edfe9e.png!small)

### 指定脚本扫描

\--script name --script-args name.arg=value

![image.png](https://image.3001.net/images/20210722/1626943512_60f93018790f011e5c803.png!small)

### 扫描速率

对于扫描来说，准确率和时间都很重要，在保证一定准确率的同时，通过调整扫描速率，可以极大缩减扫描时间

\--min-rate 最小扫描速率

\--max-rate 最大扫描速率

默认情况下nmap会跟网络状况自动调整速率，不过很多时候，指定--min-rate和--max-rate才是最适合的扫描速率，普通单机的扫描，一般指定--min-rate=1000即可，网络条件特别优的情况下，指定更大的数值也未尝不可

对比：

    
    
    nmap -p- -sV -sC 10.10.132.75
    
    Nmap done: 1 IP address (1 host up) scanned in 318.63 seconds
    
    nmap -p- -sV -sC 10.10.132.75 --min-rate 1000
    
    Nmap done: 1 IP address (1 host up) scanned in 160.55 seconds
    

### 分组大小

在大范围主机扫描的情况下，可以指定分组大小来调整扫描速率

\--min-hostgroup 最小分组大小

\--max-hostgroup 最大分组大小

参考值：--min-hostgroup 50 500 1000

### 其他时间参数

除前面的时间优化参数之外，还有很多参数--min-parallelism、--min-rtt-timeout、--host-timeout等，不过nmap已经为我们定义好了一些模板，拿来即可

`paranoid`(`0`)、`sneaky`(`1`)、`polite`(`2`)、`normal`(`3`)、`aggressive`(`4`)
和`insane`(`5`)

`T0`是序列化扫描，一次只扫描一个端口，并在发送每个探测之后等待五分钟，主要目的是避免告警

`T1`和`T2`，在两次探测之间分别等待 15 秒和 0.4 秒

`T3`是 Nmap 的默认行为

`-T4`：`--max-rtt-timeout 1250ms --min-rtt-timeout 100ms --initial-rtt-timeout
500ms --max-retries 6`并将最大 TCP 扫描延迟设置为 10 毫秒。

`-T5`:`--max-rtt-timeout 300ms --min-rtt-timeout 50ms --initial-rtt-timeout
250ms --max-retries 2 --host-timeout 15m --script-timeout 10m`并将最大 TCP 扫描延迟设置为
5 毫秒

想快速获取扫描结果，一般提到T4即可

### 其他功能

> `-f`用于对数据包进行分段（即将它们分成更小的部分），从而降低数据包被防火墙或 IDS 检测到的可能性。
>
> `-f`的替代方法，但提供对数据包大小的更多控制：`--mtu <number>`，接受用于发送的数据包的最大传输单元大小。
>
> `--scan-delay <time>ms`:- 用于在发送的数据包之间添加延迟，可用于规避任何可能存在的基于时间的防火墙/IDS 触发器。
>
> `--badsum`生成无效的数据包校验和，任何真正的 TCP/IP
> 堆栈都会丢弃此数据包，但是防火墙可能会自动响应，而不检查数据包的校验和。因此，可用于确定防火墙/IDS 的存在。

## 0x05 nmap脚本实战

数据在不断的使用中才会体现价值，nmap扫描的结果通过python引入数据库，进行多维度的分析与整合，一方面可以提供给漏扫工具作为数据源，同时可以作为资产端口变化趋势的重要组成部分；另一方面做多维度的数据分析与提取（各种TOP
10、各种报表）、扫描速度优化等。结合下CMDB、企业内部数据、日志平台，又是一个安全大屏。

常用nmap相关的python库主要有python-nmap/python-libnmap

python-nmap整体比较简单

https://pypi.org/project/python-nmap/

    
    
    >>> import nmap
    >>> nm=nmap.PortScanner()
    >>> nm.scan('10.10.92.24','22')
    {'nmap': {'command_line': 'nmap -oX - -p 22 -sV 10.10.92.24', 'scaninfo': {'tcp': {'method': 'connect', 'services': '22'}}, 'scanstats': {'timestr': 'Thu Jul 22 03:55:52 2021', 'elapsed': '1.76', 'uphosts': '1', 'downhosts': '0', 'totalhosts': '1'}}, 'scan': {'10.10.92.24': {'hostnames': [{'name': '', 'type': ''}], 'addresses': {'ipv4': '10.10.92.24'}, 'vendor': {}, 'status': {'state': 'up', 'reason': 'syn-ack'}, 'tcp': {22: {'state': 'open', 'reason': 'syn-ack', 'name': 'ssh', 'product': 'OpenSSH', 'version': '7.2p2 Ubuntu 4ubuntu2.4', 'extrainfo': 'Ubuntu Linux; protocol 2.0', 'conf': '10', 'cpe': 'cpe:/o:linux:linux_kernel'}}}}}
    

python-libnmap则细化为多个类，包括Process,Parser,Report等，可以快速调用nmap扫描并将扫描结果结构化以供针对性的进行漏洞扫描

demo代码

    
    
    #!/usr/bin/env python3
    #coding:utf-8
    
    from libnmap.process import NmapProcess
    from libnmap.parser import NmapParser
    from libnmap.objects import NmapReport
    import time
    import sys
    
    if len(sys.argv)<2:
        print("need a ip")
        sys.exit(0)
    nm=NmapProcess(sys.argv[1],'-n -vvv -sV -sC')
    nm.run_background()
    while nm.is_running():
        time.sleep(5)
        print("Nmap scan %s %s%%" %(time.strftime("%Y-%m-%d %H:%m:%S",time.localtime()),nm.progress))
    result=nm.stdout
    report=NmapParser.parse(result)
    target=report.hosts[0]
    target.services
    services=[]
    for serv in target.services:
        data=[serv.port,serv.state,serv.protocol,serv.service,serv.banner]
        print(data)
        services.append(data)
    
    # todo
    # store data
    # vuln scan
    '''python3 test_libnmap.py 10.10.92.24
    [22, 'open', 'tcp', 'ssh', 'product: OpenSSH version: 7.2p2 Ubuntu 4ubuntu2.4 extrainfo: Ubuntu Linux; protocol 2.0 ostype: Linux']
    [80, 'open', 'tcp', 'http', 'product: Apache httpd version: 2.4.18 extrainfo: (Ubuntu)']
    [139, 'open', 'tcp', 'netbios-ssn', 'product: Samba smbd version: 3.X - 4.X extrainfo: workgroup: WORKGROUP hostname: BASIC2']
    [445, 'open', 'tcp', 'netbios-ssn', 'product: Samba smbd version: 4.3.11-Ubuntu extrainfo: workgroup: WORKGROUP hostname: BASIC2']
    [8009, 'open', 'tcp', 'ajp13', 'product: Apache Jserv extrainfo: Protocol v1.3']
    [8080, 'open', 'tcp', 'http', 'product: Apache Tomcat version: 9.0.7']
    '''
    

## 0x06 写在最后

nmap，作为网络扫描界的“Swiss Army
knife”，其功能强大并不是一篇简短的文章可以覆盖完全的，本文更多的是抛砖引玉。作为扫描体系的重要一环，nmap及类似的工具也起着承上启下的作用，为漏扫、威胁建模等提供了强有力的数据源分析。拥有一张网络地图，也就有了渗透入口的全景图，这也正是nmap的核心价值。

