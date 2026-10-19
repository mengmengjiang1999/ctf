# 一次QuasarRAT的利用活动发现分析

阅读量 **306275**

发布时间 : 2020-11-18 12:00:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t013e4c47597f94ade8.jpg)

作者：看天明@meshfire

## 概述

    
    
       Quasar是使用C＃编写的快速，轻量级的远程管理工具，主要针对Windows操作系统，由于其开源，功能丰富的特性，经常被黑客用于各种网络攻击活动。
       在近日运营过程中，检测到一起仿冒VEGAS_PRO安装软件的病毒样本。该软件在运行后会设置自启项并留下后门文件，同时注入到进程RegSvcs.exe进行后续攻击活动。经过分析发现此次攻击活动利用的核心恶意程序即为QuasarRAT。
    

#

## 样本行为分析

###  软件初次运行流程

![](https://p0.ssl.qhimg.com/t017b56de8ee174e7ff.png)

其中释放的AppXApplicabilityBlob.url、AppXApplicabilityBlob.vbs、scrconsHD.exe

为其持续化手段。

###  软件具体分析

**VEGAS_Pro:**

软件具体信息:

![](https://p2.ssl.qhimg.com/t011e4e403b60cbe5fc.png)

拖入查壳软件发现AutoIt关键字

![](https://p0.ssl.qhimg.com/t01182d11cd1f5ad6d1.png)

脱出该脚本查看主要功能为设置自启项，释放真正的安装软件，解密

![](https://p5.ssl.qhimg.com/t0177ac9acedb699762.png)

![](https://p1.ssl.qhimg.com/t01074d8143aac6f7d3.png)

创建RegSvcs进程进行注入

![](https://p4.ssl.qhimg.com/t01c3c816fc35588439.png)

**加载器**

Dump出注入代码，查询发现为.net的程序

该程序为一个加载器，会再次动态解密加载两个.dll文件，进行反虚拟机，查询安全软件的功能，并加载真正的恶意程序

反虚拟机检测

![](https://p3.ssl.qhimg.com/t0155241b454238a46e.png)

安全软件路径检测

![](https://p4.ssl.qhimg.com/t01603512840ba60c38.png)

解密解压出新的pe文件

![](https://p0.ssl.qhimg.com/t01963c737b63997d15.png)

**主要恶意程序:**

对其主核心文件dump并反混淆后，调试查看其功能

根据解密出的字符串特征发现该程序为开源的QuasarRAT软件

![](https://p5.ssl.qhimg.com/t01ca8a297f6905f56a.png)

检测互斥体

![](https://p0.ssl.qhimg.com/t0195de777c354894f2.png)

连接hxxp://ip-api.com/json/，获取受害者的地理位置等信息

![](https://p2.ssl.qhimg.com/t015760bd65dfc108a7.png)

设置键盘钩子

![](https://p3.ssl.qhimg.com/t01772334b940de1ab6.png)

接受网络连接，发送并获取指令

![](https://p4.ssl.qhimg.com/t015a9eab56bd56f683.png)

可以发现具备的功能有:摄像头获取，远程桌面键盘记录，获取密码(浏览器记录)，下载上传，编辑注册表进程，创建执行关闭远程shell执行等远控功能

![](https://p2.ssl.qhimg.com/t0103352efe529ead9a.png)

## 相关IOC:

域名: starcraft.mywire.org

样本md5:

安装软件VEGAS_Pro_17.0.0.421.exe: 5260FC9C72ADDE494BCDCF7E739D635A

加载器: A1D010200E360E910C56377744FA1214

Quasar RAT: D918F2B0CDCE02D14B9F362CBA4E2DF1

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360 MeshFire Team** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222801](/post/id/222801)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [样本分析](/tag/样本分析)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t01b22d45fef232c21b.png) 360 MeshFire Team

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

