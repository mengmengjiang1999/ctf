# 【漏洞预警】Fastjson 远程代码执行漏洞(暂无PoC)

阅读量 **186665**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-03-16 16:56:12

 **x**

##### 译文声明

本文是翻译文章，文章来源：正禾@先知技术社区

原文地址：<https://bbs.aliyun.com/read/309931.html>

译文仅供参考，具体内容表达以及含义原文为准。

****

**Fastjson简介**

Fastjson是一个Java语言编写的高性能功能完善的JSON库。它采用一种“假定有序快速匹配”的算法，把JSON
Parse的性能提升到极致，是目前Java语言中最快的JSON库。Fastjson接口简单易用，已经被广泛使用在缓存序列化、协议交互、Web输出、Android客户端等多种应用场景。

**  
**

**漏洞概要**

2017年3月15日，Fastjson
官方发布安全公告，该公告介绍fastjson在1.2.24以及之前版本存在代码执行漏洞代码执行漏洞，恶意攻击者可利用此漏洞进行远程代码执行，从而进一步入侵服务器，目前官方已经发布了最新版本，最新版本已经成功修复该漏洞。

  

**漏洞详情**

**漏洞编号:** 暂无

**漏洞名称:** **** Fastjson远程代码执行漏洞

**官方评级:** 高危

**漏洞描述:**

fastjson在1.2.24以及之前版本存在代码执行漏洞，当用户提交一个精心构造的恶意的序列化数据到服务器端时，fastjson在反序列化时存在漏洞，可导致远程任意代码执行漏洞。

**漏洞利用条件和方式:**

黑客可以远程代码执行成功利用该漏洞。

**漏洞影响范围:**

1.2.24及之前版本

**  
**

**漏洞检测**

检查fastjson 版本是否在1.2.24版本内

    
    
    ps aux | grep fastjson

**POC**

暂无 ****

  

**WAF检测办法**

检测post内容中是否包含如下字符

    
    
    "@type"

**漏洞修复建议(或缓解措施)**

目前官方已经发布了最新版本，该版本已经成功修复该漏洞。

阿里云上用户建议采用以下两种方式将fastjson升级到1.2.28或者更新版本：

更新方法如下：

**1.Maven 依赖配置更新**

通过 maven 配置更新，使用最新版本，如下：

    
    
    <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>fastjson</artifactId>
        <version>1.2.28</version>
    </dependency>

**2. 最新版本下载**

下载地址：<http://repo1.maven.org/maven2/com/alibaba/fastjson/1.2.28/>

**3.云盾WAF防护**

如果您无法及时升级fastjson，您可以选用[阿里云云盾WAF](https://common-buy.aliyun.com/?spm=5176.bbsr309931.0.0.JVViAV&commodityCode=waf#/buy)自动防护。

  

**情报来源**

<https://github.com/alibaba/fastjson/wiki/security_update_20170315>

本文翻译自正禾@先知技术社区 [原文链接](https://bbs.aliyun.com/read/309931.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85713](/post/id/85713)

安全客 - 有思想的安全新媒体

本文转载自: [正禾@先知技术社区](https://bbs.aliyun.com/read/309931.html)

如若转载,请注明出处： <https://bbs.aliyun.com/read/309931.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

