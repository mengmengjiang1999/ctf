# CVE-2018-0101 Cisco ASA 拒绝服务&远程代码执行漏洞分析

阅读量 **293987**

|评论 **4**

发布时间 : 2018-03-19 16:03:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0151f208f9a86f1f6d.jpg)

## 0x00漏洞背景

2018年1月29日，思科公开了旗下ASA防火墙设备的拒绝服务&远程代码执行漏洞（CVE-2018-0101），并在2月期间多次对公开信息进行修改和更新。在思科更新漏洞相关信息期间，该漏洞也有更多信息被披露出来，其中包括漏洞发现者——NCC
Group研究人员Cedric Halbronn关于漏洞细节的更多信息和安全研究者根据相关资料完成的PoC代码（拒绝服务部分）。

从已经公开的资料来看，该漏洞影响多个版本的思科安全产品和软件。同时，受影响的系统需在网络设备端口上开启SSL服务或IKEv2
VPN服务。如果该漏洞被成功利用，将导致远程设备内存破坏，造成设备重启或拒绝服务，甚至允许攻击者在无需用户验证的情况下实现远程代码执行，进而远程控制设备并产生进一步的攻击行为。本文出于探究漏洞技术原理，了解此类网络设备漏洞分析调试方法的目的，从ASA设备解析XML数据包的过程入手，分析该漏洞产生的原因，并将部分技术细节予以呈现。

## 0x01 漏洞简要介绍

####  1. 漏洞原理

CVE-2018-0101漏洞存在于思科ASA设备的XML解析器处理XML数据包时的分配和释放内存的过程当中，是一个Double
Free漏洞，攻击者可以通过发送精心构造的SSL 协议的HTTP
XML数据包来完成对受漏洞影响系统的攻击。当漏洞触发时，可导致系统崩溃重载，ASA设备停止接受VPN验证请求，或允许攻击者远程执行代码，获得对系统的控制。

####  2. 漏洞影响范围和脆弱性配置信息

思科官方在最初的公开信息中声称：多个版本的ASA和下一代防火墙平台受漏洞影响，且受影响设备需要配置启用WebVPN功能，并允许用户访问。由于发现了新的攻击向量，思科官方在2月份数次更新了安全公告，并在更新中将开通SSL
VPN的说法引申为“Secure Socket Layer (SSL) services or IKEv2 Remote Access VPN
services”。更新后的受漏洞影响设备和软件列表如下所示：

Ø 3000 Series Industrial Security Appliance (ISA)

Ø ASA 5500 Series Adaptive Security Appliances

Ø ASA 5500-X Series Next-Generation Firewalls

Ø ASA Services Module for Cisco Catalyst 6500 Series Switches and Cisco 7600
Series Routers

Ø ASA 1000V Cloud Firewall

Ø Adaptive Security Virtual Appliance (ASAv)

Ø Firepower 2100 Series Security Appliance

Ø Firepower 4110 Security Appliance

Ø Firepower 4120 Security Appliance

Ø Firepower 4140 Security Appliance

Ø Firepower 4150 Security Appliance

Ø Firepower 9300 ASA Security Module

Ø Firepower Threat Defense Software (FTD)

Ø FTD Virtual (FTDv)

其中，Cisco ASA中易受攻击的功能列表和配置信息如下所示：

在上图的信息中：

1. ASDM仅受http 命令配置列表范围的IP攻击影响；

2. Cisco Security Manager仅受http 命令配置列表范围的IP攻击影响；

3. MDM 9.3.1以上版本受上述配置影响；

4. 其他API 9.3.2以上版本受上述配置，且仅受http 命令配置列表范围的IP攻击影响；；

5. SAML SSO 9.6以上版本受上述配置影响。

FTD软件中易受攻击的功能和配置信息如下所示：

我们可以看到，上图中的配置信息，均与Web VPN的配置有关。

####  3. 修复方案

由于在1月29日发布报告后发现了新的攻击向量，所以Cisco官方在2月份的后续更新中，对固件升级的版本信息做了变更，细节参见Cisco官方关于CVE-2018-0101的说明。版本升级建议如下：

**Cisco ASA** **列表：**

**Cisco FTD** **列表：**

****

## 0x02 调试环境准备

####  1. 调试环境信息

如果没有ASA设备，需要通过搭建模拟调试环境并修改固件来完成调试的前期准备，具体思路就是GNS3 + Qemu +
修改后的系统固件；对于有真机作为调试环境的情况而言，则可直接修改固件，使之进入调试模式，并将其刷入ASA设备，然后在终端设备启用gdb，并通过串口连接远程gdbserver，即可完成调试前的准备工作。在上述两种方案中，本文使用Cisco
ASA 5505 series + ASA924-k8.bin + Ubuntu 16.04-3 amd64作为调试环境，完成了漏洞的调试过程。

以下是调试设备软、硬件信息：

设备名称

|

ASA-5505  
  
