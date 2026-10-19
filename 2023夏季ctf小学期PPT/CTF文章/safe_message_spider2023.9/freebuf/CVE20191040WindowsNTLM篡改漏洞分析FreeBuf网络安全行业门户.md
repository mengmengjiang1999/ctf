**2019年6月11日，Microsoft发布了六月份安全补丁更新。在该安全更新补丁中，对CVE-2019-1040漏洞进行了修复
。攻击者利用该漏洞可以绕过NTLM中的MIC（Message Integrity
Code）。攻击者可以修改已经协商签名的身份验证流量，然后中继到另外一台服务器，同时完全删除签名要求。通过该攻击方式可使攻击者在仅有一个普通域账号的情况下，运程控制域中任意机器（包括域控服务器）。**

## 漏洞背景

NTLM中继是对Active
Directory环境最常见的攻击方式之一。针对此攻击技术一种重要的缓解措施是进行服务器签名。当用户与服务器建立了签名会话，攻击者如果无法检索所需的会话密钥，就无法劫持会话。但是在默认情况下，只有域控服务器会强制执行SMB签名，这导致在许多情况下会使得域中其他敏感服务器容易受到攻击。

![](https://image.3001.net/images/20190618/1560822248_5d0841e8e5447.png!small)

图1 NTLM中继

在SMB中，通过在NTLM_NEGOTIATE消息中设置”NTLMSSP_NEGOTIATE_SIGN”标志进行协商会话签名。如果攻击者试图中继这种NTLM身份验证，他们将需要确保不协商签名。一种方法是通过中继到NTLM消息不管理会话完整性的协议，如LDAPS或者HTTPS。但是这种协议并非每一台机器都会打开。而SMB协议在局域网中是经常打开的，且存在较多漏洞容易造成代码执行。因此，NTLM中继攻击的重点就在于将SMB身份验证请求转发给其他SMB服务器。为成功执行此类中继，攻击者需要修改NTLM_NEGOTIATE消息并取消设置”NTLMSSP_NEGOTIATE_SIGN”标志。

![](https://image.3001.net/images/20190618/1560822263_5d0841f7cc231.png!small)

图2 NTLM_NEGOTIATE消息指示是否协商SMB签名

在SMB中，默认情况下，通信的双方都支持签名，则必须进行会话签名。为了保证在NTLM协商阶段不被攻击者篡改数据，Microsoft在最终的NTLM身份验证消息中添加了一个额外字段——MIC。但是，微软对该字段的处理方式存在纰漏：允许无MIC的验证消息。

### MIC(Message Interity Code)消息完整性验证

NTLM身份验证由3种消息类型组成：NTLM_NEGOTIATIE，NTLM_CHALLENGE，NTLM_AUTHENTICATE。为确保在传输过程中不会被恶意篡改，在NTLM_AUTHENTICATE消息中添加了一个额外的MIC字段。MIC是使用会话密钥应用于所有3个NTLM消息的串联的HMAC_MD5，该会话密钥只有启动了认证的账户和目标服务器知道。因此，任何试图篡改其中一条消息的行为都无法生成相应的MIC，保证传输的安全性。

![](https://image.3001.net/images/20190618/1560822282_5d08420a84e6b.png!small)

图3 “MIC”字段可以防止NTLM消息修改

MIC存在于NTLM_AUTHENTICATE消息的’msvAvFlag’字段，标志0x2表示该消息包括MIC。它应该保护MIC被删除。但是，微软Microsoft服务器无法完全执行该机制，而且允许了无MIC的NTLM_AUTHENTICATE消息。这为后续NTLM中继攻击提供了条件。

![](https://image.3001.net/images/20190618/1560822328_5d084238091a8.png!small)

图4 'flags'字段指示NTLM_AUTHENTICATE消息包括MIC

## 漏洞分析

### 4.1 攻击思路

由于微软允许无MIC的NTLM_AUTHENTICATE消息，攻击者可以在获取到合法的身份验证后进行中继。主要是将SMB中继到LDAP。

首先向Windows服务器（如Exchange）发起身份验证，在获得合法的验证后将该身份验证通过LDAP中继到域控服务器，就可以在ActiveDirective中以中继的受害者权限执行一系列操作。

在Exchange场景下，可以获得DCSync权限，该种权限是PrivExchange漏洞利用的基础

在Resource Based Constrained Kerberos场景下，可以利用该种机制获得受害主机的权限，进而以管理员权限访问服务器。

对需要中继的身份验证的MIC的处理流程如下：

1\.
取消设置NTLM_NEGOTIATE消息中的签名标志（NTLMSSP_NEGOTIATE_ALWAYS_SIGN，NTLMSSP_NEGOTIATE_SIGN）

2\. 从NTLM_AUTHENTICATE消息中删除MIC

3\. 从NTLM_AUTHENTICATE消息中删除版本字段（删除MIC字段而不删除版本字段将导致错误）

4\.
取消设置NTLM_AUTHENTICATE消息中的以下标志：NTLMSSP_NEGOTIATE_ALWAYS_SIGN，NTLMSSP_NEGOTIATE_SIGN，NEGOTIATE_KEY_EXCHANGE，NEGOTIATE_VERSION。

### 4.2 攻击途径

1\.
使用任意AD账户，通过SMB连接到受害主机Exchange服务器，触发SpoolService的一个bug。然后使用网上公开的ntlmrelayx.py脚本中继到LDAP。使用中继的LDAP身份验证，攻击者可以获得DCSync权限，然后使用DCSync转储AD中所有的密码哈希。

2\.
使用任意AD账户，通过SMB连接到受害主机Exchange服务器，触发SpoolService的一个bug。然后使用网上公开的ntlmrelayx.py脚本中继到LDAP。攻击者使用中继的LDAP身份验证，获取Resource
Based Constrained
Kerberos中的相关权限，然后攻击者以受害主机服务器上的任意用户进行身份验证。成功验证后，可以进一步进行下一步攻击，甚至控制整个Wshoindows域。

## 影响范围

目前受影响的Windows版本：

    
    
    Windows 10 for 32-bit Systems
    
    Windows 10 for x64-based Systems
    
    Windows 10 Version 1607 for 32-bit Systems
    
    Windows 10 Version 1607 for x64-based Systems
    
    Windows 10 Version 1703 for 32-bit Systems
    
    Windows 10 Version 1703 for x64-based Systems
    
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
    
    Windows 7 for 32-bit Systems Service Pack 1
    
    Windows 7 for x64-based Systems Service Pack 1
    
    Windows 8.1 for 32-bit systems
    
    Windows 8.1 for x64-based systems
    
    Windows RT 8.1
    
    Windows Server 2008 for 32-bit Systems Service Pack 2
    
    Windows Server 2008 for 32-bit Systems Service Pack 2 (Server Core installation)
    
    Windows Server 2008 for Itanium-Based Systems Service Pack 2
    
    Windows Server 2008 for x64-based Systems Service Pack 2
    
    Windows Server 2008 for x64-based Systems Service Pack 2 (Server Core installation)
    
    Windows Server 2008 R2 for Itanium-Based Systems Service Pack 1
    
    Windows Server 2008 R2 for x64-based Systems Service Pack 1
    
    Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core installation)
    
    Windows Server 2012
    
    Windows Server 2012 (Server Core installation)
    
    Windows Server 2012 R2
    
    Windows Server 2012 R2 (Server Core installation)
    
    Windows Server 2016
    
    Windows Server 2016 (Server Core installation)
    
    Windows Server 2019
    
    Windows Server 2019 (Server Core installation)
    
    Windows Server, version 1803 (Server Core Installation)
    
    Windows Server, version 1903 (Server Core installation)

## 修复建议

1\. 由于针对该漏洞的 poc已在网上公开流传，强烈建议广大用户及时安装微软针对该漏洞的安全更新补丁：

> <https://portal.msrc.microsoft.com/en-US/security-> guidance/advisory/CVE-2019-1040>

2\. 其他缓解措施

以下措施可以在无法及时安装安全更新补丁时作为临时解决方案，为确保安全，仍然建议广大用户在条件允许的情况下及时进行补丁安装：

1）开启域中所有服务器的强制SMB 签名 （在 Windows 域 中 ，默认只有域控服务器开启了强制 SMB 签名）

2）对LDAP over TLS强制执行LDAP签名和LDAP通道绑定来阻止NTLM中继到LDAP

3）开启EPA，强制所有Web服务器（OWA，ADFS）只接受EPA的请求

4）开启所有重要服务器（比如所有 Exchange 服务器）上相关应用的Channel Binding

5）减少使用NTLM

6）如无特殊需求，禁用Printer Spooler服务

## 参考链接

> [1]. <https://blog.preempt.com/security-advisory-critical-vulnerabilities-> in-ntlm>
>
> [2]. <https://blog.preempt.com/drop-the-mic>
>
> [3]. <https://dirkjanm.io/worst-of-both-worlds-ntlm-relaying-and-kerberos-> delegatio>

***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

