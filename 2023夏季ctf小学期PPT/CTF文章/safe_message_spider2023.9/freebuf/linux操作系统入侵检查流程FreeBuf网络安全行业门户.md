## 1 检查概述

由于无法站在攻击者视角审视其做过哪些攻击行为，因此标准化的检查内容可以规避非标准化的风险，例如操作系统虽然没有异常登录日志，但如果不检查操作系统用户即会存在遗漏从而产生风险。同时也可规避上次检查ab内容，本次检查bc内容的非标准化风险。因此无论每个人的标准是否统一，取长补短逐渐完善自己的标准化是建议进行的。

linux操作系统入侵检查流程如下所示：

![1618920538_607ec45ad7b15f857edca.png!small?1618920538598](https://image.3001.net/images/20210420/1618920538_607ec45ad7b15f857edca.png!small?1618920538598)

## 2 瑞士军刀

由于操作系统中的系统程序可能已被恶意篡改，以及考虑检查脚本的操作系统兼容性，因此使用具有linux瑞士军*刀之称的busybox对操作系统进行检查。

下载busybox并对其进行编译。浏览器访问https://busybox.net/，下载稳定版busybox的源码。

![1618920529_607ec4512908377031752.png!small?1618920528903](https://image.3001.net/images/20210420/1618920529_607ec4512908377031752.png!small?1618920528903)

执行命令tar jxvf busybox-1.32.1.tar.bz2对压缩包进行解压。

进入目录cd busybox-1.32.1进行缺省配置make defconfig。

make可选项如下所示：

> defconfig(缺省配置)
>
> allyesconfig（最大配置）
>
> allnoconfig（最小配置）

![1618920482_607ec4222accd2c11b40b.png!small?1618920481841](https://image.3001.net/images/20210420/1618920482_607ec4222accd2c11b40b.png!small?1618920481841)

执行命令make CROSS_COMPILE=""编译busybox。

![1618920503_607ec437d710157d526a6.png!small?1618920503546](https://image.3001.net/images/20210420/1618920503_607ec437d710157d526a6.png!small?1618920503546)

等待编译结果，编译成功提示信息如下：

![1618920513_607ec4412d849940640ae.png!small?1618920512895](https://image.3001.net/images/20210420/1618920513_607ec4412d849940640ae.png!small?1618920512895)

将编译成功的busybox复制到应急响应工具包中以备应急处置时使用。

## 3 现象检查

可通过监测告警、日常巡检等主动机制发现存在的异常事件，如果没有主动发现，则只能在安全事件发生后被动发现。

现象检查发现的异常程序不可直接删除，应先验证异常进程是否存在自我守护机制，否则安全事件无法得到根除。

### 3.1 已监听端口

已监听端口并非一个独立的对象，而是和进程相关联，进程如果需要对外提供访问接口，则必须通过监听端口的方式对外开放，常用于在内网中部署正向后门程序。

> 在操作系统初始化正常运行后，建议记录已监听端口的基线值，供日常巡检使用；
>
> 受操作系统、关键路径中的网络层访问控制影响。

使用netstat命令检查已监听端口；执行命令./busybox netstat -pantu | ./busybox grep -E
"Proto|LIST"检查已监听端口。

![1618920687_607ec4ef4160c4eed7f69.png!small?1618920686993](https://image.3001.net/images/20210420/1618920687_607ec4ef4160c4eed7f69.png!small?1618920686993)

字段含义如下：

> Proto：程序协议；
>
> Recv-Q：本地准备建立连接，但正在排队的数量；
>
> Send-Q：已向本地发起建立连接的请求，但正在排队的数量；
>
> Local Address：本地地址及端口；
>
> Foreign Address：对端地址及端口；
>
> State：网络连接状态；
>
> PID/Program name：进程的pid/进程的名称。

### 3.2 已建立连接

已建立连接分为入站连接和出站连接，入站意为访问操作系统本地的方向，出站意为操作系统访问外部的方向。

> 受操作系统、关键路径中的网络层访问限制影响；
>
> 服务端如存在主动外联则需要重点检查。

使用netstat命令检查已建立连接。执行命令./busybox netstat -pantu | ./busybox grep -E
"Proto|EST"检查已监听端口。

![1618920796_607ec55cdbabcc26a1790.png!small?1618920796558](https://image.3001.net/images/20210420/1618920796_607ec55cdbabcc26a1790.png!small?1618920796558)

已建立连接中的Recv-Q意为接收队列中的数据量，Send-Q意为发送队列中的数据量。与已监听端口检查中的Recv-Q和Send-Q含义不同。

根据检查结果对非常规连接进行判断是否存在异常，并根据该连接的pid进行深入分析。

### 3.3 系统进程

cpu资源被占满、异常的已监听端口、异常的已建立连接在深入分析时均会检查系统进程。

linux进程cmd字段的值是可以伪造的，因此不可信。

使用命令获取系统进程的详细信息，由于busybox的ps命令不支持-Heo参数，因此需要执行命令ps -Heo
user,pid,ppid,tty,%cpu,%mem,lstart,etime,cmd | grep
""获取系统进程的详细信息，并检查可能存在的恶意载荷。

![1618920944_607ec5f0ab9647478d82e.png!small?1618920944642](https://image.3001.net/images/20210420/1618920944_607ec5f0ab9647478d82e.png!small?1618920944642)

-H参数用于显示进程树，因为在检查过程中部分进程可能只有命令名称加执行参数，如需在ps输出中确认执行命令的绝对路径，则需根据ppid进行上下文关联，当父进程过多则不利于检查，因此可使用-H参数精准定位父进程。-e参数用于显示全部进程，-o参数用于只显示特定字段。

ps程序输出单行过长的内容会被隐藏，虽然-w参数可不限制输出宽度，但【终端模拟器】默认不将ps输出的内容换行，当内容超出【终端模拟器】的最大宽度时，未显示的内容则会被隐藏，因此可用grep
""参数使用grep程序显示过长的内容，ps重定向至文件不受此限制。

字段含义如下：

> USER：启动该进程的用户；
>
> PID：该进程的id号；
>
> PPID：该进程的父进程id号，意为该进程是由父进程启动的；
>
> TT：启动该进程的控制台名称；
>
> %CPU：该进程占用的cpu百分比；
>
> %MEM：该进程占用的内存百分比；
>
> STARTED：该进程的启动时间，格式为“星期 月 日 时:分:秒 年”；
>
> ELAPSED：该进程已运行的时间，格式为“已启动天数-时:分:秒”；
>
> CMD：程序路径、程序命令和执行参数。

使用命令过滤已启动的操作系统程序。执行命令./busybox ps | ./busybox awk -F " " '{$3=""; sub(/
/,"\t"); sub(/ /,"\t\t"); print}' | ./busybox grep -E
"^[0-9]+\s[A-Za-z0-9]+\s+[/|A-Za-z0-9]"检查可能存在的恶意程序。

![1618920983_607ec617627a0e13c9054.png!small?1618920983324](https://image.3001.net/images/20210420/1618920983_607ec617627a0e13c9054.png!small?1618920983324)

## 4 持久化检查

如通过现象检查发现异常程序，则可以通过停止运行该进程的方式，判断其是否会重新启动。

### 4.1 计划任务

任务计划可以将任何脚本或程序定时启动。如被黑客利用则会充当恶意程序的守护机制。

linux有多个任务计划配置文件，因此在检查时注意是否遗漏。

linux的任务计划说明。linux系统中存在两个周期性运行的任务计划程序，如下所示：

![1618921066_607ec66abe400a7de1ff2.png!small?1618921066430](https://image.3001.net/images/20210420/1618921066_607ec66abe400a7de1ff2.png!small?1618921066430)

第一个是crond程序（最小时间单位是分钟），用于在指定时间运行任务。crond默认执行的任务计划配置文件位于以下位置：

> 只有root权限可增删改的/etc/crontab；
>
> 每个用户(包括root账户)可增删改自己的/var/spool/cron/$username，等效crontab命令；
>
> 只有root权限可增删改的目录/etc/cron.d/*；
>
> 已预设每分钟执行目录/etc/cron.hourly/*下所有可执行的脚本或程序。

第二个是anacron程序（最小时间单位是天），用于在指定时间运行任务。例如centos
7通过crond程序→每分钟运行一次/etc/cron.d/0hourly→该任务计划执行/etc/cron.hourly/0anacron脚本启动anacron程序。

anacron默认执行的配置文件是/etc/anacrontab，该配置文件指向每天、每周、每月需要运行的任务计划组/etc/cron.daily/*，/etc/cron.weekly/*，/etc/cron.monthly/*。

通过以上说明可知需要检查的任务计划对象。执行命令cat /etc/crontab查看检查结果。

![1618921128_607ec6a88061943914fb4.png!small?1618921128235](https://image.3001.net/images/20210420/1618921128_607ec6a88061943914fb4.png!small?1618921128235)

字段含义如下：

> 时间周期为分钟/小时/天/月/周，执行用户，执行命令；
>
> */1意为每分钟执行一次，28,36意为在28分、36分的时候执行一次，57 16意为16点57分执行1次；
>
> /etc/crontab和/etc/cron.d/*需指定用户执行命令；
>
> 而/var/spool/cron/*不需要指定用户，crond程序会自行提取*文件的名称作为执行用户。

执行命令cat /etc/anacrontab查看检查结果。

![1618921137_607ec6b1dce043654c639.png!small?1618921137517](https://image.3001.net/images/20210420/1618921137_607ec6b1dce043654c639.png!small?1618921137517)

任务计划字段含义如下：

> 任务周期：以天为单位，1为每天执行1次，7为每隔7天执行1次，@daily意为每天，@weekly意为每周，@monthly意为每月；
>
> 延迟时间：以分钟为单位，5意为anacron启动后延迟5分钟执行；
>
> 计划名称：作业标识符，例如daily；
>
> 优先级：使用nice命令指定优先级，默认10，最大-20(优先级最高)，最小19（优先级最低）；
>
> 执行程序：使用run-parts执行【脚本目录】中的对象，执行命令which run-parts可知程序路径；
>
> 脚本目录：/etc/cron.[daily|weekly|monthly]保存着需要周期性执行的脚本。

其他字段含义如下所示：

>
> RANDOM_DELAY意为随机延迟执行时间，单位为分钟，anacron会读取/var/spool/anacron/cron.[daily|weekly|monthly]日志文件，该文件记录着上次anacron执行的日期，如果相差1个【任务周期】，则在【延迟时间】的基础上，再随机延迟【RANDOM_DELAY】的值，例如在5至45分钟内执行/etc/cron.daily任务计划组中的程序脚本。
>
>
> START_HOURS_RANGE意为可执行的时间范围，例如凌晨3点至深夜22点区间内可执行对应/etc/cron.[daily|weekly|monthly]任务计划组中的程序脚本。

### 4.2 环境变量

环境变量用于将系统内容变量化，供其他程序调用。

> 环境变量分为全局生效和单用户生效，配置文件位置也不同；
>
> linux的环境变量可运行程序即实现持久化；
>
>
> 如果LD_PRELOAD环境变量被黑客利用则可以隐藏指定程序的内容回显，例如将top/lsof/ps/netstat命令的内容回显进行过滤，不显示恶意程序的相关内容；
>
>
> 动态链接库除了通过LD_PRELOAD环境变量预加载，还可通过/etc/ld.so.preload配置文件预加载。LD_PRELOAD环境变量预加载详见https://www.freebuf.com/articles/system/224742.html（论单位或个人应急演练的重要性）目录4场景分享；
>
> alias也可实现隐藏指定程序的内容回显，例如在所有命令别名后加入| grep -v xxx即可。

系统级环境变量位于/etc/目录中，用户级位于~/目录中。

![1618921195_607ec6eb542939b9e16cd.png!small?1618921195033](https://image.3001.net/images/20210420/1618921195_607ec6eb542939b9e16cd.png!small?1618921195033)

使用ps -Hef | grep "ping 127" | grep -v grep查看进程信息。

![1618921204_607ec6f4ddbff23860870.png!small?1618921204623](https://image.3001.net/images/20210420/1618921204_607ec6f4ddbff23860870.png!small?1618921204623)

在/tmp目录下新建两个ping脚本，内容如下所示，赋予可执行权限。

![1618921213_607ec6fdea54eb13d107b.png!small?1618921213627](https://image.3001.net/images/20210420/1618921213_607ec6fdea54eb13d107b.png!small?1618921213627)

将脚本放入系统级和用户级环境变量并使其生效，执行source命令模拟系统重启。

sed -i '1i /tmp/ping1.sh' /etc/profilesource /etc/profilesed -i '1i
/tmp/ping2.sh' ~/.bash_profilesource ~/.bash_profile

使用ps -Hef | grep "ping" | grep -v grep可发现程序已启动。因此linux的环境变量也可实现自启动。

![1618921225_607ec709560aa760cbc87.png!small?1618921225057](https://image.3001.net/images/20210420/1618921225_607ec709560aa760cbc87.png!small?1618921225057)

执行命令删除篡改内容。

sed -i '/\/tmp\/ping1.sh/{d}' /etc/profilesource /etc/profilesed -i
'/\/tmp\/ping2.sh/{d}' ~/.bash_profilesource /etc/profile

### 4.3 系统服务

服务可在系统启动时自动运行相关程序或脚本。

系统服务检查项内容较多，检查时应防止发生错漏少情况。

不同版本系统服务的区别以及配置文件路径：

![1618921253_607ec7254b17fb09d469c.png!small?1618921253058](https://image.3001.net/images/20210420/1618921253_607ec7254b17fb09d469c.png!small?1618921253058)

 **版本的区别**

> init是旧机制，其服务配置文件/自启动配置文件可直接运行程序；
>
> systemd是新机制，其服务配置文件运行程序需要将程序路径放入Exec*=中，如果直接/path/exe无法执行且服务重新加载时会报错。

 **服务保存路径的区别**

init版本的服务保存在/etc/rc.d/init.d/目录中，/etc/init.d/是其的软连接。

systemd版本的服务保存在如下目录：

>
> /etc/systemd/system/（该目录下部分.service是/usr/lib/systemd/system/目录下部分.service的软连接）以及/etc/systemd/user/；
>
> /run/systemd/system/（当服务正在运行进行配置修改才会创建的单元文件）
>
> /usr/lib/systemd/system/（/lib/是/usr/lib/的软连接）以及/usr/lib/systemd/user/。

 **自启动项保存路径的区别**

init版本的启动项保存在目录/etc/rc.d/rc0-6.d/以及/etc/rc.d/rc.local，/etc/rc0-6.d/以及/etc/rc.local是其的软连接。

systemd不再有runlevel运行级别的概念，而是将其变更为target单元组，将要自启动的服务脚本放入对应的单元组，即可实现不同单元组的自启动。systemd版本的启动项保存在如下目录/usr/lib/systemd/system/*target.wants/，/etc/systemd/system/*target.wants/。

单元组命令扩展：执行命令systemctl list-units -t target -a可发现单元组的加载状态、强依赖/弱依赖的单元组的加载状态。

![1618921303_607ec7575b9c9bcf01a55.png!small?1618921303847](https://image.3001.net/images/20210420/1618921303_607ec7575b9c9bcf01a55.png!small?1618921303847)

执行命令more /usr/lib/systemd/system/basic.target | grep -E
"Requires|Wants"可查看强依赖/弱依赖的单元组。

![1618921311_607ec75f367984eaa7f2d.png!small?1618921310940](https://image.3001.net/images/20210420/1618921311_607ec75f367984eaa7f2d.png!small?1618921310940)

 **命令区别**

>
> init版本的linux的服务和windows服务不同，init版本只可通过service脚本控制服务的运行、关闭、重启等操作，如需要自启动则需要调用chkconfig程序调整7个启动级别的状态on或off；
>
> systemd版本的linux的服务和windows服务功能基本相同，通过systemctl程序控制服务的运行、关闭、重启、自启动等操作。

### 4.4 账户权限

操作系统的账户和密码主要用于本地或远程登录。属于黑客持久化后门的一种方式。

> ssh公钥也可实现系统登录；
>
> gid和group为主从关系，权限相同。

执行命令./busybox cat /etc/passwd | grep -vE
":/[a-z]+/nologin|:/[a-z]+/shutdown|:/[a-z]+/halt|:/[a-z]+/sync"查看可登录的用户。

![1618921366_607ec796896f12b26285b.png!small?1618921366136](https://image.3001.net/images/20210420/1618921366_607ec796896f12b26285b.png!small?1618921366136)

执行命令./busybox id yjyl查看用户所属组。

![1618921373_607ec79d0a0ab000427c4.png!small?1618921372692](https://image.3001.net/images/20210420/1618921373_607ec79d0a0ab000427c4.png!small?1618921372692)

执行命令./busybox ls /root/.ssh/查看是否存在公钥文件。

![1618921379_607ec7a370e08e542da88.png!small?1618921379072](https://image.3001.net/images/20210420/1618921379_607ec7a370e08e542da88.png!small?1618921379072)

执行命令./busybox cat /root/.ssh/authorized_keys查看是否存在可疑公钥。

![1618923656_607ed088e461576a114ca.png!small?1618923656700](https://image.3001.net/images/20210420/1618923656_607ed088e461576a114ca.png!small?1618923656700)

### 4.5 rootkit

rootkit木马是一种系统内核级病毒木马，其进入内核模块后能获取到操作系统高级权限，从而使用各种底层技术隐藏和保护自身，绕开安全软件的检测和查杀。

rootkit检查工具chkrootkit提示，如果已找到rootkit，最好的方法是重新安装操作系统。

![1618921410_607ec7c26dcdb0d359dc1.png!small?1618921410135](https://image.3001.net/images/20210420/1618921410_607ec7c26dcdb0d359dc1.png!small?1618921410135)

浏览器访问ftp://ftp.pangeia.com.br/pub/seg/pac/chkrootkit.tar.gz下载该工具。

![1618921428_607ec7d48be38b452afd5.png!small?1618921428214](https://image.3001.net/images/20210420/1618921428_607ec7d48be38b452afd5.png!small?1618921428214)

执行命令tar zxvf chkrootkit.tar.gz将其解压。进入目录cd chkrootkit使用make
sense进行编译。如果提示/usr/bin/ld：找不到 -lc，则安装yum -y install glibc-static。

安装完成后即可执行命令./busybox sh chkrootkitDir/chkrootkit-0.54/chkrootkit 2>&1 |
./busybox grep -vE "nothing found|not found|not infected|not tested|no suspect
files|ROOTDIR"进行rootkit检查。

![1618921436_607ec7dc977f8faca78ad.png!small?1618921436363](https://image.3001.net/images/20210420/1618921436_607ec7dc977f8faca78ad.png!small?1618921436363)

如果/tmp目录下具有可执行脚本则会提示白框中的信息，判断逻辑较为简单因此容易误判。

## 5 痕迹检查

### 5.1 访问日志

操作系统的/var/log/secure日志文件中记录着用户访问的痕迹；应用系统的access日志中记录着用户访问的痕迹。

> lastb命令仅提取登录失败的日志，该命令存在被劫持的风险，可直接在/var/log/secure中日志中对登录失败的日志进行过滤；
>
> lastlog命令只匹配账户最近一次登录成功的日志，该命令存在被劫持的风险，且其功能性完全可被last命令替代。

使用last命令提取所有登录成功过的记录。执行命令./busybox last | grep "Dec
22"提取当天所有登录成功过的账户名，登录源ip，登录时间、登出时间、在线时间。

![1618921496_607ec81846fcc5a849a9b.png!small?1618921496040](https://image.3001.net/images/20210420/1618921496_607ec81846fcc5a849a9b.png!small?1618921496040)

执行命令./busybox last | grep "logged in"收集在线用户，执行结果和命令w类似。

![1618921502_607ec81eb9c95ea156741.png!small?1618921502464](https://image.3001.net/images/20210420/1618921502_607ec81eb9c95ea156741.png!small?1618921502464)

检查/var/log/secure日志，过滤所有登录失败的记录。执行命令./busybox grep "Failed password"
/var/log/secure* | ./busybox awk -F ":" '{$1=""; print}' | ./busybox awk
'{print $(NF-5),$(NF-3)}' | ./busybox uniq -c | ./busybox sort
-r收集登录失败的账户名称、ip地址以及失败次数。

![1618921512_607ec828aee5c773bbbbc.png!small?1618921512308](https://image.3001.net/images/20210420/1618921512_607ec828aee5c773bbbbc.png!small?1618921512308)

执行命令./busybox grep "Failed password" /var/log/secure* | ./busybox awk -F ":"
'{$1=""; print}' | ./busybox awk '{print
$(NF-5),$(NF-3),$1,$2,$3,$4,$5}'收集登录失败的时间。

![1618921519_607ec82fae7a666341b46.png!small?1618921519871](https://image.3001.net/images/20210420/1618921519_607ec82fae7a666341b46.png!small?1618921519871)

使用lsof命令查找应用系统访问日志。部分情况下可能不知道应用系统访问日志的存储位置，执行命令可快速定位访问日志的位置lsof | grep -E
"access[.*]?\\.log[.*]?"，如果结果中没有访问日志，则可能名称中没有access关键字或没有启用应用系统访问日志功能。

![1618921552_607ec8500c74438015ba9.png!small?1618921551670](https://image.3001.net/images/20210420/1618921552_607ec8500c74438015ba9.png!small?1618921551670)

因为lsof命令和/proc/$pid/fd均会记录进程打开并写入过内容的文件，经测试两者不会记录进程访问过的可读文件，但会记录进程调用的库。

 **应用系统访问日志检查方法论**

>
> 通过上传点上传webshell后第一个访问的人即是攻击者，因为webshell路径在应用系统中无法通过链接跳转访问，同理反推，上传webshell后的下一个动作即为验证是否可用，因此访问动作前的动作即为上传动作；
>
> 部分中间件漏洞利用无需访问网站页面，因此不会在访问日志中留下痕迹，需要通过其他特征进行逻辑关联，需要关联的特征包括不限于默认上传的路径，可能存在的漏洞。

### 5.2 文件落地

恶意程序保存在硬盘的文件系统中，例如后门程序，后门程序属于非授权的远程管理通道，黑客可通过该通道未授权管理被入侵的主机，以及随后门文件同时生成的其他恶意程序。

文件落地不单独进行手工检查，一般根据【现象检查】或【持久化检查】的结果在硬盘中寻找恶意程序，否则工作量会过大及质量较差，常规恶意程序检查建议通过操作系统杀毒软件进行。

在/tmp目录下创建并修改txt文件的修改时间为1999年01月01日00点00分00秒，访问时间为1999年01月02日00点00分00秒、状态时间为1999年01月03日00点00分00秒。

执行命令touch -a -d "1999-01-01 00:00:01" test.sh && touch -m -d "1999-01-02
00:00:01" test.sh && GetSystemDate=`date "+%Y-%m-%d %H:%M:%S"` && date -s
"1999-01-03 00:00:01" && chown root:root test.sh && date -s
"$GetSystemDate"创建文件并修改3个时间。

![1618921664_607ec8c0ad6511a0b6313.png!small?1618921664361](https://image.3001.net/images/20210420/1618921664_607ec8c0ad6511a0b6313.png!small?1618921664361)

 **示例2** **：使用命令进行检查**

执行命令find /tmp -name "*.sh" -newerat '1999-01-01 00:00:00' ! -newerat
'1999-01-01 23:59:59'查找/tmp目录下1999年01月 **01**
日访问过、后缀为sh的文件，即atime。/tmp可以是绝对路径，也可以是当前目录./。

![1618921686_607ec8d65d487dd67654c.png!small?1618921686059](https://image.3001.net/images/20210420/1618921686_607ec8d65d487dd67654c.png!small?1618921686059)

执行命令find /tmp -name "*.sh" -newermt '1999-01-02 00:00:00' ! -newermt
'1999-01-02 23:59:59'查找/tmp目录下1999年01月 **02** 日内容变更过后缀为sh的文件，即mtime。

![1618921693_607ec8ddebb69c8663f37.png!small?1618921693542](https://image.3001.net/images/20210420/1618921693_607ec8ddebb69c8663f37.png!small?1618921693542)

执行命令find /tmp -name "*.sh" -newerct '1999-01-03 00:00:00' ! -newerct
'1999-01-03 23:59:59'查找/tmp目录下1999年01月 **03** 日状态变更过、后缀为sh的文件，即ctime。

![1618921701_607ec8e5eb6e38a774606.png!small?1618921701782](https://image.3001.net/images/20210420/1618921701_607ec8e5eb6e38a774606.png!small?1618921701782)

需要注意的是newerat，newermt，newerct不会匹配起止时间，即“00:00:00”和“23:59:59”，但是区间时间“00:00:01~23:59:58”会被匹配。

蓝队比较烦的点：

>
> （红队可修改自身上传的文件，因为这样做并不触犯规则）将webshell落地转移至较为隐蔽的目录，且对3项时间均进行修改，自身免杀足够好的情况下并不会未触发安全告警，从而延迟入侵源头被发现的时间，不需要担心web访问该文件会变更该文件的访问时间，两个不同维度的机制；
>
>
> （蓝队会检查历史命令，历史命令不能增删改）因此可以将以上操作根据实际情况写好后封装到脚本中，通过执行脚本的方式完成以上操作，执行完后删除该脚本，历史命令只会记录执行和删除脚本的记录，删除时小心rm命令是否被改成了mv，导致留下痕迹。
>
> 蓝队遇到这种文件落地一般会怎么做呢？如果不看【红队比较烦的点】的话

红队比较烦的点：

> 你TM懒一点会死吗？刚上来就被T下去；
>
> 潜伏了几天，刚准备自写工具或者goby梭*哈内网就被发现了，你TM懒一点会死吗？
>
>
> 即使做了蓝队比较烦的点后，有经验的应急人员还是会过滤出访问日志中的URI，通过将路径、动作去重后排序，也是很直观的就能发现，一个时间段内存在的异常访问，最终定位落地的文件，但也仅限于攻防期间，正常人谁每隔2小时就检查1次日志啊，你TM懒一点会死吗？
>
> 如果目标可以主动外联，反弹shell会留下不能删除的痕迹；
>
> 如果目标不出网，就得上传工具到对端，通过连webshell进行操作会留下不能删除的痕迹。
>
> 如果目标不出网，就得regeog搭正向隧道进来会留下不能删除的痕迹。

部分检查场景可能会出现文件无法删除的情况，例如：

 **加锁**

删除时会出现如下提示。

![1618921765_607ec92540e08d4f15122.png!small?1618921764913](https://image.3001.net/images/20210420/1618921765_607ec92540e08d4f15122.png!small?1618921764913)

执行命令./busybox chattr -i test.sh && ./busybox rm -rf test.sh解锁后即可删除。

 **隐藏空格**

删除时会出现如下提示。

![1618921789_607ec93d3fb532b61d196.png!small?1618921788885](https://image.3001.net/images/20210420/1618921789_607ec93d3fb532b61d196.png!small?1618921788885)

因此需要知道文件的空格有多少即可删除或者通过inode索引节点删除。

![1618921798_607ec9467f915f3bf401b.png!small?1618921798136](https://image.3001.net/images/20210420/1618921798_607ec9467f915f3bf401b.png!small?1618921798136)

 **转义符**

删除时会出现命令执行无效果的情况。

![1618921808_607ec95029a1d5e68b6d1.png!small?1618921811100](https://image.3001.net/images/20210420/1618921808_607ec95029a1d5e68b6d1.png!small?1618921811100)

执行命令./busybox rm -rf \ test2.sh即可删除。

![1618921813_607ec955f08c577e5697e.png!small?1618921813659](https://image.3001.net/images/20210420/1618921813_607ec955f08c577e5697e.png!small?1618921813659)

 **连接符**

删除时会出现如下提示。

![1618921820_607ec95c90d8016ba1c53.png!small?1618921820259](https://image.3001.net/images/20210420/1618921820_607ec95c90d8016ba1c53.png!small?1618921820259)

执行命令./busybox rm -rf -- --test3.sh即可删除。

![1618921827_607ec9634b560ea40634a.png!small?1618921826989](https://image.3001.net/images/20210420/1618921827_607ec9634b560ea40634a.png!small?1618921826989)

 **显示名称乱码**

无法通过显示的文件名称进行删除。

![1618921835_607ec96b3afe5526b9a41.png!small?1618921834838](https://image.3001.net/images/20210420/1618921835_607ec96b3afe5526b9a41.png!small?1618921834838)

执行命令ls -li获取该文件的inode索引节点，然后通过find . -type f -inum 1223877 -delete即可删除。

![1618921842_607ec972354a2543fe37a.png!small?1618921841967](https://image.3001.net/images/20210420/1618921842_607ec972354a2543fe37a.png!small?1618921841967)

执行命令hmLinuxAmd64/hm-linux-amd64/hm deepscan /tmp检查webshell。

![1618921854_607ec97ed2de7176678d6.png!small?1618921854629](https://image.3001.net/images/20210420/1618921854_607ec97ed2de7176678d6.png!small?1618921854629)

![1618921858_607ec9823ac092ea7c70e.png!small?1618921858130](https://image.3001.net/images/20210420/1618921858_607ec9823ac092ea7c70e.png!small?1618921858130)

### 5.3 历史命令

history记录着用户执行过的历史命令。

退出后才会将当前shell从启动到关闭执行过的命令记录至日志文件中。

优化历史命令记录内容。将历史命令记录量进行增加以及记录命令时增加执行命令时的时间。

    
    
    vim /etc/profile
    
                   HISTSIZE=1000000
    
                   export HISTTIMEFORMAT="%y-%m-%d %H:%M:%S "
    
    source /etc/profile

效果如下：

![1618921870_607ec98ea16b00712e8f6.png!small?1618921870291](https://image.3001.net/images/20210420/1618921870_607ec98ea16b00712e8f6.png!small?1618921870291)

检查历史命令记录的内容。各账户history命令记录的日志存放于~/.bash_history。执行命令./busybox cat
/root/.bash_history查看root账户的历史命令记录。

![1618921937_607ec9d1517ec9d6b6710.png!small?1618921937082](https://image.3001.net/images/20210420/1618921937_607ec9d1517ec9d6b6710.png!small?1618921937082)

### 5.4 操作系统防火墙

linux操作防火墙配置着允许/拒绝通行的入站/出站规则。可根据防火墙配置判断该主机在同网段内的可攻击面积。

检查配置前应先检查防火墙是否已启用。

检查iptables防火墙。通过目录【系统服务】可得知iptables是否已启动，执行命令./busybox cat
/etc/sysconfig/iptables查看防火墙配置，对比目录【已监听端口】的结果可得知本机的网络层可攻击面积。

![1618921983_607ec9ffcbb8e18234131.png!small?1618921983558](https://image.3001.net/images/20210420/1618921983_607ec9ffcbb8e18234131.png!small?1618921983558)

检查firewalld防火墙。通过目录【系统服务】可得知firewalld是否已启动，执行命令./busybox cat
/etc/firewalld/zones/public.xml查看防火墙配置，对比目录【已监听端口】的结果可得知本机的网络层可攻击面积。

![1618921998_607eca0edcb779c78a037.png!small?1618921998888](https://image.3001.net/images/20210420/1618921998_607eca0edcb779c78a037.png!small?1618921998888)

### 5.5 操作系统杀毒软件

杀毒软件可用于防护恶意程序的存储、运行等恶意行为，作为主管单位对下辖单位进行攻击溯源时需进行检查。

> 应检查杀毒软件的安装时间；
>
> 应检查杀毒软件的补丁更新情况；
>
> 应检查杀毒软件的特征库是否最新；
>
> 应检查杀毒软件最近的杀毒记录；
>
> 应检查杀毒软件的白名单。

## 6 工具化

由于检查命令过长、部分检查对象例如服务通过手工检查不够直观且不够快速等等，将以上对象工具化。

下载地址：https://github.com/Ymigmli/Linux_Incident_Response/archive/refs/heads/main.zip

### 6.1 工具目录

IncidentResponse/start.sh 工具主体

IncidentResponse/busybox 用于代替系统命令

IncidentResponse/getFileTime.sh 用于获取指定时间范围内的文件

IncidentResponse/chkrootkit 第三方开源工具，用于检查rootkit

IncidentResponse/hm 第三方工具，用于检查webshell

### 6.2 IncidentResponse/start.sh说明

    
    
    #!/bin/bash
    
    
    #竹林再遇北极熊制作于2019年8月10日，今晚真的很像士兵许三多一样难过，在连长(老大)都走了以后，1个人守着1个人的连队(小组)，想起钢七连"不抛弃，不放弃"的精神，希望这种事不会再经历，真难熬
    
    
    #v1.0 建立
    #v1.1 优化
    
    
    #原则：不运行、不自启即使是威胁其影响也是微乎其微的
    #作用：好记性不如烂笔头，自动化收集操作系统中的现象、持久化、痕迹，并将无用信息进行过滤，方便检查,即只做信息收集不做过多判断；例如快速获取某个程序的启动方式
    #翻译：百度翻译
    #指南：使用root权限在当前目录下运行start.sh，根据提示输入服务器ip，检查记录存档于当前文件夹的【$HostIp_$SystemDate-results/*】目录下
    
    
    #第三方工具，可自行至源站下载、编译、替换
      #1 busybox  防止系统命令被替换以及脚本兼容性
        #下载
          #https://busybox.net/downloads/busybox-1.32.1.tar.bz2
        #编译
          #make defconfig
          #make CROSS_COMPILE=""
    
      #2 chkrootkit  rootkit检查工具
        #下载
          #ftp://ftp.pangeia.com.br/pub/seg/pac/chkrootkit.tar.gz
        #编译
          #make sense
          #yum -y install glibc-static 如果报"/usr/bin/ld：找不到 -lc"错误时
    
      #3 hm  webshell查杀工具
        #下载
          #http://dl.shellpub.com/hm/latest/hm-linux-amd64.tgz?version=1.8.2
    
    
    #异常文件删除方法
      #加锁
        #chattr -i test.sh && ./rm -rf test.sh
      #隐藏空格，转义符，连接符，显示名称乱码
        #执行命令ls -li获取该文件的inode，find . -type f -inum inodeNumber -delete
    
    
    #检查内容
      #0 创建检查目录和输出文档
      #1 现象检查
        #  1.1 已监听端口
        #  1.2 已建立连接
        #  1.3 系统进程
      #2 持久化检查
        #  2.1 任务计划
        #  2.2 环境变量
        #  2.3 系统服务
        #  2.4 账户权限
        #  2.5 rootkit
      #3 痕迹检查
        #  3.1 登陆日志
        #  3.2 文件落地
        #  3.3 历史命令
        #  3.4 防火墙
        #  3.5 杀毒软件(手动检查)
    
    
    #在可读文件中进行匹配的敏感词库，可自行更新
      #可能的启动方式
        #/end
        #. end
        #./end
        #sh/nohup/fork/exec等 /end
    
      #匹配每行第一个/，每行第一个.空格，每行第一个./,每行第一个[A-Za-z0-9/_.- ]空格/
        #^/|^\.\s+|^\./|^[A-Za-z0-9/_\.\-]+\s+/|
    
      #1-n个空格/，1-n个空格.空格，1-n个空格./，1-n个空格[A-Za-z0-9/_.- ]空格/
        #\s+/|\s+\.\s+|\s+\./|\s+[A-Za-z0-9/_\.\-]+\s+/|
    
      #[|、||、&、&&]1-n个空格[A-Za-z0-9/_.-]
        #[|&]+\s+[A-Za-z0-9\s+/_\.\-]+
                           #第一个条件不生效
    GetStartType=' grep -E "asdfasdf|curl|wget|nohup|^alias\s|LD_PRELOAD|Exec|^/|^\.\s+|^\./|^[A-Za-z0-9/_\.\-]+\s+/|\s+/|\s+\.\s+|\s+\./|\s+[A-Za-z0-9/_\.\-]+\s+/|[|&]+\s+[A-Za-z0-9\s+/_\.\-]+"'
    
    by="`pwd`/busybox"
    
    line="echo -e \n-------------------------------------------------\n-------------------------------------------------"
    
    SystemDate=`date +"%Y-%m-%d"`
    
    
    
    
    #0 创建检查目录和输出文档
    read -ep "To create a check folder, please enter the host IP address(x.x.x.x): " HostIp
    
    
    #收集合法的ip地址，如果不是则重新输入，如果是判断检查目录是否存在，如存在则结束循环，如果不存在创建后结束循环
    for ((;;))
    do
        IpMatch=`echo "$HostIp" | $by grep -E "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"`
        if [ "$IpMatch" = "" ] ; then
            read -ep "Format error, please re-enter the host IP address         (x.x.x.x): " HostIp
        else
    	if [ -d $HostIp-$SystemDate-results ] ; then
                echo "Check directory created!"
                break
            else
                mkdir $HostIp-$SystemDate-results
                $line
                echo "Check that the folder was created successfully: [ $HostIp-$SystemDate-results ]"
                break
            fi
        fi
    done
    
    
    ir="tee -a $HostIp-$SystemDate-results/0-Summary_results.txt"
    
    FileResult="$HostIp-$SystemDate-results/1-FileSumInfoResult.txt"
    
    Temp="$HostIp-$SystemDate-results/Temp.txt"
    
    Temp2="$HostIp-$SystemDate-results/Temp2.txt"
    
    #busybox没有file命令
    FileCmd=`which file`
    
    
    
    #收集文件综合信息
    GetFileSum(){
    
        #排序去重
        FileSumSort=`$by cat $Temp2 | $by grep -vE "^\$" | $by sort | $by uniq`
       
     
        #循环收集
        FileSumLine=`echo "$FileSumSort" | wc -l`
        for ((i=1; i<=$FileSumLine; i++))
        do
            FileSumName=`echo "$FileSumSort" | $by awk 'NR=='$i' {print}'`
            if [ -f $FileSumName ] ; then
                FileAccessTime=`$by stat $FileSumName | $by tail -n 3 | $by grep "Access" | $by awk -F "." '{print $1}'`
                FileModifyTime=`$by stat $FileSumName | $by tail -n 3 | $by grep "Modify" | $by awk -F "." '{print $1}'`
                FileChangeTime=`$by stat $FileSumName | $by tail -n 3 | $by grep "Change" | $by awk -F "." '{print $1}'`
                FileMd5=`$by md5sum $FileSumName | $by awk '{print $1}'`
    
                #将各信息输出至文件
                FileSumEcho1=`echo -e "[$FileSumName]"        >> $FileResult`
                FileSumEcho2=`echo -e "  FileType: $FileType" >> $FileResult`
                FileSumEcho3=`echo -e "   FileMd5:$FileMd5"   >> $FileResult`
                FileSumEcho4=`echo -e "    $FileAccessTime"   >> $FileResult`
                FileSumEcho5=`echo -e "    $FileModifyTime"   >> $FileResult`
                FileSumEcho6=`echo -e "    $FileChangeTime"   >> $FileResult`
                FileSumEcho7=`echo -e ""                      >> $FileResult`
            fi
        done    
    
        
        #删除临时文件
        if [ -f $Temp2 ] ; then
            $by rm -rf $Temp2
        fi
    }
    
    
    #收集文件类型，并对可读文件进行信息收集
    GetFileType(){
        if [[ "$FileType" =~ "shell" ]] ; then
            LineSave=`$line | $ir`
            ShellEcho=`echo "                                          [shell] [$GetFilePathEcho]" | $ir`
            Shell=`$by cat $GetFilePathEcho | $GetStartType | $by grep -vE "#|\s?for\s?|\s?if\s?"  | $ir`
            FileSum=`echo "$GetFilePathEcho" >> $Temp2`
    
        elif [[ "$FileType" =~ "Python" ]] ; then
            LineSave=`$line | $ir`
            PythonEcho=`echo "                                         [python] [$GetFilePathEcho]" | $ir`
            python=`$by cat $GetFilePathEcho | $GetStartType | $by grep -vE "#|\s?for\s?|\s?if\s?"  | $ir`
            FileSum=`echo "$GetFilePathEcho" >> $Temp2`
    
        elif [[ "$FileType" =~ "cannot open" ]] ; then
            #LineSave=`$line | $ir`
            NotExistEcho=`echo "                                      [not exist] [$GetFilePathEcho]" | $ir`
    
        elif [[ "$FileType" =~ "directory" ]] ; then
            LineSave=`$line | $ir`
            DirectoryEcho=`echo "                                      [directory] [$GetFilePathEcho]" | $ir`
            DirExist=`$by ls $GetFilePathEcho\/* 2>/dev/null | $ir`
    
            #如果是目录则会再来一次GetFileType，作用于收集更深层次的目录例如$DirExist中的文件路径及其内容，并过滤无关信息
            DirExistLine=`echo "$DirExist" | wc -l`
            if [ "$DirExist" != "" ] ; then
                for ((b=1; b<=$DirExistLine; b++))
                do
                    GetFilePathEcho=`echo "$DirExist" | $by awk 'NR=='$b' {print}'`
                    FileType=`$FileCmd $GetFilePathEcho | $by awk -F ": " '{print $2}' | $by awk -F "," '{print $1}'`
                    GetFileType
                done
            fi
    
        elif [[ "$FileType" =~ "ASCII text" ]] ; then
            LineSave=`$line | $ir`
            AsciiTextEcho=`echo "                                     [ascii text] [$GetFilePathEcho]" | $ir`
            ascii_text=`$by cat $GetFilePathEcho | $GetStartType | $by grep -vE "#|\s?for\s?|\s?if\s?"  | $ir`
            FileSum=`echo "$GetFilePathEcho" >> $Temp2`
    
        elif [[ "$FileType" =~ "ELF" ]] ; then
            #LineSave=`$line | $ir`
            ElfEcho=`echo "                                            [elf] [$GetFilePathEcho]" | $ir`
    
        elif [[ "$FileType" =~ "symbolic link" ]] ; then
            #LineSave=`$line | $ir`
            SymbolicLinkEcho=`echo "                                  [symbolic link] [$GetFilePathEcho]" | $ir`
    
        elif [[ "$FileType" =~ "empty" ]] ; then
            #LineSave=`$line | $ir`
            EmptyEcho=`echo "                                          [empty] [$GetFilePathEcho]" | $ir`
    
        else
            LineSave=`$line | $ir`
            echo "[$FileType] [$GetFilePathEcho]" | $ir
        fi
    }
    
    
    #收集文件内容
    GetFileCon(){
    
    #如果$FileName是文件，则进行信息收集，1级检查对象
    if [ -f $FileName ] ; then
        FileExist=`$by cat $FileName | $GetStartType | $by grep -vE "#|\s?for\s?|\s?if\s?" | $ir` #过滤文件中的无关信息，形成1级检查对象结果
    
        #如果是任务计划文件，则第一列可能是*/1，因此将其过滤；只显示路径；将路径最后1个.替换为空；将路径最后一个/替换为空；先排序再去重，形成2级检查对象
        GetFilePath=`echo "$FileExist" | $by awk '{sub(/^.\/[0-9]/,""); print}' | $by grep -oE "/[A-Za-z0-9/\._-]+" | $by sed 's/\.$//' | $by sed 's/\/$//' | $by sort | $by uniq`
    
        #获取已检查过文件的路径
        FileSum=`echo "$GetFilePath" >> $Temp2`
    
        #过滤白名单中的路径后放入GetFileType
        FileLine=`echo "$GetFilePath" | wc -l`
        for ((i=1; i<=$FileLine; i++))
        do
            GetFilePathEcho=`echo "$GetFilePath" | $by awk 'NR=='$i' {print}'`
    
            #2级检查对象的白名单，例如1级检查对象：/etc/profile文件中有/usr/sbin类的目录，收集无意义；非第一检查对象白名单，而是从其他检查对象跳转检查时需要排除的路径，初次使用时建议根据实际情况更新白名单，防止收集过多无用信息。如果不检查2级对象则会遗漏过多信息，但是检查就得对部分对象加白
            ExcludePath=`echo "$GetFilePathEcho" | $by grep -oE "^asdfasdf|/bin|/boot|/dev|/etc|/home|/lib|/lib64|/media|/mnt|/opt|/proc|/root|/run|/sbin|/srv|/sys|/tmp|/usr|/var|/www|/usr/bin/id|/usr/sbin|/usr/local/sbin|/dev/null|/etc/profile.d|/etc/sysconfig/bash-prompt-xterm|/etc/sysconfig/bash-prompt-screen|/etc/sysconfig/bash-prompt-default|/.bashrc|/etc/bashrc|/etc/sysconfig/network|/sbin/ip|/etc/sysconfig/network-scripts|/etc/sysconfig/pcmcia|/network-functions|/|//|/etc/sysconfig/static-routes|/sbin/route|/bin/sleep|/usr|/var/lock/subsys/network|/etc/rc.d/rc.local|/usr/lib64|/opt/RecycleBin"` 
            if [[ $GetFilePathEcho = $ExcludePath ]] ; then
                continue
            else
                FileType=`$FileCmd $GetFilePathEcho | $by awk -F ": " '{print $2}' | $by awk -F "," '{print $1}'`  #只保留文件类型
                GetFileType
            fi
        done
    
    
    #如果$FileName是目录，则进行信息收集，1级检查对象
    elif [ -d $FileName ] ; then
        FileNameMore=`$by ls $FileName\/* 2>&1`
        FileSum=`echo "$GetFilePath" >> $Temp2`
    
        #收集$FileName中存在的路径形成1级检查对象，并过滤无关信息
        FileLine=`echo "$FileNameMore" | wc -l`
        for ((i=1; i<=$FileLine; i++))
        do
            FileExistSave=`echo "$FileNameMore" | $by awk 'NR=='$i' {print}'`
            LineSave=`$line | $ir`
            FileExistSaveEcho=`echo "      [$FileExistSave]" | $ir`
    
            #1级检查对象的结果如果为空则停止本次循环
            GetFileName=`cat $FileExistSave | $GetStartType | $by grep -vE "#|\s?for\s?|\s?if\s?" | $ir`
            if [ "$GetFileName" = "" ] ; then
                LineSave=`$line | $ir`
                continue
    
            #如果不为空则形成第2级检查对象，并对其进行检查
            else
                #如果是任务计划文件，则第一列可能是*/1，因此将其过滤；只显示路径；将路径最后1个.替换为空；将路径最后一个/替换为空；先排序再去重
                GetFilePath=`echo "$GetFileName" | $by awk '{sub(/^.\/[0-9]/,""); print}' | $by grep -oE "/[A-Za-z0-9/\._-]+"| $by sed 's/\.$//' | $by sed 's/\/$//' | $by sort | $by uniq`
    
                #收集2级检查对象的路径，过滤无关信息后将其放入GetFileType
                GetFilePathLine=`echo "$GetFilePath" | wc -l`
                for ((a=1; a<=$GetFilePathLine; a++))
                do
                    GetFilePathEcho=`echo "$GetFilePath" | $by awk 'NR=='$a' {print}'`
                    FileType=`$FileCmd $GetFilePathEcho | $by awk -F ": " '{print $2}' | $by awk -F "," '{print $1}'`
                    GetFileType
                done
            fi
        done
    
    
    #如果$FileName不存在，则返回不存在的信息
    else
        FileNotExist=`echo "                                                 not exist" | $ir`
    fi
    }
    
    
    #收集普通用户名和数量
    UserHome=`$by ls -alt /home | $by grep -vE "\s\.$|\s\.\.$" | $by awk '{if (NR>1) print $NF}'`
    UserHomeLine=`echo "$UserHome" | wc -l`
    
    
    #对普通用户家目录下文件检查
    GetUserFileCon(){
        for ((n=1; n<=$UserHomeLine; n++))
        do
            UserHomeName=`echo "$UserHome" | $by awk 'NR=='$n' {print}'`
            FileName=`echo "/home/$UserHomeName/$UserFile"`
            FileSum=`echo "$FileName" >> $Temp2`
            LineSave=`$line | $ir`
            echo "      [$FileName]" | $ir
            GetFileCon
        done
    }
    
    
    #只检查1级对象，不检查2级对象
    CatFileCon(){
        if [ -f $FileName ] ; then
            CatFile=`$by cat $FileName | $ir`
            FileSum=`echo "$FileName" >> $Temp2`
        else
            FileNotExist=`echo "                                                 Not exist" | $ir`
        fi
    }
    
    
    
    
    #1 现象检查
    #1.1 已监听端口
    $line
    echo "[1 Phenomenon inspection]" | $ir
    echo "  [1.1 Monitored port]" | $ir
    listen=`$by netstat -pantu | $by grep -E "Proto|LIST" | $ir`
    
    
    #1.2 检查已建立连接
    LineSave=`$line | $ir`
    echo "  [1.2 Connection established]" | $ir
    estab=`$by netstat -pantu | $by grep -E "Proto|EST" | $ir`
    
    
    #1.3.1 收集系统进程的详细信息,busybox的ps不支持-Heo参数
    LineSave=`$line | $ir`
    echo "  [1.3-1 System process(ps)]" | $ir
    PsCmd=`which ps`
    if [ -f $PsCmd ] ; then
        SystemProcess=`$PsCmd -Heo user,pid,ppid,tty,%cpu,%mem,lstart,etime,cmd | $ir`
    else
        echo "      [ps cmdline]: not exist" | $ir
        echo "        [$PsCmd]" | $ir
    fi
    
    
    #1.3.2 收集pid,ppid不为2的系统进程信息,使用busybox
    LineSave=`$line | $ir`
    echo "  [1.3-2 System process(busybox)]" | $ir
    SystemProcessExecPath=`$by ps | $by awk -F " " '{$3=""; print}' | $by awk '{sub(/ /,"\t\t"); sub(/ /,"\t\t"); if (NR>1) print}' | $by grep -vE "\[.*\]$" | $ir`
    
    
    
    #1.3.3 收集[/proc/数字/]目录下的exe信息
    LineSave=`$line | $ir`
    echo "  [1.3-3 System process(/proc/\$pid/exe)]" | $ir
    ProcPidExe=`$by ls -alt /proc/*/exe 2>/dev/null | $by grep -v "/proc/self/exe" | $by grep " -> " | $ir`
    FileSum=`echo "$ProcPidExe" | $by awk '{sub(/ \(deleted\)$/,""); print}' | $by awk '{print $NF}' >> $Temp2`
    
    
    
    #2 持久化检查
    $line | $ir
    echo "[2 Persistence inspection]" | $ir
    echo "  [2.1 Task plan check results]" | $ir
    echo "    [2.1.1 /etc/crontab]" | $ir
    FileName="/etc/crontab"
    GetFileCon
    
    
    LineSave=`$line | $ir`
    echo "    [2.1.2 /var/spool/cron/*]" | $ir
    DirLsSave=`$by ls -alt /var/spool/cron/* 2>/dev/null | $by awk '{print $NF}' | $ir`
    FileName="/var/spool/cron"
    GetFileCon
    
    
    LineSave=`$line | $ir`
    echo "    [2.1.3 /etc/cron.d/*]" | $ir
    DirLsSave=`$by ls -alt /etc/cron.d/* 2>/dev/null | $by awk '{print $NF}' | $ir`
    FileName="/etc/cron.d"
    GetFileCon
    
    
    LineSave=`$line | $ir`
    echo "    [2.1.4 /etc/anacrontab]" | $ir
    FileName="/etc/anacrontab"
    GetFileCon
    
    
    
    #2.2 环境变量检查
    $line | $ir
    echo "  [2.2 Environmental variable check]" | $ir
    echo "    [2.2.1 /etc/profile]" | $ir
    FileName="/etc/profile"
    GetFileCon
    
    #ld.so.preload文件检查
    LineSave=`$line | $ir`
    echo "      [/etc/ld.so.preload]" | $ir
    FileName="/etc/ld.so.preload"
    CatFileCon
    
    
    #检查root账户和普通账户的/etc/bashrc
    LineSave=`$line | $ir`
    echo "    [2.2.2-1 /etc/bashrc]" | $ir
    FileName="/etc/bashrc"
    GetFileCon
    
    
    #检查root账户和普通账户的/etc/bash.bashrc
    LineSave=`$line | $ir`
    echo "    [2.2.2-2 /etc/bash.bashrc]" | $ir
    FileName="/etc/bash.bashrc"
    GetFileCon
    
    
    #检查root账户和普通账户的~/.profile
    LineSave=`$line | $ir`
    echo "    [2.2.3 ~/.profile]" | $ir
    
    echo "      [/root/.profile]" | $ir
    FileName="/root/.profile"
    GetFileCon
    
    UserFile=".profile"
    GetUserFileCon
    
    
    #检查root账户和普通账户的~/.bash_profile
    LineSave=`$line | $ir`
    echo "    [2.2.4 ~/.bash_profile]" | $ir
    
    echo "      [/root/.bash_profile]" | $ir
    FileName="/root/.bash_profile"
    GetFileCon
    
    UserFile=".bash_profile"
    GetUserFileCon
    
    
    #检查root账户和普通账户的~/.bashrc
    LineSave=`$line | $ir`
    echo "    [2.2.5 ~/.bashrc]" | $ir
    
    echo "      [/root/.bashrc]" | $ir
    FileName="/root/.bashrc"
    GetFileCon
    
    UserFile=".bashrc"
    GetUserFileCon
    
    
    #检查root账户和普通账户的~/.bash_login
    LineSave=`$line | $ir`
    echo "    [2.2.6 ~/.bash_login]" | $ir
    
    echo "      [/root/.bash_login]" | $ir
    FileName="/root/.bash_login"
    GetFileCon
    
    UserFile=".bash_login"
    GetUserFileCon
    
    
    #检查root账户和普通账户的~/.bash_logout
    LineSave=`$line | $ir`
    echo "    [2.2.7 ~/.bash_logout]" | $ir
    
    echo "      [/root/.bash_logout]" | $ir
    FileName="/root/.bash_logout"
    GetFileCon
    
    UserFile=".bash_logout"
    GetUserFileCon
    
    
    
    
    $line
    #2.3 系统服务
    LineSave=`$line | $ir`
    echo "  [2.3 System service check]" | $ir
    echo "    [2.3.1 Init]" | $ir
    
    
    #收集当前的启动级别和确认chkconfig执行路径
    RunLevel=`$by runlevel | $by awk '{print $2}'`
    echo "               [Runlevel]: $RunLevel" | $ir
    ChkCmd=`which chkconfig`
    echo "      [chkconfig cmdline]: $ChkCmd" | $ir
    
    
    LineSave=`$line | $ir`
    #收集当前启动级别下已启动的服务,busybox没有chkconfig
    echo "      [Started services]" | $ir
    #收集chkconfig命令执行路径，busybox没有chkconfig
    if [ -f $ChkCmd ] ; then
    
        #新版本使用chkconfig命令会有提示，将提示过滤
        ChkOn=`$ChkCmd 2>/dev/null | $by grep -E "$RunLevel:开|$RunLevel:on" | $ir`
        LineSave=`$line | $ir`
    
        #收集服务脚本内容
        ChkOnLine=`echo "$ChkOn" | wc -l`
        for ((n=1; n<=$ChkOnLine; n++))
        do
            ChkOnServerName=`echo "$ChkOn" | $by awk 'NR=='$n' {print $1}'`
            FileName="/etc/rc.d/init.d/$ChkOnServerName"
            echo "        [$FileName]" | $ir
            GetFileCon
        done
    else
        echo "      [chkconfig cmdline]: not exist" | $ir
        echo "        [$ChkCmd]" | $ir
    fi
    
    
    #rc.local文件内容信息收集
    LineSave=`$line | $ir`
    echo "      [/etc/rc.d/rc.local]" | $ir
    FileName="/etc/rc.d/rc.local"
    GetFileCon
    
    
    
    
    $line
    #systemd服务信息收集
    LineSave=`$line | $ir`
    echo "    [2.3.2 Systemd]" | $ir
    
    #确认systemctl执行路径
    SystemctlCmd=`which systemctl`
    echo "      [systemctl cmdline]: $SystemctlCmd" | $ir
    
    
    #收集systemctl命令执行路径，busybox没有systemctl
    if [ -f $SystemctlCmd ] ; then
    
        #收集已启动的服务
        echo "      [Started services]" | $ir
        SystemctlOn=`$SystemctlCmd list-unit-files --type service | $by grep -E "enabled|static" | $ir`
    
    
        #收集服务脚本内容
        SystemctlOnLine=`echo "$SystemctlOn" | wc -l`
        for ((i=1; i<=$SystemctlOnLine; i++))
        do
            SystemctlOnName1=`echo "$SystemctlOn" | $by awk 'NR=='$i' {print $1}'`
    
            #优先从/usr/lib/systemd/system/目录、收集Exec*=的值
            if [ -f /usr/lib/systemd/system/$SystemctlOnName1 ] ; then
                LineSave=`$line | $ir`
                echo "        [$SystemctlOnName1]" | $ir
                echo "          [/usr/lib/systemd/system/$SystemctlOnName1]" | $ir
                FilePathAll=`$by cat /usr/lib/systemd/system/$SystemctlOnName1 | $by grep "Exec" | $by awk -F "=" '{print $2}' | $by awk '{sub(/^-/,""); print}'  | $ir`
            
                #过滤Exec*=的值，只留下绝对路径，并去重
                FilePath=`echo "$FilePathAll" | $by awk -F " " '{print $1}' | $by sort | $by uniq`
                FilePathLine=`echo "$FilePath" | wc -l`
    
                #依次读取所有行的绝对路径，同时判断文件类型后放入GetFileType
                for ((a=1; a<=$FilePathLine; a++))
                do
                    GetFilePathEcho=`echo "$FilePath" | $by awk 'NR=="'$a'" {print}'`
                    FileType=`$FileCmd $GetFilePathEcho | $by awk -F ": " '{print $2}' | $by awk -F "," '{print $1}'`
                    GetFileType
                done
    
            #如果判断1无法获取则从systemctl status中获取服务配置文件的绝对路径、因为部分服务通过本方法获取[Loaded：]中的绝对路径会提示该文件不存在，因此优先在判断1中提取，1中不存在时则通过判断2提取
            else
                SystemctlOnName2=`$SystemctlCmd status $SystemctlOnName1 | $by grep "Loaded:" | $by awk '{gsub(/\(/,"");gsub(/\;/,""); print $3}'`
                if [ -f $SystemctlOnName2 ] ; then
                    LineSave=`$line | $ir`
                    echo "        [$SystemctlOnName1]" | $ir
                    echo "          [$SystemctlOnName2]" | $ir
                    FilePathAll=`$by cat $SystemctlOnName2 | $by grep "Exec" | $by awk -F "=" '{print $2}' | $by awk '{sub(/^-/,""); print}'  | $ir`
    
                    #过滤Exec*=的值，只留下绝对路径，并去重
                    FilePath=`echo "$FilePathAll" | $by awk -F " " '{print $1}' | $by sort | $by uniq`
                    FilePathLine=`echo "$FilePath" | wc -l`
    
                    #依次读取所有行的绝对路径，同时判断文件类型后放入GetFileType
                    for ((a=1; a<=$FilePathLine; a++))
                    do
                        GetFilePathEcho=`echo "$FilePath" | $by awk 'NR=="'$a'" {print}'`
                        FileType=`$FileCmd $GetFilePathEcho | $by awk -F ": " '{print $2}' | $by awk -F "," '{print $1}'`
                        GetFileType
                    done
                fi
            fi
        done
    else
        echo "      [systemctl cmdline]: not exist" | $ir
        echo "        [$SystemctlCmd]" | $ir
    fi
    
    
    
    
    #2.4 账户权限
    echo "    [2.4 Account authority]" | $ir
    #收集可以登录的账户
    if [ -f /etc/passwd ] ; then
        FileSum=`echo "/etc/passwd" >> $Temp2`
        AllAccount=`$by cat /etc/passwd | $by grep -vE ":/[a-z]+/nologin$|:/[a-z]+/shutdown$|:/[a-z]+/halt|:/[a-z]+/sync$" | $ir`
        LineSave=`$line | $ir`
    fi
    
    
    #收集该账户权限
    AccountName=`echo "$AllAccount" | $by awk -F ":" '{print $1}'`
    AccountHome=`echo "$AllAccount" | $by awk -F ":" '{print $(NF-1)}'`
    AccountNameLine=`echo "$AccountName" | wc -l`
    for ((i=1; i<=$AccountNameLine; i++))
    do
    
        #收集账户的uid、gid、group信息
        AccountNameEcho=`echo "$AccountName" | $by awk 'NR=='$i' {print}'`
        echo "      [$AccountNameEcho id]" | $ir
        AccountId=`$by id $AccountNameEcho | $ir`
    
        #收集账户的公钥信息
        AccountHomeEcho=`echo "$AccountHome" | $by awk 'NR=='$i' {print}'`
        if [ -f $AccountHomeEcho\/.ssh/authorized_keys ] ; then
            FileSum=`echo "$AccountHomeEcho\/.ssh/authorized_keys" >> $Temp2`
            KeyName=`echo "      [$AccountHomeEcho/.ssh/authorized_keys]" | $ir`
            AuthorizedKey=`$by cat $AccountHomeEcho\/.ssh/authorized_keys | $ir`
        else
            KeyName=`echo "      [$AccountHomeEcho/.ssh/authorized_keys]" | $ir`
            FileNotExist=`echo "                                                 Not exist" | $ir`
        fi
        LineSave=`$line | $ir`
    done
    
    
    
    #2.5 rootkit
    echo "    [2.5 Rootkit]" | $ir
    
    
    #检查chkrootkit版本
    ChkrootkitVerCheck(){
    
        #查看服务端和客户端的md5值
        echo "      [Chkrootkit version]" | $ir
        ChkDn=`$by nslookup ftp.pangeia.com.br 2>&1`
        DnsIp=`echo "$ChkDn" | $by awk -F ":" 'NR=="'1'" {gsub(/\t+/,""); print $2}'`
        ChkDnIp=`echo "$ChkDn" | $by grep -v "$DnsIp" | $by grep "Address" | $by awk -F ":" '{gsub(/ /,""); print $2}'`
        if [ "$ChkDnIp" = "" ] ; then
            ChkConSer=`echo "        Unable to connect ftp://ftp.pangeia.com.br/pub/seg/pac/chkrootkit.md5" | $ir`
            LineSave=`$line | $ir`
        else
            GetChkMd5File=`$by wget ftp://ftp.pangeia.com.br/pub/seg/pac/chkrootkit.md5 -O chkrootkit.md5 2>/dev/null`
            ChkMd5Ser=`$by cat chkrootkit.md5 | $by awk -F "  " '{print $1}'`
            ChkMd5Cli=`$by md5sum chkrootkit/chkrootkit.tar.gz | $by awk -F "  " '{print $1}'`
    
            #对比客户端和服务端版本是否一致
            if [ "$ChkMd5Cli" != "$ChkMd5Ser" ] ; then
                ChkEcho=`echo "        The local version of chkrootkit is not up to date,Please update yourself" | $ir`
                LineSave=`$line | $ir`
            else
                ChkEcho=`echo "        The local version of chkrootkit is up to date" | $ir`
                LineSave=`$line | $ir`
            fi
        fi
    
        #删除已下载的md5文件
        if [ -f chkrootkit.md5 ] ; then
            $by rm -rf chkrootkit.md5
        fi
    }
    
    
    #使用chkrootkit进行rootkit检查
    ChkrootkitRun(){
        echo "      [Chkrootkit check results]" | $ir
        ChkRes=`$by sh chkrootkit/chkrootkit-0.54/chkrootkit 2>/dev/null | $by grep -vE "nothing found|not found|not infected|not tested|no suspect files|ROOTDIR" | $ir`
        FileSum=`echo "$ChkRes" | $by grep -oE "^/.*+" >> $Temp2`
        LineSave=`$line | $ir`
    }
    
    
    #判断是否需要进行rootkit检查，根据匹配内容进行对应的操作
    read -ep "       Use chkrootkit to check rootkit. Chkrootkit is a third-party open source software. Need to check rootkit (y/n): " YesNo
    for ((;;))
    do
        YesNoMatch=`echo "$YesNo" | $by grep -E "^y$|^n$"`
        if [ "$YesNoMatch" = "y" ] ; then
            ChkrootkitVerCheck
            ChkrootkitRun
            break
        elif [ "$YesNoMatch" = "n" ] ; then
            LineSave=`$line | $ir`
            break
        else
            read -ep "       Use chkrootkit to check rootkit. Chkrootkit is a third-party open source software. Need to check rootkit (y/n): " YesNo
        fi
    done
    
    
    
    
    $line
    #3 痕迹
    echo "[3 Trace inspection]" | $ir
    #3.1 登录日志
    echo "  [3.1 Secure log]" | $ir
    
    
    #登陆成功的记录
    echo "    [Login successful]" | $ir
    LoginS=`$by last | $ir`
    LineSave=`$line | $ir`
    
    
    #在线的账户
    echo "    [Online account]" | $ir
    OnlineA=`$by last | $by grep "logged in" | $ir`
    LineSave=`$line | $ir`
    
    
    #登陆失败汇总信息
    echo "    [Login failed summary]" | $ir
    LoginF=`$by grep "Failed password" /var/log/secure* | $by awk -F ":" '{$1=""; print}' | $by awk '{print $(NF-5),"\t",$(NF-3)}' | $by uniq -c | $by sort -r | $ir`
    LineSave=`$line | $ir`
    
    
    #具体的登陆失败事件
    echo "    [Login failed time]" | $ir
    LastCon=`$by grep "Failed password" /var/log/secure* | $by awk -F ":" '{$1=""; print}' | $by awk '{print $(NF-5),"\t",$(NF-3),"\t",$1,$2,"\t",$3,":",$4,":",$5}' | $ir`
    LineSave=`$line | $ir`
    
    
    
    
    #3.2 文件落地
    echo "  [3.2 Document landing]" | $ir
    echo "    [FileTime]" | $ir
    
    #判断是否需要根据时间检查文件，根据匹配内容进行对应的操作
    read -ep "      Is it necessary to check the documents according to the time(y/n): " YesNo
    for ((;;))
    do
        YesNoMatch=`echo "$YesNo" | $by grep -E "^y$|^n$"`
        if [ "$YesNoMatch" = "y" ] ; then
            getFileTime=`./getFileTime.sh | $ir`
            FileSum=`echo "$getFileTime" | $by grep -oE "^/.*+" >> $Temp2`
            LineSave=`$line | $ir`
            break
        elif [ "$YesNoMatch" = "n" ] ; then
            LineSave=`$line | $ir`
            break
        else
            read -ep "      Is it necessary to check the documents according to the time(y/n): " YesNo
        fi
    done
    
    
    #针对webshell进行检查
    echo "    [Hm]" | $ir
    #检查hm版本
    HmVerCheck(){
        echo "    [Hm version]" | $ir
        HmVer=`hm/hm-linux-amd64/hm update | $ir`
        LineSave=`$line | $ir`
    }
    
    
    #使用Hm在指定的目录深度扫描WEBSHELL
    HmRun(){
        read -ep "      Please enter the web directory(/paht1/path2/pathN): " WebPath
        for ((;;))
        do
            if [ "$WebPath" != "" ] && [[ -d $WebPath || -f $WebPath ]] ; then
                break
            else
                read -ep "      Please enter the web directory(/paht1/path2/pathN): " WebPath
            fi
        done 
    
        echo "    [Hm check results]" | $ir
        HmRes=`hm/hm-linux-amd64/hm deepscan $WebPath 2>/dev/null >> $Temp`
        FileSum=`echo "$HmRes" | $by awk -F "," '{print $NF}' | $by grep -oE "^/.*+" >> $Temp2`
        HmResSave=`$by cat $Temp | $by grep -E "^\+------|^\| 类型|^\| 后门|^\| 疑似|^\|          总计" | $ir`
        HmResEcho=`$by cat hm/hm-linux-amd64/result.csv | $by awk '{if (NR>1) print}' | $ir`
        LineSave=`$line | $ir`
    
        
        #删除cache.db，未联网状态下会在当前目录下生成
        if [ -f cache.db ] ; then
            $by rm -rf cache.db
        fi
    
    
        #删除临时文件
        if [ -f $Temp ] ; then
            $by rm -rf $Temp
        fi
    }
    
    
    #判断是否需要进行webshell检查，根据匹配内容进行对应的操作
    read -ep "      Use Hm to check webshell.Hm is a third party software.Need to check webshell(y/n): " YesNo
    for ((;;))
    do
        YesNoMatch=`echo "$YesNo" | $by grep -E "^y$|^n$"`
        if [ "$YesNoMatch" = "y" ] ; then
            HmVerCheck
            HmRun
            break
        elif [ "$YesNoMatch" = "n" ] ; then
            LineSave=`$line | $ir`
            break
        else
            read -ep "      Use Hm to check webshell.Hm is a third party software.Need to check webshell(y/n): " YesNo
        fi
    done
    
    
    
    
    #3.3 历史命令
    echo "  [3.3 History]" | $ir
    
    
    #收集root账户bash的历史命令
    echo "      [/root/.bash_history]" | $ir
        if [ -f /root/.bash_history ] ; then
    	CatFile=`$by cat /root/.bash_history >> $HostIp-$SystemDate-results/2-root-history.txt`
            CatFileEcho=`echo "        Root history command saved to [$HostIp-$SystemDate-results/2-root-history.txt]"`
        else
            FileNotExist=`echo "                                                 Not exist" | $ir`
        fi
    
    
    #收集普通账户bash的历史命令
    for ((n=1; n<=$UserHomeLine; n++))
    do
        UserHomeName=`echo "$UserHome" | $by awk 'NR=='$n' {print}'`
        FileName=`echo "/home/$UserHomeName/.bash_history"`
        LineSave=`$line | $ir`
        echo "      [$FileName]" | $ir
        if [ -f $FileName ] ; then
            CatFile=`$by cat $FileName >> $HostIp-$SystemDate-results/2-$UserHomeName-history.txt`
            CatFileEcho=`echo "        Root history command saved to [$HostIp-$SystemDate-results/2-$UserHomeName-history.txt]"`
        else
            FileNotExist=`echo "                                                 Not exist" | $ir`
        fi
    done
    
    
    #3.4 防火墙
    echo "  [3.4 Firewall]" | $ir
    
    echo "    [iptables]" | $ir
    FileName="/etc/sysconfig/iptables"
    FileSum=`echo "$FileName" >> $Temp2`
    CatFileCon
    
    
    LineSave=`$line | $ir`
    echo "    [Firewalld]" | $ir
    FileName="/etc/firewalld/zones/public.xml"
    FileSum=`echo "$FileName" >> $Temp2`
    CatFileCon
    
    
    
    
    #将检查过的文件进行汇总信息记录，包括文件的类型、md5、访问时间、修改时间、状态时间
    $line
    echo "The checked files are being summarized and recorded"
    GetFileSum
    
    
    #将检查结果的md5生成并保存
    echo "Generating and saving MD5 of check results to [$HostIp-$SystemDate-results/md5.txt]"
    ReMd5=`$by md5sum $HostIp-$SystemDate-results/* >> $HostIp-$SystemDate-results/md5.txt`
    
    
    #将检查结果打包，如需要可以删除注释
    #$line
    #echo "Packing check results"
    #ReTar=`$by tar zcvf $HostIp-$SystemDate-results.tar.gz $HostIp-$SystemDate-results`
    #$line
    

### 6.3 IncidentResponse/getFileTime.sh说明

该工具可结合使用，也可以单独使用，作用于检查指定时间范围内的文件。

    
    
    #!/bin/bash
    
    
    #判断busybox是否存在，如不存在也不会影响脚本执行
    if [ -f ./busybox ] ; then
        by="./busybox"
    fi
    
    
    line="echo -e \n-------------------------------------------------\n-------------------------------------------------"
    
    
    
    
    #获取合法的绝对路径
    PathNameCon(){
        read -ep "        Please enter the absolute path to match     (/path1/path2/pathN): " GetPathName
        for ((;;))
        do
            if [ "$GetPathName" != "" ] && [ -d $GetPathName ] ; then
                break
            else
                read -ep "        Please enter the absolute path to match     (/path1/path2/pathN): " GetPathName
            fi
        done
    }
    
    
    
    
    #获取不为空的关键字
    KeyWordCon(){
        read -ep "        Please enter a keyword to match                     (* or *.php): " GetKeyWord
        for ((;;))
        do
            if [ "$GetKeyWord" != "" ] ; then
                break
            else
                read -ep "        Please enter a keyword to match                     (* or *.php): " GetKeyWord
            fi
        done
    }
    
    
    
    
    #获取开始时间，开始时间不可以比结束时间大（未作匹配，只注释说明）
    StartTimeCon(){
        read -ep "        Please enter the start time                (2021-01-01 00:00:00): " StartTime
        for ((;;))
        do
            GetStartTime=`echo "$StartTime" | $by grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}$"`
            if [ "$GetStartTime" != "" ] ; then
                break
            else
                read -ep "        Please enter the start time                (2021-01-01 00:00:00): " StartTime
            fi
        done
    }
    
    
    
    
    #获取结束时间
    EndTimeCon(){
        read -ep "        Please enter the end time                  (2021-01-01 23:59:59): " EndTime
        for ((;;))
        do
            GetEndTime=`echo "$EndTime" | $by grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}$"`
            if [ "$GetEndTime" != "" ] ; then
                break
            else
                read -ep "        Please enter the end time                  (2021-01-01 23:59:59): " EndTime
            fi
        done
    }
    
    
    #busybox的find不支持-newerXt
    #需要注意的是newerat，newermt，newerct不会匹配起止时间，即“00:00:00”和“23:59:59”，但是区间时间“00:00:01~23:59:58”会被匹配。
    
    #检查文件的Atime
    GetFileAtime(){             #使用单引号包围$GetKeyWord的值并进行调用，将$GetStartTime、$GetEndTime的值当做一个整体，否则空格两边的内容会被拆分
        find $GetPathName -name "$GetKeyWord" -newerat "$GetStartTime" ! -newerat "$GetEndTime"
    }
    
    
    #检查文件的Mtime
    GetFileMtime(){
        find $GetPathName -name "$GetKeyWord" -newermt "$GetStartTime" ! -newermt "$GetEndTime"
    }
    
    
    #检查文件的Ctime
    GetFileCtime(){
        find $GetPathName -name "$GetKeyWord" -newerct "$GetStartTime" ! -newerct "$GetEndTime"
    }
    
    
    
    
    #将值排序去重
    ConSummary(){
        PathNameCon
        KeyWordCon
        StartTimeCon
        EndTimeCon
        echo ""
        echo "    TimeType : $AMC"
        echo "    Path     : $GetPathName"
        echo "    KeyWord  : $GetKeyWord"
        echo "    StartTime: $GetStartTime"
        echo "    EndTime  : $GetEndTime"
        echo ""
        echo "    Matched  : "
        echo ""
    }
    
    GetA(){
        GetFileAtime
    }
    
    
    GetM(){
        GetFileMtime
    }
    
    
    GetC(){
        GetFileCtime
    }
    
    
    GetAM(){
        GetFileAtime
        GetFileMtime
    }
    
    
    GetAC(){
        GetFileAtime
        GetFileCtime
    }
    
    
    GetMC(){
        GetFileMtime
        GetFileCtime
    }
    
    
    GetAMC(){
        GetFileAtime
        GetFileMtime
        GetFileCtime
    }
    
    
    
    
    #根据给定的路径、关键字（如有）、开始时间、结束时间进行检查
    read -ep "      What kind of (AMC)time do you need to check  (/a/m/c/am/ac/mc/amc): " AMC   #建议选择amc，因为会对重复的结果进行去重
    for ((;;))
    do
        GetAMC=`echo "$AMC" | $by grep -E "|a|m|c|am|ac|mc|amc"`
        if [ "$GetAMC" != "" ] ; then
            if [ "$GetAMC" = "a" ] ; then
                ConSummary
                GetA                                        | $by sort | $by uniq
                break
            elif [ "$GetAMC" = "m" ] ; then
                ConSummary
                GetM                                        | $by sort | $by uniq
                break
            elif [ "$GetAMC" = "c" ] ; then
                ConSummary
                GetC                                        | $by sort | $by uniq
                break
            elif [ "$GetAMC" = "am" ] ; then
                ConSummary
                GetAM                                       | $by sort | $by uniq
                break
            elif [ "$GetAMC" = "ac" ] ; then
                ConSummary
                GetAC                                       | $by sort | $by uniq
                break
            elif [ "$GetAMC" = "mc" ] ; then
                ConSummary
                GetMC                                       | $by sort | $by uniq
                break
            elif [ "$GetAMC" = "amc" ] ; then
                ConSummary
                GetAMC                                      | $by sort | $by uniq
                break
            else
                read -ep "      What kind of (AMC)time do you need to check  (/a/m/c/am/ac/mc/amc): " AMC
            fi
        else
            read -ep "      What kind of (AMC)time do you need to check  (/a/m/c/am/ac/mc/amc): " AMC
        fi
    done
    

### 6.4 工具执行结果

部分场景需要进行数字取证，因此加上md5。

    
    
    [root@localhost IncidentResponse]# ll 1.1.1.1-2021-04-20-results/
    总用量 172
    -rw-r--r-- 1 root root 108571 4月  20 19:40 0-Summary_results.txt
    -rw-r--r-- 1 root root  13789 4月  20 19:40 1-FileSumInfoResult.txt
    -rw-r--r-- 1 root root    219 4月  20 19:40 2-gmlii-history.txt
    -rw-r--r-- 1 root root  37352 4月  20 19:40 2-root-history.txt
    -rw-r--r-- 1 root root    329 4月  20 19:40 md5.txt

### 6.5 工具运行时输出

    
    
    [root@localhost IncidentResponse]# sh start.sh 
    To create a check folder, please enter the host IP address(x.x.x.x): 1.1.1.1
    
    -------------------------------------------------    -------------------------------------------------    Check that the folder was created successfully: [ 1.1.1.1-2021-04-20-results ]
    
    -------------------------------------------------    -------------------------------------------------    [1 Phenomenon inspection]
      [1.1 Monitored port]
      [1.2 Connection established]
      [1.3-1 System process(ps)]
      [1.3-2 System process(busybox)]
      [1.3-3 System process(/proc/$pid/exe)]
    
    -------------------------------------------------    -------------------------------------------------    [2 Persistence inspection]
      [2.1 Task plan check results]
        [2.1.1 /etc/crontab]
        [2.1.2 /var/spool/cron/*]
        [2.1.3 /etc/cron.d/*]
        [2.1.4 /etc/anacrontab]
    
    -------------------------------------------------    -------------------------------------------------      [2.2 Environmental variable check]
        [2.2.1 /etc/profile]
          [/etc/ld.so.preload]
        [2.2.2-1 /etc/bashrc]
        [2.2.2-2 /etc/bash.bashrc]
        [2.2.3 ~/.profile]
          [/root/.profile]
          [/home/test/.profile]
          [/home/gmlii/.profile]
        [2.2.4 ~/.bash_profile]
          [/root/.bash_profile]
          [/home/test/.bash_profile]
          [/home/gmlii/.bash_profile]
        [2.2.5 ~/.bashrc]
          [/root/.bashrc]
          [/home/test/.bashrc]
          [/home/gmlii/.bashrc]
        [2.2.6 ~/.bash_login]
          [/root/.bash_login]
          [/home/test/.bash_login]
          [/home/gmlii/.bash_login]
        [2.2.7 ~/.bash_logout]
          [/root/.bash_logout]
          [/home/test/.bash_logout]
          [/home/gmlii/.bash_logout]
    
    -------------------------------------------------    -------------------------------------------------      [2.3 System service check]
        [2.3.1 Init]
                   [Runlevel]: 3
          [chkconfig cmdline]: /usr/sbin/chkconfig
          [Started services]
            [/etc/rc.d/init.d/network]
          [/etc/rc.d/rc.local]
    
    -------------------------------------------------    -------------------------------------------------        [2.3.2 Systemd]
          [systemctl cmdline]: /usr/bin/systemctl
          [Started services]
            [auditd.service]
              [/usr/lib/systemd/system/auditd.service]
            [autovt@.service]
              [/usr/lib/systemd/system/autovt@.service]
            [brandbot.service]
              [/usr/lib/systemd/system/brandbot.service]
            [container-getty@.service]
              [/usr/lib/systemd/system/container-getty@.service]
            [crond.service]
              [/usr/lib/systemd/system/crond.service]
            [dbus-org.fedoraproject.FirewallD1.service]
              [/usr/lib/systemd/system/firewalld.service]
            [dbus-org.freedesktop.hostname1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.hostname1.service]
            [dbus-org.freedesktop.import1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.import1.service]
            [dbus-org.freedesktop.locale1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.locale1.service]
            [dbus-org.freedesktop.login1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.login1.service]
            [dbus-org.freedesktop.machine1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.machine1.service]
            [dbus-org.freedesktop.NetworkManager.service]
              [/usr/lib/systemd/system/NetworkManager.service]
            [dbus-org.freedesktop.nm-dispatcher.service]
              [/usr/lib/systemd/system/NetworkManager-dispatcher.service]
            [dbus-org.freedesktop.timedate1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.timedate1.service]
            [dbus.service]
              [/usr/lib/systemd/system/dbus.service]
            [dracut-cmdline.service]
              [/usr/lib/systemd/system/dracut-cmdline.service]
            [dracut-initqueue.service]
              [/usr/lib/systemd/system/dracut-initqueue.service]
            [dracut-mount.service]
              [/usr/lib/systemd/system/dracut-mount.service]
            [dracut-pre-mount.service]
              [/usr/lib/systemd/system/dracut-pre-mount.service]
            [dracut-pre-pivot.service]
              [/usr/lib/systemd/system/dracut-pre-pivot.service]
            [dracut-pre-trigger.service]
              [/usr/lib/systemd/system/dracut-pre-trigger.service]
            [dracut-pre-udev.service]
              [/usr/lib/systemd/system/dracut-pre-udev.service]
            [dracut-shutdown.service]
              [/usr/lib/systemd/system/dracut-shutdown.service]
            [emergency.service]
              [/usr/lib/systemd/system/emergency.service]
            [firewalld.service]
              [/usr/lib/systemd/system/firewalld.service]
            [fstrim.service]
              [/usr/lib/systemd/system/fstrim.service]
            [getty@.service]
              [/usr/lib/systemd/system/getty@.service]
            [halt-local.service]
              [/usr/lib/systemd/system/halt-local.service]
            [initrd-cleanup.service]
              [/usr/lib/systemd/system/initrd-cleanup.service]
            [initrd-parse-etc.service]
              [/usr/lib/systemd/system/initrd-parse-etc.service]
            [initrd-switch-root.service]
              [/usr/lib/systemd/system/initrd-switch-root.service]
            [initrd-udevadm-cleanup-db.service]
              [/usr/lib/systemd/system/initrd-udevadm-cleanup-db.service]
            [irqbalance.service]
              [/usr/lib/systemd/system/irqbalance.service]
            [kdump.service]
              [/usr/lib/systemd/system/kdump.service]
            [kmod-static-nodes.service]
              [/usr/lib/systemd/system/kmod-static-nodes.service]
            [messagebus.service]
              [/usr/lib/systemd/system/messagebus.service]
            [microcode.service]
              [/usr/lib/systemd/system/microcode.service]
            [NetworkManager-dispatcher.service]
              [/usr/lib/systemd/system/NetworkManager-dispatcher.service]
            [NetworkManager-wait-online.service]
              [/usr/lib/systemd/system/NetworkManager-wait-online.service]
            [NetworkManager.service]
              [/usr/lib/systemd/system/NetworkManager.service]
            [ntpd.service]
              [/usr/lib/systemd/system/ntpd.service]
            [ntpdate.service]
              [/usr/lib/systemd/system/ntpdate.service]
            [plymouth-switch-root.service]
              [/usr/lib/systemd/system/plymouth-switch-root.service]
            [polkit.service]
              [/usr/lib/systemd/system/polkit.service]
            [postfix.service]
              [/usr/lib/systemd/system/postfix.service]
            [quotaon.service]
              [/usr/lib/systemd/system/quotaon.service]
            [rc-local.service]
              [/usr/lib/systemd/system/rc-local.service]
            [rescue.service]
              [/usr/lib/systemd/system/rescue.service]
            [rhel-autorelabel.service]
              [/usr/lib/systemd/system/rhel-autorelabel.service]
            [rhel-configure.service]
              [/usr/lib/systemd/system/rhel-configure.service]
            [rhel-dmesg.service]
              [/usr/lib/systemd/system/rhel-dmesg.service]
            [rhel-domainname.service]
              [/usr/lib/systemd/system/rhel-domainname.service]
            [rhel-import-state.service]
              [/usr/lib/systemd/system/rhel-import-state.service]
            [rhel-loadmodules.service]
              [/usr/lib/systemd/system/rhel-loadmodules.service]
            [rhel-readonly.service]
              [/usr/lib/systemd/system/rhel-readonly.service]
            [rsyslog.service]
              [/usr/lib/systemd/system/rsyslog.service]
            [selinux-policy-migrate-local-changes@.service]
              [/usr/lib/systemd/system/selinux-policy-migrate-local-changes@.service]
            [sshd-keygen.service]
              [/usr/lib/systemd/system/sshd-keygen.service]
            [sshd.service]
              [/usr/lib/systemd/system/sshd.service]
            [sshd@.service]
              [/usr/lib/systemd/system/sshd@.service]
            [systemd-ask-password-console.service]
              [/usr/lib/systemd/system/systemd-ask-password-console.service]
            [systemd-ask-password-plymouth.service]
              [/usr/lib/systemd/system/systemd-ask-password-plymouth.service]
            [systemd-ask-password-wall.service]
              [/usr/lib/systemd/system/systemd-ask-password-wall.service]
            [systemd-backlight@.service]
              [/usr/lib/systemd/system/systemd-backlight@.service]
            [systemd-binfmt.service]
              [/usr/lib/systemd/system/systemd-binfmt.service]
            [systemd-firstboot.service]
              [/usr/lib/systemd/system/systemd-firstboot.service]
            [systemd-fsck-root.service]
              [/usr/lib/systemd/system/systemd-fsck-root.service]
            [systemd-fsck@.service]
              [/usr/lib/systemd/system/systemd-fsck@.service]
            [systemd-halt.service]
              [/usr/lib/systemd/system/systemd-halt.service]
            [systemd-hibernate-resume@.service]
              [/usr/lib/systemd/system/systemd-hibernate-resume@.service]
            [systemd-hibernate.service]
              [/usr/lib/systemd/system/systemd-hibernate.service]
            [systemd-hostnamed.service]
              [/usr/lib/systemd/system/systemd-hostnamed.service]
            [systemd-hwdb-update.service]
              [/usr/lib/systemd/system/systemd-hwdb-update.service]
            [systemd-hybrid-sleep.service]
              [/usr/lib/systemd/system/systemd-hybrid-sleep.service]
            [systemd-importd.service]
              [/usr/lib/systemd/system/systemd-importd.service]
            [systemd-initctl.service]
              [/usr/lib/systemd/system/systemd-initctl.service]
            [systemd-journal-catalog-update.service]
              [/usr/lib/systemd/system/systemd-journal-catalog-update.service]
            [systemd-journal-flush.service]
              [/usr/lib/systemd/system/systemd-journal-flush.service]
            [systemd-journald.service]
              [/usr/lib/systemd/system/systemd-journald.service]
            [systemd-kexec.service]
              [/usr/lib/systemd/system/systemd-kexec.service]
            [systemd-localed.service]
              [/usr/lib/systemd/system/systemd-localed.service]
            [systemd-logind.service]
              [/usr/lib/systemd/system/systemd-logind.service]
            [systemd-machine-id-commit.service]
              [/usr/lib/systemd/system/systemd-machine-id-commit.service]
            [systemd-machined.service]
              [/usr/lib/systemd/system/systemd-machined.service]
            [systemd-modules-load.service]
              [/usr/lib/systemd/system/systemd-modules-load.service]
            [systemd-poweroff.service]
              [/usr/lib/systemd/system/systemd-poweroff.service]
            [systemd-quotacheck.service]
              [/usr/lib/systemd/system/systemd-quotacheck.service]
            [systemd-random-seed.service]
              [/usr/lib/systemd/system/systemd-random-seed.service]
            [systemd-readahead-collect.service]
              [/usr/lib/systemd/system/systemd-readahead-collect.service]
            [systemd-readahead-drop.service]
              [/usr/lib/systemd/system/systemd-readahead-drop.service]
            [systemd-readahead-replay.service]
              [/usr/lib/systemd/system/systemd-readahead-replay.service]
            [systemd-reboot.service]
              [/usr/lib/systemd/system/systemd-reboot.service]
            [systemd-remount-fs.service]
              [/usr/lib/systemd/system/systemd-remount-fs.service]
            [systemd-rfkill@.service]
              [/usr/lib/systemd/system/systemd-rfkill@.service]
            [systemd-shutdownd.service]
              [/usr/lib/systemd/system/systemd-shutdownd.service]
            [systemd-suspend.service]
              [/usr/lib/systemd/system/systemd-suspend.service]
            [systemd-sysctl.service]
              [/usr/lib/systemd/system/systemd-sysctl.service]
            [systemd-timedated.service]
              [/usr/lib/systemd/system/systemd-timedated.service]
            [systemd-tmpfiles-clean.service]
              [/usr/lib/systemd/system/systemd-tmpfiles-clean.service]
            [systemd-tmpfiles-setup-dev.service]
              [/usr/lib/systemd/system/systemd-tmpfiles-setup-dev.service]
            [systemd-tmpfiles-setup.service]
              [/usr/lib/systemd/system/systemd-tmpfiles-setup.service]
            [systemd-udev-settle.service]
              [/usr/lib/systemd/system/systemd-udev-settle.service]
            [systemd-udev-trigger.service]
              [/usr/lib/systemd/system/systemd-udev-trigger.service]
            [systemd-udevd.service]
              [/usr/lib/systemd/system/systemd-udevd.service]
            [systemd-update-done.service]
              [/usr/lib/systemd/system/systemd-update-done.service]
            [systemd-update-utmp-runlevel.service]
              [/usr/lib/systemd/system/systemd-update-utmp-runlevel.service]
            [systemd-update-utmp.service]
              [/usr/lib/systemd/system/systemd-update-utmp.service]
            [systemd-user-sessions.service]
              [/usr/lib/systemd/system/systemd-user-sessions.service]
            [systemd-vconsole-setup.service]
              [/usr/lib/systemd/system/systemd-vconsole-setup.service]
            [teamd@.service]
              [/usr/lib/systemd/system/teamd@.service]
            [tuned.service]
              [/usr/lib/systemd/system/tuned.service]
            [vgauthd.service]
              [/usr/lib/systemd/system/vgauthd.service]
            [vmtoolsd.service]
              [/usr/lib/systemd/system/vmtoolsd.service]
        [2.4 Account authority]
          [root id]
          [gmlii id]
          [test id]
        [2.5 Rootkit]
           Use chkrootkit to check rootkit. Chkrootkit is a third-party open source software. Need to check rootkit (y/n): y
          [Chkrootkit version]
          [Chkrootkit check results]
    
    -------------------------------------------------    -------------------------------------------------    [3 Trace inspection]
      [3.1 Secure log]
        [Login successful]
        [Online account]
        [Login failed summary]
        [Login failed time]
      [3.2 Document landing]
        [FileTime]
          Is it necessary to check the documents according to the time(y/n): y
          What kind of (AMC)time do you need to check  (/a/m/c/am/ac/mc/amc): amc
            Please enter the absolute path to match     (/path1/path2/pathN): /tmp/
            Please enter a keyword to match                     (* or *.php): *
            Please enter the start time                (2021-01-01 00:00:00): 2021-01-01 00:00:00
            Please enter the end time                  (2021-01-01 23:59:59): 2022-01-01 00:00:00
        [Hm]
          Use Hm to check webshell.Hm is a third party software.Need to check webshell(y/n): y
        [Hm version]
          Please enter the web directory(/paht1/path2/pathN): /tmp/
        [Hm check results]
      [3.3 History]
          [/root/.bash_history]
          [/home/test/.bash_history]
          [/home/gmlii/.bash_history]
      [3.4 Firewall]
        [iptables]
        [Firewalld]
    
    -------------------------------------------------    -------------------------------------------------    The checked files are being summarized and recorded
    Generating and saving MD5 of check results to [1.1.1.1-2021-04-20-results/md5.txt]
    

### 6.6 工具运行后输出

典型场景1：检查某个进程的自启动方式，cat | grep xxx 即可直接发现

典型场景2：应急响应时主机数过多

典型场景3：日常巡检，在其基础上增删维度，以形成自己的标准化检查流程

    
    
    [1 Phenomenon inspection]
      [1.1 Monitored port]
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
    tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      6811/sshd
    tcp        0      0 127.0.0.1:25            0.0.0.0:*               LISTEN      6920/master
    tcp        0      0 :::22                   :::*                    LISTEN      6811/sshd
    tcp        0      0 ::1:25                  :::*                    LISTEN      6920/master
    
    -------------------------------------------------    -------------------------------------------------      [1.2 Connection established]
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
    tcp        0      0 192.168.11.100:22       192.168.11.1:50308      ESTABLISHED 12889/0
    tcp        0      0 192.168.11.100:22       192.168.11.1:50620      ESTABLISHED 13397/2
    tcp        0      0 192.168.11.100:22       192.168.11.1:55773      ESTABLISHED 45208/sshd: root@no
    
    -------------------------------------------------    -------------------------------------------------      [1.3-1 System process(ps)]
    USER        PID   PPID TT       %CPU %MEM                  STARTED     ELAPSED CMD
    root          2      0 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47 [kthreadd]
    root          3      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [ksoftirqd/0]
    root          5      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [kworker/0:0H]
    root          7      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [migration/0]
    root          8      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [rcu_bh]
    root          9      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [rcu_sched]
    root         10      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [lru-add-drain]
    root         11      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [watchdog/0]
    root         13      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [kdevtmpfs]
    root         14      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [netns]
    root         15      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [khungtaskd]
    root         16      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [writeback]
    root         17      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [kintegrityd]
    root         18      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [bioset]
    root         19      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [bioset]
    root         20      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [bioset]
    root         21      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [kblockd]
    root         22      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [md]
    root         23      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [edac-poller]
    root         24      2 ?         0.0  0.0 Mon Apr 19 22:41:01 2021    20:58:47   [watchdogd]
    root         30      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [kswapd0]
    root         31      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [ksmd]
    root         32      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [khugepaged]
    root         33      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [crypto]
    root         41      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [kthrotld]
    root         43      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [kmpath_rdacd]
    root         44      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [kaluad]
    root         45      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [kpsmoused]
    root         47      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [ipv6_addrconf]
    root         60      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [deferwq]
    root         92      2 ?         0.0  0.0 Mon Apr 19 22:41:02 2021    20:58:46   [kauditd]
    root        632      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [ata_sff]
    root        637      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [mpt_poll_0]
    root        641      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [mpt/0]
    root        688      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [scsi_eh_0]
    root        694      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [scsi_tmf_0]
    root        717      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [scsi_eh_1]
    root        723      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [scsi_tmf_1]
    root        731      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [scsi_eh_2]
    root        732      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [scsi_tmf_2]
    root        794      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [ttm_swap]
    root        802      2 ?         0.0  0.0 Mon Apr 19 22:41:03 2021    20:58:45   [irq/16-vmwgfx]
    root       1682      2 ?         0.0  0.0 Mon Apr 19 22:41:04 2021    20:58:44   [nfit]
    root       2860      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [bioset]
    root       2865      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfsalloc]
    root       2870      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfs_mru_cache]
    root       2873      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfs-buf/sda2]
    root       2876      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfs-data/sda2]
    root       2879      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfs-conv/sda2]
    root       2880      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfs-cil/sda2]
    root       2881      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfs-reclaim/sda]
    root       2882      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfs-log/sda2]
    root       2883      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfs-eofblocks/s]
    root       2884      2 ?         0.0  0.0 Mon Apr 19 22:41:07 2021    20:58:41   [xfsaild/sda2]
    root       2885      2 ?         0.0  0.0 Mon Apr 19 22:41:08 2021    20:58:40   [kworker/0:1H]
    root       8760      2 ?         0.0  0.0 Tue Apr 20 09:06:36 2021    10:33:12   [kworker/u256:1]
    root      69827      2 ?         0.0  0.0 Tue Apr 20 14:00:47 2021    05:39:01   [kworker/u256:2]
    root      50297      2 ?         0.0  0.0 Tue Apr 20 19:04:13 2021       35:35   [kworker/0:3]
    root      93769      2 ?         0.0  0.0 Tue Apr 20 19:34:18 2021       05:30   [kworker/0:2]
    root      94014      2 ?         0.0  0.0 Tue Apr 20 19:39:19 2021       00:29   [kworker/0:0]
    root          1      0 ?         0.0  0.3 Mon Apr 19 22:41:01 2021    20:58:47 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
    root       2950      1 ?         0.0  0.4 Mon Apr 19 22:41:27 2021    20:58:21   /usr/lib/systemd/systemd-journald
    root       2975      1 ?         0.0  0.3 Mon Apr 19 22:41:28 2021    20:58:20   /usr/lib/systemd/systemd-udevd
    polkitd    4890      1 ?         0.0  1.4 Mon Apr 19 22:41:35 2021    20:58:13   /usr/lib/polkit-1/polkitd --no-debug
    root       5198      1 ?         0.0  0.6 Mon Apr 19 22:41:35 2021    20:58:13   /usr/bin/VGAuthService -s
    root       5199      1 ?         0.0  0.6 Mon Apr 19 22:41:35 2021    20:58:13   /usr/bin/vmtoolsd
    root       5200      1 ?         0.0  0.1 Mon Apr 19 22:41:35 2021    20:58:13   /usr/lib/systemd/systemd-logind
    dbus       5201      1 ?         0.0  0.2 Mon Apr 19 22:41:35 2021    20:58:13   /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation
    root       6356      1 ?         0.0  1.1 Mon Apr 19 22:41:50 2021    20:57:58   /usr/sbin/NetworkManager --no-daemon
    root       6811      1 ?         0.0  0.4 Mon Apr 19 22:42:05 2021    20:57:43   /usr/sbin/sshd -D
    root      12889   6811 ?         0.0  0.5 Tue Apr 20 10:28:42 2021    09:11:06     sshd: root@pts/0
    root      12891  12889 pts/0     0.0  0.2 Tue Apr 20 10:28:43 2021    09:11:05       -bash
    root      94040  12891 pts/0     0.0  0.1 Tue Apr 20 19:39:47 2021       00:01         sh start.sh
    root      94080  94040 pts/0     0.0  0.0 Tue Apr 20 19:39:48 2021       00:00           sh start.sh
    root      94081  94080 pts/0     0.0  0.1 Tue Apr 20 19:39:48 2021       00:00             /usr/bin/ps -Heo user,pid,ppid,tty,%cpu,%mem,lstart,etime,cmd
    root      94082  94080 pts/0     0.0  0.0 Tue Apr 20 19:39:48 2021       00:00             sh start.sh
    root      13397   6811 ?         0.0  0.5 Tue Apr 20 10:37:59 2021    09:01:49     sshd: root@pts/2
    root      13399  13397 pts/2     0.0  0.2 Tue Apr 20 10:37:59 2021    09:01:49       -bash
    root      45208   6811 ?         0.0  0.5 Tue Apr 20 18:17:40 2021    01:22:08     sshd: root@notty
    root      45211  45208 ?         0.0  0.2 Tue Apr 20 18:17:41 2021    01:22:07       /usr/libexec/openssh/sftp-server
    root      45231  45208 ?         0.0  0.2 Tue Apr 20 18:17:58 2021    01:21:50       /usr/libexec/openssh/sftp-server
    root       6812      1 ?         0.0  1.7 Mon Apr 19 22:42:05 2021    20:57:43   /usr/bin/python2 -Es /usr/sbin/tuned -l -P
    root       6819      1 ?         0.0  0.5 Mon Apr 19 22:42:05 2021    20:57:43   /usr/sbin/rsyslogd -n
    root       6920      1 ?         0.0  0.2 Mon Apr 19 22:42:07 2021    20:57:41   /usr/libexec/postfix/master -w
    postfix    6926   6920 ?         0.0  0.4 Mon Apr 19 22:42:07 2021    20:57:41     qmgr -l -t unix -u
    postfix   44996   6920 ?         0.0  0.4 Tue Apr 20 18:13:25 2021    01:26:23     pickup -l -t unix -u
    root       7040      1 ?         0.0  0.1 Mon Apr 19 22:42:08 2021    20:57:40   /usr/sbin/crond -n
    ntp        7084      1 ?         0.0  0.2 Mon Apr 19 22:42:09 2021    20:57:39   /usr/sbin/ntpd -u ntp:ntp -g
    root      46843      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46844      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46845      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46846      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46847      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46848      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46849      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46850      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46851      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46852      1 ?         0.0  0.1 Tue Apr 20 02:45:15 2021    16:54:33   ping 127.0.0.1
    root      46856      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46857      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46858      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46859      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46860      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46861      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46862      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46863      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46864      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46865      1 ?         0.0  0.1 Tue Apr 20 02:45:33 2021    16:54:15   ping 127.0.0.1
    root      46868      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46869      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46870      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46871      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46872      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46873      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46874      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46875      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46876      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46877      1 ?         0.0  0.1 Tue Apr 20 02:45:34 2021    16:54:14   ping 127.0.0.1
    root      46880      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46881      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46882      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46883      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46884      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46885      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46886      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46887      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46888      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      46889      1 ?         0.0  0.1 Tue Apr 20 02:45:36 2021    16:54:12   ping 127.0.0.1
    root      21577      1 tty1      0.0  0.0 Tue Apr 20 13:23:36 2021    06:16:12   /sbin/agetty --noclear tty1 linux
    
    -------------------------------------------------    -------------------------------------------------      [1.3-2 System process(busybox)]
    1		root		 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
    2950		root		 /usr/lib/systemd/systemd-journald
    2975		root		 /usr/lib/systemd/systemd-udevd
    4890		polkitd		 /usr/lib/polkit-1/polkitd --no-debug
    5198		root		 /usr/bin/VGAuthService -s
    5199		root		 /usr/bin/vmtoolsd
    5200		root		 /usr/lib/systemd/systemd-logind
    5201		dbus		 /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation
    6356		root		 /usr/sbin/NetworkManager --no-daemon
    6811		root		 /usr/sbin/sshd -D
    6812		root		 {tuned} /usr/bin/python2 -Es /usr/sbin/tuned -l -P
    6819		root		 /usr/sbin/rsyslogd -n
    6920		root		 /usr/libexec/postfix/master -w
    6926		postfix		 qmgr -l -t unix -u
    7040		root		 /usr/sbin/crond -n
    7084		ntp		 /usr/sbin/ntpd -u ntp:ntp -g
    12889		root		 sshd: root@pts/0
    12891		root		 -bash
    13397		root		 sshd: root@pts/2
    13399		root		 -bash
    21577		root		 /sbin/agetty --noclear tty1 linux
    44996		postfix		 pickup -l -t unix -u
    45208		root		 sshd: root@notty
    45211		root		 /usr/libexec/openssh/sftp-server
    45231		root		 /usr/libexec/openssh/sftp-server
    46843		root		 ping 127.0.0.1
    46844		root		 ping 127.0.0.1
    46845		root		 ping 127.0.0.1
    46846		root		 ping 127.0.0.1
    46847		root		 ping 127.0.0.1
    46848		root		 ping 127.0.0.1
    46849		root		 ping 127.0.0.1
    46850		root		 ping 127.0.0.1
    46851		root		 ping 127.0.0.1
    46852		root		 ping 127.0.0.1
    46856		root		 ping 127.0.0.1
    46857		root		 ping 127.0.0.1
    46858		root		 ping 127.0.0.1
    46859		root		 ping 127.0.0.1
    46860		root		 ping 127.0.0.1
    46861		root		 ping 127.0.0.1
    46862		root		 ping 127.0.0.1
    46863		root		 ping 127.0.0.1
    46864		root		 ping 127.0.0.1
    46865		root		 ping 127.0.0.1
    46868		root		 ping 127.0.0.1
    46869		root		 ping 127.0.0.1
    46870		root		 ping 127.0.0.1
    46871		root		 ping 127.0.0.1
    46872		root		 ping 127.0.0.1
    46873		root		 ping 127.0.0.1
    46874		root		 ping 127.0.0.1
    46875		root		 ping 127.0.0.1
    46876		root		 ping 127.0.0.1
    46877		root		 ping 127.0.0.1
    46880		root		 ping 127.0.0.1
    46881		root		 ping 127.0.0.1
    46882		root		 ping 127.0.0.1
    46883		root		 ping 127.0.0.1
    46884		root		 ping 127.0.0.1
    46885		root		 ping 127.0.0.1
    46886		root		 ping 127.0.0.1
    46887		root		 ping 127.0.0.1
    46888		root		 ping 127.0.0.1
    46889		root		 ping 127.0.0.1
    94040		root		 sh start.sh
    94088		root		 sh start.sh
    94089		root		 /root/IncidentResponse/busybox ps
    94090		root		 sh start.sh
    94091		root		 sh start.sh
    94092		root		 sh start.sh
    94093		root		 sh start.sh
    
    -------------------------------------------------    -------------------------------------------------      [1.3-3 System process(/proc/$pid/exe)]
    lrwxrwxrwx    1 root     root             0 Apr 20 19:39 /proc/94040/exe -> /usr/bin/bash
    lrwxrwxrwx    1 root     root             0 Apr 20 19:39 /proc/94099/exe -> /usr/bin/bash
    lrwxrwxrwx    1 root     root             0 Apr 20 19:39 /proc/94100/exe -> /root/IncidentResponse/busybox
    lrwxrwxrwx    1 root     root             0 Apr 20 19:39 /proc/94101/exe -> /usr/bin/bash
    lrwxrwxrwx    1 root     root             0 Apr 20 19:39 /proc/94102/exe -> /usr/bin/bash
    lrwxrwxrwx    1 root     root             0 Apr 20 19:39 /proc/94103/exe -> /usr/bin/bash
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/1/exe -> /usr/lib/systemd/systemd
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/2950/exe -> /usr/lib/systemd/systemd-journald
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/2975/exe -> /usr/lib/systemd/systemd-udevd
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/4890/exe -> /usr/lib/polkit-1/polkitd
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/5198/exe -> /usr/bin/VGAuthService
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/5199/exe -> /usr/bin/vmtoolsd
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/5200/exe -> /usr/lib/systemd/systemd-logind
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/5201/exe -> /usr/bin/dbus-daemon
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/6356/exe -> /usr/sbin/NetworkManager
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/6811/exe -> /usr/sbin/sshd
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/6812/exe -> /usr/bin/python2.7
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/6819/exe -> /usr/sbin/rsyslogd
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/6920/exe -> /usr/libexec/postfix/master
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/6926/exe -> /usr/libexec/postfix/qmgr
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/7040/exe -> /usr/sbin/crond
    lrwxrwxrwx    1 root     root             0 Apr 20 19:19 /proc/7084/exe -> /usr/sbin/ntpd
    lrwxrwxrwx    1 root     root             0 Apr 20 19:14 /proc/45211/exe -> /usr/libexec/openssh/sftp-server
    lrwxrwxrwx    1 root     root             0 Apr 20 19:14 /proc/45231/exe -> /usr/libexec/openssh/sftp-server
    lrwxrwxrwx    1 root     root             0 Apr 20 19:01 /proc/44996/exe -> /usr/libexec/postfix/pickup
    lrwxrwxrwx    1 root     root             0 Apr 20 18:17 /proc/45208/exe -> /usr/sbin/sshd
    lrwxrwxrwx    1 root     root             0 Apr 20 13:29 /proc/12891/exe -> /usr/bin/bash
    lrwxrwxrwx    1 root     root             0 Apr 20 13:29 /proc/13399/exe -> /usr/bin/bash
    lrwxrwxrwx    1 root     root             0 Apr 20 13:29 /proc/21577/exe -> /usr/sbin/agetty
    lrwxrwxrwx    1 root     root             0 Apr 20 10:38 /proc/13397/exe -> /usr/sbin/sshd
    lrwxrwxrwx    1 root     root             0 Apr 20 10:28 /proc/12889/exe -> /usr/sbin/sshd
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46843/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46844/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46845/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46846/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46847/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46848/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46849/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46850/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46851/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46852/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46856/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46857/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46858/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46859/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46860/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46861/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46862/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46863/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46864/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46865/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46868/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46869/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46870/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46871/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46872/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46873/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46874/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46875/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46876/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46877/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46880/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46881/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46882/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46883/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46884/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46885/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46886/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46887/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46888/exe -> /usr/bin/ping (deleted)
    lrwxrwxrwx    1 root     root             0 Apr 19 15:18 /proc/46889/exe -> /usr/bin/ping (deleted)
    
    -------------------------------------------------    -------------------------------------------------    [2 Persistence inspection]
      [2.1 Task plan check results]
        [2.1.1 /etc/crontab]
    01 * * * * root run-parts /tmp/ping1.sh
    01 * * * * root run-parts /tmp/ping2.sh
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/tmp/ping1.sh]
    ping2=`cat /tmp/ping2.txt`
        nohup ping $ping2 &
                                          [not exist] [/tmp/ping2.sh]
    
    -------------------------------------------------    -------------------------------------------------        [2.1.2 /var/spool/cron/*]
    /var/spool/cron/test
    /var/spool/cron/gmlii
    
    -------------------------------------------------    -------------------------------------------------          [/var/spool/cron/gmlii]
    01 * * * * root run-parts /tmp/ping1.sh
    01 * * * * root run-parts /tmp/ping2.sh
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/tmp/ping1.sh]
    ping2=`cat /tmp/ping2.txt`
        nohup ping $ping2 &
                                          [not exist] [/tmp/ping2.sh]
    
    -------------------------------------------------    -------------------------------------------------          [/var/spool/cron/test]
    01 * * * * root run-parts /tmp/ping3.sh
    01 * * * * root run-parts /tmp/ping4.sh
                                          [not exist] [/tmp/ping3.sh]
                                          [not exist] [/tmp/ping4.sh]
    
    -------------------------------------------------    -------------------------------------------------        [2.1.3 /etc/cron.d/*]
    /etc/cron.d/0hourly
    
    -------------------------------------------------    -------------------------------------------------          [/etc/cron.d/0hourly]
    01 * * * * root run-parts /etc/cron.hourly
    
    -------------------------------------------------    -------------------------------------------------                                          [directory] [/etc/cron.hourly]
    /etc/cron.hourly/0anacron
    /etc/cron.hourly/test
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/etc/cron.hourly/0anacron]
        day=`cat /var/spool/anacron/cron.daily`
        /usr/bin/on_ac_power >/dev/null 2>&1
    /usr/sbin/anacron -s
    
    -------------------------------------------------    -------------------------------------------------                                         [ascii text] [/etc/cron.hourly/test]
    /test
    
    -------------------------------------------------    -------------------------------------------------        [2.1.4 /etc/anacrontab]
    1	5	cron.daily		nice run-parts /etc/cron.daily
    7	25	cron.weekly		nice run-parts /etc/cron.weekly
    @monthly 45	cron.monthly		nice run-parts /etc/cron.monthly
    
    -------------------------------------------------    -------------------------------------------------                                          [directory] [/etc/cron.daily]
    /etc/cron.daily/logrotate
    /etc/cron.daily/man-db.cron
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/etc/cron.daily/logrotate]
    /usr/sbin/logrotate -s /var/lib/logrotate/logrotate.status /etc/logrotate.conf
        /usr/bin/logger -t logrotate "ALERT exited abnormally with [$EXITVALUE]"
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/etc/cron.daily/man-db.cron]
        . /etc/sysconfig/man-db
    
    -------------------------------------------------    -------------------------------------------------                                          [directory] [/etc/cron.monthly]
    
    -------------------------------------------------    -------------------------------------------------                                          [directory] [/etc/cron.weekly]
    
    -------------------------------------------------    -------------------------------------------------      [2.2 Environmental variable check]
        [2.2.1 /etc/profile]
        pathmunge /usr/sbin
        pathmunge /usr/local/sbin
        pathmunge /usr/local/sbin after
        pathmunge /usr/sbin after
                . "$i"
                . "$i" >/dev/null
    
    -------------------------------------------------    -------------------------------------------------          [/etc/ld.so.preload]
                                                     Not exist
    
    -------------------------------------------------    -------------------------------------------------        [2.2.2-1 /etc/bashrc]
          [ -e /etc/sysconfig/bash-prompt-default ] && PROMPT_COMMAND=/etc/sysconfig/bash-prompt-default
                    . "$i"
                    . "$i" >/dev/null
    
    -------------------------------------------------    -------------------------------------------------        [2.2.2-2 /etc/bash.bashrc]
                                                     not exist
    
    -------------------------------------------------    -------------------------------------------------        [2.2.3 ~/.profile]
          [/root/.profile]
                                                     not exist
    
    -------------------------------------------------    -------------------------------------------------          [/home/test/.profile]
                                                     not exist
    
    -------------------------------------------------    -------------------------------------------------          [/home/gmlii/.profile]
                                                     not exist
    
    -------------------------------------------------    -------------------------------------------------        [2.2.4 ~/.bash_profile]
          [/root/.bash_profile]
    	. ~/.bashrc
    
    -------------------------------------------------    -------------------------------------------------          [/home/test/.bash_profile]
    	. ~/.bashrc
    
    -------------------------------------------------    -------------------------------------------------          [/home/gmlii/.bash_profile]
    	. ~/.bashrc
    
    -------------------------------------------------    -------------------------------------------------        [2.2.5 ~/.bashrc]
          [/root/.bashrc]
    alias cp='cp -i'
    alias mv='mv -i'
    	. /etc/bashrc
    alias rm=recyclebin
    alias r=recyclebin
    alias rl='ls -alt --color=auto /opt/RecycleBin'
        mkdir /opt/RecycleBin
        mv $@ /opt/RecycleBin/$@_$system_date
    
    -------------------------------------------------    -------------------------------------------------          [/home/test/.bashrc]
    	. /etc/bashrc
    
    -------------------------------------------------    -------------------------------------------------          [/home/gmlii/.bashrc]
    	. /etc/bashrc
    
    -------------------------------------------------    -------------------------------------------------        [2.2.6 ~/.bash_login]
          [/root/.bash_login]
                                                     not exist
    
    -------------------------------------------------    -------------------------------------------------          [/home/test/.bash_login]
                                                     not exist
    
    -------------------------------------------------    -------------------------------------------------          [/home/gmlii/.bash_login]
                                                     not exist
    
    -------------------------------------------------    -------------------------------------------------        [2.2.7 ~/.bash_logout]
          [/root/.bash_logout]
    
    -------------------------------------------------    -------------------------------------------------          [/home/test/.bash_logout]
    
    -------------------------------------------------    -------------------------------------------------          [/home/gmlii/.bash_logout]
    
    -------------------------------------------------    -------------------------------------------------      [2.3 System service check]
        [2.3.1 Init]
                   [Runlevel]: 3
          [chkconfig cmdline]: /usr/sbin/chkconfig
    
    -------------------------------------------------    -------------------------------------------------          [Started services]
    network        	0:关	1:关	2:开	3:开	4:开	5:开	6:关
    
    -------------------------------------------------    -------------------------------------------------            [/etc/rc.d/init.d/network]
    . /etc/init.d/functions
    . /etc/sysconfig/network
        . /etc/sysconfig/pcmcia
    [ -x /sbin/ip ] || exit 1
    cd /etc/sysconfig/network-scripts
    . ./network-functions
            LC_ALL=C sed 's/ //')
            /etc/sysconfig/network-scripts/init.ipv6-global start pre
                grep "^any" /etc/sysconfig/static-routes | while read ignore args ; do
                    /sbin/route add -$args
                net_log $"Legacy static-route support not available: /sbin/route not found"
            /etc/sysconfig/network-scripts/init.ipv6-global start post
        touch /var/lock/subsys/network
        [ -n "${NETWORKDELAY}" ] && /bin/sleep ${NETWORKDELAY}
            net_log $"rootfs or /usr is on network filesystem, leaving network up"
            /etc/sysconfig/network-scripts/init.ipv6-global stop post
        rm -f /var/lock/subsys/network
    
    -------------------------------------------------    -------------------------------------------------                                         [ascii text] [/etc/init.d/functions]
            [ -d /run/systemd/system ] ; then
        /etc/init.d/*|/etc/rc.d/init.d/*)
            action $"Reloading systemd: " /bin/systemctl daemon-reload
        action "$s" /bin/systemctl $options $command "$prog.service"
            CONSOLETYPE="$(/sbin/consoletype < /dev/stderr 2>/dev/null)"
            [ -f /etc/sysconfig/i18n -o -f /etc/locale.conf ] ; then
        . /etc/profile.d/lang.sh 2>/dev/null
            . /etc/sysconfig/init
            read -r line < "/proc/$pid/stat" 2> /dev/null
        stat=($(< /proc/self/stat))
        local pid_dir=$(/usr/bin/dirname $pid_file > /dev/null)
                            local b=$(readlink /proc/$p/exe | sed -e 's/\s*(deleted)$//')
           $cgroup $nice /bin/bash -c "$corelimit >/dev/null 2>&1 ; $*"
           $cgroup $nice runuser -s /bin/bash $user -c "$corelimit >/dev/null 2>&1 ; $*"
            /bin/plymouth --update="$1"
        [ -x /bin/plymouth ] && /bin/plymouth --details
        deci)   retval=$(awk "BEGIN {printf \"%.1f\", ${1} / 10}") ;;
        centi)  retval=$(awk "BEGIN {printf \"%.2f\", ${1} / 100}") ;;
        mili)   retval=$(awk "BEGIN {printf \"%.3f\", ${1} / 1000}") ;;
        micro)  retval=$(awk "BEGIN {printf \"%.6f\", ${1} / 1000000}") ;;
        nano)   retval=$(awk "BEGIN {printf \"%.9f\", ${1} / 1000000000}") ;;
        piko)   retval=$(awk "BEGIN {printf \"%.12f\", ${1} / 1000000000000}") ;;
        /lib/systemd/systemd-sysctl
            sysctl -e -p /etc/sysctl.conf >/dev/null 2>&1
    strstr "$(cat /proc/cmdline)" "rc.debug" && set -x
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/etc/sysconfig/network-scripts/init.ipv6-global]
    . /etc/sysconfig/network
    cd /etc/sysconfig/network-scripts
    . ./network-functions
    [ -f /etc/sysconfig/network-scripts/network-functions-ipv6 ] || exit 1
    . /etc/sysconfig/network-scripts/network-functions-ipv6
                    /sbin/sysctl -e -w net.ipv6.conf.$sinterface.accept_ra=$ipv6_global_auto >/dev/null 2>&1
                    /sbin/sysctl -e -w net.ipv6.conf.$sinterface.accept_redirects=$ipv6_global_auto >/dev/null 2>&1
            /sbin/ip route add unreach    ::ffff:0.0.0.0/96
            /sbin/ip route add unreach    ::0.0.0.0/96
            /sbin/ip route add unreach    2002:e000::/19
            /sbin/ip route add unreach    2002:7f00::/24
            /sbin/ip route add unreach    2002:0a00::/24
            /sbin/ip route add unreach    2002:ac10::/28
            /sbin/ip route add unreach    2002:c0a8::/32
            /sbin/ip route add unreach    2002:a9fe::/32
            /sbin/ip route add unreach    3ffe:ffff::/32
                    /sbin/sysctl -e -w net.ipv6.conf.$sinterface.accept_ra=0 >/dev/null 2>&1
                    /sbin/sysctl -e -w net.ipv6.conf.$sinterface.accept_redirects=0 >/dev/null 2>&1
                /sbin/ip link set sit0 down
    
    -------------------------------------------------    -------------------------------------------------          [/etc/rc.d/rc.local]
    touch /var/lock/subsys/local
    /usr/local/phpstudy/system/phpstudyctl -start
        [Bourne-Again shell script]: /etc/rc.d/rc.local
        [Bourne-Again shell script]: /etc/rc.d/rc.local
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/local/phpstudy/system/phpstudyctl]
    	u14_04=`cat /etc/issue`
    		/bin/cgroups-mount
    	pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/docker-18.09.6/dockerd`
    		dockerd > /dev/null 2>&1 &
    		pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/docker-18.09.6/dockerd`
    	docker exec centos_env ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
        pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/system/phpstudy`
    		chmod +x /usr/local/phpstudy/system/phpstudy
    		/usr/local/phpstudy/system/phpstudy -d > /dev/null 2>&1 &
    	find /usr/local/phpstudy/soft/* -name status > /usr/local/phpstudy/soft/auto
    	cat /usr/local/phpstudy/soft/auto | while read line
    	rm -rf /usr/local/phpstudy/soft/auto
    	pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/system/module/xpupdate`
    		pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/system/module/xpupdate`
    	pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/web/php-7.3.8/bin/php`
    		docker exec centos_env $SHELL /usr/local/phpstudy/web/start > /dev/null 2>&1 &
    		pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/web/php-7.3.8/bin/php`
    		pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/docker-18.09.6/dockerd`
    	docker exec centos_env $SHELL /usr/local/phpstudy/web/stop > /dev/null 2>&1
    	pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/system/phpstudy`
    	pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/docker-18.09.6/dockerd`
    	pid=`/usr/local/phpstudy/system/module/getPidByExe /usr/local/phpstudy/web/php-7.3.8/bin/php`
    	/usr/local/phpstudy/system/phpstudy -v
    	/usr/local/phpstudy/system/phpstudy -visiturl
    		/usr/local/phpstudy/system/phpstudy -initpwd $2
    	cat /usr/local/phpstudy/install.result
    	/usr/local/phpstudy/system/phpstudy -setport $1
            /usr/local/phpstudy/system/phpstudy -retoken
    		        /bin/bash $updateFile
    	/usr/local/phpstudy/system/phpstudy -v
            /usr/local/phpstudy/system/phpstudy -canceldomain
            /usr/local/phpstudy/system/phpstudy -cancelip
    	docker exec -it  centos_env /bin/bash
    	ls -F /usr/local/phpstudy/soft/php | grep '/$' > /usr/local/phpstudy/tmp/allphp
    		line=`sed -n "$i"p /usr/local/phpstudy/tmp/allphp`
    	selPhp=`sed -n "$nSel"p /usr/local/phpstudy/tmp/allphp`
    	/usr/local/phpstudy/system/phpstudy -switchphpver $selPhp
    		/usr/local/phpstudy/system/module/xpfirewall stop
    		rm -rf /usr/local/phpstudy
    		rm -rf /usr/bin/containerd
    		rm -rf /usr/bin/containerd-shim
    		rm -rf /usr/bin/ctr
    		rm -rf /usr/bin/docker
    		rm -rf /usr/bin/dockerd
    		rm -rf /usr/bin/docker-init
    		rm -rf /usr/bin/docker-proxy
    		rm -rf /usr/bin/runc
    		rm -rf /usr/bin/xp
    		rm -rf /usr/bin/XP
    		rm -rf /usr/bin/php
    		rm -rf /usr/bin/phpstudy
    				/usr/local/phpstudy/system/phpstudy -initpwd $pwd1
                                              [empty] [/var/lock/subsys/local]
    
    -------------------------------------------------    -------------------------------------------------        [2.3.2 Systemd]
          [systemctl cmdline]: /usr/bin/systemctl
          [Started services]
    auditd.service                                enabled 
    autovt@.service                               enabled 
    brandbot.service                              static  
    container-getty@.service                      static  
    crond.service                                 enabled 
    dbus-org.fedoraproject.FirewallD1.service     enabled 
    dbus-org.freedesktop.hostname1.service        static  
    dbus-org.freedesktop.import1.service          static  
    dbus-org.freedesktop.locale1.service          static  
    dbus-org.freedesktop.login1.service           static  
    dbus-org.freedesktop.machine1.service         static  
    dbus-org.freedesktop.NetworkManager.service   enabled 
    dbus-org.freedesktop.nm-dispatcher.service    enabled 
    dbus-org.freedesktop.timedate1.service        static  
    dbus.service                                  static  
    dracut-cmdline.service                        static  
    dracut-initqueue.service                      static  
    dracut-mount.service                          static  
    dracut-pre-mount.service                      static  
    dracut-pre-pivot.service                      static  
    dracut-pre-trigger.service                    static  
    dracut-pre-udev.service                       static  
    dracut-shutdown.service                       static  
    emergency.service                             static  
    firewalld.service                             enabled 
    fstrim.service                                static  
    getty@.service                                enabled 
    halt-local.service                            static  
    initrd-cleanup.service                        static  
    initrd-parse-etc.service                      static  
    initrd-switch-root.service                    static  
    initrd-udevadm-cleanup-db.service             static  
    irqbalance.service                            enabled 
    kdump.service                                 enabled 
    kmod-static-nodes.service                     static  
    messagebus.service                            static  
    microcode.service                             enabled 
    NetworkManager-dispatcher.service             enabled 
    NetworkManager-wait-online.service            enabled 
    NetworkManager.service                        enabled 
    ntpd.service                                  enabled 
    ntpdate.service                               enabled 
    plymouth-switch-root.service                  static  
    polkit.service                                static  
    postfix.service                               enabled 
    quotaon.service                               static  
    rc-local.service                              static  
    rescue.service                                static  
    rhel-autorelabel.service                      enabled 
    rhel-configure.service                        enabled 
    rhel-dmesg.service                            enabled 
    rhel-domainname.service                       enabled 
    rhel-import-state.service                     enabled 
    rhel-loadmodules.service                      enabled 
    rhel-readonly.service                         enabled 
    rsyslog.service                               enabled 
    selinux-policy-migrate-local-changes@.service static  
    sshd-keygen.service                           static  
    sshd.service                                  enabled 
    sshd@.service                                 static  
    systemd-ask-password-console.service          static  
    systemd-ask-password-plymouth.service         static  
    systemd-ask-password-wall.service             static  
    systemd-backlight@.service                    static  
    systemd-binfmt.service                        static  
    systemd-firstboot.service                     static  
    systemd-fsck-root.service                     static  
    systemd-fsck@.service                         static  
    systemd-halt.service                          static  
    systemd-hibernate-resume@.service             static  
    systemd-hibernate.service                     static  
    systemd-hostnamed.service                     static  
    systemd-hwdb-update.service                   static  
    systemd-hybrid-sleep.service                  static  
    systemd-importd.service                       static  
    systemd-initctl.service                       static  
    systemd-journal-catalog-update.service        static  
    systemd-journal-flush.service                 static  
    systemd-journald.service                      static  
    systemd-kexec.service                         static  
    systemd-localed.service                       static  
    systemd-logind.service                        static  
    systemd-machine-id-commit.service             static  
    systemd-machined.service                      static  
    systemd-modules-load.service                  static  
    systemd-poweroff.service                      static  
    systemd-quotacheck.service                    static  
    systemd-random-seed.service                   static  
    systemd-readahead-collect.service             enabled 
    systemd-readahead-drop.service                enabled 
    systemd-readahead-replay.service              enabled 
    systemd-reboot.service                        static  
    systemd-remount-fs.service                    static  
    systemd-rfkill@.service                       static  
    systemd-shutdownd.service                     static  
    systemd-suspend.service                       static  
    systemd-sysctl.service                        static  
    systemd-timedated.service                     static  
    systemd-tmpfiles-clean.service                static  
    systemd-tmpfiles-setup-dev.service            static  
    systemd-tmpfiles-setup.service                static  
    systemd-udev-settle.service                   static  
    systemd-udev-trigger.service                  static  
    systemd-udevd.service                         static  
    systemd-update-done.service                   static  
    systemd-update-utmp-runlevel.service          static  
    systemd-update-utmp.service                   static  
    systemd-user-sessions.service                 static  
    systemd-vconsole-setup.service                static  
    teamd@.service                                static  
    tuned.service                                 enabled 
    vgauthd.service                               enabled 
    vmtoolsd.service                              enabled 
    
    -------------------------------------------------    -------------------------------------------------            [auditd.service]
              [/usr/lib/systemd/system/auditd.service]
    /sbin/auditd && /tmp/ping1.sh
    /sbin/augenrules --load
    /sbin/auditctl -R /etc/audit/audit.rules
    /sbin/auditctl -R /etc/audit/audit-stop.rules
                                                [elf] [/sbin/auditctl]
                                                [elf] [/sbin/auditd]
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/sbin/augenrules]
    TmpRules=`mktemp /tmp/aurules.XXXXXXXX`
    		/sbin/auditctl -R ${DestinationFile}
    cmp -s ${TmpRules} ${DestinationFile} > /dev/null 2>&1
    	/usr/sbin/restorecon -F ${DestinationFile}
        [Bourne-Again shell script]: /sbin/augenrules
    
    -------------------------------------------------    -------------------------------------------------            [autovt@.service]
              [/usr/lib/systemd/system/autovt@.service]
    /sbin/agetty --noclear %I $TERM
                                                [elf] [/sbin/agetty]
    
    -------------------------------------------------    -------------------------------------------------            [brandbot.service]
              [/usr/lib/systemd/system/brandbot.service]
    /usr/libexec/initscripts/brandbot
                                                [elf] [/usr/libexec/initscripts/brandbot]
    
    -------------------------------------------------    -------------------------------------------------            [container-getty@.service]
              [/usr/lib/systemd/system/container-getty@.service]
    /sbin/agetty --noclear --keep-baud pts/%I 115200,38400,9600 $TERM
                                                [elf] [/sbin/agetty]
    
    -------------------------------------------------    -------------------------------------------------            [crond.service]
              [/usr/lib/systemd/system/crond.service]
    /usr/sbin/crond -n $CRONDARGS
    /bin/kill -HUP $MAINPID
                                                [elf] [/bin/kill]
                                                [elf] [/usr/sbin/crond]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.fedoraproject.FirewallD1.service]
              [/usr/lib/systemd/system/firewalld.service]
    /usr/sbin/firewalld --nofork --nopid $FIREWALLD_ARGS
    /bin/kill -HUP $MAINPID
                                                [elf] [/bin/kill]
    
    -------------------------------------------------    -------------------------------------------------                                             [python] [/usr/sbin/firewalld]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.freedesktop.hostname1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.hostname1.service]
    /usr/lib/systemd/systemd-hostnamed
                                                [elf] [/usr/lib/systemd/systemd-hostnamed]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.freedesktop.import1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.import1.service]
    /usr/lib/systemd/systemd-importd
                                                [elf] [/usr/lib/systemd/systemd-importd]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.freedesktop.locale1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.locale1.service]
    /usr/lib/systemd/systemd-localed
                                                [elf] [/usr/lib/systemd/systemd-localed]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.freedesktop.login1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.login1.service]
    /usr/lib/systemd/systemd-logind
                                                [elf] [/usr/lib/systemd/systemd-logind]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.freedesktop.machine1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.machine1.service]
    /usr/lib/systemd/systemd-machined
                                                [elf] [/usr/lib/systemd/systemd-machined]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.freedesktop.NetworkManager.service]
              [/usr/lib/systemd/system/NetworkManager.service]
    /usr/bin/dbus-send --print-reply --system --type
    /bin/kill -HUP $MAINPID
    /usr/sbin/NetworkManager --no-daemon
                                                [elf] [/bin/kill]
                                                [elf] [/usr/bin/dbus-send]
                                                [elf] [/usr/sbin/NetworkManager]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.freedesktop.nm-dispatcher.service]
              [/usr/lib/systemd/system/NetworkManager-dispatcher.service]
    /usr/libexec/nm-dispatcher
                                                [elf] [/usr/libexec/nm-dispatcher]
    
    -------------------------------------------------    -------------------------------------------------            [dbus-org.freedesktop.timedate1.service]
              [/usr/lib/systemd/system/dbus-org.freedesktop.timedate1.service]
    /usr/lib/systemd/systemd-timedated
                                                [elf] [/usr/lib/systemd/systemd-timedated]
    
    -------------------------------------------------    -------------------------------------------------            [dbus.service]
              [/usr/lib/systemd/system/dbus.service]
    /usr/bin/dbus-daemon --system --address
    /usr/bin/dbus-send --print-reply --system --type
                                                [elf] [/usr/bin/dbus-daemon]
                                                [elf] [/usr/bin/dbus-send]
    
    -------------------------------------------------    -------------------------------------------------            [dracut-cmdline.service]
              [/usr/lib/systemd/system/dracut-cmdline.service]
    /bin/dracut-cmdline
                                          [not exist] [/bin/dracut-cmdline]
    
    -------------------------------------------------    -------------------------------------------------            [dracut-initqueue.service]
              [/usr/lib/systemd/system/dracut-initqueue.service]
    /bin/dracut-initqueue
                                          [not exist] [/bin/dracut-initqueue]
    
    -------------------------------------------------    -------------------------------------------------            [dracut-mount.service]
              [/usr/lib/systemd/system/dracut-mount.service]
    /bin/dracut-mount
                                          [not exist] [/bin/dracut-mount]
    
    -------------------------------------------------    -------------------------------------------------            [dracut-pre-mount.service]
              [/usr/lib/systemd/system/dracut-pre-mount.service]
    /bin/dracut-pre-mount
                                          [not exist] [/bin/dracut-pre-mount]
    
    -------------------------------------------------    -------------------------------------------------            [dracut-pre-pivot.service]
              [/usr/lib/systemd/system/dracut-pre-pivot.service]
    /bin/dracut-pre-pivot
                                          [not exist] [/bin/dracut-pre-pivot]
    
    -------------------------------------------------    -------------------------------------------------            [dracut-pre-trigger.service]
              [/usr/lib/systemd/system/dracut-pre-trigger.service]
    /bin/dracut-pre-trigger
                                          [not exist] [/bin/dracut-pre-trigger]
    
    -------------------------------------------------    -------------------------------------------------            [dracut-pre-udev.service]
              [/usr/lib/systemd/system/dracut-pre-udev.service]
    /bin/dracut-pre-udev
                                          [not exist] [/bin/dracut-pre-udev]
    
    -------------------------------------------------    -------------------------------------------------            [dracut-shutdown.service]
              [/usr/lib/systemd/system/dracut-shutdown.service]
    /usr/lib/dracut/dracut-initramfs-restore
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/lib/dracut/dracut-initramfs-restore]
    [[ -f /etc/machine-id ]] && read MACHINE_ID < /etc/machine-id
    cd /run/initramfs
        echo "Unpacking of $IMG to /run/initramfs failed" >&2
        rm -f -- /run/initramfs/shutdown
        [Bourne-Again shell script]: /usr/lib/dracut/dracut-initramfs-restore
    
    -------------------------------------------------    -------------------------------------------------            [emergency.service]
              [/usr/lib/systemd/system/emergency.service]
    /bin/plymouth quit
    /bin/echo -e 'Welcome to emergency mode! After logging in, type "journalctl -xb" to view\\nsystem logs, "systemctl reboot" to reboot, "systemctl default" or ^D to\\ntry again to boot into default mode.'
    /bin/sh -c "/usr/sbin/sulogin; /usr/bin/systemctl --fail --no-block default"
                                                [elf] [/bin/echo]
                                                [elf] [/bin/plymouth]
                                      [symbolic link] [/bin/sh]
    
    -------------------------------------------------    -------------------------------------------------            [firewalld.service]
              [/usr/lib/systemd/system/firewalld.service]
    /usr/sbin/firewalld --nofork --nopid $FIREWALLD_ARGS
    /bin/kill -HUP $MAINPID
                                                [elf] [/bin/kill]
    
    -------------------------------------------------    -------------------------------------------------                                             [python] [/usr/sbin/firewalld]
    
    -------------------------------------------------    -------------------------------------------------            [fstrim.service]
              [/usr/lib/systemd/system/fstrim.service]
    /usr/sbin/fstrim -a
                                                [elf] [/usr/sbin/fstrim]
    
    -------------------------------------------------    -------------------------------------------------            [getty@.service]
              [/usr/lib/systemd/system/getty@.service]
    /sbin/agetty --noclear %I $TERM
                                                [elf] [/sbin/agetty]
    
    -------------------------------------------------    -------------------------------------------------            [halt-local.service]
              [/usr/lib/systemd/system/halt-local.service]
    /usr/sbin/halt.local
    /usr/sbin/halt.local
                                          [not exist] [/usr/sbin/halt.local]
    
    -------------------------------------------------    -------------------------------------------------            [initrd-cleanup.service]
              [/usr/lib/systemd/system/initrd-cleanup.service]
    /usr/bin/systemctl --no-block isolate initrd-switch-root.target
                                                [elf] [/usr/bin/systemctl]
    
    -------------------------------------------------    -------------------------------------------------            [initrd-parse-etc.service]
              [/usr/lib/systemd/system/initrd-parse-etc.service]
    /usr/bin/systemctl daemon-reload
    /usr/bin/systemctl --no-block start initrd-fs.target
    /usr/bin/systemctl --no-block start initrd-cleanup.service
                                                [elf] [/usr/bin/systemctl]
    
    -------------------------------------------------    -------------------------------------------------            [initrd-switch-root.service]
              [/usr/lib/systemd/system/initrd-switch-root.service]
    /usr/bin/systemctl --no-block --force switch-root /sysroot
                                                [elf] [/usr/bin/systemctl]
    
    -------------------------------------------------    -------------------------------------------------            [initrd-udevadm-cleanup-db.service]
              [/usr/lib/systemd/system/initrd-udevadm-cleanup-db.service]
    /usr/bin/udevadm info --cleanup-db
                                                [elf] [/usr/bin/udevadm]
    
    -------------------------------------------------    -------------------------------------------------            [irqbalance.service]
              [/usr/lib/systemd/system/irqbalance.service]
    /usr/sbin/irqbalance --foreground $IRQBALANCE_ARGS
                                                [elf] [/usr/sbin/irqbalance]
    
    -------------------------------------------------    -------------------------------------------------            [kdump.service]
              [/usr/lib/systemd/system/kdump.service]
    /usr/bin/kdumpctl start
    /usr/bin/kdumpctl stop
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/bin/kdumpctl]
    . /lib/kdump/kdump-lib.sh
    	. /etc/sysconfig/kdump
    			     -e "s/\s\+/ /g"`
    	CPU=="0" && /^apicid/		{ print $NF; }		\
    	/proc/cpuinfo
    		cmdline=$(cat /proc/cmdline)
    	cp --sparse=always /proc/vmcore $coredir/vmcore-incomplete
    	touch /tmp/fadump.initramfs
    		-i /tmp/fadump.initramfs /etc/fadump.initramfs
    		rm -f /tmp/fadump.initramfs
    	rm -f /tmp/fadump.initramfs
    	nr=$(awk 'BEGIN{cnt=0} /^raw|^ssh[[:blank:]]|^nfs|^ext[234]|^xfs|^btrfs|^minix|^dracut_args .*\-\-mount/{cnt++} END{print cnt}' $KDUMP_CONFIG_FILE)
    		eval $(cat /proc/cmdline| grep "BOOT_IMAGE" | cut -d' ' -f1)
    	[[ -e /etc/fstab ]] && files="$files /etc/fstab"
    	echo $_dracut_args | grep "\-\-mount" &> /dev/null
    	[[ -d /sys/class/watchdog/ ]] || return 0
    	[[ $_alldrivers ]] && wd_new="rd.driver.pre=${_alldrivers// /,}"
    	local _old_modules="$(lsinitrd $TARGET_INITRD -f /usr/lib/dracut/loaded-kernel-modules.txt | sort)"
    	return `tail -n 1 /proc/iomem | awk '{ split ($1, r, "-"); \
    		/usr/bin/ssh-keygen -t rsa -f $KEYFILE -N "" 2>&1 > /dev/null
        local mem=$(cat /sys/kernel/kexec_crash_size)
        local mem_mb=$(expr $mem / 1024 / 1024)
    	rc=`cat /sys/kernel/kexec_crash_loaded`
    	raw_target=$(awk '$1 ~ /^raw$/ { print $2; }' $KDUMP_CONFIG_FILE)
    	_target=$(egrep "^ext[234]|^xfs|^btrfs|^minix|^raw|^ssh|^nfs" /etc/kdump.conf)
    	_target=$(egrep "^ext[234]|^xfs|^btrfs|^minix" /etc/kdump.conf)
    	secure_boot_file=$(find /sys/firmware/efi/efivars -name SecureBoot-* 2>/dev/null)
    	setup_mode_file=$(find /sys/firmware/efi/efivars -name SetupMode-* 2>/dev/null)
    	secure_mode_byte=$(cat /sys/kernel/security/securelevel)
    	mem_reserved=$(cat /sys/kernel/kexec_crash_size)
    		echo $ipaddrs | grep $node > /dev/null
    	default_option=$(awk '$1 ~ /^default$/ {print $2;}' $KDUMP_CONFIG_FILE)
        [Bourne-Again shell script]: /usr/bin/kdumpctl
        [Bourne-Again shell script]: /usr/bin/kdumpctl
    
    -------------------------------------------------    -------------------------------------------------            [kmod-static-nodes.service]
              [/usr/lib/systemd/system/kmod-static-nodes.service]
    /usr/bin/kmod static-nodes --format
                                                [elf] [/usr/bin/kmod]
    
    -------------------------------------------------    -------------------------------------------------            [messagebus.service]
              [/usr/lib/systemd/system/messagebus.service]
    /usr/bin/dbus-daemon --system --address
    /usr/bin/dbus-send --print-reply --system --type
                                                [elf] [/usr/bin/dbus-daemon]
                                                [elf] [/usr/bin/dbus-send]
    
    -------------------------------------------------    -------------------------------------------------            [microcode.service]
              [/usr/lib/systemd/system/microcode.service]
    /usr/libexec/microcode_ctl/reload_microcode
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/libexec/microcode_ctl/reload_microcode]
    "$CHECK_CAVEATS" -m > /dev/null || trigger=0
    [ 0 -eq "$trigger" ] || echo 2>/dev/null 1 > /sys/devices/system/cpu/microcode/reload || true
        [Bourne-Again shell script]: /usr/libexec/microcode_ctl/reload_microcode
    
    -------------------------------------------------    -------------------------------------------------            [NetworkManager-dispatcher.service]
              [/usr/lib/systemd/system/NetworkManager-dispatcher.service]
    /usr/libexec/nm-dispatcher
                                                [elf] [/usr/libexec/nm-dispatcher]
    
    -------------------------------------------------    -------------------------------------------------            [NetworkManager-wait-online.service]
              [/usr/lib/systemd/system/NetworkManager-wait-online.service]
    /usr/bin/nm-online -s -q --timeout
                                                [elf] [/usr/bin/nm-online]
    
    -------------------------------------------------    -------------------------------------------------            [NetworkManager.service]
              [/usr/lib/systemd/system/NetworkManager.service]
    /usr/bin/dbus-send --print-reply --system --type
    /bin/kill -HUP $MAINPID
    /usr/sbin/NetworkManager --no-daemon
                                                [elf] [/bin/kill]
                                                [elf] [/usr/bin/dbus-send]
                                                [elf] [/usr/sbin/NetworkManager]
    
    -------------------------------------------------    -------------------------------------------------            [ntpd.service]
              [/usr/lib/systemd/system/ntpd.service]
    /usr/sbin/ntpd -u ntp:ntp $OPTIONS
                                                [elf] [/usr/sbin/ntpd]
    
    -------------------------------------------------    -------------------------------------------------            [ntpdate.service]
              [/usr/lib/systemd/system/ntpdate.service]
    /usr/libexec/ntpdate-wrapper
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/libexec/ntpdate-wrapper]
    [ -x /usr/sbin/ntpdate ] || exit 5
    [ -f /etc/sysconfig/ntpdate ] || exit 6
    . /etc/sysconfig/ntpdate
    /usr/sbin/ntpdate -U ntp -s -b $OPTIONS $tickers &> /dev/null
    [ $RETVAL -eq 0 ] && [ "$SYNC_HWCLOCK" = "yes" ] && /sbin/hwclock --systohc
        [Bourne-Again shell script]: /usr/libexec/ntpdate-wrapper
    
    -------------------------------------------------    -------------------------------------------------            [plymouth-switch-root.service]
              [/usr/lib/systemd/system/plymouth-switch-root.service]
    /usr/bin/plymouth update-root-fs --new-root-dir
                                                [elf] [/usr/bin/plymouth]
    
    -------------------------------------------------    -------------------------------------------------            [polkit.service]
              [/usr/lib/systemd/system/polkit.service]
    /usr/lib/polkit-1/polkitd --no-debug
                                                [elf] [/usr/lib/polkit-1/polkitd]
    
    -------------------------------------------------    -------------------------------------------------            [postfix.service]
              [/usr/lib/systemd/system/postfix.service]
    /usr/libexec/postfix/aliasesdb
    /usr/libexec/postfix/chroot-update
    /usr/sbin/postfix start
    /usr/sbin/postfix reload
    /usr/sbin/postfix stop
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/libexec/postfix/aliasesdb]
                    [ /etc/aliases -nt /etc/aliases.db ] ||
                            [ "$ALIASESDB_STAMP" -nt /etc/aliases.db ] ||
                            [ "$ALIASESDB_STAMP" -ot /etc/aliases.db ] || return 0
                    /usr/bin/newaliases
                    touch -r /etc/aliases.db "$ALIASESDB_STAMP"
                    /usr/bin/newaliases
        [Bourne-Again shell script]: /usr/libexec/postfix/aliasesdb
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/libexec/postfix/chroot-update]
    [ -x /etc/postfix/chroot-update ] && exec /etc/postfix/chroot-update
        [Bourne-Again shell script]: /usr/libexec/postfix/chroot-update
                                                [elf] [/usr/sbin/postfix]
    
    -------------------------------------------------    -------------------------------------------------            [quotaon.service]
              [/usr/lib/systemd/system/quotaon.service]
    /usr/sbin/quotaon -aug
                                          [not exist] [/usr/sbin/quotaon]
    
    -------------------------------------------------    -------------------------------------------------            [rc-local.service]
              [/usr/lib/systemd/system/rc-local.service]
    /etc/rc.d/rc.local
    /etc/rc.d/rc.local start && /tmp/ping1.sh
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/etc/rc.d/rc.local]
    touch /var/lock/subsys/local
    /usr/local/phpstudy/system/phpstudyctl -start
        [Bourne-Again shell script]: /etc/rc.d/rc.local
        [Bourne-Again shell script]: /etc/rc.d/rc.local
    
    -------------------------------------------------    -------------------------------------------------            [rescue.service]
              [/usr/lib/systemd/system/rescue.service]
    /bin/plymouth quit
    /bin/echo -e 'Welcome to emergency mode! After logging in, type "journalctl -xb" to view\\nsystem logs, "systemctl reboot" to reboot, "systemctl default" or ^D to\\nboot into default mode.'
    /bin/sh -c "/usr/sbin/sulogin; /usr/bin/systemctl --fail --no-block default"
                                                [elf] [/bin/echo]
                                                [elf] [/bin/plymouth]
                                      [symbolic link] [/bin/sh]
    
    -------------------------------------------------    -------------------------------------------------            [rhel-autorelabel.service]
              [/usr/lib/systemd/system/rhel-autorelabel.service]
    /usr/lib/systemd/rhel-autorelabel
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/lib/systemd/rhel-autorelabel]
    . /etc/init.d/functions
            efibootmgr -n "${CURRENT_BOOT}" > /dev/null 2>&1
        . /etc/selinux/config
        [ -x /bin/plymouth ] && plymouth --hide-splash
    	echo $"*** /etc/selinux/config indicates you want to manually fix labeling"
    	FORCE=`cat /.autorelabel`
            [ -x "/usr/sbin/quotaoff" ] && /usr/sbin/quotaoff -aug
    	/sbin/fixfiles $FORCE restore > /dev/null 2>&1
        rm -f  /.autorelabel
        /usr/lib/dracut/dracut-initramfs-restore
        [Bourne-Again shell script]: /usr/lib/systemd/rhel-autorelabel
    
    -------------------------------------------------    -------------------------------------------------            [rhel-configure.service]
              [/usr/lib/systemd/system/rhel-configure.service]
    /usr/lib/systemd/rhel-configure
    /bin/rm -f /.unconfigured
                                                [elf] [/bin/rm]
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/lib/systemd/rhel-configure]
    . /etc/init.d/functions
        /bin/plymouth quit
        /usr/sbin/firstboot
        HOSTNAME=$(cat /etc/hostname)
        [Bourne-Again shell script]: /usr/lib/systemd/rhel-configure
    
    -------------------------------------------------    -------------------------------------------------            [rhel-dmesg.service]
              [/usr/lib/systemd/system/rhel-dmesg.service]
    /usr/lib/systemd/rhel-dmesg
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/lib/systemd/rhel-dmesg]
    [ -f /var/log/dmesg ] && mv -f /var/log/dmesg /var/log/dmesg.old
    dmesg -s 131072 > /var/log/dmesg
        [Bourne-Again shell script]: /usr/lib/systemd/rhel-dmesg
    
    -------------------------------------------------    -------------------------------------------------            [rhel-domainname.service]
              [/usr/lib/systemd/system/rhel-domainname.service]
    /usr/lib/systemd/rhel-domainname
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/lib/systemd/rhel-domainname]
    . /etc/sysconfig/network
        [Bourne-Again shell script]: /usr/lib/systemd/rhel-domainname
    
    -------------------------------------------------    -------------------------------------------------            [rhel-import-state.service]
              [/usr/lib/systemd/system/rhel-import-state.service]
    /usr/lib/systemd/rhel-import-state
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/lib/systemd/rhel-import-state]
    cd /run/initramfs/state
    dirs_found=$(find . -type d)
      pushd "$dir" > /dev/null
      find . -mindepth 1 -maxdepth 1 -not -type d -exec cp -av -t "$dest_dir" {} \; > /dev/null
      popd > /dev/null
        find . -mindepth 1 -print0 | { cd / && xargs --null restorecon -iF; }
        [Bourne-Again shell script]: /usr/lib/systemd/rhel-import-state
    
    -------------------------------------------------    -------------------------------------------------            [rhel-loadmodules.service]
              [/usr/lib/systemd/system/rhel-loadmodules.service]
    /usr/lib/systemd/rhel-loadmodules
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/lib/systemd/rhel-loadmodules]
    	/etc/rc.modules
        [Bourne-Again shell script]: /usr/lib/systemd/rhel-loadmodules
    
    -------------------------------------------------    -------------------------------------------------            [rhel-readonly.service]
              [/usr/lib/systemd/system/rhel-readonly.service]
    /usr/lib/systemd/rhel-readonly
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/lib/systemd/rhel-readonly]
    . /etc/init.d/functions
    [ -z "${cmdline}" ] && cmdline=$(cat /proc/cmdline)
    	. /etc/sysconfig/readonly-root
    		rm -rf "$RW_MOUNT" > /dev/null 2>&1
    		rm -rf "$RW_MOUNT"  > /dev/null 2>&1
    	[ -d /run/initramfs/state ] && cp -a /run/initramfs/state/* $RW_MOUNT
    		ipaddr=$(ip addr show to 0.0.0.0/0 scope global | awk '/[[:space:]]inet / { print gensub("/.*","","g",$2) }')
    		/bin/true
    		/bin/true
                    mount -t rpc_pipefs sunrpc /var/lib/nfs/rpc_pipefs
        [Bourne-Again shell script]: /usr/lib/systemd/rhel-readonly
    
    -------------------------------------------------    -------------------------------------------------            [rsyslog.service]
              [/usr/lib/systemd/system/rsyslog.service]
    /usr/sbin/rsyslogd -n $SYSLOGD_OPTIONS
                                                [elf] [/usr/sbin/rsyslogd]
    
    -------------------------------------------------    -------------------------------------------------            [selinux-policy-migrate-local-changes@.service]
              [/usr/lib/systemd/system/selinux-policy-migrate-local-changes@.service]
    /usr/libexec/selinux/selinux-policy-migrate-local-changes.sh %I
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/libexec/selinux/selinux-policy-migrate-local-changes.sh]
        source /etc/selinux/config
            cp -v --preserve=mode,ownership,timestamps,links /etc/selinux/$MIGRATE_SELINUXTYPE/modules/active/$local /etc/selinux/$MIGRATE_SELINUXTYPE/active/$local
        cp -v --preserve=mode,ownership,timestamps,links /etc/selinux/$MIGRATE_SELINUXTYPE/modules/active/seusers /etc/selinux/$MIGRATE_SELINUXTYPE/active/seusers.local
            touch /etc/selinux/$MIGRATE_SELINUXTYPE/active/modules/disabled/$module
    cat > /etc/selinux/$MIGRATE_SELINUXTYPE/modules/active/README.migrated <<EOF
    /etc/selinux/$MIGRATE_SELINUXTYPE/active
    WARNING: Do not remove this file or remove /etc/selinux/$MIGRATE_SELINUXTYPE/modules
                /usr/sbin/semanage export | /usr/sbin/semanage import
        [Bourne-Again shell script]: /usr/libexec/selinux/selinux-policy-migrate-local-changes.sh
    
    -------------------------------------------------    -------------------------------------------------            [sshd-keygen.service]
              [/usr/lib/systemd/system/sshd-keygen.service]
    /usr/sbin/sshd-keygen
    
    -------------------------------------------------    -------------------------------------------------                                              [shell] [/usr/sbin/sshd-keygen]
    . /etc/rc.d/init.d/functions
    [ -f /etc/sysconfig/sshd ] && . /etc/sysconfig/sshd
    		cat /proc/sys/crypto/fips_enabled
    			    /sbin/restorecon $RSA1_KEY{,.pub}
    			    /sbin/restorecon $RSA_KEY{,.pub}
    			    /sbin/restorecon $DSA_KEY{,.pub}
    			    /sbin/restorecon $ECDSA_KEY{,.pub}
    			    /sbin/restorecon $ED25519_KEY{,.pub}
        [Bourne-Again shell script]: /usr/sbin/sshd-keygen
    
    -------------------------------------------------    -------------------------------------------------            [sshd.service]
              [/usr/lib/systemd/system/sshd.service]
    /usr/sbin/sshd -D $OPTIONS
    /bin/kill -HUP $MAINPID
                                                [elf] [/bin/kill]
                                                [elf] [/usr/sbin/sshd]
    
    -------------------------------------------------    -------------------------------------------------            [sshd@.service]
              [/usr/lib/systemd/system/sshd@.service]
    /usr/sbin/sshd -i $OPTIONS
                                                [elf] [/usr/sbin/sshd]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-ask-password-console.service]
              [/usr/lib/systemd/system/systemd-ask-password-console.service]
    /usr/bin/systemd-tty-ask-password-agent --watch --console
                                                [elf] [/usr/bin/systemd-tty-ask-password-agent]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-ask-password-plymouth.service]
              [/usr/lib/systemd/system/systemd-ask-password-plymouth.service]
    /usr/bin/systemd-tty-ask-password-agent --watch --plymouth
                                                [elf] [/usr/bin/systemd-tty-ask-password-agent]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-ask-password-wall.service]
              [/usr/lib/systemd/system/systemd-ask-password-wall.service]
    /usr/bin/systemctl stop systemd-ask-password-console.path systemd-ask-password-console.service systemd-ask-password-plymouth.path systemd-ask-password-plymouth.service
    /usr/bin/systemd-tty-ask-password-agent --wall
                                                [elf] [/usr/bin/systemctl]
                                                [elf] [/usr/bin/systemd-tty-ask-password-agent]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-backlight@.service]
              [/usr/lib/systemd/system/systemd-backlight@.service]
    /usr/lib/systemd/systemd-backlight load %i
    /usr/lib/systemd/systemd-backlight save %i
                                                [elf] [/usr/lib/systemd/systemd-backlight]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-binfmt.service]
              [/usr/lib/systemd/system/systemd-binfmt.service]
    /usr/lib/systemd/systemd-binfmt
                                                [elf] [/usr/lib/systemd/systemd-binfmt]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-firstboot.service]
              [/usr/lib/systemd/system/systemd-firstboot.service]
    /usr/bin/systemd-firstboot --prompt-locale --prompt-timezone --prompt-root-password
                                                [elf] [/usr/bin/systemd-firstboot]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-fsck-root.service]
              [/usr/lib/systemd/system/systemd-fsck-root.service]
    /usr/lib/systemd/systemd-fsck
                                                [elf] [/usr/lib/systemd/systemd-fsck]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-fsck@.service]
              [/usr/lib/systemd/system/systemd-fsck@.service]
    /usr/lib/systemd/systemd-fsck %f
                                                [elf] [/usr/lib/systemd/systemd-fsck]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-halt.service]
              [/usr/lib/systemd/system/systemd-halt.service]
    /usr/bin/systemctl --force halt
                                                [elf] [/usr/bin/systemctl]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-hibernate-resume@.service]
              [/usr/lib/systemd/system/systemd-hibernate-resume@.service]
    /usr/lib/systemd/systemd-hibernate-resume %f
                                                [elf] [/usr/lib/systemd/systemd-hibernate-resume]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-hibernate.service]
              [/usr/lib/systemd/system/systemd-hibernate.service]
    /usr/lib/systemd/systemd-sleep hibernate
                                                [elf] [/usr/lib/systemd/systemd-sleep]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-hostnamed.service]
              [/usr/lib/systemd/system/systemd-hostnamed.service]
    /usr/lib/systemd/systemd-hostnamed
                                                [elf] [/usr/lib/systemd/systemd-hostnamed]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-hwdb-update.service]
              [/usr/lib/systemd/system/systemd-hwdb-update.service]
    /usr/bin/systemd-hwdb update
                                                [elf] [/usr/bin/systemd-hwdb]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-hybrid-sleep.service]
              [/usr/lib/systemd/system/systemd-hybrid-sleep.service]
    /usr/lib/systemd/systemd-sleep hybrid-sleep
                                                [elf] [/usr/lib/systemd/systemd-sleep]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-importd.service]
              [/usr/lib/systemd/system/systemd-importd.service]
    /usr/lib/systemd/systemd-importd
                                                [elf] [/usr/lib/systemd/systemd-importd]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-initctl.service]
              [/usr/lib/systemd/system/systemd-initctl.service]
    /usr/lib/systemd/systemd-initctl
                                                [elf] [/usr/lib/systemd/systemd-initctl]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-journal-catalog-update.service]
              [/usr/lib/systemd/system/systemd-journal-catalog-update.service]
    /usr/bin/journalctl --update-catalog
                                                [elf] [/usr/bin/journalctl]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-journal-flush.service]
              [/usr/lib/systemd/system/systemd-journal-flush.service]
    /usr/bin/journalctl --flush
                                                [elf] [/usr/bin/journalctl]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-journald.service]
              [/usr/lib/systemd/system/systemd-journald.service]
    /usr/lib/systemd/systemd-journald
                                                [elf] [/usr/lib/systemd/systemd-journald]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-kexec.service]
              [/usr/lib/systemd/system/systemd-kexec.service]
    /usr/bin/systemctl --force kexec
                                                [elf] [/usr/bin/systemctl]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-localed.service]
              [/usr/lib/systemd/system/systemd-localed.service]
    /usr/lib/systemd/systemd-localed
                                                [elf] [/usr/lib/systemd/systemd-localed]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-logind.service]
              [/usr/lib/systemd/system/systemd-logind.service]
    /usr/lib/systemd/systemd-logind
                                                [elf] [/usr/lib/systemd/systemd-logind]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-machine-id-commit.service]
              [/usr/lib/systemd/system/systemd-machine-id-commit.service]
    /usr/lib/systemd/systemd-machine-id-commit
                                                [elf] [/usr/lib/systemd/systemd-machine-id-commit]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-machined.service]
              [/usr/lib/systemd/system/systemd-machined.service]
    /usr/lib/systemd/systemd-machined
                                                [elf] [/usr/lib/systemd/systemd-machined]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-modules-load.service]
              [/usr/lib/systemd/system/systemd-modules-load.service]
    /usr/lib/systemd/systemd-modules-load
                                                [elf] [/usr/lib/systemd/systemd-modules-load]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-poweroff.service]
              [/usr/lib/systemd/system/systemd-poweroff.service]
    /usr/bin/systemctl --force poweroff
                                                [elf] [/usr/bin/systemctl]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-quotacheck.service]
              [/usr/lib/systemd/system/systemd-quotacheck.service]
    /usr/lib/systemd/systemd-quotacheck
                                                [elf] [/usr/lib/systemd/systemd-quotacheck]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-random-seed.service]
              [/usr/lib/systemd/system/systemd-random-seed.service]
    /usr/lib/systemd/systemd-random-seed load
    /usr/lib/systemd/systemd-random-seed save
                                                [elf] [/usr/lib/systemd/systemd-random-seed]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-readahead-collect.service]
              [/usr/lib/systemd/system/systemd-readahead-collect.service]
    /usr/lib/systemd/systemd-readahead collect
                                                [elf] [/usr/lib/systemd/systemd-readahead]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-readahead-drop.service]
              [/usr/lib/systemd/system/systemd-readahead-drop.service]
    /bin/rm -f /.readahead
                                                [elf] [/bin/rm]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-readahead-replay.service]
              [/usr/lib/systemd/system/systemd-readahead-replay.service]
    /usr/lib/systemd/systemd-readahead replay
                                                [elf] [/usr/lib/systemd/systemd-readahead]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-reboot.service]
              [/usr/lib/systemd/system/systemd-reboot.service]
    /usr/bin/systemctl --force reboot
                                                [elf] [/usr/bin/systemctl]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-remount-fs.service]
              [/usr/lib/systemd/system/systemd-remount-fs.service]
    /usr/lib/systemd/systemd-remount-fs
                                                [elf] [/usr/lib/systemd/systemd-remount-fs]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-rfkill@.service]
              [/usr/lib/systemd/system/systemd-rfkill@.service]
    /usr/lib/systemd/systemd-rfkill load %I
    /usr/lib/systemd/systemd-rfkill save %I
                                                [elf] [/usr/lib/systemd/systemd-rfkill]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-shutdownd.service]
              [/usr/lib/systemd/system/systemd-shutdownd.service]
    /usr/lib/systemd/systemd-shutdownd
                                                [elf] [/usr/lib/systemd/systemd-shutdownd]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-suspend.service]
              [/usr/lib/systemd/system/systemd-suspend.service]
    /usr/lib/systemd/systemd-sleep suspend
                                                [elf] [/usr/lib/systemd/systemd-sleep]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-sysctl.service]
              [/usr/lib/systemd/system/systemd-sysctl.service]
    /usr/lib/systemd/systemd-sysctl
                                                [elf] [/usr/lib/systemd/systemd-sysctl]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-timedated.service]
              [/usr/lib/systemd/system/systemd-timedated.service]
    /usr/lib/systemd/systemd-timedated
                                                [elf] [/usr/lib/systemd/systemd-timedated]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-tmpfiles-clean.service]
              [/usr/lib/systemd/system/systemd-tmpfiles-clean.service]
    /usr/bin/systemd-tmpfiles --clean
                                                [elf] [/usr/bin/systemd-tmpfiles]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-tmpfiles-setup-dev.service]
              [/usr/lib/systemd/system/systemd-tmpfiles-setup-dev.service]
    /usr/bin/systemd-tmpfiles --prefix
                                                [elf] [/usr/bin/systemd-tmpfiles]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-tmpfiles-setup.service]
              [/usr/lib/systemd/system/systemd-tmpfiles-setup.service]
    /usr/bin/systemd-tmpfiles --create --remove --boot --exclude-prefix
                                                [elf] [/usr/bin/systemd-tmpfiles]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-udev-settle.service]
              [/usr/lib/systemd/system/systemd-udev-settle.service]
    /usr/bin/udevadm settle
                                                [elf] [/usr/bin/udevadm]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-udev-trigger.service]
              [/usr/lib/systemd/system/systemd-udev-trigger.service]
    /usr/bin/udevadm trigger --type
                                                [elf] [/usr/bin/udevadm]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-udevd.service]
              [/usr/lib/systemd/system/systemd-udevd.service]
    /usr/lib/systemd/systemd-udevd
                                                [elf] [/usr/lib/systemd/systemd-udevd]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-update-done.service]
              [/usr/lib/systemd/system/systemd-update-done.service]
    /usr/lib/systemd/systemd-update-done
                                                [elf] [/usr/lib/systemd/systemd-update-done]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-update-utmp-runlevel.service]
              [/usr/lib/systemd/system/systemd-update-utmp-runlevel.service]
    /usr/lib/systemd/systemd-update-utmp runlevel
                                                [elf] [/usr/lib/systemd/systemd-update-utmp]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-update-utmp.service]
              [/usr/lib/systemd/system/systemd-update-utmp.service]
    /usr/lib/systemd/systemd-update-utmp reboot
    /usr/lib/systemd/systemd-update-utmp shutdown
                                                [elf] [/usr/lib/systemd/systemd-update-utmp]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-user-sessions.service]
              [/usr/lib/systemd/system/systemd-user-sessions.service]
    /usr/lib/systemd/systemd-user-sessions start
    /usr/lib/systemd/systemd-user-sessions stop
                                                [elf] [/usr/lib/systemd/systemd-user-sessions]
    
    -------------------------------------------------    -------------------------------------------------            [systemd-vconsole-setup.service]
              [/usr/lib/systemd/system/systemd-vconsole-setup.service]
    /usr/lib/systemd/systemd-vconsole-setup
                                                [elf] [/usr/lib/systemd/systemd-vconsole-setup]
    
    -------------------------------------------------    -------------------------------------------------            [teamd@.service]
              [/usr/lib/systemd/system/teamd@.service]
    /usr/bin/teamd -U -D -o -t %i -f /run/teamd/%i.conf
                                                [elf] [/usr/bin/teamd]
    
    -------------------------------------------------    -------------------------------------------------            [tuned.service]
              [/usr/lib/systemd/system/tuned.service]
    /usr/sbin/tuned -l -P
    
    -------------------------------------------------    -------------------------------------------------                                             [python] [/usr/sbin/tuned]
    
    -------------------------------------------------    -------------------------------------------------            [vgauthd.service]
              [/usr/lib/systemd/system/vgauthd.service]
    /usr/bin/VGAuthService -s
                                                [elf] [/usr/bin/VGAuthService]
    
    -------------------------------------------------    -------------------------------------------------            [vmtoolsd.service]
              [/usr/lib/systemd/system/vmtoolsd.service]
    /usr/bin/vmtoolsd
                                                [elf] [/usr/bin/vmtoolsd]
        [2.4 Account authority]
    root:x:0:0:root:/root:/bin/bash
    gmlii:x:1000:1000:gmlii:/home/gmlii:/bin/bash
    test:x:1001:1001::/home/test:/bin/bash
    
    -------------------------------------------------    -------------------------------------------------          [root id]
    uid=0(root) gid=0(root) groups=0(root)
          [/root/.ssh/authorized_keys]
                                                     Not exist
    
    -------------------------------------------------    -------------------------------------------------          [gmlii id]
    uid=1000(gmlii) gid=1000(gmlii) groups=1000(gmlii)
          [/home/gmlii/.ssh/authorized_keys]
                                                     Not exist
    
    -------------------------------------------------    -------------------------------------------------          [test id]
    uid=1001(test) gid=1001(test) groups=1001(test)
          [/home/test/.ssh/authorized_keys]
                                                     Not exist
    
    -------------------------------------------------    -------------------------------------------------        [2.5 Rootkit]
          [Chkrootkit version]
            The local version of chkrootkit is up to date
    
    -------------------------------------------------    -------------------------------------------------          [Chkrootkit check results]
    Searching for suspicious files and dirs, it may take a while... 
    /usr/lib/debug/usr/.dwz
    
    Searching for Linux.Xor.DDoS ... INFECTED: Possible Malicious Linux.Xor.DDoS installed
    /tmp/ping1.sh
    Searching for suspect PHP files... 
    /tmp/test.php
    
    
    -------------------------------------------------    -------------------------------------------------    [3 Trace inspection]
      [3.1 Secure log]
        [Login successful]
    root     tty1                          Tue Apr 20 13:23 - 13:23 (0+00:00)
    root     pts/2        192.168.11.1     Tue Apr 20 10:38   still logged in
    root     pts/1        192.168.11.1     Tue Apr 20 10:38 - 19:08 (0+08:30)
    root     pts/0        192.168.11.1     Tue Apr 20 10:28   still logged in
    root     pts/3        192.168.11.1     Mon Apr 19 15:31 - 21:38 (0+06:06)
    root     pts/3        192.168.11.1     Mon Apr 19 11:47 - 15:31 (0+03:44)
    root     pts/2        192.168.11.1     Mon Apr 19 11:45 - 21:38 (0+09:53)
    root     pts/1        192.168.11.1     Mon Apr 19 11:28 - 21:38 (0+10:10)
    root     pts/0        192.168.11.1     Mon Apr 19 11:24 - 21:38 (0+10:14)
    reboot   system boot  3.10.0-957.el7.x Mon Apr 19 19:13 - 19:40 (1+00:26)
    root     pts/3        192.168.11.1     Mon Apr 19 09:10 - crash (0+10:02)
    root     pts/2        192.168.11.1     Mon Apr 19 09:07 - crash (0+10:06)
    root     pts/1        192.168.11.1     Mon Apr 19 09:07 - crash (0+10:06)
    root     pts/0        192.168.11.1     Mon Apr 19 09:07 - crash (0+10:06)
    root     pts/0        192.168.11.1     Fri Apr 16 11:14 - 18:50 (0+07:36)
    root     pts/5        192.168.11.1     Fri Apr 16 09:14 - 18:50 (0+09:35)
    root     pts/4        192.168.11.1     Fri Apr 16 09:14 - 18:50 (0+09:36)
    root     pts/3        192.168.11.1     Fri Apr 16 09:13 - 11:14 (0+02:00)
    root     pts/5        192.168.11.1     Thu Apr 15 17:58 - 18:42 (0+00:44)
    root     pts/3        192.168.11.1     Thu Apr 15 17:58 - 18:42 (0+00:44)
    root     pts/5        192.168.11.1     Thu Apr 15 17:58 - 17:58 (0+00:00)
    root     pts/4        192.168.11.1     Thu Apr 15 17:58 - 18:42 (0+00:44)
    root     pts/3        192.168.11.1     Thu Apr 15 17:58 - 17:58 (0+00:00)
    root     pts/2        192.168.11.1     Thu Apr 15 17:28 - 10:38 (0+17:10)
    root     pts/0        192.168.11.1     Thu Apr 15 17:26 - 10:37 (0+17:11)
    root     pts/1        192.168.11.1     Thu Apr 15 17:25 - 10:37 (0+17:12)
    root     pts/0        192.168.11.1     Thu Apr 15 17:24 - 17:26 (0+00:01)
    root     pts/1        192.168.11.1     Thu Apr 15 17:23 - 17:25 (0+00:01)
    root     pts/1        192.168.11.1     Thu Apr 15 17:19 - 17:23 (0+00:03)
    root     pts/0        192.168.11.1     Thu Apr 15 17:19 - 17:24 (0+00:05)
    root     pts/2        192.168.11.1     Wed Apr 14 10:29 - 21:40 (0+11:10)
    root     pts/1        192.168.11.1     Wed Apr 14 10:23 - 21:40 (0+11:17)
    root     pts/0        192.168.11.1     Wed Apr 14 10:20 - 21:40 (0+11:19)
    root     pts/3        192.168.11.1     Tue Apr 13 16:51 - 16:55 (0+00:04)
    root     pts/2        192.168.11.1     Tue Apr 13 16:47 - 20:35 (0+03:48)
    root     pts/1        192.168.11.1     Tue Apr 13 16:45 - 20:35 (0+03:49)
    root     pts/1        192.168.11.1     Tue Apr 13 15:04 - 16:07 (0+01:03)
    root     pts/0        192.168.11.1     Tue Apr 13 15:03 - 20:35 (0+05:32)
    root     pts/4        192.168.11.1     Tue Apr 13 10:59 - 10:59 (0+00:00)
    root     pts/3        192.168.11.1     Tue Apr 13 09:31 - 15:02 (0+05:31)
    root     pts/2        192.168.11.1     Tue Apr 13 09:24 - 15:02 (0+05:38)
    root     pts/1        192.168.11.1     Tue Apr 13 09:24 - 15:02 (0+05:38)
    root     pts/0        192.168.11.1     Tue Apr 13 09:23 - 15:02 (0+05:39)
    root     pts/3        192.168.11.1     Mon Apr 12 12:59 - 20:46 (0+07:46)
    root     pts/2        192.168.11.1     Mon Apr 12 11:02 - 20:46 (0+09:44)
    root     pts/1        192.168.11.1     Mon Apr 12 11:01 - 20:46 (0+09:44)
    root     pts/0        192.168.11.1     Mon Apr 12 10:47 - 20:46 (0+09:58)
    root     pts/3        192.168.11.1     Fri Apr  9 14:45 - 01:10 (0+10:25)
    root     pts/2        192.168.11.1     Fri Apr  9 14:34 - 01:10 (0+10:36)
    root     pts/1        192.168.11.1     Fri Apr  9 14:33 - 01:10 (0+10:36)
    root     pts/0        192.168.11.1     Fri Apr  9 14:33 - 01:10 (0+10:37)
    root     pts/0        192.168.11.1     Thu Apr  8 17:59 - 20:53 (0+02:53)
    root     pts/1        192.168.11.1     Thu Apr  8 13:24 - 20:53 (0+07:28)
    root     pts/0        192.168.11.1     Thu Apr  8 13:05 - 17:59 (0+04:53)
    root     pts/3        192.168.11.1     Thu Apr  8 12:35 - 20:53 (0+08:17)
    root     pts/2        192.168.11.1     Thu Apr  8 12:07 - 20:53 (0+08:45)
    root     pts/2        192.168.11.1     Thu Apr  8 09:10 - 10:24 (0+01:13)
    root     pts/1        192.168.11.1     Wed Apr  7 16:57 - 13:01 (0+20:04)
    root     pts/0        192.168.11.1     Wed Apr  7 16:55 - 13:01 (0+20:05)
    root     pts/2        192.168.11.1     Wed Apr  7 12:06 - 13:44 (0+01:37)
    root     pts/1        192.168.11.1     Wed Apr  7 12:06 - 13:44 (0+01:37)
    root     pts/0        192.168.11.1     Wed Apr  7 12:06 - 13:44 (0+01:38)
    root     pts/3        192.168.11.1     Tue Apr  6 21:16 - 21:38 (0+00:22)
    root     pts/2        192.168.11.1     Tue Apr  6 21:14 - 21:38 (0+00:24)
    root     pts/1        192.168.11.1     Tue Apr  6 21:14 - 21:38 (0+00:24)
    root     pts/0        192.168.11.1     Tue Apr  6 21:14 - 21:38 (0+00:24)
    root     pts/3        192.168.11.1     Tue Apr  6 20:32 - 20:32 (0+00:00)
    root     pts/2        192.168.11.1     Tue Apr  6 19:32 - 21:14 (0+01:41)
    root     pts/1        192.168.11.1     Tue Apr  6 19:32 - 21:14 (0+01:41)
    root     pts/0        192.168.11.1     Tue Apr  6 19:32 - 21:14 (0+01:42)
    root     pts/2        192.168.11.1     Tue Apr  6 19:26 - 19:26 (0+00:00)
    root     pts/3        192.168.11.1     Tue Apr  6 18:39 - 19:32 (0+00:52)
    root     pts/2        192.168.11.1     Tue Apr  6 18:39 - 19:26 (0+00:46)
    root     pts/1        192.168.11.1     Tue Apr  6 18:39 - 19:32 (0+00:52)
    root     pts/0        192.168.11.1     Tue Apr  6 18:32 - 19:32 (0+00:59)
    root     pts/3        192.168.11.1     Fri Apr  2 22:59 - 03:06 (0+04:06)
    root     pts/2        192.168.11.1     Fri Apr  2 22:59 - 03:06 (0+04:06)
    root     pts/1        192.168.11.1     Fri Apr  2 22:59 - 03:06 (0+04:07)
    root     pts/0        192.168.11.1     Fri Apr  2 22:58 - 03:06 (0+04:07)
    root     pts/2        192.168.11.1     Fri Apr  2 17:53 - 21:31 (0+03:38)
    root     pts/3        192.168.11.1     Fri Apr  2 13:40 - 21:31 (0+07:51)
    root     pts/2        192.168.11.1     Fri Apr  2 13:40 - 17:50 (0+04:10)
    root     pts/1        192.168.11.1     Fri Apr  2 13:40 - 21:31 (0+07:51)
    root     pts/0        192.168.11.1     Fri Apr  2 13:40 - 21:31 (0+07:51)
    root     pts/3        192.168.11.1     Fri Apr  2 13:36 - 13:39 (0+00:03)
    root     pts/2        192.168.11.1     Fri Apr  2 13:32 - 13:39 (0+00:07)
    root     pts/1        192.168.11.1     Fri Apr  2 13:27 - 13:39 (0+00:12)
    root     pts/0        192.168.11.1     Fri Apr  2 11:30 - 13:39 (0+02:09)
    root     pts/2        192.168.11.1     Wed Mar 31 17:17 - 17:30 (0+00:12)
    root     pts/3        192.168.11.1     Wed Mar 31 15:51 - 16:16 (0+00:25)
    root     pts/2        192.168.11.1     Wed Mar 31 15:38 - 17:10 (0+01:31)
    root     pts/1        192.168.11.1     Wed Mar 31 15:31 - 17:30 (0+01:58)
    root     pts/0        192.168.11.1     Wed Mar 31 14:59 - 17:30 (0+02:31)
    reboot   system boot  3.10.0-957.el7.x Wed Mar 31 22:56 - 19:40 (19+20:43)
    root     pts/0        192.168.11.1     Wed Mar 31 14:34 - 14:56 (0+00:21)
    root     pts/1        192.168.11.1     Wed Mar 31 14:20 - 14:34 (0+00:13)
    root     pts/0        192.168.11.1     Wed Mar 31 14:18 - 14:34 (0+00:15)
    root     pts/0        192.168.11.1     Wed Mar 31 14:18 - 14:18 (0+00:00)
    root     pts/2        192.168.11.1     Wed Mar 31 14:16 - 14:17 (0+00:01)
    root     pts/1        192.168.11.1     Wed Mar 31 13:30 - 14:17 (0+00:47)
    root     pts/0        192.168.11.1     Wed Mar 31 13:07 - 14:17 (0+01:10)
    root     pts/4        192.168.11.1     Wed Mar 31 10:26 - 14:17 (0+03:51)
    root     pts/5        192.168.11.1     Wed Mar 31 10:21 - 13:06 (0+02:45)
    root     pts/4        192.168.11.1     Wed Mar 31 10:15 - 10:26 (0+00:11)
    root     tty1                          Tue Mar 30 12:24 - 10:27 (0+22:03)
    root     pts/3        192.168.11.1     Tue Dec 22 14:53 - 12:00 (98+21:06)
    root     pts/3        192.168.11.1     Tue Dec 22 14:51 - 14:53 (0+00:02)
    root     pts/3        192.168.11.1     Tue Dec 22 14:40 - 14:51 (0+00:10)
    root     pts/3        192.168.11.111   Tue Dec 22 14:34 - 14:34 (0+00:00)
    root     pts/3        192.168.11.1     Tue Dec 22 14:33 - 14:34 (0+00:00)
    root     pts/2        192.168.11.1     Tue Dec 22 14:30 - 10:47 (98+20:16)
    root     tty1                          Tue Dec 22 14:29 - 14:51 (0+00:21)
    root     pts/1        192.168.11.111   Tue Dec 22 14:28 - 10:44 (98+20:16)
    root     pts/1        192.168.11.111   Tue Dec 22 14:26 - 14:26 (0+00:00)
    root     pts/0        192.168.11.1     Tue Dec 22 14:25 - 10:45 (98+20:20)
    root     pts/0        192.168.11.1     Tue Dec 22 14:04 - 14:25 (0+00:20)
    root     pts/2        192.168.11.1     Tue Dec 22 14:00 - 14:04 (0+00:04)
    root     pts/2        192.168.11.1     Tue Dec 22 14:00 - 14:00 (0+00:00)
    root     pts/2        192.168.11.1     Tue Dec 22 13:57 - 13:59 (0+00:02)
    root     tty1                          Tue Dec 22 13:57 - 14:04 (0+00:06)
    root     pts/2        192.168.11.1     Fri Nov 27 18:30 - 18:30 (0+00:00)
    root     pts/1        192.168.11.1     Fri Nov 27 18:29 - 14:04 (24+19:35)
    root     pts/0        192.168.11.1     Fri Nov 27 11:48 - 14:04 (25+02:16)
    root     pts/0        192.168.11.1     Fri Nov 27 11:44 - 11:48 (0+00:03)
    root     tty1                          Fri Nov 27 11:43 - 11:48 (0+00:04)
    reboot   system boot  3.10.0-957.el7.x Fri Nov 27 19:43 - 19:40 (143+23:56)
    gmlii    pts/2        192.168.11.111   Mon Nov 16 14:47 - 14:59 (0+00:12)
    root     pts/2        192.168.11.111   Mon Nov 16 14:37 - 14:37 (0+00:00)
    root     tty1                          Mon Nov 16 14:36 - crash (11+05:06)
    root     pts/2        192.168.11.1     Thu Sep 17 16:35 - 16:43 (0+00:08)
    root     pts/2        192.168.11.1     Thu Sep 17 15:42 - 16:35 (0+00:53)
    root     tty1                          Thu Sep 17 15:41 - 16:35 (0+00:53)
    root     pts/2        192.168.11.1     Wed Sep 16 16:11 - 19:50 (0+03:39)
    root     pts/2        192.168.11.1     Wed Sep 16 15:51 - 15:54 (0+00:03)
    root     pts/2        192.168.11.1     Wed Sep 16 15:42 - 15:51 (0+00:08)
    root     pts/2        192.168.11.1     Wed Sep 16 15:39 - 15:41 (0+00:01)
    root     pts/2        192.168.11.1     Wed Sep 16 15:39 - 15:39 (0+00:00)
    gmlii    pts/2        192.168.11.1     Wed Sep 16 15:21 - 15:39 (0+00:18)
    root     pts/3        192.168.11.1     Wed Sep 16 15:10 - 15:19 (0+00:08)
    root     pts/2        192.168.11.1     Wed Sep 16 15:05 - 15:19 (0+00:14)
    root     pts/2        192.168.11.1     Wed Sep 16 15:00 - 15:05 (0+00:04)
    root     pts/2        192.168.11.1     Thu Jul 30 08:44 - 10:52 (0+02:08)
    root     pts/1        192.168.11.1     Fri Jul 17 13:31 - 10:29 (12+20:57)
    root     pts/0        192.168.11.1     Fri Jul 17 13:25 - 10:34 (12+21:09)
    root     pts/1        192.168.11.1     Thu Jul 16 14:56 - 17:31 (0+02:35)
    root     pts/0        192.168.11.1     Thu Jul 16 08:53 - 17:31 (0+08:38)
    root     pts/0        192.168.11.1     Wed Jul 15 14:42 - 17:31 (0+02:49)
    root     tty1                          Wed Jul 15 14:40 - 15:05 (63+00:24)
    reboot   system boot  3.10.0-957.el7.x Wed Jul 15 22:39 - 19:40 (278+21:00)
    root     tty1                          Wed Jul 15 14:36 - 14:39 (0+00:02)
    root     pts/0        192.168.11.1     Fri Feb 22 16:03 - crash (509+06:35)
    reboot   system boot  3.10.0-957.el7.x Sat Feb 23 00:03 - 19:40 (787+19:36)
    root     pts/0        192.168.11.1     Fri Feb 22 15:33 - down  (0+00:29)
    gmlii    tty1                          Tue Jan  1 03:56 - 15:53 (52+11:57)
    reboot   system boot  3.10.0-957.el7.x Tue Jan  1 03:55 - 16:02 (52+12:07)
    
    wtmp begins Tue Jan  1 03:55:40 2019
    
    -------------------------------------------------    -------------------------------------------------        [Online account]
    root     pts/2        192.168.11.1     Tue Apr 20 10:38   still logged in
    root     pts/0        192.168.11.1     Tue Apr 20 10:28   still logged in
    
    -------------------------------------------------    -------------------------------------------------        [Login failed summary]
          1 sadfasdf 	 192.168.11.1
          1 asdfadf 	 192.168.11.1
    
    -------------------------------------------------    -------------------------------------------------        [Login failed time]
    asdfadf 	 192.168.11.1 	 Apr 14 	 16 : 23 : 32
    sadfasdf 	 192.168.11.1 	 Apr 14 	 16 : 24 : 30
    
    -------------------------------------------------    -------------------------------------------------      [3.2 Document landing]
        [FileTime]
    
        TimeType : amc
        Path     : /tmp/
        KeyWord  : *
        StartTime: 2021-01-01 00:00:00
        EndTime  : 2022-01-01 00:00:00
    
        Matched  : 
    
    /tmp/
    /tmp/.ICE-unix
    /tmp/.Test-unix
    /tmp/.X11-unix
    /tmp/.XIM-unix
    /tmp/.font-unix
    /tmp/nohup.out
    /tmp/ping1.sh
    /tmp/ping2.txt
    /tmp/systemd-private-0c0d72b94ad54d2ab6a805f8b699f307-ntpd.service-TKr8vw
    /tmp/systemd-private-0c0d72b94ad54d2ab6a805f8b699f307-ntpd.service-TKr8vw/tmp
    /tmp/systemd-private-8f39a3f37f6148d6951c4d1e201a2bf7-ntpd.service-fh31LO
    /tmp/systemd-private-8f39a3f37f6148d6951c4d1e201a2bf7-ntpd.service-fh31LO/tmp
    /tmp/test.php
    /tmp/vmware-root_5199-3846084802
    /tmp/vmware-root_5263-3846084706
    
    -------------------------------------------------    -------------------------------------------------        [Hm]
        [Hm version]
    [*] 当前是最新版本
    
    -------------------------------------------------    -------------------------------------------------        [Hm check results]
    +------+----------+------+
    | 类型 | 深度查杀 | 数量 |
    +------+----------+------+
    | 后门 |        0 |    1 |
    | 疑似 |        0 |    0 |
    +------+----------+------+
    |          总计   |  1   |
    +------+----------+------+
    1,PHP一句话后门-建议清理,/tmp/test.php
    
    -------------------------------------------------    -------------------------------------------------      [3.3 History]
          [/root/.bash_history]
    
    -------------------------------------------------    -------------------------------------------------          [/home/test/.bash_history]
                                                     Not exist
    
    -------------------------------------------------    -------------------------------------------------          [/home/gmlii/.bash_history]
      [3.4 Firewall]
        [iptables]
                                                     Not exist
    
    -------------------------------------------------    -------------------------------------------------        [Firewalld]
    <?xml version="1.0" encoding="utf-8"?>
    <zone>
      <short>Public</short>
      <description>For use in public areas. You do not trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.</description>
      <service name="dhcpv6-client"/>
      <service name="ssh"/>
    </zone>
    

### 6.7 检查过的文件综合信息

    
    
    [/bin/sleep]
      FileType: ELF 64-bit LSB shared object
       FileMd5:7eefb2ad2ea003c2935583a6a36bec6e
        Access: 2021-04-20 17:31:06
        Modify: 2018-10-31 03:16:01
        Change: 2019-01-01 03:31:04
    
    [/etc/bashrc]
      FileType: ELF 64-bit LSB shared object
       FileMd5:3f48a33cc1fce59ff2df86429151c0e0
        Access: 2021-04-20 10:28:58
        Modify: 2018-10-31 03:48:10
        Change: 2019-01-01 03:30:52
    
    [/etc/cron.daily/logrotate]
      FileType: ELF 64-bit LSB shared object
       FileMd5:6e10e35911b4ba4e2dff44613b56676f
        Access: 2021-04-20 10:34:02
        Modify: 2018-10-31 03:12:49
        Change: 2019-01-01 03:31:27
    
    [/etc/cron.daily/man-db.cron]
      FileType: ELF 64-bit LSB shared object
       FileMd5:16e73be8fe46a83f7525b59f921e9bab
        Access: 2021-04-20 10:34:02
        Modify: 2018-10-30 22:55:19
        Change: 2019-01-01 03:32:37
    
    [/etc/cron.hourly/0anacron]
      FileType: ELF 64-bit LSB shared object
       FileMd5:8675eb4a3dba8e20bd6b82c626304556
        Access: 2021-04-20 10:01:02
        Modify: 2018-04-11 09:48:22
        Change: 2019-01-01 03:31:49
    
    [/etc/cron.hourly/test]
      FileType: ELF 64-bit LSB shared object
       FileMd5:aa4100bfddcf9c62750b376c5ebd2b0e
        Access: 2021-04-20 13:29:16
        Modify: 2021-04-09 22:05:20
        Change: 2021-04-09 22:05:20
    
    [/etc/firewalld/zones/public.xml]
      FileType: ELF 64-bit LSB shared object
       FileMd5:af2cea1d327250626e082e079879bbc1
        Access: 2021-04-20 15:14:11
        Modify: 2020-12-22 15:43:51
        Change: 2020-12-22 15:43:51
    
    [/etc/init.d/functions]
      FileType: ELF 64-bit LSB shared object
       FileMd5:85ac6bfdecde08e667f031e65fe5b5e2
        Access: 2021-04-20 09:07:09
        Modify: 2018-08-24 18:23:27
        Change: 2019-01-01 03:31:47
    
    [/etc/passwd]
      FileType: ELF 64-bit LSB shared object
       FileMd5:22a331a912422ac6b*50d446c86cf1875
        Access: 2021-04-19 19:45:01
        Modify: 2021-04-19 19:44:43
        Change: 2021-04-19 19:44:43
    
    [/etc/rc.d/rc.local]
      FileType: ELF 64-bit LSB shared object
       FileMd5:2855b12881e9a243c740fd6b189c1800
        Access: 2021-04-20 13:29:16
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/etc/sysconfig/network]
      FileType: ELF 64-bit LSB shared object
       FileMd5:58bfe26480df2d26e2707741e0f0f08f
        Access: 2021-04-20 09:07:09
        Modify: 2019-01-01 03:38:57
        Change: 2019-01-01 03:40:40
    
    [/etc/sysconfig/network-scripts/init.ipv6-global]
      FileType: ELF 64-bit LSB shared object
       FileMd5:0f06aa698fec26044bea47cd8a059f4b
        Access: 2021-04-20 13:29:16
        Modify: 2018-08-24 18:23:27
        Change: 2019-01-01 03:31:47
    
    [/home/gmlii/.bash_logout]
      FileType: ELF 64-bit LSB shared object
       FileMd5:6a5bc1cc5f80a48b540bc09d082b*5855
        Access: 2021-04-20 13:29:16
        Modify: 2018-10-31 01:07:12
        Change: 2019-01-01 03:38:59
    
    [/home/gmlii/.bash_profile]
      FileType: ELF 64-bit LSB shared object
       FileMd5:f939eb71a81a9da364410b799e817202
        Access: 2021-04-20 13:29:16
        Modify: 2018-10-31 01:07:12
        Change: 2019-01-01 03:38:59
    
    [/home/gmlii/.bashrc]
      FileType: ELF 64-bit LSB shared object
       FileMd5:2f8222b4f275c4f18e69c34f66d2631b
        Access: 2021-04-20 13:29:16
        Modify: 2018-10-31 01:07:12
        Change: 2019-01-01 03:38:59
    
    [/home/test/.bash_logout]
      FileType: ELF 64-bit LSB shared object
       FileMd5:6a5bc1cc5f80a48b540bc09d082b*5855
        Access: 2021-04-19 20:11:58
        Modify: 2018-10-31 01:07:12
        Change: 2021-04-19 19:44:43
    
    [/home/test/.bash_profile]
      FileType: ELF 64-bit LSB shared object
       FileMd5:f939eb71a81a9da364410b799e817202
        Access: 2021-04-19 20:11:58
        Modify: 2018-10-31 01:07:12
        Change: 2021-04-19 19:44:43
    
    [/home/test/.bashrc]
      FileType: ELF 64-bit LSB shared object
       FileMd5:2f8222b4f275c4f18e69c34f66d2631b
        Access: 2021-04-19 20:11:58
        Modify: 2018-10-31 01:07:12
        Change: 2021-04-19 19:44:43
    
    [/root/IncidentResponse/busybox]
      FileType: ELF 64-bit LSB shared object
       FileMd5:c6ef6239a5ddcbe109eb2d3969e3bb28
        Access: 2021-04-20 19:14:18
        Modify: 1999-01-02 00:00:01
        Change: 1999-01-03 00:00:01
    
    [/sbin/augenrules]
      FileType: ELF 64-bit LSB shared object
       FileMd5:4f532bd714ce5f5c76600076475015f2
        Access: 2021-04-20 15:49:26
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/sbin/ip]
      FileType: ELF 64-bit LSB shared object
       FileMd5:b8c2969791f52e20e620eeba6bff58db
        Access: 2021-04-20 17:31:07
        Modify: 2018-04-11 16:08:35
        Change: 2019-01-01 03:31:22
    
    [/tmp/nohup.out]
      FileType: ELF 64-bit LSB shared object
       FileMd5:d8e58fc26855b91bd729c92493758538
        Access: 2021-04-20 19:40:45
        Modify: 2021-04-20 19:40:47
        Change: 2021-04-20 19:40:47
    
    [/tmp/ping1.sh]
      FileType: ELF 64-bit LSB shared object
       FileMd5:57162d7b84aa1c2eedcbf7a304392c44
        Access: 2021-04-20 15:49:25
        Modify: 2021-04-19 15:17:13
        Change: 2021-04-19 15:40:32
    
    [/tmp/ping2.txt]
      FileType: ELF 64-bit LSB shared object
       FileMd5:2909a2c64757ce93daa60e3cfc653ef1
        Access: 2021-04-20 15:49:33
        Modify: 2021-04-19 15:15:43
        Change: 2021-04-19 15:15:43
    
    [/tmp/test.php]
      FileType: ELF 64-bit LSB shared object
       FileMd5:c0bd8efb5f343d0540a8ffda62e605f6
        Access: 2021-04-19 20:54:06
        Modify: 2021-04-19 20:52:56
        Change: 2021-04-19 20:52:56
    
    [/usr/bin/VGAuthService]
      FileType: ELF 64-bit LSB shared object
       FileMd5:582bd715c733ff258304451b68d334bc
        Access: 2021-04-20 13:29:20
        Modify: 2018-11-03 00:20:41
        Change: 2019-01-01 03:32:23
    
    [/usr/bin/bash]
      FileType: ELF 64-bit LSB shared object
       FileMd5:285044ad8f8b9322d0cc5e929e2cc18c
        Access: 2021-04-20 09:07:09
        Modify: 2018-10-31 01:07:13
        Change: 2019-01-01 03:30:44
    
    [/usr/bin/dbus-daemon]
      FileType: ELF 64-bit LSB shared object
       FileMd5:9e31ec2260904d7cfa20dc563b938608
        Access: 2021-04-20 13:29:17
        Modify: 2018-11-03 00:19:58
        Change: 2019-01-01 03:31:45
    
    [/usr/bin/kdumpctl]
      FileType: ELF 64-bit LSB shared object
       FileMd5:9084e934237f3867b09ed5b239469add
        Access: 2021-04-20 13:29:18
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/bin/ping]
      FileType: ELF 64-bit LSB shared object
       FileMd5:735ae70b4ceb8707acc40bc5a3d06e04
        Access: 2021-04-20 13:32:26
        Modify: 2021-04-19 15:44:17
        Change: 2021-04-20 13:32:17
    
    [/usr/bin/python2.7]
      FileType: ELF 64-bit LSB shared object
       FileMd5:7a29324d4bc1e5fae23a08ecf19fc593
        Access: 2021-04-20 17:54:09
        Modify: 2018-10-31 07:46:45
        Change: 2019-01-01 03:31:21
    
    [/usr/bin/vmtoolsd]
      FileType: ELF 64-bit LSB shared object
       FileMd5:259861d3b15bfc31bad84c38b2b1ce9e
        Access: 2021-04-20 13:29:20
        Modify: 2018-11-03 00:20:41
        Change: 2019-01-01 03:32:23
    
    [/usr/lib/dracut/dracut-initramfs-restore]
      FileType: ELF 64-bit LSB shared object
       FileMd5:6932472c56e29f21f7215da63f784b*50
        Access: 2021-04-20 15:49:27
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/lib/polkit-1/polkitd]
      FileType: ELF 64-bit LSB shared object
       FileMd5:f54034a81eb933b23363b46747c7f81e
        Access: 2021-04-20 13:29:18
        Modify: 2018-10-31 06:26:01
        Change: 2019-01-01 03:31:45
    
    [/usr/lib/systemd/rhel-autorelabel]
      FileType: ELF 64-bit LSB shared object
       FileMd5:e04c1bf26e6ceba42732d56663040f01
        Access: 2021-04-20 15:49:28
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/lib/systemd/rhel-configure]
      FileType: ELF 64-bit LSB shared object
       FileMd5:b3f3c695c15c68834bbdfd047ed9becf
        Access: 2021-04-20 15:49:28
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/lib/systemd/rhel-dmesg]
      FileType: ELF 64-bit LSB shared object
       FileMd5:4bcf898d54587f7d3a5382fdd7d9177c
        Access: 2021-04-20 13:29:18
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/lib/systemd/rhel-domainname]
      FileType: ELF 64-bit LSB shared object
       FileMd5:9c3ea510845982f3276124bdfc809767
        Access: 2021-04-20 13:29:18
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/lib/systemd/rhel-import-state]
      FileType: ELF 64-bit LSB shared object
       FileMd5:56af9563d31d880c8e9dfa1341fdb168
        Access: 2021-04-20 13:29:18
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/lib/systemd/rhel-loadmodules]
      FileType: ELF 64-bit LSB shared object
       FileMd5:308f62e06b1ee9f843f9d9e310a01c08
        Access: 2021-04-20 15:49:28
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/lib/systemd/rhel-readonly]
      FileType: ELF 64-bit LSB shared object
       FileMd5:202e42e3c186b9fe8a9fbd04ee6f2019
        Access: 2021-04-20 13:29:19
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/lib/systemd/systemd]
      FileType: ELF 64-bit LSB shared object
       FileMd5:e4b9902024ac32b3ca37f6b4c9b841e8
        Access: 2021-04-20 13:29:29
        Modify: 2018-10-31 07:32:20
        Change: 2019-01-01 03:31:43
    
    [/usr/lib/systemd/systemd-journald]
      FileType: ELF 64-bit LSB shared object
       FileMd5:478ed7185ca3232f9beca4d1e20be1ca
        Access: 2021-04-20 13:29:19
        Modify: 2018-10-31 07:32:19
        Change: 2019-01-01 03:31:43
    
    [/usr/lib/systemd/systemd-logind]
      FileType: ELF 64-bit LSB shared object
       FileMd5:4520c59f3010c7832fdefb03674986c4
        Access: 2021-04-20 13:29:17
        Modify: 2018-10-31 07:32:19
        Change: 2019-01-01 03:31:43
    
    [/usr/lib/systemd/systemd-udevd]
      FileType: ELF 64-bit LSB shared object
       FileMd5:97878ad86d499e55ab5584104ac799d6
        Access: 2021-04-20 13:29:20
        Modify: 2018-10-31 07:32:19
        Change: 2019-01-01 03:31:43
    
    [/usr/libexec/microcode_ctl/reload_microcode]
      FileType: ELF 64-bit LSB shared object
       FileMd5:930089e27b22fbb1e36563a0bd342cb6
        Access: 2021-04-20 15:49:28
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/libexec/ntpdate-wrapper]
      FileType: ELF 64-bit LSB shared object
       FileMd5:867930ba51a6ba8b1fc06916fcdf4293
        Access: 2021-04-20 13:29:18
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/libexec/openssh/sftp-server]
      FileType: ELF 64-bit LSB shared object
       FileMd5:e5ef049df4f2d4be1084f55e0ccb77ef
        Access: 2021-04-20 18:17:55
        Modify: 2018-04-11 12:21:32
        Change: 2019-01-01 03:32:28
    
    [/usr/libexec/postfix/aliasesdb]
      FileType: ELF 64-bit LSB shared object
       FileMd5:b90195593c9fe4915cd42246d815ceb7
        Access: 2021-04-20 13:29:18
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/libexec/postfix/chroot-update]
      FileType: ELF 64-bit LSB shared object
       FileMd5:f64dbc1e578d1082faa55aeb0b252a8a
        Access: 2021-04-20 13:29:18
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/libexec/postfix/master]
      FileType: ELF 64-bit LSB shared object
       FileMd5:4bae753076056214f799f5516415ef05
        Access: 2021-04-20 17:54:09
        Modify: 2018-10-31 00:50:33
        Change: 2019-01-01 03:32:31
    
    [/usr/libexec/postfix/pickup]
      FileType: ELF 64-bit LSB shared object
       FileMd5:7521399a48a4d991a4ff49f1ee5da049
        Access: 2021-04-20 09:07:25
        Modify: 2018-10-31 00:50:33
        Change: 2019-01-01 03:32:31
    
    [/usr/libexec/postfix/qmgr]
      FileType: ELF 64-bit LSB shared object
       FileMd5:bec9b7fee566144cc478af5a43a8b0e3
        Access: 2021-04-20 17:54:09
        Modify: 2018-10-31 00:50:33
        Change: 2019-01-01 03:32:31
    
    [/usr/libexec/selinux/selinux-policy-migrate-local-changes.sh]
      FileType: ELF 64-bit LSB shared object
       FileMd5:8260a0f8694aa5efe783df88a034b33c
        Access: 2021-04-20 15:49:28
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/local/phpstudy/system/phpstudyctl]
      FileType: ELF 64-bit LSB shared object
       FileMd5:063751bf2047a23dbdabe9e5e8f11f89
        Access: 2021-04-20 13:29:16
        Modify: 2020-07-10 13:15:38
        Change: 2020-07-15 14:52:45
    
    [/usr/sbin/NetworkManager]
      FileType: ELF 64-bit LSB shared object
       FileMd5:a4a26d90c729891c93cb7d98972043d6
        Access: 2021-04-20 13:29:17
        Modify: 2018-10-31 08:06:18
        Change: 2019-01-01 03:31:52
    
    [/usr/sbin/agetty]
      FileType: ELF 64-bit LSB shared object
       FileMd5:931daec7114ec6fec11cceb42d3b0f62
        Access: 2021-04-20 13:23:50
        Modify: 2018-10-31 06:48:52
        Change: 2019-01-01 03:31:40
    
    [/usr/sbin/crond]
      FileType: ELF 64-bit LSB shared object
       FileMd5:5d4af58369940cd6c60cbf0037e58b4d
        Access: 2021-04-20 13:29:17
        Modify: 2018-04-11 09:48:22
        Change: 2019-01-01 03:31:49
    
    [/usr/sbin/firewalld]
      FileType: ELF 64-bit LSB shared object
       FileMd5:7928bf617e49f041802634af42f028be
        Access: 2021-04-20 13:29:17
        Modify: 2018-10-31 06:47:00
        Change: 2019-01-01 03:32:14
    
    [/usr/sbin/ntpd]
      FileType: ELF 64-bit LSB shared object
       FileMd5:40c3a96a0efa63ab15ff8017bff34486
        Access: 2021-04-20 13:29:18
        Modify: 2018-04-13 20:52:34
        Change: 2019-02-22 15:55:14
    
    [/usr/sbin/rsyslogd]
      FileType: ELF 64-bit LSB shared object
       FileMd5:c1437d19669275a39ea5989dbd98a9d8
        Access: 2021-04-20 13:29:19
        Modify: 2018-10-31 07:08:28
        Change: 2019-01-01 03:32:36
    
    [/usr/sbin/sshd]
      FileType: ELF 64-bit LSB shared object
       FileMd5:56f6d9e73cfb3e36a0e321880589e830
        Access: 2021-04-20 10:28:57
        Modify: 2018-04-11 12:21:32
        Change: 2019-01-01 03:32:28
    
    [/usr/sbin/sshd-keygen]
      FileType: ELF 64-bit LSB shared object
       FileMd5:f4a3b884adab6a376e2d8580bb2e6136
        Access: 2021-04-20 15:49:28
        Modify: 2021-04-02 17:26:07
        Change: 2021-04-02 17:26:07
    
    [/usr/sbin/tuned]
      FileType: ELF 64-bit LSB shared object
       FileMd5:f6b7789e42c7628d0361eb48135a9b86
        Access: 2021-04-20 13:29:20
        Modify: 2018-07-05 03:23:21
        Change: 2019-01-01 03:32:23
    
    [/var/lock/subsys/local]
      FileType: ELF 64-bit LSB shared object
       FileMd5:d41d8cd98f00b204e9800998ecf8427e
        Access: 2021-04-20 19:30:05
        Modify: 2021-04-19 11:14:11
        Change: 2021-04-19 11:14:11
    
    [/var/lock/subsys/network]
      FileType: ELF 64-bit LSB shared object
       FileMd5:d41d8cd98f00b204e9800998ecf8427e
        Access: 2021-04-20 19:30:05
        Modify: 2021-04-19 11:14:10
        Change: 2021-04-19 11:14:10
    
    

## 7 windows入侵检查流程

详见投稿在正哥的安全分析与研究微信公众号：https://mp.weixin.qq.com/s/FchOO2lFaxNc4hdF0KPSIw

