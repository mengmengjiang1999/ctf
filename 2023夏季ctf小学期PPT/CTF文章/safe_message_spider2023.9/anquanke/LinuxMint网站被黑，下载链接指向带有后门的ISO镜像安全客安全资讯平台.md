# Linux Mint网站被黑，下载链接指向带有后门的ISO镜像

阅读量 **98564**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-02-22 17:19:11

 **x**

##### 译文声明

本文是翻译文章，文章来源：Freebuf

原文地址：<http://www.freebuf.com/news/96693.html>

译文仅供参考，具体内容表达以及含义原文为准。

你在2016年2月20日下载过Linux Mint吗？你可能已经感染了病毒……  

Linux Mint是目前最畅销、最流行的Linux发行版，如果你最近刚下载并安装了该操作系统，不幸的告诉你，你下载的可能是带有恶意程序的ISO镜像。

20日晚上，一些未知名的黑客或者组织入侵进了Linux Mint网站，替换了网站中的下载链接，指向一个提供了Linux Mint 17.3
Cinnamon版本恶意ISO镜像的服务器。

Linux Mint 负责人Clement Lefebvre评论到：

> “黑客们制作了一个修改版的Linux Mint ISO，在上面植入了后门，然后设法入侵了我们网站，把下载链接指向了这个修改版。”

**谁会感染带后门的Linux Mint呢？**

Linux Mint团队目前发现只有一个版本会受影响，它就是Linux Mint 17.3 Cinnamon版本。

入侵事件发生在20日晚上，所以受影响的人群只限制在周六晚上下载Linux Mint 17.3
Cinnamon版本的用户。如果你是在20日之前下载或者卸载了Linux Mint 17.3
Cinnamon版本，那你就不会受到影响。如果你下载的是其他版本的Linux Mint，即便通过Torrent或者HTTP链接包含了Mint 17.3
Cinnamon，那也不会受影响。

**攻击详情**

黑客通过团队的WordPress博客访问了底层服务器，然后获得了访问数据的shell。调查小组的发现，黑客操控了Linux
Mint下载页面，并将下载链接指向了一个恶意FTP（文件传输协议）服务器上，该服务器被发现位于保加利亚（IP:
5.104.175.212）。受影响的Linux ISO
安装了完整的操作系统（含有网络中继聊天（IRC）后门Tsunami），所以黑客便可以通过IRC服务器访问了系统。

注：Tsunami是非常著名的Linux ELF木马，一个简单的IRC bot，用于发动DDoS攻击。

**黑客vs Linux Mint系统管理员**

Linux Mint团队迅速发现了这次黑客入侵，清除了网站上的恶意链接，随之在Linux
Mint博客上承认了这次入侵事件。但是不久之后，这群黑客又再次入侵了它们的下载页面。

事实上，Linux Mint没有清除掉黑客所利用的入侵端口，所以后来Linux Mint团队选择下线了整个
linuxmint域名，以防止ISO镜像进一步的感染用户。

> “我们不清楚这次攻击背后的目的是什么，如果攻击者进一步的攻击我们，并且他们的目标就是伤害我们，我们将会寻求法律和安全公司的帮助，找出背后的元凶。”

**黑客售卖Linux Mint网站数据**

黑客在网上售卖Linux Mint数据，全站数据仅售85美元。这些黑客们似乎是菜鸟，或者经验不足的组织，有经验的黑客一般不会选择用IRC
bot来攻击最新的Linux发行版。而且从他们的入侵行为被发现之后又再次发动攻击来看，他们也应该是经验较少的黑客。

**怎样保护Linux设备安全？**

ISO镜像用户可以先检查签名是否有效，对比设备的MD5签名是否与官方版本一致。如果已经安装了带有后门的系统，建议执行以下步骤：

> 1.立即断网
>
> 2.备份所有的数据
>
> 3.格式化或者重新安装操作系统
>
> 4.更改敏感网站和邮箱的密码

本文翻译自Freebuf [原文链接](http://www.freebuf.com/news/96693.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83510](/post/id/83510)

安全客 - 有思想的安全新媒体

本文转载自: [Freebuf](http://www.freebuf.com/news/96693.html)

如若转载,请注明出处： <http://www.freebuf.com/news/96693.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

