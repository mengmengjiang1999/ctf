# Gorgon黑客组织再显新招：通过在线网盘发起“三重奏”攻击

阅读量 **205874**

发布时间 : 2019-07-25 14:01:52

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01b27a98e752bafacb.png)

## 概述

近日，奇安信威胁情报中心红雨滴团队在日常的样本监控过程中，发现了一个以微软名称命名的攻击文档，并在随后的关联分析中发现，此次攻击活动疑似来自一个名为Gorgon的攻击组织，而Gorgon是一个被认为来自南亚某国家的攻击组织，PAN公司的Unit42团队将该攻击活动命名为Aggah。

本次活动中涉及的样本，除了使用该活动的招牌手段：Blogspot博客页面隐藏恶意载荷之外，还使用了三层Pastbin嵌套的方式获取最终的载荷。

由于该攻击组织不仅会针对全球政府发起攻击，还会针对全球外贸单位或个人发起攻击，且某些攻击活动中邮件还会带有中文诱饵字样，可能存在针对国内的目标，本文中我们披露此次攻击活动希望有助于公众提升对于此威胁的防范意识，同时与安全业界一起完善威胁拼图。

## 诱饵分析

本次最新捕获的样本名为Microsoft_activity_report.xls，中文翻译为“微软活动报告”，样本为美国上传，暂未更多线索证明是否为针对微软提供商或政府部门的攻击。

而本系列的攻击样本均采用了一张图片，当文档使用除了Office以外的表格编辑器打开，例如WPS、Hancom等，即会显示下面的图片提示诱导用户使用低版本的Excel打开文档，目前看来这是该组织近一个月来的攻击策略。

