**上周六在拉斯维加斯举行的Defcon2019极客大会上Gordon Lyon宣布Nmap 发布新版本7.80。该版本主要包括了全新Npcap
Windows数据包捕获驱动程序更新以及80多项NSE脚本和库等更新。本文虫虫就带大家一起学习Nmap7.8带来的更新和改善。**

## Npcap更新

熟悉Nmap的同学都知道，Nmap套件中有一个Windows数据抓包程序Npcap，主要用于Windows数据包嗅探和发送。包括大名鼎鼎的抓包程序Wireshark底层现在也用的是Npcap。

此前版本的Npcap主要基于Winpcap（2013停更），并通过Microsoft Light-Weight Filter (NDIS 6
LWF)技术和Windows Filtering Platform (NDIS 6 WFP)对其改进和性能提高。

![nmap1.png](https://image.3001.net/images/20190815/1565866253_5d55390d6fa45.png!small)

Npcap开源项目源于2013年由Nmap创始人Gordon Lyon和北京大学罗杨博士发起，并由Google Summer of
Code计划赞助，以MIT协议发布。由于Winpcap已经停止更新，Npcap通过底层开发构建了全新自己的Npcap原始数据包捕获/发送驱动程序，在兼容WinpcapAPI的基础上，使用更加现代API接口，在功能、性能、安全性方面都完胜老版本。

此次更新迭代了15个版本的Npcap更新，Npcap最新版本为0.9982。

![nmap2.png](https://image.3001.net/images/20190815/1565866280_5d55392852341.png!small)

## NSE改进

NSE(Nmap scripting
Engine)是Nmap提供的扩展脚本执行引擎的脚本。可以通过NSE执行脚本进行渗透测试。NSE支持的脚本使用Lua编程语言，具有简单快捷高效的特点。如果说Nmap是最优秀的扫描器的话，那么加上NSE我们可以说Nmap就是一款集网络发现、指纹版本探测、脆弱性探测、漏洞利用等功能的全功能安全平台。

除了Npcap，Nmap 7.8还带来了80多个各种更新和改善，其中包括11个新的NSE脚本，一堆新的库，错误修复和性能改进。

### 新增脚本和库

新增11个NSE脚本后，NSE脚本总有598个，此次新增加的脚本有：

>  **broadcast-hid-discoveryd** ：用于发现局域网上通过发送网络广播探测的发现HID设备。 [Brendan Coles]  
>
>
>  **broadcast-jenkins-discove** ：用于在局域网上通过发送发现广播探测发现Jenkins服务器。 [Brendan
> Coles]
>
>  **http-hp-ilo-info** ：用于从HP Integrated Lights-Out（iLO）服务器中提取信息。
> [rajeevrmenon97]
>
>  **http-sap-netweaver-leak** ：用于从其开启匿名访问知识管理单元的匿名访问探测SAP Netweaver
> Portal。[ArphanetX]
>
>  **https-redirect** ：用于探测HTTPS网站重定向到同口的HTTP服务器。一些nginx服务器执行此操作，使ssl-*脚本失效。
> [Daniel Miller]
>
>  **lu-enum** ：用于枚举TN3270E服务器的逻辑单元（LU）。[Soldier of Fortran]
>
>  **rdp-ntlm-info** ：用于从RDP服务中提取Windows域信息。 [Tom Sellers]
>
>  **smb-vuln-webexec** ：用于检查是否安装WebExService，是否允许代码执行。 [Ron Bowes]
>
>  **smb-webexec-exploit** ：通过SYSTEM权限WebExService来运行任意命令。[RonBowes]
>
>  **ubiquiti-discovery** ：利用Ubiquiti发现服务和协助版本检测来提取信息。[om Sellers]
>
> 利用Nmap服务和应用程序版本检测的 **CPE信息调用** 查询CVE漏洞数据库API接口。[GMedian，Daniel Miller]
>
>  **stringaux.lua** **，** 字符串库。字符串处理函数收集本打包到了该新库。
>
>  **rand.lua** ，随机库。使用系统上最好的随机源来生成随机字串rand.lua库使用最好的随机源。
>
>  **oops.lua** **，** 调试信息库。新的库使错误报告变得容易，显示必要时调试细节，拒绝杂乱的情况下。 ****
>
> **tableaux.lua** **，** 新的实用表操作和搜索的函数库。 ****
>
>  **knx.lua** ，新的KNX/Konnex库。包含KNX/Konnex设备通信常用的函数和定义。

### 其他NSE功能和改善

>  **HTTP** **库，** 新版本响应正文（response
> body）对gzip编码提供透明支持。对响应正文强制执行大小限制。可以使用脚本调整默认限制参数，适用于所有脚本，可使用HTTP请求选项重设各个参数。
>
> HTTP响应解析器现在可以无理由地容忍状态短语，它改善了与某些HTTP服务器的兼容性。
>
> 脚本XML输出中支持CR字符，不再被视为非法。
>
>  **rdp-enum-encryption** **，** 添加对TLS支持。
> 允许针对需要TLS的服务器确定协议版本，并为某些NLA/CredSSP信息收集奠定基础工作。
>
>  **http-enum** 库，避免破坏指纹信息中“严重级”和“ignore_404”值。没有标准指纹使用这些字段。 [Kostas Milonas]
>
> 更新mongodb脚本的执行规则，使其支持非常用端口（非27017）上运行的实例。
>
> 更新 **TN3270.lua** 并添加参数以禁用TN3270E。
>
> 更新了 **ftp-syst** 脚本，以防止潜在死循环bug。
>
>  **HTTP Set-Cookie** 头的解析器现在更符合RFC
> 6265：对空属性容错；对cookie和/或属性值中的双引号被作为字符处理；对空值和无值属性的被解析为等值；忽略名为“name”或“value”的属性。
>
> 从ODVA列表中更新 **enip-info** 供应商。
>
> 脚本 **http-sql-injection** 添加两个可以改善MySQL检测的常见错误字符串。
>
> 脚本 **http-default-accounts**
> 新支持选择多个指纹类别。也可以按名称选择指纹，支持非常具体的扫描。只支持不超过一个目标主机/端口运行。
>
> 增加选项 **http-host** 允许用户强制所有HTTP请求中Host头的host值。
>
>  **smtp.domain** 脚本，改用arg或目标域名，用于替换STARTTLS的EHLO命令中的exampledotcom。
>
>  **dns.lua** 中对edns-client-subnet（ECS）的支持已得到改进，包括：
>
> 使用符合RFC 7871的ECS代码；按照RFC7871的要求正确修剪ECS地址；修复了阻止使用相同ECS选项表的错误。
>
>  **tls.lua** 如果协议版本是SSLv3，则在创建client_hello消息时只使用SSLv3记录层。
> 某些TLS实现不会与提供低于TLSv1.0的客户端进行握手。 脚本必须手动回退到SSLv3才能与SLv3服务器通信 ****
>
>  **vulns.lua** 中的新漏洞状态UNKNOWN用于表示测试无法排除漏洞。
>
> **tn3270.lua** 添加TN3270E支持和其他改进并更新tn3270-screen.nse以显示新内容设置。
>
>  **enip-info.nse** ，更新产品代码并添加检查响应长度。该脚本现在使用string.unpack为底层库。

### Bug修复

> 解决rdp-enum-encryption中的两个协议解析问题以及RDP nse库在Windows XP下扫描中断。并澄清了协议类型。
>
> 解决了 **http-fileupload-exploiter，** 非从特定目录执行脚本时无法找到其资源文件的bug。
>
> 修复 **SSH NSE** 脚本在非SSH服务运行时，由两次释放libssh2会话数据引起的崩溃。
>
> 修复 **NTLM** 测试，目标提供为域名时候导致脚本不遵守smbdomain -arg选项的逻辑错误。
>
> 修复 **http-grep.match** 的参数选项解析的bug。
>
> 修复http-vuln-cve2006-3392中阻止脚本正确生成漏洞报告的bug。
>
> 修复NSE库TN3270中的与屏幕渲染相关的bug。此补丁还改进了暴力脚本 **tso-brute。**
>
> 修复SIP，SASL和HTTP摘要认证当算法中包含小写字符的bug。
>
> 修复了 **brute.lua** 的BruteSocket包装器，由于套接字混淆而导致Nmap崩溃：nmap:nse_nsock.cc:672:
> int receive_buf(lua_State*, int,
>
> lua_KContext):Assertion`lua_gettop(L) == 7' failed.
>
> 修复由于IPS关闭连接导致的 **smb-vuln-ms17-010** 错误。
>
> 修复 **ssl-ccs-injectio**
> n中的一些假阳性条件，导致一些漏洞被错误的标记为使用致命警报而不是“unexpectedmessage”。
>
> 修复脚本 **traceroute-geolocation** 由于GeoPlugin返回空坐标时崩溃的bug。
>
> 修复脚本 **http-phpmyadmin-dir-traversal** 中的对任何POST请求URI的响应码200的误报的bug。
>
> 修复对非SSH服务使用SSH脚本导致的崩溃（double-free）。

### 功能删除

> 从脚本中删除了 _OSVDB引用_ ，并尽可能用BID引用替换它们。
>
>  _bin.lua_ **，** 已被正式弃用。2年前Nmap7.25BETA2增加添加了Lua
> 5.3，通过string.pack和string.unpack提供本地支持二进制数据打包。所有现有脚本和库都已更新。
>
>  _bit.lua_ ，完全删除。它的所有功能都通过原生Lua按位运算取代，arshift（算术移位）转移到 **bits.lua** 库。
>
>  _hostmap-ip2hosts.nse_ ，被删除。API已经失效，该服务于2019年2月17日完全关闭。

## Ncat更新

NcatNmap项目套件中又一个功能丰富支持多平台的网络实用程序，具有“网络瑞士军刀“之称，支持从命令行跨网络读取和写入数据。Ncat最初是用来支持Nmap而开发的，是对古老的Netcat重新实现的一个大大改进。它使用TCP和UDP进行通信，旨在成为可靠的后端工具，可为其他应用程序和用户提供网络连接。
Ncat不仅可以使用IPv4和IPv6，还可以为用户提供几乎无限的潜在用途。

![nmap3.png](https://image.3001.net/images/20190815/1565866366_5d55397e537f9.png!small)  

Nmap7.8中队Ncat的更新主要如下：

> 1、在Socket允许的情况下，允许Ncat连接服务器的0端口。 、
>
> 2、为了避免混淆并支持非默认代理端口，选项--proxy需要用方括号表示法指3、定IPv6地址，例如--proxy
> [2001:db8::123]:456。
>
> 4、新的ncat选项--proxy-dns控制代理目标由远程代理服务器解析还是由本地解析。可通过--proxy-dns选项设置。
>
> 5、临时RSA密钥更新为2048位，用于解决配置了安全级别2的OpenSSL库的兼容性问题，比如在Debian或Kali操作系统时候导致的问题。
>
> 6、将AF_VSOCK（Linux VM套接字）功能添加到Nsock和Ncat。Linux VM套接字用于虚拟机和虚拟机管理程序之间的通信。
>
> 7、修复Windows上Ncat -e时候导致的提前终止连接的问题。
>
> 8、修复了在Windows上使用-e或-c选项时启动的命令的通信，尤其是在使用—ssl情况下。
>
> 9、修复了通过HTTP代理连接的IPv6 URL文本格式。

## Zenmap更新

Zenmap
Nmap套件中的跨平台图形UI界面软件。Zenmap是用Python语言编写的开源免费的图形界面，支持不同操作系统，包括Windows/Linux/Unix/Mac
OS等。

![nmap4.png](https://image.3001.net/images/20190815/1565866390_5d553996838da.png!small)  

Zenmap旨在为用户nmap提供更加简单的操作方式。简单常用的操作命令可以保存成为profile，然后用户扫描时选择通过profile即可复用，可以方便地比较不同的扫描结果。

namp 7.8新版本中Zenmap主要修复了以下bug：

> 修复了无法找到Nmap可执行文件且系统PATH包含非UTF-8字节的崩溃，比如Windows上。
>
> 修复使用dir时由于结果搜索导致的崩溃：operator: AttributeError:'SearchDB' object has no
> attribute 'match_dir'
>
> 修复recent_scans.txt不可写时导致崩溃。
>
> 虫虫在Window 10下测试中发现以前好用快速多了，以前扫时候常死掉。

## 其他功能和安全更新

> 修复 **CVE-2019-1552** 漏洞。通过对OpenSSL的地址添加"C:\Program Files
> (x86)\Nmap\OpenSSL"前缀，预防未经授权的用户通过编写修改OpenSSL默认值配置到此目录。
>
> 修复 **CVE-2018-15173** 漏洞。通过减少LibPCRE资源限制，以便版本检测不能使用过多的堆栈。
> 此前，Nmap在低内存系统上运行时可能会因故意或意外难以匹配的目标服务而崩溃。。
>
> 允许使用冗长的命令行恢复nmap扫描。
>
> 修复遇到无效输入时，RMI解析器可能会崩溃的bug。
>
> 新版中使用 **pcap_create**
> 而非pcap_live_open，并在pcap描述符上设置即刻模式。解决了Linux上的数据包丢失问题，并能提高在其他平台上的性能。
>
> 针对adb的新服务probe和行匹配。AndroidDebug Bridge，允许远程执行代码，并在许多设备上是默认启用的。
>
> 修复由于Nmap使用未知的TCP选项，可能会导致忽略TCP响应数据包，从而使得验证失败的bug。
>
> 避免在DTLS连接期间发生错误时尝试重新连接SSLv2，解决由此导致的崩溃。
>
> 避免由于收到ARP或ND响应后由于匹配probe而导致的延迟。
>
> 支持Ubiquiti
> Discovery协议的v1和v2的新服务probe和规则配置的支持。设备通常会使相关服务保持开放状态，这会暴露大量信息，并可能被用于DdoS攻击的。并增加了针对v1协议的新nmap-> payload条目。
>
> 在搜索Lua头文件时，通过实际使用的目录，而不是不是强制搜索/usr/include。
>
> -v，-v详细级别限制为最多10级， Nmap内部也不在使用更高级别。
>
> 第一次probe发送到主机时启动主机超时时钟，主机组启动时就启动。有时，主机直到主机组的末端才会获得probe，从而导致超时的可能。
>
> 对Nmap的生日公告进行紧急修复，使Nmap在2018年9月1日以详细模式（-v选项）祝愿自己成为“21岁生日快乐”，而不是之前的“快乐21日”。
>
> -PR选项被弃用。并且禁用。在主机发现扫描时候，ARP ping已经在可能使用地方默认启用，而不能使用场合下-PR没有任何效果。

## 下载安装

nmap的安装也比较简单，官方提供了Linux
RPM，Mac和Windows的二进制安装包，可以直接下载安装。下载地址为：<https://nmap.org/download.html>  

### Window

直接从官方下载页,下载:nmap-7.80-setup.exe，下载URL为：

<https://nmap.org/dist/nmap-7.80-setup.exe>，

下载后点击安装即可：

![nmap5.png](https://image.3001.net/images/20190815/1565866633_5d553a8992432.png!small)

安装步骤中会提示使用全新的Npcap版本，用WinPcpAPI兼容模式，该选项会卸载WinPcp。

![nmap6.png](https://image.3001.net/images/20190815/1565866647_5d553a978d58d.png!small)

### Mac

直接从官方下载页下载 **nmap-7.80.dmg** ，其下载URL为：

> <https://nmap.org/dist/nmap-7.80.dmg>  
>

下载后，打开安装包安装即可：

![nmap7.png](https://image.3001.net/images/20190815/1565866666_5d553aaa534d2.png!small)

### Linux二进制安装

支持RPM包的Redhat, Mandrake, Suse,等linux可以直接下载官方的二进制RPM安装包安装。

> rpm -vhU <https://nmap.org/dist/nmap-7.80-1.x86_64.rpm>
>
> rpm -vhU <https://nmap.org/dist/zenmap-7.80-1.noarch.rpm>
>
> rpm -vhU <https://nmap.org/dist/ncat-7.80-1.x86_64.rpm>
>
> rpm -vhU <https://nmap.org/dist/nping-0.7.80-1.x86_64.rpm>

### 源码安装

没有提供二进制安装包的平台，可以使用源码安装方式手动安装。

先从官方下载页下载源码包，下载URL为：

> <https://nmap.org/dist/nmap-7.80.tar.bz2>

注意，也可以从nmap的官方Github克隆源码仓库:

> git clone <https://github.com/nmap/nmap>  
>
>
> bzip2 -cd nmap-7.80.tar.bz2 | tar xvf ->
> cd nmap-7.80
>
> ./configure
>
> make

![nmap8.png](https://image.3001.net/images/20190815/1565866966_5d553bd68e03c.png!small)

make install

注意如果你系统比较新，可能缺少组件，需要先安装这些组件，比如在Ubuntu下安装时候，需要安装gcc，make,g++等,可直接用下面命令安装

apt install gcc make g++ flex bison

好了，新版本就这样完成安装了，接下来就可以美美体验了。

有关Nmap的更多使用技巧可以参考官方文档、搜索引擎及freebuf的精品文章，此处略。  

