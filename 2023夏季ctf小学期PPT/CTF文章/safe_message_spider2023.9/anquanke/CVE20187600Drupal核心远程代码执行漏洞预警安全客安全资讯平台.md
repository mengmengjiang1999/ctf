# CVE-2018-7600:Drupal核心远程代码执行漏洞预警

阅读量 **188057**

发布时间 : 2018-03-29 17:00:48

 **x**

##### 译文声明

本文是翻译文章，文章原作者 360CERT，文章来源：cert.360.cn

原文地址：<https://cert.360.cn/warning/detail?id=3d862f150b642421c087b0493645b745>

译文仅供参考，具体内容表达以及含义原文为准。

> 报告编号： B6-2018-032901
>
> 报告来源： 360-CERT
>
> 报告作者： 360-CERT
>
> 更新日期： 2018-03-29

## 漏洞概述

Drupal是一款开源的内容管理系统，使用php语言，在业界广泛使用。

2018年3月28日，Drupal官方发布新补丁和安全公告，Drupal 6,7,8多个子版本存在远程代码执行漏洞(CVE-2018-7600)。

![](https://p3.ssl.qhimg.com/t0175d1c4fb24f83b46.png)

360CERT通过对补丁分析，结合Drupal官方通告判定

  * 风险等级严重
  * 影响范围较广

虽然漏洞细节暂未公开，仍然建议使用Drupal开源内容管理系统的用户进行更新。

## 漏洞影响面

#### 影响版本

Drupal 6.x，7.x，8.x

#### 修复版本

Drupal 7.58，Drupal 8.5.1

## 修复方案

### 推荐更新

主要支持版本推荐更新到Drupal相应的最新子版本

7.x版本，更新到 7.58 <https://www.drupal.org/project/drupal/releases/7.58>

8.5.x版本，更新到 8.5.1 <https://www.drupal.org/project/drupal/releases/8.5.1>

8.4.x 版本，更新到 8.4.6 <https://www.drupal.org/project/drupal/releases/8.4.6>

8.3.x 版本，更新到 8.3.9 <https://www.drupal.org/project/drupal/releases/8.3.9>

### 使用patch更新

如果不能立即更新，请使用对应patch

8.5.x,8.4.x,8.3.x patch地址:

[https://cgit.drupalcode.org/drupal/rawdiff/?h=8.5.x&id=5ac8738fa69df34a0635f0907d661b509ff9a28f](https://cgit.drupalcode.org/drupal/rawdiff/?h=8.5.x&id=5ac8738fa69df34a0635f0907d661b509ff9a28f)

7.x patch地址:

[https://cgit.drupalcode.org/drupal/rawdiff/?h=7.x&id=2266d2a83db50e2f97682d9a0fb8a18e2722cba5](https://cgit.drupalcode.org/drupal/rawdiff/?h=7.x&id=2266d2a83db50e2f97682d9a0fb8a18e2722cba5)

### 其他不支持版本

Drupal 8.0/8.1/8.2版本已彻底不再维护，如果你在使用这些版本的Drupal，请尽快更新到8.3.9或8.4.6版本

Drupal 6也受到漏洞影响，此版本由Drupal 6 Long Term Support维护。

参考<https://www.drupal.org/project/d6lts>

## 时间线

**2018-03-21** Drupal 官方发布公告将会在下周修复高危漏洞

**2018-03-28** Drupal 官方发布补丁和安全公告

**2018-03-29** 360CERT发布预警通告

## 参考链接

  1. <https://www.drupal.org/sa-core-2018-002>
  2. <https://groups.drupal.org/security/faq-2018-002>

本文翻译自cert.360.cn
[原文链接](https://cert.360.cn/warning/detail?id=3d862f150b642421c087b0493645b745)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/103102](/post/id/103102)

安全客 - 有思想的安全新媒体

本文转载自:
[cert.360.cn](https://cert.360.cn/warning/detail?id=3d862f150b642421c087b0493645b745)

如若转载,请注明出处：
<https://cert.360.cn/warning/detail?id=3d862f150b642421c087b0493645b745>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞预警](/tag/漏洞预警)
  * [Drupal](/tag/Drupal)
  * [Drupal内核高危漏洞](/tag/Drupal内核高危漏洞)
  * [CVE-2018-7600](/tag/CVE-2018-7600)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

