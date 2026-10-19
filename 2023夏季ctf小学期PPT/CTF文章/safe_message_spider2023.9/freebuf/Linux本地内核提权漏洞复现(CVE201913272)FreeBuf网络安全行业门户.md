# 0x00简介

在5.1.17之前的Linux内核中，kernel /
ptrace.c中的ptrace_link错误地处理了想要创建ptrace关系的进程的凭据记录，这允许本地用户通过利用父子的某些方案来获取root访问权限
进程关系，父进程删除权限并调用execve可能允许攻击者控制。

#  **0x01漏洞概述**

Linux执行PTRACE_TRACEME函数时，ptrace_link函数将获得对父进程凭据的RCU引用，然后将该指针指向get_cred函数，但是，对象struct
cred的生存周期规则不允许无条件的将RCU引用转换为稳定引用。PTRACE_TRACEME获取父进程的凭证，使其能够像父进程一样执行父进程能够执行的各种操作，如果恶意低权限子进程使用PTRACE_TRACEME并且该子进程的父进程具有高权限，子进程可获取其父进程的控制权并且使用其父进程的权限调用execve函数创建一个新的高权限进程。

注：该漏洞利用前提:需要目标服务器有桌面环境，所以较为鸡肋的漏洞

#  **0x02影响范围**

内核<5.1.17

#  **0x03环境搭建**

环境：ubuntu18.04版本

下载地址：http://mirrors.aliyun.com/ubuntu-releases/16.04/

![](https://image.3001.net/images/20210119/1611027705_600654f9a6cc4c33ff0bd.jpg!small)

1.下载完成后使用VMware虚拟机安装，安装时版本选择Ubuntu 64位的

![](https://image.3001.net/images/20210119/1611027716_60065504899b98a46d254.jpg!small)

2.镜像文件选择下载的ubuntu16版本的镜像安装开启虚拟机即可，详细安装方法自行百度

![](https://image.3001.net/images/20210119/1611027726_6006550ed60272df2ee7b.jpg!small)

3.安装完成后重启即可

![](https://image.3001.net/images/20210119/1611027733_60065515e4b4860ef6909.jpg!small)

#  **0x04漏洞复现**

1.在Ubuntu上创建一个低权限用户test并设置密码

useradd -d /home/test -m test

passwd test

![](https://image.3001.net/images/20210119/1611027742_6006551e0f72a8f388e8b.jpg!small)

2.然后切换到test用户,查看系统内核版本是否小于5.1.17,并当前用户和当前用户的UID

![](https://image.3001.net/images/20210119/1611027750_60065526e0e64827da1fd.jpg!small)

3.切换到tmp目录使用git或wget下载漏洞poc

git clone https://github.com/bcoles/kernel-exploits.git

![](https://image.3001.net/images/20210119/1611027760_600655308f0bed18e813a.jpg!small)

4.下载完成后进入CVE-2019-13272目录下，编译poc

gcc poc.c -o exp

![](https://image.3001.net/images/20210119/1611027771_6006553b2312903c13957.jpg!small)

5.然后执行exp,提权成功

![](https://image.3001.net/images/20210119/1611027779_6006554381e63827e1f6f.jpg!small)

 **总结**

1.此漏洞危害性比较大，但漏洞的限制也非常的大，需要是linux桌面freedestop上的验证程序，就是说非桌面版本此提权方法没用，要用它只能在本地使用，使用ssh连接也不行。

2.以下为作者以实验成功的版本

![](https://image.3001.net/images/20210119/1611027786_6006554ae15d44d96e40f.jpg!small)

#  **0x05修复建议**

1.建议升级linux内核版本至5.2或更高

参考链接：https://github.com/bcoles/kernel-exploits/tree/master/CVE-2019-13272

在这里，给大家介绍一下“东塔攻防世界靶场”

2020年12月，东塔攻防世界靶场正式对外提供注册，各位小伙伴可通过注册后进行体验。新注册用户可获得一定的积分，对于靶场使用获取正确的Key后，也可以获取一定的经验值，经验值根据排名会不定期给予一定的奖励。

并且，在操作过程中，针对出现的Bug和安全漏洞问题可以和塔塔子提出，审核通过后可以获得相应的奖励积分。

东塔攻防世界网站不定时推出可免费限时使用的靶场，具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服了解详情。

东塔攻防世界靶场主要分为在线靶场和职业体系两大特色板块。且平台内的靶场会定期更新内容，尤其是最新漏洞复现的一些文章和靶场，会优先在靶场中提供环境让大家体验。

东塔攻防世界网站会不定期限时免费推出最新的一些复现的靶场，以供学习交流，给了大家充分体验和使用靶场的机会。

具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服wx（dongtakefu）了解详情。

除了以上介绍的内容，还有更多宝藏区域，更强大的功能，等你来寻宝！

详戳下方“东塔攻防世界靶场”网址，Get一波新世界

https://labs.do-ta.com