---|---  
  
硬件信息

|

AMD Geode (x86)  
  
Marvell 88E6095 Gigabit Ethernet Switch  
  
软件信息

|

ASA924-k8.bin  
  
Linux 2.6.29.6  
  
lina 9.2.4  
  
####  2. WebVPN配置

Cisco SSL VPN有三种模式：Clientless SSL VPN、Thin-Client VPN 和SSL VPN
Client。经过实际测试，Clientless SSL VPN 无法正常接收POC脚本发送的数据包，所以需要在ASA设备安装SVC（SSL VPN
Client），并根据客户端的类型调整POC代码的‘X-AnyConnect-Platform’字段，使之与SVC类型相适配。另外，如果WebVPN加密套件选择不当，也会因为加密算法强度不够而导致某些高版本操作系统无法成功连接WebVPN。

####  3. 固件修改和刷写

关于Cisco ASA设备的启动流程，我们在《揭开思科ASA防火墙网络军火的面纱
（上）》一文中已进行过相关梳理。在ASA的linux系统中，lina进程是由lina_monitor以子进程的方式启动并进行管控的，启动流程通过rcS脚本的参数控制。所以，使ASA进入调试模式的大致思路即为通过修改固件改变lina的启动流程。需要注意的是，固件修改完毕后，如果没有cf卡刷写固件，则需要在上传固件时绕过校验。

## 0x03 漏洞分析

####  1. POC代码分析

