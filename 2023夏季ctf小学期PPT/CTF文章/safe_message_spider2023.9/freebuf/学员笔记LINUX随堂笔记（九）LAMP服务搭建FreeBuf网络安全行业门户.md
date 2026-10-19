**文章来源：知了堂冯老师原创**

![v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.j](https://pic4.zhimg.com/80/v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.jpg)

##  第10章 LAMP服务搭建  

## 一. LAMP简介

指一组通常一起使用的来运行动态网站或者服务器，是基于Linu小，Apache，mysql和php的开放资源网络开发平台，Linux是开放操作系统，Apache是网站服务器，mysql是带有基于网络管理附加工具的关系型数据库，PHP是流行的脚本语言（是采用Apache网站服务器+mysql数据库+PHP语言引擎开发的）

## 二. 实验环境

外网一台客户机搭建dns，apache,mysql,php和论坛，分担不同的角色，dns实现域名解析，apache实现网站代理，mysql实现用户管理和数据存储，php实现网页登录，最后论坛实现用户注册并登录，这样内网就可以访问外网搭建的论坛，确保了用户信息的安全性。

![v2-6b83100ec12dfa48f046b9ace0bd416d_hd.j](https://pic2.zhimg.com/80/v2-6b83100ec12dfa48f046b9ace0bd416d_hd.jpg)

搭建dns 搭建apache 搭建mysql 搭建php 搭建论坛

## 三. 实验安装包

1.Centos_6.5_Final或者red hat_6.5_Final

2.bind-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

3.bind-chroot-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

4.bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

5.bind-utils-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

6.httpd-2.2.17.tar.gz

7.cmake-2.8.6.tar.gz

8.mysql-5.5.22.tar.gz

9.libmcrypt-2.5.8.tar.gz

10.mhash-0.9.9.9.tar.gz

11.mcrypt-2.6.8.tar.gz

12.php-5.3.28.tar.gz

13.ZendGuardLoader-php-5.3-linux-glibc23-x86_64

14.phpMyAdmin-4.2.5-all-languages.tar.gz

15.Discuz_7.2_FULL_SC_UTF8.zip

## 四. 实验拓扑图

![v2-e11643152de4fc71e7d511ea62e35d36_hd.j](https://pic3.zhimg.com/80/v2-e11643152de4fc71e7d511ea62e35d36_hd.jpg)

## 五. 实验的步骤

1.配置本地yum源

2.安装bind包，搭建dns，实现域名解析

3.安装httpd包,搭建apache，提供网站代理

4.安装cmake和mysql包，实现用户管理和数据存储

5.安装libmcrypt，mhash，mcrypt，phpZendGuardLoader，phpMyAdmin，实现解析，并登陆

6.安装Discuz包，完成网站搭建并注册，实现个人服务和管理

## 六. 实验代码

### 6.1配yum源

#mkdir –p /media/cdrom //在media下创建一个cdrom目录，通畅情况下在media目录下，也可以在其它目录下

#mount /dev/cdrom /media/cdrom //挂载镜像

#vim /etc/yum. repos.d/local.repo //编写配置文档

[local] //源路径的文件名称

name=server //源的名称，可以是任意名称

baseurl=file:///media/cdrom //源路径

enabled=1 //使yum源生效

gpgcheck=0 //是否使用gpg验证RPM包的

否认性

#cd /etc/yum.repos.d //进入源目录下

#mkdir a //新建一个目录

#mv C* a //将/etc/yum.repos.d生成的四个Centos文件移动到a中

### 6.2搭建dns

### 6.2.1安装dns

#cd /media //进入media目录

#ls //查看是否有镜像

#cd CentOS_6.5_Final //进入镜像目录

#ls //查看镜像是否有安装包

#cd Packages/ //进入安装包目录

#ls //列出安装包

#rpm –ivh bind-utils-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm //安装与bind相应的包

#rpm –ivh bind-chroot-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

#rpm –ivh bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

#rpm –ivh bind-utils-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

### 6.2.2建立配置文件

#vim /etc/named.conf //进入配置文件

Options {

directory"/var/named"; //指定服务的工作目录，同时指定配置文件的路径

};

zone "[http://benet.com](https://link.zhihu.com/?target=http%3A//benet.com)"IN
{ //新建域

type master; //主服务器域类型

file "benet.com.zone"; //指定文件，是正向解析文件

};

### 6.2.3建立区域数据文件

#vim /var/named/ benet.com.zone. //编辑区域文件

$TTL 86400 //生存时间记录字段，它以秒为单位定义该资源记录中的信息存放在高速缓存中的时间长度

@ SOA benet.com. admin.benet.com. (

//SOA记录，特殊字符@，就是ORIGIN的意思，admin是指定这个区域的授权主机和管理者信箱。

2011030301 //更新序列号

4H //刷新时间

30M //重试延迟

12H //失效时间

1D //无效解析记录的生存周期

)

@ IN NS ns1.benet.com.

www IN A 192.168.1.2

ns1 IN A 192.168.1.2

### 6.2.4验证

#nslookup
[ns1.benet.com](https://link.zhihu.com/?target=http%3A//ns1.benet.com)

![v2-dcf7da0120e4b2f304b59b35cec22e72_hd.j](https://pic3.zhimg.com/80/v2-dcf7da0120e4b2f304b59b35cec22e72_hd.jpg)

### 6.3搭建Apache

1.下载源码软件包，卸载rpm安装的httpd软件包

#rpm -qa httpd //查看是否系统安装了httpd

#rpm -e httpd –nodeps //如果安装了httpd，就卸载httpd，包括它们的依赖关系

2.源码编译及安装

#tar zxf httpd-2.2.17.tar.gz -C /usr/src/ //将httpd包解压到/usr/src/目录下

#cd /usr/src/httpd-2.2.17//

#./configure

\--prefix=/usr/local/httpd

\--enable-so

\--enable-rewrite

\--enable-charset-lite

\--enable-cgi

//定义路径.启用动态加载模块支持启用网页地址重写.字符集支持

#make //进行源代码编译

#make install //因为源代码要写入系统，是源代码执行安装

3.优化执行路径

#ln -s /usr/local/httpd/bin/* /usr/local/bin //进行软连接

#ls -l /usr/local/bin/httpd /usr/local/bin/apachectl //查看http服务器包含的执行程序,
查看httpd服务器包含的网页文档根目录

#httpd -v = /usr/local/httpd/bin/httpd-v //用于查看优化后的程序版本

4.添加httpd系统服务

# cp /usr/local/httpd/bin/apachectl /etc/init.d/httpd
//将apachectl脚本复制为/etc/init.d/httpd

# vi /etc/init.d/httpd

#!/bin/bash

# chkconfig: 35 85 15

# description: Startup script for the Apache HTTP Server

# chkconfig --add httpd //添加http服务

# chkconfig --list httpd //c查看http的服务

5.web站点部署过程

确定网站名称、ip地址

确定网站名称及IP地址，并在DNS中设置

配置主配置文件

#vim /usr/local/httpd/conf/httpd.conf

ServerName
[http://test.benet.com](https://link.zhihu.com/?target=http%3A//test.benet.com)
//如有冲突可修改端口

#/usr/local/httpd/bin/apachectl –t //进行语法检查

启动httpd服务

#/etc/init.d/httpd start //启动httpd服务

#netstat -anpt |grep httpd //过滤httpd的服务端口

部署网页文档

#vim /usr/local/httpd/htdocs/index.html

客户机访问测试，查看日志

#tail /usr/local/httpd/logs/access_log

6.进入网页测试搭建的Apache服务器是否成功（再不修改网页文档的情况下，网页上会显示IT work，就表示Apache搭建成功）

![v2-ecfd866e2f0a3da954faf2273eba2bfe_hd.j](https://pic3.zhimg.com/80/v2-ecfd866e2f0a3da954faf2273eba2bfe_hd.jpg)

### 6.4安装mysql数据库

# rpm -q mysql-server mysql //查看系统是否安装了mysql服务

# yum -y remove mysql //如果安装了mysql，就卸载mysql

# yum -y install ncurses-devel

### 6.4.1解压cmake源码包编译安装

#cd /usr/src

# tar zxf cmake-2.8.6.tar.gz //解压到/usr/src目录下

# cd cmake-2.8.6 //进入到/usr/src下的cmake的解压文件

# ./configure //定义路径

# gmake && gmake install //进行源代码编译,执行源代码安装

### 6.4.2解压MySQL源码包

# tar zxf mysql-5.5.22.tar.gz -C /usr/src //解压mysql包到/usr/src下

# cd /usr/src/mysql-5.5.22/ //进入/usr/src目录下的mysql解压文件

# cmake -DCMAKE_INSTALL_PREFIX=/usr/local/mysql

-DSYSCONFDIR=/etc

-DDEFAULT_CHARSET=utf8

-DDEFAULT_COLLATION=utf8_general_ci

-DWITH_EXTRA_CHARSETS=all

//指定mysql的安装路径，指向mysql配置文件/etc/mysql,指定默认的字符集为utf8,设置默认排序规则（utf8_general_ci快速/utf8_unicode_ci准确），启用额外的字符集类型，默认为all

{}mysql cmake 的详细参数：

-DWITH_READLINE=1 启用readline库支持（提供可编辑的命令行）

-DWITH_SSL=system 启用ssl库支持（安全套接层）

-DWITH_ZLIB=system 启用libz库支持（zib、gzib相关）

-DWTIH_LIBWRAP=0 禁用libwrap库（实现了通用TCP包装的功能，为网络服务守护进程使用）

-DMYSQL_TCP_PORT=3306 指定TCP端口为3306

-DMYSQL_UNIX_ADDR=/tmp/mysqld.sock 指定mysql.sock路径

-DENABLED_LOCAL_INFILE=1 启用本地数据导入支持

-DEXTRA_CHARSETS=all 启用额外的字符集类型（默认为all）

-DDEFAULT_CHARSET=utf8 指定默认的字符集为utf8

-DDEFAULT_COLLATION=utf8_general_ci 设定默认排序规则（utf8_general_ci快速/utf8_unicode_ci准确）

-DWITH_EMBEDDED_SERVER=1 编译嵌入式服务器支持

-DMYSQL_USER=mysql 指定mysql用户(默认为mysql)

-DWITH_DEBUG=0 禁用debug（默认为禁用）

-DENABLE_PROFILING=0 禁用Profiling分析（默认为开启）

-DWITH_COMMENT='string' 一个关于编译环境的描述性注释

}

{mysql cmake常见参数解释：

-DCMAKE_INSTALL_PREFIX= 指向mysql安装目录

-DINSTALL_SBINDIR=sbin 指向可执行文件目录（prefix/sbin）

-DMYSQL_DATADIR=/var/lib/mysql 指向mysql数据文件目录（/var/lib/mysql）

-DSYSCONFDIR=/etc/mysql 指向mysql配置文件目录（/etc/mysql）

-DINSTALL_PLUGINDIR=lib/mysql/plugin 指向插件目录（prefix/lib/mysql/plugin）

-DINSTALL_MANDIR=share/man 指向man文档目录（prefix/share/man）

-DINSTALL_SHAREDIR=share 指向aclocal/mysql.m4安装目录（prefix/share）

-DINSTALL_LIBDIR=lib/mysql 指向对象代码库目录（prefix/lib/mysql）

-DINSTALL_INCLUDEDIR=include/mysql 指向头文件目录（prefix/include/mysql）

-DINSTALL_INFODIR=share/info 指向info文档存放目录（prefix/share/info）

}

# make //源代码编译

# make install //执行源代码编译

### 6.4.3建立配置文件

# rm -rf /etc/my.cnf //删除/etc/my.cnf/配置

# cp /usr/src/mysql-5.5.22/support-files/my-medium.cnf /etc/my.cnf

//将文件复制到/etc/my.cnf

### 6.4.4添加系统服务

# cp /usr/src/mysql-5.5.22/support-files/mysql.server /etc/rc.d/init.d/mysqld

//复制文件到/etc/rc.d/init.d/mysqld

# chmod +x /etc/rc.d/init.d/mysqld //可执行的权限

# chkconfig --add mysqld//添加mysqld服务

设置环境变量，在任何目录下都可以使用mysql命令

# echo "PATH=$PATH:/usr/local/mysql/bin" >> /etc/profile

//将环境变量下的文件输出到 /etc/profile

# . /etc/profile //执行文件

### 6.4.5初始化数据库

1.创建数据库用户

# groupadd mysql //添加组

# useradd -M -s /sbin/nologin mysql -g mysql //添加用户

2.对数据库目录进行权限设置

# chown -R mysql:mysql /usr/local/mysql

3.初始化数据

# /usr/local/mysql/scripts/mysql_install_db

\--user=mysql

\--basedir=/usr/local/mysql

\--datadir=/usr/local/mysql/data/

// 初始化mysql数据库，指定用户和数据库文件的存放位置

### 6.4.6启动mysql服务器

# service mysqld start //启动mysql

# /etc/init.d/mysqld status //查看mysql的状态

# netstat -anpt | grep mysqld //过滤mysql启用的端口

### 6.4.7更改mysql的root用户密码

# mysqladmin -u root -p password ‘123456’

### 6.4.8登录数据库测试

# mysql -u root –p //登录数据库

mysql> SHOW MASTER LOGS;

mysql> EXIT

![v2-01aa861386a110d42ead61ea0ca5b924_hd.j](https://pic1.zhimg.com/80/v2-01aa861386a110d42ead61ea0ca5b924_hd.jpg)

### 6.5安装ph#rpm -qa |grep "^php" //过滤系统中是否安装了php

### 6.5.1安装扩展工具库

#tar zxf libmcrypt-2.5.8.tar.gz -C /usr/src/ //解压libmcrypt

#cd /usr/src/libmcrypt-2.5.8/ //进入解压文件

#./configure //编译

#make && make install //源代码编译，可执行源代码编译

#ln -s /usr/locall/lib/libmcrypt.* /usr/lib/ //软衔接

#tar zxf mhash-0.9.9.9.tar.gz -C /usr/src/ //解压mhash

#cd /usr/src/mhash-0.9.9.9/ //进入解压文件

#./configure //编译

#make && make install //源代码编译，可执行源代码

#ln -s /usr/local/lib/libmhash* /usr/lib/ //软衔接

#tar zxf mcrypt-2.6.8.tar.gz -C /usr/src/ //解压mcrypt

#cd /usr/src/mcrypt-2.6.8 //进入解压文件

#./configure //编译

#export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

//设置环境变量，将编译的源代码输出代/usr/local/lib

#./configure //编译

#make && make install //源代码编译，可执行源代码

### 6.5.2编译安装PHP

#tar zxf php-5.3.28.tar.gz -C /usr/src //解压

#cd /usr/src/php-5.3.28 //进入解压文件

#./configure

\--prefix=/usr/local/php5

\--with-mcrypt

\--with-apxs2=/usr/local/httpd/bin/apxs

\--with-mysql=/usr/local/mysql

\--with-config-file-path=/usr/local/php5

\--enable-mbstring

//设置安装路径, 编译mcrypt加密支持, 编译共享的 Apache 2.0 模块, --with-mysql=/usr/local/mysql :
启用mysql支持, 指定配置文件php.ini地址, 启用支持多字节字符串

{编译参数解释：

\--prefix=/usr/local/php : 设置安装路径

\--with-apxs2=/usr/local/apache/bin/apxs : 编译共享的 Apache 2.0 模块

\--with-config-file-path=/etc : 指定配置文件php.ini地址

\--with-config-file-scan-dir=/etc/php.d : 指定额外的ini文件目录

\--with-openssl : 编译OpenSSL支持

\--with-zlib : 编译zlib支持

\--enable-bcmath : 启用BC风格精度数学函数

\--with-bz2 : BZip2支持

\--with-gd : GD支持

\--enable-gd-native-ttf : 启用TrueType字符串函数

\--with-gettext : 启用GNU gettext支持

\--with-mhash : mhash支持

\--enable-mbstring : 启用支持多字节字符串

\--with-mcrypt : 编译mcrypt加密支持

\--enable-zip : 启用zip 读/写支持

\--with-iconv=/usr/local/libiconv : iconv支持

\--with-curl : CRUL支持

\--enable-soap : SOAP支持

\--enable-sockets : SOCKETS支持

\--enable-ftp : FTP支持

\--with-mysql=/usr/local/mysql : 启用mysql支持

\--with-pdo-mysql=/usr/local/mysql : 启用pdo-mysql支持

\--without-pear : 不安装PEAR}

#make //源代码编译

#make install //执行源代码

### 6.5.3建立php.ini配置文件

#cp /usr/src/php-5.3.6/php.ini-development /usr/local/php5/php.ini

//将php.ini的配置文件复制

#vim /usr/local/php5/php.ini

default_charset = "utf-8” //设置默认字符集

file_uploads = On //允许PHP网页上传文件

upload_max_filesize = 2M //上传文件大小

max_file_uploads = 20 //每个HHTP最多允许上传数

post_max_size = 8M //每次通过表单post提交的数量

short_open_tag = On //允许识别PHP短语法标记

5.4添加ZendGuardLoader优化模块

#tar zxf ZendGuardLoader-php-5.3-linux-glibc23-i386.tar.gz -C /usr/src/ //解压

#cd /usr/src/ZendGuardLoader-php-5.3-linux-glibc23-i386/php-5.3.x/ //进入解压文件

#cp ZendGuardLoader.so /usr/local/php5/lib/php/ //将解压文件下的文件复制

#vim /usr/local/php5/php.ini //编辑优化模块的配置文档

zend_extension=/usr/local/php5/lib/php/ZendGuardLoader.so

zend_loader.enable=1

### 6.5.4修改httpd.conf配置调整

#vim /usr/local/httpd/conf/httpd.conf

LoadModule php5_module modules/libphp5.so

DirectoryIndex index.php index.html

AddType application/x-httpd-php .php

#/usr/local/httpd/bin/apachectl restart

### 6.5.5测试LAMP

#vim /usr/local/httpd/htdocs/test1.php

<?php

phpinfo( );

?>

网页访问[http://ns1.benet.com/test1.php](https://link.zhihu.com/?target=http%3A//ns1.benet.com/test1.php)

![v2-688eb1ae3ce103593e316482f9a4e22d_hd.j](https://pic2.zhimg.com/80/v2-688eb1ae3ce103593e316482f9a4e22d_hd.jpg)

### 测试PHP网页能否访问MySQL数据库

#vim /usr/local/httpd/htdocs/test2.php

<?php

$link=mysql_connect('localhost','root','123456');

if($kink) echo "恭喜你，数据库连接成功了！！";

mysql_close();

?>

网页访问[http://ns1.benet.com/test2.php](https://link.zhihu.com/?target=http%3A//ns1.benet.com/test2.php)

![v2-86836468b9b871f7e3e366338b93f98d_hd.j](https://pic2.zhimg.com/80/v2-86836468b9b871f7e3e366338b93f98d_hd.jpg)

### 6.6部署phpMyAdmin系统

### 6.6.1解包复制到网站目录

#mkdir -p /usr/local/httpd/htdocs/phpMyAdmin

#tar zxf phpMyAdmin-4.2.5-all-languages.tar.gz

#cp phpMyAdmin-4.2.5-all-languages/ /usr/local/httpd/htdocs/phpMyAdmin

### 6.6.2建立配置文件 config.inc.php

#cd /usr/local/httpd/htdocs/phpMyAdmin/

#cp config.sample.inc.php config.inc.php

# vi config.inc.php

$cfg['blowfish_secret'] = 'pwd@123';

网页测试：[http://ns1.benet.com/phpMyAdmin](https://link.zhihu.com/?target=http%3A//ns1.benet.com/phpMyAdmin)（用修改的密码登录）

![v2-1c104ee23d0e4731db96f0173b94c513_hd.j](https://pic4.zhimg.com/80/v2-1c104ee23d0e4731db96f0173b94c513_hd.jpg)

### 6.7建论坛

### 6.7.1创建新数据库，并授权

mysql> CREATE DATABASE bbsdb; //（登录进phpMyAdmin中创建数据库）

Query OK, 1 row affected (0.01 sec)

mysql> GRANT all ON bbsdb.* TO 'runbbs'@'localhost' IDENTIFIED BY ‘adm123';
//创建用户

Query OK, 0 rows affected (0.01 sec)

![v2-bb2db84e141b74260c552bf8ddbc9300_hd.j](https://pic1.zhimg.com/80/v2-bb2db84e141b74260c552bf8ddbc9300_hd.jpg)

### 6.7.2解压论坛包

[root@www ~]# unzip Discuz_7.2_FULL_SC_UTF8.zip -d DiscuzPkg //解压论坛包

[root@www ~]# ls -lh DiscuzPkg/ // 显示论坛包解压的文件

drwxr-xr-x 2 root root 4.0K 2010-01-06 readme

drwxr-xr-x 18 root root 4.0K 2010-01-06 upload

drwxr-xr-x 2 root root 4.0K 2010-01-06 utilities

### 6.7.3部署

mv DiscuzPkg/upload/ /usr/local/httpd/htdocs/bbs
//将解压论坛包目录下的upload文件移到/usr/local/httpd/htdocs/bbs下

### 6.7.4确认http运行用户

[root@www ~]# grep "^User" /usr/local/httpd/conf/httpd.conf //确定http运行用户

User daemon

[root@www ~]# cd /usr/local/httpd/htdocs/bbs

[root@www bbs]# chown -R daemon templates/ attachments/ forumdata/ //赋予权限

[root@www bbs]# chown -R daemon uc_client/data/cache/ config.inc.php //赋予权限

### 6.7.5确认读写权限

[root@www bbs]# ls -ld templates/ attachments/ forumdata/ //确认是否有读写权限

drwxr-xr-x 2 daemon root 4096 2010-01-06 attachments/

drwxr-xr-x 9 daemon root 4096 2010-01-06 forumdata/

drwxr-xr-x 11 daemon root 4096 2010-01-06 templates/

（登录网站并注册）

![v2-4a346dbee69bb4102ee4b053b1cd584d_hd.j](https://pic2.zhimg.com/80/v2-4a346dbee69bb4102ee4b053b1cd584d_hd.jpg)

### 6.7.6安装后转移

[root@www ~]# cd /usr/local/httpd/htdocs/bbs //进入目录

[root@www bbs]# mv install/ install.lock //usr/local/httpd/htdocs/bbs/

目录下的文件

[root@www bbs]# chmod 600 install.lock/ //赋予权限

[root@www bbs]# ls -ld install.lock/ //确认是否赋予了权限

\-------------------------------------------end-----------------------------------------------
![v2-be7b3a919d240f369cef3d85db776fa7_hd.j](https://pic4.zhimg.com/80/v2-be7b3a919d240f369cef3d85db776fa7_hd.jpg)

  

  

 ****

信安干货，请关注专栏：<https://zhuanlan.zhihu.com/c_1142392164838404096>

