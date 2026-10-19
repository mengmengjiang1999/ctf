## 一、sql语句：增删改查﻿

    
    
    增：insert into 表名（字段）values（值）  
    ​  
    删：delete from 表名 where 字段=某个值新建文件夹  
    ​  
    改：update 表名 set 字段=某个值 where 条件  
    ​  
    查：select * from 表名

连接数据库：

    
    
      
    mysql -u username -p -h ip

显示数据库语句：

    
    
      
    SHOW DATABASES

显示数据库创建语句：

    
    
      
    SHOW CREATE DATABASE db_name

修改数据库:

    
    
      
    alter database 数据库名 charset=新字符集 collate=新的校对集(排序规则)

数据库删除语句：

    
    
      
    DROP DATABASE  [IF EXISTS]  db_name

使用数据库:

    
    
      
    use 数据库名; 

查看数据库

    
    
      
    show databases

## [二、字段操作]()

    
    
      
    加字段：alert table 表名 add 字段名 字段属性  
    ​  
    删除字段：alert table 表名 drop 字段名  
    ​  
    修改字段属性：alert table 表名 modify 字段名 新属性  
    ​  
    修改字段：alert table 表名 change 字段原名 字段新名 新属性  
    ​  
    查看表字段信息：desc 表名  
    ​  
    修改表名：alter table 旧表名 rename 新表名  
    ​  
    清空表数据：truncate 表名

  

## [三、数据操作]()

    
    
      
    dos命令行  
    ​  
    mysqldump -u root -p 数据库名 表名 > 文件名   导出数据库中指定的数据表  
    ​  
    mysqldump -u root -p 数据库名 > 文件名    导出指定库中所有表，不包含库本身  
    ​  
    mysqldump -u root -p --databases 库1 库2  > 文件名     导出指定的数据库  
    ​  
    mysqldump -u root --all-databases  > 文件名     导出所有的数据库  
    ​  
    mysql -u root -p 已存在的库名 < 要导入的文件    还原备份的数据表  
    ​  
    mysql -u root -p < 要导入的文件       还原备份的数据库  
    ​  
    sql语句还原数据 ：例如：MariaDB[库名]  > source  G:/1.txt  
    ​  
    mysqldump -u root -p -d 库名 > 文件名      导出数据库的结构（还原时指明数据库）

## [四、用户操作]()

    
    
      
    添加用户：grant 权限 on 库.表 to ‘用户名’@‘%’ identified by ‘密码’；  
    ​  
    例如：grant select，insert on teach.user to ‘admin’@‘%’ identified by ‘123456’  
    ​  
    刷新权限：flush privileges     
    ​  
    查看权限：show grants for ‘root’@‘localhost’；  
    ​  
    删除权限：revoke 权限 on 库.表 from 用户名@localhost  
    ​  
    查看用户：select user，host from mysql.user  
    ​  
    删除用户：drop user 用户@localhost  
    ​  
    修改管理员密码为abcd：mysqladmin -u root -p password abcd  
    ​  
    修改用户密码：set password for ‘用户名’@‘主机’ = password （新密码）

 **mysql忘记root密码：**

    
    
      
     1.结束mysql.exe进程，在dos命令执行    
    ​  
    mysqld --console --skip-grant-tables --shared-memory  
    ​  
    2.在打开一个dos窗口，直接输入mysql便会以管理员的身份强行进入  
    ​  
    3.随后进入到用户管理数据库中修改密码  
    ​  
    注意：MySQL 5.7 版本中user表中的password字段改成了authentication_string  
    ​  
    4.：修改完密码后使用 flush privileges  刷新权限（必须步骤）

  

## [五、MySQL基本语法]()

#### 1.常见注释方式

    
    
      
    单行注释： #注释内容
    
    
      
    单行注释： -- 注释内容（__空格）
    
    
      
    多行注释： /*注释内容*/

#### 2.语句行

一条语句也称为一条命令，通常用一个分号 **[(;)]()** 结束；也可以通过"delimiter 新结束符"
命令来设定新的结束符。语句的执行是以一条语句为单位进行，一次执行一条语句。

​ **大小写：**

Windows是不区分大小写的。Linux 是区分的。

    
    
      
    show databases;  SHOW DATABASES;
    
    
      
    mysql中的各种系统关键字和命令名本身是不区分大小写的mysql中自定义的名称（标识符）的大小写问题，有的区分（跟操作系统有关），有的不区分，详见如下“命名规则”;

