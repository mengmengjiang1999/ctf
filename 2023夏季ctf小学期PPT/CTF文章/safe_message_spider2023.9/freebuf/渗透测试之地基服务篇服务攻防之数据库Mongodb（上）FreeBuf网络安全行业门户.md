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

今天会讲解到利用介绍和Labs安装、在Kali-2021中安装MongoDB、学习Mongo
Shell等操作，如果连Mongodb都不会安装操作提权等，怎么进行下一步的研究Mongodb数据库安全！怎么拿下对方服务器？

## 二、Windows 平台安装 MongoDB

目前MongoDB最新版本已经到了MongoDB4.4.5，但市场上的主流版本是3.4和3.6两个版本，所以，本次我们以3.6版本为例。这里自行安装！

### 1、MongoDB 下载

MongoDB 提供了可用于 32 位和 64 位系统的预编译二进制包，你可以从MongoDB官网下载安装，MongoDB 预编译二进制包

 **下载地址：**  
https://www.mongodb.com/download-center/community

首先，在 MongoDB2.2 版本后已经不再支持 Windows XP 系统。

另外，MongoDB为Windows平台提供msi和zip两种安装方式：

    
    
    1. msi方式，一路下一步，方便快捷，但只推荐MongoDB4.0及以上版本采用msi方式安装，因为MongoDB4.x版本对msi安装方式进行了优化，随着提示就可以完成配置，但3.x和更低的版本则仍旧需要在安装完毕后，手动做配置，所以低版本不推荐msi方式。
    2. zip方式，解压即安装，可以将其安装到任意目录，后续都可以手动进行配置，比较灵活，推荐采用这种方式进行安装。
    

