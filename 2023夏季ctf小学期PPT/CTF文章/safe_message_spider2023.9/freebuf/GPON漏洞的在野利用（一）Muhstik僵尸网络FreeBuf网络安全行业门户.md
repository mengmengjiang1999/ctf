**自从本次 GPON 漏洞公布以来，10 天内已经有至少 5 个僵尸网络家族在积极利用该漏洞构建其僵尸军团，包括
mettle、muhstik、mirai、hajime、satori。时间之短、参与者之多，在以往 IoT 僵尸网络发展中并不多见。**

幸运的是，当前包括 muhstik、mirai、hajime、satori
在内的其中大部分僵尸网络的攻击载荷经测试实现有问题，并不能真正植入恶意代码；mettle 虽然能够植入恶意代码，但 C2
服务器短暂出现后下线了。无论如何，由于这些恶意代码团伙在积极更新，我们仍应对他们的行为保持警惕。

muhstik 僵尸网络由我们首次批露（ [报告-2018-04](https://blog.netlab.360.com/botnet-muhstik-is-actively-exploiting-drupal-cve-2018-7600-in-a-worm-style/) ）。本次 muhstik
的更新中增加了针对包括 GPON 在内三个漏洞的利用。本轮更新后 muhstik 共有 10 种漏洞检测模块。

到北京时间 5 月 9 日，360 网络安全研究院联合安全社区关闭了部分服务器，部分减缓了 muhstik 的扩张速度。然而 muhstik
扩张的脚步并未停止，在 2018-05-10 10:30 GMT+8，我们观察到它启用了 165.227.78.159
替代被关闭的报告服务器，当前我们正在与安全社区协作采取后续行动。

##  **多个僵尸网络正在积极利用最近公开的 GPON 漏洞**

5 月 1 号，VPN Mentor 披露了 GPON Home Routers 的两个漏洞，分别是了 CVE-2018-10561 认证绕过漏洞和
CVE-2018-10562 命令执行漏洞。经过对已公开 PoC 的分析，我们能够确定该漏洞利用简单有效，影响面很广，并预期会被僵尸网络用来扩展其僵尸军团。

从第二天（5 月 2 号）开始，360 网络安全研究院就陆续看到有僵尸网络在利用该漏洞扩展感染范围。到 5 月 10 日，我们累积捕获并分析了 5
个家族的恶意代码在利用这些漏洞。

按 360 网络安全研究院观测到的时间顺序，这些僵尸网络分别是：

> · **mettle** ：一个恶意代码团伙，利用在越南的 IP 地址（C2 210.245.26.180:4441，scanner
> 118.70.80.143）和 mettle 开源攻击在积极植入恶意代码。这是该团伙首次进入我们的视野；
>
> · **muhstik** ： muhstik 僵尸网络由我们首先批露（
> [报告-2018-04](https://blog.netlab.360.com/botnet-muhstik-is-actively-> exploiting-drupal-cve-2018-7600-in-a-worm-style/) 。在这次更新中，muhstik 增加了对
> GPON（CVE-2018-10561，CVE-2018-10562）、JBOSS（CVE-2007-1036）和 DD-WRT（web
> 认证爆破）的三个漏洞的利用；
>
> · **不止一个 mirai 变种** ：[mirai 僵尸网络](https://blog.netlab.360.com/tag/mirai/) 自
> 2016 年 9 月开源以后，被数以百计的恶意团伙利用。这次我们观察到，其中不止一个团伙正在积极利用该漏洞传播 mirai 变种；
>
> · **hajime** ：我们就 hajime 僵尸网络已经发布了两份报告（
> [报告-2017-09](https://blog.netlab.360.com/hajime-status-report/) ，
> [简报-2018-03](https://blog.netlab.360.com/quick-summary-port-8291-scan-cn/)
> ）。本次 hajime 也做了更新，开始感染本次 GPON 漏洞相关设备。
>
> · **satori** ：[Satori 僵尸网络](https://blog.netlab.360.com/tag/satori/) 由 360
> 网络安全研究院首次公开披露，其在 2017-12 月中曾经用 12 小时感染了 26 万设备，创下了观测到 IoT 僵尸网络感染速度的记录。既往关于
> satori 我们发布了多份报告（ [报告-2017-11](https://blog.netlab.360.com/early-warning-a-> new-mirai-variant-is-spreading-quickly-on-> port-23-and-2323-2/)，[报告-2017-12](https://blog.netlab.360.com/wa-a-new-> mirai-variant-is-spreading-in-worm-style-on-port-37215-and-52869/)，
> [报告-2018-01](https://blog.netlab.360.com/art-of-steal-satori-variant-is-> robbing-eth-bitcoin-by-replacing-wallet-address/)）。通过本次更新，Satori 僵尸网络也加入到瓜分
> GPON 漏洞易感设备的行列。

下文集中描述 muhstik 僵尸网络。

##  **muhstik 僵尸网络基本情况**

![](https://image.3001.net/images/20180511/15260322942186.png!small)

图 1

上图是 muhstik 僵尸网络的结构示意：

> · **扫描阶段** ： **muhstik.scanner** 会发起扫描，并利用漏洞迫使 GPON 易感设备向报告服务器汇报状态；
>
> · **感染阶段** ： **muhstik.infector** 会利用漏洞迫使 GPON
> 易感设备从下载服务器下载恶意软件并安装。安装成功后设备即成为 muhstik bot，成为僵尸网络的一部分；
>
> · **控制阶段** ： **muhstik.c2.list** 会向 bot 发起指令，要求其执行扫描、SSH 横向扩展、xmrig
> 挖矿、cgminer 挖矿或者发起 DDoS 攻击。

##  **muhstik 僵尸网络的本次更新 - 扫描阶段**

muhstik 本轮新增了 3 种漏洞检测模块，目前共有 10 种漏洞检测模块。其中新增的 3 种漏洞检测模块如下:

> 1\. Gpon（CVE-2018-10561 & CVE-2018-10562）
>
> 2\. JBoss（CVE-2007-1036）
>
> 3\. DD-WRT（web 认证爆破）

与之对应的上报 URL 分别如下:

![](https://image.3001.net/images/20180511/15260323037074.png!small)

图 2

在上报服务器（51.254.219.134）被安全社区清除之后，上报服务器 ip 地址更新为 165.227.78.159。

目前 GPON 上报 URL 更新为:

![](https://image.3001.net/images/20180511/152603231591.png!small)

图 3

##  **muhstik 僵尸网络的本次更新 - 感染阶段**

在感染阶段，muhstik 探测到 GPON 易感染设备之后，试图迫使其下载 muhstik.tsunami 僵尸网络样本，以及
muhstik.aioscan 扫描模块。发起扫描的 IP 地址 muhstik.loader 没有变化，仍然是 51.254.219.137。

GPON 漏洞的扫描载荷如下：

![](https://image.3001.net/images/20180511/15260323243275.png!small)

图 4

![](https://image.3001.net/images/20180511/15260323334304.png!small)

图 5

![](https://image.3001.net/images/20180511/15260323442878.png!small)

图 6

##  **muhstik 僵尸网络的本次更新 - 恶意代码样本**

Gpon 和 JBOSS 的漏洞检测代码体现在 aiomips 样本中（5c55d50c10f2b500b0fbcd4ade2b18ea）：

![](https://image.3001.net/images/20180511/15260324138977.png!small)

图 7

![](https://image.3001.net/images/20180511/15260324211779.png!small)

图 8

DD-WRT 的漏洞检测代码体现在 aioarm 样本中（b9c8c709c89b2f9d864aa21164d25752）

![](https://image.3001.net/images/20180511/15260324293600.png!small)

图9

##  **安全社区联合行动及更新**

到北京时间 5 月 9 日，我们联合安全社区关闭了若干服务器，部分减缓了 muhstik 的扩张速度，包括：

![](https://image.3001.net/images/20180511/15260324377234.png!small)

图 10

然而 muhstik 扩张的脚步并未停止，当前（2018-05-10 10:30 GMT+8）我们观察到它启用了 165.227.78.159
替代被关闭的报告服务器。我们正在与安全社区协作采取后续行动。

新的恶意软件 url

![](https://image.3001.net/images/20180511/15260324466674.png!small)

图11

##  **IoC - muhstik**

State Report URL List

![](https://image.3001.net/images/20180511/15260324545859.png!small)

图 12

Malware Download URL List

![](https://image.3001.net/images/20180511/15260324602329.png!small)

图 13

C2 List

![](https://image.3001.net/images/20180511/15260324679841.png!small)

图 14

All IP list

![](https://image.3001.net/images/20180511/15260324747985.png!small)

图 15

曾经在 muhstik 控制之下，但已经被安全社区清除的 IP 列表：

![](https://image.3001.net/images/20180511/15260324824888.png!small)

图16

##  **IoC - mettle**

C2 and Scanner

![](https://image.3001.net/images/20180511/15260325974606.png!small)

***本文作者：360 网络安全研究院，转载请注明来自 FreeBuf.COM**

