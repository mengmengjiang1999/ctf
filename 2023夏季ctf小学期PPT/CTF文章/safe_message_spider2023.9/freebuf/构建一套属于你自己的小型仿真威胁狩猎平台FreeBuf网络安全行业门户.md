## 0x01 前言

本文主要讲述如何在自己本地构建起一套小型威胁狩猎平台，同时你也可以基于该小型威胁狩猎平台来辅助你理解ATT&CK相关技战术，并了解蓝队视角下红队攻击技术可能会带来哪些痕迹。

## 0x02 平台架构/构建

![image](https://image.3001.net/images/20211105/1636076658_61848c726d17f14356f3b.jpg!small)

操作系统| 功能角色| 采集数据| 插件配置  
---|---|---|---  
Windows server 2012| 域控服务器| Windows event log、Sysmon_log|
Splunk_forwarder、Sysmon  
Windows server 2016| 域内主机| Windows event log、Sysmon_log|
Splunk_forwarder、Sysmon  
Ubuntu 18.04| Linux主机| System_log、Audit_log| Audit、Splunk_forwarder  
Ubuntu 18.04| Soc服务器|  
| Splunk Free  
Kali linux| 模拟Red Team|  
|  
  
  
### 环境构建说明：

1、模拟部署Windows
AD域环境，并在域环境下开启Windows日志审核策略，并部署Sysmon作为Windows日志的补充。部署Splunk日志转发工具，转发Windows
event_log和Sysmon_log至Soc平台；

2、部署Ubuntu18.04，并安装Splunk Free，作为Soc平台，收集域内主机日志，并对模拟攻击行为产生的数据进行分析。

3、Kali linux作为模拟Red Team的攻击机，本次测试直接使用Atomic Red Team在Windows server
2016上进行本地测试。也可以使用远程测试，把相关测试文件部署在Kali linux上。

## 0x03 模拟狩猎

在接下来的例子中我们将会模拟使用Atomic Red Team在Windows server 2016上模拟T1069-002权限组发现。

### 阶段1：T1069.002介绍

攻击者可能会尝试查找域级别的组和权限设置。域级别的权限组的信息可以帮助攻击者确定存在哪些组以及哪些用户属于特定组。攻击者可以使用此信息来确定哪些用户具有提升的权限，例如域管理员。

在Windows操作系统上可以使用net group /domain命令进行查找，在Mac操作系统上使用dscacheutil -q
group命令、Linux上可以使用ldapsearch命令查找。

### 阶段2：执行测试

本次模拟主要为Atomic Red Team项目中的T1069-002第一个测试项，该测试项包含以下命令：

    
    
    net localgroup
    net group /domain
    net group "domain admins" /domain
    net group "enterprise admins" /domain
    

执行模拟测试：

    
    
    Invoke-AtomicTest T1069.002 -TestNumbers 1
    

![image](https://image.3001.net/images/20211105/1636076693_61848c95a7c3d301deeb6.jpg!small)

### 阶段3：分析及检测

测试命令执行后，数据采集器将会采集windows安全日志/Sysmon日志，并发送至SOC平台。SOC平台将会收集到攻击所使用的命令以及基本的进程信息。我们可以在这里提取到许多有价值的信息，包括一些进程调用、命令行参数。

![image](https://image.3001.net/images/20211105/1636076706_61848ca2b5b0767861042.jpg!small)

对数据的挖掘和分析，有助于帮助我们观察攻击中的载荷信息。直观的观察到攻击的执行流程，从powershell.exe的进程启用，到调用cmd.exe、net.exe、net1.exe等进程，再到具体命令的执行。

![image](https://image.3001.net/images/20211105/1636076725_61848cb5a038661e525e2.jpg!small)

### 阶段4：总结

在完成一次简单的模拟测试之后，你可以，分析哪些字段可以用于生成告警规则，以便于你在真实的生产环境中检测该攻击事件的发生。当然，真实的攻击并非这么简单，因此需要你不断的进行学习红队的相关技术，分析其攻击行为特征。

## 0x04 最后

通过这篇文章，你可以简单的利用自己的资源部署一套小型仿真威胁狩猎平台，来模拟各种攻击手法，并分析相关特征。同时，也可以辅助你来理解ATT&CK相关技战术手法。

基于这套小型仿真威胁狩猎平台，你还可以做更多的事情，值得你去发掘，比如利用Sysmon、Audit日志等，去做更有意义的事情。

## 0x05 参考文章

Sysmon使用社区指南

<https://mp.weixin.qq.com/s/yloFDpJ6wvFZymzqCRtbBQ>

windows基本审核策略

<https://docs.microsoft.com/zh-cn/windows/security/threat-protection/auditing/basic-security-audit-policies>

Atomic Red Team

<https://github.com/redcanaryco/atomic-red-team/>

Threathunting-book

