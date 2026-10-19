# 漏洞介绍

2020年3月10日，微软在其官方SRC发布了CVE-2020-0796的安全公告（ADV200005，MicrosoftGuidance for
Disabling SMBv3 Compression）,公告表示在Windows
SMBv3版本的客户端和服务端存在远程代码执行漏洞。同时指出该漏洞存在于MicroSoft Server Message Block
3.1.1协议处理特定请求包的功能中，攻击者利用该漏洞可在目标SMB Server或者Client中执行任意代码

# 漏洞影响

 **SMB版本 v3.1.1**

 **Windows 10 v1903-1909 x64**  
Windows 10 Version 1903 for -bit Systems  
Windows 10 Version 1903 for x64-based Systems  
Windows 10 Version 1903 for ARM64-based Systems  
Windows Server, Version 1903 (Server Core installation)  
Windows 10 Version 1909 for -bit Systems  
Windows 10 Version 1909 for x64-based Systems  
Windows 10 Version 1909 for ARM64-based Systems  
Windows Server, Version 1909 (Server Core installation)

