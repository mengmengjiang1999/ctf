## 简述：

>
> SQLMAP是一种开源渗透测试工具，可自动执行SQL注入缺陷的检测和开发过程，并接管数据库服务器。它有强大的检测引擎,针对不同类型的数据库提供多样的渗透测试功能选项，实现数据库识别、数据获取、访问DBMS\操作系统甚至通过带外数据连接的方式执行操作系统的命令。以及从数据库指纹识别、从数据库获取数据、访问底层文件的广泛范围的交换机通过带外连接在操作系统上执行命令

## 免责声明：

> 不可对真实未授权网站使用：后果自负

### 一、Option

  1. > -h：显示基础的帮助信息

  2. > -hh：显示详细的帮助信息

  3. > -v： 显示详细的注入过程0-6个等级

### 二、Target：目标

  1. > -u：需要测试的目标地址

  2. > -g：sqlmap可以测试注入Google的搜索结果中的GET参数（只获取前100个结果）

  3. > -d：直接连接数据库

  4. > -l ：可以直接把Burp proxy或者WebScarab proxy中的日志直接倒出来交给sqlmap来一个一个检测是否有注入。

  5. > -m：可以将多个url填入文件，对文件中的多个URL进行测试

  6. > -r ：可以将http请求包放入一个文本中，然后从一个文本文件中对http请求的一个参数进行测试，参数可以通过*好来固定要测试的位置，这样就可以跳过设置一些其他参数（比如cookie，POST数据，等等）

### 三、Request：请求设置

  1. > \--method：指定请求方法

  2. > \--data：把数据以POST方式提交

  3. > \--param：当GET或POST的数据需要用其他字符分割测试参数的时候需要用到此参数。

  4. > \--cookie：设置cookie，提交请求的时候附带所设置的cookie 
>     1. 这个参数在以下两个方面很有用：
>
> web应用需要登陆的时候。
>
> 你想要在这些头参数中测试SQL注入时。

  5. > \--load-cookies：从文件获取cookie

  6. > \--user-agent：可以使用–user-anget参数来修改

  7. > \--random-agent：使用–random-agnet参数来随机的从./txt/user-agents.txt中获取。当–level参数设定为3或者3以上的时候，会尝试对User-Angent进行注入。

  8. > \--referer：在请求目标的时候可以自己伪造请求包中的referer –level参数设定为3或者3以上的时候会尝试对referer注入。

  9. > \--headers：可以通过–headers参数来增加额外的http头

  10. > \--proxy：设置代理

  11. > \--delay：可以设定两个HTTP(S)请求间的延迟 防止发送过快导致被封ip

### 四、Optimization（优化）

>   1. -o 开启所有优化开关
>
>

### 五、Injection注入

  1. > -p：设置想要测试的参数

  2. > \--skip：不想要测试的参数可以通过 skip设置跳过

  3. > \--dbms：指定数据库 节省sqlmap自己检测的时间

  4. > \--os：指定数据库服务系统 节省sqlmap自己检测的时间

  5. > \--tamper：使用sqlmap自带的tamper，或者自己写的tamper，来混淆payload，通常用来绕过waf和ips。

### 六、Detection探测等级

>   1. \--level=LEVEL 执行测试的等级（1-5，默认为1）
>
>   2. \--risk：（ ***慎用** 此参数有风险），
> 共有四个风险等级，默认是1会测试大部分的测试语句，2会增加基于事件的测试语句，3会增加OR语句的SQL注入测试。
>
>

### 六、Techniques注入方式

>   1. \--technique：后面跟参数BEUST任意
>
>     * B: Boolean-based blind SQL injection（布尔型注入）
>
> E: Error-based SQL injection（报错型注入）
>
> U: UNION query SQL injection（可联合查询注入）
>
> S: Stacked queries SQL injection（可多语句查询注入）
>
> T: Time-based blind SQL injection（基于时间延迟注入）  
>  
> ---  
>   2. \--time-sec：设定延迟注入的时间
>
>   3. \--union-cols：设定UNION查询字段数
>
>   4. \--union-char：设定UNION查询使用的字符
>
>   5. \--second-order：二阶SQL注入
>
>

### 七、Fingerprint（指纹）

>   1. -f, --fingerprint 执行检查广泛的DBMS版本指纹
>
>

### 八、Enumeration枚举数据

  1.     -b, --banner        获取数据库管理系统的标识
    --current-user      获取数据库管理系统当前用户
    --current-db        获取数据库管理系统当前数据库
    --hostname          获取数据库服务器的主机名称
    --is-dba            检测DBMS当前用户是否DBA
    --users             枚举数据库管理系统用户
    --passwords         枚举数据库管理系统用户密码哈希
    --privileges        枚举数据库管理系统用户的权限
    --dbs			   枚举数据库管理系统数据库
    --tables		   枚举DBMS数据库中的表
    --columns		   枚举DBMS数据库表列
    -D                  要进行枚举的指定数据库名
    -T                  要进行枚举的指定表名
    -C                  要进行枚举的指定列名
    --dump			   转储数据库表项,查询字段值
    --search  		   搜索列（S），表（S）和/或数据库名称（S）
    --sql-query=QUERY   要执行的SQL语句
    --sql-shell         提示交互式SQL的shell

### 八、Brute force爆破

>   1. \--common-tables 检查存在共同表
>
>   2. \--common-columns 检查存在共同列
>
>   3. User-defined function injection（用户自定义函数注入）：
>
>   4. \--udf-inject 注入用户自定义函数
>
>   5. \--shared-lib=SHLIB 共享库的本地路径
>
>

### 九、File system access（访问文件系统）

>   1. \--file-read=RFILE 从后端的数据库管理系统文件系统读取文件
>
>   2. \--file-write=WFILE 编辑后端的数据库管理系统文件系统上的本地文件
>
>   3. \--file-dest=DFILE 后端的数据库管理系统写入文件的绝对路径
>
>

### 十、Operating system access（操作系统访问）

>   1. \--os-cmd=OSCMD 执行操作系统命令
>
>   2. \--os-shell 交互式的操作系统的shell
>
>   3. \--os-pwn 获取一个OOB shell，meterpreter或VNC
>
>   4. \--os-smbrelay 一键获取一个OOB shell，meterpreter或VNC
>
>   5. \--os-bof 存储过程缓冲区溢出利用
>
>   6. \--priv-esc 数据库进程用户权限提升
>
>   7. \--msf-path=MSFPATH Metasploit Framework本地的安装路径
>
>   8. \--tmp-path=TMPPATH 远程临时文件目录的绝对路径
>
>

### 十一、Miscellaneous（杂项）

>   1. \--beep 发现SQL注入时提醒
>
>   2. \--check-payload IDS对注入payloads的检测测试
>
>   3. \--tor 使用默认的Tor（Vidalia/ Privoxy/ Polipo）代理地址
>
>

### 十二、参数概览图

![](https://image.3001.net/images/20200803/1596441019.jpg!small)

