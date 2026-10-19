接上文

## 第13章 Keepalive+lvs主从dr负载均衡

## 一．主从keepalive +测试机

### 1.1主keepalive

![v2-4e817c922789d62a80fd208921ae80fe_hd.j](https://pic3.zhimg.com/80/v2-4e817c922789d62a80fd208921ae80fe_hd.jpg)

1.1.1配置本地yum源

#mkdir /media/cdrom //创建cdrom目录

#mkdir /etc/yum.repo.d/a //在yum源目录中创建a目录

#mv /etc/yum.repo.d/Cent* /etc/yum.repo.d/a //将以Cent开头的所有文件拷贝到a目录

#mount /dev/cdrom /media/cdrom //将光盘挂载到/media/cdrom/目录下

#vim /etc/yum.repo.d/local.repo //编辑本地yum源文件

[base]

name=cets

baseurl=file:///media/cdrom

enabled=1

gpgcheck=0

### 1.1.2安装支持keepalive软件包

#yum –y install openssl-devel //使用yum源安装openssl-devel软件

#yum –y install popt-devel //使用yum源安装popt-devel软件

### 1.1.3编译安装keepalive

#tar zxf keepalived-1.2.13.tar.gz //解压keepalived软件包

#cd keepalived-1.2.13 //进入解压的文件夹中

#./configure -prefix=/ --with-kernel-dir=/usr/src/kernels/2.6.32-431.el6.x86_64 //编译指定安装路径

#make && make install //编译和安装keepalived

### 1.1.4修改配置文件并启用keepalive

本机ip 192.168.1.1

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

### 1.2从keepalive

### 1.2.1本地yum

### 1.2.2安装支持keepalive软件包

### 1.2.3编译安装keepalive

### 1.2.4 修改配置文件并启用keepalive

本机ip 192.168.1.5

router_id r2

state SL**E 备注：也可以使用BACKUP

priority 99

virtual_ipaddress {

192.168.1.254}

### 1.3测试机

### 1.3.1测试机

Ip地址192.168.1.110

Service iptables stop

测试登陆192.168.1.25

### 1.3.2主开启关闭服务测试

关闭防火墙

开启httpd

重启keepalive

编辑测试网页#vim /var/www/html/index.html

<h1>192.168.1.1<h1>

down掉主服务在测试机在访问 192.168.1.254

### 1.3.2从开启关闭服务测试

关闭防火墙

开启httpd

重启keepalive

#ip addr show dev eth0 查看虚拟接口

编辑测试网页#vim /var/www/html/index.html

<h1>192.168.1.5<h1>

## 二．主从keepalive+ lvs +测试

![v2-87e9c4d234cde86c3db74656c8e9c635_hd.j](https://pic2.zhimg.com/80/v2-87e9c4d234cde86c3db74656c8e9c635_hd.jpg)

### 2.1主keepalive

### 2.1.1配置yum源

### 2.1.2安装支持包

### 2.1.3编译安装keepalive

### 2.1.4修改配置文件

router_id r1

state MASTER

priority 100

virtual_ipaddress {

192.168.1.254}

virtual_server 192.168.1.254 80 {

delay_loop 6

lb_algo rr

lb_kind DR

nat_mask 255.255.255.0

persistence_timeout 50

protocol TCP

real_server 192.168.1.11 80 {

weight 1

TCP_CHECK {

connect-port 80

connect_timeout 3

nb_get_retry 3

delay_before_retry 3

}}

}

virtual_server 192.168.1.254 80 {

delay_loop 6

lb_algo rr

lb_kind DR

nat_mask 255.255.255.0

persistence_timeout 50

protocol TCP

real_server 192.168.1.22 80 {

weight 1

TCP_CHECK {

connect-port 80

connect_timeout 3

nb_get_retry 3

delay_before_retry 3

}}

}

### 2.1.5安装ipvsadm测试看效果

### 2.2从keepalive

1.本地yum

2.安装支持keepalive软件包

3.编译安装keepalive

4.修改配置文件并启用keepalive

复制备份 cp keepalive.conf keepalive.conf.bak

本机ip 192.168.1.5

router_id r2

state SL**E

priority 99

virtual_ipaddress {

192.168.1.254}

virtual_server 192.168.1.254 80 {

delay_loop 6

lb_algo rr

lb_kind DR

nat_mask 255.255.255.0

persistence_timeout 50

protocol TCP

real_server 192.168.1.11 80 {

weight 1

TCP_CHECK {

connect-port 80

connect_timeout 3

nb_get_retry 3

delay_before_retry 3

}}

}

5.安装ipvsadm

yum –y install ipvsadm

ipvsadm –Lnc /Ln

### 2.3节点Web1

### 2.3.1修改ip地址

192.168.1.11

### 2.3.2添加lo：0

#cd /etc/sysconfig/network-scripts

#cp ifcfg-lo ifcfg-lo:0

#vim ifcfg-lo:0

DEVICE=lo:0

IPADDR=192.168.1.254

NETMASK=255.255.255.255

ONBOOT=yes

重启服务service network restart

酌情添加

vi /etc/rc.local //添加VIP本地访问路由

/sbin/route add -host 192.168.1.254 dev lo:0

# route add -host 192.168.1.254 dev lo:0

### 2.3.3调整/proc参数，禁用ARP响应

vim /etc/sysctl.conf

net.ipv4.conf.all.arp_ignore = 1

net.ipv4.conf.all.arp_announce = 2

net.ipv4.conf.default.arp_ignore = 1

net.ipv4.conf.default.arp_announce = 2

net.ipv4.conf.lo.arp_ignore = 1

net.ipv4.conf.lo.arp_announce = 2

sysctl -p

### 2.3.4 重启httpd服务建立测试网页

vi /var/www/html/index.html

<h1>192.168.1.11——测试网页/<h1>

# service httpd start

# chkconfig httpd on

### 2.4节点web2

### 2.4.1修改ip地址

192.168.1.22

### 2.4.2添加lo：0

#cd /etc/sysconfig/network-scripts

#cp ifcfg-lo ifcfg-lo:0

#vim ifcfg-lo:0

DEVICE=lo:0

IPADDR=192.168.1.254

NETMASK=255.255.255.255

ONBOOT=yes

重启服务service network restart

酌情添加

vi /etc/rc.local //添加VIP本地访问路由

/sbin/route add -host 192.168.1.254 dev lo:0

# route add -host 192.168.1.254 dev lo:0

### 2.4.3调整/proc参数，禁用ARP响应

vim /etc/sysctl.conf

net.ipv4.conf.all.arp_ignore = 1

net.ipv4.conf.all.arp_announce = 2

net.ipv4.conf.default.arp_ignore = 1

net.ipv4.conf.default.arp_announce = 2

net.ipv4.conf.lo.arp_ignore = 1

net.ipv4.conf.lo.arp_announce = 2

sysctl -p

### 2.4.4 重启httpd服务建立测试网页

vi /var/www/html/index.html

<h1>192.168.1.22/<h1>

# service httpd start

# chkconfig httpd on

### 2.5测试机

### 2.5.1测试主+lvs

配置ip 192.168.1.110

关闭防火墙能与其他主机通信

登陆192.168.1.254

主 ipvsadm -Ln

### 2.5.2测试从+lvs

Down掉主keepalive

在登陆

### 2.5.3测试节点

登陆成功节点1 down点 在测试节点2

\--------------------------------------------------end--------------------------------------------
![v2-be7b3a919d240f369cef3d85db776fa7_hd.j](https://pic4.zhimg.com/80/v2-be7b3a919d240f369cef3d85db776fa7_hd.jpg)

  

