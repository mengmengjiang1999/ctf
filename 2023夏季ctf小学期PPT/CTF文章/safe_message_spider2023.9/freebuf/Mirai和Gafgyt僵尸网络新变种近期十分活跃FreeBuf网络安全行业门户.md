**安全专家警告称，广大用户近期应该小心[Mirai](https://securityaffairs.co/wordpress/50929/cyber-crime/linux-mirai-elf.html)和[Gafgyt](https://securityaffairs.co/wordpress/45820/cyber-crime/linux-remaiten-iot-botnet.html)僵尸网络了，因为这两个臭名昭著的物联网僵尸网络又开始活跃了起来。**

![1.png](https://image.3001.net/images/20180726/15325701493248.png!small)

安全专家通过研究发现，Mirai和Gafgyt这两个僵尸网络近期十分活跃，不排除攻击者计划进行新一轮大规模网络攻击的可能性。由于Mirai僵尸网络的源代码此前已泄露在网络上，紧跟着的就是各种Mirai变种开始泛滥于“江湖”。仅在2018年，就已经出现了类似[Satori](https://securityaffairs.co/wordpress/73599/cyber-crime/satori-botnet-resurrection.html)、[Masuta](https://securityaffairs.co/wordpress/68153/cyber-crime/masuta-botnet.html)、[WickedMirai](https://securityaffairs.co/wordpress/72640/cyber-crime/wicked-mirai.html)、
[JenX](https://securityaffairs.co/wordpress/68610/cyber-crime/jenx-botnet.html)、Omni和[OMG](https://securityaffairs.co/wordpress/69449/cyber-crime/omg-botnet.html)等多款Mirai僵尸网络变种。

Gafgyt僵尸网络，又名[Bashlite](https://securityaffairs.co/wordpress/50824/malware/bashlite-botnets.html)或[Lizkebab](https://securityaffairs.co/wordpress/52845/cyber-crime/linuxirctelnet-malware.html)，该僵尸网络首次出现于2014年，其源代码泄露于2015年初。根据Flashpoint的研究报告我们可以看到，在2016年9月份，全球范围内已发现的感染了Bashlite恶意软件的设备数量就高达数百万台。

PaloAltoNetwork在其发布的分析报告中指出：“截止至2018年5月底，网络上已经出现了三款基于Mirai和Gafgyt恶意软件家族的恶意软件变种源码了，这些恶意软件变种的源代码被直接公布在了互联网中，任何人都可以随意获取并基于它们进行自定义开发，其中的漏洞利用代码涉及到了多个能够影响物联网设备安全性的已知漏洞。根据我们对恶意软件变种样本的分析，我们发现一个简单的恶意软件变种就能够一次性利用多达11个安全漏洞来实施攻击。与之相比，就连臭名昭著的
IoTReaper恶意软件（该恶意软件同样借鉴了Mirai的源代码，但是它还集成了LUA环境，并自带有九套漏洞利用代码）都“黯然失色”了。”

这两款僵尸网络变种的最新版本能够利用D-Link DSL-2750B设备的OS命令注入漏洞，并且还集成了多个最新的Metasploit模块。

安全专家表示，这两个僵尸网络活动近期突然变得非常活跃，他们推测这两者之间可能会有某种关联，很可能是同一攻击组织所为。

研究人员所发现的第一个恶意活动与Omni僵尸网络（Mirai恶意软件的最新变种之一）有关。Omni僵尸网络可利用的安全漏洞范围非常广，例如DasanGPON路由器的漏洞CVE-2018-10561和CVE-2018-1562，华为路由器的漏洞CVE-2017–17215，D-Link设备的两个命令执行漏洞，Vacron
NVR设备的相关安全漏洞，JAWS Web服务器的命令执行漏洞，以及超过70家厂商的CCTV和DVR设备漏洞等等。

PaloAlto的研究人员表示，所有的这些漏洞都是已知漏洞，并且已经有很多僵尸网络正在利用这些漏洞实施攻击，但这也是第一次有Mirai变种一次性利用这十一个漏洞来实施攻击。

最后一个Mirai变种使用了IP地址213[.]183.53.120来托管Payload，并将其作为命令控制服务器，而某些Gafgyt样本同样也使用的是这个IP地址。

研究人员所观察到的第二个恶意活动使用的是跟之前相同的漏洞利用机制，但它还会额外进行凭证爆破攻击。研究人员根据该活动所使用的Shell脚本以及相关代码名称，将该活动命名为了Okane。

研究人员表示，跟之前的恶意活动不同的是，这些样本还会进行凭证暴力破解攻击，而爆破列表中也有一些不常见的条目，比如说：

> root/t0talc0ntr0l4!– Control4设备的默认凭证
>
> admin/adc123– ADCFlexWave Prism设备的默认凭证
>
> mg3500/merlin– Camtron IP 摄像头设备的默认凭证

该活动中的某些样本还在Mirai源码中添加了两个额外的DDoS功能。

![2.png](https://image.3001.net/images/20180726/15325701649218.png!small)

除了上述两个恶意活动之外，PaloAlto
Networks的研究人员还发现了第三个僵尸网络活动，名为Hakai，该僵尸网络会尝试利用之前介绍的漏洞利用代码来让目标设备感染Gafgyt恶意软件。

PaloAltoNetworks指出，这一波新的网络攻击活动证明了攻击者构建大型僵尸网络的能力正在变得越来越强，随着各种僵尸网络变种源码泄露在互联网上，之后还会出现更多不同类型且破坏力更强的僵尸网络攻击。除此之外，各大厂商也应该提升漏洞补丁的开发效率，尽可能地保护用户的终端及数据安全。

 ***参考来源：securityaffairs，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

