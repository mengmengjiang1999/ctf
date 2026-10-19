## **概述**

近日，深信服威胁情报团队在云蜜罐中捕获到 **Sysrv-hello**
挖矿家族的最新变种，作者于7月10日和7月21日进行了多次更新，该病毒家族的攻击模块达到了18个，在本次更新中，新增了 **SSH爆破、PostgreSQL
RCE（CVE-2019-9193）** 和 **Struts2 RCE（CVE-2017-5638）**
攻击模块，进一步扩大了影响范围和危害，目前监测到失陷主机数量正呈上升趋势。

 **Sysrv-hello**
家族最早出现于2020年12月份，至今其版本迭代已数十次，不断的新增攻击模块，是一个新型且十分活跃的家族。在最新的威胁情报分析中，我们发现了其最新发展之一，包括前置Payload去除了卸载云主机安全软件的模块以及新的自建钱包地址，并且其入侵手法基本覆盖到大多数政企单位常用的Web服务，危害严重，深信服威胁情报团队提醒相关运维人员及时更新补丁做好防护。

###  **本次关键更新**

1\. 前置Payload去除了之前新增的卸载云主机安全软件模块和a.py和BrowserUpdat.exe模块；（疑似版本回溯）

2\. 删除部分漏洞利用模块，并新添SSH爆破、PostgreSQL RCE（CVE-2019-9193）和Struts2
RCE（CVE-2017-5638）攻击模块，目前该版本共有18种攻击模块，并且仍在不断迭代更有效的横向攻击模块；

3\. 更换矿机地址为自己的C2服务器，疑似使用自建矿池。

###  **病毒攻击流程**

