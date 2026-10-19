**![lynis.jpg](https://image.3001.net/images/20180531/15277381455016.jpg!small)**

**Lynis是一款Unix系统的安全审计以及加固工具，能够进行深层次的安全扫描，其目的是检测潜在的时间并对未来的系统加固提供建议。这款软件会扫描一般系统信息，脆弱软件包以及潜在的错误配置。扫描完成后，Lynis还会为我们生成一份包含所有扫描结果的安全报告。**

**Lynis是Unix/Linux系统用于软件补丁管理，恶意软件扫描和漏洞检测的最值得信赖的自动化审计工具之一。此工具非常适合于安全审计人员，网络安全专家，渗透测试人员，网络和系统管理人员以及安全工程师使用。**

## 与Lynis兼容的操作系统包括：

> AIX
>
> Arch Linux
>
> BackTrack Linux
>
> CentOS
>
> Debian, DragonFlyBSD
>
> Fedora Core, FreeBSD
>
> Gentoo
>
> HPUX
>
> Kali, Knoppix
>
> Linux Mint
>
> MacOS X, Mageia, Mandriva
>
> NetBSD
>
> OpenBSD, OpenSolaris, openSUSE, Oracle Linux
>
> PcBSD, PCLinuxOS
>
> Red Hat Enterprise Linux (RHEL) and derivatives
>
> Sabayon, Scientific Linux, Slackware, Solaris 10, SuSE
>
> TrueOS
>
> Ubuntu and derivatives

##  **Lynis也可以被用于软件审计**

> Database servers: MySQL, Oracle, PostgreSQL
>
> Time daemons: dntpd, ntpd, timed
>
> Web servers: Apache, Nginx

一旦lynis开始扫描你的系统，它将执行多个类别的审计：

> 系统工具：系统二进制文件
>
> 启动和服务：启动加载程序，启动服务
>
> 内核：运行级别，加载模块，内核配置，核心转储
>
> 内存和进程：僵尸进程，IO等待进程
>
> 用户，组和身份验证：组ID，sudoers，PAM配置，password aging，默认掩码
>
> Shells
>
> 文件系统：挂载点，/tmp文件， root文件系统
>
> 存储：usb-storage，firewire ohci
>
> NFS
>
> 软件：名称服务：DNS搜索域，BIND
>
> 端口和软件包：易受攻击/可升级软件包，安全存储库
>
> 网络：名称服务器，混杂接口（promiscuous interfaces），连接
>
> 打印机和spools： cups配置
>
> 软件：电子邮件和消息
>
> 软件：防火墙：iptables，pf
>
> 软件：webserver：Apache，nginx
>
> SSH支持：SSH配置
>
> SNMP支持
>
> 数据库：MySQL root密码
>
> LDAP服务
>
> 软件：php：php选项
>
> Squid支持
>
> 日志记录和文件：Syslog daemon，日志目录
>
> 不安全服务：inetd
>
> Banners和标识
>
> 计划任务：crontab/cronjob，atd
>
> Accounting：sysstat数据，auditd
>
> 时间和同步：ntp daemon
>
> 加密：SSL证书过期
>
> 虚拟化
>
> 安全框架：AppArmor，SELinux，安全状态
>
> 软件：文件完整性
>
> 软件：恶意软件扫描器
>
> 主目录：shell历史文件

第一次运行Lynis建议使用 **-c** 参数， **-c** 表示对系统进行最全面的检查。如果你想要添加审计员的名字，可以使用 **–auditor**
参数。

从 **[GitHub](https://github.com/CISOfy/lynis)** 下载和安装Lynis。

    
    
    git clone https://github.com/CISOfy/lynis
    $ cd lynis-1.3.8
    # ./lynis

 **使用示例：**

    
    
    # lynis -c –auditor “BALAJI”

图1.初始化

![1.png](https://image.3001.net/images/20180531/15277381675002.png!small)

图2.系统工具

![lynis2.png](https://image.3001.net/images/20180531/15277381859311.png!small)

图3. Boot＆Services和Kernel

![3.png](https://image.3001.net/images/20180531/15277382015944.png!small)

图4.用户和组

![4.png](https://image.3001.net/images/20180531/15277382142910.png!small)

图5.Shell和存储

![5.png](https://image.3001.net/images/20180531/15277382313670.png!small)

图6.软件，端口和软件包

![6.png](https://image.3001.net/images/20180531/15277382456437.png!small)

图7.网络和打印机

![7.png](https://image.3001.net/images/20180531/15277382583039.png!small)

图8.电子邮件，防火墙和Web服务器

![8.png](https://image.3001.net/images/20180531/15277383177238.png!small)

图9. SSH，SNMP和数据库

![9.png](https://image.3001.net/images/20180531/15277383322223.png!small)

图10. PHP，Squid代理和日志记录

![10.png](https://image.3001.net/images/20180531/15277383479107.png!small)

图11. Inetd，Banner和Cron

![11.png](https://image.3001.net/images/20180531/1527738363724.png!small)

图12.Accounting，NTP和密码学

![12.png](https://image.3001.net/images/20180531/15277383829470.png!small)

图13.虚拟化，安全框架和文件完整性

![13.png](https://image.3001.net/images/20180531/15277383965200.png!small)

图14.恶意软件扫描程序，系统工具和主目录

![14.png](https://image.3001.net/images/20180531/15277384143500.png!small)

图15.内核加固

![15.png](https://image.3001.net/images/20180531/15277384307634.png!small)

图16.加固，自定义测试和结果

![lynis_16_hardening_customtests_result.png](https://image.3001.net/images/20180531/15277384487380.png!small)

图17.index加固

**![17.png](https://image.3001.net/images/20180531/15277384653576.png!small)**

## 自定义测试

你的当前测试的系统可能并不需要对所有内容进行测试，例如你的系统并没有运行Web服务器，那么我们可以使用-tests参数，语法如下：

    
    
    # lynis –tests “Test-IDs”

有超过100个我们可以做的测试。以下是Lynis Tests-ID的部分列表。

FILE-7502 (检查系统所有的二进制文件)

BOOT-5121 (GRUB boot loader存在检查).

BOOT-5139 (LILO boot loader存在检查)

BOOT-5142 (检查SPARC Improved boot loader (SILO))

BOOT-5155 (检查YABOOT boot loader配置文件)

BOOT-5159 (OpenBSD i386 boot loader存在检查)

BOOT-5165 (检查FreeBSD boot services)

BOOT-5177 (检查Linux boot和正在运行的services)

BOOT-5180 (检查Linux boot services (Debian style))

BOOT-5184 (检查引导文件/脚本的权限)

BOOT-5202 (检查系统的正常运行时间)

KRNL-5677 (检查CPU选项和支持)

KRNL-5695 (确定Linux内核版本和版本号)

KRNL-5723 (确定Linux内核是否为单内核)

KRNL-5726 (检查Linux加载的内核模块)

KRNL-5728 (检查Linux内核配置)

KRNL-5745 (检查FreeBSD加载的内核模块)

KRNL-5770 (检查活动内核模块)

KRNL-5788 (检查新内核的可用性）

KRNL-5820 (检查核心转储配置)

以下是运行“检查系统正常运行时间”和“检查核心转储配置”测试的命令示例。

    
    
    # ./lynis –tests “BOOT-5202 KRNL-5820”

![111111.png](https://image.3001.net/images/20180531/15277385011.png!small)

想要获得更多Tests-ID，可以在/var/log/lynis.log中找到。这里有一个窍门。

1.首先，我们使用-c (check-all)参数运行lynis。

    
    
    # ./lynis -c -Q

2.然后看看/var/log/lynis.log文件。使用cat命令并与grep结合使用。假设你想搜索与Kernel相关的Test-ID。则可以使用关键字KRNL找到它。

    
    
    # cat /var/log/lynis.log | grep KRNL

![2222.png](https://image.3001.net/images/20180531/15277385428609.png!small)

以下是Lynis提供的完整的Test-ID关键字。

> BOOT  
> KRNL (kernel)  
> PROC (processor)  
> AUTH (authentication)  
> SHLL (shell)  
> FILE  
> STRG (storage)  
> NAME (dns)  
> PKGS (packaging)  
> NETW (network)  
> PRNT (printer)  
> MAIL  
> FIRE (firewall)  
> HTTP (webserver)  
> SSH  
> SNMP  
> DBS (database)  
> PHP  
> LDAP  
> SQD (squid proxy)  
> LOGG (logging)  
> INSE (insecure services – inetd)  
> SCHD (scheduling – cron job)  
> ACCT (accounting)  
> TIME (time protocol – NTP)  
> CRYP (cryptography)  
> VIRT (virtualization)  
> MACF (AppArmor – SELINUX)  
> MALW (malware)  
> HOME  
> HRDN (hardening)

如果你觉得输入Test-ID是件非常麻烦的事，那么你可以使用 **-test-category**
参数。使用该选项，Lynis将运行包含在特定类别内的Test-ID。例如，你想运行防火墙和内核测试。你可以输入以下命令：

    
    
    # ./lynis –tests-category “firewalls kernel”

##
![3333.png](https://image.3001.net/images/20180531/15277385751927.png!small)

## 将 **Lynis作为** **Cronjob运行**

除了以上的方便之外，我们还可以将Lynis作为Cronjob定期自动运行。以下是每月运行一次的示例：

    
    
    #!/bin/sh
    AUDITOR=”automated”
    DATE=$(date +%Y%m%d)
    HOST=$(hostname)
    LOG_DIR=”/var/log/lynis”
    REPORT=”$LOG_DIR/report-${HOST}.${DATE}”
    DATA=”$LOG_DIR/report-data-${HOST}.${DATE}.txt”
    cd /usr/local/lynis
    ./lynis -c –auditor “${AUDITOR}” –cronjob > ${REPORT}
    mv /var/log/lynis-report.dat ${DATA}
    # End

将脚本保存到/etc/cron.monthly/lynis。还有千万不要忘记添加相关路径（ **/** usr **/local/lynis** 和
**/var/log/lynis** ），否则脚本将无法正常工作。

 ***参考来源：[gbhackers](https://gbhackers.com/lynis-open-source-security-auditing-tool-a-detailed-explanation/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

