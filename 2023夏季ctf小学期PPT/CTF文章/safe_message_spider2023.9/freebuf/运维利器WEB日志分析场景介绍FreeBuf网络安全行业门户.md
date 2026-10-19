![1628844057_611630196615a32de2137.jpg!small?1628844058452](https://image.3001.net/images/20210813/1628844057_611630196615a32de2137.jpg!small?1628844058452)

## 为什么要对 Web日志进行分析

随着 Web 技术不断发展，Web
被应用得越来越广泛，现在很多企业对外就一个网站来提供服务，所以网站的业务行为，安全性显得非常重要。正如安全行业的一句话：“世界上只有两种人，一种是知道自己被黑了的，另外一种是被黑了还不知道的”。对网站的业务行为分析，网站的安全性分析一个很重要的途径就是通过日志。通过WEB日志分析最直接明显的几个目的：

一为网站安全自检查，了解服务器上正在发生的安全事件；

二为应急事件中的分析取证；

三是可根据日志分析一些常用的业务行为。

## 如何进行日志分析？

在进行日志分析之前，我们先来了解一下 Web服务器中产生的日志是什么样子。我们来看一条 Apache 的访问日志为例：

    
    
    114.221.137.87 - - [10/Sep/2019:14:52:28 +0800] "GET /login HTTP/1.1" 200 1068 https://secilog.secisland.com/ Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.105 Safari/537.36 Vivaldi/2.4.1488.40

通过以上信息，我们可以得知服务器会记录来自客户端的每一个请求，其中有大量来自正常用户的请求，当然也包括来自恶意攻击者的请求，那么我们如何区分正常请求和恶意攻击请求呢？

站在攻击者的角度，攻击者对网站进行渗透时，其中包含大量的 **扫描请求** 和 **执行恶意操作**
的请求，而这两者在日志中都有各自的特征，如扫描请求会访问大量不存在的地址，在日志中体现则为大量的响应状态码为404，而不同的恶意请求都有各自相应的特征。

如当有人对服务器进行SQL注入漏洞探测时会有类似：/login?attack=test';select/*
*/1/**/from/**/1等内容。通过关键字分析可以分析哪些 IP 在进行攻击，可以进一步的进行处置，比如封ip等。

## 日志分析场景介绍

一般可以按照两种思路展开，逐步深入，还原整个攻击过程。

 **第一种** ：确定入侵的时间范围，以此为线索，查找这个时间范围内可疑的日志，进一步排查，最终确定攻击者，还原攻击过程。

 **第二种** ：攻击者在入侵网站后，通常会留下后门权限，以方便再次访问，我们可以找到该文件，并以此为线索来展开分析。

曾经有人问过运维的人员的大神，该如何分析日志？大神回答了三个字：“用命令”。

因为站在脚本操作经验丰富的人角度来看，的确用命令足矣，可是对于一般的人员来说用Linux的shell命令还是稍显复杂。还是需要借助一些工具来提高效率。这里用了
**SECISLAND** 新推出的免费工具 **secsoso** 来作为示例：

spl 完整语法：`secsoso ‘file=("文件名"," ") 过滤|统计…’`简化语法： `secsoso ‘文件名 过滤|统计…’`

 **secsoso** 是一个小工具，用来搜索、关联、统计文本数据，它结合了 SQL 的功能与 Unix
管道语法，可以对文本数据进行快速的定位，查找和分析，从而提高处理和解决问题的效率。

 **secsoso** 获取方式如下：

1、关注公众号“SECISLAND安全官”

2、公众号内发送“secsoso”，获取下载链接

## 业务行为统计

### 列出文件中访问次数最多的10个IP

    
    
    secsoso 'file=("/export/home/20190613/access.log"," ")|stats  count($1) by $1|sort 10 -count_$1'

 **说明：** 其中/export/home/20190613/access.log为文件路径，“
”为字段分割符。文件名可以是绝对路径(/export/home/20190613/access.log)
也可以是相对路径(access.log)。默认列名为$1,$2..., count($1)后的默认名称为count_$1。

结果如下:

    
    
    $1                    count_$1  
    101.226.68.137                 972  
    163.177.71.12                 972  
    183.195.232.138                 971  
    111.192.165.229                 377  
    114.252.89.91                 374  
    66.249.66.84                 246  
    222.70.152.149                 226  
    220.181.89.174                 172  
    111.194.118.58                 160  
    60.247.77.253                 146

你也可以给字段重命名以友好方式显示，这个是简化语法：结果同上。

    
    
    secsoso ‘access.log|rename $1 as ip |stats  count(ip) by ip|sort 10 -count_ip’

### 查看文件中有多少个不同的IP访问

    
    
    secsoso  'access.log|rename $1 as ip |stats  dc(ip) '

结果如下:

    
    
    dc_ip  
    1050

### 查看某一个页面被访问的次数

比如 /nodejs-underscore/?cf_action=sync_comments为访问页面

    
    
    secsoso 'access.log "/nodejs-underscore/?cf_action=sync_comments"|eventcount'

红色字是过滤的含义，结果如下:

    
    
    event_count  
    14

### 查看每一个IP访问了多少个页面

    
    
    secsoso 'access.log $7="*.html*" |stats $1 as ip,count($1) as count by $1'

stats $1 as ip,count($1) as count by $1 和 stats count($1) by $1
结果一样，只是前者可以从新命名，命名也可以放在后面做：

stats count($1) by $1|rename $1 as ip，结果如下：

    
    
    ip                       count  
    10.70.101.89                3  
    10.70.101.90                3  
    10.70.141.32                3  
    10.70.142.18                5  
    10.70.146.115                2  
    10.70.146.120                5  
    10.70.147.28                2  
    10.70.149.233                2

### 查看每一个IP访问了多少个页面按从大到小排序

    
    
    secsoso 'access.log $7="*.html*" |stats $1 as ip,count($1) as count by $1|sort -count'

结果如下:

    
    
    ip            count  
    10.74.52.51               21  
    10.80.189.69               12  
    10.71.37.20                9  
    10.77.6.9                9  
    10.71.48.20                9  
    10.80.6.121                8  
    10.77.7.244                8

### 查看某一个IP访问了哪些页面

    
    
    secsoso  'access.log "10.74.52.51"  $7="*.html*" |fields $1,$7'

> `$7="*.html*"`也支持正则表达式需要用//包起来，比如”access.log” “10.74.52.51” $7=”/.html./“
> |fields 7，这个是查询，选择第一列和第7列。

结果如下:

    
    
    $1                                        $7  
    10.74.52.51            /zmccwps/welcome/qiyewenh.html  
    10.74.52.51                /zmccwps/welcome/gzsl.html  
    10.74.52.51                /zmccwps/welcome/gsry.html  
    10.74.52.51                /zmccwps/welcome/cylj.html  
    10.74.52.51                /zmccwps/welcome/yewu.html  
    10.74.52.51                /zmccwps/welcome/gzsl.html  
    10.74.52.51                /zmccwps/welcome/gsry.html  
    10.74.52.51                /zmccwps/welcome/yewu.html  
    10.74.52.51            /zmccwps/welcome/qiyewenh.html  
    10.74.52.51                /zmccwps/welcome/gzsl.html

### 统计每个小时的访问次数

    
    
    secsoso 'access.log|eval date=$4.to_date("[dd/MMM/yyyy:HH:mm:ss")|stats count(date) by tspan(date,"1h")'

结果如下:

    
    
    date                                 count_date  
    2013-09-18 06:00:00                   123  
    2013-09-18 07:00:00                  1075  
    2013-09-18 08:00:00                  2167  
    2013-09-18 09:00:00                  1424  
    2013-09-18 10:00:00                   621  
    2013-09-18 11:00:00                   607  
    2013-09-18 12:00:00                   652  
    2013-09-18 13:00:00                   570

### 根据浏览器指纹定位记录

    
    
    secsoso 'access.log "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9) Gecko Minefield/3.0" $7!="*.js*" $7!="*.css*"|fields $1,$4,$7'

红色是排除JS和CSS，结果如下:

    
    
    $1                 $4                            $7  
    123.125.71.103   [18/Sep/2013:07:13:23  /nodejs-bootstrap-select/  
    123.125.71.81    [19/Sep/2013:01:26:14  /r-package-faster/

### 统计爬虫

    
    
    secsoso  'access.log "Googlebot|Baiduspider|Applebot|bingbot|YoudaoBot|Sosospider|MSNBot"|stats dc($1) as count'

结果如下:

    
    
    count  
    63

### 统计每个网段的访问次数

    
    
    secsoso  'access.log| stats rex($1,"[0-3]+\.[0-9]+\.[0-9]+") as ipper,count(1) as count by ipper |sort -count'

结果如下:

    
    
    ipper                  count  
    101.226.68              972  
    3.177.71              972  
    3.195.232              971  
    111.192.165              377  
    2.89.91              374  
    222.70.152              226  
    1.135.216              185

### 统计状态码次数

    
    
    secsoso  'access.log|stats $9 as stat ,count($9) as count by $9'

结果如下:

    
    
    stat            count  
    "-"              848  
    173                1  
    200            12340  
    301               94  
    302              152  
    304              949  
    400               13  
    403                3  
    404              201  
    408                1  
    499                8  
    500                1  
    502                8

### 统计每个 URL 的访问次数

    
    
    secsoso 'access.log|eval url=$7.substring(0,POSITION("?",$7))|stats count(url) by url'

结果如下:

###
![1628844271_611630ef4b249773a5794.png!small?1628844271807](https://image.3001.net/images/20210813/1628844271_611630ef4b249773a5794.png!small?1628844271807)

### 文件流量统计

    
    
    secsoso  ‘access.log|fields $10|stats sum(casewhen($10=“\”-\””,0,$10)) as fluxcount’

红色是函数嵌套，casewhen表示如果第10列等于”-“为零，否则是它自己，然后用sum累加，结果如下:

    
    
    flowcount  
    218704890

### 统计单位时间内访问包含某个URI的IP排名

    
    
    secsoso 'access.log $7="*/wp-content/themes*"|eval date=$4.to_date("[dd/MMM/yyyy:HH:mm:ss")|stats count(date) as count by tspan(date,"1h"),$1|rename tspan_date as time,$1 as ip|sort time,-count'access.log 4.to_date(“[dd/MMM/yyyy:HH:mm:ss”)|stats count(date) as count by tspan(date,”1h”),< src=" https:="" chart.googleapis.com="" chart?cht="tx&chl=1%7Crename%20tspan_date%20as%20time%2C"" class="js_catchremoteimageerror">1 as ip|sort time,-count
    
    
    access.log 4.to_date(“[dd/MMM/yyyy:HH:mm:ss”)|stats count(date) as count by tspan(date,”1h”),<img src=" https:="" chart.googleapis.com="" chart?cht="tx&chl=1%7Crename%20tspan_date%20as%20time%2C"" class="js_catchremoteimageerror">1 as ip|sort time,-count

其中/wp-content/themes 为url关键字

结果如下:

    
    
    time                         ip            count  
    2013-09-18 06:00:00              124.42.13.230               13  
    2013-09-18 06:00:00              71.96.108.116               13  
    2013-09-18 07:00:00              222.247.54.20               26  
    2013-09-18 07:00:00              111.193.224.9               13  
    2013-09-18 07:00:00            113.106.104.210               13  
    2013-09-18 07:00:00             116.226.35.135               13  
    2013-09-18 07:00:00               116.24.8.156               13  
    2013-09-18 07:00:00            118.194.195.205               13  
    2013-09-18 07:00:00                121.8.153.6               13

### 网站登录趋势

对后台网站系统来说，一般会有登录页面，通过登录页面的状态码，可以判断是登录成功还是登录失败，比如/login，如果是post请求返回200，一般是登录失败，post请求返回302，一般表示登录成功，可以通过这个做一些业务的行为分析。比如分钟登录趋势：

    
    
    114.221.137.86 - - [11/Sep/2019:13:44:59 +0800] "POST /login HTTP/1.1" 302 - https://secilog.secisland.com/login Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.105 Safari/537.36 Vivaldi/2.4.1488.40  
      
    secsoso 'access.log $6="*POST" $7="*/login"  $9="302"| eval date=$4.to_date("[dd/MMM/yyyy:HH:mm:ss")|stats count($1) as count by tspan(date,"1m")'

结果如下:

    
    
    tspan_date            count  
    2019-09-11 09:22:00                1  
    2019-09-11 09:40:00                1  
    2019-09-11 13:44:00                1

## 安全统计

### 统计具有cc攻击的用户IP(单位时间内访问次数超过阈值的用户，不包括css 、js、png)：

    
    
    secsoso 'access.log  $7!="/.*\.js.*|.*\.css.*|.*\.png.*/" |eval date=$4.to_date("[dd/MMM/yyyy:HH:mm:ss")|stats $1 as ip,count(date) as count by tspan(date,"1h"),$1|search count>50'

其中 tspan (date,”1h”) 中的 “1h” 支持如下时间单位：

    
    
    秒:s，分钟:m，小时:h，天:d，星期:w，月:mon，年:year

count>50 表示访问次数大于50。

    
    
    $7!="/.*\.js.*|.*\.css.*|.*\.png.*/" 表示不包含css，js，png

结果如下:

    
    
    tspan_date                         ip            count  
    2013-09-18 08:00:00              114.252.89.91               65  
    2013-09-18 08:00:00              60.247.77.253               60  
    2013-09-18 11:00:00               178.24.29.69               79  
    2013-09-18 15:00:00              114.252.89.91               53  
    2013-09-18 17:00:00              208.43.225.84               62  
    2013-09-19 03:00:00             222.70.152.149               91  
    2013-09-19 04:00:00              59.60.115.180               72  
    2013-09-19 05:00:00            111.192.165.229              142

### 统计具有cc攻击的用户IP（单位时间内访问次数超过阈值的用户，包括css 、js、png）

    
    
    secsoso  'access.log|eval date=$4.to_date("[dd/MMM/yyyy:HH:mm:ss")|stats $1 as ip,count(date) as count by tspan(date,"1h"),$1|search count>100'

结果如下:

    
    
    tspan_date                         ip            count  
    2013-09-18 08:00:00              114.252.89.91               79  
    2013-09-18 08:00:00             116.24.236.137               68  
    2013-09-18 08:00:00               202.84.17.41               84  
    2013-09-18 08:00:00               203.192.6.59               83  
    2013-09-18 08:00:00            221.122.104.115               72  
    2013-09-18 08:00:00             58.248.178.212               68  
    2013-09-18 08:00:00              58.56.155.203               83  
    2013-09-18 08:00:00                  60.10.8.5               56  
    2013-09-18 08:00:00              60.247.77.253              146  
    2013-09-18 09:00:00             183.60.177.228              121

### 统计发起 SQL 注入的 IP及URI

    
    
    secsoso 'access.log "%20select%20|%20and%201=1|%20and%201=2|%20exec|%27exec| information_schema.tables|%20information_schema.tables|%20where%20|%20union%20|%20SELECT%20|%2ctable_name%20|cmdshell|%20table_schema"|fields $1,$7'

结果如下:

![](https://image.3001.net/images/20210813/1628844336_61163130d893d7c2402e8.png!small)

#### 统计发起SQL注入的IP并按IP攻击次数排名

    
    
    secsoso 'access.log "%20select%20|%20and%201=1|%20and%201=2|%20exec|%27exec| information_schema.tables|%20information_schema.tables|%20where%20|%20union%20|%20SELECT%20|%2ctable_name%20|cmdshell|%20table_schema"|fields $1,$7|stats $1 as ip,count(1) as count by $1|sort -count'

结果如下:

    
    
    ip                    count  
    66.249.66.84                4  
    111.192.165.229                2

### 敏感文件扫描

    
    
    secsoso  'access.log  ".zip|.rar|.mdb|.inc|.sql|.config|.bak|/login.inc.php|.svn|/mysql/|config.inc.php|.bak|wwwroot|网站备份|/gf_admin/|/DataBackup/|/Web.config|/web.config|/1.txt|/test.txt" |fields $1,$7 '

结果如下:

###

###
漏洞利用![1628844384_61163160071f43f112db9.png!small?1628844384381](https://image.3001.net/images/20210813/1628844384_61163160071f43f112db9.png!small?1628844384381)

    
    
    secsoso 'access.log  "struts|jmx-console|ajax_membergroup.php|iis.txt|phpMyAdmin|getWriter|dirContext|phpmyadmin|acunetix.txt|/e/|/SouthidcEditor/|/DatePicker/" |fields $1,$7'

结果如下:

![1628844394_6116316a4ccb955052104.png!small?1628844394725](https://image.3001.net/images/20210813/1628844394_6116316a4ccb955052104.png!small?1628844394725)

### 文件包含攻击

    
    
    secsoso 'access.log  "/passwd|%00|/win.ini|/my.ini|/MetaBase.xml|/ServUDaemon.ini|cmd.exe" |fields $1,$7'

结果如下:

![1628844406_61163176b6647c47b95d7.png!small?1628844407272](https://image.3001.net/images/20210813/1628844406_61163176b6647c47b95d7.png!small?1628844407272)

### getshell的攻击

    
    
    secsoso 'access.log  " eval|%eval|%execute|%3binsert|%20makewebtaski|/1.asp|/1.jsp|/1.php|/1.aspx|/xiaoma.jsp|/tom.jsp|/py.jsp|/k8cmd.jsp|/k8cmd|/ver007.jsp|/ver008.jsp|/ver007|/ver008|\.aar|%if" |fields $1,$7'

iis可以换成：

    
    
    %20exec|%27exec|%3bexec|%27%3Bexec|%eval|%20eval|%execute|%3Binsert|%20makewebtaski|%20disk%20|%3Balter|%3Bdeclare|dbo|hack523|sysname|/1.asp|/1.jsp|/1.php|/1.aspx|/xiaoma.asp|/yijuhua.asp|/yjh.asp|/hack.asp|/k8cmd.asp|/k8cmd|/ver007.asp|/ver008.asp|/ver007|/ver008|\.asa|\.cer|\.ashx|asp;|asa;|cer;|aspx;|/1.asp/|/x.asp/|/a.asp/|/2.asp/

结果如下:

![1628844423_61163187398ed791f4fb6.png!small?1628844423630](https://image.3001.net/images/20210813/1628844423_61163187398ed791f4fb6.png!small?1628844423630)

### xss跨站脚本攻击

    
    
    secsoso 'access.log  " (S)%3C(S+)%3E|(S)%3C(S+)%2F%3E|(S+)<(S+)>|(S+)<(S+)/>|onerror|onmouse|expression|alert|document.|prompt\()" |fields $1,$7'

结果如下:

### 网站登录密码猜测

比如5分钟大于10次同一个IP登录密码错误，认为是密码猜测，然后把所有IP找到。

    
    
    114.221.137.86 - - [11/Sep/2019:10:25:39 +0800] "POST /login HTTP/1.1" 200 1111 https://secilog.secisland.com/login Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.105 Safari/537.36 Vivaldi/2.4.1488.40  
    secsoso 'access.log $6="*POST" $7="*/login"  $9="200"| eval date=$4.to_date("[dd/MMM/yyyy:HH:mm:ss")|stats count($1) as count by tspan(date,"5m"),$1| search count>10|stats sum(count) by $1'

结果如下:

    
    
    $1            sum_count  
    114.221.137.86                   15

通过上面示例得知，日志中含有丰富的内容，通过这些内容可以分析出很多有价值的信息。但这些分析的前提就是要先保存这些日志，并记录请求参数，但默认的WEB中间件日志只记录GET请求的参数，没有记录POST请求的参数，所以需要通过中间件配置才可以拿到POST的请求参数来进行更多的分析。

拿到参数后还可以继续深入分析更具体的业务行为，操作记录等，比如/asset（示例）表示访问资产模块，/asset/add（示例）表示资产添加模块，/asset?id=1表示查询id为1的资产记录。

文本通过分析WEB中间件日志的示例起到抛砖引玉的目的，来说明日志分析的重要性和思路。希望能对大家的日志分析起到参考和帮助。

> 备注：内容有部分数据来源于网络。

