# 利用Consul RCE漏洞传播的挖矿木马分析

阅读量 **603523**

发布时间 : 2019-03-21 20:46:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/dm/1024_682_/t01d75e9b3d157155f0.jpg)

作者: Ksh0m、imbeee @360sglab

## 简述

在2018年11月，360观星实验室接到某客户Linux服务器挖矿，发现这是一起通过consul服务（一种配置管理云平台的分布式服务，默认开启端口8500）的RCE漏洞进行传播和植入的挖矿恶意木马，该木马会下载到/var/tmp目录下并命名为systemd-xxxx，并上传用户信息，而控制的CC隐藏在Tor网络。无独有偶，近日观星实验室又捕获到类似样本，发现黑客更新了域名和样本信息

## 事件分析

旧的恶意样本位于/var/tmp目录下名称为systemd-check，新的恶意样本位于/tmp目录下命名为systemd-login，基本信息如下

![](https://p1.ssl.qhimg.com/t01307acff24266daaf.png)

截止3月21日，VT记录上还未有杀软引擎报毒

![](https://p1.ssl.qhimg.com/dm/1024_187_/t0125d8c51fa88e95ce.png)

![](https://p0.ssl.qhimg.com/dm/1024_146_/t019ef17a1106ee073f.png)

黑客的攻击手法是扫描暴露在公网的Consul的8500端口，利用Consul
RCE漏洞注册执行脚本，并通过常见服务器运维工具如ansible、salt或knife下发恶意代码执行，注册脚本如下：

![](https://p0.ssl.qhimg.com/dm/1024_431_/t0126acdabf8e4f42f3.png)

或

![](https://p0.ssl.qhimg.com/dm/1024_124_/t011b6e2ab4ed120495.png)

黑客将CC隐藏在Tor网络中，并通过tor2web.io等暗网反向代理服务来使被攻击的机器正常访问，拉取恶意文件sytemd-check并执行后取消其注册在Consul上的脚本

## 样本分析

systemd-login(elf64)

原始样本被加了UPX 壳，脱壳后，其主要流程如下

![](https://p2.ssl.qhimg.com/t01235f6752e171408f.png)

样本首先检测LD_PRELOAD变量

![](https://p4.ssl.qhimg.com/t01ef44b9266520a298.png)

并将恶意文件移动到/lib/systemd/systemd-login和~/.systemd-login

![](https://p3.ssl.qhimg.com/t014d15d8f16cb4387a.png)

![](https://p5.ssl.qhimg.com/t010a70dd25b5fe2f0b.png)

并将pid写入到/tmp/.X1M-unix防止重复感染

![](https://p3.ssl.qhimg.com/t011e489931ad639cba.png)

随后执行一段内置的Base64编码的脚本

![](https://p1.ssl.qhimg.com/t01891edfa1d9473005.png)

此段代码功能如下

![](https://p1.ssl.qhimg.com/dm/1024_549_/t01d55c1395c811f7e0.png)

  * 将用户信息拼接成字符串并base64编码后，作为refer访问CC的/slave外带数据，目前请求该uri为404，猜测通过其访问日志来记录信息
  * 向cc请求/systemd-resolve文件并下载到/tmp目录，该文件目前不存在

![](https://p3.ssl.qhimg.com/t01a7103f307490b917.png)

  * 通过ansible、salt或knife工具执行如下代码

![](https://p1.ssl.qhimg.com/t0151b5c80d824d3ccd.png)

这段循环同样是执行内置的Base64编码脚本文件

![](https://p3.ssl.qhimg.com/t0150a11b81ae4a55b9.png)

第一段是写入计划任务

![](https://p1.ssl.qhimg.com/t01ed524d7711b371cd.png)

第二段是清理其它挖矿进程

![](https://p1.ssl.qhimg.com/dm/1024_219_/t018e18e0a387d23825.png)

第三段是下载systemd-analyze文件到/tmp/.systemd-analyze，目前该文件不存在

![](https://p5.ssl.qhimg.com/dm/1024_291_/t0191d03fbace27d962.png)

第四段是恶意文件更新的脚本

![](https://p0.ssl.qhimg.com/dm/1024_442_/t01e47e1d9005a94fbb.png)

第五段脚本功能与第四段相同

![](https://p2.ssl.qhimg.com/t01b1b23e6383862a38.png)

systemd-check(elf32)

与systemd-login流程类似，函数执行顺序如图所示

![](https://p5.ssl.qhimg.com/dm/1024_171_/t01d001a03786e200ad.png)

![](https://p3.ssl.qhimg.com/dm/1024_203_/t015d6e261c1b429dd6.png)

![](https://p4.ssl.qhimg.com/dm/1024_81_/t0119401b20cf29ecbe.png)

![](https://p0.ssl.qhimg.com/dm/1024_292_/t01fe7f50bd48349ddc.png)

![](https://p5.ssl.qhimg.com/dm/1024_187_/t011c3951855f2df512.png)

![](https://p2.ssl.qhimg.com/dm/1024_271_/t0129105272652cafb5.png)

![](https://p0.ssl.qhimg.com/t019ba0b0b7409b8a90.png)

![](https://p3.ssl.qhimg.com/dm/1024_319_/t0128fe051be7e88784.png)

## 处置方法

  1. 升级Consul版本，且不要将服务暴露在公网
  2. 停止恶意进程并清理相关计划任务及文件

## IOC

9B6A6282B47D9E7F067309AFEF9DEBF0

57B4EF04FBB773B3661287D5A2B3688E

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信观星实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/173818](/post/id/173818)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [linux](/tag/linux)
  * [系统安全](/tag/系统安全)
  * [Consul](/tag/Consul)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhimg.com/t01ca23525cfc7b9760.png) 奇安信观星实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

