## Google

### 介绍

谷歌作为最大的搜索引擎，利用其强大的搜索能力可以方便快捷的找到我们需要的信息，例如：子域名、后台管理地址、敏感信息、以及可能存在漏洞的网页

### 通配符

通配符

|

语义

|

说明

|

示例  
  
---|---|---|---  
  
+

|

包含关键词

|

+前面必须有一个空格

|

admin +login  
  
-
|

排除关键词

|

-前面必须有一个空格

|

mysql -csdn  
  
~

|

同义词

|

~前面必须有一个空格

|

天津 ~天津  
  
*

|

模糊查询

|

*代替任意字符

|

mmysql**  
  
""

|

强调

|

-
|

"mysql"  
  
### 高级语法

语法

|

语义  
  
---|---  
  
intitle

|

包含标题  
  
intext

|

包含内容  
  
filetype

|

文件类型  
  
info

|

基本信息  
  
site

|

指定网站  
  
inurl

|

包含某个URL  
  
link

|

包含指定链接的网页  
  
cache

|

显示页面的缓存版本  
  
numberange

|

搜索一个数字  
  
index of/

|

可以进入网站首页的文件中  
  
allintitle

|

类似于intitle,可对多词使用  
  
 **常用查询：**

    
    
    filetype:txt 登录  
    filetype:xls 登录  
    filetype:doc 登录
     
    intitle:后台管理  
    intitle:login
    intitle:后台管理  inurl:admin  
    intitle:登陆 intext:username inurl:login.jsp
    intitle:"index of /" 
    intitle:"index of" passwd
    intitle:"Index of" .bash_history
    intitle:"Index of" .sh_history
    intitle:"index of" etc
     
    site:218.87.21.*
    site:example.com filetype:txt 登录  
    site:example.com intitle:后台管理
    site:example.com admin
    site:example.com login
    site:example.com system
    site:example.com 管理
    site:example.com 登录
    site:example.com 内部
    site:example.com 系统
    site:example.com intext:index of / | ../ | Parent Directory
    site:example.com inurl:aspx|jsp|php|asp
    site:example.com inurl:file|load|editor|Files
    site:example.com filetype:mdb|asp|#
     
    inurl:/admin intext:后台管理系统
    inurl:admin  filetype:cfg
    inurl:admin  filetype:db
    inurl:admin  filetype:txt
    inurl:/phpmyadmin/index.php
    inurl:/admin/login.php
    inurl:editor/db/

## Shodan

### 介绍

Shodan是目前最为知名的黑客搜索引擎，它是由计算机程序员约翰·马瑟利（John
Matherly）于2009年推出的，他在2003年就提出了搜索与Internet链接的设备的想法。发展至今已经变成搜索资源最全，搜索性能最强，TOP1级别的网络资产搜索引擎。

shodan网络搜索引擎偏向网络设备以及服务器的搜索

### 语法

    
    
    hostname：      # 搜索指定的主机或域名,例如 hostname:"google"
    port：          # 搜索指定的端口或服务,例如 port:"21"
    country：       # 搜索指定的国家,例如 country:"CN"
    city：          # 搜索指定的城市,例如 city:"Hefei"
    org：           # 搜索指定的组织或公司,例如 org:"google"
    isp：           # 搜索指定的ISP供应商,例如 isp:"China Telecom"
    product：       # 搜索指定的操作系统/软件/平台,例如 product:"Apache httpd"
    version：       # 搜索指定的软件版本,例如 version:"1.6.2"
    geo：           # 搜索指定的地理位置,参数为经纬度,例如 geo:"31.8639, 117.2808"
    before/after：  # 搜索指定收录时间前后的数据,格式为dd-mm-yy,例如 before:"11-11-15"
    net：           # 搜索指定的IP地址或子网,例如 net:"210.45.240.0/24"a
    vuln            #CVE漏洞编号，例如：vuln：CVE-2014-0723
    os              #操作系统类型
    http.html       #网页内容
    html.title      #网页标题
    http.server     #http请求返回中server的类型
    http.status     #http请求返回响应码的状态

### 实例

    
    
    port:554 has_screenshot:true    # RTSP未授权访问
    port:5900 screenshot.label:loggedin    # 无认证vnc
    apache city:"Hefei"  
    nginx country:"CN" 
    huawei net:"61.191.146.0/24" 
    Server: uc-httpd 1.0.0 200 OK Country:"CN"  #弱密码（admin, ）

