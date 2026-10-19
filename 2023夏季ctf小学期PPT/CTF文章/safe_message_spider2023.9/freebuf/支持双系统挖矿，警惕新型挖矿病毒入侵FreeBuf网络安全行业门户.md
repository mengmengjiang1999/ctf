## ****背景概述****

近日，深信服漏洞团队和终端安全团队联手通过信服云安全防护体系捕获一个针对云主机可以进行双系统挖矿的新型挖矿病毒，该病毒在入侵终端后会检测并结束终端的安全防护软件，具备一定的查杀对抗能力；且能够隐藏自身进行扫描攻击和挖矿。

根据威胁情报信息，该病毒文件关联的相关域名是在今年6月才进行创建的：

![](https://image.3001.net/images/20210723/1627010432_60fa358035077984fb99f.png!small)

##  ** **样本分析****

执行流程：

![](https://image.3001.net/images/20210723/1627010447_60fa358fa7973ef06b72e.png!small)

###  ** **1、**** ** **启动脚本loader.sh****

流程如下：

（1）清除安全软件

（2）下载kworkers并启动

（3）清空历史命令记录

![](https://image.3001.net/images/20210723/1627010459_60fa359b8f46b7152b9b3.png!small)

###  ** **2、**** ** **启动程序kworker****

Kworker程序的功能是检查并更新各功能组件，以及启动挖矿程序dbus、攻击程序autoUpdate、隐藏脚本hideproc.sh、攻击脚本sshkey.sh。

（1）下载hxxp://m.windowsupdatesupport.org/d/windowsupdatev1.json并检查

![](https://image.3001.net/images/20210723/1627010470_60fa35a6ebf32c7197457.png!small)

（2）配置文件内容，可以发现该挖矿支持windows和linux两个版本

![](https://image.3001.net/images/20210723/1627010486_60fa35b696603674fb7f1.png!small)

（3）通过.{filename}_ver来标识文件版本

![](https://image.3001.net/images/20210723/1627010502_60fa35c62ec52fbcf2403.png!small)

（4）校验.{filename}_ver文件后，结束原有进程，下载新文件并执行

![](https://image.3001.net/images/20210723/1627010531_60fa35e340141fdd7bebc.png!small)

（5）启动的程序包括dbus、autoUpdate、hideproc.sh及sshkey.sh

###  ** **3、**** ** **扫描及攻击程序autoUpdate****

扫描并攻击192.168.0.0/16网段的Struts2、Shiro、Mssql、Postgres、Redis、Dubbo、Smb和SSH等组件、服务或协议漏洞，以及国内用户常用的泛微OA、致远OA、通达OA、phpcms、discuz等服务。

（1）检查并攻击structs2和shiro服务

![](https://image.3001.net/images/20210723/1627010562_60fa3602d189a6888bab9.png!small)

shiro服务

![](https://image.3001.net/images/20210723/1627010577_60fa36111d7e2b4aed45d.png!small)

struts2服务

![](https://image.3001.net/images/20210723/1627010589_60fa361d60966af027146.png!small)

（2）扫描内网的http和https服务，识别以下服务是否存在漏洞

![](https://image.3001.net/images/20210723/1627010608_60fa363083a99c1186135.png!small)

（3）检查并攻击dubbo

下载dubbo.jar和配置文件check_lin.data，执行攻击；

![](https://image.3001.net/images/20210723/1627010620_60fa363c6f5da6171ddd7.png!small)

执行dubbo攻击：

![](https://image.3001.net/images/20210723/1627010633_60fa36490b11d0598a7bd.png!small)

dubbo.jar文件是攻击测试程序，来自threedr3am的项目dubbo-exp

Dubbo反序列化一键快速攻击测试工具，支持dubbo协议和http协议，支持hessian反序列化和java原生反序列化。

![](https://image.3001.net/images/20210723/1627010648_60fa365822d17ad5cdb60.png!small)

配置文件check_len.data表明具体执行命令为下载loader.sh进行扩散；

![](https://image.3001.net/images/20210723/1627010659_60fa3663422a38311e38d.png!small)

（4）redis、mysql、postgres及smb

redis写入计划任务并执行

![](https://image.3001.net/images/20210723/1627010673_60fa3671a2d0609d89862.png!small)

通过写入mysql服务的master.dbo.xp_cmdshell来执行恶意命令

![](https://image.3001.net/images/20210723/1627010687_60fa367fdb643b7b6fa27.png!small)

Postgres恶意命令

![](https://image.3001.net/images/20210723/1627010698_60fa368a7239a911bba19.png!small)

smb恶意命令

![](https://image.3001.net/images/20210723/1627010708_60fa3694f30b757b24474.png!small)

###  ** **4、**** ** **进程隐藏脚本hideproc.sh****

相关文件包括hideproc.sh、processhide.c及libc2.28.so；

其中hideprocess.sh脚本流程如下：

（1）安装编译环境

（2）下载processhide.c隐藏进程源文件

（3）将源文件编译生成libc2.28.so

（4）将libc2.28.so添加到系统的ld.so.preload文件，即启动挖矿进程时自动载入该链接库实现进程隐藏

![](https://image.3001.net/images/20210723/1627010729_60fa36a96f0abbd561ca7.png!small)

###  ** **5、**** ** **攻击脚本sshkey.sh****

该脚本尝试从bash_history、etc/hosts、ssh/kownhost及进程已有连接中提取该终端连接过的终端，如果可以成功连接则下载并启动脚本loader.sh。

![](https://image.3001.net/images/20210723/1627010741_60fa36b53a0f17290f4f5.png!small)

##  ** **入侵利用的漏洞和服务信息****

 ** **相关漏洞信息****

![](https://image.3001.net/images/20210723/1627010750_60fa36bee28b0129fd701.png!small)

 ** **探测服务****

![](https://image.3001.net/images/20210723/1627010762_60fa36ca66c0fb9195d8e.png!small)

