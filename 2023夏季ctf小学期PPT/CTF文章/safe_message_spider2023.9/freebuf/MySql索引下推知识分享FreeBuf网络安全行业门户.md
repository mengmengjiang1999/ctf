**作者：刘邓忠**

Mysql 是大家最常用的数据库，下面为大家带来 mysql 索引下推知识点的分享，以便巩固 mysql 基础知识，如有错误，还请各位大佬们指正。

### 1 什么是索引下推

索引下推 (Index Condition Pushdown，索引条件下推，简称 ICP)，是 MySQL5.6
版本的新特性，它可以在对联合索引遍历过程中，对索引中包含的所有字段先做判断，过滤掉不符合条件的记录之后再回表，能有效的减少回表次数（目前我们使用的
mysql 版本较高，一般大家可能感觉这是正常的，但是 mysql5.6 之前都不是这样实现的，下面会细细道来）。

### 1.1 适用条件

我们先来了解一下索引下推的使用条件及限制：

  * 只支持 select。
  * 当需要访问全表时，ICP 用于 range，ref，eq_ref 和 ref_or_null 访问类型。
  * ICP 可用于 InnoDB 和 MyISAM 表，包括分区的 InnoDB 和 MyISAM 表。（5.6 版本不适用分区表查询，5.7 版本后可以用于分区表查询）。
  * 对于 InnDB 引擎只适用于二级索引（也叫辅助索引），因为 InnDB 的聚簇索引会将整行数据读到 InnDB 的缓冲区，这样一来索引条件下推的主要目的减少 IO 次数就失去了意义。因为数据已经在内存中了，不再需要去读取了。
  * 在虚拟生成列上创建的辅助索引不支持 ICP（注：InnoDB 支持虚拟生成列的辅助索引）。
  * 使用了子查询的条件无法下推。
  * 使用存储过程或函数的条件无法下推（因为因为存储引擎没有调用存储过程或函数的能力）。
  * 触发条件无法下推。（有关触发条件的信息，请参阅官方资料：Section 8.2.2.3, “Optimizing Subqueries with the EXISTS Strategy”.。）

### 1.2 原理介绍

首先，我们大致回顾下 mysql 的基本架构：

![](https://image.3001.net/images/20221222/1671677369_63a3c5b9a3f5aaf3118f3.png!small)  
  
MySQL 基本的架构示例图

  
MySQL 服务层主要负责 SQL 语法解析、生成执行计划等，并调用存储引擎层去执行数据的存储和查询。  
索引下推的下推其含义就是指将部分上层（服务层）负责的事情，交给了下层（引擎层）去处理。  
在 MySql 5.6 版本之前没有索引下推这个功能，从 5.6 版本后才加上了这个优化项。我们先简单对比一下使用和未使用 ICP 两种情况下，MySql
的查询过程吧。  
  
 **1) 未使用 ICP 的情况下：**  
  
\- 存储引擎读取索引记录；  
\- 根据索引中的主键值，定位并读取完整的行记录；  
\- 存储引擎把记录交给 Server 层去检测该记录是否满足 WHERE 条件。  
  
 **2) 使用 ICP 的情况下：**  
  
\- 存储引擎读取索引记录（不是完整的行记录）；  
\- 判断 WHERE 条件部分能否用索引中的列来做检查，条件不满足，则处理下一行索引记录；  
\- 条件满足，使用索引中的主键去定位并读取完整的行记录（就是所谓的回表）；  
\- 存储引擎把记录交给 Server 层，Server 层检测该记录是否满足 WHERE 条件的其余部分。

# 2 具体示例

  
上面介绍了基本原理，下面使用示例，带大家更直观的进行理解（注：以下示例基于 InnoDB 存储引擎。）  
首先，我们新建一张用户表（jxc_user），设置 id 为主键索引，并创建联合索引（name, age）。  
  
![](https://image.3001.net/images/20221222/1671677370_63a3c5bad580b8c231a72.png!small)  
  
我们先看一下该表主键索引的大致结构示例：

![](https://image.3001.net/images/20221222/1671677371_63a3c5bb80fc8373b929e.png!small)  
  
主键索引结构示例图

  
然后我们再看一下该表联合索引的大致结构示例：

![](https://image.3001.net/images/20221222/1671677372_63a3c5bc5b9be6c591d2a.png!small)  
  
联合索引结构示例图

如果现在有一个需求，要求检索出表中名字第一个字是张，而且年龄等于 10 岁的所有用户。示例 SQL 语句如下：

    
    
      
    

  1. `select id,name,age,tel,addr from jxc_user where name like '张%' and age=10;`

根据索引最左匹配原则，上面这个 sql 语句在查索引树的时候，只能用 “张”，查到第一个满足条件的记录：id 为 1。  
那接下来我们具体看一下 使用与未使用 ICP 的情况。

### 2.1 未使用 ICP 的情况

在 MySQL 5.6 之前，存储引擎根据联合索引先找到 name like ‘张 %’ 的主键
id（1、4），再逐一进行回表扫描，去聚簇索引找到完整的行记录，返回 server 层，server 层拿到数据后，再根据条件 age=10
对拿到的数据进行筛选。大致的示意图如下：

![](https://image.3001.net/images/20221222/1671677373_63a3c5bd5d7470d72e6bd.png!small)

从上图，可以看到需要回表两次，存储引擎并不会去按照 age=10 进行过滤，相当于联合索引的另一个字段 age 在存储引擎层没有发挥作用，比较浪费。

### 2.2 使用 ICP 的情况

而 MySQL 5.6 以后， 存储引擎会根据（name，age）联合索引，找到 name like ‘张 %’，由于联合索引中包含 age
列，所以存储引擎直接再联合索引里按照条件 age=10 进行过滤，然后根据过滤后的数据再依次进行回表扫描。大致的示意图如下：

![](https://image.3001.net/images/20221222/1671677374_63a3c5bed1b7f7b043ba3.png!small)

从上图，可以看到只是 id=1 的数据，回表了一次。

除此之外我们还可以看一下执行计划，看到 Extra 一列里 Using index condition，就是用到了索引下推。

![](https://image.3001.net/images/20221222/1671677376_63a3c5c00d3e22aaaf352.png!small)

## 3 控制参数

Mysql 索引下推功能默认是开启的，可以用系统参数 optimizer_switch 来控制是否开启。  
查看状态命令：  
select
@[@optimizer_switch](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fgithub.com%2Foptimizer_switch);

![](https://image.3001.net/images/20221222/1671677376_63a3c5c09d4ee59bc5aa4.png!small)

关闭命令：set optimizer_switch=”index_condition_pushdown=off”;  
开启命令：set optimizer_switch=”index_condition_pushdown=on”;

## 4 总结

回表操作：当所要查找的字段不在非主键索引树上时，需要通过叶子节点的主键值去主键索引上获取对应的行数据，这个过程称为回表操作。  
索引下推：索引下推主要是减少了不必要的回表操作。对于查找出来的数据，先过滤掉不符合条件的，其余的再去主键索引树上查找。

## 5 参考文献

  * [https://dev.mysql.com/doc/refman/5.6/en/index-condition-pushdown-optimization.html](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fdev.mysql.com%2Fdoc%2Frefman%2F5.6%2Fen%2Findex-condition-pushdown-optimization.html)
  * [http://mysql.taobao.org/monthly/2015/12/08/](https://www.oschina.net/action/GoToLink?url=http%3A%2F%2Fmysql.taobao.org%2Fmonthly%2F2015%2F12%2F08%2F)

