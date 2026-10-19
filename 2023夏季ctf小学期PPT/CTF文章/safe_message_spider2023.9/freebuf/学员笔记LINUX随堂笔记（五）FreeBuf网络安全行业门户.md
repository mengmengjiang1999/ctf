文章来源：知了堂冯老师  

![v2-c4c958a3e1dfbc0814708d05a49ef731_hd
\(1\).jpg](https://image.3001.net/images/20191113/1573636231_5dcbc8875a08e.jpg!small)

  

周一啦，是不是又在后悔昨晚熬了夜？没事！今天小编满血复活为大家继续更新咱们的学霸笔记！

![v2-faea99b668716167940cbf82a0c4b276_hd.j](https://pic3.zhimg.com/80/v2-faea99b668716167940cbf82a0c4b276_hd.jpg)

## 第6章 网络服务

## 一. 网络服务（基础命令）

1.查看网络接口信息：ifconfig

ifconfig 网络接口名称

2.查看主机名：hostname

hostname 主机名（修改主机名）

3.查看路由条目

router [-n]（-n：将路由记录中的地址信息显示为数字形式）

4.查看网络连接情况：netstat

netstat+选项

-a：显示所有活动连接

-n：以数字信息形式显示

-p：显示进程信息

-t：查看TCP协议相关信息

-u：查看UDP协议相关信息

5.测试网络连接

ping：+选项+目标主机

traceroute:测试从当前主机到目的主机之间经过的网络节点

traceroute 目标主机地址

6.域名解析:nslookup

nslookup 目标主机地址[dns服务器地址]

7.设置网络接口参数

ifconfig 接口名 ip地址 [netmask 子网掩码]

ifconfig 网络接口 IP地址[/掩码长度]

禁用或者重新激活网卡

ifconfig 网络接口 up

ifconfig 网络接口 down

设置虚拟网络接口

Ifconfig 接口名：序号 IP地址

8.设置路由记录

删除路由表中的默认网关记录： route del default gw ip地址

向路由表中添加默认网关记录： route add default gw ip地址

添加到指定网段的路由记录： route add –net 网络地址 gw IP地址

删除到指定网段的路由记录： route del –net 网段地址

9.网络接口配置文件

/etc/sysconfig/network-scripts/目录下：

ifcfg-eth0:第一块以太网的配置文件

ifcfg-eth1:第二块以太网的配置文件

service network restart：重启网络服务

/etc/sysconfig/network文件：保存全局网络设置，包括主机名信息

Hostname=[http://www.benet.com](https://link.zhihu.com/?target=http%3A//www.benet.com)

/etc/resolv.conf文件：保存本机需要使用的dns服务器的ip地址

/etc/host文件：保存主机名与ip地址的映射地址

## 二. DHCP服务器

![v2-3c40829a650f96ab57be6975d78f8601_hd.j](https://pic2.zhimg.com/80/v2-3c40829a650f96ab57be6975d78f8601_hd.jpg)

2.1 dhcp搭建的流程图

![v2-0fbffb339f2c340e05bd4b7afab42942_hd.j](https://pic3.zhimg.com/80/v2-0fbffb339f2c340e05bd4b7afab42942_hd.jpg)

### 2.2 dhcp软件包的主要文件

主要配置文件：/etc/dhcpd.conf

执行程序:/usr/sbin/dhcp、/usr/sbin/dhcrelay

服务脚本:/etc/init.d/dhcpd、/etc/init.d/dhcrelay

执行参数配置:/etc/sysconfig/dhcpd

DHCP中继配置:/etc/syscnfig/dhcrelay

### 2.3查看、安装dhcp服务器

#rpm –qa | grep dhcp*

#rpm -ivh /media/Packages/dhcp-4.1.1-38.P1.el6.x86_64.rpm

### 2.4建立配置文件

#vi /etc/dhcp/dhcp.conf

ddns-update-style none; //不要更新 DDNS 的设定

default-lease-time 21600; //预设租约为 3 天

max-lease-time 43200; //最大租约为 6 天

option routers 192.168.1.1; //预设路由

option domain-name-servers 192.168.1.25;

subnet 192.168.1.0 netmask 255.255.255.0 {

range 192.168.1.26 192.168.1.100; //分配的 IP 范围

option subnet-mask 255.255.255.0; //分配的ip地址子网掩

绑定特定的ip地址

host vbird-inside {

hardware ethernet 00:40:95:30:43:B4; //客户端网卡 MAC

fixed-address 192.168.1.27; //给予固定的 IP

}

#service dhcpd start //启动dhcp

#netstat -anpu |grep ":67" //检查UDP协议的67端口是否在监听

#less /var/lib/dhcpd/dhcpd.leases //查看DHCP分配情

#dhclient -d eth0

#chkconfig --level 35 dhcpd on

#chkconfig --list dhcpd

#ntpdate -u ntp.api.bz //时间同步

#service dhcpd start //启动dhcpd服务

查看租约文件/var/lib/dhcpd/dhcpd.lease

## 三. 文件共享服务器（samba）

3.1 samba搭建的流程图

![v2-0d82a7c4423909e32c687f04690be5e3_hd.j](https://pic4.zhimg.com/80/v2-0d82a7c4423909e32c687f04690be5e3_hd.jpg)

3.2安装samba服务器

# rpm -qa |grep “^samba” //查询已安装软件包

# rpm -ivh samba-3.6.9-164.el6.x86_64.rpm //安装samba服务器

# service smb start //启动smb服务

# mkconfig --level 35 smb on //设置自动启动

### 3.3设置可匿名访问的共享

1、修改默认安全级别为share

# vi /etc/samba/smb.conf

[global]

workgroup = WORKGROUP

security = share

2、添加共享目录配置

[share]

comment = share for a

path = /media/a //在media文件夹下建共享文件

public = yes //public=guest ok，设为yes允许匿名用户访问

read only = yes

# service smb reload //重启samba服务器

### 3.4建立用户验证的共享

1、建立用户数据库

# useradd jiang

# pdbedit -a -u jiang //添加指定共享用户

# pdbedit -x -u jiang //删除指定共享用户 -vL 查看

# useradd haha

# pdbedit -a -u haha

# mkdir /media/a //建立本地测试目录

# chmod 777 /media/a

2、修改默认安全级别

# vi /etc/samba/smb.conf

[global]

workgroup = WORKGROUP

security = user

3、添加共享目录配置

[tools]

comment = You can get software tools from here.

path = /opt/mytools

public = no

read only = yes

valid users = jiang,haha

write list = jiang

directory mask = 7000

createmask = 7000

# service smb reload //重启samba服务器

# testparm //配置文件检查工具

### 3.5配置用户映射及访问地址限制

1、配置文件修改

#cat /etc/samba/smbusers //查看共享账号的映射文件

#useradd jiang

#pdbedit jiang //设置共享用户

#vi /etc/samba/smbusers //1、设置别名

jiang= J

#vi /etc/samba/smb.conf //2、启用映射账号文件

[global]

username map = /etc/samba/smbusers

# service smb reload //重启samba服务

2、访问地址限制

# vi /etc/samba/smb.conf

[global]

hosts allow = 192.168.1.27 //仅允许

hosts deny =192.168.1.25 //仅拒绝的IP地址

### 3.6 Linux客户端访问

# smbclient -L 192.168.1.25 //查询目标主机匿名共享资源列表

# smbclient -U jiang //192.168.1.25 /a //登录samba进行上传下载

smb:\>

！:执行本地路径

ls:显示文件列表

get:下载单个文件

put:上传单个文件

mget:批量下载文件

mput:批量上传文件

mkdir:建立目录

rmdir:删除目录rm:删除文件

mount挂载共享文件夹

# mkdir /media/b

## 四. DNS服务器

4.1 DNS搭建的流程图

![v2-fc772b59f502213ee601f206e9402b85_hd.j](https://pic2.zhimg.com/80/v2-fc772b59f502213ee601f206e9402b85_hd.jpg)

### 4.2查询及安装DNS服务器

1、查询是否安装DNS #rpm -qa |grep "^bind"

2、安装DNS

安装包：

bind-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

bind-chroot-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

bind-utils-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

### 4.3构建缓存域名服务器

1、建立主配置文件

#vim /var/named/chroot/etc/named.conf

options {

listen-on port 53 { 192.168.37.130; }; //监听的端口

directory "/var/named"; //指定主配置文件的路径

dump-file "/var/named/data/cache_dump.db";

statistics-file "/var/named/data/named_stats.txt";

memstatistics-file "/var/named/data/named_mem_stats.txt";

query-source port 53; （指定客户端在提交DNS查询必须使用的源端口）

allow-query { 192.168.1.0/24; };

recursion yes;

# forwarders{192.168.1.25;};

};

zone "." IN {

type hint;

file "[http://named.ca](https://link.zhihu.com/?target=http%3A//named.ca)";

}; //可省略

2、启动服务并查看

#service named start

#netstart -anpt |grep named

### 4.4构建主、从域名服务器

1、确认本机的网络地址、主机映射、默认DNS服务器地址

#vim /etc/hosts

#vim /etc/resolv.conf

2、构建主域名服务器

（1）、建立主配置文件

#vim /var/named/chroot/etc/named.conf

options{

directory"/var/named"; //主配置文件的路径

};

zone "[http://haha.com](https://link.zhihu.com/?target=http%3A//haha.com)"IN{

type master;

file "haha.com.zone";

allow-transfer{192.168.1.26;};（从服务器的IP地址）

}; //配置的区域文件

（2）、建立正向区域数据文件

#cd /var/named/chroot/var/named/

#vim haha.com.zone

$TTL 86400

@ SOA haha.com. admin.haha.com. (

2017020305 更新序列号

4H 刷新时间

30M 重试延迟

12H 失效时间

1D 无效解析记录的生存周期

)

@ IN NS a.haha.com.

a IN A 192.168.1.25

3、构建从域名服务器

（1）、

新安装一台Linux服务器，关闭iptables，关闭SELinux，更改主机名称

更改IP地址，更改dns （主域名服务器的ip）

（2）、安装包

bind-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

bind-chroot-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

bind-utils-9.8.2-0.17.rc1.el6_4.6.x86_64.rpm

（3）、建立主配置文件

#vim /var/named/chroot/etc/named.conf

options {

directory "/var/named";

};

zone "[http://haha.com](https://link.zhihu.com/?target=http%3A//haha.com)" IN
{

type slave;

masters { 192.168.1.25; }; //主域名服务器的IP地址

file "slaves/haha.com.zone";

};

4、实验结果：

启动服务，查看是否下载成功

#ls -lh /var/named/chroot/var/named/slaves/

然后关闭主域名服务器，查看是否能够解析

## 五. FTP文件传输服务

### 5.1 FTP搭建的流程图

![v2-7baffb5f4569f80ecbf25e8c19c01a64_hd.j](https://pic1.zhimg.com/80/v2-7baffb5f4569f80ecbf25e8c19c01a64_hd.jpg)

5.2查询及安装FTP

1、查询vsftpd是否安装

#rpm –qa | grep “vsftpd”

2、安装vsftpd

#rpm -ivh /media/cdrom/Packages/vsftpd-2.2.2-11.el6_4.1.x86_64.rpm

3、安装ftp

rpm -ivh ftp-0.17-54.el6.x86_64.rpm

### 5.3构建可匿名上传的FTP服务器

1、准备匿名FTP访问的目录，并给予写入权限

#chown ftp /var/ftp/pub/ //修改目录属主

#ls -ld /var/ftp/pub/ //d显示目录的本身属性，不显示内部）

anonymous_enable=YES //允许匿名用户访问

local_enable=NO //不需要启用本地用户

write_enable=YES //开发服务器的写权限

anon_umask=022 //匿名用户上传数据的权限掩码

anon_upload_enable=YES //允许匿名上传文件

anon_mkdir_write_enable=YES //允许匿名用户创建目录

anon_other_write_enable=YES //允许匿名删除

#service vsftpd start //重新启动服务

2、登录：ftp 192.168.1.25/

3、匿名用户：anonymous 或 ftp

### 5.4构建用户验证的FTP服务

# vi /etc/vsftpd/vsftpd.conf

anonymous_enable=NO //禁止匿名用户访问

local_enable=YES

write_enable=YES //开发服务器的写权限

chroot_local_user=YES //本地用户禁锢在宿主目录中

# service vsftpd reload

# useradd test //新建用户

# passwd 123456

使用user_list用户列表文件

# useradd jiang haha

（为这两个用户配置密码后登录）

# vim /etc/vsftpd/user_list 清空添加两个用户

# vim /etc/vsftpd/vsftpd.conf

userlist_enable=YES

userlist_deny=NO //改为yes再测试

# service vsftpd reload //重启vsftpd服务

### 5.5基于虚拟用户的FTP服务

1、查询db4-utils软件包是否安装，提供db_load工具

# rpm -q db4-utils

安装db4-utils

#rpm -ivh db4-utils-4.7.25-18.el6_4.x86_64.rpm

2、创建用户/密码列表文件

# vim /etc/vsftpd/vusers.list

ftp1

123

ftp2

123

3、创建Berkeley DB格式的数据文件

# cd /etc/vsftpd/

# db_load -T -t hash -f vusers.list vusers.db

//-T允许其他程序转换DB数据库 -t hash指定读取数据基本方法

# file vusers.db

# chmod 600 /etc/vsftpd/vusers.*

# ls -lh /etc/vsftpd/vusers.*

4、添加虚拟用户的映射账号及创建FTP根目录

# useradd -d /var/ftproot -s /sbin/nologin test

# chmod 755 /var/ftproot

5、为虚拟用户建立PAM认证文件

# vim /etc/pam.d/vsftpd.vu

#%PAM-1.0

auth required pam_userdb.so db=/etc/vsftpd/vusers

account required pam_userdb.so db=/etc/vsftpd/vusers

6、修改主配置文件

# vim /etc/vsftpd/vsftpd.conf

local_enable=YES //映射本地用户必须开启

write_enable=YES //上传写入

anon_umask=022

guest_enable=YES //启用用户映射功能

guest_username=testftp //制定映射的系统用户名

pam_service_name=vsftpd.vu //指定新的PAM认证文件

7、建立独立的虚拟用户配置文件，设置不同的权限

（1）、主配置文件添加

#vim /etc/vsftpd/vsftpd.conf

user_config_dir=/etc/vsftpd/vusers_dir //独立配置文件路径

（2）、创建配置文件夹及虚拟用户配置文件

#mkdir /etc/vsftpd/vusers_dir/

#cd /etc/vsftpd/vusers_dir/

#vi ftp1

anon_upload_enable=YES

anon_mkdir_write_enable=YES

#touch ftp2

#service vsftpd reload

8、测试

虚拟用户登录日志 /var/log/secure

只是权限不同

一定要注释掉userlist_enable=NO

chkconfig --level 35 vsftpd //vsftp服务设置为自动启动

\-------------------------------------------end------------------------------------------
今天也给自己点个赞吧！

![v2-be7b3a919d240f369cef3d85db776fa7_hd.j](https://pic4.zhimg.com/80/v2-be7b3a919d240f369cef3d85db776fa7_hd.jpg)

  

  

