接上文

## 第11章 LNMP服务搭建

## 一．lnmp

即Nginx网站服务 Nginx是俄罗斯人编写的十分轻量级的HTTP服务器,Nginx，它的发音为“engine
X”，是一个高性能的HTTP和反向代理服务器，同时也是一个IMAP/POP3/SMTP 代理服务器。

优点：一款高性能、轻量级Web服务软件，稳定性高，系统资源消耗低,对HTTP并发连接的处理能力高，单台物理服务器可支持30 000～50 000个并发请求。

## 二．安装环境

### 2.1在虚拟机下安装RHEL_6.5

Rhel-server-6.5-x86_64-ded

### 2.2安装DNS

bind-9.8.2-0.17.rc.el6_4.6.x86_64.rpm

bind-util-9.8.2-0.17.rc.el6_4.6x86_64.rpm

bind-chroot-9.8.2-0.17rc1.el6_4.6_x86_64.rpm

bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

### 2.3安装MySQL

ncurses-devel-5.7-3.2009.2.8.el8.x86.rpm

cmake：cmake-2.8.6.tar.gz

mysql:mysal-5.5.22.tar.gz

### 2.4安装nginx

nginx:nginx-1.6.0.tar.gz

### 2.5安装PHP

libxml2-devel

libjpeg-devel

libpng-devel

php:php-5.3.28.tar.gz

ZendGuarLoader:ZendGuardLoader-php-5.3-linux-glibc23-x86_64.tar.gz

### 2.6视频点播系统

SKYUC:SKYUC.v3.4.2.SOURCE

三．拓扑图

