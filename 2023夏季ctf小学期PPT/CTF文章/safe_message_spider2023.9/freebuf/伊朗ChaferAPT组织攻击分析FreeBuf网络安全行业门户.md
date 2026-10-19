**ChaferAPT组织隶属于伊朗，自2014年以来一直处于活跃状态，专注于网络间谍活动。
Bitdefender发现该组织2018年开始针对中东关键基础设施进行攻击，攻击中使用了多种工具、定制后门等。**

攻击主要针对航空运输和政府部门，攻击者多在周末进行攻击。在针对科威特的攻击中，攻击者创建了自己的用户帐户，针对沙特的攻击主要依靠社会工程学，两种攻击的最终目标都是窃取数据。

![](https://image.3001.net/images/20200606/1591420519_5edb2667338e0.png!small)

## 攻击链分析

### 科威特

最初发现了一些反向TCP文件和PowerShell命令，攻击者可能使用恶意文档攻击受害者，并利用鱼叉式电子邮件进行传播。攻击者会在目标上使用侦察工具进行网络扫描（“
xnet.exe”，“ shareo.exe”）和凭证收集（如“ mnl.exe”或“
mimi32.exe”）或其他功能工具，例如CrackMapExec（用于用户枚举，共享列表，凭据收集等）。这些工具可帮助攻击者在网络内部横向移动。

攻击者使用psexec或使用RDP协议进行远程服务安装，一旦攻击成功便开始安装自定义模块：经过修改的Plink（wehsvc.exe）以及后门（
imjpuexa.exe）。攻击者会在受害者的计算机上创建用户，并使用该用户在网络内部执行恶意操作。

![](https://image.3001.net/images/20200606/1591424292_5edb35240ea66.png!small)

大多数活动发生在周五和周六，与中东的周末相吻合。 观察到以下顺序：在其中一台机器上部署修改后的PuTTY工具（“ wehsvc.exe”）；
四天后在同一系统上创建一个特定用户； 除了上述工具外，在该用户下还发现了rdpwinst（rdp会话管理），Smartftp Password
Decryptor（安装程序）和 Navicat Premium等。

攻击者通过代理工具（“ mfevtpse.exe”和“ mini.exe”）或后门与受害者保持通信，其中一次攻击时间线如下所示。

![](https://image.3001.net/images/20200606/1591424477_5edb35dd16b6f.png!small)

### 沙特阿拉伯攻击链

攻击者最初是通过社会工程学攻击目标。RAT组件位于％Download％文件夹中，RAT执行了两次，两次执行相隔三分钟，使用不同的名称（“
drivers.exe”和“ drivers_x64.exe”）。使用“
etblscanner.exe”进行内部网络侦察。另外还发现了三种不同的RAT组件，其中一个组件“ snmp.exe”也以“
imjpuexa.exe”出现在科威特的某些受害者身上，攻击时间线如下：

![](https://image.3001.net/images/20200606/1591425006_5edb37ee599fa.png!small)

## 工具分析

攻击者使用“the Non-Sucking”服务管理器来确保其关键组件（例如代理或RAT）已启动运行。
他们还使用Sysinternals工具（例如psexec）在受害者网络中横向移动，使用“ schtasks.exe”确保持久性，“
tasklist”用于测试持久性，“ nslookup”用于DNS通信，查询TXT记录。

发现了不同阶段使用的黑客工具，如Mimikatz、SafetyKatz或定制工具。利用所获得的凭据与psexec工具获取对特定计算机的访问权。
一些受感染的系统还包含Metasploit框架的shellcode片段，例如reverse_tcp，连接到不同的内部IP地址。另一个工具CrackMapExec，具有网络扫描等功能；发现PLINK修改版本，它可以作为Windows服务运行或卸载；发现了一个用C++编写的命令行工具，可作为代理使用。

在攻击过程中还观察到Python（可能是3.4版）编写的RAT。该工具具有两种通信类型（“ DNS”和“ HTTP”），工具的文件名是“
snmp.exe”，“ imjpuexa.exe”和“ driver_x86.exe”，硬编码的标头可如下：

![](https://image.3001.net/images/20200606/1591448756_5edb94b4136aa.png!small)

HTTP通信请求标头“ GET / owa HTTP / 1.1 \ r \ nHost：live.com”和响应标头“ HTTP / 1.1 200
OK”。

此攻击中使用的另一个命令行工具“ xnet.exe”，它与nbtscan工具非常相似，可从计算机上网络适配器获取要扫描的IP范围。
还观察到C#工具（“shareo.exe”），该工具可获得指定IP范围内每台计算机的NetBIOS名称。

发现名为“ mas.dll”的后门，此文件与“xnet.exe”之间存在联系：

> “F:\Projects\94-06\RCE\bin\Release\x64\mas.pdb” – “mas.dll”
>
> “F:\Projects\94-08\XNet\bin\Release\Win32\XNet.pdb”) – “xnet.exe”

## MITRE matrix TTPs

### 持久化

 **T1050 “New Service”:**

“wehsvc.exe” 创建 “imjpuexa.exe” 修改注册表
“HKLM\system\controlset001\services\microsoft updating\parameters\application”

 **T1053 “Scheduled Task”:**

“MSCService.exe” 、“DBXService.exe”

 **T1136 “Create Account”:**

创建用户

### 内网探测

 **T1016 “System Network Configuration Discovery”:**

“xnet.exe”

### C&C

 **T1090 “Connection Proxy”:**

“mini.exe”、“mfevtpse.exe”、“mfevtps.exe”以及修改的Plink

### 防御检测

 **T1045 “Software packing”**

“mfevtpse.exe”

 **T1036 “Masquerading”**

“DBXService.exe”、 “MSCService.exe”

### 命令执行

T1059 “Command line interface”

### 凭证访问

 **T1003 “Credential Dumping”**

Mimikatz

## 附录

![](https://image.3001.net/images/20200606/1591449655_5edb983727f6f.png!small)

## 参考来源

>
> [bitdefender](https://www.bitdefender.com/files/News/CaseStudies/study/332/Bitdefender-> Whitepaper-Chafer-creat4491-en-EN-interactive.pdf)

 ***本文作者： Kriston，转载请注明来自FreeBuf.COM**

