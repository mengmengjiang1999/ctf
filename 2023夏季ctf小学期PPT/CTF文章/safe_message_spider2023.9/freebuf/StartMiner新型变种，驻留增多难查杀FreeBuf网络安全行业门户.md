## 背景概述

近日，深信服安全团队捕获到StartMiner新型变种，该变种新增了结束杀软防护模块，并添加了更多的驻留项防止查杀，C2地址变更为bash.givemexyz.in。

该木马通过在服务器上创建多个定时任务、多个路径释放功能模块的方式进行驻留，并存在SSH暴力破解模块，下载并运行开源挖矿程序。

## 感染现象

通过$top发现进程dbused或dbusex高CPU占用；

![](https://image.3001.net/images/20201124/1606217659_5fbcefbbc66d8812be27f.png!small)

通过$ps aux查看有bash和python进程从恶意域名上下载脚本执行；

![](https://image.3001.net/images/20201124/1606217668_5fbcefc4896d76c439156.png!small)

通过$tail -f /var/log/syslog可以看到执行可疑命令：

![](https://image.3001.net/images/20201124/1606217677_5fbcefcd6270119e5f064.png!small)

## 驻留项

添加4个驻留项如下：

（1）bash启动项 ~/.bash_profile

在打开终端时将会执行该挖矿木马，注意需要到对应用户目录下清理bash_profile

cp -f -r -- /bin/bprofr /bin/dbused 2>/dev/null && /bin/dbused -c >/dev/null
2>&1 && rm -rf -- /bin/dbused 2>/dev/null

（2）crontab计划任务

第一个计划任务为下载脚本执行

![](https://image.3001.net/images/20201124/1606217712_5fbceff07cf707d5c3d21.png!small)

可能创建的crontab包括

/etc/cron.d/ngnix & apache/etc/cron.hourly & daily & weekly &
monthly/var/spool/cron/var/spool/cron/crontabs

查询得到计划任务如下：

![](https://image.3001.net/images/20201124/1606217728_5fbcf0002741229d753b9.png!small)![](https://image.3001.net/images/20201124/1606217742_5fbcf00e308f13818e355.png!small)

另一个计划任务pwnrig则是直接启动挖矿进程：

![](https://image.3001.net/images/20201124/1606217754_5fbcf01ad5cc54fb5feee.png!small)

（3）rc.d

![](https://image.3001.net/images/20201124/1606217775_5fbcf02f120155e7c4471.png!small)

（4）init.d

![](https://image.3001.net/images/20201124/1606217840_5fbcf0701c512749c1027.png!small)![](https://image.3001.net/images/20201124/1606217847_5fbcf0777707a8ec5626f.png!small)

（5）系统服务

![](https://image.3001.net/images/20201124/1606217862_5fbcf0863a65b297ecf60.png!small)

## 木马行为

该木马入侵主机后将在bash.givemexyz.in上下载shell脚本xms以及python脚本bb.py并执行。备用域名为bash.givemexyz.xyz，若无dns无法解析则链接备用地址205.185.113.12，194.156.99.30进行下载。

 **xms脚本执行流程如下：**

（1）筛选并结束现有的挖矿进程；

（2）结束杀软等防护（相关代码被注释，功能未开启）；

（3）在ssh的known_hosts中尝试连接其他主机（若已配置ssh免密登录则会扩散）；

（4）清空原有计划任务，写入新的计划任务；

（5）下载、校验、执行挖矿程序；

（6）下载SSH扫描爆破组件并执行；

（7）执行木马文件2start.jpg和xms。

bb.py脚本是根据系统平台类型下载对应的挖矿程序。

## 处置方法

（1）删除以下文件

/bin/bprofr

/bin/sysdr

/bin/crondr

/bin/initdr

/usr/bin/bprofr

/usr/bin/sysdr

/usr/bin/crondr

/usr/bin/initdr

/tmp/dbused

/tmp/dbusex

/tmp/xms

/tmp/x86_64

/tmp/i686

/tmp/go

/tmp/x64b

/tmp/x32b

/tmp/2start.jpg

# SSH传播

/tmp/sshcheck

/tmp/ssh_vuln.txt

/tmp/scan.log

/tmp/ip192.txt

/tmp/hxx

/tmp/p

/tmp/scan

/tmp/masscan

/tmp/.dat

/tmp/.checking

/tmp/good.tar.gz

/tmp/sshexec

/tmp/sshpass

/tmp/sparte.txt

（2）清理计划任务、bash_profile、rc*.d、init.d、service包含恶意文件的启动项;

过滤并删除包含dbused、dbusex的启动项;

过滤并删除包含bprofr、sysdr、crondr、initdr相关的启动项;

（3）结束相关进程

过滤并结束包含givemexyz、198.98.57.217、194.156.99.30的进程;

过滤并结束包含dbused、dbusex的进程;

过滤并结束包含lwp_download的进程（注意是否有正常任务使用lwp_download）

## IOC

> bash[.]givemexyz.in
>
> bash[.]givemexyz.xyz
>
> 205[.]185.113.12
>
> 194[.]156.99.30