![v2-d6f9be1d3105d9e8e3363b4639968478_hd.j](https://pic1.zhimg.com/80/v2-d6f9be1d3105d9e8e3363b4639968478_hd.jpg)

## 四．实验代码

### 4.1搭建DNS

导入RED HAT镜像文件

### 4.1.1安装DNS

#cd /media/RHEL_6.5\ X86_64\ Disc\ 1/Packages/ //进入镜像文件的Packages

//安装与bind相应的包

#rpm -ivh bind-9.8.2-0.17.rc.el6_4.6.x86_64.rpm

#rpm -ivh bind-util-9.8.2-0.17.rc.el6_4.6x86_64.rpm

#rpm-ivh bind-chroot-9.8.2-0.17rc1.el6_4.6_x86_64.rpm

#rpm -ivh bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

### 4.1.2建立配置文件

#vim /etc/named.conf //进入配置文件

options {

Directory “/var/named”;

//指定服务的工作目录，同时指定配置文件的路径

};

zone “benet.com” IN {
//新建域[http://benet.com](https://link.zhihu.com/?target=http%3A//benet.com)

type master; //主服务器域类型

file “benet.com.zone”;

//指定文件,是正向解析文件

}；

### 4.1.3建立区域数据文件

#vim /var/named/benet.com.zone

$TTL 86400 //生存时间记录字段，它以秒为单位

@ SOA benet.com. admin.benet.com. ( //SOA记录，特殊字符@， 是 ORIGIN admin 授权主机和管理者信箱。

2011030301 //更新序列号

4H //刷新时间

30M //重试延迟

12H //失效时间

1D //无效解析记录的生存周期

)

@ IN NS test.benet.com.

test IN A 192.168.1.61

www IN A 192.168.1.61

### 4.1.4验证

#service named restart //重启named

#nslookup
[http://test.benet.com](https://link.zhihu.com/?target=http%3A//test.benet.com)
//域名解析

### 4.2搭建MYSQL

### 4.2.1安装ncurses

# rpm -qa mysql-server mysql

//查看系统是否安装了mysql服务

# yum -y remove mysql //如果安装了mysql，就卸载mysql

#cd /media/RHEL_6.5\ X86_64\ Disc\ 1/Packages/ //进入镜像文件的Packages

#rpm -ivh ncurses-devel-5.7-3.2009.2.8.el8.x86..rpm //安装ncurse

### 4.2.2上传cmake源码包编译安装

# tar zxf cmake-2.8.6.tar.gz //解压

# cd cmake-2.8.6 //进入cmake

# ./configure //定义路径

# gmake && gmake install //进行源代码编译,行源代码安装

### 4.2.3解压MySQL源码包

#tar zxf mysql-5.5.22.tar.gz -C /usr/src/ //解压mysql到/usr/src目录下

#cd /usr/src/mysql-5.5.22/ //进入/usr/src/mysql-5.5.22

#cmake //指定mysql的安装路径，指向

-DCMAKE_INSTALL_PREFIX=/usr/local/mysql // mysql配置文件

-DDEFAULT_CHARSET=utf8 //目录/etc/mysql,指定默认的字符集

-DDEFAULT_COLLATION=utf8_general_ci //为utf8,设置默认排-DWITH_EXTRA_CHARSETS=all

# make && make install //进行源代码编译,执行源代码安装

### 4.2.4优化调整，建立配置文件

# rm -rf /etc/my.cnf //删除/etc/my.cnf/的配置

# cp

/usr/src/mysql-5.5.22/support-files/my-medium.cnf /etc/my.cnf

//将文件复制到/etc/my.cnf添加系统服务

# cp /usr/src/mysql-5.5.22/support-files/mysql.server

/etc/rc.d/init.d/mysqld //复制

# chmod +x /etc/rc.d/init.d/mysqld //给可执行的权限

# chkconfig --add mysqld //添加mysqld服务

### 4.2.5设置环境变量，在任何目录下都可以使用mysql命令

# echo "PATH=$PATH:/usr/local/mysql/bin" >> /etc/profile //将环境变量下的文件输出到
/etc/profile

### 4.2.6初始化数据库，创建数据库用户

# groupadd mysql //添加组

# useradd -M -s /sbin/nologin mysql -g mysql //添加用户

# chown -R mysql:mysql /usr/local/mysql //对数据库目录进行权限设置初始化数据

#/usr/local/mysql/scripts/mysql_install_db

\--user=mysql

\--basedir=/usr/local/mysql --datadir=/usr/local/mysql/data/

# service mysqld start //启动mysql服务器

# /etc/init.d/mysqld status //查看mysql的状态

# netstat -anpt | grep mysqld //过滤mysql启用的端口

# mysqladmin -u root -p password 123456

//更改mysql的root用户密码

### 4.2.7.登录数据库测试

# mysql -u root -p //登录用户并输入密码

mysql> SHOW MASTER LOGS;

//查看当前数据库服务的日志文件信息

mysql> EXIT //退出

### 4.3搭建NGINX

#vi /etc/yum.repos.d/local.repo //指定仓库位置，并编辑

[local]

name=123

baseurl=file:///media/cdrom

enabled=1

gpgcheck=0

#cd /etc/yum.repos.d //进入此目录

#mkdir /li //创建文件夹

#mv C* /li //移动所有以C开头的文件到/li下面

### I.安装支持软件，Nginx的配置及运行需要pcre、zlib等软件包的支持

# yum -y install pcre-devel zlib-devel

//用yum安装pcre zlib

# useradd -M -s /sbin/nologin nginx //建立用户账户

### II编译安装启用http_stub_status_module模块以支持状态统计

#tar zxf nginx-1.6.0.tar.gz //解压Nginx

#cd nginx-1.6.0 //进入此目录

#./configure

\--prefix=/usr/local/nginx

\--user=nginx

\--group=nginx

\--with-http_stub_status_module //定义路径

#make && make install //源代码编译，并执行源代码编译

#ln -s /usr/local/nginx/sbin/nginx/usr/local/sbin/

//软连接

#ln -l /usr/local/sbin/nginx //访问文件

#nginx -t //检查配置文件

#nginx //启动

#nginx -anpt | grep nginx //停止nginx

使用elink浏览器

#yum -y install elink //已经安装

#elink [http://localhost](https://link.zhihu.com/?target=http%3A//localhost/)

#kill -s HUP nginx //重载配置

#kill -s QUIT nginx //停止服务

### III.nginx 服务脚本

#vim /etc/init.d/nginx //编辑文件

#！/bin/bash

#chkconfig: - 99 20

#description: Nginx Service Control Script

PROG="/usr/local/nginx/sbin/nginx"

PIDF="/usr/local/nginx/logs/nginx.pid"

case "$1" in

start)

$PROG

;;

stop)

kill -s QUIT $(cat $PIDF)

;;

restart)

kill -s QUIT $(cat $PIDF)

$PROG

;;

