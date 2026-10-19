## **概述**

近日深信服威胁情报研究团队捕获到Kaiji僵尸网络的最新变种。该病毒最早在2020年出现，使用多种危害较高的漏洞发起攻击，试图感染服务器和物联网设备，能够发起分布式拒绝服务（DDoS）攻击。与其他IoT僵尸网络不同的是，Kaiji并没有从其他（开源或黑市论坛获取）成熟的恶意软件家族中直接套用攻击代码。

Kaiji僵尸网络病毒在最新的版本中发生了非常大的改动，采用最新的Golang1.18版本进行病毒程序编写（老版本采用Golang1.15版本），大大增加了安全人员分析和调试该病毒的难度，同时也进一步证实了越来越多的病毒开发者使用Golang语言的趋势。

Kaiji僵尸网络相对老版本代码被重构，函数功能更加聚焦，函数名不再采用中式拼音命名。最新的版本驻留功能非常强大，增加了多种持久化手段，但是传播模块相对较弱，这里猜测一下，作者正在逐渐更新功能模块，该病毒很可能会随着时间的推移进一步变得更加复杂，未来Kaiji或许会成为一款强大的僵尸网络。

###  **Kaiji僵尸网络的整体攻击流程如下**

![](https://image.3001.net/images/20220709/1657341884_62c907bcc7e1c29a6b7ea.png!small)

  

##  **情报分析**

捕获的Kaiji僵尸网络主要使用多种高危RCE漏洞（GitLab未授权访问漏洞（CVE-2021-22205）和Atlassian Confluence
OGNL注入漏洞（CVE-2021-26084））利用作为初始攻击。一旦病毒入侵了服务器或物联网设备，Kaiji僵尸网络就可以在其团伙的指挥下发动DDoS攻击。

当前版本的Kaiji持久化模块非常强大，使用超过8种驻留手段进行持久化。Kaiji僵尸网络还会窃取本地SSH密钥，并进一步发起SSH爆破攻击以感染互联网上其他暴露的设备。

Kaiji运行后，若检测自身文件名为dir、find、ls、lsof、netstat、ps、ss之一，则会伪装执行相应命令，复制自身到/tmp/seeintlog后运行。随后会将自身复制到/etc/id.services.conf：

![](https://image.3001.net/images/20220709/1657341974_62c908161d8f99aaf64b2.png!small)

生成shell脚本/etc/32678（传播模块为32679），定时执行/etc/id.services.conf：

![](https://image.3001.net/images/20220709/1657342003_62c9083334bff1c4e8916.png!small)

/etc/id.services.conf运行后，会创建协程，执行main_Link、main_Watchdog、main_Initetc、main_addtime、main_Killcpu。

###  **通信模块[main_Link函数]**

通信模块执行时，与C2服务器103.138.80.90:1111、dark1998.f3322.org:8080、156.96.156.105:8080进行通信，发送上线信息后，由main_receive函数等待接收并执行ipbegin、ipend、finish、unload、shell、reverse、remarks、http、ipspoof、tcp、udp、syn、tap等命令，包含执行shell命令、卸载自身、发动DDoS攻击等功能。

![](https://image.3001.net/images/20220709/1657342027_62c9084baf004d7a86aa9.png!small)

 **传播模块[main_Sshboom函数]**

在老版本的Kaiji僵尸网络会窃取本地SSH密钥，进一步发起SSH爆破攻击，爆破成功后会下载执行相应CPU架构的驻留模块，例如：103.138.80.90:808/808/linux_amd64、linux_arm64、linux_mips。最新版本的Kaiji僵尸网络缺少传播模块功能，这里猜测作者正在逐一优化功能模块。

![](https://image.3001.net/images/20220709/1657342044_62c9085cdd8ee18e4b0b9.png!small)

 **持久化模块[main_Initetc函数]**

通过修改/etc/rc.local、/etc/rc.d/rc.local、/etc/init.d/boot.local文件实现自启动

![](https://image.3001.net/images/20220709/1657342059_62c9086b254da33f63c05.png!small)

利用chkconfig工具添加linux_kill服务，实现自启动

![](https://image.3001.net/images/20220709/1657342070_62c908761547bc4cfab5e.png!small)

注册linux.service

![](https://image.3001.net/images/20220709/1657342083_62c908834c40f40eb7d5a.png!small)

安装SELinux策略模块

![](https://image.3001.net/images/20220709/1657342094_62c9088ecc4bdcb412314.png!small)

修改/etc/profile.d/bash_config.sh复制自身到/usr/lib/libdlrpcld.so添加定时任务，每隔一分钟执行/.img

![](https://image.3001.net/images/20220709/1657342110_62c9089e32557b60a70a9.png!small)

替换dir、find、ls、lsof、netstat、ps、ss七个工具

![](https://image.3001.net/images/20220709/1657342123_62c908ab374d40a65a159.png!small)

尝试将自身进程名伪装为ksoftirqd/0

![](https://image.3001.net/images/20220709/1657342138_62c908ba04dcb11a0a561.png!small)

  

##  **小结**

Kaiji僵尸网络作者采用最新的Golang1.18版本重构，大幅更新持久化模块，整体复杂度也相比老版本明显增加。可以发现Kaiji正处于前中期发展的僵尸网络，未来作者可能在攻击模块和横向传播模块上进行更新迭代，从而导致Kaiji进一步变得复杂。

此外，鉴于Golang语言的跨平台等特点，近年来将其作为编程语言编码的恶意软件数量急剧增加，Kaiji僵尸网络也进一步证实了使用Golang语言开发恶意软件已成为一种趋势。

 **参考链接**

https://www.intezer.com/blog/research/kaiji-new-chinese-linux-malware-turning-to-golang/

