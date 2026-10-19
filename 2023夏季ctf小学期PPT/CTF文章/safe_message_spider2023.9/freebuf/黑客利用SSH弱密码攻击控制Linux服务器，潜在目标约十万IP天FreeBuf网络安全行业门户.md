## **一、概述**

**本周腾讯安全服务中心接到客户求助，客户部署的腾讯御界高级威胁检测系统发现SSH服务失陷感知信息，该公司安全管理人员及时联络腾讯安全专家协助分析威胁来源。**  

![1.png](https://image.3001.net/images/20190606/1559784678_5cf86ce6409d5.png!small)

腾讯安全工程师在征得客户同意后对客户机器进行远程取证，客户机部署在客户的私有云上，结合御界的关键日志，我们发现这是一起针对SSH服务器弱口令爆破攻击事件，由于发现及时，工程师及时协助客户进行隔离及杀毒，并未造成损失。

根据这一线索，腾讯安全御见威胁情报中心展开事件调查，结果发现，这是一起专业黑客组织发起的攻击事件：攻击者利用SSH弱口令爆破成功后会植入SSH后门以及IRCbot后门程序，并通过SSH弱口令在内网横向传播，受害机器接收远程指令安装（包括但不限于）挖矿、DDoS攻击模块。

该黑客组织使用的基础设施分布于多个国家，包括俄罗斯、美国、法国、罗马尼亚、荷兰、新加坡等，该组织的攻击目标同样遍布世界各地，潜在的攻击目标每天约十万个IP的量级。该组织控制的一个门罗币钱包已挖到近200个门罗币，市值约12万元人民币。

##  **二、详细分析**

根据腾讯御界日志记录，该黑客团伙在对目标SSH服务器进行多达4千次连接尝试，最终爆破弱密码成功。

![2.png](https://image.3001.net/images/20190606/1559784689_5cf86cf12b3bf.png!small)

由于受害SSH服务器使用了较弱的密码，在17点23分，黑客爆破成功

![3.png](https://image.3001.net/images/20190606/1559784696_5cf86cf8074e0.png!small)

我们从受害机器提取了两个病毒文件/dev/shm/.satan及/dev/shm/rp,经分析

.satan
下载54.37.70.249/ps并执行，ps是一款ssh服务端，程序启动后会监控本机22端口，修改SSH授权，允许黑客远程免密登录，需要在受害机器上存储黑客公匙。

![4.png](https://image.3001.net/images/20190606/1559784702_5cf86cfe8e650.png!small)

添加成功后把本机信息发送到黑客服务器，共内置三个服务器地址。

> zergbase.mooo.com
>
> 5.255.86.129 （荷兰）
>
> mage.ignorelist.com （美国）

rp是一段加密的perl代码

![5.png](https://image.3001.net/images/20190606/1559784708_5cf86d04d7cbe.png!small)

解密后可以看到是perl版的ircbot后门

![6.png](https://image.3001.net/images/20190606/1559784827_5cf86d7b4ad16.png!small)

C&C：146.185.171.227（荷兰）

![7.png](https://image.3001.net/images/20190606/1559784832_5cf86d80cae21.png!small)

后门功能包括flood攻击以及云执行代码。

![8.png](https://image.3001.net/images/20190606/1559784839_5cf86d8753573.png!small)

经分析发现，黑客目前会下发挖矿的shell程序，shell首先下载54.37.70.249/dota.tar.gz （该IP位于法国）

![9.png](https://image.3001.net/images/20190606/1559784845_5cf86d8d570c5.png!small)

解压后dota目录结构

![10.png](https://image.3001.net/images/20190606/1559784852_5cf86d9466f97.png!small)

执行dota/.rsync/initall，Install做一些清理准备工作后，执行init功能

![11.png](https://image.3001.net/images/20190606/1559784859_5cf86d9b78426.png!small)

Init中清理自身挖矿进程，并设置启动项

![12.png](https://image.3001.net/images/20190606/1559784864_5cf86da01a77c.png!small)

dota/.rsync/a目录结构

![13.png](https://image.3001.net/images/20190606/1559784870_5cf86da6521d3.png!small)

接着执行dota/.rsync/a/a，a脚本执行init0，init0是专门结束竞品的shell程序

![14.png](https://image.3001.net/images/20190606/1559784876_5cf86dac0a6a4.png!small)

挖矿程序启动后会结束大部分挖矿软件的进程,并删除其他挖矿软件相关文件，独占资源。

![15.png](https://image.3001.net/images/20190606/1559784881_5cf86db10ac5c.png!small)

继续执行anacron，anacron是基于xmrig2.14修改的linux平台挖矿木马

矿池：

>  _5.255.86.129:80 （荷兰）_
>
>  _107.191.99.221:80（monerohash.com，美国）_
>
>  _workforce.ignorelist.com_

![16.png](https://image.3001.net/images/20190606/1559784888_5cf86db87ccdc.png!small)

目前该钱包已经挖到195XMR，按20190605均价来算，市值约12万人民币

![17.png](https://image.3001.net/images/20190606/1559784894_5cf86dbe3813a.png!small)

执行dota/.rsync/b/a，b/a最终执行ps，ps是上面讲的ssh后门服务端，方便黑客远程免密ssh登录。

![18.png](https://image.3001.net/images/20190606/1559784902_5cf86dc6040a2.png!small)

接着执行c目录的start，联网下载要爆破的服务器地址，端口，以及一些字典

![19.png](https://image.3001.net/images/20190606/1559784909_5cf86dcd3d43b.png!small)

三个服务器轮询下载：

>  _46.101.113.206（俄罗斯）_
>
>  _141.85.241.113（罗马尼亚）_
>
>  _sez.strangled.net （美国）_

三个服务器上，路径/a/ xtr存放的是字典服务器地址，当前为202.136.170.27（新加坡），这个地址每隔几天都会更新。

202.136.170.27/a/a存放的是将要爆破的服务器地址和端口，目前列表中被攻击的IP超过3万个，爆破成功的，或爆破不成功的IP均会从列表中删除，被攻击的目标IP仍在不断更换和增加中。我们推测，每天潜在的攻击IP约为十万量级。

![20.png](https://image.3001.net/images/20190606/1559784918_5cf86dd61c0b5.png!small)

202.136.170.27/a/b存放的是弱口令字典

![21.png](https://image.3001.net/images/20190606/1559784925_5cf86ddd2a785.png!small)

执行目录下的tsm传入要爆破的IP和字典

![22.png](https://image.3001.net/images/20190606/1559784939_5cf86deb53935.png!small)

爆破成功后远程执行shell脚本

![23.png](https://image.3001.net/images/20190606/1559784949_5cf86df52835e.png!small)

下载执行54.37.70.249/rp以及54.37.70.249/.satan （54.37.70.249位于法国），在新受害机器上重复以上动作。

##  **三、安全建议**

本次事件由于发现及时，部署腾讯御界高级威胁检测系统的客户并未遭遇损失，但溯源发现每天约十万台SSH服务器被列入攻击目标。腾讯安全专家建议企业用户高度警惕，采取以下措施防止企业SSH服务器被该团伙入侵控制。

1、 用密钥登录，不要用密码登录

2、使用安全的密码策略，使用高强度密码，切勿使用弱口令，防止黑客暴力破解

3、开SSH只监听本地内网IP

4、尽量不给服务器外网IP

5、推荐部署腾讯御界高级威胁检测系统。御界高级威胁检测系统，是基于腾讯反病毒实验室的安全能力、依托腾讯安全在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。

![24.png](https://image.3001.net/images/20190606/1559784958_5cf86dfec3873.png!small)

企业管理员也可手动清除该病毒：

删除以下文件&目录：

> _/dev/shm/.satan_
>
>  _/dev/shm/rp_
>
>  _/tmp/.X13-unix_
>
>  _/tmp/dota_

删除启动项：

>  _/tmp/data/.rsync/a/upd_
>
>  _/tmp/data/.rsync/b/sync_

IOCs

 **Domain**

> zergbase.mooo.com
>
> sez.strangled.net
>
> mage.ignorelist.com
>
> workforce.ignorelist.com

 **IP**

> 46.101.113.206
>
> 141.85.241.113
>
> 202.136.170.27
>
> 103.248.211.198
>
> 54.37.70.249
>
> 5.255.86.129
>
> 146.185.171.227

 **URLs**

> http[:]//554.37.70.249/rp
>
> http[:]//554.37.70.249/dota.tar.gz
>
> http[:]//554.37.70.249/ps
>
> http[:]//54.37.70.249/anacron
>
> http[:]//54.37.70.249/cron
>
> http[:]//54.37.70.249/dota2.tar.gz
>
> http[:]//54.37.70.249/p1
>
> http[:]//54.37.70.249/rsync
>
> http[:]//54.37.70.249/sslm.tar.gz
>
> http[:]//54.37.70.249/.x15cache
>
> http[:]//54.37.70.249/tddwrt7s.sh
>
> http[:]//54.37.70.249/lan.sh
>
> http[:]//54.37.70.249/.satan
>
> http[:]//54.37.70.249/minloc.sh
>
> http[:]//202.136.170.27/a/b
>
> http[:]//202.136.170.27/a/a
>
> http[:]//46.101.113.206/a/xtr
>
> http[:]//141.85.241.113/a/xtr
>
> http[:]//sez.strangled.net/a/xtr
>
> http[:]//zergbase.mooo.com/dota.tar.gz
>
> http[:]//zergbase.mooo.com/hello
>
> http[:]//zergbase.mooo.com/t
>
> http[:]//5.255.86.129/sslm.tar.gz
>
> http[:]//5.255.86.129/dota.tar.gz
>
> http[:]//5.255.86.129/lan.sh
>
> http[:]//5.255.86.129/ml.tar.gz
>
> http[:]//5.255.86.129/hubble.tar.gz
>
> http[:]//5.255.86.129/minloc.sh

 **钱包**

>
> 45UcbvLNayefqNad3tGpHKPzviQUYHF1mCapMhgRuiiAJPYX4KyRCVg9veTmckPN7bDebx51LCuDQYyhFgVbUMhc4qY14CQ

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

