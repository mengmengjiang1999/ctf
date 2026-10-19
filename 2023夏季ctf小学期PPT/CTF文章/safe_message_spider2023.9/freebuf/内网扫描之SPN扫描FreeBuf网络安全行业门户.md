在域环境中，使用Kerberos协议进行身份验证的网络中，必须在内置账号或者用户账号下为服务器注册SPN，对于内置账号，SPN会自动进行注册。但是如果想在域账户下运行服务器，则必须要为使用的账号进行手动注册SPN。因为在域环境中的每台服务器都必须在Kerberos身份验证中注册SPN，所以我们可以通过向域控发送查询请求，从而得知我们需要的服务资源在哪台服务器上.

举个例子，当用户需要访问MSSQL服务时，系统会以当前用户身份向域控查询SPN为MSSQL的记录，找到该记录后，用户会再次与KDC通信，将KDC发放的TGT作为身份凭证发给KDC，并将需要访问的SPN发给KDC，KDC的验证服务(AC)对TGT进行解密，确认无误后将由TGS发放一张允许访问SPN对应服务的票据和该SPN对应的服务地址发给用户，用户使用该票据便可访问MSSQL服务。

SPN查询时会向域控的LDAP发起请求，这是Kerberos票据的行为一部分，所以这个操作通常很难被检测出来，相比使用扫描工具在内网中大范围的进行扫描，SPN扫描也更加的隐蔽，与安全。

1\. 使用powershell进行扫描

在域中任意一台机器上，以域用户身份运行一个powershell进程，导入脚本：

Import-Module .\Discover-PSMSSQLServers.ps1

Discover-PSMSSQLServers

执行命令利用SPN发现域中所有的MSSQL服务

继续在域机器上运行一个powershell进程，导入脚本:

Import-Module .\Discover-PSInterestingService

执行命令:

Discover-PSInterestingService

则可以查看域中多个SPN

2\. 使用Windows自带工具

执行命令:

Setspn -q */*

则可以查看当前域所有的SPN

也可以使用命令:

Setspn -T domain_name -q */*

来查看指定域的spn

可以使用命令:

