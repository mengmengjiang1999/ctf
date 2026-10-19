# CVE-2018-7602：Drupal核心远程代码执行漏洞分析预警

阅读量 **271474**

发布时间 : 2018-04-27 11:01:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0189d3ff2edf7dabe6.png)

报告编号： B6-2018-042601

报告来源： 360-CERT

报告作者： 360-CERT

更新日期： 2018-04-26

## 漏洞概述

2018年4月26日，Drupal官方发布新补丁和安全公告，修复了编号为CVE-2018-7602的远程代码执行漏洞，此漏洞源于3月28日的更新版中对编号为CVE-2018-7600的漏洞修复不完全，导致
**补丁被绕过** ，可以造成任意代码执行。

目前，已经发现针对CVE-2018-7602/CVE-2018-7600漏洞的在野利用，且部分利用代码已经公开。360-CERT对此漏洞进行了技术分析，建议使用Drupal开源内容管理系统的用户尽快进行更新。

## 漏洞影响面

**影响版本**

Drupal 7.x，8.x

**修复版本**

Drupal 7.59，Drupal 8.5.3，Drupal 8.4.8

**修复补丁**

  1. 8.x 版本  
[https://cgit.drupalcode.org/drupal/rawdiff/?h=8.5.x&id=bb6d396609600d1169da29456ba3db59abae4b7e](https://cgit.drupalcode.org/drupal/rawdiff/?h=8.5.x&id=bb6d396609600d1169da29456ba3db59abae4b7e)

  2. 7.x 版本  
[https://cgit.drupalcode.org/drupal/rawdiff/?h=7.x&id=080daa38f265ea28444c540832509a48861587d0](https://cgit.drupalcode.org/drupal/rawdiff/?h=7.x&id=080daa38f265ea28444c540832509a48861587d0)

注意：此补丁只针对CVE-2018-7602漏洞，针对CVE-2018-7600修复方式查看

[CVE-2018-7600:Drupal核心远程代码执行漏洞预警](https://cert.360.cn/warning/detail?id=3d862f150b642421c087b0493645b745)。

## 漏洞详情

对CVE-2018-7600漏洞的补丁通过过滤带有`#`的输入来处理请求（GET，POST，COOKIE，REQUEST）中数据。

![](https://p403.ssl.qhimgs4.com/t01aaaa777f51dcedd9.png)

但是Drupal
应用还会处理`path?destination=URL`形式的请求，发起请求需要对`destination=URL`中的URL进行URL编码，当对URL中的`#`进行编码两次，就可以绕过`sanitize()`函数过滤。

构造特殊请求绕过过滤代码

    
    
    POST /drupal-7.59/drupal-7.59/node/9/delete?destination=node?q[%2523][]=passthru%26q[%2523type]=markup%26q[%2523markup]=whoami
    

其中`%2523`是对`#`的两次URL编码。

WEB中间件对`%2523`解码获得`%23`

![](https://p403.ssl.qhimgs4.com/t01c00a7517d8971d68.png)

绕过`sanitize()`,`stripDangrousValues`函数检查。

在Drupal应用对`destination URL`进行处理时，会再次解码`%23`,获得`#`。

![](https://p403.ssl.qhimgs4.com/t01f75a320627ca735a.png)

使用parse_str,并存入options，还需要通过其他步骤来触发漏洞。

![](https://p403.ssl.qhimgs4.com/t018cc99db4b6f15ffb.png)

## 补丁分析

增加对`destination URL`安全处理

![](https://p403.ssl.qhimgs4.com/t01a4326b48de9ed70a.png)

限定parse_str只对string参数做处理

![](https://p403.ssl.qhimgs4.com/t01b55bf9a95d0b1327.png)

并在可能触发漏洞的文件模块增加处理

![](https://p403.ssl.qhimgs4.com/t016cf30d411af7283d.png)

## 时间线

**2018-03-28** Drupal 官方发布针对CVE-2018-7600漏洞的补丁和安全公告

**2018-03-29** 360-CERT 发布CVE-2018-7600:Drupal核心远程代码执行漏洞预警

**2018-04-13** 360-CERT 发布CVE-2018-7600:漏洞分析报告

**2018-04-26** Drupal 官方发布针对CVE-2018-7602漏洞的补丁和安全公告

**2018-04-26** 360-CERT 发布CVE-2018-7602:Drupal核心远程代码执行漏洞分析预警

## 参考链接

  1. <https://www.drupal.org/sa-core-2018-004>
  2. <https://www.drupal.org/sa-core-2018-002>
  3. <https://cert.360.cn/report/detail?id=c92cfff2634a44c8b1d6bd5e64c07f3d>
  4. <https://cert.360.cn/warning/detail?id=3d862f150b642421c087b0493645b745>
  5. <https://pastebin.com/pRM8nmwj>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/106669](/post/id/106669)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞预警](/tag/漏洞预警)
  * [远程代码执行](/tag/远程代码执行)
  * [CVE-2018-7602](/tag/CVE-2018-7602)
  * [Drupal漏洞](/tag/Drupal漏洞)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