#### 3.命名（标识符）规则：

    
    
      
    字母数字下划线，并不用数字开头。  
    对其他自己命名的标识符（字段名，函数名，过程名），不区分大小写，但也建议全使用小写，并采用下划线分割法

## [五、常用函数]()

查看当前用户

    
    
      
    user（）

查看当前库名

    
    
      
    database()

返回当前数据库的绝对路径信息

    
    
      
    @@datadir   

​ regexp（）正则匹配，在查询语句中，可以使用regexp和like代替等号

​ select *from user where username regexp('.*d.*','i');

​ secure_file_priv 当值为null时，表示不准许读和写

​ 使用 show variables like “secure_file_priv”查看该配置的值

读取文件

    
    
      
    load_file（）

写入文件

    
    
      
    into outfile（）

写入文件（支持二进制）

    
    
      
    intodump file（)

​ 文件必须写绝对路径、要拥有写的权限

## [六、数据在数据库中的存储方式]()

![1641915075_61dda2c346af5367db0fb.png!small?1641915076862](https://image.3001.net/images/20220111/1641915075_61dda2c346af5367db0fb.png!small?1641915076862)

## [七、Mysql utf8和utf8mb4的区别]()

    
    
      
    MySQL的utf8实际上不是真正的UTF-8。   
    支持每个字符最多三个字节，   
    而真正的UTF-8是每个字符最多四个字节。  
    MySQL一直没有修复这个bug,他们在2010年发布了一个叫作 utf8mb4的字符集，绕过了这个问题。当然，他们并没有对新的字符集广而告之（可能是因为这个bug让他们 觉得很尴尬）,以致于现在网络上仍然在建议开发者使用utf8,但这些建议都是错误的。  
    ​  
    简单概括如下：   
    (1)MySQL的utf8mb4是真正的UTF-8。  
    (2)MySQL的utf8是一种专属的编码，它能够编码的Unicode字符并不多。所有在使用utf8的MySQL和MariaDB用户都应该改用utf8mb4,永远都不要再使用utf8。

![1641915101_61dda2dd86371402e4ea9.png!small?1641915103180](https://image.3001.net/images/20220111/1641915101_61dda2dd86371402e4ea9.png!small?1641915103180)

## [八、存储引擎方式]()

什么是存储引擎？

    
    
      
    存储引擎也叫“表类型”，  
    是指一个表中的数据以何种方式存放在文件或内存中。  
    不同的存储引擎（表类型）提供不同的性能特性和可用功能。没有一种各方面都又具有最佳性能又具有各种功能的存储引擎。我们要做的是要根据数据的具体使用情形（需求）来选择合适的存储引擎，有的要读取速度快，有的要写入速度快，有的要具有高安全可靠性，有的要海量存储，等等。  
    ​  
    常用的存储引擎是innoDB（默认）和Myisam。

![1641915117_61dda2edf40561f0696fd.png!small?1641915119975](https://image.3001.net/images/20220111/1641915117_61dda2edf40561f0696fd.png!small?1641915119975)

## [九、MySQL数据类型]()

![1641915128_61dda2f8c5ddb2cd0d094.png!small?1641915130503](https://image.3001.net/images/20220111/1641915128_61dda2f8c5ddb2cd0d094.png!small?1641915130503)

int==>有符号的整型（有正，有负）

## [十、Mysql常用数据类型]()

如果赋值不为enum（枚举）中设置的值,则会有warnings

    
    
      
    整型:tinyint,smallint,int

  

 **1.数值型（bit) 的使用**

![1641915172_61dda3245f400381be4e5.png!small?1641915173940](https://image.3001.net/images/20220111/1641915172_61dda3245f400381be4e5.png!small?1641915173940)

 **2.数值型（小数) 的使用**

![1641915161_61dda3195e98ac2d0622a.png!small?1641915162881](https://image.3001.net/images/20220111/1641915161_61dda3195e98ac2d0622a.png!small?1641915162881)

 **3.Float和decimal的区别:**

![1641915193_61dda339e82b9430f60a0.png!small?1641915195750](https://image.3001.net/images/20220111/1641915193_61dda339e82b9430f60a0.png!small?1641915195750)

 **CHAR(size)**

    
    
      
     固定长度字符串 最大255 字符 

  

**VARCHAR(size)**

    
    
      
     可变长度字符串 最多65532个字符 要预留3个左右的字节  
    •Latin1 一个字符占一个字节，最多能存放 65532 个字符  
    •GBK 一个字符占两个字节， 最多能存 32766 个字符  
    •UTF8 一个字符占三个字节， 最多能存 21844 个字符

  

    
    
      
    Mysql要求一个行的定义长度不能超过65535bytes，  
    若定义的表长度超过这个值，则提示：**ERROR 1118 (42000): Row size too large. The maximum row size for the used table type, not counting BLOBs, is 65535. You** **have to** **change some columns to TEXT or BLOBs**

  

仅一个字段,会自动升级为mediumtext,否则会报错

![1641915210_61dda34a8ceffa8e0e8ff.png!small?1641915212031](https://image.3001.net/images/20220111/1641915210_61dda34a8ceffa8e0e8ff.png!small?1641915212031)

 **char(4) 和 varchar(4) 的比较**

    
    
    char(4) 是定长，就是说，即使你 插入 'aa' , 也会占用 分配的4个字符.
    char(4) //这个4表示字符数(绝对最大255)，不是字节数 ,不管是中文还是字母都是放四个,按字符计算，这个4表示字符数 ，不管是字母还是中文都以定义好的表的编码来存放数据.
      
      
    
    
    
    varchar(4000) 是变长，就是说，如果你插入了 'aa',实际占用空间大小是 L+1 [注：同CHAR对比，VARCHAR值保存时只保存需要的字符数，另加一个字节来记录长度(如果列声明的长度超过255，则使用两个字节)。]
      
      
    
    
    
    char 在存放空格时会丢失，varchar不会丢失存储的空格比如 在 char 中存放了 ‘aa ‘取出来值为 ‘aa'而 varchar中存放了 ‘aa ’ ,取出来还是 ‘aa ’, 空格没有丢失
      
      
    
    
    
    因为char的存放规则是当数据放入不够时，后面全面补全空格，这样就导致取出char类型的数据时会导致问题
      
      
    

  

表的所有字段加起来不能超过65535个字节

![1641915248_61dda370606b16df8332b.png!small?1641915249817](https://image.3001.net/images/20220111/1641915248_61dda370606b16df8332b.png!small?1641915249817)

 **什么时候使用 char , 什么时候使用varchar**

    
    
    答：如果数据是定长，推荐使用char，比如md5的密码,邮编，手机号等. ‪如果一个字段的长度是不确定，我们使用varchar ，比如留言,文章

float 最多支持 7 位数字

​

float 最多支持 7 位数字

DECLMAL 最多支持

  

group by

avg 是求所分的组的平均值

  

[ **having 和 where 的区别**]()

相同点:

    
    
    having ​	跟在分组后面​	where
      
      
    

不同点:

    
    
      
      
      
    

  

 **[group by 查询字段]()**

    
    
    只要你使用了group by 之后，select字段只允许是分组的的内容或者是使用聚合函数的内容，要么使用聚合函数要么是分组的依据
      
      
    

## [十一、MySQL 权限 介绍]()

#### 1\. 4个控制权限的表:

mysql中存在4个控制权限的表

    
    
    分别为:
    user表
    db表
    tables_priv表
    columns_priv表
      
      
    

#### 2\. mysql权限表的验证过程：

    
    
    1.先从user表中的Host,User,Password这3个字段中判断连接的ip、用户名、密码是否存在，存在则通过验证。
    2.通过身份认证后，进行权限分配，按照user，db，tables_priv，columns_priv的顺序进行验证。即先检查全局权限表user，如果user中对应的权限为Y，则此用户对所有数据库的权限都为Y，将不再检查db, tables_priv,columns_priv；如果为N，则到db表中检查此用户对应的具体数据库，并得到db中为Y的权限；如果db中为N，则检查tables_priv中此数据库对应的具体表，取得表中的权限Y，以此类推。
      
      
    

#### 3\. 查看权限

    
    
    创建mysql授权用户
    执行create user/grant命令(推荐方式)
    通过SQL语句直接操作mysql系统权限表回收mysql权限
    通过revoke命令收回用户权限,回收时看用户有哪些权限然后回收删除mysql用户
    通过执行drop user命令删除MySQL用户 ​					mysql> drop user bihuo@'localhost';修改mysql用户秘密​	mysql> SET PASSWORD FOR ‘bihuo’@'localhost' = PASSWORD('mypass');​	mysql> GRANT USAGE ON *.* TO ‘bihuo'@'localhost' IDENTIFIED BY 'mypass’;修改当前会话本身用户密码的方式包括:​	mysql> SET PASSWORD = PASSWORD('mypass');
      
      
    

## [十二、时间类型]()

#### 1.日期时间:

 **date类型:**

​ 支持的范围为'1000-01-01'到'9999-12-31'

 **datetime类型:**

​ 支持的范围是'1000-01-01 00:00:00'到'999-12-31 23:59:59'

  

enum枚举类型 和 set集合类型基本使用

![1641915310_61dda3ae14407740a27c1.png!small?1641915311666](https://image.3001.net/images/20220111/1641915310_61dda3ae14407740a27c1.png!small?1641915311666)

## [十三、子查询]()

 **什么是子查询？**

    
    
    子查询是指嵌入在其它sql查询语句中的select语句，也叫嵌套查询
      
      
    

**单行子查询**

    
    
    单行子查询是指只返回一行数据的子查询语句
      
      
    

**多行子查询**

    
    
    多行子查询指返回多行数据的子查询使用关键字in
      
      
    

**合并查询**

    
    
    为了合并多个select语句的结果，可以使用**集合操作符号**
      
      
    

**union**

    
    
    该操作符用于取得两个结果集的并集。当使用该操作符时，会自动去掉结果集中重复行。
      
      
    

**union all**

    
    
    该操作赋与union相似，但是它不会取消重复行,而且不会排序。
      
      
    

## [十四、mysql维护数据的完整性——约束]()

primary key(主键）-基本使用

    
    
    字段名	字段类型	primary  key用于唯一标示表行的数据，当定义主键约束后，该列不能重复，不能为空NILL
      
      
    
    
    
    1.primary key（主键）不但不能重复而且不能为null。
    2.一张表最多只能有一个主键3.一般来说一张表总有primary key ,而且是整数类型的(ecs_vote、ecs_users、ecs_goods等等)
    3.主键的指定方式 有两种 l直接在字段名后指定：字段名 primakry keyl在表定义最后写 primary key(列名); 4.如果一个字段 设置成 not null 并 unique ，从使用效果上非常像primary key
    5.使用desc 表名，可以看到primary key的情况.
      
      
    

## [十五、mysql权限]()

#### 1.mysql控制权限4张表

 **mysql中存在4个控制权限的表**

    
    
    分别为user表，db表，tables_priv表，columns_priv表
      
      
    

#### 2.mysql权限表的验证过程为：

    
    
    1.先从user表中的Host,User,Password这3个字段中判断连接的ip、用户名、密码是否存在，存在则通过验证。
    2.通过身份认证后，进行权限分配，按照user，db，tables_priv，columns_priv的顺序进行验证。即先检查全局权限表user，如果user中对应的权限为Y，则此用户对所有数据库的权限都为Y，将不再检查db, tables_priv,columns_priv；如果为N，则到db表中检查此用户对应的具体数据库，并得到db中为Y的权限；如果db中为N，则检查tables_priv中此数据库对应的具体表，取得表中的权限Y，以此类推。
      
      
    

#### 3.查看权限

    
    
    show grants for root@localhostGRANT ALL PRIVILEGES ON *.* TO ‘bihuo'@'localhost'
      
      
    

#### 4.mysql中的权限代表含义

    
    
    All/All Privileges权限---->	代表全局或者全数据库对象级别的所有权限
      
      
    
    
    
    Alter权限---->	代表允许修改表结构的权限，但必须要求有create和insert权限配合。如果是rename表名，则要求有alter和drop原表， create和insert新表的权限
      
      
    
    
    
    Alter routine权限---->	代表允许修改或者删除存储过程、函数的权限
      
      
    
    
    
    Create权限---->	代表允许创建新的数据库和表的权限
      
      
    
    
    
    Create routine权限---->	代表允许创建存储过程、函数的权限
      
      
    
    
    
    Create tablespace权限---->	代表允许创建、修改、删除表空间和日志组的权限
      
      
    
    
    
    Create temporary tables权限---->	代表允许创建临时表的权限
      
      
    
    
    
    Create user权限代表---->	允许创建、修改、删除、重命名user的权限
      
      
    
    
    
    Create view权限---->	代表允许创建视图的权限
      
      
    
    
    
    Delete权限---->	代表允许删除行数据的权限
      
      
    
    
    
    Drop权限---->	代表允许删除数据库、表、视图的权限，包括truncate table命令
      
      
    
    
    
    Event权限---->	代表允许查询，创建，修改，删除MySQL事件
      
      
    
    
    
    Execute权限---->代表允许执行存储过程和函数的权限
      
      
    
    
    
    File权限---->代表允许在MySQL可以访问的目录进行读写磁盘文件操作，可使用的命令包括load data infile,select … into outfile,load file()函数
      
      
    
    
    
    Grant option权限代表---->是否允许此用户授权或者收回给其他用户你给予的权限,重新付给管理员的时候需要加上这个权限
      
      
    
    
    
    Index权限---->	代表是否允许创建和删除索引
      
      
    
    
    
    Insert权限---->代表是否允许在表里插入数据，同时在执行analyze table,optimize table,repair table语句的时候也需要insert权限
      
      
    
    
    
    Lock权限---->代表允许对拥有select权限的表进行锁定，以防止其他链接对此表的读或写
      
      
    
    
    
    Process权限---->代表允许查看MySQL中的进程信息，比如执行show processlist, mysqladmin processlist, show engine等命令
      
      
    
    
    
    Reference权限---->是在5.7.6版本之后引入，代表是否允许创建外键
      
      
    
    
    
    Reload权限---->代表允许执行flush命令，指明重新加载权限表到系统内存中，refresh命令代表关闭和重新开启日志文件并刷新所有的表
      
      
    
    
    
    Replication client权限---->代表允许执行show master status,show slave status,show binary logs命令
      
      
    
    
    
    Replication slave权限---->代表允许slave主机通过此用户连接master以便建立主从复制关系
      
      
    
    
    
    Select权限---->代表允许从表中查看数据，某些不查询表数据的select执行则不需要此权限，如Select 1+1， Select PI()+2；而且select权限在执行update/delete语句中含有where条件的情况下也是需要的
      
      
    
    
    
    Show databases权限---->代表通过执行show databases命令查看所有的数据库名
      
      
    
    
    
    Show view权限---->代表通过执行show create view命令查看视图创建的语句
      
      
    
    
    
    Shutdown权限---->代表允许关闭数据库实例，执行语句包括mysqladmin shutdown
      
      
    
    
    
    Super权限---->代表允许执行一系列数据库管理命令，包括kill强制关闭某个连接命令， change master to创建复制关系命令，以及create/alter/drop server等命令
      
      
    
    
    
    Trigger权限---->代表允许创建，删除，执行，显示触发器的权限
      
      
    
    
    
    Update权限---->代表允许修改表中的数据的权限
      
      
    
    
    
    Usage权限---->是创建一个用户之后的默认权限，其本身代表连接登录权限
      
      
    

#### 5.增删改查mysql

 **创建mysql授权用户**

执行create user/grant命令（推荐方式）

通过insert语句直接操作MySQL系统权限表

# 创建finley 这只是创建用户并没有权限

    
    
    mysql> CREATE USER ‘bihuo'@'localhost' IDENTIFIED BY ‘bihuo.cn';
      
      
    

# 把finley 变成管理员用户

    
    
    mysql> GRANT ALL PRIVILEGES ON *.* TO ‘bihuo'@'localhost' WITHGRANT OPTION;
      
      
    

#创建用户并赋予RELOAD,PROCESS权限 ，在所有的库和表上

    
    
    mysql> GRANT RELOAD,PROCESS ON *.* TO ‘bihuo'@'localhost' identified by '123456';
      
      
    

# 创建keme用户，在test库，temp表， 上的id列只有select 权限

    
    
    mysql> grant select(id) on test.temp to bihuo@'localhost' identified by '123456';
      
      
    

**回收mysql权限**

通过revoke命令收回用户权限,回收的时候看一下这个用户有哪些权限然后回收

    
    
    mysql> show grants for bihuo@'localhost';
      
      
    
    
    
    mysql> select user,host from mysql.user;
      
      
    
    
    
    mysql> revoke PROCESS ON *.* FROM bihuo@'localhost';
      
      
    

**删除mysql用户**

通过执行drop user命令删除MySQL用户

    
    
    mysql> drop user bihuo@'localhost';
      
      
    

**修改用户密码**

    
    
    mysql> SET PASSWORD FOR ‘bihuo’@'localhost' = PASSWORD('mypass');
      
      
    
    
    
    mysql> GRANT USAGE ON *.* TO ‘bihuo'@'localhost' IDENTIFIED BY 'mypass’;
      
      
    

**修改当前会话本身用户密码的方式包括：**

    
    
    mysql> SET PASSWORD = PASSWORD('mypass');
      
      
    

