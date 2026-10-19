# CF 云环境利用框架，一键化利用云上内网

阅读量 **127960**

发布时间 : 2022-09-09 10:30:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t010850ac9c62cd9846.jpg)

## 前言

当我们平时拿到云服务的访问凭证即 Access Key 时，通常的做法可能是看下对方的 OSS 对象存储、或者在实例上执行个命令，但 AK
的利用远不止这些，通过 AK 我们可以做太多太多的事情，为了方便 AK 的利用，于是有了这个工具。

CF 是一个云环境利用框架，主要用来方便红队人员在获得云服务的访问凭证的后续工作。

项目地址：[github.com/teamssix/cf](https://github.com/teamssix/cf)

下载地址：[github.com/teamssix/cf/releases](https://github.com/teamssix/cf/releases)

> 代码完全开源，师傅们可以放心使用，提前祝师傅打下一个又一个点、拿下一个又一个云上管理员权限。

截止到 2022 年 7 月 10 日，CF 已迭代到 v0.2.2 版本，目前 CF 仅支持阿里云，当前 CF 已支持以下功能：

  * 一键列出目标 AK 的 OSS、ECS、RDS 服务
  * 一键获得实例上的临时访问凭证
  * 一键为实例反弹 Shell
  * 一键接管控制台
  * 一键为所有实例执行三要素，方便你懂得
  * 一键查看当前配置的权限
  * ……

## 使用手册

使用手册请参见：[wiki.teamssix.com/cf](https://wiki.teamssix.com/cf)

![](https://p2.ssl.qhimg.com/t01a861e88f2fcdd31c.png)

## 简单上手

![](https://p1.ssl.qhimg.com/t016b9f2c78d5d6fb0b.png)

配置 CF

    
    
    cf configure
    

![](https://p5.ssl.qhimg.com/t01783ec866612b0a55.png)

一键列出当前访问凭证的云服务资源

    
    
    cf ls
    

![](https://p2.ssl.qhimg.com/t01f0c495638e158512.png)

一键列出当前访问凭证的权限

    
    
    cf ls permissions
    

![](https://p4.ssl.qhimg.com/t010556ed259f142c80.png)

一键接管控制台

    
    
    cf console
    

![](https://p3.ssl.qhimg.com/t017435f3e379ebc136.png)

查看 CF 为实例执行命令的操作的帮助信息

    
    
    cf ecs exec -h
    

![](https://p5.ssl.qhimg.com/t0123f9b215fa1a9d74.png)

一键为所有实例执行三要素，方便你懂得

    
    
    cf ecs exec -b
    

![](https://p2.ssl.qhimg.com/t01dea7f2c028c350fb.png)

一键获取实例中的临时访问凭证数据

    
    
    cf ecs exec -m
    

![](https://p5.ssl.qhimg.com/t01f2fc2aacdfa5858a.png)

如果感觉还不错的话，师傅记得给个 Star 呀 ~，另外 CF
的更多使用方法可以参见使用手册：[wiki.teamssix.com/cf](https://wiki.teamssix.com/cf)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **TeamsSix** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/276249](/post/id/276249)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全工具](/tag/安全工具)
  * [云安全](/tag/云安全)
  * [云服务](/tag/云服务)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t013b8f5cd7117030d7.png) TeamsSix

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