reload)

kill -s HUP $(cat $PIDF)

;;

*)

echo "Usage: $0 { start | stop | restart | reload }"

exit 1

esac

exit 0

#chmod +x /etc/init.d/nginx //给文件执行权限

#chkconfig --add nginx //启动nginx服务

### IV.准备虚拟网站测试文件

#mkdir -p /var/www/benet //创建文件夹

#echo
"<h1>[http://Ng.BENET.COM](https://link.zhihu.com/?target=http%3A//Ng.BENET.COM)<h1>"
> /var/www/benet/index.html //输出内容到网页

#vim /usr/local/nginx/conf/nginx.conf //调整nginx.conf配置文件

server {

listen 80; //端口

server_name ng.accp.com; //主机域名

charset ‘utf-8’;

access_log logs/benet.access.log;

location / {

root /var/www/benet; //根

index index.html test .php; //PHP所在的路径

}

}

#service nginx restart //重启nginx

### V.测试

[http://ng.benet.com](https://link.zhihu.com/?target=http%3A//ng.benet.com)

### 4.4搭建PHP

### I.安装PHP

#rpm -qa | grep “^php” //查看是否已安装PHP

#yum -y install gd libxml2-devel

libjpeg-devel libpng-devel //yum安装libxml2 libjpeg libpng

# tar zxf php-5.3.28.tar.gz -C /usr/src/ //解压到/usr/src

# cd /usr/src/php-5.3.28/ //进入目录

# ./config

\--prefix=/usr/local/php5

\--with-gd --with-zlib --with-mysql=/usr/lcoal/mysql --with-config-file-path=/usr/local/php5 --enable-mbstring --enable-fpm --with-jpeg-dir=/usr/lib
//定义路径

#make && make install //编译并安装

#cp /usr/src/php-5.3.28/php.ini-development /usr/local/php5/php.ini //复制

#vim /usr/local/php5/php.ini //修改文档

default_charset = "utf-8"

file_uploads = On

upload_max_filesize = 2M

max_file_uploads = 20

post_max_size = 8M

short_open_tag = On

# ln -s /usr/local/php5/bin/* /usr/local/bin/ //软连接

# ln -s /usr/local/php5/sbin/* /usr/local/sbin/ //软连接

### II安装ZendGuardLoader优化模块

1.#tar

zxf

ZendGuardLoader-php-5.3-linux-glibc23-x86_64.tar.gz

-C /usr/src/ //解压到usr/src

#cd /usr/src/ZendGuardLoader-php-5.3-linux-glibc23-x86_64/php-5.3.x/ //进入PHP目录

# cp ZendGuardLoader.so /usr/local/php5/lib/php/

//复制到/usr/local/php5/lib/php/

修改php.ini配置文件，添加加载及启用ZendGuardLoader.so模块的配置语句

# vim /usr/local/php5/php.ini //增加路径

zend_extension=

/usr/local/php5/lib/php/ZendGuardLoader.so //指定路径

zend_loader.enable=1 //

# vim /var/www/benet/test.php //编辑php

<?php

$link=mysql_connect('localhost','root','123456');

if($link) echo "<h1>恭喜你，数据库连接成功啦！</h1>";

mysql_close();

?>

~

# server nginx restart //重启Nginx

### 5.5部署PHP视频点播系统

### I下载并上传天空网络系统程序包SKYUC.v3.4.2.SOURCE.zip

#rpm -qa unzip //查看zip

#yum -y install unzip //yum安装

#cd SKYUC.v3.4.2.SOURCE

#mv wwwroot /var/www/benet//skyuc

#cd /var/www/benet/skuc/

#chown -R php:php admincp /data/ templates/ upload

### II创建数据库

#mysql -u root -p

mysql> create DATABASE skyucdb;

mysql>GRANT all ON skyucdb.* TO runskyuc@locaohost INDENTIFIED BY 123456

## 五．测试

[http://ng.benet.com/install/index.php](https://link.zhihu.com/?target=http%3A//ng.benet.com/install/index.php)

\------------------------------------------------end--------------------------------------------
LINUX笔记更新这么久了，大家还有什么想看的吗？可以再评论里告诉我们哦~

 ****

信安干货，请关注专栏：<https://zhuanlan.zhihu.com/c_1142392164838404096>

