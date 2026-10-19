## 0x0 背景介绍

 **近期，深信服安全团队捕获到Rocke
Group黑产团伙运营的新挖矿病毒，该病毒通过ssh爆破、ssh免密登录、redis未授权访问漏洞以及redis弱密码爆破、jenkins远程代码执行漏洞以及jenkins弱口令爆破和ActiveMQ远程代码执行漏洞进行传播的挖矿病毒。**

## 0x1 现象分析

机器上存在恶意的定时任务/var/spool/cron/crontabs/root

![1.png](https://image.3001.net/images/20200401/1585726614_5e84449656708.png!small)

存在恶意启动项sshservice

![2.png](https://image.3001.net/images/20200401/1585726715_5e8444fb17bbb.png!small)

/etc/crontab以及/etc/bashrc中被写入恶意命令![3.png](https://image.3001.net/images/20200401/1585726732_5e84450c28cbc.png!small)

## 0x2 病毒逻辑详细分析

### 1\. 病毒为go语言编译而成，并且使用了变异的UPX加壳逃避杀软，该病毒母体使用了5个主要的package

github.com/hippies/LSD/LSDA——病毒相关配置初始化

github.com/hippies/LSD/LSDB——文件释放

github.com/hippies/LSD/LSDC——Linux权限维持

github.com/hippies/LSD/LSDD——攻击与传播包

Main——攻击入口点

### 2\. github.com/hippies/LSD/LSDB——文件释放

![5.png](https://image.3001.net/images/20200401/1585726893_5e8445ad86519.png!small)

 **2.1 释放劫持库文件到/usr/local/lib/xxx.c，然后进行编译**

该劫持库源代码被gzip格式压缩打包在病毒文件中，32位程序这里可以使用binwalk进行提取，64位手动提取。

![6.png](https://image.3001.net/images/20200401/1585726942_5e8445ded5994.png!small)

![1583914788\(1\).png](https://image.3001.net/images/20200401/1585726980_5e84460406513.png!small)

将该so路径写入/etc/ld.so.preload文件，实现libc预加载，达到劫持的目的。该so主要劫持函数如下表

![1583914894\(1\).png](https://image.3001.net/images/20200401/1585727083_5e84466b20906.png!small)

 **2.2 创建sshservice启动项github_com_hippies_LSD_LSDB_NetdnsWrite**

释放服务bash模板文件到/etc/init.d/sshservice，该bash文同样被gzip格式压缩打包在病毒文件中，创建sshservice系统服务

![7.png](https://image.3001.net/images/20200401/1585727117_5e84468d974b2.png!small)

释放Systemd配置文件到以下三个目录，创建sshservice的Systemd服务

![1583915006\(1\).png](https://image.3001.net/images/20200401/1585727141_5e8446a531ace.png!small)

![8.png](https://image.3001.net/images/20200401/1585727154_5e8446b234277.png!small)

 **2.3 释放挖矿github_com_hippies_LSD_LSDB_KWR**

挖矿程序同样也被gzip压缩打包在病毒中，按顺序解压并释放到以下其中一个目录，运行后删除自身文件

![1583915092\(1\).png](https://image.3001.net/images/20200401/1585727214_5e8446eedd36f.png!small)

![9.png](https://image.3001.net/images/20200401/1585727225_5e8446f9b1554.png!small)

从其配置文件可以看出，该挖矿病毒进行门罗币挖矿，并且其使用了两中连接方式，一种是代理矿池，另一种是直接连接矿池进行挖矿。

![10.png](https://image.3001.net/images/20200401/1585727243_5e84470b477fc.png!small)

目前该矿池总共收益2.7个币

![11.png](https://image.3001.net/images/20200401/1585727259_5e84471b0f52f.png!small)

### 3\. Github.com/hippies/LSD/LSDC——linux权限维持

 **3.1 获取用于创建定时任务时所需要的域名**

![1583915334\(1\).png](https://image.3001.net/images/20200401/1585727427_5e8447c309221.png!small)

 **3.2 屏蔽其他组织的恶意域名**

向/etc/hosts文件中写入对应的IP-域名对，实现屏蔽。这里针对的主要是web2tor节点以及对应的一些矿池

![1583915381\(1\).png](https://image.3001.net/images/20200401/1585727458_5e8447e253edc.png!small)

 **3.3 执行下载bash命令，创建定时任务，污染bastrc文件实现启动**

![1583915475\(1\).png](https://image.3001.net/images/20200401/1585727483_5e8447fb6bd39.png!small)

污染的bashrc，执行的pygo文件为python文件

![12.png](https://image.3001.net/images/20200401/1585727529_5e844829ca028.png!small)

### 4\. github.com/hippies/LSD/LSDD——攻击与传播包

 **4.1 github_com_hippies_LSD_LSDD_Arun**

利用ssh爆破实现自身的传播，用到了1000个密码对root账户进行爆破，下表只列出部分密码

![1583915917\(1\).png](https://image.3001.net/images/20200401/1585727573_5e844855f0299.png!small)

 **4.2 github_com_hippies_LSD_LSDD_Brun**

利用Redis未授权访问、 Redis弱口令爆破，将恶意bash写入定时任务文件，实现感染

![1583916091\(1\).png](https://image.3001.net/images/20200401/1585728122_5e844a7aaba26.png!small)

爆破成功，设置redis数据库数据

![1583916147\(1\).png](https://image.3001.net/images/20200401/1585728169_5e844aa993194.png!small)

写入如下恶意bash数据到定时文件

![1583916206\(1\).png](https://image.3001.net/images/20200401/1585728188_5e844abc3141a.png!small)

 **4.3 github_com_hippies_LSD_LSDD_Crun**

利用Jenkins远程代码执行漏洞实现感染

![1583916298\(1\).png](https://image.3001.net/images/20200401/1585728261_5e844b051b9ea.png!small)

对Jenkins进行弱密码爆破实现感染，仅列出部分密码对

![1583916364\(1\).png](https://image.3001.net/images/20200401/1585728279_5e844b1767bd7.png!small)

 **4.4 github_com_hippies_LSD_LSDD_Drun**

ActiveMQ任意文件写入漏洞(CVE-2016-3088)，本次样本中其会将文件上传并且移动到Linux定时任务文件，实现感染

![1583916477\(1\).png](https://image.3001.net/images/20200401/1585728315_5e844b3bc1633.png!small)

### 5\. 关联分析：

 **5.1 域名IP关联**

通过aliyun.one可以关联到systemten.org域名

![13.png](https://image.3001.net/images/20200401/1585728359_5e844b678ae52.png!small)

systemten.org在之前已经被指出为kerberods挖矿病毒，通过对kerberods的感染方式，权限维持等方式进行对比，可以确认本次的aliyun.one与kerberods挖矿家族为同一个团体在运营。该团队在之前被Unit42团队披露为Rocke
Group黑产团伙。

 **5.2 差异对比**

![1583916602\(1\).png](https://image.3001.net/images/20200401/1585728396_5e844b8c2747c.png!small)

## 0x3感染方式

1、ssh弱口令爆破

2、ssh免密登录

3、redis未授权访问漏洞

4、redis弱口令爆破

5、Jenkins弱口令爆破

6、Jenkins远程代码执行漏洞(CVE-2018-1000861、CVE-2019-1003000)

7、ActiveMQ任意文件写入漏洞(CVE-2016-3088)

## 0x4防护

1、更改密码为强密码，密码每个机器不同

2、ssh免密登录要严格控制机器

3、加强redis防护，开启redis的密码验证，且密码更换未强密码

4、检测是否存在Jenkins弱密码，修改密码未强密码

5、检测是否存在jenkins远程代码执行漏洞并进行修复

6、检测是否存在ActiveMQ任意文件写漏洞。

7、检测是否存在Confluence未授权访问漏洞(CVE-2019-3396)

## 0x5 IOC

F81137FF4ED563101B3ACB8185CF16D5AF89C9E5

52AA4166F256495250C9191670DB258794059277

update.iap5u1rbety6vifaxsi9vovnc9jjay2l.com

x64.iap5u1rbety6vifaxsi9vovnc9jjay2l.com

cron.iap5u1rbety6vifaxsi9vovnc9jjay2l.com

aliyun.one

pool.supportxmr.com

sg.minexmr.com

iap5u1rbety6vifaxsi9vovnc9jjay2l.com

img.sobot.com/chatres/89/msg/20191225/1/ec0991da601e45c4b0bb6178da5f0cc4.png

img.sobot.com/chatres/89/msg/20191225/1/50659157a100466a88fed550423a38ee.png

cdn.xiaoduoai.com/cvd/dist/fileUpload/1577269944760/2.637890910155951.png

cdn.xiaoduoai.com/cvd/dist/fileUpload/1577269966297/8.872362655092918.png

<https://user-images.githubusercontent.com/56861392/71443284-08acf200-2745-11ea-8ef3-509d9072d970.png>

<https://user-images.githubusercontent.com/56861392/71443285-08acf200-2745-11ea-96c3-0c2be9135085.png>

钱包地址：

48tKyhLzJvmfpaZjeEh2rmWSxbFqg7jNzPvQbLgueAc6avfKVrJFnyAMBuTn9ZeG4A3Gfww512YNZB9Tvaf52aVbPHpJFXT

Ref:

<https://v2ex.com/t/624351>

<https://www.f5.com/labs/articles/threat-intelligence/vulnerabilities--exploits--and-malware-driving-attack-campaigns-in-december-2019>

<https://blog.trendmicro.com/trendlabs-security-intelligence/cve-2019-3396-redux-confluence-vulnerability-exploited-to-deliver-cryptocurrency-miner-with-rootkit/>

<https://unit42.paloaltonetworks.com/rockein-the-netflow/>

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

