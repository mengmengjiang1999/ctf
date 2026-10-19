# CVE-2018-4901 Adobe Acrobat Reader远程代码执行漏洞预警

阅读量 **200616**

|评论 **3**

发布时间 : 2018-03-06 09:56:50

 **x**

##### 译文声明

本文是翻译文章，文章原作者 360CERT，文章来源：cert.360.cn

原文地址：<https://cert.360.cn/warning/detail?id=33ec6051c0ca499106a3aa6168d853f5>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0197dc3859e8de2bd7.png)

**安全报告：CVE-2018-4901 Adobe Acrobat Reader远程代码执行漏洞预警**  
---  
报告编号：B6-2018-030501  
报告来源：360CERT  
报告作者：360CERT  
联系方式：[cert@360.cn](mailto:cert@360.cn)  
保密范围：公开  
更新日期：2018年3月5日  
  
****

## 0x00 事件描述

2018年2月23日，TALOS披露了Adobe Acrobat
Reader的一个远程代码执行漏洞相关细节，漏洞编号CVE-2018-4901，漏洞报告者为“Aleksandar
Nikolic”。该漏洞是一个栈溢出漏洞，可以通过恶意文件和恶意网页传播。目前暂时未监测到成功利用该漏洞进行攻击的样本出现。

## 0x01事件影响面

经过360CERT分析，成功利用该漏洞需要绕过GS保护，在TALOS的博客中并没有披露如何绕过GS的细节，成功利用难度较大，但也不排除未来如果POC公布后会被大量利用的可能。

综合判定CVE-2018-4901漏洞为中危漏洞，属于 **一般网络安全事件** 。

## 0x02部分技术信息

该漏洞通过指定pdf文件trailer中一个超长的ID来触发。当它在javascript被引用时，将字节编码为16进制字符串的过程中由于没有对长度进行检查会发生栈溢出。

在C:\Program Files (x86)\Adobe\Acrobat Reader
DC\Reader\plug_ins\EScript.api的sub-2389E7C0函数中：

![](https://p5.ssl.qhimg.com/t01e4548b791d89dca6.png)

可以看到这里没有对v3进行检查。

示例ID：

    
    
    /ID   <AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA><a> 

一行简单的javascript代码即可触发漏洞：

this.docID;

## 0x03处理建议

按照官网的说明，更新到不受影响的版本。

  

## 0x04 时间线

2018-02-23 事件被披露

2018-03-05 360CERT完成了基本分析报告

## 0x05 参考

  1. <https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0505>
  2. <https://helpx.adobe.com/security/products/acrobat/apsb18-02.html>

本文翻译自cert.360.cn
[原文链接](https://cert.360.cn/warning/detail?id=33ec6051c0ca499106a3aa6168d853f5)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/99919](/post/id/99919)

安全客 - 有思想的安全新媒体

本文转载自:
[cert.360.cn](https://cert.360.cn/warning/detail?id=33ec6051c0ca499106a3aa6168d853f5)

如若转载,请注明出处：
<https://cert.360.cn/warning/detail?id=33ec6051c0ca499106a3aa6168d853f5>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [栈溢出](/tag/栈溢出)
  * [CVE-2018-4901](/tag/CVE-2018-4901)
  * [远程执行漏洞](/tag/远程执行漏洞)
  * [Adobe Acrobat Reader](/tag/Adobe Acrobat Reader)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

