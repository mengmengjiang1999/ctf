## 一、概述

腾讯安全威胁情报中心检测到有攻击者使用Hadoop Yarn REST
API未授权命令执行漏洞攻击云上主机，攻击成功后执行恶意命令，向系统植入挖矿木马、IRC
BotNet后门、DDoS攻击木马，入侵成功后还会使用SSH爆破的方式进一步向目标网络横向扩散。

攻击者入侵成功后，会清理系统进程和文件，以清除其他资源占用较高的进程（可能是可疑挖矿木马，也可能是正常服务），以便最大化利用系统资源。入侵者同时会配置免密登录后门，以方便进行远程控制，入侵者安装的IRC后门、DDoS木马具备完整的目标扫描、下载恶意软件、执行任意命令和对特定目标进行网络攻击的能力。

通过对木马家族进行关联分析，发现本次攻击活动与永恒之蓝下载器木马关联度极高，攻击者使用的攻击套件与Outlaw僵尸网络木马高度一致，但尚不能肯定攻击活动由这两个团伙发起。

因本次攻击具有蠕虫式的扩散传播能力，可下载安装后门、执行任意命令，发起DDoS攻击，对受害单位网络信息系统安全构成严重影响。腾讯安全专家建议用户尽快修复Hadoop
Yarn REST API未授权命令执行漏洞，避免采用弱口令，采用腾讯安全的技术方案检测系统，清除威胁。

Hadoop是一个由Apache基金会所开发的分布式系统基础架构，YARN是hadoop系统上的资源统一管理平台，其主要作用是实现集群资源的统一管理和调度，可以把MapReduce计算框架作为一个应用程序运行在YARN系统之上，通过YARN来管理资源。

YARN提供有默认开放在8088和8090的REST
API（默认前者）允许用户直接通过API进行相关的应用创建、任务提交执行等操作。在配置不当的情况下，REST
API将会开放在公网，从而导致未授权访问的风险，黑客可利用该风险进行远程命令执行，实现对目标主机的完全控制。

腾讯安全全系列产品，可以在该团伙攻击的各个环节实施检测、防御。