![](https://image.3001.net/images/20210731/1627745386_61056c6a367484a4ea9cb.png!small)

###  **攻击活动**

通过深信服云端数据分析，发现该病毒近期扩散十分迅速，短期内有大量主机中招。如下图Sysrv-hello病毒近期的感染量，可以看到病毒在7月2-7日进行了大规模入侵活动：

![](https://image.3001.net/images/20210801/1627750432_61058020c932b28f8505d.png!small)

###  **样本关联**

通过威胁情报图数据库进行样本关联，发现大量的同家族威胁样本，该病毒的特征属于 **更新快** 、 **持续迭代** **演进** 的病毒家族：

![](https://image.3001.net/images/20210801/1627750480_61058050daa8c1117620a.png!small)

##  **病毒样本分析**

Sysrv-hello攻击目标同时覆盖Windows和Linux操作系统，针对两平台除前置Payload不同外，其他模块基本一致。其中主体程序
**sys可执行文件**
（横向传播模块）是由Golang编写的，因此具备跨平台性；矿机使用的是开源XMRig矿机。下面将分别介绍Windows和Linux的前置Payload以及主体程序sys。

###  **Windows版本**

入侵Windows系统成功后，植入名为 **ldr.ps1** 的PowerShell脚本来执行恶意命令。 **ldr.ps1** 脚本主要功能为：

1\. 关闭防火墙并结束自身老版本病毒的进程；

2\. 通过监测其他挖矿家族常用端口来清除竞品挖矿程序；

3\. 从C2：http[:]//194.145.227.21/ **sys.exe** 下载并执行主体程序 **sys.exe**
，并通过创建计划任务和写注册表来实现本地持久化。

![](https://image.3001.net/images/20210801/1627750521_610580791950e2f85644b.png!small)

 **Linux版本**

入侵Linux系统成功后，植入名为ldr.sh的Shell脚本来执行恶意命令。ldr.sh脚本功能大致与Windows下的ldr.ps1大同小异，但功能更为完善。如：

1\. 关闭防火墙并结束自身老版本病毒的进程；

2\. 通过监测其他挖矿家族常用端口来清除竞品挖矿程序；

3\. 从C2：http[:]//194.145.227.21/ **sys.x86_64** 下载并执行主体程序。

![](https://image.3001.net/images/20210801/1627750595_610580c3c380a160841ff.png!small)

除此之外 **ldr.sh**
，还会读取/、/root和/home目录下的SSH私钥及配置文件，并结合获取到的SSH密钥进行爆破。当爆破成功后，便在新的受害主机上下载并运行
**ldr.sh** 脚本，代码如图：  
![](https://image.3001.net/images/20210801/1627750611_610580d3dd62d5976865a.png!small)

 **主体sys程序（横向传播模块）**

由于主体sys程序是由Golang编写的，因此不同平台前置Payload下载的sys.exeh和sys.x86_64其代码和功能差距不大，因此本文将以Windows版本进行介绍。

通过脚本还原Go语言的函数和字符串之后，能定位出作者的编译路径和作者的用户名为 **K** ：

![](https://image.3001.net/images/20210801/1627750626_610580e2eb64ab5f85987.png!small)
**创建端口互斥体**

根据受害主机名生成随机端口，并将该随机端口作为互斥体，当检测到该端口已处于监听状态便退出程序，来确保唯一进程执行。

![](https://image.3001.net/images/20210801/1627750645_610580f56ff53494cfae7.png!small)

###  **横向传播**

本次捕获到的Sysrv-hello一共包含18个横向攻击模块，根据随机生成的IP进行端口扫描，判断目标开放的服务，来确认使用的攻击方式。18种横向攻击方式如下表：

 **端口**

|

 **漏洞**  
  
---|---  
  
9999

|

XXL-JOB executor 未授权访问漏洞  
  
8888

|

Jupyter未授权访问漏洞  
  
80

|

Laravel Debug mode RCE（CVE_2021_3129）  
  
80/8080

|

Tomcat 弱口令爆破  
  
80/8080

|

Jenkins RCE（CVE-2018-1000861）  
  
8081

|

Nexus Repository Manager 3 RCE（CVE-2019-7238）  
  
7001

|

WebLogic RCE CVE-2020-14882  
  
6379

|

Redis弱口令爆破  
  
9001

|

Supervisord远程命令执行漏洞（CVE-2017-11610）  
  
80

|

JBoss反序列化漏洞(CVE-2017-12149)  
  
80

|

ThinkPHP5 RCE  
  
5432

|

 **PostgreSQL RCE（CVE-2019-9193）**  
  
8090

|

Confluence RCE（CVE-2019-3396）  
  
22

|

 **SSH 爆破**  
  
80

|

 **Struts2-s2-045 RCE （CVE-2017-5638）**  
  
80

|

phpunit RCE（CVE-2017-9841）  
  
8088

|

Hadoop YARN REST API未授权漏洞利用  
  
80

|

Wordpress-XMLRPC暴力破解  
  
注：其中 **加粗** 的为本次版本新增的横向攻击模块。

###  **新增横向攻击模块**

新增PostgreSQL RCE（CVE-2019-9193）漏洞利用模块，如图：

![](https://image.3001.net/images/20210801/1627750684_6105811c159c979ed5135.png!small)

新增struts2-s2-045 RCE（CVE-2017-5638）漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750722_6105814216ce26a9a482a.png!small)

新增SSH爆破：![](https://image.3001.net/images/20210801/1627750732_6105814c55492f05e7cd4.png!small)

 **历史漏洞利用模块**

XL-JOB executor 未授权访问漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750743_610581573c32c1ed43756.png!small)

Jupyter未授权访问漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750755_6105816303c8f7c650b15.png!small)

Laravel Debug mode RCE（CVE_2021_3129）漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750812_6105819c14f5fb453a0b9.png!small)

Tomcat 弱口令爆破模块：

![](https://image.3001.net/images/20210801/1627750775_6105817775fcbaa48d733.png!small)

Jenkins RCE CVE-2018-1000861漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750836_610581b49788abc6d4a1d.png!small)

Nexus Repository Manager 3 RCE（CVE-2019-7238）漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750915_61058203f15a50711abe2.png!small)

WebLogic RCE （CVE-2020-14882）漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750856_610581c8e6da042d0f7b4.png!small)

Redis未授权写漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750933_6105821564da588538035.png!small)

Supervisord远程命令执行漏洞（CVE-2017-11610）利用模块：

![](https://image.3001.net/images/20210801/1627750954_6105822af0f6c7e12b61a.png!small)

JBoss反序列化漏洞(CVE-2017-12149)利用模块：

![](https://image.3001.net/images/20210801/1627750968_61058238b386aeb8e711f.png!small)

ThinkPHP5 RCE漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750982_610582462d2373716ef97.png!small)

PostgreSQL RCE（CVE-2019-9193）漏洞利用模块：

![](https://image.3001.net/images/20210801/1627750994_6105825214babb6d30d22.png!small)

Confluence RCE（CVE-2019-3396）漏洞利用模块：

![](https://image.3001.net/images/20210801/1627751014_61058266776a11e3af5bc.png!small)

Payload：

![](https://image.3001.net/images/20210801/1627751027_6105827345dc1379b3a94.png!small)

Phpunit RCE（CVE-2017-9841）漏洞利用模块：

![](https://image.3001.net/images/20210801/1627751040_610582807ff030f396980.png!small)

Hadoop YARN REST API未授权漏洞利用：

![](https://image.3001.net/images/20210801/1627751053_6105828d5b3c05fdbc6e7.png!small)

WordPress暴力破解：

![](https://image.3001.net/images/20210801/1627751065_61058299c3471c5d58edc.png!small)

###  **XMRig挖矿**

最后，样本会创建守护线程（go
routine）来守护矿机进程和文件，先将XMRig挖矿程序释放到临时目录下，并重命名为kthreaddi，然后释放配置文件，当挖矿进程运行起来，便会将配置文件删除。

![](https://image.3001.net/images/20210801/1627751083_610582abca0336317ceaa.png!small)

矿池地址为：194.145.227.21:5443，矿池与C2地址一致，并且本地配置和抓包都没有看到钱包地址，因此推测此版本使用的是病毒作者自建的矿池，详细配置如图：

![](https://image.3001.net/images/20210801/1627751096_610582b8414eeef2a9be1.png!small)

抓取的XMRig登陆信息的流量包，如图：

![](https://image.3001.net/images/20210801/1627751120_610582d0094deec882908.png!small)

##  **IOC**

 **MD5**

> DA63A2F797B27F31745CFB8F94479BF4（sys.x86_64）  
> D51BA1FEE712AAC5A3A17129782115AF(sys.exe)  
> C67607C0927154A4D2EFD79AD502CC7D(ldr.ps1)  
> 46C7302FE138E6A877755A3B5203303A(ldr.sh)  
> A7013A2C7FD3A6168A7C0D9EED825C32(kthreaddk.exe)

 **IP**

> 194[.]145.227.21

 **URL**

> http[:]//194.145.227.21/ldr.ps1  
> http[:]//194.145.227.21/ldr.sh  
> http[:]//194.145.227.21/sys.exe  
> http[:]//194.145.227.21/sys.x86_64

