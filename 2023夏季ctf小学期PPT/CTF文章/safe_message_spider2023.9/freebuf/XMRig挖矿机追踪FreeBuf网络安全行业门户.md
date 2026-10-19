随着主机保护方法改进，矿工的开发人员也在不断创新研发，寻求新的攻击方案。在对开源矿机XMRig的分析过程中，发现了以下几种新的攻击方案。

## 勒索+挖矿

除了一些利用数据盗窃和勒索软件牟利的知名犯罪组织（例如Maze，它最近对SK Hynix和LG
Electronics进行攻击），许多潜在的普通攻击者也参与其中。在技​​术能力方面，此类业余爱好者远远落后于有组织的群体，他们常使用公开可用的勒索软件，针对普通用户而不是公司部门。

此类攻击支出通常很小，必须采取各种策略使其收益最大化。今年8月，在受害者的计算机上发现Trojan，它安装了管理程序，并添加新的用户，可对计算机进行RDP访问。接下来，勒索软件Trojan-Ransom.Win32.Crusis在同一台计算机上启动，然后加载XMRig挖矿机，然后开始挖掘Monero加密货币。

结果，用户看到赎金记录的同时计算机已经开始为网络罪犯赚钱。攻击者利用RDP访问权限研究受害者网络，并在需要时将勒索软件传播到其他节点。

Trojan文件详细信息：

> Mssql — PC Hunter x64 (f6a3d38aa0ae08c3294d6ed26266693f)  
> mssql2 — PC Hunter x86 (f7d94750703f0c1ddd1edd36f6d0371d)  
> exe — 扫描器(597de376b1f80c06d501415dd973dcec)  
> bat — 删除软件  
> bat — 新建用户，添加管理员组，打开RDP访问，连接服务器  
> exe — IOBIT Unlocker (5840aa36b70b7c03c25e5e1266c5835b)  
> EVER\SearchHost.exe — Everything软件 (8add121fa398ebf83e8b5db8f17b45e0)  
> EVER\1saas\1saas.exe — Trojan-Ransom.Win32.Crusis
> (0880430c257ce49d7490099d2a8dd01a)  
> EVER\1saas \LogDelete — 加载器 (6ca170ece252721ed6cc3cfa3302d6f0, HEUR:Trojan-> Downloader.Win32.Generic)

批处理脚本systembackup.bat添加用户并打开RDP访问

![1603761074_5f9773b28bbca2f9c789d.png!small?1603761074888](https://image.3001.net/images/20201027/1603761074_5f9773b28bbca2f9c789d.png!small?1603761074888)

## Prometei后门+挖矿

Prometei家族自2016年以来就广为人知，在2020年2月首次与XMRig一起被发现。

在普通攻击中，网络犯罪分子通过各种攻击获得服务器访问权限。此次攻击中攻击者使用暴力攻击获得了MS SQL的用户名和密码，利用T-SQL函数xp_cmdshell运行多个PowerShell脚本，并利用CVE-2016-0099漏洞提权，之后将木马和Prometei安装在受害者计算机上。

安装时使用标准.NET
Core工具（Apphost）将.NET可执行文件打包到ELF文件中，将受感染计算机信息发送到C＆C服务器，然后下载加密货币矿工及其配置，Windows和Linux的加载程序的版本仅稍有不同。

## 剪贴板监控+Cliptomaner矿工

Cliptomaner在2020年9月被发现，它不仅挖掘加密货币，还可以替换剪贴板中的加密钱包地址。 根据计算机配置选择矿机版本，并从C＆C下载。
该恶意软件以Realtek音频设备的形式传播，Cliptomaner完全用AutoIT脚本语言编写。

地址替换过程如下：

![1603761487_5f97754fc802a1b07cf68.png!small?1603761488067](https://image.3001.net/images/20201027/1603761487_5f97754fc802a1b07cf68.png!small?1603761488067)

过程中检测到以下恶意程序：

> HEUR:Trojan.MSIL.Prometei.gen, HEUR:Trojan.Script.Cliptomaner.gen,
> HEUR:Trojan-Downloader.Win32.Generic, Trojan-Ransom.Win32.Crusis,
> Trojan.Win64.Agentb,RiskTool.Win64.XMRigMiner

## IOCs

### Domains

> taskhostw[.]com  
> svchost[.]xyz  
> sihost[.]xyz  
> srhost[.]xyz  
> 2fsdfsdgvsdvzxcwwef-defender[.]xyz

### 钱包地址

> LTC: LPor3PrQHcQv4obYKEZpnbqQEr8LMZoUuX  
> BTC: 33yPjjSMGHPp8zj1ZXySNJzSUfVSbpXEuL  
> ETH: 0x795957d9753e854b62C64cF880Ae22c8Ab14991b  
> ZEC: t1ZbJBqHQyytNYtCpDWFQzqPQ5xKftePPt8  
> DODGE: DEUjj7mi5N67b6LYZPApyoV8Ek8hdNL1Vy

### MD5

> 1273d0062a9c0a87e2b53e841b261976  
> 16b9c67bc36957062c17c0eff03b48f3  
> d202d4a3f832a08cb8122d0154712dd1  
> 6ca170ece252721ed6cc3cfa3302d6f0  
> 1357b42546dc1d202aa9712f7b29aa0d  
> 78f5094fa66a9aa4dc10470d5c3e3155

## 原文链接

> [securelist﻿](https://securelist.com/miner-xmrig/99151/)

