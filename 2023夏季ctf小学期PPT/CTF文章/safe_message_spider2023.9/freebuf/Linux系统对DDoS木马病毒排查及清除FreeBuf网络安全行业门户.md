# 导语

Unix.Trojan.DDoS_XOR-1是常见的linux系统DDoS木马病毒，系统感染病毒后，会受远程控制端控制，对外部IP发起主动连接并进行大流量DDoS攻击。

严重时，会导致系统CPU和公网IP出口带宽使用达到100%，通过ssh连接云主机会出现超时或中断问题，系统运行卡顿，无法正常使用。

通常建议用户备份好重要数据后重置系统，以彻底清除系统中的病毒。

# 清除病毒步骤

如果用户系统无法重置，可按照以下尝试清除病毒（由于不同类型病毒的感染和攻击方式不同。

本文所述方法仅供参考，不保证一定可以彻底清除病毒，最安全的方法还是重置系统为官方镜像）：

登录云主机（如ssh连接频繁中断，可通过VNC连接云主机），执行iftop命令，可以看到云主机对外发起大量高带宽主动连接（iftop命令使用方法请参考文档《Linux流量监控工具
- iftop》  
https://developer.jdcloud.com/article/1729?mid=12），如图：

![1683256997_645476a5530ecd88808be.png!small](https://image.3001.net/images/20230505/1683256997_645476a5530ecd88808be.png!small)

调整云主机绑定的安全组策略，删除所有出站规则，拒绝云主机主动发起的所有对外连接请求。

或者可以使用云主机系统自带防火墙进行拦截，以ubuntu系统为例（需安装ufw模块，如果未安装，执行apt-get install ufw -y安装）

先添加允许ssh连接的规则：ufw allow ssh

再添加拒绝到0.0.0.0/0的所有出站请求规则：ufw deny out to
0.0.0.0/0（由于该策略在允许ssh连接的规则之后添加，所以优先级低于先添加的规则，防火墙会先允许ssh连接，对于除ssh连接之外的连接予以拒绝）

执行ufw status确认防火墙规则，如图：

![1683257008_645476b0ded4b0b31ac83.png!small](https://image.3001.net/images/20230505/1683257008_645476b0ded4b0b31ac83.png!small)

执行iftop命令可以看到对外异常连接明显减少，如图：

![1683257018_645476ba9f768b56ce3c9.png!small](https://image.3001.net/images/20230505/1683257018_645476ba9f768b56ce3c9.png!small)

执行top命令查看系统资源使用情况，注意到有十位随机字母的进程占用CPU较高，如图：

![1683257030_645476c641c3839ec02e2.png!small](https://image.3001.net/images/20230505/1683257030_645476c641c3839ec02e2.png!small)

怀疑为病毒程序，使用kill -9 进程号杀掉进程，之后再次执行top命令，发现系统启动了新的十位随机字母进程，如图 ：

![1683257041_645476d1da657658e6cbe.png!small](https://image.3001.net/images/20230505/1683257041_645476d1da657658e6cbe.png!small)

按照文档（《Linux云主机安全入侵排查步骤》）定位启动异常进程的程序在/usr/bin目下，与进程同名的十位随机字母文件。删除文件后，会生成新的文件。

判断为病毒程序，且存在守护进程实时监测系统病毒文件和进程是否存在，如果不存在会再次创建病毒文件并启动进程。

因此我们需要定位守护进程和病毒源文件。

一般病毒都会通过编辑crontab使系统自动运行守护进程脚本，执行命令cat /etc/crontab，如图：

![1683257053_645476dde0078ad606ee8.png!small](https://image.3001.net/images/20230505/1683257053_645476dde0078ad606ee8.png!small)

注意到最后一行系统每隔3分钟自动运行/etc/cron.hourly/gcc.sh脚本  
执行命令cat /etc/cron.hourly/gcc.sh查看脚本内容，如图：

![1683257063_645476e780dab653fe8b4.png!small](https://image.3001.net/images/20230505/1683257063_645476e780dab653fe8b4.png!small)

图中蓝框部分将系统所有网卡全部启动，以防系统网卡关闭，病毒无法正常和外界通信

图中红框部分将/lib/libudev.so文件复制为/lib/libudev.so.6文件

图中黄框部分执行/lib/libudev.so.6文件

进入/lib目录，查看libudev.so文件表面上为库文件，使用file命令查看实际上是32位可执行文件，如图：

![1683257076_645476f46c6809360a2b6.png!small](https://image.3001.net/images/20230505/1683257076_645476f46c6809360a2b6.png!small)

按照文档（《Linux安全扫描工具ClamAV安装及使用 》：  
https://developer.jdcloud.com/article/1731）使用ClamAV扫描/lib目录和/usr/bin目录，结果显示libudev.so和十位随机字母文件为Unix.Trojan.DDoS_XOR-1类型木马病毒

推断该文件为病毒源文件，尝试将文件重命名为libudev.so.bak后，发现自动生成了新的libudev.so文件。如图所示，说明该文件有守护进程存在。

![1683257090_6454770210b448d0391af.png!small](https://image.3001.net/images/20230505/1683257090_6454770210b448d0391af.png!small)

执行命令echo "asdfasdf" >
libudev.so将libudev.so文件内容覆盖为asdfasdf，为防止守护进程再次修改文件，执行chattr +i
libudev.so命令锁定该文件，禁止修改，如图，可以看到文件内容已被覆盖。

![1683257101_6454770dea2f5bdd52f04.png!small](https://image.3001.net/images/20230505/1683257101_6454770dea2f5bdd52f04.png!small)

再次杀掉top命令中看到的异常进程，观察一段时间后不会再有新的进程启动

说明libudev.so程序已经无法正常运行

将之前ClamAV发现的/usr/bin目录下的病毒文件全部删除，观察一段时间，不再有新的文件生成

将/etc/crontab文件中的守护脚本内容删除，保存文件。

将/lib目录下的libudev.so文件删除，观察一段时间，不再有新的文件生成。

使用ClamAV工具对系统全盘扫描，没有发现病毒。

至此病毒清除完毕，可以关闭系统自带防火墙或删除禁止所有出站请求的规则或者调整安全组出站规则。

