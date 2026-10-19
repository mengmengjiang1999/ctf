# 安全研究 | 关于explorer一键挖矿病毒的分析研究

阅读量 **287257**

发布时间 : 2018-07-27 09:00:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01badccc94ae17c486.jpg)

近期我们的海青安全研究实验室捕获了一个新的挖矿木马样本，目前网络上还未见到关于它的分析。与以往的木马相比，这次捕获的样本有了不小的“进化”：手段更加隐蔽，清除更加困难。我们对它的各项特点进行了分析，希望给行业内带来针对此类木马的新的认识，进而发掘更有效的防护措施。

## 一、木马简介

业务环境：powershellv3及以上版本（v1/v2未测试）  

## 二、木马特点

1.纯powershell编写挖矿前置脚本，不是像以前那种使用批处理等简单挖矿了，使用一系列持久化机制，保证自身挖矿功能；

2.探测防火墙，探测虚拟机，探测反木马软件，进行对应的行为；

3.修改防火墙及反木马软件配置及策略，避免一些防护软件扫描，以及防火墙将挖矿链接阻断；

4.缓存认证密码，可选增加用户等机制；

5.使用代理中转连接，每个肉鸡都是代理服务器，增加了追踪溯源难度；

6.使用更新维护机制，若不清除干净，会常常复发；

7.系统隐藏目录存放文件，且很难清除；

8.清除竞争对手，保证自己利益最大化；

9.使用涉及各方面技术较多。

执行流程  

对应文件功能  

网络代理方式  

## 三、Powershell木马代码审计

木马powershell脚本开头定义了参数集，默认使用参数集Setup  
  
  

给脚本基本变量赋值，脚本名、脚本路径、服务名等。输出木马版本为2017-12-10  

自定义函数  

$argv0 = Get-Item $MyInvocation.MyCommand.Definition //获取当前运行目录根据启动参数执行对应命令  

首先默认执行的是setup  
1、获取系统类型架构

2、比较安装目录与执行目录脚本时间差，判断是否更新服务  
3、创建服务运行机制$source变量保存的是服务主函数，之后会将$source变量中的源代码编译成二进制程序  
编译位二进制程序cspsvc.exe（程序名随编译的脚本名改变而改变）。  
其功能是注册服务，注册服务后cspsvc.exe作用是带参数-SCMStart启动cspsvc.ps1脚本后，-SCMStart启动功能是重新以管理员权限运行cspsvc.ps1脚本  
  

4 、配置服务运行账户，默认为LocalSystem。  

5、尝试从c:windowsfontsarialconfig.xml配置文件中读取配置，若配置文件不存在，尝试从c:windowsSoftwareDistributionconfig.xml复制过来，若都不存在，则使用下列地址配置挖矿账户和矿池。  
  

初始化探测反木马软件、探测防火墙等配置  

如果有域，则使用域后门机制  

6、本地后门文件隐藏如果不存在文件c:windowsSoftwareDistributionconfig.xml、C:Windowsfontsarialconfig.xml，不存在隐藏文件夹C:Windowsfontsarial则创建文件夹C:Windowsfontsarial  

7、设置读取矿机WEBUI内配置信息解析格式，以供后续使用  
  

8、修改计算机注册表HKEY_LOCAL_MACHINESYSTEMSoftwareMicrosoftDriversPath  

从上述第三个步骤开始进入另外一个进程分支，即服务模式运行，即-SCM参数启动脚本  

Service段代码被加密，将代码中的iex改为echo，解密后分析其执行代码结构。  

1、通过bios信息判断机器是否是虚拟机，如果是，是哪种，不是则为物理机  

2、排除掉自己的挖矿进程外，干掉挖矿竞争对手，即带有关键字xmr、miner、programdatanew、programdatawin、programdataWindow、programdataWindows等进程。  
  
  

