## **背景概述**

近日，深信服终端安全团队、深信服安服应急响应中心团队监控到一款Linux系统下活跃的挖矿木马，且出现大面积感染的情况，该挖矿木马采用GO语言编译，根据其行为特点，安全专家将其命名为WorkMiner挖矿木马。

该挖矿病毒入侵终端后会占用主机资源进行挖矿，影响其他正常业务进程的运转，传播过程中病毒文件会修改防火墙的规则，开放相关端口，探测同网段其他终端并进行SSH暴力破解，容易造成大面积感染。

![](https://image.3001.net/images/20210818/1629257448_611c7ee847c1ff9ad22aa.png!small)

/受感染主机出现的异常进程/

##  **病毒现象**

1、病毒启动后，会释放如下文件：

> /tmp/xmr (xmrig挖矿程序)
>
> /tmp/config.json (xmrig挖矿配置文件)
>
> /tmp/secure.sh (封禁爆破IP)
>
> /tmp/auth.sh (封禁爆破IP)
>
> /usr/.work/work64 (病毒母体文件)

2、病毒进程

> ./work32-deamon
>
> ./work64 -deamon
>
> /tmp/xmr
>
> /usr/.work/work32
>
> /usr/.work/work64
>
> /bin/bash /tmp/secure.sh
>
> /bin/bash /tmp/auth.sh

3、在 /var/spool/cron/crontabs/root 和 /etc/crontab 中创建计划任务：

![](https://image.3001.net/images/20210818/1629257475_611c7f038f53b6b5f1139.png!small)

4、修改防火墙规则，开放8000(udp) 和8017(tcp) 端口

![](https://image.3001.net/images/20210818/1629257490_611c7f121660d2aafb058.png!small)

5、/usr/bin/url、/usr/bin/wget 命令是否被重命名为/usr/bin/curl1和/usr/bin/wget1

![](https://image.3001.net/images/20210818/1629257504_611c7f206918b6d83201d.png!small)

##  **技术分析**

病毒样本加了UPX壳：

![](https://image.3001.net/images/20210818/1629257517_611c7f2d94b8e3b6f8b47.png!small)

该挖矿木马是采用go语言编译的，脱壳后看到了golang相关的字符串：

![](https://image.3001.net/images/20210818/1629257529_611c7f39c51cbb0fd051a.png!small)

经过解析后，函数列表如下：

![](https://image.3001.net/images/20210818/1629257540_611c7f44a173d8ddcbee1.png!small)

木马启动后会先终结竞争对手的进程

![](https://image.3001.net/images/20210818/1629257553_611c7f51dff45438bb387.png!small)![](https://image.3001.net/images/20210818/1629257566_611c7f5eab4c467d5d49d.png!small)

随后释放config.json、secure.sh、auth.sh、xmrig等恶意文件，其中xmrig为挖矿程序

![](https://image.3001.net/images/20210818/1629257578_611c7f6a88062df2a38d5.png!small)

随后启动ssh爆破线程，对同网段其他终端发起ssh爆破进行传播；

![](https://image.3001.net/images/20210818/1629257591_611c7f771987e48519376.png!small)![](https://image.3001.net/images/20210818/1629257599_611c7f7f096dc381ae73b.png!small)

连接P2P僵尸网络；

![](https://image.3001.net/images/20210818/1629257609_611c7f89dfd747c5a91d4.png!small)![](https://image.3001.net/images/20210818/1629257621_611c7f95184775df9793c.png!small)

##  **IOC**

 **矿池域名：**

> xmr.crypto-pool.fr

 **矿池账号：**

>
> 47BD6QNfkWf8ZMQSdqp2tY1AdG8ofsEPf4mcDp1YB4AX32hUjoLjuDaNrYzXk7cQcoPBzAuQrmQTgNgpo6XPqSBLCnfsjaV

 **MD5：**

> 06e1f988471336d788da0fcaa29ed50b
>
> 429258270068966813aa77efd5834a94
>
> 20552242cd4b5e8fa6071951e9f4bf6d

