***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担**

**在前段时间的Defcon会议上，Nmap发布了7.8版本，包括了Npcap抓包驱动程序更新和80多项NSE脚本、库等[更新](https://nmap.org/changelog#7.80)，[中文版更新详情看这里](https://www.freebuf.com/column/211555.html)。查看更新内容是，突然发现关于Mongodb的NSE脚本更新似曾相识，点进去一看，还真是之前我提交的[#1565bug](https://github.com/nmap/nmap/issues/1565)修复请求。  
年初MongoDB数据库未授权访问漏洞造成的数据泄露事件频发，因工作需要关注了这个漏洞，网上搜索资料，发现从漏洞检测到漏洞整改，网上已有的方法、工具均存在或多或少的问题，漏洞整改建议也不完整或过时。于是对当时已有的各个Mongodb版本均做了测试，重新梳理了漏洞检测方法及漏洞整改建议，形成了这篇文档。**

## 一、漏洞危害

对外开放的MongoDB服务，未配置访问认证授权，无需认证连接数据库后对数据库进行任意操作（增、删、改、查高危动作），存在严重的数据泄露风险。

##  二、漏洞成因

MongoDB服务安装后，默认未开启权限验证。如果服务监听在0.0.0.0，则可远程无需授权访问数据库。

> 3.0之前版本的MongoDB,默认监听在0.0.0.0，3.0及之后版本默认监听在127.0.0.1。
>
>
> 3.0之前版本，如未添加用户管理员账号及数据库账号，使用`--auth`参数启动时，在本地通过127.0.0.1仍可无需账号密码登陆访问数据库，远程访问则提示需认证；
>
> 3.0及之后版本，使用`--auth`参数启动后，无账号则本地和远程均无任何数据库访问权限。

##  三、漏洞验证

MongoDB存在未授权访问漏洞时，使用MongoDB的高版本shell工具mongo（高版本兼容低版本）直接连接成功，执行`show
dbs`命令，无报错信息，列表存在默认库`local`库，则判断存在未授权访问（local库即便删除，重启MongoDB后仍会生成）。

    
    
    C:\ "C:\Program Files\MongoDB\Server\4.0\bin\mongo.exe" 127.0.0.1
    
    > show dbs
    admin   0.000GB
    config  0.000GB
    local   0.000GB
    test    0.000GB

部分版本默认不存在`admin`库，但如果创建了用户管理员账号，这个库一定存在，如果存在`admin`库，可以进入该库查看是否有用户，有用户则表示添加了用户管理员账号，但未使用`--auth`参数启动。

    
    
    > use admin
    switched to db admin
    > show users
    {
            "_id" : "admin.admin",
            "user" : "admin",
            "db" : "admin",
            "roles" : [
                    {
                            "role" : "userAdminAnyDatabase",
                            "db" : "admin"
                    }
            ],
            "mechanisms" : [
                    "SCRAM-SHA-1",
                    "SCRAM-SHA-256"
            ]
    }

也可以使用图形化界面管理工具连接服务进行测试。

Robo
3T下载地址：<https://robomongo.org/download>，建议使用1.2.1版本，使用1.3及之后版本的话，服务端如果使用较低版本MongoDB，存在未授权访问时仍无法连接。

##  四、整改建议

###  4.1. 方案1：本地监听

如MongoDB只需在本地使用，建议只在本地开启监听服务，使用`--bind_ip 127.0.0.1`绑定监听地址。

    
    
    $ mongod --bind_ip 127.0.0.1 --dbpath /tmp/test

或：在配置文件中指定监听IP，Linux下默认配置文件为/etc/mongod.conf。

    
    
    # network interfaces
    net:
      port: 27017
      bindIp: 127.0.0.1

指定配置文件启动

    
    
    mongod --config /etc/mongod.conf

> 3.0及之后版本的MongoDB，监听服务默认在127.0.0.1开启。

###  4.2. 方案2：限制访问源

如果仅对内网服务器提供服务，建议禁止将MongoDB服务发布到互联网上，并在主机上通过防火墙限制访问源IP。

Linux主机，使用iptables进行限制：

    
    
    iptables -A INPUT -s <ip-address> -p tcp --destination-port 27017 -m state --state NEW,ESTABLISHED -j ACCEPT
    iptables -A OUTPUT -d <ip-address> -p tcp --source-port 27017 -m state --state ESTABLISHED -j ACCEPT

> `<ip-> address>`替换成需访问MongoDB服务的IP；第一条规则允许外部应用访问MongoDB默认服务端口27017，第二条规则允许MongoDB外出流量到达外部应用。Windows主机，可以通过图形管理界面添加防火墙策略或使用`netsh`命令添加，参考文档：<https://docs.mongodb.com/manual/tutorial/configure-> windows-netsh-firewall/>

###  4.3. 方案3：启动基于角色的登录认证功能

MongoDB支持SCRAM、x.509证书认证等多种认证机制，SCRAM（Salted Challenge Response Authentication
Mechanism）是3.x版本的默认认证机制，该机制通过用户名、密码验证，基于用户角色进行访问控制。下面是添加账号认证的方法：

> MongoDB
> 3.0及以上版本启动时添加`--auth`参数开启认证访问，此时若数据库中无账号，本地登录则无权限进行任何操作，因此需要先以无认证的方式启动服务并创建系统用户管理员账号。

**1）以无访问认证的方式启动MongoDB**

    
    
    $ mongod --dbpath /data/db

**2）未开启认证的环境下，登录到数据库**

    
    
    $ mongo --host 127.0.0.1 --port 27017
    MongoDB shell version v4.0.8
    connecting to: mongodb://127.0.0.1:27017/test?gssapiServiceName=mongodb

**3）创建系统用户管理员** 创建一个用户名为`myUserAdmin`，密码为`Passw0rd`的系统用户管理员账号。

    
    
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

> 说明：3.0之前版本使用db.addUser方法创建用户。

**4）重启MongoDB服务，开启访问认证** 启动时添加`--auth`参数

    
    
    $ mongod --auth --port 27017 --dbpath /tmp/test

或：在配置文件中添加以下内容，指定配置文件启动服务：

    
    
    #security:
    security:
      authorization: enabled

指定配置文件启动MongoDB

    
    
    $ mongod --config /etc/mongod.conf

**5）使用系统用户管理员账号登录**

    
    
    $ mongo --port 27017 -u "myUserAdmin" -p "Passw0rd" --authenticationDatabase "admin"

也可以在连接MongoDB是不指定认证信息，连接成功后通过db.auth()方法进行认证：

    
    
    > use admin
    switched to db admin
    > db.auth("myUserAdmin","Passw0rd")
    1  #返回1，表示认证成功

**6）创建数据库用户**
创建完系统用户管理员账号并通过系统用户管理员登陆后，对每个库创建指定的用户。下面以对products库创建一个具有读写权限的用户accountUser为例：

    
    
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

**7）使用数据库用户访问指定库**

    
    
    $ mongo --port 27017 -u "accountUser" -p "password" --authenticationDatabase "products"

##  五、MongoDB安装

###  5.1. Windows下安装

MongoDB支持以下系统：

> Windows 7/Server 2008 R2
>
> Windows 8/2012 R2 and later

Windows 2012 Server和Windows
10需要安装[KB2999226](https://support.microsoft.com/en-us/help/2999226/update-for-universal-c-runtime-in-windows)用以提供C Runtime支持。

**1\. 下载安装文件**[MongoDB Download Center](https://www.mongodb.com/download-center/community?jmp=docs)![](_v_images/20190415160944306_22559.png)操作系统(OS)选择Windows
64-bit x64，然后点击`Download`按钮进行下载。

**2\. 安装MongoDB** 双击下载好的MSI文件开始安装，注意不要勾选“Install MongoDB as a
Service”。![](_v_images/20190415161520167_13746.png) **3\. 启动服务**
在C盘根目录下创建一个目录`data`，用于存放MongoDB数据文件。使用管理员权限开启CMD窗口，执行以下命令：

    
    
    "C:\Program Files\MongoDB\Server\4.0\bin\mongod.exe" --bind_ip 0.0.0.0 --port 27017 --dbpath="c:\data"

###  5.2. Ubuntu下安装

**1\. 添加MongoDB GPG公钥**

    
    
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4

**2\. 添加MongoDB软件源** 需根据Ubuntu版本添加软件源

**Ubuntu 14.04 (Trusty)**

    
    
    echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list

**Ubuntu 16.04 (Xenial)**

    
    
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list

**Ubuntu 18.04 (Bionic)**

    
    
    echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list

**3\. 更新软件包列表**

    
    
    sudo apt-get update

**4\. 安装MongoDB**

    
    
    sudo apt-get install -y mongodb-org

1.启动服务在/tmp目录下创建一个文件夹，用于存放MongoDB数据库文件（实际生产环境中根据需求指定MongoDB目录路径，严禁存放在/tmp目录下）。执行以下命令启动服务

    
    
    mongod --bind_ip 0.0.0.0 --port 27017 --dbpath /tmp/mongodb_test

##  六、各类工具检测漏报原因分析

###  6.1. Python脚本检测

网上流传的各类Python检测脚本，主要检测方式是以下两种：

1.一种检测方式是使用Python的PyMongo库，不使用账号密码连接MongoDB服务，连接成功则证明存在未授权访问漏洞。由于PyMongo库只支持MongoDB
2.6及之后版本，低版本MongoDB存在漏洞时无法发现。

2.另一种检测方式是使用socket与MongoDB服务端口建立连接后发送数据库查询指令，返回的数据中，存在默认库`local`，则表示数据库查询成功，存在未授权访问漏洞。在1.9版本的MongoDB服务中，报错信息中包含local字符，引起误报。

###  6.2. Nmap脚本

Nmap的mongodb-brute脚本，先判断是否开启验证，如果开启验证再判断是否存在弱口令。脚本运行的条件是端口为27017或服务名称为mongodb，由于Nmap端口检测结果中的服务名称是mongod，名称不一致，脚本不运行，存在漏报。另外脚本执行过程中，脚本执行出错，也会引起漏报。

该问题已向Nmap提交更新请求，检测非默认端口的MongoDB服务。<https://github.com/nmap/nmap/issues/1565>

##  七、Python检测脚本示例

    
    
    def mongodb(self, ip):
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, 27017))        s.send('\x3F\x00\x00\x00\x7E\x00\x00\x00\x00\x00\x00\x00\xD4\x07\x00\x00\x04\x00\x00\x00\x61\x64\x6D\x69\x6E\x2E\x24\x63\x6D\x64\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x18\x00\x00\x00\x10\x6C\x69\x73\x74\x44\x61\x74\x61\x62\x61\x73\x65\x73\x00\x01\x00\x00\x00\x00')
            result = s.recv(1024)
            if 'local' in result and 'errmsg' not in result:  #增加一个“errmsg”字符串判断，避免1.9版本中的误报。
                print(u'{}[+] {}:27017\tMongoDB存在未授权访问{}'.format(G, ip, W))
                with open('weakpass.txt', 'a+') as f:
                    f.write('{}\t27017\tMongoDB存在未授权访问\n'.format(ip,))
        except Exception as e:
            pass
        finally:
            s.close()
    
    
    mongodb_check("192.168.1.10","27017")

##  八、参考资料

账号管理命令

**修改用户权限**

    
    
    db.updateUser("root", {roles:[{role:"readWriteAnyDatabase", db:"admin"}] })

**修改用户密码**

    
    
    db.changeUserPassword(“username","newPasswd")

**删除用户**

    
    
    db.changeUserPassword(“username","newPasswd")

MongoDB内建角色：<https://docs.mongodb.com/manual/core/security-built-in-roles/>

认证相关官方文档该整改建议中命令方法在4.0版本中测试通过，低版本的MongoDB中，命令或角色定义可能有所变化，整改过程中，建议根据实际使用版本，查询MongoDB官方文档。

> <https://docs.mongodb.com/manual/core/authentication/>
>
> [MongoDB安装文档](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-> ubuntu/)
>
> [各版本MongoDB
> Windows服务端下载](https://www.mongodb.org/dl/win32/?_ga=2.143828661.1603721537.1555473312-1573747954.1553754766)

 ***本文原创作者：Shad0wpf_，本文属FreeBuf原创奖励计划，未经许可禁止转载**