![1626569206_60f379f671c93063cf1cb.png!small?1626569206923](https://image.3001.net/images/20210718/1626569206_60f379f671c93063cf1cb.png!small?1626569206923)

    
    
    1. MongoDB for Windows 64-bit 适合 64 位的 Windows Server 2008 R2, Windows 7 , 及最新版本的 Window 系统。
    2. MongoDB for Windows 32-bit 适合 32 位的 Window 系统及最新的 Windows Vista。 32 位系统上 MongoDB 的数据库最大为 2GB。
    3. MongoDB for Windows 64-bit Legacy 适合 64 位的 Windows Vista, Windows Server 2003, 及 Windows Server 2008 。
    

下载 .msi 文件，下载后双击该文件，按操作提示安装即可。

### 2、开始安装

安装过程中，你可以通过点击 "Custom(自定义)" 按钮来设置你的安装目录。

下一步安装 "install mongoDB compass" 不勾选（当然你也可以选择安装它，可能需要更久的安装时间），MongoDB Compass
是一个图形界面管理工具，我们可以在后面自己到官网下载安装，下载地址：

    
    
    https://www.mongodb.com/download-center/compass
    

![1626569213_60f379fd8307fdce3740d.png!small?1626569215627](https://image.3001.net/images/20210718/1626569213_60f379fd8307fdce3740d.png!small?1626569215627)

![1626569217_60f37a017f0a81d69f7e4.png!small?1626569219825](https://image.3001.net/images/20210718/1626569217_60f37a017f0a81d69f7e4.png!small?1626569219825)

![1626569221_60f37a05dedb087547bf9.png!small?1626569223921](https://image.3001.net/images/20210718/1626569221_60f37a05dedb087547bf9.png!small?1626569223921)

![1626569226_60f37a0a894ca871d8404.png!small?1626569228700](https://image.3001.net/images/20210718/1626569226_60f37a0a894ca871d8404.png!small?1626569228700)

![1626569230_60f37a0e419831efb6fb2.png!small?1626569233370](https://image.3001.net/images/20210718/1626569230_60f37a0e419831efb6fb2.png!small?1626569233370)看以上图按照图片指示安装完成！

### 3、初始配置变量

 **1）bin目录**  
![1626569235_60f37a136b51a41187ea7.png!small?1626569237129](https://image.3001.net/images/20210718/1626569235_60f37a136b51a41187ea7.png!small?1626569237129)
在bin目录内，我们暂时需要了解两个文件：

    
    
    1. mongo.exe	# MongoDB客户端软件
    2. mongod.exe	# MongoDB服务端软件
    

**2）配置环境变量**  
这一步的目的是，后续我们可以直接通过终端操作MongoDB。

步骤是此电脑--鼠标右键选择属性--高级系统设置--环境变量--系统变量选项，找到Path，选择新建，将C:\mongodb\bin目录添加进去，如下图：  
![1626569241_60f37a1907565e4c985fb.png!small?1626569242865](https://image.3001.net/images/20210718/1626569241_60f37a1907565e4c985fb.png!small?1626569242865)

 **3）编写配置文件**  
编写配置文件的目的是便于后续以配置文件的方式启动MongoDB服务。

打开mongodb.conf文件，写入如下内容，然后保存。

    
    
    # 系统日志相关
    systemLog:
      destination: file  # 使用文件存储日志
      path: C:\mongodb\log\mongodb.log  # 日志位置
      logAppend: true    # 是否以追加的形式记录日志
    
    # 数据相关
    storage:
      journal:  # 回滚日志
        enabled: true
      dbPath: C:\mongodb\data  # 数据存储目录
    
    # 网络配置相关
    net:
      port: 27017 # 默认端口
      bindIp: 127.0.0.1  # 绑定ip， 多个ip以逗号分隔
    

上面配置中的bindIp设置为127.0.0.1表示只能本地访问MongoDB，如果需要远程访问，还需要设置本机IP，然后重启服务。  
![1626569249_60f37a215481a0d3dc347.png!small?1626569254633](https://image.3001.net/images/20210718/1626569249_60f37a215481a0d3dc347.png!small?1626569254633)

 **4）将MongoDB服务添加Windows的服务**

这一步的目的是将来在终端中通过net来管理MongoDB。

以管理员的身份打开终端，输入：  
![1626569254_60f37a263e25a6ee4acaf.png!small?1626569254633](https://image.3001.net/images/20210718/1626569254_60f37a263e25a6ee4acaf.png!small?1626569254633)

    
    
    mongod --config C:\mongodb\mongodb.conf --install
    

上面的命令执行成功后，此时Windows的服务中就有了MongoDB的服务了。  
![1626569259_60f37a2b34d6533b4d8b5.png!small?1626569261604](https://image.3001.net/images/20210718/1626569259_60f37a2b34d6533b4d8b5.png!small?1626569261604)

你可以在Windows的服务中管理MongoDB，比如设置开机启动、手动等设置。

而我们现在则可以在终端中使用net来start和stop MongoDB了。

![1626569263_60f37a2f3fa72e4bb5984.png!small?1626569263787](https://image.3001.net/images/20210718/1626569263_60f37a2f3fa72e4bb5984.png!small?1626569263787)

    
    
    net start mongodb
    net stop mongodb
    

注意，只有以管理员身份打开的终端才能执行net命令。

### 4、安装测试

前提是MongoDB服务正在运行。

终端(可以是非管理员身份打开的终端)输入mongo即可开启MongoDB客户端，输入相应命令来使用MongoDB服务了：

![1626569268_60f37a345461dcd1a0c1e.png!small?1626569269284](https://image.3001.net/images/20210718/1626569268_60f37a345461dcd1a0c1e.png!small?1626569269284)

    
    
    mongo
    

移除 MongoDB 服务:

    
    
    C:\mongodb\bin\mongod.exe --remove
    

命令行下运行 MongoDB 服务器 和 配置 MongoDB 服务 任选一个方式启动就可以。

### 5、MongoDB 后台管理 Shell

![1626569273_60f37a39685675aef1731.png!small?1626569273867](https://image.3001.net/images/20210718/1626569273_60f37a39685675aef1731.png!small?1626569273867)

如果你需要进入MongoDB后台管理，你需要先打开mongodb装目录的下的bin目录，然后执行mongo.exe文件，MongoDB
Shell是MongoDB自带的交互式Javascript shell,用来对MongoDB进行操作和管理的交互式环境。

当你进入mongoDB后台后，它默认会链接到 test 文档（数据库）：

![1626569278_60f37a3e13cd96e2093fa.png!small?1626569279033](https://image.3001.net/images/20210718/1626569278_60f37a3e13cd96e2093fa.png!small?1626569279033)

    
    
    > mongo
    MongoDB shell version: 3.0.6
    connecting to: test
    ……
    

由于它是一个JavaScript shell，您可以运行一些简单的算术运算:

    
    
    > 2 + 2
    4
    >
    

db 命令用于查看当前操作的文档（数据库）：

    
    
    > db
    test
    >
    

插入一些简单的记录并查找它：

    
    
    > db.runoob.insert({x:10})
    WriteResult({ "nInserted" : 1 })
    > db.runoob.find()
    { "_id" : ObjectId("5604ff74a274a611b0c990aa"), "x" : 10 }
    >
    

参考：  
https://www.runoob.com/mongodb/mongodb-window-install.html

## 三、图形化界面安装

正如你所看到的，以上步骤已经可以完全实现使用MongoDB的需求。你要是想的话可以继续安装可视化界面，毕竟操作起来更方便。

 **开始安装MongoDB Compass**

下载地址：

    
    
    https://www.mongodb.com/download-center/compass
    

![1626569286_60f37a4696176c7efeaca.png!small?1626569287660](https://image.3001.net/images/20210718/1626569286_60f37a4696176c7efeaca.png!small?1626569287660)

![1626569295_60f37a4f724427d368a16.png!small?1626569297233](https://image.3001.net/images/20210718/1626569295_60f37a4f724427d368a16.png!small?1626569297233)

![1626569300_60f37a547586023ba1ddd.png!small?1626569307425](https://image.3001.net/images/20210718/1626569300_60f37a547586023ba1ddd.png!small?1626569307425)

![1626569304_60f37a5858bee224678f5.png!small?1626569307425](https://image.3001.net/images/20210718/1626569304_60f37a5858bee224678f5.png!small?1626569307425)

![1626569308_60f37a5cbe268f2a3cfd1.png!small](https://image.3001.net/images/20210718/1626569308_60f37a5cbe268f2a3cfd1.png!small)

直接点击上图的CONNECT，进行连接，进入如下图（还记得吗朋友们，要想连接成功必须要开服务，mongod -dbpath
C:\MongoDB\data\db 这条命令可要一直开着哦）

![1626569329_60f37a715ffece24728a2.png!small?1626569331069](https://image.3001.net/images/20210718/1626569329_60f37a715ffece24728a2.png!small?1626569331069)成功连接！

参考文章：

    
    
    https://blog.csdn.net/weixin_41466575/article/details/105326230
    

Mongodb入门：  
![1626569324_60f37a6c2ab6a66d1aea2.png!small?1626569327450](https://image.3001.net/images/20210718/1626569324_60f37a6c2ab6a66d1aea2.png!small?1626569327450)

    
    
    https://www.runoob.com/mongodb/mongodb-databases-documents-collections.html
    

## 四、配置服务并设置远程连接

接下来介绍下基础的操作！

1）新建用户  
![1626569335_60f37a774e44499dbbf84.png!small?1626569335938](https://image.3001.net/images/20210718/1626569335_60f37a774e44499dbbf84.png!small?1626569335938)

    
    
    db.createUser({user:"dayu",pwd:"123456",roles:[{"role":"userAdmin","db":"admin"},{"role":"root","db":"admin"},{"role":"userAdminAnyDatabase","db":"admin"}]})
    

2）对账号授权：  
![1626569340_60f37a7c2a106ebda005a.png!small?1626569340453](https://image.3001.net/images/20210718/1626569340_60f37a7c2a106ebda005a.png!small?1626569340453)

    
    
    db.auth("dayu","123456")
    

3）远程登录  
![1626569347_60f37a834b61d6defa3c1.png!small?1626569347926](https://image.3001.net/images/20210718/1626569347_60f37a834b61d6defa3c1.png!small?1626569347926)

    
    
    mongo -u dayu -p 123456 localhost:27017/admin
    

**拓展：**  
账号管理命令：

1）修改用户权限

    
    
    db.updateUser("root", {roles:[{role:"readWriteAnyDatabase", db:"admin"}] })
    

2）修改用户密码

    
    
    db.changeUserPassword(“username","newPasswd")
    

3）删除用户

    
    
    db.changeUserPassword(“username","newPasswd")
    

## 五、kali-Labs安装

### 1、什么是MongoDB ?

MongoDB是一种开源的、文档导向的数据库管理系统，由C++撰写而成。  
在MongoDB中，数据以JSON样式文档的形式存储。  
MongoDB的一些主要特性:

    
    
    • 基于文档
    • 高性能
    • 高可用性
    • 简单的可扩展性
    • 没有复杂的联接
    

### 2、安全性如何 ?

随着NoSQL数据库的使用越来越多，安全性应该被认真考虑。 就像其他系统一样，MongoDB的安全性也不是一个单一的工作。 生态系统中的每个人都对此负责。
尽管MongoDB具有一些内置的安全功能，但由于各种原因（如配置错误，不更新，编程不佳等），在生产中可能存在漏洞 。

### 3、在Kali-2021中安装MongoDB

#### 1）导入Mongodb密匙

在终端上，发出以下命令以从https://www.mongodb.org/static/pgp/server-4.4.asc导入MongoDB公共GPG密钥：

![1626569357_60f37a8d4b3c48ca2ec71.png!small?1626569357919](https://image.3001.net/images/20210718/1626569357_60f37a8d4b3c48ca2ec71.png!small?1626569357919)

    
    
    wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -    

该操作应以响应OK。但是，如果收到指示gnupg未安装的错误，则可以：

1）gnupg使用以下命令安装及其所需的库：

    
    
    sudo apt-get install gnupg
    

2）安装完成后，重试导入密钥：

    
    
    wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -    

#### 2）创建文件

/etc/apt/sources.list.d/mongodb-org-4.4.list为MongoDB创建文件。

![1626569365_60f37a954ca176475fb7c.png!small?1626569366025](https://image.3001.net/images/20210718/1626569365_60f37a954ca176475fb7c.png!small?1626569366025)

    
    
    echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
    

#### 3）重新加载本地软件包数据库

发出以下命令以重新加载本地软件包数据库：

    
    
    sudo apt-get update
    

#### 4）安装MongoDB软件包

您可以安装最新的稳定版MongoDB或特定版本的MongoDB

![1626569369_60f37a99ade7f609a69a4.png!small?1626569372660](https://image.3001.net/images/20210718/1626569369_60f37a99ade7f609a69a4.png!small?1626569372660)

    
    
    sudo apt-get install -y mongodb-org
    

**或者定制版：**

    
    
    sudo apt-get install -y mongodb-org=4.4 mongodb-org-server=4.4 mongodb-org-shell=4.4 mongodb-org-mongos=4.4 mongodb-org-tools=4.4
    

如果您仅安装mongodb-org=4.4而不包括组件包，则无论您指定哪个版本，都将安装每个MongoDB包的最新版本。

可选的。尽管您可以指定任何可用的MongoDB版本，但 apt-get将在更新版本可用时升级软件包。为防止意外升级，您可以将软件包固定在当前安装的版本上：

    
    
    echo "mongodb-org hold" | sudo dpkg --set-selections
    echo "mongodb-org-server hold" | sudo dpkg --set-selections
    echo "mongodb-org-shell hold" | sudo dpkg --set-selections
    echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
    echo "mongodb-org-tools hold" | sudo dpkg --set-selections
    

#### 5）运行MongoDB社区版

 **ulimit注意事项**

大多数类似Unix的操作系统都会限制进程可能使用的系统资源。这些限制可能会对MongoDB的运行产生负面影响，因此应进行调整。有关平台的推荐设置，请参见UNIXulimit设置。

    
    
    从MongoDB 4.4开始，如果ulimit打开文件数的值小于，则会生成启动错误 64000。
    

##### （1）启动MongoDB：

![1626569376_60f37aa09f28c26c42f91.png!small?1626569377529](https://image.3001.net/images/20210718/1626569376_60f37aa09f28c26c42f91.png!small?1626569377529)

    
    
    sudo systemctl start mongod
    

**如果在启动时收到类似于以下内容的错误 mongod：**

Failed to start mongod.service: Unit mongod.service not found.

首先运行以下命令：

    
    
    sudo systemctl daemon-reload
    

然后再次运行上面的启动命令。

（2）验证MongoDB是否已成功启动  
![1626569431_60f37ad7cf536c42f11b7.png!small?1626569433333](https://image.3001.net/images/20210718/1626569431_60f37ad7cf536c42f11b7.png!small?1626569433333)

    
    
    sudo systemctl status mongod
    
    您可以选择通过发出以下命令来确保MongoDB将在系统重新启动后启动：
    
    sudo systemctl enable mongod
    

（3）停止MongoDB

    
    
    根据需要，可以mongod通过发出以下命令来停止该过程：
    
    sudo systemctl stop mongod
    

（4）重新启动MongoDB

    
    
    您可以mongod通过发出以下命令来重新启动该过程：
    
    sudo systemctl restart mongod
    
    您可以通过查看/var/log/mongodb/mongod.log文件中的输出来跟踪错误或重要消息的处理状态
    

（5）开始使用MongoDB

![1626569612_60f37b8c6994b01e38053.png!small?1626569618150](https://image.3001.net/images/20210718/1626569612_60f37b8c6994b01e38053.png!small?1626569618150)

    
    
    mongo
    

#### 6）卸载MongoDB社区版

（1）停止MongoDB

mongod通过发出以下命令来停止该过程：

    
    
    sudo service mongod stop
    

（2）删除软件包  
删除以前安装的所有MongoDB软件包。

    
    
    sudo apt-get purge mongodb-org*
    

（3）删除数据目录

删除MongoDB数据库和日志文件。

    
    
    sudo rm -r /var/log/mongodb
    sudo rm -r /var/lib/mongodb
    

#### 7）外联mongodb

默认情况下的本地主机绑定:

默认情况下，MongoDB在启动时bindIp将set设置为
127.0.0.1，该绑定到localhost网络接口。这意味着mongod只能接受来自同一计算机上运行的客户端的连接。除非将此值设置为有效的网络接口，否则远程客户端将无法连接到mongod，并且mongod不能初始化副本集。

可以配置此值：

在MongoDB配置文件中，带有bindIp或  
通过命令行参数 --bind_ip

mongodb在启动时会有一个默认的配置文件，linux下为/etc/mongod.conf，mac下如果用brew启动则为/usr/local/etc/mongod.conf，windows下暂时还没玩过。这里要说明下，笔者用的mongodb@3.6，跟之前2.x的配置文件格式似乎不同，这里就以linux下3.6的为准了，请各位朋友注意。

![1626569397_60f37ab5c6ccffdcbad67.png!small?1626569404206](https://image.3001.net/images/20210718/1626569397_60f37ab5c6ccffdcbad67.png!small?1626569404206)

![1626569403_60f37abbcfdfb0f60e21c.png!small?1626569404207](https://image.3001.net/images/20210718/1626569403_60f37abbcfdfb0f60e21c.png!small?1626569404207)

    
    
    sudo gedit mongod.conf
    

这儿只能修改单个ip，不能后续添加！！

参考文章：

    
    
    https://docs.mongodb.com/manual/tutorial/install-mongodb-on-debian/#create-a-etc-apt-sources-list-d-mongodb-org-4-4-list-file-for-mongodb
    

## 六、总结

今天学到了介绍和Labs安装、在Kali-2021中安装MongoDB、学习Mongo
Shell的方式方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）-> 服务攻防之数据库Mongodb（上）......
    

接下来在《服务攻防之数据库Mongodb（下）》会接触到如何学习Mongo
Shell、自搭渗透实验环境、Mongodb进攻渗透、MSF渗透Mongodb、自动化评估、整改加固建议等操作，如何提权渗透等方法，请看下篇服务攻防之数据库Mongodb上篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

