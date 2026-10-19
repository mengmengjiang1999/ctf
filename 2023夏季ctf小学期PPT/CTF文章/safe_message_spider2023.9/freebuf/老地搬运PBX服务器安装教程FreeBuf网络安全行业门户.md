  

0x0 介绍

这里主要讲的是(基于LINUX) ippbx 或者叫 sippbx 这类服务器主要用于呼叫中心 网络电话服务器 内线电话等。

尽管现在很多呼叫中心产品有自己独立盒子系统，这里讲的是用一个PC或普通服务器实现PBX服务器搭建。

硬件需要运营商的专用线路 以及中继器 还有语音卡

语音卡这边 用的 openVOX 硬件还需要单独装驱动的。

![TIM截图20181114134518.png](https://image.3001.net/images/20181114/1542174476_5bebb70c61cf0.png!small)  

0x1 **主要步骤**

系统环境CENTOS 6.8 64

  

IPPBX 的软件部分 主要是 apache+mysql+asterisk 以及C 和各种支持库等等

1.安装gcc  
2.gcc-c++  
3.安装mysql  
4.mysql-server  
5.mysql-devel  
6.试启动mysql  
7.安装 libpri  
8.安装 asterisk 需要的包：bison，bison-devel，ncurses，ncurses-devel  
9.安装 asterirk-addons  
10.asterisk -rvvvvv  
11.DB给权限，开用户  
12.修改/etc/asterisk/cdr_mysql.conf  
hostname=数据库ip  
user=***  
password=***  
sock=/**/***/mysql.sock  
asterisk -rvvvvvv  
cdr mysql status 看是否连上数据库  
13.安装 http  
mkdir /usr/local/apache 创建一个目录  
chown -R root.root *  
chmod 755 *  
./configure -prefix=/usr/local/apache  
14.安装 DBI-1.620  
perl Makefile.PL  
看见Look good,writing xxx 代表ok  
15.安装 DBD-mysql  
perl Makefile.PL  
看见mysql_config,look good代表ok

安装php  
mkdir /usr/local/php  
./configure --prefix=/usr/local/php --with-apxs2=/usr/local/apache/bin/apxs
--with-mysql=/var/lib/mysql/ --with-libxml-dir=/usr/include/libxml2 --enable-sockets --enable-mbstring  
cp php.ini-dist /usr/local/php/lib/php.ini  
修改register_globals = Off 改成On

配置 httpd.conf 让apache支持PHP  
# vi /usr/local/apache/conf/httpd.conf  
找到 AddType application/x-gzip .gz .tgz 在其下添加如下内容  
AddType application/x-httpd-php .php  
AddType application/x-httpd-php-source .phps

找到# LoadModule foo_module modules/mod_foo.so  
添加LoadModule php5_module modules/libphp5.so

  

  

0x2 测试

配置参看 asterisk 教程  

软电话测试个人推荐 yate-4.2

