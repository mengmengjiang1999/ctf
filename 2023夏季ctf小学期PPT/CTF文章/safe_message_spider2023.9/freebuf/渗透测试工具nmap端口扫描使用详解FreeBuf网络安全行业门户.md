![](https://image.3001.net/images/20230614/1686730248_6489760835ea51c75a638.png!small)

## 前言

只介绍如何使用端口扫描及常用命令解释，如何安装在此不赘述，可自行百度。当然，可以使用kali，无需安装直接使用，

## 简介

[nmap ](https://nmap.org/
"nmap官网")是一款渗透端口扫描测试工具。它不单单可以进行端口扫描，还可以扫描漏洞、服务器信息等等。是一款十分强大的扫描工具，可以在windows、mac、Linux上运行。

  

nmap是一个网络连接端扫描软件，用来扫描网上电脑开放的网络连接端。确定哪些服务运行在哪些连接端，并且推断计算机运行哪个操作系统（这是亦称
fingerprinting）。它是网络管理员必用的软件之一，以及用以评估网络系统安全。

  
正如大多数被用于网络安全的工具，nmap 也是不少黑客及骇客（又称脚本小子）爱用的工具
。系统管理员可以利用nmap来探测工作环境中未经批准使用的服务器，但是黑客会利用nmap来搜集目标电脑的网络设定，从而计划攻击的方法。

  
Nmap 常被跟评估系统漏洞软件Nessus 混为一谈。Nmap 以隐秘的手法，避开闯入检测系统的监视，并尽可能不影响目标系统的日常操作。

  

其官网：<https://nmap.org/>

  

## 1.使用说明

用法：

> nmap[扫描类型][选项]｛目标规范｝

目标规格：可以传递主机名、IP地址、网络等。

例如：

> scanme.nmap.org，microsoft.com/24，192.168.0.1；10.0.0.255.1-2

  

安装或运行 nmap 会出现参数介绍：

    
    
    Nmap 7.92 ( https://nmap.org )
    Usage: nmap [Scan Type(s)] [Options] {target specification}
    TARGET SPECIFICATION:
      Can pass hostnames, IP addresses, networks, etc.
      Ex: scanme.nmap.org, microsoft.com/24, 192.168.0.1; 10.0.0-255.1-254
      -iL <inputfilename>: Input from list of hosts/networks
      -iR <num hosts>: Choose random targets
      --exclude <host1[,host2][,host3],...>: Exclude hosts/networks
      --excludefile <exclude_file>: Exclude list from file
    HOST DISCOVERY:
      -sL: List Scan - simply list targets to scan
      -sn: Ping Scan - disable port scan
      -Pn: Treat all hosts as online -- skip host discovery
      -PS/PA/PU/PY[portlist]: TCP SYN/ACK, UDP or SCTP discovery to given ports
      -PE/PP/PM: ICMP echo, timestamp, and netmask request discovery probes
      -PO[protocol list]: IP Protocol Ping
      -n/-R: Never do DNS resolution/Always resolve [default: sometimes]
      --dns-servers <serv1[,serv2],...>: Specify custom DNS servers
      --system-dns: Use OS's DNS resolver
      --traceroute: Trace hop path to each host
    SCAN TECHNIQUES:
      -sS/sT/sA/sW/sM: TCP SYN/Connect()/ACK/Window/Maimon scans
      -sU: UDP Scan
      -sN/sF/sX: TCP Null, FIN, and Xmas scans
      --scanflags <flags>: Customize TCP scan flags
      -sI <zombie host[:probeport]>: Idle scan
      -sY/sZ: SCTP INIT/COOKIE-ECHO scans
      -sO: IP protocol scan
      -b <FTP relay host>: FTP bounce scan
    PORT SPECIFICATION AND SCAN ORDER:
      -p <port ranges>: Only scan specified ports
        Ex: -p22; -p1-65535; -p U:53,111,137,T:21-25,80,139,8080,S:9
      --exclude-ports <port ranges>: Exclude the specified ports from scanning
      -F: Fast mode - Scan fewer ports than the default scan
      -r: Scan ports consecutively - don't randomize
      --top-ports <number>: Scan <number> most common ports
      --port-ratio <ratio>: Scan ports more common than <ratio>
    SERVICE/VERSION DETECTION:
      -sV: Probe open ports to determine service/version info
      --version-intensity <level>: Set from 0 (light) to 9 (try all probes)
      --version-light: Limit to most likely probes (intensity 2)
      --version-all: Try every single probe (intensity 9)
      --version-trace: Show detailed version scan activity (for debugging)
    SCRIPT SCAN:
      -sC: equivalent to --script=default
      --script=<Lua scripts>: <Lua scripts> is a comma separated list of
               directories, script-files or script-categories
      --script-args=<n1=v1,[n2=v2,...]>: provide arguments to scripts
      --script-args-file=filename: provide NSE script args in a file
      --script-trace: Show all data sent and received
      --script-updatedb: Update the script database.
      --script-help=<Lua scripts>: Show help about scripts.
               <Lua scripts> is a comma-separated list of script-files or
               script-categories.
    OS DETECTION:
      -O: Enable OS detection
      --osscan-limit: Limit OS detection to promising targets
      --osscan-guess: Guess OS more aggressively
    TIMING AND PERFORMANCE:
      Options which take <time> are in seconds, or append 'ms' (milliseconds),
      's' (seconds), 'm' (minutes), or 'h' (hours) to the value (e.g. 30m).
      -T<0-5>: Set timing template (higher is faster)
      --min-hostgroup/max-hostgroup <size>: Parallel host scan group sizes
      --min-parallelism/max-parallelism <numprobes>: Probe parallelization
      --min-rtt-timeout/max-rtt-timeout/initial-rtt-timeout <time>: Specifies
          probe round trip time.
      --max-retries <tries>: Caps number of port scan probe retransmissions.
      --host-timeout <time>: Give up on target after this long
      --scan-delay/--max-scan-delay <time>: Adjust delay between probes
      --min-rate <number>: Send packets no slower than <number> per second
      --max-rate <number>: Send packets no faster than <number> per second
    FIREWALL/IDS EVASION AND SPOOFING:
      -f; --mtu <val>: fragment packets (optionally w/given MTU)
      -D <decoy1,decoy2[,ME],...>: Cloak a scan with decoys
      -S <IP_Address>: Spoof source address
      -e <iface>: Use specified interface
      -g/--source-port <portnum>: Use given port number
      --proxies <url1,[url2],...>: Relay connections through HTTP/SOCKS4 proxies
      --data <hex string>: Append a custom payload to sent packets
      --data-string <string>: Append a custom ASCII string to sent packets
      --data-length <num>: Append random data to sent packets
      --ip-options <options>: Send packets with specified ip options
      --ttl <val>: Set IP time-to-live field
      --spoof-mac <mac address/prefix/vendor name>: Spoof your MAC address
      --badsum: Send packets with a bogus TCP/UDP/SCTP checksum
    OUTPUT:
      -oN/-oX/-oS/-oG <file>: Output scan in normal, XML, s|<rIpt kIddi3,
         and Grepable format, respectively, to the given filename.
      -oA <basename>: Output in the three major formats at once
      -v: Increase verbosity level (use -vv or more for greater effect)
      -d: Increase debugging level (use -dd or more for greater effect)
      --reason: Display the reason a port is in a particular state
      --open: Only show open (or possibly open) ports
      --packet-trace: Show all packets sent and received
      --iflist: Print host interfaces and routes (for debugging)
      --append-output: Append to rather than clobber specified output files
      --resume <filename>: Resume an aborted scan
      --noninteractive: Disable runtime interactions via keyboard
      --stylesheet <path/URL>: XSL stylesheet to transform XML output to HTML
      --webxml: Reference stylesheet from Nmap.Org for more portable XML
      --no-stylesheet: Prevent associating of XSL stylesheet w/XML output
    MISC:
      -6: Enable IPv6 scanning
      -A: Enable OS detection, version detection, script scanning, and traceroute
      --datadir <dirname>: Specify custom Nmap data file location
      --send-eth/--send-ip: Send using raw ethernet frames or IP packets
      --privileged: Assume that the user is fully privileged
      --unprivileged: Assume the user lacks raw socket privileges
      -V: Print version number
      -h: Print this help summary page.
    EXAMPLES:
      nmap -v -A scanme.nmap.org
      nmap -v -sn 192.168.0.0/16 10.0.0.0/8
      nmap -v -iR 10000 -Pn -p 80
    SEE THE MAN PAGE (https://nmap.org/book/man.html) FOR MORE OPTIONS AND EXAMPLES我

  

不用全部看完，只用看常用的参数，逐步从入门到入狱，一步一步来。

  

其使用格式如下：

  

    
    
    nmap [扫描类型] [选项参数] {目标端口}

> 其中，"[]" 是非必填项，{} 是必须项，

例如：

> nmap 127.0.0.1

  

运行后默认会以nmap 预设的高危的1000个端口进行扫描

  

等待结果出现：

    
    
    └─$ nmap -p 22,3306,80 114.132.238.169
    Starting Nmap 7.92 ( https://nmap.org ) at 2023-06-14 16:08 CST
    Nmap scan report for 114.132.238.169
    Host is up (0.022s latency).
    
    PORT     STATE    SERVICE
    22/tcp   open     ssh
    80/tcp   open     http
    3306/tcp filtered mysql
    
    

即代表扫描完成！

##  **参数讲解**

###  **-p＜端口范围＞：仅扫描指定的端口**

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

该参数-p 用于扫描指定端口是否开放，在 `-p` 后输入指定的端口，以英文","进行拼接多个指定端口。，例如：-p22; -p1-65535; -p
U:53,111,137,T:21-25,80,139,8080,S:9

>   * nmap **-p 80,3306,22,23,443** {IP} ：指定端口扫描
>   * nmap **-p 1-65535** {IP}：全面扫描，计算机端口共65535个。该命令将会从1-65535
> 个端口进行扫描，查找开放的端口: -p 1-65535
>   * nmap **-p-** {IP}：另一种全面扫描（缩减版）: -p->

该参数帮助网络安全人员进行指定端口扫描更准确的获取到扫描结果

###  **高级穿透防火墙扫描: -sA**

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

用于穿透防火墙，遇到禁止Ping的网站使用，与PN类似

> nmap **-sA** 127.0.0.1

###  **探测端口版本: -sV**

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

> nmap **-sV** \- 127.0.0.1

### 显示扫描信息： -v（使用-vv或更多效果）

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

###

实时输出扫描进程状态，大量端口或缓慢情况下，可以打开查看扫描情况，格式如下：

> nmap p 80,3306,22,23,443 **-v** {IP}

###  **写入报告：-oN/-oX/-oS/-oG <file> **

### **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

参数-oN、-oX、-oS和-oG用于指定将扫描结果保存到文件的格式。这些参数可以帮助网络安全人员在不将扫描结果显示在屏幕上或将其保存到屏幕截图文件的情况下，将扫描结果保存到指定的文件中

示例：

>   * nmap - **oN** output.nmap <target>：将扫描结果保存到名为output.nmap的文件中，而不将其显示在屏幕上。
>   * nmap - **oX** output.xml <target>：将扫描结果保存到名为output.xml的文件中，使用XML格式表示。
>   * nmap - **oS** output.svg <target>：将扫描结果保存到名为output.svg的文件中，使用SVG格式表示。
>   * nmap - **oG** output.gnp
> <target>：将扫描结果保存到名为output.gnp的文件中，使用GnuPlot格式表示。
>

  

  

  

这些参数可以帮助网络安全人员根据不同的需求将扫描结果保存到不同的文件中，并进行进一步的分析和可视化。

###  **扫描客户端存活主机：-sP**

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

可扫描1-255 域名/IP网段的主机信息，例如：

> nmap **-sP** www.xxx.com/24

###  **禁止动态扫描: -T4**

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

针对TCP端口禁止动态扫描延迟超过10ms

> nmap **-T4** 127.0.0.1

###  **快速扫描: -F**

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

快速模式-扫描比默认扫描更少的端口，速度更快。

> nmap -T4 **-F** 127.0.0.1

###  **穿透防火墙探测: -PN**

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

部分系统禁止ping导致nmap部分选项无法执行，则遇到禁Ping的可以加上 `-PN` 绕过防火墙进行扫描探测

> nmap **-PN** -A -v 127.0.0.1

### 反向解析域名/IP:-n/-R

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

参数 **-n** 代表不反向解析域名，而 **-R** 代表需要反向解析域名。

> nmap **-n** -v 127.0.0.1

### 指定脚本扫描：--script=<Lua scripts>

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

该参数：--script=<Lua scripts> 用于指定脚本扫描，支持泛式写法，即，如使用http所有脚本则可以使用http-* 进行脚本扫描

> nmap **\--script=http-*** <target>: 使用指定脚本进行扫描

这个参数可以帮助网络安全人员提供使用指定脚本扫描。

### 增加端口扫描解释：--reason

###  **⭐️** **⭐️** **⭐️** **⭐️** **⭐️**

参数--reason用于指定在执行扫描时，解释为什么扫描目标开放了某个特定的端口。

> nmap -p 80 **\--reason** <target>：扫描目标主机的80端口，并解释为什么该端口被认为是开放的

这个参数可以帮助网络安全人员更好地理解为什么某个端口被认为开放了，从而更好地进行漏洞评估和安全漏洞扫描。

###  **探测主机操作系统：-O (大写英文字母：O (欧) )**

###  **⭐️** **⭐️** **⭐️** **⭐️**

查看服务器是使用什么系统，如linux/windows。

> nmap **-O** www.xxx.com

###  **全面探测：-A**

###  **⭐️** **⭐️** **⭐️** **⭐️**

既然都说是全面了，那就是全部（all）扫描探测端口

> nmap **-A** -v 127.0.0.1

### 探测目标主机IP协议：-sO(英文大写字母：O)

###  **⭐️** **⭐️** **⭐️** **⭐️**

参数-sO用于判断目标主机上使用的是哪些协议，同时探测目标主机支持哪些IP协议。

> nmap **-sO** <targetIP>：扫描目标IP地址并判断目标主机上使用的是哪些协议。

  

  

  

这个参数可以帮助网络安全人员发现目标主机上支持的协议和可能存在的漏洞或弱点。

###  **读取主机列表: -iL <xxx.txt>**

###  **⭐️** **⭐️** **⭐️** **⭐️**

有时候并非一个主机IP探测，也可以有多个主机一起探测。则使用`-iL`进行批量探测。 多个ip以换行形式写入，例如ips.txt 内容：

> 127.0.0.1
>
> 192.168.0.1
>
> .....

命令：

> nmap **-iL** C:\\\ips.txt

### 指定扫描源：-S <IP_Address>

###  **⭐️** **⭐️** **⭐️** **⭐️**

参数-S用于指定扫描的源IP地址。这个参数可以帮助网络安全人员在不使用自己的IP地址进行扫描的情况下，隐藏自己的位置。

>  
>
>
> nmap **-S 192.168.0.1** <target>：使用192.168.0.1作为扫描源IP地址，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员在不暴露自己位置的情况下，进行更安全的网络扫描。

### 指定代理服务器地址：--proxies <url1,[url2],...>

###  **⭐️** **⭐️** **⭐️** **⭐️**

参数--proxies用于指定代理服务器地址。这个参数可以帮助网络安全人员在不直接连接目标主机的情况下，进行网络扫描和漏洞探测。

> nmap **\--proxies http://proxy1.example.com:8080**
> <target>：使用http://proxy1.example.com:8080作为代理服务器地址，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员在不暴露自己位置的情况下，进行更安全的网络扫描。同时，使用代理服务器还可以绕过一些防火墙和网络限制。

###  **TCP connect 扫描: -sT**

###  **⭐️** **⭐️** **⭐️**

即tcp连接形式进行扫描，通常会在目标主机的日志中存在大批量请求以及错误日志（留下痕迹）

> nmap **-sT** 127.0.0.1

### 只显示打开的端口：--open

### **⭐️** **⭐️** **⭐️**

参数 --open 用于在扫描结束后只返回打开的端口。

> nmap **\--open** <target>

这个参数可以帮助网络安全人员更准确的获取到开放端口信息

### 协议扫描：-PO[protocol list]

###  **⭐️** **⭐️** **⭐️**

指定要扫描的协议列表，它允许你扫描目标主机上开放的协议。

  

  

  

这个参数可以帮助网络安全人员发现目标主机上开放的协议和端口，从而发现可能存在的漏洞或弱点。

  

用法：

>  
>
>
>   * nmap - **PO** <target>：扫描目标主机上所有的协议（除了ICMP）。
>   * nmap - **PO** 1/3/5：扫描目标主机上的TCP、UDP和ICMP协议。
>   * nmap - **PO** 7/9：扫描目标主机上的SNMP和SMTP协议。
>

###  **启用FTP反弹扫描：-b**

###  **⭐️** **⭐️** **⭐️**

-b用于启用FTP反弹扫描。这是一种借助FTP特性进行的隐身扫描方式。通过与FTP服务器建立连接，来实现隐身扫描的目的

  

> nmap **-b** <targetIP>

这个参数可以帮助网络安全人员来实现隐身扫描的目的

  

  

### 自动完成所有操作： --noninteractive

###  **⭐️** **⭐️** **⭐️**

是一个常用的命令行选项，它表示在执行操作时不与用户进行交互。换句话说，在执行该命令时，系统将自动完成所有操作，而无需用户手动干预。

例如，在自动化任务或批处理中，您可能需要使用--noninteractive选项来确保程序的执行不会因为需要用户输入而中断。

> nmap **\--noninteractive** <target>

请注意，具体的使用方法和选项可能会根据您正在使用的软件或工具而有所不同。因此，建议您查阅相关文档或咨询技术支持以获取更准确的信息。

### 全量信息探测：--version-all

###  **⭐️** **⭐️** **⭐️**

该参数--version-all用于最强信息探测，将会获取最全的探测信息，与`--version-intensity 9`相同级别

> nmap **\--version-light** <target>:最强信息探测，将会获取最全的探测信息

这个参数可以帮助网络安全人员提供更详细的版本信息。

### 查看指定脚本帮助：--script-help=<Lua scripts>

###  **⭐️** **⭐️** **⭐️**

该参数： --script-help=<Lua scripts>用于查看脚本使用说明。＜Lua scripts＞是一个以逗号分隔的脚本文件列表，或者脚本类别

> nmap **\--script-help=http-php-version**

### 指定网络接口： -e <iface>

###  **⭐️** **⭐️** **⭐️**

参数-e用于指定要使用的网络接口。这个参数可以帮助网络安全人员针对特定的网络接口进行扫描，以便更好地理解目标主机的网络结构和探测可能存在的漏洞或弱点。

> nmap **-e eth0** <target>：使用eth0作为网络接口，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员针对特定的网络接口进行扫描，提高扫描的准确性和效率。

### 指定扫描源端口：-g/--source-port <portnum>

###  **⭐️** **⭐️** **⭐️**

参数-g或--source-port用于指定扫描时使用的源端口。这个参数可以帮助网络安全人员在不使用随机源端口的情况下，隐藏自己的位置并减少被发现的风险。

> nmap **-g 80** <target>：使用80作为源端口，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员在不暴露自己位置的情况下，进行更安全的网络扫描。

  

### 空闲扫描：-sI

###  **⭐️** **⭐️** **⭐️**

-sI用于进行空闲扫描，也被称为闲置扫描。这种类型的扫描通过发送一个带有随机源地址和源端口的TCP数据包，然后等待目标主机的响应，来探测目标主机上是否有开放端口。

>  
>
>
>   * nmap - **sI** <source_address> <target>：使用指定的源地址进行空闲扫描。
>   * nmap - **sI** <random_port> <target>：使用随机端口进行空闲扫描。
>

作用：这个参数可以帮助网络安全人员发现目标主机上开放的端口和可能存在的漏洞或弱点，并提供更隐蔽的扫描方式。

### 半开式扫描： -sS/sT/sA/sW/sM

###  **⭐️** **⭐️**

###

半开扫描,很少有系统能够把这记入系统日志。不过，需要 **root** 权限

> 半开扫描（half-open scanning），即TCP SYN
> scan。它利用了TCP连接建立三次握手的第一步，并且没有建立一个完整的TCP连接。实现办法是向远端主机某端口发送一个只有SYN标志位的TCP报文段，如果主机反馈一个SYN|ACK数据包，那么，这个主机正在监听该端口，如果反馈的是RST数据包，说明，主机没有监听该端口。在X-> Scanner扫描工具上就有SYN的选择项。

示例：

> nmap **-sS** -p 80,3306,22,23,443 {IP}

该参数帮助网络安全人员进行指定端口扫描更准确的获取到扫描结果

  

  

### 提高调试级别： -d（使用-dd或更多效果）

###  **⭐️** **⭐️**

###

增加详细程度, 实时输出扫描进程状态， 格式如下：

> nmap - **sS** -p 80,3306,22,23,443 **-v** {IP}

### 启用IPv6扫描：-6

###  **⭐️** **⭐️**

参数-6选项用于启动ipv6网络进行扫描探测

> nmap **-6** <target>

这个选项可以帮助网络安全人员使用 ipv6 进行扫描

### 指定发送数据包协议：--send-eth/--send-ip

###  **⭐️** **⭐️**

参数--send-eth和--send-ip选项用于指定发送数据包时使用的协议。

  * \--send-eth选项用于发送以太网数据包，它使用IPv4和ARP协议。
  * \--send-ip选项用于发送IPv4数据包，它只使用IPv4协议。

>   *  **nmap --send-eth** ＜target＞：发送以太网数据包给目标主机。
>   *  **nmap --send-ip** ＜target＞：发送IPv4数据包给目标主机。
>

这些选项可以帮助网络安全人员在不使用IPv6的情况下，仅使用IPv4或以太网进行网络扫描和数据包发送。这在仅支持IPv4或以太网的环境中非常有用。

### 以最高特权扫描：--privileged

###  **⭐️** **⭐️**

参数--privileged用于指定扫描的目标主机是否具有特权。

> nmap **\--privileged** ＜target＞：扫描目标主机是否具有特权

这个选项可以帮助网络安全人员在不具有特权的情况下，检查目标主机是否具有特权访问权限。这在渗透测试和漏洞评估中非常有用，因为它可以帮助确定目标主机是否易受攻击或存在漏洞。

### 非特权扫描：--unprivileged

###  **⭐️** **⭐️**

参数--unprivileged用于指定扫描的目标主机是否为非特权。

> nmap **\--unprivileged** ＜target＞：扫描目标主机是否为非特权。

这个选项可以帮助网络安全人员在不具有特权的情况下，检查目标主机是否具有特权访问权限。这在渗透测试和漏洞评估中非常有用，因为它可以帮助确定目标主机是否易受攻击或存在漏洞。

###  **秘密FN数据包扫描：-sN/sF/sX**

###  **⭐️** **⭐️**

圣诞树(Xmas Tree)、空(Nul)扫描模式

> nmap **-sF** -p 80 127.0.0.1

### 限制操作系统检测：--osscan-limit

###  **⭐️** **⭐️**

参数--osscan-limit用于限制操作系统检测的范围。这个参数可以帮助网络安全人员更准确地探测目标主机的操作系统类型，并提供更详细的信息

> nmap **\--osscan-limit** <target>：限制操作系统检测的范围，提高探测准确度。

这个参数可以帮助网络安全人员更准确地确定目标主机的操作系统类型，并提供更详细的信息。同时，这种方式也可以减少扫描时间，提高扫描效率。

### 数据包追踪：--packet-trace

###  **⭐️** **⭐️**

这个参数 --packet-trace 用于显示扫描数据包情况，并实时输出到命令行上

> nmap **\--packet-trace** <target>:显示扫描数据包情况

这个参数可以帮助网络安全人员获取到数据包扫描详情信息，便于调试。

### 系统类型模糊猜解：--osscan-guess

###  **⭐️** **⭐️**

参数--osscan-guess用于启用操作系统类型模糊猜解。这个参数可以帮助网络安全人员更准确地确定目标主机的操作系统类型，并提供更详细的信息。

> nmap **\--osscan-guess** <target>：启用操作系统类型模糊猜解，提高探测准确度

这个参数可以帮助网络安全人员更准确地确定目标主机的操作系统类型，并提供更详细的信息。但是，这种方式也存在一定的风险，如果目标主机上运行的是非常罕见的操作系统，可能会引起误判。因此，这种方式适用于对目标主机进行更深入的扫描和分析。

### 指定扫描的强度:-T<0-5>

###  **⭐️** **⭐️**

参数-T用于指定扫描的时序，即扫描的强度。其中，-T<0-5>用于指定扫描强度范围在0到5之间。不同的数字代表不同的扫描强度，数字越大表示扫描强度越高，同时也会对目标主机产生更大的干扰。

>   * nmap **-T0** <target>：最弱的扫描强度，对目标主机干扰最小。
>   * nmap **-T4** <target>：最强的扫描强度，对目标主机干扰最大。
>

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的扫描强度，并提供更准确的扫描结果。同时，这种方式也可以减少对目标主机的干扰，提高扫描效率。

### 显示追踪路径/路由信息：--traceroute

###  **⭐️** **⭐️**

显示追踪到目标的路径。这个参数可以帮助网络安全人员了解目标主机的网络路径和路由信息，以便更好地理解目标主机的网络结构和探测目标主机的开放端口

> nmap -- **traceroute** <targetIP>：显示追踪到目标IP地址的路径。

### 指定传输包数据： --data <hex string>

###  **⭐️** **⭐️**

参数--data用于指定要发送的数据。这个参数可以帮助网络安全人员在不使用默认数据的情况下，进行定制化的漏洞探测。

> nmap **\--data A1B2C3D4E5F6**
> <target>：指定要发送的数据为十六进制字符串A1B2C3D4E5F6，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员针对特定的漏洞进行定制化的数据探测，提高漏洞发现的准确性和效率。

### 指定传输字符串：--data-string <string>

###  **⭐️** **⭐️**

参数--data-string用于向目标主机发送一个特定的字符串。这个参数可以帮助网络安全人员在不使用默认数据的情况下，进行定制化的漏洞探测。

> nmap **\--data-string "GET /cgi-bin/printenv.pl HTTP/1.0"**
> <target>：向目标主机发送一个特定的字符串"GET /cgi-bin/printenv.pl
> HTTP/1.0"，扫描目标主机的开放端口和相关信息。

  

  

  

这个参数可以帮助网络安全人员针对特定的漏洞进行定制化的数据探测，提高漏洞发现的准确性和效率。

  

### 指定发送包长度： --data-length

###  **⭐️** **⭐️**

  

参数--data-length用于指定发送数据包的长度。这个参数可以帮助网络安全人员控制数据包的长度，以便更好地理解目标主机的网络结构和探测可能存在的漏洞或弱点。

>  
>
>
> nmap **\--data-length 100 <target>**：指定发送数据包的长度为100字节，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的数据包长度，并提供更精确的扫描结果。同时，控制数据包长度也可以减少对目标主机的干扰，提高扫描效率。

### 指定TTL：--ttl <val>

###  **⭐️** **⭐️**

在nmap中，参数--ttl用于指定IP头部中Time To
Live（TTL）字段的值。这个参数可以帮助网络安全人员在不使用默认TTL值的情况下，进行定制化的网络探测。

> nmap **\--ttl 30** <target>：指定IP头部中TTL字段的值为30，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的TTL值，并提供更精确的扫描结果。同时，控制TTL值也可以减少对目标主机的干扰，提高扫描效率。

### 伪装mac地址 --spoof-mac <mac address/prefix/vendor name>

###  **⭐️** **⭐️**

参数--spoof-mac用于伪装扫描的源MAC地址。这个参数可以帮助网络安全人员在不使用自己的MAC地址进行扫描的情况下，隐藏自己的位置并减少被发现的风险。

> nmap **\--spoof-mac 00:11:22:33:44:55**
> <target>：伪装源MAC地址为00:11:22:33:44:55，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员在不暴露自己位置的情况下，进行更安全的网络扫描。同时，伪装MAC地址还可以绕过一些基于MAC地址过滤的网络安全措施。

### TCP/UDP/SCTP校验和发送数据包： --badsum

###  **⭐️** **⭐️**

参数--badsum用于为数据包生成无效的校验和任何真正的TCP/IP堆栈都会丢弃此数据包，但是，防火墙可能会自动响应，而无需检查数据包的校验和。因此，此开关可用于确定防火墙/IDS的存在

> nmap **\--badsum** <target>:为数据包生成无效的校验和

这个参数可以帮助网络安全人员确定防火墙/IDS是否存在

### 全部输出文件：-oA＜basename＞

###  **扫描之前无需ping: -P0 (数字：0（零）)**

###  **⭐️** **⭐️**

> nmap **-P0** 127.0.0.1

###  **列出扫描目标：-sL**

###  **⭐️** **⭐️**

简单地列出要扫描的目标, 要注意，使用 `-sL` 参数， 不能使用-F（快速扫描）或-p（显式端口选择）参数

> nmap **-sL** -iL ./ips.txt

### Ping扫描：-sn

###  **⭐️** **⭐️**

###

Ping扫描-禁用端口扫描

> nmap **-sn** -v ./ips.txt

### 脚本参数： --script-args=<n1=v1,[n2=v2,...]>

###  **⭐️** **⭐️**

该参数： --script-args=<n1=v1,[n2=v2,...]> 用于脚本交互的参数，多个参数以英文逗号","关联

> nmap --script=xxx **\--script-args=n1=1,n2=2** <target>: 脚本参数

这个参数可以帮助网络安全人员提供使用脚本参数

### 指定信息探测强度：--version-intensity

###  **⭐️** **⭐️**

参数--version-intensity用于指定要探测的版本信息强度。这个参数可以帮助网络安全人员更详细地了解目标主机上开放端口的相关版本信息，从而发现可能存在的漏洞或弱点。

  

>  
>
>
>   * nmap **\--version-intensity 7** <target>：高强度探测目标主机上开放端口的版本信息。
>   * nmap **\--version-intensity 3** <target>：低强度探测目标主机上开放端口的版本信息。
>

  

  

  

  

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的版本信息强度，并提供更详细的版本信息。

  

###

### 显示探测信息： --version-trace

###  **⭐️** **⭐️**

该参数 --version-trace用于显示详细的版本扫描活动，一般用于调试

> nmap **\--version-trace** <target>:显示详细的版本扫描活动

这个参数可以帮助网络安全人员提供运行活动信息，便于调试

### 默认脚本扫描：-sC/--script=default

###  **⭐️** **⭐️**

该参数-sC 用于使用默认脚本进行扫描，同--script=default相同，

> nmap **-sC** <target>:使用默认脚本进行扫描

这个参数可以帮助网络安全人员提供使用默认脚本扫描。

### 使用SCTP INIT/COOKIE-ECHO扫描： -sY/sZ

###  **⭐️** **⭐️**

参数-sY/sZ用于使用SCTP INIT/COOKIE-ECHO来扫描SCTP协议端口的开放的情况。这种类型的扫描通过发送一个SCTP
INIT数据包来探测目标主机上是否存在开放的SCTP端口，如果目标主机响应一个SCTP COOKIE-ECHO数据包，则说明目标主机上存在开放的SCTP端口。

>   * nmap **-sY** <targetIP>：使用SCTP INIT扫描来探测目标主机上是否存在开放的SCTP端口。
>   * nmap **-sZ** <targetIP>：使用SCTP COOKIE-ECHO扫描来探测目标主机上是否存在开放的SCTP端口。
>

这个参数可以帮助网络安全人员发现目标主机上开放的SCTP端口和可能存在的漏洞或弱点

### 指定IP选项字段 --ip-options <options>

###  **⭐️**

参数--ip-options用于指定IP选项字段的值。这个参数可以帮助网络安全人员在不使用默认IP选项的情况下，进行定制化的漏洞探测。

> nmap **\--ip-options "DO NOT Fragment"** <target>：向目标主机发送一个特定的IP选项"DO NOT
> Fragment"，扫描目标主机的开放端口和相关信息。

这个参数可以帮助网络安全人员针对特定的漏洞进行定制化的IP选项探测，提高漏洞发现的准确性和效率。

###  **UDP扫描：-sU**

###  **⭐️**

UPD扫描可靠性低

> nmap **-sU** -p 80 127.0.0.1

###  **查看帮助文档：-h**

###  **⭐️**

有啥能说的，看看文档，获取更多工具使用详情介绍

> nmap **-h**

###  **随机IP扫描:-iR <num hosts>**

###  **⭐️**

选择从多个ip中进行扫描目标

> nmap -iL C:\\\ips.txt -F -T4 **-iR 1** -v

###  **排除扫描主机： --exclude <host1[,host2][,host3],...>**

###  **⭐️**

排除对象是 主机/网络, 多个以英文逗号 "," 分开

> nmap -iL ./ips.txt -F -T4 **\--exclude 127.0.0.1** -v

###  **从文件列表中排除扫描主机：--excludefile <exclude_file>**

###  **⭐️**

从文件中排除列表,与`--exclude`类似，区别于该参数排除的对象是文件，而`--excludefile`排除的是IP,

> nmap -iL ./ips.txt -F -T4 **\--excludefile ./ips.txt** -v

###  **联机模式: -Pn**

###  **⭐️**

将所有主机视为联机--跳过主机发现

> nmap **-Pn** -v ./ips.txt

### 指扫描的端口：-PS/PA/PU/PY[portlist]

###  **⭐️**

-PS/PA/PU/PY是nmap的四种不同的扫描方式，用于选择不同的传输层协议和扫描方式。其中，

-PS表示TCP SYN扫描，

-PA表示TCP ACK扫描，

-PU表示TCP NULL扫描，

-PY表示TCP FIN扫描。

[portlist]表示要扫描的端口列表，

可以是一个端口号、一个端口范围或者一个端口列表。

例如：

>   * - **PS** <start>:<end>：扫描从<start>到<end>之间的TCP端口，以十进制表示。
>   * - **PU** <port>：扫描单个UDP端口<port>。
>   * - **PY** <portlist>：扫描<portlist>中指定的TCP端口，以空格分隔。
>

这些参数可以帮助nmap更精确地扫描目标主机的开放端口，从而帮助网络安全人员发现目标主机上的漏洞或弱点

> -PS/PA/PU/PY 与 -p 不同之处在于：
>
>  
>
>
> -p参数可以用于指定要扫描的TCP和UDP端口范围，而-PS/PA/PU/PY参数则用于选择不同的传输层协议和扫描方式。例如，使用-> p参数可以扫描从20到1000之间的TCP端口，而使用-PS参数可以扫描单个TCP SYN端口。
>
>  
>
>
> 另外，-p参数还可以用于指定要扫描的端口列表，它接受多个端口号或端口范围作为参数。例如，使用-p 21 23
> 53可以扫描FTP、Telnet和DNS服务，而使用-p 1-65535可以扫描所有开放的TCP和UDP端口。
>
>  
>
>
> 总之，-p参数用于指定要扫描的端口范围或端口列表，而-PS/PA/PU/PY参数用于选择不同的传输层协议和扫描方式。

### ICMP扫描：-PE/PP/PM

###  **⭐️**

在nmap中，参数-PE/PP/PM用于选择不同的ICMP（Internet Control Message Protocol）类型和扫描方式。

  * -PE：发送一个类型为ICMP Echo Request的包，即ping包。
  * -PP：发送一个类型为ICMP Timestamp Request的包。
  * -PM：发送一个类型为ICMP Address Mask Request的包。

这些参数可以帮助网络安全人员探测目标主机的网络可达性、时间戳或地址掩码信息。

使用例子：

>   * nmap - **PE** <target>：扫描目标主机，并发送ping包探测网络可达性。
>   * nmap - **PP** <target>：扫描目标主机，并发送时间戳请求包。
>   * nmap - **PM** <target>：扫描目标主机，并发送地址掩码请求包。
>

>
> 注意：在使用这些参数时，需要确保目标主机允许ICMP包通过防火墙，否则nmap将无法发送这些请求包

  

### 指定DNS服务器：--dns-servers <serv1[,serv2],...>

###  **⭐️**

指定使用哪个DNS服务器进行域名解析。这个参数可以帮助网络安全人员控制DNS解析的过程，以便更好地理解目标主机的网络结构和探测目标主机的开放端口。

这个参数可以帮助网络安全人员更好地控制nmap的扫描过程，提高扫描的准确性和效率。

>   * nmap -- **dns** <DNS server> <target>：指定使用特定的DNS服务器进行域名解析。
>   * nmap -- **dns** <domain> <target>：指定使用以域名作为DNS服务器的地址进行域名解析。
>

### 系统默认DNS解析扫描：--system-dns

###  **⭐️**

指定使用系统默认的DNS服务器进行域名解析。这个参数可以帮助网络安全人员快速地进行域名解析，以便更好地理解目标主机的网络结构和探测目标主机的开放端口。

这个参数可以帮助网络安全人员快速地开始nmap扫描，并提高扫描的效率。同时，它也可以减少手动配置DNS服务器的麻烦，提高扫描的便利性

> nmap -- **system-dns** <target>：使用系统默认的DNS服务器进行域名解析。

### 自定义TCP扫描标志：--scanflags

###  **⭐️**

指定要使用的TCP标志（flags）进行扫描。TCP标志是TCP协议中用于控制数据传输的一组标记，包括SYN、ACK、RST等。使用--scanflags参数可以帮助网络安全人员发现目标主机上开放的端口和可能存在的漏洞或弱点。

>   * nmap -- **scanflags** S,A <targetIP>：使用SYN和ACK标志进行扫描，即TCP SYN和TCP
> SYN+ACK扫描。
>   * nmap -- **scanflags** R <targetIP>：使用RST标志进行扫描，即TCP RST扫描。
>

这个参数可以帮助网络安全人员发现目标主机上开放的端口和可能存在的漏洞或弱点，并提供更精确的扫描结果。

### 排除端口扫描：--exclude-ports <port ranges>

###  **⭐️**

\--exclude-ports 参数用于排除指定端口扫描，其中:<port -ranges>是端口范围列表

> nmap **\--exclude-ports** 1-100

这个参数可以帮助网络安全人员排除端口扫描

### 连续端口扫描：-r

###  **⭐️**

-r参数用于连续端口扫描，例如1-100，端口将会递增进行连续扫描，1,2,3,4....直至100。不使用`-r`则扫描将会是随机的

> nmap **-r** <target IP>

这个参数可以帮助网络安全人员有序进行端口扫描

### 指定扫描常见的端口数：--top-ports <number>

###  **⭐️**

参数--top-ports用于指定要扫描的端口范围，默认情况下会扫描最常用的100个端口。使用--top-ports参数可以帮助网络安全人员快速地扫描目标主机上最常用的端口，并发现可能存在的漏洞或弱点。

>   * nmap **\--top-ports 50** <target>：扫描目标主机上最常用的50个端口。
>   * nmap **\--top-ports 1000** <target>：扫描目标主机上最常用的1000个端口
>

  

  

  

这个参数可以帮助网络安全人员快速地开始扫描目标主机的常用端口，并发现可能存在的漏洞或弱点。

  

### 指定扫描范围及算法：--port-ratio

###  **⭐️**

参数--port-ratio用于指定要扫描的端口范围和端口扫描算法。这个参数可以帮助网络安全人员更精确地扫描目标主机上的开放端口，并提供更详细的信息。

>   * nmap **\--port-ratio strict** <target>：使用严格的端口扫描算法扫描目标主机上的开放端口。
>   * nmap **\--port-ratio aggressive** <target>：使用积极的端口扫描算法扫描目标主机上的开放端口。
>

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的端口扫描算法，并提供更精确的扫描结果。

### 轻量级信息探测：--version-ligh

###  **⭐️**

参数--version-light用于指定轻量级的版本侦测方式。这种方式会尽量减少对目标主机的干扰，同时探测到的信息也会相对有限。

>  
>
>
>   * nmap **\--version-light** <target>：使用轻量级的版本侦测方式扫描目标主机上开放端口的相关版本信息。
>

这个参数可以帮助网络安全人员在不干扰目标主机的情况下，尽可能多地获取相关的版本信息。同时，这种方式也适用于对目标主机进行快速扫描。

### 使用脚本参数文件：--script-args-file=filename

###  **⭐️**

该参数--script-args-file=filename以文件形式加载脚本交互参数，在文件中提供NSE脚本参数

> nmap --script=xxx **\--script-args-file=args.txt** <target>: 脚本参数

这个参数可以帮助网络安全人员提供使用文件形式脚本参数进行交互

### 脚本执行显示： --script-trace

###  **⭐️**

该参数 --script-trace用于显示脚本执行信息，便于网络安全人员调试

> nmap --script=xxx --script-args-file=args.txt **\--script-trace**
> <target>:显示脚本信息

这个参数可以帮助网络安全人员提供显示脚本执行信息，便于网络安全人员进行调试查看

### 更新脚本数据库：--script-updatedb

###  **⭐️**

该参数--script-updatedb用于更新脚本数据库

> nmap **\--script-updatedb** <target>: 更新脚本数据库

这个参数可以帮助网络安全人员提供更新脚本数据库

### 指定主机组范围：--min-hostgroup/max-hostgroup

###  **⭐️**

参数--min-hostgroup和max-hostgroup用于指定主机组的范围。这些参数可以帮助网络安全人员更精确地控制要扫描的主机组范围，以便更好地理解目标主机的网络结构和探测可能存在的漏洞或弱点。

> nmap **\--min-hostgroup 10 --max-hostgroup 20**
> <target>：指定主机组范围为10到20，扫描目标主机上的开放端口和相关信息。

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的主机组范围，并提供更精确的扫描结果。同时，这种方式也可以减少对目标主机的干扰，提高扫描效率。

### 指定并行扫描范围：--min-parallelism/max-parallelism

### **⭐️**

参数--min-parallelism和max-parallelism用于指定并行扫描的范围。这些参数可以帮助网络安全人员更精确地控制要扫描的目标主机范围，以便更好地理解目标主机的网络结构和探测可能存在的漏洞或弱点。

> nmap **\--min-parallelism 10 --max-parallelism 200**
> <target>：指定并行扫描范围为10到200，扫描目标主机上的开放端口和相关信息。

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的并行扫描范围，并提供更精确的扫描结果。同时，这种方式也可以减少对目标主机的干扰，提高扫描效率。

### 指定扫描往返超时时间： --min-rtt-timeout/max-rtt-timeout/initial-rtt-timeout <time>

###  **⭐️**

参数--min-rtt-timeout、max-rtt-timeout和initial-rtt-timeout用于指定往返时延的超时时间。这些参数可以帮助网络安全人员更精确地控制nmap的扫描速度和准确性，以便更好地理解目标主机的网络结构和探测可能存在的漏洞或弱点。

其中花费时间＜time＞的选项以秒为单位，或附加“ms”（毫秒），“s”（秒）、“m”（分钟）或“h”（小时）的值（例如30m）。

> nmap **\--min-rtt-timeout 100ms --max-rtt-timeout 500ms --initial-rtt-> timeout 200ms**
> <target>：指定往返时延的超时时间为100毫秒到500毫秒，初始往返时延的超时时间为200毫秒，扫描目标主机上的开放端口和相关信息。

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的往返时延超时时间，并提供更精确的扫描结果。同时，这种方式也可以减少对目标主机的干扰，提高扫描效率。

### 限制扫描重试次数： --max-retries <tries>

### **⭐️**

该参数--max-retries限制端口扫描探测重新传输的次数，其中 <tries>代表重试次数。

> nmap **\--max-retries 5** <target>

这个参数可以帮助网络安全人员更快的请求得以回应

### 设置主机超时时间： --host-timeout <time>

###  **⭐️**

该参数 --host-timeout
<time>用于限制与主机扫描连接超时时间，其中花费时间＜time＞的选项以秒为单位，或附加“ms”（毫秒），“s”（秒）、“m”（分钟）或“h”（小时）的值（例如30m）。

> nmap **\--host-timeout 10s** <target>

这个参数可以帮助网络安全人员更快的请求得以回应

### 设置与主机扫描延时及最大延时时间：--scan-delay/--max-scan-delay <time>

###  **⭐️**

该参数--scan-delay/--max-scan-delay <time> 用于设置探测延时及最大延时时间,
其中花费时间＜time＞的选项以秒为单位，或附加“ms”（毫秒），“s”（秒）、“m”（分钟）或“h”（小时）的值（例如30m）。

> nmap **\--scan-delay 10s --max-scan-delay 30** <target>

这个参数可以帮助网络安全人员更快的请求得以回应及减少错误响应，提高隐蔽的探测

### 最小扫描速率： --min-rate <number>

###  **⭐️**

该参数 --min-rate <number> 用于限制最短的扫描时间，每秒发送数据包的速度不低于＜number＞

> nmap **\--min-rate 10** <target>

这个参数可以帮助网络安全人员更快的请求得以回应及减少错误响应，提高隐蔽的探测

### 最大扫描速率： --min-rate <number>

###  **⭐️**

该参数 --max-rate <number> 用于限制最短的扫描时间，每秒发送数据包的速度不超过＜number＞

> nmap **\--max-rate 10** <target>

这个参数可以帮助网络安全人员更快的请求得以回应及减少错误响应，提高隐蔽的探测

### 指定扫描包长度：-f; --mtu <val>

###  **⭐️**

参数-f和--mtu用于指定要扫描的包长度。这些参数可以帮助网络安全人员探测目标主机的网络层协议和包处理能力，以便更好地理解目标主机的网络结构和探测可能存在的漏洞或弱点。

>   * nmap **-f**
> <target>：将TCP和UDP段长度设置为536（IPv4）/1280（IPv6），以避免丢包和过滤器阻断，同时保持与目标主机的MTU（最大传输单元）匹配。
>   * nmap **\--mtu
> <val>**<target>：将TCP和UDP段长度设置为指定值，以避免丢包和过滤器阻断，同时保持与目标主机的MTU匹配。
>

这个参数可以帮助网络安全人员根据不同的扫描需求选择不同的包长度，并提供更精确的扫描结果。同时，这种方式也可以减少对目标主机的干扰，提高扫描效率。

### 指定decoy主机： -D <decoy1,decoy2[,ME],...>

###  **⭐️**

参数-D用于指定decoy主机。Decoy主机是一种用于伪装扫描真实主机位置的虚拟主机。使用decoy主机可以减少扫描活动被发现的风险。

> nmap **-D decoy1,decoy2,decoy3**
> <target>：将decoy1、decoy2和decoy3作为decoy主机，与目标主机一起扫描。

这个参数可以帮助网络安全人员在不暴露自己位置的情况下，进行更安全的网络扫描。

###

###  **⭐️**

该参数-oA用于同时以三种主要格式输出，其中<basename>为文件名

> nmap **-oA** output <target>

这些参数可以帮助网络安全人员根据不同的需求将扫描结果保存到不同的文件中，并进行进一步的分析和可视化。

### 输出主机接口和路由：--iflist

###  **⭐️**

这个参数--iflist用于主机接口和路由显示，用于调试

> nmap **\--iflist** <target> :用于主机接口和路由显示

  

这个参数可以帮助网络安全人员获取到数据包扫描主机接口和路由情况，便于调试。

### 追加输出文件：--append output

### **⭐️**

参数--append output用于在覆盖任何存在的文件时，将新的数据附加到文件的结尾处，而不是删除文件中的现有内容。

> nmap **\--append output <filename>**：将文本附加到指定的文件中，而不是删除文件中的现有内容。

这个参数常用于在文件中追加数据而不是覆盖原有数据，适用于需要保留原有数据并添加新数据的场景。

### 断点加载未完成的扫描：--resume＜filename＞

###  **⭐️**

参数--resume＜filename＞用于从指定的文件中加载未完成的扫描会话，并继续执行扫描。这个参数可以用于恢复之前中断或未完成的扫描会话

> nmap **\--resume＜filename＞** ：从指定的文件中加载未完成的扫描会话，并继续执行扫描。

这个参数可以帮助网络安全人员恢复之前中断或未完成的扫描会话，从而减少扫描时间和提高效率。

### 指定xml转换其他格式：--stylesheet <path/URL>（如CSV或SQLite）的XSLT样式表

###  **⭐️**

参数--stylesheet＜path/URL＞用于指定将Nmap XML结果转换为另一种格式（如CSV或SQLite）的XSLT样式表文件路径或URL。

> nmap **\--stylesheet** ＜path/URL＞＜target＞：将Nmap
> XML结果转换为另一种格式（如CSV或SQLite）的XSLT样式表文件路径或URL指定的格式。

这个参数可以帮助网络安全人员将Nmap XML扫描结果转换为其他格式，以便于进一步的分析和可视化。

### 引用 nmap.org样式表：--webxml

###  **⭐️**

参数--webxml用于指定一个参考样式表，该样式表通常来自Nmap.Org，用于将Nmap的XML输出转换为更可移植的XML格式。

> nmap **\--webxml** ＜target＞：将Nmap的XML输出转换为更可移植的XML格式。

这个参数可以帮助网络安全人员更好地理解Nmap的XML输出，并将其用于进一步的分析和可视化。

### 不使用样式表：--no-stylesheet

###  **⭐️**

\--no-stylesheet选项用于指定在将Nmap XML结果生成为HTML报告时不使用样式表。

> nmap **\--no-stylesheet** ＜path/URL＞＜target＞：将Nmap XML结果生成为HTML报告时不使用样式表。

这个选项可以帮助网络安全人员生成HTML报告，并在没有样式的情况下查看Nmap XML结果。这在需要自定义样式或对报告进行进一步修改和定制时非常有用。

### 指定数据文件：--datadir＜dirname＞

###  **⭐️**

\--datadir＜dirname＞选项用于指定nmap数据文件的目录。这些文件包含了nmap的脚本、插件、配置文件等数据。

> nmap **\--datadir＜dirname＞** ：指定nmap数据文件的目录为＜dirname＞

这个选项可以帮助网络安全人员在不干扰nmap默认数据文件的情况下，使用自己定制的数据文件进行扫描和其他操作。这在需要使用特定版本的脚本或插件时非常有用。

### 打印版本号：-V(大写英文字母：V)

###  **⭐️**

该参数用于打印namp版本信息，

> nmap **-V**

这个选项可以帮助网络安全人员查看当前使用的nmap版本

  

## 2.nmap script 使用

nmap内置600多个脚本，可以使用脚本扩展及利用。使其更符合自己的扫描方式。

Nmap不单单用于端口扫描，服务检测，本节将讲解Nmap强大的脚本引擎。

Nman Script是Nmap最好的功能之一，利用Nmap Script 可以快速的探测服务

其脚本官网文档：<https://nmap.org/nsedoc/>

## nmap 脚本目录

在Nmap安装目录，存在Script文件夹，在Script文件来中，存在许多以“.nse”后级结尾的文本文件，即Nmap自带的脚本引擎，并且你也可以自己编与Nmap
script。

Nmap Script实现许多不同的功能，其中包含漏洞扫描，漏洞利用，自录扫描等实用功能。

## 使用说明

使用Nmap脚本引擎，只需要添加命令 "--script=脚本名称〞即可。 使用脚本前，必须清楚该脚本是做什么的，否则乱使用得不到预想的结果。

  

例如:

使用脚本：[http-php-version](https://nmap.org/nsedoc/scripts/http-php-version.html
"http-php-version")

脚本介绍：

尝试从web服务器检索PHP版本。PHP有许多神奇的查询，它们返回的图像或文本可能因PHP版本而异。

在命令行中输入：

> nmap **\--script=http-php-version** -v -sV 127.0.0.1

回车运行，等待执行结果即可。

  

脚本也可以使用泛式形式写法，如使用全部http开头的脚本，则写法：

> nmap **\--script=http-*** -v -sV 127.0.0.1

该命令将会查找脚本中包含 **`http-`** 开头的脚本进行运行。

  

  

-end-
