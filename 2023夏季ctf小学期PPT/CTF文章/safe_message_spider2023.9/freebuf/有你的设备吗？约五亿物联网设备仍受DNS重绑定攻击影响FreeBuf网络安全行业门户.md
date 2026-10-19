**网络安全公司Aemis在去年发现蓝牙协议漏洞“[BlueBorne](https://www.bleepingcomputer.com/news/security/blueborne-vulnerabilities-impact-over-5-billion-bluetooth-enabled-devices/)”之后，于近日再次发出警告，称大约五亿的智能设备如今仍受DNS重绑定这种老式攻击的影响。**  

**![IoT.png](https://image.3001.net/images/20180723/15323182808661.png!small)**

受近期关于[暴雪app](https://www.bleepingcomputer.com/news/security/blizzard-fixes-dns-rebinding-flaw-that-put-all-the-companys-users-at-risk/)，[uTorrent](https://www.bleepingcomputer.com/news/security/utorrent-client-affected-by-some-pretty-severe-security-flaws/)， [Google
Home](https://www.bleepingcomputer.com/news/security/google-roku-sonos-to-fix-dns-rebinding-attack-vector/)，[Roku
TV](https://www.bleepingcomputer.com/news/security/google-roku-sonos-to-fix-dns-rebinding-attack-vector/)以及[Sonos](https://www.bleepingcomputer.com/news/security/google-roku-sonos-to-fix-dns-rebinding-attack-vector/)设备中DNS重绑定漏洞报道的刺激，Aemis公司最近分析了此类攻击对物联网设备的影响。那么，什么是DNS重绑定攻击呢？

DNS重绑定攻击是指攻击者欺骗用户的设备或浏览器来绑定到一个恶意的DNS服务器，从而使设备访问非预期的域名。DNS重绑定攻击通常用于入侵设备，然后将其作为中继设备访问内部网络。一个典型的DNS重绑定攻击会经历如下阶段：

> 1.攻击者为恶意域名搭建自定义DNS服务器
>
> 2.攻击者通过网络钓鱼，垃圾邮件，XSS或者是合法网站上的广告链接欺骗受害者访问恶意域名
>
> 3.用户浏览器会查询该域名的DNS设置
>
> 4.恶意DNS服务器响应，之后浏览器将缓存类似于XX.XX.XX.XX这样的地址
>
> 5.由于攻击者已经将初始响应中的DNS
> TTL设置为1秒，一秒后，用户浏览器会对同一个域名发出另一个DNS请求，因为之前的入口已经过期，所以恶意域名需要一个新的IP地址。
>
> 6.攻击者的恶意DNS设置会响应一个恶意IP地址，如YY.YY.YY.YY，该地址通常为设备的内部网络地址。
>
> 7.攻击者为了各种目的（数据收集，发起恶意攻击等）反复使用恶意DNS服务器访问内部网络的更多IP地址。

##  **视频演示：**

## 受影响范围广，几乎覆盖所有类型设备

Armis公司表示，物联网以及其他智能设备正是攻击者通过DNS重绑定漏洞进行攻击的完美目标，主要由于其在企业网络中分布较广，在情报收集和数据窃取方面可以发挥惊人的作用。

有专家称，结果他们的调查，他们发现几乎所有类型的智能设备都容易受到DNS重绑定攻击的影响，从智能电视到路由器，从打印机到监控摄像头，从手机到智能助手...

总而言之，据专家估计，存在漏洞的设备数量当以亿计，估计量约为五亿。

![Armis_DNS_rebinding.png](https://image.3001.net/images/20180723/15323182597799.png!small)

## 补丁修复希望渺茫

然而针对DNS重绑定攻击来修补这些设备的漏洞几乎是一项永远无法完成的大任务，来自供应商的这些补丁首先需要解决XSS和CSRF这些琐碎漏洞，所以更不用说DNS重绑定这类复杂攻击。但Armis公司的专家表示，相比于查看和审核新设备以取代旧设备，将物联网设备集成到当前的网络安全监控产品中可能是最简单且最具成本效益的解决方案。

由于物联网安全在过去一年中一直是一个热门的话题，因此网络安全市场已经做出反应和调整，现在有许多网络安全公司正在为想要避免意外的企业提供监控物联网设备的专用平台。什么意外？例如最近，俄罗斯PIR银行发现黑客通过[老旧路由器](https://www.bleepingcomputer.com/news/security/hackers-breach-russian-bank-and-steal-1-million-due-to-outdated-router/)而入侵了网络，之后偷走了100万美元，耸人听闻。

总之，现在已经不再是2000年了，无论什么公司都必须更新其威胁模型以考虑物联网设备的安全性，无论它们是否易受DNS重绑定攻击或任何其他缺陷的影响。

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/half-a-billion-iot-devices-vulnerable-to-dns-rebinding-attacks/)，FB小编Covfefe编译，转载请注明来自FreeBuf.COM**

