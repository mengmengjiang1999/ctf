## **前言**

redis是一个高性能的key-value数据库，也经常被使用，今天来看看redis里面有什么好的利用方式，其一是利用redis写入shell，第二个就是写入ssh公钥进行登录。

##  **FOfa语法**

> protocol="redis" && banner="redis_version" && port="6379”

##  **Redis简介**

Redis（Remote Dictionary Server )，即远程字典服务，是⼀个开源的使用ANSI
C语言编写、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库，并提供多种语言的API。从2010年3月15日起，Redis的开发工作由VMware主持。从2013年5月开始，Redis的开发由Pivotal赞助。

Redis是⼀个key-value存储系统，和Memcached类似，它支持存储的value类型相对更多，包括string(字符
串)、list(链表)、set(集合)、zset(sorted set —有序集合)和hash（哈希类型）。这些数据类型都支持
push/pop、add/remove及取交集并集和差集及更丰富的操作，而且这些操作都是原子性的。在此基础上，redis支持各种不同方式的排序。与memcached⼀样，为了保证效率，数据都是缓存在内存中。区别的是redis会周期性的把更新的数据写入磁盘或者把修改操作写入追加的记录文件，并且在此基础上实现了master-slave(主从)同步。

##  **Ubuntu apt安装**

    
    
    stall redis-serverredis-serverredis-cli

##  **Redis命令**

redis分为服务器端和客户端，服务端上执行的是客户端发送过来的命令，Redis在安装完成之后会有redis-cli。

    
    
    redis-cli -h host #免密登录redis-cli -h host -p port -a password #使用Redis密码登录Redis服务#与Redis服务器连接成功后 执行ping 会返回⼀个PONG

##  **Redis配置文件**

Redis的配置文件位于Redis安装目录下，文件名为 redis.conf(Windows名为
redis.windows.conf)。当然也可以通过指定配置文件来进行启动。列举⼀些重要的配置项进行说明。
![](https://image.3001.net/images/20220329/1648532757_62429d1541652dc7c08cc.png!small)

## **Redis漏洞利用**

###  **1）前置条件**

  * 将redis 绑定到 0.0.0.0 (⼀般会通过ssrf gopher进行利用)；

  * 没有绑定redis到任何地址将protected-mode参数为no；

  * 使用redis-server 启动redis服务 redis-cli 本地连接，启动成功。

![](https://image.3001.net/images/20220329/1648532843_62429d6bcf378dc987cec.png!small)将bind
改为 0.0.0.0  
![](https://image.3001.net/images/20220329/1648532856_62429d789abe9324c086c.png!small)

修改成功：  
![](https://image.3001.net/images/20220329/1648532868_62429d84bc847c3af1c58.png!small)

###  **2）启动攻击机 kali 进行连接**

Ubuntu(受害机) : 192.168.23.134

kali(攻击机) : 192.168.23.129
![](https://image.3001.net/images/20220329/1648532900_62429da4a9af5c5d9da56.png!small)

### **3）写入shell**

![](https://image.3001.net/images/20220329/1648532913_62429db15afb923d67736.png!small)![](https://image.3001.net/images/20220329/1648532926_62429dbe83d38bae94c86.png!small)  
![](https://image.3001.net/images/20220329/1648532934_62429dc6a0869f41c9953.png!small)  
成功写入。

###  **4）写入SSH公钥**

服务端的Redis连接存在未授权，在攻击机上能用redis-cli直接登陆连接，并未登陆验证。服务端存在.ssh目录并且有写入的权限。

在数据库中插入一条数据，将本机的公钥作为value,key无所谓，然后通过修改数据库的默认路径为/root/.ssh和默认的缓冲文件
authorized.keys,把缓冲的数据保存在文件里，这样就可以在服务器端的/root/.ssh下生成⼀个授权的key
在kali的/root/.ssh目录里生成ssh公钥key。![](https://image.3001.net/images/20220329/1648532950_62429dd630dd121729662.png!small)

将公钥导入key.txt文件，再把key.txt文件内容写入服务端Redis的缓冲里：

    
    
    (echo -e "\n\n"; cat /root/.ssh/id_rsa.pub; echo -e "\n\n") > /root/.ssh/key.txt cat /root/.ssh/key.txt | redis-cli -h 192.168.23.134 -x set huahua

-x代表从标准输入读取数据作为该命令的最后⼀个参数 ：

![](https://image.3001.net/images/20220329/1648532970_62429deab3cb60835c129.png!small)

使用kali连接服务端Redis,设置Redis的备份路径为/root/.ssh/和保存文件名为authorized_keys，并将数据保存在目标服务器上。

![](https://image.3001.net/images/20220329/1648532983_62429df76ef8aa63eeea5.png!small)  
![](https://image.3001.net/images/20220329/1648533002_62429e0a0b729ae4c54ca.png!small)

##  **小结**

可以看到，redis的两种利用方式，可以直接拿到shell，在内网中普遍使用。

