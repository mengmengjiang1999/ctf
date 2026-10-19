## 前言

本文通过利用DCERPC协议的ping，并附加NTLMSSP认证信息来获取获取windows远程主机的版本号，主机名，所在域的域名，DNS等信息。

因为通过rpc进行探测的工具，大部分都是依托impacket来实现，而实战中通过挂代理进行内网探测速率和准确度都比较低，所以最好的方法是将脚本放到目标主机上，来进行内网探测信息收集，所以本文关注的点是想办法脱离impacket，在Socket
RAW上的实现，这样能够减小工具的体积，并且其他语言也能够轻松复刻整个过程，便于应用到实战中。

## 成果

首先看一下成果，通过DCERPC协议的ping附带NTLMSSP来获取到目标的版本号，主机名，域名，DNS等信息。

![](https://image.3001.net/images/20220601/1654058618_6296ee7a5a79043acc764.png!small)

## 协议介绍-RPC

RPC（Remote Procedure
Call）远程过程调用协议，一种通过网络从远程计算机上请求服务，而不需要了解底层网络技术的协议。RPC它假定某些协议的存在，例如TCP/UDP等，为通信程序之间携带信息数据。在OSI网络七层模型中，RPC跨越了传输层和应用层，RPC使得开发，包括网络分布式多程序在内的应用程序更加容易。

## 过程

### 原理

通过看了一篇[网络空间测绘核心技术之：协议识别（DCERPC篇）](https://nosec.org/home/detail/4709.html)的文章之后，发现可以通过dcerpc的ping包+ntlmssp，epmapper接口，OXIDResolver接口，无需认证的情况下获取目标主机的版本号、主机名、多块网卡、注册到rpc的程序服务等信息。于是想自己实现一下。

对于通过OXIDResolver接口获取多块网卡的信息，已经有大佬实现了，再次不在赘述，重点是借鉴思路。

如下图所示当带上ntlmssp的时候，响应包，就会附带完整的系统版本号，主机名，域名等信息。

请求包：

![](https://image.3001.net/images/20220601/1654058619_6296ee7b189ee0ae15849.png!small)

响应包：

![](https://image.3001.net/images/20220601/1654058619_6296ee7b849d21be249bc.png!small)

![](https://image.3001.net/images/20220601/1654058620_6296ee7c1ec01a9b49e1d.png!small)

### 交互过程分析

正常的方式有两种，第一种看官方文档，下载[idl接口文件](https://docs.microsoft.com/en-us/windows/win32/com/idl-files)，从头开始写码，另外一种是分析包的结构，寻找规律，尝试构包。

本文是选择后者。

接下来我们尝试抓流量分析包的情况，通过尝试对两台主机进行发包，看下一下是否有规律。

192.168.8.128-> 192.168.31.13  
![](https://image.3001.net/images/20220601/1654058620_6296ee7cbbaf37a16a98e.png!small)

192.168.80.134-> 192.168.31.130  
![](https://image.3001.net/images/20220601/1654058621_6296ee7d5593267878afa.png!small)

可以发现一共有4个数据包，前面是TCP握手不用管，通过分析对比后，可以发现两个请求包是一样，响应包也有一定规律。  
![](https://image.3001.net/images/20220601/1654058621_6296ee7d9e13d333be62e.png!small)

 **分析包结构** ：

请求包长度内容固定

 **第一个数据包 72 bytes（主要用于协商版本等等）：**  
![](https://image.3001.net/images/20220601/1654058622_6296ee7e3f35ce7543274.png!small)

    
    
    "\x05\x00\x0b\x03\x10\x00\x00\x00\x48\x00\x00\x00\x01\x00\x00\x00" \
    "\xb8\x10\xb8\x10\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00" \
    "\x08\x83\xaf\xe1\x1f\x5d\xc9\x11\x91\xa4\x08\x00\x2b\x14\xa0\xfa" \
    "\x03\x00\x00\x00\x33\x05\x71\x71\xba\xbe\x37\x49\x83\x19\xb5\xdb" \
    "\xef\x9c\xcc\x36\x01\x00\x00\x00"
    

**第二个数据包：**

这个包中如果包含`\x33\x05\x71\x71\xBA\xBE\x37\x49\x83\x19\xB5\xDB\xEF\x9C\xCC\x36`则是x64，否则则为x86

    
    
    "\x05\x00\x0c\x03\x10\x00\x00\x00\x3c\x00\x00\x00\x01\x00\x00\x00" \
    "\xb8\x10\xb8\x10\x41\x1a\x00\x00\x04\x00\x31\x33\x35\x00\x00\x00" \
    "\x01\x00\x00\x00\x00\x00\x00\x00\x33\x05\x71\x71\xba\xbe\x37\x49" \
    "\x83\x19\xb5\xdb\xef\x9c\xcc\x36\x01\x00\x00\x00"
    

**第三个数据包：**

这个数据包中带着ntlmssp  
![](https://image.3001.net/images/20220601/1654058622_6296ee7e9c3bcedd595a8.png!small)

    
    
    "\x05\x00\x0b\x03\x10\x00\x00\x00\x78\x00\x28\x00\x03\x00\x00\x00" \
    "\xb8\x10\xb8\x10\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x01\x00" \
    "\xa0\x01\x00\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46" \
    "\x00\x00\x00\x00\x04\x5d\x88\x8a\xeb\x1c\xc9\x11\x9f\xe8\x08\x00" \
    "\x2b\x10\x48\x60\x02\x00\x00\x00\x0a\x02\x00\x00\x00\x00\x00\x00" \
    "\x4e\x54\x4c\x4d\x53\x53\x50\x00\x01\x00\x00\x00\x07\x82\x08\xa2" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x06\x01\xb1\x1d\x00\x00\x00\x0f"
    

**第四个数据包：**

可以看到附带操作系统版本信息，主机名，域名，DNS域名，DNS主机名等信息。  
![](https://image.3001.net/images/20220601/1654058623_6296ee7f658b36ce9cefa.png!small)

    
    
    "\x05\x00\x0c\x03\x10\x00\x00\x00\x26\x01\xe2\x00\x03\x00\x00\x00" \
    "\xb8\x10\xb8\x10\x42\x1a\x00\x00\x04\x00\x31\x33\x35\x00\x00\x00" \
    "\x01\x00\x00\x00\x00\x00\x00\x00\x04\x5d\x88\x8a\xeb\x1c\xc9\x11" \
    "\x9f\xe8\x08\x00\x2b\x10\x48\x60\x02\x00\x00\x00\x0a\x02\x00\x00" \
    "\x00\x00\x00\x00\x4e\x54\x4c\x4d\x53\x53\x50\x00\x02\x00\x00\x00" \
    "\x06\x00\x06\x00\x38\x00\x00\x00\x05\x82\x89\xa2\x15\x71\x1e\x72" \
    "\x12\x1a\x14\x3d\x00\x00\x00\x00\x00\x00\x00\x00\xa4\x00\xa4\x00" \
    "\x3e\x00\x00\x00\x0a\x00\x61\x4a\x00\x00\x00\x0f\x45\x00\x53\x00" \
    "\x47\x00\x02\x00\x06\x00\x45\x00\x53\x00\x47\x00\x01\x00\x18\x00" \
    "\x41\x00\x30\x00\x32\x00\x33\x00\x35\x00\x31\x00\x38\x00\x2d\x00" \
    "\x4e\x00\x43\x00\x30\x00\x31\x00\x04\x00\x18\x00\x45\x00\x53\x00" \
    "\x47\x00\x2e\x00\x33\x00\x36\x00\x30\x00\x45\x00\x53\x00\x2e\x00" \
    "\x43\x00\x4e\x00\x03\x00\x32\x00\x41\x00\x30\x00\x32\x00\x33\x00" \
    "\x35\x00\x31\x00\x38\x00\x2d\x00\x4e\x00\x43\x00\x30\x00\x31\x00" \
    "\x2e\x00\x45\x00\x53\x00\x47\x00\x2e\x00\x33\x00\x36\x00\x30\x00" \
    "\x45\x00\x53\x00\x2e\x00\x43\x00\x4e\x00\x05\x00\x18\x00\x45\x00" \
    "\x53\x00\x47\x00\x2e\x00\x33\x00\x36\x00\x30\x00\x45\x00\x53\x00" \
    "\x2e\x00\x43\x00\x4e\x00\x07\x00\x08\x00\xa8\xb3\x8f\xb4\xaa\x71" \
    "\xd8\x01\x00\x00\x00\x00"
    

### 数据包结构解析

第四个数据包是不定长的，包括目标操作系统版本信息，主机名，域名，DNS域名，DNS主机名等信息。

![](https://image.3001.net/images/20220601/1654058623_6296ee7f658b36ce9cefa.png!small)

 **规律：**

从54位开始是dcerpc结构的内容  
![](https://image.3001.net/images/20220601/1654058624_6296ee80af57c785c2b11.png!small)

我们需要的内容在`Auth Info：NTLMSSP，Connect AuthContextID(0)`或者说`NTLM Secure Service
Provider`下面。  
![](https://image.3001.net/images/20220601/1654058625_6296ee817b3193b8f9928.png!small)

即整体包的偏移122（0x70+0x0a）开始获取所需内容。  
![](https://image.3001.net/images/20220601/1654058626_6296ee82673d77ad69dd3.png!small)

`NTLM Secure Service Provider`的结构

> 8 bytes：NTLMSSP identifier: NTLMSSP  
> 8 bytes：NTLM Message Type: NTLMSSP_CHALLENGE (0x00000002)  
> 2 bytes：Target Name的Length  
> 2 bytes：Target Name的Maxlen  
> 4 bytes：Target Name的Offset  
> 4 bytes：Negotiate Flags: 0xa2898205, Negotiate 56, Negotiate 128, Negotiate
> Version, Negotiate Target Info, Negotiate Extended Security, Target Type
> Domain, Negotiate Always Sign, Negotiate NTLM key, Request Target, Negotiate
> UNICODE  
> 8 bytes：NTLM Server Challenge: 15711e72121a143d  
> 8 bytes：Reserved: 0000000000000000  
> 2 bytes：Target Info 的Length  
> 2 bytes：Target Info 的Maxlen  
> 4 bytes：Target Info 的Offset  
> 24 bytes：操作系统版本信息  
> 剩下的全是Target Info的数据，属性有：  
> NetBIOS domain name  
> NetBIOS computer name  
> DNS domain name  
> DNS computer name  
> DNS tree name  
> Timestamp  
> End of list(0x00000000)
>
> 每个属性的结构为：
>
> 类型2bytes、长度2bytes、值（根据前面的长度）

根据上面的分析，通过socket构包，对回包进行偏移解析，获取所需字段内容，代码如下：

    
    
    OS_Version_bytes = packet2[int('0xa0', 16) - 54 + 10:int('0xa0', 16) - 54 + 18]
    Major_Version = int.from_bytes(OS_Version_bytes[0:1], byteorder='little')
    Minor_Version = int.from_bytes(OS_Version_bytes[1:2], byteorder='little')
    Build_Number = int.from_bytes(OS_Version_bytes[2:4], byteorder='little')
    NTLM_Current_Reversion = int.from_bytes(OS_Version_bytes[7:8], byteorder='little')
    OS_Verison = "Windows Version {0}.{1} Build {2} {3}".format(Major_Version, Minor_Version, Build_Number, digit)
    Target_Info_Length_bytes = packet2[int('0xa0', 16) - 54 + 2:int('0xa0', 16) - 54 + 4]
    Target_Info_Length = int.from_bytes(Target_Info_Length_bytes, byteorder='little')
    Target_Info_bytes = packet2[-Target_Info_Length:-4]  # 最后四个0x00000000
    

发送第二个包解析代码

    
    
    def get_osinfo(ip):
        global length
        osinfo = {
            "NetBIOS_domain_name": "",
            "DNS_domain_name": "",
            "DNS_computer_name": "",
            "DNS_tree_name": "",
        }
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(4)
            sock.connect((ip, 135))
            buffer_v2 = b"\x05\x00\x0b\x03\x10\x00\x00\x00\x78\x00\x28\x00\x03\x00\x00\x00\xb8\x10\xb8\x10\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x01\x00\xa0\x01\x00\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46\x00\x00\x00\x00\x04\x5d\x88\x8a\xeb\x1c\xc9\x11\x9f\xe8\x08\x00\x2b\x10\x48\x60\x02\x00\x00\x00\x0a\x02\x00\x00\x00\x00\x00\x00\x4e\x54\x4c\x4d\x53\x53\x50\x00\x01\x00\x00\x00\x07\x82\x08\xa2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x01\xb1\x1d\x00\x00\x00\x0f"
            sock.send(buffer_v2)
            packet2 = sock.recv(4096)
            digit = send_packet(ip)
            OS_Version_bytes = packet2[int('0xa0', 16) - 54 + 10:int('0xa0', 16) - 54 + 18]
            # print(test(OS_Version_bytes))
            Major_Version = int.from_bytes(OS_Version_bytes[0:1], byteorder='little')
            Minor_Version = int.from_bytes(OS_Version_bytes[1:2], byteorder='little')
            Build_Number = int.from_bytes(OS_Version_bytes[2:4], byteorder='little')
            NTLM_Current_Reversion = int.from_bytes(OS_Version_bytes[7:8], byteorder='little')
            OS_Verison = "Windows Version {0}.{1} Build {2} {3}".format(Major_Version, Minor_Version, Build_Number, digit)
            # print(OS_Verison)
    
            Target_Info_Length_bytes = packet2[int('0xa0', 16) - 54 + 2:int('0xa0', 16) - 54 + 4]
            Target_Info_Length = int.from_bytes(Target_Info_Length_bytes, byteorder='little')
            Target_Info_bytes = packet2[-Target_Info_Length:-4]  # 最后四个0x00000000
            print("[*] " + ip)
            print("\t[->]", "OS_Verison :", OS_Verison)
            for k in osinfo.keys():
                osinfo[k] = attribute_name(Target_Info_bytes)
                print("\t[->]", k, ":", osinfo[k])
                # print(attribute_name(Target_Info_bytes))
            length = 0
            osinfo["OS_Verison"] = OS_Verison
            result = {ip: osinfo}
            # print(result)
            return osinfo
        except Exception as e:
            # print(e)
            return -1
        finally:
            sock.close()
    
    
    def attribute_name(Target_Info_bytes):
        global length
        att_name_length = int.from_bytes(Target_Info_bytes[length + 2:length + 4], byteorder='little')
        att_name = Target_Info_bytes[length + 4:length + 4 + att_name_length].replace(b"\x00", b"").decode(
            encoding="unicode_escape")
        length = length + 4 + att_name_length
        return att_name
    

上面也说了要通过第一个包判断目标操作系统的架构，代码如下：

    
    
    def send_packet(ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(4)
            sock.connect((ip, 135))
            buffer_v1 = b"\x05\x00\x0b\x03\x10\x00\x00\x00\x48\x00\x00\x00\x01\x00\x00\x00\xb8\x10\xb8\x10\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x08\x83\xaf\xe1\x1f\x5d\xc9\x11\x91\xa4\x08\x00\x2b\x14\xa0\xfa\x03\x00\x00\x00\x33\x05\x71\x71\xba\xbe\x37\x49\x83\x19\xb5\xdb\xef\x9c\xcc\x36\x01\x00\x00\x00"
            sock.send(buffer_v1)
            packet1 = sock.recv(1024)
            digit = "x86"
            if b"\x33\x05\x71\x71\xBA\xBE\x37\x49\x83\x19\xB5\xDB\xEF\x9C\xCC\x36" in packet1:
                digit = "x64"
            return digit
        except Exception as e:
            # print(e)
            return -1
        finally:
            sock.close()
    

注意：经过测试发送两个数据包不能在一个socket会话里面，否则第二个包的响应会不正常，要建立两个会话进行发送。

### 写成脚本

根据上面的分析，写成了多线程的脚本， **多线程实现扫描效果** 如下：  
![](https://image.3001.net/images/20220601/1654058626_6296ee82df04e297d1f61.png!small)

![](https://image.3001.net/images/20220601/1654058627_6296ee836dd1d3af85f8d.png!small)

域内主机的话会显示域名，主机名，操作系统版本架构等信息，工作组主机则信息都是自己的主机名。

最后脚本放在了github：https://github.com/komomon/Dcerpc_Find_OSInfo

参考文章：

[Remote Enumeration of Network Interfaces without any Authentication: The OXID
Resolver](https://www.arridae.com/blogs/OXID-Resolver.php#)

[SharpDetectionNTLMSSP](https://github.com/RowTeam/SharpDetectionNTLMSSP)

[网络空间测绘核心技术之：协议识别（DCERPC篇）](https://nosec.org/home/detail/4709.html)

https://payloads.online/archivers/2020-07-16/1/