![](https://p3.ssl.qhimg.com/t0198cb477c62bb1693.png)

若在Office下打开，则会直接弹出提示框要求启用宏。

而该样本的传播方式疑似通过邮件内包含URL链接的方式进行投放。据分析，该文档来该URL：hxxp://www.jacosgallery.com/Microsoft_activity_report.xls，而该主站为一个光头男子的木匠日志博客。

但由于光头男子和他的木头作品作为网站模版，在外网中频繁出现，因此判断该站点为攻击者自行搭设。

## 样本分析

本次活动中，恶意文档中混淆后的宏代码与以往Gordon组织的截然不同，该组织以前曾采用的远程加载宏代码的模式在本次活动中并没有出现。

样本的具体流程与数字对应解释如下所示。

  * 打开样本，点击启用宏
  * 在解混淆后，可见实际执行的命令为 mshta http://www.bitly.com/LdsaKLX9GTSDLX

  * 而该短链接执行的链接为<https://xasnniejxlasx.blogspot.com/p/3.html>，页面上显示意义不明的字母，从源码可见，实际上mshta执行的为图中的javascript代码。

![](https://p5.ssl.qhimg.com/t0137fd80e0a0d5fa21.png)

  * 通过urldecode解码和字符串反转后，可以发现代码会第一次通过mshta去加载

<https://pastebin.com/raw/HX72131y>

![](https://p4.ssl.qhimg.com/t012c50eadae74efffe.png)

可见代码仍为编码状态。

![](https://p3.ssl.qhimg.com/t01122e3256085b3dce.png)

  * 紧接着，在进一步解码后，发现又会出现一段脚本。

脚本首先会调用cmd尝试通过删除签名集的方式组织Windows
Defender来组织其运行，并尝试杀掉与Defender相关的进行和office的进程等等。

![](https://p1.ssl.qhimg.com/t0184cfd5aa0ea28f3a.png)

并将即将访问的新的Pastebin网址
http://pastebin.com/raw/Cbt2DYUh写入注册表进行定期启动，并调用WScript执行新的网址代码。

同时编写计划任务，定期调用WScript获取<https://pastebin.com/raw/rwgtwLMg>的数据并解码运行

![](https://p2.ssl.qhimg.com/t01ee973f5724ceb780.png)

  * 而Cbt2DYUh同样为编码模式，解开后也是访问rwgtwLMg

![](https://p0.ssl.qhimg.com/t016f218f02e3ba0c5f.png)

  * 而rwgtwLMg是一段明显具有PE特征的未解码前的样本

![](https://p2.ssl.qhimg.com/t013dc767e01fe81fdf.png)

  * 经过分析，该样本使用C#编写，互斥量为RV_MUTEX-WindowsUpdateSysten32的RevengeRAT远控木马，其中Systen32存在拼写错误。

![](https://p5.ssl.qhimg.com/t01657dd3120442601a.png)

内置信息收集等模块。

![](https://p2.ssl.qhimg.com/t01950042da6c5ee727.png)

具体简易流程图如下所示。

![](https://p4.ssl.qhimg.com/t01f37865f3319b791d.png)

## 同源分析

通过木马分析流程，对比Unit42团队在今年4月份发布的报告中，可以发现其延续了使用blogspot隐藏代码并通过mshta.exe运行的特点，但本次通过直接解码后，通过连续访问三次Pastebin获取代码的操作并未在此前的活动中出现。

![](https://p0.ssl.qhimg.com/t01f8baba1ffdf47b47.png)

而后续中释放的RevengeRAT也与Unit42报告中的一致。

![](https://p1.ssl.qhimg.com/t01ef6e565e0dad9073.png)

并且，通过查阅腾讯御见威胁情报中心在1月份发布的关于Gorgon组织报告中称，当时所使用的为blogspot的订阅功能来保存恶意代码，因此可以确定本次活动与Gorgon组织关联甚大。

![](https://p0.ssl.qhimg.com/t01fec61729b3d85ecb.png)

可见，该组织使用blogspot作为载体为其主要特点，通过在线博客进行载荷传递可以更好的及时变更后续发放的木马。

此外，通过一些特征进行关联，可以发现一些近期的同源诱饵文档，名称多与外贸行业相关。

Invoice.xls

Invoice and date.xls

PurchaseXOrder.xls

Invoice.xls

Purchase Agreement.xlS

Payment Slip.xls

捕获的邮件中，针对外贸行业的内容。

![](https://p1.ssl.qhimg.com/t01643c2cab376129e2.png)

![](https://p0.ssl.qhimg.com/t0150278cd506e68196.png)

在分析过程中，有一个名为“MySexoPhone”的单词格外惹眼，该短句中含有一个o字，因此高度怀疑该词与攻击者有关系。

![](https://p1.ssl.qhimg.com/t015ee4abab48f28f24.png)

通过对该词进行搜索后，发现该团伙使用了以该单词为子域名的博客链接进行攻击

mysexophone.blogspot.com

同时，我们发现了一个名为MARIACDT的用户上传了该脚本：

![](https://p5.ssl.qhimg.com/t01f98d0005281f2c0c.png)

进一步分析发现，该组织会在该账号上面放置大量木马和恶意文档，并且其中有很多未公诸于世。并且访问次数千余次，猜测受害者数量可达数千人。

![](https://p2.ssl.qhimg.com/t018453573817458db0.png)

其中从命名不乏可以看出攻击者习惯使用释放木马的功能来进行命名。

![](https://p4.ssl.qhimg.com/t016ba9a5ebb3043b4e.png)

并且还有一些有趣的进行字符替换的攻击脚本

![](https://p1.ssl.qhimg.com/t01a296a41d268f1ce6.png)

至此，目前从公开渠道获取的关于该组织的内部代号有以下几个：

MARIACDT

HAGGA

Oldman

Steve

roma225

## 总结

Gorgon，一个被认为来自南亚某国家的黑客组织，其目标涉及全球政府，外贸等行业，且目的不纯粹为了金钱，还可能与政治相关。

而从本次活动中进行延伸，所发现的一些未公诸于世的安全事件，也足以说明从单独一件安全事件的表面，不进行线索深挖，并不能看到一件安全事件背后关联的更多的攻击和活动。

目前奇安信集团全线产品，包括天眼、SOC、态势感知、威胁情报平台，支持对涉及Gorgon组织的攻击活动检测，并且奇安信安全助手支持对该组织的样本进行拦截。

## IOC

### 近期活动诱饵文档

cb838037905a3382a83f83ad8aa89557

ad966af7ec29412c3bd3d849d0b9cf39

52c38a2241657c69b5d465713ca18192

c0e1b02647315fff567ae271da30c648

a8a8d792f404ecf97d0df751f6832bcf

ca2fcb72fb937541a701bd1bfc76d411

444cc47b9b44dc1606e58054bc56c471

02136c64091e48bc9ccdb392a439718e

adc2a8990f956531e2ac5caf67f233ad

c599a61f18ad70d5549aa1479d8da55e

fb909ab56b29e9ff186434193561ee23

### RevengeRAT

de3ae143782408c4fe7c833414f05f28

### URL

https://mysexophone.blogspot.com/

<https://createdbymewithdeniss.blogspot.com/p/john2formbook.html>

<https://xasnniejxlasx.blogspot.com/p/3.html>

[ahusdhailisjdiajsw.blogspot.com](https://www.virustotal.com/gui/search/behaviour_network%253A%2522ahusdhailisjdiajsw.blogspot.com%2522)

[http://hold-v02.ga/PTJ3315MIC.xls](https://www.virustotal.com/gui/url/51ed361ed753ccd51cc18af814e2ef323845edd48b9447a4b6d31861548fa1e9)

http://www.jacosgallery.com/Microsoft_activity_report.xls

[http://www.bi0l0.com/LdswraHmaKExmeSDE](https://www.virustotal.com/gui/url/f781219771dfe5c348ed8d0d4b20160b61e0c88443e6a4ce3480b4d259abe792)

[http://www.bitl4.com/Ldsw3aHmaKE6meSDE](https://www.virustotal.com/gui/url/d95d4ca68c8435f49ecb817ebaa715916ce88e87700ddb5cbba17d5640de8f20)

[lninbgsfxtgtrwfg.blogspot.com](https://www.virustotal.com/gui/search/behaviour_network%253A%2522lninbgsfxtgtrwfg.blogspot.com%2522)

### C2

kronozzz2.duckdns.org

microsoftoutlook.duckdns.org

[yahakhan.duckdns.org](https://www.virustotal.com/gui/search/behaviour_network%253A%2522yahakhan.duckdns.org%2522)

[tonypp.duckdns.org:8000](https://www.virustotal.com/gui/search/behaviour_network%253A%2522tcp%253A%252F%252Ftonypp.duckdns.org%253A8000%2522)

zoebin.duckdns.org

## 参考链接：

[1] Aggah Campaign: Bit.ly, BlogSpot, and Pastebin Used for C2 in Large Scale
Campaign

<https://unit42.paloaltonetworks.com/aggah-campaign-bit-ly-blogspot-and-pastebin-used-for-c2-in-large-scale-campaign/>

[2] 疑似Gorgon组织使用Azorult远控木马针对中国外贸行业的定向攻击活动

<https://s.tencent.com/research/report/624.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/182738](/post/id/182738)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [威胁情报](/tag/威胁情报)
  * [恶意活动](/tag/恶意活动)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

