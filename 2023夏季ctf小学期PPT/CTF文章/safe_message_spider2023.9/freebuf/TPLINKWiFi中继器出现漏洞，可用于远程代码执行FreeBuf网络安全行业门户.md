***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **IBM公司X-Force研究员Grzegorz Wypych近日发布警告称，一些TP-Link的Wi-Fi中继器设备存在严重的远程代码执行漏洞，漏洞可导致外来攻击者获取设备权限并执行任意命令。**

 **![tp-link-wifi-extenders.jpg](https://image.3001.net/images/20190619/15609337774152.jpg!small)**

IBM安全部全球执行安全顾问Limor Kessem指出，
除了使被控设备变成僵尸网络的一部分外，攻击者还可以通过在设备连接的操作系统上执行任意的shell命令来进行恶意行为。黑客可以通过这个漏洞向所在系统进行横向提权，直到获得管理员权限。

## 关于漏洞CVE-2019-7406

Wi-Fi扩展器（也就是中继器）属于价格低廉，使用广泛的一种设备，常用于放大家庭或办公环境中的Wi-Fi信号，特别是那种覆盖多个楼层的无线网络。

这个漏洞的存在，使得攻击者不需要对设备进行身份验证或权限升级（所有进程都是root权限访问的），可直接远程执行命令。攻击者只需要向Wi-Fi中继器发送格式错误的HTTP
GET请求，就能够实现执行任意shell命令。具体技术细节，可以看[这里](https://securityintelligence.com/posts/critical-rce-vulnerability-in-tp-link-wi-fi-extenders-can-grant-attackers-remote-control/)。

![CVE-2019-7406-exploit-HTTP-GET.jpg](https://image.3001.net/images/20190619/15609337521033.jpg!small)

## TP-Link的Wi-Fi中继器

Wypych发现了TP-Link RE365版本中继器的漏洞，其固件版本为1.0.2，型号为20180213 Rel。TP-Link官方也确认了部分Wi-Fi中继器受到漏洞影响，型号包括RE650，RE350和RE500。

目前TP-Link已经修复了该漏洞，并为每个版本（RE365，RE650，RE350，RE500）提供了固件更新，建议用户及时更新。

***参考来源：[helpnetsecurity](https://www.helpnetsecurity.com/2019/06/18/vulnerable-tp-link-wi-fi-extenders/)，Karunesh91编译，转载请注明来自FreeBuf.COM**

