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

如果连Oracle不会安装，怎么进行下一步的研究Oracle数据库安全！

## 二、Oracle安装

### 1、Oracle_11g_64位安装

双击setup进行安装：

![1626489203_60f24173f322da4a5d481.png!small?1626489206552](https://image.3001.net/images/20210717/1626489203_60f24173f322da4a5d481.png!small?1626489206552)

选择是继续安装：

![1626489209_60f24179552ff15f1fe55.png!small?1626489209461](https://image.3001.net/images/20210717/1626489209_60f24179552ff15f1fe55.png!small?1626489209461)

去掉勾选：

![1626489232_60f241905deba22228230.png!small?1626489232598](https://image.3001.net/images/20210717/1626489232_60f241905deba22228230.png!small?1626489232598)

选择是：

![1626489228_60f2418cd364ffbd95a11.png!small?1626489228969](https://image.3001.net/images/20210717/1626489228_60f2418cd364ffbd95a11.png!small?1626489228969)

选择创建和配置数据库：

![1626489238_60f241969fb0e6efd8746.png!small?1626489239006](https://image.3001.net/images/20210717/1626489238_60f241969fb0e6efd8746.png!small?1626489239006)

选择桌面类：

![1626489245_60f2419d124762d7f139f.png!small?1626489246170](https://image.3001.net/images/20210717/1626489245_60f2419d124762d7f139f.png!small?1626489246170)

在数据库版本选择标准版：

![1626489249_60f241a1e86a6d6ae59fb.png!small?1626489250168](https://image.3001.net/images/20210717/1626489249_60f241a1e86a6d6ae59fb.png!small?1626489250168)

在字符集选择UTF8：

![1626489254_60f241a635336a19e99df.png!small?1626489254507](https://image.3001.net/images/20210717/1626489254_60f241a635336a19e99df.png!small?1626489254507)

这里必须输入数据库名和密码：

![1626489258_60f241aaeeef5ea6dc342.png!small?1626489260394](https://image.3001.net/images/20210717/1626489258_60f241aaeeef5ea6dc342.png!small?1626489260394)

点击完成即可：

![1626489263_60f241afa97aa86cf3100.png!small?1626489264236](https://image.3001.net/images/20210717/1626489263_60f241afa97aa86cf3100.png!small?1626489264236)

### 2、安装NET Framework 3.5

这里需要安装.NET Framework 3.5：  
![1626489270_60f241b6af626504b8d7d.png!small?1626489270987](https://image.3001.net/images/20210717/1626489270_60f241b6af626504b8d7d.png!small?1626489270987)

服务器管理器中选择即可：  
![1626489294_60f241ce395e181fea5ed.png!small?1626489296465](https://image.3001.net/images/20210717/1626489294_60f241ce395e181fea5ed.png!small?1626489296465)

选择安装：  
![1626489299_60f241d39ee2018476628.png!small?1626489301835](https://image.3001.net/images/20210717/1626489299_60f241d39ee2018476628.png!small?1626489301835)

然后等待安装即可：  
![1626489304_60f241d8c92f4a1ce1068.png!small?1626489306732](https://image.3001.net/images/20210717/1626489304_60f241d8c92f4a1ce1068.png!small?1626489306732)

点击口令关系设置：  
![1626489314_60f241e25ce0a9a9cc8c6.png!small?1626489315831](https://image.3001.net/images/20210717/1626489314_60f241e25ce0a9a9cc8c6.png!small?1626489315831)

完成查看设置：  
![1626489319_60f241e76798c0c33c40f.png!small?1626489320102](https://image.3001.net/images/20210717/1626489319_60f241e76798c0c33c40f.png!small?1626489320102)![1626489323_60f241eb4ece52a6b2cfc.png!small?1626489324659](https://image.3001.net/images/20210717/1626489323_60f241eb4ece52a6b2cfc.png!small?1626489324659)![1626489328_60f241f0aff311293c953.png!small?1626489330918](https://image.3001.net/images/20210717/1626489328_60f241f0aff311293c953.png!small?1626489330918)到和一步就完成安装了，这里查看了windows服务状态已经开启了Oracle的服务！

## 三、sqldevelope安装

继续安装sqldevelope_19.2_64位，进行Oracle管理数据环境！这是绿色版的软件，直接双击打开即可！

![1626489335_60f241f7e035f572b33dc.png!small?1626489337541](https://image.3001.net/images/20210717/1626489335_60f241f7e035f572b33dc.png!small?1626489337541)

双击打开sqldeveloper：等待安装  
![1626489341_60f241fdaefcff5e28626.png!small?1626489342937](https://image.3001.net/images/20210717/1626489341_60f241fdaefcff5e28626.png!small?1626489342937)

选择否即可：  
![1626489346_60f24202933ff6114885b.png!small?1626489348226](https://image.3001.net/images/20210717/1626489346_60f24202933ff6114885b.png!small?1626489348226)

点击左上角+号：  
![1626489351_60f24207a435160e89ee8.png!small?1626489353616](https://image.3001.net/images/20210717/1626489351_60f24207a435160e89ee8.png!small?1626489353616)

填入数据库用户名密码：（这是在创建设置的）  
![1626489356_60f2420c788593ab12011.png!small?1626489357666](https://image.3001.net/images/20210717/1626489356_60f2420c788593ab12011.png!small?1626489357666)

输入完成后点击保存：  
![1626489361_60f242113e84b5d70bb3b.png!small?1626489361526](https://image.3001.net/images/20210717/1626489361_60f242113e84b5d70bb3b.png!small?1626489361526)

成功登录数据库：  
![1626489365_60f24215988d7d0830aca.png!small?1626489365769](https://image.3001.net/images/20210717/1626489365_60f24215988d7d0830aca.png!small?1626489365769)

测试查询：  
![1626489371_60f2421b488c74c71a20c.png!small?1626489374558](https://image.3001.net/images/20210717/1626489371_60f2421b488c74c71a20c.png!small?1626489374558)

成功登录本地Oracle数据库进行查看！

内网中经常会遇到站库分离的Oracle，在打下站点后可以通过配置文件连接上数据库进行渗透

## 二、Oracle权限

ORACLE系统提供三种权限：Object 对象级、System 系统级、Role 角色级，这些权限可以授予给用户、特殊用户public或角色。

如果授予一个权限给特殊用户”Public”（用户public是oracle预定义的，每个用户享有这个用户享有的权限），那么就意味作将该权限授予了该数据库的所有用户。

 **权限被大体分为两类：**

    
    
    系统权限：系统规定用户使用数据库的权限。（系统权限是对用户而言)。
    实体权限：某种权限用户对其它用户的表或视图的存取权限。（是针对表或视图而言的）
    

### 1、系统权限

系统权限就是我们常见的CREATE SESSION、ALTER SESSION等权限，这些权限通常通过角色来进行分配

oracle中有几个常见的预定义角色：

    
    
    DBA: 拥有全部特权，是系统最高权限，只有DBA才可以创建数据库结构
    RESOURCE: 拥有Resource权限的用户只可以创建实体，不可以创建数据库结构
    CONNECT: 拥有Connect权限的用户只可以登录Oracle，不可以创建实体，不可以创建数据库结构
    

一般普通用户拥有connect、resource角色，而管理员拥有connect、resource、dba角色

### 3、实体权限

简单说就是用户对表、视图、存储过程等有什么权限

    
    
    表权限：SELECT、DELETE、UPDATE、INSERT、ALTER
    视图权限：SELECT、DELTE、INSERT、UPDATE
    过程、函数、程序包权限：EXECUTE、DEBUG
    

### 4、权限查询

1）查看所有角色：

    
    
    select * from dba_roles;
    

![1626489379_60f24223b6afc799f4439.png!small?1626489380518](https://image.3001.net/images/20210717/1626489379_60f24223b6afc799f4439.png!small?1626489380518)

2）当前用户被激活的全部角色:

    
    
    select * from session_roles;
    

![1626489386_60f2422aadbf56b0387d8.png!small?1626489388473](https://image.3001.net/images/20210717/1626489386_60f2422aadbf56b0387d8.png!small?1626489388473)

3）当前用户被授予的角色:

    
    
    select * from user_role_privs;
    

![1626489392_60f2423074b39732642a3.png!small?1626489393600](https://image.3001.net/images/20210717/1626489392_60f2423074b39732642a3.png!small?1626489393600)

4）当前用户是否为DBA：

    
    
    select t.DEFAULT_ROLE from user_role_privs t where t.granted_role='DBA';
    

![1626489398_60f2423619be417bf8b40.png!small?1626489399355](https://image.3001.net/images/20210717/1626489398_60f2423619be417bf8b40.png!small?1626489399355)

5）当前用户所拥有的全部权限：

    
    
    select * from session_privs;
    

![1626489402_60f2423a9c97b7c10a0ea.png!small?1626489404598](https://image.3001.net/images/20210717/1626489402_60f2423a9c97b7c10a0ea.png!small?1626489404598)

6）当前用户的系统权限:

    
    
    select * from user_sys_privs;
    

![1626489407_60f2423fd19f1c67bd19d.png!small?1626489409860](https://image.3001.net/images/20210717/1626489407_60f2423fd19f1c67bd19d.png!small?1626489409860)

7）当前用户的表级权限:

    
    
    select * from user_tab_privs;
    

![1626489412_60f24244594e778c2744a.png!small?1626489415120](https://image.3001.net/images/20210717/1626489412_60f24244594e778c2744a.png!small?1626489415120)

8）查询某个用户所拥有的系统权限:

    
    
    select * from dba_sys_privs;
    

![1626489417_60f2424985e2a89cca53a.png!small?1626489419176](https://image.3001.net/images/20210717/1626489417_60f2424985e2a89cca53a.png!small?1626489419176)

9）查看角色(只能查看登陆用户拥有的角色)所包含的权限:

    
    
    select * from role_sys_privs;
    

![1626489453_60f2426dbe641896dc48a.png!small?1626489456123](https://image.3001.net/images/20210717/1626489453_60f2426dbe641896dc48a.png!small?1626489456123)

10）查看用户的java权限（用户名必须大写）：

    
    
    select * from user_java_policy where grantee_name='SCOTT';
    

  

![1626489460_60f24274447dcfe4f1680.png!small?1626489461210](https://image.3001.net/images/20210717/1626489460_60f24274447dcfe4f1680.png!small?1626489461210)

    
    
    -- 下面这样在sqlplus中输出会友好一些
    COL TYPE_NAME FOR A30;
    COL NAME FOR A30;
    COL ACTION FOR A10;
    SELECT TYPE_NAME, NAME, ACTION FROM user_java_policy WHERE grantee_name = 'TEST4';
    

### 5、权限更改

可以通过GRANT 和 REVOKE 命令来对账户进行权限的授予和撤回，一般这些操作会由DBA用户(SYS用户和SYSTEM用户)来执行

而权限的赋予通常也是通过角色(Role)这个“桥梁”来做的（当然也可以直接赋给user），举个例子，创建一个用户，并给该用户赋予create
session和create procedure：

1）先创建一个test/test的用户

    
    
    create user test identified by test;
    

![1626489470_60f2427ed26c8fbef1f39.png!small?1626489471196](https://image.3001.net/images/20210717/1626489470_60f2427ed26c8fbef1f39.png!small?1626489471196)  
2）然后创建一个role

    
    
    create role testrole;
    

![1626489475_60f24283529317c4769e2.png!small?1626489476294](https://image.3001.net/images/20210717/1626489475_60f24283529317c4769e2.png!small?1626489476294)

3）然后将connect和create procedure赋给testrole：

    
    
    grant connect,create procedure to testrole;
    

![1626489479_60f242875814b22f2bff5.png!small?1626489479646](https://image.3001.net/images/20210717/1626489479_60f242875814b22f2bff5.png!small?1626489479646)

4）再将testrole这个角色给用户test

    
    
    grant testrole to test;
    

![1626489483_60f2428b331c752d4981a.png!small?1626489483203](https://image.3001.net/images/20210717/1626489483_60f2428b331c752d4981a.png!small?1626489483203)

5）这样我们可以将testrole给多个用户，修改权限时只需要添加/删除角色的权限即可，方便批量管理，类似Active Directory中的组

6）如果想要收回某个权限，则使用revoke：

    
    
    revoke create procedure from testrole;
    

![1626489487_60f2428fe9be4e3d5df8d.png!small?1626489487998](https://image.3001.net/images/20210717/1626489487_60f2428fe9be4e3d5df8d.png!small?1626489487998)

7）修改用户密码：

    
    
    alter user test identified by test;
    

8）删除用户和角色：

    
    
    drop user test cascade;
    
    drop role testrole;
    

![1626489492_60f24294678631980c403.png!small?1626489492454](https://image.3001.net/images/20210717/1626489492_60f24294678631980c403.png!small?1626489492454)

通过以上的命令学习，我们在今后遇到oracle就可以进行多种需求操作了！就不会因为无知而不知道如何下手了！加油小伙伴们~

## 五、总结

今天学习了Oracle的版本安装后，还学习了各种基础的命令操作，也是在渗透中最急需了解的命令内容，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）......
    

接下来在《服务攻防之数据库Oracle（下）》会接触到如何对Oracle在各种环境中是如何提权的，如何提权渗透等方法，请看下篇服务攻防之数据库Oracle下篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

