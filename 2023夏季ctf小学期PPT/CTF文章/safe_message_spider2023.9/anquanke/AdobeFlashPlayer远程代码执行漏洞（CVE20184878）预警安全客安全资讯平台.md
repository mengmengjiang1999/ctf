# Adobe Flash Player远程代码执行漏洞（CVE-2018-4878）预警

阅读量 **261509**

发布时间 : 2018-02-03 10:57:53

 **x**

##### 译文声明

本文是翻译文章，文章来源：cert.360.cn/warning/

原文地址：<https://cert.360.cn/warning/detail?id=28a76e80274f9c1de7e76c24a5f7eba2>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01042b4c934749762b.png)

> 报告编号：B6-2018-020201
>
> 报告来源：360网络安全响应中心
>
> 报告作者： MerJerson，SuperXX
>
> 更新日期：2018年02月02日

## 漏洞背景

近日，韩国计算机应急响应中心和Adobe官方针对Adobe Flash Player系列产品发布安全公告，Adobe Flash
Player产品（包括最新款）存在远程代码命令执行漏洞，漏洞编号 CVE-2018-4878 ，Adobe计划在2月5号推送修复补丁。

有关CVE-2018-4878的Flash漏洞已经被发现在野利用，攻击者通过分发嵌入了恶意Flash的email来进行攻击，漏洞可以通过网页，office文档触发。韩国安全员Simon
Choi声称自2017年11月中旬就有部分韩国人遭受到该漏洞攻击。

## 漏洞影响面

漏洞ID: CVE-2018-4878

漏洞类型：UAF

威胁类型：远程代码执行

威胁等级：高

受影响版本：Adobe Flash Player <= 28.0.0.137

受影响产品：Adobe Flash Player 桌面应用

Adobe Flash Player for Google Chrome

Adobe Flash Player for Microsoft Edge and Internet Explorer 11

受影响平台：Windows, Macintosh, Linux, Chrome OS

攻击者可以将恶意Flash文件嵌入Office文档，网页，或者桌面应用，当用户打开时便会收到攻击。Adobe已经确认了该漏洞的存在，将在2月5日的补丁中修复该漏洞。

## 安全建议

目前该漏洞处于0day状态，漏洞修补期间建议用户禁用或者卸载Adobe Flash Player。对Office文档，采用受保护的视图的方式打开。

漏洞补丁推送后，请及时安装相关补丁。

## 时间线

2018年1月31日 KR-CERT发布安全警报

2018年2月1日 Adober确认漏洞，发布安全公告，

2018年2月2日 360CERT发布漏洞预警

## 参考链接

<https://helpx.adobe.com/security/products/flash-player/apsa18-01.html>

<https://www.bleepingcomputer.com/news/security/new-adobe-flash-zero-day-spotted-in-the-wild/>

本文翻译自cert.360.cn/warning/
[原文链接](https://cert.360.cn/warning/detail?id=28a76e80274f9c1de7e76c24a5f7eba2)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/97383](/post/id/97383)

安全客 - 有思想的安全新媒体

本文转载自:
[cert.360.cn/warning/](https://cert.360.cn/warning/detail?id=28a76e80274f9c1de7e76c24a5f7eba2)

如若转载,请注明出处：
<https://cert.360.cn/warning/detail?id=28a76e80274f9c1de7e76c24a5f7eba2>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [预警](/tag/预警)
  * [CVE-2018-4878](/tag/CVE-2018-4878)
  * [Adobe Flash Player](/tag/Adobe Flash Player)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

