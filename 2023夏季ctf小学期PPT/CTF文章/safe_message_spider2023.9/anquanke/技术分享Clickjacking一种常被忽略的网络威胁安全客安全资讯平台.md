# 【技术分享】Clickjacking：一种常被忽略的网络威胁

阅读量 **136304**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-29 14:10:54

 **x**

##### 译文声明

本文是翻译文章，文章来源：bartblaze.blogspot.jp

原文地址：<https://bartblaze.blogspot.jp/2017/09/malicious-adclick-networks-common-or.html>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**前言**

众所周知，恶意广告、恶意点击以及广告诈骗并不是什么新的网络威胁，但这些恶意行为很有可能会对网络用户构成威胁，而这也是常容易安全研究人员忽略的网络威胁。在这篇博文中，我们将介绍一些看似无害的网络点击链接和网页广告是如何具有恶意行为的。

一个“更新”提醒

在收到上图所示的“ **critical Firefox update**
”更新提醒后，用户会下载并运行上图中.js文件，但该文件是经过多重混淆处理的，下图是我们经过2次反混淆处理后得到的结果：

该脚本（附加其他参数）尝试从 **ohchivsevmeste5[.]com**
服务器上下载一个.flv文件，虽然在写这篇博文时已经无法再复现上述事件，但是我们确定该脚本会去获取另一个严重混淆的JavaScript，以用来对用户的操作进行劫持。劫持操作并非罕见的现象，以下是维基百科关于该恶意行为的描述：点击劫持（clickjacking）是一种在[网页](https://zh.wikipedia.org/wiki/%E7%BD%91%E9%A1%B5
"网页")中将[恶意代码](https://zh.wikipedia.org/wiki/%E6%81%B6%E6%84%8F%E4%BB%A3%E7%A0%81
"恶意代码")等隐藏在看似无害的内容（如[按钮](https://zh.wikipedia.org/wiki/%E6%8C%89%E9%92%AE_\(%E8%AE%A1%E7%AE%97%E6%9C%BA\)
"按钮 \(计算机\)")）之下，并诱使用户点击的手段。正如上图所示，我们看到的是Firefox更新，但其实更新的背后是恶意的JS脚本。  
**  
**

**深入调查**

