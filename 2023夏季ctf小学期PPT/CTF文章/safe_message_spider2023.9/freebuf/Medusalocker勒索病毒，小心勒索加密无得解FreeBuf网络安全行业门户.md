# 背景概述

近日，深信服安全团队接到用户的勒索求助，排查发现是一款名为MedusaLocker的勒索软件家族。该勒索病毒家族具有一些独特的功能，它不仅会感染本地计算机，而且还会通过网络进行扩散，对其他主机进行加密。

为了最大程度地在受感染机器上成功加密文件，并且保证用户能够支付赎金，MedusaLocker勒索病毒不会对可执行文件进行加密。其使用AES和RSA-2048的组合，使得加密的文件解密变成不太可能。

在本文中，我们将介绍MedusaLocker勒索病毒的工作原理。

##  ** **情报分析****

 **样本名称**

|

skynet.exe  
  
---|---  
  
 **样本类型**

|

exe  
  
 **恶意类型**

|

勒索病毒  
  
 **Sha256**

|

fbf6c8f0857d888385f6bc0d46523ebcc1634e06d0e96411fc43a8ae4213d1f3  
  
勒索信息：

  

##  ** **技术分析****

ida动态获取sig服务器命名，直接定位到winmain，创建了一个硬编码的{8761ABBD-7F85-42EE-B272-A76179687C63}互斥信号量，操作之前检查mutex是否存在；

