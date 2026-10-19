## 判断是否有域

### 网络连接

查看网关IP地址、DNS的IP地址、本地地址是否和DNS服务器为同一网段、域名等。

    
    
    ipconfig /all
    

![](https://image.3001.net/images/20221026/1666748334_63588fae9b676f37e44a8.png!small)

### 系统详情

查看是否存在域.如果域显示为WORKGROUP，表示当前服务器不在域内，有则显示域名。

    
    
    systeminfo
    

![](https://image.3001.net/images/20221026/1666748335_63588faf6a27fa7fec8f4.png!small)

### 登录域

工作站、域、DNS名称显示域名（如果显示为 WORKGROUP，则表示非域环境）。  
登录域：表明当前用户是域用户登录还是本地用户登录，此处表明当前用户是域用户登录。

    
    
    net config workstation
    

![](https://image.3001.net/images/20221026/1666748336_63588fb05fbe73dd92763.png!small)

## 定位域控

### 时间服务器

一般域服务器都会同时作为时间服务器,所以使用下面命令判断是否有域。

    
    
    net time /domain
    

会有三种情况：

  1. 存在域，并且是域用户。  
![](https://image.3001.net/images/20221026/1666748337_63588fb10a4b20f24cbd0.png!small)

  2. 存在域，但不是域用户。  
![](https://image.3001.net/images/20221026/1666748337_63588fb1b9645ef1c7ff6.png!small)

  3. 不存在域。  
![](https://image.3001.net/images/20221026/1666748338_63588fb25f3d2021b1d67.png!small)

### 域控制器查询

域用户+域机器，查询当前域内域全部域控机器名。

    
    
    net group "domain controllers" /domain
    

![](https://image.3001.net/images/20221026/1666748339_63588fb3036b3bb73ca13.png!small)

### DNS解析记录查询定位

域控服务器会向 DNS 服务器注册DNS记录，以便当客户端需要加入域或者和域有其他交互的时候，可以找到它。一般DNS服务器和域控是同一台服务器。

    
    
    nslookup -type=all ldap.tcp.dc._msdcs.Domain_name
    

![](https://image.3001.net/images/20221026/1666748339_63588fb39745ba1085a18.png!small)

### SPN查询

由于 SPN 本身就是正常的 kerberos 请求，所以扫描隐蔽，它不同于 TCP 与 UDP 常规端口扫描。大部分 windows 已经自带
setspn.exe，且此操作无需管理权限。在域内机器执行：

    
    
    setspn -T test.com -Q */*
    

![](https://image.3001.net/images/20221026/1666748340_63588fb448bdc59526213.png!small)

## 定位域管

### 域管理员查询

域用户+域机器，查询当前域内域全部域管名。

    
    
    net group "Domain admins" /domain
    

![](https://image.3001.net/images/20221026/1666748341_63588fb50bd89d8ce60bc.png!small)

### PsLoggedon.exe

psloggedon.exe 可以显示本地登录的用户和通过本地计算机或远程计算机的资源登录的用户指定了用户名而不是计算机，psloggedon.exe
会搜索网络邻居中的计算机，并显示该用户当前是否已登录，其原理是通过检 验注册表里 HKEY_USERS 项的 key 值来查询谁登录过机器(同样调用了
NetSessionEnum API)， 某些功能需要拥有管理员权限才能使用。  
 **域用户+域机器**

    
    
    \\指定用户名，在网络中搜索该用户登陆的计算机
    PsLoggedon.exe Administrator
    

![](https://image.3001.net/images/20221026/1666748341_63588fb5cf0c284571497.png!small)

    
    
    \\指定要列出登录信息的计算机的名称
    PsLoggedon.exe \\DC
    

![](https://image.3001.net/images/20221026/1666748342_63588fb67910541ce7cfe.png!small)

### pveFindADUser.exe

pveFindADUser.exe 可用于查找 Active Directory 用户登录的位置，枚举域用户，以及查找在
特定计算机上登录的用户，包括本地用户、通过 RDP 登录的用户、用于运行服务和计划任务的用户账 户。运行该工具的计算机需要具有.NET Framework
2.0，并且需要具有管理员权限。

    
    
    \\获取所有目标计算机上当前登录的所有用户
    pveFindADUser.exe -current
    

![](https://image.3001.net/images/20221026/1666748343_63588fb716d820d5c04a5.png!small)

    
    
    \\指定了用户名(DOMAIN\Username)，则显示该用户登录的计算机
    pveFindADUser.exe -current TEST\test
    

![](https://image.3001.net/images/20221026/1666748343_63588fb7cad233518242b.png!small)

## 域基本信息

查询条件：域用户+域机器。

### 查询ARP缓存

查看内网是否有其他主机。

    
    
    arp -a
    

![](https://image.3001.net/images/20221026/1666748345_63588fb9a35a40cb588f0.png!small)

### 查询域机器

    
    
    net group "domain computers" /domain
    

![](https://image.3001.net/images/20221026/1666748347_63588fbbdd90eff87e8f7.png!small)

### 查询域内工作组

    
    
    net group /domain
    

![](https://image.3001.net/images/20221026/1666748348_63588fbc8578bd73f429d.png!small)

### 查看同一域内机器列表

    
    
    net view
    

![](https://image.3001.net/images/20221026/1666748349_63588fbde856bff6d1f93.png!small)

### 查看内网存在多少个域

    
    
    net view /domain
    

![](https://image.3001.net/images/20221026/1666748352_63588fc033179773c7cb9.png!small)

### 查看xxx域中的机器列表

    
    
    net view /domain:xxxx
    

![](https://image.3001.net/images/20221026/1666748354_63588fc275fa0781d8a6a.png!small)

### 查看某ip共享

    
    
    net view \\ip
    

![](https://image.3001.net/images/20221026/1666748356_63588fc491928c7c22a2d.png!small)

### 查看OWA计算机的共享资源列表

    
    
    net view \\OWA
    

![](https://image.3001.net/images/20221026/1666748358_63588fc6b92cc54937671.png!small)

### 查询域用户密码相关信息

需要在域控机器上操作

    
    
    net accounts /domain
    

![](https://image.3001.net/images/20221026/1666748360_63588fc82ec980ef82443.png!small)

### 查询信任域

返回所有信任ip的域（TEST）。

    
    
    nltest /domain_trusts /all_trusts /v /server:ip
    

![](https://image.3001.net/images/20221026/1666748361_63588fc9a9eca10f14840.png!small)

### csvde（逗号分离值目录交换）

如果您使用的是Active Directory管理中心（或Active
Directory用户和计算机）的图形界面来创建大量的用户的话，将浪费管理员很多重复的时间，您可以使用系统内置的工具程序csvde.exe,
ldifde.exe, 和dsadd.exe来批量添加用户。

    
    
    csvde -setspn 域名 -f c:\windows\temp\hack.csv
    

![](https://image.3001.net/images/20221026/1666748363_63588fcbee163835c5b7f.png!small)

  1. 将hack改为域环境的名字。

  2. 将AD活动目录的信息保存出来。

CSV中字段解释。  
![](https://image.3001.net/images/20221026/1666748367_63588fcf44a63f5b845c7.png!small)

### Ldifde（轻型目录访问协议互换个数目录交换）

下载地址：https://www.pconlife.com/fileinfo/ldifde.exe-info/  
 **前提：已知某台域机器ip与普通域用户账号密码。**

导出整个域的详细信息。

    
    
    ldifde.exe -f 输出文件名 -s 域机器ip -b 域用户名 域名 域用户密码 -n
    
    ldifde.exe -f out.ldf -s 192.168.220.143 -b administrator test Wzh`password -n
    

![](https://image.3001.net/images/20221026/1666748372_63588fd43d59ca54e30f9.png!small)

查找方法：sAMAccountName对应域用户名。  
![](https://image.3001.net/images/20221026/1666748375_63588fd712d8d1050eeff.png!small)

dNSHostName 对应域机器名。  
![](https://image.3001.net/images/20221026/1666748377_63588fd9c4c4845cc7e7c.png!small)

### DNS查询

用普通权限的域账户获得域环境中所有DNS解析记录。  
前提条件：

  1. 域控

  2. 掌握一台域机器

  3. 掌握的域用户账号密码

#### SharpAdidnsdump.exe

 **域机器+域用户**

    
    
    SharpAdidnsdump.exe 192.168.52.138
    

![](https://image.3001.net/images/20221026/1666748379_63588fdb31df79ef1f5c4.png!small)

### SPN查询

  1. 服务主体名称（SPN）是Kerberos客户端用于唯一标识给特定Kerberos目标计算机的服务实例名称。Kerberos身份验证使用SPN将服务实例与服务登录帐户相关联。

  2. 如果在整个林中的计算机上安装多个服务实例，则每个实例都必须具有自己的SPN。

  3. 如果客户端可能使用多个名称进行身份验证，则给定的服务实例可以具有多个SPN。

类型：

  1. 当一个服务的权限为Local System或Network Service，则SPN注册在域内机器帐户(Computers)下。

  2. 当一个服务的权限为一个域用户，则SPN注册在域内用户帐户(Users)下。

作用：

  1. 通过SPN，可快速定位开启了关键服务的机器，这样就不需要去扫对应服务的端口，有效规避端口扫描动作，且隐蔽性更高。

  2. 对域控制器发起LDAP查询，这是正常kerberos票据行为的一部分，因此查询SPN的操作很难被检测。

查询原理：

  1. 在 SPN 扫描时我们可以直接通过脚本，或者命令去获悉内网已经注册的 SPN 内容。

  2. 在域控中默认安装有 ADSI 编辑器，它是 LDAP 的编辑器。（在域控中运行adsiedit.msc来打开）。

  3. SPN 查询，实际上就是就是查询LDAP中存储的内容。

服务类和FQDN(对应机器名)是必需参数，端口和服务名是可选的。  
![](https://image.3001.net/images/20221026/1666748380_63588fdceb6aadabc8b12.png!small)

#### setspn

setspn是系统自带的查找和设置spn的命令。Win7和Windows Server2008自带的工具。  
 **前提：某个域机器的管理员权限（可以是本地用户，也可以是域用户）。**

    
    
    setspn -l accountname                  # 参数接受计算机名或者用户名
    
    setspn –q */*                          # 查询当前域下的所有SPN
    
    setspn –T 域名 –q */*                   # 指定域查询
    
    setspn -T hack -Q */* | findstr IIS    # 结合findstr查询自己想要的内容
    

![](https://image.3001.net/images/20221026/1666748383_63588fdfbc9040ec9f4ab.png!small)

以CN开头的每一行代表一个帐户，其下的信息是与该帐户相关联的SPN。  
对于上面的输出数据，机器帐户(Computers)为：

    
    
    CN=WIN-7,CN=Computers,DC=test,DC=com
    
    CN=WIN-XP,CN=Computers,DC=test,DC=com
    

域用户帐户(Users)为：

    
    
    CN=krbtgt,CN=Users,DC=test,DC=com
    

注册在域用户帐户(Users)下的SPN有一个：kadmin/changepw。

#### 常见SPN实例名称

    
    
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
    
    RestrictedKrbHost：使用服务类字符串等于“RestrictedKrbHost”的 SPN的服务类，其服务凭单使用计算机帐户密钥并共享会话密钥。
    
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
    

