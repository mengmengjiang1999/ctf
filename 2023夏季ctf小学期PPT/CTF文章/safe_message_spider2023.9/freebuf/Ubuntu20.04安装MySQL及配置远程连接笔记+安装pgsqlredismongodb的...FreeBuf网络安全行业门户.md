## 前言

安装了一下MySQL挺曲折，特此记录一下过程。我安装MySQL只为测试使用，踩坑较多所以记录下，其实用phpstudy弄一个低版改几下就好了。

 **注意注意注意！！！这些方式安装的数据库都存在默认口令，未授权的漏洞，这是我想要的，运维及开发人员请注意修改以保证数据库安全性。**

## 环境

Ubuntu20.04![image-20210908140055041](https://image.3001.net/images/20210908/1631092241_61387e1130e739711e98b.png!small)

## 更新源软件包列表

Ubuntu安装完成之后首先需要更换国内源，更新源，推荐清华源，其他源网上找吧

    
    
    # 清华源获取方法  
    # Ubuntu 的软件源配置文件是 /etc/apt/sources.list。将系统自带的该文件做个备份，将该文件替换，即可使用 TUNA 的软件源镜像。  
    https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/  
    # 替换之后，更新源  
    $ apt-get update  # 取回更新的软件包列表信息

## 安装MySQL

    
    
    sudo apt-get install -y mysql-server

## 查看MySQL运行状态

显示running说明已经在运行

    
    
    systemctl status mysql

## 登录MySQL

可以直接在命令行输入mysql进入命令行。也可以使用下面命令登录，mysql默认密码是root

    
    
    # 不需要输入密码，直接登录  
    sudo mysql  
    # -u指定用户名root，回车后输入密码  
    mysql -uroot -p

## MySQL常用命令

    
    
    #启动  
    service mysql start  
    systemctl start mysql  
    #关闭  
    service mysql stop  
    systemctl stop mysql  
    #重启  
    service mysql restart  
    systemctl restart mysql  
    # 查看运行状态  
    service mysql status  
    systemctl status mysql  
    # 新增用户  
    CREATE USER 'admin'@'localhost' IDENTIFIED BY '你要设置的密码';  
    # 对新增的用户更改加密方式和密码  
    ALTER USER 'admin'@'localhost' IDENTIFIED WITH mysql_native_password BY 'admin';  
    # 退出  
    quit  
    # 卸载MySQL  
    sudo rm /var/lib/mysql/ -R  
    sudo rm /etc/mysql/ -R  
    sudo apt-get autoremove mysql* --purge

## 设置允许远程登录

### 1.查看root用户允许登录的范围(host)

    
    
    use mysql  
    select host, user, authentication_string, plugin from user;

### 2.设置root允许远程登录

默认的root用户的host值是本地localhost，说明root用户只能本地登录。我们把root用户的修改为全部方式，host值为%

    
    
    update user set host='%' where user='root';

### 3.刷新权限

    
    
    FLUSH PRIVILEGES;

### 4.修改MySQL加密规则

    
    
    MySQL8.0之前的版本密码加密规则：mysql_native_password  
    MySQL8.0密码加密规则：caching_sha2_password

开始修改，注意字段的值，`'root'@'localhost'`由于我们前面设置远程登陆，host修改为%，所以我这里要写`'root'@'%'`，password位置要写MySQL的root用户密码，这里是`root`

    
    
    # 执行命令  
    ALTER USER 'root'@'%' IDENTIFIED BY 'root' PASSWORD EXPIRE NEVER;  
    ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root';  
    ​  
    # 修改加密方式  
    ALTER USER 'root'@'localhost' IDENTIFIED BY 'password' PASSWORD EXPIRE NEVER;  
    # 重新设置root的密码，我这里新的密码依然写root  
    ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '新的密码';

### 5.刷新下权限

    
    
    FLUSH PRIVILEGES;

查看结果![image-20210908154317624](https://image.3001.net/images/20210908/1631092250_61387e1a777d58c34cb37.png!small)

这时候还是不能远程

### 6.修改bind-address

看一下端口，发现3306的ip在127.0.0.1，我们需要把这个ip修改为0.0.0.0就可以了

    
    
    netstat -ntulp

设置ip

    
    
    vi /etc/mysql/mysql.conf.d/mysqld.cnf  
    bind-address            = 0.0.0.0

### 7.重启MySQL服务

    
    
    systemctl restart mysql

### 8.防火墙放行3306端口

发现竟然还不能远程，扫描3306端口是filter，那肯定是防火墙在搞鬼了![image-20210908155514661](https://image.3001.net/images/20210908/1631092255_61387e1f0c9701a10ecb1.png!small)

我的Ubuntu装了iptables，其他的firewall和ufw都类似，这里只说iptables。添加规则

    
    
    iptables -A INPUT -p tcp -s 0.0.0.0 --dport 3306 -j ACCEPT
    
    
    # 如果是本地的测试环境，没有业务需求的话，直接关闭防火墙或者开启所有规则就行，方式如下  
    iptables -P INPUT ACCEPT                                             
    iptables -P OUTPUT ACCEPT  
    iptables -P FORWARD ACCEPT

###
9.远程连接MySQL![image-20210908162226599](https://image.3001.net/images/20210908/1631092257_61387e210a8983cdcc430.png!small)

![image-20210908162307996](https://image.3001.net/images/20210908/1631092258_61387e22506304c4c9130.png!small)

## Ubuntu20.04安装redis、mongodb、postgresql方法链接

我就是按照这几个教程做的，教程中都有说明怎么设置远程连接，跟着做应该不会有问题

### mongodb

这个在安装过程中由于软件包下载速度太慢了，啥原因你肯定洞=懂，这里多放一个proxychains4安装方法，设置socks5代理去下载，速度嗖嗖的。

> <https://blog.csdn.net/a806689294/article/details/109635803>
>
> Ubuntu20.04 通过 apt 方式安装 mongoDB
> <https://www.jianshu.com/p/e35ccf131784>mongodb远程连接配置
> <https://www.jianshu.com/p/d1dd4aea6b65>

### redis

> <https://blog.csdn.net/snowdream86/article/details/106608928>

### pgsql

> <https://cloud.tencent.com/developer/article/1632506>

  

  

