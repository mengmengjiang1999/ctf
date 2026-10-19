# 【漏洞预警】CVE-2016-8610: “SSL Death Alert“漏洞公告

阅读量 **294444**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-10-25 11:16:26

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

来自Qihoo 360 Gear
Team的安全研究员石磊（360信息安全部）发现OpenSSL中存在一个影响广泛的远程匿名拒绝服务漏洞，该漏洞被命名为“SSL Death Alert”
(即“OpenSSL红色警戒”漏洞)，通用漏洞编号CVE-2016-8610。

目前已确认该漏洞影响到互联网广泛提供HTTPS(包括SSL和TLS协议)服务的Nginx，OpenSSL官方已经于2016-09-22完成源码层面的修复，建议立即跟进修复！

**  
**

**什么是OpenSSL？**

OpenSSL
是一个开源的安全套接字层实现库，包括常见的密码算法（RSA、AES、DES等）、常用的密钥和证书封装管理功能及SSL协议，并提供丰富的应用程序供测试或其它目的使用。OpenSSL具有优秀的跨平台性能，OpenSSL支持Linux、Windows、BSD、Mac、VMS等平台。在HTTPS协议实际应用方面，它经常和Nginx、Apache等搭配使用提供安全的Web服务。

  

**漏洞与危害描述**

在OpenSSL针对SSL/TLS协议握手过程的实现中，允许客户端重复发送打包的 "SSL3_RT_ALERT" -> "SSL3_AL_WARNING"
类型明文未定义警告包，且OpenSSL在实现中遇到未定义警告包时仍选择忽略并继续处理接下来的通信内容（如果有的话）。攻击者可以容易的利用该缺陷在一个消息中打包大量未定义类型警告包，使服务或进程陷入无意义的循环，从而导致占用掉服务或进程100%的CPU使用率。

所有使用OpenSSL版本库中的SSL/TLS协议都是可能受影响的（我们没有做更多的验证），
其中提供HTTPS服务的Nginx是可以容易的被攻击到无法提供服务。

该漏洞被命名为 “SSL Death Alert”，即“OpenSSL红色警戒”漏洞。

“SSL Death ALert“漏洞由来自奇虎360 Gear
Team的安全研究员石磊（360信息安全部）发现并报告给OpenSSL官方和相关开源组织，通用漏洞编号为CVE-2016-8610。

  

**CVE编号**

CVE-2016-8610

  

**受影响的OpenSSL版本**

OpenSSL 1.1.0

OpenSSL 1.0.2 – 1.0.2h

OpenSSL All 1.0.1

OpenSSL All 0.9.8

  

**不受影响的版本**

OpenSSL >= 1.0.2j

OpenSSL >= 1.1.0b

  

**缓解措施**

暂无

  

**修复建议**

建议立即对受影响和可能受影响的业务进行安全补丁或升级到不受影响的版本。

**  
**

**参考**

[1] <http://security.360.cn/cve/CVE-2016-8610/>

[2] <https://www.openssl.org>

[3]
[https://access.redhat.com/security/cve/CVE-2016-8610/](https://access.redhat.com/security/cve/CVE-2016-8610/a)

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360GearTeam** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84788](/post/id/84788)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t01c466407f2a92aaf5.jpg)
360GearTeam

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