上图中的域名对应的IP地址是192.129.215[.]157，该IP地址上还有大量其他域名，其中大部分域名都是随机的，我们发现其中一个域名（aiwohblackhatx[.]org）的注册人的电子邮件地址是abdelrahman.a.y.127@gmail[.]com，并且该电子邮件地址链接到了一个Facebook页面（[mltaqaalwza2f2](https://www.facebook.com/mltaqaalwza2f2/)）
，该页面声称是一个求职类网站，直到最近，该页面才将联系人的电子邮件地址更改为ADMIN @ ULTIMATECLIXX
[。]ADMIN@ULTIMATECLIXX[.]COM COM,Ultimateclixx网站支持即时付款功能，如下图所示：

被动DNS数据显示，上述电子邮件地址与多个域名有联系，特别是“Mohammed
Farajalla”这个人，这个人拥有多个电子邮件地址，且都与恶意点击网络有关，具体分析如下所示：

刚开始，我认为Abdelrahman和Mohammed是同一个人。
然而，来自另一个域名（aifomtomyam69[.]org）的Whois数据显示，该域名的所有者是Abdelrahman Farajallah。

似乎Abdelrahman和Mohammed的关系很亲近，Mohammed在该恶意活动中负责传播，而Abdelrahman则负责网站的技术（包括注册域名等），这显然是一个很好的恶意商业活动。从上图我们看到mhmadfarajalla在帖子中说明了他是如何从2013年起加入Goldenclixx的
，并在该公司做了相当多的投资。下面这个回复可用于质疑其合法性：

上述是一个2015年发布在eMoneySpace论坛上的一个帖子，该论坛是一个合法的论坛，旨在推广或谈论与互联网金钱相关的网站，基本上就是讨论如何通过在线广告赚钱。

相关的URL是：

[https://www.emoneyspace.com/forum/index.php?topic=361872.0](https://translate.googleusercontent.com/translate_c?depth=1&hl=zh-CN&prev=search&rurl=translate.google.com.hk&sl=en&sp=nmt4&u=https://www.emoneyspace.com/forum/index.php?topic=361872.0&usg=ALkJrhgqjP2a_CC85Du5Mp5z_Yev5Hd96A)

我也在这里设置了一个镜像：

[web.archive.org/web/20170918213144/](https://translate.googleusercontent.com/translate_c?depth=1&hl=zh-CN&prev=search&rurl=translate.google.com.hk&sl=en&sp=nmt4&u=https://web.archive.org/web/20170918213144/https://www.emoneyspace.com/forum/index.php?topic=361872.0&usg=ALkJrhjiLC8WI7HRuocb5CTwcZ_BbnGqSw)
[www.emoneyspace.com/forum/index.php?topic=361872.0](https://translate.googleusercontent.com/translate_c?depth=1&hl=zh-CN&prev=search&rurl=translate.google.com.hk&sl=en&sp=nmt4&u=https://web.archive.org/web/20170918213144/https://www.emoneyspace.com/forum/index.php?topic=361872.0&usg=ALkJrhjiLC8WI7HRuocb5CTwcZ_BbnGqSw)

看来，Abdelrahman和Mohammed已经长期参与了该诈骗计划，虽然他们最初可能以一种合法赚钱的方式开始他们的项目或业务，但现在该项目或者业务已经开始实施诈骗恶意行为，他们可能位于巴勒斯坦。  
 **  
**

**恶意域名分析**

此前，我提到恶意JS脚本中涉及到的域名似乎是随机的，让我们一起看看这些域名：

    
    
    aidixhurricane[.]net
    aifomtomyam69[.]org
    aingucareersearchings[.]com
    aiteobutigim[.]net
    aiwohblackhatx[.]org 
    ohchivsevmeste5[.]com
    ohighzapiska[.]org
    ohlahlukoil[.]org
    ohmuogoodlacksha[.]com
    ohseltelists[.]org

通过观察我们发现，域名的前两个字符是相同的，而其余部分的确是随机的，我们再看一些其他域名：

    
    
    vaewedashrecipes[.]net
    vahfebankofamerica[.]net
    iechow3blog[.]org
    iefaxshoeboxapp[.]net
    iegiwrealarcade[.]org
    iehohclock-world[.]org
    iengeluxauto[.]com
    ieweimz16[.]org
    ieyonthesubfactory[.]net

上述列表中有一个注册较新的域名（vahfebankofamerica[.]net）它的注册时间是2017-09-12，由Megan
Quinn注册，注册电子邮件地址是qum65@binkmail[.]com。
我猜测Quinn女士会使用这个电子邮件地址来试图说服用户相信该网站的合法性，因为该地址看起来像是一家美国银行网站的邮箱地址。有趣的是，我们发现了通过该域托管的JavaScript：

[https://vahfebankofamerica[.]net/3558451080485/150526622449473/firefox-patch[.]js](https://vahfebankofamerica%5B.%5Dnet/3558451080485/150526622449473/firefox-patch%5B.%5Djs)

毫无疑问，该网站还将提示用户下载Firefox安全更新，该重定向混合使用了广告欺诈和clickjacking。其实，很多电子邮件地址似乎都是随机生成的，包括他们使用的用户名，下图所示的是另一个例子：

上述的Whois信息都是假的，且不说Allan Yates这个用户名是否存在，但就算他存在，上述的Whois信息也与他没有任何关系，Allan
Yates这个用户名只是用“假名称生成器”生成的。
我们现在获取到几个IP主机，该主机上都托管了一些随机域名，这些域名大多用来设置重定向，广告欺诈和点击劫持。最初发现的是192.129.215 [.]
157这个IP，现在又找到一个192.129.215 [.] 155。  
因此，我决定研究一些192.129.215 [.] 156这个IP，
事实证明该IP地址同样用于实施恶意行为，难道我们应该阻止整个192.129.215.0/24子网? 通过研究我们发现，大部分域名拥有以下特性：

**使用DomainsByProxy进行域名Whois隐私保护**

**网站部署了CloudFlare**

**使用由Comodo发行的有效SSL证书。**  
 **  
**

**进一步分析**

早些时候，Mohammed在他的论坛上发表了关于adzbazar.com的帖子，这是他注册的一个新网站，该网站界面如下所示：

通过之前发现的abdelrahman.ay127@gmail [.] com这个电子邮件地址，我经过关联分析找到了另一个注册域名adz2you [.]
com。通过使用PassiveTotal工具，我们可以找到一个带有gptplanet的hostpair，其中Gptplanet声称：

任何人都可以免费加入，并通过完成在线简单任务赚取收益。

分析Mohammed和他所拥有的域名以及挖掘其发表的与广告欺诈主题相关的论坛帖子并没有花费我太长的时间，在下面这个URL中可以找到相关讨论的主题：

[http://www.gptplanet.com/forum.php?topic=18119](https://translate.googleusercontent.com/translate_c?depth=1&hl=zh-CN&prev=search&rurl=translate.google.com.hk&sl=en&sp=nmt4&u=http://www.gptplanet.com/forum.php?topic=18119&usg=ALkJrhj7RIBPgLIZiUjpMTEE0MJtDpmEeg)  
同样，我也在以下这个URL处设置了一个网站镜像：

[https://web.archive.org/web/20170920001823/http://www.gptplanet.com/forum.php?topic=18119](https://translate.googleusercontent.com/translate_c?depth=1&hl=zh-CN&prev=search&rurl=translate.google.com.hk&sl=en&sp=nmt4&u=https://web.archive.org/web/20170918213144/https://www.emoneyspace.com/forum/index.php?topic=361872.0&usg=ALkJrhjiLC8WI7HRuocb5CTwcZ_BbnGqSw)
。

最后，基于我们的研究猜测，似乎Mohammed还没有完成这两个“骗局”，目前为止也没有发现用户受到此恶意行为的威胁。  
 **  
**

**安全建议**

以下是可用于预防恶意广告和clickjacking的措施：

**a.安装防病毒软件；**

**b.保持浏览器版本是最新的；**

**c.如果正在使用Firefox，请安装**[
**NoScript**](https://translate.googleusercontent.com/translate_c?depth=1&hl=zh-CN&prev=search&rurl=translate.google.com.hk&sl=en&sp=nmt4&u=https://noscript.net/&usg=ALkJrhgWkOXzUziZowKtELX0SwKHvJg-ow) **；**

**d.安装广告拦截器，例如**[ **uBlock
Origin**](https://translate.googleusercontent.com/translate_c?depth=1&hl=zh-CN&prev=search&rurl=translate.google.com.hk&sl=en&sp=nmt4&u=https://github.com/gorhill/uBlock&usg=ALkJrhhMdiE17A0sONnB41NPHJ9cyz1LuA#installation)
**（适用于大多数浏览器）。**

并且，在浏览互联网时请保持小心谨慎。由于192.129.215 [.]
157服务器上的恶意活动仍保持高度活跃，因此建议将该IP以及文章末尾提供的其他域和IP加入到阻止或黑名单中去。  
当你碰到类似于上述的Firefox更新下载提示或其他任何弹出窗口时，你需要立马取消下载，如果手动不能取消下载，那么需要停止浏览器进程的运行，该操作可以通过任务管理器来完成。如果你真的受到了广告欺诈和clickjacking的恶意威胁，那么建议你执行以下操作：

**a.卸载并重新安装当前浏览器及其扩展应用；**

**b.使用安装的防病毒产品执行全面扫描;**

**c.使用在线防病毒产品或**[
**Malwarebytes**](https://translate.googleusercontent.com/translate_c?depth=1&hl=zh-CN&prev=search&rurl=translate.google.com.hk&sl=en&sp=nmt4&u=https://www.malwarebytes.com/&usg=ALkJrhjdxsUp0o9IylXpuSTT9nhICfXMzg)
**进行全面扫描;**

**d.更改密码**

此外，你还可以检查防火墙或代理的日志，查看文章末尾提供的IOCS中的IP或者域名是否出现在你的日志文件中。  
**  
**

**结论**

互联网中有许多和广告欺诈、clickjacking以及网络广告类似的网络站点，虽然网络广告通常不是恶意的，但在以下几种情况下其可能存在恶意行为：

**a.投放广告的网站遭到入侵；**

**b.广告遭到入侵；**

**c.网络广告本身是恶意的。**

可能在某些时候，应该有更好的网络广告安全控制策略，以防止像本文中描述的攻击或恶意活动，因此适当的安全措施对于广告网站而言是必要的，并且对于任何投放广告的网站也是如此。

  

**IOC**

https://otx.alienvault.com/otxapi/pulses/59c2ef1529b98a74bb6d7a1c/export?format=csv

本文翻译自bartblaze.blogspot.jp
[原文链接](https://bartblaze.blogspot.jp/2017/09/malicious-adclick-networks-common-or.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **blueSky** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86957](/post/id/86957)

安全客 - 有思想的安全新媒体

本文转载自:
[bartblaze.blogspot.jp](https://bartblaze.blogspot.jp/2017/09/malicious-adclick-networks-common-or.html)

如若转载,请注明出处： <https://bartblaze.blogspot.jp/2017/09/malicious-adclick-networks-common-or.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t01d4c6d0183e5e3280.jpg) blueSky

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