3、判断域名内是否带有csd、CSP、SERVER-BI、环境变量$env:COMPUTERNAME、WIN-IT9E5B2V9AE、IT9E5B、xzspn、dtlab，若有则测试127.0.0.1:5650tcp端口是否打开，如果没有打开探测路径C:Program
Files (x86)Remote Manipulator System – Host，如果有就删除C:Program Files (x86)Remote
Manipulator System –
Host，然后下载[http://185.48.59.45/uni/RMS.exe到C:ProgramDataRMS.exe，然后运行，接着更改防火墙配置；](http://185.48.59.45/uni/RMS.exe%E5%88%B0C:/ProgramData/RMS.exe%EF%BC%8C%E7%84%B6%E5%90%8E%E8%BF%90%E8%A1%8C%EF%BC%8C%E6%8E%A5%E7%9D%80%E6%9B%B4%E6%94%B9%E9%98%B2%E7%81%AB%E5%A2%99%E9%85%8D%E7%BD%AE%EF%BC%9B)  
如果IP为212.16.70.23然后下载[http://185.48.59.45/uni/RMS.exe到C:ProgramDataRMS.exe，然后运行，接着更改防火墙配置；](http://185.48.59.45/uni/RMS.exe%E5%88%B0C:/ProgramData/RMS.exe%EF%BC%8C%E7%84%B6%E5%90%8E%E8%BF%90%E8%A1%8C%EF%BC%8C%E6%8E%A5%E7%9D%80%E6%9B%B4%E6%94%B9%E9%98%B2%E7%81%AB%E5%A2%99%E9%85%8D%E7%BD%AE%EF%BC%9B)  

4、请求dns，’msupdate.info’，若无响应则连接服务器为$ms = “185.48.59.45”

5、删除计划任务  

6、查找路径  

7、停止进程JavaCu

8、如果存在sc_nmap服务，则删除  
$env:windirSystem32sc_snmp.ps1脚本和sc_nmap服务；查找进程路径名为sc_service、snmp_reciever、进程路径名为sc_snmp.ps1的进程并强行停止。

9、查看防火墙规则相关服务，并将其规则文件$env:windirSystem32firewall_rules.ps1和服务删除firewall_rules

10、终止Windows更新进程命令行为：windowsupdate.ps1

11、如果存在sc_snmp或firewall_rules服务，获取驱动路径注册表HKLM:SYSTEMSoftwareMicrosoftDriversPath中restart项，若无restart则新建键，其值为0；如果restart值为3则删除restart键值。请求计划任务start
service，如果存在则删除；创建计划任务Start Service，一分钟之后执行任务计划，运行服务。$data = (get-date).AddMinutes(1).ToString(“HH:mm”)schtasks /create /TN “Start Service” /TR
“net start cspsvc” /SC ONCE /V1 /Z /ru System /ST $data

12、如果不存在sc_snmp和firewall_rules服务，若存在任务计划名如start
service，将其删除。如果不存在目录$env:windirfontsarial，但存在$env:windirSoftwareDistributionconfig.xml，则将config.xml复制到$env:windirfontsarial。若都不存在，则在arial目录新建config.xml，将矿机配置信息写入  

13、如果存在C:WindowsSoftwareDistributionwindows.log，获取config.xml中AV变量，默认为1，则默认设定认为反木马软件不存在。添加防火墙排除项。  

若设定手工设定为0，则认为反木马软件存在，若机器不是服务器，判断其防火墙类型是windows defender或System Center Endpoint
Protection，接着添加扫描排除项。  

针对部分域，做了特定的识别。  

14、如果认定反木马软件不存在，设定矿机路径为c:windowsfontsttf，常用路径为c:windowsfontsarial，临时路径为c:windowsfontstemp。如果有域，则检查域内后门是否存在$domainsysvol$domainPolicies，接着设置注册表，将WDigest身份认证缓存在内存。  

15、fw默认设置为0，若手工设置为1，则设置地图服务Mapsvc自动运行。防火墙规则开启3389，并且远程连接地址添加”185.48.59.0/24,$ips.0.0.0/8”$ips为IP的A段。这样就可以使所有处于内网地址的基本都可以连接。  

16、Psw为账户选项，默认值为0，提供Psw参数为账户密码，并提供了group参数，且如果是管理员则利用WINNT组件添加用户  

并添加为可登录用户  

17、矿池服务器80端口若是开启，则开启757端口代理转发msupdate.info，并且703端口也代理转发到服务器185.48.59.50:80  
  

757端口为代理矿池服务器下载转发端口，703端口为矿池连接进行挖矿流量转发端口。若无法连接互联网，若为域则从域后门复制dll到$env:windirFontsarial，若域为*mi3g*，则连接代理端口192.168.10.99:14445，若能连接C2则设定该代理IP为代理服务器。若存在文件api-ms-win-core-console-l2-2-0.dll，其内容为代理服务器列表。

18、更新矿机

访问http://msupdate.info/uni/MD5/explorerx64.exe.md5，获取最新矿机、木马ps1脚本MD5值，然后对比本地矿机、木马ps1脚本MD5值决定是否更新，若有更新，则创建任务计划”update”将文件下载到c:windowsfontstemp，然后覆盖旧文件。

![](https://p2.ssl.qhimg.com/t01487e95dc75b962a6.png)

![](https://p0.ssl.qhimg.com/t0116fa381073201b72.png)

更新办法：

![](https://p1.ssl.qhimg.com/t013cf253f495c0ced0.png)

![](https://p3.ssl.qhimg.com/t01986f534528593994.png)

19、根据硬件UUID，判断硬件性能，选择挖矿模式

![](https://p0.ssl.qhimg.com/t01baca8f6e39259572.png)

20、测试连接矿池703端口，poolstemp.txt来源于pools.txt，根据配置和矿池连通性，从中选取一条配置，创建配置信息$GeneralPathconfig.json。

![](https://p3.ssl.qhimg.com/t015f85b850d006c5ce.png)

![](https://p1.ssl.qhimg.com/t017a9bfc22be08ddd2.png)

21、接着再释放一段加密代码，到c:windowssystem32driversen-USGpCheck.ps1，同上面方法，代码中的iex改为echo，解密代码，发现其作用是维护更新文件、端口转发、防火墙策略、测试矿池连通性等。

![](https://p0.ssl.qhimg.com/t0181f3138af8c1e390.png)

![](https://p1.ssl.qhimg.com/t01bd6d278220bf8867.png)

22、写入xml文件到c:windowsfonttemptask.xml，该文件作用是利用任务计划创建gpcheck，调用gpcheck.ps1

![](https://p1.ssl.qhimg.com/t01d3cb4f264d34da46.png)

23、释放加密代码到c:windowsSystem32driversWmiPrvSE.ps1，同上方法解密其代码

首先使用wmi创建了挖矿进程 c:windowsFontsttfexplorer.exe

![](https://p3.ssl.qhimg.com/t0134b43c0eabcd0d35.png)

一旦发现分析工具，则中止挖矿进程

![](https://p2.ssl.qhimg.com/t014ef3b1a9bc055571.png)

24、再次释放了一个精简版gpcheck.ps1，其主要功能不变但精简了不少检查。

**从第23个步骤开始进入explorer挖矿分支，矿机会监听999端口，通过本地访问可以获得矿机状态信息。**

![](https://p0.ssl.qhimg.com/t013b97ccec2e95f3fa.png)

账户adm，密码14370

![](https://p1.ssl.qhimg.com/t019ceae29d89696751.png)

## 四、IOCS

**URL**

http://msupdate.info/uni/explorerx64.exehttp://msupdate.info/uni/explorerx86.exehttp://msupdate.info/uni/visual.ziphttp://msupdate.info/test.txthttp://msupdate.info/uni/MD5/explorerx64.exe.MD5

http://msupdate.info/uni/MD5/explorerx86.exe.MD5

http://msupdate.info/uni/MD5/explorerx86.exe.md5

http://msupdate.info/uni/MD5/explorerx64.exe.md5

**File**

C:WindowsFontsarialC:WindowsFontsLogsC:WindowsFontstempC:WindowsFontsttfc:windowsSoftwareDistributionconfig.xml

c:windowssystem32driversen-USGpCheck.ps1

c:windowsSystem32driversWmiPrvSE.ps1

C:WindowsSystem32driversetcservices

C:WindowsSystem32driversetcprotocol

C:WindowsSystem32driversetcnetworks

C:WindowsSystem32driversetclmhosts.sam

C:WindowsSystem32driversetchosts

**Domain/Ip**

msupdate.info（185.48.59.45:80）185.48.59.52:34444185.48.59.51:24444185.48.59.50:14444

追踪：查询矿池代理服务器为俄罗斯IP，服务器也是俄语操作系统

![](https://p2.ssl.qhimg.com/t01348c83c61e5abcbe.png)

所有IP都属同一个C段，相信这至少是一个长期的据点。

## 五、处置方案

### 1、进程清理

清理转发规则：

Powershell运行以下命令

> Start-Process PowerShell.exe -ArgumentList(“-c &{netsh interface portproxy
> delete v4tov4 listenport=757;netsh interface portproxy delete v4tov4
> listenport=703;pause}”) -Verb runas

![](https://p3.ssl.qhimg.com/t01e56489b9ef4ff8b2.png)

清理带有System32driversWmiPrvSE.ps1文件路径的进程（可能已经退出）

### 2、注册表清理

病毒配置：HKEY_LOCAL_MACHINESYSTEMSoftwareMicrosoftDriversPath

![](https://p5.ssl.qhimg.com/t01c41c8eb7be16bc8a.png)

防火墙配置清除

检查防火墙配置HKLM:SOFTWAREPoliciesMicrosoftWindows
DefenderExclusions，将防火墙策略配置修改为正常状态

修改HKLMSYSTEMCurrentControlSetControlSecurityProvidersWDigestUseLogonCredential
为0为0

### 3、文件清理

删除目录及文件

C:WindowsFontsarial

C:WindowsFontsLogs

C:WindowsFontstemp

C:WindowsFontsttf

c:windowsSoftwareDistributionconfig.xml

c:windowssystem32driversen-USGpCheck.ps1

c:windowsSystem32driversWmiPrvSE.ps1

C:WindowsSystem32driversetcservices

C:WindowsSystem32driversetcprotocol

C:WindowsSystem32driversetcnetworks

C:WindowsSystem32driversetclmhosts.sam

C:WindowsSystem32driversetchosts

若为域则要清除\$domainsysvol$domainPolicies及其子目录下的explorer.exe

![](https://p4.ssl.qhimg.com/t01e12f1e181aa2dab7.png)

正常情况下文件资源管理器是看不到logs目录的，而且显示了隐藏文件夹（win10和winserver2008下）也看不到，但可以在cmd或者powershell可以探测到

![](https://p2.ssl.qhimg.com/t0143bc9a1d64d52f93.png)

使用PCHUNTER强行删除，或者进入安全模式下删除，或者使用强力的杀毒软件对指定目录进行清除。

![](https://p4.ssl.qhimg.com/t018d2a886a7e9e4b81.png)

### 4、服务清理

服务名cspsvc，显示名为Cryptographic Service Providers。

### 5、任务计划清理

任务计划GpCheck

![](https://p3.ssl.qhimg.com/t0136da96eead1ff815.png)

### 6、批量排查

Nmap批量扫描999端口

![](https://p0.ssl.qhimg.com/t014660a48538e7f062.png)

账户adm，密码14370

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **safedog** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/153070](/post/id/153070)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [木马](/tag/木马)
  * [挖矿](/tag/挖矿)
  * [加密货币](/tag/加密货币)
  * [服务器安全](/tag/服务器安全)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t01026aa3d214bcbbf7.png) safedog

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