根据Cedric Halbronn对漏洞信息的说明，拒绝服务部分的POC代码已经公开。该代码由python编写，核心代码如下：

    
    
    headers = {}
    
    headers['User-Agent'] = 'Open AnyConnect VPN Agent v7.08-265-gae481214-dirty'
    
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    headers['X-Aggregate-Auth'] = '1'
    
    headers['X-Transcend-Version'] = '1'
    
    headers['Accept-Encoding'] = 'identity'
    
    headers['Accept'] = '*/*'
    
    headers['X-AnyConnect-Platform'] = 'linux-64'
    
    headers['X-Support-HTTP-Auth'] = 'false'
    
    headers['X-Pad'] = '0000000000000000000000000000000000000000'
    
     
    
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    
    <config-auth client="a" type="a" aggregate-auth-version="a">
    
        <host-scan-reply>A</host-scan-reply> #方便调试字符串改为flagflag
    
    </config-auth>
    
    """
    
    r = requests.post(sys.argv[1], data = xml, headers = headers, verify=False, allow_redirects=False)

这段代码的功能就是通过构造WebVPN请求的头部和特定格式的数据，向目标连续发送post请求，并使目标WebVPN拒绝服务。其中，XML格式数据中<host-scan-reply>标签的内容即为漏洞触发时内存块中保存的内容。

####  2. POC代码测试

连续两次运行POC脚本代码，第一次发送成功，http特征码200。第二次发送同样的数据包时，ASA崩溃并重启。系统反馈的内存崩溃的信息如下所示：

####  3. 漏洞代码静态分析

结合动态调试崩溃时的相关信息，通过排查系统堆栈，并尝试不同的断点进行调试，最后确定有漏洞的函数为sub_994E660。sub_994E660函数是ASA解析XML数据包并进行回复数据包的整个流程。在这个流程中，通过调用sub_807ECE0来完成对XML的解析。由于调试的固件中并没有符号表，所以下图中显示的是人工分析后修改的函数名。

上图的代码显示：开发人员是采用类似expat XML解释器的方法对XML进行解析的，而红框标注的部分表明开发人员是通过回调函数的方式来解析XML数据。

上图为aggregatexmldatahandler函数的部分代码。根据注释可以看到，代码在开始会判断要解析的XML
tag是否为”host_scan_reply”，如果是则读取全局变量0xA38E4F8的值。根据分析，该变量用来保存解”host_scan_reply”标签内容时所申请的内存块的指针。当指针指向的内存区域中存有字符串时，将进行Strncat操作，反之则重新申请内存用来存放XML解析出的内容。如下图所示：

XML数据解析完毕，并产生相应的反馈后，系统会释放此前申请的内存，代码如下所示：

……

以上就是ASA处理WebVPN请求中解析XML数据的流程。在该流程中，虽然开发人员在流程的末端释放了在堆中申请的内存，但是有一个全局变量保存了申请内存的指针。同时，考虑到ASA是一个linux系统之上运行的软件，参考Linux系统glibc内存管理机制，在内存块被释放后，并不会立即被OS回收，而是要进行合并操作。合并操作之前也要判断chunk的大小是否大于FASTBIN_CONSOLIDATION_THRESHOLD（默认为64KB），当条件符合时才会进行FASTBIN的合并操作，并将FASTBIN置为空。通过数次调试，我们认为ASA的内存管理机制与glibc存在类似之处，在ASA再次接受解析XML数据的请求时，上一次相同流程中申请的内存指针被全局变量保存，且该内存区域可能存有数据。当该内存区域中的数据没有被置空时，代码流程就会选择直接在内存区域将新解析的数据在以Strncat的形式写入内存区域，在流程末端的free操作中，两次释放同一chunk，造成double
free。

####  4. 动态调试

启动修改完成的系统固件，并在host端用gdb连接gdbserver并将watchdog复位。设置相应断点后运行程序，待ASA可以ping通后运行POC代码，此时代码断在0x0807D840，也就是上文提到的aggregatexmldatahandler函数。两个参数分别为xml_parser类型的userdata和指向XML数据的指针。当解析的标签为host_scan_reply时，两个参数的内容如下：

结合静态代码来看，此时*(userdata + 4) 的值是0xd，代码获取了0xA3BE4F8地址的值，这个全局变量被初始化为0。

所以此时堆中并没有申请内存用来保存XML数据 ，代码进入malloc分支，申请大小为0x2000的缓冲区。

XML数据（为了方便查找内存，POC代码中相应的字符串被换成flagflag）写入buffer后，查看内存和全局变量的值，如下所示：

XML解析完毕后调用aggregateAuthFreeParserDataOutMem，释放此前申请的内存，然后生成用于反馈请求的报文。free()函数释放相应的内存后，内存块中仍存有”flagflag”字符串。

第二次运行POC代码时，还是相同的流程。但是不同的是，此时全局变量中保存的值，是第一次解析XML数据包时申请的内存指针，也就是0xc85b5648。在通过strlen（）求得此时buffer中仍有字符串flagflag。

所以根据流程，当buffer中有字符串时，直接调用Strncat函数，拼接字符串。

然后和第一次解析XML的流程相同，释放内存并生成用于反馈的报文。

在代码调用free()释放内存后，这块缓冲区就会由于两次释放而造成Double Free，导致系统崩溃。至此，漏洞触发的原因和过程分析完毕。

##

## 0x04 总结

NCC Group公开的资料提供了一部分关于利用漏洞完成远程代码执行的思路。目前，对相关信息的理解是：攻击者可以利用IKE
v1协议的分片重组过程灵活地控制会话报文，通过调整内存布局，构造出可以跳转到shellcode区域的指令，并在空闲Chunk的Unlink操作时，将指令覆盖函数指针，进而达到远程代码执行的效果。至于不依赖IKE协议进行漏洞利用的方法，则需要在弄清Cisco
ASA的内存管理机制后才能实现。

由于在2016年8月，Shadow Brokers 公开了方程式组织针对思科ASA系列全套的攻击和利用框架（参见《8月19日：Shadow-Brokers所泄露文件的介绍、技术分析（上）》），一旦该漏洞被成功利用造成远程代码执行，则可配合其他工具和套件，实现对网络设备的管理控制，并完成更深层次的攻击活动。

据漏洞作者分析，思科从2011年起支持AnyConnect HOST SCAN模块开始，该漏洞可能已存在达七年之久。思科的SSL
VPN网络安全产品一直有高的市场占有率，该漏洞是在继CVE-2016-1287
IKE协议堆溢出远程代码执行漏洞后，最新公开的无需任何认证条件，即可实现突破企业网络边界的远程代码执行漏洞。虽然截至目前，还没有可以远程代码执行的漏洞利用公开，但对众多的思科ASA防火墙产品及SSL
VPN用户而言，即使仅造成设备拒绝服务，也会对线上生产环境产生较大影响。所以，相关运维人员应及早修复漏洞，跟进思科官方的最新补丁，以避免ASA设备遭受漏洞攻击。

## 参考链接

[https://www.anquanke.com/post/id/84614](../post/id/84614)

[https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20180129-ASA1](https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20180129-asa1)

[https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/september/cisco-ASA-series-part-one-intro-to-the-cisco-ASA/](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/september/cisco-asa-series-part-one-intro-to-the-cisco-asa/)

<http://www.freebuf.com/articles/system/114741.html>

[https://www.nccgroup.trust/globalassets/newsroom/uk/events/2018/02/reconbrx2018-robin-hood-vs-cisco-ASA.pdf](https://www.nccgroup.trust/globalassets/newsroom/uk/events/2018/02/reconbrx2018-robin-hood-vs-cisco-asa.pdf)

[https://www.anquanke.com/post/id/84419](../post/id/84419)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360 MeshFire Team** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/101446](/post/id/101446)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [RCE](/tag/RCE)
  * [cisco](/tag/cisco)
  * [远程代码执行](/tag/远程代码执行)
  * [asa](/tag/asa)
  * [DoS](/tag/DoS)
  * [FTD](/tag/FTD)
  * [CISCO ASA拒绝服务](/tag/CISCO ASA拒绝服务)
  * [CISCO ASA远程代码执行](/tag/CISCO ASA远程代码执行)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t01b22d45fef232c21b.png) 360 MeshFire Team

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