Setspn -q */* | findstr “MSSQL”

来搜索指定服务的spn

以下是在网上收集的其他一些spn实例名称

AcronisAgent：针对Acronis备份和数据恢复软件  
AdtServer：带有ACS的Microsoft System Center Operations Manager（2007/2012）管理服务器  
afpserver：Apple归档协议  
AgpmServer：Microsoft高级组策略管理（AGPM）  
aradminsvc - 任务主角色服务器  
arssvc - 任务主角色服务器  
bocms：商业化CMS  
BOSSO：商业对象  
CESREMOTE：与VMWare上的Citrix VDI解决方案有关，许多VDI工作站都有这个SPN。  
cifs：通用Internet文件系统  
CmRcService：Microsoft系统中心配置管理器（SCCM）远程控制  
CUSESSIONKEYSVR：CiscoUnity VOIP系统  
cvs：CVS库  
Dfsr *：分布式文件系统  
DNS：域名服务器  
E3514235-4B06-11D1-AB04-00C04FC2DCD2：NTDS DC RPC复制  
E3514235-4B06-11D1-AB04-00C04FC2DCD2-ADAM：ADAM实例  
EDVR：ExacqVision服务  
exchangeAB：Exchange通讯簿服务（通常是支持NSPI的域控制器，也通常是所有的GC）  
exchangeMDB：RPC客户端访问服务器角色  
exchangeRFR：交换通讯簿服务  
fcsvr：Apple FinalCut Server  
FileRepService：WSFileRepService.exe  
FIMService：MicrosoftForefront标识管理器（FIM）  
ftp：文件传输协议  
GC：域控制器全局编录服务  
HDFS：Hadoop（Ambari）  
host：主机服务代表主机。HOSTSPN用于在创建服务票据时访问由Kerberos协议使用长期密钥的主机帐户。  
http：支持Kerberos身份验证的http网络服务的SPN  
Hyper-V副本服务：MicrosoftHyper-V的副本服务  
IMAP：Internet消息访问协议  
IMAP4：Internet消息访问协议版本4  
ipp：Internet打印协议  
iSCSITarget：iSCSI 配置  
kadmin：Kerberos  
ldap：LDAP服务，如域控制器或ADAM实例。  
Magfs：MaginaticsMagFS  
mapred：Cloudera  
Microsoft虚拟控制台服务：HyperV主机  
Microsoft虚拟系统迁移服务：P2V支持（Hyper-V）  
mongod：MongoDBEnterprise  
mongos：MongoDBEnterprise  
MSClusterVirtualServer：Windows群集服务器  
MSOLAPSvc：SQLServer分析服务  
MSOLAPSvc.3：SQLServer分析服务  
MSOLAPDisco.3：SQLServer分析服务  
MSOMHSvc：Microsoft系统中心运营经理（2007/2012）管理服务器  
MSOMSdkSvc：MicrosoftSystem Center Operations Manager（2007/2012）管理服务器  
MSServerCluster：Windows群集服务器  
MSServerClusterMgmtAPI：此群集API需要此SPN才能通过使用Kerberos向服务器进行身份验证  
MSSQL：Microsoft SQLServer  
MSSQLSvc：MicrosoftSQL Server  
MSSQL $ ADOBECONNECT：支持Adobe Connect的Microsoft SQL Server  
MSSQL $ BIZTALK：MicrosoftSQL Server支持Microsoft Biztalk服务器  
MSSQL $ BUSINESSOBJECTS：支持Business Objects的Microsoft SQL Server  
MSSQL $ DB01NETIQ：支持NetIQ的Microsoft SQL Server  
nfs：网络文件系统  
NPPolicyEvaluator：戴尔Quest审计员  
NPRepository 4（CHANGEAUDITOR）：戴尔Quest Change Auditor  
NPRepository4（CAAD）：戴尔Quest审核员  
NPRepository4（默认）：戴尔任务审计员  
NtFrs *：NT文件复制服务  
oracle：OracleKerberos身份验证  
pcast：苹果播客制作人  
PCNSCLNT：自动密码同步解决方案（MIIS 2003＆FIM）  
POP：邮箱协议  
POP3：邮箱协议版本3  
PVSSoap：Citrix ProvisioningServices（7.1）  
RestrictedKrbHost：使用服务类字符串等于“RestrictedKrbHost”的
SPN的服务类，其服务凭单使用计算机帐户密钥并共享会话密钥。  
RPC：远程过程调用服务  
SAP：SAP /SAPService  
SAS：SAS服务器  
SCVMM：System Center虚拟机管理器  
secshd：IBMInfoSphere  
sip：会话启动协议  
SMTP：简单邮件传输协议  
SMTPSVC：简单邮件传输协议  
SoftGrid： Microsoft应用程序虚拟化（App-V）以前的“SoftGrid”  
STS：VMWare SSO服务  
SQLAgent $ DB01NETIQ：NetIQ的SQL服务  
tapinego：与路由应用程序相关联，例如Microsoft防火墙（ISA，TMG等）  
TERMSRV：Microsoft远程桌面协议服务，又名终端服务。  
tnetd：JuniperKerberos身份验证 “Tnetd是一个守护进程，用于路由引擎和数据包转发引擎等不同组件之间的内部通信”  
vmrc：Microsoft VirtualServer 2005  
vnc：VNC服务器  
VPN：虚拟专用网络  
VProRecovery Backup Exec系统恢复代理7.0  
VProRecovery Backup Exec系统恢复代理8.0  
VProRecovery Backup Exec系统恢复代理9.0  
VProRecovery诺顿克隆代理12.0  
VProRecovery诺顿  
克隆代理14.0 VProRecovery诺顿克隆代理15.0  
VProRecovery Symantec系统恢复代理10.0  
VProRecovery Symantec系统恢复代理11.0  
VProRecovery Symantec系统恢复代理14.0  
vssrvc：微软虚拟服务器（2005）  
WSMAN：Windows远程管理（基于WS-Management标准）服务  
xmpp / XMPP：可扩展消息和呈现协议（Jabber）  
xgrid：苹果的分布式（网格）计算/ Mac OS X 10.6服务器管理  
YARN：ClouderaMapReduce

