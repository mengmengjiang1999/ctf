**近日，深信服安全团队追踪到公有云上及外部Linux服务器存在大量被入侵，表现为/tmp临时目录存在watchdogs文件，出现了crontab任务异常、网络异常、系统文件被删除、CPU异常卡顿等情况，严重影响用户业务。多个用户邀请深信服安全专家远程排查，最终经过分析确认，用户Linux服务器被植入新型恶意挖矿蠕虫，且较难清理。**

深信服安全团队将其命名为WatchDogsMiner，并紧急发布预警，提醒企业用户及时开展自查修复，防范WatchDogsMiner挖矿蠕虫。

 **病毒名称** ：WatchDogsMiner

 **病毒性质** ：挖矿蠕虫

 **影响范围** ：国内不少用户受感染，包括公有云用户

 **危害等级** ：高危

 **传播方式** ：基于Redis未授权访问、集成SSH爆破实现内外网的蠕虫式传播。

##  **0x01 如何确认是否中毒**

通过服务器终端进行检查发现部分常用命令被删除后出现未找到命令：

![01.png](https://image.3001.net/images/20190223/1550890492_5c70b5fcc89d2.png!small)

authorized_keys文件被清空无法使用免密登录：

![02.png](https://image.3001.net/images/20190223/1550890508_5c70b60cb3ca2.png!small)

系统内置的mail邮箱也出现相关的通知类邮件，查看发现有定时任务的通知与相关的命令：

![03.png](https://image.3001.net/images/20190223/1550890571_5c70b64b32b39.png!small)

在计划任务的相关路径下发现一个root的计划任务：

![04.png](https://image.3001.net/images/20190223/1550890603_5c70b66b80a6d.png!small)

使用 **深信服安全感知平台** 的用户，安全感知平台主动提示主机出现虚拟货币挖矿、数据库扫描、SSH暴力破解等多个安全事件：

![05.png](https://image.3001.net/images/20190223/1550890622_5c70b67ec63cf.png!small)

##  **0x02 病毒分析**

[1]WatchDogsMiner整体比较复杂，病毒母体为一个sh脚本，来自pastebin.com/raw/sByq0rym；

[2]sh脚本主要做了两个操作，净化主机环境，然后下载并运行挖矿病毒体；

[3]挖矿病毒是一个elf文件，从thyrsi.com/t6/672/1550667479x1822611209.jpg处下载得到；

[4]挖矿病毒使用go语言编写，病毒会通过SSH和Redis未授权访问进行传播，然后以守护进程的方式进行挖矿，挖矿的币种为门罗币。

![06.png](https://image.3001.net/images/20190223/1550890726_5c70b6e6debf2.png!small)

###  **WatchDogsMiner** **挖矿毒体分析**

WatchDogsMiner病毒程序是由go语言编写的elf文件，程序包含了网络通信模块、加密算法、Redis攻击、SSH暴力破解、挖矿等自实现功能。

详细分析如下：

启动，执行pastebin上保存的母体脚本：

![07.png](https://image.3001.net/images/20190223/1550890747_5c70b6fb55dc5.png!small)

![08.png](https://image.3001.net/images/20190223/1550890778_5c70b71a143b0.png!small)

将挖矿模块写入/tmp/ksoftirqds并执行。

 **Redis** **攻击模块：**

![09.png](https://image.3001.net/images/20190223/1550890803_5c70b7335dec4.png!small)![10.png](https://image.3001.net/images/20190223/1550890833_5c70b7519b5e6.png!small)

 **SSH** **暴力破解模块：**

![11.png](https://image.3001.net/images/20190223/1550890849_5c70b76140adb.png!small)

###  **母体脚本功能分析**

定时指定链接，执行母体脚本，并结束其他挖矿进程：

![12.png](https://image.3001.net/images/20190223/1550890856_5c70b768a620c.png!small)

修改所需要操作的目录属性，删除定时任务及服务，清理billgates病毒相关进程和文件：

![13.png](https://image.3001.net/images/20190223/1550890868_5c70b77469639.png!small)

更新挖矿木马：

![14.png](https://image.3001.net/images/20190223/1550890878_5c70b77eefbc3.png!small)

最后进行清理工作：

![15.png](https://image.3001.net/images/20190223/1550890890_5c70b78aa2550.png!small)

##  **0x03 解决方案**

###  **WatchDogsMiner** **病毒清理：**

1.删除恶意动态链接库/usr/local/lib/libioset.so；

2.清理 crontab 异常项，删除恶意任务(无法修改则先执行4-a)；

3.使用kill命令终止挖矿进程；

4.排查清理残留的病毒文件；

> a.chattr -i /usr/sbin/watchdogs /etc/init.d/watchdogs/var/spool/cron/root
> /etc/cron.d/root
>
> b.chkconfig watchdogs off
>
> c.rm -f /usr/sbin/watchdogs /etc/init.d/watchdogs

5.相关系统命令如netstat等可能被病毒删除，建议重新进行安装恢复；

6.由于文件只读且相关命令被hook，需要安装busybox并使用busybox rm命令删除；

7.部分操作需要重启机器生效。

###  **WatchDogsMiner** **病毒防御：**

1.为 Redis 添加密码验证；禁止外网访问Redis；以低权限运行Redis服务。（重启 Redis 才能生效。）

2.更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

3.深信服下一代防火墙、终端检测响应平台（EDR）均有防爆破功能。下一代防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能可进行防御。

4.深信服下一代防火墙客户，建议升级到AF805版本，并开启SAVE安全智能检测引擎，以达到最好的防御效果。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知平台+下一代防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