### 使用方法

  * [网页访问](https://www.shodan.io/)
  * 命令行下使用 Shodan
    * Shodan 是有官方 Python 库的，项目位于：https://github.com/achillean/shodan-python
    *         pip install shodan         #安装
        shodan init [API_Key]                  #初始化
        shodan count microsoft iis 6.0         #返回查询的结果数量
        shadon download file microsft iis 6.0  #将搜索结果下载到一个文件中

  * [命令行使用方法参考](https://cli.shodan.io/)
  * [代码中使用 Shodan 库](https://developer.shodan.io/api/clients)

## FoFa

### 介绍

FOFA是白帽汇推出的一款网络空间资产搜索引擎。它能够帮助用户迅速进行网络资产匹配、加快后续工作进程。例如进行漏洞影响范围分析、应用分布统计、应用流行度排名统计等。

FoFa更加偏向资产搜索。

### 语法

    
    
    domain="qq.com"   #搜索根域名带有qq.com的网站。例： 根域名是qq.com的网站。
    host=".gov.cn"    #从url中搜索.gov.cn,注意搜索要用host作为名称。
    port="443"        #查找对应443端口的资产。例： 查找对应443端口的资产。
    ip="1.1.1.1"      #从ip中搜索包含1.1.1.1的网站,注意搜索要用ip作为名称。
    server="Apache"   #搜索apache的服务器
    os="centos"       #搜索centos所有主机
    title="abc"       #从标题中搜索abc。例：标题中有北京的网站。
    header="abc"      #从http头中搜索abc。例：jboss服务器、Hikvision。
    body="abc"        #从html正文中搜索abc。例：正文包含Hacked by。
    protocol="https"  #搜索制定协议类型(在开启端口扫描的情况下有效)。例： 查询https协议资产。
    city="Beijing"    #搜索指定城市的资产。例： 搜索指定城市的资产。
    region="Zhejiang" #搜索指定行政区的资产。例： 搜索指定行政区的资产。
    country="CN"      #搜索指定国家(编码)的资产。例： 搜索指定国家(编码)的资产。
    cert="google.com" #搜索证书(https或者imaps等)中带有google.com的资产。

### 实例

    
    
    title="后台管理"
    title="powered by" && title!=discuz
    title!="powered by" && body=discuz
    ( body="content=\"WordPress" || (header="X-Pingback" && header="/xmlrpc.php" && body="/wp-includes/") ) && host="gov.cn"

如何搜索关键词可以看看[大佬的总结](https://redyanly.github.io/2019/08/08/FOFA%E7%AE%80%E4%BB%8B%E5%8F%8A%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/)，非常的详细清楚。

### 使用方式

  * [网页访问](https://fofa.so/)
  * 会员可以使用客户端
  * [API接口](https://fofa.so/static_pages/api_help)

## Zoomeye

### 介绍

ZoomEye
是北京知道创宇公司发布的网络空间侦测引擎，积累了丰富的网络扫描与组件识别经验。在此网络空间侦测引擎的基础上，结合“知道创宇”漏洞发现检测技术和大数据情报分析能力，研制出网络空间雷达系统，为政府、企事业及军工单位客户建设全球网络空间测绘提供技术支持及产品支撑。

ZoomEye 支持公网设备指纹检索和 Web
指纹检索。网站指纹包括应用名、版本、前端框架、后端框架、服务端语言、服务器操作系统、网站容器、内容管理系统和数据库等。设备指纹包括应用名、版本、开放端口、操作系统、服务名、地理位置等。

Zoomeye更加偏向web应用层面的搜索，并且对国内的搜索结果做了处理。

### 语法

    
    
    app:nginx　　          #组件名
    ver:1.0　　            #版本
    os:windows　　         #操作系统
    country:"China"　　    #国家
    city:"hangzhou"　　    #城市
    port:80　　            #端口
    hostname:google　      #主机名
    site:google.com　　    #网站域名
    desc:nmask　　         #描述
    keywords:Nginx　　     #关键词
    service:ftp　　        #服务类型
    headers:Server        #http头
    title:Nginx           #页面标题
    ip:8.8.8.8　　         #ip地址
    cidr:8.8.8.8/24　　    #ip地址段

### 实例

    
    
    app:apache ver:2.4
    OS：Linux port:22
    country:China city：Beijing
    site:www.baidu.com
    keyword:technology
    app:"Cisco TANDBERG Codian ISDN GW 3240 video conference system ftp"
    app:"骑士cms"

### 使用方法

  * [网页访问](https://www.zoomeye.org/)
  * [API接口](https://www.zoomeye.org/doc)

## censys

### 介绍

censys搜索引擎功能与shodan类似，能够扫描整个互联网，Censys
每天都会扫描IPv4地址空间，以搜索所有联网设备并收集相关的信息，并返回一份有关资源（如设备、网站和证书）配置和部署信息的总体报告。

地址：https://www.censys.io/

### 语法

    
    
    #默认情况下censys支持全文检索。
    #支持正则表达式
    23.0.0.0/8 or 8.8.8.0/24　　    #可以使用and or not
    80.http.get.status_code: 200　　#指定状态
    80.http.get.status_code:[200 TO 300]　　#200-300之间的状态码
    location.country_code: DE　　#国家
    protocols: (“23/telnet” or “21/ftp”)　　#协议
    tags: scada　　#标签
    80.http.get.headers.server：nginx　　#服务器类型版本
    autonomous_system.description: University　　#系统描述

### 使用方法

https://www.censys.io/certificates/help #帮助文档  
https://www.censys.io/ipv4?q= #ip查询  
https://www.censys.io/domain?q= #域名查询  
https://www.censys.io/certificates?q= #证书查询

## Dnsdb

### 介绍

dnsdb搜索引擎是一款针对dbs解析的查询平台。

地址：https://www.dnsdb.io/

### 语法

条件名称

|

解释

|

实例  
  
---|---|---  
  
domain

|

查询指定域名下的所有DNS解析记录

|

该查询条件的值应该是顶级私有域名 domain:google.com  
  
host

|

查询该主机地址对应的解析记录

|

host:www.google.com  
  
ip

|

查询解析到指定的IP地址的DNS记录

|

ip:8.8.8.8 or ip:8.8.8.8/24 or ip:8.8.8.0-8.8.8.255  
  
type

|

限制DNS记录类型

|

type:a  
  
value.domain

|

匹配DNS记录value值出现的顶级私有域名

|

value.domain:google.com  
  
value.host

|

匹配DNS记录value中出现的主机地址

|

value.host:www.google.com  
  
value.ip

|

查询DNS记录中value出现的IP

|

value.ip:8.8.8.8 or value.ip:8.8.8.8/24  
  
email

|

匹配DNS记录value中出现的email地址

|

  
  
  
  

