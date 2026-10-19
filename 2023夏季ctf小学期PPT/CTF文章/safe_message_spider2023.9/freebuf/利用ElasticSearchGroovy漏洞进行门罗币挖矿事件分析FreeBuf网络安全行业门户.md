## 一、概述

 **2019年6月13日，安天蜜网捕获到利用CVE-2015-1427(ElasticSearch
Groovy)远程命令执行漏洞的攻击行为。该漏洞原理是Elaticsearch将groovy作为脚本语言，并使用基于黑白名单的沙盒机制限制危险代码执行，但该机制不够严格，可以被绕过，从而导致出现远程代码执行的情况。我们对此次事件进行了详细的样本分析，并给出预防及修复建议。**

## 二、样本分析

### 2.1 关键攻击载荷

从攻击载荷来看，攻击者通过groovy作为脚本语言，向_search?pretty页面发送一段带有恶意链接为<http://185.181.10.234/E5DB0E07C3D7BE80V520/init.sh>的json脚本，进行恶意shell脚本下载，从而实现远程代码攻击，并进行挖矿行为

![1561513329_5d12cd71dc3f2.png!small](https://image.3001.net/images/20190626/1561513329_5d12cd71dc3f2.png!small)

图 2-1 数据包内容

解密后核心代码：

![1561513337_5d12cd798aef6.png!small](https://image.3001.net/images/20190626/1561513337_5d12cd798aef6.png!small)

图 2-2 核心代码

### 2.2 样本分析

1) 入侵脚本分析—init.sh

攻击者通过<http://185.181.10.234/E5DB0E07C3D7BE80V520/init.sh>下载并执行恶意脚本init.sh来植入Dog挖矿程序，同时对主机进行扫描等一系列操作。

![1561513348_5d12cd8400c5d.png!small](https://image.3001.net/images/20190626/1561513348_5d12cd8400c5d.png!small)

图 2-3 关闭防火墙

之后执行关闭防火墙、关闭selinux并释放占用的资源、杀掉其他与挖矿相关的进程、设置定时任务（每30分钟下载一次可执行文件update.sh），获取ssh权限，进行iptables规则转发修改，同时清理相关操作历史、日志等操作。

![1561513355_5d12cd8b2a528.png!small](https://image.3001.net/images/20190626/1561513355_5d12cd8b2a528.png!small)

图 2-4 检查并杀死其它存在的挖矿进程

![1561513362_5d12cd927732a.png!small](https://image.3001.net/images/20190626/1561513362_5d12cd927732a.png!small)

图 2-5 设置定时任务

![1561513370_5d12cd9a4a952.png!small](https://image.3001.net/images/20190626/1561513370_5d12cd9a4a952.png!small)

图 2-6 恶意脚本下载地址、备份地址以及大小设置

![1561513378_5d12cda26286d.png!small](https://image.3001.net/images/20190626/1561513378_5d12cda26286d.png!small)

图 2-7 清理相关日志、历史

在此过程中，脚本会检查sysupdate、networkservice 和sysguard这3个进程是否启动，如果没有则进行启动。

![1561513385_5d12cda9174dc.png!small](https://image.3001.net/images/20190626/1561513385_5d12cda9174dc.png!small)

图 2-8 当其中一个被kill掉后，调度文件重新启动

2) 样本分析—sysguard、networkservice、sysupdate

三个样本为go语言编写并使用UPX加壳，对应的main_main函数结构分别如下：

![1561513399_5d12cdb779203.png!small](https://image.3001.net/images/20190626/1561513399_5d12cdb779203.png!small)

图 2-9 sysguard-main_main函数结构

![1561513409_5d12cdc1d9b2b.png!small](https://image.3001.net/images/20190626/1561513409_5d12cdc1d9b2b.png!small)

图 2-10 networkservice-main_main函数结构

![1561513417_5d12cdc9bc6a8.png!small](https://image.3001.net/images/20190626/1561513417_5d12cdc9bc6a8.png!small)

图 2-11 sysupdate-main函数

通过与之前捕获的systemctI样本对比发现，此次攻击分成挖矿、扫描、函数调用三个进程进行调度。并且在networkservice样本中发现了相关漏洞利用函数和扫描函数。

![1561513425_5d12cdd1c6d80.png!small](https://image.3001.net/images/20190626/1561513425_5d12cdd1c6d80.png!small)

图 2-12 networkservice扫描函数

通过对比之前捕获的样本发现两次攻击手法类似，不同的是此次攻击是通过sysguard、networkservice（扫描）和sysupdate三个进程共同进行的。这也意味着，发现服务器被感染后要将这三个进程同时kill掉。

3) 配置文件—config.json

在下载的配置文件中，我们发现了多个矿池地址：

表 2-1 矿池列表

![1561513435_5d12cddb83f73.png!small](https://image.3001.net/images/20190626/1561513435_5d12cddb83f73.png!small)

![1561513443_5d12cde30ba55.png!small](https://image.3001.net/images/20190626/1561513443_5d12cde30ba55.png!small)

图 2-13 s配置文件

## 三、受影响的服务及漏洞

表 3-1 受影响的服务和漏洞

![1561513455_5d12cdef6732f.png!small](https://image.3001.net/images/20190626/1561513455_5d12cdef6732f.png!small)

## 四、IOC

表 4-1 攻击IP

![1561513464_5d12cdf80be55.png!small](https://image.3001.net/images/20190626/1561513464_5d12cdf80be55.png!small)

表 4-2 URL

![1561513472_5d12ce003e390.png!small](https://image.3001.net/images/20190626/1561513472_5d12ce003e390.png!small)

表 4-3 MD5

![1561513477_5d12ce05e6490.png!small](https://image.3001.net/images/20190626/1561513477_5d12ce05e6490.png!small)

## 五、预防与修复建议

### 预防建议：

> a) 确保系统与应用程序及时下载更新为官方提供的最新补丁；
>
> b) 禁止使用弱口令密码；
>
> c) 定期检查服务器异常，如CPU持续占用高、磁盘异常情况；
>
> d) 安装终端威胁安全防护产品

### 修复建议：

> a) 断网、备份重要的crontab，关闭或删除定时任务：systemctl stop crontab或 rm -rf /etc/cron.d/*；
>
> b) 锁定crontab中的恶意文件；
>
> c) 查看并杀掉病毒进程：同时杀掉sysguard、networkservice、sysupdate三个进程；
>
> d) 删除病毒相关文件；
>
> e) 确认无误后，重启服务器，安装漏洞补丁。

## 附录一：参考链接

> [1] Reversing GO binaries like a
> pro：<https://rednaga.io/2016/09/21/reversing_go_binaries_like_a_pro/>

 ***本文作者：antiylab，转载请注明来自FreeBuf.COM**

