原创 Qftm 合天智汇

接着上一篇：[信息收集-旅行记（上） -FreeBuf专栏·合天智汇](https://www.freebuf.com/column/225946.html)

## 收集常用端口信息  

在对目标进行漏洞挖掘的过程中，对端口信息的收集是一个很重要的过程，
通过扫描服务器开放的端口以及从该端口判断服务器上存在的服务，就可以对症下药，便于我们渗透目标服务器。

所以在端口渗透信息的收集过程中，我们需要关注常见应用的默认端口和在端口上运行的服务。

端口一般是指TCP/IP协议中的端口，端口号的范围是从0-65535。

## 常见端口&解析&总结  

常用的端口利用及解析总结

端口：21 服务：FTP/TFTP/VSFTPD 总结：爆破/嗅探/溢出/后门 端口：22 服务：ssh远程连接 总结：爆破/openssh漏洞 端口：23
服务：Telnet远程连接 总结：爆破/嗅探/弱口令 端口：25 服务：SMTP邮件服务 总结：邮件伪造 端口：53 服务：DNS域名解析系统
总结：域传送/劫持/缓存投毒/欺骗 端口：67/68 服务：dhcp服务 总结：劫持/欺骗 端口：110 服务：pop3 总结：爆破/嗅探 端口：139
服务：Samba服务 总结：爆破/未授权访问/远程命令执行 端口：143 服务：Imap协议 总结：爆破161SNMP协议爆破/搜集目标内网信息
端口：389 服务：Ldap目录访问协议 总结：注入/未授权访问/弱口令 端口：445 服务：smb 总结：ms17-010/端口溢出
端口：512/513/514 服务：Linux Rexec服务 总结：爆破/Rlogin登陆 端口：873 服务：Rsync服务 总结：文件上传/未授权访问
端口：1080 服务：socket 总结：爆破 端口：1352 服务：Lotus domino邮件服务 总结：爆破/信息泄漏 端口：1433
服务：mssql 总结：爆破/注入/SA弱口令 端口：1521 服务：oracle 总结：爆破/注入/TNS爆破/反弹shell2049Nfs服务配置不当
端口：2181 服务：zookeeper服务 总结：未授权访问 端口：2375 服务：docker remote api 总结：未授权访问 端口：3306
服务：mysql 总结：爆破/注入 端口：3389 服务：Rdp远程桌面链接 总结：爆破/shift后门 端口：4848 服务：GlassFish控制台
总结：爆破/认证绕过 端口：5000 服务：sybase/DB2数据库 总结：爆破/注入/提权 端口：5432 服务：postgresql
总结：爆破/注入/缓冲区溢出 端口：5632 服务：pcanywhere服务 总结：抓密码/代码执行 端口：5900 服务：vnc 总结：爆破/认证绕过
端口：6379 服务：Redis数据库 总结：未授权访问/爆破 端口：7001/7002 服务：weblogic 总结：java反序列化/控制台弱口令
端口：80/443 服务：http/https 总结：web应用漏洞/**滴血 端口：8069 服务：zabbix服务 总结：远程命令执行/注入
端口：8161 服务：activemq 总结：弱口令/写文件 端口：8080/8089 服务：Jboss/Tomcat/Resin
总结：爆破/PUT文件上传/反序列化 端口：8083/8086 服务：influxDB 总结：未授权访问 端口：9000 服务：fastcgi
总结：远程命令执行 端口：9090 服务：Websphere 总结：控制台爆破/java反序列化/弱口令 端口：9200/9300
服务：elasticsearch 总结：远程代码执行 端口：11211 服务：memcached 总结：未授权访问 端口：27017/27018
服务：mongodb 总结：未授权访问/爆破

详细参考：掘安攻防实验室

上合天网安实验室体验相关实验操作：《用Python认识端口扫描》

[实验:用Python认识端口扫描(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID32d0-132b-4acc-aca0-e139dccb0535)

（通过本实验的学习，能让刚入门安全的同学更清楚的认识端口扫描，以及其中涉及的原理知识。）

## 扫描工具  

常用扫描工具

Nmap Masscan ZMap 御剑高速TCP端口扫描工具 御剑高速端口扫描工具 IISPutScanner IISPutScanner增强版-DotNetScan v1.1 Beta masnmapscan

常用扫描工具使用

nmap

项目地址：<https://github.com/nmap/nmap>

扫描多个IP

扫描整个子网 nmap 192.168.6.1/24 nmap 192.168.1.1/16 nmap 192.168.1-30.1-254 nmap
192.168.1-254.6扫描多个主机 namp 192.168.6.2 192.168.6.6扫描一个小范围 nmap
192.168.6.2-10扫描txt内的ip列表 nmap -iL text.txt扫描除某个目标外 nmap 192.168.6.1/24
-exclude 192.168.6.25

绕过Firewalld扫描主机端口

通过不同的协议(TCP半连接、TCP全连接、ICMP、UDP等)的扫描绕过Firewalld的限制

nmap -sP 192.33.6.128 nmap -sT 192.33.6.128 nmap -sS 192.33.6.128 nmap -sU
192.33.6.128 nmap -sF 192.33.6.128 nmap -sX 192.33.6.128 nmap -sN 192.33.6.128

初步扫描端口信息

nmap -T4 -A -v -Pn 192.168.1.1/24 -p
21,22,23,25,80,81,82,83,88,110,143,443,445,512,513,514,1433,1521,2082,2083,2181,2601,2604,3128,3306,3389,3690,4848,5432,5900,5984,6379,7001,7002,8069,8080,8081,8086,8088,9200,9300,11211,10000,27017,27018,50000,50030,50070
-oN nmap_result.txt

![v2-50c50a55d358670bff6887b9d0cf5e84_hd.j](https://pic4.zhimg.com/80/v2-50c50a55d358670bff6887b9d0cf5e84_hd.jpg)

扫描端口并且标记可以爆破的服务

nmap 127.0.0.1 --script=ftp-brute,imap-brute,smtp-brute,pop3-brute,mongodb-brute,redis-brute,ms-sql-brute,rlogin-brute,rsync-brute,mysql-brute,pgsql-brute,oracle-sid-brute,oracle-brute,rtsp-url-brute,snmp-brute,svn-brute,telnet-brute,vnc-brute,xmpp-brute

![v2-330e5c35adc231f0146b9a3a70247210_hd.j](https://pic4.zhimg.com/80/v2-330e5c35adc231f0146b9a3a70247210_hd.jpg)

判断常见的漏洞并扫描端口

nmap 127.0.0.1 --script=auth,vuln

![v2-445f4f756e992a2189ca884bf01ce5fc_hd.j](https://pic3.zhimg.com/80/v2-445f4f756e992a2189ca884bf01ce5fc_hd.jpg)

精确判断漏洞并扫描端口

nmap 127.0.0.1 --script=dns-zone-transfer,ftp-anon,ftp-proftpd-backdoor,ftp-vsftpd-backdoor,ftp-vuln-cve2010-4221,http-backup-finder,http-cisco-anyconnect,http-iis-short-name-brute,http-put,http-php-version,http-shellshock,http-robots.txt,http-svn-enum,http-webdav-scan,iis-buffer-overflow,iax2-version,memcached-info,mongodb-info,msrpc-enum,ms-sql-info,mysql-info,nrpe-enum,pptp-version,redis-info,rpcinfo,samba-vuln-cve-2012-1182,smb-vuln-ms08-067,smb-vuln-ms17-010,snmp-info,sshv1,xmpp-info,tftp-enum,teamspeak2-version

Masscan

项目地址：https://github.com/robertdavidgraham/masscan

Masscan主要是真对全网进行端口扫描

Zmap

项目地址：https://github.com/zmap/zmap

Zmap主要是真对全网进行端口扫描

御剑高速TCP端口扫描工具

![v2-456a53687e421fe468a43b7349d5757d_hd.j](https://pic2.zhimg.com/80/v2-456a53687e421fe468a43b7349d5757d_hd.jpg)

御剑高速端口扫描工具

![v2-114fa45d3b3132d61f9aa9bad46bfebd_hd.j](https://pic3.zhimg.com/80/v2-114fa45d3b3132d61f9aa9bad46bfebd_hd.jpg)

masnmapscan

项目地址：<https://github.com/hellogoldsnakeman/masnmapscan-V1.0>

masnmapscan整合了masscan和nmap两款扫描器，masscan扫描端口，nmap扫描端口对应服务，二者结合起来实现了又快又好地扫描。并且加入了针对目标资产有防火墙的应对措施。

网络空间引擎搜索

shodan、FOFA、zoomeye

FOFA为例

https://fofa.so/

![v2-3181d94f6b30f4769f91c8629f5e694e_hd.j](https://pic3.zhimg.com/80/v2-3181d94f6b30f4769f91c8629f5e694e_hd.jpg)

浏览器插件

通过Google、FireFox等插件的使用，收集主机端口开放信息

Shodan

![v2-fd15fe59d2e9eaec79bbe81a9c2b39be_hd.j](https://pic1.zhimg.com/80/v2-fd15fe59d2e9eaec79bbe81a9c2b39be_hd.jpg)

TCPIPUTILS

![v2-b689cb788697718778352d511256abf3_hd.j](https://pic2.zhimg.com/80/v2-b689cb788697718778352d511256abf3_hd.jpg)

DNSlytics

![v2-37a6630be2ee415d1ce4e5ccdaa6214f_hd.j](https://pic1.zhimg.com/80/v2-37a6630be2ee415d1ce4e5ccdaa6214f_hd.jpg)

关于这一方面的知识，小编推荐实验：《渗透扫描工具使用》

[课程:渗透扫描工具使用(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C9d6c0ca797abec2017041916081500001)

（通过本课程的学习，你将掌握如何通过漏洞扫描工具快速发现目标漏洞，从而为下一步的安全测试做好准备。）

## 指纹识别  

在漏洞挖掘中，对目标服务器进行指纹识别是相当有必要的，因为只有识别出相应的Web容器或者CMS，才能查找与其相关的漏洞，然后才能进行相应的渗透操作。

CMS (Content Management System)又称整站系统或文章系统。常见的CMS有Dedecms (织梦)、Discuz、 PHPWEB、
PHPWind、PHPCMS、ECShop、 Dvbbs、 SiteWeaver、 ASPCMS、帝国、Z- Blog、WordPress等。

## 第三方平台  

云悉 http://www.yunsee.cn/

TideFinger http://finger.tidesec.net/

BugScaner http://whatweb.bugscaner.com/look/

数字观星 https://fp.shuziguanxing.com/#/

![v2-4440cccce5629a20e31d20a60dcaa103_hd.j](https://pic3.zhimg.com/80/v2-4440cccce5629a20e31d20a60dcaa103_hd.jpg)

## 工具  

常用指纹识别工具有：御剑Web指纹识别、WhatWeb、Test404轻量CMS指纹识别+v2.1、椰树等，可以快速识别一些主流CMS

![v2-d2bc9f98f80ea5a3f11684deba2516bf_hd.j](https://pic3.zhimg.com/80/v2-d2bc9f98f80ea5a3f11684deba2516bf_hd.jpg)

Github项目

[CMSeeK](https://github.com/Tuhinshubhra/CMSeeK)
[CMSmap](https://github.com/Dionach/CMSmap)[ACMSDiscovery](https://github.com/aedoo/ACMSDiscovery)[TideFinger](https://github.com/TideSec/TideFinger)[AngelSword](https://github.com/Lucifer1993/AngelSword)

![v2-f678b5da3b8efa63a68e24b186a***15_hd.j](https://pic1.zhimg.com/80/v2-f678b5da3b8efa63a68e24b186a***15_hd.jpg)

浏览器插件

通过Google、FireFox等插件的使用，收集网站结构信息

Wappalyzer

![v2-7cf2ab0c14a4321a1aeb01502f58f26a_hd.j](https://pic1.zhimg.com/80/v2-7cf2ab0c14a4321a1aeb01502f58f26a_hd.jpg)

《python爬虫-WEB目录爆破和指纹识别》

http://www.hetianlab.com/expc.do?ec=ECID8c3b-a997-48f1-a59b-70259fe9b2ec

快复制链接体验实验

收集敏感信息

## WAF识别  

识别网站使用的什么WAF，可以去找相应的绕过手段

### wafw00f  

项目地址：https://github.com/EnableSecurity/wafw00f

![v2-f87e74073e05dd0b5585a5449426b6d8_hd.j](https://pic3.zhimg.com/80/v2-f87e74073e05dd0b5585a5449426b6d8_hd.jpg)

源码泄露

### 常见源码泄露  

/.bzr/ /CVS/Entries /CVS/Root /.DS_Store MacOS自动生成 /.hg//.svn/ (/.svn/entries)
/.git//WEB-INF/src/ /WEB-INF/lib/ /WEB-INF/classes//WEB-INF/database.properties /WEB-INF/web.xml Robots.txt

上述源码泄露在Github上都可以找到相应的利用工具

源码泄露扫描工具

将常见源码泄露加入字典配合FUZZ、御剑等扫描器进行扫描收集

源码泄露利用工具

.git源码泄露：<https://github.com/lijiejie/GitHack>

.DS_Store泄露：<https://github.com/lijiejie/ds_store_exp>

.bzr、CVS、.svn、.hg源码泄露：<https://github.com/kost/dvcs-ripper>

备份文件泄露

网站备份文件泄露常见名称

backup db data web wwwroot database www code test admin user sql

网站备份文件泄露常见后缀

.bak. html _index.html .swp .rar .txt .zip .7z .sql .tar .gz .tgz .tar

网站备份文件泄露扫描工具

常见扫描工具有：Test404网站备份文件扫描器 v2.0、ihoneyBakFileScan等

ihoneyBakFileScan v0.2 多进程批量网站备份文件泄露扫描工具，根据域名自动生成相关扫描字典，自动记录扫描成功的备份地址到文件

![v2-6a66b979bad03e0eb439843792a33c14_hd.j](https://pic4.zhimg.com/80/v2-6a66b979bad03e0eb439843792a33c14_hd.jpg)

Google Hacking

常用GoogleHacking语法

1、intext：（仅针对Google有效）把网页中的正文内容中的某个字符作为搜索的条件

2、intitle：把网页标题中的某个字符作为搜索的条件

3、cache：搜索搜索引擎里关于某些内容的缓存，可能会在过期内容中发现有价值的信息

4、filetype/ext：指定一个格式类型的文件作为搜索对象

5、inurl：搜索包含指定字符的URL

6、site：在指定的(域名)站点搜索相关内容

其他GoogleHacking语法

1、引号 '' "把关键字打上引号后，把引号部分作为整体来搜索

2、or同时搜索两个或更多的关键字

3、link搜索某个网站的链接 link:baidu.com即返回所有和baidu做了链接的URL

4、info查找指定站点的一些基本信息

GoogleHacking典型用法

管理后台地址

site:target.com intext:管理 | 后台 | 后台管理 | 登陆 | 登录 | 用户名 | 密码 | 系统 | 账号 | login |
system site:target.com inurl:login | inurl:admin | inurl:manage |
inurl:manager | inurl:admin_login | inurl:system | inurl:backend
site:target.com intitle:管理 | 后台 | 后台管理 | 登陆 | 登录

上传类漏洞地址

site:target.com inurl:filesite:target.com inurl:upload

注入页面

site:target.com inurl:php?id=

编辑器页面

site:target.com inurl:ewebeditor

目录遍历漏洞

site:target.com intitle:index.of

SQL错误

site:target.com intext:"sql syntax near" | intext:"syntax error has occurred"
| intext:"incorrect syntax near" | intext:"unexpected end of SQL command" |
intext:"Warning: mysql_connect()" | intext:”Warning: mysql_query()" |
intext:”Warning: pg_connect()"

phpinfo()

site:target.com ext:php intitle:phpinfo "published by the PHP Group"

配置文件泄露

site:target.com ext:.xml | .conf | .cnf | .reg | .inf | .rdp | .cfg | .txt |
.ora | .ini

数据库文件泄露

site:target.com ext:.sql | .dbf | .mdb | .db

日志文件泄露

site:target.com ext:.log

备份和历史文件泄露

site:target.com ext:.bkf | .bkp | .old | .backup | .bak | .swp | .rar | .txt |
.zip | .7z | .sql | .tar.gz | .tgz | .tar

公开文件泄露

site:target.com filetype:.doc | .docx | .xls | .xlsx | .ppt | .pptx | .odt |
.pdf | .rtf | .sxw | .psw | .csv

邮箱信息

site:target.com intext:@target.com site:target.com 邮件 site:target.com email

社工信息

site:target.com intitle:账号 | 密码 | 工号 | 学号 | ***

![v2-8d18e2890ec451d135513f79235417c0_hd.j](https://pic1.zhimg.com/80/v2-8d18e2890ec451d135513f79235417c0_hd.jpg)

## JS获取敏感接口  

JSFinder

JSFinder是一款用作快速在网站的js文件中提取URL，子域名的工具。

安装

pip3 install requests bs4 git clone https://github.com/Threezh1/JSFinder.git

使用

python3 JSFinder.py -u http://www.mi.com python3 JSFinder.py -u
http://www.mi.com -d

![v2-9f8024470c5ca88b9a43baf77403d764_hd.j](https://pic1.zhimg.com/80/v2-9f8024470c5ca88b9a43baf77403d764_hd.jpg)

LinkFinder

该工具通过网站中的JS文件来发现服务端、敏感信息、隐藏控制面板的URL链接等有用信息，可最大化地提高URL发现效率

安装

git clone https://github.com/GerbenJavado/LinkFinder.git cd LinkFinder python2
setup.py install

使用

在线JavaScript文件中查找端点的最基本用法，并将结果输出到results.html：

python linkfinder.py -i https://example.com/1.js -o results.html

CLI输出（不使用jsbeautifier，这使得它非常快）：

pyhon linkfinder.py -i https://example.com/1.js -o cli

分析整个域及其JS文件：

python linkfinder.py -i https://example.com -d

Burp输入（在目标中选择要保存的文件，右键单击，Save selected items将该文件作为输入）：

python linkfinder.py -i burpfile -b

枚举JavaScript文件的整个文件夹，同时查找以/ api /开头的终结点，并最终将结果保存到results.html：

python linkfinder.py -i 'Desktop/*.js' -r ^/api/ -o results.html

![v2-b46d8db7d022eb24bfcbbc027a4c6459_hd.j](https://pic3.zhimg.com/80/v2-b46d8db7d022eb24bfcbbc027a4c6459_hd.jpg)

## 目录&后台扫描  

常用工具-自己

7kbscan-WebPathBrute https://github.com/7kbstorm/7kbscan-WebPathBrute DirMap
https://github.com/H4ckForJob/dirmap dirsearch
https://github.com/maurosoria/dirsearch Fuzz-gobuster
https://github.com/OJ/gobuster Fuzz-dirbuster OWASP kali自带 Fuzz-wfuzz
https://github.com/xmendez/wfuzz Test404轻量后台扫描器+v2.0 御剑

个人比较喜欢使用Fuzz大法，不管是目录扫描、后台扫描、Web漏洞模糊测试都是非常灵活的。这几款fuzz工具都比较好用

基于Go开发：gobuster 基于Java开发：dirbuster 基于Python开发：wfuzz

dirbuster

![v2-610782506e66cd0bbb0809f2882ea148_hd.j](https://pic2.zhimg.com/80/v2-610782506e66cd0bbb0809f2882ea148_hd.jpg)

wfuzz

![v2-2ff53bf35c4a474b4d04fa5d4455ac9f_hd.j](https://pic1.zhimg.com/80/v2-2ff53bf35c4a474b4d04fa5d4455ac9f_hd.jpg)

工具无论再多再好，没有一个好的字典一切都是空谈。强大字典是需要自己平时慢慢的积累。

## 越权查询  

遍历uid获得身份信息等

## 代码托管  

通过代码托管平台搜索敏感信息（内部邮箱账号密码、数据库账号密码等）

github

GitHub是一个面向开源及私有软件项目的托管平台。

平台地址：https://github.com/

GitHub敏感信息泄露一直是企业信息泄露和知识产权泄露的重灾区，安全意识薄弱的同事经常会将公司的代码、各种服务的账户等极度敏感的信息『开源』到github中，github也是黑、白帽子、安全工程师的必争之地。

Github泄露扫描系统开发：https://sec.xiaomi.com/article/37

在GitHub中一般通过搜索网站域名、网站JS路径、网站备案、网站下的技术支持等进行敏感信息查询

![v2-af7c8f62ea5d4b6cce96fcf466bab4a9_hd.j](https://pic3.zhimg.com/80/v2-af7c8f62ea5d4b6cce96fcf466bab4a9_hd.jpg)

gitee

平台地址：<https://gitee.com/>

码云：开源中国出品的代码托管、协作开发平台。

gitcafe

GitCafe一个基于代码托管服务打造的技术协作与分享平台

Whois&备案查询

通过Whois和备案查询得到网站的注册人、手机号、邮箱等（对后续的密码生成和社工很有帮助）

公网网盘

公司员工可能把一些内部资料放在了公网网盘，然后被在线云网盘搜索的网站抓取了，我们就可以利用这个来对目标系统进行深入挖掘。

可以利用云网盘搜索工具搜集敏感文件，一般直接输入厂商名字进行搜索

凌风云搜索

地址：<https://www.lingfengyun.com/>

![v2-1070d82a30a94207f7d778636b38360d_hd.j](https://pic2.zhimg.com/80/v2-1070d82a30a94207f7d778636b38360d_hd.jpg)

## 网站截图  

对目标网站页面进行截图，通过截图找到敏感页面

webscreenshot

基于url-to-image的网站截图工具

安装

git clone https://github.com/maaaaz/webscreenshot.gitapt-get update && apt-get
-y install phantomjsphantomjs -vUbuntu 16 中安装 phantomjs 出现 QXcbConnection 问题
export QT_QPA_PLATFORM=offscreen export QT_QPA_FONTDIR=/usr/share/fonts

使用

cd webscreenshot/ python2.7 webscreenshot.py -i url.txt

![v2-dc37395333a50f2ba9cbf09ebec3c43b_hd.j](https://pic4.zhimg.com/80/v2-dc37395333a50f2ba9cbf09ebec3c43b_hd.jpg)

## 获取公开文件  

snitch

Snitch可以针对指定域自动执行信息收集过程。此工具可帮助收集可通过Web搜索引擎找到的指定信息。在渗透测试的早期阶段，它可能非常有用。

安装

git clone https://github.com/Smaash/snitch.git

使用

python2.7 snitch.py -C "site:whitehouse.gov filetype:pdf" -P 100

![v2-1308b105fa2f373301ac18938e076e1a_hd.j](https://pic1.zhimg.com/80/v2-1308b105fa2f373301ac18938e076e1a_hd.jpg)

Google Hacking

site:target.com filetype:.doc | .docx | .xls | .xlsx | .ppt | .pptx | .odt |
.pdf | .rtf | .sxw | .psw | .csv

![v2-e7cf545af3ce829d80cd8ccc7f27f3b9_hd.j](https://pic2.zhimg.com/80/v2-e7cf545af3ce829d80cd8ccc7f27f3b9_hd.jpg)

## 邮箱信息收集  

Infoga

Infoga可从不同的公共源网络（搜索引擎，pgp密钥服务器和shodan）收集电子邮件帐户信息（ip，主机名，国家/地区...）。是一个用法非常简单的工具，但是，对于渗透测试的早期阶段，或者只是为了了解自己公司在互联网上的可见性是非常有效的。

安装

git clone https://github.com/m4ll0k/Infoga.git /data/infoga cd /data/infoga
pip3 install requests python3 infoga.py

使用

site:target.com intext:@target.com site:target.com 邮件 site:target.com email

![v2-391972dbb78ec2aaae602434ff4e0fac_hd.j](https://pic4.zhimg.com/80/v2-391972dbb78ec2aaae602434ff4e0fac_hd.jpg)

历史漏洞&资产

很多时候去查看目标的历史漏洞和资产信息，往往能够得到很多有价值的信息。

乌云漏洞库

平台地址：<https://github.com/hanc00l/wooyun_public>

Exploit-db

平台地址：<https://www.exploit-db.com/>

Securityfocus

平台地址：<https://www.securityfocus.com/bid>

Cxsecurity

平台地址：<https://cxsecurity.com/exploit/>

国家信息安全漏洞库

平台地址：<http://www.cnnvd.org.cn/>

Seebug

平台地址：<https://www.seebug.org/>

等。。。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

