## 0x00简介

CVE-2020-16898，当Windows TCP/IP堆栈不正确地处理ICMPv6 Router
Advertisement数据包时，存在一个远程执行代码漏洞。成功利用此漏洞的攻击者可以获得在目标服务器或客户端上执行代码的能力。要利用此漏洞，攻击者必须将经过特殊设计的ICMPv6
Router Advertisement数据包发送到远程Windows计算机上。

## 0x01漏洞描述

远程攻击者通过构造特制的ICMPv6 Router
Advertisement（路由通告）数据包，并将其发送到远程Windows主机上，即可在目标主机上执行任意代码。

攻击者可以利用该漏洞发送恶意制作的数据包，从而有可能在远程系统上执行任意代码。与MAPP（Microsoft Active
Protection计划）成员共享的概念证明既非常简单又非常可靠。它会导致立即出现BSOD（蓝屏死机），但更严重的是，对于那些能够绕过Windows
10和Windows Server
2019缓解措施的人来说，存在被利用的可能性。可以使远程代码执行的漏洞利用的影响将是广泛的，并且影响很大，因为这种类型的错误可能会变成可感染的。

  

## 0x02受影响版本

Windows 10 Version 1709 for 32-bit Systems

Windows 10 Version 1709 for ARM64-based Systems

Windows 10 Version 1709 for x64-based Systems

Windows 10 Version 1803 for 32-bit Systems

Windows 10 Version 1803 for ARM64-based Systems

Windows 10 Version 1803 for x64-based Systems

Windows 10 Version 1809 for 32-bit Systems

Windows 10 Version 1809 for ARM64-based Systems

Windows 10 Version 1809 for x64-based Systems

Windows 10 Version 1903 for 32-bit Systems

Windows 10 Version 1903 for ARM64-based Systems

Windows 10 Version 1903 for x64-based Systems

Windows 10 Version 1909 for 32-bit Systems

Windows 10 Version 1909 for ARM64-based Systems

Windows 10 Version 1909 for x64-based Systems

Windows 10 Version 2004 for 32-bit Systems

Windows 10 Version 2004 for ARM64-based Systems

Windows 10 Version 2004 for x64-based Systems

Windows Server 2019

Windows Server 2019 (Server Core installation)

Windows Server, version 1903 (Server Core installation)

Windows Server, version 1909 (Server Core installation)

Windows Server, version 2004 (Server Core installation)

  

## 0x03 环境搭建

网络环境开启ipv6支持。这里使用vmware，NAT出一个子网，并开启ipv6支持。点击VM的编辑--->虚拟网络编辑器，选择NAT模式，开启ipv6支持，点击确定，如下图。

![](https://image.3001.net/images/20201106/1604624361_5fa49fe9b900f1a432d65.png!small)

  

选取一个受影响版本的windows10镜像，安装在虚拟机里。

这里我使用的是1709版本：

![](https://image.3001.net/images/20201106/1604624379_5fa49ffb538493ea8fd3a.png!small)

  

打开win10的控制面板-->选择网络和共享中心，右键打开Ethernet0

![](https://image.3001.net/images/20201106/1604624389_5fa4a005b379e324e24e5.png!small)

  

打开ipv6版本：

![](https://image.3001.net/images/20201106/1604624402_5fa4a01232f7521ba838e.png!small)

  

## 0x04漏洞复现

1.执行ipconfig，查看IPv6地址：

![](https://image.3001.net/images/20201106/1604624415_5fa4a01f5728a1a4efd8b.png!small)

  

2.注意：受害机器的 IPv6地址选取“ipv6地址”或者“临时ipv6地址”

3.攻击者和目标主机通信(这里把自己的物理机作为攻击机者)

执行ipconfig查看攻击机的ipv6地址，选择“本地链接的ipv6地址”。

![](https://image.3001.net/images/20201106/1604624432_5fa4a0309952548b1cc1a.png!small)

  

4.攻击机中python为3.7+ ，并且安装了scapy。 ：在安装好的python后，打开cmd，输入python,没有报错，说明成功：

![](https://image.3001.net/images/20201106/1604624445_5fa4a03d47823ea09f635.png!small)

  

然后安装scapy：

直接使用pip安装：

pip install scapy

一些扩展功能安装，可选：

pip install matplotlib pyx cryptography

启动scapy交互shell

切换到Python的Scripts文件夹下，直接使用scapy命令启动（本质是scapy.bat）：

Scapy

启动界面如下图：

![](https://image.3001.net/images/20201106/1604624457_5fa4a049d72205245272a.png!small)

  

  

5.这段payload作用是构造特定ipv6数据包，发送给受害者机器，让受害机器蓝屏。

CVE-2020-16898-exp1.py:

![](https://image.3001.net/images/20201106/1604624493_5fa4a06d9f33cbb1dcb01.png!small)

  

  

修改完后，在攻击者上执行：python 1.py

![](https://image.3001.net/images/20201106/1604624502_5fa4a0766b3b61472daef.png!small)

  

  

虚拟机被打成蓝屏：如下

![](https://image.3001.net/images/20201106/1604624513_5fa4a081082f08b90633e.png!small)

  

可以使用wirkshark选择对应的虚拟网卡进行抓包查看

如下图所示:

![](https://image.3001.net/images/20201106/1604624522_5fa4a08ae37fe3bdee760.png!small)

  

查看数据包可以看到里面有发送的payload。

![](https://image.3001.net/images/20201106/1604624532_5fa4a0945d93e49c64ccb.png!small)

  

## 0x05修复建议

1.升级更新。立即安装针对此漏洞的更新，下载最新的补丁包进行更新修复，如下连接。

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-16898>

2.不能升级的话，建议先禁用基于RA的DNS配置

