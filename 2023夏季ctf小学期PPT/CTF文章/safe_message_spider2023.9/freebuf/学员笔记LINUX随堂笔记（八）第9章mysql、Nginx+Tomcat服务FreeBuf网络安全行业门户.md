**文章来源：知了堂冯老师原创**

![v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.j](https://pic4.zhimg.com/80/v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.jpg)

##  接上文  

## 第9章 mysql、Nginx+Tomcat服务

## 一. MySQL

### 1.1 MySQL服务基础

### 1.1.1 MySQL的特点

多线程、多用户

基于C/S（客户端/服务器）架构

简单易用、查询速度快

安全可靠

### 1.1.2 所需软件安装包

1、ncurses-devel-5.7-3.20090208.el6.x86_64.rpm

2、cmake-2.8.6.tar.gz

3、mysql-5.5.22.tar.gz

### 1.1.3 MySQL主要安装步骤

1、卸载mysql-server，mysql，安装ncurses包

2、编译安装cmake包

3、源码编译及安装MySql

4、安装后的其他调整

5、添加为系统服务，启动服务

### 1.1.4 MySQL搭建配置命令

1.卸载mysql-server，mysql，安装ncurses包

# rpm -q mysql-server mysql //确认没有使用RPM方式安装mysql-server、mysql

# rpm -ivh ncurses-devel-5.7-3.20090208.el6.x86_64.rpm //安装ncurses-devel包

2.编译安装cmake包

# tar zxf cmake-2.8.6.tar.gz

# cd cmake-2.8.6

# ./configure

#gmake && gmake install

3.源码编译及安装

#groupadd _mysql_ //添加mysql组

#useradd -M -s /sbin/nologin _mysql_ -g _mysql_ //添加mysql组的用户mysql

#tar zxf mysql-5.5.22.tar.gz -C _/usr/src/_

#cd /usr/src/mysql-5.5.22/

#cmake

-DCMAKE_INSTALL_PREFIX= _/usr/local/mysql_ //指定编译安装位置

-DSYSCONFDIR= _/etc_

-DDEFAULT_CHARSET= _utf8_ //设置默认字体

-DDEFAULT_COLLATION= _utf8_general_ci_

-DWITH_EXTRA_CHARSETS=all

#make

#make install

4.安装后的其他调整

#chown -R _mysql:mysql /usr/local/mysql_ //设置数据库的目录权限

#cp support-files/my-medium.cnf /etc/my.cnf //建立配置文件

#/usr/local/mysql/scripts/mysql_install_db

\--user= _mysql_ \--basedir= _/usr/local/mysql_ \--datadir=
_/usr/local/mysql/data/_ //初始化数据库

#echo "PATH=$PATH:/usr/local/mysql/bin" >> /etc/profile //设置环境变量

#./etc/profile //执行环境变量配置

### 1.2加为系统服务，启动服务

#cp support-files/mysql.server /etc/rc.d/init.d/mysqld

#chmod +x /etc/rc.d/init.d/mysqld //添加可执行权限

#chkconfig --add mysqld //添加mysqld系统服务

#service mysqld start //启动mysql

#/etc/init.d/mysql status //查看mysql的启动状态

#netstat -anpt | grep mysqld //查看mysql服务端口

### 1.3访问MySQL数据库

#mysql -u _root_ [-p] //-u后面为登录用户，-p为有密码登录

#mysql -u root -p password //设置数据库用户名的密码

#mysql>exit //退出MySQL操作环境

### 1.4维护数据库及用户权限

### 1.4.1设置用户权限

GRANT 权限列表 ON 数据库名.表名 TO 用户名@来源地址 [ IDENTIFIED BY ‘密码’]

//用户不存在时，则新建用户

SHOW GRANTS FOR 用户名@来源地址 //查看用户的权限

REVOKE 权限列表 ON 数据库名.表名 FROM 用户名@来源地址 //撤销用户的权限

### 1.4.2数据库的备份与恢复

1.数据库的备份

mysqldump –u 用户名 –p [密码] [选项] [数据库名] [表名] > /备份路径/备份文件名

常见选项：--all-databases、--opt

#mysqldump –u root –p _mysql user_ > _/mysoft/mysql-user.sql_ //备份表

#mysqldump –u root –p --databases mysql > _/mysoft/mysql.sql_ //备份库

#mysqldump –u root –p –opt --all-databases > _all-data.sql_ //备份所有库

2.数据库的恢复

mysql -u root -p [数据库名] < /备份路径/备份文件名

#mysql -u root -p _test_ < _/mysoft/mysql-user.sql_

#mysql -u root -p < _/mysoft/mysql.sql_

## 二. Apache

### 2.1 Apache网站服务基础

### 2.1.1所需软件包

1、bind-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

2、bind-chroot-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

3、bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64

4、bind-utils-9.8.2-0.17.rc1.el6_4.6.x86_64 //安装dns

5、httpd-2.2.17.tar.gz //安装httpd服务器

6、awstats-7.3.tar.gz //安装AWStats分析系统

### 2.1.2 httpd服务的主要配置文件和目录

服务目录 /usr/local/httpd/

主配置文件 /usr/local/httpd/conf/httpd.conf

网页目录 /usr/local/httpd/htdocs/

服务脚本 /usr/local/httpd/bin/apachectl

执行程序 /usr/local/htppd/bin/httpd

访问日志 /usr/local/httpd/log/access_log

错误日志 /usr/local/httpd/log/error_log

### 2.2 httpd服务器安装

### 2.2.1httpd服务器主要安装步骤

1、卸载安装的httpd软件包

2、源码编译安装

3、优化执行路径

4、添加httpd系统服务

### 2.2.2httpd服务器的安装配置命令

1.卸载安装的httpd软件包

#rpm -qa httpd //查询已安装的httpd软件包

#rpm -e httpd -nodeps //若已安装，卸载

2.源码编译安装

#tar zxf httpd-2.2.17.tar.gz -C _/usr/src/_ //解压httpd软件包

#cd /usr/src/httpd-2.2.17

#./configure --prefix= _/usr/local/httpd_ \--enable-so

\--enable-rewrite --enable-charset-lite --enable-cgi

#make && make install

3.优化执行路径

#ln -s /usr/local/httpd/bin/* _/usr/local/bin_ //创建bin目录下的链接

#ls -l /usr/local/bin/httpd _/usr/local/bin/apachectl_ //查看链接

#httpd -v = _/usr/local/httpd/bin/httpd-v_

4.添加httpd系统服务

# cp /usr/local/httpd/bin/apachectl /etc/init.d/httpd //拷贝配置文件到启动项

# vi /etc/init.d/httpd //进入启动项配置

#!/bin/bash

# chkconfig: 35 85 15

# description: Startup script for the Apache HTTP Server

……

# chkconfig --add httpd //添加httpd服务

# chkconfig --list httpd //列出httpd服务设置

### 2.3 Web站点部署

首先确定网站名称、ip地址，并在dns中设置

### 2.3.1配置主配置文件

#vim /usr/local/httpd/conf/httpd.conf

ServerName _[http://
test.benet.com](https://link.zhihu.com/?target=http%3A//test.benet.com)_
//指定网站名

#/usr/local/httpd/bin/apachectl –t //语法检查

### 2.3.2启动httpd服务

#/etc/init.d/httpd start //启动httpd服务

#netstat -anpt |grep httpd //查看httpd运行端口

### 2.3.3 部署网页文档

#vim /usr/local/httpd/htdocs/ _index.html_

### 2.4部署AWStats分析系统

### 2.4.1安装AWStats软件包

#tar zxf awstats-7.3.tar.gz //解压awstats软件包

#mv awstats-7.3 _/usr/local/awstats_ //移动awstats包到指定路径

### 2.4.2 建立站点统计配置文件

#cd /usr/local/awstats/tools/

#chmod +x awstats_configure.pl //添加可执行权限

#./awstats_configure.pl //执行交互式配置过程

> _/usr/local/httpd/conf/httpd.conf_ //输入主配置文件路径

Y 确认修改日常类型

Y 确认创建新的站点统计配置文件

>
> [http://test.benet.com](https://link.zhihu.com/?target=http%3A//test.benet.com)
> //制定要统计的目标站点名称

> //回车两次完成

//如果需要统计其他站点日志，可以再执行脚本创建新配置文件

### 2.4.3 修改站点统计配置文件

#vim /etc/awstats/ _awstats.test.bente.com.conf_

LogFile=" _/usr/local/httpd/logs/access_log_ " //指定日志文件路径

DirData=" _/var/lib/awstats_ " //指定统计数据存放目录

#mkdir _/var/lib/awstats_

### 2.4.4 执行日志分析，并设置cron计划任务

#chmod +x awstats_updateall.pl //添加可执行权限

#./awstats_updateall.pl //执行配置文件

#crontab –e

# /usr/local/awstats/tools/awstats_updateall.pl

#/etc/init.d/crond start

#chkconfig --level 35 crond on

### 2.4.5访问AWStats测试

httpd://[http://test.benet.com/awstats/awstats.pl?config=test.benet.com](https://link.zhihu.com/?target=http%3A//test.benet.com/awstats/awstats.pl%3Fconfig%3Dtest.benet.com)

# vim /usr/local/httpd/htdocs/aws.html

<html>

<head>

<meta http-equiv=refresh content="0;

url=[http://www.benet.com/awstats/awstats.pl?config=www.benet.com](https://link.zhihu.com/?target=http%3A//www.benet.com/awstats/awstats.pl%3Fconfig%3Dwww.benet.com)">

</head>

<body></body>

</html> //建立自动跳转html网页

[http://test.benet.com/awb.html](https://link.zhihu.com/?target=http%3A//test.benet.com/awb.html)

### 2.5 httpd服务访问控制限制

### 2.5.1客户端地址限制

#vim /usr/local/httpd/conf/httpd.conf

<Directory "/usr/local/awstats/wwwroot">

……

Order _deny,allow_ //定义控制顺序

 _deny from 192.168.37.130_ //设置拒绝地址

</Directory>

### 2.5.2 用户授权限制

1\. 创建用户认证数据库

# cd /usr/local/httpd/

# bin/htpasswd -c /usr/local/httpd/conf/.awspwd webadmin

//-c新建文件 不加则是新增用户

# cat /usr/local/httpd/conf/.awspwd

# bin/htpasswd /usr/local/httpd/conf/.awspwd webuser1

2\. 在主配置文件中添加用户授权配置

# vim /usr/local/httpd/conf/httpd.conf

<Directory "/usr/local/awstats/wwwroot">

……

AuthName "AWStats Directory"

AuthType _Basic_ //认证类型为基本认证

AuthUserFile _/usr/local/httpd/conf/.awspwd_ //认证文件路径

require _valid-user_ //允许访问的用户

</Directory

3\. 启服务，测试访问

# /usr/local/httpd/bin/apachectl restart

### 2.6构建虚拟主机

### 2.6.1基于域名的虚拟主机

#vim /etc/named.conf

options{

directory" _/var/named_ ";

};

zone " _[http://
benet.com](https://link.zhihu.com/?target=http%3A//benet.com)_"IN{

type _master_ ;

file " _benet.com.zone_ ";

allow-transfer{ _192.168.37.131_ ;};

};

zone " _37.168.192.in-addr.arpa_ "IN{

type _master_ ;

file " _192.168.37.arpa_ ";

allow-transfer{ _192.168.37.131_ ;};

};

zone " _[http://
accp.com](https://link.zhihu.com/?target=http%3A//accp.com)_"IN{

type _master_ ;

file " _accp.com.zone_ ";

};

# vim var/named/ _accp.com.zone_

$TTL 86400

@ SOA _accp.com._ _admin.accp.com._ (

2011030301 //更新序列号

4H //刷新时间

30M //重试延迟

12H //失效时间

1D //无效解析记录的生存周期

)

@ IN NS _[http://www.
benet.com](https://link.zhihu.com/?target=http%3A//www.benet.com)_.

 _test_ IN A _192.168.37.131_

建立测试网页

# mkdir -p _/var/www/html/benetcom_

# mkdir -p _/var/www/html/accpcom_

# echo " _<
h1>[http://www.benet.com](https://link.zhihu.com/?target=http%3A//www.benet.com)</h1>_"
> _/var/www/html/benetcom/index.html_

# echo " _<
h1>[http://www.accp.com](https://link.zhihu.com/?target=http%3A//www.accp.com)</h1>_"
> _/var/www/html/accpcom/index.html_

添加独立的虚拟主机配置文件

#vim /usr/local/httpd/conf/extra/httpd-vhosts.conf

<Directory " _/var/www/html_ ">

Order _allow,deny_ //定义访问控制顺序,先允许后拒绝，默认拒绝所有

Allow from all //允许所有人访问此区域

</Directory>

NameVirtualHost _192.168.37.131_ //添加虚拟主机名

<VirtualHost _192.168.37.131_ >

DocumentRoot _/var/www/html/benetcom_ //文档根目录

ServerName _[http://
test.benet.com](https://link.zhihu.com/?target=http%3A//test.benet.com)_ //网站名

ErrorLog logs _/www.benet.com.error_log_ //错误日志保存目录

Customlog logs _/www.benet.com.access_log common_ //访问日志保存目录

</VirtualHost>

<VirtualHost _192.168.37.131_ >

DocumentRoot _/var/www/html/accpcom_

ServerName _[http://
test.accp.com](https://link.zhihu.com/?target=http%3A//test.accp.com)_

ErrorLog logs _/www.benet.com.error_log_

Customlog logs _/www.benet.com.access_log common_

</VirtualHost>

在主配置文件中加独立配置文件

# vim /usr/local/httpd/conf/httpd.conf

Include conf/extra/httpd-vhosts.conf

### 2.6.2基于ip地址的虚拟主机

#ifconfig eth1 192.168.37.133/24

#ifconfig eth2 192.168.37.134/24 //分别为网卡配置ip地址

建立dns解析

#vim /etc/named.conf

zone " _[http://
test1.com](https://link.zhihu.com/?target=http%3A//test1.com)_" IN {

type _master_ ;

file " _test1.com.zone_ ";

};

zone " _[http://
test2.com](https://link.zhihu.com/?target=http%3A//test2.com)_" IN {

type _master_ ;

file " _test2.com.zone_ ";

};

#vim /var/named/test1.com.zone

$TTL 86400

@ SOA _test1.com._ _admin.test1.com._ (

2011030301

4H

30M

12H

1D

)

@ IN NS _[http://www.
benet.com](https://link.zhihu.com/?target=http%3A//www.benet.com)_.

 _www_ IN A _192.168.37.133_

#vim /var/named/test2.com.zone

$TTL 86400

@ SOA _test2.com._ _admin.test2.com._ (

2011030301

4H

30M

12H

1D

)

@ IN NS _www.benet.com._

 _www_ IN A 192.168.37.134

建立测试网页

# mkdir _/var/www/html/test1com_

# mkdir _/var/www/html/test2com_

# echo "<h1> _[http://www.
test1.com](https://link.zhihu.com/?target=http%3A//www.test1.com)_</h1>" >
_/var/www/html/test1com/index.html_

# echo "<h1> _[http://www.
test2.com](https://link.zhihu.com/?target=http%3A//www.test2.com)_</h1>" >
_/var/www/html/test2com/index.html_

添加独立的虚拟主机配置文件

#vim /usr/local/httpd/conf/extra/httpd-iphosts.conf

<Directory " _/var/www/html_ ">

Order allow,deny

Allow from all

</Directory>

<VirtualHost 192.168.37.133> //配置虚拟主机

DocumentRoot _/var/www/html/test1com_

ServerName _[http://www.
test1.com](https://link.zhihu.com/?target=http%3A//www.test1.com)_

ErrorLog logs _/www.test1.com.error_log_

Customlog logs _/www.test1.com.access_log common_

</VirtualHost>

<VirtualHost 192.168.37.134>

DocumentRoot _/var/www/test2/accpcom_

ServerName _[http://www.
test2.com](https://link.zhihu.com/?target=http%3A//www.test2.com)_

ErrorLog logs _/www.test2.com.error_log_

Customlog logs _/www.test2.com.access_log common_

</VirtualHost>

在主配置文件中加载独立配置文件

# vim /usr/local/httpd/conf/httpd.conf

Include conf/extra/httpd-iphosts.conf

## 一. nginx+tomcat负载均衡

### 3.1 拓补图

![v2-972f2be3d32d3f7456f885f232f73f44_hd.j](https://pic1.zhimg.com/80/v2-972f2be3d32d3f7456f885f232f73f44_hd.jpg)

### 3.2 服务环境

Server1、Server2以Tomcat作为应用服务器，需配置java环境

Server3以Nginx作为负载均衡器

三台服务器为Centos操作系统

### 3.3 所需软件安装包

1、jdk-7u65-linux-x64.gz

2、apache-tomcat-7.0.54.tar.gz

3、pcre-devel

4、zlib-devel

5、 openssl-devel

6、nginx-1.6.0.tar.gz

### 3.4 Tomcat配置

### 3.4.1 Tomcat主要目录及配置文件

bin/：存放启动和关闭Tomcat的脚本文件

conf/：存放服务器的各种全局配置文件，如server.xml、web.xml

lib/：存放Tomcat运行需要的库文件（JARS包文件）

logs/：存放Tomcat相关的日志文件

webapps/：Web应用的发布目录，默认把Web应用文件放于此目录

work/：Tomcat的工作目录，默认存放编译JSP文件生成的servlet类文件

temp/：存放Tomcat运行的临时文件

### 3.4.2主要配置文件说明

catalina.policy：权限控制配置文件

catalina.properties：Tomcat属性配置文件

context.xml：配置web应用部署时的物理目录与虚拟目录的映射等。

logging.properties：日志log相关配置文件

server.xml：主配置文件

tomcat-users.xml：配置Tomcat的管理用户(通过web来管理和查看tomca

运行情况以及部署的webApp)

web.xml：Web应用程序描述文件是Web应用程序的配置文件

### 3.4.3 tomcat主要配置步骤（需配置2台）

1、安装jdk，配置Java环境

2、安装配置tomcat

3、建立java的web测试站点

### 3.4.5 Tomcat配置命令

1.安装jdk，配置Java环境

#tar xf jdk-7u65-linux-x64.gz //解压jdk软件包

#mv jdk1.7.0_65/ _/usr/local/java_ //移动解压的jdk包到指定路径

#vim /etc/profile.d/java.sh //建立java.sh脚本

export J**A_HOME= _/usr/local/java_

export PATH=$PATH:$J**A_HOME/bin //在PATH环境变量中添加java根目录下的/bin子目录

#source /etc/profile.d/java.sh //执行java.sh脚本

#java -version //查看java版本

#rpm -qa | grep java //查看是否安装java

#rpm -e --nodeps tzdata-java-2012c-1.el6.noarch

2.安装配置tomcat

#tar zxvf apache-tomcat-7.0.54.tar.gz

#mv apache-tomcat-7.0.54 _/usr/local/tomcat7_

#/usr/local/tomcat7/bin/startup.sh //启动tomcat，重启要添加自动启动rc.local

#netstat -anpt | grep 8080 //tomcat默认运行端口为8080

登录
[http://192.168.1.1:8080](https://link.zhihu.com/?target=http%3A//192.168.1.1%3A8080)
测试Tomcat成功

3.建立java的web测试站点

#mkdir –pv _/web/webapp1_

#vim _/web/webapp1/index.jsp_

<%@ page language="java" import="java.util.*" pageEncoding="UTF-8"%>l

<html>

<head>

<title>JSP test1 page</title>

</head>

<body>

<% out.println("Welcom to test
site,[http://www.test1.com](https://link.zhihu.com/?target=http%3A//www.test1.com)");%>

<body>

</html>

#vim /usr/local/tomcat7/conf/server.xml

<Host name="localhost" appBase="webapps"

unpackWARs="true" autoDeploy="true">

<Context docBase=" _/web/webapp1_ " path="" loadable="false" >

</Context>

### 3.5 nginx服务器配置

### 3.5.1建立yum源

#mkdir _/media/cdrom_

#mount /dev/cdrom _/media/cdrom_

#vim /etc/yum.repos.d/local.repo

[local]

name= _RHEL DVD_

baseurl=file:/// _media/cdrom_

enabled=1

gpgcheck=0

#yum -y install pcre-devel zlib-devel openssl-devel //安装相关软件包

### 3.5.2解压并安装nginx

#groupadd www //创建组

#useradd -g www www -s /bin/false //创建用户

# tar zxf nginx-1.6.0.tar.gz

#cd nginx-1.6.0

#./configure --prefix= _/usr/local/nginx_ \--user= _www_ \--group= _www_

\--with-file-aio --with-http_stub_status_module --with-http_gzip_static_module

\--with-http_flv_module --with-http_ssl_module

#make && make install

### 3.5.3配置nginx.conf

#vim /usr/local/nginx/conf/nginx.conf

在http { }中添加

upstream _tomcat_server_ {

server _192.168.1.1:8080_ weight= _1_ ; //指定服务器及权重

server _192.168.1.2:8080_ weight= _1_ ;

}

location / {

root html;

index _index.html index.htm_ ;

proxy_pass
="[http://tomcat_server/](https://link.zhihu.com/?target=http%3A//tomcat_server/)">[http://tomcat_server](https://link.zhihu.com/?target=http%3A//tomcat_server);
//设置转发的服务器

}

# /usr/local/nginx/sbin/nginx -t //测试nginx配置文件

### 3.5.4启动nginx服务

#/usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf

#killall -s HUP nginx

# ps aux | grep nginx //查看nginx服务进程

# netstat -anpt | grep nginx //查看端口号及PID进程号

\-------------------------------------------end----------------------------------------
![v2-be7b3a919d240f369cef3d85db776fa7_hd.j](https://pic4.zhimg.com/80/v2-be7b3a919d240f369cef3d85db776fa7_hd.jpg)

  

  

 ****

信安干货，请关注专栏：<https://zhuanlan.zhihu.com/c_1142392164838404096>

