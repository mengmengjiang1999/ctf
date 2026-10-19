# 简单实用远控小工具Todesk

阅读量 **183184**

发布时间 : 2022-07-08 14:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0139008ea18dc4fe5f.png)

## 前言

之前写过anydesk远控，然后在一次测试中，在客户那边看到一个远控软件–Todesk，然后就去官网下载下来研究了一下。

## 准备工作

在开始测试之前先查看官方文档。

支持静默安装

![](https://p4.ssl.qhimg.com/t01185a198a9b1b74e9.jpg)

可设置安全密码

![](https://p5.ssl.qhimg.com/t010f7fa78616e17051.jpg)

![](https://p0.ssl.qhimg.com/t01d3ba078d5202af12.jpg)

我们看到todesk支持命令行静默安装，和设置安全密码，而安全密码和临时密码都可以进行连接。

![](https://p0.ssl.qhimg.com/t010fd69d8fa30d2cee.jpg)

## 本地测试

环境：windows2012R2。

工具：冰蝎3、todesk安装包。

我们在本地搭建环境进行测试，这里利用冰蝎作为测试工具。

todesk1.exe /S 静默安装

![](https://p5.ssl.qhimg.com/t019667be55382f79d2.jpg)

这边执行完成后我们来到本地发现已经安装完成，安装路径在

`C:\Program Files (x86)\ToDesk\<br/>`

![](https://p2.ssl.qhimg.com/t01eccbcb1d14415f8b.jpg)

现在我们就可以根据官方的使用示例来查看状态以及设置安全密码, 如下图。

![](https://p0.ssl.qhimg.com/t017494c6bc1a635597.jpg)

新建2.bat文件内容为上图中的内容，然后在冰蝎中执行，不出意外的话会设置好安全密码以及输出连接的识别码。

![](https://p2.ssl.qhimg.com/t0136fca663afe7a0ea.jpg)

然后再冰蝎中执行时我们发现，虽然正常执行了也输出了识别码，但是输出在目标机器上我们在冰蝎中看不到，所以这里有两种解决办法：

1、使用虚拟终端

![](https://p4.ssl.qhimg.com/t01a06f269c53462567.jpg)

2、输出结果到文件然后读取

![](https://p4.ssl.qhimg.com/t01fcbd099f05aa729b.jpg)

到此我们读取到了连接需要的识别码且已经设置好了安全密码，直接连接。

![](https://p4.ssl.qhimg.com/t0187378ffb4f417a72.jpg)

## 意外情况

到这里已经基本完成了，但是测试环境毕竟是理想环境，接下来再说一些遇到过的情况。

##### **1、目标机器已安装了todesk**

这种意外情况对于我们来说就挺，应该是那种想到了开心的事的感觉。其实在这里要说的是另一种方法获取识别码以及连接密码，我们只需要找到todesk的根目录即可，然后查看config.ini，在cinfig.ini可以找到识别码以及加密的密码。

![](https://p2.ssl.qhimg.com/t017058e55eba0a1056.jpg)

对于加密的密码我们可以复制到本地的todesk配置文件里，替换我们本地的密码，然后重新打开todesk，这样就能得倒对方机器的连接密码。

![](https://p2.ssl.qhimg.com/t01c18c706d6220dc82.jpg)

成功替换得到密码。

![](https://p4.ssl.qhimg.com/t014a72ce2827ae539a.jpg)

##### **2、极端情况**

在之前的一次测试中目标机器可以成功安装，但是不能设置安全密码，并且读取的出来的密码也不是正常的6位密码，这里可以直接kill

todesk进程（一定要杀ToDesk_Service.exe）然后给目标机器修改config文件，替换成我们设置的密码和上一步完全反过来了，再重启todesk。

## 总结

todesk只是作为一个简单的小工具，研究的目的是为了应对一些特殊的环境，而且缺点也有很多：需要管理员权限，目标机器锁屏需要密码，体积太大，容易被发现等问题。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Tide安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/275941](/post/id/275941)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [远控](/tag/远控)
  * [Todesk](/tag/Todesk)

 **+1** __8赞

 __收藏

![](https://p5.ssl.qhimg.com/t013dca47abc465f8d2.png) Tide安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

