# 【技术分享】BurpSuite插件：利用BurpSuite Spider收集子域名和相似域名

阅读量 **201179**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-07-28 20:51:55

 **x**

##### 译文声明

本文是翻译文章，文章来源：polaris-lab.com

原文地址：<http://www.polaris-lab.com/index.php/archives/349/>

译文仅供参考，具体内容表达以及含义原文为准。

**作者：bit4@polaris-lab.com**

**  
**

**前言**

在我的域名收集知识体系中，利用爬虫来获取域名是其中的一部分（见文末思维导图，其他部分的实现请访问我的另外一个项目：<https://github.com/bit4woo/Teemo>
），由于使用频率，使用习惯等问题，而我最终决定使用BurpSuite的Spider来实现爬虫部分的自动化收集。所以有了这个BurpSuite插件：Domain
Hunter。

  

**原理**

****

当使用了BurpSuite作为代理，或者使用它进行了安全测试，会就会记录相关的域名。其中，某个目标的子域名和相似域名很有价值，尤其是相似域名，往往有惊喜！插件的主要原理就是从BurpSuite的Sitemap中搜索出子域名和相似域名。也可以对已经发现的子域名进行主动爬取，以发现更多的相关域名，这个动作可以自己重复递归下去，直到没有新的域名发现为止。

  

**项目地址**

****

<https://github.com/bit4woo/domain_hunter>

**截图**

****

**Change Log**

****

2017-07-28: Add a function to crawl all known subdomains; fix some bug.

  

**Xmind Of Domain Collection**

****

本文翻译自polaris-lab.com [原文链接](http://www.polaris-lab.com/index.php/archives/349/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86512](/post/id/86512)

安全客 - 有思想的安全新媒体

本文转载自: [polaris-lab.com](http://www.polaris-lab.com/index.php/archives/349/)

如若转载,请注明出处： <http://www.polaris-lab.com/index.php/archives/349/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

