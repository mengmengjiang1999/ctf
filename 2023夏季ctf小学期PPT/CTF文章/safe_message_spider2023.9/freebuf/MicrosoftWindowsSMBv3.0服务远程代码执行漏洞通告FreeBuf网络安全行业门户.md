## 文档信息

编号  |  QiAnXinTI-SV-2020-0008  
---|---  
关键字  |  SMB ADV200005  
发布日期  |  2020年03月11日  
更新日期  |  2020年03月11日  
TLP  |  WHITE  
分析团队  |  奇安信威胁情报中心  
  
  

  

## 通告背景

2020年3月11日，某国外安全公司发布了一个近期微软安全补丁包所涉及漏洞的综述，其中谈到了一个威胁等级被标记为Critical的SMB服务远程代码执行漏洞（据称编号为CVE-2020-0796），攻击者可以利用此漏洞远程无需用户验证通过发送构造特殊的恶意数据导致在目标系统上执行恶意代码，从而获取机器的完全控制。此漏洞主要影响支持SMBv3.0的设备，理论上存在蠕虫化的可能性，目前微软还没有提供相应的漏洞信息，而是发布了一个SMBv3.0漏洞的通告。

奇安信息威胁情报中心红雨滴团队已经确认漏洞的存在，据称微软可能发布例行外的补丁修复此漏洞。由于漏洞存在的信息已经扩散，有迹象表明黑客团伙正在积极地研究漏洞细节尝试利用，构成潜在的安全威胁，在漏洞得到修复之前请按本通告所建议的临时解决方案处理以暂时避免受此漏洞的影响。

## 漏洞概要

**漏洞名称** **** |  Microsoft Windows SMBv3.0服务远程代码执行漏洞  
---|---  
**威胁类型** **** |  远程代码执行  |  **威胁等级** **** |  严重  |  **漏洞** **ID** |  ADV200005  
**利用场景** **** |  攻击者可以通过发送特殊构造的数据包触发漏洞，无需用户验证就可能导致控制目标系统。  
**受影响系统及应用版本** ****  
Windows 10 Version 1903 for 32-bit Systems Windows 10 Version 1903 for
ARM64-based Systems Windows 10 Version 1903 for x64-based Systems Windows 10
Version 1909 for 32-bit Systems Windows 10 Version 1909 for ARM64-based
Systems Windows 10 Version 1909 for x64-based Systems Windows Server, version
1903 (Server Core installation) Windows Server, version 1909 (Server Core
installation)  
  
## 漏洞描述

漏洞存在于Windows的SMBv3.0（文件共享与打印服务）中，目前技术细节未知，对于漏洞的利用无需用户验证，通过构造恶意请求即可触发导致任意代码执行，系统受到非授权控制。

## 影响面评估

此漏洞主要影响SMBv3.0协议,目前支持该协议的设备包括Windows 8、Windows 8.1、Windows 10、Windows Server
2012 和 Windows Server 2016，但是从微软的通告来看受影响目标主要是Win10系统，考虑到相关设备的数量级，潜在威胁较大。

## 处置建议

### 修复方法

1\. 目前暂时没有相关的补丁发布，微软当前建议按如下临时解决方案处理：

执行以下命令

Set-ItemProperty-Path"HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"DisableCompression
-Type DWORD -Value 1 -Force 禁用SMB 3.0的压缩功能，是否使用需要结合自己业务进行判断。

## 参考资料

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV200005>

[https://cc.bingj.com/cache.aspx?q=https%3a%2f%2fblog.talosintelligence.com%2f2020%2f03%2fmicrosoft-patch-tuesday-march-2020.html&w=NrvF66m3pULMCOMEBw-cKyRUwi9s1qXv&d=928684983196](https://cc.bingj.com/cache.aspx?q=https%3A%2F%2Fblog.talosintelligence.com%2F2020%2F03%2Fmicrosoft-patch-tuesday-march-2020.html&w=NrvF66m3pULMCOMEBw-cKyRUwi9s1qXv&d=928684983196)

