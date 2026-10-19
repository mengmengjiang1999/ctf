## 背景概述

近日，深信服终端安全团队捕捉到“驱动人生”病毒的新变种，并通过云端的威胁情报系统监测到海内外已有大量终端被感染。“驱动人生”病毒自2018年出现，至今出现多个变种，不断进行技术优化以躲避安全软件的查杀监测。

该病毒利用永恒之蓝漏洞、SMBGhost漏洞等多种高危漏洞对Windows、Linux下的主机进行入侵感染，在入侵成功之后不仅会下载挖矿文件进行挖矿，还会释放传播模块继续入侵感染其他终端，并且病毒所使用的Powershell脚本经过多层混淆用以逃避安全软件的查杀。

## “驱动人生”病毒变种跟踪图

![](https://image.3001.net/images/20210924/1632464114_614d6cf29f9cb9cd6a097.png!small)

点击查看相关的分析文章

1.《[谨防“驱动人生”升级通道木马病毒恶意传播](https://mp.weixin.qq.com/s/D2gPdsplQFQcjq_pplg5xQ)》

2.《[警惕“驱动人生”木马最新变种袭击MSSQL数据库](https://mp.weixin.qq.com/s/u1IPZBLP6fEhOv2gfKCq9Q)》

3.《[借鸡生蛋！“驱动人生”挖矿木马使用Outlaw僵尸网络模块进行广泛传播](https://mp.weixin.qq.com/s/z6dge1WCUAru4ZaEpRd-Hg)》

根据威胁情报查询此次新变种利用的域名信息，创建时间于9月初，说明该变种刚开始传播不久。

![](https://image.3001.net/images/20210924/1632464230_614d6d6614caceb72063b.png!small)

## 病毒运行流程

![](https://image.3001.net/images/20210924/1632464253_614d6d7d9edf56df58e82.png!small)

## Windows

https://t[.]m7n0y.com/*.jsp 会卸载部分杀毒软件；

![](https://image.3001.net/images/20210924/1632464268_614d6d8ccd162a11ae80d.png!small)

在如下位置创建计划任务：

\\[随机字符串1]

\\[随机字符串1]\\[随机字符串2]

\Microsoft\Windows\\[随机字符串1]\\[随机字符串2]

![](https://image.3001.net/images/20210924/1632464284_614d6d9c3305be252c5d0.png!small)

如果WMI中没有检测到名为blsckbell的事件过滤器，则会创建多个随机名称的WMI过滤器和WMI消费者驻留项；![](https://image.3001.net/images/20210924/1632464315_614d6dbbe3d6c2e819f11.png!small)

计划任务和WMI中执行的代码内容主要为释放挖矿程序、if.bin和kr.bin模块；

![](https://image.3001.net/images/20210924/1632464328_614d6dc89fbb33e47680a.png!small)

病毒还会将
C:\Windows\System32\Windowspowershell\V1.0\[powershell.ex](http://powershell.ex/)e
重命名为随机字符，后续使用随机字符命名的powershell执行挖矿脚本等命令，给管理员编写脚本批量清除这些进程增加了难度

![](https://image.3001.net/images/20210924/1632464355_614d6de34550da689ca94.png!small)![](https://image.3001.net/images/20210924/1632464363_614d6deb0b23d9b95d8e1.png!small)  

### If.bin模块分析

If.bin 是传播模块，主要功能为暴力破解和漏洞利用，并然后在成功入侵其他主机后持续传播病毒。

1.内网IP收集：传播阶段需要获取目标IP列表，病毒默认扫描192.168.*.*、10.0.*.*、172.16.*.*
中的数个C段地址，并会通过ipconfig、GetHostByName、收集外网地址等方式扩充扫描IP地址段。

![](https://image.3001.net/images/20210924/1632464387_614d6e03900915ec2d7e5.png!small)

2.密码收集：病毒内置了部分常用的用户名和弱密码，列表如下图：

![](https://image.3001.net/images/20210924/1632464407_614d6e170286aa7c8e75e.png!small)

在实行暴力破解之前，还会使用 mimikatz 模块获取本机的密码，用以扩充现有的密码表，增加爆破成功概率（由此可见，不同主机使用相同密码危害有多大）

![](https://image.3001.net/images/20210924/1632464418_614d6e227cc60bbb1e223.png!small)

3.暴力破解和漏洞利用

针对的服务列表如下：

![](https://image.3001.net/images/20210924/1632464431_614d6e2f801592ab10f6b.png!small)

执行暴力破解前会检查65529端口，这是xmrig挖矿进程监听的端口，避免主机被重复感染。

![](https://image.3001.net/images/20210924/1632464441_614d6e39c68cab20d0bb6.png!small)

4.传播阶段

通过暴力破解、漏洞利用等方式成功获取到其他主机的权限之后，会直接尝试在主机中执行powershell或shell命令，从
https://t[.]m7n0y.com/*.jsp (Windows)或 https://t[.]m7n0y.com/ln/core.png
(Linux) 中下载并执行启动脚本，进行新一轮的感染。

![](https://image.3001.net/images/20210924/1632464458_614d6e4a08204cc54ab23.png!small)![](https://image.3001.net/images/20210924/1632464465_614d6e51f256ccad812b4.png!small)  

### Kr.bin模块分析

Kr模块循环不断地对失陷主机的进行监控，不仅可以关闭名单中的进程、服务、计划任务，还可以中断其他挖矿进程的连接，并封禁掉相应的ip。

停止并删除在名单中的服务、进程、计划任务：

![](https://image.3001.net/images/20210924/1632464480_614d6e602bc0e49803066.png!small)

隐藏任务管理器：

![](https://image.3001.net/images/20210924/1632464506_614d6e7a4169b3b15e834.png!small)

解禁自己的ip：

![](https://image.3001.net/images/20210924/1632464517_614d6e85015be74367113.png!small)

判断外部连接中是否存在挖矿连接，存在则停止相应进程并禁掉该ip：

![](https://image.3001.net/images/20210924/1632464525_614d6e8dd6710c485ad41.png!small)

获取自身挖矿进程的id，避免被杀掉：

![](https://image.3001.net/images/20210924/1632464539_614d6e9bda720fbdbff40.png!small)

## Linux

https://t[.]m7n0y.com/ln/core.png通过/etc/crontab文件写入计划任务，执行a.asp脚本；

![](https://image.3001.net/images/20210924/1632464553_614d6ea9a625acdc60c07.png!small)

a.asp脚本会关闭同行的挖矿进程；

![](https://image.3001.net/images/20210924/1632464564_614d6eb4b0211cbc37a3f.png!small)

下载挖矿文件xr至/.Xl1目录，并运行挖矿文件。

利用ssh横向传播

![](https://image.3001.net/images/20210924/1632464576_614d6ec075559df55ea4c.png!small)

封禁除自己以外的挖矿ip

![](https://image.3001.net/images/20210924/1632464588_614d6eccdf4be07611eb4.png!small)

获取矿机ip、版本、算力等信息，并返回给后台。

![](https://image.3001.net/images/20210924/1632464597_614d6ed59811b8adfcb6f.png!small)

## IOC

t.m7n0y.com

d.bb3u9.com

t.jdjdcjq.top

t.qq7u0.com

t.phu7t.com

d.u78wjdu.com

p.jue82h.com