![](https://image.3001.net/images/20210129/1611882657_601360a1cf5331482e699.png!small)

## 木马清理&系统加固

腾讯安全专家建议受影响的用户检查以下项目，清除木马，加固系统。

目录：

/tmp/.W10-unix/.rsync/

计划任务项:

11*/2** /a/upd>/dev/null 2>&1

58**0 /b/sync>/dev/null 2>&1

@reboot /b/sync>/dev/null 2>&1

00*/3** /c/aptitude>/dev/null 2>&1

加固：

1.如果Hadoop环境仅对内网提供服务，请不要将其服务开放到外网可访问。

2.如果必须开启公网访问，Hadoop在2.X以上版本提供了安全认证功能，建议管理员升级并启用Kerberos的认证功能，阻止未经授权的访问。

## 二、样本分析

攻击者使用Hadoop
命令执行入侵成功后执行恶意的经过BASE64编码的shell脚本，解码后可知，其目的是使用sftp从sshapi.netcatkit.com内下载dota3.tar.gz包，将其解压后执行目录内的initall文件和golan文件。

/tmp/.W10-unix/.rsync/initall

/tmp/.W10-unix/.rsync/c/golan

![](https://image.3001.net/images/20210129/1611882690_601360c22706bb23d7018.png!small)

initall执行后则进一步对系统进程，文件进行清理，最终调用执行init2

![](https://image.3001.net/images/20210129/1611882700_601360cc0d05356ae9ab1.png!small)

Intit2执行后则执行解压包内的多个文件，分别存放在a,b,c三个子文件夹。a目录下文件多层调用后执行挖矿程序；b目录多层调用后传播IRC
BotNet后门木马，同时修改系统免密登录配置留下后门；c目录文件主要运行masscan做端口扫描，运行stsm（sshprank）进行暴力破解。同时将3个目录下的主调度文件写入crontab启动项。

![](https://image.3001.net/images/20210129/1611882708_601360d4c3bf73c9dfff9.png!small)

 **/.rsync/a/init0**

主要功能为从文件、进程、网络对其它资源占用较高的程序进行清理，最终调用脚本执行wanwakuang的矿机文件。

![](https://image.3001.net/images/20210129/1611882718_601360de2bca1c638be31.png!small)

 **/.rsync/a/a**

x86_64架构下执行挖矿wanwakuang，i686架构下执行anacron，但anacron模块并不存在，推测当前其挖矿平台覆盖度并不完善

![](https://image.3001.net/images/20210129/1611882728_601360e8af14c6d23a033.png!small)

wanwakuang则为xmr矿机程序，进行门罗币挖矿。

![](https://image.3001.net/images/20210129/1611882739_601360f33f92c0f16cb39.png!small)

 **/.rsync/b/a**

进一步执行/.rsync/b/run程序

![](https://image.3001.net/images/20210129/1611882748_601360fc13ce0b24de514.png!small)

 **/.rsync/b/run**

该脚本主要包含两部分BASE64编码过的恶意命令，第一部分解码后为使用Perl编写的IRC
BotNet木马，第二部分解码后主要为结束其它资源占用进程的shell命令，该文件同时会篡改authorized_keys文件进行免密登录后门配置。

![](https://image.3001.net/images/20210129/1611882759_601361073a24519276b05.png!small)

解码后Perl编写的IRC BotNet
木马，该木马会对C2地址：api.netcatkit.com:443建立IRC连接，本地NICK，USER随机生成，管理员NICK为polly，molly。IRC连接成功后默认加入#007频道，木马具备基本的远程shell命令执行，文件下载，ddos网络攻击等功能。

![](https://image.3001.net/images/20210129/1611882768_60136110c9340765a5c78.png!small)

  

![](https://image.3001.net/images/20210129/1611882778_6013611a170a9740d9828.png!small)

指定目标进行Shell命令执行

![](https://image.3001.net/images/20210129/1611882793_601361292e4c5ac7003f2.png!small)

指定目标端口扫描，指定下载

![](https://image.3001.net/images/20210129/1611882801_60136131ef10f16933b5d.png!small)

指定目标进行TCP，UDP，IGMP，ICMP类型流量攻击

![](https://image.3001.net/images/20210129/1611882810_6013613ae27e97ac1a0aa.png!small)

  

![](https://image.3001.net/images/20210129/1611882819_601361438960b7bb586ea.png!small)

 **/.rsync/c/golan**

调用masscan端口扫描工具和stsm暴力破解工具，对局域网内的开放的SSH服务进行暴破攻击，扫描时会首先获取本地SSH历史登录配置信息，通过直接攻击本地登录过的机器以提高其爆破成功率。

![](https://image.3001.net/images/20210129/1611882828_6013614cf1e760000bbc8.png!small)

  

![](https://image.3001.net/images/20210129/1611882838_601361562f217be72abbd.png!small)

分析可知，该挖矿攻击代码结构，调度流程与Outlaw僵尸网络高度一致，下左图为本次捕获到的挖矿套件，右为Outlaw僵尸网络攻击套件。两者有着基本一致的包名，子模块名，脚本调度流程。不同之处为两者挖矿模块名字不同，挖矿模块存储方式分别为本地包内存储化和动态C2下载形式，同时两者使用到的扫描器有些许差异。

![](https://image.3001.net/images/20210129/1611882846_6013615ee70d903968db8.png!small)

从其攻击方式和基础设施来看，更像是永恒之蓝家族投递，样本payload都使用netcatkit.com，sqlnetcat.com下的子域名进行托管，同时最终的包名，挖矿模块名有一致性。

下图为最近捕获的永恒之蓝下载器木马使用Hadoop Yarn REST
API未授权命令执行攻击入侵，其payload托管地址为t.netcatkit.com/ln.core

![](https://image.3001.net/images/20210129/1611882858_6013616a568b5507f5a3b.png!small)

永恒之蓝payload其内当前注释掉的代码部分，下载链接包解压后执行initall：down.sqlnetcat.com/dota3.tar.gz（当前下载链接失效），dota3.tar.gz同样解压出名为的.rsync攻击套件

![](https://image.3001.net/images/20210129/1611882867_6013617349a0da3374f30.png!small)

## IOCs

 **MD5:**

6eb76f7d81e899b29c03b8ee62d9acb3

be85068596881f3ebd6c0c76288c9415

10ea65f54f719bffcc0ae2cde450cb7a

4adb78770e06f8b257f77f555bf28065

eefc0ce93d254982fbbcd26460f3d10d

be5771254df14479ad822ac0a150807a

e46e8c74e2ae7d9bc2f286793fe2b6e2

c2531e3ee3b3ca43262ab638f9daa101

f093aae452fb4d8b72fe9db5f3ad559a

c97485d5ba33291ed09b63286a7d124c

3570a54d6dace426e9e8520f302fe551

 **Domain** **：**

sshapi.sqlnetcat.com

sshapi.netcatkit.com

sshapi.ouler.cc

api.netcatkit.com

www.minpop.com

t.netcatkit.com

down.sqlnetcat.com

 **URL** **：**

hxxp://www.minpop.com/sk12pack/names.php

hxxp://www.minpop.com/sk12pack/idents.php

## 参考链接：

亡命徒（Outlaw）僵尸网络感染约2万台Linux服务器，腾讯安全提醒企业及时清除

https://s.tencent.com/research/report/1021.html

永恒之蓝木马下载器再更新，云上主机成为新目标

https://mp.weixin.qq.com/s/953ZHaf8IjLGyxB3tWSoDQ

