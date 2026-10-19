## 环境搭建：

实验环境可参照：https://www.freebuf.com/articles/web/253234.html

## SQL语句基础:

注意在mysql里每句语句结束一定要加分号;

### 1.查询语句：

1 **select database(); #查询当前使用的数据库**

2 **select user(); #查询当前用户**

3 **select now(); #查询当前时间**

4 **select version(); #查询数据库版本**

5 **show databases; #查询所有数据库**

6 **show tables; #查询当前数据库下的所有表**

### 2.建立表库:

1 create database name; #建立数据库name为你要建立的库的名字

2 **drop database name; #删除数据库 name为你要删除的数据库名**

3 create table name (id int,username varchar(30),password varchar(40));
#建立表name为表名 其中id，username，password为字段，int为整形，varchar为字符串,30与40代表能储存的最大长度

4\. desc name； #看表结构，name为表名

5\. drop table name； #删表name为表名

6\. insert into name values(1,'names')； #给表添加记录，name为表名，添加1和names

### 3.查询数据：

1. **select * from name; #查询表的所有记录，name为表名**

2\. **select * from name where username='admin'；
#从表中查找条件usrename为admin的所以记录，可以再用and来加条件**

3\. **select * from name order by 3；#查看字段长**

5\. **select * from name union select database(); #首先查询name表的所以记录，然后查询当前数据库**

### 4.注释：

 **单行注释：# --** （注意--后面有个空格）

 **多行注释：/**\ /*放在要注释的开始 *\ 放在完成注释的结尾**

## SQL注入原理

sql 注入攻击：通过构建特殊 sql 命令作为参数传入 web 应用程序

## 联合查询注入

1.mysql里的元数据库：information_schema #用于存放mysql的所以数据

2.mysql里的元数据表：table 表：主要是记录 Mysql 当中的所库及所有表，表的字段
table_schema（用于记录库名）table_name（用于记录表名）

>  **column 表：主要是用于记录库中的表，表中的字段该表的字段
> table_schema（用于记录库名）table_name（用于记录表名），column_name（用于记录字段名）**

 **我们以sqlilabs的第一关进行讲解，sqlilabs的搭建可以参照前面放的dvwa的搭建，我使用到的手注工具为hackbar**

 **1.首先我们使用转义符\看看闭合用的符号是什么**

![1609859348_5ff4811425d951d7751d0.png!small?1609859348427](https://image.3001.net/images/20210105/1609859348_5ff4811425d951d7751d0.png!small?1609859348427)

 **2.通过报错我们能看到闭合符号用的是单引号**

 **接着我们使用 order by 来查看字段**

 **使用到的指令是**

![1609859439_5ff4816fdbf5775bc8137.png!small?1609859440116](https://image.3001.net/images/20210105/1609859439_5ff4816fdbf5775bc8137.png!small?1609859440116)

我们这里使用了--+注释掉了后面的代码，我们的基本就是要闭合它原来的sql语句然后再注释掉后面的会报错的语句，这样我们注入sql语句就能被对方数据库正常执行了

发现字段为3

![1609859586_5ff48202d81790edd8ac6.png!small?1609859587267](https://image.3001.net/images/20210105/1609859586_5ff48202d81790edd8ac6.png!small?1609859587267)

###  

 **我们给参数 id 为一个不存在的页面**

 **接着使用 union 联合查询来得知数据库库名是什么用到的注入语句是**

![1609859777_5ff482c1541ba063fe960.png!small?1609859777603](https://image.3001.net/images/20210105/1609859777_5ff482c1541ba063fe960.png!small?1609859777603)

数据库名我们拿到了，接着我们使用之前提到过的元数据库爆破表名

![1609859869_5ff4831d0d362035d7dba.png!small?1609859869294](https://image.3001.net/images/20210105/1609859869_5ff4831d0d362035d7dba.png!small?1609859869294)

成功拿到表名

Group_concat（）这个函数简单来说是让我们查询到的东西放在 1 行显示我们通过判断发现 users 表最有用我们就查看 users 表的字段名

用到的语句

![1609859969_5ff48381272519becf886.png!small?1609859969480](https://image.3001.net/images/20210105/1609859969_5ff48381272519becf886.png!small?1609859969480)

成功拿到字段名我们能知道这个表是用来存放用户名和密码的，我们接着来取出数据 使用到的命令是

![1609860012_5ff483acbdabd7b7f487a.png!small?1609860013011](https://image.3001.net/images/20210105/1609860012_5ff483acbdabd7b7f487a.png!small?1609860013011)

###  

成功拿到数据，添加冒号的原因是更好分辨什么是 username 什么是 password

## 盲注稍后更新

