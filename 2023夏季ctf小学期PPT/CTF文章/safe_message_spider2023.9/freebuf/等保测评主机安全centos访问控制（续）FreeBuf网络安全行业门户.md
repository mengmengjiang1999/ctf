## 一、说明

**权限控制在等保测评里仅仅说了要求，但是怎么落地却基本没写，怎么说呢，比较抽象。所以，我觉得还是有必要了解一下centos系统大概有什么方法可以实现对用户的权限控制，不至于测评的时候完全不知道怎么测。这里我把我现在知道的关于权限控制的方法都列举出来，供大家参考参考。**

> 这里是访问控制的上一篇文章，大家可以先看看上一篇：
>
> [等保测评主机安全：CentOS访问控制](https://www.freebuf.com/articles/terminal/208657.html)

##  二、 更精细化的文件权限控制

一般的，对目录和文件，可以实现创建者、所属组、其他用户这三类用户（UGO）的访问权限设置(r、w、x)。而setfacl命令，则可以更为精确的在这三类用户之外对权限进行分配，叫做ACL权限设置。比如：让某一个用户对某一个文件具有某个权限。

与setfacl相对的，可以用getfacl查看设置好的ACL权限。

###  2.1. ACL

比如用getfacl命令来查看一个定义好了的ACL文件：

    
    
    [root@localhost ~]# getfacl ./test.txt
    #file: test.txt
    #owner: root
    #group: admin
    user::rw-    user:john:rw-    group::rw-    group:dev:r--    mask::rw-    other::r--
类型  |  说明  
---|---  
#file: test.txt  |  说明文件名为 test.txt  
#owner: root  |  说明文件创建者为root  
#group: admin  |  说明文件所属组为admin组  
user::rw-  |  定义了ACL_USER_OBJ, 说明文件创建者拥有read and write permission  
user:john:rw-  |  定义了ACL_USER,这样用户john就拥有了对文件的读写权限,实现了我们一开始要达到的目的  
group::rw-  |  定义了ACL_GROUP_OBJ,说明文件的所属组拥有read and write permission  
group:dev:r--  |  定义了ACL_GROUP,使得dev组拥有了对文件的read permission  
mask::rw-  |  定义了ACL_MASK的权限为read and write  
other::r--  |  定义了ACL_OTHER的权限为read  
  
这里稍微说明下，mask::rw-代表着这个文件的最大权限，在ACL中定义的用户、组的权限实际都不是真实权限，真实的权限是要跟mask的权限相与之后产生的权限。

如这个例子，mask的值为rw，所以定义的ACL的权限中，假如john的权限设置为rwx，那么那么它的最终权限就是与mask相与之后的结果，也就是rw。（当然，对于txt文件而言，执行权限没有啥意义）。

注：Mask只对其他用户和组的权限有影响，对owner和other的权限是没有任何影响的。

###  2.2. ACL与UGO

UGO也就是我们常用的文件权限模式，比如：-rwxr-xr-x. 1 root root 10688 11月 23 2013
/etc/init.d/iptables

而当你对某文件设置了ACL之后，再用ls命令查看UGO，就会发现多出一个+号：

    
    
    [root@localhost ~]# ls -l
    -rwxrwxr--+ 1 root admin 0 Jul 3 23:10 test.sh

并且其中原来代表group权限的权限位，被mask所替代，也就是说rwx **rwx** r--中的rwx不再代表group的权限，而是代表mask，用getfacl 查看如下：

    
    
    [root@localhost ~]# getfacl --omit-header ./test.sh 
    user::rwx user:john:rwx 
    group::rw- 
    mask::rwx
    other::r--
可以得知，group的实际权限是rw-。

###  2.3. 更多内容

实际上setfacl和getfacl相关的内容很多，我这里只是摘抄了一部分比较基础的，想要详细了解的可以点击：<https://www.cnblogs.com/MLibra/p/6240209.html>  
我这里就不继续摘抄了。

##  三、chroot命令

linux的目录结构如下：  
![](https://image.3001.net/images/20190827/1566898934_5d64faf6d5b17.png!small)

通过chroot命令可以将根目录设置为指定的位置，而根目录之上的位置将不可再访问，则这样就实现了一定的访问控制。

具体内容，大家可以看一看：<https://www.ibm.com/developerworks/cn/linux/l-cn-chroot/>

##  四、sudo命令

sudo命令可以允许用户以另外的某个用户的身份执行某些命令，它的配置文件为/etc/sudoers。

比如在sudoers文件中这样配置：

###  4.1. 常见形式

    
    
    beinan ALL=(root) /bin/chown, /bin/chmod

表示的是beinan用户可以在任何可能出现的主机名的主机中，可以切换到root下执行 /bin/chown ，可以切换到任何用户招执行/bin/chmod
命令，但切换的时候都需要输入beinan自己的密码。

如果是这样：

    
    
    beinan ALL=(root) NOPASSWD: /bin/chown,/bin/chmod

则beinan用户在任何可能出现的主机名的主机中，都可以切换到root下去执行/bin/chown命令，而且还不需要输入beinan用户自己的密码。（但执行chmod时还是需要beinan输入自己的密码）

所以在等号右边是一种这样的格式：

    
    
    授权用户 主机=[(切换到哪些用户或用户组)] [是否需要密码验证] 命令1,[(切换到哪些用户或用户组)] [是否需要密码验证] [命令2],[(切换到哪些用户或用户组)] [是否需要密码验证] [命令3]......

[(切换到哪些用户或用户组)]：如果不写，则默认为切换到root用户。如果是ALL ，则代表能切换到所有用户。与此相对应的，sudo命令有一个-u参数，以指定的用户作为新的身份。若不加上此参数，则预设以root作为新的身份。

[是否需要密码验证]：如果不写，则默认为要输入自己的密码。如果是NOPASSWD:，则代表不需要输入自己的密码。

    
    
    %beinan ALL=/usr/sbin/*,/sbin/*

这里加%号代表用户组，%和用户组名之间不能有空格。而/usr/sbin/*中最后的符号代表通配符，表示sbin目录下的的所有命令。

而且对于命令，还可以指定参数，比如：

    
    
    beinan ALL=/bin/more /etc/shadow

对于beinan用户，在这里只能用more命令查看/etc/shadow文件。

所以从上面的几个例子可以看到，sudo权限的控制粒度可以达到非常细的地步。

###  4.2. 别名

可以对用户、用户组、命令等设置别名（组），需要使用时直接引用这个别名（组）即可：

    
    
    User_Alias SYSADER=beinan,linuxsir,%beinan
    User_Alias DISKADER=lanhaitun
    Runas_Alias OP=root
    Cmnd_Alias SYDCMD=/bin/chown,/bin/chmod,/usr/sbin/adduser,/usr/bin/passwd [A-Za-z]*,!/usr/bin/passwd root
    Cmnd_Alias DSKCMD=/sbin/parted,/sbin/fdisk 注：定义命令别名DSKCMD，下有成员parted和fdisk ；
    SYSADER ALL= SYDCMD,DSKCMD
    DISKADER ALL=(OP) DSKCMD

> 第一行：定义用户别名SYSADER 下有成员 beinan、linuxsir和beinan用户组下的成员，用户组前面必须加%号；
>
> 第二行：定义用户别名 DISKADER ，成员有lanhaitun
>
> 第三行：定义Runas用户，也就是目标用户的别名为OP，下有成员root
>
> 第四行：定义SYSCMD命令别名，成员之间用,号分隔，最后的!/usr/bin/passwd root 表示不能通过passwd 来更改root密码；
>
> 第五行：定义命令别名DSKCMD，下有成员parted和fdisk ；
>
> 第六行：
> 表示授权SYSADER下的所有成员，在所有可能存在的主机名的主机下运行或禁止运行SYDCMD和DSKCMD下定义的命令（这里的禁止是指SYDCMD定义里的!符号）。更为明确的说，
> beinan、linuxsir和beinan用户组下的成员能以root身份运行 chown 、chmod
> 、adduser、passwd，但不能更改root的密码；也可以以root身份运行 parted和fdisk
> ，本条规则的等价规则是：beinan,linuxsir,%beinan
> ALL=/bin/chown,/bin/chmod,/usr/sbin/adduser,/usr/bin/passwd
> [A-Za-z]*,!/usr/bin/passwd root,/sbin/parted,/sbin/fdisk
>
> 第七行：表示授权DISKADER 下的所有成员，能以OP的身份，来运行 DSKCMD（所以op才是runas用户，目标用户？）
> ，不需要密码；更为明确的说 lanhaitun 能以root身份运行 parted和fdisk 命令；其等价规则是：lanhaitun
> ALL=(root) /sbin/parted,/sbin/fdisk

###  4.3. 注意

对于某些命令，是不能够给与用户执行权限的，否则就是给与全部权限了。

/bin/bash，如果给与了用户以root身份执行该命令的权限，用户就可以用sudo -s或sudo -i登录任何一个用户。

su命令，如果给与了用户以root身份执行该命令的权限，用户可以切换到任何一个账户。

PS：更多内容请上网搜索。

## 五、su命令

通过su命令可以从现有账户切换到其他账户，除了root，切换到其它账户都需要目标账户的密码。

所以，从表面上看来su命令起不到什么访问控制的作用，毕竟要切换到目标账户需要知道对方的密码，那还不如直接用目标账户来登录。

但是实际上，它还是存在一些访问控制的功能的。

在/etc/pam.d/su文件中，有如下内容：

    
    
    auth            sufficient      pam_rootok.so
    #Uncomment the following line to implicitly trust users in the "wheel" group.
    #auth            sufficient      pam_wheel.so trust use_uid
    #Uncomment the following line to require a user to be in the "wheel" group.
    #auth           required        pam_wheel.so use_uid
    auth            include         system-auth
    account         sufficient      pam_succeed_if.so uid = 0 use_uid quiet
    account         include         system-auth
    password        include         system-auth
    session         include         system-auth
    session         optional        pam_xauth.so

其中的#auth required pam_wheel.so
use_uid，如果取消注释，则代表所有位于wheel用户组的用户，都失去了su命令的使用权限，无法再通过su命令切换到其他账户上，这里的wheel用户组为系统自创的一个用户组。

另外，其中的#auth sufficient pam_wheel.so trust
use_uid，如果取消注释，则代表wheel组的用户为可信任的，wheel组的用户切换到其他账户不需要输入目标账户的口令，就像root一样。

如果想使用自定义的用户组，那么使用以下配置语句即可：

    
    
    auth            required        pam_wheel.so use_uid group=myadmingroup

##  六、环境变量

环境变量也算是访问控制的一种，我们常见的比如安装oracle数据库时，需要指定一个账户进行安装，一般将这个账户命名为oracle。  
这个账户就在~/.bash_profile文件中定义了某些环境变量：

    
    
    [oracle@centos01 ~]$ cat ~/.bash_profile
    #.bash_profile
    #Get the aliases and functions
    if [ -f ~/.bashrc ]; then
    	. ~/.bashrc
    fi
    #User specific environment and startup programs
    PATH=$PATH:$HOME/bin
    export PATH
    export ORACLE_BASE=/oracle
    export ORACLE_HOME=/oracle/app
    export ORACLE_SID=oracleSI
    export PATH=$ORACLE_HOME/bin:$PATH

这样一来，由于启动监听和oracle数据库的脚本里会用到其中定义的环境变量。

所以哪怕是root，没有配置环境变量，也没法启动启动监听和oracle数据库，因为相关脚本里需要使用的环境变量root账户没有进行定义。

这样，也就起到了一定的访问控制的功能。

##  七、结尾

这里列举的都是一些比较基本的centos中可能涉及到访问控制的点了，当然，肯定还有一些技术要么我自己压根不知道，或者我还没遇到过，所以没法列举出来。

这些内容都比较基础，但也很繁琐和复杂，所以我都是摘抄加修改，弄出一些比较基础、实用的知识点。

我觉得先做到：不一定有能进行设置，但是有能力看得懂别人的设置，这样就先可以了。

至于一些命令比如setfacl有一些比较奇怪的用法，有兴趣的可以自己去加大深度的学习。

 ***本文原创作者：起于凡而非于凡，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

