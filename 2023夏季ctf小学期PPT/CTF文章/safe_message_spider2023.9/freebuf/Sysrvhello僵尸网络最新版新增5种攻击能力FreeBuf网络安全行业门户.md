## 摘要

> Sysrv-hello僵尸网络木马当前版本更新较大：更新基础设施，新增端口反调试；
>
> 传统攻击手法保留：Mysql爆破、Tomcat爆破、Weblogic漏洞利用、Nexus弱口令命令执行漏洞利用；
>
> 新增5种攻击方式：Jupyter弱口令爆破、WordPress 弱口令爆破、Jenkins弱口令爆破、Redis未授权写入计划任务、Apache
> Solr命令执行漏洞攻击。
>
> 入侵成功后拉取sysrv蠕虫扩散模块，每5分钟随机扫描探测新攻击目标；
>
> 投递载荷：门罗币挖矿木马kthreaddi。

## 一、概述

腾讯安全威胁情报中心检测到Sysrv-hello僵尸网络近期十分活跃，该僵尸网络具备木马、后门、蠕虫等多种恶意软件的综合攻击能力。

Sysrv-hello僵尸网络于2020年12月首次披露，腾讯安全曾在今年1月发现该团伙使用Weblogic远程代码执行漏洞（CVE-2020-14882）攻击传播，本月该团伙再次升级攻击手法：新增5种攻击能力，已观察到失陷主机数量呈上升趋势。其入侵方式覆盖到多数政企单位常用的Web服务，危害严重，腾讯安全专家提醒相关单位安全运维人员高度警惕。

Sysrv-hello僵尸网络攻击目标同时覆盖Linux和Windows操作系统，最终利用失陷主机挖矿，会大量消耗主机CPU资源，严重影响主机正常服务运行，该僵尸网络还会利用已失陷主机继续扫描攻击其他目标。腾讯安全全系列产品已支持对Sysrv-hello僵尸网络各个环节的攻击传播活动进行检测防御。

