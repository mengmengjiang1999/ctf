**前段时间公司发生了一起服务器入侵事件，在此分享给大家也顺便理顺下linux入侵应急响应思路。**

##  **一、事件描述**

某天监控同事反馈有台机器cpu飙高到2000%，可能机器已经被黑。于是登录上去查看，果然有个进程名为"HT8sUy71"的进程在作祟，这一看名字就不大可能是正常进程。

![1.png](https://image.3001.net/images/20190719/1563503943_5d312d470be46.png!small)

##  **二、处理过程**

###  **2.1 查杀病毒进程**

cpu占用率如此之高，基本可判断为挖矿程序无疑了，使用在线威胁情报系统对进程进行检测，不出所料，得出的标签是coinminer。这种挖矿进程一般都有自动重启机制，可能是某个进程的子进程，也可能在cron定时任务里出现。

首先，检查cron定时任务，发现/var/spool/cron/crontabs/root和/etc/cron.d/tomcat文件修改时间有变化，但是内容却无改动。

然后，使用ps
-ef进行查找主进程，并无收获。同时发现此挖矿进程正在和“172.105.114.84”这个ip的8443端口进行通信，可能是黑客的一台远控服务器。

![2.png](https://image.3001.net/images/20190719/1563504024_5d312d98ecf4b.png!small)

之后，lsof查看此进程在操作哪些文件，也无实际收获。

![3.png](https://image.3001.net/images/20190719/1563504052_5d312db4164e2.png!small)

推测一定是有某个主进程在工作，so,继续通过ps和netstat查找监听所监听端口的异常。果不其然，看到异常进程，正在批量爆破，看来是被当做肉鸡了。同时使用lsof查看此进程文件，发现在调用/root/.ddg/4003.db文件，貌似是个加密的社工库。

![4.png](https://image.3001.net/images/20190719/1563504080_5d312dd071765.png!small)

判断是此程序即是主程序，kill掉挖矿进程后，使用strace -T -tt -e
strace=full进行跟踪，发现主进程先对挖矿进程增加可执行权限，之后拉起进程。

![5.png](https://image.3001.net/images/20190719/1563504105_5d312de9ed3f0.png!small)![6.png](https://image.3001.net/images/20190719/1563504113_5d312df1d8570.png!small)

那么现在kill掉主进程吧，发生个小插曲，发现主进程pid一直在变化，好吧，直接killall osryfa3。

![7.png](https://image.3001.net/images/20190719/1563504135_5d312e0742b58.png!small)

至此，算是暂时消停一下，简单总结一下此病毒特征，其一方面释放挖矿病毒进行挖矿，同时又对公网ssh服务进行爆破以扩大感染面。在这里同时给了我一个提醒，或许这台服务器就是通过ssh爆破被入侵的。

###  **2.2 查找入侵痕迹**

一般情况下，入侵可能有以下几种方式：

> a.各种弱口令爆破
>
> b.系统漏洞的利用
>
> c.应用漏洞的利用

上面说了，可能是通过ssh爆破被入侵的，我们先来验证一下。

查看登录日志，发现异常(下图是已经过滤掉正常登录的日志)，基本可断定是通过ssh爆破入侵了，也可以断定ssh的访问控制已经失效。

    
    
    cat /var/log/secure* | grep Accepted

![8.png](https://image.3001.net/images/20190719/1563504155_5d312e1b94547.png!small)

结合以上ip查看爆破日志，确认以上ip的用户不是同一个人，是刚好有这么多ip同时爆破了root账户，而且最短的爆破时间只花了1分钟。想来这个root账户必然是个弱密码了。继续查找Failed日志的最早时间如下：

    
    
     cat /var/log/secure* | grep Failed 

![9.png](https://image.3001.net/images/20190719/1563504174_5d312e2ef0778.png!small)

基本可断定在这之前有人动过访问控制策略了，询问运维人员无果。。。。。

stats查看iptables、/etc/hosts.allow和/etc/hosts.deny文件状态，结合.bash_history命令，一切真相大白，一言难尽，你们自己体会。

![10.png](https://image.3001.net/images/20190719/1563504238_5d312e6e8fa2e.png!small)

###  **2.3 病毒文件的清理**

首先，使用stat查看上面两个进程的修改时间，大约在7月8号早上6点多，而ssh系统最早爆破时间是7月6号16:41。

![11.png](https://image.3001.net/images/20190719/1563504261_5d312e85ab02b.png!small)![12.png](https://image.3001.net/images/20190719/1563504269_5d312e8d06155.png!small)然后，结合这两个时间来查找敏感目录中被修改过的系统文件，进行检查修复和清除。

    
    
    find /etc/ /usr/bin/ /usr/sbin/ /bin/ /usr/local/bin/ /var/spool/cron/ -type f -mtime -3 | xargs ls -l  

![13.png](https://image.3001.net/images/20190719/1563504297_5d312ea9aff10.png!small)

最后 ，使用chkrootkit、clamav、rkhunter一通查杀，当然，还是重装系统最保险。

##  **三、总结**

首先啰嗦一下，关于linux主机，高危端口真得万万不能全网开放。看了日志后，发现黑客真是时时刻刻在爆破啊。

关于linux入侵的排查思路，总结如下：

### 1.查看异常进程活动-查找是否有异常进程和端口占用

1.1查找占用cpu最多的进程，相关命令：运行top命令后，键入大写字母P按cpu排序；

1.2查找占用内存最多的进程，相关命令：运行top命令后，键入大写字母M

    
    
    ps aux | sort -k4nr

1.3查找进程文件：

    
    
    ls -la /proc/$pid/exe

1.4跟踪异常进程运行情况：

    
    
    strace -tt  -T -e  trace=all  -p $pid

1.5查看进程打开的文件

    
    
    lsof -p $pid

1.6 查看进程端口情况

    
    
    netstat -anltp | grep $pid  
    

### 2.查看账号安全

2.1查看是否有存在新增异常账号：

a.查找特权用户

    
    
    awk -F ":" '$3==0{print $1}' /etc/passwd

b.查找可以远程登录的账号信息

    
    
    awk '/\$1|\$6/{print $1}' /etc/shadow

c.查找sudo权限账户

    
    
    cat /etc/sudoers | grep -v "^#\|^$" | grep "ALL=(ALL)"

2.2 查看是否有账号异常登录情况：

a.查看当前登录用户和其行为

    
    
    w

b.查看所有用户最后一次登录的时间

    
    
    lastlog

c.查看所有用户的登录注销信息及系统的启动、重启及关机事件

    
    
    last

d.查看登录成功的日期、用户名及ip

    
    
    grep "Accepted " /var/log/secure* | awk '{print $1,$2,$3,$9,$11}'

e.查看试图爆破主机的ip

    
    
    grep refused /var/log/secure* | awk {'print $9'} | sort | uniq -c |sort -nr | more
    
    grep "Failed password" /var/log/secure* | grep -E -o "(([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}))" | uniq -c 

f.查看有哪些ip在爆破主机的root账号

    
    
    grep "Failed password for root" /var/log/secure | awk '{print $11}' | sort

g.查看爆破用户名字典

    
    
    grep "Failed password" /var/log/secure | awk {'print $9'} | sort | uniq -c | sort -nr        

### 3.查找异常文件

3.1 查找cron文件中是否存在恶意脚本

    
    
    /var/spool/cron/*
    
    /etc/crontab 
    
    /etc/cron.d/* 
    
    /etc/cron.daily/* 
    
    /etc/cron.hourly/* 
    
    /etc/cron.monthly/* 
    
    /etc/cron.weekly/ 
    
    /etc/anacrontab     
    
    /var/spool/anacron/*

3.2 查看最近一段时间内被修改的系统文件

    
    
    find /etc/ /usr/bin/ /usr/sbin/ /bin/ /usr/local/bin/  -type f -mtime -T | xargs ls -la

3.3 按时间排序，确认最近是否有命令被替换，可以结合rpm -Va命令

    
    
    ls -alt /usr/bin /usr/sbin /bin /usr/local/bin
    
    rpm -Va>rpm.log  
    

3.4 确认是否有异常开机启动项

    
    
    cat /etc/rc.local
    
    chkconfig --list  
    

### 4.借助工具查杀病毒和rootkit

4.1 查杀rootkit

    
    
    chkrootkit (下载地址-http://www.chkrootkit.org)
    
    rkhunter (下载地址-http://rkhunter.sourceforge.net)

4.2 查杀病毒

    
    
    clamav(下载地址-http://www.clamav.net/download.html)  

4.3 查杀webshell

    
    
    cloudwalker(下载地址-http://github.com/chaitin/cloudwalker)

工具用法不再赘述，大家自行查阅。

 ***本文原创作者：xyl870612，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

