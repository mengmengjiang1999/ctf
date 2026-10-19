## ****背景**** ** **概述****

Lockbit勒索病毒最初于2019年9月被发现，当时称之为“ABCD病毒”，该别名是参考了当时被加密文件的后缀。利用此勒索病毒进行攻击的黑客团伙以针对企业及政府组织而出名，主要目标为中国，印度，印度尼西亚，乌克兰；对英国，法国，德国等欧洲国家也有过数次攻击。

Lockbit勒索病毒主要会将终端文件进行加密并将后缀修改为.lockbit，生成Restore-My-Files.txt的勒索信息，并修改桌面背景，这个勒索病毒家族目前没有公开的解密工具，用户一旦中招只能提交大量的赎金才可以解密。

![](https://image.3001.net/images/20210722/1626940923_60f925fbdbfad8ea34413.png!small)

##  ** **主要特征****

Lockbit的特征主要是以下几点：

1、独特的解密记号：在LockBit的勒索信中Tor
URL的16字节分别对应了每个加密文件后的字节以及公共注册表项的前8个字节，从而可以让该团伙在解密的过程中，更容易定位及匹配密钥信息。

![](https://image.3001.net/images/20210722/1626941173_60f926f5c9863d2923af5.png!small)![](https://image.3001.net/images/20210722/1626941189_60f92705b86904eb13f3d.png!small)

2、存在不加害对象列表：LockBit似乎对部分国家存在“善心”，病毒文件会获取本机系统语言信息，遇到以下列表的国家或系统语言则不会进行勒索加密。

![](https://image.3001.net/images/20210722/1626941223_60f9272741d10948fcba5.png!small)

排除国家和语言列表

![](https://image.3001.net/images/20210722/1626941002_60f9264aae95a66ee1a5b.png!small)

3、独有的桌面壁纸：LockBit除了和其他勒索病毒家族一样留下勒索信之外，还会修改当前的桌面背景，它将独有的桌面背景图片储存在路径Appdata\Local\Temp下，修改注册表wallpaper项将其设置为桌面背景。

![](https://image.3001.net/images/20210722/1626941048_60f92678c979c10754e06.png!small)![](https://image.3001.net/images/20210722/1626941061_60f926853de4a8cc01ddd.png!small)

##  ** **样本**** ** **分析****

LockBit勒索病毒大量使用了英特尔的SSE指令集和特定于体系结构的功能，以提高其性能，并将这些字符串变量通过异或进行解密；

解密前：

![](https://image.3001.net/images/20210722/1626941126_60f926c6288132f3865bb.png!small)

解密后：

![](https://image.3001.net/images/20210722/1626941291_60f9276be8b0b1c85b476.png!small)

LockBit使用互斥信号量来防止多个勒索病毒在该系统上运行；

![](https://image.3001.net/images/20210722/1626941309_60f9277dd896b0a9152e2.png!small)

修改注册表SOFTWARE\Microsoft\Windows\CurrentVersion\Run让恶意的软件随着开机启动；

![](https://image.3001.net/images/20210722/1626941327_60f9278fcf1b502b1d879.png!small)

LockBit含有包含多个防病毒软件的服务列表，一旦检测到相关的防病毒软件服务则进行干预并停止防病毒软件，以避免自身被查杀；

![](https://image.3001.net/images/20210722/1626941341_60f9279d0bfb870951e93.png!small)

> 相关的防病毒软件服务列表为：wrapper, DefWatch, ccEvtMgr, ccSetMgr, SavRoam, Sqlservr,
> sqlagent, sqladhlp, Culserver, RTVscan, sqlbrowser, SQLADHLP, QBIDService,
> Intuit.QuickBooks.FCS, QBCFMonitorService, sqlwriter, msmdsrv, tomcat6,
> zhudongfangyu, vmware-usbarbitator64, vmware-converter, dbsrv12, dbeng8,
> MSSQL$MICROSOFT##WID, MSSQL$VEEAMSQL2012, SQLAgent$VEEAMSQL2012, SQLBrowser,
> SQLWriter, FishbowlMySQL, MySQL57, MSSQL$KAVCSADMINKIT,
> MSSQLServerADHelper100, SQLAgent$KAVCSADMINKIT, msftesql-Exchange,
> MSSQL$MICROSOFT##SSEE, MSSQL$SBSMONITORING, MSSQL$SHAREPOINT,
> MSSQLFDLauncher$SBSMONITORING, MSSQLFDLauncher$SHAREPOINT,
> SQLAgent$SBSMONITORING, SQLAgent$SHAREPOINT, QBFCService, QBVSS, YooBackup,
> YooIT, vss, sql, svc$, MSSQL, MSSQL$, memtas, mepocs, sophos, veeam, backup,
> bedbg, PDVF$Service, BackupExecVSSProvider, BackupExecAgentAccelerator,
> BackupExecAgentBrowser, BackupExecDiveciMediaService, BackupExecJobEngine,
> BackupExecManagementService, BackupExecRPCService, MVArmor, MVarmor64,
> stcrawagent, VSNAPVSS, VeeamTransportSvc, VeeamDeploymentService,
> VeeamNFSSvc, AcronisAgent, ARSM, AcrSch2Svc, CASAD2DWebSvc, WSBExchange,
> MSExchange

在确保“自身安全”后，LockBit将会获取主机中的文件后缀进行比对并加密；

![](https://image.3001.net/images/20210722/1626941367_60f927b7bcb56cc9342a8.png!small)

加密文件后缀列表：

> .386, .cmd, .exe, .ani, .adv, .theme, .msi, .msp, .com, .diagpkg, .nls,
> .diagcab, .lock, .ocx, .mpa, .cpl, .mod, .hta, .icns, .prf, .rtp, .diagcfg,
> .msstyles, .bin, .hlp, .shs, .drv, .wpx, .bat, .rom, .msc, .spl, .ps1, .msu,
> .ics, .key, .mp3, .reg, .dll, .ini, .idx, .sys, .ico, .Lnk, .rdp

为了防止加密某些系统文件导致操作系统异常，LockBit“很贴心”地将一些特定的系统文件排除到加密范围，使得用户可以正常打开系统；

![](https://image.3001.net/images/20210722/1626941387_60f927cb53d710bcaa654.png!small)

不加密文件列表：

> $windows.~bt, intel, msocache, $recycle.bin, $windows.~ws, tor browser,
> boot, system volume information, perflogs, google, appliction data, windows,
> windows.old, appdata

##  ** **加密过程****

遍历主机中的文件夹与文件；

![](https://image.3001.net/images/20210722/1626941400_60f927d8c1e572f9d4873.png!small)

遍历结束后，加密文件并将.lockbit加到后缀名；

![](https://image.3001.net/images/20210722/1626941420_60f927ec4d7d95df33ad3.png!small)

生成RSA的公钥 ；

![](https://image.3001.net/images/20210722/1626941431_60f927f7d24dcb0b3e987.png!small)

完成了加密会话后，RSA的完整加密会话的公钥会存储在注册表的full与public中（模数和指数，分别为 0x100 和 0x3 字节）。

![](https://image.3001.net/images/20210722/1626941453_60f9280db4b57cc5d46fe.png!small)![](https://image.3001.net/images/20210722/1626941463_60f92817c968efba68e57.png!small)

使用AES算法加密

![](https://image.3001.net/images/20210722/1626941488_60f9283099fde697fc7cb.png!small)

为了可以加密更多的主机，LockBit在加密后会通过枚举驱动号，来确定是否为网络共享的盘；

![](https://image.3001.net/images/20210722/1626941516_60f9284cf1ea367fadd76.png!small)

获取名称后，会调用共享的所有文件夹和文件，从而加密更多的文件，达到不可挽回的后果。

![](https://image.3001.net/images/20210722/1626941536_60f92860a5aa6ea4bfd6d.png!small)

通过异或来解密出勒索文件信息内容，文件内容如下：

![](https://image.3001.net/images/20210722/1626941564_60f9287cb6229e8d9a352.png!small)![](https://image.3001.net/images/20210722/1626941579_60f9288b2a00467829787.png!small)

##  ** **加固建议****

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

