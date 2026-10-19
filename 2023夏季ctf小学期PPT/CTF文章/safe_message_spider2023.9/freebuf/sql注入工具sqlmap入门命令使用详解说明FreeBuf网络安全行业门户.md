![](https://image.3001.net/images/20230615/1686825883_648aeb9b4a43bdfba4f86.png!small)

## 前言

帮助初学者使用sqlmap注入工具，便于快速掌握及理解sqlmap工具，同时也是一个sql帮助命令手册。提供示例及说明。如何在windows/mac中安装可自行查找。本次使用环境是kali来演示操作使用。

## 提示说明：

本文章仅用于信息安全教学，请遵守相关法律法规，严禁用于非法途径。若观众因此作出任何危害网络安全的行为，后果自负，与UP主无关。遵纪守法做一个良好公民，切勿违法国家计算机安全法，以免牢底坐穿。

## 工具介绍

sqlmap 是一个开源渗透测试工具，它可以自动检测和利用 SQL
注入漏洞并接管数据库服务器。它具有强大的检测引擎，同时有众多功能，包括数据库指纹识别、从数据库中获取数据、访问底层文件系统以及在操作系统上带内连接执行命令。

## 工具使用

使用格式：

    
    
    python3 sqlmap [options]

如在kali中，则不用加上python ， windows 则需要加上对应的python.

帮助命令：

    
    
    sqlmap -h

命令将会输出英文帮助信息

![](https://image.3001.net/images/20230615/1686820329_648ad5e9ef4718f7f4b0e.png!small)

 **常见命令实用说明**

sqlmap 使用很简单，命令是结合起来使用的。现在假设我们有一个url，我们想检测是否有sql漏洞，可以输入命令：

    
    
    sqlmap -u www.xxx.com?name=hellosql

其中命令：-u (url) 即为url 需要检测的路径。回车运行可查看结果。

###  **成功结果示例：**

成功将会返回注入成功的参数列表如下：

![](https://image.3001.net/images/20230615/1686820665_648ad739a78d4f849fa7f.png!small)

 **注入失败结果示例：**

![](https://image.3001.net/images/20230615/1686821161_648ad929f21f8cb69389b.png!small)

例如，我们要查看数据库:test 里面的表 user 有什么属性（字段），从帮助文档得知：

  

搜索列，表和/或数据库名称

> -D

指定要进行枚举的指定数据库名

> -T

  

因此只需要输入：

    
    
    sqlmap -u www.xxx.com -D test -T user --columns

即可列出 user表的数据信息。其他命令操作也是如同，自个可以举一反三。

  

## 命令说明

    
    
    ┌──(parallels㉿kali-linux-2022-2)-[~]
    └─$ sqlmap -hh                                                                 
            ___
           __H__
     ___ ___[']_____ ___ ___  {1.6.6#stable}
    |_ -| . [)]     | .'| . |
    |___|_  [,]_|_|_|__,|  _|
          |_|V...       |_|   https://sqlmap.org
    
    Usage: python3 sqlmap [options]
    
    
    
    
    用法：python3 sqlmap [选项]

### 选项

选项| 中文说明  
---|---  
-hh| 显示高级帮助信息和退出  
\--version| 显示程序版本号和退出  
-v| verbosity level（详细级别）：0-6（默认值为1  
  
### 目标：

选项| 描述  
---|---  
-u URL| 目标URL (例如："http://www.site.com/vuln.php?id=1")  
\--url=URL| 目标URL  
-d| 直接数据库连接的连接字符串  
-l LOGFILE| 从Burp或WebScarab代理日志文件中解析目标  
-m BULKFILE| 扫描文本文件中提供的多个目标  
-r REQUESTFILE| 从文件中加载HTTP请求  
-g GOOGLEDORK| 将Google搜索结果作为目标URL处理  
-c CONFIGFILE| 从配置INI文件中加载选项  
  
 **请求：**

这些选项可用于指定如何连接到目标URL

选项| 描述  
---|---  
-A AGENT, --user..| HTTP User-Agent头部字段值  
-H HEADER, --hea..| 额外头部（例如："X-Forwarded-For: 127.0.0.1"）  
\--method=METHOD| 强制使用给定的HTTP方法（例如：PUT）  
\--data=DATA| 通过POST发送的数据字符串（例如："id=1"）  
\--param-del=PARA..| 分隔参数值的字符（例如："&"）  
\--cookie=COOKIE| HTTP Cookie头部字段值（例如："PHPSESSID=a8d127e.."）  
\--cookie-del=COO..| 分隔Cookie值的字符（例如：";"）  
\--live-cookies=L..| 用于加载最新值的实时Cookies文件  
\--load-cookies=L..| 包含以Netscape/wget格式的Cookies的文件  
\--drop-set-cookie| 忽略响应中的Set-Cookie头部字段  
\--mobile| 通过HTTP User-Agent头部字段模仿智能手机  
\--random-agent| 使用随机选择的HTTP User-Agent头部字段值  
\--host=HOST| HTTP Host头部字段值  
\--referer=REFERER| HTTP Referer头部字段值  
\--headers=HEADERS| 额外头部（例如："Accept-Language: fr\nETag: 123"）  
\--auth-type=AUTH..| HTTP身份验证类型（Basic，Digest，Bearer，...）  
\--auth-cred=AUTH..| HTTP身份验证凭据（名称：密码）  
\--auth-file=AUTH..| HTTP身份验证PEM证书/私钥文件  
\--ignore-code=IG..| 忽略（有问题的）HTTP错误代码（例如：401）  
\--ignore-proxy| 忽略系统默认代理设置  
\--ignore-redirects| 忽略重定向尝试  
\--ignore-timeouts| 忽略连接超时  
\--proxy=PROXY| 使用代理连接到目标URL  
\--proxy-cred=PRO..| 代理身份验证凭据（name:password）  
\--proxy-file=PRO..| 从文件中加载代理列  
\--proxy-freq=PRO..| 代理列表之间的请求更改  
\--tor| 使用Tor匿名网络  
\--tor-port=TORPORT| 设置Tor代理端口（默认为其他端口）  
\--tor-type=TORTYPE| 设置Tor代理类型（HTTP、SOCKS4或SOCKS5（默认））  
\--check-tor| 检查Tor是否正确使用  
\--delay=DELAY| 每个HTTP请求之间的延迟（以秒为单位）  
\--timeout=TIMEOUT| 连接超时之前的等待时间（秒）（默认30秒）  
\--retries=RETRIES| 连接超时时重试次数（默认3次）  
\--retry-on=RETRYON| 重试请求的正则表达式匹配内容（例如“drop”）  
\--randomize=RPARAM| 随机更改给定参数的值  
\--safe-url=SAFEURL| 在测试期间经常访问的URL地址  
\--safe-post=SAFE..| 发送POST数据到安全URL  
\--safe-req=SAFER..| 从文件中加载安全的HTTP请求  
\--safe-freq=SAFE..| 经常访问安全URL的常规请求  
\--skip-urlencode| 跳过有效载荷数据的URL编码  
\--csrf-token=CSR..| 保存CSRF令牌的参数  
\--csrf-url=CSRFURL| 访问以提取CSRF令牌的URL地址  
\--csrf-method=CS..| 访问CSRF令牌页面的HTTP方法  
\--csrf-retries=C..| CSRF令牌检索的重试次数（默认0）  
\--force-ssl| 强制使用SSL/HTTPS  
\--chunked| 使用HTTP分块传输编码（POST）请求  
\--hpp| 使用HTTP参数污染方法  
\--eval=EVALCODE| 在请求之前评估提供的Python代码（例如“import
hashlib;id2=hashlib.md5(id).hexdigest()”）  
  
### 优化

这些选项可用于优化sqlmap的性能

选项| 描述  
---|---  
-o| 开启所有优化开关  
\--predict-output| 预测常见查询的输出  
\--keep-alive| 使用持久的 HTTP(s) 连接  
\--null-connection| 获取页面长度而不实际发送 HTTP 响应体  
\--threads=THREADS| 最大并发 HTTP(s) 请求数量（默认为 1）  
  
 **注入：**

这些选项可以用于指定要测试的参数，提供自定义注入有效负载和可选篡改脚本

选项| 描述  
---|---  
-p TESTPARAMETER| 可测试参数  
\--skip=SKIP| 跳过指定参数的测试  
\--skip-static| 跳过静态参数的测试  
\--param-exclude=..| 用于排除参数的正则表达式（例如："ses"）  
\--param-filter=P..| 通过位置选择可测试参数（例如："POST"）  
\--dbms=DBMS| 后端DBMS强制设置为提供的值  
\--dbms-cred=DBMS..| DBMS认证凭据（用户名：密码）  
\--os=OS| 后端DBMS操作系统强制设置为提供的值  
\--invalid-bignum| 使用大数字来使值无效  
\--invalid-logical| 使用逻辑运算使值无效  
\--invalid-string| 使用随机字符串使值无效  
\--no-cast| 关闭有效负载的投射机制  
\--no-escape| 关闭字符串转义机制  
\--prefix=PREFIX| 注入有效负载的前缀字符串  
\--suffix=SUFFIX| 注入有效负载的后缀字符串  
\--tamper=TAMPER| 使用给定的脚本来篡改注入数据  
  
 **检测：**

这些选项可用于自定义检测阶段

选项| 描述  
---|---  
\--level=LEVEL| 要执行测试的级别（1-5，默认值：1）  
\--risk=RISK| 要执行测试的风险（1-3，默认值：1）  
\--string=STRING| 当查询结果为True时匹配的字符串  
\--not-string=NOT..| 当查询结果为False时匹配的字符串  
\--regexp=REGEXP| 当查询结果为True时匹配的正则表达式  
\--code=CODE| 当查询结果为True时匹配的HTTP代码  
\--smart| 仅在积极的启发式（s）时执行彻底的测试  
\--text-only| 仅根据文本内容比较页面  
\--titles| 仅根据标题比较页面  
  
 **技术：**

这些选项可用于调整特定SQL注入的测试

选项| 描述  
---|---  
\--technique=TECH..| 要使用的SQL注入技术（默认为“BEUSTQ”）  
\--time-sec=TIMESEC| 延迟DBMS响应的秒数（默认值：5）  
\--union-cols=UCOLS| 用于测试UNION查询SQL注入的列范围  
\--union-char=UCHAR| 用于暴力破解列数的字符  
\--union-from=UFROM| 用于UNION查询SQL注入的FROM部分的表  
\--dns-domain=DNS..| DNS渗漏攻击中使用的域名  
\--second-url=SEC..| 搜索二级响应的页面URL  
\--second-req=SEC..| 从文件加载二级HTTP请求  
  
 **指纹**

选项| 描述  
---|---  
-f| 进行广泛的DBMS版本指紋（fingerprint）  
  
 **枚举：**

这些选项可用于枚举后端数据库管理系统信息、结构和包含在表

选项| 描述  
---|---  
-a, --all| 检索一切  
-b, --banner| 检索DBMS横幅  
\--current-user| 检索DBMS当前用户  
\--current-db| 检索DBMS当前数据库  
\--hostname| 检索DBMS服务器主机名  
\--is-dba| 检测DBMS当前用户是否为DBA  
\--users| 枚举DBMS用户  
\--passwords| 枚举DBMS用户的密码哈希值  
\--privileges| 枚举DBMS用户的权限  
\--roles| 枚举DBMS用户的角色  
\--dbs| 枚举DBMS数据库  
\--tables| 枚举DBMS数据库表  
\--columns| 枚举DBMS数据库表列  
\--schema| 枚举DBMS模式  
\--count| 检索表中的条目数  
\--dump| 转储DBMS数据库表中的条目  
\--dump-all| 转储所有DBMS数据库表的条目  
\--search| 搜索列、表和/或数据库名称  
\--comments| 在枚举期间检查DBMS注释  
\--statements| 检索在DBMS上运行的SQL语句  
-D DB| 要枚举的DBMS数据库  
-T TBL| 要枚举的DBMS数据库表  
-C COL| 要枚举的DBMS数据库表列  
-X EXCLUDE| 不枚举的DBMS数据库标识符  
-U USER| 要枚举的DBMS用户  
\--exclude-sysdbs| 枚举表时排除DBMS系统数据库  
\--pivot-column=P..| 枢轴列名称  
\--where=DUMPWHERE| 转储表时使用WHERE条件  
\--start=LIMITSTART| 要检索的第一个转储表条目  
\--stop=LIMITSTOP| 要检索的最后一个转储表条目  
\--first=FIRSTCHAR| 要检索的第一个查询输出单词字符  
\--last=LASTCHAR| 要检索的最后一个查询输出单词字符  
\--sql-query=SQLQ..| 要执行的SQL语句  
\--sql-shell| 提示交互式SQL shell  
\--sql-file=SQLFILE| 从给定文件执行SQL语句  
  
 **蛮力：**

这些选项可用于运行暴力检查

选项| 描述  
---|---  
\--common-tables| 检查普通表是否存在  
\--common-columns| 检查普通列是否存在  
\--common-files| 检查普通文件是否存在  
  
 **用户定义的功能注入：**

这些选项可用于创建自定义的用户定义函数

选项| 描述  
---|---  
\--udf-inject| 注入自定义用户定义的功能  
\--shared-lib=SHLIB| 共享库的本地路径  
  
 **文件系统访问：**

这些选项可用于访问后端数据库管理

系统基础文件系统

选项| 描述  
---|---  
\--file-read=FILE..| 从后端DBMS文件系统中读取文件  
\--file-write=FIL..| 在后端DBMS文件系统中写入本地文件  
\--file-dest=FILE..| 后端DBMS的绝对路径文件要写入的文件路径  
  
 **操作系统访问** ：

这些选项可用于访问后端数据库管理

系统底层操作系统

选项| 描述  
---|---  
\--os-cmd=OSCMD| 执行操作系统命令  
\--os-shell| 提示交互式操作系统shell  
\--os-pwn| 提示OOB shell、Meterpreter或VNC  
\--os-smbrelay| 单击提示OOB shell、Meterpreter或VNC  
\--os-bof| 存储过程缓冲区溢出利用  
\--priv-esc| 数据库进程用户特权提升  
\--msf-path=MSFPATH| Metasploit框架安装的本地路径  
\--tmp-path=TMPPATH| 远程临时文件目录的绝对路径  
  
 **Windows注册表访问：**

这些选项可用于访问后端数据库管理

系统Windows注册表

选项| 描述  
---|---  
\--reg-read| 读取Windows注册表键值  
\--reg-add| 写入Windows注册表键值数据  
\--reg-del| 删除Windows注册表键值  
\--reg-key=REGKEY| Windows注册表键  
\--reg-value=REGVAL| Windows注册表键值  
\--reg-data=REGDATA| Windows注册表键值数据  
\--reg-type=REGTYPE| Windows注册表键值类型  
  
 **概述：**

这些选项可用于设置一些通用工作参数

选项| 描述  
---|---  
-s SESSIONFILE| 从存储的(.sqlite)文件加载会话  
-t TRAFFICFILE| 将所有HTTP流量记录到文本文件  
\--answers=ANSWERS| 预设答案（例如："quit=N,follow=N"）  
\--base64=BASE64P..| 包含Base64编码数据的参数  
\--base64-safe| 使用URL和文件名安全Base64字母表（RFC 4648）  
\--batch| 不询问用户输入，使用默认行为  
\--binary-fields=..| 结果字段具有二进制值（例如："digest"）  
\--check-internet| 在评估目标之前检查Internet连接  
\--cleanup| 从sqlmap特定UDF和表中清理DBMS  
\--crawl=CRAWLDEPTH| 从目标URL开始爬取网站  
\--crawl-exclude=..| 用于排除爬取页面的正则表达式（例如："logout"）  
\--csv-del=CSVDEL| CSV输出中使用的分隔符字符（默认为逗号）  
\--charset=CHARSET| 盲注SQL注入字符集（例如："0123456789abcdef"）  
\--dump-format=DU..| 转储数据的格式（CSV（默认值），HTML或SQLITE）  
\--encoding=ENCOD..| 数据检索所使用的字符编码（例如："GBK"）  
\--eta| 显示每个输出的到达时间估计值  
\--flush-session| 清除当前目标文件的会话文件  
\--forms| 解析和测试目标URL上的表单  
\--fresh-queries| 忽略会话文件中存储的查询结果  
\--gpage=GOOGLEPAGE| 使用指定页码的Google搜索结果进行搜索  
\--har=HARFILE| 将所有HTTP流量记录到HAR文件中  
\--hex| 在数据检索期间使用十六进制转换  
\--output-dir=OUT..| 自定义输出目录路径  
\--parse-errors| 解析并显示响应中的 DBMS 错误信息  
\--preprocess=PRE..| 使用给定脚本来进行预处理（请求）  
\--postprocess=PO..| 使用给定脚本来进行后处理（响应）  
\--repair| 转储具有未知字符标记（？）的条目  
\--save=SAVECONFIG| 将选项保存到配置 INI 文件  
\--scope=SCOPE| 用于过滤目标的正则表达式  
\--skip-heuristics| 跳过漏洞的启发式检测  
\--skip-waf| 跳过 WAF/IPS 保护的启发式检测  
\--table-prefix=T..| 用于临时表的名称前缀（默认为："sqlmap"）  
\--test-filter=TE..| 通过有效载荷和/或标题选择测试（例如：ROW）  
\--test-skip=TEST..| 跳过测试的有效载荷和/或标题（例如：BENCHMARK）  
\--web-root=WEBROOT| Web 服务器文档根目录（例如："/var/www"）  
  
 **其他：**

这些选项不属于任何其他类别

选项| 描述  
---|---  
-z MNEMONICS| 使用简短助记符（例如："flu,bat,ban,tec=EU"）  
\--alert=ALERT| 找到 SQL 注入时运行主机 OS 命令（S）  
\--beep| 在问题和/或漏洞被发现时发出蜂鸣声  
\--dependencies| 检查缺少的（可选）sqlmap 依赖项  
\--disable-coloring| 禁用控制台输出着色  
\--list-tampers| 显示可用的篡改脚本列表  
\--no-logging| 禁用日志记录到文件  
\--offline| 在脱机模式下工作（仅使用会话数据）  
\--purge| 安全地删除 sqlmap 数据目录中的所有内容  
\--results-file=R..| 多个目标模式下 CSV 结果文件的存储位置  
\--shell| 提示交互式 sqlmap shell  
\--tmp-dir=TMPDIR| 用于存储临时文件的本地目录  
\--unstable| 调整不稳定连接的选项  
\--update| 更新 sqlmap  
\--wizard| 为初学者用户提供简单的向导界面  
  
  

