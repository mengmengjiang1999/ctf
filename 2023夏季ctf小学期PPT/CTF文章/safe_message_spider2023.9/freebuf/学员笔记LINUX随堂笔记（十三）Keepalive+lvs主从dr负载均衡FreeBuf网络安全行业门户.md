大家有好好学习吗！今天又来和大家分享了哦

## 第14章 搭建haproxy服务

## 一. 服务拓扑图

![v2-2129074473b4637cfc6128832470c51e_hd.j](https://pic3.zhimg.com/80/v2-2129074473b4637cfc6128832470c51e_hd.jpg)

## 二. 配置步骤

步骤1：创建本地yum源，安装必要的辅助程序

步骤2：解压并编译安装haproxy软件包

步骤3：配置haproxy服务

步骤4：测试haproxy服务

## 三. 命令配置

步骤1：创建本地yum源，安装必要的辅助程序

# cat /etc/yum.repos.d/local.repo //创建本地yum源文件

# rpm -q pcre-devel bzip2-deve //查询是否安装pcre-devel 和bzip2-devel是否安装

# yum -y install pcre-devel bzip2-devel //如果未安装，使用yum完成安装

步骤2：解压并编译安装haproxy软件包

# tar xf haproxy-1.4.24.tar.gz //解压haproxy程序包

# cd haproxy-1.4.24 //进入解压文件目录

# make TARGET=linux26 //根据内核版本编译

# make install //安装haproxy程序

步骤3：配置haproxy服务

#mkdir /etc/haproxy //在etc下创建一个haproxy目录

#cp examples//haproxy.cfg /etc/haproxy/ //将haproxy主配置文件拷贝到创建好的路径下

# vim /etc/haproxy/haproxy.cfg //编辑主配置文件

# this config needs haproxy-1.1.28 or haproxy-1.2.1

global

log 127.0.0.1 local0 //日志输出配置，所有日志都记录在本机，通过local0输出

log 127.0.0.1 local1 notice //定义haproxy日志级别[error warringinfo debug]

#log loghost local0 info

maxconn 4096 //默认最大连接数，需考虑ulimit-n限制

uid 99 //运行haproxy，用户UID

gid 99 //运行haproxy，用户组GID

daemon

#debug // haproxy 调试级别，建议只在开启单进程的时候调试

#quiet

defaults

log global

mode http //默认的模式mode { tcp|http|health }

option httplog //日志类别,采用httplog

option dontlognull //不记录健康检查日志信息

retries 3 //三次连接失败就认为是服务器不可用，也可以通过后面设置

maxconn 2000 //默认的最大连接数

contimeout 5000 //连接超时

clitimeout 50000 //客户端超时

srvtimeout 50000 //服务器超时

listen admin_stats

bind 0.0.0.0:1080 //设置Frontend和Backend的组合体，监控组的名称，按需要

自定义名称

mode http //http的7层模式

option httplog //采用http日志格式

#log 127.0.0.1 local0 err //错误日志记录

maxconn 10 //默认的最大连接数

stats refresh 30s //统计页面自动刷新时间

stats uri /stats //统计页面url

stats realm XingCloud\ Haproxy //统计页面密码框上提示文本

stats auth admin:admin //设置监控页面的用户和密码:admin,可以设置多个用户名

stats auth Frank:Frank //设置监控页面的用户和密码：Frank

stats hide-version //隐藏统计页面上HAProxy的版本信息

stats admin if TRUE

listen test1

bind 0.0.0.0:80

option httpchk GET /index.html //指定网页木

balance roundrobin //默认负载均衡方式是轮询

server app1_1 192.168.3.2:80 check inter 2000 fall 3 //添加服务主机，设置检测约束

server app1_2 192.168.3.3:80 check inter 2000 fall 3

# cp ~/haproxy-1.4.24/examples/haproxy.init /etc/init.d/haproxy
//将haproxy引导文件，拷贝到启动

项目录

# ln -s /usr/local/sbin/haproxy /usr/sbin/haproxy //给启动脚本文件创建软连接

# chmod +x /etc/init.d/haproxy //给启动文件赋予可执行权限

#cd /etc/init.d/ //进入启动目录

#./haproxy start //启动haproxy服务

安装web测试服务器

使用客户机，输入haproxy服务器ip完成测试

## 四. 搭建haproxy+keepalived服务

### 4.1拓扑图

![v2-2fbf1d35a9ae04eb0c4406b6d53e7a64_hd.j](https://pic1.zhimg.com/80/v2-2fbf1d35a9ae04eb0c4406b6d53e7a64_hd.jpg)

4.2配置步骤

步骤1：创建本地yum源，安装必要的辅助程序

步骤2：解压并编译安装haproxy软件包

步骤3：配置haproxy服务

步骤4：测试haproxy服务

### 4.3命令配置

步骤1：创建本地yum源，安装必要的辅助程序

# cat /etc/yum.repos.d/local.repo //创建本地yum源文件

# rpm -q pcre-devel bzip2-deve //查询是否安装pcre-devel 和bzip2-devel是否安装

# yum -y install pcre-devel bzip2-devel //如果未安装，使用yum完成安装

步骤2：解压并编译安装haproxy软件包

# tar xf haproxy-1.4.24.tar.gz //解压haproxy程序包

# cd haproxy-1.4.24 //进入解压文件目录

# make TARGET=linux26 //根据内核版本编译

# make install //安装haproxy程序

步骤3：配置haproxy服务

#mkdir /etc/haproxy //在etc下创建一个haproxy目录

#cp examples//haproxy.cfg /etc/haproxy/ //将haproxy主配置文件拷贝到创建好的路径下

# vim /etc/haproxy/haproxy.cfg //编辑主配置文件

# this config needs haproxy-1.1.28 or haproxy-1.2.1

global

log 127.0.0.1 local0 //日志输出配置，所有日志都记录在本机，通过local0输出

log 127.0.0.1 local1 notice //定义haproxy日志级别[error warringinfo debug]

#log loghost local0 info //

maxconn 4096 //默认最大连接数，需考虑ulimit-n限制

uid 99 //运行haproxy，用户UID

gid 99 //运行haproxy，用户组GID

daemon

#debug // haproxy 调试级别，建议只在开启单进程的时候调试

#quiet

defaults

log global

mode http //默认的模式mode { tcp|http|health }，

option httplog //日志类别,采用httplog

option dontlognull //不记录健康检查日志信息

retries 3 //三次连接失败就认为是服务器不可用，也可以通过后面设置

maxconn 2000 //默认的最大连接数

contimeout 5000 //连接超时

clitimeout 50000 //客户端超时

srvtimeout 50000 //服务器超时

listen admin_stats

bind 0.0.0.0:1080 //设置Frontend和Backend的组合体，监控组的名称，按需要

自定义名称

mode http //http的7层模式

option httplog //采用http日志格式

#log 127.0.0.1 local0 err //错误日志记录

maxconn 10 //默认的最大连接数

stats refresh 30s //统计页面自动刷新时间

stats uri /stats //统计页面url

stats realm XingCloud\ Haproxy //统计页面密码框上提示文本

stats auth admin:admin //设置监控页面的用户和密码:admin,可以设置多个用户名

stats auth Frank:Frank //设置监控页面的用户和密码：Frank

stats hide-version //隐藏统计页面上HAProxy的版本信息

stats admin if TRUE

listen test1

bind 0.0.0.0:80

option httpchk GET /index.html //指定网页木

balance roundrobin //默认负载均衡方式是轮询

server app1_1 192.168.3.2:80 check inter 2000 fall 3 //添加服务主机，设置检测约束

server app1_2 192.168.3.3:80 check inter 2000 fall 3

# cp ~/haproxy-1.4.24/examples/haproxy.init /etc/init.d/haproxy
//将haproxy引导文件，拷贝到启动

项目录

# ln -s /usr/local/sbin/haproxy /usr/sbin/haproxy //给启动脚本文件创建软连接

# chmod +x /etc/init.d/haproxy //给启动文件赋予可执行权限

#cd /etc/init.d/ //进入启动目录

#./haproxy start //启动haproxy服务

### 4.4安装web测试服务器

keepalived具体配置步骤

步骤1：创建本地yum源，安装必要的辅助程序

步骤2：解压并编译安装keepalived软件包

步骤3：配置keepalived服务

步骤4：测试keepalived服务

步骤1：创建本地yum源，安装必要的辅助程序

#mkdir /media/cdrom

#mkdir /etc/yum.repo.d/a

#mv /etc/yum.repo.d/Cent* /etc/yum.repo.d/a

#mount /dev/cdrom /media/cdrom

#vim /etc/yum.repo.d/local.repo

[base]

name=cets

baseurl=file:///media/cdrom

enabled=1

gpgcheck=0

#yum –y install openssl-devel

#yum –y install popt-devel

步骤2：解压并编译安装keepalived软件包

#tar zxf keepalived-1.2.13.tar.gz

#cd keepalived-1.2.13

#./configure -prefix=/ --with-kernel-dir=/usr/src/kernels/2.6.32-431.el6.x86_64 //编译指定安装路径

#make && make install /

步骤3：配置keepalived主服务器

#cd /etc/keepalived/ //进入keepalived软件主目录

#cp keepalived.conf keepalived.conf.bak //备份keepalived主配置文件

#vim keepalived.conf //编辑keepalived主配置文件

router_id r1 //给该keepalived主机取名

state MASTER //该keepalived主机类型为主

priority 100 //优先级100

virtual_ipaddress {

192.168.1.254} //虚拟ip地址

#service keepalived restart //重启服务

#service iptables stop //关闭防火墙

#service network restart //重启网卡

步骤4：配置keepalived从服务器

router_id r2 //给keepalived从服务器命名

state BACKUP //指定为备份服务器

priority 99 //优先级99

\------------------------------------------end------------------------------------------------
![v2-b1a5e188a1151634467f3268b1be13bd_hd.j](https://pic2.zhimg.com/80/v2-b1a5e188a1151634467f3268b1be13bd_hd.jpg)

  

