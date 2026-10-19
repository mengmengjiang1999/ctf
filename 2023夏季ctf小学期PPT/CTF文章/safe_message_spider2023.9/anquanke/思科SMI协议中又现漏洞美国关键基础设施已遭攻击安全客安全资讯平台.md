# 思科 SMI 协议中又现漏洞 美国关键基础设施已遭攻击

阅读量 **143399**

|评论 **3**

发布时间 : 2018-04-08 15:00:19

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Catalin Cimpanu;Lawrence Abrams

原文地址：<https://www.bleepingcomputer.com/news/security/cyber-attacks-on-us-critical-infrastructure-linked-to-cisco-switch-flaw/
https://www.bleepingcomputer.com/news/security/iranian-and-russian-networks-attacked-using-ciscos-cve-2018-0171-vulnerability/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0116500746ca25026d.jpg)

**4** **月** **5** **日，思科** **Talos** **团队指出黑客正在滥用配置不当的思科交换机获取对全球各地组织机构的入口点。**

思科 Talos 团队表示，其中一些入侵尝试和美国国土安全局于今年3月中旬发布的一份警告信息相关。US-CERT
在安全公告中曾警告称，“俄罗斯国家网络行动者”针对并渗透进美国能源网和其它基础设施网络发动攻击。

思科 Talos 团队认为，针对思科交换机的某些攻击是由 US-CERT 安全公告中说明的同一个组织执行的，该组织被指为“蜻蜓
(Dragonfly)”或称为“蹲伏的雪人(Crouching Yeti)”或“能量熊 (Energetic Bear)”。

## 攻击和思科 SMI 协议相关

这些遭“蜻蜓”黑客组织以及其它组织实施的攻击针对的是 Cisco Smart Install (SMI)
客户端，后者是一款老旧工具，旨在让思科交换机实现无触摸式安装，如今已被“思科网络即插即用 (Cisco Network Plug and
Play)”解决方案所取代。

产生缺陷的原因是，这些交换机的所有人未配置或禁用 Smart Install 协议，而SMI
客户端仍然在后台等待“安装/配置”命令，从而导致黑客利用这个被忘记的协议（1）修改 TFTP 服务器设置通过 TFTP
协议渗透配置文件；（2）修改交换机通用配置文件；（3）更换 IOS 操作系统镜像；（4）设置本地账户让攻击者登录并执行任意 IOS 命令。

## 在网上扫描到逾16.8万台启用 SMI 的思科设备

思科在2017年2月检测到滥用 SMI 协议的情况，当时它曾对客户发出警报信息；今年2月份，该团队又发出另一份警告信息。

对启用 SMI 设备（端口4786）的扫描工作始于2017年2月，扫描到的设备数量并在10月明显增多，而在今年2月份思科发出最新警告后数量翻了一番。

思科表示网上暴露了超过16.8万台启用 SMI 的思科交换机。Talos 团队不久前不仅发布操作指南供网络管理员禁用受感染设备上的
SMI，而其还发布了一款[开源工具](https://github.com/Cisco-Talos/smi_check)供扫描其它启用 SMI
设备的本地网络或互联网 IP 地址范围之用。

思科表示，这个“错误配置”问题和最近由 Embedi 研究人员在同样协议中发现的一个远程代码执行缺陷之间并不存在关联。尽管如此，如果管理员选择在设备上启用
SMI 协议，则应该将交换机的操作系统更新至包含该漏洞修复方案的版本。

## 思科 CVE-2018-0171 漏洞已遭大规模利用

4月6日，黑客组织 “JHT” 攻击了包括俄罗斯和伊朗网络在内的大规模网络基础设施，它利用的是思科 CVE-2018-0171 Smart Install
漏洞。黑客利用这个漏洞能将路由器重置为默认配置并向受害者展示信息。

易遭攻击的思科路由器遭 CVE-2018-0171 攻击后，路由器的配置文件即 “startup-config”
被覆写而路由器遭重启。这不仅导致受影响网络中断，而且管理员还发现路由器的 startup-config
文件被更改为一条内容是“不要干扰我们的大选…….-JHT
[usafreedom_jht@tutanota.com](mailto:usafreedom_jht@tutanota.com)”。

路透社报道称，伊朗通信和信息技术部表示，全球超过20万台路由器受影响，其中3500台位于伊朗。伊朗通信和信息技术部部长 Mohammad Javad
Azari-Jahromi 在推特上指出，截止到美国东部时间4月6日下午4:12，伊朗95% 的受影响路由器已恢复正常服务。

攻击者告知媒体 Motherboard 称扫描了多个国家的易受攻击系统，不过仅攻击了俄罗斯或伊朗的路由器。他们还声称通过发布 no vstack
命令修复了所发现的美国和英国路由器上的这个漏洞。

4月7日下午5点，CNCERT旗下CNVD漏洞平台[紧急发布安全公告](http://www.cnvd.org.cn/flaw/show/CNVD-2018-06774)，对思科Smart
Install远程命令执行漏洞进行预警。

本文翻译自 [原文链接](https://www.bleepingcomputer.com/news/security/cyber-attacks-on-us-critical-infrastructure-linked-to-cisco-switch-flaw/
https://www.bleepingcomputer.com/news/security/iranian-and-russian-networks-attacked-using-ciscos-cve-2018-0171-vulnerability/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信代码卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/103824](/post/id/103824)

安全客 - 有思想的安全新媒体

本文转载自: [](https://www.bleepingcomputer.com/news/security/cyber-attacks-on-us-critical-infrastructure-linked-to-cisco-switch-flaw/
https://www.bleepingcomputer.com/news/security/iranian-and-russian-networks-attacked-using-ciscos-cve-2018-0171-vulnerability/)

如若转载,请注明出处： <https://www.bleepingcomputer.com/news/security/cyber-attacks-on-us-critical-infrastructure-linked-to-cisco-switch-flaw/
https://www.bleepingcomputer.com/news/security/iranian-and-russian-networks-attacked-using-ciscos-cve-2018-0171-vulnerability/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [思科](/tag/思科)
  * [CVE-2018-0171](/tag/CVE-2018-0171)
  * [思科 SMI 协议](/tag/思科 SMI 协议)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t015a32ce3696fa7636.png) 奇安信代码卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

