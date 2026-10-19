**Fortinet的安全专家发现了一种新的变体Mirai僵尸网络，称为“Wicked Mirai”，它包括新的漏洞同时传播一个新的僵尸程序。**

**![Mirai.jpg](https://image.3001.net/images/20180521/15268886534508.jpg!small)**

Wicked
Mirai这个名字来自代码中的字符串，专家发现，与原始版本相比，这个新变种至少包含三个新的漏洞。由于两年前公布了源代码，FortiGuard实验室的团队看到了越来越多的Mirai变体。

“一些做了重大的修改，例如增加了将受感染的设备变成恶意软件代理 和 密码器群的 功能。其他人则将Mirai代码与多种针对已知和未知漏洞的漏洞整合在一起
，类似于最近由FortiGuard实验室发现的新变种，我们现在称其为WICKED。”

![resize=902%2C121&ssl=1.jpg](https://image.3001.net/images/20180521/15268706534153.jpg!small)

Mirai 僵尸网络[第一次发现](https://securityaffairs.co/wordpress/50929/cyber-crime/linux-mirai-elf.html)2016年，MalwareMustdie的专家们用它在野外发动了大规模的DDoS攻击。Mirai的源代码是2016年10月在网上泄露，很快便出现了许多其他变体，包括
[Satori](https://securityaffairs.co/wordpress/67040/hacking/satori-botnet-mirai-variant.html),
[Masuta](https://securityaffairs.co/wordpress/68153/cyber-crime/masuta-botnet.html)，和[Okiru](https://securityaffairs.co/wordpress/67742/cyber-crime/mirai-okiru-botnet.html)。

据Fortinet说，“Wicked
Mirai”的作者和其他变体很可能是同一个人。Mirai僵尸网络通常由三个主要模块组成：攻击、杀手和扫描仪。Fortinet将其分析集中在负责传播恶意软件的Scaner模块上。

最初的Mirai试图强行破坏其他IOT设备，而Wicked Mirai使用已知的漏洞。Wicked
Mirai将通过启动物联网设备的原始套接字SYN连接扫描端口8080、8443、80和81。一旦建立了连接，僵尸程序将尝试利用该设备并通过将攻击字符串写入套接字来下载攻击载荷。

专家们发现，要使用的漏洞取决于僵尸程序能够连接到的特定端口。在Wicked Mirai的目标设备列表下面：

> 8080端口：[NETGEAR DGN1000](https://www.exploit-db.com/exploits/43055/)和DGN2200
> v1路由器(也被死神僵尸网络使用) **)**
>
> 81 端口：CCTV-DVR远程代码执行
>
> 8443端口：NETGEAR R7000和R6400命令注入([CVE-2016-6277](https://www.exploit-> db.com/exploits/41598/))
>
> 80端口：受威胁的Web服务器中的调用程序外壳

对代码的分析揭示了String
SoraLOADER的存在，这表明它可能试图分发Sora僵尸网络。进一步的调查让研究人员反驳了这一假设，并证实机器人实际上会连接到恶意域名下载OwariMirai机器人。

成功利用该漏洞后，此僵尸程序将从恶意站点下载其有效负载。这种情况下，
hxxp://185[.]246[.]152[.]173/exploit/owari.{extension}。这使得它很明显地想要下载另一个Mirai变体Owari
bot，而不是先前暗示的那个。

然而，在分析时，在网站目录中找不到Owari bot样本。在另一轮事件中，它们被下面所示的示例所取代，这些样本后来被发现是Omni bot。

对该网站 /bins
目录的分析显示了其他Omni样本，这些样本显然是使用GPON提供的[漏洞CVE-2018-10561](https://securityaffairs.co/wordpress/72269/hacking/gpon-home-routers.html)。

![resize=561%2C613&ssl=1.jpg](https://image.3001.net/images/20180521/15268708224932.jpg!small)

[](https://i0.wp.com/securityaffairs.co/wordpress/wp-content/uploads/2018/05/Wicked-Mirai-2.png?ssl=1)

Fortinet的安全研究人员在寻找Wicked，Sora，Owari和Omni之间的联系时，发现了一个对Owari/Sora
IoT的僵尸网络作者的[采访](https://blog.newskysecurity.com/understanding-the-iot-hacker-a-conversation-with-owari-sora-iot-botnet-author-117feff56863)。

采访中透露，作者抛弃了Sora 和Owari的僵尸程序，他目前正在从事Omni项目。

“根据作者在上述访谈中就同一主机上的不同僵尸网络所作的陈述，我们可以从根本上确认僵尸网络Wicked、Sora、Owari和Omni
的作者是同一个人。这也使我们得出结论，虽然Wicked bot
最初是为了交付Sora僵尸网络，但后来它被重新用于为作者的后续项目服务，”Fortinet总结道。

***参考来源：[SecurityAffairs](https://securityaffairs.co/wordpress/72640/malware/wicked-mirai.html)，由Andy编译，转载请注明来自FreeBuf.COM**

