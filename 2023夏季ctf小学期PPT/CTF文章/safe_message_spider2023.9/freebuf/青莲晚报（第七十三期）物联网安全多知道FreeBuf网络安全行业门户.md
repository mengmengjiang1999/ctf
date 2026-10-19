![73.jpg](https://image.3001.net/images/20200424/1587696651_5ea2540b54145.jpg!small)  

**到2024年，物联网连接总数将达到830亿**

 **  
**

根据[Juniper Research的数据](https://www.helpnetsecurity.com/tag/juniper-research/)，到2020年，[物联网连接](https://www.helpnetsecurity.com/2020/03/30/secure-iot-connections/)的总数将从2020年的350亿增加到830亿。该研究发现，到2024年，包括制造业，零售业和农业在内的工业部门将占所有IoT连接的70％以上。预计具有成本效益的专用蜂窝网络的出现将成为未来一个增长的主要驱动力。
4年后，随着技术成本在未来2年内下降，预计近期对专用LTE网络的需求增长将延续到[5G](https://www.helpnetsecurity.com/2020/03/05/devices-5g-networks/)专用[网络](https://www.helpnetsecurity.com/2020/03/05/devices-5g-networks/)。

该研究预测，在未来四年中，服务中的工业物联网单位数量将增长180％。研究合著者Sam Barker指出：“
随着工业IoT用户采用新技术来扩展其网络上可用的服务，[工业网络](https://www.helpnetsecurity.com/2019/06/21/standards-based-licensed-wireless-networks/)将需要快速扩展。但是，[物联网平台](https://geekflare.com/iot-platform-tools/)必须确保安全流程可以随着网络的增长而扩展。”

私有物联网网络日益复杂，这意味着平台必须实施步骤以在[物联网生态系统的](https://www.helpnetsecurity.com/2019/11/05/iot-security/)所有层（包括设备，连接性和平台本身）中最大化安全性。

详文阅读：

<https://www.helpnetsecurity.com/2020/04/02/total-iot-connections/>

**黑客劫持路由器 DNS：以 COVID-19 之名重定向至恶意网站**

  

根据安全公司Bitdefender研究人员本周三发布的博文，发现了通过DNS劫持将用户重定向到新冠病毒（COVID-19）信息APP的下载页面。用户访问页面之后并不会下载任何APP文件，会直接被恶意程序感染，并会获取诸如加密钱包凭证和其他私人敏感信息。

Bitdefender研究人员表示，黑客向存在漏洞的路由器发起攻击，并使用暴力破解的方式来猜测控制面板的密码。（这并不难做到，因为很多用户的帐号凭证均为默认设置，为admin和password）。一旦攻击者获得了路由器的控制权限，更改DNS设置就变得非常简单。

详文阅读：

<http://hackernews.cc/archives/29803>

**D-Link DSL-2640B** **设备多个最新漏洞利用分析**

 **  
**

[D-Link
DSL-2640B](https://eu.dlink.com/uk/en/products/dsl-2640b-adsl-2-wireless-g-router-with-4-port-10-100-switch)
DSL网关中发现了几个漏洞，由于设备是EoL状态，因此这些漏洞可能不会被打补丁。在EoL设备中发现的漏洞通常具有无限寿命，尽管[Shodan](https://www.shodan.io/)仅扫描出两个设备，但不应忽略这些漏洞的影响。

[DNSChanger](https://en.*********.org/wiki/DNSChanger)恶意软件2018年将目标设备定为DSL-2640B。[Bad
Packets](https://badpackets.net/)分析发现，设备数量很大，超过了14,000个设备。

对于EoL超过7年的设备，设备总体规模可能令人惊讶，控制如此大的设备数量可进行大规模攻击，例如在DDoS攻击中贡献大量带宽。

详文阅读：

<https://www.4hou.com/posts/kOJ5>

**利用Safari浏览器的7个0-day漏洞利用链劫持相机**

 **  
**

当你在一个网站上看到一条消息有人劫持了你的相机和麦克风在监视你，这正是这一串漏洞可以做到的。

当在Desktop Safari（Mac）或Mobile Safari（iPhone或iPad）上查看时，此漏洞允许恶意网站伪装成受信任的网站。

然后，黑客可以使用其身份获取用户的隐私，之所以可行，是因为Apple允许用户在每个网站上永久保存其安全设置。

如果恶意网站想要访问摄像机，那么它所要做的就是伪装成可信任的视频会议网站，例如Skype或Zoom（Zoom刚爆出一堆漏洞，哈哈哈哈哈）。

我的研究发现了Safari中的七个0-day漏洞（CVE-2020-3852，CVE-2020-3864，CVE-2020-3865，CVE-2020-3885，CVE-2020-3887，CVE-2020-9784和CVE-2020-9787），其中三个用于构造利用链劫持访问相机。

详文阅读：

<https://www.4hou.com/posts/DJMx>

**TP-Link Archer A7** **命令注入漏洞分析**

 **  
**

有研究人员使用了TP-Link Archer A7中的一个命令注入漏洞，本文介绍了该漏洞的具体细节。

该漏洞位于tdpServer（/usr/bin/tdpServer）守护进程中，这是运行在TP-Link Archer
A7（AC1750）路由器上的一个进程，这款设备的硬件版本号为5，采用MIPS架构，固件版本为190726。攻击者必须处于路由器的LAN网络中才能利用该漏洞，但利用过程不需要经过身份认证。漏洞利用成功后，攻击者可以以root权限执行任意命令，包括下载和执行二进制程序。该漏洞对应的编号为CVE-2020-10882，TP-Link官方发布了[A7(US)_V5_200220](https://www.tp-link.com/us/support/download/archer-a7/)版固件，修复了该漏洞。

详文阅读：

<https://www.anquanke.com/post/id/202671>

  

