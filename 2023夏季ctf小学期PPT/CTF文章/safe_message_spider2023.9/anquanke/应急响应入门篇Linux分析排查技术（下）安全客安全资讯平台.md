# 应急响应入门篇-Linux分析排查技术（下）

阅读量 **156988**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-24 10:30:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t015bc3fad101be7f66.jpg)

## 一、Linux分析排查技术

###  1- 异常用户分析排查

在Linux中root用户是一个无敌的存在，可以在Linux上做任何事情。

**新建用户 useradd username**  
 **  
设置密码 passwd username 输出密码**

设置用户uid和gid都为0，（root用户uid为0，gid为0）修改问即可/etc/

    
    
    cat /etc/passwd
    
    grep “0:0” /etc/passwd
    
    ls -l /etc/passwd
    
    awk -F: “$3==0”{print$1}’ /etc/shadow或awk -F:’length($2)==0{print$1}’ /etc/shadow

1.cat /etc/passwd //查看etc/passwd目录下的用户

![](https://p5.ssl.qhimg.com/t011484334f6844daac.png)

![](https://p3.ssl.qhimg.com/t01d9f66327c56f580b.png)

2.vim /etc/passwd 进入这个目录下，将test1的uid和gid改为0，0.

![](https://p0.ssl.qhimg.com/t01271cf34f1e653505.png)

3.新建用户 useradd username

设置密码 passwd username 输出密码

![](https://p4.ssl.qhimg.com/t01d326c79d12e0d1ae.png)

4.使用su test1 切换到test1用户下。

![](https://p5.ssl.qhimg.com/t01ae0f43c39c5e6e18.png)

5.使用grep “0:0” /etc/passwd来找gid和pid都为管理员用户的用户。

![](https://p1.ssl.qhimg.com/t01bb4fe73d22879436.png)

6.ls -l /etc/passwd 查看修改时间

![](https://p4.ssl.qhimg.com/t0187a868cd357b77e7.png)

7.还可以使用awk -F: “$3==0”{print$1}’ /etc/passwd或awk -F:’length($2)==0{print$1}’
/etc/passwd来对其进行查找

![](https://p3.ssl.qhimg.com/t01aeb7a18c8d354b73.png)

![](https://p0.ssl.qhimg.com/t0186946c2475ae95c7.png)

![](https://p3.ssl.qhimg.com/t01bef34995c24a93a5.png)

8.最后使用id来查看test1的用户属性

![](https://p4.ssl.qhimg.com/t019962f8bfdf9bd36d.png)

    
    
    Linux所有用户都会在/etc/passwd、/etc/shadow、/etc/group文件中记录
    
    cat /etc/passwd ：查看是否有其他uid，gid为0的情况
    
    less /etc/passwd：查看是否有新增用户
    
    grep :0 /etc/passwd：查看是否有特权用户
    
    ls -l /etc/passwd：查看passwd最后修改时间
    
    awk -F: 'length($2)==0 {print $1}' /etc/shadow：查看是否存在空口令用户
    

### 2-历史命令分析history

在Linux系统中默认会记录之前执行的命令 **/root/bash_history** 文件中

用户可以使用 **cat /root/bash_history** 进行查看或者使用history命令进行查看

特别注意:wget（可能下载远程木马）、ssh（连接内网主机）、tar zip 类命令（数据打包）、系统配置等（命令修改）

1.使用history可以查看历史命令。

![](https://p1.ssl.qhimg.com/t0110bc3a8fb0d280b8.png)

2.然后对其进行查找一些比较特别的命令如wget、ssh、tar，zip等等命令。

![](https://p2.ssl.qhimg.com/t013bcf25baf5969bc2.png)

###  3-计划任务排查-crontab

在Liunx系统中可以使用命令 **crontab** 进行计划任务的设定

其中-e 可以用来编辑设定计划任务，-l可以用来查看当前计划任务，-r用来删除计划任务。

**特别注意计划任务中未知内容。**

使用 **crontab -h** 查看帮助信息

![](https://p5.ssl.qhimg.com/t01cc54af8b340e13dc.png)

crontab -l 查看当前的计划任务。

![](https://p3.ssl.qhimg.com/t01d6bdb428f79d1469.png)

新建一个计划任务。

![](https://p0.ssl.qhimg.com/t01663574825a38b1f8.png)

然后把它保存到/bin/ls目录下。

![](https://p3.ssl.qhimg.com/t01f64003f4bcd537e3.png)

常见计划任务位置：

    
    
    /var/spool/cron/*
    /var/spool/anacron/*
    /etc/crontab
    /etc/anacrontab
    /etc/cron.*
    /etc/anacrontab
    /etc/rc.d/init.d/
    

### 4-开机启动项

在Linux（Debian）系统中，/etc/init.d/目录下保存着开机自启动程序的目录

用户可以直接使用/etc/init.d/程序名称查看status状态

使用update-rc.d 程序名称 disable 取消开机自启动。 enable开机启动

使用etc/init.d 查看开机自启动目录

![](https://p5.ssl.qhimg.com/t0132c6dbb102f74cbd.png)

查看apache2 开机启动项的状态

![](https://p1.ssl.qhimg.com/t01078fb7617d6fe1b8.png)

使用/etc/init.d/apche2 start 讲apache2 开启。

![](https://p4.ssl.qhimg.com/t01adc4ed9a608b1265.png)

再次查看它的状态值，发现已经启动了。

![](https://p1.ssl.qhimg.com/t01c20142d6fce09d89.png)

使用upadte-rc.d apache2 enbale 设置开机自启动。

![](https://p1.ssl.qhimg.com/t01cf9520b8f070bb01.png)

重启一次之后再次查看状态值。

![](https://p5.ssl.qhimg.com/t019c662c4aecf85a45.png)

![](https://p3.ssl.qhimg.com/t015059638b1d39af3b.png)

    
    
    常用命令：
    
    ls /etc/rc.d
    systemctl list-unit-files
    chkconfig --list [service_name]
    

###  5-$path变量异常

决定了shell将到那些目录中寻找命令或程序，PATH的值是一系列目录，当你运行一个程序时，LINux在这些目录下仅需搜寻编译连接。ls cd

![](https://p2.ssl.qhimg.com/t018ff846c1d25e5a16.png)

修改PATH export PATH=$PATH:/usr/locar/new/bin
本地终端中有效，重启后无效。在/etc/profile或/home/.bashrc(source~/.bashrc)才能永久生效。

![](https://p0.ssl.qhimg.com/t018991d8791b2e9658.png)

###  6-后门排查-rkhunter

Rkhunter具有如下功能：

1.系统命令检测、MD5校验

2.Rookit检测

3.本机敏感目录、系统配置异常检测

安装：apt install rkhunter

基本使用： rkhunter -check -sk

![](https://p4.ssl.qhimg.com/t01a987fd2b7845b384.png)

使用 rkhunter -check -sk 进行后门检测。

![](https://p5.ssl.qhimg.com/t01e36e80436522ec62.png)

![](https://p4.ssl.qhimg.com/t018068f2f30455c998.png)

![](https://p0.ssl.qhimg.com/t012c48c4b98e7d76ec.png)

要注意那些warning的一些目录。

![](https://p0.ssl.qhimg.com/t01cc70b4594504c287.png)

跑完程序之后，然后对可疑目录再次进行排查。

![](https://p1.ssl.qhimg.com/t015b76f53bc3d09254.png)

## 二、常用技巧：

**1.日志如果被软链接到`/dev/null`**  
1.删除log  
2.重启rsyslog

**2 如果文件/目录无法删除，可使用lsattr查看文件/目录属性，如果有-i属性可使用chattr -i去除**

**3 查找777的权限的文件：`find / \*.php -perm 777`，因为大部分黑客普遍喜欢直接赋于文件/目录777的权限**

**4 搜集SSH爆破字典：`grep "Failed password" /var/log/secure | awk {'print $9'} |
sor0t | uniq -c | sort -nr`**

**5 查看恶意文件里面的IP：`strings /usr/bin/.sshd | egrep '[1-9]{1,3}\.[1-9]{1,3}\.'`**

**6 根据特征删除指定进程：`ps aux|grep -v grep|grep "mysqlc"|awk '{print $2}'|xargs kill
-9`**

**7 获取进程id数组，并循环杀死所有进程**

    
    
    ps -ef|grep "java" | grep -v grep|awk '{print $2}'
    kill -9 `ps -ef|grep "java" | grep -v grep|awk '{print $2}'`
    for pid in $(ps -ef|grep "java" | grep -v grep|awk '{print $2}'); do
      echo $pid
      kill -9 $pid
    done
    

**8 隐藏进程查找：**  
进程都存在于内存中，而内存中的数据又都是写入到/proc/目录下，基于此可查找隐藏文件

    
    
    ps -ef | awk '{print}' | sort -n | uniq >1
    ls /proc | sort -n |uniq >2
    diff 1 2
    

另外，针对挖矿命令被劫持的情况下可以使用perf top -s pid,comm,dso,symbol来看到挖矿进程

**9 SEO文件搜索：`grep -ri baiduspider web_root_master`**

**10`netstat`被替换，可使用ss、lsof来替换**

**11`arp -a`：查看arp记录是否正常**

**12 关注Content-Length值：`awk '{if($10>5000000){print $0}}'
/var/log/httpd/access_log`**

**13 查看动态库是否被修改**

    
    
    echo $LD_PRELOAD
    busybox cat /etc/ld.so.preload
    

也可使用strace、ldd、readefl等命令

**14 利用iptables阻断通讯**

    
    
    iptables -A INPUT -s xmr.crypto-pool.fr -j DROP
    iptables -A OUTPUT -d xmr.crypto-pool.fr -j DROP
    

**15 文件监控**  
创建文件监控规则

    
    
    auditctl -w /etc/passwd -p war -k password_monitor
    

监听日志

    
    
    tail -f /var/log/audit/audit.log|grep password_monitor
    

**16 网页挖矿多数都是加载conhive.min.js，script标签里有miner.start关键字，全局查找即可**

**17 检查SSH后门**  
•对比ssh版本：ssh -V  
•查看ssh配置文件和/usr/sbin/sshd的时间:stat /usr/sbin/sshd  
•strings检查/usr/sbin/sshd，看是否有邮箱、IP等信息:strings /usr/bin/.sshd | egrep
‘[1-9]{1,3}.[1-9]{1,3}.‘  
•通过strace监控sshd进程读写文件的操作，一般的sshd后门都会将账户密码记录到文件，可以通过strace进程跟踪到ssh登录密码文件。

**18 清除僵尸进程**  
父进程调用fork创建子进程后，子进程运行直至其终止，它立即从内存中移除，但进程描述符仍然保留在内存中。

    
    
    ps -e -o stat,ppid,pid,cmd | grep -e '^[Zz]' | awk '{print $2}' | xargs kill -9
    

## 三、总结：

本文主要是紧接着之前的文章进行补充，主要是从异常用户分析、历史命令分析、计划任务排查、开机启动项、$path变量异常、后门排查-rkhunter等方面出发，来对linux系统进行全方面的应急响应。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Arthur** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/260049](/post/id/260049)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Linu应急响应](/tag/Linu应急响应)

 **+1** __7赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) Arthur

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