![](https://image.3001.net/images/20201203/1606995712_5fc8cf00729a7c6261d0e.png!small)

通过这个函数判断是Admin还是user账户运行；

![](https://image.3001.net/images/20201203/1606995843_5fc8cf833b15b8616e8a1.png!small)

使用GetTokenInformation确定权限；

![](https://image.3001.net/images/20201203/1606996073_5fc8d0691f4fedd20afb1.png!small)

UAC绕过，使用CMSTP是一个与Microsoft连接管理器配置文件安装程序关联的二进制文件。它接受INF文件，这些文件可以通过恶意命令武器化，以脚本（SCT）和DLL的形式执行任意代码；

![](https://image.3001.net/images/20201203/1606996108_5fc8d08c0a230b5f2762b.png!small)![](https://image.3001.net/images/20201203/1606996119_5fc8d0979a66d2fbc2c2e.png!small)

创建了新的注册表值：

![](https://image.3001.net/images/20201203/1606996140_5fc8d0acd86586274b360.png!small)

HKEY_CURRENT_USER\SOFTWARE\MDSLK\Self

创建计划性任务计划指向%AppData%\Roaming\svhost.exe

![](https://image.3001.net/images/20201203/1606996224_5fc8d100819aa1aa7c880.png!small)

建立时间间隔PT x M，使用Microsoft代码创建任务，从而过检测；

![](https://image.3001.net/images/20201203/1606996247_5fc8d117efa5ee8d9ed85.png!small)

检测服务名称是否与预先定义的列表匹配，如果匹配就终止服务；

![](https://image.3001.net/images/20201203/1606996261_5fc8d1258742183262e73.png!small)

列表：

wrapper,DefWatch,ccEvtMgr,ccSetMgr,SavRoam,sqlservr,sqlagent,sqladhlp,Culserver,RTVscan,sqlbrowser,SQLADHLP,QBIDPService,Intuit.QuickBooks.FCS,QBCFMonitorService,sqlwriter,msmdsrv,tomcat6,zhudongfangyu,SQLADHLP,vmware-usbarbitator64,vmware-converter,dbsrv12,dbeng8

wxServer.exe,wxServerView,sqlservr.exe,sqlmangr.exe,RAgui.exe,supervise.exe,Culture.exe,RTVscan.exe,Defwatch.exe,sqlbrowser.exe,winword.exe,QBW32.exe,QBDBMgr.exe,qbupdate.exe,QBCFMonitorService.exe,axlbridge.exe,QBIDPService.exe,httpd.exe,fdlauncher.exe,MsDtSrvr.exe,tomcat6.exe,java.exe,360se.exe,360doctor.exe,wdswfsafe.exe,fdlauncher.exe,fdhost.exe,GDscan.exe,ZhuDongFangYu.exe

如果后缀名是：.csv,.sql,.mdf,.NDF,.SQLITEDB,.DDL,.SQLITE,.SQLITE3,.LDF,.EDB,.FDB,.FBK,.DBF，即文件内容全部加密。

若文件为勒索信息提示文件HOW_TO_RECOVER_DATA.html，或是扩展名类型属于可执行文件和配置文件，同样不进行加密

可执行文件和配置文件列表：

.exe,.dll,.sys,.ini,.lnk,.rdp,.encrypted,.READINSTRUCTIONS,.recoverme,.Readinstructions,.hivteam,.hiv,.386,.adv,.ani,.bat,.bin,.cab,.cmd,.com,.cpl,.cur,.deskthemepack,.diagcab,.diagcfg,.diagpkg,.dll,.drv,.exe,.hlp,.icl,.icns,.ico,.ics,.idx,.ldf,.lnk,.log,.mod,.mpa,.msc,.msp,.msstyles,.msu,.nls,.nomedia,.ocx,.prf,.ps1,.rom,.rtp,.scr,.shs,.spl,.sys,.theme,.themepack,.wpx,.lock,.key,.hta,.msi,.enc,.deadfiles,.lockernetwork,.monster,.NETFULL,.shanghai,.support,.DE,.netlock,.BR,.LOCK,.shanghai2,.monster,.MY,.GR,.ID,.MA,.HU,.IN,.BG,.titan,.cryptocrypto,.dodik,.shanghai3,.TW,.shanghai4,.AU,.lockes,.DEDE,.RS,.local,.shanghai5,.shanghai6,.shanghai7,.locklock,.AULOCK,.FRFR,.lockers,.PedroChicken,.DogUlitos,.datalock,.stopfiles,.viets,.ILLOCK,.GBLOCK,.lokes,.KRLOCK,.AU,.KRLOCK2,.KRLOCK3,.KRLOCK4,.shanghai8,.sglock,.shanghai9,.shan,.EG,.grgr,.locks,.CN,.CN2,.locklock,.cnlock,.netlock,.netlock2,.vikings,.usus,.lockfilesus,.creepers,.shanghaiX,.kwlock,.mzlock,.lklock,.zoomzoom,.lockfiles,.shanghai11pro,.locklock,.wtf,.diablo,.nett,.lock,.de,.IL,.cn,.batman,.valhalla,.mx,.barracuda,.scheisse,.EG,.IT,.kw,.fr,.babadook,.tw,.us,.Readinstructions,.diablo,.KR,.kimchin,.help,.lt,.us,.skynet,.au,.ZA,.AR,.dolock,.uslock,.ReadInstructions,.zalock,.detrov,.skynet

禁止系统恢复，使用vssadmin，WMI删除所有卷，使用bcdedit命令防止启动时候进入恢复模式；

![](https://image.3001.net/images/20201203/1606996282_5fc8d13ab3033c119cf78.png!small)

清除回收站；

![](https://image.3001.net/images/20201203/1606996296_5fc8d14872fe3faa18397.png!small)

传入的a1 = 1，普通用户和管理员权限下都可以使用网络共享；

![](https://image.3001.net/images/20201203/1606996304_5fc8d150d70569239e99c.png!small)

带有$的文件和文件夹不加密，不加密的文件以及文件夹列表。

![](https://image.3001.net/images/20201203/1606996315_5fc8d15b8a89fc2fe691b.png!small)

不加密的文件以及文件夹列表：

ALLUSERSPROFILE

PUBLIC

TMP

USERPROFILE

\\\AppData

ProgramData

PROGRAMFILES(x86)

SYSTEMDRIVE

\\\Program Files

\\\Application Data

\\\intel

\\\nvidia

\\\Users\\\All Users

\\\Windows

\\\Program Files\\\Microsoft\\\Exchange Server

\\\Program Files (x86)\\\Microsoft\\\Exchange Server

\\\Program Files\\\Microsoft SQL Server

\\\Program Files (x86)\\\Microsoft SQL Server

通过重启来判定文件打开与加密与否 从而让更多的文件进行加密；

![](https://image.3001.net/images/20201203/1606996332_5fc8d16cd6b94d2d64845.png!small)

文件进行加密：

![](https://image.3001.net/images/20201203/1606996401_5fc8d1b1d9238687289e4.png!small)

加密公钥：

BgIAAACkAABSU0ExAAgAAAEAAQBtv9E5cdLPoTK8PwG0VTbxxURbhYM00jmY1b22v+Nwoe6+Vi6zHYcP5JmmueP4FBZBwANscT6dGxHpP4f4l9L9b/VLT6npX7+821EksPXaUJ8piYp8TCQPKRLJt6v7foVnI7jRW//K0wX9YmF7JWbBQROHPQTX7g3CQqZM7xGT4PfMa8g7+UBbstiEThpJo8PE1pgHfZrUFyiMwAv1hoXvaWVeAHKGOvoV+pKZ6Qi2fBCyJFmfL3hChhDWzIjp5oWd3l/RuSgET1sNAV8lkQPpf80OwlxFls5C8OnoG2d7eZJXDhcelK6K67Pp1Y6nC/B5mGpMhERMGnzSg9JkcrOn

![](https://image.3001.net/images/20201203/1606996390_5fc8d1a6712ebec9a71fe.png!small)

缺少私钥所以无法解密

与本地网络；建立链接，查找共享

![](https://image.3001.net/images/20201203/1606996376_5fc8d1986fcbb267f22cd.png!small)

查找SMB共享，除了带有$的共享其他都添加到列表中

![](https://image.3001.net/images/20201203/1606996366_5fc8d18e4b089a0747e79.png!small)

每个搜寻的目录下创建勒索信息文件HOW_TO_RECOVER_DATA.html 告诉我们如何购买

##  ** **加固建议****

> 尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；
>
> 尽量避免打开不明邮件;
>
> 3\. 定期检测系统漏洞并且及时进行补丁修复。