![](https://image.3001.net/images/20210302/1614665490_603dd71235217bedd8024.png!small)

### 排查&加固

腾讯安全专家建议安全运维人员排查以下条目，以判断系统是否受到损害。

 **文件：**

/tmp/sysrv*

/tmp/随机目录/kthreaddi

 **进程：**

sysrv*

kthreaddi

 **定时任务：**

下拉执行(hxxp://xx.xx.x.x/ldr.sh)的风险crontab项

 **建议加固以下项目，以消除风险：**

Jupyter、WordPress、Jenkins、Redis等服务组件配置强密码；

非必须的情况下，不对外开放redis端口。必须开放时，应配置相应的访问控制策略；

升级Apache Solr组件至最新版本，以消除漏洞影响。

## 二、样本分析

分析样本后发现，Sysrv-hello僵尸网络木马当前版本代码结构相对以往版本变化较大，样本行为层除增加端口反调试、使用的基础设施更新之外。其入侵方式也增加了5种，除去之前使用的Mysql爆破，Tomcat爆破，Weblogic漏洞利用，Nexus弱口令命令执行漏洞利用外。新增以下5种组件的入侵攻击。

1.Jupyter弱口令爆破入侵；

2.WordPress 弱口令爆破入侵；

3.Jenkins弱口令爆破入侵；

4.Redis未授权写计划任务入侵；

5.Apache Solr命令执行漏洞入侵（CVE_2019_0193）。

保留了前一版本的hello_src_exp组合攻击：

![](https://image.3001.net/images/20210302/1614665523_603dd73386f905d4805bb.png!small)

入侵成功后植入shell脚本执行恶意命令，脚本进一步拉取sysrv蠕虫扩散模块，分析过程种捕获到两个恶意文件托管地址，hxxp://finalshell.nl，hxxp://45.145.185.85，对应sysrv蠕虫模块分别命名为sysrv002，sysrv003，可见该蠕虫更新频繁。

![](https://image.3001.net/images/20210302/1614665544_603dd748ceadbb73e6efe.png!small)

![](https://image.3001.net/images/20210302/1614665555_603dd7531dcbc80ccc747.png!small)

分析版本sysrv蠕虫启动后会对端口进行随机扫描，ip随机生成，随机从9个准备好的目标端口内选择一个进行扫描探测，确认目标开放服务，确认攻击方式。单次扫描循环单位为5分钟。

![](https://image.3001.net/images/20210302/1614665565_603dd75d8bd59ff59ba54.png!small)

扫描端口信息如下

![](https://image.3001.net/images/20210302/1614665576_603dd7683e10c93ed2065.png!small)

![](https://image.3001.net/images/20210302/1614665587_603dd77385aac7a370670.png!small)

对sysrv蠕虫随机目标扫描代码进行相关patch后可进一步方便观察其单次攻击流程

![](https://image.3001.net/images/20210302/1614665596_603dd77cc01abfa234505.png!small)

![](https://image.3001.net/images/20210302/1614665606_603dd7863cb24fedc9757.png!small)

新版本病毒，相比之前的版本增加了5种组件的攻击方式，主要有以下部分：

 **Jupyter** **弱口令爆破入侵**

Jupyter Notebook是一个交互式笔记本，支持运行 40 多种编程语言。本质是一个 Web
应用程序，便于创建和共享文学化程序文档，支持实时代码，数学方程，可视化。当管理员未为Jupyter
Notebook配置密码，或者配置了弱密码时，将导致未授权访问漏洞。攻击者即有机会登录其管理界面，进而创建console执行任意代码。

Jupyter Notebook登录管理界面

![](https://image.3001.net/images/20210302/1614665615_603dd78fb41f36c9e6a1c.png!small)

点击terminal创建console可执行任意代码

![](https://image.3001.net/images/20210302/1614665623_603dd797c70487ab993ad.png!small)

sysrv感染过程对目标进行Jupyter登录页面探测

![](https://image.3001.net/images/20210302/1614665632_603dd7a09b082e8474f58.png!small)

查询其登录接口尝试弱密码组包登录Jupyter管理后台

![](https://image.3001.net/images/20210302/1614665641_603dd7a9ba191dafe409e.png!small)

![](https://image.3001.net/images/20210302/1614665650_603dd7b2979839790200a.png!small)

攻击过程种使用到的部分弱密码

![](https://image.3001.net/images/20210302/1614665659_603dd7bb7ae2d8f91fda4.png!small)

登录成功后调用管理面板terminals接口执行命令入侵服务器执行恶意脚本

![](https://image.3001.net/images/20210302/1614665668_603dd7c4bd70883afaddb.png!small)

下图为Jupyter组件被入侵成功后，被植入了sysrv003蠕虫模块

![](https://image.3001.net/images/20210302/1614665677_603dd7cd143f67a7be32b.png!small)

 **Apache Solr** **命令执行漏洞 入侵（CVE_2019_0193）**

Apache Solr 是一个开源的搜索服务器。Solr 使用 Java 语言开发，主要基于 HTTP 和 Apache Lucene
实现，2019年8月1日，Apache
Solr官方发布了CVE-2019-0193漏洞预警，漏洞危害评级为严重。病毒利用该方式对服务器进行入侵，植入恶意脚本执行恶意代码。

**![](https://image.3001.net/images/20210302/1614665686_603dd7d66622af3759383.png!small)**

![](https://image.3001.net/images/20210302/1614665700_603dd7e4456af7dfdbed1.png!small)

 **WordPress** **弱口令爆破入侵**

WordPress是一款快速建立出色网站、博客或应用的开源软件系统，当WordPress
管理员口令设置得过于简单，攻击者则有机会暴力破解并登录到系统，进一步入侵主机。攻击者对xmlrpc.php接口进行暴力破解，进一步绕过WordPress安全限制，最终通过修改主题或上传插件的方式进一步植入恶意代码。

![](https://image.3001.net/images/20210302/1614665734_603dd806a180c0c29cd19.png!small)

![](https://image.3001.net/images/20210302/1614665745_603dd8118c0c4c729ef69.png!small)

![](https://image.3001.net/images/20210302/1614665754_603dd81a60e8ee3830f88.png!small)

 **Jenkins** **弱口令爆破入侵**

Jenkins面板中用户可以选择执行脚本界面来操作一些系统命令，攻击者可通过未授权访问漏洞或者暴力破解用户密码等进脚本执行界面从而获取服务器权限。

![](https://image.3001.net/images/20210302/1614665765_603dd82545b159585edd2.png!small)

攻击过程使用到的部分弱口令

![](https://image.3001.net/images/20210302/1614665775_603dd82f62f5e8354be0b.png!small)

 **Redis** **未授权写计划任务入侵**

Redis在默认情况会将服务绑定在0.0.0.0:6379上，从而将服务暴露在公网环境下，如果在没有开启安全认证的情况下，可以导致任意用户未授权访问Redis服务器并Redis进行读写操作，病毒通过漏洞利用写入计划任务进一步实现入侵。

![](https://image.3001.net/images/20210302/1614665786_603dd83a313a528b4442c.png!small)

 **kthreaddi** **挖矿**

病毒当前投递最终载荷依然为挖矿木马，sysrv模块会在其Guard守护流程内对挖矿进程做保护，当kthreaddi进程不存在，则释放矿机到tmp目录下的随机目录内，并将其运行，随后会将本地矿机文件进行删除。

![](https://image.3001.net/images/20210302/1614665811_603dd85305c4e6f8d3368.png!small)

释放矿机到\tmp目录下的随机文件夹内，命名为kthreaddi，并将其进行删除

![](https://image.3001.net/images/20210302/1614665820_603dd85cad853e5e66795.png!small)

![](https://image.3001.net/images/20210302/1614665879_603dd897a0152bb57a456.png!small)

矿机将对机器资源进行高占用，矿机依然为XMR类型，进行门罗币挖矿。

![](https://image.3001.net/images/20210302/1614665889_603dd8a14c2f28b795a87.png!small)

![](https://image.3001.net/images/20210302/1614665899_603dd8abb13b2476bb2b1.png!small)

## 三、威胁视角看攻击行为

 **ATT &CK** **阶段**

|

 **行为**  
  
---|---  
  
 **侦察**

|

通过随机生成IP，扫描IP端口，确认可攻击目标存在的Web服务：Jupyter、WordPress、Jenkins等。  
  
 **资源开发**

|

注册C2服务器，同时对已入侵的服务器植入蠕虫模块进一步扩散传播  
  
 **初始访问**

|

利用对外开放的Web服务，植入恶意Payload执行恶意命令进而入侵系统  
  
 **执行**

|

首先植入恶意脚本执行恶意命令，随后下载植入ELF蠕虫、挖矿模块  
  
 **持久化**

|

利用计划任务实现持久化驻留  
  
 **防御规避**

|

挖矿进程名为kthreadaddi，挖矿进程名与系统进程名高度相似，以实现混淆  
  
 **发现**

|

通过扫描目标web服务信息以确认后续攻击方式  
  
 **影响**

|

蠕虫sysrv模块长时间的扫描，门罗币矿机不间断的工作，会导致系统CPU负载过大，大量消耗主机CPU资源，严重影响主机正常服务运行，导致主机有系统崩溃风险。  
  
## IOCs

 **MD5:**  
64cfecd6ae9730ee553824b3d1037ffd  
289572ebd295c6d6c004445a53a4a77a  
cac751b8f6c0fcf7c75df1680c356429

1f58426b51dac9172e5cdaad993a814c

620e54b0252d8179a7ff90967b643889

 **URL:**

hxxp://45.145.185.85/ldr.ps1

hxxp://45.145.185.85/ldr.sh

hxxp://45.145.185.85/sysrv

hxxp://45.145.185.85/sysrv.exe

hxxp://finalshell.nl/ldr.ps1

hxxp://finalshell.nl/ldr.sh

hxxp://finalshell.nl/sysrv

 **Domain &IP**

finalshell.nl

45.145.185.85

## 参考资料：

《Sysrv-hello僵尸网络集木马、后门、蠕虫于一身，攻击Linux、Windows主机挖矿》

https://mp.weixin.qq.com/s/iNqBcLKwhVUSz5ltLN_ubw

