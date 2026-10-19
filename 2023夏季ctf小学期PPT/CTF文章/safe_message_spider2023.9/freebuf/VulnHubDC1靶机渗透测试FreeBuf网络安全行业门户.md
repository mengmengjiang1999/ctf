##  0x00 前言

 **在开始之前我们需要先配置一下环境，因不知道DC-1靶机的IP，所有我们需要将靶机和kali放在同一个局域网里面，我这里是桥接。**

##  0x01 探测目标

> kali：192.168.199.241

首先，我们先来探测一下目标机器的IP，这里有很多种方法，着重讲一下其中2种方法。

###  **（1）运行arp-scan识别目标的IP地址**

使用arp-scan -l命令探测同一区域中存活主机。

![](https://image.3001.net/images/20191026/1572075356_5db3f75c375fe.png!small)

###  **（2）使用netdiscover识别目标主机**

使用netdiscover -i eth0命令探测存活主机。

![](https://image.3001.net/images/20191026/1572075369_5db3f7692d078.png!small)

因我这只有一个虚拟机，所有192.168.199.203就说目标机器的IP。

##  0x02 枚举和初步搜索信息

我们利用Nmap执行全端口扫描

    
    
    Nmap -sV -p- 192.168.199.203

![](https://image.3001.net/images/20191026/1572075376_5db3f77075037.png!small)

可以看到开启了80端口，使用浏览器打开看一下。

![](https://image.3001.net/images/20191026/1572075384_5db3f778b04f2.png!small)

很明显，我们看到网站的cms，所以我们可以直接在网上搜索这个cms的漏洞利用方式

![](https://image.3001.net/images/20191026/1572075391_5db3f77f4fbbd.png!small)

##  0x03 漏洞利用

我们使用metasploit对漏洞进行利用

1.启动metasploit，搜索drupal模块。

![](https://image.3001.net/images/20191026/1572075398_5db3f78675382.png!small)

搜索这个类cms在msf中能进行利用的方法

以上有数个攻击模块，哪一个能用，就需要一个一个进行尝试了。

2.经测试采用2018的，配置好参数，开始攻击。

![](https://image.3001.net/images/20191026/1572075405_5db3f78d904f3.png!small)

3.在meterpreter中能进行的命令比较少，所有我们一般都直接进入系统下的shell

![](https://image.3001.net/images/20191026/1572075412_5db3f7945a6c2.png!small)

4.很显然这个shell虽然已经进入，但是这里并不是交互的shell，所以我们要进入交互式的shell

使用python反弹一个交互式shell

![](https://image.3001.net/images/20191026/1572075423_5db3f79f4d641.png!small)

5.因www-data权限很低，我们接下来开始提权。

使用suid提权

找到一个属于root的有s权限的文件

![](https://image.3001.net/images/20191026/1572075429_5db3f7a5bb59c.png!small)

查看find是否可以。

![](https://image.3001.net/images/20191026/1572075437_5db3f7ad13a04.png!small)

提权成功。

![](https://image.3001.net/images/20191026/1572075446_5db3f7b687816.png!small)

6.接下来我们开始寻找flag。

进入/home目录，发现flag4文件。

![](https://image.3001.net/images/20191026/1572075454_5db3f7be3b8f1.png!small)

![](https://image.3001.net/images/20191026/1572075459_5db3f7c3e1081.png!small)

继续查找敏感文件，在/var/www文件夹下发现flag1.txt，内容提示寻找站点的配置文件

![](https://image.3001.net/images/20191026/1572075465_5db3f7c9bbccb.png!small)

Drupal的默认配置文件为
/var/www/sites/default/settings.php，查看发现了flag2和数据库的账号密码，我们先进入数据库查看。

![](https://image.3001.net/images/20191026/1572075471_5db3f7cfddae6.png!small)

![](https://image.3001.net/images/20191026/1572075477_5db3f7d5be605.png!small)

![](https://image.3001.net/images/20191026/1572075484_5db3f7dc39761.png!small)

直接查找默认的Drupal user 表，发现admin用户。

![](https://image.3001.net/images/20191026/1572075493_5db3f7e55c4d6.png!small)

###  方法一

使用Drupal对数据库的加密方法，加密脚本位置在网站根目录下的scripts下

使用加密脚本加密新密码123456，生成加密密文

参考链接：<http://drupalchina.cn/node/2128>

> 1.站点路径下执行
>
> 2.php scripts/password-hash.sh 新密码
>
> 3.修改admin用户的密码，更新为新密码：123456

![](https://image.3001.net/images/20191026/1572075501_5db3f7edf3974.png!small)

![](https://image.3001.net/images/20191026/1572075511_5db3f7f741905.png!small)

尝试登录一下。

![](https://image.3001.net/images/20191026/1572075519_5db3f7ff21335.png!small)

###  方法二

在exploitdb中有一个针对Drupal 7版本的攻击脚本，可以增加一个admin权限的用户账号，使用此方法简便了破解admin的密码，更直接

查看Drupal版本,确定Drupal版本为7.24

    
    
    cat /var/www/includes/bootstrap.inc | grep VERSION

![](https://image.3001.net/images/20191026/1572075527_5db3f8076a179.png!small)

    
    
    msf > searchsploit drupal

攻击脚本适用于7.31以下，所以适合7.24版本

![](https://image.3001.net/images/20191026/1572075534_5db3f80e45b71.png!small)

利用drupal7.0版本漏洞增加有admin权限的用户：admin1/admin1

    
    
    python /usr/share/exploitdb/exploits/php/webapps/34992.py -t [http://192.168.199.203](http://192.168.199.203/) -u admin1 -p admin1

![](https://image.3001.net/images/20191026/1572075543_5db3f81731f4e.png!small)

查看users表，添加admin1成功

![](https://image.3001.net/images/20191026/1572075550_5db3f81e31060.png!small)

使用新添加的用户admin1/admin1登录网站，在content模块下，找到flag3

![](https://image.3001.net/images/20191026/1572075557_5db3f825ebc0d.png!small)

![](https://image.3001.net/images/20191026/1572075567_5db3f82f885e1.png!small)

查看/etc/shadow 文件，发现flag4用户，并且flag4用户可以登录并且有密码，所以存在flag4的根目录，我们可以使用 **hydra**
进行爆破

![](https://image.3001.net/images/20191026/1572075575_5db3f8376c0db.png!small)

> 1.-l 指定用户名
>
> 2.-P 加载密码字典（自定义)
>
> 3.ssh://ip 指定使用协议和ip地址
>
> 4.爆破密码为：flag4/orange

![](https://image.3001.net/images/20191026/1572075582_5db3f83ee22c9.png!small)

使用flag4用户可以通过ssh登录系统

> 1.ssh flag4@192.168.199.203
>
> 2.密码：orange

![](https://image.3001.net/images/20191026/1572075591_5db3f847db47d.png!small)

![](https://image.3001.net/images/20191026/1572075598_5db3f84e30601.png!small)

在flag4中提示在root根目录下存在，进入到root根目录/root下找到thefinalflag.txt文本文件

![](https://image.3001.net/images/20191026/1572075604_5db3f8546a78e.png!small)

自此五个flag全部找到，主要联系了命令和工具的使用，以及使用find命令找suid和提权。

 ***本文作者： MzHeader，转载请注明来自FreeBuf.COM**  
  

