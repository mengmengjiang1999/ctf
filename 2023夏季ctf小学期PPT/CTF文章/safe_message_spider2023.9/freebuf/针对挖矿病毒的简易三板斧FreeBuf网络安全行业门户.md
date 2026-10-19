## **一. 简介**

本文只基础说明遇到挖矿病毒的简单快速的处理思路，现实生产中遇到的病毒复杂的多。当企业面对病毒攻击的时候，一定要尽快交予专业安全人士处理，减少损失。

###  **二. 实现过程（研究内容）**

以linux系统为例，对中毒主机进行断网隔离后，查找挖矿病毒的基本操作：

1寻找进程，使用命令：Top

2删除进程，使用命令：kill -i PID

3删除文件，使用命令：rm -rf

后续处理：溯源分析，修补漏洞，安全加固

##  **三. 检测方式（防御建议）**

挖矿病毒特征：最大的特征就是主机的cpu资源占用，可以直接使用top命令查看进程来发现可疑进程。一般情况下，cpu使用居高不下的就是挖矿进程了。

根据进程的pid找到进程的文件路径，然后删除文件，杀死进程

![v2-1e523272a84d022e194ffacaf9cc1c37_720w.png](https://image.3001.net/images/20210916/1631760055_6142aeb77e9bb45241da9.png!small)

图1：确认挖矿进程

删除进程，命令：kill -9 PID

![v2-d3ec869b3f01b96e13c2d24fc74b9e10_720w.png](https://image.3001.net/images/20210916/1631760055_6142aeb7e12be40a15f0e.png!small)

图2：进程清除

寻找文件，命令：ls -l /proc/PID/exe

删除文件，命令：rm -rf

![v2-33313f360c846007a8dafde6ee5d1d92_720w.png](https://image.3001.net/images/20210916/1631760056_6142aeb83b3adefbb412b.png!small)

图3：寻找并删除恶意文件

如果你不确定文件是否有毒，那可以将可疑文件上传到在线沙箱，如微步和virustotal。要是文件已经没了，你可以把进程dump下来再上传。

![v2-a306a82932f03e9ac70754f1e2a6a1ca_720w.jpg](https://image.3001.net/images/20210916/1631760056_6142aeb8989e5665a68cb.jpg!small)

图4：在线沙箱结果

到这只是针对挖矿进程的基本处理，后续还要做这几件事。

1检查网络连接是否有C2通信，查看是否有其他非正常连接

重点关注防火墙iptables，命令：iptables -L -n

2检查最近修改的文件，避免遗漏，因为挖矿病毒，往往还携带者其他病毒或工具包

命令：find /etc -ctime -2 （命令解释：指定目录/etc，且近2天内的新增文件）

3修补漏洞并加固系统

3.1你可以使用上述提到的沙箱确定病毒的家族，然后使用搜素引擎确认使用的漏洞， 并与自己的系统做比对

3.2通过病毒的行为确认漏洞。最常见的就是爆破各种服务的弱口令和未授权等。

 **列举处理中会遇到的一些问题，推荐几个小技巧**

使用top命令时，未发现cpu占用率高的进程？

1.系统命令被修改:

建议直接去其他正常主机上下载命令源文件至感染主机上

2使用busybox工具替代系统的命令:

存在守护进程监视操作行为，发现敏感操作挖矿程序自动停止

多试几次top命令，因为卡顿等原因有时会看到未来得及退出的进程，很实用。

预加载so文件，隐藏进程

>
> 请参考往期公众号文章，[https://mp.weixin.qq.com/s/Vu568MO03nHYgYznsLkC3w](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Vu568MO03nHYgYznsLkC3w)

 **删除文件和进程后，过段时间再次出现？**

病毒采用了持久化的防护，要仔细检查启动项，计划任务，守护进程

1.查看计划任务，命令：cat /etc/crontab。计划任务文件有很多，不要看漏。

/etc/crontab；/var/spool/cron；/etc/anacrontab；

/etc/cron.d/；/etc/cron.daily/；/etc/cron.hourly/；

/etc/cron.weekly/；/etc/cron.monthly/；/var/spool/cron/

2.查看启动项

CentOS7以下版本：chkconfig –list；

CentOS7及以上版本：systemctl list-unit-files；

关闭启动项

CentOS7以下版本：chkconfig 服务名 off；

CentOS7及以上版本：systemctl disable 服务名；

启动项文件有很多，不要看漏。

/usr/lib/systemd/system；/usr/lib/systemd/system/multi-user.target.wants

/etc/rc.local；/etc/inittab；/etc/rc[0-6].d/；/etc/rc.d/

