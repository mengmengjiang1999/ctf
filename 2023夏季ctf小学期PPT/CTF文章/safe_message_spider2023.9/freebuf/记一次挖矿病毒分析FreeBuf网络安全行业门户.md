***本文作者：lostCooky，本文属 FreeBuf 原创奖励计划，未经许可禁止转载**

## 前言

 **上午接到同事通知，有客户中了挖矿病毒，所以通过 ssh 登陆服务器检查，简单记录后遂有此文。**

## 阶段一：从发现脚本到删除脚本

1、使用`top`命令查看系统运行情况，发现多个名为sustse的进程占用 cpu 资源过高。

![阶段一：从发现脚本到删除脚本](https://image.3001.net/images/20181031/1540980101_5bd97d8500b8e.png!small)

2、使用`whereis sustse`和`which sustse`命令查找此命令位置,发现未找到。

![阶段一：从发现脚本到删除脚本](https://image.3001.net/images/20181031/1540980107_5bd97d8baeefb.png!small)

3、使用`find / -name sustse`命令查找文件是否存在,此时找到文件在/var/tmp/sustse下面,且同目录下面有另外两个文件

![阶段一：从发现脚本到删除脚本](https://image.3001.net/images/20181031/1540980117_5bd97d95daa7a.png!small)

![阶段一：从发现脚本到删除脚本](https://image.3001.net/images/20181031/1540980127_5bd97d9f04412.png!small)

发现这个文件时我就比较干脆，结束进程，删除文件.但是没一会进程有出现了。

## 阶段二：从脚本再次出现到彻底清除

1、使用命令`ps -anx | grep sustse`查看与sustse相关的进程。此时我就懵了为啥删除了文件，还会出现呢。突然想起来之前打 CTF
是用的一种利用定时任务启动的后门。

![阶段二：从脚本再次出现到彻底清除](https://image.3001.net/images/20181031/1540980169_5bd97dc99f271.png!small)

2、使用命令`crontab -l`查看是否有定时任务，发现里面有这个一条。

![阶段二：从脚本再次出现到彻底清除](https://image.3001.net/images/20181031/1540980175_5bd97dcf8316e.png!small)

3、我比较直接，记录下来后直接删除，然后删除文件，结束进程。等待一会看看进程是否会再次启动。一段时间后发现挖矿脚本已经被清除。

![阶段二：从脚本再次出现到彻底清除](https://image.3001.net/images/20181031/1540980185_5bd97dd914881.png!small)

## 阶段三：脚本分析

脚本下载地址：<http://www.tionhgjk.com:8220/mr.sh>

1、脚本内容一

![阶段三：脚本分析](https://image.3001.net/images/20181031/1540980194_5bd97de247ba1.png!small)

> 结束部分进程，删除一些文件。具体目的没有搞懂，这里做个猜测会不会是之前版本的地址发生了变化，现在要干掉这些；
>
> 删除一些文件。

2、脚本内容二

![阶段三：脚本分析](https://image.3001.net/images/20181031/1540980202_5bd97dea98bd7.png!small)

判断文件是否存在，如果存在就验证sustse文件的MD5值判断这文件是不是他的。如果不存在就给变量 DIR 赋值为"/var/tmp"

![阶段三：脚本分析](https://image.3001.net/images/20181031/1540980214_5bd97df66dd33.png!small)

判断命令`curl`和`wget`是否存在。

3、脚本内容三

![阶段三：脚本分析](https://image.3001.net/images/20181031/1540980227_5bd97e0307279.png!small)

downloadIfNeed函数判断是否需要下载sustse文件，如果需要就调用 download 函数。

4、脚本内容四

![阶段三：脚本分析](https://image.3001.net/images/20181031/1540980278_5bd97e36c5bcd.png!small)

> download 函数判断 sustse3文件是否存在或者sustse3文件的 MD5值是否符合，不符合或者文件不存在就调用 download2；
>
>
> download2函数,判断系统是不是64位，如果是就从[http://www.tionhgjk.com:8220/tte2](http://www.tionhgjk.com:8220/tte2%E4%B8%8B%E8%BD%BD%EF%BC%8C%E4%B8%8B%E8%BD%BD%E4%BD%8D%E7%BD%AE%E5%9C%A8/var/tmp/sustse%E3%80%82)下载，下载位置在/var/tmp/sustse；
>
> 验证 sustse 的MD5值，如果 MD5值符合，就改名为sustse3。

5、脚本内容五

![阶段三：脚本分析](https://image.3001.net/images/20181031/1540980286_5bd97e3e0cfeb.png!small)

> judge 函数下载 <http://www.tionhgjk.com:8220/wt.conf> 到/var/tmp/wc.conf；
>
> 使用nohup 启动 sustse，且在后台运行；
>
> judge2函数，使用nohup 启动 sustse，且在后台运行。

6、脚本内容六

![阶段三：脚本分析](https://image.3001.net/images/20181031/1540980296_5bd97e48e175e.png!small)

使用 crontab 创建定时任务。

## 查看sustse运行配置文件

![查看sustse运行配置文件
](https://image.3001.net/images/20181031/1540980307_5bd97e535349e.png!small)

发现有一个 GitHub
地址，查看之后发现是门罗币的挖矿程序。查询tionhgjk.com的注册信息发现域名的注册日期是2018-10-06T19:45:40.00，但是没有找到更多信息。

至此结束！

 ***本文作者：lostCooky，本文属 FreeBuf 原创奖励计划，未经许可禁止转载**

