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

## 二、查询数据

### 1、表单查询

![1625812535_60e7ee37c381d5f248793.png!small?1625812537835](https://image.3001.net/images/20210709/1625812535_60e7ee37c381d5f248793.png!small?1625812537835)

    
    
    1. select * from biao1;   #查询所有数据
    2. select username from biao1;    #查询单个类型数据
    3. select username,password from biao1;   #查询多个类型数据
    

### 2、按条件查询

![1625812539_60e7ee3b243f729bb8e0c.png!small?1625812539459](https://image.3001.net/images/20210709/1625812539_60e7ee3b243f729bb8e0c.png!small?1625812539459)

命令：

    
    
    select * from biao1 where id=1;
    #按指定条件查询
    select * from biao1 where id<=1;
    
    关系运算符说明：
    = 	等于
    <> 	不等于
    != 	不等于< 小于
    <= 	小于等于
    > 	大于
    >= 	大于等于
    

### 3、带 IN 关键字的查询

![1625812544_60e7ee408a24bc15a7acd.png!small?1625812544946](https://image.3001.net/images/20210709/1625812544_60e7ee408a24bc15a7acd.png!small?1625812544946)

命令：

    
    
    select * from biao1 where id in(1,2,3);
    select * from biao1 where id not in(1,2,3);
    

### 4、空值查询

![1625812549_60e7ee454d30d7105791c.png!small?1625812549822](https://image.3001.net/images/20210709/1625812549_60e7ee454d30d7105791c.png!small?1625812549822)

命令：

    
    
    select * from biao1 where id is not null;
    select * from biao1 where id is null;
    

### 5、去掉重复查询

![1625812553_60e7ee497684057ea4d53.png!small?1625812554375](https://image.3001.net/images/20210709/1625812553_60e7ee497684057ea4d53.png!small?1625812554375)

命令：

    
    
    select distinct username from biao1;
    

### 6、带 LIKE 关键字进行模糊查询

常用百分号通配符：  
![1625812558_60e7ee4ea9c831857543d.png!small?1625812559632](https://image.3001.net/images/20210709/1625812558_60e7ee4ea9c831857543d.png!small?1625812559632)

命令：

    
    
    select * from biao1 where username like "d%";
    select * from biao1 where username like "%d%";
    

下划线通配符：  
![1625812563_60e7ee53e8689225c090f.png!small?1625812564511](https://image.3001.net/images/20210709/1625812563_60e7ee53e8689225c090f.png!small?1625812564511)

命令：

    
    
    select * from biao1 where username like "dayu_";   
    select * from biao1 where username like "d____";
    #一个数值加一个_
    

### 7、带 AND和or 关键字的多条件查询

带 AND 关键字的多条件查询：  
![1625812568_60e7ee589843ae63018b9.png!small?1625812569067](https://image.3001.net/images/20210709/1625812568_60e7ee589843ae63018b9.png!small?1625812569067)

命令：

    
    
    select * from biao1 where id<7 and username='test1';
    

带 OR 关键字的多条件查询：  
![1625812573_60e7ee5d14786be8d7a08.png!small?1625812574307](https://image.3001.net/images/20210709/1625812573_60e7ee5d14786be8d7a08.png!small?1625812574307)

命令：

    
    
    select * from biao1 where id<7 or username='test1';
    select * from biao1 where id=5 or username='test1';
    

OR 和 AND 一起使用：  
![1625812577_60e7ee61bc99a564538c1.png!small?1625812578503](https://image.3001.net/images/20210709/1625812577_60e7ee61bc99a564538c1.png!small?1625812578503)

命令：

    
    
    select * from biao1 where id>2 and password='12345116' or username='test';
    select * from biao1 where id>2 and password='123456' or username='testa';
    select * from biao1 where id>2 and password='123456' or username='test11'
    

OR 和 AND 一起使用的时候，AND 的优先级高于 OR，因此二者一起使用时，会先运算 AND 两边的表达式，再运算 OR 两边的表达式。

## 三、高级查询数据

### 1、聚合查询

![1625812583_60e7ee67e37fe743bc51d.png!small?1625812585843](https://image.3001.net/images/20210709/1625812583_60e7ee67e37fe743bc51d.png!small?1625812585843)

命令：

    
    
    select count(id) from biao1；
    select count(*) from biao1;
    
    select sum(id) from biao1;
    select avg(id) from biao1;
    select max(id) from biao1;
    select min(id) from biao1;
    
    COUNT() 	返回某列的行数
    SUM()		返回某列值的和
    AVG() 		返回某列的平均值
    MAX() 		返回某列的最大值
    MIN() 		返回某列的最小值
    

### 2、分组查询

1）单独使用 GROUP BY 进行分组  
![1625812590_60e7ee6ec2603b1c1f8f8.png!small?1625812591240](https://image.3001.net/images/20210709/1625812590_60e7ee6ec2603b1c1f8f8.png!small?1625812591240)

命令：

    
    
    select * from biao1 group by password;
    select * from biao1 group by username;
    

2） GROUP BY 和 HAVING 关键字一起使用  
![1625812595_60e7ee73da13d96c50895.png!small?1625812596330](https://image.3001.net/images/20210709/1625812595_60e7ee73da13d96c50895.png!small?1625812596330)

    
    
    select max(id) from biao1 group by username;
    select count(id) from biao1 group by username;
    

HAVING关键字和WHERE关键字的作用相同，区别在于HAVING 关键字可以跟聚合函数，而 WHERE 关键字不能。通常HAVING
关键字都和GROUP BY一起使用，用于对分组后的结果进行过滤。

例如：

![1625812600_60e7ee789585a111d1b72.png!small?1625812601116](https://image.3001.net/images/20210709/1625812600_60e7ee789585a111d1b72.png!small?1625812601116)

命令：

    
    
    select * from biao1 group by username having sum(id)<6;
    #查询sum函数求和中小于6的数据返回
    

### 3、使用 LIMIT 限制查询结果的数量

![1625812604_60e7ee7cecb5365d7b0f2.png!small?1625812605757](https://image.3001.net/images/20210709/1625812604_60e7ee7cecb5365d7b0f2.png!small?1625812605757)

命令：

    
    
    select * from biao1 limit 1;
    select * from biao1 limit 4;
    select * from biao1 limit 1,5;  #显示1~5的结果
    

### 4、为表和字段取别名

1）为表取别名

![1625812609_60e7ee81a277d09ecb7b7.png!small?1625812610325](https://image.3001.net/images/20210709/1625812609_60e7ee81a277d09ecb7b7.png!small?1625812610325)

命令：

    
    
    select * from biao1 as u where u.id=2;
    #数据量非常大的情况下，用as定义类型别名查询
    

2）为字段别名  
![1625812613_60e7ee85aaf2887068813.png!small?1625812614583](https://image.3001.net/images/20210709/1625812613_60e7ee85aaf2887068813.png!small?1625812614583)

命令：

    
    
    select username as n from biao1;
    select username as myname from biao1;
    #字段名username变成myname，在以后会使用到
    

## 四、mysql的子查询

### 1、where型子查询

![1625812619_60e7ee8b09c071bf4cb32.png!small?1625812619518](https://image.3001.net/images/20210709/1625812619_60e7ee8b09c071bf4cb32.png!small?1625812619518)

命令：

    
    
    select * from biao1 where id in (select * from biao1 where id>5);
    # "*"类型需要选择需要查询的类型， （把内层查询结果当作外层查询的比较条件）
    select * from biao1 where id in (select id from biao1 where id>5);
    

### 2、from型子查询

![1625812623_60e7ee8f5376709f47e0a.png!small?1625812623645](https://image.3001.net/images/20210709/1625812623_60e7ee8f5376709f47e0a.png!small?1625812623645)

命令：

    
    
    select * from (select * from biao1 where id<4) as age_1;
    #(把内层的查询结果供外层再次查询)
    #(select * from users where id<4)查询出来的是一个集合别名为age_1
    #例如：select * from age_1 内容一样
    

### 3、exists型子查询

![1625812628_60e7ee941495d9037272b.png!small?1625812628492](https://image.3001.net/images/20210709/1625812628_60e7ee941495d9037272b.png!small?1625812628492)

命令：

    
    
    select * from biao1 where exists(select * from biao1 where id>2);
    #（把外层查询结果拿到内层，看内层的查询是否成立）
    #假如（）内返回成立，则输出所有，返回不成立则无
    

### 4、联合查询（两个表的查询）

![1625812632_60e7ee9872d9c5dd807ac.png!small?1625812633399](https://image.3001.net/images/20210709/1625812632_60e7ee9872d9c5dd807ac.png!small?1625812633399)

利用前面的知识创建一个表，然后添加三行数据。  
![1625812636_60e7ee9cb149366e838cf.png!small?1625812637354](https://image.3001.net/images/20210709/1625812636_60e7ee9cb149366e838cf.png!small?1625812637354)

命令：

    
    
    select * from biao1 union select *,1 from biao2;
    #这里*,1 指的是两个表列不一致的情况下，添加可相匹配后列出数据
    

## 五、数据库内链接、左和右连接操作

### 1、利用navicat操作数据库

![1625812642_60e7eea290d7b929c534e.png!small?1625812644107](https://image.3001.net/images/20210709/1625812642_60e7eea290d7b929c534e.png!small?1625812644107)  
登录数据库；

![1625812646_60e7eea6c844e5dbaef19.png!small?1625812648420](https://image.3001.net/images/20210709/1625812646_60e7eea6c844e5dbaef19.png!small?1625812648420)  
这就是我们之前学习操作的四个表；

![1625812651_60e7eeab3a793e68f0d99.png!small?1625812652236](https://image.3001.net/images/20210709/1625812651_60e7eeab3a793e68f0d99.png!small?1625812652236)  
创建a_new表内容如图；

![1625812660_60e7eeb4893a434eed459.png!small?1625812661306](https://image.3001.net/images/20210709/1625812660_60e7eeb4893a434eed459.png!small?1625812661306)  
创建b_new表内容如图；

![1625812664_60e7eeb8b3fe3dc38b61a.png!small?1625812667110](https://image.3001.net/images/20210709/1625812664_60e7eeb8b3fe3dc38b61a.png!small?1625812667110)  
开始查询；

### 2、数据库内连接

![1625812670_60e7eebe4e31ad77e1e60.png!small?1625812673103](https://image.3001.net/images/20210709/1625812670_60e7eebe4e31ad77e1e60.png!small?1625812673103)

关键字：inner join on  
说明：组合两个表中的记录，返回关联字段相符的记录，也就是返回两个表的交集（阴影）部分。

    
    
    select * from a_new a INNER JOIN b_new b on a.classid=b.user_id;
    

### 3、数据库左连接

![1625812676_60e7eec422b54316107b5.png!small?1625812678076](https://image.3001.net/images/20210709/1625812676_60e7eec422b54316107b5.png!small?1625812678076)

关键字：left join on / left outer join on  
说明：left join 是left outer join的简写，它的全称是左外连接，是外连接中的一种。  
左(外)连接，左表(a_table)的记录将会全部表示出来，而右表(b_table)只会显示符合搜索条件的记录。右表记录不足的地方均为NULL。

    
    
    select * from a_new a LEFT JOIN b_new b on a.classid=b.user_id;
    

### 4、数据库右链接

![1625812681_60e7eec968fb2a24f97ac.png!small?1625812683568](https://image.3001.net/images/20210709/1625812681_60e7eec968fb2a24f97ac.png!small?1625812683568)

关键字：right join on / right outer join on  
说明：right join是right outer join的简写，它的全称是右外连接，是外连接中的一种。  
与左(外)连接相反，右(外)连接，左表(a_table)只会显示符合搜索条件的记录，而右表(b_table)的记录将会全部表示出来。左表记录不足的地方均为NULL。

    
    
    select * from a_new a RIGHT JOIN b_new b on a.classid=b.user_id;
    

## 六、数据库-IFORMATION_SCHEMA详解

### 1、前言背景

跨库查询 是 SQL注入的一种：

information_schema数据库是MySQL自带的，它提供了访问数据库元数据的方式。什么是元数据呢？元数据是关于数据的数据，如数据库名或表名，列的数据类型，或访问权限等。有些时候用于表述该信息的其他术语包括“数据词典”和“系统目录”。

在MySQL中，把 information_schema
看作是一个数据库，确切说是信息数据库。其中保存着关于MySQL服务器所维护的所有其他数据库的信息。如数据库名，数据库的表，表栏的数据类型与访问权
限等。在INFORMATION_SCHEMA中，有数个只读表。它们实际上是视图，而不是基本表，因此，你将无法看到与之相关的任何文件。

### 2、information_schema数据库表

1）information_schema数据库表说明：

    
    
    SCHEMATA表：提供了当前mysql实例中所有数据库的信息。是show databases的结果取之此表。
     
    TABLES表：提供了关于数据库中的表的信息（包括视图）。详细表述了某个表属于哪个schema，表类型，表引擎，创建时间等信息。是show tables from schemaname的结果取之此表。
     
    COLUMNS表：提供了表中的列信息。详细表述了某张表的所有列以及每个列的信息。是show columns from schemaname.tablename的结果取之此表。
     
    STATISTICS表：提供了关于表索引的信息。是show index from schemaname.tablename的结果取之此表。
     
    USER_PRIVILEGES（用户权限）表：给出了关于全程权限的信息。该信息源自mysql.user授权表。是非标准表。
     
    SCHEMA_PRIVILEGES（方案权限）表：给出了关于方案（数据库）权限的信息。该信息来自mysql.db授权表。是非标准表。
     
    TABLE_PRIVILEGES（表权限）表：给出了关于表权限的信息。该信息源自mysql.tables_priv授权表。是非标准表。
     
    COLUMN_PRIVILEGES（列权限）表：给出了关于列权限的信息。该信息源自mysql.columns_priv授权表。是非标准表。
     
    CHARACTER_SETS（字符集）表：提供了mysql实例可用字符集的信息。是SHOW CHARACTER SET结果集取之此表。
     
    COLLATIONS表：提供了关于各字符集的对照信息。
     
    COLLATION_CHARACTER_SET_APPLICABILITY表：指明了可用于校对的字符集。这些列等效于SHOW COLLATION的前两个显示字段。
     
    TABLE_CONSTRAINTS表：描述了存在约束的表。以及表的约束类型。
     
    KEY_COLUMN_USAGE表：描述了具有约束的键列。
     
    ROUTINES表：提供了关于存储子程序（存储程序和函数）的信息。此时，ROUTINES表不包含自定义函数（UDF）。名为“mysql.proc name”的列指明了对应于INFORMATION_SCHEMA.ROUTINES表的mysql.proc表列。
     
    VIEWS表：给出了关于数据库中的视图的信息。需要有show views权限，否则无法查看视图信息。
     
    TRIGGERS表：提供了关于触发程序的信息。必须有super权限才能查看该表
    

### 3、information_schema数据库-三种表

#### 1）三种重要表格介绍

渗透测试后期基础上必须掌握以下三种表格，数据收集等；  
![1625812696_60e7eed8470544e3b388e.png!small?1625812700563](https://image.3001.net/images/20210709/1625812696_60e7eed8470544e3b388e.png!small?1625812700563)

    
    
    SCHEMATA		#包含了所有数据库名、类型、字符集等
    TABLES			#新建所有表的信息
    COLUMNS			#列的类型
    

![1625812703_60e7eedf62674eef4d89a.png!small?1625812719176](https://image.3001.net/images/20210709/1625812703_60e7eedf62674eef4d89a.png!small?1625812719176)

可以开始进行联动查询；

#### 2）查询SCHEMATA库

![1625812705_60e7eee1ad19d71ab376b.png!small?1625812719176](https://image.3001.net/images/20210709/1625812705_60e7eee1ad19d71ab376b.png!small?1625812719176)

    
    
    SELECT schema_name FROM information_schema.SCHEMATA LIMIT 0,1
    

此类查询出库中第一个表里的第一行数据；  
![1625812714_60e7eeea7bbaa945741d1.png!small?1625812722158](https://image.3001.net/images/20210709/1625812714_60e7eeea7bbaa945741d1.png!small?1625812722158)

    
    
    SELECT schema_name FROM information_schema.SCHEMATA LIMIT 1,1
    

此类查询出库中第二个表里的第一行数据，下面以此类推

#### 3）查询库中TABLES表

![1625812714_60e7eeea6af8a6585df75.png!small?1625812722158](https://image.3001.net/images/20210709/1625812714_60e7eeea6af8a6585df75.png!small?1625812722158)

    
    
    select * from information_schema.`TABLES` where TABLE_SCHEMA='ceshi' limit 0,1
    

查询出表中第一个数据信息；

在平常SQL注入中，不会直接写账号，需要转换下值：  
![1625812718_60e7eeee8ae364907cec6.png!small?1625812726504](https://image.3001.net/images/20210709/1625812718_60e7eeee8ae364907cec6.png!small?1625812726504)

    
    
    select HEX('ceshi')
    6365736869
    

![1625812723_60e7eef364495fc3c88bd.png!small?1625812726504](https://image.3001.net/images/20210709/1625812723_60e7eef364495fc3c88bd.png!small?1625812726504)

    
    
    select * from information_schema.`TABLES` where TABLE_SCHEMA=0x6365736869 limit 0,1
    

可以看到通过转值查询也是没问题的，该思路对于后期SQL注入更好的理解；

#### 4）查询COLUMNS列

![1625812727_60e7eef7436a54a66d9dc.png!small?1625812729957](https://image.3001.net/images/20210709/1625812727_60e7eef7436a54a66d9dc.png!small?1625812729957)

    
    
    select COLUMN_NAME from information_schema.`COLUMNS` where TABLE_SCHEMA=0x6365736869 and TABLE_NAME='biao1'
    

或者：  
![1625812734_60e7eefeea637452c5b2c.png!small?1625812744308](https://image.3001.net/images/20210709/1625812734_60e7eefeea637452c5b2c.png!small?1625812744308)

    
    
    select COLUMN_NAME from information_schema.`COLUMNS` WHERE TABLE_NAME='biao1'
    

#### 5）综合查询

![1625812741_60e7ef052b9cbd46ed7be.png!small?1625812744308](https://image.3001.net/images/20210709/1625812741_60e7ef052b9cbd46ed7be.png!small?1625812744308)

    
    
    select id,username,password from ceshi.biao1
    #通过information_schema系统库里面表来查询其他库表的数据，跨库查询需要权限比较大的时候才可以的
    

## 七、总结

经历完Mysql数据库的基础篇操作后，熟悉了查询数据七种方法，高级查询四种方法，子查询、内连接、左右连接、information_schema数据库表操作等等，当然还有很多渗透的方式方法，在高级篇会详细讲解！到这里就已经结束了数据库五章的渗透学习，想要入门渗透，这些必须得牢记掌握！知识点有：

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）......
    

接下来在《服务攻防之数据库MSSQL（上）》中会接触到如何对数据MSSQL的安装、漏洞的分析详解等操作，请看下篇服务攻防之数据库MSSQL上篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

